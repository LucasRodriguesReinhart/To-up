# db_layout - planta TRAVADA da Ilha 2 (Dragon Ball). 1 BU = 1 stud, Z para cima. Cotas Z ABSOLUTAS = Y do Roblox.
# Referencial LOCAL de projeto (o da concept aprovada, refs/concept_db_aprovado.png):
#   origem = centro da arena de mineracao; +Y = norte (vila tech -> Capsule), +X = leste (saida -> Shadow Garden),
#   -Y = sul (chegada vinda da Ilha 1 Naruto). Summon a oeste (-X).
# Mundo (Blender do lobby) - regra de encaixe de ilha_naruto/CONEXAO_DRAGONBALL.md:
#   W2 = T(ancora_mundo) . Rz(rumo_mundo - 90) . T(-entrada_local)
#   ancora_mundo = ISLAND_NEXT_ANCHOR da Ilha 1 no mundo = (-192,17; -612,17; 16,2); rumo_mundo = 225 -> giro 135
#   entrada_local = WORLD_FROM_PREV (inicio da ponte de chegada desta ilha) = (0, PREV_Y, DECK)
#   Roblox = (x_mundo, z, -y_mundo)  ->  centro da arena em Roblox ~ (-323,7; z; 743,7)
# NARUTO DEFINE O PIPELINE, NAO O LAYOUT: nada aqui copia a planta da Ilha 1 (fosso redondo + anel + C + paredao).
import math

# ------------------------------------------------------------------ encaixe na Ilha 1
NARUTO_ANCHOR_WORLD = (-192.1670, -612.1670, 16.2)   # il_layout.anchor_pos() levado ao mundo por export_ilha.WORLD
NARUTO_HEADING_WORLD_DEG = 225.0
WORLD_YAW_DEG = NARUTO_HEADING_WORLD_DEG - 90.0      # 135
PREV_Y = -186.0                                      # WORLD_FROM_PREV (y local), ponta sul da ponte de chegada


def world_matrix():
    """matriz local -> mundo do lobby (mathutils), so XY (as cotas Z ja sao absolutas)"""
    from mathutils import Matrix, Vector
    ax, ay, _ = NARUTO_ANCHOR_WORLD
    return (Matrix.Translation(Vector((ax, ay, 0.0))) @ Matrix.Rotation(math.radians(WORLD_YAW_DEG), 4, "Z")
            @ Matrix.Translation(Vector((0.0, -PREV_Y, 0.0))))


def to_world_xy(x, y):
    a = math.radians(WORLD_YAW_DEG)
    ax, ay, _ = NARUTO_ANCHOR_WORLD
    ly = y - PREV_Y
    return (ax + x * math.cos(a) - ly * math.sin(a), ay + x * math.sin(a) + ly * math.cos(a))


def to_roblox(x, y, z):
    wx, wy = to_world_xy(x, y)
    return (wx, z, -wy)


# ------------------------------------------------------------------ niveis
DECK = 16.2       # ponte de chegada (= cabeceira da Ilha 1)
GROUND = 24.2     # chao geral da ilha: praca de entrada, promenade em volta da arena, jardins
ARENA = 20.2      # piso da arena de mineracao (bacia rasa, 4 abaixo do promenade)
HUB = 28.2        # terraco da vila tech (norte) e prateleira da saida (leste)
EXIT_Z = 28.2
SUM = 30.2        # plataforma do summon (oeste)
CAP = 34.2        # terraco do Capsule (fundo, norte)
SEA = -110.0      # mar (so visual)
RISE = 0.8        # espelho maximo
TREAD = 1.7

LEVELS = (DECK, ARENA, GROUND, HUB, SUM, CAP)

# ------------------------------------------------------------------ chegada (sul)
DECK_W = 18.0                 # largura padrao entre ilhas (il_gate_std.DECK_W)
BRIDGE_Y0 = PREV_Y            # -186: ponta sul (encosta na ancora da Ilha 1)
BRIDGE_Y1 = -130.0            # fim da ponte / pe da escadaria
ENTRY_STAIR_N = 10            # 10 x 0,8 = 8,0 (DECK -> GROUND)
ENTRY_STAIR_TREAD = 1.8       # 18 de comprimento: y -130 .. -112
ENTRY_STAIR_W = 20.0
ENTRY_STAIR_Y1 = BRIDGE_Y1 + ENTRY_STAIR_N * ENTRY_STAIR_TREAD    # -112
GATE_Y = -104.0               # eixo do portal de entrada (arco Capsule branco/azul-marinho, vao 18 x 16)
GATE_OPEN_W = 18.0
GATE_OPEN_H = 16.0
ENTRY_PLAZA = (-22.0, -112.0, 22.0, -74.0)    # x0, y0, x1, y1 (piso GROUND)
ENTRY_SPAWN = (0.0, -92.0)                    # WORLD_ENTRY_DragonBall (olhando +Y, para a arena)

