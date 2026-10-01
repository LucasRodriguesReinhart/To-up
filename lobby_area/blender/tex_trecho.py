# tex_trecho.py - texturas do trecho de amostra (PIL + numpy, python do sistema). Saida: lobby_area/tex_trecho/
# Biblioteca minima: pedra principal, pedra de molduras, pedra sombreada (corpo escuro), ouro, vidro leitoso, piso,
# folhagem dourada (pluma com alpha + tufo), agua e' Terrain no Roblox. Cada material: albedo (+ normal + rugosidade).
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tex_trecho')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

def save(name, arr, mode='RGB'):
    a = np.clip(arr, 0, 1)
    im = Image.fromarray((a * 255 + .5).astype(np.uint8), mode)
    im.save(os.path.join(OUT, name)); print('tex', name, im.size)

def noise(S, cells, seed, octaves=4, persist=.5):
    r = np.random.default_rng(seed); acc = np.zeros((S, S)); amp = 1; tot = 0
    for o in range(octaves):
        c = cells * 2 ** o
        g = r.random((c + 1, c + 1)); g[-1] = g[0]; g[:, -1] = g[:, 0]
        acc += np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC), dtype=np.float32) / 255 * amp
        tot += amp; amp *= persist
    return acc / tot

def normal_from_height(h, strength=2.0):
    dx = np.roll(h, -1, 1) - np.roll(h, 1, 1); dy = np.roll(h, -1, 0) - np.roll(h, 1, 0)
    nx, ny, nz = -dx * strength, dy * strength, np.ones_like(h)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return np.stack([nx / l, ny / l, nz / l], -1) * .5 + .5

def ashlar(S, rows, cols, joint, bevel, seed, stagger=True):
    """fiadas de blocos: devolve (altura 0..1, id do bloco)."""
    rh, bw = S / rows, S / cols
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    row = np.floor(yy / rh); off = np.where((row % 2 == 1) & stagger, bw / 2, 0)
    col = np.floor((xx + off) / bw)
    ey = np.minimum(yy - row * rh, (row + 1) * rh - yy); ex = np.minimum((xx + off) - col * bw, (col + 1) * bw - (xx + off))
    e = np.minimum(ex, ey)
    h = np.clip((e - joint / 2) / bevel, 0, 1); h = h * h * (3 - 2 * h)
    return h, (col * 31 + row * 17 + seed)

def hashf(i, seed):
    v = np.sin(i * 12.9898 + seed * 78.233) * 43758.5453
    return v - np.floor(v)

def stone_set(name, S, base, joint, rows, cols, jw, bev, seed, var=.05, warm=.02, grain=.03, chisel=0.0, rough=(.72, .1)):
    h, bid = ashlar(S, rows, cols, jw, bev, seed)
    base = np.array(base) / 255; jc = np.array(joint) / 255
    v = (hashf(bid, seed) - .5) * 2 * var; w = (hashf(bid, seed + 5) - .5) * 2 * warm
    col = base[None, None, :] * (1 + v[..., None]) + np.stack([w, w * .45, -w * .4], -1)
    big = noise(S, 3, seed + 1, 3) - .5; fine = noise(S, 40, seed + 2, 2) - .5
    col += big[..., None] * .05 + fine[..., None] * grain
    # marcas de talhe: estrias diagonais suaves dentro dos blocos
    if chisel > 0:
        yy, xx = np.mgrid[0:S, 0:S]
        st = (np.sin((xx + yy) * .35 + noise(S, 8, seed + 3) * 6) * .5 + .5) ** 3 * chisel
        col -= st[..., None] * h[..., None]
    col = col * (1 - .05 * (1 - h[..., None]))
    alb = jc[None, None, :] * (1 - h[..., None]) + col * h[..., None]
    save(name + '_albedo.png', alb)
    save(name + '_normal.png', normal_from_height(h * .7 + noise(S, 24, seed + 9, 2) * .06, 2.2))
    r = rough[0] + (noise(S, 12, seed + 4, 2) - .5) * rough[1] + (1 - h) * .1
    save(name + '_rough.png', np.repeat(r[..., None], 3, -1))

