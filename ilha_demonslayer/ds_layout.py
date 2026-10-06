# ds_layout - planta TRAVADA da Ilha 4 (DEMON SLAYER, Monte Natagumo). Onda 0 (plano/PLANO_DS.md, aprovado 2026-10-06).
# Origem: plano/scripts/ds_geo.py (constantes e encaixe), travadas aqui com as correcoes da onda 0 (ver "CORRECOES").
# 1 BU = 1 stud, Z para cima. Cotas Z ABSOLUTAS = Y do Roblox.
# Referencial LOCAL: origem = centro da soleira do TORII DE ENTRADA; +Y = eixo do percurso (entrada -> trilha -> clareira
# -> subida -> forja -> saida); +X = direita de quem chega (bambuzal, summon, roda d'agua); -X = esquerda (vila, saida NO).
# Mundo (Blender do lobby): W4 = T(ancora_SG) . Rz(WORLD_YAW_DEG) . T(-WORLD_FROM_PREV_local); Roblox = (x, z, -y).
# CORRECOES da onda 0 sobre o ds_geo (medidas na planta; nenhuma muda a ideia do plano):
#   C1 nariz sul do RIM alargado (o patio T0 passava 4 da borda) e pontos de piso recuados 2-4 da borda (a borda e
#      suavizada por Catmull-Rom);
#   C2 patio T0 vai ate y 42 (o pe da escada Trilha ficava 0,6 fora do patio) e a trilha T1 comeca em y 54 (o topo da
#      escada chega em 54,4);
#   C3 borda sul do terraco da forja passa NORTE do patamar da subida: (-36, 392) -> (-20, 436) -> (118, 428). O ds_geo
#      cortava o patamar (T3) com o T4. Entre a clareira e o T4 fica o PATAMAR-MIRANTE (berma T3 70,2), que contem o
#      CLIMB_LAND; o patio da forja comeca em y 436 (igual ao FORGE_YARD do plano);
#   C4 piso T1 unico (T1_BASE) para trilha + vila baixa + clareira + margens (o plano deixava frestas entre poligonos ->
#      paredes invisiveis no meio do chao); a vila alta (T2) vai ate o pe do muro da forja (sem fosso entre T2 e T4);
#   C5 canal leste passa para x ~121 (no plano ele caia em cima do pe da escada do summon, x 128); a pontezinha fica
#      em (121, 300);
#   C6 lagoa alongada ate o pe do muro da forja (cascata de 20 cai direto nela: entre o T4 e a lagoa do plano havia a
#      berma), centro (112, 402);
#   C7 bambuzal = chao INCLINADO andavel (54,2 em y 28 -> 60,2 em y 132, 5,8%); a rampa do plano e o caminho calcado nele;
#   C8 torre-chamine da forja mais alta (corpo +50, chapeu +58, chamine ate +72 = 152,2): a torre AMS aprovada (sem
#      redesenho) tem 60 de altura (estrela em ~130 sobre o T3); o plano estimava ~115. Com isso a chamine fica >= 20
#      acima de tudo (criterio do gate) e o summon segue abaixo dela;
#   C9 saida: piso T4 proprio (EXIT_LAND) em volta do caminho de saida ate o torii (o plano so tinha a polilinha).
import math

# ------------------------------------------------------------------ encaixe (ancora REAL da Ilha 3 lida no Studio = sg_layout)
A_RBX = (-1534.4934, 52.2, 962.4429)          # ISLAND_NEXT_ANCHOR_DemonSlayer (Roblox)
A_FWD = (-0.7660, 0.0, 0.6428)                # frente da ancora (Roblox)
A_W = 18.0
GATE_DS_RBX = (-1513.04, 52.2, 944.45)        # portao Demon Slayer aprovado (ilhota da Shadow Garden), 28 antes da ancora
ANCHOR_WORLD = (A_RBX[0], -A_RBX[2], A_RBX[1])   # Blender (x, y, z) do mundo do lobby
WORLD_YAW_DEG = 130.0                          # local +Y -> Roblox (-0,766; 0; 0,643) = frente da ancora (ponte reta)
BRIDGE_IN_LEN = 100.0
PREV_X, PREV_Y = 0.0, -BRIDGE_IN_LEN           # WORLD_FROM_PREV local