# ------------------------------------------------------------------ arena de mineracao (bacia de canion, ovalada)
# contorno por raio em funcao do angulo (graus, 0 = leste, anti-horario), interpolado periodico (Catmull-Rom)
ARENA_CTRL = [(0, 66.0), (30, 63.0), (60, 56.0), (90, 53.0), (120, 56.0), (150, 61.0), (180, 64.0),
              (210, 62.0), (240, 58.0), (270, 56.0), (300, 59.0), (330, 65.0)]
# largura do promenade (piso GROUND em volta da arena) por angulo
PROM_W_CTRL = [(0, 16.0), (45, 14.0), (90, 14.0), (135, 14.0), (180, 15.0), (225, 17.0), (270, 18.0), (315, 17.0)]
# acessos arena <-> promenade: (angulo, largura, tipo). Escada = 5 x 0,8 (piso 1,7 -> 8,5 para dentro da arena);
# rampa = rampa natural de pedra 4 / 18 (12,5 graus)
ARENA_ACCESS = [(270.0, 14.0, "stair"), (90.0, 12.0, "stair"), (180.0, 10.0, "stair"), (14.0, 9.0, "ramp"),
                (222.0, 8.0, "stair"), (318.0, 8.0, "stair")]
STAIR_RUN = 5 * TREAD         # 8,5
RAMP_RUN = 18.0
CORE_POD = (0.0, 0.0, 4.5)    # pod de sondagem Capsule no centro (domo pequeno, marco; NAO e minerio)
# formacoes de rocha (mesas baixas) DENTRO da arena, junto da borda: (x, y, raio, altura). Nao-andaveis, colisao.
ARENA_ROCKS = [(-44.0, 30.0, 6.0, 11.0), (-50.0, -18.0, 5.0, 8.0), (38.0, 38.0, 5.5, 13.0), (52.0, -26.0, 6.0, 9.0),
               (-18.0, 44.0, 4.0, 7.0), (22.0, -44.0, 4.5, 7.5), (-30.0, -42.0, 4.0, 6.0)]
LANE_HW = 4.0                 # corredor livre do pe de cada acesso ate o pod central (sem minerio)

# ------------------------------------------------------------------ contorno da ilha (topo do penhasco, anti-horario)
ISLAND_CTRL = [(-22.0, -134.0), (22.0, -134.0), (46.0, -126.0), (72.0, -112.0), (96.0, -94.0), (118.0, -68.0),
               (136.0, -38.0), (150.0, -4.0), (158.0, 32.0), (156.0, 60.0), (148.0, 90.0), (132.0, 126.0),
               (112.0, 160.0), (88.0, 188.0), (56.0, 206.0), (18.0, 214.0), (-22.0, 214.0), (-60.0, 206.0),
               (-94.0, 188.0), (-122.0, 162.0), (-144.0, 128.0), (-160.0, 92.0), (-172.0, 54.0), (-176.0, 14.0),
               (-170.0, -24.0), (-152.0, -58.0), (-128.0, -88.0), (-100.0, -110.0), (-72.0, -124.0),
               (-46.0, -132.0)]

# ------------------------------------------------------------------ terracos elevados
# vila tech (norte, HUB 28,2): frente reta em y 76 (escada central do promenade), laterais ate a borda
HUB_POLY = [(-118.0, 96.0), (-96.0, 82.0), (-52.0, 76.0), (52.0, 76.0), (96.0, 80.0), (112.0, 92.0), (124.0, 118.0),
            (114.0, 158.0), (88.0, 188.0), (56.0, 206.0), (18.0, 214.0), (-22.0, 214.0), (-60.0, 206.0),
            (-94.0, 188.0), (-122.0, 162.0), (-140.0, 128.0)]
