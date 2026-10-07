# fm_mat_textures - texturas estilizadas TILEAVEIS geradas por codigo (numpy puro + PNG via zlib).
# Roda dentro do Blender (numpy embutido) ou no Python do sistema:  python fm_mat_textures.py [pasta]
#
# Sao texturas de DETALHE em overlay (RGBA): RGB quase preto (escurece) ou quase branco (clareia) e o ALPHA
# e a forca. A cor de fundo vem da variante do material (Stone_Light_B, Wood_Dark_C...), entao UMA textura
# serve para todas as variantes da familia:
#   Blender : base_color = mix(cor_variante, tex.rgb, tex.alpha)          (fm_lib.make_materials)
#   Roblox  : SurfaceAppearance.AlphaMode = Overlay -> mesma formula sobre MeshPart.Color (montar_lobby_forja.lua)
# As UVs sao projecao planar alinhada a cada primitiva, em studs / TILE (fm_lib.MB), e vao no FBX.
# Espirais dos portais (v4): PNG RGBA 1024 por portal, ALFA 0 fora do circulo, desenho e paleta PROPRIOS por
# portal (SWIRL_SPEC). A MESMA imagem e usada no Blender (fm_lib: shader da espiral = esta textura em coordenadas
# do objeto), no FBX (UV do disco, export_roblox.py) e no SurfaceGui do export_vfx.py (T_swirl_<key>_v4.png).
import os, math, zlib, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "textures")
N = 512
VERSION = 3
SWIRL_VERSION = 4          # nome novo a cada mudanca de desenho: o 3D Importer reimporta do cache se o nome repete
SWIRL_N = 1024

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
# espirais: material -> desenho do portal (cores sRGB 0-255). Regras comuns: base escura e saturada, bracos finos e
# brilhantes (<= 25% do periodo, luminancia <= 85%), aro mais claro que tudo, nucleo pequeno, ruido de rastro.
# twist = voltas por raio (3..7, diferente em cada portal); width = largura do braco em fracao do periodo.
SWIRL_SPEC = {
    "P_Naruto_Swirl": dict(key="naruto", portal="Naruto", border=(45, 12, 0), arm=(255, 115, 20),
                           core=(255, 210, 90), arms=3, twist=3.4, width=0.20, style="leaf", seed=11),
    "P_DB_Swirl":     dict(key="db", portal="DragonBall", border=(60, 35, 0), arm=(255, 195, 30),
                           core=(255, 245, 205), arms=4, twist=4.2, width=0.17, style="ki", seed=23),
    "P_Shadow_Swirl": dict(key="shadow", portal="ShadowGarden", border=(10, 0, 20), arm=(150, 60, 255),
                           core=(220, 170, 255), arms=5, twist=5.6, width=0.12, style="stars", seed=37),
    "P_DS_Swirl":     dict(key="ds", portal="DemonSlayer", border=(25, 0, 0), arm=(185, 12, 22),
                           core=(255, 110, 40), arms=2, twist=3.0, width=0.36, style="fire", seed=41),
    "P_OP_Swirl":     dict(key="op", portal="OnePiece", border=(0, 15, 45), arm=(25, 105, 255),
                           core=(150, 215, 255), arms=4, twist=4.8, width=0.21, style="foam", seed=53),
    "P_OPM_Swirl":    dict(key="opm", portal="OnePunchMan", border=(0, 20, 35), arm=(0, 225, 255),
                           core=(225, 255, 255), arms=6, twist=6.6, width=0.10, style="cracks", seed=67),
}
# compatibilidade (export_roblox / export_vfx): material -> (arquivo, cor dos bracos sRGB, cor do nucleo sRGB)
SWIRL_TEX = {m: ("T_swirl_%s_v%d.png" % (s["key"], SWIRL_VERSION), s["arm"], s["core"])
             for m, s in SWIRL_SPEC.items()}
# portal (fm_layout.PORTAL_KEYS) -> material da espiral
SWIRL_BY_PORTAL = {s["portal"]: m for m, s in SWIRL_SPEC.items()}


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


