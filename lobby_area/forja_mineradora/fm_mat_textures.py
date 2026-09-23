# fm_mat_textures - texturas estilizadas TILEAVEIS geradas por codigo (numpy puro + PNG via zlib).
# Roda dentro do Blender (numpy embutido) ou no Python do sistema:  python fm_mat_textures.py [pasta]
#
# Sao texturas de DETALHE em overlay (RGBA): RGB quase preto (escurece) ou quase branco (clareia) e o ALPHA
# e a forca. A cor de fundo vem da variante do material (Stone_Light_B, Wood_Dark_C...), entao UMA textura
# serve para todas as variantes da familia:
#   Blender : base_color = mix(cor_variante, tex.rgb, tex.alpha)          (fm_lib.make_materials)
#   Roblox  : SurfaceAppearance.AlphaMode = Overlay -> mesma formula sobre MeshPart.Color (montar_lobby_forja.lua)
# As UVs sao projecao planar alinhada a cada primitiva, em studs / TILE (fm_lib.MB), e vao no FBX.
# Espirais dos portais: PNG opaco por portal, UV planar do disco (export_roblox.py).
import os, math, zlib, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "textures")
N = 512
VERSION = 3

# chave: (arquivo, studs por repeticao)
TEXTURES = {
    "stone":   ("T_stone_v%d.png" % VERSION, 6.0),
    "wood":    ("T_wood_v%d.png" % VERSION, 5.0),
    "roof":    ("T_roof_v%d.png" % VERSION, 5.0),
    "rock":    ("T_rock_v%d.png" % VERSION, 18.0),
    "grass":   ("T_grass_v%d.png" % VERSION, 14.0),
    "plaster": ("T_plaster_v%d.png" % VERSION, 8.0),
    "dirt":    ("T_dirt_v%d.png" % VERSION, 10.0),
}
# espirais: material -> (arquivo, cor dos bracos sRGB, cor do nucleo sRGB)
SWIRL_TEX = {
    "P_Naruto_Swirl": ("T_swirl_naruto_v%d.png" % VERSION, (236, 110, 158), (255, 214, 226)),
    "P_DB_Swirl":     ("T_swirl_db_v%d.png" % VERSION, (236, 184, 70), (255, 246, 200)),
    "P_Shadow_Swirl": ("T_swirl_shadow_v%d.png" % VERSION, (160, 96, 226), (236, 214, 255)),
    "P_DS_Swirl":     ("T_swirl_ds_v%d.png" % VERSION, (226, 86, 86), (255, 214, 206)),
    "P_OP_Swirl":     ("T_swirl_op_v%d.png" % VERSION, (84, 146, 236), (214, 234, 255)),
    "P_OPM_Swirl":    ("T_swirl_opm_v%d.png" % VERSION, (96, 192, 236), (224, 248, 255)),
}


# ------------------------------------------------------------------ PNG
def write_png(path, rgba):
    """rgba: float [H,W,4] em 0..1 (sRGB) -> PNG RGBA 8 bits"""
    a = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
    h, w, _ = a.shape
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
           chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------------ ruido tileavel
def vnoise(rng, cx, cy=None, n=N):
    """value noise periodico (cx x cy celulas), suavizado (smoothstep), em 0..1"""
    cy = cy or cx
    g = rng.random((cy, cx))
    xs = np.arange(n) * cx / n
    ys = np.arange(n) * cy / n
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = xs - x0
    fy = ys - y0
    sx = (fx * fx * (3 - 2 * fx))[None, :]
    sy = (fy * fy * (3 - 2 * fy))[:, None]
    x1 = (x0 + 1) % cx
    y1 = (y0 + 1) % cy
    x0 %= cx
    y0 %= cy
    r0 = g[y0]
    r1 = g[y1]
    top = r0[:, x0] + (r0[:, x1] - r0[:, x0]) * sx
    bot = r1[:, x0] + (r1[:, x1] - r1[:, x0]) * sx
    return top + (bot - top) * sy


