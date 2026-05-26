#!/usr/bin/env python3
"""
Patch 3 :
- Bouton back : icône SVG chevron + texte court ("Retour", "Back"…)
- Fix mobile : titre de collection pas masqué par les boutons fixes
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
LANGS = ['fr', 'en', 'de', 'es', 'it', 'ja']
COLLECTIONS_LIST = ['bleu', 'chevaux', 'marron', 'multi', 'ukraine']

# Texte court par langue
BACK = {'fr': 'Retour', 'en': 'Back', 'de': 'Zurück',
        'es': 'Volver', 'it': 'Indietro', 'ja': '戻る'}

# SVG chevron gauche (même style que les flèches carousel)
SVG_LEFT = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2.5" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<polyline points="15 18 9 12 15 6"></polyline></svg>'
)

# CSS mobile à injecter dans les pages collection (body a un padding-top fixe)
MOBILE_CSS = """\
        @media (max-width: 600px) {
            body { padding-top: 90px; }
            .header h1 { font-size: 1.6em; margin-top: 10px; }
        }"""

def patch_back_btn_css(html):
    """Remplace '←' par rien dans le CSS (le SVG est maintenant dans le HTML)."""
    return re.sub(
        r"\.back-btn::before\s*\{[^}]*\}",
        ".back-btn::before { content: ''; }",
        html
    )

def patch_back_btn_html(html, lang):
    """Remplace le texte du bouton back par SVG + mot court."""
    label = BACK[lang]
    # Remplace tout texte dans class="back-btn">...</a>
    html = re.sub(
        r'(<a [^>]*class="back-btn"[^>]*>)\s*[^<]+\s*(</a>)',
        rf'\1{SVG_LEFT} {label}\2',
        html
    )
    return html

def add_mobile_css(html):
    """Injecte le CSS mobile avant </style> si pas déjà présent."""
    if '@media (max-width: 600px)' not in html:
        html = html.replace('    </style>', MOBILE_CSS + '\n    </style>', 1)
    return html

count = 0

for lang in LANGS:
    # ── Homepages ──────────────────────────────────────────────────────────────
    p = os.path.join(BASE, lang, 'index.html')
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: html = f.read()
        html = patch_back_btn_css(html)
        html = patch_back_btn_html(html, lang)
        with open(p, 'w', encoding='utf-8') as f: f.write(html)
        count += 1

    # ── Contact ────────────────────────────────────────────────────────────────
    p = os.path.join(BASE, lang, 'contact.html')
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: html = f.read()
        html = patch_back_btn_css(html)
        html = patch_back_btn_html(html, lang)
        with open(p, 'w', encoding='utf-8') as f: f.write(html)
        count += 1

    for col in COLLECTIONS_LIST:
        col_dir = os.path.join(BASE, lang, col)

        # ── Collection index ───────────────────────────────────────────────────
        p = os.path.join(col_dir, 'index.html')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: html = f.read()
            html = patch_back_btn_css(html)
            html = patch_back_btn_html(html, lang)
            html = add_mobile_css(html)
            with open(p, 'w', encoding='utf-8') as f: f.write(html)
            count += 1

        # ── Pages image ────────────────────────────────────────────────────────
        for fname in os.listdir(col_dir):
            if fname.endswith('.html') and fname != 'index.html':
                p = os.path.join(col_dir, fname)
                with open(p, 'r', encoding='utf-8') as f: html = f.read()
                html = patch_back_btn_css(html)
                html = patch_back_btn_html(html, lang)
                with open(p, 'w', encoding='utf-8') as f: f.write(html)
                count += 1

print(f'✅ {count} fichiers patchés')
