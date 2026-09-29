# sg_dungeon - ZONA DUNGEON da Ilha 3 (Shadow Garden). build() substitui sg_blockout.dungeon (inclusive as colisoes e as
# luzes dela). Prefixo SG_Dun_, colecao 17_DUNGEON, VFX_SGDUN_* em 12_VFX_HELPERS. A dungeon e a "corrida de mineracao"
# periodica do jogo (XX:00 / XX:30): o jogador entra pelo PORTAL (vortice no fundo da caverna, superficie, P3) e o jogo o
# leva para as 3 SALAS modulares escondidas dentro da rocha (piso DUN_Z 6,0; teto DUN_CEIL 28); minera nos DUN_ORE_* e
# sai pelo portal de saida da R3. O sistema e do jogo: aqui so o LUGAR. NAO modela minerio.
# v3 (2026-09-29, referencia dominante refs/v2/ref2_dungeon_cave.png): a portaria e uma BOCA DE CAVERNA.
# ACABAMENTO (2026-09-29): CAVERNA ANTIGA EM RUINAS COM MAGIA QUE SURGE DE DENTRO. Gradiente de brilho: EXTERIOR quase
# natural (so lanternas quentes e o emblema) -> BOCA (cristal pendurado, fios que se apagam em tracos) -> TUNEL forte
# (veios que saem do vortice, cristais mais densos no fundo, portal). Sem brilho a entrada se sustenta pela forma.
#   1. MASSA DE ROCHA NATURAL em ESTRATOS (strata_rock): juntas globais com mergulho leve, camada dura saliente / mole
#      recuada, topo chanfrado de cada camada, degraus que recuam para o centro; topos de liquen com pinheiros. Nada de
#      veio ou cristal por fora. Dentro da pegada DUNGEON_HOUSE + DUNGEON_CAVE_MASS.
#   2. RUINA na boca: ombreiras de cantaria em fiadas, imposta de obsidiana, arco ogival de ADUELAS violeta sobre nucleo
#      escuro, ARCO EXTERNO de cantaria PARTIDO a leste, FECHO de obsidiana com o emblema (sg_emblem.plaque); o cristal
#      VFX_SGDUN_MouthCrystal pende do fecho por corrente. Pilar oeste inteiro com o estandarte; pilar LESTE partido
#      (quebra em degrau) com o capitel, uma fiada e uma aduela caidos no patio (RUBBLE, colisao propria).
#   3. TUNEL: casca de rocha com ESTRATOS continuos (cristas ao longo do tunel), gradiente rocha natural -> violeta
#      profundo; os primeiros metros revestidos de CANTARIA que termina em degraus partidos (encontro ruina x caverna);
#      veios que sobem do vortice e morrem perto da boca; cristais; piso de marmore negro com 2 fios que nascem dentro;
#      VORTICE com anel escuro sobre o estrado de 2 degraus (colisao casada).
#   4. APROXIMACAO: ferradura + corredor de lajes de marmore negro SEM energia; 2 pares de MARCOS de pedra com cinta de
#      ferro e correntes presas em ARGOLAS aos pilares; lanternas quentes. Linhas do andador livres (_approach_check).
#   5. SALAS (R1 chegada 36 x 36, R2 mineracao 44 x 44, R3 camara final 44 x 44) com o MESMO kit: parede com pilastras
#      e arcos ogivais cegos, colunas de canto, cornija, tochas, piso de lajes com friso, abobada ogival de bercos com
#      nervuras. Vaos de ligacao 12 x 12 (timpano com o emblema). R1 portal de chegada (aceso); R3 portal de saida (a
#      espiral e objeto proprio SG_Dun_R3_ExitSpiral que o jogo liga em FINISHING), altar = medalhao embutido no piso.
#   Colisao propria (caixas): massa de rocha, paredes da portaria com o vao da boca, paredes/teto do tunel, estrado,
#   ombreiras, pilares, pedestais, lanternas; salas (piso, paredes com vaos, teto). Nada colidivel a menos de 5 dos
#   DUN_ORE_* ate piso+12 (ccol()). Luzes (7): vortice, violeta DENTRO da boca, lanternas da boca (quente); salas 4.
import math, random
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light
import fm_lib
import sg_layout as L
import sg_emblem as EM
import sg_veg as VEG

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (3; os pinheiros trazem 2 do sg_veg)
NEW_MATS = {
    "Stone_SGDunVault": (S(34, 38, 62), 0.8, 0.0, 0, None, 0.06),      # navy escuro: abobadas, fustes dos pilares
    "SG_DunVoid_Glow": (S(46, 26, 104), 0.3, 0.0, 1.0, S(56, 30, 124), 0.0),   # fundo do vortice (violeta profundo)
    "Stone_SGDunCaveDeep": (S(40, 24, 74), 0.8, 0.0, 0, None, 0.06),          # pedra violeta profunda do fundo do tunel
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

CS, TR, BL, FL = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Block", "Stone_SG_Floor"
VA, VO = "Stone_SGDunVault", "SG_DunVoid_Glow"
NAVY, SLATE, SV, IR = "Roof_SG_Navy", "Roof_SG_Slate", "Metal_SG_Silver", "Metal_SG_Iron"
GL, WW, VG = "Lantern_Glow", "Window_Warm", "SG_Violet_Glow"
# paleta de identidade (sg_lib.SMATS, refinamento): funcao de cada material na dungeon
OB, MBK, VS, BI = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Stone_SG_Violet", "Metal_SG_BlackIron"
VD, RG = "SG_VioletDeep_Glow", "SG_Rune_Glow"

P3 = L.P3
HX, HY, HW, HD = L.DUNGEON_HOUSE                 # 100, 72, 26, 26
HT = 3.0                                         # espessura das paredes da portaria
HX0, HX1, HY0, HY1 = HX - HW / 2, HX + HW / 2, HY - HD / 2, HY + HD / 2      # 87..113 x 59..85
IX0, IX1, IY0, IY1 = HX0 + HT, HX1 - HT, HY0 + HT, HY1 - HT                 # 90..110 x 62..82 (interior 20 x 20)
DW, DH = L.DUNGEON_DOOR_W, L.DUNGEON_DOOR_H      # 10 x 14
D_RISE = 4.5
D_SPR = DH - D_RISE                              # arranque da ogiva da porta (9,5)
BODY = 34.0                                      # topo da COLISAO das paredes do nucleo da caverna (acima do piso P3)
IN_SPR, IN_CROWN, IN_CEIL = 14.5, 21.6, 22.0     # abobada interna da caverna / teto colidivel
PX, PY = L.DUNGEON_PORTAL                        # (100, 80)
DAIS = ((72.6, 0.4), (74.6, 0.8))                # (y inicial, topo) dos 2 degraus do estrado

Z, ZCEIL = L.DUN_Z, L.DUN_CEIL                   # 6, 28
ROOMS = dict(L.DUN_ROOMS)
WT = 2.0                                         # espessura das paredes das salas
LINK_H = 12.0
LY = 80.0                                        # eixo dos vaos / portais das salas
R_SPR = 12.0                                     # arranque da abobada das salas (acima do piso)
R_CROWN = ZCEIL - Z - 0.4                        # fecho (21,6): a casca (0,35) fica abaixo do teto colidivel
BX0, BY0, BX1, BY1 = -64.0, 56.0, 68.0, 104.0    # envelope das salas (paredes externas incluidas)

# ------------------------------------------------------------------ BOCA DE CAVERNA v3 (face sul; F: s = x, d = para o sul)
ROCK, RKD, RKT = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top"
CRY, DEEP, GOLD = "SG_Crystal_Glow", "Stone_SGDunCaveDeep", "Metal_Gold"
CMX0, CMY0, CMX1, CMY1 = L.DUNGEON_CAVE_MASS     # caixa da massa de rocha (80..126 x 74..116)
M_HW, M_SPR, M_RISE = 9.6, 11.0, 13.0            # intradorso do arco ogival da boca (apice 24)
M_T, M_DEP = 3.2, 4.2                            # espessura radial das aduelas / projecao do arco para o sul
PIL_DX, PIL_Y, PIL_H = 15.5, 55.8, 24.0          # pilares dos estandartes (x = 100 +- PIL_DX)
# tunel: secoes (y, meia-largura, arranque, flecha, jitter maximo para DENTRO); apice <= 21,6 onde ha teto (y >= 62)
TUN = [(58.5, 9.5, 11.0, 12.9, 0.15), (61.8, 9.4, 10.2, 11.0, 0.7), (65.4, 9.2, 9.8, 10.8, 0.9),
       (69.0, 8.9, 9.4, 10.4, 0.9), (72.6, 8.6, 9.0, 10.0, 0.8), (76.2, 8.3, 8.6, 9.6, 0.6),
       (79.6, 8.1, 8.4, 9.2, 0.45), (82.9, 7.6, 8.0, 8.6, 0.3)]
MOUTH_W = 8.4                                    # meia-largura livre (colisao) da boca entre as ombreiras
# volumes vazios que a rocha NUNCA invade: tunel + arco + pilares (x0, x1, y0, y1, z0, z1 acima do P3)
VOIDS = [(89.6, 110.4, 50.0, 83.4, -9.0, 23.0), (86.8, 113.2, 50.0, 59.2, -9.0, 30.0),
         (82.4, 86.6, 53.6, 58.0, -9.0, 32.0), (113.4, 117.6, 53.6, 58.0, -9.0, 32.0)]
# massa de rocha facetada (casco convexo de pontos sorteados em cada caixa): (x0, x1, y0, y1, z0, z1, pontos)
CHUNKS = [
    # ombros da boca (baixos na frente, sobem para tras)
    (85.3, 89.5, 59.3, 63.0, -5.0, 14.0, 14), (85.4, 89.5, 60.0, 69.0, -5.0, 26.0, 18),
    (85.3, 89.5, 63.0, 74.0, 14.0, 38.0, 16), (110.5, 114.7, 59.3, 63.0, -5.0, 15.0, 14),
    (110.5, 114.7, 60.0, 69.0, -5.0, 28.0, 18), (110.5, 114.8, 63.0, 74.0, 16.0, 42.0, 16),
    # sobrancelha sobre o arco (atras dele) e coroa sobre o tunel
    (87.0, 99.2, 59.4, 68.0, 23.2, 38.0, 18), (100.8, 113.0, 59.4, 69.0, 23.4, 41.0, 18),
    (93.0, 107.0, 60.5, 72.0, 28.0, 48.0, 20), (88.0, 104.0, 66.0, 84.0, 23.2, 46.0, 22),
    (98.0, 112.0, 70.0, 86.5, 23.2, 43.0, 20), (91.0, 103.0, 74.0, 90.0, 30.0, 52.0, 18),
    # flancos (fundem com os montes do terreno)
    (80.5, 89.5, 74.0, 86.0, -5.0, 32.0, 22), (81.0, 90.5, 84.0, 99.0, -5.0, 27.0, 20),
    (110.5, 121.0, 74.0, 86.0, -5.0, 35.0, 22), (111.5, 123.0, 84.0, 97.0, -5.0, 29.0, 20),
    # costas
    (89.0, 104.0, 83.6, 100.0, -5.0, 40.0, 20), (102.0, 116.0, 83.6, 98.5, -5.0, 36.0, 20),
    (92.0, 108.0, 95.0, 102.0, -5.0, 22.0, 14),
]
# agulhas de rocha (penhascos) na coroa: silhueta quebrada da referencia (x, y, meio-x, meio-y, z0, z1)
SPIRES = [(96.5, 70.5, 3.6, 3.2, 34.0, 55.0), (106.5, 76.0, 3.2, 3.0, 32.0, 48.0), (87.4, 67.5, 2.0, 2.6, 28.0, 42.0),
          (112.6, 66.5, 2.0, 2.6, 30.0, 45.0), (99.5, 88.0, 3.4, 3.4, 30.0, 47.0), (84.8, 80.0, 2.8, 3.2, 20.0, 36.0)]
# ESTRATOS (acabamento 2026-09-29): a massa e rocha NATURAL em camadas; as juntas sao GLOBAIS (mesma cota em todos os
# blocos, com um mergulho leve) para a leitura geologica ser uma so. Espessuras alternam camada DURA (saliente, clara) e
# MOLE (recuada, escura). Sem veio/cristal fora: a magia vem de dentro do tunel.
STRATA_T = (4.6, 1.8, 5.4, 2.4, 4.2, 1.6, 5.8, 2.6, 4.8, 2.0, 5.2, 2.8, 4.4, 1.8, 5.6, 2.4, 4.6, 2.0, 5.0, 2.6)
STRATA_Z0 = -6.0                                 # primeira junta (acima do P3, enterrada)
STRATA_DIP = (-0.05, 0.025)                      # dz por stud em x / y a partir de (100, 80): camadas sobem a oeste
MASS_C = (100.0, 88.0)                           # centro da massa: os degraus dos estratos recuam para ele
# pinheiros no topo da massa (x, y, altura): so onde o raio acha topo quase plano
MASS_PINES = [(84.0, 90.0, 10.5), (86.5, 76.5, 9.0), (116.5, 80.0, 9.5), (117.5, 91.0, 11.0), (108.0, 94.5, 8.5),
              (95.0, 96.5, 9.5), (113.0, 69.0, 7.5)]
# cristais nas paredes/teto do tunel: (y, t no perfil 0 = pe oeste .. 0,5 = apice .. 1 = pe leste, altura, raio)
TUN_CRYSTALS = [(66.2, 0.03, 2.4, 0.5), (68.8, 0.97, 3.0, 0.62), (71.0, 0.03, 3.6, 0.75), (72.4, 0.97, 3.9, 0.8),
                (74.6, 0.22, 3.2, 0.65), (75.4, 0.78, 3.4, 0.66)]
# veios de energia NAS PAREDES DO TUNEL: nascem no anel do vortice e SOBEM em diagonal pela parede ate morrer perto da
# boca (raios que saem da fonte). (angulo a partir do zenite no portal, angulo no fim, y inicial, y final)
TUN_VEINS = [(-80.0, -40.0, 80.2, 66.4), (78.0, 44.0, 80.0, 67.2)]


def _box_hit(a, b):
    return a[0] < b[1] and b[0] < a[1] and a[2] < b[3] and b[2] < a[3] and a[4] < b[5] and b[4] < a[5]


def chunk_check():
    """cada caixa de rocha: dentro da regiao permitida (pegada da portaria + DUNGEON_CAVE_MASS, folga 1,8) e fora
    dos vazios (tunel, arco, pilares)"""
    bad = []
    boxes = [c[:6] for c in CHUNKS] + [(x - rx, x + rx, y - ry, y + ry, z0, z1) for x, y, rx, ry, z0, z1 in SPIRES]
    for i, c in enumerate(boxes):
        x0, x1, y0, y1 = c[:4]
        in_house = HX0 - 1.8 <= x0 and x1 <= HX1 + 1.8 and HY0 - 1.8 <= y0 and y1 <= HY1 + 1.8
        in_box = CMX0 <= x0 and x1 <= CMX1 and CMY0 <= y0 and y1 <= CMY1
        if not (in_house or in_box):
            bad.append(("fora", i))
        for v in VOIDS:
            if _box_hit(c[:6], v):
                bad.append(("vazio", i, v[:2]))
    print("DUN massa: %d blocos de rocha, conferencia %s" % (len(boxes), bad or "OK"))


# ------------------------------------------------------------------ APROXIMACAO (patio P3 ao sul da boca)
PC = (100.0, 56.0)                               # centro da ferradura de lajes
PR = 22.0                                        # raio da ferradura
COR_Y0 = 24.0                                    # inicio do corredor cerimonial (lanternas do eixo)
LINE_DX = 5.6                                    # fios de energia rentes ao piso (x = 100 +- 5,6) ate o estrado
# pares de pedestais de obsidiana com cristal (funil que abre para o sul) e lanternas quentes
PED_XY = ((86.5, 47.0), (113.5, 47.0), (84.5, 41.5), (115.5, 41.5))
LANTERN_XY = ((88.8, 52.6), (111.2, 52.6), (93.5, 24.0), (106.5, 24.0))
PILLAR_XY = ((HX - PIL_DX, PIL_Y), (HX + PIL_DX, PIL_Y))
# linhas do andador do sg_qa que cruzam o patio (patio -> portaria e portaria -> escada leste) + corredor do eixo
WALK_LINES = [((80.0, 30.0), (100.0, 51.0)), ((100.0, 51.0), (110.0, 30.0)), ((100.0, 51.0), (100.0, 62.0))]

CAMS = {
    "CAM_SGDun_HouseSouth": ((100.0, 18.0, P3 + 9.0), (100.0, 72.0, P3 + 24.0), 20),
    "CAM_SGDun_HouseEast": ((150.0, 40.0, P3 + 16.0), (100.0, 72.0, P3 + 24.0), 22),
    "CAM_SGDun_HouseNorth": ((132.0, 128.0, P3 + 34.0), (100.0, 72.0, P3 + 26.0), 22),
    "CAM_SGDun_HouseWest": ((58.0, 104.0, P3 + 16.0), (100.0, 72.0, P3 + 24.0), 22),
    "CAM_SGDun_PlayerDoor": ((100.0, 42.0, P3 + 5.2), (100.0, 72.0, P3 + 9.0), 22),
    "CAM_SGDun_Mouth": ((100.0, 30.0, P3 + 4.6), (100.0, 60.0, P3 + 20.0), 24),
    "CAM_SGDun_Tunnel": ((100.0, 60.5, P3 + 5.2), (100.0, 82.0, P3 + 8.0), 18),
    "CAM_SGDun_InteriorBack": ((100.0, 77.5, P3 + 6.0), (100.0, 59.0, P3 + 7.0), 18),
    "CAM_SGDun_R1Arrival": ((-36.0, 86.0, Z + 5.2), (-62.0, 79.0, Z + 7.0), 20),
    "CAM_SGDun_R1Spawn": ((-58.0, 70.0, Z + 5.2), (0.0, 82.0, Z + 5.0), 20),
    "CAM_SGDun_R2": ((-21.0, 61.0, Z + 9.0), (16.0, 98.0, Z + 8.0), 16),
    "CAM_SGDun_R2Link": ((-38.0, 84.0, Z + 5.2), (-8.0, 78.0, Z + 7.0), 20),
    "CAM_SGDun_R3Exit": ((25.0, 76.0, Z + 5.2), (66.0, 80.0, Z + 7.0), 20),
    "CAM_SGDun_R3Back": ((62.0, 62.0, Z + 10.0), (22.0, 96.0, Z + 7.0), 16),
    "CAM_SGDun_FromCastleCourt": ((30.0, 4.0, P3 + 7.0), (100.0, 58.0, P3 + 15.0), 26),
    "CAM_SGDun_Approach": ((90.0, 30.0, P3 + 5.2), (100.0, 60.0, P3 + 12.0), 20),
    "CAM_SGDun_Far": ((10.0, -70.0, P3 + 62.0), (100.0, 62.0, P3 + 16.0), 34),
}

EXTRA_ROUTES = {
    "PORTARIA_ATE_O_PORTAL": ([(100.0, 50.0), (100.0, 60.0), (100.0, 70.0), (100.0, 73.6), (100.0, 76.5)], P3),
    "APROXIMACAO_EIXO": ([(100.0, 26.0), (100.0, 36.0), (100.0, 46.0), (100.0, 54.0), (100.0, 61.0)], P3),
    "APROXIMACAO_TRAVESSIA": ([(92.0, 40.0), (100.0, 46.5), (108.0, 40.0)], P3),
    "SALA_R1_VOLTA": ([(-57.5, 66.5), (-30.5, 66.5), (-30.5, 93.5), (-57.5, 93.5), (-57.5, 66.5)], Z),
    "SALA_R2_VOLTA": ([(-19.5, 62.5), (15.5, 62.5), (15.5, 97.5), (-19.5, 97.5), (-19.5, 62.5)], Z),
    "SALA_R3_VOLTA": ([(26.5, 62.5), (61.5, 62.5), (61.5, 97.5), (26.5, 97.5), (26.5, 62.5)], Z),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ colisao com folga dos minerios
_ORES = [(x, y) for room, kind, i, x, y, r in L.dun_ore_points()]
_SKIP = []


def _clear(p0, p1, rad=5.0):
    x0, x1 = sorted((p0[0], p1[0]))
    y0, y1 = sorted((p0[1], p1[1]))
    z0, z1 = sorted((p0[2], p1[2]))
    if z1 <= Z or z0 >= Z + 12.0:
        return True
    for x, y in _ORES:
        dx = max(x0 - x, 0.0, x - x1)
        dy = max(y0 - y, 0.0, y - y1)
        if math.hypot(dx, dy) < rad:
            return False
    return True


def ccol(area, p0, p1):
    """caixa de colisao; nas salas so se ficar a >= 5 de todo DUN_ORE (senao fica so o visual e avisa)"""
    if not _clear(p0, p1):
        _SKIP.append((area, tuple(round(v, 1) for v in p0)))
        return None
    return col_box2(area, p0, p1)


# ------------------------------------------------------------------ referencial de uma face de parede
class Face:
    """face plana de parede: s = coordenada ao longo (x se horiz, y se nao), d = distancia a partir da face no sentido
    'sign' (para dentro da sala ou para fora da torre), h = altura acima de z0"""

    def __init__(self, horiz, plane, sign, z0):
        self.hz, self.pl, self.sg, self.z0 = horiz, plane, sign, z0

    def p(self, s, d, h):
        if self.hz:
            return (s, self.pl + self.sg * d, self.z0 + h)
        return (self.pl + self.sg * d, s, self.z0 + h)

    def v(self, s, d, h):
        return Vector(self.p(s, d, h))

    def n(self):
        return Vector((0.0, self.sg, 0.0)) if self.hz else Vector((self.sg, 0.0, 0.0))

    def u(self):
        return Vector((1.0, 0.0, 0.0)) if self.hz else Vector((0.0, 1.0, 0.0))


def fbox(mb, F, s0, s1, d0, d1, h0, h1, m, bev=0.0):
    mb.box2(F.p(s0, d0, h0), F.p(s1, d1, h1), m, bev)


def fcol(area, F, s0, s1, d0, d1, h0, h1):
    return ccol(area, F.p(s0, d0, h0), F.p(s1, d1, h1))


def fcyl(mb, F, s, d, h0, h1, r, m, n=8, r2=None):
    mb.cyl(r, h1 - h0, F.p(s, d, (h0 + h1) / 2.0), m=m, n=n, r2=r2, bevel=0.0)


# ------------------------------------------------------------------ ogivas (arco quebrado) no plano da parede
def _ogive_center(hw, rise):
    xc = (hw * hw - rise * rise) / (2.0 * hw)
    c = min(xc, -0.25 * hw)
    zc = (rise * rise - hw * hw + 2.0 * hw * c) / (2.0 * rise)
    return c, zc, math.hypot(hw - c, zc)


def ogive_right(hw, rise, n):
    c, zc, R = _ogive_center(hw, rise)
    t0 = math.atan2(-zc, hw - c)
    ta = math.atan2(rise - zc, -c)
    pts = [(c + R * math.cos(t0 + (ta - t0) * k / n), zc + R * math.sin(t0 + (ta - t0) * k / n)) for k in range(n + 1)]
    pts[0] = (hw, 0.0)
    pts[-1] = (0.0, rise)
    return pts


def ogive(cs, hw, rise, spring, n=6):
    r = ogive_right(hw, rise, n)
    return [(cs - u, spring + v) for u, v in r] + [(cs + u, spring + v) for u, v in reversed(r)][1:]


def ogive_z(hw, rise, u):
    c, zc, R = _ogive_center(hw, rise)
    return max(0.0, zc + math.sqrt(max(0.0, R * R - (abs(u) - c) ** 2)))


def band(mb, F, inner, outer, d0, d1, m, closed=False):
    """faixa solida no plano da parede entre duas polilinhas (s, h) do mesmo tamanho"""
    bm = mb.bm
    n = len(inner)
    iF = [bm.verts.new(F.p(s, d1, h)) for s, h in inner]
    iB = [bm.verts.new(F.p(s, d0, h)) for s, h in inner]
    oF = [bm.verts.new(F.p(s, d1, h)) for s, h in outer]
    oB = [bm.verts.new(F.p(s, d0, h)) for s, h in outer]
    for i in (range(n) if closed else range(n - 1)):
        j = (i + 1) % n
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    if not closed:
        for k in (0, n - 1):
            bm.faces.new((iF[k], oF[k], oB[k], iB[k]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def slab(mb, F, pts, d0, d1, m):
    """placa no plano da parede (poligono CONVEXO (s, h))"""
    bm = mb.bm
    Fv = [bm.verts.new(F.p(s, d1, h)) for s, h in pts]
    Bv = [bm.verts.new(F.p(s, d0, h)) for s, h in pts]
    n = len(pts)
    bm.faces.new(Fv)
    bm.faces.new(list(reversed(Bv)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((Fv[j], Fv[i], Bv[i], Bv[j]))
    mb._post(Fv + Bv, m, None, 0, 1)


def spandrel(mb, F, corner, arc, d0, d1, m):
    """tampa entre um canto (s, h) e um trecho de arco (leque a partir do canto): o 'tímpano' ao lado da ogiva"""
    bm = mb.bm
    cF, cB = bm.verts.new(F.p(corner[0], d1, corner[1])), bm.verts.new(F.p(corner[0], d0, corner[1]))
    aF = [bm.verts.new(F.p(s, d1, h)) for s, h in arc]
    aB = [bm.verts.new(F.p(s, d0, h)) for s, h in arc]
    for i in range(len(arc) - 1):
        bm.faces.new((cF, aF[i], aF[i + 1]))
        bm.faces.new((cB, aB[i + 1], aB[i]))
        bm.faces.new((aF[i], aB[i], aB[i + 1], aF[i + 1]))
    bm.faces.new((cF, cB, aB[0], aF[0]))
    bm.faces.new((cF, aF[-1], aB[-1], cB))
    mb._post([cF, cB] + aF + aB, m, None, 0, 1)


def arch_band(mb, F, cs, hw, rise, spring, foot, t, d0, d1, m, n=6):
    inner = [(cs - hw, foot)] + ogive(cs, hw, rise, spring, n) + [(cs + hw, foot)]
    outer = [(cs - hw - t, foot)] + ogive(cs, hw + t, rise + t, spring, n) + [(cs + hw + t, foot)]
    band(mb, F, inner, outer, d0, d1, m)


def arch_panel(mb, F, cs, hw, rise, spring, foot, d0, d1, m, n=6):
    slab(mb, F, [(cs - hw, foot)] + ogive(cs, hw, rise, spring, n) + [(cs + hw, foot)], d0, d1, m)




def wall_ogive_opening(mb, F, s0, s1, cs, hw, spring, rise, top, d0, d1, m, n=6):
    """pano de parede de s0..s1 x 0..top com um vao ogival (retangulo ate 'spring' + ogiva) centrado em cs"""
    fbox(mb, F, s0, cs - hw, d0, d1, -0.5, top, m)
    fbox(mb, F, cs + hw, s1, d0, d1, -0.5, top, m)
    fbox(mb, F, cs - hw, cs + hw, d0, d1, spring + rise, top, m)
    r = ogive_right(hw, rise, n)
    spandrel(mb, F, (cs - hw, spring + rise), [(cs - u, spring + v) for u, v in r], d0, d1, m)
    spandrel(mb, F, (cs + hw, spring + rise), [(cs + u, spring + v) for u, v in r], d0, d1, m)


def tri_prism(mb, F, pts, d0, d1, m):
    slab(mb, F, pts, d0, d1, m)


# ------------------------------------------------------------------ pecas do sistema (laminas, runas, correntes)
def obox3(mb, c, ax, ay, az, sx, sy, sz, m):
    """caixa orientada: centro c, eixos (unitarios) ax, ay, az e medidas ao longo deles"""
    c = Vector(c)
    hx, hy, hz = ax * (sx / 2.0), ay * (sy / 2.0), az * (sz / 2.0)
    bm = mb.bm
    V = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                V[i, j, k] = bm.verts.new(c + hx * (2 * i - 1) + hy * (2 * j - 1) + hz * (2 * k - 1))
    for f in (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
              ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
              ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))):
        bm.faces.new([V[q] for q in f])
    mb._post(list(V.values()), m, None, 0, 1)


def blade(mb, base, dirv, side, fwd, L_, w, th, m, curl=0.0, ridge=None):
    """lamina/espinho de obsidiana: base w x th, ombro a 45% (afinando) e ponta; curl = desvio lateral (garra);
    ridge = material de um fio (energia) na lombada da face da frente (le a silhueta de noite)"""
    base, dirv, side, fwd = Vector(base), Vector(dirv).normalized(), Vector(side).normalized(), Vector(fwd).normalized()
    mid = base + dirv * (L_ * 0.45) + side * (w * curl)
    tip = base + dirv * L_ + side * (w * curl * 1.6)
    bm = mb.bm
    sq = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    B = [bm.verts.new(base + side * (a * w / 2) + fwd * (b * th / 2)) for a, b in sq]
    M = [bm.verts.new(mid + side * (a * w * 0.3) + fwd * (b * th * 0.32)) for a, b in sq]
    T = bm.verts.new(tip)
    bm.faces.new(list(reversed(B)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((B[i], B[j], M[j], M[i]))
        bm.faces.new((M[i], M[j], T))
    mb._post(B + M + [T], m, None, 0, 1)
    if ridge:
        a = base + fwd * (th / 2 + 0.02)
        b = mid + fwd * (th * 0.32 + 0.02)
        c = base.lerp(tip, 0.86) + fwd * 0.04
        for p0, p1, wd in ((a, b, 0.26), (b, c, 0.2)):
            ax = (p1 - p0).normalized()
            obox3(mb, (p0 + p1) / 2, ax, side, ax.cross(side).normalized(), (p1 - p0).length + 0.1, wd, 0.1, ridge)


# runas da ordem: UM alfabeto angular (7 glifos) usado em monolitos, portal, pedestais e pisos das salas (sistema)
GLYPHS = [
    [((0, 0), (0, 1.4)), ((0, 1.0), (0.5, 1.4)), ((0, 0.55), (0.5, 0.95))],
    [((0, 0), (0, 1.4)), ((0, 1.4), (0.5, 1.0)), ((0.5, 1.0), (0, 0.6))],
    [((-0.45, 0), (0.45, 1.4)), ((0.45, 0), (-0.45, 1.4))],
    [((0, 0), (0, 1.4)), ((-0.5, 0.9), (0, 1.4)), ((0.5, 0.9), (0, 1.4))],
    [((-0.4, 0), (-0.4, 1.4)), ((0.4, 0), (0.4, 1.4)), ((-0.4, 1.4), (0.4, 0.7))],
    [((0, 0), (0, 1.4)), ((-0.5, 0.3), (0.5, 1.1))],
    [((0, 0.15), (0.45, 0.7)), ((0.45, 0.7), (0, 1.25)), ((0, 1.25), (-0.45, 0.7)), ((-0.45, 0.7), (0, 0.15))],
]


def glyph(mb, o, ea, eb, en, k, sc, m=RG, dep=0.12, w=0.22):
    """glifo k (base-centro o) no plano (ea lateral, eb 'cima'), saltado 'dep' ao longo da normal en"""
    o, ea, eb, en = Vector(o), Vector(ea), Vector(eb), Vector(en)
    for (a0, b0), (a1, b1) in GLYPHS[k % len(GLYPHS)]:
        p0 = o + ea * (a0 * sc) + eb * (b0 * sc)
        p1 = o + ea * (a1 * sc) + eb * (b1 * sc)
        d = p1 - p0
        ax = d.normalized()
        ay = en.cross(ax).normalized()
        obox3(mb, (p0 + p1) / 2 + en * (dep / 2), ax, ay, en, d.length + w, w, dep, m)


def chain(mb, p0, p1, sag, m=BI, pitch=0.66):
    """corrente de ferro negro em catenaria (parabola): elos VAZADOS (4 barras) alternando deitado/em pe"""
    p0, p1 = Vector(p0), Vector(p1)
    n = max(3, int((p1 - p0).length / pitch))
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(p0.lerp(p1, t) + Vector((0.0, 0.0, -4.0 * sag * t * (1.0 - t))))
    hw, wr = 0.26, 0.2
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        ax = (b - a).normalized()
        hl = (b - a).length * 0.5 + 0.13
        s0 = ax.cross(Vector((0.0, 0.0, 1.0)))
        s0 = s0.normalized() if s0.length > 1e-3 else Vector((1.0, 0.0, 0.0))     # corrente a prumo
        s = s0 if i % 2 == 0 else ax.cross(s0).normalized()
        nn = ax.cross(s).normalized()
        c = (a + b) / 2
        for sg in (-1, 1):
            obox3(mb, c + s * (sg * hw), ax, s, nn, 2 * hl, wr, wr, m)
            obox3(mb, c + ax * (sg * (hl - wr / 2)), s, ax, nn, 2 * hw + wr, wr, wr, m)


def eye_ring(mb, p, n, r=0.34, m=BI):
    """ARGOLA de ferro: chapa na face (p = ponto da face, n = normal para fora), grampo e anel pendurado no plano
    (n, z). Devolve o ponto mais baixo do anel (onde a corrente prende)."""
    p, n = Vector(p), Vector(n).normalized()
    up = Vector((0.0, 0.0, 1.0))
    sd = up.cross(n).normalized()
    obox3(mb, p + n * 0.06, n, sd, up, 0.12, 0.62, 0.62, m)                       # chapa
    obox3(mb, p + n * 0.24, n, sd, up, 0.3, 0.16, 0.16, m)                        # grampo
    c = p + n * 0.38 - up * (r - 0.05)
    k = 8
    for i in range(k):
        a0, a1 = 2 * math.pi * i / k, 2 * math.pi * (i + 1) / k
        q0 = c + n * (math.sin(a0) * r) + up * (math.cos(a0) * r)
        q1 = c + n * (math.sin(a1) * r) + up * (math.cos(a1) * r)
        ax = (q1 - q0).normalized()
        obox3(mb, (q0 + q1) / 2, ax, sd, ax.cross(sd).normalized(), (q1 - q0).length + 0.08, 0.14, 0.14, m)
    return c - up * r


# ------------------------------------------------------------------ KIT (portaria e salas usam as mesmas pecas)
PIL_D, PIL_HW = 1.5, 1.5


def pilaster(mb, F, s, top, area=None):
    """pilastra engastada: plinto, fuste + colunelo frontal, capitel (arranque da abobada em 'top')"""
    fbox(mb, F, s - PIL_HW - 0.3, s + PIL_HW + 0.3, 0.0, PIL_D + 0.3, 0.0, 1.0, TR, 0.08)
    fbox(mb, F, s - PIL_HW, s + PIL_HW, 0.0, PIL_D, 1.0, top - 0.9, CS, 0.06)
    fcyl(mb, F, s, PIL_D, 1.0, top - 0.9, 0.45, CS, 8)
    fbox(mb, F, s - PIL_HW - 0.25, s + PIL_HW + 0.25, 0.0, PIL_D + 0.45, top - 0.9, top, TR, 0.08)
    if area:
        fcol(area, F, s - PIL_HW - 0.3, s + PIL_HW + 0.3, 0.0, PIL_D + 0.3, -0.5, top)


def corner_col(mb, F, s, sgn, top, area=None):
    """coluna de canto (ocupa o canto das duas paredes): s = canto, sgn = para onde ela cresce ao longo da face F"""
    a, b = sorted((s, s + sgn * 2.4))
    a2, b2 = sorted((s, s + sgn * 2.7))
    fbox(mb, F, a2, b2, 0.0, 2.7, 0.0, 1.0, TR, 0.08)
    fbox(mb, F, a, b, 0.0, 2.4, 1.0, top - 0.9, CS, 0.06)
    fbox(mb, F, a2, b2, 0.0, 2.75, top - 0.9, top, TR, 0.08)
    if area:
        fcol(area, F, a2, b2, 0.0, 2.7, -0.5, top)


def blind_arch(mb, F, s0, s1, spring=7.0, twin=False):
    """arco ogival cego (fundo navy + arquivolta clara) no vao entre duas pilastras; twin = arcada dupla"""
    fbox(mb, F, s0, s1, 0.0, 0.4, 0.0, 0.9, TR, 0.05)                 # rodape
    if twin:
        mid = (s0 + s1) / 2.0
        blind_arch(mb, F, s0, mid + 0.35, spring, False)
        blind_arch(mb, F, mid - 0.35, s1, spring, False)
        fbox(mb, F, mid - 0.45, mid + 0.45, 0.0, 0.7, 0.9, spring + 0.4, CS, 0.05)   # colunelo central
        return
    cs = (s0 + s1) / 2.0
    hw = (s1 - s0) / 2.0 - 0.8
    if hw < 1.2:
        return
    rise = min(hw * 1.15, 5.2)
    arch_panel(mb, F, cs, hw, rise, spring, 0.9, 0.0, 0.15, VA)
    arch_band(mb, F, cs, hw, rise, spring, 0.9, 0.55, 0.0, 0.5, TR)


def cornice(mb, F, s0, s1, h):
    if s1 - s0 > 0.3:
        fbox(mb, F, s0, s1, 0.0, 0.6, h - 0.6, h, TR, 0.05)


def torch(mb, F, s, d, h):
    """tocha de parede: mao-francesa de ferro, copo e chama (Neon quente)"""
    mb.beam(F.p(s, d, h - 1.4), F.p(s, d + 0.95, h - 0.25), 0.22, 0.22, IR, 0.0)
    mb.cyl(0.36, 0.5, F.p(s, d + 1.0, h), m=IR, n=6, r2=0.52, bevel=0.0)
    mb.cyl(0.3, 0.9, F.p(s, d + 1.0, h + 0.7), m=GL, n=6, r2=0.04, bevel=0.0)


def link_frame(mb, F, cs, hw_open):
    """moldura do vao de ligacao 12 x 12: verga clara + timpano ogival navy com o emblema da ordem"""
    fbox(mb, F, cs - hw_open - 1.3, cs + hw_open + 1.3, 0.0, 0.8, LINK_H, LINK_H + 1.2, TR, 0.06)
    th = hw_open + 0.6
    arch_panel(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.0, 0.15, VA)
    arch_band(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.7, 0.0, 0.6, TR)
    # emblema da ordem no timpano (substitui a estrela avulsa: um simbolo so)
    n = F.n()
    EM.plaque(mb, mb, mb, mb, F.p(cs, 0.6, LINK_H + 3.5), math.atan2(n.y, n.x), 1.25)


def tile_floor(mb, rect, z, tile=4.0, margin=1.0, friso=0.8, gap=0.25, skip=None):
    """piso de lajes escuras (topo EXATO em z) com friso claro junto as paredes; juntas mostram a base mais clara"""
    x0, y0, x1, y1 = rect
    mb.box2((x0, y0, z - 0.6), (x1, y1, z - 0.15), BL, 0.0)

    def ringbox(a, b, m):
        # anel entre o retangulo recuado 'a' e o recuado 'b' (a < b)
        ax0, ay0, ax1, ay1 = x0 + a, y0 + a, x1 - a, y1 - a
        bx0, by0, bx1, by1 = x0 + b, y0 + b, x1 - b, y1 - b
        mb.box2((ax0, ay0, z - 0.4), (ax1, by0, z), m, 0.0)
        mb.box2((ax0, by1, z - 0.4), (ax1, ay1, z), m, 0.0)
        mb.box2((ax0, by0, z - 0.4), (bx0, by1, z), m, 0.0)
        mb.box2((bx1, by0, z - 0.4), (ax1, by1, z), m, 0.0)
    ringbox(0.0, margin, FL)
    ringbox(margin, margin + friso, TR)
    ix0, iy0, ix1, iy1 = x0 + margin + friso, y0 + margin + friso, x1 - margin - friso, y1 - margin - friso
    nx = max(1, int(round((ix1 - ix0) / tile)))
    ny = max(1, int(round((iy1 - iy0) / tile)))
    tx, ty = (ix1 - ix0) / nx, (iy1 - iy0) / ny
    for i in range(nx):
        for j in range(ny):
            ax, ay = ix0 + i * tx, iy0 + j * ty
            if skip and skip(ax + tx / 2, ay + ty / 2):
                continue
            mb.box2((ax + gap / 2, ay + gap / 2, z - 0.4), (ax + tx - gap / 2, ay + ty - gap / 2, z), FL, 0.0)


# ------------------------------------------------------------------ abobada ogival de bercos + nervuras
def _vault_map(rect, axis):
    x0, y0, x1, y1 = rect
    if axis == "x":
        yc, hw = (y0 + y1) / 2.0, (y1 - y0) / 2.0
        return (x0, x1), hw, (lambda a, u: (a, yc + u))
    xc, hw = (x0 + x1) / 2.0, (x1 - x0) / 2.0
    return (y0, y1), hw, (lambda a, u: (xc + u, a))


def vault_z(rect, axis, zf, spring, crown, u):
    _, hw, _ = _vault_map(rect, axis)
    return zf + spring + ogive_z(hw, crown - spring, u)


def vault(mb, rect, axis, zf, spring, crown, ribs=(), nseg=18):
    """berco ogival (arranque 'spring', fecho 'crown' acima de zf) ao longo de 'axis'; nervuras transversais nos
    valores de 'ribs' (coordenada ao longo do eixo), nervuras de testa nas duas pontas e cumeeira"""
    (a0, a1), hw, mp = _vault_map(rect, axis)
    rise = crown - spring
    bm = mb.bm
    us = [-hw + 2 * hw * (0.5 - 0.5 * math.cos(math.pi * k / nseg)) for k in range(nseg + 1)]

    def zz(u):
        return zf + spring + ogive_z(hw, rise, u)
    lo = [[bm.verts.new((*mp(a, u), zz(u))) for u in us] for a in (a0, a1)]
    hi = [[bm.verts.new((*mp(a, u), zz(u) + 0.35)) for u in us] for a in (a0, a1)]
    n = len(us)
    for i in range(n - 1):
        bm.faces.new((lo[0][i], lo[0][i + 1], lo[1][i + 1], lo[1][i]))
        bm.faces.new((hi[0][i], hi[1][i], hi[1][i + 1], hi[0][i + 1]))
        for k in (0, 1):
            bm.faces.new((lo[k][i], hi[k][i], hi[k][i + 1], lo[k][i + 1]))
    for i in (0, n - 1):
        bm.faces.new((lo[0][i], lo[1][i], hi[1][i], hi[0][i]))
    mb._post([v for r in lo + hi for v in r], VA, None, 0, 1)
    prof = [(-0.45, 0.12), (0.45, 0.12), (0.45, -0.8), (-0.45, -0.8)]
    prof_w = [(-0.35, 0.12), (0.35, 0.12), (0.35, -0.6), (-0.35, -0.6)]
    ue = [-hw + 0.3 + (2 * hw - 0.6) * (0.5 - 0.5 * math.cos(math.pi * k / 20)) for k in range(21)]

    def rib(a, pr):
        mb.sweep([(*mp(a, u), zz(u) - 0.02) for u in ue], pr, TR)
    for a in ribs:
        rib(a, prof)
    rib(a0 + 0.4, prof_w)
    rib(a1 - 0.4, prof_w)
    mb.sweep([(*mp(a0 + 0.4, 0.0), zz(0.0) - 0.02), (*mp(a1 - 0.4, 0.0), zz(0.0) - 0.02)], prof, TR)
    for a in ribs:
        x, y = mp(a, 0.0)
        mb.cyl(0.95, 0.7, (x, y, zz(0.0) - 0.95), m=TR, n=8, bevel=0.0)


# ------------------------------------------------------------------ portal (anel com runas + disco + espiral)
def _pl(c, u, v, n, a, r, d):
    return c + u * (math.cos(a) * r) + v * (math.sin(a) * r) + n * d


def ring3(mb, c, u, v, n, r0, r1, d0, d1, m, seg=28):
    bm = mb.bm
    A = [2 * math.pi * k / seg for k in range(seg)]
    iF = [bm.verts.new(_pl(c, u, v, n, a, r0, d1)) for a in A]
    iB = [bm.verts.new(_pl(c, u, v, n, a, r0, d0)) for a in A]
    oF = [bm.verts.new(_pl(c, u, v, n, a, r1, d1)) for a in A]
    oB = [bm.verts.new(_pl(c, u, v, n, a, r1, d0)) for a in A]
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def disc3(mb, c, u, v, n, r, d0, d1, m, seg=28):
    bm = mb.bm
    A = [2 * math.pi * k / seg for k in range(seg)]
    Fv = [bm.verts.new(_pl(c, u, v, n, a, r, d1)) for a in A]
    Bv = [bm.verts.new(_pl(c, u, v, n, a, r, d0)) for a in A]
    bm.faces.new(Fv)
    bm.faces.new(list(reversed(Bv)))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((Fv[j], Fv[i], Bv[i], Bv[j]))
    mb._post(Fv + Bv, m, None, 0, 1)


def spiral(mb, c, u, v, n, R, d0, d1, m, arms=5, twist=2.7, seg=14, a0=0.0):
    """bracos da espiral (fitas que afinam nas pontas) + nucleo"""
    bm = mb.bm
    for k in range(arms):
        th0 = a0 + 2 * math.pi * k / arms
        LF, RF, LB, RB = [], [], [], []
        for i in range(seg + 1):
            t = i / seg
            r = 0.7 + (R - 0.7) * t
            th = th0 + twist * t
            w = 0.28 + 1.7 * t * (1.0 - t)
            dl = (w / 2.0) / r
            LF.append(bm.verts.new(_pl(c, u, v, n, th - dl, r, d1)))
            RF.append(bm.verts.new(_pl(c, u, v, n, th + dl, r, d1)))
            LB.append(bm.verts.new(_pl(c, u, v, n, th - dl, r, d0)))
            RB.append(bm.verts.new(_pl(c, u, v, n, th + dl, r, d0)))
        for i in range(seg):
            bm.faces.new((LF[i], RF[i], RF[i + 1], LF[i + 1]))
            bm.faces.new((LB[i + 1], RB[i + 1], RB[i], LB[i]))
            bm.faces.new((LF[i + 1], LB[i + 1], LB[i], LF[i]))
            bm.faces.new((RF[i], RB[i], RB[i + 1], RF[i + 1]))
        bm.faces.new((LF[0], LB[0], RB[0], RF[0]))
        bm.faces.new((RF[-1], RB[-1], LB[-1], LF[-1]))
        mb._post(LF + RF + LB + RB, m, None, 0, 1)
    disc3(mb, c, u, v, n, 1.0, d0, d1 + 0.05, m, 12)


def obox(mb, c, u, v, n, su, sv, sn, m, bev=0.0):
    """caixa centrada em c com medidas ao longo de u, v, n (eixos alinhados ao mundo)"""
    h = u * (su / 2) + v * (sv / 2) + n * (sn / 2)
    ext = Vector((abs(h.x), abs(h.y), abs(h.z)))
    mb.box2(c - ext, c + ext, m, bev)


def portal_frame(mb, c, u, v, n, r_in, r_out, floor_z):
    """anel de pedra (cantaria clara com runas de prata + coroa escura), chave com estrela e pes"""
    v3 = Vector
    ring3(mb, c, u, v, n, r_in, r_in + 0.9, -0.6, 0.7, TR)
    ring3(mb, c, u, v, n, r_in + 0.9, r_out, -0.6, 0.35, CS)
    # runas: 16 barrinhas de prata no aro claro (radiais e tangenciais alternadas)
    rr = r_in + 0.45
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16
        p = _pl(c, u, v, n, a, rr, 0.72)
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        dirv = radial if k % 2 == 0 else tang
        ln = 0.55 if k % 2 == 0 else 0.4
        mb.beam(p - dirv * ln, p + dirv * ln, 0.22, 0.2, SV, 0.0)
    # chave (topo) e pes (base) do anel
    top = c + v * (r_out - 0.2)
    obox(mb, top + n * 0.1, u, v, n, 1.6, 1.8, 1.6, TR, 0.08)
    obox(mb, top + n * 0.95, u, v, n, 0.5, 0.6, 0.5, SV)
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        h = p.z + 0.4 - floor_z
        obox(mb, v3((p.x, p.y, floor_z + h / 2)), u, v, n, 2.2, h, 2.0, CS, 0.08)



def chandelier(mb, x, y, h, top, r=3.0, n=8):
    """lustre de ferro (aro + raios + velas) pendurado da abobada: h = altura do aro, top = z da nervura"""
    ring_lo = [(x + r * math.cos(2 * math.pi * k / 16), y + r * math.sin(2 * math.pi * k / 16), h) for k in range(17)]
    mb.tube(ring_lo, 0.2, IR, 6)
    mb.cyl(0.45, 2.6, (x, y, h + 1.1), m=IR, n=8, r2=0.25, bevel=0.0)
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        ca, sa = math.cos(a), math.sin(a)
        mb.beam((x + 0.3 * ca, y + 0.3 * sa, h + 2.0), (x + r * ca, y + r * sa, h), 0.2, 0.2, IR, 0.0)
        mb.cyl(0.32, 0.3, (x + r * ca, y + r * sa, h + 0.25), m=IR, n=6, bevel=0.0)
        mb.cyl(0.2, 0.7, (x + r * ca, y + r * sa, h + 0.75), m=GL, n=6, bevel=0.0)
    mb.rod((x, y, h + 2.4), (x, y, top), 0.13, IR, 6)


# ==================================================================== PORTARIA = BOCA DE CAVERNA (superficie)
def crystal(mb, c, h, r, out_deg=0.0, lean=0.0, m=CRY, n=4):
    """cristal em LOSANGO (bipiramide n-gonal alongada): c = centro (equador), h = altura total, r = meio-eixo,
    inclinado 'lean' rad na direcao horizontal out_deg (lean > pi/2 = aponta para baixo)"""
    rx, rz = lean, math.radians(out_deg) + math.pi / 2
    ax = Vector((math.sin(rx) * math.sin(rz), -math.sin(rx) * math.cos(rz), math.cos(rx)))
    c = Vector(c)
    ht, hb = h * 0.56, h * 0.44
    mb.cyl(r, ht, c + ax * (ht / 2), (rx, 0.0, rz), m=m, n=n, r2=0.05, bevel=0.0)
    mb.cyl(r, hb, c - ax * (hb / 2), (rx + math.pi, 0.0, rz), m=m, n=n, r2=0.05, bevel=0.0)


def crystal_col(mb, base, dirv, h, r, m=CRY):
    """cristal de COLUNA hexagonal com ponta (le como cristal de caverna, nao como lasca): nasce em 'base'"""
    d = Vector(dirv).normalized()
    lean = math.acos(max(-1.0, min(1.0, d.z)))
    rz = math.atan2(d.y, d.x) + math.pi / 2
    rot = (lean, 0.0, rz)
    b = Vector(base) - d * 0.6
    hb = h * 0.68 + 0.6
    mb.cyl(r, hb, b + d * (hb / 2), rot, m=m, n=6, r2=r * 0.9, bevel=0.0)
    ht = h * 0.32
    mb.cyl(r * 0.9, ht, b + d * (hb + ht / 2), rot, m=m, n=6, r2=0.04, bevel=0.0)


def cluster(mb, base, dirv, h, rng, r=None, boss=OB):
    """aglomerado: 1 coluna de cristal grande + 2 menores abertas em leque, brotando de um CALO de rocha (nada solto)"""
    d = Vector(dirv).normalized()
    r = r or h * 0.2
    if boss:
        rr = r * 2.6
        mb.rock(Vector(base) - d * (rr * 0.15), (rr * 2.0, rr * 2.0, rr * 1.2), boss, 1,
                (math.acos(max(-1.0, min(1.0, d.z))), 0.0, math.atan2(d.y, d.x) + math.pi / 2), 0.35, None, False)
    crystal_col(mb, base, d, h, r)
    side = d.orthogonal().normalized()
    other = d.cross(side).normalized()
    for k, (sc, a) in enumerate(((0.58, 0.55), (0.46, -0.6))):
        ang = rng.uniform(0.0, math.tau)
        off = side * math.cos(ang) + other * math.sin(ang)
        dd = (d + off * a).normalized()
        crystal_col(mb, Vector(base) + off * (r * 1.1), dd, h * sc, r * sc * 1.05)


def _strata_bounds(z0, z1):
    """camadas [za, zb, dura] entre z0 e z1 (acima do P3) cortadas nas juntas GLOBAIS; sobra fina (< 1,0) junta"""
    out = []
    z, i = STRATA_Z0, 0
    while z < z1 and i < 400:
        t = STRATA_T[i % len(STRATA_T)]
        a, b = max(z, z0), min(z + t, z1)
        if b - a > 0.02:
            out.append([a, b, i % 2 == 0])
        z += t
        i += 1
    merged = []
    for s in out:
        if merged and (s[1] - s[0] < 1.0 or merged[-1][1] - merged[-1][0] < 1.0):
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def _dip(x, y):
    return STRATA_DIP[0] * (x - 100.0) + STRATA_DIP[1] * (y - 80.0)


def strata_rock(mb, box, rng, taper=0.8, n=9):
    """bloco de ROCHA NATURAL em estratos: a mesma planta (poligono convexo de n lados que enche a caixa) empilhada nas
    juntas globais; camada dura saliente (Cliff_Rock_SG), camada mole recuada e escura (Cliff_Rock_SG_Dark); cada
    camada tem o topo chanfrado (faixa de luar Cliff_Rock_SG_Top) e recua para o centro da massa conforme sobe
    (degraus que pegam luz). Topo da ultima camada = grama/liquen. Tudo dentro da caixa (x0, x1, y0, y1, z0, z1)."""
    x0, x1, y0, y1, z0, z1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    ph = rng.uniform(0.0, 2 * math.pi / n)
    shape = []
    for k in range(n):
        a = ph + 2 * math.pi * k / n + rng.uniform(-0.16, 0.16)
        ca, sa = math.cos(a), math.sin(a)
        f = rng.uniform(0.88, 1.0)
        shape.append((math.copysign(abs(ca) ** 0.7, ca) * f, math.copysign(abs(sa) ** 0.7, sa) * f))
    dv = Vector((MASS_C[0] - cx, MASS_C[1] - cy))
    dv = dv.normalized() if dv.length > 1e-3 else Vector((0.0, 0.0))
    bands = _strata_bounds(z0, z1)
    H = max(0.1, z1 - z0)
    gi, ti = mb._mi_for("Grass_SG"), mb._mi_for(RKT)
    bm = mb.bm
    for li, (za, zb, hard) in enumerate(bands):
        top = li == len(bands) - 1
        t = ((za + zb) / 2 - z0) / H
        s = 1.0 - (1.0 - taper) * t ** 1.15
        if not hard:
            s *= 0.9
        off = dv * ((1.0 - s) * min(hx, hy) * 0.85)
        ch = min(0.7, (zb - za) * 0.28)
        vs = []
        for zz, sc in ((za, s), (zb - ch, s * 0.94), (zb, s * 0.85)):
            for k, (u, v) in enumerate(shape):
                wv = 1.0 + 0.06 * math.sin(k * 2.3 + li * 1.7)          # a borda de cada camada muda (dirigido)
                px = cx + off.x + u * hx * sc * wv
                py = cy + off.y + v * hy * sc * wv
                vs.append(bm.verts.new((px, py, P3 + zz + _dip(px, py))))
        res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
        junk = list({v for v in res["geom_interior"] + res["geom_unused"] if isinstance(v, bmesh.types.BMVert)})
        if junk:
            bmesh.ops.delete(bm, geom=junk, context="VERTS")
        keep = [v for v in vs if v.is_valid]
        for f in mb._post(keep, ROCK if hard else RKD, None, 0, 1):
            nz = f.normal.z
            if nz > 0.97:
                f.material_index = gi if (top and zb > 6.0) else ti


def _surf(bvh, o, d):
    hit = bvh.ray_cast(Vector(o), Vector(d).normalized(), 200.0)
    if hit[0] is None:
        return None, None
    n = Vector(hit[1])
    if n.dot(Vector(d)) > 0:
        n = -n
    return hit[0], n


def house_shell():
    """a MASSA DE ROCHA da caverna: rocha NATURAL em estratos (juntas globais, camada dura saliente / mole recuada,
    degraus que recuam para o centro) em volta e em cima do tunel, fundindo com os montes do terreno; pinheiros nos
    topos. Nada de veio ou cristal por fora (acabamento: a magia nasce DENTRO da caverna). Depois: a boca e as
    colisoes."""
    chunk_check()
    mb = MB("SG_Dun_Cave_Body", "17_DUNGEON", random.Random(701), detail="near")
    for i, c in enumerate(CHUNKS):
        # ombros e sobrancelha (8 primeiros) quase a prumo: a rocha fica COLADA atras do arco (o arco nao fica solto)
        strata_rock(mb, c[:6], random.Random(7100 + i), taper=0.95 if i < 8 else (0.78 if c[5] - c[4] > 16.0 else 0.88))
    for i, (x, y, rx, ry, z0, z1) in enumerate(SPIRES):
        strata_rock(mb, (x - rx, x + rx, y - ry, y + ry, z0, z1), random.Random(7300 + i), taper=0.4, n=7)
    bvh = BVHTree.FromBMesh(mb.bm)
    mv = MB("SG_Dun_Cave_Pines", "17_DUNGEON", random.Random(705), detail="near")
    npine = 0
    for x, y, h in MASS_PINES:
        best = (None, None)
        for dx in (-2.4, 0.0, 2.4):
            for dy in (-2.4, 0.0, 2.4):
                q, nq = _surf(bvh, Vector((x + dx, y + dy, P3 + 90.0)), (0.0, 0.0, -1.0))
                if q is not None and (best[0] is None or nq.z > best[1].z):
                    best = (q, nq)
        p, n = best
        if p is None or n.z < 0.62:
            print("DUN AVISO pinheiro sem topo plano em", (x, y))
            continue
        VEG.pine(mv, p.x, p.y, p.z - 0.9, h, random.Random(int(x * 13 + y)), "fir", lod=1)
        npine += 1
    mb.finish()
    mv.finish()
    print("DUN massa: pinheiros %d" % npine)
    cave_mouth()
    # colisao da massa de rocha (caixas grossas; o tunel e as paredes da portaria ja tem as suas)
    ccol("SG_DunRock", (85.3, 59.2, P3 - 0.5), (89.8, 74.0, P3 + 28.0))           # ombro oeste
    ccol("SG_DunRock", (80.5, 74.0, P3 - 0.5), (89.8, 99.0, P3 + 28.0))           # flanco oeste
    ccol("SG_DunRock", (110.2, 59.2, P3 - 0.5), (114.7, 74.0, P3 + 30.0))         # ombro leste
    ccol("SG_DunRock", (110.2, 74.0, P3 - 0.5), (122.5, 97.0, P3 + 30.0))         # flanco leste
    ccol("SG_DunRock", (89.8, 83.4, P3 - 0.5), (110.2, 101.5, P3 + 33.0))         # costas
    # colisao das paredes da portaria: vao da boca (2 x MOUTH_W, teto em 21,8), fundo, lados e teto do tunel
    ccol("SG_DunHouse", (HX0, HY0, P3 - 0.5), (HX - MOUTH_W, IY0, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX + MOUTH_W, HY0, P3 - 0.5), (HX1, IY0, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX - MOUTH_W, HY0, P3 + 21.8), (HX + MOUTH_W, IY0, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX0, IY1, P3 - 0.5), (HX1, HY1, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX0, IY0, P3 - 0.5), (IX0, IY1, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (IX1, IY0, P3 - 0.5), (HX1, IY1, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (IX0, IY0, P3 + IN_CEIL), (IX1, IY1, P3 + IN_CEIL + 2.0))


def _arc_at(pts, f):
    """ponto e tangente (unitaria) a uma fracao f do comprimento de uma polilinha 2D"""
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    t = f * cum[-1]
    for i in range(len(pts) - 1):
        if cum[i + 1] >= t:
            a, b = pts[i], pts[i + 1]
            L_ = max(1e-6, cum[i + 1] - cum[i])
            k = (t - cum[i]) / L_
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
    a, b = pts[-2], pts[-1]
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    return b, ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)


PIL_BREAK = 12.7                                 # o pilar LESTE partiu nesta fiada (o topo caiu no patio)


def rest_box(mb, size, xy, rot, m, floor=P3 + 0.13, sink=0.1, bev=0.06):
    """caixa ROTACIONADA pousada no piso: o canto mais baixo fica 'sink' abaixo de 'floor' (nada flutua)"""
    from mathutils import Euler
    R = Euler(rot).to_matrix()
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    low = min((R @ Vector((sx * hx, sy * hy, sz * hz))).z for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1))
    c = (xy[0], xy[1], floor - sink - low)
    mb.box(size, c, rot, m, bev)
    return c


def pillar(mb, x, y, broken=False):
    """pilar da ordem: soco de obsidiana, fuste em fiadas navy com cintas de obsidiana, capitel e pinaculo com remate de
    pedra; estandarte de debrum DOURADO na face sul. broken = o pilar LESTE partiu na fiada PIL_BREAK (quebra em degrau,
    dirigida) e perdeu o topo e o estandarte. Sem brilho: a magia e de dentro da caverna."""
    mb.box2((x - 2.1, y - 2.1, P3 - 0.3), (x + 2.1, y + 2.1, P3 + 1.4), OB, 0.12)
    mb.box2((x - 1.9, y - 1.9, P3 + 1.4), (x + 1.9, y + 1.9, P3 + 1.7), VS, 0.0)
    top_h = PIL_BREAK if broken else PIL_H - 2.2
    h, k = 1.7, 0
    while h < top_h - 0.05:
        ch = min(2.6, top_h - h)
        w = 1.6 if k % 2 == 0 else 1.52
        m = OB if k % 3 == 2 else VA
        if m == OB:
            w = 1.72
            ch = 0.6
        mb.box2((x - w, y - w, P3 + h), (x + w, y + w, P3 + h + ch), m, 0.06)
        h += ch
        k += 1
    if broken:
        # quebra em degrau (nao ruido): 2/3 da fiada seguinte e um canto dela; faces lisas de fratura
        w = 1.6
        mb.box2((x - w, y - w, P3 + h), (x + 0.55, y + w, P3 + h + 1.25), VA, 0.06)
        mb.box2((x - w, y - 0.1, P3 + h + 1.25), (x - 0.35, y + w, P3 + h + 2.0), VA, 0.06)
        col_box2("SG_DunApproach", (x - 2.1, y - 2.1, P3 - 0.3), (x + 2.1, y + 2.1, P3 + h + 1.25))
        return P3 + h
    mb.box2((x - 2.0, y - 2.0, P3 + PIL_H - 2.2), (x + 2.0, y + 2.0, P3 + PIL_H - 1.1), OB, 0.1)
    mb.cyl(2.2, 1.6, (x, y, P3 + PIL_H - 0.3), (0.0, 0.0, math.pi / 4), m=OB, n=4, r2=0.7, bevel=0.0)
    mb.box2((x - 0.62, y - 0.62, P3 + PIL_H + 0.5), (x + 0.62, y + 0.62, P3 + PIL_H + 0.8), TR, 0.05)
    mb.cyl(0.62, 1.5, (x, y, P3 + PIL_H + 1.55), (0.0, 0.0, math.pi / 4), m=TR, n=4, r2=0.06, bevel=0.0)
    EM.banner(mb, mb, mb, mb, (x, y - 1.95, P3 + 19.6), -math.pi / 2, 3.0, 10.4, trim=GOLD)
    col_box2("SG_DunApproach", (x - 2.1, y - 2.1, P3 - 0.3), (x + 2.1, y + 2.1, P3 + PIL_H))
    return P3 + PIL_H


# o que caiu do lado LESTE (pilar partido + aduelas do arco externo): (tamanho, (x, y), rotacao, material)
RUBBLE = [((4.0, 4.0, 1.1), (119.7, 51.4), (0.16, -0.05, 0.52), OB),       # capitel do pilar, de lado
          ((3.2, 3.2, 2.5), (119.3, 57.0), (-0.1, 0.22, -0.3), VA),        # fiada do fuste
          ((2.3, 1.2, 1.6), (117.4, 48.6), (0.0, 0.12, 0.9), CS)]         # aduela do arco externo


def rubble(mb):
    for size, xy, rot, m in RUBBLE:
        c = rest_box(mb, size, xy, rot, m)
        top = c[2] + max(size) * 0.5
        col_box("SG_DunApproach", (size[0] * 0.9, size[1] * 0.9, top - P3 + 0.3), (xy[0], xy[1], (P3 + top) / 2 - 0.15),
                (0.0, 0.0, rot[2]))
    # 2 lascas pequenas junto do capitel (mesma queda)
    rest_box(mb, (0.9, 0.7, 0.6), (117.6, 52.9), (0.3, 0.1, 0.4), OB, bev=0.04)
    rest_box(mb, (1.1, 0.8, 0.7), (121.7, 54.4), (0.0, 0.25, 1.2), VA, bev=0.04)


def crystal_pedestal(mb, x, y, k):
    """MARCO de pedra da aproximacao (sem magia): soco de obsidiana, fuste navy com runa ENTALHADA (obsidiana, apagada),
    cinta de ferro negro com as argolas das correntes, capa de pedra e remate piramidal"""
    up = Vector((0.0, 0.0, 1.0))
    mb.box2((x - 1.35, y - 1.35, P3 - 0.2), (x + 1.35, y + 1.35, P3 + 0.6), OB, 0.08)
    mb.box2((x - 0.95, y - 0.95, P3 + 0.6), (x + 0.95, y + 0.95, P3 + 3.3), VA, 0.05)
    mb.box2((x - 1.03, y - 1.03, P3 + 2.55), (x + 1.03, y + 1.03, P3 + 2.95), BI, 0.0)
    mb.box2((x - 1.2, y - 1.2, P3 + 3.3), (x + 1.2, y + 1.2, P3 + 3.62), TR, 0.06)
    mb.cyl(1.05, 0.9, (x, y, P3 + 4.07), (0.0, 0.0, math.pi / 4), m=OB, n=4, r2=0.2, bevel=0.0)
    tx = -1.0 if x > HX else 1.0                                                  # face que olha o corredor
    glyph(mb, (x + tx * 0.96, y, P3 + 0.95), (0.0, tx, 0.0), up, (tx, 0.0, 0.0), k, 0.72, m=OB, dep=0.08)
    col_box2("SG_DunApproach", (x - 1.35, y - 1.35, P3 - 0.3), (x + 1.35, y + 1.35, P3 + 4.6))


def cave_mouth():
    """BOCA = RUINA ANTIGA encaixada na rocha: ombreiras de cantaria em fiadas, imposta de obsidiana, arco ogival de
    ADUELAS de pedra violeta sobre nucleo escuro (as juntas leem), ARCO EXTERNO de cantaria clara PARTIDO do lado leste,
    fecho de obsidiana com o emblema da ordem. Por fora nada brilha; a magia comeca NA boca: o cristal pendurado por
    corrente no fecho (gira = VFX_SGDUN_MouthCrystal) e a luz que vem do tunel."""
    mb = MB("SG_Dun_Cave_Mouth", "17_DUNGEON", random.Random(731), detail="near")
    F = Face(True, HY0, -1, P3)
    up = Vector((0.0, 0.0, 1.0))
    u3, n3 = F.u(), F.n()
    # 1. ombreiras: fiadas continuas (sem fresta), alternando largura e recuo (as juntas leem por sombra)
    COURSES = (2.4, 2.0, 2.6, 2.2, 2.3)
    for sg in (-1, 1):
        h, k = -0.3, 0
        while h < M_SPR - 1.05:
            ch = min(COURSES[k % len(COURSES)], M_SPR - 1.0 - h)
            ex = 0.0 if k % 2 == 0 else 0.3
            rc = 0.0 if k % 2 == 0 else 0.1
            s0, s1 = sorted((HX + sg * (M_HW - 0.1 + rc), HX + sg * (M_HW + M_T + 0.2 - ex)))
            fbox(mb, F, s0, s1, -0.3, M_DEP - rc, h, h + ch, CS, 0.1)
            h += ch
            k += 1
        s0, s1 = sorted((HX + sg * (M_HW - 0.5), HX + sg * (M_HW + M_T + 1.3)))
        fbox(mb, F, s0, s1, -0.3, M_DEP + 0.45, M_SPR - 1.0, M_SPR + 0.2, OB, 0.08)       # imposta
        s0, s1 = sorted((HX + sg * (M_HW + M_T + 0.2), HX + sg * (M_HW + M_T + 1.1)))
        fbox(mb, F, s0, s1, -0.3, M_DEP - 0.4, -0.3, M_SPR - 1.0, OB, 0.06)              # contraforte escuro
        for i, hh in enumerate((3.0, 5.6)):                                              # runas ENTALHADAS (apagadas)
            glyph(mb, F.v(HX + sg * (M_HW + M_T / 2), M_DEP + 0.02, hh), F.u(), up, F.n(), 2 * i + (0 if sg < 0 else 1),
                  0.7, m=OB, dep=0.1)
    # 2. nucleo escuro atras das aduelas (as juntas mostram sombra, nao ceu) + ADUELAS radiais de pedra violeta
    arch_band(mb, F, HX, M_HW + 0.15, M_RISE + 0.15, M_SPR, M_SPR, M_T - 0.5, -0.2, M_DEP - 0.25, OB, n=14)
    mid = ogive_right(M_HW + M_T / 2, M_RISE + M_T * 0.45, 60)
    NV = 7
    half = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(mid, mid[1:]))
    for sg in (-1, 1):
        for k in range(NV):
            fr = 0.9 * (k + 0.5) / NV
            (u, v), (tu, tv) = _arc_at(mid, fr)
            nu, nv = tv, -tu
            L_ = 0.9 * half / NV - 0.16
            rad = M_T * (1.0 if k % 2 == 0 else 1.1)
            c = F.v(HX + sg * u, M_DEP / 2 - 0.15, M_SPR + v)
            a_al = F.u() * (sg * tu) + up * tv
            a_rd = F.u() * (sg * nu) + up * nv
            obox3(mb, c, a_al, a_rd, F.n(), L_, rad, M_DEP + 0.3, VS)
    # 3. ARCO EXTERNO (cantaria clara) sobre as aduelas: inteiro a oeste, PARTIDO a leste (as pedras estao no patio)
    hw_h, rs_h, t_h = M_HW + M_T / 2 + 1.76 + 0.55, M_RISE + M_T * 0.45 + 1.76 + 0.55, 1.1
    midh = ogive_right(hw_h, rs_h, 60)
    halfh = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(midh, midh[1:]))
    NH = 9
    for sg in (-1, 1):
        for k in range(NH):
            if sg > 0 and k > 3:
                break
            fr = 0.9 * (k + 0.5) / NH
            ln = 0.9 * halfh / NH - 0.12
            if sg > 0 and k == 3:                              # a ultima pedra que ficou: metade, presa embaixo
                fr -= 0.9 / NH * 0.25
                ln *= 0.5
            (u, v), (tu, tv) = _arc_at(midh, fr)
            nu, nv = tv, -tu
            c = F.v(HX + sg * u, (M_DEP + 0.35 - 0.3) / 2, M_SPR + v)
            obox3(mb, c, F.u() * (sg * tu) + up * tv, F.u() * (sg * nu) + up * nv, F.n(), ln, t_h, M_DEP + 0.65, CS)
    # 4. FECHO: pedra de obsidiana saliente (2 prismas convexos) que prende aduelas e arco externo; emblema da ordem
    intr = ogive_right(M_HW, M_RISE, 60)
    outr = ogive_right(hw_h + t_h / 2, rs_h + t_h / 2, 60)
    (ui, vi), _ = _arc_at(intr, 0.86)
    (uo, vo), _ = _arc_at(outr, 0.88)
    top_k = rs_h + t_h / 2 + 0.5
    for sg in (-1, 1):
        q = [(HX + sg * ui, M_SPR + vi), (HX, M_SPR + M_RISE - 0.05), (HX, M_SPR + top_k), (HX + sg * uo, M_SPR + vo)]
        if sg > 0:
            q = list(reversed(q))
        slab(mb, F, q, -0.3, M_DEP + 0.7, OB)
    zc = M_SPR + (M_RISE + top_k) / 2 + 0.25
    EM.plaque(mb, mb, mb, mb, F.v(HX, M_DEP + 0.95, zc), -math.pi / 2, 1.15)
    # 5. o cristal da boca PENDURADO do fecho por corrente (argola no intradorso, capuz de prata)
    ya = HY0 - M_DEP / 2
    zi = P3 + M_SPR + M_RISE
    cc = Vector((HX, ya, zi - 4.0))              # ponta de baixo em P3+18,3: livre da placa DUNGEON_UI (P3+15,45)
    ch_top = Vector((HX, ya, zi - 0.55))
    mb.box2((HX - 0.5, ya - 0.5, zi - 0.25), (HX + 0.5, ya + 0.5, zi + 0.4), BI, 0.0)          # chapa no intradorso
    mb.rod(Vector((HX, ya, zi - 0.25)), ch_top, 0.1, BI, 6)
    cap = cc + up * (3.8 * 0.56 - 0.1)
    chain(mb, ch_top, cap + up * 0.55, 0.0, pitch=0.6)
    mb.cyl(0.55, 0.55, cap + up * 0.22, m=SV, n=6, r2=0.18, bevel=0.0)
    mb.finish()
    vf = MB("VFX_SGDUN_MouthCrystal", "12_VFX_HELPERS", random.Random(735), detail="near")
    crystal(vf, cc, 3.8, 1.0, 0.0, 0.0)
    ob = vf.finish()
    ob["pivot"] = [round(cc.x, 3), round(cc.y, 3), round(cc.z, 3)]
    ob["axis"] = [0.0, 0.0, 1.0]
    ob["rpm"] = 4.0
    ob["vfx"] = "cristal pendurado por corrente no fecho do arco (a magia comeca na boca): gira devagar e pulsa"
    # 6. pilares (o leste partido) + o que caiu; lanternas quentes ao pe das ombreiras e no inicio do corredor
    mp = MB("SG_Dun_Cave_Pillars", "17_DUNGEON", random.Random(739), detail="near")
    for i, (x, y) in enumerate(PILLAR_XY):
        pillar(mp, x, y, broken=(i == 1))
    rubble(mp)
    for x, y in LANTERN_XY:
        EM.lantern_pedestal(mp, mp, mp, (x, y, P3), 0.0, 1.0)
        col_box2("SG_DunApproach", (x - 0.95, y - 0.95, P3 - 0.3), (x + 0.95, y + 0.95, P3 + 5.2))
    mp.finish()
    # 7. colisao das ombreiras (o vao livre da boca e 2 x M_HW)
    for sg in (-1, 1):
        s0, s1 = sorted((HX + sg * M_HW, HX + sg * (M_HW + M_T + 1.1)))
        ccol("SG_DunMouth", (s0, HY0 - M_DEP - 0.5, P3 - 0.5), (s1, HY0 + 0.3, P3 + M_SPR + 1.5))
    print("DUN boca: arco hw %.1f apice %.1f | fecho %.1f..%.1f (u intradorso %.2f, externo %.2f) | cristal z %.1f"
          % (M_HW, M_SPR + M_RISE, M_SPR + M_RISE, M_SPR + top_k, ui, uo, cc.z - P3))


# ==================================================================== TUNEL (interior da caverna ate o vortice)
def tun_profile(hw, spr, rise, n_arc=7):
    """perfil (u, h) de uma secao do tunel: pe oeste -> parede -> ogiva -> apice -> ... -> pe leste (19 pontos)"""
    r = ogive_right(hw, rise, n_arc)
    left = [(-u, spr + v) for u, v in r]
    right = [(u, spr + v) for u, v in reversed(r)][1:]
    return [(-hw, -0.4), (-hw, spr * 0.5)] + left + right + [(hw, spr * 0.5), (hw, -0.4)]


def tun_at(y):
    """parametros (hw, arranque, flecha) interpolados no y"""
    for a, b in zip(TUN, TUN[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 3))
    s = TUN[0] if y < TUN[0][0] else TUN[-1]
    return s[1], s[2], s[3]


def tun_point(y, t):
    """ponto do perfil (sem jitter) na fracao t (0..1 pelos indices) + normal para DENTRO do tunel"""
    hw, spr, rise = tun_at(y)
    pr = tun_profile(hw, spr, rise)
    f = t * (len(pr) - 1)
    i = min(len(pr) - 2, int(f))
    k = f - i
    u = pr[i][0] + (pr[i + 1][0] - pr[i][0]) * k
    h = pr[i][1] + (pr[i + 1][1] - pr[i][1]) * k
    c = Vector((0.0, spr * 0.55))
    d = (c - Vector((u, h))).normalized()
    return Vector((HX + u, y, P3 + h)), Vector((d.x, 0.0, d.y))


def tunnel(mb, rng):
    """casca FACETADA do tunel: secoes ogivais que encolhem para o fundo (perspectiva), vertices puxados para dentro
    (rocha irregular), casca dupla fechada; gradiente de material: rocha escura na boca -> violeta profundo no fundo"""
    bm = mb.bm
    rows_i, rows_o = [], []
    last = len(TUN) - 1
    # ESTRATOS do tunel: o recuo de cada ponto do perfil e (quase) o mesmo em todas as secoes -> cristas e sulcos
    # CONTINUOS ao longo do tunel (camadas da rocha), nao facetas soltas
    kr = random.Random(719)
    KJ = [kr.choice((0.25, 0.45, 1.0)) for _ in range(len(tun_profile(*TUN[0][1:4])))]
    for j, (y, hw, spr, rise, jit) in enumerate(TUN):
        pr = tun_profile(hw, spr, rise)
        cen = Vector((0.0, spr * 0.55))
        ri, ro = [], []
        for k, (u, h) in enumerate(pr):
            p = Vector((u, h))
            d = (cen - p).normalized() if h > 0 else Vector((-math.copysign(1.0, u), 0.0))
            if 0 < j < last:
                p = p + d * (jit * (0.8 * KJ[k] + 0.2 * rng.random()))
                yy = y + rng.uniform(-0.2, 0.2)
            else:
                p = p + d * (jit * KJ[k])
                yy = y
            if h < 0:
                p.y = -0.4
            ri.append(bm.verts.new((HX + p.x, yy, P3 + p.y)))
            po = p - d * 0.9
            if h < 0:
                po.y = -0.4
            ro.append(bm.verts.new((HX + po.x, yy, P3 + po.y)))
        rows_i.append(ri)
        rows_o.append(ro)
    ns, npf = len(rows_i), len(rows_i[0])
    band_faces = []
    for j in range(ns - 1):
        fs = []
        for k in range(npf - 1):
            fs.append(bm.faces.new((rows_i[j][k], rows_i[j + 1][k], rows_i[j + 1][k + 1], rows_i[j][k + 1])))
            bm.faces.new((rows_o[j][k], rows_o[j][k + 1], rows_o[j + 1][k + 1], rows_o[j + 1][k]))
        band_faces.append(fs)
    for j in (0, ns - 1):
        for k in range(npf - 1):
            qd = (rows_i[j][k], rows_i[j][k + 1], rows_o[j][k + 1], rows_o[j][k])
            bm.faces.new(qd if j == 0 else tuple(reversed(qd)))
    for k in (0, npf - 1):
        for j in range(ns - 1):
            qd = (rows_i[j][k], rows_o[j][k], rows_o[j + 1][k], rows_i[j + 1][k])
            bm.faces.new(qd if k == 0 else tuple(reversed(qd)))
    mb._post([v for r in rows_i + rows_o for v in r], RKD, None, 0, 1)
    # gradiente: rocha natural na boca -> bandas do fundo em rocha violeta profunda (a luz do portal pega nelas)
    mi_deep = mb._mi_for(DEEP)
    for j, fs in enumerate(band_faces):
        for k, f in enumerate(fs):
            if j >= 4 or (j == 3 and (k // 3) % 2 == 0):
                f.material_index = mi_deep
    # parede do fundo (atras do portal), mesma rocha profunda
    y, hw, spr, rise, jit = TUN[-1]
    pr = tun_profile(hw + 0.4, spr + 0.2, rise + 0.3)
    fv = [bm.verts.new((HX + u, y + 0.2, P3 + h)) for u, h in pr]
    bv = [bm.verts.new((HX + u, y + 1.1, P3 + h)) for u, h in pr]
    bm.faces.new(fv)
    bm.faces.new(list(reversed(bv)))
    for k in range(len(pr)):
        k2 = (k + 1) % len(pr)
        bm.faces.new((fv[k2], fv[k], bv[k], bv[k2]))
    mb._post(fv + bv, DEEP, None, 0, 1)


def tunnel_veins(mb, bvh, rng):
    """veios de energia nas PAREDES DO TUNEL: nascem no anel do vortice e vem para a boca afinando ate sumir (a magia
    sai de dentro); seguem a rocha (raio do eixo do tunel ate a casca)"""
    nseg = 0
    for ang, ang1, ya, yb in TUN_VEINS:
        th = math.radians(ang)
        pts = []
        y = ya
        while y >= yb - 0.01:
            hw, spr, rise = tun_at(y)
            p, n = _surf(bvh, Vector((HX, y, P3 + spr * 0.55)), Vector((math.sin(th), 0.0, math.cos(th))))
            if p is not None:
                pts.append((p + n * 0.05, n, y))
            y -= 1.5
            f = max(0.0, min(1.0, (ya - y) / (ya - yb)))
            th = math.radians(ang + (ang1 - ang) * f) + 0.05 * math.sin(y * 0.7 + ang)    # ondula devagar
        for (a, na, y_a), (b, nb, y_b) in zip(pts, pts[1:]):
            if (b - a).length > 3.2:
                continue
            f = max(0.0, min(1.0, (y_a - yb) / max(0.1, ya - yb)))
            w = 0.08 + 0.2 * f
            ax = (b - a).normalized()
            nn = (na + nb).normalized()
            sd = nn.cross(ax).normalized()
            obox3(mb, (a + b) / 2, ax, sd, ax.cross(sd).normalized(), (b - a).length + w * 0.6, w, 0.12, VD)
            nseg += 1
    print("DUN tunel: %d segmentos de veio (do vortice para a boca)" % nseg)


# revestimento de cantaria dos primeiros metros do tunel: lado -> (y final da fiada de baixo, fiadas)
LINING = {-1: (65.4, 6), 1: (63.6, 4)}
LINING_ROWS = (1.9, 1.7, 1.8, 1.6, 1.7, 1.5)
LINING_LEN = (2.6, 2.2, 2.8, 2.4)
LINING_U = 8.5                                   # face da cantaria (colisao da boca em 8,4 / tunel em 8,0)


def mouth_lining(mb):
    """o ENCONTRO RUINA x CAVERNA: os antigos revestiram so os primeiros metros do tunel com cantaria em fiadas
    desencontradas; a parede termina em DEGRAUS partidos e a rocha natural continua (leste mais arruinado).
    So visual: a colisao das paredes do tunel ja esta atras dela."""
    y0 = HY0 + 0.1
    for sg, (y_end0, nrow) in LINING.items():
        h = -0.1
        for r in range(nrow):
            rh = LINING_ROWS[r]
            y_end = y_end0 - r * 1.1
            y = y0 - (1.3 if r % 2 else 0.0)
            i = r
            while y < y_end - 0.6:
                ln = LINING_LEN[i % len(LINING_LEN)]
                a, b = max(y, y0), min(y + ln, y_end)
                if b - a > 0.6:
                    s0, s1 = sorted((HX + sg * LINING_U, HX + sg * (LINING_U + 1.4)))
                    mb.box2((s0, a + 0.06, P3 + h), (s1, b - 0.06, P3 + h + rh - 0.08), CS, 0.08)
                y += ln
                i += 1
            h += rh


def house_interior():
    """interior da caverna: TUNEL de rocha facetada do arco ate o vortice (paredes e teto irregulares recuando em
    perspectiva), piso de lajes de marmore negro com os 2 fios de energia do corredor, estrado de 2 degraus (colisao
    casada) e aglomerados de cristal violeta nas paredes/teto, mais densos no fundo (gradiente escuro -> violeta)"""
    mb = MB("SG_Dun_Cave_Interior", "17_DUNGEON", random.Random(711), detail="near")
    rng = random.Random(713)
    tunnel(mb, rng)
    tunnel_veins(mb, BVHTree.FromBMesh(mb.bm), random.Random(717))
    mouth_lining(mb)
    # piso: base de obsidiana + lajes de marmore negro em fiadas desencontradas ate o estrado
    (y1, z1), (y2, z2) = DAIS
    mb.box2((IX0, HY0 - 0.2, P3 - 0.4), (IX1, y1, P3 + 0.06), OB, 0.0)
    yy, row = HY0 - 0.1, 0
    while yy < y1 - 0.4:
        dy = min(3.0, y1 - yy)
        hwf = tun_at(yy + dy / 2)[0] - 0.6
        xs = -hwf + (1.6 if row % 2 else 0.0)
        cuts = [-hwf] + [v for v in (xs + 3.2 * i for i in range(8)) if -hwf + 0.5 < v < hwf - 0.5] + [hwf]
        for a, b in zip(cuts, cuts[1:]):
            mb.box2((HX + a + 0.12, yy + 0.12, P3 - 0.1), (HX + b - 0.12, yy + dy - 0.12, P3 + 0.12), MBK, 0.0)
        yy += dy
        row += 1
    # estrado: 2 degraus (0,4 e 0,8: colisao casada), espelho de obsidiana, focinho de pedra violeta
    mb.box2((IX0 + 2.2, y1, P3 - 0.2), (IX1 - 2.2, y2, P3 + z1), OB, 0.06)
    mb.box2((IX0 + 2.2, y1 - 0.05, P3 + z1 - 0.14), (IX1 - 2.2, y1 + 0.35, P3 + z1 + 0.02), VS, 0.0)
    mb.box2((IX0, y2, P3 - 0.2), (IX1, IY1, P3 + z2), OB, 0.06)
    mb.box2((IX0, y2 - 0.05, P3 + z2 - 0.14), (IX1, y2 + 0.35, P3 + z2 + 0.02), VS, 0.0)
    col_box2("SG_DunHouse", (IX0 + 2.2, y1, P3 - 0.5), (IX1 - 2.2, y2, P3 + z1))
    col_box2("SG_DunHouse", (IX0, y2, P3 - 0.5), (IX1, IY1, P3 + z2))
    # fios de energia do corredor continuam ate o estrado (rentes: topo P3 + 0,15)
    # (acabamento: nascem DENTRO e se apagam em tracos junto a boca; por fora o piso e so pedra)
    for sx in (-LINE_DX, LINE_DX):
        for ya, yb in ((60.4, 60.9), (61.4, 62.3), (62.8, y1 - 0.3)):
            mb.box2((HX + sx - 0.12, ya, P3 + 0.0), (HX + sx + 0.12, yb, P3 + 0.15), VD, 0.0)
    # cristais do tunel (Neon, sem luz nova)
    for y, t, h, r in TUN_CRYSTALS:
        p, n = tun_point(y, t)
        base = p - n * 0.5
        d = n if 0.25 < t < 0.75 else (n + Vector((0.0, 0.0, 1.1))).normalized()
        cluster(mb, base, d, h, rng, r, boss=OB)
    # 2 aglomerados grandes no estrado ladeando o vortice
    for sg in (-1, 1):
        b = Vector((HX + sg * 7.7, 78.2, P3 + z2 - 0.2))
        cluster(mb, b, Vector((-sg * 0.4, -0.2, 1.0)), 4.8, rng, 0.95, boss=OB)
        col_box2("SG_DunHouse", (HX + sg * 7.7 - 1.3, 76.9, P3), (HX + sg * 7.7 + 1.3, 79.5, P3 + 5.5))
    mb.finish()
    # colisao das paredes do tunel (a rocha facetada; o vao andavel fica com >= 7,7 de meia-largura)
    for y0_, y1_, hwc in ((IY0, 69.0, 8.0), (69.0, 76.0, 7.7), (76.0, IY1, 7.6)):
        for sg in (-1, 1):
            s0, s1 = sorted((HX + sg * hwc, HX + sg * (IX1 - HX)))
            ccol("SG_DunHouse", (s0, y0_, P3 - 0.5), (s1, y1_, P3 + 14.0))
    light("L_SGDun_Portal", "POINT", (PX, 77.0, P3 + 7.5), 1200.0, (0.64, 0.42, 1.0), 1.5)


def portal_ring_dark(mb, c, u, v, n, r_in, r_out, floor_z):
    """anel ESCURO do vortice: aro de obsidiana com runas acesas, coroa de ferro negro com laminas de obsidiana em raio
    (ameaca) e fio de energia no labio interno; pes de obsidiana"""
    ring3(mb, c, u, v, n, r_in, r_in + 1.05, -0.6, 0.7, OB)
    ring3(mb, c, u, v, n, r_in + 1.05, r_out, -0.6, 0.42, BI)
    ring3(mb, c, u, v, n, r_in - 0.08, r_in + 0.1, -0.35, 0.78, VD)
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        glyph(mb, c + radial * (r_in + 0.2) + n * 0.7, tang, radial, n, k, 0.48, m=VD, dep=0.08, w=0.18)
    for k in range(12):
        a = 2 * math.pi * k / 12 + math.pi / 2
        if abs(math.sin(a) + 1.0) < 0.3:
            continue                                                          # nada de lamina para baixo
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        ln = 2.4 if k == 0 else (1.6 if k % 2 == 0 else 1.1)
        blade(mb, c + radial * (r_out - 0.3) + n * 0.05, radial, tang, n, ln, 0.9, 0.55, OB)
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        h = p.z + 0.4 - floor_z
        obox(mb, Vector((p.x, p.y, floor_z + h / 2)), u, v, n, 2.4, h, 2.2, OB, 0.08)


def house_portal():
    """vortice da portaria: anel escuro + disco (estaticos) e a espiral que gira (VFX_SGDUN_Portal)"""
    r_in, r_out = 5.4, 7.0
    zf = P3 + DAIS[1][1]
    c = Vector((PX, PY + 0.6, zf + r_out - 0.4))
    u, v, n = Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0))
    mb = MB("SG_Dun_House_Portal", "17_DUNGEON", random.Random(721), detail="near")
    portal_ring_dark(mb, c, u, v, n, r_in, r_out, zf)
    disc3(mb, c, u, v, n, r_in + 0.15, -0.5, -0.3, VO, 32)
    mb.finish()
    vf = MB("VFX_SGDUN_Portal", "12_VFX_HELPERS", random.Random(723), detail="near")
    spiral(vf, c, u, v, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7)
    ob = vf.finish()
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, -1.0, 0.0]
    ob["rpm"] = 5.0
    ob["vfx"] = "espiral violeta do portal da dungeon (gira no plano do disco)"
    col_box2("SG_DunPortal", (PX - r_out, PY - 0.2, zf), (PX + r_out, IY1, zf + 2 * r_out - 0.4))
    return c


# ==================================================================== APROXIMACAO (patio P3 ao sul da boca)
def approach_floor():
    """ferradura de lajes de marmore negro (juntas de obsidiana) + CORREDOR cerimonial reto desde as lanternas do eixo;
    2 fios de energia rentes (x = 100 +- 5,6) levam ate o estrado; soleira escura com runas. Topo das lajes P3+0,13."""
    mb = MB("SG_Dun_Approach_Floor", "17_DUNGEON", random.Random(781), detail="near")
    cx, cy = PC
    z0, zj, zt = P3 - 0.25, P3 + 0.07, P3 + 0.13
    arc = [(cx + PR * math.cos(math.pi + math.pi * k / 32), cy + PR * math.sin(math.pi + math.pi * k / 32))
           for k in range(33)]
    mb.prism(SL.ccw(arc), z0, zj, OB)
    mb.box2((cx - PR, cy - 0.01, z0), (cx + PR, HY0, zj), OB, 0.0)
    rings = (5.5, 9.0, 12.5, 16.0, 19.2, PR)
    for r0, r1 in zip(rings, rings[1:]):
        rm = (r0 + r1) / 2.0
        n = max(4, int(round(math.pi * rm / 3.3)))
        for i in range(n):
            ga = math.pi + math.pi * i / n + 0.13 / rm
            gb = math.pi + math.pi * (i + 1) / n - 0.13 / rm
            ra, rb = r0 + 0.13, r1 - 0.13
            gm = (ga + gb) / 2.0
            pts = [(cx + ra * math.cos(g), cy + ra * math.sin(g)) for g in (ga, gm, gb)] + \
                  [(cx + rb * math.cos(g), cy + rb * math.sin(g)) for g in (gb, gm, ga)]
            mb.prism(SL.ccw(pts), P3 - 0.1, zt, MBK)
    for x0 in (cx - PR, cx - PR + 3.0, cx - PR + 6.0, cx + PR - 9.0, cx + PR - 6.0, cx + PR - 3.0):
        mb.box2((x0 + 0.13, cy + 0.13, P3 - 0.1), (x0 + 2.87, HY0 - 0.13, zt), MBK, 0.0)
    # borda de obsidiana (limite do lugar do desafio sobre o calcamento do patio)
    rim_o = [(cx + (PR + 0.7) * math.cos(math.pi + math.pi * k / 32), cy + (PR + 0.7) * math.sin(math.pi + math.pi * k / 32))
             for k in range(33)]
    for k in range(32):
        a0, a1 = rim_o[k], rim_o[k + 1]
        i0, i1 = arc[k], arc[k + 1]
        if abs((a0[0] + a1[0]) / 2 - cx) < 6.8:
            continue                                                         # o corredor entra aqui
        mb.prism(SL.ccw([i0, i1, a1, a0]), z0, P3 + 0.3, OB)
    for sx in (-1, 1):
        xa = cx + sx * PR
        xb = cx + sx * (PR + 0.7)
        mb.box2((min(xa, xb), cy, z0), (max(xa, xb), HY0, P3 + 0.3), OB, 0.0)
    # corredor cerimonial: base de obsidiana, lajes de marmore negro em 2 fiadas desencontradas, meio-fio de obsidiana
    y_end = cy - PR + 1.0
    mb.box2((cx - 6.0, COR_Y0 - 1.0, z0), (cx + 6.0, y_end, zj), OB, 0.0)
    yy, row = COR_Y0 - 1.0, 0
    while yy < y_end - 0.3:
        dy = min(2.6, y_end - yy)
        cuts = (-6.0, -2.0, 2.0, 6.0) if row % 2 == 0 else (-6.0, -4.0, 0.0, 4.0, 6.0)
        for a, b in zip(cuts, cuts[1:]):
            mb.box2((cx + a + 0.13, yy + 0.13, P3 - 0.1), (cx + b - 0.13, yy + dy - 0.13, zt), MBK, 0.0)
        yy += dy
        row += 1
    for sx in (-1, 1):
        mb.box2((cx + sx * 6.0 - 0.35, COR_Y0 - 1.0, z0), (cx + sx * 6.0 + 0.35, y_end, P3 + 0.3), OB, 0.0)
    # soleira escura (meia-lua r 5,4 + recuo sob o arco) com runas
    a5 = [(cx + 5.37 * math.cos(math.pi + math.pi * k / 16), cy + 5.37 * math.sin(math.pi + math.pi * k / 16))
          for k in range(17)]
    mb.prism(SL.ccw(a5), P3 - 0.1, zt, OB)
    mb.box2((HX - M_HW, HY0 - M_DEP - 0.3, P3 - 0.1), (HX + M_HW, HY0, zt), OB, 0.0)
    # (acabamento: sem runas acesas nem fios de energia por fora; os fios nascem dentro do tunel)
    mb.finish()


def approach_guard():
    """2 pares de PEDESTAIS de obsidiana com cristal (funil que abre para o sul) acorrentados aos pilares da boca;
    1 luz violeta na aproximacao + 1 quente das lanternas da boca"""
    mb = MB("SG_Dun_Approach_Guard", "17_DUNGEON", random.Random(791), detail="near")
    for i, (x, y) in enumerate(PED_XY):
        crystal_pedestal(mb, x, y, i + 2)
    ys, yn = Vector((0.0, -1.0, 0.0)), Vector((0.0, 1.0, 0.0))
    for sg, (pa, pb) in ((-1, (0, 2)), (1, (1, 3))):
        px, py = PILLAR_XY[0 if sg < 0 else 1]
        (ax_, ay_), (bx_, by_) = PED_XY[pa], PED_XY[pb]
        # correntes presas em ARGOLAS: pilar (fiada navy) -> marco -> marco
        r0 = eye_ring(mb, (px, py - 1.52, P3 + 6.2), ys)
        r1 = eye_ring(mb, (ax_, ay_ + 1.03, P3 + 2.75), yn)
        r2 = eye_ring(mb, (ax_, ay_ - 1.03, P3 + 2.75), ys)
        r3 = eye_ring(mb, (bx_, by_ + 1.03, P3 + 2.75), yn)
        chain(mb, r0, r1, 0.8)
        chain(mb, r2, r3, 0.5)
    mb.finish()
    # a luz violeta mora DENTRO da boca: acende o intradorso e o tunel e so derrama no patio (mesma luz, outro lugar)
    light("L_SGDun_Approach", "POINT", (100.0, 63.5, P3 + 7.0), 1800.0, (0.62, 0.38, 1.0), 2.0)
    light("L_SGDun_MouthWarm", "POINT", (100.0, 51.5, P3 + 5.0), 1300.0, (1.0, 0.66, 0.36), 1.0)


def _approach_check():
    """folga das colisoes novas do patio ate as linhas do andador (corpo 1,1; exigimos >= 1,7) e o corredor x=100"""
    items = [("pedestal", x, y, 1.35 * math.sqrt(2.0)) for x, y in PED_XY]
    items += [("lanterna", x, y, 0.95 * math.sqrt(2.0)) for x, y in LANTERN_XY]
    items += [("pilar", x, y, 2.1 * math.sqrt(2.0)) for x, y in PILLAR_XY]
    items += [("entulho", xy[0], xy[1], max(sz[:2]) * 0.75) for sz, xy, rot, m in RUBBLE]
    worst = 99.0
    for nm, x, y, r in items:
        dmin = min(L.seg_dist(x, y, a[0], a[1], b[0], b[1])[0] for a, b in WALK_LINES) - r
        dcor = abs(x - HX) - r - 5.0
        worst = min(worst, dmin, dcor + 1.7)
        if dmin < 1.7 or dcor < 0.0:
            print("DUN AVISO aproximacao: %s (%.1f, %.1f) folga rota %.2f corredor %.2f" % (nm, x, y, dmin, dcor))
    print("DUN aproximacao: folga minima ate o andador/corredor = %.2f (exige >= 1,7)" % worst)


def approach():
    approach_floor()
    approach_guard()
    _approach_check()



# ==================================================================== SALAS (sob a ilha)
def room_walls():
    """paredes das 3 salas (visual + colisao identicos), piso e teto colidiveis"""
    mb = MB("SG_Dun_Rooms_Shell", "17_DUNGEON", random.Random(741), detail="far", floor=-999)
    zb, zt = Z - 0.6, ZCEIL
    y0l, y1l = LY - L.DUN_LINK_W / 2, LY + L.DUN_LINK_W / 2
    pieces = [
        ((-64.0, 60.0), (-62.0, 100.0)),            # R1 oeste
        ((-64.0, 98.0), (-26.0, 100.0)),            # R1 norte
        ((-64.0, 60.0), (-26.0, 62.0)),             # R1 sul
        ((-24.0, 102.0), (20.0, 104.0)),            # R2 norte
        ((-24.0, 56.0), (20.0, 58.0)),              # R2 sul
        ((22.0, 102.0), (68.0, 104.0)),             # R3 norte
        ((22.0, 56.0), (68.0, 58.0)),               # R3 sul
        ((66.0, 56.0), (68.0, 104.0)),              # R3 leste
    ]
    for xa, xb in ((-26.0, -24.0), (20.0, 22.0)):   # paredes compartilhadas com o vao de ligacao
        pieces += [((xa, 56.0), (xb, y0l)), ((xa, y1l), (xb, 104.0))]
        mb.box2((xa, y0l, Z + LINK_H), (xb, y1l, zt), CS, 0.0)
        ccol("SG_DunRoom", (xa, y0l, Z + LINK_H), (xb, y1l, zt))
    for (xa, ya), (xb, yb) in pieces:
        mb.box2((xa, ya, zb), (xb, yb, zt), CS, 0.0)
        ccol("SG_DunRoom", (xa, ya, zb), (xb, yb, zt))
    mb.finish()
    ccol("SG_DunRoom", (BX0, BY0, Z - 2.0), (BX1, BY1, Z))
    ccol("SG_DunRoom", (BX0, BY0, ZCEIL), (BX1, BY1, ZCEIL + 1.5))


def room_kit():
    """kit das salas: pilastras, colunas de canto, arcos cegos, cornijas, molduras dos vaos, tochas, pisos, abobadas"""
    mk = MB("SG_Dun_Rooms_Kit", "17_DUNGEON", random.Random(751), detail="near")
    mv = MB("SG_Dun_Rooms_Vault", "17_DUNGEON", random.Random(753), detail="near")
    mf = MB("SG_Dun_Rooms_Floor", "17_DUNGEON", random.Random(755), detail="near")
    mi = MB("SG_Dun_Rooms_Iron", "17_DUNGEON", random.Random(757), detail="near")
    A = "SG_DunKit"
    cx3 = sum(ROOMS["R3"][0::2]) / 2.0
    for nm in ("R1", "R2", "R3"):
        x0, y0, x1, y1 = ROOMS[nm]
        FS, FN = Face(True, y0, 1, Z), Face(True, y1, -1, Z)
        FW, FE = Face(False, x0, 1, Z), Face(False, x1, -1, Z)
        # colunas de canto
        for F, a, b in ((FS, x0, x1), (FN, x0, x1)):
            corner_col(mk, F, a, 1, R_SPR, A)
            corner_col(mk, F, b, -1, R_SPR, A)
        # paredes N/S: pilastras que carregam as nervuras
        if nm == "R1":
            ps = [x0 + 12.0, x0 + 24.0]
        elif nm == "R2":
            ps = [x0 + 11.0, x1 - 11.0]
        else:
            ps = [x0 + 11.0, x0 + 22.0, x0 + 33.0]
        for F in (FS, FN):
            bounds = [x0 + 2.4] + [q for p in ps for q in (p - PIL_HW - 0.3, p + PIL_HW + 0.3)] + [x1 - 2.4]
            for p in ps:
                pilaster(mk, F, p, R_SPR, A)
            for k in range(0, len(bounds), 2):
                sa, sb = bounds[k], bounds[k + 1]
                blind_arch(mk, F, sa, sb, 7.0, twin=(sb - sa > 16.0))
            cornice(mk, F, x0 + 2.4, x1 - 2.4, R_SPR)
            if nm == "R1":
                for p in ps:
                    torch(mi, F, p, PIL_D + 0.45, 8.4)
        # paredes L/O: vao de ligacao ou portal no eixo y 80, pilastras-ombreira, arcos cegos nos lados
        for F, side in ((FW, "W"), (FE, "E")):
            jam = (LY - L.DUN_LINK_W / 2 - PIL_HW - 0.3, LY + L.DUN_LINK_W / 2 + PIL_HW + 0.3)
            if (nm, side) in (("R1", "W"), ("R3", "E")):
                jam = (LY - 9.5, LY + 9.5)
            for p in jam:
                pilaster(mk, F, p, R_SPR, A)
                torch(mi, F, p, PIL_D + 0.45, 8.4)
            blind_arch(mk, F, y0 + 2.4, jam[0] - PIL_HW - 0.3, 7.0)
            blind_arch(mk, F, jam[1] + PIL_HW + 0.3, y1 - 2.4, 7.0)
            cornice(mk, F, y0 + 2.4, jam[0] - PIL_HW - 0.3, R_SPR)
            cornice(mk, F, jam[1] + PIL_HW + 0.3, y1 - 2.4, R_SPR)
            is_link = (nm == "R1" and side == "E") or nm == "R2" or (nm == "R3" and side == "W")
            if is_link:
                link_frame(mk, F, LY, L.DUN_LINK_W / 2)
        # piso de lajes com friso; R3: medalhao do altar no centro (sob o minerio SUPERLEGENDARY)
        cxr, cyr = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        skip = (lambda x, y, cx=cxr, cy=cyr: abs(x - cx) < 9.0 and abs(y - cy) < 9.0) if nm == "R3" else None
        tile_floor(mf, (x0, y0, x1, y1), Z, tile=4.0, margin=1.0, friso=0.8, skip=skip)
        # abobada de bercos ao longo de x com nervuras nas pilastras
        vault(mv, (x0, y0, x1, y1), "x", Z, R_SPR, R_CROWN, ribs=ps)
    # soleiras dos vaos
    for xa, xb in ((-26.0, -24.0), (20.0, 22.0)):
        mf.box2((xa, LY - L.DUN_LINK_W / 2, Z - 0.4), (xb, LY + L.DUN_LINK_W / 2, Z), TR, 0.0)
    # medalhao do altar da R3 (embutido, topo exato no piso: nada colidivel perto do minerio)
    altar_medallion(mf, *[(ROOMS["R3"][0] + ROOMS["R3"][2]) / 2.0, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0])
    # lustres: 2 na R2 (mineracao), 1 coroa na R3 (altar)
    for x, y, h, r in ((-13.0, LY, 16.5, 3.0), (9.0, LY, 16.5, 3.0), (cx3, LY, 15.8, 3.8)):
        rect = ROOMS["R2"] if x < 21.0 else ROOMS["R3"]
        top = vault_z(rect, "x", Z, R_SPR, R_CROWN, 0.0) - 0.8
        chandelier(mi, x, y, Z + h, top, r=r, n=8 if r < 3.5 else 12)
    for m in (mk, mv, mf, mi):
        m.finish()


def altar_medallion(mb, cx, cy):
    """quadrado 18 x 18 sem lajes -> anel de cantaria -> campo navy -> anel de prata -> disco (tudo com topo em Z)"""
    n = 32
    ang = [2 * math.pi * k / n for k in range(n)]
    Hs = 9.0

    def circ(r):
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in ang]
    sq = [(cx + Hs * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
           cy + Hs * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    # o quadrado de 18 fica no miolo da grade (ja sem lajes): a borda e ajustada a grade na sala
    rings = [(sq, circ(7.8), FL), (circ(7.8), circ(7.0), TR), (circ(7.0), circ(3.2), VA), (circ(3.2), circ(2.7), SV)]
    zt, zb = Z, Z - 0.4
    bm = mb.bm
    for outer, inner, m in rings:
        oT = [bm.verts.new((x, y, zt)) for x, y in outer]
        iT = [bm.verts.new((x, y, zt)) for x, y in inner]
        oB = [bm.verts.new((x, y, zb)) for x, y in outer]
        iB = [bm.verts.new((x, y, zb)) for x, y in inner]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
            bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
            bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
            bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
        mb._post(oT + iT + oB + iB, m, None, 0, 1)
    mb.prism(circ(2.7), zb, zt, FL)
    # 8 runas da ordem no campo navy (no lugar dos raios de estrela), rentes: topo Z + 0,03
    up = Vector((0.0, 0.0, 1.0))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        glyph(mb, Vector((cx, cy, zt - 0.1)) + rad * 3.9, Vector((-rad.y, rad.x, 0.0)), rad, up, k, 1.5, RG, dep=0.13)


def floor_runes(mb, c, n):
    """arco de 7 runas rentes ao piso diante de um portal das salas (c = pe do portal, n = para dentro da sala)"""
    up = Vector((0.0, 0.0, 1.0))
    base = math.atan2(n.y, n.x)
    for i in range(7):
        a = base + math.radians(-54.0 + 18.0 * i)
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        glyph(mb, Vector((c.x, c.y, Z - 0.1)) + rad * 7.0, Vector((-rad.y, rad.x, 0.0)), -rad, up, i + 2, 1.0, RG,
              dep=0.13)
    for i in range(24):
        a0 = base + math.radians(-66.0 + 5.5 * i)
        a1 = a0 + math.radians(5.5)
        p0 = Vector((c.x + 9.2 * math.cos(a0), c.y + 9.2 * math.sin(a0), Z - 0.07))
        p1 = Vector((c.x + 9.2 * math.cos(a1), c.y + 9.2 * math.sin(a1), Z - 0.07))
        ax = (p1 - p0).normalized()
        obox3(mb, (p0 + p1) / 2, ax, Vector((-ax.y, ax.x, 0.0)), up, (p1 - p0).length + 0.05, 0.3, 0.2, RG)


def room_portals():
    """portal de chegada (R1, parede oeste, aceso) e portal de saida (R3, parede leste): mesma peca da portaria"""
    mb = MB("SG_Dun_Rooms_Portals", "17_DUNGEON", random.Random(761), detail="near")
    r_in, r_out = 5.0, 6.5
    x0 = ROOMS["R1"][0]
    x1 = ROOMS["R3"][2]
    v = Vector((0, 0, 1))
    specs = [("R1", Vector((x0 + 1.0, LY, Z + r_out - 0.3)), Vector((1, 0, 0)), Face(False, x0, 1, Z)),
             ("R3", Vector((x1 - 1.0, LY, Z + r_out - 0.3)), Vector((-1, 0, 0)), Face(False, x1, -1, Z))]
    out = {}
    for nm, c, n, F in specs:
        u = n.cross(v).normalized()
        portal_frame(mb, c, u, v, n, r_in, r_out, Z)
        disc3(mb, c, u, v, n, r_in + 0.15, -0.5, -0.3, VO if nm == "R1" else VA, 32)
        # nicho ogival navy atras do anel + arquivolta
        arch_panel(mb, F, LY, r_out + 0.2, r_out + 0.8, c.z - Z, 0.0, 0.0, 0.15, VA, n=8)
        arch_band(mb, F, LY, r_out + 0.2, r_out + 0.8, c.z - Z, 0.0, 0.6, 0.0, 0.55, TR, n=8)
        ccol("SG_DunPortal", F.p(LY - r_out, 0.0, -0.5), F.p(LY + r_out, 1.75, 2 * r_out - 0.6))
        floor_runes(mb, Vector((c.x, c.y, Z)), n)
        out[nm] = (c, u, n)
    c, u, n = out["R1"]
    spiral(mb, c, u, v, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7, a0=0.4)
    mb.finish()
    # espiral da saida: objeto proprio (o jogo mostra so em FINISHING/FINISHED)
    c, u, n = out["R3"]
    ms = MB("SG_Dun_R3_ExitSpiral", "17_DUNGEON", random.Random(763), detail="near")
    spiral(ms, c, u, v, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7, a0=1.1)
    ob = ms.finish()
    ob["show"] = "FINISHING,FINISHED"
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [round(n.x, 3), round(n.y, 3), round(n.z, 3)]
    ob["note"] = "espiral do portal de saida: o jogo liga (Transparency 0) quando a corrida termina"


def room_lights():
    x0 = ROOMS["R1"][0]
    light("L_SGDun_R1_Portal", "POINT", (x0 + 6.0, LY, Z + 7.0), 2600.0, (0.64, 0.42, 1.0), 1.5)
    light("L_SGDun_R2_ChandelierW", "POINT", (-13.0, LY, Z + 15.8), 5200.0, (1.0, 0.68, 0.40), 1.0)
    light("L_SGDun_R2_ChandelierE", "POINT", (9.0, LY, Z + 15.8), 5200.0, (1.0, 0.68, 0.40), 1.0)
    cx3 = sum(ROOMS["R3"][0::2]) / 2.0
    light("L_SGDun_R3_Altar", "POINT", (cx3, LY, Z + 15.0), 5600.0, (1.0, 0.68, 0.40), 1.0)


def build():
    _SKIP.clear()
    house_shell()
    house_interior()
    house_portal()
    approach()
    room_walls()
    room_kit()
    room_portals()
    room_lights()
    bad = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith(("SG_Dun_", "VFX_SGDUN_")):
            nd = sum(1 for p in o.data.polygons if p.area < 1e-6)
            if nd:
                bad.append((o.name, nd, [tuple(round(c, 1) for c in o.data.polygons[i].center)
                                         for i in range(len(o.data.polygons)) if o.data.polygons[i].area < 1e-6][:3]))
    print("DUN faces degeneradas:", bad or "nenhuma")
    if _SKIP:
        print("DUN AVISO colisoes omitidas por folga de minerio (so visual):", _SKIP)
    else:
        print("DUN folga dos minerios: OK (nenhuma colisao a menos de 5 de DUN_ORE_* ate piso+12)")
