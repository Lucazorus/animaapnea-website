#!/usr/bin/env python3
"""Build step for the blog.

1. Replaces <!--ALTERNATES--> (or any existing hreflang block) in every article
   with the full hreflang set from slugs.json.
2. Generates the blog index for each language: /blog/index.html (en) and /blog/<lang>/index.html.
3. Regenerates /sitemap.xml.
"""
import html, json, os, re

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.dirname(BLOG)
BASE = 'https://www.animaapnea.com'
LANGS = ['en', 'fr', 'es', 'de', 'it', 'pt', 'ja', 'zh', 'da', 'nl', 'hi', 'id', 'th', 'vi']
REG = json.load(open(os.path.join(BLOG, '_data', 'slugs.json'), encoding='utf-8'))
TODAY = '2026-10-12'

GROUPS = [
    ('start', ['beginner-plan', 'measure-pb', 'without-coach', 'best-app']),
    ('training', ['co2-table', 'o2-table', 'co2-vs-o2', 'three-minutes']),
    ('breathing', ['breathwork', 'breathe-up']),
    ('body', ['contractions', 'dive-reflex', 'blackout', 'equalization']),
]
FEATURED = 'co2-table'

UI = {
    'en': dict(privacy='Privacy policy', title='Guides', h1='Train smarter, hold longer.', lede='Clear, sourced guides to static apnea: the physiology behind a breath-hold, how to train it, and how to stay safe.', start='Getting started', training='Training tables', breathing='Breathing', body='Body and safety', read='min read', meta='Freediving and static apnea guides: CO₂ and O₂ tables, breathwork, contractions, blackout prevention and beginner programs.', home='Home'),
    'fr': dict(privacy='Confidentialité', title='Guides', h1='S’entraîner mieux, tenir plus longtemps.', lede='Des guides clairs et sourcés sur l’apnée statique : la physiologie d’une apnée, comment l’entraîner, et comment rester en sécurité.', start='Bien commencer', training='Tables d’entraînement', breathing='Respiration', body='Corps et sécurité', read='min de lecture', meta='Guides d’apnée statique : tables CO₂ et O₂, respiration, contractions, prévention de la syncope et programmes pour débuter.', home='Accueil'),
    'es': dict(privacy='Privacidad', title='Guías', h1='Entrena mejor, aguanta más.', lede='Guías claras y con fuentes sobre apnea estática: la fisiología de una apnea, cómo entrenarla y cómo hacerlo con seguridad.', start='Para empezar', training='Tablas de entrenamiento', breathing='Respiración', body='Cuerpo y seguridad', read='min de lectura', meta='Guías de apnea estática: tablas CO₂ y O₂, respiración, contracciones, prevención del síncope y programas para principiantes.', home='Inicio'),
    'de': dict(privacy='Datenschutz', title='Ratgeber', h1='Besser trainieren, länger anhalten.', lede='Klare, belegte Ratgeber zur statischen Apnoe: die Physiologie des Atemanhaltens, wie man sie trainiert und wie man dabei sicher bleibt.', start='Erste Schritte', training='Trainingstabellen', breathing='Atmung', body='Körper und Sicherheit', read='Min. Lesezeit', meta='Ratgeber zur statischen Apnoe: CO₂- und O₂-Tabellen, Atemtechnik, Kontraktionen, Blackout-Prävention und Einsteigerprogramme.', home='Startseite'),
    'it': dict(privacy='Privacy', title='Guide', h1='Allenati meglio, resisti di più.', lede='Guide chiare e documentate sull’apnea statica: la fisiologia dell’apnea, come allenarla e come farlo in sicurezza.', start='Per iniziare', training='Tabelle di allenamento', breathing='Respirazione', body='Corpo e sicurezza', read='min di lettura', meta='Guide all’apnea statica: tabelle CO₂ e O₂, respirazione, contrazioni, prevenzione della sincope e programmi per principianti.', home='Home'),
    'pt': dict(privacy='Privacidade', title='Guias', h1='Treine melhor, segure por mais tempo.', lede='Guias claros e com fontes sobre apneia estática: a fisiologia da apneia, como treiná-la e como fazer isso com segurança.', start='Primeiros passos', training='Tabelas de treino', breathing='Respiração', body='Corpo e segurança', read='min de leitura', meta='Guias de apneia estática: tabelas CO₂ e O₂, respiração, contrações, prevenção de apagamento e programas para iniciantes.', home='Início'),
    'ja': dict(privacy='プライバシーポリシー', title='ガイド', h1='賢く鍛えて、もっと長く。', lede='スタティックアプネアのための、根拠のある分かりやすいガイド。息止めの生理学、トレーニング方法、そして安全に続けるために。', start='はじめに', training='トレーニングテーブル', breathing='呼吸', body='身体と安全', read='分で読めます', meta='スタティックアプネアのガイド：CO₂・O₂テーブル、呼吸法、横隔膜の収縮、ブラックアウト予防、初心者向けプログラム。', home='ホーム'),
    'zh': dict(privacy='隐私政策', title='指南', h1='练得更科学，憋得更长久。', lede='关于静态闭气的清晰、有据可查的指南：闭气背后的生理学、训练方法，以及如何安全练习。', start='入门', training='训练表', breathing='呼吸', body='身体与安全', read='分钟阅读', meta='静态闭气指南：CO₂ 与 O₂ 训练表、呼吸法、膈肌收缩、昏厥预防和新手训练计划。', home='首页'),
    'da': dict(privacy='Privatlivspolitik', title='Guides', h1='Træn klogere, hold længere.', lede='Klare guides med kilder om statisk apnø: fysiologien bag at holde vejret, hvordan du træner det, og hvordan du gør det sikkert.', start='Kom godt i gang', training='Træningstabeller', breathing='Vejrtrækning', body='Krop og sikkerhed', read='min. læsning', meta='Guides til statisk apnø: CO₂- og O₂-tabeller, vejrtrækning, kontraktioner, forebyggelse af blackout og begynderprogrammer.', home='Forside'),
    'nl': dict(privacy='Privacybeleid', title='Gidsen', h1='Slimmer trainen, langer volhouden.', lede='Heldere gidsen met bronnen over statische apneu: de fysiologie van het adem inhouden, hoe u het traint en hoe u veilig blijft.', start='Aan de slag', training='Trainingstabellen', breathing='Ademhaling', body='Lichaam en veiligheid', read='min lezen', meta='Gidsen voor statische apneu: CO₂- en O₂-tabellen, ademhaling, contracties, blackoutpreventie en beginnersprogramma’s.', home='Home'),
    'hi': dict(privacy='गोपनीयता नीति', title='गाइड', h1='समझदारी से अभ्यास करें, ज़्यादा देर साँस रोकें।', lede='स्टैटिक एप्निया पर स्पष्ट और प्रमाण-आधारित गाइड: साँस रोकने की फ़िज़ियोलॉजी, इसका अभ्यास कैसे करें और सुरक्षित कैसे रहें।', start='शुरुआत', training='ट्रेनिंग टेबल', breathing='श्वसन', body='शरीर और सुरक्षा', read='मिनट में पढ़ें', meta='स्टैटिक एप्निया गाइड: CO₂ और O₂ टेबल, ब्रीदवर्क, संकुचन, ब्लैकआउट से बचाव और शुरुआती प्रोग्राम।', home='होम'),
    'id': dict(privacy='Kebijakan privasi', title='Panduan', h1='Berlatih lebih cerdas, tahan lebih lama.', lede='Panduan yang jelas dan bersumber tentang apnea statis: fisiologi menahan napas, cara melatihnya, dan cara tetap aman.', start='Memulai', training='Tabel latihan', breathing='Pernapasan', body='Tubuh dan keselamatan', read='menit baca', meta='Panduan apnea statis: tabel CO₂ dan O₂, teknik pernapasan, kontraksi, pencegahan blackout, dan program pemula.', home='Beranda'),
    'th': dict(privacy='นโยบายความเป็นส่วนตัว', title='คู่มือ', h1='ฝึกอย่างเข้าใจ กลั้นได้นานขึ้น', lede='คู่มือการกลั้นหายใจแบบสแตติกที่ชัดเจนและมีแหล่งอ้างอิง ทั้งสรีรวิทยาของการกลั้นหายใจ วิธีฝึก และวิธีฝึกอย่างปลอดภัย', start='เริ่มต้น', training='ตารางฝึก', breathing='การหายใจ', body='ร่างกายและความปลอดภัย', read='นาทีในการอ่าน', meta='คู่มือการกลั้นหายใจแบบสแตติก: ตาราง CO₂ และ O₂ เทคนิคการหายใจ การหดเกร็งของกระบังลม การป้องกันการหมดสติ และโปรแกรมสำหรับผู้เริ่มต้น', home='หน้าแรก'),
    'vi': dict(privacy='Chính sách quyền riêng tư', title='Hướng dẫn', h1='Tập thông minh hơn, nín thở lâu hơn.', lede='Các hướng dẫn rõ ràng, có nguồn dẫn về nín thở tĩnh: sinh lý học của việc nín thở, cách tập luyện và cách giữ an toàn.', start='Bắt đầu', training='Bảng tập luyện', breathing='Hơi thở', body='Cơ thể và an toàn', read='phút đọc', meta='Hướng dẫn nín thở tĩnh: bảng CO₂ và O₂, kỹ thuật thở, co thắt cơ hoành, phòng ngừa ngất và chương trình cho người mới.', home='Trang chủ'),
}


