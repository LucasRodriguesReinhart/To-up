# sg_dungeon - ZONA DUNGEON da Ilha 3 (Shadow Garden). build() substitui sg_blockout.dungeon (inclusive as colisoes e as
# luzes dela). Prefixo SG_Dun_, colecao 17_DUNGEON, VFX_SGDUN_* em 12_VFX_HELPERS. A dungeon e a "corrida de mineracao"
# periodica do jogo (XX:00 / XX:30): o jogador entra pelo PORTAL (vortice no fundo da caverna, superficie, P3) e o jogo o
# leva para as 3 SALAS modulares escondidas dentro da rocha (piso DUN_Z 6,0; teto DUN_CEIL 28); minera nos DUN_ORE_* e
# sai pelo portal de saida da R3. O sistema e do jogo: aqui so o LUGAR. NAO modela minerio.
# v3 (2026-09-29, referencia dominante refs/v2/ref2_dungeon_cave.png): a portaria e uma BOCA DE CAVERNA.
# ACABAMENTO (2026-09-29): CAVERNA ANTIGA EM RUINAS COM MAGIA QUE SURGE DE DENTRO. Gradiente de brilho: EXTERIOR quase
# natural (so lanternas quentes e o emblema) -> BOCA (cristal pendurado, fios que se apagam em tracos) -> TUNEL forte
# (veios que saem do vortice, cristais mais densos no fundo, portal). Sem brilho a entrada se sustenta pela forma.
# OVERHAUL 09 (2026-09-29, AUDITORIA2 09.01-09.13, "tolerancia zero"): caverna ANTIGA em ruina com a magia vindo de
#   dentro. Rocha FRATURADA (bancos grossos + diaclases verticais de rumo unico, blocos deslocados, labios; rock_mass) no
#   lugar dos estratos empilhados; boca em cantaria da RUINA (Stone_SGDunRuin, um tom acima da rocha) com quinas
#   quebradas, aduelas em CUNHA, arco externo partido com fratura; revestimento do tunel com quebra irregular e pedra
#   caida; UM alfabeto de runas = o dos obeliscos (rune); cristais em COLUNA hexagonal com calo (so a ponta acende);
#   veios em FENDA; pilares/marcos/entulho com pecas de verdade (kit do castelo: pinnacle, sq_ch); salas com pilastras
#   de base e capitel + colunelos, arcadas cegas de 2 ordens, piso em 2 tamanhos, nervuras em pera, tochas de ferro,
#   portal de aduelas e inscricao entalhada; variacao dirigida R1 (arcos altos) / R2 (escoras + grelhas) / R3
#   (colunelos duplos + retabulo). Planta, marcadores, colisoes e gameplay IGUAIS.
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
# ------------------------------------------------------------------ materiais novos da zona (6 + TrimLow do kit do castelo +
# vela do kit do salao; os pinheiros trazem 2 do sg_veg = 10)
NEW_MATS = {
    "Stone_SGDunVault": (S(34, 38, 62), 0.8, 0.0, 0, None, 0.06),      # navy escuro: abobadas, fustes dos pilares
    "SG_DunVoid_Glow": (S(46, 26, 104), 0.3, 0.0, 1.0, S(56, 30, 124), 0.0),   # fundo do vortice (violeta profundo)
    "Stone_SGDunCaveDeep": (S(40, 24, 74), 0.8, 0.0, 0, None, 0.06),          # pedra violeta profunda do fundo do tunel
    # OVERHAUL 09 (2026-09-29): cantaria da RUINA um tom acima da rocha (09.02); cristal = casca escura nao emissiva
    # (Crystal_ -> SmoothPlastic) + ponta Neon media menos saturada (09.08)
    "Stone_SGDunRuin": (S(80, 74, 102), 0.85, 0.0, 0, None, 0.08),
    "Crystal_SGDun": (S(62, 42, 108), 0.3, 0.0, 0, None, 0.04),
    "SG_DunCrystal_Glow": (S(140, 100, 228), 0.3, 0.0, 2.2, S(140, 100, 228), 0.0),
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)
fm_lib.RBX_CAL.setdefault("SG_DunCrystal_Glow", (None, [int(c) for c in fm_lib.to_srgb(NEW_MATS["SG_DunCrystal_Glow"][0])]))
# a abobada das salas nao usa a textura de ruido da pedra (14.02): a leitura vem das nervuras
if ("Stone_SGDunVault", None) not in fm_lib.TEX_RULES:
    fm_lib.TEX_RULES = (("Stone_SGDunVault", None),) + tuple(fm_lib.TEX_RULES)
import sg_castle as CA                           # kit de cantaria do overhaul (pinnacle, finial, sq_ch, drip)
import sg_hall as HA                             # kit de vela (12.09) e perfil de nervura em pera
RUIN, CSH, CGL = "Stone_SGDunRuin", "Crystal_SGDun", "SG_DunCrystal_Glow"
TRL = CA.CAPL                                    # Stone_SG_TrimLow: remate perto do jogador (14.01)
WD = "Wood_SG_Dark"

CS, BL, FL = "Stone_SG_Castle", "Stone_SG_Block", "Stone_SG_Floor"
VA, VO = "Stone_SGDunVault", "SG_DunVoid_Glow"
NAVY, SLATE, SV, IR = "Roof_SG_Navy", "Roof_SG_Slate", "Metal_SG_Silver", "Metal_SG_Iron"
GL, WW, VG = "Lantern_Glow", "Window_Warm", "SG_Violet_Glow"
# paleta de identidade (sg_lib.SMATS, refinamento): funcao de cada material na dungeon
OB, MBK, VS, BI = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Stone_SG_Violet", "Metal_SG_BlackIron"
VD = "SG_VioletDeep_Glow"

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
DEEP, GOLD = "Stone_SGDunCaveDeep", "Metal_Gold"
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
# mergulho das juntas GLOBAIS da massa de rocha (bancos e diaclases: ver OVERHAUL 09.01, rock_mass)
STRATA_DIP = (-0.05, 0.025)                      # dz por stud em x / y a partir de (100, 80): camadas sobem a oeste
MASS_C = (100.0, 88.0)                           # centro da massa: os degraus dos estratos recuam para ele
# pinheiros no topo da massa (x, y, altura): so onde o raio acha topo quase plano
MASS_PINES = [(84.0, 90.0, 10.5), (86.5, 76.5, 9.0), (116.5, 80.0, 9.5), (117.5, 91.0, 11.0), (108.0, 94.5, 8.5),
              (95.0, 96.5, 9.5), (113.0, 69.0, 7.5)]
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
    # overhaul 09 (2026-09-29): closes na altura do jogador (antes/depois)
    "CAM_SGDun_OV_Jamb": ((95.5, 44.0, P3 + 5.2), (88.5, 57.5, P3 + 5.5), 24),
    "CAM_SGDun_OV_Rubble": ((125.0, 43.0, P3 + 5.2), (118.5, 53.5, P3 + 1.5), 24),
    "CAM_SGDun_OV_Marker": ((99.0, 38.0, P3 + 5.2), (86.5, 46.0, P3 + 2.8), 26),
    "CAM_SGDun_OV_Rock": ((126.0, 50.0, P3 + 5.2), (113.0, 70.0, P3 + 12.0), 20),
    "CAM_SGDun_OV_TunnelWall": ((98.5, 61.0, P3 + 5.2), (91.0, 69.0, P3 + 4.0), 22),
    "CAM_SGDun_OV_Crystal": ((96.5, 72.5, P3 + 5.0), (92.3, 78.0, P3 + 3.0), 30),
    "CAM_SGDun_OV_Torch": ((-47.0, 69.0, Z + 7.0), (-50.0, 64.8, Z + 8.6), 30),
    "CAM_SGDun_OV_Portal": ((-49.0, 76.0, Z + 5.2), (-61.0, 80.0, Z + 6.2), 20),
    "CAM_SGDun_OV_R2Wall": ((0.0, 88.0, Z + 5.2), (-4.0, 102.0, Z + 8.0), 20),
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


# OVERHAUL 09 (09.04/09.13/16.07): UM alfabeto de runas na ilha inteira = sg_court.RUNE_SEGS (runas ANGULARES da
# ordem: haste + ramos diagonais, nada de curva de letra latina). Os obeliscos do patio usam o MESMO desenho.
import sg_court as CT


def rune(mb, o, ea, eb, en, k, sc, m=OB, dep=0.05, w=0.09):
    """runa k do alfabeto da ilha com CENTRO em o, no plano (ea lateral, eb 'cima'), tracos saltando 'dep' ao longo
    de en (entalhe: o traco e o FUNDO escuro/aceso do sulco). sc = 1 -> glifo de 0,76 de altura (o do obelisco)."""
    o, ea, eb, en = Vector(o), Vector(ea).normalized(), Vector(eb).normalized(), Vector(en).normalized()
    ww = w * sc
    for (a0, b0), (a1, b1) in CT.RUNE_SEGS[k % len(CT.RUNE_SEGS)]:
        p0 = o + ea * (a0 * sc) + eb * (b0 * sc)
        p1 = o + ea * (a1 * sc) + eb * (b1 * sc)
        d = p1 - p0
        ax = d.normalized()
        ay = en.cross(ax).normalized()
        obox3(mb, (p0 + p1) / 2 + en * (dep / 2), ax, ay, en, d.length + ww, ww, dep, m)


# ------------------------------------------------------------------ OVERHAUL 09: solidos convexos (casco) e cortes
def _dedupe3(pts, tol=2e-3):
    out = []
    for p in pts:
        p = Vector(p)
        if all((p - q).length > tol for q in out):
            out.append(p)
    return out


def hull(mb, pts, m, face_m=None):
    """solido convexo dos pontos (sem pontos internos). face_m(normal, centro) -> material ou None (troca por face)"""
    bm = mb.bm
    vs = [bm.verts.new(p) for p in _dedupe3(pts)]
    if len(vs) < 4:
        for v in vs:
            bm.verts.remove(v)
        return []
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({v for v in res["geom_interior"] + res["geom_unused"] if isinstance(v, bmesh.types.BMVert)})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    for _ in range(4):                                # pontos colineares -> triangulo de area nula: colapsa a aresta
        fs = {f for v in vs if v.is_valid for f in v.link_faces}
        bad = [f for f in fs if f.calc_area() < 2e-5]
        if not bad:
            break
        es = list({min(f.edges, key=lambda e: e.calc_length()) for f in bad})
        bmesh.ops.collapse(bm, edges=es, uvs=False)
    keep = [v for v in vs if v.is_valid]
    faces = mb._post(keep, m, None, 0, 1)
    if face_m:
        cache = {}
        for f in faces:
            mm = face_m(f.normal, f.calc_center_median())
            if mm:
                if mm not in cache:
                    cache[mm] = mb._mi_for(mm)
                f.material_index = cache[mm]
    return faces


