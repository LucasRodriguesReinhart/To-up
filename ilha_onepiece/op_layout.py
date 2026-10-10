# op_layout - planta TRAVADA da Ilha 5 (ONE PIECE / WANO, area 5 "Grand Line", tema mare). Onda M1 (plano/PLANO_OP.md).
# 1 BU = 1 stud, Z para cima. Cotas Z ABSOLUTAS = Y do Roblox.
# Referencial LOCAL: origem = centro da soleira do GRANDE TORII de entrada; +Y = eixo visual (ponte -> torii -> rua de
# chegada -> praca -> patio do castelo -> castelo/arvore); +X = direita de quem chega (summon, porto, enseada, caveira,
# saida para One Punch Man); -X = esquerda (bairro do canal, quarteirao oeste, terraco alto e pagode).
# Mundo (Blender do lobby): W5 = T(ancora_DS) . Rz(WORLD_YAW_DEG) . T(-WORLD_FROM_PREV_local); Roblox = (x, z, -y).
# A ancora e a SAIDA REAL da Demon Slayer (export 9cc4bef4, ilha_demonslayer/export/conexao_roblox.json).
import math

# ------------------------------------------------------------------ encaixe (ancora REAL da Ilha 4)
A_RBX = (-2054.391, 80.2, 1551.759)           # ISLAND_NEXT_ANCHOR_OnePiece (Roblox)
A_FWD = (-0.5736, 0.0, 0.8192)                # frente da ancora (Roblox)
A_W = 18.0
A_CLEAR_H = 22.0
GATE_OP_RBX = (-2044.067, 80.2, 1537.014)     # portao One Piece APROVADO (fica na DS, 18 antes da ancora): nao cobra de novo
ANCHOR_WORLD = (A_RBX[0], -A_RBX[2], A_RBX[1])   # Blender (x, y, z) do mundo do lobby
WORLD_YAW_DEG = 145.0                          # local +Y -> Roblox (-0,5736; 0; 0,8192) = frente da ancora (ponte reta)
BRIDGE_IN_LEN = 120.0                          # ponte de chegada (>= 100 pedido pelo plano da DS; borda a ~197 da DS)
PREV_X, PREV_Y = 0.0, -BRIDGE_IN_LEN           # WORLD_FROM_PREV local

# ------------------------------------------------------------------ cotas (Z absoluto = Y Roblox)
SEA = 36.0           # mar LOCAL de Wano (feito no CLIENTE so na area 5, como o mar de nuvens da DS); so visual
HARBOR = 42.2        # cais do porto (6,2 acima do mar)
HMID = 65.2          # rua alta do porto (patamar entre o cais e o terraco do summon)
DECK = 80.2          # tabuleiro na ancora (= T4 da Demon Slayer)
T0 = 84.2            # patio do grande torii (a ponte sobe 4 em 120: 1,9 graus, sem degrau)
T1 = 88.2            # rua de chegada, bairro do canal (SO), viela leste, terraco do SUMMON, promontorio da saida
P = 92.2             # PRACA DE MINERACAO + quarteirao oeste (W2) + quarteirao NE
CF = 98.2            # adro do castelo (bacia da cachoeira, portao vermelho)
W3 = 100.2           # terraco alto oeste (mansoes, pagode ao fundo)
CL = 117.2           # patamar da subida do castelo
CC = 136.2           # patio do castelo (honmaru): torre + varanda vermelha + base da arvore
SHIP = 46.2          # convés do navio (acessivel pela prancha)
SHOULDER = 37.0      # topo da quilha (o que nao e piso fica rente a agua)
BASE = 30.0          # fundo das massas dos patamares
FLOOR_BOT = 30.0     # fundo das caixas de colisao dos pisos (macico)
KEEL = 0.0           # fundo da quilha (Tier C; some sob o mar local na area 5; vista da DS: ilha flutuante)
RISE_MAX, TREAD_MIN = 0.8, 1.7
LEVELS = (HARBOR, SHIP, HMID, DECK, T0, T1, P, CF, W3, CL, CC)
DECK_W = 18.0
EYE = 5.5
CLEAR_H = 12.0       # nada colidivel na MiningZone ate piso + 12
NEM = 100.2          # V2-0: MIRANTE do santuario NE (patamar 1 dos socalcos; jardim alcancavel com colisao)
JUMP = 7.2           # V2-0: pulo padrao do Roblox (CharacterJumpHeight; conferir no Studio na V2-4)
GUARD_V2 = 8.5       # V2-0: guarda invisivel = pulo + 1,3 (PLANO_V2 secao 9 item 4)


# ------------------------------------------------------------------ transformacoes
def world_matrix():
    """matriz local -> mundo do lobby (mathutils), so XY (as cotas Z ja sao absolutas)"""
    from mathutils import Matrix, Vector
    ax, ay, _ = ANCHOR_WORLD
    return (Matrix.Translation(Vector((ax, ay, 0.0))) @ Matrix.Rotation(math.radians(WORLD_YAW_DEG), 4, "Z")
            @ Matrix.Translation(Vector((-PREV_X, -PREV_Y, 0.0))))


def to_world_xy(x, y):
    a = math.radians(WORLD_YAW_DEG)
    ax, ay, _ = ANCHOR_WORLD
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
    a = math.radians(WORLD_YAW_DEG)
    ax, ay, _ = ANCHOR_WORLD
    dx, dy = wx - ax, wy - ay
    return (dx * math.cos(a) + dy * math.sin(a) + PREV_X, -dx * math.sin(a) + dy * math.cos(a) + PREV_Y)


def local_of_roblox(rx, rz):
    return local_of_world(rx, -rz)


# ------------------------------------------------------------------ helpers de forma (iguais aos do ds_layout)
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
    return min(seg_dist(px, py, a[0], a[1], b[0], b[1])[0] for a, b in zip(pts, pts[1:]))


def poly_edge_dist(px, py, poly):
    n = len(poly)
    return min(seg_dist(px, py, poly[i][0], poly[i][1], poly[(i + 1) % n][0], poly[(i + 1) % n][1])[0] for i in range(n))


def ribbon(pts, hw):
    left, right = [], []
    n = len(pts)
    for i in range(n):
        x, y = pts[i][0], pts[i][1]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + list(reversed(right))


def circle_poly(c, r, step_deg=10.0):
    return [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
            for a in [i * step_deg for i in range(int(round(360.0 / step_deg)))]]


def rect_poly(r):
    x0, y0, x1, y1 = r[:4]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def area(P_):
    return abs(sum(P_[i][0] * P_[(i + 1) % len(P_)][1] - P_[(i + 1) % len(P_)][0] * P_[i][1]
                   for i in range(len(P_)))) / 2


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ SAIDA para One Punch Man (area 6) - definida antes
# do contorno porque o promontorio (e a borda dele) e construido em volta dela
EXIT_START = (206.0, 236.0)                    # ISLAND_EXIT_OnePiece: borda leste do terraco do summon (T1)
EXIT_DEG = 15.0                                # rumo local da ponte vermelha de saida (15 graus para fora da enseada)
EXIT_W = 18.0
EXIT_BRIDGE_LEN = 88.0                         # ponte vermelha sobre a enseada (88, a 42 do mar)
GATE_OPM_OFF = 22.0                            # portao One Punch Man a 22 do fim da ponte (no promontorio)
ANCHOR_OPM_OFF = 46.0                          # ancora One Punch Man na borda de fora do promontorio
HEAD_HW = 28.0                                 # meia largura do topo do promontorio
NEXT_AREA_ID = 6                               # One Punch Man ("serio", Cidade Z)
NEXT_KEY = "OnePunchMan"
NEXT_CLEAR_H = 22.0


def exit_dir():
    a = math.radians(EXIT_DEG)
    return (math.cos(a), math.sin(a))


def exit_point(d, v=0.0):
    """ponto a 'd' ao longo da ponte de saida (a partir de EXIT_START); v = afastamento lateral (+ = esquerda)"""
    ux, uy = exit_dir()
    return (EXIT_START[0] + ux * d - uy * v, EXIT_START[1] + uy * d + ux * v)


def gate_opm_pos():
    return exit_point(EXIT_BRIDGE_LEN + GATE_OPM_OFF)


def anchor_opm_pos():
    return exit_point(EXIT_BRIDGE_LEN + ANCHOR_OPM_OFF)


def gate_yaw():
    ux, uy = exit_dir()
    return math.atan2(uy, ux) - math.pi / 2


def headland_poly():
    """topo do promontorio da saida (T1): do fim da ponte ate a borda da ancora, meia largura HEAD_HW"""
    a, b = EXIT_BRIDGE_LEN, EXIT_BRIDGE_LEN + ANCHOR_OPM_OFF
    return [exit_point(a, -HEAD_HW), exit_point(b, -HEAD_HW), exit_point(b, HEAD_HW), exit_point(a, HEAD_HW)]


