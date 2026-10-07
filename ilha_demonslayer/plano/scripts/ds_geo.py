# ds_geo.py - geometria do PLANO da Ilha 4 DEMON SLAYER (Monte Natagumo). So leitura do projeto: importa as plantas
# das Ilhas 1, 2 e 3 (via ilha_shadowgarden/renders/plano_mestre/scripts/geo.py) para medir folgas.
# Constantes daqui = proposta do ds_layout.py da Onda 0 (o agente da Onda 0 copia e trava).
#
# CONVENCOES (iguais ao sg_layout):
#   1 BU = 1 stud; Z absoluto = Y do Roblox.
#   Referencial LOCAL: origem = centro da soleira do TORII DE ENTRADA na borda sul da ilha;
#   +Y = eixo longitudinal (entrada -> trilha -> clareira -> subida -> forja -> saida), +X = direita de quem chega
#   (bambuzal, summon, roda d'agua), -X = esquerda (vila, saida NO).
#   Mundo (Blender do lobby): W4 = T(ancora_SG) . Rz(WORLD_YAW_DEG) . T(-WORLD_FROM_PREV_local)
#   Roblox = (x_mundo, z, -y_mundo).
import sys, math, os
sys.dont_write_bytecode = True        # nada de __pycache__ nas pastas das outras ilhas (so leitura)
ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up"
sys.path.insert(0, os.path.join(ROOT, "ilha_shadowgarden", "renders", "plano_mestre", "scripts"))
import geo as G          # i1_polys, i2_polys, SG (sg_layout v4), LOBBY, poly_dist, ribbon, circle, rect, pip

# ------------------------------------------------------------------ encaixe (ancora REAL lida no Studio = sg_layout)
A_RBX = (-1534.4934, 52.2, 962.4429)          # ISLAND_NEXT_ANCHOR_DemonSlayer (Roblox)
A_FWD = (-0.7660, 0.0, 0.6428)                # frente da ancora (Roblox)
A_W = 18.0
GATE_DS_RBX = (-1513.04, 52.2, 944.45)        # portao Demon Slayer aprovado (fica na ilhota da Shadow Garden)
WORLD_YAW_DEG = 130.0                          # local +Y -> Roblox (-0,766; 0; 0,643) = frente da ancora (ponte reta)
BRIDGE_IN_LEN = 100.0                          # ancora -> soleira do torii de entrada (folga de 188 ate a borda da SG)
PREV = (0.0, -BRIDGE_IN_LEN)                   # WORLD_FROM_PREV local

# ------------------------------------------------------------------ cotas (Z absoluto = Y Roblox)
DECK = 52.2          # tabuleiro na ancora (= P3 da Shadow Garden)
T0 = 54.2            # patio do torii (a ponte sobe 2 em 100: rampa de 1,1 grau, sem degrau)
T1 = 60.2            # trilha alta, vila baixa e CLAREIRA (piso da MiningZone)
T2 = 66.2            # vila alta
T3 = 70.2            # plato do summon e patamar do meio da subida
T4 = 80.2            # terraco da forja, caminho de saida, ponte de saida e ancora One Piece
SEA_CLOUD = -60.0    # mar de nuvens (cliente), so visual
RISE_MAX, TREAD_MIN = 0.8, 1.7
LEVELS = (DECK, T0, T1, T2, T3, T4)

# ------------------------------------------------------------------ contorno (topo do penhasco), anti-horario
RIM = [(-18, -2), (18, -2), (36, 6), (58, 22), (72, 48), (76, 84), (86, 112), (108, 128), (132, 140), (144, 168),
       (150, 196), (148, 214), (158, 226), (184, 238), (204, 258), (212, 290), (206, 322), (188, 342), (160, 352),
       (140, 372), (136, 404), (134, 440), (132, 478), (126, 516), (108, 548), (80, 572), (40, 586), (0, 590),
       (-40, 584), (-70, 586), (-92, 600), (-108, 594), (-120, 572), (-130, 540), (-138, 500), (-146, 460),
       (-152, 420), (-158, 380), (-160, 340), (-162, 300), (-160, 260), (-152, 222), (-146, 186), (-138, 150),
       (-120, 120), (-92, 104), (-64, 92), (-56, 64), (-52, 36), (-36, 12)]

