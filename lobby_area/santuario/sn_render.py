# sn_render.py - renderiza cameras de um .blend montado pelo sn_build (sem remontar)
# uso: blender -b renders/build/build.blend --python sn_render.py -- <pasta> CAM_A CAM_B ... [--res 1600x900]
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
import sn_lib as SL

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
os.makedirs(out, exist_ok=True)
cams = [a for a in argv[1:] if a.startswith("CAM_")] or sorted(o.name for o in bpy.data.objects if o.name.startswith("CAM_SN_"))
res = (1600, 900)
if "--res" in argv:
    res = tuple(int(v) for v in argv[argv.index("--res") + 1].split("x"))
SL.register()
SL.setup_render(res=res, samples=64)
for n in cams:
    if n in bpy.data.objects:
        SL.render(bpy.data.objects[n], os.path.join(out, n + ".png"))
        print("RENDER", n)
