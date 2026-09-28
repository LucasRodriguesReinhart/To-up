# sg_blockout - BLOCKOUT da Ilha 3 (Shadow Garden), zona por zona, com a paleta final em formas simples.
# Cada zona cria: massas visuais (detail="far"), a colisao dos PROPRIOS volumes (predios, torres, muralha, salas) e as
# luzes basicas. O chao, as escadas, as pontes, as guardas e TODOS os marcadores sao do sg_core/sg_col (sempre).
# O modulo de detalhe de uma zona SUBSTITUI a funcao dela aqui (build(skip={...})).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, yaw_to, prism, Frame, light, ngon_col, octo_col, box_walls_col
import sg_layout as L
import sg_col

ZONES = ["terrain", "entry", "village", "castle", "hall", "summon", "craft", "dungeon", "water", "exit", "dressing"]
WIN = "Window_Warm"


# ------------------------------------------------------------------ utilidades de forma
def gable_house(mb, F, w, d, h, rise, over=1.2, wall_m="Plaster_SG", roof_m="Roof_SG_Slate", base_m="Stone_SG_Block",
                timber_m="Wood_SG_Dark"):
    """casa de meia-enxaimel no referencial F (local +Y = frente, X = largura): base de pedra, corpo, telhado ingreme
    de ardosia com cumeeira ao longo de X, empenas fechadas"""
    mb.box((w, d, 1.6), F.p(0, 0, 0.8), F.r(), base_m, 0.1)
    mb.box((w - 0.2, d - 0.2, h - 1.6), F.p(0, 0, 1.6 + (h - 1.6) / 2), F.r(), wall_m, 0.05)
    # enxaimel: vigas horizontais + montantes nas 4 faces (so no blockout: poucas)
    for zz in (1.7, h - 0.2):
        for s in (-1, 1):
            mb.box((w + 0.1, 0.35, 0.45), F.p(0, s * d / 2, zz), F.r(), timber_m, 0.0)
            mb.box((0.35, d + 0.1, 0.45), F.p(s * w / 2, 0, zz), F.r(), timber_m, 0.0)
    for k in range(-2, 3):
        x = k * (w / 2 - 0.4) / 2
        for s in (-1, 1):
            mb.box((0.4, 0.35, h - 1.8), F.p(x, s * d / 2, 1.6 + (h - 1.6) / 2), F.r(), timber_m, 0.0)
    tilt = math.atan2(rise, d / 2)
    span = math.hypot(d / 2 + over, rise * (d / 2 + over) / (d / 2))
    for s in (-1, 1):
        mb.box((w + 2 * over, span, 0.7), F.p(0, s * (d / 4 + over / 2) * 0.98, h + rise / 2 - 0.1),
               (-s * tilt, 0, F.a), roof_m, 0.05)
    for s in (-1, 1):
        mb.tri(F.p(s * w / 2, -d / 2, h), F.p(s * w / 2, d / 2, h), F.p(s * w / 2, 0, h + rise), wall_m)
    mb.box((1.4, 1.4, rise + 2.0), F.p(w * 0.28, -d * 0.18, h + rise * 0.6), F.r(), base_m, 0.05)   # chamine


def tower(mb, x, y, r, z0, z1, m, roof_m, spire_h, n=8, cap_m="Stone_SG_Trim"):
    mb.cyl(r, z1 - z0, (x, y, (z0 + z1) / 2), m=m, n=n, bevel=0.0)
    mb.cyl(r + 0.8, 1.4, (x, y, z1 + 0.7), m=cap_m, n=n, bevel=0.0)
    SL.spire(mb, (x, y), r + 1.2, z1 + 1.4, spire_h, roof_m, n=n)


