# fm_terrain - lajes caminhaveis, niveis, escadas de acesso, penhascos e montanhas
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, col_ramp, coll, sub_coll, marker, arc, bezier
from fm_parts import (stairs, cliff_band, rock_scatter, pave_poly, fence, stone_parapet, masonry_wall, Frame, peak)
import fm_layout as L


def _skip_ranges(x0, x1, holes):
    """divide [x0,x1] tirando os intervalos 'holes'"""
    segs = []
    cur = x0
    for a, b in sorted(holes):
        if b <= cur or a >= x1:
            continue
        if a > cur:
            segs.append((cur, a))
        cur = max(cur, b)
    if cur < x1:
        segs.append((cur, x1))
    return segs


def build_ground():
    rng = random.Random(101)
    C = "02_TERRAIN"
    # ---------------- vale principal (z=4)
    g = MB("TER_Floor_Grass", C, rng)
    g.slab_poly(L.FLOOR_W, L.FLOOR, 8.0, "Grass")
    g.slab_poly(L.FLOOR_E, L.FLOOR, 8.0, "Grass")
    g.finish()
    col_box2("Floor", (L.WEST_X - 10, -62, -4), (L.RIVER_X[0], 46, L.FLOOR + 0.35))
    col_box2("Floor", (L.WEST_X - 10, 46, -4), (L.POOL[0], 62, L.FLOOR + 0.35))
    col_box2("Floor", (L.RIVER_X[1], -62, -4), (L.EAST_X + 10, 46, L.FLOOR + 0.35))
    col_box2("Floor", (L.POOL[2], 46, -4), (L.EAST_X + 10, 62, L.FLOOR + 0.35))

    # ---------------- patamar do spawn (z=0) + avenida + escadaria frontal
    s = MB("TER_Spawn_Ledge", C, rng)
    x0, y0, x1, y1 = L.SPAWN_PAD
    s.box2((x0, y0, -6), (x1, y1, L.SPAWN_Z - 0.35), "Stone_Dark", 0.3)
    pave_poly(s, [(x0 + 0.5, y0 + 0.5), (x1 - 0.5, y0 + 0.5), (x1 - 0.5, y1), (x0 + 0.5, y1)], L.SPAWN_Z - 0.35,
              rng, tile=2.8, h=0.35)
    ax0, ay0, ax1, ay1 = L.AVENUE
    s.box2((ax0 - 2, ay0 - 0.5, -6), (ax1 + 2, ay1, L.SPAWN_Z - 0.35), "Stone_Dark", 0.3)
    pave_poly(s, [(ax0, ay0), (ax1, ay0), (ax1, ay1), (ax0, ay1)], L.SPAWN_Z - 0.35, rng, tile=2.6, h=0.35)
    # escadaria frontal: 4 degraus de 1 (z0 -> z4), piso 2
    stairs(s, "Spawn", (0, L.FRONT_STAIRS_Y0, L.SPAWN_Z), D(90), 20, 4, 1.0, 2.0, "Stone_Light", "Stone_Dark",
           stringers=True)
    s.finish()
    col_box2("Spawn", (x0, y0, -6), (x1, y1, L.SPAWN_Z))
    col_box2("Spawn", (ax0 - 2, ay0 - 0.5, -6), (ax1 + 2, ay1, L.SPAWN_Z))
    # muretas do spawn (sul, leste, oeste) e da avenida - impedem queda no vazio
    pp = MB("TER_Spawn_Parapets", C, rng)
    stone_parapet(pp, "Spawn", [(x0, y1), (x0, y0), (x1, y0), (x1, y1)], h=2.4, w=1.8, rng=rng)
    stone_parapet(pp, "Spawn", [(x0, y1), (ax0 - 1, y1)], h=2.4, w=1.8, rng=rng)
    stone_parapet(pp, "Spawn", [(ax1 + 1, y1), (x1, y1)], h=2.4, w=1.8, rng=rng)
    for sx in (-1, 1):
        stone_parapet(pp, "Spawn", [(sx * (ax1 + 1), ay0), (sx * (ax1 + 1), ay1 + 0.5)], h=2.2, w=1.8, rng=rng)
    pp.finish()

    # ---------------- borda sul do vale: parapeito (menos a boca da escadaria e o rio)
    bs = MB("TER_South_Edge_Wall", C, rng)
    stone_parapet(bs, "FloorEdge", [(-52, -61.2, L.FLOOR), (-11.5, -61.2, L.FLOOR)], h=2.3, w=1.6, rng=rng)
    stone_parapet(bs, "FloorEdge", [(11.5, -61.2, L.FLOOR), (L.RIVER_X[0] - 1, -61.2, L.FLOOR)], h=2.3, w=1.6, rng=rng)
    stone_parapet(bs, "FloorEdge", [(L.RIVER_X[1] + 1, -61.2, L.FLOOR), (L.EAST_X - 1, -61.2, L.FLOOR)], h=2.3, w=1.6, rng=rng)
    bs.finish()

    # ---------------- ledge intermediario (z=14) com canal
    mid = MB("TER_MidLedge", C, rng)
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, [(L.SPILL_X - 4.5, L.SPILL_X + 4.5)]):
        mid.box2((a, L.MID_FRONT_Y, -2), (b, L.CANAL_Y[0], L.MID - 0.3), "Stone_Dark", 0.0)
        pave_poly(mid, [(a + 0.3, L.MID_FRONT_Y + 0.3), (b - 0.3, L.MID_FRONT_Y + 0.3),
                        (b - 0.3, L.CANAL_Y[0] - 0.2), (a + 0.3, L.CANAL_Y[0] - 0.2)],
                  L.MID - 0.3, rng, tile=2.6, h=0.3, grout=False)
        col_box2("MidLedge", (a, L.MID_FRONT_Y, -2), (b, L.CANAL_Y[0], L.MID))
    # leito do canal + parapeito frontal (aberto nas pontes)
    mid.box2((L.WEST_X, L.CANAL_Y[0], -2), (L.EAST_X, L.UPPER_FRONT_Y, 11.5), "Stone_Dark", 0.0)
    col_box2("MidLedge", (L.WEST_X, L.CANAL_Y[0], -2), (L.EAST_X, L.UPPER_FRONT_Y, 11.5))
    holes = [(px - 6.5, px + 6.5) for px in L.PORTAL_X]
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, holes):
        stone_parapet(mid, "MidLedge", [(a, L.CANAL_Y[0] + 0.8, L.MID - 0.3), (b, L.CANAL_Y[0] + 0.8, L.MID - 0.3)],
                      h=1.8, w=1.6, rng=rng)
        # parede interna do canal (face frontal)
        mid.box2((a, L.CANAL_Y[0], 11.4), (b, L.CANAL_Y[0] + 1.6, L.MID - 0.3), "Stone_Light", 0.15)
    # vertedouro atravessa o passeio: leito + passarela de tabuas
    mid.box2((L.SPILL_X - 4.5, L.MID_FRONT_Y, -2), (L.SPILL_X + 4.5, L.CANAL_Y[0], 11.5), "Stone_Dark", 0.0)
    for sx in (L.SPILL_X - 4.5, L.SPILL_X + 3.5):
        mid.box2((sx, L.MID_FRONT_Y, 11.5), (sx + 1.0, L.CANAL_Y[0], L.MID + 0.5), "Stone_Light", 0.15)
    col_box2("MidLedge", (L.SPILL_X - 4.5, L.MID_FRONT_Y, -2), (L.SPILL_X + 4.5, L.CANAL_Y[0], 11.5))
    for i in range(10):
        y = L.MID_FRONT_Y + 0.9 + i * 0.85
        mid.box((10.5, 0.75, 0.35), (L.SPILL_X, y, L.MID + 0.05), (0, 0, rng.uniform(-0.02, 0.02)), "Wood_Plank", 0.06)
    for sy in (L.MID_FRONT_Y + 0.8, L.CANAL_Y[0] - 0.8):
        mid.box((11.2, 0.6, 0.5), (L.SPILL_X, sy, L.MID - 0.3), (0, 0, 0), "Wood_Dark", 0.05)
    col_box2("MidLedge", (L.SPILL_X - 5, L.MID_FRONT_Y + 0.5, L.MID - 1.0), (L.SPILL_X + 5, L.CANAL_Y[0] - 0.5, L.MID + 0.2))
    mid.finish()

    # ---------------- terraco dos portais (z=26) com os pocos das escadas
    ter = MB("TER_PortalTerrace", C, rng)
    holes = [(px - 7.4, px + 7.4) for px in L.PORTAL_X] + [(-4.3, 4.3)]
    for a, b in _skip_ranges(L.WEST_X - 30, L.EAST_X + 30, holes):
        ter.box2((a, L.UPPER_FRONT_Y, -2), (b, L.TERR_BACK_Y + 30, L.TERR - 0.35), "Stone_Dark", 0.0)
        ter.box2((a, L.UPPER_FRONT_Y + 0.6, L.TERR - 0.8), (b, L.TERR_BACK_Y + 30, L.TERR - 0.05), "Grass", 0.0)
        col_box2("Terrace", (a, L.UPPER_FRONT_Y, -2), (b, L.TERR_BACK_Y + 30, L.TERR))
    ter.box2((-4.3, L.UPPER_FRONT_Y, -2), (4.3, L.TERR_BACK_Y + 30, L.TERR - 2.2), "Stone_Dark", 0.0)
    col_box2("Terrace", (-4.3, L.UPPER_FRONT_Y, -2), (4.3, L.TERR_BACK_Y + 30, L.TERR - 2.2))
    for px in L.PORTAL_X:
        ter.box2((px - 7.4, L.FLIGHT2_Y1, -2), (px + 7.4, L.TERR_BACK_Y + 30, L.TERR - 0.35), "Stone_Dark", 0.0)
        col_box2("Terrace", (px - 7.4, L.FLIGHT2_Y1, -2), (px + 7.4, L.TERR_BACK_Y + 30, L.TERR))
    for px in L.PORTAL_X:
        ter.box2((px - 7.4, L.FLIGHT2_Y1 + 0.6, L.TERR - 0.8), (px + 7.4, L.TERR_BACK_Y + 30, L.TERR - 0.05), "Grass", 0.0)
    ter.finish()

    # ---------------- escadas: lance 1 (vale -> ledge) e lance 2 (ledge -> terraco) + ponte sobre o canal
    st = MB("TER_PortalStairs", C, rng)
    for i, px in enumerate(L.PORTAL_X):
        stairs(st, "Stairs", (px, L.FLIGHT1_Y0, L.FLOOR), D(90), 12, 10, 1.0, 1.5, "Stone_Light", "Stone_Dark")
        # ponte de pedra sobre o canal (tabuleiro z=14)
        st.box2((px - 6.2, L.CANAL_Y[0] - 0.2, 12.3), (px + 6.2, L.UPPER_FRONT_Y + 0.2, L.MID - 0.3), "Stone_Light", 0.2)
        pave_poly(st, [(px - 6, L.CANAL_Y[0]), (px + 6, L.CANAL_Y[0]), (px + 6, L.UPPER_FRONT_Y),
                       (px - 6, L.UPPER_FRONT_Y)], L.MID - 0.3, rng, tile=2.4, h=0.3, grout=False)
        for sx in (-1, 1):
            stone_parapet(st, "Stairs", [(px + sx * 6.9, L.CANAL_Y[0] - 0.4, L.MID - 0.3),
                                         (px + sx * 6.9, L.UPPER_FRONT_Y + 0.2, L.MID - 0.3)], h=1.6, w=1.2, rng=rng)
        col_box2("Stairs", (px - 6.2, L.CANAL_Y[0] - 0.2, 11.0), (px + 6.2, L.UPPER_FRONT_Y + 0.2, L.MID))
        # lance 2: degraus de 1 (MID -> TERR) dentro do poco do terraco
        stairs(st, "Stairs", (px, L.UPPER_FRONT_Y, L.MID), D(90), 12, int(L.TERR - L.MID), 1.0,
               (L.FLIGHT2_Y1 - L.UPPER_FRONT_Y) / (L.TERR - L.MID), "Stone_Light", "Stone_Dark")
    st.finish()


