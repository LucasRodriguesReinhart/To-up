# sg_layout - planta TRAVADA da Ilha 3 (Shadow Garden), versao v4 (PLANO MESTRE aprovado 2026-09-30,
# renders/plano_mestre/PLANO.md). 1 BU = 1 stud, Z para cima. Cotas Z ABSOLUTAS = Y do Roblox.
# Referencial LOCAL de projeto: +Y = norte (entrada -> praca -> vila -> muralha -> castelo -> terraco norte -> saida NO),
# +X = leste (alquimia, jardim-mirante), -X = oeste (invocacao, beco da saida), -Y = sul (ponte de chegada).
# Mundo (Blender do lobby) - mesma regra das Ilhas 1 e 2, com a ponte de chegada CURVA:
#   W3 = T(ancora_mundo) . Rz(WORLD_YAW_DEG) . T(-WORLD_FROM_PREV_local)
#   ancora_mundo = ISLAND_NEXT_ANCHOR_ShadowGarden da Ilha 2 = (-579,227; -650,727; 28,2) (Roblox -579,227; 28,2; 650,727)
#   v4: giro 100 (era 67); a ponte sai da ancora no rumo da Ilha 2 (fwd Roblox -0,9205; 0; -0,3907), faz um arco de 33
#   graus (raio 160, 92 studs) e segue reta ate o patio baixo: 232 no total. Roblox = (x_mundo, z, -y_mundo).
# v4 (plano mestre): castelo 2x (salao 184 x 196 x 84), trono que desliza e abre a ESCADA CARACOL, SALAO SOMBRIO sob o
# castelo com o portal da masmorra, salas da masmorra 3x sob ele, 7 casas visitaveis, saida no NOROESTE.
# Entrada (patio baixo, escadaria, calcada alta, porticos), invocacao, alquimia e praca/fonte tem as MESMAS medidas da
# v3, so transladadas (os modulos antigos rodam pelo sg_relocate ate a onda 1).
import math

# ------------------------------------------------------------------ encaixe na Ilha 2
DB_ANCHOR_WORLD = (-579.2270, -650.7270, 28.2)       # ISLAND_NEXT_ANCHOR_ShadowGarden (Roblox -579,227; 28,2; 650,727)
DB_HEADING_WORLD_DEG = math.degrees(math.atan2(0.3907, -0.9205))   # ~157,0 (rumo da Ilha 2 na ancora)
WORLD_YAW_DEG = 100.0                                # giro da ilha (local +Y -> Roblox (-0,985; 0; 0,174))
BRIDGE_ARC_R = 160.0                                 # raio do arco da ponte de chegada
BRIDGE_STRAIGHT = 140.0                              # reta final (ate o patio baixo)
Y_ENTRY = -334.0                                     # fim da ponte = inicio do patio baixo (EntryLow)


def _bridge_local():
    """polilinha LOCAL da ponte de chegada, da ancora (WORLD_FROM_PREV) ate (0, Y_ENTRY); e o PREV local"""
    ax, ay = 0.0, 0.0
    h0 = math.radians(DB_HEADING_WORLD_DEG)
    hi = math.radians(WORLD_YAW_DEG + 90.0)
    d = hi - h0
    pts = [(ax, ay)]
    ax, ay = ax + 2.0 * math.cos(h0), ay + 2.0 * math.sin(h0)      # 2 retos: o 1o trecho sai TANGENTE ao rumo da Ilha 2
    pts.append((ax, ay))
    sgn = 1.0 if d > 0 else -1.0
    cx, cy = ax + BRIDGE_ARC_R * math.cos(h0 + sgn * math.pi / 2), ay + BRIDGE_ARC_R * math.sin(h0 + sgn * math.pi / 2)
    a0 = math.atan2(ay - cy, ax - cx)
    for k in range(1, 13):
        a = a0 + d * k / 12
        pts.append((cx + BRIDGE_ARC_R * math.cos(a), cy + BRIDGE_ARC_R * math.sin(a)))
    ex, ey = pts[-1]
    pts.append((ex + BRIDGE_STRAIGHT * math.cos(hi), ey + BRIDGE_STRAIGHT * math.sin(hi)))
    # referencial "delta" (origem na ancora, eixos do mundo) -> local da ilha (fim da ponte em (0, Y_ENTRY), +Y = hi)
    a = math.radians(WORLD_YAW_DEG)
    E = pts[-1]
    out = []
    for x, y in pts:
        dx, dy = x - E[0], y - E[1]
        out.append((dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a) + Y_ENTRY))
    return out


BRIDGE_PATH = [(round(x, 3), round(y, 3)) for x, y in _bridge_local()]   # 15 pontos: ancora ... (0, -334)
BRIDGE_PATH[-1] = (0.0, Y_ENTRY)
PREV_X, PREV_Y = BRIDGE_PATH[0]                      # WORLD_FROM_PREV local (~ -25,81; -561,14)
BRIDGE_LEN = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(BRIDGE_PATH, BRIDGE_PATH[1:]))   # ~232


