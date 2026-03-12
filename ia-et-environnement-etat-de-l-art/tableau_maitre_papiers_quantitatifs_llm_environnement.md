# Tableau maître des papiers quantitatifs: LLMs et environnement

Ce tableau vise à recenser les références les plus utiles pour une synthèse quantitative sur l'impact environnemental des LLMs.

Colonnes:

- `Phase`: entraînement, inférence, infrastructure, cycle de vie
- `Impact`: CO2, énergie, eau, e-waste, carbone incorporé, mix électrique
- `Type de donnée`: mesuré, calculé, modélisé, projeté
- `Objet`: modèle, service, datacenter, scénario
- `Valeur(s) clé(s)`: valeurs numériques directement mobilisables
- `Utilité`: pourquoi la référence est importante pour la synthèse
- `Limites`: précautions d'interprétation

| Référence | Phase | Impact | Type de donnée | Objet | Valeur(s) clé(s) | Utilité | Limites |
|---|---|---|---|---|---|---|---|
| Strubell, Ganesh, McCallum (2019), *Energy and Policy Considerations for Deep Learning in NLP* | Entraînement | CO2 | Calculé | modèles NLP pré-LLM récents | `192 lb CO2e`; `78,468 lb CO2e`; `626,155 lb CO2e` | Point de départ historique sur la montée du coût environnemental de la NLP moderne | Antérieur à l'ère actuelle des frontier LLMs; matériel et pratiques désormais différents |
| Patterson et al. (2021), *Carbon emissions and large neural network training* | Entraînement | Énergie, CO2 | Calculé / méthodologique | grands réseaux neuronaux | chiffres variables selon matériel et intensité électrique | Référence forte pour la méthodologie de calcul CO2 liée à l'entraînement | Pas centré exclusivement sur les LLMs; comparabilité dépend des hypothèses |
| Luccioni, Viguier, Ligozat (2023), *Estimating the carbon footprint of BLOOM* | Entraînement | CO2 | Mesuré / calculé | BLOOM 176B | `24.7 tCO2e`; `50.5 tCO2e` | L'un des meilleurs cas documentés pour un grand LLM open-weight | Cas fortement dépendant du contexte français et du supercalculateur utilisé |
| Meta (2024), *Llama 3.1 Model Card* | Entraînement | CO2, calcul | Mesuré / publié | Llama 3.1 405B | `8,930 tCO2e`; `30.84M GPU-hours`; `>15T tokens` | Référence centrale pour calibrer les comparaisons entre grands modèles récents | Model card plutôt qu'article revu par les pairs; périmètre exact à lire finement |
| Faiz et al. (2023), *LLMCarbon* | Entraînement + inférence + stockage | CO2 | Modélisé | LLMs généraux | valeurs dépendantes des scénarios; modélisation end-to-end | Très utile pour articuler opérationnel et incorporé | Pas une campagne de mesure directe sur un grand nombre de modèles |
| Liu & Yin (2024), *Green AI: Exploring Carbon Footprints...* | Entraînement + inférence | CO2, énergie | Calculé / comparatif | LLMs multiples | chiffres comparatifs selon hypothèses de mix et d'inférence | Utile pour les arbitrages performance / mitigation / coût carbone | Dépend fortement des hypothèses de calcul |
| Everman et al. (2023), *Evaluating the carbon impact of large language models at the inference stage* | Inférence | CO2 | Calculé / mesuré | inférence LLM | ordres de grandeur par inférence selon cadre retenu | Référence explicitement dédiée à l'inférence | Couverture de modèles et de matériels plus limitée que les benchmarks plus récents |
| Argerich & Patiño-Martínez (2024), *Measuring and improving the energy efficiency of large language models inference* | Inférence | Énergie, CO2 | Mesuré | inférence LLM | chiffres de consommation à l'inférence selon configuration | Référence importante pour la mesure énergétique réelle à l'inférence | Plus orientée efficacité système que comparaisons macro |
| Jegham et al. (2025), *How hungry is AI? Benchmarking energy, water, and carbon footprint of LLM inference* | Inférence | Énergie, CO2, eau | Mesuré / benchmarké | 30 LLMs | benchmark multi-modèles; chiffres énergie/eau/carbone | Référence prioritaire pour séparer l'inférence de l'entraînement | Prépublication; méthodologie à examiner modèle par modèle |
| Elsworth et al. (2025), *Measuring the environmental impact of delivering AI at Google Scale* | Inférence en production | Énergie, CO2, eau | Mesuré | services IA à grande échelle | `0.24 Wh/prompt`; `0.03 gCO2e/prompt`; `0.26 mL/prompt`; `33x` moins d'énergie/prompt; `44x` moins de CO2/prompt en un an | Référence majeure pour la production réelle, pas seulement les benchmarks | Porte sur l'écosystème Google; difficilement généralisable à tous les services |
| Ren et al. (2024), *Reconciling the contrasting narratives on the environmental impact of large language models* | Inférence / comparaison d'unités | Énergie, CO2, eau, coût | Calculé | production d'une page de 500 mots | Gemma-2B-it: `0.00024 kWh`, `0.18 gCO2`, `0.0017 L`; Llama-3-70B: `0.0195 kWh`, `15 gCO2`, `0.14 L`; humain moyen US: `0.85 kWh`, `800 gCO2`, `5.68 L` | Excellent pour discuter les unités d'analyse et les mauvaises comparaisons | Cadre comparatif normatif discutable; ne doit pas être lu comme mesure “universelle” |
| Li, Yang, Islam, Ren (2023/2025), *Making AI Less “Thirsty”* | Entraînement + infrastructure | Eau | Calculé / projeté | GPT-3 et projections IA | GPT-3: `700,000 liters`; projection mondiale IA en 2027: `4.2–6.6 billion m3` | Référence pivot sur l'eau | Une partie importante des résultats relève de scénarios et de projections |
| Morrison et al. (2025), *Holistically evaluating the environmental impact of creating language models* | Cycle de vie de création | CO2, eau, hardware | Mesuré / calculé | série de modèles de langage | `493 tCO2e`; `2.769 million liters`; développement = `~50%` de l'impact de l'entraînement final | Référence clé pour dépasser le seul run final | Prépublication; résultats dépendants de la série de modèles étudiée |
| Wang et al. (2024), *E-waste challenges of generative artificial intelligence* | Cycle de vie / matérialité | E-waste | Projeté / modélisé | IA générative | `2.6 kt/year` en 2023; `0.4–2.5 Mt/year` en 2030; `1.2–5.0 Mt` cumulés; jusqu'à `86%` de réduction possible | Meilleure entrée quantitative actuelle sur la matérialité indirecte | Pas une mesure directe des LLMs seuls; dépend de scénarios d'adoption |
| d'Orgeval et al. (2026), *Generative AI impact assessment through a life cycle analysis of multiple data center typologies* | Cycle de vie + datacenter + inférence | CO2, eau | LCA / modélisé | modèles et architectures de datacenters | `28.4 gCO2e/inference` pour Llama 3.1-405B; `15.4 gCO2e/inference` pour GPT-4o; `4.9 gCO2e/inference` pour DeepSeek-V3; jusqu'à `77.8 million m3/year` d'eau; jusqu'à `79,844 tCO2e/year` | Référence centrale pour relier LLMs, inférence et infrastructure | Résultats très dépendants des typologies de datacenters et du scénario LCA |
| IEA (2025), *Energy and AI* | Infrastructure | Électricité | Projeté / statistique | datacenters mondiaux | `415 TWh` en 2024; `945 TWh` en 2030 | Cadre macro indispensable pour replacer les LLMs dans l'évolution des datacenters | Ne mesure pas l'impact “LLM seul” |
| Berkeley Lab (2025), *2024 U.S. Data Center Energy Usage Report* | Infrastructure | Électricité | Mesuré / projeté | datacenters US | `58 TWh` en 2014; `176 TWh` en 2023; `325–580 TWh` en 2028 | Très utile pour les trajectoires historiques et projections américaines | Ne sépare pas proprement les LLMs du reste des usages |
| EPRI (2024), *Power Demand for Data Centers and Artificial Intelligence* | Infrastructure + inférence | Électricité | Mesuré / estimé | IA dans datacenters, ChatGPT | `10–20%` de part IA dans l'électricité des datacenters; `~2.9 Wh` par requête ChatGPT | Référence simple, lisible, utile pour les ordres de grandeur | Rapport, non article scientifique; dépend de l'hypothèse retenue pour la requête |
| McKinsey (2024), *AI Power: Expanding Data Center Capacity to Meet Growing Demand* | Infrastructure | Puissance, densité rack | Rapport industriel | datacenters IA | `30 MW` -> `200 MW`; `8 kW/rack` -> `17 kW/rack`; projection `30 kW/rack`; `>80 kW/rack` pour certains entraînements de LLMs | Très utile pour matérialiser la transformation physique des datacenters | Source non académique; à utiliser comme contextualisation industrielle |

