"""Tell Bing, Copilot, Yandex and other IndexNow engines about pages that changed in this deploy.

Only URLs whose sitemap <lastmod> (set from git by sitemap_lastmod.py) matches the date of the
commit being deployed are sent. Re-sending the whole site on every push (2,000+ URLs in 10 days)
reads as noise to Bing and can slow indexing rather than speed it up.
"""
import json, re, subprocess, urllib.request, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = '0e1bc3e14f8d4e0f8a0eb6cb454d3c00'
head = subprocess.run(['git', 'log', '-1', '--format=%cs'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
pairs = re.findall(r'<loc>(.*?)</loc><lastmod>(.*?)</lastmod>', (ROOT / 'sitemap.xml').read_text())
urls = [u for u, d in pairs if d == head]
if not urls:
    print('IndexNow: no page content changed in this deploy, nothing sent')
    raise SystemExit(0)
body = json.dumps({'host': 'digitallineup.com', 'key': KEY,
                   'keyLocation': f'https://digitallineup.com/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                             headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow', r.status, len(urls), 'urls')
except Exception as e:
    print('IndexNow failed (non-blocking):', e)