# ------------------------------------------------------------------ penhascos e montanhas
def build_cliffs():
    rng = random.Random(202)
    C = "02_TERRAIN"
    # parede do ledge (y=62, face sul) - colunas na frente da linha, topo ~14
    cm = MB("TER_Cliff_MidWall", C, rng)
    holes = [(px - 8.5, px + 8.5) for px in L.PORTAL_X] + [(L.SPILL_X - 5.5, L.SPILL_X + 5.5)]
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, holes):
        if b - a < 3:
            continue
        cliff_band(cm, [(a + 2, L.MID_FRONT_Y - 1.5), (b - 2, L.MID_FRONT_Y - 1.5)], L.FLOOR - 1, L.MID - 0.4, rng,
                   depth=1.4, rmin=2.6, rmax=4.4, step=4.6, grass=False, var=0.8, face_side=1)
        col_box2("MidWall", (a, L.MID_FRONT_Y - 4.5, L.FLOOR - 1), (b, L.MID_FRONT_Y, L.MID))
    cm.finish()

    # parede superior (y=80, z 14->26): alvenaria atras do canal + berma de rocha no alto
    cu = MB("TER_Cliff_UpperWall", C, rng)
    holes = [(px - 7.4, px + 7.4) for px in L.PORTAL_X] + [(-3.6, 3.6)]
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, holes):
        masonry_wall(cu, (a, L.UPPER_FRONT_Y - 0.6), (b, L.UPPER_FRONT_Y - 0.6), 11.5, L.TERR - 0.3, 1.4, rng,
                     "Stone_Light", "Stone_Dark", course=2.0, mix=0.3)
        if b - a > 12:
            cliff_band(cu, [(a + 4, L.UPPER_FRONT_Y + 4), (b - 4, L.UPPER_FRONT_Y + 4)], L.TERR - 3, L.TERR + 2.5,
                       rng, depth=1.5, rmin=2.4, rmax=4.0, step=5.5, grass=True, var=1.2, face_side=-1, strata=False)
            col_box2("UpperWall", (a, L.UPPER_FRONT_Y, L.TERR - 1), (b, L.UPPER_FRONT_Y + 8, L.TERR + 4))
    # pilastras de pedra com lanterna e trepadeiras (quebram a monotonia do muro de arrimo)
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, holes):
        span = b - a
        if span < 14:
            continue
        k = max(1, int(span / 17))
        for i in range(k):
            x = a + span * (i + 0.5) / k
            if abs(x) < 6:
                continue
            cu.box((3.0, 2.2, L.TERR + 1.2 - 11.5), (x, L.UPPER_FRONT_Y - 1.6, (11.5 + L.TERR + 1.2) / 2), (0, 0, 0),
                   "Stone_Light", 0.25)
            cu.box((3.6, 2.8, 0.9), (x, L.UPPER_FRONT_Y - 1.6, L.TERR + 1.5), (0, 0, 0), "Stone_Dark", 0.2)
            for j in range(rng.randint(2, 4)):
                vx = x + rng.uniform(-7, 7)
                if abs(vx - x) < 2.2:
                    continue
                top = L.TERR - 0.2
                ln = rng.uniform(4.0, 9.0)
                pts = [Vector((vx, L.UPPER_FRONT_Y - 1.4, top)), Vector((vx + rng.uniform(-0.6, 0.6), L.UPPER_FRONT_Y - 1.5,
                       top - ln * 0.5)), Vector((vx + rng.uniform(-0.8, 0.8), L.UPPER_FRONT_Y - 1.45, top - ln))]
                cu.tube(pts, 0.35, "Leaf_Pine_Light", 5)
                for q in pts[1:]:
                    cu.ico(0.7, q, "Leaf_Pine", 1, (1, 0.5, 1))
    cu.finish()

    # bordas do vale: oeste (macico SW + oeste), leste, sul (queda)
    cw = MB("TER_Cliff_West", C, rng)
    fw = L.FLOOR_W
    west = [fw[0], fw[10], fw[9], fw[8], fw[7], fw[6], fw[5]]   # sul -> norte pela borda oeste
    # face da mina (fw[10]->fw[9]) fica livre: o portal da mina e modelado em fm_mine
    cliff_band(cw, [(fw[0][0] - 1, -63), (fw[10][0] - 1, fw[10][1] + 1)], L.FLOOR - 2, 30, rng, depth=2, rmin=4,
               rmax=7, step=5, face_side=-1)
    cliff_band(cw, [fw[9], fw[8], fw[7], fw[6], (fw[5][0] - 1, fw[5][1] + 2)], L.FLOOR - 2, 34, rng,
               depth=3, rmin=4.5, rmax=7.5, step=6, face_side=-1, top_fn=lambda c: 30 + 8 * math.sin(c.y * 0.07))
    for a, b in zip(west, west[1:]):
        if (a, b) == (fw[10], fw[9]):
            continue  # face da mina: colisao propria em fm_mine
        d = Vector(b) - Vector(a)
        c = (Vector(a) + Vector(b)) / 2
        n = Vector((-d.y, d.x)).normalized()
        cc = c + n * 3.0
        col_box("WestCliff", (d.length + 4, 8, 60), (cc.x, cc.y, 26), (0, 0, math.atan2(d.y, d.x)))
    cw.finish()

    ce = MB("TER_Cliff_East", C, rng)
    cliff_band(ce, [(L.EAST_X + 2, -60), (L.EAST_X + 2, 64)], L.FLOOR - 2, 34, rng, depth=3, rmin=4.5, rmax=7.5,
               step=6, face_side=1, top_fn=lambda c: 32 + 7 * math.sin(c.y * 0.08 + 1))
    col_box2("EastCliff", (L.EAST_X, -64, -2), (L.EAST_X + 10, 64, 60))
    ce.finish()

    # queda sul (abaixo do vale e do spawn) - rocha pendente para o vazio
    cs = MB("TER_Cliff_South", C, rng)
    cliff_band(cs, [(fw[0][0] - 4, -63.5), (-12, -63.5)], -46, L.FLOOR - 0.5, rng, depth=1.5, rmin=4, rmax=7, step=6,
               face_side=1, grass=True, var=1.0)
    cliff_band(cs, [(12, -63.5), (L.EAST_X + 2, -63.5)], -46, L.FLOOR - 0.5, rng, depth=1.5, rmin=4, rmax=7, step=6,
               face_side=1, grass=True, var=1.0)
    x0, y0, x1, y1 = L.SPAWN_PAD
    cliff_band(cs, [(-12, -71), (-12, -92), (x0 - 1, -92), (x0 - 1, y0 - 1), (x1 + 1, y0 - 1), (x1 + 1, -92),
                    (12, -92), (12, -71)], -46, L.SPAWN_Z - 0.6, rng, depth=1.5, rmin=4, rmax=6.5, step=5.5,
               face_side=-1, grass=True, var=0.8)
    for sx in (-1, 1):
        cliff_band(cs, [(sx * 13, -70), (sx * 13, -62)], -2, L.FLOOR - 0.3, rng, depth=1, rmin=2.5, rmax=3.5,
                   step=3.5, grass=True, var=0.3, face_side=sx)
    cs.finish()


