#!/usr/bin/env python3
"""
Script d'amélioration UI pour Art Mirror:
1. Dropdown de langue CSS avec drapeaux (sur toutes les pages)
2. Boutons "Back" redessinés
3. Carousel prev/next sur les pages image
"""

import os
import re

SITE_ROOT = '/home/user/artmirror'
LANGS = ['fr', 'en', 'de', 'es', 'it', 'ja']
COLLECTIONS_LIST = ['bleu', 'chevaux', 'marron', 'multi', 'ukraine']

LANG_FLAGS = {
    'fr': '🇫🇷', 'en': '🇬🇧', 'de': '🇩🇪',
    'es': '🇪🇸', 'it': '🇮🇹', 'ja': '🇯🇵'
}
LANG_NAMES = {
    'fr': 'Français', 'en': 'English', 'de': 'Deutsch',
    'es': 'Español', 'it': 'Italiano', 'ja': '日本語'
}

BACK_TEXTS = {
    'fr': {'home': "Retour à l'accueil", 'collection': 'Retour à la collection'},
    'en': {'home': 'Back to home', 'collection': 'Back to the collection'},
    'de': {'home': 'Zurück zur Startseite', 'collection': 'Zurück zur Sammlung'},
    'es': {'home': 'Volver a la página principal', 'collection': 'Volver a la colección'},
    'it': {'home': 'Torna alla home', 'collection': 'Torna alla collezione'},
    'ja': {'home': 'ホームに戻る', 'collection': 'コレクションに戻る'},
}

# Build image order for carousel (sorted, all images including cover)
collection_images = {}
for col in COLLECTIONS_LIST:
    imgs = []
    col_path = os.path.join(SITE_ROOT, 'en', col)
    for f in sorted(os.listdir(col_path)):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            imgs.append(os.path.splitext(f)[0])
    collection_images[col] = imgs

# ─────────────────────────────── CSS BLOCKS ──────────────────────────────────

LANG_DROPDOWN_CSS = """\
        /* ── Language dropdown ── */
        .lang-dropdown {
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 300;
            font-family: Arial, sans-serif;
        }
        .lang-dropdown-btn {
            padding: 8px 14px;
            background: rgba(255,255,255,0.12);
            color: white;
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.92em;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 7px;
            backdrop-filter: blur(6px);
            transition: background 0.2s;
            white-space: nowrap;
        }
        .lang-dropdown-btn:hover {
            background: rgba(255,255,255,0.22);
        }
        .lang-dropdown-menu {
            display: none;
            position: absolute;
            right: 0;
            top: calc(100% + 6px);
            background: rgba(0,0,40,0.97);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 10px;
            overflow: hidden;
            min-width: 168px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.55);
        }
        .lang-dropdown:hover .lang-dropdown-menu {
            display: block;
        }
        .lang-dropdown-menu a {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 16px;
            color: white;
            text-decoration: none;
            font-size: 0.93em;
            transition: background 0.15s;
        }
        .lang-dropdown-menu a:hover {
            background: rgba(255,255,255,0.1);
        }
        .lang-dropdown-menu a.lang-active {
            background: rgba(255,255,255,0.14);
            font-weight: 700;
        }"""

BACK_BTN_CSS = """\
        /* ── Back button ── */
        .back-btn {
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 300;
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 8px 16px 8px 12px;
            background: rgba(255,255,255,0.12);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.28);
            font-size: 0.92em;
            font-weight: 600;
            backdrop-filter: blur(6px);
            transition: background 0.2s, transform 0.15s;
            white-space: nowrap;
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.22);
            transform: translateX(-3px);
        }
        .back-btn::before { content: '←'; font-size: 1.05em; }"""

CAROUSEL_CSS = """\
        /* ── Carousel navigation ── */
        .carousel-arrow {
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            z-index: 300;
        }
        .carousel-arrow.prev { left: 14px; }
        .carousel-arrow.next { right: 14px; }
        .carousel-arrow a {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 46px;
            height: 46px;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 50%;
            color: white;
            text-decoration: none;
            font-size: 1.3em;
            backdrop-filter: blur(6px);
            transition: background 0.2s, transform 0.15s;
        }
        .carousel-arrow a:hover {
            background: rgba(255,255,255,0.25);
            transform: scale(1.1);
        }
        .carousel-counter {
            position: fixed;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 300;
            background: rgba(0,0,40,0.72);
            color: rgba(255,255,255,0.85);
            padding: 5px 16px;
            border-radius: 20px;
            font-size: 0.82em;
            font-family: Arial, sans-serif;
            border: 1px solid rgba(255,255,255,0.16);
            backdrop-filter: blur(4px);
            letter-spacing: 0.05em;
        }"""

# ─────────────────────────────── HTML BUILDERS ───────────────────────────────