# ------------------------------------------------------------------ cotas (Z absoluto = Y Roblox)
DECK = 52.2          # tabuleiro na ancora (= P3 da Shadow Garden)
T0 = 54.2            # patio do torii (a ponte sobe 2 em 100: rampa de 1,1 grau, sem degrau)
T1 = 60.2            # trilha, vila baixa e CLAREIRA (piso da MiningZone)
T2 = 66.2            # vila alta
T3 = 70.2            # plato do summon e patamar-mirante da subida
T4 = 80.2            # terraco da forja, caminho de saida, ponte de saida e ancora One Piece
SHOULDER = 53.6      # chao "bravo" (fora dos pisos): ravina leste e nariz sul
FLOOR_BOT = 46.0     # fundo das caixas de colisao dos pisos (macico: ninguem passa por baixo de um terraco)
KEEL = -34.0         # fundo da quilha (Tier C)
SEA_CLOUD = -60.0    # mar de nuvens (cliente), so visual
RISE_MAX, TREAD_MIN = 0.8, 1.7
LEVELS = (DECK, T0, T1, T2, T3, T4)
DECK_W = 18.0
EYE = 5.5


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
        x, y = pts[i]
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


def area(P):
    return abs(sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))) / 2


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ contorno (topo do penhasco), anti-horario (C1)
RIM_CTRL = [(-26, -3), (26, -3), (38, 6), (58, 22), (72, 48), (76, 84), (86, 112), (108, 128), (132, 140), (144, 168),
            (150, 196), (148, 214), (158, 226), (184, 238), (204, 258), (212, 290), (206, 322), (188, 342), (160, 352),
            (146, 368), (142, 392), (150, 414), (138, 436), (144, 462), (134, 488), (128, 514), (108, 548), (80, 572),
            (40, 586), (0, 590), (-40, 584), (-70, 586), (-92, 600), (-108, 594), (-121, 574), (-128, 552),
            (-140, 532), (-136, 506), (-150, 484), (-148, 456), (-160, 436), (-156, 410), (-164, 388), (-160, 364),
            (-170, 340), (-174, 312), (-166, 288), (-170, 262), (-158, 240), (-160, 214), (-148, 196), (-150, 172),
            (-141, 150), (-128, 132), (-120, 120), (-92, 104), (-64, 92), (-56, 64), (-52, 36), (-38, 12)]
# borda com lobos e reentrancias DIRIGIDOS (sem trecho reto > 60; gate "nao parecer quadrado"): promontorio da vila
# alta a oeste (mirante sobre o vazio), baia entre a vila e a forja, lobo do patio do carvao, nariz da saida a NO
ISLAND_RIM = smooth_closed(RIM_CTRL, 2)

# ------------------------------------------------------------------ patamares (pisos) - prioridade maior manda
ENTRY_COURT = [(-22, 0), (22, 0), (28, 14), (26, 34), (8, 42), (-18, 42), (-26, 20)]                       # T0 (C2)
TRAIL_T1 = [(-28, 54), (8, 54), (14, 80), (10, 110), (4, 130), (-40, 130), (-44, 96), (-36, 70)]          # T1 (visual)
BAMBOO_RAMP = [(20, 28), (40, 58), (54, 98), (66, 132), (68, 142)]                                       # caminho calcado
BAMBOO = [(22, 0), (37, 6), (56, 22), (69, 48), (73, 84), (83, 112), (104, 127), (120, 136), (98, 154), (68, 140),
          (36, 132), (6, 128), (12, 110), (14, 80), (8, 54), (8, 42), (26, 34), (28, 14)]               # chao inclinado (C7)
BAMBOO_Y0, BAMBOO_Y1 = 28.0, 132.0
CLEARING = [(-40, 132), (0, 126), (36, 132), (68, 140), (98, 154), (118, 178), (128, 212), (126, 252),
            (122, 292), (126, 336), (130, 380), (116, 400), (92, 396), (76, 382), (54, 380), (14, 378), (-22, 368),
            (-42, 344), (-46, 304), (-44, 256), (-42, 212), (-40, 172)]                                    # T1 (visual)
VILLAGE_LOW = [(-40, 112), (-40, 214), (-74, 226), (-148, 226), (-143, 186), (-135, 150), (-118, 124),
               (-90, 110), (-63, 102)]                                                                    # T1 (visual)
