# wb_plan.py - planta esquematica (PNG) do wb_layout, sem Blender: zonas, edificios, rotas, contratos.
# uso: python wb_plan.py [saida.png]
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_layout as L

W, H = 1400, 1500
SC = 2.9                       # px por stud
CX, CZ = 760, 560              # pixel do (0, 0) Roblox


def P(x, z):
    return (CX + x * SC, CZ + z * SC)


def poly(d, pts, fill, outline=None, width=2):
    d.polygon([P(x, z) for x, z in pts], fill=fill, outline=outline, width=width)


def rect(d, x0, z0, x1, z1, fill, outline=None, width=2):
    d.rectangle([P(x0, z0), P(x1, z1)], fill=fill, outline=outline, width=width)


def circ(d, x, z, r, fill, outline=None, width=2):
    d.ellipse([P(x - r, z - r), P(x + r, z + r)], fill=fill, outline=outline, width=width)


def text(d, x, z, s, fill=(20, 20, 20), size=14, anchor="mm"):
    try:
        f = ImageFont.truetype("arial.ttf", size)
    except Exception:
        f = ImageFont.load_default()
    d.text(P(x, z), s, fill=fill, font=f, anchor=anchor)


def house_poly(h):
    fx, fz = h["fx"], h["fz"]
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    tx, tz = -fz, fx
    w, dd = h["w"] / 2, h["d"] / 2
    c = (h["x"], h["z"])
    pts = []
    for a, b in ((-w, dd), (w, dd), (w, -dd), (-w, -dd)):
        pts.append((c[0] + tx * a + fx * b, c[1] + tz * a + fz * b))
    return pts


