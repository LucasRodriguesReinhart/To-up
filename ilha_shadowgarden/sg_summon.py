# sg_summon - ZONA SUMMON da Ilha 3 (Shadow Garden). Substitui sg_blockout.summon. Prefixo SG_Sum_, colecao 06_SUMMON,
# pecas moveis VFX_SGSUM_* em 12_VFX_HELPERS, luzes L_SGSum_*.
# REGRA DA MISSAO: a maquina e a MESMA torre de invocacao das Ilhas 1 e 2 (familia aprovada). O codigo da torre e o da
# Ilha 1 (ilha_naruto/il_summon.py), carregado com a planta DESTA ilha (il_layout.SUMMON_TOWER/FACE/T1/SUMMON_C/R
# trocados so durante o import e restaurados logo depois, como fez a Ilha 2 em db_summon.tower_mod). Reaproveitado sem
# redesenho: corpo L1 com o NICHO do portal + frontispicio + frontao, cornijas, corpo L2 com a janela-estrela, coroa
# L3 com pinaculos, contrafortes, mastros com estandartes e lanternas penduradas, pedestais internos, patamar do portal
# e a esfera armilar (gaiola + 3 aneis moveis + estrela de cristal). As funcoes que misturam base e torre
# (tower_stone, masts_and_lanterns, tower_collision) foram PORTADAS aqui so com a parte da torre; tower_details,
# in_pedestal e sphere sao chamadas direto.
# O QUE MUDOU (so base, materiais, luz e VFX):
#   - materiais: troca por apelido SO durante a torre (fm_lib.MAT_ALIAS): pedra lilas -> pedra fria SG (castelo /
#     bloco / escura: o xadrez claro/escuro da Ilha 1 vira alternancia sutil), ouro -> prata, azul royal -> navy, portal azul -> indigo (SG_SumPortal_Glow), estrela
#     ambar/amarela -> violeta + lilas (SG_Violet_Glow / SG_SumStar_Glow), bordas azuis -> violeta;
#   - base: o soco de 40 x 20 com 4 pedestais de lanterna japonesa NAO cabe na plataforma de raio 22 -> podio proprio
#     (laterais retas + fundo em arco concentrico a plataforma, que vira bastiao na borda oeste), soco claro, arcada cega
#     ogival com estrelas de prata na frente; escada da torre (mesma medida: 5 x 0,8, 7,6 de largura) sem as bordas de
#     brilho, com banzos lisos; pedestais internos com lanterna gotica de ferro (as 2 luzes quentes baixas);
#   - praca: o piso e do terreno (topo 40,2); aqui so o desenho radial discreto (+0,05) centrado no ponto do jogador
#     (SUMMON_PlayerPosition) + faixa de borda; balaustrada gotica baixa na borda (aberta na escada, x -120,5, largura
#     12), ponte curta com arco ogival e parapeitos iguais, escada da planta (sg_lib.plan_stair) com banzos lisos;
#   - fora: constelacao das asas, cristais (liam como minerio), lanternas japonesas, postes do pe da escada.
# Colisao propria: podio/soco, corpo da torre, patamar + escada da torre, pedestais. Piso, escada da planta, ponte e
# guardas: sg_col (congelado). Marcadores SUMMON_*: sg_core (congelado; o jogador fica em v 16 no piso, o gabinete
# invisivel do gacha em v 7).
import math, random, sys, importlib
from contextlib import contextmanager
from mathutils import Vector
import bpy
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, Frame
import sg_layout as L
import fm_lib
import fm_parts as FP
import fm_portal_kit as PK

COL = "06_SUMMON"
CX, CY = L.SUMMON_C
R = L.SUMMON_R
Z = L.SUM
P1 = L.P1

# ------------------------------------------------------------------ materiais novos (2 de 4)
_S = fm_lib.S
fm_lib.MATS.setdefault("SG_SumPortal_Glow", (_S(78, 58, 206), 0.3, 0.0, 1.3, _S(92, 66, 240), 0.0))   # nicho/janelas
fm_lib.MATS.setdefault("SG_SumStar_Glow", (_S(228, 208, 255), 0.2, 0.0, 2.6, _S(212, 186, 255), 0.0))  # estrela lilas
for _k in ("SG_SumPortal_Glow", "SG_SumStar_Glow"):
    fm_lib.RBX_CAL.setdefault(_k, (None, [int(c) for c in fm_lib.to_srgb(fm_lib.MATS[_k][0])]))

# materiais da Ilha 1 -> paleta SMATS (apelido so durante a torre; os nomes da Ilha 1 nunca chegam ao export)
TOWER_ALIAS = {
    "Summon_Stone": "Stone_SG_Castle", "Stone_SumBlock": "Stone_SG_Block", "Summon_Stone_Dark": "Stone_SG_Floor",
    "Metal_Gold": "Metal_SG_Silver", "Cloth_Royal_Blue": "Cloth_SG_Navy", "Wood_Dark": "Wood_SG_Dark",
    "Crystal_SumPortal_Glow": "SG_SumPortal_Glow", "Crystal_SumStar_Glow": "SG_SumStar_Glow",
    "Summon_Blue_Glow": "SG_Violet_Glow", "Summon_Star_Glow": "SG_SumStar_Glow",
    "Crystal_SumAmber_Glow": "SG_Violet_Glow", "Crystal_SumYellow_Glow": "SG_SumStar_Glow",
    "Crystal_Blue": "SG_Violet_Glow",
}

# ------------------------------------------------------------------ referencial da torre (o mesmo do il_summon)
TX, TY = L.SUMMON_TOWER
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2
F = Frame(TX, TY, Z, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))
ZZ = Vector((0.0, 0.0, 1.0))
# medidas da torre da Ilha 1 (il_summon) usadas antes do import (rotas/cameras); build() confere que batem
ST_FOOT, LAND_Z, PV, CORR, POD_TOP, AX, ZS = 13.6, 4.0, -1.4, 5.0, 3.3, -3.0, 46.0
LAND_V1 = 5.6
C_V = math.hypot(CX - TX, CY - TY)          # centro da plataforma no referencial da torre: (0, 7,5)
PAD_V = 16.0                                # SUMMON_PlayerPosition (sg_core)
INTER_V = 7.0                               # SUMMON_Interact (sg_core)

# ------------------------------------------------------------------ base (podio proprio)
POD_HW = 12.2          # meia largura do podio (inclui os mastros, u 10,4 +- 1)
POD_VF = 7.2           # frente do podio (a da Ilha 1)
POD_RB = 20.0          # fundo do podio: arco concentrico a plataforma
SOC_OFF = 0.9          # soco claro (0 .. 0,8) sai 0,9 do podio
SOC_RB = 20.8
PLZ = 0.8
IN_PED = (9.6, 5.6)    # pedestais internos (Ilha 1) com a lanterna gotica
RAIL_R = 21.2          # linha da balaustrada (a guarda invisivel do sg_col fica de 22 a 23)
GATE_A = 20.0          # abertura da escada: +-20 graus a partir de +X (meia largura 7,25 no raio da balaustrada)
BR_Y = 6.6             # parapeitos da ponte e banzos da escada (linha da guarda do sg_col)
WARM = (1.0, 0.64, 0.34)
VIOLET = (0.62, 0.44, 1.0)


