#!/usr/bin/env python3
"""
transform_html.py — Patch UI sur les fichiers HTML existants.

Les nouveaux templates (index.html, collection.html, image.html, contact.html)
contiennent déjà toute l'UI moderne (dropdown, SVG arrows, back button).
Ce script saute les fichiers déjà à jour et ne patche que les anciens.

Signe qu'un fichier est déjà "moderne" : il contient 'lang-dropdown-btn'
ET un SVG dans les flèches carousel (ou pas de carousel du tout).
"""

import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
LANGS = ['fr', 'en', 'de', 'es', 'it', 'ja']
COLLECTIONS_LIST = ['bleu', 'chevaux', 'marron', 'multi', 'ukraine']

BACK = {'fr': 'Retour', 'en': 'Back', 'de': 'Zurück',
        'es': 'Volver', 'it': 'Indietro', 'ja': '戻る'}

SVG_LEFT  = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
             'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
             '<polyline points="15 18 9 12 15 6"></polyline></svg>')
SVG_PREV  = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
             'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
             '<polyline points="15 18 9 12 15 6"></polyline></svg>')
SVG_NEXT  = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
             'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
             '<polyline points="9 18 15 12 9 6"></polyline></svg>')

DROPDOWN_JS = """\
    <script>
    (function(){
      document.querySelectorAll('.lang-dropdown').forEach(function(dd){
        dd.querySelector('.lang-dropdown-btn').addEventListener('click', function(e){
          e.stopPropagation(); dd.classList.toggle('open');
        });
      });
      document.addEventListener('click', function(){
        document.querySelectorAll('.lang-dropdown.open')
          .forEach(function(dd){ dd.classList.remove('open'); });
      });
    })();
    </script>"""

def is_modern(html):
    """Vrai si le fichier a déjà été généré par les nouveaux templates."""
    return 'lang-dropdown-btn' in html and (
        'polyline points="15 18 9 12 15 6"' in html or
        'polyline points="9 18 15 12 9 6"' in html or
        'carousel-arrow' not in html  # pages sans carousel (home, contact, collection)
    )

def patch_dropdown_css(html):
    html = html.replace('top: calc(100% + 6px);', 'top: 100%; padding-top: 6px;')
    html = html.replace(
        '.lang-dropdown:hover .lang-dropdown-menu {\n            display: block;\n        }',
        '.lang-dropdown:hover .lang-dropdown-menu,\n        .lang-dropdown.open .lang-dropdown-menu {\n            display: block;\n        }'
    )
    return html

def patch_back_btn(html, lang):
    label = BACK.get(lang, 'Back')
    # Remplacer ::before content: '←' par vide
    html = re.sub(r"\.back-btn::before\s*\{[^}]*\}", ".back-btn::before { content: ''; }", html)
    # Remplacer le contenu du bouton retour
    html = re.sub(
        r'(<a [^>]*class="back-btn"[^>]*>)\s*[^<]+\s*(</a>)',
        rf'\1{SVG_LEFT} {label}\2', html
    )
    return html

def patch_arrows(html):
    html = html.replace('&#8592;', SVG_PREV)
    html = html.replace('&#8594;', SVG_NEXT)
    return html

def patch_dropdown_js(html):
    if 'lang-dropdown' in html and DROPDOWN_JS not in html:
        html = html.replace('</body>', DROPDOWN_JS + '\n</body>')
    return html

def patch_file(path, lang):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if is_modern(html):
        return False  # déjà à jour
    html = patch_dropdown_css(html)
    html = patch_back_btn(html, lang)
    html = patch_arrows(html)
    html = patch_dropdown_js(html)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

count = skipped = 0
for lang in LANGS:
    for fname in ['index.html', 'contact.html']:
        p = os.path.join(BASE, lang, fname)
        if os.path.exists(p):
            if patch_file(p, lang): count += 1
            else: skipped += 1

    for col in COLLECTIONS_LIST:
        col_dir = os.path.join(BASE, lang, col)
        if not os.path.isdir(col_dir):
            continue
        for fname in os.listdir(col_dir):
            if fname.endswith('.html'):
                p = os.path.join(col_dir, fname)
                if patch_file(p, lang): count += 1
                else: skipped += 1

print(f'✅ {count} fichiers patchés, {skipped} déjà à jour (templates modernes)')