## Lecture synthétique par bloc

### Entraînement

Références les plus robustes:

- Luccioni et al. (2023)
- Meta (2024)
- Morrison et al. (2025)

Message principal:

- l'entraînement est la partie la mieux documentée;
- les différences de périmètre comptable restent fortes;
- le mix électrique modifie fortement les résultats.

### Inférence

Références les plus robustes:

- Jegham et al. (2025)
- Elsworth et al. (2025)
- Argerich & Patiño-Martínez (2024)
- Ren et al. (2024)

Message principal:

- l'inférence est probablement la composante appelée à dominer l'impact total;
- le coût unitaire par requête peut être faible;
- l'impact agrégé dépend du volume d'usage et de l'infrastructure.

### Eau

Références les plus robustes:

- Li et al. (“Making AI Less Thirsty”)
- Jegham et al. (2025)
- Elsworth et al. (2025)
- Morrison et al. (2025)

Message principal:

- l'eau ne doit plus être traitée comme un indicateur secondaire;
- elle dépend fortement de la localisation et du type de datacenter.

### Matérialité

Références les plus robustes:

- Wang et al. (2024) sur l'e-waste
- Morrison et al. (2025)
- d'Orgeval et al. (2026)
- Faiz et al. (2023)

Message principal:

- la matérialité des LLMs est aujourd'hui surtout documentée via:
  - carbone incorporé,
  - hardware manufacturing,
  - e-waste,
  - LCA des datacenters;
- la quantification directe des terres rares “par LLM” reste encore lacunaire.

## Ce qu'on pourra faire ensuite

Cette base permet maintenant de produire:

1. un tableau de synthèse séparant strictement `training` et `inference`;
2. une section méthodologique distinguant `mesuré`, `calculé`, `modélisé`, `projeté`;
3. des prédictions 2027-2030 sur l'évolution “complexité/impact” des LLMs.