def clip(pts, n, c):
    """recorta o poliedro convexo dos pontos pelo semiespaco n.p <= c: vertices do casco que ficam + intersecoes das
    ARESTAS do casco com o plano (exato, sem pontos internos)"""
    n = Vector(n)
    tmp = bmesh.new()
    tv = [tmp.verts.new(p) for p in _dedupe3(pts)]
    res = bmesh.ops.convex_hull(tmp, input=tv, use_existing_faces=False)
    edges = [e for e in res["geom"] if isinstance(e, bmesh.types.BMEdge)]
    out = [v.co.copy() for v in tmp.verts if v.link_edges and n.dot(v.co) <= c + 1e-6]
    for e in edges:
        a, b = e.verts[0].co, e.verts[1].co
        da, db = n.dot(a) - c, n.dot(b) - c
        if (da < -1e-6 < 1e-6 < db) or (db < -1e-6 < 1e-6 < da):
            out.append(a.lerp(b, da / (da - db)))
    tmp.free()
    return _dedupe3(out, 0.01)


def cbox_pts(c, ax, ay, az, sx, sy, sz, ch):
    """pontos de uma caixa orientada com TODAS as arestas chanfradas 'ch' (24 pontos: cada canto vira 3)"""
    c, ax, ay, az = Vector(c), Vector(ax), Vector(ay), Vector(az)
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    ch = max(0.0, min(ch, hx * 0.45, hy * 0.45, hz * 0.45))
    out = []
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                if ch < 1e-4:
                    out.append(c + ax * (i * hx) + ay * (j * hy) + az * (k * hz))
                    continue
                for a, b, d in ((ch, 0, 0), (0, ch, 0), (0, 0, ch)):
                    out.append(c + ax * (i * (hx - a)) + ay * (j * (hy - b)) + az * (k * (hz - d)))
    return out


def cbox(mb, c, ax, ay, az, sx, sy, sz, m, ch=0.1, cuts=(), face_m=None):
    """bloco orientado chanfrado; cuts = [(normal LOCAL (x, y, z), recuo a partir do canto mais externo nessa
    direcao)] = faces de FRATURA / quinas quebradas (ruina dirigida, nada sorteado)"""
    c, ax, ay, az = Vector(c), Vector(ax).normalized(), Vector(ay).normalized(), Vector(az).normalized()
    pts = cbox_pts(c, ax, ay, az, sx, sy, sz, ch)
    for nl, dep in cuts:
        nw = (ax * nl[0] + ay * nl[1] + az * nl[2]).normalized()
        top = max(nw.dot(p) for p in pts)
        pts = clip(pts, nw, top - dep)
    return hull(mb, pts, m, face_m)


def fblock(mb, F, s0, s1, d0, d1, h0, h1, m, ch=0.1, cuts=(), face_m=None):
    """bloco de cantaria no referencial da face F (s ao longo, d para fora, h para cima); cuts em (s, d, h) locais"""
    up = Vector((0.0, 0.0, 1.0))
    c = F.v((s0 + s1) / 2.0, (d0 + d1) / 2.0, (h0 + h1) / 2.0)
    return cbox(mb, c, F.u(), F.n(), up, abs(s1 - s0), abs(d1 - d0), abs(h1 - h0), m, ch, cuts, face_m)


def fledge(mb, F, s0, s1, prof, m):
    """perfil [(d, h)] (poligono CONVEXO no plano d-h da face F) extrudado de s0 a s1: cornija, imposta, cordao"""
    pts = [F.v(s, d, h) for s in (s0, s1) for d, h in prof]
    return hull(mb, pts, m)