# ------------------------------------------------------------------ patamares andaveis (prioridade maior manda)
ENTRY_COURT = [(-22, 0), (22, 0), (28, 14), (26, 34), (8, 40), (-18, 38), (-26, 20)]                      # T0
TRAIL_T1 = [(-28, 56), (6, 56), (14, 80), (10, 110), (4, 130), (-40, 130), (-44, 96), (-36, 70)]       # T1
BAMBOO_RAMP = [(20, 28), (40, 58), (54, 98), (66, 132)]                                                  # T0 -> T1
CLEARING = [(-40, 132), (0, 126), (36, 132), (68, 140), (98, 154), (118, 178), (128, 212), (126, 252),
            (122, 292), (126, 336), (130, 380), (116, 406), (92, 402), (76, 382), (54, 380), (14, 378), (-22, 368), (-42, 344),
            (-46, 304), (-44, 256), (-42, 212), (-40, 172)]                                               # T1
VILLAGE_LOW = [(-40, 112), (-40, 214), (-74, 226), (-150, 226), (-146, 186), (-138, 150), (-120, 122),
               (-92, 108), (-64, 100)]                                                                    # T1
VILLAGE_HIGH = [(-150, 226), (-74, 226), (-56, 250), (-50, 300), (-54, 344), (-60, 362), (-158, 362),
                (-160, 300), (-158, 260)]                                                                 # T2
SUMMON_PLAT = [(150, 270), (176, 264), (200, 274), (206, 300), (198, 326), (176, 336), (150, 330)]        # T3
CLIMB_LAND = (-14, 400, 46, 414)                                                                          # T3 (x0,y0,x1,y1)
FORGE_TERR = [(-152, 380), (-60, 372), (-30, 392), (40, 434), (118, 428), (130, 440), (128, 478),
              (118, 512), (60, 520), (-60, 524), (-104, 540), (-120, 528), (-136, 500), (-146, 460),
              (-150, 420)]                                                                               # T4
EXIT_PATH = [(-104, 452), (-114, 496), (-110, 540), (-100, 572), (-94, 590)]                             # T4

# ------------------------------------------------------------------ elementos
TORII_IN = (0.0, 8.0)                          # torii de entrada (vao livre 12 x 14)
TORII_OUT = (-94.0, 586.0)                     # torii de saida (na cabeca da ponte de saida)
EXIT_START = (-95.0, 594.0)                    # ISLAND_EXIT_DemonSlayer (borda NO, cota T4)
EXIT_DEG = 105.0                               # rumo local da ponte de saida (15 graus a esquerda do eixo)
EXIT_BRIDGE_LEN = 56.0
PIER = (30.0, 30.0)                            # cabeceira de pedra (largura, fundo) do portao One Piece
GATE_OP_OFF = 12.0                             # portao One Piece a 12 do fim da ponte (como na SG)
ANCHOR_OP_OFF = 30.0                           # ancora One Piece na borda de fora da cabeceira
NEXT_AREA_ID = 5                               # One Piece ("mare")

