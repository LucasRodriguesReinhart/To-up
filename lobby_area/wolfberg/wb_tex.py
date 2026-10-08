# wb_tex.py - texturas TILEAVEIS coloridas, estilo pintado (Roblox cartoon), do lobby WOLFBERG. numpy puro + PNG.
# Diferente das texturas de detalhe do fm_mat_textures (overlay quase branco), estas sao albedo COMPLETO (alpha 1):
# no Roblox entram como SurfaceAppearance.ColorMap (AlphaMode Overlay com alpha 1 = substitui a cor) e no Blender
# como Base Color (fm_lib mistura cor x textura pelo alpha). A cor base do material so aparece onde alpha < 1.
# uso: python wb_tex.py [pasta]   (padrao: lobby_area/wolfberg/textures). Determinístico por chave.
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "textures")
VERSION = 1
N = 1024

# chave -> (arquivo, studs por repeticao)
TEXTURES = {
    "wb_cobble": ("WB_cobble_v%d.png" % VERSION, 6.0),
    "wb_stone": ("WB_stone_v%d.png" % VERSION, 6.0),
    "wb_stone_dark": ("WB_stone_dark_v%d.png" % VERSION, 6.0),
    "wb_plaster": ("WB_plaster_v%d.png" % VERSION, 8.0),
    "wb_timber": ("WB_timber_v%d.png" % VERSION, 4.0),
    "wb_plank": ("WB_plank_v%d.png" % VERSION, 4.0),
    "wb_roof": ("WB_roof_v%d.png" % VERSION, 4.0),
    "wb_canvas_red": ("WB_canvas_red_v%d.png" % VERSION, 4.0),
    "wb_canvas_blue": ("WB_canvas_blue_v%d.png" % VERSION, 4.0),
    "wb_canvas_green": ("WB_canvas_green_v%d.png" % VERSION, 4.0),
    "wb_iron": ("WB_iron_v%d.png" % VERSION, 4.0),
    "wb_grass": ("WB_grass_v%d.png" % VERSION, 10.0),
    "wb_dirt": ("WB_dirt_v%d.png" % VERSION, 8.0),
    "wb_bark": ("WB_bark_v%d.png" % VERSION, 4.0),
    "wb_leaf": ("WB_leaf_v%d.png" % VERSION, 6.0),
    "wb_rock": ("WB_rock_v%d.png" % VERSION, 16.0),
    "wb_pine": ("WB_pine_v%d.png" % VERSION, 6.0),
    "wb_crop": ("WB_crop_v%d.png" % VERSION, 12.0),
    "wb_roof_dark": ("WB_roof_dark_v%d.png" % VERSION, 4.0),
    "wb_plaster_ochre": ("WB_plaster_ochre_v%d.png" % VERSION, 8.0),
    "wb_flag": ("WB_flag_v%d.png" % VERSION, 8.0),
}


# ------------------------------------------------------------------ PNG + ruido tileavel
def write_png(path, rgba):
    import struct
    a = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    h, w, _ = a.shape
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
           chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def vnoise(rng, cx, cy=None, n=N):
    """value noise tileavel com cx x cy celulas (interpolacao suave)"""
    cy = cy or cx
    g = rng.random((cy, cx))
    ys = np.linspace(0, cy, n, endpoint=False)
    xs = np.linspace(0, cx, n, endpoint=False)
    y0 = np.floor(ys).astype(int) % cy
    x0 = np.floor(xs).astype(int) % cx
    fy = ys - np.floor(ys)
    fx = xs - np.floor(xs)
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    y1 = (y0 + 1) % cy
    x1 = (x0 + 1) % cx
    a = g[np.ix_(y0, x0)]
    b = g[np.ix_(y0, x1)]
    c = g[np.ix_(y1, x0)]
    d = g[np.ix_(y1, x1)]
    fx = fx[None, :]
    fy = fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(rng, c0, octaves=4, aniso=1.0, n=N, gain=0.5):
    out = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    c = c0
    for _ in range(octaves):
        out += amp * vnoise(rng, max(1, int(round(c * aniso))), max(1, int(round(c))), n)
        tot += amp
        amp *= gain
        c *= 2
    return out / tot


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def grid(n=N):
    y, x = np.mgrid[0:n, 0:n]
    return x / n, y / n


