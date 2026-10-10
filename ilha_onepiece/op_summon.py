# op_summon - ZONA SUMMON da Ilha 5 (ONE PIECE / WANO): M2 + V2-2 'Conves do Summon' (PLANO_V2 secao 6).
# Substitui op_blockout.summon. Prefixo OP_Sum_, colecao 06_SUMMON, pecas moveis VFX_OPSUM_* (12_VFX_HELPERS), luzes
# L_OPSum_* (de dia, LIGHT_KEEP) e L_OPProp_Lamp_Sum* (lanternas de popa: NightOnly).
#
# TORRE AMS SEM REDESENHO, POR ALIAS (como o ds_summon da Ilha 4): e a MESMA torre de invocacao das Ilhas 1-4 (codigo da
# Ilha 1, ilha_naruto/il_summon.py, carregado com a planta DESTA ilha: il_layout.SUMMON_TOWER/FACE/T1/SUMMON_C/R
# trocados so durante o import). Preservados: ESTRELA dourada + ANEIS da esfera armilar + TORRE (corpo L1 com o nicho do
# portal, frontispicio, frontao, cornijas, L2 com a janela-estrela, coroa L3, contrafortes, mastros (sem estandartes) e
# lanternas penduradas) + NUCLEO de energia azul do portal (Crystal_SumPortal_Glow, intocado). As partes da Ilha 1 que
# misturam base e torre (tower_stone, masts_and_lanterns, tower_collision) foram PORTADAS so com a parte da torre, como no
# ds_summon; tower_details e sphere sao chamadas direto. Os cristais pequenos da boca do nicho saem (liam como minerio).
#
# V2-2 (U10 "summon sem tema One Piece", U16 bandeiras; PLANO_V2 secao 6, opcao A): o terraco virou o CONVES DE UM
# NAVIO PIRATA. A torre continua a do alias (paleta Wano por apelido SO durante a torre: pedra escura de Wano, ouro VELHO
# Metal_Gold_OPOld, estrela Summon_OPStar_Glow, luz de dia contida: estrela 420, nucleo 650); sem as 2 flamulas (U16).
#   - CASCO no eixo da torre (y 214): popa aberta no pe da escada da praca (x 128), boca 36 -> 48, proa parabolica para
#     o MAR (leste): o bico passa a borda do terraco (x 206) e fica sobre o porto, com costado de tabuas ate a quilha,
#     roda de proa, ancora no turco e a CARRANCA de leao (juba-sol de 16 raios, sem texto) olhando o mar.
#   - CONVES de tabuas ao comprido (so faces de cima, sub-conves escuro nas frestas), trincaniz escuro, ROSA-DOS-VENTOS
#     no lugar do jogador (SUMMON_PlayerPosition), 2 escotilhas com grade, cabrestante, quebra-mar antes do bico.
#   - AMURADAS: costado com cinta vermelha, capa escura, forro claro e guarda-corpo vermelho vazado; portalos abertos
#     onde as rotas cruzam (bombordo x 131..147,5, boreste x 132..157,5, popa y 206,2..225,8) com cabecos e 2
#     lanternas de popa (NightOnly).
#   - CASA DO MASTRO = o antigo podio com AS MESMAS medidas/colisao: degrau e costado de tabuas em trincado, cinta
#     vermelha, vigias de latao acesas, tabuado, escada da torre em madeira (medida da Ilha 1), 2 lanternas de navio
#     (L_OPSum_Lamp_L/R) e guarda-corpo vermelho de navio.
#   - 2 MASTROS LATERAIS (x 176, y 214 +- 21, ladeando a torre) com cesto, verga, VELA REDONDA com a JOLLY ROGER dos
#     Chapeus de Palha virada para a praca (desenho aprovado do op_ship), bandeira preta com a caveira no mastareu e
#     cordame (ovens com enfrechates, estai ate a roda, brandal). Sao as 2 bandeiras do conves do PLANO_V2 secao 8.
#   - TIMAO grande na popa (bombordo), BAUS DO TESOURO abertos com moedas de ouro (discos, sem cristal), barris,
#     4 canhoes decorativos (bocas nas portinholas do costado), cabeco de amarracao entre a proa e a ponte de saida.
#   - TERRACO em volta: escada da praca (op_kit), lajeado so nas rotas de fora (porto e ponte de saida), guarda-corpo
#     vermelho da borda (aberto onde a proa passa) com colisao propria; sem os toro, o adro e os pinheiros da V1.
# Colisao (gate 'visual' da V2-0 verde): amuradas em cordas ate T1+4,2 (guarda de 4), quebra-mar, bico da proa,
# ancora, mastros, lanternas de popa, carga/timao/bau/canhoes/cabrestante, escotilhas e rosa (o pe nao afunda),
# banzos da escada da praca, casa do mastro + torre (as da V1). Piso do terraco e guardas do labio: op_col.
# Materiais novos: Emblem_OP_LionMane / Emblem_OP_LionFace (SmoothPlastic). Objetos: OP_Sum_Ship (normais calculadas,
# so os tubos recalculados), OP_Sum_Deck (so faces de cima), OP_Sum_Sails, OP_Sum_Paving + os da torre.
# Marcadores SUMMON_* sao do op_core (congelado): jogador em v 16 no piso, gabinete invisivel do gacha em v 7.
import math, random, sys, importlib
import bmesh
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
PINES = []                               # V2: sem os canteiros de pinheiro (wano_pine fica para quem precisar)


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


def masts(T, stone, gold, glow, bn=None):
    """PORTADO de il_summon.masts_and_lanterns: so os mastros (contrafortes) e as lanternas das misulas da torre (as
    da Ilha 1, intocadas). Os 4 pedestais externos, os pedestais dos cristais e os postes do pe da escada da Ilha 1 nao
    entram (a base e o conves). V2: sem os estandartes (U16)."""
    K1 = T.K
    rng = random.Random(651)
    hw, v0, v1, z0, z1 = T.L1
    hw2, w0, w1, y0, y1 = T.L2
    MAST_U, MAST_V = T.MAST_U, T.MAST_V
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
        # V2 (U16, PLANO_V2 secoes 6 e 8): SAEM as 2 flamulas da torre (vara, ponteira, estandarte e a lanterna
        # pendurada na vara); a bandeira do conves e a Jolly Roger dos mastros do navio. O resto da torre fica intacto.
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


# ================================================================== CONVES DO SUMMON (V2, U10): NAVIO PIRATA
# Eixo do navio = eixo da torre (y = TY, 214), PROA para LESTE (o mar: a ponta passa a borda do terraco x 206 e fica
# sobre o porto), POPA no pe da escada da praca (x 128). Tudo em pecas proprias (detalhe 'far', sem chanfro: o custo
# vai para a silhueta). Ver o cabecalho para a lista completa.
WD, WM, HULL, LACQ = "Wood_OP_Dark", "Wood_OP_Mid", "Wood_OP_Hull", "Wood_OP_Lacquer"
IRON, BGOLD = "Metal_OP_Iron", "Metal_OP_Gold"
SAIL, CW, CB, CST, CR, ROPE = "Cloth_OP_Sail", "Cloth_OP_White", "Cloth_OP_Black", "Cloth_OP_Straw", "Cloth_OP_Red", "Rope"
LIT, LGLOW = "Window_OP_Warm", "Glass_OP_Lantern"
MANE, LFACE = "Emblem_OP_LionMane", "Emblem_OP_LionFace"        # 2 materiais novos (Emblem_ -> SmoothPlastic)
fm_lib.MATS.setdefault(MANE, (_S(226, 126, 44), 0.7, 0.0, 0, None, 0.0))
fm_lib.MATS.setdefault(LFACE, (_S(248, 208, 108), 0.7, 0.0, 0, None, 0.0))

CY = TY                                   # linha de centro do navio = eixo da torre
X_ST, X_F0, X_F1, X_TIP = 128.0, 142.0, 170.0, 215.0     # painel de popa, inicio/fim do trecho reto, ponta da roda
HB_ST, HB = 18.0, 24.0                    # meia boca na popa / no meio
X_BRK = 204.6                             # vertice do quebra-mar (antes da guarda invisivel do op_col em x ~206,5)
X_WEND = 214.2                            # fim das amuradas (a roda de proa cobre a junta)
DZ = T1 + 0.30                            # topo das tabuas (a cota das lajes antigas, sobre a pele do terreno)
SUBZ = T1 + 0.18                          # sub-conves escuro (as frestas leem escuras; 0,12 abaixo das tabuas)
BW_T = 0.5                                # espessura da amurada
WL0, WL1 = T1 + 1.42, T1 + 1.72           # cinta vermelha (wale) no costado
BW_TOP = T1 + 1.95                        # topo da amurada macica
CAP_Z = BW_TOP + 0.16                     # capa escura (borda falsa)
RAIL_Z = T1 + 3.3                         # corrimao vermelho
COL_TOP = T1 + 4.2                        # topo da guarda da amurada (PLANO_V2 secao 6: guarda de 4; cobre corrimao e cabecos)
GUN_Z = T1 + 0.85                         # eixo dos canhoes / portinholas
OPEN_X = {-1: (131.0, 147.5), 1: (132.0, 157.5)}   # portalos de bordo (bombordo = sul, boreste = norte): rotas
STERN_OPEN = (206.2, 225.8)               # popa aberta na escada da praca (y)
OUT_XS = [128.0, 129.2, 130.6, 132.2, 134.0, 136.0, 138.4, 142.0, 150.0, 158.0, 166.0, 170.0, 175.0, 180.0, 185.0,
          190.0, 194.0, 198.0, 201.0, 204.0, 206.5, 209.0, 211.0, 212.6, 213.6, 214.2]
SAIL_MASTS = [(176.0, CY - 21.0, -1), (176.0, CY + 21.0, 1)]     # mastros laterais (velas com a Jolly Roger)
YARD_Z, SAIL_FOOT = T1 + 24.6, T1 + 11.0
MAST_TOP = T1 + 31.0
GUNS = [(186.0, -1), (194.0, -1), (186.0, 1), (194.0, 1)]
HELM = (133.2, 199.6)
ROSE_R = 4.6
F0 = Frame(0.0, 0.0, 0.0, 0.0)


def hb(x):
    """meia boca do casco (linha de fora) em x: popa arredondada 18 -> 24, trecho reto, proa parabolica ate a ponta"""
    if x <= X_ST:
        return HB_ST
    if x < X_F0:
        return HB_ST + (HB - HB_ST) * math.sin(math.pi / 2 * (x - X_ST) / (X_F0 - X_ST))
    if x <= X_F1:
        return HB
    t = min(1.0, (x - X_F1) / (X_TIP - X_F1))
    return HB * (1.0 - t * t)


def in_hull(x, y, pad=0.0):
    if x < X_ST - pad or x > X_TIP + pad:
        return False
    return abs(y - CY) <= hb(min(max(x, X_ST), X_TIP)) + pad


def outline(off=0.0):
    """contorno do casco (CCW) recuado 'off' para dentro (so nos bordos; a popa fica em X_ST)"""
    xs = [x for x in OUT_XS if hb(x) - off > 0.05]
    lo = [(x, CY - (hb(x) - off)) for x in xs]
    hi = [(x, CY + (hb(x) - off)) for x in reversed(xs)]
    t = math.sqrt(max(0.0, 1.0 - off / HB))
    return lo + [(X_F1 + (X_TIP - X_F1) * t, CY)] + hi