# ------------------------------------------------------------------ terreno: patamares, ombro, massa inferior, colunas
def terrain():
    rng = random.Random(11)
    mt = MB("SG_Ter_Blockout_Terraces", "02_TERRAIN", rng, detail="far", floor=-999)
    top = {"P1": "Stone_Paving_SG", "P2": "Grass_SG", "P3": "Stone_Paving_SG", "EntryHigh": "Stone_Paving_SG",
           "EntryLow": "Stone_Paving_SG", "Summon": "Stone_Paving_SG"}
    for nm, poly, z, pr in L.floors():
        side = "Cliff_Rock_SG" if nm in ("Summon", "EntryLow", "EntryHigh") else "Stone_SG_Block"
        prism(mt, SL.ccw(poly), z - 10.0 if nm != "Summon" else z - 16.0, z, side, top_m=top[nm])
    mt.finish()
    # ombro da ilha (terreno bravo entre os patamares e a borda): rocha baixa com topo de grama
    ms = MB("SG_Ter_Blockout_Shoulder", "02_TERRAIN", rng, detail="far", floor=-999)
    prism(ms, SL.rim(), 32.5, L.P1 - 2.0, "Cliff_Rock_SG", top_m="Grass_SG")
    # montes de rocha no terreno bravo do topo (oeste e nordeste do castelo): moldura, com colisao
    for x, y, r, h in [(-86.0, 60.0, 16.0, 70.0), (-88.0, 100.0, 14.0, 64.0), (-74.0, 150.0, 16.0, 76.0),
                       (86.0, 128.0, 16.0, 72.0), (100.0, 160.0, 12.0, 66.0), (-96.0, 14.0, 10.0, 58.0)]:
        poly = SL.blob_poly(x, y, r, 10, rng, 0.2)
        ms.prism(SL.ccw(poly), 32.5, h - 6.0, "Cliff_Rock_SG")
        ms.prism(SL.ccw(SL.blob_poly(x, y, r * 0.8, 9, rng, 0.2)), h - 6.0, h, "Cliff_Rock_SG_Top")
        ms.prism(SL.ccw(SL.blob_poly(x, y, r * 0.6, 8, rng, 0.2)), h, h + 0.6, "Grass_SG")
        octo_col("SG_TerMound", x, y, r * 0.9, 32.5, h)
    ms.finish()
    # massa inferior (ilha flutuante): bandas afinando. As tampas das bandas ficam FORA da caixa da dungeon
    # (z 2..32): a banda de cima vai de -14 a 32,5
    mu = MB("SG_Ter_Blockout_Under", "02_TERRAIN", rng, detail="far", floor=-999)
    rim = SL.rim()
    cx = sum(p[0] for p in rim) / len(rim)
    cy = sum(p[1] for p in rim) / len(rim)
    bands = [(32.5, 0.99, -14.0, "Cliff_Rock_SG"), (-14.0, 0.84, -46.0, "Cliff_Rock_SG_Dark"),
             (-46.0, 0.6, -80.0, "Cliff_Rock_SG"), (-80.0, 0.32, -108.0, "Cliff_Rock_SG_Dark")]
    for z1, f, z0, m in bands:
        pts = [(cx + (x - cx) * f * rng.uniform(0.97, 1.02), cy + (y - cy) * f * rng.uniform(0.97, 1.02))
               for x, y in rim[::2]]
        mu.prism(SL.ccw(pts), z0, z1, m)
    # rocha da plataforma do summon (ilhota propria)
    sx, sy = L.SUMMON_C
    for k, (f, z0, z1) in enumerate(((1.0, L.SUM - 30.0, L.SUM - 16.0), (0.7, L.SUM - 52.0, L.SUM - 30.0),
                                     (0.35, L.SUM - 70.0, L.SUM - 52.0))):
        mu.prism(SL.ccw(SL.blob_poly(sx, sy, L.SUMMON_R * f, 12, rng, 0.08)), z0, z1,
                 "Cliff_Rock_SG" if k % 2 == 0 else "Cliff_Rock_SG_Dark")
    mu.finish()
    # colunas de basalto na borda (silhueta vertical)
    mc = MB("SG_Ter_Blockout_Spires", "02_TERRAIN", rng, detail="far", floor=-999)
    for x, y, r, top_z, kind in L.CLIFF_SPIRES:
        z0 = -30.0
        for k in range(5):
            a = rng.uniform(0, 6.28)
            rr = r * rng.uniform(0.25, 0.55)
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            hh = top_z - rng.uniform(0, 18.0)
            mc.cyl(r * rng.uniform(0.35, 0.5), hh - z0, (px, py, (z0 + hh) / 2), m="Cliff_Rock_SG", n=6, bevel=0.0)
            mc.cyl(r * 0.4, 0.8, (px, py, hh + 0.4), m="Cliff_Rock_SG_Top", n=6, bevel=0.0)
        if L.point_in_poly(x, y, L.ISLAND_RIM):
            octo_col("SG_TerSpire", x, y, r * 0.8, 32.5, 32.5 + 20.0)
    mc.finish()


# ------------------------------------------------------------------ entrada: ponte, escadaria, 2 porticos, parapeitos
def portico(mb, y, z, hw=11.0, h=17.0, name_light=None):
    for s in (-1, 1):
        x = s * hw
        mb.box((4.0, 4.0, 1.2), (x, y, z + 0.6), (0, 0, 0), "Stone_SG_Trim", 0.1)
        mb.box((3.2, 3.2, h), (x, y, z + 1.2 + h / 2), (0, 0, 0), "Stone_SG_Castle", 0.1)
        SL.spire(mb, (x, y), 2.4, z + 1.2 + h, 5.0, "Roof_SG_Navy", n=4)
        mb.box((0.3, 2.4, 9.0), (x - s * 1.75, y, z + h - 4.0), (0, 0, 0), "Cloth_SG_Navy", 0.0)   # estandarte
        col_box("SG_EntPortico", (3.4, 3.4, h + 1.2), (x, y, z + (h + 1.2) / 2))
    mb.box((2 * hw + 3.2, 2.4, 2.0), (0, y, z + h + 0.2), (0, 0, 0), "Stone_SG_Castle", 0.1)
    mb.box((2.6, 0.5, 2.6), (0, y - 1.3, z + h + 0.2), (0, 0, math.pi / 4), "SG_Violet_Glow", 0.0)     # emblema
    for s in (-1, 1):
        mb.box((0.8, 0.8, 1.4), (s * (hw - 2.6), y - 2.0, z + 0.7), (0, 0, 0), "Metal_SG_Iron", 0.0)
        mb.box((0.9, 0.9, 1.0), (s * (hw - 2.6), y - 2.0, z + 1.9), (0, 0, 0), "Lantern_Glow", 0.0)
        light("L_SGEnt_Portico_%d_%s" % (int(-y), "W" if s < 0 else "E"), "POINT", (s * (hw - 2.6), y - 2.0, z + 2.6),
              300.0, (1.0, 0.72, 0.42), 0.4)


