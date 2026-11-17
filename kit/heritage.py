#!/usr/bin/env python3
"""Heritage concert-poster template (Hatch Show / letterpress / tour admat cues).
Usage: python3 heritage.py specs.json outdir   (same spec fields as render.py)"""
import json, sys, os, datetime
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import uri, ff, ribbon_text, A

PAPER = '#EDE3CC'
ACTS = {
  'band':   dict(logo='ink-jatp.png', logo_w=470, photo='band-field.jpg', frac=.78, pos='50% 0%', ink='#1C1A17', accent='#B0281F',
                 handle='@juniorandthepush', site='juniorandthepush.com', photo_h=430),
  'lite':   dict(logo='ink-pushlite.png', logo_w=500, photo='pushlite-duo3.jpg', frac=1.0, pos='50% 50%', ink='#152540', accent='#B8862B',
                 handle='@pushlitemusic', site='lite.juniorandthepush.com', photo_h=470),
  'junior': dict(logo='ink-junior.png', logo_w=300, photo='junior-acoustic.jpg', frac=1.0, pos='50% 50%', ink='#1C1A17', accent='#B8862B',
                 handle='@juniorguthriemusic', site='juniorguthrie.com', photo_h=450),
}
STATES = {'PA': 'PENNSYLVANIA', 'WV': 'WEST VIRGINIA', 'OH': 'OHIO', 'MD': 'MARYLAND', 'NY': 'NEW YORK'}

GRAIN = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .35 0 0 0 0 .28 0 0 0 0 .18 0 0 0 .5 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")
BLOTCH = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1080'>"
          "<filter id='b'><feTurbulence type='fractalNoise' baseFrequency='.006' numOctaves='4' seed='7'/>"
          "<feColorMatrix values='0 0 0 0 .55 0 0 0 0 .42 0 0 0 0 .25 0 0 0 .45 -.05'/></filter>"
          "<rect width='100%' height='100%' filter='url(%23b)'/></svg>")

def photo_palette(path, n=3):
    from PIL import Image
    import colorsys
    p = path if os.path.isabs(path) else os.path.join(A, path)
    im = Image.open(p).convert('RGB'); im.thumbnail((200, 200))
    q = im.quantize(8).convert('RGB'); cnt = sorted(q.getcolors(99999), reverse=True)
    out = []
    for c, rgb in cnt:
        h, l, sat = colorsys.rgb_to_hls(*[v / 255 for v in rgb])
        if .12 < l < .75:
            r2, g2, b2 = colorsys.hls_to_rgb(h, min(.55, max(.38, l)), min(1, sat * 1.8 + .15))
            out.append((int(r2 * 255), int(g2 * 255), int(b2 * 255)))
    return (out or [rgb for _, rgb in cnt])[:n]

def distress(path):
    layers = []
    for i, (r, g, b) in enumerate(photo_palette(path)):
        fr, fg, fb = r / 255, g / 255, b / 255
        svg = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920'>"
               f"<filter id='d'><feTurbulence type='fractalNoise' baseFrequency='{[.009,.02,.05][i%3]}' numOctaves='4' seed='{11+i*17}'/>"
               f"<feColorMatrix values='0 0 0 0 {fr:.3f} 0 0 0 0 {fg:.3f} 0 0 0 0 {fb:.3f} 0 0 0 {[3.2,3.6,4.2][i%3]} {[-1.75,-2.0,-2.45][i%3]}'/></filter>"
               "<rect width='100%' height='100%' filter='url(%23d)'/></svg>")
        layers.append(f'<div class="dz" style="background:url(&quot;{svg}&quot;);background-size:cover;opacity:{[.20,.15,.13][i%3]}"></div>')
    return ''.join(layers)

def _b64(im, fmt='JPEG'):
    import io, base64
    b = io.BytesIO(); im.save(b, fmt, **({'quality': 90} if fmt == 'JPEG' else {}))
    return f"data:image/{'jpeg' if fmt == 'JPEG' else 'png'};base64," + base64.b64encode(b.getvalue()).decode()

