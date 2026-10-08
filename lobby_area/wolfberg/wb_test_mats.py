# wb_test_mats.py - teste dos materiais WB: um bloco por material, com textura, renderizado em EEVEE
# uso: blender -b --factory-startup --python wb_test_mats.py -- <pasta_saida>
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_lib as W
import bpy
import fm_lib

out = sys.argv[sys.argv.index("--") + 1]
W.reset_scene()
W.register()
fm_lib.make_materials()
names = [k for k in W.WBMATS]
b = W.Build("WB_Test", "03_TOWN")
cols = 7
for i, m in enumerate(names):
    x = (i % cols) * 7.0
    y = -(i // cols) * 7.0
    b.box((x, y, 2.5), (5.0, 5.0, 5.0), m, bevel=0.15)
    b.cyl((x + 3.2, y + 3.2, 0), (x + 3.2, y + 3.2, 4.0), 0.6, m, seg=12)
b.slab([(-6, 6), (48, 6), (48, -36), (-6, -36)], 0.0, 1.0, "WB_Cobble")
b.finish()
W.setup_render(res=(1600, 1000))
cam = W.camera("CAM_T", (20.0, 48.0, 36.0), (20.0, 2.0, -12.0), 40)
W.render(cam, os.path.join(out, "mats_test.png"))
cam2 = W.camera("CAM_T2", (6.0, 10.0, 12.0), (6.0, 3.0, 0.0), 45)
W.render(cam2, os.path.join(out, "mats_close.png"))
print("MATS", len(names))
