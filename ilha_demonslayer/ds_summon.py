# ds_summon - ZONA SUMMON da Ilha 4 (DEMON SLAYER), agente 1d da Onda 1 (PLANO_DS secao 12, prompt secao 12).
# Substitui ds_blockout.summon. Prefixo DS_Sum_, colecao 06_SUMMON, pecas moveis VFX_DSSUM_* (12_VFX_HELPERS), luzes
# L_DSSum_* (de dia, LIGHT_KEEP) e L_DSProp_Lamp_Sum* (lanternas de no: NightOnly).
#
# TORRE AMS SEM REDESENHO: e a MESMA torre de invocacao das Ilhas 1, 2 e 3 (codigo da Ilha 1, ilha_naruto/il_summon.py,
# carregado com a planta DESTA ilha: il_layout.SUMMON_TOWER/FACE/T1/SUMMON_C/R trocados so durante o import, como o
# sg_summon.tower_mod da Ilha 3 e o blockout da onda 0). Nucleo visual preservado: ESTRELA + ANEIS + TORRE + NUCLEO de
# energia azul (corpo L1 com o nicho do portal, frontispicio, frontao, cornijas, L2 com a janela-estrela, coroa L3 com
# pinaculos, contrafortes, mastros com estandartes, esfera armilar com 3 aneis moveis e a estrela de cristal).
# As funcoes da Ilha 1 que misturam base e torre (tower_stone, masts_and_lanterns, tower_collision) foram PORTADAS so
# com a parte da torre (como no sg_summon); tower_details e sphere sao chamadas direto.
#
# O QUE MUDOU (so base, plataforma, materiais, ornamentos, luz e entorno):
#   - materiais por apelido SO durante a torre (fm_lib.MAT_ALIAS): pedra lilas -> pedra escura DS (Stone_DS_Dark com
#     fiadas de Cliff_DS, a rocha da ilha: alternancia SUTIL, a torre fica escura e nao disputa com o reboco da
#     forja); ouro -> ouro VELHO (Metal_Gold_DS, um valor abaixo); estandartes azul-royal -> indigo DS; estrela ambar/amarela (Neon 3,0 que
#     estourava em creme) -> facetas alternadas de Neon ambar MEDIO (Summon_DSStar_Glow) e ouro velho; brilhos azuis
#     da Ilha 1 (circulo do patamar, miolos das estrelas) -> violeta medio-escuro (Summon_DSViolet_Glow = os acentos
#     violeta CONTROLADOS, so filetes). O nucleo azul do portal (Crystal_SumPortal_Glow) NAO muda: e a identidade AMS.
#   - luz: estrela 3000 -> 900, nucleo 1600 -> 1200 (hierarquia do PLANO secao 10: fornalha > janelas da forja >
#     summon > casas > lanternas). O summon fica visivel e nao compete com a forja.
#   - base: o soco de 40 x 19,6 da Ilha 1 (4 pedestais de lanterna nas quinas) nao cabe no plato -> PODIO PROPRIO de
#     santuario: degrau (kidan) de pedra escura chanfrado com capa de pedra media, podio em ENXAIMEL de madeira escura
#     (soleira, pilares, travessa e beiral-capa com balanco) sobre paineis de pedra RECUADOS 0,35, ferragens de ouro
#     velho (kanamono) nas quinas e cortina VIOLETA (maku) em festoes na frente; escada da torre com a medida da Ilha 1
#     (5 x 0,8, 7,6 de largura) em pedra com focinho chanfrado e espelho recuado, banzos de pedra escura com corrimao
#     de madeira e pilares de giboshi; 2 lanternas de pedestal (toro de pedra) no podio ladeando o portal.
#   - entorno: escadaria da planta (13 degraus, clareira -> plato) com banzos inclinados macicos, capa e pilar de
#     arranque; pontezinha arqueada de madeira sobre o canal (tabuleiro de tabuas, vigas curvas, guarda-corpo com
#     giboshi, encontros de pedra); guarda-corpo baixo de madeira (koran) em volta do plato, aberto na escada;
#     MIRANTE no canto leste/nordeste: pavilhao aberto de madeira escura (azumaya) na borda, com bancos virados para o
#     vazio, guarda-corpo, lanterna pendurada e maku violeta; 2 toro no topo da escada (lanternas de no, NightOnly);
#     as 2 GLICINIAS do plano (as unicas do plato) com tronco-lider em S, galhos em guarda-chuva e CACHOS PENDENTES de
#     verdade (camadas de petalas em sino, 3 tons) - wisteria_tree() fica exposta para o ds_veg (mesma familia).
# Fora: praca redonda, cristais (liam como minerio), constelacao, pedestais externos e postes de lanterna da Ilha 1.
# Colisao propria: degrau/podio, escada da torre + patamar, corpo da torre, mastros, toro, guarda-corpo do plato,
# pontezinha (rampas do arco + parapeitos), mirante, troncos das glicinias. Piso do plato, escada da planta e as guardas
# de borda: ds_col (congelado). Marcadores SUMMON_*: ds_core (congelado; jogador em v 16 no piso, gabinete invisivel
# do gacha em v 7).
import math, random, sys, importlib
from contextlib import contextmanager
from mathutils import Vector
import bpy
import ds_lib as DL
from ds_lib import MB, col_box, col_ramp, light, Frame, ccw
import ds_layout as L
import ds_col
import fm_lib
import fm_portal_kit as PK

COL = "06_SUMMON"
T1, T3 = L.T1, L.T3
Z = T3
TX, TY = L.SUMMON_TOWER
CX, CY = L.SUMMON_C
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2
F = Frame(TX, TY, Z, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))     # +u (lateral; aqui = +y do mundo, norte)
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))    # +v (frente da torre; aqui = -x, oeste: clareira)
ZZ = Vector((0.0, 0.0, 1.0))
# medidas da torre da Ilha 1 (il_summon) usadas antes do import; tower_mod() confere que batem
ST_FOOT, LAND_Z, PV, CORR, POD_TOP, AX, ZS = 13.6, 4.0, -1.4, 5.0, 3.3, -3.0, 46.0
LAND_V1 = 5.6
ST_W, ST_N, ST_RISE, ST_TREAD = 7.6, 5, 0.8, 1.6
WARM = (1.0, 0.64, 0.34)

# ------------------------------------------------------------------ materiais novos (5 de 5, contando o portal)
_S = fm_lib.S
GOLD = "Metal_Gold_DS"            # ouro VELHO (prefixo Metal_Gold: FOLD_PROTECT e Metal no Roblox)
STAR = "Summon_DSStar_Glow"       # ambar MEDIO (Neon pela palavra glow): estrela, faiscas, enfeites dos aneis
VIOLET = "Summon_DSViolet_Glow"   # violeta medio-escuro (Neon): os filetes violeta controlados
WIS_DEEP = "Wisteria_DS_Deep"     # 3o tom da glicinia (alto dos cachos, massas de flor)
fm_lib.MATS.setdefault(GOLD, (_S(158, 118, 56), 0.45, 0.7, 0, None, 0.04))
# ONDA 3c (ds_lights, equilibrio de destaque pedido pela onda 2b: da clareira o dourado do summon competia com a forja).
# SO os numeros de emissao/brilho (geometria, ouro da estrutura e o azul do portal intactos): estrela ambar 0,6 -> 0,32
# e o Neon dela no Roblox um valor abaixo (192,114,40 -> 162,94,34); filetes violeta 0,55 -> 0,40. As luzes L_DSSum_*
# (estrela 900 -> 160, nucleo 1200 -> 450) sao do passe global ds_lights (que roda depois e manda nas energias).
fm_lib.MATS.setdefault(STAR, (_S(162, 94, 34), 0.3, 0.0, 0.32, _S(162, 94, 34), 0.0))
fm_lib.MATS.setdefault(VIOLET, (_S(96, 68, 166), 0.3, 0.0, 0.40, _S(96, 68, 166), 0.0))
fm_lib.MATS.setdefault(WIS_DEEP, (_S(112, 76, 170), 0.8, 0.0, 0, None, 0.04))
for _k in (STAR, VIOLET):
    fm_lib.RBX_CAL.setdefault(_k, (None, [int(c) for c in fm_lib.to_srgb(fm_lib.MATS[_k][0])]))
WIS_TONES = (WIS_DEEP, "Wisteria_DS", "Wisteria_DS_Light")
IRON = "Metal_DS_Iron"
PAPER = "Glass_DS_Lantern"

TOWER_ALIAS = {
    "Summon_Stone_Dark": "Stone_DS_Dark", "Summon_Stone": "Stone_DS_Dark", "Stone_SumBlock": "Cliff_DS",
    "Metal_Gold": GOLD, "Cloth_Royal_Blue": "Cloth_DS_Indigo", "Wood_Dark": "Wood_DS_Dark",
    "Crystal_SumStar_Glow": STAR, "Summon_Star_Glow": STAR, "Crystal_SumAmber_Glow": STAR,
    "Crystal_SumYellow_Glow": GOLD, "Summon_Blue_Glow": VIOLET, "Crystal_Blue": VIOLET, "Lantern_Glow": PAPER,
}