def lathe_ax(mb, o, ax, prof, m, n=6, ph=0.0):
    """revolucao em torno de um eixo qualquer (o = origem, ax = direcao); prof = [(raio, distancia)] de baixo para
    cima, raio 0 = polo (tampas nas pontas com raio > 0): fustes, remates, colunas de cristal"""
    o, ax = Vector(o), Vector(ax).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    bm = mb.bm
    rows = []
    for r, d in prof:
        if r < 1e-5:
            rows.append([bm.verts.new(o + ax * d)])
        else:
            rows.append([bm.verts.new(o + ax * d + (e1 * math.cos(ph + 2 * math.pi * i / n) +
                                                    e2 * math.sin(ph + 2 * math.pi * i / n)) * r) for i in range(n)])
    faces = []
    for A, B in zip(rows, rows[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new((A[0], B[i], B[j])))
            elif len(B) == 1:
                faces.append(bm.faces.new((A[i], A[j], B[0])))
            else:
                faces.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    for R in (rows[0], rows[-1]):
        if len(R) > 2:
            faces.append(bm.faces.new(R))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return mb._post([v for r in rows for v in r], m, None, 0, 1)


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


# ------------------------------------------------------------------ KIT DAS SALAS (OVERHAUL 09.10: Tier A)
# linguagem unica de chanfro 0,1 na cantaria; remates em Stone_SG_TrimLow (14.01); pecas redondas em torno (n 10)
PIL_D, PIL_HW = 1.5, 1.5
COL_R = 0.42                                     # colunelo engastado da pilastra
UPZ = Vector((0.0, 0.0, 1.0))


def fplinth(mb, F, s0, s1, d1, h0, h1, e, m, d0=-0.2):
    """soco em TALUDE: retangulo s0..s1 x d0..d1 em h0 que recua 'e' (frente e lados) ate h1"""
    pts = [F.v(s, d, h0) for s in (s0, s1) for d in (d0, d1)]
    pts += [F.v(s, d, h1) for s in (s0 + e, s1 - e) for d in (d0, d1 - e)]
    return hull(mb, pts, m)


def colonette(mb, F, s, d, h0, h1, r, cap=True):
    """colunelo redondo em pe na face F (centro s, d): base com PLINTO e TORO, fuste, capitel em SINO com astragalo.
    h0 = pe, h1 = topo do capitel (o abaco e o bloco de cima)"""
    o = F.v(s, d, 0.0)
    x, y, z0 = o.x, o.y, o.z
    EM._lathe(mb, (x, y, z0 + h0), [(r + 0.24, 0.0), (r + 0.24, 0.16), (r + 0.1, 0.32), (r + 0.02, 0.5)],
              TRL, 8, math.pi / 8, caps=(False, True))
    EM._lathe(mb, (x, y, z0 + h0 + 0.5), [(r, 0.0), (r, h1 - h0 - (1.05 if cap else 0.5))], CS, 8, math.pi / 8,
              caps=(False, False))
    if cap:
        EM._lathe(mb, (x, y, z0 + h1 - 1.05), [(r + 0.1, 0.0), (r + 0.1, 0.14), (r + 0.04, 0.45),
                                                (r + 0.3, 0.85)], TRL, 8, math.pi / 8, caps=(False, True))
        a = r + 0.38                                                                    # abaco sobre o sino
        fblock(mb, F, s - a, s + a, d - a, d + a, h1 - 0.2, h1, TRL, 0.0)


def pilaster(mb, F, s, top, area=None, twin=False, altar=False, mi=None):
    """pilastra (09.10): soco de obsidiana chanfrado em talude, fuste de cantaria chanfrado, COLUNELO engastado
    (twin = colunelos DUPLOS: R3), capitel moldurado onde a nervura nasce; altar = a pilastra do eixo da R3 vira
    RETABULO (mesa de altar + painel ogival + misula que continua carregando a nervura)"""
    W = PIL_HW
    if altar:
        altar_retable(mb, F, s, top, mi or mb)
        if area:
            fcol(area, F, s - W - 0.3, s + W + 0.3, 0.0, PIL_D + 0.3, -0.5, top)
        return
    fblock(mb, F, s - W - 0.35, s + W + 0.35, -0.2, PIL_D + 0.45, -0.1, 0.7, OB, 0.1)
    fplinth(mb, F, s - W - 0.35, s + W + 0.35, PIL_D + 0.45, 0.7, 1.0, 0.25, OB)
    fblock(mb, F, s - W, s + W, -0.2, PIL_D, 1.0, top - 1.3, CS, 0.1)
    for sc in ((s - 0.54, s + 0.54) if twin else (s,)):
        colonette(mb, F, sc, PIL_D + 0.08, 1.0, top - 1.3, COL_R * (0.78 if twin else 1.0))
    fledge(mb, F, s - W - 0.3, s + W + 0.3, [(-0.2, top - 1.3), (PIL_D + 0.3, top - 1.3), (PIL_D + 0.62, top - 0.62),
                                             (PIL_D + 0.66, top - 0.36), (PIL_D + 0.66, top), (-0.2, top)], TRL)
    if area:
        fcol(area, F, s - W - 0.3, s + W + 0.3, 0.0, PIL_D + 0.3, -0.5, top)


def altar_retable(mb, F, s, top, mi):
    """RETABULO da R3 (09.10: 'altar'): mesa de altar de obsidiana com tampo moldurado e frontal com runa acesa baixa,
    2 velas do kit, painel ogival navy em moldura de remate e MISULA no alto (a nervura continua nascendo dela)"""
    fblock(mb, F, s - 2.6, s + 2.6, -0.2, 1.2, -0.1, 0.45, OB, 0.1)                       # degrau
    fblock(mb, F, s - 2.2, s + 2.2, -0.2, 1.05, 0.45, 2.75, OB, 0.1)                      # corpo da mesa
    fledge(mb, F, s - 2.5, s + 2.5, [(-0.2, 2.75), (1.2, 2.75), (1.38, 2.9), (1.38, 3.1), (-0.2, 3.1)], TRL)  # tampo
    fblock(mb, F, s - 1.45, s + 1.45, 1.0, 1.1, 0.95, 2.35, VA, 0.04)                     # frontal rebaixado
    rune(mb, F.v(s, 1.1, 1.65), F.u(), UPZ, F.n(), 4, 1.25, VD, 0.04)
    for sc in (s - 1.7, s + 1.7):
        p = F.v(sc, 0.55, 3.1)
        HA.candle(mi, p.x, p.y, p.z, 0.62, 1.1, dish=True)
    # painel ogival (retabulo) + moldura
    arch_panel(mb, F, s, 2.0, 2.4, 7.6, 3.1, 0.0, 0.18, VA, n=6)
    ogee_band(mb, F, s, 2.0, 2.4, 7.6, 0.42, 0.0, 0.5, TRL)
    for sc in (s - 2.21, s + 2.21):
        fblock(mb, F, sc - 0.21, sc + 0.21, 0.0, 0.5, 3.1, 7.6, TRL, 0.06)
    # misula que carrega a nervura (no lugar do capitel da pilastra)
    hull(mb, [F.v(ss, d, h) for ss in (s - 1.2, s + 1.2) for d, h in
              ((-0.2, top - 2.6), (0.3, top - 2.6), (PIL_D + 0.66, top - 0.4), (PIL_D + 0.66, top), (-0.2, top))], TRL)


def corner_col(mb, F, s, sgn, top, area=None):
    """coluna de canto: soco em talude, massa chanfrada e colunelo de 3/4 no canto interno, capitel moldurado"""
    a, b = sorted((s, s + sgn * 2.4))
    a2, b2 = sorted((s, s + sgn * 2.75))
    fblock(mb, F, a2, b2, -0.2, 2.75, -0.1, 0.7, OB, 0.1)
    fblock(mb, F, a, b, -0.2, 2.4, 0.7, top - 1.3, CS, 0.1)
    colonette(mb, F, s + sgn * 2.4, 2.4, 0.7, top - 1.3, 0.5)
    ca, cb = sorted((s, s + sgn * 3.0))
    fledge(mb, F, ca, cb, [(-0.2, top - 1.3), (2.4, top - 1.3), (3.0, top - 0.5), (3.0, top), (-0.2, top)], TRL)
    if area:
        fcol(area, F, a2, b2, 0.0, 2.7, -0.5, top)


def ogee_band(mb, F, cs, hw, rise, spring, t, d0, d1, m, n=6):
    """arquivolta (so o arco, do arranque ao fecho) de espessura radial t"""
    band(mb, F, ogive(cs, hw, rise, spring, n), ogive(cs, hw + t, rise + t, spring, n), d0, d1, m)


def skirting(mb, F, s0, s1):
    """soco corrido da parede (obsidiana em talude): a parede nasce do piso, nao de um rodape-caixa"""
    if s1 - s0 > 0.3:
        fledge(mb, F, s0, s1, [(-0.1, -0.1), (0.42, -0.1), (0.42, 0.5), (0.2, 0.78), (-0.1, 0.78)], OB)


def grille(mb, mi, F, cs, h0, h1, hw):
    """GRELHA de ferro (R2): soleira e verga de remate, 5 barras redondas e 2 travessas chatas, chumbadas na pedra"""
    fblock(mb, F, cs - hw - 0.35, cs + hw + 0.35, 0.0, 0.5, h0 - 0.35, h0, TRL, 0.06)
    fblock(mb, F, cs - hw - 0.35, cs + hw + 0.35, 0.0, 0.5, h1, h1 + 0.35, TRL, 0.06)
    for i in range(5):
        p = F.v(cs - hw + 2 * hw * (i + 0.5) / 5, 0.28, 0.0)
        mi.rod((p.x, p.y, p.z + h0 - 0.1), (p.x, p.y, p.z + h1 + 0.1), 0.075, BI, 6)
    for hh in (h0 + (h1 - h0) * 0.3, h0 + (h1 - h0) * 0.72):
        fblock(mi, F, cs - hw - 0.05, cs + hw + 0.05, 0.18, 0.4, hh - 0.09, hh + 0.09, BI, 0.0)


def shoring(mb, F, cs, hw, spring):
    """ESCORA de madeira de mina (R2): 2 esteios, chapeu com cunhas, 2 maos-francesas e grampos de ferro, encostada
    na arcada cega (so visual, a menos de 1,3 da parede)"""
    hp = 0.28
    zt = spring + 0.35
    for sg in (-1, 1):
        sp = cs + sg * (hw + 0.2)
        fblock(mb, F, sp - hp, sp + hp, 0.6, 1.16, -0.02, zt, WD, 0.0)
        fblock(mb, F, sp - hp - 0.06, sp + hp + 0.06, 0.56, 1.2, zt - 1.05, zt - 0.85, BI, 0.0)        # grampo
        a = F.v(sp - sg * 0.2, 0.88, zt - 1.7)
        b = F.v(sp - sg * 1.5, 0.88, zt - 0.15)
        mb.beam(a, b, 0.34, 0.34, WD, 0.05)
    fblock(mb, F, cs - hw - 0.75, cs + hw + 0.75, 0.55, 1.21, zt, zt + 0.62, WD, 0.0)                 # chapeu
    for sg in (-1, 1):                                                                              # cunhas
        fblock(mb, F, cs + sg * (hw * 0.5) - 0.35, cs + sg * (hw * 0.5) + 0.35, 0.6, 1.15, zt + 0.62, zt + 0.84,
               WD, 0.0)


def _arch_geo(s0, s1, spring):
    """(meia-largura, flecha, arranque) da arcada cega: a ogiva mantem a proporcao e o ARRANQUE desce se preciso para
    a chave ficar 0,1 abaixo da cornija (nada atravessa a cornija)"""
    hw = (s1 - s0) / 2.0 - 0.8
    rise = min(hw * 1.15, 5.2)
    return hw, rise, min(spring, R_SPR - 0.88 - 1.02 - rise)


def blind_arch(mb, F, s0, s1, spring=7.0, twin=False, room="R1", mi=None, skirt=True):
    """arcada CEGA (09.10): campo navy rebaixado, ombreiras de cantaria, impostas de remate, arquivolta de 2 ORDENS
    (a interna em cantaria, a externa em remate) com chave; twin = arcada dupla sobre colunelo central.
    R2: grelha de ferro nos arcos da arcada dupla e escoras de mina nos arcos simples."""
    mi = mi or mb
    if skirt:
        skirting(mb, F, s0, s1)
    if twin:
        mid = (s0 + s1) / 2.0
        blind_arch(mb, F, s0, mid + 0.35, spring, False, room + "_twin", mi, False)
        blind_arch(mb, F, mid - 0.35, s1, spring, False, room + "_twin", mi, False)
        colonette(mb, F, mid, 0.45, 0.78, _arch_geo(s0, mid + 0.35, spring)[2], 0.34)
        return
    cs = (s0 + s1) / 2.0
    hw, rise, spring = _arch_geo(s0, s1, spring)
    if hw < 1.2:
        return
    arch_panel(mb, F, cs, hw, rise, spring, 0.78, 0.0, 0.12, VA, 5)
    for sg in (-1, 1):
        a, b = sorted((cs + sg * hw, cs + sg * (hw + 0.42)))
        fblock(mb, F, a, b, -0.1, 0.34, 0.78, spring - 0.34, CS, 0.0)                     # ombreira (recuada)
        a, b = sorted((cs + sg * (hw - 0.06), cs + sg * (hw + 0.62)))
        fledge(mb, F, a, b, [(-0.1, spring - 0.34), (0.42, spring - 0.34), (0.56, spring - 0.12), (0.56, spring),
                             (-0.1, spring)], TRL)                                          # imposta
    ogee_band(mb, F, cs, hw, rise, spring, 0.4, -0.1, 0.34, CS, 5)
    ogee_band(mb, F, cs, hw + 0.4, rise + 0.4, spring, 0.42, -0.1, 0.52, TRL, 5)
    kz = spring + rise + 0.4
    fblock(mb, F, cs - 0.34, cs + 0.34, -0.1, 0.62, kz - 0.25, kz + 0.62, TRL, 0.0)        # chave
    if room == "R2_twin":
        grille(mb, mi, F, cs, 1.7, spring - 0.9, min(1.5, hw - 0.5))
    elif room == "R2":
        shoring(mi, F, cs, hw, spring)


def cornice(mb, F, s0, s1, h):
    """cornija de remate com perfil (face, gola e aba), no arranque da abobada"""
    if s1 - s0 > 0.3:
        fledge(mb, F, s0, s1, [(-0.1, h - 0.78), (0.22, h - 0.78), (0.62, h - 0.3), (0.72, h - 0.3), (0.72, h),
                               (-0.1, h)], TRL)


def torch(mb, F, s, d, h, twin=False):
    """tocha de FERRO (09.11/12.09): BRACADEIRA em volta do colunelo (ou chapa entre os colunelos duplos), braco com
    argola, cabo de madeira inclinado, cesto de 4 hastes curvas com trapo escuro e chama PEQUENA em gota (so ela
    emite). d = face da frente do colunelo; h = altura da chama"""
    n, u = F.n(), F.u()
    cc = F.v(s, PIL_D + 0.08, 0.0)
    zc = F.p(s, 0, h - 1.75)[2]
    if twin:
        p = F.v(s, PIL_D, h - 1.75)
        obox3(mb, p + n * 0.05, u, n, UPZ, 0.34, 0.1, 0.9, BI)
        root = p + n * 0.1
    else:
        EM._lathe(mb, (cc.x, cc.y, zc - 0.14), [(COL_R + 0.06, 0.0), (COL_R + 0.06, 0.28)], BI, 8, math.pi / 8)
        root = Vector((cc.x, cc.y, zc)) + n * (COL_R + 0.06)
    tip = root + n * 0.55 + UPZ * 0.28
    obox3(mb, (root + tip) / 2, (tip - root).normalized(), u, (tip - root).normalized().cross(u).normalized(),
          (tip - root).length + 0.06, 0.13, 0.13, BI)
    ax = (UPZ * 0.94 + n * 0.34).normalized()                                            # tocha inclinada para fora
    ring_c = tip + n * 0.14
    EM._lathe(mb, (ring_c.x, ring_c.y, ring_c.z - 0.09), [(0.19, 0.0), (0.19, 0.18)], BI, 8, 0.0, caps=(False, False))
    bot = ring_c - ax * 0.75
    lathe_ax(mb, bot, ax, [(0.07, 0.0), (0.12, 0.95), (0.14, 1.3)], WD, 6)
    top = bot + ax * 1.3
    lathe_ax(mb, top - ax * 0.05, ax, [(0.13, 0.0), (0.2, 0.12), (0.23, 0.3), (0.16, 0.42)], "Cloth_SG_Navy", 6)
    e1 = ax.cross(u).normalized()
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        rv = (u * math.cos(a) + e1 * math.sin(a))
        pts = [top + ax * 0.02 + rv * 0.12, top + ax * 0.24 + rv * 0.31, top + ax * 0.54 + rv * 0.24]
        mb.tube(pts, 0.035, BI, 3)
    EM._lathe(mb, (top.x + ax.x * 0.36, top.y + ax.y * 0.36, top.z + ax.z * 0.36),
              [(0.0, 0.0), (0.13, 0.11), (0.085, 0.28), (0.0, 0.47)], GL, 6)


def link_frame(mb, F, cs, hw_open):
    """moldura do vao de ligacao 12 x 12: verga moldurada, timpano ogival navy, arquivolta com chave. Sem emblema
    (12.11/16.02: o emblema fica no fecho da boca)"""
    fledge(mb, F, cs - hw_open - 1.3, cs + hw_open + 1.3, [(-0.1, LINK_H), (0.7, LINK_H), (0.86, LINK_H + 0.22),
                                                           (0.86, LINK_H + 1.0), (0.6, LINK_H + 1.22),
                                                           (-0.1, LINK_H + 1.22)], TRL)
    th = hw_open + 0.6
    arch_panel(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.0, 0.15, VA)
    ogee_band(mb, F, cs, th, 5.0, LINK_H + 1.2, 0.72, -0.1, 0.62, TRL)
    kz = LINK_H + 1.2 + 5.0 + 0.72
    fblock(mb, F, cs - 0.45, cs + 0.45, -0.1, 0.78, kz - 0.4, kz + 0.7, TRL, 0.06)


def tile_floor(mb, rect, z, margin=1.0, friso=0.8, gap=0.25, skip=None):
    """piso (09.10): lajes em 2 TAMANHOS - fiadas de lajes grandes 4 x 4 e, a cada 2, uma fiada de meias lajes
    4 x 2 desencontradas (junta que aparece mostra a base clara); friso de remate junto as paredes"""
    x0, y0, x1, y1 = rect
    mb.box2((x0, y0, z - 0.6), (x1, y1, z - 0.15), BL, 0.0)

    def ringbox(a, b, m):
        ax0, ay0, ax1, ay1 = x0 + a, y0 + a, x1 - a, y1 - a
        bx0, by0, bx1, by1 = x0 + b, y0 + b, x1 - b, y1 - b
        mb.box2((ax0, ay0, z - 0.4), (ax1, by0, z), m, 0.0)
        mb.box2((ax0, by1, z - 0.4), (ax1, ay1, z), m, 0.0)
        mb.box2((ax0, by0, z - 0.4), (bx0, by1, z), m, 0.0)
        mb.box2((bx1, by0, z - 0.4), (ax1, by1, z), m, 0.0)
    ringbox(0.0, margin, FL)
    ringbox(margin, margin + friso, TRL)
    ix0, iy0, ix1, iy1 = x0 + margin + friso, y0 + margin + friso, x1 - margin - friso, y1 - margin - friso
    pat = (4.0, 4.0, 2.0)
    rows, acc, k = [], 0.0, 0
    while acc < (iy1 - iy0) - 0.5:
        rows.append(pat[k % 3])
        acc += pat[k % 3]
        k += 1
    sc = (iy1 - iy0) / sum(rows)
    nx = max(1, int(round((ix1 - ix0) / 4.0)))
    tx = (ix1 - ix0) / nx
    yy = iy0
    for j, rh in enumerate(rows):
        ty = rh * sc
        off = 0.0 if rh > 3.0 else tx / 2.0
        cuts = [ix0] + [ix0 + off + tx * i for i in range(nx + 1) if ix0 + 0.5 < ix0 + off + tx * i < ix1 - 0.5] + [ix1]
        for a, b in zip(cuts, cuts[1:]):
            if skip and skip((a + b) / 2, yy + ty / 2):
                continue
            mb.box2((a + gap / 2, yy + gap / 2, z - 0.4), (b - gap / 2, yy + ty - gap / 2, z), FL, 0.0)
        yy += ty


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
    """berco ogival (arranque 'spring', fecho 'crown' acima de zf) ao longo de 'axis'; NERVURAS em perfil de PERA
    (redondo por baixo: 09.10) nas pilastras, nervuras de testa e cumeeira; chaves em ROSETA de torno"""
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
    def pear5(w, dep):                            # perfil em PERA de 5 pontos (redondo por baixo, leve)
        h = w / 2.0
        return [(-h, 0.12), (h, 0.12), (h * 0.82, -dep * 0.52), (0.0, -dep), (-h * 0.82, -dep * 0.52)]
    prof = pear5(0.9, 0.85)
    prof_w = pear5(0.7, 0.62)
    ue = [-hw + 0.3 + (2 * hw - 0.6) * (0.5 - 0.5 * math.cos(math.pi * k / 20)) for k in range(21)]

    def rib(a, pr):
        mb.sweep([(*mp(a, u), zz(u) - 0.02) for u in ue], pr, TRL)
    for a in ribs:
        rib(a, prof)
    rib(a0 + 0.4, prof_w)
    rib(a1 - 0.4, prof_w)
    mb.sweep([(*mp(a0 + 0.4, 0.0), zz(0.0) - 0.02), (*mp(a1 - 0.4, 0.0), zz(0.0) - 0.02)], prof, TRL)
    for a in ribs:
        x, y = mp(a, 0.0)
        EM._lathe(mb, (x, y, zz(0.0) - 0.9), [(0.0, -0.05), (0.36, 0.0), (0.78, 0.28), (1.02, 0.6), (0.9, 0.88)],
                  TRL, 8, math.pi / 8, caps=(False, True))


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


PORTAL_NV = 18                                   # aduelas do anel do portal das salas


def portal_frame(mb, c, u, v, n, r_in, r_out, floor_z):
    """moldura do portal das salas (09.12): ANEL DE ADUELAS de remate (juntas abertas sobre o aro escuro) com runas
    ENTALHADAS do alfabeto da ilha em aduelas alternadas (Neon escuro), coroa de cantaria, CHAVE esculpida saliente
    (degraus + voluta) e PES em consola sobre socos de obsidiana"""
    ring3(mb, c, u, v, n, r_in - 0.05, r_in + 0.9, -0.6, 0.3, OB)                        # aro escuro (juntas)
    ring3(mb, c, u, v, n, r_in + 0.9, r_out, -0.6, 0.35, CS)
    ch = 0.1
    for k in range(PORTAL_NV):
        a0 = math.pi / 2 + 2 * math.pi * (k - 0.5) / PORTAL_NV + 0.018
        a1 = math.pi / 2 + 2 * math.pi * (k + 0.5) / PORTAL_NV - 0.018
        if k == 0:
            continue                                                                    # a chave
        pts = []
        for a in (a0, (a0 + a1) / 2, a1):
            for r in (r_in, r_in + 0.95):
                pts.append(_pl(c, u, v, n, a, r, -0.55))
                pts.append(_pl(c, u, v, n, a, r, 0.72 - ch))
                rr = r + (ch if r < r_in + 0.5 else -ch)
                aa = a + (ch / r if a == a0 else (-ch / r if a == a1 else 0.0))
                pts.append(_pl(c, u, v, n, aa, rr, 0.72))
        hull(mb, pts, TRL)
        if k % 2 == 0 and k not in (PORTAL_NV // 2 - 1, PORTAL_NV // 2, PORTAL_NV // 2 + 1):
            am = (a0 + a1) / 2
            radial = u * math.cos(am) + v * math.sin(am)
            tang = u * -math.sin(am) + v * math.cos(am)
            rune(mb, c + radial * (r_in + 0.47) + n * 0.72, tang, radial, n, k // 2, 0.78, VD, 0.04, 0.12)
    # chave: pedra maior que sai do anel (frente em degraus) + voluta de remate em cima
    top = c + v * (r_in + 0.35)
    for w, hh, d1 in ((1.3, 2.2, 1.0), (0.9, 1.6, 1.3)):
        cbox(mb, top + v * (hh / 2) + n * ((d1 - 0.6) / 2), u, n, v, w, d1 + 0.6, hh, TRL, 0.1)
    lathe_ax(mb, top + v * 1.35 + n * 1.3, n, [(0.0, 0.0), (0.3, 0.02), (0.34, 0.14), (0.0, 0.24)], TRL, 8)
    # pes em consola: soco de obsidiana + consola de remate com o perfil que recebe o anel
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        hz = p.z + 0.4 - floor_z
        base = Vector((p.x, p.y, floor_z))
        cbox(mb, base + UPZ * 0.35, u, n, UPZ, 2.5, 2.3, 0.8, OB, 0.1)
        hull(mb, [base + u * (s_ * 1.0) + n * d + UPZ * z for s_ in (-1, 1) for d, z in
                  ((-0.9, 0.7), (0.9, 0.7), (1.05, hz * 0.55), (0.75, hz), (-0.9, hz))], TRL)


def chandelier(mb, x, y, h, top, r=3.0, n=8):
    """lustre de ferro (12.09): aro em tubo, bracos em S, balaustre de torno no centro, VELAS DO KIT (prato, vela
    creme, chama em gota) e haste presa na nervura por uma roseta de ferro"""
    mb.tube([(x + r * math.cos(2 * math.pi * k / 16), y + r * math.sin(2 * math.pi * k / 16), h) for k in range(17)],
            0.16, BI, 5)
    # balaustre ACIMA da luz da sala (a luz fica ~0,7 abaixo do aro: nada de ferro envolvendo o ponto de luz)
    EM._lathe(mb, (x, y, h - 0.3), [(0.0, 0.0), (0.3, 0.2), (0.42, 0.45), (0.2, 0.95), (0.3, 1.2), (0.12, 1.5),
                                    (0.12, 1.95)], BI, 6, caps=(False, True))
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + rr * ca, y + rr * sa, h + zz) for rr, zz in ((0.3, 0.9), (1.2, 0.2), (2.2, 0.55), (r, 0.12))]
        mb.tube(pts, 0.08, BI, 4)
        HA.candle(mb, x + r * ca, y + r * sa, h + 0.1, 0.8, 1.3, dish=True)
    mb.rod((x, y, h + 1.6), (x, y, top - 0.2), 0.11, BI, 6)
    EM._lathe(mb, (x, y, top - 0.55), [(0.12, 0.0), (0.62, 0.35), (0.66, 0.5), (0.0, 0.58)], BI, 6, caps=(True, False))


# ==================================================================== PORTARIA = BOCA DE CAVERNA (superficie)
# ------------------------------------------------------------------ OVERHAUL 09.08: CRISTAIS com facetas de verdade
def _frame3(d):
    d = Vector(d).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = d.cross(ref).normalized()
    return d, e1, d.cross(e1).normalized()


def crystal_hex(mb, base, dirv, h, r, ph=0.0, body=CSH, tip=CGL):
    """COLUNA de cristal: prisma hexagonal levemente conico (casca escura, sem brilho) que nasce 0,6 dentro do calo
    e TERMINACAO de 6 facetas com o apice deslocado (so a ponta e Neon: 09.08)"""
    d, e1, e2 = _frame3(dirv)
    b = Vector(base) - d * 0.6
    hb = h * 0.7 + 0.6

    def ring(o, rr):
        return [o + (e1 * math.cos(ph + k * math.pi / 3) + e2 * math.sin(ph + k * math.pi / 3)) * rr for k in range(6)]
    r1 = ring(b + d * hb, r * 0.86)
    hull(mb, ring(b, r) + r1, body)
    hull(mb, r1 + [b + d * (hb + h * 0.3) + (e1 * math.cos(ph) + e2 * math.sin(ph)) * (r * 0.22)], tip)


def crystal_boss(mb, base, dirv, R, m):
    """CALO de rocha de onde o aglomerado brota (casco dirigido, afunda na parede): nada solto"""
    d, e1, e2 = _frame3(dirv)
    b = Vector(base)
    pts = []
    for k in range(7):
        a = 2 * math.pi * k / 7
        rr = R * (1.0 + 0.22 * math.sin(k * 2.1 + 0.4))
        pts.append(b - d * 0.25 + (e1 * math.cos(a) + e2 * math.sin(a)) * rr)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.5
        rr = R * 0.55 * (1.0 + 0.2 * math.cos(k * 1.7))
        pts.append(b + d * (0.32 * R) + (e1 * math.cos(a) + e2 * math.sin(a)) * rr)
    pts.append(b - d * (0.9 * R))
    hull(mb, pts, m)


# aglomerado: (escala, abertura, azimute) das colunas menores em volta da maior (leque dirigido, assimetrico)
SPREAD = ((0.62, 0.5, 0.6), (0.46, 0.62, 2.6), (0.34, 0.55, 4.3), (0.28, 0.7, 5.4))


def cluster(mb, base, dirv, h, r, k, boss_m):
    d, e1, e2 = _frame3(dirv)
    crystal_boss(mb, base, d, r * 2.2, boss_m)
    crystal_hex(mb, base, d, h, r, 0.3)
    for i, (sc, a, az) in enumerate(SPREAD[:max(0, k - 1)]):
        off = e1 * math.cos(az) + e2 * math.sin(az)
        dd = (d + off * a).normalized()
        crystal_hex(mb, Vector(base) + off * (r * 1.2), dd, h * sc, r * sc * 1.1, 0.9 * i)


def crystal_pendant(mb, c, m=CGL):
    """o cristal da boca (VFX: gira no eixo z do pivot): biterminado hexagonal, facetas de verdade, ponta de cima
    entra no capuz de prata"""
    EM._lathe(mb, (c.x, c.y, c.z), [(0.0, -1.75), (0.6, -0.9), (0.7, 0.55), (0.6, 1.15), (0.0, 2.08)], m, 6)


# ------------------------------------------------------------------ OVERHAUL 09.01: MASSA DE ROCHA FRATURADA
# a massa deixa de ser a mesma planta empilhada ("pilha de pneus"): BANCOS GROSSOS (duro) e finos (mole) nas juntas
# globais com mergulho; cada banco e cortado por DIACLASES VERTICAIS de rumo unico na massa inteira (fendas abertas de
# ~0,5) em prismas que escorregam 0,3..0,8 ao longo da fenda e sobem/descem um pouco (blocos deslocados); planta
# diferente a cada banco (nao so escala); banco duro com LABIO saliente e topo chanfrado; faces de fenda escuras.
JOINT_A = math.radians(34.0)                     # rumo das diaclases (o mesmo em toda a massa)
JT = (math.cos(JOINT_A), math.sin(JOINT_A))      # ao longo da fenda
JN = (-math.sin(JOINT_A), math.cos(JOINT_A))     # normal da fenda
JOINT_S, JOINT_O, JOINT_GAP = 9.2, 2.6, 0.26     # passo, fase global, meia-abertura
BENCH_T = (6.4, 2.6, 7.6, 3.6, 5.8, 2.4, 8.2, 3.4, 6.8, 3.0, 7.2, 2.8)
BENCH_Z0 = -6.0


def _bench_bounds(z0, z1):
    """bancos [za, zb, duro] entre z0 e z1 cortados nas juntas GLOBAIS; sobra fina (< 1,6) junta no vizinho"""
    out = []
    z, i = BENCH_Z0, 0
    while z < z1 and i < 400:
        t = BENCH_T[i % len(BENCH_T)]
        a, b = max(z, z0), min(z + t, z1)
        if b - a > 0.02:
            out.append([a, b, i % 2 == 0])
        z += t
        i += 1
    merged = []
    for s in out:
        if merged and (s[1] - s[0] < 1.6 or merged[-1][1] - merged[-1][0] < 1.6):
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def _dip(x, y):
    return STRATA_DIP[0] * (x - 100.0) + STRATA_DIP[1] * (y - 80.0)


def _clip2(poly, n, c):
    """poligono convexo 2D recortado pelo semiplano n.p <= c"""
    out = []
    k = len(poly)
    for i in range(k):
        a, b = poly[i], poly[(i + 1) % k]
        da = n[0] * a[0] + n[1] * a[1] - c
        db = n[0] * b[0] + n[1] * b[1] - c
        if da <= 0:
            out.append(a)
        if (da < 0 < db) or (db < 0 < da):
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _area2(p):
    return 0.5 * abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))))