def world_matrix():
    """matriz local -> mundo do lobby (mathutils), so XY (as cotas Z ja sao absolutas)"""
    from mathutils import Matrix, Vector
    ax, ay, _ = DB_ANCHOR_WORLD
    return (Matrix.Translation(Vector((ax, ay, 0.0))) @ Matrix.Rotation(math.radians(WORLD_YAW_DEG), 4, "Z")
            @ Matrix.Translation(Vector((-PREV_X, -PREV_Y, 0.0))))


def to_world_xy(x, y):
    a = math.radians(WORLD_YAW_DEG)
    ax, ay, _ = DB_ANCHOR_WORLD
    lx, ly = x - PREV_X, y - PREV_Y
    return (ax + lx * math.cos(a) - ly * math.sin(a), ay + lx * math.sin(a) + ly * math.cos(a))


def to_roblox(x, y, z):
    wx, wy = to_world_xy(x, y)
    return (wx, z, -wy)


def dir_to_roblox(dx, dy):
    a = math.radians(WORLD_YAW_DEG)
    wx, wy = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return (wx, 0.0, -wy)


def local_of_world(wx, wy):
    """mundo (Blender XY) -> local da ilha"""
    a = math.radians(WORLD_YAW_DEG)
    ax, ay, _ = DB_ANCHOR_WORLD
    dx, dy = wx - ax, wy - ay
    return (dx * math.cos(a) + dy * math.sin(a) + PREV_X, -dx * math.sin(a) + dy * math.cos(a) + PREV_Y)


# ------------------------------------------------------------------ niveis (patamares) - iguais a v3
DECK = 28.2        # ponte de chegada (= ancora da Ilha 2)
P1 = 36.2          # patio da entrada, praca da fonte, vila baixa
SUM = 40.2         # plataforma de invocacao (oeste)
P2 = 44.2          # vila alta, alquimia
P3 = 52.2          # patio do castelo, castelo (Mining Hall), terraco norte, SAIDA (v4)
HALL = P3
EXIT_Z = P3        # v4: a saida sai do terraco norte (a area 4 comeca na cota 52,2)
SEA = -110.0       # mar (so visual)
RISE = 0.8
TREAD = 1.7

LEVELS = (DECK, P1, SUM, P2, P3)

# ------------------------------------------------------------------ chegada: ponte curva -> patio baixo -> escadaria -> calcada
# (entrada da v3 transladada de ENTRY_SHIFT; o sg_entry antigo roda no referencial dele pelo sg_relocate)
ENTRY_SHIFT = (0.0, -106.0)
DECK_W = 18.0
BRIDGE_Y0 = PREV_Y            # compat: ponta de cima (a ponte e a polilinha BRIDGE_PATH)
BRIDGE_Y1 = Y_ENTRY           # fim da ponte / inicio do patio baixo
ENTRY_LOW = (-13.0, -334.0, 13.0, -312.0)     # patio baixo (DECK): portico A
ENTRY_STAIR = (0.0, -312.0, 18.0)             # pe (x, y), largura - sobe para o norte 10 x 0,8 (piso 1,8)
ENTRY_STAIR_N = 10
ENTRY_STAIR_TREAD = 1.8
ENTRY_STAIR_Y1 = ENTRY_STAIR[1] + ENTRY_STAIR_N * ENTRY_STAIR_TREAD   # -294
ENTRY_HIGH = (-12.0, -294.0, 12.0, -264.0)    # calcada alta (P1): portico B
PORTICO_A_Y = -322.0
PORTICO_B_Y = -282.0
ENTRY_SPAWN = (0.0, -272.0)                   # WORLD_ENTRY_ShadowGarden (olhando +Y)

# ------------------------------------------------------------------ praca central (P1) - mesma praca da v3, transladada
PLAZA_SHIFT = (0.0, -94.0)
PLAZA_C = (0.0, -222.0)
PLAZA_R = 26.0
FOUNTAIN_R = 7.0              # fonte (bacia colidivel; nao-andavel)

# ------------------------------------------------------------------ contornos dos patamares (anti-horario)
P1_POLY = [(-24.0, -272.0), (24.0, -272.0), (70.0, -278.0), (116.0, -272.0), (150.0, -254.0), (162.0, -222.0),
           (166.0, -186.0), (172.0, -145.0), (-160.0, -145.0), (-162.0, -190.0), (-166.0, -210.0), (-166.0, -234.0),
           (-158.0, -252.0), (-140.0, -272.0), (-116.0, -280.0), (-70.0, -278.0)]
P2_POLY = [(-180.0, -150.0), (178.0, -150.0), (184.0, -104.0), (180.0, -60.0), (174.0, -18.0), (-172.0, -18.0),
           (-178.0, -60.0), (-184.0, -110.0)]