def P(u, v, z=0.0):
    return F.p(u, v, z)


def to_local(x, y):
    d = Vector((x - TX, y - TY, 0.0))
    return d.dot(XU), d.dot(YV)


def _side_v(hw, rb):
    """v onde a lateral reta (|u| = hw) encontra o arco do fundo (raio rb em volta do centro da plataforma)"""
    return C_V - math.sqrt(rb * rb - hw * hw)


def in_base(x, y, pad=0.0):
    """ponto sobre a base da torre (soco/podio) ou sobre a escada da torre"""
    u, v = to_local(x, y)
    hw = POD_HW + SOC_OFF
    if abs(u) < hw + pad and v < POD_VF + SOC_OFF + pad and math.hypot(u, v - C_V) < SOC_RB + pad:
        return True
    return abs(u) < CORR + pad and v < ST_FOOT + pad


def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    # frente: da ponta da ponte, acima (a torre inteira, base ao remate da esfera ~62)
    "CAM_SGSum_Front": ((-78.0, -114.0, Z + 18.0), (TX, TY, Z + 28.0), 20),
    # tras (oeste, fora da ilha): bastiao do podio na borda + costas da torre
    "CAM_SGSum_Back": ((-236.0, -96.0, Z + 26.0), (TX, TY, Z + 24.0), 22),
    # lados
    "CAM_SGSum_North": ((-138.0, -38.0, Z + 22.0), (-146.0, -118.0, Z + 24.0), 22),
    "CAM_SGSum_South": ((-150.0, -198.0, Z + 22.0), (-146.0, -118.0, Z + 24.0), 22),
    # altura do jogador: na ponte olhando a subida e a torre; no pad (SUMMON_PlayerPosition) olhando o portal
    "CAM_SGSum_PlayerBridge": ((-102.0, -118.0, P1 + 5.2), (TX, TY, Z + 14.0), 22),
    "CAM_SGSum_PlayerPad": ((-131.5, -121.0, Z + 5.2), (TX, TY, Z + 10.0), 20),
    # altura do jogador na passagem lateral (norte) entre o podio e a balaustrada
    "CAM_SGSum_PlayerWalk": ((-127.0, -100.5, Z + 5.2), (-158.0, -108.0, Z + 3.0), 20),
    # ponte vista de lado (arco ogival) a partir do vao ao norte, entre a ilha e a ilhota, baixa
    "CAM_SGSum_BridgeSide": ((-119.0, -95.0, P1 - 2.0), (-106.0, -118.0, P1 - 4.0), 22),
    # esfera armilar + estrela de perto
    "CAM_SGSum_Sphere": ((-112.0, -128.0, Z + 44.0), (TX - 3.0, TY, Z + 46.0), 30),
}

# ------------------------------------------------------------------ rotas e sondas proprias (sg_qa)
_TOP = L.stair_top("Summon")
_PAD = tuple(P(0.0, PAD_V).xy)
EXTRA_ROUTES = {
    # pad do jogador -> sobe a escada da torre -> patamar diante do portal
    "PAD->PATAMAR": ([_PAD, tuple(P(0.0, ST_FOOT + 0.4).xy), tuple(P(0.0, ST_FOOT - 1.0).xy),
                      tuple(P(0.0, LAND_V1 + 0.6).xy), tuple(P(0.0, LAND_V1 - 1.0).xy), tuple(P(0.0, PV + 2.0).xy)], Z),
    # topo da escada -> volta pelo norte e pelo sul, entre o podio e a balaustrada, ate o canto do soco
    "ESCADA->LADO_NORTE": ([(_TOP[0] - 1.5, _TOP[1])] + [(CX + 18.0 * math.cos(math.radians(a)),
                                                          CY + 18.0 * math.sin(math.radians(a)))
                                                         for a in (20.0, 50.0, 80.0, 105.0, 128.0)], Z),
    "ESCADA->LADO_SUL": ([(_TOP[0] - 1.5, _TOP[1])] + [(CX + 18.0 * math.cos(math.radians(a)),
                                                        CY + 18.0 * math.sin(math.radians(a)))
                                                       for a in (-20.0, -50.0, -80.0, -105.0, -128.0)], Z),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ utilidades de geometria
def top_prism(mb, pts, z0, z1, m):
    """prisma sem a face de baixo (inlay/aro assentado no piso: o fundo nunca aparece)"""
    pts = SL.ccw(pts)
    vb = [mb.bm.verts.new((p[0], p[1], z0)) for p in pts]
    vt = [mb.bm.verts.new((p[0], p[1], z1)) for p in pts]
    n = len(pts)
    mb.bm.faces.new(vt)
    for i in range(n):
        j = (i + 1) % n
        mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m, None, 0, 1)


def side_prism(mb, Fr, prof, y0, y1, m):
    """poligono CONVEXO (x, z) no plano vertical do referencial Fr, extrudado na lateral de y0 a y1"""
    bm = mb.bm
    a = [bm.verts.new(Fr.p(x, y0, z)) for x, z in prof]
    b = [bm.verts.new(Fr.p(x, y1, z)) for x, z in prof]
    n = len(prof)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


def arc_piece(cx, cy, r0, r1, a0, a1, step=4.0):
    n = max(1, int(math.ceil(abs(a1 - a0) / step)))
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
              cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
              cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return outer + inner


def local_poly(pts_uv):
    return [tuple(P(u, v).xy) for u, v in pts_uv]


