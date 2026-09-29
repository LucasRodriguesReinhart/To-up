# sg_layout - planta TRAVADA da Ilha 3 (Shadow Garden). 1 BU = 1 stud, Z para cima. Cotas Z ABSOLUTAS = Y do Roblox.
# Referencial LOCAL de projeto (o da concept aprovada, refs/concept_sg_aprovado.png):
#   +Y = norte (entrada -> praca -> vila -> muralha -> castelo), +X = leste (craft, dungeon, saida Demon Slayer),
#   -Y = sul (chegada vinda da Ilha 2 Dragon Ball), -X = oeste (plataforma de invocacao).
# Mundo (Blender do lobby) - mesma regra de encaixe da Ilha 2:
#   W3 = T(ancora_mundo) . Rz(rumo_mundo - 90) . T(-entrada_local)
#   ancora_mundo = ISLAND_NEXT_ANCHOR_ShadowGarden da Ilha 2 no mundo = (-579,227; -650,727; 28,2)
#   rumo_mundo = 157 graus (fwd Roblox (-0,9205; 0; -0,3907)) -> giro 67
#   entrada_local = WORLD_FROM_PREV (inicio da ponte de chegada desta ilha) = (0, PREV_Y, DECK)
#   Roblox = (x_mundo, z, -y_mundo)
# PIPELINE DAS ILHAS 1/2, LAYOUT PROPRIO: patamares que sobem para o norte, castelo gotico no topo, mineracao DENTRO
# do castelo (Mining Hall), vila so de ambientacao. Hierarquia: castelo > mining hall > entrada > dungeon > craft >
# saida > vila.
import math

# ------------------------------------------------------------------ encaixe na Ilha 2
DB_ANCHOR_WORLD = (-579.2270, -650.7270, 28.2)       # ISLAND_NEXT_ANCHOR_ShadowGarden (Roblox -579,227; 28,2; 650,727)
DB_HEADING_WORLD_DEG = math.degrees(math.atan2(0.3907, -0.9205))   # ~157,0
WORLD_YAW_DEG = DB_HEADING_WORLD_DEG - 90.0          # ~67,0
PREV_Y = -262.0                                      # WORLD_FROM_PREV (y local), ponta sul da ponte de chegada


def world_matrix():
    """matriz local -> mundo do lobby (mathutils), so XY (as cotas Z ja sao absolutas)"""
    from mathutils import Matrix, Vector
    ax, ay, _ = DB_ANCHOR_WORLD
    return (Matrix.Translation(Vector((ax, ay, 0.0))) @ Matrix.Rotation(math.radians(WORLD_YAW_DEG), 4, "Z")
            @ Matrix.Translation(Vector((0.0, -PREV_Y, 0.0))))


def to_world_xy(x, y):
    a = math.radians(WORLD_YAW_DEG)
    ax, ay, _ = DB_ANCHOR_WORLD
    ly = y - PREV_Y
    return (ax + x * math.cos(a) - ly * math.sin(a), ay + x * math.sin(a) + ly * math.cos(a))


def to_roblox(x, y, z):
    wx, wy = to_world_xy(x, y)
    return (wx, z, -wy)


def dir_to_roblox(dx, dy):
    a = math.radians(WORLD_YAW_DEG)
    wx, wy = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return (wx, 0.0, -wy)


# ------------------------------------------------------------------ niveis (patamares)
DECK = 28.2        # ponte de chegada (= ancora da Ilha 2)
P1 = 36.2          # patamar 1: patio da entrada, praca da fonte, vila baixa
SUM = 40.2         # plataforma de invocacao (oeste)
P2 = 44.2          # patamar 2: vila alta, craft, saida Demon Slayer
P3 = 52.2          # patamar 3: castelo (Mining Hall no mesmo piso), portaria da dungeon
HALL = P3
EXIT_Z = P2
SEA = -110.0       # mar (so visual)
RISE = 0.8         # espelho maximo
TREAD = 1.7

LEVELS = (DECK, P1, SUM, P2, P3)

