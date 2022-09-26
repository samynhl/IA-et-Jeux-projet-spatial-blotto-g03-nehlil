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
    # print("Wall states:", wallStates)

    def legal_position(row, col):
        # une position legale est dans la carte et pas sur un mur
        return ((row, col) not in wallStates) and row >= 0 and row < nbLignes and col >= 0 and col < nbCols

    # Structures utilisées
    objectifs = goalStates
    nb_militants, nb_obj = len(initStates), len(objectifs)
    score = {1: 0, 2: 0}
    strategy1 = [0 for k in range(nb_obj)] # liste pour sauvegarder la strategie précédente du parti 1
    strategy2 = [0 for k in range(nb_obj)] # liste pour sauvegarder la strategie précédente du parti 2
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

    # STRATEGIES = ["aleatoire","tetu","tetu_uniform","focus","better_response","best_response","titfortat"]
    # Nom de stratégies pour chaque parti (cas de strategies fixes durant toute l'élection)
    nom_str1, nom_str2 = "best_response", "affect_uniform"
    
    NBJOURS = 20
    # Boucle principale des elections sur les jours
    for jour in range(NBJOURS):
        # Initialisation des strateegies d'affectation
        strategy1 = ut.prochainCoup(historique[1],historique[2],nom_str1)
        strategy2 = ut.prochainCoup(historique[2],historique[1],nom_str2)

        obj_milit = ut.str_to_obj(strategy1, nb_militants//2) +  ut.str_to_obj(strategy2, nb_militants//2)
        
        # Sauvegarde de stratégies
        historique[1].append(strategy1)
        historique[2].append(strategy2)
        # Mettre à jour la matrice des probabilités
        ft.updateMatProba(historique[2][-1], jour+1)
        
        for militant in range(nb_militants):
            obj = obj_milit[militant]
            p = ProblemeGrid2D(posPlayers[militant], objectifs[obj], g, 'manhattan')
            path = probleme.astar(p)
            # -------------------------------
            # Boucle principale de déplacements
            # -------------------------------
            for i in range(iterations):
                # on fait bouger chaque joueur séquentiellement

                # Joueur militant: suit son chemin trouve avec A*

                row, col = path[i]
                posPlayers[militant] = (row, col)
                players[militant].set_rowcol(row, col)
                if (row, col) == objectifs[obj]:
                    # Si nouvelle position alors la sauvegarder
                    posPlayers[militant] = (row, col)
                    break
                # on passe a l'iteration suivante du jeu
                #game.mainiteration()

        # pygame.quit()

        # Calculer le score de chaque parti en ce jour
        score_parti1, score_parti2 = ut.calcul_score_jour(strategy1, strategy2)
        # Sauvegarder le score journalier de chaque parti
        score[1] += score_parti1
        score[2] += score_parti2
        # Affichage de score et des strategies en fin de journée
        print("-------------------------------------------------------------------------")
        print("jour ", jour+1)
        print("Strategie parti 1 ({}): {}".format(nom_str1,strategy1))
        print("Strategie parti 2 ({}): {}".format(nom_str2,strategy2))
        print("---")
        print("le score du parti 1 : {}".format(score_parti1))
        print("le score du parti 2 : {}".format(score_parti2))
        print("Le partie qui a emporté la journée {}: {}".format(jour+1, '1' if score_parti1 > score_parti2 else '2'))

    # Affichage du score après la fin des elections
    print("-------------------------------------------------------------------------")
    print("strategie parti 1: {} - stratégie parti 2: {}".format(nom_str1,nom_str2))
    print("le score du parti 1 à la fin des elections: {}".format(score[1]))
    print("le score du parti 2 à la fin des elections: {}".format(score[2]))
    print("Le parti qui a emporté l'election : {}".format('1' if score[1] > score[2] else '2'))

# Main
if __name__ == '__main__':
    main()