# fm_terrain - lajes caminhaveis, niveis, escadas de acesso, penhascos e montanhas
# Modulos do tema: fm_terrain_ground (chao em manchas, desgaste, ondulacoes), fm_terrain_walls (muro de arrimo dos
# portais, mureta sul, esporoes, contrafortes das cachoeiras), fm_terrain_ridges (skyline com hierarquia),
# fm_terrain_guardian (busto esculpido na dominante NE), fm_terrain_detail (nivel de detalhe das caixas).
import math, random
import bpy, bmesh
from mathutils import Vector, noise
import fm_lib
from fm_lib import MB, D, col_box, col_box2, col_ramp, coll, sub_coll, marker, arc, bezier, point_in_poly
from fm_parts import (stairs, cliff_band, rock_scatter, pave_poly, fence, stone_parapet, masonry_wall, Frame, peak)
import fm_layout as L
import fm_terrain_ridges
import fm_terrain_ground as G
import fm_terrain_walls as W
from fm_terrain_detail import TMB

# materiais do terreno (faixa de topo clara das massas de rocha; musgo de altitude nos tampos)
fm_lib.MATS.setdefault("Cliff_Rock_Top", ((0.33, 0.32, 0.305), 0.9, 0.0, 0, None, 0.10))
fm_lib.MATS.setdefault("Leaf_Moss", ((0.120, 0.270, 0.035), 0.9, 0.0, 0, None, 0.14))

# colisoes de borda (o visual nao muda): topo acima do alcance do pulo (7,2) a partir do piso
SPAWN_COL_TOP = 12.0      # muretas do spawn/avenida e banzos da escadaria frontal (piso z0)
EDGE_COL_TOP = 16.0       # borda sul do vale (piso z4)
CANAL_COL_TOP = 16.2      # parapeito do canal do ledge (mureta visual ~15.5)
CANAL_BED = 13.0          # leito de colisao do canal: fosso fechado sem armadilha
LEDGE_X1 = 131.0          # fim do piso do ledge/canal a leste (rocha da encosta a partir daqui)

_VALLEY = None            # consultas de area livre do vale (talude, ondulacoes) - fm_terrain_ground.Valley


def crest(base, amp, freq=0.03, seed=0.0, lo=None):
    """cota de crista irregular (ruido coerente em 2 oitavas + quebras), no lugar do seno regular"""
    def f(c):
        p = Vector((c.x * freq + seed, c.y * freq - seed * 0.7, seed * 0.31))
        n1 = noise.noise(p)
        n2 = noise.noise(p * 2.9 + Vector((7.1, 3.3, 1.7)))
        v = base + amp * (2.4 * n1 + 1.1 * n2)
        return v if lo is None else max(lo, v)
    return f


def _skip_ranges(x0, x1, holes):
    """divide [x0,x1] tirando os intervalos 'holes'"""
    return W.skip_ranges(x0, x1, holes)