def rock_mass(mb, box, rng, idx, taper=0.8, n=9):
    """bloco de ROCHA NATURAL fraturada dentro da caixa (x0, x1, y0, y1, z0, z1)"""
    x0, x1, y0, y1, z0, z1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    ph = rng.uniform(0.0, 2 * math.pi / n)
    shape = []
    for k in range(n):
        a = ph + 2 * math.pi * k / n + rng.uniform(-0.14, 0.14)
        ca, sa = math.cos(a), math.sin(a)
        f = rng.uniform(0.9, 1.0)
        shape.append((math.copysign(abs(ca) ** 0.7, ca) * f, math.copysign(abs(sa) ** 0.7, sa) * f))
    dv = Vector((MASS_C[0] - cx, MASS_C[1] - cy))
    dv = dv.normalized() if dv.length > 1e-3 else Vector((0.0, 0.0))
    benches = _bench_bounds(z0, z1)
    H = max(0.1, z1 - z0)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pj = [JN[0] * x + JN[1] * y for x, y in corners]
    k0, k1 = int(math.floor((min(pj) - JOINT_O) / JOINT_S)), int(math.ceil((max(pj) - JOINT_O) / JOINT_S))
    cuts = [JOINT_O + k * JOINT_S for k in range(k0, k1 + 1) if min(pj) + 2.4 < JOINT_O + k * JOINT_S < max(pj) - 2.4]
    gi, ti, di = mb._mi_for("Grass_SG"), mb._mi_for(RKT), mb._mi_for(RKD)
    jn3 = Vector((JN[0], JN[1], 0.0))
    prev = []                                    # plantas do banco de baixo: bloco sem apoio nao entra (flutuante)
    for li, (za, zb, hard) in enumerate(benches):
        cur = []
        top = li == len(benches) - 1
        t = ((za + zb) / 2 - z0) / H
        s = 1.0 - (1.0 - taper) * t ** 1.15
        if not hard:
            s *= 0.9
        off = dv * ((1.0 - s) * min(hx, hy) * 0.85)
        ex = 1.04 if li % 2 == 0 else 0.95                                  # planta muda de banco para banco
        poly = []
        for k, (u, v) in enumerate(shape):
            wv = 1.0 + 0.09 * math.sin(k * 2.3 + li * 1.7)
            poly.append((cx + off.x + u * hx * s * wv * ex, cy + off.y + v * hy * s * wv * (2.0 - ex)))
        pieces = [poly]
        for c in cuts:
            nxt = []
            for P in pieces:
                for Q in (_clip2(P, JN, c - JOINT_GAP), _clip2(P, (-JN[0], -JN[1]), -(c + JOINT_GAP))):
                    if len(Q) >= 3 and _area2(Q) > 1.2:
                        nxt.append(Q)
            pieces = nxt
        for pi, P in enumerate(pieces):
            f = (idx * 0.37 + pi * 0.618 + li * 0.29) % 1.0
            slip = (0.3 + 0.5 * f) * (1.0 if (pi + li) % 2 else -1.0)
            P = [(px + JT[0] * slip, py + JT[1] * slip) for px, py in P]
            dz = (0.45, 0.15, 0.0)[(pi + li + idx) % 3] if not top else -0.2 * ((pi + idx) % 2)
            zt = min(zb + dz, z1)
            gx = sum(p[0] for p in P) / len(P)
            gy = sum(p[1] for p in P) / len(P)
            if li > 0 and not any(fm_lib.point_in_poly(gx, gy, Q) for Q in prev):
                continue
            cur.append(P)
            ch = min(0.75, (zt - za) * 0.2)
            if hard and (li + pi + idx) % 3 == 0:
                rings = ((za, 0.95), (zt - ch, 1.03), (zt, 0.92))          # LABIO saliente quebrado (1 em 3)
            elif hard:
                rings = ((za, 0.98), (zt - ch * 0.5, 1.0), (zt, 0.95))     # face quase a prumo, aresta viva
            else:
                rings = ((za, 1.0), (zt - ch * 0.4, 0.99), (zt, 0.96))
            vs = []
            for ri, (zz, sc) in enumerate(rings):
                for vi, (px, py) in enumerate(P):
                    # plano de fratura: cada vertice recua um pouco diferente por anel (dirigido, sem sorteio)
                    sc2 = sc * (1.0 - 0.05 * ri * (0.5 + 0.5 * math.sin(vi * 2.3 + li * 1.3 + pi * 0.7)))
                    qx = min(max(gx + (px - gx) * sc2, x0), x1)
                    qy = min(max(gy + (py - gy) * sc2, y0), y1)
                    vs.append(Vector((qx, qy, P3 + zz + _dip(qx, qy))))
            faces = hull(mb, vs, ROCK if hard else RKD)
            for fc in faces:
                nz = fc.normal.z
                if nz > 0.97:
                    fc.material_index = gi if (top and zb > 6.0) else ti
                elif abs(fc.normal.dot(jn3)) > 0.93:
                    fc.material_index = di                                  # parede da fenda: sombra
        prev = cur


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
        rock_mass(mb, c[:6], random.Random(7100 + i), i, taper=0.95 if i < 8 else (0.78 if c[5] - c[4] > 16.0 else 0.88))
    for i, (x, y, rx, ry, z0, z1) in enumerate(SPIRES):
        rock_mass(mb, (x - rx, x + rx, y - ry, y + ry, z0, z1), random.Random(7300 + i), 30 + i, taper=0.4, n=7)
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
UPV = Vector((0.0, 0.0, 1.0))


