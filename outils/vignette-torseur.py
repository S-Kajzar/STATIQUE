#!/usr/bin/env python3
"""Dessine la vignette de la carte « Déplacer un torseur » (480 × 270) : src/images/carte-deplacer-torseur.jpg (Pillow)."""
import math
import pathlib
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "images" / "carte-deplacer-torseur.jpg"
K = 3                                     # suréchantillonnage, réduit à la fin
W, H = 480 * K, 270 * K
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 22 * K) if pathlib.Path(
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf").exists() else ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 22 * K)
fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20 * K)


def P(x, y): return (x * K, y * K)


def fleche(a, b, coul, w, tete=14):
    d.line([P(*a), P(*b)], fill=coul, width=w * K)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = [b, (b[0] - tete * math.cos(ang - 0.4), b[1] - tete * math.sin(ang - 0.4)),
           (b[0] - tete * math.cos(ang + 0.4), b[1] - tete * math.sin(ang + 0.4))]
    d.polygon([P(*p) for p in pts], fill=coul)


def tirets(a, b, coul, w, l=9, e=6):
    n = math.dist(a, b); ux, uy = (b[0] - a[0]) / n, (b[1] - a[1]) / n; s = 0
    while s < n - 14:
        t = min(s + l, n - 14)
        d.line([P(a[0] + ux * s, a[1] + uy * s), P(a[0] + ux * t, a[1] + uy * t)], fill=coul, width=w * K)
        s += l + e
    fleche((a[0] + ux * (n - 16), a[1] + uy * (n - 16)), b, coul, w)


# axes
fleche((40, 235), (450, 235), "#9AA2A8", 1, 10); fleche((40, 235), (40, 20), "#9AA2A8", 1, 10)
d.text(P(452, 238), "x", font=f, fill="#46525C"); d.text(P(22, 14), "y", font=f, fill="#46525C")
A, B = (300, 95), (110, 190)
tirets(B, A, "#7B3FA0", 2)                                    # vecteur BA
fleche(A, (400, 40), "#C62828", 4, 18)                         # résultante en A
d.text(P(405, 22), "R", font=f, fill="#C62828"); d.line([P(406, 22), P(420, 22)], fill="#C62828", width=2 * K)
# moment en B (arc, sens trigonométrique)
r = 30
d.arc([P(B[0] - r, B[1] - r), P(B[0] + r, B[1] + r)], start=30, end=290, fill="#1B7A43", width=3 * K)
a = math.radians(30); e = (B[0] + r * math.cos(a), B[1] + r * math.sin(a))      # bout de l'arc (haut d'écran = angle 290)
a2 = math.radians(290); e2 = (B[0] + r * math.cos(a2), B[1] + r * math.sin(a2))
fleche((e2[0] - 8, e2[1] - 3), (e2[0] + 1, e2[1] - 1), "#1B7A43", 3, 12)
fs = fb.font_variant(size=13 * K)


def indice(x, y, base, ind, font, coul):
    """Écrit « base » puis l'indice ; renvoie l'abscisse de fin."""
    d.text(P(x, y), base, font=font, fill=coul)
    x += d.textlength(base, font=font) / K
    d.text(P(x, y + 12), ind, font=fs, fill=coul)
    return x + d.textlength(ind, font=fs) / K


indice(B[0] - 80, B[1] - 12, "M", "B", f, "#1B7A43")
for p, n, dx, dy in ((A, "A", -10, -34), (B, "B", -6, 12)):
    d.ellipse([P(p[0] - 6, p[1] - 6), P(p[0] + 6, p[1] + 6)], fill="#1C2530")
    d.text(P(p[0] + dx, p[1] + dy), n, font=fb, fill="#1C2530")
d.text(P(170, 108), "BA", font=f, fill="#7B3FA0"); d.line([P(171, 108), P(202, 108)], fill="#7B3FA0", width=2 * K)
x = indice(235, 196, "M", "B", f, "#1C2530")
x = indice(x + 4, 196, " = M", "A", f, "#1C2530")
d.text(P(x + 4, 196), "+ BA ∧ R", font=f, fill="#1C2530")
im.resize((480, 270), Image.LANCZOS).save(OUT, quality=88)
print(OUT)
