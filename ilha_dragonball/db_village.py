# db_village - ZONA VILLAGE (vila tech) da Ilha 2 (Dragon Ball): poucas construcoes, alta qualidade.
# Terraco HUB (28,2), lotes L.HUB_LOTS (o db_terrain ja assenta uma laje rente em cada lote, topo HUB - 0,04):
#   capsule_house_A (-58,100)  casa Capsule classica: soco, tambor branco com faixa azul e escotilhas, VARANDA ALTA
#                              em arco com guarda-corpo, faixa de vidro (solario), beiral, cupula branca com faixa e
#                              capa azuis, antena com prato; anexo-torre (tambor + cupula azul + prato). SEM porta.
#   capsule_house_B (62,98)    OUTRA familia: capsula deitada sobre 4 pernas de pouso + coluna tecnica; faixas azuis,
#                              escotilhas laterais, janelao redondo no nariz (olha a praca), exaustor ciano na cauda,
#                              espinha azul com mastro. SEM porta.
#   martial_market (-86,128)   pavilhao marcial ABERTO: 8 postes laqueados em soco de pedra, arquitrave com friso,
#                              telhado chines de 4 aguas laranja (beiral curvo, cantos levantados, fiadas de telha),
#                              balcao (NPC_Market), estantes + expositor de bastoes, 2 barracas laterais NA ESCALA DO
#                              JOGADOR (postes 6,6, testeira H + 5,82; comida no vapor | tecidos e potes) viradas para o
#                              corredor de entrada, lanternas de papel penduradas e 2 lanternas de poste na entrada.
#   workshop (34,116)          OFICINA ENTRAVEL (hangar Capsule): abobada azul com costelas brancas e claraboia de
#                              vidro, portao em arco ABERTO de 10 x 12 virado para a praca (oeste), pe-direito 17;
#                              dentro: veiculo capsula estacionado na plataforma, talha, bancada (NPC_Workshop),
#                              painel de ferramentas, armario, turbina em cavalete, tambores, luz interna; torreta na
#                              cumeeira com radar giratorio (VFX).
#   4 pods (L.PODS)            capsulas pequenas SEM porta, 4 formas: domo, capsula em pe, domo duplo, farol.
#   quiosques + barracas       (rodada final, critica da concept: o terraco lia vazio) 5 quiosques Capsule NAO
#                              entraveis das mesmas 4 familias, menores e enxutos, e 2 barracas ABERTAS de toldo laranja
#                              (balcao, caixotes, 1 lanterna pendurada + lanterna de poste) nas bolsas de areia entre o
#                              mercado, a casa A, a casa B e as torres - DB_Hub_PodsNorth (junto com os postes Capsule e
#                              a moto; 1 MeshPart por material) com colisao propria (area DB_HubPodN).
# Pecas nao entraveis (pods, quiosques, casa A, torreta da oficina) usam cascas ABERTAS (so a face de fora): a face de
# dentro e as tampas escondidas nao eram vistas e custavam os tris que pagam os quiosques novos.
#   dojo (120,-14) GROUND      pavilhao marcial aberto: plataforma de madeira 1,6 acima do chao (2 degraus de 0,8 com
#                              colisao), 8 colunas vermelhas, telhado duplo laranja (clerestorio), 3 bonecos de treino
#                              (poste com bracos), gongo, biombo com janela lua, expositor de armas, estandartes.
#   mobiliario                 3 postes Capsule (lampiao ambar) nos lotes + moto flutuante Capsule estacionada atras da
#                              barraca leste do mercado (dentro do lote).
# Lanternas penduradas: as que ficam FORA de uma colisao tem a borla acima da cabeca (mercado H + 5,55; dojo, no beiral
# sobre o chao, G + 6,65; no meio do dojo D + 5,85); as das barracas penduram DENTRO da planta da colisao da barraca.
# Colisao: SO dos volumes proprios (area DB_Hub*). O piso do terraco/chao e do db_col (congelado).
import math, random
from mathutils import Vector
import db_lib as DL
from db_lib import col_box, col_box2, mk, light, octo_col, Frame, FP
import db_layout as L
import fm_lib
import db_capsule_kit as K
import db_village_kit as VG