def url(lang, f):
    return f'{BASE}/blog/{lang}/{f}'


def alternates(art_id, indent='  '):
    lines = [f'{indent}<link rel="alternate" hreflang="{l}" href="{url(l, REG[art_id][l])}">' for l in LANGS]
    lines.append(f'{indent}<link rel="alternate" hreflang="x-default" href="{url("en", REG[art_id]["en"])}">')
    return '\n'.join(lines)


def page_meta(path):
    s = open(path, encoding='utf-8').read()
    def grab(rx):
        m = re.search(rx, s, re.S)
        return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''
    return {
        'title': html.unescape(grab(r'<h1[^>]*>(.*?)</h1>')),
        'dek': html.unescape(grab(r'<p class="dek">(.*?)</p>')),
        'kicker': html.unescape(grab(r'<span class="kicker">(.*?)</span>')),
        'mins': grab(r'(\d+)\s*(?:min|分|मिनट|นาที|phút|menit)'),
        'modified': grab(r'"dateModified":\s*"([^"]+)"') or TODAY,
    }


def short_title(lang, fname):
    p = os.path.join(BLOG, lang, fname)
    if not os.path.exists(p): return None
    m = re.search(r'<title>(.*?)</title>', open(p, encoding='utf-8').read(), re.S)
    return re.sub(r'\s*\|\s*Anima Apnea\s*$', '', m.group(1)).strip() if m else None