# ------------------------------------------------------------------ chegada (sul): ponte -> patio baixo -> escadaria -> calcada
DECK_W = 18.0
BRIDGE_Y0 = PREV_Y            # -262: ponta sul (encosta na ancora da Ilha 2)
BRIDGE_Y1 = -228.0            # fim da ponte / inicio do patio baixo
ENTRY_LOW = (-13.0, -228.0, 13.0, -206.0)     # patio baixo (DECK): portico A
ENTRY_STAIR = (0.0, -206.0, 18.0)             # pe (x, y), largura - sobe para o norte 10 x 0,8 (piso 1,8)
ENTRY_STAIR_N = 10
ENTRY_STAIR_TREAD = 1.8
ENTRY_STAIR_Y1 = ENTRY_STAIR[1] + ENTRY_STAIR_N * ENTRY_STAIR_TREAD   # -188
ENTRY_HIGH = (-12.0, -188.0, 12.0, -158.0)    # calcada alta (P1): portico B, desemboca na praca
PORTICO_A_Y = -216.0
PORTICO_B_Y = -176.0
ENTRY_SPAWN = (0.0, -166.0)                   # WORLD_ENTRY_ShadowGarden (olhando +Y, para a praca e o castelo)

# ------------------------------------------------------------------ praca central (P1)
PLAZA_C = (0.0, -128.0)
PLAZA_R = 26.0
FOUNTAIN_R = 7.0              # fonte (bacia colidivel; nao-andavel)

# ------------------------------------------------------------------ contornos dos patamares (anti-horario)
P1_POLY = [(-100.0, -134.0), (-96.0, -150.0), (-62.0, -162.0), (-24.0, -164.0), (24.0, -164.0), (62.0, -162.0),
           (104.0, -152.0), (134.0, -128.0), (146.0, -100.0), (140.0, -78.0), (-116.0, -78.0), (-108.0, -96.0),
           (-100.0, -106.0)]
P2_POLY = [(-116.0, -83.0), (-40.0, -83.0), (40.0, -83.0), (118.0, -83.0), (148.0, -66.0), (157.0, -52.0),
           (157.0, -24.0), (146.0, -4.0), (-108.0, -4.0), (-120.0, -40.0)]
# P3 = patio do castelo + patio leste (dungeon) + pegada do castelo. O resto do topo (oeste e nordeste do castelo) e
# terreno bravo (rocha em coluna, pinheiros, cachoeira) - moldura, nao piso vazio.
P3_POLY = [(-80.0, -9.0), (126.0, -9.0), (130.0, 40.0), (124.0, 98.0), (98.0, 106.0), (60.0, 106.0),
           (56.0, 176.0), (-56.0, 176.0), (-60.0, 60.0), (-78.0, 40.0)]

# ------------------------------------------------------------------ escadas da planta
# (nome, pe (x, y, z), rumo_graus, largura, n, piso, guardas). Espelho = desnivel / n.
STAIRS = [
    ("Entry", (ENTRY_STAIR[0], ENTRY_STAIR[1], DECK), 90.0, ENTRY_STAIR[2], ENTRY_STAIR_N, ENTRY_STAIR_TREAD, True),
    ("P1P2", (0.0, -100.0, P1), 90.0, 16.0, 10, TREAD, True),          # praca -> vila alta (eixo)
    ("Gate", (0.0, -26.0, P2), 90.0, 16.0, 10, TREAD, True),           # vila alta -> portao da muralha -> castelo
    ("EastP3", (112.0, -26.0, P2), 90.0, 12.0, 10, TREAD, True),       # vila alta (craft) -> patio leste (dungeon)
    ("Summon", (-112.0, -118.0, P1), 180.0, 12.0, 5, TREAD, True),     # ponte do summon -> plataforma (oeste)
]
STAIR_TOP_Z = {"Entry": P1, "P1P2": P2, "Gate": P3, "EastP3": P3, "Summon": SUM}

# ------------------------------------------------------------------ invocacao (oeste): ponte curta + plataforma redonda
SUMMON_BRIDGE = ((-100.0, -118.0), (-112.0, -118.0), 12.0)   # (inicio, fim, largura) no P1
SUMMON_C = (-142.5, -118.0)
SUMMON_R = 22.0
SUMMON_TOWER = (-150.0, -118.0)       # maquina/torre no fundo da plataforma (encara leste)
SUMMON_FACE_DEG = 0.0                 # a torre olha para +X (para quem chega pela ponte)