# ------------------------------------------------------------------ base (podio proprio), no referencial da torre
DAIS = (14.6, -14.4, 9.6, 3.0, 0.7)      # degrau kidan: meia largura, v de tras, v da frente, chanfro, topo
POD = (12.4, -12.2, 7.2)                 # podio: meia largura, v de tras, v da frente (linha da face do enxaimel)
DECK = POD_TOP                           # tampo do podio (a torre nasce aqui)
CORN = 3.42                              # topo do beiral-capa de madeira (0,12 acima do tampo: sem face coplanar)
RECESS = 0.35                            # paineis de pedra recuados atras da face do enxaimel
IN_LAMP = (9.6, 4.4)                     # toro do podio (u, v): o lugar dos pedestais internos da Ilha 1
# entorno (mundo)
SHELTER = (192.6, 322.4, 7.0, 5.6)       # mirante coberto (x, y, w ao longo de x, d ao longo de y)
TOP_TORO = ((153.6, 290.6), (153.6, 309.4))
RAIL_IN = 1.0                            # guarda-corpo do plato: recuo da borda (a guarda invisivel do ds_col fica fora)


def P(u, v, z=0.0):
    return F.p(u, v, z)


def to_local(x, y):
    d = Vector((x - TX, y - TY, 0.0))
    return d.dot(XU), d.dot(YV)


def local_poly(pts_uv):
    return [tuple(P(u, v).xy) for u, v in pts_uv]


def lbox(mb, size, u, v, z, m, bevel=0.0, rz=0.0):
    mb.box(size, P(u, v, z), (0, 0, YAW + rz), m, bevel)


def lbox2(mb, u0, v0, z0, u1, v1, z1, m, bevel=0.0):
    lbox(mb, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, m, bevel)


def lcol2(area, u0, v0, z0, u1, v1, z1):
    c = P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
    col_box(area, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), c, (0, 0, YAW))


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


def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


# ------------------------------------------------------------------ cameras de revisao (o studio_ds as cria)
_BR = L.FOOTBRIDGE
CAMS = {
    # a torre inteira: da margem leste da clareira, da diagonal sudoeste, de tras (no ar) e do norte
    "CAM_DSSum_Front": ((112.0, 300.0, T3 + 14.0), (TX, TY, T3 + 26.0), 24),
    "CAM_DSSum_34": ((128.0, 246.0, T3 + 12.0), (178.0, 300.0, T3 + 20.0), 24),
    "CAM_DSSum_Back": ((250.0, 318.0, T3 + 24.0), (TX, TY, T3 + 24.0), 26),
    "CAM_DSSum_North": ((170.0, 392.0, T3 + 22.0), (182.0, 300.0, T3 + 18.0), 24),
    # altura do jogador: no SUMMON_PlayerPosition olhando o portal; no topo da escada; no podio de perto
    "CAM_DSSum_Pad": ((166.0, 300.0, T3 + 5.4), (TX, TY, T3 + 11.0), 20),
    "CAM_DSSum_StairTop": ((152.0, 300.0, T3 + 5.4), (TX, TY, T3 + 14.0), 22),
    "CAM_DSSum_Podium": ((166.0, 283.0, T3 + 5.2), (178.0, 293.0, T3 + 2.4), 26),
    "CAM_DSSum_Lantern": ((168.5, 286.0, T3 + 6.2), (P(-IN_LAMP[0], IN_LAMP[1]).x, P(-IN_LAMP[0], IN_LAMP[1]).y,
                                                       T3 + 6.0), 34),
    # glicinia de perto (galho, cachos) e o mirante coberto
    "CAM_DSSum_Wisteria": ((160.0, 281.0, T3 + 4.8), (176.0, 270.0, T3 + 7.6), 26),
    "CAM_DSSum_Mirante": ((176.0, 312.0, T3 + 5.2), (SHELTER[0], SHELTER[1], T3 + 3.4), 24),
    "CAM_DSSum_MiranteRoof": ((180.0, 309.0, T3 + 11.0), (SHELTER[0], SHELTER[1], T3 + 8.0), 30),
    # pontezinha e pe da escada da planta (da clareira, na altura do jogador)
    "CAM_DSSum_Bridge": ((100.0, 288.0, T1 + 5.2), (124.0, 300.0, T1 + 2.6), 26),
    "CAM_DSSum_BridgeSide": ((121.0, 276.0, T1 + 3.2), (121.0, 300.0, T1 + 1.4), 26),
    # esfera armilar + estrela de perto
    "CAM_DSSum_Sphere": ((148.0, 282.0, T3 + 48.0), (TX + 3.0, TY, T3 + 46.0), 32),
}

