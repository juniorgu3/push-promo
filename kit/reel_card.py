#!/usr/bin/env python3
"""Song reel with a designed cover card in the first slot.
Usage: python3 reel_card.py reels.json outdir
Spec: act (band|lite|junior), song (title), artist, clip (file in ../songs/), hook (on-screen hook,
use | for a line break), sub (small line under the hook), optional photo, tagline, out (name without extension).
Makes <out>.mp4 (1080x1920, 30fps, H.264), <out>-cover.jpg (the cover card, for the custom thumbnail)
and <out>-frame.jpg (the main frame) so every crop can be checked.
Cover card is held 0.5 s and the song starts after it (audio delayed 0.5 s to match).
Every key element sits in the band all crops keep: x 90-950, y 430-1310 (also during the push-in)."""
import json, sys, os, subprocess
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import uri, ff
from heritage import frame_photo, GRAIN

KIT = os.path.dirname(os.path.abspath(__file__))
SONGS = os.path.join(KIT, '..', 'songs')
ACTS = {
  'band':   dict(logo='t-jatp-logo-silver.png', bg='#141A24', hot='#C9CED6', ink='#F3EEE3', handle='@juniorandthepush',
                 site='juniorandthepush.com', tagline='ALMOST LEGENDARY', photo='band-field.jpg', frac=.78),
  'lite':   dict(logo='t-pushlite-logo.png', bg='#18202D', hot='#E2A72E', ink='#DADDE2', handle='@pushlitemusic',
                 site='lite.juniorandthepush.com', tagline='JUNIOR & DAVE, SOMETIMES JEFF…', photo='pushlite-duo-wide.jpg', frac=1.0),
  'junior': dict(logo='t-junior-logo.png', bg='#161C27', hot='#D99A1E', ink='#F1EADB', handle='@juniorguthriemusic',
                 site='juniorguthrie.com', tagline='JUNIOR AND THE PUSH FRONTMAN', photo='junior-acoustic.jpg', frac=1.0),
}
ZOOM = 1.03   # slow push-in, centred on the safe band so nothing leaves it

def page(s, kind):
    a = ACTS[s['act']]
    faces = ''.join(f"@font-face{{font-family:'{n}';src:url({ff(f, w)})}}" for n, f, w in [
        ('bsd', 'big-shoulders-display', 900), ('bsd8', 'big-shoulders-display', 800), ('inter', 'inter', 600), ('interb', 'inter', 700)])
    stars = ' '.join(['&#9733;'] * 11)
    common = f"""<!doctype html><html><head><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:{a['bg']};position:relative;overflow:hidden;color:{a['ink']}}}
.g{{position:absolute;inset:0;background:url("{GRAIN}");mix-blend-mode:screen;opacity:.18}}
.band{{position:absolute;left:90px;width:860px;top:450px;height:840px;display:flex;flex-direction:column;align-items:center;justify-content:space-between}}
.stars{{font:26px bsd8;letter-spacing:10px;padding-left:10px;color:{a['hot']}}}
</style></head><body><div class='g'></div>"""
    if kind == 'cover':
        return common + f"""<div class='band' style='justify-content:center;gap:34px'>
  <div class='stars'>{stars}</div>
  <img src='{uri(a['logo'])}' style='max-width:700px;max-height:330px'>
  <div style='font:44px/1.1 bsd8;letter-spacing:6px;color:{a['hot']};text-align:center;white-space:nowrap'>{s.get('tagline', a['tagline'])}</div>
  <div style='width:520px;border-top:4px solid {a['ink']};opacity:.5'></div>
  <div style='font:92px/1 bsd;letter-spacing:2px;text-align:center;white-space:nowrap'>&#9834; {s['song'].upper()}</div>
  <div style='font:30px inter;letter-spacing:1px;text-align:center;white-space:nowrap;opacity:.9'>{s['artist']}</div>
  <div class='stars'>{stars}</div>
</div></body></html>"""
    bg_uri, _, (pw, ph) = frame_photo(s.get('photo') or a['photo'], s.get('photo_w', 780), s.get('photo_h', 420), s.get('frac', a['frac']), 'torn')
    hook = '<br>'.join(s['hook'].split('|'))
    return common + f"""<div class='band'>
  <div style='text-align:center'>
    <div style='font:{s.get('hook_size', 104)}px/.92 bsd;letter-spacing:2px;color:{a['hot']};text-shadow:5px 5px 0 #070B12;white-space:nowrap'>{hook}</div>
    <div style='margin-top:16px;font:36px/1.2 inter;white-space:nowrap'>{s.get('sub', '')}</div>
  </div>
  <img src='{bg_uri}' style='width:{int(pw)}px;height:{int(ph)}px'>
  <div style='text-align:center'>
    <div style='font:64px/1 bsd;letter-spacing:2px;white-space:nowrap'>&#9834; {s['song'].upper()}</div>
    <div style='margin-top:10px;font:30px inter;white-space:nowrap;opacity:.92'>{s['artist']}</div>
    <div style='margin-top:14px;font:30px interb;letter-spacing:1px;white-space:nowrap;color:{a['hot']}'>{a['site']} &#9733; {a['handle']}</div>
  </div>
</div></body></html>"""

def check(pg):
    """Every element inside the band, even at full push-in."""
    return pg.evaluate("""(()=>{const z=%f,cx=540,cy=870,bad=[];
      document.querySelectorAll('.band *').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width)return;
        const L=cx+(r.left-cx)*z,R=cx+(r.right-cx)*z,T=cy+(r.top-cy)*z,B=cy+(r.bottom-cy)*z;
        if(L<90||R>950||T<430||B>1310||e.scrollWidth>e.clientWidth+1)bad.push(e.tagName+':'+(e.textContent||'img').slice(0,24))});return bad})()""" % ZOOM)

def main():
    specs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for s in specs:
            o = os.path.join(out, s['out']); bad = []
            for kind, path in (('cover', o + '-cover.jpg'), ('main', o + '-frame.jpg')):
                pg = b.new_page(viewport={'width': 1080, 'height': 1920}); pg.set_content(page(s, kind)); pg.wait_for_timeout(600)
                bad += check(pg); pg.screenshot(path=path, type='jpeg', quality=94); pg.close()
            clip = os.path.join(SONGS, s['clip'])
            dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', clip]))
            n = int(dur * 30)
            vf = (f"[1:v]scale=2160:3840,zoompan=z='1+{ZOOM - 1:.3f}*on/{n}':x='iw/2-(iw/zoom/2)':y='{870 * 2}-({870 * 2}/zoom)':d={n}:s=1080x1920:fps=30,setsar=1,settb=1/30[m];"
                  f"[0:v]scale=1080:1920,setsar=1,fps=30,settb=1/30[c];[c][m]concat=n=2:v=1:a=0,format=yuv420p[v];"
                  f"[2:a]adelay=500|500,apad,atrim=0:{dur + .5},afade=t=out:st={dur - 0.1:.2f}:d=0.6[a]")
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-t', '0.5', '-i', o + '-cover.jpg', '-i', o + '-frame.jpg',
                            '-i', clip, '-filter_complex', vf, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(dur + .5), o + '.mp4'], check=True)
            print(s['out'], 'OUTSIDE SAFE BAND: ' + ', '.join(bad) if bad else 'ok')
        b.close()

if __name__ == '__main__':
    main()
