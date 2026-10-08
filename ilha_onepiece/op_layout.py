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
           (148.0, 150.0), (204.0, 150.0), (206.0, 170.0), (206.0, 256.0), (200.0, 264.0), (116.0, 264.0),
           (116.0, 140.0), (112.0, 126.0), (96.0, 120.0), (64.0, 117.0), (-64.0, 117.0), (-110.0, 117.0),
           (-170.0, 117.0), (-170.0, 60.0)]                                                                 # T1
P_BASE = [(-170.0, 118.0), (-110.0, 118.0), (-64.0, 118.0), (64.0, 118.0), (96.0, 124.0), (112.0, 140.0),
          (116.0, 170.0), (116.0, 262.0), (222.0, 262.0), (226.0, 290.0), (206.0, 316.0), (190.0, 336.0),
          (100.0, 336.0), (96.0, 314.0), (-96.0, 314.0), (-110.0, 300.0), (-170.0, 300.0)]                # P
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
    ("CastleFootE", [(18.0, 348.0), (254.0, 348.0), (254.0, 364.0), (228.0, 370.0), (212.0, 382.0), (186.0, 352.0),
                     (72.0, 372.0), (62.0, 352.0), (18.0, 350.0)], 104.0),
    ("NERocksW", [(206.0, 316.0), (226.0, 290.0), (241.0, 298.0), (242.0, 338.5), (190.0, 338.5), (190.0, 336.0)], 100.0),
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
HEADLAND = _HL                                  # T1 (promontorio da saida)
SKULL_C, SKULL_FACE_DEG = (322.0, 190.0), 195.0  # caveira com chifres (formacao na ponta sul do promontorio)
SKULL_ROCK = [(296.0, 228.0), (294.0, 168.0), (306.0, 152.0), (326.0, 147.0), (344.0, 158.0), (351.0, 182.0),
              (350.0, 208.0), (342.0, 230.0), (318.0, 234.0)]
SWORD_SPUR = [(176.0, 488.0), (200.0, 462.0), (238.0, 506.0), (286.0, 560.0), (312.0, 590.0), (306.0, 616.0),
              (282.0, 622.0), (262.0, 590.0), (226.0, 546.0), (194.0, 512.0)]
SWORD_POS, SWORD_ROCK_Z = (292.0, 600.0), 100.0  # espada monumental cravada no pinaculo do esporao (silhueta distante)
WEST_SPIRE = (-246.0, 372.0, 20.0, 158.0)       # pinaculo oeste com o pagode (x, y, raio, topo) - cenografico


def floors():
    """pisos andaveis: (nome, poligono, cota, prioridade) - o de MAIOR prioridade manda"""
    return [
        ("Court", COURT, CC, 70),
        ("CastleLanding", CASTLE_LAND, CL, 68),
        ("W3", W3_POLY, W3, 66),
        ("Forecourt", FORECOURT, CF, 64),
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


def zone_of(x, y):
    for nm, poly, z, pr in _FLOORS:
        if point_in_poly(x, y, poly):
            return _zval(z, x, y)
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
]
STAIR_TOP_Z = {"Chegada": T1, "Praca": P, "Summon": P, "Sudoeste": P, "OesteAlta": W3, "Adro": CF, "CasteloA": CL,
               "CasteloB": CC, "PortoA": T1, "PortoB": HMID}


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


def bridge_list():
    """(nome, inicio (x, y, z), fim (x, y, z), largura): ponte de chegada (rampa 80,2 -> 84,2), ponte vermelha de
    saida (T1), 2 pontes vermelhas do canal oeste, prancha do navio"""
    e0 = exit_point(0.0)
    e1 = exit_point(EXIT_BRIDGE_LEN)
    return [("Arrival", (PREV_X, PREV_Y, DECK), (0.0, 0.0, T0), DECK_W),
            ("ExitBridge", (e0[0], e0[1], T1), (e1[0], e1[1], T1), EXIT_W),
            ("CanalS", (-168.0, 182.0, P), (-180.0, 182.0, P), 10.0),
            ("CanalN", (-168.0, 252.0, P), (-180.0, 252.0, P), 10.0),
            ("Gangway", (230.0, 152.0, HARBOR), (241.6, 152.0, SHIP), 5.0)]


