# sg_craft - CRAFT da Ilha 3 (Shadow Garden), 5o na hierarquia: o SALAO NOBRE DE ALQUIMIA (refinamento v2, referencia
# refs/v2/ref2_alchemy_interior.png e ref2_alchemy_ext.jpg). Substitui sg_blockout.craft. Tudo sai da planta: CRAFT_C
# (90, -60) no P2, CRAFT_R 16 (raio externo; interior ~13), porta a OESTE (CRAFT_DOOR_DEG 180) com vao 8 x 11 na mesma
# posicao. Os marcadores CRAFT_Station (centro), PLAYER_INTERACT_Craft (5 a oeste, em cima do ESTRADO) e NPC_Craft sao
# do sg_core: aqui so o lugar em volta deles.
#   EXTERIOR (acabamento 2026-09-29: LABORATORIO ARCANO, menos neon): pavilhao redondo (24 faces) de pedra ESCURA sobre
#     SOCO ALTO de obsidiana com remate de pedra violeta; 7 contrafortes com REMATES ALQUIMICOS (colar de latao + esfera
#     de vidro com anel e agulha) no lugar dos pinaculos goticos; 6 janelas ogivais ALTAS em luz QUENTE; portico ogival
#     com moldura de pedra, OCULO de vitral (Glass_SG_Rose), empena com o frasco de prata, 2 estandartes e 2 postes de
#     lanterna; 4 CAMARAS DE VIDRO (tanques com liquido, gaiola de ferro, tampa de latao) no pe dos contrafortes
#     diagonais, cada uma ligada ao contraforte por TUBO -> FLANGE -> PAREDE; domo navy com nervuras de prata,
#     lanternim de obsidiana e o FRASCO GIGANTE no topo com 2 ANEIS ARMILARES de prata (VFX_SGCRAFT_Ring_1/2, girando).
#   INTERIOR (pe-direito 18 ate a cornija, abobada de marmore negro com nervuras claras):
#     - CALDEIRAO (hero): bojo de perfil desenhado (fundo, barriga, ombro, pescoco), BOCA de latao enrolada com
#       espessura real, cinta de ferro negro que abraca a barriga com rebites, MEDALHAO DA ORDEM (sg_emblem.plaque)
#       preso por espelho de latao que abraca a curvatura do bojo (sela + rampa + labio, rebites), 2 orelhas com argola apoiada na barriga, 4 pes de ferro fundido
#       sobre a LAREIRA (4 setores de obsidiana com bocas de ventilacao mostrando as brasas violeta), pocao violeta na
#       boca, colher de pau apoiada na borda e um fio de energia fino ate o cristal do lustre;
#     - ESTANTES de verdade (rodape, montantes nas bissetrizes das faces - o movel acompanha a parede curva sem
#       atravessar -, prateleiras com testeira, fundo, friso e cornija; frontao nas estantes sem janela) com KIT de
#       livros (6 formatos, capa maior que o miolo, lombada com nervuras) arrumado a mao em grupos, inclinados, pilhas
#       e vazios, e KIT de frascos (redondo, tubo de ensaio no suporte, quadrado com rotulo, pote de ingrediente,
#       frasco de pocao grande): vidro em cima, liquido embaixo, tampas diferentes; poucos acesos;
#     - 2 MESAS DE ESTUDO (pernas torneadas sob o tampo, saia, travessa em H, banqueta de 3 pes), bancada do
#       alquimista com alambique ligado ao coletor, atril e bau perto da porta, lustre baixo com o grande cristal;
#     - 2 ESTANDARTES da ordem presos por mao-francesa; GALERIA estreita nas costas (leste), so leitura de profundidade.
# Colisao propria: anel da parede (20 caixas) + portico com o vao, contrafortes, tanques, cobertura, ESTRADO
# (2 x 10-gono), caldeirao (8-gono), bancada, estantes, mesas, atril, bau e 4 postes de lanterna. Luzes (4): caldeirao
# (violeta), lustre, lanternas da porta (quente), bancada (quente).
import math, random
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, Frame, ngon_col
import fm_lib
import sg_layout as L
import sg_emblem as EM

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (10)
NEW_MATS = {
    "Glass_SGCraftAmber": (S(150, 116, 80), 0.15, 0.0, 0.22, S(168, 118, 70), 0.0),    # vidro ambar (potes, frascos)
    "Glass_SGCraftSage": (S(104, 128, 118), 0.15, 0.0, 0.14, S(110, 140, 126), 0.0),   # vidro verde-salvia
    "Glass_SGCraftPale": (S(150, 162, 186), 0.1, 0.0, 0.1, S(120, 136, 170), 0.0),     # vidro claro (frascos, esferas)
    "Cloth_SGCraftBook": (S(98, 42, 52), 0.85, 0.0, 0, None, 0.06),                    # encadernacao VINHO
    "Cloth_SGCraftBookInk": (S(38, 36, 46), 0.8, 0.0, 0, None, 0.05),                  # encadernacao PRETA
    "Cloth_SGCraftBookPlum": (S(86, 68, 102), 0.85, 0.0, 0, None, 0.05),               # roxo dessaturado
    "Cloth_SGCraftBookBrown": (S(96, 64, 44), 0.8, 0.0, 0, None, 0.06),                # couro marrom escuro
    "Potion_SGCraftWine": (S(128, 38, 70), 0.25, 0.0, 0, None, 0.0),                   # liquido vinho-violeta
    "Potion_SGCraftTeal": (S(44, 116, 112), 0.25, 0.0, 0, None, 0.0),                  # liquido verde-azulado
    "Stone_SGCraftDark": (S(54, 52, 74), 0.8, 0.0, 0, None, 0.08),                     # alvenaria ESCURA do pavilhao
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
FLASK_R = 5.4                  # FRASCO maior (era 4)
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

IRON, SILVER, BRASS = "Metal_SG_Iron", "Metal_SG_Silver", "Metal_Brass"
CASTLE, TRIM, BLOCK, NAVY = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Block", "Roof_SG_Navy"
WALL = "Stone_SGCraftDark"     # corpo das paredes (pedra escura fria; contrafortes em Stone_SG_Castle, luar raspando)
WOOD, GLOW, VIOLET = "Wood_SG_Dark", "Lantern_Glow", "SG_Violet_Glow"
OBS, MARB, BIRON = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Metal_SG_BlackIron"
RUNE, CRYS, VDEEP, GOLD = "SG_Rune_Glow", "SG_Crystal_Glow", "SG_VioletDeep_Glow", "Metal_Gold"
VSTONE = "Stone_SG_Violet"
SOCLE = 2.6                    # soco alto de obsidiana (v3)
WIN_FOOT, WIN_SPRING, WIN_RISE, WIN_HW = 9.3, 14.4, 2.5, 1.35   # janelas ALTAS (v3: 9,3 -> 16,9)
OCU_Z, OCU_R = 14.8, 1.7       # oculo sobre a porta (portico)
POST_A = [150.0, 210.0]        # lanternas do circulo magico (ancoras dos raios)
TANK_A = [45.0, 225.0, 315.0]         # camaras de vidro no pe dos contrafortes diagonais (135 ficaria na rota da dungeon)
TANK_Y = 19.45                 # centro radial dos tanques (face do contraforte em 17,5; soco do contraforte ate 17,75)
CHAND_Z, CHAND_R, CHAND_TIP = 12.6, 5.0, 8.2   # lustre BAIXO (lido da camera da porta): aro, raio, ponta do cristal
AMBER, SAGE, PALE, ROSE = "Glass_SGCraftAmber", "Glass_SGCraftSage", "Glass_SGCraftPale", "Glass_SG_Rose"
BK_WINE, BK_INK, BK_PLUM, BK_BROWN = "Cloth_SGCraftBook", "Cloth_SGCraftBookInk", "Cloth_SGCraftBookPlum", "Cloth_SGCraftBookBrown"
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


def lathe(mb, x, y, z, prof, m, n=12, rot=0.0, cap0=True, cap1=True):
    """solido de revolucao: prof = [(raio, altura)] de baixo para cima; raio 0 = polo"""
    bm = mb.bm
    rows = []
    for r, h in prof:
        if r < 1e-4:
            rows.append([bm.verts.new((x, y, z + h))])
        else:
            rows.append([bm.verts.new((x + r * math.cos(rot + 2 * math.pi * i / n),
                                       y + r * math.sin(rot + 2 * math.pi * i / n), z + h)) for i in range(n)])
    for A, B in zip(rows, rows[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
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


# ------------------------------------------------------------------ remate alquimico (no lugar do pinaculo gotico)
def finial(mb, x, y, z, s=1.0):
    """colar de latao assentado no bloco de pedra, ESFERA DE VIDRO com anel de latao no equador e agulha no topo:
    a silhueta do telhado passa a dizer 'laboratorio' (retortas), nao 'igreja'"""
    lathe(mb, x, y, 0.0, [(0.0, z), (0.5 * s, z), (0.5 * s, z + 0.16 * s), (0.36 * s, z + 0.3 * s), (0.0, z + 0.3 * s)],
          BRASS, n=8)
    R = 0.56 * s
    zc = z + 0.26 * s + R
    prof = [(0.0, zc - R)] + [(R * math.sin(math.pi * k / 6), zc - R * math.cos(math.pi * k / 6)) for k in range(1, 6)]
    lathe(mb, x, y, 0.0, prof + [(0.0, zc + R)], PALE, n=8)
    lathe(mb, x, y, 0.0, [(R * 0.97, zc - 0.07 * s), (R + 0.06 * s, zc - 0.05 * s), (R + 0.06 * s, zc + 0.05 * s),
                          (R * 0.97, zc + 0.07 * s)], BRASS, n=8, cap0=False, cap1=False)
    lathe(mb, x, y, 0.0, [(0.0, zc + R - 0.06 * s), (0.14 * s, zc + R - 0.06 * s), (0.1 * s, zc + R + 0.1 * s),
                          (0.02 * s, zc + R + 0.9 * s), (0.0, zc + R + 0.92 * s)], BRASS, n=6)


# ------------------------------------------------------------------ casca: embasamento, parede, frisos, contrafortes
def shell():
    mb = MB("SG_Craft_Shell", "16_CRAFT", random.Random(8101), detail="near")
    # SOCO ALTO de obsidiana (base da ordem) + remate de pedra violeta (acabamento: sem o friso de neon)
    ring_band(mb, 15.15, 16.3, -0.4, SOCLE, OBS, A0, A1)
    ring_band(mb, 15.35, 16.05, SOCLE, SOCLE + 0.4, VSTONE, A0, A1)
    ring_band(mb, R_IN, R_OUT, -0.3, H, WALL, A0, A1)                    # parede (24-gono sem as 4 faces da porta)
    ring_band(mb, 15.45, 15.95, 8.7, 9.2, VSTONE, A0, A1)                # friso violeta sob as janelas
    ring_band(mb, 15.45, 16.4, H - 0.6, H, OBS, A0, A1)                  # cornija de obsidiana
    ring_band(mb, 15.0, 16.15, H, H + 1.0, VSTONE, 0.0, 360.0)           # anel de apoio do domo (volta inteira)
    ring_band(mb, 15.9, 16.22, H + 0.1, H + 0.3, SILVER, 0.0, 360.0)     # fio de prata do anel
    # contrafortes (ritmo; alinhados as nervuras do domo): pe de obsidiana alto, pingadeira violeta e REMATE ALQUIMICO
    for a in BUTT_A:
        F = fr(a)
        pside(mb, F, [(15.3, 0.0), (17.5, 0.0), (17.5, 7.6), (16.7, 9.9), (15.3, 9.9)], -0.95, 0.95, CASTLE)
        pside(mb, F, [(15.3, 9.9), (16.7, 9.9), (16.7, 15.0), (15.3, 17.3)], -0.78, 0.78, CASTLE)
        fbox(mb, F, -1.1, 1.1, 15.3, 17.75, -0.1, SOCLE, OBS, 0.08)      # pe do contraforte (acompanha o soco)
        fbox(mb, F, -1.05, 1.05, 16.6, 17.62, 7.2, 7.5, VSTONE, 0.05)    # pingadeira
        fbox(mb, F, -0.84, 0.84, 16.5, 16.8, 14.85, 15.15, VSTONE, 0.04) # pingadeira de cima
        fbox(mb, F, -0.62, 0.62, 16.0, 17.24, H - 0.6, H + 1.4, VSTONE, 0.05)
        c = F.p(0.0, 16.62, H + 1.4)
        finial(mb, c[0], c[1], c[2], 1.0)
    # janelas ogivais ALTAS (por fora): vidraca quente, moldura violeta saliente (recuo de 0,4), mainel e travessa de
    # ferro negro, peitoril violeta
    for a in WIN_A:
        F = fr(a)
        y = apo(R_OUT)
        arch_panel(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, WIN_FOOT, y - 0.05, y + 0.06, WIN_M[a])
        arch_band(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, WIN_FOOT, 0.38, y - 0.05, y + 0.42, VSTONE)
        fbox(mb, F, -0.1, 0.1, y, y + 0.22, WIN_FOOT, WIN_SPRING + WIN_RISE - 0.3, BIRON)
        fbox(mb, F, -WIN_HW, WIN_HW, y, y + 0.22, 12.6, 12.8, BIRON)
        fbox(mb, F, -1.95, 1.95, y - 0.05, y + 0.66, 9.0, 9.3, VSTONE, 0.05)
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


def lab_tanks(mb):
    """CAMARAS DE VIDRO do laboratorio (substituem os canteiros de cristal de neon) no pe de 3 contrafortes
    diagonais (o do noroeste fica livre: rota da dungeon): soco octogonal de obsidiana, anel de latao, tanque de vidro com o liquido ate 2/3, gaiola de 4 montantes
    e 2 aros de ferro negro, tampa de latao com gola; o tubo de latao sobe da tampa, faz a curva e entra no contraforte
    por uma FLANGE aparafusada (tubo -> flange -> parede)."""
    for i, a in enumerate(TANK_A):
        F = fr(a)
        c = F.p(0.0, TANK_Y, 0.0)
        x, y = c[0], c[1]
        liq = POT_W if a == 225.0 else POT_T
        lathe(mb, x, y, Z, [(0.0, -0.3), (1.5, -0.3), (1.5, 0.5), (1.38, 0.64), (0.0, 0.64)], OBS, n=8, rot=math.pi / 8)
        lathe(mb, x, y, Z, [(0.0, 0.64), (1.3, 0.64), (1.32, 0.78), (1.28, 0.94), (0.0, 0.94)], BRASS, n=16)
        lathe(mb, x, y, Z, [(1.15, 0.94), (1.15, 3.7), (0.0, 3.7)], liq, n=16, cap0=False)
        lathe(mb, x, y, Z, [(1.15, 3.7), (1.15, 5.06), (0.0, 5.06)], PALE, n=16, cap0=False)
        for hz in (2.3, 4.35):
            lathe(mb, x, y, Z, [(1.14, hz - 0.1), (1.23, hz - 0.08), (1.23, hz + 0.08), (1.14, hz + 0.1)], BIRON,
                  n=16, cap0=False, cap1=False)
        for k in range(4):
            b = F.a + math.pi / 4 + k * math.pi / 2
            px, py = x + 1.22 * math.cos(b), y + 1.22 * math.sin(b)
            mb.box((0.13, 0.13, 4.2), (px, py, Z + 3.0), (0, 0, b), BIRON, 0.0)
        lathe(mb, x, y, Z, [(0.0, 5.04), (1.32, 5.04), (1.32, 5.26), (1.12, 5.54), (0.64, 5.78), (0.28, 5.88), (0.28, 6.02),
                            (0.36, 6.06), (0.36, 6.18), (0.0, 6.18)], BRASS, n=16)
        # tubo: sobe da gola, curva e entra no contraforte (face em y = 17,5)
        zp = 7.0
        pts = [F.p(0.0, TANK_Y, 6.1), F.p(0.0, TANK_Y, zp - 0.5), F.p(0.0, TANK_Y - 0.12, zp - 0.24),
               F.p(0.0, TANK_Y - 0.4, zp - 0.06), F.p(0.0, TANK_Y - 0.75, zp), F.p(0.0, 17.45, zp)]
        mb.tube(pts, 0.15, BRASS, 8)
        # flange na face do contraforte (4 parafusos) + colar no tubo
        mb.cyl(0.38, 0.12, F.p(0.0, 17.56, zp), F.r(math.pi / 2, 0.0, 0.0), BRASS, n=10, bevel=0.0)
        for k in range(4):
            b = math.pi / 4 + k * math.pi / 2
            mb.box((0.08, 0.06, 0.08), F.p(0.27 * math.cos(b), 17.64, zp + 0.27 * math.sin(b)), F.r(), BIRON, 0.0)
        mb.cyl(0.21, 0.14, F.p(0.0, 18.0, zp), F.r(math.pi / 2, 0.0, 0.0), BRASS, n=8, bevel=0.0)
        col_box("SG_CraftTank", (2.8, 2.8, 6.6), (x, y, Z + 3.0), (0, 0, F.a))


def portal(mb):
    """portico saliente da porta (oeste): vao ogival 8 x 11 aberto de ponta a ponta (mesma posicao), moldura de pedra
    violeta em 2 camadas com capa de obsidiana, pilastras de obsidiana com REMATES ALQUIMICOS, OCULO de vitral sobre a
    porta, empena com o emblema de prata do frasco, 2 ESTANDARTES da ordem e 2 POSTES de lanterna dourada na frente"""
    F = FD
    y0, y1 = PORT_Y0, PORT_Y1
    for s in (-1, 1):
        fbox(mb, F, s * DW, s * PORT_HW, y0, y1, -0.3, H, WALL)                        # ombreiras (macico)
        fbox(mb, F, s * (DW + 0.05), s * (PORT_HW + 0.45), y0 - 0.2, y1 + 0.5, -0.4, SOCLE, OBS, 0.08)   # soco
        fbox(mb, F, s * (DW + 0.8), s * (PORT_HW + 0.45), y1 + 0.02, y1 + 0.55, SOCLE, SOCLE + 0.4, VSTONE, 0.04)
        fbox(mb, F, s * 7.3, s * 8.35, y1, y1 + 0.5, SOCLE, H, OBS, 0.06)             # pilastra de canto
        fbox(mb, F, s * 7.2, s * 8.45, y1 - 0.6, y1 + 0.6, H, H + 1.5, VSTONE, 0.06)   # base do remate
        c = F.p(s * 7.82, y1 - 0.05, H + 1.5)
        finial(mb, c[0], c[1], c[2], 1.3)
    spandrels(mb, F, DW, RISE, SPRING, H, y0, y1, WALL)
    # moldura do vao (frente e dentro) em 2 camadas de pedra (sem o fio de neon) + capa de obsidiana acima
    arch_band(mb, F, DW, RISE, SPRING, 0.9, 0.8, y1, y1 + 0.5, VSTONE)
    arch_band(mb, F, DW + 0.8, RISE + 0.8, SPRING, SOCLE + 0.4, 0.18, y1, y1 + 0.3, VSTONE)
    arch_band(mb, F, DW + 0.98, RISE + 0.98, SPRING, 6.3, 0.42, y1, y1 + 0.38, OBS)
    arch_band(mb, F, DW, RISE, SPRING, 0.8, 0.7, y0 - 0.4, y0, VSTONE)
    # OCULO de vitral sobre a porta (atravessa o portico: vidraca nas duas faces), moldura violeta, cruz de ferro
    ring = [(OCU_R * math.cos(2 * math.pi * k / 16), OCU_Z + OCU_R * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    ringo = [((OCU_R + 0.45) * math.cos(2 * math.pi * k / 16), OCU_Z + (OCU_R + 0.45) * math.sin(2 * math.pi * k / 16))
             for k in range(16)]
    pslab(mb, F, ring, y1 - 0.06, y1 + 0.05, ROSE)
    pslab(mb, F, ring, y0 - 0.05, y0 + 0.06, ROSE)
    band(mb, F, ring + ring[:1], ringo + ringo[:1], y1 - 0.05, y1 + 0.4, VSTONE)
    fbox(mb, F, -0.09, 0.09, y1, y1 + 0.2, OCU_Z - OCU_R, OCU_Z + OCU_R, BIRON)
    fbox(mb, F, -OCU_R, OCU_R, y1, y1 + 0.2, OCU_Z - 0.09, OCU_Z + 0.09, BIRON)
    # cornija do portico e empena
    fbox(mb, F, -PORT_HW - 0.4, PORT_HW + 0.4, y0 + 0.4, y1 + 0.6, H - 0.6, H, OBS, 0.05)
    GH = 7.4                                                      # empena gotica (ingreme)
    pslab(mb, F, [(-7.0, H), (7.0, H), (0.0, H + GH)], y1 - 1.4, y1, WALL)
    for s in (-1, 1):
        a = F.p(s * 7.4, y1 - 0.55, H - 0.1)
        b = F.p(0.0, y1 - 0.55, H + GH + 0.5)
        mb.beam(a, b, 1.4, 0.55, VSTONE, 0.05)
    c = F.p(0.0, y1 - 0.55, H + GH + 0.4)
    SL.spire(mb, (c[0], c[1]), 0.55, c[2], 2.0, SILVER, n=4)
    # emblema de prata: o frasco (bojo + gargalo + boca) na empena - o que o craft faz, lido da rua
    yb0, yb1 = y1, y1 + 0.18
    ce = H + 2.3
    pslab(mb, F, [(1.15 * math.cos(2 * math.pi * k / 12 - math.pi / 2), ce + 1.15 * math.sin(2 * math.pi * k / 12 - math.pi / 2))
                  for k in range(12)], yb0, yb1, SILVER)
    pslab(mb, F, [(-0.34, ce + 0.8), (0.34, ce + 0.8), (0.34, ce + 2.25), (-0.34, ce + 2.25)], yb0, yb1, SILVER)
    pslab(mb, F, [(-0.62, ce + 2.25), (0.62, ce + 2.25), (0.62, ce + 2.6), (-0.62, ce + 2.6)], yb0, yb1, SILVER)
    # soleira de obsidiana (topo 0,05 acima do piso, como o calcamento das ruas)
    fbox(mb, F, -DW, DW, y0 - 0.2, y1 + 0.5, -0.3, 0.05, OBS)
    # ESTANDARTES da ordem (debrum dourado) na face do portico, entre a moldura e as pilastras
    for s in (-1, 1):
        EM.banner(mb, mb, mb, mb, F.p(s * 6.3, y1 + 0.5, 17.0), math.radians(DOOR), 1.7, 8.2, tails=True, trim=GOLD)
    # POSTES DE LANTERNA DOURADA na frente da porta (o ritmo de lanternas da referencia chega ate a porta)
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


# ------------------------------------------------------------------ domo, nervuras de prata, lanternim
def dome():
    mb = MB("SG_Craft_Dome", "16_CRAFT", random.Random(8102), detail="near")
    # casca fechada (sem disco de fundo: a abobada de dentro fica visivel de baixo)
    dome_shell(mb, DOME_R - 0.4, DOME_RISE - 0.4, DOME_R, DOME_RISE, DOME_Z, NAVY, n=24, rings=8)
    # nervuras de prata sobre os contrafortes / o portico
    for a in RIB_A:
        ar = math.radians(a)
        pts = []
        for k in range(15):
            phi = (math.pi / 2) * 0.86 * k / 14.0
            rr = (DOME_R + 0.08) * math.cos(phi)
            if rr < LAN_R + 0.25:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + DOME_Z + (DOME_RISE + 0.08) * math.sin(phi)))
        up = (-math.sin(ar), math.cos(ar), 0.0)
        mb.sweep(pts, [(-0.24, -0.34), (0.34, -0.34), (0.34, 0.34), (-0.24, 0.34)], SILVER, up=up)
    # lanternim: tambor octogonal com fendas quentes + anel de prata (assento do frasco)
    mb.cyl(LAN_R, LAN_Z1 - LAN_Z0, (CX, CY, Z + (LAN_Z0 + LAN_Z1) / 2.0), (0, 0, math.pi / 8), OBS, n=8, bevel=0.0)
    for k in range(8):
        F = fr(45.0 * k)
        y = LAN_R * math.cos(math.pi / 8)
        arch_panel(mb, F, 0.5, 0.62, 31.0, 29.4, y - 0.05, y + 0.06, "Window_Warm", n=3)
        fbox(mb, fr(45.0 * k + 22.5), -0.3, 0.3, LAN_R - 0.3, LAN_R + 0.25, 28.9, LAN_Z1, VSTONE)
    mb.cyl(LAN_R + 0.5, 0.65, (CX, CY, Z + LAN_Z1 + 0.32), (0, 0, math.pi / 8), SILVER, n=8, bevel=0.0)
    mb.cyl(LAN_R + 0.12, 0.55, (CX, CY, Z + LAN_Z0 + 0.28), (0, 0, math.pi / 8), VSTONE, n=8, bevel=0.0)
    flask(mb)
    mb.finish()
    # cobertura (colisao): octogono no topo da parede
    ngon_col("SG_CraftRoof", CX, CY, 8, R_OUT + 0.8, Z + H, Z + DOME_Z + 1.0)


def flask(mb):
    """o FRASCO GIGANTE: bojo de vidro com o liquido violeta ESCURO ate o equador (acabamento: neon moderado), gargalo,
    boca e rolha de prata, preso ao lanternim por 4 garras de prata"""
    zc = FLASK_ZC
    R = FLASK_R
    fill = 0.0                                     # nivel do liquido no equador: metade magia, metade vidro (v2)
    th_f = math.acos(-fill / R)                    # angulo (a partir do polo de baixo) do nivel
    rn = 1.7
    th_n = math.pi - math.asin(rn / R)
    liq = [(0.0, zc - R)]
    for k in range(1, 9):
        t = th_f * k / 8.0
        liq.append((R * math.sin(t), zc - R * math.cos(t)))
    lathe(mb, CX, CY, Z, liq, VDEEP, n=18, cap1=True)
    gl = []
    for k in range(0, 6):
        t = th_f + (th_n - th_f) * k / 5.0
        gl.append((R * math.sin(t) + 0.02, zc - R * math.cos(t)))
    gl[0] = (gl[0][0], gl[0][1] + 0.06)
    gtop = zc - R * math.cos(th_n)
    gl += [(rn, gtop + 1.1), (rn, gtop + 4.0), (rn + 0.4, gtop + 4.35), (rn + 0.4, gtop + 4.8), (rn - 0.12, gtop + 4.8)]
    lathe(mb, CX, CY, Z, gl, ROSE, n=18)
    # rolha de prata + anel do gargalo
    lathe(mb, CX, CY, Z, [(0.0, gtop + 4.4), (rn - 0.15, gtop + 4.4), (rn + 0.06, gtop + 5.6), (rn + 0.4, gtop + 5.85),
                          (rn + 0.25, gtop + 6.3), (0.5, gtop + 6.6), (0.5, gtop + 7.1), (0.0, gtop + 7.35)], SILVER, n=12)
    lathe(mb, CX, CY, Z, [(rn + 0.02, gtop + 1.5), (rn + 0.26, gtop + 1.5), (rn + 0.26, gtop + 2.0), (rn + 0.02, gtop + 2.0)],
          SILVER, n=12)
    # garras (do anel do lanternim ao bojo)
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        p0 = (CX + (LAN_R + 0.35) * ca, CY + (LAN_R + 0.35) * sa, Z + LAN_Z1 + 0.55)
        zz = zc - 1.6
        rr = math.sqrt(R * R - 1.6 * 1.6) + 0.14
        p1 = (CX + rr * ca, CY + rr * sa, Z + zz)
        mb.beam(p0, p1, 0.5, 0.42, SILVER, 0.0)
        mb.ico(0.4, p1, SILVER, 1)


def energy_rings():
    """2 ANEIS ARMILARES de prata em volta do frasco (acabamento: eram tubos de neon; agora a forma de observatorio le
    sem brilho): banda chata (0,56 de largura, 0,16 de espessura) com 12 marcas de graduacao; pecas moveis como as do
    summon, girando em torno do eixo VERTICAL do frasco (a inclinacao faz o bamboleio ler de longe)"""
    for idx, (tilt, azim, R, rpm) in enumerate(((18.0, 0.0, 7.9, 4.2), (-34.0, 90.0, 9.9, -3.4)), 1):
        vf = MB("VFX_SGCRAFT_Ring_%d" % idx, "12_VFX_HELPERS", random.Random(8110 + idx), detail="near")
        t, p = math.radians(tilt), math.radians(azim)
        ct, st, cp, sp = math.cos(t), math.sin(t), math.cos(p), math.sin(p)

        def W(lx, ly, lz):
            ly, lz = ly * ct - lz * st, ly * st + lz * ct
            return (CX + lx * cp - ly * sp, CY + lx * sp + ly * cp, Z + FLASK_ZC + lz)
        nrm = W(0.0, 0.0, 1.0)
        up = (nrm[0] - CX, nrm[1] - CY, nrm[2] - Z - FLASK_ZC)
        pts = [W(R * math.cos(2 * math.pi * k / 32.0), R * math.sin(2 * math.pi * k / 32.0), 0.0) for k in range(33)]
        vf.sweep(pts, [(-0.08, -0.28), (0.08, -0.28), (0.08, 0.28), (-0.08, 0.28)], SILVER, up=up, caps=False)
        for k in range(12):
            th = 2 * math.pi * (k + 0.5) / 12.0
            c = W((R + 0.1) * math.cos(th), (R + 0.1) * math.sin(th), 0.0)
            a = W((R + 0.1) * math.cos(th), (R + 0.1) * math.sin(th), 0.3)
            vf.rod(tuple(2 * c[i] - a[i] for i in range(3)), a, 0.07, GOLD, 4)
        ob = vf.finish()
        ob["pivot"] = [round(CX, 3), round(CY, 3), round(Z + FLASK_ZC, 3)]
        ob["axis"] = [0.0, 0.0, 1.0]
        ob["rpm"] = rpm
        ob["vfx"] = "anel armilar %d do frasco do craft: inclinado, gira em torno do eixo vertical" % idx


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


def magic_circle(mb):
    """CIRCULO MAGICO no piso em volta do estrado (acabamento: brilho moderado): 1 anel fino de energia rente
    (+0,055..0,09) e 10 glifos em violeta escuro (sem as barras soltas); o anel de ouro embutido faz a moldura. As 2
    lanternas da porta (POST_A) sao as ancoras do circulo (sem glifo embaixo delas)"""
    ring_band(mb, 8.82, 9.0, 0.055, 0.09, VDEEP, 0.0, 360.0, 7.5)
    ring_band(mb, 7.1, 7.25, 0.055, 0.085, GOLD, 0.0, 360.0, 7.5)
    for k in range(12):
        a = 15.0 + 30.0 * k
        if min(abs(a - p) for p in POST_A) < 20.0:
            continue
        ar = math.radians(a)
        c = pol(8.05, a, 0.072)
        if k % 3 == 0:                                    # duas barras tangentes
            for d in (-0.2, 0.2):
                mb.box((0.2, 0.56, 0.036), (c[0] + d * math.cos(ar), c[1] + d * math.sin(ar), c[2]), (0, 0, ar), VDEEP, 0.0)
        elif k % 3 == 1:                                  # barra + tico radial
            mb.box((0.2, 0.6, 0.036), c, (0, 0, ar), VDEEP, 0.0)
            t = pol(8.5, a, 0.072)
            mb.box((0.26, 0.2, 0.036), t, (0, 0, ar), VDEEP, 0.0)
        else:                                             # losango
            mb.box((0.42, 0.42, 0.036), c, (0, 0, ar + math.pi / 4), VDEEP, 0.0)


def dais_step(mb, r, z0, z1, n=30):
    """degrau do estrado: corpo de obsidiana, tampo de marmore negro embutido e fio de ouro na borda do tampo"""
    lathe(mb, CX, CY, Z, [(0.0, z0), (r, z0), (r, z1 - 0.06), (r - 0.06, z1), (0.0, z1)], OBS, n=n)
    lathe(mb, CX, CY, Z, [(0.0, z1 - 0.02), (r - 0.55, z1 - 0.02), (r - 0.55, z1 + 0.02), (0.0, z1 + 0.02)], MARB, n=n)
    ring_band(mb, r - 0.55, r - 0.3, z1 - 0.02, z1 + 0.03, GOLD, 0.0, 360.0, 360.0 / n)


def interior(mb):
    """piso, estrado, circulo e abobada (no mesmo objeto da mobilia - os materiais sao os mesmos, menos MeshParts)"""
    # ESTRADO circular de 2 degraus (obsidiana + tampo de marmore negro + fio de ouro): o caldeirao sobe no palco
    dais_step(mb, DAIS_R1, -0.3, DAIS_H1)
    dais_step(mb, DAIS_R2, DAIS_H1, DAIS_H2)
    # piso nobre radial (topo 0,05 acima do piso; a colisao e a do P2): marmore negro com incrustacao de prata
    for r0, r1, m, st in ((DAIS_R1 + 0.05, 6.45, SILVER, 12.0), (6.45, 9.85, MARB, 12.0), (9.85, 10.1, SILVER, 12.0),
                          (10.1, R_IN + 0.1, MARB, STEP)):
        ring_band(mb, r0, r1, -0.3, 0.05, m, 0.0, 360.0, st)
    magic_circle(mb)
    # frisos internos: rodape de obsidiana (interrompido atras das estantes: o movel tem rodape proprio e encosta na
    # parede), friso violeta sobre as estantes, cornija violeta
    for a0, a1 in ((A0, SHELF_RUNS[1][0]), (SHELF_RUNS[1][1], SHELF_RUNS[0][0] + 360.0), (SHELF_RUNS[0][1] + 360.0, A1)):
        ring_band(mb, R_IN - 0.3, R_IN + 0.05, 0.0, 0.8, OBS, a0, a1)
    ring_band(mb, R_IN - 0.4, R_IN + 0.05, 9.16, 9.4, VSTONE, A0, A1)
    ring_band(mb, R_IN - 0.6, R_IN + 0.05, 17.4, 18.0, VSTONE, 0.0, 360.0)
    # abobada de marmore negro + nervuras claras apoiadas em misulas de obsidiana + chave central
    dome_shell(mb, R_IN, IN_DOME_RISE, R_IN + 0.4, IN_DOME_RISE + 0.4, H, MARB)
    for a in RIB_A:
        ar = math.radians(a)
        pts = []
        for k in range(13):
            phi = (math.pi / 2) * 0.9 * k / 12.0
            rr = (R_IN - 0.06) * math.cos(phi)
            if rr < 1.0:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + H + (IN_DOME_RISE - 0.06) * math.sin(phi)))
        mb.sweep(pts, [(-0.3, -0.3), (0.3, -0.3), (0.3, 0.3), (-0.3, 0.3)], TRIM, up=(-math.sin(ar), math.cos(ar), 0.0))
        F = fr(a)
        if a != DOOR:
            fbox(mb, F, -0.5, 0.5, R_IN - 0.8, R_IN + 0.02, 16.0, 17.4, OBS, 0.05)
    mb.cyl(1.3, 0.75, (CX, CY, Z + H + IN_DOME_RISE - 0.38), (0, 0, 0), VSTONE, n=12, bevel=0.0)
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


def cauldron():
    mb = MB("SG_Craft_Cauldron", "16_CRAFT", random.Random(8105), detail="hero")
    x, y = CX, CY
    # LAREIRA: anel de obsidiana com 4 bocas de ventilacao estreitas (0/90/180/270) sob uma CAPA continua de pedra
    # violeta (a capa passa por cima das bocas como verga); dentro, o leito de brasa escuro com a brasa violeta rasa
    for a0 in (10.0, 100.0, 190.0, 280.0):
        ring_band(mb, 2.25, 3.4, HEARTH_Z0, HEARTH_Z1, OBS, a0, a0 + 70.0, 7.0)
    ring_band(mb, 2.16, 3.5, HEARTH_Z1, HEARTH_Z1 + 0.1, VSTONE, 0.0, 360.0, 7.5)
    lathe(mb, x, y, Z, [(0.0, HEARTH_Z0), (2.3, HEARTH_Z0), (2.3, 1.56), (0.0, 1.56)], BIRON, n=16)   # leito
    lathe(mb, x, y, Z, [(0.0, 1.55), (1.7, 1.55), (1.55, 1.6), (0.0, 1.62)], "SG_VioletSoft_Glow", n=16)   # brasa rasa
    # 4 PES de ferro fundido (diagonais: o medalhao da porta e as argolas ficam livres) - sapata na capa da lareira,
    # canela afunilada que entra no fundo do bojo
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        zf = HEARTH_Z1 + 0.1
        lathe(mb, x + 2.85 * ca, y + 2.85 * sa, Z, [(0.0, zf), (0.4, zf), (0.4, zf + 0.08), (0.27, zf + 0.2), (0.0, zf + 0.22)],
              BIRON, n=8)
        cone(mb, (x + 2.85 * ca, y + 2.85 * sa, Z + zf + 0.12), (x + 2.2 * ca, y + 2.2 * sa, Z + 3.25), 0.2, 0.32, IRON, 8)
        mb.ico(0.24, (x + 2.8 * ca, y + 2.8 * sa, Z + zf + 0.3), IRON, 1)
    # BOJO (ferro) + BOCA enrolada (latao) - uma so silhueta, transicao no pescoco
    lathe(mb, x, y, Z, CAUL, IRON, n=24, cap1=False)
    lathe(mb, x, y, Z, LIP, GOLD, n=24, cap0=False)
    # CINTA de ferro negro abracando a barriga (o medalhao e rebitado nela) + rebites de latao
    lathe(mb, x, y, Z, hug(BELLY_Z - 0.26, BELLY_Z + 0.26, 0.08), BIRON, n=24, cap0=False, cap1=False)
    for k in range(12):
        a = 15.0 + 30.0 * k
        if min(abs(a - 180.0), abs(a), abs(a - 360.0)) < 25.0:
            continue
        ar = math.radians(a)
        rr = caul_r(BELLY_Z) + 0.1
        mb.cyl(0.07, 0.08, (x + rr * math.cos(ar), y + rr * math.sin(ar), Z + BELLY_Z), (math.pi / 2, 0.0, ar + math.pi / 2),
               GOLD, n=6, bevel=0.0)
    # MEDALHAO DA ORDEM (porta e alquimista): disco de obsidiana (sg_emblem.plaque) rente ao ferro, preso por um
    # ESPELHO de latao que ABRACA o bojo - o pe do espelho segue a curvatura (sela), a face sobe em rampa ate o labio
    # que prende a borda do disco; de lado le como aro fino, nao como bloco. 4 rebites na rampa.
    for ang in (math.pi, 0.0):
        f = Vector((math.cos(ang), math.sin(ang), 0.0))
        O = Vector((x, y, Z + MED_Z)) + f * caul_r(MED_Z)
        medal_bezel(mb, O, f)
        EM.plaque(mb, mb, mb, mb, tuple(O + f * MED_CD), ang, MED_R)
    # ORELHAS com ARGOLA (norte e sul): orelha fundida no ombro, pino de latao, argola apoiada na barriga
    pin = (3.3, 5.02)
    Rr, tr = 0.42, 0.075
    phi = next((math.radians(d) for d in range(0, 80, 2) if _ring_ok(pin, Rr, tr, math.radians(d))), math.radians(60))
    for ang in (math.pi / 2, -math.pi / 2):
        ca, sa = math.cos(ang), math.sin(ang)
        mb.box((0.84, 0.36, 0.38), (x + 3.02 * ca, y + 3.02 * sa, Z + pin[1]), (0, 0, ang), IRON, 0.06)
        tx, ty = -sa, ca
        pc = (x + pin[0] * ca, y + pin[0] * sa, Z + pin[1])
        mb.rod((pc[0] - 0.24 * tx, pc[1] - 0.24 * ty, pc[2]), (pc[0] + 0.24 * tx, pc[1] + 0.24 * ty, pc[2]), 0.07, GOLD, 6)
        cr, ch = pin[0] + Rr * math.sin(phi), pin[1] - Rr * math.cos(phi)
        pts = [(x + (cr + Rr * math.cos(2 * math.pi * j / 16)) * ca, y + (cr + Rr * math.cos(2 * math.pi * j / 16)) * sa,
                Z + ch + Rr * math.sin(2 * math.pi * j / 16)) for j in range(17)]
        mb.tube(pts, tr, GOLD, 6)
    # POCAO violeta (moderada) + 3 bolhas + colher de pau apoiada no labio (do lado do alquimista)
    mb.cyl(2.39, 0.1, (x, y, Z + LIQ_Z - 0.05), (0, 0, 0), VDEEP, n=24, bevel=0.0)
    for (dx, dy, r) in ((-0.78, 0.65, 0.3), (0.26, -1.04, 0.22), (1.05, 0.3, 0.16)):
        mb.ico(r, (x + dx, y + dy, Z + LIQ_Z), RUNE, 1, scale=(1, 1, 0.55))
    a = math.radians(40.0)
    d0, d1 = (1.3, 5.55), (2.6, 6.25 + 0.1)             # apoia na quina de DENTRO do labio
    sl = (d1[1] - d0[1]) / (d1[0] - d0[0])
    e = (3.85, d0[1] + (3.85 - d0[0]) * sl)
    mb.rod((x + d0[0] * math.cos(a), y + d0[0] * math.sin(a), Z + d0[1]),
           (x + e[0] * math.cos(a), y + e[0] * math.sin(a), Z + e[1]), 0.09, WOOD, 6)
    mb.ico(0.13, (x + e[0] * math.cos(a), y + e[0] * math.sin(a), Z + e[1]), WOOD, 1)
    # FIO DE ENERGIA fino (violeta escuro) do cristal do lustre ate a pocao
    mb.rod((x, y, Z + LIQ_Z), (x, y, Z + CHAND_TIP + 0.05), 0.05, VDEEP, 6)
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
    return 2 if (gold or t in "TF") else 0


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
               (0.14, 1.1), (0.0, 1.14)], 7, 0.0, 0.44, 0.43),
    "potion": ([(0.0, 0.0), (0.28, 0.0), (0.48, 0.14), (0.55, 0.4), (0.46, 0.74), (0.28, 0.96), (0.14, 1.12), (0.13, 1.42),
                (0.17, 1.47), (0.0, 1.52)], 7, 0.0, 0.6, 0.55),
    "vial": ([(0.0, 0.0), (0.1, 0.03), (0.1, 0.92), (0.12, 0.95), (0.0, 0.98)], 6, 0.0, 0.58, 0.12),
    "square": ([(0.0, 0.0), (0.34, 0.0), (0.34, 0.68), (0.3, 0.74), (0.13, 0.86), (0.12, 0.98), (0.15, 1.0), (0.0, 1.04)],
               4, math.pi / 4, None, 0.25),
    "small": ([(0.0, 0.0), (0.26, 0.0), (0.28, 0.3), (0.24, 0.4), (0.2, 0.44), (0.2, 0.5), (0.0, 0.5)], 7, 0.0, None, 0.28),
}
LIQ = {"wine": POT_W, "teal": POT_T, "lit_v": CRYS, "lit_a": GLOW, "violet": VDEEP}


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
    """pilha de pergaminhos enrolados (3 embaixo, 2 em cima, apoiados nos de baixo) com fita vinho em alguns"""
    r = 0.13
    top = r + math.sqrt((2 * r) ** 2 - 0.135 ** 2)
    for k, (uu, vv) in enumerate(((0.13, r), (0.4, r), (0.67, r), (0.265, top), (0.535, top))):
        row.rod((u + uu, 0.06, vv), (u + uu, 0.74, vv), r, CANVAS, 7)
        if k in (0, 2, 3):
            row.rod((u + uu, 0.36, vv), (u + uu, 0.44, vv), r + 0.012, BK_WINE, 7)
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
    292.5: [("B", 0), ("D", 1), ("F", 0), ("A", 1), ("K", 0)],
}
SHELF_V = [0.5, 2.16, 3.82, 5.48, 7.14]      # tampos (o 1o e o fundo da caixa, sobre o rodape)
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
        fprism(mb, F, [(-13.1 * TAN, 13.1), (13.1 * TAN, 13.1), (wl, YB_IN), (-wl, YB_IN)], 0.42, 8.6, WOOD)
        # prateleiras (trapezio entre os montantes) com testeira mais alta na frente
        for v in SHELF_V:
            t = 0.08 if v == SHELF_V[0] else 0.14
            fprism(mb, F, [(-_uin(12.06), 12.06), (_uin(12.06), 12.06), (_uin(13.1), 13.1), (-_uin(13.1), 13.1)], v - t, v,
                   WOOD)
            fbox(mb, F, -_uin(11.98), _uin(11.98), 11.98, 12.06, v - 0.2, v + 0.03, WOOD, 0.02)
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
    # alambique: fogareiro de ferro, caldeira de latao, capitel com o bico
    p = F.p(-2.5, 11.3, top)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.0), (0.62, 0.0), (0.62, 0.55), (0.5, 0.62), (0.0, 0.62)], IRON, n=8)
    mb.cyl(0.36, 0.12, (p[0], p[1], p[2] + 0.64), (0, 0, 0), GLOW, n=8, bevel=0.0)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.66), (0.5, 0.66), (0.78, 0.95), (0.8, 1.35), (0.55, 1.72), (0.24, 1.92),
                                 (0.24, 2.35), (0.42, 2.6), (0.3, 2.95), (0.0, 3.05)], BRASS, n=12)
    tube = []
    for k in range(10):
        t = k / 9.0
        tube.append(F.p(-2.2 + 1.45 * t, 11.3 - 0.2 * t, top + 2.72 + 0.25 * math.sin(math.pi * t) - 1.64 * t * t))
    mb.tube(tube, 0.075, BRASS, 6)
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
    travessa em H; livro aberto, balanca, alambique pequeno / vela e tinteiro, lanterna assentada; banqueta; tapete navy
    com debrum dourado rente"""
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
            vp = F.p(1.45, rc - 0.55, top)
            lathe(mb, vp[0], vp[1], vp[2], [(0.0, 0.0), (0.22, 0.0), (0.22, 0.05), (0.08, 0.1), (0.0, 0.1)], BRASS, n=8)
            mb.cyl(0.12, 0.55, (vp[0], vp[1], vp[2] + 0.37), (0, 0, 0), "Plaster_SG", n=6, bevel=0.0)
            mb.ico(0.1, (vp[0], vp[1], vp[2] + 0.74), GLOW, 1, scale=(1, 1, 1.6))
            tp = F.p(1.05, rc + 0.35, top)
            lathe(mb, tp[0], tp[1], tp[2], [(0.0, 0.0), (0.2, 0.0), (0.22, 0.22), (0.1, 0.3), (0.0, 0.3)], IRON, n=6)
            mb.rod(F.p(1.05, rc + 0.35, top + 0.2), F.p(1.35, rc + 0.62, top + 1.0), 0.03, PAGES, 4)
        row.emit(mb, F, 0.0, 0.0)
        # lanterna dourada pequena no canto de tras (base assentada no tampo)
        s = 0.46
        EM.lantern_head(mb, mb, F.p(-1.45 if i == 0 else 1.45, rc + 0.62, top + 1.14 * s), math.radians(a), s)
        fcol("SG_CraftTable", F, -2.0, 2.0, rc - 1.15, rc + 1.15, -0.5, 2.78)


def gallery(mb, rng):
    """GALERIA anular estreita a +8,35..8,95 nas costas (leste) do salao: nao entravel (sem escada), so leitura de
    profundidade - piso de madeira sobre misulas, balaustrada de ferro negro e livros do kit; sem colisao"""
    ring_band(mb, 10.8, R_IN + 0.05, GAL_Z0, GAL_Z1, WOOD, GAL_A0, GAL_A1)
    ring_band(mb, 10.72, 10.98, GAL_Z0 - 0.15, GAL_Z1 + 0.05, VSTONE, GAL_A0, GAL_A1)    # testeira
    for k in range(7):
        a = GAL_A0 + 15.0 * k
        pside(mb, fr(a), [(R_IN + 0.02, GAL_Z0), (11.0, GAL_Z0), (R_IN + 0.02, GAL_Z0 - 1.8)], -0.4, 0.4, OBS)
    # balaustrada de ferro negro
    for k in range(13):
        a = GAL_A0 + 7.5 * k
        mb.box((0.16, 0.16, 2.35), pol(11.05, a, GAL_Z1 + 1.175), (0, 0, math.radians(a)), BIRON, 0.0)
    ring_band(mb, 10.9, 11.2, GAL_Z1 + 2.3, GAL_Z1 + 2.55, BIRON, GAL_A0, GAL_A1)        # corrimao
    ring_band(mb, 10.98, 11.12, GAL_Z1 + 1.1, GAL_Z1 + 1.25, BIRON, GAL_A0, GAL_A1)      # travessa
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
            fbox(mb, F, u - 0.16, u + 0.16, YB_IN - 0.06, YB_IN + 0.02, 14.5, 15.1, BIRON)


def circle_lanterns(mb):
    """2 POSTES DE LANTERNA dourada ancorando o circulo magico dos dois lados da passadeira (referencia: lanternas em
    volta do estrado) - colisao fina propria, fora da volta do caldeirao (raio 5,2) e da passadeira"""
    for a in POST_A:
        b = pol(8.05, a, 0.05)
        EM.lantern_post(mb, mb, b, math.radians(a), h=4.4, s=0.8)
        col_box("SG_CraftLanternPost", (1.0, 1.0, 5.6), (b[0], b[1], b[2] + 2.6), (0, 0, math.radians(a)))


def lectern(mb):
    """atril com o livro de receitas (perto da porta, lado sul): o 'menu' do craft"""
    F = fr(217.5)
    r = 11.0
    lathe(mb, *F.p(0.0, r, 0.0), [(0.0, 0.0), (0.68, 0.0), (0.68, 0.16), (0.5, 0.3), (0.0, 0.3)], IRON, n=8)
    fbox(mb, F, -0.22, 0.22, r - 0.22, r + 0.22, 0.3, 3.05, WOOD, 0.03)
    fbox(mb, F, -0.6, 0.6, r - 0.5, r + 0.5, 2.7, 3.0, WOOD, 0.03)
    t = math.radians(24.0)
    nY, nZ = -math.sin(t), math.cos(t)

    def at(u, d):
        return F.p(u, r + nY * d, 3.35 + nZ * d)
    mb.box((1.7, 1.25, 0.14), at(0.0, 0.0), F.r(t, 0.0, 0.0), WOOD, 0.0)
    mb.box((0.06, 1.25, 0.12), at(0.0, 0.1), F.r(t, 0.0, 0.0), WOOD, 0.0)
    mb.box((1.6, 1.12, 0.05), at(0.0, 0.095), F.r(t, 0.0, 0.0), BK_WINE, 0.0)
    for s in (-1, 1):
        mb.box((0.72, 1.0, 0.1), at(s * 0.38, 0.17), F.r(t, s * 0.06, 0.0), PAGES, 0.0)
    fcol("SG_CraftLectern", F, -0.85, 0.85, r - 0.75, r + 0.75, -0.5, 3.6)


def chest(mb):
    """bau de ingredientes da dungeon (perto da porta, lado norte) + saco de lona"""
    F = fr(142.5)
    r = 11.4
    fbox(mb, F, -1.0, 1.0, r - 0.6, r + 0.6, 0.0, 1.05, WOOD, 0.06)
    fbox(mb, F, -1.05, 1.05, r - 0.65, r + 0.65, 1.05, 1.45, WOOD, 0.08)
    for u in (-0.6, 0.6):
        fbox(mb, F, u - 0.12, u + 0.12, r - 0.68, r + 0.68, -0.02, 1.5, IRON)
    fbox(mb, F, -0.16, 0.16, r - 0.72, r - 0.64, 0.8, 1.2, SILVER)
    s = F.p(1.55, r - 0.2, 0.0)
    mb.ico(0.55, (s[0], s[1], s[2] + 0.5), "Cloth_Canvas", 1, scale=(1.0, 1.0, 0.95))
    mb.cyl(0.24, 0.3, (s[0], s[1], s[2] + 1.12), (0, 0, 0), "Cloth_Canvas", n=6, r2=0.34, bevel=0.0)
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
        arch_panel(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, 9.4, y - 0.06, y + 0.05, WIN_M[a])
        arch_band(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, 9.4, 0.3, y - 0.3, y + 0.05, VSTONE)
        fbox(mb, F, -0.1, 0.1, y - 0.16, y - 0.04, 9.4, WIN_SPRING + WIN_RISE - 0.3, BIRON)
        fbox(mb, F, -WIN_HW, WIN_HW, y - 0.16, y - 0.04, 12.6, 12.8, BIRON)


def chandelier(mb):
    """LUSTRE de ferro negro BAIXO (aro a +12,6, lido da camera da porta) com 8 velas acesas, 8 pingentes de VIDRO e o
    GRANDE CRISTAL SG_Crystal_Glow pendendo sobre o caldeirao (ponta a +8,2; o fio de energia sai dela); correntes ate a
    abobada. Sem colisao (fora do alcance de quem esta no estrado)."""
    x, y = CX, CY
    zr = Z + CHAND_Z
    R = CHAND_R
    ring = [(x + R * math.cos(2 * math.pi * k / 16), y + R * math.sin(2 * math.pi * k / 16), zr) for k in range(17)]
    mb.tube(ring, 0.22, BIRON, 6)
    ring2 = [(x + (R - 0.9) * math.cos(2 * math.pi * k / 16), y + (R - 0.9) * math.sin(2 * math.pi * k / 16), zr - 0.45)
             for k in range(17)]
    mb.tube(ring2, 0.12, GOLD, 5)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        px, py = x + R * ca, y + R * sa
        # vela no aro (copinho dourado + vela + chama)
        mb.cyl(0.3, 0.16, (px, py, zr + 0.3), (0, 0, 0), GOLD, n=6, bevel=0.0)
        mb.cyl(0.14, 0.6, (px, py, zr + 0.68), (0, 0, 0), "Plaster_SG", n=6, bevel=0.0)
        mb.ico(0.13, (px, py, zr + 1.1), GLOW, 1, scale=(1, 1, 1.7))
        # pingente de vidro entre as velas, pendurado no aro de baixo
        b = 2 * math.pi * k / 8
        qx, qy = x + (R - 0.9) * math.cos(b), y + (R - 0.9) * math.sin(b)
        lathe(mb, qx, qy, Z, [(0.0, CHAND_Z - 1.75), (0.22, CHAND_Z - 1.25), (0.27, CHAND_Z - 0.9), (0.0, CHAND_Z - 0.55)],
              PALE, n=5)
        mb.rod((qx, qy, Z + CHAND_Z - 0.6), (qx, qy, zr - 0.45), 0.04, GOLD, 4)
        # raio do aro ate o cubo
        mb.rod((px, py, zr), (x + 0.5 * ca, y + 0.5 * sa, zr + 1.3), 0.08, BIRON, 4)
    mb.cyl(0.55, 1.1, (x, y, zr + 1.4), (0, 0, 0), BIRON, n=8, r2=0.3, bevel=0.0)
    mb.cyl(0.7, 0.2, (x, y, zr + 0.85), (0, 0, 0), GOLD, n=8, bevel=0.0)
    # o GRANDE CRISTAL central (bipiramide alongada) pendendo do cubo
    t0 = CHAND_TIP
    lathe(mb, x, y, Z, [(0.0, t0), (0.6, t0 + 1.0), (1.02, t0 + 2.1), (0.78, t0 + 3.1), (0.36, t0 + 3.7), (0.0, t0 + 4.0)],
          CRYS, n=6, rot=math.pi / 6)
    mb.cyl(0.48, 0.3, (x, y, Z + t0 + 3.8), (0, 0, 0), GOLD, n=6, bevel=0.0)
    mb.rod((x, y, Z + t0 + 3.9), (x, y, zr + 0.85), 0.09, BIRON, 4)
    # correntes ate a abobada (4 tirantes + o fio central)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        mb.rod((x + R * math.cos(a), y + R * math.sin(a), zr), (x + 1.1 * math.cos(a), y + 1.1 * math.sin(a), Z + H + IN_DOME_RISE - 0.9),
               0.07, BIRON, 4)
    mb.rod((x, y, zr + 1.9), (x, y, Z + H + IN_DOME_RISE - 0.6), 0.1, BIRON, 4)


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
