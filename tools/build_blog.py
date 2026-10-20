#!/usr/bin/env python3
"""Builds the Digital Lineup blog, sitemap.xml and llms.txt.

Write a post as blog/posts/<slug>.md with a header like:

    ---
    title: The post title
    description: One or two sentences for Google (under 160 characters).
    date: 2026-10-20
    cover: /img/some-image.jpg
    cover_alt: What the image shows
    tags: Meta ads, Australia
    ---

    The article in Markdown...

Then run:  python3 tools/build_blog.py   (GitHub Actions also runs it on every push.)
"""
import html, json, os, re, glob, datetime
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://digitallineup.com'
ORG = {'@id': SITE + '/#org'}
AUTHOR = {'@type': 'Person', '@id': SITE + '/#ali', 'name': 'Ali Hannan Siddique', 'jobTitle': 'Founder, Digital Lineup',
          'url': SITE + '/'}


def read_post(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
    if not m:
        raise SystemExit(f'{path}: missing --- header ---')
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip()
    meta['slug'] = os.path.splitext(os.path.basename(path))[0]
    meta['body_md'] = m.group(2)
    meta['tags'] = [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]
    if meta.get('draft', '').lower() in ('yes', 'true'):
        return None
    words = len(re.findall(r'\w+', m.group(2)))
    meta['minutes'] = max(1, round(words / 220))
    return meta


def esc(s):
    return html.escape(s, quote=True)


CSS = """
:root{--cream:#FBF6EF;--cream-2:#F4ECE1;--sand:#EFE3D3;--mint:#DCEDE2;--ink:#0B1F15;--ink-2:#2A3A32;--muted:#5F6E66;--line:rgba(11,31,21,.12);--green:#03180e;--lime:#00d24c;--font:"Helvetica Neue",Helvetica,"Inter",Arial,sans-serif;--ease:cubic-bezier(.2,.8,.2,1)}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:84px}
body{background:var(--cream);color:var(--ink);font-family:var(--font);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased}
img{display:block;max-width:100%;height:auto}
a{color:inherit}
.wrap{width:100%;max-width:1200px;margin:0 auto;padding:0 20px}
.top{position:sticky;top:0;z-index:20;background:rgba(251,246,239,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:12px}
.top nav{display:flex;align-items:center;gap:22px;font-size:14px;font-weight:600}
.top nav a{text-decoration:none}
.top nav a.on{color:var(--green);text-decoration:underline;text-decoration-color:var(--lime);text-decoration-thickness:2px;text-underline-offset:6px}
.top .go{background:var(--green);color:var(--cream);padding:9px 16px;border-radius:999px}
.top img{height:30px;width:auto}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--lime);color:var(--green);font-weight:700;font-size:16px;padding:14px 22px;border-radius:999px;text-decoration:none;border:0;cursor:pointer;font-family:inherit}
.btn.ghost{background:transparent;border:1.5px solid rgba(251,246,239,.4);color:var(--cream)}
.dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--lime);margin-right:7px;vertical-align:middle;transform:translateY(-1px)}
h1,h2,h3{letter-spacing:-.03em;line-height:1.12;font-weight:600}
/* index */
.bh{padding-top:64px;padding-bottom:34px}
.bh h1{font-size:clamp(46px,8.4vw,112px);line-height:.98;letter-spacing:-.045em;font-weight:500}
.bh h1 span{display:block;overflow:hidden}
.bh h1 span i{display:block;font-style:normal;transform:translateY(105%);transition:transform 1s var(--ease)}
.bh.in h1 span i{transform:none}
.bh h1 span:nth-child(2) i{transition-delay:.12s}
.bh p{color:var(--muted);max-width:46ch;margin-top:20px;font-size:18px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 30px}
.chip{font:inherit;font-size:13px;font-weight:600;border:1.5px solid var(--ink);background:transparent;color:var(--ink);border-radius:999px;padding:6px 14px;cursor:pointer;transition:background .25s,color .25s}
.chip.on,.chip:hover{background:var(--ink);color:var(--cream)}
.grid{display:grid;gap:52px 18px;padding-bottom:90px}
.card{display:block;text-decoration:none;opacity:0;transform:translateY(28px);transition:opacity .8s var(--ease),transform .8s var(--ease)}
.card.in{opacity:1;transform:none}
.card.hide{display:none}
.card .im{border-radius:22px;overflow:hidden;height:var(--h,230px);background:var(--sand);will-change:height}
.card .im img{width:100%;height:100%;object-fit:cover;transition:transform 1.1s var(--ease)}
.card:hover .im img{transform:scale(1.05)}
.card .d{font-size:13px;color:var(--muted);margin-top:16px}
.card h2{font-size:22px;letter-spacing:-.02em;line-height:1.25;margin:6px 0 10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card p{font-size:15px;color:var(--muted);line-height:1.75;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
/* article hero */
.ah{background:var(--cream-2);border-bottom:1px solid var(--line)}
.ah .wrap{display:grid;gap:30px;padding-top:40px;padding-bottom:44px;align-items:center}
.crumb{font-size:12px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px}
.crumb a{text-decoration:none}
.ah h1{font-size:clamp(30px,4.6vw,48px);margin:14px 0 18px}
.ah .meta{display:flex;flex-wrap:wrap;gap:16px;font-size:13px;color:var(--muted)}
.ah .meta span{display:inline-flex;align-items:center;gap:6px}
.ah .meta svg{width:15px;height:15px}
.ah .by{display:flex;align-items:center;gap:12px;margin-top:20px}
.ah .by img{width:44px;height:44px;border-radius:12px;object-fit:cover;object-position:top}
.ah .by b{display:block;font-size:15px}
.ah .by small{font-size:12px;color:var(--muted)}
.ah .cv{border-radius:22px;overflow:hidden;aspect-ratio:16/10}
.ah .cv img{width:100%;height:100%;object-fit:cover}
/* body layout */
.body{display:grid;gap:34px;padding-top:48px;padding-bottom:40px}
.side{display:none}
.toc b{display:block;font-size:13px;font-weight:700;padding-bottom:12px;border-bottom:1px solid var(--line);margin-bottom:12px}
.toc a{display:block;font-size:13px;line-height:1.45;color:var(--muted);text-decoration:none;padding:5px 0;transition:color .2s}
.toc a.on{color:var(--ink);font-weight:600}
.mtoc{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px 18px}
.mtoc summary{font-weight:700;font-size:15px;cursor:pointer}
.mtoc .toc{margin-top:10px}
.mtoc .toc b{display:none}
.scard{background:#fff;border:1px solid var(--line);border-radius:22px;padding:20px;margin-top:26px;box-shadow:0 30px 60px -40px rgba(3,24,14,.35)}
.scard .rb{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;border:1px solid var(--line);border-radius:10px;padding:6px 10px}
.scard .rb i{color:#f5a623;font-style:normal;letter-spacing:1px}
.scard h3{font-size:19px;margin:14px 0 6px}
.scard p{font-size:13px;color:var(--muted);line-height:1.5}
.scard form{display:grid;gap:8px;margin-top:14px}
.scard input{font:inherit;font-size:15px;padding:11px 12px;border:1.5px solid var(--line);border-radius:10px;background:var(--cream);width:100%}
.scard input:focus{outline:none;border-color:var(--green);background:#fff}
.scard .btn{width:100%;padding:12px}
.scard .note{text-align:center;font-size:12px;margin-top:10px}
.scard .ok{display:none;background:var(--mint);border-radius:10px;padding:12px;font-weight:700;font-size:14px;margin-top:12px}
.scard form.sent{display:none}.scard form.sent+.ok{display:block}
.hp{position:absolute;left:-9999px}
/* prose */
.prose{min-width:0}
.prose>*:first-child{margin-top:0}
.prose h2{font-size:clamp(25px,3vw,32px);margin:52px 0 14px}
.prose h3{font-size:21px;margin:30px 0 10px}
.prose p,.prose ul,.prose ol,.prose blockquote{margin:0 0 18px}
.prose p,.prose li{color:var(--ink-2)}
.prose ul,.prose ol{padding-left:22px}
.prose li{margin:7px 0}
.prose strong{color:var(--ink)}
.prose a{color:var(--green);text-decoration-color:var(--lime);text-decoration-thickness:2px;text-underline-offset:3px}
.prose blockquote{border-left:4px solid var(--lime);padding:4px 0 4px 18px;font-size:20px;color:var(--ink)}
.prose table{width:100%;border-collapse:collapse;font-size:15px;margin:0 0 22px;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden;display:table}
.tw{overflow-x:auto;margin:0 0 22px}.tw table{margin:0}
.prose th,.prose td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line)}
.prose th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);background:var(--cream-2)}
.prose tr:last-child td{border-bottom:0}
.qa{background:var(--mint);border:1px solid rgba(3,24,14,.1);border-radius:18px;padding:18px 22px;margin:0 0 12px}
.qa h3{font-size:22px;margin:0 0 8px}
.qa p{font-size:15px;margin:0 0 6px}
.qa p:last-child{margin:0}
.tldr{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px 24px;margin:0 0 26px}
.tldr b{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;color:var(--muted)}
.tldr ul{margin:0}
.panel{background:var(--cream-2);border:1px solid var(--line);border-radius:24px;padding:22px;margin:8px 0 28px}
.panel>h4{font-size:22px;letter-spacing:-.02em;font-weight:600}
.panel>p{font-size:16px;color:var(--ink-2);margin:6px 0 16px}
.steps{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(150px,1fr);gap:10px;background:var(--lime);border-radius:18px;padding:14px;overflow-x:auto;scroll-snap-type:x mandatory}
.step{background:#fff;border-radius:14px;padding:16px 14px;scroll-snap-align:start;min-height:170px}
.step i{display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:var(--mint);font-style:normal;font-weight:700;font-size:14px;color:var(--green);margin-bottom:12px}
.step b{display:block;font-size:17px;line-height:1.2;letter-spacing:-.01em;color:var(--ink)}
.step span{display:block;font-size:13px;color:var(--muted);line-height:1.45;margin-top:6px}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.tile{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px}
.tile.g{background:var(--lime);border-color:var(--lime)}
.tile small{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:var(--ink-2)}
.tile b{display:block;font-size:clamp(24px,3vw,32px);letter-spacing:-.03em;line-height:1.1;margin:6px 0 4px;color:var(--ink)}
.tile span{font-size:13px;color:var(--ink-2)}
.cta{background:var(--green);color:var(--cream);border-radius:24px;padding:30px 26px;margin:48px 0 10px}
.cta h2{font-size:28px;margin:0 0 10px;color:var(--cream)}
.cta p{color:rgba(251,246,239,.8);margin-bottom:18px;font-size:16px}
.cta .row{display:flex;flex-wrap:wrap;gap:10px}
.author{display:flex;gap:16px;align-items:flex-start;border-top:1px solid var(--line);padding:28px 0;margin-top:20px}
.author img{width:64px;height:64px;border-radius:16px;object-fit:cover;object-position:top;flex:none}
.author b{display:block;font-size:17px}
.author p{font-size:14px;color:var(--muted);line-height:1.55;margin-top:4px}
.more{padding:30px 0 90px;border-top:1px solid var(--line)}
.more h2{font-size:clamp(28px,4vw,40px);margin:30px 0 26px;font-weight:500}
.rv{opacity:0;transform:translateY(22px);transition:opacity .8s var(--ease),transform .8s var(--ease)}
.rv.in{opacity:1;transform:none}
.foot{border-top:1px solid var(--line);padding:30px 0;font-size:14px;color:var(--muted)}
.foot .wrap{display:flex;flex-wrap:wrap;gap:10px 22px;justify-content:space-between}
.foot a{text-decoration:none;color:var(--ink)}
@media (min-width:760px){.grid{grid-template-columns:repeat(2,1fr)}}
@media (min-width:1020px){
  .grid{grid-template-columns:repeat(3,1fr)}
  .ah .wrap{grid-template-columns:1.05fr 1fr;gap:56px;padding-top:56px;padding-bottom:60px}
  .body{grid-template-columns:290px minmax(0,1fr);gap:64px;padding-top:64px}
  .side{display:block}.side .stick{position:sticky;top:92px}
  .mtoc{display:none}
  .prose{max-width:760px}
}
@media (max-width:560px){.top nav .hide-s{display:none}.card .im{height:var(--h,210px)}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}.card,.rv{opacity:1;transform:none}.bh h1 span i{transform:none}}
"""

LEADS_URL = 'https://script.google.com/macros/s/AKfycbzxXJoWIFjgC3vkHPjD8hULkTI7GZZrGoFeuULeVolUNI9fhGg2DP7Lt_m7JjRn-85CKQ/exec'

JS_INDEX = """<script>(function(){
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
var bh=document.querySelector('.bh'); requestAnimationFrame(function(){bh.classList.add('in');});
var cards=[].slice.call(document.querySelectorAll('.card'));
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12});
cards.forEach(function(c,i){c.style.transitionDelay=(i%3)*90+'ms';io.observe(c);});
document.querySelectorAll('.chip').forEach(function(ch){ch.addEventListener('click',function(){
  document.querySelectorAll('.chip').forEach(function(x){x.classList.remove('on');});ch.classList.add('on');
  var f=ch.dataset.f;cards.forEach(function(c){c.classList.toggle('hide',f!=='all'&&(c.dataset.tags||'').split('|').indexOf(f)<0);});
});});
if(rm)return;
var ims=[].slice.call(document.querySelectorAll('.card .im')),tick=false;
function upd(){tick=false;var vh=innerHeight,small=innerWidth<560,max=small?210:230,min=small?150:130;
  ims.forEach(function(im){var r=im.getBoundingClientRect();var p=Math.min(1,Math.max(0,(vh*0.72-r.top)/(vh*0.6)));im.style.setProperty('--h',(max-(max-min)*p).toFixed(1)+'px');});}
addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(upd);}},{passive:true});addEventListener('resize',upd);upd();
})();</script>"""

JS_POST = """<script>(function(){
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.1});
document.querySelectorAll('.rv,.card').forEach(function(el){io.observe(el);});
var links=[].slice.call(document.querySelectorAll('.side .toc a')),heads=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));}).filter(Boolean);
function act(){var y=120,cur=heads[0];heads.forEach(function(h){if(h.getBoundingClientRect().top<y)cur=h;});links.forEach(function(a){a.classList.toggle('on',cur&&a.getAttribute('href')==='#'+cur.id);});}
addEventListener('scroll',act,{passive:true});act();
document.querySelectorAll('.prose table').forEach(function(t){var w=document.createElement('div');w.className='tw';t.parentNode.insertBefore(w,t);w.appendChild(t);});
var f=document.getElementById('sf');if(f)f.addEventListener('submit',function(e){e.preventDefault();var d=Object.fromEntries(new FormData(f));if(d._honey)return;if(!d.name||!d.email)return;
  d.page='digitallineup.com'+location.pathname;d.service='Blog: '+document.title;var b=f.querySelector('button');b.disabled=true;b.textContent='Sending...';
  fetch('"""+LEADS_URL+"""',{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(d)}).then(function(){f.classList.add('sent');}).catch(function(){b.disabled=false;b.textContent='Send';});});
})();</script>"""

ICON_CAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>'
ICON_CLK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'


def page(title, desc, path, body, ld, og_image, og_type='website', js='', nav_on='blog'):
    url = SITE + path
    ldtag = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}"><meta property="og:url" content="{url}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF6EF"><link rel="icon" href="/img/mark-dark.svg"><link rel="alternate" type="application/rss+xml" title="Digital Lineup blog" href="/blog/feed.xml">
{ldtag}<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a href="/" aria-label="Digital Lineup home"><img src="/logo-dark.svg" alt="Digital Lineup" width="98" height="36"></a>
<nav><a class="hide-s" href="/#services">Services</a><a class="hide-s" href="/work/">Work</a><a class="on" href="/blog/">Blog</a><a class="go" href="/#contact">Let's talk</a></nav></div></header>
<main>{body}</main>
<footer class="foot"><div class="wrap"><span>&copy; {datetime.date.today().year} Digital Lineup. Office #1, Basement, Al Shifa Hospital, Masoom Shah Rd, Multan, Pakistan.</span>
<span><a href="mailto:hello@digitallineup.com">hello@digitallineup.com</a> &middot; <a href="https://wa.me/923009590042">WhatsApp +92 300 959 0042</a> &middot; <a href="https://www.instagram.com/digitallineup_/">Instagram</a> &middot; <a href="https://www.linkedin.com/company/digital-lineup-agency">LinkedIn</a> &middot; <a href="https://www.facebook.com/digitallineup1">Facebook</a> &middot; <a href="https://www.youtube.com/@DigitalLineup">YouTube</a></span></div></footer>
{js}</body></html>
"""


def nice_date(d):
    return datetime.date.fromisoformat(d).strftime('%-d %B %Y')


def card(p):
    return f"""<a class="card" href="/blog/{p['slug']}/" data-tags="{esc('|'.join(p['tags']))}"><div class="im"><img src="{p['cover']}" alt="{esc(p.get('cover_alt', ''))}" loading="lazy" width="1200" height="675"></div>
