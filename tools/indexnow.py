"""Tell Bing, Copilot, Yandex and other IndexNow engines about every URL in the sitemap (runs after deploy)."""
import json, re, urllib.request, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = '0e1bc3e14f8d4e0f8a0eb6cb454d3c00'
urls = re.findall(r'<loc>(.*?)</loc>', (ROOT / 'sitemap.xml').read_text())
body = json.dumps({'host': 'digitallineup.com', 'key': KEY,
                   'keyLocation': f'https://digitallineup.com/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                             headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow', r.status, len(urls), 'urls')
except Exception as e:
    print('IndexNow failed (non-blocking):', e)
