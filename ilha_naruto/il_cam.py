# il_cam.py - renderiza vistas avulsas (inspecao) sem mexer no .blend
# uso: blender -b ilha_naruto.blend --python il_cam.py -- <pasta> nome:x,y,z:tx,ty,tz[:lente] [nome2:...] [--res 1280x720]
import sys, os, bpy
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
res = (1280, 720)
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    res = (int(w), int(h))
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = res
sc.eevee.taa_render_samples = 12
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 88
for spec in argv[1:]:
    if spec.startswith("--") or ":" not in spec:
        continue
    parts = spec.split(":")
    name = parts[0]
    loc = Vector([float(v) for v in parts[1].split(",")])
    tgt = Vector([float(v) for v in parts[2].split(",")])
    lens = float(parts[3]) if len(parts) > 3 else 20.0
    cd = bpy.data.cameras.new("tmp_" + name)
    cd.lens = lens
    cd.clip_end = 4000
    ob = bpy.data.objects.new("tmp_" + name, cd)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    sc.camera = ob
    sc.render.filepath = os.path.join(out, name + ".jpg")
    bpy.ops.render.render(write_still=True)
    print("CAM", sc.render.filepath)
