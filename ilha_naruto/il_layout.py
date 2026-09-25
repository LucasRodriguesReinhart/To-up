# il_layout - planta TRAVADA da Ilha 1 (Naruto / Vila da Folha). 1 BU = 1 stud, Z para cima.
# Referencial LOCAL de projeto (o das referencias): origem = centro do fosso; +Y = norte (vila), +X = leste (saida),
# -Y = sul (entrada, lobby). Cotas Z ABSOLUTAS = Y do Roblox.
# Mundo (Blender do lobby): world = Rz(180) * local + (0, -420, 0)  ->  Roblox = (-x_local, z, 420 + y_local).
#   A ponta sul da ponte de chegada (y -198) cai em Roblox z 222 = ponta do patamar da ponte do lobby (fm_terrain_isles).
import math

WORLD_YAW_DEG = 180.0
WORLD_OFFSET = (0.0, -420.0, 0.0)       # Blender do lobby (x, y, z) depois do giro

# ------------------------------------------------------------------ niveis
G = 6.2           # ponte do lobby, praca do portao, gramados S/SE/SO, vale do riacho
RING = 10.2       # anel pavimentado
PIT = 3.2         # piso do fosso
T1 = 16.2         # terraco em C (summon O, vila baixa N, saida NE)
T2 = 22.2         # terraco do salao principal
CLIFF_TOP = 72.0  # plato do paredao do fundo
SEA = -110.0      # mar (so visual)
STREAM_BED = 3.4  # leito do riacho leste
STREAM_WATER = 4.6

RISE = 0.8        # espelho padrao
TREAD = 1.7       # piso padrao

# ------------------------------------------------------------------ fosso e anel
PIT_R = 60.0
RING_R0 = 60.0
RING_R1 = 82.0
RING_WALL_T = 2.0         # muro de arrimo externo do anel (r 82..84) nas faces que dao para G
FENCE_R = 60.9            # cerca da borda do fosso (em cima do anel)
PIT_STAIR_W = 10.0        # escadas N e S para dentro do fosso
PIT_STAIR_N = 9           # 9 x 0.778 = 7.0
PIT_RAMP_W = 8.0          # rampas de madeira L e O (tangentes ao muro); 8 desde a rodada 2 (6 virava fila unica)
PIT_RAMP_A = (-22.0, 12.0)    # graus: topo e pe da rampa leste (a oeste e o espelho)
CORE_R = 10.0             # rochedo central (minerio raro)
DERRICKS = [50.0, 130.0, 230.0, 310.0]   # torres de madeira (angulo, r 50)
DERRICK_R = 50.0
LANE_HW = 4.0             # corredores livres: pe das escadas/rampas -> rochedo central

# ------------------------------------------------------------------ entrada
BRIDGE_W = 24.0           # igual a ponte do lobby (ISLES_GATE_HW 12)
LOBBY_Y = -198.0          # WORLD_FROM_LOBBY (ponta do patamar do lobby)
ISLAND_S_Y = -118.0       # borda da ilha onde a ponte encosta
GATE_Y = -110.0           # eixo do portao principal
GATE_OPEN_W = 20.0
GATE_OPEN_H = 18.0
GATE_W = 52.0
GATE_D = 8.0
LIONS = [(-20.0, -116.0), (20.0, -116.0)]   # rodada 2: a frente das alas, nas quinas da praca junto a ponte
ENTRY_PLAZA = (-16.0, -106.0, 16.0, -92.0)     # x0, y0, x1, y1 (piso G)
ENTRY_STAIR_Y0 = -92.0    # 5 degraus G -> anel (+4)
ENTRY_STAIR_N = 5
ENTRY_STAIR_W = 16.0

# ------------------------------------------------------------------ terraco T1 (C que abraca o norte do anel)
T1_WALL_R = 88.0          # muro anel -> T1 (arco de 20 a 160 graus, alem disso o terraco do summon)
T1_WALL_A = (26.0, 200.0)
T2_WALL_Y = 126.0         # muro T1 -> T2 (reto)
T2_WALL_X = (-78.0, 78.0)
VILLAGE_STAIRS = {        # escadas anel -> T1 (angulo em graus sobre o arco T1_WALL_R, largura)
    "C": (90.0, 12.0), "NW": (128.0, 9.0), "NE": (52.0, 12.0)}   # NE = caminho da progressao (saida): 12
