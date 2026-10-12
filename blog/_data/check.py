#!/usr/bin/env python3
"""Validate a blog article against the brief. Usage: check.py <file.html> [...]"""
import json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # blog/
REG = json.load(open(os.path.join(ROOT, '_data', 'slugs.json')))
SLUGS = {(lang, f) for art in REG.values() for lang, f in art.items()}


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.toc, self.h2ids, self.related, self.labels = set(), [], [], [], []
        self.figs = self.details = 0
        self.in_toc = self.in_related = False
        self.stack = []
        self.text = []
        self.in_body = False
        self.skip = 0

    def handle_starttag(self, tag, a):
        a = dict(a)
        cls = a.get('class', '') or ''
        if 'id' in a: self.ids.add(a['id'])
        if tag == 'aside' and 'toc' in cls.split(): self.in_toc = True
        if tag == 'section' and 'related' in cls.split(): self.in_related = True
        if tag == 'a' and self.in_toc and a.get('href', '').startswith('#'): self.toc.append(a['href'][1:])
        if tag == 'a' and self.in_related: self.related.append(a.get('href', ''))
        if tag == 'h2' and 'id' in a: self.h2ids.append(a['id'])
        if tag == 'figure' and 'fig' in cls.split(): self.figs += 1
        if tag == 'details': self.details += 1
        if tag == 'article': self.in_body = True
        if tag in ('script', 'style', 'svg'): self.skip += 1
        for k in ('data-labels', 'data-rounds', 'data-days'):
            if k in a: self.labels.append((k, a[k]))

    def handle_endtag(self, tag):
        if tag == 'aside': self.in_toc = False
        if tag == 'section': self.in_related = False
        if tag == 'article': self.in_body = False
        if tag in ('script', 'style', 'svg'): self.skip -= 1

    def handle_data(self, d):
        if self.in_body and not self.skip: self.text.append(d)


def check(path):
    errs = []
    s = open(path, encoding='utf-8').read()
    lang, fname = os.path.basename(os.path.dirname(path)), os.path.basename(path)
    if (lang, fname) not in SLUGS: errs.append(f'{lang}/{fname} is not in slugs.json')
    if f'<html lang="{lang}">' not in s: errs.append(f'<html lang="{lang}"> missing')
    if f'<link rel="canonical" href="https://www.animaapnea.com/blog/{lang}/{fname}">' not in s:
        errs.append('canonical missing or wrong')
    if '<!--ALTERNATES-->' not in s and 'hreflang="x-default"' not in s: errs.append('<!--ALTERNATES--> marker missing')
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    if not t or not t.group(1).strip().endswith('| Anima Apnea'): errs.append('title must end with "| Anima Apnea"')
    d = re.search(r'<meta name="description" content="([^"]*)"', s)
    if not d: errs.append('meta description missing')
    for need in ['../style.css', '../article.css', '../lang.js', '../article.js', 'class="read-progress"', 'class="article-hero"', 'class="takeaways"', 'class="cta-app"', 'class="refs"', 'class="author-box"', 'class="related"', 'class="toc"', 'class="blog-brand"', 'callout warning']:
        if need not in s: errs.append(f'missing: {need}')
    faq_n = None
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            j = json.loads(m.group(1))
            for node in j.get('@graph', [j]):
                if node.get('@type') == 'FAQPage': faq_n = len(node.get('mainEntity', []))
                if node.get('@type') == 'Article' and node.get('inLanguage') != lang: errs.append('Article.inLanguage wrong')
        except Exception as e:
            errs.append(f'JSON-LD invalid: {e}')
    p = P(); p.feed(s)
    if faq_n is None: errs.append('FAQPage JSON-LD missing')
    elif faq_n != p.details: errs.append(f'FAQPage has {faq_n} questions but page shows {p.details}')
    if p.figs < 2: errs.append(f'only {p.figs} figure(s), need ≥ 2')
    for t_id in p.toc:
        if t_id not in p.ids: errs.append(f'TOC link #{t_id} has no target')
    for h in p.h2ids:
        if h not in p.toc and h != 'faq': errs.append(f'h2#{h} not in TOC')
    for r in re.findall(r'href="#(ref-\d+)"', s):
        if r not in p.ids: errs.append(f'citation #{r} has no source')
    if len(p.related) != 4: errs.append(f'{len(p.related)} related links, need 4')
    for href in p.related + re.findall(r'<a href="([a-z0-9\-]+\.html)"', s):
        if href.startswith('http') or href.startswith('/'): continue
        if (lang, href) not in SLUGS: errs.append(f'link to unknown article {href}')
    for k, v in p.labels:
        try: json.loads(v)
        except Exception: errs.append(f'{k} is not valid JSON: {v[:60]}')
    for svg in re.findall(r'<svg.*?</svg>', s, re.S):
        if re.search(r'(fill|stroke)="#[0-9a-fA-F]{3,6}"', svg): errs.append('hard-coded colour in inline SVG')
    if re.search(r'apple watch|heart rate monitor|fréquence cardiaque', s, re.I): errs.append('mentions a feature the app does not have (watch / heart rate)')
    words = len(re.findall(r'[\w\u0900-\u097F]+', ' '.join(p.text)))
    cjk = len(re.findall(r'[぀-ヿ一-鿿฀-๿]', ' '.join(p.text)))
    if not cjk and not (1500 <= words <= 3300): errs.append(f'body is {words} words (target 1800–2600)')
    return errs


if __name__ == '__main__':
    bad = 0
    for f in sys.argv[1:]:
        e = check(f)
        print(('OK   ' if not e else 'FAIL ') + f)
        for x in e: print('   - ' + x)
        bad += bool(e)
    sys.exit(1 if bad else 0)