# pedra principal (nivel terreo): calcario claro quente, blocos medios
stone_set('pedra_principal', 1024, (206, 196, 178), (170, 160, 144), 8, 4, 6, 16, 21, var=.05, warm=.025, chisel=.03)
# pedra de molduras: marmore claro quase liso, veios suaves
def marble(name, S=1024, base=(232, 226, 214), vein=(196, 188, 176), seed=31):
    n = noise(S, 3, seed, 5, .6); n2 = noise(S, 6, seed + 1, 4, .55)
    veins = np.abs(np.sin((n * 4 + n2 * 2) * math.pi)) ** 14
    b = np.array(base) / 255; vc = np.array(vein) / 255
    alb = b[None, None, :] * (1 - veins[..., None] * .28) + vc[None, None, :] * veins[..., None] * .28
    alb += ((noise(S, 4, seed + 7, 3) - .5) * .03)[..., None]
    alb += (noise(S, 48, seed + 2, 2) - .5)[..., None] * .025
    save(name + '_albedo.png', alb)
    save(name + '_normal.png', normal_from_height(noise(S, 32, seed + 3, 2) * .05, 1.5))
    save(name + '_rough.png', np.repeat((.55 + (noise(S, 10, seed + 4, 2) - .5) * .12)[..., None], 3, -1))
marble('pedra_moldura')
# pedra sombreada: corpo escuro quente (bronze/marrom), blocos grandes com juntas discretas
stone_set('pedra_escura', 1024, (92, 72, 58), (64, 50, 40), 6, 3, 5, 18, 41, var=.06, warm=.03, grain=.035, chisel=.05, rough=(.8, .08))
# piso: lajotas grandes claras, juntas finas, variacao leve
stone_set('piso', 1024, (212, 206, 192), (168, 160, 146), 4, 4, 5, 14, 51, var=.035, warm=.015, grain=.02, rough=(.7, .08))
# ouro: base quente com variacao suave, riscos de escovado, rugosidade baixa
def gold(name, S=512, seed=61):
    n = noise(S, 3, seed, 3); br = noise(S, 64, seed + 1, 1)
    a = np.array((214, 168, 72)) / 255; b = np.array((250, 226, 150)) / 255
    t = np.clip(.35 + (n - .5) * 1.1, 0, 1)
    alb = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    alb += ((br - .5) * .06)[..., None] * np.array([1, .9, .6])[None, None, :]
    save(name + '_albedo.png', alb)
    save(name + '_normal.png', normal_from_height(br * .02, 1.2))
    save(name + '_rough.png', np.repeat((.28 + (br - .5) * .12)[..., None], 3, -1))
    save(name + '_metal.png', np.ones((S, S, 3)))
gold('ouro')
# vidro leitoso da lanterna
def milk(name, S=256, seed=71):
    n = noise(S, 3, seed, 3)
    a = np.array((238, 240, 234)) / 255; b = np.array((255, 254, 246)) / 255
    save(name + '_albedo.png', a[None, None, :] * (1 - n[..., None]) + b[None, None, :] * n[..., None])
    save(name + '_rough.png', np.full((S, S, 3), .35))
milk('vidro_leitoso')

