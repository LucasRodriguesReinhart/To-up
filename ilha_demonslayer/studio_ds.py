# studio_ds.py - estudio de UMA zona da Ilha 4 (DEMON SLAYER): monta a ilha com a zona pedida em DETALHE (modulo
# ds_<zona>) e o resto em blockout, renderiza as cameras da zona, roda as rotas de navegacao, confere os marcadores
# obrigatorios e mede o orcamento (tris, MeshParts estimadas, materiais novos, colisoes, luzes).
# uso:
#   blender -b --factory-startup --python studio_ds.py -- <zona> <pasta_saida_ABSOLUTA> [--cams CAM_A,CAM_B]
#           [--res 960x540] [--save] [--no-render] [--samples 16] [--all-detail]
# zonas: terrain entry village clearing forge summon water exit dressing
# Onda 0: nenhuma zona tem modulo -> a zona pedida e medida em BLOCKOUT.
#   --all-detail: as OUTRAS zonas prontas tambem entram em detalhe (para o vestir/integracao)
import sys, os, time, math, re, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ds_lib as DL
import bpy
import fm_lib
import ds_layout as L

ZONE_CAMS = {
    "terrain": ["CAM_DS_Ref_01", "CAM_DS_Front", "CAM_DS_Left", "CAM_DS_Right", "CAM_DS_Back", "CAM_DS_BirdEye"],
    "entry": ["CAM_DS_Entry", "CAM_DS_PlayerHeight_Entry", "CAM_DS_Ref_05"],
    "village": ["CAM_DS_Village", "CAM_DS_PlayerHeight_Village", "CAM_DS_Ref_04"],
    "clearing": ["CAM_DS_Clearing", "CAM_DS_PlayerHeight_Clearing", "CAM_DS_BirdEye"],
    "forge": ["CAM_DS_Forge", "CAM_DS_PlayerHeight_Forge", "CAM_DS_Ref_03"],
    "summon": ["CAM_DS_Summon", "CAM_DS_PlayerHeight_Summon", "CAM_DS_Ref_02"],
    "water": ["CAM_DS_Forge", "CAM_DS_Clearing", "CAM_DS_Right"],
    "exit": ["CAM_DS_OnePieceGate", "CAM_DS_PlayerHeight_OnePieceGate", "CAM_DS_Back"],
    "dressing": ["CAM_DS_Ref_01", "CAM_DS_PlayerHeight_Entry", "CAM_DS_Village", "CAM_DS_PlayerHeight_Clearing"],
}
ZONE_MARKERS = {
    "summon": ["SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition"],
    "exit": ["ISLAND_EXIT_DemonSlayer", "ISLAND_NEXT_ANCHOR_OnePiece", "GATE_OnePiece", "COL_DSAnchorGuard_001"],
    "clearing": ["MiningZone_DemonSlayer", "GP_Block_01"],
    "entry": ["WORLD_FROM_PREV", "WORLD_ENTRY_DemonSlayer"],
    "forge": ["FX_Forge_Smoke", "FX_Forge_Embers", "AUDIO_Forge", "AUDIO_Waterwheel"],
    "water": ["WATER_Pond", "WATER_Flume", "WATER_Tailrace", "WATER_Channel", "FX_Fall_1_Lip", "FX_Fall_2_Lip"],
}
# orcamento por zona (PLANO_DS secao 7): (tris, MeshParts estimadas, materiais NOVOS, colisoes COL_, luzes)
# total da ilha: <= 600k tris e <= 650 MeshParts estaticos (+ reserva VFX 15k / 30), materiais <= 110, colisoes <= 1300,
# luzes de dia <= 36 (+ NightOnly)
BUDGET = {
    "terrain": (95000, 110, 8, 700, 0), "entry": (32000, 34, 4, 40, 4), "village": (110000, 105, 10, 160, 8),
    "clearing": (12000, 20, 3, 30, 0), "forge": (120000, 95, 10, 90, 6), "summon": (32000, 40, 5, 60, 4),
    "water": (6000, 12, 2, 10, 0), "exit": (24000, 30, 3, 40, 3), "dressing": (105000, 125, 10, 120, 24),
}
# donos do export (prefixo -> dono), iguais ao export_ds.OWNERS
OWNERS = [("DS_Ter_", "terrain"), ("DS_Ent_", "entry"), ("DS_Vil_", "village"), ("DS_Clr_", "terrain"),
          ("DS_Frg_", "forge"), ("DS_Sum_", "summon"), ("DS_Exit_", "exit"), ("GATE_", "gate_op"),
          ("DS_Water_", "water"), ("VFX_", "vfx"), ("DS_Veg_", "vegetation"), ("DS_Prop_", "props")]


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


