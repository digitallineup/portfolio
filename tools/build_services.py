"""Build the rich service pages (/services/<slug>/) from tools/services/*.html.

Each source file starts with a JSON header inside an HTML comment, then the page body.
The shell adds the header with the Services mega-menu, the FAQ, the lead form,
the footer and the JSON-LD (Service, BreadcrumbList, FAQPage).
Shared CSS and JS live in /services/assets/.
"""
import json, pathlib, re, html, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from footer import footer_html, HEAD as FOOT_HEAD, SCRIPTS as FOOT_JS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'tools' / 'services'
SITE = 'https://digitallineup.com'
LEADS_URL = 'https://script.google.com/macros/s/AKfycbzxXJoWIFjgC3vkHPjD8hULkTI7GZZrGoFeuULeVolUNI9fhGg2DP7Lt_m7JjRn-85CKQ/exec'
VER = '20261022b'

I = {  # small line icons for the mega-menu
    'cam': '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    'box': '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
    'film': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 9l5 3-5 3z"/>',
    'star': '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
    'chart': '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/>',
    'pen': '<path d="M12 20l8-8-4-4-8 8-1 5z"/><path d="M14 6l4 4"/>',
    'web': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M7 6.5h.01M10 6.5h.01"/>',
}
# (column, name, one-liner, url, icon). URLs switch to the new pages as each one ships.
MENU = [
    ('Photography', 'Food Photography', 'Restaurants, bakeries, menus', '/services/', 'cam'),
    ('Photography', 'Product Photography', 'Ecommerce, catalogues, ads', '/services/', 'box'),
    ('Production', 'Video Production', 'Brand films, reels, drone', '/services/video-production-multan/', 'film'),
    ('Production', 'Creator Campaigns', 'Influencer films that travel', '/work/apex-solar.html', 'star'),
    ('Growth', 'Meta Ads', 'Leads and sales, tracked', '/services/meta-ads-agency-pakistan/', 'chart'),
    ('Growth', 'Social Media Management', 'Content, posting, community', '/services/social-media-management-pakistan/', 'chat'),
    ('Brand & Web', 'Branding & Identity', 'Logos, systems, brand books', '/services/branding-identity/', 'pen'),
    ('Brand & Web', 'Website Design', 'Fast sites that convert', '/services/website-design-pakistan/', 'web'),
]
BUDGETS = ['PKR 120K to 250K', 'PKR 250K to 500K', 'PKR 500K+', 'Not sure yet']
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def esc(s):
    return html.escape(s, quote=True)


def icon(k):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{I[k]}</svg>'


def mega(cur):
    cols = []
    for col in ['Photography', 'Production', 'Growth', 'Brand & Web']:
        items = ''.join(f'<a class="it{" on" if n == cur else ""}" href="{u}"><i>{icon(ic)}</i><span>{esc(n)}<small>{esc(d)}</small></span></a>'
                        for c, n, d, u, ic in MENU if c == col)
        cols.append(f'<div><p class="mh">{esc(col)}</p>{items}</div>')
    feat = '<a class="feat" href="/services/"><img src="/work/assets/img/lume-07.jpg" alt="" loading="lazy" width="1080" height="1350"><span>Explore all services</span></a>'
    return '<div class="mega" role="region" aria-label="Services">' + ''.join(cols) + feat + '</div>'


def mobile_menu():
    grp = ''
    for col in ['Photography', 'Production', 'Growth', 'Brand & Web']:
        grp += f'<b>{esc(col)}</b>' + ''.join(f'<a href="{u}">{esc(n)}</a>' for c, n, d, u, ic in MENU if c == col)
    return ('<nav class="mnav" aria-label="Mobile menu"><details open><summary>Services <span>+</span></summary><div class="grp">' + grp + '</div></details>'
            '<a href="/work/">Work</a><a href="/about/">About</a><a href="/blog/">Blog</a><a href="#contact">Contact</a>'
            '<div class="mfoot"><a href="https://wa.me/923009590042">WhatsApp +92 300 959 0042</a><a href="mailto:hello@digitallineup.com">hello@digitallineup.com</a><span>Studio in Multan, Pakistan. Working worldwide.</span></div></nav>')