T1_BASE = [(-28, 54), (8, 54), (14, 80), (12, 110), (6, 128), (36, 132), (68, 140), (98, 154), (118, 178), (128, 212),
           (134, 236), (146, 258), (149, 272), (149, 328), (140, 338), (134, 378), (127, 428), (106, 428),
           (101, 412), (92, 402), (76, 382), (54, 380), (14, 378), (-22, 370), (-44, 372), (-60, 366), (-61, 362),
           (-55, 344), (-51, 300), (-57, 250), (-75, 227), (-148, 227), (-143, 186), (-135, 150), (-118, 124),
           (-90, 110), (-63, 102), (-44, 96), (-36, 70)]                                                   # T1 (C4)
VILLAGE_HIGH = [(-148, 228), (-74, 226), (-56, 250), (-50, 300), (-54, 344), (-60, 371), (-148, 380),
                (-156, 340), (-157, 300), (-156, 262)]                                                     # T2 (C4)
SUMMON_PLAT = [(150, 270), (176, 264), (200, 274), (206, 300), (198, 326), (176, 336), (150, 330)]        # T3
BERM = [(-60, 366), (-44, 372), (-22, 370), (14, 378), (54, 380), (76, 382), (92, 402), (101, 412), (104, 429),
        (-20, 436), (-36, 392), (-60, 372)]                                                                # T3 (C3)
CLIMB_LAND = (-14.0, 400.0, 46.0, 414.0)                                                                  # T3 calcado
FORGE_TERR = [(-148, 380), (-60, 372), (-36, 392), (-20, 436), (118, 428), (130, 440), (128, 478),
              (118, 512), (60, 520), (-60, 524), (-104, 540), (-118, 528), (-132, 500), (-141, 460),
              (-146, 420)]                                                                                # T4 (C3)
EXIT_PATH = [(-104, 452), (-114, 496), (-110, 540), (-100, 572), (-95, 594)]                             # calcada
EXIT_LAND = [(-128, 520), (-100, 520), (-78, 530), (-72, 582), (-90, 594), (-104, 590), (-116, 570),
             (-126, 543)]                                                                                 # T4 (C9)
# terreno que nao e piso (so visual): crista oeste da trilha, barranco nordeste, rochas da montanha atras da forja
WEST_RIDGE = [(-36, 14), (-26, 20), (-18, 42), (-28, 54), (-36, 70), (-44, 96), (-63, 102), (-62, 92), (-54, 64),
              (-50, 36)]
WEST_RIDGE_Z = 68.0
NE_BANK = [(140, 338), (150, 331), (176, 336), (160, 352), (140, 372), (136, 404), (133, 440), (130, 440),
           (118, 428), (127, 428), (134, 378)]
NE_BANK_Z = 74.0
BACK_ROCKS = [(-78, 530), (-60, 524), (60, 520), (118, 512), (125, 516), (107, 547), (80, 570), (40, 584), (0, 588),
              (-40, 582), (-71, 584)]
BACK_ROCKS_Z = 98.0


def bamboo_z(x, y):
    t = max(0.0, min(1.0, (y - BAMBOO_Y0) / (BAMBOO_Y1 - BAMBOO_Y0)))
    return T0 + (T1 - T0) * t


def floors():
    """pisos andaveis: (nome, poligono, cota (numero ou funcao (x, y)), prioridade) - o de MAIOR prioridade manda"""
    return [
        ("Summon", SUMMON_PLAT, T3, 60),
        ("Forge", FORGE_TERR, T4, 55),
        ("ExitLand", EXIT_LAND, T4, 54),
        ("Berm", BERM, T3, 50),
        ("VillageHigh", VILLAGE_HIGH, T2, 45),
        ("T1", T1_BASE, T1, 30),
        ("Bamboo", BAMBOO, bamboo_z, 25),
        ("Entry", ENTRY_COURT, T0, 20),
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
    ("Trilha", (-12.0, 40.0, T0), 90.0, 12.0, 8, 1.8, True),
    ("VilaAlta", (-84.0, 216.0, T1), 90.0, 10.0, 8, 1.8, True),
    ("VilaClareira", (-44.0, 284.0, T1), 180.0, 8.0, 8, 1.8, True),
    ("Summon", (128.0, 300.0, T1), 0.0, 12.0, 13, 1.75, True),
    ("SubidaA", (16.0, 377.0, T1), 90.0, 16.0, 13, 1.8, True),
    ("SubidaB", (30.0, 414.0, T3), 90.0, 14.0, 13, 1.8, True),
    ("OesteForja", (-66.0, 342.0, T2), 90.0, 10.0, 18, 1.75, True),
]
STAIR_TOP_Z = {"Trilha": T1, "VilaAlta": T2, "VilaClareira": T2, "Summon": T3, "SubidaA": T3, "SubidaB": T4,
               "OesteForja": T4}


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
    """Sutherland-Hodgman: parte do poligono com a*x + b*y + c >= 0"""
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
    """poligono - retangulo (alinhado aos eixos) em ate 4 pedacos disjuntos (oeste, leste, sul, norte do retangulo)"""
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
    """entalhe de cada escada no patamar de CIMA (a escada e cortada no arrimo, como no plano): (escada, piso de cima,
    retangulo (x0, y0, x1, y1) do pe ao topo com os banzos, cota do pe, cota do topo). O piso de cima perde o
    retangulo (visual e colisao) do pe ate a linha do topo; um enchimento ate a cota do pe fecha o fundo."""
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
    """poligono do piso 'name' sem os entalhes das escadas que chegam nele"""
    pieces = [floor_poly(name)]
    for nm, up, rect, zf, zt in stair_notches():
        if up != name:
            continue
        nxt = []
        for p in pieces:
            nxt += subtract_rect(p, rect)
        pieces = nxt
    return pieces


