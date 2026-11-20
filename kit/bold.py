#!/usr/bin/env python3
"""BOLD Hatch Show letterpress poster: huge wood-type headline, big torn-print photo,
ribbon banners (no boxes, no black), venue + date as the heroes.
Usage: python3 bold.py specs.json outdir   (same spec fields as heritage.py)"""
import json, sys, os, datetime
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import uri, ff, ribbon_text
from heritage import frame_photo, distress, GRAIN, BLOTCH, STATES, PAPER

ACTS = {
  'band':   dict(logo='ink-jatp.png', logo_w=360, photo='band-field.jpg', frac=.78, ink='#16243F', hot='#C42A1E',
                 rib='#16243F', handle='@juniorandthepush', site='juniorandthepush.com'),
  # Push Lite = its own colors: silver "Push" + gold "LITE" on a deep slate-navy base (dark, never black)
  'lite':   dict(logo='t-pushlite-logo.png', logo_w=430, photo='pushlite-duo-wide.jpg', frac=1.0, ink='#DADDE2', hot='#E2A72E',
                 rib='#E2A72E', ribtail='#A9771A', ribtext='#141C2A', gold='#141C2A', shadow='#070B12', paper='#18202D', dark=True,
                 handle='@pushlitemusic', site='lite.juniorandthepush.com'),
  'junior': dict(logo='ink-junior.png', logo_w=240, photo='junior-acoustic.jpg', frac=1.0, ink='#16243F', hot='#C42A1E',
                 rib='#16243F', gold='#D99A1E', handle='@juniorguthriemusic', site='juniorguthrie.com'),
}

def ribbon_svg(w, h, face, tail):
    """Hatch-style banner: flat face, folded tails with V notches. Pure shapes, no gradients."""
    t = h * .55; d = h * .22  # tail length, fold drop
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h + d}' viewBox='0 0 {w} {h + d}'>"
            f"<polygon points='0,{d} {t},{d} {t},{h + d} 0,{h + d} {t * .45},{d + (h) / 2}' fill='{tail}'/>"
            f"<polygon points='{w},{d} {w - t},{d} {w - t},{h + d} {w},{h + d} {w - t * .45},{d + h / 2}' fill='{tail}'/>"
            f"<polygon points='{t},{h} {t + d * 1.1},{h + d} {t + d * 1.1},{h}' fill='#0B1220' opacity='.55'/>"
            f"<polygon points='{w - t},{h} {w - t - d * 1.1},{h + d} {w - t - d * 1.1},{h}' fill='#0B1220' opacity='.55'/>"
            f"<rect x='{t * .7}' y='0' width='{w - t * 1.4}' height='{h}' fill='{face}'/></svg>")

