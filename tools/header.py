"""One header for the whole site: logo, main links, Services mega-menu, mobile menu.
Used by build_services.py, build_blog.py and apply_header.py (homepage and work pages)."""
import html

import pathlib as _p
HEAD = '<style id="hd-css">' + (_p.Path(__file__).resolve().parent.parent / 'css/header.css').read_text(encoding='utf-8').replace('\n', '') + '</style>'
SCRIPTS = '<script src="/js/header.js?v=20261022" defer></script>'


def esc(s):
    return html.escape(s, quote=True)


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
    ('Photography', 'Food Photography', 'Restaurants, bakeries, menus', '/services/food-photography/', 'cam'),
    ('Photography', 'Product Photography', 'Ecommerce, catalogues, ads', '/services/product-photography/', 'box'),
    ('Production', 'Video Production', 'Brand films, reels, drone', '/services/video-production/', 'film'),
    ('Production', 'Creator Campaigns', 'Influencer films that travel', '/services/influencer-marketing/', 'star'),
    ('Growth', 'Meta Ads', 'Leads and sales, tracked', '/services/meta-ads/', 'chart'),
    ('Growth', 'Social Media Management', 'Content, posting, community', '/services/social-media-management/', 'chat'),
    ('Brand & Web', 'Branding & Identity', 'Logos, systems, brand books', '/services/branding-identity/', 'pen'),
    ('Brand & Web', 'Website Design', 'Fast sites that convert', '/services/website-design/', 'web'),
]

def icon(k):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{I[k]}</svg>'


def mega(cur):
    cols = []
    for col in ['Photography', 'Production', 'Growth', 'Brand & Web']:
        items = ''.join(f'<a class="it{" on" if n == cur else ""}" href="{u}"><i>{icon(ic)}</i><span>{esc(n)}<small>{esc(d)}</small></span></a>'
                        for c, n, d, u, ic in MENU if c == col)
        cols.append(f'<div><p class="mh">{esc(col)}</p>{items}</div>')
    feat = '<a class="feat" href="/services/"><img src="/work/assets/img/lume-07-640.webp" alt="" loading="lazy" decoding="async" width="640" height="800"><span>Explore all services</span></a>'
    return '<div class="mega" role="region" aria-label="Services">' + ''.join(cols) + feat + '</div>'


def mobile_menu():
    grp = ''
    for col in ['Photography', 'Production', 'Growth', 'Brand & Web']:
        grp += f'<b>{esc(col)}</b>' + ''.join(f'<a href="{u}">{esc(n)}</a>' for c, n, d, u, ic in MENU if c == col)
    return ('<nav class="mnav" aria-label="Mobile menu"><details open><summary>Services <span>+</span></summary><div class="grp">' + grp + '</div></details>'
            '<a href="/">Home</a><a href="/about/">About</a><a href="/work/">Work</a><a href="/blog/">Blog</a><a href="/contact/">Contact</a>'
            '<div class="mfoot"><a href="https://wa.me/923009590042">WhatsApp +92 300 959 0042</a><a href="mailto:hello@digitallineup.com">hello@digitallineup.com</a><span>Studio in Multan, Pakistan. Working worldwide.</span></div></nav>')



DOWN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>'


def header_html(active='', cur_service='', cta_href='/contact/'):
    def a(key, href, label):
        on = ' class="on" aria-current="page"' if key == active else ''
        return f'<a href="{href}"{on}>{label}</a>'
    svc_on = ' on' if active == 'services' else ''
    return (f'<header class="hd"><div class="wrap"><a class="logo" href="/" aria-label="Digital Lineup home"><img src="/logo-dark.svg" alt="Digital Lineup" width="98" height="36"></a>'
            f'<nav class="main" aria-label="Main">{a("home", "/", "Home")}{a("about", "/about/", "About")}{a("work", "/work/", "Work")}'
            f'<div class="has{svc_on}"><button type="button" aria-expanded="false">Services {DOWN}</button>{mega(cur_service)}</div>'
            f'{a("blog", "/blog/", "Blog")}{a("contact", "/contact/", "Contact")}</nav>'
            f'<a class="cta" href="{cta_href}">Start a project</a><button class="burger" type="button" aria-label="Menu" aria-expanded="false"><i></i><i></i><i></i></button></div></header>'
            + mobile_menu())
