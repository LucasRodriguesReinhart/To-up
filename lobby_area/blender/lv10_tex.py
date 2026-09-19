# lv10_tex.py - texturas autorais (estilizadas, pintadas por procedimento) do Lobby V10.
# Roda no Python do sistema (PIL + numpy). Saida: lobby_area/export/tex/*.png
# Estilo: pedra clara/escura com blocos de bordas suaves, juntas visiveis, variacao por bloco,
# sem ruido fotografico. Cada textura tem ColorMap (+ NormalMap quando faz sentido).
import os, math
import numpy as np
from PIL import Image, ImageFilter

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
    """ruido de valor suave (varias oitavas) 0..1 -- para variacao de cor, nao para 'sujeira'"""
    acc = np.zeros((S, S)); amp = 1; tot = 0
    for o in range(octaves):
        c = cells * (2 ** o)
        g = rng.random((c + 1, c + 1))
        g[-1, :] = g[0, :]; g[:, -1] = g[:, 0]
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)
        acc += np.asarray(img, dtype=np.float32) / 255 * amp
        tot += amp; amp *= .5
    return acc / tot

def height_to_normal(h, strength=2.0):
    """normal map (OpenGL, +Y para cima) a partir de altura 0..1"""
    dx = np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)
    dy = np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)
    nx = -dx * strength; ny = dy * strength; nz = np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / l, ny / l, nz / l], -1)
    return n * .5 + .5

def block_layers(S, rows, cols_per_row, joint, bevel, seed, stagger=True, var=.06, warm_var=.02):
    """gera mapa de cor (variacao por bloco) e altura (juntas rebaixadas + chanfro suave)
    rows: numero de fiadas; cols_per_row: blocos por fiada; joint: largura da junta (px); bevel: largura do chanfro (px)"""
    rh = S / rows
    bw = S / cols_per_row
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    row = np.floor(yy / rh)
    off = np.where((row % 2 == 1) & stagger, bw / 2, 0)
    col = np.floor((xx + off) / bw)
    # distancia ate a borda do bloco
    ey = np.minimum(yy - row * rh, (row + 1) * rh - yy)
    ex = np.minimum((xx + off) - col * bw, (col + 1) * bw - (xx + off))
    e = np.minimum(ex, ey)
    h = np.clip((e - joint / 2) / max(bevel, 1), 0, 1)
    h = h * h * (3 - 2 * h)                     # smoothstep
    v = (hash2(col, row, seed) - .5) * 2 * var  # variacao de luminosidade por bloco
    w = (hash2(col, row, seed + 3) - .5) * 2 * warm_var
    return h, v, w

def stone(name, S, base, joint_col, rows, cols, joint, bevel, seed, var=.06, streak=.03, normal=True):
    h, v, w = block_layers(S, rows, cols, joint, bevel, seed, var=var)
    n = smooth_noise(S, 6, seed) - .5
    base = np.array(base) / 255; jc = np.array(joint_col) / 255
    col = base[None, None, :] * (1 + v[..., None]) + np.stack([w, w * .5, -w * .3], -1)
    col += n[..., None] * streak                          # manchas grandes e suaves
    # borda do bloco levemente mais clara no topo (luz pintada) e escura embaixo
    yy = np.mgrid[0:S, 0:S][0]
    col = col * (1 - .06 * (1 - h[..., None]))
    img = jc[None, None, :] * (1 - h[..., None]) + col * h[..., None]
    save(name + '.png', img)
    if normal:
        save(name + '_n.png', height_to_normal(h * .6 + smooth_noise(S, 24, seed + 9) * .05, 3.0))
    return img

# ---------------- pedra escura do corpo da torre (ref: Tower, marrom-cinza) ----------------
stone('t_stone_dark', 512, (124, 114, 102), (92, 84, 76), rows=6, cols=3, joint=4, bevel=12, seed=11, var=.06, streak=.05)
# ---------------- pedra clara das molduras / alas / bochechas (cinza-azulado claro) ----------------
stone('t_stone_light', 512, (182, 184, 190), (140, 142, 150), rows=6, cols=3, joint=4, bevel=10, seed=21, var=.045, streak=.03)
# ---------------- cantaria lisa grande (plataformas, muretas) ----------------
stone('t_ashlar', 512, (200, 196, 186), (152, 148, 140), rows=4, cols=2, joint=4, bevel=8, seed=31, var=.04, streak=.025)

