#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère l'accueil (index.html) de « Statique » et les pages d'exercices (copiées depuis src/exercices/).

Gabarit repris du dépôt « Chaîne fonctionnelle » : même charte (src/gabarit-exercice-interactif.html, dont seul le
bloc <style> est utilisé ici), même accueil en cartes illustrées (rubriques Les cours, Le formulaire, Les exercices,
Études de cas), mêmes pastilles Niveau 1 / Niveau 2. Une carte sans contenu est « en cours d'édition » : légèrement
transparente, sans lien.

    python3 src/generer.py     # écrit index.html et les pages d'exercices

Ajouter un exercice : déposer sa page dans src/exercices/, sa vignette (480 × 270) dans src/images/, puis décrire
la carte dans EXERCICES (avec "page" : nom du fichier publié). Remplacer une carte « en cours d'édition » : même chose,
en retirant sa ligne de ENCOURS.
"""
import base64
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
GABARIT = ROOT / "src" / "gabarit-exercice-interactif.html"
IMAGES = ROOT / "src" / "images"
SOURCES = ROOT / "src" / "exercices"
TITRE = "Statique"
SOUS_TITRE = ("Statique du solide : modéliser les actions mécaniques, appliquer le principe fondamental de la statique, isoler un solide et déterminer les actions inconnues. Des cours, des exercices et des études de cas interactifs de deux niveaux, à faire en mode entraînement ou en mode examen.")

# Cartes avec contenu : la page est copiée de src/exercices/<source> vers <page> (lien de retour ajouté).
EXERCICES = [
    {"rubrique": "exercices", "tag": "Exercice 2.1", "level": "Niveau 2", "title": "Potence à tirant sur mur",
     "mots": ["Isolement", "Deux forces", "Trois forces", "Moments", "Vérification"], "vign": "carte-potence.jpg",
     "alt": "Schéma cinématique de la potence : colonne 1, tirant 2, flèche 3", "page": "potence.html",
     "source": "potence-source.html",
     "ancre": '<p class="home-note small">Le mode se choisit une seule fois : pour en changer, recharge la page. Rien n\'est enregistré sur l\'ordinateur.</p>',
     "avant": False,
     "css": "body:not(.no-mode) .home-back{display:none}"},
]
# Cartes « en cours d'édition » : (rubrique, étiquette, niveau, titre, mots-clés)
ENCOURS = [
    ("cours", "Cours 1", "Niveau 1", "Principe fondamental de la statique", ["Équilibre", "Résultante", "Moment"]),
    ("cours", "Cours 2", "Niveau 2", "Isolement et théorèmes généraux", ["Isolement", "Deux forces", "Trois forces"]),
    ("formulaire", "Formulaire", None, "Formulaire de statique", ["Formules", "Unités", "Rappels"]),
    ("exercices", "Exercice 1.1", "Niveau 1", "Équilibre d'un solide", ["Bilan des actions", "Équations", "Résolution"]),
    ("etudes", "Étude 1", None, "Étude de cas", ["Système réel", "Isolement", "Dimensionnement"]),
]
RUBRIQUES = [("cours", "Les cours"), ("formulaire", "Le formulaire"), ("exercices", "Les exercices"),
             ("etudes", "Études de cas")]

HOUSE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.3" '
         'stroke-linejoin="round" stroke-linecap="round"><path d="M3 11.5 12 4l9 7.5"/>'
         '<path d="M5.5 9.8V20h4.5v-5.5h4V20h4.5V9.8"/></svg>')


def esc(s):
    return html.escape(s, quote=True)


def pastille(level):
    return f' <span class="pastille n{level.split()[-1]}">{level}</span>' if level else ""


def vignette(name):
    data = (IMAGES / name).read_bytes()
    mime = "jpeg" if name.endswith(".jpg") else "png"
    return f"data:image/{mime};base64," + base64.b64encode(data).decode()


def carte(tag, level, title, mots, href=None, bouton="Ouvrir l'exercice", vign=None, alt=""):
    """Carte de l'accueil : vignette, étiquette, titre, mots-clés, bouton (ou « En cours d'édition »)."""
    if vign:
        img = f'<img class="cv-img" src="{vignette(vign)}" alt="{esc(alt)}" width="480" height="270" loading="lazy">'
    else:
        img = '<div class="cv-img cv-vide" aria-hidden="true"></div>'
    mots_html = '<ul class="cv-mots">' + "".join(f"<li>{m}</li>" for m in mots) + "</ul>"
    if href:
        fin, cls = f'<a class="btn" href="{href}">{bouton}</a>', ""
    else:
        fin, cls = '<p class="small ex-meta etat">En cours d\'édition</p>', "en-edition"
    return (f'<article class="mode-card carte-v {cls}">{img}<div class="mc-head"><span class="mc-tag">{tag}'
            f'{pastille(level)}</span><h3>{title}</h3></div>{mots_html}{fin}</article>')


def render_hub():
    grilles = {k: [] for k, _ in RUBRIQUES}  # (étiquette, carte) : triées par étiquette
    for e in EXERCICES:
        grilles[e["rubrique"]].append((e["tag"], carte(e["tag"], e["level"], e["title"], e["mots"], e["page"],
                                            e.get("bouton", "Ouvrir l'exercice"), e["vign"], e["alt"])))
    for rub, tag, level, title, mots in ENCOURS:
        grilles[rub].append((tag, carte(tag, level, title, mots)))
    sections = "".join(f'<h2 class="home-choose">{nom}</h2><div class="ex-grid {k}-grid">{"".join(c for _, c in sorted(grilles[k], key=lambda t: t[0]))}</div>'
                       for k, nom in RUBRIQUES if grilles[k])
    return (f'<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head">'
            f'<h1 id="home-title">{TITRE}</h1><p class="home-sub">{SOUS_TITRE}</p></header></div></div>'
            f'{sections}<p class="home-note small">Pastilles : {pastille("Niveau 1").strip()} premier niveau, '
            f'{pastille("Niveau 2").strip()} niveau approfondi. Les cartes légèrement transparentes sont en cours '
            "d'édition. Rien n'est enregistré sur l'ordinateur.</p>")


HUB_CSS = r"""<style>
/* ---------- accueil en cartes (repris du dépôt « Chaîne fonctionnelle ») ---------- */
a.btn{display:inline-flex; align-items:center; gap:8px; text-decoration:none}
a.btn svg,.c-top svg{width:18px; height:18px; flex:0 0 auto}
.tab-home{display:flex; align-items:center; justify-content:center; padding:8px 0 8px 4px; background:var(--encre); color:var(--jaune); text-decoration:none}
.tab-home svg{width:22px; height:22px; display:block}
.tab-home:hover{background:#2E3B47}
.c-top{margin:0 0 12px}
.c-top a{display:inline-flex; align-items:center; gap:6px; font:600 .95rem var(--f-titre); color:var(--encre); text-decoration:none; border:1.5px solid var(--encre); background:var(--papier); padding:5px 12px 5px 10px}
.c-top a:hover{background:var(--jaune-pale)}
#home{padding:20px 20px 32px}
.home-top{display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:14px; align-items:stretch; margin:0 0 14px}
.home-top-single{grid-template-columns:1fr}
.home-top-l{display:flex; flex-direction:column; gap:10px; min-width:0}
.home-top .home-head{padding:14px 20px; flex:1}
.home-top .home-head h1{margin:6px 0 6px; font-size:clamp(1.4rem,2.4vw,1.85rem)}
.home-top .home-sub{font-size:.95rem}
.home-top .home-hero{margin:0; padding:8px; display:flex; flex-direction:column; justify-content:center; min-width:0}
.home-top .home-hero img{width:auto!important; max-width:100%; max-height:160px; margin:0 auto}
body.hub .home-top .home-hero img{max-height:210px}
.home-top .home-hero figcaption{font-size:.78rem; line-height:1.3; margin-top:4px}
.home-top .home-facts{grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin:0}
.home-top .home-facts div{padding:6px 10px}
.home-top .home-facts b{font-size:1.02rem}
.home-top .home-facts span{font-size:.76rem; line-height:1.3; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
@media (max-width:980px){ .home-top .home-facts{grid-template-columns:repeat(2,minmax(0,1fr))} }
@media (max-width:820px){ .home-top{grid-template-columns:1fr} }
#home .home-choose{margin:18px 0 8px; font-size:1.25rem}
#home .mode-card{padding:12px 18px 14px}
#home .mode-card .mc-lead{margin:2px 0 4px; font-size:.92rem}
#home .mode-card ul{margin:0 0 10px; font-size:.9rem; line-height:1.45}
#home .mode-card li{margin:.15rem 0}
#home .mode-card .btn{padding:9px 16px}
#home .home-note{margin:10px 0 0}
.home-back{margin:12px 0 0}
.ex-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:16px}
.ex-grid .mode-card p{margin:4px 0 8px; font-size:.95rem}
.ex-grid .mode-card .ex-meta{margin:0 0 12px; font-size:.85rem}
.ex-grid .mode-card h3{font-size:1.2rem}
.ex-grid .mc-head{flex-direction:column; align-items:flex-start; gap:6px}
.ex-grid .mode-card .btn{margin-top:auto; align-self:flex-start}
.ex-grid .en-edition{border-style:dashed; border-color:var(--trait)}
.ex-grid .en-edition h3,.ex-grid .en-edition p{color:var(--encre-2)}
.ex-grid .etat{font-weight:700; color:var(--orange)}
/* cartes de l'accueil : image, titre, mots-clés ; toutes de la même taille, dans toutes les rubriques */
body.hub .ex-grid{grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); grid-auto-rows:1fr}
.carte-v{display:grid; grid-template-rows:auto auto 62px 46px; gap:8px; padding:0 0 16px!important; overflow:hidden; height:100%}
body.hub .carte-v>*:not(.cv-img){margin-left:18px; margin-right:18px}
.carte-v .cv-img{display:block; width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; background:#fff; border-bottom:2px solid var(--encre); margin:0}
.carte-v .cv-vide{background:repeating-linear-gradient(135deg,#F4F5F2 0 12px,#ECEEEA 12px 24px)}
.carte-v .mc-head{margin:6px 18px 0}
.carte-v h3{margin:0; min-height:2.4em; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; line-height:1.2}
#home .carte-v .cv-mots{display:flex; flex-wrap:wrap; align-content:flex-start; gap:5px; list-style:none; margin:0 18px; padding:0}
#home .carte-v .cv-mots li{margin:0}
body.hub .carte-v .btn,body.hub .carte-v .etat{align-self:end; justify-self:start; margin-top:0; margin-bottom:0}
.cv-mots li{font:600 .8rem var(--f-titre); background:var(--bleu-pale); color:var(--encre); border:1px solid #C9D8EC; padding:2px 8px; border-radius:12px; white-space:nowrap}
.en-edition .cv-img{filter:grayscale(1) opacity(.55)}
.en-edition .cv-mots li{background:#F4F5F2; border-color:var(--trait-fin); color:var(--encre-2)}
.pastille{display:inline-block; font:700 .72rem var(--f-titre); letter-spacing:.03em; background:var(--vert); color:#fff; padding:2px 8px; margin-left:6px; vertical-align:middle}
.pastille.n2{background:var(--bleu)}
.mc-tag .pastille{margin-left:8px; font-size:.68rem; padding:1px 6px}
.ex-grid .en-edition{opacity:.62}
body.hub #home{min-height:0}
</style>"""


def page_exercice(e):
    """Copie de la page d'exercice, avec un lien de retour vers l'accueil de ce dépôt."""
    s = (SOURCES / e["source"]).read_text(encoding="utf-8")
    retour = (f'<p class="home-back no-print"><a class="btn ghost retour-accueil" href="index.html">{HOUSE} Accueil : {TITRE}</a></p>')
    css = ("<style>/* lien de retour vers l'accueil du dépôt */\n"
           ".retour-accueil{display:inline-flex; align-items:center; gap:8px; text-decoration:none; margin:0 0 14px}\n"
           ".retour-accueil svg{width:18px; height:18px; flex:0 0 auto}\n"
           f"{e.get('css', '')}</style>")
    i = s.index("</head>")  # la première : une autre figure dans un script (fenêtre d'impression)
    assert i < s.index("<body"), f"{e['source']} : </head> introuvable avant <body>"
    s = s[:i] + css + "\n" + s[i:]
    anchor = e["ancre"]
    assert s.count(anchor) == 1, f"{e['source']} : ancre introuvable ou multiple"
    s = s.replace(anchor, retour + anchor if e.get("avant", True) else anchor + retour)
    return s


def build():
    g = GABARIT.read_text(encoding="utf-8")
    s0 = g.index("<style>:root{")
    style = g[s0:g.index("</style>", s0) + len("</style>")]
    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITRE} — cours et exercices interactifs</title>
<meta name="description" content="{esc(SOUS_TITRE)}">
{style}
{HUB_CSS}
</head>
<body class="no-mode hub">
<section id="home" aria-labelledby="home-title"><div class="home-inner">{render_hub()}</div></section>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html : {len(page.encode('utf-8')) / 1024:.0f} Kio")
    for e in EXERCICES:
        out = page_exercice(e)
        (ROOT / e["page"]).write_text(out, encoding="utf-8")
        print(f"{e['page']} : {len(out.encode('utf-8')) / 1024:.0f} Kio")


if __name__ == "__main__":
    build()