def faq_html(faqs):
    items = ''.join(f'<details><summary>{esc(q)}<i aria-hidden="true"></i></summary><div class="a"><p>{a}</p></div></details>' for q, a in faqs)
    return (f'<section class="s" id="faq"><div class="wrap faq"><div><span class="eyebrow">FAQ</span><h2 class="h-l" data-split style="margin-top:24px">Questions, answered.</h2>'
            f'<p class="lead mut" style="margin-top:22px" data-rv>Anything else, ask us on <a href="https://wa.me/923009590042" style="text-decoration:underline">WhatsApp</a>. A person replies, not a bot.</p></div>'
            f'<div class="qa" data-rv>{items}</div></div></section>')


def form_html(service):
    opts = ''.join(f'<option{" selected" if n == service else ""}>{esc(n)}</option>' for c, n, d, u, ic in MENU) + f'<option{" selected" if service not in [m[1] for m in MENU] else ""}>Something else</option>'
    pills = ''.join(f'<label><input type="radio" name="budget" value="{esc(b)}"><span>{esc(b)}</span></label>' for b in BUDGETS)
    return f'''<section class="contact" id="contact"><div class="wrap g">
<div class="side"><span class="eyebrow" style="background:transparent;color:#fff;border-color:rgba(255,255,255,.25)">Start a project</span>
<h2 class="h-l" data-split style="margin-top:24px">Let&rsquo;s build yours.</h2>
<p data-rv>Tell us a little about the business. Ali or the project lead replies personally with next steps and a time to talk.</p>
<ul data-rv><li><small>WhatsApp</small><a href="https://wa.me/923009590042">+92 300 959 0042</a></li>
<li><small>Email</small><a href="mailto:hello@digitallineup.com">hello@digitallineup.com</a></li>
<li><small>Studio</small><span>Office #1, Basement, Al Shifa Hospital, Masoom Shah Rd, Multan, Pakistan</span></li></ul></div>
<form id="lead" class="lf" novalidate data-url="{LEADS_URL}" data-rv>
<div class="f"><label for="f-name">Your name *</label><input id="f-name" name="name" autocomplete="name" required placeholder="Full name"></div>
<div class="f"><label for="f-email">Email *</label><input id="f-email" name="email" type="email" autocomplete="email" required placeholder="you@company.com"></div>
<div class="f"><label for="f-phone">WhatsApp or phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" placeholder="+92 or your country code"></div>
<div class="f"><label for="f-biz">Company or brand</label><input id="f-biz" name="business" autocomplete="organization" placeholder="Brand name"></div>
<div class="f"><label for="f-country">Country</label><input id="f-country" name="country" autocomplete="country-name" placeholder="Where is the business?"></div>
<div class="f"><label for="f-svc">Service</label><select id="f-svc" name="service">{opts}</select></div>
<div class="f full"><label>Budget</label><div class="pills" role="radiogroup" aria-label="Budget">{pills}</div></div>
<div class="f full"><label for="f-msg">About the project</label><textarea id="f-msg" name="details" placeholder="What do you sell, who buys it, and what do you need first?"></textarea></div>
<input class="hp" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
<p class="err" role="alert"></p>
<div class="sub"><small>We only use your details to reply to this enquiry. See our <a href="/privacy-policy/" style="text-decoration:underline">privacy policy</a>.</small><button class="btn lime" type="submit">Send enquiry {ARROW}</button></div>
<div class="ok" role="status"><b>Got it, thank you.</b>We will reply within one working day. For anything urgent, message us on <a href="https://wa.me/923009590042" style="text-decoration:underline">WhatsApp</a>.</div>
</form></div></section>'''


