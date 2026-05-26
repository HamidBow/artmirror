#!/usr/bin/env python3
"""
Patch 2 : fix dropdown hover gap + JS click, flèches SVG, contact info
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
LANGS = ['fr', 'en', 'de', 'es', 'it', 'ja']
COLLECTIONS_LIST = ['bleu', 'chevaux', 'marron', 'multi', 'ukraine']

# ── SVG chevrons ──────────────────────────────────────────────────────────────
SVG_PREV = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<polyline points="15 18 9 12 15 6"></polyline></svg>'
)
SVG_NEXT = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<polyline points="9 18 15 12 9 6"></polyline></svg>'
)

# ── JS snippet (click toggle + close on outside click) ────────────────────────
DROPDOWN_JS = """\
    <script>
    (function(){
      document.querySelectorAll('.lang-dropdown').forEach(function(dd){
        var btn = dd.querySelector('.lang-dropdown-btn');
        btn.addEventListener('click', function(e){
          e.stopPropagation();
          dd.classList.toggle('open');
        });
      });
      document.addEventListener('click', function(){
        document.querySelectorAll('.lang-dropdown.open')
          .forEach(function(dd){ dd.classList.remove('open'); });
      });
    })();
    </script>"""

# ── CSS fix: bridge the 6px gap + .open class ────────────────────────────────
OLD_MENU_TOP  = 'top: calc(100% + 6px);'
NEW_MENU_TOP  = 'top: 100%; padding-top: 6px;'
OLD_HOVER_CSS = '.lang-dropdown:hover .lang-dropdown-menu {\n            display: block;\n        }'
NEW_HOVER_CSS = (
    '.lang-dropdown:hover .lang-dropdown-menu,\n'
    '        .lang-dropdown.open .lang-dropdown-menu {\n'
    '            display: block;\n'
    '        }'
)


def patch_html(html):
    """Applique tous les correctifs à un fichier HTML."""
    # 1. Fix gap du dropdown
    html = html.replace(OLD_MENU_TOP, NEW_MENU_TOP)
    # 2. Ajouter .open au sélecteur CSS
    html = html.replace(OLD_HOVER_CSS, NEW_HOVER_CSS)
    # 3. Remplacer flèches HTML entities par SVG
    html = html.replace('&#8592;', SVG_PREV)
    html = html.replace('&#8594;', SVG_NEXT)
    # 4. Injecter JS juste avant </body> (si pas déjà présent)
    if 'lang-dropdown' in html and DROPDOWN_JS not in html:
        html = html.replace('</body>', DROPDOWN_JS + '\n</body>')
    return html


def patch_contact(lang):
    """Met à jour les informations de contact."""
    path = os.path.join(BASE, lang, 'contact.html')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    # Téléphone
    html = re.sub(
        r'href="tel:[^"]*">[^<]*</a>',
        'href="tel:+33643477112">+33643477112</a>',
        html
    )
    # Facebook URL + affichage
    html = re.sub(
        r'href="https://www\.facebook\.com/[^"]*"[^>]*>[^<]*</a>',
        'href="https://www.facebook.com/hamid.bow.7" target="_blank">@hamid.bow.7</a>',
        html
    )
    # Aussi corriger le back-link → back-btn
    html = re.sub(r'\s*\.back-link\s*\{[^}]*\}', '', html, flags=re.DOTALL)
    html = html.replace('class="back-link"', 'class="back-btn"')
    if '.back-btn' not in html:
        back_css = """\n        .back-btn {
            position: fixed; top: 16px; left: 16px; z-index: 300;
            display: inline-flex; align-items: center; gap: 7px;
            padding: 8px 16px 8px 12px;
            background: rgba(255,255,255,0.12); color: white;
            text-decoration: none; border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.28);
            font-size: 0.92em; font-weight: 600;
            backdrop-filter: blur(6px);
            transition: background 0.2s, transform 0.15s; white-space: nowrap;
        }
        .back-btn:hover { background: rgba(255,255,255,0.22); transform: translateX(-3px); }
        .back-btn::before { content: '←'; font-size: 1.05em; }"""
        html = html.replace('    </style>', back_css + '\n    </style>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


# ── Run ───────────────────────────────────────────────────────────────────────
count = 0
for lang in LANGS:
    # Homepage
    p = os.path.join(BASE, lang, 'index.html')
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: html = f.read()
        html = patch_html(html)
        with open(p, 'w', encoding='utf-8') as f: f.write(html)
        count += 1

    # Contact
    patch_contact(lang)
    count += 1

    for col in COLLECTIONS_LIST:
        # Collection index
        p = os.path.join(BASE, lang, col, 'index.html')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: html = f.read()
            html = patch_html(html)
            with open(p, 'w', encoding='utf-8') as f: f.write(html)
            count += 1

        # Image pages
        for fname in os.listdir(os.path.join(BASE, lang, col)):
            if fname.endswith('.html') and fname != 'index.html':
                p = os.path.join(BASE, lang, col, fname)
                with open(p, 'r', encoding='utf-8') as f: html = f.read()
                html = patch_html(html)
                with open(p, 'w', encoding='utf-8') as f: f.write(html)
                count += 1

print(f'✅ {count} fichiers patchés')