MINE_RECT = (-11.0, 180.0, 101.0, 330.0)       # MiningZone 112 x 150 (eixos locais)
MINE_C = ((MINE_RECT[0] + MINE_RECT[2]) / 2, (MINE_RECT[1] + MINE_RECT[3]) / 2)
ORE_PLAN = [("SUPERLEGENDARY", 2), ("EPIC", 10), ("UNCOMMON", 22), ("COMMON", 38)]   # 72 marcadores
SUMMON_C, SUMMON_R = (176.0, 300.0), 24.0
SUMMON_TOWER = (184.0, 300.0)                  # frente para -X (oeste: clareira, entrada)
FORGE = {   # (x0, y0, x1, y1, beiral, cumeeira) relativo a T4
    "hall": (-22.0, 470.0, 22.0, 502.0, 13.0, 24.0),
    "workshop": (-68.0, 476.0, -36.0, 500.0, 12.0, 20.0),
    "tower": (30.0, 486.0, 44.0, 500.0, 44.0, 60.0),
    "east": (52.0, 474.0, 74.0, 496.0, 9.0, 16.0),
}
FORGE_YARD = (-60.0, 436.0, 84.0, 468.0)
FURNACE_MOUTH = (0.0, 470.0, 10.0, 9.0)        # (x, y face sul, largura, altura)
WHEEL = (92.0, 488.0, 20.0, 4.0)               # (x, y, diametro, largura); eixo leste-oeste, plano norte-sul
SPRING = (100.0, 552.0, 104.0)                 # nascente na rocha de tras (x, y, z)
FLUME = [(100.0, 548.0), (98.0, 520.0), (94.0, 500.0)]
TAILRACE = [(96.0, 482.0), (110.0, 470.0), (116.0, 446.0), (118.0, 432.0)]
CASCADE = (118.0, 430.0, T4, T1)               # unica queda interna: terraco da forja -> lagoa (20)
POND = (110.0, 392.0, 14.0)
CHANNEL = [(122.0, 380.0), (128.0, 340.0), (128.0, 300.0), (130.0, 262.0), (134.0, 236.0), (150.0, 226.0)]
SPILL = (154.0, 230.0)                         # saida da agua pela borda (ravina), unica queda para fora
HOUSES = [  # (nome, tipo, x, y, largura, fundo, rumo da frente (graus), cota)
    ("V1", "pavilhao (chaya)", -62.0, 128.0, 14.0, 10.0, 0.0, T1),
    ("V2", "residencia (minka)", -112.0, 150.0, 22.0, 16.0, 0.0, T1),
    ("V3", "oficina (afiador)", -100.0, 198.0, 18.0, 14.0, 0.0, T1),
    ("V4", "armazem (kura)", -134.0, 252.0, 14.0, 12.0, 0.0, T2),
    ("V5", "residencia 2", -118.0, 294.0, 22.0, 16.0, 0.0, T2),
    ("V6", "casa principal", -116.0, 340.0, 30.0, 20.0, 0.0, T2),
]
WELL = (-30.0, 196.0)
STAIRS = [  # (nome, pe (x, y), rumo, largura, n, espelho, piso, z do pe)
    ("Trilha", (-12.0, 40.0), 90.0, 12.0, 8, 0.75, 1.8, T0),
    ("VilaAlta", (-84.0, 216.0), 90.0, 10.0, 8, 0.75, 1.8, T1),
    ("VilaClareira", (-44.0, 284.0), 180.0, 8.0, 8, 0.75, 1.8, T1),
    ("Summon", (128.0, 300.0), 0.0, 12.0, 13, 10.0 / 13, 1.75, T1),
    ("SubidaA", (16.0, 377.0), 90.0, 16.0, 13, 10.0 / 13, 1.8, T1),
    ("SubidaB", (30.0, 414.0), 90.0, 14.0, 13, 10.0 / 13, 1.8, T3),
    ("OesteForja", (-66.0, 342.0), 90.0, 10.0, 18, 14.0 / 18, 1.75, T2),
]
ROUTES = {   # waypoints (x, y) de cada rota de navegacao da secao 30 do prompt
    "SHADOW_GATE->ENTRY": [(0.0, -128.0), (0.0, -100.0), (0.0, 0.0), (0.0, 20.0)],
    "ENTRY->VILLAGE": [(0.0, 20.0), (-12.0, 38.0), (-12.0, 56.0), (-20.0, 84.0), (-36, 112), (-56.0, 140.0),
                       (-70.0, 180.0), (-84.0, 214.0), (-84.0, 232.0), (-80.0, 270.0)],
    "ENTRY->CLEARING": [(0.0, 20.0), (-12.0, 38.0), (-12.0, 56.0), (-8.0, 96.0), (0.0, 140.0), (30.0, 200.0)],
    "ENTRY->CLEARING (bambuzal)": [(8.0, 22.0), (20.0, 28.0), (40.0, 58.0), (54.0, 98.0), (66.0, 132.0), (60.0, 170.0)],
    "CLEARING->FORGE": [(40.0, 255.0), (16.0, 350.0), (16.0, 375.0), (16.0, 400.0), (24.0, 408.0), (30.0, 412.0),
                        (30.0, 438.0), (10.0, 452.0), (0.0, 466.0)],
    "CLEARING->SUMMON": [(40.0, 255.0), (100.0, 300.0), (126.0, 300.0), (150.0, 300.0), (166.0, 300.0)],
    "CLEARING->ONE_PIECE_GATE": [(40.0, 255.0), (16.0, 350.0), (16.0, 400.0), (30.0, 412.0), (30.0, 438.0),
                                 (-40.0, 446.0), (-104.0, 452.0), (-114.0, 496.0), (-110.0, 540.0),
                                 (-100.0, 572.0), (-95.0, 594.0)],
    "FORGE->ONE_PIECE_GATE": [(0.0, 466.0), (-40.0, 446.0), (-104.0, 452.0), (-114.0, 496.0), (-110.0, 540.0),
                              (-100.0, 572.0), (-95.0, 594.0)],
    "SUMMON->CLEARING": [(166.0, 300.0), (150.0, 300.0), (126.0, 300.0), (100.0, 290.0), (40.0, 255.0)],
    "VILLAGE->FORGE (secundaria)": [(-80.0, 270.0), (-66.0, 320.0), (-66.0, 342.0), (-66.0, 374.0),
                                    (-60.0, 410.0), (-20.0, 446.0)],
}

