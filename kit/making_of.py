#!/usr/bin/env python3
"""Hatch 'bold' style behind-the-scenes post (no show info). Usage: python3 making_of.py photo.jpg out.jpg"""
import sys, os
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import uri, ff, A
import types; sys.modules.setdefault("matte", types.SimpleNamespace(matte=lambda n: os.path.join(A, "matte-" + os.path.splitext(n)[0] + ".png")))
from heritage import frame_photo, distress, GRAIN, BLOTCH, PAPER
from bold import ribbon_svg
photo, out = sys.argv[1], sys.argv[2]
# hand matte (no rembg here): Junior + Gretsch + Bad Cat stack, in source pixels
W0, H0 = Image.open(os.path.join(A, photo)).size; k = W0 / 1932
m = np.zeros((H0, W0), np.uint8); m[int(205*k):int(1915*k), int(275*k):int(1490*k)] = 255
Image.fromarray(m).save(os.path.join(A, 'matte-' + os.path.splitext(photo)[0] + '.png'))
ink, hot = '#16243F', '#C42A1E'
bg, _, (pw, ph) = frame_photo(photo, 700, 700, 1.0, 'torn', raw=True)
rib = 'data:image/svg+xml;utf8,' + ribbon_svg(940, 104, ink, '#0F1A2E').replace('#', '%23')
faces = ''.join(f"@font-face{{font-family:'{n}';src:url({ff(f, w)})}}" for n, f, w in [
    ('slab', 'alfa-slab-one', 400), ('goth', 'league-gothic', 400), ('condb', 'barlow-condensed', 800)])
html = f"""<!doctype html><html><head><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:{PAPER};position:relative;overflow:hidden;color:{ink}}}
.p1{{position:absolute;inset:0;background:url("{BLOTCH}");background-size:cover;mix-blend-mode:multiply;opacity:.5}}
.p2{{position:absolute;inset:0;background:url("{GRAIN}");mix-blend-mode:multiply;opacity:.5}}
.frame{{position:absolute;inset:22px;border:7px solid {ink}}}
.wrap{{position:absolute;left:40px;right:40px;top:46px;bottom:44px;display:flex;flex-direction:column;align-items:center}}
.stars{{font:24px goth;letter-spacing:9px;padding-left:9px;color:{hot}}}
.logo{{margin-top:6px;max-width:330px;max-height:112px}}
.at{{margin-top:8px;font:46px/1 goth;letter-spacing:8px;padding-left:8px;-webkit-text-stroke:1.2px currentColor;color:{hot};white-space:nowrap}}
.head{{margin-top:4px;font:176px/.84 goth;letter-spacing:3px;color:{hot};text-shadow:6px 6px 0 {ink};white-space:nowrap}}
.photo{{margin-top:12px;width:{int(pw)}px;height:{int(ph)}px;flex:none;position:relative}}
.photo img{{position:absolute;inset:0;width:100%;height:100%}}
.rib{{margin-top:6px;width:940px;height:{104*1.22:.0f}px;background:url("{rib}") no-repeat;background-size:100% 100%;display:flex;justify-content:center;padding-top:14px;flex:none}}
.rib span{{font:56px/1 slab;color:#F6EEDC;white-space:nowrap}} .rib .g{{color:#D99A1E}}
.foot{{margin-top:auto;font:27px condb;letter-spacing:3px;white-space:nowrap}} .foot b{{color:{hot};margin:0 12px}}
</style></head><body><div class='p1'></div><div class='p2'></div>{distress(photo)}<div class='frame'></div>
<div class='wrap'><div class='stars'>{' '.join(['&#9733;']*15)}</div>
<img class='logo' src='{uri('ink-jatp.png')}'>
<div class='at'>&#9733; THE MAKING OF &#9733;</div>
<div class='head'>TWINKLE TOES</div>
<div class='photo'><img src='{bg}'></div>
<div class='rib'><span>COMING THIS <span class='g'>CHRISTMAS</span></span></div>
<div class='foot'>juniorandthepush.com<b>&#9733;</b>@juniorandthepush</div></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = b.new_page(viewport={'width':1080,'height':1350})
    pg.set_content(html); pg.wait_for_timeout(600)
    print(pg.evaluate("""[...document.querySelectorAll('.wrap > *')].map(e=>{const r=e.getBoundingClientRect();return e.className+':'+[r.left,r.top,r.right,r.bottom].map(Math.round)})"""))
    pg.screenshot(path=out, type='jpeg', quality=92); b.close()
