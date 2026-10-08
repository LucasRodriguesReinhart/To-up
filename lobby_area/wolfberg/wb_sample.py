# wb_sample.py - AMOSTRA do lobby Wolfberg para avaliacao: chao + forja + casas da praca + mobiliario + fundo,
# renderizada nas cameras da referencia. uso:
#   blender -b --factory-startup --python wb_sample.py -- <pasta_saida> [CAM ...] [--all] [--save x.blend]
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
out = argv[0] if argv else os.path.join(HERE, "renders", "sample")
cams = [a for a in argv[1:] if a.startswith("CAM_")]
ALL = "--all" in argv
save = argv[argv.index("--save") + 1] if "--save" in argv else None
os.makedirs(out, exist_ok=True)

t0 = time.time()
W.reset_scene()
W.register()
fm_lib.make_materials()
import wb_terrain
import wb_forge
import wb_town

wb_terrain.ground()
print("TERRENO %.0fs" % (time.time() - t0))
wb_terrain.backdrop()
print("FUNDO %.0fs" % (time.time() - t0))
wb_forge.build()
print("FORJA %.0fs" % (time.time() - t0))
ids = None if ALL else ("TAV", "PAD", "SE", "S1W", "S1E", "FW", "FE", "SW", "W1")
wb_town.houses(ids)
print("CASAS %.0fs" % (time.time() - t0))
wb_town.plaza_furniture()
# previa de fumaca (so render): PREVIEW_ nunca entra no export
import random as _r
_rs = _r.Random(3)
_pb = W.Build("PREVIEW_Smoke", "03_TOWN")
for (cx, cz) in L.CHIMNEYS:
    for k in range(9):
        t = k / 8.0
        _pb.sphere(W.RB(cx + _rs.uniform(-1, 1) + 6 * t, cz - 3 * t, L.CHIMNEY_TOP + 1 + 14 * t), 1.6 + 3.2 * t, "WB_Smoke", seg=7)
_pb.finish()
wb_terrain.vegetation(pines=True)
print("VILA %.0fs" % (time.time() - t0))

# orcamento
tris = 0
meshes = 0
for o in bpy.data.objects:
    if o.type == "MESH" and not o.name.startswith(("COL_", "QA_")):
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
        meshes += 1
print("TRIS %d em %d malhas" % (tris, meshes))

W.setup_render(res=(1600, 900), samples=48, sun_rot=(50, 0, -40), sun_energy=4.5, sky=(0.58, 0.74, 0.96))
sc = bpy.context.scene
try:
    sc.eevee.use_gtao = True
    sc.eevee.use_bloom = True
    sc.eevee.bloom_threshold = 1.5
    sc.eevee.bloom_intensity = 0.03
except Exception:
    pass
# nevoa leve (perspectiva aerea) pelo mundo: mist pass nao; usamos cor do ceu + fundo azulado nas montanhas
for n, (eye, tgt, lens) in L.cams().items():
    W.camera(n, eye, tgt, lens)
if save:
    bpy.ops.wm.save_as_mainfile(filepath=save)
todo = cams or ["CAM_WB_Ref", "CAM_WB_P_Spawn", "CAM_WB_P_Forja", "CAM_WB_P_Praca"]
for n in todo:
    W.render(bpy.data.objects[n], os.path.join(out, n + ".png"))
print("FIM %.0fs" % (time.time() - t0))
