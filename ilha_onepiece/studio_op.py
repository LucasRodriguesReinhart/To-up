# studio_op.py - estudio de UMA zona da Ilha 5 (ONE PIECE / WANO): monta a ilha com a zona pedida em DETALHE (modulo
# op_<zona>) e o resto em blockout, renderiza as cameras da zona, roda as rotas de navegacao, confere os marcadores
# obrigatorios e mede o orcamento (tris, MeshParts estimadas, materiais novos, colisoes, luzes).
# uso:
#   blender -b --factory-startup --python studio_op.py -- <zona> <pasta_saida_ABSOLUTA> [--cams CAM_A,CAM_B]
#           [--res 960x540] [--save] [--no-render] [--samples 16] [--all-detail]
# zonas: terrain entry capital plaza castle tree summon harbor ship water exit landmarks dressing
# M1: nenhuma zona tem modulo -> a zona pedida e medida em BLOCKOUT.
import sys, os, time, math, re, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import op_lib as DL
import bpy
import fm_lib
import op_layout as L

ZONE_CAMS = {
    "terrain": ["CAM_OP_Ref_01", "CAM_OP_Front", "CAM_OP_Left", "CAM_OP_Right", "CAM_OP_Back", "CAM_OP_BirdEye"],
    "entry": ["CAM_OP_Entry", "CAM_OP_PlayerHeight_Entry", "CAM_OP_Ref_01"],
    "capital": ["CAM_OP_PlayerHeight_Street", "CAM_OP_Plaza", "CAM_OP_Ref_01"],
    "plaza": ["CAM_OP_Plaza", "CAM_OP_PlayerHeight_Plaza", "CAM_OP_BirdEye"],
    "castle": ["CAM_OP_Castle", "CAM_OP_PlayerHeight_Castle", "CAM_OP_Ref_02"],
    "tree": ["CAM_OP_Tree", "CAM_OP_Ref_02", "CAM_OP_PlayerHeight_Plaza"],
    "summon": ["CAM_OP_Summon", "CAM_OP_PlayerHeight_Summon"],
    "harbor": ["CAM_OP_Harbor", "CAM_OP_PlayerHeight_Harbor"],
    "ship": ["CAM_OP_Harbor", "CAM_OP_PlayerHeight_Harbor"],
    "water": ["CAM_OP_Ref_01", "CAM_OP_Castle", "CAM_OP_Left"],
    "exit": ["CAM_OP_Exit", "CAM_OP_PlayerHeight_Exit", "CAM_OP_Right"],
    "landmarks": ["CAM_OP_Skull", "CAM_OP_Right", "CAM_OP_Ref_01"],
    "dressing": ["CAM_OP_Ref_01", "CAM_OP_PlayerHeight_Entry", "CAM_OP_PlayerHeight_Street", "CAM_OP_PlayerHeight_Plaza"],
}
ZONE_MARKERS = {
    "summon": ["SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition"],
    "exit": ["ISLAND_EXIT_OnePiece", "ISLAND_NEXT_ANCHOR_OnePunchMan", "GATE_OnePunchMan", "COL_OPAnchorGuard_001"],
    "plaza": ["MiningZone_OnePiece", "GP_Block_01"],
    "entry": ["WORLD_FROM_PREV", "WORLD_ENTRY_OnePiece"],
    "water": ["WATER_Sea", "WATER_Basin", "WATER_CanalE", "WATER_CanalW", "FX_Fall_Castle_Lip", "FX_Fall_E_Lip",
              "FX_Fall_W_Lip", "VFX_OP_Wheel"],
    "tree": ["FX_Petals_Tree"],
}
# orcamento por zona (PLANO_OP secao 9): (tris, MeshParts estimadas, materiais NOVOS, colisoes COL_, luzes de dia)
# total da ilha: <= 620k tris e <= 650 MeshParts estaticos (+ reserva VFX 15k / 30), materiais <= 110, colisoes <= 1300,
# luzes de dia <= 36 (+ NightOnly)
BUDGET = {
    "terrain": (100000, 75, 8, 820, 0), "entry": (30000, 32, 4, 30, 2), "capital": (230000, 140, 10, 150, 12),
    "plaza": (31500, 33, 3, 50, 0), "castle": (70000, 55, 8, 60, 4), "tree": (40000, 30, 4, 6, 0),
    "summon": (34000, 40, 5, 60, 4), "harbor": (35000, 40, 5, 40, 2), "ship": (18000, 16, 4, 10, 0),
    "water": (10000, 16, 3, 10, 0), "exit": (18000, 24, 3, 30, 2), "landmarks": (14000, 14, 4, 6, 0),
    "dressing": (70000, 80, 8, 80, 12),
}
# M4 op_plaza (acrescimo pontual): plaza 20k/24 -> 31,5k/33 (= teto do lead 34k / 36 MeshParts no export, sem os 8%) e
# colisoes 20 -> 50 (mureta + COL_OP_Prop* da borda: postes, estandartes, bancos, toro)
# donos do export (prefixo -> dono), iguais ao export_op.ER.OWNERS
OWNERS = [("OP_Ter_", "terrain"), ("OP_Ent_", "entry"), ("OP_Cap_", "capital"), ("OP_Plz_", "plaza"),
          ("OP_Cas_", "castle"), ("OP_Tree_", "tree"), ("OP_Port_", "harbor"), ("OP_Ship_", "ship"),
          ("OP_Sum_", "summon"), ("OP_Exit_", "exit"), ("GATE_", "gate_opm"), ("OP_Lmk_", "landmarks"),
          ("OP_Water_", "water"), ("VFX_", "vfx"), ("OP_Veg_", "vegetation"), ("OP_Prop_", "props")]