# rotas proprias (para o QA local do agente: a do jogo e a CLEARING->SUMMON do ds_layout)
EXTRA_ROUTES = {
    "PAD->PATAMAR": ([tuple(P(0.0, 16.0).xy), tuple(P(0.0, ST_FOOT + 0.4).xy), tuple(P(0.0, ST_FOOT - 1.0).xy),
                      tuple(P(0.0, LAND_V1 + 0.6).xy), tuple(P(0.0, LAND_V1 - 1.0).xy), tuple(P(0.0, PV + 2.0).xy)], Z),
    "TOPO_ESCADA->MIRANTE (norte)": ([(152.5, 300.0), (160.0, 306.0), (172.0, 317.6), (192.6, 317.6),
                                      (192.6, 322.0)], Z),
    "TOPO_ESCADA->LESTE (sul)": ([(152.5, 300.0), (160.0, 292.0), (176.0, 280.5), (194.0, 281.0), (201.0, 290.0),
                                 (201.5, 300.0)], Z),
    "PONTE (ida)": ([(104.0, 300.0), (115.0, 300.0), (121.0, 300.0), (127.0, 300.0), (130.0, 300.0)], T1),
}


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
    """materiais da Ilha 1 -> paleta DS so enquanto a torre e montada (o MB.finish aplica fm_lib.alias)"""
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
    """PORTADO de il_summon.tower_stone (so a torre: corpo L1 com o nicho, frontispicio, frontao, cornijas, L2 com a
    janela-estrela, coroa L3). O soco/podio de 40 x 19,6 e a escada com bordas de brilho da Ilha 1 ficam de fora (a
    base desta ilha e a de podium())."""
    rng = random.Random(621)
    lb, lb2, face_skin, larch, _buttress = T.lbox, T.lbox2, T.face_skin, T.larch, T._buttress
    PORT_HW, PORT_SPRING, NICHE_TOP, MAST_V = T.PORT_HW, T.PORT_SPRING, T.NICHE_TOP, T.MAST_V
    L1_SWIN, L1_BWIN, BUT_V = T.L1_SWIN, T.L1_BWIN, T.BUT_V
    # --- corpo L1: nucleo com o NICHO do portal (fundo em PV) + contrafortes de canto + pele de alvenaria
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
        lb(stone, (0.75, 0.9, L1_BWIN[1] - L1_BWIN[0]), s * (L1_BWIN[2] + 0.38), v0 - 0.5,
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
    # --- cornija 1
    lb2(stone, -hw - 1.0, v0 - 1.0, z1, hw + 1.0, 2.4, z1 + 0.6, "Summon_Stone_Dark", 0.0)
    lb2(gold, -hw - 1.3, v0 - 1.3, z1 + 0.6, hw + 1.3, 2.6, z1 + 1.3, "Metal_Gold", 0.0)
    # --- corpo L2
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
    # janela de TRAS do L2 com o mesmo emolduramento da frente (o arco de ouro da Ilha 1 ficava solto na parede)
    larch(stone, 0.0, w0 - 0.4, 5.2, y0 + 6.8, 2.6, 1.3, n=7, band=0.9, keystone=True, seed=4)
    for s in (-1, 1):
        lb2(stone, s * 2.6, w0 + 0.1, y0 + 1.4, s * 3.5, w0 - 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lb2(gold, -3.8, w0 + 0.1, y0 + 0.85, 3.8, w0 - 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    # --- cornija 2
    lb2(stone, -hw2 - 0.9, w0 - 0.9, y1, hw2 + 0.9, w1 + 0.9, y1 + 0.5, "Summon_Stone_Dark", 0.0)
    lb2(gold, -hw2 - 1.2, w0 - 1.2, y1 + 0.5, hw2 + 1.2, w1 + 1.2, y1 + 1.15, "Metal_Gold", 0.0)
    # --- coroa L3 + pinaculos
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
    """PORTADO de il_summon.masts_and_lanterns: so os mastros com estandartes (indigo DS) e as lanternas penduradas,
    que viram a lanterna de papel com gaiola de ferro desta ilha (hang_lamp). Os 4 pedestais externos, os pedestais
    dos cristais e os postes do pe da escada da Ilha 1 nao entram."""
    K = T.K
    rng = random.Random(651)
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
        # lanterna pendurada na haste, entre o corpo e o mastro (era a caixa de Neon da Ilha 1)
        hang_lamp(gold, glow, Fb.p(-s * 2.4, 0.0, z_pole - 0.3), 1.0, drop=0.9, yaw=YAW + s * BAN_TH)
        # lanternas penduradas nos cantos da frente do L2 (bracos de ouro)
        br0 = P(s * (hw2 + 0.95), w1, 29.6)
        br1 = P(s * (hw2 + 2.3), w1 + 0.4, 29.6)
        gold.beam(br0, br1, 0.35, 0.35, "Metal_Gold", 0.0)
        gold.beam(P(s * (hw2 + 0.95), w1, 28.2), br1 - ZZ * 0.1, 0.3, 0.3, "Metal_Gold", 0.0)
        hang_lamp(gold, glow, br1, 0.85, drop=0.55, yaw=YAW)


def tower_collision(T):
    """PORTADO de il_summon.tower_collision (so a torre; a base e de podium_collision)"""
    A = "DSSumTower"
    hw, v0, v1, z0, z1 = T.L1
    lcol2(A, -hw - 1.3, v0 - 1.3, POD_TOP, hw + 1.3, PV, T.L3[4])                        # corpo atras do portal
    lcol2(A, -hw - 1.3, PV, T.PORT_SPRING + T.PORT_HW, hw + 1.3, v1 + 0.1, T.L3[4])      # sobre o nicho
    lcol2(A, -T.PORT_HW, v1 + 0.1, T.PORT_SPRING + T.PORT_HW, T.PORT_HW, 4.3, 18.2)      # timpano
    for s in (-1, 1):
        lcol2(A, s * T.PORT_HW, PV, POD_TOP, s * (hw + 1.3), 4.3, 18.2)                  # paredes do nicho
        lcol2(A, s * (hw - 0.1), T.MAST_V - 1.1, POD_TOP, s * (T.MAST_U + 1.0), T.MAST_V + 1.1, 31.0)   # mastro


def build_tower(stone, gold, glow, cloth):
    """a torre nos MBs da zona (pedra, metal, brilho, pano): chamar DENTRO de tower_palette()"""
    T = tower_mod()
    tower_body(T, stone, gold)
    cr = T.tower_details(stone, gold, glow)
    cr.bm.free()                          # cristais da boca do nicho: fora (liam como minerio)
    masts(T, stone, gold, glow, cloth)
    c = T.sphere(gold, glow)              # gaiola (objeto proprio) + 3 aneis e a estrela (VFX)
    return T, c


def adopt_tower_objects(before):
    """renomeia o que o codigo da Ilha 1 criou: SUM_* -> DS_Sum_*, VFX_SUM_* -> VFX_DSSUM_*; colecao 05 -> 06"""
    dst = fm_lib.coll(COL)
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_DSSUM_" + n[len("VFX_SUM_"):]
            ob["vfx_zone"] = "summon"
        elif n.startswith("SUM_"):
            ob.name = "DS_Sum_" + n[len("SUM_"):]
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


# ------------------------------------------------------------------ pecas pequenas: lanternas e remates
def hang_lamp(metal, glow, top, s=1.0, drop=0.8, yaw=0.0):
    """lanterna de papel com GAIOLA de ferro, pendurada de 'top' (mundo): gancho + tirante, chapeu de 4 aguas com
    remate, prato de cima e bandeja de baixo, 4 montantes e travessas de ferro por FORA do papel aceso (o papel fica
    0,05 atras das travessas: nada coplanar com o Neon). Devolve o centro do papel."""
    top = Vector(top)
    metal.cyl(0.16 * s, 0.14, top - ZZ * 0.05, (0, 0, 0), IRON, 6, bevel=0.0)                       # argola
    hat_top = top - ZZ * drop
    metal.rod(top - ZZ * 0.05, hat_top + ZZ * 0.12, 0.07 * s, IRON, 6)
    c = hat_top - ZZ * (0.5 * s + 0.62 * s)
    hp, hh = 0.48 * s, 0.6 * s
    glow.box((2 * hp, 2 * hp, 2 * hh), c, (0, 0, yaw), PAPER, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = c + Vector((math.cos(yaw) * sx - math.sin(yaw) * sy, math.sin(yaw) * sx + math.cos(yaw) * sy, 0)) * (
                hp + 0.06 * s)
            metal.box((0.15 * s, 0.15 * s, 2 * hh + 0.3 * s), q, (0, 0, yaw), IRON, 0.0)
    for k, off in enumerate((-hh - 0.1 * s, hh + 0.1 * s)):
        metal.box((2 * hp + 0.42 * s, 2 * hp + 0.42 * s, 0.16 * s), c + ZZ * off, (0, 0, yaw), IRON, 0.0)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d = Vector((math.cos(yaw) * sx - math.sin(yaw) * sy, math.sin(yaw) * sx + math.cos(yaw) * sy, 0))
        metal.box((0.1 if sx else 2 * hp + 0.1, 2 * hp + 0.1 if sx else 0.1, 0.1), c + d * (hp + 0.05 * s), (0, 0, yaw),
                  IRON, 0.0)
    metal.cyl(0.95 * s, 0.5 * s, c + ZZ * (hh + 0.18 * s + 0.25 * s), (0, 0, yaw + math.pi / 4), IRON, 4,
              r2=0.22 * s, bevel=0.0)
    metal.ico(0.16 * s, c + ZZ * (hh + 0.18 * s + 0.62 * s), GOLD, 1)
    return c


def giboshi(mb, base, s=1.0, m=GOLD):
    """remate em cebola (giboshi) de pilar de guarda-corpo: colar, bulbo e ponta"""
    b = Vector(base)
    mb.cyl(0.3 * s, 0.14 * s, b + ZZ * 0.07 * s, (0, 0, 0), m, 8, bevel=0.0)
    mb.ico(0.3 * s, b + ZZ * 0.42 * s, m, 1, scale=(1.0, 1.0, 1.15))
    mb.cyl(0.16 * s, 0.4 * s, b + ZZ * 0.86 * s, (0, 0, 0), m, 6, r2=0.0, bevel=0.0)


def toro(st, glow, x, y, z, s=1.0, yaw=0.0):
    """lanterna de pedestal de pedra (toro): base sextavada, fuste com anel, mesa, CAMARA de luz (6 montantes de
    pedra com o papel aceso recuado entre eles, laje de baixo e de cima), chapeu largo de 6 aguas com beiral grosso e
    hoju no remate. Devolve o centro da camara (a luz)."""
    zz = z
    st.cyl(1.05 * s, 0.38 * s, (x, y, zz + 0.19 * s), (0, 0, yaw), "Stone_DS_Dark", 6, r2=0.92 * s, bevel=0.0)
    zz += 0.38 * s
    st.cyl(0.36 * s, 1.55 * s, (x, y, zz + 0.775 * s), (0, 0, yaw), "Stone_DS", 8, r2=0.3 * s, bevel=0.0)
    st.cyl(0.44 * s, 0.16 * s, (x, y, zz + 0.8 * s), (0, 0, yaw), "Stone_DS", 8, bevel=0.0)
    zz += 1.55 * s
    st.cyl(0.62 * s, 0.32 * s, (x, y, zz + 0.16 * s), (0, 0, yaw), "Stone_DS", 6, r2=0.9 * s, bevel=0.0)
    zz += 0.32 * s
    hc = 0.95 * s
    glow.cyl(0.46 * s, hc, (x, y, zz + hc / 2), (0, 0, yaw + math.pi / 6), PAPER, 6, bevel=0.0)
    for k in range(6):
        a = yaw + k * math.pi / 3
        st.box((0.2 * s, 0.24 * s, hc), (x + math.cos(a) * 0.6 * s, y + math.sin(a) * 0.6 * s, zz + hc / 2),
               (0, 0, a), "Stone_DS", 0.0)
    zz += hc
    st.cyl(0.78 * s, 0.2 * s, (x, y, zz + 0.1 * s), (0, 0, yaw), "Stone_DS", 6, bevel=0.0)
    zz += 0.2 * s
    st.cyl(1.42 * s, 0.22 * s, (x, y, zz + 0.11 * s), (0, 0, yaw), "Stone_DS_Dark", 6, bevel=0.0)
    zz += 0.22 * s
    st.cyl(1.36 * s, 0.62 * s, (x, y, zz + 0.31 * s), (0, 0, yaw), "Stone_DS_Dark", 6, r2=0.3 * s, bevel=0.0)
    zz += 0.62 * s
    st.cyl(0.2 * s, 0.16 * s, (x, y, zz + 0.08 * s), (0, 0, yaw), "Stone_DS", 6, bevel=0.0)
    st.ico(0.26 * s, (x, y, zz + 0.36 * s), "Stone_DS", 1, scale=(1, 1, 1.25))
    return Vector((x, y, z + (0.38 + 1.55 + 0.32 + 0.5) * s))


# ------------------------------------------------------------------ podio de santuario (pedra escura + madeira)
def _bays(a, b, step):
    n = max(1, int(math.ceil(abs(b - a) / step - 0.15)))
    return [a + (b - a) * k / n for k in range(n + 1)]


def podium(st, wd, mt, cl):
    """degrau kidan + podio em enxaimel (ver o cabecalho). st = pedra, wd = madeira, mt = ferragens, cl = maku"""
    du, dvb, dvf, ch, dz = DAIS
    pu, pvb, pvf = POD
    # --- degrau (kidan): nucleo de pedra escura + capa de pedra media com focinho de 0,12 (2 alas + fundo)
    right = [(CORR, dvb), (du - ch, dvb), (du, dvb + ch), (du, dvf - ch), (du - ch, dvf), (CORR, dvf)]
    back = [(-CORR, dvb), (CORR, dvb), (CORR, pvb + 0.6), (-CORR, pvb + 0.6)]
    for pc in (right, [(-u, v) for u, v in reversed(right)], back):
        poly = ccw(local_poly(pc))
        st.prism(poly, Z - 0.5, Z + dz - 0.24, "Stone_DS_Dark")
        st.prism(ccw(DL.offset_poly(poly, 0.12)), Z + dz - 0.24, Z + dz, "Stone_DS")
    # --- paineis de pedra (nucleo recuado) e tampo
    r = RECESS
    pieces = [[(CORR, pvb + r), (pu - r, pvb + r), (pu - r, pvf - r), (CORR, pvf - r)],
              [(-pu + r, pvb + r), (-CORR, pvb + r), (-CORR, pvf - r), (-pu + r, pvf - r)],
              [(-CORR, pvb + r), (CORR, pvb + r), (CORR, PV), (-CORR, PV)]]
    for pc in pieces:
        st.prism(ccw(local_poly(pc)), Z + dz - 0.05, Z + 3.05, "Stone_DS_B")
    deck = [[(CORR, pvb), (pu, pvb), (pu, pvf), (CORR, pvf)], [(-pu, pvb), (-CORR, pvb), (-CORR, pvf), (-pu, pvf)],
            [(-CORR, pvb), (CORR, pvb), (CORR, PV), (-CORR, PV)]]
    for pc in deck:
        st.prism(ccw(DL.offset_poly(local_poly(pc), -0.5)), Z + 3.05, Z + DECK, "Stone_DS_Dark")
    # --- enxaimel de madeira escura: soleira, pilares, travessa e beiral-capa (com balanco de 0,35), por face
    faces = []           # (a_uv, b_uv, normal_uv, pilares)
    faces.append(((pu, pvf), (CORR, pvf), (0.0, 1.0)))
    faces.append(((-CORR, pvf), (-pu, pvf), (0.0, 1.0)))
    faces.append(((pu, pvb), (pu, pvf), (1.0, 0.0)))
    faces.append(((-pu, pvf), (-pu, pvb), (-1.0, 0.0)))
    faces.append(((-pu, pvb), (pu, pvb), (0.0, -1.0)))
    posts = []
    for a, b, nrm in faces:
        a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        d = b - a
        ln = d.length
        t = d / ln
        nv = Vector((nrm[0], nrm[1], 0))
        rz = math.atan2(t.y, t.x)
        mid = (a + b) / 2
        for (z0, z1, dep, ext, m) in ((dz, dz + 0.5, 0.5, 0.0, "Wood_DS_Dark"),
                                      (2.62, 3.05, 0.5, 0.0, "Wood_DS_Dark")):
            c = mid - nv * (dep / 2 - 0.02)
            lbox(wd, (ln + ext, dep, z1 - z0), c.x, c.y, (z0 + z1) / 2, m, 0.0, rz)
        # beiral-capa: tabua grossa com balanco (cobre a quina do tampo; 0,12 acima dele)
        c = mid + nv * (0.35 - 0.95 / 2)
        lbox(wd, (ln + (0.7 if ln > 9 else 0.35), 0.95, CORN - 3.05), c.x, c.y, (3.05 + CORN) / 2, "Wood_DS_Dark",
             0.0, rz)
        step = 3.9 if ln > 12 else 3.7
        for k, tt in enumerate(_bays(0.0, ln, step)):
            p = a + t * tt
            key = (round(p.x, 2), round(p.y, 2))
            if key in [q[0] for q in posts]:
                continue
            posts.append((key, nv.copy(), rz))
    for (pu_, pv_), nv, rz in posts:
        # o pilar fica DENTRO da linha da face nos 2 eixos (quina sem dente para fora); nas pontas do corredor da
        # escada ele recua para dentro do podio (o patamar ocupa |u| < CORR)
        cu = max(-pu + 0.27, min(pu - 0.27, pu_))
        cv = max(pvb + 0.27, min(pvf - 0.27, pv_))
        if abs(pv_ - pvf) < 0.01 and abs(cu) < CORR + 0.3:
            cu = math.copysign(CORR + 0.3, pu_)
        lbox(wd, (0.6, 0.6, 2.62 - dz - 0.5), cu, cv, (dz + 0.5 + 2.62) / 2, "Wood_DS_Dark", 0.0, rz)
        on_corner = abs(abs(pu_) - pu) < 0.01 and (abs(pv_ - pvb) < 0.01 or abs(pv_ - pvf) < 0.01)
        c = Vector((cu, cv, 0.0))
        if on_corner or abs(abs(pu_) - CORR) < 0.01 or abs(nv.y - 1.0) < 0.01:
            # kanamono: bracadeiras de ouro velho no pe e na cabeca do pilar (frente e quinas)
            for zc in (dz + 0.62, 2.5):
                lbox(mt, (0.72, 0.72, 0.16), c.x, c.y, zc, GOLD, 0.0, rz)
    # --- maku violeta na frente (2 festoes por vao, presos sob o beiral-capa, 0,1 a frente dos pilares)
    for s in (-1, 1):
        us = _bays(s * CORR, s * pu, 3.7)
        for ua, ub in zip(us, us[1:]):
            for k in range(2):
                u0 = ua + (ub - ua) * k / 2
                u1 = ua + (ub - ua) * (k + 1) / 2
                hwid = abs(u1 - u0) / 2
                pts = [(-hwid, 0.0), (hwid, 0.0)]
                for i in range(1, 6):
                    a = math.pi * i / 6
                    pts.append((hwid * math.cos(a), -0.55 * math.sin(a) - 0.18))
                PK.plate(cl, [(x, zz) for x, zz in pts], P((u0 + u1) / 2, pvf + 0.12, 3.0), XU, ZZ, 0.1,
                         "Cloth_DS_Indigo")
            # cordao de ouro velho no ponto de encontro dos festoes
            lbox(mt, (0.16, 0.16, 0.7), (ua + ub) / 2, pvf + 0.2, 2.68, GOLD, 0.0)
    # --- patamar do portal: pedra escura + laje de caminho com focinho (de PV ate a frente do podio)
    lbox2(st, -CORR, PV, dz - 0.05, CORR, pvf, LAND_Z - 0.3, "Stone_DS_Dark")
    lbox2(st, -CORR, PV, LAND_Z - 0.3, CORR, pvf + 0.12, LAND_Z, "Stone_DS_Path")


def podium_collision():
    A = "DSSumTower"
    du, dvb, dvf, ch, dz = DAIS
    pu, pvb, pvf = POD
    for s in (-1, 1):
        lcol2(A, s * CORR, dvb + ch, -0.6, s * du, dvf - ch, dz)                       # degrau (lados)
        lcol2(A, s * CORR, dvb, -0.6, s * (du - ch), dvf, dz)
        lcol2(A, s * CORR, pvb - 0.35, -0.6, s * (pu + 0.35), pvf + 0.35, CORN)        # podio (lados)
    lcol2(A, -CORR, dvb, -0.6, CORR, pvb - 0.35, dz)                                   # degrau (fundo)
    lcol2(A, -CORR, pvb - 0.35, -0.6, CORR, PV, DECK)                                  # podio (meio, atras do portal)
    lcol2(A, -CORR, PV, -0.2, CORR, LAND_V1, LAND_Z)                                   # patamar do portal


def tower_stair(st, wd, mt):
    """escada da torre com a medida da Ilha 1 (5 x 0,8 de espelho, piso 1,6, 7,6 de largura; o 5o degrau e a frente
    do patamar): pisadas de pedra de caminho com focinho de 0,12 e espelho recuado, banzos de pedra escura inclinados
    com corrimao de madeira escura e pilares de giboshi nas pontas. Colisao: ds_col.stair_col (rampa + guardas)."""
    base = P(0.0, ST_FOOT, 0.0)
    ang = FACE + math.pi
    Fs = Frame(base.x, base.y, base.z, ang)
    rise, tread, n, w = ST_RISE, ST_TREAD, ST_N - 1, ST_W
    TH, NOSE = 0.3, 0.12
    for i in range(n):
        ztop = rise * (i + 1)
        hc = ztop - TH - 0.02
        st.box((tread + 0.02, w - 0.06, hc + 0.5), Fs.p(tread * i + tread / 2 + 0.01, 0, (hc - 0.5) / 2), Fs.r(),
               "Stone_DS", 0.0)
        x0, x1 = tread * i - NOSE, tread * (i + 1) + 0.01
        st.box((x1 - x0, w + 0.04, TH), Fs.p((x0 + x1) / 2, 0, ztop - TH / 2), Fs.r(), "Stone_DS_Path", 0.04)
    # banzos: pedra escura do chao ate 0,9 acima da linha dos focinhos, encostando no podio (x = 4 pisadas)
    xe = tread * n

    def ztop(x):                       # topo do banzo: 0,9 acima da linha dos focinhos
        return min(rise * (x / tread + 1.0), LAND_Z) + 0.9
    for s in (-1, 1):
        y0, y1 = s * (w / 2), s * (w / 2 + 1.2)
        prof = [(-0.5, -0.6), (xe, -0.6), (xe, ztop(xe)), (-0.5, ztop(-0.5))]
        side_prism(st, Fs, prof, min(y0, y1), max(y0, y1), "Stone_DS_Dark")
        yc = s * (w / 2 + 0.6)
        # corrimao de madeira (kasagi) assentado no topo do banzo, entre os pilares
        wd.beam(Fs.p(-0.2, yc, ztop(-0.2) + 0.12), Fs.p(xe - 0.3, yc, ztop(xe - 0.3) + 0.12), 0.9, 0.28,
                "Wood_DS_Dark", 0.0)
        for xp in (-0.05, xe - 0.42):
            zp = ztop(xp) - 0.25
            wd.box((0.62, 0.62, 1.75), Fs.p(xp, yc, zp + 0.875), Fs.r(), "Wood_DS_Dark", 0.0)
            mt.box((0.7, 0.7, 0.14), Fs.p(xp, yc, zp + 1.45), Fs.r(), GOLD, 0.0)
            giboshi(mt, Fs.p(xp, yc, zp + 1.75), 0.9)
    ds_col.stair_col("DSSumTower", (base.x, base.y, base.z), ang, w, ST_N, rise, tread, guards=True, guard_h=4.0)


def podium_lamps(st, glow, mt):
    """2 toro de pedra no podio, ladeando o portal (o lugar dos pedestais de cristal da Ilha 1); luz quente baixa"""
    out = []
    for s in (-1, 1):
        p = P(s * IN_LAMP[0], IN_LAMP[1], DECK)
        out.append(toro(st, glow, p.x, p.y, p.z, 0.95, YAW))
        col_box("DSSumTower", (2.0, 2.0, 4.6), (p.x, p.y, p.z + 2.3), (0, 0, YAW))
    return out


# ------------------------------------------------------------------ escadaria da planta (clareira -> plato)
def plan_stair(st):
    """VISUAL da escada 'Summon' da planta (a colisao e do ds_col: mesmo envelope e cotas). Pisadas de pedra de
    caminho com focinho, espelho recuado, banzos MACICOS de pedra escura do T1 ate 0,9 acima dos focinhos (face
    inclinada continua, nada de caixas em degrau), capa de pedra e pilar de arranque no pe."""
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    rise = L.stair_rise("Summon")
    Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg))
    TH, NOSE = 0.3, 0.12
    for i in range(n):
        ztop = rise * (i + 1)
        hc = ztop - TH - 0.02
        st.box((tread + 0.02, w - 0.06, hc + 0.5), Fs.p(tread * i + tread / 2 + 0.01, 0, (hc - 0.5) / 2), Fs.r(),
               "Stone_DS", 0.0)
        x0, x1 = tread * i - NOSE, tread * (i + 1) + 0.01
        st.box((x1 - x0, w + 0.04, TH), Fs.p((x0 + x1) / 2, 0, ztop - TH / 2), Fs.r(), "Stone_DS_Path", 0.04)
    zt = rise * n
    xe = tread * n + 0.4
    x_flat = tread * ((zt + 0.9 - 0.9) / rise - 1)
    for s in (-1, 1):
        y0, y1 = s * (w / 2), s * (w / 2 + 1.25)
        z_a = rise * (1 - 0.6 / tread) + 0.9
        prof = [(-0.6, -0.6), (xe, -0.6), (xe, zt + 0.9), (x_flat, zt + 0.9), (-0.6, z_a)]
        side_prism(st, Fs, prof, min(y0, y1), max(y0, y1), "Stone_DS_Dark")
        yc = s * (w / 2 + 0.62)
        st.beam(Fs.p(-0.5, yc, z_a + 0.15), Fs.p(x_flat, yc, zt + 0.9 + 0.15), 1.55, 0.3, "Stone_DS", 0.0)
        st.beam(Fs.p(x_flat, yc, zt + 0.9 + 0.15), Fs.p(xe, yc, zt + 0.9 + 0.15), 1.55, 0.3, "Stone_DS", 0.0)
        # pilar de arranque (pedra) com capa
        st.box((1.7, 1.7, 2.1), Fs.p(-1.25, yc, 1.05 - 0.3), Fs.r(), "Stone_DS_Dark", 0.0)
        st.box((2.0, 2.0, 0.34), Fs.p(-1.25, yc, 2.1 - 0.3 + 0.17), Fs.r(), "Stone_DS", 0.0)
        col_box("DSSumTower", (2.0, 2.0, 2.4), Fs.p(-1.25, yc, 1.2), Fs.r())
    return Fs


# ------------------------------------------------------------------ pontezinha sobre o canal
BR_RISE = 1.6
RAIL_HALF = 2.65                  # meio comprimento do guarda-corpo da pontezinha (so a corcova, sobre o canal)


def footbridge(wd, st, mt):
    """pontezinha ARQUEADA de madeira (a planta: L.FOOTBRIDGE): tabuas atravessadas sobre 2 vigas curvas, guarda-corpo
    SO sobre a corcova (o vao do canal: pilares com travessa e corrimao seguindo o arco, giboshi de ouro velho nos 4
    pilares das pontas), rampas de tabua sem guarda nas 2 pontas e encontros de pedra nas cabeceiras. O guarda-corpo
    curto deixa livre a rota SUMMON->CLEARING do ds_layout (sai da ponte na diagonal; folga >= 1,7 do corpo).
    O vao livre sobre os muros do canal (T1 + 0,4) e >= 0,1."""
    (xa0, yb), (xb0, _), w = L.FOOTBRIDGE
    xa, xb = xa0 + 0.4, xb0 - 0.7
    mid, half = (xa + xb) / 2, (xb - xa) / 2

    def zd(x):
        t = (x - mid) / half
        return T1 + 0.1 + BR_RISE * (1.0 - t * t)

    def slope(x):
        return -2.0 * BR_RISE * (x - mid) / (half * half)
    hw = w / 2 - 0.25                 # meia largura das tabuas
    npl = int(round((xb - xa) / 0.78))
    pl = (xb - xa) / npl
    for k in range(npl):
        x = xa + pl * (k + 0.5)
        a = math.atan(slope(x))
        wd.box((pl - 0.09, 2 * hw - 0.5, 0.26), (x, yb, zd(x) - 0.13), (0, -a, 0), "Wood_DS_Mid", 0.0)
    xs = [xa + (xb - xa) * i / 8 for i in range(9)]
    for s in (-1, 1):
        for x0, x1 in zip(xs, xs[1:]):
            wd.beam((x0, yb + s * (hw - 0.6), zd(x0) - 0.5), (x1, yb + s * (hw - 0.6), zd(x1) - 0.5), 0.5, 0.45,
                    "Wood_DS_Dark", 0.0)
            # testeira lateral (mimi-ita): esconde as pontas das tabuas e desenha o arco de perfil
            wd.beam((x0, yb + s * (hw - 0.12), zd(x0) - 0.12), (x1, yb + s * (hw - 0.12), zd(x1) - 0.12), 0.26, 0.5,
                    "Wood_DS_Dark", 0.0)
    # guarda-corpo: 5 pilares por lado, travessa e corrimao seguindo o arco
    yr = hw + 0.2
    pxs = [mid - RAIL_HALF, mid - 0.9, mid + 0.9, mid + RAIL_HALF]
    H, TOP = 2.3, 0.3
    for s in (-1, 1):
        y = yb + s * yr
        for i, x in enumerate(pxs):
            end = i in (0, len(pxs) - 1)
            hh = H + (0.35 if end else 0.0)
            wd.box((0.44, 0.44, hh + 0.4), (x, y, zd(x) - 0.4 + (hh + 0.4) / 2), (0, 0, 0), "Wood_DS_Dark", 0.0)
            if end:
                mt.box((0.52, 0.52, 0.14), (x, y, zd(x) + hh - 0.25), (0, 0, 0), GOLD, 0.0)
                giboshi(mt, (x, y, zd(x) + hh), 0.85)
        for x0, x1 in zip(pxs, pxs[1:]):
            wd.beam((x0, y, zd(x0) + H - TOP / 2), (x1, y, zd(x1) + H - TOP / 2), 0.46, TOP, "Wood_DS_Dark", 0.0)
            wd.beam((x0, y, zd(x0) + 1.15), (x1, y, zd(x1) + 1.15), 0.22, 0.22, "Wood_DS_Mid", 0.0)
    # encontros de pedra nas cabeceiras (a tabua da ponta assenta neles)
    for xe, sg in ((xa, -1), (xb, 1)):
        st.box((1.7, w + 0.6, 0.52), (xe + sg * 0.45, yb, T1 - 0.24), (0, 0, 0), "Stone_DS_Dark", 0.0)
        st.box((1.9, w + 0.8, 0.14), (xe + sg * 0.45, yb, T1 + 0.09), (0, 0, 0), "Stone_DS", 0.0)
    # colisao: o arco em 4 rampas (encostam no piso T1 nas pontas) + parapeitos
    A = "DS_SumBridge"
    pts = [(xa - 1.0, T1)] + [(x, zd(x)) for x in (xa + half * 0.5, mid, xb - half * 0.5)] + [(xb + 0.8, T1)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        col_ramp(A, (x0, yb, z0), (x1, yb, z1), 2 * hw, thick=1.0)
    for s in (-1, 1):
        col_box(A, (2 * RAIL_HALF + 0.44, 0.6, 4.8), (mid, yb + s * yr, T1 + 2.4))


# ------------------------------------------------------------------ guarda-corpo do plato (koran baixo)
def _rail_skip(x, y):
    """trechos sem guarda-corpo: a boca da escada da planta e o mirante coberto (o banco/guarda dele assume)"""
    if x < 153.5 and abs(y - 300.0) < 7.7:
        return True
    sx, sy, sw, sd = SHELTER
    return abs(x - sx) < sw / 2 + 0.9 and abs(y - sy) < sd / 2 + 0.9


def plateau_rail(wd, mt):
    """pilares 0,42 a cada <= 3,2 (quinas sempre), travessa (nuki) passante e corrimao largo (kasagi) por cima; nas
    pontas dos trechos (boca da escada, mirante) pilar mais alto com giboshi. Colisao: parede fina por trecho."""
    ring = ccw(DL.offset_poly(ccw(L.SUMMON_PLAT), -RAIL_IN))
    H = 2.4
    runs = []
    n = len(ring)
    for i in range(n):
        a, b = Vector((*ring[i], Z)), Vector((*ring[(i + 1) % n], Z))
        d = b - a
        ln = d.length
        k = max(2, int(ln / 0.25))
        cur = None
        for j in range(k + 1):
            p = a + d * (j / k)
            if _rail_skip(p.x, p.y):
                if cur:
                    runs.append(cur)
                cur = None
                continue
            if cur is None:
                cur = [p, p]
            cur[1] = p
        if cur:
            runs.append(cur)
    posts = {}
    spans = []
    for a, b in runs:
        ln = (b - a).length
        if ln < 0.6:
            continue
        m = max(1, int(math.ceil(ln / 3.2)))
        ps = [a + (b - a) * (j / m) for j in range(m + 1)]
        for p in ps:
            posts.setdefault((round(p.x, 1), round(p.y, 1)), p)
        spans += list(zip(ps, ps[1:]))
    # pontas de trecho (pilares altos com giboshi): as que nao sao partilhadas por 2 trechos
    ends = {}
    for a, b in runs:
        for p in (a, b):
            kk = (round(p.x, 1), round(p.y, 1))
            ends[kk] = ends.get(kk, 0) + 1
    for kk, p in posts.items():
        tall = ends.get(kk, 0) == 1
        hh = H + (0.5 if tall else 0.0)
        wd.box((0.42, 0.42, hh + 0.3), (p.x, p.y, Z - 0.3 + (hh + 0.3) / 2), (0, 0, 0), "Wood_DS_Dark", 0.0)
        if tall:
            mt.box((0.5, 0.5, 0.12), (p.x, p.y, Z + hh - 0.22), (0, 0, 0), GOLD, 0.0)
            giboshi(mt, (p.x, p.y, Z + hh), 0.8)
    for a, b in spans:
        d = b - a
        rz = math.atan2(d.y, d.x)
        c = (a + b) / 2
        wd.box((d.length + 0.5, 0.5, 0.26), (c.x, c.y, Z + H - 0.13 + 0.01), (0, 0, rz), "Wood_DS_Dark", 0.0)
        wd.box((d.length + 0.2, 0.2, 0.22), (c.x, c.y, Z + 1.2), (0, 0, rz), "Wood_DS_Mid", 0.0)
    A = "DS_SumRail"
    for a, b in runs:
        d = b - a
        if d.length < 0.6:
            continue
        c = (a + b) / 2
        col_box(A, (d.length + 0.4, 0.5, 3.4), (c.x, c.y, Z + 1.4), (0, 0, math.atan2(d.y, d.x)))
    return len(posts)


# ------------------------------------------------------------------ mirante coberto (azumaya) na borda NE
def _irimoya(mb, Fs, w, d, z0, rise, over, th=0.36):
    """telhado IRIMOYA do pavilhao, na escala dele (o do blockout tem cumeeira de casa): saia de 4 aguas com espessura,
    empena de 2 aguas por cima com o triangulo de madeira escura recuado, cumeeira fina (0,55) com onigawara baixas e
    testeira (hana-kakushi) em volta do beiral"""
    from ds_blockout import faces_solid
    W, Dd = w / 2 + over, d / 2 + over
    z1 = z0 + rise * 0.55
    zr = z0 + rise
    hd = 0.45 * Dd
    hw = max(W - (Dd - hd), W * 0.55)
    co = [Fs.p(-W, -Dd, z0), Fs.p(W, -Dd, z0), Fs.p(W, Dd, z0), Fs.p(-W, Dd, z0),
          Fs.p(-hw, -hd, z1), Fs.p(hw, -hd, z1), Fs.p(hw, hd, z1), Fs.p(-hw, hd, z1),
          Fs.p(-W, -Dd, z0 - th), Fs.p(W, -Dd, z0 - th), Fs.p(W, Dd, z0 - th), Fs.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7],
          [8, 9, 1, 0], [9, 10, 2, 1], [10, 11, 3, 2], [11, 8, 0, 3], [11, 10, 9, 8]]
    faces_solid(mb, co, fs, "Roof_DS_Tile")
    # canais de telha em relevo na saia (o ladrilhado vem da geometria): costelas do beiral ate o topo da saia
    for sy in (-1, 1):
        for i in range(9):
            x = -hw * 0.92 + 2 * hw * 0.92 * i / 8
            a, b = Vector(Fs.p(x * W / hw * 0.97, sy * Dd, z0)), Vector(Fs.p(x, sy * hd, z1))
            nrm = (b - a).cross(Vector(Fs.p(1, 0, 0)) - Vector(Fs.p(0, 0, 0))).normalized() * (-sy)
            if nrm.z < 0:
                nrm = -nrm
            mb.beam(a + nrm * 0.07 + (b - a) * 0.01, b + nrm * 0.07, 0.22, 0.14, "Roof_DS_Ridge", 0.0)
    for sx in (-1, 1):
        for i in range(4):
            yy = -hd * 0.85 + 2 * hd * 0.85 * i / 3
            a, b = Vector(Fs.p(sx * W, yy * Dd / hd * 0.97, z0)), Vector(Fs.p(sx * hw, yy, z1))
            nrm = (b - a).cross(Vector(Fs.p(0, 1, 0)) - Vector(Fs.p(0, 0, 0))).normalized()
            if nrm.z < 0:
                nrm = -nrm
            mb.beam(a + nrm * 0.07 + (b - a) * 0.01, b + nrm * 0.07, 0.22, 0.14, "Roof_DS_Ridge", 0.0)
    gw = hw + 0.5
    co = [Fs.p(-gw, -hd - 0.35, z1 - 0.2), Fs.p(gw, -hd - 0.35, z1 - 0.2), Fs.p(gw, 0, zr), Fs.p(-gw, 0, zr),
          Fs.p(gw, hd + 0.35, z1 - 0.2), Fs.p(-gw, hd + 0.35, z1 - 0.2),
          Fs.p(-gw, -hd - 0.35, z1 - 0.2 - th), Fs.p(gw, -hd - 0.35, z1 - 0.2 - th),
          Fs.p(gw, hd + 0.35, z1 - 0.2 - th), Fs.p(-gw, hd + 0.35, z1 - 0.2 - th)]
    fs = [[0, 1, 2, 3], [4, 5, 3, 2], [6, 7, 1, 0], [8, 9, 5, 4], [7, 8, 4, 2, 1], [9, 6, 0, 3, 5], [9, 8, 7, 6]]
    faces_solid(mb, co, fs, "Roof_DS_Tile")
    for sx in (-1, 1):
        x = sx * (gw - 0.45)
        co = [Fs.p(x, -hd, z1 - 0.05), Fs.p(x, hd, z1 - 0.05), Fs.p(x, 0, zr - 0.45),
              Fs.p(x - sx * 0.25, -hd, z1 - 0.05), Fs.p(x - sx * 0.25, hd, z1 - 0.05), Fs.p(x - sx * 0.25, 0, zr - 0.45)]
        faces_solid(mb, co, [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]], "Wood_DS_Dark")
        # onigawara baixa: placa que abre para cima (trapezio), na ponta da cumeeira
        xo = sx * (gw + 0.12)
        PK.plate(mb, [(-0.32, -0.25), (0.32, -0.25), (0.46, 0.55), (0.3, 0.72), (-0.3, 0.72), (-0.46, 0.55)],
                 Fs.p(xo, 0, zr + 0.1), Vector(Fs.p(0, 1, 0)) - Vector(Fs.p(0, 0, 0)), ZZ, 0.36, "Roof_DS_Ridge")
    mb.box((2 * gw + 0.3, 0.6, 0.5), Fs.p(0, 0, zr + 0.1), Fs.r(), "Roof_DS_Ridge", 0.0)
    for sy in (-1, 1):
        mb.box((2 * W + 0.12, 0.16, th + 0.12), Fs.p(0, sy * (Dd + 0.06), z0 - th / 2), Fs.r(), "Wood_DS_Dark", 0.0)
    for sx in (-1, 1):
        mb.box((0.16, 2 * Dd + 0.12, th + 0.12), Fs.p(sx * (W + 0.06), 0, z0 - th / 2), Fs.r(), "Wood_DS_Dark", 0.0)


def shelter(wd, st, rf, mt, glow, cl):
    sx, sy, w, d = SHELTER
    Fs = Frame(sx, sy, Z, 0.0)
    A = "DS_SumShelter"
    px, py = w / 2 - 0.35, d / 2 - 0.35
    HP = 6.2
    for ax in (-1, 1):
        for ay in (-1, 1):
            st.box((0.95, 0.95, 0.45), Fs.p(ax * px, ay * py, 0.2), Fs.r(), "Stone_DS_Dark", 0.0)
            wd.box((0.5, 0.5, HP - 0.42), Fs.p(ax * px, ay * py, 0.42 + (HP - 0.42) / 2), Fs.r(), "Wood_DS_Dark", 0.0)
            col_box(A, (0.7, 0.7, HP), Fs.p(ax * px, ay * py, HP / 2), Fs.r())
    # nuki passantes (com as pontas para fora dos pilares) e frechais (keta) ao longo de x, vigas (hari) em y
    for ay in (-1, 1):
        wd.box((2 * px + 1.3, 0.3, 0.42), Fs.p(0, ay * py, 5.25), Fs.r(), "Wood_DS_Dark", 0.0)
        wd.box((2 * px + 2.0, 0.52, 0.5), Fs.p(0, ay * py, HP + 0.25), Fs.r(), "Wood_DS_Dark", 0.0)
    for ax in (-1, 1):
        wd.box((0.3, 2 * py + 1.3, 0.42), Fs.p(ax * px, 0, 5.25), Fs.r(), "Wood_DS_Dark", 0.0)
        wd.box((0.48, 2 * py + 0.5, 0.44), Fs.p(ax * px, 0, HP - 0.22), Fs.r(), "Wood_DS_Dark", 0.0)
    wd.box((0.4, 2 * py + 0.5, 0.4), Fs.p(0, 0, HP - 0.2), Fs.r(), "Wood_DS_Dark", 0.0)       # viga do meio
    # caibros a mostra sob o beiral dos lados longos
    over = 1.25
    for ay in (-1, 1):
        for k in range(9):
            x = -px - 0.5 + (2 * px + 1.0) * k / 8
            wd.beam(Fs.p(x, ay * (py - 0.1), HP + 0.5), Fs.p(x, ay * (d / 2 + over - 0.2), HP + 0.5 - 0.3), 0.2, 0.26,
                    "Wood_DS_Dark", 0.0)
    _irimoya(rf, Fs, w - 0.2, d - 0.2, HP + 0.95, 3.1, over)
    # bancos nos lados de FORA (norte e leste: virados para o vazio) + guarda (corrimao) atras deles
    for side in ("N", "E"):
        if side == "N":
            a, b, n_out = Fs.p(-px + 0.35, py - 0.55, 0), Fs.p(px - 0.35, py - 0.55, 0), Vector((0, 1, 0))
        else:
            a, b, n_out = Fs.p(px - 0.55, -py + 0.35, 0), Fs.p(px - 0.55, py - 1.05, 0), Vector((1, 0, 0))
        d_ = b - a
        rz = math.atan2(d_.y, d_.x)
        c = (a + b) / 2
        wd.box((d_.length, 0.95, 0.16), (c.x, c.y, Z + 1.45), (0, 0, rz), "Wood_DS_Mid", 0.0)
        for t in (0.08, 0.5, 0.92):
            q = a + d_ * t
            wd.box((0.3, 0.7, 1.37), (q.x, q.y, Z + 0.685), (0, 0, rz), "Wood_DS_Dark", 0.0)
        g = c + n_out * 0.62
        wd.box((d_.length + 0.6, 0.36, 0.26), (g.x, g.y, Z + 2.55), (0, 0, rz), "Wood_DS_Dark", 0.0)
        wd.box((d_.length + 0.4, 0.2, 0.2), (g.x, g.y, Z + 1.85), (0, 0, rz), "Wood_DS_Mid", 0.0)
        col_box(A, (d_.length + 0.8, 1.6, 1.45), (c.x + n_out.x * 0.3, c.y + n_out.y * 0.3, Z + 0.72), (0, 0, rz))
        col_box(A, (d_.length + 0.8, 0.5, 3.4), (g.x, g.y, Z + 1.7), (0, 0, rz))
    # maku violeta no lado de dentro (sul: de frente para a torre), 3 festoes sob o frechal
    for k in range(3):
        u0 = -px + 2 * px * k / 3
        u1 = -px + 2 * px * (k + 1) / 3
        hwid = (u1 - u0) / 2
        pts = [(-hwid, 0.0), (hwid, 0.0)]
        for i in range(1, 6):
            a = math.pi * i / 6
            pts.append((hwid * math.cos(a), -0.6 * math.sin(a) - 0.2))
        PK.plate(cl, pts, Fs.p((u0 + u1) / 2, -py - 0.32, HP - 0.02), Vector((1, 0, 0)), ZZ, 0.1, "Cloth_DS_Indigo")
    # lanterna pendurada da viga do meio
    c = hang_lamp(mt, glow, Fs.p(0, 0, HP - 0.4), 0.9, drop=0.5, yaw=0.0)
    light("L_DSProp_Lamp_SumMirante", "POINT", tuple(c), 70.0, WARM, 0.3)


# ------------------------------------------------------------------ GLICINIA (familia do jogo; o ds_veg reaproveita)
def _bell(mb, a, b, ra, rb, m, n=5, rot=0.0, cap_a=True):
    """tronco de cone de a (raio ra) ate b (raio rb): uma camada de petalas do cacho (cap_a=False: o topo fica
    escondido dentro da camada de cima e nao precisa de tampa)"""
    bm = mb.bm
    d = (b - a).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u)
    RA = [bm.verts.new(a + (u * math.cos(rot + math.tau * j / n) + v * math.sin(rot + math.tau * j / n)) * ra)
          for j in range(n)]
    RB = [bm.verts.new(b + (u * math.cos(rot + math.tau * j / n) + v * math.sin(rot + math.tau * j / n)) * rb)
          for j in range(n)]
    for j in range(n):
        bm.faces.new((RA[j], RA[(j + 1) % n], RB[(j + 1) % n], RB[j]))
    if cap_a:
        bm.faces.new(RA)
    bm.faces.new(RB[::-1])
    mb._post(RA + RB, m, None, 0, 1)


