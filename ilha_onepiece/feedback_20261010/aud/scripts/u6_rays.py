import bpy, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
D = json.load(open(PROJ + "/export/ilha5_data.json"))
objs = sorted(set(m["obj"] for m in D["meshes"]))
dg = bpy.context.evaluated_depsgraph_get()
def bvh(names, excl=None):
    V, T, info = [], [], []
    for nm in names:
        o = bpy.data.objects[nm]; oe = o.evaluated_get(dg); me = oe.to_mesh(); b = len(V)
        V += [tuple(o.matrix_world @ v.co) for v in me.vertices]
        me.calc_loop_triangles()
        for t in me.loop_triangles:
            mn = o.material_slots[t.material_index].material.name
            T.append(tuple(b + k for k in t.vertices)); info.append((nm, mn))
        oe.to_mesh_clear()
    return BVHTree.FromPolygons(V, T, all_triangles=True), info
BV, INFO = bvh(objs)
# sem a ponte: tudo menos as tabuas/laca do OP_Cap_Oeste (filtra por material depois: hits multiplos)
def hits(x, y, z0=130.0, n=6):
    out = []; z = z0
    for _ in range(n):
        h = BV.ray_cast(Vector((x, y, z)), Vector((0, 0, -1)), 500)
        if h[0] is None: break
        out.append((round(h[0].z, 2), INFO[h[2]][0], INFO[h[2]][1])); z = h[0].z - 0.01
    return out
res = {}
for yc in (182.0, 252.0):
    for yy in (yc, yc + 3.0, yc - 6.0):
        row = []
        for k in range(0, 121):
            x = -186.0 + k * 0.2 + 0.013
            row.append((round(x, 2), hits(x, yy + 0.017)))
        res["y%.0f" % yy] = row
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "u6.json"), "w"))
print("U6 ok")
