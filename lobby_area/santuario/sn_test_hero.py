# sn_test_hero.py - render da PECA-HEROI (bigorna-tita, martelo, forja do Ignis, praca das runas) com o golem do Ignis
# uso: blender -b --factory-startup --python sn_test_hero.py -- <pasta> [CAM ...] [--no-ignis] [--save x.blend]
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sn_lib as SL
import bpy
import fm_lib

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
cams = [a for a in argv[1:] if a.startswith("CAM_")]
os.makedirs(out, exist_ok=True)
t0 = time.time()
SL.reset_scene()
SL.register()
fm_lib.make_materials()
import sn_layout as L
import sn_hero as H

g = SL.Build("WB_Ter_Test", "02_TERRAIN")
pl = [(x, -z) for (x, z) in L.PLATEAU]
g.prism(pl, L.PLATEAU_BOTTOM, L.Y_GRASS - 0.6, "WB_Rock")
g.prism([(x * 1.01, y * 1.01) for (x, y) in pl], L.Y_GRASS - 0.6, L.Y_GRASS, "WB_Grass")
g.cyl((0, 0, L.Y_WATER - 1.0), (0, 0, L.Y_WATER), L.LAKE_R, "WB_Water", seg=48)
g.finish()
if "--relief" in argv:
    import sn_relief
    sn_relief.build()
import random as _r
import math as _m
import sn_paint as P
P.build_paints()
import sn_veg as VG
VG.build_kit(reuse="--reuse" in argv)
rr = _r.Random(4)
spots = {}
for k in range(70):
    a = rr.uniform(0, 6.283)
    d = rr.uniform(96, 142)
    x, z = d * _m.cos(a), d * _m.sin(a) - 10
    if abs(x) < 20 and z > 40:
        continue
    nm = rr.choice(["oak1", "oak2", "oak3", "pine1", "pine2", "pine1", "oak1", "oakG"])
    spots.setdefault(nm, []).append((x, z, L.Y_GRASS, rr.uniform(0, 360), rr.uniform(0.85, 1.15)))
for k in range(30):
    a = rr.uniform(0, 6.283)
    d = rr.uniform(60, 95)
    x, z = d * _m.cos(a), d * _m.sin(a)
    if abs(x) < 24 and z > 30:
        continue
    spots.setdefault(rr.choice(["bush1", "bushF"]), []).append((x, z, L.Y_GRASS, rr.uniform(0, 360), rr.uniform(0.8, 1.3)))
spots["ancient"] = [(-104.0, -40.0, L.Y_GRASS, 30.0, 1.0)]
for nm, sp in spots.items():
    VG.place(nm, sp)
VG.hide_kit()
H.anvil()
H.hammer()
H.forge()
H.plaza()
print("HEROI construido %.0fs" % (time.time() - t0))
if "--bake" in argv:
    import sn_paint as P
    P.build_paints()
    for pre, at, pps in (("WB_Frg_Anvil", "Anvil", 7.0), ("WB_Frg_Hammer", "Hammer", 8.0), ("WB_Frg_Hall", "Hall", 8.0),
                         ("WB_Town_Plaza", "Plaza", 8.0)):
        P.bake_group(pre, at, pps=pps, samples=16, reuse="--reuse" in argv)
if "--no-ignis" not in argv:
    fbx = os.path.join(SL.W.ROOT, "output", "ignis_golem_20261007", "export", "final", "IGNIS_GOLEM_417ec4.fbx")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx, use_image_search=True)
    off = SL.RB(L.IGNIS_ROOT[0], L.IGNIS_ROOT[2], L.IGNIS_ROOT[1])
    for o in bpy.data.objects:
        if o not in before:
            if o.parent is None:
                o.location = o.location + off
            o.name = "PREVIEW_Ignis_" + o.name
tris = {}
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("WB_"):
        k = o.name.split("__")[0]
        tris[k] = tris.get(k, 0) + sum(len(p.vertices) - 2 for p in o.data.polygons)
print("TRIS", tris)
SL.setup_render(res=(1600, 900), samples=64)
for n, (e, t, lens) in L.cams().items():
    SL.camera(n, e, t, lens)
if "--save" in argv:
    bpy.ops.wm.save_as_mainfile(filepath=argv[argv.index("--save") + 1])
for n in (cams or ["CAM_SN_Hero", "CAM_SN_Spawn", "CAM_SN_Forge", "CAM_SN_Anvil", "CAM_SN_Hammer", "CAM_SN_Plaza"]):
    SL.render(bpy.data.objects[n], os.path.join(out, n + ".png"))
print("FIM %.0fs" % (time.time() - t0))
