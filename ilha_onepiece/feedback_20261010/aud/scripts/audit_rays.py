# audit_rays.py - V2 auditoria (so leitura): raios de cima na COPIA do ilha_onepiece.blend
# visual = as 72 malhas exportadas (export 37998c7c); colisao = as 743 caixas EXPORTADAS (ilha5_data.json, Roblox -> local)
# saida: grid.npz (grade 1,5) + lines.npz (linhas finas 0,2 a cada 3) + meta.json
import bpy, json, math, sys, os, time
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

OUT = os.path.dirname(os.path.abspath(__file__))
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L
D = json.load(open(PROJ + "/export/ilha5_data.json"))

# ------------------------------------------------------------------ visual
objs = sorted(set(m["obj"] for m in D["meshes"]))
dg = bpy.context.evaluated_depsgraph_get()
verts, tris, tri_obj, tri_mat = [], [], [], []
mats = []
mat_idx = {}
for oi, nm in enumerate(objs):
    o = bpy.data.objects[nm]
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    mw = o.matrix_world
    base = len(verts)
    for v in me.vertices:
        verts.append(tuple(mw @ v.co))
    me.calc_loop_triangles()
    for t in me.loop_triangles:
        tris.append(tuple(base + i for i in t.vertices))
        tri_obj.append(oi)
        mn = o.material_slots[t.material_index].material.name if o.material_slots and o.material_slots[t.material_index].material else "?"
        if mn not in mat_idx:
            mat_idx[mn] = len(mats)
            mats.append(mn)
        tri_mat.append(mat_idx[mn])
    oe.to_mesh_clear()
print("AUD visual objs", len(objs), "tris", len(tris))
BV = BVHTree.FromPolygons(verts, tris, all_triangles=True)
tri_obj = np.array(tri_obj, np.int16)
tri_mat = np.array(tri_mat, np.int16)

# ------------------------------------------------------------------ colisao exportada -> local
a = math.radians(L.WORLD_YAW_DEG)
ca, sa = math.cos(a), math.sin(a)


def vec_local(v):
    wx, wy, wz = v[0], -v[2], v[1]
    return Vector((wx * ca + wy * sa, -wx * sa + wy * ca, wz))


def pt_local(p):
    x, y = L.local_of_roblox(p[0], p[2])
    return Vector((x, y, p[1]))


cverts, ctris, cbox = [], [], []
for ci, c in enumerate(D["collisions"]):
    ax = vec_local(c["x"]).normalized()
    ay = vec_local(c["y"]).normalized()
    az = ax.cross(ay).normalized()
    sx, sy, sz = [s / 2 for s in c["size"]]
    p = pt_local(c["pos"])
    b = len(cverts)
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                cverts.append(tuple(p + ax * sx * i + ay * sy * j + az * sz * k))
    # cubo: indices (i,j,k) -> 4i+2j+k
    F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for f in F:
        ctris.append((b + f[0], b + f[1], b + f[2]))
        ctris.append((b + f[0], b + f[2], b + f[3]))
        cbox += [ci, ci]
CB = BVHTree.FromPolygons(cverts, ctris, all_triangles=True)
cbox = np.array(cbox, np.int16)
print("AUD col boxes", len(D["collisions"]))

DOWN = Vector((0, 0, -1))
ZTOP = 420.0


def vis_first(x, y, z0=ZTOP):
    h = BV.ray_cast(Vector((x, y, z0)), DOWN, 1000.0)
    if h[0] is None:
        return (np.nan, 0.0, -1, -1)
    n = h[1]
    nz = abs(n.z)
    return (h[0].z, nz, int(tri_obj[h[2]]), int(tri_mat[h[2]]))


def col_hits(x, y, maxn=10):
    out = []
    z = ZTOP
    for _ in range(maxn):
        h = CB.ray_cast(Vector((x, y, z)), DOWN, 1000.0)
        if h[0] is None:
            break
        out.append((h[0].z, 1 if h[1].z > 0 else -1, int(cbox[h[2]])))   # normal geometrica: + = topo (entra), - = fundo
        z = h[0].z - 0.002
    return out