# P3 = patio-jardim + castelo + becos (oeste: rota da saida; leste: jardim-mirante) + terraco norte
P3_POLY = [(-172.0, -23.0), (172.0, -23.0), (168.0, 30.0), (162.0, 90.0), (156.0, 150.0), (150.0, 220.0),
           (142.0, 280.0), (122.0, 326.0), (84.0, 362.0), (30.0, 380.0), (-30.0, 380.0), (-84.0, 364.0),
           (-122.0, 340.0), (-148.0, 314.0), (-158.0, 270.0), (-158.0, 200.0), (-164.0, 120.0), (-168.0, 60.0)]

# ------------------------------------------------------------------ escadas da planta
# (nome, pe (x, y, z), rumo_graus, largura, n, piso, guardas). Espelho = desnivel / n.
STAIRS = [
    ("Entry", (ENTRY_STAIR[0], ENTRY_STAIR[1], DECK), 90.0, ENTRY_STAIR[2], ENTRY_STAIR_N, ENTRY_STAIR_TREAD, True),
    ("P1P2", (0.0, -168.0, P1), 90.0, 18.0, 10, 1.8, True),         # praca -> vila alta (eixo)
    ("Gate", (0.0, -40.0, P2), 90.0, 20.0, 10, TREAD, True),        # vila alta -> portao da muralha -> patio do castelo
    ("EastP3", (150.0, -40.0, P2), 90.0, 14.0, 10, TREAD, True),    # alquimia -> passagem leste -> jardim-mirante
    ("Summon", (-178.0, -222.0, P1), 180.0, 12.0, 5, TREAD, True),  # ponte do summon -> plataforma (oeste)
]
STAIR_TOP_Z = {"Entry": P1, "P1P2": P2, "Gate": P3, "EastP3": P3, "Summon": SUM}

# ------------------------------------------------------------------ invocacao (oeste) - a da v3 transladada
SUMMON_SHIFT = (-66.0, -104.0)
SUMMON_BRIDGE = ((-166.0, -222.0), (-178.0, -222.0), 12.0)   # (inicio, fim, largura) no P1
SUMMON_C = (-208.5, -222.0)
SUMMON_R = 22.0
SUMMON_TOWER = (-216.0, -222.0)
SUMMON_FACE_DEG = 0.0

# ------------------------------------------------------------------ muralha e portao (P2 -> P3), 2x
WALL_Y0, WALL_Y1 = -23.0, -13.0       # espessura 10 sobre a borda sul do P3
WALL_X = (-172.0, 172.0)
WALL_TOP = P3 + 24.0
GATEHOUSE_W = 24.0                    # vao livre do portao da muralha
GATEHOUSE_H = 32.0
GATEHOUSE_TOWERS = [(-24.0, -18.0, 12.0), (24.0, -18.0, 12.0)]
GATEHOUSE_TOWER_TOP = P3 + 44.0
EAST_WALL_GAP = (150.0, 18.0)         # (x, largura) passagem do topo da escada leste

