# Synthèse analytique: entraînement, inférence et projections 2027-2030

Ce document synthétise la littérature quantitative collectée sur l'impact environnemental des LLMs en distinguant strictement:

1. l'entraînement
2. l'inférence

Il se termine par des projections raisonnées sur les années à venir, à partir de l'évolution conjointe de la complexité des modèles, des volumes d'usage et des infrastructures de datacenters.

## 1. Point méthodologique

La littérature actuelle mélange souvent quatre types de résultats:

- des **mesures directes** sur un modèle ou un service donné;
- des **calculs** fondés sur la consommation électrique observée et l'intensité carbone;
- des **modélisations** ex ante ou end-to-end;
- des **projections** à partir de scénarios d'adoption ou d'infrastructure.

La distinction est essentielle, car les chiffres issus de ces catégories ne portent pas sur le même objet. Une mesure d'entraînement d'un modèle précis n'est pas directement comparable à une projection d'inférence mondiale, ni à une analyse de cycle de vie d'un datacenter. Malgré cela, la littérature est désormais suffisamment riche pour dégager une structure robuste de l'impact environnemental des LLMs.

## 2. Entraînement

### 2.1. Ce qu'on sait le mieux mesurer

L'entraînement est la composante historiquement la mieux documentée, car il se déroule sur une fenêtre temporelle relativement bien définie et implique des ressources de calcul concentrées. Les meilleurs points d'ancrage empiriques sont aujourd'hui:

- **BLOOM 176B**: `24.7 tCO2e` à `50.5 tCO2e` selon le périmètre retenu \\
  Source: Luccioni et al. (2023)
- **Llama 3.1 405B**: `8,930 tCO2e`, `30.84M GPU-hours`, `>15T tokens` \\
  Source: Meta model card (2024)
- **Morrison et al. (2025)**: `493 tCO2e` et `2.769 million liters` d'eau pour un ensemble de modèles, avec environ `50%` d'impact supplémentaire lié au développement au-delà du run final

Le premier résultat important est donc l'extrême dispersion des ordres de grandeur. Cette dispersion ne traduit pas seulement une hausse de la complexité des modèles; elle reflète aussi:

- les différences de périmètre comptable;
- les différences de matériel;
- le nombre de tokens;
- le degré d'optimisation logicielle;
- et surtout la localisation énergétique du calcul.

### 2.2. Ce qui explique la croissance de l'impact

Trois variables ressortent systématiquement.

**1. La taille effective du modèle**

Le nombre de paramètres reste un indicateur grossier mais utile. Il doit toutefois être corrigé pour les architectures MoE, où les paramètres totaux surestiment la charge réelle par token si une faible fraction seulement est activée.

**2. Le volume de données d'entraînement**

Les LLMs contemporains sont de moins en moins caractérisés seulement par leur nombre de paramètres et de plus en plus par les volumes de tokens ingérés. Le cas de Llama 3.1 (`>15T tokens`) ou de Qwen2.5 (`jusqu'à 18T tokens`) montre que la montée en charge des corpus devient un déterminant central du coût.

**3. Le mix électrique**

La même charge de calcul peut produire des émissions très différentes selon le pays. C'est ce que montre clairement le tableau comparatif 2026 construit dans le projet: une relocalisation contrefactuelle d'un entraînement vers un mix proche du mix français réduit l'empreinte carbone d'un ordre de grandeur dans plusieurs cas.

### 2.3. Ce qu'on sait moins bien mesurer

La littérature tend encore à sous-estimer trois dimensions de l'entraînement:

- les itérations de développement avant le run final;
- le carbone incorporé dans le matériel;
- la contribution des opérations de stockage, d'orchestration et d'infrastructure.

Sur ce point, **Morrison et al. (2025)** et **LLMCarbon** sont des références particulièrement importantes, car elles déplacent l'analyse au-delà du seul événement d'entraînement final.

### 2.4. Diagnostic synthétique sur l'entraînement

Le diagnostic le plus robuste est le suivant:

- l'entraînement des LLMs frontier reste un événement environnemental majeur;
- son impact unitaire augmente fortement avec la taille et les tokens;
- mais sa contribution relative à l'impact total pourrait diminuer à mesure que l'inférence se généralise.

Autrement dit, l'entraînement est aujourd'hui la partie la mieux mesurée, mais probablement pas celle qui dominera nécessairement l'empreinte totale à moyen terme.

## 3. Inférence

### 3.1. Pourquoi l'inférence devient centrale

