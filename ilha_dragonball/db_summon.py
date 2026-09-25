# db_summon - ZONA SUMMON da Ilha 2 (Dragon Ball). Prefixo DB_Sum_, colecao 06_SUMMON, VFX_DBSUM_* em 12_VFX_HELPERS.
# A MAQUINA E A MESMA DA ILHA 1 (familia aprovada): torre de pedra com nicho do portal azul, cornijas de ouro, esfera
# armilar dourada com aneis moveis e a estrela facetada. O codigo da torre e o da Ilha 1 (ilha_naruto/il_summon.py),
# carregado com os valores da planta DESTA ilha (il_layout.SUMMON_TOWER/FACE/T1/SUMMON_C/R trocados so durante o
# import e restaurados logo depois); so as funcoes da TORRE sao chamadas (pedra, detalhes, pedestais, mastros,
# esfera, constelacao, colisao da torre). A praca de mosaico/balaustrada da Ilha 1 NAO entra.
# Trocas na maquina (identidade DB, mesma familia): os cachos de cristal azul (liam como MINERIO numa ilha de mineracao)
# viraram CELULAS DE ENERGIA Capsule (nucleo ciano + costelas brancas + aneis de ouro) nos mesmos pedestais, e as
# lanternas de pagode dos 4 pedestais de canto viraram FAROIS Capsule; os postes do pe da escada da torre assentam
# no L2 desta praca (troca temporaria de il_summon.ZL1/K.corner_lantern durante a chamada, restaurada depois).
# Area adaptada a DRAGON BALL (missao secao 20/21): plato redondo tecnologico (disco SUMMON_C r 25, topo SUM 30,2)
# sobre base de arenito (alvenaria + rocha) ate o GROUND 24,2; aneis escalonados concentricos na frente da torre
# (L1 +0,4 e L2 +0,8, com colisao propria), frisos Capsule branco/azul, linhas de energia laranja (DB_Energy_Glow),
# balaustrada branca/azul (lanterna a cada 5 postes) nas linhas da TerraceGuard (aberta na escada), 2 pilones Capsule,
# 2 postes de lanterna emoldurando a chegada, bastiao de arenito sob a traseira da torre (que passa da borda do disco),
# rochedos do pe no estilo de rocha da ilha (5 grupos, fora das PLATEAU_ROCKS/MESAS) e a escada visual do db_col.
# Orcamento (studio): as pecas repetidas vao em POUCOS objetos por material (1 MeshPart por objeto x material).
import math, random, sys, importlib
import bmesh
from mathutils import Vector, Euler
import bpy
import db_lib as DL
from db_lib import MB, col_box, mk, yaw_to, light, dome, octo_col, Frame
import db_layout as L
import db_col
import fm_lib
import fm_parts as FP
import fm_portal_kit as PK

COL = "06_SUMMON"
CX, CY = L.SUMMON_C
R = L.SUMMON_R
Z = L.SUM
G = L.GROUND

# ------------------------------------------------------------------ referencial da torre (o mesmo do il_summon)
TX, TY = L.SUMMON_TOWER
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2
F = Frame(TX, TY, Z, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))
ZZ = Vector((0.0, 0.0, 1.0))
# medidas da torre da Ilha 1 (il_summon) usadas antes do import (rotas/cameras); build() confere que batem
ST_FOOT, LAND_Z, PV, PLAYER_V = 13.6, 4.0, -1.4, 3.4
LAND_V = (-1.4, 5.6)
PLINTH_R = (20.7, -12.4, 8.7)       # pegada do soco com rodape de ouro: meia largura u, v tras, v frente
STAIR_R = (5.15, 13.72)             # escada frontal da torre (com banzos): meia largura u, v do pe

# ------------------------------------------------------------------ praca (niveis e aneis)
LV0 = Z + 0.05                      # piso L0 (5 cm acima da colisao do db_col: cobre o tampo do terreno sem z-fight)
LV1 = Z + 0.40                      # anel L1 (colisao propria)
LV2 = Z + 0.80                      # anel L2 = topo do soco da torre (colisao propria)
PC_V = 16.0                         # centro dos aneis escalonados (no eixo da torre, logo a frente da escada)
R1 = 15.2                           # borda do L1
R2 = 10.8                           # borda do L2
R_TILE0 = 22.2                      # pavimento do L0 ate aqui (depois: energia, azul, aro branco)
RAIL_R = 24.9                       # balaustrada (linha da guarda invisivel do db_col, r 24,5..25,5)
PYLON_UV = (17.5, 12.0)             # pilones (+-u, v)
LAMP_TH = (32.0,)                   # postes de lanterna (+-graus a partir da frente, no espelho do L1)
FREE_V = (ST_FOOT, ST_FOOT + 14.0)  # espaco livre 14 x 14 na frente da escada da torre


def P(u, v, z=0.0):
    return F.p(u, v, z)


def to_local(x, y):
    d = Vector((x - TX, y - TY, 0.0))
    return d.dot(XU), d.dot(YV)


PCW = P(0.0, PC_V, 0.0)
PCX, PCY = PCW.x, PCW.y


def in_rect(u, v, rect, pad=0.0):
    u0, u1, v0, v1 = rect
    return u0 - pad < u < u1 + pad and v0 - pad < v < v1 + pad


RECTS = [(-PLINTH_R[0], PLINTH_R[0], -99.0, PLINTH_R[2]), (-STAIR_R[0], STAIR_R[0], -99.0, STAIR_R[1])]


def in_tower(x, y, pad=0.0):
    u, v = to_local(x, y)
    return any(in_rect(u, v, r, pad) for r in RECTS)


def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


def _circ_pt(r, a_deg, cx=CX, cy=CY):
    return (cx + r * math.cos(math.radians(a_deg)), cy + r * math.sin(math.radians(a_deg)))


# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    "CAM_DBSum_Front": ((-74.0, -10.0, Z + 16.0), (TX - 2.0, TY, Z + 22.0), 22),
    "CAM_DBSum_Back": ((-205.0, 26.0, Z + 34.0), (CX, CY, Z + 10.0), 24),
    "CAM_DBSum_North": ((-122.0, 62.0, Z + 20.0), (CX - 4.0, CY, Z + 12.0), 22),
    "CAM_DBSum_South": ((-112.0, -72.0, Z + 20.0), (CX - 4.0, CY, Z + 12.0), 22),
    "CAM_DBSum_Top": ((CX + 0.01, CY - 8.0, Z + 120.0), (CX, CY, Z), 26),
    "CAM_DBSum_Eye": ((-106.0, -3.5, LV0 + 5.2), (TX, TY, Z + 16.0), 22),
    "CAM_DBSum_Landing": _cam(0.0, PLAYER_V + 10.5, LAND_Z + 5.5, 0.0, PV, LAND_Z + 5.0, 18),
    "CAM_DBSum_Base": ((-168.0, -46.0, G + 5.2), (-140.0, -8.0, Z + 3.0), 20),
    # pe do plato na altura do jogador (rochedos do pe junto dos da planta) e postes do pe da escada da torre no L2
    "CAM_DBSum_FootNW": ((-158.0, 50.0, G + 5.2), (-146.0, 22.0, G + 3.5), 22),
    "CAM_DBSum_FootS": ((-146.0, -50.0, G + 5.2), (-134.0, -24.0, G + 3.0), 22),
    "CAM_DBSum_StairFoot": _cam(9.0, ST_FOOT + 8.0, 0.8 + 5.2, 0.0, ST_FOOT - 1.0, 2.2, 22),
}

