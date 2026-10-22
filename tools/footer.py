"""One footer for the whole site (matches the homepage footer).
Used by build_blog.py, build_services.py and apply_footer.py (work pages)."""
import datetime

import pathlib as _p
HEAD = '<style id="ft-css">' + (_p.Path(__file__).resolve().parent.parent / 'css/footer.css').read_text(encoding='utf-8').replace('\n', '') + '</style>'
SCRIPTS = '<script src="/js/footer.js?v=20261022b" defer></script>'


def footer_html(contact_href='/contact/'):
    y = datetime.date.today().year
    return f'''<footer class="foot2" id="footer">
  <div class="fmeta wrap">
    <span>&copy; {y} Digital Lineup. Multan, Pakistan.</span>
    <nav class="flinks" aria-label="Site pages"><a href="/services/">Services</a><a href="/work/">Work</a><a href="/blog/">Blog</a><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy/">Privacy</a></nav>
    <a href="#">Back to top &uarr;</a>
  </div>
  <div class="fpit" data-pit role="group" aria-label="Contact links">
    <a class="pill" href="https://wa.me/923009590042" target="_blank" rel="noopener">WhatsApp</a>
    <a class="pill" href="mailto:hello@digitallineup.com">Email</a>
    <a class="pill" href="https://www.instagram.com/digitallineup_/" target="_blank" rel="noopener">Instagram</a>
    <a class="pill" href="https://www.linkedin.com/company/digital-lineup-agency" target="_blank" rel="noopener">LinkedIn</a>
    <a class="pill" href="https://www.facebook.com/digitallineup1" target="_blank" rel="noopener">Facebook</a>
    <a class="pill" href="https://www.youtube.com/@DigitalLineup" target="_blank" rel="noopener">YouTube</a>
    <a class="pill" href="https://www.tiktok.com/@digitallineup" target="_blank" rel="noopener">TikTok</a>
    <a class="pill" href="https://www.google.com/maps?cid=114504805028664053" target="_blank" rel="noopener">Google 5.0</a>
    <a class="pill" href="/services/">Services</a>
    <a class="pill accent" href="{contact_href}">Start something cool</a>
    <a class="pill ghost" href="#">Carrier pigeon</a>
  </div>
  <div class="fword" aria-hidden="true" data-fit><span>DIGITAL LINEUP</span></div>
</footer>'''
