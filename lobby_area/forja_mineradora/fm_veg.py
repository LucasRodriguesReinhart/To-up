# fm_veg - vegetacao por raycast na superficie real do terreno, com exclusao de caminhos e colisoes.
# Distribuicao em AGLOMERADOS com clareiras (campo de densidade por centros de bosque + ruido), especies e
# tamanhos misturados (kit em fm_veg_kit), LOD por zona (vale = heroi, borda = medio, montanhas = fundo).
# Enquadra (bordas, penhascos, terracos), quebra repeticao, esconde transicoes (pe de penhasco, meio-fio,
# base de construcao) e nunca bloqueia rota, portal, porta ou a forja.
import math, random
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree
from fm_lib import MB, D, col_box, point_in_poly
from fm_parts import crystal_cluster
import fm_layout as L
import fm_veg_kit as K


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
                                  "COL_EastCliff", "COL_MidWall", "COL_UpperWall", "COL_Konoha")):
                continue
            self.rects.append((o.location.copy(), o.rotation_euler.z, o.scale.x / 2 + margin, o.scale.y / 2 + margin,
                               o.location.z - o.scale.z / 2, o.location.z + o.scale.z / 2))
        # indice espacial (mesma regra, so acelera a consulta)
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
        cx, cy = 0.0, -30.0
        self.circles = [(cx, cy, 29.0), (L.DAIS_C[0], L.DAIS_C[1], L.DAIS_R + 5)]
        # corredores de circulacao que nao sao pavimentados
        for px in L.PORTAL_X:
            self.polys.append([(px - 11, 30), (px + 11, 30), (px + 11, 64), (px - 11, 64)])
            self.polys.append([(px - 14, L.FLIGHT2_Y1 - 2), (px + 14, L.FLIGHT2_Y1 - 2), (px + 14, L.PORTAL_Y + 9),
                               (px - 14, L.PORTAL_Y + 9)])
        self.polys.append([(-150, 60), (160, 60), (160, 82), (-150, 82)])   # ledge + canal
        self.polys.append([(-20, -120), (20, -120), (20, -52), (-20, -52)])  # spawn/avenida
        # visada da praca para a boca da mina (a mina tem que ser lida de longe)
        self.polys.append([(-20, -38), (-20, -52), (-60, -60), (-80, -46), (-66, -28), (-40, -24)])
        # pegada (bbox xy + 2) de cada construcao: nada nasce dentro de alas, torre, bolsoes da forja ou casas
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
        # marcadores de gameplay: portas, NPCs, pontos de interacao, portais e saidas de mundo ficam livres
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


# ------------------------------------------------------------------ zonas
VALLEY_EDGE = [(-52, -62), (135, -62), (135, 58), (-125, 58), (-125, 30), (-110, 0), (-92, -18), (-78, -32),
               (-56, -54), (-52, -62)]


def _seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-9)))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))


def valley_edge_dist(x, y):
    return min(_seg_dist(x, y, a, b) for a, b in zip(VALLEY_EDGE, VALLEY_EDGE[1:]))


def _rect_dist(x, y, x0, y0, x1, y1):
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


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
    # ledge, berma e terraco inteiros entre os portais extremos: das cameras laterais qualquer arvore
    # nessa faixa cai na frente de algum portal; alem disso, a crista logo atras de cada anel
    d = min(abs(x - px) for px in L.PORTAL_X)
    span = min(L.PORTAL_X) - 24 < x < max(L.PORTAL_X) + 24
    return (L.MID_FRONT_Y - 2 < y < L.TERR_BACK_Y and span) or (L.MID_FRONT_Y - 2 < y < 154 and d < 14)


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
    """centros de bosque espalhados (disco de Poisson) sobre os pontos validos; 'keep' abre clareiras"""
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


