# Grille d'extraction des donnees quantifiees: LLM et environnement

Document de cadrage pour la reprise de la publication. L'objectif n'est pas de produire une revue narrative supplementaire, mais de definir exactement quelles donnees numeriques extraire des papiers recents, en priorite ceux reperes sur Google Scholar entre 2024 et 2026.

## Principe directeur

La litterature melange souvent quatre objets differents:

- le cout d'entrainement d'un modele;
- le cout unitaire d'une inference;
- l'impact de l'infrastructure de datacenter;
- les projections systemiques a horizon 2027-2030.

Ces objets ne sont pas directement comparables. La grille d'extraction doit donc separer strictement:

- l'objet mesure;
- l'unite;
- le perimetre du calcul;
- le statut de la donnee: mesuree, calculee, modelisee, projetee.

## Types de donnees a extraire

### 1. Donnees de carbone operationnel d'entrainement

Variables pertinentes:

- emissions totales d'entrainement en `gCO2e`, `kgCO2e` ou `tCO2e`;
- emissions du run final seulement;
- emissions du developpement complet, y compris essais, ablations, debugging et relances;
- emissions scopees ou descopees selon le mix electrique local;
- emissions rapportees par token, par GPU-hour, par parametre ou par FLOP si disponibles.

Pourquoi c'est central:

- c'est le point d'ancrage le plus solide pour comparer des LLMs frontier ou open;
- c'est aussi la variable la plus souvent citee a tort sans precision sur le perimetre.

Papiers ou cette famille apparait clairement:

- Luccioni et al. (2023), BLOOM;
- Liu and Yin (2024);
- Morrison et al. (2025);
- Jeanquartier et al. (2026);
- model cards comme Meta Llama 3.1 (2024), a utiliser comme source primaire annexe.

### 2. Donnees d'energie d'entrainement

Variables pertinentes:

- consommation electrique totale en `Wh`, `kWh`, `MWh` ou `GWh`;
- puissance moyenne ou pic de puissance pendant l'entrainement;
- energie IT seule vs energie facility;
- energie par GPU, par noeud, par heure, par token ou par etape;
- duree totale d'entrainement.

Pourquoi c'est central:

- le carbone derive souvent de l'energie; quand l'energie est fournie explicitement, le calcul est plus auditable;
- cela permet de recomposer les emissions avec un autre mix electrique.

Papiers ou cette famille apparait clairement:

- Patterson et al. (2021), encore utile methodologiquement;
- Liu and Yin (2024);
- Morrison et al. (2025);
- Jeanquartier et al. (2026).

### 3. Donnees de charge de calcul et d'echelle du modele

Variables pertinentes:

- nombre de parametres;
- nombre de tokens d'entrainement;
- GPU-hours ou TPU-hours;
- nombre et type d'accelerateurs;
- precision numerique: FP32, BF16, FP16, INT8, INT4;
- estimation des FLOPs si fournie;
- taille du contexte;
- batch size, sequence length, throughput.

Pourquoi c'est central:

- ces variables expliquent les ordres de grandeur environnementaux;
- elles sont indispensables pour normaliser les comparaisons entre papiers.

Papiers ou cette famille apparait clairement:

- Meta Llama 3.1 (2024);
- Morrison et al. (2025);
- plusieurs papiers d'inference 2024-2025 qui rapportent `J/token` ou `tokens/s`.

### 4. Donnees d'inference: energie unitaire

Variables pertinentes:

- energie par prompt;
- energie par reponse;
- energie par token genere;
- energie pour une longueur de prompt donnee, par exemple `300 tokens`, `500 mots`, `1k tokens`;
- energie selon le materiel, le framework de serving et la quantization;
- energie sous differents regimes: single request, batch, throughput soutenu, latency ciblee.

Pourquoi c'est central:

- la publication doit distinguer rigoureusement cout unitaire et impact aggregate;
- c'est aujourd'hui le meilleur point d'entree pour une comparaison inter-modeles.

Papiers ou cette famille apparait clairement:

- Argerich and Patino-Martinez (2024);
- Jegham et al. (2025);
- Poddar et al. (2025);
- Fernandez et al. (2025);
- Elsworth et al. (2025).

### 5. Donnees d'inference: carbone unitaire

