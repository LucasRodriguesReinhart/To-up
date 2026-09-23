# fm_veg - vegetacao da Vila-Forja por raycast na superficie real do terreno (kit em fm_veg_kit).
# VALE (heroi): pinheiros em camadas nas molduras (pe dos penhascos, cantos, 3-4 bosquetes na mureta sul com vaos),
#   folhosas de copa redonda perto das casas e da praca, sakura a oeste. Regras: 4,5 studs do trilho da mina, 1,5 alem
#   do meio-fio, raio da copa + 2 ate as pegadas das construcoes; arvore a menos de 3 studs de area andavel tem copa
#   alta (base >= 5,5: o jogador passa por baixo e no Roblox a copa nao some vista de dentro); visadas do spawn e da
#   praca (loja, Ignis, mina, portais, roda, portas) sempre livres; COL de tronco so perto das rotas do fm_qa.
#   Sub-bosque: talude dos penhascos, canteiros na base das casas, junco no pe das paredes do rio, moitas nas
#   cercas do rio e manchas de grama com flores separadas por gramado aberto.
# TAMPAS (topos e patamares de coluna das bordas/montanhas): campo de aglomerados -> ~27% com grupo de 3-6 arvores
#   junto a borda externa, ~13% com arvore seca ou inclinada para fora, ~60% so com moita pendente (ou nua), com
#   trechos de 20-30 studs sem arvore. Patamares e fendas (tampas encostadas numa parede) entram com bonus.
# PLANALTOS: 2-3 manchas densas grandes (raio variando 2x), clareiras com afloramentos, linha de arvores na borda.
# STREAMING: uma malha por SETOR (<= 150 studs) e paleta curta (cada material = 1 MeshPart por setor).
import math, random
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree
from fm_lib import MB, col_box, point_in_poly
import fm_layout as L
import fm_veg_kit as K

PLACED = []   # (zona, especie, x, y, z, h) de cada arvore - conferencia/QA
STATS = {}


def surface_bvh(prefixes=("TER_",)):
    verts, polys, mats = [], [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(prefixes):
            continue
        if o.name in ("TER_Far_Valley",):
            continue
        base = len(verts)
        mw = o.matrix_world
        verts += [mw @ v.co for v in o.data.vertices]
        for p in o.data.polygons:
            polys.append([base + i for i in p.vertices])
            mn = o.data.materials[p.material_index].name if o.data.materials else ""
            mats.append(mn)
    return BVHTree.FromPolygons(verts, polys), mats


class Blockers:
    """pegadas 2D (retangulos orientados) das colisoes + faixas dos caminhos (+ marcadores de gameplay)"""

    CELL = 16.0

    def __init__(self, margin=2.5, markers=True):
        self.rects = []
        for o in bpy.data.objects:
            if not o.name.startswith("COL_") or o.get("col_kind") in ("Floor",):
                continue
            if o.name.startswith(("COL_Floor", "COL_Terrace", "COL_MidLedge", "COL_BackMountain", "COL_WestCliff",
                                  "COL_EastCliff", "COL_MidWall", "COL_UpperWall", "COL_Konoha", "COL_Veg")):
                continue
            self.rects.append((o.location.copy(), o.rotation_euler.z, o.scale.x / 2 + margin, o.scale.y / 2 + margin,
                               o.location.z - o.scale.z / 2, o.location.z + o.scale.z / 2))
        self.grid = {}
        for idx, (c, a, hx, hy, z0, z1) in enumerate(self.rects):
            rad = math.hypot(hx, hy)
            for gx in range(int(math.floor((c.x - rad) / self.CELL)), int(math.floor((c.x + rad) / self.CELL)) + 1):
                for gy in range(int(math.floor((c.y - rad) / self.CELL)), int(math.floor((c.y + rad) / self.CELL)) + 1):
                    self.grid.setdefault((gx, gy), []).append(idx)
        import fm_buildings
        self.polys = []
        for name, (pts, w) in fm_buildings.PATHS.items():
            self.polys.append(fm_buildings.ribbon(pts, w + 4.0))
        self.circles = [(0.0, -30.0, 29.0), (L.DAIS_C[0], L.DAIS_C[1], L.DAIS_R + 5)]
        # corredores de circulacao que nao sao pavimentados
        for px in L.PORTAL_X:
            self.polys.append([(px - 11, 30), (px + 11, 30), (px + 11, 64), (px - 11, 64)])
            self.polys.append([(px - 14, L.FLIGHT2_Y1 - 2), (px + 14, L.FLIGHT2_Y1 - 2), (px + 14, L.PORTAL_Y + 9),
                               (px - 14, L.PORTAL_Y + 9)])
        self.polys.append([(-150, 60), (160, 60), (160, 82), (-150, 82)])   # ledge + canal
        self.polys.append([(-20, -120), (20, -120), (20, -52), (-20, -52)])  # spawn/avenida
        # visada da praca para a boca da mina (a mina tem que ser lida de longe)
        self.polys.append([(-20, -38), (-20, -52), (-60, -60), (-80, -46), (-66, -28), (-40, -24)])
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(("FORGE_", "BLD_", "WATER_Waterwheel", "MINE_Entrance")):
                continue
            if o.name.startswith("BLD_Bridges"):
                continue
            cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
            x0, x1 = min(c.x for c in cs) - 2, max(c.x for c in cs) + 2
            y0, y1 = min(c.y for c in cs) - 2, max(c.y for c in cs) + 2
            self.polys.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        self.bboxes = [(min(p[0] for p in q), min(p[1] for p in q), max(p[0] for p in q), max(p[1] for p in q))
                       for q in self.polys]
        if markers:
            for o in bpy.data.objects:
                if o.type != "EMPTY":
                    continue
                n = o.name
                if n.startswith(("DOOR_", "NPC_", "INTERACT_", "PLAYER_INTERACT_", "WORLD_", "MINE_Entrance",
                                 "LEADERBOARD_")):
                    self.circles.append((o.location.x, o.location.y, 7.0))
                elif n.startswith("PORTAL_"):
                    self.circles.append((o.location.x, o.location.y, 15.0))

    def blocked(self, x, y, z):
        for idx in self.grid.get((int(math.floor(x / self.CELL)), int(math.floor(y / self.CELL))), ()):
            c, a, hx, hy, z0, z1 = self.rects[idx]
            if z < z0 - 3 or z > z1 + 3:
                continue
            dx, dy = x - c.x, y - c.y
            ca, sa = math.cos(-a), math.sin(-a)
            lx, ly = dx * ca - dy * sa, dx * sa + dy * ca
            if abs(lx) < hx and abs(ly) < hy:
                return True
        for poly, bb in zip(self.polys, self.bboxes):
            if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and point_in_poly(x, y, poly):
                return True
        for (cx, cy, r) in self.circles:
            if (x - cx) ** 2 + (y - cy) ** 2 < r * r:
                return True
        return False


class Spacing:
    """hash espacial de ocupacao (x, y, raio)"""

    def __init__(self, cell=8.0):
        self.cell = cell
        self.g = {}

    def free(self, x, y, r, k=1.0):
        c = self.cell
        gx, gy = int(math.floor(x / c)), int(math.floor(y / c))
        reach = int(math.ceil((r + 14.0) / c))
        for i in range(gx - reach, gx + reach + 1):
            for j in range(gy - reach, gy + reach + 1):
                for (px, py, pr) in self.g.get((i, j), ()):
                    d = (r + pr) * k
                    if (x - px) ** 2 + (y - py) ** 2 < d * d:
                        return False
        return True

    def add(self, x, y, r):
        self.g.setdefault((int(math.floor(x / self.cell)), int(math.floor(y / self.cell))), []).append((x, y, r))


# ------------------------------------------------------------------ geometria 2D
def _seg_dist(px, py, a, b):
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-9)))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))