def _blob(mb, c, rx, ry, rz, m, nu=7, nv=3, rot=0.0):
    """massa achatada (elipsoide de poucos lados) de folha/flor"""
    bm = mb.bm
    rings = []
    for i in range(1, nv):
        ph = -math.pi / 2 + math.pi * i / nv
        cz, rr = math.sin(ph), math.cos(ph)
        rings.append([bm.verts.new((c.x + math.cos(rot + math.tau * j / nu) * rx * rr,
                                    c.y + math.sin(rot + math.tau * j / nu) * ry * rr, c.z + rz * cz))
                      for j in range(nu)])
    bot = bm.verts.new((c.x, c.y, c.z - rz))
    top = bm.verts.new((c.x, c.y, c.z + rz))
    for j in range(nu):
        j2 = (j + 1) % nu
        bm.faces.new((rings[0][j2], rings[0][j], bot))
        bm.faces.new((rings[-1][j], rings[-1][j2], top))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(nu):
            j2 = (j + 1) % nu
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    mb._post([v for r in rings for v in r] + [bot, top], m, None, 0, 1)


def raceme(mb, top, vis, r0, rng, tones=WIS_TONES, step=0.6):
    """CACHO PENDENTE de glicinia (proporcao ~1:5, esguio): 3-5 camadas de petalas em sino de 5 lados (borda larga
    embaixo, topo estreito escondido 35% dentro da camada de cima), cheio no alto e afinando, eixo que pende reto junto
    do galho e abre na ponta (sway quadratico) com zigue-zague leve, cor por camada (fundo -> medio -> claro) e um
    botao rombo na ponta. 'top' fica escondido 0,35 dentro do galho/massa."""
    top = Vector(top)
    n = max(3, min(5, int(round(vis / step))))
    hide = 0.35
    total = vis + hide
    sway = Vector((rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0.0))
    a_ = rng.uniform(0, math.tau)
    lat = Vector((math.cos(a_), math.sin(a_), 0.0))
    pts, rad = [top], [r0 * 0.45]
    for k in range(n):
        f = (hide + vis * (k + 1) / n) / total
        pts.append(top - ZZ * (total * f) + sway * (f * f) + lat * (0.07 * (1 if k % 2 else -1)))
        rad.append(r0 * (1.1 + (0.5 - 1.1) * k / (n - 1)))
    rot = rng.uniform(0, math.tau)
    for k in range(n):
        t = k / (n - 1)
        m = tones[0] if t < 0.3 else (tones[1] if t < 0.68 else tones[2])
        rim, rk = pts[k + 1], rad[k + 1]
        a = pts[0] if k == 0 else pts[k] + (pts[k] - rim) * 0.35
        _bell(mb, a, rim, rk * 0.4, rk, m, rot=rot + 0.6 * k, cap_a=(k == 0))
    rim, rl = pts[-1], rad[-1]
    d = (pts[-1] - pts[-2]).normalized()
    _bell(mb, rim - d * rl * 0.2, rim + d * rl * 0.7, rl * 0.66, rl * 0.25, tones[2], rot=rot, cap_a=False)
    return pts[-1]