# ---------------- folhagem dourada: PLUMA (card com alpha) ----------------
def plume(name, W=512, H=1024, seed=81, barbs=2600):
    """pluma densa tipo capim-dos-pampas: massa felpuda (silhueta cheia no terco inferior/medio, afinando para a
    ponta) + milhares de fios finos curvos por cima, mais claros nas pontas; alpha fora da massa."""
    r = np.random.default_rng(seed)
    def width_at(t):   # meia-largura da silhueta (fracao de W) em funcao da altura t (0 base, 1 ponta)
        return .44 * math.sin(math.pi * (t * .82 + .1)) ** .8 * (1 - .5 * t) + .02
    cx = W // 2
    # 1) massa: muitos tracos curtos e grossos semi-transparentes -> textura felpuda cheia
    mass = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dm = ImageDraw.Draw(mass)
    for k in range(barbs * 2):
        t = r.random() ** .9
        hw = width_at(t) * W
        u0 = r.random(); x0 = cx + (u0 ** 1.3) * hw * (1 if r.random() < .5 else -1)
        y0 = H * (.03 + .95 * t)
        shade = r.random() * .6 + .2 * (1 - abs(x0 - cx) / max(hw, 1))
        col = (int(188 + 60 * shade), int(140 + 78 * shade), int(50 + 80 * shade), int(90 + 90 * r.random()))
        ang = math.radians(-62 + 20 * r.random() + 30 * t) * (1 if x0 >= cx else -1)
        L = 10 + 26 * (1 - t) * r.random()
        dm.line([(x0, y0), (x0 + math.sin(ang) * L, y0 - math.cos(ang) * L * .6)], fill=col, width=3)
    mass = mass.filter(ImageFilter.GaussianBlur(2.2))
    # 2) espinha
    spine = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(spine)
    for i in range(0, H, 4):
        t = i / H; wdt = 2 + 4 * (1 - t)
        ds.ellipse((cx - wdt, i, cx + wdt, i + 6), fill=(160 + int(50 * t), 115 + int(55 * t), 45 + int(30 * t), 230))
    # 3) fios finos por cima (barbas), pontas claras
    fib = Image.new('RGBA', (W, H), (0, 0, 0, 0)); df = ImageDraw.Draw(fib)
    for k in range(barbs):
        t = r.random() ** .85
        y0 = int(H * (0.03 + .95 * t))
        side = 1 if r.random() < .5 else -1
        length = width_at(t) * W * (.6 + .5 * r.random())
        ang = math.radians(-60 + 30 * r.random() + 28 * t)
        shade = r.random()
        col = (int(206 + 46 * shade), int(160 + 70 * shade), int(66 + 80 * shade), int(140 + 110 * r.random()))
        pts = []
        for s in range(0, 12):
            u = s / 11
            pts.append((cx + side * math.cos(ang) * length * u, y0 - math.sin(ang) * length * u - 22 * u * u))
        df.line(pts, fill=col, width=2 if t < .5 else 1, joint='curve')
        df.line(pts[-3:], fill=(250, 236, 178, 210), width=1)
    out = Image.alpha_composite(Image.alpha_composite(mass, spine), fib)
    out.save(os.path.join(OUT, name + '.png')); print('tex', name, out.size)
plume('pluma_ouro')
plume('pluma_ouro2', seed=83, barbs=2300)

def tuft(name, S=512, seed=91):
    """arbusto dourado da referencia: aglomerado de florzinhas redondas (bolinhas) densas no centro, mais soltas
    na borda, com sombra suave entre elas; alpha fora do aglomerado."""
    r = np.random.default_rng(seed)
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    c = S / 2
    balls = []
    for k in range(420):
        a = r.random() * math.tau; rad = (r.random() ** .6) * S * .44
        x, y = c + math.cos(a) * rad, c + math.sin(a) * rad * .92
        rr = 9 + 13 * r.random() * (1 - rad / (S * .5)) + 4
        balls.append((rad, x, y, rr))
    balls.sort(key=lambda b: -b[0])       # de fora para dentro (as do centro por cima)
    for rad, x, y, rr in balls:
        shade = .35 + .65 * (1 - rad / (S * .48)) * r.random() ** .3
        base = (int(150 + 100 * shade), int(105 + 90 * shade), int(30 + 70 * shade), 255)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(int(base[0] * .72), int(base[1] * .7), int(base[2] * .6), 255))   # sombra
        d.ellipse((x - rr * .82, y - rr * .95, x + rr * .82, y + rr * .65), fill=base)
        d.ellipse((x - rr * .35, y - rr * .7, x + rr * .25, y - rr * .15), fill=(min(255, base[0] + 30), min(255, base[1] + 30), min(255, base[2] + 40), 255))
    out = img.filter(ImageFilter.GaussianBlur(.6))
    out.save(os.path.join(OUT, name + '.png')); print('tex', name, out.size)
tuft('tufo_ouro')
print('done')