def _pl_dist(x, y, pts):
    return min(_seg_dist(x, y, a, b) for a, b in zip(pts, pts[1:])) if len(pts) > 1 else \
        math.hypot(x - pts[0][0], y - pts[0][1])


def _rect_dist(x, y, x0, y0, x1, y1):
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


VALLEY_EDGE = [(-52, -62), (135, -62), (135, 58), (-125, 58), (-125, 30), (-110, 0), (-92, -18), (-78, -32),
               (-56, -54), (-52, -62)]


def valley_edge_dist(x, y):
    return _pl_dist(x, y, VALLEY_EDGE)


class Rules:
    """distancias do vale: trilho, meio-fio, pegadas das construcoes, area andavel e rotas do fm_qa"""

    def __init__(self):
        import fm_buildings, fm_mine
        self.paths = [([(p[0], p[1]) for p in pts], w) for pts, w in fm_buildings.PATHS.values()]
        self.rail = [(p.x, p.y) for p in fm_mine.rail_path(fm_mine.tunnel_frame())]
        self.feet = []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(("FORGE_", "BLD_", "WATER_Waterwheel", "MINE_Entrance")):
                continue
            if o.name.startswith("BLD_Bridges"):
                continue
            cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
            self.feet.append((min(c.x for c in cs), min(c.y for c in cs), max(c.x for c in cs), max(c.y for c in cs),
                              o.name))
        self.doors = [(o.location.x, o.location.y) for o in bpy.data.objects
                      if o.type == "EMPTY" and o.name.startswith(("DOOR_", "MINE_Entrance", "PLAYER_INTERACT_"))]
        self.routes = []
        try:
            import fm_qa
            for pts, z0 in fm_qa.routes().values():
                self.routes.append([(p[0], p[1]) for p in pts])
        except Exception as e:   # sem o QA: a regra de copa alta continua valendo pelos caminhos
            print("VEG aviso: rotas do fm_qa indisponiveis", e)

    def rail_d(self, x, y):
        return _pl_dist(x, y, self.rail)

    def curb_d(self, x, y):
        """distancia ao meio-fio (borda do caminho); negativa = em cima do caminho"""
        return min(_pl_dist(x, y, pts) - w / 2 for pts, w in self.paths)

    def foot_d(self, x, y):
        return min(_rect_dist(x, y, f[0], f[1], f[2], f[3]) for f in self.feet)

    def route_d(self, x, y):
        return min((_pl_dist(x, y, r) for r in self.routes), default=1e9)

    def stair_d(self, x, y):
        """distancia ao lance 1 das escadas dos portais (o jogador sobe ate z 14: copa nenhuma por cima)"""
        return min(_rect_dist(x, y, px - 7.5, L.FLIGHT1_Y0 - 3, px + 7.5, L.MID_FRONT_Y + 2) for px in L.PORTAL_X)

    def walk_d(self, x, y):
        """distancia a area andavel: caminhos, praca, avenida, portas, rotas do QA, entorno dos galpoes abertos
        e os corredores das escadas dos portais"""
        d = self.curb_d(x, y)
        d = min(d, math.hypot(x, y + 30.0) - 26.0, _rect_dist(x, y, -11, -120, 11, -52))
        d = min(d, self.route_d(x, y) - 1.2)
        for (dx, dy) in self.doors:
            d = min(d, math.hypot(x - dx, y - dy) - 3.0)
        for f in self.feet:
            if f[4] in ("BLD_Crystal_Shed", "BLD_Rail_Weigh_Station"):
                d = min(d, _rect_dist(x, y, f[0], f[1], f[2], f[3]) - 3.0)
        for px in L.PORTAL_X:
            d = min(d, _rect_dist(x, y, px - 7, 44, px + 7, 64))
        return d


class Sight:
    """visadas que nenhuma copa pode cortar: spawn -> loja/Ignis/mina/portais/roda e praca -> portais/mina/portas"""

    CELL = 6.0

    def __init__(self):
        M = {o.name: o.location.copy() for o in bpy.data.objects if o.type == "EMPTY"}

        def mk(n, dz):
            p = M.get(n)
            return (p.x, p.y, p.z + dz) if p is not None else None
        portals = [mk(n, 0.0) for n in M if n.startswith("PORTAL_")]
        shop, mine = mk("DOOR_Shop", 3.0), mk("MINE_Entrance", 5.0)
        doors = [mk(n, 3.0) for n in M if n.startswith("DOOR_") and n != "DOOR_Loft"]
        spawn_t = [t for t in [shop, (0.0, -5.0, 8.5), mine, (62.0, 20.0, 12.0)] + portals if t]
        plaza_t = [t for t in portals + doors + [mine, (112.0, -34.0, 8.0)] if t]
        segs = [(e, t) for e in ((0.0, -104.0, 5.5), (0.0, -112.0, 12.0), (0.0, -64.0, 9.5)) for t in spawn_t]
        segs += [((0.0, -30.0, 9.5), t) for t in plaza_t]
        self.g = {}
        for e, t in segs:
            e, t = Vector(e), Vector(t)
            ln = (t - e).length
            n = int(ln / 1.5)
            for i in range(n + 1):
                s = i * 1.5
                if s < 6.0 or s > ln - 3.0:
                    continue
                p = e.lerp(t, s / ln)
                self.g.setdefault((int(math.floor(p.x / self.CELL)), int(math.floor(p.y / self.CELL))), []).append(p)

    def blocks(self, x, y, z0, z1, r):
        rr = r * 0.85 + 0.4
        gx, gy = int(math.floor(x / self.CELL)), int(math.floor(y / self.CELL))
        reach = int(math.ceil(rr / self.CELL))
        for i in range(gx - reach, gx + reach + 1):
            for j in range(gy - reach, gy + reach + 1):
                for p in self.g.get((i, j), ()):
                    if z0 - 0.3 < p.z < z1 and (p.x - x) ** 2 + (p.y - y) ** 2 < rr * rr:
                        return True
        return False


# ------------------------------------------------------------------ zonas
def classify(x, y, z, m):
    """zona de um ponto de chao valido"""
    if m == "Grass" and abs(z - L.FLOOR) < 0.6 and L.WEST_X - 1 < x < L.EAST_X + 1 and -62 < y < 60:
        return "valley"
    if m == "Grass" and abs(z - L.TERR) < 0.8 and L.UPPER_FRONT_Y < y < L.TERR_BACK_Y + 30:
        return "terrace"
    if y < -62 and -4 < z < 8 and m == "Grass":
        return "south"
    if z < 10:
        return None
    if m == "Grass_Dark":
        return "plateau"
    d = _rect_dist(x, y, L.WEST_X, -62, L.EAST_X, L.TERR_BACK_Y)
    return "rim" if d < 32 else "mountain"


def konoha_corridor(x, y):
    return -126 < x < -76 and y > 118


def terrace_excl(x, y):
    """terraco dos portais: arvores so no fundo e longe dos portais (portal sempre legivel do spawn)"""
    return y < L.PORTAL_Y + 6 or min(abs(x - px) for px in L.PORTAL_X) < 26


