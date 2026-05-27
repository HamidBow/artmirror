#!/usr/bin/env python3
"""
Générateur de site Art Mirror
Usage: python generate_site.py
Lit les images depuis images/{collection}/ et génère les HTML dans {lang}/{collection}/
"""

import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from data import LANGUAGES, TEXTS, COLLECTIONS, CONTACT_INFO

# ---------- CONFIGURATION ----------
SITE_ROOT      = os.path.dirname(os.path.abspath(__file__))
IMAGES_ROOT    = os.path.join(SITE_ROOT, "images")          # images/collection/*.jpg
BACKGROUND_COLOR   = "#000028"
PORTFOLIO_FILENAME = "mon-portfolio.pdf"

LANG_FLAGS = {
    'fr': '🇫🇷', 'en': '🇬🇧', 'de': '🇩🇪',
    'es': '🇪🇸', 'it': '🇮🇹', 'ja': '🇯🇵',
}

# ---------- SETUP JINJA2 ----------
env = Environment(loader=FileSystemLoader(os.path.join(SITE_ROOT, "templates")))
env.filters['splitext'] = os.path.splitext
index_tpl      = env.get_template("index.html")
collection_tpl = env.get_template("collection.html")
image_tpl      = env.get_template("image.html")
contact_tpl    = env.get_template("contact.html")

# ---------- DISCOVERY ----------
def discover_collections():
    """Retourne la liste des collections avec leurs images."""
    if not os.path.exists(IMAGES_ROOT):
        print(f"⚠️  Dossier images/ introuvable : {IMAGES_ROOT}")
        print("   → Créez images/{collection}/*.jpg et relancez.")
        return []
    result = []
    for slug in sorted(os.listdir(IMAGES_ROOT)):
        cpath = os.path.join(IMAGES_ROOT, slug)
        if not os.path.isdir(cpath):
            continue
        all_files = [f for f in os.listdir(cpath)
                     if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        cover_img   = next((f for f in all_files if "cover" in f.lower()), None)
        normal_files = [f for f in all_files if "cover" not in f.lower()]

        # Ordre personnalisé via _order.json (créé par l'admin)
        order_path = os.path.join(cpath, "_order.json")
        if os.path.exists(order_path):
            with open(order_path, encoding="utf-8") as f:
                custom_order = json.load(f)
            ordered   = [n for n in custom_order if n in normal_files]
            remaining = sorted(n for n in normal_files if n not in ordered)
            normal_files = ordered + remaining
        else:
            normal_files = sorted(normal_files)

        # La cover est incluse dans le carousel (en première position)
        if cover_img:
            images = [{"file": cover_img}] + [{"file": f} for f in normal_files]
        else:
            images = [{"file": f} for f in normal_files]
            if images:
                cover_img = images[0]["file"]
        result.append({"slug": slug, "images": images, "cover_img": cover_img})
    return result

all_collections = discover_collections()

# ---------- GENERATION ----------
for lang in LANGUAGES.keys():
    print(f"🌍 Génération en {LANGUAGES[lang]}…")
    lang_dir = os.path.join(SITE_ROOT, lang)
    os.makedirs(lang_dir, exist_ok=True)

    collections_data = []

    for col in all_collections:
        slug      = col["slug"]
        images    = col["images"]
        cover_img = col["cover_img"]
        collection_title = COLLECTIONS.get(slug, {}).get(lang, slug.capitalize())

        out_col_dir = os.path.join(lang_dir, slug)
        os.makedirs(out_col_dir, exist_ok=True)

        # Chemin relatif depuis lang/slug/ vers images/slug/
        image_base_path = "../../images/" + slug + "/"

        # Page de collection
        html = collection_tpl.render(
            texts=TEXTS, lang=lang, slug=slug,
            images=images, collection_title=collection_title,
            background_color=BACKGROUND_COLOR,
            lang_data=LANGUAGES, lang_flags=LANG_FLAGS,
            image_base_path=image_base_path,
        )
        with open(os.path.join(out_col_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

        # Pages image (avec prev/next pour le carousel)
        for i, img_data in enumerate(images):
            fname = img_data["file"]
            prev_img = images[i - 1] if i > 0 else None
            next_img = images[i + 1] if i < len(images) - 1 else None
            html = image_tpl.render(
                texts=TEXTS, lang=lang, slug=slug,
                collection_title=collection_title,
                file=fname,
                image_path=image_base_path + fname,
                background_color=BACKGROUND_COLOR,
                lang_data=LANGUAGES, lang_flags=LANG_FLAGS,
                prev_img=prev_img, next_img=next_img,
                current_index=i + 1, total_images=len(images),
            )
            out_name = os.path.splitext(fname)[0] + ".html"
            with open(os.path.join(out_col_dir, out_name), "w", encoding="utf-8") as f:
                f.write(html)

        collections_data.append({
            "title": collection_title,
            "slug":  slug,
            "cover": ("../images/" + slug + "/" + cover_img) if cover_img else "",
        })

    # Page de contact
    html = contact_tpl.render(
        texts=TEXTS, lang=lang,
        lang_data=LANGUAGES, contact_info=CONTACT_INFO,
    )
    with open(os.path.join(lang_dir, "contact.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Page d'accueil
    url_for_lang = {code: f"../{code}/" for code in LANGUAGES}
    html = index_tpl.render(
        texts=TEXTS, lang=lang,
        collections=collections_data,
        background_color=BACKGROUND_COLOR,
        lang_data=LANGUAGES, lang_flags=LANG_FLAGS,
        url_for_portfolio=f"../documents/{PORTFOLIO_FILENAME}",
        url_for_lang=url_for_lang,
    )
    with open(os.path.join(lang_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

# Page de redirection racine
redir_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Redirection…</title>
    <script>
        var lang = (navigator.language || navigator.userLanguage).split('-')[0];
        var supported = ['en', 'de', 'es', 'it', 'ja'];
        window.location.replace(supported.includes(lang) ? lang + '/' : 'fr/');
    </script>
</head>
<body></body>
</html>
"""
with open(os.path.join(SITE_ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(redir_html)

print("✅ Génération terminée !")
print(f"   → Pensez à placer vos images dans images/{{collection}}/ avant de lancer ce script.")
