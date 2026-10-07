# geo.py - geometria do PLANO MESTRE da Ilha 3 (v4). So leitura dos layouts; nada no projeto e editado.
import sys, math, os
ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up"
for sub in ("ilha_naruto", "ilha_dragonball"):
    sys.path.insert(0, os.path.join(ROOT, sub))
import importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


IL = _load("il_layout", os.path.join(ROOT, "ilha_naruto", "il_layout.py"))
DB = _load("db_layout", os.path.join(ROOT, "ilha_dragonball", "db_layout.py"))
SG = _load("sg_layout", os.path.join(ROOT, "ilha_shadowgarden", "sg_layout.py"))

# ------------------------------------------------------------------ utilidades 2D (Roblox XZ)
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


def circle(c, r, n=32):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def pip(x, y, poly):
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


def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - (a[0] + dx * t), p[1] - (a[1] + dy * t))


def poly_dist(A, B):
    """distancia minima entre poligonos (0 se sobrepoem)"""
    if any(pip(x, y, B) for x, y in A) or any(pip(x, y, A) for x, y in B):
        return 0.0
    best = 1e9
    for P, Q in ((A, B), (B, A)):
        for p in P:
            for i in range(len(Q)):
                best = min(best, segd(p, Q[i], Q[(i + 1) % len(Q)]))
    return best


def multi_dist(As, Bs):
    return min(poly_dist(a, b) for a in As for b in Bs)


# ------------------------------------------------------------------ vizinhos (Roblox XZ)
def i1_to_rbx(x, y):
    return (-x, 420.0 + y)


def i1_polys():
    rim = [i1_to_rbx(*p) for p in IL.SHELF_RIM]
    br = [i1_to_rbx(*IL.exit_point(d)) for d in (0.0, IL.EXIT_BRIDGE_LEN)]
    isl = [i1_to_rbx(*p) for p in circle(IL.islet_center(), IL.GATE_ISLET_R)]
    return {"rim": rim, "bridge": ribbon(br, 9.0), "islet": isl}


def db_rbx(x, y):
    r = DB.to_roblox(x, y, 0.0)
    return (r[0], r[2])


def i2_polys():
    rim = [db_rbx(*p) for p in DB.ISLAND_RIM]
    br = [db_rbx(*DB.exit_point(d)) for d in (0.0, DB.EXIT_BRIDGE_LEN)]
    isl = [db_rbx(*p) for p in circle(DB.islet_center(), DB.GATE_ISLET_R)]
    arr = [db_rbx(0.0, DB.PREV_Y), db_rbx(0.0, DB.BRIDGE_Y1)]
    return {"rim": rim, "bridge": ribbon(br, 9.0), "islet": isl, "arrival": ribbon(arr, 9.0)}


def sg_rbx(x, y):
    r = SG.to_roblox(x, y, 0.0)
    return (r[0], r[2])


def i3_old_polys():
    rim = [sg_rbx(*p) for p in SG.ISLAND_RIM]
    br = [sg_rbx(*SG.exit_point(d)) for d in (0.0, SG.EXIT_BRIDGE_LEN)]
    isl = [sg_rbx(*p) for p in circle(SG.islet_center(), SG.GATE_ISLET_R)]
    arr = [sg_rbx(0.0, SG.PREV_Y), sg_rbx(0.0, SG.BRIDGE_Y1)]
    sm = [sg_rbx(*p) for p in circle(SG.SUMMON_C, SG.SUMMON_R)]
    return {"rim": rim, "bridge": ribbon(br, 9.0), "islet": isl, "arrival": ribbon(arr, 9.0), "summon": sm}


LOBBY = {
    "picos": rect(-650.0, -710.0, 660.0, 408.0),          # TER_Mountains_Peaks (bbox, conservador)
    "montanhas": rect(-225.0, -208.0, 245.0, 182.0),      # montanhas proximas ~470 x 390 em torno de (10, -13)
    "nucleo": rect(-344.0, -358.0, 342.0, 295.0),         # pecas do lobby sem o fundo
}
LOBBY_C = (0.0, -177.0)
A_RBX = (-579.227, 650.727)                                # ISLAND_NEXT_ANCHOR_ShadowGarden (fixo)
H0_RBX = (-0.9205, -0.3907)                               # rumo da Ilha 2 na ancora

# ------------------------------------------------------------------ PLANTA NOVA (local v4; +Y = castelo, +X = leste)
DECK, P1, SUM, P2, P3 = 28.2, 36.2, 40.2, 44.2, 52.2
Y_ENTRY = -334.0                  # fim da ponte de chegada (nariz sul da ilha)
RIM = [(-22, -334), (22, -334), (30, -306), (40, -294), (86, -302), (132, -290), (164, -262), (176, -222),
       (172, -182), (182, -150), (188, -104), (184, -58), (176, -20), (170, 30), (168, 90), (160, 150),
       (154, 220), (146, 282), (124, 332), (84, 368), (30, 386), (-30, 386), (-86, 370), (-124, 346),
       (-150, 318), (-160, 270), (-160, 200), (-166, 120), (-170, 60), (-176, 0), (-182, -60), (-186, -110),
       (-178, -160), (-168, -196), (-166, -250), (-150, -286), (-96, -304), (-42, -296)]