def main(out):
    im = Image.new("RGB", (W, H), (120, 170, 215))         # lago
    d = ImageDraw.Draw(im)
    poly(d, L.PLATEAU, (150, 196, 110), (90, 130, 70), 3)
    # ruas e praca
    poly(d, L.PLAZA, (205, 192, 168), (120, 108, 90), 2)
    rw = L.ROAD_W / 2
    pts = L.WEST_ROAD
    for (a, b) in zip(pts[:-1], pts[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n * rw, dx / n * rw
        poly(d, [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)],
             (205, 192, 168))
    sw = L.SOUTH_ROAD_W / 2
    rect(d, -sw, L.SOUTH_ROAD[0][1], sw, L.SOUTH_ROAD[1][1], (205, 192, 168))
    rect(d, -14, 88, 14, 104, (205, 192, 168))
    circ(d, *L.WELL, 2.5, (120, 120, 120))
    # patio dos portais
    circ(d, *L.COURT_C, L.COURT_RING[1], (190, 178, 158))
    circ(d, *L.COURT_C, L.COURT_R, (205, 192, 168), (120, 108, 90))
    for i, (k, aid) in enumerate(L.PORTALS):
        (x, z), (fx, fz) = L.portal_pos(i)
        circ(d, x, z, 7, (140, 90, 200), (60, 30, 120))
        text(d, x, z, str(aid), (255, 255, 255), 16)
        text(d, x - fx * 14, z - fz * 14, k, (40, 20, 80), 11)
    text(d, L.COURT_C[0], L.COURT_C[1], "CAMINHO DOS MUNDOS", (60, 40, 20), 16)
    # ponte
    b = L.BRIDGE
    rect(d, b["x"] - b["w"] / 2, b["z0"], b["x"] + b["w"] / 2, b["z1"], (175, 165, 150), (90, 80, 70))
    text(d, 22, 185, "ponte -> Ilha 1 (z 222, piso 6)", (30, 30, 30), 12, "lm")
    rect(d, -L.GATE_HW - L.GATE_TOWER_W, L.GATE[1] - 4, L.GATE_HW + L.GATE_TOWER_W, L.GATE[1] + 4, (130, 125, 120))
    text(d, 24, 142, "portao", (30, 30, 30), 12, "lm")
    # forja
    f = L.FORGE
    rect(d, f["x0"], f["z_back"], f["x1"], f["z_front"], (170, 90, 60), (80, 40, 20), 3)
    rect(d, L.FORGE_BAY[0], f["z_front"] - 14, L.FORGE_BAY[1], f["z_front"], (230, 200, 150))
    for hx, hz in L.HEARTHS:
        circ(d, hx, hz, 4, (255, 140, 40), (120, 40, 0))
    circ(d, L.IGNIS_ROOT[0], L.IGNIS_ROOT[2], 4, (90, 90, 90), (0, 0, 0))
    text(d, 0, -76, "FORJA DO IGNIS", (255, 240, 220), 18)
    text(d, 0, -64, "Ignis", (255, 255, 255), 11)
    poly(d, L.FORGE_YARD, (160, 140, 100), (90, 80, 50))
    poly(d, L.FORGE_YARD_E, (160, 140, 100), (90, 80, 50))
    # loja
    s = L.SHOP
    rect(d, s["x0"], s["z0"], s["x1"], s["z1"], (120, 80, 160), (60, 30, 90), 3)
    text(d, (s["x0"] + s["x1"]) / 2, (s["z0"] + s["z1"]) / 2, "LOJA DE\nMOCHILAS", (255, 255, 255), 14)
    circ(d, *L.SHOP_NPC, 1.8, (255, 255, 0))
    circ(d, *L.SHOP_PLAYER, 1.8, (0, 200, 255))
    circ(d, *L.SHOP_DOOR, 1.5, (255, 255, 255))
    # mural dos campeoes
    r = L.RANK_ROOF
    rect(d, r["x0"], r["z0"], r["x1"], r["z1"], (90, 130, 190), (30, 60, 120), 3)
    text(d, (r["x0"] + r["x1"]) / 2, (r["z0"] + r["z1"]) / 2, "MURAL DOS\nCAMPEOES\n(Top 100)", (255, 255, 255), 13)
    # casas
    for h in L.HOUSES:
        poly(d, house_poly(h), (235, 215, 170), (100, 70, 40), 2)
        fx, fz = h["fx"], h["fz"]
        n = math.hypot(fx, fz)
        d.line([P(h["x"], h["z"]), P(h["x"] + fx / n * h["d"] * 0.7, h["z"] + fz / n * h["d"] * 0.7)],
               fill=(100, 70, 40), width=2)
        text(d, h["x"], h["z"], h["id"] + (" " + h["sign"] if h["sign"] else ""), (60, 40, 20), 11)
    # praca: mobiliario
    circ(d, *L.FOUNTAIN, L.FOUNTAIN_R, (120, 180, 220), (60, 90, 130))
    text(d, L.FOUNTAIN[0], L.FOUNTAIN[1], "fonte", (20, 40, 80), 11)
    for (x, z, f_, c) in L.STALLS:
        rect(d, x - 4, z - 6, x + 4, z + 6, (220, 90, 80) if "Red" in c else (90, 110, 200) if "Blue" in c else (90, 160, 90))
    text(d, 34, 32, "barracas", (40, 20, 20), 12)
    rect(d, L.CART[0] - 3, L.CART[1] - 6, L.CART[0] + 3, L.CART[1] + 6, (140, 100, 60))
    for (x, z) in L.OAKS:
        circ(d, x, z, 7, (70, 140, 60), (40, 90, 30))
    # cerca + placa + spawn + correio
    d.line([P(L.FENCE_X[0], L.FENCE_Z), P(-L.FENCE_GAP, L.FENCE_Z)], fill=(110, 70, 30), width=4)
    d.line([P(L.FENCE_GAP, L.FENCE_Z), P(L.FENCE_X[1], L.FENCE_Z)], fill=(110, 70, 30), width=4)
    rect(d, L.SIGN[0] - 6, L.SIGN[1] - 1, L.SIGN[0] + 6, L.SIGN[1] + 1, (150, 90, 40))
    text(d, L.SIGN[0] + 8, L.SIGN[1] + 6, "placa BEM-VINDO", (60, 30, 10), 11, "lm")
    circ(d, *L.SPAWN, 3, (255, 60, 60), (120, 0, 0))
    text(d, L.SPAWN[0] + 5, L.SPAWN[1], "SPAWN (olha a forja)", (120, 0, 0), 12, "lm")
    circ(d, *L.MAILBOX, 1.8, (60, 60, 200))
    text(d, L.MAILBOX[0] - 3, L.MAILBOX[1], "correio", (30, 30, 120), 11, "rm")
    circ(d, *L.SIGNPOST, 1.5, (90, 60, 30))
    circ(d, *L.COURT_SIGN, 1.5, (90, 60, 30))
    # rotas de QA
    for name, (pts, y) in L.routes().items():
        if "PORTAL" in name and "PORTAL4" not in name:
            continue
        d.line([P(x, z) for x, z in pts], fill=(200, 30, 30), width=2)
    # legenda / escala
    text(d, -200, -120, "WOLFBERG - planta esquematica (X leste, Z sul; 1 quadrado = 50 studs)", (20, 20, 20), 16, "lm")
    for gx in range(-250, 251, 50):
        d.line([P(gx, -140), P(gx, 240)], fill=(255, 255, 255, 60), width=1)
    for gz in range(-150, 251, 50):
        d.line([P(-260, gz), P(260, gz)], fill=(255, 255, 255, 60), width=1)
    im.save(out)
    print("PLANTA", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "renders", "planta_wb.png"))