# ------------------------------------------------------------------ espirais dos portais (v4)
def _grid_noise(rng, gx, gy):
    """amostrador de value noise periodico (gx x gy celulas) em coordenadas arbitrarias (u em celulas, v em celulas)"""
    g = rng.random((gy, gx))

    def at(u, v):
        x0 = np.floor(u)
        y0 = np.floor(v)
        fx = u - x0
        fy = v - y0
        sx = fx * fx * (3 - 2 * fx)
        sy = fy * fy * (3 - 2 * fy)
        x0 = x0.astype(int) % gx
        y0 = y0.astype(int) % gy
        x1 = (x0 + 1) % gx
        y1 = (y0 + 1) % gy
        top = g[y0, x0] + (g[y0, x1] - g[y0, x0]) * sx
        bot = g[y1, x0] + (g[y1, x1] - g[y1, x0]) * sx
        return top + (bot - top) * sy
    return at


def _luma(c):
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def _cap_luma(c, lim):
    """escala a cor para a luminancia (Rec.709 sobre sRGB) nao passar de lim"""
    L = _luma(c)
    k = np.where(L > lim, lim / np.maximum(L, 1e-6), 1.0)
    return c * k[..., None]


def _mix(a, b, t):
    t = np.asarray(t)[..., None]
    return a * (1 - t) + b * t


