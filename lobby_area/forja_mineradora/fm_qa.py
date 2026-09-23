# fm_qa - testes automaticos: navegacao sobre as colisoes COL_ + auditoria tecnica da cena
# uso: blender -b lobby_forja_mineradora.blend --python fm_qa.py -- [nav] [tech]
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import fm_layout as L

STEP_UP = 2.3       # degrau maximo que o Humanoid sobe
DROP = 2.3          # queda maxima aceita nas rotas (rotas nao podem exigir pulo)
HEAD = 6.5          # altura livre minima
BODY_R = 1.1        # raio do corpo


OWNER = []


def col_bvh():
    verts, polys = [], []
    OWNER.clear()
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
        OWNER.extend([o.name] * len(o.data.polygons))
    return BVHTree.FromPolygons(verts, polys), len(polys)


def ground(bvh, x, y, zref, up=STEP_UP + 0.2):
    hit = bvh.ray_cast(Vector((x, y, zref + up)), Vector((0, 0, -1)), 60)
    return hit[0].z if hit[0] is not None else None


def walk(bvh, pts, z0):
    fails = []
    z = z0
    samples = []
    for a, b in zip(pts, pts[1:]):
        a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        n = max(1, int((b - a).length / 0.5))
        for i in range(n + 1):
            p = a + (b - a) * (i / n)
            samples.append(p)
    for p in samples:
        g = ground(bvh, p.x, p.y, z)
        if g is None:
            fails.append(("VAZIO", tuple(round(c, 1) for c in p.xy), round(z, 1)))
            break
        if g - z > STEP_UP:
            fails.append(("DEGRAU_ALTO", tuple(round(c, 1) for c in p.xy), round(g - z, 2)))
            break
        if z - g > DROP:
            fails.append(("QUEDA", tuple(round(c, 1) for c in p.xy), round(z - g, 2)))
            break
        z = g
        # altura livre
        h = bvh.ray_cast(Vector((p.x, p.y, z + 0.4)), Vector((0, 0, 1)), HEAD - 0.4)
        if h[0] is not None:
            fails.append(("TETO_BAIXO", tuple(round(c, 1) for c in p.xy), round(h[0].z - z, 2)))
            break
        # corpo livre (joelho/peito/cabeca)
        for hz in (2.0, 3.6, 5.0):
            nn = bvh.find_nearest(Vector((p.x, p.y, z + hz)), BODY_R * 0.9)
            if nn[0] is not None:
                fails.append(("OBSTACULO", tuple(round(c, 1) for c in p.xy), round(hz, 1), OWNER[nn[2]]))
                break
        if fails:
            break
    return fails, z