def fbm(rng, c0, octaves=4, aniso=1.0, n=N):
    """fBm periodico em -1..1; aniso > 1 estica ao longo de x (fibras)"""
    acc = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for k in range(octaves):
        c = c0 * 2 ** k
        cx = max(1, int(round(c / aniso)))
        acc += amp * (vnoise(rng, cx, int(c), n) * 2 - 1)
        tot += amp
        amp *= 0.5
    return acc / tot


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def crack(E, rng, x, y, ang, length, strength, width=1.0, wobble=0.35, branch=0.0, n=N):
    """fissura: passeio aleatorio desenhado com wrap (continua tileavel). Escurece E (negativo)."""
    step = 1.5
    for i in range(int(length / step)):
        ang += rng.normal(0, wobble)
        x += math.cos(ang) * step
        y += math.sin(ang) * step
        taper = 1.0 - i / (length / step) * 0.6
        r = width * taper
        ri = int(math.ceil(r + 1))
        for dy in range(-ri, ri + 1):
            for dx in range(-ri, ri + 1):
                d = math.hypot(dx, dy)
                if d > r + 1:
                    continue
                f = strength * taper * (1.0 if d <= r else (r + 1 - d))
                yy = int(y + dy) % n
                xx = int(x + dx) % n
                if -f < E[yy, xx]:
                    E[yy, xx] = -f
        if branch > 0 and rng.random() < branch / (length / step):
            crack(E, rng, x, y, ang + rng.choice((-1, 1)) * rng.uniform(0.5, 1.1), length * 0.35,
                  strength * 0.8, width * 0.7, wobble, 0.0, n)


def blobs(rng, count, rmin, rmax, squash=1.0, n=N):
    """manchas redondas suaves (com wrap) -> campo 0..1 (poros, graos, liquen, pedriscos)"""
    F = np.zeros((n, n))
    for i in range(count):
        cx, cy = rng.uniform(0, n), rng.uniform(0, n)
        r = rng.uniform(rmin, rmax)
        R = int(math.ceil(r * max(1.0, squash))) + 2
        xs = (np.arange(int(cx) - R, int(cx) + R + 1)) % n
        ys = (np.arange(int(cy) - R, int(cy) + R + 1)) % n
        dx = (np.arange(int(cx) - R, int(cx) + R + 1) - cx)[None, :] / squash
        dy = (np.arange(int(cy) - R, int(cy) + R + 1) - cy)[:, None]
        d = np.sqrt(dx * dx + dy * dy) / r
        v = 1 - smoothstep(0.55, 1.0, d)
        sub = F[np.ix_(ys, xs)]
        F[np.ix_(ys, xs)] = np.maximum(sub, v * rng.uniform(0.6, 1.0))
    return F


def to_overlay(E, dark=(0.10, 0.075, 0.06), light=(1.0, 0.97, 0.90), gain=1.0):
    """E em -1..1 -> RGBA de overlay (preto quente escurece, branco quente clareia, alpha = |E|)"""
    a = np.clip(np.abs(E) * gain, 0, 1)
    neg = (E < 0)[..., None]
    rgb = np.where(neg, np.array(dark)[None, None, :], np.array(light)[None, None, :])
    return np.concatenate([rgb, a[..., None]], axis=2)


# ------------------------------------------------------------------ familias
def tex_stone(rng):
    """alvenaria/calcamento: manchas amplas, poros escuros, graos claros, poucas fissuras finas"""
    E = 0.13 * fbm(rng, 3, 4)
    E += 0.05 * fbm(rng, 24, 2)
    E -= 0.30 * blobs(rng, 260, 1.2, 2.6)          # poros
    E += 0.16 * blobs(rng, 160, 1.5, 3.5)          # graos claros
    E -= 0.08 * blobs(rng, 7, 26, 48) * (0.6 + 0.4 * fbm(rng, 8, 2))   # manchas de fuligem/umidade
    C = np.zeros_like(E)
    for i in range(3):
        x, y, a = rng.uniform(0, N), rng.uniform(0, N), rng.uniform(0, math.tau)
        crack(C, rng, x, y, a, rng.uniform(90, 170), 0.5, 1.0, 0.13, branch=0.8)
    # fissura com borda lascada: realce claro ao lado da linha escura
    L = np.roll(np.roll(-C, 2, 0), 2, 1) * 0.35
    E = np.where(C < -0.05, C, np.maximum(E, E + L))
    return to_overlay(E)