# escadas laterais gramado (G) -> anel, dos 2 lados do portao (as refs 14/18 tem): radiais, pe em r 92,5, topo r 84
SIDE_STAIRS = [(247.0, 10.0), (293.0, 10.0)]          # (angulo, largura) - 5 espelhos de 0,8, piso 1,7
# escada vale leste (G) -> T1, encostada no muro radial de 26 graus pelo lado do vale: liga o moinho a saida
VALLEY_STAIR = dict(foot=(82.0, 33.0), top=(101.0, 43.0), width=8.0, n=13)
T2_STAIR_W = 12.0         # escada central T1 -> T2 (y 116..128)
T2_EXIT_CUT = -14.85      # o T2 so existe onde x - y <= isto (recorte paralelo a ponte de saida, 10,5 do eixo)
T2_STAIR_Y0 = 116.0

# ------------------------------------------------------------------ vila
MAIN_HALL = (0.0, 160.0, 22.0)        # x, y, raio (entravel, porta ao sul)
BLUE_W = (-58.0, 154.0, 14.0)         # loja de armas ninja (entravel, porta ao sul)
BLUE_E = (58.0, 154.0, 14.0)          # prédio redondo sem porta (torre de agua / deposito)
RAMEN = (-38.0, 107.0, 18.0, 12.0, 0.0)   # x, y, largura, fundo, yaw (frente para o sul = anel)
HOUSES_T1 = [(38.0, 107.0, 16.0, 12.0, 0.0, "Roof_Green"), (-84.0, 110.0, 16.0, 13.0, 0.0, "Roof_Terracotta"),
             (84.0, 108.0, 16.0, 13.0, 0.0, "Roof_Terracotta"), (-112.0, 84.0, 14.0, 12.0, 0.0, "Roof_Terracotta")]
HOUSES_T2 = [(-98.0, 160.0, 16.0, 14.0, 0.0, "Roof_Terracotta"), (96.5, 149.5, 13.5, 12.0, 0.0, "Roof_Green"),
             (-126.0, 136.0, 13.0, 12.0, 0.0, "Roof_Green")]
BACK_CLIFF_Y = 186.0      # pe do paredao (T2) -> topo em CLIFF_TOP
BACK_FALLS = [(-80.0, 188.0), (80.0, 188.0), (-30.0, 188.0)]   # a 3a (rodada 2) cai num poco atras do salao
CANAL_MID = [(-30.0, 177.0), (-44.0, 179.0), (-60.0, 179.5), (-72.0, 178.0)]  # poco da 3a queda -> poco NO (-80)

# ------------------------------------------------------------------ summon (O-NO, nivel T1)
SUMMON_C = (-120.0, 22.0)
SUMMON_R = 28.0
SUMMON_TOWER = (-133.0, 36.0)
SUMMON_FACE_DEG = -35.0       # frente da torre (ESE -> para o anel e a entrada)
SUMMON_STAIR = (-83.0, 16.0, 190.0, 12.0)   # pe (x, y) no anel, rumo (graus), largura: anel -> T1

# ------------------------------------------------------------------ leste (riacho, roda, moinho)
# Agua (revisao da integracao): a cascata T2 -> vale em y 126 caia DENTRO da faixa da ponte de saida. Agora:
#   sistema NE: queda do paredao (80,188) -> poco no T2 -> canal STREAM_T2 -> queda pela borda NE (NE_FALL), ao lado
#               da ponte (vista da travessia), sem cruzar a faixa dela;
#   sistema do vale: aqueduto subterraneo -> BICA no muro x=108 (SPOUT, ao sul da ponte) -> STREAM (vale) -> roda
#               d'agua -> ponte em arco -> queda pela borda SE.
STREAM_T2 = [(86.5, 177.4), (104.6, 168.2), (112.4, 152.0), (116.6, 143.0)]
NE_FALL = (119.2, 141.2)           # borda NE (contorno entre (122,124) e (116,160)); a queda comeca aqui
SPOUT = (108.0, 80.0, T1 - 3.2)    # bica (x da face do muro, y, cota da boca); cai numa bacia no nivel G
STREAM = [(110.5, 80.0), (113.5, 70.0), (116.0, 60.0), (118.0, 20.0), (117.0, -20.0), (113.0, -42.0),
          (106.0, -60.0), (102.0, -76.0)]
