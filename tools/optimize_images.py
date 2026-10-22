"""Make every local <img> load fast: WebP copies at a few widths, srcset/sizes, width/height and lazy loading.

- Creates name-<w>.webp next to each local .jpg/.jpeg/.png (once; reused on later runs).
- Rewrites <img> tags in the built HTML: src -> WebP, srcset with all widths, sizes, decoding=async,
  width/height when missing. Images above the fold keep eager loading; the rest get loading="lazy".
- Adds a zero-specificity `:where(img){height:auto}` so width/height attributes never stretch an image.
Safe to run repeatedly. Needs Pillow.
"""
import pathlib, re, html
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIDTHS = [320, 640, 960, 1440]
SKIP_DIRS = {'.git', 'tools', 'v1', 'v2', 'node_modules', '.github'}
GUARD = '<style id="img-guard">:where(img){height:auto}</style>'
_dims = {}


def local_path(src, page):
    if src.startswith(('http:', 'https:', 'data:', '//')):
        return None
    clean = src.split('?')[0].split('#')[0]
    if not re.search(r'\.(jpe?g|png)$', clean, re.I):
        return None
    p = (ROOT / clean.lstrip('/')) if clean.startswith('/') else (page.parent / clean)
    p = p.resolve()
    return p if p.exists() and ROOT in p.parents else None


def variants(img_path):
    """Return [(width, path)] of WebP copies, creating any that are missing."""
    if img_path not in _dims:
        with Image.open(img_path) as im:
            _dims[img_path] = im.size
    w0, h0 = _dims[img_path]
    out = []
    ws = [w for w in WIDTHS if w < w0] + [min(w0, 1920)]
    for w in sorted(set(ws)):
        dst = img_path.with_name(f'{img_path.stem}-{w}.webp')
        if not dst.exists() or dst.stat().st_mtime < img_path.stat().st_mtime:
            with Image.open(img_path) as im:
                im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
                if w < im.width:
                    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                im.save(dst, 'WEBP', quality=78, method=6)
        out.append((w, dst))
    return out


def url_for(target, page, src):
    return '/' + target.relative_to(ROOT).as_posix()


def attr(tag, name):
    m = re.search(r'\s' + name + r'\s*=\s*"([^"]*)"', tag)
    return m.group(1) if m else None


def set_attr(tag, name, value):
    if attr(tag, name) is not None:
        return re.sub(r'(\s' + name + r'\s*=\s*")[^"]*(")', lambda m: m.group(1) + value + m.group(2), tag, count=1)
    return tag[:-1].rstrip('/').rstrip() + f' {name}="{value}">'


def process(page):
    s = orig = page.read_text(encoding='utf-8')
    count = [0]
    seen = [0]

    def fix(m):
        tag = m.group(0)
        if 'data-noopt' in tag:
            return tag
        src = attr(tag, 'src')
        if not src:
            return tag
        p = local_path(html.unescape(src), page)
        if not p:
            return tag
        seen[0] += 1
        vs = variants(p)
        w0, h0 = _dims[p]
        best = next((v for v in vs if v[0] >= 960), vs[-1])
        tag = set_attr(tag, 'src', url_for(best[1], page, src))
        tag = set_attr(tag, 'srcset', ', '.join(f'{url_for(d, page, src)} {w}w' for w, d in vs))
        lazy = attr(tag, 'loading') == 'lazy'
        eager_hint = attr(tag, 'fetchpriority') == 'high'
        if attr(tag, 'sizes') is None:
            tag = set_attr(tag, 'sizes', 'auto, (max-width: 760px) 100vw, 50vw' if lazy else '(max-width: 760px) 60vw, 33vw')
        if attr(tag, 'width') is None and attr(tag, 'height') is None:
            tag = set_attr(tag, 'width', str(w0))
            tag = set_attr(tag, 'height', str(h0))
        if attr(tag, 'decoding') is None:
            tag = set_attr(tag, 'decoding', 'async')
        # anything after the first few images on the page loads lazily
        if not lazy and not eager_hint and seen[0] > 12:
            tag = set_attr(tag, 'loading', 'lazy')
        count[0] += 1
        return tag

    def fix_poster(m):
        tag = m.group(0)
        if 'data-noopt' in tag:
            return tag
        src = attr(tag, 'poster')
        p = local_path(html.unescape(src), page) if src else None
        if not p:
            return tag
        vs = variants(p)
        want = 960 if 'data-poster-big' in tag else 480
        pick = next((v for v in vs if v[0] >= want), vs[-1])
        count[0] += 1
        return set_attr(tag, 'poster', url_for(pick[1], page, src))

    s = re.sub(r'<video\b[^>]*>', fix_poster, s)
    s2 = re.sub(r'<img\b[^>]*>', fix, s)
    if count[0] and GUARD not in s2:
        s2 = re.sub(r'(<head[^>]*>)', r'\1' + GUARD, s2, count=1)
    if s2 != orig:
        page.write_text(s2, encoding='utf-8')
    return count[0]


if __name__ == '__main__':
    total = pages = 0
    for page in sorted(ROOT.rglob('*.html')):
        if any(part in SKIP_DIRS for part in page.relative_to(ROOT).parts):
            continue
        n = process(page)
        if n:
            pages += 1
            total += n
    print(f'optimized {total} images on {pages} pages')