# ------------------------------------------------------------------ entrada / saida
TORII_IN = (0.0, 8.0)                          # torii de entrada (vao livre 12 x 14)
TORII_W, TORII_H = 12.0, 14.0
TORII_OUT = (-94.0, 586.0)                     # torii de saida (antes da cabeca da ponte de saida)
EXIT_START = (-95.0, 594.0)                    # ISLAND_EXIT_DemonSlayer (borda NO, cota T4)
EXIT_DEG = 105.0                               # rumo local da ponte de saida (15 graus a esquerda do eixo)
EXIT_W = 18.0
EXIT_BRIDGE_LEN = 56.0
PIER = (30.0, 30.0)                            # cabeceira de pedra (largura, fundo) do portao One Piece
GATE_OP_OFF = 12.0                             # portao One Piece a 12 do fim da ponte (como na SG)
ANCHOR_OP_OFF = 30.0                           # ancora One Piece na borda de fora da cabeceira
NEXT_AREA_ID = 5                               # One Piece ("mare")
NEXT_CLEAR_H = 22.0
SPAWN = (0.0, 22.0)                            # WORLD_ENTRY_DemonSlayer


def exit_dir():
    a = math.radians(EXIT_DEG)
    return (math.cos(a), math.sin(a))


def exit_point(d, v=0.0):
    """ponto a 'd' ao longo da ponte de saida (a partir de EXIT_START); v = afastamento lateral (+ = esquerda)"""
    ux, uy = exit_dir()
    return (EXIT_START[0] + ux * d - uy * v, EXIT_START[1] + uy * d + ux * v)


def gate_op_pos():
    return exit_point(EXIT_BRIDGE_LEN + GATE_OP_OFF)


def anchor_op_pos():
    return exit_point(EXIT_BRIDGE_LEN + ANCHOR_OP_OFF)


def gate_yaw():
    ux, uy = exit_dir()
    return math.atan2(uy, ux) - math.pi / 2


def pier_poly():
    pw, pd = PIER
    return [exit_point(EXIT_BRIDGE_LEN, -pw / 2), exit_point(EXIT_BRIDGE_LEN + pd, -pw / 2),
            exit_point(EXIT_BRIDGE_LEN + pd, pw / 2), exit_point(EXIT_BRIDGE_LEN, pw / 2)]


def bridge_list():
    """(nome, inicio (x, y, z), fim (x, y, z), largura): ponte de chegada (rampa 52,2 -> 54,2) e ponte de saida (T4)"""
    e0 = exit_point(0.0)
    e1 = exit_point(EXIT_BRIDGE_LEN)
    return [("Arrival", (PREV_X, PREV_Y, DECK), (0.0, 0.0, T0), DECK_W),
            ("ExitBridge", (e0[0], e0[1], T4), (e1[0], e1[1], T4), EXIT_W)]


