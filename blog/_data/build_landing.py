#!/usr/bin/env python3
"""Génère une homepage par langue (/fr/, /es/, …) à partir du gabarit /index.html.

1. Fusionne les textes rédigés nativement (blog/_data/landing/<lang>.json) dans /i18n.js.
2. Pour chaque langue autre que l'anglais, écrit /<lang>/index.html avec le texte
   directement dans le HTML (indexable sans JavaScript), sa propre URL canonique,
   son <title>, sa description et ses balises Open Graph.
Usage : python3 blog/_data/build_landing.py
"""
import html, json, os, re, subprocess

DATA = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(DATA))
BASE = 'https://www.animaapnea.com'
LANGS = ['en', 'fr', 'es', 'de', 'it', 'pt', 'ja', 'zh', 'da', 'nl', 'hi', 'id', 'th', 'vi']
LOCALE = {'en': 'en_US', 'fr': 'fr_FR', 'es': 'es_ES', 'de': 'de_DE', 'it': 'it_IT', 'pt': 'pt_BR', 'ja': 'ja_JP',
          'zh': 'zh_CN', 'da': 'da_DK', 'nl': 'nl_NL', 'hi': 'hi_IN', 'id': 'id_ID', 'th': 'th_TH', 'vi': 'vi_VN'}


def load_i18n():
    js = os.path.join(SITE, 'i18n.js')
    out = subprocess.run(['node', '-e', f"global.window={{}};require({json.dumps(js)});process.stdout.write(JSON.stringify(window.ANIMA_I18N))"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def merge_native(i18n, only=None):
    en_keys = set(i18n['en']['data'])
    for l in (only or LANGS):
        p = os.path.join(DATA, 'landing', f'{l}.json')
        if l == 'en' or not os.path.exists(p):
            continue
        native = json.load(open(p, encoding='utf-8'))
        if native.get('title'):
            i18n[l]['title'] = native['title']
        for k, v in native.items():
            if k in en_keys and isinstance(v, str) and v.strip():
                i18n[l]['data'][k] = v
    return i18n


def write_i18n(i18n):
    body = json.dumps(i18n, ensure_ascii=False, indent=1)
    head = ('/* Textes de la homepage, une entrée par langue (rédigés nativement).\n'
            '   Généré par blog/_data/build_landing.py à partir de blog/_data/landing/<lang>.json.\n'
            '   {t} dans dialResult est remplacé par la durée de l’apnée. */\n')
    open(os.path.join(SITE, 'i18n.js'), 'w', encoding='utf-8').write(head + 'window.ANIMA_I18N = ' + body + ';\n')


def fill(template, d):
    """Remplace le contenu des éléments data-i18n / data-i18n-html par le texte de la langue."""
    out = re.sub(r'(<(\w+)[^>]*\bdata-i18n="([\w]+)"[^>]*>)(.*?)(</\2>)',
                 lambda m: m.group(1) + (html.escape(d[m.group(3)], quote=False) if m.group(3) in d else m.group(4)) + m.group(5),
                 template, flags=re.S)
    out = re.sub(r'(<(\w+)[^>]*\bdata-i18n-html="([\w]+)"[^>]*>)(.*?)(</\2>)',
                 lambda m: m.group(1) + d.get(m.group(3), m.group(4)) + m.group(5),
                 out, flags=re.S)
    return out


def set_meta(page, l, entry):
    d = entry['data']
    url = f'{BASE}/' if l == 'en' else f'{BASE}/{l}/'
    title = entry.get('title') or d.get('heroTitle', 'Anima Apnea')
    if 'Anima' not in title:
        title = f'Anima Apnea · {title}'
    desc = re.sub(r'<[^>]+>', '', d.get('heroLede', ''))
    page = re.sub(r'<html lang="[^"]*">', f'<html lang="{l}">', page, count=1)
    page = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title, quote=False)}</title>', page, count=1, flags=re.S)
    page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', page, count=1)
    page = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title)}">', page, count=1)
    page = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(desc)}">', page, count=1)
    page = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', page, count=1)
    page = re.sub(r'<meta property="og:locale" content="[^"]*">\n', '', page)
    page = page.replace('<meta property="og:type"', f'<meta property="og:locale" content="{LOCALE[l]}">\n  <meta property="og:type"', 1)
    page = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', page, count=1)
    # liens internes de la page vers les bonnes langues
    page = page.replace('href="/privacy/en.html"', f'href="/privacy/{l}.html"')
    if l != 'en':
        page = page.replace('href="/blog/" data-blog-index', f'href="/blog/{l}/" data-blog-index')
    return page


def main():
    import sys
    only = sys.argv[1:] or None  # ex. : build_landing.py fr es it (langues dont le texte natif est prêt)
    i18n = merge_native(load_i18n(), only)
    write_i18n(i18n)
    template = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
    for l in LANGS:
        if l == 'en' or l not in i18n:
            continue
        page = set_meta(fill(template, i18n[l]['data']), l, i18n[l])
        os.makedirs(os.path.join(SITE, l), exist_ok=True)
        open(os.path.join(SITE, l, 'index.html'), 'w', encoding='utf-8').write(page)
    merged = [l for l in (only or LANGS) if os.path.exists(os.path.join(DATA, 'landing', f'{l}.json'))]
    print('homepages générées :', ', '.join(l for l in LANGS if l != 'en'))
    print('textes natifs fusionnés :', ', '.join(merged) or 'aucun')


if __name__ == '__main__':
    main()