def frame_photo(photo, pw, ph, frac=.85, style='layers'):
    """Auto-frame on the people (from the person matte) so nobody is ever cropped, then build two layers:
    a soft faded background and the people with a soft aura that only dissolves at the very bottom."""
    import numpy as np
    from PIL import Image, ImageOps, ImageFilter
    from scipy import ndimage
    from matte import matte
    src = Image.open(os.path.join(A, photo)).convert('RGB'); W, H = src.size
    rng_g = np.random.default_rng(9)
    m = np.asarray(Image.open(matte(photo)).convert('L').resize((W, H))) > 128
    m = ndimage.binary_closing(m, iterations=6); m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m); sizes = ndimage.sum(m, lab, range(1, n + 1))
    keep = [i + 1 for i, s_ in enumerate(sizes) if s_ > .004 * W * H]; m = np.isin(lab, keep)
    ys, xs = np.where(m); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    bw, bh = x1 - x0, y1 - y0; r = pw / ph
    h = frac * bh / .82; w = max(bw * 1.20, h * r); h = w / r            # 12% top+side room, bottom fade zone
    cx = (x0 + x1) / 2; left = cx - w / 2; top = y0 - .07 * h
    if style == 'torn':          # a torn print can't extend past the real photo: clamp, narrow the print if needed
        # guaranteed room: 15% each side and 17% over the tallest head, measured INSIDE the tear
        w = bw / .70
        h = max(frac * bh / .76, min(w / r, H)); w = max(w, min(h * r, W))
        cx = (x0 + x1) / 2; left = cx - w / 2; top = y0 - .17 * h
        if left < 0 and left + w < W: left = min(0, W - w) if w <= W else left   # use real photo before padding
        if left + w > W and left > 0: left = max(W - w, 0) if w <= W else left
        left = min(left, x0 - .15 * w); left = max(left, x1 + .15 * w - w)
        if top + h > H: top = max(H - h, min(top, 0)) if h <= H else top   # prefer real photo at the bottom too
        if top < 0: h = min(h + top, H); top = 0                           # never invent sky: print starts where the photo starts
        h = min(h, H - top)
    # pad source by mirroring when the frame runs past the photo
    pad = int(max(0, -left, -top, left + w - W, top + h - H)) + 2
    big = ImageOps.expand(src, pad); mb = ImageOps.expand(Image.fromarray((m * 255).astype('uint8')), pad)
    if pad:
        a_ = np.asarray(src); big = np.pad(a_, ((pad, pad), (pad, pad), (0, 0)), mode='edge')
        if style == 'torn':      # extend the scene naturally (inpaint) instead of streaky edge pixels
            import cv2
            hole = np.ones(big.shape[:2], np.uint8) * 255; hole[pad:pad + H, pad:pad + W] = 0
            k = 4; small = cv2.resize(big, (big.shape[1] // k, big.shape[0] // k), interpolation=cv2.INTER_AREA)
            hs = cv2.resize(hole, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
            fill = cv2.inpaint(small, cv2.dilate(hs, np.ones((3, 3), np.uint8)), 12, cv2.INPAINT_TELEA)
            fill = cv2.GaussianBlur(cv2.resize(fill, (big.shape[1], big.shape[0]), interpolation=cv2.INTER_CUBIC), (0, 0), 6)
            fill = np.clip(fill.astype(float) + rng_g.normal(0, 6, fill.shape), 0, 255).astype(np.uint8)
            feather = cv2.GaussianBlur(hole.astype(float) / 255, (0, 0), 10)[..., None]
            big = (big * (1 - feather) + fill * feather).astype(np.uint8)
        big = Image.fromarray(big)
    inside = ImageOps.expand(Image.new('L', (W, H), 255), pad)          # padded area = bare paper
    box = tuple(int(v) for v in (left + pad, top + pad, left + pad + w, top + pad + h))
    sc = min(pw / w, ph / h) if style == 'torn' else pw / w
    OW, OH = int(w * sc * 1.5), int(h * sc * 1.5) if style == 'torn' else int(ph * 1.5)
    img = big.crop(box).resize((OW, OH), Image.LANCZOS)
    # brighten: auto levels, lift shadows (gamma), touch more pop
    from PIL import ImageEnhance
    img = ImageOps.autocontrast(img, cutoff=(0.5, 0.3))
    lut = [int(255 * (i / 255) ** 0.78) for i in range(256)]; img = img.point(lut * 3)
    img = ImageEnhance.Brightness(img).enhance(1.06); img = ImageEnhance.Color(img).enhance(1.08)
    mt = mb.crop(box).resize((OW, OH), Image.LANCZOS)
    ins = np.asarray(inside.crop(box).resize((OW, OH)).filter(ImageFilter.GaussianBlur(OW * .05)), float) / 255
    yy = np.linspace(0, 1, OH)[:, None]; xx = np.linspace(0, 1, OW)[None, :]
    def ramp(d, wd): t = np.clip(d / wd, 0, 1); return t * t * (3 - 2 * t)
    def with_alpha(im, a): o = im.convert('RGBA'); o.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype('uint8'))); return o
    rng = np.random.default_rng(5)
    if style == 'bleed':      # edge to edge between the frame lines, long fade only at the bottom
        a = ramp(yy, .05) * ramp(1 - yy, .30) * ins
        return _b64(with_alpha(img, a), 'PNG'), None, (OW / 1.5, OH / 1.5)
    if style == 'torn':       # photo torn out and laid on the poster: rough edges, thin paper lip
        def rough(n, amp):
            v = np.cumsum(rng.normal(0, 1, n)); v = (v - np.linspace(v[0], v[-1], n)); v = v / (np.abs(v).max() + 1e-6)
            return amp * v + amp * .35 * rng.normal(0, 1, n)
        mx, my = .03, .04
        L = mx + rough(OH, .012)[:, None] * 1; R = 1 - mx + rough(OH, .012)[:, None]
        T = my + rough(OW, .02)[None, :]; B = 1 - my + rough(OW, .02)[None, :]
        inside_ = (xx > L) & (xx < R) & (yy > T) & (yy < B)
        lip = (xx > L - .006) & (xx < R + .006) & (yy > T - .009) & (yy < B + .009)
        a = inside_.astype(float)
        o = with_alpha(img, a)
        paper = Image.new('RGBA', (OW, OH), (246, 240, 226, 0)); paper.putalpha(Image.fromarray((lip * 235).astype('uint8')))
        shadow = Image.new('RGBA', (OW, OH), (40, 28, 12, 0)); sh = Image.fromarray((lip * 110).astype('uint8')).filter(ImageFilter.GaussianBlur(9))
        shadow.putalpha(ImageOps.expand(sh, (6, 8, 0, 0)).crop((0, 0, OW, OH)))
        out = Image.alpha_composite(Image.alpha_composite(shadow, paper), o)
        return _b64(out, 'PNG'), None, (OW / 1.5, OH / 1.5)
    if style == 'halftone':   # photo breaks into printed halftone dots as it reaches the paper
        base = ramp(xx, .16) * ramp(1 - xx, .16) * ramp(yy, .12) * ramp(1 - yy, .26)
        cell = 9; gy, gx = np.mgrid[0:OH, 0:OW]
        u = (gx + gy) / np.sqrt(2) % cell - cell / 2; v = (gx - gy) / np.sqrt(2) % cell - cell / 2   # 45-degree screen
        dist = np.sqrt(u * u + v * v) / (cell * .7071)
        dots = (dist < np.sqrt(np.clip(base, 0, 1)) * 1.02).astype(float)
        a = np.where(base > .985, 1, dots)
        return _b64(with_alpha(img, a), 'PNG'), None, (OW / 1.5, OH / 1.5)
    # people layer: matte grown into a soft aura, dissolving only over the last part of the frame
    aura = mt.filter(ImageFilter.MaxFilter(int(OW * .008) | 1)).filter(ImageFilter.GaussianBlur(OW * .012))
    yy = np.linspace(0, 1, OH)[:, None]; xx = np.linspace(0, 1, OW)[None, :]
    def ramp(d, wd): t = np.clip(d / wd, 0, 1); return t * t * (3 - 2 * t)
    bottom = ramp(1 - yy, .20) * ramp(xx, .03) * ramp(1 - xx, .03) * ramp(yy, .03)
    fg = np.clip(np.asarray(aura, float) / 255 * 1.25, 0, 1) * bottom
    # background layer: very wide, soft feather everywhere
    bg = ramp(xx, .26) * ramp(1 - xx, .26) * ramp(yy, .22) * ramp(1 - yy, .30) * ins
    def with_alpha(im, a): o = im.convert('RGBA'); o.putalpha(Image.fromarray((a * 255).astype('uint8'))); return o
    return _b64(with_alpha(img, bg), 'PNG'), _b64(with_alpha(img, fg), 'PNG'), (OW / 1.5, OH / 1.5)

def html(s):
    a = ACTS[s['act']]; story = s.get('format') == 'story'
    W, H = 1080, (1920 if story else 1350)
    dt = datetime.datetime.strptime(s['date'] + ' ' + s['time'], '%Y-%m-%d %H:%M')
    count = s.get('headline') or ribbon_text(s['step'], dt.hour)
    tstr = dt.strftime('%-I:%M %p').replace(':00 ', ' ')
    town, st = (s['town'].split(',') + [''])[:2]; st = st.strip().upper()
    place = f"{town.strip().upper()}, {STATES.get(st, st)}"
    photo = s.get('photo') or a['photo']
    pos = s.get('photo_pos') or (a.get('story_pos') if story else None) or a['pos']
    pw = s.get('photo_w', 960)
    fb = s.get('fade_bottom', 86); fy = s.get('fade_radial_y', 72)
    vl = s.get('venue_logo')
    venue = (f"<img class='vlogo' src='{uri(vl)}'>" if vl else f"<div class='vname'>{s['venue'].upper()}</div>")
    tag = f"<div class='tag'>&#9733; {s['tag'].upper()} &#9733;</div>" if s.get('tag') else ''
    sample = "<div class='sample'>SAMPLE LAYOUT</div>" if s.get('sample') else ''
    ph = a['photo_h'] + (a.get('story_extra', 300) if story else 0) - (50 if s.get('tag') else 0)
    top = 230 if story else 96
    if not story and not s.get('shows') and not s.get('dates'): ph -= 85 if vl else 40
    multi = ''
    if s.get('dates'):
        ph = s.get('photo_h', 300 if not story else 520)
        rows = ''.join(f"<div class='drow'><span class='dw'>{d['when']}</span><span class='dv'>{d['venue'].upper()}</span><span class='dt'>{d['town'].upper()}</span></div>" for d in s['dates'])
        book = f"<div class='book'>{s['booking']}</div>" if s.get('booking') else ''
        multi = f"<div class='dlist'>{rows}</div>{book}"
    if s.get('shows'):
        ph -= 200 if not story else 40
        cols = []
        for sh in s['shows']:
            d2 = datetime.datetime.strptime(sh['date'] + ' ' + sh['time'], '%Y-%m-%d %H:%M')
            t2 = d2.strftime('%-I:%M').replace(':00', '') + ('–' + sh['end'] if sh.get('end') else '') + ' ' + d2.strftime('%p')
            vl2 = sh.get('venue_logo')
            v2 = f"<img class='mlogo' src='{uri(vl2)}'>" if vl2 else f"<div class='mname'>{sh['venue'].upper()}</div>"
            tw, st2 = (sh['town'].split(',') + [''])[:2]
            cols.append(f"<div class='mcol'><div class='mday'>{d2.strftime('%a').upper()} &middot; {d2.strftime('%b').upper()} {d2.day}</div>{v2}"
                        f"<div class='mtown'>{tw.strip().upper()}, {st2.strip().upper()}</div><div class='mtime'>{t2}</div></div>")
        follow = f"<div class='follow'>FOLLOW <b>{s['follow']}</b></div>" if s.get('follow') else ''
        multi = f"<div class='at'>live at</div><div class='multi'>{('<div class=msep></div>').join(cols)}</div>{follow}"
    style = s.get('fade_style', 'torn')
    if style == 'bleed': pw = 1000
    bg_uri, fg_uri, (pw, ph) = frame_photo(photo, pw, ph, s.get('frac', a.get('frac', .85)), style)
    pw, ph = int(pw), int(ph)
    faces = ''.join(f"@font-face{{font-family:'{n}';src:url({ff(f, w)})}}" for n, f, w in [
        ('slab', 'alfa-slab-one', 400), ('goth', 'league-gothic', 400), ('cond', 'barlow-condensed', 600),
        ('condb', 'barlow-condensed', 800), ('scr', 'mr-dafoe', 400)])
    stars = ' '.join(['&#9733;'] * 14)
    return f"""<!doctype html><html><head><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:{PAPER};position:relative;overflow:hidden;color:{a['ink']}}}
.paper1{{position:absolute;inset:0;background:url("{BLOTCH}");background-size:cover;mix-blend-mode:multiply;opacity:.55}}
.paper2{{position:absolute;inset:0;background:url("{GRAIN}");mix-blend-mode:multiply;opacity:.55}}
.dz{{position:absolute;inset:0;mix-blend-mode:multiply;pointer-events:none}}
.vig{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 55%,rgba(90,60,20,.28) 100%)}}
.frame{{position:absolute;inset:26px;border:6px solid {a['ink']}}}
.frame2{{position:absolute;inset:40px;border:2px solid {a['ink']}}}
.stars{{position:absolute;top:{top-44 if not story else top-60}px;left:0;right:0;text-align:center;font:26px goth;letter-spacing:10px;padding-left:10px;color:{a['accent']}}}
.wrap{{position:absolute;left:60px;right:60px;top:{top}px;bottom:{300 if story else 62}px;display:flex;flex-direction:column;align-items:center}}
.logo{{width:{s.get('logo_w', a['logo_w'])}px}}
.count{{margin-top:10px;display:flex;align-items:center;gap:22px;font:96px/1 goth;letter-spacing:4px;color:{a['accent']};white-space:nowrap}}
.count:before,.count:after{{content:'';width:120px;height:0;border-top:3px solid {a['ink']};border-bottom:3px solid {a['ink']};padding-top:5px}}
.tag{{margin-top:6px;font:40px/1 goth;letter-spacing:5px;white-space:nowrap}}
.photo{{margin-top:6px;position:relative;width:{pw}px;height:{ph}px;flex:none}}
.photo img{{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:multiply}}
.photo .bg{{opacity:.82;filter:saturate(.8) sepia(.15) contrast(.95)}}
.photo .one{{mix-blend-mode:normal;filter:contrast(1.04)}}
.photo .fg{{filter:contrast(1.05) saturate(.95) sepia(.08)}}
.at{{margin-top:2px;position:relative;font:64px/1 scr;color:{a['accent']}}}
.vlogo{{margin-top:4px;max-height:{200 if not story else 250}px;max-width:640px;mix-blend-mode:multiply}}
.vname{{margin-top:6px;font:96px/1 slab;letter-spacing:1px;white-space:nowrap}}
.place{{margin-top:12px;font:46px/1 goth;letter-spacing:7px;white-space:nowrap}}
.daterow{{margin-top:16px;display:flex;align-items:center;gap:22px;white-space:nowrap}}
.dow,.time{{font:44px/1 goth;letter-spacing:4px;padding:8px 0;border-top:3px solid {a['ink']};border-bottom:3px solid {a['ink']}}}
.big{{font:92px/1 slab;color:{a['accent']};letter-spacing:1px}}
.addr{{margin-top:auto;font:26px condb;letter-spacing:3px;text-transform:uppercase;white-space:nowrap}}
.foot{{margin-top:8px;font:25px condb;letter-spacing:3px;white-space:nowrap}}
.foot b{{color:{a['accent']};margin:0 12px}}
.dlist{{margin-top:14px;width:900px}}
.drow{{display:flex;align-items:baseline;gap:18px;padding:{4 if not story else 12}px 6px;border-bottom:2px solid {a['ink']}33;white-space:nowrap}}
.drow:first-child{{border-top:3px solid {a['ink']}}}
.drow:last-child{{border-bottom:3px solid {a['ink']}}}
.dw{{width:250px;font:{33 if not story else 42}px/1 slab;color:{a['accent']}}}
.dv{{flex:1;font:{35 if not story else 44}px/1 goth;letter-spacing:3px}}
.dt{{font:{26 if not story else 30}px/1 condb;letter-spacing:3px}}
.book{{margin-top:auto;font:{44 if not story else 52}px/1 goth;letter-spacing:5px;white-space:nowrap}}
.book b{{color:{a['accent']};font-weight:400}}
.multi{{margin-top:2px;display:flex;align-items:stretch;justify-content:center;gap:30px}}
.mcol{{width:400px;display:flex;flex-direction:column;align-items:center}}
.msep{{width:0;border-left:3px solid {a['ink']};margin:10px 0}}
.mday{{font:56px/1 slab;color:{a['accent']};white-space:nowrap}}
.mlogo{{margin-top:10px;height:{215 if not story else 270}px;max-width:400px;object-fit:contain;mix-blend-mode:multiply}}
.mname{{margin-top:12px;font:46px/1 slab;white-space:nowrap}}
.mtown{{margin-top:12px;font:36px/1 goth;letter-spacing:5px;white-space:nowrap}}
.mtime{{margin-top:8px;font:40px/1 goth;letter-spacing:4px;white-space:nowrap;padding:6px 18px;border-top:3px solid {a['ink']};border-bottom:3px solid {a['ink']}}}
.follow{{margin-top:auto;margin-bottom:auto;padding-top:20px;font:50px/1 goth;letter-spacing:6px;white-space:nowrap}}
.follow b{{color:{a['accent']};font-weight:400}}
.place,.dow,.time,.mtown,.mtime,.dv,.follow,.book,.tag{{-webkit-text-stroke:1.2px currentColor;paint-order:stroke fill}}
.addr,.foot,.dt{{-webkit-text-stroke:.6px currentColor}}
.sample{{position:absolute;top:44%;left:-60px;right:-60px;transform:rotate(-14deg);text-align:center;font:150px goth;color:rgba(176,40,31,.22);letter-spacing:14px}}
</style></head><body>
<div class='paper1'></div><div class='paper2'></div>{distress(photo)}<div class='vig'></div>
<div class='frame'></div><div class='frame2'></div>
<div class='stars'>{stars}</div>
<div class='wrap'>
  <img class='logo' src='{uri(a['logo'])}'>
  <div class='count'>{count}</div>{tag}
  <div class='photo' style='{'margin-left:-20px;margin-right:-20px' if style == 'bleed' else ''}'><img class='{'bg' if fg_uri else 'one'}' src='{bg_uri}'>{f'<img class=fg src={fg_uri}>' if fg_uri else ''}</div>
  {multi or f'''<div class='at'>live at</div>
  {venue}
  <div class='place'>{place}</div>
  <div class='daterow'><span class='dow'>{dt.strftime('%A').upper()}</span><span class='big'>{dt.strftime('%b').upper()} {dt.day}</span><span class='time'>{tstr}</span></div>
  <div class='addr'>{s['address']}</div>'''}
  <div class='foot' style='{"margin-top:0" if multi else ""}'>{a['site']}<b>&#9733;</b>{a['handle']}</div>
</div>{sample}
</body></html>""", W, H

def main():
    specs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for s in specs:
            h, W, H = html(s)
            pg = b.new_page(viewport={'width': W, 'height': H}); pg.set_content(h); pg.wait_for_timeout(400)
            over = pg.evaluate("""(()=>{const W=%d,H=%d;return [...document.querySelectorAll('.wrap > *')].filter(e=>{const r=e.getBoundingClientRect();return r.left<50||r.right>W-50||r.bottom>H-50}).map(e=>e.className)})()""" % (W, H))
            pg.screenshot(path=os.path.join(out, s['out'])); pg.close()
            print(s['out'], 'OVERFLOW:' + ','.join(over) if over else 'ok')
        b.close()

if __name__ == '__main__':
    main()