<div class="d"><span class="dot"></span>{nice_date(p['date'])}</div><h2>{esc(p['title'])}</h2><p>{esc(p['description'])}</p></a>"""


def quick_answers(body_html):
    """Turn the '## Quick answers' section into boxed Q&As and return FAQ schema items."""
    m = re.search(r'(<h2 id="quick-answers">.*?</h2>)(.*?)(?=<h2|$)', body_html, re.S)
    if not m:
        return body_html, []
    sect = m.group(2)
    parts = re.split(r'(?=<h3)', sect)
    faq, out = [], ''
    for part in parts:
        q = re.match(r'<h3[^>]*>(.*?)</h3>(.*)', part, re.S)
        if not q:
            out += part
            continue
        out += f'<div class="qa"><h3>{q.group(1)}</h3>{q.group(2).strip()}</div>'
        faq.append({'@type': 'Question', 'name': html.unescape(re.sub('<[^>]+>', '', q.group(1))),
                    'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', q.group(2)))).strip()}})
    return body_html[:m.start(2)] + out + body_html[m.end(2):], faq


def build():
    posts = [p for p in (read_post(f) for f in sorted(glob.glob(os.path.join(ROOT, 'blog/posts/*.md'))) if not f.endswith('README.md')) if p]
    posts.sort(key=lambda p: p['date'], reverse=True)
    md = markdown.Markdown(extensions=['tables', 'toc', 'sane_lists', 'md_in_html'])
    for p in posts:
        md.reset()
        body_html = md.convert(p['body_md'])
        body_html, faq = quick_answers(body_html)
        toc = ''.join(f'<a href="#{t["id"]}">{esc(html.unescape(t["name"]))}</a>' for t in md.toc_tokens)
        url = f"{SITE}/blog/{p['slug']}/"
        cover_abs = SITE + p['cover'] if p['cover'].startswith('/') else p['cover']
        others = [o for o in posts if o['slug'] != p['slug']][:3]
        more = ('<section class="more"><div class="wrap"><h2>Keep reading</h2><div class="grid">' + ''.join(card(o) for o in others) + '</div></div></section>') if others else ''
        if p.get('cta') == 'installers':
            cta_html = '<div class="cta rv"><h2>Run an installation business in Australia?</h2><p>See the full numbers and how we work with installers, or email us your website for a free 2-minute video on what we would fix first.</p><div class="row"><a class="btn" href="/installers/">See how we work with installers</a><a class="btn ghost" href="mailto:hello@digitallineup.com?subject=Free%202-minute%20video">Email us your website</a></div></div>'
            side_h, side_p = 'More leads from the ads you already run.', 'Meta ads, install reels and landing pages for Australian installers.'
        else:
            cta_html = '<div class="cta rv"><h2>Want this for your brand?</h2><p>Video, brand identity, Meta ads and social media, made in-house by our team in Multan. Tell us what you are building.</p><div class="row"><a class="btn" href="/#contact">Start a project</a><a class="btn ghost" href="https://wa.me/923009590042">WhatsApp us</a></div></div>'
            side_h, side_p = 'Your brand should look as good as it is.', 'Video, branding, Meta ads and social, made in-house in Multan.'
        side_card = f"""<div class="scard"><span class="rb">Google <i>&#9733;&#9733;&#9733;&#9733;&#9733;</i> 5.0</span><h3>{side_h}</h3><p>{side_p}</p>