S_ = fm_lib.S
# ------------------------------------------------------------------ materiais novos (3 de 6)
NEW_MATS = {
    "Wood_DBHubDeck": (S_(214, 156, 96), 0.7, 0.0, 0, None, 0.0),        # assoalho/balcoes (madeira mel)
    "Plaster_DBHubYellow": (S_(250, 194, 52), 0.5, 0.0, 0, None, 0.0),   # pintura do veiculo/armario (acento)
    "Stone_DBHubConcrete": (S_(186, 192, 200), 0.6, 0.0, 0, None, 0.0),  # piso da oficina
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

COLL = "05_TECH_VILLAGE"
VFXC = "12_VFX_HELPERS"
H, G = L.HUB, L.GROUND
LOTS = {k: (x, y, r) for x, y, r, k in L.HUB_LOTS}
DOJO = [(x, y, r) for x, y, r, k in L.GROUND_LOTS if k == "dojo"][0]
DOJO_D = G + 1.6                    # topo do assoalho do dojo (2 degraus de 0,8)

WHITE, NAVY, BLUE, GLASS = "Plaster_DB_White", "Plaster_DB_Navy", "Roof_DB_Blue", "Glass_DB_Blue"
STEEL, DARK, CYAN = "Metal_DB_Steel", "Metal_DB_Dark", "DB_Cyan_Glow"
ORANGE, RED, WDARK, GOLD, LAMP = "Roof_DB_Orange", "Wood_Lacquer_Red", "Wood_Dark", "Metal_Gold", "Lantern_Glow"
WDARK_B = "Wood_Dark_B"             # 2o tom das tabuas (material explicito: nao e sorteado pela familia do objeto)
BLOCK, PAVE, CREAM = "Stone_DB_Block", "Stone_Paving_DB", "Plaster_Cream"
DECK, YELLOW, CONC = "Wood_DBHubDeck", "Plaster_DBHubYellow", "Stone_DBHubConcrete"
CLOTH, CANVAS = "Cloth_Red", "Cloth_Canvas"

# oficina: referencial (x local = leste, y local = norte), casca e paredes
WS = LOTS["workshop"]
WS_F = Frame(WS[0], WS[1], H, 0.0)
WS_RO, WS_RI, WS_WH = 9.0, 8.2, 9.0         # raio externo/interno da abobada, altura da parede reta
WS_XA, WS_XB = -11.2, 10.8                  # casca (aba de 1,2 na frente = portal fundo)
WS_XW = (-10.0, -9.2)                       # parede da frente (portao)
WS_XE = (9.2, 10.0)                         # parede do fundo
WS_DOOR = (5.0, 7.0, 5.0)                   # meia largura, arranque do arco, flecha -> vao 10 x 12
WS_CAR = (WS[0] - 2.8, WS[1] - 3.2)         # veiculo capsula (31,2; 112,8)
WS_BENCH_X = WS[0] + 5.5                    # eixo da bancada (39,5)
WS_NPC = (WS[0] + 7.8, WS[1] + 1.0)         # (41,8; 117)
WS_INTERACT = (WS[0] + 2.6, WS[1] + 1.0)    # (36,6; 117)
WS_TOWER = (WS[0] + 7.0, WS[1], 1.6)        # torreta do radar na cumeeira da abobada (perto do fundo)

MK = LOTS["martial_market"]
MK_F = Frame(MK[0], MK[1], H, 0.0)

# ------------------------------------------------------------------ cameras de revisao (360 + jogador + interiores)
CAMS = {
    "CAM_DBHub_Overview": ((30.0, 34.0, H + 64.0), (-12.0, 112.0, H + 2.0), 24),
    "CAM_DBHub_PlayerHeight_Street": ((-18.0, 90.0, H + 5.2), (-84.0, 118.0, H + 6.0), 22),
    # vista do mercado desde a casa A (o CAM_DB_Ref_Village antigo ficava dentro do anexo; o db_scene usa (-100, 104))
    "CAM_DBHub_RefVillage_Proposta": ((-50.0, 113.0, H + 6.0), (-86.0, 126.0, H + 5.0), 20),
    "CAM_DBHub_HouseA_SE": ((-36.0, 80.0, H + 8.0), (-58.0, 100.0, H + 9.0), 22),
    "CAM_DBHub_HouseA_W": ((-92.0, 94.0, H + 15.0), (-58.0, 100.0, H + 8.0), 22),
    "CAM_DBHub_HouseA_N": ((-44.0, 136.0, H + 22.0), (-58.0, 100.0, H + 7.0), 22),
    "CAM_DBHub_HouseB_SW": ((40.0, 80.0, H + 7.0), (62.0, 98.0, H + 8.0), 22),
    "CAM_DBHub_HouseB_NE": ((88.0, 122.0, H + 16.0), (62.0, 98.0, H + 7.0), 22),
    "CAM_DBHub_HouseB_NW": ((49.0, 113.0, H + 5.2), (62.0, 98.0, H + 7.0), 22),
    "CAM_DBHub_HouseB_SE": ((82.0, 86.0, H + 5.2), (62.0, 98.0, H + 7.0), 22),
    "CAM_DBHub_Market_Front": ((-86.0, 102.0, H + 5.2), (-86.0, 128.0, H + 5.5), 22),
    "CAM_DBHub_Market_Entry": ((-68.0, 104.0, H + 5.2), (-82.0, 116.0, H + 3.0), 22),
    "CAM_DBHub_Market_Inside": ((-82.5, 117.5, H + 5.2), (-88.0, 131.0, H + 3.5), 18),
    "CAM_DBHub_Market_StallL": ((-83.5, 120.5, H + 5.2), (-93.5, 116.8, H + 4.2), 22),
    "CAM_DBHub_Market_StallR": ((-88.5, 120.5, H + 5.2), (-78.5, 116.8, H + 4.2), 22),
    "CAM_DBHub_Market_E": ((-56.0, 134.0, H + 12.0), (-86.0, 127.0, H + 5.0), 22),
    "CAM_DBHub_Market_NW": ((-118.0, 144.0, H + 20.0), (-86.0, 126.0, H + 4.0), 22),
    "CAM_DBHub_Workshop_Front": ((6.0, 109.0, H + 5.2), (32.0, 116.0, H + 6.5), 22),
    "CAM_DBHub_Workshop_Inside": ((26.6, 120.2, H + 5.2), (41.5, 113.5, H + 3.2), 18),
    "CAM_DBHub_Workshop_Inside2": ((40.6, 122.0, H + 6.2), (26.0, 112.0, H + 5.0), 18),
    "CAM_DBHub_Workshop_Back": ((62.0, 140.0, H + 22.0), (34.0, 116.0, H + 8.0), 22),
    "CAM_DBHub_Workshop_S": ((30.0, 84.0, H + 12.0), (32.0, 114.0, H + 7.0), 22),
    "CAM_DBHub_Workshop_N": ((50.0, 130.0, H + 5.2), (30.0, 117.0, H + 5.0), 22),
    "CAM_DBHub_Workshop_Plaza": ((10.0, 100.0, H + 5.2), (26.0, 110.0, H + 6.0), 22),
    "CAM_DBHub_Dojo_Front": ((90.0, -11.0, G + 5.2), (118.0, -14.0, G + 6.5), 22),
    "CAM_DBHub_Dojo_Inside": ((110.5, -18.5, DOJO_D + 5.2), (128.0, -12.0, DOJO_D + 3.2), 18),
    "CAM_DBHub_Dojo_Back": ((150.0, -40.0, G + 24.0), (120.0, -14.0, G + 8.0), 22),
    "CAM_DBHub_Dojo_N": ((114.0, 22.0, G + 14.0), (120.0, -14.0, G + 6.0), 22),
    "CAM_DBHub_Dojo_S": ((130.0, -44.0, G + 5.2), (120.0, -14.0, G + 5.0), 22),
    "CAM_DBHub_Dojo_Dummies": ((116.0, -17.5, DOJO_D + 5.2), (120.0, -10.5, DOJO_D + 3.0), 22),
    "CAM_DBHub_PodS": ((-40.0, -70.0, G + 9.0), (-58.0, -92.0, G + 3.5), 22),
    "CAM_DBHub_PodSE": ((42.0, -72.0, G + 9.0), (60.0, -90.0, G + 4.5), 22),
    "CAM_DBHub_PodW": ((-82.0, 56.0, G + 8.0), (-100.0, 40.0, G + 3.0), 22),
    "CAM_DBHub_PodE": ((88.0, 30.0, G + 8.0), (104.0, 14.0, G + 3.5), 22),
    # quiosques e barracas de toldo nas bolsas do terraco (rodada final) + paineis de tabuas das barracas do mercado
    "CAM_DBHub_Top": ((0.0, 132.0, H + 240.0), (0.0, 133.0, H), 24),
    "CAM_DBHub_Kiosks_W": ((-34.0, 103.0, H + 5.2), (-58.0, 121.0, H + 4.0), 22),
    "CAM_DBHub_Stall_W": ((-8.0, 108.0, H + 5.2), (-24.0, 116.0, H + 3.8), 22),
    "CAM_DBHub_Kiosks_N": ((-80.0, 148.0, H + 6.0), (-93.0, 170.0, H + 4.0), 22),
    "CAM_DBHub_Kiosks_E": ((86.0, 104.0, H + 5.2), (106.0, 120.0, H + 4.0), 22),
    "CAM_DBHub_Kiosks_E2": ((118.0, 98.0, H + 8.0), (102.0, 120.0, H + 3.0), 22),
    "CAM_DBHub_Market_StallBackE": ((-69.0, 108.0, H + 5.2), (-77.5, 117.5, H + 3.5), 22),
    "CAM_DBHub_Market_StallBackW": ((-104.0, 108.0, H + 5.2), (-95.0, 117.5, H + 3.5), 22),
}

# ------------------------------------------------------------------ rotas e sondas extras (db_qa)
EXTRA_ROUTES = {
    "OFICINA_PRACA->PORTAO->BANCADA": ([(8.0, 110.0), (16.0, 114.0), (21.0, 116.0), (26.0, 116.2), (31.0, 116.6),
                                        WS_INTERACT], H),
    "MERCADO_RUA->BALCAO": ([(-86.0, 84.0), (-86.0, 100.0), (-86.0, 112.0), (-86.0, 118.0), (-86.0, 124.6)], H),
    "VILA_RUA_OESTE": ([(0.0, 96.0), (-20.0, 86.0), (-50.0, 84.0), (-80.0, 84.0), (-92.0, 86.5)], H),
    "DOJO_TRILHA->DEGRAUS->TATAME": ([(96.0, -10.5), (102.0, -13.0), (104.0, -14.0), (106.5, -14.0), (109.0, -14.0),
                                      (114.0, -14.0), (120.0, -14.5)], G),
}
EXTRA_PROBES = [
    ("OFICINA_parede_S", WS[0], WS[1] - 6.0, H, 0.0, -1.0, 3.5),
    ("OFICINA_parede_N", WS[0] + 1.0, WS[1] + 5.0, H, 0.0, 1.0, 4.5),
    ("OFICINA_fundo", WS[0] + 7.0, WS[1] - 6.0, H, 1.0, 0.0, 3.5),
]


# ------------------------------------------------------------------ pecas comuns
def capsule_lamp(mb, x, y, z, h=5.0):
    """poste Capsule da vila: soco de arenito, fuste branco com anel azul, lampiao (globo ambar entre discos
    brancos, cupula azul) - a mesma familia do db_entrance"""
    mb.cyl(0.95, 0.5, (x, y, z + 0.25), (0, 0, 0), BLOCK, 8, bevel=0.0)
    mb.cyl(0.4, h, (x, y, z + 0.5 + h / 2), (0, 0, 0), WHITE, 8, bevel=0.0)
    mb.cyl(0.55, 0.4, (x, y, z + 0.5 + h * 0.4), (0, 0, 0), BLUE, 8, bevel=0.0)
    t = z + 0.5 + h
    mb.cyl(0.4, 0.6, (x, y, t + 0.3), (0, 0, 0), NAVY, 8, bevel=0.0)
    mb.cyl(0.9, 0.28, (x, y, t + 0.74), (0, 0, 0), WHITE, 10, bevel=0.0)
    mb.cyl(0.62, 1.3, (x, y, t + 0.88 + 0.65), (0, 0, 0), LAMP, 10, bevel=0.0)
    mb.cyl(0.94, 0.28, (x, y, t + 2.18 + 0.14), (0, 0, 0), WHITE, 10, bevel=0.0)
    VG.dome_open(mb, (x, y), 0.7, 0.62, t + 2.46, 0.0, 70.0, 3, BLUE, 10)
    mb.cyl(0.28, 0.35, (x, y, t + 2.46 + 0.62), (0, 0, 0), BLUE, 6, bevel=0.0)
    col_box("DB_HubLamp", (1.9, 1.9, h + 3.4), (x, y, z + (h + 3.4) / 2))


def hover_bike(mb, x, y, z, yaw):
    """moto flutuante Capsule estacionada (so visual + caixa de colisao): casco branco, carenagem azul, banco
    azul-marinho, para-brisa, 2 sapatas de flutuacao com brilho ciano e um pezinho de apoio. Frente = +x local"""
    F = Frame(x, y, z, yaw)
    VG.ellipsoid(mb, F.p(0.0, 0.0, 1.35), (1.75, 0.62, 0.5), yaw, WHITE, sub=2)
    VG.ellipsoid(mb, F.p(1.05, 0.0, 1.62), (0.8, 0.56, 0.44), yaw, BLUE, sub=1)
    VG.ellipsoid(mb, F.p(1.3, 0.0, 2.02), (0.36, 0.44, 0.3), yaw, GLASS, sub=1)
    mb.box((1.3, 0.62, 0.3), F.p(-0.35, 0.0, 1.86), F.r(), NAVY, 0.0)
    mb.rod(F.p(0.95, -0.7, 2.1), F.p(0.95, 0.7, 2.1), 0.1, NAVY, 6)
    for sx in (-1.0, 1.0):
        mb.cyl(0.56, 0.36, F.p(sx, 0.0, 0.6), F.r(), NAVY, 12, bevel=0.0)
        mb.cyl(0.42, 0.12, F.p(sx, 0.0, 0.38), F.r(), CYAN, 12, bevel=0.0)
    mb.beam(F.p(-0.2, 0.35, 1.0), F.p(-0.1, 0.85, 0.05), 0.2, 0.22, NAVY, 0.0)
    mb.box((1.2, 0.2, 0.26), F.p(-1.45, 0.0, 1.55), F.r(0.0, -0.3, 0.0), BLUE, 0.0)
    col_box("DB_HubBike", (4.3, 1.8, 2.4), F.p(-0.1, 0.0, 1.2), F.r())


def dish(mb, c, facing, r=1.3, m=WHITE, rim_m=NAVY, n=14):
    """prato de antena (cone raso) virado para 'facing', com haste da antena receptora"""
    f = Vector(facing).normalized()
    c = Vector(c)
    K.cyl_axis(mb, r, 0.45, c, f, m, n, r2=r * 0.35)
    K.cyl_axis(mb, r + 0.12, 0.2, c + f * 0.22, f, rim_m, n)
    mb.rod(c, c + f * 1.3, 0.1, STEEL, 4)
    K.sphere(mb, c + f * 1.35, 0.2, rim_m, sub=0)


def mast(mb, x, y, z0, z1, orb=0.42):
    mb.rod((x, y, z0), (x, y, z1), 0.2, STEEL, 6)
    mb.cyl(0.45, 0.3, (x, y, z0 + (z1 - z0) * 0.55), (0, 0, 0), NAVY, 8, bevel=0.0)
    K.sphere(mb, (x, y, z1 + orb * 0.7), orb, CYAN, sub=1)


# ------------------------------------------------------------------ casa Capsule A (classica, varanda alta)
def house_a():
    cx, cy, _ = LOTS["capsule_house_A"]
    c = (cx, cy)
    z = H
    mb = K.CMB("DB_Hub_HouseA", COLL, rng=random.Random(5101))
    R = 9.0
    # soco de arenito + rodape azul-marinho + tambor branco + faixa azul (topo do tambor)
    prof = [(7.6, z - 0.3), (9.9, z - 0.3), (9.9, z + 0.45), (9.55, z + 0.45), (9.55, z + 0.95), (9.08, z + 0.95),
            (R, z + 1.3), (R, z + 7.3), (R + 0.32, z + 7.3), (R + 0.32, z + 8.6), (R, z + 8.6), (R, z + 8.95),
            (7.6, z + 8.95)]
    mats = [BLOCK, BLOCK, NAVY, NAVY, WHITE, WHITE, BLUE, BLUE, BLUE, WHITE, WHITE, WHITE]
    VG.lathe_open(mb, c, prof[1:] + prof[:1], WHITE, 40, smooth=[5, 7], mats=mats)     # (o fundo enterrado sai)
    annex_th = 135.0
    # escotilhas no tambor + costuras de painel azul-marinho entre elas
    for th in (-157.5, -112.5, -67.5, -22.5, 22.5, 67.5):
        t = math.radians(th)
        VG.porthole(mb, (cx + R * math.cos(t), cy + R * math.sin(t), z + 4.5), (math.cos(t), math.sin(t), 0), 1.25,
                    0.6, n=PORT_N)
    for k in range(16):
        th = 11.25 + 22.5 * k
        if abs((th - annex_th + 180.0) % 360.0 - 180.0) < 32.0:
            continue
        t = math.radians(th)
        mb.box((0.3, 0.36, 5.8), (cx + (R + 0.08) * math.cos(t), cy + (R + 0.08) * math.sin(t), z + 4.2),
               (0, 0, t), NAVY, 0.0)
    # varanda alta em arco (SE, de frente para a rua e a praca): laje, testeira, maos-francesas, guarda-corpo
    ba0, ba1 = -150.0, 40.0
    K.lathe(mb, c, [(8.4, z + 8.95), (10.9, z + 8.95), (10.9, z + 9.5), (8.4, z + 9.5)], WHITE, 32, ba0, ba1)
    K.lathe(mb, c, [(10.85, z + 8.72), (11.15, z + 8.72), (11.15, z + 9.58), (10.85, z + 9.58)], NAVY, 32, ba0, ba1)
    K.lathe(mb, c, [(10.5, z + 10.6), (10.84, z + 10.6), (10.84, z + 10.92), (10.5, z + 10.92)], BLUE, 32, ba0, ba1)
    npost = 16
    for i in range(npost + 1):
        t = math.radians(ba0 + (ba1 - ba0) * i / npost)
        big = i in (0, npost) or i % 4 == 0
        s = 0.5 if big else 0.34
        mb.box((s, s, 1.12), (cx + 10.67 * math.cos(t), cy + 10.67 * math.sin(t), z + 9.5 + 0.56), (0, 0, t),
               WHITE if not big else NAVY, 0.0)
    for i in range(6):
        t = math.radians(ba0 + 12.0 + (ba1 - ba0 - 24.0) * i / 5)
        u = Vector((math.cos(t), math.sin(t), 0.0))
        a = Vector((cx, cy, z + 6.6)) + u * (R - 0.1)
        b = Vector((cx, cy, z + 8.85)) + u * 10.4
        mb.beam(a, b, 0.42, 0.5, NAVY, 0.0)
    # solario: faixa de vidro com montantes + beiral (forro azul-marinho)
    K.lathe(mb, c, [(8.05, z + 9.5), (8.45, z + 9.5), (8.45, z + 11.65), (8.05, z + 11.65)], GLASS, 32)
    for k in range(24):
        t = math.radians(7.5 + 15.0 * k)
        mb.box((0.36, 0.4, 2.15), (cx + 8.5 * math.cos(t), cy + 8.5 * math.sin(t), z + 10.575), (0, 0, t), NAVY, 0.0)
    VG.lathe_open(mb, c, [(7.9, z + 11.65), (9.95, z + 11.65), (9.95, z + 12.0), (9.6, z + 12.28), (7.9, z + 12.28)],
                  WHITE, 40, mats=[NAVY, NAVY, WHITE, WHITE])
    # cupula branca com faixa azul, capa azul, 3 escotilhas-mansarda e antena
    # (casa NAO entravel: cupula e capa sao cascas abertas, so a face de fora - a de dentro nunca aparece)
    E = K.Ell(cx, cy, z + 12.2, 9.4, 6.9)
    VG.dome_open(mb, c, 9.4, 6.9, z + 12.2, 0.0, 62.0, 7, WHITE, 40)
    K.rib_parallel(mb, E, 30.0, 0.0, 360.0, 40, 1.2, 0.2, 0.3, BLUE)
    VG.dome_open(mb, c, 9.56, 7.06, z + 12.2, 60.0, 86.0, 4, BLUE, 40, lip=(9.4, 6.9))
    K.rib_parallel(mb, K.Ell(cx, cy, z + 12.2, 9.56, 7.06), 60.5, 0.0, 360.0, 40, 0.5, 0.12, 0.3, WHITE)
    for th in (-100.0, -55.0, -10.0):
        VG.porthole(mb, E.pt(th, 20.0), E.nrm(th, 20.0), 0.95, 0.5, n=PORT_N)
    ztop = z + 12.2 + 7.06 * math.sin(math.radians(86.0))
    mb.cyl(1.25, 0.8, (cx, cy, ztop + 0.25), (0, 0, 0), WHITE, 16, bevel=0.0)
    mast(mb, cx, cy, ztop + 0.6, ztop + 5.4)
    dish(mb, (cx + 0.9, cy - 0.9, ztop + 3.0), (0.7, -0.7, 0.6), 1.1)
    # anexo-torre (NO): tambor alto, faixa azul, escotilhas, cupula azul e prato de satelite
    ad = 8.7
    ax, ay = cx + ad * math.cos(math.radians(annex_th)), cy + ad * math.sin(math.radians(annex_th))
    ar = 3.6
    prof = [(3.95, z - 0.3), (3.95, z + 0.45), (ar, z + 0.45), (ar, z + 9.6), (ar + 0.26, z + 9.6),
            (ar + 0.26, z + 10.6), (ar, z + 10.6), (ar, z + 11.25)]
    VG.lathe_open(mb, (ax, ay), prof, WHITE, 32, smooth=[2], mats=[BLOCK, BLOCK, WHITE, BLUE, BLUE, BLUE, WHITE])
    for th in (95.0, 175.0):
        t = math.radians(th)
        VG.porthole(mb, (ax + ar * math.cos(t), ay + ar * math.sin(t), z + 7.4), (math.cos(t), math.sin(t), 0), 0.85,
                    0.5, n=PORT_N)
    t = math.radians(135.0)
    mb.box((0.5, 1.2, 5.6), (ax + (ar + 0.05) * math.cos(t), ay + (ar + 0.05) * math.sin(t), z + 4.2), (0, 0, t),
           NAVY, 0.0)
    VG.dome_open(mb, (ax, ay), 3.8, 2.9, z + 11.2, 0.0, 78.0, 6, BLUE, 32)
    zt = z + 11.2 + 2.9 * math.sin(math.radians(78.0))
    mb.cyl(0.95, 0.6, (ax, ay, zt + 0.2), (0, 0, 0), WHITE, 12, bevel=0.0)
    mb.rod((ax, ay, zt + 0.4), (ax, ay, zt + 2.6), 0.18, STEEL, 6)
    dish(mb, (ax, ay, zt + 2.6), (-0.6, 0.55, 0.6), 1.5)
    mb.finish()
    octo_col("DB_HubHouseA", cx, cy, 10.6, z - 0.5, z + 19.5)
    octo_col("DB_HubHouseA", ax, ay, 4.1, z - 0.5, z + 14.5)


# ------------------------------------------------------------------ casa Capsule B (capsula deitada sobre pernas)
def house_b():
    cx, cy, _ = LOTS["capsule_house_B"]
    z = H
    mb = K.CMB("DB_Hub_HouseB", COLL, rng=random.Random(5102))
    ang = math.radians(18.0)                    # nariz (-u) para o oeste-sudoeste: olha a praca e a rua
    u = Vector((math.cos(ang), math.sin(ang), 0.0))
    v = Vector((-u.y, u.x, 0.0))
    zc = z + 8.3
    Rp, hl = 4.8, 5.0
    C = Vector((cx, cy, zc))
    # casco: nariz de vidro (janelao que olha a praca) e cauda azul-marinho com bocal ciano
    NS, TS = 40.0, 52.0
    VG.pill(mb, C, u, Rp, hl, WHITE, n=24, k_cap=6, nose=(GLASS, NS), tail=(NAVY, TS))
    for ph in (NS, TS):
        sg = -1 if ph == NS else 1
        rr = Rp * math.cos(math.radians(ph))
        K.cyl_axis(mb, rr + 0.16, 0.45, C + u * (sg * (hl + Rp * math.sin(math.radians(ph)))), u, NAVY, 24)
    K.cyl_axis(mb, 1.05, 0.5, C + u * (hl + Rp * math.sin(math.radians(72.0)) + 0.1), u, CYAN, 16)
    for s in (-hl + 0.7, hl - 0.7):
        K.cyl_axis(mb, Rp + 0.14, 0.95, C + u * s, u, BLUE, 24)
    K.cyl_axis(mb, Rp + 0.08, 0.35, C + u * 0.0, u, NAVY, 24)
    for s in (-2.5, 2.5):
        for sg in (-1, 1):
            n_ = v * sg
            VG.porthole(mb, C + u * s + n_ * Rp, n_, 1.05, 0.5, n=PORT_N)
    # espinha azul no dorso + mastro com prato
    yaw = math.atan2(u.y, u.x)
    mb.box((8.6, 1.1, 0.9), C + Vector((0, 0, Rp + 0.2)), (0, 0, yaw), BLUE, 0.0)
    mb.box((2.2, 1.5, 0.6), C + u * 3.2 + Vector((0, 0, Rp + 0.62)), (0, 0, yaw), NAVY, 0.0)
    mast(mb, C.x + u.x * 3.2, C.y + u.y * 3.2, zc + Rp + 0.9, zc + Rp + 5.2)
    dish(mb, C - u * 2.2 + Vector((0, 0, Rp + 1.3)), (-u.x * 0.7, -u.y * 0.7, 0.7), 1.2)
    # coluna tecnica (anel de vidro) + soco
    mb.cyl(3.1, 0.4, (cx, cy, z + 0.2), (0, 0, 0), BLOCK, 20, bevel=0.0)
    mb.cyl(2.2, zc - 3.9 - (z + 0.4), (cx, cy, (z + 0.4 + zc - 3.9) / 2), (0, 0, 0), NAVY, 20, bevel=0.0)
    mb.cyl(2.32, 1.0, (cx, cy, z + 2.3), (0, 0, 0), GLASS, 20, bevel=0.0)
    for zz in (z + 1.6, z + 3.0):
        mb.cyl(2.4, 0.25, (cx, cy, zz), (0, 0, 0), STEEL, 20, bevel=0.0)
    # 4 pernas de pouso (azul-marinho) com junta, pistao e sapata
    for su in (-1, 1):
        for sv in (-1, 1):
            hip = C + u * (su * 3.4) + v * (sv * 2.7) + Vector((0, 0, -3.5))
            knee = C + u * (su * 5.0) + v * (sv * 4.1) + Vector((0, 0, -5.4))
            foot = Vector((cx, cy, 0)) + u * (su * 5.5) + v * (sv * 4.3)
            foot.z = z + 0.4
            mb.beam(hip, knee, 0.7, 0.7, NAVY, 0.0)
            mb.beam(knee, foot, 0.62, 0.62, NAVY, 0.0)
            K.sphere(mb, knee, 0.5, STEEL, sub=1)
            mb.beam(hip + Vector((0, 0, -0.4)), (knee + foot) / 2, 0.3, 0.3, STEEL, 0.0)
            mb.cyl(1.0, 0.4, (foot.x, foot.y, z + 0.2), (0, 0, 0), STEEL, 12, bevel=0.0)
    mb.finish()
    # colisao: corpo (cilindro + pernas) e as duas pontas mais estreitas
    col_box("DB_HubHouseB", (12.8, 10.4, zc + Rp + 0.8 - (z - 0.5)), (cx, cy, (z - 0.5 + zc + Rp + 0.8) / 2),
            (0, 0, yaw))
    for sg in (-1, 1):
        q = C + u * (sg * 8.1)
        col_box("DB_HubHouseB", (3.4, 7.0, zc + 3.6 - (z - 0.5)), (q.x, q.y, (z - 0.5 + zc + 3.6) / 2), (0, 0, yaw))


# ------------------------------------------------------------------ mercado marcial (pavilhao aberto + barracas)
STALL_EAVE = 6.5                    # beiral da barraca: testeira em H + 5,82 (acima da cabeca 5,2 de quem compra)
STALL_RISE = 1.8                    # agua mais baixa e sem chifres na cumeeira: a barraca fica subordinada ao pavilhao


def _bun(mb, x, y, z, s=1.0):
    """pao no vapor (baozi): domo de torno liso com o biquinho torcido no topo - nada de pedra facetada"""
    prof = [(0.06 * s, z), (0.3 * s, z), (0.34 * s, z + 0.09 * s), (0.29 * s, z + 0.21 * s), (0.16 * s, z + 0.29 * s),
            (0.06 * s, z + 0.31 * s)]
    K.lathe(mb, (x, y), prof, CREAM, 10, smooth=[1, 2, 3, 4])
    mb.cyl(0.08 * s + 0.04, 0.1, (x, y, z + 0.33 * s), (0, 0, 0), CREAM, 6, r2=0.03, bevel=0.0)


def _stall(mb, x, y, yaw, rng, goods="food"):
    """barraca na escala do jogador: 4 postes laqueados de 6,6, vigas em H + 6,25, painel de fundo, balcao virado para
    +y local, sanefa vermelha, telhadinho chines com beiral em H + 6,5 (testeira H + 5,82). A lanterna pendura DENTRO
    da planta da colisao (y local <= 0,2), atras da mercadoria: quem compra no balcao nao a atravessa."""
    F = Frame(x, y, H, yaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.5, 0.5, 6.6), F.p(sx * 2.75, sy * 1.65, 3.3), F.r(), RED, 0.0)
            mb.box((0.9, 0.9, 0.35), F.p(sx * 2.75, sy * 1.65, 0.175), F.r(), BLOCK, 0.0)
        mb.box((0.4, 3.7, 0.45), F.p(sx * 2.75, 0, 6.25), F.r(), RED, 0.0)
    mb.box((6.0, 0.4, 0.6), F.p(0, 1.65, 6.25), F.r(), RED, 0.0)
    mb.box((6.0, 0.4, 0.6), F.p(0, -1.65, 6.25), F.r(), RED, 0.0)
    mb.box((5.8, 0.44, 0.16), F.p(0, 1.66, 5.9), F.r(), GOLD, 0.0)
    # sanefa de pano em 2 folhas na frente (dentro da planta: y 1,98 < 2,05; vao no meio mostra a lanterna) e
    # painel de fundo ate a viga
    for sx in (-1, 1):
        mb.box((1.9, 0.12, 0.5), F.p(sx * 1.6, 1.92, 5.7), F.r(), CLOTH, 0.0)
    # painel de fundo em TABUAS verticais (0,9 com junta de 0,08, dois tons) sobre um fundo recuado, entre os postes
    # de canto, com travessa laqueada no topo e rodape; faixa de pano vermelho com bandeirolas no terco de cima (lado
    # de fora). Antes era 1 caixa: na textura de 5 studs virava uma tabua gigante (placa escura chapada)
    mb.box((5.0, 0.12, 5.4), F.p(0, -1.62, 3.0), F.r(), WDARK, 0.0)
    nbd, bw, gap = 5, 0.9, 0.08
    bx0 = -(nbd * bw + (nbd - 1) * gap) / 2.0 + bw / 2.0
    for i in range(nbd):
        mb.box((bw, 0.22, 5.3), F.p(bx0 + i * (bw + gap), -1.8, 2.95), F.r(), WDARK if i % 2 else WDARK_B, 0.0)
    mb.box((5.6, 0.44, 0.4), F.p(0, -1.78, 5.75), F.r(), RED, 0.0)
    mb.box((5.6, 0.44, 0.35), F.p(0, -1.78, 0.4), F.r(), RED, 0.0)
    mb.box((5.0, 0.1, 1.05), F.p(0, -1.97, 4.95), F.r(), CLOTH, 0.0)
    mb.box((5.0, 0.14, 0.16), F.p(0, -1.99, 4.42), F.r(), GOLD, 0.0)
    for gx in (-1.7, 0.0, 1.7):
        mb.box((0.9, 0.1, 0.45), F.p(gx, -1.97, 4.12), F.r(), CLOTH, 0.0)
    for zz in (2.2, 4.4):
        mb.box((5.5, 0.4, 0.22), F.p(0, -1.6, zz), F.r(), RED, 0.0)
    mb.box((5.5, 0.9, 2.4), F.p(0, 1.2, 1.2), F.r(), WDARK, 0.0)
    mb.box((5.1, 0.2, 1.6), F.p(0, 1.68, 1.25), F.r(), RED, 0.0)
    mb.box((5.9, 1.3, 0.25), F.p(0, 1.25, 2.52), F.r(), DECK, 0.0)
    zc = 2.645                                  # topo do tampo do balcao
    if goods == "food":
        # barraca de comida: 2 torres de cestos de bambu no vapor (tampa em cone) + cesto aberto com paes + gamela
        # com laranjas lisas (folhinha verde no cabo): nada que leia como pedra ou cristal
        for gx in (-2.05, -1.1):
            p = F.p(gx, 1.15, zc)
            nb = 3 if gx < -2.0 else 2
            for k in range(nb):
                mb.cyl(0.46, 0.3, (p.x, p.y, p.z + 0.15 + 0.32 * k), (0, 0, 0), DECK, 12, bevel=0.0)
                mb.cyl(0.49, 0.07, (p.x, p.y, p.z + 0.29 + 0.32 * k), (0, 0, 0), WDARK, 12, bevel=0.0)
            zt = p.z + 0.32 * nb
            mb.cyl(0.47, 0.34, (p.x, p.y, zt + 0.17), (0, 0, 0), DECK, 12, r2=0.14, bevel=0.0)
            mb.cyl(0.1, 0.14, (p.x, p.y, zt + 0.4), (0, 0, 0), WDARK, 6, bevel=0.0)
        p = F.p(0.35, 1.15, zc)
        mb.cyl(0.66, 0.26, (p.x, p.y, p.z + 0.13), (0, 0, 0), DECK, 12, bevel=0.0)
        mb.cyl(0.69, 0.07, (p.x, p.y, p.z + 0.25), (0, 0, 0), WDARK, 12, bevel=0.0)
        for j in range(4):
            a = j * math.pi / 2 + 0.3
            _bun(mb, p.x + 0.3 * math.cos(a), p.y + 0.3 * math.sin(a), p.z + 0.26, 0.85)
        p = F.p(1.85, 1.15, zc)
        K.lathe(mb, (p.x, p.y), [(0.3, p.z), (0.62, p.z + 0.14), (0.68, p.z + 0.36), (0.58, p.z + 0.36),
                                 (0.5, p.z + 0.2), (0.3, p.z + 0.14)], WDARK, 12, smooth=[1])
        for j in range(3):
            a = j * 2.0 * math.pi / 3 + 0.4
            q = (p.x + 0.24 * math.cos(a), p.y + 0.24 * math.sin(a), p.z + 0.5)
            K.sphere(mb, q, 0.25, ORANGE, sub=2)
            mb.box((0.3, 0.18, 0.08), (q[0] + 0.06, q[1], q[2] + 0.26), (0, 0.35, a), "Leaf_Palm", 0.0)
        K.sphere(mb, (p.x, p.y, p.z + 0.78), 0.25, ORANGE, sub=2)
    else:
        for k, gx in enumerate((-1.9, -0.7, 0.6, 1.8)):
            p = F.p(gx, 1.2, 2.65)
            mm = CLOTH if k % 2 == 0 else CANVAS
            mb.cyl(0.42, 1.1, (p.x, p.y, p.z + 0.42), (0, math.pi / 2, yaw), mm, 8, bevel=0.0)
        VG.jar(mb, *F.p(2.3, -1.1, 0.0)[:2], H, 1.0, BLUE)
        # pecas de tecido penduradas numa vara diante do painel de fundo (vitrine da barraca)
        mb.beam(F.p(-2.5, -1.35, 5.45), F.p(2.5, -1.35, 5.45), 0.16, 0.16, WDARK, 0.0)
        for gx, mm, hh in ((-1.55, CLOTH, 2.6), (0.0, BLUE, 2.2), (1.55, CANVAS, 2.5)):
            mb.box((1.3, 0.12, hh), F.p(gx, -1.3, 5.45 - hh / 2), F.r(), mm, 0.0)
            mb.box((1.34, 0.16, 0.2), F.p(gx, -1.3, 5.45 - hh + 0.1), F.r(), GOLD, 0.0)
    VG.hip_roof(mb, F.p(0, 0).x, F.p(0, 0).y, yaw, 4.0, 3.0, H + STALL_EAVE, STALL_RISE, lift=0.75, flare=0.55, ns=6,
                nu=4, rib_step=1.7, th=0.4, horns=False, fascia_n=6, hip_n=3)
    # lanterna no meio, atras do balcao (y local -0,4): corpo H + 5,7..4,7, borla ate H + 3,85, tudo na planta da
    # colisao; aparece pelo vao da sanefa para quem esta no balcao
    ztop = VG.roof_z(4.0, 3.0, STALL_EAVE, STALL_RISE, 0.0, -0.4) - 0.4
    VG.red_lantern(mb, F.p(0, -0.4, ztop), r=0.6, h=1.0, hang=ztop - 5.9)
    col_box("DB_HubMarket", (6.45, 4.25, 6.6), F.p(0, 0, 3.3), F.r())