def entry():
    rng = random.Random(31)
    mb = MB("SG_Ent_Blockout", "18_ENTRY", rng, detail="far", floor=-999)
    hw = L.DECK_W / 2
    # ponte de chegada: tabuleiro + parapeitos + 2 pilares
    mb.box((L.DECK_W, L.BRIDGE_Y1 - L.BRIDGE_Y0, 2.0), (0, (L.BRIDGE_Y0 + L.BRIDGE_Y1) / 2, L.DECK - 1.0), (0, 0, 0),
           "Stone_SG_Block", 0.1)
    for s in (-1, 1):
        SL.vis_parapet(mb, [(s * (hw + 0.6), L.BRIDGE_Y0, L.DECK), (s * (hw + 0.6), L.BRIDGE_Y1, L.DECK)], h=1.6, w=1.0)
    mb.cyl(6.0, 60.0, (0, (L.BRIDGE_Y0 + L.BRIDGE_Y1) / 2, L.DECK - 32.0), m="Cliff_Rock_SG_Dark", n=8, r2=3.0, bevel=0.0)
    SL.plan_stair(mb, "Entry")
    portico(mb, L.PORTICO_A_Y, L.DECK)
    portico(mb, L.PORTICO_B_Y, L.P1)
    x0, y0, x1, y1 = L.ENTRY_HIGH
    for s in (-1, 1):
        SL.vis_parapet(mb, [(s * (x1 + 0.6), y0, L.P1), (s * (x1 + 0.6), y1 - 6.0, L.P1)], h=1.6, w=1.0)
    x0, y0, x1, y1 = L.ENTRY_LOW
    for s in (-1, 1):
        SL.vis_parapet(mb, [(s * (x1 + 0.6), y0, L.DECK), (s * (x1 + 0.6), y1, L.DECK)], h=1.6, w=1.0)
    mb.finish()


# ------------------------------------------------------------------ vila: praca + fonte, ruas, 12 casas
def village():
    rng = random.Random(41)
    mb = MB("SG_Vil_Blockout", "05_VILLAGE", rng, detail="far", floor=-999)
    cx, cy = L.PLAZA_C
    mb.prism(SL.ccw(L.plaza_poly()), L.P1 - 0.2, L.P1 + 0.06, "Stone_SG_Trim")
    mb.cyl(L.FOUNTAIN_R, 2.6, (cx, cy, L.P1 + 1.3), m="Stone_SG_Castle", n=16, bevel=0.0)
    mb.cyl(L.FOUNTAIN_R - 0.9, 0.3, (cx, cy, L.P1 + 2.3), m="Water_SG", n=16, bevel=0.0)
    mb.cyl(1.6, 7.0, (cx, cy, L.P1 + 5.0), m="Stone_SG_Trim", n=8, bevel=0.0)
    mb.cyl(3.2, 0.8, (cx, cy, L.P1 + 7.0), m="Stone_SG_Castle", n=12, bevel=0.0)
    for pts, w, z in L.STREETS:
        mb.prism(SL.ribbon_poly(pts, w / 2), z - 0.2, z + 0.05, "Stone_Paving_SG")
    for i, (x, y, w, d, deg, z) in enumerate(L.HOUSE_LOTS):
        ya = math.radians(deg) - math.pi / 2
        F = Frame(x, y, z, ya)
        h = 9.0 + (i % 3) * 1.5
        gable_house(mb, F, w, d, h, rise=6.5 + (i % 2) * 1.5)
        for k in (-1, 1):
            mb.box((1.6, 0.2, 2.2), F.p(k * w * 0.26, d / 2 + 0.05, 5.4), F.r(), WIN, 0.0)
            mb.box((1.6, 0.2, 2.2), F.p(k * w * 0.26, -d / 2 - 0.05, 5.4), F.r(), WIN, 0.0)
        col_box("SG_VilHouse", (w, d, h + 4.0), F.p(0, 0, (h + 4.0) / 2), F.r())
        if i % 3 == 0:
            light("L_SGVil_House_%02d" % i, "POINT", F.p(0, d / 2 + 2.0, 5.0), 180.0, (1.0, 0.7, 0.42), 0.3)
    mb.finish()