def wisteria_tree(mb, x, y, z, rng, h=10.5, spread=6.4, face=0.0, n_br=4, bark="Bark_DS", leaf="Leaf_DS_Broad",
                  tones=WIS_TONES, col_area=None):
    """GLICINIA (acento): tronco-lider retorcido em S com raiz alargada; no alto ele abre em n_br GALHOS em
    guarda-chuva (sobem, arqueiam e caem nas pontas). Folhagem em TUFOS irregulares (3 massas achatadas desencontradas
    por tufo, no meio e na ponta de cada galho, + 1 tufo sobre a forquilha), com massas de flor no tom fundo saindo de
    alguns tufos, e CACHOS PENDENTES esguios (raceme) pendurados de verdade: cortina longa embaixo dos tufos da ponta,
    cachos medios nos do meio e cachos curtos direto da face de baixo do galho nu. face = rumo (rad) para onde a copa
    pende mais (o lado de quem olha). Devolve a lista das pontas dos cachos."""
    base = Vector((x, y, z))
    ht = h * 0.6
    # tronco em S (2 curvas) + raiz
    ph = rng.uniform(0, math.tau)
    tr, rr = [], []
    for i in range(8):
        f = i / 7
        off = Vector((math.cos(ph) * math.sin(f * 5.2) * 0.55, math.sin(ph) * math.sin(f * 5.2 + 0.8) * 0.45, 0.0))
        tr.append(base + off * (0.3 + f) + ZZ * (ht * f - 0.3 * (1 - f)))
        rr.append(0.88 - 0.42 * f)
    PK.taper_tube(mb, tr, rr, bark, n=8)
    PK.cone(mb, base - ZZ * 0.3, base + ZZ * 1.0, 1.3, 0.82, bark, 8)
    crown = tr[-1]
    racemes = []
    used = []

    def hang(p, vis, r0):
        for q in used:
            if (Vector((p.x, p.y)) - Vector((q.x, q.y))).length < 2.0 * r0 + 0.3:
                return
        used.append(p)
        racemes.append(raceme(mb, p, vis, r0, rng, tones))

    def tuft(c, s_, rot, flower):
        """tufo: 3 massas achatadas desencontradas (silhueta irregular, nao disco); devolve o raio util"""
        for j in range(3):
            aa = rot + j * 2.1 + rng.uniform(-0.4, 0.4)
            off = Vector((math.cos(aa), math.sin(aa), 0.0)) * s_ * 0.7
            _blob(mb, c + off + ZZ * rng.uniform(-0.12, 0.28), s_ * rng.uniform(0.95, 1.15), s_ * rng.uniform(0.75, 0.9),
                  s_ * 0.52, leaf, nu=8, rot=aa)
        if flower:
            # massa de flor no tom fundo saindo do tufo para fora e para baixo (de onde a cortina nasce)
            aa = rot + rng.uniform(-0.5, 0.5)
            off = Vector((math.cos(aa), math.sin(aa), 0.0)) * s_ * 1.0
            _blob(mb, c + off - ZZ * s_ * 0.22, s_ * 0.8, s_ * 0.66, s_ * 0.46, tones[0], nu=8, rot=aa)
        return s_ * 1.5

    for k in range(n_br):
        a = face + math.tau * k / n_br + rng.uniform(-0.35, 0.35)
        dvec = Vector((math.cos(a), math.sin(a), 0.0))
        # o lado de 'face' estica mais (a cortina de cachos fica para quem olha)
        Ln = spread * rng.uniform(0.82, 1.0) * (1.0 + 0.18 * max(0.0, math.cos(a - face)))
        br = [crown, crown + dvec * (Ln * 0.3) + ZZ * 1.5, crown + dvec * (Ln * 0.65) + ZZ * 1.9,
              crown + dvec * Ln + ZZ * 1.1]
        PK.taper_tube(mb, br, [0.42, 0.34, 0.26, 0.18], bark, n=6)
        # tufos no meio e na ponta do galho (o galho atravessa o tufo) + cachos embaixo
        for t, s_, ncl, vr in ((0.55, 1.05, 4, (1.7, 2.5)), (0.97, 1.25, 7, (2.3, 3.6))):
            p = br[1].lerp(br[2], (t - 0.3) / 0.35) if t < 0.65 else br[2].lerp(br[3], (t - 0.65) / 0.35)
            c = p + ZZ * 0.25
            R = tuft(c, s_, a, t > 0.9 or k % 2 == 0)
            for j in range(ncl):
                aa = a + (j - (ncl - 1) / 2) * (4.2 / ncl) + rng.uniform(-0.2, 0.2)
                rad = rng.uniform(0.35, 0.85) * R * 0.8
                q = Vector((c.x + math.cos(aa) * rad, c.y + math.sin(aa) * rad, c.z - s_ * 0.4 + 0.3))
                hang(q, rng.uniform(*vr), rng.uniform(0.3, 0.38))
        # cachos curtos direto da face de baixo do galho nu (o galho le como galho, com cachos pendentes)
        for t in (0.3, 0.6, 0.85):
            p = br[1].lerp(br[2], t)
            hang(p - ZZ * 0.18, rng.uniform(1.3, 2.0), 0.3)
    # tufo do alto sobre a forquilha
    tuft(crown + ZZ * 1.7, 1.35, face, False)
    if col_area:
        col_box(col_area, (1.9, 1.9, ht), (x, y, z + ht / 2))
    return racemes