def market():
    x0, y0, _ = MK
    F = MK_F
    mb = K.CMB("DB_Hub_Market", COLL, rng=random.Random(5103))
    rng = random.Random(5113)
    PX = (-10.2, -4.6, 4.6, 10.2)
    PY = (-5.6, 7.4)
    # assoalho de tabuas rente (topo H + 0,03 = o piso de colisao; juntas escuras rebaixadas a H - 0,02)
    mb.box2(F.p(-11.6, -6.8, -0.14), F.p(11.6, 8.6, -0.02), WDARK, 0.0)
    nb = 12
    for k in range(nb):
        yy = -6.8 + 15.4 * (k + 0.5) / nb
        mb.box((23.0, 15.4 / nb - 0.14, 0.12), F.p(0, yy, -0.03), F.r(), DECK, 0.0)
    # postes laqueados em soco de pedra, capitel dourado
    for px in PX:
        for py in PY:
            mb.box((1.7, 1.7, 0.55), F.p(px, py, 0.275), F.r(), BLOCK, 0.0)
            mb.cyl(0.56, 7.9, F.p(px, py, 0.55 + 3.95), (0, 0, 0), RED, 12, bevel=0.0)
            mb.cyl(0.64, 0.26, F.p(px, py, 1.0), (0, 0, 0), GOLD, 10, bevel=0.0)
            mb.cyl(0.64, 0.26, F.p(px, py, 7.1), (0, 0, 0), GOLD, 10, bevel=0.0)
            mb.box((1.5, 1.5, 0.5), F.p(px, py, 8.7), F.r(), GOLD, 0.0)
            col_box("DB_HubMarket", (1.7, 1.7, 9.0), F.p(px, py, 4.5), F.r())
    # arquitrave (vigas laqueadas + filete dourado) e frechal sob o telhado
    for py in PY:
        mb.beam(F.p(-10.8, py, 8.0), F.p(10.8, py, 8.0), 0.75, 0.95, RED, 0.0)
        mb.beam(F.p(-10.6, py, 7.38), F.p(10.6, py, 7.38), 0.55, 0.24, GOLD, 0.0)
        mb.beam(F.p(-11.0, py, 9.2), F.p(11.0, py, 9.2), 0.6, 0.6, RED, 0.0)
    for px in (-10.2, 10.2):
        mb.beam(F.p(px, -6.2, 8.0), F.p(px, 8.0, 8.0), 0.75, 0.95, RED, 0.0)
        mb.beam(F.p(px, -6.2, 9.2), F.p(px, 8.0, 9.2), 0.6, 0.6, RED, 0.0)
    # friso vazado sob a viga da frente (vao central)
    for x_a, x_b in ((-4.0, 4.0),):
        mb.beam(F.p(x_a, -5.6, 7.1), F.p(x_b, -5.6, 7.1), 0.3, 0.3, WDARK, 0.0)
        mb.beam(F.p(x_a, -5.6, 6.45), F.p(x_b, -5.6, 6.45), 0.3, 0.3, WDARK, 0.0)
        for k in range(11):
            xx = x_a + (x_b - x_a) * k / 10
            mb.box((0.26, 0.3, 0.95), F.p(xx, -5.6, 6.8), F.r(), WDARK if k % 2 else RED, 0.0)
    # telhado chines (beiral curvo, cantos levantados)
    VG.hip_roof(mb, x0, y0 + 0.9, 0.0, 13.0, 9.3, H + 8.9, 4.6, lift=1.6, flare=1.2, ns=8, nu=5)
    # parede de fundo: rodape laqueado + biombo de papel com grade
    mb.box((20.4, 0.45, 1.3), F.p(0, 7.4, 0.65), F.r(), RED, 0.0)
    mb.box((20.2, 0.3, 5.4), F.p(0, 7.45, 1.3 + 2.7), F.r(), CREAM, 0.0)
    for k in range(9):
        xx = -10.2 + 20.4 * k / 8
        mb.box((0.34, 0.5, 5.4), F.p(xx, 7.4, 1.3 + 2.7), F.r(), WDARK, 0.0)
    for zz in (3.1, 5.0, 6.7):
        mb.beam(F.p(-10.2, 7.4, zz), F.p(10.2, 7.4, zz), 0.5, 0.26, WDARK, 0.0)
    col_box("DB_HubMarket", (20.6, 0.9, 7.2), F.p(0, 7.45, 3.6), F.r())
    # estantes com potes e caixas (dos dois lados do NPC) + expositor de bastoes no meio
    for sx in (-1, 1):
        xa, xb = sx * 3.4, sx * 8.9
        for xx in (xa, xb):
            mb.box((0.4, 1.2, 4.6), F.p(xx, 6.5, 2.3), F.r(), WDARK, 0.0)
        for zz in (1.1, 2.6, 4.1):
            mb.box((abs(xb - xa) + 0.4, 1.3, 0.2), F.p((xa + xb) / 2, 6.5, zz), F.r(), DECK, 0.0)
        for k in range(4):
            xx = xa + (xb - xa) * (k + 0.5) / 4
            VG.jar(mb, *F.p(xx, 6.45, 0)[:2], H + 1.2, 0.62 + 0.08 * (k % 2), (BLUE, ORANGE, WHITE, BLUE)[k])
        for k in range(3):
            xx = xa + (xb - xa) * (k + 0.5) / 3
            mb.box((1.2, 0.9, 0.9), F.p(xx, 6.45, 2.7 + 0.45), F.r(0, 0, rng.uniform(-0.2, 0.2)), CANVAS, 0.0)
            mb.box((1.3, 0.2, 0.2), F.p(xx, 6.0, 2.7 + 0.65), F.r(), CLOTH, 0.0)
        mb.cyl(0.45, 1.4, F.p((xa + xb) / 2 + sx * 0.8, 6.45, 4.2 + 0.45), (0, math.pi / 2, 0), CLOTH, 8, bevel=0.0)
        mb.cyl(0.45, 1.4, F.p((xa + xb) / 2 - sx * 0.9, 6.45, 4.2 + 0.45), (0, math.pi / 2, 0), CANVAS, 8,
               bevel=0.0)
    col_box("DB_HubMarket", (18.4, 1.6, 4.8), F.p(0, 6.5, 2.4), F.r())
    for xx in (-1.6, 1.6):
        mb.box((0.4, 0.5, 5.2), F.p(xx, 6.6, 2.6), F.r(), RED, 0.0)
    for zz in (1.4, 4.4):
        mb.beam(F.p(-1.8, 6.4, zz), F.p(1.8, 6.4, zz), 0.35, 0.35, RED, 0.0)
    for k in range(5):
        xx = -1.1 + 0.55 * k
        mb.rod(F.p(xx, 6.25, 0.2), F.p(xx + 0.15, 6.35, 5.9), 0.13, WDARK, 6)
        mb.cyl(0.2, 0.5, F.p(xx + 0.16, 6.35, 6.15), (0, 0, 0), GOLD, 6, r2=0.04, bevel=0.0)
    # balcao (frente do NPC): corpo escuro, painel laqueado, filete dourado, tampo de madeira mel + mercadoria
    mb.box((11.0, 1.3, 2.75), F.p(0, -1.2, 1.375), F.r(), WDARK, 0.0)
    mb.box((10.4, 0.2, 2.0), F.p(0, -1.9, 1.3), F.r(), RED, 0.0)
    mb.box((10.8, 0.26, 0.26), F.p(0, -1.95, 2.5), F.r(), GOLD, 0.0)
    mb.box((11.6, 1.9, 0.3), F.p(0, -1.2, 2.9), F.r(), DECK, 0.0)
    for gx, m_, s in ((-4.2, BLUE, 0.7), (-3.2, ORANGE, 0.55), (3.6, WHITE, 0.62)):
        VG.jar(mb, *F.p(gx, -1.1, 0)[:2], H + 3.05, s, m_)
    for k in range(3):
        mb.box((1.4, 1.0, 0.36), F.p(-0.9 + 0.2 * k, -1.0, 3.05 + 0.18 + 0.36 * k), F.r(0, 0, 0.12 * k),
               (CLOTH, CANVAS, CLOTH)[k], 0.0)
    mb.cyl(0.7, 0.12, F.p(1.6, -1.2, 3.12), (0, 0, 0), GOLD, 10, bevel=0.0)
    mb.rod(F.p(1.6, -1.2, 3.1), F.p(1.6, -1.2, 4.1), 0.09, GOLD, 4)
    col_box("DB_HubMarket", (11.6, 1.9, 3.2), F.p(0, -1.2, 1.6), F.r())
    # lanternas de papel sob o beiral da frente + lanternas de poste na entrada
    for xx in (-7.4, -2.4, 2.4, 7.4):
        VG.red_lantern(mb, F.p(xx, -7.25, 8.3), r=0.72, h=1.25, hang=0.45)
        mb.beam(F.p(xx, -5.9, 8.35), F.p(xx, -7.4, 8.35), 0.25, 0.25, WDARK, 0.0)
    for sx in (-1, 1):
        VG.post_lantern(mb, *F.p(sx * 4.3, -13.3)[:2], H, 0.0, h=4.2)
        col_box("DB_HubMarket", (1.6, 1.6, 7.0), F.p(sx * 4.3, -13.3, 3.5), F.r())
    # barracas laterais de frente para o passeio (esquerda: comida | direita: tecidos e potes)
    _stall(mb, *F.p(-8.9, -10.6)[:2], -math.pi / 2, rng, "food")
    _stall(mb, *F.p(8.9, -10.6)[:2], math.pi / 2, rng, "cloth")
    mb.finish()
    mk("NPC_Market", tuple(F.p(0, 1.6, 0)), (0, 0, math.pi), 1.5, "SPHERE",
       props={"floor": H, "note": "atras do balcao do pavilhao marcial, olhando para a entrada (sul)"})
    mk("PLAYER_INTERACT_Market", tuple(F.p(0, -3.4, 0)), (0, 0, 0), 1.5, "SPHERE",
       props={"floor": H, "note": "na frente do balcao, sob o beiral"})


