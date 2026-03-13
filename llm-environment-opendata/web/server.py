#!/usr/bin/env python3
import json
import re
import sys
from functools import lru_cache
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.estimator import (
    compute_token_ratio,
    estimate_feature_externalities,
    get_record,
    load_country_energy_mix,
    load_models,
    load_records,
    wh_to_gco2e,
    wh_to_liters,
)
from core.openai_parser import (
    OpenAIModerationError,
    OpenAIParserError,
    moderate_application_description_with_openai,
    parse_application_description_with_openai,
)


PROJECT_NAME = "EcoTrace LLM"
BIB_PATH = ROOT.parent / "llm-environment-opendata-paper" / "references_llm_environment_opendata.bib"
REFERENCE_PAGE_TOKENS = 750.0
DEFAULT_PROMPT_TOKENS = 1550.0


def normalize_model_label(value):
    if not value:
        return ""
    lowered = str(value).lower()
    for char in (" ", "-", "_", ".", ",", ":", ";", "/", "(", ")"):
        lowered = lowered.replace(char, "")
    return lowered


def format_apa_hover(row):
    apa_citation = format_apa_citation(row)
    locator = str((row or {}).get("source_locator", "")).strip()
    metric_name = str((row or {}).get("metric_name", "")).strip()
    if not apa_citation:
        return locator or metric_name
    extras = [part for part in (metric_name, locator) if part]
    if extras:
        return f"{apa_citation}. {' | '.join(extras)}"
    return apa_citation


def format_apa_citation(row):
    study_key = str((row or {}).get("study_key", "")).strip()
    if study_key:
        bib_entry = load_bibliography_index().get(study_key)
        if bib_entry:
            return format_bib_entry_apa(bib_entry)

    citation = str((row or {}).get("citation", "")).strip()
    if not citation:
        return ""
    return citation


@lru_cache(maxsize=1)
def load_bibliography_index():
    if not BIB_PATH.exists():
        return {}
    content = BIB_PATH.read_text(encoding="utf-8")
    entries = {}
    for match in re.finditer(r"@(\w+)\{([^,]+),\s*(.*?)\n\}", content, re.DOTALL):
        entry_type = match.group(1).strip().lower()
        key = match.group(2).strip()
        body = match.group(3)
        fields = {}
        for field_match in re.finditer(r"(\w+)\s*=\s*\{(.*?)\},?", body, re.DOTALL):
            field_name = field_match.group(1).strip().lower()
            field_value = " ".join(field_match.group(2).strip().split())
            fields[field_name] = field_value
        fields["entry_type"] = entry_type
        entries[key] = fields
    return entries


