# db_veg - VEGETACAO da Ilha 2 (Dragon Ball), zona "dressing" (prefixo DB_Veg_, colecao 10_VEGETATION).
# Achado da comparacao com a concept: o plato lia como um grande DISCO DE AREIA LARANJA vazio entre o promenade e a
# borda. Aqui: VINHETAS compostas (nao floresta) a cada ~30-40 studs de arco do anel do plato - canteiro de grama,
# palmeiras em grupos de 2-3 (alturas e inclinacoes variadas), moitas redondas low-poly (3 verdes + topo lima), flores
# quentes, rochas de arenito no estilo do terreno (2-4 por grupo, tamanhos mistos); nas vinhetas de BORDA ('edge') e
# de ROCHAS o dobro de palmeiras/moitas, em fileira ao longo da borda. Manchas de terra rachada fora da arena.
# Canteiros (revisao final): BOLHA MACIA (contorno do blob_poly suavizado, 14 vertices) levantada como MONTE baixo de
# 0,3-0,45 com orla chanfrada mais escura (0,15 onde uma rota do QA passa rente), cercado de 3-5 moitinhas e com tufos
# de laminas a cada ~1,8 studs de orla (nada de folha de papel dentada). Vila (HUB): arvores de sombra de copa
# redonda, floreiras Capsule com palmeira, moitas no pe dos predios, canteiros nos cantos. Alas do terraco do Capsule:
# floreiras com palmeira. COROAS: toda tampa de grama das mesas ganha 1-3 folhosas/palmeiras + moitas (malha propria
# DB_Veg_Crowns, detail far) e os rochedos do plato um tufo de moitas no topo. Pocos, dojo e heliponto: palmeiras e
# moitas fora dos caminhos. Orcamento: VEG_TRIS (tris exatos) - o enchimento para quando so sobra a reserva das coroas.
# Tudo passa por um teste de SITIO: regras da planta (arena/promenade, trilhas radiais, escadas, pontes, summon + zona
# livre de 14 x 14, prateleira da saida, ruas e faixa y 76..88 da vila, lotes, portas, marcadores), folga das rotas do
# db_qa e raios verticais contra a geometria JA MONTADA das outras zonas (o pe tem que cair no chao do terreno, a copa
# nao pode entrar em nada).
# Colisao: so troncos e rochas perto de onde se anda (coluna octogonal INSCRITA na rocha; caixa no tronco) e as
# floreiras. Sem luzes. Sem minerio/cristal, sem placas, sem personagens.
import math, random
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import db_lib as DL
from db_lib import MB, col_box, octo_col
import db_layout as L
import db_col
import db_veg_kit as VG

C = "10_VEGETATION"
G, HB, CZ = L.GROUND, L.HUB, L.CAP
TAU = math.tau
DOWN = Vector((0.0, 0.0, -1.0))
COL_BUDGET = 45
TUFT_STEP = 1.8          # tufos de laminas na orla dos canteiros: 1 a cada ~1,8 studs de contorno
FILL_MAX = 60            # canteiros do enchimento (teto; quem manda e o orcamento abaixo)
VEG_TRIS = 37000         # teto de tris da vegetacao (a zona 'dressing' divide 50k com os props, ~12,8k)
CROWN_RESERVE = 5100     # reservado para as coroas das mesas (fase 'topos', depois do enchimento)
TUFT_CAP = 4             # teto de tufos por canteiro (orcamento de tris: as moitinhas ja quebram a orla)

# ------------------------------------------------------------------ cameras de revisao (plato na altura do jogador
# nas 4 direcoes, rua da vila, ala do Capsule, vistas altas)
CAMS = {
    "CAM_DBVeg_PlayerSW": ((-57.0, -60.0, G + 5.2), (-120.0, -52.0, G + 4.0), 22),
    "CAM_DBVeg_PlayerSE": ((58.0, -52.0, G + 5.2), (112.0, -70.0, G + 4.0), 22),
    "CAM_DBVeg_PlayerE": ((80.0, -10.0, G + 5.2), (132.0, 30.0, G + 5.0), 22),
    "CAM_DBVeg_PlayerW": ((-80.0, 30.0, G + 5.2), (-150.0, 60.0, G + 5.0), 22),
    "CAM_DBVeg_PlayerS": ((0.0, -80.0, G + 5.2), (-60.0, -112.0, G + 3.0), 22),
    "CAM_DBVeg_PlayerN": ((-30.0, 66.0, G + 5.2), (-100.0, 64.0, G + 4.0), 22),
    "CAM_DBVeg_HubStreet": ((0.0, 84.0, HB + 5.2), (-40.0, 118.0, HB + 5.0), 22),
    "CAM_DBVeg_HubEast": ((20.0, 88.0, HB + 5.2), (96.0, 112.0, HB + 5.0), 22),
    "CAM_DBVeg_CapWing": ((-14.0, 136.0, CZ + 5.2), (-60.0, 150.0, CZ + 4.0), 22),
    "CAM_DBVeg_Aerial": ((-150.0, -190.0, 120.0), (-40.0, -20.0, G), 24),
    "CAM_DBVeg_MesaTops": ((-40.0, 40.0, 112.0), (-140.0, 150.0, 82.0), 24),     # coroas do cacho NO
    "CAM_DBVeg_PlateauEye": ((-40.0, -64.0, G + 5.2), (-100.0, -96.0, G + 3.0), 22),
}
EXTRA_ROUTES = {}
EXTRA_PROBES = []

# ------------------------------------------------------------------ vinhetas do anel do plato (x, y, raio, tipo)
# tipos: grove (canteiro + 2-3 palmeiras + moitas + flores), mixed (canteiro + palmeira + par de rochas), rocks (grupo
# de rochas + canteiro pequeno + moita), hedge (canteiro alongado com fileira de moitas e flores), edge (borda:
# moitas e palmeiras inclinadas para fora, sem canteiro), wall (pe do muro da vila: canteiro estreito + moitas)
GROUND_VIGNETTES = [
    # sudoeste
    (-100.0, -40.0, 9.0, "grove"), (-132.0, -52.0, 6.0, "mixed"), (-153.0, -36.0, 5.0, "rocks"),
    (-76.0, -50.0, 5.0, "hedge"), (-116.0, -94.0, 5.0, "edge"), (-62.0, -110.0, 5.0, "rocks"),
    (-40.0, -82.0, 5.0, "grove"), (-28.0, -124.0, 4.0, "edge"), (-96.0, -99.0, 3.5, "edge"),
    # sul / sudeste
    (28.0, -124.0, 4.0, "edge"), (58.0, -104.0, 5.0, "grove"), (62.0, -74.0, 4.0, "hedge"),
    (108.0, -78.0, 4.5, "edge"), (92.0, -46.0, 4.0, "rocks"), (132.0, -40.0, 5.0, "mixed"),
    (88.0, -30.0, 5.0, "grove"), (40.0, -80.0, 4.5, "mixed"),
    # leste
    (126.0, 26.0, 4.5, "rocks"), (140.0, 40.0, 5.0, "grove"), (92.0, 62.0, 5.0, "grove"), (138.0, 6.0, 3.0, "edge"),
    (50.0, 68.0, 4.5, "wall"),
    # oeste / noroeste
    (-165.0, 34.0, 4.0, "edge"), (-120.0, 26.0, 4.0, "rocks"), (-148.0, 86.0, 6.0, "grove"),
    (-96.0, 64.0, 6.0, "grove"), (-52.0, 67.0, 4.5, "wall"), (-156.0, 46.0, 3.5, "edge"),
    (-123.0, 74.0, 3.5, "mixed"), (-160.0, 6.0, 3.0, "edge"),
]
# manchas de terra rachada (fora da arena): (x, y, raio, alongamento)
DIRT_PATCHES = [(-120.0, -64.0, 3.2, 1.3), (-58.0, -72.0, 3.0, 1.4), (82.0, -50.0, 3.2, 1.3), (64.0, 52.0, 3.2, 1.5),
                (-140.0, -40.0, 3.5, 1.3)]

# vila (HUB): arvores de sombra, floreiras com palmeira, canteiros
HUB_TREES = [(-34.0, 116.0, 13.0), (40.0, 97.0, 12.0), (-114.0, 134.0, 13.5), (98.0, 110.0, 12.5),
             (-118.0, 176.0, 12.0)]
HUB_PLANTERS = [(-22.0, 95.5, 1.9), (22.0, 95.5, 1.9), (-20.0, 127.0, 1.8)]
HUB_BEDS = [(-28.0, 102.0, 4.0), (-108.0, 150.0, 5.5), (112.0, 132.0, 5.0), (-92.0, 170.0, 5.0), (100.0, 170.0, 4.5),
            (86.0, 100.0, 3.5), (-60.0, 122.0, 4.0), (30.0, 132.0, 3.5), (-128.0, 118.0, 3.0)]
# alas do terraco do Capsule (CAP): floreiras com palmeira / com flores
CAP_PLANTERS = [(-58.0, 140.0, 1.9, "palm"), (-36.0, 152.0, 1.9, "palm"), (58.0, 140.0, 1.9, "palm"),
                (36.0, 152.0, 1.9, "palm"), (-47.0, 137.0, 1.4, "flower"), (47.0, 137.0, 1.4, "flower")]
# palmeiras soltas junto dos pocos, do dojo e do heliponto (x, y, altura)
POOL_PALMS = [(-66.0, -80.0, 12.5), (-99.0, -84.0, 14.0), (-70.0, -99.0, 10.5), (96.0, -86.0, 13.0),
              (70.0, -92.0, 10.0), (100.0, -30.0, 12.0), (140.0, -18.0, 11.0), (-122.0, 72.0, 12.0),
              (-157.0, 60.0, 11.5), (-127.0, 42.0, 10.0)]


# ------------------------------------------------------------------ raios contra a geometria ja montada
_SKIP = ("COL_", "SCALE_", "DB_Sky_", "DB_Veg_", "DB_Prop_", "BLK_Sea")
GROUND_SURF = ("DB_Ter_Ground", "DB_Ter_HubTop")
LID_SURF = GROUND_SURF + ("DB_Ter_Cliffs",)          # tampas das costelas da borda (moitas/palmeiras)


