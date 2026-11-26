#!/usr/bin/env python3
"""BOLD Hatch Show letterpress poster: huge wood-type headline, big torn-print photo,
ribbon banners (no boxes, no black), venue + date as the heroes.
Usage: python3 bold.py specs.json outdir   (same spec fields as heritage.py)"""
import json, sys, os, datetime
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import uri, ff, ribbon_text, A
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

def trange(d, end=None):
    """'7–10 PM', or '10:30 AM–12 PM' when the show crosses noon/midnight."""
    st = d.strftime('%-I:%M').replace(':00', '')
    if not end: return f"{st} {d.strftime('%p')}"
    eh, _, em = str(end).partition(':'); eh = int(eh) % 12; em = int(em or 0)
    e = d.replace(minute=em, hour=eh)
    while e <= d: e += datetime.timedelta(hours=12)
    en = e.strftime('%-I:%M').replace(':00', '')
    return f"{st}–{en} {e.strftime('%p')}" if e.strftime('%p') == d.strftime('%p') else f"{st} {d.strftime('%p')}–{en} {e.strftime('%p')}"

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
    if s.get('shows'):
        f0 = s['shows'][0]; s = {'headline': 'THIS WEEKEND', 'address': '', 'venue': '', **s, 'date': f0['date'], 'time': f0['time'], 'town': f0['town']}
    W, H = 1080, (1920 if story else 1350)
    dt = datetime.datetime.strptime(s['date'] + ' ' + s['time'], '%Y-%m-%d %H:%M')
    head = (s.get('headline') or ribbon_text(s['step'], dt.hour))
    words = head.split()
    head_html = head; two = False
    tstr = trange(dt, s.get('end'))
    town, st = (s['town'].split(',') + [''])[:2]; st = st.strip().upper()
    place = f"{town.strip().upper()}, {STATES.get(st, st)}"
    photo = s.get('photo') or a['photo']
    vl = s.get('venue_logo')
    vh = s.get('venue_h', 185 if not story else 220)
    if vl and 'venue_h' not in s:                       # tall/square logos get more height so the venue still pops
        from PIL import Image
        lw, lh = Image.open(os.path.join(A, vl)).size
        if lw / lh < 1.6: vh += 60 if not story else 20
    multi = ''
    ph = s.get('photo_h', 375 + (330 if story else 0) - (45 if vh > (185 if not story else 220) else 0))
    if s.get('shows'):
        ph = s.get('photo_h', 330 + (330 if story else 0) + (0 if all(x.get('venue_logo') for x in s['shows']) else 150))
        cols = []
        all_logos = all(sh.get('venue_logo') for sh in s['shows'])   # mixed logo + typed name looks lopsided: type them all
        for sh in s['shows']:
            if not all_logos: sh = {**sh, 'venue_logo': None}
            nsize = min(64 if not story else 72, *[int(410 / (max(len(w) for w in x['venue'].upper().split()) * .72)) for x in s['shows']])
            d2 = datetime.datetime.strptime(sh['date'] + ' ' + sh['time'], '%Y-%m-%d %H:%M')
            t2 = trange(d2, sh.get('end'))
            l2 = sh.get('venue_logo'); f2 = 'mix-blend-mode:multiply'
            if l2 and a.get('dark'):
                alt = l2.replace('.png', '-white.png')
                if os.path.exists(os.path.join(A, alt)): l2 = alt; f2 = ''
                else: f2 = 'filter:invert(1) grayscale(1) brightness(.9)'
            v2 = f"<img class='mlogo' style='{f2}' src='{uri(l2)}'>" if l2 else f"<div class='mname' style='font-size:{nsize}px'>{sh['venue'].upper()}</div>"
            tw, st2 = (sh['town'].split(',') + [''])[:2]
            cols.append(f"<div class='mcol'><div class='mday'>{d2.strftime('%a').upper()} &middot; {d2.strftime('%b').upper()} {d2.day}</div><div class='mv' style='{"" if l2 else "height:auto;margin:14px 0 4px"}'>{v2}</div>"
                        f"<div class='mtown'>{tw.strip().upper()}, {st2.strip().upper()}</div><div class='mrib'><span style='font-size:{min(48, int(330 / (len(t2) * .6)))}px'>{t2}</span></div></div>")
        multi = f"<div class='at'>&#9733; {s.get('at_label', 'LIVE AT')} &#9733;</div><div class='multi'>{'<div class=msep></div>'.join(cols)}</div>" + \
                (f"<div class='follow'>FOLLOW <b>{s['follow']}</b></div>" if s.get('follow') else '')
    bg_uri, fg_uri, (pw, ph) = frame_photo(photo, 1000, ph, s.get('frac', a['frac']), 'torn')
    pw, ph = int(pw), int(ph)
    dark = a.get('dark', False); vfilter = 'mix-blend-mode:multiply'
    if dark and vl:
        from PIL import Image
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
    hs = s.get('head_size', int(min(230 if not story else 245, 1000 / (len(head) * .40))))
    rib = ribbon_svg(1000, 112 if not story else 132, a['rib'], a.get('ribtail', '#0F1A2E'))
    ribu = 'data:image/svg+xml;utf8,' + rib.replace('#', '%23')
    ribm = 'data:image/svg+xml;utf8,' + ribbon_svg(400, 80, a['rib'], a.get('ribtail', '#0F1A2E')).replace('#', '%23')
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
.wrap{{position:absolute;left:40px;right:40px;top:{44 if not story else 250}px;bottom:{44 if not story else 300}px;display:flex;flex-direction:column;align-items:center;{'justify-content:space-between' if story else ''}}}
.stars{{font:24px goth;letter-spacing:9px;padding-left:9px;color:{a['hot']}}}
.logo{{margin-top:6px;max-width:{s.get('logo_w', a['logo_w'])}px;max-height:{125 if not story else 150}px}}
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
.rib span{{font:{72 if not story else 68}px/1 slab;color:{a.get('ribtext', '#F6EEDC')};letter-spacing:1px;white-space:nowrap}}
.rib .g{{color:{gold}}}
.multi{{display:flex;align-items:stretch;justify-content:center;gap:26px;margin-top:4px}}
.mcol{{width:440px;display:flex;flex-direction:column;align-items:center}}
.msep{{width:0;border-left:4px solid {a['ink']};margin:10px 0}}
.mday{{font:58px/1 slab;color:{a['hot']};white-space:nowrap}}
.mv{{margin-top:10px;height:{190 if not story else 260}px;display:flex;align-items:center;justify-content:center}}
.mlogo{{height:100%;max-width:420px;object-fit:contain}}
.mname{{font:{64 if not story else 72}px/1.02 slab;text-align:center;max-width:420px}}
.mtown{{margin-top:10px;font:36px/1 goth;letter-spacing:5px;white-space:nowrap;-webkit-text-stroke:1.1px currentColor}}
.mrib{{margin-top:12px;width:400px;height:96px;background:url("{ribm}") no-repeat;background-size:100% 100%;display:flex;justify-content:center;align-items:center;padding-bottom:16px}}
.mrib span{{font:48px/1 slab;color:{a.get('ribtext', '#F6EEDC')};white-space:nowrap}}
.follow{{margin-top:auto;padding-top:14px;font:46px/1 goth;letter-spacing:6px;white-space:nowrap;-webkit-text-stroke:1.2px currentColor}}
.follow b{{color:{a['hot']};font-weight:400}}
.foot{{margin-top:{'14px' if story else 'auto'};text-align:center;font:27px condb;letter-spacing:3px;white-space:nowrap;text-transform:uppercase}}
.foot2{{margin-top:4px;font:27px condb;letter-spacing:3px;white-space:nowrap}}
.foot2 b{{color:{a['hot']};margin:0 12px}}
</style></head><body>
<div class='paper1'></div><div class='paper2'></div>{'' if dark else distress(photo)}
{'' if dark else "<div class='frame'></div>"}
<div class='wrap'>
  <div class='stars'>{stars}</div>
  <img class='logo' src='{uri(a['logo'])}'>
  <div class='head'>{head_html}</div>
  <div class='photo'><img src='{bg_uri}'></div>
  {multi or f'''<div class='vrow'><div class='at'>&#9733; {s.get('at_label', 'LIVE AT')} &#9733;</div>{venue}</div>
  <div class='place'>{place}</div>
  <div class='rib'><span>{dt.strftime('%a').upper()} <span class='g'>{dt.strftime('%b').upper()} {dt.day}</span> &middot; {tstr}</span></div>
  <div class='foot'>{s['address']}</div>'''}
  <div class='foot2' style='{"margin-top:10px" if multi else ""}'>{a['site']}<b>&#9733;</b>{a['handle']}</div>
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
