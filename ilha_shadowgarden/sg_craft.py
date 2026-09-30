# sg_craft - CRAFT da Ilha 3 (Shadow Garden), 5o na hierarquia: o SALAO NOBRE DE ALQUIMIA (refinamento v2, referencia
# refs/v2/ref2_alchemy_interior.png e ref2_alchemy_ext.jpg). Substitui sg_blockout.craft. Tudo sai da planta: CRAFT_C
# (90, -60) no P2, CRAFT_R 16 (raio externo; interior ~13), porta a OESTE (CRAFT_DOOR_DEG 180) com vao 8 x 11 na mesma
# posicao. Os marcadores CRAFT_Station (centro), PLAYER_INTERACT_Craft (5 a oeste, em cima do ESTRADO) e NPC_Craft sao
# do sg_core: aqui so o lugar em volta deles.
#   EXTERIOR: pavilhao redondo (24 faces) de pedra ESCURA; 7 contrafortes com URNA; 6 janelas ogivais ALTAS em luz
#     QUENTE; portico ogival com OCULO de vitral (Glass_SG_Rose), empena com o medalhao do frasco e 2 postes de lanterna
#     (kit); 3 VASOS DE BRONZE no pe dos contrafortes diagonais, ligados ao contraforte por TUBO -> FLANGE -> PAREDE;
#     domo navy com nervuras de prata, lanternim e o FRASCO GIGANTE com 2 ANEIS ARMILARES (VFX_SGCRAFT_Ring_1/2).
#   INTERIOR (pe-direito 18 ate a cornija, abobada de marmore negro com nervuras claras):
#     - CALDEIRAO (hero): bojo de perfil desenhado, BOCA de bronze enrolada, cinta de ferro negro com rebites,
#       MEDALHAO DA ORDEM (sg_emblem.plaque) preso por espelho que abraca a curvatura do bojo, 2 orelhas fundidas com
#       argola, 4 patas sobre a LAREIRA (4 setores de obsidiana com bocas de ventilacao: carvoes sob a grelha), pocao
#       violeta na boca, colher de pau apoiada na borda (ajuste 19: o fio de energia e o cristal do lustre sairam);
#     - ESTANTES de verdade (rodape, montantes nas bissetrizes das faces - o movel acompanha a parede curva sem
#       atravessar -, prateleiras com testeira, fundo escuro, friso e cornija; frontao nas estantes sem janela) com KIT
#       de livros (6 formatos, capa maior que o miolo, lombada com nervuras) arrumado a mao em grupos, inclinados,
#       pilhas e vazios, e KIT de frascos (redondo, tubo de ensaio no suporte, quadrado com rotulo, pote de
#       ingrediente, frasco de pocao grande): liquido embaixo, vidro em cima, tampas diferentes; 2 acesos;
#     - 2 MESAS DE ESTUDO (pernas torneadas sob o tampo, saia, travessa em H, banqueta de 3 pes), bancada do
#       alquimista com alambique ligado ao coletor, atril e bau perto da porta, lustre baixo de velas;
#     - 2 ESTANDARTES da ordem presos por mao-francesa; GALERIA estreita nas costas (leste), so leitura de profundidade.
# Colisao propria: anel da parede (20 caixas) + portico com o vao, contrafortes, tanques, cobertura, ESTRADO
# (2 x 10-gono), caldeirao (8-gono), bancada, estantes, mesas, atril, bau e 4 postes de lanterna. Luzes (4): caldeirao
# (violeta), lustre, lanternas da porta (quente), bancada (quente).
#
# OVERHAUL 06-08 (2026-09-29, "tolerancia zero", AUDITORIA2 06.xx / 07.xx / 08.xx):
#   EXTERIOR = laboratorio arcano, nao "predio redondo + pote": parede em CAMADAS (soco de obsidiana em talude ->
#     cantaria em fiadas ate +4,4 -> cordao -> arcada cega / avental das janelas -> cunhais nas juntas das faces ->
#     janela em 2 ordens de moldura com recuo -> vidro); contrafortes em 3 lances com talude e fiadas; remate = URNA de
#     pedra com tampa de bronze (o balao de vidro saiu); portico com flancos em chanfro, pilastras com base e capitel,
#     jambas em cunhais, ARQUIVOLTA EM ADUELAS, oculo em moldura de torno, cornija moldurada, EMPENA com cimalha em
#     perfil e TELHADO PROPRIO de 2 aguas que morre no domo com rufo (a nervura de 180 saiu), medalhao do frasco em
#     relevo; domo em FIADAS DE ESCAMAS (normais suaves) com nervuras redondas; lanternim com colunelos e cornija.
#   HEROIS: frasco gigante em VIDRO PINTADO opaco (bojo em pera, ombro, gargalo afunilado, aro, cinta, tampa de bronze),
#     liquido violeta ESCURO so no terco de baixo, 4 ESTRIBOS (berco) que seguram tambem os mancais dos 2 aneis
#     armilares (os aneis giram no PROPRIO plano, guiados pelos mancais); os tanques viram VASOS DE BRONZE (suporte de
#     ferro, cintas rebitadas, flange e tampa aparafusadas, visor, valvula, tubo -> flange -> contraforte); caldeirao com
#     labio de bronze, patas de 3 dedos, orelhas fundidas, grelha sobre carvoes (so as frestas brilham).
#   INTERIOR: lambril de madeira + pilastras de pedra ate as misulas + reboco; estantes com fundo escuro; pocoes com
#     cor media (vidro 0,55 so onde o liquido aparece); kit de vela no lustre e nas mesas; circulo com o alfabeto unico
#     (sg_court.RUNE_SEGS) embutido; hierarquia de magia: a POCAO do caldeirao e o unico foco (SG_VioletDeep); frasco,
#     circulo e 2 pocoes acesas em SG_VioletSoft (Neon escuro).
import math, random
import bmesh
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, Frame, ngon_col
import fm_lib
import sg_layout as L
import sg_emblem as EM
import sg_castle as CA          # kit de cantaria do overhaul 03 (ledge, block, ashlar, strip, finial, drip, plinth)
from sg_court import RUNE_SEGS, OBELISK_RUNES   # o alfabeto UNICO da ilha (16.07): runas angulares da ordem

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (12; 11 contam no orcamento)
NEW_MATS = {
    "Glass_SGCraftAmber": (S(150, 116, 80), 0.15, 0.0, 0.22, S(168, 118, 70), 0.0),    # vidro ambar (potes, frascos)
    "Glass_SGCraftSage": (S(104, 128, 118), 0.15, 0.0, 0.14, S(110, 140, 126), 0.0),   # vidro verde-salvia
    "Glass_SGCraftPale": (S(150, 162, 186), 0.1, 0.0, 0.1, S(120, 136, 170), 0.0),     # vidro claro (frascos, pingentes)
    "Cloth_SGCraftBook": (S(98, 42, 52), 0.85, 0.0, 0, None, 0.06),                    # encadernacao VINHO
    "Cloth_SGCraftBookInk": (S(38, 36, 46), 0.8, 0.0, 0, None, 0.05),                  # encadernacao PRETA
    "Cloth_SGCraftBookBrown": (S(96, 64, 44), 0.8, 0.0, 0, None, 0.06),                # couro marrom escuro
    # overhaul 07.08: liquidos em cor MEDIA (os escuros viravam frasco preto no jogo)
    "Potion_SGCraftWine": (S(160, 58, 98), 0.25, 0.0, 0, None, 0.0),                   # liquido vinho-rosado
    "Potion_SGCraftTeal": (S(58, 146, 136), 0.25, 0.0, 0, None, 0.0),                  # liquido verde-azulado
    "Stone_SGCraftDark": (S(54, 52, 74), 0.8, 0.0, 0, None, 0.08),                     # alvenaria ESCURA do pavilhao
    # overhaul 07.01/14.03: VIDRO PINTADO opaco (frasco gigante): le sem transparencia; o reflexo e malha propria
    "Glaze_SGCraftFlask": (S(140, 132, 174), 0.2, 0.0, 0, None, 0.0),
    # ajuste 19: vidro do ICONE da empena - azul-violeta claro e saturado, opaco (SmoothPlastic no Roblox, sem Neon)
    "Glaze_SGCraftIcon": (S(128, 138, 240), 0.35, 0.0, 0, None, 0.0),
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

CX, CY = L.CRAFT_C
Z = L.P2
DOOR = L.CRAFT_DOOR_DEG
R_IN = 13.4                    # face interna (vertices do 24-gono; interior ~13 de apotema)
R_OUT = 15.6                   # face externa (CRAFT_R 16 e o raio nominal; embasamento chega a 16,3)
H = 18.0                       # topo da parede / cornija (pe-direito interno)
STEP = 15.0                    # 24 faces
GAP = 30.0                     # meio vao angular do portico (4 faces abertas no anel)
A0, A1 = DOOR + GAP, DOOR + 360.0 - GAP
DW = L.CRAFT_DOOR_W / 2.0      # 4
DH = L.CRAFT_DOOR_H            # 11 (fecho do arco)
SPRING, RISE = 7.0, DH - 7.0   # arranque 7, flecha 4
PORT_HW = 8.1                  # meia largura do portico (cobre o vao angular de 30 no raio novo)
PORT_Y0, PORT_Y1 = 11.8, 16.6  # portico: face interna / face externa (distancia ao centro, no eixo da porta)
DOME_Z, DOME_R, DOME_RISE = 19.0, 15.8, 10.5
LAN_R, LAN_Z0, LAN_Z1 = 3.1, 28.6, 32.2
FLASK_ZC = LAN_Z1 + 0.6 + 4.6  # centro do bojo (37,4)
IN_DOME_RISE = 8.6
WIN_A = [22.5, 67.5, 112.5, 247.5, 292.5, 337.5]
# acabamento: TODAS as janelas em luz quente (a magia fica no caldeirao, no circulo e no frasco do topo)
WIN_M = {a: "Window_Warm" for a in WIN_A}
BUTT_A = [0.0, 45.0, 90.0, 135.0, 225.0, 270.0, 315.0]
SHELF_A = [67.5, 82.5, 97.5, 112.5, 247.5, 262.5, 277.5, 292.5]
SHELF_RUNS = [(60.0, 120.0), (240.0, 300.0)]  # as estantes ocupam essas faixas da parede (montantes nas bissetrizes)
BANNER_A = [52.5, 307.5]                     # faces livres (sem estante e sem janela)
TABLE_A = [37.5, 322.5]                      # mesas de estudo
RIB_A = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
GAL_A0, GAL_A1 = 315.0, 405.0                # galeria nas costas (leste) do salao
GAL_Z0, GAL_Z1 = 8.35, 8.95                  # piso da galeria (+8..9)
DAIS_R1, DAIS_R2 = 6.2, 4.8                  # estrado: degrau de baixo / de cima
DAIS_H1, DAIS_H2 = 0.7, 1.4                  # topos dos degraus (espelhos 0,7 <= 0,8)
WARM = (1.0, 0.68, 0.40)

# overhaul 14-16: o bronze da alquimia virou o bronze da ilha (Metal_SG_Bronze, sg_lib)
BRONZE, GLAZE, VSOFT = "Metal_SG_Bronze", "Glaze_SGCraftFlask", "SG_VioletSoft_Glow"
# overhaul 14.04: latao e ouro da alquimia viram BRONZE envelhecido (um metal de acento so)
IRON, SILVER, BRASS = "Metal_SG_Iron", "Metal_SG_Silver", BRONZE
CASTLE, TRIM, BLOCK, NAVY = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Block", "Roof_SG_Navy"
WALL = "Stone_SGCraftDark"     # corpo das paredes (pedra escura fria; contrafortes em Stone_SG_Castle, luar raspando)
WOOD, GLOW, VIOLET = "Wood_SG_Dark", "Lantern_Glow", "SG_Violet_Glow"
OBS, MARB, BIRON = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Metal_SG_BlackIron"
RUNE, CRYS, VDEEP, GOLD = "SG_Rune_Glow", "SG_Crystal_Glow", "SG_VioletDeep_Glow", BRONZE
VSTONE = "Stone_SG_Violet"
SOCLE = 2.6                    # soco alto de obsidiana (v3)
WIN_FOOT, WIN_SPRING, WIN_RISE, WIN_HW = 9.3, 14.4, 2.5, 1.35   # janelas ALTAS (v3: 9,3 -> 16,9)
OCU_Z, OCU_R = 14.8, 1.7       # oculo sobre a porta (portico)
POST_A = [150.0, 210.0]        # lanternas do circulo magico (ancoras dos raios)
TANK_A = [45.0, 225.0, 315.0]         # camaras de vidro no pe dos contrafortes diagonais (135 ficaria na rota da dungeon)
TANK_Y = 19.45                 # centro radial dos tanques (face do contraforte em 17,5; soco do contraforte ate 17,75)
CHAND_Z, CHAND_R = 12.6, 5.0   # lustre BAIXO (lido da camera da porta): aro, raio (ajuste 19: o cristal pendurado saiu)
AMBER, SAGE, PALE, ROSE = "Glass_SGCraftAmber", "Glass_SGCraftSage", "Glass_SGCraftPale", "Glass_SG_Rose"
BK_WINE, BK_INK, BK_PLUM, BK_BROWN = "Cloth_SGCraftBook", "Cloth_SGCraftBookInk", "Cloth_SG_Purple", "Cloth_SGCraftBookBrown"
POT_W, POT_T = "Potion_SGCraftWine", "Potion_SGCraftTeal"
PAGES, CANVAS = "Plaster_SG", "Cloth_Canvas"

P2 = Z
CAMS = {
    # 360 de fora (frente = oeste, a porta; tras = leste; lados norte e sul)
    "CAM_SGCraft_W": ((46.0, -52.0, P2 + 9.0), (90.0, -60.0, P2 + 24.0), 22),
    "CAM_SGCraft_N": ((102.0, -12.0, P2 + 18.0), (90.0, -60.0, P2 + 18.0), 22),
    "CAM_SGCraft_E": ((148.0, -46.0, P2 + 13.0), (90.0, -60.0, P2 + 22.0), 22),
    "CAM_SGCraft_S": ((108.0, -120.0, P2 + 9.0), (90.0, -60.0, P2 + 22.0), 22),
    "CAM_SGCraft_Far": ((0.0, -164.0, P2 + 50.0), (90.0, -60.0, P2 + 22.0), 30),
    # altura do jogador chegando pela rua do P2 (a porta e o frasco lidos juntos)
    "CAM_SGCraft_PH_Door": ((62.0, -58.0, P2 + 5.2), (90.0, -60.0, P2 + 11.0), 22),
    # dentro: da porta para o estrado/caldeirao; estantes; galeria; circulo; de volta; teto e lustre
    "CAM_SGCraft_In_Cauldron": ((78.2, -62.8, P2 + 6.2), (97.0, -59.0, P2 + 5.0), 18),
    "CAM_SGCraft_In_ShelvesN": ((81.5, -66.5, P2 + 6.0), (93.0, -46.5, P2 + 6.0), 18),
    "CAM_SGCraft_In_ShelvesS": ((81.5, -53.5, P2 + 6.0), (93.0, -73.5, P2 + 6.0), 18),
    "CAM_SGCraft_In_Gallery": ((80.0, -65.5, P2 + 5.2), (102.5, -57.0, P2 + 10.5), 17),
    "CAM_SGCraft_In_Circle": ((83.0, -67.5, P2 + 8.0), (92.5, -57.5, P2 + 1.4), 18),
    "CAM_SGCraft_In_Door": ((99.0, -61.0, P2 + 5.6), (76.0, -60.0, P2 + 7.0), 16),
    "CAM_SGCraft_In_Up": ((80.6, -60.0, P2 + 3.2), (93.0, -60.0, P2 + 18.0), 14),
}

# rota extra: da rua, pela porta, uma volta inteira em torno do caldeirao (raio 5,2 - SOBE no estrado, degraus 0,7) e
# saida - prova que estrado, mesas, atril, bau e estantes deixam a circulacao livre
_VOLTA = [(CX + 5.2 * math.cos(math.radians(180.0 - 30.0 * k)), CY + 5.2 * math.sin(math.radians(180.0 - 30.0 * k)))
          for k in range(13)]
EXTRA_ROUTES = {
    "CRAFT_VOLTA_CALDEIRAO": ([(CX - 20.0, CY), (CX - 13.0, CY), (CX - 8.0, CY)] + _VOLTA + [(CX - 8.0, CY), (CX - 20.0, CY)],
                              P2),
}
EXTRA_PROBES = [("CRAFT_estante_N", CX + 1.3, CY + 9.5, P2, 0.0, 1.0), ("CRAFT_bancada_L", CX + 7.6, CY, P2, 1.0, 0.0)]


# ------------------------------------------------------------------ referenciais
def fr(a_deg):
    """referencial no centro do pavilhao: local +y = radial para fora no rumo a_deg, local x = tangente, z = altura"""
    return Frame(CX, CY, Z, math.radians(a_deg) - math.pi / 2)


FD = fr(DOOR)


def pol(r, a_deg, z):
    a = math.radians(a_deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a), Z + z)


def apo(r):
    """apotema do 24-gono de raio (vertice) r: onde fica a face plana no meio de cada lado"""
    return r * math.cos(math.radians(STEP / 2.0))


YB_IN = apo(R_IN)              # face interna plana (~13,28): as estantes encostam aqui
SH_F = YB_IN - 1.24            # frente da caixa das estantes (colisao)
TAN = math.tan(math.radians(STEP / 2.0))