# ------------------------------------------------------------------ oficina (hangar Capsule entravel)
def _ws_mat(i, side, zc, ang):
    if zc > WS_WH + 0.5 and abs(ang - 90.0) < 14.0:
        return GLASS                                   # claraboia na cumeeira
    if side == "in":
        return WHITE
    return BLUE if zc > WS_WH + 0.01 else WHITE


def workshop():
    F = WS_F
    cx, cy = WS[0], WS[1]
    mb = K.CMB("DB_Hub_Workshop", COLL, rng=random.Random(5104))
    RO, RI, WH = WS_RO, WS_RI, WS_WH
    VG.vault_shell(mb, F, RO, RI, WH, WS_XA, WS_XB, _ws_mat, NAVY, k=14)
    # costelas brancas sobre a abobada + pilastras azul-marinho nas paredes
    for xr in (WS_XA + 0.45, -6.0, -1.0, 4.0, WS_XB - 0.45):
        w = 0.9 if xr in (WS_XA + 0.45, WS_XB - 0.45) else 0.7
        pts = [F.p(xr, (RO + 0.16) * math.cos(math.pi * (1 - j / 14)), WH + (RO + 0.16) * math.sin(math.pi * (1 - j / 14)))
               for j in range(15)]
        for a, b in zip(pts, pts[1:]):
            mb.beam(a, b, w, 0.42, WHITE, 0.0)
        for sg in (-1, 1):
            mb.box((w, 0.4, WH - 0.4), F.p(xr, sg * (RO + 0.14), (WH - 0.4) / 2 + 0.2), F.r(), NAVY, 0.0)
    # faixa azul no alto da parede + rodape azul-marinho (as duas laterais)
    for sg in (-1, 1):
        mb.box((WS_XB - WS_XA, 0.34, 1.2), F.p((WS_XA + WS_XB) / 2, sg * (RO + 0.1), WH - 0.9), F.r(), BLUE, 0.0)
        mb.box((WS_XB - WS_XA, 0.3, 0.9), F.p((WS_XA + WS_XB) / 2, sg * (RO + 0.08), 0.45), F.r(), NAVY, 0.0)
    # empenas: frente com o portao em arco (vao 10 x 12) e fundo com janela redonda
    VG.end_wall(mb, F, WS_XW[0], WS_XW[1], RI, WH, WHITE, door=WS_DOOR, k=20)
    VG.end_wall(mb, F, WS_XE[0], WS_XE[1], RI, WH, WHITE, None, k=16)
    dw, zs, fl = WS_DOOR
    xf = WS_XW[0] - 0.22
    # moldura azul-marinho do portao + linha de luz ciano no arco + faixas de alerta nos batentes
    outl = [(-(dw + 0.45), 0.0)] + [((dw + 0.45) * math.cos(math.pi * (1 - j / 12)), zs + (fl + 0.45) *
                                     math.sin(math.pi * (1 - j / 12))) for j in range(13)] + [(dw + 0.45, 0.0)]
    for (ua, za), (ub, zb) in zip(outl, outl[1:]):
        mb.beam(F.p(xf, ua, za), F.p(xf, ub, zb), 0.75, 0.9, NAVY, 0.0)
    arc = [((dw + 1.25) * math.cos(math.pi * (1 - j / 12)), zs + (fl + 1.25) * math.sin(math.pi * (1 - j / 12)))
           for j in range(13)]
    for (ua, za), (ub, zb) in zip(arc, arc[1:]):
        mb.beam(F.p(xf + 0.05, ua, za), F.p(xf + 0.05, ub, zb), 0.4, 0.34, CYAN, 0.0)
    for sg in (-1, 1):
        for k in range(5):
            mb.box((0.8, 0.28, 0.5), F.p((WS_XW[0] + WS_XW[1]) / 2, sg * (dw - 0.1), 0.45 + 0.5 * k), F.r(),
                   YELLOW if k % 2 == 0 else DARK, 0.0)
    VG.porthole(mb, F.p(WS_XW[0], 0.0, 15.0), (-1, 0, 0), 1.05, 0.8, n=16)
    VG.porthole(mb, F.p(WS_XE[1], 0.0, 12.6), (1, 0, 0), 1.8, 0.8, n=18)
    # faixas das laterais continuam nas empenas (frente: dos dois lados da moldura do portao)
    uf = dw + 0.9
    for sg in (-1, 1):
        um = sg * (uf + RI) / 2
        mb.box((0.34, RI - uf, 1.2), F.p(WS_XW[0] - 0.12, um, WH - 0.9), F.r(), BLUE, 0.0)
        mb.box((0.3, RI - uf, 0.9), F.p(WS_XW[0] - 0.1, um, 0.45), F.r(), NAVY, 0.0)
    mb.box((0.34, 2 * RI, 1.2), F.p(WS_XE[1] + 0.12, 0.0, WH - 0.9), F.r(), BLUE, 0.0)
    mb.box((0.3, 2 * RI, 0.9), F.p(WS_XE[1] + 0.1, 0.0, 0.45), F.r(), NAVY, 0.0)
    # fundo: gerador Capsule encostado na empena (ventoinhas, luz de estado) + dutos subindo para a abobada
    gx0, gx1, gy0, gy1 = WS_XE[1], WS_XE[1] + 2.5, -5.4, 0.6
    mb.box2(F.p(gx0, gy0, 0.0), F.p(gx1, gy1, 2.7), NAVY, 0.0)
    mb.box2(F.p(gx0, gy0 - 0.15, 2.7), F.p(gx1 + 0.15, gy1 + 0.15, 3.0), WHITE, 0.0)
    for gu in (gy0 + 1.5, gy1 - 1.5):
        mb.cyl(1.05, 0.3, F.p((gx0 + gx1) / 2 + 0.1, gu, 3.12), (0, 0, 0), STEEL, 14, bevel=0.0)
        mb.cyl(0.35, 0.35, F.p((gx0 + gx1) / 2 + 0.1, gu, 3.2), (0, 0, 0), DARK, 8, bevel=0.0)
    mb.box((0.14, 4.6, 0.3), F.p(gx1 + 0.02, (gy0 + gy1) / 2, 2.1), F.r(), CYAN, 0.0)
    for gu in (gy0 + 0.6, gy1 - 0.6):
        mb.box((0.14, 0.9, 1.2), F.p(gx1 + 0.02, gu, 1.0), F.r(), STEEL, 0.0)
    for gu in (-3.4, -2.5):
        mb.rod(F.p(gx0 + 0.35, gu, 3.0), F.p(gx0 + 0.35, gu, 10.8), 0.24, STEEL, 8)
        mb.cyl(0.36, 0.3, F.p(gx0 + 0.35, gu, 7.0), (0, 0, 0), NAVY, 8, bevel=0.0)
    col_box2("DB_HubWorkshop", F.p(gx0, gy0 - 0.2, -0.5), F.p(gx1 + 0.2, gy1 + 0.2, 3.4))
    # escotilhas das laterais (atravessam a parede: vidro por dentro)
    for xx in (-3.5, 1.5, 6.8):
        for sg in (-1, 1):
            VG.porthole(mb, F.p(xx, sg * RO, 5.4), (0, sg, 0), 1.2, RO - RI + 0.02, n=PORT_N)
    # porta de enrolar recolhida atras da verga + soleira
    K.cyl_axis(mb, 0.75, 10.8, F.p(WS_XW[1] + 0.55, 0.0, 11.7), (0, 1, 0), STEEL, 12)
    mb.box((1.2, 10.0, 0.08), F.p(WS_XW[0] - 0.2, 0.0, 0.03), F.r(), YELLOW, 0.0)
    # piso: concreto polido rente (topo H + 0,03 = piso de colisao; entra sob a parede da frente e forma a soleira do
    # vao), avental azul-marinho no portal (topo H + 0,02)
    mb.box2(F.p(WS_XW[0], -RI, -0.3), F.p(WS_XE[0], RI, 0.03), CONC, 0.0)
    mb.box2(F.p(WS_XA, -RO + 0.02, -0.3), F.p(WS_XW[0], RO - 0.02, 0.02), NAVY, 0.0)
    # ---- interior: plataforma do veiculo, veiculo capsula, talha
    px, py = WS_CAR
    mb.cyl(4.6, 0.1, (px, py, H + 0.02), (0, 0, 0), NAVY, 32, bevel=0.0)
    K.ring(mb, (px, py), 3.95, 4.3, H - 0.02, H + 0.1, CYAN, 32)
    mb.box((9.6, 0.36, 0.08), (px, py + 4.95, H + 0.03), (0, 0, 0), YELLOW, 0.0)
    yb0 = cy - WS_RI + 0.3
    mb.box((0.36, py + 5.1 - yb0, 0.08), (px + 4.95, (py + 5.1 + yb0) / 2, H + 0.03), (0, 0, 0), YELLOW, 0.0)
    VG.ellipsoid(mb, (px, py, H + 2.05), (3.7, 1.85, 1.05), 0.0, YELLOW)
    VG.ellipsoid(mb, (px, py, H + 1.8), (3.8, 1.93, 0.3), 0.0, NAVY)
    VG.ellipsoid(mb, (px - 0.8, py, H + 2.7), (1.8, 1.35, 1.1), 0.0, GLASS)
    mb.box((1.5, 0.3, 1.0), (px + 2.8, py, H + 3.2), (0, -0.4, 0), BLUE, 0.0)
    for sg in (-1, 1):
        mb.box((1.3, 0.9, 0.24), (px + 2.2, py + sg * 2.05, H + 1.85), (sg * 0.15, 0, 0), NAVY, 0.0)
        VG.ellipsoid(mb, (px - 3.45, py + sg * 0.95, H + 2.05), (0.3, 0.42, 0.26), 0.0, LAMP, sub=1)
        for su in (-1, 1):
            mb.cyl(0.7, 0.45, (px + su * 2.1, py + sg * 1.45, H + 0.78), (0, 0, 0), DARK, 12, bevel=0.0)
            mb.cyl(0.52, 0.12, (px + su * 2.1, py + sg * 1.45, H + 0.5), (0, 0, 0), CYAN, 12, bevel=0.0)
    mb.box((1.1, 1.5, 0.5), (px + 3.5, py, H + 2.1), (0, 0, 0), NAVY, 0.0)
    col_box("DB_HubWorkshop", (7.9, 4.1, 4.2), (px, py, H + 2.1))
    zg = 13.2
    ug = math.sqrt(RI * RI - (zg - WH) ** 2) - 0.1
    mb.beam((px, cy - ug, H + zg), (px, cy + ug, H + zg), 0.6, 0.9, STEEL, 0.0)
    mb.box((1.1, 1.3, 0.8), (px, py, H + zg - 0.8), (0, 0, 0), DARK, 0.0)
    mb.rod((px, py, H + zg - 1.2), (px, py, H + 8.4), 0.12, STEEL, 4)
    mb.box((0.7, 0.5, 0.5), (px, py, H + 8.3), (0, 0, 0), NAVY, 0.0)
    for a, b in (((px, py, H + 8.05), (px, py, H + 7.3)), ((px, py, H + 7.3), (px, py + 0.55, H + 7.05)),
                 ((px, py + 0.55, H + 7.05), (px, py + 0.75, H + 7.5))):
        mb.beam(a, b, 0.24, 0.24, YELLOW, 0.0)
    # ---- bancada (NPC atras), monitor, torno de bancada, caixa de ferramentas, capsulas
    bx = WS_BENCH_X
    by0, by1 = cy - 4.5, cy + 5.5
    bym = (by0 + by1) / 2
    mb.box((1.9, by1 - by0, 0.3), (bx, bym, H + 3.15), (0, 0, 0), DECK, 0.0)
    for yy in (by0 + 0.3, by1 - 0.3):
        for xx in (bx - 0.7, bx + 0.7):
            mb.box((0.35, 0.35, 3.0), (xx, yy, H + 1.5), (0, 0, 0), STEEL, 0.0)
    mb.box((1.6, by1 - by0 - 0.4, 0.2), (bx, bym, H + 0.9), (0, 0, 0), DARK, 0.0)
    for yy in (by0 + 1.4, by1 - 1.4):
        mb.box((1.7, 2.4, 2.5), (bx, yy, H + 1.55), (0, 0, 0), NAVY, 0.0)
        for zz in (0.8, 1.6, 2.4):
            mb.box((0.2, 1.4, 0.22), (bx - 0.9, yy, H + zz), (0, 0, 0), YELLOW, 0.0)
    mb.box((0.25, 2.6, 1.7), (bx + 0.5, cy + 3.1, H + 4.35), (0, 0, 0), NAVY, 0.0)
    mb.box((0.12, 2.3, 1.4), (bx + 0.36, cy + 3.1, H + 4.35), (0, 0, 0), CYAN, 0.0)
    mb.box((0.5, 0.8, 0.3), (bx + 0.5, cy + 3.1, H + 3.45), (0, 0, 0), DARK, 0.0)
    mb.box((0.8, 1.0, 0.7), (bx - 0.2, cy - 2.6, H + 3.65), (0, 0, 0), DARK, 0.0)
    mb.box((1.0, 0.36, 0.5), (bx - 0.2, cy - 2.6, H + 4.2), (0, 0, 0), STEEL, 0.0)
    mb.box((1.0, 1.8, 0.8), (bx + 0.1, cy - 0.4, H + 3.7), (0, 0, 0), RED, 0.0)
    mb.box((1.05, 1.85, 0.2), (bx + 0.1, cy - 0.4, H + 4.2), (0, 0, 0), DARK, 0.0)
    for k in range(3):
        c = Vector((bx - 0.35, cy + 0.9 + 0.55 * k, H + 3.52))
        VG.pill(mb, c, (1, 0, 0), 0.22, 0.28, WHITE, n=10, k_cap=2)
        K.cyl_axis(mb, 0.25, 0.14, c, (1, 0, 0), (NAVY, RED, NAVY)[k], 10)
    col_box("DB_HubWorkshop", (2.0, by1 - by0 + 0.2, 3.4), (bx, bym, H + 1.7))
    # painel de ferramentas na parede do fundo (atras do NPC)
    xw = cx + WS_XE[0] - 0.12
    mb.box((0.22, 10.0, 4.4), (xw, cy + 0.5, H + 6.0), (0, 0, 0), NAVY, 0.0)
    for k, yy in enumerate((cy - 3.6, cy - 1.8, cy + 0.2, cy + 2.2, cy + 4.1)):
        kind = k % 3
        if kind == 0:                       # chave de boca
            mb.box((0.25, 0.32, 2.2), (xw - 0.2, yy, H + 6.0), (0, 0, 0), STEEL, 0.0)
            mb.box((0.25, 0.9, 0.5), (xw - 0.2, yy, H + 7.25), (0, 0, 0), STEEL, 0.0)
            mb.box((0.25, 0.8, 0.45), (xw - 0.2, yy, H + 4.8), (0, 0, 0), STEEL, 0.0)
        elif kind == 1:                     # martelo
            mb.box((0.25, 0.3, 2.0), (xw - 0.2, yy, H + 5.9), (0, 0, 0), YELLOW, 0.0)
            mb.box((0.3, 1.2, 0.55), (xw - 0.22, yy, H + 7.05), (0, 0, 0), DARK, 0.0)
        else:                               # chaves de fenda
            for j in (-0.35, 0.35):
                mb.box((0.25, 0.36, 0.9), (xw - 0.2, yy + j, H + 6.9), (0, 0, 0), RED, 0.0)
                mb.box((0.22, 0.22, 1.2), (xw - 0.2, yy + j, H + 5.85), (0, 0, 0), STEEL, 0.0)
    # armario de ferramentas (parede norte), turbina em cavalete, tambores
    ax0 = cx - 6.8
    mb.box((4.6, 1.7, 4.8), (ax0, cy + RI - 0.9, H + 2.4), (0, 0, 0), YELLOW, 0.0)
    for k in range(4):
        mb.box((4.2, 0.2, 0.85), (ax0, cy + RI - 1.8, H + 0.8 + 1.0 * k), (0, 0, 0), NAVY, 0.0)
        mb.box((1.4, 0.2, 0.22), (ax0, cy + RI - 1.92, H + 1.05 + 1.0 * k), (0, 0, 0), STEEL, 0.0)
    mb.box((4.8, 1.9, 0.3), (ax0, cy + RI - 0.9, H + 4.95), (0, 0, 0), NAVY, 0.0)
    col_box("DB_HubWorkshop", (4.8, 1.9, 5.1), (ax0, cy + RI - 0.9, H + 2.55))
    tx, ty = cx + 1.6, cy + RI - 1.6
    mb.box((2.6, 1.6, 1.2), (tx, ty, H + 0.6), (0, 0, 0), DARK, 0.0)
    K.cyl_axis(mb, 1.15, 2.6, (tx, ty, H + 2.35), (1, 0, 0), STEEL, 16)
    K.cyl_axis(mb, 1.25, 0.4, (tx - 0.9, ty, H + 2.35), (1, 0, 0), NAVY, 16)
    K.cyl_axis(mb, 0.8, 0.2, (tx - 1.35, ty, H + 2.35), (1, 0, 0), CYAN, 16)
    K.cyl_axis(mb, 1.22, 0.3, (tx + 0.6, ty, H + 2.35), (1, 0, 0), BLUE, 16)
    col_box("DB_HubWorkshop", (2.8, 2.6, 3.6), (tx, ty, H + 1.8))
    for (dx, dy) in ((7.6, RI - 1.3), (5.9, RI - 1.0)):
        mb.cyl(0.85, 2.2, (cx + dx, cy + dy, H + 1.1), (0, 0, 0), BLUE, 14, bevel=0.0)
        for zz in (0.35, 1.85):
            mb.cyl(0.9, 0.2, (cx + dx, cy + dy, H + zz), (0, 0, 0), WHITE, 14, bevel=0.0)
    col_box("DB_HubWorkshop", (3.6, 2.2, 2.4), (cx + 6.75, cy + RI - 1.15, H + 1.2))
    # luminarias (barras de luz na abobada, dos dois lados da claraboia)
    for sg in (-1, 1):
        u_ = sg * 3.3
        zl = WH + math.sqrt(RI * RI - u_ * u_) - 0.3
        mb.box((16.0, 0.36, 0.3), F.p(0.0, u_, zl), F.r(), CYAN, 0.0)
    # torreta do radar na cumeeira, perto do fundo (dentro do lote; o portao em arco fica limpo visto da praca):
    # soco azul-marinho assentado na abobada, tambor branco com faixa azul e escotilhas, cupula azul e mastro
    tx, ty, tr = WS_TOWER
    zb = H + WH + math.sqrt(RO * RO - (tr + 0.2) ** 2) - 0.08       # a abobada sob a borda do soco
    zr = H + WH + RO + 0.2
    # (casca aberta: o fundo fica entre as duas cascas da abobada e a tampa sob a cupula)
    prof = [(tr + 0.2, zb), (tr + 0.2, zr + 0.3), (tr, zr + 0.3), (tr, zr + 1.5), (tr + 0.14, zr + 1.5),
            (tr + 0.14, zr + 1.95), (tr, zr + 1.95), (tr, zr + 2.25)]
    VG.lathe_open(mb, (tx, ty), prof, WHITE, 20, smooth=[2], mats=[NAVY, NAVY, WHITE, BLUE, BLUE, BLUE, WHITE])
    for th in (0.0, 180.0):
        t = math.radians(th)
        VG.porthole(mb, (tx + tr * math.cos(t), ty + tr * math.sin(t), zr + 0.9), (math.cos(t), math.sin(t), 0),
                    0.42, 0.4, n=10)
    VG.dome_open(mb, (tx, ty), tr + 0.05, 1.15, zr + 2.2, 0.0, 76.0, 5, BLUE, 20)
    zt = zr + 2.2 + 1.15 * math.sin(math.radians(76.0))
    mb.cyl(0.6, 0.4, (tx, ty, zt + 0.1), (0, 0, 0), WHITE, 10, bevel=0.0)
    z_mast = zt + 2.0
    mb.rod((tx, ty, zt + 0.25), (tx, ty, z_mast), 0.2, STEEL, 6)
    mb.finish()
    # radar giratorio (VFX): prato + braco + receptor, pivo no topo do mastro
    pv = Vector((tx, ty, z_mast))
    vf = K.CMB("VFX_DBHUB_WorkshopRadar", VFXC, rng=random.Random(5105))
    vf.box((0.5, 0.5, 0.6), pv + Vector((0, 0, 0.3)), (0, 0, 0), NAVY, 0.0)
    dish(vf, pv + Vector((0.0, -0.9, 1.0)), (0.0, -0.75, 0.55), 1.6)
    vf.beam(pv + Vector((0, 0, 0.5)), pv + Vector((0.0, 0.9, 0.9)), 0.3, 0.3, STEEL, 0.0)
    K.sphere(vf, pv + Vector((0.0, 1.0, 1.0)), 0.3, CYAN, sub=0)
    ob = vf.finish()
    if ob:
        ob["pivot"] = (pv.x, pv.y, pv.z)
        ob["axis"] = (0.0, 0.0, 1.0)
        ob["rpm"] = 6.0
    # colisao: paredes da casca, fundo, frente com o vao do portao (e a verga acima do arco)
    A = "DB_HubWorkshop"
    col_box2(A, F.p(WS_XA, -RO - 0.1, -0.5), F.p(WS_XB, -RI, 18.0))
    col_box2(A, F.p(WS_XA, RI, -0.5), F.p(WS_XB, RO + 0.1, 18.0))
    col_box2(A, F.p(WS_XE[0], -RI, -0.5), F.p(WS_XE[1], RI, 18.0))
    col_box2(A, F.p(WS_XW[0], -RI, -0.5), F.p(WS_XW[1], -dw, 18.0))
    col_box2(A, F.p(WS_XW[0], dw, -0.5), F.p(WS_XW[1], RI, 18.0))
    col_box2(A, F.p(WS_XW[0], -dw, zs + fl), F.p(WS_XW[1], dw, 18.0))
    mk("NPC_Workshop", (WS_NPC[0], WS_NPC[1], H), (0, 0, math.pi / 2), 1.5, "SPHERE",
       props={"floor": H, "note": "atras da bancada da oficina, olhando para o portao (oeste)"})
    mk("PLAYER_INTERACT_Workshop", (WS_INTERACT[0], WS_INTERACT[1], H), (0, 0, -math.pi / 2), 1.5, "SPHERE",
       props={"floor": H, "note": "na frente da bancada, ao lado do veiculo capsula"})


