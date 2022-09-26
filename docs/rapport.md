# Rapport de projet

## Groupe 03
* Samy Mouloud NEHLIL 21113646
* Amel BELDJILALI 21115553

## Description des choix importants d'implémentation

Jeu sans budget et déplacement: 

Pour cette première partie du projet, on a implémenté les stratégies (aléatoire, deux variantes de tétu: tétu aléatoire et tétu uniforme, stochastique expert, tit-for-tat, réponse améliorante, fictitious play et une nouvelle stratégie qu'on a nommé focus). Pour implémenter ces stratégies, on a défini les fonctions suivantes:

I\ Dans le module util.py:  

    1) init_alea_parti(nb_obj, nb_militants_p): Prend en entrée le nombre d'élécteurs et le nombre de militants. Chaque militant est affecté aléatoirement à un élécteur en utilisant la fonction randint de numpy.

    2) init_uniform(nb_obj, nb_militants): Retourne une distribution uniforme des militants sur l'ensemble des élécteurs. Par exemple: si on a 9 militants et 5 élécteurs, on aura l'affectation suivante: (2, 2, 2, 2, 1).

    3) calcul_score_jour(strategy1, strategy2): Calcule le score du jour des deux partis étant données leurs stratégies respectives pour le jour.

    4) stochastique_expert(): Choisit aléatoirement une startégie parmis celles impléméntées en utilisant la fonction random.choice().

    5) prochainCoup(mesCoups,adversCoups,nom): Retourne le prochaine coup (stratégie) pour un partie étant donnés l'historique des stratégies utilisées par le parti et l'historique du parti adversaire et le nom de la stratégie. Les coups possibles sont: aleatoire qui utilise la fonction init_alea_parti, tetu qui commence par une stratégie aléatoire et la répète jusqu'à la fin du jeu, tetu uniforme qui donne toujours une affectation uniforme via la fonction init_uniform, titfortat qui retourne la dernière stratégie jouée par l'adversaire, better_response qui fourni une meilleur réponse par rapport au dernier coup joué par l'adversaire, focus qui affecte le plus grand nombre possible de militants à la moitié des élécteurs et aucun militant à l'autre moitié et best_response qui retourne la meilleur stratégie en réponse au dernier coup de l'adversaire.
    Explication des stratégies better_response, focus et best_response:

    *** Stratégie better_response: L'idée de cette stratégie est celle vue en TD c.à.d: On prend la moitié des secteurs auxquels l'adversaire a envoyé le plus de militants dan son coup précédent et on n'y envoie aucun militant. Et on envoie le plus de militants possibles (au moins un de plus que l'adversaire) aux secteurs auxquels l'adversaire a envoyé le moins de militants dans son coup précédent. 
    Par exemple: Si le coup précédent de notre adversaire avec 5 secteurs et 15 militants était: (10, 3, 0, 1, 1), la stratégie best_response nous fournira l'affectation suivante: (0, 0, 5, 5, 5).

    *** Stratégie focus: Ici le joueur concentre ses efforts sur la moitié des secteurs et laisse l'autre moitié vide (n'envoie aucun militant). Par exemple avec 5 secteurs et 15 militants, la stratégie focus donne l'affectation suivante: (5, 5, 5, 0, 0).

    ** Startégie best_response: La fonction best_response() utilise la fonction combinations() qui retourne toutes les combinaisons possibles d'affectation des militants sur les secteurs (en s'assurant que la somme des militants affectés est bien 7 (Le nombre de militants dans notre exemple)) et calcule le score obtenu en jouant chacune de ces startégies (combinaisons) par rapport à la dernière stratégie de l'adversaire. La fonction retourne en sortie la stratégie qui fournie le meilleur score par rapport à celui de l'adversaire.

    6) str_to_obj(strategy, nb_militants_p): Affecte à chaque militant un élécteur étant donné la stratégie (combien de militant affecter à chacun des élécteurs) et le nombre de militants. Par exemple si on a 10 militants affectés à 4 élécteurs selon la stratégie (5, 3, 2, 0), la fonction str_to_obj rend la liste suivante: [0, 0, 0, 0, 0, 1, 1, 1, 2, 2] c.à.d que les 5 premiers militants seront afféctés à l'élécteur 0 (le premier), les 3 suivants au 2ème et les deux restants au 3ème alors que le dernier élécteurs n'aura aucun militant.

