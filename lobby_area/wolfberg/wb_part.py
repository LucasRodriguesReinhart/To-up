# wb_part.py - harness de teste de UM componente do lobby Wolfberg: monta o chao (opcional) + o modulo pedido e
# renderiza as cameras. uso:
#   blender -b --factory-startup --python wb_part.py -- <modulo> <pasta_saida> [CAM ...] [--no-ground] [--town]
#                                                       [--save x.blend]
# O modulo precisa ter build() (constroi tudo) e pode ter CAMS = [(nome, (x, y, z) olho Roblox, (x, y, z) alvo, lente)].
# Sem CAM na linha de comando: renderiza as CAMS do modulo (ou CAM_WB_Ref se nao houver).
import importlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_lib as W
import bpy
import fm_lib
import wb_layout as L

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
mod_name, out = argv[0], argv[1]
cams = [a for a in argv[2:] if a.startswith("CAM_")]
save = argv[argv.index("--save") + 1] if "--save" in argv else None
os.makedirs(out, exist_ok=True)
t0 = time.time()
W.reset_scene()
W.register()
fm_lib.make_materials()
if "--no-ground" not in argv:
    import wb_terrain
    wb_terrain.ground()
    wb_terrain.backdrop()
if "--town" in argv:
    import wb_forge
    import wb_town
    import wb_terrain
    wb_forge.build()
    wb_town.houses()
    wb_town.plaza_furniture()
    wb_terrain.vegetation()
mod = importlib.import_module(mod_name)
objs = mod.build()
tris = 0
for o in bpy.data.objects:
    if o.type == "MESH" and not o.name.startswith(("COL_", "QA_", "PREVIEW_")) and o.name.startswith(getattr(mod, "PREFIX", "WB_")):
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
print("PARTE %s: %d tris nos objetos %s*, %.0fs" % (mod_name, tris, getattr(mod, "PREFIX", "WB_"), time.time() - t0))
W.setup_render(res=(1600, 900), samples=48, sun_rot=(50, 0, -40), sun_energy=4.5, sky=(0.58, 0.74, 0.96))
for n, (eye, tgt, lens) in L.cams().items():
    W.camera(n, eye, tgt, lens)
for (n, eye, tgt, lens) in getattr(mod, "CAMS", []):
    W.camera(n, eye, tgt, lens)
if save:
    bpy.ops.wm.save_as_mainfile(filepath=save)
todo = cams or [c[0] for c in getattr(mod, "CAMS", [])] or ["CAM_WB_Ref"]
for n in todo:
    W.render(bpy.data.objects[n], os.path.join(out, n + ".png"))
print("FIM %.0fs" % (time.time() - t0))