def wrap_d(a, b):
    d = np.abs(a - b)
    return np.minimum(d, 1 - d)


def rgb(c):
    return np.array(c, dtype=float) / 255.0


def paint(col, shade):
    """col (3,) * shade [H,W] -> [H,W,3]"""
    return col[None, None, :] * shade[:, :, None]


def rgba(img3, alpha=1.0):
    a = np.full(img3.shape[:2] + (1,), alpha)
    return np.concatenate([np.clip(img3, 0, 1), a], axis=2)


def mix(a, b, t):
    t = t[:, :, None] if t.ndim == 2 else t
    return a * (1 - t) + b * t


def srgb_tone(img, k=1.0):
    return np.clip(img * k, 0, 1)


# ------------------------------------------------------------------ pedras arredondadas (celulas com jitter)
def stones(rng, nx, ny, jitter=0.35, round_k=0.45, gap=0.09, shade_dir=(-0.6, -0.8), n=N, rect=False):
    """mapa de pedras: devolve (mask dentro-da-pedra 0..1, altura/shading 0..1, id por pixel) com repeticao perfeita"""
    x, y = grid(n)
    best_d = np.full((n, n), 9.0)
    second = np.full((n, n), 9.0)
    best_id = np.zeros((n, n), dtype=int)
    best_dx = np.zeros((n, n))
    best_dy = np.zeros((n, n))
    sx, sy = 1.0 / nx, 1.0 / ny
    for j in range(ny):
        for i in range(nx):
            cx = (i + 0.5 + rng.uniform(-jitter, jitter) * 0.5) * sx
            cy = (j + 0.5 + rng.uniform(-jitter, jitter) * 0.5) * sy
            rx = sx * 0.5 * rng.uniform(0.85, 1.0)
            ry = sy * 0.5 * rng.uniform(0.85, 1.0)
            dx = wrap_d(x, cx) / rx
            dy = wrap_d(y, cy) / ry
            if rect:
                d = np.maximum(dx, dy) * (1 - round_k) + round_k * np.sqrt(dx * dx + dy * dy)
            else:
                d = (dx ** 3 + dy ** 3) ** (1 / 3)
            upd = d < best_d
            second = np.where(upd, best_d, np.minimum(second, d))
            best_d = np.where(upd, d, best_d)
            best_id = np.where(upd, j * nx + i, best_id)
            ndx = np.where(x - cx > 0.5, x - cx - 1, np.where(x - cx < -0.5, x - cx + 1, x - cx)) / rx
            ndy = np.where(y - cy > 0.5, y - cy - 1, np.where(y - cy < -0.5, y - cy + 1, y - cy)) / ry
            best_dx = np.where(upd, ndx, best_dx)
            best_dy = np.where(upd, ndy, best_dy)
    edge = second - best_d          # distancia ate a pedra vizinha (0 na junta)
    inside = smoothstep(gap, gap * 2.2, edge)
    dome = np.clip(1 - best_d, 0, 1) ** 0.6
    light = np.clip(0.5 + 0.5 * (best_dx * shade_dir[0] + best_dy * shade_dir[1]), 0, 1)
    shade = 0.55 + 0.45 * dome * (0.6 + 0.4 * light)
    return inside, shade, best_id


def id_variation(ids, rng, k=0.12, n=N):
    tab = rng.uniform(1 - k, 1 + k, ids.max() + 1)
    return tab[ids]