L'inférence est plus difficile à mesurer que l'entraînement, mais elle est probablement la composante la plus importante pour l'avenir. La raison est simple: un entraînement est ponctuel; l'inférence est répétée à grande échelle, parfois en continu, sur des millions ou des milliards de requêtes.

La littérature récente fournit désormais plusieurs ancrages quantitatifs:

- **EPRI (2024)**: `~2.9 Wh` par requête ChatGPT
- **Elsworth et al. (2025)**: `0.24 Wh/prompt`, `0.03 gCO2e/prompt`, `0.26 mL/prompt` dans un cadre Google à grande échelle
- **Ren et al. (2024)**: pour une page de 500 mots, `0.0195 kWh`, `15 gCO2`, `0.14 L` pour Llama-3-70B
- **d'Orgeval et al. (2026)**: ordres de grandeur par inférence via LCA de datacenters, dont `28.4 gCO2e/inference` pour Llama 3.1-405B dans un cas étudié

Ces chiffres paraissent parfois contradictoires. En réalité, ils n'ont pas le même périmètre:

- certains sont par prompt court;
- d'autres par page de 500 mots;
- d'autres encore intègrent l'architecture du datacenter dans une logique de cycle de vie.

### 3.2. Pourquoi les chiffres d'inférence varient autant

Les écarts proviennent principalement de six facteurs:

- taille du modèle;
- longueur d'entrée et de sortie;
- nombre de tokens générés;
- efficacité de l'infrastructure;
- degré de mutualisation ou de batching;
- périmètre retenu pour le calcul environnemental.

La littérature récente montre cependant un point très important: **le coût unitaire d'inférence peut diminuer rapidement**. Elsworth et al. rapportent ainsi des réductions de `33x` en énergie par prompt et `44x` en CO2e par prompt en un an dans un environnement industriel Google. Cela signifie que les trajectoires futures ne dépendront pas uniquement de la croissance des modèles, mais du rapport entre:

- croissance du volume d'usage,
- progrès d'efficacité,
- et intensité carbone des infrastructures.

### 3.3. Le rôle des datacenters

L'inférence fait passer la question environnementale des LLMs d'un problème de calcul ponctuel à un problème d'**infrastructure continue**.

Les chiffres macro les plus solides sont ici:

- `415 TWh` pour les datacenters mondiaux en `2024` (IEA)
- `945 TWh` projetés en `2030` (IEA)
- `58 TWh` en `2014`, `176 TWh` en `2023`, `325–580 TWh` en `2028` pour les datacenters américains (Berkeley Lab)
- `10–20%` de l'électricité des datacenters déjà imputable à l'IA selon EPRI

Ces résultats ne mesurent pas les LLMs seuls, mais ils confirment que l'inférence de modèles génératifs ne peut plus être pensée indépendamment de la transformation physique des datacenters.

### 3.4. Diagnostic synthétique sur l'inférence

Le diagnostic le plus probable est le suivant:

- l'inférence est encore sous-mesurée;
- son coût unitaire peut baisser vite;
- mais son impact total est susceptible de croître fortement si la demande explose plus vite que l'efficacité.

En d'autres termes, **l'inférence est la composante la plus incertaine, mais aussi la plus susceptible de devenir dominante**.

## 4. Eau

La littérature sur l'eau confirme cette différence entre entraînement et inférence.

Du côté de l'entraînement, l'étude de **Li et al.** sur l'empreinte hydrique de l'IA fournit un résultat emblématique:

- `700,000 liters` d'eau douce pour l'entraînement de GPT-3

Du côté de l'inférence, les mesures récentes en production montrent au contraire des coûts unitaires très faibles, par exemple:

- `0.26 mL/prompt` chez Google (Elsworth et al., 2025)

Le point critique est donc le même que pour l'énergie: un coût unitaire faible peut se traduire par un coût agrégé élevé si les volumes de service deviennent massifs. L'eau est en outre plus dépendante que le carbone de la **localisation** et du **stress hydrique local**, ce qui rend les comparaisons globales encore plus délicates.

## 5. Matérialité, e-waste et limites actuelles

La littérature quantitative sur les **terres rares spécifiques aux LLMs** reste encore trop faible pour soutenir des comparaisons solides. En revanche, la matérialité indirecte des LLMs peut être documentée à partir de trois familles de travaux:

- analyses de cycle de vie des datacenters;
- carbone incorporé du matériel;
- projections d'e-waste.

La référence la plus claire est actuellement **Wang et al. (2024)** sur l'e-waste de l'IA générative:

- `2.6 kt/year` en 2023
- `0.4–2.5 Mt/year` en 2030
- `1.2–5.0 Mt` cumulés
- jusqu'à `86%` de réduction avec stratégies circulaires