P1_POLY = [(-176, -150), (182, -150), (176, -222), (164, -262), (132, -290), (86, -302), (40, -294), (14, -286),
           (-14, -286), (-42, -296), (-96, -304), (-150, -286), (-166, -250), (-168, -196)]
P2_POLY = [(-186, -150), (182, -150), (188, -104), (184, -58), (178, -23), (-180, -23), (-182, -60), (-186, -110)]
P3_POLY = [(-176, -13), (176, -13), (170, 30), (168, 90), (160, 150), (154, 220), (146, 282), (124, 332),
           (84, 368), (30, 384), (-30, 384), (-86, 368), (-124, 344), (-150, 316), (-160, 270), (-160, 200),
           (-166, 120), (-170, 60)]
ENTRY_LOW = (-15, -334, 15, -310)
ENTRY_HIGH = (-14, -292, 14, -262)
PLAZA_C, PLAZA_R, FOUNTAIN_R = (0, -222), 32.0, 9.0
SUMMON_C, SUMMON_R = (-208, -222), 24.0
SUMMON_BRIDGE = ((-166, -222), (-184, -222), 12.0)
CRAFT_C, CRAFT_R = (112, -86), 16.0
# castelo 2x
FACADE_Y = 60.0
HALL = (-92.0, 66.0, 92.0, 262.0)          # interior do salao (184 x 196), piso P3, teto P3 + 84
HALL_CEIL_REL = 84.0
HALL_WALL = 5.0
ARCADE_X = 66.0                            # eixo dos pilares da arcada (face interna 64): nave central 128, naves laterais 24
MINE = (-52.0, 80.0, 52.0, 216.0)          # MiningZone 104 x 136
FRONT_TOWERS = [(-120.0, 72.0, 20.0), (120.0, 72.0, 20.0)]
CROWN_BASE = (-38.0, 262.0, 38.0, 344.0)   # base da torre-coroa: presbiterio + camara da escada
CHANCEL = (-20.0, 267.0, 20.0, 300.0)      # presbiterio (piso P3 + 2,4)
THRONE = (0.0, 294.0)
THRONE_PARK = (27.5, 294.0)                # trono recolhido no bolso da parede leste
STAIR_C, STAIR_R_IN, STAIR_R_OUT = (0.0, 322.0), 14.0, 18.0
GATEHOUSE = (0.0, -18.0, 24.0, 32.0)       # (x, y, vao livre, altura)
WALL_Y = (-23.0, -13.0)
FORECOURT = (-100.0, -13.0, 100.0, 60.0)
# salao sombrio (sob o castelo) e salas
CAVE = (-90.0, 88.0, 90.0, 336.0)          # interior; piso principal -12; galeria 6,6; abobada ate 46
CAVE_FLOOR, CAVE_GALLERY, CAVE_TOP = -12.0, 6.6, 46.0
CAVE_PORTAL = (0.0, 104.0)                 # DUNGEON_Hall (portal no fundo sul, encara o norte)
DUN_Z, DUN_CEIL = -72.0, -28.0
DUN_ROOMS = [("R1", (-42.0, 6.0, 42.0, 90.0)), ("R2", (-52.0, 92.0, 52.0, 196.0)), ("R3", (-52.0, 198.0, 52.0, 302.0))]
DUN_LINK_W, DUN_LINK_H = 32.0, 24.0
# vila: (nome, tipo, x, y, largura, profundidade, rumo da frente (graus), nivel)
HOUSES = [("H1", "B", -92.0, -262.0, 38.0, 28.0, 90.0, P1), ("H2", "A", -100.0, -180.0, 32.0, 24.0, 270.0, P1),
          ("H3", "A", 96.0, -262.0, 32.0, 24.0, 90.0, P1), ("H4", "C", 104.0, -180.0, 24.0, 18.0, 270.0, P1),
          ("H5", "A", -66.0, -114.0, 32.0, 24.0, 90.0, P2), ("H6", "C", -122.0, -58.0, 24.0, 18.0, 270.0, P2),
          ("H7", "A", -62.0, -56.0, 32.0, 24.0, 270.0, P2)]
