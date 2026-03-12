# Bibliographie structurée: LLMs et environnement

Cette bibliographie est organisée en quatre blocs:

1. entraînement
2. inférence
3. eau
4. matérialité, e-waste et cycle de vie

L'objectif est de distinguer les références les plus utiles pour une synthèse quantitative. Les entrées ci-dessous privilégient les papiers qui donnent des chiffres mesurés, calculés ou modélisés, ainsi que les rapports d'infrastructure indispensables pour contextualiser les LLMs.

## 1. Entraînement

### Références prioritaires

**Luccioni, A. S., Viguier, S., & Ligozat, A.-L. (2023). _Estimating the carbon footprint of BLOOM, a 176B parameter language model_. Journal of Machine Learning Research, 24(253), 1-15.**

- URL: <https://www.jmlr.org/papers/v24/23-0069.html>
- Intérêt: l'un des meilleurs cas documentés de mesure du coût carbone d'un LLM.
- Chiffres clés:
  - `24.7 tCO2e` en ne considérant que la puissance dynamique
  - `50.5 tCO2e` dans un périmètre plus large
- Usage dans l'article: point d'ancrage empirique pour les comparaisons d'entraînement.

**Meta (2024). _Llama 3.1 Model Card_.**

- URL: <https://huggingface.co/meta-llama/Llama-3.1-405B>
- Intérêt: source primaire récente avec informations d'entraînement à très grande échelle.
- Chiffres clés:
  - `8,930 tCO2e` pour Llama 3.1 405B
  - `30.84M GPU-hours`
  - `>15T tokens`
- Usage dans l'article: calibration des estimations 2026.

**Strubell, E., Ganesh, A., & McCallum, A. (2019). _Energy and Policy Considerations for Deep Learning in NLP_. ACL 2019.**

- URL: <https://aclanthology.org/P19-1355/>
- Intérêt: référence historique sur la montée du coût énergétique en NLP.
- Chiffres clés:
  - `192 lb CO2e`
  - `78,468 lb CO2e`
  - `626,155 lb CO2e`
- Usage dans l'article: base historique pour la trajectoire complexité/impact.

**Patterson, D., Gonzalez, J., Le, Q., Liang, C., Munguia, L.-M., Rothchild, D., So, D., Texier, M., & Dean, J. (2021). _Carbon emissions and large neural network training_.**

- URL: <https://arxiv.org/abs/2104.10350>
- Intérêt: approche méthodologique importante pour relier matériel, énergie et CO2.
- Usage: cadre de comparaison plus robuste que les estimations uniquement fondées sur la puissance.

**Faiz, A., Kaneda, S., Wang, R., Osi, R., Sharma, P., & Krisnadhi, A. (2023). _LLMCarbon: Modeling the end-to-end carbon footprint of large language models_.**

- URL: <https://arxiv.org/abs/2309.14393>
- Intérêt: couvre entraînement, inférence, expérimentation, stockage, carbone opérationnel et incorporé.
- Usage: utile pour construire une synthèse “end-to-end”.

**Morrison, J., Na, C., Fernandez, J., Dettmers, T., et al. (2025). _Holistically evaluating the environmental impact of creating language models_.**

- URL: <https://arxiv.org/abs/2503.05804>
- Intérêt: référence majeure pour une approche holistique.
- Chiffres clés:
  - `493 tCO2e`
  - `2.769 million liters` d'eau
  - le développement représente `~50%` de l'impact de l'entraînement final
- Usage: très forte valeur pour distinguer run final et développement.

### Références secondaires

**Liu, V., & Yin, Y. (2024). _Green AI: Exploring Carbon Footprints, Mitigation Strategies, and Trade-Offs in Large Language Model Training_. Discover Artificial Intelligence.**

- URL: <https://link.springer.com/article/10.1007/s44163-024-00149-w>
- Intérêt: synthèse des arbitrages carbone/performance dans l'entraînement.

**Iftikhar, S., & Davy, S. (2024). _Reducing carbon footprint in AI: A framework for sustainable training of large language models_.**

- Intérêt: utile pour les stratégies de réduction, moins central pour la mesure primaire.

## 2. Inférence

### Références prioritaires

