# il_summon - PECA-HEROI No 1 da Ilha 1: torre estrelada de invocacao + praca redonda (zona summon).
# Prefixo SUM_, colecao 05_SUMMON; pecas moveis VFX_SUM_* em 12_VFX_HELPERS. Substitui il_blockout.summon().
# Referencias: refs/ref_08..12 (torre em 5 angulos) e ref_14/15/18 (posicao na ilha).
#
# Referencial da torre (F): origem = L.SUMMON_TOWER no nivel T1; +v = frente (L.SUMMON_FACE_DEG, para o anel e a
# entrada); +u = lateral; z para cima a partir de T1. O eixo vertical da torre (esfera armilar) fica em v = AX.
#   base: soco escuro 28 x 19,6 + podio de alvenaria azul-acinzentada com friso de ouro e estrelas de 4 pontas;
#   escadaria frontal de 5 degraus com bordas azuis brilhando -> patamar -> PORTAL em arco (energia azul + estrela
#   de cristal; nao se entra: e a maquina de invocacao); pedestais com cristais, 4 lanternas japonesas nos cantos;
#   corpo L1 (portal) -> cornija de ouro -> L2 (janela-estrela) -> cornija -> coroa L3 -> prato de ouro;
#   esfera armilar: gaiola fixa + 3 aneis moveis (VFX_SUM_Ring_1..3) + estrela dourada (VFX_SUM_Star) + constelacao
#   de estrelas de cristal azul; 2 mastros laterais com estandartes azul-royal e lanternas penduradas.
# Praca: piso redondo de mosaico (roxo + estrela + aneis dourados), balaustrada de pedra e ouro aberta para a
# escada do anel (170 graus, il_col.RADIAL_STAIRS) e para a vila (NE); livre >= 14 x 14 na frente da torre.
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box, mk
import il_layout as L
import fm_lib
from fm_lib import light
import fm_parts as FP
from fm_parts import Frame
import fm_portal_kit as PK
from il_col import RADIAL_STAIRS, STAIR_TOP_R
import il_summon_kit as K

# ------------------------------------------------------------------ materiais novos da zona (4 de 6)
_S = fm_lib.S
fm_lib.MATS.setdefault("Crystal_SumPortal_Glow", (_S(58, 70, 232), 0.3, 0.0, 1.15, _S(64, 84, 255), 0.0))
fm_lib.MATS.setdefault("Crystal_SumStar_Glow", (_S(178, 222, 255), 0.2, 0.0, 2.6, _S(150, 206, 255), 0.0))
fm_lib.MATS.setdefault("Stone_SumFloor_Pale", (_S(212, 194, 236), 0.8, 0.0, 0, None, 0.06))
fm_lib.MATS.setdefault("Stone_SumBlock", (_S(126, 130, 170), 0.8, 0.0, 0, None, 0.08))    # bloco claro da alvenaria

# ------------------------------------------------------------------ referencial e medidas (studs)
TX, TY = L.SUMMON_TOWER
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2                       # o blockout usa o mesmo: +Y local = frente
Z0 = L.T1
F = Frame(TX, TY, Z0, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))       # +u (mundo)
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))      # +v = frente (mundo)
ZZ = Vector((0.0, 0.0, 1.0))
CX, CY = L.SUMMON_C
PR = L.SUMMON_R

AX = -3.0                    # v do eixo vertical (esfera, coroa, L2)
PLINTH = (14.0, -11.6, 8.0)  # meia largura u, v de tras, v da frente (soco escuro, z -0.5..0.8)
PLZ = 0.8
POD = (12.8, -10.2, 7.2)     # podio de alvenaria (z 0.8..3.0) + friso de ouro (3.0..3.3)
POD_TOP = 3.3
ST_W, ST_N, ST_RISE, ST_TREAD = 7.6, 5, 0.8, 1.6
ST_FOOT = 13.0               # v do pe da escada (SUMMON_Interact)
LAND_Z = ST_N * ST_RISE      # 4.0 patamar do portal
LAND_V = (1.2, ST_FOOT - ST_N * ST_TREAD)   # 1.2 .. 5.0
CORR = ST_W / 2 + 1.2        # meia largura do corredor da escada (com os banzos) = 5.0
PORT_HW, PORT_SPRING = 4.0, 12.0            # vao do portal (8 x 16 ate o fecho), plano da energia em v 1.3
L1 = (7.3, -8.8, 1.2, POD_TOP, 20.4)        # corpo L1: meia largura, v tras, v frente (nicho), z0, z1
L2 = (6.0, -7.7, 1.1, 21.3, 31.8)
L3 = (4.6, AX - 4.6, AX + 4.6, 32.6, 36.4)
ZS = 46.0                    # centro da esfera armilar (acima de T1)
CAGE_R = 9.2
MAST_U, MAST_V = 10.4, AX
FREE_V = (ST_FOOT, ST_FOOT + 14.0)          # espaco livre na frente (14 x 14)
BUT_V = 2.35                 # v dos contrafortes da frente do L1 (ladeiam o frontispicio)
L1_SWIN = (13.4, 18.1, 1.3)  # janelas dos lados do L1: z do peitoril, z da nascenca, meia largura (arco pleno)
L1_BWIN = (7.0, 14.8, 1.7)   # janela gotica do fundo do L1
BAN_TH = math.radians(35.0)  # estandartes girados 35 graus para a frente: leem de frente, dos lados e de tras


def P(u, v, z=0.0):
    return F.p(u, v, z)


def RT(rx=0.0, ry=0.0, rz=0.0):
    return F.r(rx, ry, rz)


def to_local(x, y):
    d = Vector((x - TX, y - TY, 0.0))
    return d.dot(XU), d.dot(YV)


def in_footprint(x, y, pad=0.0):
    """ponto dentro da pegada da torre (soco + escada)"""
    u, v = to_local(x, y)
    if abs(u) < PLINTH[0] + pad and PLINTH[1] - pad < v < PLINTH[2] + pad:
        return True
    return abs(u) < CORR + 1.4 + pad and PLINTH[2] - 0.1 < v < ST_FOOT + pad


# escada do anel (terreno): eixo radial a 170 graus, topo em r = STAIR_TOP_R
_SA = [a for k, a, w in RADIAL_STAIRS if k == "SUMMON"][0]
_SW = [w for k, a, w in RADIAL_STAIRS if k == "SUMMON"][0]
SU = Vector((math.cos(math.radians(_SA)), math.sin(math.radians(_SA)), 0.0))    # sobe a escada (para fora)
SL = Vector((-SU.y, SU.x, 0.0))
S_HW = _SW / 2 + 1.2         # meia largura com os banzos


def stair_zone(x, y, pad=0.0):
    """ponto sobre o entalhe da escada do anel (nao pavimentar)"""
    p = Vector((x, y, 0.0))
    return p.dot(SU) < STAIR_TOP_R + 0.2 + pad and abs(p.dot(SL)) < S_HW + pad


# cameras de revisao (360 graus + altura do jogador)
def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


CAMS = {
    "CAM_Summon_Front": _cam(0.0, 66.0, 22.0, 0.0, AX, 28.0, 22),
    "CAM_Summon_34": _cam(-40.0, 50.0, 26.0, 0.0, AX, 27.0, 22),
    "CAM_Summon_Side": _cam(-74.0, 2.0, 22.0, 0.0, AX, 25.0, 22),
    "CAM_Summon_Side2": _cam(72.0, 8.0, 22.0, 0.0, AX, 25.0, 22),
    "CAM_Summon_Back": _cam(10.0, -74.0, 26.0, 0.0, AX, 25.0, 22),
    "CAM_Summon_Player": _cam(-4.5, 31.0, 5.4, 0.0, AX, 22.0, 18),
    "CAM_Summon_High": _cam(34.0, 56.0, 58.0, 0.0, AX, 24.0, 22),
    "CAM_Summon_Base": _cam(9.0, 30.0, 7.5, 0.0, 4.0, 5.5, 22),
    "CAM_Summon_Top": ((CX + 0.01, CY - 6.0, L.T1 + 150.0), (CX, CY, L.T1), 24),
    # chegada pela escada do anel (170 graus): o jogador ve a torre de frente, a 3/4
    "CAM_Summon_Arrive": ((-78.0, 13.0, L.RING + 5.4), (-110.0, 24.0, L.T1 + 9.0), 20),
}