<form id="sf" novalidate><input name="name" placeholder="Your name" autocomplete="name" required><input name="email" type="email" placeholder="Work email" autocomplete="email" required><input class="hp" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true"><button class="btn" type="submit">Start your project</button></form>
<div class="ok" role="status">Thanks. Our team will get back to you shortly.</div><p class="note">16 five-star reviews on Google</p></div>"""
        body = f"""<section class="ah"><div class="wrap"><div>
<nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a><span>&rsaquo;</span><a href="/blog/">Blog</a><span>&rsaquo;</span><span>{esc(p['title'])}</span></nav>
<h1>{esc(p['title'])}</h1>
<div class="meta"><span>{ICON_CAL}<time datetime="{p['date']}">{nice_date(p['date'])}</time></span><span>{ICON_CLK}{p['minutes']} min read</span></div>
<div class="by"><img src="/img/ali-hannan-founder.jpg" alt="Ali Hannan Siddique" width="44" height="44"><div><b>Ali Hannan Siddique</b><small>Founder, Digital Lineup</small></div></div></div>
<div class="cv"><img src="{p['cover']}" alt="{esc(p.get('cover_alt', ''))}" width="1200" height="675" fetchpriority="high"></div></div></section>
<div class="wrap body"><aside class="side"><div class="stick"><nav class="toc" aria-label="In this article"><b>In this article</b>{toc}</nav>{side_card}</div></aside>
<article class="prose"><details class="mtoc"><summary>In this article</summary><nav class="toc"><b>In this article</b>{toc}</nav></details><div style="height:22px" class="mtoc-gap"></div>
{body_html}{cta_html}
<div class="author"><img src="/img/ali-hannan-founder.jpg" alt="Ali Hannan Siddique" width="64" height="64" loading="lazy"><div><b>Ali Hannan Siddique</b><p>Founder of Digital Lineup, a content production and digital marketing agency in Multan, Pakistan. Four years of brand films, Meta ads, identities and social media for brands in Pakistan and Australia.</p></div></div>
</article></div>{more}"""
        ld = [{'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'], 'description': p['description'],
               'datePublished': p['date'], 'dateModified': p.get('updated', p['date']), 'author': AUTHOR, 'publisher': ORG,
               'image': cover_abs, 'mainEntityOfPage': url, 'url': url, 'keywords': ', '.join(p['tags']), 'inLanguage': 'en'},
              {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                  {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
                  {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE + '/blog/'},
                  {'@type': 'ListItem', 'position': 3, 'name': p['title'], 'item': url}]}]
        if faq:
            ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': faq})
        out = os.path.join(ROOT, 'blog', p['slug'])
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(
            page(p.get('seo_title', p['title']) + ' | Digital Lineup', p['description'], f"/blog/{p['slug']}/", body, ld, cover_abs, 'article', JS_POST))

    tags = []
    for p in posts:
        for t in p['tags']:
            if t not in tags and t != 'Case study':
                tags.append(t)
    chips = '<button class="chip on" data-f="all">All</button>' + ''.join(f'<button class="chip" data-f="{esc(t)}">{esc(t)}</button>' for t in tags[:6])
    body = f"""<section class="bh wrap"><h1><span><i>Notes from the work.</i></span><span><i>Numbers included.</i></span></h1>
