import random
import numpy as np
from math import *
import itertools

STRATEGIES = ["affect_uniform", "focus", "better_response", "aleatoire", "titfortat", "best_response"]
nb_obj, nb_militants = 5, 7

# Génère aléatoirement une stratégie pour un parti donné


def init_alea_parti(nb_obj, nb_militants_p):
    obj_militants = [0 for k in range(nb_militants_p)]
    strategy = [0 for k in range(nb_obj)]
    for i in range(nb_militants_p):
        # Allouer aléatoirement un electeur à chaque militant
        obj = np.random.randint(0, nb_obj)
        obj_militants.append(obj)
        strategy[obj] += 1
    return strategy

# Génère aléatoirement de manière uniforme une stratégie pour un parti donné


def init_uniform(nb_obj, nb_militants):
    affec_list = []
    q, r = nb_militants//nb_obj, nb_militants % nb_obj
    for i in range(nb_obj):
        affec_list.append(q)
    for i in range(r):
        affec_list[i] += 1
    return affec_list

# Retourne le score journalier des deux partis


def calcul_score_jour(strategy1, strategy2):
    score1, score2 = 0, 0
    for el1, el2 in zip(strategy1, strategy2):
        if el1 > el2:
            score1 += 1
        elif el1 < el2:
            score2 += 1
    return score1, score2

# Transforme une stratègie d'un parti donné en affectation des militants


def str_to_obj(strategy, nb_militants_p):
    obj_milit = [0 for k in range(nb_militants_p)]
    k = 0
    for i in range(len(strategy)):
        for j in range(strategy[i]):
            obj_milit[k] = i
            k += 1
    return obj_milit

# Retourn toutes les combinaisons possibles qui somme à 7


def combinations():
    comb = []
    cpt = 0
    comb_ = list(itertools.product([0, 1, 2, 3, 4], repeat=5))
    for v in comb_:
        if sum(v) <= 7:
            comb.append(v)
    return comb

# Retourne aléatoirement une stratégie parmi celles implémentées


def stochastique_expert():
    return random.choice(STRATEGIES)

# Retourne le prochaine coup(stratégie) pour un parti


def prochainCoup(mesCoups, adversCoups, nom):
    # selon la liste de mes coups et des coups de l'autre je choisis un coup
    nb_obj, nb_militants = 5, 7
    # Mettre à jour la matrice de probabilités
    # Retourner la strategie selon le nom
    if nom == 'aleatoire':
        return init_alea_parti(nb_obj, nb_militants)

    if nom == 'tetu':
        if len(mesCoups) == 0:
            return init_alea_parti(nb_obj, nb_militants)
        else:
            return mesCoups[-1]

    if nom == 'affect_uniform':
        return init_uniform(nb_obj, nb_militants)

    if nom == 'titfortat':
        if adversCoups == []:
            return init_alea_parti(nb_obj, nb_militants)
        else:
            return adversCoups[-1]

    if nom == 'better_response':
        if adversCoups == []:
            return init_alea_parti(nb_obj, nb_militants)
        else:
            adv_str = adversCoups[-1]
            idx_list = np.argsort(adv_str)[::-1]
            new_strategy = [0 for k in range(nb_obj)]
            for i in range(nb_obj):
                if i < nb_obj//2:
                    new_strategy[idx_list[i]] = 0
                else:
                    new_strategy[idx_list[i]] = adv_str[idx_list[i]]+1
            new_strategy[idx_list[i]] += (nb_militants - sum(new_strategy))
            return new_strategy

    if nom == 'best_response':
        if adversCoups == []:
            return init_alea_parti(nb_obj, nb_militants)
        else:
            combs = combinations()
            sc1, sc2 = 0, 0
            best_score = 0
            best_strategy = []
            for comb in combs:
                sc1, sc2 = calcul_score_jour(comb, adversCoups[-1])
                if sc1 > best_score:
                    best_score = sc1
                    best_strategy = comb
            return best_strategy

    if nom == 'focus':
        strategy = []
        secteurs = ceil(nb_obj/2)
        aff, res = nb_militants//secteurs, nb_militants % secteurs
        for i in range(secteurs-1):
            strategy.append(aff)
        strategy.append(aff+res)
        for i in range(nb_obj-secteurs):
            strategy.append(0)
        return strategy
    else:
        return []