# ------------------------------------------------------------------ PRACA / mineracao
MINE_RECT = (-76.0, 156.0, 76.0, 276.0)        # MiningZone 152 x 120 (>= 112 x 150 da DS girado; 18.240 studs2)
MINE_C = ((MINE_RECT[0] + MINE_RECT[2]) / 2, (MINE_RECT[1] + MINE_RECT[3]) / 2)
ORE_PLAN = [("SUPERLEGENDARY", 2), ("EPIC", 10), ("UNCOMMON", 22), ("COMMON", 38)]   # 72 marcadores (como a DS)
ORE_RADIUS = {"COMMON": 2.6, "UNCOMMON": 3.0, "EPIC": 3.4, "SUPERLEGENDARY": 4.4}
EMBLEM_C, EMBLEM_R = (0.0, 216.0), 13.0        # emblema de chao RENTE (sem colisao, sem relevo)
BANNERS = [(-98.0, 136.0), (98.0, 136.0), (-88.0, 300.0), (100.0, 296.0)]   # mastros de estandarte (fora da zona + 8)


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
CANAL_E = [(18.0, 342.0, CF - 0.6), (92.0, 342.0, CF - 0.6), (100.0, 342.0, P - 0.6), (188.0, 343.0, P - 0.6),
           (248.0, 343.0, P - 0.6), (248.5, 304.0, P - 0.6)]
FALL_E = (248.5, 301.0, P - 0.6, SEA)             # queda leste: canal (garganta na rocha NE) -> enseada
CANAL_W = [(-174.0, 299.0, P - 0.6), (-174.0, 250.0, P - 0.6), (-174.0, 182.0, P - 0.6), (-174.0, 120.0, P - 0.6),
           (-174.0, 114.0, T1 - 0.6), (-174.0, 92.0, T1 - 0.6), (-174.0, 58.0, T1 - 0.6)]
CANAL_W_X = (-178.0, -170.0)
SPRING_W = (-174.0, 300.0, W3 - 3.0)              # bica no arrimo do terraco alto
WHEEL = (-174.0, 90.0, 13.0, 4.0)                 # roda d'agua no canal (x, y, diametro, largura); eixo leste-oeste
WHEEL_AXLE_Z = T1 + 3.4
FALL_W = (-174.0, 54.0, T1 - 0.6, SEA)            # queda oeste: canal -> mar
WEIRS = [("Weir_E", (96.0, 342.0, CF - 0.6, P - 0.6)), ("Weir_W", (-174.0, 117.0, P - 0.6, T1 - 0.6))]
SEA_C, SEA_SIZE = (60.0, 260.0), 2200.0           # mar local (quadrado no cliente, so na area 5)

# ------------------------------------------------------------------ SUMMON (terraco lateral, transicao para o porto)
SUMMON_TOWER = (170.0, 214.0)                     # torre AMS aprovada, frente para -X (oeste: praca)
SUMMON_FACE_DEG = 180.0
SUMMON_C, SUMMON_R = (166.0, 214.0), 26.0
SUMMON_INTERACT_D, SUMMON_PLAYER_D = 7.0, 16.0

