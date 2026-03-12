# Tableau de synthèse "article-ready": LLMs et environnement

Ce tableau est une version compacte, destinée à être intégrée dans un article. Il ne retient que les références les plus robustes et les chiffres les plus facilement mobilisables.

## Version condensée

| Phase | Référence | Objet | Indicateur | Valeur clé | Type |
|---|---|---|---|---:|---|
| Entraînement | Luccioni et al. (2023) | BLOOM 176B | CO2 | `24.7–50.5 tCO2e` | mesuré / calculé |
| Entraînement | Meta (2024) | Llama 3.1 405B | CO2 | `8,930 tCO2e` | mesuré |
| Entraînement | Meta (2024) | Llama 3.1 405B | GPU-hours | `30.84M` | mesuré |
| Entraînement | Meta (2024) | Llama 3.1 405B | tokens | `>15T` | mesuré |
| Entraînement | Morrison et al. (2025) | série de modèles | CO2 | `493 tCO2e` | mesuré / calculé |
| Entraînement | Morrison et al. (2025) | série de modèles | eau | `2.769 million liters` | mesuré / calculé |
| Entraînement | Morrison et al. (2025) | développement vs run final | part relative | `~50%` de l'impact du run final | calculé |
| Inférence | EPRI (2024) | requête ChatGPT | énergie | `~2.9 Wh/query` | estimé |
| Inférence | Elsworth et al. (2025) | prompt Gemini | énergie | `0.24 Wh/prompt` | mesuré |
| Inférence | Elsworth et al. (2025) | prompt Gemini | CO2 | `0.03 gCO2e/prompt` | mesuré |
| Inférence | Elsworth et al. (2025) | prompt Gemini | eau | `0.26 mL/prompt` | mesuré |
| Inférence | Elsworth et al. (2025) | efficacité en un an | énergie | `33x` moins d'énergie/prompt | mesuré |
| Inférence | Elsworth et al. (2025) | efficacité en un an | CO2 | `44x` moins de CO2/prompt | mesuré |
| Inférence | Ren et al. (2024) | Llama-3-70B, page 500 mots | énergie | `0.0195 kWh` | calculé |
| Inférence | Ren et al. (2024) | Llama-3-70B, page 500 mots | CO2 | `15 gCO2` | calculé |
| Inférence | Ren et al. (2024) | Llama-3-70B, page 500 mots | eau | `0.14 L` | calculé |
| Inférence | Ren et al. (2024) | Gemma-2B-it, page 500 mots | énergie | `0.00024 kWh` | calculé |
| Inférence | Ren et al. (2024) | Gemma-2B-it, page 500 mots | CO2 | `0.18 gCO2` | calculé |
| Eau | Li et al. (2023/2025) | GPT-3 training | eau | `700,000 liters` | calculé |
| Eau | Li et al. (2023/2025) | projection mondiale IA | eau | `4.2–6.6 billion m3` en 2027 | projeté |
| Matérialité | Wang et al. (2024) | e-waste IA générative | flux annuel | `2.6 kt/year` en 2023 | projeté / estimé |
| Matérialité | Wang et al. (2024) | e-waste IA générative | flux annuel | `0.4–2.5 Mt/year` en 2030 | projeté |
| Infrastructure | IEA (2025) | datacenters mondiaux | électricité | `415 TWh` en 2024 | statistique |
| Infrastructure | IEA (2025) | datacenters mondiaux | électricité | `945 TWh` en 2030 | projeté |
| Infrastructure | Berkeley Lab (2025) | datacenters US | électricité | `176 TWh` en 2023 | statistique |
| Infrastructure | Berkeley Lab (2025) | datacenters US | électricité | `325–580 TWh` en 2028 | projeté |

## Version interprétative minimale

### Entraînement

- Le meilleur point d'ancrage open science reste **BLOOM** avec `24.7–50.5 tCO2e`.
- Le meilleur point d'ancrage frontier récent reste **Llama 3.1 405B** avec `8,930 tCO2e`, `30.84M GPU-hours`, `>15T tokens`.
- Le principal enseignement est que l'entraînement d'un frontier LLM peut désormais atteindre des ordres de grandeur de plusieurs milliers de tonnes de CO2e.

### Inférence

- Le meilleur chiffre simple est **`~2.9 Wh/query`** pour ChatGPT (EPRI), mais c'est un ordre de grandeur de vulgarisation.
- Le meilleur chiffre de production réelle est aujourd'hui **Google**:
  - `0.24 Wh/prompt`
  - `0.03 gCO2e/prompt`
  - `0.26 mL/prompt`
- Le principal enseignement est que le coût unitaire peut devenir faible, mais que l'impact agrégé dépend entièrement du volume d'usage.

### Eau

- Le meilleur ancrage sur l'entraînement est **GPT-3: `700,000 liters`**.
- Le meilleur signal prospectif est la projection **`4.2–6.6 billion m3` en 2027** pour l'IA au sens large.

### Infrastructure

- La meilleure base macro reste:
  - `415 TWh` de datacenters mondiaux en `2024`
  - `945 TWh` en `2030`
- Cela signifie que la discussion sur les LLMs ne peut pas être séparée de celle des datacenters.

## Recommandation pour insertion dans l'article

Dans l'article, le plus robuste est d'utiliser:

1. un tableau "entraînement" avec `BLOOM`, `Llama 3.1`, `Morrison`;
2. un tableau "inférence" avec `EPRI`, `Elsworth`, `Ren`;
3. un court tableau "infrastructure" avec `IEA` et `Berkeley Lab`.

Cette structure évite de mélanger:

- les mesures ponctuelles,
- les coûts par requête,
- et les trajectoires macro des datacenters.