# ------------------------------------------------------------------ muralha e portao (P2 -> P3)
WALL_Y0, WALL_Y1 = -9.0, -3.0         # espessura da muralha sobre a borda sul do P3
WALL_X = (-80.0, 126.0)
GATEHOUSE_W = 16.0                    # vao livre do portao da muralha
GATEHOUSE_H = 18.0
GATEHOUSE_TOWERS = [(-14.0, -6.0, 7.0), (14.0, -6.0, 7.0)]    # (x, y, raio) torres que ladeiam o portao
EAST_WALL_GAP = (112.0, 12.0)         # (x, largura) passagem do topo da escada leste

# ------------------------------------------------------------------ castelo (P3) + MINING HALL interno
CASTLE_FACADE_Y = 40.0
# SALAO MAIOR (setor 04b, 2026-09-29, pedido do usuario: "o castelo por dentro ta muito pouco espacoso"):
#   antes 84 x 88 x 28 (pilastras saindo 3,25: vao livre 77,5); agora 96 x 99 x 48 com pilastras rasas (1,85: vao
#   livre 92,3) e ABSIDE do trono cavada na base da torre-coroa (arco triunfal de 34 no eixo com a ROSACEA da lua
#   acima; trono a ~120 da porta). Revisao 04b-2/3: pe-direito 36 -> 48 para caber arco largo + rosacea de 18 no fundo.
#   A porta, a fachada (y 40), o patio e a rota de entrada nao mudam. Limites: a oeste o beco do castelo (a borda do
#   P3 em x ~ -57) segura a largura; ao norte a rota do mirante norte (sg_water, ponto (-20, 150)) segura a nave
#   retangular - por isso o ganho de profundidade vem da abside dentro da torre-coroa.
HALL_X0, HALL_X1 = -48.0, 48.0        # interior 96 x 99 x 48 (+ abside)
HALL_Y0, HALL_Y1 = 44.0, 143.0
HALL_WALL = 3.5                       # espessura das paredes externas
HALL_CEIL = HALL + 48.0               # teto interno (opaco e colidivel: segura a camera) - pe-direito 48
HALL_DOOR_W = 16.0                    # porta principal (fachada sul): vao 16 x 18
HALL_DOOR_H = 18.0
FRONT_TOWERS = [(-58.0, 42.0, 10.0, 142.0), (58.0, 42.0, 10.0, 142.0)]   # (x, y, raio, topo) torres da fachada
CROWN_TOWER = (0.0, 158.0, 16.0, 196.0)      # torre-coroa (heroi), atras da nave; a base guarda a ABSIDE do trono
CROWN_SPIRE_TOP = 232.0
CASTLE_FORECOURT = (-46.0, -3.0, 46.0, 40.0)   # patio de chegada em frente a fachada
# ABSIDE (dentro da base da torre-coroa): presbiterio de meia largura APSE_HW de HALL_Y1 ate o centro da torre e meio
# hexagono de raio APSE_R (vertices a 0/60/120/180 graus) ao norte. Arco triunfal e abobada: nascenca APSE_SPRING,
# fecho APSE_KEY (acima do piso). Piso da abside = estrado do trono (degraus).
APSE_C = (CROWN_TOWER[0], CROWN_TOWER[1])
APSE_HW = 11.0
APSE_R = 11.0
APSE_SPRING = 22.0
APSE_KEY = 34.0
# ARCO TRIUNFAL (parede norte da nave): vao LIVRE = presbiterio (TRI_HW = APSE_HW), nascenca TRI_SPRING e flecha
# TRI_RISE; TRI_ORDERS ordens de TRI_STEP escalonadas na espessura da parede -> na face da nave o arco tem
# 2 * (TRI_HW + TRI_ORDERS * TRI_STEP) = 34 de vao (35% da nave) e fecho a ~28,5 (22,5 no vao livre = nascenca da
# abobada da abside); a rosacea da lua (18 de diametro) ocupa a parede acima ate a abobada
TRI_HW = APSE_HW
TRI_SPRING = 10.0
TRI_RISE = 12.5
TRI_ORDERS = 3
TRI_STEP = 2.0


def apse_poly():
    """contorno interno (x, y) do presbiterio + abside, anti-horario, a partir da face interna norte da nave"""
    cx, cy = APSE_C
    pts = [(-APSE_HW, HALL_Y1), (APSE_HW, HALL_Y1)]
    for a in (0.0, 60.0, 120.0, 180.0):
        pts.append((cx + APSE_R * math.cos(math.radians(a)), cy + APSE_R * math.sin(math.radians(a))))
    return pts


