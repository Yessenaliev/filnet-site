# -*- coding: utf-8 -*-
"""Сборка страниц сайта.

Редактируется русский шаблон  src/index.ru.html  и казахский словарь KK в  js/main.js.
Затем:  python tools/build.py

Получается:
  index.html      — казахская версия, открывается по основной ссылке
  ru/index.html   — русская версия
  kk/index.html   — переадресация со старого адреса /kk/ на основной
Файлы index.html, ru/index.html и kk/index.html руками не править: сборка их перезапишет.

Порядок языков в переключателе: ҚАЗ, (позже ENG — сразу после казахского), RU.
Нужны Python 3 и Node.js (словарь читается из JavaScript).
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
URL = 'https://yessenaliev.github.io/filnet-site/'

SRC = open('src/index.ru.html', encoding='utf-8').read()

# --- казахский словарь из js/main.js ---
NODE = ("const J=require('fs').readFileSync('js/main.js','utf8');"
        "const s=J.slice(J.indexOf('var PH ='),J.indexOf('var WA_PREFIX'));"
        "process.stdout.write(JSON.stringify(new Function(s+';return KK;')()))")
KK = json.loads(subprocess.run(['node', '-e', NODE], check=True, capture_output=True).stdout.decode('utf-8'))


def plain(s):
    return re.sub('<[^>]+>', '', s)


def head_links(self_url):
    return ('<link rel="canonical" href="%s">\n'
            '<link rel="alternate" hreflang="kk" href="%s">\n'
            '<link rel="alternate" hreflang="ru" href="%sru/">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">\n') % (self_url, URL, URL, URL)


def set_head(page, self_url):
    page = re.sub(r'<link rel="(?:canonical|alternate)"[^>]*>\n?', '', page)
    page = page.replace('<meta name="theme-color"', head_links(self_url) + '<meta name="theme-color"', 1)
    return page.replace('<meta property="og:url" content="%s">' % URL,
                        '<meta property="og:url" content="%s">' % self_url)


# --- русская страница: ru/index.html ---
ru = set_head(SRC, URL + 'ru/')
for attr in ['href="css/', 'src="js/', 'src="assets/', 'data-src="assets/', 'data-lb="assets/',
             'poster="assets/', 'href="privacy.html']:
    ru = ru.replace(attr, attr.replace('="', '="../', 1))

# --- казахская страница: index.html ---
kk = SRC
kk = re.sub(r'(<(\w+)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)(.*?)(</\2>)',
            lambda m: m.group(1) + (KK.get(m.group(3)) or m.group(4)) + m.group(5), kk, flags=re.S)
kk = re.sub(r'alt="([^"]*)"( data-i18n-alt="([^"]+)")',
            lambda m: 'alt="%s"%s' % (KK.get(m.group(3), m.group(1)), m.group(2)), kk)
kk = re.sub(r'aria-label="([^"]*)"( data-i18n-aria="([^"]+)")',
            lambda m: 'aria-label="%s"%s' % (KK.get(m.group(3), m.group(1)), m.group(2)), kk)
kk = kk.replace('<html lang="ru" data-lang="ru">', '<html lang="kk" data-lang="kk">')

TITLE = 'Филнет-Казахстан — бүкіл Қазақстан бойынша бас мердігер'
DESCR = ('«Филнет-Казахстан» ЖШС — бүкіл Қазақстан бойынша бас мердігер: өндірістік, коммерциялық және '
         'қоғамдық ғимараттар. Смета мен жұмыс барысы Тапсырыс берушіге ашық.')
kk = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, kk, count=1)
kk = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + DESCR + m.group(2), kk, count=1)
kk = re.sub(r'<meta property="og:title" content="[^"]*">',
            '<meta property="og:title" content="Филнет-Казахстан — саламыз, көрсетеміз, жауап береміз">', kk)
kk = re.sub(r'<meta property="og:description" content="[^"]*">',
            '<meta property="og:description" content="Бүкіл Қазақстан бойынша бас мердігер. '
            'Смета мен жұмыс барысы Тапсырыс берушіге ашық.">', kk)
kk = kk.replace('<meta property="og:site_name" content="Филнет-Казахстан">',
                '<meta property="og:site_name" content="Филнет-Казахстан">')
kk = kk.replace('<meta property="og:locale" content="ru_RU">', '<meta property="og:locale" content="kk_KZ">')
kk = kk.replace('<meta property="og:locale:alternate" content="kk_KZ">',
                '<meta property="og:locale:alternate" content="ru_RU">')

# кнопки языка: активна казахская
kk = kk.replace('data-set-lang="kk">', 'data-set-lang="kk" class="is-on">')
kk = kk.replace('data-set-lang="ru" class="is-on">', 'data-set-lang="ru">')

# разметка FAQ на казахском
FAQ = re.findall(r'<details><summary data-i18n="(fq\.q\d+)">(.*?)</summary><p data-i18n="(fq\.a\d+)">(.*?)</p></details>',
                 SRC, re.S)
ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": plain(KK.get(q, qt)),
     "acceptedAnswer": {"@type": "Answer", "text": plain(KK.get(a, at))}} for q, qt, a, at in FAQ]}
kk, n_ld = re.subn(r'<script type="application/ld\+json">\{"@context": ?"https://schema.org", ?"@type": ?"FAQPage".*?</script>',
                   lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>',
                   kk, count=1, flags=re.S)
assert n_ld == 1, 'FAQ JSON-LD not found'
kk = set_head(kk, URL)

os.makedirs('ru', exist_ok=True)
os.makedirs('kk', exist_ok=True)
open('index.html', 'w', encoding='utf-8').write(kk)
open('ru/index.html', 'w', encoding='utf-8').write(ru)

# --- старый адрес /kk/ ---
open('kk/index.html', 'w', encoding='utf-8').write(
    '<!doctype html>\n<html lang="kk">\n<head>\n<meta charset="utf-8">\n<meta name="robots" content="noindex">\n'
    '<meta http-equiv="refresh" content="0; url=../">\n<link rel="canonical" href="%s">\n'
    '<title>Филнет-Казахстан</title>\n</head>\n<body><a href="../">Филнет-Казахстан</a></body>\n</html>\n' % URL)

open('sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + ''.join(
        '<url><loc>%s</loc><xhtml:link rel="alternate" hreflang="kk" href="%s"/>'
        '<xhtml:link rel="alternate" hreflang="ru" href="%sru/"/></url>\n' % (u, URL, URL)
        for u in (URL, URL + 'ru/')) + '</urlset>\n')

print('built: index.html (kk), ru/index.html, kk/index.html (redirect), sitemap.xml; kk keys:', len(KK))