# ------------------------------------------------------------------ castelo 2x (P3) + MINING HALL interno
CASTLE_FACADE_Y = 61.0                # face externa da fachada
HALL_X0, HALL_X1 = -92.0, 92.0        # interior 184 x 196 x 84
HALL_Y0, HALL_Y1 = 66.0, 262.0
HALL_WALL = 5.0
HALL_CEIL = HALL + 84.0               # 136,2 (teto opaco e colidivel)
HALL_DOOR_W = 28.0                    # porta principal: vao livre 28 x 34 (verga reta) + timpano ogival ate 46
HALL_DOOR_H = 34.0
HALL_TYMPANUM_H = 46.0
NAVE_OUT = (-104.0, 61.0, 104.0, 267.0)       # casca externa com contrafortes
NAVE_WALL_TOP = HALL + 100.0          # 152,2 cornija da nave
NAVE_RIDGE = 228.0
ARCADE_X = 66.0                       # eixo dos pilares da arcada (nave central 128 + naves laterais 24)
ARCADE_Y = [78.0 + 22.5 * k for k in range(8)]
ARCADE_PIER = (4.0, 6.0)
FRONT_TOWERS = [(-116.0, 72.0, 20.0, 214.0), (116.0, 72.0, 20.0, 214.0)]   # (x, y, raio, topo); agulha +65
FRONT_SPIRE_TOP = 279.0
CROWN_BASE = (-38.0, 262.0, 38.0, 344.0)     # base da torre-coroa: presbiterio + camara/poco da escada
CROWN_TOWER = (0.0, 303.0, 30.0, 311.0)      # (x, y, raio do fuste octogonal, topo)
CROWN_SPIRE_TOP = 376.0
CASTLE_FORECOURT = (-100.0, -13.0, 100.0, 61.0)
TRI_ARCH_W, TRI_ARCH_H = 40.0, 60.0          # arco triunfal (nave -> presbiterio)
# PRESBITERIO (na base da torre-coroa): piso P3+2,4, 3 degraus a partir da nave
CHANCEL_Z = P3 + 2.4                          # 54,6
CHANCEL = (-20.0, 262.0, 20.0, 300.0)        # interior (x0, y0, x1, y1)
CHANCEL_STEPS = ((0.0, 256.6), 40.0, 3, 1.8)  # (pe (x, y), largura, n, piso) sobe para o norte ate y 262
THRONE_REST = (0.0, 294.0)                    # centro do trono em repouso (14 x 11 x 20), frente para -Y (nave)
THRONE_SIZE = (14.0, 11.0, 20.0)
THRONE_TRAVEL = 27.5                          # desliza +X (leste) para dentro do bolso
THRONE_PARK = (THRONE_REST[0] + THRONE_TRAVEL, THRONE_REST[1])
THRONE_POCKET = (20.0, 288.0, 35.5, 300.0, CHANCEL_Z, CHANCEL_Z + 22.0)   # bolso na parede leste (x0, y0, x1, y1, z0, z1)
RETABLE_Y = (300.0, 308.0)                    # muro do retabulo entre o presbiterio e o poco
SECRET_ARCH = (12.0, 18.0)                    # arco secreto (largura, altura) no eixo, atras do trono
# ESCADA CARACOL (dentro da base da torre-coroa, desce ao salao sombrio)
SPIRAL_C = (0.0, 322.0)
SPIRAL_R_NEWEL = 3.0
SPIRAL_R_STEP = 13.5                           # degrau util de R 3 a R 13,5 (10,5)
SPIRAL_R_IN = 14.0                             # face interna do poco
SPIRAL_R_OUT = 18.0
SPIRAL_TOP_Z = CHANCEL_Z                       # 54,6 (patamar de topo, sul do poco)
SPIRAL_N = 60
SPIRAL_RISE = 0.8
SPIRAL_BOT_Z = SPIRAL_TOP_Z - SPIRAL_N * SPIRAL_RISE    # 6,6
SPIRAL_A0 = -60.0                              # angulo (graus) do 1o degrau; desce no sentido anti-horario
SPIRAL_A1 = 630.0                              # ultimo degrau: 270 = sul (saida para a galeria)
SPIRAL_WALK_R = 8.25
SPIRAL_LANDING = (-120.0, -60.0)               # setor do patamar de topo (graus)

# ------------------------------------------------------------------ SALAO SOMBRIO (sob o castelo)
CAVE = (-90.0, 88.0, 90.0, 336.0)            # interior (x0, y0, x1, y1)
CAVE_FLOOR = -12.0
CAVE_TOP = 41.0                               # abobada (abaixo do fundo do patamar P3, 42,2)
CAVE_GALLERY_Z = SPIRAL_BOT_Z                  # 6,6
CAVE_GALLERY = (-90.0, 274.0, 90.0, 306.0)   # galeria de chegada (passa em volta do pe do poco)
CAVE_CATWALKS = [(-90.0, 150.0, -80.0, 274.0), (80.0, 150.0, 90.0, 274.0)]   # passarelas a 6,6
CAVE_HANGING_BRIDGE = (-80.0, 196.0, 80.0, 204.0)                             # ponte suspensa a 6,6
# escadaria da galeria ao piso: 2 lances de 12 x 0,775 (piso 1,8), patamar de 6, largura 16 (nome, pe, n, rise, tread)
CAVE_STAIR_W = 16.0
CAVE_STAIRS = [("CaveLow", (0.0, 224.8, CAVE_FLOOR), 12, (-2.7 - CAVE_FLOOR) / 12, 1.8),
               ("CaveHigh", (0.0, 252.4, -2.7), 12, (CAVE_GALLERY_Z + 2.7) / 12, 1.8)]
CAVE_LANDING = (-8.0, 246.4, 8.0, 252.4, -2.7)
CAVE_POOL = (-86.0, 196.0, 86.0, 220.0, -13.5, -15.0)   # rio escuro (x0, y0, x1, y1, lamina, fundo)
CAVE_POOL_BRIDGE_W = 16.0
CAVE_PORTAL = (0.0, 100.0)                    # plano do anel do portal (encara o norte)
CAVE_PORTAL_R = 13.0
CAVE_DAIS = (-16.0, 92.0, 16.0, 116.0, CAVE_FLOOR + 1.6)   # estrado do portal (2 degraus pelo norte)
CAVE_FORGE = (-88.0, 130.0, -50.0, 190.0)    # forja/oficina secreta (oeste)
CAVE_MAPROOM = (50.0, 130.0, 88.0, 190.0)    # sala do mapa (leste)
CAVE_KEEP_OUT = (-92.0, 86.0, -17.0, 92.0, 338.0, 41.8)

