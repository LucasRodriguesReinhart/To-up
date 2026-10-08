# wb_render.py - renderiza cameras de um .blend ja montado (build_wb) sem reconstruir nada.
# uso: blender -b --factory-startup lobby_wolfberg.blend --python wb_render.py -- <pasta_saida> [CAM ...] [--all]
#      [--res 1600x900] [--samples 48]
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
import wb_lib as W

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0]
cams = [a for a in argv[1:] if a.startswith("CAM_")]
res = (1600, 900)
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    res = (int(w), int(h))
samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 48
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = res
try:
    sc.eevee.taa_render_samples = samples
except Exception:
    pass
if "--all" in argv:
    cams = [o.name for o in bpy.data.objects if o.type == "CAMERA"]
for n in cams:
    if n in bpy.data.objects:
        W.render(bpy.data.objects[n], os.path.join(out, n + ".png"))
    else:
        print("CAMERA NAO EXISTE:", n)
print("RENDER FIM")
