#!/usr/bin/env python3
"""Push Promo Kit renderer.
Usage: python3 render.py specs.json outdir
Each spec: {act, step, venue, venue_logo (path or null), town, date, time, address,
            photo (path, optional), photo_pos (CSS object-position, optional), out}
act: band | lite | junior
step: announce | 3wk | 10d | tomorrow | tonight
format: feed (1080x1350) | story (1080x1920)
"""
import json, sys, os, base64, mimetypes, datetime
from playwright.sync_api import sync_playwright

KIT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(KIT, 'assets')
F = os.path.join(KIT, 'fonts')

ACTS = {
    'band': dict(logo='t-jatp-logo-silver.png', logo_w=600, photo='band-field.jpg', pos='50% 30%', ptop=110,
                 accent='#E8333A', text='#FFFFFF', handle='@juniorandthepush', site='juniorandthepush.com'),
    'lite': dict(logo='t-pushlite-logo.png', logo_w=560, photo='pushlite-duo2.jpg', pos='50% 0%', ptop=250,
                 accent='#F2B632', text='#FFFFFF', handle='@pushlitemusic', site='lite.juniorandthepush.com'),
    'junior': dict(logo='t-junior-logo.png', logo_w=360, photo='junior-fence.jpg', pos='50% 0%', ptop=300,
                   accent='#E2B547', text='#FFFFFF', handle='@juniorguthriemusic', site='juniorguthrie.com'),
}

def uri(path):
    if not os.path.isabs(path):
        path = os.path.join(A, path)
    mt = mimetypes.guess_type(path)[0] or 'image/png'
    return f'data:{mt};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def font(name, w):
    p = {'bsd': f'{F}/fontsource-big-shoulders-display-5.3.0/files/big-shoulders-display-latin-{w}-normal.woff2',
         'inter': f'{F}/fontsource-inter-5.3.0/files/inter-latin-{w}-normal.woff2'}[name]
    return 'data:font/woff2;base64,' + base64.b64encode(open(p, 'rb').read()).decode()

def ff(name, w=400):
    p = f"{F}/fontsource-{name}-5.3.0/files/{name}-latin-{w}-normal.woff2"
    return 'data:font/woff2;base64,' + base64.b64encode(open(p, 'rb').read()).decode()

# name, weight, size multiplier, letter-spacing, transform
THEMES = {
  'shoulders': dict(count=('big-shoulders-display',900,1.0,'1px'), date=('big-shoulders-display',900,1.0,'1px'),
                    detail=('inter',500,1.0,'0'), foot=('inter',700,1.0,'1px'), script=None),
  'modern':    dict(count=('anton',400,.92,'2px'), date=('anton',400,.86,'1.5px'),
                    detail=('barlow-condensed',500,1.18,'1px'), foot=('barlow-condensed',600,1.2,'2px'), script=('yellowtail',400)),
  'honkytonk': dict(count=('alfa-slab-one',400,.74,'1px'), date=('league-gothic',400,1.16,'2px'),
                    detail=('barlow-condensed',500,1.18,'1px'), foot=('barlow-condensed',600,1.2,'2px'), script=('mr-dafoe',400)),
  'arena':     dict(count=('league-gothic',400,1.28,'3px'), date=('league-gothic',400,1.22,'2px'),
                    detail=('archivo',500,1.0,'0'), foot=('archivo',700,1.0,'1px'), script=('kaushan-script',400)),
}

def ribbon_text(step, hour):
    day = hour < 17
    return {'announce': 'JUST ANNOUNCED', '3wk': '3 WEEKS OUT', '10d': '10 DAYS OUT',
            'tomorrow': 'TOMORROW' if day else 'TOMORROW NIGHT', 'tonight': 'TODAY' if day else 'TONIGHT'}[step]

GRAIN = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .55 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")

