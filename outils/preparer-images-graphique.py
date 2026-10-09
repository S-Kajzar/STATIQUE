#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prépare les figures de la statique graphique (cours 1.1, exercices 1.2 à 1.5).

    python3 outils/preparer-images-graphique.py   # seulement si src/images/originaux/g-* change (Pillow)

Entrées : pages et figures des documents d'origine (src/images/originaux/g-*.png), déjà redressées.
Sorties (src/images/) :
  - g-*-dr.png : fonds des documents réponses, débarrassés des tableaux, des conclusions et des barres
    d'échelle d'origine (remplacés par des questions et par les échelles dessinées par le moteur de tracé) ;
  - g-*.png : figures des énoncés et des dossiers de présentation ;
  - carte-*.jpg : vignettes 480 × 270 de l'accueil.
Les coordonnées des points utilisées par src/graphique.py sont exprimées dans les fonds g-*-dr.png produits ici.
"""
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORIG = ROOT / "src" / "images" / "originaux"
OUT = ROOT / "src" / "images"


def ouvrir(nom):
    return Image.open(ORIG / f"{nom}.png").convert("RGB")


def blanchir(im, zones):
    d = ImageDraw.Draw(im)
    for z in zones:
        d.rectangle(z, fill="white")
    return im


def sortie(im, nom, couleurs=64, largeur_max=None, gris=False):
    if largeur_max and im.width > largeur_max:
        im = im.resize((largeur_max, round(im.height * largeur_max / im.width)), Image.LANCZOS)
    if gris:
        im = im.convert("L").quantize(colors=couleurs, dither=Image.NONE)
    else:
        im = im.quantize(colors=couleurs, method=Image.MEDIANCUT, dither=Image.NONE)
    im.save(OUT / f"{nom}.png", optimize=True)
    print(f"{nom}.png : {im.width} × {im.height}, {(OUT / f'{nom}.png').stat().st_size / 1024:.0f} Kio")


def vignette(im, nom, marge=10):
    W, H = 480, 270
    k = min((W - 2 * marge) / im.width, (H - 2 * marge) / im.height)
    r = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    fond = Image.new("RGB", (W, H), "white")
    fond.paste(r, ((W - r.width) // 2, (H - r.height) // 2))
    fond.save(OUT / f"{nom}.jpg", quality=86, optimize=True)
    print(f"{nom}.jpg : {(OUT / f'{nom}.jpg').stat().st_size / 1024:.0f} Kio")


def main():
    # ---------- cours : bride, levier isolé, pièce 6
    c3 = ouvrir("g-cours-003")
    sortie(c3.crop((0, 70, 500, 450)), "g-bride", 64)
    c4 = ouvrir("g-cours-004")
    levier = c4.crop((590, 120, 967, 559))  # levier isolé et force F (origine du fond : (590 ; 120) de la figure)
    sortie(levier, "g-levier", 48)
    c6 = ouvrir("g-cours-006")
    sortie(c6.crop((690, 15, 900, 135)), "g-piece6", 32)
    vignette(c3.crop((0, 70, 950, 450)), "carte-cours-statique-graphique")

    # ---------- panneau solaire : figure ×2 et zone libre à droite pour le dynamique
    pan = ouvrir("g-panneau")
    sortie(pan, "g-panneau", 48)
    p2 = pan.resize((pan.width * 2, pan.height * 2), Image.LANCZOS)
    dr = Image.new("RGB", (p2.width + 700, p2.height), "white")
    dr.paste(p2, (0, 0))
    ImageDraw.Draw(dr).line([(p2.width + 20, 30), (p2.width + 20, p2.height - 30)], fill=(200, 205, 202), width=2)
    sortie(dr, "g-panneau-dr", 48)
    vignette(pan, "carte-panneau-solaire")

    # ---------- pince : présentation, configurations, deux documents réponses
    p1 = ouvrir("g-pince-p1")
    sortie(p1.crop((580, 50, 1193, 500)), "g-pince-photo", 96, 520)
    sortie(p1.crop((0, 440, 410, 945)), "g-pince-cotee", 64)
    sortie(p1.crop((732, 555, 1193, 975)), "g-pince-schema", 32)
    sortie(p1.crop((30, 1080, 700, 1550)), "g-pince-configs", 32)
    vignette(p1.crop((580, 50, 1193, 500)), "carte-pince-kobelco")
    c1p = ouvrir("g-pince-c1")
    dr1 = c1p.crop((30, 875, 1199, 1545))   # origine du fond : (30 ; 875) de la page
    blanchir(dr1, [(0, 465, 860, 670), (1115, 90, 1169, 300)])
    sortie(dr1, "g-pince-dr1", 16, gris=True)
    c2p = ouvrir("g-pince-c2")
    dr2 = c2p.crop((30, 560, 1199, 1225))   # origine du fond : (30 ; 560) de la page
    blanchir(dr2, [(0, 525, 860, 665), (1115, 250, 1169, 450)])
    sortie(dr2, "g-pince-dr2", 16, gris=True)

    # ---------- cric : présentation et document réponse ×2
    cp = ouvrir("g-cric-p1")
    sortie(cp.crop((0, 280, 660, 590)), "g-cric-meca", 64)
    sortie(cp.crop((925, 40, 1207, 290)), "g-cric-photo", 64)
    vignette(cp.crop((925, 40, 1207, 290)), "carte-cric-hydraulique")
    cd = ouvrir("g-cric-dr")
    cd = cd.resize((cd.width * 2, cd.height * 2), Image.LANCZOS)
    blanchir(cd, [(1570, 20, 2210, 390),        # tableau d'isolement du bras
                  (360, 1120, 900, 1340), (1880, 1100, 2425, 1320),  # conclusions
                  (480, 300, 612, 382), (1680, 1040, 1822, 1128)])   # barres d'échelle d'origine
    sortie(cd, "g-cric-dr", 16, gris=True)

    # ---------- suspension de VTT : présentation et document réponse (page 2, 200 dpi, redressée)
    vp = ouvrir("g-vtt-photo")
    sortie(vp, "g-vtt-photo", 96, 600)
    vignette(vp, "carte-suspension-vtt")
    v1 = ouvrir("g-vtt-p1")
    sortie(v1.crop((480, 470, 1600, 1100)), "g-vtt-cadre", 64, 900)
    vd = ouvrir("g-vtt-dr")
    blanchir(vd, [(70, 115, 650, 445), (1055, 55, 1640, 405),        # tableaux d'isolement
                  (480, 1385, 960, 1590), (1715, 1395, 2200, 1600),   # conclusions
                  (85, 1240, 160, 1610),                              # adresse du site d'origine
                  (590, 600, 710, 680), (1250, 690, 1370, 760)])      # barres d'échelle d'origine
    sortie(vd, "g-vtt-dr", 16, gris=True)


if __name__ == "__main__":
    main()