ZONE_PREFIX = {"terrain": ("DS_Ter_",), "entry": ("DS_Ent_",), "village": ("DS_Vil_", "COL_DS_Vil"),
               "clearing": ("DS_Clr_", "COL_DS_Clr"), "forge": ("DS_Frg_", "VFX_DS_Wheel", "COL_DS_Frg"),
               "summon": ("DS_Sum_", "VFX_DSSUM_", "COL_DSSum", "COL_DS_Sum"), "water": ("DS_Water_",),
               "exit": ("DS_Exit_",), "dressing": ("DS_Veg_", "DS_Prop_", "COL_DS_Veg", "COL_DS_Prop")}


def main():
    import ds_scene, ds_core, ds_blockout
    import build_ds as B
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
    ds_scene.setup(res=res, samples=samples)
    ds_core.build()
    others = [z for z in B.ZONE_MODULES if z != zone and all_detail and B.zone_ready(z)]
    detail_zone = B.zone_ready(zone)
    ds_blockout.build(skip=({zone} if detail_zone else set()) | set(others))
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
        print("STUDIO AVISO: zona %s em BLOCKOUT (sem modulo de detalhe na onda 0)" % zone)
        made = [o for o in bpy.data.objects if o.name.startswith(ZONE_PREFIX[zone])]
    fm_lib.make_materials()
    ds_scene.tone_emissives()
    ds_scene.clouds()
    ds_scene.moon()
    ds_scene.neighbors()
    ds_scene.cameras()
    ds_scene.scale_reference(visible=True)
    for mod in mods:
        for n, v in getattr(mod, "CAMS", {}).items():
            DL.camera(n, v[0], v[1], v[2] if len(v) > 2 else 20)
    bpy.context.view_layer.update()
    meshes = [o for o in made if o.type == "MESH" and not o.name.startswith("COL_")]
    cols = [o for o in made if o.name.startswith("COL_")]
    lpre = {"forge": ("L_DSFrg",), "summon": ("L_DSSum",), "village": ("L_DSVil", "L_DSProp_Lamp_Vil"),
            "entry": ("L_DSProp_Toro_In", "L_DSProp_Lamp_Bridge"), "exit": ("L_DSProp_Lamp_Exit",),
            "dressing": ("L_DSProp_",)}.get(zone, ("L_DS_none",))
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
    prefix_ok = [o.name for o in meshes if not o.name.startswith(("DS_", "VFX_", "GATE_", "SCALE_", "PREVIEW_"))]
    degen = sum(1 for o in meshes for p in o.data.polygons if p.area < 1e-6)
    print("STUDIO tecnico: nomes_ruins=%s prefixo_fora_do_padrao=%s degeneradas=%d" % (bad_names[:8], prefix_ok[:8], degen))
    names = {o.name for o in bpy.data.objects}
    req = ZONE_MARKERS.get(zone, [])
    miss = [n for n in req if n not in names]
    print("STUDIO marcadores obrigatorios: %d/%d %s" % (len(req) - len(miss), len(req), ("FALTAM " + str(miss)) if miss else "OK"))
    import ds_qa
    ds_qa.nav()
    ds_qa.clear()
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