# ------------------------------------------------------------------ texturas
def tex_cobble(rng):
    inside, shade, ids = stones(rng, 7, 7, jitter=0.5, gap=0.07)
    base = rgb((160, 146, 128))
    var = id_variation(ids, rng, 0.18)
    warm = rng.uniform(-0.05, 0.05, ids.max() + 1)
    tint = np.stack([1 + warm, 1 + warm * 0.4, 1 - warm * 0.6], axis=1)      # so deriva quente/fria, sem arco-iris
    col = base[None, None, :] * tint[ids] * var[:, :, None]
    grain = 0.92 + 0.16 * fbm(rng, 48, 3)
    col = col * (shade * grain)[:, :, None]
    joint = rgb((82, 70, 58)) * (0.85 + 0.3 * fbm(rng, 24, 2))[:, :, None]
    img = mix(joint, col, inside)
    moss = smoothstep(0.62, 0.78, fbm(rng, 5, 3)) * (1 - inside) * 0.6
    img = mix(img, rgb((96, 118, 60)), moss)
    return rgba(img)


def _ashlar(rng, rows, cols, dark=False):
    """fiadas de blocos (aparelho) com juntas; blocos arredondados"""
    x, y = grid()
    img = np.zeros((N, N, 3))
    inside_all = np.zeros((N, N))
    shade_all = np.zeros((N, N))
    rh = 1.0 / rows
    base = rgb((108, 102, 98)) if dark else rgb((152, 144, 132))
    for j in range(rows):
        off = (j % 2) * 0.5 / cols
        y0 = j * rh
        for i in range(cols):
            w = 1.0 / cols * rng.uniform(0.75, 1.25)
            x0 = i / cols + off
            cx = x0 + w * 0.5
            cy = y0 + rh * 0.5
            dx = wrap_d(x, cx) / (w * 0.5)
            dy = wrap_d(y, cy) / (rh * 0.5)
            d = (dx ** 4 + dy ** 4) ** 0.25
            inside = smoothstep(1.0, 0.86, d)
            dome = np.clip(1 - d, 0, 1) ** 0.5
            lx = np.where(x - cx > 0.5, x - cx - 1, np.where(x - cx < -0.5, x - cx + 1, x - cx)) / (w * 0.5)
            ly = np.where(y - cy > 0.5, y - cy - 1, np.where(y - cy < -0.5, y - cy + 1, y - cy)) / (rh * 0.5)
            light = np.clip(0.5 + 0.5 * (-0.5 * lx - 0.85 * ly), 0, 1)
            sh = 0.6 + 0.4 * dome * (0.55 + 0.45 * light)
            k = rng.uniform(0.82, 1.14)
            wv = rng.uniform(-0.04, 0.04)
            tint = np.array([k * (1 + wv), k * (1 + wv * 0.4), k * (1 - wv * 0.6)])
            img = np.where(inside[:, :, None] > inside_all[:, :, None], (base * tint)[None, None, :] * sh[:, :, None], img)
            shade_all = np.where(inside > inside_all, sh, shade_all)
            inside_all = np.maximum(inside_all, inside)
    grain = 0.9 + 0.2 * fbm(rng, 40, 3)
    img = img * grain[:, :, None]
    mortar = (rgb((70, 64, 60)) if dark else rgb((92, 86, 80))) * (0.85 + 0.3 * fbm(rng, 20, 2))[:, :, None]
    return mix(mortar, img, inside_all)


def tex_stone(rng):
    return rgba(_ashlar(rng, 7, 5))


def tex_stone_dark(rng):
    return rgba(_ashlar(rng, 8, 6, dark=True))


