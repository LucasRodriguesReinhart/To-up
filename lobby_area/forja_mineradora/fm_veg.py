# fm_veg - vegetacao e rochas por raycast na superficie real do terreno, com exclusao de caminhos e colisoes.
# Enquadra (bordas, penhascos, terracos), quebra repeticao e nunca bloqueia rota, portal ou forja.
import math, random
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from fm_lib import MB, D, col_box, point_in_poly
from fm_parts import pine, bush, sakura, crystal_cluster, rock_scatter
import fm_layout as L


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
    """pegadas 2D (retangulos orientados) das colisoes + faixas dos caminhos"""

    def __init__(self, margin=2.5):
        self.rects = []
        for o in bpy.data.objects:
            if not o.name.startswith("COL_") or o.get("col_kind") in ("Floor",):
                continue
            if o.name.startswith(("COL_Floor", "COL_Terrace", "COL_MidLedge", "COL_BackMountain", "COL_WestCliff",
                                  "COL_EastCliff", "COL_MidWall", "COL_UpperWall", "COL_Konoha")):
                continue
            self.rects.append((o.location.copy(), o.rotation_euler.z, o.scale.x / 2 + margin, o.scale.y / 2 + margin,
                               o.location.z - o.scale.z / 2, o.location.z + o.scale.z / 2))
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

    def blocked(self, x, y, z):
        for (c, a, hx, hy, z0, z1) in self.rects:
            if z < z0 - 3 or z > z1 + 3:
                continue
            dx, dy = x - c.x, y - c.y
            ca, sa = math.cos(-a), math.sin(-a)
            lx, ly = dx * ca - dy * sa, dx * sa + dy * ca
            if abs(lx) < hx and abs(ly) < hy:
                return True
        for poly in self.polys:
            if point_in_poly(x, y, poly):
                return True
        for (cx, cy, r) in self.circles:
            if (x - cx) ** 2 + (y - cy) ** 2 < r * r:
                return True
        return False


def build():
    rng = random.Random(1010)
    bvh, mats = surface_bvh()
    blk = Blockers()
    placed = []

    def free(x, y, r):
        for (px, py, pr) in placed:
            if (x - px) ** 2 + (y - py) ** 2 < (r + pr) ** 2:
                return False
        return True

    def ground(x, y, top=260.0):
        hit = bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)), 400)
        if hit[0] is None:
            return None
        return hit[0], hit[1], mats[hit[2]]

    pines = MB("VEG_Pines", "09_VEGETATION", rng)
    bushes = MB("VEG_Bushes", "09_VEGETATION", rng)
    rocks = MB("VEG_Rocks", "09_VEGETATION", rng)
    cr = MB("VEG_Crystal_Outcrops", "09_VEGETATION", rng)
    sak = MB("VEG_Sakura", "09_VEGETATION", rng)
    n_p = n_b = 0

    # 1) arvores no piso do vale (junto as bordas e entre construcoes), sem bloquear rotas
    for i in range(1400):
        x = rng.uniform(L.WEST_X + 2, L.EAST_X - 2)
        y = rng.uniform(-60, 60)
        g = ground(x, y, 20.0)
        if not g or g[2] != "Grass" or g[1].z < 0.9 or abs(g[0].z - L.FLOOR) > 0.6:
            continue
        # prefere bordas: probabilidade cresce perto das paredes do vale
        edge = min(x - L.WEST_X, L.EAST_X - x, y + 62, 62 - y)
        if edge > 22 and rng.random() < 0.8:
            continue
        if blk.blocked(x, y, g[0].z) or not free(x, y, 4.5):
            continue
        h = rng.uniform(11, 19)
        pine(pines, (x, y, g[0].z - 0.2), h, rng)
        col_box("Veg", (1.8, 1.8, h * 0.4), (x, y, g[0].z + h * 0.2))
        placed.append((x, y, 3.5))
        n_p += 1
        if n_p > 70:
            break
    # 2) topos dos penhascos, terracos e montanhas (so onde ha grama plana) - moldura do mapa
    for i in range(5000):
        x = rng.uniform(-230, 240)
        y = rng.uniform(-110, 300)
        if -128 < x < 143 and -60 < y < 128:
            continue
        g = ground(x, y)
        if not g or g[2] not in ("Grass", "Grass_Dark") or g[1].z < 0.85 or g[0].z < 10:
            continue
        if not free(x, y, 3.0):
            continue
        # nao tapa o corredor de Konoha
        if -126 < x < -76 and y > 118:
            continue
        h = rng.uniform(10, 20)
        pine(pines, (x, y, g[0].z - 0.3), h, rng)
        placed.append((x, y, 3.0))
        n_p += 1
        if n_p > 470:
            break
    # topos das paredes do vale e do terraco (primeira fila visivel)
    for i in range(3000):
        x = rng.uniform(-170, 185)
        y = rng.uniform(-120, 160)
        g = ground(x, y)
        if not g or g[2] != "Grass" or g[1].z < 0.85 or g[0].z < 20:
            continue
        if blk.blocked(x, y, g[0].z) or not free(x, y, 3.2):
            continue
        if -126 < x < -76 and y > 118:
            continue
        if abs(g[0].z - L.TERR) < 0.8 and (L.UPPER_FRONT_Y < y < L.TERR_BACK_Y):
            # terraco: so perto do fundo e longe dos portais
            if y < L.PORTAL_Y + 6 or min(abs(x - px) for px in L.PORTAL_X) < 20:
                continue
        h = rng.uniform(9, 17)
        pine(pines, (x, y, g[0].z - 0.3), h, rng)
        placed.append((x, y, 3.0))
        n_p += 1
        if n_p > 610:
            break
    pines.finish()

    # 3) arbustos e rochas soltas no vale (base de construcoes, pes de penhasco)
    for i in range(2000):
        x = rng.uniform(L.WEST_X + 1, L.EAST_X - 1)
        y = rng.uniform(-60, 60)
        g = ground(x, y, 20.0)
        if not g or g[2] != "Grass" or abs(g[0].z - L.FLOOR) > 0.6:
            continue
        if blk.blocked(x, y, g[0].z) or not free(x, y, 1.6):
            continue
        if rng.random() < 0.7:
            bush(bushes, (x, y, g[0].z - 0.3), rng.uniform(1.4, 2.4), rng)
        else:
            s = rng.uniform(1.2, 3.0)
            rocks.rock((x, y, g[0].z + s * 0.2), (s * 1.3, s * 1.1, s * 0.8), "Cliff_Rock", 1, (0, 0, rng.uniform(0, 6)))
        placed.append((x, y, 1.5))
        n_b += 1
        if n_b > 160:
            break
    bushes.finish()
    rocks.finish()

    # 4) afloramentos de cristal (acento frio) perto da mina e nas bases dos penhascos oeste/sul
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

    # 5) sakura moderada no lado oeste (perto do portal Naruto) e junto as cabanas oeste
    for (x, y) in ((-120, 36), (-98, 50), (-126, 12), (-70, 44)):
        g = ground(x, y, 40.0)
        if not g or blk.blocked(x, y, g[0].z):
            continue
        sakura(sak, (x, y, g[0].z - 0.2), rng.uniform(10, 13), rng)
        col_box("Veg", (1.8, 1.8, 6.0), (x, y, g[0].z + 3.0))
    sak.finish()
    print("VEG pines=%d bushes/rocks=%d" % (n_p, n_b))