HUB_STAIR = (0.0, 76.0, 14.0)            # (x, y da borda do terraco, largura) - desce para o sul (promenade)
HUB_SIDE_STAIRS = [(-78.0, 78.5, 10.0), (78.0, 78.0, 10.0)]   # escadas laterais do promenade para a vila
# terraco do Capsule (CAP 34,2), dentro da vila
CAP_POLY = [(-70.0, 132.0), (70.0, 132.0), (76.0, 160.0), (64.0, 192.0), (36.0, 206.0), (-36.0, 206.0),
            (-64.0, 192.0), (-76.0, 160.0)]
CAP_STAIR = (0.0, 132.0, 22.0)           # escadaria grande HUB -> CAP (8 x 0,75), centrada, sobe para o norte
CAP_STAIR_N = 8
# Capsule (heroi): cupula principal + anexos. ENTRAVEL: foyer -> corredor -> salao sob a cupula
CAPSULE_C = (0.0, 174.0)
CAPSULE_R = 29.0              # raio externo da cupula principal (diametro 58; frente y 145, fundo y 203)
CAPSULE_DOOR_Y = 135.0        # plano da porta principal = frente do pavilhao de entrada (vao 10 x 12, frente sul)
CAPSULE_DOOR_W = 10.0
CAPSULE_DOOR_H = 12.0
CAPSULE_FOYER = (-10.0, 135.0, 10.0, 145.0)   # pavilhao de entrada (foyer) x0, y0, x1, y1 (piso CAP)
CAPSULE_CORRIDOR = (-5.0, 145.0, 5.0, 153.0)  # corredor foyer -> salao (dentro da casca da cupula)
CAPSULE_HALL_R = 21.0          # raio do salao sob a cupula (centro CAPSULE_C; y 153..195; pe-direito >= 18)
CAPSULE_ANNEX = [(-48.0, 180.0, 13.0), (48.0, 176.0, 12.0)]   # anexos (x, y, raio) - nao entraveis

# summon (oeste, SUM 30,2)
SUMMON_C = (-128.0, -4.0)
SUMMON_R = 25.0
SUMMON_TOWER = (-141.0, 2.0)
SUMMON_FACE_DEG = -12.0       # frente da torre (para leste, levemente ao sul: arena e entrada)
SUMMON_STAIR = (-89.4, -2.0, 12.0)  # pe (x, y) no chao GROUND, largura; sobe para oeste (8 x 0,75) ate a borda x -103
SUMMON_STAIR_N = 8

# saida (leste, EXIT_Z 28,2): escada do promenade -> prateleira ao longo da borda -> arco de rocha -> ponte
EXIT_STAIR = (74.0, 27.0, 35.0, 12.0)    # pe (x, y), rumo (graus), largura: GROUND -> EXIT_Z (5 x 0,8)
EXIT_PATH = [(81.0, 32.0), (98.0, 44.0), (120.0, 58.0), (140.0, 70.0), (150.0, 76.0)]
EXIT_PATH_HW = 9.0
HUB_EXIT_LINK = [(100.0, 88.0), (114.0, 72.0), (124.0, 62.0)]    # vila (leste) <-> prateleira da saida
HUB_EXIT_LINK_HW = 7.0
EXIT_ARCH = (112.0, 53.0, 34.0)       # arco natural de rocha sobre a trilha (x, y, rumo da trilha); vao >= 18 x 22
EXIT_START = (150.0, 76.0)            # ISLAND_EXIT_DragonBall (inicio da ponte de saida, na borda da ilha)
EXIT_DEG = 22.0                       # rumo da ponte de saida (ENE do projeto)
EXIT_W = 18.0
EXIT_BRIDGE_LEN = 64.0
GATE_ISLET_R = 22.0
GATE_SG_OFF = 12.0                    # do inicio da ilhota ate o eixo do portao Shadow Garden
ANCHOR_OFF = 40.0                     # do inicio da ilhota ate ISLAND_NEXT_ANCHOR_ShadowGarden
SG_TRANSITION_D = 20.0                # a paleta Shadow Garden comeca 20 antes do inicio da ponte (depois do arco)