def sync_related(lang, s):
    """Related cards always show the target article's real title."""
    def rep(m):
        t = short_title(lang, m.group(2))
        return m.group(1) + (t if t else m.group(4)) + m.group(5) if t else m.group(0)
    return re.sub(r'(<a href="(([a-z0-9\-]+\.html))">\s*<span class="k">[^<]*</span>\s*<span class="h">)([^<]*)(</span>)', rep, s)


def fix_articles():
    done, missing = 0, []
    for art_id, per in REG.items():
        for l in LANGS:
            p = os.path.join(BLOG, l, per[l])
            if not os.path.exists(p):
                missing.append(f'{l}/{per[l]}'); continue
            s = orig = open(p, encoding='utf-8').read()
            block = alternates(art_id)
            s = sync_related(l, s)
            # same nav label on every article of a language
            s = re.sub(r'(<a class="blog-home" href="/blog/">)[^<]*(</a>)', lambda m: m.group(1) + UI[l]['title'] + m.group(2), s)
            s = re.sub(r'(<a class="blog-home" href="/blog/)(">)', r'\1' + ('' if l == 'en' else l + '/') + r'\2', s)
            s2 = re.sub(r'(?:[ \t]*<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n)+', '  <!--ALTERNATES-->\n', s)
            s2 = s2.replace('  <!--ALTERNATES-->', block, 1).replace('<!--ALTERNATES-->', block, 1)
            if s2 != orig:
                open(p, 'w', encoding='utf-8').write(s2); done += 1
    return done, missing