def tex_plaster(rng):
    base = rgb((222, 204, 170))
    big = fbm(rng, 3, 4)
    fine = fbm(rng, 60, 3)
    img = paint(base, 0.84 + 0.18 * big + 0.08 * fine)
    dirt = smoothstep(0.5, 0.85, fbm(rng, 4, 4, gain=0.6))
    img = mix(img, rgb((138, 116, 88)), dirt * 0.55)
    # trincas finas
    x, y = grid()
    for _ in range(5):
        px, py = rng.random(), rng.random()
        ang = rng.uniform(0, math.pi)
        L = rng.uniform(0.08, 0.22)
        t = np.linspace(0, 1, 220)
        wob = np.cumsum(rng.normal(0, 0.012, 220))
        cx = (px + np.cos(ang) * t * L + np.sin(ang) * wob) % 1
        cy = (py + np.sin(ang) * t * L - np.cos(ang) * wob) % 1
        d = np.full((N, N), 9.0)
        for k in range(0, 220, 4):
            d = np.minimum(d, np.hypot(wrap_d(x, cx[k]), wrap_d(y, cy[k])))
        img = mix(img, rgb((120, 104, 84)), smoothstep(0.0025, 0.0008, d) * 0.7)
    return rgba(img)


def tex_timber(rng):
    base = rgb((88, 60, 40))
    g = fbm(rng, 3, 5, aniso=12)
    rings = 0.5 + 0.5 * np.sin(g * 26 + fbm(rng, 2, 3, aniso=6) * 6)
    img = paint(base, 0.78 + 0.32 * rings)
    knots = smoothstep(0.78, 0.9, fbm(rng, 6, 2))
    img = mix(img, rgb((52, 34, 22)), knots * 0.8)
    return rgba(img)


def tex_plank(rng):
    base = rgb((150, 104, 64))
    x, y = grid()
    rows = 5
    img = np.zeros((N, N, 3))
    seam = np.ones((N, N))
    for j in range(rows):
        y0 = j / rows
        yy = (y - y0) % 1
        inside = (yy < 1.0 / rows)
        tint = rng.uniform(0.86, 1.1, 3)
        g = fbm(rng, 2, 4, aniso=14)
        grain = 0.82 + 0.28 * (0.5 + 0.5 * np.sin(g * 22 + rng.uniform(0, 6)))
        img = np.where(inside[:, :, None], (base * tint)[None, None, :] * grain[:, :, None], img)
        s = smoothstep(0.012, 0.0, wrap_d(y, y0))
        seam = np.minimum(seam, 1 - s * 0.7)
    img = img * seam[:, :, None]
    nails = np.zeros((N, N))
    for j in range(rows):
        for k in (0.12, 0.88):
            cy = (j / rows + 0.5 / rows) % 1
            nails = np.maximum(nails, smoothstep(0.009, 0.004, np.hypot(wrap_d(x, k), wrap_d(y, cy))))
    img = mix(img, rgb((60, 56, 56)), nails)
    return rgba(img)


def tex_roof(rng):
    base = rgb((156, 72, 46))
    x, y = grid()
    rows, cols = 8, 6
    img = np.zeros((N, N, 3))
    cover = np.zeros((N, N))
    for j in range(rows):
        y0 = j / rows
        off = (j % 2) * 0.5 / cols
        for i in range(cols):
            cx = (i / cols + off + 0.5 / cols)
            dx = wrap_d(x, cx) * cols * 2
            yy = ((y - y0) % 1) * rows
            # telha: meia-cana arredondada, sombra na base da fiada
            inside = (yy < 1.0) & (dx < 1.0)
            curve = np.sqrt(np.clip(1 - dx * dx, 0, 1))
            tint = rng.uniform(0.85, 1.12, 3)
            sh = (0.55 + 0.45 * curve) * (0.75 + 0.25 * smoothstep(0.0, 0.35, yy))
            img = np.where(inside[:, :, None], (base * tint)[None, None, :] * sh[:, :, None], img)
            cover = np.where(inside, 1.0, cover)
    grain = 0.9 + 0.2 * fbm(rng, 30, 3)
    img = img * grain[:, :, None]
    lichen = smoothstep(0.7, 0.9, fbm(rng, 5, 3)) * 0.35
    img = mix(img, rgb((150, 150, 110)), lichen)
    return rgba(img)