# ------------------------------------------------------------------ contorno (topo do penhasco), anti-horario
# Nao circular: pescoco estreito na entrada (o torii no "nariz" da falesia, como na concept), lobo SO do bairro do
# canal, flanco oeste reto-ondulado com o pagode, fundo alto do castelo, ENSEADA do porto a leste (aberta para SE)
# fechada pelo PROMONTORIO da caveira, que leva a saida. O esporao da espada sai do canto NE do fundo (so terreno).
_HL = headland_poly()
RIM_CTRL = [(0.0, -3.0), (30.0, -3.0), (46.0, 8.0), (70.0, 18.0), (100.0, 20.0), (128.0, 16.0), (162.0, 14.0),
            (196.0, 14.0), (216.0, 20.0), (224.0, 40.0), (222.5, 80.0), (222.0, 130.0), (222.0, 190.0), (222.0, 240.0),
            (224.0, 268.0), (236.0, 292.0), (258.0, 302.0), (280.0, 300.0),
            # promontorio: margem oeste (lado da enseada) -> caveira (ponta sul) -> borda da ancora -> raiz NE
            (_HL[3][0] - 2.0, _HL[3][1] + 4.0), (288.0, 262.0), (_HL[0][0] - 2.0, _HL[0][1] - 2.0), (297.0, 210.0),
            (292.0, 188.0), (294.0, 166.0), (306.0, 150.0), (326.0, 145.0), (344.0, 156.0), (353.0, 180.0),
            (352.0, 208.0), (_HL[1][0] + 1.5, _HL[1][1] - 6.0), (_HL[1][0] + 0.6, _HL[1][1]),
            (anchor_opm_pos()[0] + 0.3, anchor_opm_pos()[1]), (_HL[2][0] + 0.6, _HL[2][1]),
            (_HL[2][0] - 4.0, _HL[2][1] + 16.0), (306.0, 336.0), (282.0, 354.0), (254.0, 366.0), (228.0, 372.0),
            (212.0, 386.0), (204.0, 412.0), (198.0, 442.0), (186.0, 470.0), (164.0, 490.0), (126.0, 500.0),
            (76.0, 498.0), (24.0, 500.0), (-30.0, 496.0), (-72.0, 488.0), (-104.0, 474.0), (-128.0, 456.0),
            (-160.0, 448.0), (-196.0, 434.0), (-220.0, 414.0), (-230.0, 388.0), (-234.0, 356.0), (-233.0, 322.0),
            (-229.0, 290.0), (-228.0, 250.0), (-231.0, 210.0), (-229.0, 170.0), (-223.0, 138.0), (-212.0, 118.0),
            (-204.0, 100.0), (-194.0, 78.0), (-184.0, 58.0), (-170.0, 42.0), (-150.0, 34.0), (-120.0, 30.0),
            (-90.0, 28.0), (-66.0, 24.0), (-48.0, 16.0), (-36.0, 5.0), (-30.0, -3.0)]
ISLAND_RIM = smooth_closed(RIM_CTRL, 2)

# ------------------------------------------------------------------ patamares (pisos) - prioridade maior manda
ENTRY_COURT = [(-26.0, 0.0), (26.0, 0.0), (28.0, 16.0), (26.0, 34.0), (-26.0, 34.0), (-28.0, 16.0)]   # T0
T1_BASE = [(-168.0, 52.0), (-150.0, 42.0), (-110.0, 36.0), (-70.0, 34.0), (-30.0, 34.0), (30.0, 34.0), (44.0, 36.0),
           (70.0, 36.0), (100.0, 38.0), (120.0, 44.0), (122.0, 100.0), (130.0, 118.0), (148.0, 126.0),
           (148.0, 147.4), (204.0, 147.4), (206.0, 170.0), (206.0, 256.0), (200.0, 264.0), (116.0, 264.0),
           (116.0, 140.0), (112.0, 126.0), (96.0, 120.0), (64.0, 117.0), (-64.0, 117.0), (-110.0, 117.0),
           (-170.0, 117.0), (-170.0, 60.0)]                                                                 # T1
# V2-0 (PLANO_V2 3.4): o NE deixa de ser 'vilarejo solto + rocha NERocksW'; a praca NE vai ate x 236 (lojas, sando,
# haiden, honden, lago) e o canto NE vira o MIRANTE (100,2) atras do santuario. A montanha de tras = socalcos:
# mirante 100,2 (alcancavel) -> CastleFootE 110 (>= 8,5 acima do alcancavel) -> BackE 120.
P_BASE = [(-170.0, 118.0), (-110.0, 118.0), (-64.0, 118.0), (64.0, 118.0), (96.0, 124.0), (112.0, 140.0),
          (116.0, 170.0), (116.0, 262.0), (222.0, 262.0), (234.0, 286.0), (236.0, 316.0), (236.0, 338.0),
          (100.0, 338.0), (96.0, 314.0), (-96.0, 314.0), (-110.0, 300.0), (-170.0, 300.0)]                # P
NE_MIRANTE = [(172.0, 316.0), (236.0, 316.0), (236.0, 338.0), (172.0, 338.0)]                         # NEM (V2-0)
PLAZA = [(-64.0, 120.0), (64.0, 120.0), (92.0, 126.0), (110.0, 142.0), (116.0, 172.0), (116.0, 262.0),
         (108.0, 292.0), (86.0, 310.0), (40.0, 314.0), (-40.0, 314.0), (-86.0, 310.0), (-108.0, 292.0),
         (-116.0, 262.0), (-116.0, 172.0), (-110.0, 142.0), (-92.0, 126.0)]                              # praca (visual)
W2B = [(-214.0, 126.0), (-178.0, 122.0), (-178.0, 300.0), (-214.0, 296.0), (-222.0, 262.0), (-224.0, 214.0),
       (-224.0, 172.0), (-219.0, 140.0)]                                                                 # P (alem do canal)
W3_POLY = [(-212.0, 300.0), (-112.0, 300.0), (-100.0, 312.0), (-100.0, 360.0), (-104.0, 410.0), (-130.0, 430.0),
           (-170.0, 436.0), (-200.0, 420.0), (-216.0, 386.0), (-221.0, 334.0)]                          # W3
FORECOURT = [(-94.0, 314.0), (96.0, 314.0), (98.0, 339.0), (20.0, 339.0), (20.0, 335.0), (-20.0, 335.0), (-20.0, 338.0),
             (-64.0, 338.0), (-64.0, 346.0), (-94.0, 346.0)]                                                 # CF
CASTLE_LAND = [(-80.0, 380.0), (-64.0, 380.0), (-64.0, 396.0), (-80.0, 396.0)]                          # CL
COURT = [(-50.0, 358.0), (-24.0, 352.0), (24.0, 352.0), (50.0, 358.0), (66.0, 372.0), (74.0, 440.0), (62.0, 468.0),
         (20.0, 476.0), (-40.0, 474.0), (-90.0, 470.0), (-90.0, 436.0), (-64.0, 436.0), (-64.0, 376.0)]  # proa na frente               # CC
HARBOR_POLY = [(120.0, 30.0), (150.0, 26.0), (190.0, 24.0), (214.0, 28.0), (222.0, 40.0), (246.0, 40.0),
               (246.0, 76.0), (222.0, 76.0), (222.0, 110.0), (234.0, 110.0), (234.0, 200.0), (222.0, 200.0),
               (222.0, 262.0), (206.0, 262.0), (206.0, 100.0), (124.0, 100.0), (122.0, 60.0)]          # HARBOR
