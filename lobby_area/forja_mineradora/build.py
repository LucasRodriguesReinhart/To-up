# build.py - reconstroi o lobby inteiro do zero e salva o .blend
# uso: blender -b --factory-startup --python build.py -- [etapas...]
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BLOCKOUT = "blockout" in argv
OUT = os.environ.get("FM_OUT") or os.path.join(HERE, "lobby_forja_mineradora.blend")

mods = ["fm_lib", "fm_parts", "fm_layout", "fm_terrain", "fm_scene", "fm_blockout"]
extra = ["fm_forge", "fm_mine", "fm_water", "fm_buildings", "fm_portals", "fm_konoha", "fm_props", "fm_veg",
         "fm_lights"]
for m in mods + extra:
    if os.path.exists(os.path.join(HERE, m + ".py")):
        importlib.import_module(m)

import fm_pv3
fm_pv3.load()       # portais v3: registram materiais/texturas das espirais antes do make_materials
import fm_lib, fm_terrain, fm_scene
t0 = time.time()
fm_lib.reset_scene()
fm_lib.make_materials()
fm_scene.setup_render()
fm_scene.setup_world()
fm_scene.setup_sun()
fm_terrain.build_ground()
fm_terrain.build_cliffs()
fm_terrain.build_mountains()
print("terrain", round(time.time() - t0, 1))


def step(modname, fn="build"):
    if modname in sys.modules:
        t = time.time()
        getattr(sys.modules[modname], fn)()
        print(modname, round(time.time() - t, 1))
        return True
    return False


done = {}
for m in extra:
    done[m] = step(m)
if BLOCKOUT or not all(done.get(k) for k in ("fm_forge", "fm_mine", "fm_water", "fm_buildings", "fm_portals")):
    import fm_blockout
    fm_blockout.build()
fm_scene.cameras()
fm_scene.scale_reference()
fm_scene.clouds()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
tris = 0
for o in bpy.data.objects:
    if o.type == "MESH" and not o.name.startswith("COL_"):
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
print("BUILD OK objs=%d tris=%d t=%.1fs" % (len(bpy.data.objects), tris, time.time() - t0))