# ------------------------------------------------------------------ castelo: muralha + portao, nave, torres, coroa
def castle():
    rng = random.Random(51)
    mb = MB("SG_Cas_Blockout", "04_CASTLE", rng, detail="far", floor=-999)
    z = L.P3
    # muralha sobre a borda sul do P3 (face externa em y -9): 12 de altura, ameias; portao 16 x 18 com torre-portaria
    wy0, wy1 = L.WALL_Y0, L.WALL_Y1
    gx, gw = L.EAST_WALL_GAP
    cuts = [(-L.GATEHOUSE_W / 2, L.GATEHOUSE_W / 2), (gx - gw / 2, gx + gw / 2)]
    xs = [L.WALL_X[0]] + [c for ab in cuts for c in ab] + [L.WALL_X[1]]
    for a, b in zip(xs[0::2], xs[1::2]):
        mb.box2((a, wy0, z - 0.2), (b, wy1, z + 12.0), "Stone_SG_Block", 0.1)
        n = int((b - a) / 3.0)
        for k in range(n):
            if k % 2 == 0:
                x = a + (k + 0.5) * (b - a) / n
                mb.box((1.4, wy1 - wy0, 1.6), (x, (wy0 + wy1) / 2, z + 12.8), (0, 0, 0), "Stone_SG_Block", 0.0)
        col_box2("SG_CasWall", (a, wy0, z - 0.5), (b, wy1, z + 12.0))
    # torre-portaria sobre o portao (verga acima de 18)
    mb.box2((-L.GATEHOUSE_W / 2 - 1.0, wy0 - 1.0, z + L.GATEHOUSE_H), (L.GATEHOUSE_W / 2 + 1.0, wy1 + 1.0, z + 26.0),
            "Stone_SG_Castle", 0.1)
    col_box2("SG_CasWall", (-L.GATEHOUSE_W / 2 - 1.0, wy0 - 1.0, z + L.GATEHOUSE_H), (L.GATEHOUSE_W / 2 + 1.0, wy1 + 1.0, z + 26.0))
    for x, y, r in L.GATEHOUSE_TOWERS:
        tower(mb, x, y, r, z - 8.0, z + 28.0, "Stone_SG_Castle", "Roof_SG_Navy", 12.0)
        octo_col("SG_CasTower", x, y, r, z - 8.0, z + 28.0)
    for x in (gx - gw / 2 - 3.0, gx + gw / 2 + 3.0):
        tower(mb, x, -6.0, 3.6, z - 8.0, z + 18.0, "Stone_SG_Castle", "Roof_SG_Navy", 7.0)
        octo_col("SG_CasTower", x, -6.0, 3.6, z - 8.0, z + 18.0)
    # nave (paredes do Mining Hall): face interna = retangulo do salao; porta 16 x 18 na fachada
    hx0, hy0, hx1, hy1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
    t = L.HALL_WALL
    wall_top = z + 34.0
    rect_out = (hx0 - t, hy0 - t, hx1 + t, hy1 + t)
    dw, dh = L.HALL_DOOR_W, L.HALL_DOOR_H
    # paredes (visual): 4 caixas + fachada com vao
    mb.box2((hx0 - t, hy0, z - 0.2), (hx0, hy1, wall_top), "Stone_SG_Castle", 0.1)
    mb.box2((hx1, hy0, z - 0.2), (hx1 + t, hy1, wall_top), "Stone_SG_Castle", 0.1)
    mb.box2((hx0 - t, hy1, z - 0.2), (hx1 + t, hy1 + t, wall_top), "Stone_SG_Castle", 0.1)
    mb.box2((hx0 - t, hy0 - t, z - 0.2), (-dw / 2, hy0, wall_top), "Stone_SG_Castle", 0.1)
    mb.box2((dw / 2, hy0 - t, z - 0.2), (hx1 + t, hy0, wall_top), "Stone_SG_Castle", 0.1)
    mb.box2((-dw / 2, hy0 - t, z + dh), (dw / 2, hy0, wall_top), "Stone_SG_Castle", 0.1)
    # empena da fachada + rosacea (acento violeta: marca do castelo)
    mb.tri((hx0 - t, hy0 - t - 0.1, wall_top), (hx1 + t, hy0 - t - 0.1, wall_top), (0.0, hy0 - t - 0.1, wall_top + 26.0),
           "Stone_SG_Castle")
    mb.cyl(6.5, 0.6, (0.0, hy0 - t - 0.3, z + 26.0), (math.pi / 2, 0, 0), m="Glass_SG_Rose", n=16, bevel=0.0)
    mb.cyl(7.3, 0.5, (0.0, hy0 - t - 0.2, z + 26.0), (math.pi / 2, 0, 0), m="Stone_SG_Trim", n=16, bevel=0.0)
    # porta: moldura em arco (blockout: verga e ombreiras claras)
    for s in (-1, 1):
        mb.box((1.4, 1.2, dh + 2.0), (s * (dw / 2 + 0.7), hy0 - t - 0.4, z + (dh + 2.0) / 2), (0, 0, 0), "Stone_SG_Trim", 0.05)
    mb.box((dw + 2.8, 1.2, 1.6), (0.0, hy0 - t - 0.4, z + dh + 1.2), (0, 0, 0), "Stone_SG_Trim", 0.05)
    # telhado navy ingreme (cumeeira norte-sul)
    rise = 26.0
    half = (hx1 - hx0) / 2 + t + 1.5
    tilt = math.atan2(rise, half - 1.5)
    span = math.hypot(half, rise * half / (half - 1.5))
    for s in (-1, 1):
        mb.box((span, hy1 - hy0 + 2 * t + 3.0, 1.0), (s * half / 2, (hy0 + hy1) / 2, wall_top + rise / 2),
               (0, s * tilt, 0), "Roof_SG_Navy", 0.05)
    # contrafortes nas laterais (ritmo gotico), pinaculos
    for k in range(5):
        y = hy0 + 8.0 + k * (hy1 - hy0 - 16.0) / 4
        for s in (-1, 1):
            x = s * (hx1 + t + 1.6)
            mb.box((3.2, 3.0, wall_top - z - 4.0), (x, y, z + (wall_top - z - 4.0) / 2), (0, 0, 0), "Stone_SG_Castle", 0.1)
            SL.spire(mb, (x, y), 1.8, wall_top - 4.0, 8.0, "Stone_SG_Trim", n=4)
            col_box("SG_CasButtress", (3.2, 3.0, 12.0), (x, y, z + 6.0))
    # janelas altas (luar dentro do salao): faixas de vidro violeta escuro, acima de 14
    for k in range(4):
        y = hy0 + 16.0 + k * (hy1 - hy0 - 32.0) / 3
        for s in (-1, 1):
            mb.box((0.4, 4.0, 14.0), (s * (hx1 + t + 0.1), y, z + 22.0), (0, 0, 0), "Glass_SG_Rose", 0.0)
    # colisao das paredes do salao + teto (opaco, segura a camera)
    box_walls_col("SG_CasHall", (hx0, hy0, hx1, hy1), z - 0.5, wall_top, t, doors=[("S", 0.0, dw, dh)])
    col_box2("SG_CasHallCeil", (hx0 - t, hy0 - t, L.HALL_CEIL), (hx1 + t, hy1 + t, L.HALL_CEIL + 2.0))
    # teto interno visual (abobada simples no blockout)
    mb.box2((hx0, hy0, L.HALL_CEIL), (hx1, hy1, L.HALL_CEIL + 1.0), "Stone_SG_Castle", 0.0)
    # torres da fachada
    for x, y, r, top in L.FRONT_TOWERS:
        tower(mb, x, y, r, z - 10.0, top, "Stone_SG_Castle", "Roof_SG_Navy", 34.0)
        octo_col("SG_CasTower", x, y, r, z - 1.0, top)
    # torre-coroa (heroi): tambor + andar de agulhas + flecha
    x, y, r, top = L.CROWN_TOWER
    mb.cyl(r, top - z, (x, y, (z + top) / 2), m="Stone_SG_Castle", n=12, bevel=0.0)
    mb.cyl(r + 1.2, 2.0, (x, y, top + 1.0), m="Stone_SG_Trim", n=12, bevel=0.0)
    for k in range(8):
        a = k * math.pi / 4
        SL.spire(mb, (x + (r - 1.0) * math.cos(a), y + (r - 1.0) * math.sin(a)), 2.0, top + 2.0, 14.0, "Roof_SG_Navy", n=4)
    mb.cyl(r * 0.62, 14.0, (x, y, top + 9.0), m="Stone_SG_Castle", n=12, bevel=0.0)
    SL.spire(mb, (x, y), r * 0.7, top + 16.0, L.CROWN_SPIRE_TOP - top - 16.0, "Roof_SG_Navy", n=12)
    mb.cyl(3.0, 0.6, (x, y - r * 0.62 - 0.3, top + 9.0), (math.pi / 2, 0, 0), m="SG_Violet_Glow", n=12, bevel=0.0)
    ngon_col("SG_CasCrown", x, y, 12, r, z - 1.0, top)
    mb.finish()
    light("L_SGCas_Door", "POINT", (0.0, hy0 - t - 3.0, z + 8.0), 600.0, (1.0, 0.72, 0.45), 0.5)
    light("L_SGCas_Rose", "POINT", (0.0, hy0 - t - 3.0, z + 26.0), 500.0, (0.62, 0.45, 1.0), 0.5)