# ------------------------------------------------------------------ rotas e sondas proprias (db_qa)
_STAIR_TOP = (L.SUMMON_STAIR[0] - L.SUMMON_STAIR_N * L.TREAD - 1.5, L.SUMMON_STAIR[1])
EXTRA_ROUTES = {
    # topo da escada do plato -> aneis -> escada da torre -> patamar diante do portal (SUMMON_PlayerPosition)
    "ESCADA->PORTAL": ([_STAIR_TOP, tuple(P(0.0, 27.0).xy), tuple(P(0.0, ST_FOOT + 2.0).xy),
                        tuple(P(0.0, ST_FOOT - 0.3).xy), tuple(P(0.0, LAND_V[1] - 0.6).xy),
                        tuple(P(0.0, PLAYER_V).xy), tuple(P(0.0, PV + 1.9).xy)], Z),
    # volta pelo L0 (fora dos aneis e dos postes): topo da escada -> sul -> encosta na lateral sul da torre
    "ANEL_SUL": ([_STAIR_TOP] + [_circ_pt(22.0, a) for a in (-20.0, -45.0, -70.0, -95.0, -115.0)], Z),
    # topo da escada -> norte (passa entre os postes de lanterna e a balaustrada) -> canto da torre
    "ANEL_NORTE": ([_STAIR_TOP] + [_circ_pt(22.2, a) for a in (22.0, 40.0, 58.0, 70.0)], Z),
}
_NB = _circ_pt(22.6, 50.0)
_SB = _circ_pt(22.6, 300.0)
_WS = P(18.6, -1.2, 0.0)
EXTRA_PROBES = [
    ("SUM_borda_N", _NB[0], _NB[1], Z, math.cos(math.radians(50.0)), math.sin(math.radians(50.0))),
    ("SUM_borda_S", _SB[0], _SB[1], Z, math.cos(math.radians(300.0)), math.sin(math.radians(300.0))),
    ("SUM_asa_S_tras", _WS.x, _WS.y, Z + 0.8, -YV.x, -YV.y),
]


# ------------------------------------------------------------------ geometria
def arc_piece(cx, cy, r0, r1, a0, a1, step=4.0):
    """setor de anel (graus) como poligono ccw"""
    n = max(1, int(math.ceil(abs(a1 - a0) / step)))
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
              cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
              cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return outer + inner


def top_prism(mb, pts, z0, z1, m, bevel=0.0):
    """prisma sem a face de baixo (piso/aro assentado: o fundo nunca aparece)"""
    pts = DL.ccw(pts)
    vb = [mb.bm.verts.new((p[0], p[1], z0)) for p in pts]
    vt = [mb.bm.verts.new((p[0], p[1], z1)) for p in pts]
    n = len(pts)
    mb.bm.faces.new(vt)
    for i in range(n):
        j = (i + 1) % n
        mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m, None, bevel, 1, angle=0.6)


def _overlaps_tower(poly, pad=0.0):
    loc = [to_local(x, y) for x, y in poly]
    us = [p[0] for p in loc]
    vs = [p[1] for p in loc]
    for u0, u1, v0, v1 in RECTS:
        if not (max(us) <= u0 - pad or min(us) >= u1 + pad or max(vs) <= v0 - pad or min(vs) >= v1 + pad):
            return True
    return False


def _clip_out_rect(poly, rect):
    """partes de 'poly' (mundo) FORA do retangulo local (u0, u1, v0, v1) do referencial da torre"""
    loc = [to_local(x, y) for x, y in poly]
    u0, u1, v0, v1 = rect
    us = [p[0] for p in loc]
    vs = [p[1] for p in loc]
    if max(us) <= u0 or min(us) >= u1 or max(vs) <= v0 or min(vs) >= v1:
        return [poly]
    out = []
    for nx, ny, c, mid in ((1.0, 0.0, u0, False), (-1.0, 0.0, -u1, False), (0.0, 1.0, v0, True),
                           (0.0, -1.0, -v1, True)):
        p = DL.clip(loc, nx, ny, c)                 # nx*u + ny*v <= c
        if mid and p:
            p = DL.clip(p, -1.0, 0.0, -u0)          # u >= u0
            p = DL.clip(p, 1.0, 0.0, u1) if p else p
        if len(p) >= 3 and abs(DL.area(p)) > 0.08:
            out.append([tuple(P(a, b).xy) for a, b in p])
    return out


def clip_tower(poly):
    pieces = [poly]
    for rc in RECTS:
        nxt = []
        for p in pieces:
            nxt += _clip_out_rect(p, rc)
        pieces = nxt
    return pieces


def ring_strip(mb, cx, cy, r0, r1, z0, z1, m, angs, closed):
    """faixa continua de anel (tampo + paredes interna/externa; sem fundo) nos angulos dados (graus)"""
    bm = mb.bm
    ti, to, bi, bo = [], [], [], []
    for a in angs:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        ti.append(bm.verts.new((cx + c * r0, cy + s * r0, z1)))
        to.append(bm.verts.new((cx + c * r1, cy + s * r1, z1)))
        bi.append(bm.verts.new((cx + c * r0, cy + s * r0, z0)))
        bo.append(bm.verts.new((cx + c * r1, cy + s * r1, z0)))
    k = len(angs)
    for i in range(k if closed else k - 1):
        j = (i + 1) % k
        bm.faces.new((ti[i], to[i], to[j], ti[j]))
        bm.faces.new((ti[j], bi[j], bi[i], ti[i]))
        bm.faces.new((to[i], bo[i], bo[j], to[j]))
    if not closed:
        bm.faces.new((ti[0], bi[0], bo[0], to[0]))
        bm.faces.new((to[-1], bo[-1], bi[-1], ti[-1]))
    mb._post(ti + to + bi + bo, m, None, 0, 1)


def band(mb, cx, cy, r0, r1, z0, z1, m, step=6.0, skip=None, clip=False):
    """anel inteiro: trechos livres viram faixas continuas; setores que tocam a pegada da torre sao recortados"""
    n = max(3, int(math.ceil(360.0 / step)))
    kinds = []
    for i in range(n):
        aa, ab = 360.0 * i / n, 360.0 * (i + 1) / n
        am = math.radians((aa + ab) / 2)
        rm = (r0 + r1) / 2
        x, y = cx + rm * math.cos(am), cy + rm * math.sin(am)
        if skip and skip(x, y):
            kinds.append("s")
            continue
        poly = arc_piece(cx, cy, r0, r1, aa, ab, step)
        kinds.append("c" if clip and _overlaps_tower(poly) else "f")
    if all(k == "f" for k in kinds):
        ring_strip(mb, cx, cy, r0, r1, z0, z1, m, [360.0 * i / n for i in range(n)], True)
        return
    i0 = next(i for i in range(n) if kinds[i] != "f")
    run = []
    for k in range(1, n + 1):
        i = (i0 + k) % n
        if kinds[i] == "f":
            run.append(i)
            continue
        if run:
            angs = [360.0 * j / n for j in run] + [360.0 * (run[-1] + 1) / n]
            angs = [a + (360.0 if a < angs[0] - 1e-6 else 0.0) for a in angs]
            ring_strip(mb, cx, cy, r0, r1, z0, z1, m, angs, False)
            run = []
        if kinds[i] == "c":
            aa, ab = 360.0 * i / n, 360.0 * (i + 1) / n
            for p in clip_tower(arc_piece(cx, cy, r0, r1, aa, ab, step)):
                top_prism(mb, p, z0, z1, m)
    if run:
        angs = [360.0 * j / n for j in run] + [360.0 * (run[-1] + 1) / n]
        angs = [a + (360.0 if a < angs[0] - 1e-6 else 0.0) for a in angs]
        ring_strip(mb, cx, cy, r0, r1, z0, z1, m, angs, False)