def ring8(x, y, hw, c, z):
    return [Vector((px, py, z)) for px, py in CA.sq_ch(x, y, hw, c)]


def place(pts, xy, rot, floor=P3 + 0.13, sink=0.1):
    """pontos locais girados (Euler) e POUSADOS no piso: o ponto mais baixo fica 'sink' abaixo de 'floor'"""
    from mathutils import Euler
    R = Euler(rot).to_matrix()
    q = [R @ Vector(p) for p in pts]
    low = min(p.z for p in q)
    return [Vector((xy[0] + p.x, xy[1] + p.y, floor - sink - low + p.z)) for p in q]


def pillar(mb, x, y, broken=False):
    """pilar da ordem (09.05): base MOLDURADA (plinto chanfrado, talude, filete violeta), fuste OCTOGONAL (quinas
    chanfradas) em fiadas navy, cintas finas de obsidiana com PINGADEIRA, capitel com 4 MISULAS e cornija, remate =
    PINACULO do kit do castelo (sem piramide de 4 lados). broken = o pilar LESTE partiu (fratura em cunha, dirigida)."""
    cbox(mb, (x, y, P3 + 0.4), (1, 0, 0), (0, 1, 0), UPV, 4.2, 4.2, 1.4, OB, 0.1)
    hull(mb, ring8(x, y, 2.05, 0.5, P3 + 1.1) + ring8(x, y, 1.8, 0.45, P3 + 1.45), OB)
    hull(mb, ring8(x, y, 1.86, 0.46, P3 + 1.45) + ring8(x, y, 1.86, 0.46, P3 + 1.62), VS)
    top_h = PIL_BREAK if broken else PIL_H - 2.6
    h, k = 1.62, 0
    CH = (2.5, 2.1, 2.3)
    while h < top_h - 0.05:
        if k % 3 == 2 and top_h - h > 1.0:
            hull(mb, ring8(x, y, 1.66, 0.43, P3 + h) + ring8(x, y, 1.76, 0.45, P3 + h + 0.07) +
                 ring8(x, y, 1.76, 0.45, P3 + h + 0.22) + ring8(x, y, 1.6, 0.42, P3 + h + 0.4), OB)
            h += 0.4
            k += 1
            continue
        ch_ = min(CH[k % 3], top_h - h)
        mb.prism(SL.ccw(CA.sq_ch(x, y, 1.6, 0.42)), P3 + h, P3 + h + ch_, VA, 0.07)
        h += ch_
        k += 1
    if broken:
        # fratura em CUNHA: a fiada partida desce de oeste (alta) para leste (baixa), com uma lasca presa no canto NO
        bot = ring8(x, y, 1.6, 0.42, P3 + h)
        topr = [Vector((p.x, p.y, P3 + h + 1.25 + 0.5 * (x - p.x) / 1.6 + 0.2 * (p.y - y) / 1.6)) for p in bot]
        hull(mb, bot + topr, VA)
        zt = P3 + h + 1.25
        hull(mb, [Vector((x - 1.6, y + 0.1, zt + 0.35)), Vector((x - 0.5, y + 1.6, zt + 0.2)),
                  Vector((x - 1.55, y + 1.55, zt + 0.25)), Vector((x - 0.9, y + 0.5, zt + 0.1)),
                  Vector((x - 1.45, y + 1.2, zt + 1.05)), Vector((x - 1.2, y + 0.9, zt + 0.95))], VA)
        col_box2("SG_DunApproach", (x - 2.1, y - 2.1, P3 - 0.3), (x + 2.1, y + 2.1, P3 + h + 1.25))
        return P3 + h
    zc = P3 + h
    for a in (0.0, math.pi / 2, math.pi, 1.5 * math.pi):                     # 4 misulas sob o capitel
        n, t = Vector((math.cos(a), math.sin(a), 0.0)), Vector((-math.sin(a), math.cos(a), 0.0))
        c = Vector((x, y, 0.0))
        prof = [(1.5, zc - 1.2), (1.5, zc + 0.02), (2.0, zc + 0.02), (1.96, zc - 0.28), (1.72, zc - 0.78)]
        hull(mb, [c + n * r + t * w + UPV * z for r, z in prof for w in (-0.42, 0.42)], OB)
    hull(mb, ring8(x, y, 2.0, 0.5, zc) + ring8(x, y, 2.0, 0.5, zc + 0.7) + ring8(x, y, 2.26, 0.56, zc + 0.86) +
         ring8(x, y, 2.26, 0.56, zc + 1.08) + ring8(x, y, 2.02, 0.5, zc + 1.25), OB)
    CA.pinnacle(mb, x, y, zc + 1.25, s=1.0, hb=1.8, hn=4.0, body_m=VA, spire_m=NAVY, ring_m=SV, cap_m=OB)
    EM.banner(mb, mb, mb, mb, (x, y - 1.95, P3 + 19.6), -math.pi / 2, 3.0, 10.4, trim=GOLD)
    col_box2("SG_DunApproach", (x - 2.1, y - 2.1, P3 - 0.3), (x + 2.1, y + 2.1, P3 + PIL_H))
    return P3 + PIL_H