def _canvas(rng, col_a, col_b):
    x, y = grid()
    stripes = 0.5 + 0.5 * np.sign(np.sin(x * 2 * math.pi * 4 + 1e-6))
    weave = 0.9 + 0.1 * fbm(rng, 90, 2)
    img = mix(np.broadcast_to(rgb(col_a), (N, N, 3)), np.broadcast_to(rgb(col_b), (N, N, 3)), stripes)
    img = img * weave[:, :, None]
    dirt = smoothstep(0.6, 0.85, fbm(rng, 3, 3)) * 0.25
    img = mix(img, rgb((120, 100, 80)), dirt)
    return rgba(img)


def tex_canvas_red(rng):
    return _canvas(rng, (236, 226, 206), (190, 52, 44))


def tex_canvas_blue(rng):
    return _canvas(rng, (236, 226, 206), (54, 92, 160))


def tex_canvas_green(rng):
    return _canvas(rng, (236, 226, 206), (76, 132, 72))


def tex_iron(rng):
    base = rgb((74, 72, 76))
    img = paint(base, 0.85 + 0.3 * fbm(rng, 40, 4, aniso=4))
    rust = smoothstep(0.6, 0.85, fbm(rng, 4, 4, gain=0.6))
    img = mix(img, rgb((132, 72, 36)), rust * 0.7)
    return rgba(img)


def tex_grass(rng):
    base = rgb((104, 160, 58))
    big = fbm(rng, 3, 3)
    blades = fbm(rng, 70, 3, aniso=0.4)
    img = paint(base, 0.8 + 0.25 * big + 0.2 * (blades - 0.5))
    clumps = smoothstep(0.68, 0.85, fbm(rng, 10, 3))
    img = mix(img, rgb((72, 128, 46)), clumps * 0.6)
    flowers = smoothstep(0.86, 0.9, fbm(rng, 60, 1))
    img = mix(img, rgb((240, 220, 90)), flowers * 0.8)
    return rgba(img)


def tex_dirt(rng):
    base = rgb((150, 118, 82))
    img = paint(base, 0.8 + 0.3 * fbm(rng, 6, 4))
    inside, shade, ids = stones(rng, 14, 14, jitter=0.9, gap=0.3)
    pebbles = inside * smoothstep(0.7, 0.9, fbm(rng, 14, 1))
    img = mix(img, rgb((130, 122, 110)) * shade[:, :, None], pebbles)
    return rgba(img)


def tex_bark(rng):
    base = rgb((96, 66, 44))
    g = fbm(rng, 2, 5, aniso=0.15)
    img = paint(base, 0.65 + 0.5 * g)
    fiss = smoothstep(0.3, 0.2, fbm(rng, 6, 3, aniso=0.2))
    img = mix(img, rgb((48, 32, 22)), fiss * 0.8)
    return rgba(img)


def tex_leaf(rng):
    base = rgb((84, 150, 62))
    inside, shade, ids = stones(rng, 6, 6, jitter=0.6, gap=0.02)
    var = id_variation(ids, rng, 0.14)
    img = paint(base, (0.7 + 0.5 * shade) * var)
    img = mix(img, rgb((56, 110, 44)), (1 - inside) * 0.7)
    return rgba(img)


def tex_rock(rng):
    base = rgb((132, 122, 112))
    big = fbm(rng, 2, 5)
    strata = 0.5 + 0.5 * np.sin(grid()[1] * 2 * math.pi * 5 + big * 4)
    img = paint(base, 0.55 + 0.45 * big + 0.18 * strata)
    cracks = smoothstep(0.26, 0.2, fbm(rng, 8, 3))
    img = mix(img, rgb((70, 64, 60)), cracks * 0.6)
    return rgba(img)


def tex_pine(rng):
    base = rgb((46, 104, 66))
    inside, shade, ids = stones(rng, 7, 7, jitter=0.6, gap=0.02)
    var = id_variation(ids, rng, 0.16)
    img = paint(base, (0.7 + 0.5 * shade) * var)
    img = mix(img, rgb((28, 66, 48)), (1 - inside) * 0.7)
    return rgba(img)