def tile_rings(mb, cx, cy, r0, r1, ztop, h, m, ring_w=3.0, tile_len=3.6, gap=0.22, skip=None, bevel=0.0):
    """pavimento em aneis de pedras em arco (centro cx, cy), recortado na pegada da torre"""
    r = r0
    k = 0
    while r < r1 - 0.3:
        rr = min(r + ring_w, r1)
        if r1 - rr < 1.0:
            rr = r1
        if r < 0.3:
            pts = [(cx + (rr - gap / 2) * math.cos(t * math.tau / 10), cy + (rr - gap / 2) * math.sin(t * math.tau / 10))
                   for t in range(10)]
            if not (skip and skip(cx, cy)):
                for p in clip_tower(pts):
                    top_prism(mb, p, ztop - h, ztop, m, bevel)
            r, k = rr, k + 1
            continue
        rm = (r + rr) / 2
        n = max(6, int(round(math.tau * rm / tile_len)))
        off = (180.0 / n) if k % 2 else 0.0
        g = math.degrees((gap / 2) / rm)
        for i in range(n):
            aa = off + 360.0 * i / n + g
            ab = off + 360.0 * (i + 1) / n - g
            poly = arc_piece(cx, cy, r + gap / 2, rr - gap / 2, aa, ab, 7.0)
            mx = sum(p[0] for p in poly) / len(poly)
            my = sum(p[1] for p in poly) / len(poly)
            if skip and skip(mx, my):
                continue
            for p in clip_tower(poly):
                top_prism(mb, p, ztop - h, ztop, m, bevel)
        r, k = rr, k + 1


def merge_by_material(src, route):
    """junta as faces de 'src' nos objetos de destino por material (route = {material: objeto, '*': objeto});
    menos MeshParts no export (1 por objeto x material). Os objetos do MB ja estao em coordenadas de mundo."""
    mats = [m.name for m in src.data.materials]
    targets = {}
    for i, mn in enumerate(mats):
        targets.setdefault(route.get(mn, route["*"]), []).append(i)
    for dst, idxs in targets.items():
        me = src.data.copy()
        bm = bmesh.new()
        bm.from_mesh(me)
        dead = [f for f in bm.faces if f.material_index not in idxs]
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        names = [m.name for m in dst.data.materials]
        remap = {}
        for i in idxs:
            if mats[i] not in names:
                dst.data.materials.append(src.data.materials[i])
                names.append(mats[i])
            remap[i] = names.index(mats[i])
        for f in bm.faces:
            f.material_index = remap[f.material_index]
        bm.to_mesh(me)
        bm.free()
        bm2 = bmesh.new()
        bm2.from_mesh(dst.data)
        bm2.from_mesh(me)
        bm2.to_mesh(dst.data)
        bm2.free()
        bpy.data.meshes.remove(me)
    me = src.data
    bpy.data.objects.remove(src, do_unlink=True)
    bpy.data.meshes.remove(me)


# ------------------------------------------------------------------ torre (codigo da Ilha 1)
_TOWER = None


def tower_mod():
    """importa il_summon com a planta desta ilha (valores do il_layout trocados so durante o import)"""
    global _TOWER
    if _TOWER is not None:
        return _TOWER
    import il_layout as NL
    want = {"SUMMON_TOWER": tuple(L.SUMMON_TOWER), "SUMMON_FACE_DEG": L.SUMMON_FACE_DEG, "T1": L.SUM,
            "SUMMON_C": tuple(L.SUMMON_C), "SUMMON_R": L.SUMMON_R}
    saved = {k: getattr(NL, k) for k in want}
    for k, v in want.items():
        setattr(NL, k, v)
    try:
        if "il_summon" in sys.modules:
            T = importlib.reload(sys.modules["il_summon"])
        else:
            T = importlib.import_module("il_summon")
    finally:
        for k, v in saved.items():
            setattr(NL, k, v)
    assert abs(T.Z0 - Z) < 1e-6 and abs(T.TX - TX) < 1e-6 and abs(T.TY - TY) < 1e-6 and abs(T.YAW - YAW) < 1e-9
    for a, b in ((T.ST_FOOT, ST_FOOT), (T.LAND_Z, LAND_Z), (T.PV, PV), (T.PLAYER_V, PLAYER_V)):
        assert abs(a - b) < 1e-6, (a, b)
    _TOWER = T
    return T


def energy_cells(T, dress, gold, glow):
    """no lugar dos cachos de cristal (liam como minerio): celula de energia Capsule em cada pedestal interno"""
    import il_summon_kit as K
    for s in (-1, 1):
        u, v = s * T.IN_PED[0], T.IN_PED[1]
        b = P(u, v, T.POD_TOP + T.IN_PED[3] + 0.5)
        dress.cyl(1.35, 0.6, b + ZZ * 0.3, (0, 0, 0), "Plaster_DB_White", 12, bevel=0.0)
        dress.cyl(1.45, 0.35, b + ZZ * 0.75, (0, 0, 0), "Roof_DB_Blue", 12, bevel=0.0)
        glow.cyl(0.95, 4.4, b + ZZ * 3.1, (0, 0, 0), "DB_Cyan_Glow", 10, bevel=0.0)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            d = XU * math.cos(a) + YV * math.sin(a)
            dress.box((0.45, 0.45, 4.6), b + d * 1.0 + ZZ * 3.1, (0, 0, YAW + a), "Plaster_DB_White", 0.0)
        for zz in (2.0, 4.2):
            gold.cyl(1.25, 0.32, b + ZZ * zz, (0, 0, 0), "Metal_Gold", 12, bevel=0.0)
        dress.cyl(1.35, 0.5, b + ZZ * 5.55, (0, 0, 0), "Roof_DB_Blue", 12, bevel=0.0)
        dome(dress, (b.x, b.y), 1.3, b.z + 5.8, "Plaster_DB_White", n=12, rings=3, squash=0.7, open_bottom=False)
        K.spike(gold, b + ZZ * 6.65, b + ZZ * 8.0, 0.3, "Metal_Gold", 4)
        col_box("DB_SumCell", (2.9, 2.9, 7.4), b + ZZ * 3.7, (0, 0, YAW))


def capsule_beacon(dress, glow, gold, Fr, u, v, z):
    """farol Capsule no topo do pedestal de canto (no lugar da lanterna de pagode da Ilha 1): tambor branco, anel de
    ouro, luz quente entre costelas brancas, tampa azul e cupula branca com ponta de ouro (~4,4 de altura, dentro da
    colisao pedestal + lanterna do il_summon). Devolve o centro da luz (para as luzes L_DBSum_Lantern_*)."""
    import il_summon_kit as K
    b = Vector(Fr.p(u, v, z))
    dress.cyl(1.5, 0.35, b + ZZ * 0.175, (0, 0, 0), "Plaster_DB_Navy", 16, bevel=0.0)
    dress.cyl(1.15, 1.0, b + ZZ * 0.85, (0, 0, 0), "Plaster_DB_White", 16, bevel=0.0)
    gold.cyl(1.28, 0.28, b + ZZ * 1.49, (0, 0, 0), "Metal_Gold", 16, bevel=0.0)
    zc = 1.63 + 0.7
    glow.cyl(0.8, 1.4, b + ZZ * zc, (0, 0, 0), "Lantern_Glow", 10, bevel=0.0)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        d = XU * math.cos(a) + YV * math.sin(a)
        dress.box((0.36, 0.36, 1.5), b + d * 0.92 + ZZ * zc, (0, 0, YAW + a), "Plaster_DB_White", 0.0)
    dress.cyl(1.22, 0.3, b + ZZ * 3.18, (0, 0, 0), "Roof_DB_Blue", 16, bevel=0.0)
    dome(dress, (b.x, b.y), 1.05, b.z + 3.33, "Plaster_DB_White", n=12, rings=3, squash=0.6, open_bottom=False)
    K.spike(gold, b + ZZ * 3.9, b + ZZ * 4.5, 0.22, "Metal_Gold", 4)
    return b + ZZ * zc


