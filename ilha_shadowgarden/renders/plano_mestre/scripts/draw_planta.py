import math, os
from PIL import Image, ImageDraw, ImageFont
from geo import *

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\ilha_shadowgarden\renders\plano_mestre"
X0, X1, Y0, Y1 = -260.0, 330.0, -380.0, 470.0
S = 2.0
W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)
FT = ImageFont.truetype("arial.ttf", 14)
FB = ImageFont.truetype("arialbd.ttf", 17)
FS = ImageFont.truetype("arial.ttf", 11)
im = Image.new("RGB", (W, H), (20, 26, 48))
d = ImageDraw.Draw(im, "RGBA")


def P(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


def poly(pts, fill=None, outline=None, width=2):
    q = [P(*p) for p in pts]
    d.polygon(q, fill=fill)
    if outline:
        d.line(q + [q[0]], fill=outline, width=width)


def R(x0, y0, x1, y1, fill=None, outline=None, width=2):
    poly(rect(x0, y0, x1, y1), fill, outline, width)


def C(c, r, fill=None, outline=None, width=2):
    d.ellipse([P(c[0] - r, c[1] + r), P(c[0] + r, c[1] - r)], fill=fill, outline=outline, width=width)


def T(x, y, s, col=(240, 240, 250), f=None):
    d.text(P(x, y), s, fill=col, font=f or FT)


def dashed(pts, col, w=2, dash=6.0, closed=True):
    pts = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / dash))
        for k in range(0, n, 2):
            t0, t1 = k / n, min(1.0, (k + 1) / n)
            d.line([P(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    P(a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=col, width=w)


def arrow_path(pts, col, w=3):
    d.line([P(*p) for p in pts], fill=col, width=w)
    a, b = pts[-2], pts[-1]
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (2.6, -2.6):
        d.line([P(*b), P(b[0] + 7 * math.cos(ang + s), b[1] + 7 * math.sin(ang + s))], fill=col, width=w)


# ilha e patamares
poly(RIM, fill=(64, 66, 86), outline=(12, 12, 20), width=3)
poly(P1_POLY, fill=(112, 116, 134), outline=(30, 30, 40))
poly(P2_POLY, fill=(132, 136, 154), outline=(30, 30, 40))
poly(P3_POLY, fill=(160, 162, 180), outline=(30, 30, 40))
R(*ENTRY_LOW, fill=(96, 100, 116), outline=(30, 30, 40))
R(*ENTRY_HIGH, fill=(112, 116, 134), outline=(30, 30, 40))
T(-150, -236, "P1 36,2", (255, 255, 255), FB); T(-170, -140, "P2 44,2", (255, 255, 255), FB)
T(-150, 10, "P3 52,2", (20, 20, 30), FB)
# ponte de chegada (so o fim) e sumario
d.rectangle([P(-9, -334), P(9, -380)], fill=(150, 150, 160))
T(14, -372, "ponte de chegada 232 (curva de 33 graus) -> ancora da Ilha 2", (220, 220, 230), FS)
# ruas
for pts, w in STREETS:
    poly(ribbon(pts, w / 2), fill=(196, 196, 208))
# praca e fonte
C(PLAZA_C, PLAZA_R, fill=(170, 170, 184), outline=(50, 50, 60))
C(PLAZA_C, FOUNTAIN_R, fill=(60, 110, 190), outline=(20, 40, 80))
T(14, -212, "praca R32 + fonte R9 (agua Roblox)", (20, 20, 30), FS)
# summon
a, b, w = SUMMON_BRIDGE
poly(ribbon([a, b], w / 2), fill=(200, 200, 212))
C(SUMMON_C, SUMMON_R, fill=(130, 110, 170), outline=(60, 40, 90))
R(-222, -229, -210, -215, fill=(150, 90, 230))
T(-250, -256, "INVOCACAO (SUM 40,2)", (240, 230, 255), FS)
# escadas
for nm, foot, deg, w, n, tread in STAIRS:
    aa = math.radians(deg)
    top = (foot[0] + math.cos(aa) * tread * n, foot[1] + math.sin(aa) * tread * n)
    poly(ribbon([foot, top], w / 2), fill=(255, 255, 255), outline=(60, 60, 60))
# muralha + portao
R(-176, WALL_Y[0], 176, WALL_Y[1], fill=(46, 46, 62))
R(-12, WALL_Y[0], 12, WALL_Y[1], fill=(196, 196, 208))
R(143, WALL_Y[0], 157, WALL_Y[1], fill=(196, 196, 208))
for x in (-24, 24):
    C((x, -18), 12, fill=(46, 46, 62))
T(30, -34, "muralha h 24 / portao 24 x 32", (20, 20, 30), FS)
# casas
col = {"A": (190, 120, 70), "B": (210, 90, 60), "C": (160, 130, 90)}
for nm, tp, x, y, w, dd, face, z in HOUSES:
    ang = math.radians(face)
    fx, fy = math.cos(ang), math.sin(ang)
    lx, ly = -fy, fx
    hw, hd = w / 2, dd / 2
    corners = [(x + lx * sx * hw + fx * sy * hd, y + ly * sx * hw + fy * sy * hd) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    # lote
    lot = [(x + lx * sx * (hw + 8) + fx * sy * (hd + 7), y + ly * sx * (hw + 8) + fy * sy * (hd + 7)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    dashed(lot, (90, 160, 90), 1, 4)
    poly(corners, fill=col[tp], outline=(40, 20, 10))
    door = (x + fx * hd, y + fy * hd)
    d.line([P(door[0] - lx * 3.5, door[1] - ly * 3.5), P(door[0] + lx * 3.5, door[1] + ly * 3.5)], fill=(255, 230, 120), width=5)
    T(x - 12, y + 6, "%s %s" % (nm, tp), (255, 255, 255), FB)
    T(x - 12, y - 4, "%dx%d" % (w, dd), (255, 255, 255), FS)
# craft + mirante leste
C(CRAFT_C, CRAFT_R, fill=(90, 70, 140), outline=(200, 160, 255))
T(CRAFT_C[0] - 22, CRAFT_C[1] - 22, "ALQUIMIA", (255, 255, 255), FS)
C((178, -80), 10, fill=(90, 150, 110), outline=(30, 60, 40))
T(150, -100, "mirante leste (antiga saida)", (20, 20, 30), FS)
# patio / jardim
dashed(rect(*FORECOURT), (60, 120, 60), 2)
R(-86, 0, -24, 48, fill=(70, 120, 70, 140))
R(24, 0, 86, 48, fill=(70, 120, 70, 140))
R(-60, 8, -40, 40, fill=(60, 100, 180, 160)); R(40, 8, 60, 40, fill=(60, 100, 180, 160))
C((-74, 24), 7, fill=(30, 70, 40)); C((74, 24), 7, fill=(30, 70, 40))
T(-96, -8, "patio-jardim: eixo 20 + 2 gramados rebaixados, 2 espelhos d'agua, 2 arvores-marco", (20, 60, 20), FS)
# castelo
R(-104, 60, 104, 274, fill=(46, 42, 74), outline=(210, 190, 255), width=3)
R(*HALL, fill=(92, 88, 120), outline=(200, 190, 240))
for x in (-ARCADE_X, ARCADE_X):
    for k in range(9):
        yy = 66 + 12 + k * 22.5
        R(x - 2, yy - 3, x + 2, yy + 3, fill=(40, 36, 60))
d.rectangle([P(MINE[0], MINE[3]), P(MINE[2], MINE[1])], outline=(255, 200, 0), width=3)
T(MINE[0] + 4, MINE[3] - 4, "MiningZone 104 x 136 (~90 minerios)", (255, 220, 60), FB)
R(-8, 60, 8, 96, fill=(220, 220, 235, 120))
R(-14, 52, 14, 66, fill=(220, 220, 235))
T(18, 58, "PORTA 28 x 34 (timpano ate 46)", (255, 255, 255), FS)
T(-90, 250, "SALAO 184 x 196 x 84", (255, 255, 255), FB)
T(70, 236, "naves", (230, 230, 245), FS); T(70, 228, "laterais 24", (230, 230, 245), FS)
for x, y, r in FRONT_TOWERS:
    C((x, y), r, fill=(46, 42, 74), outline=(200, 170, 255), width=3)
R(*CROWN_BASE, fill=(46, 42, 74), outline=(220, 190, 255), width=3)
R(*CHANCEL, fill=(110, 96, 150), outline=(220, 200, 255))
R(-7, 289, 7, 299, fill=(170, 90, 255))
R(20.5, 288, 35, 300, fill=(120, 60, 180, 160))
arrow_path([(8, 294), (26, 294)], (255, 90, 255), 3)
T(40, 300, "TRONO desliza 27,5 p/ o bolso leste", (255, 220, 255), FS)
C(STAIR_C, STAIR_R_OUT, fill=(30, 24, 48), outline=(255, 150, 255), width=3)
C(STAIR_C, STAIR_R_IN, fill=(120, 110, 150))
C(STAIR_C, 3, fill=(30, 24, 48))
T(-150, 330, "ESCADA CARACOL (r int 14, 2 voltas, -48)", (255, 200, 255), FS)
# salao sombrio e salas (tracejado)
dashed(rect(*CAVE), (80, 200, 255), 3, 8)
T(40, 352, "SALAO SOMBRIO (subsolo) 180 x 248", (120, 210, 255), FS); T(40, 342, "piso -12 / galeria 6,6 / abobada 46", (120, 210, 255), FS)
C(CAVE_PORTAL, 13, outline=(80, 200, 255), width=3)
T(-90, 108, "portal da masmorra -> (piso -12)", (120, 210, 255), FS)
for nm, (a, b, c2, e) in DUN_ROOMS:
    dashed(rect(a, b, c2, e), (255, 110, 180), 2, 5)
    T(c2 - 24, e - 12, nm, (255, 140, 200), FB)
T(-248, 150, "salas da masmorra (tracejado rosa)", (255, 140, 200), FS)
T(-248, 138, "piso -72, sob o salao sombrio", (255, 140, 200), FS)
# saida NO
ux, uy = exit_dir_local(120.0)
ep = [EXIT_START, (EXIT_START[0] + ux * 64, EXIT_START[1] + uy * 64)]
poly(ribbon(ep, 9), fill=(200, 200, 212))
isc = (EXIT_START[0] + ux * 82, EXIT_START[1] + uy * 82)
C(isc, 22, fill=(150, 60, 60), outline=(255, 120, 120))
T(isc[0] - 60, isc[1] + 30, "PORTAO DEMON SLAYER (area 4)", (255, 160, 160), FB)
arrow_path([(isc[0] + ux * 20, isc[1] + uy * 20), (isc[0] + ux * 60, isc[1] + uy * 60)], (255, 90, 90), 4)
# mirante / jardim leste
C(MIRANTE_E, 16, fill=(70, 120, 80), outline=(30, 60, 40))
T(MIRANTE_E[0] - 20, MIRANTE_E[1] + 26, "jardim-mirante", (20, 60, 20), FS)
T(MIRANTE_E[0] - 20, MIRANTE_E[1] + 16, "(ex-masmorra)", (20, 60, 20), FS)
# rotas
arrow_path([(0, -334), (0, -268), (0, -254)], (255, 80, 80), 3)
arrow_path([(0, -190), (0, -150), (0, -40), (0, -13), (0, 60), (0, 96), (0, 230), (0, 286)], (255, 80, 80), 3)
arrow_path(EXIT_ROUTE + [EXIT_START], (255, 150, 60), 3)
arrow_path([(0, -86), (60, -86), (94, -86)], (255, 150, 60), 2)
arrow_path([(-32, -222), (-166, -222), (-190, -222)], (255, 150, 60), 2)
arrow_path([(150, -40), (150, 40), (136, 120), (130, 150)], (255, 150, 60), 2)
# legenda
lx0, ly0 = 190, 440
d.rectangle([P(lx0 - 6, ly0 + 6), P(lx0 + 136, ly0 - 118)], fill=(10, 12, 24, 220))
items = [((255, 80, 80), "rota principal"), ((255, 150, 60), "rotas secundarias"), ((80, 200, 255), "salao sombrio (subsolo)"),
         ((255, 110, 180), "salas da masmorra"), ((255, 200, 0), "MiningZone"), ((190, 120, 70), "casa A (2 andares)"),
         ((210, 90, 60), "casa B taverna"), ((160, 130, 90), "casa C terrea"), ((255, 230, 120), "porta aberta (vao)")]
for i, (c, s) in enumerate(items):
    yy = ly0 - 4 - i * 12.5
    d.rectangle([P(lx0, yy), P(lx0 + 8, yy - 6)], fill=c)
    T(lx0 + 12, yy + 1, s, (230, 230, 240), FS)
d.text((12, 8), "PLANTA NOVA - Ilha 3 v4 (local: +Y castelo, +X leste). 1 quadrado = 50 studs", fill=(255, 255, 255), font=FB)
for gx in range(-250, 331, 50):
    d.line([P(gx, Y0), P(gx, Y0 + 6)], fill=(200, 200, 220), width=1)
    T(gx - 8, Y0 + 16, str(gx), (180, 180, 200), FS)
for gy in range(-350, 451, 50):
    d.line([P(X0, gy), P(X0 + 6, gy)], fill=(200, 200, 220), width=1)
    T(X0 + 8, gy + 6, str(gy), (180, 180, 200), FS)
im.save(os.path.join(OUT, "planta_ilha.png"))
print(im.size)