# ------------------------------------------------------------------ rochedos grandes (mesas/pilares; nao-andaveis)
# (x, y, raio_base, altura_topo_absoluta, tipo) - PRIMARY: silhueta; SECONDARY: moldura; tipo: mesa|pillar|spire
MESAS = [
    # AGRUPADAS (nao cercam a ilha): cacho NO, fundo (moldura da cupula), cacho NE, acento frontal e mesa leste baixa.
    # PRIMARY: silhueta alta; SECONDARY: moldura; tipo: mesa (topo largo e plano, com verde) | pillar | spire (agulha)
    # cacho noroeste (atras do summon e da vila oeste)
    (-150.0, 118.0, 18.0, 98.0, "mesa"), (-126.0, 152.0, 12.0, 124.0, "pillar"), (-172.0, 84.0, 9.0, 76.0, "spire"),
    (-102.0, 184.0, 10.0, 90.0, "pillar"),
    # fundo: pilares que emolduram a cupula (concept) + mesa larga atras
    (-58.0, 216.0, 15.0, 136.0, "pillar"), (-14.0, 240.0, 20.0, 84.0, "mesa"), (62.0, 212.0, 13.0, 96.0, "pillar"),
    # cacho nordeste (atras da saida e do mirante)
    (132.0, 136.0, 17.0, 104.0, "mesa"), (154.0, 106.0, 9.0, 86.0, "spire"), (108.0, 180.0, 11.0, 94.0, "pillar"),
    # acento frontal esquerdo (ao lado da queda SW, como na concept) e mesa baixa leste (atras do dojo)
    (-118.0, -104.0, 9.0, 62.0, "pillar"), (160.0, -26.0, 12.0, 56.0, "mesa"),
]
# rochedos medios NO plato (massa secundaria: quebram o chao liso; nao-andaveis, colisao) - (x, y, raio, altura)
PLATEAU_ROCKS = [(-120.0, -42.0, 7.0, 11.0), (-136.0, 28.0, 6.0, 13.0), (108.0, -34.0, 6.0, 9.0),
                 (-44.0, -112.0, 5.0, 7.0), (44.0, -114.0, 5.0, 6.0), (130.0, 8.0, 5.0, 8.0),
                 (-146.0, -64.0, 5.0, 9.0), (84.0, -116.0, 5.0, 8.0)]
# canteiros verdes (o chao geral e areia/terra; verde so perto da agua, da entrada e da vila) - (x, y, raio)
GARDENS = [(-82.0, -88.0, 16.0), (80.0, -84.0, 14.0), (-30.0, -96.0, 9.0), (30.0, -96.0, 9.0), (-104.0, 40.0, 13.0),
           (100.0, 18.0, 11.0), (-108.0, 102.0, 16.0), (-150.0, 40.0, 10.0), (142.0, -52.0, 8.0)]
# caminhos pavimentados radiais no chao GROUND (a "flor" da vista superior): (pontos, largura)
GROUND_PATHS = [
    ([(-52.0, -64.0), (-92.0, -70.0), (-124.0, -78.0)], 6.0),          # promenade -> satelite SW (poco SW no caminho)
    ([(52.0, -62.0), (90.0, -62.0), (116.0, -58.0)], 6.0),             # promenade -> satelite SE
    ([(78.0, -8.0), (104.0, -12.0)], 6.0),                               # promenade -> dojo
    ([(-78.0, 22.0), (-100.0, 26.0), (-118.0, 44.0), (-128.0, 54.0)], 6.0),   # promenade -> heliponto (contorna o pod O)
    ([(-79.0, -2.0), (-89.4, -2.0)], 12.0),                              # promenade -> escada do summon
]
# satelites: torres em plataformas redondas na borda (a "flor" da vista superior da concept).
# (x, y, raio_plataforma, tipo, andavel) - andavel: ponte curta do chao GROUND ate a plataforma (mirante)
TOWER_SITES = [(-104.0, 150.0, 8.0, "comm", False), (100.0, 140.0, 8.0, "lookout", False),
               (74.0, 118.0, 6.0, "energy", False), (-148.0, -98.0, 10.0, "pad_sw", True),
               (140.0, -76.0, 10.0, "pad_se", True)]
# pontes curtas (GROUND) do chao ate as plataformas satelite andaveis: (inicio_no_chao, fim_na_plataforma)
SAT_BRIDGES = {"pad_sw": ((-124.0, -78.0), (-141.0, -91.0)), "pad_se": ((116.0, -58.0), (132.0, -70.0))}
SAT_BRIDGE_W = 8.0

