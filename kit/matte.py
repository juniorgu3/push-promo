"""Make person mattes (alpha only) for poster photos. Cached as assets/matte-<name>.png"""
import os, sys
os.environ.setdefault('U2NET_HOME', '/root/.rembg/models/u2net_human_seg')
from rembg import remove, new_session
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
def matte(name, model='u2net_human_seg'):
    out = os.path.join(A, 'matte-' + os.path.splitext(name)[0] + '.png')
    if os.path.exists(out): return out
    im = Image.open(os.path.join(A, name)).convert('RGB')
    m = remove(im, session=new_session(model), only_mask=True, post_process_mask=True)
    m.save(out); return out
if __name__ == '__main__':
    for n in sys.argv[1:]: print(matte(n))