# zona de mineracao DENTRO do salao (sem colunas no meio; o auto-minerador anda reto)
MINE_RECT = (-45.0, 50.0, 45.0, 139.0)       # x0, y0, x1, y1 (90 x 89; antes 76 x 78)
MINE_DOOR_LANE = (0.0, 44.0, 60.0, 7.0)      # (x, y0, y1, meia-largura) corredor livre da porta ate dentro

# ------------------------------------------------------------------ dungeon: portaria (NE, P3) + salas modulares (sob a ilha)
DUNGEON_HOUSE = (100.0, 72.0, 30.0, 26.0)    # (cx, cy, largura, profundidade) torre-portaria; porta na face SUL
# refino v2: a portaria vira BOCA DE CAVERNA escavada na rocha; a massa de rocha da caverna pode ocupar esta caixa
# (x0, y0, x1, y1) no P3, fundindo com os montes do terreno. Interior/porta/portal/rotas iguais.
# ov09b (2026-09-29, "cabe um GRUPO"): portaria 26 -> 30 de largura (tunel com vao livre >= 18,8; boca 22), mesma
# profundidade, mesmo eixo x = 100, mesma boca no patio (a rota do patio ate a boca nao muda).
DUNGEON_CAVE_MASS = (80.0, 74.0, 126.0, 116.0)
DUNGEON_DOOR_W = 22.0                        # vao LIVRE da boca (colisao das ombreiras); era 10 (desenho) / 16,8 (colisao)
DUNGEON_DOOR_H = 25.0                        # altura livre sob o arco da boca (colisao do dintel)
DUNGEON_PORTAL = (100.0, 80.0)               # portal espiral no fundo do interior (encara o sul)
# ov09b: salas MAIORES (R1 36 -> 48, R2/R3 44 -> 60) e pe-direito 22 -> 29,5: o piso desce de 6 para 2 (o teto fica
# abaixo de 32, onde o terreno comeca: a caixa DUN_KEEP_OUT desce junto); vaos de ligacao 12 x 12 -> 18 x 14.
DUN_Z = 2.0                                  # piso das salas da dungeon (dentro da regiao da area, acima de Y -12)
DUN_CEIL = DUN_Z + 29.5
# salas modulares em fila (x0, y0, x1, y1): R1 chegada, R2 e R3 as ARENAS da masmorra infinita (sala 1 = R2, depois
# R3, R2, R3...); paredes de 2 entre elas; eixo dos vaos e dos portais em y = DUN_LY
DUN_LY = 80.0
DUN_ROOMS = [("R1", (-84.0, 56.0, -36.0, 104.0)), ("R2", (-34.0, 50.0, 26.0, 110.0)), ("R3", (28.0, 50.0, 88.0, 110.0))]
DUN_LINK_W = 18.0
DUN_LINK_H = 14.0
DUN_WALL = 2.0
# caixa (x0, y0, z0, x1, y1, z1) onde NENHUMA geometria de fora da dungeon pode entrar. ov09b: justa nas paredes externas
# (o terreno descarta bloco da coroa do penhasco a menos da largura do bloco (ate 26) desta caixa: x0 >= -87 e
# x1 <= 95,5 mantem a coroa inteira; por isso a fila de salas corre de -86 a 90)
DUN_KEEP_OUT = (-86.5, 46.0, -2.0, 90.5, 114.0, 32.0)
DUN_SPAWN_CLEAR = 10.0                       # raio sem minerio em volta do spawn de cada arena (o grupo chega junto)

# ------------------------------------------------------------------ craft (P2, leste do meio)
CRAFT_C = (90.0, -60.0)
CRAFT_R = 16.0                        # raio externo do pavilhao redondo (interior ~13; porta a oeste)  [refino v2]
CRAFT_DOOR_DEG = 180.0                # porta voltada para o oeste (rua principal do P2)
CRAFT_DOOR_W = 8.0
CRAFT_DOOR_H = 11.0