def _bvh(keep, zr=None, boxes=None):
    """BVH das malhas 'keep' (so os triangulos na faixa de cota zr e, se 'boxes', com o centro dentro de alguma
    caixa (x0, y0, x1, y1)): (bvh, dono por tri, material por tri, [(nome, materiais)])"""
    bx = np.array(boxes, dtype=np.float64) if boxes else None
    verts, tris, own, mats, names = [], [], [], [], []
    base = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or not keep(o.name):
            continue
        me = o.data
        me.calc_loop_triangles()
        nv, nt = len(me.vertices), len(me.loop_triangles)
        if nv == 0 or nt == 0:
            continue
        co = np.empty(nv * 3, dtype=np.float64)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        mw = np.array(o.matrix_world)
        co = co @ mw[:3, :3].T + mw[:3, 3]
        tv = np.empty(nt * 3, dtype=np.int64)
        me.loop_triangles.foreach_get("vertices", tv)
        tv = tv.reshape(-1, 3)
        mi = np.empty(nt, dtype=np.int64)
        me.loop_triangles.foreach_get("material_index", mi)
        if zr is not None:
            z = co[:, 2][tv]
            k = (z.max(1) > zr[0]) & (z.min(1) < zr[1])
            tv, mi = tv[k], mi[k]
            if len(tv) == 0:
                continue
        if bx is not None:
            cxy = co[:, :2][tv].mean(1)
            k = np.zeros(len(tv), dtype=bool)
            for x0, y0, x1, y1 in bx:
                k |= (cxy[:, 0] > x0) & (cxy[:, 0] < x1) & (cxy[:, 1] > y0) & (cxy[:, 1] < y1)
            tv, mi = tv[k], mi[k]
            if len(tv) == 0:
                continue
        used, inv = np.unique(tv, return_inverse=True)
        verts.append(co[used])
        tris.append(inv.reshape(-1, 3) + base)
        base += len(used)
        names.append((o.name, [m.name if m else "" for m in me.materials]))
        own.append(np.full(len(tv), len(names) - 1, dtype=np.int64))
        mats.append(mi)
    if not verts:
        return None
    V = np.concatenate(verts)
    T = np.concatenate(tris)
    return (BVHTree.FromPolygons(V.tolist(), T.tolist(), all_triangles=True), np.concatenate(own),
            np.concatenate(mats), names)


class World:
    """chao real (terreno) para assentar as manchas + obstaculos ja montados pelas outras zonas"""

    def __init__(self):
        self.g = _bvh(lambda n: n.startswith(GROUND_SURF + ("DB_Cap_Terrace",)))
        self.o = _bvh(lambda n: not n.startswith(_SKIP), (G - 0.8, CZ + 24.0))
        self.blockout = self.g is None
        self.last, self.last_m = "", ""

    def _hit(self, B, origin, dist):
        if B is None:
            return None
        loc, nrm, idx, d = B[0].ray_cast(Vector(origin), DOWN, dist)
        if loc is None:
            return None
        on, ml = B[3][B[1][idx]]
        mi = B[2][idx]
        return loc, on, (ml[mi] if 0 <= mi < len(ml) else "")

    def surf(self, x, y, lv):
        """cota do chao visual em (x, y) (limitada a lv -0,2 .. +0,08: o topo das manchas fica <= piso + 0,15)"""
        h = self._hit(self.g, (x, y, lv + 1.2), 2.6)
        z = h[0].z if h else lv
        return max(lv - 0.2, min(lv + 0.08, z))

    def ground_ok(self, x, y, lv, top=9.0, surf=GROUND_SURF, paved=False):
        """o raio de cima (lv + top) cai direto no chao do nivel lv (sem nada no caminho)"""
        if self.o is None:
            return True
        h = self._hit(self.o, (x, y, lv + top), top + 1.2)
        if h is None:
            self.last = "vazio"
            return False
        loc, on, mn = h
        self.last = on.split("_")[1] + "_" + on.split("_")[2] if on.count("_") >= 2 else on
        self.last_m = mn
        if not (lv - 0.6 < loc.z < lv + 0.45):
            return False
        if not on.startswith(surf):
            return False
        return paved or not mn.startswith("Stone")

    def air_ok(self, x, y, z_top, z_low):
        """nada entre z_low e z_top na vertical (copa de palmeira/arvore)"""
        if self.o is None:
            return True
        h = self._hit(self.o, (x, y, z_top), z_top - z_low)
        return h is None


# ------------------------------------------------------------------ regras da planta + rotas do QA
RIM_CL = list(L.ISLAND_RIM) + [L.ISLAND_RIM[0]]
MARGIN = {"flat": 0.6, "low": 1.4, "tall": 2.2}


def _seg_d(px, py, a, b):
    return L.seg_dist(px, py, a[0], a[1], b[0], b[1])[0]


def _rect_d(x, y, r):
    x0, y0, x1, y1 = r
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