# ------------------------------------------------------------------ utilidades
def face_skin(mb, a_uv, b_uv, z0, z1, rng, openings=(), thick=0.8, course=2.0, blk=(2.4, 4.0),
              m="Stone_SumBlock", m2="Summon_Stone", quoins=(True, True), base_dark=True, mix=0.1):
    """pele de alvenaria (blocos) numa face vertical da torre; a_uv, b_uv em (u, v) locais"""
    a = P(a_uv[0], a_uv[1], 0.0)
    b = P(b_uv[0], b_uv[1], 0.0)
    openings = [tuple([o[0], o[1], Z0 + o[2], Z0 + o[3]] + list(o[4:])) for o in openings]
    FP.masonry_wall(mb, (a.x, a.y), (b.x, b.y), Z0 + z0, Z0 + z1, thick, rng, m=m, m2=m2, course=course, mix=mix,
                    openings=openings, blk=blk, core=False, quoins=quoins, base_dark=base_dark, bevel=0.14)


def lbox(mb, size, u, v, z, m, bevel=0.1, rz=0.0):
    """caixa no referencial da torre (z = centro, relativo a T1)"""
    mb.box(size, P(u, v, z), RT(0, 0, rz), m, bevel)


def lbox2(mb, u0, v0, z0, u1, v1, z1, m, bevel=0.1):
    lbox(mb, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, m, bevel)


def lcol(size, u, v, z, area="SummonTower"):
    col_box(area, size, P(u, v, z), RT())