# ------------------------------------------------------------------ Mining Hall (interior): piso, pilastras, lustres, luz
def hall():
    rng = random.Random(61)
    mb = MB("SG_Hall_Blockout", "03_MINING_HALL", rng, detail="far", floor=-999)
    z = L.HALL
    hx0, hy0, hx1, hy1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
    mb.box2((hx0, hy0, z - 0.2), (hx1, hy1, z + 0.04), "Stone_SG_Floor", 0.0)
    x0, y0, x1, y1 = L.MINE_RECT
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        mb.beam((a[0], a[1], z + 0.08), (b[0], b[1], z + 0.08), 0.6, 0.08, "Stone_SG_Trim", 0.0)
    # pilastras engastadas nas paredes (sem nada no meio do salao)
    for k in range(7):
        y = hy0 + 6.0 + k * (hy1 - hy0 - 12.0) / 6
        for s in (-1, 1):
            mb.box((1.6, 2.4, L.HALL_CEIL - z), (s * (hx1 - 0.8), y, z + (L.HALL_CEIL - z) / 2), (0, 0, 0), "Stone_SG_Trim", 0.05)
    # lustres altos (acima de 20: nada colidivel ate piso+12; sem colisao) + luz propria do salao
    for i, (x, y) in enumerate(((-18.0, 66.0), (18.0, 66.0), (-18.0, 110.0), (18.0, 110.0), (0.0, 88.0))):
        mb.cyl(3.0, 0.6, (x, y, z + 21.0), m="Metal_SG_Iron", n=10, bevel=0.0)
        mb.cyl(2.4, 0.5, (x, y, z + 21.6), m="Lantern_Glow", n=10, bevel=0.0)
        mb.rod((x, y, z + 21.6), (x, y, L.HALL_CEIL), 0.15, "Metal_SG_Iron", 4)
        light("L_SGHall_Chandelier_%d" % i, "POINT", (x, y, z + 19.0), 2600.0, (1.0, 0.76, 0.5), 1.0)
    light("L_SGHall_Moon_W", "POINT", (hx0 + 3.0, 88.0, z + 22.0), 1500.0, (0.6, 0.7, 1.0), 2.0)
    light("L_SGHall_Moon_E", "POINT", (hx1 - 3.0, 88.0, z + 22.0), 1500.0, (0.6, 0.7, 1.0), 2.0)
    mb.finish()


# ------------------------------------------------------------------ invocacao: ponte, escada, torre (familia das ilhas)
def summon():
    rng = random.Random(71)
    mb = MB("SG_Sum_Blockout", "06_SUMMON", rng, detail="far", floor=-999)
    a0, a1, w = L.SUMMON_BRIDGE
    mb.box2((a1[0], a0[1] - w / 2, L.P1 - 2.0), (a0[0], a0[1] + w / 2, L.P1), "Stone_SG_Block", 0.05)
    for s in (-1, 1):
        SL.vis_parapet(mb, [(a0[0], a0[1] + s * (w / 2 + 0.6), L.P1), (a1[0], a1[1] + s * (w / 2 + 0.6), L.P1)], h=1.6, w=1.0)
    SL.plan_stair(mb, "Summon")
    tx, ty = L.SUMMON_TOWER
    z = L.SUM
    mb.box((12.0, 14.0, 2.0), (tx, ty, z + 1.0), (0, 0, 0), "Stone_SG_Trim", 0.1)
    for s in (-1, 1):
        mb.box((3.4, 3.4, 20.0), (tx, ty + s * 6.0, z + 12.0), (0, 0, 0), "Stone_SG_Castle", 0.1)
        SL.spire(mb, (tx, ty + s * 6.0), 2.6, z + 22.0, 7.0, "Roof_SG_Navy", n=4)
    mb.box((3.4, 15.4, 3.0), (tx, ty, z + 21.0), (0, 0, 0), "Stone_SG_Castle", 0.1)
    mb.box((2.0, 8.0, 18.0), (tx - 1.6, ty, z + 11.0), (0, 0, 0), "Stone_SG_Castle", 0.0)
    mb.cyl(3.6, 0.6, (tx + 0.4, ty, z + 12.0), (0, math.pi / 2, 0), m="SG_Violet_Glow", n=16, bevel=0.0)   # esfera-estrela
    mb.cyl(4.4, 0.5, (tx + 0.2, ty, z + 12.0), (0, math.pi / 2, 0), m="Metal_SG_Silver", n=16, bevel=0.0)
    col_box("SG_SumTower", (4.0, 16.0, 22.0), (tx - 1.0, ty, z + 11.0))
    mb.finish()
    light("L_SGSum_Star", "POINT", (tx + 3.0, ty, z + 12.0), 900.0, (0.66, 0.46, 1.0), 1.0)