def tube(mb, pts, r, m, n=4):
    """tubo varrido com as normais recalculadas SO nele (ilha propria): o MB do navio fecha sem recalcular"""
    nf = len(mb.bm.faces)
    mb.tube(pts, r, m, n=n)
    mb.bm.faces.ensure_lookup_table()
    fs = [mb.bm.faces[i] for i in range(nf, len(mb.bm.faces))]
    if fs:
        bmesh.ops.recalc_face_normals(mb.bm, faces=fs)


def qf(mb, pts, m, hint):
    """face (poligono convexo) com a normal virada para 'hint' (o MB fecha sem recalcular)"""
    vs = [mb.bm.verts.new(Vector(p)) for p in pts]
    f = mb.bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(Vector(hint)) < 0:
        f.normal_flip()
    mb._post(vs, m, None, 0, 1)


def _in_dais_poly(x, y):
    du, dvb, dvf, ch, dz = DAIS
    u, v = y - TY, -(x - TX)
    if not (-du <= u <= du and dvb <= v <= dvf):
        return False
    return (du - abs(u)) + (min(v - dvb, dvf - v)) >= ch


# ------------------------------------------------------------------ conves (tabuas ao comprido + sub-conves)
def deck(dk):
    full = outline(0.0)
    qf(dk, [(x, y, SUBZ) for x, y in full], WD, (0, 0, 1))                     # sub-conves (so a face de cima)
    poly = ccw(outline(1.0))
    pw, n = 1.3, 36
    y_first = CY - pw * n / 2
    nt = 0
    for k in range(n):
        y0 = y_first + k * pw
        off = (k % 4) * 3.1 + (k % 3) * 1.3
        x = X_ST + 1.0 - off
        while x < X_TIP:
            seg = 11.0 + 2.5 * E.hsh(77, k, int(x))
            a, b = max(x, X_ST + 1.0), x + seg
            x = b
            r = (a + 0.06, y0 + 0.06, b - 0.06, y0 + pw - 0.06)
            if r[2] - r[0] < 0.4:
                continue
            if all(_in_dais_poly(px, py) for px in (r[0], r[2]) for py in (r[1], r[3])):
                continue                                                         # escondida sob o degrau da torre
            pc = L.clip_rect(poly, r)
            if len(pc) >= 3 and L.area(pc) > 0.05:
                qf(dk, [(px, py, DZ) for px, py in ccw(pc)], WM, (0, 0, 1))
                nt += 1
    # borda escura (trincaniz) entre as tabuas e o costado: aparece nos portalos e na popa aberta
    for s in (-1, 1):
        xs = [x for x in OUT_XS if hb(x) > 0.05]
        for xa, xb in zip(xs, xs[1:]):
            pa, pb = (xa, CY + s * hb(xa)), (xb, CY + s * hb(xb))
            qa = (xa, CY + s * max(0.0, hb(xa) - 1.0))
            qb = (xb, CY + s * max(0.0, hb(xb) - 1.0))
            qf(dk, [(p[0], p[1], DZ) for p in (pa, pb, qb, qa)], WD, (0, 0, 1))
    qf(dk, [(X_ST, CY - HB_ST + 1.0, DZ), (X_ST + 1.0, CY - HB_ST + 1.0, DZ), (X_ST + 1.0, CY + HB_ST - 1.0, DZ),
            (X_ST, CY + HB_ST - 1.0, DZ)], WD, (0, 0, 1))
    # testa do conves (face vertical) onde nao ha amurada: portalos e popa aberta
    for s in (-1, 1):
        o0, o1 = OPEN_X[s]
        xs = [o0] + [x for x in OUT_XS if o0 < x < o1] + [o1]
        for xa, xb in zip(xs, xs[1:]):
            ya, yb = CY + s * hb(xa), CY + s * hb(xb)
            qf(dk, [(xa, ya, T1 - 0.25), (xb, yb, T1 - 0.25), (xb, yb, DZ), (xa, ya, DZ)], WD, (0, s, 0))
    qf(dk, [(X_ST, STERN_OPEN[0], T1 - 0.25), (X_ST, STERN_OPEN[1], T1 - 0.25), (X_ST, STERN_OPEN[1], DZ),
            (X_ST, STERN_OPEN[0], DZ)], WD, (-1, 0, 0))
    return nt


# ------------------------------------------------------------------ amuradas (costado, cinta, capa, guarda-corpo)
def _normals(pts):
    """normal PARA DENTRO do casco em cada ponto da polilinha (meia-esquadria)"""
    segn = []
    for a, b in zip(pts, pts[1:]):
        d = Vector((b[0] - a[0], b[1] - a[1]))
        d.normalize()
        nl = Vector((-d.y, d.x))
        m = (Vector(a) + Vector(b)) / 2
        if not in_hull(m.x + nl.x * 0.3, m.y + nl.y * 0.3):
            nl = -nl
        segn.append(nl)
    out = []
    for i in range(len(pts)):
        if i == 0:
            n = segn[0]
        elif i == len(pts) - 1:
            n = segn[-1]
        else:
            n = segn[i - 1] + segn[i]
            n.normalize()
            c = max(0.5, n.dot(segn[i]))
            n = n / c
        out.append(n)
    return out


def wall_runs():
    """polilinhas das amuradas (2D, de fora): popa+quartel de cada bordo (ate o portalo) e bordo de proa (do portalo
    ate a roda)"""
    runs = []
    for s in (-1, 1):
        o0, o1 = OPEN_X[s]
        ys = STERN_OPEN[0] if s < 0 else STERN_OPEN[1]
        aft = [(X_ST, ys), (X_ST, CY + s * HB_ST)] + [(x, CY + s * hb(x)) for x in OUT_XS if X_ST < x < o0] + \
              [(o0, CY + s * hb(o0))]
        fore = [(o1, CY + s * hb(o1))] + [(x, CY + s * hb(x)) for x in OUT_XS if o1 < x <= X_WEND]
        runs += [(s, "aft", aft), (s, "fore", fore)]
    return runs


def wall(sh, pts):
    N = _normals(pts)
    O = [Vector(p) for p in pts]
    I = [o + n * BW_T for o, n in zip(O, N)]
    for i in range(len(pts) - 1):
        o0, o1, i0, i1 = O[i], O[i + 1], I[i], I[i + 1]
        n = (N[i] + N[i + 1]).normalized()
        out = Vector((-n.x, -n.y, 0.0))
        w0, w1 = o0 - N[i] * 0.14, o1 - N[i + 1] * 0.14
        c0, c1 = o0 - N[i] * 0.14, o1 - N[i + 1] * 0.14
        k0, k1 = i0 + N[i] * 0.14, i1 + N[i + 1] * 0.14

        def V(p, z):
            return (p.x, p.y, z)
        qf(sh, [V(o0, T1 - 0.4), V(o1, T1 - 0.4), V(o1, WL0), V(o0, WL0)], HULL, out)
        qf(sh, [V(o0, WL1), V(o1, WL1), V(o1, BW_TOP), V(o0, BW_TOP)], HULL, out)
        qf(sh, [V(w0, WL0), V(w1, WL0), V(w1, WL1), V(w0, WL1)], LACQ, out)                 # cinta vermelha
        qf(sh, [V(o0, WL0), V(o1, WL0), V(w1, WL0), V(w0, WL0)], LACQ, (0, 0, -1))
        qf(sh, [V(o0, WL1), V(o1, WL1), V(w1, WL1), V(w0, WL1)], LACQ, (0, 0, 1))
        qf(sh, [V(c0, CAP_Z), V(c1, CAP_Z), V(k1, CAP_Z), V(k0, CAP_Z)], WD, (0, 0, 1))      # capa
        qf(sh, [V(c0, BW_TOP), V(c1, BW_TOP), V(c1, CAP_Z), V(c0, CAP_Z)], WD, out)
        qf(sh, [V(k0, BW_TOP), V(k1, BW_TOP), V(k1, CAP_Z), V(k0, CAP_Z)], WD, -out)
        qf(sh, [V(i0, DZ - 0.05), V(i1, DZ - 0.05), V(i1, BW_TOP), V(i0, BW_TOP)], WM, -out)  # forro (face interna)
    for j, sg in ((0, -1), (len(pts) - 1, 1)):                                           # topos das pontas
        a, b = (pts[1], pts[0]) if j == 0 else (pts[-2], pts[-1])
        t = Vector((b[0] - a[0], b[1] - a[1], 0.0)).normalized()
        o, i_ = O[j], I[j]
        qf(sh, [(o.x, o.y, T1 - 0.4), (i_.x, i_.y, T1 - 0.4), (i_.x, i_.y, BW_TOP), (o.x, o.y, BW_TOP)], HULL, t)
    return O, I, N


def rail(sh, O, N, posts=True):
    """guarda-corpo vermelho vazado sobre a capa: pilaretes a <= 3,3 + corrimao + travessa"""
    C = [o + n * (BW_T / 2) for o, n in zip(O, N)]
    zm = (CAP_Z + RAIL_Z) / 2
    for a, b in zip(C, C[1:]):
        if (b - a).length < 0.05:
            continue
        sh.beam((a.x, a.y, RAIL_Z - 0.13), (b.x, b.y, RAIL_Z - 0.13), 0.36, 0.26, LACQ, 0.0)
        sh.beam((a.x, a.y, zm), (b.x, b.y, zm), 0.16, 0.16, LACQ, 0.0)
    if not posts:
        return
    total = sum((b - a).length for a, b in zip(C, C[1:]))
    n = max(1, int(math.ceil(total / 3.3)))
    marks = [total * k / n for k in range(n + 1)]
    acc, mi = 0.0, 0
    for a, b in zip(C, C[1:]):
        ln = (b - a).length
        while mi < len(marks) and marks[mi] <= acc + ln + 1e-6:
            p = a.lerp(b, (marks[mi] - acc) / ln if ln > 1e-6 else 0.0)
            sh.box((0.34, 0.34, RAIL_Z - CAP_Z), (p.x, p.y, (CAP_Z + RAIL_Z) / 2), (0, 0, 0), LACQ, 0.0)
            mi += 1
        acc += ln


def wall_col(pts, N, tol=0.3):
    """guarda da amurada: caixas em CORDA do costado ao forro, de T1-0,5 ate COL_TOP; a corda cresce enquanto a
    polilinha fica a <= tol dela (nada da capa/corrimao fica fora: gate 'visual'); nas pontas da polilinha a caixa passa
    0,7 (cobre o cabeco do portalo)"""
    O = [Vector(p) for p in pts]
    i = 0
    while i < len(O) - 1:
        j = i + 1
        while j < len(O) - 1:
            a, b = O[i], O[j + 1]
            u = (b - a).normalized()
            dev = max(abs((O[k] - a).cross(u)) if hasattr((O[k] - a), "cross") else 0.0 for k in range(i + 1, j + 1))
            if dev > tol or (b - a).length > 20.0:
                break
            j += 1
        a, b = O[i], O[j]
        n = (N[i] + N[j]).normalized()
        d = b - a
        u = d.normalized()
        a = a - u * (0.7 if i == 0 else 0.3)
        b = b + u * (0.7 if j == len(O) - 1 else 0.3)
        c = (a + b) / 2 + n * 0.3
        d = b - a
        col_box("OPSumShip", (d.length, 1.6, COL_TOP - (T1 - 0.5)),
                (c.x, c.y, (COL_TOP + T1 - 0.5) / 2), (0, 0, math.atan2(d.y, d.x)))
        i = j