def base_outline(hw, vf, rb, step=6.0):
    """contorno (u, v) do podio/soco: frente reta em vf, laterais retas em +-hw, fundo em arco de raio rb em volta
    do centro da plataforma (0, C_V). Devolve (lateral_direita, arco, lateral_esquerda) para montar pecas convexas"""
    vs = _side_v(hw, rb)
    a0 = math.degrees(math.atan2(vs - C_V, hw))
    a1 = -180.0 - a0
    n = max(2, int(math.ceil(abs(a1 - a0) / step)))
    arc = [(rb * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C_V + rb * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    return vs, arc


# ------------------------------------------------------------------ torre (codigo da Ilha 1)
_TOWER = None


def tower_mod():
    """importa il_summon com a planta desta ilha (valores do il_layout trocados so durante o import)"""
    global _TOWER
    if _TOWER is not None:
        return _TOWER
    import il_layout as NL
    want = {"SUMMON_TOWER": (TX, TY), "SUMMON_FACE_DEG": L.SUMMON_FACE_DEG, "T1": Z, "SUMMON_C": (CX, CY),
            "SUMMON_R": R}
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
    for a, b in ((T.ST_FOOT, ST_FOOT), (T.LAND_Z, LAND_Z), (T.PV, PV), (T.CORR, CORR), (T.POD_TOP, POD_TOP),
                 (T.AX, AX), (T.ZS, ZS), (T.LAND_V[1], LAND_V1), (T.IN_PED[0], IN_PED[0]), (T.IN_PED[1], IN_PED[1])):
        assert abs(a - b) < 1e-6, (a, b)
    _TOWER = T
    return T


@contextmanager
def tower_palette():
    """materiais da Ilha 1 -> SMATS so enquanto a torre e montada (o MB.finish aplica fm_lib.alias)"""
    saved = dict(fm_lib.MAT_ALIAS)
    for k, v in TOWER_ALIAS.items():
        fm_lib.MAT_ALIAS[k] = v
        fam = fm_lib.FAMILIES.get(k)
        if fam:
            for n, _ in fam[1]:
                fm_lib.MAT_ALIAS[n] = v
    try:
        yield
    finally:
        fm_lib.MAT_ALIAS.clear()
        fm_lib.MAT_ALIAS.update(saved)


def tower_body(T, stone, gold, glow):
    """PORTADO de il_summon.tower_stone (so a torre: corpo L1 com o nicho, frontispicio, frontao, cornijas, L2 com a
    janela-estrela, coroa L3). O soco, o podio de 32 de largura e a escada com bordas de brilho da Ilha 1 ficam de fora
    (a base desta ilha e a de base())."""
    rng = random.Random(621)
    lbox, lbox2, face_skin, larch, _buttress = T.lbox, T.lbox2, T.face_skin, T.larch, T._buttress
    PORT_HW, PORT_SPRING, NICHE_TOP, MAST_V = T.PORT_HW, T.PORT_SPRING, T.NICHE_TOP, T.MAST_V
    L1_SWIN, L1_BWIN, BUT_V = T.L1_SWIN, T.L1_BWIN, T.BUT_V
    # --- corpo L1: nucleo com o NICHO do portal (fundo em PV) + contrafortes de canto + pele de alvenaria
    hw, v0, v1, z0, z1 = T.L1
    nw = PORT_HW + 0.8
    lbox2(stone, -hw, v0, z0, hw, PV, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        lbox2(stone, s * nw, PV, z0, s * hw, v1, z1, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -nw, PV, NICHE_TOP, nw, v1, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Summon_Stone" if k % 2 == 0 else "Stone_SumBlock"
            lbox(stone, (0.8, v1 - PV - 0.1, zz1 - zz0 - 0.08), s * (PORT_HW + 0.4), (PV + v1) / 2, (zz0 + zz1) / 2,
                 m, 0.0)
    larch(stone, 0.0, (PV + v1) / 2, 2 * PORT_HW, PORT_SPRING, PORT_HW, v1 - PV - 0.1, m="Summon_Stone",
          key_m="Stone_SumBlock", n=9, band=2.4, keystone=False, seed=1)
    s_side = (v1 - 0.6) - MAST_V
    side_op = (s_side - 1.75, s_side + 1.75, L1_SWIN[0] - 0.2, L1_SWIN[1] + L1_SWIN[2] + 0.5, L1_SWIN[2] + 0.45)
    for s in (-1, 1):
        face_skin(stone, (s * (hw + 0.25), v1 - 0.6), (s * (hw + 0.25), v0 + 0.6), z0, z1, rng, course=2.1,
                  blk=(2.6, 4.2), thick=0.8, openings=[side_op])
        for dv in (-1, 1):
            lbox(stone, (0.9, 0.7, L1_SWIN[1] - L1_SWIN[0]), s * (hw + 0.5), MAST_V + dv * (L1_SWIN[2] + 0.35),
                 (L1_SWIN[0] + L1_SWIN[1]) / 2, "Summon_Stone", 0.0)
    back_op = (hw - 0.6 - 2.1, hw - 0.6 + 2.1, L1_BWIN[0] - 0.2, L1_BWIN[1] + L1_BWIN[2] + 0.6, L1_BWIN[2] + 0.5)
    face_skin(stone, (hw - 0.6, v0 - 0.25), (-hw + 0.6, v0 - 0.25), z0, z1, rng, course=2.1, blk=(2.6, 4.2),
              thick=0.8, openings=[back_op])
    for s in (-1, 1):
        lbox(stone, (0.75, 0.9, L1_BWIN[1] - L1_BWIN[0]), s * (L1_BWIN[2] + 0.38), v0 - 0.5,
             (L1_BWIN[0] + L1_BWIN[1]) / 2, "Summon_Stone", 0.0)
    for su in (-1, 1):
        for vv in (v0, BUT_V):
            _buttress(stone, gold, su * hw, vv, z0, 22.2, 2.5, rng, spire=2.8,
                      edges=((-1, 1), (1, 1)) if vv > 0 else ((-1, -1), (1, -1)))
    face_skin(stone, (-hw + 0.9, v1 + 0.35), (hw - 0.9, v1 + 0.35), 16.8, z1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, quoins=(False, False), base_dark=False)
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Stone_SumBlock" if k % 2 == 0 else "Summon_Stone"
            w = 2.3 if k % 2 == 0 else 2.0
            lbox(stone, (w, 2.9, zz1 - zz0 - 0.08), s * (PORT_HW + 1.1), 2.55, (zz0 + zz1) / 2, m, 0.14)
        lbox2(stone, s * (PORT_HW + 0.35), v1, PORT_SPRING, s * 6.3, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -PORT_HW - 0.4, v1, PORT_SPRING + PORT_HW + 0.2, PORT_HW + 0.4, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    larch(stone, 0.0, 2.6, 2 * PORT_HW, PORT_SPRING, PORT_HW, 2.9, n=9, band=1.5, keystone=True, seed=2)
    apex = (0.0, 22.6)
    for s in (-1, 1):
        a = P(s * 6.9, 3.45, 17.6)
        b = P(apex[0], 3.45, apex[1])
        stone.beam(a, b, 1.9, 1.2, "Stone_SumBlock", 0.0)
        ga = P(s * 7.2, 3.55, 18.45)
        gb = P(0.0, 3.55, apex[1] + 0.85)
        gold.beam(ga, gb, 2.2, 0.6, "Metal_Gold", 0.0)
    tri = [(-6.3, 17.6), (6.3, 17.6), (0.0, apex[1] - 0.2)]
    PK.plate(stone, tri, P(0.0, 3.0, 0.0), XU, ZZ, 1.0, "Summon_Stone_Dark")
    # --- cornija 1
    lbox2(stone, -hw - 1.0, v0 - 1.0, z1, hw + 1.0, 2.4, z1 + 0.6, "Summon_Stone_Dark", 0.0)
    lbox2(gold, -hw - 1.3, v0 - 1.3, z1 + 0.6, hw + 1.3, 2.6, z1 + 1.3, "Metal_Gold", 0.0)
    # --- corpo L2
    hw2, w0, w1, y0, y1 = T.L2
    lbox2(stone, -hw2, w0, y0, hw2, w1, y1, "Summon_Stone_Dark", 0.0)
    wcs = hw2 - 0.2
    win_front = (wcs - 3.5, wcs + 3.5, y0 + 1.0, y0 + 6.8 + 3.5, 3.5)
    face_skin(stone, (-hw2 + 0.2, w1 + 0.35), (hw2 - 0.2, w1 + 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    face_skin(stone, (hw2 - 0.2, w0 - 0.35), (-hw2 + 0.2, w0 - 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    ln_side = (w1 - 0.6) - (w0 + 0.6)
    for s in (-1, 1):
        a_uv = (s * (hw2 + 0.35), w1 - 0.6) if s > 0 else (s * (hw2 + 0.35), w0 + 0.6)
        b_uv = (s * (hw2 + 0.35), w0 + 0.6) if s > 0 else (s * (hw2 + 0.35), w1 - 0.6)
        side_win = (ln_side / 2 - 2.3, ln_side / 2 + 2.3, y0 + 2.4, y0 + 8.6, 2.3)
        face_skin(stone, a_uv, b_uv, y0, y1, rng, course=1.8, blk=(2.2, 3.6), thick=0.8, openings=[side_win])
    for su in (-1, 1):
        for vv in (w0, w1):
            _buttress(stone, gold, su * hw2, vv, y0, y1 + 1.4, 1.9, rng, spire=3.3, course=1.6)
    larch(stone, 0.0, w1 + 0.4, 5.2, y0 + 6.8, 2.6, 1.3, n=7, band=0.9, keystone=True, seed=3)
    for s in (-1, 1):
        lbox2(stone, s * 2.6, w1 - 0.1, y0 + 1.4, s * 3.5, w1 + 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lbox2(gold, -3.8, w1 - 0.1, y0 + 0.85, 3.8, w1 + 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    # --- cornija 2
    lbox2(stone, -hw2 - 0.9, w0 - 0.9, y1, hw2 + 0.9, w1 + 0.9, y1 + 0.5, "Summon_Stone_Dark", 0.0)
    lbox2(gold, -hw2 - 1.2, w0 - 1.2, y1 + 0.5, hw2 + 1.2, w1 + 1.2, y1 + 1.15, "Metal_Gold", 0.0)
    # --- coroa L3 + pinaculos
    h3, c0, c1, q0, q1 = T.L3
    lbox2(stone, -h3, c0, q0, h3, c1, q1, "Summon_Stone_Dark", 0.0)
    for (a_uv, b_uv) in (((-h3 - 0.3, c1 + 0.3), (h3 + 0.3, c1 + 0.3)), ((h3 + 0.3, c0 - 0.3), (-h3 - 0.3, c0 - 0.3)),
                         ((h3 + 0.3, c1 + 0.3), (h3 + 0.3, c0 - 0.3)), ((-h3 - 0.3, c0 - 0.3), (-h3 - 0.3, c1 + 0.3))):
        face_skin(stone, a_uv, b_uv, q0, q1 - 0.25, rng, course=1.9, blk=(2.0, 3.2), thick=0.7, quoins=(False, False))
    lbox2(gold, -h3 - 0.8, c0 - 0.8, q1 - 0.25, h3 + 0.8, c1 + 0.8, q1 + 0.35, "Metal_Gold", 0.0)
    for su in (-1, 1):
        for vv in (c0, c1):
            _buttress(stone, gold, su * h3, vv, q0, q1 + 0.9, 1.3, rng, spire=1.8, course=1.4)


def masts(T, stone, gold, glow):
    """PORTADO de il_summon.masts_and_lanterns (so os mastros com estandartes e as lanternas penduradas; os 4
    pedestais de lanterna japonesa e os postes do pe da escada da Ilha 1 nao entram)"""
    K = T.K
    rng = random.Random(651)
    bn = MB("SG_Sum_Tower_Banners", COL, rng, detail="near")
    hw, v0, v1, z0, z1 = T.L1
    hw2, w0, w1, y0, y1 = T.L2
    MAST_U, MAST_V, BAN_TH = T.MAST_U, T.MAST_V, T.BAN_TH
    z_pole = 29.8
    for s in (-1, 1):
        u = s * MAST_U
        T._buttress(stone, gold, u, MAST_V, POD_TOP, 31.0, 2.0, rng, spire=3.0, course=2.0, edges=((s, 1), (s, -1)))
        for zc in (13.0, 22.5):
            T.lbox(gold, (2.4, 2.4, 0.5), u, MAST_V, zc, "Metal_Gold", 0.0)
        T.lbox2(stone, s * (hw - 0.1), MAST_V - 0.95, POD_TOP, s * (MAST_U - 0.9), MAST_V + 0.95, 12.0,
                "Summon_Stone", 0.0)
        T.lbox2(gold, s * (hw - 0.1), MAST_V - 1.15, 12.0, s * (MAST_U - 0.7), MAST_V + 1.15, 12.5, "Metal_Gold", 0.0)
        T.gold_star4(gold, s * ((hw + MAST_U) / 2 - 0.4), MAST_V + 0.95, 8.0, 0.75, "v+")
        T.gold_star4(gold, s * ((hw + MAST_U) / 2 - 0.4), MAST_V - 0.95, 8.0, 0.75, "v-")
        T.lbox2(stone, s * (hw + 0.8), MAST_V - 0.8, z1, s * (MAST_U - 0.9), MAST_V + 0.8, z1 + 0.9,
                "Summon_Stone_Dark", 0.0)
        mw = P(u, MAST_V, 0.0)
        Fb = Frame(mw.x, mw.y, Z, YAW + s * BAN_TH)
        ub = Vector(Fb.p(1, 0, 0)) - Vector(Fb.p(0, 0, 0))
        stub = (MAST_U - (hw2 + 0.35)) / math.cos(BAN_TH)
        a = Fb.p(-s * stub, 0.0, z_pole)
        b = Fb.p(s * 7.0, 0.0, z_pole)
        bn.rod(a, b, 0.3, "Wood_Dark", 8)
        K.spike(gold, b, b + ub * (s * 1.5), 0.45, "Metal_Gold", 4)
        gold.ico(0.5, Fb.p(s * 6.8, 0.0, z_pole), "Metal_Gold", 1)
        for uu in (-s * (stub - 0.25), s * 1.3, s * 5.9):
            gold.box((0.4, 0.8, 0.8), Fb.p(uu, 0.0, z_pole), Fb.r(), "Metal_Gold", 0.0)
        K.banner(bn, gold, bn, Fb, 1.5 if s > 0 else -5.7, 5.7 if s > 0 else -1.5, 0.0, z_pole - 0.5, 12.6, tip=1.6)
        K.hang_lantern(stone, glow, gold, Fb.p(-s * 2.4, 0.0, z_pole - 0.3), 1.0, drop=0.9)
    return bn.finish()


def gothic_lantern(stone, glow, silver, base):
    """lanterna gotica de ferro (no lugar da gema/cristal do pedestal interno): pe, camara quente entre montantes,
    chapeu em agulha de ardosia e remate de prata. Devolve o centro da luz."""
    b = Vector(base)
    stone.box((1.7, 1.7, 0.3), b + ZZ * 0.15, (0, 0, YAW), "Metal_SG_Iron", 0.0)
    zc = 0.3 + 1.0
    glow.box((0.9, 0.9, 1.6), b + ZZ * zc, (0, 0, YAW), "Lantern_Glow", 0.0)
    for k in range(4):
        a = YAW + math.pi / 4 + k * math.pi / 2
        d = Vector((math.cos(a), math.sin(a), 0.0))
        stone.box((0.28, 0.28, 2.0), b + d * 0.78 + ZZ * zc, (0, 0, YAW), "Metal_SG_Iron", 0.0)
    stone.box((1.8, 1.8, 0.3), b + ZZ * 2.45, (0, 0, YAW), "Metal_SG_Iron", 0.0)
    SL.spire(stone, (b.x, b.y), 1.25, b.z + 2.6, 2.2, "Roof_SG_Slate", n=4)
    silver.ico(0.24, b + ZZ * 4.95, "Metal_SG_Silver", 1)
    return b + ZZ * zc


def tower_collision(T):
    """PORTADO de il_summon.tower_collision (so a torre; a base e de base_collision)"""
    A = "SG_SumTower"

    def lc2(u0, v0, z0, u1, v1, z1):
        c = P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
        col_box(A, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), c, (0, 0, YAW))
    hw, v0, v1, z0, z1 = T.L1
    lc2(-hw - 1.3, v0 - 1.3, POD_TOP, hw + 1.3, PV, T.L3[4])                          # corpo atras do plano do portal
    lc2(-hw - 1.3, PV, T.PORT_SPRING + T.PORT_HW, hw + 1.3, v1 + 0.1, T.L3[4])        # sobre o nicho
    lc2(-T.PORT_HW, v1 + 0.1, T.PORT_SPRING + T.PORT_HW, T.PORT_HW, 4.3, 18.2)        # timpano
    for s in (-1, 1):
        lc2(s * T.PORT_HW, PV, POD_TOP, s * (hw + 1.3), 4.3, 18.2)                    # paredes do nicho + ombreiras
        lc2(s * (hw - 0.1), T.MAST_V - 1.1, POD_TOP, s * (T.MAST_U + 1.0), T.MAST_V + 1.1, 31.0)   # asa + mastro
        ih = T.IN_PED[3] + 0.5 + 5.0
        lc2(s * IN_PED[0] - 1.7, IN_PED[1] - 1.7, POD_TOP, s * IN_PED[0] + 1.7, IN_PED[1] + 1.7, POD_TOP + ih)
    lc2(-CORR, PV, -0.2, CORR, LAND_V1, LAND_Z)                                       # patamar do portal


def build_tower():
    T = tower_mod()
    before = {o.name for o in bpy.data.objects}
    stone = MB("SG_Sum_Tower_Stone", COL, random.Random(620), detail="near")
    gold = MB("SG_Sum_Tower_Silver", COL, random.Random(622), detail="near")
    glow = MB("SG_Sum_Tower_Glow", COL, random.Random(623), detail="hero")
    with tower_palette():
        tower_body(T, stone, gold, glow)
        cr = T.tower_details(stone, gold, glow)
        cr.bm.free()                              # cristais da boca do nicho: fora (liam como minerio)
        masts(T, stone, gold, glow)
        lamp_c = []
        for s in (-1, 1):
            zb = T.in_pedestal(stone, gold, s * IN_PED[0], IN_PED[1])
            lamp_c.append(gothic_lantern(stone, glow, gold, P(s * IN_PED[0], IN_PED[1], zb)))
        c = T.sphere(gold, glow)
        stone.finish()
        gold.finish()
        glow.finish()
    tower_collision(T)
    # renomeia o que o codigo da Ilha 1 criou: SUM_* -> SG_Sum_*, VFX_SUM_* -> VFX_SGSUM_*; colecao 05 -> 06
    dst = fm_lib.coll(COL)
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_SGSUM_" + n[len("VFX_SUM_"):]
        elif n.startswith("SUM_"):
            ob.name = "SG_Sum_" + n[len("SUM_"):]
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
    for ob in bpy.data.objects:
        if ob.name.startswith("VFX_SGSUM_"):
            ob["vfx_zone"] = "summon"
    return T, c, lamp_c


# ------------------------------------------------------------------ base: soco + podio (bastiao no fundo)
def base(bm_stone, bm_trim, T):
    K = T.K
    rng = random.Random(7303)
    # --- soco claro (0 .. 0,8): laterais + faixa da frente dos 2 lados da escada + arco do fundo
    hw_s, vf_s = POD_HW + SOC_OFF, POD_VF + SOC_OFF
    vs_s, arc_s = base_outline(hw_s, vf_s, SOC_RB)
    for s in (-1, 1):
        bm_stone.prism(SL.ccw(local_poly([(s * CORR, vs_s), (s * hw_s, vs_s), (s * hw_s, vf_s), (s * CORR, vf_s)])),
                       -0.6 + Z, PLZ + Z, "Stone_SG_Block")
    bm_stone.prism(SL.ccw(local_poly([(-CORR, vs_s), (CORR, vs_s), (CORR, PV), (-CORR, PV)])), -0.6 + Z, PLZ + Z,
                   "Stone_SG_Block")
    bm_stone.prism(SL.ccw(local_poly(arc_s)), -0.6 + Z, PLZ + Z, "Stone_SG_Block")
    # --- podio (0,8 .. 3,3): laterais, meio (atras do patamar) e fundo em arco
    hw, vf = POD_HW, POD_VF
    vs, arc = base_outline(hw, vf, POD_RB)
    zc0, zc1 = Z + PLZ, Z + POD_TOP
    pieces = [[(s * CORR, vs), (s * hw, vs), (s * hw, vf), (s * CORR, vf)] for s in (-1, 1)]
    pieces.append([(-CORR, vs), (CORR, vs), (CORR, PV), (-CORR, PV)])
    pieces.append(arc)
    for pc in pieces:
        bm_stone.prism(SL.ccw(local_poly(pc)), zc0 - 0.1, zc1 - 0.4, "Stone_SG_Castle")
    # rodape (fiada de base mais escura, 0,25 para fora) e capa de cantaria clara (0,35 para fora) no contorno externo
    outer = [(CORR, vf), (hw, vf), (hw, vs)] + arc[1:-1] + [(-hw, vs), (-hw, vf), (-CORR, vf)]
    for i in range(len(outer) - 1):
        (ua, va), (ub, vb) = outer[i], outer[i + 1]
        a, b = P(ua, va), P(ub, vb)
        d = (b - a)
        ln = d.length
        if ln < 0.3:
            continue
        nrm = Vector((d.y, -d.x, 0.0)).normalized()      # para fora (contorno horario no referencial -> conferir)
        mid = (a + b) / 2
        # o lado de fora e o que se afasta do eixo da torre
        cen = P(0.0, 0.0)
        if (mid - cen).dot(nrm) < 0:
            nrm = -nrm
        ang = math.atan2(d.y, d.x)
        for (z0, z1, off, m) in ((zc0 - 0.1, zc0 + 0.55, 0.22, "Stone_SG_Floor"),
                                 (zc1 - 0.45, zc1, 0.35, "Stone_SG_Trim")):
            w = 0.9 + off
            c = mid + nrm * (off - w / 2 + 0.0)
            (bm_trim if m == "Stone_SG_Trim" else bm_stone).box((ln + (0.7 if m == "Stone_SG_Trim" else 0.45), w,
                                                                 z1 - z0), (c.x, c.y, (z0 + z1) / 2),
                                                                (0, 0, ang), m, 0.0)
    # tampo do podio (dentro da capa): ardosia escura
    for pc in pieces:
        top_prism(bm_stone, local_poly(pc), zc1 - 0.45, zc1 - 0.02, "Stone_SG_Floor")
    # pilastras (contrafortes baixos) no contorno: frente e laterais a cada ~4, fundo a cada 16 graus
    pil = []
    for s in (-1, 1):
        for u in (CORR + 0.6, 8.0, hw - 0.5):
            pil.append((s * u, vf, "v+"))
        v = vf - 3.6
        while v > vs + 1.0:
            pil.append((s * hw, v, "u+" if s > 0 else "u-"))
            v -= 4.0
    a0 = math.degrees(math.atan2(vs - C_V, hw))
    a1 = -180.0 - a0
    nk = max(2, int(abs(a1 - a0) / 16.0))
    for k in range(nk + 1):
        a = math.radians(a0 + (a1 - a0) * k / nk)
        pil.append((POD_RB * math.cos(a), C_V + POD_RB * math.sin(a), ("arc", a)))
    for u, v, face in pil:
        if isinstance(face, tuple):
            a = face[1]
            nu, nv = math.cos(a), math.sin(a)
        else:
            nu, nv = {"v+": (0.0, 1.0), "u+": (1.0, 0.0), "u-": (-1.0, 0.0)}[face]
        pu, pv = u + nu * 0.1, v + nv * 0.1
        rz = YAW + math.atan2(nv, nu)
        bm_stone.box((1.0, 1.0, POD_TOP - PLZ - 0.9), P(pu, pv, PLZ + 0.55 + (POD_TOP - PLZ - 0.9) / 2), (0, 0, rz),
                     "Stone_SG_Block", 0.0)
    # arcada cega ogival na frente do podio (2 paineis de cada lado da escada) + estrela de prata de 4 pontas
    for s in (-1, 1):
        for uc in ((CORR + 0.6 + 8.0) / 2, (8.0 + hw - 0.5) / 2):
            w = 1.0
            pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.45)]
            for i in range(1, 5):
                t = i / 5.0
                aa = math.radians(60.0 * t)
                pts.append((w / 2 - w * (1 - math.cos(aa)), 0.45 + w * math.sin(aa)))
            pts.append((0.0, 0.45 + w * math.sin(math.radians(60.0))))
            for i in range(4, 0, -1):
                t = i / 5.0
                aa = math.radians(60.0 * t)
                pts.append((-(w / 2 - w * (1 - math.cos(aa))), 0.45 + w * math.sin(aa)))
            pts.append((-w / 2, 0.45))
            PK.plate(bm_stone, pts, P(s * uc, vf + 0.06, PLZ + 0.62), XU, ZZ, 0.16, "Stone_SG_Floor")
            K.star(bm_trim, P(s * uc, vf + 0.2, PLZ + 1.25), XU, ZZ, 4, 0.42, 0.13, 0.18, "Metal_SG_Silver")


def base_collision():
    A = "SG_SumPodium"

    def lc2(u0, v0, z0, u1, v1, z1):
        c = P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
        col_box(A, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), c, (0, 0, YAW))
    hw, vf = POD_HW, POD_VF
    vs = _side_v(hw, POD_RB)
    for s in (-1, 1):
        lc2(s * CORR, vs, -0.6, s * (hw + 0.35), vf + 0.35, POD_TOP)             # podio (lados)
    lc2(-CORR, vs, -0.6, CORR, PV, POD_TOP)                                      # podio (meio, atras do patamar)
    # fundo em arco: 2 caixas dentro do arco
    for uu in (9.0, 5.0):
        vb = C_V - math.sqrt(POD_RB ** 2 - uu ** 2)
        lc2(-uu, vb + 0.1, -0.6, uu, vs if uu == 9.0 else C_V - math.sqrt(POD_RB ** 2 - 81.0) + 0.1, POD_TOP)
    # soco (degrau de 0,8 em volta do podio: frente e lados)
    hs, vfs = hw + SOC_OFF, vf + SOC_OFF
    vss = _side_v(hs, SOC_RB)
    for s in (-1, 1):
        lc2(s * (hw + 0.35), vss, -0.6, s * hs, vfs, PLZ)
        lc2(s * CORR, vf + 0.35, -0.6, s * (hw + 0.35), vfs, PLZ)


# ------------------------------------------------------------------ escada da torre (medidas da Ilha 1, sem brilho)
def tower_stair(stair):
    base = P(0.0, ST_FOOT, 0.0)
    ang = FACE + math.pi
    rise, tread, n, width = 0.8, 1.6, 5, 7.6
    FP.stairs(stair, "SG_SumStair", (base.x, base.y, base.z), ang, width, n, rise=rise, tread=tread,
              m="Stone_Paving_SG", side_m="Stone_SG_Block", stringers=False, col=True)
    Fs = Frame(base.x, base.y, base.z, ang)
    k = rise / tread
    # guardas invisiveis dos banzos (as mesmas do fm_parts.stairs com banzo)
    H = 4.0
    Tt = H + 1.5
    off = k * (tread * k / 2 + H) / (1 + k * k)
    for s in (-1, 1):
        y = s * (width / 2 + 0.6)
        xa, xb = -off, tread * n - off
        SL.col_ramp("SG_SumStair", Fs.p(xa, y, (xa + tread / 2) * k + H), Fs.p(xb, y, (xb + tread / 2) * k + H),
                    1.2, thick=Tt)
    # banzos lisos (sobem ate o patamar e encostam no podio) + capa de cantaria
    x_end = tread * n                                # ate a borda do patamar (v 5,6)
    zt = rise * n
    for s in (-1, 1):
        y0, y1 = s * (width / 2 + 0.05), s * (width / 2 + 1.25)
        prof = [(-0.1, -0.6), (x_end, -0.6), (x_end, zt + 0.9), (tread * n - tread / 2, zt + 0.9),
                (-0.1, 1.05)]
        side_prism(stair, Fs, prof, min(y0, y1), max(y0, y1), "Stone_SG_Block")
        yc = s * (width / 2 + 0.65)
        a = Fs.p(-0.25, yc, 1.05 + 0.18)
        b = Fs.p(tread * n - tread / 2, yc, zt + 0.9 + 0.18)
        stair.beam(a, b, 1.45, 0.36, "Stone_SG_Trim", 0.0)
        stair.beam(b, Fs.p(x_end, yc, zt + 0.9 + 0.18), 1.45, 0.36, "Stone_SG_Trim", 0.0)
    # patamar do portal (o da Ilha 1: 7 de fundo, do fundo do nicho ate o topo da escada)
    for pc, z0, z1, m in (((-CORR + 0.05, PV, CORR - 0.05, LAND_V1), -0.4, LAND_Z - 0.3, "Stone_SG_Block"),
                          ((-CORR + 0.05, PV, CORR - 0.05, LAND_V1 + 0.1), LAND_Z - 0.3, LAND_Z, "Stone_Paving_SG")):
        u0, v0, u1, v1 = pc
        stair.box(((u1 - u0), (v1 - v0), z1 - z0), P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2), (0, 0, YAW), m, 0.0)


# ------------------------------------------------------------------ piso: desenho radial discreto + faixa de borda
def floor_inlay(inl):
    zt, zb = Z + 0.05, Z - 0.1
    px, py = P(0.0, PAD_V).xy
    ok = lambda x, y: (not in_base(x, y, 0.5)) and math.hypot(x - CX, y - CY) < R - 1.6
    # aneis em volta do ponto do jogador (cortados pela base da torre e pela borda)
    for r0, r1, m in ((2.35, 2.7, "Stone_SG_Floor"), (6.3, 6.7, "Stone_SG_Floor"), (11.0, 11.45, "Stone_SG_Floor")):
        n = max(12, int(2 * math.pi * r1 / 1.6))
        for i in range(n):
            a0, a1 = 360.0 * i / n, 360.0 * (i + 1) / n
            am = math.radians((a0 + a1) / 2)
            rm = (r0 + r1) / 2
            if not ok(px + rm * math.cos(am), py + rm * math.sin(am)):
                continue
            top_prism(inl, arc_piece(px, py, r0, r1, a0, a1, 6.0), zb, zt, m)
    # raios (12) entre os aneis
    for k in range(12):
        a = math.radians(15.0 + 30.0 * k)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        for ra, rb in ((2.7, 6.3), (6.7, 11.0)):
            pa = Vector((px, py, 0.0)) + d * ra
            pb = Vector((px, py, 0.0)) + d * rb
            q = [pa + (pb - pa) * (t / 6.0) for t in range(7)]
            good = [p for p in q if ok(p.x, p.y)]
            if len(good) < 7:
                continue
            w = 0.3 if ra < 3 else 0.34
            nrm = Vector((-d.y, d.x, 0.0)) * (w / 2)
            top_prism(inl, [tuple((pa + nrm).xy), tuple((pa - nrm).xy), tuple((pb - nrm).xy), tuple((pb + nrm).xy)],
                      zb, zt, m)
    # estrela de 8 pontas (cantaria clara) no ponto do jogador, rente ao piso
    import il_summon_kit as K
    pts = [(px + x, py + y) for x, y in K.star_pts(8, 2.05, 0.95, rot=math.radians(11.25))]
    top_prism(inl, pts, zb, zt + 0.01, "Stone_SG_Trim")
    # faixa de borda (lajes escuras) por dentro da balaustrada, cortada na escada e na base da torre
    for a0 in range(-180, 180, 6):
        a1 = a0 + 6
        am = math.radians(a0 + 3.0)
        rm = (RAIL_R - 1.3)
        x, y = CX + rm * math.cos(am), CY + rm * math.sin(am)
        if in_base(x, y, 0.6) or abs(a0 + 3.0) < GATE_A + 1.0:
            continue
        top_prism(inl, arc_piece(CX, CY, RAIL_R - 1.9, RAIL_R - 0.55, a0, a1, 3.0), zb, zt, "Stone_SG_Block")


# ------------------------------------------------------------------ balaustrada gotica baixa (borda, ponte)
def gothic_rail(rl, pts, z, post_every=7.5, end_posts=(True, True), post_big=()):
    """guarda-corpo gotico baixo sobre a polilinha 'pts' (2D) na cota z: fiada de base, colunelos a cada ~1,15,
    corrimao de cantaria clara; pilares a cada ~post_every com capitel e agulha de 4 aguas. post_big: indices dos
    pilares mais altos (portao da escada)."""
    pts = [Vector((p[0], p[1], z)) for p in pts]
    base_h, col_h, rail_h = 0.5, 1.05, 0.4
    rl.sweep([p + ZZ * 0.0 for p in pts], [(-0.5, -0.1), (0.5, -0.1), (0.5, base_h), (-0.5, base_h)],
             "Stone_SG_Block", True)
    rl.sweep(pts, [(-0.48, base_h + col_h), (0.48, base_h + col_h), (0.48, base_h + col_h + rail_h),
                   (-0.48, base_h + col_h + rail_h)], "Stone_SG_Trim", True)
    # comprimento acumulado
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + (b - a).length)
    total = acc[-1]

    def at(s):
        for i in range(len(pts) - 1):
            if acc[i + 1] >= s - 1e-9:
                t = (s - acc[i]) / max(1e-9, acc[i + 1] - acc[i])
                d = (pts[i + 1] - pts[i]).normalized()
                return pts[i] + (pts[i + 1] - pts[i]) * t, d
        d = (pts[-1] - pts[-2]).normalized()
        return pts[-1], d
    npost = max(1, int(round(total / post_every)))
    posts = [total * k / npost for k in range(npost + 1)]
    if not end_posts[0]:
        posts = posts[1:]
    if not end_posts[1]:
        posts = posts[:-1]
    # colunelos entre os pilares
    s = 0.0
    step = 1.15
    n = max(1, int(total / step))
    for k in range(n):
        sc = (k + 0.5) * total / n
        if any(abs(sc - sp) < 0.95 for sp in posts):
            continue
        p, d = at(sc)
        rl.box((0.32, 0.32, col_h), p + ZZ * (base_h + col_h / 2), (0, 0, math.atan2(d.y, d.x)), "Stone_SG_Block", 0.0)
    for i, sp in enumerate(posts):
        p, d = at(sp)
        big = i in post_big or (i - len(posts)) in post_big
        wp = 1.5 if big else 1.2
        hp = 3.0 if big else 2.3
        rz = math.atan2(d.y, d.x)
        rl.box((wp, wp, hp), p + ZZ * (hp / 2 - 0.1), (0, 0, rz), "Stone_SG_Block", 0.0)
        rl.box((wp + 0.3, wp + 0.3, 0.3), p + ZZ * (hp + 0.05), (0, 0, rz), "Stone_SG_Trim", 0.0)
        ring = [p + ZZ * (hp + 0.2) + Vector((math.cos(rz + math.pi / 4 + j * math.pi / 2),
                                                 math.sin(rz + math.pi / 4 + j * math.pi / 2), 0.0)) * (wp * 0.62)
                for j in range(4)]
        tip = p + ZZ * (hp + 0.2 + (2.4 if big else 0.55))
        bm = rl.bm
        vr = [bm.verts.new(q) for q in ring]
        vt = bm.verts.new(tip)
        for j in range(4):
            bm.faces.new((vr[j], vr[(j + 1) % 4], vt))
        bm.faces.new(list(reversed(vr)))
        rl._post(vr + [vt], "Stone_SG_Trim", None, 0, 1)


def balustrade(rl):
    """borda da plataforma: dois arcos (norte e sul) do portao da escada ate o canto do soco (bastiao)"""
    hs = POD_HW + SOC_OFF
    # angulo (em volta do centro da plataforma) onde o arco da balaustrada encontra a lateral do soco
    a_end = 180.0 - math.degrees(math.asin(min(1.0, (hs + 0.2) / RAIL_R)))
    for s in (1, -1):
        pts = [(CX + RAIL_R * math.cos(math.radians(s * a)), CY + RAIL_R * math.sin(math.radians(s * a)))
               for a in [GATE_A + (a_end - GATE_A) * i / 40 for i in range(41)]]
        gothic_rail(rl, pts, Z, post_every=7.2, post_big=(0,))


# ------------------------------------------------------------------ ponte curta (arco ogival) e escada da planta
def bridge(br, rl):
    a0, a1, w = L.SUMMON_BRIDGE
    x0, x1 = a0[0], a1[0] + 0.4                     # -100 .. -111,6 (a lingua de rocha do terreno comeca em -111,6)
    y = a0[1]
    hw = w / 2 + 1.2                                # tabuleiro ate a face de fora dos parapeitos
    # tabuleiro: lajes no topo (P1) + corpo
    br.box2((x1, y - hw, P1 - 0.35), (x0, y + hw, P1), "Stone_Paving_SG", 0.0)
    br.box2((x1, y - hw + 0.1, P1 - 2.3), (x0, y + hw - 0.1, P1 - 0.35), "Stone_SG_Block", 0.0)
    br.box2((x1 - 0.05, y - hw - 0.15, P1 - 0.75), (x0, y + hw + 0.15, P1 - 0.35), "Stone_SG_Trim", 0.0)   # cornija
    # timpanos + arco ogival (intradorso em (1 - t)^0.55: vertical na nascenca, ponta no fecho)
    zs, zk = P1 - 8.5, P1 - 3.3
    xs0, xs1 = x0 - 1.2, x1 + 0.2                   # nascencas: no penhasco da ilha e na lingua de rocha
    xm = (xs0 + xs1) / 2
    half = (xs0 - xs1) / 2
    Fr = Frame(0.0, y, 0.0, 0.0)
    nseg = 10

    def zi(x):
        t = min(1.0, abs(x - xm) / half)
        return zs + (zk - zs) * (1.0 - t) ** 0.55
    xs = [xs1 + (xs0 - xs1) * i / nseg for i in range(nseg + 1)]
    for xa, xb in zip(xs, xs[1:]):
        prof = [(xa, zi(xa)), (xb, zi(xb)), (xb, P1 - 2.3), (xa, P1 - 2.3)]
        side_prism(br, Fr, prof, -(w / 2 + 0.4), (w / 2 + 0.4), "Stone_SG_Block")
    # pes do arco ate a rocha (sob as nascencas)
    for xx in (xs0 + 0.9, xs1 - 0.9):
        br.box2((xx - 1.1, y - w / 2 - 0.4, zs - 5.0), (xx + 1.1, y + w / 2 + 0.4, zs + 0.2), "Stone_SG_Block", 0.0)
    # aduelas claras nas 2 faces (salientes 0,25)
    nv = 9
    for sy in (-1, 1):
        yy = y + sy * (w / 2 + 0.55)
        for i in range(nv):
            xa = xs1 + (xs0 - xs1) * i / nv
            xb = xs1 + (xs0 - xs1) * (i + 1) / nv
            pa, pb = Vector((xa, yy, zi(xa))), Vector((xb, yy, zi(xb)))
            mid = (pa + pb) / 2
            d = pb - pa
            tilt = math.atan2(d.z, d.x)
            br.box((d.length - 0.1, 0.5, 1.0), mid + Vector((0.0, 0.0, 0.45)), (0, -tilt, 0), "Stone_SG_Trim", 0.0)
    # parapeitos goticos (a guarda invisivel do sg_col fica na mesma linha)
    for sy in (-1, 1):
        gothic_rail(rl, [(x0 + 0.2, y + sy * BR_Y), (a1[0] - 0.3, y + sy * BR_Y)], P1, post_every=6.0)


def plan_stair(st):
    """escada 'Summon' da planta (sg_lib.plan_stair: casa com a colisao do sg_col) + banzos lisos inclinados"""
    SL.plan_stair(st, "Summon", m="Stone_Paving_SG", side_m="Stone_SG_Block", stringers=False)
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    rise = (L.STAIR_TOP_Z["Summon"] - foot[2]) / n
    Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg))
    k = rise / tread
    x_top = tread * n - tread / 2
    zt = rise * n
    x_end = (foot[0] - (CX + RAIL_R * math.cos(math.radians(GATE_A)))) - 0.8     # ate o pilar do portao
    for s in (-1, 1):
        y0, y1 = s * (BR_Y - 0.5), s * (BR_Y + 0.5)
        prof = [(0.4, -1.8), (x_end, -1.8 + zt), (x_end, zt + 1.35), (x_top, zt + 1.35), (0.4, 1.35 + 0.4 * k)]
        side_prism(st, Fs, prof, min(y0, y1), max(y0, y1), "Stone_SG_Block")
        a = Fs.p(0.4, s * BR_Y, 1.35 + 0.4 * k + 0.18)
        b = Fs.p(x_top, s * BR_Y, zt + 1.35 + 0.18)
        st.beam(a, b, 1.3, 0.36, "Stone_SG_Trim", 0.0)
        st.beam(b, Fs.p(x_end, s * BR_Y, zt + 1.35 + 0.18), 1.3, 0.36, "Stone_SG_Trim", 0.0)


# ------------------------------------------------------------------ build
def build():
    T, c, lamp_c = build_tower()
    stone = MB("SG_Sum_Base", COL, random.Random(7301), detail="near")
    trim = MB("SG_Sum_BaseTrim", COL, random.Random(7302), detail="near")
    base(stone, trim, T)
    tower_stair(stone)
    base_collision()
    inl = MB("SG_Sum_FloorInlay", COL, random.Random(7401), detail="near")
    floor_inlay(inl)
    rl = MB("SG_Sum_Balustrade", COL, random.Random(7501), detail="near")
    balustrade(rl)
    br = MB("SG_Sum_Bridge", COL, random.Random(7601), detail="near")
    bridge(br, rl)
    plan_stair(br)
    for mb in (stone, trim, inl, rl, br):
        mb.finish()
    # luzes (3): nucleo violeta (esfera-estrela) + 2 quentes baixas (lanternas goticas dos pedestais)
    light("L_SGSum_Core", "POINT", c, 9000.0, VIOLET, 3.0)
    for n, p in zip(("L_SGSum_Lantern_S", "L_SGSum_Lantern_N"), lamp_c):
        light(n, "POINT", p, 380.0, WARM, 0.4)
