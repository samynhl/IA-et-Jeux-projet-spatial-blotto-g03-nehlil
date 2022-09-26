# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random
from stat import IO_REPARSE_TAG_MOUNT_POINT
from matplotlib.pyplot import hist
import numpy as np
import sys
from itertools import chain

import random

import pygame

from pySpriteWorld.gameclass import Game, check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

import util as ut
import fictitious as ft
# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----


# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player, game
    name = _boardname if _boardname is not None else 'blottoMap'
    game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player

def main():
    # for arg in sys.argv:
    iterations = 100  # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print("Iterations: ")
    print(iterations)

    init()

    # Affectation des militants sur les secteurs avec budget
    # Deuxième variante des elections avec budget dans ce fichier

    # -------------------------------
    # Initialisation
    # -------------------------------

    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize

    print("lignes", nbLignes)
    print("colonnes", nbCols)

    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    print("Trouvé ", nbPlayers, " militants")

    # on localise tous les états initiaux (loc du joueur)
    # positions initiales des joueurs
    # Retourne des couples (x,y) : positions des joueurs
    initStates = [o.get_rowcol() for o in players]
    print("Init states:", initStates)
    print("Number of players:", len(initStates))

    # on localise tous les secteurs d'interet (les votants)
    # sur le layer ramassable
    # Retourne des couples (x,y) : positions des votants
    pos_secteurs = {0:[(1,3),(1,4)],1:[(1,3),(8,11)],2:[(1,3),(15,18)],
                3:[(5,9),(1,4)],4:[(5,9),(15,18)],5:[(11,14),(1,4)],
                6:[(11,14),(15,18)],7:[(16,18),(1,6)],8:[(16,18),(8,11)],
                9:[(16,18),(15,18)]}

    
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print("Goal states:", goalStates)
    print("Number of goals:", len(goalStates))
    

    # on localise tous les murs
    # sur le layer obstacle
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]

    def legal_position(row, col):
        # une position legale est dans la carte et pas sur un mur
        return ((row, col) not in wallStates) and row >= 0 and row < nbLignes and col >= 0 and col < nbCols

    # Structures utilisées
    objectifs = goalStates
    nb_militants, nb_obj = len(initStates), len(objectifs)
    score = {1: 0, 2: 0}
    strategy1, strategy2 = [0 for k in range(nb_obj)], [0 for k in range(nb_obj)]
    historique = {1:[], 2:[]}

    # -------------------------------
    # Carte demo
    # Tous les joueurs exécutent A*
    # -------------------------------

    # par defaut la matrice comprend des True
    g = np.ones((nbLignes, nbCols), dtype=bool)
    for w in wallStates:            # putting False for walls
        g[w] = False

    posPlayers = initStates
    # ---------------------------------------------------------------
    # Fonctions de traitement du budget
    # Budget fixe par militant (premiere variante)
    # ---------------------------------------------------------------
    # Re-affectation des electeurs aléatoirement sur les secteurs
    def reaffect():
        affec_alea,l = [],[]
        l = random.sample(range(10), 5)
        for el in l:
            pos = pos_secteurs[el]
            affec_alea.append((random.randint(pos[0][0],pos[0][1]), random.randint(pos[1][0],pos[1][1])))
        s = 0
        for o in game.layers['ramassable']:
            row, col = affec_alea[s]
            s+=1
            o.set_rowcol(row, col)
    # Calcule le cout pour se déplacer d'un point à un autre
    def cout_chemin(posPlayer, posTarget):
        p = ProblemeGrid2D(posPlayer, posTarget, g, 'manhattan')
        path = probleme.astar(p)
        return len(path)
    # Choisit aleatoirement un electeur parmi les choix possible selon le budget du militant
    def pick_from_possible_moves(myPosition, myBudget):
        output = []
        for obj in objectifs:
            if cout_chemin(myPosition, obj)<=myBudget: output.append(obj)
        return random.sample(output,1)[0] if len(output)!=0 else myPosition
    # retourne une strategie aleatoire parmi les choix possibles des militants
    def strategy_with_budget(posPlayers, budget):
        newPos, strategy = [], [0 for k in range(nb_obj)]
        for pos in posPlayers:
            pos_ = pick_from_possible_moves(pos, budget)
            newPos.append(pos_)
            if pos_ in objectifs: strategy[objectifs.index(pos_)]+=1
        return newPos, strategy
    # Choisir l'objectif le plus proche
    # Pas plus de trois militants par secteur
    def choose_nearest_obj(posPlayers):
        new_objectifs, couts = [], []
        strategy = [0 for k in range(nb_obj)]
        for posPlayer in posPlayers:
            pref = [cout_chemin(posPlayer, objectifs[x]) for x in range(nb_obj)]
            sortedPref = np.argsort(pref)
            for pos in sortedPref:
                if strategy[pos]<3:
                    new_objectifs.append(objectifs[pos])
                    strategy[pos]+=1
                    couts.append(pref[pos])
                    break
        return new_objectifs, strategy, couts

    # Nom de stratégies pour chaque parti
    nom_str1, nom_str2 = "aleatoire avec budget v2", "aleatoire avec budget v2"

    NBJOURS = 20
    budget1, budget2  = 0,0
    # Boucle principale des elections sur les jours
    for jour in range(NBJOURS):
        # Initialisation des strategies d'affectation
        newPos1, strategy1, cout1 = choose_nearest_obj(posPlayers[:7])
        newPos2, strategy2, cout2 = choose_nearest_obj(posPlayers[7:])

        obj_milit = newPos1 + newPos2
        budget1 += sum(cout1)
        budget2 += sum(cout2)
        
        # Sauvegarde de stratégies
        historique[1].append(strategy1)
        historique[2].append(strategy2)
        
        for militant in range(nb_militants):
            obj = obj_milit[militant]
            p = ProblemeGrid2D(posPlayers[militant], obj, g, 'manhattan')
            path = probleme.astar(p)
            # Boucle principale de déplacements
            for i in range(iterations):
                # on fait bouger chaque joueur séquentiellement
                row, col = path[i]
                posPlayers[militant] = (row, col)
                players[militant].set_rowcol(row, col)
                if (row, col) == obj:
                    # Si nouvelle position alors la sauvegarder
                    posPlayers[militant] = (row, col)
                    break
                # on passe a l'iteration suivante du jeu
                # Pour affichage, décommentez l'instruction suivante
                # game.mainiteration()
        # pygame.quit()

        # Re-affectation des electeurs aléatoirement sur les secteurs
        reaffect()
        objectifs = [o.get_rowcol() for o in game.layers['ramassable']]
        
        # Calculer le score de chaque parti en ce jour
        score_parti1, score_parti2 = ut.calcul_score_jour(strategy1, strategy2)
        # Sauvegarder le score journalier de chaque parti
        score[1] += score_parti1
        score[2] += score_parti2

        # Affichage de score et des strategies à la fin de la journée
        print("-------------------------------------------------------------------------")
        print("Jour ", jour+1)
        print("Strategie parti 1 ({}): {}".format(nom_str1,strategy1))
        print("Strategie parti 2 ({}): {}".format(nom_str2,strategy2))
        print("---")
        print("le score du parti 1 : {}".format(score_parti1))
        print("le score du parti 2 : {}".format(score_parti2))
        print("Le partie qui a emporté la journée {}: {}".format(jour+1, '1' if score_parti1 > score_parti2 else '2'))
    
    # Affichage du score à la fin des elections
    print("-------------------------------------------------------------------------")
    print("strategie parti 1: {} - stratégie parti 2: {}".format(nom_str1,nom_str2))
    print("le score du parti 1 à la fin des elections: {}".format(score[1]))
    print("le score du parti 2 à la fin des elections: {}".format(score[2]))
    print("---")
    print("le budget du parti 1 à la fin des elections: {}".format(budget1))
    print("le budget du parti 2 à la fin des elections: {}".format(budget2))
    print("---")
    print("Le parti qui a emporté l'election : {}".format('1' if score[1] > score[2] else '2'))

# Main
if __name__ == '__main__':
    main()