def make_dropdown_html(current_lang, link_prefix, current_col=None):
    """Génère le HTML du dropdown de langue."""
    flag = LANG_FLAGS[current_lang]
    name = LANG_NAMES[current_lang]
    lines = [
        f'    <div class="lang-dropdown">',
        f'        <button class="lang-dropdown-btn">{flag}&nbsp;{name} ▾</button>',
        f'        <div class="lang-dropdown-menu">',
    ]
    # Français toujours en premier
    for lang in ['fr', 'en', 'de', 'es', 'it', 'ja']:
        lf = LANG_FLAGS[lang]
        ln = LANG_NAMES[lang]
        if current_col:
            href = f'{link_prefix}{lang}/{current_col}/'
        else:
            href = f'{link_prefix}{lang}/'
        active = ' class="lang-active"' if lang == current_lang else ''
        lines.append(f'            <a href="{href}"{active}>{lf}&nbsp;{ln}</a>')
    lines += ['        </div>', '    </div>']
    return '\n'.join(lines)

def make_carousel_html(col, img_stem, lang):
    """Génère prev/next arrows et le compteur."""
    imgs = collection_images.get(col, [])
    if img_stem not in imgs:
        return '', ''
    idx = imgs.index(img_stem)
    total = len(imgs)

    prev_html = ''
    if idx > 0:
        prev_stem = imgs[idx - 1]
        prev_html = (
            f'    <div class="carousel-arrow prev">\n'
            f'        <a href="{prev_stem}.html" title="Précédent">&#8592;</a>\n'
            f'    </div>'
        )

    next_html = ''
    if idx < total - 1:
        next_stem = imgs[idx + 1]
        next_html = (
            f'    <div class="carousel-arrow next">\n'
            f'        <a href="{next_stem}.html" title="Suivant">&#8594;</a>\n'
            f'    </div>'
        )

    counter_html = f'    <div class="carousel-counter">{idx + 1} / {total}</div>'
    nav_html = '\n'.join(filter(None, [prev_html, next_html, counter_html]))
    return nav_html

# ─────────────────────────────── PROCESSORS ──────────────────────────────────

def inject_css_before_closing_style(html, new_css):
    """Injecte du CSS juste avant </style>."""
    return html.replace('    </style>', f'{new_css}\n    </style>', 1)

def inject_html_after_body(html, new_html):
    """Injecte du HTML juste après <body...>."""
    return re.sub(r'(<body[^>]*>)', r'\1\n' + new_html, html, count=1)

def inject_html_before_closing_body(html, new_html):
    """Injecte du HTML juste avant </body>."""
    return html.replace('</body>', new_html + '\n</body>', 1)

# ── HOMEPAGE ─────────────────────────────────────────────────────────────────

def process_homepage(lang):
    path = os.path.join(SITE_ROOT, lang, 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remplacer CSS lang-container + lang-button
    html = re.sub(
        r'\s*\.lang-container\s*\{[^}]*\}\s*\.lang-button\s*\{[^}]*\}',
        '\n' + LANG_DROPDOWN_CSS,
        html, flags=re.DOTALL
    )

    # 2. Remplacer le bloc HTML lang-container
    html = re.sub(
        r'<div class="lang-container">.*?</div>',
        make_dropdown_html(lang, '../'),
        html, flags=re.DOTALL
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

# ── COLLECTION INDEX ──────────────────────────────────────────────────────────

def process_collection_index(lang, col):
    path = os.path.join(SITE_ROOT, lang, col, 'index.html')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remplacer CSS back-link
    html = re.sub(
        r'\s*\.back-link\s*\{[^}]*\}',
        '\n' + BACK_BTN_CSS,
        html, flags=re.DOTALL
    )

    # 2. Injecter CSS dropdown
    html = inject_css_before_closing_style(html, LANG_DROPDOWN_CSS)

    # 3. Remplacer class back-link → back-btn sur le lien
    html = html.replace('class="back-link"', 'class="back-btn"')

    # 4. Injecter dropdown HTML après <body>
    dropdown_html = make_dropdown_html(lang, '../../', current_col=col)
    html = inject_html_after_body(html, dropdown_html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

# ── IMAGE PAGE ────────────────────────────────────────────────────────────────

def process_image_page(lang, col, img_stem):
    path = os.path.join(SITE_ROOT, lang, col, f'{img_stem}.html')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remplacer CSS back-link
    html = re.sub(
        r'\s*\.back-link\s*\{[^}]*\}',
        '\n' + BACK_BTN_CSS,
        html, flags=re.DOTALL
    )

    # 2. Injecter CSS dropdown + carousel
    html = inject_css_before_closing_style(html, LANG_DROPDOWN_CSS + '\n' + CAROUSEL_CSS)

    # 3. back-link → back-btn
    html = html.replace('class="back-link"', 'class="back-btn"')

    # 4. Injecter dropdown + carousel HTML après <body>
    dropdown_html = make_dropdown_html(lang, '../../', current_col=col)
    carousel_html = make_carousel_html(col, img_stem, lang)
    html = inject_html_after_body(html, dropdown_html + '\n' + carousel_html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

# ─────────────────────────────── MAIN ────────────────────────────────────────

if __name__ == '__main__':
    count = 0
    for lang in LANGS:
        # Homepage
        p = process_homepage(lang)
        print(f'  ✅ {p}')
        count += 1

        for col in COLLECTIONS_LIST:
            # Collection index
            p = process_collection_index(lang, col)
            if p:
                print(f'  ✅ {p}')
                count += 1

            # Image pages
            for img_stem in collection_images.get(col, []):
                p = process_image_page(lang, col, img_stem)
                if p:
                    count += 1

    print(f'\n✅ {count} fichiers traités')