# especies por zona (pesos)
MIX = {
    "valley":   [("fir", 0.34), ("spruce", 0.24), ("young", 0.22), ("umbrella", 0.20)],
    "rim":      [("fir", 0.32), ("spruce", 0.30), ("young", 0.14), ("windswept", 0.14), ("umbrella", 0.06),
                 ("snag", 0.02), ("dead", 0.02)],
    "terrace":  [("fir", 0.34), ("spruce", 0.34), ("young", 0.2), ("umbrella", 0.12)],
    "south":    [("young", 0.45), ("fir", 0.3), ("windswept", 0.25)],
    "mountain": [("fir", 0.40), ("spruce", 0.42), ("young", 0.12), ("snag", 0.03), ("dead", 0.03)],
    "plateau":  [("fir", 0.38), ("spruce", 0.46), ("young", 0.14), ("snag", 0.02)],
}
SIZES = {"small": (5.0, 8.5), "medium": (9.0, 14.0), "large": (15.0, 21.0)}


def pick(rng, mix):
    t = rng.random() * sum(w for _, w in mix)
    for k, w in mix:
        t -= w
        if t <= 0:
            return k
    return mix[-1][0]


def size_class(rng, v):
    if v > 0.72:
        w = [("large", 0.55), ("medium", 0.35), ("small", 0.10)]
    elif v > 0.4:
        w = [("large", 0.2), ("medium", 0.55), ("small", 0.25)]
    else:
        w = [("large", 0.04), ("medium", 0.36), ("small", 0.60)]
    return pick(rng, w)


PLACED = []   # (zona, especie, x, y, z, h) de cada arvore - conferencia/QA