**Everman, B., Villwock, T., Chen, D., Soto, N., et al. (2023). _Evaluating the carbon impact of large language models at the inference stage_. IEEE.**

- Intérêt: papier explicitement centré sur l'inférence.
- Usage: séparation nette entre coût d'entraînement et coût d'usage.

**Argerich, M. F., & Patiño-Martínez, M. (2024). _Measuring and improving the energy efficiency of large language models inference_. IEEE Access.**

- URL: <https://ieeexplore.ieee.org/abstract/document/10549890/>
- Intérêt: mesures et méthodes d'amélioration de l'efficacité énergétique à l'inférence.

**Jegham, N., Abdelatti, M., Koh, C. Y., Elmoubarki, L., et al. (2025). _How hungry is AI? Benchmarking energy, water, and carbon footprint of LLM inference_.**

- URL: <https://arxiv.org/abs/2505.09598>
- Intérêt: référence prioritaire pour une synthèse quantitative de l'inférence.
- Couvre: énergie, eau, carbone.

**Elsworth, C., Huang, K., Patterson, D., Schneider, I., et al. (2025). _Measuring the environmental impact of delivering AI at Google Scale_.**

- URL: <https://arxiv.org/abs/2508.15734>
- Intérêt: probablement la meilleure référence pour l'inférence en production réelle.
- Chiffres clés rapportés:
  - `0.24 Wh/prompt`
  - `0.03 gCO2e/prompt`
  - `0.26 mL d'eau/prompt`
  - `33x` de réduction d'énergie par prompt en un an
  - `44x` de réduction d'empreinte carbone par prompt en un an
- Usage: très forte valeur pour distinguer benchmark et production industrielle.

**Ren, S., Tomlinson, B., Black, R. W., & Torrance, A. W. (2024). _Reconciling the contrasting narratives on the environmental impact of large language models_. Scientific Reports.**

- URL: <https://www.nature.com/articles/s41598-024-76682-6>
- Intérêt: très utile pour comparer des unités d'analyse différentes.
- Usage: essentiel pour discuter les interprétations contradictoires de l'impact des LLMs.

### Références secondaires

**Yang, Y. (2025). _Large Language Models for Energy and Carbon Footprint Optimization: A Comprehensive Survey_.**

- Intérêt: utile comme revue secondaire sur l'inférence et la mesure.

## 3. Eau

### Références prioritaires

**Li, P., Yang, J., Islam, M. A., & Ren, S. (2023, puis 2025). _Making AI Less “Thirsty”: Uncovering and Addressing the Secret Water Footprint of AI Models_.**

- Version initiale: arXiv
- Version de diffusion large: Communications of the ACM
- Intérêt: référence centrale sur le coût en eau de l'IA générative.
- Chiffres clés:
  - GPT-3: `700,000 liters` d'eau douce pour l'entraînement
  - projection mondiale: `4.2–6.6 billion m³` de retrait d'eau en `2027`
- Usage: papier pivot pour la section eau.

**Jegham, N., Abdelatti, M., Koh, C. Y., Elmoubarki, L., et al. (2025). _How hungry is AI? Benchmarking energy, water, and carbon footprint of LLM inference_.**

- Intérêt: l'une des rares références qui traite eau + inférence dans un cadre de benchmark.

**Elsworth, C., Huang, K., Patterson, D., Schneider, I., et al. (2025). _Measuring the environmental impact of delivering AI at Google Scale_.**

- Intérêt: mesure en production réelle avec indicateur d'eau par prompt.

**Morrison, J., Na, C., Fernandez, J., Dettmers, T., et al. (2025). _Holistically evaluating the environmental impact of creating language models_.**

- Intérêt: eau totale de création de modèles, au-delà du seul run final.

### Références secondaires

**Zuccon, G., Scells, H., & Zhuang, S. (2023). _Beyond CO2 emissions: The overlooked impact of water consumption of information retrieval models_.**

- Intérêt: pas exclusivement LLM, mais utile pour la discussion méthodologique sur l'eau.

**d'Orgeval, A., Sheehan, S., Avenas, Q., Assoumou, E., et al. (2026). _Generative AI impact assessment through a life cycle analysis of multiple data center typologies_. Applied Energy.**