def html(s):
    a = ACTS[s['act']]; story = s.get('format') == 'story'
    W, H = 1080, (1920 if story else 1350)
    dt = datetime.datetime.strptime(s['date'] + ' ' + s['time'], '%Y-%m-%d %H:%M')
    head = (s.get('headline') or ribbon_text(s['step'], dt.hour))
    words = head.split()
    head_html = head; two = False
    t1 = dt.strftime('%-I:%M').replace(':00', '')
    tstr = (t1 + ('–' + s['end'] if s.get('end') else '') + ' ' + dt.strftime('%p'))
    town, st = (s['town'].split(',') + [''])[:2]; st = st.strip().upper()
    place = f"{town.strip().upper()}, {STATES.get(st, st)}"
    photo = s.get('photo') or a['photo']
    vl = s.get('venue_logo')
    vh = s.get('venue_h', 185 if not story else 290)
    if vl and 'venue_h' not in s:                       # tall/square logos get more height so the venue still pops
        from PIL import Image
        from render import A
        lw, lh = Image.open(os.path.join(A, vl)).size
        if lw / lh < 1.6: vh += 60
    ph = s.get('photo_h', 375 + (330 if story else 0) - (45 if vh > (185 if not story else 290) else 0))
    bg_uri, fg_uri, (pw, ph) = frame_photo(photo, 1000, ph, s.get('frac', a['frac']), 'torn')
    pw, ph = int(pw), int(ph)
    dark = a.get('dark', False); vfilter = 'mix-blend-mode:multiply'
    if dark and vl:
        from PIL import Image
        from render import A
        import numpy as np
        alt = vl.replace('.png', '-white.png')
        if os.path.exists(os.path.join(A, alt)): vl = alt; vfilter = ''
        else:
            px = np.asarray(Image.open(os.path.join(A, vl)).convert('RGBA'), float)
            op = px[..., 3] > 128
            lum = (px[..., :3][op] @ [.299, .587, .114]).mean() if op.any() else 255
            vfilter = 'filter:invert(1) grayscale(1) brightness(.9)' if lum < 110 else ''
    venue = (f"<img class='vlogo' src='{uri(vl)}'>" if vl else f"<div class='vname'>{s['venue'].upper()}</div>")
    gold = a.get('gold', a['hot'])
    hs = s.get('head_size', int(min(230, 1000 / (len(head) * .40))))
    rib = ribbon_svg(1000, 112 if not story else 132, a['rib'], a.get('ribtail', '#0F1A2E'))
    ribu = 'data:image/svg+xml;utf8,' + rib.replace('#', '%23')
    faces = ''.join(f"@font-face{{font-family:'{n}';src:url({ff(f, w)})}}" for n, f, w in [
        ('slab', 'alfa-slab-one', 400), ('goth', 'league-gothic', 400), ('condb', 'barlow-condensed', 800),
        ('scr', 'mr-dafoe', 400)])
    stars = ' '.join(['&#9733;'] * 15)
    return f"""<!doctype html><html><head><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:{a.get('paper', PAPER)};position:relative;overflow:hidden;color:{a['ink']}}}
.paper1{{position:absolute;inset:0;background:url("{BLOTCH}");background-size:cover;mix-blend-mode:{'screen' if dark else 'multiply'};opacity:{.22 if dark else .5}}}
.paper2{{position:absolute;inset:0;background:url("{GRAIN}");mix-blend-mode:{'screen' if dark else 'multiply'};opacity:{.35 if dark else .5}}}
.dz{{position:absolute;inset:0;mix-blend-mode:multiply;pointer-events:none}}
.frame{{position:absolute;inset:22px;border:7px solid {a['ink']}}}
.wrap{{position:absolute;left:40px;right:40px;top:{44 if not story else 150}px;bottom:{44 if not story else 230}px;display:flex;flex-direction:column;align-items:center}}
.stars{{font:24px goth;letter-spacing:9px;padding-left:9px;color:{a['hot']}}}
.logo{{margin-top:6px;max-width:{s.get('logo_w', a['logo_w'])}px;max-height:{125 if not story else 190}px}}
.head{{margin-top:{-4 if not two else 2}px;font:{hs}px/.84 goth;letter-spacing:3px;color:{a['hot']};text-align:center;
       text-shadow:6px 6px 0 {a.get('shadow', a['ink'])};white-space:nowrap}}
.photo{{margin-top:{8 if not two else 14}px;position:relative;width:{pw}px;height:{ph}px;flex:none}}
.photo img{{position:absolute;inset:0;width:100%;height:100%}}
.vrow{{margin-top:2px;display:flex;flex-direction:column;align-items:center}}
.at{{font:46px/1 goth;letter-spacing:8px;padding-left:8px;-webkit-text-stroke:1.2px currentColor;color:{a['hot']};margin-bottom:6px;position:relative;z-index:2}}
.vlogo{{max-height:{vh}px;max-width:700px;{vfilter}}}
.vname{{font:110px/1 slab;white-space:nowrap}}
.place{{margin-top:6px;font:48px/1 goth;letter-spacing:8px;white-space:nowrap;-webkit-text-stroke:1.4px currentColor}}
.rib{{margin-top:14px;width:1000px;height:{(112 if not story else 132) * 1.22:.0f}px;background:url("{ribu}") no-repeat;background-size:100% 100%;
      display:flex;align-items:flex-start;justify-content:center;padding-top:{13 if not story else 16}px;flex:none}}
.rib span{{font:{72 if not story else 88}px/1 slab;color:{a.get('ribtext', '#F6EEDC')};letter-spacing:2px;white-space:nowrap}}
.rib .g{{color:{gold}}}
.foot{{margin-top:auto;text-align:center;font:27px condb;letter-spacing:3px;white-space:nowrap;text-transform:uppercase}}
.foot2{{margin-top:4px;font:27px condb;letter-spacing:3px;white-space:nowrap}}
.foot2 b{{color:{a['hot']};margin:0 12px}}
</style></head><body>
<div class='paper1'></div><div class='paper2'></div>{'' if dark else distress(photo)}
<div class='frame'></div>
<div class='wrap'>
  <div class='stars'>{stars}</div>
  <img class='logo' src='{uri(a['logo'])}'>
  <div class='head'>{head_html}</div>
  <div class='photo'><img src='{bg_uri}'></div>
  <div class='vrow'><div class='at'>&#9733; LIVE AT &#9733;</div>{venue}</div>
  <div class='place'>{place}</div>
  <div class='rib'><span>{dt.strftime('%a').upper()} <span class='g'>{dt.strftime('%b').upper()} {dt.day}</span> &middot; {tstr}</span></div>
  <div class='foot'>{s['address']}</div>
  <div class='foot2'>{a['site']}<b>&#9733;</b>{a['handle']}</div>
</div>
</body></html>""", W, H

def main():
    specs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for s in specs:
            h, W, H = html(s)
            pg = b.new_page(viewport={'width': W, 'height': H}); pg.set_content(h); pg.wait_for_timeout(500)
            over = pg.evaluate("""(()=>{const W=%d,H=%d;const w=document.querySelector('.wrap').getBoundingClientRect();
              return [...document.querySelectorAll('.wrap > *')].filter(e=>{const r=e.getBoundingClientRect();return r.left<28||r.right>W-28||r.bottom>w.bottom+1}).map(e=>e.className)})()""" % (W, H))
            pg.screenshot(path=os.path.join(out, s['out']), type='jpeg', quality=92) if s['out'].endswith('.jpg') else pg.screenshot(path=os.path.join(out, s['out']))
            pg.close()
            print(s['out'], 'OVERFLOW:' + ','.join(over) if over else 'ok')
        b.close()

if __name__ == '__main__':
    main()