def build_tower(dress, glow_db):
    T = tower_mod()
    before = {o.name for o in bpy.data.objects}
    stone = MB("DB_Sum_Tower_Stone", COL, random.Random(620), detail="near")
    gold = MB("DB_Sum_Tower_Gold", COL, random.Random(622), detail="near")
    glow = MB("DB_Sum_Tower_Glow", COL, random.Random(623), detail="hero")
    T.tower_stone(stone, gold, glow)
    cr = T.tower_details(stone, gold, glow)
    cr.bm.free()                                      # cristais pequenos da boca do nicho: fora (minerio)
    # 2 trocas SO durante esta chamada (restauradas logo depois; nenhum arquivo da Ilha 1 e editado):
    # - os postes do pe da escada da torre assentam no L2 desta praca (+0,8), nao no mosaico da Ilha 1 (+0,3):
    #   ZL1 so e lido ali dentro de masts_and_lanterns (zp = ZL1 - 0,05)
    # - as lanternas japonesas (pagode) dos 4 pedestais de canto viram farois Capsule (identidade DB)
    saved = (T.ZL1, T.K.corner_lantern)
    T.ZL1 = (LV2 - Z) + 0.05
    T.K.corner_lantern = lambda st, gl, go, Fr, u, v, z, s=1.0, sh=None: capsule_beacon(dress, glow_db, go, Fr, u, v, z)
    try:
        lamp_c = T.masts_and_lanterns(stone, gold, glow)
    finally:
        T.ZL1, T.K.corner_lantern = saved
    energy_cells(T, dress, gold, glow_db)
    c = T.sphere(gold, glow)
    T.constellation(c)
    stone.finish()
    ob_gold = gold.finish()
    ob_glow = glow.finish()
    T.tower_collision()
    # renomeia o que o codigo da Ilha 1 criou: SUM_* -> DB_Sum_*, VFX_SUM_* -> VFX_DBSUM_*; colecao 05 -> 06
    dst = fm_lib.coll(COL)
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_DBSUM_" + n[len("VFX_SUM_"):]
        elif n == "SUM_Banners":
            ob.name = "DB_Sum_Tower_Banners"
        elif n.startswith("SUM_"):
            ob.name = "DB_Sum_" + n[len("SUM_"):]
        if ob.type == "MESH":
            ob.data.name = ob.name
        for cl in list(ob.users_collection):
            if cl.name == "05_SUMMON":
                cl.objects.unlink(ob)
                if ob.name not in dst.objects:
                    dst.objects.link(ob)
    c05 = bpy.data.collections.get("05_SUMMON")
    if c05 is not None and not c05.objects and not c05.children:
        bpy.data.collections.remove(c05)
    # armacao da esfera e constelacao entram na torre (ouro / brilho): 4 MeshParts a menos, mesma geometria
    for nm in ("DB_Sum_Sphere_Frame", "DB_Sum_Constellation"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            merge_by_material(ob, {"Metal_Gold": ob_gold, "*": ob_glow})
    # luzes (4 de dia): estrela (quente), portal (fria), 2 lanternas de canto da frente
    light("L_DBSum_Star", "POINT", c, 9000, (1.0, 0.74, 0.34), 3.0)
    light("L_DBSum_Portal", "POINT", P(0.0, PV + 3.0, 9.0), 1800, (0.36, 0.52, 1.0), 1.2)
    for n, p in zip(("L_DBSum_Lantern_L", "L_DBSum_Lantern_R"), lamp_c[:2]):
        light(n, "POINT", p, 320, (1.0, 0.62, 0.28), 0.4)
    return T, c


# ------------------------------------------------------------------ plato: piso escalonado
def _skip0(x, y):
    return math.hypot(x - PCX, y - PCY) < R1 - 0.4


def _skip1(x, y):
    return math.hypot(x - PCX, y - PCY) < R2 - 0.4


def _skip_tw(x, y):
    return in_tower(x, y, 0.3)


def floor(plat, glow):
    import il_summon_kit as K
    # --- L0 (disco do plato, centro SUMMON_C): rejunte + pedras + energia + azul (o aro branco e da lateral)
    plat.cyl(R_TILE0 + 0.1, 0.36, (CX, CY, LV0 - 0.2), (0, 0, 0), "Stone_DB_Block", 40, bevel=0.0)
    tile_rings(plat, CX, CY, 0.0, R_TILE0, LV0, 0.3, "Stone_Paving_DB", skip=_skip0)
    band(glow, CX, CY, R_TILE0 + 0.08, R_TILE0 + 0.45, LV0 - 0.3, LV0 + 0.03, "DB_Energy_Glow", 6.0, skip=_skip_tw)
    band(plat, CX, CY, R_TILE0 + 0.45, 23.3, LV0 - 0.3, LV0 + 0.02, "Roof_DB_Blue", 6.0, skip=_skip_tw)
    # --- L1 (+0,4) e L2 (+0,8): aneis escalonados na frente da torre (centro no eixo, a frente da escada)
    for rr, zt, zb, skip, tile_m, st in ((R1, LV1, LV0 - 0.3, _skip1, "Stone_Paving_Warm", 7.5),
                                         (R2, LV2, LV1 - 0.3, None, "Stone_Paving_DB", 9.0)):
        plat.cyl(rr - 0.5, zt - 0.3 - zb, (PCX, PCY, (zb + zt - 0.3) / 2), (0, 0, 0), "Stone_DB_Block", 32, bevel=0.0)
        r_in = R2 if rr == R1 else 0.0
        tile_rings(plat, PCX, PCY, r_in, rr - 1.35, zt, 0.3, tile_m, ring_w=2.7, tile_len=3.3, skip=skip)
        band(glow, PCX, PCY, rr - 1.3, rr - 0.95, zt - 0.3, zt + 0.03, "DB_Energy_Glow", st, clip=True)
        band(plat, PCX, PCY, rr - 0.95, rr - 0.55, zt - 0.3, zt, "Roof_DB_Blue", st, clip=True)
        band(plat, PCX, PCY, rr - 0.55, rr, zb, zt, "Plaster_DB_White", st, clip=True)
    # L2: circulo de invocacao - aro de energia + raios (salientes 0,12: Neon longe da pedra) + estrela de ouro
    band(glow, PCX, PCY, 2.5, 2.9, LV2 - 0.3, LV2 + 0.12, "DB_Energy_Glow", 12.0, clip=True)
    for k in range(8):
        a = math.radians(22.5 + 45.0 * k) + YAW
        d = Vector((math.cos(a), math.sin(a), 0.0))
        p0 = PCW + d * 3.3
        p1 = PCW + d * (R2 - 1.45)
        mid = (p0 + p1) / 2
        if in_tower(mid.x, mid.y, 0.4) or in_tower(p1.x, p1.y, 0.3):
            continue
        glow.beam(Vector((p0.x, p0.y, LV2 - 0.12)), Vector((p1.x, p1.y, LV2 - 0.12)), 0.4, 0.48, "DB_Energy_Glow", 0.0)
    K.star(plat, (PCX, PCY, LV2 + 0.02), (1, 0, 0), (0, 1, 0), 5, 2.0, 0.85, 0.1, "Metal_Gold", rot=FACE + math.pi / 2,
           edge=0.3)
    # colisao propria SO dos aneis L1/L2 (o L0 e o piso SUM do db_col: 24-gono cheio). 16-gono exato (db_col.ngon_col)
    # com os vertices 0,05 dentro do espelho branco: a borda da colisao corre sempre sobre o topo do aro branco
    # (apotema 14,86 / 10,54 contra o aro 14,65-15,2 / 10,25-10,8), sem degrau invisivel para fora do visual
    db_col.ngon_col("DB_SumRing", PCX, PCY, 16, R1 - 0.05, Z - 1.0, LV1)
    db_col.ngon_col("DB_SumRing", PCX, PCY, 16, R2 - 0.05, Z - 1.0, LV2)


# ------------------------------------------------------------------ plato: lateral (arenito) e bastiao da torre
def _stair_ang(a_deg, r=R + 0.4):
    """ponto da borda (angulo a partir do centro do plato) sobre a escada visual (com os banzos)"""
    x, y = _circ_pt(r, a_deg)
    return x > L.SUMMON_STAIR[0] - L.SUMMON_STAIR_N * L.TREAD - 1.2 and abs(y - L.SUMMON_STAIR[1]) < \
        L.SUMMON_STAIR[2] / 2 + 1.3


def sides(plat):
    rng = random.Random(7201)
    # aro branco Capsule (topo da lateral, base da balaustrada) + faixa azul saliente; na escada o aro para em r 25
    n = 60
    runs, cur = [], None
    for i in range(n):
        a0, a1 = 360.0 * i / n, 360.0 * (i + 1) / n
        am = (a0 + a1) / 2
        hidden = in_tower(*_circ_pt(23.4, am), -0.3) and in_tower(*_circ_pt(25.3, am), -0.3)
        kind = "h" if hidden else ("s" if _stair_ang(am) else "f")
        if cur and cur[0] == kind:
            cur[2] = a1
        else:
            cur = [kind, a0, a1]
            runs.append(cur)
    for kind, a0, a1 in runs:
        if kind == "h":
            continue
        k = max(1, int(round((a1 - a0) / 6.0)))
        angs = [a0 + (a1 - a0) * j / k for j in range(k + 1)]
        if kind == "s":
            ring_strip(plat, CX, CY, 23.3, R, Z - 0.2, LV0 + 0.05, "Plaster_DB_White", angs, False)
        else:
            ring_strip(plat, CX, CY, 23.3, R + 0.4, Z - 1.3, LV0 + 0.05, "Plaster_DB_White", angs, False)
            ring_strip(plat, CX, CY, R + 0.35, R + 0.62, Z - 1.05, Z - 0.5, "Roof_DB_Blue", angs, False)
    # alvenaria de arenito em cordas (so onde nao ha escada nem bastiao da torre)
    nch = 36
    for i in range(nch):
        a0, a1 = 360.0 * i / nch, 360.0 * (i + 1) / nch
        am = (a0 + a1) / 2
        if _stair_ang(am, R + 0.6):
            continue
        pa, pb = _circ_pt(R - 0.05, a0), _circ_pt(R - 0.05, a1)
        mx, my = _circ_pt(R + 0.3, am)
        if in_tower(mx, my, 0.8):
            continue
        FP.masonry_wall(plat, (pa[0], pa[1], 0), (pb[0], pb[1], 0), G - 0.8, Z - 1.3, 1.0, rng, m="Stone_DB_Block",
                        m2="Cliff_Rock_DB", course=1.8, blk=(3.2, 5.0), quoins=(False, False), base_dark=True,
                        bevel=0.0, core_m="Stone_DB_Block")
    # pilastras de arenito laranja a cada 20 graus (ritmo na lateral lisa) com capitel azul-marinho sob o aro
    for i in range(18):
        a = 10.0 + 20.0 * i
        if _stair_ang(a, R + 0.6) or _stair_ang(a + 4.0, R + 0.6) or _stair_ang(a - 4.0, R + 0.6):
            continue
        x, y = _circ_pt(R + 0.35, a)
        if in_tower(x, y, 1.2):
            continue
        ra = math.radians(a)
        plat.box((0.9, 1.9, (Z - 1.3) - (G - 0.6)), (x, y, ((Z - 1.3) + (G - 0.6)) / 2), (0, 0, ra), "Cliff_Rock_DB",
                 0.0)
        cx2, cy2 = _circ_pt(R + 0.45, a)
        plat.box((1.1, 2.3, 0.4), (cx2, cy2, Z - 1.3 - 0.2), (0, 0, ra), "Plaster_DB_Navy", 0.0)
    # bastiao de arenito sob a parte da torre que passa da borda do disco (tras e lados)
    pu, pv0, pv1 = PLINTH_R[0] - 0.55, PLINTH_R[1] + 0.3, PLINTH_R[2]
    walls = [((-pu, pv1), (-pu, pv0)), ((-pu, pv0), (pu, pv0)), ((pu, pv0), (pu, -2.2))]
    for (ua, va), (ub, vb) in walls:
        a, b = P(ua, va, 0.0), P(ub, vb, 0.0)
        FP.masonry_wall(plat, (a.x, a.y, 0), (b.x, b.y, 0), G - 0.8, Z - 0.45, 1.1, rng, m="Stone_DB_Block",
                        m2="Cliff_Rock_DB", course=1.8, blk=(3.2, 5.0), quoins=(True, True), base_dark=True,
                        bevel=0.0, core_m="Stone_DB_Block")
    c = P(0.0, (PLINTH_R[1] + PLINTH_R[2]) / 2, 0.0)
    col_box("DB_SumBastion", (2 * PLINTH_R[0], PLINTH_R[2] - PLINTH_R[1], (Z - 0.6) - (G - 1.0)),
            (c.x, c.y, ((Z - 0.6) + (G - 1.0)) / 2), (0, 0, YAW))
    # bloqueio da asa sul do soco onde ela sai do disco (nao se anda por fora do plato); o visual e a grade
    # wing_barrier() na mesma linha (nada de parede invisivel sem aviso)
    b = P(18.6, WING_V, 0.0)
    col_box("DB_SumBastion", (4.6, 1.0, 5.0), (b.x, b.y, Z + 0.8 + 2.5), (0, 0, YAW))


WING_V = -3.0                        # linha do bloqueio da asa sul do soco (v local da torre)


def wing_barrier(mb):
    """trecho curto da balaustrada (mesma familia: postes brancos com base azul-marinho, tampa azul e remate de ouro,
    barra baixa branca, corrimao azul + ouro, balaustres) fechando a asa sul do soco entre o podio (u 16) e a borda
    do soco (u 20,7), sobre o soco (+0,8)"""
    zb = Z + 0.8
    rz = YAW
    posts = [P(16.8, WING_V, zb), P(19.95, WING_V, zb)]
    for p in posts:
        mb.box((1.4, 1.4, 0.4), p + Vector((0, 0, 0.2)), (0, 0, rz), "Plaster_DB_Navy", 0.0)
        mb.box((1.05, 1.05, 2.7), p + Vector((0, 0, 1.35 + 0.3)), (0, 0, rz), "Plaster_DB_White", 0.0)
        mb.box((1.35, 1.35, 0.35), p + Vector((0, 0, 3.17)), (0, 0, rz), "Roof_DB_Blue", 0.0)
        PK.octa(mb, p + Vector((0, 0, 3.35 + 0.35)), 0.34, 0.4, "Metal_Gold", rot=rz)
    a, b = posts
    u = (b - a).normalized()
    a2, b2 = a + u * 0.5, b - u * 0.5
    mb.beam(a2 + Vector((0, 0, 0.35)), b2 + Vector((0, 0, 0.35)), 0.9, 0.5, "Plaster_DB_White", 0.0)
    mb.beam(a2 + Vector((0, 0, 2.2)), b2 + Vector((0, 0, 2.2)), 0.75, 0.42, "Roof_DB_Blue", 0.0)
    mb.beam(a2 + Vector((0, 0, 2.52)), b2 + Vector((0, 0, 2.52)), 0.5, 0.26, "Metal_Gold", 0.0)
    q = (a2 + b2) / 2
    mb.box((0.45, 0.45, 1.5), q + Vector((0, 0, 1.3)), (0, 0, rz + math.pi / 4), "Plaster_DB_White", 0.0)


ROCK, DARK, TOPR, GRASS = "Cliff_Rock_DB", "Cliff_Rock_DB_Dark", "Cliff_Rock_DB_Top", "Grass_DB"


def _stack(mb, rng, c, a, b, n, ex, rot, z0, z1, m, taper=0.94, lid=None, band=None, lean=None, chamfer=0.6,
           rings=2, jitter=0.1, tilt=0.06):
    """corpo de rocha do kit da ilha (o mesmo recorte de db_terrain_rock._stack): superelipse facetada afunilada,
    faixa de topo clara, chanfro/tampa de grama; base enterrada (sem face de baixo)"""
    ca, sa = math.cos(rot), math.sin(rot)
    poly = [(x * ca - y * sa, x * sa + y * ca) for x, y in FP._rock_poly(a, b, n, rng, ex=ex, jit=0.1)]
    return FP.rock_column(mb, Vector((c[0], c[1], 0.0)), poly, z0, z1, rng, m, taper=taper, rings=rings,
                          jitter=jitter, tilt=tilt, lean=lean, top_m=lid, lip=1.0, chamfer=chamfer, rim=False,
                          band=band, tongues=None, bottom=False)


def rock_box(x, y, a, b, rot, z0, z1):
    """colisao de 1 caixa orientada pelo contorno do corpo (superelipse a x b girada de rot; 0,8 dos semi-eixos: os
    cantos da caixa ficam sobre a face facetada, sem sobra fora do visual)"""
    col_box("DB_SumRock", (2.0 * a * 0.8, 2.0 * b * 0.8, z1 - z0), (x, y, (z0 + z1) / 2), (0, 0, rot))


def rock_clear(x, y, r, pad=2.0):
    """o rochedo do summon nao encosta nos rochedos/mesas da planta (dono: terrain) e fica dentro da ilha"""
    for px, py, pr, _h in L.PLATEAU_ROCKS:
        if math.hypot(x - px, y - py) < pr + r + pad:
            return False
    for px, py, pr, _t, _k in L.MESAS:
        if math.hypot(x - px, y - py) < pr + r + pad:
            return False
    return all(L.point_in_poly(x + (r + 1.0) * math.cos(t), y + (r + 1.0) * math.sin(t), L.ISLAND_RIM)
               for t in [k * math.tau / 8 for k in range(8)])


# grupos do pe do plato (5, cada um com receita propria; nada de pilha repetida em escala diferente):
# (nome, 'c' = angulo/raio a partir do centro do plato | 't' = u/v da torre, a|u, r|v, raio, altura, receita, lado)
ROCK_GROUPS = [
    ("SW", "t", 20.0, -12.6, 5.8, 8.4, "tall", 1),      # quina SO do bastiao: primario de 2 corpos + coroa + secundario
    ("NW", "t", -21.0, -13.8, 4.0, 5.6, "lid", 1),      # quina NO: tronco afunilado com tampa de grama; secundario
    #                                                      para SO (longe da PLATEAU_ROCKS (-136, 28): folga 4,4)
    ("S", "c", 247.0, 27.2, 3.8, 3.2, "ledge", 1),      # sul: laje baixa e larga inclinada (estrato)
    ("NE", "c", 62.0, 26.4, 2.3, 4.8, "spire", 1),      # acento da chegada norte: agulha curta inclinada para fora
    ("SE", "c", 300.0, 26.6, 2.6, 2.4, "boulders", -1),  # acento da chegada sul: blocos rolados baixos
]


def rocks(plat):
    """pe do plato e do bastiao no estilo de rocha da ilha (db_terrain_rock): corpos afunilados com faixa de topo
    clara, estrato escuro recuado, coroa deslocada (fratura), secundario baixo e pedras soltas. Colisao por caixas."""
    rng = random.Random(7301)
    for name, kind, a, r, rad, h, recipe, sd in ROCK_GROUPS:
        if kind == "c":
            x, y = _circ_pt(r, a)
            out = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0))
        else:
            p = P(a, r, 0.0)
            x, y = p.x, p.y
            out = (XU * (1 if a > 0 else -1) - YV).normalized()
        if not rock_clear(x, y, rad):
            print("DB_SUM AVISO: grupo de rocha %s pulado (encosta em rocha da planta ou fora da ilha)" % name)
            continue
        side = Vector((-out.y, out.x, 0.0)) * sd
        rot = math.atan2(side.y, side.x) + rng.uniform(-0.3, 0.3)
        z0 = G - 0.8
        lean_out = (out.x * 0.5, out.y * 0.5)
        if recipe == "tall":
            a1, b1 = rad * 0.92, rad * 0.74
            zm, z1 = G + h * 0.34, G + h * 0.7
            # patamares afunilados 1,0 / 0,84 / 0,5 (nada de corpo de cima mais largo que o de baixo)
            _stack(plat, rng, (x, y), a1, b1, 7, 2.3, rot, z0, zm, ROCK, taper=0.94, chamfer=0.0, rings=1)
            _stack(plat, rng, (x, y), a1 * 0.86, b1 * 0.86, 7, 2.6, rot, zm - 0.2, zm + 1.1, DARK, taper=1.0,
                   rings=1, chamfer=0.0, jitter=0.04, tilt=0.0)                       # estrato escuro recuado
            _stack(plat, rng, (x, y), a1 * 0.84, b1 * 0.84, 7, 2.3, rot, zm + 0.9, z1, ROCK, taper=0.84,
                   band=(1.1, TOPR), chamfer=0.4, rings=1, lean=lean_out)
            c2 = Vector((x, y, 0.0)) - side * rad * 0.2 + out * rad * 0.1                # coroa deslocada (fratura)
            _stack(plat, rng, (c2.x, c2.y), a1 * 0.5, b1 * 0.56, 6, 2.1, rot + 0.4, z1 - 0.6, G + h, ROCK,
                   taper=0.72, band=(1.1, TOPR), chamfer=0.5, rings=1, tilt=0.14)
            octo_col("DB_SumRock", x, y, rad * 0.86, G - 1.0, z1)
            q = Vector((x, y, 0.0)) + side * rad * 1.15 + out * rad * 0.2               # secundario baixo e escuro
            _stack(plat, rng, (q.x, q.y), rad * 0.5, rad * 0.38, 6, 2.0, rot + 1.2, z0, G + h * 0.4, DARK,
                   taper=0.7, band=(0.8, TOPR), chamfer=0.4, rings=1, tilt=0.12)
            col_box("DB_SumRock", (rad * 0.85, rad * 0.65, h * 0.4 + 0.8), (q.x, q.y, (G - 1.0 + G + h * 0.4) / 2),
                    (0, 0, rot + 1.2))
            chips = [(side * rad * 1.9 + out * rad * 0.7, 1.3), (-side * rad * 0.9 + out * rad * 1.0, 1.0)]
        elif recipe == "lid":
            a1, b1 = rad * 0.95, rad * 0.8
            _stack(plat, rng, (x, y), a1, b1, 7, 2.4, rot, z0, G + h * 0.8, ROCK, taper=0.8, lid=GRASS,
                   rings=2, lean=lean_out)
            c2 = Vector((x, y, 0.0)) + side * rad * 0.55 - out * rad * 0.15              # ombro mais alto atras
            _stack(plat, rng, (c2.x, c2.y), rad * 0.5, rad * 0.46, 6, 2.1, rot + 0.7, G + h * 0.5, G + h, ROCK,
                   taper=0.7, band=(0.9, TOPR), chamfer=0.4, rings=1, tilt=0.12)
            rock_box(x, y, a1, b1, rot, G - 1.0, G + h * 0.8)
            chips = [(-side * rad * 1.1 + out * rad * 0.8, 1.1), (side * rad * 1.3 + out * rad * 0.5, 0.8)]
        elif recipe == "ledge":
            # laje baixa e larga + bloco fraturado mais alto numa ponta (silhueta em degrau, nao tampa chata)
            a1, b1 = rad * 1.15, rad * 0.62
            zl = G + h * 0.7
            _stack(plat, rng, (x, y), a1, b1, 7, 2.6, rot, z0, zl, ROCK, taper=0.85, band=(0.7, TOPR),
                   chamfer=0.35, rings=1, tilt=0.1)
            ca = Vector((math.cos(rot), math.sin(rot), 0.0))
            c2 = Vector((x, y, 0.0)) - ca * a1 * 0.45 + out * b1 * 0.1
            _stack(plat, rng, (c2.x, c2.y), a1 * 0.5, b1 * 0.8, 6, 2.2, rot + 0.25, zl - 0.8, G + h + 0.8, ROCK,
                   taper=0.72, band=(0.9, TOPR), chamfer=0.4, rings=1, tilt=0.14)
            q = Vector((x, y, 0.0)) + ca * a1 * 0.95 + out * rad * 0.45
            _stack(plat, rng, (q.x, q.y), rad * 0.55, rad * 0.4, 6, 2.4, rot + 0.3, z0, G + h * 0.45, DARK,
                   taper=0.8, band=(0.6, TOPR), chamfer=0.3, rings=1, tilt=0.1)
            col_box("DB_SumRock", (a1 * 1.8, b1 * 1.6, zl - (G - 1.0)), (x, y, (G - 1.0 + zl) / 2), (0, 0, rot))
            col_box("DB_SumRock", (a1 * 0.85, b1 * 1.3, G + h + 0.8 - (G - 1.0)),
                    (c2.x, c2.y, (G - 1.0 + G + h + 0.8) / 2), (0, 0, rot + 0.25))
            chips = [(-side * rad * 1.2 + out * rad * 0.7, 1.0)]
        elif recipe == "spire":
            _stack(plat, rng, (x, y), rad * 0.9, rad * 0.75, 6, 2.2, rot, z0, G + h, ROCK, taper=0.6,
                   band=(1.0, TOPR), chamfer=0.4, rings=2, lean=(out.x * 0.9, out.y * 0.9), tilt=0.1)
            q = Vector((x, y, 0.0)) + side * rad * 0.95 + out * rad * 0.3
            _stack(plat, rng, (q.x, q.y), rad * 0.55, rad * 0.45, 5, 2.0, rot + 0.9, z0, G + h * 0.36, DARK,
                   taper=0.75, band=(0.5, TOPR), chamfer=0.25, rings=1)
            # 2 caixas: pe cheio + metade de cima afunilada e deslocada para fora (acompanha a inclinacao)
            rock_box(x, y, rad * 0.9, rad * 0.75, rot, G - 1.0, G + h * 0.5)
            rock_box(x + out.x * 0.55, y + out.y * 0.55, rad * 0.9 * 0.72, rad * 0.75 * 0.72, rot, G + h * 0.5, G + h)
            chips = [(-side * rad * 1.2 + out * rad * 0.9, 0.8)]
        else:                                                                           # boulders
            for k, (ds, do, s_) in enumerate(((0.0, 0.0, 1.0), (1.05, 0.35, 0.62), (-0.95, 0.75, 0.42))):
                c = Vector((x, y, 0.0)) + side * rad * ds + out * rad * do
                plat.rock((c.x, c.y, G + 0.25 * s_ * h), (rad * 2.0 * s_, rad * 1.55 * s_, h * 1.1 * s_),
                          ROCK if k != 1 else DARK, 1, (0, 0, rot + k * 1.1), jitter=0.2)
            col_box("DB_SumRock", (rad * 1.7, rad * 1.3, h * 0.8 + 1.0), (x, y, (G - 1.0 + G + h * 0.8) / 2),
                    (0, 0, rot))
            chips = [(side * rad * 1.9 + out * rad * 0.9, 0.7)]
        # pedras soltas no pe (quebra pequena)
        for off, s_ in chips:
            e = Vector((x, y, 0.0)) + off
            plat.rock((e.x, e.y, G + s_ * 0.2), (s_ * 1.8, s_ * 1.4, s_ * 1.0), DARK if s_ > 1.0 else ROCK, 1,
                      (0, 0, rng.uniform(0, 6.28)), jitter=0.22)