def index_page(lang):
    u = UI[lang]
    canon = f'{BASE}/blog/' if lang == 'en' else f'{BASE}/blog/{lang}/'
    prefix = f'{lang}/' if lang == 'en' else ''
    root = '' if lang == 'en' else '../'
    alts = '\n'.join(f'  <link rel="alternate" hreflang="{l}" href="{BASE}/blog/{"" if l == "en" else l + "/"}">' for l in LANGS)
    alts += f'\n  <link rel="alternate" hreflang="x-default" href="{BASE}/blog/">'

    def card(art_id, big=False):
        p = os.path.join(BLOG, lang, REG[art_id][lang])
        if not os.path.exists(p): return ''
        m = page_meta(p)
        mins = f'<span class="mins">{m["mins"]} {u["read"]}</span>' if m['mins'] else ''
        cls = 'feature' if big else 'entry'
        return (f'<a class="{cls}" href="{prefix}{REG[art_id][lang]}">'
                f'<h3>{html.escape(m["title"])}</h3><p>{html.escape(m["dek"])}</p>{mins}</a>')

    groups = ''
    for key, ids in GROUPS:
        cards = ''.join(card(i) for i in ids)
        if cards:
            groups += f'<section class="group"><h2>{u[key]}</h2><div class="entries">{cards}</div></section>\n'

    items = [{"@type": "ListItem", "position": n + 1, "url": url(lang, REG[i][lang])}
             for n, i in enumerate([i for _, ids in GROUPS for i in ids]) if os.path.exists(os.path.join(BLOG, lang, REG[i][lang]))]
    ld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": f'{u["title"]} | Anima Apnea',
                     "url": canon, "inLanguage": lang, "mainEntity": {"@type": "ItemList", "itemListElement": items}}, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{u["title"]} | Anima Apnea</title>
  <meta name="description" content="{html.escape(u["meta"])}">
  <link rel="canonical" href="{canon}">
{alts}
  <meta property="og:title" content="{u["title"]} | Anima Apnea">
  <meta property="og:description" content="{html.escape(u["meta"])}">
  <meta property="og:image" content="{BASE}/og-image.png">
  <link rel="icon" type="image/png" href="/logo-256.png">
  <script type="application/ld+json">{ld}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}style.css?v=20261012">
  <link rel="stylesheet" href="{root}article.css?v=20261012">
  <link rel="stylesheet" href="{root}index.css?v=20261012">
</head>
<body>
  <nav class="blog-nav">
    <div class="nav-left">
      <a class="blog-brand" href="/"><img src="/logo-256.png" alt="" width="28" height="28">Anima Apnea</a>
      <a class="blog-home" href="/">{u["home"]}</a>
    </div>
  </nav>
  <main class="index-main">
    <header class="index-hero">
      <h1>{html.escape(u["h1"])}</h1>
      <p>{html.escape(u["lede"])}</p>
    </header>
    {card(FEATURED, big=True)}
    {groups}
  </main>
  <footer class="blog-footer">
    <p>© 2026 Anima Apnea · <a href="/privacy/{lang}.html">{u["privacy"]}</a></p>
  </footer>
<script src="{root}lang.js?v=20261012"></script>
</body>
</html>
'''


def write_indexes():
    for l in LANGS:
        out = os.path.join(BLOG, 'index.html') if l == 'en' else os.path.join(BLOG, l, 'index.html')
        open(out, 'w', encoding='utf-8').write(index_page(l))


def sitemap():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']

    def entry(loc, alts, lastmod, prio):
        x = [f'  <url>', f'    <loc>{loc}</loc>', f'    <lastmod>{lastmod}</lastmod>', f'    <priority>{prio}</priority>']
        x += [f'    <xhtml:link rel="alternate" hreflang="{h}" href="{a}"/>' for h, a in alts]
        x.append('  </url>')
        return '\n'.join(x)

    home_alts = [(l, f'{BASE}/' if l == 'en' else f'{BASE}/?lang={l}') for l in LANGS] + [('x-default', f'{BASE}/')]
    parts.append(entry(f'{BASE}/', home_alts, TODAY, '1.0'))
    idx_alts = [(l, f'{BASE}/blog/' if l == 'en' else f'{BASE}/blog/{l}/') for l in LANGS] + [('x-default', f'{BASE}/blog/')]
    for l in LANGS:
        parts.append(entry(f'{BASE}/blog/' if l == 'en' else f'{BASE}/blog/{l}/', idx_alts, TODAY, '0.8'))
    for art_id, per in REG.items():
        alts = [(l, url(l, per[l])) for l in LANGS] + [('x-default', url('en', per['en']))]
        for l in LANGS:
            p = os.path.join(BLOG, l, per[l])
            if os.path.exists(p):
                parts.append(entry(url(l, per[l]), alts, page_meta(p)['modified'], '0.7'))
    parts.append('</urlset>\n')
    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(parts))


if __name__ == '__main__':
    n, missing = fix_articles()
    write_indexes()
    sitemap()
    print(f'alternates updated in {n} pages; indexes and sitemap written')
    if missing: print('MISSING PAGES:', len(missing), missing[:20])
