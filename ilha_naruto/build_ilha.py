# build_ilha.py - reconstroi a Ilha 1 (Naruto) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_ilha.py -- [blockout]
#      IL_OUT=<caminho.blend> muda a saida (padrao ilha_naruto.blend)
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL                  # poe o pipeline do lobby no sys.path
import bpy
import fm_lib
import il_layout as L
import il_scene

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BLOCKOUT = "blockout" in argv
OUT = os.environ.get("IL_OUT") or os.path.join(HERE, "ilha_naruto.blend")

t0 = time.time()
IL.reset_scene()
fm_lib.make_materials()
il_scene.setup(res=(1600, 900), samples=24)

# modulos de detalhe (cada um substitui a parte correspondente do blockout quando existir)
DETAIL = ["il_terrain", "il_mining", "il_entrance", "il_village", "il_summon", "il_water", "il_exit", "il_gates",
          "il_props", "il_veg", "il_lights"]
done = {}
if not BLOCKOUT:
    for m in DETAIL:
        if os.path.exists(os.path.join(HERE, m + ".py")):
            t = time.time()
            importlib.import_module(m).build()
            done[m] = True
            print(m, round(time.time() - t, 1))
if BLOCKOUT or not done:
    import il_blockout
    il_blockout.build()
    print("blockout", round(time.time() - t0, 1))

il_scene.sea()
il_scene.islets()
il_scene.clouds()
il_scene.cameras()
il_scene.scale_reference(visible=BLOCKOUT or not done)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
tris = 0
for o in bpy.data.objects:
    if o.type == "MESH" and not o.name.startswith("COL_"):
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
print("BUILD OK objs=%d tris=%d col=%d t=%.1fs -> %s" % (len(bpy.data.objects), tris, ncol, time.time() - t0, OUT))