# ------------------------------------------------------------------ CAPITAL: construcoes (blockout) por conjunto
# (nome, familia, x, y, w (ao longo da frente), d (fundo), rumo da FRENTE (graus), cota, pisos, telhado, cor do telhado)
# familias: loja (machiya comercial cenografica), casa (minka), esquina (2-3 pisos), pavilhao (aberto), mansao,
# santuario, armazem (portuario), moinho. A cor do telhado e POR CONJUNTO: rua de chegada azul; oeste azul com
# esquinas verdes; terraco alto verde; NE (santuario) avermelhado; porto madeira/azul.
BUILDINGS = [
    # rua de chegada (T1): fachadas comerciais dos 2 lados, ritmo de alturas e recuos; 1 esquina-marco de 3 pisos
    ("C1", "loja", -27.0, 55.0, 16.0, 22.0, 0.0, T1, 2, "irimoya", "Roof_OP_Blue"),
    ("C2", "loja", -30.0, 73.0, 14.0, 26.0, 0.0, T1, 1, "kirizuma", "Roof_OP_Blue"),
    ("C4", "esquina", -28.0, 101.0, 16.0, 24.0, 0.0, T1, 2, "irimoya", "Roof_OP_Green"),
    ("C5", "loja", 26.0, 53.0, 14.0, 20.0, 180.0, T1, 2, "kirizuma", "Roof_OP_Blue"),
    ("C6", "loja", 30.0, 72.0, 18.0, 28.0, 180.0, T1, 1, "irimoya", "Roof_OP_Blue"),
    ("C7", "esquina", 28.0, 93.0, 16.0, 22.0, 180.0, T1, 3, "irimoya", "Roof_OP_Red"),
    ("B1", "casa", -54.0, 62.0, 18.0, 16.0, 0.0, T1, 1, "irimoya", "Roof_OP_Blue"),
    ("B2", "casa", -58.0, 97.0, 18.0, 18.0, 0.0, T1, 2, "kirizuma", "Roof_OP_Blue"),
    ("B3", "casa", 56.0, 60.0, 18.0, 18.0, 180.0, T1, 1, "irimoya", "Roof_OP_Blue"),
    ("B4", "casa", 62.0, 92.0, 22.0, 16.0, 180.0, T1, 2, "irimoya", "Roof_OP_Blue"),
    ("B5", "casa", 82.0, 60.0, 18.0, 16.0, 180.0, T1, 1, "irimoya", "Roof_OP_Blue"),
    ("B6", "casa", 88.0, 88.0, 20.0, 18.0, 180.0, T1, 2, "kirizuma", "Roof_OP_Green"),
    ("B7", "casa", 106.0, 70.0, 16.0, 14.0, 180.0, T1, 1, "irimoya", "Roof_OP_Blue"),
    # bairro do canal (T1, sudoeste): casas baixas, moinho da roda d'agua
    ("S1", "casa", -86.0, 58.0, 22.0, 16.0, 90.0, T1, 1, "irimoya", "Roof_OP_Blue"),
    ("S2", "casa", -120.0, 56.0, 20.0, 16.0, 90.0, T1, 1, "kirizuma", "Roof_OP_Blue"),
    ("S3", "casa", -98.0, 98.0, 24.0, 16.0, -90.0, T1, 2, "irimoya", "Roof_OP_Green"),
    ("S4", "moinho", -156.0, 90.0, 14.0, 18.0, 180.0, T1, 1, "kirizuma", "Roof_OP_Blue"),
    ("S5", "casa", -121.0, 100.0, 16.0, 14.0, -90.0, T1, 1, "kirizuma", "Roof_OP_Blue"),
    # quarteirao oeste (P): fileira que encara a praca (comercio) + fileira do outro lado do canal (casas)
    ("W1", "esquina", -140.0, 140.0, 26.0, 30.0, 0.0, P, 2, "irimoya", "Roof_OP_Green"),
    ("W2", "loja", -140.0, 177.0, 24.0, 32.0, 0.0, P, 1, "irimoya", "Roof_OP_Blue"),
    ("W3", "pavilhao", -134.0, 212.0, 22.0, 20.0, 0.0, P, 1, "hip", "Roof_OP_Blue"),
    ("W4", "esquina", -140.0, 248.0, 24.0, 32.0, 0.0, P, 3, "irimoya", "Roof_OP_Blue"),
    ("W5", "casa", -140.0, 283.0, 26.0, 28.0, 0.0, P, 2, "irimoya", "Roof_OP_Green"),
    ("X1", "casa", -203.0, 152.0, 22.0, 22.0, 0.0, P, 1, "irimoya", "Roof_OP_Blue"),
    ("X2", "casa", -204.0, 212.0, 26.0, 24.0, 0.0, P, 2, "kirizuma", "Roof_OP_Blue"),
    ("X3", "casa", -203.0, 268.0, 22.0, 22.0, 0.0, P, 1, "irimoya", "Roof_OP_Green"),
    # terraco alto oeste (W3): mansoes de telhado verde
    ("U1", "mansao", -150.0, 332.0, 34.0, 22.0, -90.0, W3, 2, "irimoya", "Roof_OP_Green"),
    ("U2", "mansao", -128.0, 386.0, 26.0, 22.0, 0.0, W3, 2, "irimoya", "Roof_OP_Green"),
    ("U3", "casa", -176.0, 398.0, 24.0, 20.0, 0.0, W3, 1, "irimoya", "Roof_OP_Blue"),
    ("U4", "casa", -198.0, 344.0, 18.0, 22.0, 0.0, W3, 1, "kirizuma", "Roof_OP_Green"),
    ("U5", "pavilhao", -202.0, 380.0, 14.0, 12.0, 0.0, W3, 1, "hip", "Roof_OP_Green"),
    # quarteirao NE (P): santuario de telhado avermelhado + casas
    ("N1", "santuario", 150.0, 306.0, 24.0, 22.0, 180.0, P, 1, "irimoya", "Roof_OP_Red"),
    ("N2", "casa", 190.0, 280.0, 20.0, 16.0, -90.0, P, 2, "irimoya", "Roof_OP_Red"),
    ("N3", "casa", 176.0, 326.0, 18.0, 14.0, -90.0, P, 1, "kirizuma", "Roof_OP_Blue"),
    ("N4", "casa", 210.0, 276.0, 14.0, 12.0, -90.0, P, 1, "irimoya", "Roof_OP_Red"),
    ("N5", "esquina", 110.0, 324.0, 18.0, 14.0, -90.0, P, 2, "irimoya", "Roof_OP_Red"),
    # porto (cais 52,2 e rua alta 70,2): armazens e pavilhao sobre palafitas
    ("H1", "armazem", 136.0, 44.0, 22.0, 16.0, 90.0, HARBOR, 2, "kirizuma", "Roof_OP_Blue"),
    ("H2", "armazem", 192.0, 42.0, 20.0, 14.0, 90.0, HARBOR, 1, "kirizuma", "Roof_OP_Blue"),
    ("H3", "armazem", 176.0, 120.0, 24.0, 14.0, -90.0, HMID, 2, "irimoya", "Roof_OP_Blue"),
    ("H4", "pavilhao", 236.0, 58.0, 18.0, 14.0, 180.0, HARBOR, 1, "hip", "Roof_OP_Red"),
]
# ruas e vielas (laje clara rente sobre o tampo de grama): (pontos, largura, cota)
STREETS = [
    ([(0.0, 44.0), (0.0, 112.0)], 24.0, T1),                                                    # rua de chegada
    ([(10.0, 111.0), (60.0, 111.0), (122.0, 111.0), (126.0, 140.0), (132.0, 158.0)], 12.0, T1),  # viela leste (summon)
    ([(-12.0, 86.0), (-44.0, 86.0), (-48.0, 78.0), (-120.0, 77.0), (-160.0, 72.0)], 10.0, T1),   # viela do canal
    ([(-140.0, 76.0), (-140.0, 108.0)], 10.0, T1),
    ([(-164.0, 120.0), (-164.0, 298.0)], 10.0, P),                                              # cais do canal (leste)
    ([(-186.0, 126.0), (-186.0, 296.0)], 8.0, P),                                               # cais do canal (oeste)
    ([(-118.0, 159.0), (-160.0, 159.0)], 10.0, P), ([(-118.0, 265.0), (-160.0, 265.0)], 9.0, P),
    ([(-119.0, 120.0), (-119.0, 300.0)], 7.0, P),                                               # frente do quarteirao
    ([(-110.0, 312.0), (-120.0, 330.0), (-120.0, 365.0), (-170.0, 366.0)], 10.0, W3),           # terraco alto
    ([(100.0, 282.0), (170.0, 290.0), (204.0, 296.0)], 10.0, P), ([(118.0, 286.0), (126.0, 306.0), (138.0, 306.0)], 8.0, P),
    ([(127.0, 216.0), (152.0, 216.0)], 14.0, T1), ([(146.0, 242.0), (206.0, 237.0)], 12.0, T1),   # terraco do summon
    ([(132.0, 150.0), (140.0, 196.0)], 12.0, T1),
]
PAGODA = (WEST_SPIRE[0], WEST_SPIRE[1], WEST_SPIRE[3])   # pagode de 5 andares no pinaculo oeste (cenografico)
SHRINE_TORII = (128.0, 306.0)                            # torii pequeno do santuario NE (vao 8 x 9)

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
        "ENTRY->SUMMON (viela, sem praca)": ([(0.0, 22.0), (0.0, 33.0), (0.0, 46.0), (6.0, 104.0), (60.0, 110.0),
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
        "ENTRY->BAIRRO_CANAL": ([(0.0, 46.0), (-4.0, 84.0), (-40.0, 86.0), (-46.0, 83.0), (-72.0, 78.0),
                                 (-120.0, 78.0), (-146.0, 74.0), (-160.0, 66.0)], T1),
        "BAIRRO_CANAL->OESTE": ([(-146.0, 74.0), (-140.0, 100.0), (-140.0, 108.0), (-140.0, 121.0),
                                 (-116.0, 123.0), (-104.0, 160.0)], T1),
        "PLAZA->NE (santuario)": ([plaza_c, (100.0, 282.0), (170.0, 290.0), (204.0, 296.0)], P),
        "NE->SANTUARIO (frente)": ([(100.0, 282.0), (124.0, 296.0), (126.0, 306.0), (134.0, 306.0)], P),
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
    }


PLAYER_CAMS = [k for k in cams() if "PlayerHeight" in k]
REF_CAMS = ["CAM_OP_Ref_01", "CAM_OP_Ref_02"]