HARBOR_MID = [(126.0, 100.0), (211.0, 100.0), (211.0, 150.0), (148.0, 150.0), (148.0, 126.0), (130.0, 118.0)]  # HMID
SHIP_C, SHIP_LEN, SHIP_BEAM = (248.0, 152.0), 80.0, 16.0     # navio (proa para o SUL = saida da enseada)
SHIP_DECK = [(242.0, 120.0), (248.0, 112.0), (254.0, 120.0), (255.0, 186.0), (241.0, 186.0)]          # SHIP (convés)
# terreno que NAO e piso (so visual): ombros e rochas que fecham a borda (nada de prateleira rente a agua)
ROCKS = [
    ("EntryL", [(-30.0, -1.0), (-26.0, 0.0), (-28.0, 16.0), (-26.0, 34.0), (-30.0, 34.0), (-48.0, 20.0), (-40.0, 6.0)], 90.0),
    ("EntryR", [(30.0, -1.0), (42.0, 6.0), (60.0, 18.0), (44.0, 34.0), (26.0, 34.0), (28.0, 16.0), (26.0, 0.0)], 90.0),
    ("FrontR", [(44.0, 34.0), (60.0, 18.0), (100.0, 22.0), (126.0, 18.0), (122.0, 44.0), (100.0, 37.0), (70.0, 35.0)], 86.0),
    ("SWBank", [(-200.0, 100.0), (-192.0, 78.0), (-182.0, 60.0), (-178.0, 60.0), (-178.0, 118.0), (-208.0, 118.0)], 90.0),
    ("CastleFootW", [(-64.0, 338.0), (-20.0, 338.0), (-20.0, 350.0), (-64.0, 350.0)], 101.0),
    ("CastleFootE", [(18.0, 344.5), (254.0, 344.5), (254.0, 364.0), (228.0, 370.0), (212.0, 382.0), (186.0, 352.0),
                     (72.0, 372.0), (62.0, 352.0), (18.0, 350.0)], 110.0),     # V2-0: socalco 2 (era 104: 5,8 sobre o adro)
    ("NESocalco", [(234.0, 286.0), (241.0, 298.0), (245.4, 304.0), (245.4, 339.4), (236.0, 339.4), (236.0, 316.0)], 110.0),  # V2-0 (era NERocksW)
    ("NERocksE", [(255.0, 301.0), (262.0, 306.0), (282.0, 300.0), (290.0, 312.0), (300.0, 334.0), (280.0, 350.0),
                  (256.0, 364.0), (255.0, 349.0)], 104.0),
    ("BackE", [(72.0, 372.0), (186.0, 352.0), (210.0, 380.0), (200.0, 440.0), (180.0, 470.0), (130.0, 494.0),
               (74.0, 490.0), (62.0, 468.0), (74.0, 440.0)], 120.0),
    ("BackN", [(-94.0, 471.0), (-40.0, 474.0), (20.0, 476.0), (62.0, 468.0), (74.0, 490.0), (20.0, 494.0),
               (-30.0, 490.0), (-70.0, 482.0), (-100.0, 474.0)], 150.0),
    ("ButtressL", [(-64.0, 350.0), (-46.0, 342.0), (-30.0, 346.0), (-24.0, 352.0), (-50.0, 358.0), (-64.0, 366.0)], 124.0),
    ("ButtressR", [(24.0, 352.0), (32.0, 345.0), (52.0, 344.0), (68.0, 352.0), (66.0, 372.0), (50.0, 358.0)], 128.0),
    ("BackW", [(-100.0, 360.0), (-94.0, 346.0), (-79.0, 346.0), (-80.0, 380.0), (-80.0, 396.0), (-79.0, 436.0),
               (-92.0, 436.0), (-94.0, 469.0), (-106.0, 471.0), (-126.0, 452.0), (-130.0, 430.0), (-104.0, 410.0)], 118.0),
]
# V2-0 (PLANO_V2 secao 9 item 3): TODA massa de ROCKS ganha colisao macica ate o topo visual (op_col.rock_cols). A flag
# diz o papel do topo: 'walk' = topo alcancavel (vira piso: entra na logica das guardas, guarda de 8,5 no labio de
# fora); 'tall' = topo >= 8,5 acima de tudo o que e alcancavel (a guarda fica na borda do piso vizinho).
# (lista separada para nao mudar a forma (nome, poligono, cota) que op_terrain/op_veg/op_map desempacotam)
ROCK_COL = {"EntryL": "walk", "EntryR": "walk", "FrontR": "walk", "SWBank": "walk", "CastleFootW": "walk",
            "CastleFootE": "tall", "NESocalco": "tall", "NERocksE": "tall", "BackE": "tall", "BackN": "tall",
            "ButtressL": "tall", "ButtressR": "tall", "BackW": "walk"}   # BackW: 0,8 acima do patamar CL
HEADLAND = _HL                                  # T1 (promontorio da saida)
SKULL_C, SKULL_FACE_DEG = (322.0, 190.0), 195.0  # caveira com chifres (formacao na ponta sul do promontorio)
SKULL_ROCK = [(296.0, 228.0), (294.0, 168.0), (306.0, 152.0), (326.0, 147.0), (344.0, 158.0), (351.0, 182.0),
              (350.0, 208.0), (342.0, 230.0), (318.0, 234.0)]
SWORD_SPUR = [(176.0, 488.0), (200.0, 462.0), (238.0, 506.0), (286.0, 560.0), (312.0, 590.0), (306.0, 616.0),
              (282.0, 622.0), (262.0, 590.0), (226.0, 546.0), (194.0, 512.0)]
SWORD_POS, SWORD_ROCK_Z = (292.0, 600.0), 100.0  # espada monumental cravada no pinaculo do esporao (silhueta distante)
WEST_SPIRE = (-246.0, 372.0, 20.0, 130.0)       # pinaculo oeste (x, y, raio, topo) - V2-0 (U13): SEM pagode, agulha de
                                                # rocha com pinheiro no topo, mais baixa (158 -> 130)


def floors():
    """pisos andaveis: (nome, poligono, cota, prioridade) - o de MAIOR prioridade manda"""
    return [
        ("Court", COURT, CC, 70),
        ("CastleLanding", CASTLE_LAND, CL, 68),
        ("W3", W3_POLY, W3, 66),
        ("Forecourt", FORECOURT, CF, 64),
        ("NEMirante", NE_MIRANTE, NEM, 52),
        ("Plaza", P_BASE, P, 50),
        ("W2b", W2B, P, 49),
        ("ExitLand", HEADLAND, T1, 46),
        ("T1", T1_BASE, T1, 40),
        ("Entry", ENTRY_COURT, T0, 30),
        ("HarborMid", HARBOR_MID, HMID, 24),
        ("Harbor", HARBOR_POLY, HARBOR, 20),
        ("ShipDeck", SHIP_DECK, SHIP, 18),
    ]


_FLOORS = sorted(floors(), key=lambda f: -f[3])


def _zval(z, x, y):
    return z(x, y) if callable(z) else z


def in_hole(nm, x, y):
    return any(r[0] <= x <= r[2] and r[1] <= y <= r[3] for r in FLOOR_HOLES.get(nm, ()))


def zone_of(x, y):
    for nm, poly, z, pr in _FLOORS:
        if point_in_poly(x, y, poly):
            return None if in_hole(nm, x, y) else _zval(z, x, y)
    return None


def floor_name(x, y):
    for nm, poly, z, pr in _FLOORS:
        if point_in_poly(x, y, poly):
            return nm
    return None


def floor_poly(name):
    for nm, poly, z, pr in _FLOORS:
        if nm == name:
            return poly
    raise KeyError(name)


# ------------------------------------------------------------------ escadas da planta
# (nome, pe (x, y, z), rumo graus, largura, degraus, piso, guardas). Espelho = desnivel / n (<= 0,8).
STAIRS = [
    ("Chegada", (0.0, 34.0, T0), 90.0, 16.0, 6, 1.8, True),           # patio do torii -> rua de chegada
    ("Praca", (0.0, 109.0, T1), 90.0, 28.0, 6, 1.8, True),            # rua de chegada -> PRACA (escadaria larga)
    ("Summon", (127.0, 216.0, T1), 180.0, 14.0, 6, 1.8, True),        # terraco do summon -> praca (lado leste)
    ("Sudoeste", (-140.0, 109.0, T1), 90.0, 10.0, 6, 1.8, True),      # bairro do canal -> quarteirao oeste
    ("OesteAlta", (-110.0, 288.0, P), 90.0, 12.0, 11, 1.8, True),     # quarteirao oeste -> terraco alto oeste
    ("Adro", (0.0, 312.6, P), 90.0, 30.0, 8, 1.8, True),              # praca -> adro do castelo (sob o portao)
    ("CasteloA", (-71.0, 336.0, CF), 90.0, 12.0, 25, 1.8, True),      # adro -> patamar (flanco oeste da rocha)
    ("CasteloB", (-71.0, 394.0, CL), 90.0, 12.0, 25, 1.8, True),      # patamar -> patio do castelo
    ("PortoA", (200.8, 140.0, HMID), 180.0, 12.0, 30, 1.8, True),     # rua alta do porto -> mirante do porto (T1)
    ("PortoB", (160.0, 46.0, HARBOR), 90.0, 12.0, 30, 1.8, True),     # cais -> rua alta do porto
    ("Mirante", (180.0, 304.0, P), 90.0, 10.0, 10, 1.8, True),        # V2-0: sando NE -> mirante do santuario (100,2)
]
STAIR_TOP_Z = {"Chegada": T1, "Praca": P, "Summon": P, "Sudoeste": P, "OesteAlta": W3, "Adro": CF, "CasteloA": CL,
               "CasteloB": CC, "PortoA": T1, "PortoB": HMID, "Mirante": NEM}


def stair_frame(name):
    for nm, foot, deg, w, n, tread, g in STAIRS:
        if nm == name:
            return foot, deg, w, n, tread, g
    raise KeyError(name)


def stair_top(name):
    foot, deg, w, n, tread, g = stair_frame(name)
    a = math.radians(deg)
    return (foot[0] + math.cos(a) * tread * n, foot[1] + math.sin(a) * tread * n, STAIR_TOP_Z[name])


def stair_rise(name):
    foot, deg, w, n, tread, g = stair_frame(name)
    return (STAIR_TOP_Z[name] - foot[2]) / n


def _clip_half(poly, a, b, c):
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def clip_rect(poly, rect):
    x0, y0, x1, y1 = rect
    for a, b, c in ((1, 0, -x0), (-1, 0, x1), (0, 1, -y0), (0, -1, y1)):
        poly = _clip_half(poly, a, b, c)
        if len(poly) < 3:
            return []
    return poly


def subtract_rect(poly, rect):
    x0, y0, x1, y1 = rect
    out = []
    for hs in (((-1, 0, x0),), ((1, 0, -x1),), ((1, 0, -x0), (-1, 0, x1), (0, -1, y0)),
               ((1, 0, -x0), (-1, 0, x1), (0, 1, -y1))):
        p = list(poly)
        for a, b, c in hs:
            p = _clip_half(p, a, b, c)
            if len(p) < 3:
                break
        if len(p) >= 3 and area(p) > 0.5:
            out.append(p)
    return out


