# studio.py - estudio de UMA zona: monta a ilha com a zona pedida em DETALHE (modulo il_<zona>) e o resto em
# blockout, renderiza as cameras da zona, roda as 14 rotas de navegacao, confere os marcadores obrigatorios e mede
# o orcamento (tris, MeshParts estimadas, materiais novos, colisoes, luzes).
# uso:
#   blender -b --factory-startup --python studio.py -- <zona> <pasta_saida_ABSOLUTA> [--cams CAM_A,CAM_B]
#           [--res 960x540] [--save] [--no-render] [--samples 16]
# zonas: terrain mining entrance village houses summon water exit gates dressing
import sys, os, time, math, re, importlib, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy
import fm_lib
import il_layout as L
import il_scene
import il_core
import il_blockout
import build_ilha as B

ZONE_CAMS = {
    "terrain": ["CAM_Ref14", "CAM_Ref16", "CAM_Front", "CAM_Left", "CAM_Right", "CAM_Back"],
    "mining": ["CAM_Mining", "CAM_Center", "CAM_Ref18"],
    "entrance": ["CAM_Entry", "CAM_Ref14"],
    "village": ["CAM_Village", "CAM_Center", "CAM_Ref14"],
    "houses": ["CAM_Ref15", "CAM_Right", "CAM_Village"],
    "summon": ["CAM_Summon", "CAM_Ref15"],
    "water": ["CAM_Right", "CAM_Ref16", "CAM_Back"],
    "exit": ["CAM_NextBridge", "CAM_DB_Gate", "CAM_Ref16"],
    "gate_db": ["CAM_DB_Gate", "CAM_NextBridge"],
    "gates": [],
    "dressing": ["CAM_Ref14", "CAM_Ref15", "CAM_Entry", "CAM_Center", "CAM_Village"],
}
ZONE_MARKERS = {
    "summon": ["SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition"],
    "exit": ["ISLAND_EXIT_Naruto", "ISLAND_NEXT_ANCHOR"],
    "gate_db": ["GATE_DB", "GATE_DB_INTERACT", "GATE_DB_LOCKED", "GATE_DB_EXIT", "PURCHASE_UI_ANCHOR_DB",
                "GATE_DB_Barrier", "GATE_DB_Lock", "GATE_DB_OpenFX"],
    "village": ["NPC_MainHall", "PLAYER_INTERACT_MainHall", "NPC_WeaponShop", "PLAYER_INTERACT_WeaponShop",
                "NPC_Ramen", "PLAYER_INTERACT_Ramen"],
    "houses": ["NPC_Mill", "PLAYER_INTERACT_Mill"],
    "gates": [p % k for k in ("ShadowGarden", "DemonSlayer", "OnePiece", "OnePunchMan")
              for p in ("GATE_%s", "GATE_%s_INTERACT", "GATE_%s_LOCKED", "GATE_%s_EXIT", "PURCHASE_UI_ANCHOR_%s",
                        "GATE_%s_Barrier", "GATE_%s_Lock", "GATE_%s_OpenFX")],
}
# orcamento por zona: (tris, MeshParts estimadas, materiais NOVOS, colisoes COL_, luzes de dia)
BUDGET = {
    "terrain": (100000, 120, 6, 420, 0), "mining": (45000, 65, 5, 130, 4), "entrance": (30000, 40, 4, 70, 4),
    "village": (55000, 80, 6, 160, 6), "houses": (45000, 70, 5, 130, 4), "summon": (35000, 45, 6, 70, 4),
    "water": (22000, 35, 4, 50, 0), "exit": (20000, 30, 4, 70, 2), "gate_db": (24000, 32, 6, 30, 3),
    "gates": (100000, 140, 12, 120, 0),
    "dressing": (55000, 90, 6, 90, 18),
}
BASE_MATS = None