# ------------------------------------------------------------------ masmorra: salas 3x sob o salao sombrio, fila em +Y
DUN_Z = -72.0
DUN_CEIL = -28.0
DUN_LX = 0.0                                  # eixo dos vaos e dos portais (x)
DUN_ROOMS = [("R1", (-42.0, 6.0, 42.0, 90.0)), ("R2", (-52.0, 92.0, 52.0, 196.0)), ("R3", (-52.0, 198.0, 52.0, 302.0))]
DUN_LINK_W = 28.0
DUN_LINK_H = 22.0
DUN_WALL = 2.0
DUN_NEXT_W, DUN_NEXT_H, DUN_NEXT_T = 27.0, 21.0, 1.0   # portal da proxima sala (dentro do plano do vao/nicho)
DUN_KEEP_OUT = (-56.0, 2.0, -76.0, 56.0, 306.0, -26.0)
DUN_SPAWN_CLEAR = 14.0
# compat (modulos antigos rodam na v3): portaria da v3 nao existe mais
DUN_LY = None

# ------------------------------------------------------------------ alquimia (P2) - a da v3 transladada
CRAFT_SHIFT = (22.0, -26.0)
CRAFT_C = (112.0, -86.0)
CRAFT_R = 16.0
CRAFT_DOOR_DEG = 180.0
CRAFT_DOOR_W = 8.0
CRAFT_DOOR_H = 11.0

# ------------------------------------------------------------------ saida (NOROESTE, P3) -> ponte -> portao Demon Slayer
EXIT_START = (-116.0, 342.0)          # ISLAND_EXIT_ShadowGarden (borda NO do terraco norte)
EXIT_DEG = 120.0                      # rumo local da ponte (Roblox ~ (-0,766; 0; 0,643))
EXIT_W = 18.0
EXIT_BRIDGE_LEN = 64.0
GATE_ISLET_R = 22.0
GATE_DS_OFF = 12.0
ANCHOR_OFF = 40.0
NEXT_AREA_ID = 4
EXIT_OLD_START = (157.0, -38.0)       # referencial do sg_exit da v3 (sg_relocate)
EXIT_OLD_DEG = 0.0
EXIT_OLD_Z = 44.2

# ------------------------------------------------------------------ jardim-mirante (P3 leste, no lugar da portaria)
MIRANTE_E = (132.0, 170.0, 16.0)      # (x, y, raio) terraco do mirante

# ------------------------------------------------------------------ vila: 7 casas VISITAVEIS
# (nome, tipo, x, y, largura, profundidade, rumo da FRENTE (graus), nivel). Porta = vao 8 x 11 no meio da frente.
HOUSE_TYPES = {"A": dict(floors=2, h0=12.0, h1=12.0, stair=True),      # 2 andares, escada reta ao longo do fundo
               "B": dict(floors=2, h0=14.0, h1=12.0, stair=True),      # taverna: salao de 14 + andar
               "C": dict(floors=1, h0=12.0, h1=0.0, stair=False)}      # terrea, forro aberto
HOUSE_DOOR = (8.0, 11.0)
HOUSE_WALL = 1.0
HOUSES = [("H1", "B", -92.0, -262.0, 38.0, 28.0, 90.0, P1), ("H2", "A", -100.0, -180.0, 32.0, 24.0, 270.0, P1),
          ("H3", "A", 96.0, -258.0, 32.0, 24.0, 90.0, P1), ("H4", "C", 104.0, -180.0, 24.0, 18.0, 270.0, P1),
          ("H5", "A", -66.0, -114.0, 32.0, 24.0, 90.0, P2), ("H6", "C", -122.0, -58.0, 24.0, 18.0, 270.0, P2),
          ("H7", "A", -62.0, -56.0, 32.0, 24.0, 270.0, P2)]
# compat (v3: x, y, largura, profundidade, rumo, nivel)
HOUSE_LOTS = [(x, y, w, d, deg, z) for nm, t, x, y, w, d, deg, z in HOUSES]
STREETS = [
    ([(-26.0, -222.0), (-100.0, -222.0), (-166.0, -222.0)], 10.0, P1),        # praca -> ponte do summon
    ([(26.0, -222.0), (96.0, -222.0), (156.0, -222.0)], 10.0, P1),            # praca -> leste
    ([(0.0, -248.0), (0.0, -264.0)], 14.0, P1),                               # calcada alta -> praca
    ([(0.0, -196.0), (0.0, -168.0)], 14.0, P1),                               # praca -> escada P1P2
    ([(0.0, -150.0), (0.0, -40.0)], 14.0, P2),                                # eixo da vila alta
    ([(-170.0, -86.0), (-60.0, -86.0), (0.0, -86.0), (60.0, -86.0), (95.0, -86.0)], 10.0, P2),   # rua do P2 -> alquimia
    ([(128.0, -88.0), (150.0, -70.0), (150.0, -40.0)], 10.0, P2),             # alquimia -> escada leste
    ([(0.0, -13.0), (0.0, 52.0)], 20.0, P3),                                  # portao -> porta do castelo (eixo)
    ([(150.0, -13.0), (150.0, 40.0), (140.0, 120.0), (132.0, 160.0)], 12.0, P3),   # passagem leste -> mirante
    ([(-90.0, 30.0), (-150.0, 44.0), (-148.0, 100.0), (-136.0, 200.0), (-132.0, 290.0), (-116.0, 334.0)], 12.0, P3),
]
EXIT_ROUTE = STREETS[-1][0]