- Intérêt: très forte valeur pour relier eau, datacenters et modèles génératifs.
- Chiffres rapportés:
  - jusqu'à `77.8 million m³/year` d'eau selon architecture
- Usage: excellent pour contextualiser l'eau à l'échelle infrastructurelle.

## 4. Matérialité, e-waste et cycle de vie

### Références prioritaires

**Wang, X., Tzachor, A., et al. (2024). _E-waste challenges of generative artificial intelligence_. Nature Computational Science.**

- Intérêt: référence centrale pour la matérialité indirecte de l'IA générative.
- Chiffres clés:
  - `2.6 kt/year` d'e-waste en 2023
  - `0.4–2.5 Mt/year` en 2030
  - `1.2–5.0 Mt` cumulés
  - jusqu'à `86%` de réduction avec des stratégies circulaires
- Usage: meilleure entrée quantitative actuelle sur la matérialité indirecte.

**Morrison, J., Na, C., Fernandez, J., Dettmers, T., et al. (2025). _Holistically evaluating the environmental impact of creating language models_.**

- Intérêt: inclut fabrication du hardware et impact total de développement.
- Usage: référence clé pour embodied carbon.

**Faiz, A., Kaneda, S., Wang, R., Osi, R., Sharma, P., & Krisnadhi, A. (2023). _LLMCarbon_.**

- Intérêt: inclut explicitement le carbone incorporé.

**d'Orgeval, A., Sheehan, S., Avenas, Q., Assoumou, E., et al. (2026). _Generative AI impact assessment through a life cycle analysis of multiple data center typologies_.**

- Intérêt: permet de relier directement LLMs, datacenters et cycle de vie.
- Chiffres rapportés:
  - `28.4 gCO2e/inference` pour Llama 3.1-405B dans un cas étudié
  - `15.4 gCO2e/inference` pour GPT-4o
  - `4.9 gCO2e/inference` pour DeepSeek-V3
- Usage: très utile pour les comparaisons prospectives.

### Angle mort identifié

La littérature directement quantitative sur les **terres rares spécifiques aux LLMs** reste limitée. À ce stade, il est plus rigoureux de parler:

- de **hardware manufacturing**,
- de **carbone incorporé**,
- de **datacenter life cycle assessment**,
- et de **e-waste**,

plutôt que d'affirmer disposer d'une comptabilité robuste des terres rares “par modèle”.

## Références d'infrastructure indispensables

Ces références ne sont pas strictement des papiers sur les LLMs, mais elles sont nécessaires pour la partie prospective.

**International Energy Agency (2025). _Energy and AI_.**

- URL: <https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai>
- Chiffres clés:
  - `415 TWh` pour les datacenters mondiaux en 2024
  - `945 TWh` projetés en 2030

**Lawrence Berkeley National Laboratory (2025). _2024 U.S. Data Center Energy Usage Report_ / summary.**

- URL: <https://newscenter.lbl.gov/2025/01/15/berkeley-lab-report-evaluates-increase-in-electricity-demand-from-data-centers/>
- Chiffres clés:
  - `58 TWh` en 2014
  - `176 TWh` en 2023
  - `325–580 TWh` en 2028

**EPRI (2024). _Power Demand for Data Centers and Artificial Intelligence_.**

- Chiffres clés:
  - `10–20%` de part IA dans l'électricité des datacenters
  - `~2.9 Wh` par requête ChatGPT

**McKinsey (2024). _AI Power: Expanding Data Center Capacity to Meet Growing Demand_.**

- Chiffres clés:
  - `30 MW` -> `200 MW`
  - `8 kW/rack` -> `17 kW/rack`
  - projection `30 kW/rack`

## Conclusion de cadrage

À ce stade, la base bibliographique est suffisamment solide pour passer à une synthèse en deux parties:

- **entraînement**: coût ponctuel, mieux mesuré, plus dépendant du mix électrique et du développement du modèle
- **inférence**: coût diffus, encore sous-mesuré, probablement dominant à terme

Le point le plus fragile reste la **matérialité fine** des LLMs, notamment les terres rares. Le point le plus solide est aujourd'hui la mesure de:

- l'entraînement,
- l'inférence,
- l'eau,
- l'évolution de l'infrastructure des datacenters,
- et les projections d'e-waste.
