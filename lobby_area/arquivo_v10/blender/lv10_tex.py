# lv10_tex.py - texturas autorais (estilizadas) do Lobby V10 - PALETA v2 (revisao do usuario):
# pedra CLARA (marfim / cinza claro quente), juntas moderadas, sem azul-marinho; dourado quente;
# piso em lajotas irregulares (menos "grade"), variante com folhas caidas para bordas/canteiros.
# Roda no Python do sistema (PIL + numpy). Saida: lobby_area/export/tex/*.png (cor + normal quando util)
import os, math
import numpy as np
from PIL import Image, ImageDraw

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\export\tex"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def save(name, arr):
    arr = np.clip(arr, 0, 1)
    Image.fromarray((arr * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, name))
    print('tex', name, arr.shape)

def hash2(ix, iy, seed):
    v = np.sin(ix * 127.1 + iy * 311.7 + seed * 74.7) * 43758.5453
    return v - np.floor(v)

def smooth_noise(S, cells, seed, octaves=3):
    r = np.random.default_rng(seed)
    acc = np.zeros((S, S)); amp = 1; tot = 0
    for o in range(octaves):
        c = cells * (2 ** o)
        g = r.random((c + 1, c + 1)); g[-1, :] = g[0, :]; g[:, -1] = g[:, 0]
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)
        acc += np.asarray(img, dtype=np.float32) / 255 * amp
        tot += amp; amp *= .5
    return acc / tot

def height_to_normal(h, strength=2.0):
    dx = np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)
    dy = np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)
    nx = -dx * strength; ny = dy * strength; nz = np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx / l, ny / l, nz / l], -1) * .5 + .5

def block_layers(S, rows, cols_per_row, joint, bevel, seed, var=.06, warm_var=.02):
    rh = S / rows; bw = S / cols_per_row
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    row = np.floor(yy / rh)
    off = np.where(row % 2 == 1, bw / 2, 0)
    col = np.floor((xx + off) / bw)
    ey = np.minimum(yy - row * rh, (row + 1) * rh - yy)
    ex = np.minimum((xx + off) - col * bw, (col + 1) * bw - (xx + off))
    e = np.minimum(ex, ey)
    h = np.clip((e - joint / 2) / max(bevel, 1), 0, 1); h = h * h * (3 - 2 * h)
    v = (hash2(col, row, seed) - .5) * 2 * var
    w = (hash2(col, row, seed + 3) - .5) * 2 * warm_var
    return h, v, w

def stone(name, S, base, joint_col, rows, cols, joint, bevel, seed, var=.05, streak=.03, normal=True, nstrength=2.2):
    h, v, w = block_layers(S, rows, cols, joint, bevel, seed, var=var)
    n = smooth_noise(S, 6, seed) - .5
    base = np.array(base) / 255; jc = np.array(joint_col) / 255
    col = base[None, None, :] * (1 + v[..., None]) + np.stack([w, w * .5, -w * .3], -1)
    col += n[..., None] * streak
    col = col * (1 - .04 * (1 - h[..., None]))
    img = jc[None, None, :] * (1 - h[..., None]) + col * h[..., None]
    save(name + '.png', img)
    if normal:
        save(name + '_n.png', height_to_normal(h * .6 + smooth_noise(S, 24, seed + 9) * .04, nstrength))
    return img

# ---------------- pedra media quente do corpo da torre (clara, sem azul) ----------------
stone('t_stone_mid', 512, (190, 182, 168), (160, 152, 140), rows=5, cols=3, joint=4, bevel=14, seed=11, var=.045, streak=.035)
# ---------------- pedra clara (marfim) de molduras, pilastras, cornijas, bochechas ----------------
stone('t_stone_light', 512, (228, 223, 212), (198, 192, 180), rows=6, cols=3, joint=3, bevel=10, seed=21, var=.03, streak=.02, nstrength=1.8)
# ---------------- cantaria de plataformas / muretas ----------------
stone('t_ashlar', 512, (212, 206, 194), (176, 170, 158), rows=4, cols=2, joint=4, bevel=9, seed=31, var=.035, streak=.02)
# (legado) pedra escura - mantida para o kit antigo
stone('t_stone_dark', 512, (124, 114, 102), (92, 84, 76), rows=6, cols=3, joint=4, bevel=12, seed=11, var=.06, streak=.05)