# o que caiu do lado LESTE (pilar partido + aduelas do arco externo): (tamanho, (x, y), rotacao, material) - o
# tamanho e o da COLISAO e da folga (_approach_check); a peca visual e a PECA de verdade (09.06)
RUBBLE = [((4.0, 4.0, 1.1), (119.7, 51.4), (0.16, -0.05, 0.52), OB),       # capitel do pilar, de lado
          ((3.2, 3.2, 2.5), (119.3, 57.0), (-0.1, 0.22, -0.3), VA),        # fiada do fuste
          ((2.3, 1.2, 1.6), (117.4, 48.6), (0.0, 0.12, 0.9), RUIN)]       # aduela do arco externo


def _oct_loc(hw, c, z):
    return [(px, py, z) for px, py in CA.sq_ch(0.0, 0.0, hw, c)]


def rubble(mb):
    """as PECAS do pilar e do arco no patio, todas com face de FRATURA (casco recortado), pousadas no piso"""
    # capitel: a cornija moldurada inteira de um lado, partida em diagonal do outro
    cap = _oct_loc(2.0, 0.5, -0.55) + _oct_loc(2.0, 0.5, 0.05) + _oct_loc(2.25, 0.56, 0.2) + \
        _oct_loc(2.25, 0.56, 0.42) + _oct_loc(2.02, 0.5, 0.55)
    cap = clip(cap, Vector((0.8, 0.35, 0.45)).normalized(), 1.45)
    # fiada do fuste: as 2 pontas quebradas (planos inclinados diferentes)
    sh = _oct_loc(1.6, 0.42, -1.25) + _oct_loc(1.6, 0.42, 1.25)
    sh = clip(sh, Vector((0.35, 0.2, 1.0)).normalized(), 0.85)
    sh = clip(sh, Vector((-0.25, 0.1, -1.0)).normalized(), 1.1)
    # aduela: cunha (intradorso 2,0 -> extradorso 2,5) com uma ponta partida
    vo = []
    for z in (-0.8, 0.8):
        vo += [(-1.0, -0.6, z), (1.0, -0.6, z), (1.25, 0.6, z), (-1.25, 0.6, z)]
    vo = clip(vo, Vector((1.0, 0.25, 0.3)).normalized(), 0.95)
    vo = clip(vo, Vector((-0.8, 0.5, -0.35)).normalized(), 0.85)                   # lasca do outro lado
    for (size, xy, rot, m), pts in zip(RUBBLE, (cap, sh, vo)):
        q = place(pts, xy, rot)
        hull(mb, q, m)
        top = max(p.z for p in q)
        col_box("SG_DunApproach", (size[0] * 0.9, size[1] * 0.9, top - P3 + 0.3), (xy[0], xy[1], (P3 + top) / 2 - 0.15),
                (0.0, 0.0, rot[2]))
    # 2 lascas (mesma queda): cascos dirigidos
    for pts, xy, rot, m in ((((-0.45, -0.3, -0.2), (0.4, -0.35, -0.25), (0.5, 0.3, -0.2), (-0.3, 0.35, -0.3),
                               (-0.2, -0.1, 0.3), (0.25, 0.1, 0.25)), (117.6, 52.9), (0.3, 0.1, 0.4), OB),
                            (((-0.55, -0.4, -0.3), (0.5, -0.35, -0.3), (0.55, 0.4, -0.25), (-0.45, 0.4, -0.35),
                              (-0.3, -0.2, 0.35), (0.35, 0.05, 0.3), (0.0, 0.3, 0.2)), (121.7, 54.4), (0.0, 0.25, 1.2),
                             VA)):
        hull(mb, place(pts, xy, rot), m)


def crystal_pedestal(mb, x, y, k):
    """MARCO de pedra da aproximacao (09.07, sem magia): plinto chanfrado e talude de obsidiana, fuste OCTOGONAL com
    leve entase, runa ENTALHADA (fundo violeta, o mesmo do obelisco), cinta de ferro onde as ARGOLAS prendem, capa
    moldurada e remate em BOLA com colar"""
    cbox(mb, (x, y, P3 + 0.12), (1, 0, 0), (0, 1, 0), UPV, 2.7, 2.7, 0.64, OB, 0.1)
    hull(mb, ring8(x, y, 1.2, 0.3, P3 + 0.44) + ring8(x, y, 1.0, 0.26, P3 + 0.7), OB)
    hull(mb, ring8(x, y, 0.95, 0.26, P3 + 0.7) + ring8(x, y, 0.97, 0.26, P3 + 1.8) + ring8(x, y, 0.9, 0.25, P3 + 3.3),
         VA)
    hull(mb, ring8(x, y, 1.03, 0.28, P3 + 2.6) + ring8(x, y, 1.03, 0.28, P3 + 2.9), BI)
    hull(mb, ring8(x, y, 0.9, 0.25, P3 + 3.3) + ring8(x, y, 1.2, 0.32, P3 + 3.48) + ring8(x, y, 1.2, 0.32, P3 + 3.62) +
         ring8(x, y, 1.0, 0.27, P3 + 3.72), OB)
    EM._lathe(mb, (x, y, P3 + 3.72), [(0.34, 0.0), (0.36, 0.08), (0.2, 0.2), (0.46, 0.5), (0.4, 0.75), (0.0, 0.95)],
              OB, 8, math.pi / 8)
    tx = -1.0 if x > HX else 1.0                                                  # face que olha o corredor
    rune(mb, (x + tx * 0.95, y, P3 + 1.75), (0.0, tx, 0.0), UPV, (tx, 0.0, 0.0), k, 1.15, m=VS, dep=0.05)
    col_box2("SG_DunApproach", (x - 1.35, y - 1.35, P3 - 0.3), (x + 1.35, y + 1.35, P3 + 4.6))


def vouss(F, cs, sg, cin, cout, f0, f1, d0, d1, spring, ch=0.1, lean=0.0, dz=0.0):
    """pontos de uma ADUELA em cunha entre as fracoes f0..f1 do intradorso 'cin' e do extradorso 'cout'
    (ogive_right), da face de tras d0 a frente d1 com chanfro; lean = a pedra tomba para fora no extradorso"""
    prof = [(_arc_at(cin, f)[0], 0) for f in (f0, (f0 + f1) / 2, f1)] + \
           [(_arc_at(cout, f)[0], 1) for f in (f0, (f0 + f1) / 2, f1)]
    gu = sum(p[0][0] for p in prof) / 6.0
    gv = sum(p[0][1] for p in prof) / 6.0
    pts = []
    for (u, v), side in prof:
        dl = lean * side
        g = Vector((gu - u, gv - v))
        g = g.normalized() * (ch * 1.3) if g.length > 1e-6 else g
        for d in (d0, d1 - ch):
            pts.append(F.v(cs + sg * u, d + dl, spring + v + dz))
        pts.append(F.v(cs + sg * (u + g.x), d1 + dl, spring + v + g.y + dz))
    return pts


JAMB_BREAK = {(-1, 3): 0.45, (1, 2): 0.4, (1, 3): 0.7, (1, 4): 0.5}     # (lado, fiada) -> quina quebrada (ruina)