def portal_view(x, y):
    """faixa de visada de cada portal (escadas, ponte, ledge, berma do muro, terraco e a crista logo atras
    do anel): sem arvores - o portal le limpo do spawn e das laterais"""
    d = min(abs(x - px) for px in L.PORTAL_X)
    span = min(L.PORTAL_X) - 24 < x < max(L.PORTAL_X) + 24
    return (L.MID_FRONT_Y - 2 < y < L.TERR_BACK_Y and span) or (L.MID_FRONT_Y - 2 < y < 154 and d < 14)


# ------------------------------------------------------------------ setores de streaming
# (nome, x0, y0, x1, y1) pelo pe da arvore; cada setor vira UMA malha (cada material = 1 MeshPart <= 150 studs).
# Fora dos setores nao nasce vegetacao (planalto de tras escondido pelas faixas de montanha, picos distantes).
SECTORS = [
    ("VEG_Vale_Oeste", -128.0, -72.0, 5.0, 61.0),
    ("VEG_Vale_Leste", 5.0, -72.0, 138.0, 61.0),
    ("VEG_Queda_Sul_Oeste", -128.0, -150.0, 5.0, -72.0),
    ("VEG_Queda_Sul_Leste", 5.0, -150.0, 138.0, -72.0),
    ("VEG_Norte_Oeste", -128.0, 61.0, 5.0, 190.0),
    ("VEG_Norte_Leste", 5.0, 61.0, 138.0, 190.0),
    ("VEG_Oeste_Sul", -222.0, -150.0, -128.0, -18.0),
    ("VEG_Oeste_Norte", -222.0, -18.0, -128.0, 110.0),
    ("VEG_Noroeste", -222.0, 110.0, -128.0, 236.0),
    ("VEG_Leste_Sul", 138.0, -150.0, 232.0, -18.0),
    ("VEG_Leste_Norte", 138.0, -18.0, 232.0, 110.0),
    ("VEG_Nordeste", 138.0, 110.0, 232.0, 236.0),
]


def sector_of(x, y, margin=0.0):
    for (n, x0, y0, x1, y1) in SECTORS:
        if x0 + margin <= x < x1 - margin and y0 + margin <= y < y1 - margin:
            return n
    return None


# ------------------------------------------------------------------ campo de aglomerados
class Field:
    def __init__(self):
        self.c = []

    def add(self, x, y, R, dens, tag=None):
        self.c.append((x, y, R, dens, tag))

    def value(self, x, y):
        best, bc = 0.0, None
        for c in self.c:
            d2 = ((x - c[0]) ** 2 + (y - c[1]) ** 2) / (c[2] * c[2])
            if d2 > 4.0:
                continue
            v = math.exp(-1.6 * d2) * c[3]
            if v > best:
                best, bc = v, c
        return best, bc


def poisson_pick(points, rng, dmin, keep=1.0, weight=None):
    """centros espalhados (disco de Poisson) sobre os pontos validos; 'keep' abre clareiras"""
    pts = list(points)
    rng.shuffle(pts)
    if weight:
        pts.sort(key=lambda p: -weight(p) * rng.uniform(0.5, 1.0))
    out = []
    d2 = dmin * dmin
    for p in pts:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= d2 for q in out):
            out.append(p)
    return [p for p in out if rng.random() < keep]


def pick(rng, mix):
    t = rng.random() * sum(w for _, w in mix)
    for k, w in mix:
        t -= w
        if t <= 0:
            return k
    return mix[-1][0]


# alcance da copa (x h) - inclui bracos e almofadas (guarda-chuva, sakura, folhosa)
CANOPY = {"fir": 0.31, "windswept": 0.34, "spruce": 0.23, "young": 0.44, "umbrella": 0.55, "broad": 0.48,
          "sakura": 0.56, "dead": 0.3, "snag": 0.12}
CLEAR = 6.0   # altura livre sob copas perto de area andavel (5,5 acima do calcamento, que fica 0,5 acima da grama)


def canopy_r(kind, h):
    return h * CANOPY[kind]


# ------------------------------------------------------------------ tampas de grama (topos/patamares de coluna)
CAP_SKIP = ("TER_Far_Valley", "TER_PortalTerrace", "TER_Floor_Grass", "TER_Mountains_Peaks")


def find_caps():
    """componentes conexos de faces 'Grass' planas acima do vale (tampas dos blocos de rocha dos penhascos)"""
    caps = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("TER_") or o.name in CAP_SKIP:
            continue
        me = o.data
        mats = [m.name if m else "" for m in me.materials]
        mw = o.matrix_world
        m3 = mw.to_3x3()
        polys = me.polygons
        sel = []
        for p in polys:
            if mats[p.material_index] != "Grass":
                continue
            if (m3 @ p.normal).normalized().z < 0.86:
                continue
            c = mw @ p.center
            if c.z < 10.0 or sector_of(c.x, c.y) is None:
                continue
            sel.append(p.index)
        sset = set(sel)
        vf = {}
        for i in sel:
            for v in polys[i].vertices:
                vf.setdefault(v, []).append(i)
        seen = set()
        for i in sel:
            if i in seen:
                continue
            comp, st = [], [i]
            seen.add(i)
            while st:
                k = st.pop()
                comp.append(k)
                for v in polys[k].vertices:
                    for g in vf[v]:
                        if g not in seen and g in sset:
                            seen.add(g)
                            st.append(g)
            area = sum(polys[k].area for k in comp)
            if area < 6.0 or area > 900.0:
                continue
            P = [mw @ me.vertices[v].co for v in {v for k in comp for v in polys[k].vertices}]
            cx = sum(p.x for p in P) / len(P)
            cy = sum(p.y for p in P) / len(P)
            cz = max(p.z for p in P)
            r = max(math.hypot(p.x - cx, p.y - cy) for p in P)
            caps.append({"x": cx, "y": cy, "z": cz, "r": r, "area": area})
    return caps