# ---------------- piso: lajotas grandes com padrao 2x2 deslocado + juntas escuras ----------------
def floor_slabs(name, S=512, base=(212, 205, 190), jc=(150, 143, 130), seed=41):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    # celulas grandes 4x4 por textura; dentro de cada celula, subdivisao aleatoria 1x1, 1x2 ou 2x1
    N = 4; cs = S / N
    cell_x = np.floor(xx / cs); cell_y = np.floor(yy / cs)
    kind = np.floor(hash2(cell_x, cell_y, seed) * 3)     # 0 inteira, 1 dividida em x, 2 dividida em y
    lx = xx - cell_x * cs; ly = yy - cell_y * cs
    sub_x = np.where(kind == 1, np.floor(lx / (cs / 2)), 0)
    sub_y = np.where(kind == 2, np.floor(ly / (cs / 2)), 0)
    bx0 = np.where(kind == 1, sub_x * cs / 2, 0); bx1 = np.where(kind == 1, (sub_x + 1) * cs / 2, cs)
    by0 = np.where(kind == 2, sub_y * cs / 2, 0); by1 = np.where(kind == 2, (sub_y + 1) * cs / 2, cs)
    ex = np.minimum(lx - bx0, bx1 - lx); ey = np.minimum(ly - by0, by1 - ly)
    e = np.minimum(ex, ey)
    joint, bevel = 4, 9
    h = np.clip((e - joint / 2) / bevel, 0, 1); h = h * h * (3 - 2 * h)
    bid = cell_x * 7 + cell_y * 13 + sub_x * 3 + sub_y * 5
    v = (hash2(bid, cell_y, seed + 1) - .5) * .09
    w = (hash2(bid, cell_x, seed + 2) - .5) * .03
    base = np.array(base) / 255; jcol = np.array(jc) / 255
    col = base[None, None, :] * (1 + v[..., None]) + np.stack([w, w * .4, -w * .5], -1)
    col += (smooth_noise(S, 5, seed) - .5)[..., None] * .035
    col = col * (1 - .05 * (1 - h[..., None]))
    img = jcol[None, None, :] * (1 - h[..., None]) + col * h[..., None]
    save(name + '.png', img)
    save(name + '_n.png', height_to_normal(h * .5 + smooth_noise(S, 32, seed + 9) * .04, 3.0))
floor_slabs('t_floor', base=(206, 199, 184), jc=(138, 131, 118))
# piso claro do patamar/terraco (um tom acima)
floor_slabs('t_floor_light', base=(216, 210, 196), jc=(146, 140, 128), seed=43)

# ---------------- dourado: base quente com gradiente suave e leve escovado ----------------
def gold(name, S=256):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
    n = smooth_noise(S, 3, 51)
    base = np.array((222, 176, 78)) / 255
    hi = np.array((250, 222, 140)) / 255
    t = np.clip(.35 + (n - .5) * .9 + (yy - .5) * .2, 0, 1)
    img = base[None, None, :] * (1 - t[..., None]) + hi[None, None, :] * t[..., None]
    streak = (smooth_noise(S, 48, 52) - .5) * .05
    img += streak[..., None] * np.array([1, .9, .6])[None, None, :]
    save(name + '.png', img)
    # roughness/metal em cinza para o SurfaceAppearance
    save(name + '_r.png', np.repeat((.28 + streak * .6)[..., None], 3, -1))
gold('t_gold')

# ---------------- azul lapis dos embutidos (com veios suaves) ----------------
def lapis(name, S=256):
    n = smooth_noise(S, 4, 61); n2 = smooth_noise(S, 16, 62)
    base = np.array((34, 78, 190)) / 255; hi = np.array((70, 128, 235)) / 255; dk = np.array((22, 50, 140)) / 255
    t = np.clip((n - .5) * 2 + .5, 0, 1)
    img = dk[None, None, :] * (1 - t[..., None]) + hi[None, None, :] * t[..., None]
    img = img * .6 + base[None, None, :] * .4
    img += ((n2 - .5) * .06)[..., None]
    save(name + '.png', img)
lapis('t_lapis')

# ---------------- grama dos canteiros com florzinhas ----------------
def grass(name, S=256):
    n = smooth_noise(S, 6, 71); n2 = smooth_noise(S, 40, 72)
    a = np.array((92, 168, 78)) / 255; b = np.array((132, 200, 96)) / 255
    t = np.clip((n - .5) * 1.6 + .5 + (n2 - .5) * .8, 0, 1)
    img = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    # flores: pontinhos brancos/rosa/amarelos
    for col, k in (((250, 245, 240), 70), ((246, 176, 206), 40), ((250, 220, 110), 30)):
        for _ in range(k):
            cx, cy = rng.integers(2, S - 2, 2)
            r = rng.integers(1, 3)
            img[cy - r:cy + r + 1, cx - r:cx + r + 1] = np.array(col) / 255
    save(name + '.png', img)
grass('t_grass')

# ---------------- rocha (rochedos e pedras do canal) ----------------
def rock(name, S=512):
    n = smooth_noise(S, 4, 81); n2 = smooth_noise(S, 12, 82); n3 = smooth_noise(S, 40, 83)
    a = np.array((112, 116, 124)) / 255; b = np.array((168, 170, 176)) / 255
    t = np.clip((n - .5) * 1.8 + .5 + (n2 - .5) * .7 + (n3 - .5) * .25, 0, 1)
    img = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    # facetas: bandas horizontais suaves (estratos)
    yy = np.mgrid[0:S, 0:S][0] / S
    strata = (np.sin(yy * 40 + n * 6) * .5 + .5) ** 3 * .08
    img -= strata[..., None]
    save(name + '.png', img)
    save(name + '_n.png', height_to_normal(t * .5 + n3 * .2, 2.5))
rock('t_rock')

# ---------------- telhado/ardosia da cupula pequena (nao usado no trecho, fica pronto) ----------------
stone('t_slate', 256, (96, 112, 132), (60, 72, 88), rows=8, cols=6, joint=2, bevel=5, seed=91, var=.06, streak=.03, normal=False)

# ---------------- vidro da lanterna (branco leitoso com veios) ----------------
def milk(name, S=128):
    n = smooth_noise(S, 3, 101)
    a = np.array((236, 240, 236)) / 255; b = np.array((255, 255, 250)) / 255
    img = a[None, None, :] * (1 - n[..., None]) + b[None, None, :] * n[..., None]
    save(name + '.png', img)
milk('t_milk')
print('done')