# ------------------------------------------------------------------ craft: pavilhao redondo com domo + frasco gigante
def craft():
    rng = random.Random(81)
    mb = MB("SG_Craft_Blockout", "16_CRAFT", rng, detail="far", floor=-999)
    cx, cy = L.CRAFT_C
    z = L.P2
    R, ri, h = L.CRAFT_R, L.CRAFT_R - 2.5, 14.0
    da = math.radians(L.CRAFT_DOOR_DEG)
    half = math.asin((L.CRAFT_DOOR_W / 2) / ri)
    n = 20
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        diff = abs((am - da + math.pi) % (2 * math.pi) - math.pi)
        rm = (R + ri) / 2
        seg_w = 2 * R * math.sin(math.pi / n) + 0.3
        x, y = cx + rm * math.cos(am), cy + rm * math.sin(am)
        if diff < half + math.pi / n * 0.5:
            mb.box((R - ri, seg_w, h - L.CRAFT_DOOR_H), (x, y, z + L.CRAFT_DOOR_H + (h - L.CRAFT_DOOR_H) / 2), (0, 0, am),
                   "Stone_SG_Castle", 0.0)
            col_box("SG_CraftWall", (R - ri, seg_w, h - L.CRAFT_DOOR_H), (x, y, z + L.CRAFT_DOOR_H + (h - L.CRAFT_DOOR_H) / 2),
                    (0, 0, am))
            continue
        mb.box((R - ri, seg_w, h), (x, y, z + h / 2), (0, 0, am), "Stone_SG_Castle", 0.0)
        col_box("SG_CraftWall", (R - ri, seg_w, h), (x, y, z + h / 2), (0, 0, am))
    mb.cyl(R + 0.8, 1.2, (cx, cy, z + h + 0.6), m="Stone_SG_Trim", n=20, bevel=0.0)
    SL.dome(mb, (cx, cy), R + 0.4, z + h + 1.2, "Roof_SG_Navy", n=20, rings=6, squash=0.8)
    col_box2("SG_CraftRoof", (cx - R, cy - R, z + h), (cx + R, cy + R, z + h + 1.2))
    # frasco gigante no topo (a marca do pavilhao): bojo de vidro violeta + gargalo + rolha de prata
    top = z + h + 1.2 + (R + 0.4) * 0.8
    mb.ico(4.2, (cx, cy, top + 3.6), "Glass_SG_Rose", 2)
    mb.cyl(1.4, 4.0, (cx, cy, top + 9.0), m="Glass_SG_Rose", n=10, bevel=0.0)
    mb.cyl(1.7, 1.0, (cx, cy, top + 11.4), m="Metal_SG_Silver", n=10, bevel=0.0)
    mb.ico(2.6, (cx, cy, top + 3.2), "SG_Violet_Glow", 1)
    # interior: caldeirao (estacao), bancada, estantes
    mb.box2((cx - ri, cy - ri, z - 0.2), (cx + ri, cy + ri, z + 0.04), "Stone_SG_Floor", 0.0)
    mb.cyl(2.2, 2.6, (cx, cy, z + 1.3), m="Metal_SG_Iron", n=14, r2=2.6, bevel=0.0)
    mb.cyl(1.9, 0.3, (cx, cy, z + 2.5), m="SG_Violet_Glow", n=14, bevel=0.0)
    ngon_col("SG_CraftCauldron", cx, cy, 12, 2.6, z, z + 2.8)
    for k, a in enumerate((60.0, 100.0, 260.0, 300.0)):
        ar = math.radians(a)
        x, y = cx + (ri - 1.0) * math.cos(ar), cy + (ri - 1.0) * math.sin(ar)
        mb.box((1.4, 5.0, 7.0), (x, y, z + 3.5), (0, 0, ar), "Wood_SG_Dark", 0.05)
    nx, ny = cx - math.cos(da) * 6.0, cy - math.sin(da) * 6.0
    mb.box((1.6, 6.0, 3.2), (nx + math.cos(da) * 1.6, ny, z + 1.6), (0, 0, da), "Wood_SG_Dark", 0.05)
    mb.finish()
    light("L_SGCraft_Cauldron", "POINT", (cx, cy, z + 4.0), 700.0, (0.8, 0.55, 1.0), 0.6)
    light("L_SGCraft_Warm", "POINT", (cx, cy, z + 10.0), 900.0, (1.0, 0.7, 0.42), 1.0)