STREAM_W = 9.0
WHEEL = (118.0, 12.0, 11.0)   # x, y, raio (eixo L-O: a roda gira no plano YZ)
MILL = (100.0, 12.0, 14.0, 18.0)   # moinho de minerio / posto do minerador (x, y, largura X, fundo Y) no nivel G
MILL_STAIR = (82.5, 12.0, 0.0, 8.0)  # anel -> G (desce para leste)
FOOTBRIDGE = (115.0, -40.0)
EAST_HOUSES = [(134.0, -26.0, 14.0, 12.0, 0.0, "Roof_Terracotta"), (136.0, 36.0, 13.0, 12.0, 0.0, "Roof_Green")]

# ------------------------------------------------------------------ saida (NE)
EXIT_START = (96.0, 96.0)     # borda NE do T1 (ISLAND_EXIT_Naruto)
EXIT_DEG = 45.0               # rumo da ponte de saida
EXIT_W = 18.0                 # largura padrao da interface entre ilhas
EXIT_Z = T1
EXIT_BRIDGE_LEN = 96.0        # ate a ilhota do portao
GATE_ISLET_R = 23.0
GATE_DB_OFF = 12.0            # distancia do inicio da ilhota ate o eixo do portao
ANCHOR_OFF = 40.0             # distancia do inicio da ilhota ate a ISLAND_NEXT_ANCHOR (borda da plataforma, d=136)
# portao de compra padrao (familia): vao livre e altura (todos iguais)
PG_OPEN_W = 16.0
PG_OPEN_H = 18.0
PG_DEPTH = 10.0


def exit_dir():
    a = math.radians(EXIT_DEG)
    return (math.cos(a), math.sin(a))


def exit_point(d):
    """ponto no eixo da saida a d studs do inicio da ponte"""
    ux, uy = exit_dir()
    return (EXIT_START[0] + ux * d, EXIT_START[1] + uy * d)


def islet_center():
    return exit_point(EXIT_BRIDGE_LEN + GATE_ISLET_R - 4.0)


def gate_db_pos():
    return exit_point(EXIT_BRIDGE_LEN + GATE_DB_OFF)


def anchor_pos():
    return exit_point(EXIT_BRIDGE_LEN + ANCHOR_OFF)


# ------------------------------------------------------------------ contorno da ilha (topo do penhasco, anti-horario)
ISLAND_RIM = [(-24.0, -118.6), (24.0, -118.6), (35.0, -114.5), (56.0, -101.0), (76.0, -88.0), (96.0, -80.0),
              (112.0, -64.0), (130.0, -44.0), (144.0, -12.0), (150.0, 26.0), (146.0, 64.0), (132.0, 98.0),
              (122.0, 124.0), (116.0, 160.0), (100.0, 190.0), (64.0, 204.0), (0.0, 208.0), (-64.0, 204.0),
              (-104.0, 190.0), (-134.0, 160.0), (-150.0, 120.0), (-158.0, 76.0), (-158.0, 30.0),
              (-148.0, -6.0), (-126.0, -36.0), (-96.0, -62.0), (-76.0, -86.0), (-52.0, -104.0), (-35.0, -114.5)]
# prateleira de penhasco mais baixa em volta (lobulos da borda, so visual)
SHELF_Z = G - 9.0


