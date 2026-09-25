# studio_db.py - estudio de UMA zona da Ilha 2: monta a ilha com a zona pedida em DETALHE (modulo db_<zona>) e o resto
# em blockout, renderiza as cameras da zona, roda as rotas de navegacao, confere os marcadores obrigatorios e mede o
# orcamento (tris, MeshParts estimadas, materiais novos, colisoes, luzes).
# uso:
#   blender -b --factory-startup --python studio_db.py -- <zona> <pasta_saida_ABSOLUTA> [--cams CAM_A,CAM_B]
#           [--res 960x540] [--save] [--no-render] [--samples 16] [--all-detail]
# zonas: terrain mining entrance capsule village towers summon water exit dressing
#   --all-detail: as OUTRAS zonas prontas tambem entram em detalhe (para o vestir/integracao)
import sys, os, time, math, re, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db_lib as DL
import bpy
import fm_lib
import db_layout as L
import db_scene
import db_core
import db_blockout
import build_db as B

ZONE_CAMS = {
    "terrain": ["CAM_DB_Ref_Main", "CAM_DB_Front", "CAM_DB_Left", "CAM_DB_Right", "CAM_DB_Back", "CAM_DB_Ref_Side"],
    "mining": ["CAM_DB_Mining", "CAM_DB_PlayerHeight_Mining", "CAM_DB_Ref_Main"],
    "entrance": ["CAM_DB_Entry", "CAM_DB_PlayerHeight_Entry", "CAM_DB_Ref_Front"],
    "capsule": ["CAM_DB_Capsule", "CAM_DB_Ref_Capsule", "CAM_DB_CapsuleInterior"],
    "village": ["CAM_DB_Ref_Village", "CAM_DB_Capsule", "CAM_DB_Ref_Main"],
    "towers": ["CAM_DB_Ref_Main", "CAM_DB_Back", "CAM_DB_Ref_Side"],
    "summon": ["CAM_DB_Summon", "CAM_DB_Ref_Summon", "CAM_DB_PlayerHeight_Summon"],
    "water": ["CAM_DB_Ref_Environment", "CAM_DB_Front", "CAM_DB_Ref_Main"],
    "exit": ["CAM_DB_ShadowGate", "CAM_DB_PlayerHeight_ShadowGate", "CAM_DB_Right"],
    "dressing": ["CAM_DB_Ref_Main", "CAM_DB_Entry", "CAM_DB_Mining", "CAM_DB_Ref_Village"],
}
ZONE_MARKERS = {
    "summon": ["SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition"],
    "capsule": ["NPC_Capsule", "PLAYER_INTERACT_Capsule"],
    "village": ["NPC_Market", "PLAYER_INTERACT_Market", "NPC_Workshop", "PLAYER_INTERACT_Workshop"],
    "exit": ["ISLAND_EXIT_DragonBall", "ISLAND_NEXT_ANCHOR_ShadowGarden", "GATE_ShadowGarden"],
}
# orcamento por zona: (tris, MeshParts estimadas, materiais NOVOS, colisoes COL_, luzes de dia)
BUDGET = {
    "terrain": (95000, 120, 6, 60, 0), "mining": (35000, 45, 4, 60, 2), "entrance": (35000, 45, 5, 60, 3),
    "capsule": (60000, 80, 7, 170, 6), "village": (55000, 85, 6, 150, 4), "towers": (35000, 55, 5, 90, 3),
    "summon": (40000, 50, 5, 80, 4), "water": (20000, 30, 3, 20, 0), "exit": (25000, 35, 4, 60, 2),
    "dressing": (50000, 90, 6, 90, 12),
}


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
    all_detail = "--all-detail" in argv
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    DL.reset_scene()
    fm_lib.make_materials()
    base_mats = set(fm_lib.MATS.keys())
    db_scene.setup(res=res, samples=samples)
    db_core.build()
    others = [z for z in B.ZONE_MODULES if z != zone and all_detail and B.zone_ready(z)]
    db_blockout.build(skip={zone} | set(others))
    for z in others:
        for m in B.ZONE_MODULES[z]:
            try:
                importlib.import_module(m).build()
            except Exception:
                import traceback
                traceback.print_exc()
                print("STUDIO ERRO no modulo vizinho %s" % m)
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
    fm_lib.make_materials()
    db_scene.tone_emissives()
    db_scene.sea()
    db_scene.islets()
    db_scene.clouds()
    db_scene.cameras()
    db_scene.scale_reference(visible=True)
    for mod in mods:
        for n, v in getattr(mod, "CAMS", {}).items():
            DL.camera(n, v[0], v[1], v[2] if len(v) > 2 else 20)
    bpy.context.view_layer.update()

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
    prefix_ok = [o.name for o in meshes if not o.name.startswith(("DB_", "VFX_", "GATE_", "SCALE_"))]
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
    print("STUDIO tecnico: nomes_ruins=%s prefixo_fora_do_padrao=%s sem_material=%s degeneradas=%d" % (
        bad_names[:8], prefix_ok[:8], nomat[:8], degen))
    names = {o.name for o in bpy.data.objects}
    req = ZONE_MARKERS.get(zone, [])
    miss = [n for n in req if n not in names]
    print("STUDIO marcadores obrigatorios: %d/%d %s" % (len(req) - len(miss), len(req),
                                                         ("FALTAM " + str(miss)) if miss else "OK"))
    import db_qa
    db_qa.nav()
    if "--save" in argv:
        p = os.path.join(HERE, "_studio", "studio_%s.blend" % zone)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=p, compress=True)
        print("STUDIO salvo", p)
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