# ------------------------------------------------------------------ saida (leste, P2) -> ponte -> portao Demon Slayer -> ancora
EXIT_START = (157.0, -38.0)           # ISLAND_EXIT_ShadowGarden (inicio da ponte, na borda do P2)
EXIT_DEG = 0.0                        # rumo da ponte (leste local)
EXIT_W = 18.0
EXIT_BRIDGE_LEN = 64.0
GATE_ISLET_R = 22.0
GATE_DS_OFF = 12.0                    # do inicio da ilhota ate o eixo do portao Demon Slayer
ANCHOR_OFF = 40.0                     # do inicio da ilhota ate ISLAND_NEXT_ANCHOR_DemonSlayer
NEXT_AREA_ID = 4                      # Monte Natagumo depois da troca 3<->4 (DECISOES.md D1)

# ------------------------------------------------------------------ vila (so ambientacao): 11 casas em 4 grupos
# (x, y, largura, profundidade, rumo_graus_da_frente, nivel) - NAO entraveis (sem porta falsa; janelas quentes)
HOUSE_LOTS = [
    # P1 oeste (rua da praca ao summon)
    (-50.0, -146.0, 14.0, 10.0, 90.0, P1), (-78.0, -142.0, 12.0, 10.0, 90.0, P1), (-68.0, -94.0, 12.0, 10.0, 270.0, P1),
    # P1 leste
    (50.0, -146.0, 14.0, 10.0, 90.0, P1), (82.0, -138.0, 12.0, 10.0, 120.0, P1), (72.0, -94.0, 12.0, 10.0, 270.0, P1),
    # P2 oeste (dos dois lados da rua do P2, y -45)
    (-62.0, -66.0, 14.0, 10.0, 90.0, P2), (-92.0, -66.0, 12.0, 10.0, 90.0, P2), (-58.0, -24.0, 12.0, 10.0, 270.0, P2),
    # P2 leste (entre a rua e o craft)
    (40.0, -64.0, 12.0, 10.0, 90.0, P2), (48.0, -24.0, 12.0, 10.0, 270.0, P2),
]
# ruas (pontos, largura) - calcamento; o piso e o do patamar
STREETS = [
    ([(-26.0, -118.0), (-60.0, -120.0), (-100.0, -118.0)], 9.0, P1),          # praca -> ponte do summon
    ([(26.0, -118.0), (64.0, -120.0), (110.0, -116.0)], 9.0, P1),             # praca -> mirante leste
    ([(0.0, -83.0), (0.0, -26.0)], 12.0, P2),                                 # eixo: escada P1P2 -> escada do portao
    ([(-110.0, -45.0), (-40.0, -44.0), (0.0, -45.0), (58.0, -45.0), (66.0, -56.0), (72.0, -60.0)], 9.0, P2),   # rua do P2 -> craft (pavilhao maior)
    ([(104.0, -36.0), (130.0, -38.0), (157.0, -38.0)], 12.0, P2),             # craft -> saida (pavilhao maior)
    ([(0.0, -3.0), (0.0, 40.0)], 14.0, P3),                                   # portao -> porta do castelo
    ([(46.0, 20.0), (80.0, 30.0), (100.0, 59.0)], 9.0, P3),                   # patio -> portaria da dungeon
    ([(112.0, -9.0), (110.0, 30.0), (100.0, 59.0)], 9.0, P3),                 # escada leste -> dungeon
]

# ------------------------------------------------------------------ contorno da ilha (topo do penhasco, anti-horario)
ISLAND_CTRL = [(-18.0, -230.0), (18.0, -230.0), (24.0, -206.0), (30.0, -176.0), (64.0, -168.0), (108.0, -160.0),
               (140.0, -134.0), (154.0, -100.0), (150.0, -76.0), (162.0, -58.0), (162.0, -20.0), (148.0, 0.0),
               (138.0, 40.0), (132.0, 100.0), (114.0, 146.0), (82.0, 180.0), (34.0, 198.0), (-34.0, 198.0),
               (-82.0, 182.0), (-108.0, 146.0), (-118.0, 90.0), (-114.0, 30.0), (-126.0, -40.0), (-124.0, -80.0),
               (-106.0, -104.0), (-103.0, -112.0), (-103.0, -124.0), (-104.0, -140.0), (-100.0, -156.0),
               (-66.0, -168.0), (-30.0, -176.0), (-24.0, -206.0)]