def build():
    PLACED.clear()
    rng = random.Random(1010)
    bvh, mats = surface_bvh()
    blk = Blockers()
    blk_wide = Blockers(margin=5.5, markers=False)
    sp = Spacing()

    def ground(x, y, top=260.0):
        hit = bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)), 400)
        if hit[0] is None:
            return None
        return hit[0], hit[1], mats[hit[2]]

    # ---------------- amostragem da superficie (grade com jitter)
    pool = {"valley": [], "terrace": [], "south": [], "rim": [], "mountain": [], "plateau": []}
    step = 2.4
    x = -236.0
    while x < 244.0:
        y = -126.0
        while y < 300.0:
            px, py = x + rng.uniform(-0.9, 0.9), y + rng.uniform(-0.9, 0.9)
            y += step
            if konoha_corridor(px, py):
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

    cliff_dirs = [(math.cos(a), math.sin(a)) for a in (i * math.tau / 8 for i in range(8))]

    def near_cliff(x, y, z, d=6.0, rise=4.0):
        for (cx, cy) in cliff_dirs:
            g = ground(x + cx * d, y + cy * d)
            if g and g[0].z > z + rise:
                return True
        return False

    # ---------------- construtores (um objeto por zona: streaming no Roblox)
    O = {k: MB(k, "09_VEGETATION", rng) for k in
         ("VEG_Valley_Trees", "VEG_Valley_Undergrowth", "VEG_Rim_Trees", "VEG_Rim_Undergrowth",
          "VEG_Mountain_Forest", "VEG_Deadwood", "VEG_Rocks")}
    TREE_OBJ = {"valley": "VEG_Valley_Trees", "terrace": "VEG_Rim_Trees", "south": "VEG_Rim_Trees",
                "rim": "VEG_Rim_Trees", "mountain": "VEG_Mountain_Forest", "plateau": "VEG_Mountain_Forest"}
    LOD = {"valley": 0, "terrace": 1, "south": 1, "rim": 1, "mountain": 2, "plateau": 2}
    stats = {}

    def plant_tree(zone, kind, x, y, z, h, wind=None):
        lod = LOD[zone]
        obj = TREE_OBJ[zone]
        if zone == "rim" and (y > 136 or x < -150 or x > 160 or y < -95):
            lod, obj = 2, "VEG_Mountain_Forest"      # faixas de fundo: versao leve
        mb = O["VEG_Deadwood"] if kind in ("dead", "snag") else O[obj]
        if kind == "umbrella":
            h = min(h, 16.0)
        if kind in ("dead", "snag"):
            h = min(h, 15.0)
        tr, cr = K.tree(kind, mb, (x, y, z - 0.25), h, rng, lod, wind=wind)
        sp.add(x, y, cr)
        PLACED.append((zone, kind, round(x, 1), round(y, 1), round(z, 1), round(h, 1)))
        stats[zone + ":" + kind] = stats.get(zone + ":" + kind, 0) + 1
        if zone == "valley":
            # colisao do tronco (arvores no vale)
            col_box("Veg", (max(1.8, tr * 2.4), max(1.8, tr * 2.4), h * 0.4), (x, y, z + h * 0.2))
        return cr

    def canopy_r(kind, h):
        return h * {"fir": 0.31, "windswept": 0.31, "spruce": 0.22, "young": 0.44, "umbrella": 0.35,
                    "dead": 0.3, "snag": 0.12}[kind]

    # ---------------- 1) bosques: centros por zona (disco de Poisson; centros descartados = clareiras)
    params = {  # dmin, keep, R, dens
        "valley": (22.0, 0.85, (7.0, 12.0), (0.7, 1.0)),
        "rim": (21.0, 0.76, (8.0, 15.0), (0.65, 1.0)),
        "terrace": (18.0, 0.85, (6.0, 10.0), (0.6, 1.0)),
        "mountain": (24.0, 0.7, (9.0, 17.0), (0.6, 1.0)),
        "plateau": (17.0, 0.7, (10.0, 16.0), (0.55, 0.95)),
        "south": (26.0, 0.7, (5.0, 8.0), (0.5, 0.8)),
    }
    vpts = [p for p in pool["valley"] if not blk.blocked(p[0], p[1], p[2])]
    fields = {}
    for zone, (dmin, keep, Rr, Dr) in params.items():
        f = Field()
        pts = vpts if zone == "valley" else pool[zone]
        weight = None
        if zone == "terrace":
            pts = [p for p in pts if not terrace_excl(p[0], p[1])]
        if zone == "south":
            pts = [p for p in pts if abs(p[0]) > 30]
        if zone == "valley":
            # vale: aglomerados junto as paredes/penhascos (moldura), miolo quase livre
            weight = lambda p: 1.0 / (6.0 + valley_edge_dist(p[0], p[1]))
        for (cx, cy, cz) in poisson_pick(pts[:5000], rng, dmin, keep, weight):
            dens = rng.uniform(*Dr)
            if zone == "valley":
                e = valley_edge_dist(cx, cy)
                if e > 34:
                    continue
                dens *= 1.0 if e < 18 else 0.7
            f.add(cx, cy, rng.uniform(*Rr), dens, zone)
        fields[zone] = f
    # ancoras de direcao de arte no vale: cantos e margem leste enquadram as vistas (validadas por site())
    for (ax, ay, R, dens) in ((82, -50, 9, 1.0), (116, -46, 11, 1.0), (120, 8, 10, 0.9), (108, 50, 9, 0.9),
                              (-104, 42, 9, 0.9), (-100, -4, 8, 0.8), (-36, -57, 6, 0.8), (44, -56, 7, 0.8),
                              (84, 22, 7, 0.8)):
        fields["valley"].add(ax, ay, R, dens, "valley")

    ALLOWED = {"valley": ("valley",), "rim": ("rim", "terrace"), "terrace": ("terrace", "rim"),
               "south": ("south",), "mountain": ("mountain", "rim"), "plateau": ("plateau", "mountain")}

    def site(x, y, czone):
        if konoha_corridor(x, y) or portal_view(x, y):
            return None
        g = ground(x, y, 20.0 if czone == "valley" else 260.0)
        if not g or g[2] not in ("Grass", "Grass_Dark") or g[1].z < 0.86:
            return None
        z = g[0].z
        zone = classify(x, y, z, g[2])
        if zone not in ALLOWED[czone]:
            return None
        if zone == "terrace" and terrace_excl(x, y):
            return None
        if zone == "south" and abs(x) < 30:
            return None
        if zone in ("valley", "terrace", "rim", "south") and blk.blocked(x, y, z):
            return None
        return zone, z

    def choose_kind(zone, dom, q, x):
        if q > 0.85 and rng.random() < 0.45:
            kind = "young"                               # borda do bosque: pinheiros jovens
        elif rng.random() < 0.6:
            kind = dom                                   # especie dominante do bosque (bosques diferentes)
        else:
            kind = pick(rng, MIX[zone])
        if kind == "umbrella" and x > -20 and rng.random() < 0.65:
            kind = "fir"   # pinheiro-guarda-chuva pende para o lado oeste (Konoha/Naruto)
        return kind

    def tree_h(zone, kind, v, x, y):
        cls = size_class(rng, v)
        if kind == "young":
            cls = "small" if rng.random() < 0.8 else "medium"
        h = rng.uniform(*SIZES[cls])
        if zone in ("mountain", "plateau"):
            h *= 1.28          # fundo: silhueta maior le melhor a 200+ studs (mesmo custo em tris)
        elif zone == "rim" and (y > 136 or x < -150 or x > 160 or y < -95):
            h *= 1.18
        if zone == "south":
            h = min(h, 11.0)
        if zone == "terrace":
            h = min(h, 13.0)
        if zone == "valley" and valley_edge_dist(x, y) > 14:
            h = min(h, 15.0)
        return h

    def try_plant(czone, x, y, v, dom, q, kmin):
        s = site(x, y, czone)
        if not s:
            return False
        zone, z = s
        kind = choose_kind(zone, dom, q, x)
        h = tree_h(zone, kind, v, x, y)
        cr = canopy_r(kind, h)
        if not sp.free(x, y, cr, kmin):
            return False
        wind = None
        if kind == "windswept":
            wind = math.atan2(-y, -x) + rng.uniform(-0.6, 0.6)   # inclina para o vazio do vale
        plant_tree(zone, kind, x, y, z, h, wind)
        return True

    # planaltos: manchas de floresta densa (groves) no nucleo dos bosques + arvores soltas na borda
    n_grove = 0
    GF = O["VEG_Mountain_Forest"]
    for (cx, cy, R, dens, tag) in fields["plateau"].c:
        g = ground(cx, cy)
        if not g or g[2] != "Grass_Dark" or portal_view(cx, cy):
            continue
        zc = g[0].z
        Rg = R * 0.62
        good = 0
        for k in range(8):
            a = k * math.tau / 8
            gg = ground(cx + math.cos(a) * Rg, cy + math.sin(a) * Rg)
            if gg and gg[2] in ("Grass_Dark", "Grass") and abs(gg[0].z - zc) < 3.0:
                good += 1
        if good < 5 or not sp.free(cx, cy, Rg, 0.75):
            continue
        K.grove(GF, (cx, cy, zc), Rg, rng, lod=2)
        sp.add(cx, cy, Rg * 0.9)
        n_grove += 1

    budget = {"valley": 50, "south": 8, "terrace": 22, "rim": 270, "mountain": 190, "plateau": 36}
    per_r = {"valley": 0.42, "south": 0.35, "terrace": 0.6, "rim": 1.0, "mountain": 0.9, "plateau": 0.3}
    order = ["valley", "south", "terrace", "rim", "mountain", "plateau"]
    count = {z: 0 for z in order}
    for zone in order:
        cl = list(fields[zone].c)
        rng.shuffle(cl)
        for (cx, cy, R, dens, tag) in cl:
            if count[zone] >= budget[zone]:
                break
            nz = noise.noise(Vector((cx * 0.03, cy * 0.03, 7.3)))
            n = int(round(R * dens * per_r[zone] * (0.75 + 0.6 * max(0.0, nz + 0.3))))
            n = max(2, min(n, 16))
            dom = pick(rng, [(k, w) for k, w in MIX[zone] if k not in ("dead", "snag")])
            got = tries = 0
            while got < n and tries < n * 10 and count[zone] < budget[zone]:
                tries += 1
                a = rng.uniform(0, math.tau)
                d = abs(rng.gauss(0.0, R * 0.5))
                if d > R * 1.2:
                    continue
                q = d / R
                v = math.exp(-1.6 * q * q) * dens
                kmin = (0.34 if q < 0.6 else 0.55) if zone != "valley" else (0.45 if q < 0.6 else 0.65)
                if try_plant(zone, cx + math.cos(a) * d, cy + math.sin(a) * d, v, dom, q, kmin):
                    got += 1
                    count[zone] += 1
    # solitarios nas clareiras (quebram o padrao dos bosques)
    lone_n = {"valley": 7, "rim": 22, "mountain": 18, "plateau": 10, "terrace": 0, "south": 2}
    for zone in order:
        pts = vpts if zone == "valley" else pool[zone]
        got = 0
        for (x, y, z) in pts:
            if got >= lone_n[zone]:
                break
            v, c = fields[zone].value(x, y)
            if v > 0.12 or rng.random() > 0.08:
                continue
            if try_plant(zone, x, y, 0.3, pick(rng, MIX[zone]), 1.0, 1.0):
                got += 1
                count[zone] += 1

    # ---------------- 2) arvores secas de destaque (silhuetas de contraste; mina = area arida)
    def feature(cx, cy, R, kind, h, zones):
        """procura um lugar valido num raio (o ponto exato costuma cair em caminho ou bosque)"""
        for i in range(60):
            a = rng.uniform(0, math.tau)
            d = R * math.sqrt(rng.random())
            x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
            if portal_view(x, y) or konoha_corridor(x, y):
                continue
            g = ground(x, y, 20.0 if zones == ("valley",) else 260.0)
            if not g or g[2] not in ("Grass", "Grass_Dark") or g[1].z < 0.86:
                continue
            zone = classify(x, y, g[0].z, g[2])
            if zone not in zones or blk.blocked(x, y, g[0].z) or not sp.free(x, y, 2.5, 0.7):
                continue
            plant_tree(zone, kind, x, y, g[0].z, h)
            return True
        return False

    n_feat = 0
    for (cx, cy, R, kind, h, zones) in ((-96, -8, 16, "dead", 9.5, ("valley",)),
                                        (122, -50, 12, "snag", 11.0, ("valley",)),
                                        (120, 48, 12, "dead", 9.0, ("valley",)),
                                        (-104, -66, 18, "snag", 13.0, ("rim",)),
                                        (-140, 30, 16, "dead", 10.0, ("rim", "mountain")),
                                        (150, 10, 16, "snag", 12.0, ("rim", "mountain"))):
        n_feat += feature(cx, cy, R, kind, h, zones)
    for (x, y) in ((-140, -40), (-150, 20), (150, -20), (160, 90), (-40, 150), (60, 146), (-170, -80), (190, 30)):
        g = ground(x, y)
        if not g or g[1].z < 0.86 or g[2] not in ("Grass", "Grass_Dark") or g[0].z < 10:
            continue
        if not sp.free(x, y, 3.0, 0.8):
            continue
        plant_tree("mountain", rng.choice(("dead", "snag")), x, y, g[0].z, rng.uniform(9, 14))

    # ---------------- 3) vegetacao baixa do vale: pe de penhasco, meio-fio, base de construcao, prados
    VU = O["VEG_Valley_Undergrowth"]
    RK = O["VEG_Rocks"]
    n_u = {"bush": 0, "fern": 0, "tuft": 0, "flower": 0, "rockplant": 0, "boulder": 0, "flowerbush": 0}
    budget_u = 380
    cap_u = {"bush": 26, "fern": 24, "tuft": 64, "flower": 22, "rockplant": 8, "boulder": 9, "flowerbush": 5}
    for (x, y, z) in pool["valley"]:
        if sum(n_u.values()) >= budget_u:
            break
        if blk.blocked(x, y, z):
            continue
        nz = noise.noise(Vector((x * 0.07, y * 0.07, 3.1)))
        edge = valley_edge_dist(x, y)
        foot = edge < 9 and near_cliff(x, y, z)
        struct = blk_wide.blocked(x, y, z)          # faixa junto a caminho/construcao
        if foot:
            if nz < -0.25 or rng.random() > 0.55:
                continue
            kind = pick(rng, [("bush", 0.3), ("fern", 0.22), ("rockplant", 0.2), ("boulder", 0.12), ("tuft", 0.16)])
        elif struct:
            if rng.random() > 0.2:
                continue
            kind = pick(rng, [("tuft", 0.48), ("flower", 0.24), ("bush", 0.14), ("fern", 0.08), ("flowerbush", 0.06)])
        else:
            if nz < 0.05 or rng.random() > 0.16:
                continue
            kind = pick(rng, [("tuft", 0.42), ("flower", 0.3), ("bush", 0.12), ("fern", 0.08), ("flowerbush", 0.08)])
        r = {"bush": 2.0, "fern": 1.8, "tuft": 0.9, "flower": 0.9, "rockplant": 1.9, "boulder": 2.0,
             "flowerbush": 1.8}[kind]
        if n_u[kind] >= cap_u[kind] or not sp.free(x, y, r, 0.9):
            continue
        zz = z - 0.2
        if kind == "bush":
            K.bush(VU, (x, y, zz), rng.uniform(1.3, 2.3), rng, lod=0)
        elif kind == "fern":
            K.fern(VU, (x, y, zz), rng.uniform(1.6, 2.4), rng)
        elif kind == "tuft":
            K.grass_tuft(VU, (x, y, z), rng.uniform(1.1, 1.7), rng)
        elif kind == "flower":
            K.flowers(VU, (x, y, z), rng.uniform(1.2, 1.6), rng)
        elif kind == "flowerbush":
            K.flower_bush(VU, (x, y, zz), rng.uniform(1.4, 2.0), rng)
        elif kind == "rockplant":
            K.rock_plant(VU, (x, y, z), rng.uniform(1.2, 1.9), rng)
        else:
            K.boulder(RK, (x, y, z), rng.uniform(1.4, 3.0), rng, rng.choice(("Cliff_Rock", "Cliff_Rock", "Stone_Light")))
        sp.add(x, y, r)
        n_u[kind] += 1

    # ---------------- 4) vegetacao baixa das bordas: orla dos bosques (transicao floresta -> rocha nua),
    # plantas de pedra nos topos nus, e tufos/flores no terraco e na queda sul (perto do jogador e do spawn)
    RU = O["VEG_Rim_Undergrowth"]
    n_r = {"bush": 0, "fern": 0, "rockplant": 0, "tuft": 0, "flower": 0}

    def low_site(x, y, strict=True):
        if konoha_corridor(x, y) or (strict and portal_view(x, y)):
            return None
        g = ground(x, y)
        if not g or g[2] not in ("Grass", "Grass_Dark") or g[1].z < 0.86:
            return None
        z = g[0].z
        zone = classify(x, y, z, g[2])
        if zone not in ("rim", "terrace", "south") or blk.blocked(x, y, z):
            return None
        return zone, z

    def put_low(kind, x, y, z):
        r = {"bush": 2.0, "fern": 1.8, "tuft": 1.0, "flower": 1.0, "rockplant": 1.9}[kind]
        if not sp.free(x, y, r, 0.85):
            return False
        if kind == "bush":
            K.bush(RU, (x, y, z - 0.2), rng.uniform(1.5, 2.6), rng, lod=1)
        elif kind == "fern":
            K.fern(RU, (x, y, z - 0.2), rng.uniform(1.7, 2.4), rng)
        elif kind == "tuft":
            K.grass_tuft(RU, (x, y, z), rng.uniform(1.2, 1.8), rng)
        elif kind == "flower":
            K.flowers(RU, (x, y, z), rng.uniform(1.2, 1.6), rng)
        else:
            K.rock_plant(RU, (x, y, z), rng.uniform(1.3, 1.9), rng, rosettes=False)
        sp.add(x, y, r)
        n_r[kind] += 1
        return True

    for zone in ("south", "terrace", "rim"):
        cl = list(fields[zone].c)
        rng.shuffle(cl)
        for (cx, cy, R, dens, tag) in cl:
            if sum(n_r.values()) >= 70:
                break
            if cy > 136 or cx < -150 or cx > 160:
                continue                      # faixas de fundo: so arvores
            want, got_c = rng.randint(1, 3), 0
            for i in range(10):
                if got_c >= want:
                    break
                a = rng.uniform(0, math.tau)
                d = R * rng.uniform(0.55, 1.2)
                x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
                s = low_site(x, y)
                if s and put_low(pick(rng, [("bush", 0.6), ("fern", 0.25), ("rockplant", 0.15)]), x, y, s[1]):
                    got_c += 1
    # topos nus: algumas plantas de pedra (a rocha nao fica "careca" nem vira floresta)
    got = 0
    for (x, y, z) in pool["rim"]:
        if got >= 10:
            break
        if y > 136 or portal_view(x, y) or fields["rim"].value(x, y)[0] > 0.1 or rng.random() > 0.1:
            continue
        s = low_site(x, y)
        if s and put_low("rockplant", x, y, s[1]):
            got += 1
    # terraco (fundo) e queda sul: tufos e flores ao alcance do olhar
    got = 0
    for (x, y, z) in pool["terrace"] + pool["south"]:
        if got >= 22:
            break
        if rng.random() > 0.12 or noise.noise(Vector((x * 0.08, y * 0.08, 5.5))) < -0.1:
            continue
        if L.UPPER_FRONT_Y < y < L.TERR_BACK_Y and min(abs(x - px) for px in L.PORTAL_X) < 12:
            continue
        s = low_site(x, y, strict=False)
        if s and put_low(pick(rng, [("tuft", 0.55), ("flower", 0.35), ("fern", 0.1)]), x, y, s[1]):
            got += 1

    # troncos caidos nas clareiras das bordas e das montanhas
    n_log = 0
    logs = pool["rim"][:] + pool["mountain"][:]
    rng.shuffle(logs)
    for (x, y, z) in logs:
        if n_log >= 6:
            break
        if z < 40 or portal_view(x, y) or fields["rim"].value(x, y)[0] > 0.3 or fields["mountain"].value(x, y)[0] > 0.3:
            continue   # so no alto (fora do alcance do jogador: o tronco nao tem colisao)
        if blk.blocked(x, y, z) or not sp.free(x, y, 4.0, 1.0):
            continue
        K.fallen_log(O["VEG_Deadwood"], (x, y, z - 0.3), rng.uniform(5, 8), rng.uniform(0.6, 0.9), rng.uniform(0, 6), rng)
        sp.add(x, y, 4.0)
        n_log += 1

    for k in O:
        O[k].finish()

    # ---------------- 5) afloramentos de cristal (acento frio) perto da mina e nas bases dos penhascos oeste/sul
    cr = MB("VEG_Crystal_Outcrops", "09_VEGETATION", rng)
    spots = [(-58, -30), (-50, -52), (-84, -22), (-100, 8), (-110, 34), (-40, -58), (86, -52), (128, 30),
             (-118, 52), (124, -40)]
    for (x, y) in spots:
        g = ground(x, y, 20.0)
        if not g or blk.blocked(x, y, g[0].z):
            continue
        crystal_cluster(cr, (x, y, g[0].z - 0.2), rng.uniform(1.1, 1.8), "Crystal_Blue" if rng.random() > 0.3
                        else "Crystal_Purple", rng, 7)
        col_box("Veg", (3.0, 3.0, 4.0), (x, y, g[0].z + 2.0))
    cr.finish()

    # ---------------- 6) cerejeiras (sakura) moderadas no lado oeste (perto do portal Naruto e das cabanas)
    sak = MB("VEG_Sakura", "09_VEGETATION", rng)
    for (x, y) in ((-120, 36), (-98, 50), (-126, 12), (-70, 44), (-112, 44)):
        g = ground(x, y, 40.0)
        if not g or blk.blocked(x, y, g[0].z):
            continue
        h = rng.uniform(10, 12.5)
        K.sakura_tree(sak, (x, y, g[0].z - 0.2), h, rng, 0)
        col_box("Veg", (1.8, 1.8, 6.0), (x, y, g[0].z + 3.0))
    sak.finish()
    print("VEG arvores=%s groves=%d secas_destaque=%d" % (count, n_grove, n_feat))
    print("VEG especies=%s" % sorted(stats.items()))
    print("VEG baixa vale=%s bordas=%s troncos=%d" % (n_u, n_r, n_log))