# ------------------------------------------------------------------ primitivas
def ring_band(mb, r0, r1, z0, z1, m, a0=0.0, a1=360.0, step=STEP):
    """anel (setor) solido entre os raios r0 e r1 (vertices do poligono), de z0 a z1 (acima do piso)"""
    bm = mb.bm
    full = abs(a1 - a0 - 360.0) < 1e-6
    n = int(round((a1 - a0) / step))
    angs = [math.radians(a0 + (a1 - a0) * k / n) for k in range(n + (0 if full else 1))]

    def v(r, a, z):
        return bm.verts.new((CX + r * math.cos(a), CY + r * math.sin(a), Z + z))
    ib = [v(r0, a, z0) for a in angs]
    ob = [v(r1, a, z0) for a in angs]
    it = [v(r0, a, z1) for a in angs]
    ot = [v(r1, a, z1) for a in angs]
    K = len(angs)
    for i in (range(K) if full else range(K - 1)):
        j = (i + 1) % K
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((ib[j], ib[i], it[i], it[j]))
        bm.faces.new((it[i], ot[i], ot[j], it[j]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    if not full:
        bm.faces.new((ib[0], ob[0], ot[0], it[0]))
        bm.faces.new((ib[-1], it[-1], ot[-1], ob[-1]))
    mb._post(ib + ob + it + ot, m, None, 0, 1)


def pslab(mb, F, pts, y0, y1, m):
    """poligono (u, v) no plano tangente do referencial F, extrudado no radial de y0 a y1"""
    bm = mb.bm
    A = [bm.verts.new(F.p(u, y1, v)) for u, v in pts]
    B = [bm.verts.new(F.p(u, y0, v)) for u, v in pts]
    n = len(pts)
    bm.faces.new(A)
    bm.faces.new(list(reversed(B)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((A[j], A[i], B[i], B[j]))
    mb._post(A + B, m, None, 0, 1)


def pside(mb, F, pts, u0, u1, m):
    """poligono (y, v) no plano radial do referencial F, extrudado na tangente de u0 a u1"""
    bm = mb.bm
    A = [bm.verts.new(F.p(u1, y, v)) for y, v in pts]
    B = [bm.verts.new(F.p(u0, y, v)) for y, v in pts]
    n = len(pts)
    bm.faces.new(A)
    bm.faces.new(list(reversed(B)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((A[j], A[i], B[i], B[j]))
    mb._post(A + B, m, None, 0, 1)


def fprism(mb, F, pts, v0, v1, m, bevel=0.0):
    """poligono (u, y) em planta no referencial F (anti-horario), extrudado na vertical de v0 a v1 (acima do piso)"""
    w = [F.p(u, y, 0.0) for u, y in pts]
    mb.prism([(p[0], p[1]) for p in w], Z + v0, Z + v1, m, bevel)


def fbox(mb, F, u0, u1, y0, y1, v0, v1, m, bevel=0.0):
    c = F.p((u0 + u1) / 2.0, (y0 + y1) / 2.0, (v0 + v1) / 2.0)
    mb.box((abs(u1 - u0), abs(y1 - y0), abs(v1 - v0)), c, F.r(), m, bevel)


def fcol(area, F, u0, u1, y0, y1, v0, v1):
    c = F.p((u0 + u1) / 2.0, (y0 + y1) / 2.0, (v0 + v1) / 2.0)
    col_box(area, (abs(u1 - u0), abs(y1 - y0), abs(v1 - v0)), c, F.r())


def lathe(mb, x, y, z, prof, m, n=12, rot=0.0, cap0=True, cap1=True, sm=None):
    """solido de revolucao: prof = [(raio, altura)] de baixo para cima; raio 0 = polo.
    sm: normais lisas nas faces laterais ('all' ou conjunto de indices j do trecho prof[j] -> prof[j+1])"""
    bm = mb.bm
    rows = []
    for r, h in prof:
        if r < 1e-4:
            rows.append([bm.verts.new((x, y, z + h))])
        else:
            rows.append([bm.verts.new((x + r * math.cos(rot + 2 * math.pi * i / n),
                                       y + r * math.sin(rot + 2 * math.pi * i / n), z + h)) for i in range(n)])
    side = []
    for jj, (A, B) in enumerate(zip(rows, rows[1:])):
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                f = bm.faces.new((A[0], B[i], B[j]))
            elif len(B) == 1:
                f = bm.faces.new((A[i], A[j], B[0]))
            else:
                f = bm.faces.new((A[i], A[j], B[j], B[i]))
            if sm == "all" or (sm and jj in sm):
                side.append(f)
    if cap0 and len(rows[0]) > 1:
        bm.faces.new(list(reversed(rows[0])))
    if cap1 and len(rows[-1]) > 1:
        bm.faces.new(rows[-1])
    mb._post([v for r in rows for v in r], m, None, 0, 1)
    smooth(side)


def lathe_ax(mb, o, ax, prof, m, n=16, cap0=True, cap1=True):
    """solido de revolucao em torno de um eixo qualquer (o = origem, ax = direcao); prof = [(raio, distancia no eixo)]"""
    bm = mb.bm
    ax = Vector(ax).normalized()
    o = Vector(o)
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    rows = []
    for r, d in prof:
        if r < 1e-4:
            rows.append([bm.verts.new(o + ax * d)])
        else:
            rows.append([bm.verts.new(o + ax * d + (e1 * math.cos(2 * math.pi * i / n) + e2 * math.sin(2 * math.pi * i / n)) * r)
                         for i in range(n)])
    for A, B in zip(rows, rows[1:]):
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                bm.faces.new((A[0], B[i], B[j]))
            elif len(B) == 1:
                bm.faces.new((A[i], A[j], B[0]))
            else:
                bm.faces.new((A[i], A[j], B[j], B[i]))
    if cap0 and len(rows[0]) > 1:
        bm.faces.new(list(reversed(rows[0])))
    if cap1 and len(rows[-1]) > 1:
        bm.faces.new(rows[-1])
    mb._post([v for r in rows for v in r], m, None, 0, 1)


def cone(mb, a, b, r0, r1, m, n=8):
    """tronco de cone de a (raio r0) ate b (raio r1)"""
    import bmesh
    from mathutils import Matrix
    a, b = Vector(a), Vector(b)
    d = b - a
    Ln = d.length
    if Ln < 1e-4:
        return
    q = d.to_track_quat("Z", "Y")
    M = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    res = bmesh.ops.create_cone(mb.bm, cap_ends=True, cap_tris=False, segments=n, radius1=r0, radius2=r1, depth=Ln,
                                matrix=M)
    mb._post(res["verts"], m, None, 0, 1)


# ------------------------------------------------------------------ helpers do overhaul 06-08
def W_of(a_deg):
    """referencial de PAREDE do kit do castelo (sg_castle._P) no rumo a_deg: u = tangente (mesmo sentido do fr(a)),
    t = distancia radial ao centro do pavilhao, z ABSOLUTO"""
    a = math.radians(a_deg)
    return ((CX, CY), (math.sin(a), -math.cos(a)), (math.cos(a), math.sin(a)))


def smooth(faces):
    """sombreamento liso (o FBX sai com mesh_smooth_type FACE: vale no Roblox tambem)"""
    for f in faces:
        if f.is_valid:
            f.smooth = True


def _faces_of(verts):
    return {f for v in verts if v.is_valid for f in v.link_faces}


def poly_ring(mb, prof, a0, a1, m, ap=None, step=None):
    """PERFIL (t, v) varrido em volta do 24-gono com esquadria exata nas juntas: t = afastamento da face plana de
    apotema ap (padrao: face externa), v = altura sobre o piso. prof = poligono simples (fechado)."""
    step = STEP if step is None else step
    ap = apo(R_OUT) if ap is None else ap
    bm = mb.bm
    full = abs(a1 - a0 - 360.0) < 1e-6
    n = int(round((a1 - a0) / step))
    angs = [math.radians(a0 + step * k) for k in range(n + (0 if full else 1))]
    kc = 1.0 / math.cos(math.radians(step / 2.0))
    loops = []
    for a in angs:
        ca, sa = math.cos(a), math.sin(a)
        loops.append([bm.verts.new((CX + (ap + t) * kc * ca, CY + (ap + t) * kc * sa, Z + v)) for t, v in prof])
    K = len(prof)
    fs = []
    for i in (range(len(loops)) if full else range(len(loops) - 1)):
        A, B = loops[i], loops[(i + 1) % len(loops)]
        for j in range(K):
            j2 = (j + 1) % K
            fs.append(bm.faces.new((A[j], A[j2], B[j2], B[j])))
    if not full:
        fs.append(bm.faces.new(loops[0]))
        fs.append(bm.faces.new(list(reversed(loops[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for lp in loops for v in lp], m, None, 0, 1)


def revolve(mb, c, prof, m, n=16, rot=0.0, closed=True, smooth_edges=None, a0=None, a1=None):
    """perfil [(r, z)] (z relativo a c) girado em volta do eixo vertical por c. closed=True: perfil FECHADO (anel
    solido, sem tampas); smooth_edges: indices j das arestas prof[j]->prof[j+1] com normais lisas (None = todas).
    a0/a1 (graus): so um setor, com tampas planas nas pontas."""
    bm = mb.bm
    x, y, z = c
    part = a0 is not None
    cnt = n + 1 if part else n
    rows = []
    for i in range(cnt):
        a = (math.radians(a0) + (math.radians(a1) - math.radians(a0)) * i / n) if part else rot + 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        rows.append([bm.verts.new((x + r * ca, y + r * sa, z + h)) for r, h in prof])
    K = len(prof)
    edges = range(K) if closed else range(K - 1)
    sm = []
    fs = []
    for i in (range(cnt - 1) if part else range(cnt)):
        A, B = rows[i], rows[(i + 1) % cnt]
        for j in edges:
            j2 = (j + 1) % K
            f = bm.faces.new((A[j], B[j], B[j2], A[j2]))
            fs.append(f)
            if smooth_edges is None or j in smooth_edges:
                sm.append(f)
    if part and closed:
        fs.append(bm.faces.new(rows[0]))
        fs.append(bm.faces.new(list(reversed(rows[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)
    smooth(sm)


def ring_ax(mb, o, ax, prof, m, n=20, ph=0.0):
    """perfil FECHADO [(r, d)] girado em volta do eixo ax por o (moldura de oculo, flange, anel de visor)"""
    bm = mb.bm
    ax = Vector(ax).normalized()
    o = Vector(o)
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    rows = []
    for i in range(n):
        t = ph + 2 * math.pi * i / n
        d = e1 * math.cos(t) + e2 * math.sin(t)
        rows.append([bm.verts.new(o + ax * dd + d * r) for r, dd in prof])
    K = len(prof)
    fs = []
    for i in range(n):
        A, B = rows[i], rows[(i + 1) % n]
        for j in range(K):
            j2 = (j + 1) % K
            fs.append(bm.faces.new((A[j], B[j], B[j2], A[j2])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)


def disc_ax(mb, o, ax, r, d0, d1, m, n=20):
    """disco (cilindro curto) no eixo ax: de d0 a d1 ao longo do eixo"""
    lathe_ax(mb, o, ax, [(r, d0), (r, d1)], m, n=n)


def ext_poly(mb, pts, P, d0, d1, m):
    """poligono SIMPLES [(a, b)] mapeado por P(a, b, d) e extrudado de d0 a d1 (casca fechada; ngon nas tampas)"""
    bm = mb.bm
    A = [bm.verts.new(P(a, b, d0)) for a, b in pts]
    B = [bm.verts.new(P(a, b, d1)) for a, b in pts]
    n = len(pts)
    fs = [bm.faces.new(A), bm.faces.new(list(reversed(B)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(A + B, m, None, 0, 1)


def offset_line(pts, e):
    """polilinha aberta deslocada 'e' para a ESQUERDA do caminho, com esquadria nos cantos"""
    n = len(pts)
    nr = []
    for i in range(n - 1):
        dx, dy = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        Ln = math.hypot(dx, dy)
        nr.append((-dy / Ln, dx / Ln))
    out = []
    for i in range(n):
        if i == 0:
            mx, my = nr[0]
        elif i == n - 1:
            mx, my = nr[-1]
        else:
            a, b = nr[i - 1], nr[i]
            s = 1.0 + a[0] * b[0] + a[1] * b[1]
            mx, my = (a[0] + b[0]) / s, (a[1] + b[1]) / s
        out.append((pts[i][0] + mx * e, pts[i][1] + my * e))
    return out


def sph_uv(mb, faces, m, zb, R):
    """UV esferica (azimute x elevacao, em studs/TILE) para cupulas: a projecao planar do MB (uma primitiva so) esticava
    a textura em faixas"""
    key = fm_lib.tex_key(m)
    if key is None:
        return
    inv = 1.0 / fm_lib.tex_tile(key)
    uvl = mb.uvl
    for f in faces:
        c = f.calc_center_median()
        a0 = math.atan2(c.y - CY, c.x - CX)
        for lp in f.loops:
            co = lp.vert.co
            rr = math.hypot(co.x - CX, co.y - CY)
            az = a0 if rr < 1e-3 else math.atan2(co.y - CY, co.x - CX)
            while az - a0 > math.pi:
                az -= 2 * math.pi
            while az - a0 < -math.pi:
                az += 2 * math.pi
            el = math.atan2(co.z - zb, max(rr, 1e-3))
            lp[uvl].uv = (az * R * inv, el * R * inv)


# ------------------------------------------------------------------ arco ogival (mesmo desenho do Mining Hall)
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


def band(mb, F, inner, outer, y0, y1, m):
    """faixa solida no plano tangente entre duas polilinhas (u, v) de mesmo tamanho"""
    bm = mb.bm
    n = len(inner)
    iF = [bm.verts.new(F.p(u, y1, v)) for u, v in inner]
    iB = [bm.verts.new(F.p(u, y0, v)) for u, v in inner]
    oF = [bm.verts.new(F.p(u, y1, v)) for u, v in outer]
    oB = [bm.verts.new(F.p(u, y0, v)) for u, v in outer]
    for i in range(n - 1):
        j = i + 1
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    for k in (0, n - 1):
        bm.faces.new((iF[k], oF[k], oB[k], iB[k]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def arch_band(mb, F, hw, rise, spring, foot, t, y0, y1, m, n=6):
    inner = [(-hw, foot)] + ogive(0.0, hw, rise, spring, n) + [(hw, foot)]
    outer = [(-hw - t, foot)] + ogive(0.0, hw + t, rise + t, spring, n) + [(hw + t, foot)]
    band(mb, F, inner, outer, y0, y1, m)


def arch_panel(mb, F, hw, rise, spring, foot, y0, y1, m, n=6):
    pslab(mb, F, [(-hw, foot)] + ogive(0.0, hw, rise, spring, n) + [(hw, foot)], y0, y1, m)


def spandrels(mb, F, hw, rise, spring, top, y0, y1, m, n=6):
    """parede cheia acima do arco (de |u| <= hw ate top), em faixas verticais convexas: o intradorso segue a ogiva"""
    r = ogive_right(hw, rise, n)
    for s in (-1, 1):
        for (ua, va), (ub, vb) in zip(r, r[1:]):
            pslab(mb, F, [(s * ua, spring + va), (s * ub, spring + vb), (s * ub, top), (s * ua, top)], y0, y1, m)


# ------------------------------------------------------------------ remate: URNA de pedra com tampa de bronze (06.04)
# (o balao de vidro de 8 lados com cinta e agulha saiu: no jogo era uma bola navy facetada com cinta laranja)
URN_BODY = [(0.0, 0.0), (0.42, 0.0), (0.4, 0.1), (0.22, 0.24), (0.27, 0.36), (0.56, 0.58), (0.64, 0.84), (0.47, 1.18),
            (0.31, 1.3), (0.0, 1.3)]
URN_LID = [(0.0, 1.28), (0.38, 1.28), (0.35, 1.43), (0.16, 1.58), (0.13, 1.74), (0.0, 1.88)]


def urn(mb, x, y, z, s=1.0, n=10):
    """urna do atanor: pe torneado e bojo de obsidiana polida (normais lisas no bojo), cinta e tampa de bronze com
    botao. Assenta em z (topo do pedestal). Altura 1,88 s."""
    def P(pr):
        return [(r * s, h * s) for r, h in pr]
    lathe(mb, x, y, z, P(URN_BODY), OBS, n=16, sm={3, 4, 5, 6, 7})
    revolve(mb, (x, y, z), P([(0.58, 0.74), (0.68, 0.76), (0.68, 0.9), (0.58, 0.92)]), BRONZE, n=16,
            smooth_edges=set())
    lathe(mb, x, y, z, P(URN_LID), BRONZE, n=n, rot=math.pi / n, sm={1, 2})


def pedestal(mb, F, u, y0, y1, z0, hw):
    """dado do remate sobre a cornija: base moldurada (pedra violeta), dado (pedra do castelo), capa. Devolve o topo."""
    fbox(mb, F, u - hw - 0.14, u + hw + 0.14, y0 - 0.14, y1 + 0.14, z0, z0 + 0.3, VSTONE, 0.05)
    fbox(mb, F, u - hw, u + hw, y0, y1, z0 + 0.3, z0 + 1.55, CASTLE, 0.05)
    fbox(mb, F, u - hw - 0.12, u + hw + 0.12, y0 - 0.12, y1 + 0.12, z0 + 1.55, z0 + 1.8, VSTONE, 0.05)
    return z0 + 1.8


# ------------------------------------------------------------------ casca: embasamento, parede, frisos, contrafortes
AP_O = apo(R_OUT)                                   # face externa plana (~15,47)
SIDE = 2.0 * R_OUT * math.sin(math.radians(STEP / 2.0))     # largura de cada face (~4,07)
PLINTH_TOP = 1.3                                    # soco de obsidiana em talude
ASH_TOP = 4.35                                      # cantaria em 2 fiadas (0,875 / 0,65) ate aqui
CRD_TOP = 4.93                                      # cordao (pingadeira) sobre a cantaria
COURSES = [PLINTH_TOP, 2.175, 2.825, 3.7, ASH_TOP, 5.225, 5.875, 6.75, 7.4]   # fiadas (base e 1o lance)
SILL_TOP = WIN_FOOT                                 # cordao-peitoril corrido (topo = pe das janelas)
QUOIN_W = 0.3                                       # meia largura do cunhal nas juntas das faces
PROF_PLINTH = [(-0.3, -0.4), (0.72, -0.4), (0.72, 0.88), (0.3, PLINTH_TOP), (-0.3, PLINTH_TOP)]
PROF_CORD = [(-0.3, ASH_TOP), (0.24, ASH_TOP), (0.42, ASH_TOP + 0.16), (0.42, ASH_TOP + 0.34), (0.2, CRD_TOP),
             (-0.3, CRD_TOP)]
PROF_SILL = [(-0.3, SILL_TOP - 0.45), (0.26, SILL_TOP - 0.45), (0.46, SILL_TOP - 0.3), (0.46, SILL_TOP - 0.06),
             (0.38, SILL_TOP), (-0.3, SILL_TOP)]
PROF_CORNICE = [(-0.3, H - 0.75), (0.2, H - 0.75), (0.2, H - 0.6), (0.45, H - 0.42), (0.78, H - 0.32), (0.78, H),
                (-0.3, H)]


def frs(a_deg, uc):
    """fr(a) deslocado de uc na tangente (arcos centrados fora do meio da face)"""
    a = math.radians(a_deg)
    return Frame(CX + uc * math.sin(a), CY - uc * math.cos(a), Z, a - math.pi / 2)


def _joint(v):
    v = v % 360.0
    if any(abs(((v - b + 180.0) % 360.0) - 180.0) < 0.1 for b in BUTT_A):
        return "butt"
    if abs(v - 150.0) < 0.1 or abs(v - 210.0) < 0.1:
        return "door"
    return "quoin"


CLEAR = {"butt": 1.0, "quoin": QUOIN_W + 0.04, "door": 1.35}


def face_span(phi):
    """faixa livre (u0, u1) da face phi entre o que ocupa as juntas (contraforte, cunhal ou portico)"""
    kp, km = _joint(phi - STEP / 2.0), _joint(phi + STEP / 2.0)      # u+ = junta em phi-7,5; u- = junta em phi+7,5
    return -SIDE / 2.0 + CLEAR[km], SIDE / 2.0 - CLEAR[kp]


FACES = [(A0 + STEP * (k + 0.5)) % 360.0 for k in range(int(round((A1 - A0) / STEP)))]


def window_out(mb, a):
    """janela alta por fora em CAMADAS: vidraca quente -> 1a ordem (pedra violeta) -> 2a ordem (pedra do castelo,
    mais saliente: o recuo le) -> pingadeira de obsidiana no arco com batentes; mainel e travessa de ferro; embaixo, o
    AVENTAL rebaixado entre 2 montantes que descem ate o cordao"""
    F = fr(a)
    y = AP_O
    arch_panel(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, WIN_FOOT, y - 0.05, y + 0.06, WIN_M[a], n=4)
    arch_band(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, WIN_FOOT, 0.2, y - 0.05, y + 0.3, VSTONE, n=4)
    arch_band(mb, F, WIN_HW + 0.2, WIN_RISE + 0.2, WIN_SPRING, WIN_FOOT, 0.28, y - 0.05, y + 0.5, CASTLE, n=4)
    arch_band(mb, F, WIN_HW + 0.48, WIN_RISE + 0.48, WIN_SPRING, WIN_SPRING - 0.5, 0.13, y - 0.05, y + 0.64, OBS, n=4)
    for s in (-1, 1):
        fbox(mb, F, s * (WIN_HW + 0.46), s * (WIN_HW + 0.72), y - 0.05, y + 0.66, WIN_SPRING - 0.78, WIN_SPRING - 0.5,
             OBS, 0.03)                                                                  # batente da pingadeira
    fbox(mb, F, -0.09, 0.09, y, y + 0.2, WIN_FOOT, WIN_SPRING + WIN_RISE - 0.3, BIRON)
    fbox(mb, F, -WIN_HW, WIN_HW, y, y + 0.2, 12.6, 12.76, BIRON)
    # avental: montantes (continuam a 2a ordem) e painel escuro rebaixado; o respiro do porao fica na cantaria
    for s in (-1, 1):
        fbox(mb, F, s * (WIN_HW + 0.2), s * (WIN_HW + 0.48), y - 0.05, y + 0.22, CRD_TOP - 0.02, SILL_TOP - 0.44,
             CASTLE, 0.04)
    fbox(mb, F, -WIN_HW - 0.2, WIN_HW + 0.2, y - 0.02, y + 0.03, CRD_TOP, SILL_TOP - 0.44, OBS)
    fbox(mb, F, -WIN_HW - 0.2, WIN_HW + 0.2, y - 0.05, y + 0.16, CRD_TOP - 0.02, CRD_TOP + 0.14, VSTONE, 0.03)


def cellar_vent(mb, a):
    """respiro de porao (faces de janela, na cantaria): moldura de pedra, fundo escuro e 4 barras de ferro"""
    F = fr(a)
    y = AP_O
    v0, v1, hw = 1.85, 3.45, 0.62
    fbox(mb, F, -hw, hw, y - 0.05, y + 0.02, v0, v1, OBS)
    for s in (-1, 1):
        fbox(mb, F, s * hw, s * (hw + 0.3), y - 0.05, y + 0.2, v0 - 0.2, v1 + 0.02, CASTLE, 0.04)
    fbox(mb, F, -hw - 0.3, hw + 0.3, y - 0.05, y + 0.2, v1, v1 + 0.3, CASTLE, 0.04)
    fbox(mb, F, -hw - 0.34, hw + 0.34, y - 0.05, y + 0.3, v0 - 0.3, v0, VSTONE, 0.03)
    for k in range(4):
        u = -hw + (k + 0.5) * 2 * hw / 4.0
        fbox(mb, F, u - 0.05, u + 0.05, y + 0.02, y + 0.12, v0, v1, BIRON)


def blind_arch(mb, a):
    """arcada cega baixa (faces sem janela, 06.01): arco em pedra do castelo saliente 0,2, painel escuro rebaixado,
    impostas de pedra violeta; assenta no cordao"""
    u0, u1 = face_span(a)
    F = frs(a, (u0 + u1) / 2.0)
    y = AP_O
    hw, rise, spring = 1.02, 1.25, 7.05
    arch_panel(mb, F, hw, rise, spring, CRD_TOP, y - 0.02, y + 0.03, OBS, n=4)
    arch_band(mb, F, hw, rise, spring, CRD_TOP - 0.02, 0.26, y - 0.05, y + 0.2, CASTLE, n=4)
    for s in (-1, 1):
        fbox(mb, F, s * (hw - 0.04), s * (hw + 0.34), y - 0.05, y + 0.28, spring - 0.22, spring, VSTONE, 0.03)


def buttress(mb, a):
    """contraforte (06.05) em 3 lances: soco de obsidiana em talude, 1o lance em FIADAS (as mesmas da cantaria),
    talude de pedra violeta com pingadeira, 2o e 3o lances lisos com 2o talude, pedestal e URNA no alto"""
    F = fr(a)
    pside(mb, F, [(15.2, -0.4), (17.85, -0.4), (17.85, 0.85), (17.45, PLINTH_TOP), (15.2, PLINTH_TOP)], -1.15, 1.15, OBS)
    for k, (v0, v1) in enumerate(zip(COURSES, COURSES[1:])):
        e = 0.03 if k % 2 else 0.0                                        # fiadas alternadas: junta le pela sombra
        fbox(mb, F, -0.95 - e, 0.95 + e, 15.2, 17.5 + e, v0, v1, CA.ASH, 0.06)
    pside(mb, F, [(15.2, 7.4), (17.64, 7.4), (17.64, 7.58), (17.2, 8.1), (15.2, 8.1)], -1.0, 1.0, VSTONE)
    fbox(mb, F, -0.8, 0.8, 15.2, 17.2, 8.1, 14.4, CASTLE, 0.05)
    pside(mb, F, [(15.2, 14.4), (17.32, 14.4), (17.32, 14.56), (16.95, 15.0), (15.2, 15.0)], -0.86, 0.86, VSTONE)
    fbox(mb, F, -0.66, 0.66, 15.2, 16.95, 15.0, H - 0.75, CASTLE, 0.05)
    top = pedestal(mb, F, 0.0, 16.2, 17.3, H - 0.75, 0.56)
    c = F.p(0.0, 16.75, 0.0)
    urn(mb, c[0], c[1], Z + top, 1.0)


def shell():
    mb = MB("SG_Craft_Shell", "16_CRAFT", random.Random(8101), detail="near")
    ring_band(mb, R_IN, R_OUT, -0.3, H, WALL, A0, A1)                    # nucleo da parede (24-gono sem a porta)
    # EMBASAMENTO (06.01 / 14.07): soco de obsidiana em talude, cantaria em fiadas ate +4,35, cordao de pedra violeta
    poly_ring(mb, PROF_PLINTH, A0, A1, OBS)
    for k, phi in enumerate(FACES):
        u0, u1 = face_span(phi)
        excl = [(-0.98, 0.98, Z + 1.55, Z + 3.8)] if phi in WIN_M else []
        CA.ashlar(mb, W_of(phi), u0, u1, Z + PLINTH_TOP, Z + ASH_TOP, AP_O, excl, m=CA.ASH, PL=1.95, dep=0.1,
                  ch=0.06, phase=0.55 * (k % 3))
    poly_ring(mb, PROF_CORD, A0, A1, VSTONE)
    # corpo: cunhais finos nas juntas livres (quebram os 24 planos), arcada cega nas faces cheias, avental + respiro
    # nas faces de janela, cordao-peitoril corrido, cornija moldurada
    for k in range(int(round((A1 - A0) / STEP)) + 1):
        v = (A0 + STEP * k) % 360.0
        if _joint(v) != "quoin":
            continue
        fbox(mb, fr(v), -QUOIN_W, QUOIN_W, R_OUT - 0.3, R_OUT + 0.17, CRD_TOP - 0.02, H - 0.74, CASTLE, 0.05)
    for phi in FACES:
        if phi in WIN_M:
            window_out(mb, phi)
            cellar_vent(mb, phi)
        elif abs(phi - 142.5) > 0.1 and abs(phi - 217.5) > 0.1:
            blind_arch(mb, phi)
    poly_ring(mb, PROF_SILL, A0, A1, VSTONE)
    poly_ring(mb, PROF_CORNICE, A0, A1, OBS)
    ring_band(mb, 15.0, 16.15, H, H + 1.0, VSTONE, 0.0, 360.0)           # anel de apoio do domo (volta inteira)
    ring_band(mb, 15.9, 16.22, H + 0.1, H + 0.3, SILVER, 0.0, 360.0)     # fio de prata do anel
    for a in BUTT_A:
        buttress(mb, a)
    portal(mb)
    lab_tanks(mb)
    mb.finish()
    # colisao: anel refeito para o raio novo (20 caixas, mesmo padrao), contrafortes
    rm = (R_IN + R_OUT) / 2.0
    chord = 2.0 * R_OUT * math.sin(math.radians(STEP / 2.0)) + 0.1
    n = int(round((A1 - A0) / STEP))
    for k in range(n):
        am = math.radians(A0 + STEP * (k + 0.5))
        col_box("SG_CraftWall", (R_OUT - R_IN, chord, H + 0.5), (CX + rm * math.cos(am), CY + rm * math.sin(am), Z + (H - 0.5) / 2.0),
                (0, 0, am))
    for a in BUTT_A:
        fcol("SG_CraftButtress", fr(a), -0.95, 0.95, R_OUT - 0.2, 17.35, -0.5, 10.2)


# ------------------------------------------------------------------ VASOS DE BRONZE do laboratorio (07.02)
VESSEL = [(0.0, 1.1), (0.62, 1.13), (1.05, 1.3), (1.33, 1.6), (1.47, 2.05), (1.45, 2.55), (1.33, 3.05), (1.1, 3.52),
          (0.84, 3.9), (0.66, 4.22), (0.62, 4.5), (0.0, 4.5)]             # caldeira em CEBOLA (nao barril)
VESSEL_LID = [(0.0, 4.48), (0.84, 4.48), (0.84, 4.64), (0.76, 4.68), (0.58, 4.84), (0.36, 4.98), (0.28, 5.06),
              (0.28, 5.7), (0.37, 5.74), (0.37, 5.86), (0.0, 5.86)]


def _vr(v):
    return _r_at(VESSEL[1:-1], v)


def lab_tanks(mb):
    """os 3 'jarros cinza' viram VASOS DE LABORATORIO de verdade (no pe dos contrafortes diagonais; o do noroeste fica
    livre: rota da dungeon): soco octogonal de obsidiana, SUPORTE de ferro (anel sob o bojo + 4 pernas com sapata),
    corpo de BRONZE torneado (normais lisas), 2 CINTAS de ferro rebitadas, FLANGE e TAMPA aparafusadas, VISOR redondo
    de moldura aparafusada (o liquido aparece so ali, em cor solida, com o nivel), VALVULA de volante no tubo e o tubo
    -> flange -> contraforte."""
    for i, a in enumerate(TANK_A):
        F = fr(a)
        c = F.p(0.0, TANK_Y, 0.0)
        x, y = c[0], c[1]
        liq = POT_W if a == 225.0 else POT_T
        lathe(mb, x, y, Z, [(0.0, -0.3), (1.5, -0.3), (1.5, 0.3), (1.38, 0.42), (0.0, 0.42)], OBS, n=8, rot=math.pi / 8)
        # suporte de ferro: anel sob o bojo e 4 pernas em arco ate a sapata no soco
        revolve(mb, (x, y, Z), [(1.22, 1.5), (1.4, 1.5), (1.4, 1.66), (1.22, 1.66)], BIRON, n=12, smooth_edges={1})
        for k in range(4):
            b = F.a + math.pi / 4 + k * math.pi / 2
            ca, sa = math.cos(b), math.sin(b)
            pts = [(x + r * ca, y + r * sa, Z + v) for r, v in ((1.36, 1.6), (1.5, 1.25), (1.49, 0.85), (1.3, 0.5))]
            mb.sweep(pts, [(-0.09, -0.08), (0.09, -0.08), (0.09, 0.08), (-0.09, 0.08)], BIRON, True, None,
                     up=(ca, sa, 0.0))
            mb.box((0.34, 0.26, 0.1), (x + 1.28 * ca, y + 1.28 * sa, Z + 0.47), (0, 0, b), BIRON, 0.03)
        lathe(mb, x, y, Z, VESSEL, BRONZE, n=10, sm={1, 2, 3, 4, 5, 6, 7, 8})
        lathe(mb, x, y, Z, VESSEL_LID, BRONZE, n=10, sm={3, 4, 5})
        for k in range(6):                                                # parafusos da flange
            b = F.a + math.pi / 6 + k * math.pi / 3
            mb.box((0.11, 0.11, 0.08), (x + 0.73 * math.cos(b), y + 0.73 * math.sin(b), Z + 4.66), (0, 0, b), BIRON, 0.0)
        for vb in (1.85, 3.1):                                            # cintas rebitadas
            r0, r1 = _vr(vb - 0.13), _vr(vb + 0.13)
            revolve(mb, (x, y, Z), [(r0 - 0.03, vb - 0.13), (r0 + 0.07, vb - 0.11), (r1 + 0.07, vb + 0.11),
                                    (r1 - 0.03, vb + 0.13)], BIRON, n=10, smooth_edges={1})
            for b in (F.a + math.pi / 2 - 0.75, F.a + math.pi / 2 + 0.75, F.a - math.pi / 2):   # rebites (lado visto)
                rr = _vr(vb) + 0.09
                mb.box((0.07, 0.09, 0.09), (x + rr * math.cos(b), y + rr * math.sin(b), Z + vb), (0, 0, b), IRON, 0.0)
        # VISOR na face de fora (o que o jogador ve da rua)
        ax = Vector((math.cos(F.a + math.pi / 2), math.sin(F.a + math.pi / 2), 0.0))
        tg = Vector((-ax.y, ax.x, 0.0))
        vz = 2.5
        o = Vector((x, y, Z + vz)) + ax * (_vr(vz) - 0.06)
        ring_ax(mb, o, ax, [(0.27, -0.02), (0.44, -0.02), (0.44, 0.1), (0.36, 0.15), (0.27, 0.12)], BRONZE, n=12)
        for k in range(4):
            t = math.pi / 4 + k * math.pi / 2
            p = o + tg * (0.37 * math.cos(t)) + Vector((0, 0, 0.37 * math.sin(t))) + ax * 0.15
            mb.box((0.07, 0.07, 0.07), tuple(p), (0, 0, F.a), IRON, 0.0)
        P = lambda aa, bb, d: tuple(o + tg * aa + Vector((0, 0, bb)) + ax * d)
        lvl = -0.06
        circ = [(0.28 * math.cos(2 * math.pi * k / 12 + 0.13), 0.28 * math.sin(2 * math.pi * k / 12 + 0.13)) for k in range(12)]
        low = [p for p in circ if p[1] < lvl]
        hw_l = math.sqrt(0.28 ** 2 - lvl ** 2)
        low = sorted(low, key=lambda p: math.atan2(p[1], p[0]))
        ext_poly(mb, [(-hw_l, lvl)] + low + [(hw_l, lvl)], P, -0.04, 0.06, liq)
        hi = sorted([p for p in circ if p[1] > lvl], key=lambda p: math.atan2(p[1], p[0]))
        ext_poly(mb, [(hw_l, lvl)] + hi + [(-hw_l, lvl)], P, -0.04, 0.05, OBS)
        # tubo: sobe da gola, VALVULA, curva e entra no contraforte (face em y = 17,5)
        zp = 7.0
        pts = [F.p(0.0, TANK_Y, 5.8), F.p(0.0, TANK_Y, zp - 0.5), F.p(0.0, TANK_Y - 0.12, zp - 0.24),
               F.p(0.0, TANK_Y - 0.4, zp - 0.06), F.p(0.0, TANK_Y - 0.75, zp), F.p(0.0, 17.45, zp)]
        mb.tube(pts, 0.15, BRASS, 8)
        vc = F.p(0.0, TANK_Y, 6.2)
        lathe(mb, vc[0], vc[1], vc[2], [(0.0, -0.2), (0.24, -0.2), (0.27, -0.1), (0.27, 0.1), (0.24, 0.2), (0.0, 0.2)],
              BRONZE, n=8)
        tax = Vector((math.cos(F.a), math.sin(F.a), 0.0))          # eixo do volante (tangente)
        mb.rod(tuple(Vector(vc)), tuple(Vector(vc) + tax * 0.5), 0.05, IRON, 6)
        wc = Vector(vc) + tax * 0.5
        ring_ax(mb, wc, tax, [(0.24, -0.04), (0.31, -0.04), (0.31, 0.04), (0.24, 0.04)], BIRON, n=8)
        for q in range(2):
            t = q * math.pi / 2
            d = Vector((0, 0, 1)) * math.cos(t) + Vector((-tax.y, tax.x, 0)) * math.sin(t)
            mb.rod(tuple(wc - d * 0.26), tuple(wc + d * 0.26), 0.035, BIRON, 4)
        # flange na face do contraforte (4 parafusos) + colar no tubo
        mb.cyl(0.38, 0.12, F.p(0.0, 17.56, zp), F.r(math.pi / 2, 0.0, 0.0), BRASS, n=10, bevel=0.0)
        for k in range(4):
            b = math.pi / 4 + k * math.pi / 2
            mb.box((0.08, 0.06, 0.08), F.p(0.27 * math.cos(b), 17.64, zp + 0.27 * math.sin(b)), F.r(), BIRON, 0.0)
        mb.cyl(0.21, 0.14, F.p(0.0, 18.0, zp), F.r(math.pi / 2, 0.0, 0.0), BRASS, n=8, bevel=0.0)
        col_box("SG_CraftTank", (2.8, 2.8, 6.6), (x, y, Z + 3.0), (0, 0, F.a))


# ------------------------------------------------------------------ PORTICO (06.02 / 06.03 / 06.07 / 06.08)
GH = 7.0                                   # empena a 45 graus (apice H + 7)
P_FRONT, P_CH = 7.0, (8.3, 15.3)           # frente plana |u| <= 7; chanfro ate (8,3; 15,3); flanco ate o tambor
P_BACK = (9.9, 11.3)                       # o flanco morre dentro do tambor
OUTLINE = [P_BACK, P_CH, (P_FRONT, PORT_Y1)]


def _outline(e=0.0, full=True):
    """contorno do portico em planta (u, y), no sentido anti-horario visto de cima (norte -> sul), deslocado 'e'
    para fora"""
    north = OUTLINE
    south = [(-u, y) for u, y in reversed(OUTLINE)]
    pts = north + south if full else north
    if e:
        pts = offset_line(pts, -e)
    return pts


def molding_uv(mb, F, path, prof, y_base, m):
    """moldura no PLANO da fachada (u, v) do referencial F: path = polilinha (u, v); prof = [(a, b)] com a =
    afastamento para a ESQUERDA do caminho (no plano) e b = saliencia radial a partir de y_base. Esquadria exata."""
    bm = mb.bm
    offs = [offset_line(path, a) for a, b in prof]
    rows = []
    for i in range(len(path)):
        rows.append([bm.verts.new(F.p(offs[k][i][0], y_base + prof[k][1], offs[k][i][1])) for k in range(len(prof))])
    K = len(prof)
    fs = []
    for A, B in zip(rows, rows[1:]):
        for j in range(K):
            j2 = (j + 1) % K
            fs.append(bm.faces.new((A[j], A[j2], B[j2], B[j])))
    fs.append(bm.faces.new(rows[0]))
    fs.append(bm.faces.new(list(reversed(rows[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)


def molding_plan(mb, F, path, prof, m):
    """moldura HORIZONTAL em volta do contorno em planta: path (u, y) anti-horario; prof = [(t, v)] com t =
    afastamento para FORA do contorno (direita do caminho) e v = altura. Esquadria exata."""
    bm = mb.bm
    offs = [offset_line(path, -t) for t, v in prof]
    rows = []
    for i in range(len(path)):
        rows.append([bm.verts.new(F.p(offs[k][i][0], offs[k][i][1], prof[k][1])) for k in range(len(prof))])
    K = len(prof)
    fs = []
    for A, B in zip(rows, rows[1:]):
        for j in range(K):
            j2 = (j + 1) % K
            fs.append(bm.faces.new((A[j], A[j2], B[j2], B[j])))
    fs.append(bm.faces.new(rows[0]))
    fs.append(bm.faces.new(list(reversed(rows[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)


def _arch_pts(hw, rise, n):
    """ogiva completa (u, v acima da nascenca) da esquerda para a direita, 2n segmentos"""
    r = ogive_right(hw, rise, n)
    return [(-u, v) for u, v in r] + [(u, v) for u, v in reversed(r)][1:]


def voussoirs(mb, F, hw_i, hw_o, rise_i, rise_o, spring, y0, y1, n_side=7, gap=0.07):
    """ARQUIVOLTA EM ADUELAS: 2 x n_side aduelas + fecho (maior e mais saliente), juntas radiais, todas na mesma
    cantaria (a alternancia de cor lia engrenagem); so o fecho em pedra violeta"""
    seg = 3
    lo = _arch_pts(hw_i, rise_i, n_side * seg + 2)
    hi = _arch_pts(hw_o, rise_o, n_side * seg + 2)
    N = len(lo) - 1                                      # segmentos totais (par)
    W = W_of(DOOR)
    cuts = [seg * k for k in range(n_side + 1)] + [N - seg * k for k in range(n_side, -1, -1)]
    pieces = [(cuts[k], cuts[k + 1]) for k in range(len(cuts) - 1)]

    def lerp(p, q, t):
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    mid = len(pieces) // 2
    for k, (i0, i1) in enumerate(pieces):
        if i1 <= i0:
            continue
        key = k == mid
        L_ = [lo[i] for i in range(i0, i1 + 1)]
        H_ = [hi[i] for i in range(i0, i1 + 1)]
        g = gap / max(1e-3, math.hypot(lo[i0 + 1][0] - lo[i0][0], lo[i0 + 1][1] - lo[i0][1]))
        L_[0], H_[0] = lerp(L_[0], L_[1], g), lerp(H_[0], H_[1], g)
        L_[-1], H_[-1] = lerp(L_[-1], L_[-2], g), lerp(H_[-1], H_[-2], g)
        if key:                                          # fecho: sobe 0,25 acima da arquivolta
            H_ = [(u, v + 0.25) for u, v in H_]
        m = VSTONE if key else CA.ASH                    # um tom so (junta separa); acento discreto no fecho
        CA.strip(mb, W, [(u, Z + spring + v) for u, v in L_], [(u, Z + spring + v) for u, v in H_],
                 y0, y1 + (0.14 if key else 0.0), m)


def half_lathe(mb, F, uc, y0, vc, prof, dep, m, n=10):
    """relevo: meio solido de revolucao (eixo vertical no plano da fachada em u = uc) achatado 'dep' para fora da
    fachada (y0); prof = [(r, dv)] de baixo para cima, sem polos (tampas em leque)"""
    bm = mb.bm
    rows = []
    for r, dv in prof:
        rows.append([bm.verts.new(F.p(uc + r * math.cos(math.pi * i / n), y0 + dep * r * math.sin(math.pi * i / n),
                                      vc + dv)) for i in range(n + 1)])
    fs = []
    for A, B in zip(rows, rows[1:]):
        for i in range(n):
            fs.append(bm.faces.new((A[i], A[i + 1], B[i + 1], B[i])))
    for R_, rev in ((rows[0], True), (rows[-1], False)):
        fs.append(bm.faces.new(list(reversed(R_)) if rev else R_))
    for A, B in zip(rows, rows[1:]):                     # costas (planas, rentes ao medalhao)
        fs.append(bm.faces.new((A[0], B[0], B[-1], A[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)


# ICONE DA ALQUIMIA (ajuste 19): frasco de bojo redondo em relevo, lido SO por cor solida (sem transparencia e sem
# Neon: no Roblox o vidro vira SmoothPlastic azul-violeta claro): placa de BRONZE com a silhueta do frasco + rolha
# (o contorno de bronze aparece 0,08 em volta), vidro azul-violeta (ICON_GLASS), liquido AMBAR no terco de baixo do
# bojo (Window_Warm: SmoothPlastic ambar 214/140/74 no Roblox, o mesmo material das janelas - sem MeshPart nova),
# rolha de bronze e 3 borbulhas BRANCAS (icosfera baixa, Flower_White: o branco do reflexo do frasco gigante)
# subindo no liquido. Perfis (raio, altura) do centro do disco.
ICON_GLASS = "Glaze_SGCraftIcon"
ICON_LIQ = "Window_Warm"
ICON_FOAM = "Flower_White"
ICON_FLASK = [(0.24, -1.0), (0.48, -0.93), (0.64, -0.7), (0.69, -0.42), (0.6, -0.13), (0.38, 0.06), (0.21, 0.19),
              (0.19, 0.6), (0.28, 0.66), (0.28, 0.78)]
ICON_CORK = [(0.19, 0.74), (0.24, 0.8), (0.25, 1.02), (0.2, 1.08)]
ICON_LIQ_V = -0.34                         # nivel do liquido (logo acima da barriga)
ICON_DV = -0.04                            # o icone inteiro desce um pouco: fica centrado no disco


def _prof_r(prof, v):
    """raio do perfil na altura v (interpolacao linear)"""
    for (r0, v0), (r1, v1) in zip(prof, prof[1:]):
        if v0 <= v <= v1:
            return r0 + (r1 - r0) * (v - v0) / max(v1 - v0, 1e-6)
    return prof[0][0] if v < prof[0][1] else prof[-1][0]


def flat_profile(mb, F, y0, y1, vc, prof, m):
    """placa plana com a silhueta de um perfil de torno [(r, dv)] (simetrica em u = 0), de y0 a y1: faixas trapezoidais
    (convexas) empilhadas numa casca fechada"""
    bm = mb.bm
    rows = [[bm.verts.new(F.p(s_ * r, y, vc + dv)) for s_, y in ((-1, y0), (1, y0), (1, y1), (-1, y1))]
            for r, dv in prof]
    fs = []
    for A, B in zip(rows, rows[1:]):
        for i in range(4):
            j = (i + 1) % 4
            fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    fs.append(bm.faces.new(list(reversed(rows[0]))))
    fs.append(bm.faces.new(rows[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)


def alchemy_icon(mb, F, yf, vc):
    """o icone da empena da alquimia. yf = face do disco de obsidiana (distancia radial), vc = centro (altura)"""
    vc += ICON_DV
    # contorno: placa de bronze 0,08 maior que frasco + rolha, saindo 0,1 do disco
    out = [(0.3, -1.08), (0.56, -0.99), (0.72, -0.74), (0.77, -0.42), (0.68, -0.1), (0.46, 0.09), (0.29, 0.23),
           (0.27, 0.58), (0.36, 0.62), (0.36, 0.8), (0.33, 0.83), (0.33, 1.03), (0.27, 1.15)]
    flat_profile(mb, F, yf - 0.02, yf + 0.1, vc, out, BRONZE)
    # vidro azul-violeta (meio torno achatado; o fundo fica 0,02 dentro da placa)
    y0 = yf + 0.08
    half_lathe(mb, F, 0.0, y0, vc, ICON_FLASK, 0.5, ICON_GLASS, n=10)
    # liquido ambar: casca do bojo ate o nivel, 0,025 mais larga (cobre o vidro), com a superficie plana no nivel
    liq = [(r + 0.025, dv) for r, dv in ICON_FLASK if dv < ICON_LIQ_V]
    liq = [(liq[0][0], liq[0][1] - 0.02)] + liq[1:] + [(_prof_r(ICON_FLASK, ICON_LIQ_V) + 0.025, ICON_LIQ_V)]
    half_lathe(mb, F, 0.0, y0, vc, liq, 0.5, ICON_LIQ, n=10)
    # rolha de bronze (sai um pouco mais que o gargalo)
    half_lathe(mb, F, 0.0, y0, vc, ICON_CORK, 0.62, BRONZE, n=8)
    # 3 borbulhas claras subindo no liquido (meio embutidas na superficie do liquido)
    for u, dv, rb in ((0.2, -0.56, 0.1), (-0.14, -0.74, 0.075), (0.02, -0.45, 0.06)):
        R = _prof_r(ICON_FLASK, dv) + 0.025
        d = 0.5 * math.sqrt(max(R * R - u * u, 0.0))
        mb.ico(rb, F.p(u, y0 + d, vc + dv), ICON_FOAM, 1)


def _dome_rho(z):
    """raio horizontal da superficie externa do domo na altura z (acima do piso); abaixo do domo: anel de apoio"""
    if z <= DOME_Z:
        return 16.0
    f = (z - DOME_Z) / DOME_RISE
    return DOME_R * math.sqrt(max(0.0, 1.0 - f * f))


def portal(mb):
    """portico da porta (oeste), vao ogival 8 x 11 na mesma posicao. Overhaul: macico com FLANCOS em chanfro que morrem
    no tambor (nao e mais caixa colada), soco em talude e cornija moldurada correndo o contorno, PILASTRAS de canto com
    base e capitel nos chanfros (pedestal + urna no alto), jambas em CUNHAIS alternados, 1a ordem em toro e ARQUIVOLTA
    EM ADUELAS com fecho, pingadeira com batentes, OCULO em moldura de torno, EMPENA com cimalha em perfil, TELHADO
    PROPRIO de 2 aguas que morre no domo com rufo de prata e cumeeira, MEDALHAO do frasco em relevo. Os estandartes
    sairam (16.02: o emblema ja esta no portico e dentro); os postes de lanterna sao o kit definitivo."""
    F = FD
    y0, y1 = PORT_Y0, PORT_Y1
    # macico: um prisma por lado (planta convexa: jamba -> fundo -> flanco -> chanfro -> frente)
    for s in (-1, 1):
        pts = [(DW, y0), (P_BACK[0], y0), P_BACK, P_CH, (P_FRONT, y1), (DW, y1)]
        pts = [(s * u, yy) for u, yy in pts]
        if s < 0:
            pts = list(reversed(pts))
        fprism(mb, F, pts, -0.3, H, WALL)
    spandrels(mb, F, DW, RISE, SPRING, H, y0, y1, WALL)
    # soco em talude e cordao nos lados (param nas jambas), cornija no contorno inteiro
    for s in (-1, 1):
        side = [(s * u, yy) for u, yy in OUTLINE] + [(s * (DW + 0.06), y1)]
        if s < 0:
            side = list(reversed(side))
        molding_plan(mb, F, side, PROF_PLINTH, OBS)
        molding_plan(mb, F, [(s * u, yy) for u, yy in OUTLINE[:2]] if s > 0 else
                     [(s * u, yy) for u, yy in reversed(OUTLINE[:2])], PROF_CORD, VSTONE)
    molding_plan(mb, F, _outline(), PROF_CORNICE, OBS)
    for s in (-1, 1):
        pa, pb = Vector(F.p(s * P_BACK[0], P_BACK[1], 0.0)), Vector(F.p(s * P_CH[0], P_CH[1], 0.0))
        d = (pb - pa)
        Lf = d.length
        d.normalize()
        n = Vector((d.y, -d.x, 0.0)) * s
        CA.ashlar(mb, ((pa.x, pa.y), (d.x, d.y), (n.x, n.y)), 1.1, Lf - 0.3, Z + PLINTH_TOP, Z + ASH_TOP, 0.0, [],
                  m=CA.ASH, PL=1.95, dep=0.1, ch=0.06, phase=0.4)
        um = (1.1 + Lf) / 2.0
        o = pa + d * um
        Ff = Frame(o.x, o.y, Z, math.atan2(n.y, n.x) - math.pi / 2)
        arch_panel(mb, Ff, 1.0, 1.25, 7.05, CRD_TOP, -0.02, 0.03, OBS, n=4)
        arch_band(mb, Ff, 1.0, 1.25, 7.05, CRD_TOP - 0.02, 0.26, -0.05, 0.2, CASTLE, n=4)
        for q in (-1, 1):
            fbox(mb, Ff, q * 0.96, q * 1.32, -0.05, 0.28, 6.83, 7.05, VSTONE, 0.03)
        fo = Vector(F.p(0.0, y1, 0.0))
        fu = Vector((math.cos(F.a), math.sin(F.a), 0.0))
        fn = Vector((math.cos(F.a + math.pi / 2), math.sin(F.a + math.pi / 2), 0.0))
        ua, ub = sorted((s * (DW + 1.1), s * (P_FRONT - 0.04)))
        CA.ashlar(mb, ((fo.x, fo.y), (fu.x, fu.y), (fn.x, fn.y)), ua, ub, Z + PLINTH_TOP, Z + ASH_TOP, 0.0, [],
                  m=CA.ASH, PL=1.95, dep=0.1, ch=0.06, phase=0.8)
        seg = [(s * P_FRONT, y1), (s * (DW + 1.07), y1)] if s > 0 else [(-(DW + 1.07), y1), (-P_FRONT, y1)]
        molding_plan(mb, F, seg, PROF_CORD, VSTONE)
    # PILASTRAS nos chanfros (base moldurada no soco, fuste, capitel sob a cornija) + pedestal e urna no alto
    for s in (-1, 1):
        (ua, ya), (ub, yb) = P_CH, (P_FRONT, y1)
        cu, cy = s * (ua + ub) / 2.0, (ya + yb) / 2.0
        nx, ny = s * (yb - ya), (ua - ub)                             # normal para fora do chanfro, no plano (u, y)
        pa = math.atan2(ny, nx)
        o = F.p(cu, cy, 0.0)
        Fp = Frame(o[0], o[1], Z, F.a + pa - math.pi / 2)
        fbox(mb, Fp, -0.72, 0.72, -0.2, 0.55, PLINTH_TOP, PLINTH_TOP + 0.3, VSTONE, 0.05)
        fbox(mb, Fp, -0.62, 0.62, -0.2, 0.45, PLINTH_TOP + 0.3, PLINTH_TOP + 0.62, CASTLE, 0.05)
        fbox(mb, Fp, -0.52, 0.52, -0.2, 0.34, PLINTH_TOP + 0.62, H - 1.15, CASTLE, 0.05)
        fbox(mb, Fp, -0.6, 0.6, -0.2, 0.42, H - 1.15, H - 0.95, VSTONE, 0.04)
        fbox(mb, Fp, -0.7, 0.7, -0.2, 0.52, H - 0.95, H - 0.75, CASTLE, 0.04)
        top = pedestal(mb, Fp, 0.0, -0.3, 0.75, H, 0.5)
        c = Fp.p(0.0, 0.22, 0.0)
        urn(mb, c[0], c[1], Z + top, 1.15)
    # JAMBAS em cunhais alternados (longo / curto, mesma cantaria das aduelas) ate a nascenca
    hs = (0.82, 0.6)
    sc = (SPRING - 0.05) / (5.0 * (hs[0] + hs[1]))
    zc = [0.05]
    for k in range(10):
        zc.append(zc[-1] + hs[k % 2] * sc)
    for s in (-1, 1):
        for k, (v0, v1) in enumerate(zip(zc, zc[1:])):
            w = 1.05 if k % 2 == 0 else 0.7
            fbox(mb, F, s * (DW - 0.02), s * (DW + w), y1 - 0.05, y1 + 0.34, v0 + 0.03, v1 - 0.03, CA.ASH, 0.05)
    # 1a ordem (toro de pedra violeta), ADUELAS, pingadeira de obsidiana com batentes
    arch_band(mb, F, DW, RISE, SPRING, SPRING - 0.02, 0.32, y1 - 0.05, y1 + 0.42, VSTONE)
    voussoirs(mb, F, DW + 0.32, DW + 1.08, RISE + 0.32, RISE + 1.08, SPRING, y1 - 0.05, y1 + 0.36)
    arch_band(mb, F, DW + 1.1, RISE + 1.1, SPRING, SPRING - 0.55, 0.17, y1 - 0.05, y1 + 0.58, OBS)
    for s in (-1, 1):
        fbox(mb, F, s * (DW + 1.02), s * (DW + 1.5), y1 - 0.05, y1 + 0.62, SPRING - 0.85, SPRING - 0.55, OBS, 0.03)
    arch_band(mb, F, DW, RISE, SPRING, 0.8, 0.7, y0 - 0.4, y0, VSTONE)                  # moldura de dentro
    # OCULO de vitral (vidraca nas 2 faces), moldura de torno, cruz de ferro com botoes
    ring = [(OCU_R * math.cos(2 * math.pi * k / 16), OCU_Z + OCU_R * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    pslab(mb, F, ring, y1 - 0.06, y1 + 0.05, ROSE)
    pslab(mb, F, ring, y0 - 0.05, y0 + 0.06, ROSE)
    ax = Vector((math.cos(F.a + math.pi / 2), math.sin(F.a + math.pi / 2), 0.0))
    o = Vector(F.p(0.0, 0.0, OCU_Z))
    ring_ax(mb, o, ax, [(OCU_R - 0.06, y1 - 0.05), (OCU_R + 0.5, y1 - 0.05), (OCU_R + 0.5, y1 + 0.2),
                        (OCU_R + 0.32, y1 + 0.42), (OCU_R + 0.1, y1 + 0.42), (OCU_R - 0.06, y1 + 0.24)], VSTONE, n=16)
    fbox(mb, F, -0.09, 0.09, y1, y1 + 0.2, OCU_Z - OCU_R, OCU_Z + OCU_R, BIRON)
    fbox(mb, F, -OCU_R, OCU_R, y1, y1 + 0.2, OCU_Z - 0.09, OCU_Z + 0.09, BIRON)
    disc_ax(mb, Vector(F.p(0.0, 0.0, OCU_Z)), ax, 0.2, y1 + 0.18, y1 + 0.3, BRONZE, n=8)
    # EMPENA: tambor triangular, CIMALHA em perfil correndo as 2 aguas (esquadria no apice), acroterio com florao
    pslab(mb, F, [(-P_FRONT, H), (P_FRONT, H), (0.0, H + GH)], y1 - 0.9, y1, WALL)
    rake = [(-P_FRONT - 0.35, H - 0.35), (0.0, H + GH), (P_FRONT + 0.35, H - 0.35)]
    molding_uv(mb, F, rake, [(-0.5, -0.95), (0.32, -0.95), (0.32, 0.06), (0.2, 0.3), (-0.06, 0.44), (-0.5, 0.44)],
               y1, VSTONE)
    ap = F.p(0.0, y1 - 0.25, H + GH + 0.3)
    lathe(mb, ap[0], ap[1], ap[2] - 0.1, [(0.0, 0.0), (0.42, 0.0), (0.42, 0.34), (0.3, 0.46), (0.0, 0.46)], VSTONE, n=8,
          rot=math.pi / 8)
    CA.finial(mb, ap[0], ap[1], ap[2] + 0.36, 1.25)
    # MEDALHAO do frasco (06.07; ajuste 19, pedido do usuario: "o icone de alquimia sem cor, um lixo"): disco de
    # obsidiana e ARO DE BRONZE (era pedra violeta); o icone COLORIDO em relevo sai no MB do domo (alchemy_icon: la
    # ja existem todos os materiais dele menos o vidro)
    mc = Vector(F.p(0.0, 0.0, H + 2.55))
    disc_ax(mb, mc, ax, 1.45, y1 - 0.05, y1 + 0.12, OBS, n=16)
    ring_ax(mb, mc, ax, [(1.34, y1 - 0.05), (1.72, y1 - 0.05), (1.72, y1 + 0.2), (1.56, y1 + 0.34), (1.36, y1 + 0.28)],
            BRONZE, n=16)
    # TELHADO PROPRIO de 2 aguas (navy) atras da empena: nasce dentro da cimalha e morre no domo; rufo e cumeeira
    bm = mb.bm
    NU = 7
    for s in (-1, 1):
        us = [s * (P_FRONT + 0.3) * i / NU for i in range(NU + 1)]
        yf = y1 - 0.85
        top, bot = [], []
        back_pts = []
        for u in us:
            zt = H + GH - abs(u) + 0.18
            yb = math.sqrt(max(0.0, _dome_rho(zt) ** 2 - u * u)) - 0.35
            back_pts.append((u, yb, zt))
            top.append((bm.verts.new(F.p(u, yf, zt)), bm.verts.new(F.p(u, yb, zt))))
            bot.append((bm.verts.new(F.p(u, yf, zt - 0.42)), bm.verts.new(F.p(u, yb, zt - 0.42))))
        fs = []
        for i in range(NU):
            j = i + 1
            fs.append(bm.faces.new((top[i][0], top[j][0], top[j][1], top[i][1])))
            fs.append(bm.faces.new((bot[i][1], bot[j][1], bot[j][0], bot[i][0])))
            fs.append(bm.faces.new((top[i][0], bot[i][0], bot[j][0], top[j][0])))
            fs.append(bm.faces.new((top[j][1], bot[j][1], bot[i][1], top[i][1])))
        for i in (0, NU):
            fs.append(bm.faces.new((top[i][0], top[i][1], bot[i][1], bot[i][0])))
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        mb._post([v for pr in top + bot for v in pr], NAVY, None, 0, 1)
        # rufo de prata na linha onde a agua encontra o domo
        mb.sweep([F.p(u, yb + 0.38, zt + 0.02) for u, yb, zt in back_pts],
                 [(-0.2, -0.06), (0.2, -0.06), (0.2, 0.08), (-0.2, 0.08)], SILVER, True, None, up=(0.0, 0.0, 1.0))
    ridge_end = math.sqrt(max(0.0, _dome_rho(H + GH + 0.2) ** 2)) - 0.1
    mb.sweep([F.p(0.0, y1 - 0.4, H + GH + 0.24), F.p(0.0, ridge_end, H + GH + 0.24)],
             [(0.2 * math.cos(2 * math.pi * k / 6), 0.2 * math.sin(2 * math.pi * k / 6)) for k in range(6)], SILVER,
             True, None, up=(0.0, 0.0, 1.0))
    # soleira de obsidiana (topo 0,05 acima do piso, como o calcamento das ruas)
    fbox(mb, F, -DW, DW, y0 - 0.2, y1 + 0.5, -0.3, 0.05, OBS)
    # POSTES DE LANTERNA (kit definitivo) na frente da porta
    for s in (-1, 1):
        p = F.p(s * 6.4, y1 + 2.2, 0.0)
        EM.lantern_post(mb, mb, (p[0], p[1], p[2]), math.radians(DOOR), h=6.6, s=1.0)
        col_box("SG_CraftLanternPost", (1.2, 1.2, 7.2), (p[0], p[1], p[2] + 3.4), (0, 0, math.radians(DOOR)))
    # colisao do portico: ombreiras + verga em degraus que acompanha a ogiva (o vao fica 8 x 7 reto + arco ate 11)
    for s in (-1, 1):
        fcol("SG_CraftPortal", F, s * DW, s * (PORT_HW + 0.45), y0, y1 + 0.5, -0.5, H)
        fcol("SG_CraftPortal", F, s * 2.0, s * 3.2, y0, y1 + 0.5, SPRING + ogive_z(DW, RISE, 2.0), DH)
        fcol("SG_CraftPortal", F, s * 3.2, s * DW, y0, y1 + 0.5, SPRING + ogive_z(DW, RISE, 3.2), DH)
    fcol("SG_CraftPortal", F, -DW, DW, y0, y1 + 0.5, DH, H)
    # flancos em chanfro (a massa nova fora da caixa antiga)
    for s in (-1, 1):
        (ua, ya), (ub, yb) = P_BACK, P_CH
        cu, cyy = s * (ua + ub) / 2.0 - s * 0.3, (ya + yb) / 2.0
        ln = math.hypot(ub - ua, yb - ya)
        ang = math.atan2(yb - ya, s * (ub - ua))
        p = F.p(cu, cyy, (H - 0.5) / 2.0)
        col_box("SG_CraftPortal", (ln, 1.0, H + 0.5), (p[0], p[1], p[2]), (0, 0, F.a + ang))


# ------------------------------------------------------------------ domo em FIADAS DE ESCAMAS, nervuras, lanternim
DOME_RIB_A = [a for a in RIB_A if a != DOOR]          # a nervura de 180 nascia atras da empena (06.02): saiu
DOME_N, DOME_COURSES = 32, 10


def _dome_pt(phi, off=0.0):
    """ponto (raio, z acima do piso) da superficie do domo no angulo phi, afastado 'off' na normal"""
    r, z = DOME_R * math.cos(phi), DOME_Z + DOME_RISE * math.sin(phi)
    nr, nz = math.cos(phi) / DOME_R, math.sin(phi) / DOME_RISE
    Ln = math.hypot(nr, nz)
    return r + off * nr / Ln, z + off * nz / Ln


def dome_scales(mb):
    """o domo em 10 FIADAS de ardosia sobrepostas (06.06): cada fiada e uma cunha cuja borda de baixo sai 0,16 da
    superficie (a sombra da borda marca a fiada) e e RECORTADA em dentes alternados (escamas desencontradas fiada a
    fiada); normais lisas no dorso (sem o tabuleiro de luz)"""
    bm = mb.bm
    ph_top = math.acos((LAN_R + 0.5) / DOME_R)
    for k in range(DOME_COURSES):
        f0 = ph_top * k / DOME_COURSES
        f1 = ph_top * (k + 1) / DOME_COURSES
        fl = f0 - 0.012                                   # a borda desce um pouco sobre a fiada de baixo
        rows = []
        for i in range(DOME_N):
            a = 2 * math.pi * i / DOME_N
            ca, sa = math.cos(a), math.sin(a)
            tooth = (i + k) % 2 == 0
            fe = fl - (0.03 if tooth else 0.0)
            pts = [_dome_pt(fe, 0.0), _dome_pt(fe, 0.17), _dome_pt(f1, 0.0)]
            rows.append([bm.verts.new((CX + r * ca, CY + r * sa, Z + z)) for r, z in pts])
        fs, sm = [], []
        for i in range(DOME_N):
            A, B = rows[i], rows[(i + 1) % DOME_N]
            for j in range(3):
                j2 = (j + 1) % 3
                f = bm.faces.new((A[j], B[j], B[j2], A[j2]))
                fs.append(f)
                if j == 1:
                    sm.append(f)
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        mb._post([v for r_ in rows for v in r_], NAVY, None, 0, 1)
        smooth(sm)


def lanternim(mb):
    """lanternim (06.06): tambor octogonal de obsidiana com as fendas quentes, COLUNELOS torneados nas quinas, base e
    CORNIJA molduradas (a cornija e o assento do frasco)"""
    rot = math.pi / 8
    lathe(mb, CX, CY, Z, [(0.0, LAN_Z0), (LAN_R, LAN_Z0), (LAN_R, LAN_Z1), (0.0, LAN_Z1)], OBS, n=8, rot=rot)
    for k in range(8):
        F = fr(45.0 * k)
        y = LAN_R * math.cos(math.pi / 8)
        arch_panel(mb, F, 0.5, 0.62, 31.0, 29.5, y - 0.05, y + 0.06, "Window_Warm", n=3)
        arch_band(mb, F, 0.5, 0.62, 31.0, 29.5, 0.14, y - 0.05, y + 0.16, VSTONE, n=3)
        q = fr(45.0 * k + 22.5).p(0.0, LAN_R + 0.1, 0.0)
        EM._lathe(mb, (q[0], q[1], Z + 29.45), [(0.2, 0.0), (0.21, 0.1), (0.13, 0.2), (0.12, 2.1), (0.16, 2.22),
                                               (0.22, 2.3), (0.22, 2.4)], SILVER, 6, caps=(False, True))
    lathe(mb, CX, CY, Z, [(0.0, LAN_Z0 - 0.1), (3.75, LAN_Z0 - 0.1), (3.75, LAN_Z0 + 0.35), (3.5, LAN_Z0 + 0.6),
                          (3.2, LAN_Z0 + 0.85), (0.0, LAN_Z0 + 0.85)], VSTONE, n=8, rot=rot)
    lathe(mb, CX, CY, Z, [(0.0, LAN_Z1 - 0.35), (3.35, LAN_Z1 - 0.35), (3.62, LAN_Z1 - 0.12), (3.9, LAN_Z1 + 0.1),
                          (3.9, LAN_Z1 + 0.4), (0.0, LAN_Z1 + 0.4)], VSTONE, n=8, rot=rot)


def dome():
    mb = MB("SG_Craft_Dome", "16_CRAFT", random.Random(8102), detail="near")
    dome_scales(mb)
    # nervuras de prata de secao REDONDA assentadas sobre as escamas, com pe no anel de apoio
    for a in DOME_RIB_A:
        ar = math.radians(a)
        pts = []
        ph_top = math.acos((LAN_R + 0.75) / DOME_R)
        for k in range(11):
            phi = ph_top * k / 10.0
            r, z = _dome_pt(phi, 0.36)
            pts.append((CX + r * math.cos(ar), CY + r * math.sin(ar), Z + z))
        up = (-math.sin(ar), math.cos(ar), 0.0)
        mb.sweep(pts, [(0.27 * math.cos(2 * math.pi * k / 6), 0.27 * math.sin(2 * math.pi * k / 6)) for k in range(6)],
                 SILVER, up=up)
        fbox(mb, fr(a), -0.42, 0.42, 15.55, 16.55, H + 0.95, H + 1.35, SILVER, 0.04)
    lanternim(mb)
    flask(mb)
    # icone da empena (ajuste 19) neste MB: bronze, ambar (Window_Warm) e branco (Flower_White) ja estao aqui - so o
    # vidro do icone e MeshPart nova (compensada no caldeirao: crescente da placa no violeta da pocao)
    alchemy_icon(mb, FD, PORT_Y1 + 0.12, H + 2.55)
    mb.finish()
    # cobertura (colisao): octogono no topo da parede
    ngon_col("SG_CraftRoof", CX, CY, 8, R_OUT + 0.8, Z + H, Z + DOME_Z + 1.0)


# ------------------------------------------------------------------ o FRASCO GIGANTE (07.01)
FLASK_B = LAN_Z1 + 0.4                   # fundo chato do frasco (assenta na cornija do lanternim)
FL = [(2.4, FLASK_B), (3.5, FLASK_B + 0.25), (4.4, FLASK_B + 0.75), (5.05, FLASK_B + 1.5), (5.45, FLASK_B + 2.4),
      (5.6, FLASK_B + 3.4), (5.52, FLASK_B + 4.4), (5.25, FLASK_B + 5.4), (4.75, FLASK_B + 6.4), (4.0, FLASK_B + 7.3),
      (3.1, FLASK_B + 8.0), (2.3, FLASK_B + 8.55), (1.82, FLASK_B + 9.0), (1.6, FLASK_B + 9.8), (1.5, FLASK_B + 11.0),
      (1.46, FLASK_B + 12.0), (1.64, FLASK_B + 12.15), (1.8, FLASK_B + 12.4)]
LIQ_V = FLASK_B + 2.75                   # nivel do liquido (terco de baixo do bojo) = eixo da CINTA
RING_Z = FLASK_ZC                        # nascenca dos aneis (mancais)
RING_DEF = ((18.0, 0.0, 7.9, 4.2), (-34.0, 90.0, 9.9, -3.4))    # (inclinacao, azimute do eixo, raio, rpm)


def _fl_r(v):
    return _r_at(FL, v)


def _ring_frame(tilt, azim):
    t, p = math.radians(tilt), math.radians(azim)
    ct, st, cp, sp = math.cos(t), math.sin(t), math.cos(p), math.sin(p)

    def W(lx, ly, lz):
        ly, lz = ly * ct - lz * st, ly * st + lz * ct
        return (CX + lx * cp - ly * sp, CY + lx * sp + ly * cp, Z + RING_Z + lz)
    return W


def flask(mb):
    """o FRASCO GIGANTE em VIDRO PINTADO (opaco: le sem transparencia no Roblox): fundo chato, bojo em PERA, ombro,
    gargalo afunilado e ARO virado; o liquido violeta ESCURO (Neon fraco) so no terco de baixo, CINTA de bronze no
    nivel, faixa de REFLEXO, colar no gargalo, TAMPA de bronze com florao; BERCO de 4 ESTRIBOS de prata rebitados que
    sobem do lanternim, abracam o bojo e seguram os MANCAIS dos 2 aneis armilares"""
    x, y = CX, CY
    iv = next(i for i, (r, v) in enumerate(FL) if v > LIQ_V)
    rl = _fl_r(LIQ_V)
    lathe(mb, x, y, Z, [(0.0, FLASK_B)] + FL[:iv] + [(rl, LIQ_V), (0.0, LIQ_V)], VSOFT, n=24,
          sm=set(range(1, iv + 1)))
    glass = [(0.0, LIQ_V - 0.02), (rl, LIQ_V - 0.02)] + FL[iv:] + [(1.55, FLASK_B + 12.4)]
    lathe(mb, x, y, Z, glass, GLAZE, n=24, sm=set(range(1, len(glass) - 5)), cap0=True, cap1=False)
    # cinta de bronze no nivel (esconde a emenda liquido/vidro)
    r0, r1 = _fl_r(LIQ_V - 0.28), _fl_r(LIQ_V + 0.28)
    revolve(mb, (x, y, Z), [(r0 - 0.05, LIQ_V - 0.3), (r0 + 0.14, LIQ_V - 0.26), (max(r0, r1) + 0.18, LIQ_V),
                            (r1 + 0.14, LIQ_V + 0.26), (r1 - 0.05, LIQ_V + 0.3)], BRONZE, n=24,
            smooth_edges={0, 1, 2, 3})
    # colar do gargalo e TAMPA de bronze (sobre o aro) + florao de prata
    revolve(mb, (x, y, Z), [(1.7, FLASK_B + 8.95), (2.02, FLASK_B + 9.0), (2.02, FLASK_B + 9.4), (1.62, FLASK_B + 9.45)],
            BRONZE, n=16, smooth_edges={1})
    tb = FLASK_B + 12.25
    lathe(mb, x, y, Z, [(0.0, tb), (1.66, tb), (1.98, tb + 0.14), (2.0, tb + 0.55), (1.84, tb + 0.74), (1.3, tb + 0.98),
                        (0.72, tb + 1.12), (0.46, tb + 1.3), (0.52, tb + 1.6), (0.3, tb + 1.78), (0.0, tb + 1.82)],
          BRONZE, n=16, sm={3, 4, 5, 6})
    CA.finial(mb, x, y, Z + tb + 1.76, 1.4)
    # REFLEXO: faixa em crescente sobre o vidro (casca fina fechada), do lado que o jogador ve (rua e porta)
    for ac, v0, v1, wmax in ((151.0, FLASK_B + 4.0, FLASK_B + 7.2, 0.085), (163.0, FLASK_B + 6.5, FLASK_B + 7.4, 0.035)):
        highlight(mb, math.radians(ac), v0, v1, wmax)
    # BERCO: 4 estribos (0/90/180/270 = eixos dos mancais), rebites, bracos e MANCAIS dos aneis
    vs = [LAN_Z1 + 0.35, FLASK_B + 0.45, FLASK_B + 1.1, FLASK_B + 1.9, FLASK_B + 2.75, FLASK_B + 3.6, RING_Z,
          FLASK_B + 5.3]
    prof = [(-0.25, -0.12), (0.25, -0.12), (0.25, 0.12), (-0.25, 0.12)]
    for k in range(4):
        a = math.radians(90.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + (max(_fl_r(v), 3.45) + 0.26) * ca, y + (max(_fl_r(v), 3.45) + 0.26) * sa, Z + v) for v in vs]
        vt = FLASK_B + 5.9
        pts += [(x + (_fl_r(vt) + 0.16) * ca, y + (_fl_r(vt) + 0.16) * sa, Z + vt)]
        mb.sweep(pts, prof, SILVER, True, None, up=(ca, sa, 0.0))
        for v in (LIQ_V, FLASK_B + 1.4):
            rr = _fl_r(v) + 0.4
            mb.cyl(0.1, 0.1, (x + rr * ca, y + rr * sa, Z + v), (0.0, math.pi / 2, a), BRONZE, n=6, bevel=0.0)
        # braco do mancal: do estribo ate o anel (horizontal, com mao-francesa por baixo)
        idx = 0 if k in (0, 2) else 1
        tilt, azim, R, rpm = RING_DEF[idx]
        r0 = _fl_r(RING_Z) + 0.36
        r1 = R - 0.62
        mb.sweep([(x + r0 * ca, y + r0 * sa, Z + RING_Z), (x + r1 * ca, y + r1 * sa, Z + RING_Z)],
                 [(-0.18, -0.2), (0.18, -0.2), (0.18, 0.2), (-0.18, 0.2)], SILVER, True, None, up=(0.0, 0.0, 1.0))
        rb = _fl_r(FLASK_B + 2.2) + 0.3
        mb.rod((x + rb * ca, y + rb * sa, Z + FLASK_B + 2.2), (x + (r1 - 0.2) * ca, y + (r1 - 0.2) * sa, Z + RING_Z - 0.15),
               0.09, SILVER, 6)
        # mancal: bloco de bronze que abraca a banda do anel no eixo de inclinacao
        W = _ring_frame(tilt, azim)
        sgn = 1.0 if k in (0, 1) else -1.0
        pc = W(sgn * R, 0.0, 0.0)
        mb.box((1.25, 0.56, 0.5), pc, (math.radians(tilt), 0.0, math.radians(azim)), BRONZE, 0.05)


def highlight(mb, ac, v0, v1, wmax, n=8):
    """REFLEXO pintado no vidro: crescente fino (casca fechada rente ao bojo) no rumo ac, de v0 a v1"""
    bm = mb.bm
    x, y = CX, CY
    rows = []
    for k in range(n + 1):
        v = v0 + (v1 - v0) * k / n
        w = wmax * math.sin(math.pi * k / n) ** 0.8 + 0.006
        a_c = ac + 0.02 * math.sin(math.pi * k / n)                    # leve curva (acompanha o bojo)
        r = _fl_r(v)
        row = []
        for off in (0.03, 0.065):
            for s in (-1, 1):
                a = a_c + s * w
                row.append(bm.verts.new((x + (r + off) * math.cos(a), y + (r + off) * math.sin(a), Z + v)))
        rows.append(row)                                                 # [in-, in+, out-, out+]
    fs = []
    for A, B in zip(rows, rows[1:]):
        for i0, i1 in ((2, 3), (1, 0), (0, 2), (3, 1)):
            fs.append(bm.faces.new((A[i0], A[i1], B[i1], B[i0])))
    fs.append(bm.faces.new((rows[0][0], rows[0][1], rows[0][3], rows[0][2])))
    fs.append(bm.faces.new((rows[-1][2], rows[-1][3], rows[-1][1], rows[-1][0])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], "Flower_White", None, 0, 1)


def energy_rings():
    """2 ANEIS ARMILARES de prata (07.01): banda chata de 0,9 em U (bordas levantadas) com fio de energia violeta
    ESCURO no fundo e 16 marcas de graduacao em relevo. Presos nos MANCAIS dos estribos (eixo de inclinacao) e girando
    no PROPRIO plano (eixo = normal do anel): gira sem flutuar. Pecas moveis como as do summon."""
    for idx, (tilt, azim, R, rpm) in enumerate(RING_DEF, 1):
        vf = MB("VFX_SGCRAFT_Ring_%d" % idx, "12_VFX_HELPERS", random.Random(8110 + idx), detail="near")
        W = _ring_frame(tilt, azim)
        nrm = W(0.0, 0.0, 1.0)
        up = (nrm[0] - CX, nrm[1] - CY, nrm[2] - Z - RING_Z)
        NP = 40
        pts = [W(R * math.cos(2 * math.pi * k / NP), R * math.sin(2 * math.pi * k / NP), 0.0) for k in range(NP + 1)]
        vf.sweep(pts, [(-0.45, -0.07), (0.45, -0.07), (0.45, 0.11), (0.35, 0.11), (0.35, 0.03), (-0.35, 0.03),
                       (-0.35, 0.11), (-0.45, 0.11)], SILVER, up=up, caps=False)
        vf.sweep(pts, [(-0.09, 0.02), (0.09, 0.02), (0.09, 0.055), (-0.09, 0.055)], VSOFT, up=up, caps=False)
        for k in range(16):
            th = 2 * math.pi * (k + 0.5) / 16.0
            long_ = k % 4 == 0
            a = W((R - (0.3 if long_ else 0.22)) * math.cos(th), (R - (0.3 if long_ else 0.22)) * math.sin(th), 0.07)
            b = W((R - 0.14) * math.cos(th), (R - 0.14) * math.sin(th), 0.07)
            vf.rod(a, b, 0.05, SILVER, 4)
        ob = vf.finish()
        n = Vector(up).normalized()
        ob["pivot"] = [round(CX, 3), round(CY, 3), round(Z + RING_Z, 3)]
        ob["axis"] = [round(n.x, 4), round(n.y, 4), round(n.z, 4)]
        ob["rpm"] = rpm
        ob["vfx"] = "anel armilar %d do frasco do craft: gira no proprio plano, guiado pelos mancais dos estribos" % idx


# ------------------------------------------------------------------ interior: piso, estrado, circulo magico, abobada
def dome_shell(mb, r_lo, rise_lo, r_hi, rise_hi, z0, m, n=24, rings=6):
    """abobada fechada (intradorso + extradorso + anel da base) - a de dentro e vista de baixo"""
    bm = mb.bm

    def surf(r, rise):
        rows = []
        for k in range(rings):
            phi = (math.pi / 2) * k / rings
            rr, zz = r * math.cos(phi), Z + z0 + rise * math.sin(phi)
            rows.append([bm.verts.new((CX + rr * math.cos(2 * math.pi * i / n), CY + rr * math.sin(2 * math.pi * i / n), zz))
                         for i in range(n)])
        top = bm.verts.new((CX, CY, Z + z0 + rise))
        return rows, top
    lo, tlo = surf(r_lo, rise_lo)
    hi, thi = surf(r_hi, rise_hi)
    for rows, top in ((lo, tlo), (hi, thi)):
        for r0, r1 in zip(rows, rows[1:]):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        for i in range(n):
            bm.faces.new((rows[-1][i], rows[-1][(i + 1) % n], top))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[0][j], lo[0][i], hi[0][i], hi[0][j]))
    faces = mb._post([v for r in lo + hi for v in r] + [tlo, thi], m, None, 0, 1)
    sph_uv(mb, faces, m, Z + z0, r_lo)


def flat_stroke(mb, pts, w, z0, z1, m):
    """traco de glifo DEITADO: cada segmento da polilinha (x, y) e um prisma convexo de largura w (juntas sobrepostas)"""
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        dx, dy = xb - xa, yb - ya
        Ln = math.hypot(dx, dy)
        if Ln < 1e-4:
            continue
        ux, uy = dx / Ln, dy / Ln
        nx, ny = -uy * w / 2.0, ux * w / 2.0
        e = w * 0.35
        a = (xa - ux * e, ya - uy * e)
        b = (xb + ux * e, yb + uy * e)
        mb.prism([(a[0] - nx, a[1] - ny), (b[0] - nx, b[1] - ny), (b[0] + nx, b[1] + ny), (a[0] + nx, a[1] + ny)],
                 z0, z1, m)


def floor_glyph(mb, c, ang, k, sc=1.55, m=VSOFT):
    """runa k do ALFABETO UNICO da ilha (sg_court.RUNE_SEGS: haste + ramos diagonais, angular) deitada e EMBUTIDA
    no marmore (sobe 0,07 acima do piso); c = centro (x, y), ang = rumo do 'alto' do glifo"""
    ex, ey = math.cos(ang), math.sin(ang)          # alto do glifo
    tx, ty = -ey, ex                               # lateral

    def P(u, w):
        return (c[0] + (tx * u + ex * w) * sc, c[1] + (ty * u + ey * w) * sc)
    z0, z1 = Z + 0.0, Z + 0.07
    wd = 0.14
    for (a0, b0), (a1, b1) in RUNE_SEGS[k % len(RUNE_SEGS)]:
        flat_stroke(mb, [P(a0, b0), P(a1, b1)], wd, z0, z1, m)


def magic_circle(mb):
    """CIRCULO MAGICO no piso em volta do estrado (07.07): anel fino de energia (Neon ESCURO) rente, anel de bronze
    embutido como moldura e 10 GLIFOS do alfabeto unico (sg_court.RUNE_SEGS) EMBUTIDOS, em sequencia fixa; as 2 lanternas
    da porta (POST_A) sao as ancoras do circulo (sem glifo embaixo delas)"""
    ring_band(mb, 8.82, 9.0, 0.03, 0.07, VSOFT, 0.0, 360.0, 10.0)
    ring_band(mb, 7.1, 7.25, 0.03, 0.075, IRON, 0.0, 360.0, 10.0)
    i = 0
    for k in range(12):
        a = 15.0 + 30.0 * k
        if min(abs(a - p) for p in POST_A) < 20.0:
            continue
        c = pol(8.05, a, 0.0)
        floor_glyph(mb, c, math.radians(a), OBELISK_RUNES[i % len(OBELISK_RUNES)])
        i += 1


def dais_step(mb, r, z0, z1, n=30):
    """degrau do estrado: corpo de obsidiana, tampo de marmore negro embutido e fio de FERRO escuro na borda (o ouro vivo saiu)"""
    lathe(mb, CX, CY, Z, [(0.0, z0), (r, z0), (r, z1 - 0.06), (r - 0.06, z1), (0.0, z1)], OBS, n=n)
    lathe(mb, CX, CY, Z, [(0.0, z1 - 0.02), (r - 0.55, z1 - 0.02), (r - 0.55, z1 + 0.02), (0.0, z1 + 0.02)], MARB, n=n)
    ring_band(mb, r - 0.55, r - 0.3, z1 - 0.02, z1 + 0.03, IRON, 0.0, 360.0, 360.0 / n)


def pear_rib(w, dep):
    """perfil de nervura em PERA (igual ao salao, 04.04): (profundidade para dentro da sala, largura)"""
    h = w / 2.0
    pts = [(-h, 0.12), (h, 0.12), (h, -dep * 0.25), (h * 0.62, -dep * 0.66), (0.0, -dep), (-h * 0.62, -dep * 0.66),
           (-h, -dep * 0.25)]
    return [(-b, a) for a, b in pts]


def rosette(mb, cx, cy, zt, R, dep, m, petals=8, n=24):
    """FLORAO pendente (chave da abobada): rosa de 'petals' petalas, do teto (zt) descendo 'dep'"""
    bm = mb.bm
    k = petals / 2.0
    rows = []
    for f, h, mod in ((1.0, 0.0, True), (1.0, 0.12, True), (0.8, 0.45, True), (0.55, 0.78, True)):
        rows.append([bm.verts.new((cx + R * f * (0.72 + 0.28 * abs(math.cos(k * a))) * math.cos(a),
                                   cy + R * f * (0.72 + 0.28 * abs(math.cos(k * a))) * math.sin(a), zt - dep * h))
                     for a in [2 * math.pi * i / n for i in range(n)]])
    fs = [bm.faces.new(rows[0])]
    for A, B in zip(rows, rows[1:]):
        for i in range(n):
            j = (i + 1) % n
            fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    pole = bm.verts.new((cx, cy, zt - dep))
    for i in range(n):
        fs.append(bm.faces.new((rows[-1][i], rows[-1][(i + 1) % n], pole)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_] + [pole], m, None, 0, 1)


PLASTER_IN = "Stone_SG_Castle"      # reboco liso de valor MEDIO (o bege do Plaster_SG virava sala da vila)
WAINSCOT_RUNS = [(210.0, 240.0), (300.0, 345.0), (15.0, 60.0), (120.0, 150.0)]
PILASTERS = {45.0: 0.0, 135.0: 0.0, 225.0: 0.0, 315.0: 0.0, 90.0: 9.1, 270.0: 9.1}   # vertice: pe (o de 0 fica atras
#                                                                  da prateleira da bancada: nao nasce no ar)
PROF_WAINSCOT = [(0.05, 0.0), (-0.16, 0.0), (-0.16, 0.42), (-0.1, 0.5), (-0.08, 0.5), (-0.08, 2.7), (-0.14, 2.74),
                 (-0.22, 2.86), (-0.22, 3.0), (0.05, 3.0)]


def walls_in(mb):
    """PAREDE INTERNA (08.01 / 14.07): LAMBRIL de madeira ate +3 (rodape, campo, cimalha) com painel almofadado e
    montante por face; REBOCO liso acima; PILASTRAS de pedra nas juntas das nervuras (base, fuste, capitel) subindo
    ate as misulas; o reboco quebra o 24-gono navy chapado"""
    ap = YB_IN
    ring_band(mb, R_IN - 0.05, R_IN - 0.01, 2.9, 17.45, PLASTER_IN, A0, A1)
    for a0, a1 in WAINSCOT_RUNS:
        poly_ring(mb, PROF_WAINSCOT, a0, a1, WOOD, ap=ap)
        n = int(round((a1 - a0) / STEP))
        for k in range(n):
            phi = a0 + STEP * (k + 0.5)
            F = fr(phi)
            fbox(mb, F, -1.28, 1.28, ap - 0.15, ap - 0.06, 0.78, 2.46, WOOD, 0.04)       # almofada
            v = a0 + STEP * k
            if k > 0 and (v % 360.0) not in PILASTERS:
                fbox(mb, fr(v), -0.2, 0.2, R_IN - 0.2, R_IN + 0.02, 0.5, 2.72, WOOD, 0.03)  # montante na junta
    for v, foot in PILASTERS.items():
        F = fr(v)
        if foot == 0.0:
            fbox(mb, F, -0.6, 0.6, R_IN - 0.62, R_IN + 0.02, 0.0, 0.34, VSTONE, 0.05)
            fbox(mb, F, -0.54, 0.54, R_IN - 0.56, R_IN + 0.02, 0.34, 0.62, VSTONE, 0.04)
            f0 = 0.62
        else:
            fbox(mb, F, -0.54, 0.54, R_IN - 0.56, R_IN + 0.02, foot, foot + 0.24, VSTONE, 0.04)
            f0 = foot + 0.24
        fbox(mb, F, -0.44, 0.44, R_IN - 0.48, R_IN + 0.02, f0, 15.55, OBS, 0.05)      # rompe o friso (mais saliente)
        fbox(mb, F, -0.54, 0.54, R_IN - 0.58, R_IN + 0.02, 15.55, 15.78, VSTONE, 0.04)
        fbox(mb, F, -0.6, 0.6, R_IN - 0.68, R_IN + 0.02, 15.78, 16.0, VSTONE, 0.04)


def interior(mb):
    """piso, estrado, circulo e abobada (no mesmo objeto da mobilia - os materiais sao os mesmos, menos MeshParts)"""
    # ESTRADO circular de 2 degraus (obsidiana + tampo de marmore negro + fio de bronze): o caldeirao sobe no palco
    dais_step(mb, DAIS_R1, -0.3, DAIS_H1)
    dais_step(mb, DAIS_R2, DAIS_H1, DAIS_H2)
    # piso nobre radial (topo 0,05 acima do piso; a colisao e a do P2): marmore negro com incrustacao de prata
    for r0, r1, m, st in ((DAIS_R1 + 0.05, 6.45, SILVER, 12.0), (6.45, 9.85, MARB, 12.0), (9.85, 10.1, SILVER, 12.0),
                          (10.1, R_IN + 0.1, MARB, STEP)):
        ring_band(mb, r0, r1, -0.3, 0.05, m, 0.0, 360.0, st)
    magic_circle(mb)
    walls_in(mb)
    # frisos internos: friso violeta sobre as estantes, cornija violeta
    ring_band(mb, R_IN - 0.4, R_IN + 0.05, 9.16, 9.4, VSTONE, A0, A1)
    ring_band(mb, R_IN - 0.6, R_IN + 0.05, 17.4, 18.0, VSTONE, 0.0, 360.0)
    # abobada de marmore negro + nervuras em PERA apoiadas em misulas de obsidiana + chave em FLORAO
    dome_shell(mb, R_IN, IN_DOME_RISE, R_IN + 0.4, IN_DOME_RISE + 0.4, H, MARB)
    for a in RIB_A:
        ar = math.radians(a)
        pts = []
        for k in range(9):
            phi = (math.pi / 2) * 0.9 * k / 8.0
            rr = (R_IN - 0.06) * math.cos(phi)
            if rr < 1.0:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + H + (IN_DOME_RISE - 0.06) * math.sin(phi)))
        mb.sweep(pts, pear_rib(0.62, 0.5), TRIM, up=(-math.sin(ar), math.cos(ar), 0.0))
        F = fr(a)
        if a != DOOR:
            fbox(mb, F, -0.5, 0.5, R_IN - 0.8, R_IN + 0.02, 16.0, 17.4, OBS, 0.05)
    rosette(mb, CX, CY, Z + H + IN_DOME_RISE - 0.05, 1.35, 0.85, TRIM)
    # colisao do estrado: um 10-gono por degrau (o jogador sobe: espelhos 0,7), apotema ~ raio do desenho
    ngon_col("SG_CraftDais", CX, CY, 10, DAIS_R1 + 0.25, Z - 0.3, Z + DAIS_H1)
    ngon_col("SG_CraftDais", CX, CY, 10, DAIS_R2 + 0.25, Z + DAIS_H1, Z + DAIS_H2)


# ------------------------------------------------------------------ o CALDEIRAO (hero prop) - no estrado
# perfil EXTERNO do bojo (raio, altura sobre o P2): fundo quase chato, barriga em 4,2, ombro, pescoco em 5,52
CAUL = [(0.0, 2.55), (0.9, 2.58), (1.7, 2.76), (2.35, 3.06), (2.8, 3.46), (3.04, 3.86), (3.12, 4.22), (3.06, 4.6),
        (2.88, 4.98), (2.64, 5.3), (2.5, 5.52)]
# BOCA enrolada (latao): sai do pescoco, rola para fora (3,0) e volta por dentro ate abaixo do nivel da pocao
LIP = [(2.5, 5.52), (2.58, 5.66), (2.8, 5.78), (2.96, 5.92), (3.0, 6.06), (2.94, 6.18), (2.78, 6.25), (2.6, 6.25),
       (2.46, 6.16), (2.4, 5.95), (2.36, 5.72), (0.0, 5.66)]
HEARTH_Z0, HEARTH_Z1 = DAIS_H2, 1.95            # lareira: do tampo do estrado ate 1,95 (+ capa ate 2,05)
LIQ_Z = 5.84                                   # superficie da pocao
BELLY_Z = 4.22                                 # altura do medalhao (a camera CU_Emblem mira em 4,0)


def caul_r(h):
    """raio externo do bojo na altura h (P2)"""
    for (ra, ha), (rb, hb) in zip(CAUL, CAUL[1:]):
        if ha <= h <= hb and hb > ha:
            return ra + (rb - ra) * (h - ha) / (hb - ha)
    return CAUL[-1][0] if h > CAUL[-1][1] else 0.0


def hug(h0, h1, t, steps=4):
    """perfil de uma CINTA que abraca o bojo de h0 a h1 (espessura t, bordas arredondadas): segue a curva do corpo"""
    pts = [(caul_r(h0) - 0.02, h0), (caul_r(h0 + 0.03) + t * 0.7, h0 + 0.03)]
    for k in range(steps + 1):
        h = h0 + 0.07 + (h1 - h0 - 0.14) * k / steps
        pts.append((caul_r(h) + t, h))
    pts += [(caul_r(h1 - 0.03) + t * 0.7, h1 - 0.03), (caul_r(h1) - 0.02, h1)]
    return pts


MED_Z, MED_R, MED_CD = 4.28, 0.62, 0.02       # medalhao: altura do centro, raio do emblema, frente do disco
MED_RI, MED_RO = 0.64, 0.86                    # espelho: labio (cobre a borda do disco, R 0,69) / pe


def medal_bezel(mb, O, f, n=24):
    """espelho de latao do medalhao: para cada angulo em volta do eixo f, perfil fechado cujo PE fica 0,04 dentro do
    bojo e 0,09 fora dele (segue a curvatura real: sela), rampa ate o labio plano na frente do disco. Cobre tambem a
    cinta de ferro que passa por baixo."""
    bm = mb.bm
    side = Vector((-f.y, f.x, 0.0))
    up = Vector((0.0, 0.0, 1.0))
    R0 = caul_r(MED_Z)

    def sdep(rho, th):
        a, b = rho * math.cos(th), rho * math.sin(th)
        R = caul_r(MED_Z + b)
        return math.sqrt(max(R * R - a * a, 0.0)) - R0

    def P(rho, th, d):
        return O + f * d + side * (rho * math.cos(th)) + up * (rho * math.sin(th))
    lip = MED_CD + 0.08
    loops = []
    rivets = []
    for i in range(n):
        th = 2 * math.pi * i / n
        so, sm, si = sdep(MED_RO, th), sdep(MED_RO - 0.05, th), sdep(MED_RI, th)
        prof = [(MED_RO, so - 0.04), (MED_RO, so + 0.06), (MED_RO - 0.05, sm + 0.09), (MED_RI + 0.06, lip),
                (MED_RI, lip), (MED_RI - 0.01, MED_CD + 0.012), (MED_RI, si - 0.12)]
        loops.append([bm.verts.new(P(r, th, d)) for r, d in prof])
    K = len(loops[0])
    for i in range(n):
        A, B = loops[i], loops[(i + 1) % n]
        for k in range(K):
            k2 = (k + 1) % K
            bm.faces.new((A[k], A[k2], B[k2], B[k]))
    mb._post([v for L_ in loops for v in L_], GOLD, None, 0, 1)
    for q in range(4):
        th = math.pi / 4 + q * math.pi / 2
        rho = 0.76
        sm = sdep(MED_RO - 0.05, th) + 0.09
        t = (MED_RO - 0.05 - rho) / (MED_RO - 0.05 - MED_RI - 0.06)
        mb.ico(0.05, tuple(P(rho, th, sm + (lip - sm) * t + 0.015)), BIRON, 1)


def _ring_ok(pin, R, tr, phi):
    """a argola (plano radial-vertical) pendurada no pino com balanco phi para fora nao entra no bojo?"""
    cr, ch = pin[0] + R * math.sin(phi), pin[1] - R * math.cos(phi)
    for k in range(36):
        th = 2 * math.pi * k / 36
        pr, ph = cr + R * math.cos(th), ch + R * math.sin(th)
        if math.hypot(pr - pin[0], ph - pin[1]) < 0.28:
            continue
        if CAUL[0][1] <= ph <= CAUL[-1][1] and pr - tr < caul_r(ph) + 0.02:
            return False
    return True


def paw_leg(mb, ang):
    """PATA de ferro fundido (07.03): perna em S (perfil radial extrudado) que nasce da barriga do bojo e desce ate a
    sapata de 3 DEDOS apoiada na capa da lareira"""
    F = fr(math.degrees(ang))
    zf = HEARTH_Z1 + 0.1
    outer = [(caul_r(3.62) - 0.06, 3.62), (3.08, 3.3), (3.14, 2.96), (3.02, 2.66), (3.1, zf + 0.2)]
    inner = [(2.7, zf + 0.2), (2.62, 2.58), (2.58, 2.84), (2.36, 3.08), (caul_r(3.12) - 0.2, 3.12)]
    pts = outer + inner
    # fatias convexas (perfil em S): quadrilateros entre a borda de fora e a de dentro
    for (a, b), (c, d) in zip(zip(outer, outer[1:]), zip(reversed(inner), list(reversed(inner))[1:])):
        pside(mb, F, [a, b, d, c], -0.19, 0.19, IRON)
    # sapata e 3 dedos
    fbox(mb, F, -0.3, 0.3, 2.62, 3.22, zf, zf + 0.22, IRON, 0.05)
    for t in (-0.42, 0.0, 0.42):
        c = F.p(0.0, 3.02, zf + 0.1)
        d = (math.cos(F.a + math.pi / 2 + t), math.sin(F.a + math.pi / 2 + t))
        p = (c[0] + d[0] * 0.3, c[1] + d[1] * 0.3, c[2])
        mb.box((0.46, 0.17, 0.2), p, (0.0, 0.0, F.a + math.pi / 2 + t), IRON, 0.05)


def ear_lug(mb, ang, pin):
    """ORELHA fundida (07.03): 2 chapas em D abracando a argola, nascendo do ombro do bojo, com o pino de bronze"""
    F = fr(math.degrees(ang))
    pr, pz = pin
    pts = [(caul_r(4.62) - 0.08, 4.62), (pr - 0.1, 4.7)]
    for k in range(7):
        t = -1.2 + 2.4 * k / 6.0
        pts.append((pr + 0.27 * math.cos(t), pz + 0.27 * math.sin(t)))
    pts += [(pr - 0.1, pz + 0.34), (caul_r(5.44) - 0.08, 5.44)]
    for u0, u1 in ((0.1, 0.22), (-0.22, -0.1)):
        pside(mb, F, pts, u0, u1, IRON)


def hearth_embers(mb, x, y):
    """BRASA (07.04): leito de brasa violeta ESCURA, 7 CARVOES facetados em volta de 1 central cobrindo o leito (so as
    frestas brilham) e GRELHA de ferro de 4 barras apoiada no anel da lareira, sob o fundo do bojo"""
    lathe(mb, x, y, Z, [(0.0, HEARTH_Z0), (2.3, HEARTH_Z0), (2.3, 1.5), (0.0, 1.5)], BIRON, n=16)
    lathe(mb, x, y, Z, [(0.0, 1.5), (1.3, 1.5), (1.25, 1.56), (0.0, 1.57)], VSOFT, n=10)
    coals = [(0.0, 0.0, 0.44, 0.0), (0.82, 20.0, 0.44, 40.0), (0.86, 95.0, 0.42, 10.0), (0.8, 165.0, 0.44, 70.0),
             (0.85, 240.0, 0.43, 25.0), (0.82, 310.0, 0.42, 55.0),
             (1.56, 0.0, 0.42, 5.0), (1.6, 50.0, 0.4, 80.0), (1.55, 102.0, 0.42, 30.0), (1.6, 150.0, 0.4, 60.0),
             (1.57, 205.0, 0.42, 15.0), (1.6, 258.0, 0.4, 45.0), (1.55, 308.0, 0.41, 75.0)]
    for r, a, s, rot in coals:
        ar = math.radians(a)
        mb.ico(s, (x + r * math.cos(ar), y + r * math.sin(ar), Z + 1.46 + s * 0.3), OBS, 1,
               scale=(1.15, 0.9, 0.55), rot=(0.25, 0.1, math.radians(rot)))
    for k in range(4):
        yy = -1.2 + 0.8 * k
        hl = math.sqrt(max(0.0, 2.32 ** 2 - yy * yy))
        mb.box((2 * hl, 0.12, 0.12), (x, y + yy, Z + HEARTH_Z1 - 0.08), (0, 0, 0), BIRON, 0.0)
    mb.box((0.12, 4.62, 0.1), (x, y, Z + HEARTH_Z1 - 0.02), (0, 0, 0), BIRON, 0.0)


def cauldron():
    mb = MB("SG_Craft_Cauldron", "16_CRAFT", random.Random(8105), detail="hero")
    x, y = CX, CY
    # LAREIRA: anel de obsidiana com 4 bocas de ventilacao estreitas (0/90/180/270) sob uma CAPA continua de pedra
    # violeta (a capa passa por cima das bocas como verga); dentro, carvoes sobre o leito e a grelha
    for a0 in (10.0, 100.0, 190.0, 280.0):
        ring_band(mb, 2.25, 3.4, HEARTH_Z0, HEARTH_Z1, OBS, a0, a0 + 70.0, 7.0)
    ring_band(mb, 2.16, 3.5, HEARTH_Z1, HEARTH_Z1 + 0.1, VSTONE, 0.0, 360.0, 7.5)
    hearth_embers(mb, x, y)
    # 4 PATAS de ferro fundido (diagonais: o medalhao da porta e as argolas ficam livres)
    for k in range(4):
        paw_leg(mb, math.radians(45.0 + 90.0 * k))
    # BOJO (ferro, normais lisas) + BOCA enrolada de BRONZE envelhecido - uma so silhueta, transicao no pescoco
    lathe(mb, x, y, Z, CAUL, IRON, n=24, cap1=False, sm=set(range(1, len(CAUL) - 1)))
    lathe(mb, x, y, Z, LIP, GOLD, n=24, cap0=False, sm={0, 1, 2, 3, 4, 5, 6, 7, 8})
    # CINTA de ferro negro abracando a barriga (o medalhao e rebitado nela) + rebites de ferro rentes
    lathe(mb, x, y, Z, hug(BELLY_Z - 0.26, BELLY_Z + 0.26, 0.08), BIRON, n=24, cap0=False, cap1=False, sm="all")
    for k in range(12):
        a = 15.0 + 30.0 * k
        if min(abs(a - 180.0), abs(a), abs(a - 360.0)) < 25.0:
            continue
        ar = math.radians(a)
        rr = caul_r(BELLY_Z) + 0.1
        mb.cyl(0.05, 0.05, (x + rr * math.cos(ar), y + rr * math.sin(ar), Z + BELLY_Z), (math.pi / 2, 0.0, ar + math.pi / 2),
               IRON, n=6, bevel=0.0)
    # MEDALHAO DA ORDEM (porta e alquimista): disco de obsidiana (sg_emblem.plaque) rente ao ferro, preso por um
    # ESPELHO que ABRACA o bojo
    for ang in (math.pi, 0.0):
        f = Vector((math.cos(ang), math.sin(ang), 0.0))
        O = Vector((x, y, Z + MED_Z)) + f * caul_r(MED_Z)
        medal_bezel(mb, O, f)
        # ov12: crescente aceso SO aqui; ajuste 19: no violeta da POCAO (VDEEP, o foco da sala) em vez da lavanda
        # SG_Rune_Glow - uma MeshPart a menos no caldeirao (paga o vidro do icone da empena)
        EM.plaque(mb, mb, mb, mb, tuple(O + f * MED_CD), ang, MED_R, glow=VDEEP)
    # ORELHAS fundidas com ARGOLA (norte e sul)
    pin = (3.3, 5.02)
    Rr, tr = 0.42, 0.075
    phi = next((math.radians(d) for d in range(0, 80, 2) if _ring_ok(pin, Rr, tr, math.radians(d))), math.radians(60))
    for ang in (math.pi / 2, -math.pi / 2):
        ca, sa = math.cos(ang), math.sin(ang)
        ear_lug(mb, ang, pin)
        tx, ty = -sa, ca
        pc = (x + pin[0] * ca, y + pin[0] * sa, Z + pin[1])
        mb.rod((pc[0] - 0.26 * tx, pc[1] - 0.26 * ty, pc[2]), (pc[0] + 0.26 * tx, pc[1] + 0.26 * ty, pc[2]), 0.07, GOLD, 6)
        cr, ch = pin[0] + Rr * math.sin(phi), pin[1] - Rr * math.cos(phi)
        pts = [(x + (cr + Rr * math.cos(2 * math.pi * j / 16)) * ca, y + (cr + Rr * math.cos(2 * math.pi * j / 16)) * sa,
                Z + ch + Rr * math.sin(2 * math.pi * j / 16)) for j in range(17)]
        mb.tube(pts, tr, GOLD, 6)
    # POCAO violeta: o UNICO foco violeta da sala (15.02) + 3 bolhas + colher de pau apoiada no labio
    mb.cyl(2.39, 0.1, (x, y, Z + LIQ_Z - 0.05), (0, 0, 0), VDEEP, n=24, bevel=0.0)
    for (dx, dy, r) in ((-0.78, 0.65, 0.26), (0.26, -1.04, 0.2), (1.05, 0.3, 0.14)):
        mb.ico(r, (x + dx, y + dy, Z + LIQ_Z), VDEEP, 1, scale=(1, 1, 0.55))
    a = math.radians(40.0)
    d0, d1 = (1.3, 5.55), (2.6, 6.25 + 0.1)             # apoia na quina de DENTRO do labio
    sl = (d1[1] - d0[1]) / (d1[0] - d0[0])
    e = (3.85, d0[1] + (3.85 - d0[0]) * sl)
    mb.rod((x + d0[0] * math.cos(a), y + d0[0] * math.sin(a), Z + d0[1]),
           (x + e[0] * math.cos(a), y + e[0] * math.sin(a), Z + e[1]), 0.09, WOOD, 6)
    mb.ico(0.13, (x + e[0] * math.cos(a), y + e[0] * math.sin(a), Z + e[1]), WOOD, 1)
    # (ajuste 19: o FIO DE ENERGIA que subia da pocao ate o cristal do lustre saiu junto com o cristal)
    mb.finish()
    ngon_col("SG_CraftCauldron", x, y, 8, 3.5, Z + DAIS_H2 - 0.1, Z + DAIS_H2 + 4.9, rot0=22.5)


# ------------------------------------------------------------------ KIT de livros e frascos (composicao por prateleira)
class Row:
    """composicao de UMA prateleira em coordenadas locais (u ao longo da prateleira, y = profundidade a partir da
    frente util, v = altura sobre o tampo). emit() grava no MB pelo referencial da estante, espelhando se pedido."""

    def __init__(self):
        self.ops = []

    def box(self, c, size, tilt, m):
        self.ops.append(("box", c, size, tilt, m))

    def lathe(self, c, prof, m, n=8, rot=0.0, cap0=True, cap1=True):
        self.ops.append(("lathe", c, prof, m, n, rot, cap0, cap1))

    def rod(self, a, b, r, m, n=6):
        self.ops.append(("rod", a, b, r, m, n))

    def tube(self, pts, r, m, n=6):
        self.ops.append(("tube", pts, r, m, n))

    def emit(self, mb, F, y0, v0, mirror=False, du=0.0):
        s = -1.0 if mirror else 1.0

        def P(q):
            return F.p(s * q[0] + du, y0 + q[1], v0 + q[2])
        for op in self.ops:
            if op[0] == "box":
                _, c, size, tilt, m = op
                mb.box(size, P(c), F.r(0.0, -tilt * s, 0.0), m, 0.0)
            elif op[0] == "lathe":
                _, c, prof, m, n, rot, c0, c1 = op
                p = P(c)
                lathe(mb, p[0], p[1], p[2], prof, m, n, rot + F.a, c0, c1)
            elif op[0] == "rod":
                _, a, b, r, m, n = op
                mb.rod(P(a), P(b), r, m, n)
            elif op[0] == "tube":
                _, pts, r, m, n = op
                mb.tube([P(q) for q in pts], r, m, n)


# formatos do kit: (espessura, profundidade, altura) - folio, tomo grosso, quarto, octavo, fino, pequeno
BK = {"F": (0.30, 0.76, 1.38), "T": (0.40, 0.72, 1.22), "Q": (0.26, 0.70, 1.2), "O": (0.22, 0.62, 1.04),
      "N": (0.14, 0.64, 1.12), "D": (0.18, 0.56, 0.88)}
BOOKC = {"w": BK_WINE, "b": BK_BROWN, "n": "Cloth_SG_Navy", "k": BK_INK, "p": BK_PLUM, "l": "Leather"}
YOFF = [0.0, 0.03, 0.01, 0.05, 0.0, 0.02, 0.04]     # recuo da lombada (dirigido: nao alinha tudo no fio)
GAPB = 0.012
ROW_U0, ROW_U1 = -1.38, 1.38                         # vao livre entre os montantes na frente da prateleira


def book(row, x0, v0, w, d, h, m, yoff=0.0, tilt=0.0, px=0.0, ridges=2, gold=False):
    """livro do kit (local: x espessura, y profundidade a partir da lombada, z altura), girado de 'tilt' em torno da
    quina de baixo px (0 = esquerda): lombada, 2 capas e miolo recuado (capa maior que o miolo), nervuras na lombada"""
    c, s = math.cos(tilt), math.sin(tilt)

    def B(xa, xb, ya, yb, za, zb, mm):
        xm, ym, zm = (xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2
        xx = px + (xm - px) * c - zm * s
        zz = (xm - px) * s + zm * c
        row.box((x0 + xx, yoff + ym, v0 + zz), (xb - xa, yb - ya, zb - za), tilt, mm)
    t = 0.032 if w >= 0.18 else 0.026
    sp = 0.05
    B(0.0, w, 0.0, sp, 0.0, h, m)                                 # lombada
    B(0.0, t, sp, d, 0.0, h, m)                                   # capas
    B(w - t, w, sp, d, 0.0, h, m)
    B(t, w - t, sp - 0.01, d - 0.04, 0.035, h - 0.035, PAGES)     # miolo (recuado 0,035 em cima/baixo/frente)
    rm = GOLD if gold else m
    for k in range(ridges):
        zr = h * (0.18 + 0.64 * k / (ridges - 1)) if ridges > 1 else h * 0.82
        B(0.0, w, -0.024, 0.01, zr - 0.035, zr + 0.035, rm)


def _ridges(t, gold=False):
    """nervuras so onde contam: tomos, folios e as series douradas (o resto e lombada lisa)"""
    return 2 if (gold or t == "F") else 0


def place_v(row, u, types, cols, gold=False):
    last = None
    for i, (t, cc) in enumerate(zip(types, cols)):
        w, d, h = BK[t]
        book(row, u, 0.0, w, d, h, BOOKC[cc], YOFF[(i * 3 + len(types)) % len(YOFF)], ridges=_ridges(t, gold), gold=gold)
        last = (u + w, h)
        u += w + GAPB
    return u, last


def place_lean(row, last, t, cc, deg):
    """livro inclinado encostado no ultimo livro em pe (quina de baixo esquerda no tampo, face encostada na quina de
    cima do vizinho - ou a quina de cima dele na face do vizinho se for mais baixo)"""
    w, d, h = BK[t]
    a = math.radians(deg)
    un, hn = last
    ub = un + (h * math.sin(a) if h * math.cos(a) <= hn else hn * math.tan(a)) + 0.008
    book(row, ub, 0.0, w, d, h, BOOKC[cc], 0.02, tilt=a, ridges=_ridges(t))
    return ub + w * math.cos(a) + GAPB + 0.02


def place_stack(row, u, types, cols):
    """pilha deitada (de baixo para cima, maior embaixo), lombadas para a frente, deslocamentos pequenos dirigidos"""
    z = 0.0
    offs = [0.0, 0.05, 0.02, 0.07]
    Lmax = max(BK[t][2] for t in types)
    for i, (t, cc) in enumerate(zip(types, cols)):
        w, d, h = BK[t]
        book(row, u + offs[i] + h, z, w, d, h, BOOKC[cc], 0.01 * i, tilt=math.pi / 2, ridges=min(2, _ridges(t)))
        z += w + 0.004
    return u + Lmax + max(offs[:len(types)]) + 0.05


# frascos do kit: perfil (raio, altura), lados, rotacao, nivel do liquido (fração da altura ou None), raio de ocupacao
FLASK = {
    "round": ([(0.0, 0.0), (0.22, 0.0), (0.38, 0.12), (0.43, 0.36), (0.37, 0.6), (0.15, 0.78), (0.1, 0.86), (0.1, 1.06),
               (0.14, 1.1), (0.0, 1.14)], 7, 0.0, 0.58, 0.43),
    "potion": ([(0.0, 0.0), (0.28, 0.0), (0.48, 0.14), (0.55, 0.4), (0.46, 0.74), (0.28, 0.96), (0.14, 1.12), (0.13, 1.42),
                (0.17, 1.47), (0.0, 1.52)], 7, 0.0, 0.8, 0.55),
    "vial": ([(0.0, 0.0), (0.1, 0.03), (0.1, 0.92), (0.12, 0.95), (0.0, 0.98)], 6, 0.0, 0.68, 0.12),
    "square": ([(0.0, 0.0), (0.34, 0.0), (0.34, 0.68), (0.3, 0.74), (0.13, 0.86), (0.12, 0.98), (0.15, 1.0), (0.0, 1.04)],
               4, math.pi / 4, None, 0.25),
    "small": ([(0.0, 0.0), (0.26, 0.0), (0.28, 0.3), (0.24, 0.4), (0.2, 0.44), (0.2, 0.5), (0.0, 0.5)], 7, 0.0, None, 0.28),
}
# overhaul 07.08 / 15.02: so 2 pocoes ACESAS na sala (violeta ESCURO); o bastao amarelo (lit_a) saiu
LIQ = {"wine": POT_W, "teal": POT_T, "lit_v": VSOFT, "lit_a": POT_T, "violet": VDEEP}


def _r_at(P, h):
    for (ra, ha), (rb, hb) in zip(P, P[1:]):
        if ha <= h <= hb and hb > ha:
            return ra + (rb - ra) * (h - ha) / (hb - ha)
    return P[-1][0]


def flask_at(row, x, yc, v, kind, glass, liq=None, s=1.0, stop="cork"):
    """frasco do kit em pe (centro x, yc; base v): liquido embaixo, vidro em cima (le com e sem transparencia), tampa"""
    prof, n, rot, fill, rmax = FLASK[kind]
    P = [(r * s, h * s) for r, h in prof]
    c = (x, yc, v)
    if liq and fill:
        hf = fill * s
        rf = _r_at(P, hf)
        lower = [p for p in P if p[1] < hf - 1e-3]
        row.lathe(c, lower + [(rf, hf), (0.0, hf)], LIQ[liq], n, rot)
        row.lathe(c, [(rf, hf)] + [p for p in P if p[1] > hf + 1e-3], glass, n, rot, cap0=False)
    else:
        row.lathe(c, P, glass, n, rot)
    top = P[-1][1]
    rn = prof[-4][0] * s if kind != "small" else 0.2 * s
    if stop == "cork":
        row.lathe((x, yc, v + top - 0.08 * s), [(0.0, 0.0), (rn * 0.95, 0.0), (rn * 1.12, 0.22 * s), (0.0, 0.22 * s)], WOOD, 6)
    elif stop == "glass":                         # rolha de cristal facetada + gola de latao no gargalo
        row.lathe((x, yc, v + top - 0.06 * s), [(0.0, 0.0), (0.09 * s, 0.0), (0.09 * s, 0.14 * s), (0.2 * s, 0.24 * s),
                                                  (0.15 * s, 0.38 * s), (0.0, 0.44 * s)], glass, 6)
        row.lathe((x, yc, v), [(0.128 * s, 1.2 * s), (0.162 * s, 1.22 * s), (0.162 * s, 1.3 * s), (0.128 * s, 1.32 * s)],
                  GOLD, n, 0.0, False, False)
    elif stop == "cap":                           # tampa de ferro rosqueada
        row.lathe((x, yc, v + top - 0.03 * s), [(0.0, 0.0), (0.17 * s, 0.0), (0.17 * s, 0.13 * s), (0.14 * s, 0.17 * s),
                                                  (0.0, 0.17 * s)], IRON, 8)
    elif stop == "cloth":                         # pano amarrado sobre a boca larga
        row.lathe((x, yc, v), [(0.0, 0.5 * s), (0.215 * s, 0.5 * s), (0.215 * s, 0.43 * s), (0.25 * s, 0.4 * s),
                               (0.27 * s, 0.47 * s), (0.25 * s, 0.53 * s), (0.17 * s, 0.58 * s), (0.0, 0.6 * s)], CANVAS, 8)
        row.lathe((x, yc, v), [(0.2 * s, 0.445 * s), (0.232 * s, 0.45 * s), (0.232 * s, 0.49 * s), (0.2 * s, 0.495 * s)],
                  BK_BROWN, 8, 0.0, False, False)
    if kind == "square":                          # rotulo de papel na face da frente
        row.box((x, yc - 0.245 * s, v + 0.38 * s), (0.3 * s, 0.02, 0.3 * s), 0.0, PAGES)
    return rmax * s


def place_flask(row, u, kind, glass, liq=None, s=1.0, stop="cork"):
    r = FLASK[kind][4] * s
    flask_at(row, u + r, 0.42, 0.0, kind, glass, liq, s, stop)
    return u + 2 * r + 0.1


def place_rack(row, u, liqs):
    """suporte de madeira com 3 tubos de ensaio (tampo com furos, montantes, base)"""
    row.box((u + 0.475, 0.42, 0.04), (0.95, 0.44, 0.08), 0.0, WOOD)
    for e in (0.035, 0.915):
        row.box((u + e, 0.42, 0.33), (0.07, 0.3, 0.5), 0.0, WOOD)
    row.box((u + 0.475, 0.42, 0.56), (0.95, 0.3, 0.07), 0.0, WOOD)
    for k, lq in enumerate(liqs):
        flask_at(row, u + 0.2 + 0.275 * k, 0.42, 0.08, "vial", PALE, lq, 1.0, "cork")
    return u + 1.05


def place_jar(row, u, glass):
    return place_flask(row, u, "small", glass, None, 1.0, "cloth")


def place_scrolls(row, u):
    """pilha de PERGAMINHOS enrolados (08.03): tom de pergaminho quente apagado (nao mais o branco do Cloth_Canvas),
    ROLO de madeira na ponta da frente de cada um e fita vinho so em 2"""
    r = 0.13
    top = r + math.sqrt((2 * r) ** 2 - 0.135 ** 2)
    for k, (uu, vv) in enumerate(((0.13, r), (0.4, r), (0.67, r), (0.265, top), (0.535, top))):
        row.rod((u + uu, 0.08, vv), (u + uu, 0.74, vv), r, PAGES, 7)
        row.rod((u + uu, 0.02, vv), (u + uu, 0.09, vv), r + 0.025, WOOD, 6)
        if k in (1, 3):
            row.rod((u + uu, 0.38, vv), (u + uu, 0.46, vv), r + 0.012, BK_WINE, 7)
    return u + 0.9


def build_row(comp):
    row = Row()
    u = ROW_U0
    last = None
    for it in comp:
        k = it[0]
        if k == "v":
            u, last = place_v(row, u, it[1], it[2], it[3] if len(it) > 3 else False)
        elif k == "lean":
            u = place_lean(row, last, it[1], it[2], it[3])
            last = None
        elif k == "stack":
            u = place_stack(row, u, it[1], it[2])
        elif k == "flask":
            u = place_flask(row, u, *it[1:])
        elif k == "rack":
            u = place_rack(row, u, it[1])
        elif k == "jar":
            u = place_jar(row, u, it[1])
        elif k == "scrolls":
            u = place_scrolls(row, u)
        elif k == "gap":
            u += it[1]
        if u > ROW_U1 + 0.1:
            print("CRAFT AVISO: prateleira passou do vao (%.2f): %s" % (u, comp))
    return row


# composicoes feitas a mao (tipos: F T Q O N D; cores: w vinho, b marrom, n azul-escuro, k preto, p roxo, l couro)
COMP = {
    "A": [("v", "FFQTQ", "wwnkb"), ("lean", "O", "p", 17)],
    "B": [("stack", "FTQ", "kbn"), ("gap", 0.1), ("v", "QQQQ", "nnnn", True)],
    "C": [("v", "TFF", "bkk", True), ("gap", 0.4), ("v", "NOD", "pwl"), ("lean", "Q", "b", 14)],
    "D": [("v", "OOND", "klwn"), ("lean", "O", "p", 20), ("gap", 0.2), ("stack", "OD", "wk")],
    "E": [("flask", "potion", PALE, "wine", 0.72, "glass"), ("rack", ["wine", "teal", "wine"]),
          ("flask", "square", AMBER, None, 1.0, "cap")],
    "F": [("jar", SAGE), ("gap", 0.24), ("flask", "round", PALE, "lit_v", 1.0, "cork"),
          ("flask", "potion", PALE, "teal", 0.7, "glass")],
    "F2": [("jar", SAGE), ("gap", 0.24), ("flask", "round", PALE, "wine", 1.0, "cork"),
           ("flask", "potion", PALE, "teal", 0.7, "glass")],
    "G": [("v", "FQO", "kwb", True), ("gap", 0.15), ("flask", "round", PALE, "wine", 0.85, "cork"), ("scrolls",)],
    "H": [("jar", AMBER), ("jar", SAGE), ("gap", 0.25), ("stack", "OD", "nb")],
    "I": [("rack", ["teal", "lit_a", "wine"]), ("gap", 0.3), ("flask", "potion", PALE, "wine", 0.72, "glass")],
    "J": [("v", "DOOQ", "lbwk"), ("gap", 0.6), ("v", "TT", "kk", True)],
    "K": [("scrolls",), ("gap", 0.2), ("v", "QON", "bnw"), ("lean", "O", "l", 18)],
    "L": [("stack", "TQ", "kw"), ("gap", 0.5), ("jar", SAGE)],
    "M": [("v", "NQQF", "pbwn"), ("gap", 0.9), ("flask", "square", AMBER, None, 1.0, "cap")],
}
# por estante, de baixo para cima: (composicao, espelhada?) - cada estante diferente, ritmo de frascos na altura dos
# olhos (3o nivel) sem repetir a mesma fileira
SHELF_LAYOUT = {
    67.5: [("H", 0), ("A", 0), ("E", 0), ("J", 0), ("L", 0)],
    82.5: [("B", 0), ("G", 0), ("F", 0), ("M", 1), ("D", 0)],
    97.5: [("K", 0), ("C", 1), ("I", 0), ("B", 1), ("J", 1)],
    112.5: [("L", 1), ("D", 0), ("E", 1), ("G", 1), ("A", 0)],
    247.5: [("B", 1), ("J", 0), ("F", 1), ("K", 0), ("C", 1)],
    262.5: [("H", 1), ("A", 1), ("I", 1), ("D", 1), ("L", 0)],
    277.5: [("K", 1), ("M", 0), ("E", 0), ("C", 0), ("J", 0)],
    292.5: [("B", 0), ("D", 1), ("F2", 0), ("A", 1), ("K", 0)],
}
SHELF_V = [0.5, 2.16, 3.82, 5.48, 7.14]      # tampos (o 1o e o fundo da caixa, sobre o rodape)
SHELF_BACK = "Roof_SG_Slate"                 # fundo 2 valores abaixo da madeira (08.02): livros recortam contra ele
SHELF_TOP = 8.8                              # (colisao) topo da caixa
CASE_Y0 = 12.1                               # frente util das prateleiras (livros e frascos daqui para tras)
POST_HW = 0.18                               # meia largura dos montantes
POST_K = POST_HW / math.cos(math.radians(STEP / 2.0))


def _uin(y):
    """meia largura livre da prateleira na profundidade y (entre as faces dos montantes nas bissetrizes)"""
    return y * TAN - POST_K


def bookcases(mb):
    """ESTANTES: o movel acompanha a parede de 24 faces - montantes nas BISSETRIZES (juntas das faces), rodape e
    cornija em esquadria continua, prateleiras em trapezio entre os montantes (nada atravessa o vizinho), testeira nas
    prateleiras, fundo, frontao nas estantes sem janela"""
    posts = sorted({a0 + STEP * k for a0, a1 in SHELF_RUNS for k in range(int(round((a1 - a0) / STEP)) + 1)})
    for b in posts:
        F = fr(b)
        yb = (YB_IN - POST_HW * math.sin(math.radians(STEP / 2.0))) / math.cos(math.radians(STEP / 2.0))
        fbox(mb, F, -POST_HW, POST_HW, 11.92, yb, 0.42, 8.6, WOOD)                       # montante
        fbox(mb, F, -0.23, 0.23, 11.84, 11.96, 0.5, 8.36, WOOD, 0.03)                    # pilastra da frente
        fbox(mb, F, -0.27, 0.27, 11.8, 12.3, 0.0, 0.62, WOOD, 0.04)                      # base da pilastra
        fbox(mb, F, -0.27, 0.27, 11.8, 12.2, 8.3, 8.6, WOOD, 0.03)                       # capitel
    for a in SHELF_A:
        F = fr(a)
        wl = YB_IN * TAN
        # rodape (esquadria nas bissetrizes) e fundo
        fprism(mb, F, [(-11.96 * TAN, 11.96), (11.96 * TAN, 11.96), (wl, YB_IN), (-wl, YB_IN)], 0.0, 0.42, WOOD, 0.03)
        fprism(mb, F, [(-13.1 * TAN, 13.1), (13.1 * TAN, 13.1), (wl, YB_IN), (-wl, YB_IN)], 0.42, 8.6, SHELF_BACK)
        # prateleiras (trapezio entre os montantes) com testeira mais alta na frente
        for v in SHELF_V:
            t = 0.08 if v == SHELF_V[0] else 0.14
            fprism(mb, F, [(-_uin(12.06), 12.06), (_uin(12.06), 12.06), (_uin(13.1), 13.1), (-_uin(13.1), 13.1)], v - t, v,
                   WOOD)
            fbox(mb, F, -_uin(11.98), _uin(11.98), 11.98, 12.06, v - 0.2, v + 0.03, WOOD, 0.02)
            if v == SHELF_V[2]:
                fbox(mb, F, -_uin(11.95), _uin(11.95), 11.94, 11.99, v - 0.1, v - 0.05, GOLD)     # filete de bronze
        # friso e cornija (esquadria nas bissetrizes, cornija com balanco)
        fprism(mb, F, [(-11.9 * TAN, 11.9), (11.9 * TAN, 11.9), (wl, YB_IN), (-wl, YB_IN)], 8.6, 8.9, WOOD)
        fprism(mb, F, [(-11.7 * TAN, 11.7), (11.7 * TAN, 11.7), (wl, YB_IN), (-wl, YB_IN)], 8.9, 9.1, WOOD, 0.04)
        if a not in WIN_M:
            # frontao (so nas estantes sem janela acima): timpano + cimalhas inclinadas + medalhao de obsidiana + remate
            pslab(mb, F, [(-1.42, 9.1), (1.42, 9.1), (0.0, 10.42)], 11.92, 12.5, WOOD)
            for s in (-1, 1):
                mb.beam(F.p(s * 1.62, 12.17, 9.12), F.p(0.0, 12.17, 10.64), 0.74, 0.2, WOOD, 0.03)
            c = F.p(0.0, 11.91, 9.62)
            mb.cyl(0.26, 0.06, c, F.r(math.pi / 2, 0.0, 0.0), OBS, n=10, bevel=0.0)
            lathe(mb, *F.p(0.0, 12.17, 10.6), [(0.0, 0.0), (0.13, 0.0), (0.16, 0.12), (0.08, 0.26), (0.1, 0.34), (0.0, 0.42)],
                  WOOD, n=6)
        for i, (key, mir) in enumerate(SHELF_LAYOUT[a]):
            build_row(COMP[key]).emit(mb, F, CASE_Y0, SHELF_V[i], bool(mir))
        fcol("SG_CraftShelf", F, -1.73, 1.73, SH_F - 0.05, YB_IN + 0.05, -0.5, SHELF_TOP + 0.34)


def open_book(mb, F, u, y, v, m, ang=0.0):
    """livro ABERTO sobre o tampo: capa maior que as folhas, dois blocos de folhas levantando para a lombada"""
    mb.box((1.3, 0.9, 0.04), F.p(u, y, v + 0.02), F.r(0.0, 0.0, ang), m, 0.0)
    for s in (-1, 1):
        t = math.radians(6.0) * -s
        cu = u + s * 0.32 * math.cos(ang)
        cy = y + s * 0.32 * math.sin(ang)
        mb.box((0.6, 0.82, 0.07), F.p(cu, cy, v + 0.04 + 0.035 + 0.02), F.r(0.0, -t, ang), PAGES, 0.0)
    mb.box((0.08, 0.86, 0.06), F.p(u, y, v + 0.07), F.r(0.0, 0.0, ang), m, 0.0)


def candle(mb, x, y, z, hc=0.6, s=1.0, dish=True, cup=False):
    """KIT DE VELA (12.09, o mesmo desenho do salao): prato de ferro ou COPINHO de bronze, vela creme NAO emissiva,
    pavio e chama em GOTA (so ela e Neon). z = apoio. Devolve o topo da chama."""
    if dish:
        EM._lathe(mb, (x, y, z), [(0.12 * s, 0.0), (0.34 * s, 0.07 * s), (0.3 * s, 0.1 * s), (0.0, 0.07 * s)], IRON, 6,
                  caps=(True, False))
        z += 0.07 * s
    if cup:
        EM._lathe(mb, (x, y, z), [(0.07 * s, 0.0), (0.24 * s, 0.12 * s), (0.0, 0.1 * s)], BRONZE, 6, caps=(True, False))
        z += 0.1 * s
    r = 0.1 * s
    EM._lathe(mb, (x, y, z), [(r, 0.0), (r, hc - 0.04 * s), (0.0, hc - 0.01 * s)], PAGES, 5, caps=(True, False))
    zt = z + hc - 0.02 * s
    mb.rod((x, y, zt - 0.02 * s), (x, y, zt + 0.12 * s), 0.018 * s + 0.01, BIRON, 3, caps=False)
    zf = zt + 0.05 * s
    EM._lathe(mb, (x, y, zf), [(0.0, 0.0), (0.11 * s, 0.14 * s), (0.06 * s, 0.3 * s), (0.0, 0.44 * s)], GLOW, 6)
    return zf + 0.44 * s


def candlestick(mb, x, y, z, s=1.0):
    """castical de bronze de mesa (pe, haste torneada, prato) com a vela do kit"""
    EM._lathe(mb, (x, y, z), [(0.26 * s, 0.0), (0.26 * s, 0.05 * s), (0.12 * s, 0.14 * s), (0.06 * s, 0.22 * s),
                              (0.09 * s, 0.34 * s), (0.05 * s, 0.46 * s), (0.2 * s, 0.52 * s), (0.18 * s, 0.56 * s)],
              BRONZE, 6, caps=(False, True))
    return candle(mb, x, y, z + 0.56 * s, 0.5 * s, s, dish=False)


def bench(mb, rng):
    """bancada do alquimista (leste, atras do NPC): rodape recuado, corpo com gavetas e portas com puxadores, tampo
    com balanco; alambique (fogareiro, caldeira de latao, capitel) com o pescoco de cisne ENTRANDO no gargalo do
    coletor; bandeja com frascos do kit, almofariz, livro aberto; prateleira de parede em V (acompanha a quina da
    parede) com potes e livros"""
    F = fr(0.0)
    fbox(mb, F, -3.45, 3.45, 10.62, 12.1, 0.0, 0.3, WOOD)                    # rodape recuado
    fbox(mb, F, -3.6, 3.6, 10.5, 12.2, 0.3, 2.7, WOOD, 0.04)
    fbox(mb, F, -3.85, 3.85, 10.2, 12.35, 2.7, 3.0, WOOD, 0.06)
    for u in (-3.6, 3.6):
        fbox(mb, F, u - 0.12, u + 0.12, 10.42, 12.2, 0.3, 2.7, WOOD, 0.03)   # montantes laterais salientes
    for u in (-2.4, 0.0, 2.4):
        fbox(mb, F, u - 1.05, u + 1.05, 10.36, 10.5, 1.95, 2.55, WOOD, 0.04)
        fbox(mb, F, u - 0.16, u + 0.16, 10.26, 10.36, 2.18, 2.32, GOLD)
    for u in (-1.75, 1.75):
        fbox(mb, F, u - 1.6, u + 1.6, 10.36, 10.5, 0.4, 1.78, WOOD, 0.04)
        pu = u - math.copysign(1.3, u)                                       # puxador junto ao encontro das portas
        fbox(mb, F, pu - 0.08, pu + 0.08, 10.26, 10.36, 0.9, 1.3, GOLD)
    top = 3.0
    # alambique: FOGAREIRO de ferro (07.09: 3 pes, bacia com 3 bocas, carvoes sobre o leito, grelha), caldeira de
    # bronze, capitel com o bico
    p = F.p(-2.5, 11.3, top)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.2), (0.5, 0.2), (0.56, 0.3), (0.0, 0.3)], IRON, n=8)
    for k in range(3):
        b = F.a + 2 * math.pi * k / 3 + 0.3
        mb.box((0.14, 0.14, 0.24), (p[0] + 0.42 * math.cos(b), p[1] + 0.42 * math.sin(b), p[2] + 0.12), (0, 0, b), IRON,
               0.02)
    for k in range(3):
        a0 = math.degrees(F.a) + 120.0 * k + 18.0
        revolve(mb, tuple(p), [(0.5, 0.28), (0.62, 0.3), (0.62, 0.6), (0.52, 0.6)], IRON, n=4, a0=a0, a1=a0 + 84.0,
                smooth_edges=set())
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.3), (0.48, 0.3), (0.46, 0.36), (0.0, 0.37)], VSOFT, n=8)
    for k in range(3):
        b = F.a + 2 * math.pi * k / 3 + 1.2
        mb.ico(0.16, (p[0] + 0.22 * math.cos(b), p[1] + 0.22 * math.sin(b), p[2] + 0.42), OBS, 1,
               scale=(1.1, 0.9, 0.6), rot=(0.2, 0.0, b))
    for d in (-0.26, 0.0, 0.26):
        mb.box((1.14, 0.06, 0.06), Vector(p) + Vector((0, 0, 0.6)) + Vector((-math.sin(F.a), math.cos(F.a), 0)) * d,
               (0, 0, F.a), IRON, 0.0)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.66), (0.5, 0.66), (0.78, 0.95), (0.8, 1.35), (0.55, 1.72), (0.24, 1.92),
                                 (0.24, 2.35), (0.42, 2.6), (0.3, 2.95), (0.0, 3.05)], BRASS, n=12)
    tube = []
    for k in range(10):
        t = k / 9.0
        tube.append(F.p(-2.2 + 1.45 * t, 11.3 - 0.2 * t, top + 2.72 + 0.25 * math.sin(math.pi * t) - 1.64 * t * t))
    mb.tube(tube, 0.075, BRASS, 8)
    e = tube[-1]
    revolve(mb, (e[0], e[1], e[2]), [(0.07, -0.12), (0.14, -0.1), (0.14, 0.04), (0.07, 0.06)], BRASS, n=8,
            smooth_edges=set())                                              # colar no gargalo do coletor
    row = Row()
    flask_at(row, -0.75, 11.1, top, "round", PALE, "wine", 1.0, stop=None)       # coletor (o tubo entra no gargalo)
    fbox(mb, F, 0.15, 1.95, 10.65, 11.8, top, top + 0.14, WOOD, 0.03)            # bandeja com frascos
    flask_at(row, 0.62, 11.2, top + 0.14, "potion", PALE, "teal", 0.8, "glass")
    flask_at(row, 1.5, 11.25, top + 0.14, "square", SAGE, None, 0.9, "cap")
    row.emit(mb, F, 0.0, 0.0)
    # almofariz e pilao
    m0 = F.p(2.85, 11.65, top)
    lathe(mb, m0[0], m0[1], m0[2], [(0.0, 0.0), (0.4, 0.0), (0.52, 0.42), (0.36, 0.44), (0.0, 0.3)], TRIM, n=10)
    mb.rod(F.p(2.8, 11.6, top + 0.3), F.p(3.1, 12.0, top + 1.0), 0.11, TRIM, 6)
    open_book(mb, F, 2.2, 10.75, top, BK_BROWN)
    # prateleira de parede acima da bancada: tabua em V que acompanha a quina da parede, maos-francesas de ferro
    yw = lambda u: (YB_IN - abs(u) * math.sin(math.radians(7.5))) / math.cos(math.radians(7.5))
    fprism(mb, F, [(-3.2, 12.3), (3.2, 12.3), (3.2, yw(3.2) - 0.02), (0.0, R_IN - 0.02), (-3.2, yw(3.2) - 0.02)], 6.5, 6.72,
           WOOD, 0.03)
    for u in (-2.6, 2.6):
        pside(mb, F, [(yw(u) - 0.01, 6.5), (12.55, 6.5), (yw(u) - 0.01, 5.6)], u - 0.1, u + 0.1, BIRON)
    sh = Row()
    for u, g in ((-2.75, AMBER), (-2.15, SAGE), (-1.55, AMBER)):
        flask_at(sh, u, 12.72, 0.0, "small", g, None, 1.0, "cloth")
    sh.emit(mb, F, 0.0, 6.72)
    sb = Row()
    u, last = place_v(sb, -0.6, "OQON", "wkbn")
    place_lean(sb, last, "D", "p", 20)
    sb.emit(mb, F, 12.35, 6.72)
    fcol("SG_CraftBench", F, -3.85, 3.85, 10.2, 12.8, -0.5, 3.0)


def stool(mb, p):
    """banqueta: assento torneado sobre 3 pes abertos de madeira com aro de ferro"""
    x, y, z = p
    lathe(mb, x, y, z, [(0.0, 1.7), (0.52, 1.7), (0.57, 1.78), (0.53, 1.88), (0.0, 1.9)], WOOD, n=10)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        cone(mb, (x + 0.55 * math.cos(a), y + 0.55 * math.sin(a), z), (x + 0.32 * math.cos(a), y + 0.32 * math.sin(a), z + 1.72),
             0.08, 0.07, WOOD, 6)
    rr = 0.55 - 0.23 * (0.6 / 1.72)
    lathe(mb, x, y, z, [(rr - 0.05, 0.56), (rr + 0.03, 0.56), (rr + 0.03, 0.64), (rr - 0.05, 0.64)], BIRON, n=10,
          cap0=False, cap1=False)


def study_tables(mb, rng):
    """2 MESAS DE ESTUDO: tampo com balanco e chanfro, SAIA entre os blocos das pernas, pernas TORNEADAS sob o tampo,
    travessa em H; livro aberto, balanca, alambique pequeno / tinteiro, VELA no castical (kit); banqueta; tapete navy
    com debrum de bronze rente"""
    for i, a in enumerate(TABLE_A):
        F = fr(a)
        rc = 10.6
        # tapete navy + debrum dourado (rente: 0,05..0,12)
        fbox(mb, F, -2.4, 2.4, rc - 1.9, rc + 1.9, 0.05, 0.1, "Cloth_SG_Navy")
        for u0, u1, w0, w1 in ((-2.4, -2.08, rc - 1.9, rc + 1.9), (2.08, 2.4, rc - 1.9, rc + 1.9),
                               (-2.08, 2.08, rc - 1.9, rc - 1.62), (-2.08, 2.08, rc + 1.62, rc + 1.9)):
            fbox(mb, F, u0, u1, w0, w1, 0.05, 0.12, GOLD)
        top = 2.8
        fbox(mb, F, -1.9, 1.9, rc - 1.1, rc + 1.1, 2.56, top, WOOD, 0.05)
        for sy in (-1, 1):
            fbox(mb, F, -1.47, 1.47, rc + sy * 0.82 - 0.05, rc + sy * 0.82 + 0.05, 2.22, 2.56, WOOD)
        for su in (-1, 1):
            fbox(mb, F, su * 1.6 - 0.05, su * 1.6 + 0.05, rc - 0.69, rc + 0.69, 2.22, 2.56, WOOD)
        for su in (-1, 1):
            for sy in (-1, 1):
                p = F.p(su * 1.6, rc + sy * 0.82, 0.0)
                fbox(mb, F, su * 1.6 - 0.13, su * 1.6 + 0.13, rc + sy * 0.82 - 0.13, rc + sy * 0.82 + 0.13, 2.18, 2.56, WOOD)
                lathe(mb, p[0], p[1], p[2], [(0.0, 0.0), (0.15, 0.0), (0.16, 0.1), (0.1, 0.34), (0.13, 0.56), (0.085, 0.8),
                                             (0.09, 1.7), (0.12, 2.0), (0.12, 2.18), (0.0, 2.18)], WOOD, n=6)
        for su in (-1, 1):
            fbox(mb, F, su * 1.6 - 0.05, su * 1.6 + 0.05, rc - 0.72, rc + 0.72, 0.55, 0.68, WOOD)
        fbox(mb, F, -1.55, 1.55, rc - 0.05, rc + 0.05, 0.55, 0.68, WOOD)
        stool(mb, tuple(F.p(-2.55 if i == 0 else 2.55, rc - 0.4, 0.0)))
        open_book(mb, F, -0.75, rc - 0.3, top, BK_WINE if i == 0 else BK_INK)
        # balanca de dois pratos (coluna, travessao, pratos pendurados)
        bp = F.p(0.75, rc + 0.42, top)
        lathe(mb, bp[0], bp[1], bp[2], [(0.0, 0.0), (0.26, 0.0), (0.24, 0.1), (0.0, 0.12)], IRON, n=8)
        mb.rod(bp, (bp[0], bp[1], bp[2] + 1.5), 0.06, IRON, 6)
        mb.box((1.7, 0.08, 0.08), F.p(0.75, rc + 0.42, top + 1.44), F.r(), IRON, 0.0)
        for s in (-1, 1):
            pa = F.p(0.75 + s * 0.78, rc + 0.42, top + 1.42)
            mb.rod(pa, (pa[0], pa[1], pa[2] - 0.62), 0.025, IRON, 4)
            mb.cyl(0.28, 0.06, (pa[0], pa[1], pa[2] - 0.66), (0, 0, 0), SILVER, n=8, bevel=0.0)
        row = Row()
        if i == 0:
            ap = F.p(1.45, rc - 0.55, top)
            lathe(mb, ap[0], ap[1], ap[2], [(0.0, 0.0), (0.34, 0.0), (0.44, 0.35), (0.3, 0.7), (0.12, 0.8), (0.12, 1.15),
                                            (0.2, 1.3), (0.0, 1.35)], BRASS, n=8)
            flask_at(row, 1.1, rc + 0.62 - 0.3, top, "round", PALE, "teal", 0.75)
        else:
            tp = F.p(1.05, rc + 0.35, top)
            lathe(mb, tp[0], tp[1], tp[2], [(0.0, 0.0), (0.2, 0.0), (0.22, 0.22), (0.1, 0.3), (0.0, 0.3)], IRON, n=6)
            mb.rod(F.p(1.05, rc + 0.35, top + 0.2), F.p(1.35, rc + 0.62, top + 1.0), 0.03, PAGES, 4)
        row.emit(mb, F, 0.0, 0.0)
        # 08.08: a lanterna-cubo saiu; na mesa, uma VELA no castical basta (kit de vela)
        cp = F.p(-1.45, rc + 0.62, top) if i == 0 else F.p(1.45, rc - 0.55, top)
        candlestick(mb, cp[0], cp[1], cp[2], 1.0)
        fcol("SG_CraftTable", F, -2.0, 2.0, rc - 1.15, rc + 1.15, -0.5, 2.78)


def gallery(mb, rng):
    """GALERIA anular estreita a +8,35..8,95 nas costas (leste) do salao: nao entravel (sem escada), so leitura de
    profundidade (08.06): piso de madeira sobre MISULAS EM S (perfil de pedra), balaustrada de ferro com BALAUSTRES
    REDONDOS (anel a cada 3) e CORRIMAO boleado; livros do kit; sem colisao"""
    ring_band(mb, 10.8, R_IN + 0.05, GAL_Z0, GAL_Z1, WOOD, GAL_A0, GAL_A1)
    ring_band(mb, 10.72, 10.98, GAL_Z0 - 0.15, GAL_Z1 + 0.05, VSTONE, GAL_A0, GAL_A1)    # testeira
    s_top = [(11.0, 0.0), (11.3, 0.0), (11.7, 0.0), (12.1, 0.0), (12.5, 0.0), (12.9, 0.0), (R_IN + 0.02, 0.0)]
    s_low = [(11.0, -0.26), (11.3, -0.42), (11.7, -0.55), (12.1, -0.72), (12.5, -1.08), (12.9, -1.52), (R_IN + 0.02, -1.8)]
    for k in range(7):
        a = GAL_A0 + 15.0 * k
        ar = math.radians(a)
        W = ((CX, CY), (math.cos(ar), math.sin(ar)), (-math.sin(ar), math.cos(ar)))
        CA.strip(mb, W, [(u, Z + GAL_Z0 + v) for u, v in s_low], [(u, Z + GAL_Z0 + v) for u, v in s_top], -0.36, 0.36,
                 OBS)
    # balaustrada de ferro negro: balaustres torneados (n=6), anel a cada 3, corrimao e travessa redondos
    for k in range(13):
        a = GAL_A0 + 7.5 * k
        p = pol(11.05, a, GAL_Z1)
        EM._lathe(mb, (p[0], p[1], p[2]), [(0.12, 0.0), (0.08, 0.16), (0.07, 2.12), (0.1, 2.32)], BIRON, 6,
                  caps=(False, True))
        if k % 3 == 0:
            EM._lathe(mb, (p[0], p[1], p[2]), [(0.07, 0.95), (0.13, 1.0), (0.13, 1.14), (0.07, 1.19)], BIRON, 6,
                      caps=(False, False))
    arc = [pol(11.05, GAL_A0 + (GAL_A1 - GAL_A0) * k / 18.0, GAL_Z1 + 2.42) for k in range(19)]
    mb.tube(arc, 0.14, BIRON, 6)
    arc = [pol(11.05, GAL_A0 + (GAL_A1 - GAL_A0) * k / 18.0, GAL_Z1 + 1.16) for k in range(19)]
    mb.tube(arc, 0.06, BIRON, 4)
    for a, comp, du in ((337.5, [("stack", "FQO", "kbw")], 0.6), (7.5, [("v", "QQOFN", "nnkbw", True), ("lean", "O", "p", 18)], 0.2),
                        (22.5, [("stack", "TO", "bn")], 0.9)):
        build_row(comp).emit(mb, fr(a), 12.35, GAL_Z1, False, du)


def banners(mb):
    """2 ESTANDARTES da ordem (debrum dourado) nas faces livres, presos a parede por 2 maos-francesas de ferro"""
    for a in BANNER_A:
        F = fr(a)
        w = 2.4
        EM.banner(mb, mb, mb, mb, F.p(0.0, 12.85, 14.0), math.radians(a + 180.0), w, 7.2, tails=True, trim=GOLD)
        for s in (-1, 1):
            u = s * (w / 2 + 0.12)
            mb.beam(F.p(u, YB_IN + 0.02, 14.8), F.p(u, 12.85, 14.02), 0.12, 0.12, BIRON, 0.0)
            fbox(mb, F, u - 0.16, u + 0.16, YB_IN - 0.12, YB_IN + 0.02, 14.5, 15.1, BIRON)


def circle_lanterns(mb):
    """2 POSTES DE LANTERNA ancorando o circulo magico dos dois lados da passadeira (07.06): o KIT DEFINITIVO
    (lanterna hexagonal da ordem), BAIXO (poste 3,3, escala 0,65: a lanterna fica abaixo do olho e nao tapa o
    caldeirao da porta); colisao fina propria, fora da volta do caldeirao (raio 5,2) e da passadeira"""
    for a in POST_A:
        b = pol(8.05, a, 0.05)
        EM.lantern_post(mb, mb, b, math.radians(a), h=3.3, s=0.65)
        col_box("SG_CraftLanternPost", (0.9, 0.9, 4.6), (b[0], b[1], b[2] + 2.2), (0, 0, math.radians(a)))


def lectern(mb):
    """ATRIL com o livro de receitas (perto da porta, lado sul) (08.04): pes em CRUZ de madeira com sapatas, COLUNA
    TORNEADA, capitel, tampo inclinado com BORDA e TRAVE de apoio do livro, livro aberto"""
    F = fr(217.5)
    r = 11.0
    c = F.p(0.0, r, 0.0)
    for k in range(2):
        a = F.a + math.pi / 4 + k * math.pi / 2
        mb.box((1.5, 0.22, 0.2), (c[0], c[1], c[2] + 0.1), (0.0, 0.0, a), WOOD, 0.05)
        for s in (-1, 1):
            mb.box((0.3, 0.3, 0.1), (c[0] + s * 0.66 * math.cos(a), c[1] + s * 0.66 * math.sin(a), c[2] + 0.05),
                   (0.0, 0.0, a), IRON, 0.03)
    EM._lathe(mb, (c[0], c[1], c[2] + 0.2), [(0.33, 0.0), (0.35, 0.12), (0.24, 0.3), (0.21, 0.72), (0.31, 1.0),
                                             (0.33, 1.2), (0.23, 1.5), (0.2, 2.2), (0.27, 2.36), (0.37, 2.52),
                                             (0.37, 2.64)], WOOD, 8, caps=(False, True))
    t = math.radians(24.0)
    nY, nZ = -math.sin(t), math.cos(t)

    def at(u, d, off=0.0):
        return F.p(u, r + nY * d + math.cos(t) * off, 3.2 + nZ * d + math.sin(t) * off)
    mb.box((1.6, 1.15, 0.1), at(0.0, 0.0), F.r(t, 0.0, 0.0), WOOD, 0.03)
    for s in (-1, 1):                                                       # borda
        mb.box((0.08, 1.15, 0.12), at(s * 0.8, 0.04), F.r(t, 0.0, 0.0), WOOD, 0.02)
    mb.box((1.68, 0.1, 0.16), at(0.0, 0.08, -0.6), F.r(t, 0.0, 0.0), WOOD, 0.02)   # trave de apoio (em baixo)
    mb.box((0.34, 0.5, 0.4), F.p(0.0, r, 2.97), F.r(), WOOD, 0.03)          # cachorro sob o tampo
    mb.box((1.44, 0.94, 0.05), at(0.0, 0.075, 0.03), F.r(t, 0.0, 0.0), BK_WINE, 0.0)
    for s in (-1, 1):
        mb.box((0.66, 0.84, 0.08), at(s * 0.35, 0.13, 0.03), F.r(t, s * 0.06, 0.0), PAGES, 0.0)
    fcol("SG_CraftLectern", F, -0.85, 0.85, r - 0.75, r + 0.75, -0.5, 3.6)


def chest(mb):
    """BAU de ingredientes da dungeon (perto da porta, lado norte) (08.05): corpo com rodape, TAMPA ABAULADA (arco
    extrudado), cintas de ferro que seguem o arco, CANTONEIRAS, ALCAS de argola nas laterais, fechadura; SACO de lona
    torneado com 2 DOBRAS e amarracao"""
    F = fr(142.5)
    r = 11.4
    hw, hd = 1.0, 0.6
    fbox(mb, F, -hw, hw, r - hd, r + hd, 0.0, 0.1, IRON, 0.02)
    fbox(mb, F, -hw + 0.03, hw - 0.03, r - hd + 0.03, r + hd - 0.03, 0.1, 1.02, WOOD, 0.04)
    arc_o = [(hw * math.cos(math.pi * k / 8), 1.02 + 0.42 * math.sin(math.pi * k / 8)) for k in range(9)]
    pslab(mb, F, arc_o, r - hd - 0.03, r + hd + 0.03, WOOD)
    for u in (-0.62, 0.62):
        # cinta vertical no corpo (frente/fundo/tampo) seguindo a tampa
        fbox(mb, F, u - 0.1, u + 0.1, r - hd - 0.05, r + hd + 0.05, 0.1, 1.02, IRON, 0.0)
        zz = 1.02 + 0.42 * math.sqrt(max(0.0, 1.0 - (u / hw) ** 2))
        fbox(mb, F, u - 0.1, u + 0.1, r - hd - 0.05, r + hd + 0.05, 1.0, zz + 0.04, IRON, 0.0)
    band(mb, F, arc_o, [(u * 1.05, 1.02 + (v - 1.02) * 1.12) for u, v in arc_o], r - hd - 0.06, r - hd + 0.06, IRON)
    band(mb, F, arc_o, [(u * 1.05, 1.02 + (v - 1.02) * 1.12) for u, v in arc_o], r + hd - 0.06, r + hd + 0.06, IRON)
    for su in (-1, 1):
        for sy in (-1, 1):
            fbox(mb, F, su * (hw - 0.22), su * (hw + 0.02), r + sy * (hd - 0.22), r + sy * (hd + 0.02), 0.86, 1.04, IRON,
                 0.0)
    fbox(mb, F, -0.16, 0.16, r - hd - 0.08, r - hd, 0.78, 1.14, SILVER, 0.02)
    for s in (-1, 1):                                                        # alcas de argola nas laterais
        c = Vector(F.p(s * (hw - 0.03), r, 0.74))
        axv = Vector((math.cos(F.a), math.sin(F.a), 0.0)) * s
        disc_ax(mb, c, axv, 0.12, 0.0, 0.14, IRON, n=6)
        ring_ax(mb, c + axv * 0.1 + Vector((0, 0, -0.2)), axv,
                [(0.17, -0.035), (0.23, -0.035), (0.23, 0.035), (0.17, 0.035)], IRON, n=8)
    # saco de lona: torno com 2 dobras (raio modulado), gargalo amarrado e boca franzida
    s = F.p(1.6, r - 0.15, 0.0)
    bm = mb.bm
    prof = [(0.38, 0.0), (0.56, 0.18), (0.6, 0.46), (0.52, 0.74), (0.34, 0.92), (0.2, 1.0), (0.19, 1.06),
            (0.27, 1.16), (0.16, 1.24)]
    n = 10
    rows = []
    for rr, h in prof:
        rows.append([bm.verts.new((s[0] + rr * (1.0 + 0.09 * math.cos(2 * t + 0.6)) * math.cos(t),
                                   s[1] + rr * (1.0 + 0.09 * math.cos(2 * t + 0.6)) * math.sin(t), s[2] + h))
                     for t in [2 * math.pi * i / n for i in range(n)]])
    fs = [bm.faces.new(list(reversed(rows[0])))]
    for A, B in zip(rows, rows[1:]):
        for i in range(n):
            j = (i + 1) % n
            fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    fs.append(bm.faces.new(rows[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r_ in rows for v in r_], "Leather", None, 0, 1)     # juta/estopa em tom medio quente
    smooth([f for f in fs[1:-1]])
    EM._lathe(mb, (s[0], s[1], s[2]), [(0.18, 1.0), (0.24, 1.02), (0.24, 1.08), (0.18, 1.1)], BK_BROWN, 8, closed=True)
    fcol("SG_CraftChest", F, -1.1, 2.15, r - 0.75, r + 0.75, -0.5, 1.5)


def rug(mb):
    """passadeira da porta ao estrado (a linha que leva o jogador a estacao): navy com debrum DOURADO rente"""
    x0, x1 = CX - 13.3, CX - 6.45
    mb.box2((x0, CY - 2.2, Z + 0.05), (x1, CY + 2.2, Z + 0.1), "Cloth_SG_Navy", 0.0)
    for s in (-1, 1):
        mb.box2((x0, CY + s * 2.2, Z + 0.05), (x1, CY + s * 1.78, Z + 0.12), GOLD, 0.0)
    for xx in (x0, x1 - 0.42):
        mb.box2((xx, CY - 1.78, Z + 0.05), (xx + 0.42, CY + 1.78, Z + 0.12), GOLD, 0.0)


def windows_in(mb):
    """o lado de dentro das janelas: vidraca quente, moldura de pedra violeta, mainel e travessa de ferro"""
    for a in WIN_A:
        F = fr(a)
        y = YB_IN
        arch_panel(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, 9.4, y - 0.11, y + 0.05, WIN_M[a], n=4)
        arch_band(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, 9.4, 0.3, y - 0.3, y + 0.05, VSTONE, n=4)
        fbox(mb, F, -0.1, 0.1, y - 0.2, y - 0.09, 9.4, WIN_SPRING + WIN_RISE - 0.3, BIRON)
        fbox(mb, F, -WIN_HW, WIN_HW, y - 0.2, y - 0.09, 12.6, 12.8, BIRON)


def chandelier(mb):
    """LUSTRE de ferro negro BAIXO (07.05 / 08.09): ARO de perfil moldurado (8 pontos), 8 VELAS DO KIT em copinhos de
    bronze, 8 PINGENTES em gota com capa de bronze e cubo em BALAUSTRE torneado (ajuste 19: o CRISTAL pendurado e a
    garra que o prendia sairam); correntes ate o florao da abobada.
    Sem colisao (fora do alcance de quem esta no estrado)."""
    x, y = CX, CY
    zr = Z + CHAND_Z
    R = CHAND_R
    ring = [(x + R * math.cos(2 * math.pi * k / 24), y + R * math.sin(2 * math.pi * k / 24), zr) for k in range(25)]
    mb.sweep(ring, [(-0.2, -0.12), (0.2, -0.12), (0.26, 0.0), (0.2, 0.1), (0.1, 0.16), (-0.1, 0.16), (-0.2, 0.1),
                    (-0.26, 0.0)], BIRON, up=(0.0, 0.0, 1.0))
    ring2 = [(x + (R - 0.9) * math.cos(2 * math.pi * k / 16), y + (R - 0.9) * math.sin(2 * math.pi * k / 16), zr - 0.45)
             for k in range(17)]
    mb.tube(ring2, 0.09, GOLD, 5)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        px, py = x + R * ca, y + R * sa
        candle(mb, px, py, zr + 0.14, 0.62, 1.1, dish=False, cup=True)
        # pingente em gota (vidro) com capa de bronze, pendurado no aro de baixo
        b = 2 * math.pi * k / 8
        qx, qy = x + (R - 0.9) * math.cos(b), y + (R - 0.9) * math.sin(b)
        zq = Z + CHAND_Z - 0.62
        EM._lathe(mb, (qx, qy, zq), [(0.0, -0.66), (0.13, -0.35), (0.105, -0.11), (0.05, 0.0)], PALE, 6)
        EM._lathe(mb, (qx, qy, zq), [(0.065, -0.03), (0.08, 0.03), (0.03, 0.09)], GOLD, 6, caps=(True, False))
        mb.rod((qx, qy, zq + 0.1), (qx, qy, zr - 0.45), 0.03, GOLD, 4)
        # raio do aro ate o cubo
        mb.rod((px, py, zr), (x + 0.45 * ca, y + 0.45 * sa, zr + 1.25), 0.07, BIRON, 5)
    EM._lathe(mb, (x, y, zr - 0.5), [(0.0, 0.0), (0.3, 0.2), (0.48, 0.55), (0.4, 0.85), (0.22, 1.1), (0.3, 1.35),
                                     (0.52, 1.5), (0.44, 1.7), (0.16, 1.9), (0.16, 2.4)], BIRON, 6, caps=(False, True))
    # (ajuste 19, pedido do usuario: "esse cristal em cima do pote de pocoes muito ruim, remova isso") o CRISTAL
    # pendurado, a garra de bronze de 3 dedos e a haste que o prendia ao cubo SAIRAM; o cubo em balaustre termina no
    # proprio pingente torneado (ponta fechada em zr - 0,5)
    # correntes ate a abobada (4 tirantes + o fio central ate o florao)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        mb.rod((x + R * math.cos(a), y + R * math.sin(a), zr), (x + 1.1 * math.cos(a), y + 1.1 * math.sin(a), Z + H + IN_DOME_RISE - 0.9),
               0.06, BIRON, 4)
    mb.rod((x, y, zr + 1.9), (x, y, Z + H + IN_DOME_RISE - 0.6), 0.09, BIRON, 5)


def furnishings():
    rng = random.Random(8106)
    mb = MB("SG_Craft_Furnishings", "16_CRAFT", rng, detail="near")
    interior(mb)
    bookcases(mb)
    bench(mb, rng)
    study_tables(mb, rng)
    gallery(mb, rng)
    banners(mb)
    lectern(mb)
    chest(mb)
    rug(mb)
    circle_lanterns(mb)
    windows_in(mb)
    chandelier(mb)
    mb.finish()


def lights():
    light("L_SGCraft_Cauldron", "POINT", (CX, CY, Z + 7.4), 300.0, (0.72, 0.5, 1.0), 0.7)
    light("L_SGCraft_Chandelier", "POINT", (CX, CY, Z + 15.6), 650.0, (0.9, 0.74, 1.0), 1.0)
    p = FD.p(0.0, PORT_Y1 + 2.2, 8.0)
    light("L_SGCraft_DoorLantern", "POINT", tuple(p), 340.0, WARM, 0.5)
    q = fr(0.0).p(0.0, 9.2, 7.6)
    light("L_SGCraft_Bench", "POINT", tuple(q), 900.0, WARM, 0.8)


def build():
    shell()
    dome()
    energy_rings()
    cauldron()
    furnishings()
    lights()
