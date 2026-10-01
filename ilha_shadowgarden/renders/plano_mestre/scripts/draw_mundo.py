import math, os
from PIL import Image, ImageDraw, ImageFont
from geo import *

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\ilha_shadowgarden\renders\plano_mestre"
os.makedirs(OUT, exist_ok=True)
F = Fit(100.0, 160.0, 140.0, 120.0)
i1, i2, o3 = i1_polys(), i2_polys(), i3_old_polys()
X0, X1, Z0, Z1 = -2150.0, 800.0, -850.0, 1500.0
S = 0.37
W, H = int((X1 - X0) * S), int((Z1 - Z0) * S)
try:
    FT = ImageFont.truetype("arial.ttf", 15)
    FB = ImageFont.truetype("arialbd.ttf", 20)
    FS = ImageFont.truetype("arial.ttf", 12)
except Exception:
    FT = FB = FS = None
BG = (22, 26, 44)


def P(x, z):
    return ((x - X0) * S, (Z1 - z) * S)


def poly(d, pts, fill=None, outline=None, width=2):
    q = [P(*p) for p in pts]
    d.polygon(q, fill=fill)
    if outline:
        d.line(q + [q[0]], fill=outline, width=width)


def dashed_rect(d, r, col, dash=10):
    x0, z0, x1, z1 = r
    pts = [(x0, z0), (x1, z0), (x1, z1), (x0, z1), (x0, z0)]
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(L / dash)
        for k in range(0, n, 2):
            t0, t1 = k / n, min(1.0, (k + 1) / n)
            d.line([P(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    P(a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=col, width=2)


def arrow(d, p, v, L, col, w=4):
    q = (p[0] + v[0] * L, p[1] + v[1] * L)
    d.line([P(*p), P(*q)], fill=col, width=w)
    a = math.atan2(v[1], v[0])
    for s in (2.6, -2.6):
        r = (q[0] + 28 * math.cos(a + s), q[1] + 28 * math.sin(a + s))
        d.line([P(*q), P(*r)], fill=col, width=w)


def txt(d, x, z, s, col=(235, 235, 245), f=None):
    d.text(P(x, z), s, fill=col, font=f or FT)


def dist_line(d, a, b, label, col=(255, 210, 90)):
    d.line([P(*a), P(*b)], fill=col, width=2)
    txt(d, (a[0] + b[0]) / 2 + 8, (a[1] + b[1]) / 2 + 8, label, col, FS)


def nearest(A, B):
    best = (1e9, None, None)
    for p in A:
        for q in B:
            dd = math.hypot(p[0] - q[0], p[1] - q[1])
            if dd < best[0]:
                best = (dd, p, q)
    return best


def base(d, title):
    # lobby
    poly(d, LOBBY["picos"], fill=(46, 52, 66), outline=(120, 130, 150))
    poly(d, LOBBY["nucleo"], fill=(60, 70, 84), outline=(140, 150, 170))
    poly(d, LOBBY["montanhas"], fill=(84, 96, 88), outline=(160, 180, 160))
    txt(d, -600, 395, "LOBBY - picos do fundo (bbox 1309 x 1118)", (170, 180, 200))
    txt(d, -60, -10, "lobby", (230, 235, 240), FB)
    # ilha 1
    poly(d, i1["rim"], fill=(80, 130, 70), outline=(170, 220, 140))
    poly(d, i1["bridge"], fill=(150, 150, 150))
    poly(d, i1["islet"], fill=(110, 150, 90))
    txt(d, -60, 470, "Ilha 1 Naruto", (240, 250, 230), FB)
    # ilha 2
    poly(d, i2["rim"], fill=(190, 150, 70), outline=(240, 210, 140))
    poly(d, i2["bridge"], fill=(150, 150, 150))
    poly(d, i2["islet"], fill=(200, 170, 90))
    poly(d, i2["arrival"], fill=(150, 150, 150))
    txt(d, -420, 800, "Ilha 2 Dragon Ball", (255, 245, 220), FB)
    d.ellipse([P(A_RBX[0] - 8, A_RBX[1] + 8), P(A_RBX[0] + 8, A_RBX[1] - 8)], fill=(255, 80, 80))
    txt(d, A_RBX[0] + 12, A_RBX[1] - 10, "ancora fixa (-579; 28,2; 651)", (255, 150, 150), FS)
    d.text((14, 10), title, fill=(255, 255, 255), font=FB)
    # rosa e escala
    txt(d, 520, 1300, "+Z", (200, 200, 220)); d.line([P(540, 1180), P(540, 1290)], fill=(200, 200, 220), width=2)
    txt(d, 620, 1200, "+X", (200, 200, 220)); d.line([P(540, 1180), P(650, 1180)], fill=(200, 200, 220), width=2)
    d.line([P(-2100, -800), P(-1600, -800)], fill=(255, 255, 255), width=3)
    txt(d, -2100, -760, "500 studs (vista de cima, Roblox X/Z)", (255, 255, 255), FS)


def antes():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    base(d, "ANTES (export 58cdd0bf)")
    dashed_rect(d, (-1307, 36, -504, 939), (160, 140, 220))
    txt(d, -1300, 960, "bbox da Ilha 3 com ilhotas 803 x 902", (180, 160, 230), FS)
    poly(d, o3["rim"], fill=(90, 80, 140), outline=(190, 170, 255))
    for k in ("bridge", "arrival"):
        poly(d, o3[k], fill=(150, 150, 150))
    poly(d, o3["islet"], fill=(120, 100, 170))
    poly(d, o3["summon"], fill=(120, 100, 170))
    txt(d, -1000, 560, "Ilha 3 atual", (235, 225, 255), FB)
    ap = sg_rbx(*SG.anchor_pos())
    arrow(d, ap, (0.3907, -0.9205), 330, (255, 90, 90))
    txt(d, -660, 60, "portao DS aponta para os picos do lobby", (255, 120, 120))
    dd, p, q = nearest(o3["rim"], i2["rim"])
    dist_line(d, p, q, "%.0f" % dd)
    dd, p, q = nearest(o3["rim"], [c for c in LOBBY["picos"]] + [(-650.0, z) for z in range(-700, 409, 10)] + [(x, 408.0) for x in range(-650, 661, 10)])
    dist_line(d, p, q, "%.0f ate a bbox dos picos" % dd)
    return im


def depois():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    base(d, "DEPOIS (plano v4: giro 100, ponte 232, saida NO)")
    P3 = F.polys()
    poly(d, P3["arrival"], fill=(170, 170, 180))
    poly(d, P3["rim"], fill=(90, 80, 140), outline=(190, 170, 255))
    poly(d, P3["summon"], fill=(120, 100, 170))
    poly(d, P3["exit_bridge"], fill=(170, 170, 180))
    poly(d, P3["islet"], fill=(200, 80, 80))
    # castelo em planta
    poly(d, [F.rbx(*p) for p in rect(-104, 60, 104, 274)], fill=(50, 44, 80), outline=(210, 190, 255))
    poly(d, [F.rbx(*p) for p in rect(*CROWN_BASE)], fill=(50, 44, 80), outline=(210, 190, 255))
    c = F.rbx(0, 140)
    txt(d, c[0] - 60, c[1] + 60, "castelo 2x", (235, 225, 255), FS)
    txt(d, -1480, 560, "Ilha 3 nova (sem ilhotas)", (235, 225, 255), FB)
    a4, d4 = F.anchor4()
    arrow(d, a4, d4, 260, (255, 90, 90))
    c4 = (a4[0] + d4[0] * 350, a4[1] + d4[1] * 350)
    q = [P(*p) for p in circle(c4, 300, 48)]
    d.line(q + [q[0]], fill=(255, 120, 120), width=2)
    txt(d, c4[0] - 150, c4[1] + 10, "espaco da area 4 (r 300)", (255, 150, 150))
    txt(d, a4[0] - 10, a4[1] - 40, "ancora area 4 (-1533; 52,2; 963)", (255, 150, 150), FS)
    # distancias
    dd, p, q_ = nearest(P3["rim"], i2["rim"]); dist_line(d, p, q_, "%.0f ate a Ilha 2" % dd)
    dd, p, q_ = nearest(P3["rim"], [(-650.0, z) for z in range(-700, 409, 8)] + [(x, 408.0) for x in range(-650, 661, 8)])
    dist_line(d, p, q_, "%.0f ate os picos" % dd)
    dd, p, q_ = nearest(P3["rim"], i1["rim"]); dist_line(d, p, q_, "%.0f ate a Ilha 1" % dd)
    # radial
    d.line([P(*LOBBY_C), P(a4[0], a4[1])], fill=(120, 120, 150), width=1)
    txt(d, -300, 520, "radial lobby -> saida (desvio 3 graus)", (150, 150, 180), FS)
    return im


a, b = antes(), depois()
im = Image.new("RGB", (W * 2 + 20, H), (10, 10, 16))
im.paste(a, (0, 0))
im.paste(b, (W + 20, 0))
im.save(os.path.join(OUT, "mundo.png"))
print("mundo.png", im.size)