def build_mountains():
    """macicos que fecham o vale: SW (mina), N atras do terraco, leste e picos de fundo"""
    rng = random.Random(303)
    C = "02_TERRAIN"
    fw = L.FLOOR_W
    m = MB("TER_Mountains_Near", C, rng)
    # macico SW: faixas recuadas subindo em terracos (acima do teto do tunel da mina)
    for k, (off, top) in enumerate(((14, 52), (30, 74)), start=1):
        pts = [(fw[0][0] - 6 - off * 0.3, -68 - off), (fw[10][0] - 8 - off, fw[10][1] - 6 - off * 0.6),
               (fw[9][0] - 8 - off, fw[9][1] - 6 - off * 0.3), (fw[8][0] - 8 - off, fw[8][1] - off * 0.2),
               (fw[7][0] - 8 - off, fw[7][1]), (fw[6][0] - 8 - off, 30), (fw[5][0] - 8 - off, 70)]
        cliff_band(m, pts, L.FLOOR - 2 + k * 18, top, rng, depth=4, rmin=6, rmax=10, step=8, face_side=-1,
                   top_fn=lambda c, t=top: t + 6 * math.sin(c.x * 0.05 + c.y * 0.03))
    sw = [(fw[0][0] - 4, -70), (-110, -115), (-200, -80), (-200, 80), (fw[5][0] - 10, 72), fw[5], fw[6], fw[7],
          fw[8], fw[9], fw[10]]
    m.prism(sw, 19, 29.2, "Cliff_Rock_Dark")
    m.prism(sw, 29.2, 30.0, "Grass_Dark")
    # saia de penhasco fechando o macico por fora (sul/oeste): o tunel da mina nunca aparece de fora
    cliff_band(m, [(fw[0][0] - 2, -74), (-110, -121), (-206, -84), (-206, 84)], -46, 31, rng, depth=2.5, rmin=6,
               rmax=9, step=7.5, face_side=1, top_fn=lambda c: 30 + 4 * math.sin(c.x * 0.07))
    # atras do terraco (y>122): faixas subindo
    for k, (y, top) in enumerate(((124, 48), (140, 70), (162, 96))):
        pts = [(-78, y), (-30, y + 3), (20, y - 2), (70, y + 2), (120, y), (L.EAST_X + 25, y - 4)]
        cliff_band(m, pts, L.TERR - 2 + k * 16, top, rng, depth=4, rmin=6.5, rmax=11, step=8.5, face_side=1,
                   top_fn=lambda c, t=top: t + 9 * math.sin(c.x * 0.045 + 2))
        pts = [(L.WEST_X - 40, y + 10), (L.WEST_X - 6, y)]
        cliff_band(m, pts, L.TERR - 2 + k * 16, top + 6, rng, depth=4, rmin=6.5, rmax=11, step=8.5, face_side=1)
    col_box2("BackMountain", (-78, L.TERR_BACK_Y, 0), (L.EAST_X + 30, L.TERR_BACK_Y + 30, 90))
    col_box2("BackMountain", (L.WEST_X - 40, L.TERR_BACK_Y, 0), (-116, L.TERR_BACK_Y + 30, 90))
    # lado leste: rampa de penhascos
    for k, (x, top) in enumerate(((L.EAST_X + 10, 52), (L.EAST_X + 26, 76))):
        cliff_band(m, [(x, -70), (x + 4, 40), (x, 130)], L.FLOOR - 2 + k * 20, top, rng, depth=4, rmin=6.5, rmax=10,
                   step=8.5, face_side=1, top_fn=lambda c, t=top: t + 8 * math.sin(c.y * 0.05))
    for poly, z0, z1 in (([(L.EAST_X + 8, -80), (L.EAST_X + 100, -80), (L.EAST_X + 100, 200), (L.EAST_X + 12, 200),
                          (L.EAST_X + 16, 60)], -40, 40),
                         ([(-78, 128), (L.EAST_X + 40, 128), (L.EAST_X + 40, 260), (-72, 260)], 0, 44),
                         ([(L.WEST_X - 60, 128), (-118, 128), (-118, 260), (L.WEST_X - 60, 260)], 0, 44)):
        m.prism(poly, z0, z1 - 0.8, "Cliff_Rock_Dark")
        m.prism(poly, z1 - 0.8, z1, "Grass_Dark")
    # lateral oeste do terraco
    cliff_band(m, [(L.WEST_X - 1, 64), (L.WEST_X - 2, 124)], L.MID - 2, 52, rng, depth=3, rmin=5, rmax=8, step=6.5,
               face_side=-1)
    col_box2("WestCliff", (L.WEST_X - 12, 62, 0), (L.WEST_X, 124, 70))
    cliff_band(m, [(L.EAST_X + 1, 64), (L.EAST_X + 2, 124)], L.MID - 2, 52, rng, depth=3, rmin=5, rmax=8, step=6.5,
               face_side=1)
    col_box2("EastCliff", (L.EAST_X, 62, 0), (L.EAST_X + 12, 124, 70))
    m.finish()

    # picos de fundo (silhueta alta, estratos grandes)
    p = MB("TER_Mountains_Peaks", C, rng)
    peaks = [(-160, 200, 150, 34), (-40, 230, 175, 40), (50, 250, 160, 38), (140, 205, 185, 42),
             (230, 110, 140, 36), (-230, 60, 130, 34), (220, -40, 110, 30), (-210, -90, 105, 30),
             (100, 330, 210, 55), (-120, 330, 190, 50)]
    from fm_parts import peak
    for (x, y, h, r) in peaks:
        peak(p, x, y, r * 1.5, h, rng, z0=10.0)
    p.finish()

    # vale distante sob a nevoa (fundo)
    f = MB("TER_Far_Valley", C, rng)
    f.box((2400, 2400, 2), (0, 0, -70), (0, 0, 0), "Grass_Dark", 0.0)
    for i in range(40):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(260, 700)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rng.uniform(40, 140)
        f.cyl(rng.uniform(40, 90), h, (x, y, -70 + h / 2), (0, 0, rng.uniform(0, 6)),
              rng.choice(("Cliff_Rock", "Cliff_Rock_Dark")), rng.choice((5, 6, 7)), r2=rng.uniform(8, 30), bevel=0.0)
    f.finish()