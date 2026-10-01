# Stylized water textures (tileable PNGs) generated with numpy inside Blender.
#  agua_linhas.png  : white caustic web (alpha)            -> top layer, scrolls slowly
#  agua_sombra.png  : dark offset web (alpha)              -> shadow layer, scrolls the other way
#  cachoeira.png    : cartoon waterfall ribbons (alpha)    -> Beam texture, flows along X
#  espuma.png       : puffy foam blobs (alpha)             -> splash / foam rings
import bpy, numpy as np, os

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\dragonball_area\export\tex"

def _save(name, rgba):
    h, w, _ = rgba.shape
    img = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, alpha=True)
    if tuple(img.size) != (w, h): img.scale(w, h)
    img.alpha_mode = 'STRAIGHT'
    img.pixels.foreach_set(np.flipud(rgba).astype(np.float32).ravel())
    os.makedirs(OUT, exist_ok=True)
    img.filepath_raw = os.path.join(OUT, name + '.png')
    img.file_format = 'PNG'
    img.save()
    return img.filepath_raw

def _smooth(e0, e1, x):
    t = np.clip((x - e0)/(e1 - e0), 0, 1)
    return t*t*(3 - 2*t)

def cell_edges(size, cells, seed, warp=.06, jitter=.8):
    """Tileable Voronoi edge distance (F2-F1) on a size x size grid, in cell units."""
    rs = np.random.RandomState(seed)
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float64)/size
    # organic wobble (tileable sines)
    u = xs + warp*np.sin(2*np.pi*(ys*2 + .3*seed)) + warp*.5*np.sin(2*np.pi*(xs*3 + ys))
    v = ys + warp*np.sin(2*np.pi*(xs*2 + .7*seed)) + warp*.5*np.sin(2*np.pi*(ys*3 - xs))
    pts = []
    for i in range(cells):
        for j in range(cells):
            pts.append(((i + .5 + (rs.rand() - .5)*jitter)/cells, (j + .5 + (rs.rand() - .5)*jitter)/cells))
    pts = np.array(pts)
    f1 = np.full((size, size), 9.0); f2 = np.full((size, size), 9.0)
    for (px, py) in pts:
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                d = np.sqrt((u - px - ox)**2 + (v - py - oy)**2)*cells
                m = d < f1
                f2 = np.where(m, f1, np.minimum(f2, d))
                f1 = np.where(m, d, f1)
    return f2 - f1, f1

def water(size=512):
    e, f1 = cell_edges(size, 6, 3, warp=.022, jitter=.7)
    # thick rounded rims, thicker at the junctions (like the reference)
    width = .03 + .07*_smooth(.3, .75, f1)
    lines = 1 - _smooth(width, width + .04, e)
    rgba = np.zeros((size, size, 4)); rgba[..., :3] = 1.0; rgba[..., 3] = lines
    p1 = _save('agua_linhas', rgba)
    e2, f12 = cell_edges(size, 5, 11, warp=.03, jitter=.7)
    w2 = .035 + .06*_smooth(.35, .75, f12)
    sh = 1 - _smooth(w2, w2 + .06, e2)
    rgba = np.zeros((size, size, 4)); rgba[..., 0] = .08; rgba[..., 1] = .33; rgba[..., 2] = .55; rgba[..., 3] = sh*.55
    p2 = _save('agua_sombra', rgba)
    return p1, p2

def waterfall(w=512, h=256):
    rs = np.random.RandomState(5)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    a = np.zeros((h, w)); white = np.zeros((h, w))
    # base translucent body
    a += .55
    # ribbons: horizontal (flow along X) wavy bands, tileable in X
    for k in range(26):
        yc = rs.rand()*h; thick = rs.uniform(3, 11); amp = rs.uniform(2, 9); freq = rs.randint(1, 4); ph = rs.rand()*6.28
        length = rs.uniform(.35, .8)*w; start = rs.rand()*w
        y = yc + amp*np.sin(2*np.pi*freq*xs/w + ph)
        band = 1 - _smooth(thick*.5, thick*.5 + 2.5, np.abs(ys - y))
        dx = (xs - start) % w
        env = _smooth(0, 40, dx)*(1 - _smooth(length - 60, length, dx))
        white = np.maximum(white, band*env*rs.uniform(.6, 1))
    edge = _smooth(0, 26, ys)*(1 - _smooth(h - 26, h, ys))        # soft side edges across the width
    rgba = np.zeros((h, w, 4))
    base = np.array([.55, .86, 1.0])
    for c in range(3):
        rgba[..., c] = base[c]*(1 - white) + 1.0*white
    rgba[..., 3] = np.clip((a + white*.45)*edge, 0, 1)
    return _save('cachoeira', rgba)

