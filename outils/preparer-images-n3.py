#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prépare les figures du niveau 3 (cours de statique analytique, exercices 3.1 à 3.3).

    python3 outils/preparer-images-n3.py     # à relancer seulement si src/images/originaux/n3-* change (Pillow)

Entrées : figures extraites de la séquence « Statique analytique » (src/images/originaux/n3-*.png).
Sorties : figures quantifiées intégrées aux pages (src/images/n3-*.png), vignettes des cartes de
l'accueil en 480 × 270 (src/images/carte-*.jpg) et fonds blancs des graphes de liaisons à tracer.
"""
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORIG = ROOT / "src" / "images" / "originaux"
OUT = ROOT / "src" / "images"


def ouvrir(nom):
    im = Image.open(ORIG / f"{nom}.png").convert("RGB")
    return im


def figure(im, nom, largeur_max=900, couleurs=128):
    if im.width > largeur_max:
        im = im.resize((largeur_max, round(im.height * largeur_max / im.width)), Image.LANCZOS)
    q = im.quantize(colors=couleurs, method=Image.MEDIANCUT, dither=Image.NONE)
    q.save(OUT / f"{nom}.png", optimize=True)
    print(f"{nom}.png : {q.width} × {q.height}, {(OUT / f'{nom}.png').stat().st_size / 1024:.0f} Kio")


def vignette(im, nom, marge=10):
    """Image entière, centrée sur fond blanc, dans un cadre 480 × 270 (16/9)."""
    W, H = 480, 270
    k = min((W - 2 * marge) / im.width, (H - 2 * marge) / im.height)
    r = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    fond = Image.new("RGB", (W, H), "white")
    fond.paste(r, ((W - r.width) // 2, (H - r.height) // 2))
    fond.save(OUT / f"{nom}.jpg", quality=86, optimize=True)
    print(f"{nom}.jpg : {(OUT / f'{nom}.jpg').stat().st_size / 1024:.0f} Kio")


def fond_blanc(nom, w, h):
    im = Image.new("RGB", (w, h), "white")
    ImageDraw.Draw(im).rectangle([0, 0, w - 1, h - 1], outline=(214, 219, 216), width=1)
    im.quantize(colors=2).save(OUT / f"{nom}.png", optimize=True)
    print(f"{nom}.png : {w} × {h} (fond de tracé)")


def main():
    deux = ouvrir("n3-deux-forces")
    figure(deux, "n3-deux-forces", 380)
    plan = ouvrir("n3-coffre-plan")
    figure(plan, "n3-coffre-plan", 510)
    photo = ouvrir("n3-coffre-photo")
    figure(photo, "n3-coffre-photo", 520)
    cine = ouvrir("n3-coffre-cine")
    figure(cine, "n3-coffre-cine", 288, 32)
    ech = ouvrir("n3-echelle")
    figure(ech, "n3-echelle", 584)
    iso = ouvrir("n3-echelle-iso")
    figure(iso, "n3-echelle-iso", 470)
    velo = ouvrir("n3-velo")
    figure(velo, "n3-velo", 1332)
    # vélo complet seul (partie gauche) et cadre arrière (2) isolé (partie droite)
    figure(velo.crop((0, 0, 905, 431)), "n3-velo-cadre", 905)
    figure(velo.crop((930, 60, 1332, 431)), "n3-velo-arriere", 402)
    figure(velo.crop((680, 0, 905, 150)), "n3-velo-amortisseur", 225)

    vignette(deux, "carte-cours-statique-analytique")
    vignette(plan, "carte-coffre-fort")
    vignette(ech, "carte-echelle-pompier")
    vignette(velo.crop((0, 0, 905, 431)), "carte-cadre-velo")

    fond_blanc("n3-graphe-coffre", 760, 400)
    fond_blanc("n3-graphe-velo", 760, 400)


if __name__ == "__main__":
    main()