def stair_notches():
    """entalhe de cada escada no patamar de CIMA (como na DS): (escada, piso de cima, retangulo, cota pe, cota topo)"""
    out = []
    for nm, foot, deg, w, n, tread, g in STAIRS:
        a = math.radians(deg)
        ux, uy = round(math.cos(a)), round(math.sin(a))
        t = stair_top(nm)
        up = floor_name(t[0] + ux * 0.6, t[1] + uy * 0.6)
        hw = w / 2 + 1.25
        bx, by = foot[0] - ux * tread / 2, foot[1] - uy * tread / 2
        if ux:
            rect = (min(bx, t[0]), foot[1] - hw, max(bx, t[0]), foot[1] + hw)
        else:
            rect = (foot[0] - hw, min(by, t[1]), foot[0] + hw, max(by, t[1]))
        out.append((nm, up, rect, foot[2], t[2]))
    return out


def floor_pieces(name):
    pieces = [floor_poly(name)]
    for rect in FLOOR_HOLES.get(name, ()):             # V2-0: lago/rego do NE
        nxt = []
        for p in pieces:
            nxt += subtract_rect(p, rect)
        pieces = nxt
    for nm, up, rect, zf, zt in stair_notches():
        if up != name:
            continue
        nxt = []
        for p in pieces:
            nxt += subtract_rect(p, rect)
        pieces = nxt
    return pieces


# ------------------------------------------------------------------ entrada
TORII_IN = (0.0, 10.0)                         # GRANDE torii vermelho (vao livre 18 x 22)
TORII_W, TORII_H = 18.0, 22.0
SPAWN = (0.0, 24.0)                            # WORLD_ENTRY_OnePiece


# V2-0 (PLANO_V2 secao 8, U6): as 2 pontes do canal oeste viram ARCO que vence o vao entre as margens: encontros de
# pedra FORA do vao, 2 degraus de 0,7 por lado, tabuleiro a P + 1,4 (acima da capa de 0,9 do canal); colisao em 2 rampas
# + topo (op_col.arch_bridge). Canal rebaixado embaixo: agua 89,6, leito colidivel 88,6.
BRIDGE_ARCH = {"CanalS": 1.4, "CanalN": 1.4}      # subida no meio (2 degraus de 0,7)
BRIDGE_ARCH_STEP = (0.7, 1.4)                     # (espelho, pisada) dos degraus de cada ponta
BRIDGE_ARCH_X = (-165.4, -182.6)                  # pe leste (praca) -> pe oeste (W2b): 17,2 = 2 x 2,8 de degraus + 11,6
                                                  # de tabuleiro (vao 8 + encontros de 1,8 nas 2 margens)


def bridge_list():
    """(nome, inicio (x, y, z), fim (x, y, z), largura): ponte de chegada (rampa 80,2 -> 84,2), ponte vermelha de
    saida (T1), 2 pontes vermelhas do canal oeste, prancha do navio"""
    e0 = exit_point(0.0)
    e1 = exit_point(EXIT_BRIDGE_LEN)
    return [("Arrival", (PREV_X, PREV_Y, DECK), (0.0, 0.0, T0), DECK_W),
            ("ExitBridge", (e0[0], e0[1], T1), (e1[0], e1[1], T1), EXIT_W),
            ("CanalS", (BRIDGE_ARCH_X[0], 182.0, P), (BRIDGE_ARCH_X[1], 182.0, P), 10.0),
            ("CanalN", (BRIDGE_ARCH_X[0], 252.0, P), (BRIDGE_ARCH_X[1], 252.0, P), 10.0),
            ("Gangway", (230.0, 152.0, HARBOR), (241.6, 152.0, SHIP), 5.0)]


# ------------------------------------------------------------------ PRACA / mineracao
MINE_RECT = (-76.0, 156.0, 76.0, 276.0)        # MiningZone 152 x 120 (>= 112 x 150 da DS girado; 18.240 studs2)
MINE_C = ((MINE_RECT[0] + MINE_RECT[2]) / 2, (MINE_RECT[1] + MINE_RECT[3]) / 2)
ORE_PLAN = [("SUPERLEGENDARY", 2), ("EPIC", 10), ("UNCOMMON", 22), ("COMMON", 38)]   # 72 marcadores (como a DS)
ORE_RADIUS = {"COMMON": 2.6, "UNCOMMON": 3.0, "EPIC": 3.4, "SUPERLEGENDARY": 4.4}
EMBLEM_C, EMBLEM_R = (0.0, 216.0), 13.0        # emblema de chao RENTE (sem colisao, sem relevo)
BANNERS = []                                   # V2-0 (U16): os 4 estandartes dos cantos da praca SAIRAM


def ore_points():
    """72 pontos (kind, i, x, y, raio): grade hexagonal no MAIOR passo que da a contagem, cantos recortados por elipse,
    raridade pela profundidade (perto da chegada = comum ... perto do adro do castelo = super)"""
    import random
    x0, y0, x1, y1 = MINE_RECT
    cx, cy = MINE_C
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    need = sum(n for _, n in ORE_PLAN)

    def ok(x, y):
        return ((x - cx) / (hx - 5.0)) ** 2 + ((y - cy) / (hy - 5.0)) ** 2 <= 1.08 and x0 + 5 <= x <= x1 - 5 \
            and y0 + 5 <= y <= y1 - 5 and math.hypot(x - EMBLEM_C[0], y - EMBLEM_C[1]) > 0.0

    def grid(step):
        rng = random.Random(5505)
        out, row = [], 0
        y = y0 + 5.0
        while y <= y1 - 5.0:
            sh = step / 2 if row % 2 else 0.0
            x = x0 + 5.0 + sh
            while x <= x1 - 5.0:
                jx, jy = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8)
                if ok(x + jx, y + jy):
                    out.append((x + jx, y + jy))
                x += step
            y += step * 0.866
            row += 1
        return out
    step = 18.0
    cand = grid(step)
    while len(cand) < need and step > 10.4:
        step -= 0.1
        cand = grid(step)
    cand.sort(key=lambda p: (-p[1] + abs(p[0] - cx) * 0.35))
    pts, i = [], 0
    for kind, n in ORE_PLAN:
        for k in range(n):
            pts.append((kind, k + 1, round(cand[i][0], 2), round(cand[i][1], 2), ORE_RADIUS[kind]))
            i += 1
    return pts


# ------------------------------------------------------------------ CASTELO (heroi) + ARVORE ARQUEADA
KEEP_C = (0.0, 404.0)                          # torre de menagem (tenshu), frente para -Y (praca)
# andares (meia largura x, meia profundidade y, z0 acima do CC, altura da parede, beiral do telhado-saia)
KEEP_TIERS = [(28.0, 23.0, 0.0, 21.0, 5.4), (22.0, 18.0, 25.0, 13.0, 4.6), (16.5, 13.5, 42.0, 12.0, 4.0),
              (11.5, 10.0, 58.0, 11.0, 3.5)]          # torre GRANDE (concept: castelo = 1/3 da altura do quadro)
KEEP_TOP_Z = CC + 69.0 + 10.0                   # cumeeira do ultimo telhado (~193) + shachihoko
KEEP_DOOR = (0.0, 381.0, 6.0, 9.0)             # porta ABERTA do terreo (x, y da face, largura, altura) -> salao real
KEEP_HALL = (-25.0, 383.0, 25.0, 425.0, 12.0)  # salao interno acessivel (x0, y0, x1, y1, pe-direito)
CASTLE_GATE = (0.0, 324.5, 36.0)               # portao vermelho do adro, sobre o topo da escada Adro (x, y, vao)
COURT_GATE = (-71.0, 442.0, 16.0)              # portao do patio no topo da CasteloB
TURRET = (58.0, 364.0, 12.0)                   # yagura (torreao) no canto SE do patio
# tronco: (x, y, z, raio) - nasce de base com raizes no fundo-leste do patio, sobe a direita da torre, curva por cima
# e termina a esquerda; afina progressivamente (nao e tubo uniforme nem aro perfeito)
_TREE_TRUNK0 = [(54.0, 446.0, CC - 2.0, 12.0), (58.0, 443.0, CC + 10.0, 9.4), (64.0, 439.0, CC + 26.0, 7.8),
              (68.0, 434.0, CC + 44.0, 6.8), (67.0, 429.0, CC + 62.0, 6.1), (60.0, 425.0, CC + 80.0, 5.5),
              (45.0, 421.0, CC + 96.0, 4.9), (24.0, 419.0, CC + 106.0, 4.4), (0.0, 418.0, CC + 110.0, 4.0),
              (-22.0, 419.0, CC + 106.0, 3.5), (-40.0, 421.0, CC + 96.0, 3.0), (-52.0, 423.0, CC + 84.0, 2.5),
              (-57.0, 424.0, CC + 74.0, 2.0)]