def est_meshparts(ob):
    """estimativa do export: 1 MeshPart por material usado (variante), + fatias de 18k tris, + celulas de 128 se o
    objeto passa de 160 studs em X/Y"""
    me = ob.data
    per = {}
    for p in me.polygons:
        per[p.material_index] = per.get(p.material_index, 0) + len(p.vertices) - 2
    n = sum(max(1, math.ceil(t / 18000.0)) for t in per.values())
    step = max(1, len(me.vertices) // 400)
    xs = [ob.matrix_world @ me.vertices[i].co for i in range(0, len(me.vertices), step)]
    if xs:
        sx = max(v.x for v in xs) - min(v.x for v in xs)
        sy = max(v.y for v in xs) - min(v.y for v in xs)
        if max(sx, sy) > 160:
            n = max(n, int(math.ceil(sx / 128.0) * math.ceil(sy / 128.0) * 0.6))
    return n


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    zone, out = argv[0], argv[1]
    res = (960, 540)
    cams = None
    samples = 16
    for i, a in enumerate(argv):
        if a == "--res":
            w, h = argv[i + 1].split("x")
            res = (int(w), int(h))
        if a == "--cams":
            cams = [c for c in argv[i + 1].split(",") if c]
        if a == "--samples":
            samples = int(argv[i + 1])
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    IL.reset_scene()
    fm_lib.make_materials()
    base_mats = set(fm_lib.MATS.keys())
    il_scene.setup(res=res, samples=samples)
    il_core.build()
    il_blockout.build(skip={zone})            # resto da ilha ANTES (o modulo pode testar contra a geometria dele)
    before = {o.name for o in bpy.data.objects}
    mods = []
    for m in B.ZONE_MODULES[zone]:
        if os.path.exists(os.path.join(HERE, m + ".py")):
            t = time.time()
            try:
                mod = importlib.import_module(m)
                mod.build()
                mods.append(mod)
                print("STUDIO modulo %s %.1fs" % (m, time.time() - t))
            except Exception:
                import traceback
                traceback.print_exc()
                print("STUDIO ERRO no modulo %s (veja o traceback acima)" % m)
        else:
            print("STUDIO AVISO: %s.py nao existe (zona em blockout)" % m)
    made = [o for o in bpy.data.objects if o.name not in before]
    il_scene.sea()
    il_scene.islets()
    il_scene.cameras()
    il_scene.scale_reference(visible=True)
    for mod in mods:
        for n, v in getattr(mod, "CAMS", {}).items():
            IL.camera(n, v[0], v[1], v[2] if len(v) > 2 else 20)
    bpy.context.view_layer.update()

    # ---- metricas da zona
    meshes = [o for o in made if o.type == "MESH" and not o.name.startswith("COL_")]
    cols = [o for o in made if o.name.startswith("COL_")]
    lights = [o for o in made if o.type == "LIGHT"]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    mats = set()
    for o in meshes:
        for m in o.data.materials:
            if m:
                mats.add(m.name)
    new_mats = sorted(m for m in mats if m not in base_mats and fm_lib.family_of(m) not in base_mats)
    mp = sum(est_meshparts(o) for o in meshes)
    b = BUDGET[zone]
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh|Empty)(\.\d+)?$")
    bad_names = [o.name for o in made if gen.match(o.name) or re.match(r".+\.\d{3}$", o.name)]
    nomat = [o.name for o in meshes if not o.data.materials or any(m is None for m in o.data.materials)]
    degen = sum(1 for o in meshes for p in o.data.polygons if p.area < 1e-6)
    heavy = sorted(((sum(len(p.vertices) - 2 for p in o.data.polygons), o.name) for o in meshes), reverse=True)[:6]
    def flag(v, lim):
        return "OK" if v <= lim else "ESTOUROU"
    print("STUDIO METRICAS zona=%s objetos=%d malhas=%d" % (zone, len(made), len(meshes)))
    print("STUDIO tris=%d/%d %s | MeshParts~%d/%d %s | materiais_novos=%d/%d %s %s" % (
        tris, b[0], flag(tris, b[0]), mp, b[1], flag(mp, b[1]), len(new_mats), b[2], flag(len(new_mats), b[2]),
        new_mats))
    print("STUDIO colisoes=%d/%d %s | luzes=%d (de dia <= %d)" % (len(cols), b[3], flag(len(cols), b[3]), len(lights),
                                                                  b[4]))
    print("STUDIO maiores:", heavy)
    print("STUDIO tecnico: nomes_ruins=%s sem_material=%s degeneradas=%d" % (bad_names[:8], nomat[:8], degen))
    names = {o.name for o in bpy.data.objects}
    req = ZONE_MARKERS.get(zone, [])
    miss = [n for n in req if n not in names]
    print("STUDIO marcadores obrigatorios: %d/%d %s" % (len(req) - len(miss), len(req), ("FALTAM " + str(miss)) if miss else "OK"))

    # ---- navegacao (as 14 rotas da ilha)
    import il_qa
    il_qa.nav()

    if "--save" in argv:
        os.makedirs(os.path.join(HERE, "_studio"), exist_ok=True)
        p = os.path.join(HERE, "_studio", "studio_%s.blend" % zone)
        bpy.ops.wm.save_as_mainfile(filepath=p, compress=True)
        print("STUDIO salvo", p)

    # ---- render
    if "--no-render" not in argv:
        sc = bpy.context.scene
        sc.render.image_settings.file_format = "JPEG"
        sc.render.image_settings.quality = 88
        want = cams or (ZONE_CAMS.get(zone, []) + [n for mod in mods for n in getattr(mod, "CAMS", {})])
        for cn in want:
            ob = bpy.data.objects.get(cn)
            if not ob:
                print("STUDIO camera inexistente:", cn)
                continue
            sc.camera = ob
            sc.render.filepath = os.path.join(out, cn + ".jpg")
            bpy.ops.render.render(write_still=True)
            print("STUDIO RENDER", sc.render.filepath)
    print("STUDIO FIM %.1fs" % (time.time() - t0))


main()
