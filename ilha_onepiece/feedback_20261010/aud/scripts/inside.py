import bpy, json, sys, os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT = os.path.dirname(os.path.abspath(__file__))
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
D = json.load(open(PROJ + "/export/ilha5_data.json"))
objs = sorted(set(m["obj"] for m in D["meshes"]))
dg = bpy.context.evaluated_depsgraph_get()
verts, tris, tobj, tmat, mats, mi = [], [], [], [], [], {}
for oi, nm in enumerate(objs):
    o = bpy.data.objects[nm]; oe = o.evaluated_get(dg); me = oe.to_mesh(); mw = o.matrix_world; b = len(verts)
    verts += [tuple(mw @ v.co) for v in me.vertices]
    me.calc_loop_triangles()
    for t in me.loop_triangles:
        tris.append(tuple(b + k for k in t.vertices)); tobj.append(oi)
        mn = o.material_slots[t.material_index].material.name
        if mn not in mi: mi[mn] = len(mats); mats.append(mn)
        tmat.append(mi[mn])
    oe.to_mesh_clear()
BV = BVHTree.FromPolygons(verts, tris, all_triangles=True)
P = np.load(os.path.join(OUT, "reach_pts.npy"))
UP = Vector((0, 0, 1))
res = np.full((len(P), 4), -1.0, np.float32)
for k, (x, y, h) in enumerate(P):
    r = BV.ray_cast(Vector((float(x), float(y), float(h) + 0.4)), UP, 4.6)
    if r[0] is not None:
        res[k] = (r[0].z - h, 1.0 if r[1].z > 0 else 0.0, tobj[r[2]], tmat[r[2]])
np.save(os.path.join(OUT, "inside.npy"), res)
json.dump(dict(objs=objs, mats=mats), open(os.path.join(OUT, "meta2.json"), "w"))
print("INSIDE done", int((res[:, 0] >= 0).sum()))