Variables pertinentes:

- `gCO2e/prompt`;
- `gCO2e/requete`;
- `gCO2e/page generee`;
- `gCO2e/token`;
- reduction relative du carbone grace a l'optimisation ou au deplacement de charge;
- sensibilite au mix electrique et a l'heure de la journee si le papier la donne.

Pourquoi c'est central:

- beaucoup de controverses publiques portent sur cette unite;
- c'est aussi la variable la plus sensible aux hypotheses de localisation et de temporalite.

Papiers ou cette famille apparait clairement:

- Everman et al. (2023), utile comme base;
- Ren et al. (2024);
- Jegham et al. (2025);
- Elsworth et al. (2025);
- Hoxha et al. (2025) pour les cadres deployment-aware.

### 6. Donnees de consommation d'eau

Variables pertinentes:

- eau de retrait (`water withdrawal`);
- eau consommee (`water consumption`) si distinguee;
- `mL/prompt`, `L/prompt`, `L/training run`, `m3/year`;
- eau directe de refroidissement vs eau indirecte liee a la production d'electricite;
- WUE (`Water Usage Effectiveness`);
- dependance a la localisation ou au stress hydrique local.

Pourquoi c'est central:

- l'eau est devenue un axe empirique majeur dans la litterature recente;
- c'est aussi un indicateur tres heterogene methodologiquement.

Papiers ou cette famille apparait clairement:

- Li et al. (2023/2025), sur GPT-3 et projections;
- Jegham et al. (2025);
- Elsworth et al. (2025);
- Morrison et al. (2025);
- d'Orgeval et al. (2026).

### 7. Donnees d'infrastructure et de datacenter

Variables pertinentes:

- PUE (`Power Usage Effectiveness`);
- WUE;
- type de refroidissement;
- localisation geographique;
- intensite carbone du reseau en `gCO2e/kWh`;
- facteur d'utilisation des machines;
- densite de puissance par rack;
- consommation electrique annuelle du datacenter ou du parc de datacenters.

Pourquoi c'est central:

- ces variables expliquent une part importante des ecarts entre papiers;
- elles permettent de reconnecter les LLMs au systeme physique qui les supporte.

Papiers ou cette famille apparait clairement:

- Jegham et al. (2025), usage de PUE et WUE;
- Elsworth et al. (2025), production Google;
- d'Orgeval et al. (2026), typologies de datacenters;
- IEA (2025) et Berkeley Lab (2025), pour le contexte macro.

### 8. Donnees de cycle de vie et carbone incorpore

Variables pertinentes:

- carbone incorpore du hardware;
- part relative fabrication vs usage;
- impact du developpement en amont du run final;
- duree de vie du materiel;
- allocations par serveur, par GPU ou par inference;
- ACV multi-indicateurs si presente.

Pourquoi c'est central:

- la litterature recente se deplace d'une lecture "run unique" vers une lecture cycle de vie;
- sans ces donnees, on sous-estime le poids du materiel et du developpement.

Papiers ou cette famille apparait clairement:

- Faiz et al. (2023), LLMCarbon;
- Morrison et al. (2025);
- d'Orgeval et al. (2026).

### 9. Donnees de materialite et de dechets

Variables pertinentes:

- e-waste annuel ou cumule;
- masse de materiaux ou de dechets en `kg`, `t`, `kt` ou `Mt`;
- scenario baseline vs scenario circulaire;
- duree de renouvellement des accelerateurs;
- part attribuable a l'IA generative ou aux LLMs.

Pourquoi c'est central:

- c'est la meilleure entree quantitative disponible pour la materialite;
- en revanche, la litterature ne permet pas encore une comptabilite robuste des terres rares par LLM.

Papiers ou cette famille apparait clairement:

- Wang et al. (2024);
- Morrison et al. (2025) de maniere plus indirecte;
- d'Orgeval et al. (2026) si l'ACV detaille les composants.

### 10. Donnees de projection et de changement d'echelle

Variables pertinentes:

- projection de demande electrique ou hydrique a horizon `2027`, `2028`, `2030`;
- scenarios de diffusion de l'IA generative;
- volume de prompts, requetes, utilisateurs ou agents;
- gains d'efficacite annuels;
- scenarii de relocalisation vers des mixes bas carbone.