Cette littérature ne quantifie pas directement les terres rares par LLM. La conclusion rigoureuse est donc qu'il faut, à ce stade, traiter cette dimension par les proxys de cycle de vie et de déchets plutôt que par une comptabilité minérale précise des modèles.

## 6. Synthèse comparative: entraînement versus inférence

| Dimension | Entraînement | Inférence |
|---|---|---|
| Temporalité | Ponctuelle, concentrée | Continue, répétée |
| Niveau de documentation | Relativement bon | Encore incomplet mais en forte progression |
| Déterminants majeurs | paramètres, tokens, matériel, mix électrique | taille du modèle, longueur de requête, volume d'usage, batching, datacenter |
| Risque principal d'interprétation | confondre périmètres comptables | comparer des unités incompatibles |
| Tendance future probable | coût unitaire encore élevé pour les frontier models | impact total potentiellement dominant |

La formulation la plus défendable à ce stade est donc:

- **l'entraînement** reste le meilleur objet pour documenter le coût unitaire maximal d'un LLM;
- **l'inférence** est le meilleur candidat pour expliquer l'impact total des LLMs à l'échelle du système dans les années à venir.

## 7. Projections 2027-2030

Les projections doivent rester conditionnelles. Il n'existe pas aujourd'hui de base suffisamment homogène pour annoncer une trajectoire unique des émissions mondiales des LLMs. En revanche, plusieurs tendances sont suffisamment robustes pour formuler des scénarios argumentés.

### 7.1. Tendance 1: l'inférence deviendra probablement dominante

Les preuves convergent:

- amélioration très rapide du coût par prompt en production;
- explosion des usages conversationnels;
- montée de l'IA dans la demande électrique des datacenters;
- quasi-doublement attendu de la consommation mondiale des datacenters entre 2024 et 2030.

Même si le coût environnemental par requête diminue, la croissance du nombre de requêtes, d'agents et d'intégrations logicielles pourrait faire croître l'impact total.

### 7.2. Tendance 2: le coût par modèle continuera d'augmenter au sommet de la distribution

Pour les modèles frontier, les signaux restent ceux d'une hausse:

- plus de tokens;
- infrastructures plus denses;
- datacenters plus puissants;
- volumes d'expérimentation encore mal comptés.

Il est donc plausible que de futurs very-large LLMs dépassent encore les ordres de grandeur actuels de plusieurs milliers de tonnes de CO$_2$e par entraînement, même si les gains d'efficacité ralentissent cette croissance.

### 7.3. Tendance 3: la localisation énergétique deviendra un paramètre central

Les écarts observés entre mix français, américain et chinois montrent déjà qu'une même charge de calcul peut produire des empreintes radicalement différentes. On peut donc s'attendre à une polarisation croissante entre:

- des entraînements relocalisés vers des mix bas carbone;
- et des services d'inférence déployés au plus près des marchés, avec des profils carbone plus hétérogènes.

### 7.4. Tendance 4: l'eau et le cycle de vie monteront en importance

Le carbone restera l'indicateur dominant du débat public, mais la littérature scientifique devrait progressivement intégrer davantage:

- l'eau;
- le carbone incorporé;
- l'e-waste;
- l'impact des datacenters comme systèmes physiques complets.

Autrement dit, la tendance va vers une **écologisation méthodologique** de l'évaluation des LLMs: moins centrée sur un seul chiffre carbone, plus orientée cycle de vie.

## 8. Conclusion

La littérature quantitative sur les LLMs et l'environnement permet désormais d'affirmer trois choses avec un niveau de confiance raisonnable.

Premièrement, l'empreinte d'entraînement des grands modèles est réelle, mesurable et parfois massive, mais elle dépend fortement du périmètre comptable et du mix électrique.

Deuxièmement, l'inférence est la composante la plus stratégique pour les années à venir: moins visible, plus diffuse, mais potentiellement dominante à l'échelle agrégée.

Troisièmement, les projections les plus crédibles ne reposent pas sur l'idée d'un impact linéairement proportionnel à la taille des modèles. Elles dépendent d'un système de variables couplées: complexité des modèles, volume d'usage, efficacité de l'infrastructure, localisation énergétique et cadence de renouvellement du matériel.

La prochaine étape logique consiste donc à construire, à partir du tableau maître, un **tableau de synthèse article-ready** séparant strictement `training` et `inference`, puis à dériver un petit nombre de **scénarios prospectifs 2027-2030** appuyés sur les chiffres les plus robustes.
