import math, os
from PIL import Image, ImageDraw, ImageFont
from geo import *

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\ilha_shadowgarden\renders\plano_mestre"
Y0, Y1, Z0, Z1 = -70.0, 420.0, -125.0, 395.0
S = 2.6
W, H = int((Y1 - Y0) * S), int((Z1 - Z0) * S)
FT = ImageFont.truetype("arial.ttf", 15)
FB = ImageFont.truetype("arialbd.ttf", 18)
FS = ImageFont.truetype("arial.ttf", 12)
im = Image.new("RGB", (W, H), (26, 30, 56))
d = ImageDraw.Draw(im, "RGBA")


def P(y, z):
    return ((y - Y0) * S, (Z1 - z) * S)


def R(y0, z0, y1, z1, fill=None, outline=None, w=2):
    d.rectangle([P(y0, z1), P(y1, z0)], fill=fill, outline=outline, width=w)


def poly(pts, fill=None, outline=None, w=2):
    q = [P(*p) for p in pts]
    d.polygon(q, fill=fill)
    if outline:
        d.line(q + [q[0]], fill=outline, width=w)


def T(y, z, s, col=(240, 240, 250), f=None):
    d.text(P(y, z), s, fill=col, font=f or FT)


def man(y, z, col=(255, 255, 255)):
    d.line([P(y, z), P(y, z + 3.2)], fill=col, width=3)
    d.ellipse([P(y - 0.9, z + 5.2), P(y + 0.9, z + 3.4)], fill=col)


ROCK = (70, 64, 92)
# mar e rede
R(Y0, Z0, Y1, -111, fill=(24, 60, 100))
T(Y0 + 4, -114, "mar (FAR_GROUND) -111", (150, 190, 230), FS)
d.line([P(Y0, -100), P(Y1, -100)], fill=(255, 120, 120), width=1)
T(Y0 + 120, -94, "VOID_CATCH novo em -100 (hoje -40: cortaria as salas)", (255, 150, 150), FS)
# massa da ilha (corte no eixo)
isl = [(-70, 44.2), (-23, 44.2), (-23, 52.2), (384, 52.2), (388, 30), (380, -10), (350, -60), (310, -92), (160, -108),
       (20, -100), (-30, -80), (-60, -40), (-70, 0)]
poly(isl, fill=ROCK, outline=(30, 26, 40))
T(-60, 48, "P2 44,2", (255, 255, 255), FS)
T(0, 56, "P3 52,2", (255, 255, 255), FS)
# muralha
R(-23, 52.2, -13, 76.2, fill=(60, 58, 80), outline=(20, 20, 30))
R(-23, 44.2, -13, 76.2, outline=(20, 20, 30))
T(-58, 90, "muralha 24 / portao 24 x 32", (220, 220, 240), FS)
# torre da fachada (fora do plano, silhueta)
poly([(52, 52.2), (92, 52.2), (92, 214), (72, 279), (52, 214)], fill=(60, 56, 90, 110), outline=(120, 110, 170))
T(40, 284, "torres da fachada x +-120 (fora do corte): 214 / agulha 279", (200, 190, 240), FS)
# nave
R(60, 52.2, 66, 136.2 + 8, fill=(56, 52, 84), outline=(20, 20, 30))          # fachada
R(262, 52.2, 267, 136.2 + 8, fill=(56, 52, 84), outline=(20, 20, 30))
R(66, 136.2, 262, 144.2, fill=(56, 52, 84))
poly([(60, 144.2), (160, 228), (267, 144.2)], fill=(44, 40, 70), outline=(20, 20, 30))
R(66, 52.2, 262, 136.2, fill=(118, 112, 150))
R(60, 52.2, 66, 86.2, fill=(118, 112, 150))                                  # vao da porta 34
poly([(60, 86.2), (63, 98.2), (66, 86.2)], fill=(90, 80, 120))
T(70, 60, "PORTA 28 x 34 + timpano 46", (255, 255, 255), FS)
d.line([P(80, 52.4), P(216, 52.4)], fill=(255, 200, 0), width=5)
T(96, 120, "MINING HALL 184 x 196, teto P3+84 = 136,2", (255, 255, 255), FB)
T(96, 110, "MiningZone y 80..216 (amarelo)", (255, 220, 60), FS)
for y in (100, 150, 200):
    man(y, 52.2)
