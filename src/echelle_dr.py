#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Géométrie du document réponse de l'échelle de pompier (exercice 3.2), partagée par le dessin du DR
(outils/preparer-images-echelle.py) et par l'exercice (src/niveau3.py) : les points du DR et la correction
graphique sont ainsi calculés sur les mêmes cotes que la résolution analytique.

Cotes du livre (repère (A, x, y), en m) : B (2,85 ; 1,65), G3 à 6 m de A en x, droite (BC) à 70° de x.
Le DR est à l'échelle 1 m ↔ 1 cm (80 px du fond par cm) ; la zone de droite reçoit le dynamique.
"""
import math

PX_CM = 80                       # pixels du fond par centimètre du document
W, H = 1340, 1060                # taille du fond (px)
SEP = 800                        # abscisse de la séparation tracé | dynamique
O = (150, 400)                   # position de A sur le fond (px)
ALPHA = math.radians(70)

A = (0.0, 0.0)
B = (2.85, 1.65)
G3 = (6.0, 6.0 * math.tan(math.radians(30)) + 0.7 / math.cos(math.radians(30)))   # milieu de la bande
C = (B[0] + 2.2 * math.cos(ALPHA), B[1] - 2.2 * math.sin(ALPHA))


def px(p):
    """Point en mètres → pixels du fond (y vers le bas)."""
    return (O[0] + PX_CM * p[0], O[1] - PX_CM * p[1])


POINTS = {"A": px(A), "B": px(B), "C": px(C), "G3": px(G3)}