def html(s):
    a = ACTS[s['act']]
    fmt = s.get('format', 'feed'); story = fmt == 'story'
    W, H = 1080, (1350 if not story else 1920)
    dt = datetime.datetime.strptime(s['date'] + ' ' + s['time'], '%Y-%m-%d %H:%M')
    rib = ribbon_text(s['step'], dt.hour)
    tstr = dt.strftime('%-I:%M %p').replace(':00 ', ' ')
    dateline = f"{dt.strftime('%A').upper()} &middot; {dt.strftime('%B').upper()} {dt.day} &middot; {tstr}"
    photo = s.get('photo') or a['photo']; pos = s.get('photo_pos') or a['pos']
    vl = s.get('venue_logo')
    venue = (f"<img class='vlogo' src='{uri(vl)}'>" if vl else f"<div class='vname'>{s['venue'].upper()}</div>")
    tag = f"<div class='tag'>{s['tag'].upper()}</div>" if s.get('tag') else ''
    sample = "<div class='sample'>SAMPLE LAYOUT</div>" if s.get('sample') else ''
    top = 230 if story else 56
    ptop = s.get('photo_top', a['ptop']) + (180 if story else 0)
    bottom = 300 if story else 54
    rsize = 118 if len(rib) <= 11 else 96
    T = THEMES[s.get('theme','shoulders')]
    faces=''
    for k in ['count','date','detail','foot']:
        n,w=T[k][0],T[k][1]; faces+=f"@font-face{{font-family:'{k}';src:url({ff(n,w)})}}\n"
    if T['script']: faces+=f"@font-face{{font-family:'scr';src:url({ff(*T['script'])})}}\n"
    faces+=f"@font-face{{font-family:BSD;font-weight:800;src:url({ff('big-shoulders-display',800)})}}@font-face{{font-family:BSD;font-weight:900;src:url({ff('big-shoulders-display',900)})}}"
    cz=T['count'];dz=T['date'];tz=T['detail'];fz=T['foot']
    at_css = (f"font:{int(52)}px scr;letter-spacing:0;color:#fff;text-transform:none" if T['script'] else "font:700 20px detail;letter-spacing:8px;color:rgba(255,255,255,.75)")
    at_txt = 'Live at' if T['script'] else 'LIVE AT'
    return f"""<!doctype html><html><head><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#0B0B0C;overflow:hidden;position:relative;font-family:detail;color:#fff}}
.photo{{position:absolute;left:0;top:{ptop}px;width:{W}px;height:{H-ptop}px;object-fit:cover;object-position:{pos};filter:contrast(1.06) saturate(1.05)}}
.shade{{position:absolute;inset:0;background:
  linear-gradient(180deg,rgba(11,11,12,1) {ptop}px,rgba(11,11,12,0) {ptop+160}px),
  linear-gradient(0deg,rgba(8,8,9,.96) 0%,rgba(8,8,9,.86) {30 if not story else 28}%,rgba(8,8,9,0) {52 if not story else 50}%)}}
.grain{{position:absolute;inset:0;background:url("{GRAIN}");opacity:.12;mix-blend-mode:overlay}}
.logo{{position:absolute;top:{top}px;left:50%;transform:translateX(-50%);width:{a['logo_w']}px;filter:drop-shadow(0 4px 14px rgba(0,0,0,.7))}}
.info{{position:absolute;left:64px;right:64px;bottom:{bottom}px;text-align:center}}
.count{{font:{int(rsize*cz[2])}px/.95 count;color:{a['accent']};letter-spacing:{cz[3]};white-space:nowrap;text-shadow:0 3px 18px rgba(0,0,0,.6)}}
.tag{{margin-top:8px;font:800 40px/1 BSD;letter-spacing:6px;color:#fff;white-space:nowrap}}
.at{{margin:16px auto 10px;display:flex;align-items:center;justify-content:center;gap:18px;{at_css}}}
.at:before,.at:after{{content:'';height:2px;width:90px;background:{a['accent']}}}
.vlogo{{max-height:{196 if not story else 220}px;max-width:620px;filter:drop-shadow(0 4px 14px rgba(0,0,0,.6))}}
.vname{{font:900 104px/1 BSD;color:#fff;letter-spacing:1px;white-space:nowrap}}
.date{{margin-top:18px;font:{int(64*dz[2])}px/1 date;letter-spacing:{dz[3]};color:{a['text']};white-space:nowrap}}
.addr{{margin-top:10px;font:{int(25*tz[2])}px detail;letter-spacing:{tz[3]};color:rgba(255,255,255,.78);white-space:nowrap}}
.foot{{margin-top:22px;font:{int(22*fz[2])}px foot;color:rgba(255,255,255,.62);letter-spacing:{fz[3]};white-space:nowrap}}
.foot b{{color:{a['accent']};margin:0 14px}}
.sample{{position:absolute;top:40%;left:-60px;right:-60px;transform:rotate(-14deg);text-align:center;font:900 150px BSD;color:rgba(255,255,255,.18);letter-spacing:12px}}
</style></head><body>
<img class='photo' src='{uri(photo)}'><div class='shade'></div><div class='grain'></div>
<img class='logo' src='{uri(a['logo'])}'>
<div class='info'>
  <div class='count'>{rib}</div>{tag}
  <div class='at'>{at_txt}</div>
  {venue}
  <div class='date'>{dateline}</div>
  <div class='addr'>{s['address']}</div>
  <div class='foot'>{a['site']}<b>&bull;</b>{a['handle']}</div>
</div>{sample}
</body></html>""", W, H

def main():
    specs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for s in specs:
            h, W, H = html(s)
            pg = b.new_page(viewport={'width': W, 'height': H})
            pg.set_content(h); pg.wait_for_timeout(300)
            # overflow check: any element wider than canvas
            over = pg.evaluate("[...document.querySelectorAll('.info *')].filter(e=>{const r=e.getBoundingClientRect();return r.left<0||r.right>%d}).map(e=>e.className)" % W)
            path = os.path.join(out, s['out']); pg.screenshot(path=path)
            print(path, 'OVERFLOW:' + ','.join(over) if over else 'ok')
            pg.close()
        b.close()

if __name__ == '__main__':
    main()