<p>Meta ads, content production, branding and social media, written from real campaigns by the Digital Lineup team in Multan, Pakistan.</p></section>
<section class="wrap"><div class="chips">{chips}</div><div class="grid">{''.join(card(p) for p in posts)}</div></section>"""
    ld = [{'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Digital Lineup blog', 'url': SITE + '/blog/', 'publisher': ORG,
           'blogPost': [{'@type': 'BlogPosting', 'headline': p['title'], 'url': f"{SITE}/blog/{p['slug']}/", 'datePublished': p['date']} for p in posts]}]
    open(os.path.join(ROOT, 'blog', 'index.html'), 'w', encoding='utf-8').write(
        page('Blog: Meta Ads, Content Production and Branding Insights | Digital Lineup',
             'Practical, numbers-first articles on Meta ads, content production, branding and social media from Digital Lineup, an agency in Multan, Pakistan.',
             '/blog/', body, ld, SITE + '/og.jpg', 'website', JS_INDEX))

    items = ''.join(f"<item><title>{esc(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link><guid>{SITE}/blog/{p['slug']}/</guid><pubDate>{datetime.date.fromisoformat(p['date']).strftime('%a, %d %b %Y 09:00:00 +0500')}</pubDate><description>{esc(p['description'])}</description></item>" for p in posts)
    open(os.path.join(ROOT, 'blog', 'feed.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Digital Lineup blog</title><link>{SITE}/blog/</link><description>Notes from the work.</description>{items}</channel></rss>\n')

    today = datetime.date.today().isoformat()
    urls = [('/', today, '1.0'), ('/work/', today, '0.8'), ('/installers/', today, '0.8'), ('/blog/', today, '0.8')]
    urls += [('/work/' + os.path.basename(f), today, '0.6') for f in sorted(glob.glob(os.path.join(ROOT, 'work/*.html'))) if not f.endswith('index.html')]
    urls += [(f"/blog/{p['slug']}/", p.get('updated', p['date']), '0.7') for p in posts]
    sm = ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>' for u, d, pr in urls)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')

    intro = open(os.path.join(ROOT, 'tools', 'llms-intro.md'), encoding='utf-8').read().rstrip()
    arts = '\n'.join(f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['description']}" for p in posts)
    open(os.path.join(ROOT, 'llms.txt'), 'w', encoding='utf-8').write(intro + '\n\n## Articles\n\n' + arts + '\n')
    print(f'built {len(posts)} posts, {len(urls)} sitemap urls')


if __name__ == '__main__':
    build()