II\ Dans le module fictitious.py: 
    Pour implémenter la stratégie fictitious play, on avait besoin de sauvegarder l'historique du nombre de militants dans chaque secteur (élécteur) pour l'adversaire. Pour cela, on a défini une matrice matProb de taille (nombre de secteurs X nombre de militants): la case (i,j) contient une probabilité calculé sur les jours passées que l'adversaire affecte au secteur (i) j militants. Par exemple, si matProb[1, 2]= 0,2 aprés 10 jours alors on comprends que l'adversaire a affecté 2 de ses militants au secteur numéro 1 20% du temps (2 jours dans ce cas).

    On a ensuite implémenté les fonctions suivantes:

    1) updateMatProba(strategy, jours_passes): Cette fonction met à jour les probabilités dans la matrice matProb en prenant en entrée la stratégie jouée par l'adversaire (nombre de militants afféctés à chaque secteur) et le nombre de jour passés.

    2) gain_espere(maStrategy): Retourne le gain espéré pour le joueur s'il joue la stratégie maStrategy au coup suivant en se basant sur les probabilités stoquées dans la matrice matProb. Pour mieux comprendre comment se fait le calcul, prenons l'exemple suivant:
    Si on a 2 secteurs (numérotés 0 et 1) et 3 militants pour chaque parti: Après 10 jours de jeu, on obtient la matrice de probabilités suivante pour le joueur 2:
    |0.1|0.9| 0 | 0 |
    | 0 |0.1|0.1|0.8|
    Ce qui se traduit par:
    - Pour le secteur 0: Il y a une probabilité de 10% que l'adversaire n'affecte aucun militant à cet élécteur et un probabilité de 90% qu'il lui affecte 1 militant.
    - Pour le secteur 1: Il y a une probabilité de 10% que l'adversaire affecte 1 militant à cet élécteur et un probabilité de 10% qu'il lui affecte 2 militants et une probabilité de 80% qu'il lui affecte 3 militants.
    Si maStartegy = (1, 2) alors le gain espéré est: (0.1*1 + 0.9*1) pour le secteur 0 car 1 > 0 et 1 >= 1 et (0 * 1 + 0.1*1 + 0.1*1) pour le secteur 1 car 2 > 0 et 2 > 1 et 2 >= 2. La fonction retourne le vecteur des gains. 

    3) fictitious(mesCoups,adversCoups): Cette fonctionne utilise la fonction gain_espere pour calculer le gain total (somme des gains dans le vecteur retourné par gain_espere) de chacune des stratégies possibles pour le joueur (celles présentes dans util.py) et choisit celle qui fournit le meilleur gain (max).


Jeu avec budget et déplacement: Dans cette deuxième partie du projet qu'on a implémenté dans les deux fichiers budget.py et budget2.py (les deux variantes du budget), on a supposé que les élécteurs se déplacent dans un autre secteur à la fin de chaque jour et qu'il y a un budget de pas à respecter.

Variante 1: Chaque militant a son propre budget fixe qu'il ne doit pas dépasser dans une journée.

Variante 2: Le budget concerne la campagne entière: chaque jour le parti paye comme prix la somme des trajets réalisés par ses militants dans la journée. Le but est donc de minimiser les distances parcourues par chaque militant.

Afin de satisfaire ces conditions, on a implémenté les fonctions suivantes:

III\ Dans le fichier budgetV1.py: Pour la première variante:        

    1) reaffect(): Qui reaffecte les élécteurs à des secteurs différents à la fin de chaque journée. Pour cela, on stocke les positions possibles dans chaque secteur dans le tableau pos_secteur puis en utilisant la fonction randint du module random, pour chaque élécteur on choisit un secteur (différent de celui où il était le jour d'avant) aléatoirement et on le positionne dans ce secteur (position aléatoire dans le secteur).

    2) cout_chemin(posPlayer, posTarget): Calcule le coût de déplacement -nombre de pas-  d'un militant d'une position initiale posPlayer à une position finale posTarget en utilisant la distance de manhattan.

    3) pick_from_possible_moves(myPosition, myBudget): Choisit pour un militant donné situé à la position myPosition un élécteur parmi les élécteurs qu'il peut atteindre étant donné son budget myBudget et ceci en calculant le coût du chemin entre le militant et chaqun des élécteurs. Par exemple, si on a 5 élécteurs et que la fonction cout_chemin retourne 10, 15, 13, 6, 2 (les distances à parcourir pour chaque chemin), et sachant que myBudget = 12, on obtient le tableau suivangt: [0, 3, 4] (les indices des élécteurs que le militant peut atteindre avec son budget) puis on choisit un de ces élécteurs aléatoirement et on retourne la nouvelle position du militant (celle de l'élécteur qu'il a comme but). Si aucun élécteur n'est atteignable avec myBudget, le militant reste dans la même position.

    4) strategy_with_budget(posPlayers, budget): Cette fonction retourne une stratégie aléatoire en affectant à chaque militant du parti un objectif (élécteur) aléatoire avec la fonction pick_from_possible_moves.