def bulwarks(sh):
    ends = []
    for s, kind, pts in wall_runs():
        O, I, N = wall(sh, pts)
        rail(sh, O, N)
        wall_col(pts, N)
        ends.append((s, kind, pts, N))
    # quebra-mar (V atravessando o conves antes do bico da proa): ninguem chega a guarda invisivel da borda
    yw = hb(201.0) - BW_T
    legs = [((201.0, CY - yw), (X_BRK, CY)), ((201.0, CY + yw), (X_BRK, CY))]
    for a, b in legs:
        sh.beam((a[0], a[1], (T1 - 0.3 + BW_TOP + 0.2) / 2), (b[0], b[1], (T1 - 0.3 + BW_TOP + 0.2) / 2), 0.55,
                BW_TOP + 0.2 - (T1 - 0.3), HULL, 0.0)
        sh.beam((a[0], a[1], BW_TOP + 0.28), (b[0], b[1], BW_TOP + 0.28), 0.8, 0.16, WD, 0.0)
        sh.beam((a[0], a[1], WL0 + 0.15), (b[0], b[1], WL0 + 0.15), 0.75, 0.3, LACQ, 0.0)
        d = Vector((b[0] - a[0], b[1] - a[1]))
        col_box("OPSumShip", (d.length + 0.6, 0.9, COL_TOP - (T1 - 0.5)),
                ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (COL_TOP + T1 - 0.5) / 2), (0, 0, math.atan2(d.y, d.x)))
    # bico da proa alem da borda do terraco (x > 206: sem piso do op_col embaixo) - o gate 'visual' pede colisao sob
    # todo tabuado ao alcance; atras da guarda de 8,5 da borda ninguem chega la (e so o 'chao' das tabuas)
    for x0, x1 in ((205.5, 210.0), (210.0, 214.6)):
        w = hb(x0)
        col_box("OPSumShip", (x1 - x0, 2 * w, 0.6), ((x0 + x1) / 2, CY, T1 - 0.2))
    # pilaretes de portalo (cabecos) nas pontas das amuradas abertas: popa e portalos de bordo
    lamps = []
    for s in (-1, 1):
        for x in OPEN_X[s]:
            y = CY + s * (hb(x) - 0.3)
            bitt(sh, x, y)
        ys = STERN_OPEN[0] if s < 0 else STERN_OPEN[1]
        lamps.append(bitt(sh, X_ST + 0.3, ys, lamp=True))
    return lamps


def bitt(sh, x, y, lamp=False):
    """cabeco de portalo: poste quadrado escuro com colar de ferro e chapeu; 'lamp' = lanterna de popa no topo"""
    h = 4.4 if lamp else 3.35
    sh.box((1.0, 1.0, h + 0.4), (x, y, T1 - 0.2 + (h + 0.4) / 2), (0, 0, 0), WD, 0.0)
    sh.box((1.16, 1.16, 0.3), (x, y, T1 + 1.0), (0, 0, 0), IRON, 0.0)
    sh.box((1.16, 1.16, 0.3), (x, y, T1 + h - 0.6), (0, 0, 0), IRON, 0.0)
    if not lamp:                                  # (colisao: a ponta estendida da guarda da amurada, ate COL_TOP)
        K.lathe(sh, F0, (x, y, T1 + h), [(0.62, 0.0), (0.62, 0.16), (0.3, 0.5), (0.05, 0.72)], 6, GOLD)
        return None
    col_box("OPSumShip", (1.5, 1.5, h + 3.4), (x, y, T1 - 0.5 + (h + 3.4) / 2))
    return ship_lantern(sh, x, y, T1 + h)


