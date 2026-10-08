# vm_render.py - renderiza as cameras CAM_VM_* do .blend montado (JPEG 960x540; a planta sai 960x912 = recorte da
# planta aprovada). Modos: previa (padrao do build) ou --roblox (FM_MAT_PREVIEW=roblox: a COR QUE O ROBLOX RECEBE,
# sem textura; Neon brilha) aplicado em memoria, sem salvar o .blend.
# uso: blender -b --factory-startup lobby_vila_medieval.blend --python vm_render.py -- <pasta> [CAM ...] [--roblox]
#      [--res 960x540] [--samples 16] [--sem-escala]
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vm_lib as VL
import bpy
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[0]
cams = [a for a in argv[1:] if a.startswith("CAM_")]
res = (960, 540)
samples = 16
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    res = (int(w), int(h))
if "--samples" in argv:
    samples = int(argv[argv.index("--samples") + 1])
if "--roblox" in argv:
    import fm_pv3
    fm_pv3.load()
    import fm_portals, fm_lib
    print("MODO roblox: %d materiais" % fm_lib.apply_preview("roblox"))
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = samples
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 90
for o in bpy.data.objects:
    if o.name.startswith("SCALE_"):
        o.hide_render = "--sem-escala" in argv
if not cams:
    cams = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith("CAM_VM_"))
for cn in cams:
    ob = bpy.data.objects.get(cn)
    if not ob:
        print("RENDER camera inexistente:", cn)
        continue
    if cn == "CAM_VM_Plan":
        sc.render.resolution_x, sc.render.resolution_y = 960, 912
    else:
        sc.render.resolution_x, sc.render.resolution_y = res
    sc.camera = ob
    sc.render.filepath = os.path.join(out, cn + ".jpg")
    bpy.ops.render.render(write_still=True)
    print("RENDER", cn)
