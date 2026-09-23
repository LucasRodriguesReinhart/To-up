# render.py - renderiza cameras de QA do .blend salvo
# uso: blender -b lobby_forja_mineradora.blend --python render.py -- <pasta_saida> [cam ...] [--res 1280x720] [--clay]
import sys, os, bpy
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0]
cams = [a for a in argv[1:] if a.startswith("CAM_")]
res = (1280, 720)
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    res = (int(w), int(h))
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = res
if "--fast" in argv:
    sc.eevee.taa_render_samples = 8
# blockout escondido se houver arte final no lugar
if not cams:
    cams = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA")
for cn in cams:
    ob = bpy.data.objects.get(cn)
    if not ob:
        continue
    sc.camera = ob
    sc.render.filepath = os.path.join(out, cn + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDER", cn)
