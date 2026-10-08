# build_wb.py - monta o lobby WOLFBERG inteiro no Blender (chao, fundo, forja, casas, praca, loja, mural, patio dos
# portais, portao + ponte, vegetacao), previa do Ignis golem (FBX, PREVIEW_), cameras; salva o .blend e renderiza.
# uso: blender -b --factory-startup --python build_wb.py -- [--out <pasta_renders>] [--blend <arquivo.blend>]
#                                                         [--cams CAM_A,CAM_B | --all-cams] [--no-render] [--skip mod,mod]
import importlib
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_lib as W
import bpy
import fm_lib
import wb_layout as L
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


OUT = opt("--out", os.path.join(HERE, "renders", "full"))
BLEND = opt("--blend", os.path.join(HERE, "lobby_wolfberg.blend"))
SKIP = set((opt("--skip", "") or "").split(",")) - {""}
IGNIS_FBX = os.path.join(W.ROOT, "output", "ignis_golem_20261007", "export", "final", "IGNIS_GOLEM_417ec4.fbx")
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
W.reset_scene()
W.register()
fm_lib.make_materials()
report = []


def step(name, fn):
    if name in SKIP:
        report.append((name, "pulado"))
        return
    t = time.time()
    try:
        fn()
        report.append((name, "ok %.0fs" % (time.time() - t)))
    except Exception as e:
        traceback.print_exc()
        report.append((name, "FALHOU: %s" % e))


def mod_build(mname):
    def f():
        m = importlib.import_module(mname)
        m.build()
    return f


import wb_terrain
import wb_forge
import wb_town

step("terrain", wb_terrain.ground)
step("backdrop", wb_terrain.backdrop)
step("forge", wb_forge.build)
step("houses", lambda: wb_town.houses())
step("plaza", wb_town.plaza_furniture)
for m in ("wb_shop", "wb_rank", "wb_court", "wb_exit"):
    step(m, mod_build(m))
step("vegetation", lambda: wb_terrain.vegetation())


def ignis_preview():
    if not os.path.exists(IGNIS_FBX):
        raise FileNotFoundError(IGNIS_FBX)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=IGNIS_FBX, use_image_search=True)
    new = [o for o in bpy.data.objects if o not in before]
    coll = W.collection("00_REFERENCE")
    off = W.RB(L.IGNIS_ROOT[0], L.IGNIS_ROOT[2], L.IGNIS_ROOT[1])
    for o in new:
        if o.parent is None:
            o.location = o.location + off
        o.name = "PREVIEW_Ignis_" + o.name
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        if o.type == "MESH":
            for p in o.data.polygons:
                p.use_smooth = False
    print("PREVIEW Ignis: %d objetos em %s" % (len(new), tuple(round(v, 1) for v in off)))


step("ignis_preview", ignis_preview)


def smoke_preview():
    import random
    rs = random.Random(3)
    pb = W.Build("PREVIEW_Smoke", "00_REFERENCE")
    for (cx, cz) in L.CHIMNEYS:
        for k in range(9):
            t = k / 8.0
            pb.sphere(W.RB(cx + rs.uniform(-1, 1) + 6 * t, cz - 3 * t, L.CHIMNEY_TOP + 1 + 14 * t), 1.6 + 3.2 * t,
                      "WB_Smoke", seg=7)
    pb.finish()


step("smoke_preview", smoke_preview)

# orcamento por prefixo
tris = {}
meshes = {}
for o in bpy.data.objects:
    if o.type != "MESH" or o.name.startswith(("COL_", "QA_", "PREVIEW_", "CAM_", "TMP_")):
        continue
    pre = o.name.split("_")[0] + "_" + (o.name.split("_")[1] if "_" in o.name else "")
    t = sum(len(p.vertices) - 2 for p in o.data.polygons)
    tris[pre] = tris.get(pre, 0) + t
    meshes[pre] = meshes.get(pre, 0) + 1
print("ORCAMENTO (tris / malhas antes do export):")
tot = 0
for k in sorted(tris):
    print("  %-14s %8d  %4d" % (k, tris[k], meshes[k]))
    tot += tris[k]
print("  TOTAL          %8d  %4d" % (tot, sum(meshes.values())))
for n, s in report:
    print("ETAPA %-14s %s" % (n, s))

W.setup_render(res=(1600, 900), samples=48, sun_rot=(50, 0, -40), sun_energy=4.5, sky=(0.58, 0.74, 0.96))
for n, (eye, tgt, lens) in L.cams().items():
    W.camera(n, eye, tgt, lens)
for mname in ("wb_shop", "wb_rank", "wb_court", "wb_exit"):
    try:
        m = sys.modules.get(mname) or importlib.import_module(mname)
        for (n, eye, tgt, lens) in getattr(m, "CAMS", []):
            W.camera(n, eye, tgt, lens)
    except Exception:
        pass
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("BLEND salvo:", BLEND, "%.0fs" % (time.time() - t0))
if "--no-render" not in argv:
    if "--all-cams" in argv:
        todo = [o.name for o in bpy.data.objects if o.type == "CAMERA"]
    else:
        todo = (opt("--cams") or "CAM_WB_Ref,CAM_WB_P_Spawn,CAM_WB_Air_Sul").split(",")
    for n in todo:
        if n in bpy.data.objects:
            W.render(bpy.data.objects[n], os.path.join(OUT, n + ".png"))
print("FIM %.0fs" % (time.time() - t0))
