# map_u8.py - folha de evidencia U8: mapa de cima (local) com chao visual x colisao x alcance
import sys, json, math, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L
OUTD = PROJ + "/feedback_20261010/aud"
os.makedirs(OUTD, exist_ok=True)
g = np.load("grid.npz")
mk = np.load("u8_masks.npz")
xs, ys = g["xs"], g["ys"]
zv = g["zv"]
S = 2.0
X0, X1, Y0, Y1 = -275.0, 375.0, -140.0, 635.0
W, H = int((X1 - X0) * S), int((Y1 - Y0) * S) + 70


def P(x, y):
    return ((x - X0) * S, (Y1 - y) * S + 70)


try:
    F = ImageFont.truetype("arial.ttf", 15)
    FB = ImageFont.truetype("arialbd.ttf", 22)
    FS = ImageFont.truetype("arial.ttf", 12)
except Exception:
    F = FB = FS = ImageFont.load_default()

img = Image.new("RGB", (W, H), (24, 34, 48))
d = ImageDraw.Draw(img)
# altura visual em cinza
z = np.nan_to_num(zv, nan=0.0)
zn = np.clip((z - 30) / 130, 0, 1)
ST = 1.5
cat = mk["cat"]
for j in range(len(ys)):
    for i in range(len(xs)):
        if not np.isfinite(zv[j, i]):
            continue
        v = int(70 + 120 * zn[j, i])
        col = (v, v, v)
        if mk["walk"][j, i] and not mk["miss"][j, i]:
            col = (v - 20, v + 20, v - 20) if mk["reach"][j, i] else (v, v, v)
        if mk["miss"][j, i]:
            col = (v // 2 + 40, v // 2 + 40, v // 2 + 70)       # sem colisao, nao alcancavel (azulado)
        if mk["hit"][j, i]:
            c = int(cat[j, i])
            col = {1: (235, 40, 40), 2: (255, 150, 20), 3: (230, 60, 220)}.get(c, (255, 255, 0))
        x, y = P(xs[i] - ST / 2, ys[j] + ST / 2)
        d.rectangle([x, y, x + ST * S, y + ST * S], fill=col)
# contornos
d.line([P(*p) for p in L.ISLAND_RIM] + [P(*L.ISLAND_RIM[0])], fill=(120, 200, 255), width=2)
for nm, poly, zz, pr in L.floors():
    d.line([P(*p) for p in poly] + [P(*poly[0])], fill=(255, 255, 255), width=1)
for nm, poly, zz in L.ROCKS:
    d.line([P(*p) for p in poly] + [P(*poly[0])], fill=(255, 220, 120), width=1)
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    d.text(P(cx, cy), nm, fill=(255, 230, 150), font=FS)
regs = json.load(open("u8_regioes.json"))
for r in regs[:40]:
    if r["area"] >= 40:
        d.text(P(r["c"][0] + 2, r["c"][1] + 2), "#%d" % r["id"], fill=(255, 255, 255), font=F, stroke_width=2, stroke_fill=(0, 0, 0))
# grade de coordenadas
for gx in range(-250, 376, 50):
    d.text(P(gx, Y0 + 6), str(gx), fill=(180, 180, 180), font=FS)
for gy in range(-100, 636, 50):
    d.text(P(X0 + 2, gy), str(gy), fill=(180, 180, 180), font=FS)
d.rectangle([0, 0, W, 68], fill=(10, 14, 20))
d.text((10, 6), "U8 - chao visual sem colisao (export 37998c7c, raios de cima, grade 1,5, coord. LOCAIS)", fill=(255, 255, 255), font=FB)
d.text((10, 38), "VERMELHO chao/rocha | LARANJA telhado | MAGENTA copa  = visual andavel (normal>=0,7) sem COL ate 1,5 abaixo E alcancavel (<=6 de piso alcancavel, pulo 7,2)."
       "  verde = chao com colisao alcancado | azulado = sem colisao fora de alcance", fill=(220, 220, 220), font=FS)
img.save(OUTD + "/U8_mapa_chao_sem_colisao.png")
print("ok", img.size)