# ------------------------------------------------------------------ balaustrada (linhas da TerraceGuard)
def _rail_blocked(a_deg):
    x, y = _circ_pt(RAIL_R, a_deg)
    # abertura da escada (a guarda do db_col abre |y - y_escada| < w/2 + 0,8 no topo; os banzos vao a w/2 + 1,2)
    if x > CX + 20.0 and abs(y - L.SUMMON_STAIR[1]) < L.SUMMON_STAIR[2] / 2 + 1.7:
        return "stair"
    if in_tower(x, y, 0.9):
        return "tower"
    return None


def rail_spans(step=0.5):
    n = int(360 / step)
    flags = [_rail_blocked(i * step) for i in range(n)]
    i0 = next(i for i in range(n) if flags[i])
    spans, cur = [], None
    for k in range(1, n + 1):
        i = (i0 + k) % n
        a = i0 * step + k * step
        if flags[i] is None:
            if cur is None:
                cur = [a, a, flags[(i - 1) % n]]
            cur[1] = a
        elif cur is not None:
            spans.append((cur[0], cur[1], cur[2], flags[i]))
            cur = None
    return spans


def _lamp_head(mb, glow, top, rz, s=1.0):
    """lanterna de posto: base de ouro, caixa de luz, montantes azul-marinho, chapeu laranja (acento marcial)"""
    mb.box((1.05 * s, 1.05 * s, 0.3), top + Vector((0, 0, 0.15)), (0, 0, rz), "Metal_Gold", 0.0)
    glow.box((0.78 * s, 0.78 * s, 1.0 * s), top + Vector((0, 0, 0.3 + 0.5 * s)), (0, 0, rz), "Lantern_Glow", 0.0)
    for du in (-1, 1):
        for dv in (-1, 1):
            q = Vector((du * 0.44 * s, dv * 0.44 * s, 0.0))
            q.rotate(Euler((0, 0, rz)))
            mb.box((0.26, 0.26, 1.1 * s), top + q + Vector((0, 0, 0.3 + 0.5 * s)), (0, 0, rz), "Plaster_DB_Navy", 0.0)
    mb.cyl(0.95 * s, 0.6 * s, top + Vector((0, 0, 0.3 + 1.0 * s + 0.3 * s)), (0, 0, rz + math.pi / 4),
           "Roof_DB_Orange", 4, r2=0.22, bevel=0.0)
    PK.octa(mb, top + Vector((0, 0, 0.3 + 1.6 * s + 0.35)), 0.3, 0.38, "Metal_Gold", rot=rz)