def footer():
    word = ''
    for i, ch in enumerate('digital lineup.'):
        cls = ' class="g"' if ch == '.' else ''
        word += f'<span style="--i:{i}"{cls}>' + ('&nbsp;' if ch == ' ' else ch) + '</span>' 
    svc = ''.join(f'<a href="{u}">{esc(n)}</a>' for c, n, d, u, ic in MENU)
    return f'''<footer class="ft"><div class="wrap">
<div class="cols"><div><h6>Studio</h6><address>Office #1, Basement, Al Shifa Hospital, Masoom Shah Rd, Ahmad Park Colony, Multan, Pakistan.<br><br>Working with brands worldwide.</address></div>
<div><h6>Services</h6>{svc}</div>
<div><h6>Company</h6><a href="/work/">Work</a><a href="/about/">About</a><a href="/blog/">Blog</a><a href="/contact/">Contact</a><a href="/ali-hannan-siddique/">Founder</a></div>
<div><h6>Follow</h6><a href="https://www.instagram.com/digitallineup_/">Instagram</a><a href="https://www.linkedin.com/company/digital-lineup-agency">LinkedIn</a><a href="https://www.facebook.com/digitallineup1">Facebook</a><a href="https://www.youtube.com/@DigitalLineup">YouTube</a><a href="https://wa.me/923009590042">WhatsApp</a></div></div>
<div class="big" aria-hidden="true">{word}</div>
<div class="base"><span>&copy; <span data-year>2026</span> Digital Lineup. All rights reserved.</span><span><a href="/privacy-policy/">Privacy</a></span></div>
</div></footer>'''


def build_one(src):
    raw = src.read_text(encoding='utf-8')
    m = re.match(r'\s*<!--(.*?)-->\s*', raw, re.S)
    meta = json.loads(m.group(1))
    body = raw[m.end():]
    path, title, desc, svc = meta['path'], meta['seo_title'], meta['description'], meta['service']
    url = SITE + path
    faqs = meta.get('faqs', [])
    ld = [
        {'@context': 'https://schema.org', '@type': 'Service', 'name': meta['title'], 'serviceType': meta.get('service_type', svc),
         'description': desc, 'url': url, 'areaServed': 'Worldwide',
         'provider': {'@type': 'ProfessionalService', 'name': 'Digital Lineup', 'url': SITE + '/',
                      'address': {'@type': 'PostalAddress', 'addressLocality': 'Multan', 'addressCountry': 'PK'}}},
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Services', 'item': SITE + '/services/'}]
            + ([{'@type': 'ListItem', 'position': 3, 'name': meta['title'], 'item': url}] if path != '/services/' else [])},
    ]
    if faqs:
        ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in faqs]})
    ldtag = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
    robots = '<meta name="robots" content="noindex,follow">' if meta.get('noindex') else ''
    og = SITE + meta.get('og_image', '/og-home.jpg')
    down = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>'
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="/img/mark-dark.svg">
<link rel="stylesheet" href="/services/assets/svc.css?v={VER}">{FOOT_HEAD}{ldtag}</head><body>
<a class="sr" href="#main">Skip to content</a>
<div class="cur" aria-hidden="true"><span></span></div>
<header class="hd"><div class="wrap"><a class="logo" href="/" aria-label="Digital Lineup home"><img src="/logo-dark.svg" alt="Digital Lineup" width="98" height="36"></a>
<nav class="main" aria-label="Main"><a href="/about/">About</a><a href="/work/">Work</a><div class="has"><button type="button" aria-expanded="false">Services {down}</button>{mega(svc)}</div><a href="/blog/">Blog</a><a href="/contact/">Contact</a></nav>
<a class="cta" href="#contact">Start a project</a><button class="burger" type="button" aria-label="Menu" aria-expanded="false"><i></i><i></i><i></i></button></div></header>
{mobile_menu()}
<main id="main">{body}{faq_html(faqs) if faqs else ''}{form_html(svc)}</main>
{footer_html('#contact')}
<script src="/services/assets/svc.js?v={VER}" defer></script>{FOOT_JS}</body></html>
'''
    out = ROOT / path.strip('/') / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    return path


def add_to_sitemap(paths):
    sm = ROOT / 'sitemap.xml'
    if not sm.exists():
        return
    x = sm.read_text(encoding='utf-8')
    import datetime
    today = datetime.date.today().isoformat()
    for p in paths:
        loc = f'<loc>{SITE}{p}</loc>'
        if loc not in x:
            x = x.replace('</urlset>', f'<url>{loc}<lastmod>{today}</lastmod><priority>0.8</priority></url></urlset>')
    sm.write_text(x, encoding='utf-8')


if __name__ == '__main__':
    public = []
    for f in sorted(SRC.glob('*.html')):
        path = build_one(f)
        print('built', path)
        meta = json.loads(re.match(r'\s*<!--(.*?)-->', f.read_text(encoding='utf-8'), re.S).group(1))
        if not meta.get('noindex'):
            public.append(path)
    add_to_sitemap(public)
