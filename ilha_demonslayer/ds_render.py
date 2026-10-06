# ds_render.py - renderiza as cameras CAM_DS_* do .blend montado em JPEG
# uso: blender -b --factory-startup ilha_demonslayer.blend --python ds_render.py -- <pasta> [CAM ...] [--res 1280x720]
#      [--samples 16] [--proxies-only]
#   (modo Roblox: monte o .blend com FM_MAT_PREVIEW=roblox no build_ds e renderize esse .blend)
import sys, os
import bpy
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0]
cams = [a for a in argv[1:] if a.startswith("CAM_")]
res = (1280, 720)
samples = 16
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    res = (int(w), int(h))
if "--samples" in argv:
    samples = int(argv[argv.index("--samples") + 1])
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = res
sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = samples
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 90
for o in bpy.data.objects:                  # bonecos de escala aparecem (leitura de escala); cameras de outros: nao
    if o.name.startswith("SCALE_Dummy_Gate"):
        o.hide_render = True
if not cams:
    cams = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith("CAM_DS_"))
for cn in cams:
    ob = bpy.data.objects.get(cn)
    if not ob:
        print("RENDER camera inexistente:", cn)
        continue
    sc.camera = ob
    sc.render.filepath = os.path.join(out, cn + ".jpg")
    bpy.ops.render.render(write_still=True)
    print("RENDER", cn)