# ------------------------------------------------------------------ transformacoes
_ax, _ay = A_RBX[0], -A_RBX[2]                  # ancora em Blender XY


def to_bl(x, y):
    a = math.radians(WORLD_YAW_DEG)
    lx, ly = x - PREV[0], y - PREV[1]
    return (_ax + lx * math.cos(a) - ly * math.sin(a), _ay + lx * math.sin(a) + ly * math.cos(a))


def rbx(x, y):
    bx, by = to_bl(x, y)
    return (bx, -by)


def dir_rbx(dx, dy):
    a = math.radians(WORLD_YAW_DEG)
    wx, wy = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return (wx, -wy)


def exit_dir():
    a = math.radians(EXIT_DEG)
    return (math.cos(a), math.sin(a))


def exit_point(d):
    ux, uy = exit_dir()
    return (EXIT_START[0] + ux * d, EXIT_START[1] + uy * d)


def stair_top(nm):
    for n, (fx, fy), deg, w, k, rise, tread, z in STAIRS:
        if n == nm:
            a = math.radians(deg)
            return (fx + math.cos(a) * tread * k, fy + math.sin(a) * tread * k, z + rise * k)


def ore_points():
    """72 pontos: grade hexagonal centrada no MAIOR passo (>= 10,4) que da a contagem, cantos recortados pela borda
    organica (elipse 0,94 da zona), raridade pela profundidade (entrada sul = comum ... pe da subida = super)"""
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
            pts.append((kind, k + 1, round(cand[i][0], 2), round(cand[i][1], 2)))
            i += 1
    return pts, step


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def area(P):
    return abs(sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))) / 2


def world_polys():
    T = lambda pts: [rbx(*p) for p in pts]
    ux, uy = exit_dir()
    eb = [exit_point(0.0), exit_point(EXIT_BRIDGE_LEN)]
    pw, pd = PIER
    c0 = exit_point(EXIT_BRIDGE_LEN)
    c1 = exit_point(EXIT_BRIDGE_LEN + pd)
    vx, vy = -uy, ux
    pier = [(c0[0] + vx * pw / 2, c0[1] + vy * pw / 2), (c1[0] + vx * pw / 2, c1[1] + vy * pw / 2),
            (c1[0] - vx * pw / 2, c1[1] - vy * pw / 2), (c0[0] - vx * pw / 2, c0[1] - vy * pw / 2)]
    return {"rim": T(RIM), "bridge_in": T(G.ribbon([PREV, (0.0, 0.0)], 9.0)), "bridge_out": T(G.ribbon(eb, 9.0)),
            "pier": T(pier)}


def anchor_op():
    ux, uy = exit_dir()
    p = exit_point(EXIT_BRIDGE_LEN + ANCHOR_OFF_OP())
    return rbx(*p), dir_rbx(ux, uy)


def ANCHOR_OFF_OP():
    return ANCHOR_OP_OFF


def gate_op():
    return exit_point(EXIT_BRIDGE_LEN + GATE_OP_OFF)


def sg_polys():
    s = G.i3_old_polys()          # nome antigo do geo.py: e a planta ATUAL (sg_layout v4)
    return s
