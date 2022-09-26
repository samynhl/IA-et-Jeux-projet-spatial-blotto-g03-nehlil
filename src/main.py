# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random
from stat import IO_REPARSE_TAG_MOUNT_POINT
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game, check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

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
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print("Goal states:", goalStates)
    print("Number of goals:", len(goalStates))

    # on localise tous les murs
    # sur le layer obstacle
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    print("Wall states:", wallStates)

    def legal_position(row, col):
        # une position legale est dans la carte et pas sur un mur
        return ((row, col) not in wallStates) and row >= 0 and row < nbLignes and col >= 0 and col < nbCols

    # -------------------------------
    # Attributaion aleatoire des fioles
    # -------------------------------

    objectifs = goalStates
    # random.shuffle(objectifs)
    # print("Objectif joueur 0", objectifs[0])
    # print("Objectif joueur 1", objectifs[1])
    obj_milit = {}
    # Clé : electeur , Valeur : militants de parti affecté
    elec_dic = {k: [] for k in range(len(objectifs))}
    militants_list = initStates.copy()
    nb_militants = len(militants_list)
    for i in range(nb_militants):
        # Allouer aléatoirement un electeur à chaque militant
        obj = np.random.randint(0, len(objectifs))
        # list_elec.append((i,a))
        elec_dic[obj].append(i)
        obj_milit[i] = obj

    # -------------------------------
    # Carte demo
    # 2 joueurs
    # Joueur 0: A*
    # Joueur 1: random walk
    # -------------------------------

    # -------------------------------
    # calcul A* pour le joueur 0
    # -------------------------------

    # par defaut la matrice comprend des True
    g = np.ones((nbLignes, nbCols), dtype=bool)
    for w in wallStates:            # putting False for walls
        g[w] = False
    for j in range(nb_militants):
        obj = obj_milit[j]
        p = ProblemeGrid2D(initStates[j], objectifs[obj], g, 'manhattan')
        path = probleme.astar(p)
        print("Chemin trouvé:", path)

        # -------------------------------
        # Boucle principale de déplacements
        # -------------------------------

        posPlayers = initStates

        for i in range(iterations):

            # on fait bouger chaque joueur séquentiellement

            # Joueur j: suit son chemin trouve avec A*

            row, col = path[i]
            posPlayers[j] = (row, col)
            players[j].set_rowcol(row, col)
            print("pos :", row, col)
            if (row, col) == objectifs[obj]:
                print("le joueur {} a atteint son but!".format(j))
                break
            """
            # Joueur 1: fait du random walk
            
            row,col = posPlayers[1]

            while True: # tant que pas legal on retire une position
                x_inc,y_inc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
                next_row = row+x_inc
                next_col = col+y_inc
                if legal_position(next_row,next_col):
                    break
            players[1].set_rowcol(next_row,next_col)
            print ("pos 1:", next_row,next_col)
        
            col=next_col
            row=next_row
            posPlayers[1]=(row,col)
                
            if (row,col) == objectifs[1]:
                print("le joueur 1 a atteint son but!")
                break
                
                
            """
            # on passe a l'iteration suivante du jeu
            game.mainiteration()

    pygame.quit()

    # Calculer le score de chaque parti
    score_parti1, score_parti2 = 0, 0
    for (militants) in elec_dic.values():
        a, b = 0, 0
        for militant in militants:
            if militant < (nb_militants//2):
                a += 1
            else:
                b += 1
        if a > b:
            score_parti1 += 1
        else:
            score_parti2 += 1

    print("-------------------------------------------------------------------------")
    print("le score du parti 1 : {}".format(score_parti1))
    print("le score du parti 2 : {}".format(score_parti2))
    print("Le partie qui a emporté la journée : {}".format('1' if score_parti1>score_parti2 else '2'))
    print("-------------------------------------------------------------------------")
    # -------------------------------


if __name__ == '__main__':
    main()