_TREE_BRANCHES0 = [  # (indice do ponto de saida no tronco, pontos (x, y, z, r))
    (4, [(70.0, 428.0, CC + 66.0, 3.2), (84.0, 430.0, CC + 72.0, 2.4), (96.0, 432.0, CC + 74.0, 1.6)]),
    (7, [(20.0, 416.0, CC + 110.0, 2.6), (10.0, 410.0, CC + 120.0, 1.8), (2.0, 404.0, CC + 124.0, 1.2)]),
    (9, [(-26.0, 420.0, CC + 104.0, 2.4), (-44.0, 428.0, CC + 110.0, 1.7), (-60.0, 432.0, CC + 112.0, 1.2)]),
]
TREE_ROOTS = [(36.0, 452.0, CC, 3.4), (40.0, 432.0, CC, 3.0), (72.0, 456.0, CC - 6.0, 3.2), (76.0, 438.0, CC - 10.0, 3.0),
              (58.0, 466.0, CC - 3.0, 2.8)]
# copa florida em massas principais e secundarias (centro, raio, achatamento) - abertura no meio para ceu/castelo
_TREE_CANOPY0 = [((-30.0, 424.0, CC + 118.0), 23.0, 0.55), ((-58.0, 430.0, CC + 100.0), 15.0, 0.62),
               ((-70.0, 434.0, CC + 114.0), 10.0, 0.6), ((-6.0, 414.0, CC + 128.0), 14.0, 0.52),
               ((22.0, 420.0, CC + 120.0), 13.0, 0.55), ((48.0, 426.0, CC + 104.0), 10.0, 0.6),
               ((86.0, 430.0, CC + 78.0), 14.0, 0.55), ((102.0, 434.0, CC + 72.0), 9.0, 0.6),
               ((74.0, 438.0, CC + 44.0), 9.0, 0.6), ((-44.0, 416.0, CC + 126.0), 11.0, 0.55)]
TREE_S = 1.25                                  # escala do arco em torno da base (casa com a torre grande)
_TB = (54.0, 446.0)


def _ts(x, y, z):
    return (_TB[0] + (x - _TB[0]) * TREE_S, _TB[1] + (y - _TB[1]) * 0.6 + (y - _TB[1]) * 0.4 * TREE_S, CC + (z - CC) * TREE_S)


TREE_TRUNK = [_ts(x, y, z) + (r * (1.0 if i == 0 else 1.12),) for i, (x, y, z, r) in enumerate(_TREE_TRUNK0)]
TREE_BRANCHES = [(i, [_ts(x, y, z) + (r * 1.12,) for x, y, z, r in pts]) for i, pts in _TREE_BRANCHES0]
TREE_CANOPY = [(_ts(*c), r * 1.15, f) for c, r, f in _TREE_CANOPY0]
TREE_TOP_Z = CC + 165.0

# ------------------------------------------------------------------ AGUA (uma historia por bacia; a agua e do Roblox)
# 1) Castelo: nascente na rocha sob o patio -> CACHOEIRA DO CASTELO (30) -> bacia do adro -> canal leste -> NE ->
#    QUEDA LESTE na enseada (o porto ve a agua chegando). 2) Oeste: bica no arrimo do terraco alto -> canal oeste pelo
#    quarteirao (2 pontes vermelhas) -> degrau -> RODA D'AGUA -> QUEDA OESTE para o mar (falesia SO).
CASTLE_FALL = (0.0, 351.0, CC - 4.0, CF - 0.6)    # (x, y labio, z labio, z base) - nasce sob a varanda vermelha
BASIN = [(-18.0, 335.0), (18.0, 335.0), (20.0, 343.0), (14.0, 350.0), (-14.0, 350.0), (-20.0, 343.0)]
BASIN_Z = CF - 0.6
# V2-0 (PLANO_V2 secao 8/9, U6/U8): canais REBAIXADOS - agua 2,6 abaixo da margem (89,6 na praca, 85,6 no bairro),
# LEITO COLIDIVEL 1,0 abaixo da agua (op_col.water_beds), capa de 0,9 acima do piso SO fora das pontes (com colisao);
# a bacia do adro fica na cota (97,6) e ganha leito colidivel a 96,6. Sem buraco ate o vazio: guarda de 8,5 so na boca
# das quedas (FALL_E/FALL_W).
CANAL_DROP = 2.6                                  # agua abaixo da margem
CANAL_BED = 1.0                                   # leito colidivel abaixo da agua
CANAL_COPE_H, CANAL_COPE_W = 0.9, 1.0             # capa (mureta) das margens, fora das pontes
CANAL_E = [(18.0, 342.0, CF - 0.6), (92.0, 342.0, CF - 0.6), (100.0, 342.0, P - CANAL_DROP),
           (188.0, 342.5, P - CANAL_DROP), (248.5, 342.5, P - CANAL_DROP), (248.5, 304.0, P - CANAL_DROP)]
CANAL_E_W = 6.0
FALL_E = (248.5, 301.0, P - CANAL_DROP, SEA)      # queda leste: canal (garganta na rocha NE) -> enseada
CANAL_W = [(-174.0, 299.0, P - CANAL_DROP), (-174.0, 250.0, P - CANAL_DROP), (-174.0, 182.0, P - CANAL_DROP),
           (-174.0, 120.0, P - CANAL_DROP), (-174.0, 114.0, T1 - CANAL_DROP), (-174.0, 92.0, T1 - CANAL_DROP),
           (-174.0, 58.0, T1 - CANAL_DROP)]
CANAL_W_X = (-178.0, -170.0)
SPRING_W = (-174.0, 300.0, W3 - 3.0)              # bica no arrimo do terraco alto
WHEEL = (-174.0, 90.0, 13.0, 4.0)                 # roda d'agua no canal (x, y, diametro, largura); eixo leste-oeste
WHEEL_AXLE_Z = T1 + 1.9                           # V2-0: desce com a agua (pa mergulha ~2,0)
FALL_W = (-174.0, 54.0, T1 - CANAL_DROP, SEA)     # queda oeste: canal -> mar
WEIRS = [("Weir_E", (96.0, 342.0, CF - 0.6, P - CANAL_DROP)), ("Weir_W", (-174.0, 117.0, P - CANAL_DROP, T1 - CANAL_DROP))]
NE_POND = ((141.0, 317.0, 155.0, 327.0), P - 0.8)  # V2-0: lago do santuario NE (retangulo, agua); leito a -1,0
NE_POND_LINK = (145.7, 326.5, 150.3, 338.6)        # rego do lago ate o canal leste (4,6 de largura: nao le como fresta)
FLOOR_HOLES = {"Plaza": [NE_POND[0], NE_POND_LINK]}  # buracos retangulares nos pisos (visual e colisao)
SEA_C, SEA_SIZE = (60.0, 260.0), 2200.0           # mar local (quadrado no cliente, so na area 5)

# ------------------------------------------------------------------ SUMMON (terraco lateral, transicao para o porto)
SUMMON_TOWER = (170.0, 214.0)                     # torre AMS aprovada, frente para -X (oeste: praca)
SUMMON_FACE_DEG = 180.0
SUMMON_C, SUMMON_R = (166.0, 214.0), 26.0
SUMMON_INTERACT_D, SUMMON_PLAYER_D = 7.0, 16.0

# ------------------------------------------------------------------ CAPITAL V2 (PLANO_V2 secao 3): QUADRAS, nao casas
# A V1 (BUILDINGS: ~40 casas soltas) foi reprovada (U1/U2/U11). A cidade V2 e feita de FILEIRAS de lotes GEMINADOS
# (parede-meia, sem fresta) que formam quadras com fachada continua; cor do telhado por quadra (ref_03).
# ROWS: (quadra, fileira, a (x, y), b (x, y), lado da rua, cota, fundo D, telhado, lotes)
#   a -> b = linha da FACHADA (frente dos lotes); lado +1 = a rua fica a ESQUERDA de a -> b, -1 = a direita;
#   lotes em ordem de a para b: (largura da frente, tipo, pisos, flags)
#   tipos (os do op_kit2): loja, sobrado, esquina, kura, chaya, fundo + santuario, honden, mansao, armazem, moinho,
#   portal (passagem coberta: vao livre no terreo, telhado continuo por cima)
#   flags: h = hisashi continuo no terreo; t = tsumairi (empena para a rua, cumeeira perpendicular); e = esquina-marco;
#          i = INTERIOR vivo (PLANO_V2 3.5: no maximo 5); o = frente aberta (alpendre/varanda com piso, santuario);
#          c<Mat> = troca a cor do telhado do lote (ex.: "cRoof_OP_RedV2")
# O ENVELOPE (beiral/cumeeira) e o contrato do lote: o kit V2 pode variar detalhe, mas a superficie de cima do telhado
# tem de ficar a <= 0,5 deste envelope - ou o op_capital troca a colisao pelo op_col.roof_col() com o info do kit.
ROOF_PITCH = 0.58          # caimento do telhado (normal 0,86 > 0,7: andavel -> colide quando alcancavel)
ROOF_OV = 1.6              # beiral alem da parede
HISASHI = (2.4, 7.9)       # hisashi: profundidade, cota da borda baixa acima do piso (> 7,2: nao se alcanca da rua)
EAVE_H = {("fundo", 1): 8.8, ("loja", 2): 16.8, ("sobrado", 3): 22.8, ("esquina", 3): 22.8, ("kura", 2): 13.3,
          ("chaya", 1): 10.0, ("santuario", 1): 11.0, ("honden", 1): 9.0, ("mansao", 2): 15.0, ("armazem", 2): 15.0,
          ("moinho", 1): 10.0, ("portal", 1): 9.6, ("loja", 1): 9.6}