# ------------------------------------------------------------------ montagem
def build():
    PLACED.clear()
    STATS.clear()
    rng = random.Random(1010)
    bvh, mats = surface_bvh()
    blk = Blockers()
    R = Rules()
    sight = Sight()
    sp = Spacing()
    items = []          # (x, y, semente, fn(mb, rng)) - geometria agendada, montada por setor no fim
    tri_zone = {}

    def put(x, y, fn, zone="misc"):
        items.append((x, y, rng.random(), fn, zone))

    def ground(x, y, top=260.0):
        hit = bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)), 400)
        if hit[0] is None:
            return None
        return hit[0], hit[1], mats[hit[2]]

    def plant(zone, kind, x, y, z, h, lod, clear=None, wind=None, lean=None):
        """agenda uma arvore; lean = (angulo, graus) inclina a arvore inteira para fora"""
        def fn(mb, r, kind=kind, x=x, y=y, z=z, h=h, lod=lod, clear=clear, wind=wind, lean=lean):
            n0 = len(mb.bm.verts)
            K.tree(kind, mb, (x, y, z - 0.25), h, r, lod, wind=wind, clear=clear)
            if lean:
                K.lean_new(mb, n0, (x, y, z - 0.25), lean[0], math.radians(lean[1]))
        put(x, y, fn, zone)
        PLACED.append((zone, kind, round(x, 1), round(y, 1), round(z, 1), round(h, 1)))
        STATS.setdefault("especies", {})
        k = zone + ":" + kind + (":inclinada" if lean else "")
        STATS["especies"][k] = STATS["especies"].get(k, 0) + 1

    # ---------------- amostragem da superficie (grade com jitter)
    pool = {"valley": [], "terrace": [], "south": [], "rim": [], "mountain": [], "plateau": []}
    step = 2.4
    x = -222.0
    while x < 232.0:
        y = -150.0
        while y < 236.0:
            px, py = x + rng.uniform(-0.9, 0.9), y + rng.uniform(-0.9, 0.9)
            y += step
            if konoha_corridor(px, py) or sector_of(px, py, 1.0) is None:
                continue
            g = ground(px, py)
            if not g or g[2] not in ("Grass", "Grass_Dark") or g[1].z < 0.86:
                continue
            zone = classify(px, py, g[0].z, g[2])
            if zone:
                pool[zone].append((px, py, g[0].z))
        x += step
    for k in pool:
        rng.shuffle(pool[k])

    dirs8 = [(math.cos(a), math.sin(a)) for a in (i * math.tau / 8 for i in range(8))]

    def near_cliff(x, y, z, d=6.0, rise=4.0):
        for (cx, cy) in dirs8:
            g = ground(x + cx * d, y + cy * d)
            if g and g[0].z > z + rise:
                return True
        return False

    # =====================================================================================================
    # 1) VALE
    # =====================================================================================================
    col_cands = []

    def valley_site(x, y):
        g = ground(x, y, 20.0)
        if not g or g[2] != "Grass" or g[1].z < 0.86:
            return None
        z = g[0].z
        if classify(x, y, z, g[2]) != "valley" or blk.blocked(x, y, z):
            return None
        return z

    why = {}

    def fail(kind, reason):
        why.setdefault(kind, {})
        why[kind][reason] = why[kind].get(reason, 0) + 1
        return False

    def valley_tree(x, y, kind, h, lod=0, kmin=0.5, tag="valley"):
        """valida (trilho, meio-fio, pegadas, area andavel, visadas, espacamento) e agenda uma arvore do vale"""
        z = valley_site(x, y)
        if z is None or sector_of(x, y, 3.0) is None:
            return fail(kind, "chao")
        wd = R.walk_d(x, y)
        clear = None
        cr = canopy_r(kind, h)
        if kind in ("broad", "sakura", "umbrella"):
            clear = CLEAR
        elif wd - cr < 3.0:
            # a menos de 3 studs de area andavel: copa alta (base >= 5,5 acima do chao)
            if kind == "young":
                return fail(kind, "jovem_perto_andavel")
            h = max(h, rng.uniform(15.5, 18.0))
            clear = CLEAR
            cr = canopy_r(kind, h) * 0.9
            if wd - cr < -1.5 and kind != "spruce":
                return fail(kind, "copa_sobre_caminho")
        if R.rail_d(x, y) < (4.5 if clear else max(4.5, cr + 1.0)):
            return fail(kind, "trilho")
        if R.curb_d(x, y) < 1.5:
            return fail(kind, "meio_fio")
        if R.foot_d(x, y) < cr + 2.0:
            return fail(kind, "pegada")
        if R.stair_d(x, y) < cr + 0.8:
            return fail(kind, "escada")
        cb = clear if clear is not None else 0.6
        if sight.blocks(x, y, z + cb, z + h, cr):
            return fail(kind, "visada")
        if not sp.free(x, y, cr, kmin):
            return fail(kind, "espaco")
        sp.add(x, y, cr)
        plant(tag, kind, x, y, z, h, lod, clear=clear)
        rd = R.route_d(x, y)
        if rd <= 8.0 and kind not in ("dead", "snag"):
            tr = h * (0.05 if kind in ("broad", "sakura", "umbrella") else 0.045)
            col_cands.append((rd, x, y, z, max(1.6, tr * 2.6), clear or 0.0, h))
        return True

    vpts = [p for p in pool["valley"] if not blk.blocked(p[0], p[1], p[2])]
    STATS["valley_pts"] = len(vpts)

    def near_pts(ax, ay, rad):
        """pontos validos do gramado perto de uma ancora de direcao de arte (mais perto primeiro, com jitter)"""
        c = [p for p in vpts if (p[0] - ax) ** 2 + (p[1] - ay) ** 2 < rad * rad]
        c.sort(key=lambda p: (p[0] - ax) ** 2 + (p[1] - ay) ** 2 + rng.uniform(0, rad * rad * 0.6))
        return c

    # (a) sakura moderada no lado oeste (perto do portal Naruto e das cabanas), com petalas caidas no gramado
    n_sak = 0
    for (ax, ay) in ((-120, 27), (-92, 52), (-121, 50), (-68, 4), (-122, 8), (-108, 32), (-50, 52), (-84, 32),
                     (-116, -12), (-26, 52), (-72, -4), (-100, -24)):
        if n_sak >= 5:
            break
        for (qx, qy, qz) in near_pts(ax, ay, 9.0)[:24]:
            if valley_tree(qx, qy, "sakura", rng.uniform(10.0, 12.5), 0, 0.55):
                n_sak += 1
                zz = PLACED[-1][4]

                def petals(mb, r, qx=qx, qy=qy, zz=zz):
                    for j in range(r.randint(3, 5)):
                        a, dd = r.uniform(0, math.tau), r.uniform(1.5, 4.5)
                        K.blossom(mb, (qx + math.cos(a) * dd, qy + math.sin(a) * dd, zz + 0.05), r.uniform(0.3, 0.45),
                                  "Sakura_Pink", r)
                put(qx, qy, petals, "valley_low")
                break

    # (b) pinheiros-guarda-chuva (lado oeste, clima Konoha)
    n_umb = 0
    for (ax, ay) in ((-116, -2), (-60, 52), (-104, 36), (-30, 52), (-119, 42)):
        if n_umb >= 3:
            break
        for (qx, qy, qz) in near_pts(ax, ay, 9.0)[:24]:
            if valley_tree(qx, qy, "umbrella", rng.uniform(12.0, 14.5), 0, 0.6):
                n_umb += 1
                break

    # (c) folhosas de copa redonda perto das casas e da praca (15-20% das arvores do vale)
    broad_c = []
    for f in R.feet:
        if not f[4].startswith(("BLD_Cabin", "BLD_Shop", "BLD_WheelHouse", "BLD_Crystal")):
            continue
        cx, cy = (f[0] + f[2]) / 2, (f[1] + f[3]) / 2
        for k in range(16):
            a = k * math.tau / 16 + rng.uniform(-0.1, 0.1)
            dd = max(f[2] - f[0], f[3] - f[1]) * 0.5 + rng.uniform(6.5, 10.0)
            broad_c.append((cx + math.cos(a) * dd, cy + math.sin(a) * dd))
    for k in range(24):
        a = k * math.tau / 24
        broad_c.append((math.cos(a) * rng.uniform(33, 40), -30.0 + math.sin(a) * rng.uniform(33, 40)))
    rng.shuffle(broad_c)
    n_broad = 0
    placed_b = []
    for (px, py) in broad_c:
        if n_broad >= 10:
            break
        if any(math.hypot(px - qx, py - qy) < 20 for qx, qy in placed_b):
            continue
        if valley_tree(px, py, "broad", rng.uniform(9.0, 12.0), 0, 0.6, "valley"):
            n_broad += 1
            placed_b.append((px, py))

    # (d) mureta sul: 3-4 bosquetes (arvore + moitas) com vaos de 15 studs ou mais (antes: cerca-viva reta)
    SOUTH_GROVES = [(44.0, 55.0), (70.0, 82.0), (98.0, 110.0), (126.0, 134.0)]
    n_sg = 0
    for (xa, xb) in SOUTH_GROVES:
        planted = 0
        for i in range(40):
            if planted >= 2:
                break
            px, py = rng.uniform(xa, xb), rng.uniform(-58.5, -52.0)
            kind = pick(rng, [("fir", 0.4), ("young", 0.35), ("spruce", 0.25)])
            h = rng.uniform(6.0, 8.5) if kind == "young" else rng.uniform(11.0, 16.0)
            if valley_tree(px, py, kind, h, 0, 0.55, "valley"):
                planted += 1
        n_sg += planted > 0
        STATS.setdefault("south_groves", []).append((xa, xb, planted))

    # (e) molduras: bosques junto aos penhascos/paredes (centros por Poisson com peso na borda) + ancoras de
    #     direcao de arte (cantos e pe dos penhascos). Nenhuma ancora no eixo do spawn (sem par espelhado).
    vf = Field()
    for (cx, cy, cz) in poisson_pick(vpts[:4000], rng, 21.0, 0.85, lambda p: 1.0 / (5.0 + valley_edge_dist(p[0], p[1]))):
        e = valley_edge_dist(cx, cy)
        if e > 16 or cy < -50:
            continue                    # mureta sul: so os bosquetes (d)
        vf.add(cx, cy, rng.uniform(6.0, 10.0), rng.uniform(0.7, 1.0))
    for (ax, ay, Rr, dens) in ((-118, 20, 9, 1.0), (-114, 50, 8, 0.9), (-104, -6, 7, 0.8), (-90, -26, 6, 0.7),
                               (128, -46, 8, 0.9), (129, -12, 7, 0.8), (128, 32, 7, 0.9), (124, 52, 8, 1.0),
                               (-80, 52, 5, 0.7), (92, 52, 6, 0.8)):
        vf.add(ax, ay, Rr, dens)
    n_valley = 0
    VALLEY_MAX = 34
    cl = list(vf.c)
    rng.shuffle(cl)
    for (cx, cy, Rr, dens, tag) in cl:
        if n_valley >= VALLEY_MAX:
            break
        dom = pick(rng, [("fir", 0.55), ("spruce", 0.45)])
        want = max(2, min(5, int(round(Rr * dens * 0.42))))
        got = tries = 0
        while got < want and tries < want * 12 and n_valley < VALLEY_MAX:
            tries += 1
            a = rng.uniform(0, math.tau)
            d = abs(rng.gauss(0.0, Rr * 0.5))
            if d > Rr * 1.2:
                continue
            px, py = cx + math.cos(a) * d, cy + math.sin(a) * d
            q = d / Rr
            kind = "young" if (q > 0.8 and rng.random() < 0.4) else (dom if rng.random() < 0.7 else
                                                                    pick(rng, [("fir", 0.5), ("spruce", 0.5)]))
            h = rng.uniform(9.0, 13.0) if q > 0.6 else rng.uniform(12.0, 19.0)
            if kind == "young":
                h = rng.uniform(6.0, 9.0)
            if valley_edge_dist(px, py) > 12:
                h = min(h, 15.0)
            if valley_tree(px, py, kind, h, 0, 0.5 if q < 0.6 else 0.62):
                got += 1
                n_valley += 1

    # (f) arvores secas de destaque: a mina e area arida; margem leste com uma seca
    for (cx, cy, kind, h) in ((-88, -40, "snag", 11.0), (-100, -10, "dead", 9.5), (126, -54, "dead", 9.0)):
        for (qx, qy, qz) in near_pts(cx, cy, 9.0)[:24]:
            if valley_tree(qx, qy, kind, h, 0, 0.7):
                break
    STATS["valley_trees"] = {"molduras": n_valley, "bosquetes_sul": n_sg, "folhosas": n_broad, "sakura": n_sak,
                             "guarda_chuva": n_umb}
    STATS["vale_rejeicoes"] = why

    # COL de tronco: so a <= 8 studs de uma rota do fm_qa (as mais proximas, orcamento)
    col_cands.sort()
    n_col = 0
    for (rd, x, y, z, w, clear, h) in col_cands[:18]:
        hc = max(5.2, min(clear if clear else h * 0.4, 7.0))
        col_box("Veg", (w, w, hc), (x, y, z + hc / 2))
        n_col += 1
    STATS["col_tronco"] = n_col

    # ---------------- sub-bosque do vale
    n_u = {}

    def low(kind, x, y, z, fn, r):
        if not sp.free(x, y, r, 0.9):
            return False
        sp.add(x, y, r)
        put(x, y, fn, "valley_low")
        n_u[kind] = n_u.get(kind, 0) + 1
        return True

    # talude: pe dos penhascos do vale (samambaia, moita, pedra com musgo, pedra solta), em manchas
    for (x, y, z) in pool["valley"]:
        if n_u.get("talude", 0) >= 34:
            break
        if valley_edge_dist(x, y) > 8 or blk.blocked(x, y, z) or R.rail_d(x, y) < 3.5:
            continue
        if noise.noise(Vector((x * 0.06, y * 0.06, 3.1))) < -0.05 or rng.random() > 0.35:
            continue
        k = pick(rng, [("fern", 0.34), ("bush", 0.3), ("rockplant", 0.2), ("boulder", 0.16)])
        s = rng.uniform(1.4, 2.3)
        if R.curb_d(x, y) < s + 0.4 or not near_cliff(x, y, z):
            continue
        if k == "fern":
            fn = (lambda mb, r, x=x, y=y, z=z, s=s: K.fern(mb, (x, y, z - 0.2), s, r))
        elif k == "bush":
            fn = (lambda mb, r, x=x, y=y, z=z, s=s: K.bush(mb, (x, y, z - 0.2), s, r, lod=0))
        elif k == "rockplant":
            fn = (lambda mb, r, x=x, y=y, z=z, s=s: K.rock_plant(mb, (x, y, z), s * 0.8, r))
        else:
            fn = (lambda mb, r, x=x, y=y, z=z, s=s: K.boulder(mb, (x, y, z), s, r))
        if low("talude", x, y, z, fn, s):
            n_u[k] = n_u.get(k, 0) + 1

    # canteiros na base das casas (fora das portas e dos caminhos)
    for f in R.feet:
        if not f[4].startswith(("BLD_Cabin", "BLD_Shop", "BLD_WheelHouse")):
            continue
        x0, y0, x1, y1 = f[0], f[1], f[2], f[3]
        sides = [((x0, y0), (x1, y0), (0, -1)), ((x1, y0), (x1, y1), (1, 0)), ((x1, y1), (x0, y1), (0, 1)),
                 ((x0, y1), (x0, y0), (-1, 0))]
        rng.shuffle(sides)
        beds = 0
        for (a, b, nrm) in sides:
            if beds >= 2:
                break
            for i in range(6):
                t = rng.uniform(0.15, 0.85)
                px = a[0] + (b[0] - a[0]) * t + nrm[0] * 1.6
                py = a[1] + (b[1] - a[1]) * t + nrm[1] * 1.6
                if min(math.hypot(px - dx, py - dy) for dx, dy in R.doors) < 5.0 or R.curb_d(px, py) < 2.2:
                    continue
                g = ground(px, py, 20.0)
                if not g or g[2] != "Grass" or abs(g[0].z - L.FLOOR) > 0.6:
                    continue
                z = g[0].z
                ang = math.atan2(nrm[1], nrm[0])

                def bed(mb, r, px=px, py=py, z=z, ang=ang):
                    K.bush(mb, (px, py, z - 0.2), r.uniform(1.0, 1.4), r, pal=("Leaf_Broad", K.LEAF), n=2, lod=0)
                    for j in range(r.randint(2, 3)):
                        a2 = ang + math.pi / 2 * r.choice((-1, 1))
                        dd = r.uniform(1.4, 2.6)
                        K.flowers(mb, (px + math.cos(a2) * dd, py + math.sin(a2) * dd, z), r.uniform(0.9, 1.2), r)
                if low("canteiro", px, py, z, bed, 1.6):
                    beds += 1
                    break

    # junco no pe das paredes do rio (dentro do canal, na linha d'agua) + moitas junto as cercas do rio
    rx0, rx1 = L.RIVER_X
    yv = -58.0
    side = 0
    while yv < 44.0:
        yv += rng.uniform(5.0, 10.0)
        if abs(yv - L.BRIDGE_MAIN_Y) < 7 or abs(yv - L.WHEEL_C[1]) < 12.5 or abs(yv - L.BRIDGE_BACK_Y) < 5 or yv > 44:
            continue
        side = 1 - side if rng.random() < 0.7 else side
        px = (rx0 + 1.1) if side == 0 else (rx1 - 1.1)
        n_u["junco"] = n_u.get("junco", 0) + 1
        put(px, yv, (lambda mb, r, px=px, yv=yv: K.reeds(mb, (px, yv, 2.8), r.uniform(1.1, 1.5), r)), "valley_low")
        if rng.random() < 0.45:
            py2 = yv + rng.uniform(1.5, 3.0)
            put(px, py2, (lambda mb, r, px=px, py2=py2: K.reeds(mb, (px, py2, 2.8), r.uniform(0.9, 1.2), r)),
                "valley_low")
    fence_n = 0
    for (x, y, z) in pool["valley"]:
        if fence_n >= 9:
            break
        if not (rx0 - 3.6 < x < rx0 - 1.6 or rx1 + 1.6 < x < rx1 + 3.6) or y > 40:
            continue
        if blk.blocked(x, y, z) and R.curb_d(x, y) < 1.0:
            continue
        s = rng.uniform(1.2, 1.8)
        if R.curb_d(x, y) < s + 0.4 or abs(y - L.WHEEL_C[1]) < 12 or R.foot_d(x, y) < 1.0:
            continue
        if noise.noise(Vector((x * 0.05, y * 0.05, 8.8))) < 0.0:
            continue
        if low("cerca_rio", x, y, z, (lambda mb, r, x=x, y=y, z=z, s=s: K.bush(mb, (x, y, z - 0.2), s, r, lod=0)), s):
            fence_n += 1

    # bosquetes da mureta sul: moitas e flores em volta das arvores (b)
    for (xa, xb) in SOUTH_GROVES:
        for i in range(3):
            px, py = rng.uniform(xa - 2, xb + 2), rng.uniform(-59.5, -54.0)
            z = valley_site(px, py)
            s = rng.uniform(1.4, 2.0)
            if z is None or R.curb_d(px, py) < s + 0.4:
                continue
            fn = (lambda mb, r, px=px, py=py, z=z, s=s: K.bush(mb, (px, py, z - 0.2), s, r, lod=0)) if i < 2 else \
                (lambda mb, r, px=px, py=py, z=z, s=s: K.flower_bush(mb, (px, py, z - 0.2), s, r))
            low("bosquete_sul", px, py, z, fn, s)

    # manchas de grama (5-12 tufos) com flores, separadas por gramado aberto
    lawn = [p for p in vpts if R.curb_d(p[0], p[1]) > 1.2 and R.rail_d(p[0], p[1]) > 3.0]
    n_patch = 0
    for (cx, cy, cz) in poisson_pick(lawn[:3000], rng, 17.0, 0.8):
        if n_patch >= 14:
            break
        if noise.noise(Vector((cx * 0.04, cy * 0.04, 1.3))) < -0.25:
            continue
        nt = rng.randint(5, 12)
        col = rng.choice(K.FLOWERS)
        pr = rng.uniform(2.2, 3.6)
        tufts = []
        for i in range(nt * 3):
            if len(tufts) >= nt:
                break
            a, d = rng.uniform(0, math.tau), pr * math.sqrt(rng.random())
            px, py = cx + math.cos(a) * d, cy + math.sin(a) * d
            if R.curb_d(px, py) < 0.8 or R.walk_d(px, py) < 0.5 or blk.blocked(px, py, cz):
                continue
            tufts.append((px, py, rng.random() < 0.22))
        if len(tufts) < 5:
            continue

        def patch(mb, r, tufts=tufts, cz=cz, col=col):
            for (px, py, fl) in tufts:
                if fl:
                    K.flowers(mb, (px, py, cz), r.uniform(1.0, 1.35), r, col)
                else:
                    K.grass_tuft(mb, (px, py, cz), r.uniform(0.9, 1.5), r)
        put(cx, cy, patch, "valley_low")
        n_patch += 1
    n_u["manchas_grama"] = n_patch

    # cristais: so no macico SW, na boca da mina e em fendas; grupos de 3-5 + 2 pedras (nada no gramado aberto)
    mx, my = L.MINE_MOUTH
    fd = Vector((0.7071, -0.7071))        # ao longo da face da mina
    fo = Vector((0.7071, 0.7071))         # face -> vale
    cr_spots = [(mx - fd.x * 10.5 + fo.x * 2.0, my - fd.y * 10.5 + fo.y * 2.0),
                (mx + fd.x * 10.5 + fo.x * 2.0, my + fd.y * 10.5 + fo.y * 2.0),
                (-104.0, -4.0), (-86.0, -30.0)]
    n_cr = 0
    for (cx, cy) in cr_spots:
        for i in range(24):
            px, py = cx + rng.uniform(-3, 3), cy + rng.uniform(-3, 3)
            g = ground(px, py, 20.0)
            if not g or g[2] != "Grass" or abs(g[0].z - L.FLOOR) > 0.6:
                continue
            if R.rail_d(px, py) < 3.5 or R.curb_d(px, py) < 2.4 or not near_cliff(px, py, g[0].z, 7.0):
                continue
            if math.hypot(px - mx, py - my) < 8.0 or not sp.free(px, py, 2.5, 0.8):
                continue
            z = g[0].z
            sp.add(px, py, 2.5)
            put(px, py, (lambda mb, r, px=px, py=py, z=z: K.crystal_outcrop(mb, (px, py, z), r.uniform(0.9, 1.2), r)),
                "valley_low")
            if R.route_d(px, py) <= 8.0:
                col_box("Veg", (3.2, 3.2, 3.6), (px, py, z + 1.8))
                STATS["col_cristal"] = STATS.get("col_cristal", 0) + 1
            n_cr += 1
            break
    STATS["cristais_vale"] = n_cr
    STATS["sub_bosque_vale"] = n_u

    # =====================================================================================================
    # 2) TAMPAS DAS BORDAS E MONTANHAS
    # =====================================================================================================
    caps = find_caps()
    ok_caps = []
    for c in caps:
        x, y = c["x"], c["y"]
        if portal_view(x, y) or konoha_corridor(x, y):
            continue
        g = ground(x, y)
        zone = classify(x, y, c["z"], "Grass") if g else None
        if zone not in ("rim", "mountain"):
            continue
        c["zone"] = zone
        # lado de fora (maior queda) e patamar/fenda (parede mais alta encostada)
        drops = []
        for k in range(12):
            a = k * math.tau / 12
            gg = ground(x + math.cos(a) * (c["r"] + 3.0), y + math.sin(a) * (c["r"] + 3.0))
            drops.append((c["z"] - gg[0].z) if gg else 60.0)
        sm = [drops[k - 1] * 0.25 + drops[k] * 0.5 + drops[(k + 1) % 12] * 0.25 for k in range(12)]
        kbest = max(range(12), key=lambda k: sm[k])
        c["out"] = kbest * math.tau / 12 if sm[kbest] > 2.0 else math.atan2(y - 30.0, x)
        c["ledge"] = sum(1 for d in drops if d < -4.0) >= 2
        # proximo = le do vale/terraco (lod medio); fundo = lod leve
        c["near"] = zone == "rim" and _rect_dist(x, y, L.WEST_X, -62, L.EAST_X, L.TERR_BACK_Y) < 30
        # campo de aglomerados: ruido de baixa frequencia (trechos de 20-30 studs sem arvore) + bonus em
        # patamares/fendas (abrigo) + um pouco de ruido fino
        v = noise.noise(Vector((x * 0.021 + 3.1, y * 0.021 - 1.7, 0.4)))
        v += 0.3 * noise.noise(Vector((x * 0.08, y * 0.08, 2.2))) + (0.18 if c["ledge"] else 0.0)
        c["v"] = v
        ok_caps.append(c)
    ok_caps.sort(key=lambda c: -c["v"])
    nC = len(ok_caps)
    for i, c in enumerate(ok_caps):
        q = i / max(1, nC)
        c["fate"] = "group" if q < 0.27 else ("single" if q < 0.40 else "bush")
        if c["fate"] == "group" and c["area"] < 12.0:
            c["fate"] = "single"

    def cap_point(c, u0, u1, spread=0.7):
        ox, oy = math.cos(c["out"]), math.sin(c["out"])
        for i in range(24):
            u = rng.uniform(u0, u1)
            v = rng.uniform(-spread, spread)
            px = c["x"] + (ox * u - oy * v) * c["r"]
            py = c["y"] + (oy * u + ox * v) * c["r"]
            g = ground(px, py)
            if g and g[2] == "Grass" and abs(g[0].z - c["z"]) < 1.3 and g[1].z > 0.86:
                return px, py, g[0].z
        return None

    cap_tree = {"group": 0, "single": 0, "bush": 0}
    ntree_caps = 0
    for c in ok_caps:
        lod = 1 if c["near"] else 2
        zone = c["zone"]
        fate = c["fate"]
        if fate == "group":
            n = pick(rng, [(3, 0.3), (4, 0.34), (5, 0.21), (6, 0.15)])
            h0 = rng.uniform(10.0, 13.0) if zone == "rim" else rng.uniform(12.0, 15.0) * 1.2
            got = []
            for i in range(n * 6):
                if len(got) >= n:
                    break
                p = cap_point(c, 0.2, 0.95)
                if not p:
                    continue
                h = h0 * rng.uniform(0.6, 1.4)
                kind = pick(rng, [("fir", 0.5), ("spruce", 0.36), ("young", 0.14)]) if h > h0 * 0.8 else \
                    pick(rng, [("fir", 0.4), ("young", 0.35), ("spruce", 0.25)])
                if kind == "young":
                    h = min(h, 9.0)
                cr = canopy_r(kind, h)
                if any(math.hypot(p[0] - q[0], p[1] - q[1]) < max(1.6, 0.34 * (cr + q[2])) for q in got):
                    continue
                got.append((p[0], p[1], cr))
                plant(zone, kind, p[0], p[1], p[2], h, lod)
                sp.add(p[0], p[1], cr * 0.6)
            if got:
                ntree_caps += 1
                cap_tree["group"] += 1
            # moita pendente na borda tambem nos topos com grupo (1 em 2)
            if c["near"] and rng.random() < 0.5:
                fate = "bush"
        if fate == "single":
            p = cap_point(c, 0.45, 0.85, 0.4)
            if p:
                if rng.random() < 0.5:
                    plant(zone, "snag", p[0], p[1], p[2], rng.uniform(8.0, 13.0), lod)
                else:
                    kind = pick(rng, [("fir", 0.6), ("spruce", 0.4)])
                    plant(zone, kind, p[0], p[1], p[2], rng.uniform(9.0, 14.0), lod,
                          lean=(c["out"] + rng.uniform(-0.4, 0.4), rng.uniform(10.0, 25.0)))
                ntree_caps += 1
                cap_tree["single"] += 1
        if fate == "bush":
            # so moita/samambaia pendendo pela borda (nas tampas que o jogador enxerga); fundo: nua ou 1 moita
            if not c["near"] and rng.random() > 0.3:
                continue
            nb = 1 if (not c["near"] or c["area"] < 25 or rng.random() < 0.55) else 2
            for i in range(nb):
                p = cap_point(c, 0.8, 1.0, 0.5)
                if not p:
                    continue
                s = rng.uniform(1.5, 2.4) if c["near"] else rng.uniform(2.2, 3.0)
                oa = c["out"] + rng.uniform(-0.5, 0.5)
                put(p[0], p[1], (lambda mb, r, p=p, s=s, oa=oa, lod=lod:
                                 K.edge_bush(mb, (p[0], p[1], p[2] - 0.15), s, oa, r, m=K.LEAF, m2=K.LEAF, lod=lod)),
                    zone)
            cap_tree["bush"] += 1
    STATS["tampas"] = {"n": nC, "com_arvore": ntree_caps, "pct_sem_arvore": round(100.0 * (1 - ntree_caps / max(1, nC)), 1),
                       "destinos": cap_tree, "patamares": sum(1 for c in ok_caps if c["ledge"])}

    # =====================================================================================================
    # 3) PLANALTOS: 2-3 manchas densas grandes, clareiras com afloramentos, linha de arvores na borda
    # =====================================================================================================
    pts = [p for p in pool["plateau"] if not portal_view(p[0], p[1])]
    # regioes conexas (grade de amostras)
    cell = 4.0
    hsh = {}
    for i, p in enumerate(pts):
        hsh.setdefault((int(p[0] // cell), int(p[1] // cell)), []).append(i)
    reg = [-1] * len(pts)
    regions = []
    for i in range(len(pts)):
        if reg[i] >= 0:
            continue
        rid = len(regions)
        st, members = [i], []
        reg[i] = rid
        while st:
            k = st.pop()
            members.append(k)
            px, py, pz = pts[k]
            gx, gy = int(px // cell), int(py // cell)
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for j in hsh.get((gx + a, gy + b), ()):
                        if reg[j] < 0 and abs(pts[j][2] - pz) < 2.0 and \
                                (pts[j][0] - px) ** 2 + (pts[j][1] - py) ** 2 < 16.0:
                            reg[j] = rid
                            st.append(j)
        regions.append(members)
    n_grove = n_line = n_rock = n_log = 0
    GR = []
    for members in regions:
        if len(members) < 40:
            continue
        P = [pts[k] for k in members]
        area = len(P) * step * step
        # borda: queda forte a 5 studs
        edge, inner = [], []
        for (px, py, pz) in P:
            drop_dir = None
            for (dx, dy) in dirs8:
                g = ground(px + dx * 5.0, py + dy * 5.0)
                if not g or g[0].z < pz - 4.0:
                    drop_dir = (dx, dy)
                    break
            (edge if drop_dir else inner).append((px, py, pz, drop_dir))
        # manchas densas: 2-3 por planalto (1 nos pequenos), raio variando 2x
        ng = 3 if area > 9000 else (2 if area > 3500 else 1)
        centers = poisson_pick([p for p in inner if sector_of(p[0], p[1], 12.0)], rng, 58.0, 1.0)
        centers.sort(key=lambda p: noise.noise(Vector((p[0] * 0.013, p[1] * 0.013, 5.0))), reverse=True)
        got_g = 0
        for (cx, cy, cz, _) in centers:
            if got_g >= ng:
                break
            Rg = rng.uniform(11.0, 22.0)

            def inside(Rt, cx=cx, cy=cy, cz=cz):
                for k in range(10):
                    gg = ground(cx + math.cos(k * math.tau / 10) * Rt, cy + math.sin(k * math.tau / 10) * Rt)
                    if not gg or gg[2] != "Grass_Dark" or abs(gg[0].z - cz) > 3.0:
                        return False
                return True
            while Rg > 7.0 and not inside(Rg * 1.08):
                Rg *= 0.82          # a mancha inteira fica em cima do planalto (nada de copa flutuando na borda)
            if Rg <= 7.0 or sector_of(cx, cy, Rg * 0.7) is None:
                continue
            put(cx, cy, (lambda mb, r, cx=cx, cy=cy, cz=cz, Rg=Rg: K.grove(mb, (cx, cy, cz), Rg, r, lod=2,
                                                                          dome_m=K.UNDER)), "plateau")
            sp.add(cx, cy, Rg)
            GR.append((cx, cy, Rg))
            n_grove += 1
            got_g += 1
            # borda rasgada: arvores soltas em volta da mancha
            for k in range(rng.randint(4, 7)):
                a = rng.uniform(0, math.tau)
                d = Rg * rng.uniform(0.95, 1.35)
                px, py = cx + math.cos(a) * d, cy + math.sin(a) * d
                g = ground(px, py)
                if not g or g[2] != "Grass_Dark" or abs(g[0].z - cz) > 2.5 or portal_view(px, py):
                    continue
                h = rng.uniform(12.0, 20.0)
                plant("plateau", pick(rng, [("fir", 0.5), ("spruce", 0.5)]), px, py, g[0].z, h, 2)
        # linha de arvores na borda do penhasco, voltada para o vale (com vaos)
        edge.sort(key=lambda p: math.atan2(p[1] - 20.0, p[0]))
        last = None
        for (px, py, pz, dd) in edge:
            if (px * dd[0] + (py - 20.0) * dd[1]) > 0:
                continue            # borda de tras (invisivel do vale)
            if last and math.hypot(px - last[0], py - last[1]) < rng.uniform(6.5, 10.0):
                continue
            if noise.noise(Vector((px * 0.035, py * 0.035, 9.1))) < 0.0:
                last = (px, py)
                continue            # vao na linha
            if sector_of(px, py, 2.0) is None or not sp.free(px, py, 3.0, 0.6):
                continue
            plant("plateau", pick(rng, [("fir", 0.55), ("spruce", 0.45)]), px, py, pz, rng.uniform(11.0, 17.0), 2)
            sp.add(px, py, 3.0)
            last = (px, py)
            n_line += 1
        # clareiras: afloramentos de rocha (2-3 por planalto) e um tronco caido
        cl_pts = [p for p in inner if all(math.hypot(p[0] - g[0], p[1] - g[1]) > g[2] + 12 for g in GR)]
        for (px, py, pz, _) in poisson_pick(cl_pts, rng, 40.0, 1.0)[:rng.randint(2, 3)]:
            def outcrop(mb, r, px=px, py=py, pz=pz):
                for j in range(r.randint(2, 3)):
                    a, d = r.uniform(0, math.tau), r.uniform(0, 3.5)
                    K.boulder(mb, (px + math.cos(a) * d, py + math.sin(a) * d, pz), r.uniform(2.0, 4.2), r)
            put(px, py, outcrop, "plateau")
            sp.add(px, py, 5.0)
            n_rock += 1
        if cl_pts and n_log < 4:
            px, py, pz, _ = cl_pts[rng.randrange(len(cl_pts))]
            if sp.free(px, py, 4.0, 1.0):
                put(px, py, (lambda mb, r, px=px, py=py, pz=pz: K.fallen_log(mb, (px, py, pz - 0.3), r.uniform(6, 9),
                                                                            r.uniform(0.7, 1.0), r.uniform(0, 6), r)),
                    "plateau")
                n_log += 1
    STATS["planaltos"] = {"regioes": sum(1 for m in regions if len(m) >= 40), "manchas": n_grove, "linha": n_line,
                          "afloramentos": n_rock, "troncos": n_log}

    # =====================================================================================================
    # 4) TERRACO (fundo, longe dos portais) e QUEDA SUL (lajes de grama abaixo do vale)
    # =====================================================================================================
    n_ter = 0
    for (x, y, z) in pool["terrace"]:
        if n_ter >= 8:
            break
        if terrace_excl(x, y) or portal_view(x, y) or blk.blocked(x, y, z) or rng.random() > 0.2:
            continue
        kind = pick(rng, [("fir", 0.4), ("spruce", 0.35), ("young", 0.25)])
        h = rng.uniform(7.0, 9.0) if kind == "young" else rng.uniform(10.0, 13.0)
        cr = canopy_r(kind, h)
        if not sp.free(x, y, cr, 0.9):
            continue
        sp.add(x, y, cr)
        plant("terrace", kind, x, y, z, h, 1)
        n_ter += 1
    n_south = 0
    for (x, y, z) in pool["south"]:
        if n_south >= 7:
            break
        if abs(x) < 34 or blk.blocked(x, y, z) or rng.random() > 0.25:
            continue
        kind = pick(rng, [("young", 0.5), ("fir", 0.3), ("windswept", 0.2)])
        h = rng.uniform(6.0, 9.0) if kind == "young" else rng.uniform(8.0, 11.0)
        cr = canopy_r(kind, h)
        if not sp.free(x, y, cr, 1.0):
            continue
        sp.add(x, y, cr)
        plant("south", kind, x, y, z, h, 1, wind=math.atan2(-1.0, 0.0) if kind == "windswept" else None)
        n_south += 1
    STATS["terraco_sul"] = (n_ter, n_south)

    # =====================================================================================================
    # 5) MONTAGEM POR SETOR
    # =====================================================================================================
    by = {}
    dropped = 0
    for (x, y, seed, fn, zone) in items:
        s = sector_of(x, y)
        if s is None:
            dropped += 1
            continue
        by.setdefault(s, []).append((seed, fn, zone))
    sectors = {}
    for (name, x0, y0, x1, y1) in SECTORS:
        if name not in by:
            continue
        mb = MB(name, "09_VEGETATION")
        for seed, fn, zone in by[name]:
            f0 = len(mb.bm.faces)
            fn(mb, random.Random(seed))
            tri_zone[zone] = tri_zone.get(zone, 0) + len(mb.bm.faces) - f0     # faces (quads contam 1)
        ob = mb.finish()
        if ob is not None:
            sectors[name] = ob
    STATS["setores"] = len(sectors)
    STATS["itens_fora"] = dropped
    STATS["tris_por_zona"] = tri_zone
    print("VEG %s" % {k: v for k, v in STATS.items() if k not in ("especies",)})
    print("VEG especies=%s" % sorted(STATS.get("especies", {}).items()))