# ------------------------------------------------------------------ vila tech (lotes: x, y, raio/largura, tipo)
HUB_LOTS = [(-58.0, 100.0, 11.0, "capsule_house_A"), (62.0, 98.0, 10.0, "capsule_house_B"),
            (-86.0, 128.0, 13.0, "martial_market"), (34.0, 116.0, 11.0, "workshop")]
# lotes no chao GROUND (leste e oeste; ocupam as sobras grandes entre o promenade e a borda)
GROUND_LOTS = [(120.0, -14.0, 14.0, "dojo"), (-140.0, 58.0, 12.0, "landing_pad")]
# pods pequenos em volta do promenade (casas-capsula nao entraveis, sem porta): (x, y, raio)
PODS = [(-58.0, -92.0, 5.5), (60.0, -90.0, 5.0), (-100.0, 40.0, 5.0), (104.0, 14.0, 4.5)]

# ------------------------------------------------------------------ agua (moderada)
POOL_SW = (-82.0, -88.0, 8.0)            # poco no jardim SW -> canal -> queda pela borda da frente (concept)
FALL_SW = (-94.0, -113.0)
POOL_SE = (80.0, -84.0, 7.0)
FALL_SE = (88.0, -102.0)
POOL_NW = (-108.0, 104.0, 10.0)          # poco na vila (HUB, >= 2 da borda do terraco) com cascata que desce da mesa NW
CASCADE_NW_TOP = (-132.0, 110.0, 70.0)
WATER_DROP = 0.8                         # lamina d'agua abaixo do piso do terraco onde esta


# ------------------------------------------------------------------ helpers de forma
def _periodic_interp(ctrl, ang_deg):
    """interpolacao periodica Catmull-Rom de (angulo, valor)"""
    pts = sorted(ctrl)
    n = len(pts)
    a = ang_deg % 360.0
    i = 0
    while i < n and pts[i][0] <= a:
        i += 1
    i1 = (i - 1) % n
    i2 = i % n
    a1, v1 = pts[i1]
    a2, v2 = pts[i2]
    span = (a2 - a1) % 360.0 or 360.0
    t = ((a - a1) % 360.0) / span
    v0 = pts[(i1 - 1) % n][1]
    v3 = pts[(i2 + 1) % n][1]
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * v1) + (-v0 + v2) * t + (2 * v0 - 5 * v1 + 4 * v2 - v3) * t2 + (-v0 + 3 * v1 - 3 * v2 + v3) * t3)


def arena_r(ang_deg):
    return _periodic_interp(ARENA_CTRL, ang_deg)


def prom_w(ang_deg):
    return _periodic_interp(PROM_W_CTRL, ang_deg)


def prom_r(ang_deg):
    return arena_r(ang_deg) + prom_w(ang_deg)


def polar_poly(fn, step=3.0, a0=0.0, a1=360.0, closed=True):
    n = max(3, int(round(abs(a1 - a0) / step)))
    last = n if not closed else n - 1
    pts = []
    for i in range(0, n + (0 if closed else 1)):
        a = a0 + (a1 - a0) * i / n
        r = fn(a)
        pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
    return pts


def arena_poly(step=3.0):
    return polar_poly(arena_r, step)


def prom_poly(step=3.0):
    return polar_poly(prom_r, step)


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


def summon_poly(step=6.0):
    cx, cy = SUMMON_C
    return [(cx + SUMMON_R * math.cos(math.radians(a)), cy + SUMMON_R * math.sin(math.radians(a)))
            for a in range(0, 360, int(step))]


def in_exit_shelf(x, y):
    return (polyline_dist(x, y, EXIT_PATH) <= EXIT_PATH_HW or polyline_dist(x, y, HUB_EXIT_LINK) <= HUB_EXIT_LINK_HW)


def zone_of(x, y):
    """nivel do terreno em (x, y) (fora de pontes/escadas)"""
    r = math.hypot(x, y)
    ang = math.degrees(math.atan2(y, x))
    if r <= arena_r(ang):
        return ARENA
    if point_in_poly(x, y, CAP_POLY):
        return CAP
    if math.hypot(x - SUMMON_C[0], y - SUMMON_C[1]) <= SUMMON_R:
        return SUM
    if point_in_poly(x, y, HUB_POLY):
        return HUB
    if in_exit_shelf(x, y):
        return EXIT_Z
    return GROUND