R_COB, R_TEAL, R_VIO, R_RED, R_GRN = "Roof_OP_Cobalt", "Roof_OP_Teal", "Roof_OP_Violet", "Roof_OP_RedV2", "Roof_OP_Green"
ROWS = [
    # ---- AVENIDA DE CHEGADA (T1, leito x -9..9, calcadas ate a fachada em x +-15) - quadras AvO / AvL
    ("AvO", "F1", (-15.0, 40.0), (-15.0, 83.0), -1, T1, 20.0, R_COB,
     [(11.0, "loja", 2, "h"), (9.0, "loja", 2, ""), (12.0, "sobrado", 3, "t"), (11.0, "loja", 2, "hi")]),
    ("AvO", "PV", (-15.0, 83.0), (-15.0, 89.0), -1, T1, 20.0, R_COB, [(6.0, "portal", 1, "")]),   # viela do canal:
    ("AvO", "PV2", (-62.0, 83.0), (-62.0, 89.0), 1, T1, 20.0, R_COB, [(6.0, "portal", 1, "")]),   # portal nas 2 fileiras
    ("AvO", "F2", (-15.0, 89.0), (-15.0, 105.0), -1, T1, 20.0, R_COB, [(16.0, "esquina", 3, "e")]),
    ("AvO", "B1", (-62.0, 40.0), (-62.0, 83.0), 1, T1, 20.0, R_COB,
     [(10.0, "fundo", 1, ""), (13.0, "loja", 2, ""), (10.0, "fundo", 1, ""), (10.0, "loja", 2, "h")]),
    ("AvO", "B2", (-62.0, 89.0), (-62.0, 105.0), 1, T1, 20.0, R_COB, [(16.0, "loja", 2, "t")]),
    ("AvL", "F1", (15.0, 40.0), (15.0, 101.0), 1, T1, 20.0, R_COB,      # termina em y 101: folga ate o pe da escada
     [(11.0, "loja", 2, "h"), (9.0, "loja", 2, ""), (12.0, "sobrado", 3, "t"), (9.0, "loja", 2, "h"),  # Praca (viela leste)
      (10.0, "loja", 2, "i"), (10.0, "esquina", 3, "ec" + R_RED)]),
    ("AvL", "B1", (58.0, 40.0), (58.0, 105.0), -1, T1, 18.0, R_COB,
     [(14.0, "fundo", 1, ""), (12.0, "loja", 2, ""), (13.0, "fundo", 1, "h"), (14.0, "loja", 2, ""), (12.0, "fundo", 1, "")]),
    # ---- BAIRRO DO CANAL (T1 SO): 2 quadras na viela do canal (y 82..90); moinho com a roda d'agua
    ("BairroN", "F1", (-70.0, 90.0), (-134.0, 90.0), 1, T1, 14.0, R_VIO,
     [(12.0, "loja", 2, ""), (10.0, "fundo", 1, "h"), (14.0, "sobrado", 3, "t"), (10.0, "fundo", 1, ""),
      (8.0, "fundo", 1, ""), (10.0, "loja", 2, "")]),
    ("BairroN", "M", (-146.0, 90.0), (-168.0, 90.0), 1, T1, 14.0, R_VIO, [(22.0, "moinho", 1, "")]),
    ("BairroS", "F1", (-166.0, 82.0), (-70.0, 82.0), 1, T1, 18.0, R_COB,
     [(12.0, "loja", 2, ""), (10.0, "fundo", 1, ""), (14.0, "sobrado", 3, "t"), (10.0, "loja", 2, "h"),
      (12.0, "fundo", 1, ""), (13.0, "loja", 2, ""), (12.0, "fundo", 1, "h"), (13.0, "loja", 2, "")]),
    ("BairroS", "B1", (-70.0, 50.0), (-150.0, 50.0), 1, T1, 14.0, R_VIO,
     [(12.0, "fundo", 1, ""), (10.0, "fundo", 1, ""), (14.0, "loja", 2, ""), (10.0, "fundo", 1, "h"),
      (12.0, "fundo", 1, ""), (10.0, "fundo", 1, ""), (12.0, "loja", 2, "")]),
    # ---- FACHADA OESTE DA PRACA (P): 3 quadras continuas (vielas y 159 e y 265 + viela y 212 da casa de cha)
    ("OesteS", "F", (-121.0, 124.0), (-121.0, 154.0), -1, P, 20.0, R_TEAL,
     [(12.0, "esquina", 3, "e"), (9.0, "loja", 2, "h"), (9.0, "loja", 2, "")]),
    ("OesteS", "B", (-159.0, 124.0), (-159.0, 154.0), 1, P, 18.0, R_TEAL, [(14.0, "fundo", 1, ""), (16.0, "loja", 2, "h")]),
    ("OesteM", "F1", (-121.0, 164.0), (-121.0, 207.0), -1, P, 20.0, R_TEAL,
     [(11.0, "loja", 2, "h"), (10.0, "loja", 2, ""), (12.0, "sobrado", 3, "t"), (10.0, "loja", 2, "")]),
    ("OesteM", "B1", (-159.0, 164.0), (-159.0, 207.0), 1, P, 18.0, R_TEAL,
     [(10.0, "fundo", 1, ""), (12.0, "loja", 2, ""), (11.0, "fundo", 1, "h"), (10.0, "loja", 2, "")]),
    ("OesteM", "F2", (-121.0, 217.0), (-121.0, 260.0), -1, P, 20.0, R_TEAL,
     [(16.0, "chaya", 1, "io"), (10.0, "loja", 2, "h"), (9.0, "loja", 2, ""), (8.0, "fundo", 1, "")]),
    ("OesteM", "B2", (-159.0, 217.0), (-159.0, 260.0), 1, P, 18.0, R_TEAL,
     [(12.0, "loja", 2, ""), (10.0, "fundo", 1, ""), (11.0, "fundo", 1, "h"), (10.0, "loja", 2, "")]),
    ("OesteN", "F", (-121.0, 270.0), (-121.0, 298.0), -1, P, 20.0, R_TEAL, [(10.0, "loja", 2, ""), (18.0, "esquina", 3, "e")]),
    ("OesteN", "B", (-159.0, 270.0), (-159.0, 298.0), 1, P, 18.0, R_TEAL, [(14.0, "loja", 2, ""), (14.0, "fundo", 1, "")]),
    # ---- ALEM DO CANAL (W2b, P): 1 fileira continua de frente para o canal (2 trechos)
    ("AlemCanal", "F1", (-190.0, 128.0), (-190.0, 206.0), -1, P, 18.0, R_TEAL,
     [(12.0, "loja", 2, ""), (10.0, "fundo", 1, ""), (14.0, "sobrado", 3, "tc" + R_COB), (10.0, "fundo", 1, "h"),
      (12.0, "loja", 2, ""), (10.0, "fundo", 1, ""), (10.0, "loja", 2, "")]),
    ("AlemCanal", "F2", (-190.0, 214.0), (-190.0, 294.0), -1, P, 18.0, R_TEAL,
     [(10.0, "fundo", 1, ""), (12.0, "loja", 2, "h"), (14.0, "sobrado", 3, "t"), (10.0, "fundo", 1, ""),
      (12.0, "loja", 2, ""), (10.0, "fundo", 1, ""), (12.0, "loja", 2, "")]),
    # ---- RUA ALTA DO PORTO (T1 leste): 2 quadras de lojas de carga e armazens, fachada para a viela leste
    ("PortoAlto1", "F", (66.0, 105.0), (90.0, 105.0), 1, T1, 20.0, R_RED, [(12.0, "armazem", 2, ""), (12.0, "loja", 2, "h")]),
    ("PortoAlto1", "B", (90.0, 67.0), (66.0, 67.0), 1, T1, 18.0, R_RED, [(12.0, "fundo", 1, ""), (12.0, "kura", 2, "")]),
    ("PortoAlto2", "F", (96.0, 105.0), (120.0, 105.0), 1, T1, 20.0, R_RED, [(12.0, "kura", 2, "t"), (12.0, "armazem", 2, "")]),
    ("PortoAlto2", "B", (120.0, 67.0), (96.0, 67.0), 1, T1, 18.0, R_RED, [(12.0, "fundo", 1, "h"), (12.0, "armazem", 2, "")]),
    # ---- NE (PLANO_V2 3.4): fileira continua de 5 lojas no sando + haiden (interior) + honden; o resto e jardim
    ("NE", "Lojas", (122.0, 286.0), (202.0, 286.0), 1, P, 18.0, R_VIO,
     [(16.0, "loja", 2, "h"), (16.0, "loja", 2, ""), (16.0, "sobrado", 3, "t"), (16.0, "loja", 2, "h"), (16.0, "loja", 2, "")]),
    ("NE", "Haiden", (194.0, 291.0), (194.0, 309.0), 1, P, 20.0, R_RED, [(18.0, "santuario", 1, "io")]),
    ("NE", "Honden", (219.0, 295.0), (219.0, 305.0), 1, P, 10.0, R_RED, [(10.0, "honden", 1, "")]),
    # ---- TERRACO ALTO (W3): 2 mansoes com jardim (as casas soltas sairam)
    ("W3", "M1", (-128.0, 326.0), (-128.0, 356.0), -1, W3, 24.0, R_GRN, [(30.0, "mansao", 2, "")]),
    ("W3", "M2", (-186.0, 372.0), (-150.0, 372.0), -1, W3, 22.0, R_GRN, [(36.0, "mansao", 2, "")]),
]