# ------------------------------------------------------------------ pods (4 formas, sem porta)
# Pods NAO sao entraveis e nao tem vao nenhum (as escotilhas tem o aro macico atras do vidro): tambores e cupulas sao
# cascas ABERTAS (VG.lathe_open / VG.dome_open, so a face de fora) - a face de dentro, o fundo enterrado e a tampa
# escondida sob a cupula nunca aparecem e custavam ~40% dos tris. Parametros comuns:
#   z     piso (None = G, os 4 pods do chao; H nos quiosques da vila)
#   n     segmentos do torno; s escala (quiosques menores da vila)
#   lean  versao enxuta dos quiosques da vila: faixas como material (sem cinta saliente), 3 escotilhas, menos
#         montantes/balaustres, prato menor
#   area  area de colisao (DB_HubPod no chao, DB_HubPodN na vila)
PORT_N = 10


def pod_dome(mb, x, y, r, z=None, n=24, lean=False, area="DB_HubPod", face=-90.0):
    """domo Capsule: soco, tambor branco com faixa azul, cupula branca com capa azul, escotilhas, caixa tecnica
    azul-marinho (lado 'face'), mastro com orbe e prato"""
    z = G if z is None else z
    pn = PORT_N
    rw = r - 0.9
    if lean:
        prof = [(r - 0.2, z - 0.3), (r - 0.2, z + 0.4), (rw, z + 0.4), (rw, z + 2.5), (rw + 0.25, z + 2.5),
                (rw + 0.25, z + 3.3), (rw, z + 3.3), (rw, z + 3.65)]
        VG.lathe_open(mb, (x, y), prof, WHITE, n, mats=[BLOCK, BLOCK, WHITE, BLUE, BLUE, BLUE, WHITE], smooth=[2])
    else:
        prof = [(r - 0.2, z - 0.3), (r - 0.2, z + 0.35), (r - 0.55, z + 0.35), (r - 0.55, z + 0.7), (rw, z + 0.7),
                (rw, z + 2.5), (r - 0.65, z + 2.5), (r - 0.65, z + 3.3), (rw, z + 3.3), (rw, z + 3.65)]
        VG.lathe_open(mb, (x, y), prof, WHITE, n, mats=[BLOCK, BLOCK, NAVY, NAVY, WHITE, BLUE, BLUE, BLUE, WHITE],
                      smooth=[4])
    rd = r - 0.8
    bd = rd * 0.78
    E = K.Ell(x, y, z + 3.6, rd, bd)
    if lean:
        VG.dome_open(mb, (x, y), rd, bd, z + 3.6, 0.0, 60.0, 5, WHITE, n, mats=[WHITE, WHITE, WHITE, BLUE, WHITE])
    else:
        VG.dome_open(mb, (x, y), rd, bd, z + 3.6, 0.0, 60.0, 5, WHITE, n)
        K.rib_parallel(mb, E, 40.0, 0.0, 360.0, n, 0.8, 0.15, 0.25, BLUE)
    VG.dome_open(mb, (x, y), rd + 0.15, bd + 0.15, z + 3.6, 58.0, 88.0, 4, BLUE, n, lip=(rd, bd))
    angs = (face + 60.0, face + 180.0, face - 60.0) if lean else (-135.0, -45.0, 45.0, 135.0)
    for th in angs:
        t = math.radians(th)
        VG.porthole(mb, (x + rw * math.cos(t), y + rw * math.sin(t), z + 1.65), (math.cos(t), math.sin(t), 0),
                    0.7 if not lean else 0.62, 0.5, n=pn)
    t = math.radians(face)
    if lean:
        # unidade tecnica ALTA e larga com 2 ventoinhas (no quiosque pequeno o bloco baixo lia como portinhola)
        u = Vector((math.cos(t), math.sin(t), 0.0))
        v = Vector((-u.y, u.x, 0.0))
        c = Vector((x, y, z + 1.9)) + u * (rw + 0.25)
        mb.box((1.1, 1.6, 0.8), c, (0, 0, t), NAVY, 0.0)
        for sv in (-0.4, 0.4):
            K.cyl_axis(mb, 0.28, 0.12, c + u * 0.58 + v * sv, u, STEEL, 8)
    else:
        mb.box((1.4, 1.0, 1.3), (x + (r - 0.6) * math.cos(t), y + (r - 0.6) * math.sin(t), z + 1.4), (0, 0, t), NAVY,
               0.0)
    zt = z + 3.6 + (bd + 0.15) * math.sin(math.radians(88.0))
    mast(mb, x, y, zt - 0.1, zt + (2.6 if lean else 3.4), 0.36)
    nd = E.nrm(face - 60.0, 48.0)
    dish(mb, E.pt(face - 60.0, 48.0) + nd * 0.45, nd + Vector((0.0, 0.0, 0.5)), 0.9 if not lean else 0.8,
         n=10 if lean else 14)
    octo_col(area, x, y, r + 0.2, z - 0.5, z + 8.0)