# ------------------------------------------------------------------ acessos e saida
def access_frame(ang_deg):
    """(pe, topo, direcao_para_dentro) de um acesso da arena: topo na borda (GROUND), pe dentro (ARENA)"""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    r = arena_r(ang_deg)
    kind = [k for aa, w, k in ARENA_ACCESS if abs((aa - ang_deg + 180) % 360 - 180) < 1e-6]
    run = RAMP_RUN if kind and kind[0] == "ramp" else STAIR_RUN
    top = (ux * r, uy * r)
    foot = (ux * (r - run), uy * (r - run))
    return foot, top, (-ux, -uy)


def exit_dir():
    a = math.radians(EXIT_DEG)
    return (math.cos(a), math.sin(a))


def exit_point(d):
    """ponto no eixo da saida a d studs do inicio da ponte de saida"""
    ux, uy = exit_dir()
    return (EXIT_START[0] + ux * d, EXIT_START[1] + uy * d)


def islet_center():
    return exit_point(EXIT_BRIDGE_LEN + GATE_ISLET_R - 4.0)


def gate_sg_pos():
    return exit_point(EXIT_BRIDGE_LEN + GATE_SG_OFF)


def anchor_pos():
    return exit_point(EXIT_BRIDGE_LEN + ANCHOR_OFF)


def sg_yaw():
    """yaw do referencial do portao (il_gate_std): +Y local aponta para quem atravessa (sai da ilha)"""
    ux, uy = exit_dir()
    return math.atan2(uy, ux) - math.pi / 2


# ------------------------------------------------------------------ minerio: pontos reais (gerados e travados aqui)
ORE_KINDS = [("COMMON", 2.6), ("UNCOMMON", 3.0), ("EPIC", 3.4), ("SUPERLEGENDARY", 4.4)]
ORE_RIM_CLEAR = 5.0     # distancia minima do centro do minerio ate a borda da arena


def ore_blocked(x, y, clear):
    r = math.hypot(x, y)
    ang = math.degrees(math.atan2(y, x))
    if r > arena_r(ang) - ORE_RIM_CLEAR - clear:
        return True
    if r < CORE_POD[2] + 4.0 + clear:
        return True
    for rx, ry, rr, h in ARENA_ROCKS:
        if math.hypot(x - rx, y - ry) < rr + 3.0 + clear:
            return True
    for aa, w, kind in ARENA_ACCESS:
        foot, top, _ = access_frame(aa)
        # faixa do acesso (escada/rampa) + corredor ate o pod
        d, t = seg_dist(x, y, top[0], top[1], foot[0], foot[1])
        if d < w / 2 + 1.5 + clear:
            return True
        d2, t2 = seg_dist(x, y, foot[0], foot[1], 0.0, 0.0)
        if d2 < LANE_HW + clear and t2 < 0.92:
            return True
    return False


def ore_points():
    """lista (kind, i, x, y, raio) - 2 super, 8 epicos, 16 incomuns, 28 comuns (mesma contagem da Ilha 1),
    espacamento >= r1 + r2 + 3 (varios jogadores minerando lado a lado). Distribuicao por aneis ovalados."""
    import random
    rng = random.Random(2202)
    rad = dict(ORE_KINDS)
    plan = [("SUPERLEGENDARY", 2, 0.28, 0.34), ("EPIC", 8, 0.40, 0.52), ("UNCOMMON", 16, 0.56, 0.70),
            ("COMMON", 28, 0.60, 0.95)]
    pts = []
    for kind, n, f0, f1 in plan:
        got = 0
        tries = 0
        base = rng.uniform(0, 360)
        while got < n and tries < 12000:
            tries += 1
            a = base + 360.0 * (got + rng.uniform(-0.35, 0.35)) / n + (tries // 200) * 7.0
            f = rng.uniform(f0, f1)
            rmax = arena_r(a) - ORE_RIM_CLEAR
            r = f * rmax
            x, y = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            if ore_blocked(x, y, rad[kind] * 0.5):
                continue
            if any(math.hypot(x - p[2], y - p[3]) < rad[kind] + p[4] + 3.0 for p in pts):
                continue
            got += 1
            pts.append((kind, got, round(x, 2), round(y, 2), rad[kind]))
    return pts