# ------------------------------------------------------------------ clareira / mineracao
MINE_RECT = (-11.0, 180.0, 101.0, 330.0)       # MiningZone 112 x 150 (eixos locais), piso T1, ceu aberto
MINE_C = ((MINE_RECT[0] + MINE_RECT[2]) / 2, (MINE_RECT[1] + MINE_RECT[3]) / 2)
ORE_PLAN = [("SUPERLEGENDARY", 2), ("EPIC", 10), ("UNCOMMON", 22), ("COMMON", 38)]   # 72 marcadores
ORE_RADIUS = {"COMMON": 2.6, "UNCOMMON": 3.0, "EPIC": 3.4, "SUPERLEGENDARY": 4.4}
CLEAR_H = 12.0                                 # nada colidivel na zona ate piso + 12
WELL = (-30.0, 196.0)                          # poco coberto (borda oeste da clareira, fora da zona)
HOKORA = (-34.0, 214.0)                        # oratorio pequeno
CLEARING_TREES = [(-36.0, 152.0, 7.0), (110.0, 168.0, 8.0), (116.0, 352.0, 7.0)]   # 3 arvores largas (fora da zona+8)


def ore_points():
    """72 pontos (kind, i, x, y, raio): grade hexagonal no MAIOR passo (>= 10,4) que da a contagem, cantos recortados
    pela borda organica (elipse da zona), raridade pela profundidade (entrada sul = comum ... pe da subida = super)"""
    import random
    x0, y0, x1, y1 = MINE_RECT
    cx, cy = MINE_C
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    need = sum(n for _, n in ORE_PLAN)

    def ok(x, y):
        return ((x - cx) / (hx - 5.0)) ** 2 + ((y - cy) / (hy - 5.0)) ** 2 <= 1.08 and x0 + 5 <= x <= x1 - 5 \
            and y0 + 5 <= y <= y1 - 5

    def grid(step):
        rng = random.Random(4404)
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


# ------------------------------------------------------------------ forja (heroi) - (x0, y0, x1, y1, beiral, cumeeira) sobre o T4
FORGE = {
    "hall": (-22.0, 470.0, 22.0, 502.0, 13.0, 24.0),
    "workshop": (-68.0, 476.0, -36.0, 500.0, 12.0, 20.0),
    "tower": (30.0, 486.0, 44.0, 500.0, 50.0, 58.0),          # C8: corpo +50, chapeu ate +58
    "east": (52.0, 474.0, 74.0, 496.0, 9.0, 16.0),
}
CHIMNEY_TOP = T4 + 72.0                        # C8: chamine de pedra ate 152,2 (ponto mais alto da ilha)
CHIMNEY = (37.0, 493.0, 4.6)                   # (x, y, lado)
FORGE_YARD = (-60.0, 436.0, 84.0, 468.0)
FURNACE_MOUTH = (0.0, 470.0, 10.0, 9.0)        # (x, y face sul, largura, altura)
COAL_YARD = (-150.0, 372.0, -40.0, 440.0)
WHEEL = (92.0, 488.0, 20.0, 4.0)               # (x, y, diametro, largura); eixo leste-oeste, plano norte-sul
WHEEL_AXLE_Z = T4 + 11.0
SPRING = (100.0, 552.0, 104.0)                 # nascente na rocha de tras (x, y, z)
FLUME = [(100.0, 548.0), (98.0, 520.0), (94.0, 500.0)]
TAILRACE = [(96.0, 482.0), (110.0, 470.0), (116.0, 446.0), (116.0, 432.0)]
CASCADE = (116.0, 428.6, T4, T1)               # unica queda interna: terraco da forja -> lagoa (20)
POND = [(98, 382), (122, 378), (128, 396), (125, 426), (108, 427), (103, 412), (95, 396)]   # C6
POND_C = (112.0, 402.0)
CHANNEL = [(118.0, 380.0), (121.0, 340.0), (121.0, 300.0), (123.0, 262.0), (128.0, 236.0), (150.0, 226.0)]   # C5
FOOTBRIDGE = ((115.0, 300.0), (127.5, 300.0), 10.0)   # pontezinha sobre o canal (inicio, fim, largura)
SPILL = (154.0, 230.0)                         # saida da agua pela borda (ravina), unica queda para fora

# ------------------------------------------------------------------ summon (plato lateral leste, T3)
SUMMON_C, SUMMON_R = (176.0, 300.0), 24.0
SUMMON_TOWER = (184.0, 300.0)                  # torre AMS, frente para -X (oeste: clareira e entrada)
SUMMON_FACE_DEG = 180.0
SUMMON_INTERACT_D, SUMMON_PLAYER_D = 7.0, 16.0
SUMMON_SHELTER = (194.0, 324.0, 8.0, 6.0)      # abrigo pequeno de madeira escura (x, y, w, d)
WISTERIA = [(176.0, 270.0), (176.0, 330.0), (-104.0, 352.0), (52.0, 112.0)]   # os 4 acentos (2 summon, V6, bambuzal)