def cave_mouth():
    """BOCA = RUINA ANTIGA encaixada na rocha (OVERHAUL 09.02/09.04): ombreiras de CANTARIA no valor da rocha (um tom
    acima), blocos chanfrados com quinas QUEBRADAS nas fiadas altas (o lado leste mais arruinado), runas ENTALHADAS do
    alfabeto da ilha, imposta de obsidiana com pingadeira, arco ogival de ADUELAS em cunha de pedra violeta (uma
    escorregou) sobre nucleo escuro, ARCO EXTERNO de cantaria PARTIDO a leste (pedra fraturada, as outras no patio),
    fecho de obsidiana com o emblema. Por fora nada brilha; a magia comeca NA boca (cristal pendurado)."""
    mb = MB("SG_Dun_Cave_Mouth", "17_DUNGEON", random.Random(731), detail="near")
    F = Face(True, HY0, -1, P3)
    up = UPV
    # 1. ombreiras em fiadas (mesmo envelope/colisao de antes)
    COURSES = (2.4, 2.0, 2.6, 2.2, 2.3)
    for sg in (-1, 1):
        h, k = -0.3, 0
        while h < M_SPR - 1.05:
            ch = min(COURSES[k % len(COURSES)], M_SPR - 1.0 - h)
            ex = 0.0 if k % 2 == 0 else 0.3
            rc = 0.0 if k % 2 == 0 else 0.1
            s0, s1 = sorted((HX + sg * (M_HW - 0.1 + rc), HX + sg * (M_HW + M_T + 0.2 - ex)))
            bk = JAMB_BREAK.get((sg, k))
            cuts = [((sg, 1.0, 1.0), bk)] if bk else []
            if sg > 0 and k == 1:
                cuts.append(((-1.0, 1.0, -0.6), 0.3))                              # lasca no pe da face do vao
            fblock(mb, F, s0, s1, -0.3, M_DEP - rc, h, h + ch, RUIN, 0.1, cuts)
            if k in (1, 2):
                rune(mb, F.v(HX + sg * (M_HW + M_T / 2 + 0.1), M_DEP - rc, h + ch / 2), F.u(), up, F.n(),
                     2 * (k - 1) + (0 if sg < 0 else 1), 1.35, OB, 0.05)
            if k == 2:                                                            # liquen no topo exposto da fiada
                so = HX + sg * (M_HW + M_T + 0.2)
                hull(mb, [F.v(so - sg * a, d, h + ch + z) for a, d, z in
                          ((0.0, -0.1, 0.0), (0.32, -0.1, 0.0), (0.0, M_DEP - 0.3, 0.0), (0.3, M_DEP - 0.2, 0.0),
                           (0.05, 0.4, 0.09), (0.25, 1.6, 0.08), (0.0, 2.6, 0.02))], "Grass_SG")
            h += ch
            k += 1
        s0, s1 = sorted((HX + sg * (M_HW - 0.5), HX + sg * (M_HW + M_T + 1.3)))
        fledge(mb, F, s0, s1, [(-0.3, M_SPR - 1.0), (M_DEP + 0.2, M_SPR - 1.0), (M_DEP + 0.45, M_SPR - 0.72),
                               (M_DEP + 0.45, M_SPR - 0.05), (M_DEP + 0.28, M_SPR + 0.2), (-0.3, M_SPR + 0.2)], OB)
        s0, s1 = sorted((HX + sg * (M_HW + M_T + 0.2), HX + sg * (M_HW + M_T + 1.1)))
        fblock(mb, F, s0, s1, -0.3, M_DEP - 0.4, -0.3, M_SPR - 1.0, OB, 0.1)          # contraforte escuro
    # 2. nucleo escuro + ADUELAS em cunha (juntas abertas mostram o nucleo)
    arch_band(mb, F, HX, M_HW + 0.15, M_RISE + 0.15, M_SPR, M_SPR, M_T - 0.5, -0.2, M_DEP - 0.25, OB, n=14)
    cin = ogive_right(M_HW, M_RISE, 60)
    NV = 7
    for sg in (-1, 1):
        for k in range(NV):
            rad = M_T * (1.0 if k % 2 == 0 else 1.1)
            cout = ogive_right(M_HW + rad, M_RISE + rad * 0.9, 60)
            f0, f1 = 0.9 * k / NV + 0.006, 0.9 * (k + 1) / NV - 0.006
            slip = sg > 0 and k == 4
            pts = vouss(F, HX, sg, cin, cout, f0, f1, -0.3, M_DEP - 0.05, M_SPR, 0.1,
                        lean=0.28 if slip else 0.0, dz=-0.07 if slip else 0.0)
            if sg > 0 and k == 5:
                (u, v), _ = _arc_at(cout, f1)
                pn = (F.u() * sg * 0.6 + up * 0.5 + F.n() * 0.8).normalized()
                pts = clip(pts, pn, pn.dot(F.v(HX + sg * u, M_DEP - 0.05, M_SPR + v)) - 0.55)
            hull(mb, pts, VS)
    # 3. ARCO EXTERNO de cantaria (ruina): inteiro a oeste, PARTIDO a leste (a pedra que ficou esta fraturada)
    hw_h, rs_h, t_h = M_HW + M_T / 2 + 1.76 + 0.55, M_RISE + M_T * 0.45 + 1.76 + 0.55, 1.1
    lo = ogive_right(hw_h - t_h / 2, rs_h - t_h / 2, 60)
    hi = ogive_right(hw_h + t_h / 2, rs_h + t_h / 2, 60)
    NH = 9
    for sg in (-1, 1):
        for k in range(NH):
            if sg > 0 and k > 3:
                break
            f0, f1 = 0.9 * k / NH + 0.005, 0.9 * (k + 1) / NH - 0.005
            if sg > 0 and k == 3:
                f1 = f0 + (f1 - f0) * 0.75
            pts = vouss(F, HX, sg, lo, hi, f0, f1, -0.3, M_DEP + 0.35, M_SPR, 0.1)
            if sg > 0 and k == 3:                         # fratura obliqua na ponta de cima
                (u, v), (tu, tv) = _arc_at(hi, f1)
                pn = (F.u() * (sg * tu) + up * tv + F.n() * 0.45).normalized()
                pts = clip(pts, pn, pn.dot(F.v(HX + sg * u, M_DEP / 2, M_SPR + v)) - 0.35)
            hull(mb, pts, RUIN)
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
    crystal_pendant(vf, cc)
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
    """veios de energia nas PAREDES DO TUNEL (09.09): cada veio e uma FENDA - dois labios de rocha escura saltam da
    parede e o fio Neon corre no fundo, 0,2 abaixo deles (a borda faz sombra; nao e raio 2D colado). Nascem no anel do
    vortice e vem para a boca afinando ate sumir."""
    nseg = 0
    for ang, ang1, ya, yb in TUN_VEINS:
        th = math.radians(ang)
        pts = []
        y = ya
        while y >= yb - 0.01:
            hw, spr, rise = tun_at(y)
            p, n = _surf(bvh, Vector((HX, y, P3 + spr * 0.55)), Vector((math.sin(th), 0.0, math.cos(th))))
            if p is not None:
                pts.append((p, n, y))
            y -= 1.5
            f = max(0.0, min(1.0, (ya - y) / (ya - yb)))
            th = math.radians(ang + (ang1 - ang) * f) + 0.05 * math.sin(y * 0.7 + ang)    # ondula devagar
        for (a, na, y_a), (b, nb, y_b) in zip(pts, pts[1:]):
            if (b - a).length > 3.2:
                continue
            f = max(0.0, min(1.0, (y_a - yb) / max(0.1, ya - yb)))
            w = 0.1 + 0.16 * f
            ax = (b - a).normalized()
            nn = (na + nb).normalized()
            sd = nn.cross(ax).normalized()
            up_ = ax.cross(sd).normalized()
            if up_.dot(nn) < 0:
                up_ = -up_
            c = (a + b) / 2
            ln = (b - a).length + 0.2
            lip_m = DEEP if (a.y + b.y) / 2 > 71.0 else RKD
            obox3(mb, c + up_ * 0.02, ax, sd, up_, ln, w, 0.14, VD)                    # fio no fundo da fenda
            for s_ in (-1, 1):                                                        # labios (sombra)
                obox3(mb, c + sd * (s_ * (w / 2 + 0.13)) + up_ * 0.08, ax, sd, up_, ln + 0.1, 0.26, 0.36, lip_m)
            nseg += 1
    print("DUN tunel: %d segmentos de veio (fenda com fio no fundo)" % nseg)


# revestimento de cantaria dos primeiros metros do tunel (09.03): lado -> y final de cada fiada (quebra IRREGULAR,
# dirigida: nada de escadinha regular; o leste mais arruinado)
LINING_END = {-1: (65.4, 64.1, 64.9, 62.8, 63.6, 61.5), 1: (63.6, 62.2, 62.9, 60.9)}
LINING_ROWS = (1.9, 1.7, 1.8, 1.6, 1.7, 1.5)
LINING_LEN = (2.6, 2.2, 2.8, 2.4)
LINING_U = 8.5                                   # face da cantaria (colisao da boca em 8,4 / tunel em 8,0)


def mouth_lining(mb):
    """o ENCONTRO RUINA x CAVERNA: cantaria da RUINA (o tom da boca) em fiadas desencontradas nos primeiros metros; cada
    fiada termina num bloco PARTIDO (face de fratura inclinada), uma pedra alta tombou para dentro e outra caiu no piso
    junto a parede leste. So visual: a colisao das paredes do tunel ja esta atras dela."""
    X, Y = Vector((1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0))
    y0 = HY0 + 0.1
    for sg, ends in LINING_END.items():
        h = -0.1
        for r, y_end in enumerate(ends):
            rh = LINING_ROWS[r]
            y = y0 - (1.3 if r % 2 else 0.0)
            i = r
            blocks = []
            while y < y_end - 0.6:
                ln = LINING_LEN[i % len(LINING_LEN)]
                a, b = max(y, y0), min(y + ln, y_end)
                if b - a > 0.6:
                    blocks.append((a, b))
                y += ln
                i += 1
            for j, (a, b) in enumerate(blocks):
                last = j == len(blocks) - 1
                cuts = []
                ax_, ay_ = X, Y
                if last:
                    cuts.append(((0.0, 1.0, 0.55 if r % 2 else -0.45), 0.55 + 0.1 * (r % 3)))    # face de fratura
                    cuts.append(((-sg * 0.6, 1.0, 0.8), 0.3))
                c = Vector((HX + sg * (LINING_U + 0.7), (a + b) / 2, P3 + h + rh / 2 - 0.02))
                az_ = UPV
                if last and sg < 0 and r == 3:                  # a pedra que tombou: gira 7 graus para dentro
                    t = math.radians(7.0)
                    ax_ = Vector((math.cos(t), 0.0, math.sin(t) * sg))
                    az_ = Vector((-math.sin(t) * sg, 0.0, math.cos(t)))
                    c = c + Vector((-sg * 0.12, 0.0, 0.06))
                cbox(mb, c, ax_, ay_, az_, 1.4, b - a - 0.08, rh - 0.06, RUIN, 0.1, cuts)
            h += rh
    # a pedra que caiu: deitada no piso rente a parede leste, depois do fim do revestimento
    q = place(cbox_pts(Vector(), X, Y, UPV, 1.3, 1.9, 1.4, 0.1), (HX + 8.45, 64.6), (0.3, 0.12, 0.35),
              floor=P3 + 0.12, sink=0.08)
    q = clip(q, Vector((0.2, 1.0, 0.5)).normalized(), max(Vector((0.2, 1.0, 0.5)).normalized().dot(p) for p in q) - 0.45)
    hull(mb, q, RUIN)