T(120, 232, "cumeeira ~228", (220, 220, 240), FS)
# presbiterio + torre-coroa
R(262, 52.2, 344, 311, fill=(52, 48, 80), outline=(20, 20, 30))
poly([(282, 311), (303, 376), (324, 311)], fill=(44, 40, 70), outline=(20, 20, 30))
T(250, 380, "torre-coroa: topo 311 / agulha 376", (230, 220, 255), FS)
R(267, 54.6, 300, 112, fill=(118, 112, 150))
R(262, 52.2, 267, 112, fill=(118, 112, 150))                                 # arco triunfal
d.line([P(250, 53.0), P(262, 53.8), P(267, 54.6)], fill=(200, 200, 220), width=2)
R(289, 54.6, 299, 74.6, fill=(170, 90, 255))
T(262, 118, "presbiterio (piso 54,6)", (255, 255, 255), FS)
T(236, 80, "TRONO 14x11x20", (255, 200, 255), FS)
R(300, 54.6, 306, 112, fill=(56, 52, 84))
R(300, 54.6, 306, 72.6, fill=(30, 24, 48), outline=(255, 150, 255))
T(262, 100, "arco secreto 12 x 18", (255, 200, 255), FS)
# salao sombrio
cave = [(88, -12), (88, 30), (110, 40), (160, 46), (220, 43), (280, 46), (336, 36), (336, -12)]
poly(cave, fill=(24, 22, 38), outline=(80, 200, 255), w=3)
R(290, 2.6, 336, 6.6, fill=(80, 76, 100))
T(250, 0, "galeria 6,6", (120, 210, 255), FS)
st = [(290, 6.6), (268.4, -2.7), (262.4, -2.7), (240.8, -12)]
d.line([P(*p) for p in st], fill=(200, 200, 220), width=4)
T(212, -6, "escadaria 24 x 0,775", (200, 200, 220), FS)
R(196, -18, 220, -14, fill=(20, 40, 70))
d.line([P(190, -12), P(226, -12)], fill=(160, 160, 170), width=3)
T(186, -24, "agua escura + ponte", (120, 180, 230), FS)
for y in range(110, 330, 16):
    zt = 44 if 110 < y < 300 else 36
    poly([(y - 2.5, zt), (y + 2.5, zt), (y, zt - 9 - (y % 3) * 3)], fill=(60, 56, 80))
R(92, -12, 124, -10.4, fill=(80, 76, 100))
d.ellipse([P(96, 18), P(112, -10.4)], outline=(190, 110, 255), width=4)
T(92, 26, "UI 22", (120, 210, 255), FS)
T(126, 4, "PORTAL (DUNGEON_Hall)", (190, 140, 255), FB)
T(126, -5, "piso -12 / estrado -10,4", (190, 140, 255), FS)
man(140, -12)
T(150, 30, "SALAO SOMBRIO 180 x 248, pe-direito ate 58", (120, 210, 255), FB)
d.line([P(104, -10.4), P(104, -28)], fill=(255, 110, 180), width=2)
d.line([P(104, -28), P(48, -40)], fill=(255, 110, 180), width=2)
T(60, -24, "teleporte", (255, 140, 200), FS)
# escada caracol
R(304, 6.6, 340, 58, fill=(30, 24, 48), outline=(255, 150, 255), w=3)
R(320.5, 6.6, 323.5, 58, fill=(90, 80, 120))
z = 54.6
pts = []
for k in range(61):
    a = 2 * math.pi * k / 30.0
    pts.append((322 + 10.5 * math.cos(a + math.pi / 2), 54.6 - 0.8 * k))
d.line([P(*p) for p in pts], fill=(255, 190, 255), width=3)
T(344, 40, "ESCADA CARACOL", (255, 190, 255), FB)
T(344, 31, "54,6 -> 6,6 (-48)", (255, 190, 255), FS)
T(344, 23, "60 degraus 0,8 / 2 voltas", (255, 190, 255), FS)
T(344, 15, "degrau 10,5 (r 3..13,5)", (255, 190, 255), FS)
man(310, 54.6)
# salas
for nm, (a, b, c2, e) in DUN_ROOMS:
    R(b, DUN_Z, e, DUN_CEIL, fill=(40, 30, 50), outline=(255, 110, 180), w=3)
    T(b + 6, DUN_CEIL - 12, "%s %dx%d" % (nm, c2 - a, e - b), (255, 150, 200), FB)
for yl in (91, 197):
    R(yl - 1, DUN_Z, yl + 1, DUN_Z + 22, fill=(120, 60, 200))
R(300, DUN_Z, 304, DUN_Z + 22, fill=(120, 60, 200))
T(60, -64, "piso -72, teto -28 (44)", (255, 150, 200), FS)
T(206, -64, "vaos 28 x 22: selo/portal DENTRO do vao", (200, 150, 255), FS)
man(30, DUN_Z)
man(150, DUN_Z)
# legenda
d.text((12, 8), "CORTE NO EIXO x = 0 (local): castelo -> escada caracol -> salao sombrio -> salas (cotas = Y do Roblox)",
       fill=(255, 255, 255), font=FB)
for z in range(-100, 391, 50):
    d.line([P(Y0, z), P(Y0 + 4, z)], fill=(200, 200, 220))
    T(Y0 + 6, z + 5, str(z), (170, 170, 190), FS)
for y in range(-50, 421, 50):
    d.line([P(y, Z0), P(y, Z0 + 4)], fill=(200, 200, 220))
    T(y - 6, Z0 + 12, str(y), (170, 170, 190), FS)
T(Y1 - 150, Z0 + 26, "y local (studs); figuras = jogador 5,2", (170, 170, 190), FS)
d.line([P(Y0, -100), P(Y1, -100)], fill=(255, 120, 120), width=2)
T(230, -102, "VOID_CATCH novo em -100 (hoje -40 cortaria as salas)", (255, 170, 170), FS)
im.save(os.path.join(OUT, "corte_castelo.png"))
print(im.size)