def offset_line(pts, d):
    """polilinha deslocada d para a ESQUERDA do sentido de percurso (mitra nos vertices)"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    out = []
    for i, p in enumerate(P):
        ns = []
        if i > 0:
            t = (p - P[i - 1]).normalized()
            ns.append(Vector((-t.y, t.x, 0.0)))
        if i < len(P) - 1:
            t = (P[i + 1] - p).normalized()
            ns.append(Vector((-t.y, t.x, 0.0)))
        n = sum(ns, Vector()).normalized()
        k = 1.0 / max(0.5, n.dot(ns[0]))
        q = p + n * (d * k)
        out.append((q.x, q.y))
    return out


def _valley_ok(margin=0.8):
    def ok(x, y):
        return _VALLEY is not None and _VALLEY.free(x, y, margin)
    return ok


def parapet(mb, area, pts, col_top=None, **kw):
    """stone_parapet com a colisao ate a cota ABSOLUTA col_top: mureta de borda de abismo (acima do alcance do pulo
    a partir do piso: o topo nao vira passarela invisivel) ou parapeito do canal (colisao rente a mureta visual);
    o visual nao muda. col_top None = colisao padrao (h + 2 acima da base)."""
    n0 = fm_lib._COL_COUNT.get(area, 0)
    stone_parapet(mb, area, pts, **kw)
    if col_top is None:
        return
    h = kw.get("h", 2.2)
    for i in range(n0 + 1, fm_lib._COL_COUNT.get(area, 0) + 1):
        o = bpy.data.objects.get("COL_%s_%03d" % (area, i))
        if o is None:
            continue
        zb = o.location.z - o.scale.z / 2
        if col_top > zb + h:
            o.scale.z = col_top - zb
            o.location.z = zb + o.scale.z / 2


# ------------------------------------------------------------------ chao, niveis e escadas
def build_ground():
    global _VALLEY
    rng = random.Random(101)
    C = "02_TERRAIN"
    # ---------------- vale principal (z=4): laje de terra + gramado elevado em manchas (fm_terrain_ground)
    _VALLEY = G.valley_ground(C, random.Random(111))
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
    before = {o.name for o in bpy.data.objects if o.name.startswith("COL_Spawn")}
    stairs(s, "Spawn", (0, L.FRONT_STAIRS_Y0, L.SPAWN_Z), D(90), 20, 4, 1.0, 2.0, "Stone_Light", "Stone_Dark",
           stringers=True)
    # banzos: colisao alta (o topo do banzo nao vira atalho ate a mureta da avenida nem para fora)
    for o in bpy.data.objects:
        # so banzos (blocos altos); a "meia pisada" plana do topo (fm_parts.stairs, 1.0 de altura) fica como esta
        if (o.name.startswith("COL_Spawn") and o.name not in before and o.get("col_kind") == "Block"
                and o.scale.z > 2.0):
            zb = o.location.z - o.scale.z / 2
            o.scale.z = SPAWN_COL_TOP - zb
            o.location.z = zb + o.scale.z / 2
    s.finish()
    col_box2("Spawn", (x0, y0, -6), (x1, y1, L.SPAWN_Z))
    col_box2("Spawn", (ax0 - 2, ay0 - 0.5, -6), (ax1 + 2, ay1, L.SPAWN_Z))
    # muretas do spawn (sul, leste, oeste) e da avenida - impedem queda no vazio (colisao alta, visual igual)
    pp = MB("TER_Spawn_Parapets", C, rng)
    # parapeito sul com a ABERTURA do portao para as ilhas (fm_terrain_isles: pilares em +-(gw + 1.3))
    gw = L.ISLES_GATE_HW
    parapet(pp, "Spawn", [(x0, y1), (x0, y0), (-gw - 2.6, y0)], SPAWN_COL_TOP, h=2.4, w=1.8, rng=rng)
    parapet(pp, "Spawn", [(gw + 2.6, y0), (x1, y0), (x1, y1)], SPAWN_COL_TOP, h=2.4, w=1.8, rng=rng)
    parapet(pp, "Spawn", [(x0, y1), (ax0 - 1, y1)], SPAWN_COL_TOP, h=2.4, w=1.8, rng=rng)
    parapet(pp, "Spawn", [(ax1 + 1, y1), (x1, y1)], SPAWN_COL_TOP, h=2.4, w=1.8, rng=rng)
    for sx in (-1, 1):
        parapet(pp, "Spawn", [(sx * (ax1 + 1), ay0), (sx * (ax1 + 1), ay1 + 0.5)], SPAWN_COL_TOP, h=2.2, w=1.8,
                rng=rng)
    pp.finish()
    import fm_terrain_isles
    fm_terrain_isles.build(random.Random(2209))

    # ---------------- borda sul do vale: mureta de blocos variados + afloramentos (menos a escadaria e o rio)
    W.south_wall(C, rng, [(-52, -11.5), (11.5, L.RIVER_X[0] - 1), (L.RIVER_X[1] + 1, L.EAST_X - 1)], -61.2, L.FLOOR,
                 2.3, 1.6, EDGE_COL_TOP)
    # guarda invisivel na saida do rio: a agua cai no penhasco sul, o jogador nao
    col_box2("FloorEdge", (L.RIVER_X[0] - 1.2, -62.8, -2.0), (L.RIVER_X[1] + 1.2, -61.8, EDGE_COL_TOP))

    # ---------------- ledge intermediario (z=14) com canal
    mid = TMB("TER_MidLedge", C, rng, detail="far")
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, [(L.SPILL_X - 4.5, L.SPILL_X + 4.5)]):
        mid.box2((a, L.MID_FRONT_Y, -2), (b, L.CANAL_Y[0], L.MID - 0.3), "Stone_Dark", 0.0)
        pave_poly(mid, [(a + 0.3, L.MID_FRONT_Y + 0.3), (b - 0.3, L.MID_FRONT_Y + 0.3),
                        (b - 0.3, L.CANAL_Y[0] - 0.2), (a + 0.3, L.CANAL_Y[0] - 0.2)],
                  L.MID - 0.3, rng, tile=2.6, h=0.3, grout=False)
        col_box2("MidLedge", (a, L.MID_FRONT_Y, -2), (min(b, LEDGE_X1), L.CANAL_Y[0], L.MID))
    # leito do canal + parapeito frontal (aberto nas pontes): fosso fechado (leito de colisao a 13)
    mid.box2((L.WEST_X, L.CANAL_Y[0], -2), (L.EAST_X, L.UPPER_FRONT_Y, 11.5), "Stone_Dark", 0.0)
    col_box2("MidLedge", (L.WEST_X, L.CANAL_Y[0], -2), (LEDGE_X1, L.UPPER_FRONT_Y, CANAL_BED))
    holes = [(px - 6.5, px + 6.5) for px in L.PORTAL_X]
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, holes):
        parapet(mid, "MidLedge", [(a, L.CANAL_Y[0] + 0.8, L.MID - 0.3), (b, L.CANAL_Y[0] + 0.8, L.MID - 0.3)],
                CANAL_COL_TOP, h=1.8, w=1.6, rng=rng)
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

    # ---------------- terraco dos portais (z=30) com os pocos das escadas: enchimento de pedra ate 29.2 e gramado
    # em manchas por cima (sem faixas coplanares de pedra x grama nos cortes das escadas)
    ter = TMB("TER_PortalTerrace", C, rng, detail="far")
    zf = L.TERR - 0.8
    holes = [(px - 7.4, px + 7.4) for px in L.PORTAL_X] + [(-4.3, 4.3)]
    for a, b in _skip_ranges(L.WEST_X - 30, L.EAST_X + 30, holes):
        ter.box2((a, L.UPPER_FRONT_Y, -2), (b, L.TERR_BACK_Y + 30, zf), "Stone_Dark", 0.0)
        col_box2("Terrace", (a, L.UPPER_FRONT_Y, -2), (min(b, L.EAST_X + 1.0), L.TERR_BACK_Y + 30, L.TERR))
    ter.box2((-4.3, L.UPPER_FRONT_Y, -2), (4.3, L.TERR_BACK_Y + 30, L.TERR - 2.2), "Stone_Dark", 0.0)
    col_box2("Terrace", (-4.3, L.UPPER_FRONT_Y, -2), (4.3, L.TERR_BACK_Y + 30, L.TERR - 2.2))
    for px in L.PORTAL_X:
        ter.box2((px - 7.4, L.FLIGHT2_Y1, -2), (px + 7.4, L.TERR_BACK_Y + 30, zf), "Stone_Dark", 0.0)
        col_box2("Terrace", (px - 7.4, L.FLIGHT2_Y1, -2), (px + 7.4, L.TERR_BACK_Y + 30, L.TERR))
    ter.finish()
    G.terrace_ground(C, random.Random(121))

    # ---------------- escadas: lance 1 (vale -> ledge) e lance 2 (ledge -> terraco) + ponte sobre o canal
    st = TMB("TER_PortalStairs", C, rng, detail="near")
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
    talus_valley = dict(z=G.Z_LAWN, ok=_valley_ok(0.6), every=10.0)
    # parede do ledge (y=62, face sul): face das massas alinhada a colisao (sem plataforma invisivel na frente)
    cm = MB("TER_Cliff_MidWall", C, rng)
    holes = [(px - 8.5, px + 8.5) for px in L.PORTAL_X] + [(L.SPILL_X - 5.5, L.SPILL_X + 5.5)]
    for a, b in _skip_ranges(L.WEST_X, L.EAST_X, holes):
        if b - a < 3:
            continue
        cliff_band(cm, [(a + 2, L.MID_FRONT_Y - 0.9), (b - 2, L.MID_FRONT_Y - 0.9)], L.FLOOR - 1, L.MID - 0.6, rng,
                   depth=1.4, rmin=2.6, rmax=4.4, step=4.6, grass=False, var=0.8, face_side=-1, front=0.3,
                   detail="far", talus=talus_valley)
        col_box2("MidWall", (a, L.MID_FRONT_Y - 1.2, L.FLOOR - 1), (b, L.MID_FRONT_Y, L.MID))
    cm.finish()

    # parede superior (y=80, z 14->30): muro de arrimo com afloramentos, entalhes, pilastras e hera + contrafortes
    W.retaining_wall(C, rng)

    # bordas do vale: oeste (macico SW + oeste), leste, sul (queda)
    cw = MB("TER_Cliff_West", C, rng)
    fw = L.FLOOR_W
    west = [fw[0], fw[10], fw[9], fw[8], fw[7], fw[6], fw[5]]   # sul -> norte pela borda oeste
    # face da mina (fw[10]->fw[9]) fica livre: o portal da mina e modelado em fm_mine
    # (linha 1 stud para fora do piso + frente limitada: as massas nao invadem o piso caminhavel)
    cliff_band(cw, offset_line([(fw[0][0] - 1, -63), (fw[10][0] - 1, fw[10][1] + 1)], 1.0), L.FLOOR - 2, 30, rng,
               depth=2, rmin=4, rmax=7, step=5, face_side=-1, front=1.5, talus=talus_valley)
    cliff_band(cw, offset_line([fw[9], fw[8], fw[7], fw[6], (fw[5][0] - 1, fw[5][1] + 2)], 1.0), L.FLOOR - 2, 34, rng,
               depth=3, rmin=4.5, rmax=7.5, step=6, face_side=-1, top_fn=crest(32, 2.6, 0.035, 1.3), front=1.5,
               talus=talus_valley)
    for a, b in zip(west, west[1:]):
        if (a, b) == (fw[10], fw[9]):
            continue  # face da mina: colisao propria em fm_mine
        d = Vector(b) - Vector(a)
        c = (Vector(a) + Vector(b)) / 2
        n = Vector((-d.y, d.x)).normalized()
        cc = c + n * 3.0
        col_box("WestCliff", (d.length + 4, 8, 60), (cc.x, cc.y, 26), (0, 0, math.atan2(d.y, d.x)))
    cw.finish()

    # leste: polilinha com contrafortes e reentrancias (4-8 studs atras da colisao, que fica reta em x=135)
    ce = MB("TER_Cliff_East", C, rng)
    ex = L.EAST_X
    east = [(ex + 2.5, -60), (ex + 8.5, -38), (ex + 3.0, -14), (ex + 9.5, 12), (ex + 2.5, 36), (ex + 6.0, 64)]

    def east_ok(x, y):
        return x > ex + 0.3 or _valley_ok(0.6)(x, y)
    cliff_band(ce, east, L.FLOOR - 2, 34, rng, depth=3, rmin=4.5, rmax=7.5, step=6, face_side=1,
               top_fn=crest(33, 2.6, 0.035, 4.1), front=1.5, talus=dict(z=L.FLOOR, ok=east_ok, every=9.0))
    col_box2("EastCliff", (L.EAST_X, -64, -2), (L.EAST_X + 10, 64, 60))
    ce.finish()

    # queda sul (abaixo do vale e do spawn) - rocha pendente para o vazio
    # (face para o SUL = o vazio; as massas ficam sob a laje e a borda de grama nao fura o piso nem o pavimento)
    cs = MB("TER_Cliff_South", C, rng)
    # (bordas vistas do spawn: grama caindo em linguetas pela face, nada de laje reta de 'cobertura de bolo')
    cliff_band(cs, [(fw[0][0] - 4, -63.5), (-12, -63.5)], -46, L.FLOOR - 1.0, rng, depth=1.5, rmin=4, rmax=7, step=6,
               face_side=-1, grass=True, var=1.0, detail="far", tongues="always")
    cliff_band(cs, [(12, -63.5), (L.EAST_X + 2, -63.5)], -46, L.FLOOR - 1.0, rng, depth=1.5, rmin=4, rmax=7, step=6,
               face_side=-1, grass=True, var=1.0, detail="far", tongues="always")
    x0, y0, x1, y1 = L.SPAWN_PAD
    cliff_band(cs, [(-12, -71), (-12, -92), (x0 - 1, -92), (x0 - 1, y0 - 1), (x1 + 1, y0 - 1), (x1 + 1, -92),
                    (12, -92), (12, -71)], -46, L.SPAWN_Z - 1.3, rng, depth=1.5, rmin=4, rmax=6.5, step=5.5,
               face_side=-1, grass=True, var=0.8, detail="far", tongues="always")
    for sx in (-1, 1):
        cliff_band(cs, [(sx * 13, -70), (sx * 13, -62)], -2, L.FLOOR - 0.3, rng, depth=1, rmin=2.5, rmax=3.5,
                   step=3.5, grass=True, var=0.3, face_side=sx, detail="far", tongues="always")
    # esporoes de rocha saindo para fora da mureta sul (quebram a borda reta vista do spawn)
    for x in (30.0, 100.0):
        W.spur(cs, x, rng)
    cs.finish()


def _decimate_far(ob, center=(0.0, -26.0), dist=150.0, angle=5.0):
    """dissolucao planar (angulo baixo) nas faces longe da praca: menos triangulos onde ninguem chega perto"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    c = Vector(center)
    far = {f for f in bm.faces if (f.calc_center_median().xy - c).length > dist}
    edges = [e for e in bm.edges if e.link_faces and all(f in far for f in e.link_faces)]
    verts = [v for v in bm.verts if v.link_faces and all(f in far for f in v.link_faces)]
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), use_dissolve_boundaries=False, verts=verts,
                             edges=edges, delimit={"MATERIAL"})
    bm.to_mesh(me)
    bm.free()


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
        cliff_band(m, pts, (20.0, 29.0)[k - 1], top, rng, depth=4, rmin=7.0, rmax=12.0, step=8, face_side=-1,
                   top_fn=crest(top, 3.2, 0.035, 3.7 * k), detail=("far" if k == 2 else None))
    sw = [(fw[0][0] - 4, -70), (-110, -115), (-200, -80), (-200, 80), (fw[5][0] - 10, 72), fw[5], fw[6], fw[7],
          fw[8], fw[9], fw[10]]
    m.prism(sw, 19, 29.2, "Cliff_Rock_Dark")
    m.prism(sw, 29.2, 30.0, "Grass_Dark")
    # topo do macico: cabecos de rocha e patamares quebrando o tampo liso (longe do tunel da mina)
    for (hx, hy, top, r) in ((-162.0, -46.0, 50.0, 11.0), (-172.0, 34.0, 58.0, 9.0), (-132.0, -98.0, 44.0, 8.0)):
        peak(m, hx, hy, r, top - 30.0, rng, z0=30.0, kind=rng.choice(("mesa", "horn")), root=26.0,
             face=(-60.0 - hx, -10.0 - hy), top_m="Grass_Dark")
    # saia de penhasco fechando o macico por fora (sul/oeste): o tunel da mina nunca aparece de fora; alturas
    # alternando 25-45 (as massas altas avancam sobre a borda do tampo) + 2 chifres altos
    # (back: a camara de cristais fica a ~16 studs da linha, entao as massas crescem para FORA e nao a invadem)
    def skirt_top(c):
        v = noise.noise(Vector((c.x * 0.022 + 9.2, c.y * 0.022, 0.4)))
        return max(25.0, min(45.0, 35.0 + 17.0 * v))
    cliff_band(m, [(fw[0][0] - 2, -74), (-110, -121), (-206, -84), (-206, 84)], -46, 31, rng, depth=2.5, rmin=6,
               rmax=9, step=7.5, face_side=1, top_fn=skirt_top, min_top=25.0, back=3.2, detail="far")
    for (hx, hy, top) in ((-150.0, -112.0, 68.0), (-212.0, 8.0, 74.0)):
        peak(m, hx, hy, 9.0, top - 30.0, rng, z0=30.0, kind="horn", root=-40.0, face=(-hx, -30.0 - hy),
             top_m="Grass_Dark")
    # atras do terraco (y>128): faixas subindo, face para o sul, com a frente atras do fim do terraco (y=128,
    # onde comeca a colisao); a 2a e a 3a faixa ja sao o plano medio (Cliff_Rock_Mid)
    for k, (y, top) in enumerate(((136, 50), (151, 72), (171, 98))):
        pts = [(-78, y), (-30, y + 3), (20, y - 2), (70, y + 2), (120, y), (L.EAST_X + 25, y - 4)]
        mm, mm2 = (("Cliff_Rock", "Cliff_Rock_Dark") if k == 0 else ("Cliff_Rock_Mid", "Cliff_Rock_Mid_Dark"))
        # a 2a e a 3a faixa formam o horizonte do meio visto do spawn: massas largas (paredoes/blocos) agrupadas,
        # crista com amplitude maior (grupos e vaos), nada de fileira de tubos
        rmn, rmx, amp = ((6.5, 11.0, 3.4), (9.0, 15.0, 5.5), (10.0, 17.0, 7.5))[k]
        cliff_band(m, pts, (28.0, 43.0, 43.0)[k], top, rng, depth=4, rmin=rmn, rmax=rmx, step=8.5, face_side=-1,
                   top_fn=crest(top, amp, 0.02, 11.0 + 5.3 * k), m=mm, m2=mm2,
                   band_m=("Cliff_Rock_Top" if k == 0 else None), detail=(None if k == 0 else "far"),
                   talus=(dict(z=L.TERR, ok=lambda x, y: y > L.TERR_BACK_Y - 3 and not (-134 < x < -66), every=11.0)
                          if k == 0 else None))
        pts = [(L.WEST_X - 63, y + 9), (L.WEST_X - 40, y + 7), (L.WEST_X - 6, y)]
        cliff_band(m, pts, (28.0, 43.0, 43.0)[k], top + 6, rng, depth=4, rmin=6.5, rmax=11, step=8.5, face_side=-1,
                   top_fn=crest(top + 6, 3.0, 0.03, 31.0 + 2.1 * k), m=mm, m2=mm2,
                   band_m=("Cliff_Rock_Top" if k == 0 else None), detail=(None if k == 0 else "far"))
    col_box2("BackMountain", (-90, L.TERR_BACK_Y, 0), (L.EAST_X + 30, L.TERR_BACK_Y + 30, 90))
    col_box2("BackMountain", (L.WEST_X - 40, L.TERR_BACK_Y, 0), (-116, L.TERR_BACK_Y + 30, 90))
    # macicos no planalto de tras: plano intermediario entre as faixas e a cordilheira (silhueta em camadas),
    # larguras e alturas contrastantes (mesa larga e baixa / chifre estreito / paredao), fora da frente do busto;
    # nenhum flanco entra no corredor de Konoha
    def konoha_corridor(x, y, a):
        mg = 0.7 * a
        return -134 - mg < x < -66 + mg and 112 - mg < y < 305 + mg
    for (x, y, top, r, kind) in ((-30, 206, 104, 22, "mesa"), (58, 200, 128, 11, "horn"),
                                 (160, 150, 100, 20, "wall"), (-172, 184, 126, 14, "horn")):
        peak(m, x, y, r, top - L.TERR, rng, z0=L.TERR, kind=kind, root=0.0, face=(0.0 - x, -40.0 - y),
             avoid=konoha_corridor, m="Cliff_Rock_Mid", m2="Cliff_Rock_Mid_Dark")
    # lado leste: rampa de penhascos
    # (massas largas: vista do alto a rampa leste nao vira feixe de tubos)
    for k, (x, top) in enumerate(((L.EAST_X + 10, 52), (L.EAST_X + 26, 76))):
        cliff_band(m, [(x, -70), (x + 4, 40), (x, 130)], L.FLOOR - 2 + k * 20, top, rng, depth=4, rmin=8.0, rmax=13.0,
                   step=8.5, face_side=1, top_fn=crest(top, 3.6, 0.03, 21.0 + 4.4 * k), detail=("far" if k else None))
    for poly, z0, z1 in (([(L.EAST_X + 8, -80), (L.EAST_X + 100, -80), (L.EAST_X + 100, 200), (L.EAST_X + 12, 200),
                          (L.EAST_X + 16, 60)], -40, 40),
                         # (frente dos planaltos atras da 1a faixa: sem paredao liso exposto atras dos portais)
                         ([(-78, 138), (L.EAST_X + 40, 138), (L.EAST_X + 40, 260), (-72, 260)], 0, 44),
                         # (borda leste recuada para tras da parede oeste do canion de Konoha: quem aparece no
                         #  Passo da Folha sao as massas do canion, nao a face lisa do planalto)
                         ([(L.WEST_X - 60, 137), (-128, 137), (-128, 260), (L.WEST_X - 60, 260)], 0, 44)):
        m.prism(poly, z0, z1 - 0.8, "Cliff_Rock_Dark")
        m.prism(poly, z1 - 0.8, z1, "Grass_Dark")
    # face sul do planalto leste (antes um paredao liso de caixa, bem visivel do alto): massas quebradas
    cliff_band(m, [(L.EAST_X + 104, -83), (L.EAST_X + 56, -86), (L.EAST_X + 8, -83)], -46, 40, rng, depth=3,
               rmin=7, rmax=11, step=9, face_side=1, top_fn=crest(41, 2.6, 0.04, 57.0), detail="far")
    # laterais do terraco: face das massas alinhada a colisao (nada de rocha invadindo o ledge/terraco)
    cliff_band(m, [(L.WEST_X - 3.5, 64), (L.WEST_X - 3.5, 124)], L.MID - 2, 52, rng, depth=3, rmin=5, rmax=8,
               step=6.5, face_side=-1, front=1.5)
    col_box2("WestCliff", (L.WEST_X - 12, 62, 0), (L.WEST_X, 124, 70))
    cliff_band(m, [(LEDGE_X1 + 1.5, 64), (LEDGE_X1 + 1.5, 130)], L.MID - 2, 52, rng, depth=3, rmin=5, rmax=8,
               step=6.5, face_side=1, front=1.5)
    # encosta leste do ledge/terraco ate o fundo (fecha o vao atras do One Punch Man)
    col_box2("EastCliff", (LEDGE_X1, 62, 0), (L.EAST_X + 12, 130, 70))
    ob = m.finish()
    _decimate_far(ob)

    # silhueta distante: cordilheiras em 3 planos com hierarquia (fm_terrain_ridges) + vale distante sob a nevoa
    fm_terrain_ridges.build(C)
    fm_terrain_ridges.build_far_valley(C)