STREETS = [([(-32, -222), (-100, -222), (-166, -222)], 10.0), ([(32, -222), (96, -224), (150, -222)], 10.0),
           ([(0, -254), (0, -290)], 14.0), ([(0, -190), (0, -150)], 14.0), ([(0, -132), (0, -40)], 14.0),
           ([(-166, -86), (-60, -86), (0, -86), (60, -86), (94, -86)], 10.0), ([(128, -86), (150, -60), (150, -40)], 10.0),
           ([(0, -13), (0, 52)], 20.0), ([(150, -23), (150, 40), (136, 120)], 12.0)]
STAIRS = [("Entry", (0, -310), 90, 20, 10, 1.8), ("P1P2", (0, -150), 90, 18, 10, 1.8), ("Gate", (0, -40), 90, 20, 10, 1.7),
          ("EastP3", (150, -40), 90, 14, 10, 1.7), ("Summon", (-184, -222), 180, 12, 5, 1.7)]
# rota da saida (P3): patio -> beco oeste -> terraco norte -> cabeceira NW
EXIT_ROUTE = [(0, 30), (-90, 34), (-150, 44), (-148, 100), (-136, 200), (-132, 290), (-116, 334)]
EXIT_START = (-116.0, 342.0)               # ISLAND_EXIT_ShadowGarden (na borda NW, cota P3)
MIRANTE_E = (130.0, 170.0)                 # jardim-mirante no lugar da antiga portaria da masmorra (P3 leste)
OLD_DUNGEON_SITE = (80.0, 46.0, 126.0, 116.0)   # (no local ANTIGO) caixa da boca da caverna


def exit_dir_local(deg):
    a = math.radians(deg)
    return (math.cos(a), math.sin(a))


# ------------------------------------------------------------------ encaixe no mundo
class Fit:
    def __init__(self, yaw, arc_R, straight, exit_deg, exit_len=64.0):
        self.yaw, self.R, self.s, self.exit_deg, self.exit_len = yaw, arc_R, straight, exit_deg, exit_len
        # Blender XY: Roblox z = -y
        ax, ay = A_RBX[0], -A_RBX[1]
        h0 = math.atan2(-H0_RBX[1], H0_RBX[0])                 # 157 graus
        hi = math.radians(yaw + 90.0)
        d = hi - h0
        pts = [(ax, ay)]
        if abs(d) > 1e-6:
            sgn = 1.0 if d > 0 else -1.0
            cx, cy = ax + arc_R * math.cos(h0 + sgn * math.pi / 2), ay + arc_R * math.sin(h0 + sgn * math.pi / 2)
            a0 = math.atan2(ay - cy, ax - cx)
            n = 12
            for k in range(1, n + 1):
                a = a0 + d * k / n
                pts.append((cx + arc_R * math.cos(a), cy + arc_R * math.sin(a)))
        ex, ey = pts[-1]
        ex, ey = ex + straight * math.cos(hi), ey + straight * math.sin(hi)
        pts.append((ex, ey))
        self.bridge_bl = pts
        self.arc_len = arc_R * abs(d)
        self.length = self.arc_len + straight
        self.E = (ex, ey)
        self.turn = math.degrees(d)

    def to_bl(self, x, y):
        a = math.radians(self.yaw)
        ly = y - Y_ENTRY
        return (self.E[0] + x * math.cos(a) - ly * math.sin(a), self.E[1] + x * math.sin(a) + ly * math.cos(a))

    def rbx(self, x, y):
        bx, by = self.to_bl(x, y)
        return (bx, -by)

    def dir_rbx(self, dx, dy):
        a = math.radians(self.yaw)
        return (dx * math.cos(a) - dy * math.sin(a), -(dx * math.sin(a) + dy * math.cos(a)))

    def local_of_bl(self, bx, by):
        a = math.radians(self.yaw)
        dx, dy = bx - self.E[0], by - self.E[1]
        return (dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a) + Y_ENTRY)

    def polys(self):
        T = lambda pts: [self.rbx(*p) for p in pts]
        ux, uy = exit_dir_local(self.exit_deg)
        ep = [(EXIT_START[0] + ux * d, EXIT_START[1] + uy * d) for d in (0.0, self.exit_len)]
        isc = (EXIT_START[0] + ux * (self.exit_len + 18.0), EXIT_START[1] + uy * (self.exit_len + 18.0))
        br = [(x, -y) for x, y in self.bridge_bl]
        return {"rim": T(RIM), "summon": T(circle(SUMMON_C, SUMMON_R)), "exit_bridge": T(ribbon(ep, 9.0)),
                "islet": T(circle(isc, 22.0)), "arrival": ribbon(br, 9.0)}

    def anchor4(self):
        ux, uy = exit_dir_local(self.exit_deg)
        p = (EXIT_START[0] + ux * (self.exit_len + 40.0), EXIT_START[1] + uy * (self.exit_len + 40.0))
        return self.rbx(*p), self.dir_rbx(ux, uy)

    def exit_start(self):
        return self.rbx(*EXIT_START)