IV\ Dans le fichier budgetV2.py: Pour la deuxième variante: 

    On a gardé les fonctions reaffect(), cout_chemin(posPlayer, posTarget) pour la réaffectation des élécteurs dans de différents secteurs et le calcul du coût, et on rajoute la fonction suivante:

    5) choose_nearest_obj(posPlayers): Cette fonction choisit l'objectif le plus proche pour chaque militant du parti en utilisant la fonction cout_chemin et ceci afin de minimiser le prix que le parti aura à payer à la fin de la journée. Afin de ne pas concentrer tous ses efforts sur le même secteur si tous les militants d'un parti se trouvent le plus proche d'un même élécteur, on rajoute la condition suivante: Ne pas affecter plus de trois militants au même élécteur.

    Ensuite, on lance le jeu et à la finc de chaque jour on met à jour le budget du parti en lui rajoutant la somme des pas de chaque militant (le budget du partie 1 est sauvegardé dans la variable budget1 et celui du porti 2 dans la variable budget2 qui sont initialisée à 0 au début de la campagne).



## Description des résultats
Pour évaluer les différentes stratégies, on organise des confrontations. On répète les campagnes de 20 jours 30 fois et on observe les réseultats obtenus.

1) Tétu VS aléatoire: Sur les 30 campagnes:
    Tétu a remporté le vote 10 fois.
    Aléatoire a remporté le vote 19 fois.
    Il y avait une seule fois où les deux stratégies ont eu le même score.

2) Tit-for-tat VS aléatoire:
    Tit-for-tat a remporté le vote 16 fois.
    Aléatoire a remporté le vote 10 fois.
    Il y avait 4 fois où les deux stratégies ont eu le même score.

3) Better response VS tit-for-tat:
    Better reponse a remporté le vote 16 fois.
    Tit-for-tat a remporté le vote 11 fois.
    Il y avait 3 fois où les deux stratégies ont eu le même score.

4) Aléatoire VS better response: (sur 35 campagnes)
    Aléatoire a remporté le vote 17 fois.
    Better response a remporté le vote 13 fois.
    Il y avait 5 fois où les deux stratégies ont eu le même score.

5) Fictitious Play VS better response:
    Better response a gagné 30 fois sur 30 (100%).

6) Fictitious Play VS stochastique expert:
    Fictitious Play a remporté le vote 8 fois.
    Stochastique expert a remporté le vote 21 fois.
    Les deux stratégies ont eu le même score une seule fois.

7) Better response VS stochastique expert:
    Better response a remporté le vote 27 fois.
    Stochastique expert a remporté le vote 3 fois.

8) Tit-for-tat VS stochastique expert:
    Tit-for-tat a remporté le vote 5 fois.
    Stochastique expert a remporté le vote 19 fois.
    Il y avait 6 fois où les deux stratégies ont eu le même score.

9) Fictitious Play VS aléatoire:
    Fictitious Play a remporté le vote 21 fois.
    Stochastique expert a remporté le vote 3 fois.
    Il y avait 6 fois où les deux stratégies ont eu le même score.

10) Fictitious Play VS tétu:
    Fictitious Play a remporté le vote 11 fois.
    Tétu expert a remporté le vote 14 fois.
    Il y avait 5 fois où les deux stratégies ont eu le même score.


En observant ces résultats, on peut déduire que:

    - La stratégie tétu uniforme est meilleur que tétu aléatoire et donne de bons résultats contre les autres stratégies vu qu'elle distribue les militants d'une façon uniforme sur l'ensemble des élécteurs.

    - La stratégie better response donne de bons résultats contre les stratégies stationnaire et contre stochastique expert (car elle choisit une des stratégies stationnaires + better_response aléatirement) vu qu'elle prend l'historique de l'adversaire en compte.

    -La stratégie stochastique expert bat Fictitious play grace au choix aléatoire du prochain coup (l'historique ne donne pas d'information sur les prochains coups de stochastique expert (imprévisible)). Fictitious play n'est plus performante quand l'aléatoire intervient.


    