def rail(mb, glow):
    zb = LV0 + 0.05
    for a0, a1, why0, why1 in rail_spans():
        ln = math.radians(a1 - a0) * RAIL_R
        nb = max(1, int(round(ln / 4.2)))
        angs = [a0 + (a1 - a0) * i / nb for i in range(nb + 1)]
        pts = [Vector((*_circ_pt(RAIL_R, a), zb)) for a in angs]
        for i, (p, a) in enumerate(zip(pts, angs)):
            end = i in (0, len(pts) - 1)
            gate = (i == 0 and why0 == "stair") or (i == len(pts) - 1 and why1 == "stair")
            rz = math.radians(a)
            s = 1.3 if gate else 1.0
            h = 3.4 if gate else 2.7
            mb.box((1.45 * s, 1.45 * s, 0.4), p + Vector((0, 0, 0.2)), (0, 0, rz), "Plaster_DB_Navy", 0.0)
            mb.box((1.1 * s, 1.1 * s, h), p + Vector((0, 0, h / 2 + 0.3)), (0, 0, rz), "Plaster_DB_White", 0.0)
            mb.box((1.4 * s, 1.4 * s, 0.35), p + Vector((0, 0, h + 0.47)), (0, 0, rz), "Roof_DB_Blue", 0.0)
            top = p + Vector((0, 0, h + 0.65))
            if gate or (i % 5 == 2 and not end):
                _lamp_head(mb, glow, top, rz, 1.15 * s if gate else 0.9)
            else:
                PK.octa(mb, top + Vector((0, 0, 0.35)), 0.34, 0.4, "Metal_Gold", rot=rz)
        for a, b in zip(pts, pts[1:]):
            d = b - a
            if d.length < 1.6:
                continue
            u = d.normalized()
            a2, b2 = a + u * 0.55, b - u * 0.55
            mb.beam(a2 + Vector((0, 0, 0.35)), b2 + Vector((0, 0, 0.35)), 0.9, 0.5, "Plaster_DB_White", 0.0)
            mb.beam(a2 + Vector((0, 0, 2.2)), b2 + Vector((0, 0, 2.2)), 0.75, 0.42, "Roof_DB_Blue", 0.0)
            mb.beam(a2 + Vector((0, 0, 2.52)), b2 + Vector((0, 0, 2.52)), 0.5, 0.26, "Metal_Gold", 0.0)
            nbal = max(1, int(d.length / 1.5) - 1)
            for k in range(nbal):
                q = a2 + (b2 - a2) * ((k + 1) / (nbal + 1))
                mb.box((0.45, 0.45, 1.5), q + Vector((0, 0, 1.3)), (0, 0, math.atan2(d.y, d.x) + math.pi / 4),
                       "Plaster_DB_White", 0.0)