Pourquoi c'est central:

- la publication vise aussi l'environnement futur des LLMs, pas seulement l'etat statique des mesures;
- ces donnees doivent etre clairement etiquetees comme projections et jamais melangees aux mesures.

Papiers ou cette famille apparait clairement:

- Li et al. (2023/2025);
- Wang et al. (2024);
- Elsworth et al. (2025) pour les gains d'efficacite observes;
- IEA (2025);
- Berkeley Lab (2025).

### 11. Metadonnees methodologiques indispensables

Ces donnees ne sont pas des impacts, mais doivent etre extraites systematiquement car elles conditionnent toute comparabilite:

- type d'etude: mesure, benchmark, estimation, modele, ACV, projection;
- niveau d'analyse: modele, prompt, service, datacenter, ecosysteme;
- unite d'analyse exacte;
- frontiere systeme incluse et exclue;
- methode de calcul du carbone;
- source de l'intensite carbone;
- taille du prompt et de la sortie;
- type de materiel et version logicielle;
- date de la mesure ou periode observee;
- incertitude, intervalle, scenario bas/haut.

## Hierarchie de priorite pour l'etude

Toutes les donnees ne se valent pas. Pour la publication, l'ordre de priorite devrait etre:

1. energie, carbone et eau par objet bien defini;
2. variables d'echelle qui expliquent ces impacts: tokens, GPU-hours, type de GPU, longueur de sequence;
3. variables d'infrastructure: PUE, WUE, intensite carbone, localisation;
4. cycle de vie et materialite;
5. projections macro, a tenir a part.

## Format d'extraction minimal par papier

Pour chaque article scientifique, il faut pouvoir remplir au minimum les champs suivants:

- reference bibliographique complete;
- annee;
- type d'etude;
- phase analysee: entrainement, inference, infrastructure, cycle de vie;
- objet exact mesure;
- variables quantitatives presentes;
- valeur numerique;
- unite;
- perimetre retenu;
- hypothese de mix electrique ou localisation;
- materiel et configuration;
- comparabilite avec les autres papiers: forte, moyenne, faible;
- citation exacte de la phrase ou du tableau source a verifier ensuite dans le PDF.

## Papiers 2024-2026 a mobiliser en priorite

### Noyau principal

- Liu and Yin (2024): entrainement, carbone, energie, arbitrages methodologiques.
- Argerich and Patino-Martinez (2024): inference, energie, efficacite systeme.
- Ren et al. (2024): conversion par page, energie, carbone, eau, discussion des unites.
- Morrison et al. (2025): creation de modeles, carbone, eau, developpement, hardware.
- Jegham et al. (2025): benchmark inference multi-modeles, energie, eau, carbone, PUE, WUE.
- Elsworth et al. (2025): mesures de production, `Wh/prompt`, `gCO2e/prompt`, `mL/prompt`, gains d'efficacite.
- Poddar et al. (2025): benchmarking inference energy.
- Fernandez et al. (2025): effets des optimisations de serving sur l'energie.
- d'Orgeval et al. (2026): ACV de datacenters et comparaison de LLMs.
- Jeanquartier et al. (2026): evaluation carbone de language models en croisant benchmark et cas d'etude.

### Noyau secondaire

- Wang et al. (2024): e-waste et scenarios materiels.
- Li et al. (2023/2025): eau et projections.
- IEA (2025): electricite des datacenters a l'echelle mondiale.
- Berkeley Lab (2025): electricite des datacenters aux Etats-Unis.

## Conclusion operationnelle

Pour notre etude, il faut donc viser non pas "toutes les donnees environnementales" au sens vague, mais onze familles de donnees clairement separables. Les plus decisives sont:

- carbone d'entrainement;
- energie d'entrainement;
- charge de calcul et echelle;
- energie d'inference;
- carbone d'inference;
- eau;
- variables d'infrastructure;
- cycle de vie et carbone incorpore.

Si on extrait proprement ces huit blocs en premier, on aura deja une base solide, quantitative et non narrative pour l'article. Les projections macro et la materialite devront venir ensuite, avec un marquage explicite des hypotheses et des niveaux d'incertitude.
