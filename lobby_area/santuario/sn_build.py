# sn_build.py - MONTAGEM do lobby Santuario do Deus-Ferreiro no Blender (todas as partes + pintura assada + previa)
# uso: blender -b --factory-startup --python sn_build.py -- <pasta_renders> [--mods a,b,...] [--rebake g1,g2|all]
#        [--cams CAM_A,CAM_B] [--save x.blend] [--no-render] [--no-ignis] [--no-bake] [--res 1600x900]
# modulos: terrain, relief, veg, hero, portals, shop, rank, south, ruins (padrao: todos os que existem)
# --rebake: grupos cuja pintura e reassada; os demais reaproveitam o PNG ja assado (UV deterministico).
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
import sn_lib as SL
import fm_lib

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv and not argv[0].startswith("--") else os.path.join(HERE, "renders", "build")


def opt(name, default=None):
    if name in argv:
        i = argv.index(name)
        return argv[i + 1] if i + 1 < len(argv) else default
    return default


ALL = ["terrain", "relief", "veg", "hero", "portals", "shop", "rank", "south", "ruins"]
MODS = (opt("--mods") or ",".join(ALL)).split(",")
REBAKE = (opt("--rebake") or "").split(",")
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
SL.reset_scene()
SL.register()
fm_lib.make_materials()
import sn_layout as L
import sn_paint as P
P.build_paints()

# grupo do Build -> (atlas, px por stud)
BAKE = [("WB_Frg_Anvil", "Anvil", 6.0), ("WB_Frg_Hammer", "Hammer", 8.0), ("WB_Frg_Hall", "Hall", 8.0),
        ("WB_Town_Plaza", "Plaza", 8.0), ("WB_Court_Dais", "Dais", 7.0), ("WB_Shop_Temple", "Shop", 8.0),
        ("WB_Shop_Inside", "ShopIn", 9.0), ("WB_Rank_Tablets", "Rank", 7.0), ("WB_Exit_Spawn", "Spawn", 7.0),
        ("WB_Exit_Avenue", "Avenue", 6.0), ("WB_Exit_Gate", "Gate", 7.0), ("WB_Exit_Bridge", "Bridge", 6.0),
        ("WB_Prop_Ruins", "Ruins", 6.0), ("WB_Ter_Ground", "Ground", 3.0), ("WB_Ter_Shore", "Shore", 3.0),
        ("WB_Veg_Tufts", "Tufts", 5.0)]


def has(m):
    return m in MODS


def mod(name):
    try:
        return __import__(name)
    except ImportError as e:
        print("MODULO AUSENTE", name, e)
        return None


if has("terrain"):
    g = mod("sn_ground")
    if g:
        g.build()
    else:
        b = SL.Build("WB_Ter_Test", "02_TERRAIN")
        pl = [(x, -z) for (x, z) in L.PLATEAU]
        b.prism(pl, L.PLATEAU_BOTTOM, L.Y_GRASS - 0.6, "WB_Rock")
        b.prism([(x * 1.01, y * 1.01) for (x, y) in pl], L.Y_GRASS - 0.6, L.Y_GRASS, "WB_Grass")
        b.cyl((0, 0, L.Y_WATER - 1.0), (0, 0, L.Y_WATER), L.LAKE_R, "WB_Water", seg=48)
        b.finish()
if has("relief"):
    import sn_relief
    sn_relief.build()
if has("hero"):
    import sn_hero as H
    H.anvil()
    H.hammer()
    H.forge()
    H.plaza()
if has("portals"):
    import sn_portals
    sn_portals.build()
for nm in ("shop", "rank", "south", "ruins"):
    if has(nm):
        m = mod("sn_" + nm)
        if m:
            m.build()
if has("veg"):
    import sn_veg as VG
    VG.build_kit(reuse="veg" not in REBAKE and "all" not in REBAKE)
    sp = mod("sn_vegplan")
    spots = sp.spots() if sp else {}
    for nm, s in spots.items():
        VG.place(nm, s)
    VG.hide_kit()
    import sn_fx
    sn_fx.build(spots)
print("MONTADO %.0fs" % (time.time() - t0))
if "--no-bake" not in argv:
    for pre, at, pps in BAKE:
        if any(o.name.startswith(pre + "__") for o in bpy.data.objects):
            P.bake_group(pre, at, pps=pps, samples=16, reuse=not ("all" in REBAKE or pre in REBAKE or at in REBAKE))
print("ASSADO %.0fs" % (time.time() - t0))
if "--no-ignis" not in argv:
    fbx = os.path.join(SL.W.ROOT, "output", "ignis_golem_20261007", "export", "final", "IGNIS_GOLEM_417ec4.fbx")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx, use_image_search=True)
    off = SL.RB(L.IGNIS_ROOT[0], L.IGNIS_ROOT[2], L.IGNIS_ROOT[1])
    for o in bpy.data.objects:
        if o not in before:
            if o.parent is None:
                o.location = o.location + off
            o.name = "PREVIEW_Ignis_" + o.name
tris = {}
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.startswith("WB_") and o.users_collection:
        k = o.name.split("__")[0]
        tris[k] = tris.get(k, 0) + sum(len(p.vertices) - 2 for p in o.data.polygons)
print("TRIS", sum(tris.values()), sorted(tris.items(), key=lambda kv: -kv[1])[:25])
res = [int(v) for v in (opt("--res") or "1600x900").split("x")]
SL.setup_render(res=tuple(res), samples=64)
for n, (e, t, lens) in L.cams().items():
    SL.camera(n, e, t, lens)
if opt("--save"):
    bpy.ops.wm.save_as_mainfile(filepath=opt("--save"))
if "--no-render" not in argv:
    cams = (opt("--cams") or "CAM_SN_Spawn,CAM_SN_Hero").split(",")
    for n in cams:
        if n in bpy.data.objects:
            SL.render(bpy.data.objects[n], os.path.join(OUT, n + ".png"))
print("FIM %.0fs" % (time.time() - t0))