def pod_standing(mb, x, y, r, z=None, n=24, s=1.0, lean=False, area="DB_HubPod", foot_m=STEEL):
    """capsula em pe sobre 3 pernas: bojo branco, anel de vidro com montantes, cupula azul com faixa branca, mastro"""
    z = G if z is None else z

    def Z(v):
        return z + v * s
    for k in range(3):
        t = math.radians(90.0 + 120.0 * k)
        d = Vector((math.cos(t), math.sin(t), 0.0))
        a = Vector((x, y, Z(2.6))) + d * (2.7 * s)
        b = Vector((x, y, z + 0.35)) + d * (4.1 * s)
        mb.beam(a, b, 0.62 * s, 0.62 * s, NAVY, 0.0)
        mb.cyl(0.8 * s, 0.35, (b.x, b.y, z + 0.175), (0, 0, 0), foot_m, 8 if lean else 10, bevel=0.0)
    if lean:
        pts = [(0.25, 1.05), (2.4, 1.3), (3.3, 2.2), (3.4, 3.0), (3.4, 4.75), (3.56, 4.85), (3.56, 6.45), (3.4, 6.55),
               (3.4, 7.35)]
        mats = [WHITE, WHITE, WHITE, WHITE, NAVY, GLASS, NAVY, WHITE]
        sm = [0, 1, 2, 3, 7]
    else:
        pts = [(0.25, 1.05), (2.0, 1.2), (2.9, 1.7), (3.35, 2.5), (3.4, 3.0), (3.4, 4.75), (3.58, 4.75), (3.58, 5.0),
               (3.4, 5.0), (3.4, 6.3), (3.58, 6.3), (3.58, 6.55), (3.4, 6.55), (3.4, 7.35)]
        mats = [WHITE, WHITE, WHITE, WHITE, WHITE, NAVY, NAVY, NAVY, GLASS, NAVY, NAVY, NAVY, WHITE]
        sm = [0, 1, 2, 3, 4, 12]
    VG.lathe_open(mb, (x, y), [(rr * s, Z(zz)) for rr, zz in pts], WHITE, n, mats=mats, smooth=sm)
    nm_, rm_ = (6, 3.62) if lean else (8, 3.45)
    for k in range(nm_):
        t = math.radians(180.0 / nm_ + 360.0 / nm_ * k)
        mb.box((0.3 * s, 0.38 * s, (1.6 if lean else 1.3) * s), (x + rm_ * s * math.cos(t), y + rm_ * s * math.sin(t),
                                                               Z(5.65)), (0, 0, t), NAVY, 0.0)
    E = K.Ell(x, y, Z(7.3), 3.45 * s, 2.6 * s)
    if lean:
        VG.dome_open(mb, (x, y), 3.45 * s, 2.6 * s, Z(7.3), 0.0, 80.0, 5, BLUE, n, mats=[WHITE, BLUE, BLUE, BLUE, BLUE])
    else:
        VG.dome_open(mb, (x, y), 3.45 * s, 2.6 * s, Z(7.3), 0.0, 80.0, 6, BLUE, n)
        K.rib_parallel(mb, E, 8.0, 0.0, 360.0, n, 0.6, 0.15, 0.25, WHITE)
    zt = Z(7.3) + 2.6 * s * math.sin(math.radians(80.0))
    mb.cyl(0.8 * s + 0.05, 0.4, (x, y, zt + 0.1), (0, 0, 0), WHITE, 10 if lean else 12, bevel=0.0)
    mast(mb, x, y, zt + 0.3, zt + 3.0 * s, 0.34 * s)
    mb.cyl(2.0 * s, 0.35, (x, y, z + 0.175), (0, 0, 0), BLOCK, 12 if lean else 16, bevel=0.0)
    octo_col(area, x, y, r, z - 0.5, z + 10.5 * s)


def pod_twin(mb, x, y, r, z=None, n=24, s=1.0, lean=False, area="DB_HubPod", yaw=0.0):
    """domo duplo: tambor + cupula azul grande e um domo branco pequeno ao lado, mastro com prato entre os dois"""
    z = G if z is None else z
    F = Frame(x, y, z, yaw)
    yd = math.degrees(yaw)
    pn = PORT_N

    def Z(v):
        return z + v * s
    mc, sc = F.p(-0.9 * s, 0.6 * s), F.p(2.6 * s, -1.9 * s)
    mx, my, mr = mc.x, mc.y, 3.5 * s
    sx, sy, sr = sc.x, sc.y, 2.0 * s
    prof = [(mr + 0.3, z - 0.3), (mr + 0.3, z + 0.35), (mr, z + 0.35), (mr, Z(1.9)), (mr + 0.22, Z(1.9)),
            (mr + 0.22, Z(2.5)), (mr, Z(2.5)), (mr, Z(2.75))]
    VG.lathe_open(mb, (mx, my), prof, WHITE, n, mats=[BLOCK, BLOCK, WHITE, BLUE, BLUE, BLUE, WHITE], smooth=[2])
    E = K.Ell(mx, my, Z(2.7), mr + 0.1, 2.9 * s)
    if lean:
        VG.dome_open(mb, (mx, my), mr + 0.1, 2.9 * s, Z(2.7), 0.0, 78.0, 6, BLUE, n,
                     mats=[BLUE, BLUE, BLUE, WHITE, BLUE, BLUE])
    else:
        VG.dome_open(mb, (mx, my), mr + 0.1, 2.9 * s, Z(2.7), 0.0, 78.0, 6, BLUE, n)
        K.rib_parallel(mb, E, 45.0, 0.0, 360.0, n, 0.6, 0.14, 0.25, WHITE)
    for th in (60.0, 150.0, 240.0):
        t = math.radians(th + yd)
        VG.porthole(mb, (mx + mr * math.cos(t), my + mr * math.sin(t), Z(1.2)), (math.cos(t), math.sin(t), 0),
                    0.62 * s, 0.5, n=pn)
    zt = Z(2.7) + 2.9 * s * math.sin(math.radians(78.0))
    mb.cyl(0.21 * (mr + 0.1) + 0.08, 0.4, (mx, my, zt + 0.1), (0, 0, 0), WHITE, 10 if lean else 12, bevel=0.0)
    ns_ = 14 if lean else 20
    mb.cyl(sr + 0.3, 0.45, (sx, sy, z + 0.225), (0, 0, 0), BLOCK, ns_, bevel=0.0)
    zs = z + 0.4 + 0.5 * s
    VG.lathe_open(mb, (sx, sy), [(sr, z + 0.4), (sr, zs + 0.05)], NAVY, ns_)
    E2 = K.Ell(sx, sy, zs, sr, sr * 0.95)
    VG.dome_open(mb, (sx, sy), sr, sr * 0.95, zs, 0.0, 88.0, 5 if lean else 6, WHITE, ns_)
    VG.porthole(mb, E2.pt(yd - 60.0, 32.0), E2.nrm(yd - 60.0, 32.0), 0.5 * s, 0.4, n=pn)
    # mastro com prato entre os dois domos
    q = F.p(1.45 * s, 0.75 * s)
    mb.rod((q.x, q.y, Z(2.6)), (q.x, q.y, Z(7.0)), 0.18, STEEL, 6)
    ca, sa = math.cos(yaw), math.sin(yaw)
    dish(mb, (q.x, q.y, Z(6.6)), (0.3 * ca + 0.7 * sa, 0.3 * sa - 0.7 * ca, 0.65), 1.2 * s, n=10 if lean else 14)
    octo_col(area, x, y, r + 0.6, z - 0.5, z + 7.2 * s)