def tex_swirl(spec, n=None):
    """espiral de energia de UM portal (desenho proprio): base escura e saturada, bracos finos com rastro,
    detalhe tematico (style), nucleo pequeno e aro mais claro que tudo; alfa 0 fora do circulo."""
    n = n or SWIRL_N
    rng = np.random.default_rng(spec.get("seed", 1))
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)                     # linha 0 = topo (Y = +1), mesma convencao das UVs (v = cima)
    r = np.sqrt(X * X + Y * Y)
    th = np.arctan2(Y, X)
    B = np.array(spec["border"], float) / 255.0
    A = np.array(spec["arm"], float) / 255.0
    C = np.array(spec["core"], float) / 255.0
    na, tw, w = spec["arms"], spec["twist"], spec["width"]
    style = spec.get("style")
    # ---- base: borda escura e saturada, interior um pouco aceso pela cor do braco
    inner = np.clip(1 - r, 0, 1)
    rgb = B[None, None, :] * (1.0 + 1.0 * inner[..., None]) + A[None, None, :] * (0.08 * inner ** 2)[..., None]
    # rastro difuso (streaks ao longo da espiral) tambem na base
    nz_s = _grid_noise(rng, 48 * na, 6)
    nz_w = _grid_noise(rng, 7, 5)
    warp = (nz_w(th / (2 * math.pi) * 7, r * 5) - 0.5) * 0.10
    ph = na * th / (2 * math.pi) + tw * r + warp
    streak = nz_s(ph * 48, r * 6)
    rgb = rgb + A[None, None, :] * (0.10 * smoothstep(0.55, 0.95, streak) * smoothstep(0.12, 0.35, r)
                                    * (1 - smoothstep(0.80, 0.92, r)))[..., None]
    # ---- bracos: borda de ataque nitida, rastro suave, linha central clara; mais finos perto do centro
    f = ph % 1.0
    s = f - 0.5
    wl = w * (0.55 + 0.55 * np.clip(r, 0, 1))
    if style == "fire":                            # linguas de fogo: largura ondulante
        fl = _grid_noise(rng, 2 * na * 3, 9)
        wl = wl * (0.65 + 0.7 * fl(ph * 6, r * 9))
    if style == "fire":                            # lingua larga de topo chato
        lead = np.exp(-(np.maximum(s, 0) / (wl * 0.45)) ** 4)
        trail = np.exp(-(np.maximum(-s, 0) / (wl * 0.95)) ** 2)
        line = np.exp(-(s / (wl * 0.28)) ** 2)
    else:
        lead = np.exp(-(np.maximum(s, 0) / (wl * 0.30)) ** 2)
        trail = np.exp(-(np.maximum(-s, 0) / (wl * 0.85)) ** 2)
        line = np.exp(-(s / (wl * 0.12)) ** 2)
    arm_i = np.where(s >= 0, lead, trail)
    env = smoothstep(0.08, 0.24, r) * (1 - smoothstep(0.83, 0.93, r))
    arm_i = arm_i * env * (0.72 + 0.28 * streak)
    line = line * env
    A_hi = _cap_luma(_mix(A[None, None, :], C[None, None, :], 0.35 * np.ones_like(r)), 0.85)
    A_c = _cap_luma(A[None, None, :] * np.ones_like(rgb), 0.85)
    rgb = _mix(rgb, A_c, np.clip(arm_i, 0, 1))
    rgb = _mix(rgb, A_hi, np.clip(line * 0.8, 0, 1))
    # ---- detalhe tematico
    if style == "leaf":
        # espiral de Konoha: um traco unico (Arquimedes) saindo do nucleo, 1,6 volta, afinando
        phi = (th - 0.6) % (2 * math.pi)
        best = np.full_like(r, 9.0)
        for k in range(3):
            rr = 0.045 * (phi + 2 * math.pi * k)
            ok = (phi + 2 * math.pi * k) <= 1.6 * 2 * math.pi
            d = np.where(ok, np.abs(r - rr), 9.0)
            best = np.minimum(best, d)
        thick = 0.022 * (1 - np.clip(r / 0.48, 0, 1)) + 0.006
        m = np.exp(-(best / thick) ** 2) * (1 - smoothstep(0.40, 0.50, r))
        col = _cap_luma(_mix(A[None, None, :], C[None, None, :], 0.5 * np.ones_like(r)), 0.85)
        rgb = _mix(rgb, col, np.clip(m, 0, 1))
    elif style == "ki":
        # raios de ki: tracos radiais retos, mais fortes perto do aro
        ray = np.zeros_like(r)
        for i in range(30):
            a0 = rng.uniform(-math.pi, math.pi)
            r0, r1 = rng.uniform(0.28, 0.62), rng.uniform(0.78, 0.93)
            wid = rng.uniform(0.004, 0.009)
            da = np.angle(np.exp(1j * (th - a0)))
            d = np.abs(da) * r
            m = np.exp(-(d / wid) ** 2) * smoothstep(r0, r0 + 0.12, r) * (1 - smoothstep(r1 - 0.04, r1, r))
            ray = np.maximum(ray, m * rng.uniform(0.55, 1.0))
        col = _cap_luma(_mix(A[None, None, :], C[None, None, :], 0.45 * np.ones_like(r)), 0.85)
        rgb = _mix(rgb, col, np.clip(ray, 0, 1))
    elif style == "stars":
        # pontos de estrela: brilhos de 4 pontas espalhados
        st = np.zeros_like(r)
        for i in range(70):
            rr = math.sqrt(rng.uniform(0.03, 0.78))
            aa = rng.uniform(-math.pi, math.pi)
            cx, cy = rr * math.cos(aa), rr * math.sin(aa)
            sz = rng.uniform(0.6, 1.4)
            dx, dy = np.abs(X - cx), np.abs(Y - cy)
            m = (np.exp(-(dx / (0.0035 * sz)) ** 2 - (dy / (0.020 * sz)) ** 2) +
                 np.exp(-(dx / (0.020 * sz)) ** 2 - (dy / (0.0035 * sz)) ** 2) +
                 np.exp(-((dx * dx + dy * dy) / (0.0065 * sz) ** 2)))
            st = np.maximum(st, np.clip(m, 0, 1) * rng.uniform(0.5, 1.0))
        col = _cap_luma(_mix(A[None, None, :], C[None, None, :], 0.75 * np.ones_like(r)), 0.85)
        rgb = _mix(rgb, col, np.clip(st, 0, 1))
    elif style == "fire":
        # nucleo das linguas mais quente (crimson na borda, laranja no meio) + anel negro antes do aro
        hot = np.clip(line * 1.2 + arm_i * 0.35 - 0.2, 0, 1)
        rgb = _mix(rgb, _cap_luma(C[None, None, :] * np.ones_like(rgb), 0.85), hot * 0.85)
        ring = np.exp(-((r - 0.865) / 0.030) ** 2)
        rgb = rgb * (1 - 0.94 * ring)[..., None]
    elif style == "foam":
        # cristas de espuma: tracos claros na borda de ataque de cada braco
        dash = _grid_noise(rng, 14 * na, 8)
        edge = np.exp(-((s - wl * 0.28) / (wl * 0.16)) ** 2) * env
        m = edge * smoothstep(0.42, 0.62, dash(ph * 14, r * 8))
        col = np.array([185, 225, 250], float)[None, None, :] / 255.0 * np.ones_like(rgb)
        rgb = _mix(rgb, _cap_luma(col, 0.85), np.clip(m * 1.1, 0, 1))
    elif style == "cracks":
        # rachaduras eletricas: raios quebrados do centro para fora (com galhos) + brilho em volta
        E = np.zeros((n, n))
        G = np.zeros((n, n))
        for i in range(7):
            ang = 2 * math.pi * i / 7 + rng.uniform(-0.3, 0.3)
            x = n / 2 + math.cos(ang) * n * 0.08
            y = n / 2 - math.sin(ang) * n * 0.08
            ln = n * rng.uniform(0.26, 0.36)
            sd = int(rng.integers(0, 1 << 30))
            crack(G, np.random.default_rng(sd), x, y, -ang, ln, 0.35, 5.0 * n / 512, 0.16, branch=1.2, n=n)
            crack(E, np.random.default_rng(sd), x, y, -ang, ln, 1.0, 1.0 * n / 512, 0.16, branch=1.2, n=n)
        cut = smoothstep(0.10, 0.20, r) * (1 - smoothstep(0.84, 0.91, r))
        glow_c = _cap_luma(_mix(A[None, None, :], C[None, None, :], 0.2 * np.ones_like(r)), 0.85)
        rgb = _mix(rgb, glow_c, np.clip(-G, 0, 1) * cut)
        rgb = _mix(rgb, _cap_luma(C[None, None, :] * np.ones_like(rgb), 0.85), np.clip(-E, 0, 1) * cut)
    # ---- nucleo pequeno (quente/claro) + halo
    halo = np.exp(-(r / 0.17) ** 2) * 0.55
    rgb = _mix(rgb, _cap_luma(_mix(A[None, None, :], C[None, None, :], 0.6 * np.ones_like(r)), 0.9), halo)
    core = np.exp(-(r / 0.075) ** 2)
    rgb = _mix(rgb, C[None, None, :] * np.ones_like(rgb), core)
    # ---- aro: o mais claro de tudo (linha fina + brilho para dentro)
    RC = np.clip(C * 0.5 + 0.5, 0, 1)
    rim = np.exp(-((r - 0.955) / 0.024) ** 2)
    glow = np.exp(-((r - 0.955) / 0.075) ** 2) * 0.40 * (r < 0.955)
    rgb = _mix(rgb, _mix(A[None, None, :], RC[None, None, :], 0.5 * np.ones_like(r)), np.clip(glow, 0, 1))
    rgb = _mix(rgb, RC[None, None, :] * np.ones_like(rgb), np.clip(rim * 1.15, 0, 1))
    rgb = np.where((r > 0.955)[..., None], _mix(rgb, RC[None, None, :] * np.ones_like(rgb), 0.85 * np.ones_like(r)),
                   rgb)
    alpha = (1 - smoothstep(0.985, 1.0, r))[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), alpha], axis=2)


def swirl_stats(img):
    """metricas de QA da espiral: luminancia media, maxima dos bracos e do aro (dentro do circulo)"""
    n = img.shape[0]
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)
    r = np.sqrt(X * X + Y * Y)
    L = _luma(img[..., :3])
    body = (r > 0.2) & (r < 0.85)
    rim = (r > 0.94) & (r < 0.97)
    return dict(mean=float(L[r < 0.98].mean()), body_max=float(L[body].max()), rim=float(L[rim].mean()),
                body_p95=float(np.percentile(L[body], 95)))


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
            write_png(p, tex_swirl(SWIRL_SPEC[mat]))
        done[mat] = p
    return done


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    r = ensure(force=True, out_dir=out)
    for k, v in r.items():
        print(k, v)
    for m, spec in SWIRL_SPEC.items():
        st = swirl_stats(tex_swirl(spec, 256))
        print("%-16s %-12s bracos=%d twist=%.1f  lum media=%.2f bracos max=%.2f aro=%.2f" % (
            m, spec["portal"], spec["arms"], spec["twist"], st["mean"], st["body_max"], st["rim"]))
