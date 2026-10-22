"""Put the shared site header on the hand-built pages (homepage and work/*.html). Safe to run again."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from header import header_html, HEAD, SCRIPTS

def _css(s, head):
    s = re.sub(r'<link rel="stylesheet" href="/css/header\.css[^"]*">', '', s)
    s = re.sub(r'<style id="hd-css">.*?</style>', '', s, flags=re.S)
    return s.replace('</head>', head + '</head>', 1)


HOME_FIX = ('<style id="hd-fix">.hero{margin-top:10px!important;padding-top:clamp(56px,8vh,100px)!important}'
            '@media(max-width:700px){.hero{padding-top:44px!important}}</style>')


def swap(path, active, cta, extra_head=''):
    s = path.read_text(encoding='utf-8')
    new_hdr = header_html(active, '', cta)
    if '<header class="hd">' in s:
        s2 = re.sub(r'<header class="hd">.*?</header>\s*<nav class="mnav".*?</nav>', lambda m: new_hdr, s, count=1, flags=re.S)
    else:
        s2 = re.sub(r'<header class="nav">.*?</header>', lambda m: new_hdr, s, count=1, flags=re.S)
        s2 = re.sub(r'\s*<nav class="menu" aria-label="Site menu">.*?</nav>', '', s2, count=1, flags=re.S)
    s2 = re.sub(r'<link rel="stylesheet" href="/css/header\\.css[^"]*">', '', s2)
    if re.search(r'<style id="hd-css">.*?</style>', s2, flags=re.S):
        s2 = re.sub(r'<style id="hd-css">.*?</style>', lambda m: HEAD, s2, count=1, flags=re.S)
    else:
        s2 = s2.replace('</head>', HEAD + ('' if 'id="hd-fix"' in s2 else extra_head) + '</head>', 1)
    if '/js/header.js' not in s2:
        s2 = s2.replace('</body>', SCRIPTS + '</body>', 1)
    if s2 != s:
        path.write_text(s2, encoding='utf-8')
        return 1
    return 0


n = swap(ROOT / 'index.html', 'home', '#contact', HOME_FIX)
for p in sorted((ROOT / 'work').glob('*.html')):
    n += swap(p, 'work', '/contact/')
print('header applied to', n, 'pages')