def wisterias(mb):
    """as 2 glicinias do plano no plato (L.WISTERIA[:2]); a copa pende para o lado da escada/clareira (oeste) e
    para a torre"""
    out = []
    for i, (x, y) in enumerate(L.WISTERIA[:2]):
        rng = random.Random(4100 + i)
        face = math.atan2(300.0 - y, -0.6 * abs(300.0 - y))      # para a torre e para o oeste
        out += wisteria_tree(mb, x, y, Z, rng, h=10.5, spread=6.2, face=face, col_area="DS_SumWisteria")
    return out


# ------------------------------------------------------------------ build
def build():
    """a zona inteira em POUCOS objetos por familia de material (orcamento de MeshParts: 1 por material por objeto):
    pedra, madeira (+ telhado do mirante), metal (ouro velho + ferro), brilho (portal, estrela, violeta, papel), pano
    (estandartes + maku) e glicinias; a gaiola da esfera e os VFX saem do codigo da Ilha 1. Tudo e fechado DENTRO do
    tower_palette (os nomes DS nao estao no apelido; os da Ilha 1 viram DS)."""
    before = {o.name for o in bpy.data.objects}
    st = MB("DS_Sum_Stone", COL, random.Random(7401), detail="near")
    wd = MB("DS_Sum_Wood", COL, random.Random(7402), detail="near")
    mt = MB("DS_Sum_Metal", COL, random.Random(7403), detail="near")
    gl = MB("DS_Sum_Glow", COL, random.Random(7404), detail="hero")
    cl = MB("DS_Sum_Cloth", COL, random.Random(7405), detail="near")
    wv = MB("DS_Sum_Wisteria", COL, random.Random(7410), detail="near")
    with tower_palette():
        T, c = build_tower(st, mt, gl, cl)
        podium(st, wd, mt, cl)
        tower_stair(st, wd, mt)
        lamps = podium_lamps(st, gl, mt)
        plan_stair(st)
        footbridge(wd, st, mt)
        tops = [toro(st, gl, x, y, Z, 0.9, 0.0) for x, y in TOP_TORO]
        nposts = plateau_rail(wd, mt)
        shelter(wd, st, wd, mt, gl, cl)
        wisterias(wv)
        for mb in (st, wd, mt, gl, cl, wv):
            mb.finish()
    adopt_tower_objects(before)
    tower_collision(T)
    podium_collision()
    for i, ((x, y), cc) in enumerate(zip(TOP_TORO, tops)):
        col_box("DSSumTower", (1.9, 1.9, 5.0), (x, y, Z + 2.5))
        light("L_DSProp_Lamp_SumTop_%d" % i, "POINT", tuple(cc), 120.0, WARM, 0.3)
    # luzes de dia (4): nucleo azul do portal, estrela (quente, contida), 2 toro do podio
    # ONDA 3c: nucleo 1200 -> 450 e estrela 900 -> 160 (os mesmos numeros do passe global ds_lights)
    light("L_DSSum_Core", "POINT", tuple(P(0.0, PV + 3.0, 9.0)), 450.0, (0.36, 0.52, 1.0), 1.0)
    light("L_DSSum_Star", "POINT", tuple(c), 160.0, (1.0, 0.70, 0.36), 1.2)
    for n, p in zip(("L_DSSum_Lamp_L", "L_DSSum_Lamp_R"), lamps):
        light(n, "POINT", tuple(p), 150.0, WARM, 0.3)
    print("DS_SUMMON ok: guarda-corpo %d pilares" % nposts)
