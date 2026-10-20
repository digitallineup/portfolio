"""Add security meta tags to every built HTML page (runs in the deploy workflow).
GitHub Pages cannot send custom HTTP headers, so the policy is delivered as <meta>."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
CSP = ("default-src 'self'; "
       "script-src 'self' 'unsafe-inline'; "
       "style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: https:; "
       "font-src 'self' data:; "
       "media-src 'self' blob:; "
       "connect-src 'self' https://script.google.com https://script.googleusercontent.com https://formsubmit.co; "
       "frame-src https://maps.google.com https://www.google.com; "
       "base-uri 'self'; form-action 'self' https://formsubmit.co; object-src 'none'; "
       "upgrade-insecure-requests")
TAGS = (f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
        '<meta name="referrer" content="strict-origin-when-cross-origin">\n')
n = 0
for p in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in p.relative_to(ROOT).parts):
        continue
    s = p.read_text(encoding='utf-8')
    if 'Content-Security-Policy' in s:
        continue
    s2, k = re.subn(r'(<meta charset="?utf-8"?\s*/?>\s*\n?)', r'\1' + TAGS.replace('\\', r'\\'), s, count=1, flags=re.I)
    if not k:
        s2, k = re.subn(r'(<head[^>]*>\s*\n?)', r'\1' + TAGS, s, count=1, flags=re.I)
    if k:
        p.write_text(s2, encoding='utf-8'); n += 1
print(f'hardened {n} pages')