def col_below(x, y, z0):
    h = CB.ray_cast(Vector((x, y, z0)), DOWN, 1000.0)
    return np.nan if h[0] is None else h[0].z


# ------------------------------------------------------------------ grade 1,5
STEP = 1.5
X0, X1, Y0, Y1 = -272.0 + 0.0371, 372.0 + 0.0371, -136.0 + 0.0613, 632.0 + 0.0613
xs = np.arange(X0, X1 + 1e-6, STEP)
ys = np.arange(Y0, Y1 + 1e-6, STEP)
NX, NY = len(xs), len(ys)
MAXH = 10
zv = np.full((NY, NX), np.nan, np.float32)
nv = np.zeros((NY, NX), np.float32)
vo = np.full((NY, NX), -1, np.int16)
vm = np.full((NY, NX), -1, np.int16)
zcb = np.full((NY, NX), np.nan, np.float32)        # 1a colisao abaixo de zv + 1,5
ch = np.full((NY, NX, MAXH), np.nan, np.float32)   # hits de colisao (z) de cima para baixo
cs = np.zeros((NY, NX, MAXH), np.int8)              # sinal (+1 topo, -1 fundo)
cbx = np.full((NY, NX, MAXH), -1, np.int16)
t0 = time.time()
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        z, n, oi, mi = vis_first(float(x), float(y))
        zv[j, i] = z
        nv[j, i] = n
        vo[j, i] = oi
        vm[j, i] = mi
        if z == z:
            zcb[j, i] = col_below(float(x), float(y), z + 1.5)
        hs = col_hits(float(x), float(y), MAXH)
        for k, (hz, sg, bi) in enumerate(hs):
            ch[j, i, k] = hz
            cs[j, i, k] = sg
            cbx[j, i, k] = bi
print("AUD grid %dx%d %.1fs" % (NX, NY, time.time() - t0))
np.savez_compressed(os.path.join(OUT, "grid.npz"), xs=xs, ys=ys, zv=zv, nv=nv, vo=vo, vm=vm, zcb=zcb, ch=ch, cs=cs, cbx=cbx)

# ------------------------------------------------------------------ linhas finas (U5): passo 0,2, a cada 3
FS = 0.2
lines = {}
for axis in ("x", "y"):
    if axis == "x":
        fixed = np.arange(Y0, Y1 + 1e-6, 3.0)
        run = np.arange(X0, X1 + 1e-6, FS)
    else:
        fixed = np.arange(X0, X1 + 1e-6, 3.0)
        run = np.arange(Y0, Y1 + 1e-6, FS)
    Z = np.full((len(fixed), len(run)), np.nan, np.float32)
    N = np.zeros((len(fixed), len(run)), np.float32)
    M = np.full((len(fixed), len(run)), -1, np.int16)
    O = np.full((len(fixed), len(run)), -1, np.int16)
    C = np.full((len(fixed), len(run)), np.nan, np.float32)
    for a_, f in enumerate(fixed):
        for b_, r in enumerate(run):
            x, y = (float(r), float(f)) if axis == "x" else (float(f), float(r))
            z, n, oi, mi = vis_first(x, y)
            Z[a_, b_] = z
            N[a_, b_] = n
            M[a_, b_] = mi
            O[a_, b_] = oi
            if z == z:
                C[a_, b_] = col_below(x, y, z + 1.5)
    lines[axis] = dict(fixed=fixed, run=run, Z=Z, N=N, M=M, O=O, C=C)
    print("AUD lines", axis, Z.shape, "%.1fs" % (time.time() - t0))
np.savez_compressed(os.path.join(OUT, "lines.npz"), **{"%s_%s" % (ax, k): v for ax, d in lines.items() for k, v in d.items()})
json.dump(dict(objs=objs, mats=mats, cols=[c["name"] for c in D["collisions"]]), open(os.path.join(OUT, "meta.json"), "w"))
print("AUD done %.1fs" % (time.time() - t0))