def ship_lantern(sh, x, y, z, s=1.0):
    """lanterna de navio: base de ferro, 4 montantes, vidro aceso, chapeu de 4 aguas e argola. Devolve o centro"""
    hx, hz = 0.55 * s, 1.3 * s
    sh.box((1.3 * s, 1.3 * s, 0.22), (x, y, z + 0.11), (0, 0, 0), IRON, 0.0)
    sh.box((2 * hx - 0.16, 2 * hx - 0.16, hz), (x, y, z + 0.22 + hz / 2), (0, 0, 0), LGLOW, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sh.box((0.16, 0.16, hz), (x + sx * hx, y + sy * hx, z + 0.22 + hz / 2), (0, 0, 0), IRON, 0.0)
    zt = z + 0.22 + hz
    K.lathe(sh, F0, (x, y, zt), [(0.85 * s, 0.0), (0.85 * s, 0.12), (0.2 * s, 0.6 * s), (0.08 * s, 0.75 * s)], 4, IRON,
            rot=math.pi / 4)
    sh.rod(Vector((x, y, zt + 0.75 * s)), Vector((x, y, zt + 1.0 * s)), 0.1, IRON, 4)
    return Vector((x, y, z + 0.22 + hz / 2))


# ------------------------------------------------------------------ proa: casco sobre o porto, roda, carranca
def bow(sh):
    """costado da PROA abaixo do conves (x >= 203: so aparece fora da falesia, sobre o porto), roda de proa, ancora"""
    xs = [203.0, 205.0, 207.0, 209.0, 210.6, 212.0, 213.2, X_WEND]

    def zb(x):
        return T1 - 13.0 * ((X_TIP - x) / 12.0) ** 0.65

    rings = []
    for x in xs:
        w, z0, z1 = hb(x), T1 - 0.4, zb(x)
        prof = [(w, z0), (w * 0.93, z0 + (z1 - z0) * 0.35), (w * 0.68, z0 + (z1 - z0) * 0.7), (w * 0.3, z1 + 0.25),
                (0.0, z1)]
        ring = [(x, CY - y, z) for y, z in prof[:-1]] + [(x, CY, prof[-1][1])] + \
               [(x, CY + y, z) for y, z in reversed(prof[:-1])]
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        za = (T1 - 0.4 + ra[len(ra) // 2][2]) / 2
        for j in range(len(ra) - 1):
            q = [ra[j], ra[j + 1], rb[j + 1], rb[j]]
            c = Vector(sum((Vector(p) for p in q), Vector()) / 4)
            qf(sh, q, HULL, (0.0, c.y - CY, c.z - za))
    for j in (1, 2, len(rings[0]) - 3, len(rings[0]) - 2):         # 2 fiadas escuras por bordo
        pts = [Vector(r[j]) + Vector((0.0, (0.12 if r[j][1] > CY else -0.12), 0.0)) for r in rings]
        tube(sh, pts, 0.16, WD, n=4)
    # roda de proa (escura) da quilha ate o pe da carranca + cinta vermelha que fecha na roda
    stem = [(206.0, CY, zb(206.0) - 0.3), (209.5, CY, zb(209.5) - 0.2), (212.4, CY, zb(212.4) - 0.1),
            (214.2, CY, T1 - 1.6), (215.2, CY, T1 + 0.8), (215.9, CY, T1 + 3.4)]
    for a, b in zip(stem, stem[1:]):
        sh.beam(a, b, 1.1, 1.1, WD, 0.0)
    # ancora no turco de bombordo (pendurada no costado, por fora da falesia)
    xa = 208.4
    ya = CY - hb(xa) - 0.45
    t = math.atan2(-(hb(xa + 0.5) - hb(xa - 0.5)), 1.0)            # tangente do costado (bombordo)
    Fa = Frame(xa, ya, 0.0, t)
    z_top = CAP_Z - 0.2
    K.beam(sh, Fa, (0.0, 0.0, z_top), (0.0, 0.0, z_top - 5.0), 0.34, 0.34, IRON)              # haste
    K.beam(sh, Fa, (-1.5, 0.0, z_top - 0.6), (1.5, 0.0, z_top - 0.6), 0.3, 0.3, WD)          # cepo
    K.lathe_y(sh, Fa, (0.0, 0.0, z_top + 0.35), [(0.5, -0.08), (0.5, 0.08)], 8, IRON)          # argola
    zc = z_top - 5.0
    for sg in (-1, 1):
        K.beam(sh, Fa, (0.0, 0.0, zc), (sg * 1.3, 0.0, zc + 0.6), 0.32, 0.32, IRON)
        K.beam(sh, Fa, (sg * 1.3, 0.0, zc + 0.6), (sg * 1.9, 0.0, zc + 1.8), 0.32, 0.32, IRON)
        K.bx(sh, Fa, sg * 1.75, 0.0, zc + 1.45, 0.9, 0.2, 0.9, IRON, rz=0.0, ry=sg * 0.5)       # pata
    c_ = Fa.p(0.0, 0.0, (z_top + 0.6 + zc) / 2)
    col_box("OPSumShip", (4.2, 0.9, z_top + 0.6 - zc + 0.4), (c_.x, c_.y, c_.z), (0, 0, t))


def lion(sh):
    """CARRANCA de leao (estilo Thousand Sunny, sem texto): juba-sol de 16 raios em 2 comprimentos, cabeca redonda
    amarela, focinho, nariz e olhos escuros, sorriso, orelhas. Olha para o MAR (+x) e levanta 18 graus (le de cima e
    das pontes); de tras (do conves) a juba le como um sol."""
    C = Vector((216.6, CY, T1 + 5.4))
    tl = math.radians(18.0)
    A = Vector((math.cos(tl), 0.0, math.sin(tl)))             # frente
    B = Vector((-math.sin(tl), 0.0, math.cos(tl)))            # cima
    S_ = Vector((0.0, 1.0, 0.0))                               # lado

    def W(a, b, s):
        return C + A * a + B * b + S_ * s
    nr = 16
    for i in range(nr):
        ph = 2 * math.pi * i / nr + math.pi / nr
        r0, r1 = 2.6, (5.9 if i % 2 == 0 else 4.9)
        hw = math.pi / nr * 0.98
        pts = []
        for da, rr, dph in ((-0.9, r0, -hw), (-0.9, r0, hw), (-0.9, r1, 0.0), (0.5, r0 - 0.1, -hw * 0.9),
                            (0.5, r0 - 0.1, hw * 0.9), (0.5, r1 - 0.7, 0.0)):
            pts.append(W(da, rr * math.cos(ph + dph), rr * math.sin(ph + dph)))
        b0, b1, b2, f0, f1, f2 = pts
        cen = W(-0.2, 0.0, 0.0)
        for q in ((b0, b2, b1), (f0, f1, f2), (b0, b1, f1, f0), (b1, b2, f2, f1), (b2, b0, f0, f2)):
            c = sum((Vector(p) for p in q), Vector()) / len(q)
            hint = (c - cen) if len(q) == 4 else (A if q[0] is f0 else -A)
            qf(sh, q, MANE, hint)
    # disco da juba por tras da cabeca (fecha o miolo dos raios)
    K.loft(sh, F0, [[tuple(W(-0.95, 2.75 * math.cos(-2 * math.pi * j / 16), 2.75 * math.sin(-2 * math.pi * j / 16)))
                     for j in range(16)],
                    [tuple(W(0.45, 2.75 * math.cos(-2 * math.pi * j / 16), 2.75 * math.sin(-2 * math.pi * j / 16)))
                     for j in range(16)]], MANE)
    rot = (0.0, -tl, 0.0)
    sh.ico(2.75, tuple(W(1.0, 0.0, 0.0)), LFACE, 2, scale=(0.82, 1.0, 0.94), rot=rot)            # cabeca
    sh.ico(1.4, tuple(W(2.55, -0.8, 0.0)), LFACE, 1, scale=(0.6, 1.3, 0.8), rot=rot)             # focinho
    sh.ico(0.6, tuple(W(3.3, -0.2, 0.0)), WD, 1, scale=(0.8, 1.2, 0.75), rot=rot)                 # nariz
    for sg in (-1, 1):
        sh.ico(0.46, tuple(W(2.62, 0.95, sg * 1.2)), WD, 1, scale=(0.6, 1.0, 1.25), rot=rot)      # olhos
        sh.beam(tuple(W(2.55, 1.75, sg * 0.55)), tuple(W(2.3, 1.95, sg * 1.75)), 0.26, 0.26, MANE, 0.0)  # sobrancelhas
        sh.ico(0.85, tuple(W(1.2, 2.25, sg * 1.95)), MANE, 1, scale=(0.6, 1.0, 1.0), rot=rot)      # orelhas
    sm = [W(3.3 - 0.45 * (k / 3.0) ** 2, -1.8 + 0.42 * (k / 3.0) ** 2, 1.35 * k / 3.0) for k in range(-3, 4)]
    tube(sh, sm, 0.13, WD, n=4)                                                                     # sorriso


# ------------------------------------------------------------------ mastros laterais, velas e Jolly Roger
def spar(mb, a, b, r0, r1, m, n=10):
    """verga/mastro afinando de r0 (em a) a r1 (em b) (linguagem do op_ship)"""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    e1 = d.cross(up).normalized()
    e2 = d.cross(e1).normalized()
    rings = []
    for p, r in ((a, r0), (b, r1)):
        rings.append([tuple(p + (e1 * math.cos(2 * math.pi * j / n) + e2 * math.sin(2 * math.pi * j / n)) * r)
                      for j in range(n)])
    K.loft(mb, F0, rings, m)


def rope(mb, a, b, r=0.1):
    mb.rod(Vector(a), Vector(b), r, ROPE, 4, caps=False)


def _circle(cx, cz, r, n=28, rz=None):
    rz = r if rz is None else rz
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + rz * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _bar(a, b, hw):
    ax, az = a
    bx_, bz = b
    dx, dz = bx_ - ax, bz - az
    ln = math.hypot(dx, dz)
    nx, nz = -dz / ln * hw, dx / ln * hw
    return [(ax - nx, az - nz), (bx_ - nx, bz - nz), (bx_ + nx, bz + nz), (ax + nx, az + nz)]


def _rrect(cx, cz, w, h, r, n=4):
    out = []
    for qx, qz, a0 in ((1, -1, -math.pi / 2), (1, 1, 0.0), (-1, 1, math.pi / 2), (-1, -1, math.pi)):
        ccx, ccz = cx + qx * (w / 2 - r), cz + qz * (h / 2 - r)
        for k in range(n + 1):
            a = a0 + (math.pi / 2) * k / n
            out.append((ccx + r * math.cos(a), ccz + r * math.sin(a)))
    return out


def _dome(cx, z0, hw, h, n=14):
    return [(cx + hw * math.cos(math.pi * i / n), z0 + h * math.sin(math.pi * i / n)) for i in range(n + 1)]


def emblem_shapes(k=1.0):
    """Jolly Roger dos Chapeus de Palha (MESMO desenho aprovado do op_ship): camadas (indice, material, poligono
    convexo em (x, z) com a caveira na origem)"""
    S = []
    sc = lambda P_: [(x * k, z * k) for x, z in P_]
    bones = []
    for sgn in (1, -1):
        a = math.radians(32.0) * sgn
        ux, uz = math.cos(a), math.sin(a)
        c = (0.0, -1.3)
        A = (c[0] - ux * 6.4, c[1] - uz * 6.4)
        Bp = (c[0] + ux * 6.4, c[1] + uz * 6.4)
        knobs = []
        for e, sg in ((A, -1), (Bp, 1)):
            for o in (-0.66, 0.66):
                knobs.append((e[0] + ux * sg * 0.45 - uz * o, e[1] + uz * sg * 0.45 + ux * o))
        bones.append((A, Bp, knobs))
    for A, Bp, knobs in bones:
        S.append((1, CB, sc(_bar(A, Bp, 0.85))))
        for q in knobs:
            S.append((1, CB, sc(_circle(q[0], q[1], 1.16, 10))))
    for A, Bp, knobs in bones:
        S.append((2, CW, sc(_bar(A, Bp, 0.55))))
        for q in knobs:
            S.append((2, CW, sc(_circle(q[0], q[1], 0.86, 10))))
    S.append((3, CB, sc(_circle(0.0, 0.9, 3.42, 20))))
    S.append((3, CB, sc(_rrect(0.0, -1.75, 4.24, 3.24, 0.9, 3))))
    S.append((4, CW, sc(_circle(0.0, 0.9, 3.1, 20))))
    S.append((4, CW, sc(_rrect(0.0, -1.75, 3.6, 2.6, 0.6, 3))))
    for sx in (-1, 1):
        S.append((5, CB, sc(_circle(sx * 1.25, 0.15, 0.88, 10, 1.02))))
    S.append((5, CB, sc([(0.0, -1.45), (0.36, -0.75), (-0.36, -0.75)])))
    S.append((5, CB, sc(_bar((-1.3, -2.15), (1.3, -2.15), 0.08))))
    for x in (-0.65, 0.0, 0.65):
        S.append((5, CB, sc(_bar((x, -2.8), (x, -1.6), 0.08))))
    S.append((5, CB, sc(_circle(0.0, 2.75, 4.78, 20, 1.08))))
    S.append((5, CB, sc(_dome(0.0, 2.75, 2.83, 2.63, 10))))
    S.append((6, CST, sc(_circle(0.0, 2.75, 4.5, 20, 0.8))))
    S.append((6, CST, sc(_dome(0.0, 2.75, 2.55, 2.35, 10))))
    hw = lambda z: 2.55 * math.sqrt(max(0.0, 1.0 - ((z - 2.75) / 2.35) ** 2))
    za, zz = 3.0, 3.75
    S.append((7, CR, sc([(-hw(za), za), (hw(za), za), (hw(zz), zz), (-hw(zz), zz)])))
    return S


def fan(mb, pts, m, hint, center=None):
    bm = mb.bm
    c = Vector(center) if center is not None else sum((Vector(p) for p in pts), Vector()) / len(pts)
    vc = bm.verts.new(c)
    vs = [bm.verts.new(Vector(p)) for p in pts]
    hint = Vector(hint)
    for i in range(len(vs)):
        f = bm.faces.new((vc, vs[i], vs[(i + 1) % len(vs)]))
        f.normal_update()
        if f.normal.dot(hint) < 0:
            f.normal_flip()
    mb._post([vc] + vs, m, None, 0, 1)


def sail(mb, Fm, z_top, H, Wt, Wb, y0=1.35, belly_k=0.1, roach=0.6, emblem=True):
    """VELA REDONDA presa na verga (linguagem do op_ship), no referencial Fm do mastro: x local = ao longo da verga,
    +y local = lado de quem chega da praca (oeste: o bojo e o desenho viram para a praca). Casca de 2 faces 0,18,
    panos verticais, esteira arqueada, tralha de cabo; Jolly Roger recortada nas 2 faces."""
    npan, nv = 6, 6
    nu = 2 * npan
    t = 0.18
    belly = belly_k * H

    def S(u, v):
        W_ = Wt + (Wb - Wt) * v
        x = u * W_ / 2.0
        z = z_top - v * H + roach * (1.0 - u * u) * v ** 3
        g = math.sin(0.8 * math.pi * v)
        seam = 0.07 * (0.3 + g) * math.cos(u * npan * math.pi)
        y = y0 + belly * g * (1.0 - 0.55 * u * u) + seam
        return Vector((x, y, z))

    def Wp(p):
        return Vector(Fm.p(p.x, p.y, p.z))
    wy = Vector(Fm.p(0.0, 1.0, 0.0)) - Vector(Fm.p(0.0, 0.0, 0.0))
    bm = mb.bm
    for side in (1, -1):
        G = [[bm.verts.new(Wp(S(-1.0 + 2.0 * i / nu, j / nv) + Vector((0, side * t / 2, 0)))) for j in range(nv + 1)]
             for i in range(nu + 1)]
        fs = []
        for i in range(nu):
            for j in range(nv):
                f = bm.faces.new((G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]))
                f.normal_update()
                if f.normal.dot(wy * side) < 0:
                    f.normal_flip()
                fs.append(f)
        mb._post([v for col in G for v in col], SAIL, None, 0, 1)
    for e in ([S(-1.0 + 2.0 * i / nu, 1.0) for i in range(0, nu + 1, 2)], [S(-1.0, j / nv) for j in range(nv + 1)],
              [S(1.0, j / nv) for j in range(nv + 1)]):
        tube(mb, [Wp(p) for p in e], 0.14, ROPE, n=4)
    if emblem:
        k = H / 14.5
        zc = z_top - 0.5 * H
        gap = 0.2

        def on_sail(ex, ez, side, layer):
            exs = ex * side
            z = zc + ez
            v = (z_top - z) / H
            W_ = Wt + (Wb - Wt) * v
            p = S(exs / (W_ / 2.0), v)
            p.y += side * (t / 2.0 + gap * layer)
            return p

        def pieces(poly):
            if len(poly) != 4:
                return [poly]
            a, b, c, d = [Vector((x, z, 0.0)) for x, z in poly]
            n = int(math.ceil((b - a).length / (1.6 * k)))
            if n <= 1:
                return [poly]
            return [[(q.x, q.y) for q in (a.lerp(b, i / n), a.lerp(b, (i + 1) / n), d.lerp(c, (i + 1) / n),
                                          d.lerp(c, i / n))] for i in range(n)]
        for side in (1, -1):
            for layer, m, poly0 in emblem_shapes(k):
                for poly in pieces(poly0):
                    pts = [Wp(on_sail(ex, ez, side, layer)) for ex, ez in poly]
                    ce = (sum(q[0] for q in poly) / len(poly), sum(q[1] for q in poly) / len(poly))
                    fan(mb, pts, m, wy * side, Wp(on_sail(ce[0], ce[1], side, layer)))
    return [Wp(S(-1.0, 1.0)), Wp(S(1.0, 1.0))]


def flag(mb, Ff, z, w, h, cloth=CB, waves=3, amp=0.45):
    """bandeira ondulada (casca de 2 faces) presa ao mastro (canto de cima em z), voando para +x local, com a Jolly
    Roger em miniatura nas 2 faces (linguagem do op_ship.flag)"""
    nu, nv, t = 6, 2, 0.1

    def Pl(u, v):
        return Vector((0.2 + u * w, amp * math.sin(u * waves * math.pi) * u, z - v * h))

    def Wp(p):
        return Vector(Ff.p(p.x, p.y, p.z))
    wy = Vector(Ff.p(0.0, 1.0, 0.0)) - Vector(Ff.p(0.0, 0.0, 0.0))
    bm = mb.bm
    for side in (1, -1):
        G = [[bm.verts.new(Wp(Pl(i / nu, j / nv) + Vector((0, -side * t / 2, 0)))) for j in range(nv + 1)]
             for i in range(nu + 1)]
        for i in range(nu):
            for j in range(nv):
                f = bm.faces.new((G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]))
                f.normal_update()
                if f.normal.dot(-wy * side) < 0:
                    f.normal_flip()
        mb._post([v for c in G for v in c], cloth, None, 0, 1)
    for side in (1, -1):
        for layer, m, poly in ((1, CW, _bar((-0.9, -0.75), (0.9, 0.25), 0.13)),
                               (1, CW, _bar((-0.9, 0.25), (0.9, -0.75), 0.13)),
                               (2, CW, _circle(0.0, 0.05, 0.5, 12)),
                               (3, CST, _circle(0.0, 0.42, 0.62, 10, 0.14))):
            pts = []
            for ex, ez in poly:
                u = (0.5 * w + ex * side) / w
                p = Pl(u, 0.5) + Vector((0, 0, ez))
                p.y -= side * (t / 2.0 + 0.1 * layer)
                pts.append(Wp(p))
            fan(mb, pts, m, -wy * side)


def rig(sh, sl):
    """2 mastros laterais (um por bordo, ao lado da torre) com cesto, verga, vela redonda com a Jolly Roger virada
    para a praca, mastareu com bandeira preta e cordame (ovens com enfrechates ate a amurada, estai ate a roda de proa,
    brandal ate o bordo de re). sh = madeira/cabo, sl = velas e bandeiras (normais calculadas)."""
    for mx, my, s in SAIL_MASTS:
        K.lathe(sh, F0, (mx, my, DZ - 0.05), [(1.35, 0.0), (1.35, 0.35), (1.0, 0.55)], 8, WD)      # colar
        spar(sh, (mx, my, DZ), (mx, my, MAST_TOP), 0.82, 0.62, WD, 10)
        for z in (T1 + 6.0, T1 + 13.0, T1 + 20.0):
            K.lathe(sh, F0, (mx, my, z), [(0.95, 0.0), (0.95, 0.4)], 10, IRON, caps=(False, False))
        zn = T1 + 26.4                                                                              # cesto da gavea
        K.lathe(sh, F0, (mx, my, zn), [(0.9, -0.5), (1.85, 0.0), (1.95, 0.1), (1.95, 1.8), (2.05, 1.9), (2.05, 2.1),
                                       (1.75, 2.1), (1.75, 0.35), (0.7, 0.35)], 12, WM)
        spar(sh, (mx, my, MAST_TOP - 2.0), (mx, my, MAST_TOP + 5.0), 0.45, 0.3, WD, 8)              # mastareu
        K.lathe(sh, F0, (mx, my, MAST_TOP + 5.0), [(0.38, 0.0), (0.42, 0.22), (0.24, 0.5)], 8, GOLD)
        col_box("OPSumShip", (2.8, 2.8, 9.0), (mx, my, T1 + 4.5))         # cobre o colar
        Fm = Frame(mx, my, 0.0, YAW)                      # x local = +y do mundo (verga), +y local = oeste (praca)
        yl = 15.4
        a, b = Vector(Fm.p(-yl / 2, 0.75, YARD_Z)), Vector(Fm.p(yl / 2, 0.75, YARD_Z))
        c = (a + b) / 2
        spar(sh, c, a, 0.42, 0.24, WD, 8)
        spar(sh, c, b, 0.42, 0.24, WD, 8)
        sh.box((1.1, 1.1, 0.9), tuple(Vector(Fm.p(0.0, 0.5, YARD_Z))), (0, 0, YAW), WD, 0.0)            # troco
        clews = sail(sl, Fm, YARD_Z - 0.4, YARD_Z - 0.4 - SAIL_FOOT, yl - 2.2, yl - 0.8)
        for p_ in (a, b):                                                                              # amantilhos
            rope(sh, (mx, my, MAST_TOP - 1.2), (p_.x, p_.y, p_.z + 0.2), 0.08)
        for cl_ in clews:                                                                              # escotas
            x = cl_.x + 1.6
            if (cl_.y - my) * s > 0:                      # punho de fora -> capa da amurada
                rope(sh, cl_, (x, CY + s * (hb(x) - BW_T / 2), CAP_Z + 0.05), 0.09)
            else:                                         # punho de dentro -> malagueta no conves
                rope(sh, cl_, (x, cl_.y, DZ + 0.9), 0.09)
                sh.box((0.5, 0.5, 0.9), (x, cl_.y, DZ + 0.45), (0, 0, 0), WD, 0.0)
        # ovens (3) do cesto ate a capa da amurada do mesmo bordo, com enfrechates
        head = Vector((mx, my + s * 0.6, zn - 0.6))
        feet = []
        for dx in (-3.2, 0.0, 3.2):
            x = mx + dx
            feet.append(Vector((x, CY + s * (hb(x) - BW_T / 2), CAP_Z + 0.05)))
        for f_ in feet:
            rope(sh, f_, head, 0.11)
            sh.box((0.5, 0.5, 0.3), (f_.x, f_.y, CAP_Z + 0.15), (0, 0, 0), WD, 0.0)                  # bigota
        z = CAP_Z + 2.2
        while z < head.z - 3.0:
            q = [f_.lerp(head, (z - f_.z) / (head.z - f_.z)) for f_ in feet]
            for p_, q_ in zip(q, q[1:]):
                rope(sh, p_, q_, 0.06)
            z += 2.5
        rope(sh, (mx, my, MAST_TOP + 3.6), (215.3, CY, T1 + 3.0), 0.1)                               # estai (proa)
        xb = 152.0
        rope(sh, (mx, my, MAST_TOP + 3.2), (xb, CY + s * (hb(xb) - BW_T / 2), CAP_Z + 0.1), 0.1)      # brandal
        Ff = Frame(mx, my, 0.0, math.pi)                  # bandeira voando para OESTE (vento do mar)
        flag(sl, Ff, MAST_TOP + 4.6, 4.4, 2.9)


# ------------------------------------------------------------------ timao, rosa-dos-ventos, escotilhas, cabrestante
def helm(sh):
    """TIMAO grande na popa (bombordo): estrado de 1 degrau, coluna, aro de 16 lados com 8 raios que passam do aro
    como punhos; o timoneiro fica a re (oeste) olhando a proa"""
    x, y = HELM
    sh.box((1.0, 1.2, 2.75), (x + 0.55, y, DZ + 1.375), (0, 0, 0), WM, 0.0)
    sh.box((1.5, 1.7, 0.3), (x + 0.55, y, DZ + 0.15), (0, 0, 0), WD, 0.0)
    sh.box((1.2, 1.4, 0.25), (x + 0.55, y, DZ + 2.85), (0, 0, 0), WD, 0.0)
    zc = DZ + 3.05
    cx = x - 0.05
    R = 2.0
    Fw = Frame(cx, y, zc, 0.0)
    ring = [(0.0, R * math.cos(2 * math.pi * j / 16), R * math.sin(2 * math.pi * j / 16)) for j in range(17)]
    tube(sh, [Fw.p(*p) for p in ring], 0.2, WM, n=6)
    sh.rod(Vector((cx - 0.35, y, zc)), Vector((cx + 0.7, y, zc)), 0.42, GOLD, 8)
    for j in range(8):
        a = 2 * math.pi * j / 8 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        sh.beam((cx, y + 0.3 * ca, zc + 0.3 * sa), (cx, y + R * ca, zc + R * sa), 0.16, 0.16, WD, 0.0)
        sh.beam((cx, y + (R + 0.1) * ca, zc + (R + 0.1) * sa), (cx, y + (R + 0.8) * ca, zc + (R + 0.8) * sa), 0.26,
                0.26, WD, 0.0)
    col_box("OPSumProp", (2.0, 6.0, 6.8), (x, y, T1 + 3.4))


def compass_rose(dk, cx, cy):
    """ROSA-DOS-VENTOS embutida no conves no lugar do jogador (SUMMON_PlayerPosition): placa redonda escura com aro
    dourado e estrela de 8 pontas bicolor (4 longas para os rumos, 4 curtas), 0,12 acima das tabuas"""
    z = DZ + 0.12
    n = 24
    R0, R1 = ROSE_R - 0.5, ROSE_R
    ring_o = [(cx + R1 * math.cos(2 * math.pi * j / n), cy + R1 * math.sin(2 * math.pi * j / n)) for j in range(n)]
    ring_i = [(cx + R0 * math.cos(2 * math.pi * j / n), cy + R0 * math.sin(2 * math.pi * j / n)) for j in range(n)]
    for j in range(n):
        k = (j + 1) % n
        qf(dk, [(*ring_o[j], z), (*ring_o[k], z), (*ring_i[k], z), (*ring_i[j], z)], GOLD, (0, 0, 1))
        qf(dk, [(*ring_o[j], DZ - 0.02), (*ring_o[k], DZ - 0.02), (*ring_o[k], z), (*ring_o[j], z)], GOLD,
           (ring_o[j][0] - cx, ring_o[j][1] - cy, 0))
    qf(dk, [(*p, z) for p in ring_i], WD, (0, 0, 1))
    zs = z + 0.12
    for i in range(8):
        a = math.pi / 4 * i
        r = R0 - 0.15 if i % 2 == 0 else 2.5
        w = 0.62 if i % 2 == 0 else 0.48
        tip = (cx + r * math.cos(a), cy + r * math.sin(a), zs)
        l_ = (cx + w * math.cos(a + math.pi / 2), cy + w * math.sin(a + math.pi / 2), zs)
        r_ = (cx + w * math.cos(a - math.pi / 2), cy + w * math.sin(a - math.pi / 2), zs)
        c = (cx, cy, zs)
        qf(dk, [c, r_, tip], GOLD, (0, 0, 1))
        qf(dk, [c, tip, l_], WM, (0, 0, 1))
    qf(dk, [(cx + 0.55 * math.cos(2 * math.pi * j / 8), cy + 0.55 * math.sin(2 * math.pi * j / 8), zs + 0.12)
            for j in range(8)], GOLD, (0, 0, 1))
    col_box("OPSumProp", (2 * ROSE_R, 2 * ROSE_R, 0.9), (cx, cy, T1 - 0.05))   # topo +0,4 rente a placa: o pe nao afunda


def hatch(sh, x, y, w, d):
    """escotilha: bracola de 0,35 (degrau) + grade escura sobre o fundo preto"""
    h = 0.35
    for (a0, a1, b0, b1) in ((x - w / 2, x + w / 2, y - d / 2, y - d / 2 + 0.35),
                             (x - w / 2, x + w / 2, y + d / 2 - 0.35, y + d / 2),
                             (x - w / 2, x - w / 2 + 0.35, y - d / 2 + 0.35, y + d / 2 - 0.35),
                             (x + w / 2 - 0.35, x + w / 2, y - d / 2 + 0.35, y + d / 2 - 0.35)):
        sh.box((a1 - a0, b1 - b0, h), ((a0 + a1) / 2, (b0 + b1) / 2, DZ + h / 2), (0, 0, 0), WD, 0.0)
    qf(sh, [(x - w / 2 + 0.35, y - d / 2 + 0.35, DZ + 0.02), (x + w / 2 - 0.35, y - d / 2 + 0.35, DZ + 0.02),
            (x + w / 2 - 0.35, y + d / 2 - 0.35, DZ + 0.02), (x - w / 2 + 0.35, y + d / 2 - 0.35, DZ + 0.02)], WD,
       (0, 0, 1))
    xs = K.even(x - w / 2 + 0.35, x + w / 2 - 0.35, 0.75)
    for xx in xs[1:-1]:
        sh.box((0.22, d - 0.7, 0.2), (xx, y, DZ + h - 0.12), (0, 0, 0), WM, 0.0)
    col_box("OPSumProp", (w, d, 1.0), (x, y, DZ + h - 0.5))           # pisa-se na bracola (o pe nao afunda)


def capstan(sh, x, y):
    K.lathe(sh, F0, (x, y, DZ), [(1.25, 0.0), (1.25, 0.35), (0.85, 0.5), (0.7, 1.4), (0.95, 1.55), (0.95, 1.85),
                                  (0.4, 2.0)], 8, WM)
    for j in range(4):
        a = math.pi / 4 * j
        sh.beam((x - 2.0 * math.cos(a), y - 2.0 * math.sin(a), DZ + 1.7), (x + 2.0 * math.cos(a), y + 2.0 * math.sin(a),
                DZ + 1.7), 0.2, 0.2, WD, 0.0)
    col_box("OPSumProp", (2.6, 2.6, 3.0), (x, y, T1 + 1.5))


# ------------------------------------------------------------------ carga: bau do tesouro, barris, canhoes, cabos
def chest(sh, x, y, ang, coins=5, seed=0):
    """BAU DO TESOURO aberto: caixa de madeira com cintas de ferro e cantoneiras douradas, tampa abaulada aberta para
    tras, monte de MOEDAS de ouro transbordando e moedas soltas no conves (discos achatados: nada de cristal)"""
    Fc = Frame(x, y, DZ, ang)
    W_, D_, H_ = 2.6, 1.6, 1.15
    K.bb(sh, Fc, -W_ / 2, W_ / 2, -D_ / 2, D_ / 2, 0.0, H_, WM)
    for xx in (-W_ / 2 + 0.35, W_ / 2 - 0.35):
        K.bb(sh, Fc, xx - 0.12, xx + 0.12, -D_ / 2 - 0.06, D_ / 2 + 0.06, -0.01, H_ + 0.04, IRON)
    K.bb(sh, Fc, -0.22, 0.22, -D_ / 2 - 0.12, -D_ / 2, H_ - 0.55, H_ - 0.05, BGOLD)                 # fechadura
    for sx in (-1, 1):
        K.bb(sh, Fc, sx * W_ / 2 - 0.2 * sx - 0.1, sx * W_ / 2 - 0.2 * sx + 0.1 + 0.12 * sx, -D_ / 2 - 0.08,
             -D_ / 2 + 0.25, 0.0, 0.3, BGOLD)
    # tampa aberta para tras (gira 105 graus na aresta de tras)
    K.bx(sh, Fc, 0.0, D_ / 2 + 0.424, H_ + 0.715, W_, D_, 0.45, WM, 0.0, rx=math.radians(-105.0))
    for xx in (-W_ / 2 + 0.35, W_ / 2 - 0.35):                                        # cintas da tampa
        K.bx(sh, Fc, xx, D_ / 2 + 0.424, H_ + 0.715, 0.26, D_ + 0.08, 0.57, IRON, 0.0, rx=math.radians(-105.0))
    K.bb(sh, Fc, -W_ / 2 - 0.04, W_ / 2 + 0.04, -D_ / 2 - 0.04, D_ / 2 + 0.04, H_ - 0.16, H_ + 0.14, BGOLD)  # friso + ouro rente
    sh.ico(1.0, tuple(Fc.p(0.0, -0.05, H_ + 0.05)), BGOLD, 1, scale=(1.2, 0.74, 0.62))               # monte de moedas
    for k, (dx, dy) in enumerate(((-0.7, -0.62), (0.45, -0.7), (0.95, -0.4))):                    # moedas na borda
        p = Fc.p(dx, dy, H_ + 0.1)
        sh.cyl(0.3, 0.09, (p.x, p.y, p.z), (0.5 + 0.2 * k, 0.3, 0.0), BGOLD, n=8, bevel=0.0)
    rng = random.Random(4100 + seed)
    for k in range(coins):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(1.3, 2.4)
        p = Fc.p(math.cos(a) * r * 0.9, -abs(math.sin(a)) * r - 0.4, 0.0)
        sh.cyl(0.32, 0.09, (p.x, p.y, DZ + 0.05), (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), 0.0), BGOLD,
               n=8, bevel=0.0)
    for k in range(2):                                                    # 2 pilhas de moedas ao lado
        p = Fc.p(W_ / 2 + 0.6, -0.6 + 0.9 * k, 0.0)
        sh.cyl(0.36, 0.3 + 0.25 * k, (p.x, p.y, DZ + (0.3 + 0.25 * k) / 2), (0, 0, 0), BGOLD, n=8, bevel=0.0)
    c = Fc.p(0.0, 0.35, 0.0)
    col_box("OPSumProp", (W_ + 0.4, D_ + 1.6, 3.5), (c.x, c.y, T1 + 1.75), (0, 0, ang))