# ------------------------------------------------------------------ pilones Capsule, postes de lanterna, escada
def pylon(mb, glow, x, y):
    z = LV0
    mb.cyl(2.35, 1.3, (x, y, z + 0.65), (0, 0, math.pi / 8), "Stone_DB_Block", 8, bevel=0.0)
    mb.cyl(2.0, 0.5, (x, y, z + 1.55), (0, 0, 0), "Plaster_DB_Navy", 16, bevel=0.0)
    mb.cyl(1.55, 13.2, (x, y, z + 1.8 + 6.6), (0, 0, 0), "Plaster_DB_White", 16, bevel=0.0)
    mb.cyl(1.75, 0.7, (x, y, z + 9.0), (0, 0, 0), "Plaster_DB_Navy", 16, bevel=0.0)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2 + YAW
        d = Vector((math.cos(a), math.sin(a), 0.0))
        for z0, z1 in ((2.6, 8.5), (9.5, 14.2)):
            c = Vector((x, y, z + (z0 + z1) / 2)) + d * 1.42
            mb.box((0.5, 1.3, z1 - z0), c, (0, 0, a), "Glass_DB_Blue", 0.0)
            glow.box((0.3, 0.32, z1 - z0 - 0.8), c + d * 0.28, (0, 0, a), "DB_Cyan_Glow", 0.0)
    mb.cyl(1.95, 0.45, (x, y, z + 15.2), (0, 0, 0), "Metal_Gold", 16, bevel=0.0)
    mb.cyl(3.0, 0.85, (x, y, z + 15.85), (0, 0, 0), "Plaster_DB_White", 20, r2=2.3, bevel=0.0)
    mb.cyl(3.05, 0.35, (x, y, z + 15.6), (0, 0, 0), "Roof_DB_Blue", 20, bevel=0.0)
    dome(mb, (x, y), 2.25, z + 16.25, "Roof_DB_Blue", n=16, rings=4, squash=0.62)
    mb.rod((x, y, z + 17.5), (x, y, z + 20.0), 0.2, "Metal_Gold", 6)
    glow.ico(0.5, (x, y, z + 20.3), "DB_Energy_Glow", 1)
    octo_col("DB_SumPylon", x, y, 2.3, Z - 0.5, z + 17.0)