# ------------------------------------------------------------------ dungeon: portaria (P3) + 3 salas sob a ilha
def dungeon():
    rng = random.Random(91)
    mb = MB("SG_Dun_Blockout", "17_DUNGEON", rng, detail="far", floor=-999)
    cx, cy, w, d = L.DUNGEON_HOUSE
    z = L.P3
    t = 3.0
    ix0, iy0, ix1, iy1 = cx - w / 2 + t, cy - d / 2 + t, cx + w / 2 - t, cy + d / 2 - t
    top = z + 30.0
    dw, dh = L.DUNGEON_DOOR_W, L.DUNGEON_DOOR_H
    mb.box2((cx - w / 2, cy - d / 2, z - 0.2), (cx - dw / 2, iy0, top), "Stone_SG_Castle", 0.1)
    mb.box2((cx + dw / 2, cy - d / 2, z - 0.2), (cx + w / 2, iy0, top), "Stone_SG_Castle", 0.1)
    mb.box2((cx - dw / 2, cy - d / 2, z + dh), (cx + dw / 2, iy0, top), "Stone_SG_Castle", 0.1)
    mb.box2((cx - w / 2, iy1, z - 0.2), (cx + w / 2, cy + d / 2, top), "Stone_SG_Castle", 0.1)
    mb.box2((cx - w / 2, iy0, z - 0.2), (ix0, iy1, top), "Stone_SG_Castle", 0.1)
    mb.box2((ix1, iy0, z - 0.2), (cx + w / 2, iy1, top), "Stone_SG_Castle", 0.1)
    mb.box2((cx - w / 2 - 0.6, cy - d / 2 - 0.6, top), (cx + w / 2 + 0.6, cy + d / 2 + 0.6, top + 1.4), "Stone_SG_Trim", 0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tower(mb, cx + sx * (w / 2 - 1.5), cy + sy * (d / 2 - 1.5), 3.2, top - 6.0, top + 6.0, "Stone_SG_Castle",
                  "Roof_SG_Navy", 8.0)
    SL.spire(mb, (cx, cy), w * 0.42, top + 1.4, 18.0, "Roof_SG_Navy", n=4)
    box_walls_col("SG_DunHouse", (ix0, iy0, ix1, iy1), z - 0.5, top, t, doors=[("S", cx, dw, dh)])
    col_box2("SG_DunHouseRoof", (cx - w / 2, cy - d / 2, top), (cx + w / 2, cy + d / 2, top + 1.4))
    mb.box2((ix0, iy0, z - 0.2), (ix1, iy1, z + 0.04), "Stone_SG_Floor", 0.0)
    # portal espiral no fundo (a marca da dungeon): anel de pedra + disco violeta
    px, py = L.DUNGEON_PORTAL
    mb.cyl(5.6, 1.0, (px, py + 0.6, z + 7.0), (math.pi / 2, 0, 0), m="Stone_SG_Trim", n=20, bevel=0.0)
    mb.cyl(4.6, 0.4, (px, py + 0.2, z + 7.0), (math.pi / 2, 0, 0), m="SG_Violet_Glow", n=20, bevel=0.0)
    mb.box((12.0, 2.0, 1.2), (px, py + 0.6, z + 0.6), (0, 0, 0), "Stone_SG_Trim", 0.05)
    col_box("SG_DunPortal", (12.0, 2.0, 13.0), (px, py + 1.4, z + 6.5))
    # salas modulares sob a ilha: piso, paredes (vaos de ligacao), teto; tochas
    rooms = L.DUN_ROOMS
    for i, (nm, (x0, y0, x1, y1)) in enumerate(rooms):
        zf, zc = L.DUN_Z, L.DUN_CEIL
        mb.box2((x0, y0, zf - 2.0), (x1, y1, zf), "Stone_SG_Floor", 0.0)
        mb.box2((x0, y0, zc), (x1, y1, zc + 1.5), "Stone_SG_Castle", 0.0)
        doors = []
        yc = (y0 + y1) / 2
        if i > 0:
            doors.append(("W", yc, L.DUN_LINK_W, 12.0))
        if i < len(rooms) - 1:
            doors.append(("E", yc, L.DUN_LINK_W, 12.0))
        # paredes visuais (espessura 1) com os vaos
        for sd in ("S", "N", "W", "E"):
            ds = [dd for dd in doors if dd[0] == sd]
            if sd in ("S", "N"):
                yy = y0 - 0.5 if sd == "S" else y1 + 0.5
                mb.box2((x0 - 1.0, yy - 0.5, zf), (x1 + 1.0, yy + 0.5, zc), "Stone_SG_Block", 0.0)
            else:
                xx = x0 - 0.5 if sd == "W" else x1 + 0.5
                if ds:
                    _, c, ww, hh = ds[0]
                    mb.box2((xx - 0.5, y0, zf), (xx + 0.5, c - ww / 2, zc), "Stone_SG_Block", 0.0)
                    mb.box2((xx - 0.5, c + ww / 2, zf), (xx + 0.5, y1, zc), "Stone_SG_Block", 0.0)
                    mb.box2((xx - 0.5, c - ww / 2, zf + hh), (xx + 0.5, c + ww / 2, zc), "Stone_SG_Block", 0.0)
                else:
                    mb.box2((xx - 0.5, y0, zf), (xx + 0.5, y1, zc), "Stone_SG_Block", 0.0)
        box_walls_col("SG_DunRoom", (x0, y0, x1, y1), zf, zc, 1.0, doors=doors)
        col_box2("SG_DunRoom", (x0 - 1.0, y0 - 1.0, zf - 2.0), (x1 + 1.0, y1 + 1.0, zf))
        col_box2("SG_DunRoom", (x0 - 1.0, y0 - 1.0, zc), (x1 + 1.0, y1 + 1.0, zc + 1.5))
        for sx, sy in ((0.2, 0.15), (0.8, 0.85)):
            lx, ly = x0 + (x1 - x0) * sx, y0 + (y1 - y0) * sy
            light("L_SGDun_%s_%d" % (nm, int(sx * 10)), "POINT", (lx, ly, zf + 10.0), 1400.0, (0.72, 0.5, 1.0), 1.0)
    x0, y0, x1, y1 = dict(rooms)["R3"]
    mb.cyl(4.6, 0.4, (x1 - 0.8, (y0 + y1) / 2, L.DUN_Z + 6.5), (0, math.pi / 2, 0), m="SG_Violet_Glow", n=20, bevel=0.0)
    mb.finish()
    light("L_SGDun_Portal", "POINT", (px, py - 3.0, z + 7.0), 900.0, (0.66, 0.44, 1.0), 1.0)


# ------------------------------------------------------------------ agua: 4 cachoeiras frias (so visual)
def water():
    rng = random.Random(101)
    mb = MB("SG_Water_Blockout", "07_WATER", rng, detail="far", floor=-999)
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        mb.box((1.0, 7.0, z + 70.0), (x + ux * 2.5, y + uy * 2.5, (z - 70.0 + z) / 2 - 0.0), (0, 0, a), "Water_Fall", 0.0)
        mb.box((3.0, 8.0, 1.2), (x, y, z), (0, 0, a), "Foam", 0.0)
    mb.finish()


# ------------------------------------------------------------------ saida: ponte leste, ilhota do portao DS, ancora
def exit_():
    rng = random.Random(111)
    mb = MB("SG_Exit_Blockout", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    Ln = L.EXIT_BRIDGE_LEN
    c = L.exit_point(Ln / 2)
    mb.box((Ln, L.EXIT_W, 2.0), (c[0], c[1], L.EXIT_Z - 1.0), (0, 0, a), "Stone_SG_Block", 0.1)
    for s in (-1, 1):
        p0 = (L.EXIT_START[0] - uy * s * (L.EXIT_W / 2 + 0.6), L.EXIT_START[1] + ux * s * (L.EXIT_W / 2 + 0.6), L.EXIT_Z)
        e = L.exit_point(Ln)
        p1 = (e[0] - uy * s * (L.EXIT_W / 2 + 0.6), e[1] + ux * s * (L.EXIT_W / 2 + 0.6), L.EXIT_Z)
        SL.vis_parapet(mb, [p0, p1], h=1.6, w=1.0)
    for d in (Ln * 0.33, Ln * 0.67):
        p = L.exit_point(d)
        mb.cyl(5.0, 70.0, (p[0], p[1], L.EXIT_Z - 36.0), m="Cliff_Rock_SG_Dark", n=8, r2=2.4, bevel=0.0)
    ic = L.islet_center()
    mb.cyl(L.GATE_ISLET_R, 3.0, (ic[0], ic[1], L.EXIT_Z - 1.5), m="Stone_Paving_SG", n=24, bevel=0.0)
    for k, (f, dz) in enumerate(((0.95, -8.0), (0.7, -22.0), (0.4, -36.0))):
        mb.cyl(L.GATE_ISLET_R * f, 14.0, (ic[0], ic[1], L.EXIT_Z - 3.0 + dz + 7.0 - 7.0), m="Cliff_Rock_SG", n=12,
               r2=L.GATE_ISLET_R * f * 0.8, bevel=0.0)
    ap = L.anchor_pos()
    pc = (ap[0] - ux * 5.0, ap[1] - uy * 5.0)
    mb.box((10.0, L.DECK_W, 2.0), (pc[0], pc[1], L.EXIT_Z - 1.0), (0, 0, a), "Stone_Paving_SG", 0.05)
    mb.finish()


# ------------------------------------------------------------------ vestir: pinheiros, lanternas de rua, luzes da praca
def pine(mb, x, y, z, h, rng):
    mb.cyl(0.45, h * 0.3, (x, y, z + h * 0.15), m="Wood_SG_Dark", n=6, bevel=0.0)
    for k, (fr, fz) in enumerate(((1.0, 0.28), (0.74, 0.52), (0.48, 0.74))):
        mb.cyl(h * 0.18 * fr, h * 0.34, (x, y, z + h * fz), m="Leaf_SG_Pine", n=7, r2=0.15, bevel=0.0)


def dressing():
    rng = random.Random(121)
    mb = MB("SG_Veg_Blockout", "10_VEGETATION", rng, detail="far", floor=-999)
    for x, y, r, n in L.PINE_GROVES:
        for k in range(n):
            a = rng.uniform(0, 6.28)
            rr = rng.uniform(0, r)
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            z = L.zone_of(px, py)
            z = z if z is not None else L.P1 - 2.0
            h = rng.uniform(13.0, 20.0)
            pine(mb, px, py, z, h, rng)
            if L.zone_of(px, py) is not None:
                col_box("SG_VegPine", (1.2, 1.2, 8.0), (px, py, z + 4.0))
    mb.finish()
    mp = MB("SG_Prop_Blockout", "09_PROPS", rng, detail="far", floor=-999)
    cx, cy = L.PLAZA_C
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        x, y = cx + (L.PLAZA_R - 2.5) * math.cos(a), cy + (L.PLAZA_R - 2.5) * math.sin(a)
        mp.cyl(0.35, 7.0, (x, y, L.P1 + 3.5), m="Metal_SG_Iron", n=6, bevel=0.0)
        mp.box((1.0, 1.0, 1.4), (x, y, L.P1 + 7.4), (0, 0, 0), "Lantern_Glow", 0.0)
        col_box("SG_PropLamp", (0.8, 0.8, 7.0), (x, y, L.P1 + 3.5))
        light("L_SGProp_Plaza_%d" % k, "POINT", (x, y, L.P1 + 7.4), 250.0, (1.0, 0.72, 0.42), 0.3)
    mp.finish()


def build(skip=()):
    fns = {"terrain": terrain, "entry": entry, "village": village, "castle": castle, "hall": hall, "summon": summon,
           "craft": craft, "dungeon": dungeon, "water": water, "exit": exit_, "dressing": dressing}
    for z in ZONES:
        if z not in skip:
            fns[z]()