def routes():
    P = L.PORTAL_X
    r = {}
    r["SPAWN->IGNIS"] = ([(0, -104), (0, -84), (0, -66), (0, -50), (0, -30), L.PLAYER_IGNIS], L.SPAWN_Z)
    mx, my = L.MINE_MOUTH
    dx, dy = math.cos(L.MINE_DIR), math.sin(L.MINE_DIR)
    sx, sy = -dy * 3.5, dx * 3.5   # anda ao lado dos trilhos
    r["SPAWN->MINE"] = ([(0, -104), (0, -66), (0, -54), (-14, -46), (-22, -44), (-40, -46), (mx - 12 * dx + sx, my - 12 * dy + sy),
                         (mx + sx, my + sy), (mx + 22 * dx + sx, my + 22 * dy + sy)], L.SPAWN_Z)
    r["IGNIS->SHOP"] = ([L.PLAYER_IGNIS, (12, -34), (20, -38), (29, -36), (32, -38)], L.FLOOR)
    ds = L.MILL[0] + 9.0
    r["IGNIS->WHEELHOUSE"] = ([L.PLAYER_IGNIS, (18, -24), (24, -20), (38, -18), (38, -8), (38, 2), (ds, 6), (ds, 16)],
                              L.FLOOR)
    for k, px in zip(L.PORTAL_KEYS, P):
        if px < 0:
            via = [(-20, -34), (-24, -36), (-38, -24), (-44, -8), (-44, 34), (-44, 41), (px, 41)]
        elif px < L.RIVER_X[0]:
            via = [(18, -24), (24, -20), (38, -18), (38, -8), (38, 36), (38, 41), (px, 41)]
        else:
            via = [(18, -24), (24, -20), (38, -18), (38, -8), (38, 36), (38, 41), (50, 41), (74, 41), (px, 41)]
        r["IGNIS->PORTAL_" + k] = ([L.PLAYER_IGNIS] + via + [(px, 46), (px, 62.5), (px, 70), (px, 80),
                                   (px, L.FLIGHT2_Y1 + 0.5), (px, L.FLIGHT2_Y1 + 6)], L.FLOOR)
    r["PORTALS->NARUTO(ledge)"] = ([(P[2], 66), (P[1], 66), (P[0], 66), (P[0], 80), (P[0], L.FLIGHT2_Y1 + 6)], L.MID)
    kp = L.KONOHA_PATH
    r["NARUTO->KONOHA"] = ([(P[0], L.FLIGHT2_Y1 + 6), (P[0], L.PORTAL_Y), kp[0]] + list(kp[1:]), L.TERR)
    r["EAST_BANK"] = ([L.PLAYER_IGNIS, (18, -24), (24, -20), (40, -18), (54, -18), (70, -18), (96, -18), (96, 36),
                       (76, 41), (P[4], 44), (P[4], 62.5)], L.FLOOR)
    r["SPAWN->FORGE_HALL"] = ([(0, -104), (0, -66), (0, -30), (-14.5, -14), (-14.5, 2), (-14.5, 10), (-6, 16)], L.SPAWN_Z)
    r["HALL->FURNACE"] = ([(-6, 16), (0, 18), (0, 24), (3, 26)], L.FL)
    r["PLAZA->LOFT_BALCONY"] = ([(-14, -24), (L.FORGE_WING_L[2] - 3.8, -22), (L.FORGE_WING_L[2] - 3.8, -12),
                                 (L.FORGE_WING_L[2] - 3.8, 1.5), (L.FORGE_WING_L[0] + 10.5, 3.0), (L.FORGE_WING_L[0] + 10.5, 9.0),
                                 (L.FORGE_WING_L[0] + 6.0, 12.0)], L.FLOOR)
    r["PLAZA->COUNTER_STALL"] = ([(10, -22), (L.FORGE_WING_R[0] + 5, -6), (L.FORGE_WING_R[0] + 5, -3.5)], L.FLOOR)
    r["RAIL_DOOR->INTAKE"] = ([(-44, 15), (-36, 15), (-30, 14.8), (-27, 11)], L.FLOOR)
    return r


def nav():
    bvh, n = col_bvh()
    print("COL faces:", n)
    res = {}
    for name, (pts, z0) in routes().items():
        f, zend = walk(bvh, pts, z0)
        res[name] = f
        print(("OK   " if not f else "FAIL ") + name + ("" if not f else "  " + str(f)))
    return res


def tech():
    bad_names, no_mat, neg_scale, heavy, nonuni = [], [], [], [], []
    import re
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh)(\.\d+)?$")
    tris_total = 0
    per = []
    for o in bpy.data.objects:
        if gen.match(o.name):
            bad_names.append(o.name)
        if o.type == "MESH":
            if not o.name.startswith("COL_"):
                t = sum(len(p.vertices) - 2 for p in o.data.polygons)
                tris_total += t
                per.append((t, o.name))
                if len(o.data.materials) == 0:
                    no_mat.append(o.name)
                if t > 120000:
                    heavy.append((o.name, t))
                if any(s < 0 for s in o.scale):
                    neg_scale.append(o.name)
                if not o.name.startswith("COL_") and any(abs(s - 1) > 1e-4 for s in o.scale):
                    nonuni.append(o.name)
    # degeneradas / non-manifold (so malhas visuais)
    degen = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith("COL_"):
            for p in o.data.polygons:
                if p.area < 1e-6:
                    degen += 1
    per.sort(reverse=True)
    print("TECH names_genericos=%d sem_material=%d escala_neg=%d escala_nao_aplicada=%d pesadas=%d degeneradas=%d"
          % (len(bad_names), len(no_mat), len(neg_scale), len(nonuni), len(heavy), degen))
    print("TECH tris_total=%d objetos=%d materiais=%d" % (tris_total, len(bpy.data.objects), len(bpy.data.materials)))
    print("TECH top:", per[:8])
    if bad_names:
        print("TECH nomes:", bad_names[:20])
    if no_mat:
        print("TECH sem material:", no_mat[:20])
    return dict(bad_names=bad_names, no_mat=no_mat, degen=degen, tris=tris_total)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["nav", "tech"]
    if "nav" in argv:
        nav()
    if "tech" in argv:
        tech()
