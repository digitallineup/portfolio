"""Add security meta tags to every built HTML page (runs in the deploy workflow).
GitHub Pages cannot send custom HTTP headers, so the policy is delivered as <meta>."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / 'tools' / 'site-config.json').read_text())
GA, CL = CFG.get('ga4_measurement_id', '').strip(), CFG.get('clarity_project_id', '').strip()
CSP = ("default-src 'self'; "
       "script-src 'self' 'unsafe-inline' https://app.cal.com"
       + (" https://www.googletagmanager.com" if GA else "") + (" https://www.clarity.ms https://*.clarity.ms" if CL else "") + "; "
       "style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: https:; "
       "font-src 'self' data:; "
       "media-src 'self' blob:; "
       "connect-src 'self' https://app.cal.com https://cal.com https://script.google.com https://script.googleusercontent.com https://formsubmit.co"
       + (" https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com" if GA else "")
       + (" https://*.clarity.ms https://c.bing.com" if CL else "") + "; "
       "frame-src https://maps.google.com https://www.google.com https://cal.com https://app.cal.com; "
       "base-uri 'self'; form-action 'self' https://formsubmit.co; object-src 'none'; "
       "upgrade-insecure-requests")
TAGS = (f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
        '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
        # Anti-clickjacking: frame-ancestors is ignored in a meta CSP, so refuse to render inside a foreign frame.
        '<style id="afc">html{display:none}</style><script>if(self===top){var a=document.getElementById("afc");a.parentNode.removeChild(a)}else{try{top.location=self.location}catch(e){}}</script>\n')
# Analytics: loaded after the first scroll/tap or 3.5s idle so phone speed is unaffected.
# Also records leads (form posts to the Apps Script) and WhatsApp clicks as GA4 events.
GUARD = "<script>\n/* Lead guard: stamps every lead with a page token + timing, drops obvious bots, and tells analytics only about clean leads. */\n(function(){var t0=Date.now(),hu=0;['pointerdown','keydown','touchstart','scroll'].forEach(function(e){addEventListener(e,function(){hu=1},{once:true,passive:true,capture:true})});\nvar f=window.fetch;if(!f)return;\nfunction digits(v){return String(v||'').replace(/\\D/g,'').length}\nfunction soft(d){var r=[],n=String(d.name||'').trim(),b=String(d.business||'').trim().toLowerCase(),em=String(d.email||'').toLowerCase();\nif(d.phone&&(digits(d.phone)<10||digits(d.phone)>15))r.push('phone');\nif(/[bcdfghjklmnpqrstvwxz]{4,}|[bcdfghjkmnpqrstvwxz]{3,}$/i.test(n.replace(/\\s/g,'')))r.push('name');\nif(/^[A-Z][a-z]+[A-Z][a-z]{1,3}$/.test(n))r.push('name2');\nif(/^(aliexpress|nokia|google|amazon|facebook|meta|apple|microsoft|test|asdf|qwerty)$/.test(b))r.push('brand');\nif(/no-?reply|noreply/.test(em)||/@[a-z0-9-]+\\.[a-z0-9-]+\\.[a-z]{2,}$/.test(em)&&!/\\.(com|net|org|edu|gov)\\.[a-z]{2}$/.test(em))r.push('email');\nif(/https?:\\/\\//i.test(String(d.details||'')+String(d.name||''))) r.push('link');\nreturn r}\nwindow.fetch=function(u,o){try{if(String(u).indexOf('script.google.com/macros')>-1&&o&&o.method==='POST'&&typeof o.body==='string'){\nvar d=JSON.parse(o.body),ms=Date.now()-t0;\nif(d._honey||ms<3000||!hu){return Promise.resolve(new Response('ok',{status:200}))}\nvar r=soft(d);d._k='dl7k2026';d._ms=ms;d._flags=r.join(',');d._spam=r.length>=2?'likely':'';o.body=JSON.stringify(d);\nif(!d._spam){try{dispatchEvent(new CustomEvent('dl:lead',{detail:{page:location.pathname}}))}catch(e){}}\n}}catch(e){}return f.apply(this,arguments)}})();\n</script>\n"
ANALYTICS = ''
if GA or CL:
    ANALYTICS = """<script>
(function(){var GA=%s,CL=%s;window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}window.gtag=gtag;
if(GA){gtag('js',new Date());gtag('config',GA);}
addEventListener('dl:lead',function(e){gtag('event','generate_lead',{page_path:location.pathname});});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*="wa.me"]');if(a)gtag('event','whatsapp_click',{page_path:location.pathname});},true);
var done=0;function go(){if(done)return;done=1;
if(GA){var s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s);}
if(CL){(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script",CL);}}
['pointerdown','keydown','touchstart','wheel'].forEach(function(t){addEventListener(t,go,{once:true,passive:true})});setTimeout(go,9000);})();
</script>
""" % (json.dumps(GA), json.dumps(CL))
n = 0
for p in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in p.relative_to(ROOT).parts):
        continue
    s = p.read_text(encoding='utf-8')
    if 'Content-Security-Policy' in s:
        continue
    s2, k = re.subn(r'(<meta charset="?utf-8"?\s*/?>\s*\n?)', r'\1' + (TAGS + GUARD).replace('\\', r'\\'), s, count=1, flags=re.I)
    if not k:
        s2, k = re.subn(r'(<head[^>]*>\s*\n?)', lambda m: m.group(1) + TAGS + GUARD, s, count=1, flags=re.I)
    if k and ANALYTICS and 'noindex' not in s2:
        s2 = s2.replace('</head>', ANALYTICS + '</head>', 1)
    if k and 'og:site_name' not in s2:
        s2 = s2.replace('</head>', '<meta property="og:site_name" content="Digital Lineup">\n</head>', 1)
    if k:
        p.write_text(s2, encoding='utf-8'); n += 1
print(f'hardened {n} pages')