# ------------------------------------------------------------------ contorno da ilha (topo do penhasco, anti-horario)
ISLAND_CTRL = [(-18.0, -336.0), (18.0, -336.0), (24.0, -312.0), (30.0, -286.0), (70.0, -290.0), (120.0, -284.0),
               (158.0, -262.0), (172.0, -226.0), (172.0, -186.0), (184.0, -150.0), (190.0, -104.0), (186.0, -60.0),
               (180.0, -22.0), (174.0, 30.0), (168.0, 90.0), (162.0, 150.0), (156.0, 220.0), (148.0, 282.0),
               (128.0, 332.0), (88.0, 370.0), (32.0, 390.0), (-32.0, 390.0), (-88.0, 374.0), (-126.0, 348.0),
               (-154.0, 320.0), (-164.0, 270.0), (-164.0, 200.0), (-170.0, 120.0), (-174.0, 60.0), (-178.0, 0.0),
               (-184.0, -60.0), (-190.0, -110.0), (-182.0, -160.0), (-170.0, -196.0), (-170.0, -222.0),
               (-172.0, -250.0), (-154.0, -282.0), (-100.0, -292.0), (-40.0, -288.0), (-30.0, -282.0),
               (-24.0, -312.0)]

# ------------------------------------------------------------------ borda: cachoeiras, colunas, pinheiros
# cachoeiras (x, y do labio na borda, z do labio, rumo da queda graus) - a AGUA e feita no Roblox (FX_Fall_*)
WATERFALLS = [(-187.0, -60.0, P2 - 1.0, 180.0), (174.0, -200.0, P1 - 1.0, 0.0), (-60.0, 383.0, P3 - 1.0, 105.0),
              (-26.8, -296.0, DECK + 2.0, 200.0)]
CLIFF_SPIRES = [(-166.0, 250.0, 12.0, 110.0, "column"), (154.0, 262.0, 11.0, 104.0, "column"),
                (-40.0, 398.0, 14.0, 98.0, "column"), (60.0, 392.0, 10.0, 106.0, "column"),
                (-190.0, -20.0, 9.0, 78.0, "column"), (184.0, -170.0, 8.0, 66.0, "column"),
                (-168.0, -272.0, 8.0, 62.0, "column")]
PINE_GROVES = [(-150.0, -272.0, 6.0, 3), (148.0, -262.0, 8.0, 3), (-164.0, -30.0, 8.0, 3), (170.0, -120.0, 6.0, 2),
               (-154.0, 160.0, 5.0, 2), (136.0, 232.0, 8.0, 3), (112.0, 318.0, 8.0, 3), (-26.0, -258.0, 4.0, 2),
               (30.0, -258.0, 4.0, 2), (116.0, 196.0, 5.0, 2)]


# ------------------------------------------------------------------ helpers de forma
def smooth_closed(ctrl, sub=4):
    """Catmull-Rom fechado sobre pontos 2D (contorno organico)"""
    n = len(ctrl)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = ctrl[(i - 1) % n], ctrl[i], ctrl[(i + 1) % n], ctrl[(i + 2) % n]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    return out


ISLAND_RIM = smooth_closed(ISLAND_CTRL, 3)


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t)), t


def polyline_dist(px, py, pts):
    best = 1e9
    for a, b in zip(pts, pts[1:]):
        d, _ = seg_dist(px, py, a[0], a[1], b[0], b[1])
        best = min(best, d)
    return best


def circle_poly(c, r, step_deg=7.5):
    return [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
            for a in [i * step_deg for i in range(int(round(360.0 / step_deg)))]]


def rect_poly(r):
    x0, y0, x1, y1 = r[:4]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def plaza_poly():
    return circle_poly(PLAZA_C, PLAZA_R, 6.0)


def summon_poly():
    return circle_poly(SUMMON_C, SUMMON_R, 7.5)


def floors():
    """pisos andaveis de SUPERFICIE: (nome, poligono, cota, prioridade) - o de MAIOR prioridade manda"""
    return [
        ("P3", P3_POLY, P3, 50),
        ("P2", P2_POLY, P2, 40),
        ("Summon", summon_poly(), SUM, 35),
        ("EntryHigh", rect_poly(ENTRY_HIGH), P1, 30),
        ("P1", P1_POLY, P1, 20),
        ("EntryLow", rect_poly(ENTRY_LOW), DECK, 10),
    ]