# ------------------------------------------------------------------ vila (6 construcoes) - (nome, tipo, x, y, w, d, rumo, cota, pisos)
HOUSES = [
    ("V1", "pavilhao (chaya)", -62.0, 128.0, 14.0, 10.0, 0.0, T1, 1),
    ("V2", "residencia (minka)", -112.0, 150.0, 22.0, 16.0, 0.0, T1, 1),
    ("V3", "oficina (afiador)", -100.0, 198.0, 18.0, 14.0, 0.0, T1, 1),
    ("V4", "armazem (kura)", -134.0, 252.0, 14.0, 12.0, 0.0, T2, 2),
    ("V5", "residencia 2", -118.0, 294.0, 22.0, 16.0, 0.0, T2, 2),
    ("V6", "casa principal", -116.0, 340.0, 30.0, 20.0, 0.0, T2, 1),
]
VILLAGE_GATE = (-38.0, 116.0)                  # portao de postes com lanternas (nao e torii)
VILLAGE_STREET = [(-30.0, 104.0), (-38.0, 116.0), (-52.0, 140.0), (-66.0, 172.0), (-78.0, 200.0), (-84.0, 214.0)]
VILLAGE_STREET_HIGH = [(-84.0, 232.0), (-82.0, 262.0), (-76.0, 300.0), (-70.0, 330.0), (-66.0, 342.0)]

# ------------------------------------------------------------------ rotas de navegacao (secao 30 do prompt + extras)
def _exit_tail():
    g = gate_op_pos()
    ux, uy = exit_dir()
    return [exit_point(1.5), exit_point(20.0), exit_point(44.0), exit_point(EXIT_BRIDGE_LEN + 2.0),
            (g[0] - ux * 7.0, g[1] - uy * 7.0)]


def routes():
    exit_walk = [(-104.0, 452.0), (-114.0, 496.0), (-110.0, 540.0), (-100.0, 572.0), (-97.0, 586.0)]
    return {
        "SHADOW_GATE->ENTRY": ([(0.0, -128.0), (0.0, -100.0), (0.0, -50.0), (0.0, 0.0), (0.0, 20.0)], DECK),
        "ENTRY->VILLAGE": ([(0.0, 20.0), (-12.0, 37.0), (-12.0, 56.0), (-20.0, 84.0), (-36.0, 112.0), (-56.0, 140.0),
                            (-70.0, 180.0), (-84.0, 213.0), (-84.0, 232.0), (-80.0, 270.0)], T0),
        "ENTRY->CLEARING": ([(0.0, 20.0), (-12.0, 37.0), (-12.0, 56.0), (-8.0, 96.0), (0.0, 140.0), (30.0, 200.0)], T0),
        "ENTRY->CLEARING (bambuzal)": ([(8.0, 22.0), (20.0, 28.0), (40.0, 58.0), (54.0, 98.0), (66.0, 132.0),
                                        (60.0, 170.0)], T0),
        "CLEARING->FORGE": ([(40.0, 255.0), (16.0, 350.0), (16.0, 375.0), (16.0, 401.0), (24.0, 408.0),
                             (30.0, 412.0), (30.0, 438.0), (10.0, 452.0), (0.0, 466.0)], T1),
        "CLEARING->SUMMON": ([(40.0, 255.0), (100.0, 300.0), (126.0, 300.0), (151.5, 300.0), (166.0, 300.0)], T1),
        "CLEARING->ONE_PIECE_GATE": ([(40.0, 255.0), (16.0, 350.0), (16.0, 401.0), (30.0, 412.0), (30.0, 438.0),
                                      (-40.0, 446.0)] + exit_walk + _exit_tail(), T1),
        "FORGE->ONE_PIECE_GATE": ([(0.0, 466.0), (-40.0, 446.0)] + exit_walk + _exit_tail(), T4),
        "SUMMON->CLEARING": ([(166.0, 300.0), (151.5, 300.0), (126.0, 300.0), (100.0, 290.0), (40.0, 255.0)], T3),
        "VILLAGE->FORGE (secundaria)": ([(-80.0, 270.0), (-66.0, 320.0), (-66.0, 341.0), (-66.0, 374.0),
                                         (-60.0, 410.0), (-20.0, 446.0)], T2),
        "CLEARING->VILLAGE_ALTA (VilaClareira)": ([(20.0, 284.0), (-40.0, 284.0), (-60.0, 284.0), (-90.0, 284.0)], T1),
        "FORGE->MIRANTE (patamar)": ([(0.0, 452.0), (30.0, 440.0), (30.0, 413.0), (10.0, 406.0), (-10.0, 402.0)], T4),
    }