# ------------------------------------------------------------------ borda: penhascos, cachoeiras, pinheiros, ilhotas
# cachoeiras frias (azul): (x, y do labio na borda, z do labio, rumo da queda graus) - so visual + FX
WATERFALLS = [(-124.0, -52.0, P2 - 1.0, 180.0), (150.0, -112.0, P1 - 1.0, 0.0), (-52.0, 192.0, P3 - 1.0, 110.0),
              (-26.0, -190.0, DECK + 2.0, 200.0)]
# massas de rocha em coluna (basalto escuro) na borda - silhueta; nao-andaveis. (x, y, raio, topo, tipo)
CLIFF_SPIRES = [(-118.0, 120.0, 12.0, 96.0, "column"), (118.0, 124.0, 11.0, 90.0, "column"),
                (-40.0, 204.0, 14.0, 84.0, "column"), (60.0, 196.0, 10.0, 92.0, "column"),
                (-128.0, -20.0, 9.0, 70.0, "column"), (156.0, -140.0, 8.0, 58.0, "column"),
                (-112.0, -150.0, 8.0, 56.0, "column")]
# grupos de pinheiros escuros (x, y, raio do grupo, n) - entre casas e na borda (fora das ruas/escadas)
PINE_GROVES = [(-96.0, -150.0, 8.0, 3), (100.0, -150.0, 10.0, 4), (-104.0, -20.0, 10.0, 4), (136.0, -86.0, 8.0, 3),
               (-86.0, 120.0, 14.0, 5), (84.0, 150.0, 14.0, 5), (-20.0, -150.0, 5.0, 2), (126.0, 20.0, 6.0, 2),
               (-96.0, 40.0, 10.0, 4), (30.0, -150.0, 5.0, 2)]

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
    x0, y0, x1, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def plaza_poly():
    return circle_poly(PLAZA_C, PLAZA_R, 6.0)


def summon_poly():
    return circle_poly(SUMMON_C, SUMMON_R, 7.5)


# pisos andaveis: (nome, poligono, cota, prioridade) - o de MAIOR prioridade manda onde se sobrepoem
def floors():
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
    """cota do piso andavel em (x, y), ou None (fora de piso: penhasco/rocha/vazio). Pontes e escadas a parte."""
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
    """yaw do referencial do portao (il_gate_std): +Y local aponta para quem atravessa (sai da ilha)"""
    ux, uy = exit_dir()
    return math.atan2(uy, ux) - math.pi / 2


# ------------------------------------------------------------------ minerio do Mining Hall (pontos travados aqui)
ORE_KINDS = [("COMMON", 2.6), ("UNCOMMON", 3.0), ("EPIC", 3.4), ("SUPERLEGENDARY", 4.4)]
ORE_WALL_CLEAR = 5.0


def ore_blocked(x, y, clear):
    x0, y0, x1, y1 = MINE_RECT
    if x < x0 + clear or x > x1 - clear or y < y0 + clear or y > y1 - clear:
        return True
    lx, ly0, ly1, hw = MINE_DOOR_LANE
    if ly0 - 1.0 <= y <= ly1 and abs(x - lx) < hw + clear:
        return True
    # 04b: fora do anel de bloqueio "borda" do SpawnMinerio (sg_core.spawn_blocks: circulos de 5,5 a 3 das paredes)
    if x < HALL_X0 + 9.0 or x > HALL_X1 - 9.0 or y < HALL_Y0 + 9.0 or y > HALL_Y1 - 9.0:
        return True
    return False


def ore_points():
    """lista (kind, i, x, y, raio) - 2 super, 8 epicos, 16 incomuns, 28 comuns (mesma contagem das Ilhas 1 e 2),
    espacamento >= r1 + r2 + 3. Os super ficam no fundo do salao (o 'altar' da nave); o jogo completa com a grade."""
    import random
    rad = dict(ORE_KINDS)
    x0, y0, x1, y1 = MINE_RECT
    plan = [("SUPERLEGENDARY", 2), ("EPIC", 8), ("UNCOMMON", 16), ("COMMON", 28)]
    need = sum(n for _, n in plan)
    # grade hexagonal CENTRADA com leve ruido; setor 04b (salao maior): o passo e o MAIOR (>= 10,4 = 4,4 + 2,6 + 3)
    # que ainda da a contagem do plano -> os pontos se ESPALHAM pela area nova (nao se amontoam no fundo). Depois a
    # raridade por faixa de profundidade (porta = comum ... fundo = super, diante do arco do trono)

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
    step = 14.0
    cand = grid(step)
    while len(cand) < need and step > 10.4 + 1e-6:
        step = max(10.4, step - 0.1)
        cand = grid(step)
    cand.sort(key=lambda p: (-(p[1]) + abs(p[0]) * 0.35))         # fundo e centro primeiro
    pts = []
    i = 0
    for kind, n in plan:
        for k in range(n):
            if i >= len(cand):
                break
            x, y = cand[i]
            i += 1
            pts.append((kind, k + 1, x, y, rad[kind]))
    return pts


