# -*- coding: utf-8 -*-
"""Erzeugt die App-Seiten docs/plan.html und docs/analyse.html
aus ../trainingsplan.md und ../analyse.md.

Nur Standardbibliothek. Der Markdown-Umfang ist auf das beschränkt, was die beiden
Dateien verwenden: Überschriften, Absätze, Tabellen, Zitate, einfache Listen,
Trennlinien, <details>-Blöcke sowie fett, kursiv, Code und Links im Text."""
import html
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
DOCS = os.path.join(ROOT, 'docs')

TABS = [('./', 'Fueling', 'index'), ('plan.html', 'Trainingsplan', 'plan'), ('analyse.html', 'Analyse', 'analyse')]

PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · Fueling-Rechner</title>
<meta name="robots" content="noindex">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f9f9f7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0d0d0d" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="stylesheet" href="style.css">
</head>
<body>
<!-- Erzeugt von werkzeug/export_app.py aus {source} – nicht von Hand ändern. -->

{header}

<main class="doc" data-page="{page}">
{body}
</main>

<footer class="foot">Erzeugt aus <code>{source}</code>.</footer>

<script src="pwa.js" defer></script>
{scripts}</body>
</html>
"""

# Zelle sieht nach Zahl aus (mit Einheit): solche Spalten werden rechtsbündig gesetzt
NUM = re.compile(r'^(?:[≈~<>±+\-–−]\s?)?\d[\d.,:]*(?:\s?(?:%|h|W|kg|m/h|W/kg|g/h|TSS|km|hm|min|s|bpm|°C|€))?$')
DASHES = ('', '—', '–', '-')


def header(current):
    links = ''.join(
        '    <a class="tab" href="%s"%s>%s</a>\n' % (href, ' aria-current="page"' if key == current else '', label)
        for href, label, key in TABS)
    return ('<header class="top">\n  <nav class="tabs" aria-label="Bereiche">\n%s  </nav>\n'
            '  <button type="button" class="chip" id="install" hidden>Installieren</button>\n</header>' % links)


def inline(text):
    s = html.escape(text, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return s


def plain(text):
    return re.sub(r'[*`]', '', text).strip()


def slug(text):
    s = plain(text).lower()
    for a, b in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss')):
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'abschnitt'


def table(lines):
    rows = [[c.strip() for c in ln.strip().strip('|').split('|')] for ln in lines]
    has_sep = len(lines) > 1 and re.match(r'^[\s:|-]+$', lines[1]) is not None
    head = rows[0] if has_sep else None
    body = rows[2:] if has_sep else rows
    n = max(len(r) for r in rows)
    cell = lambda r, i: r[i] if i < len(r) else ''
    numeric = []
    for i in range(n):
        vals = [plain(cell(r, i)) for r in body]
        filled = [v for v in vals if v not in DASHES]
        numeric.append(bool(filled) and all(NUM.match(v) for v in filled))
    cls = lambda i: ' class="num"' if numeric[i] else ''
    out = ['<div class="table-wrap"><table%s>' % (' class="wide"' if n >= 7 else '')]
    if head and any(head):
        out.append('<thead><tr>%s</tr></thead>' % ''.join(
            '<th scope="col"%s>%s</th>' % (cls(i), inline(cell(head, i))) for i in range(n)))
    out.append('<tbody>')
    for r in body:
        out.append('<tr>%s</tr>' % ''.join('<td%s>%s</td>' % (cls(i), inline(cell(r, i))) for i in range(n)))
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def blocks(md):
    """Zerlegt Markdown in eine Liste aus ('h', Ebene, Text), ('hr',) und ('html', Text)."""
    out = []
    para, quote, items, rows = [], [], [], []

    def flush():
        if para:
            parts = []
            for ln in para:
                parts.append(inline(ln.strip()) + ('<br>' if ln.endswith('  ') else ' '))
            out.append(('html', '<p>%s</p>' % ''.join(parts).rstrip()))
            del para[:]
        if quote:
            out.append(('html', '<blockquote><p>%s</p></blockquote>' % inline(' '.join(quote))))
            del quote[:]
        if items:
            out.append(('html', '<ul>\n%s\n</ul>' % '\n'.join('<li>%s</li>' % inline(x) for x in items)))
            del items[:]
        if rows:
            out.append(('html', table(rows)))
            del rows[:]

    for raw in md.split('\n'):
        line = raw.rstrip('\r')
        stripped = line.strip()
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if not stripped:
            flush()
        elif m:
            flush()
            out.append(('h', len(m.group(1)), m.group(2).strip()))
        elif re.match(r'^-{3,}$', stripped):
            flush()
            out.append(('hr',))
        elif stripped.startswith('<details') or stripped.startswith('</details'):
            flush()
            out.append(('html', stripped))
        elif line.startswith('|'):
            if not rows:
                flush()
            rows.append(line)
        elif line.startswith('>'):
            if not quote:
                flush()
            quote.append(re.sub(r'^>\s?', '', line).strip())
        elif re.match(r'^[-*]\s+', line):
            if not items:
                flush()
            items.append(re.sub(r'^[-*]\s+', '', line).strip())
        elif items and line.startswith(' '):
            items[-1] += ' ' + stripped          # Fortsetzung eines Listenpunkts
        else:
            if not para:
                flush()
            para.append(line)
    flush()
    return out


def render(md, page):
    """Fasst alles unter einer h2-Überschrift zu einer Karte zusammen."""
    title = None
    sections = [{'attrs': ' class="card intro"', 'html': []}]
    used = set()
    for b in blocks(md):
        if b[0] == 'hr':
            continue                              # Karten trennen schon, Linien wären doppelt
        if b[0] == 'html':
            sections[-1]['html'].append(b[1])
            continue
        level, text = b[1], b[2]
        if level == 1:
            title = title or plain(text)
            sections[-1]['html'].append('<h1>%s</h1>' % inline(text))
        elif level == 2:
            week = re.match(r'^KW\s*(\d+)/(\d{4})\s*·\s*([^·]+?)(?:\s*·\s*(.+))?$', text)
            if page == 'plan' and week:
                kw, year, dates, tag = int(week.group(1)), week.group(2), week.group(3).strip(), week.group(4)
                key = '%s-%02d' % (year, kw)
                attrs = ' class="card week" id="kw-%s" data-week="%s"' % (key, key)
                head = '<h2>KW %d <small>%s · %s</small>%s</h2>' % (
                    kw, inline(dates), year, ' <span class="pill">%s</span>' % inline(tag) if tag else '')
            else:
                sid = slug(text)
                while sid in used:
                    sid += '-2'
                used.add(sid)
                attrs = ' class="card" id="%s"' % sid
                head = '<h2>%s</h2>' % inline(text)
            sections.append({'attrs': attrs, 'html': [head]})
        else:
            sections[-1]['html'].append('<h%d>%s</h%d>' % (level, inline(text), level))
    if page == 'plan':
        sections[0]['html'].append(
            '<p><button type="button" class="chip" id="jump-week" hidden>Zur aktuellen Woche</button></p>')
    body = '\n\n'.join('<section%s>\n%s\n</section>' % (s['attrs'], '\n'.join(s['html']))
                       for s in sections if s['html'])
    return title or page, body


def export(source, target, page, scripts=''):
    md = io.open(os.path.join(ROOT, source), encoding='utf-8').read()
    title, body = render(md, page)
    out = PAGE.format(title=html.escape(title), source=source, page=page, header=header(page),
                      body=body, scripts=scripts)
    io.open(os.path.join(DOCS, target), 'w', encoding='utf-8', newline='\n').write(out)
    print('%s -> docs/%s (%d Abschnitte, %.0f kB)' % (source, target, body.count('<section'), len(out.encode('utf-8')) / 1024.0))


if __name__ == '__main__':
    export('trainingsplan.md', 'plan.html', 'plan', '<script src="doc.js" defer></script>\n')
    export('analyse.md', 'analyse.html', 'analyse')