class Site:
    def __init__(self, world):
        import db_qa
        import db_terrain as DT
        self.W = world
        self.stairs = db_col.stair_list()
        self.notch = db_col.entry_notch()
        self.streets = list(DT.HUB_STREETS)
        self.pave_rects = list(DT.HUB_PAVE_RECTS)
        self.pave_discs = list(DT.HUB_PAVE_DISCS)
        self.lots = DT.lot_rects()
        lines = [pts for pts, z in db_qa.routes().values()] + [pts for pts, z in db_qa.open_routes().values()]
        try:
            mr, mp = db_qa.module_routes()
            lines += [pts for pts, z in mr.values()]
        except Exception as ex:              # rotas dos modulos sao extras: sem elas vale a planta
            print("VEG aviso: rotas dos modulos indisponiveis (%s)" % ex)
        self.routes = [[(p[0], p[1]) for p in pts] for pts in lines if len(pts) >= 2]
        self.marks = []
        for o in bpy.data.objects:
            if o.type == "EMPTY" and o.name.startswith(("NPC_", "PLAYER_INTERACT_", "SUMMON_", "GATE_", "WORLD_",
                                                        "ISLAND_", "PATH_ENTRY_CENTER")):
                self.marks.append((o.location.x, o.location.y))
        self._rim_grid()
        self.prom_tab = np.array([L.prom_r(a) for a in range(0, 361)])
        self.solid = []          # (x, y, r) de tudo que tem volume (tronco, rocha, moita, floreira)
        self.beds = []           # (x, y, R) dos canteiros/manchas
        self.bedcells = set()    # raster de 1 stud das manchas (nenhuma sobrepoe outra: z-fight)

    def _no(self, why):
        self.why = why
        return False

    # ---------------------------------------------------------- distancias
    def route_d(self, x, y):
        best = 1e9
        for pts in self.routes:
            for a, b in zip(pts, pts[1:]):
                if abs(x - a[0]) > best + 40 and abs(x - b[0]) > best + 40:
                    continue
                best = min(best, _seg_d(x, y, a, b))
        return best

    def walk_d(self, x, y):
        """distancia ao lugar por onde se anda de verdade (rotas, trilhas, promenade, ruas): prioridade da colisao"""
        d = self.route_d(x, y)
        r = math.hypot(x, y)
        ang = math.degrees(math.atan2(y, x))
        d = min(d, max(0.0, r - L.prom_r(ang)))
        for pts, w in L.GROUND_PATHS:
            d = min(d, max(0.0, L.polyline_dist(x, y, pts) - w / 2))
        for pts, hw in self.streets:
            d = min(d, max(0.0, L.polyline_dist(x, y, pts) - hw))
        return d

    RG = 1.0
    RX0, RY0 = -190.0, -150.0

    def _rim_grid(self):
        """dentro/fora da borda e distancia ate ela numa grade de 1 stud (vetorial): consulta rapida; perto da borda
        a conta exata decide"""
        xs = np.arange(self.RX0, 176.0, self.RG) + 0.5
        ys = np.arange(self.RY0, 232.0, self.RG) + 0.5
        X, Y = np.meshgrid(xs, ys)
        inside = np.zeros(X.shape, dtype=bool)
        d = np.full(X.shape, 1e9)
        P = RIM_CL
        for (x0, y0), (x1, y1) in zip(P, P[1:]):
            c = ((y0 > Y) != (y1 > Y)) & (X < (x1 - x0) * (Y - y0) / ((y1 - y0) or 1e-9) + x0)
            inside ^= c
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy or 1e-9
            t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0.0, 1.0)
            d = np.minimum(d, np.hypot(X - (x0 + dx * t), Y - (y0 + dy * t)))
        self.rim_in, self.rim_dg = inside, d

    def _rim_cell(self, x, y):
        i, j = int((x - self.RX0) // self.RG), int((y - self.RY0) // self.RG)
        if 0 <= j < self.rim_in.shape[0] and 0 <= i < self.rim_in.shape[1]:
            return bool(self.rim_in[j, i]), float(self.rim_dg[j, i])
        return False, 0.0

    def rim_d(self, x, y):
        inside, d = self._rim_cell(x, y)
        if d > 3.0:
            return d - 0.75                     # centro da celula: erro <= 0,71
        return L.polyline_dist(x, y, RIM_CL)

    # ---------------------------------------------------------- planta
    def plan_ok(self, x, y, rad, cls, cap=False):
        m = MARGIN[cls]
        e = rad + m
        r = math.hypot(x, y)
        ang = math.degrees(math.atan2(y, x))
        if r < min(self.prom_tab) + e or r < L.prom_r(ang) + e:     # arena + promenade
            return self._no("r < L.prom_r(ang) + e")
        inside, dg = self._rim_cell(x, y)
        if dg > 3.0 and not inside:
            return self._no("not L.point_in_poly(x, y, L.ISLAND_RIM")
        if dg <= 3.0 and not L.point_in_poly(x, y, L.ISLAND_RIM):
            return self._no("not L.point_in_poly(x, y, L.ISLAND_RIM")
        rd = self.rim_d(x, y)
        if rd < rad + (0.9 if cls != "tall" else 1.6):
            return self._no("rd < rad + (0.9 if cls != 'tall' else ")
        lv = L.zone_of(x, y)
        sx, sy = L.SUMMON_C
        if math.hypot(x - sx, y - sy) < 27.0 + e:                   # disco do summon (r 27)
            return self._no("math.hypot(x - sx, y - sy) < 27.0 + e")
        if _rect_d(x, y, (-104.0, -10.0, -74.0, 6.0)) < e:          # escada do summon + zona livre 14 x 14
            return self._no("_rect_d(x, y, (-104.0, -10.0, -74.0, 6")
        if _rect_d(x, y, L.ENTRY_PLAZA) < e + 0.6:
            return self._no("_rect_d(x, y, L.ENTRY_PLAZA) < e + 0.6")
        if L.point_in_poly(x, y, self.notch) or _rect_d(x, y, (-12.6, -140.0, 12.6, -104.0)) < e:
            return self._no("L.point_in_poly(x, y, self.notch) or _")
        for pts, w in L.GROUND_PATHS:
            if L.polyline_dist(x, y, pts) < w / 2 + e:
                return self._no("L.polyline_dist(x, y, pts) < w / 2 + e")
        for nm, base, a, w, n, rise, tread, g in self.stairs:
            dx, dy = x - base[0], y - base[1]
            u = dx * math.cos(a) + dy * math.sin(a)
            v = -dx * math.sin(a) + dy * math.cos(a)
            if -8.0 - e < u < tread * n + 4.0 + e and abs(v) < w / 2 + 1.5 + e:
                return self._no("-8.0 - e < u < tread * n + 4.0 + e and")
        if L.polyline_dist(x, y, L.EXIT_PATH) < L.EXIT_PATH_HW + e or \
                L.polyline_dist(x, y, L.HUB_EXIT_LINK) < L.HUB_EXIT_LINK_HW + e:
            return self._no("L.polyline_dist(x, y, L.EXIT_PATH) < L")
        for k, (a0, a1) in L.SAT_BRIDGES.items():
            if _seg_d(x, y, a0, a1) < L.SAT_BRIDGE_W / 2 + e:
                return self._no("_seg_d(x, y, a0, a1) < L.SAT_BRIDGE_W ")
        for tx, ty, tr, kind, walk in L.TOWER_SITES:
            if math.hypot(x - tx, y - ty) < tr + e:
                return self._no("math.hypot(x - tx, y - ty) < tr + e")
        for gx, gy, gr, kind in L.GROUND_LOTS:
            pad = 3.5 if kind == "landing_pad" else 3.0
            if math.hypot(x - gx, y - gy) < gr + pad + rad:
                return self._no("math.hypot(x - gx, y - gy) < gr + pad ")
        for px, py, pr in L.PODS:
            if math.hypot(x - px, y - py) < pr + 1.5 + rad:
                return self._no("math.hypot(x - px, y - py) < pr + 1.5 ")
        for (px, py, pr), f in ((L.POOL_SW, L.FALL_SW), (L.POOL_SE, L.FALL_SE)):
            if math.hypot(x - px, y - py) < pr + 2.2 + rad or _seg_d(x, y, (px, py), f) < 2.4 + 1.6 + rad:
                return self._no("math.hypot(x - px, y - py) < pr + 2.2 ")
        px, py, pr = L.POOL_NW
        if math.hypot(x - px, y - py) < pr + 2.5 + rad:
            return self._no("math.hypot(x - px, y - py) < pr + 2.5 ")
        for qx, qy, qr, h in L.PLATEAU_ROCKS:
            if math.hypot(x - qx, y - qy) < qr + 0.8 + rad:
                return self._no("math.hypot(x - qx, y - qy) < qr + 0.8 ")
        for qx, qy, qr, top, kind in L.MESAS:
            if math.hypot(x - qx, y - qy) < qr + 1.2 + rad:
                return self._no("math.hypot(x - qx, y - qy) < qr + 1.2 ")
        for mx, my in self.marks:
            if math.hypot(x - mx, y - my) < 5.0 + rad:
                return self._no("math.hypot(x - mx, y - my) < 5.0 + rad")
        if lv >= HB - 0.1:                                            # vila / terraco do Capsule
            if lv >= CZ - 0.1:
                if not cap:
                    return self._no("not cap")
                if not ((24.0 <= abs(x) <= 66.0) and 136.0 <= y <= 158.0):
                    return self._no("not ((24.0 <= abs(x) <= 66.0) and 136.")
                for ax, ay, ar in L.CAPSULE_ANNEX:
                    if math.hypot(x - ax, y - ay) < ar + 2.0 + rad:
                        return self._no("math.hypot(x - ax, y - ay) < ar + 2.0 ")
                if math.hypot(x - L.CAPSULE_C[0], y - L.CAPSULE_C[1]) < L.CAPSULE_R + 3.0 + rad:
                    return self._no("math.hypot(x - L.CAPSULE_C[0], y - L.C")
            else:
                if abs(x) < 100.0 and 74.0 < y < 89.0 + e:              # faixa y 76..88 (rota Capsule -> saida)
                    return self._no("abs(x) < 100.0 and 74.0 < y < 89.0 + e")
                for rr in self.lots:
                    if _rect_d(x, y, rr) < 0.6 + rad:
                        return self._no("_rect_d(x, y, rr) < 0.6 + rad")
                for rr in self.pave_rects:
                    if _rect_d(x, y, rr) < e:
                        return self._no("_rect_d(x, y, rr) < e")
                for cx, cy, cr in self.pave_discs:
                    if math.hypot(x - cx, y - cy) < cr + e:
                        return self._no("math.hypot(x - cx, y - cy) < cr + e")
                for pts, hw in self.streets:
                    if L.polyline_dist(x, y, pts) < hw + e:
                        return self._no("L.polyline_dist(x, y, pts) < hw + e")
                if abs(x) < 13.5 + rad and 114.0 < y < 134.0:            # escadaria do Capsule
                    return self._no("abs(x) < 13.5 + rad and 114.0 < y < 13")
                if _rect_d(x, y, (6.0, 106.0, 24.0, 126.0)) < rad:       # frente do portao da oficina
                    return self._no("_rect_d(x, y, (6.0, 106.0, 24.0, 126.0")
                if _rect_d(x, y, (-101.0, 98.0, -71.0, 116.0)) < rad:    # frente do mercado
                    return self._no("_rect_d(x, y, (-101.0, 98.0, -71.0, 11")
                if L.point_in_poly(x, y, L.CAP_POLY) or _rect_d(x, y, (-70.0, 131.0, 70.0, 133.0)) < rad + 1.0:
                    return self._no("L.point_in_poly(x, y, L.CAP_POLY) or _")
        elif cap:
            return self._no("f cap")
        if cls != "flat":
            clear = rad + (1.2 if cls == "low" else 2.2)
            if self.route_d(x, y) < clear:
                return self._no("self.route_d(x, y) < clear")
        return True

    # ---------------------------------------------------------- sitio completo
    def ok(self, x, y, rad, cls, top=9.0, gap=0.3, cap=False, crown=None, solid=True, skip=()):
        if not self.plan_ok(x, y, rad, cls, cap):
            return False
        if solid:
            for i, (sx, sy, sr) in enumerate(self.solid):
                if i in skip:
                    continue
                if math.hypot(x - sx, y - sy) < rad + sr + gap:
                    return self._no("math.hypot(x - sx, y - sy) < rad + sr ")
        lv = L.zone_of(x, y)
        surf = ("DB_Cap_Terrace",) if cap else LID_SURF
        k = 8 if rad > 1.5 else 6
        pts = [(x, y)] + [(x + rad * math.cos(i * TAU / k), y + rad * math.sin(i * TAU / k)) for i in range(k)]
        for px, py in pts:
            if not self.W.ground_ok(px, py, lv, top, surf, paved=cap):
                return self._no("chao:%s" % self.W.last)
        if crown:
            cx, cy, cr, z0, z1 = crown
            for i in range(7):
                a = i * TAU / 6
                px, py = (cx, cy) if i == 6 else (cx + cr * math.cos(a), cy + cr * math.sin(a))
                if not self.W.air_ok(px, py, z1, z0):
                    return self._no("not self.W.air_ok(px, py, z1, z0)")
        return True

    @staticmethod
    def ellipse_cells(x, y, r, aspect, rot, pad):
        """celulas (1 stud) cobertas pela elipse da mancha (contorno com folga do ruido + franja)"""
        ra, rb = r * aspect * 1.24 + pad, r / aspect * 1.24 + pad
        ca, sa = math.cos(rot), math.sin(rot)
        R = max(ra, rb)
        out = set()
        for i in range(int(math.floor(x - R)), int(math.ceil(x + R)) + 1):
            for j in range(int(math.floor(y - R)), int(math.ceil(y + R)) + 1):
                dx, dy = i + 0.5 - x, j + 0.5 - y
                u, v = dx * ca + dy * sa, -dx * sa + dy * ca
                if (u / ra) ** 2 + (v / rb) ** 2 <= 1.0:
                    out.add((i, j))
        return out

    def bed_ok(self, cells):
        return not (cells & self.bedcells)


# ------------------------------------------------------------------ montagem
class Stage:
    def __init__(self):
        self.W = World()
        self.S = Site(self.W)
        self.beds = MB("DB_Veg_Beds", C, random.Random(7101), detail="near", floor=-999)
        self.palms = MB("DB_Veg_Palms", C, random.Random(7102), detail="near", floor=-999)
        self.shrubs = MB("DB_Veg_Shrubs", C, random.Random(7103), detail="near", floor=-999)
        self.rocks = MB("DB_Veg_Rocks", C, random.Random(7104), detail="near", floor=-999)
        self.pots = MB("DB_Veg_Planters", C, random.Random(7105), detail="near", floor=-999)
        self.crowns = MB("DB_Veg_Crowns", C, random.Random(7106), detail="far", floor=-999)   # topo das mesas
        self.col = []            # (tipo, x, y, raio, piso, dados) candidatos a colisao
        self.kinds = {}          # vinheta -> [quantas, palmeiras, moitas]
        self._tc = {}            # cache de tris por malha
        self.fails = {}
        self.n = {}
        self.area = 0.0

    def count(self, k, v=1):
        self.n[k] = self.n.get(k, 0) + v

    def fail(self, kind, why):
        d = self.fails.setdefault(kind, {})
        d[why] = d.get(why, 0) + 1

    def surf_fn(self, lv):
        return lambda px, py: self.W.surf(px, py, lv)

    # ---------------------------------------------------------- elementos (com teste de sitio)
    def bed(self, x, y, r, rng, aspect=1.0, rot=None, m=VG.GRASS, ring_w=1.0, tries=3, flowers=None, quiet=False,
            dress=True, clumps=None):
        """canteiro em BOLHA MACIA levantado como monte baixo (0,3-0,45; 0,15 onde uma rota do QA passa rente) com
        orla chanfrada. dress: ja veste a orla (moitinhas + tufos); as vinhetas vestem depois (dress=False e
        dress_bed no fim, para as palmeiras/moitas da vinheta escolherem lugar primeiro)"""
        rot = rng.uniform(0, TAU) if rot is None else rot
        self.last_bed = None
        for k in range(tries):
            R = r * aspect * 1.24 + ring_w * 1.5
            cells = self.S.ellipse_cells(x, y, r, aspect, rot, ring_w * 1.5 + 0.4)
            self.S.why = "sobrepoe"
            if self.S.bed_ok(cells) and self._flat_ok(x, y, r, aspect, rot, ring_w):
                lv = L.zone_of(x, y)
                ext = r * max(aspect, 1.0 / aspect) * 1.21
                n = 14
                h = min(0.45, 0.28 + 0.025 * ext)
                if self.S.route_d(x, y) < ext + 1.0:
                    h = 0.15                      # a rota do QA passa por cima: fica rente (visual = piso +- 0,15)
                    self.count("canteiros_rentes")
                surf = self.surf_fn(lv)
                poly = VG.bed(self.beds, x, y, r, rng, surf, aspect, rot, n, h, m)
                self.S.beds.append((x, y, R))
                self.S.bedcells |= cells
                self.last_cells = cells
                self.last_bed = (x, y, poly, lv, ext)
                self.area += math.pi * r * r
                self.count("canteiros")
                nf = rng.choice((0, 0, 0, 0, 3)) if flowers is None else flowers
                if nf:
                    VG.blossoms(self.shrubs, x, y, self.W.surf(x, y, lv) + h * 0.72, r * 0.62, rng, nf,
                                rng.choice((VG.BLOOM, VG.BLOOM, VG.WHITE_F)))
                    self.count("flores_soltas", nf)
                if dress:
                    self.dress_bed(self.last_bed, rng, clumps)
                return r
            r *= 0.82
        if not quiet:
            self.fail("canteiro", self.S.why)
        return None

    def dress_bed(self, info, rng, clumps=None):
        """orla do canteiro: 3-5 moitinhas (meio na grama, meio na areia) + tufos de laminas a cada ~1,8 studs"""
        if not info:
            return
        x, y, poly, lv, ext = info
        k = clumps if clumps is not None else (3 if ext < 10.0 else 4)
        got = self.bed_clumps(x, y, poly, rng, k, lv)
        near = [(sx, sy, sr) for sx, sy, sr in self.S.solid if math.hypot(sx - x, sy - y) < ext + sr + 1.0]
        nt = VG.edge_tufts(self.shrubs, poly, (x, y), self.surf_fn(lv), rng, step=TUFT_STEP, avoid=near,
                           cap=TUFT_CAP)
        self.count("tufos_orla", nt)

    def bed_clumps(self, x, y, poly, rng, k, lv):
        got = []
        n = len(poly)
        if k <= 0 or n < 3:
            return got
        i0 = rng.randrange(n)
        for j in range(k):
            for t in range(4):
                f = (j + rng.uniform(-0.18, 0.18)) / k + (t + 1) // 2 * 0.09 * (1 if t % 2 else -1)
                px, py = poly[int(round(i0 + f * n)) % n]
                dx, dy = px - x, py - y
                dd = math.hypot(dx, dy) or 1.0
                s = rng.uniform(0.75, 1.3)
                qx, qy = px - dx / dd * s * 0.25, py - dy / dd * s * 0.25
                if self.S.ok(qx, qy, s * 0.9, "low", top=5.0, gap=0.1):
                    VG.clump(self.shrubs, qx, qy, lv, s, rng)
                    self.S.solid.append((qx, qy, s * 0.9))
                    got.append((qx, qy, s * 0.9))
                    self.count("moitinhas_orla")
                    self.area += math.pi * s * s
                    break
        return got

    def _flat_ok(self, x, y, r, aspect, rot, ring_w):
        """o contorno (com folga da orla e do ruido do contorno) cai todo em chao livre"""
        ca, sa = math.cos(rot), math.sin(rot)
        rr = r * 1.24 + ring_w * 1.5
        pts = [(x, y)]
        for i in range(12):
            t = i * TAU / 12
            px, py = math.cos(t) * rr * aspect, math.sin(t) * rr / aspect
            pts.append((x + px * ca - py * sa, y + px * sa + py * ca))
        for px, py in pts:
            if not self.S.plan_ok(px, py, 0.0, "flat"):
                return False
            if not self.W.ground_ok(px, py, L.zone_of(px, py), 9.0):
                self.S.why = "chao:%s" % self.W.last
                return False
        return True

    def palm(self, x, y, h, rng, lean=None, lean_dir=None, planter_z=None, prio_bonus=0.0):
        lv = L.zone_of(x, y)
        z = lv if planter_z is None else planter_z
        lean = rng.uniform(0.1, 0.26) if lean is None else lean
        a = rng.uniform(0, TAU) if lean_dir is None else lean_dir
        tx, ty = x + math.cos(a) * lean * h, y + math.sin(a) * lean * h
        if planter_z is None:
            if not self.S.ok(x, y, 1.2, "tall", top=min(h, 14.0), gap=0.8,
                             crown=(tx, ty, 4.0, z + h - 3.2, z + h + 2.0)):
                self.fail("palmeira", self.S.why)
                return False
        (cx, cy), tr = VG.palm(self.palms, x, y, z, h, rng, lean, a, fronds=8 if h >= 13.0 else 7)
        self.S.solid.append((x, y, 1.2))
        self.count("palmeiras")
        self.area += 20.0
        if planter_z is None:
            self.col.append(("palm", x, y, tr, lv, (h, lean, a)))
        return True

    def shrub(self, x, y, s, rng, flower=False, group=True, cls="low"):
        if not self.S.ok(x, y, s * 1.1, cls, top=6.0, gap=0.2):
            self.fail("moita", self.S.why)
            return False
        lv = L.zone_of(x, y)
        if flower:
            VG.flower_bush(self.shrubs, x, y, lv, s, rng, rng.choice((VG.BLOOM, VG.BLOOM, VG.WHITE_F)))
            self.count("flores")
        elif group:
            VG.shrub_group(self.shrubs, x, y, lv, s, rng)
            self.count("moitas")
        else:
            VG.shrub(self.shrubs, x, y, lv, s, rng)
            self.count("moitas")
        self.S.solid.append((x, y, s * 1.1))
        self.area += math.pi * (s * 1.2) ** 2
        return True

    def tuft(self, x, y, s, rng, m=VG.PALM):
        if not self.S.ok(x, y, 0.35, "flat", top=5.0, solid=False):
            return False
        VG.tuft(self.shrubs, x, y, L.zone_of(x, y) + 0.02, s, rng, m)
        self.count("tufos")
        return True

    def rock(self, x, y, r, h, rng, lid=False, m=VG.ROCK, collide=True, skip=()):
        cls = "tall" if h > 2.2 else "low"
        if not self.S.ok(x, y, r * 1.3, cls, top=max(6.0, h + 2.0), gap=0.25, skip=skip):
            self.fail("rocha", self.S.why)
            return False
        lv = L.zone_of(x, y)
        ri = VG.rock(self.rocks, x, y, lv, r, h, rng, m=m, lid=lid)
        self.S.solid.append((x, y, r * 1.3))
        self.count("rochas")
        self.area += math.pi * r * r
        if collide and h >= 2.4:
            self.col.append(("rock", x, y, ri, lv, h - min(0.5, h * 0.18)))
        return True

    # ---------------------------------------------------------- vinhetas
    def around(self, x, y, R, rng, a0=None, n=1, spread=None):
        a0 = rng.uniform(0, TAU) if a0 is None else a0
        spread = TAU / max(1, n) if spread is None else spread
        return [(x + math.cos(a0 + i * spread + rng.uniform(-0.3, 0.3)) * R * rng.uniform(0.85, 1.1),
                 y + math.sin(a0 + i * spread + rng.uniform(-0.3, 0.3)) * R * rng.uniform(0.85, 1.1),
                 a0 + i * spread) for i in range(n)]

    def rim_frame(self, x, y):
        """(tangente, normal PARA DENTRO) da borda da ilha no ponto mais proximo de (x, y)"""
        best, seg = 1e9, None
        for a, b in zip(RIM_CL, RIM_CL[1:]):
            d, t = L.seg_dist(x, y, a[0], a[1], b[0], b[1])
            if d < best:
                best, seg = d, (a, b, t)
        (ax, ay), (bx, by), t = seg
        ln = math.hypot(bx - ax, by - ay) or 1.0
        tx, ty = (bx - ax) / ln, (by - ay) / ln
        nx, ny = x - (ax + (bx - ax) * t), y - (ay + (by - ay) * t)
        nn = math.hypot(nx, ny)
        if nn < 1e-6:
            nx, ny, nn = -x, -y, math.hypot(x, y) or 1.0
        return tx, ty, nx / nn, ny / nn

    def palms_in(self, x, y, r, rng, n, hs=(15.0, 12.0, 9.5)):
        """grupo de n palmeiras dentro do raio r: alturas bem diferentes, inclinadas para fora do grupo"""
        a0 = rng.uniform(0, TAU)
        got = 0
        for i in range(n):
            h = hs[i % len(hs)] * rng.uniform(0.92, 1.08)
            for t in range(7):
                a = a0 + i * TAU / n + rng.uniform(-0.5, 0.5) + t * 0.9
                d = max(2.0, r * rng.uniform(0.2, 0.6)) if n > 1 else r * rng.uniform(0.0, 0.3)
                px, py = x + math.cos(a) * d, y + math.sin(a) * d
                if self.palm(px, py, h, rng, rng.uniform(0.12, 0.28), a + rng.uniform(-0.5, 0.5)):
                    got += 1
                    break
        return got

    def rock_cluster(self, x, y, s, rng, big=True):
        """2-4 rochas de tamanhos misturados: uma grande (colisao), uma media escura/clara, 1-2 seixos + tufos"""
        a0 = rng.uniform(0, TAU)
        placed = []
        own = set()
        if big:
            r0, h0 = s * rng.uniform(0.95, 1.15), s * rng.uniform(1.5, 2.1)
            for t in range(4):
                px, py = x + math.cos(a0 + t * 1.6) * s * 0.2 * t, y + math.sin(a0 + t * 1.6) * s * 0.2 * t
                if self.rock(px, py, r0, h0, rng, lid=rng.random() < 0.3):
                    placed.append((px, py, r0))
                    own.add(len(self.S.solid) - 1)
                    break
        bx, by, br = placed[0] if placed else (x, y, s * 0.5)
        for j, (f, hf, m) in enumerate(((0.62, 0.62, VG.DARK if rng.random() < 0.5 else VG.ROCK), (0.42, 0.45, VG.ROCK))):
            if j == 1 and rng.random() < 0.35:
                continue
            rr, hh = s * f * rng.uniform(0.9, 1.1), s * hf * rng.uniform(0.85, 1.2) + 0.4
            for t in range(6):
                a = a0 + math.pi * (0.55 + j * 0.8) + rng.uniform(-0.5, 0.5) + t * 0.8
                d = br + rr * 0.95 + 0.1
                px, py = bx + math.cos(a) * d, by + math.sin(a) * d
                if self.rock(px, py, rr, hh, rng, m=m, collide=False, skip=own):
                    placed.append((px, py, rr))
                    own.add(len(self.S.solid) - 1)
                    break
        lv = L.zone_of(x, y)
        for k in range(rng.randint(1, 2)):                        # seixos
            a = rng.uniform(0, TAU)
            d = br + rng.uniform(1.0, 2.2)
            px, py = bx + math.cos(a) * d, by + math.sin(a) * d
            ps = rng.uniform(0.45, 0.75)
            if self.S.ok(px, py, ps, "low", top=4.0, gap=0.1):
                VG.pebble(self.rocks, px, py, lv, ps, rng, VG.ROCK if rng.random() < 0.6 else VG.DARK)
                self.S.solid.append((px, py, ps))
        for (px, py, pr) in placed:                                  # tufos no pe das rochas
            for k in range(1):
                a = rng.uniform(0, TAU)
                self.tuft(px + math.cos(a) * (pr + 0.35), py + math.sin(a) * (pr + 0.35), rng.uniform(0.9, 1.5), rng)
        return placed

    def shrubs_ring(self, x, y, R, rng, n, smin=1.2, smax=2.1, flowers=1, a0=None, group=True):
        got = 0
        pts = self.around(x, y, R, rng, a0, n)
        fl = set(rng.sample(range(n), min(flowers, n))) if n else set()
        for i, (px, py, a) in enumerate(pts):
            s = rng.uniform(smin, smax)
            for t in range(3):
                qx, qy = px + math.cos(a + t * 0.5) * t * 0.9, py + math.sin(a + t * 0.5) * t * 0.9
                if self.shrub(qx, qy, s * (1.0 if i not in fl else 0.85), rng, flower=i in fl, group=group):
                    got += 1
                    break
        return got

    def tufts_ring(self, x, y, R, rng, n, s=(0.9, 1.6)):
        for px, py, a in self.around(x, y, R, rng, None, n):
            self.tuft(px, py, rng.uniform(*s), rng, VG.PALM if rng.random() < 0.7 else VG.GRASS_B)

    def vignette(self, x, y, r, kind, rng):
        """a vinheta monta o canteiro sem vestir (dress=False), poe as palmeiras/moitas/rochas dela e so no fim veste
        a orla (moitinhas + tufos), para nao roubar o lugar das pecas grandes"""
        bed = None
        n0 = (self.n.get("palmeiras", 0), self.n.get("moitas", 0) + self.n.get("flores", 0))
        if kind == "grove":
            asp = rng.uniform(1.0, 1.35)
            br = self.bed(x, y, r * 1.55, rng, asp, dress=False)
            bed = self.last_bed
            rr = br or r * 0.7
            self.palms_in(x, y, rr, rng, rng.choice((2, 3, 3)))
            self.shrubs_ring(x, y, rr * 0.95, rng, rng.randint(3, 4), flowers=1, group=False)
        elif kind == "mixed":
            br = self.bed(x, y, r * 1.45, rng, rng.uniform(1.0, 1.3), dress=False)
            bed = self.last_bed
            rr = br or r * 0.7
            a = rng.uniform(0, TAU)
            self.rock_cluster(x + math.cos(a) * rr * 0.55, y + math.sin(a) * rr * 0.55, rng.uniform(1.5, 2.1), rng)
            self.palms_in(x - math.cos(a) * rr * 0.3, y - math.sin(a) * rr * 0.3, rr * 0.6, rng, rng.choice((1, 2)),
                          hs=(13.5, 10.0))
            self.shrubs_ring(x, y, rr * 0.9, rng, rng.randint(2, 4), flowers=1, a0=a + 1.4)
        elif kind == "rocks":
            # borda: o DOBRO de moitas (2 -> 4) e de palmeiras (0,6 -> 1,2 em media) em volta das rochas
            a = rng.uniform(0, TAU)
            self.bed(x + math.cos(a) * r * 0.4, y + math.sin(a) * r * 0.4, r * 1.1, rng, 1.2, ring_w=0.8, flowers=0,
                     dress=False)
            bed = self.last_bed
            self.rock_cluster(x - math.cos(a) * r * 0.25, y - math.sin(a) * r * 0.25, rng.uniform(1.7, 2.4), rng)
            # palmeiras e moitas EM VOLTA do grupo de rochas (nao no meio dele): antes as palmeiras caiam no centro
            cx_, cy_ = x - math.cos(a) * r * 0.25, y - math.sin(a) * r * 0.25
            npm = 1 if rng.random() < 0.8 else 2
            b0 = a + rng.uniform(-0.6, 0.6)
            for i in range(npm):
                h = (12.0, 9.5)[i] * rng.uniform(0.92, 1.08)
                for t in range(8):
                    b = b0 + i * 2.4 + (t % 4) * 0.8 * (1 if t % 2 else -1)
                    d = r * 0.9 + 2.0 + (t // 4) * 1.6
                    if self.palm(cx_ + math.cos(b) * d, cy_ + math.sin(b) * d, h, rng, rng.uniform(0.12, 0.26),
                                 b + rng.uniform(-0.4, 0.4)):
                        break
            self.shrubs_ring(cx_, cy_, r * 0.9 + 1.6, rng, 4, 1.0, 1.7, flowers=1, a0=b0 + 0.8, group=False)
        elif kind == "hedge":
            rot = rng.uniform(0, TAU)
            br = self.bed(x, y, r * 1.1, rng, 1.8, rot, dress=False)
            bed = self.last_bed
            n = rng.randint(4, 5)
            for i in range(n):
                t = (i / (n - 1) - 0.5) * 2.0
                px = x + math.cos(rot) * t * r * 1.05 + rng.uniform(-0.4, 0.4)
                py = y + math.sin(rot) * t * r * 1.05 + rng.uniform(-0.4, 0.4)
                self.shrub(px, py, rng.uniform(1.1, 1.6), rng, flower=(i % 2 == 1), group=False)
            self.palms_in(x + math.cos(rot) * r * 1.3, y + math.sin(rot) * r * 1.3, 1.2, rng, 1, hs=(11.5,))
        elif kind == "edge":
            # borda da ilha: o DOBRO de palmeiras (1-2 -> 2-4) e de moitas (2-4 -> 5-7), em FILEIRA ao longo da borda
            # (anel em volta do centro batia na borda) e palmeiras inclinadas para fora
            tx, ty, nx, ny = self.rim_frame(x, y)
            self.bed(x, y, r * 1.1, rng, 1.4, math.atan2(ty, tx), flowers=0, quiet=True, dress=False)
            bed = self.last_bed
            out = math.atan2(-ny, -nx)
            hs = (12.5, 9.5, 11.0, 8.5)
            npm = rng.choice((2, 3, 4))
            span = r * 0.9 + npm * 1.4
            for i in range(npm):
                u = (i / (npm - 1) - 0.5) * 2.0 * span
                h = hs[i % 4] * rng.uniform(0.92, 1.08)
                for t in range(6):
                    uu = u + rng.uniform(-1.0, 1.0) + (t % 3 - 1) * 1.7
                    vv = rng.uniform(-0.5, 1.2) + (t // 3) * 2.0
                    if self.palm(x + tx * uu + nx * vv, y + ty * uu + ny * vv, h, rng, rng.uniform(0.14, 0.3),
                                 out + rng.uniform(-0.5, 0.5)):
                        break
            nsh = rng.randint(5, 7)
            span = r * 1.2 + nsh * 1.25
            fl = rng.randrange(nsh) if rng.random() < 0.5 else -1
            for i in range(nsh):
                u = (i / (nsh - 1) - 0.5) * 2.0 * span
                s_ = rng.uniform(0.95, 1.6)
                side = 1.0 if i % 2 else -0.5
                for t in range(6):
                    uu = u + rng.uniform(-0.7, 0.7) + (t % 3 - 1) * 1.3
                    vv = side * rng.uniform(0.8, 2.0) + t * 0.7
                    if self.shrub(x + tx * uu + nx * vv, y + ty * uu + ny * vv, s_ * (0.85 if i == fl else 1.0), rng,
                                  flower=i == fl, group=False):
                        break
        elif kind == "wall":
            self.bed(x, y, r * 0.7, rng, 1.7, 0.0, ring_w=0.8, flowers=0, dress=False)
            bed = self.last_bed
            self.shrubs_ring(x, y, r * 0.8, rng, 3, 1.1, 1.7, flowers=1)
            self.palms_in(x, y, r * 0.5, rng, 1, hs=(13.0,))
        k = self.kinds.setdefault(kind, [0, 0, 0])
        k[0] += 1
        k[1] += self.n.get("palmeiras", 0) - n0[0]
        k[2] += self.n.get("moitas", 0) + self.n.get("flores", 0) - n0[1]
        if bed:          # a vinheta ja cerca o canteiro com as moitas dela: a orla ganha mais 1-2 moitinhas
            self.dress_bed(bed, rng, 2 if kind in ("rocks", "wall") else 1)
        else:
            self.tufts_ring(x, y, r * 1.1, rng, 2)

    # ---------------------------------------------------------- blocos da ilha
    def ground_ring(self):
        for i, (x, y, r, asp) in enumerate(DIRT_PATCHES):
            rng = random.Random(8300 + i * 13)
            rot = rng.uniform(0, TAU)
            for t in range(3):
                R = r * asp * 1.25
                cells = self.S.ellipse_cells(x, y, r, asp, rot, 0.6)
                if self.S.bed_ok(cells) and self._flat_ok(x, y, r, asp, rot, 0.0):
                    VG.cracked_patch(self.beds, x, y, r, rng, self.surf_fn(L.zone_of(x, y)), asp)
                    self.S.beds.append((x, y, R))
                    self.S.bedcells |= cells
                    self.count("terra_rachada")
                    for k in range(rng.randint(1, 2)):
                        a = rng.uniform(0, TAU)
                        px, py = x + math.cos(a) * r * 1.1, y + math.sin(a) * r * 1.1
                        if self.S.ok(px, py, 0.6, "low", top=4.0, gap=0.1):
                            VG.pebble(self.rocks, px, py, L.zone_of(px, py), rng.uniform(0.4, 0.65), rng, VG.DARK)
                            self.S.solid.append((px, py, 0.6))
                    self.tufts_ring(x, y, r * 1.2, rng, 1, (0.8, 1.2))
                    break
                r *= 0.8
            else:
                self.fail("terra", self.S.why)
        for i, (x, y, r, kind) in enumerate(GROUND_VIGNETTES):
            self.vignette(x, y, r, kind, random.Random(8100 + i * 17))

    # ---------------------------------------------------------- enchimento guloso (verde-e-laranja misturado)
    GRID = 2.0
    X0, Y0 = -181.0, -141.0

    def free_mask(self):
        """chao livre do plato/vila numa grade de 2 studs (planta + raio no chao do terreno); a grama que o terreno
        ja desenha conta como verde (nao e preenchida de novo)"""
        xs = np.arange(self.X0, 166.0, self.GRID)
        ys = np.arange(self.Y0, 222.0, self.GRID)
        free = np.zeros((len(ys), len(xs)), dtype=bool)
        green = np.zeros_like(free)
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                inside, dg = self.S._rim_cell(x, y)
                if not inside or dg < 0.9:
                    continue
                lv = L.zone_of(x, y)
                if lv >= CZ - 0.1 or not self.W.ground_ok(x, y, lv, 9.0):
                    continue
                if not self.S.plan_ok(x, y, 0.0, "flat"):
                    continue
                if self.W.last_m.startswith("Grass"):
                    green[j, i] = True
                else:
                    free[j, i] = True
        return xs, ys, free, green

    def occupied(self, shape, pad):
        """celulas ja cobertas (manchas + volumes) dilatadas de 'pad' studs"""
        occ = np.zeros(shape, dtype=bool)
        g = self.GRID
        for i, j in self.S.bedcells:
            jj, ii = int((j + 0.5 - self.Y0) // g), int((i + 0.5 - self.X0) // g)
            if 0 <= jj < shape[0] and 0 <= ii < shape[1]:
                occ[jj, ii] = True
        for sx, sy, sr in self.S.solid:
            rr = int(math.ceil(sr / g))
            cj, ci = int((sy - self.Y0) // g), int((sx - self.X0) // g)
            occ[max(0, cj - rr):cj + rr + 1, max(0, ci - rr):ci + rr + 1] = True
        return _dilate(occ, int(round(pad / g)))

    def fill_greedy(self, gap=2.4, min_clear=5.4):
        """manchas de grama no MAIOR vazio que sobrou, uma de cada vez (raio do vazio -> tamanho da mancha), sempre
        com uma faixa de areia de 'gap' em volta: o plato fica verde-e-laranja misturado como na concept, nao um
        tapete. 1 em 3 ganha moita, 1 em 8 uma palmeira"""
        import time
        rng = random.Random(9300)
        t0 = time.time()
        xs, ys, free, green = self.free_mask()
        t1 = time.time()
        self.mask = (xs, ys, free | green, green)
        avail = free & ~self.occupied(free.shape, gap)
        print("VEG enchimento: mascara %.1fs livre %d disponivel %d" % (t1 - t0, free.sum(), avail.sum()))
        g = self.GRID
        n = 0
        for it in range(260):
            D = _clearance(avail)
            k = int(np.argmax(D))
            j, i = divmod(k, D.shape[1])
            clear = D[j, i] * g
            if clear < min_clear or n >= FILL_MAX or self.tris() > VEG_TRIS - CROWN_RESERVE:
                print("VEG enchimento parou: it %d canteiros %d folga %.1f disponivel %d tris %d t %.1fs" % (
                    it, n, clear, avail.sum(), self.tris(), time.time() - t1))
                break
            x, y = float(xs[i]) + rng.uniform(-0.6, 0.6), float(ys[j]) + rng.uniform(-0.6, 0.6)
            lv = L.zone_of(x, y)
            asp = rng.uniform(1.0, 1.35)
            r = max(2.6, min(10.0, (clear - 1.4) / (1.24 * asp)))
            rot = math.atan2(y, x) + math.pi / 2 + rng.uniform(-0.5, 0.5) if lv < HB else rng.uniform(0, TAU)
            br = self.bed(x, y, r, rng, asp, rot, tries=3, quiet=True, flowers=0, dress=False)
            if not br:
                self.fail("enchimento", self.S.why.split(":")[0][:22])
            if br:
                n += 1
                info = self.last_bed
                u = rng.random()
                a = rng.uniform(0, TAU)
                if u < 0.45 and br > 5.0:              # canteiro grande: uma moita de miolo (volume no meio)
                    self.shrub(x + math.cos(a) * br * 0.3, y + math.sin(a) * br * 0.3, rng.uniform(1.3, 1.8), rng,
                               group=True, flower=rng.random() < 0.2)
                elif u > 0.86 and br > 3.5:
                    self.palm(x - math.cos(a) * br * 0.25, y - math.sin(a) * br * 0.25, rng.uniform(10.0, 17.0), rng)
                self.dress_bed(info, rng)
                new = np.zeros(avail.shape, dtype=bool)
                for ci, cj in self.last_cells:
                    jj, ii = int((cj + 0.5 - self.Y0) // g), int((ci + 0.5 - self.X0) // g)
                    if 0 <= jj < new.shape[0] and 0 <= ii < new.shape[1]:
                        new[jj, ii] = True
                avail &= ~_dilate(new, int(round(gap / g)))
            else:
                yy, xx = np.ogrid[-j:D.shape[0] - j, -i:D.shape[1] - i]
                avail &= ~((yy * yy + xx * xx) <= 4)
        self.count("enchimento", n)

    def feet(self):
        """tufos e moitinhas no pe das rochas do plato, dos pods e do muro da vila (lado do chao)"""
        rng = random.Random(8500)
        for qx, qy, qr, h in L.PLATEAU_ROCKS:
            for k in range(2):
                a = rng.uniform(0, TAU)
                d = qr * 0.95 + rng.uniform(1.4, 2.2)
                self.tuft(qx + math.cos(a) * d, qy + math.sin(a) * d, rng.uniform(1.0, 1.6), rng)
            a = rng.uniform(0, TAU)
            d = qr + 2.6
            self.shrub(qx + math.cos(a) * d, qy + math.sin(a) * d, rng.uniform(1.0, 1.5), rng, group=False)
        for px, py, pr in L.PODS:
            for k in range(2):
                a = rng.uniform(0, TAU)
                d = pr + rng.uniform(1.7, 2.4)
                self.tuft(px + math.cos(a) * d, py + math.sin(a) * d, rng.uniform(0.9, 1.4), rng)
        try:
            import db_terrain as DT
            runs = DT.wall_runs()
        except Exception as ex:
            print("VEG aviso: sem os muros da vila (%s)" % ex)
            runs = []
        for run in runs:
            acc = 0.0
            for a_, b_ in zip(run, run[1:]):
                d = b_ - a_
                ln = d.length
                if ln < 1e-3:
                    continue
                u = d / ln
                nout = Vector((u.y, -u.x, 0.0))
                acc += ln
                if acc < 7.0:
                    continue
                acc = 0.0
                if rng.random() < 0.6:
                    continue
                p = a_ + nout * rng.uniform(1.6, 2.4)
                if L.zone_of(p.x, p.y) > G + 0.1:
                    continue
                self.tuft(p.x, p.y, rng.uniform(1.0, 1.6), rng)

    def pools_dojo_pad(self):
        for i, (x, y, h) in enumerate(POOL_PALMS):
            rng = random.Random(8600 + i * 7)
            if self.palm(x, y, h, rng):
                self.shrub(x + rng.uniform(-3, 3), y + rng.uniform(-3, 3), rng.uniform(1.0, 1.6), rng,
                           flower=rng.random() < 0.4)

    def hub(self):
        for i, (x, y, h) in enumerate(HUB_TREES):
            rng = random.Random(8700 + i * 11)
            lv = L.zone_of(x, y)
            R = h * 0.33 * 1.3
            if not self.S.ok(x, y, 1.4, "tall", top=6.0, gap=1.0,
                             crown=(x, y, R * 0.8, lv + 6.0, lv + h + 2.0)):
                print("VEG arvore da vila %d fora (sitio)" % i)
                continue
            self.bed(x, y, 3.2, rng, 1.0, ring_w=0.7, dress=False)
            info = self.last_bed
            trb, cr, (p0, p1) = VG.shade_tree(self.palms, x, y, lv, h, rng)   # arvore inteira em DB_Veg_Palms
            self.S.solid.append((x, y, 1.4))
            self.count("arvores")
            self.area += math.pi * cr * cr * 0.6
            self.col.append(("tree", x, y, trb, lv, (p0, p1)))
            self.shrubs_ring(x, y, 3.4, rng, 2, 1.0, 1.4, flowers=1)
            self.dress_bed(info, rng, 2)
        for i, (x, y, r) in enumerate(HUB_PLANTERS):
            rng = random.Random(8800 + i * 5)
            self.planter(x, y, r, rng, "palm")
        for i, (x, y, r) in enumerate(HUB_BEDS):
            rng = random.Random(8900 + i * 3)
            br = self.bed(x, y, r, rng, rng.uniform(1.0, 1.4), dress=False)
            if br:
                info = self.last_bed
                self.shrubs_ring(x, y, br * 0.8, rng, rng.randint(2, 3), 1.0, 1.7, flowers=1)
                if br > 3.5 and rng.random() < 0.7:
                    self.palms_in(x, y, br * 0.4, rng, 1, hs=(rng.uniform(10.0, 13.0),))
                self.dress_bed(info, rng, 2)
        # moitas no pe dos predios da vila (fora das frentes/portas, fora das ruas)
        rng = random.Random(8950)
        for x0, y0, x1, y1 in self.S.lots:
            per = []
            for t in np.linspace(0.1, 0.9, 5):
                per += [(x0 + (x1 - x0) * t, y0 - 1.9), (x0 + (x1 - x0) * t, y1 + 1.9),
                        (x0 - 1.9, y0 + (y1 - y0) * t), (x1 + 1.9, y0 + (y1 - y0) * t)]
            rng.shuffle(per)
            got = 0
            for px, py in per:
                if got >= 3:
                    break
                if self.shrub(px, py, rng.uniform(1.0, 1.5), rng, flower=rng.random() < 0.3, group=False):
                    got += 1

    def planter(self, x, y, r, rng, kind, cap=False):
        lv = L.zone_of(x, y)
        h = rng.uniform(11.5, 13.5)
        crown = (x, y, 3.8, lv + 1.2 + h - 3.2, lv + 1.2 + h + 2.0) if kind == "palm" else None
        if not self.S.ok(x, y, r * 1.15, "tall" if kind == "palm" else "low", top=6.0, gap=0.8, cap=cap, crown=crown):
            print("VEG floreira (%.0f, %.0f) fora (sitio)" % (x, y))
            return False
        soil = VG.planter(self.pots, x, y, lv, r, rng)
        if kind == "palm":
            VG.palm(self.palms, x, y, soil, h, rng, rng.uniform(0.08, 0.16))
            a = rng.uniform(0, TAU)
            VG.shrub(self.shrubs, x + math.cos(a) * r * 0.45, y + math.sin(a) * r * 0.45, soil, r * 0.5, rng,
                     seg=5, lumps=1)
            self.count("palmeiras")
        else:
            VG.flower_bush(self.shrubs, x, y, soil, r * 0.7, rng, VG.BLOOM, n=5)
            self.count("flores")
        self.S.solid.append((x, y, r * 1.15))
        self.count("floreiras")
        self.col.append(("planter", x, y, r, lv, 1.2 + (h if kind == "palm" else 1.0)))
        return True

    def cap_wings(self):
        for i, (x, y, r, kind) in enumerate(CAP_PLANTERS):
            self.planter(x, y, r, random.Random(9000 + i * 7), kind, cap=True)

    def tops(self):
        """COROAS VERDES: em TODA tampa de grama das mesas (inalcancavel, sem colisao) 1-3 folhosas de copa redonda ou
        palmeiras + moitas, como na concept (toda rocha alta tem arvores no topo); nos rochedos do plato (topo de
        pedra, sem grama) um tufo de 1-2 moitas. Malha propria DB_Veg_Crowns em detail 'far' (so vista de longe).
        Cada pe e conferido por raio vertical: cai na PROPRIA tampa (grama, virada para cima) e a copa nao entra em
        nada (degrau mais alto da mesa, torre, passarela)."""
        rng = random.Random(9100)
        lids = []
        for o in sorted(bpy.data.objects, key=lambda o: o.name):
            if o.type != "MESH" or not o.name.startswith("DB_Ter_Mesas"):
                continue
            me = o.data
            gi = {i for i, m in enumerate(me.materials) if m and m.name.startswith("Grass")}
            mw = o.matrix_world
            r3 = mw.to_3x3()
            for p in me.polygons:
                if p.material_index in gi and (r3 @ p.normal).normalized().z > 0.85 and p.area > 8.0:
                    lids.append((o.name, p.area, mw @ p.center, [(mw @ me.vertices[v].co).xy for v in p.vertices]))
        rocks = []
        for o in bpy.data.objects:
            if o.type == "MESH" and o.name.startswith("DB_Ter_PlateauRocks"):
                rocks.append(o.name)
        if not lids and not rocks:
            self.count("coroas", 0)
            return
        boxes = [(min(v.x for v in pl) - 12.0, min(v.y for v in pl) - 12.0, max(v.x for v in pl) + 12.0,
                  max(v.y for v in pl) + 12.0) for _, _, _, pl in lids]
        boxes += [(qx - qr - 6.0, qy - qr - 6.0, qx + qr + 6.0, qy + qr + 6.0) for qx, qy, qr, h in L.PLATEAU_ROCKS]
        z0 = min([c.z for _, _, c, _ in lids] + [G]) - 2.0
        B = _bvh(lambda n: not n.startswith(_SKIP), (z0, 140.0), boxes)

        def hit(px, py, ztop, dist):
            if B is None:
                return None
            loc, nrm, idx, d = B[0].ray_cast(Vector((px, py, ztop)), DOWN, dist)
            if loc is None:
                return None
            on, ml = B[3][B[1][idx]]
            mi = B[2][idx]
            return loc, nrm, on, (ml[mi] if 0 <= mi < len(ml) else "")

        def on_lid(px, py, name, zc, mat="Grass"):
            h = hit(px, py, zc + 30.0, 32.0)
            if h is None:
                return None
            loc, nrm, on, mn = h
            if on != name or not mn.startswith(mat) or nrm.z < 0.8 or abs(loc.z - zc) > 1.2:
                return None
            return loc.z

        def air(px, py, rad, zt, zb):
            for i in range(7):
                a = i * TAU / 6
                qx, qy = (px, py) if i == 6 else (px + rad * math.cos(a), py + rad * math.sin(a))
                if hit(qx, qy, zt, zt - zb) is not None:
                    return False
            return True

        def inset(px, py, pl):
            if not L.point_in_poly(px, py, pl):
                return -1.0
            return L.polyline_dist(px, py, list(pl) + [pl[0]])

        mb = self.crowns
        nt_all = nb_all = 0
        lid_n = {"com_arvore": 0, "so_moitas": 0, "vazias": 0}
        for name, area, c, pl in lids:
            pl = [(v.x, v.y) for v in pl]
            rr = math.sqrt(area / math.pi)
            if c.z < G - 1.0:          # prateleira do pe da mesa, ABAIXO do plato (quase escondida): 1 arvore
                nt, nb = 1, (1 if rr > 6.0 else 0)
            else:
                nt = 1 if rr < 6.0 else (2 if rr < 11.0 else 3)
                nb = 1 if rr < 12.0 else 2
            placed = []
            a0 = rng.uniform(0, TAU)
            for i in range(nt):
                palm = rng.random() < (0.45 if rr < 6.0 else 0.3)     # a concept coroa as rochas com copas redondas
                # copas GRANDES (mais verde por tri: a mesa tem 60-100 de altura, arvore miuda some)
                h = rng.uniform(9.5, 13.0) if palm else rng.uniform(10.0, 13.5) * min(1.0, 0.75 + rr * 0.035)
                cr = h * 0.46 if palm else h * 0.34 * 1.35
                for t in range(8):
                    if i == 0 and t == 0:
                        d, a = rr * rng.uniform(0.0, 0.2), rng.uniform(0, TAU)
                    else:
                        a = a0 + i * TAU / nt + t * 0.85
                        d = rr * min(0.88, rng.uniform(0.3, 0.6) + t * 0.05)
                    px, py = c.x + math.cos(a) * d, c.y + math.sin(a) * d
                    if inset(px, py, pl) < 1.3:
                        continue
                    if any(math.hypot(px - qx, py - qy) < 0.62 * (cr + qr) for qx, qy, qr in placed):
                        continue
                    z = on_lid(px, py, name, c.z)
                    if z is None or not air(px, py, cr * 0.8, z + h + cr * 0.6, z + 2.2):
                        continue
                    if palm:
                        VG.crown_palm(mb, px, py, z, h, rng, rng.uniform(0.08, 0.2), a + rng.uniform(-0.6, 0.6))
                    else:
                        VG.crown_tree(mb, px, py, z, h, rng, sides=1 if (h < 10.0 or rr < 9.0) else None)
                    placed.append((px, py, cr))
                    nt_all += 1
                    break
            if not placed:              # tampa apertada (degrau mais alto do lado): palmeirinha de 6,5-8
                h = rng.uniform(6.5, 8.0)
                cr = h * 0.46
                for t in range(14):
                    d = 0.0 if t == 0 else rr * min(0.9, 0.15 + 0.06 * t)
                    a = a0 + t * 2.1
                    px, py = c.x + math.cos(a) * d, c.y + math.sin(a) * d
                    if inset(px, py, pl) < 0.9:
                        continue
                    z = on_lid(px, py, name, c.z)
                    if z is None or not air(px, py, cr * 0.55, z + h + cr * 0.4, z + 2.0):
                        continue
                    VG.crown_palm(mb, px, py, z, h, rng, rng.uniform(0.06, 0.16), a, fronds=5)
                    placed.append((px, py, cr))
                    nt_all += 1
                    break
            has_tree = bool(placed)
            # sem arvore (degrau coberto pelo bloco de cima: so a orla livre): 2 moitas; com arvore: 1 moita nas
            # tampas largas
            nb = 2 if not placed else (1 if rr >= 7.0 else 0)
            for i in range(nb):
                s = rng.uniform(1.5, 2.4) * min(1.0, 0.6 + rr * 0.08)
                for t in range(6 if has_tree else 12):
                    if not has_tree and t >= 6:
                        s *= 0.9
                    a = rng.uniform(0, TAU)
                    d = rr * rng.uniform(0.2, 0.75 if has_tree else 0.92)
                    px, py = c.x + math.cos(a) * d, c.y + math.sin(a) * d
                    if inset(px, py, pl) < s * 0.55:
                        continue
                    if any(math.hypot(px - qx, py - qy) < s + (1.2 if qr > 3.0 else qr) for qx, qy, qr in placed):
                        continue
                    z = on_lid(px, py, name, c.z)
                    if z is None or not air(px, py, s, z + s * 1.8, z + 0.6):
                        continue
                    VG.crown_bush(mb, px, py, z, s, rng)
                    placed.append((px, py, s * 0.9))
                    nb_all += 1
                    break
            lid_n["com_arvore" if has_tree else ("so_moitas" if placed else "vazias")] += 1
        nr = 0
        for qx, qy, qr, qh in L.PLATEAU_ROCKS:            # rochedos do plato: tufo de moitas no topo de pedra
            k = 1 if qr < 6.0 else 2
            for i in range(k):
                for t in range(6):
                    a = rng.uniform(0, TAU)
                    d = qr * rng.uniform(0.0, 0.3)
                    px, py = qx + math.cos(a) * d, qy + math.sin(a) * d
                    hz = hit(px, py, G + qh + 8.0, qh + 8.0)
                    if hz is None or not hz[2].startswith("DB_Ter_PlateauRocks") or hz[1].z < 0.85 or \
                            hz[0].z < G + qh * 0.5:
                        continue
                    s = rng.uniform(1.1, 1.6)
                    ok = True
                    for j in range(6):                      # a moita inteira em cima do topo (nada pendurado)
                        b = j * TAU / 6
                        hb = hit(px + math.cos(b) * s * 0.7, py + math.sin(b) * s * 0.7, hz[0].z + 3.0, 3.6)
                        if hb is None or not hb[2].startswith("DB_Ter_PlateauRocks") or abs(hb[0].z - hz[0].z) > 0.6:
                            ok = False
                            break
                    if ok:
                        VG.crown_bush(mb, px, py, hz[0].z, s, rng)
                        nr += 1
                        break
        self.count("coroas_arvores", nt_all)
        self.count("coroas_moitas", nb_all)
        self.count("coroas_rochedos", nr)
        self.count("tampas_mesa", len(lids))
        print("VEG tampas das mesas: %s" % lid_n)

    # ---------------------------------------------------------- colisao (orcamento) e fechamento
    def collisions(self):
        cands = []
        for kind, x, y, r, lv, h in self.col:
            reach = self.S.rim_d(x, y) > 4.6 + r
            if not reach:
                continue
            d = self.S.walk_d(x, y)
            if kind == "planter":
                d = -1.0                                   # floreira sempre (na rua / terraco)
            cands.append((d, kind, x, y, r, lv, h))
        cands.sort(key=lambda t: t[0])
        used = 0
        n_by = {}
        for d, kind, x, y, r, lv, h in cands:
            cost = 4 if kind == "rock" else 1
            if d > 20.0 and kind != "planter":
                continue
            if used + cost > COL_BUDGET:
                continue
            if kind == "rock":
                octo_col("DB_VegRock", x, y, r * 0.97, lv - 0.6, lv + h)
            elif kind == "planter":
                s = r * 1.414 * 0.98
                col_box("DB_VegPlanter", (s, s, h), (x, y, lv + h / 2))
            elif kind == "palm":
                hh, lean, a = h
                t6 = 7.0 / (hh + 0.45)                    # eixo do tronco do pe ate lv + 6,55 (acima da cabeca)
                off = lean * hh * t6 * t6
                col_seg("DB_VegTrunk", Vector((x, y, lv - 0.45)),
                        Vector((x + math.cos(a) * off, y + math.sin(a) * off, lv + 6.55)), 0.8)
            else:
                p0, p1 = h
                col_seg("DB_VegTrunk", p0, p0.lerp(p1, min(1.0, 7.0 / max(1.0, p1.z - p0.z))), max(0.7, r * 0.6))
            used += cost
            n_by[kind] = n_by.get(kind, 0) + 1
        print("VEG colisoes: %d caixas %s (candidatos %d)" % (used, n_by, len(cands)))

    def finish(self):
        self.beds.finish(recalc=False)
        for mb in (self.palms, self.shrubs, self.rocks, self.pots, self.crowns):
            mb.finish()

    def tris(self):
        """tris exatos das malhas em montagem (incremental: as faces so sao acrescentadas ate o finish)"""
        tot = 0
        for mb in (self.beds, self.palms, self.shrubs, self.rocks, self.pots, self.crowns):
            bm = mb.bm
            n = len(bm.faces)
            c0, t0 = self._tc.get(mb.name, (0, 0))
            if n != c0:
                bm.faces.ensure_lookup_table()
                t0 += sum(len(bm.faces[i].verts) - 2 for i in range(c0, n))
                self._tc[mb.name] = (n, t0)
            tot += t0
        return tot


def col_seg(area, a, b, side):
    """caixa de colisao de secao side x side ao longo do segmento a-b (tronco inclinado)"""
    d = b - a
    return col_box(area, (side, side, d.length), (a + b) / 2, d.to_track_quat("Z", "Y").to_euler())


def coverage(st, png=None):
    """fracao do plato livre (chao do terreno sem obstaculo, grade de 2 studs) que le VERDE: manchas, moitas, rochas,
    palmeiras e a grama que o terreno ja tinha. png: grava o mapa (areia / verde) para revisao"""
    xs, ys, free, green = st.mask
    img = np.zeros(free.shape + (3,), dtype=np.uint8) + np.array([30, 60, 120], dtype=np.uint8)
    X, Y = np.meshgrid(xs, ys)
    vol = np.zeros(free.shape, dtype=bool)
    for sx, sy, sr in st.S.solid:
        vol |= (X - sx) ** 2 + (Y - sy) ** 2 < (sr + 0.6) ** 2
    bed = np.zeros(free.shape, dtype=bool)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if free[j, i] and (int(math.floor(x)), int(math.floor(y))) in st.S.bedcells:
                bed[j, i] = True
    hit = free & (green | bed | vol)
    cov = int(hit.sum())
    img[free] = (226, 178, 118)
    img[hit] = (90, 170, 60)
    if png:
        _png(png, np.ascontiguousarray(img[::-1]))
    tot = int(free.sum())
    return cov / max(1, tot), tot * 4.0


def _dilate(m, k):
    out = m.copy()
    for _ in range(max(0, k)):
        t = out.copy()
        t[1:, :] |= out[:-1, :]
        t[:-1, :] |= out[1:, :]
        t[:, 1:] |= out[:, :-1]
        t[:, :-1] |= out[:, 1:]
        out = t
    return out


def _clearance(m):
    """distancia (em celulas) de cada celula livre ate a borda da regiao livre (erosao alternando vizinhanca de 4 e
    de 8: aproxima um disco)"""
    D = np.zeros(m.shape, dtype=np.int32)
    cur = m.copy()
    d = 0
    while cur.any() and d < 40:
        d += 1
        D[cur] = d
        t = cur.copy()
        t[1:, :] &= cur[:-1, :]
        t[:-1, :] &= cur[1:, :]
        t[:, 1:] &= cur[:, :-1]
        t[:, :-1] &= cur[:, 1:]
        if d % 2 == 0:
            t[1:, 1:] &= cur[:-1, :-1]
            t[:-1, :-1] &= cur[1:, 1:]
            t[1:, :-1] &= cur[:-1, 1:]
            t[:-1, 1:] &= cur[1:, :-1]
        t[0, :] = t[-1, :] = False
        t[:, 0] = t[:, -1] = False
        cur = t
    return D


def _png(path, a):
    import struct, zlib
    h, w, _ = a.shape
    raw = b"".join(bytes(1) + a[r].tobytes() for r in range(h))

    def ch(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    head = bytes((137, 80, 78, 71, 13, 10, 26, 10))
    with open(path, "wb") as f:
        f.write(head + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
                ch(b"IDAT", zlib.compress(raw, 6)) + ch(b"IEND", b""))


def build():
    import time
    t0 = time.time()
    st = Stage()
    t1 = time.time()
    tt, tr = [], []
    t_prev = 0
    for nm, fn in (("vila", st.hub), ("alas", st.cap_wings), ("pocos", st.pools_dojo_pad), ("anel", st.ground_ring),
                   ("pes", st.feet), ("enchimento", st.fill_greedy), ("topos", st.tops), ("colisao", st.collisions),
                   ("malhas", st.finish)):
        ta = time.time()
        if nm == "malhas":
            print("VEG tris por fase: %s | total %d" % (", ".join(tr), t_prev))
        fn()
        tt.append("%s %.1f" % (nm, time.time() - ta))
        if nm != "malhas":
            t_now = st.tris()
            tr.append("%s %d" % (nm, t_now - t_prev))
            t_prev = t_now
    print("VEG tempos: " + ", ".join(tt))
    import os
    cv, fa = coverage(st, os.environ.get("DB_VEG_MAP"))
    print("VEG vinhetas (n, palmeiras, moitas): %s" % st.kinds)
    print("VEG falhas %s" % {k: sorted(v.items(), key=lambda t: -t[1])[:5] for k, v in st.fails.items()})
    print("VEG %s | cobertura ~%.0f%% de %.0f studs2 livres | raios %.1fs, total %.1fs" % (
        st.n, cv * 100.0, fa, t1 - t0, time.time() - t0))
