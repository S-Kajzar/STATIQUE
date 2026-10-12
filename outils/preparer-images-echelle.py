#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prépare les figures de l'exercice 3.2 (échelle de pompier) tirées du manuel, et dessine son document réponse.

    python3 outils/preparer-images-echelle.py   # seulement si src/images/originaux/n3-ep-* ou src/echelle_dr.py change

Entrées : recadrages des pages du manuel (src/images/originaux/n3-ep-*.jpg).
Sorties : figures blanchies et quantifiées (src/images/n3-ep-*.png) et DR à l'échelle (src/images/n3-echelle-dr.png),
dessiné d'après les cotes de src/echelle_dr.py (Pillow).
"""
import math
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import echelle_dr as E  # noqa: E402

ORIG = ROOT / "src" / "images" / "originaux"
OUT = ROOT / "src" / "images"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_I = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def blanchir(im):
    """Ramène le papier gris-bleu du scan au blanc : niveaux par canal entre le noir et la teinte du papier."""
    im = im.convert("RGB")
    bandes = []
    for b in im.split():
        h = b.histogram()
        tot, acc, papier = sum(h), 0, 255
        for v in range(256):
            acc += h[v]
            if acc >= 0.80 * tot:
                papier = v
                break
        acc, noir = 0, 0
        for v in range(256):
            acc += h[v]
            if acc >= 0.01 * tot:
                noir = v
                break
        papier = max(papier - 6, noir + 40)
        bandes.append(b.point(lambda x, n=noir, p=papier: max(0, min(255, round((x - n) * 255 / (p - n))))))
    return Image.merge("RGB", bandes)


def figure(nom, largeur):
    im = blanchir(Image.open(ORIG / f"{nom}.jpg"))
    if im.width > largeur:
        im = im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)
    q = im.quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE)
    q.save(OUT / f"{nom}.png", optimize=True)
    print(f"{nom}.png : {q.width} × {q.height}, {(OUT / f'{nom}.png').stat().st_size / 1024:.0f} Kio")


def dr():
    """Document réponse : échelle (3) isolée à l'échelle 1 m ↔ 1 cm, zone du dynamique à droite."""
    im = Image.new("RGB", (E.W, E.H), "white")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 26)
    fs = ImageFont.truetype(FONT, 20)
    fi = ImageFont.truetype(FONT_I, 20)
    P = E.px
    d.rectangle([0, 0, E.W - 1, E.H - 1], outline=(214, 219, 216), width=2)
    # échelle : bande inclinée à 30°, posée sur les chapes A et B
    a30 = math.radians(30)
    t, n = (math.cos(a30), math.sin(a30)), (-math.sin(a30), math.cos(a30))

    def pt(s, h):        # abscisse s le long de l'échelle, hauteur h au-dessus de la droite (AB)
        return P((s * t[0] + h * n[0], s * t[1] + h * n[1]))
    s0, s1, h0, h1 = -1.5, 7.45, 0.3, 1.1
    d.polygon([pt(s0, h0), pt(s1, h0), pt(s1, h1), pt(s0, h1)], fill=(250, 236, 196), outline=(184, 137, 43))
    for k in range(13):                                   # treillis
        sa, sb = s0 + 0.2 + k * 0.75, s0 + 0.2 + (k + 0.5) * 0.75
        if sb > s1 - 0.1:
            break
        d.line([pt(sa, h0), pt(sb, h1)], fill=(214, 172, 80), width=4)
        if sb + 0.375 < s1:
            d.line([pt(sb, h1), pt(sb + 0.375, h0)], fill=(214, 172, 80), width=4)
    d.line([pt(s0, h0 + 0.12), pt(s1, h0 + 0.12)], fill=(184, 137, 43), width=3)
    d.line([pt(s0, h1 - 0.12), pt(s1, h1 - 0.12)], fill=(184, 137, 43), width=3)
    d.line([pt(s0 + 0.1, h0), pt(s0 - 0.25, h0 - 0.3), pt(s0 + 0.15, h0 - 0.42)], fill=(184, 137, 43), width=5)  # crochet
    for s in (0.0, math.hypot(*E.B)):                     # chapes en A et en B
        d.polygon([pt(s - 0.32, h0), pt(s + 0.32, h0), pt(s + 0.18, -0.05), pt(s - 0.18, -0.05)],
                  fill=(240, 214, 150), outline=(184, 137, 43))
    # axes (A, x, y)
    gx = (120, 128, 134)
    ax0, ax1 = P((-1.6, 0)), P((7.85, 0))
    d.line([ax0, ax1], fill=gx, width=2)
    d.polygon([ax1, (ax1[0] - 14, ax1[1] - 6), (ax1[0] - 14, ax1[1] + 6)], fill=gx)
    ay0, ay1 = P((0, -1.0)), P((0, 4.75))
    d.line([ay0, ay1], fill=gx, width=2)
    d.polygon([ay1, (ay1[0] - 6, ay1[1] + 14), (ay1[0] + 6, ay1[1] + 14)], fill=gx)
    d.text((ax1[0] - 4, ax1[1] + 8), "x", font=fi, fill=gx)
    d.text((ay1[0] + 10, ay1[1] - 4), "y", font=fi, fill=gx)
    # poids P3, à titre indicatif (longueur hors échelle des forces)
    g = E.POINTS["G3"]
    rouge = (198, 40, 40)
    d.line([g, (g[0], g[1] + 90)], fill=rouge, width=4)
    d.polygon([(g[0], g[1] + 104), (g[0] - 9, g[1] + 84), (g[0] + 9, g[1] + 84)], fill=rouge)
    d.text((g[0] + 14, g[1] + 40), "P3\n5 000 daN", font=fs, fill=rouge)
    # points
    enc = (28, 37, 48)
    for nom, (dx, dy) in {"A": (-34, 6), "B": (12, -34), "C": (16, -6), "G3": (14, -36)}.items():
        x, y = E.POINTS[nom]
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill="white", outline=enc, width=3)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=enc)
        d.text((x + dx, y + dy), nom, font=f, fill=enc)
    d.text((E.POINTS["C"][0] + 16, E.POINTS["C"][1] + 24), "articulation du vérin\nsur la tourelle", font=fi, fill=(70, 82, 92))
    # titres et séparation
    d.text((28, E.H - 46), "Échelle (3) isolée — 1 cm ↔ 1 m", font=f, fill=enc)
    for y in range(10, E.H - 10, 26):
        d.line([(E.SEP, y), (E.SEP, y + 14)], fill=(150, 158, 164), width=2)
    d.text((E.SEP + 24, 22), "Dynamique des forces", font=f, fill=enc)
    im.quantize(colors=48, method=Image.MEDIANCUT, dither=Image.NONE).save(OUT / "n3-echelle-dr.png", optimize=True)
    print(f"n3-echelle-dr.png : {E.W} × {E.H}, {(OUT / 'n3-echelle-dr.png').stat().st_size / 1024:.0f} Kio")


def main():
    figure("n3-ep-verin-isole", 360)
    figure("n3-ep-graphique", 620)
    figure("n3-ep-verin-coupe", 760)
    dr()


if __name__ == "__main__":
    main()