def barrels(sh, x, y, ang, kind=0):
    Fb = Frame(x, y, DZ, ang)
    spots = ([(-0.85, 0.0, 0.72, 1.6), (0.75, -0.2, 0.72, 1.6), (0.0, 1.2, 0.62, 1.35)] if kind == 0 else
             [(-0.7, 0.0, 0.72, 1.6), (0.75, 0.15, 0.66, 1.45)])
    for bx_, by_, r, h in spots:
        K.lathe(sh, Fb, (bx_, by_, 0.0), [(r * 0.86, 0.0), (r, h * 0.5), (r * 0.86, h), (r * 0.76, h - 0.06)], 8, WM)
        for zz in (h * 0.22, h * 0.78):
            K.lathe(sh, Fb, (bx_, by_, zz - 0.07), [(r * 0.96 + 0.1, 0.0), (r * 0.96 + 0.1, 0.14)], 8, IRON,
                    caps=(False, False))
    c = Fb.p(0.0, 0.4, 0.0)
    col_box("OPSumProp", (3.4, 3.2, 2.0), (c.x, c.y, T1 + 1.0), (0, 0, ang))


def cannon(sh, x, s):
    """CANHAO decorativo no reparo de 4 rodas, encostado na amurada com a boca na portinhola; por fora do costado: a
    portinhola emoldurada e a boca de ferro aparecendo"""
    yi = CY + s * (hb(x) - BW_T)                      # face interna da amurada
    yo = CY + s * hb(x)
    yc = yi - s * 1.55
    K.bb(sh, F0, x - 0.8, x + 0.8, yc - 1.15, yc + 1.15, DZ, DZ + 0.62, WD)
    for dx in (-0.6, 0.6):
        for dy in (-0.8, 0.8):
            sh.rod(Vector((x + dx * 1.42, yc + dy, DZ + 0.36)), Vector((x + dx * 1.42 + (0.22 if dx > 0 else -0.22),
                   yc + dy, DZ + 0.36)), 0.36, WM, 8)
    a = Vector((x, yc + s * 1.0, GUN_Z))
    b = Vector((x, yi - s * 0.05, GUN_Z))
    c = Vector((x, yc - s * 1.0, GUN_Z))
    sh.rod(c, a, 0.4, IRON, 8)
    sh.rod(a, b, 0.33, IRON, 8)
    sh.rod(b - Vector((0, s * 0.35, 0)), b, 0.42, IRON, 8)
    sh.ico(0.28, tuple(c - Vector((0, s * 0.3, 0))), IRON, 1)
    # por fora: moldura da portinhola (4 travessas) + fundo preto + boca
    for (a0, a1, z0, z1) in ((-0.75, 0.75, -0.55, -0.32), (-0.75, 0.75, 0.32, 0.55), (-0.75, -0.52, -0.32, 0.32),
                             (0.52, 0.75, -0.32, 0.32)):
        sh.box((a1 - a0, 0.3, z1 - z0), (x + (a0 + a1) / 2, yo + s * 0.15, GUN_Z + (z0 + z1) / 2), (0, 0, 0), WD, 0.0)
    qf(sh, [(x - 0.52, yo + s * 0.12, GUN_Z - 0.32), (x + 0.52, yo + s * 0.12, GUN_Z - 0.32),
            (x + 0.52, yo + s * 0.12, GUN_Z + 0.32), (x - 0.52, yo + s * 0.12, GUN_Z + 0.32)], WD, (0, s, 0))
    sh.rod(Vector((x, yo + s * 0.1, GUN_Z)), Vector((x, yo + s * 0.75, GUN_Z)), 0.28, IRON, 8)
    sh.rod(Vector((x, yo + s * 0.55, GUN_Z)), Vector((x, yo + s * 0.8, GUN_Z)), 0.36, IRON, 8)
    return yc