def lamp_post(mb, glow, x, y, z, rz):
    mb.box((1.6, 1.6, 0.6), (x, y, z + 0.3), (0, 0, rz), "Stone_DB_Block", 0.0)
    mb.box((0.85, 0.85, 3.3), (x, y, z + 0.6 + 1.65), (0, 0, rz), "Plaster_DB_White", 0.0)
    mb.box((1.15, 1.15, 0.35), (x, y, z + 3.9 + 0.17), (0, 0, rz), "Roof_DB_Blue", 0.0)
    _lamp_head(mb, glow, Vector((x, y, z + 4.25)), rz, 1.1)
    col_box("DB_SumLamp", (1.7, 1.7, 6.8), (x, y, z + 3.4), (0, 0, rz))


def props(dress, glow, plat):
    for s in (-1, 1):
        p = P(s * PYLON_UV[0], PYLON_UV[1], 0.0)
        pylon(dress, glow, p.x, p.y)
    for s in (-1, 1):
        for th in LAMP_TH:
            t = math.radians(th)
            p = P(s * (R1 - 0.25) * math.sin(t), PC_V + (R1 - 0.25) * math.cos(t), 0.0)
            lamp_post(dress, glow, p.x, p.y, LV0, YAW + s * t)
    # escada visual do db_col (GROUND -> SUM, 8 x 0,75, sobe para oeste) + 2 postes de lanterna no pe
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if nm == "Summon":
            DL.vis_stairs(plat, base, ang, w, n, rise, tread, "Stone_Paving_DB", "Stone_DB_Block")
            for s in (-1, 1):
                lamp_post(dress, glow, base[0] + 1.3, base[1] + s * (w / 2 + 1.9), G, 0.0)


# ------------------------------------------------------------------ marcadores
def markers(c):
    ux, uy = math.cos(FACE), math.sin(FACE)
    yaw = yaw_to(ux, uy)
    mk("SUMMON_Main", P(0.0, 0.0, 0.0), (0, 0, yaw), 4.0, "ARROWS",
       props={"face_deg": L.SUMMON_FACE_DEG, "star_pivot": [round(c.x, 3), round(c.y, 3), round(c.z, 3)],
              "height": 60.1, "free_zone_v": list(FREE_V), "free_zone_w": 14.0, "floor": Z,
              "note": "raiz da torre de invocacao (+Y local = frente); zona livre na frente: v local em free_zone_v"})
    mk("SUMMON_Interact", P(0.0, PV + 1.9, LAND_Z + 0.12), (0, 0, yaw), 2.0, "SPHERE",
       props={"radius": 6.0, "portal_plane_v": PV, "floor": Z + LAND_Z,
              "note": "patamar do portal, 1,9 a frente do plano da energia (ProximityPrompt da invocacao)"})
    cam = P(0.0, PLAYER_V + 10.5, LAND_Z + 5.5)
    look = P(0.0, PV, LAND_Z + 5.5)
    mk("SUMMON_PlayerPosition", P(0.0, PLAYER_V, LAND_Z + 0.12), (0, 0, yaw + math.pi), 2.0, "ARROWS",
       props={"camera_pos": [round(cam.x, 2), round(cam.y, 2), round(cam.z, 2)],
              "camera_look": [round(look.x, 2), round(look.y, 2), round(look.z, 2)], "floor": Z + LAND_Z,
              "note": "jogador no patamar olhando o portal; camera da animacao atras dele, sobre a escada (livre)"})


def build():
    plat = MB("DB_Sum_Platform", COL, random.Random(7101), detail="near")
    dress = MB("DB_Sum_Dressing", COL, random.Random(7401), detail="near")
    glow = MB("DB_Sum_Energy", COL, random.Random(7501), detail="hero")
    T, c = build_tower(dress, glow)
    floor(plat, glow)
    sides(plat)
    rocks(plat)
    rail(dress, glow)
    wing_barrier(dress)
    props(dress, glow, plat)
    plat.finish()
    dress.finish()
    glow.finish()
    markers(c)