def tex_wood(rng):
    """veio longitudinal (ao longo de u = eixo maior da peca), fibras, nos"""
    warp = fbm(rng, 3, 3, aniso=4.0)
    yy = np.arange(N)[:, None] / N
    ring = yy * 11.0 + warp * 1.6
    fr = np.abs((ring % 1.0) - 0.5) * 2          # 0 no veio
    lines = 1 - smoothstep(0.0, 0.16, fr)
    E = -0.30 * lines
    E += 0.12 * fbm(rng, 6, 3, aniso=8.0)        # fibras compridas
    E -= 0.10 * smoothstep(0.55, 0.9, vnoise(rng, 2, 40))   # faixas escuras
    # nos: aneis escuros elipticos
    xx = np.arange(N)[None, :]
    yv = np.arange(N)[:, None]
    for i in range(2):
        cx, cy = rng.uniform(0, N), rng.uniform(0, N)
        dx = (xx - cx + N / 2) % N - N / 2
        dy = (yv - cy + N / 2) % N - N / 2
        d = np.sqrt((dx / 2.6) ** 2 + dy ** 2)
        r = rng.uniform(7, 11)
        E -= 0.45 * (1 - smoothstep(r * 0.35, r, d))
        E -= 0.18 * (1 - smoothstep(0.0, 1.8, np.abs(d - r * 1.5)))
    return to_overlay(E, dark=(0.09, 0.05, 0.02), light=(1.0, 0.93, 0.80))


def tex_roof(rng):
    """telhas individuais: frestas verticais com jitter (u = ao longo da fiada) + tom por telha"""
    E = np.zeros((N, N))
    xs = []
    x = 0.0
    while x < N - 40:
        xs.append(x)
        x += rng.uniform(46, 70)          # ~0.5-0.7 stud por telha (tile de 5 studs)
    xx = np.arange(N)[None, :].repeat(N, 0).astype(float)
    wob = fbm(rng, 2, 2) * 6
    xw = (xx + wob) % N
    idx = np.searchsorted(np.array(xs), xw, side="right") - 1
    tone = np.array([rng.choice((-1, 1)) * rng.uniform(0.06, 0.22) for _ in xs])
    E += tone[idx]
    gap = np.full((N, N), 1e9)
    for x0 in xs + [N]:
        gap = np.minimum(gap, np.abs(xw - x0))
    E = np.where(gap < 2.5, -0.50, E)
    E = np.where((gap >= 2.5) & (gap < 6.0), E - 0.10, E)
    E += 0.07 * fbm(rng, 6, 3, aniso=0.3)            # escorrido vertical
    E -= 0.14 * blobs(rng, 30, 4, 10)                  # manchas escuras (musgo/fuligem)
    return to_overlay(E, dark=(0.07, 0.06, 0.06), light=(1.0, 0.98, 0.94))


def tex_rock(rng):
    """penhasco: estratos (variam em u = eixo maior, vertical nas colunas), juntas longas, liquen claro"""
    E = 0.12 * fbm(rng, 2, 4)
    band = vnoise(rng, 5, 1)                       # varia so em x (estratos)
    E += 0.20 * (band - 0.5)
    b2 = np.abs(((np.arange(N)[None, :] / N * 4 + fbm(rng, 2, 2) * 0.35) % 1.0) - 0.5) * 2
    E -= 0.26 * (1 - smoothstep(0.0, 0.025, b2))    # 4 linhas de estrato largas
    E += 0.10 * (1 - smoothstep(0.025, 0.06, b2)) * (b2 > 0.025)   # quina clara acima da linha
    C = np.zeros_like(E)
    for i in range(4):
        crack(C, rng, rng.uniform(0, N), rng.uniform(0, N), rng.choice((0.0, math.pi)) + rng.uniform(-0.25, 0.25),
              rng.uniform(160, 320), 0.5, 1.4, 0.08, branch=1.0)
    E = np.minimum(E, E + C)
    E -= 0.10 * np.clip(fbm(rng, 3, 3, aniso=6.0), 0, 1)          # escorridos de agua (ao longo de u)
    moss = smoothstep(0.35, 0.75, fbm(rng, 4, 4) * 0.5 + 0.5) * smoothstep(0.2, 0.6, vnoise(rng, 12))
    E += 0.10 * moss                                                  # liquen/musgo claro irregular
    E -= 0.10 * blobs(rng, 60, 1.5, 3.0)             # cavidades
    return to_overlay(E, dark=(0.08, 0.07, 0.08), light=(0.86, 0.95, 0.74))