def owner_of(name):
    for p, o in OWNERS:
        if name.startswith(p):
            return o
    return "?"


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


ZONE_PREFIX = {"terrain": ("OP_Ter_",), "entry": ("OP_Ent_", "COL_OP_Ent"), "capital": ("OP_Cap_", "COL_OP_Cap"),
               "plaza": ("OP_Plz_", "COL_OP_Prop"), "castle": ("OP_Cas_", "COL_OP_Cas"), "tree": ("OP_Tree_", "COL_OP_Tree"),
               "summon": ("OP_Sum_", "VFX_OPSUM_", "COL_OPSum", "COL_OP_Sum"), "harbor": ("OP_Port_", "COL_OP_Port"),
               "ship": ("OP_Ship_", "COL_OP_Ship"), "water": ("OP_Water_", "VFX_OP_Wheel"), "exit": ("OP_Exit_",),
               "landmarks": ("OP_Lmk_",), "dressing": ("OP_Veg_", "OP_Prop_", "COL_OP_Veg")}


def main():
    import op_scene, op_core, op_blockout
    import build_op as B
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
    op_scene.setup(res=res, samples=samples)
    op_core.build()
    others = [z for z in B.ZONE_MODULES if z != zone and all_detail and B.zone_ready(z)]
    detail_zone = B.zone_ready(zone)
    op_blockout.build(skip=({zone} if detail_zone else set()) | set(others))
    for z in others:
        for m in B.ZONE_MODULES[z]:
            B.run_module(m)
    mods = []
    if detail_zone:
        before = {o.name for o in bpy.data.objects}
        for m in B.ZONE_MODULES[zone]:
            t = time.time()
            mods.append(B.run_module(m))
            print("STUDIO modulo %s %.1fs" % (m, time.time() - t))
        made = [o for o in bpy.data.objects if o.name not in before]
    else:
        print("STUDIO AVISO: zona %s em BLOCKOUT (sem modulo de detalhe no M1)" % zone)
        made = [o for o in bpy.data.objects if o.name.startswith(ZONE_PREFIX[zone])]
    fm_lib.make_materials()
    op_scene.tone_emissives()
    op_scene.sea()
    op_scene.neighbors()
    op_scene.cameras()
    op_scene.scale_reference(visible=True)
    for mod in mods:
        for n, v in getattr(mod, "CAMS", {}).items():
            DL.camera(n, v[0], v[1], v[2] if len(v) > 2 else 20)
    bpy.context.view_layer.update()
    meshes = [o for o in made if o.type == "MESH" and not o.name.startswith("COL_")]
    cols = [o for o in made if o.name.startswith("COL_")]
    lpre = {"castle": ("L_OPCas",), "summon": ("L_OPSum",), "capital": ("L_OPCap", "L_OPProp_Lamp_Rua"),
            "entry": ("L_OPProp_Toro_In", "L_OPProp_Lamp_Bridge"), "exit": ("L_OPProp_Lamp_Saida",),
            "harbor": ("L_OPProp_Lamp_Porto",), "dressing": ("L_OPProp_",)}.get(zone, ("L_OP_none",))
    lights = [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith(lpre)]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    mats = set()
    for o in meshes:
        for m in o.data.materials:
            if m:
                mats.add(m.name)
    new_mats = sorted(m for m in mats if m not in base_mats and fm_lib.family_of(m) not in base_mats)
    mp = sum(est_meshparts(o) for o in meshes)
    b = BUDGET[zone]
    flag = lambda v, lim: "OK" if v <= lim else "ESTOUROU"
    print("STUDIO METRICAS zona=%s objetos=%d malhas=%d" % (zone, len(made), len(meshes)))
    print("STUDIO tris=%d/%d %s | MeshParts~%d/%d %s | materiais_novos=%d/%d %s %s" % (
        tris, b[0], flag(tris, b[0]), mp, b[1], flag(mp, b[1]), len(new_mats), b[2], flag(len(new_mats), b[2]), new_mats))
    print("STUDIO colisoes=%d/%d %s | luzes~%d (de dia <= %d)" % (len(cols), b[3], flag(len(cols), b[3]), len(lights), b[4]))
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh|Empty)(\.\d+)?$")
    bad_names = [o.name for o in made if gen.match(o.name) or re.match(r".+\.\d{3}$", o.name)]
    prefix_ok = [o.name for o in meshes if not o.name.startswith(("OP_", "VFX_", "GATE_", "SCALE_", "PREVIEW_"))]
    degen = sum(1 for o in meshes for p in o.data.polygons if p.area < 1e-6)
    print("STUDIO tecnico: nomes_ruins=%s prefixo_fora_do_padrao=%s degeneradas=%d" % (bad_names[:8], prefix_ok[:8], degen))
    names = {o.name for o in bpy.data.objects}
    req = ZONE_MARKERS.get(zone, [])
    miss = [n for n in req if n not in names]
    print("STUDIO marcadores obrigatorios: %d/%d %s" % (len(req) - len(miss), len(req), ("FALTAM " + str(miss)) if miss else "OK"))
    import op_qa
    op_qa.nav()
    op_qa.clear()
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


if __name__ == "__main__":
    main()