def dun_rect(name):
    return dict(DUN_ROOMS)[name]


def dun_spawn(name):
    """(x, y) do spawn de cada sala: R1 = DUNGEON_Spawn (chegada, 8 a leste do portal); R2/R3 = junto do vao OESTE
    (a sala e alcancada andando pela R1 na sala 1 e por teleporte curto nas seguintes)"""
    x0, y0, x1, y1 = dun_rect(name)
    return (x0 + (8.0 if name == "R1" else 6.5), DUN_LY)


def dun_links():
    """vaos de ligacao: (nome, x do meio da parede, y do eixo) - R1R2 fica sempre aberto; R2R3 e o que a masmorra
    infinita sela entre as salas (o selo e do jogo)"""
    out = []
    for (na, ra), (nb, rb) in zip(DUN_ROOMS, DUN_ROOMS[1:]):
        out.append(("%s%s" % (na, nb), (ra[2] + rb[0]) / 2.0, DUN_LY))
    return out


def dun_exit_r3():
    x0, y0, x1, y1 = dun_rect("R3")
    return (x1 - 4.0, DUN_LY)


# pontos de minerio de cada ARENA (mesma logica de aneis em volta do centro; densidade ~1 ponto / 210 studs2):
# centro (o grande), anel interno de 6 e anel externo de 12 posicoes sem as 2 do eixo dos vaos (spawn e vao/saida).
# O marcador diz a raridade do NIVEL 1 (piso); o DungeonService promove por nivel (AlquimiaConfig.Masmorra.NIVEL).
# Espacamento: pequeno-pequeno >= 3,4 + 3,4 + 3 (um ponto pequeno pode virar EPICO); centro e anel interno da R3
# >= 4,4 + 3,4 + 3 (podem virar LENDARIO).
DUN_ORE_PLAN = {
    "R2": ("EPIC", "UNCOMMON", ("COMMON", "UNCOMMON")),
    "R3": ("SUPERLEGENDARY", "EPIC", ("UNCOMMON", "COMMON")),
}
DUN_ORE_RINGS = (12.0, 23.0)
DUN_ORE_RADIUS = {"COMMON": 2.8, "UNCOMMON": 3.0, "EPIC": 3.4, "SUPERLEGENDARY": 4.4}


def dun_ore_points():
    """minerios FIXOS da dungeon (posFixa do AreaBuilder.novoMinerio), R2 e R3 (a R1 e a chegada, sem minerio):
    17 pontos por arena = centro + 6 (anel de 12) + 10 (anel de 23, sem 0 e 180 graus). (sala, tipo, i, x, y, raio)"""
    out = []
    k = 0
    for room in ("R2", "R3"):
        center, inner, outer = DUN_ORE_PLAN[room]
        x0, y0, x1, y1 = dun_rect(room)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k += 1
        out.append((room, center, k, cx, cy, DUN_ORE_RADIUS[center]))
        for i in range(6):
            a = math.radians(30.0 + 60.0 * i)
            k += 1
            out.append((room, inner, k, round(cx + DUN_ORE_RINGS[0] * math.cos(a), 2),
                        round(cy + DUN_ORE_RINGS[0] * math.sin(a), 2), DUN_ORE_RADIUS[inner]))
        j = 0
        for i in range(12):
            if i in (0, 6):
                continue
            a = math.radians(30.0 * i)
            kind = outer[j % 2]
            j += 1
            k += 1
            out.append((room, kind, k, round(cx + DUN_ORE_RINGS[1] * math.cos(a), 2),
                        round(cy + DUN_ORE_RINGS[1] * math.sin(a), 2), DUN_ORE_RADIUS[kind]))
    return out
