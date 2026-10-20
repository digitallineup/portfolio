"""Add security meta tags to every built HTML page (runs in the deploy workflow).
GitHub Pages cannot send custom HTTP headers, so the policy is delivered as <meta>."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / 'tools' / 'site-config.json').read_text())
GA, CL = CFG.get('ga4_measurement_id', '').strip(), CFG.get('clarity_project_id', '').strip()
CSP = ("default-src 'self'; "
       "script-src 'self' 'unsafe-inline'"
       + (" https://www.googletagmanager.com" if GA else "") + (" https://www.clarity.ms https://*.clarity.ms" if CL else "") + "; "
       "style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: https:; "
       "font-src 'self' data:; "
       "media-src 'self' blob:; "
       "connect-src 'self' https://script.google.com https://script.googleusercontent.com https://formsubmit.co"
       + (" https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com" if GA else "")
       + (" https://*.clarity.ms https://c.bing.com" if CL else "") + "; "
       "frame-src https://maps.google.com https://www.google.com; "
       "base-uri 'self'; form-action 'self' https://formsubmit.co; object-src 'none'; "
       "upgrade-insecure-requests")
TAGS = (f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
        '<meta name="referrer" content="strict-origin-when-cross-origin">\n')
# Analytics: loaded after the first scroll/tap or 3.5s idle so phone speed is unaffected.
# Also records leads (form posts to the Apps Script) and WhatsApp clicks as GA4 events.
ANALYTICS = ''
if GA or CL:
    ANALYTICS = """<script>
(function(){var GA=%s,CL=%s;window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}window.gtag=gtag;
if(GA){gtag('js',new Date());gtag('config',GA);}
var f=window.fetch;if(f){window.fetch=function(u,o){try{if(String(u).indexOf('script.google.com/macros')>-1&&o&&o.method==='POST')gtag('event','generate_lead',{page_path:location.pathname});}catch(e){}return f.apply(this,arguments)}}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*="wa.me"]');if(a)gtag('event','whatsapp_click',{page_path:location.pathname});},true);
var done=0;function go(){if(done)return;done=1;
if(GA){var s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s);}
if(CL){(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script",CL);}}
['scroll','pointerdown','keydown','touchstart'].forEach(function(t){addEventListener(t,go,{once:true,passive:true})});setTimeout(go,3500);})();
</script>
""" % (json.dumps(GA), json.dumps(CL))
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
    if k and ANALYTICS and 'noindex' not in s2:
        s2 = s2.replace('</head>', ANALYTICS + '</head>', 1)
    if k:
        p.write_text(s2, encoding='utf-8'); n += 1
print(f'hardened {n} pages')