def foam(size=256):
    rs = np.random.RandomState(9)
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float64)
    a = np.zeros((size, size))
    for k in range(40):
        cx, cy, r = rs.rand()*size, rs.rand()*size, rs.uniform(10, 30)
        for ox in (-size, 0, size):
            for oy in (-size, 0, size):
                d = np.sqrt((xs - cx - ox)**2 + (ys - cy - oy)**2)
                a = np.maximum(a, 1 - _smooth(r - 3, r, d))
    rgba = np.ones((size, size, 4)); rgba[..., 3] = a*.9
    return _save('espuma', rgba)

def build():
    return water(), waterfall(), foam()

def leaves(size=1024):
    """2x2 atlas of painted leaf tufts (alpha): [0] light green, [1] mid green, [2] dark green, [3] teal (Namek)."""
    rs = np.random.RandomState(21)
    cell = size//2
    ys, xs = np.mgrid[0:cell, 0:cell].astype(np.float64)
    tones = [((.62, .86, .34), (.36, .66, .22)), ((.40, .72, .28), (.22, .50, .18)),
             ((.24, .52, .22), (.12, .33, .15)), ((.36, .78, .66), (.16, .50, .46))]
    atlas = np.zeros((size, size, 4))
    for idx, (hi, lo) in enumerate(tones):
        rgb = np.zeros((cell, cell, 3)); a = np.zeros((cell, cell))
        c = cell/2
        # dense painted core (jagged by the leaves drawn over it)
        dd = np.sqrt((xs - c)**2 + ((ys - c)/.92)**2)
        core = dd < cell*.27
        tcore = np.clip(1 - ys/cell, 0, 1)
        for ch in range(3):
            rgb[..., ch] = np.where(core, lo[ch]*(1 - tcore*.6) + hi[ch]*tcore*.6, rgb[..., ch])
        a = np.where(core, 1.0, a)
        order = []
        for k in range(130):
            ang = rs.uniform(0, 2*np.pi)
            rad = cell*(.12 + (rs.rand()**.7)*.26)
            order.append((rad, ang))
        order.sort(key=lambda t: t[0])                         # inner leaves first, outer leaves drawn on top
        for rad, ang in order:
            px, py = c + np.cos(ang)*rad, c + np.sin(ang)*rad*.9
            L = cell*rs.uniform(.09, .15); W = L*rs.uniform(.42, .55)
            rot = ang + rs.uniform(-.35, .35)
            dx, dy = xs - px, ys - py
            u = (dx*np.cos(rot) + dy*np.sin(rot))/L          # along the leaf (0 at base, 1 at tip)
            v = (-dx*np.sin(rot) + dy*np.cos(rot))/W
            shape = (u > -.15) & (u < 1.0) & (np.abs(v) < np.sqrt(np.clip(1 - ((u - .42)/.58)**2, 0, 1))*.5)
            t = np.clip(1 - py/cell, 0, 1)*.7 + rad/(cell*.36)*.3           # lighter toward top / outer edge
            tone = np.array(lo)*(1 - t) + np.array(hi)*t
            vein = np.clip(1 - np.abs(v)*6, 0, 1)*.08
            for ch in range(3):
                rgb[..., ch] = np.where(shape, np.clip(tone[ch] + vein - (1 - np.abs(v)*2)*.02 + rs.uniform(-.03, .03), 0, 1), rgb[..., ch])
            a = np.where(shape, 1.0, a)
        oy, ox = (idx // 2)*cell, (idx % 2)*cell
        atlas[oy:oy+cell, ox:ox+cell, :3] = rgb
        atlas[oy:oy+cell, ox:ox+cell, 3] = a
    return _save('folhas', atlas)