# ---------------- piso v2: lajotas IRREGULARES (grid 6x6 com fusao aleatoria), juntas suaves ----------------
def floor_irregular(name, S=512, base=(214, 207, 192), jc=(172, 165, 152), seed=41, N=6, leaves=False):
    r = np.random.default_rng(seed)
    cs = S / N
    # mapa de "dono" da celula: funde celulas vizinhas aleatoriamente (1x1, 1x2, 2x1, 2x2)
    owner = np.arange(N * N).reshape(N, N)
    for _ in range(N * N // 2):
        i, j = r.integers(0, N, 2)
        di, dj = [(0, 1), (1, 0), (0, -1), (-1, 0)][r.integers(0, 4)]
        i2, j2 = (i + di) % N, (j + dj) % N
        owner[i2, j2] = owner[i, j]
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    ci = (np.floor(yy / cs).astype(int)) % N; cj = (np.floor(xx / cs).astype(int)) % N
    own = owner[ci, cj]
    # distancia ate a borda da lajota = distancia ate celula vizinha com dono diferente
    e = np.full((S, S), cs, dtype=np.float32)
    for d in range(1, int(cs) + 1):
        pass
    # abordagem simples: borda onde o dono muda entre pixels vizinhos, depois distancia por dilatacao
    edge = np.zeros((S, S), bool)
    edge |= own != np.roll(own, 1, 0); edge |= own != np.roll(own, 1, 1)
    from scipy import ndimage  # type: ignore
    dist = ndimage.distance_transform_edt(~edge)
    joint, bevel = 3, 9
    h = np.clip((dist - joint / 2) / bevel, 0, 1); h = h * h * (3 - 2 * h)
    v = (hash2(own % 97, own // 97, seed + 1) - .5) * .08
    w = (hash2(own % 89, own // 89, seed + 2) - .5) * .03
    base = np.array(base) / 255; jcol = np.array(jc) / 255
    col = base[None, None, :] * (1 + v[..., None]) + np.stack([w, w * .4, -w * .5], -1)
    col += (smooth_noise(S, 5, seed) - .5)[..., None] * .03
    col = col * (1 - .04 * (1 - h[..., None]))
    img = jcol[None, None, :] * (1 - h[..., None]) + col * h[..., None]
    if leaves:
        pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(pil)
        for _ in range(26):
            x, y = r.integers(0, S, 2); a = r.random() * math.pi
            L, Wd = r.integers(9, 15), r.integers(4, 7)
            colr = [(104, 168, 86), (128, 186, 96), (226, 186, 86), (200, 156, 64)][r.integers(0, 4)]
            pts = [(x + math.cos(a) * L, y + math.sin(a) * L), (x + math.cos(a + 1.9) * Wd, y + math.sin(a + 1.9) * Wd),
                   (x - math.cos(a) * L * .6, y - math.sin(a) * L * .6), (x - math.cos(a + 1.9) * Wd, y - math.sin(a + 1.9) * Wd)]
            d.polygon(pts, fill=colr)
        img = np.asarray(pil, dtype=np.float32) / 255
    save(name + '.png', img)
    save(name + '_n.png', height_to_normal(h * .5 + smooth_noise(S, 32, seed + 9) * .03, 2.2))

try:
    import scipy  # noqa
    floor_irregular('t_floor')
    floor_irregular('t_floor_light', base=(222, 216, 202), jc=(182, 175, 162), seed=43)
    floor_irregular('t_floor_leaf', base=(222, 216, 202), jc=(182, 175, 162), seed=47, leaves=True)
except ImportError:
    print('scipy ausente: piso irregular nao gerado')

# ---------------- dourado quente ----------------
def gold(name, S=256):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
    n = smooth_noise(S, 3, 51)
    base = np.array((226, 180, 82)) / 255
    hi = np.array((252, 228, 152)) / 255
    t = np.clip(.4 + (n - .5) * .9 + (yy - .5) * .2, 0, 1)
    img = base[None, None, :] * (1 - t[..., None]) + hi[None, None, :] * t[..., None]
    streak = (smooth_noise(S, 48, 52) - .5) * .05
    img += streak[..., None] * np.array([1, .9, .6])[None, None, :]
    save(name + '.png', img)
    save(name + '_r.png', np.repeat((.3 + streak * .6)[..., None], 3, -1))
gold('t_gold')

def lapis(name, S=256):
    n = smooth_noise(S, 4, 61); n2 = smooth_noise(S, 16, 62)
    hi = np.array((76, 132, 232)) / 255; dk = np.array((28, 60, 156)) / 255
    t = np.clip((n - .5) * 2 + .5, 0, 1)
    img = dk[None, None, :] * (1 - t[..., None]) + hi[None, None, :] * t[..., None]
    img += ((n2 - .5) * .06)[..., None]
    save(name + '.png', img)
lapis('t_lapis')

def grass(name, S=256):
    n = smooth_noise(S, 6, 71); n2 = smooth_noise(S, 40, 72)
    a = np.array((96, 170, 82)) / 255; b = np.array((138, 204, 100)) / 255
    t = np.clip((n - .5) * 1.6 + .5 + (n2 - .5) * .8, 0, 1)
    img = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    for col, k in (((250, 245, 240), 70), ((246, 176, 206), 40), ((250, 220, 110), 30)):
        for _ in range(k):
            cx, cy = rng.integers(2, S - 2, 2); r = rng.integers(1, 3)
            img[cy - r:cy + r + 1, cx - r:cx + r + 1] = np.array(col) / 255
    save(name + '.png', img)
grass('t_grass')

def rock(name, S=512):
    n = smooth_noise(S, 4, 81); n2 = smooth_noise(S, 12, 82); n3 = smooth_noise(S, 40, 83)
    a = np.array((138, 140, 146)) / 255; b = np.array((190, 190, 194)) / 255
    t = np.clip((n - .5) * 1.8 + .5 + (n2 - .5) * .7 + (n3 - .5) * .25, 0, 1)
    img = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    yy = np.mgrid[0:S, 0:S][0] / S
    img -= ((np.sin(yy * 40 + n * 6) * .5 + .5) ** 3 * .07)[..., None]
    save(name + '.png', img)
    save(name + '_n.png', height_to_normal(t * .5 + n3 * .2, 2.5))
rock('t_rock')

stone('t_slate', 256, (120, 138, 160), (84, 98, 118), rows=8, cols=6, joint=2, bevel=5, seed=91, var=.06, streak=.03, normal=False)

def milk(name, S=128):
    n = smooth_noise(S, 3, 101)
    a = np.array((238, 240, 236)) / 255; b = np.array((255, 255, 250)) / 255
    save(name + '.png', a[None, None, :] * (1 - n[..., None]) + b[None, None, :] * n[..., None])
milk('t_milk')
print('done')