def shelf_rim(seed=5):
    """contorno da prateleira: a borda da ilha deslocada para fora 9..20 studs, irregular (lobulos)"""
    import random
    rng = random.Random(seed)
    pts = ISLAND_RIM
    n = len(pts)
    out = []
    for i in range(n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        tx, ty = x2 - x0, y2 - y0
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = ty / ln, -tx / ln          # normal para fora (contorno anti-horario)
        d = rng.uniform(9.0, 20.0)
        if y1 < -112.0 and abs(x1) < 20.0:
            d = 7.0                          # sob a ponte de chegada: a prateleira nao avanca
        out.append((x1 + nx * d, y1 + ny * d))
        # lobulo intermediario
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        ex, ey = x2 - x1, y2 - y1
        le = math.hypot(ex, ey) or 1.0
        d2 = rng.uniform(6.0, 22.0)
        out.append((xm + ey / le * d2, ym - ex / le * d2))
    return out


SHELF_RIM = shelf_rim()

# ------------------------------------------------------------------ zonas de piso (poligonos no plano, usados pelo terreno)
# T1: tudo ao norte do arco T1_WALL_R entre 26 e 154 graus, ate o muro T2; + o terraco do summon a oeste
def zone_of(x, y):
    """nivel do terreno em (x, y) (fora de pontes/escadas). Retorna uma das cotas acima."""
    r = math.hypot(x, y)
    if r <= PIT_R:
        return PIT
    if r <= RING_R1:
        return RING
    ang = math.degrees(math.atan2(y, x)) % 360.0
    in_c = T1_WALL_A[0] <= ang <= T1_WALL_A[1]
    if in_c and r <= T1_WALL_R:
        return RING               # faixa do anel ao pe do muro T1
    if y >= BACK_CLIFF_Y:
        return CLIFF_TOP
    if y >= T2_WALL_Y and x <= 118.0 and (x - y) <= T2_EXIT_CUT:
        return T2
    if x >= 108.0:
        return G                  # vale do riacho
    if in_c:
        return T1
    return G


# ------------------------------------------------------------------ minerio: pontos reais (gerados e travados aqui)
ORE_KINDS = [("COMMON", 2.6), ("UNCOMMON", 3.0), ("EPIC", 3.4), ("SUPERLEGENDARY", 4.4)]


def _blocked(x, y, clear):
    r = math.hypot(x, y)
    if r < CORE_R + 3.0 + clear or r > PIT_R - 4.0 - clear:
        return True
    # corredores livres do rochedo central ate o pe de cada acesso: escadas N/S e pe das rampas L/O
    if abs(x) < PIT_STAIR_W / 2 + 1.2 + clear and abs(y) > PIT_R - PIT_STAIR_N * 1.6 - 1.0 - clear:
        return True               # escadas N/S do fosso
    for fx, fy in lane_ends():
        ln = math.hypot(fx, fy)
        t = max(0.0, min(1.0, (x * fx + y * fy) / (ln * ln)))
        if math.hypot(x - fx * t, y - fy * t) < LANE_HW + clear and t * ln > CORE_R:
            return True
    for a in DERRICKS:
        dx = x - DERRICK_R * math.cos(math.radians(a))
        dy = y - DERRICK_R * math.sin(math.radians(a))
        if math.hypot(dx, dy) < 6.5 + clear:
            return True
    # pe das rampas L/O (patamar livre)
    for s in (-1, 1):
        a = math.radians(PIT_RAMP_A[1]) if s > 0 else math.pi - math.radians(PIT_RAMP_A[1])
        fx, fy = (PIT_R - 5.0) * math.cos(a), (PIT_R - 5.0) * math.sin(a)
        if math.hypot(x - fx, y - fy) < 8.0 + clear:
            return True
    return False


def lane_ends():
    """pe de cada acesso ao fosso (escadas N/S e rampas L/O)"""
    rp = PIT_R - PIT_RAMP_W / 2 - 0.5
    a = math.radians(PIT_RAMP_A[1])
    return [(0.0, PIT_R - 14.0), (0.0, -(PIT_R - 14.0)), (rp * math.cos(a), rp * math.sin(a)),
            (-rp * math.cos(a), rp * math.sin(a))]


def ore_points():
    """lista (kind, i, x, y, raio) - espacamento >= 2*raio + 3 (varios jogadores minerando lado a lado)"""
    import random
    rng = random.Random(1101)
    plan = [("SUPERLEGENDARY", [(CORE_R + 6.0, a) for a in (45.0, 225.0)]),
            ("EPIC", [(24.0, a) for a in (20.0, 65.0, 115.0, 160.0, 200.0, 245.0, 295.0, 340.0)]),
            ("UNCOMMON", [(34.0 + (i % 2) * 4.0, 11.25 + i * 22.5) for i in range(16)]),
            ("COMMON", [(46.0 + (i % 3) * 2.5, 5.0 + i * 11.25) for i in range(32)])]
    rad = dict(ORE_KINDS)
    pts = []
    for kind, spots in plan:
        n = 0
        for r, a in spots:
            ok = None
            for t in range(80):
                rr = r + rng.uniform(-2.5, 2.5) * (1 if t else 0)
                aa = a + rng.uniform(-6.0, 6.0) * (min(t, 20) / 10.0 if t else 0)
                x, y = rr * math.cos(math.radians(aa)), rr * math.sin(math.radians(aa))
                if _blocked(x, y, rad[kind] * 0.5):
                    continue
                if any(math.hypot(x - p[2], y - p[3]) < rad[kind] + p[4] + 3.0 for p in pts):
                    continue
                ok = (x, y)
                break
            if ok:
                n += 1
                pts.append((kind, n, round(ok[0], 2), round(ok[1], 2), rad[kind]))
    return pts
