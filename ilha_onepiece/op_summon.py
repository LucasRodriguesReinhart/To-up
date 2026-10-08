# op_summon - ZONA SUMMON da Ilha 5 (ONE PIECE / WANO), M2 (PLANO_OP secoes 0.7, 4.3, 7 e 9; PROMPT_USUARIO secao 13).
# Substitui op_blockout.summon. Prefixo OP_Sum_, colecao 06_SUMMON, pecas moveis VFX_OPSUM_* (12_VFX_HELPERS), luzes
# L_OPSum_* (de dia, LIGHT_KEEP) e L_OPProp_Lamp_Sum* (toro do terraco: NightOnly).
#
# TORRE AMS SEM REDESENHO, POR ALIAS (como o ds_summon da Ilha 4): e a MESMA torre de invocacao das Ilhas 1-4 (codigo da
# Ilha 1, ilha_naruto/il_summon.py, carregado com a planta DESTA ilha: il_layout.SUMMON_TOWER/FACE/T1/SUMMON_C/R
# trocados so durante o import). Preservados: ESTRELA dourada + ANEIS da esfera armilar + TORRE (corpo L1 com o nicho do
# portal, frontispicio, frontao, cornijas, L2 com a janela-estrela, coroa L3, contrafortes, mastros com estandartes e
# lanternas penduradas) + NUCLEO de energia azul do portal (Crystal_SumPortal_Glow, intocado). As partes da Ilha 1 que
# misturam base e torre (tower_stone, masts_and_lanterns, tower_collision) foram PORTADAS so com a parte da torre, como no
# ds_summon; tower_details e sphere sao chamadas direto. Os cristais pequenos da boca do nicho saem (liam como minerio).
#
# O QUE E DE WANO (so base, acesso, materiais por apelido, luz e entorno):
#   - materiais por apelido SO durante a torre: pedra lilas da Ilha 1 -> pedra escura de Wano com fiadas de pedra media
#     (Stone_OP_Dark / Stone_OP); ouro -> ouro VELHO (Metal_Gold_OPOld, um valor abaixo do Metal_OP_Gold do castelo: o
#     brilho do summon nao ofusca o marco principal - licao da DS); estandartes azul-royal -> indigo Wano; estrela: facetas
#     de Neon ambar MEDIO (Summon_OPStar_Glow) alternadas com ouro velho (a estrela continua DOURADA, nao estoura em creme
#     no dia); lanternas -> papel Wano.
#   - luz de dia contida: estrela 3000 -> 420, nucleo 1600 -> 650 (hierarquia do PLANO secao 10: sol > summon > castelo).
#   - base: PODIO DE ISHIGAKI (pedra de castelo de Wano): degrau kidan de pedra escura chanfrado com capa de pedra media,
#     podio de blocos em 3 fiadas desencontradas com recuo por fiada (talude) sobre nucleo escuro recuado (as juntas leem
#     escuras), capa de pedra escura com balanco; GUARDA-CORPO VERMELHO com cintas e giboshi de ouro velho em volta do
#     podio (aberto no corredor da escada); 2 toro de pedra (op_kit) no podio ladeando o portal; escada da torre com a
#     medida da Ilha 1 (5 x 0,8, 7,6 de largura) em pedra do op_kit.
#   - terraco: escadaria de pedra da planta (Summon, praca -> terraco, op_kit), ADRO lajeado (sando claro da escada ate a
#     torre = area de interacao para varios jogadores: ~28 x 22 livres na frente da torre) com um ANEL de pedra escura
#     rente marcando o lugar do jogador (SUMMON_PlayerPosition), faixa lajeada em volta do podio, caminhos lajeados para
#     o porto (sul) e para a ponte de saida (leste); guarda-corpo vermelho nas bordas que dao para o porto (aberto na
#     cabeca da ponte de saida); 4 toro altos (op_kit) emoldurando o adro; 2 canteiros com pinheiro de Wano (copa em
#     nuvens), arbustos podados e pedras.
# Marcadores SUMMON_* sao do op_core (congelado): jogador em v 16 no piso, gabinete invisivel do gacha em v 7.
# Colisao propria: degrau/podio, escada da torre + patamar, corpo da torre, mastros, toro, pinheiros, pilares de
# arranque. Piso do terraco, escada da planta e guardas de borda: op_col (congelado).
# Aviso para o op_capital (M4): as lajes do terraco do summon (x 116..206, y 150..264) sao DESTE modulo; a capital nao
# deve desenhar ruas ali. Hoje as ruas do blockout ficam 0,18 abaixo do topo das lajes (sem z-fight).
import math, random, sys, importlib
from contextlib import contextmanager
from mathutils import Vector
import bpy
import op_lib as DL
from op_lib import MB, col_box, light, Frame, ccw
import op_layout as L
import op_col
import fm_lib
import fm_portal_kit as PK
import op_kit as K
import op_entry as E

COL = "06_SUMMON"
T1 = L.T1
Z = T1
TX, TY = L.SUMMON_TOWER
CX, CY = L.SUMMON_C
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2
F = Frame(TX, TY, Z, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))     # +u (lateral; aqui = +y do mundo, norte)
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))    # +v (frente da torre; aqui = -x, oeste: praca)
ZZ = Vector((0.0, 0.0, 1.0))
# medidas da torre da Ilha 1 (il_summon) usadas antes do import; tower_mod() confere que batem
ST_FOOT, LAND_Z, PV, CORR, POD_TOP, AX, ZS = 13.6, 4.0, -1.4, 5.0, 3.3, -3.0, 46.0
LAND_V1 = 5.6
ST_W, ST_N, ST_RISE, ST_TREAD = 7.6, 5, 0.8, 1.6
WARM = (1.0, 0.64, 0.34)

