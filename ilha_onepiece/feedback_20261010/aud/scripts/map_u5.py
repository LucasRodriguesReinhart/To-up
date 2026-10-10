import sys, json, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L
OUTD = PROJ + "/feedback_20261010/aud"
g = np.load("grid.npz"); mk = np.load("u8_masks.npz")
xs, ys, zv = g["xs"], g["ys"], g["zv"]
S = 2.0; X0, X1, Y0, Y1 = -275.0, 375.0, -140.0, 635.0
W, H = int((X1 - X0) * S), int((Y1 - Y0) * S) + 70
def P(x, y): return ((x - X0) * S, (Y1 - y) * S + 70)
F = ImageFont.truetype("arial.ttf", 14); FB = ImageFont.truetype("arialbd.ttf", 22); FS = ImageFont.truetype("arial.ttf", 12)
img = Image.new("RGB", (W, H), (24, 34, 48)); d = ImageDraw.Draw(img)
zn = np.clip((np.nan_to_num(zv, nan=0) - 30) / 130, 0, 1)
for j in range(len(ys)):
    for i in range(len(xs)):
        if np.isfinite(zv[j, i]):
            v = int(60 + 110 * zn[j, i]); c = (v, v, v)
            if mk["reach"][j, i]: c = (v - 15, v + 10, v - 15)
            x, y = P(xs[i] - .75, ys[j] + .75); d.rectangle([x, y, x + 3, y + 3], fill=c)
d.line([P(*p) for p in L.ISLAND_RIM] + [P(*L.ISLAND_RIM[0])], fill=(120, 200, 255), width=2)
for nm, poly, zz, pr in L.floors():
    d.line([P(*p) for p in poly] + [P(*poly[0])], fill=(255, 255, 255), width=1)
# U8b: corpo/cabeca dentro do visual (rocha/construcao), pontos alcancaveis
Pp = np.load("reach_pts.npy"); R = np.load("inside.npy"); m2 = json.load(open("meta2.json"))
for (x, y, h), (dd, back, oi, mi) in zip(Pp, R):
    if dd < 0: continue
    mat = m2["mats"][int(mi)]
    if mat.startswith(("Leaf", "Flower")): continue
    if back > 0 and dd >= 1.5: col = (40, 220, 255)       # corpo dentro
    elif back > 0: continue                                # pe afunda < 1,1 (lista no json)
    elif dd < 3.0: col = (120, 120, 255)                    # cabeca dentro (< 3 acima do pe)
    else: continue
    a, b = P(x - .75, y + .75); d.rectangle([a, b, a + 3, b + 3], fill=col)
U5 = json.load(open(OUTD + "/U5_vaos.json"))
for c in U5["B"]:
    a, b = P(c["x"], c["y"]); r = 3 + min(6, c["n"])
    d.ellipse([a - r, b - r, a + r, b + r], outline=(255, 60, 60), width=2)
for c in U5["A"]:
    a, b = P(c["x"], c["y"]); r = 6
    d.rectangle([a - r, b - r, a + r, b + r], outline=(255, 230, 0), width=2)
for gx in range(-250, 376, 50): d.text(P(gx, Y0 + 6), str(gx), fill=(180, 180, 180), font=FS)
for gy in range(-100, 636, 50): d.text(P(X0 + 2, gy), str(gy), fill=(180, 180, 180), font=FS)
notes = [((213, 238), "ponte de saida: frestas 0,2-0,6 entre tabuas (ve o cais 46 abaixo)"),
         ((-60, 112), "junta T1/praca y~117,5: frestas 0,2-0,8 (ve arrimo/falesia)"),
         ((-215, 300), "borda W/W3: trincas 0,4-3,8 pele x falesia"),
         ((205, 318), "piso 92,2 ENTRA na rocha NE (corpo dentro)"),
         ((180, 150), "cais/arrimos: corpo dentro de muralha/pier"),
         ((-20, 430), "patio: raizes/base da torre sem colisao")]
for (x, y), t in notes:
    d.text(P(x, y), t, fill=(255, 255, 255), font=F, stroke_width=2, stroke_fill=(0, 0, 0))
d.rectangle([0, 0, W, 68], fill=(10, 14, 20))
d.text((10, 6), "U5 vaos + U8b 'dentro do modelo' (export 37998c7c, coord. LOCAIS)", fill=(255, 255, 255), font=FB)
d.text((10, 38), "circulo VERMELHO = fresta visual 0,2-4 entre pisos na mesma cota | quadrado AMARELO = vao de colisao >=0,6 sob visual continuo | CIANO = corpo dentro de rocha/construcao (>=1,5) | AZUL = cabeca dentro (<3)", fill=(220, 220, 220), font=FS)
img.save(OUTD + "/U5_U8b_mapa_vaos_dentro.png"); print("ok")