_FLOORS = floors()


def zone_of(x, y):
    for nm, poly, z, pr in _FLOORS:
        if point_in_poly(x, y, poly):
            return z
    return None


def floor_name(x, y):
    for nm, poly, z, pr in _FLOORS:
        if point_in_poly(x, y, poly):
            return nm
    return None


# ------------------------------------------------------------------ escadas / saida
def stair_frame(name):
    for nm, foot, deg, w, n, tread, g in STAIRS:
        if nm == name:
            return foot, deg, w, n, tread, g
    raise KeyError(name)


def stair_top(name):
    foot, deg, w, n, tread, g = stair_frame(name)
    a = math.radians(deg)
    return (foot[0] + math.cos(a) * tread * n, foot[1] + math.sin(a) * tread * n, STAIR_TOP_Z[name])


def exit_dir():
    a = math.radians(EXIT_DEG)
    return (math.cos(a), math.sin(a))


def exit_point(d):
    ux, uy = exit_dir()
    return (EXIT_START[0] + ux * d, EXIT_START[1] + uy * d)


def islet_center():
    return exit_point(EXIT_BRIDGE_LEN + GATE_ISLET_R - 4.0)


def gate_ds_pos():
    return exit_point(EXIT_BRIDGE_LEN + GATE_DS_OFF)


def anchor_pos():
    return exit_point(EXIT_BRIDGE_LEN + ANCHOR_OFF)


def gate_yaw():
    ux, uy = exit_dir()
    return math.atan2(uy, ux) - math.pi / 2


# ------------------------------------------------------------------ escada caracol
def stair_angle(i):
    """angulo (graus) do inicio do degrau i (0..SPIRAL_N); desce SPIRAL_RISE por degrau"""
    return SPIRAL_A0 + (SPIRAL_A1 - SPIRAL_A0) * i / SPIRAL_N


def stair_point(ang_deg, r=SPIRAL_WALK_R):
    a = math.radians(ang_deg)
    return (SPIRAL_C[0] + r * math.cos(a), SPIRAL_C[1] + r * math.sin(a))


def stair_z(ang_deg):
    t = (ang_deg - SPIRAL_A0) / (SPIRAL_A1 - SPIRAL_A0)
    return SPIRAL_TOP_Z - (SPIRAL_TOP_Z - SPIRAL_BOT_Z) * max(0.0, min(1.0, t))


# ------------------------------------------------------------------ minerio do Mining Hall (pontos travados aqui)
MINE_RECT = (-52.0, 80.0, 52.0, 216.0)       # 104 x 136, na nave central (pilares da arcada em x +-66)
MINE_DOOR_LANE = (0.0, 66.0, 96.0, 8.0)      # (x, y0, y1, meia-largura) corredor livre da porta ate dentro
ORE_KINDS = [("COMMON", 2.6), ("UNCOMMON", 3.0), ("EPIC", 3.4), ("SUPERLEGENDARY", 4.4)]
ORE_WALL_CLEAR = 5.0
ORE_PLAN = [("SUPERLEGENDARY", 2), ("EPIC", 10), ("UNCOMMON", 24), ("COMMON", 44)]   # 80 pontos


def ore_blocked(x, y, clear):
    x0, y0, x1, y1 = MINE_RECT
    if x < x0 + clear or x > x1 - clear or y < y0 + clear or y > y1 - clear:
        return True
    lx, ly0, ly1, hw = MINE_DOOR_LANE
    if ly0 - 1.0 <= y <= ly1 and abs(x - lx) < hw + clear:
        return True
    return False


def ore_points():
    """lista (kind, i, x, y, raio): grade hexagonal centrada com leve ruido no MAIOR passo (>= 10,4) que da a contagem
    do plano; raridade por profundidade (porta = comum ... fundo = super, diante do presbiterio)"""
    import random
    rad = dict(ORE_KINDS)
    x0, y0, x1, y1 = MINE_RECT
    need = sum(n for _, n in ORE_PLAN)

    def grid(step):
        rng = random.Random(3303)
        out = []
        row = 0
        ny = int((y1 - y0 - 2 * ORE_WALL_CLEAR) / (step * 0.866) + 1e-6)
        y = y0 + ORE_WALL_CLEAR + ((y1 - y0 - 2 * ORE_WALL_CLEAR) - ny * step * 0.866) / 2.0
        while y <= y1 - ORE_WALL_CLEAR + 1e-6:
            sh = step / 2 if row % 2 else 0.0
            nx = int((x1 - x0 - 2 * ORE_WALL_CLEAR - sh) / step + 1e-6)
            x = x0 + ORE_WALL_CLEAR + sh + ((x1 - x0 - 2 * ORE_WALL_CLEAR - sh) - nx * step) / 2.0
            while x <= x1 - ORE_WALL_CLEAR + 1e-6:
                jx, jy = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8)
                if not ore_blocked(x + jx, y + jy, 3.7):
                    out.append((round(x + jx, 2), round(y + jy, 2)))
                x += step
            y += step * 0.866
            row += 1
        return out
    step = 16.0
    cand = grid(step)
    while len(cand) < need and step > 10.4 + 1e-6:
        step = max(10.4, step - 0.1)
        cand = grid(step)
    cand.sort(key=lambda p: (-(p[1]) + abs(p[0]) * 0.35))
    pts = []
    i = 0
    for kind, n in ORE_PLAN:
        for k in range(n):
            if i >= len(cand):
                break
            x, y = cand[i]
            i += 1
            pts.append((kind, k + 1, x, y, rad[kind]))
    return pts