# ------------------------------------------------------------------ materiais novos (2 + os 2 da torre AMS)
_S = fm_lib.S
GOLD = "Metal_Gold_OPOld"          # ouro VELHO (prefixo Metal_Gold: Metal no Roblox), um valor abaixo do Metal_OP_Gold
STAR = "Summon_OPStar_Glow"        # ambar MEDIO (Neon pela palavra glow): estrela, enfeites dos aneis
fm_lib.MATS.setdefault(GOLD, (_S(176, 134, 62), 0.45, 0.7, 0, None, 0.04))
fm_lib.MATS.setdefault(STAR, (_S(196, 120, 40), 0.3, 0.0, 0.4, _S(196, 120, 40), 0.0))
fm_lib.RBX_CAL.setdefault(STAR, (None, [int(c) for c in fm_lib.to_srgb(fm_lib.MATS[STAR][0])]))

TOWER_ALIAS = {
    "Summon_Stone_Dark": "Stone_OP_Dark", "Summon_Stone": "Stone_OP_Dark", "Stone_SumBlock": "Stone_OP",
    "Stone_Wall_Light": "Stone_OP", "Stone_SumFloor_Pale": "Stone_OP_Path", "Summon_Floor": "Stone_OP_Dark",
    "Stone_Paving_Warm": "Stone_OP_Path", "Metal_Gold": GOLD, "Cloth_Royal_Blue": "Cloth_OP_Indigo",
    "Wood_Dark": "Wood_OP_Dark", "Crystal_SumStar_Glow": STAR, "Summon_Star_Glow": STAR,
    "Crystal_SumAmber_Glow": STAR, "Crystal_SumYellow_Glow": GOLD, "Lantern_Glow": "Glass_OP_Lantern",
}
ST, STD, STP = E.ST, E.STD, E.STP
LAC, WD = E.LAC, E.WD

# ------------------------------------------------------------------ base Wano, no referencial da torre
DAIS = (15.0, -14.8, 10.0, 3.0, 0.7)     # degrau kidan: meia largura, v de tras, v da frente, chanfro, topo
POD = (12.4, -12.2, 7.2)                 # podio de ishigaki: meia largura, v de tras, v da frente
DECK = POD_TOP                           # tampo do podio (a torre nasce aqui)
COPE = 2.92                              # base da capa de pedra escura (topo = DECK)
IN_LAMP = (9.4, 4.3)                     # toro do podio (u, v)
RAIL_IN = 0.55                           # guarda-corpo do podio: recuo da borda
# entorno (mundo)
FORE = (127.4, 203.0, 156.2, 225.0)      # adro lajeado (x0, y0, x1, y1): escada da praca -> pe da escada da torre
TORO_T = [(134.5, 199.6), (140.0, 228.8), (151.0, 199.6), (156.5, 228.8)]   # fora das rotas praca/summon -> saida
PINES = [(194.0, 163.0, 11.0), (186.0, 256.0, 9.5)]
RING_R = (3.0, 4.0)                      # anel rente do lugar do jogador (SUMMON_PlayerPosition)


def P(u, v, z=0.0):
    return F.p(u, v, z)


def lbox(mb, size, u, v, z, m, bevel=0.0, rz=0.0):
    mb.box(size, P(u, v, z), (0, 0, YAW + rz), m, bevel)


def lbox2(mb, u0, v0, z0, u1, v1, z1, m, bevel=0.0):
    lbox(mb, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, m, bevel)


def lcol2(area, u0, v0, z0, u1, v1, z1):
    c = P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
    col_box(area, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), c, (0, 0, YAW))


def local_poly(pts_uv):
    return [tuple(P(u, v).xy) for u, v in pts_uv]


# ------------------------------------------------------------------ torre (codigo da Ilha 1)
_TOWER = None


def tower_mod():
    """importa il_summon com a planta desta ilha (valores do il_layout trocados so durante o import)"""
    global _TOWER
    if _TOWER is not None:
        return _TOWER
    import il_layout as NL
    want = {"SUMMON_TOWER": (TX, TY), "SUMMON_FACE_DEG": L.SUMMON_FACE_DEG, "T1": Z, "SUMMON_C": (CX, CY),
            "SUMMON_R": L.SUMMON_R}
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
                 (T.AX, AX), (T.ZS, ZS), (T.LAND_V[1], LAND_V1), (T.ST_W, ST_W), (T.ST_N, ST_N),
                 (T.ST_RISE, ST_RISE), (T.ST_TREAD, ST_TREAD)):
        assert abs(a - b) < 1e-6, (a, b)
    _TOWER = T
    return T


@contextmanager
def tower_palette():
    """materiais da Ilha 1 -> paleta Wano so enquanto a torre e montada (o MB.finish aplica fm_lib.alias)"""
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