def tex_crop(rng):
    """faixas lavradas (campos das colinas): sulcos de terra entre linhas verde-amareladas"""
    gy = grid()[1]
    rows = 0.5 + 0.5 * np.sin(gy * 2 * math.pi * 12)
    big = fbm(rng, 3, 3)
    green = rgb((150, 170, 70))
    img = paint(green, 0.75 + 0.3 * big)
    img = mix(img, rgb((140, 108, 72)), smoothstep(0.55, 0.9, rows) * 0.8)
    return rgba(img)


def tex_flag(rng):
    """lajeado de pedras GRANDES (3-4 por tile de 8 studs) com juntas de musgo/terra: o eixo principal da vila"""
    inside, shade, ids = stones(rng, 4, 3, jitter=0.3, round_k=0.2, gap=0.05, rect=True)
    base = rgb((178, 166, 146))
    var = id_variation(ids, rng, 0.14)
    warm = rng.uniform(-0.04, 0.04, ids.max() + 1)
    tint = np.stack([1 + warm, 1 + warm * 0.4, 1 - warm * 0.6], axis=1)
    col = base[None, None, :] * tint[ids] * var[:, :, None]
    fine = fbm(rng, 40, 3)
    img = col * (0.9 + 0.2 * fine[:, :, None]) * (0.75 + 0.35 * shade[:, :, None])
    joint = rgb((96, 108, 70))                        # musgo/terra nas juntas
    img = mix(img, joint, (1 - inside) * 0.85)
    cracks = smoothstep(0.3, 0.24, fbm(rng, 10, 3))
    img = mix(img, rgb((120, 110, 96)), cracks * inside * 0.5)
    return rgba(img)


def tex_roof_dark(rng):
    img = tex_roof(rng)
    img[:, :, :3] = img[:, :, :3] * np.array([0.78, 0.74, 0.8])[None, None, :]
    return img


def tex_plaster_ochre(rng):
    img = tex_plaster(rng)
    img[:, :, :3] = img[:, :, :3] * np.array([0.98, 0.92, 0.8])[None, None, :]
    return img


GEN = {"wb_cobble": tex_cobble, "wb_stone": tex_stone, "wb_stone_dark": tex_stone_dark, "wb_plaster": tex_plaster,
       "wb_timber": tex_timber, "wb_plank": tex_plank, "wb_roof": tex_roof, "wb_canvas_red": tex_canvas_red,
       "wb_canvas_blue": tex_canvas_blue, "wb_canvas_green": tex_canvas_green, "wb_iron": tex_iron,
       "wb_grass": tex_grass, "wb_dirt": tex_dirt, "wb_bark": tex_bark, "wb_leaf": tex_leaf, "wb_rock": tex_rock,
       "wb_pine": tex_pine, "wb_crop": tex_crop, "wb_roof_dark": tex_roof_dark, "wb_plaster_ochre": tex_plaster_ochre,
       "wb_flag": tex_flag}


def path(key):
    return os.path.join(TEX_DIR, TEXTURES[key][0])


def ensure(force=False, out_dir=None, only=None):
    global TEX_DIR
    if out_dir:
        TEX_DIR = out_dir
    os.makedirs(TEX_DIR, exist_ok=True)
    done = {}
    for key, (fn, tile) in sorted(TEXTURES.items()):
        if only and key not in only:
            continue
        p = os.path.join(TEX_DIR, fn)
        if force or not os.path.exists(p):
            rng = np.random.default_rng(7000 + zlib.crc32(key.encode()) % 10000)
            write_png(p, GEN[key](rng))
            print("TEX", key, fn)
        done[key] = p
    return done


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    force = "--force" in sys.argv
    only = [a for a in sys.argv[2:] if not a.startswith("--")] or None
    ensure(force=force, out_dir=out, only=only)