def rope_coil(sh, x, y, r=0.9):
    sh.cyl(r, 0.32, (x, y, DZ + 0.16), (0, 0, 0), ROPE, n=10, bevel=0.0)
    sh.cyl(r * 0.7, 0.3, (x, y, DZ + 0.46), (0, 0, 0), ROPE, n=10, bevel=0.0)


def bollard(sh, x, y, to=None):
    """cabeco de amarracao no terraco + espia (cabo) ate a amurada: o navio esta ATRACADO"""
    K.lathe(sh, F0, (x, y, T1 - 0.1), [(0.85, 0.0), (0.85, 0.3), (0.52, 0.42), (0.48, 1.0), (0.78, 1.15), (0.78, 1.35),
                                       (0.3, 1.42)], 8, IRON)
    if to is not None:
        a, b = Vector((x, y, T1 + 1.05)), Vector(to)
        n = 7
        pts = [a + (b - a) * (i / n) - Vector((0, 0, 0.7 * 4.0 * (i / n) * (1 - i / n))) for i in range(n + 1)]
        tube(sh, pts, 0.13, ROPE, n=4)


def ship_props(sh, dk):
    helm(sh)
    pp = P(0.0, L.SUMMON_PLAYER_D)
    compass_rose(dk, pp.x, pp.y)
    hatch(sh, 141.5, 229.5, 4.0, 3.4)
    hatch(sh, 191.0, CY, 4.4, 4.6)
    capstan(sh, 198.2, CY)
    for s in (-1, 1):
        ycs = [cannon(sh, x, s_) for x, s_ in GUNS if s_ == s]
        xs = [x for x, s_ in GUNS if s_ == s]
        ya, yb = min(ycs) - 1.3, max(ycs) + 1.3
        col_box("OPSumProp", (max(xs) - min(xs) + 2.2, yb - ya, 2.0), ((min(xs) + max(xs)) / 2, (ya + yb) / 2,
                                                                         T1 + 1.0))
    chest(sh, 166.5, CY - 19.4, 0.0, seed=1)
    chest(sh, 168.0, CY + 19.4, math.pi, seed=2)
    chest(sh, 197.8, CY + 7.6, math.pi * 0.62, coins=4, seed=3)
    barrels(sh, 152.5, CY - 21.3, 0.0, 0)
    barrels(sh, 161.5, CY + 21.0, math.pi, 1)
    barrels(sh, 199.0, CY - 7.4, math.pi * 1.2, 1)
    # cabeco de amarracao entre a proa e a ponte de saida (espia ate a amurada de boreste)
    xb = 204.4
    bollard(sh, xb, 225.6, (201.0, CY + hb(201.0) - 0.1, CAP_Z))


