#!/usr/bin/env python3
import json
import os
import ssl
from pathlib import Path
from urllib import error, request

import certifi


ROOT = Path(__file__).resolve().parents[1]
ENV_CANDIDATES = [
    ROOT / ".env",
    ROOT / "web" / ".env",
]
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


class OpenAIParserError(RuntimeError):
    pass


def parse_application_description_with_openai(text):
    settings = load_openai_settings()
    payload = {
        "model": settings["model"],
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": build_messages(text),
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with request.urlopen(req, timeout=60, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise OpenAIParserError(f"OpenAI API error {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise OpenAIParserError(f"OpenAI API connection error: {exc}") from exc

    try:
        completion = json.loads(raw)
        content = completion["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise OpenAIParserError(f"Invalid OpenAI response format: {raw[:500]}") from exc

    payload = {
        "scenario_id": parsed.get("scenario_id", "llm-parsed-application"),
        "provider": parsed.get("provider", "unknown"),
        "model_id": parsed.get("model_id", "unknown"),
        "deployment_mode": parsed.get("deployment_mode", "remote_api"),
        "request_type": parsed.get("request_type", "chat_generation"),
        "input_tokens": to_float(parsed.get("input_tokens"), 1200.0),
        "output_tokens": to_float(parsed.get("output_tokens"), 350.0),
        "requests_per_feature": to_float(parsed.get("requests_per_feature"), 1.0),
        "feature_uses_per_month": to_float(parsed.get("feature_uses_per_month"), 1000.0),
        "months_per_year": to_float(parsed.get("months_per_year"), 12.0),
        "country": parsed.get("country", "FR"),
        "grid_carbon_intensity_gco2_per_kwh": to_float(parsed.get("grid_carbon_intensity_gco2_per_kwh"), 40.0),
        "water_intensity_l_per_kwh": to_float(parsed.get("water_intensity_l_per_kwh"), 0.4),
        "software_components": normalize_components(parsed.get("software_components")),
    }
    parser_notes = parsed.get("parser_notes", [])
    if not isinstance(parser_notes, list):
        parser_notes = [str(parser_notes)]
    parser_meta = {"mode": "openai", "model": settings["model"]}
    return payload, parser_notes, parser_meta


def normalize_components(components):
    if not isinstance(components, list) or not components:
        raise OpenAIParserError("The OpenAI parser returned no valid software components.")
    normalized = []
    for component in components:
        if not isinstance(component, dict):
            continue
        normalized.append(
            {
                "component_type": str(component.get("component_type", "component")),
                "energy_wh_per_feature": round(to_float(component.get("energy_wh_per_feature"), 0.0), 4),
                "description": str(component.get("description", "")),
            }
        )
    if not normalized:
        raise OpenAIParserError("The OpenAI parser returned an empty software component list.")
    return normalized


def load_openai_settings():
    env = dict(os.environ)
    for candidate in ENV_CANDIDATES:
        if candidate.exists():
            env.update(parse_dotenv(candidate))
    api_key = env.get("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIParserError("OPENAI_API_KEY is missing. Add it to .env.")
    return {
        "api_key": api_key,
        "model": env.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
    }


def parse_dotenv(path):
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_messages(text):
    schema = {
        "scenario_id": "short-kebab-case-identifier",
        "provider": "openai/google/anthropic/meta/mistral/unknown",
        "model_id": "specific or approximate model identifier",
        "deployment_mode": "remote_api/self_hosted",
        "request_type": "chat_generation/text_summarization/batch_generation/code_assistance",
        "input_tokens": 1200,
        "output_tokens": 350,
        "requests_per_feature": 1,
        "feature_uses_per_month": 1000,
        "months_per_year": 12,
        "country": "FR",
        "grid_carbon_intensity_gco2_per_kwh": 40,
        "water_intensity_l_per_kwh": 0.4,
        "software_components": [
            {
                "component_type": "application_server",
                "energy_wh_per_feature": 0.08,
                "description": "application server and orchestration"
            }
        ],
        "parser_notes": [
            "List every assumption or default introduced by the model."
        ]
    }
    system = (
        "You are a structured parser for an environmental estimation tool for software systems using LLMs. "
        "Read a natural-language application description and output only valid JSON. "
        "Infer a realistic feature-level annualized scenario. "
        "If the user omits a value, insert a conservative default and explain it in parser_notes. "
        "Always provide a non-empty software_components list. "
        "Return numeric values as numbers, not strings. "
        "Do not output markdown or prose outside JSON."
    )
    user = (
        "Parse the following application description into the required JSON structure.\n\n"
        f"Target JSON shape:\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        f"Application description:\n{text}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def to_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