def pod_beacon(mb, x, y, r, z=None, n=24, s=1.0, lean=False, area="DB_HubPod", face=-90.0):
    """farol Capsule: tambor com faixa azul, deque com balaustrada, lanterna de vidro com montantes, capuz azul"""
    z = G if z is None else z
    pn = PORT_N

    def Z(v):
        return z + v * s

    def R(v):
        return v * s
    rd = R(3.9)
    prof = [(rd + R(0.4), z - 0.3), (rd + R(0.4), z + 0.35), (rd, z + 0.35), (rd, Z(2.2)), (rd + R(0.25), Z(2.2)),
            (rd + R(0.25), Z(2.9)), (rd, Z(2.9)), (rd, Z(3.1))]
    VG.lathe_open(mb, (x, y), prof, WHITE, n, mats=[BLOCK, BLOCK, WHITE, BLUE, BLUE, BLUE, WHITE], smooth=[2])
    VG.lathe_open(mb, (x, y), [(rd, Z(3.1)), (R(4.2), Z(3.1)), (R(4.2), Z(3.4)), (R(2.4), Z(3.4))], WHITE, n)
    for k in range(3):
        t = math.radians(face + 120.0 * k)
        VG.porthole(mb, (x + rd * math.cos(t), y + rd * math.sin(t), Z(1.3)), (math.cos(t), math.sin(t), 0),
                    0.68 * s, 0.5, n=pn)
    nb = 8 if lean else 12
    for k in range(nb):
        t = math.radians(180.0 / nb + 360.0 / nb * k)
        mb.box((0.3, 0.3, 1.0 * s), (x + R(4.0) * math.cos(t), y + R(4.0) * math.sin(t), Z(3.9)), (0, 0, t), NAVY, 0.0)
    K.lathe(mb, (x, y), [(R(3.82), Z(4.35)), (R(4.16), Z(4.35)), (R(4.16), Z(4.6)), (R(3.82), Z(4.6))], BLUE, n)
    VG.lathe_open(mb, (x, y), [(R(2.4), Z(3.4)), (R(2.4), Z(5.0))], GLASS, n)
    nm_ = 6 if lean else 8
    for k in range(nm_):
        t = math.radians(180.0 / nm_ + 360.0 / nm_ * k)
        mb.box((0.3, 0.36, 1.6 * s), (x + R(2.45) * math.cos(t), y + R(2.45) * math.sin(t), Z(4.2)), (0, 0, t), NAVY,
               0.0)
    VG.lathe_open(mb, (x, y), [(R(2.4), Z(5.0)), (R(2.75), Z(5.0)), (R(2.75), Z(5.3)), (R(2.65), Z(5.3))], WHITE, n)
    VG.dome_open(mb, (x, y), R(2.7), R(2.0), Z(5.3), 0.0, 76.0, 5 if lean else 6, BLUE, n)
    zt = Z(5.3) + R(2.0) * math.sin(math.radians(76.0))
    mb.cyl(R(0.7) + 0.06, 0.4, (x, y, zt + 0.1), (0, 0, 0), WHITE, 10 if lean else 12, bevel=0.0)
    mast(mb, x, y, zt + 0.3, zt + R(3.6), 0.5 * s)
    octo_col(area, x, y, r + 0.1, z - 0.5, z + 7.6 * s)


def pods():
    """os 4 pods do chao, em volta do promenade (L.PODS)"""
    (p1, p2, p3, p4) = L.PODS
    mbs = K.CMB("DB_Hub_PodsSouth", COLL, rng=random.Random(5106))
    pod_dome(mbs, *p1)
    pod_standing(mbs, *p2)
    mbs.finish()
    mbw = K.CMB("DB_Hub_PodsSide", COLL, rng=random.Random(5107))
    pod_twin(mbw, *p3)
    pod_beacon(mbw, *p4)
    mbw.finish()


# ------------------------------------------------------------------ dojo (pavilhao marcial aberto no chao)
def dojo():
    cx, cy, _ = DOJO
    D = DOJO_D
    mb = K.CMB("DB_Hub_Dojo", COLL, rng=random.Random(5108))
    x0, x1, y0, y1 = cx - 12.0, cx + 12.0, cy - 9.0, cy + 9.0
    # plataforma: soco de arenito, cinta laqueada, assoalho de tabuas (topo = colisao = G + 1,6)
    mb.box2((x0, y0, G - 0.4), (x1, y1, D - 0.3), BLOCK, 0.0)
    mb.box2((x0 - 0.12, y0 - 0.12, D - 0.62), (x1 + 0.12, y1 + 0.12, D - 0.3), RED, 0.0)
    for k in range(12):
        yy = y0 + 18.0 * (k + 0.5) / 12
        mb.box((24.0, 1.5 - 0.12, 0.3), (cx, yy, D - 0.15), (0, 0, 0), DECK, 0.0)
    col_box2("DB_HubDojo", (x0, y0, G - 0.5), (x1, y1, D))
    # degraus (2 x 0,8, piso 1,7, largura 10) do lado oeste, com colisao em rampa (fm_parts.stairs)
    FP.stairs(mb, "DB_HubDojo", (x0 - 3.4, cy, G), 0.0, 10.0, 2, rise=0.8, tread=1.7, m=BLOCK, side_m=BLOCK,
              stringers=False, col=True)
    for sg in (-1, 1):
        yy = cy + sg * 5.6
        mb.box((3.5, 1.2, 1.9), (x0 - 1.75, yy, G + 0.95), (0, 0, 0), BLOCK, 0.0)
        VG.post_lantern(mb, x0 - 1.9, yy, G + 1.9, 0.0, h=1.6, s=0.85, post_m=RED, base_m=BLOCK)
        col_box("DB_HubDojo", (3.5, 1.2, 5.6), (x0 - 1.75, yy, G + 2.8))
    # tatame: lona clara com borda laqueada (0,05 acima do assoalho)
    mb.box((12.0, 8.0, 0.2), (cx + 0.5, cy - 1.0, D - 0.05), (0, 0, 0), CANVAS, 0.0)
    for sg in (-1, 1):
        mb.box((12.8, 0.4, 0.22), (cx + 0.5, cy - 1.0 + sg * 4.2, D - 0.04), (0, 0, 0), RED, 0.0)
        mb.box((0.4, 8.8, 0.22), (cx + 0.5 + sg * 6.2, cy - 1.0, D - 0.04), (0, 0, 0), RED, 0.0)
    # colunas vermelhas em base de pedra
    PXS = (x0 + 1.5, cx - 3.5, cx + 3.5, x1 - 1.5)
    PYS = (y0 + 1.5, y1 - 1.5)
    ZE1 = D + 8.1
    for px in PXS:
        for py in PYS:
            mb.cyl(0.95, 0.45, (px, py, D + 0.225), (0, 0, 0), BLOCK, 10, bevel=0.0)
            mb.cyl(0.6, 7.2, (px, py, D + 0.45 + 3.6), (0, 0, 0), RED, 12, bevel=0.0)
            for zz in (0.75, 6.4):
                mb.cyl(0.68, 0.3, (px, py, D + zz), (0, 0, 0), GOLD, 10, bevel=0.0)
            mb.box((1.6, 1.6, 0.45), (px, py, D + 7.65 + 0.225 - 0.225), (0, 0, 0), WDARK, 0.0)
            col_box("DB_HubDojo", (1.4, 1.4, 7.8), (px, py, D + 3.9))
    # arquitrave, friso vazado nos lados longos, frechal
    for py in PYS:
        mb.beam((PXS[0] - 0.6, py, D + 7.1), (PXS[-1] + 0.6, py, D + 7.1), 0.75, 0.95, RED, 0.0)
        mb.beam((PXS[0] - 0.4, py, D + 6.5), (PXS[-1] + 0.4, py, D + 6.5), 0.55, 0.22, GOLD, 0.0)
        mb.beam((PXS[0] - 0.9, py, D + 8.0), (PXS[-1] + 0.9, py, D + 8.0), 0.62, 0.55, RED, 0.0)
        for a, b in zip(PXS, PXS[1:]):
            n_ = 7
            for k in range(1, n_):
                xx = a + (b - a) * k / n_
                mb.box((0.24, 0.3, 0.8), (xx, py, D + 6.0), (0, 0, 0), WDARK, 0.0)
            mb.beam((a + 0.6, py, D + 5.55), (b - 0.6, py, D + 5.55), 0.3, 0.26, WDARK, 0.0)
    for px in (PXS[0], PXS[-1]):
        mb.beam((px, PYS[0] - 0.6, D + 7.1), (px, PYS[1] + 0.6, D + 7.1), 0.75, 0.95, RED, 0.0)
        mb.beam((px, PYS[0] - 0.4, D + 6.5), (px, PYS[1] + 0.4, D + 6.5), 0.55, 0.22, GOLD, 0.0)
        mb.beam((px, PYS[0] - 0.9, D + 8.0), (px, PYS[1] + 0.9, D + 8.0), 0.62, 0.55, RED, 0.0)
    # telhado duplo: agua de baixo + clerestorio + agua de cima
    VG.hip_roof(mb, cx, cy, 0.0, 14.0, 10.4, ZE1, 3.8, lift=1.7, flare=1.3, ns=8, nu=5)
    hxc, hyc = 7.6, 4.4
    zc0, zc1 = D + 9.2, D + 12.9
    # clerestorio: parede de madeira escura com janelas de trelica (papel creme atras das ripas laqueadas);
    # nada de painel liso claro (lia como placa)
    for sg in (-1, 1):
        mb.box((2 * hxc, 0.4, zc1 - zc0), (cx, cy + sg * hyc, (zc0 + zc1) / 2), (0, 0, 0), WDARK, 0.0)
        mb.box((0.4, 2 * hyc, zc1 - zc0), (cx + sg * hxc, cy, (zc0 + zc1) / 2), (0, 0, 0), WDARK, 0.0)
        wins = [((cx - 4.6 + 4.6 * k, cy + sg * hyc), 0.0) for k in range(3)] + \
               [((cx + sg * hxc, cy + dd), math.pi / 2) for dd in (-2.0, 2.0)]
        for (wx, wy), rz in wins:
            ca, sa = math.cos(rz), math.sin(rz)
            nx, ny = (0.0, sg) if rz == 0.0 else (sg, 0.0)
            mb.box((2.8, 0.44, 2.1), (wx, wy, D + 11.05), (0, 0, rz), CREAM, 0.0)
            mb.box((3.2, 0.5, 0.3), (wx, wy, D + 12.15), (0, 0, rz), RED, 0.0)
            mb.box((3.2, 0.5, 0.3), (wx, wy, D + 9.95), (0, 0, rz), RED, 0.0)
            for j in range(4):
                o = -1.05 + 0.7 * j
                mb.box((0.22, 0.5, 2.1), (wx + ca * o + nx * 0.06, wy + sa * o + ny * 0.06, D + 11.05), (0, 0, rz),
                       RED, 0.0)
            mb.box((2.8, 0.5, 0.2), (wx + nx * 0.06, wy + ny * 0.06, D + 11.05), (0, 0, rz), RED, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.75, 0.75, D + 13.5 - zc0), (cx + sx * hxc, cy + sy * hyc, (zc0 + D + 13.5) / 2), (0, 0, 0), RED,
                   0.0)
    for sg in (-1, 1):
        mb.beam((cx - hxc - 0.4, cy + sg * hyc, zc1 - 0.2), (cx + hxc + 0.4, cy + sg * hyc, zc1 - 0.2), 0.6, 0.6, RED,
                0.0)
        mb.beam((cx + sg * hxc, cy - hyc - 0.4, zc1 - 0.2), (cx + sg * hxc, cy + hyc + 0.4, zc1 - 0.2), 0.6, 0.6, RED,
                0.0)
    VG.hip_roof(mb, cx, cy, 0.0, 9.8, 6.6, D + 12.5, 4.2, lift=1.5, flare=1.1, ns=7, nu=5, rib_step=1.7)
    # bonecos de treino (lado norte, de frente para o tatame); a colisao cobre o tronco E os bracos/perna, que
    # avancam 2,2 para o tatame (quem chega no boneco para nos bracos, nao os atravessa)
    for dx in (-6.0, 0.0, 6.0):
        VG.wing_dummy(mb, cx + dx, y1 - 4.4, D, math.pi)
        col_box("DB_HubDojo", (1.9, 3.3, 5.6), (cx + dx, y1 - 4.4 - 0.7, D + 2.8))
    # biombo de fundo (leste) com janela lua + gongo na frente dele
    xs = PXS[-1]
    mb.box((0.3, 2 * 7.5 - 1.2, 6.0), (xs, cy, D + 3.35), (0, 0, 0), CREAM, 0.0)
    for zz in (0.5, 6.35):
        mb.beam((xs, cy - 7.5, D + zz), (xs, cy + 7.5, D + zz), 0.5, 0.5, RED, 0.0)
    for yy in (cy - 3.8, cy + 3.8):
        mb.box((0.5, 0.5, 6.0), (xs, yy, D + 3.4), (0, 0, 0), RED, 0.0)
    K.torus(mb, (xs - 0.1, cy, D + 3.5), 1.5, 0.22, RED, axis=(1, 0, 0), n=20, k=5)
    for j in (-0.75, 0.0, 0.75):
        L_ = math.sqrt(max(0.0, 1.45 ** 2 - j * j))
        mb.box((0.34, 0.2, 2 * L_), (xs - 0.1, cy + j, D + 3.5), (0, 0, 0), WDARK, 0.0)
        mb.box((0.34, 2 * L_, 0.2), (xs - 0.1, cy, D + 3.5 + j), (0, 0, 0), WDARK, 0.0)
    col_box("DB_HubDojo", (0.8, 15.0, 6.8), (xs, cy, D + 3.4))
    gx, gy = xs - 2.0, cy - 4.4
    for sg in (-1, 1):
        mb.box((0.5, 0.5, 6.4), (gx, gy + sg * 2.6, D + 3.2), (0, 0, 0), RED, 0.0)
        mb.box((1.8, 0.8, 0.5), (gx, gy + sg * 2.6, D + 0.25), (0, 0, 0), WDARK, 0.0)
        mb.beam((gx, gy + sg * 2.6, D + 6.2), (gx, gy + sg * 3.5, D + 6.9), 0.45, 0.45, RED, 0.0)
        mb.cyl(0.2, 0.5, (gx, gy + sg * 3.55, D + 7.1), (0, 0, 0), GOLD, 6, r2=0.05, bevel=0.0)
    mb.beam((gx, gy - 2.9, D + 6.25), (gx, gy + 2.9, D + 6.25), 0.55, 0.6, RED, 0.0)
    K.cyl_axis(mb, 2.0, 0.34, (gx, gy, D + 3.6), (1, 0, 0), GOLD, 24)
    K.cyl_axis(mb, 0.65, 0.5, (gx - 0.1, gy, D + 3.6), (1, 0, 0), "Metal_Brass", 16)
    K.cyl_axis(mb, 1.55, 0.4, (gx - 0.04, gy, D + 3.6), (1, 0, 0), "Metal_Brass", 24)
    for sg in (-1, 1):
        mb.rod((gx, gy + sg * 1.2, D + 6.0), (gx, gy + sg * 1.0, D + 5.4), 0.1, "Rope", 4)
    # malho encostado no montante do gongo, cabeca no chao (tudo dentro da colisao do gongo, alargada 0,6 em -x)
    mb.rod((gx - 1.1, gy - 1.95, D + 0.5), (gx - 0.37, gy - 2.6, D + 2.9), 0.12, WDARK, 5)
    K.sphere(mb, (gx - 1.12, gy - 1.93, D + 0.36), 0.36, CLOTH, sub=2)
    col_box("DB_HubDojo", (2.5, 6.4, 6.8), (gx - 0.3, gy, D + 3.4))
    # expositor de armas (lado sul): bastoes e lancas
    rx, ry = cx - 1.0, y0 + 2.6
    for sg in (-1, 1):
        mb.box((0.45, 0.6, 4.4), (rx + sg * 2.4, ry, D + 2.2), (0, 0, 0), RED, 0.0)
    for zz in (1.2, 4.1):
        mb.beam((rx - 2.6, ry, D + zz), (rx + 2.6, ry, D + zz), 0.4, 0.4, WDARK, 0.0)
    for k in range(7):
        xx = rx - 1.8 + 0.6 * k
        mb.rod((xx, ry - 0.25, D + 0.15), (xx + 0.12, ry + 0.2, D + 5.6), 0.13, WDARK, 6)
        if k % 3 == 1:
            mb.cyl(0.24, 0.8, (xx + 0.13, ry + 0.22, D + 5.95), (0, 0, 0), DARK, 6, r2=0.03, bevel=0.0)
    col_box("DB_HubDojo", (5.6, 1.2, 5.0), (rx, ry, D + 2.5))
    # estandartes nas colunas de canto da frente (oeste; a ponta da flamula desce ate D + 1,7, por isso cada um tem a
    # sua caixa de colisao colada na da coluna) e lanternas penduradas
    for py in PYS:
        FP.banner(mb, (PXS[0] - 0.75, py, D + 6.6), -math.pi / 2, w=1.9, h=3.8, cloth=CLOTH, trim=GOLD, emblem="")
        col_box2("DB_HubDojo", (PXS[0] - 1.05, py - 1.1, D), (PXS[0] - 0.5, py + 1.1, D + 6.8))
    for px in (cx - 7.0, cx + 7.0):
        for py, off in ((y0, -0.9), (y1, 0.9)):
            VG.red_lantern(mb, (px, py + off, ZE1 - 0.3), r=0.7, h=1.2, hang=0.5)
    for px in (cx - 4.0, cx + 4.0):
        VG.red_lantern(mb, (px, cy - 1.0, D + 10.6), r=0.8, h=1.3, hang=2.4)
    mb.finish()