def _h01(key):
    """hash murmur-like (finalizador fmix32) -> [0, 1): variacao determinista sem a correlacao do crc32 (Ilha 4)"""
    h = 2166136261
    for ch in key:
        h = ((h ^ ord(ch)) * 16777619) & 0xffffffff
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


def block_lots():
    """lista de lotes (dict) das ROWS: nome, quadra, centro (x, y), yaw da FRENTE (rad), W (frente), D (fundo), cota z,
    tipo, pisos, beiral (cota absoluta da linha da parede), cumeeira (absoluta), tsuma, hisashi, interior, aberto,
    esquina, telhado (material), trecho de fachada (a, b). A altura varia -1,5..+2 de lote para lote (hash do nome)."""
    out = []
    for blk, row, a, b, side, z, D, roof, lots in ROWS:
        ux, uy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        nx, ny = -uy * side, ux * side                      # normal para a RUA
        s0 = 0.0
        for k, (w, kind, fl, flags) in enumerate(lots):
            nm = "%s_%s%d" % (blk, row, k + 1)
            cx = a[0] + ux * (s0 + w / 2) - nx * D / 2
            cy = a[1] + uy * (s0 + w / 2) - ny * D / 2
            eave = EAVE_H.get((kind, fl), 8.8 + 6.0 * (fl - 1))
            dh = 0.0 if kind in ("portal", "santuario", "honden", "mansao") else round(-1.5 + 3.5 * _h01(nm), 1)
            if kind == "fundo":                      # casa de 1 piso: beiral nunca abaixo de 8,8 (borda baixa do
                dh = round(2.5 * _h01(nm), 1)        # telhado a 7,87 da rua > pulo 7,2: nao se sobe nos telhados)
            rm = flags[flags.index("c") + 1:] if "c" in flags else roof
            flags = flags.split("c")[0]
            tsuma = "t" in flags
            span = (w if tsuma else D) / 2.0
            out.append(dict(name=nm, block=blk, row=row, x=round(cx, 3), y=round(cy, 3), yaw=math.atan2(ny, nx), W=w, D=D,
                            z=z, kind=kind, floors=fl, eave=round(z + eave + dh, 2),
                            ridge=round(z + eave + dh + ROOF_PITCH * span, 2), tsuma=tsuma, hisashi="h" in flags,
                            interior="i" in flags, open="o" in flags, corner="e" in flags, roof=rm,
                            front=((a[0] + ux * s0, a[1] + uy * s0), (a[0] + ux * (s0 + w), a[1] + uy * (s0 + w)))))
            s0 += w
    return out


