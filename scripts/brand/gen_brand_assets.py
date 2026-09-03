"""Generate DevAgent.Dev brand assets for Open WebUI's static directory.

Source: brand-assets/logo-sizes/devagent-icon-master.png (400x400, flat RGB on white).
The symbol-only configuration is the approved form for favicons, app icons and
small spaces (Branding CI §5.1). Colors, proportions and node count are never
altered (§5.5); we only cut the white background and add padding / a white tile
where the guidelines call for a light background under the mark (§5.4).
"""

import base64
import io
import os
import sys
from collections import deque

from PIL import Image, ImageDraw

SRC = os.path.expanduser('~/DevAgent.Dev/brand-assets/logo-sizes/devagent-icon-master.png')
REPO = sys.argv[1] if len(sys.argv) > 1 else '.'
STATIC = os.path.join(REPO, 'static', 'static')
ROOT_STATIC = os.path.join(REPO, 'static')

WHITE = (255, 255, 255, 255)


def cut_background(img: Image.Image, thresh: int = 28) -> Image.Image:
    """Make the outer white background transparent via flood fill from the edges.

    Only white connected to the image border is removed, so the light interior
    'open space' of the D/A mark and the silver nodes are preserved.
    Near-white anti-aliased edge pixels get a proportional alpha for a clean edge.
    """
    img = img.convert('RGBA')
    w, h = img.size
    px = img.load()
    visited = bytearray(w * h)
    q = deque()

    def near_white(p):
        r, g, b, _ = p
        return (255 - r) + (255 - g) + (255 - b) <= thresh * 3

    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))

    while q:
        x, y = q.popleft()
        i = y * w + x
        if visited[i]:
            continue
        visited[i] = 1
        p = px[x, y]
        if not near_white(p):
            continue
        # distance from white drives residual alpha (soft edge)
        d = (255 - p[0]) + (255 - p[1]) + (255 - p[2])
        alpha = 0 if d <= 6 else min(255, int(255 * d / (thresh * 3)))
        px[x, y] = (p[0], p[1], p[2], alpha)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx]:
                q.append((nx, ny))
    return img


def trim(img: Image.Image) -> Image.Image:
    bbox = img.getchannel('A').getbbox()
    return img.crop(bbox)


def place(mark: Image.Image, size: int, padding: float, bg=None, radius: float = 0.0) -> Image.Image:
    """Center `mark` on a size×size canvas with `padding` fraction on each side."""
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    if bg is not None:
        plate = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(plate)
        d.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * radius), fill=bg)
        canvas.alpha_composite(plate)
    inner = int(size * (1 - 2 * padding))
    m = mark.copy()
    m.thumbnail((inner, inner), Image.LANCZOS)
    ox = (size - m.width) // 2
    oy = (size - m.height) // 2
    canvas.alpha_composite(m, (ox, oy))
    return canvas


def save(img: Image.Image, *paths):
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        img.save(p, optimize=True)
        print('wrote', p, img.size)


def main():
    src = Image.open(SRC)
    mark = trim(cut_background(src))
    # Work from a 4x upscaled master so downsampling stays crisp.
    hi = mark.resize((mark.width * 4, mark.height * 4), Image.LANCZOS)

    # Favicons: symbol on white (guidelines: primary background is white). The UI renders
    # these with rounded-full, so a white square becomes a white disc under the mark.
    fav512 = place(hi, 512, 0.14, bg=WHITE)
    save(fav512, os.path.join(STATIC, 'favicon.png'), os.path.join(ROOT_STATIC, 'favicon.png'))
    save(place(hi, 96, 0.12, bg=WHITE), os.path.join(STATIC, 'favicon-96x96.png'))
    save(place(hi, 180, 0.14, bg=WHITE), os.path.join(STATIC, 'apple-touch-icon.png'))

    # Multi-resolution .ico
    ico = place(hi, 256, 0.10, bg=WHITE)
    ico.save(os.path.join(STATIC, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print('wrote', os.path.join(STATIC, 'favicon.ico'))

    # SVG wrapper (same approach upstream used: embedded PNG), keeps the <link rel=icon svg> valid.
    buf = io.BytesIO()
    place(hi, 500, 0.12, bg=WHITE).save(buf, format='PNG', optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="500" height="500" viewBox="0 0 500 500">'
        f'<image width="500" height="500" xlink:href="data:image/png;base64,{b64}"/></svg>'
    )
    with open(os.path.join(STATIC, 'favicon.svg'), 'w') as f:
        f.write(svg)
    print('wrote', os.path.join(STATIC, 'favicon.svg'))

    # PWA icons. `maskable` needs the mark inside the 80% safe zone → 20% padding on white.
    save(place(hi, 500, 0.20, bg=WHITE), os.path.join(STATIC, 'logo.png'))
    save(place(hi, 192, 0.20, bg=WHITE), os.path.join(STATIC, 'web-app-manifest-192x192.png'))
    save(place(hi, 512, 0.20, bg=WHITE), os.path.join(STATIC, 'web-app-manifest-512x512.png'))

    # Splash. Light: transparent mark on the white splash. Dark: the mark on a white
    # rounded plate, since the guidelines require a light background under the
    # symbol and no official reverse/knockout version exists yet (§5.4).
    save(place(hi, 500, 0.06), os.path.join(STATIC, 'splash.png'))
    save(place(hi, 500, 0.20, bg=WHITE, radius=0.22), os.path.join(STATIC, 'splash-dark.png'))

    # Also keep a transparent master mark and the horizontal lockup available for the UI.
    save(place(hi, 512, 0.0), os.path.join(STATIC, 'brand', 'devagent-mark.png'))
    lock = Image.open(os.path.expanduser('~/DevAgent.Dev/brand-assets/logo-sizes/horizontal/devagent-horizontal-1350px.png'))
    lock = trim(cut_background(lock))
    save(lock, os.path.join(STATIC, 'brand', 'devagent-horizontal.png'))


if __name__ == '__main__':
    main()
