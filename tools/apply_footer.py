"""Swap the old one-line footer on hand-built pages (work/*.html) for the shared site footer."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from footer import footer_html, HEAD, SCRIPTS
n = 0
for p in sorted((ROOT / 'work').glob('*.html')):
    s = p.read_text(encoding='utf-8')
    s2 = re.sub(r'<footer class="foot">.*?</footer>|<footer class="foot2" id="footer">.*?</footer>', lambda m: footer_html(), s, count=1, flags=re.S)
    s2 = re.sub(r'<link rel="stylesheet" href="/css/footer\\.css[^"]*">', '', s2)
    if re.search(r'<style id="ft-css">.*?</style>', s2, flags=re.S):
        s2 = re.sub(r'<style id="ft-css">.*?</style>', lambda m: HEAD, s2, count=1, flags=re.S)
    else:
        s2 = s2.replace('</head>', HEAD + '' + '</head>', 1)
    s2 = re.sub(r'<script src="/js/matter\.min\.js" defer></script>', '', s2)
    s2 = re.sub(r'<script src="/js/footer\.js[^"]*" defer></script>', '', s2)
    s2 = s2.replace('</body>', SCRIPTS + '</body>', 1)
    if s2 != s:
        p.write_text(s2, encoding='utf-8'); n += 1
print('footer applied to', n, 'pages')