# ------------------------------------------------------------------ casa do mastro (o antigo podio, mesmas medidas)
def _board_face(mb, a, b, z0, z1, n_c, trim0=0.0, trim1=0.0, m=HULL):
    """face de TABUAS horizontais (costado em trincado: cada fiada 0,08 para fora da de baixo) de a ate b"""
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    d = b - a
    ln = d.length
    t = d / ln
    nrm = Vector((t.y, -t.x, 0.0))
    rz = math.atan2(t.y, t.x)
    hc = (z1 - z0) / n_c
    w = ln - trim0 - trim1
    for c in range(n_c):
        cm = a + t * (trim0 + w / 2) + nrm * (-0.25 + 0.08 * c)
        lbox(mb, (w, 0.5, hc - 0.06), cm.x, cm.y, z0 + c * hc + 0.03 + (hc - 0.06) / 2, m, 0.0, rz)
    return nrm, t, ln


def _porthole(mb, a, nrm, t, d_along, zc):
    p = Vector((a[0], a[1], 0.0)) + t * d_along
    w = P(p.x, p.y, zc)
    n_w = Vector(P(nrm.x, nrm.y, 0.0)) - Vector(P(0.0, 0.0, 0.0))
    Fp = Frame(w.x, w.y, w.z, math.atan2(-n_w.x, n_w.y))
    K.lathe_y(mb, Fp, (0.0, 0.0, 0.0), [(0.78, -0.1), (0.78, 0.2)], 8, GOLD)
    K.lathe_y(mb, Fp, (0.0, 0.0, 0.0), [(0.54, 0.0), (0.54, 0.34)], 8, LGLOW)


def deckhouse(sh, rl):
    """o podio de ishigaki vira a CASA DO MASTRO (convés elevado em volta da torre) com AS MESMAS medidas e colisao:
    degrau de madeira, costado de tabuas em trincado com cinta vermelha e vigias de latao acesas, capa de tabuado,
    patamar do portal em madeira e guarda-corpo vermelho de navio"""
    du, dvb, dvf, ch, dz = DAIS
    pu, pvb, pvf = POD
    right = [(CORR, dvb), (du - ch, dvb), (du, dvb + ch), (du, dvf - ch), (du - ch, dvf), (CORR, dvf)]
    back = [(-CORR, dvb), (CORR, dvb), (CORR, pvb + 0.6), (-CORR, pvb + 0.6)]
    for pc in (right, [(-u, v) for u, v in reversed(right)], back):
        poly = ccw(local_poly(pc))
        sh.prism(poly, Z - 0.5, Z + dz - 0.2, WD)
        sh.prism(ccw(DL.offset_poly(poly, 0.12)), Z + dz - 0.2, Z + dz, WM)
    r = 0.3
    cr_ = CORR + 0.2
    pieces = [[(cr_, pvb + r), (pu - r, pvb + r), (pu - r, pvf - r), (cr_, pvf - r)],
              [(-pu + r, pvb + r), (-cr_, pvb + r), (-cr_, pvf - r), (-pu + r, pvf - r)],
              [(-CORR, pvb + r), (CORR, pvb + r), (CORR, PV), (-CORR, PV)]]
    for pc in pieces:
        sh.prism(ccw(local_poly(pc)), Z + dz - 0.05, Z + COPE + 0.02, WD)
    faces = [((pu, pvf), (CORR + 0.15, pvf)), ((-CORR - 0.15, pvf), (-pu, pvf)), ((pu, pvb), (pu, pvf)),
             ((-pu, pvf), (-pu, pvb)), ((-pu, pvb), (pu, pvb))]
    trims = [(0.9, 0.0), (0.0, 0.9), (0.0, 0.0), (0.0, 0.0), (0.9, 0.9)]
    ports = {0: [0.5], 1: [0.5], 2: [0.3, 0.7], 3: [0.3, 0.7], 4: [0.3, 0.7]}
    for i, (a, b) in enumerate(faces):
        nrm, t, ln = _board_face(sh, a, b, dz, COPE - 0.42, 3, trims[i][0], trims[i][1])
        # cinta vermelha logo abaixo da capa
        w = ln - trims[i][0] - trims[i][1]
        cm = Vector((a[0], a[1], 0)) + t * (trims[i][0] + w / 2) + nrm * (-0.1)
        lbox(sh, (w, 0.5, 0.36), cm.x, cm.y, COPE - 0.22, LACQ, 0.0, math.atan2(t.y, t.x))
        for f in ports[i]:
            _porthole(sh, a, nrm, t, trims[i][0] + w * f, (dz + COPE - 0.42) / 2 + 0.05)
    deck_ = [[(CORR, pvb), (pu, pvb), (pu, pvf), (CORR, pvf)], [(-pu, pvb), (-CORR, pvb), (-CORR, pvf), (-pu, pvf)],
             [(-CORR, pvb), (CORR, pvb), (CORR, PV), (-CORR, PV)]]
    for i, pc in enumerate(deck_):
        poly = local_poly(pc)
        grow = 0.3 if i < 2 else 0.0
        sh.prism(ccw(DL.offset_poly(ccw(poly), grow)), Z + COPE, Z + DECK, WM)
    lbox2(sh, -CORR, PV, dz - 0.05, CORR, pvf, LAND_Z - 0.3, WD)
    lbox2(sh, -CORR, PV, LAND_Z - 0.3, CORR, pvf + 0.12, LAND_Z + 0.025, WM)
    # guarda-corpo vermelho de navio (recuado RAIL_IN), aberto no corredor da escada
    ri = RAIL_IN
    path_l = [(-CORR - 0.45, pvf - ri), (-pu + ri, pvf - ri), (-pu + ri, pvb + ri), (pu - ri, pvb + ri),
              (pu - ri, pvf - ri), (CORR + 0.45, pvf - ri)]
    C = [Vector(P(u, v, 0.0)) for u, v in path_l]
    zt, zm = Z + DECK + 2.0, Z + DECK + 1.05
    for a, b in zip(C, C[1:]):
        rl.beam((a.x, a.y, zt - 0.13), (b.x, b.y, zt - 0.13), 0.38, 0.26, LACQ, 0.0)
        rl.beam((a.x, a.y, zm), (b.x, b.y, zm), 0.16, 0.16, LACQ, 0.0)
        ln = (b - a).length
        n = max(1, int(math.ceil(ln / 3.2)))
        for k in range(n + (1 if b is C[-1] else 0)):
            p = a.lerp(b, k / n)
            big = k == 0 and a is C[0] or (b is C[-1] and k == n)
            s_ = 0.5 if big else 0.32
            rl.box((s_, s_, 2.0 + (0.3 if big else 0.0)), (p.x, p.y, Z + DECK + (2.0 + (0.3 if big else 0.0)) / 2),
                   (0, 0, 0), LACQ, 0.0)
            if big:
                K.lathe(rl, F0, (p.x, p.y, Z + DECK + 2.3), [(0.32, 0.0), (0.32, 0.12), (0.16, 0.36), (0.04, 0.5)], 6,
                        GOLD)


def podium_collision():
    A = "OPSumTower"
    du, dvb, dvf, ch, dz = DAIS
    pu, pvb, pvf = POD
    for s in (-1, 1):
        lcol2(A, s * CORR, dvb + ch, -0.6, s * du, dvf - ch, dz)
        lcol2(A, s * CORR, dvb, -0.6, s * (du - ch), dvf, dz)
        lcol2(A, s * CORR, pvb - 0.3, -0.6, s * (pu + 0.3), pvf + 0.3, DECK + 2.95)    # casa do mastro + guarda-corpo
    lcol2(A, -CORR, dvb, -0.6, CORR, pvb - 0.3, dz)
    lcol2(A, -CORR, pvb - 0.3, -0.6, CORR, PV, DECK + 2.95)
    lcol2(A, -CORR, PV, -0.2, CORR, LAND_V1, LAND_Z)


def tower_stair(sh):
    """escada da torre com a medida da Ilha 1 (5 x 0,8, piso 1,6, 7,6 de largura; o 5o degrau e a frente do patamar)
    no desenho do op_kit.stair_stone, agora em MADEIRA de navio (pisadas claras, espelhos escuros, banzos de costado).
    Colisao: op_col.stair_col (rampa + guardas)."""
    base = P(0.0, ST_FOOT, 0.0)
    ang = FACE + math.pi
    Fs = Frame(base.x, base.y, base.z, ang - math.pi / 2)        # o kit sobe para +y
    K.stair_stone(sh, Fs, ST_W, ST_N - 1, rise=ST_RISE, tread=ST_TREAD, z_floor=-0.3, cheek_h=0.9, m=WM, riser_m=WD,
                  cheek_m=HULL, cap_m=WD)
    op_col.stair_col("OPSumTower", (base.x, base.y, base.z), ang, ST_W, ST_N, ST_RISE, ST_TREAD, guards=True,
                     guard_h=4.0)


def podium_lamps(sh):
    """2 lanternas de navio em postes na casa do mastro (onde ficavam os toro), ladeando o portal"""
    out = []
    for s in (-1, 1):
        p = P(s * IN_LAMP[0], IN_LAMP[1], DECK)
        sh.box((0.5, 0.5, 2.6), (p.x, p.y, p.z + 1.3), (0, 0, 0), WD, 0.0)
        sh.box((0.7, 0.7, 0.3), (p.x, p.y, p.z + 0.15), (0, 0, 0), IRON, 0.0)
        out.append(ship_lantern(sh, p.x, p.y, p.z + 2.6, 1.0))
        col_box("OPSumTower", (1.4, 1.4, 5.6), (p.x, p.y, p.z + 2.8), (0, 0, YAW))
    return out


# ------------------------------------------------------------------ terraco em volta do navio (pedra, cabecos, pinheiros)
def _flags(mb, x0, y0, x1, y1, z, seed, m=ST, along="x", lw=(1.8, 3.2), lh=(1.7, 2.3), skip=None):
    """lajeado retangular em fiadas desencontradas (juntas 0,16; topo z). 'skip(x0, y0, x1, y1)' -> True: sem laje"""
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
            if not (skip and skip(cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2)):
                mb.box((sx - 0.16, sy - 0.16, 0.34), (cx, cy, z - 0.17), (0, 0, (E.hsh(seed, row, j, 5) - 0.5) * 0.02),
                       m, 0.0)
            b += w
            j += 1
        a += h
        row += 1


def _near_hull(x0, y0, x1, y1, pad=0.7):
    return any(in_hull(x, y, pad) for x in (x0, (x0 + x1) / 2, x1) for y in (y0, (y0 + y1) / 2, y1))


def _exit_rail_ends():
    """M6b item 14: y onde o guarda-corpo do terraco termina (sul) e recomeca (norte) junto a ponte de saida: 0,6 livre
    antes do 1o poste-mestre da ponte (op_exit.rails: eixo v = +-9,82, comeca na borda x 205,45 + 0,05; poste 0,8 + cinta
    0,13) e do nosso poste-mestre final (0,7 + cinta 0,13). Antes os 2 postes-mestre caiam um dentro do outro."""
    ux, uy = L.exit_dir()
    sx, sy = L.EXIT_START
    out = []
    for v in (-9.82, 9.82):
        d = (205.45 - sx + uy * v) / ux + 0.05
        out.append(sy + uy * d + ux * v)
    gap = (0.8 / 2 + 0.13) + 0.6 + (0.7 / 2 + 0.13)
    return out[0] - gap, out[1] + gap