def lot_poly(lot, pad=0.0):
    """planta do lote (retangulo W x D) + pad"""
    c, sn = math.cos(lot["yaw"]), math.sin(lot["yaw"])          # frente
    ux, uy = -sn, c                                              # ao longo da fachada
    hw, hd = lot["W"] / 2 + pad, lot["D"] / 2 + pad
    return [(lot["x"] + ux * su * hw + c * sv * hd, lot["y"] + uy * su * hw + sn * sv * hd)
            for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


# V2-0: os ARMAZENS DO CAIS continuam como na V1 (op_harbor e refeito na V2-2); o H3 do topo da muralha SAIU (U13)
# (nome, familia, x, y, w, d, rumo da FRENTE, cota, pisos, telhado, cor)
BUILDINGS = [
    ("H1", "armazem", 136.0, 44.0, 22.0, 16.0, 90.0, HARBOR, 2, "kirizuma", "Roof_OP_Blue"),
    ("H2", "armazem", 192.0, 42.0, 20.0, 14.0, 90.0, HARBOR, 1, "kirizuma", "Roof_OP_Blue"),
    ("H4", "pavilhao", 236.0, 58.0, 18.0, 14.0, 180.0, HARBOR, 1, "hip", "Roof_OP_Red"),
]
# RUAS V2 (PLANO_V2 3.3): (pontos, largura, cota). Pedra assentada; a avenida tem leito de 18 + calcadas com meio-fio e
# sarjeta (AVENUE); praca e vielas sem meio-fio. Nada de laje solta sobre grama: o que nao e rua e patio de pedra,
# jardim emoldurado ou lote.
AVENUE = dict(x=(-9.0, 9.0), walk=4.0, front=15.0, y=(44.8, 108.1), curb=(0.3, 0.3), gutter=(0.8, -0.15))
STREETS_V2 = [
    ([(0.0, 44.0), (0.0, 108.0)], 30.0, T1),                                                    # 0 avenida (leito+calcadas)
    ([(10.0, 111.0), (60.0, 111.0), (122.0, 111.0), (126.0, 140.0), (132.0, 158.0)], 12.0, T1),  # 1 viela leste (summon)
    ([(-15.0, 86.0), (-62.0, 86.0)], 6.0, T1),                                                  # 2 viela do canal: portal
    ([(-62.0, 86.0), (-168.0, 86.0)], 8.0, T1),                                                 #   ... ate o canal
    ([(-140.0, 86.0), (-140.0, 108.0)], 12.0, T1),                                              # 3 travessa -> Sudoeste
    ([(-15.0, 111.0), (-160.0, 111.0)], 12.0, T1),                                              # 4 rua do arrimo (T1)
    ([(-66.0, 40.0), (-66.0, 108.0)], 8.0, T1),                                                 # 5 travessa AvO/bairro
    ([(62.0, 40.0), (62.0, 108.0)], 8.0, T1),                                                   # 6 travessa AvL/porto
    ([(-146.0, 47.0), (-66.0, 42.0)], 5.0, T1),                                                 # 7 caminho do penhasco sul
    ([(-164.0, 120.0), (-164.0, 298.0)], 10.0, P),                                              # 8 cais do canal (leste)
    ([(-186.0, 126.0), (-186.0, 296.0)], 8.0, P),                                               # 9 cais do canal (oeste)
    ([(-118.0, 159.0), (-162.0, 159.0)], 10.0, P),                                              # 10 viela y 159
    ([(-118.0, 212.0), (-162.0, 212.0)], 10.0, P),                                              # 11 viela da casa de cha
    ([(-118.0, 265.0), (-162.0, 265.0)], 10.0, P),                                              # 12 viela y 265
    ([(-118.5, 120.0), (-118.5, 300.0)], 5.0, P),                                               # 13 frente da fachada oeste
    ([(-110.0, 312.0), (-120.0, 330.0), (-120.0, 365.0), (-170.0, 366.0)], 10.0, W3),           # 14 terraco alto
    ([(108.0, 296.0), (192.0, 296.0)], 10.0, P),                                                # 15 SANDO do santuario NE
    ([(127.0, 216.0), (152.0, 216.0)], 14.0, T1), ([(146.0, 242.0), (206.0, 237.0)], 12.0, T1),   # 16-17 terraco do summon
    ([(132.0, 150.0), (140.0, 196.0)], 12.0, T1),                                               # 18
    ([(93.0, 67.0), (93.0, 105.0)], 6.0, T1),                                                   # 19 travessa da rua alta
]
STREETS = STREETS_V2               # compatibilidade: quem le L.STREETS (op_veg, op_terrain) ja ve a malha V2
PAGODA = None                      # V2-0 (U13): o pagode do pinaculo oeste SAIU
SHRINE_TORII = (110.0, 296.0)      # torii do sando NE (entrada do santuario, no canto da praca)
NE_TORO = [(124.0, 290.0), (124.0, 302.0), (148.0, 290.0), (148.0, 302.0), (172.0, 290.0), (172.0, 302.0)]  # 6 toro
NE_CHERRY = [(130.0, 312.0), (138.0, 330.0), (160.0, 310.0), (166.0, 330.0),                               # grupo 1
             (214.0, 322.0), (226.0, 331.0), (205.0, 335.0), (190.0, 335.0)]                               # 2 (mirante)


# ------------------------------------------------------------------ rotas de navegacao (andador do QA)
def _exit_tail():
    g = gate_opm_pos()
    ux, uy = exit_dir()
    return [exit_point(1.5), exit_point(30.0), exit_point(60.0), exit_point(EXIT_BRIDGE_LEN + 2.0),
            (g[0] - ux * 7.0, g[1] - uy * 7.0)]


def routes():
    plaza_c = (MINE_C[0], MINE_C[1])
    castle = [(0.0, 300.0), (0.0, 311.0), (0.0, 331.0), (-50.0, 331.0), (-71.0, 331.0), (-71.0, 337.0), (-71.0, 381.0),
              (-71.0, 395.0), (-71.0, 443.0), (-71.0, 452.0), (-46.0, 452.0), (-44.0, 410.0), (-44.0, 370.0),
              (0.0, 368.0), (0.0, 380.0), (0.0, 404.0), (12.0, 414.0)]
    harbor = [(128.0, 216.0), (140.0, 200.0), (140.0, 160.0), (140.0, 140.0), (146.0, 140.0), (201.5, 140.0),
              (207.0, 140.0), (207.0, 128.0), (198.0, 105.0), (160.0, 104.0), (160.0, 99.0), (160.0, 46.0), (160.0, 42.0), (174.0, 42.0),
              (174.0, 58.0),
              (214.0, 60.0), (216.0, 112.0), (228.0, 120.0), (228.0, 152.0), (233.0, 152.0), (244.0, 152.0),
              (248.0, 150.0)]
    return {
        "DS_GATE->ENTRY": ([(0.0, -148.0), (0.0, -120.0), (0.0, -60.0), (0.0, 0.0), (0.0, 22.0)], DECK),
        "ENTRY->PLAZA": ([(0.0, 22.0), (0.0, 33.0), (0.0, 46.0), (0.0, 100.0), (0.0, 108.0), (0.0, 122.0),
                          (0.0, 150.0), plaza_c], T0),
        "ENTRY->SUMMON (viela, sem praca)": ([(0.0, 22.0), (0.0, 33.0), (0.0, 46.0), (4.0, 100.0), (18.0, 106.0),
                                               (60.0, 110.0),
                                               (120.0, 112.0), (126.0, 130.0), (128.0, 160.0), (140.0, 200.0),
                                               (152.0, 214.0)], T0),
        "PLAZA->SUMMON": ([plaza_c, (96.0, 216.0), (114.0, 216.0), (128.0, 216.0), (152.0, 214.0)], P),
        "SUMMON->PLAZA": ([(152.0, 214.0), (128.0, 216.0), (114.0, 216.0), (96.0, 216.0), plaza_c], T1),
        "PLAZA->CASTLE (acessivel)": ([plaza_c, (0.0, 290.0)] + castle, P),
        "PLAZA->HARBOR (navio)": ([plaza_c, (96.0, 216.0), (114.0, 216.0)] + harbor, P),
        "PLAZA->EXIT_OPM": ([plaza_c, (96.0, 216.0), (114.0, 216.0), (128.0, 216.0), (140.0, 244.0),
                             (196.0, 240.0)] + _exit_tail(), P),
        "SUMMON->EXIT_OPM": ([(152.0, 214.0), (150.0, 244.0), (196.0, 240.0)] + _exit_tail(), T1),
        "PLAZA->OESTE (pontes do canal)": ([plaza_c, (-100.0, 170.0), (-118.0, 159.0), (-162.0, 159.0),
                                            (-162.0, 182.0), (-186.0, 182.0), (-188.0, 230.0), (-186.0, 252.0),
                                            (-162.0, 252.0), (-162.0, 265.0), (-118.0, 265.0)], P),
        "PLAZA->TERRACO_ALTO": ([plaza_c, (-96.0, 270.0), (-110.0, 280.0), (-110.0, 287.0), (-110.0, 310.0),
                                 (-120.0, 330.0), (-120.0, 362.0), (-150.0, 364.0)], P),
        # V2-0: viela do canal reta (y 86) pela passagem coberta da quadra AvO; NE = sando -> haiden e sando -> mirante
        "ENTRY->BAIRRO_CANAL": ([(0.0, 46.0), (-4.0, 84.0), (-20.0, 86.0), (-66.0, 86.0), (-120.0, 86.0),
                                 (-146.0, 86.0), (-162.0, 86.0)], T1),
        "BAIRRO_CANAL->OESTE": ([(-146.0, 86.0), (-140.0, 88.0), (-140.0, 108.0), (-140.0, 121.0),
                                 (-116.0, 123.0), (-104.0, 160.0)], T1),
        "PLAZA->NE (santuario)": ([plaza_c, (90.0, 270.0), (102.0, 296.0), (150.0, 296.0), (176.0, 296.0),
                                   (180.0, 301.0), (180.0, 323.0), (200.0, 327.0)], P),
        "NE->SANTUARIO (frente)": ([(102.0, 296.0), (150.0, 296.0), (186.0, 296.0), (192.0, 300.0), (199.0, 300.0)], P),
    }


def gate_open_route():
    g = gate_opm_pos()
    ux, uy = exit_dir()
    return [(g[0] - ux * 7.0, g[1] - uy * 7.0), g, (g[0] + ux * 12.0, g[1] + uy * 12.0),
            exit_point(EXIT_BRIDGE_LEN + ANCHOR_OPM_OFF - 1.0)]


# ------------------------------------------------------------------ cameras de QA (local)
def cams():
    g = gate_opm_pos()
    e = exit_point(40.0)
    return {
        # referencias: mesmo enquadramento da concept (sul, alta, no eixo) e da ref do anime (da praca, baixa, castelo +
        # arvore no alto)
        "CAM_OP_Ref_01": ((14.0, -170.0, 214.0), (24.0, 300.0, 50.0), 18),
        "CAM_OP_Ref_02": ((0.0, 196.0, P + 9.0), (0.0, 420.0, CC + 64.0), 22),
        "CAM_OP_Front": ((40.0, -330.0, 200.0), (40.0, 260.0, 90.0), 26),
        "CAM_OP_Back": ((40.0, 900.0, 260.0), (40.0, 220.0, 90.0), 26),
        "CAM_OP_Left": ((-620.0, 230.0, 220.0), (40.0, 240.0, 90.0), 28),
        "CAM_OP_Right": ((760.0, 200.0, 220.0), (60.0, 250.0, 90.0), 28),
        "CAM_OP_BirdEye": ((60.0, 250.0, 1250.0), (60.0, 252.0, 60.0), 30),
        "CAM_OP_Entry": ((10.0, -60.0, 96.0), (0.0, 80.0, 100.0), 22),
        "CAM_OP_Plaza": ((0.0, 128.0, 128.0), (0.0, 300.0, 100.0), 18),
        "CAM_OP_Castle": ((-30.0, 270.0, 150.0), (0.0, 410.0, 170.0), 22),
        "CAM_OP_Tree": ((120.0, 330.0, 170.0), (20.0, 425.0, 200.0), 20),
        "CAM_OP_Harbor": ((150.0, -40.0, 110.0), (250.0, 160.0, 70.0), 22),
        "CAM_OP_Summon": ((60.0, 170.0, 112.0), (170.0, 214.0, 120.0), 22),
        "CAM_OP_Exit": ((200.0, 190.0, 120.0), (g[0], g[1], T1 + 10.0), 22),
        "CAM_OP_Skull": ((120.0, 140.0, 110.0), (322.0, 190.0, 110.0), 26),
        "CAM_OP_PlayerHeight_Entry": ((0.0, -40.0, DECK + 0.8 + EYE), (0.0, 120.0, T1 + 10.0), 22),
        "CAM_OP_PlayerHeight_Street": ((0.0, 50.0, T1 + EYE), (0.0, 160.0, P + 14.0), 22),
        "CAM_OP_PlayerHeight_Plaza": ((0.0, 140.0, P + EYE), (0.0, 400.0, CC + 30.0), 22),
        "CAM_OP_PlayerHeight_Castle": ((-48.0, 360.0, CC + EYE), (0.0, 392.0, CC + 16.0), 22),
        "CAM_OP_PlayerHeight_Harbor": ((214.0, 70.0, HARBOR + EYE), (248.0, 160.0, HARBOR + 16.0), 22),
        "CAM_OP_PlayerHeight_Summon": ((100.0, 214.0, P + EYE), (170.0, 214.0, T1 + 22.0), 22),
        "CAM_OP_PlayerHeight_Exit": ((e[0], e[1], T1 + EYE), (g[0], g[1], T1 + 10.0), 22),
        # V2-0: planta nova (avenida, quadras, NE, canal, porto) - de cima e na altura do jogador
        "CAM_OP_V2_TopCidade": ((-30.0, -90.0, 420.0), (-30.0, 190.0, 90.0), 24),
        "CAM_OP_V2_AereaAvenida": ((0.0, -6.0, 150.0), (0.0, 110.0, 96.0), 24),
        "CAM_OP_V2_AereaOeste": ((-70.0, 120.0, 170.0), (-160.0, 215.0, 95.0), 22),
        "CAM_OP_V2_AereaNE": ((110.0, 210.0, 165.0), (190.0, 306.0, 100.0), 22),
        "CAM_OP_V2_AereaPorto": ((100.0, 40.0, 150.0), (190.0, 120.0, 60.0), 22),
        "CAM_OP_PlayerHeight_Oeste": ((-106.0, 128.0, P + EYE), (-124.0, 250.0, P + 10.0), 22),
        "CAM_OP_PlayerHeight_Bairro": ((-68.0, 86.0, T1 + EYE), (-170.0, 88.0, T1 + 9.0), 22),
        "CAM_OP_PlayerHeight_NE": ((110.0, 296.0, P + EYE), (200.0, 302.0, P + 9.0), 22),
        "CAM_OP_PlayerHeight_Canal": ((-164.0, 168.0, P + EYE), (-176.0, 262.0, P + 4.0), 22),
    }


PLAYER_CAMS = [k for k in cams() if "PlayerHeight" in k]
REF_CAMS = ["CAM_OP_Ref_01", "CAM_OP_Ref_02"]