# aglomerados de cristal do tunel (09.08): 3 grupos ASSIMETRICOS, crescendo para o fundo
# (y, t no perfil 0 = pe oeste .. 1 = pe leste, altura da coluna maior, raio, colunas)
TUN_CLUSTERS = [(71.0, 0.03, 4.4, 0.72, 4),      # o maior: pe da parede oeste, na metade do tunel
                (75.0, 0.76, 3.3, 0.55, 3),      # medio: alto na parede leste, junto ao arranque
                (67.2, 0.28, 2.0, 0.36, 2),      # pequeno: parede oeste alta, o primeiro que se ve da boca
                (73.2, 0.97, 2.6, 0.46, 3)]      # pe da parede leste, antes do estrado (nunca em par com o oeste)


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
    # cristais do tunel (09.08): 3 aglomerados assimetricos com calo de rocha (casca escura, so a ponta acesa)
    for y, t, h, r, k in TUN_CLUSTERS:
        p, n = tun_point(y, t)
        base = p - n * 0.35
        d = n if 0.25 < t < 0.75 else (n + Vector((0.0, 0.0, 1.1))).normalized()
        cluster(mb, base, d, h, r, k, DEEP if y > 72.0 else RKD)
    # 2 aglomerados no estrado ladeando o vortice: o oeste maior, o leste menor e mais aberto (nada espelhado)
    for sg, h, r, k, d in ((-1, 4.8, 0.9, 4, Vector((0.4, -0.25, 1.0))), (1, 3.3, 0.66, 3, Vector((-0.55, -0.1, 1.0)))):
        b = Vector((HX + sg * 7.7, 78.2, P3 + z2 - 0.2))
        cluster(mb, b, d, h, r, k, OB)
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
        rune(mb, c + radial * (r_in + 0.53) + n * 0.7, tang, radial, n, k, 0.8, m=VD, dep=0.06, w=0.12)
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


ROOM_SPRING = {"R1": 9.0, "R2": 7.0, "R3": 7.0}  # R1 (chegada): arcos ALTOS; R2 mina; R3 altar (09.10)


def room_kit():
    """kit das salas (OVERHAUL 09.10) - MESMA planta, marcadores e colisoes; 1 variacao DIRIGIDA por sala:
    R1 chegada = arcadas cegas ALTAS e o portal em nicho de 2 ordens; R2 mineracao = ESCORAS de madeira de mina nos
    arcos simples e GRELHAS de ferro na arcada dupla; R3 camara final = colunelos DUPLOS e o RETABULO (altar) no eixo
    da parede norte. Pilastras com base e capitel, piso em 2 tamanhos de laje, nervuras em pera, tochas de ferro."""
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
        spr = ROOM_SPRING[nm]
        twin = nm == "R3"
        for F, a, b in ((FS, x0, x1), (FN, x0, x1)):
            corner_col(mk, F, a, 1, R_SPR, A)
            corner_col(mk, F, b, -1, R_SPR, A)
        if nm == "R1":
            ps = [x0 + 12.0, x0 + 24.0]
        elif nm == "R2":
            ps = [x0 + 11.0, x1 - 11.0]
        else:
            ps = [x0 + 11.0, x0 + 22.0, x0 + 33.0]
        for F in (FS, FN):
            bounds = [x0 + 2.4] + [q for p in ps for q in (p - PIL_HW - 0.3, p + PIL_HW + 0.3)] + [x1 - 2.4]
            for p in ps:
                alt = nm == "R3" and F is FN and abs(p - cx3) < 0.1
                pilaster(mk, F, p, R_SPR, A, twin=twin, altar=alt, mi=mi)
            for k in range(0, len(bounds), 2):
                sa, sb = bounds[k], bounds[k + 1]
                # R1: arcada dupla de LANCETAS altas e estreitas em todo vao largo (a variacao da sala)
                blind_arch(mk, F, sa, sb, spr, twin=(sb - sa > 16.0) or (nm == "R1" and sb - sa > 7.0), room=nm,
                           mi=mi)
            cornice(mk, F, x0 + 2.4, x1 - 2.4, R_SPR)
            if nm == "R1":
                for p in ps:
                    torch(mi, F, p, 0.0, 8.4)
        for F, side in ((FW, "W"), (FE, "E")):
            jam = (LY - L.DUN_LINK_W / 2 - PIL_HW - 0.3, LY + L.DUN_LINK_W / 2 + PIL_HW + 0.3)
            if (nm, side) in (("R1", "W"), ("R3", "E")):
                jam = (LY - 9.5, LY + 9.5)
            for p in jam:
                pilaster(mk, F, p, R_SPR, A, twin=twin)
                torch(mi, F, p, 0.0, 8.4, twin=twin)
            blind_arch(mk, F, y0 + 2.4, jam[0] - PIL_HW - 0.3, spr, room=nm, mi=mi)
            blind_arch(mk, F, jam[1] + PIL_HW + 0.3, y1 - 2.4, spr, room=nm, mi=mi)
            cornice(mk, F, y0 + 2.4, jam[0] - PIL_HW - 0.3, R_SPR)
            cornice(mk, F, jam[1] + PIL_HW + 0.3, y1 - 2.4, R_SPR)
            is_link = (nm == "R1" and side == "E") or nm == "R2" or (nm == "R3" and side == "W")
            if is_link:
                link_frame(mk, F, LY, L.DUN_LINK_W / 2)
                skirting(mk, F, jam[0] + PIL_HW + 0.3, LY - L.DUN_LINK_W / 2)
                skirting(mk, F, LY + L.DUN_LINK_W / 2, jam[1] - PIL_HW - 0.3)
        cxr, cyr = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        skip = (lambda x, y, cx=cxr, cy=cyr: abs(x - cx) < 9.0 and abs(y - cy) < 9.0) if nm == "R3" else None
        tile_floor(mf, (x0, y0, x1, y1), Z, margin=1.0, friso=0.8, skip=skip)
        vault(mv, (x0, y0, x1, y1), "x", Z, R_SPR, R_CROWN, ribs=ps)
    # soleiras dos vaos (remate em 3 pedras)
    for xa, xb in ((-26.0, -24.0), (20.0, 22.0)):
        for k in range(3):
            ya = LY - L.DUN_LINK_W / 2 + k * L.DUN_LINK_W / 3
            mf.box2((xa, ya + 0.04, Z - 0.4), (xb, ya + L.DUN_LINK_W / 3 - 0.04, Z), TRL, 0.06)
    altar_medallion(mf, *[(ROOMS["R3"][0] + ROOMS["R3"][2]) / 2.0, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0])
    # lustres: 2 na R2 (mineracao), 1 coroa na R3 (altar)
    for x, y, h, r in ((-13.0, LY, 16.5, 3.0), (9.0, LY, 16.5, 3.0), (cx3, LY, 15.8, 3.8)):
        rect = ROOMS["R2"] if x < 21.0 else ROOMS["R3"]
        top = vault_z(rect, "x", Z, R_SPR, R_CROWN, 0.0) - 0.8
        chandelier(mi, x, y, Z + h, top, r=r, n=6 if r < 3.5 else 8)
    for m in (mk, mv, mf, mi):
        m.finish()


def altar_medallion(mb, cx, cy):
    """quadrado 18 x 18 sem lajes -> anel de remate -> campo navy com as runas ENTALHADAS (Neon escuro) -> anel de
    prata -> disco (tudo com topo em Z)"""
    n = 32
    ang = [2 * math.pi * k / n for k in range(n)]
    Hs = 9.0

    def circ(r):
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in ang]
    sq = [(cx + Hs * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
           cy + Hs * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    rings = [(sq, circ(7.8), FL), (circ(7.8), circ(7.0), TRL), (circ(7.0), circ(6.8), VD), (circ(6.8), circ(3.2), VA),
             (circ(3.2), circ(2.7), VD)]
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
    up = Vector((0.0, 0.0, 1.0))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        rune(mb, Vector((cx, cy, zt - 0.05)) + rad * 5.1, Vector((-rad.y, rad.x, 0.0)), rad, up, k, 2.6, VD, dep=0.06)


def _floor_arc(mb, c, r, a0, a1, w, m, k=12):
    """filete ENTALHADO rente ao piso (arco continuo, topo em Z + 0,01)"""
    pts = [Vector((c.x + r * math.cos(a0 + (a1 - a0) * i / k), c.y + r * math.sin(a0 + (a1 - a0) * i / k),
                   Z - 0.05)) for i in range(k + 1)]
    mb.sweep(pts, [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.06), (-w / 2, 0.06)], m, True, None, up=(0.0, 0.0, 1.0))


def floor_runes(mb, c, n):
    """INSCRICAO no piso diante de um portal das salas (09.13): 7 runas do alfabeto da ilha ENTALHADAS (Neon escuro,
    rentes) entre 2 filetes continuos de obsidiana - faixa de inscricao, nao letreiro aceso"""
    up = Vector((0.0, 0.0, 1.0))
    base = math.atan2(n.y, n.x)
    for i in range(7):
        a = base + math.radians(-54.0 + 18.0 * i)
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        rune(mb, Vector((c.x, c.y, Z - 0.05)) + rad * 6.4, Vector((-rad.y, rad.x, 0.0)), -rad, up, i + 2, 1.6, VD,
             dep=0.06)
    for r in (5.3, 7.5):
        _floor_arc(mb, c, r, base - math.radians(64.0), base + math.radians(64.0), 0.16, VD)


def room_portals():
    """portal de chegada (R1, parede oeste, aceso) e portal de saida (R3, parede leste): moldura de aduelas (09.12);
    R1 (chegada): nicho de 2 ORDENS mais alto (a variacao da sala)"""
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
        rise = r_out + (2.2 if nm == "R1" else 0.8)
        arch_panel(mb, F, LY, r_out + 0.2, rise, c.z - Z, 0.0, 0.0, 0.15, VA, n=8)
        arch_band(mb, F, LY, r_out + 0.2, rise, c.z - Z, 0.0, 0.6, -0.1, 0.55, TRL, n=8)
        if nm == "R1":
            ogee_band(mb, F, LY, r_out + 0.8, rise + 0.6, c.z - Z, 0.5, -0.1, 0.8, CS, n=8)
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
