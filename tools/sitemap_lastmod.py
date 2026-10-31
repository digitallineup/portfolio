"""Set each sitemap <lastmod> to the date that page's source file last changed in git.

The blog and services builders stamp every URL with the build date, so every deploy
told Google that all pages changed today. Google ignores lastmod once it learns it is
always "now". This makes it truthful again, so a real update gets recrawled faster.
Needs full git history in CI (actions/checkout fetch-depth: 0). Falls back to the
existing value when a page has no known source.
"""
import glob, json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://digitallineup.com'


def gdate(*paths):
    ds = []
    for p in paths:
        try:
            d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', str(p)], cwd=ROOT,
                               capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception:
            d = ''
        if d:
            ds.append(d)
    return max(ds) if ds else ''


src = {'/': ['index.html'], '/work/': ['work/index.html'], '/installers/': ['installers/index.html']}
for f in glob.glob(str(ROOT / 'tools/services/*.html')):
    m = re.search(r'"path"\s*:\s*"([^"]+)"', open(f, encoding='utf-8').read(2000))
    if m:
        src.setdefault(m.group(1), []).append(f)
for f in glob.glob(str(ROOT / 'tools/pages/*.md')):
    m = re.search(r'^path:\s*(\S+)', open(f, encoding='utf-8').read(3000), re.M)
    if m:
        src.setdefault(m.group(1), []).append(f)
posts = sorted(glob.glob(str(ROOT / 'blog/posts/*.md')))
for f in posts:
    src['/blog/' + Path(f).stem + '/'] = [f]
src['/blog/'] = posts
for f in glob.glob(str(ROOT / 'work/*.html')):
    src.setdefault('/work/' + os.path.basename(f), [f])

sm = ROOT / 'sitemap.xml'
x = sm.read_text(encoding='utf-8')


def fix(m):
    path, old = m.group(1), m.group(2)
    d = gdate(*src.get(path, [])) or old
    return f'<loc>{SITE}{path}</loc><lastmod>{d}</lastmod>'


x = re.sub(r'<loc>' + re.escape(SITE) + r'([^<]*)</loc><lastmod>([^<]*)</lastmod>', fix, x)
sm.write_text(x, encoding='utf-8')
print('sitemap lastmod set from git for', len(re.findall('<url>', x)), 'urls')
