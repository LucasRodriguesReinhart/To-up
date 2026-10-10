# sheet_u6.py - corte transversal medido da ponte do canal (y 182 e 252) + captura 05
import json, os
from PIL import Image, ImageDraw, ImageFont
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
OUTD = PROJ + "/feedback_20261010/aud"
r = json.load(open("u6.json"))
F = ImageFont.truetype("arial.ttf", 15); FB = ImageFont.truetype("arialbd.ttf", 22); FS = ImageFont.truetype("arial.ttf", 13)
W, H = 1700, 980
img = Image.new("RGB", (W, H), (20, 26, 36)); d = ImageDraw.Draw(img)
d.text((16, 10), "U6 - ponte vermelha do canal oeste 'dentro da calcada' (corte medido por raios, export 37998c7c)", fill=(255, 255, 255), font=FB)
X0, X1, Z0, Z1 = -186.2, -161.8, 88.6, 94.0
ox, oy, sw, sh = 40, 70, 1080, 380


def P(x, z, row=0):
    return (ox + (x - X0) / (X1 - X0) * sw, oy + row * (sh + 60) + (Z1 - z) / (Z1 - Z0) * sh)


COL = {"Wood_OP_Mid": (176, 120, 70), "Wood_OP_Dark": (90, 60, 40), "Wood_OP_Lacquer": (200, 40, 40), "Stone_OP_Path": (200, 196, 180),
       "Stone_OP_B": (150, 150, 150), "Dirt_OP": (130, 100, 70), "Dirt_OP_Dark": (90, 70, 50), "Grass_OP_B": (90, 150, 70),
       "Grass_OP": (90, 150, 70), "Stone_OP": (170, 166, 156)}
for row, key in enumerate(("y182", "y176")):
    d.rectangle([ox, oy + row * (sh + 60), ox + sw, oy + row * (sh + 60) + sh], outline=(80, 90, 110))
    for z in range(89, 94):
        a = P(X0, z, row); b = P(X1, z, row)
        d.line([a, b], fill=(45, 55, 70)); d.text((ox + sw + 6, a[1] - 8), "%d" % z, fill=(150, 150, 150), font=FS)
    for x in range(-186, -161, 2):
        a = P(x, Z0, row); d.text((a[0] - 14, a[1] + 4), str(x), fill=(150, 150, 150), font=FS)
    # agua (Roblox, nao colide) e colisao
    a, b = P(-177.4, 91.6, row), P(-170.4, 89.4, row)
    d.rectangle([a, b], fill=(40, 120, 170))
    d.text((a[0] + 4, a[1] + 4), "agua 91,6 (Part do Roblox, CanCollide=false)", fill=(220, 240, 255), font=FS)
    if key == "y182":
        a, b = P(-182.0, 92.2, row), P(-166.0, 92.2, row)
        d.line([a, b], fill=(255, 230, 0), width=3)
        d.text((a[0], a[1] + 4), "COLISAO CanalS 92,2 (rampa plana, 10 de largura, x -182..-166)", fill=(255, 230, 0), font=FS)
    else:
        a, b = P(-186.0, 92.2, row), P(-178.0, 92.2, row)
        d.line([a, b], fill=(255, 230, 0), width=3)
        a, b = P(-170.0, 92.2, row), P(-162.0, 92.2, row)
        d.line([a, b], fill=(255, 230, 0), width=3)
        d.text((P(-176.5, 92.0, row)[0], P(-176, 90.8, row)[1]), "SEM colisao: canal = buraco ate o vazio", fill=(255, 230, 0), font=FS)
    for x, hs in r[key]:
        for h in hs[:3]:
            c = COL.get(h[2], (230, 230, 230))
            a = P(x - 0.1, h[0], row)
            d.rectangle([a[0], a[1] - 2, a[0] + sw * 0.2 / (X1 - X0), a[1] + 2], fill=c)
    d.text((ox + 6, oy + row * (sh + 60) + 6), {"y182": "CORTE y = 182 (eixo da ponte CanalS; a CanalN em y 252 mede igual)",
                                                 "y176": "CORTE y = 176 (6 ao lado: canal sem ponte)"}[key], fill=(255, 255, 255), font=F)
txt = [
    "MEDIDAS (iguais nas 2 pontes):",
    "- vao real do canal: 7,0 (x -177,4..-170,4), leito 89,4, agua 91,6",
    "- capa de pedra do canal (op_water): 93,05..93,15, 1,2-2,6 de largura",
    "- tabuleiro: 14,4 de comprimento (x -181,2..-166,8), 92,79..92,92 sobre a",
    "  agua e 92,50..92,69 sobre a calcada: flecha de 0,13",
    "- a CAPA do canal fica 0,15-0,35 ACIMA do tabuleiro: as pedras",
    "  atravessam as tabuas (as faixas cinza da captura 05)",
    "- 3,6 a 3,8 de tabuleiro deitados em cada calcada (92,35 / 92,0-92,3):",
    "  sobra so 0,2-0,35 de espessura acima do piso = 'prancha no chao'",
    "- folga sob a ponte: 1,2-1,3 sobre a agua (le como laje, nao arco)",
    "- colisao plana 92,2: o pe afunda 0,6-0,7 nas tabuas e 0,9 nas capas",
    "- o canal tem 0,6 de diferenca piso/agua: a ponte nao tem o que vencer",
    "",
    "CAUSA: op_capital.canal_bridge() desenha o tabuleiro para",
    "'capa 92,5' (pedido do op_water no cabecalho), mas a capa medida",
    "nas pontes e 93,05-93,15; e a ponte foi pensada plana na cota da",
    "praca (op_col.bridges 'CanalS/N' a 92,2) - sem encontros, sem",
    "rampa/degrau, sem arco que suba acima das margens.",
    "",
    "V2: canal 2,5-3 abaixo do piso (agua ~89,5), muretas de 0,9",
    "acima do piso SO fora das pontes, ponte em ARCO de verdade",
    "(sobe 1,2-1,6 no meio, 2 degraus/rampa de 1:8 nos encontros de",
    "pedra que ficam FORA do vao), colisao em 2 rampas + topo.",
]
y = 70
for t in txt:
    d.text((1150, y), t, fill=(230, 230, 230) if not t.startswith(("MEDIDAS", "CAUSA", "V2")) else (255, 210, 120), font=FS)
    y += 21
try:
    sc = Image.open(PROJ + "/feedback_20261010/05_ponte_canal_na_calcada.jpg")
    sc.thumbnail((420, 400))
    img.paste(sc, (1180, y + 10))
except Exception as e:
    print(e)
img.save(OUTD + "/U6_ponte_canal_corte.png")
print("ok")