# ------------------------------------------------------------------ masmorra (fila em +Y, eixo x = DUN_LX)
def dun_rect(name):
    return dict(DUN_ROOMS)[name]


def dun_center(name):
    x0, y0, x1, y1 = dun_rect(name)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def dun_spawn(name):
    """spawn de cada sala: R1 = DUNGEON_Spawn (chegada, 12 do muro sul); R2/R3 = 10 depois do vao SUL"""
    x0, y0, x1, y1 = dun_rect(name)
    return (DUN_LX, y0 + (12.0 if name == "R1" else 10.0))


def dun_links():
    """vaos de ligacao: (nome, x, y do meio da parede) - R1R2 sempre aberto; R2R3 = vao do portal da proxima sala"""
    out = []
    for (na, ra), (nb, rb) in zip(DUN_ROOMS, DUN_ROOMS[1:]):
        out.append(("%s%s" % (na, nb), DUN_LX, (ra[3] + rb[1]) / 2.0))
    return out


def dun_next(name):
    """(x, y) do portal da PROXIMA sala no plano medio da parede: R2 = vao R2R3; R3 = nicho do muro norte"""
    if name == "R2":
        return (DUN_LX, dict((n, y) for n, x, y in dun_links())["R2R3"])
    x0, y0, x1, y1 = dun_rect("R3")
    return (DUN_LX, y1 + DUN_WALL / 2.0)


def dun_exit(name):
    if name == "R1":
        x0, y0, x1, y1 = dun_rect("R1")
        return (x0 + 12.0, y0 + 4.0)
    x0, y0, x1, y1 = dun_rect("R3")
    return (x0 + 8.0, y0 + 6.0)


def dun_exit_r3():
    return dun_exit("R3")


# minerios FIXOS de cada ARENA (posFixa do AreaBuilder.novoMinerio): centro + 6 (R 16) + 10 (R 30, sem 90/270 = eixo dos
# vaos) + 6 (R 42). O marcador diz a raridade do NIVEL 1; o DungeonService promove por nivel.
DUN_ORE_PLAN = {
    "R2": ("EPIC", "UNCOMMON", ("COMMON", "UNCOMMON"), ("COMMON", "COMMON")),
    "R3": ("SUPERLEGENDARY", "EPIC", ("UNCOMMON", "COMMON"), ("COMMON", "UNCOMMON")),
}
DUN_ORE_RINGS = (16.0, 30.0, 42.0)
DUN_ORE_ANGLES = ([30.0 + 60.0 * i for i in range(6)], [0.0, 30.0, 60.0, 120.0, 150.0, 180.0, 210.0, 240.0, 300.0, 330.0],
                  [0.0, 40.0, 140.0, 180.0, 220.0, 320.0])
DUN_ORE_RADIUS = {"COMMON": 2.8, "UNCOMMON": 3.0, "EPIC": 3.4, "SUPERLEGENDARY": 4.4}


def dun_ore_points():
    """(sala, tipo, i, x, y, raio) - 23 por arena (R2, R3); a R1 e a chegada, sem minerio"""
    out = []
    k = 0
    for room in ("R2", "R3"):
        center, inner, mid, outer = DUN_ORE_PLAN[room]
        cx, cy = dun_center(room)
        k += 1
        out.append((room, center, k, cx, cy, DUN_ORE_RADIUS[center]))
        for ring, angs, kinds in ((DUN_ORE_RINGS[0], DUN_ORE_ANGLES[0], (inner, inner)),
                                  (DUN_ORE_RINGS[1], DUN_ORE_ANGLES[1], mid), (DUN_ORE_RINGS[2], DUN_ORE_ANGLES[2], outer)):
            for j, ang in enumerate(angs):
                kind = kinds[j % 2]
                a = math.radians(ang)
                k += 1
                out.append((room, kind, k, round(cx + ring * math.cos(a), 2), round(cy + ring * math.sin(a), 2),
                            DUN_ORE_RADIUS[kind]))
    return out