def lcol2(u0, v0, z0, u1, v1, z1, area="SummonTower"):
    lcol((abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, area)


def gold_star4(gold, u, v, z, r, face="v+", depth=0.28):
    """estrela dourada de 4 pontas aplicada numa face (v+ frente, v- tras, u+ / u- lados)"""
    if face in ("v+", "v-"):
        s = 1.0 if face == "v+" else -1.0
        K.star(gold, P(u, v + s * depth * 0.5, z), XU, ZZ, 4, r, r * 0.26, depth, "Metal_Gold", edge=0.12)
    else:
        s = 1.0 if face == "u+" else -1.0
        K.star(gold, P(u + s * depth * 0.5, v, z), YV, ZZ, 4, r, r * 0.26, depth, "Metal_Gold", edge=0.12)


# ------------------------------------------------------------------ praca: piso de mosaico
def _ring_pieces(r0, r1, step_len, a_off=0.0):
    """pecas (poligonos mundo) de um anel em volta do centro da praca, cortadas no entalhe da escada"""
    out = []
    rm = (r0 + r1) / 2
    n = max(8, int(round(2 * math.pi * rm / step_len)))
    for i in range(n):
        a0 = a_off + 360.0 * i / n
        a1 = a_off + 360.0 * (i + 1) / n
        g = math.degrees(0.11 / rm)
        pts = IL.arc_pts(r1, a0 + g, a1 - g, max(1.0, (a1 - a0) / 2.0), CX, CY)
        pts += IL.arc_pts(r0, a1 - g, a0 + g, max(1.0, (a1 - a0) / 2.0), CX, CY)
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        if in_footprint(cx, cy, -0.6):
            continue
        if stair_zone(cx, cy):
            pts = IL.clip(pts, -SU.x, -SU.y, -(STAIR_TOP_R + 0.25))
            if len(pts) < 3 or abs(IL.area(pts)) < 0.3:
                continue
        out.append(IL.ccw(pts))
    return out


def plaza_floor():
    rng = random.Random(601)
    mb = MB("SUM_Plaza_Floor", "05_SUMMON", rng, detail="far")
    # base escura (rejunte / borda), cortada na linha do topo da escada do anel
    disc = IL.arc_pts(PR, 0.0, 360.0, 4.0, CX, CY)[:-1]
    disc = IL.clip(disc, -SU.x, -SU.y, -(STAIR_TOP_R + 0.25))
    mb.prism(IL.ccw(disc), Z0 - 0.3, Z0 + 0.06, "Summon_Stone_Dark")
    # campo roxo
    mb.prism(IL.ccw(IL.arc_pts(25.3, 0.0, 360.0, 4.0, CX, CY)[:-1]), Z0 - 0.02, Z0 + 0.1, "Summon_Floor")
    # aneis dourados e lavanda
    for poly in _ring_pieces(25.35, 26.05, 3.2):
        mb.prism(poly, Z0 - 0.02, Z0 + 0.13, "Metal_Gold")
    for poly in _ring_pieces(26.2, 27.95, 2.5, 2.0):
        mb.prism(poly, Z0 - 0.02, Z0 + 0.17 + rng.uniform(-0.02, 0.02), "Stone_Paving_Warm")
    for r0, r1, m, st in ((12.4, 12.9, "Metal_Gold", 3.0), (13.0, 14.3, "Stone_SumFloor_Pale", 2.6),
                          (14.4, 14.9, "Metal_Gold", 3.0), (22.6, 23.2, "Stone_SumFloor_Pale", 3.0)):
        for poly in _ring_pieces(r0, r1, st, 1.0):
            mb.prism(poly, Z0 - 0.02, Z0 + 0.14, m)
    # estrela de 5 pontas no centro (uma ponta para a torre) com contorno de ouro
    to_t = math.atan2(TY - CY, TX - CX)
    rot = to_t - math.pi / 2
    c = Vector((CX, CY, Z0 - 0.02))
    K.star_flat(mb, c, (1, 0, 0), (0, 1, 0), 5, 10.2, 4.1, 0.16, "Stone_SumFloor_Pale", rot=rot)
    pts = K.star_pts(5, 10.2, 4.1, rot)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        mb.beam((CX + a[0], CY + a[1], Z0 + 0.1), (CX + b[0], CY + b[1], Z0 + 0.1), 0.42, 0.24, "Metal_Gold", 0.0)
    K.star_flat(mb, c, (1, 0, 0), (0, 1, 0), 5, 3.2, 1.3, 0.2, "Metal_Gold", rot=rot)
    # estrelinhas de 4 pontas douradas no campo roxo (fora da pegada da torre)
    for i in range(10):
        a = math.radians(18.0 + 36.0 * i)
        x, y = CX + 18.9 * math.cos(a), CY + 18.9 * math.sin(a)
        if in_footprint(x, y, 1.5):
            continue
        K.star_flat(mb, (x, y, Z0 - 0.02), (1, 0, 0), (0, 1, 0), 4, 1.7, 0.45, 0.17, "Metal_Gold", rot=a)
    mb.finish()


# ------------------------------------------------------------------ praca: balaustrada (pedra clara + ouro)
RB = 26.9            # raio da balaustrada
VILLAGE_A = 42.0     # abertura para a vila (NE), graus a partir do centro da praca
VILLAGE_HW = 5.6


def _rail_blocked(a_deg):
    x = CX + RB * math.cos(math.radians(a_deg))
    y = CY + RB * math.sin(a_deg * math.pi / 180.0)
    p = Vector((x, y, 0.0))
    if abs(p.dot(SL)) < S_HW + 0.35 and p.dot(SU) < STAIR_TOP_R + 3.0:
        return "stair"
    d = (a_deg - VILLAGE_A + 180.0) % 360.0 - 180.0
    if abs(math.radians(d) * RB) < VILLAGE_HW:
        return "village"
    if in_footprint(x, y, 0.9):
        return "tower"
    return None


def rail_spans():
    step = 0.25
    n = int(360 / step)
    flags = [_rail_blocked(i * step) for i in range(n)]
    # comeca num ponto bloqueado para as corridas nao cruzarem o zero
    i0 = next(i for i in range(n) if flags[i])
    spans = []
    cur = None
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


def plaza_rail():
    rng = random.Random(611)
    mb = MB("SUM_Plaza_Rail", "05_SUMMON", rng, detail="near")
    zb = Z0 + 0.17
    for a0, a1, why0, why1 in rail_spans():
        ln = math.radians(a1 - a0) * RB
        nb = max(1, int(round(ln / 4.3)))
        angs = [a0 + (a1 - a0) * i / nb for i in range(nb + 1)]
        pts = [Vector((CX + RB * math.cos(math.radians(a)), CY + RB * math.sin(math.radians(a)), zb)) for a in angs]
        for i, (p, a) in enumerate(zip(pts, angs)):
            end = i in (0, len(pts) - 1)
            gate = (i == 0 and why0 in ("stair", "village")) or (i == len(pts) - 1 and why1 in ("stair", "village"))
            rz = math.radians(a)
            s = 1.35 if gate else 1.0
            h = 3.6 if gate else 2.8
            mb.box((1.5 * s, 1.5 * s, 0.4), p + Vector((0, 0, 0.2)), (0, 0, rz), "Stone_Wall_Light", 0.1)
            mb.box((1.15 * s, 1.15 * s, h), p + Vector((0, 0, h / 2 + 0.3)), (0, 0, rz), "Stone_Wall_Light", 0.12)
            mb.box((1.5 * s, 1.5 * s, 0.35), p + Vector((0, 0, h + 0.47)), (0, 0, rz), "Stone_Wall_Light", 0.1)
            top = p + Vector((0, 0, h + 0.65))
            if gate or (i % 3 == 1 and not end):
                # lanterninha no poste
                mb.box((0.95 * s, 0.95 * s, 0.25), top + Vector((0, 0, 0.12)), (0, 0, rz), "Metal_Gold", 0.05)
                mb.box((0.72 * s, 0.72 * s, 0.95 * s), top + Vector((0, 0, 0.25 + 0.47 * s)), (0, 0, rz),
                       "Lantern_Glow", 0.0)
                mb.cyl(0.85 * s, 0.55 * s, top + Vector((0, 0, 0.25 + 0.95 * s + 0.27 * s)), (0, 0, rz + math.pi / 4),
                       "Metal_Gold", 4, r2=0.12, bevel=0.0)
            else:
                mb.box((0.62, 0.62, 0.25), top + Vector((0, 0, 0.12)), (0, 0, rz), "Metal_Gold", 0.05)
                PK.octa(mb, top + Vector((0, 0, 0.62)), 0.36, 0.42, "Metal_Gold", rot=rz)
        for a, b in zip(pts, pts[1:]):
            d = b - a
            if d.length < 1.6:
                continue
            u = d.normalized()
            a2, b2 = a + u * 0.55, b - u * 0.55
            mb.beam(a2 + Vector((0, 0, 0.35)), b2 + Vector((0, 0, 0.35)), 0.95, 0.5, "Stone_Wall_Light", 0.08)
            mb.beam(a2 + Vector((0, 0, 2.45)), b2 + Vector((0, 0, 2.45)), 0.8, 0.42, "Stone_Wall_Light", 0.08)
            mb.beam(a2 + Vector((0, 0, 2.74)), b2 + Vector((0, 0, 2.74)), 0.45, 0.2, "Metal_Gold", 0.0)
            nbal = max(1, int(d.length / 1.45) - 1)
            for k in range(nbal):
                q = a2 + (b2 - a2) * ((k + 1) / (nbal + 1))
                mb.box((0.48, 0.48, 1.6), q + Vector((0, 0, 1.4)), (0, 0, math.atan2(d.y, d.x) + math.pi / 4),
                       "Stone_Wall_Light", 0.0)
        # colisao: cordas de ate ~24 graus
        nc = max(1, int(math.ceil((a1 - a0) / 24.0)))
        for k in range(nc):
            ca = a0 + (a1 - a0) * k / nc
            cb = a0 + (a1 - a0) * (k + 1) / nc
            pa = Vector((CX + RB * math.cos(math.radians(ca)), CY + RB * math.sin(math.radians(ca)), zb))
            pb = Vector((CX + RB * math.cos(math.radians(cb)), CY + RB * math.sin(math.radians(cb)), zb))
            d = pb - pa
            c = (pa + pb) / 2
            col_box("SummonRail", (d.length + 1.2, 1.3, 4.4), (c.x, c.y, zb + 2.0), (0, 0, math.atan2(d.y, d.x)))
    mb.finish()


# ------------------------------------------------------------------ torre: pedra (soco, podio, escada, corpos)
def tower_stone(stone, gold, glow):
    rng = random.Random(621)
    pu, pv0, pv1 = PLINTH
    # soco escuro (3 blocos macicos com fiada de blocos nas faces)
    for s in (-1, 1):
        lbox2(stone, s * CORR, pv0, -0.5, s * pu, pv1, PLZ - 0.1, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -CORR, pv0, -0.5, CORR, POD[1], PLZ - 0.1, "Summon_Stone_Dark", 0.0)
    face_skin(stone, (-pu - 0.2, pv1 + 0.2), (-CORR, pv1 + 0.2), -0.5, PLZ, rng, course=1.4, blk=(2.2, 3.4),
              thick=0.7, m="Summon_Stone_Dark", m2="Summon_Stone", base_dark=False, quoins=(False, False))
    face_skin(stone, (CORR, pv1 + 0.2), (pu + 0.2, pv1 + 0.2), -0.5, PLZ, rng, course=1.4, blk=(2.2, 3.4),
              thick=0.7, m="Summon_Stone_Dark", m2="Summon_Stone", base_dark=False, quoins=(False, False))
    for s in (-1, 1):
        face_skin(stone, (s * (pu + 0.2), pv1 + 0.5), (s * (pu + 0.2), pv0 - 0.5), -0.5, PLZ, rng, course=1.4,
                  blk=(2.2, 3.4), thick=0.7, m="Summon_Stone_Dark", m2="Summon_Stone", base_dark=False,
                  quoins=(False, False))
    face_skin(stone, (-pu - 0.5, pv0 - 0.2), (pu + 0.5, pv0 - 0.2), -0.5, PLZ, rng, course=1.4, blk=(2.2, 3.4),
              thick=0.7, m="Summon_Stone_Dark", m2="Summon_Stone", base_dark=False, quoins=(False, False))
    for s in (-1, 1):
        lbox2(gold, s * CORR, pv1 + 0.15, PLZ - 0.14, s * (pu + 0.45), pv1 + 0.5, PLZ + 0.14, "Metal_Gold", 0.0)
        lbox2(gold, s * (pu + 0.15), pv0 - 0.5, PLZ - 0.14, s * (pu + 0.5), pv1 + 0.5, PLZ + 0.14, "Metal_Gold", 0.0)
    lbox2(gold, -pu - 0.5, pv0 - 0.5, PLZ - 0.14, pu + 0.5, pv0 - 0.15, PLZ + 0.14, "Metal_Gold", 0.0)
    # podio: nucleo escuro + pele de alvenaria (2 fiadas) + friso de ouro
    du, dv0, dv1 = POD
    for s in (-1, 1):
        lbox2(stone, s * CORR, dv0 + 0.2, PLZ - 0.1, s * (du - 0.2), dv1 - 0.2, 3.0, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -CORR, dv0 + 0.2, PLZ - 0.1, CORR, LAND_V[0], 3.0, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        face_skin(stone, (s * CORR, dv1 + 0.1), (s * (du + 0.3), dv1 + 0.1), PLZ, 3.0, rng, course=1.1,
                  blk=(2.0, 3.2), thick=0.6)
        face_skin(stone, (s * du, dv1 + 0.4), (s * du, dv0 - 0.4), PLZ, 3.0, rng, course=1.1, blk=(2.0, 3.2),
                  thick=0.6)
    face_skin(stone, (-du - 0.3, dv0), (du + 0.3, dv0), PLZ, 3.0, rng, course=1.1, blk=(2.0, 3.4), thick=0.6)
    for s in (-1, 1):
        lbox2(gold, s * (CORR - 0.05), dv0 - 0.35, 3.0, s * (du + 0.35), dv1 + 0.35, POD_TOP, "Metal_Gold", 0.06)
    lbox2(gold, -CORR, dv0 - 0.35, 3.0, CORR, LAND_V[0] + 0.2, POD_TOP, "Metal_Gold", 0.06)
    # estrelas de 4 pontas douradas nos paineis do podio (lados e fundo)
    for s in (-1, 1):
        for v in (-5.8, -1.0, 3.2):
            gold_star4(gold, s * (du + 0.35), v, 1.95, 0.85, "u+" if s > 0 else "u-")
    for u in (-8.2, -3.0, 3.0, 8.2):
        gold_star4(gold, u, dv0 - 0.35, 1.95, 0.85, "v-")
    # escadaria frontal (5 degraus) com banzos
    base = P(0.0, ST_FOOT, 0.0)
    FP.stairs(stone, "SummonTower", (base.x, base.y, base.z), FACE + math.pi, ST_W, ST_N, ST_RISE, ST_TREAD,
              "Summon_Stone", "Summon_Stone_Dark")
    # bordas azuis brilhando: ponta de cada piso + espelho, dos dois lados (ziguezague de luz)
    for i in range(ST_N):
        v_hi = ST_FOOT - ST_TREAD * i            # quina do degrau i (v)
        z_top = ST_RISE * (i + 1)
        for s in (-1, 1):
            uu = s * (ST_W / 2 - 0.3)
            lbox(glow, (0.36, ST_TREAD - 0.1, 0.14), uu, v_hi - ST_TREAD / 2 - 0.05, z_top + 0.03, "Summon_Blue_Glow", 0.0)
            lbox(glow, (0.36, 0.14, ST_RISE - 0.05), uu, v_hi + 0.06, z_top - ST_RISE / 2, "Summon_Blue_Glow", 0.0)
    # patamar do portal
    lbox2(stone, -CORR + 0.05, LAND_V[0], 0.0, CORR - 0.05, LAND_V[1], LAND_Z, "Summon_Stone", 0.12)
    lbox2(gold, -ST_W / 2, LAND_V[1] - 0.25, LAND_Z - 0.2, ST_W / 2, LAND_V[1] + 0.05, LAND_Z + 0.02, "Metal_Gold", 0.04)
    # --- corpo L1: nucleo (nicho do portal na frente) + contrafortes de canto + pele de alvenaria
    hw, v0, v1, z0, z1 = L1
    lbox2(stone, -hw, v0, z0, hw, v1, z1, "Summon_Stone_Dark", 0.0)
    # janelas altas do L1: uma em cada lado (acima da asa do mastro) e uma gotica no fundo
    s_side = (v1 - 0.6) - MAST_V
    side_op = (s_side - 1.75, s_side + 1.75, L1_SWIN[0] - 0.2, L1_SWIN[1] + L1_SWIN[2] + 0.5, L1_SWIN[2] + 0.45)
    for s in (-1, 1):
        face_skin(stone, (s * (hw + 0.25), v1 - 0.6), (s * (hw + 0.25), v0 + 0.6), z0, z1, rng, course=2.1,
                  blk=(2.6, 4.2), thick=0.8, openings=[side_op])
        for dv in (-1, 1):
            lbox(stone, (0.9, 0.7, L1_SWIN[1] - L1_SWIN[0]), s * (hw + 0.5), MAST_V + dv * (L1_SWIN[2] + 0.35),
                 (L1_SWIN[0] + L1_SWIN[1]) / 2, "Summon_Stone", 0.1)
    back_op = (hw - 0.6 - 2.1, hw - 0.6 + 2.1, L1_BWIN[0] - 0.2, L1_BWIN[1] + L1_BWIN[2] + 0.6, L1_BWIN[2] + 0.5)
    face_skin(stone, (hw - 0.6, v0 - 0.25), (-hw + 0.6, v0 - 0.25), z0, z1, rng, course=2.1, blk=(2.6, 4.2),
              thick=0.8, openings=[back_op])
    for s in (-1, 1):
        lbox(stone, (0.75, 0.9, L1_BWIN[1] - L1_BWIN[0]), s * (L1_BWIN[2] + 0.38), v0 - 0.5,
             (L1_BWIN[0] + L1_BWIN[1]) / 2, "Summon_Stone", 0.1)
    for su in (-1, 1):
        for vv in (v0, BUT_V):
            _buttress(stone, gold, su * hw, vv, z0, 22.2, 2.5, rng, spire=2.8,
                      edges=((-1, 1), (1, 1)) if vv > 0 else ((-1, -1), (1, -1)))
    # pele da frente do nucleo acima do timpano (atras do frontao)
    face_skin(stone, (-hw + 0.9, v1 + 0.35), (hw - 0.9, v1 + 0.35), 16.8, z1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, quoins=(False, False), base_dark=False)
    # frontispicio do portal: ombreiras, aduelas, timpano, frontao
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Stone_SumBlock" if k % 2 == 0 else "Summon_Stone"
            w = 2.3 if k % 2 == 0 else 2.0
            lbox(stone, (w, 2.9, zz1 - zz0 - 0.08), s * (PORT_HW + 1.1), 2.55, (zz0 + zz1) / 2, m, 0.14)
        # fundo do timpano (atras das aduelas)
        lbox2(stone, s * (PORT_HW + 0.35), v1, PORT_SPRING, s * 6.3, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -PORT_HW - 0.4, v1, PORT_SPRING + PORT_HW + 0.2, PORT_HW + 0.4, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    ac = P(0.0, 2.6, 0.0)
    FP.arch(stone, (ac.x, ac.y, 0.0), YAW, 2 * PORT_HW, Z0 + PORT_SPRING, PORT_HW, 2.9, m="Stone_SumBlock",
            key_m="Summon_Stone", n=9, band=1.5, keystone=True)
    # frontao (duas aguas) com beirada de ouro
    apex = (0.0, 22.6)
    for s in (-1, 1):
        a = P(s * 6.9, 3.45, 17.6)
        b = P(apex[0], 3.45, apex[1])
        stone.beam(a, b, 1.9, 1.2, "Stone_SumBlock", 0.12)
        ga = P(s * 7.1, 3.5, 18.35)
        gb = P(0.0, 3.5, apex[1] + 0.75)
        gold.beam(ga, gb, 2.1, 0.35, "Metal_Gold", 0.06)
    tri = [(-6.3, 17.6), (6.3, 17.6), (0.0, apex[1] - 0.2)]
    PK.plate(stone, tri, P(0.0, 3.0, 0.0), XU, ZZ, 1.0, "Summon_Stone_Dark")
    # --- cornija 1 (pedra + ouro), com braco ate os mastros
    lbox2(stone, -hw - 1.0, v0 - 1.0, z1, hw + 1.0, 2.4, z1 + 0.55, "Summon_Stone_Dark", 0.12)
    lbox2(gold, -hw - 1.2, v0 - 1.2, z1 + 0.55, hw + 1.2, 2.5, z1 + 0.9, "Metal_Gold", 0.08)
    # --- corpo L2 (janela-estrela na frente, janelas menores nos lados e no fundo)
    hw2, w0, w1, y0, y1 = L2
    lbox2(stone, -hw2, w0, y0, hw2, w1, y1, "Summon_Stone_Dark", 0.0)
    wcs = hw2 - 0.2                      # centro da janela ao longo da pele (a pele vai de -wcs a +wcs)
    win_front = (wcs - 3.5, wcs + 3.5, y0 + 1.0, y0 + 6.8 + 3.5, 3.5)
    face_skin(stone, (-hw2 + 0.2, w1 + 0.35), (hw2 - 0.2, w1 + 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    face_skin(stone, (hw2 - 0.2, w0 - 0.35), (-hw2 + 0.2, w0 - 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    vs = (w0 + w1) / 2
    ln_side = (w1 - 0.6) - (w0 + 0.6)
    for s in (-1, 1):
        a_uv = (s * (hw2 + 0.35), w1 - 0.6) if s > 0 else (s * (hw2 + 0.35), w0 + 0.6)
        b_uv = (s * (hw2 + 0.35), w0 + 0.6) if s > 0 else (s * (hw2 + 0.35), w1 - 0.6)
        side_win = (ln_side / 2 - 2.3, ln_side / 2 + 2.3, y0 + 2.4, y0 + 8.6, 2.3)
        face_skin(stone, a_uv, b_uv, y0, y1, rng, course=1.8, blk=(2.2, 3.6), thick=0.8, openings=[side_win])
    for su in (-1, 1):
        for vv in (w0, w1):
            _buttress(stone, gold, su * hw2, vv, y0, y1 + 1.4, 1.9, rng, spire=3.3, course=1.6)
    # janela-estrela da frente: aduelas + fundo de energia (o fundo fica no glow)
    wc = P(0.0, w1 + 0.4, 0.0)
    FP.arch(stone, (wc.x, wc.y, 0.0), YAW, 5.2, Z0 + y0 + 6.8, 2.6, 1.3, m="Stone_SumBlock", key_m="Summon_Stone",
            n=7, band=0.9, keystone=True)
    for s in (-1, 1):
        lbox2(stone, s * 2.6, w1 - 0.1, y0 + 1.4, s * 3.5, w1 + 1.05, y0 + 6.8, "Summon_Stone", 0.12)
    lbox2(gold, -3.7, w1 - 0.1, y0 + 1.0, 3.7, w1 + 1.2, y0 + 1.4, "Metal_Gold", 0.06)
    # --- cornija 2
    lbox2(stone, -hw2 - 0.9, w0 - 0.9, y1, hw2 + 0.9, w1 + 0.9, y1 + 0.5, "Summon_Stone_Dark", 0.12)
    lbox2(gold, -hw2 - 1.1, w0 - 1.1, y1 + 0.5, hw2 + 1.1, w1 + 1.1, y1 + 0.8, "Metal_Gold", 0.08)
    # --- coroa L3 + pinaculos
    h3, c0, c1, q0, q1 = L3
    lbox2(stone, -h3, c0, q0, h3, c1, q1, "Summon_Stone_Dark", 0.0)
    for (a_uv, b_uv) in (((-h3 - 0.3, c1 + 0.3), (h3 + 0.3, c1 + 0.3)), ((h3 + 0.3, c0 - 0.3), (-h3 - 0.3, c0 - 0.3)),
                         ((h3 + 0.3, c1 + 0.3), (h3 + 0.3, c0 - 0.3)), ((-h3 - 0.3, c0 - 0.3), (-h3 - 0.3, c1 + 0.3))):
        face_skin(stone, a_uv, b_uv, q0, q1, rng, course=1.9, blk=(2.0, 3.2), thick=0.7, quoins=(False, False))
    lbox2(gold, -h3 - 0.7, c0 - 0.7, q1, h3 + 0.7, c1 + 0.7, q1 + 0.35, "Metal_Gold", 0.08)
    for su in (-1, 1):
        for vv in (c0, c1):
            _buttress(stone, gold, su * h3, vv, q0, q1 + 0.9, 1.3, rng, spire=1.8, course=1.4)
    return rng


def _buttress(stone, gold, u, v, z0, z1, w, rng, spire=2.6, course=2.1, edges=()):
    """contraforte/pilar de canto em blocos alternados, capitel de ouro e pinaculo dourado.
    edges: quinas (du, dv) que recebem cantoneira vertical de ouro"""
    for du, dv in edges:
        lbox(gold, (0.36, 0.36, z1 - z0 - 0.6), u + du * (w / 2 - 0.08), v + dv * (w / 2 - 0.08), (z0 + z1) / 2,
             "Metal_Gold", 0.0)
    z = z0
    k = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        m = "Stone_SumBlock" if k % 2 == 0 else "Summon_Stone"
        ww = w if k % 2 == 0 else w - 0.3
        lbox(stone, (ww, ww, h - 0.08), u, v, z + h / 2, m, 0.14)
        z += h
        k += 1
    lbox(gold, (w + 0.4, w + 0.4, 0.35), u, v, z1 + 0.17, "Metal_Gold", 0.08)
    lbox(gold, (w * 0.7, w * 0.7, 0.4), u, v, z1 + 0.55, "Metal_Gold", 0.06)
    a = P(u, v, z1 + 0.75)
    PK.cone(gold, a, a + Vector((0, 0, spire)), w * 0.36, 0.02, "Metal_Gold", 4)


# ------------------------------------------------------------------ torre: ouro, estrelas, energia
def tower_details(stone, gold, glow):
    hw, v0, v1, z0, z1 = L1
    # energia do portal (arco) + estrela de cristal + faiscas + anel no chao
    pts = K.arch_poly(PORT_HW - 0.05, LAND_Z - 0.05, PORT_SPRING, 14)
    PK.plate(glow, pts, P(0.0, v1 + 0.08, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, v1 + 0.75, 9.4), XU, ZZ, 5, 2.7, 1.12, 0.55, "Crystal_SumStar_Glow", edge=0.3)
    rng = random.Random(631)
    for k in range(9):
        uu = rng.uniform(-3.2, 3.2)
        zz = rng.uniform(LAND_Z + 1.0, PORT_SPRING + 2.8)
        if abs(uu) < 2.8 and 6.6 < zz < 12.3:
            continue
        K.star(glow, P(uu, v1 + 0.3, zz), XU, ZZ, 4, rng.uniform(0.4, 0.7), 0.1, 0.12, "Crystal_SumStar_Glow")
    for r, w in ((2.0, 0.34), (1.1, 0.26)):
        PK.ring(glow, P(0.0, 2.5, LAND_Z + 0.05), r, XU, YV, w, 0.12, "Summon_Blue_Glow", 0, 360, 24)
    # cristais pequenos nos cantos do patamar
    cr = MB("SUM_Crystals", "05_SUMMON", random.Random(632), detail="hero")
    for s in (-1, 1):
        K.gem_cluster(cr, P(s * (CORR - 0.9), LAND_V[1] - 0.8, LAND_Z), 0.42, "Crystal_Blue", random.Random(640 + s))
    # arquivolta de ouro + chave com estrela
    PK.ring(gold, P(0.0, 4.1, PORT_SPRING), PORT_HW + 0.12, XU, ZZ, 0.3, 0.3, "Metal_Gold", 0, 180, 16)
    PK.ring(gold, P(0.0, 4.1, PORT_SPRING), PORT_HW + 1.62, XU, ZZ, 0.28, 0.3, "Metal_Gold", 0, 180, 18)
    for s in (-1, 1):
        lbox(gold, (0.3, 0.3, PORT_SPRING - LAND_Z), s * (PORT_HW + 0.12), 4.1, (LAND_Z + PORT_SPRING) / 2,
             "Metal_Gold", 0.0)
        lbox(gold, (2.7, 3.2, 0.35), s * (PORT_HW + 1.1), 2.55, PORT_SPRING + 0.1, "Metal_Gold", 0.06)
        lbox(gold, (2.7, 3.2, 0.35), s * (PORT_HW + 1.1), 2.55, POD_TOP + 0.2, "Metal_Gold", 0.06)
    # estrela de ouro com miolo azul no frontao (e a do fecho do arco)
    K.star(gold, P(0.0, 4.0, 19.6), XU, ZZ, 4, 2.6, 0.72, 0.55, "Metal_Gold", edge=0.35)
    K.star(glow, P(0.0, 4.45, 19.6), XU, ZZ, 4, 1.05, 0.34, 0.38, "Summon_Blue_Glow", edge=0.1)
    # estrelas de 4 pontas nos contrafortes (frente) e nos lados do corpo L1
    for s in (-1, 1):
        gold_star4(gold, s * hw, BUT_V + 1.25, 8.0, 0.8, "v+")
    # janelas altas dos lados do L1 (energia + estrelinha + arco e ombreiras de ouro)
    zs0, zsp, shw = L1_SWIN
    for s in (-1, 1):
        sp = K.arch_poly(shw, zs0, zsp, 8)
        PK.plate(glow, sp, P(s * (hw + 0.1), MAST_V, 0.0), YV, ZZ, 0.2, "Crystal_SumPortal_Glow")
        K.star(glow, P(s * (hw + 0.45), MAST_V, zsp - 0.6), YV, ZZ, 4, 0.95, 0.26, 0.28, "Crystal_SumStar_Glow",
               edge=0.15)
        PK.ring(gold, P(s * (hw + 0.95), MAST_V, zsp), shw + 0.25, YV, ZZ, 0.3, 0.3, "Metal_Gold", 0, 180, 10)
        lbox(gold, (0.35, 2 * shw + 1.2, 0.3), s * (hw + 0.8), MAST_V, zs0 - 0.1, "Metal_Gold", 0.05)
    # janela gotica do fundo do L1 (arco apontado) + estrela de ouro com miolo azul por cima
    zb0, zbs, bhw = L1_BWIN
    gp = [(-bhw, zb0), (bhw, zb0), (bhw, zbs)]
    for i in range(1, 6):
        t = i / 6.0
        a = math.radians(60.0 * t)
        gp.append((bhw - 2 * bhw * (1 - math.cos(a)), zbs + 2 * bhw * math.sin(a)))
    gp.append((0.0, zbs + 2 * bhw * math.sin(math.radians(60.0))))
    for i in range(5, 0, -1):
        t = i / 6.0
        a = math.radians(60.0 * t)
        gp.append((-(bhw - 2 * bhw * (1 - math.cos(a))), zbs + 2 * bhw * math.sin(a)))
    gp.append((-bhw, zbs))
    PK.plate(glow, gp, P(0.0, v0 - 0.12, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, v0 - 0.5, zbs - 1.2), XU, ZZ, 4, 1.25, 0.32, 0.3, "Crystal_SumStar_Glow", edge=0.15)
    gtop = zbs + 2 * bhw * math.sin(math.radians(60.0))
    for s in (-1, 1):
        lbox(gold, (0.3, 0.3, zbs - zb0), s * (bhw + 0.12), v0 - 1.0, (zb0 + zbs) / 2, "Metal_Gold", 0.0)
        gold.beam(P(s * (bhw + 0.12), v0 - 1.0, zbs), P(0.0, v0 - 1.0, gtop + 0.25), 0.3, 0.3, "Metal_Gold", 0.0)
    lbox(gold, (2 * bhw + 1.6, 1.1, 0.35), 0.0, v0 - 0.6, zb0 - 0.15, "Metal_Gold", 0.05)
    gold_star4(gold, 0.0, v0 - 0.65, 18.9, 1.05, "v-")
    K.star(glow, P(0.0, v0 - 1.05, 18.9), XU, ZZ, 4, 0.45, 0.15, 0.25, "Summon_Blue_Glow", edge=0.1)
    # --- janela-estrela (L2 frente) + janelas menores
    hw2, w0, w1, y0, y1 = L2
    pts = K.arch_poly(2.6, y0 + 1.4, y0 + 6.8, 10)
    PK.plate(glow, pts, P(0.0, w1 + 0.12, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, w1 + 0.7, y0 + 5.6), XU, ZZ, 5, 2.15, 0.9, 0.45, "Crystal_SumStar_Glow", edge=0.25)
    PK.plate(glow, pts, P(0.0, w0 - 0.12, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, w0 - 0.6, y0 + 5.6), XU, ZZ, 5, 1.7, 0.72, 0.4, "Crystal_SumStar_Glow", edge=0.2)
    vs = (w0 + w1) / 2
    for s in (-1, 1):
        sp = K.arch_poly(2.1, y0 + 2.4, y0 + 6.5, 8)
        PK.plate(glow, sp, P(s * (hw2 + 0.12), vs, 0.0), YV, ZZ, 0.2, "Crystal_SumPortal_Glow")
        K.star(glow, P(s * (hw2 + 0.55), vs, y0 + 5.4), YV, ZZ, 4, 1.35, 0.36, 0.35, "Crystal_SumStar_Glow", edge=0.2)
        PK.ring(gold, P(s * (hw2 + 0.95), vs, y0 + 6.5), 2.35, YV, ZZ, 0.3, 0.3, "Metal_Gold", 0, 180, 12)
    PK.ring(gold, P(0.0, w1 + 1.15, y0 + 6.8), 2.75, XU, ZZ, 0.3, 0.3, "Metal_Gold", 0, 180, 14)
    PK.ring(gold, P(0.0, w0 - 1.15, y0 + 6.8), 2.75, XU, ZZ, 0.3, 0.3, "Metal_Gold", 0, 180, 14)
    # estrela de 4 pontas sobre a janela (cornija 2)
    K.star(gold, P(0.0, w1 + 1.3, y1 + 0.2), XU, ZZ, 4, 1.8, 0.5, 0.45, "Metal_Gold", edge=0.3)
    K.star(glow, P(0.0, w1 + 1.65, y1 + 0.2), XU, ZZ, 4, 0.75, 0.25, 0.3, "Summon_Blue_Glow", edge=0.1)
    # --- coroa: emblema da frente + prato de ouro da esfera
    h3, c0, c1, q0, q1 = L3
    K.star(gold, P(0.0, c1 + 0.55, (q0 + q1) / 2), XU, ZZ, 4, 1.7, 0.46, 0.4, "Metal_Gold", edge=0.25)
    K.star(glow, P(0.0, c1 + 0.85, (q0 + q1) / 2), XU, ZZ, 4, 0.65, 0.2, 0.28, "Summon_Blue_Glow", edge=0.1)
    gold.cyl(4.7, 0.45, P(0.0, AX, q1 + 0.35 + 0.22), RT(), "Metal_Gold", 16, r2=4.1, bevel=0.06)
    PK.ring(gold, P(0.0, AX, q1 + 1.15), 4.0, XU, YV, 0.45, 0.5, "Metal_Gold", 0, 360, 24)
    return cr


# ------------------------------------------------------------------ mastros, estandartes, lanternas
def masts_and_lanterns(stone, gold, glow):
    rng = random.Random(651)
    bn = MB("SUM_Banners", "05_SUMMON", rng, detail="near")
    hw, v0, v1, z0, z1 = L1
    hw2, w0, w1, y0, y1 = L2
    z_pole = 29.8
    for s in (-1, 1):
        u = s * MAST_U
        # mastro em blocos + asa de ligacao com o corpo L1 + braco na cornija
        _buttress(stone, gold, u, MAST_V, POD_TOP, 31.0, 2.0, rng, spire=3.0, course=2.0,
                  edges=((s, 1), (s, -1)))
        for zc in (13.0, 22.5):
            lbox(gold, (2.35, 2.35, 0.32), u, MAST_V, zc, "Metal_Gold", 0.06)
        lbox2(stone, s * (hw - 0.1), MAST_V - 0.95, POD_TOP, s * (MAST_U - 0.9), MAST_V + 0.95, 12.2,
              "Summon_Stone", 0.12)
        lbox2(gold, s * (hw - 0.1), MAST_V - 1.1, 12.2, s * (MAST_U - 0.7), MAST_V + 1.1, 12.5, "Metal_Gold", 0.05)
        gold_star4(gold, s * ((hw + MAST_U) / 2 - 0.4), MAST_V + 0.95, 8.0, 0.75, "v+")
        gold_star4(gold, s * ((hw + MAST_U) / 2 - 0.4), MAST_V - 0.95, 8.0, 0.75, "v-")
        lbox2(stone, s * (hw + 0.8), MAST_V - 0.8, z1, s * (MAST_U - 0.9), MAST_V + 0.8, z1 + 0.9, "Summon_Stone_Dark",
              0.1)
        # haste horizontal girada 35 graus para a frente (referencial Fb no eixo do mastro): sai da parede do L2,
        # atravessa o mastro e leva o estandarte, que assim le de frente, dos lados e de tras
        mw = P(u, MAST_V, 0.0)
        Fb = Frame(mw.x, mw.y, Z0, YAW + s * BAN_TH)
        ub = Vector(Fb.p(1, 0, 0)) - Vector(Fb.p(0, 0, 0))
        stub = (MAST_U - (hw2 + 0.35)) / math.cos(BAN_TH)
        a = Fb.p(-s * stub, 0.0, z_pole)
        b = Fb.p(s * 7.0, 0.0, z_pole)
        bn.rod(a, b, 0.3, "Wood_Dark", 8)
        PK.cone(gold, b, b + ub * (s * 1.5), 0.45, 0.02, "Metal_Gold", 4)
        gold.ico(0.5, Fb.p(s * 6.8, 0.0, z_pole), "Metal_Gold", 1)
        for uu in (-s * (stub - 0.25), s * 1.3, s * 5.9):
            gold.box((0.35, 0.75, 0.75), Fb.p(uu, 0.0, z_pole), Fb.r(), "Metal_Gold", 0.04)
        K.banner(bn, gold, bn, Fb, 1.5 if s > 0 else -5.7, 5.7 if s > 0 else -1.5, 0.0, z_pole - 0.5, 12.6, tip=1.6)
        # lanterna pendurada na haste, entre o corpo e o mastro
        K.hang_lantern(stone, glow, gold, Fb.p(-s * 2.4, 0.0, z_pole - 0.3), 1.0, drop=0.9)
        # lanternas penduradas nos cantos da frente do L2 (bracos de ouro)
        br0 = P(s * (hw2 + 0.95), w1, 29.6)
        br1 = P(s * (hw2 + 2.3), w1 + 0.4, 29.6)
        gold.beam(br0, br1, 0.3, 0.3, "Metal_Gold", 0.0)
        gold.beam(P(s * (hw2 + 0.95), w1, 28.2), br1 - ZZ * 0.1, 0.24, 0.24, "Metal_Gold", 0.0)
        K.hang_lantern(stone, glow, gold, br1, 0.85, drop=0.55)
    bn.finish()
    # 4 lanternas japonesas nos cantos, sobre pilares com estrela de ouro
    pu, pv0, pv1 = PLINTH
    corners = [(s * 12.5, 6.0) for s in (-1, 1)] + [(s * 12.5, -9.8) for s in (-1, 1)]
    lamp_c = []
    for (u, v) in corners:
        lbox(stone, (3.3, 3.3, 0.5), u, v, PLZ + 0.25, "Summon_Stone_Dark", 0.12)
        for k, (hh, ww) in enumerate(((1.5, 2.9), (1.4, 2.6), (1.4, 2.9))):
            zc = PLZ + 0.5 + sum(x[0] for x in ((1.5, 2.9), (1.4, 2.6), (1.4, 2.9))[:k]) + hh / 2
            lbox(stone, (ww, ww, hh - 0.08), u, v, zc, "Stone_SumBlock" if k != 1 else "Summon_Stone", 0.14)
        ztop = PLZ + 0.5 + 4.3
        lbox(gold, (3.35, 3.35, 0.35), u, v, ztop + 0.17, "Metal_Gold", 0.08)
        # cantoneiras de ouro: 4 quinas verticais do pilar + chapa em L no pe
        for du in (-1, 1):
            for dv in (-1, 1):
                lbox(gold, (0.42, 0.42, 4.2), u + du * 1.37, v + dv * 1.37, PLZ + 0.55 + 2.1, "Metal_Gold", 0.0)
        lbox(gold, (3.5, 3.5, 0.3), u, v, PLZ + 0.62, "Metal_Gold", 0.05)
        su = 1 if u > 0 else -1
        gold_star4(gold, u + su * 1.45, v, PLZ + 2.7, 0.95, "u+" if su > 0 else "u-")
        gold_star4(gold, u, v + (1.45 if v > 0 else -1.45), PLZ + 2.7, 0.95, "v+" if v > 0 else "v-")
        lamp_c.append(K.corner_lantern(stone, glow, gold, F, u, v, ztop + 0.35, 1.05))
    # pedestais dos cristais grandes (na frente, dos dois lados da escada)
    for s in (-1, 1):
        u, v = s * 8.6, 5.8
        lbox(stone, (3.4, 3.4, 0.55), u, v, POD_TOP + 0.27, "Summon_Stone_Dark", 0.12)
        lbox(stone, (2.6, 2.6, 2.7), u, v, POD_TOP + 0.55 + 1.35, "Stone_SumBlock", 0.14)
        gold_star4(gold, u, v + 1.3, POD_TOP + 1.95, 0.8, "v+")
        lbox(gold, (3.1, 3.1, 0.35), u, v, POD_TOP + 3.25 + 0.17, "Metal_Gold", 0.08)
        stone.cyl(1.35, 0.5, P(u, v, POD_TOP + 3.6 + 0.25), RT(), "Summon_Stone_Dark", 8, r2=1.7, bevel=0.0)
    # postes com lanterninha no pe da escada
    for s in (-1, 1):
        u, v = s * (CORR + 0.65), ST_FOOT - 0.8
        lbox(stone, (1.5, 1.5, 0.4), u, v, 0.2, "Summon_Stone_Dark", 0.08)
        lbox(stone, (1.1, 1.1, 2.9), u, v, 0.4 + 1.45, "Stone_SumBlock", 0.12)
        lbox(gold, (1.45, 1.45, 0.3), u, v, 3.45, "Metal_Gold", 0.06)
        lbox(glow, (0.85, 0.85, 1.05), u, v, 3.6 + 0.52, "Lantern_Glow", 0.0)
        for du in (-1, 1):
            for dv in (-1, 1):
                lbox(gold, (0.2, 0.2, 1.1), u + du * 0.45, v + dv * 0.45, 4.12, "Metal_Gold", 0.0)
        gold.cyl(0.95, 0.6, P(u, v, 4.65 + 0.3), RT(0, 0, math.pi / 4), "Metal_Gold", 4, r2=0.15, bevel=0.0)
    return lamp_c


def crystals_big(cr):
    for s in (-1, 1):
        u, v = s * 8.6, 5.8
        base = P(u, v, POD_TOP + 4.0)
        K.gem_cluster(cr, base, 1.0, "Crystal_Blue", random.Random(660 + s))
    cr.finish()


# ------------------------------------------------------------------ esfera armilar, estrela, constelacao
def sphere(gold, glow):
    c = P(0.0, AX, ZS)
    fr = MB("SUM_Sphere_Frame", "05_SUMMON", random.Random(671), detail="hero")
    # gaiola fixa: 2 meridianos + equador
    PK.ring(fr, c, CAGE_R, XU, ZZ, 0.62, 0.46, "Metal_Gold", 0, 360, 44)
    PK.ring(fr, c, CAGE_R, YV, ZZ, 0.62, 0.46, "Metal_Gold", 0, 360, 44)
    PK.ring(fr, c, CAGE_R, XU, YV, 0.55, 0.42, "Metal_Gold", 0, 360, 44)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        d = XU * math.cos(a) + YV * math.sin(a)
        K.star(fr, c + d * CAGE_R, d.cross(ZZ), ZZ, 4, 0.8, 0.22, 0.3, "Metal_Gold", edge=0.15)
    # remate: bola, haste, estrela de 4 pontas com gema azul, ponta
    top = c + ZZ * CAGE_R
    fr.ico(0.65, top + ZZ * 0.5, "Metal_Gold", 1)
    fr.rod(top + ZZ * 0.4, top + ZZ * 3.7, 0.24, "Metal_Gold", 6)
    sc = top + ZZ * 2.1
    K.star(fr, sc, XU, ZZ, 4, 1.75, 0.45, 0.42, "Metal_Gold", edge=0.3)
    K.star(fr, sc, YV, ZZ, 4, 1.2, 0.35, 0.35, "Metal_Gold", edge=0.2)
    K.star(fr, sc, XU, ZZ, 4, 0.7, 0.26, 0.62, "Summon_Blue_Glow", edge=0.2)
    PK.cone(fr, top + ZZ * 3.7, top + ZZ * 4.9, 0.3, 0.02, "Metal_Gold", 4)
    fr.finish()
    # pecas moveis (VFX): 3 aneis + estrela
    specs = [
        # nome, raio, secao (w, h), eixo do plano (inclinacao), inclinacao graus, eixo de giro, rpm, enfeites
        ("VFX_SUM_Ring_1", 11.4, (0.95, 0.5), XU, 16.0, "z", 2.0, 6),
        ("VFX_SUM_Ring_2", 8.3, (0.72, 0.46), None, 90.0, "-z", 4.0, 4),
        ("VFX_SUM_Ring_3", 7.35, (0.66, 0.42), (XU * math.cos(math.radians(120)) + YV * math.sin(math.radians(120))),
         58.0, "normal", 6.0, 4),
    ]
    rings = []
    for name, rr, (w, h), tilt_ax, tilt, spin, rpm, nst in specs:
        mb = MB(name, "12_VFX_HELPERS", random.Random(len(name) * 13), detail="hero")
        if tilt_ax is None:
            ang = math.radians(30.0)
            u = XU * math.cos(ang) + YV * math.sin(ang)
            v = ZZ.copy()
        else:
            ta = Vector(tilt_ax).normalized()
            other = ZZ.cross(ta).normalized()           # horizontal, perpendicular ao eixo de inclinacao
            u = ta
            v = (other * math.cos(math.radians(tilt)) + ZZ * math.sin(math.radians(tilt))).normalized()
        nrm = u.cross(v).normalized()
        PK.ring(mb, c, rr, u, v, w, h, "Metal_Gold", 0, 360, 56 if rr > 10 else 44)
        for k in range(nst):
            a = 2 * math.pi * (k + 0.5) / nst
            d = u * math.cos(a) + v * math.sin(a)
            tng = (-u * math.sin(a) + v * math.cos(a)).normalized()
            # enfeite centrado na faixa do anel: nao sai da casca radial do anel (os aneis giram um dentro do
            # outro e dentro da gaiola; folga radial >= 0,15 entre cascas)
            p = c + d * rr
            K.star(mb, p, tng, nrm, 5, 0.85, 0.36, 0.22, "Summon_Star_Glow", edge=0.12)
        ob = mb.finish()
        axis = (0.0, 0.0, 1.0) if spin == "z" else ((0.0, 0.0, -1.0) if spin == "-z" else tuple(round(x, 4) for x in nrm))
        ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
        ob["axis"] = [round(x, 4) for x in axis]
        ob["rpm"] = rpm
        ob["vfx"] = "anel da esfera armilar (gira no eixo 'axis' passando por 'pivot')"
        rings.append(ob)
    st = MB("VFX_SUM_Star", "12_VFX_HELPERS", random.Random(691), detail="hero")
    K.star(st, c, XU, ZZ, 5, 6.0, 2.55, 1.45, "Summon_Star_Glow", edge=0.9)
    sp = K.star_pts(5, 6.0, 2.55)
    for i in range(len(sp)):
        a, b = sp[i], sp[(i + 1) % len(sp)]
        st.beam(c + XU * a[0] + ZZ * a[1], c + XU * b[0] + ZZ * b[1], 1.1, 0.34, "Metal_Gold", 0.0)
    ob = st.finish()
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, 0.0, 1.0]
    ob["rpm"] = 5.0
    ob["vfx"] = "estrela dourada (Neon) girando devagar no eixo vertical"
    return c


def constellation(c):
    rng = random.Random(701)
    mb = MB("SUM_Constellation", "05_SUMMON", rng, detail="hero")
    # 3 cadeias em volta da esfera (esquerda, direita, fundo): (azimute graus em torno do eixo, raio, z relativo)
    chains = [
        [(118.0, 16.0, 7.6), (140.0, 18.6, 9.4), (160.0, 20.4, 5.8), (182.0, 20.0, 8.2), (204.0, 18.2, 3.6),
         (222.0, 15.8, 6.2)],
        [(62.0, 16.0, 7.2), (40.0, 18.8, 9.8), (20.0, 20.6, 5.2), (-2.0, 20.0, 8.6), (-24.0, 18.0, 3.2),
         (-42.0, 15.8, 6.6)],
        [(246.0, 17.4, 10.2), (264.0, 19.4, 6.8), (282.0, 18.4, 10.6), (300.0, 16.6, 7.4)],
    ]
    sizes = [2.3, 1.4, 2.0, 1.2, 1.8, 1.3]
    for ch in chains:
        pts = []
        for k, (az, r, dz) in enumerate(ch):
            a = math.radians(az)
            d = XU * math.cos(a) + YV * math.sin(a)
            p = c + d * r + ZZ * dz
            pts.append(p)
            K.star3d(mb, p, sizes[k % len(sizes)], "Crystal_SumStar_Glow", rot=a + YAW)
        for a, b in zip(pts, pts[1:]):
            dd = (b - a)
            e = dd.normalized()
            mb.beam(a + e * 1.0, b - e * 1.0, 0.26, 0.26, "Summon_Blue_Glow", 0.0)
            for t in (0.33, 0.66):
                q = a + dd * t + Vector((0, 0, rng.uniform(-0.3, 0.3)))
                PK.octa(mb, q, 0.34, 0.45, "Crystal_SumStar_Glow", rot=rng.uniform(0, 1.5))
    mb.finish()


# ------------------------------------------------------------------ colisao da torre
def tower_collision():
    pu, pv0, pv1 = PLINTH
    for s in (-1, 1):
        lcol2(s * CORR, pv0, -0.6, s * pu, pv1, PLZ)                       # soco (lados)
        lcol2(s * CORR, POD[1], PLZ, s * (POD[0] + 0.35), POD[2] + 0.35, POD_TOP)   # podio (lados)
    lcol2(-CORR, pv0, -0.6, CORR, LAND_V[0], POD_TOP)                     # soco + podio (fundo)
    lcol2(-CORR, LAND_V[0], -0.2, CORR, LAND_V[1], LAND_Z)               # patamar do portal
    hw, v0, v1, z0, z1 = L1
    lcol2(-hw - 1.3, v0 - 1.3, POD_TOP, hw + 1.3, v1 + 0.1, L3[4])       # corpo (L1 + L2 + coroa)
    for s in (-1, 1):
        lcol2(s * PORT_HW, v1, POD_TOP, s * (hw + 1.3), 4.3, 18.0)        # ombreiras do portal
        lcol2(s * (hw - 0.1), MAST_V - 1.1, POD_TOP, s * (MAST_U + 1.0), MAST_V + 1.1, 31.0)   # asa + mastro
        lcol((3.3, 3.3, 3.2), s * 8.6, 5.8, POD_TOP + 1.6)                  # pedestal do cristal (base)
        lcol((1.5, 1.5, 4.6), s * (CORR + 0.65), ST_FOOT - 0.8, 2.3)        # poste do pe da escada
        for v in (6.0, -9.8):
            lcol((3.3, 3.3, 5.1), s * 12.5, v, PLZ + 2.5)                   # pilar da lanterna de canto


# ------------------------------------------------------------------ build
def build():
    plaza_floor()
    plaza_rail()
    stone = MB("SUM_Tower_Stone", "05_SUMMON", random.Random(620), detail="near")
    gold = MB("SUM_Tower_Gold", "05_SUMMON", random.Random(622), detail="near")
    glow = MB("SUM_Tower_Glow", "05_SUMMON", random.Random(623), detail="hero")
    tower_stone(stone, gold, glow)
    cr = tower_details(stone, gold, glow)
    lamp_c = masts_and_lanterns(stone, gold, glow)
    crystals_big(cr)
    c = sphere(gold, glow)
    constellation(c)
    stone.finish()
    gold.finish()
    glow.finish()
    tower_collision()
    # luzes (4): estrela (quente), portal (fria), 2 lanternas de canto da frente (quentes)
    light("L_Summon_Star", "POINT", c, 9000, (1.0, 0.74, 0.34), 3.0)
    light("L_Summon_Portal", "POINT", P(0.0, 4.6, 9.0), 1800, (0.36, 0.52, 1.0), 1.2)
    for n, p in zip(("L_Summon_Lantern_L", "L_Summon_Lantern_R"), lamp_c[:2]):
        light(n, "POINT", p, 320, (1.0, 0.62, 0.28), 0.4)
    # marcadores de gameplay
    mk("SUMMON_Main", P(0.0, 0.0, 0.0), (0, 0, YAW), 4.0, "ARROWS",
       props={"face_deg": L.SUMMON_FACE_DEG, "star_pivot": [round(c.x, 3), round(c.y, 3), round(c.z, 3)],
              "height": round(ZS + CAGE_R + 4.9, 1), "free_zone_v": list(FREE_V), "free_zone_w": 14.0,
              "note": "raiz da torre de invocacao (+Y local = frente); zona livre na frente: v local em free_zone_v"})
    mk("SUMMON_Interact", P(0.0, ST_FOOT + 0.3, 0.12), (0, 0, YAW), 2.0, "SPHERE",
       props={"radius": 8.0, "note": "pe da escadaria frontal (ProximityPrompt da invocacao)"})
    mk("SUMMON_PlayerPosition", P(0.0, 18.0, 0.12), (0, 0, YAW + math.pi), 2.0, "ARROWS",
       props={"note": "jogador na praca, olhando para a torre (camera da animacao atras dele)"})