def format_bib_author_list(author_field):
    if not author_field:
        return ""
    authors = [part.strip().strip("{}") for part in author_field.split(" and ") if part.strip()]
    formatted = []
    for author in authors:
        if "," in author:
            last, first = [part.strip() for part in author.split(",", 1)]
            initials = " ".join(f"{chunk[0]}." for chunk in re.split(r"[\s-]+", first) if chunk)
            formatted.append(f"{last}, {initials}".strip())
        else:
            parts = author.split()
            if len(parts) == 1:
                formatted.append(parts[0])
            else:
                last = parts[-1]
                first = " ".join(parts[:-1])
                initials = " ".join(f"{chunk[0]}." for chunk in re.split(r"[\s-]+", first) if chunk)
                formatted.append(f"{last}, {initials}".strip())
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]}, & {formatted[1]}"
    return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def format_bib_entry_apa(entry):
    authors = format_bib_author_list(entry.get("author", ""))
    year = entry.get("year", "n.d.")
    title = entry.get("title", "").replace("{", "").replace("}", "")
    journal = entry.get("journal", "") or entry.get("booktitle", "") or entry.get("institution", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")
    url = entry.get("url", "")

    parts = []
    if authors:
        parts.append(f"{authors} ({year}).")
    else:
        parts.append(f"({year}).")
    if title:
        parts.append(f"{title}.")
    if journal:
        container = journal
        if volume:
            container += f", {volume}"
            if number:
                container += f"({number})"
        elif number:
            container += f", ({number})"
        if pages:
            container += f", {pages}"
        container += "."
        parts.append(container)
    if url:
        parts.append(url)
    return " ".join(part for part in parts if part)


def reference_anchor_id(row):
    record_id = str((row or {}).get("record_id", "")).strip()
    if not record_id:
        return ""
    return f"ref-{record_id}"


def format_reference_parameters(value):
    raw = str(value or "").strip()
    if not raw:
        return "n.d."
    if "est" in raw.lower():
        return f"{raw}*"
    return raw


def html_id_attr(value):
    if not value:
        return ""
    return f' id="{escape(value, quote=True)}"'


@lru_cache(maxsize=1)
def build_reference_number_map():
    mapping = {}
    for index, row in enumerate(build_literature_catalog_rows(), start=1):
        record_id = str(row.get("record_id", "")).strip()
        if record_id:
            mapping[record_id] = index
    return mapping


def classify_evidence_level(parsed_payload, factor_rows):
    model_id = parsed_payload.get("model_id", "")
    normalized_model = normalize_model_label(model_id)
    if not normalized_model or normalized_model in {"unknown", "generic"}:
        return {
            "level": "proxy_scientifique",
            "label": "Proxy scientifique",
            "description": "L'estimation repose sur des facteurs de littérature applicables a une famille d'usages, sans mesure attribuable a un modele cible specifique.",
        }

    direct_match = False
    family_match = False
    provider = normalize_model_label(parsed_payload.get("provider", ""))
    prefixes = tuple(part for part in normalized_model.split() if part)

    for row in factor_rows:
        haystack = normalize_model_label(
            " ".join(
                [
                    row.get("metric_name", ""),
                    row.get("citation", ""),
                    row.get("source_locator", ""),
                ]
            )
        )
        if normalized_model and normalized_model in haystack:
            direct_match = True
            break
        if provider and provider in haystack:
            family_match = True
        if normalized_model.startswith(("gpt", "gemini", "claude", "llama", "mistral", "qwen", "deepseek")):
            family = "".join(ch for ch in normalized_model if not ch.isdigit())
            if family and family in haystack:
                family_match = True

    if direct_match:
        return {
            "level": "mesure_directe",
            "label": "Mesure directe",
            "description": "Au moins un facteur selectionne correspond explicitement au modele mentionne dans la demande.",
        }
    if family_match:
        return {
            "level": "proxy_scientifique",
            "label": "Proxy scientifique",
            "description": "Les facteurs retenus sont proches de la famille de service ou du fournisseur mentionne, mais ne constituent pas une mesure directe du modele cible.",
        }
    return {
        "level": "extrapolation",
        "label": "Extrapolation",
        "description": "Aucune mesure directe du modele cible n'est disponible dans le corpus mobilise; l'estimation est derivee de facteurs de reference et d'ajustements de contexte.",
    }


def format_scaled_value(value, unit_kind):
    value = 0.0 if value is None else float(value)
    abs_value = abs(value)

    if unit_kind == "energy":
        if abs_value >= 1000:
            return f"{value / 1000.0:.1f}", "kWh"
        return f"{value:.1f}", "Wh"

    if unit_kind == "carbon":
        if abs_value >= 1000:
            return f"{value / 1000.0:.2f}", "kgCO2e"
        return f"{value:.1f}", "gCO2e"

    if unit_kind == "water":
        if abs_value >= 1000:
            return f"{value / 1000.0:.1f}", "L"
        return f"{value:.1f}", "mL"

    return f"{value:.1f}", ""


def format_range_display(range_obj, unit_kind):
    low_value, unit = format_scaled_value(range_obj["low"], unit_kind)
    high_value, _ = format_scaled_value(range_obj["high"], unit_kind)
    return f"{low_value} - {high_value} {unit}"


def format_value_display(value, unit_kind):
    formatted_value, unit = format_scaled_value(value, unit_kind)
    return f"{formatted_value} {unit}".strip()


def format_count(value):
    return f"{int(round(float(value))):,}".replace(",", " ")


def humanize_assumption(text):
    value = str(text)
    replacements = {
        "Parametric extrapolation enabled for target model": "Extrapolation parametrique appliquee au modele cible",
        "Reference inference scaling derived from Ren et al. 2024 with page-level measurements at": "Mise a l'echelle fondee sur Ren et al. (2024), a partir de mesures par page de",
        "Token scaling applied relative to": "Ajustement realise en fonction du volume de tokens, avec une reference de",
        "Carbon contextualized using country electricity carbon intensity": "Les emissions carbone sont ajustées avec l'intensite carbone du mix electrique du pays retenu.",
        "Water contextualized using country electricity water intensity": "La consommation d'eau est ajustée avec l'intensite hydrique du mix electrique retenu.",
        "Request type classified as": "Type d'usage interprete comme",
        "Country mix fallback applied for": "Mix electrique par defaut applique pour",
        "LLM request(s) per feature use": "appel(s) au LLM par usage de la fonctionnalite",
        "feature uses per year": "usages annuels de la fonctionnalite",
    }
    for source, target in replacements.items():
        if source in value:
            value = value.replace(source, target)
    value = value.replace("750 tokens", "750 tokens")
    value = value.replace("12.0", "12")
    value = value.replace("1.0", "1")
    return value


def matching_factor_rows(factor_rows, keywords):
    matches = []
    lowered_keywords = [keyword.lower() for keyword in keywords]
    for row in factor_rows or []:
        haystack = " ".join(
            [
                str(row.get("metric_name", "")),
                str(row.get("metric_unit", "")),
                str(row.get("citation", "")),
                str(row.get("source_locator", "")),
            ]
        ).lower()
        if any(keyword in haystack for keyword in lowered_keywords):
            matches.append(row)
    return matches


def render_source_refs(rows):
    number_map = build_reference_number_map()
    refs = []
    for row in rows:
        title = escape(format_apa_hover(row))
        href = f"#{reference_anchor_id(row)}" if reference_anchor_id(row) else "#"
        ref_number = number_map.get(str(row.get("record_id", "")).strip())
        if not ref_number:
            continue
        refs.append(
            f'<a class="inline-ref" href="{href}" title="{title}">[{ref_number}]</a>'
        )
    return " ".join(refs)


def render_sourced_value(value_text, rows):
    if not rows:
        return f"<code>{escape(value_text)}</code>"
    title = " ; ".join(format_apa_hover(row) for row in rows)
    return (
        f'<span class="sourced-value" title="{escape(title)}">'
        f'<code>{escape(value_text)}</code>'
        f'{render_source_refs(rows)}'
        f"</span>"
    )


def render_extrapolation_details(result, metric_label, source_rows):
    if result.get("method") != "parametric_extrapolation":
        return ""
    unit_key = {
        "energy": "energy_wh",
        "carbon": "carbon_gco2e",
        "water": "water_ml",
    }.get(metric_label)
    detail = ((result.get("per_request_llm") or {}) and (result.get("extrapolation_details") or {}).get(unit_key)) or {}
    row_lookup = {row.get("record_id"): row for row in source_rows or []}
    detail_lines = []
    for anchor in detail.get("anchors", []):
        source_value = anchor.get("source_value")
        source_unit = anchor.get("source_unit", "")
        factor_value = anchor.get("factor_central")
        extrapolated_value = anchor.get("extrapolated_value_central")
        if source_value is None or factor_value is None or extrapolated_value is None:
            continue
        row = row_lookup.get(anchor.get("record_id"))
        citation_link = ""
        if row:
            title = escape(format_apa_hover(row))
            href = f"#{reference_anchor_id(row)}" if reference_anchor_id(row) else "#"
            citation_link = (
                f' <a class="inline-ref" href="{href}" title="{title}">'
                f'{escape(row.get("citation", "source"))}</a>'
            )
        formatted_source = f"{source_value} {source_unit}".strip()
        formatted_extrapolated = format_value_display(extrapolated_value, metric_label if metric_label != "carbon" else "carbon")
        detail_lines.append(
            f"<li><strong>{escape(anchor.get('source_model', 'modele source'))}</strong> : valeur d'origine "
            f"<code>{escape(formatted_source)}</code>{citation_link} × facteur applique <code>{factor_value:.3f}</code> "
            f"= valeur extrapolee <code>{escape(formatted_extrapolated)}</code></li>"
        )

    if not detail_lines:
        return ""
    return f'<ul class="extrapolation-list">{"".join(detail_lines)}</ul>'


def render_metric_detail(result, factor_rows, metric_label, title):
    annual_llm = result["annual_llm"]
    scope = result["feature_scope"]
    annual_requests = float(scope["annual_llm_requests"])
    per_request = result["per_request_llm"]
    per_feature = result["per_feature_llm"]
    source_rows = matching_factor_rows(
        factor_rows,
        {
            "energy": ["energy", "wh"],
            "carbon": ["carbon", "emission", "gco2"],
            "water": ["water", "ml", "liter", "litre"],
        }[metric_label],
    )
    unit_key = {
        "energy": "energy_wh",
        "carbon": "carbon_gco2e",
        "water": "water_ml",
    }[metric_label]
    return f"""
    <details class="metric-detail">
      <summary class="metric-detail-toggle">
        <span class="metric-detail-icon" aria-hidden="true">+</span>
        <span>Voir le détail du calcul</span>
      </summary>
      <div class="metric-detail-body">
        <p class="math-detail">
          <strong>{escape(title)}</strong> :
          <code>{escape(format_range_display(annual_llm[unit_key], metric_label))}</code>
        </p>
        {render_extrapolation_details(result, metric_label, source_rows)}
        <p class="math-detail">
          Impact estime pour une requete LLM :
          <code>{escape(format_range_display(per_request[unit_key], metric_label))}</code>
        </p>
        <p class="math-detail">
          Impact estime pour un usage de la fonctionnalite :
          <code>{escape(format_range_display(per_feature[unit_key], metric_label))}</code>
        </p>
        <p class="math-detail">
          En projetant cette valeur sur <code>{format_count(annual_requests)}</code> appels par an,
          on obtient <code>{escape(format_range_display(annual_llm[unit_key], metric_label))}</code>.
        </p>
      </div>
    </details>
    """


def render_assumptions_summary(result):
    assumptions = result.get("assumptions", [])
    if not assumptions:
        return ""
    return f"""
    <div class="assumptions-box assumptions-box-compact">
      <span class="math-label">Hypotheses retenues</span>
      <ul class="assumptions-list">
        {''.join(f'<li>{escape(humanize_assumption(item))}</li>' for item in assumptions)}
      </ul>
    </div>
    """


def build_method_comparisons(records, parsed_payload, result):
    annual_requests = float(result["feature_scope"]["annual_llm_requests"])
    input_tokens = float(parsed_payload.get("input_tokens", 0.0) or 0.0)
    output_tokens = float(parsed_payload.get("output_tokens", 0.0) or 0.0)
    total_tokens = input_tokens + output_tokens
    token_ratio = compute_token_ratio(input_tokens, output_tokens)
    page_ratio = (total_tokens / REFERENCE_PAGE_TOKENS) if total_tokens > 0 else (DEFAULT_PROMPT_TOKENS / REFERENCE_PAGE_TOKENS)
    grid_carbon_intensity = float(parsed_payload.get("grid_carbon_intensity_gco2_per_kwh", 0.0) or 0.0)
    water_intensity = float(parsed_payload.get("water_intensity_l_per_kwh", 0.0) or 0.0)

    methods = []

    def add_method(label, basis, energy_wh=None, carbon_g=None, water_ml=None, record_ids=None):
        rows = factor_details(records, record_ids or [])
        methods.append(
            {
                "label": label,
                "basis": basis,
                "energy": format_range_display({"low": energy_wh, "high": energy_wh}, "energy") if energy_wh is not None else "n.d.",
                "carbon": format_range_display({"low": carbon_g, "high": carbon_g}, "carbon") if carbon_g is not None else "n.d.",
                "water": format_range_display({"low": water_ml, "high": water_ml}, "water") if water_ml is not None else "n.d.",
                "refs": render_source_refs(rows),
            }
        )

    if result.get("method") == "parametric_extrapolation":
        annual = result["annual_llm"]
        add_method(
            "Extrapolation paramétrique",
            "Ancrages par page, mise à l'échelle par paramètres actifs, tokens et mix électrique",
            annual["energy_wh"]["central"],
            annual["carbon_gco2e"]["central"],
            annual["water_ml"]["central"],
            result.get("selected_factors", []),
        )

    prompt_energy = get_record(records, "elsworth2025_prompt_energy")
    prompt_carbon = get_record(records, "elsworth2025_prompt_carbon")
    prompt_water = get_record(records, "elsworth2025_prompt_water")
    if prompt_energy:
        energy_wh = float(prompt_energy["metric_value"]) * token_ratio * annual_requests
        carbon_g = float(prompt_carbon["metric_value"]) * token_ratio * annual_requests if prompt_carbon else wh_to_gco2e(energy_wh, grid_carbon_intensity)
        water_ml = float(prompt_water["metric_value"]) * token_ratio * annual_requests if prompt_water else wh_to_liters(energy_wh, water_intensity) * 1000.0
        add_method(
            "Méthode par prompt",
            "Facteurs en Wh/prompt, gCO2e/prompt et mL/prompt",
            energy_wh,
            carbon_g,
            water_ml,
            ["elsworth2025_prompt_energy", "elsworth2025_prompt_carbon", "elsworth2025_prompt_water"],
        )

    query_energy = get_record(records, "epri2024_chatgpt_query")
    if query_energy:
        energy_wh = float(query_energy["metric_value"]) * token_ratio * annual_requests
        carbon_g = wh_to_gco2e(energy_wh, grid_carbon_intensity) if grid_carbon_intensity else None
        water_ml = wh_to_liters(energy_wh, water_intensity) * 1000.0 if water_intensity else None
        add_method(
            "Méthode par requête",
            "Facteur en Wh/query contextualisé avec le mix électrique",
            energy_wh,
            carbon_g,
            water_ml,
            ["epri2024_chatgpt_query"],
        )

    for prefix, model_label in (("ren2024_gemma2b", "Méthode par page - Gemma-2B-it"), ("ren2024_llama70b", "Méthode par page - Llama-3-70B")):
        energy_record = get_record(records, f"{prefix}_energy")
        carbon_record = get_record(records, f"{prefix}_carbon")
        water_record = get_record(records, f"{prefix}_water")
        if not energy_record:
            continue
        pages_per_request = page_ratio
        annual_pages = pages_per_request * annual_requests
        energy_wh = float(energy_record["metric_value"]) * 1000.0 * annual_pages
        carbon_g = float(carbon_record["metric_value"]) * annual_pages if carbon_record else wh_to_gco2e(energy_wh, grid_carbon_intensity)
        water_ml = float(water_record["metric_value"]) * 1000.0 * annual_pages if water_record else wh_to_liters(energy_wh, water_intensity) * 1000.0
        add_method(
            model_label,
            "Facteurs par page, annualisés via le nombre estimé de pages générées",
            energy_wh,
            carbon_g,
            water_ml,
            [f"{prefix}_energy", f"{prefix}_carbon", f"{prefix}_water"],
        )

    return methods


def render_method_comparisons(methods):
    if not methods:
        return ""
    rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(method['label'])}</strong><div class="method-basis">{escape(method['basis'])}</div></td>
          <td>{escape(method['energy'])}</td>
          <td>{escape(method['carbon'])}</td>
          <td>{escape(method['water'])}</td>
          <td>{method['refs']}</td>
        </tr>
        """
        for method in methods
    )
    return f"""
    <div class="method-panel">
      <p class="submetrics-title">Méthodes de calcul mobilisées</p>
      <div class="reference-table-wrap">
        <table class="reference-table">
          <thead>
            <tr>
              <th>Méthode</th>
              <th>Énergie annuelle</th>
              <th>Carbone annuel</th>
              <th>Eau annuelle</th>
              <th>Références</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </div>
    """


def render_summary_html(summary_text, factor_rows):
    text = escape(summary_text or "")
    source_map = {}
    number_map = build_reference_number_map()
    for row in factor_rows or []:
        ref_number = number_map.get(str(row.get("record_id", "")).strip())
        if not ref_number:
            continue
        source_map[str(ref_number)] = row
        source_map[f"SRC{ref_number}"] = row

    def replace_source_tag(match):
        tag = match.group(1)
        row = source_map.get(tag)
        if not row:
            return f"[{escape(tag)}]"
        title = escape(format_apa_hover(row))
        href = f"#{reference_anchor_id(row)}" if reference_anchor_id(row) else "#"
        display_tag = re.sub(r"^SRC", "", tag)
        return (
            f'<a class="source-tag" href="{href}" '
            f'title="{title}">[{escape(display_tag)}]</a>'
        )

    html = re.sub(r"\[(SRC\d+|\d+)\]", replace_source_tag, text)
    return html.replace("\n", "<br>")


def describe_record_type_fr(record):
    phase = str(record.get("phase", "")).strip()
    metric_name = str(record.get("metric_name", "")).strip()
    model_or_scope = str(record.get("model_or_scope", "")).strip()

    labels = {
        ("training", "training_emissions"): "Émissions de gaz à effet de serre liées à l'entraînement",
        ("training", "compute_time"): "Temps de calcul mobilisé pour l'entraînement",
        ("training", "training_tokens"): "Volume de tokens utilisés pour l'entraînement",
        ("lifecycle", "creation_lifecycle_emissions"): "Émissions sur l'ensemble du cycle de création du modèle",
        ("lifecycle", "creation_lifecycle_water"): "Consommation d'eau sur l'ensemble du cycle de création du modèle",
        ("lifecycle", "development_share"): "Part de l'impact attribuée à la phase de développement",
        ("lifecycle", "power_utilization_range"): "Plage de facteur d'utilisation électrique de l'infrastructure",
        ("lifecycle", "training_water_total"): "Consommation totale d'eau associée à l'entraînement",
        ("lifecycle", "training_water_onsite"): "Consommation d'eau sur site associée à l'entraînement",
        ("infrastructure", "ai_share_of_datacenter_electricity"): "Part de l'IA dans la consommation électrique des centres de données",
        ("infrastructure", "annual_electricity"): "Consommation électrique annuelle des centres de données",
        ("infrastructure", "electricity_share"): "Part de la demande électrique attribuée aux centres de données",
        ("infrastructure", "annual_growth_rate"): "Taux de croissance annuel de la consommation électrique",
        ("infrastructure", "ai_power_demand"): "Puissance électrique appelée par les systèmes d'IA",
        ("infrastructure", "annualized_energy"): "Consommation énergétique annualisée des systèmes d'IA",
        ("inference", "query_energy"): "Consommation énergétique par requête",
        ("inference", "prompt_energy"): "Consommation énergétique par prompt",
        ("inference", "prompt_emissions"): "Émissions par prompt",
        ("inference", "prompt_water"): "Consommation d'eau par prompt",
        ("inference", "efficiency_gain"): "Gain d'efficacité annoncé entre deux configurations d'inférence",
        ("inference", "energy_component"): "Répartition de la consommation énergétique par composant d'inférence",
        ("inference", "page_generation_energy"): "Consommation énergétique pour générer une page",
        ("inference", "page_generation_emissions"): "Émissions pour générer une page",
        ("inference", "page_generation_water"): "Consommation d'eau pour générer une page",
        ("inference", "response_water_equivalent"): "Consommation d'eau pour un petit ensemble de réponses",
    }

    label = labels.get((phase, metric_name))
    if not label:
        phase_label = {
            "training": "Entraînement",
            "inference": "Inférence",
            "infrastructure": "Infrastructure",
            "lifecycle": "Cycle de vie",
        }.get(phase, phase.capitalize() if phase else "Indicateur")
        metric_label = metric_name.replace("_", " ") if metric_name else "non précisé"
        label = f"{phase_label} : {metric_label}"

    if model_or_scope:
        return f"{label} ({model_or_scope})"
    return label


def build_literature_catalog_rows():
    rows = []
    excluded_study_keys = {"lbl2025", "devriesgao2025joule", "iea2025", "epri2024"}
    for record in load_records():
        source_url = str(record.get("source_url", ""))
        if record.get("study_key") in excluded_study_keys:
            continue
        if record.get("record_id") in {
            "morrison2025_dev_share",
            "morrison2025_power_variation",
            "li2025_chatbot_water",
            "strubell2019_co2_tuning_pipeline",
            "strubell2019_co2_nas",
        }:
            continue
        if "iea.org" in source_url or "publicpower.org" in source_url:
            continue
        rows.append(
            {
                "record_id": record.get("record_id", ""),
                "study_key": record.get("study_key", ""),
                "data_type": describe_record_type_fr(record),
                "model_or_scope": record.get("llm_normalized", "") or "n.d.",
                "model_parameters": record.get("model_parameters_normalized", "") or "n.d.",
                "geography": record.get("country_normalized", "") or "n.d.",
                "metric_value": f"{record.get('metric_value', '')} {record.get('metric_unit', '')}".strip(),
                "citation": record.get("citation", ""),
                "source_locator": record.get("source_locator", ""),
                "source_url": record.get("source_url", "#"),
            }
        )
    return rows


def render_reference_catalog():
    rows = build_literature_catalog_rows()
    if not rows:
        return ""
    number_map = build_reference_number_map()
    rendered_rows = []
    for row in rows:
        locator_html = ""
        if row["source_locator"]:
            locator_html = f'<div class="reference-locator">{escape(row["source_locator"])}</div>'
        row_id = reference_anchor_id(row)
        ref_number = number_map.get(str(row.get("record_id", "")).strip(), "")
        rendered_rows.append(
            f"<tr{html_id_attr(row_id)}>"
            f"<td class=\"reference-number\">[{escape(str(ref_number))}]</td>"
            f"<td>{escape(row['data_type'])}</td>"
            f"<td>{escape(row.get('model_or_scope', '') or 'n.d.')}</td>"
            f"<td>{escape(format_reference_parameters(row.get('model_parameters', '') or 'n.d.'))}</td>"
            f"<td>{escape(row.get('geography', '') or 'n.d.')}</td>"
            f"<td>{escape(row['metric_value'])}</td>"
            f"<td>"
            f"<a href=\"{escape(row['source_url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\" title=\"{escape(format_apa_hover(row))}\">{escape(format_apa_citation(row))}</a>"
            f"{locator_html}"
            f"</td>"
            f"</tr>"
        )
    table_rows = "".join(rendered_rows)

    return f"""
    <section class="panel reference-panel">
      <div class="summary-header">
        <div>
          <div class="summary-kicker">Referentiel</div>
          <h3>{len(rows)} indicateurs issus de la litterature scientifique</h3>
        </div>
        <div class="summary-badge">Tableau de reference</div>
      </div>
      <p class="summary-intro">Ce tableau presente les indicateurs quantifies extraits du corpus scientifique mobilise par le projet. Les références macro d'infrastructure et les sources institutionnelles hors périmètre LLM ont été exclues de ce référentiel.</p>
      <div class="reference-table-wrap">
        <table class="reference-table">
          <thead>
            <tr>
              <th>Réf.</th>
              <th>Type de donnée</th>
              <th>Modèle LLM</th>
              <th>Paramètres</th>
              <th>Pays</th>
              <th>Valeur</th>
              <th>Citation</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
      <p class="summary-intro">`*` indique une valeur de nombre de paramètres estimée et non officiellement publiée par le fournisseur.</p>
    </section>
    """


def render_model_reference_table():
    rows = load_models()
    if not rows:
        return ""
    body = "".join(
        f"""
        <tr>
          <td>{escape(row.get('model_id', ''))}</td>
          <td>{escape(row.get('provider', ''))}</td>
          <td>{escape((row.get('active_parameters_billion') or 'n.d.') + ('B' if row.get('active_parameters_billion') else ''))}</td>
          <td>{escape((row.get('total_parameters_billion') or 'n.d.') + ('B' if row.get('total_parameters_billion') else ''))}</td>
          <td>{escape(row.get('parameter_value_status', 'n.d.'))}</td>
          <td>{escape(row.get('parameter_source', 'n.d.'))}</td>
        </tr>
        """
        for row in rows
    )
    return f"""
    <section class="panel reference-panel">
      <div class="summary-header">
        <div>
          <div class="summary-kicker">Modèles</div>
          <h3>Table de référence des modèles</h3>
        </div>
        <div class="summary-badge">Paramètres</div>
      </div>
      <p class="summary-intro">Cette table recense les modèles de référence utilisés par le projet, leur nombre de paramètres et la source de la valeur observée ou estimée.</p>
      <div class="reference-table-wrap">
        <table class="reference-table">
          <thead>
            <tr>
              <th>Modèle</th>
              <th>Provider</th>
              <th>Paramètres actifs</th>
              <th>Paramètres totaux</th>
              <th>Statut</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>{body}</tbody>
        </table>
      </div>
    </section>
    """


def render_country_mix_table():
    rows = load_country_energy_mix()
    if not rows:
        return ""
    body = "".join(
        f"""
        <tr>
          <td>{escape(row.get('country_code', ''))}</td>
          <td>{escape(row.get('country_name', ''))}</td>
          <td>{escape(row.get('year', ''))}</td>
          <td>{escape(row.get('grid_carbon_intensity_gco2_per_kwh', ''))} gCO2e/kWh</td>
          <td>{escape(row.get('water_intensity_l_per_kwh', ''))} L/kWh</td>
          <td>{escape(row.get('source_citation', 'n.d.'))}</td>
        </tr>
        """
        for row in rows
    )
    return f"""
    <section class="panel reference-panel">
      <div class="summary-header">
        <div>
          <div class="summary-kicker">Pays</div>
          <h3>Table de référence des mix énergétiques</h3>
        </div>
        <div class="summary-badge">Mix électrique</div>
      </div>
      <p class="summary-intro">Cette table recense les facteurs pays utilisés pour contextualiser le carbone et l'eau, avec la source associée à chaque valeur.</p>
      <div class="reference-table-wrap">
        <table class="reference-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Pays</th>
              <th>Année</th>
              <th>Intensité carbone</th>
              <th>Intensité eau</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>{body}</tbody>
        </table>
      </div>
    </section>
    """


def factor_details(records, factor_ids):
    rows = []
    for factor_id in factor_ids:
        record = get_record(records, factor_id)
        if not record:
            continue
        rows.append(
            {
                "record_id": record["record_id"],
                "study_key": record.get("study_key", ""),
                "metric_name": record["metric_name"],
                "metric_value": record["metric_value"],
                "metric_unit": record["metric_unit"],
                "citation": record["citation"],
                "source_locator": record["source_locator"],
                "source_url": record["source_url"],
            }
        )
    return rows


def process_description(form):
    description = form.get("description", [""])[0]
    moderation = moderate_application_description_with_openai(description)
    if moderation["decision"] != "allow":
        guidance = (
            "Décris une application, une fonctionnalité ou un workflow utilisant un LLM, "
            "avec son usage, son volume ou son contexte technique."
        )
        raise OpenAIModerationError(
            f"Cette description ne correspond pas clairement à un logiciel ou à un usage de LLM exploitable par la plateforme. "
            f"{moderation['reason']} {guidance}"
        )
    parsed_payload, parser_notes, parser_meta = parse_application_description_with_openai(description)
    parser_meta["moderation"] = moderation
    parsed_payload["software_components"] = []
    parser_notes.append("L'estimation a ete restreinte aux consommations du LLM; les composants logiciels hors LLM ont ete exclus du calcul.")
    apply_overrides(parsed_payload, form)
    records = load_records()
    result = estimate_feature_externalities(records, parsed_payload)
    rows = factor_details(records, result["selected_factors"])
    parser_meta["evidence"] = classify_evidence_level(parsed_payload, rows)
    return description, parsed_payload, parser_notes, parser_meta, result, rows


def render_page(result=None, description="", parsed_payload=None, parser_notes=None, parser_meta=None, factor_rows=None, error_message=None):
    error_block = ""
    if error_message:
        error_block = f"""
        <section class="panel alert-panel error">
          <h2>Description non exploitable</h2>
          <p class="lead">{escape(error_message)}</p>
          <p class="lead">EcoTrace LLM attend une description d'application, de fonctionnalité ou de workflow mobilisant un ou plusieurs LLMs.</p>
        </section>
        """

    reference_block = render_reference_catalog()
    model_reference_block = render_model_reference_table()
    country_mix_block = render_country_mix_table()
    result_block = ""
    if result:
        annual = result["annual_llm"]
        method_comparisons = build_method_comparisons(load_records(), parsed_payload, result)
        evidence = (parser_meta or {}).get("evidence", {})
        method_label = {
            "parametric_extrapolation": "Extrapolation parametrique",
            "literature_proxy": "Proxy de litterature",
        }.get(result.get("method"), "Methode non qualifiee")
        model_profile = result.get("model_profile") or {}
        country_mix = result.get("country_energy_mix") or {}
        result_block = f"""
        <section class="panel result hero-card">
          <h2>Evaluation environnementale</h2>
          <p class="lead">Estimation fondee sur des indicateurs scientifiques sourcés et un calcul traceable.</p>
          <p class="scope-note">Perimetre retenu: seules les consommations du LLM sont prises en compte. Les autres consommations du systeme logiciel, de l'infrastructure applicative et des services annexes sont exclues de cette estimation.</p>
          <p class="meta-inline">Niveau de preuve: <strong>{escape(evidence.get('label', 'Non qualifie'))}</strong></p>
          <p class="meta-inline">Methode: <strong>{escape(method_label)}</strong></p>
          <p class="meta-inline">Modele de reference: <strong>{escape(model_profile.get('model_id', parsed_payload.get('model_id', 'non specifie')))}</strong>{' | Parametres actifs approx.: <strong>' + escape(model_profile.get('active_parameters_billion', '')) + 'B</strong>' if model_profile.get('active_parameters_billion') else ''}</p>
          <p class="meta-inline">Mix electrique: <strong>{escape(country_mix.get('country_code', parsed_payload.get('country', 'non specifie')))}</strong>{' | ' + escape(country_mix.get('grid_carbon_intensity_gco2_per_kwh', '')) + ' gCO2e/kWh' if country_mix.get('grid_carbon_intensity_gco2_per_kwh') else ''}</p>
          {render_assumptions_summary(result)}
          {render_method_comparisons(method_comparisons)}
        </section>
        """

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PROJECT_NAME}</title>
  <style>
    :root {{
      --bg: #f8f9fa;
      --paper: #ffffff;
      --ink: #212529;
      --muted: #6c757d;
      --line: #dee2e6;
      --accent: #0d6efd;
      --accent-soft: #e7f1ff;
      --error: #dc3545;
      --shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
      scroll-behavior: smooth;
    }}
    .wrap {{ max-width: 960px; margin: 0 auto; padding: 24px 16px 40px; }}
    .hero {{ margin-bottom: 16px; }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 8px;
      padding: 0.25rem 0.55rem;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.74rem;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(1.8rem, 4vw, 2.5rem); line-height: 1.15; font-weight: 700; }}
    h2, h3 {{ margin: 0 0 0.75rem; font-weight: 700; }}
    .subtitle {{ max-width: 760px; color: var(--muted); font-size: 0.98rem; line-height: 1.55; margin: 0; }}
    .panel {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 0.75rem;
      padding: 1rem 1.1rem;
      box-shadow: var(--shadow);
      margin-bottom: 1rem;
    }}
    .hero-card {{
      border-color: rgba(13,110,253,0.18);
      background: #ffffff;
    }}
    .alert-panel.error {{
      border-color: rgba(220,53,69,0.3);
      background: #fff5f6;
    }}
    textarea, input {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 0.5rem;
      padding: 0.875rem 1rem;
      font: inherit;
      background: #fff;
    }}
    textarea:focus, input:focus {{
      outline: none;
      border-color: rgba(13,110,253,0.55);
      box-shadow: 0 0 0 0.2rem rgba(13,110,253,0.15);
    }}
    textarea {{ min-height: 200px; resize: vertical; }}
    label {{ display: block; font-size: 0.95rem; font-weight: 600; color: var(--ink); margin-bottom: 0.5rem; }}
    button {{
      margin-top: 1rem;
      border: 0;
      border-radius: 0.5rem;
      background: var(--accent);
      color: white;
      padding: 0.75rem 1.15rem;
      font: inherit;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
    }}
    button:hover {{ background: #0b5ed7; }}
    button:disabled {{
      background: #6ea8fe;
      cursor: wait;
    }}
    .spinner {{
      width: 1rem;
      height: 1rem;
      border: 2px solid rgba(255,255,255,0.45);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      display: none;
    }}
    .is-loading .spinner {{
      display: inline-block;
    }}
    .loading-text {{
      display: none;
    }}
    .is-loading .loading-text {{
      display: inline;
    }}
    .is-loading .default-text {{
      display: none;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    .metric {{
      margin-top: 0.9rem;
      padding: 0.9rem;
      border-radius: 0.65rem;
      background: #fff;
      border: 1px solid var(--line);
    }}
    .metric .label {{
      display: block;
      color: var(--muted);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      margin-bottom: 0.5rem;
    }}
    .metric strong {{
      font-size: 1.12rem;
      line-height: 1.35;
    }}
    .submetrics-block {{
      margin-top: 1rem;
      padding-top: 0.9rem;
      border-top: 1px solid var(--line);
    }}
    .submetrics-title {{
      margin: 0 0 0.7rem;
      color: #495057;
      font-size: 0.92rem;
      font-weight: 700;
    }}
    .submetrics-title-secondary {{
      margin-top: 1rem;
    }}
    .submetrics {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.7rem;
    }}
    .submetric {{
      padding: 0.75rem 0.8rem;
      border: 1px solid var(--line);
      border-radius: 0.6rem;
      background: #f8f9fa;
    }}
    .submetric-label {{
      display: block;
      margin-bottom: 0.35rem;
      color: var(--muted);
      font-size: 0.8rem;
      line-height: 1.35;
    }}
    .submetric strong {{
      font-size: 0.98rem;
      line-height: 1.35;
    }}
    .submetrics-native {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .submetric-native {{
      background: #fff;
    }}
    .method-panel {{
      margin-top: 1rem;
      padding-top: 0.9rem;
      border-top: 1px solid var(--line);
    }}
    .method-basis {{
      margin-top: 0.25rem;
      color: var(--muted);
      font-size: 0.83rem;
      line-height: 1.45;
    }}
    .metric-detail {{
      margin-top: 0.85rem;
      border-top: 1px solid var(--line);
      padding-top: 0.7rem;
    }}
    .metric-detail-toggle {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      cursor: pointer;
      color: var(--accent);
      font-size: 0.9rem;
      font-weight: 600;
      list-style: none;
    }}
    .metric-detail-toggle::-webkit-details-marker {{
      display: none;
    }}
    .metric-detail-icon {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1.25rem;
      height: 1.25rem;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 700;
      line-height: 1;
    }}
    .metric-detail[open] .metric-detail-icon {{
      transform: rotate(45deg);
    }}
    .metric-detail-body {{
      margin-top: 0.7rem;
      padding: 0.85rem 0.9rem;
      border: 1px solid var(--line);
      border-radius: 0.65rem;
      background: #f8f9fa;
    }}
    .lead {{ color: var(--muted); line-height: 1.6; margin: 0; }}
    .scope-note {{
      margin: 0.6rem 0 0;
      padding: 0.7rem 0.85rem;
      border-left: 3px solid var(--accent);
      background: #f8fbff;
      color: #495057;
      font-size: 0.93rem;
      line-height: 1.55;
    }}
    .meta-inline {{
      margin: 0.45rem 0 0;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .summary-panel {{
      border-color: rgba(13,110,253,0.18);
      background: var(--paper);
    }}
    .summary-header {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: center;
      margin-bottom: 0.5rem;
    }}
    .summary-kicker {{
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-size: 0.78rem;
      font-weight: 700;
      margin-bottom: 0.35rem;
    }}
    .summary-badge {{
      flex: 0 0 auto;
      border: 1px solid rgba(13,110,253,0.18);
      border-radius: 999px;
      padding: 0.4rem 0.75rem;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.82rem;
      font-weight: 600;
    }}
    .summary-intro {{
      margin: 0 0 0.85rem;
      color: var(--muted);
      max-width: 72ch;
      line-height: 1.5;
      font-size: 0.94rem;
    }}
    .summary-body {{
      border: 1px solid var(--line);
      padding: 0.9rem 1rem;
      background: #f8fbff;
      border-radius: 0.75rem;
      line-height: 1.7;
      font-size: 0.96rem;
    }}
    .reference-panel {{
      border-color: rgba(13,110,253,0.14);
    }}
    .reference-table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 0.65rem;
      background: #fff;
    }}
    .reference-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.94rem;
    }}
    .reference-table th,
    .reference-table td {{
      padding: 0.75rem 0.85rem;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    .reference-table th {{
      background: #f8f9fa;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: #495057;
    }}
    .reference-table tbody tr:last-child td {{
      border-bottom: 0;
    }}
    .reference-table tbody tr:target td {{
      background: #fff8db;
    }}
    .reference-locator {{
      margin-top: 0.2rem;
      color: var(--muted);
      font-size: 0.83rem;
      line-height: 1.45;
    }}
    .source-tag {{
      display: inline-block;
      margin-left: 0.15rem;
      padding: 0.05rem 0.35rem;
      border-radius: 999px;
      background: rgba(13,110,253,0.1);
      color: var(--accent);
      font-size: 0.8rem;
      font-weight: 700;
      text-decoration: none;
      vertical-align: baseline;
    }}
    .source-tag:hover {{
      background: rgba(13,110,253,0.18);
      text-decoration: none;
    }}
    .math-panel {{
      border-color: rgba(108,117,125,0.18);
      background: #fff;
    }}
    .assumptions-box {{
      margin-bottom: 0.85rem;
      padding: 0.9rem;
      border: 1px solid var(--line);
      border-radius: 0.65rem;
      background: #f8f9fa;
    }}
    .assumptions-box-compact {{
      margin-top: 0.9rem;
      margin-bottom: 0;
    }}
    .assumptions-list {{
      margin: 0;
      padding-left: 1.15rem;
      color: #495057;
      line-height: 1.6;
    }}
    .assumptions-list li + li {{
      margin-top: 0.35rem;
    }}
    .math-label {{
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.82rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: #495057;
    }}
    .math-formula {{
      margin-bottom: 0.75rem;
      font-size: 1.05rem;
    }}
    .math-formula code,
    .metric-detail-body code,
    .math-panel code {{
      font-family: "SFMono-Regular", Consolas, monospace;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 0.45rem;
      padding: 0.2rem 0.4rem;
    }}
    .sourced-value {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      flex-wrap: wrap;
    }}
    .inline-ref {{
      display: inline-block;
      padding: 0.1rem 0.38rem;
      border-radius: 999px;
      background: rgba(13,110,253,0.1);
      color: var(--accent);
      font-size: 0.74rem;
      font-weight: 700;
      text-decoration: none;
    }}
    .inline-ref:hover {{
      background: rgba(13,110,253,0.18);
      text-decoration: none;
    }}
    .metric-detail-body p,
    .math-panel p {{
      margin: 0;
      color: #495057;
      line-height: 1.7;
    }}
    .extrapolation-list {{
      margin: 0 0 0.75rem;
      padding-left: 1.2rem;
      color: #495057;
      line-height: 1.6;
      font-size: 0.92rem;
    }}
    .extrapolation-list li + li {{
      margin-top: 0.35rem;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 900px) {{
      .submetrics {{ grid-template-columns: 1fr; }}
      .summary-header {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <header class="hero">
      <div class="eyebrow">Projet {PROJECT_NAME}</div>
      <h1>Estimer l’empreinte environnementale d’une application utilisant des LLMs</h1>
      <p class="subtitle">Décris ton application en langage naturel pour obtenir une estimation environnementale, ses hypothèses et son détail de calcul sourcé.</p>
    </header>

    <form class="panel" method="post" action="/" id="estimate-form">
      <label for="description">Description libre de l'application</label>
      <textarea id="description" name="description" placeholder="Exemple: Nous avons un assistant RAG sur GPT-4 via API, utilisé 4000 fois par mois en France. Chaque requête envoie 2200 input tokens et reçoit 500 output tokens. Il y a une base vectorielle, des embeddings et du logging.">{escape(description)}</textarea>
      <button type="submit" id="submit-button">
        <span class="spinner" aria-hidden="true"></span>
        <span class="default-text">Evaluer l'application</span>
        <span class="loading-text">Evaluation en cours...</span>
      </button>
    </form>
    {error_block}
    {result_block}
    {reference_block}
    {model_reference_block}
    {country_mix_block}
  </main>
  <script>
    const estimateForm = document.getElementById('estimate-form');
    const submitButton = document.getElementById('submit-button');
    if (estimateForm && submitButton) {{
      estimateForm.addEventListener('submit', function () {{
        submitButton.disabled = true;
        submitButton.classList.add('is-loading');
      }});
    }}
  </script>
</body>
</html>
"""
class Handler(BaseHTTPRequestHandler):
    def _write_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._write_html(render_page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        form = parse_qs(raw)
        description = form.get("description", [""])[0]

        try:
            description, parsed_payload, parser_notes, parser_meta, result, rows = process_description(form)
        except (OpenAIModerationError, OpenAIParserError) as exc:
            self._write_html(render_page(description=description, error_message=str(exc)), status=502)
            return

        self._write_html(
            render_page(
                result=result,
                description=description,
                parsed_payload=parsed_payload,
                parser_notes=parser_notes,
                parser_meta=parser_meta,
                factor_rows=rows,
            )
        )


def apply_overrides(payload, form):
    return payload


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8080), Handler)
    print(f"{PROJECT_NAME} web app running on http://127.0.0.1:8080")
    server.serve_forever()