# ------------------------------------------------------------------ vila: quiosques Capsule + barracas de toldo
# Enchem as bolsas de areia do terraco HUB (critica da concept: a vila tech lia vazia perto da concept, que tem um cacho
# de domos brancos/azuis, barracas com toldo e lanternas). Quiosques NAO entraveis (sem porta nenhuma, so escotilhas,
# antenas e pratos) das 4 familias dos pods, menores e enxutos; 2 barracas ABERTAS de toldo laranja. As posicoes sairam
# de um mapa de ocupacao por raios da ilha montada (visual + colisao) e ficam fora dos lotes, das ruas/calcadas do
# db_terrain, da faixa de rua y 76-88, das arvores/canteiros do db_veg, dos props e das rotas do db_qa (folga >= raio +
# 2,6). Tudo num objeto so (1 MeshPart por material), junto com os postes Capsule e a moto flutuante.
HUB_KIOSKS = [
    ("dome", -67.0, 116.0, 3.6, dict(face=-45.0)),            # entre a casa A e a barraca leste do mercado
    ("twin", -45.0, 123.0, 4.0, dict(s=0.8, yaw=0.5)),        # atras da casa A, a oeste da escadaria do Capsule
    ("standing", -82.0, 172.0, 4.0, dict(s=0.8)),             # norte do mercado, pe do terraco do Capsule
    ("dome", -102.5, 168.5, 3.8, dict(face=90.0)),            # ao norte da torre de comunicacao
    ("beacon", 111.0, 113.0, 3.7, dict(s=0.85, face=180.0)),  # entre a casa B e o mirante
]
HUB_STALLS = [(-23.5, 115.0, -math.pi / 2, "food"),        # oeste da escadaria do Capsule, balcao para a praca
              (100.0, 123.0, math.pi / 2, "capsule")]       # entre a casa B e o mirante, balcao para a rua do mirante
KIOSK_N = 16                        # segmentos do torno dos quiosques (raio 3-4)
AW_HX, AW_HY = 2.8, 1.8             # meia-planta da barraca de toldo (colisao 6,0 x 4,0)
AW_ZB, AW_ZF = 6.95, 6.25           # toldo: cota no fundo (y -AW_HY - 0,1) e na frente (y AW_HY + 0,7)


def _aw_z(y):
    """cota do plano do toldo no y local"""
    yb, yf = -AW_HY - 0.1, AW_HY + 0.7
    return AW_ZB + (y - yb) * (AW_ZF - AW_ZB) / (yf - yb)


def awning_stall(mb, x, y, yaw, goods="food", area="DB_HubPodN"):
    """barraca ABERTA de toldo: 4 postes laqueados em sapatas de pedra, toldo listrado laranja/branco caindo para a
    frente (+y local) com sanefa recortada (ponto mais baixo H + 5,68: fora da colisao, acima da cabeca), balcao
    escuro com frente laqueada, filete dourado e tampo branco, mercadoria, caixotes (madeira + caixa Capsule) e 1
    lanterna de papel pendurada numa travessa DENTRO da planta da colisao"""
    F = Frame(x, y, H, yaw)
    hx, hy = AW_HX, AW_HY
    yb, yf = -hy - 0.1, hy + 0.7
    px, py = hx - 0.2, hy - 0.25
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = _aw_z(sy * py) - 0.08
            mb.box((0.36, 0.36, h), F.p(sx * px, sy * py, h / 2), F.r(), RED, 0.0)
            mb.box((0.7, 0.7, 0.3), F.p(sx * px, sy * py, 0.15), F.r(), BLOCK, 0.0)
        mb.beam(F.p(sx * px, -py - 0.2, _aw_z(-py) - 0.25), F.p(sx * px, py + 0.2, _aw_z(py) - 0.25), 0.3, 0.3, RED,
                0.0)
    for yy in (-py, py):
        mb.beam(F.p(-px - 0.2, yy, _aw_z(yy) - 0.25), F.p(px + 0.2, yy, _aw_z(yy) - 0.25), 0.3, 0.3, RED, 0.0)
    ly = -0.3                                          # travessa da lanterna
    mb.beam(F.p(-px, ly, _aw_z(ly) - 0.22), F.p(px, ly, _aw_z(ly) - 0.22), 0.26, 0.26, WDARK, 0.0)
    mb.beam(F.p(-px, -py, 1.2), F.p(px, -py, 1.2), 0.26, 0.26, RED, 0.0)      # guarda baixa no fundo (aberto)
    # toldo listrado (6 faixas) + sanefa recortada na frente
    ln = math.hypot(yf - yb, AW_ZF - AW_ZB)
    pitch = math.atan2(AW_ZF - AW_ZB, yf - yb)
    zc = (AW_ZB + AW_ZF) / 2.0
    for i in range(6):
        mb.box((1.0, ln, 0.14), F.p(-2.5 + i, (yb + yf) / 2.0, zc), F.r(pitch, 0, 0),
               ORANGE if i % 2 == 0 else WHITE, 0.0)
    for i in range(6):
        mb.box((0.86, 0.1, 0.5), F.p(-2.5 + i, yf - 0.03, AW_ZF - 0.32), F.r(), ORANGE if i % 2 == 0 else WHITE, 0.0)
    # balcao
    mb.box((5.0, 1.0, 2.4), F.p(0, hy - 0.65, 1.2), F.r(), WDARK, 0.0)
    mb.box((4.6, 0.12, 1.5), F.p(0, hy - 0.1, 1.25), F.r(), RED, 0.0)
    mb.box((4.8, 0.14, 0.14), F.p(0, hy - 0.1, 2.15), F.r(), GOLD, 0.0)
    mb.box((5.3, 1.3, 0.2), F.p(0, hy - 0.65, 2.5), F.r(), WHITE, 0.0)
    zt = 2.6
    if goods == "food":
        # 2 cestos de bambu no vapor empilhados com tampa + gamela de laranjas + pote
        p = F.p(-1.6, hy - 0.65, zt)
        for k in range(2):
            mb.cyl(0.46, 0.3, (p.x, p.y, p.z + 0.15 + 0.32 * k), (0, 0, 0), WDARK, 10, bevel=0.0)
        mb.cyl(0.47, 0.34, (p.x, p.y, p.z + 0.64 + 0.17), (0, 0, 0), WDARK, 10, r2=0.14, bevel=0.0)
        p = F.p(0.3, hy - 0.65, zt)
        K.lathe(mb, (p.x, p.y), [(0.3, p.z), (0.62, p.z + 0.14), (0.68, p.z + 0.36), (0.56, p.z + 0.36),
                                 (0.3, p.z + 0.16)], WDARK, 10)
        for j in range(3):
            a = j * 2.0 * math.pi / 3 + 0.4
            K.sphere(mb, (p.x + 0.24 * math.cos(a), p.y + 0.24 * math.sin(a), p.z + 0.5), 0.25, ORANGE, sub=1)
        K.sphere(mb, (p.x, p.y, p.z + 0.76), 0.25, ORANGE, sub=1)
        q = F.p(1.8, hy - 0.7, 0.0)
        VG.jar(mb, q.x, q.y, H + zt, 0.55, BLUE)
    else:
        # capsulas de brinde deitadas numa bandeja (meio branco, meio colorido) + caixa Capsule pequena
        mb.box((2.6, 0.9, 0.12), F.p(-0.9, hy - 0.65, zt + 0.06), F.r(), NAVY, 0.0)
        ax = F.p(0.0, 1.0) - F.p(0.0, 0.0)
        for k in range(4):
            c = F.p(-1.95 + 0.7 * k, hy - 0.65, zt + 0.36)
            K.cyl_axis(mb, 0.24, 0.42, c - ax * 0.2, ax, WHITE, 8)
            K.cyl_axis(mb, 0.24, 0.42, c + ax * 0.2, ax, (BLUE, RED, BLUE, RED)[k], 8)
        mb.box((1.0, 0.8, 0.8), F.p(1.6, hy - 0.65, zt + 0.4), F.r(0, 0, 0.15), WHITE, 0.0)
        mb.box((1.04, 0.84, 0.24), F.p(1.6, hy - 0.65, zt + 0.4), F.r(0, 0, 0.15), BLUE, 0.0)
    # caixotes atras do balcao (madeira empilhada | caixa Capsule branca com cinta azul)
    mb.box((1.2, 1.1, 1.1), F.p(-1.85, -1.0, 0.55), F.r(0, 0, 0.1), WDARK, 0.0)
    mb.box((0.95, 0.9, 0.85), F.p(-1.8, -1.0, 1.1 + 0.425), F.r(0, 0, -0.2), WDARK, 0.0)
    mb.box((1.1, 1.0, 1.0), F.p(1.9, -1.05, 0.5), F.r(0, 0, -0.1), WHITE, 0.0)
    mb.box((1.14, 1.04, 0.28), F.p(1.9, -1.05, 0.62), F.r(0, 0, -0.1), BLUE, 0.0)
    # lanterna de papel na travessa (corpo ~H + 5,3, borla ate ~H + 4,0: dentro da planta da colisao)
    top = _aw_z(ly) - 0.35
    VG.red_lantern(mb, F.p(0.0, ly, top), r=0.55, h=0.9, hang=0.4)
    col_box(area, (2 * hx + 0.2, 2 * hy + 0.2, 7.0), F.p(0, 0, 3.5), F.r())
    # lanterna marcial de poste na quina da frente (a mesma do mercado, menor), com a sua caixa de colisao
    q = F.p(hx + 1.2, hy + 0.2)
    VG.post_lantern(mb, q.x, q.y, H, yaw, h=3.4, s=0.85)
    col_box(area, (1.4, 1.4, 6.2), (q.x, q.y, H + 3.1), F.r())


def pods_north(mb):
    """quiosques Capsule e barracas de toldo nas bolsas do terraco da vila"""
    fns = {"dome": pod_dome, "twin": pod_twin, "standing": pod_standing, "beacon": pod_beacon}
    for kind, x, y, r, kw in HUB_KIOSKS:
        fns[kind](mb, x, y, r, z=H, n=KIOSK_N, lean=True, area="DB_HubPodN", **kw)
    for x, y, yaw, goods in HUB_STALLS:
        awning_stall(mb, x, y, yaw, goods)


# ------------------------------------------------------------------ mobiliario da vila (postes Capsule nos lotes)
def street_lamps(mb):
    for x, y in ((WS[0] - 13.4, WS[1] + 5.8), (-47.5, 91.0), (53.0, 91.5)):
        capsule_lamp(mb, x, y, H)
    # moto flutuante Capsule estacionada atras da barraca leste do mercado, dentro do lote (o acento tech do
    # mercado marcial), de frente para a rua
    bp = MK_F.p(12.1, -11.6)
    hover_bike(mb, bp.x, bp.y, H, math.radians(-100.0))


def build_lights():
    light("L_DBHub_Workshop", "POINT", (WS[0] - 1.0, WS[1], H + 11.0), 2600, (0.92, 0.96, 1.0), 2.0)
    light("L_DBHub_Market", "POINT", (MK[0], MK[1] + 0.5, H + 6.8), 1100, (1.0, 0.7, 0.42), 1.5)
    light("L_DBHub_Dojo", "POINT", (DOJO[0], DOJO[1], DOJO_D + 6.4), 1400, (1.0, 0.72, 0.45), 1.5)


def build():
    house_a()
    house_b()
    market()
    workshop()
    pods()
    dojo()
    mbn = K.CMB("DB_Hub_PodsNorth", COLL, rng=random.Random(5109))
    pods_north(mbn)
    street_lamps(mbn)
    mbn.finish()
    build_lights()