def gate_open_route():
    g = gate_op_pos()
    ux, uy = exit_dir()
    return [(g[0] - ux * 7.0, g[1] - uy * 7.0), g, (g[0] + ux * 12.0, g[1] + uy * 12.0),
            exit_point(EXIT_BRIDGE_LEN + ANCHOR_OP_OFF - 1.0)]


# ------------------------------------------------------------------ cameras de QA (do plano, ds_cams.py)
def cams():
    g = gate_op_pos()
    e = exit_point(20.0)
    return {
        "CAM_DS_Entry": ((8.0, -45.0, 62.0), (-4.0, 90.0, 66.0), 22),
        "CAM_DS_Front": ((40.0, -260.0, 220.0), (20.0, 300.0, 70.0), 28),
        "CAM_DS_Left": ((-460.0, 300.0, 230.0), (20.0, 300.0, 70.0), 30),
        "CAM_DS_Right": ((520.0, 280.0, 230.0), (20.0, 300.0, 70.0), 30),
        "CAM_DS_Back": ((-20.0, 900.0, 260.0), (20.0, 280.0, 70.0), 30),
        "CAM_DS_BirdEye": ((25.0, 300.0, 1100.0), (25.0, 302.0, 60.0), 32),
        "CAM_DS_Clearing": ((24.0, 404.0, T3 + 10.0), (40.0, 200.0, T1), 24),
        "CAM_DS_Village": ((-20.0, 150.0, 100.0), (-110.0, 260.0, 68.0), 26),
        "CAM_DS_Forge": ((30.0, 300.0, 96.0), (10.0, 480.0, 102.0), 26),
        "CAM_DS_Summon": ((70.0, 230.0, 84.0), (180.0, 300.0, 92.0), 28),
        "CAM_DS_OnePieceGate": ((-110.0, 548.0, 92.0), (g[0], g[1], 90.0), 24),
        "CAM_DS_PlayerHeight_Entry": ((0.0, -40.0, DECK + 1.2 + EYE), (0.0, 120.0, 64.0), 22),
        "CAM_DS_PlayerHeight_Clearing": ((-20.0, 140.0, T1 + EYE), (50.0, 280.0, 63.0), 22),
        "CAM_DS_PlayerHeight_Village": ((-44.0, 130.0, T1 + EYE), (-84.0, 210.0, 66.0), 22),
        "CAM_DS_PlayerHeight_Forge": ((16.0, 360.0, T1 + EYE), (10.0, 480.0, 96.0), 22),
        "CAM_DS_PlayerHeight_Summon": ((112.0, 300.0, T1 + EYE), (184.0, 300.0, 82.0), 22),
        "CAM_DS_PlayerHeight_OnePieceGate": ((e[0], e[1], T4 + EYE), (g[0], g[1], T4 + 9.0), 24),
        # referencias aprovadas: enquadramento refeito na onda 0 para casar com as imagens (ilha mais longa que nas refs)
        "CAM_DS_Ref_01": ((25.0, -240.0, 400.0), (25.0, 250.0, 40.0), 24),     # sul, alta, no eixo
        "CAM_DS_Ref_02": ((300.0, -110.0, 320.0), (30.0, 260.0, 40.0), 24),    # sudeste: summon a direita, entrada embaixo-esq
        "CAM_DS_Ref_03": ((0.0, 720.0, 300.0), (25.0, 300.0, 40.0), 24),       # norte: forja na frente, entrada ao fundo
        "CAM_DS_Ref_04": ((-120.0, -230.0, 420.0), (30.0, 260.0, 30.0), 24),   # sul-sudoeste alta e aberta
        "CAM_DS_Ref_05": ((-190.0, -120.0, 210.0), (40.0, 230.0, 60.0), 26),   # sudoeste baixa: torii na frente, vila a esq
    }


PLAYER_CAMS = [k for k in cams() if "PlayerHeight" in k]
REF_CAMS = ["CAM_DS_Ref_%02d" % i for i in range(1, 6)]