def terrace(st, pv, rl, gr):
    zt = T1 + 0.3                                   # topo das lajes (0,18 acima das ruas do blockout da capital)
    # escadaria da planta: terraco -> praca (lado leste da praca), pedra do op_kit no envelope do op_col; chega na
    # POPA ABERTA do navio
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    K.stair_stone(st, Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2), w, n,
                  rise=L.stair_rise("Summon"), tread=tread, z_floor=-0.3)
    Fst = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
    rise = L.stair_rise("Summon")
    for sx in (-1, 1):                              # banzos (capa inclinada): rampa de colisao 0,3 alem da capa
        xc = sx * (w / 2 + 0.6)
        za = rise * (0.3 / tread + 1.0) + 1.0 + 0.3
        zb = rise * ((tread * (n - 1) + 0.5) / tread + 1.0) + 1.0 + 0.3
        DL.col_ramp("OPSumStair", Fst.p(xc, 0.3, za), Fst.p(xc, tread * (n - 1) + 0.5, zb), 1.95, thick=2.4)
    # caminhos lajeados FORA do casco: porto (sul, pelo portalo de bombordo) e ponte de saida (norte/leste)
    _flags(pv, 134.0, 151.0, 149.0, 192.0, zt, 41, along="x", lw=(1.8, 3.0), m=STP, skip=_near_hull)
    _flags(pv, 134.0, 233.6, 205.4, 246.4, zt, 43, along="y", lw=(1.8, 3.0), m=STP, skip=_near_hull)
    _flags(pv, 192.0, 222.0, 205.4, 233.6, zt, 47, along="y", lw=(1.8, 2.6), m=STP, skip=_near_hull)
    # guarda-corpo vermelho nas bordas que dao para o porto (aberto na cabeca da ponte de saida e onde a PROA passa)
    ys, yn = _exit_rail_ends()
    yb0 = CY - hb(205.25) - 0.9
    for a_, b_, nodes in (((149.0, 150.75), (205.25, 150.75), (0.0, 0.5, 1.0)),
                          ((205.25, 151.2), (205.25, yb0), (0.0, 0.5, 1.0)),
                          ((205.25, yn), (205.25, 256.0), (0.0, 1.0)),
                          ((205.25, 256.0), (199.6, 263.4), (1.0,))):
        E.rail_run(rl, (a_[0], a_[1], T1), (b_[0], b_[1], T1), h=2.4, step=4.6, nodes=nodes, node_up=0.7, post=0.44,
                   node_post=0.7, top_w=0.66, gold=GOLD)
        d = Vector((b_[0] - a_[0], b_[1] - a_[1]))
        col_box("OPSumRail", (d.length + 1.2, 1.2, 4.6), ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2, T1 + 1.8),
                (0, 0, math.atan2(d.y, d.x)))
    # V3 fix (gate visual U5_B, fresta (204; 259,9)): no canto NE do terraco a pele T1 termina na diagonal do guarda-
    # corpo e sobra uma FENDA (0,5..2,5) ate o muro do terraco de cima (y 261,5) e a borda da falesia (x 206): SOLEIRA
    # de pedra (topo T1 + 0,4, 1,0 de espessura) do lado de dentro do guarda-corpo ate o muro/borda, fechando a fenda.
    # Sob a guarda do op_col (COL_OP_Guard_*) e o corrimao (COL_OPSumRail): ja coberta; 1 caixa propria rente ao topo.
    sill = [(204.75, 255.0), (206.2, 255.0), (206.2, 262.4), (199.9, 262.4)]
    st.prism(ccw(sill), T1 - 0.6, T1 + 0.4, STD)
    col_box("OPSumRail", (1.4, 7.6, 1.0), (205.5, 258.7, T1 - 0.1))
    # (V2: os 2 canteiros com pinheiro sairam - o orcamento foi para o navio; 'PINES' vazio)
    for i, (px, py, h) in enumerate(PINES):
        bed = DL.blob_poly(px, py, 6.2, 10, random.Random(950 + i), 0.12, sx=1.25)
        outer = ccw(bed)
        inner = ccw(DL.offset_poly(outer, -0.55))
        K.loft(st, Frame(0.0, 0.0, 0.0, 0.0), [[(x, y, T1 - 0.2) for x, y in outer], [(x, y, T1 + 0.38) for x, y in outer],
                                               [(x, y, T1 + 0.38) for x, y in inner], [(x, y, T1 + 0.05) for x, y in inner]],
               STD, caps=(False, False))
        gr.prism(ccw(DL.offset_poly(outer, -0.5)), T1 - 0.1, T1 + 0.23, "Dirt_OP")
        wano_pine(gr, px, py, T1 + 0.23, h, random.Random(960 + i))
        col_box("OPSumPine", (1.8, 1.8, h * 0.6), (px, py, T1 + h * 0.3))
        for k in range(3):
            aa = 2.1 + k * 1.9 + i
            r = 1.1 + 0.4 * E.hsh(i, k)
            gr.ico(r, (px + math.cos(aa) * 4.0, py + math.sin(aa) * 3.4, T1 + 0.5 + r * 0.45), "Leaf_OP", 1,
                   scale=(1.3, 1.15, 0.8))
        st.ico(1.0, (px - 3.6, py + 2.2, T1 + 0.6), "Stone_OP", 1, scale=(1.4, 1.0, 0.7))


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


# ------------------------------------------------------------------ cameras de revisao (renders/v2/summon)
EYE = L.EYE
CAMS = {
    "CAM_OPSum_Jogo": ((112.0, 214.0, T1 + 36.0), (168.0, 214.0, T1 + 6.0), 24),          # camera do jogo (de tras/cima)
    "CAM_OPSum_Jogo34": ((118.0, 160.0, T1 + 40.0), (172.0, 216.0, T1 + 4.0), 24),
    "CAM_OPSum_Chegada": ((100.0, 214.0, L.P + EYE), (170.0, 214.0, T1 + 16.0), 22),       # descendo da praca
    "CAM_OPSum_Conves": ((136.0, 194.0, T1 + EYE), (176.0, 222.0, T1 + 10.0), 22),
    "CAM_OPSum_Torre": ((146.0, 214.0, T1 + EYE), (170.0, 214.0, T1 + 18.0), 22),
    "CAM_OPSum_Timao": ((140.0, 205.0, T1 + EYE), (133.2, 199.6, T1 + 3.2), 30),
    "CAM_OPSum_Proa": ((232.0, 246.0, T1 + 7.0), (214.0, 214.0, T1 + 3.0), 24),            # da ponte de saida
    "CAM_OPSum_Carranca": ((236.0, 206.0, T1 + 6.0), (215.0, 214.0, T1 + 4.0), 26),
    "CAM_OPSum_Porto": ((236.0, 128.0, L.HARBOR + EYE), (200.0, 212.0, T1 + 4.0), 22),     # de baixo, no cais
    "CAM_OPSum_Castelo": ((182.0, 200.0, T1 + EYE), (212.0, 214.0, T1 + 4.0), 22),         # castelo de proa
    "CAM_OPSum_Planta": ((166.0, 207.0, T1 + 150.0), (166.0, 207.01, T1), 30),
}


def _remap(mb, src, dst):
    """faces do material 'src' passam para 'dst' (o banzo do stair_stone sorteia pedra escura: no navio vira costado)"""
    di = mb._mi_for(dst)
    idx = {i for i, k in enumerate(mb.mats) if (k[1] if isinstance(k, tuple) else k) == src}
    n = 0
    for f in mb.bm.faces:
        if f.material_index in idx:
            f.material_index = di
            n += 1
    return n


def build():
    """a zona em POUCOS objetos por familia (orcamento de MeshParts: 1 por material por objeto): torre (pedra, ouro
    velho, brilho, gaiola/VFX da Ilha 1), NAVIO (casco/amurada/madeira/guarda-corpos/carga/carranca, normais
    calculadas), CONVES (tabuas + rosa-dos-ventos, so faces de cima), VELAS (velas e bandeiras com a Jolly Roger) e o
    lajeado do terraco."""
    before = {o.name for o in bpy.data.objects}
    st = MB("OP_Sum_Stone", COL, random.Random(7401), detail="near")
    mt = MB("OP_Sum_Metal", COL, random.Random(7403), detail="near")
    gl = MB("OP_Sum_Glow", COL, random.Random(7404), detail="hero")
    pv = MB("OP_Sum_Paving", COL, random.Random(7407), detail="near")
    sh = MB("OP_Sum_Ship", COL, random.Random(7420), detail="far", floor=-999)
    dk = MB("OP_Sum_Deck", COL, random.Random(7421), detail="far", floor=-999)
    sl = MB("OP_Sum_Sails", COL, random.Random(7422), detail="far", floor=-999)
    with tower_palette():
        T, c = build_tower(st, mt, gl, None)
        terrace(st, pv, sh, None)                  # escada da praca, lajeado de fora, guarda-corpo da borda
        for mb in (st, mt, gl):
            mb.finish()
    tw = {}

    def tri(mb):
        return sum(len(f.verts) - 2 for f in mb.bm.faces)
    stern_lamps = []
    for nm, fn in (("casa do mastro", lambda: deckhouse(sh, sh)), ("escada da torre", lambda: tower_stair(sh)),
                   ("conves", lambda: deck(dk)), ("amuradas", lambda: bulwarks(sh)), ("proa", lambda: bow(sh)),
                   ("carranca", lambda: lion(sh)), ("mastros+velas", lambda: rig(sh, sl)),
                   ("carga/timao/rosa", lambda: ship_props(sh, dk))):
        t0 = tri(sh) + tri(dk) + tri(sl)
        res = fn()
        tw[nm] = tri(sh) + tri(dk) + tri(sl) - t0
        if nm == "amuradas":
            stern_lamps = res
    lamps = podium_lamps(sh)
    _remap(sh, STD, HULL)
    # cabos varridos (tubos): normais recalculadas SO neles (ilhas fechadas); o resto com orientacao calculada
    ri = {i for i, k in enumerate(sh.mats) if (k[1] if isinstance(k, tuple) else k) == ROPE}
    rf = [f for f in sh.bm.faces if f.material_index in ri]
    if rf:
        bmesh.ops.recalc_face_normals(sh.bm, faces=rf)
    for mb in (sh, dk, sl):
        mb.finish(recalc=False)
    pv.finish()
    adopt_tower_objects(before)
    tower_collision(T)
    podium_collision()
    for i, cc in enumerate(stern_lamps[:2]):
        light("L_OPProp_Lamp_Sum_%d" % i, "POINT", tuple(cc), 120.0, WARM, 0.3)
    # luzes de dia (4): nucleo azul do portal, estrela (quente, contida), 2 lanternas da casa do mastro
    light("L_OPSum_Core", "POINT", tuple(P(0.0, PV + 3.0, 9.0)), 650.0, (0.36, 0.52, 1.0), 1.0)
    light("L_OPSum_Star", "POINT", tuple(c), 420.0, (1.0, 0.72, 0.36), 1.4)
    for n, p in zip(("L_OPSum_Lamp_L", "L_OPSum_Lamp_R"), lamps):
        light(n, "POINT", tuple(p), 130.0, WARM, 0.3)
    print("OP_SUMMON tris por parte: " + ", ".join("%s %d" % kv for kv in tw.items()))
    print("OP_SUMMON ok")