def tower_body(T, stone, gold):
    """PORTADO de il_summon.tower_stone (so a torre, como o ds_summon.tower_body): corpo L1 com o nicho, frontispicio,
    frontao, cornijas, L2 com a janela-estrela, coroa L3. O soco/podio de 40 x 19,6 da Ilha 1 fica de fora (a base
    desta ilha e o podio de ishigaki)."""
    rng = random.Random(621)
    lb, lb2, face_skin, larch, _buttress = T.lbox, T.lbox2, T.face_skin, T.larch, T._buttress
    PORT_HW, PORT_SPRING, NICHE_TOP, MAST_V = T.PORT_HW, T.PORT_SPRING, T.NICHE_TOP, T.MAST_V
    L1_SWIN, L1_BWIN, BUT_V = T.L1_SWIN, T.L1_BWIN, T.BUT_V
    hw, v0, v1, z0, z1 = T.L1
    nw = PORT_HW + 0.8
    lb2(stone, -hw, v0, z0, hw, PV, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        lb2(stone, s * nw, PV, z0, s * hw, v1, z1, "Summon_Stone_Dark", 0.0)
    lb2(stone, -nw, PV, NICHE_TOP, nw, v1, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Summon_Stone" if k % 2 == 0 else "Stone_SumBlock"
            lb(stone, (0.8, v1 - PV - 0.1, zz1 - zz0 - 0.08), s * (PORT_HW + 0.4), (PV + v1) / 2, (zz0 + zz1) / 2,
               m, 0.0)
    larch(stone, 0.0, (PV + v1) / 2, 2 * PORT_HW, PORT_SPRING, PORT_HW, v1 - PV - 0.1, m="Summon_Stone",
          key_m="Stone_SumBlock", n=9, band=2.4, keystone=False, seed=1)
    s_side = (v1 - 0.6) - MAST_V
    side_op = (s_side - 1.75, s_side + 1.75, L1_SWIN[0] - 0.2, L1_SWIN[1] + L1_SWIN[2] + 0.5, L1_SWIN[2] + 0.45)
    for s in (-1, 1):
        face_skin(stone, (s * (hw + 0.25), v1 - 0.6), (s * (hw + 0.25), v0 + 0.6), z0, z1, rng, course=2.1,
                  blk=(2.6, 4.2), thick=0.8, openings=[side_op])
        for dv in (-1, 1):
            lb(stone, (0.9, 0.7, L1_SWIN[1] - L1_SWIN[0]), s * (hw + 0.5), MAST_V + dv * (L1_SWIN[2] + 0.35),
               (L1_SWIN[0] + L1_SWIN[1]) / 2, "Summon_Stone", 0.0)
    back_op = (hw - 0.6 - 2.1, hw - 0.6 + 2.1, L1_BWIN[0] - 0.2, L1_BWIN[1] + L1_BWIN[2] + 0.6, L1_BWIN[2] + 0.5)
    face_skin(stone, (hw - 0.6, v0 - 0.25), (-hw + 0.6, v0 - 0.25), z0, z1, rng, course=2.1, blk=(2.6, 4.2),
              thick=0.8, openings=[back_op])
    for s in (-1, 1):
        lb(stone, (0.6, 0.9, L1_BWIN[1] - L1_BWIN[0]), s * (L1_BWIN[2] + 0.455), v0 - 0.5,
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
            w = 2.1 if k % 2 == 0 else 1.8
            lb(stone, (w, 2.9, zz1 - zz0 - 0.08), s * (PORT_HW + 1.1), 2.55, (zz0 + zz1) / 2, m, 0.14)
        lb2(stone, s * (PORT_HW + 0.35), v1, PORT_SPRING, s * 6.3, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    lb2(stone, -PORT_HW - 0.4, v1, PORT_SPRING + PORT_HW + 0.2, PORT_HW + 0.4, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    larch(stone, 0.0, 2.6, 2 * PORT_HW, PORT_SPRING, PORT_HW, 2.9, n=9, band=1.5, keystone=True, seed=2)
    apex = (0.0, 22.6)
    for s in (-1, 1):
        stone.beam(P(s * 6.9, 3.45, 17.6), P(apex[0], 3.45, apex[1]), 1.9, 1.2, "Stone_SumBlock", 0.0)
        gold.beam(P(s * 7.2, 3.55, 18.45), P(0.0, 3.55, apex[1] + 0.85), 2.2, 0.6, "Metal_Gold", 0.0)
    PK.plate(stone, [(-6.3, 17.6), (6.3, 17.6), (0.0, apex[1] - 0.2)], P(0.0, 3.0, 0.0), XU, ZZ, 1.0,
             "Summon_Stone_Dark")
    lb2(stone, -hw - 1.0, v0 - 1.0, z1, hw + 1.0, 2.4, z1 + 0.6, "Summon_Stone_Dark", 0.0)
    lb2(gold, -hw - 1.45, v0 - 1.3, z1 + 0.6, hw + 1.45, 2.6, z1 + 1.3, "Metal_Gold", 0.0)
    hw2, w0, w1, y0, y1 = T.L2
    lb2(stone, -hw2, w0, y0, hw2, w1, y1, "Summon_Stone_Dark", 0.0)
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
        lb2(stone, s * 2.6, w1 - 0.1, y0 + 1.4, s * 3.5, w1 + 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lb2(gold, -3.8, w1 - 0.1, y0 + 0.85, 3.8, w1 + 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    larch(stone, 0.0, w0 - 0.4, 5.2, y0 + 6.8, 2.6, 1.3, n=7, band=0.9, keystone=True, seed=4)
    for s in (-1, 1):
        lb2(stone, s * 2.6, w0 + 0.1, y0 + 1.4, s * 3.5, w0 - 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lb2(gold, -3.8, w0 + 0.1, y0 + 0.85, 3.8, w0 - 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    lb2(stone, -hw2 - 0.9, w0 - 0.9, y1, hw2 + 0.9, w1 + 0.9, y1 + 0.5, "Summon_Stone_Dark", 0.0)
    lb2(gold, -hw2 - 1.2, w0 - 1.2, y1 + 0.5, hw2 + 1.2, w1 + 1.2, y1 + 1.15, "Metal_Gold", 0.0)
    h3, c0, c1, q0, q1 = T.L3
    lb2(stone, -h3, c0, q0, h3, c1, q1, "Summon_Stone_Dark", 0.0)
    for (a_uv, b_uv) in (((-h3 - 0.3, c1 + 0.3), (h3 + 0.3, c1 + 0.3)), ((h3 + 0.3, c0 - 0.3), (-h3 - 0.3, c0 - 0.3)),
                         ((h3 + 0.3, c1 + 0.3), (h3 + 0.3, c0 - 0.3)), ((-h3 - 0.3, c0 - 0.3), (-h3 - 0.3, c1 + 0.3))):
        face_skin(stone, a_uv, b_uv, q0, q1 - 0.25, rng, course=1.9, blk=(2.0, 3.2), thick=0.7, quoins=(False, False))
    lb2(gold, -h3 - 0.8, c0 - 0.8, q1 - 0.25, h3 + 0.8, c1 + 0.8, q1 + 0.35, "Metal_Gold", 0.0)
    for su in (-1, 1):
        for vv in (c0, c1):
            _buttress(stone, gold, su * h3, vv, q0, q1 + 0.9, 1.3, rng, spire=1.8, course=1.4)


def masts(T, stone, gold, glow, bn):
    """PORTADO de il_summon.masts_and_lanterns: so os mastros com estandartes e as lanternas penduradas da torre (as
    da Ilha 1, intocadas). Os 4 pedestais externos, os pedestais dos cristais e os postes do pe da escada da Ilha 1 nao
    entram (a base e de Wano)."""
    K1 = T.K
    rng = random.Random(651)
    hw, v0, v1, z0, z1 = T.L1
    hw2, w0, w1, y0, y1 = T.L2
    MAST_U, MAST_V, BAN_TH = T.MAST_U, T.MAST_V, T.BAN_TH
    z_pole = 29.8
    for s in (-1, 1):
        u = s * MAST_U
        T._buttress(stone, gold, u, MAST_V, POD_TOP, 31.0, 2.0, rng, spire=3.0, course=2.0, edges=((s, 1), (s, -1)))
        for zc in (13.18, 22.5):
            T.lbox(gold, (2.4, 2.4, 0.5), u, MAST_V, zc, "Metal_Gold", 0.0)
        T.lbox2(stone, s * (hw - 0.5), MAST_V - 0.95, POD_TOP, s * (MAST_U - 0.9), MAST_V + 0.95, 12.0,
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
        K1.spike(gold, b, b + ub * (s * 1.5), 0.45, "Metal_Gold", 4)
        gold.ico(0.5, Fb.p(s * 6.8, 0.0, z_pole), "Metal_Gold", 1)
        for uu in (-s * (stub - 0.25), s * 1.3, s * 5.9):
            gold.box((0.4, 0.8, 0.8), Fb.p(uu, 0.0, z_pole), Fb.r(), "Metal_Gold", 0.0)
        K1.banner(bn, gold, bn, Fb, 1.5 if s > 0 else -5.7, 5.7 if s > 0 else -1.5, 0.0, z_pole - 0.5, 12.6, tip=1.6)
        K1.hang_lantern(stone, glow, gold, Fb.p(-s * 2.4, 0.0, z_pole - 0.3), 1.0, drop=0.9)
        br0 = P(s * (hw2 + 0.95), w1, 29.6)
        br1 = P(s * (hw2 + 2.3), w1 + 0.4, 29.6)
        gold.beam(br0, br1, 0.35, 0.35, "Metal_Gold", 0.0)
        gold.beam(P(s * (hw2 + 0.95), w1, 28.2), br1 - ZZ * 0.1, 0.3, 0.3, "Metal_Gold", 0.0)
        K1.hang_lantern(stone, glow, gold, br1, 0.85, drop=0.55)


def tower_collision(T):
    """PORTADO de il_summon.tower_collision (so a torre; a base e de podium_collision)"""
    A = "OPSumTower"
    hw, v0, v1, z0, z1 = T.L1
    lcol2(A, -hw - 1.3, v0 - 1.3, POD_TOP, hw + 1.3, PV, T.L3[4])
    lcol2(A, -hw - 1.3, PV, T.PORT_SPRING + T.PORT_HW, hw + 1.3, v1 + 0.1, T.L3[4])
    lcol2(A, -T.PORT_HW, v1 + 0.1, T.PORT_SPRING + T.PORT_HW, T.PORT_HW, 4.3, 18.2)
    for s in (-1, 1):
        lcol2(A, s * T.PORT_HW, PV, POD_TOP, s * (hw + 1.3), 4.3, 18.2)
        lcol2(A, s * (hw - 0.1), T.MAST_V - 1.1, POD_TOP, s * (T.MAST_U + 1.0), T.MAST_V + 1.1, 31.0)


def build_tower(stone, gold, glow, cloth):
    """a torre nos MBs da zona: chamar DENTRO de tower_palette()"""
    T = tower_mod()
    tower_body(T, stone, gold)
    cr = T.tower_details(stone, gold, glow)
    cr.bm.free()                          # cristais da boca do nicho: fora (liam como minerio)
    masts(T, stone, gold, glow, cloth)
    c = T.sphere(gold, glow)              # gaiola (objeto proprio) + 3 aneis e a estrela (VFX)
    return T, c


def adopt_tower_objects(before):
    """renomeia o que o codigo da Ilha 1 criou: SUM_* -> OP_Sum_*, VFX_SUM_* -> VFX_OPSUM_*; colecao 05 -> 06"""
    dst = fm_lib.coll(COL)
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_OPSUM_" + n[len("VFX_SUM_"):]
            ob["vfx_zone"] = "summon"
        elif n.startswith("SUM_"):
            ob.name = "OP_Sum_" + n[len("SUM_"):]
        if ob.type == "MESH":
            ob.data.name = ob.name
        if not ob.name.startswith(("COL_", "VFX_")):
            for cl in list(ob.users_collection):
                if cl.name == "05_SUMMON":
                    cl.objects.unlink(ob)
                    if ob.name not in dst.objects:
                        dst.objects.link(ob)
    c05 = bpy.data.collections.get("05_SUMMON")
    if c05 is not None and not c05.objects and not c05.children:
        bpy.data.collections.remove(c05)


# ------------------------------------------------------------------ podio de ishigaki
def _course_face(mb, a, b, z0, z1, n_c, seed, setback=0.09, depth=0.9, m=ST, trim0=0.0, trim1=0.0):
    """face de blocos de pedra (uv do referencial da torre) de a ate b, de z0 a z1 em n_c fiadas desencontradas; cada
    fiada recua 'setback' (talude) e cada bloco sai um pouco diferente; juntas de 0,18 mostram o nucleo escuro"""
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    d = b - a
    ln = d.length
    t = d / ln
    nrm = Vector((t.y, -t.x, 0.0))                      # para fora (a -> b anti-horario visto de cima)
    rz = math.atan2(t.y, t.x)
    hc = (z1 - z0) / n_c
    for c in range(n_c):
        zc0 = z0 + c * hc
        off = -c * setback
        x = trim0
        j = 0
        lnx = ln - trim1
        while x < lnx - 0.05:
            w = 1.9 + 1.5 * E.hsh(seed, c, j)
            if c % 2 and j == 0:
                w *= 0.55
            if lnx - (x + w) < 0.9:
                w = lnx - x
            cm = a + t * (x + w / 2) + nrm * (off - depth / 2 + 0.06 * E.hsh(seed, c, j, 7))
            hh = hc - 0.16
            lbox(mb, (w - 0.18, depth, hh), cm.x, cm.y, zc0 + 0.08 + hh / 2, m, 0.08, rz)
            x += w
            j += 1


def podium(st, rl):
    """degrau kidan + podio de ishigaki (ver o cabecalho). st = pedra, rl = guarda-corpo (laca + ouro velho)"""
    du, dvb, dvf, ch, dz = DAIS
    pu, pvb, pvf = POD
    # --- degrau (kidan): nucleo de pedra escura + capa de pedra media com focinho de 0,12 (2 alas + fundo)
    right = [(CORR, dvb), (du - ch, dvb), (du, dvb + ch), (du, dvf - ch), (du - ch, dvf), (CORR, dvf)]
    back = [(-CORR, dvb), (CORR, dvb), (CORR, pvb + 0.6), (-CORR, pvb + 0.6)]
    for pc in (right, [(-u, v) for u, v in reversed(right)], back):
        poly = ccw(local_poly(pc))
        st.prism(poly, Z - 0.5, Z + dz - 0.24, STD)
        st.prism(ccw(DL.offset_poly(poly, 0.12)), Z + dz - 0.24, Z + dz, ST)
    # --- nucleo escuro RECUADO 0,3 (as juntas dos blocos leem escuras)
    r = 0.3
    cr_ = CORR + 0.2
    pieces = [[(cr_, pvb + r), (pu - r, pvb + r), (pu - r, pvf - r), (cr_, pvf - r)],
              [(-pu + r, pvb + r), (-cr_, pvb + r), (-cr_, pvf - r), (-pu + r, pvf - r)],
              [(-CORR, pvb + r), (CORR, pvb + r), (CORR, PV), (-CORR, PV)]]
    for pc in pieces:
        st.prism(ccw(local_poly(pc)), Z + dz - 0.05, Z + COPE + 0.02, STD)
    # --- blocos em 3 fiadas (talude) nas faces: frente das 2 alas, lados e fundo; as faces laterais sao donas das
    #     quinas (frente e fundo param 1,0 antes: sem faces coplanares na quina)
    faces = [((pu, pvf), (CORR + 0.15, pvf)), ((-CORR - 0.15, pvf), (-pu, pvf)), ((pu, pvb), (pu, pvf)),
             ((-pu, pvf), (-pu, pvb)), ((-pu, pvb), (pu, pvb))]
    trims = [(1.0, 0.0), (0.0, 1.0), (0.0, 0.0), (0.0, 0.0), (1.0, 1.0)]
    for i, (a, b) in enumerate(faces):
        _course_face(st, a, b, dz, COPE, 3, 800 + i, trim0=trims[i][0], trim1=trims[i][1])
    # --- capa de pedra escura com balanco de 0,3 (o tampo do podio) - 2 alas + meio (atras do portal)
    deck = [[(CORR, pvb), (pu, pvb), (pu, pvf), (CORR, pvf)], [(-pu, pvb), (-CORR, pvb), (-CORR, pvf), (-pu, pvf)],
            [(-CORR, pvb), (CORR, pvb), (CORR, PV), (-CORR, PV)]]
    for i, pc in enumerate(deck):
        poly = local_poly(pc)
        grow = 0.3 if i < 2 else 0.0
        st.prism(ccw(DL.offset_poly(ccw(poly), grow)), Z + COPE, Z + DECK, STD)
    # --- patamar do portal: pedra escura + laje de caminho com focinho
    lbox2(st, -CORR, PV, dz - 0.05, CORR, pvf, LAND_Z - 0.3, STD)
    lbox2(st, -CORR, PV, LAND_Z - 0.3, CORR, pvf + 0.12, LAND_Z, STP)
    # --- guarda-corpo vermelho do podio (recuado RAIL_IN), aberto no corredor da escada; postes-mestre nas quinas
    ri = RAIL_IN
    path_l = [(-CORR - 0.45, pvf - ri), (-pu + ri, pvf - ri), (-pu + ri, pvb + ri), (pu - ri, pvb + ri),
              (pu - ri, pvf - ri), (CORR + 0.45, pvf - ri)]
    for (ua, va), (ub, vb) in zip(path_l, path_l[1:]):
        a = P(ua, va, DECK)
        b = P(ub, vb, DECK)
        E.rail_run(rl, (a.x, a.y, a.z), (b.x, b.y, b.z), h=2.0, step=4.2, nodes=(0.0, 1.0), node_up=0.6, post=0.4,
                   node_post=0.62, top_w=0.6, gold=GOLD)


def podium_collision():
    A = "OPSumTower"
    du, dvb, dvf, ch, dz = DAIS
    pu, pvb, pvf = POD
    for s in (-1, 1):
        lcol2(A, s * CORR, dvb + ch, -0.6, s * du, dvf - ch, dz)
        lcol2(A, s * CORR, dvb, -0.6, s * (du - ch), dvf, dz)
        lcol2(A, s * CORR, pvb - 0.3, -0.6, s * (pu + 0.3), pvf + 0.3, DECK + 2.2)     # podio + guarda-corpo
    lcol2(A, -CORR, dvb, -0.6, CORR, pvb - 0.3, dz)
    lcol2(A, -CORR, pvb - 0.3, -0.6, CORR, PV, DECK)
    lcol2(A, -CORR, PV, -0.2, CORR, LAND_V1, LAND_Z)


def tower_stair(st):
    """escada da torre com a medida da Ilha 1 (5 x 0,8, piso 1,6, 7,6 de largura; o 5o degrau e a frente do patamar)
    em pedra do op_kit (stair_stone: juntas desencontradas, focinho, banzos com capa e pilaretes). Colisao:
    op_col.stair_col (rampa + guardas)."""
    base = P(0.0, ST_FOOT, 0.0)
    ang = FACE + math.pi
    Fs = Frame(base.x, base.y, base.z, ang - math.pi / 2)        # o kit sobe para +y
    K.stair_stone(st, Fs, ST_W, ST_N - 1, rise=ST_RISE, tread=ST_TREAD, z_floor=-0.3, cheek_h=0.9)
    op_col.stair_col("OPSumTower", (base.x, base.y, base.z), ang, ST_W, ST_N, ST_RISE, ST_TREAD, guards=True,
                     guard_h=4.0)


def podium_lamps(st):
    out = []
    for s in (-1, 1):
        p = P(s * IN_LAMP[0], IN_LAMP[1], DECK)
        out.append(K.toro(st, Frame(p.x, p.y, p.z, YAW), 0.82))
        col_box("OPSumTower", (2.2, 2.2, 6.4), (p.x, p.y, p.z + 3.2), (0, 0, YAW))
    return out


# ------------------------------------------------------------------ terraco: pavimento, guarda-corpo, paisagismo
def _flags(mb, x0, y0, x1, y1, z, seed, m=ST, along="x", lw=(1.8, 3.2), lh=(1.7, 2.3), skip=None, edge=None):
    """lajeado retangular em fiadas desencontradas (juntas 0,16; topo z; sem chanfro: o orcamento vai para a junta).
    'skip(x, y)' -> True: sem laje ali; 'edge(x, y)' -> material da laje."""
    if along == "x":
        a0, a1, b0, b1 = y0, y1, x0, x1
    else:
        a0, a1, b0, b1 = x0, x1, y0, y1
    a = a0
    row = 0
    while a < a1 - 0.4:
        h = lh[0] + (lh[1] - lh[0]) * E.hsh(seed, row)
        if a1 - (a + h) < 0.8:
            h = a1 - a
        b = b0
        j = 0
        while b < b1 - 0.4:
            w = lw[0] + (lw[1] - lw[0]) * E.hsh(seed, row, j)
            if row % 2 and j == 0:
                w *= 0.6
            if b1 - (b + w) < 0.9:
                w = b1 - b
            if along == "x":
                cx, cy, sx, sy = b + w / 2, a + h / 2, w, h
            else:
                cx, cy, sx, sy = a + h / 2, b + w / 2, h, w
            if not (skip and skip(cx, cy)):
                mm = edge(cx, cy) if edge else m
                mb.box((sx - 0.16, sy - 0.16, 0.34), (cx, cy, z - 0.17), (0, 0, (E.hsh(seed, row, j, 5) - 0.5) * 0.02),
                       mm, 0.0)
            b += w
            j += 1
        a += h
        row += 1


def _in_dais(x, y, pad=0.0):
    du, dvb, dvf, ch, dz = DAIS
    u = (y - TY)
    v = -(x - TX)
    return -du - pad <= u <= du + pad and dvb - pad <= v <= dvf + pad


def terrace(st, pv, rl, gr):
    zt = T1 + 0.3                                   # topo das lajes (0,18 acima das ruas do blockout da capital)
    # escadaria da planta: terraco -> praca (lado leste da praca), pedra do op_kit no envelope do op_col
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    K.stair_stone(st, Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2), w, n,
                  rise=L.stair_rise("Summon"), tread=tread, z_floor=-0.3)
    a = math.radians(deg)
    for sx in (-1, 1):                              # pilaretes de arranque do kit
        px = foot[0] - math.cos(a) * 0.55 - math.sin(a) * sx * (w / 2 + 0.6)
        py = foot[1] - math.sin(a) * 0.55 + math.cos(a) * sx * (w / 2 + 0.6)
        col_box("OPSumStair", (1.6, 1.6, 2.2), (px, py, foot[2] + 1.1))
    # ADRO: sando claro (lajes grandes) no eixo + bordas de pedra media; area livre de interacao; ANEL rente de pedra
    # escura no lugar do jogador (laje propria, mesma cota: nada coplanar)
    x0, y0, x1, y1 = FORE
    pp = P(0.0, L.SUMMON_PLAYER_D)

    def fore_m(cx, cy):
        return STP if abs(cy - TY) < 5.2 else ST

    def in_ring(cx, cy):
        return math.hypot(cx - pp.x, cy - pp.y) < RING_R[1] + 1.4
    _flags(pv, x0, y0, x1, y1, zt, 31, along="y", lw=(2.2, 3.4), lh=(1.9, 2.5), edge=fore_m, skip=in_ring)
    nr = 20
    for i in range(nr):
        a0, a1 = 2 * math.pi * i / nr + 0.02, 2 * math.pi * (i + 1) / nr - 0.02
        pts = [(pp.x + RING_R[0] * math.cos(a0), pp.y + RING_R[0] * math.sin(a0)),
               (pp.x + RING_R[0] * math.cos(a1), pp.y + RING_R[0] * math.sin(a1)),
               (pp.x + RING_R[1] * math.cos(a1), pp.y + RING_R[1] * math.sin(a1)),
               (pp.x + RING_R[1] * math.cos(a0), pp.y + RING_R[1] * math.sin(a0))]
        pv.prism(ccw(pts), T1 - 0.02, zt, STD)
    for i in range(6):
        a0, a1 = 2 * math.pi * i / 6 + 0.05, 2 * math.pi * (i + 1) / 6 - 0.05
        pts = [(pp.x, pp.y)] + [(pp.x + (RING_R[0] - 0.12) * math.cos(a0 + (a1 - a0) * k / 3),
                                 pp.y + (RING_R[0] - 0.12) * math.sin(a0 + (a1 - a0) * k / 3)) for k in range(4)]
        pv.prism(ccw(pts), T1 - 0.02, zt, STP)
    # lajes livres entre o adro e o anel (o anel tira um furo redondo do adro: preenche com lajes radiais curtas)
    for i in range(12):
        a0, a1 = 2 * math.pi * i / 12 + 0.03, 2 * math.pi * (i + 1) / 12 - 0.03
        r0, r1 = RING_R[1] + 0.08, RING_R[1] + 1.4 + 1.2
        pts = [(pp.x + r0 * math.cos(a0), pp.y + r0 * math.sin(a0)), (pp.x + r0 * math.cos(a1), pp.y + r0 * math.sin(a1)),
               (pp.x + r1 * math.cos(a1), pp.y + r1 * math.sin(a1)), (pp.x + r1 * math.cos(a0), pp.y + r1 * math.sin(a0))]
        pts = [(min(max(px, x0 + 0.1), x1 - 0.1), min(max(py, y0 + 0.1), y1 - 0.1)) for px, py in pts]
        pv.prism(ccw(pts), T1 - 0.02, zt, ST)
    # faixa lajeada em volta do degrau do podio (3 de largura), fora do corredor da escada da torre
    du, dvb, dvf, ch, dz = DAIS
    ring_x0, ring_x1 = TX - dvf - 0.2, TX - dvb + 3.0
    ring_y0, ring_y1 = TY - du - 3.0, TY + du + 3.0

    def skip_ring(cx, cy):
        if _in_dais(cx, cy, 0.9):
            return True
        return abs(cy - TY) < ST_W / 2 + 1.8 and cx < TX - dvf + 1.0          # corredor da escada (sem laje)
    _flags(pv, ring_x0, ring_y0, ring_x1, ring_y1, zt, 37, along="x", lw=(1.6, 2.8), lh=(1.6, 2.2), skip=skip_ring)
    # caminho do porto (sul) e da ponte de saida (leste)
    _flags(pv, 138.2, 151.0, 149.0, y0, zt, 41, along="x", lw=(1.8, 3.0), m=STP)
    _flags(pv, 146.0, 233.6, 205.4, 246.4, zt, 43, along="y", lw=(1.8, 3.0), m=STP)
    _flags(pv, 192.0, 226.6, 205.4, 233.6, zt, 47, along="y", lw=(1.8, 2.6), m=STP)     # boca da ponte de saida
    # meio-fio de pedra escura nas bordas longas do adro (separa o lajeado claro da grama)
    for (a_, b_) in (((x0, y0 - 0.35), (x1, y0 - 0.35)), ((x0, y1 + 0.35), (x1, y1 + 0.35))):
        st.box((b_[0] - a_[0], 0.5, 0.6), ((a_[0] + b_[0]) / 2, a_[1], T1 + 0.1), (0, 0, 0), STD, 0.0)
    # guarda-corpo vermelho nas bordas que dao para o porto (aberto na cabeca da ponte de saida e nas escadas)
    for a_, b_, nodes in (((149.0, 150.75), (205.25, 150.75), (0.0, 0.5, 1.0)),
                          ((205.25, 151.2), (205.25, 225.6), (0.0, 0.5, 1.0)),
                          ((205.25, 246.4), (205.25, 256.0), (0.0, 1.0)),
                          ((205.25, 256.0), (199.6, 263.4), (1.0,))):
        E.rail_run(rl, (a_[0], a_[1], T1), (b_[0], b_[1], T1), h=2.4, step=4.6, nodes=nodes, node_up=0.7, post=0.44,
                   node_post=0.7, top_w=0.66, gold=GOLD)
    # 4 toro altos (op_kit) emoldurando o adro
    cs = []
    for i, (x, y) in enumerate(TORO_T):
        cs.append(K.toro(st, Frame(x, y, T1, 0.0), 1.1))
        col_box("OPSumToro", (2.5, 2.5, 7.8), (x, y, T1 + 3.9))
    # canteiros: meio-fio de pedra, terra, pinheiro de Wano (copa em nuvens), arbustos podados e pedras
    for i, (px, py, h) in enumerate(PINES):
        bed = DL.blob_poly(px, py, 6.2, 10, random.Random(950 + i), 0.12, sx=1.25)
        st.prism(ccw(bed), T1 - 0.2, T1 + 0.38, STD)
        gr.prism(ccw(DL.offset_poly(ccw(bed), -0.55)), T1 + 0.2, T1 + 0.52, "Dirt_OP")
        wano_pine(gr, px, py, T1 + 0.52, h, random.Random(960 + i))
        col_box("OPSumPine", (1.8, 1.8, h * 0.6), (px, py, T1 + h * 0.3))
        for k in range(3):
            aa = 2.1 + k * 1.9 + i
            r = 1.1 + 0.4 * E.hsh(i, k)
            gr.ico(r, (px + math.cos(aa) * 4.0, py + math.sin(aa) * 3.4, T1 + 0.5 + r * 0.45), "Leaf_OP", 1,
                   scale=(1.3, 1.15, 0.8))
        st.ico(1.0, (px - 3.6, py + 2.2, T1 + 0.6), "Stone_OP", 1, scale=(1.4, 1.0, 0.7))
        st.ico(0.7, (px - 2.2, py + 3.4, T1 + 0.5), "Stone_OP_Dark", 1, scale=(1.3, 1.0, 0.7))
    return cs


def wano_pine(mb, x, y, z, h, rng):
    """pinheiro de Wano (kuromatsu podado): raiz alargada, tronco BAIXO que inclina e torce em S (afinando), galhos
    quase horizontais em alturas desencontradas terminando em COPAS EM NUVEM (camada de baixo verde-pinho escura e
    larga + camada de cima mais clara e menor, achatadas, com folga entre as nuvens: le como bonsai grande, nao como
    guarda-chuva) e uma nuvem no topo"""
    lean = rng.uniform(0, math.tau)
    lv = Vector((math.cos(lean), math.sin(lean), 0.0))
    sv = Vector((-lv.y, lv.x, 0.0))
    b0 = Vector((x, y, z))
    pts = [b0 - ZZ * 0.3, b0 + lv * 0.6 + ZZ * h * 0.22, b0 + lv * 2.2 + sv * 0.8 + ZZ * h * 0.45,
           b0 + lv * 3.0 - sv * 0.4 + ZZ * h * 0.68, b0 + lv * 2.4 + ZZ * h * 0.86]
    PK.taper_tube(mb, pts, [0.85, 0.66, 0.5, 0.36, 0.26], "Bark_OP", n=8)
    PK.cone(mb, b0 - ZZ * 0.3, b0 + ZZ * 0.9, 1.5, 0.82, "Bark_OP", 8)
    pads = []
    for k, (t, ang, ln, rr) in enumerate(((0.34, 2.9, 4.6, 2.6), (0.5, 0.6, 4.2, 2.4), (0.62, 4.3, 3.8, 2.2),
                                           (0.76, 1.9, 3.4, 2.0), (0.88, 5.4, 2.6, 1.7))):
        a = lean + ang + rng.uniform(-0.25, 0.25)
        seg = min(3, int(t * 4))
        base = pts[seg].lerp(pts[seg + 1], t * 4 - seg)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        mid = base + d * ln * 0.55 + ZZ * 0.25
        tip = base + d * ln + ZZ * 0.55
        PK.taper_tube(mb, [base, mid, tip], [0.3, 0.22, 0.15], "Bark_OP", n=6)
        pads.append((tip, rr, a))
    pads.append((pts[-1] + ZZ * 0.5, 1.9, lean))
    for c, rr, a in pads:
        mb.ico(rr, c + ZZ * 0.15, "Leaf_OP_Pine", 1, scale=(1.4, 1.15, 0.42), rot=(0, 0, a))
        mb.ico(rr * 0.72, c + ZZ * 0.62 + Vector((math.cos(a), math.sin(a), 0)) * 0.3, "Leaf_OP", 1,
               scale=(1.3, 1.1, 0.4), rot=(0, 0, a + 0.5))


# ------------------------------------------------------------------ cameras de revisao
def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


EYE = L.EYE
CAMS = {
    "CAM_OPSum_Terrace": ((131.0, 214.0, T1 + EYE), (TX, TY, T1 + 20.0), 22),
    "CAM_OPSum_Pad": _cam(0.0, 16.0, EYE, 0.0, PV, 10.0, 22),
    "CAM_OPSum_Base": _cam(-12.0, 18.0, 4.2, -9.0, 6.0, 2.0, 26),
    "CAM_OPSum_BaseSide": ((176.0, 186.0, T1 + 5.2), (178.0, 202.0, T1 + 3.0), 26),
    "CAM_OPSum_34": ((140.0, 182.0, T1 + 14.0), (TX + 2.0, TY, T1 + 20.0), 22),
    "CAM_OPSum_Back": ((214.0, 252.0, T1 + 22.0), (TX, TY, T1 + 16.0), 24),
    "CAM_OPSum_FromPlaza": ((88.0, 214.0, L.P + EYE), (TX, TY, T1 + 24.0), 22),
    "CAM_OPSum_Rail": ((196.0, 198.0, T1 + 4.8), (205.0, 182.0, T1 + 1.6), 26),
    "CAM_OPSum_Pine": ((182.0, 176.0, T1 + 6.0), (194.0, 163.0, T1 + 5.0), 24),
    "CAM_OPSum_ExitPath": ((152.0, 240.0, T1 + EYE), (206.0, 236.0, T1 + 4.0), 22),
}


def build():
    """a zona em POUCOS objetos por familia (orcamento de MeshParts: 1 por material por objeto): pedra (torre, podio,
    escadas, toro), lajeado, metal (ouro velho da torre), brilho (portal, estrela, lanternas), pano (estandartes),
    guarda-corpo (laca + ouro velho) e verde (pinheiros, arbustos, terra). A gaiola da esfera e os VFX saem do codigo
    da Ilha 1."""
    before = {o.name for o in bpy.data.objects}
    st = MB("OP_Sum_Stone", COL, random.Random(7401), detail="near")
    mt = MB("OP_Sum_Metal", COL, random.Random(7403), detail="near")
    gl = MB("OP_Sum_Glow", COL, random.Random(7404), detail="hero")
    cl = MB("OP_Sum_Cloth", COL, random.Random(7405), detail="near")
    rl = MB("OP_Sum_Rail", COL, random.Random(7406), detail="near")
    gr = MB("OP_Sum_Garden", COL, random.Random(7410), detail="near")
    pv = MB("OP_Sum_Paving", COL, random.Random(7407), detail="near")
    with tower_palette():
        T, c = build_tower(st, mt, gl, cl)
        podium(st, rl)
        tower_stair(st)
        lamps = podium_lamps(st)
        tops = terrace(st, pv, rl, gr)
        for mb in (st, mt, gl, cl, rl, gr, pv):
            mb.finish()
    adopt_tower_objects(before)
    tower_collision(T)
    podium_collision()
    for i, cc in enumerate(tops[:2]):
        light("L_OPProp_Lamp_Sum_%d" % i, "POINT", tuple(cc), 120.0, WARM, 0.3)
    # luzes de dia (4): nucleo azul do portal, estrela (quente, contida), 2 toro do podio
    light("L_OPSum_Core", "POINT", tuple(P(0.0, PV + 3.0, 9.0)), 650.0, (0.36, 0.52, 1.0), 1.0)
    light("L_OPSum_Star", "POINT", tuple(c), 420.0, (1.0, 0.72, 0.36), 1.4)
    for n, p in zip(("L_OPSum_Lamp_L", "L_OPSum_Lamp_R"), lamps):
        light(n, "POINT", tuple(p), 130.0, WARM, 0.3)
    print("OP_SUMMON ok")