def tex_grass(rng):
    """gramado estilizado: tufos claros/escuros e laminas curtas"""
    E = 0.14 * fbm(rng, 3, 3)
    E += 0.06 * (vnoise(rng, 90, 30) * 2 - 1)
    E -= 0.14 * blobs(rng, 120, 3, 7, squash=0.5)     # tufos escuros
    E += 0.13 * blobs(rng, 120, 2, 6, squash=0.4)     # laminas claras
    return to_overlay(E, dark=(0.03, 0.08, 0.02), light=(0.95, 1.0, 0.78))


def tex_plaster(rng):
    """reboco: manchas suaves, umidade junto a um lado, trincas raras"""
    E = 0.05 * fbm(rng, 3, 4)
    E -= 0.07 * smoothstep(0.6, 0.9, vnoise(rng, 3))
    C = np.zeros_like(E)
    for i in range(2):
        crack(C, rng, rng.uniform(0, N), rng.uniform(0, N), rng.uniform(0, math.tau), rng.uniform(40, 90), 0.28,
              0.7, 0.4, branch=1.0)
    E = np.minimum(E, E + C)
    return to_overlay(E, dark=(0.14, 0.10, 0.07), light=(1.0, 0.98, 0.94))


def tex_dirt(rng):
    E = 0.14 * fbm(rng, 4, 4)
    E += 0.18 * blobs(rng, 120, 1.5, 4.0)
    E -= 0.20 * blobs(rng, 160, 1.2, 3.0)
    return to_overlay(E, dark=(0.08, 0.05, 0.03), light=(1.0, 0.95, 0.85))


GEN = {"stone": tex_stone, "wood": tex_wood, "roof": tex_roof, "rock": tex_rock, "grass": tex_grass,
       "plaster": tex_plaster, "dirt": tex_dirt}


def tex_swirl(arm, core):
    """espiral de energia (mesmo desenho do shader do Blender): bracos, nucleo claro, aro brilhante"""
    c = (np.arange(N) + 0.5) / N * 2 - 1
    X, Y = np.meshgrid(c, -c)
    r = np.sqrt(X * X + Y * Y)
    a = np.arctan2(Y, X)
    f = ((a * 3 / (2 * math.pi) + r * 3.2) % 1.0) ** 2.2
    body = (f * 1.1 + 0.25) * (1 - 0.55 * r)
    rim = smoothstep(0.80, 0.98, r) * 1.2
    ctr = smoothstep(0.38, 0.0, r) * 1.3
    t = np.clip(body + rim + ctr, 0, 2.2) / 2.2
    arm = np.array(arm) / 255.0
    core = np.array(core) / 255.0
    dark = arm * 0.62          # vales claros o bastante para ler "energia" na luz do dia (SmoothPlastic no Roblox)
    k = smoothstep(0.10, 0.75, t)[..., None]
    rgb = dark[None, None, :] * (1 - k) + arm[None, None, :] * k
    hk = smoothstep(0.55, 1.0, t)[..., None]
    rgb = rgb * (1 - hk) + core[None, None, :] * hk
    alpha = (1 - smoothstep(0.985, 1.0, r))[..., None]
    return np.concatenate([rgb, alpha], axis=2)


def path(key):
    return os.path.join(TEX_DIR, TEXTURES[key][0])


def swirl_path(mat):
    return os.path.join(TEX_DIR, SWIRL_TEX[mat][0])


def ensure(force=False, out_dir=None):
    """gera o que faltar (deterministico: semente fixa por textura). Retorna {chave: caminho}."""
    global TEX_DIR
    if out_dir:
        TEX_DIR = out_dir
    os.makedirs(TEX_DIR, exist_ok=True)
    done = {}
    for i, (key, (fn, tile)) in enumerate(sorted(TEXTURES.items())):
        p = os.path.join(TEX_DIR, fn)
        if force or not os.path.exists(p):
            rng = np.random.default_rng(1000 + zlib.crc32(key.encode()) % 10000)
            write_png(p, GEN[key](rng))
        done[key] = p
    for mat, (fn, arm, core) in sorted(SWIRL_TEX.items()):
        p = os.path.join(TEX_DIR, fn)
        if force or not os.path.exists(p):
            write_png(p, tex_swirl(arm, core))
        done[mat] = p
    return done


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    r = ensure(force=True, out_dir=out)
    for k, v in r.items():
        print(k, v)
