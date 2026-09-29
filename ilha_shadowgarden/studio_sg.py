# studio_sg.py - estudio de UMA zona da Ilha 3 (Shadow Garden): monta a ilha com a zona pedida em DETALHE (modulo sg_<zona>) e o resto
# em blockout, renderiza as cameras da zona, roda as rotas de navegacao, confere os marcadores obrigatorios e mede o
# orcamento (tris, MeshParts estimadas, materiais novos, colisoes, luzes).
# uso:
#   blender -b --factory-startup --python studio_db.py -- <zona> <pasta_saida_ABSOLUTA> [--cams CAM_A,CAM_B]
#           [--res 960x540] [--save] [--no-render] [--samples 16] [--all-detail]
# zonas: terrain entry village castle hall summon craft dungeon water exit dressing
#   --all-detail: as OUTRAS zonas prontas tambem entram em detalhe (para o vestir/integracao)
import sys, os, time, math, re, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_lib as DL
import bpy
import fm_lib
import sg_layout as L
import sg_scene as db_scene
import sg_core as db_core
import sg_blockout as db_blockout
import build_sg as B

ZONE_CAMS = {
    "terrain": ["CAM_SG_Ref_Main", "CAM_SG_Front", "CAM_SG_Left", "CAM_SG_Right", "CAM_SG_Back", "CAM_SG_Ref_Side"],
    "entry": ["CAM_SG_Entry", "CAM_SG_PlayerHeight_Entry", "CAM_SG_Ref_Front"],
    "village": ["CAM_SG_Village", "CAM_SG_Ref_Village", "CAM_SG_PlayerHeight_Plaza", "CAM_SG_PlayerHeight_Village"],
    "castle": ["CAM_SG_Castle", "CAM_SG_Ref_Castle", "CAM_SG_PlayerHeight_Castle", "CAM_SG_Ref_Main", "CAM_SG_Back"],
    "hall": ["CAM_SG_MiningHall", "CAM_SG_PlayerHeight_MiningHall"],
    "summon": ["CAM_SG_Summon", "CAM_SG_PlayerHeight_Summon"],
    "craft": ["CAM_SG_Craft", "CAM_SG_CraftInterior", "CAM_SG_PlayerHeight_Craft"],
    "dungeon": ["CAM_SG_Dungeon", "CAM_SG_DungeonInterior", "CAM_SG_DungeonRooms", "CAM_SG_PlayerHeight_DungeonRoom"],
    "water": ["CAM_SG_Ref_Main", "CAM_SG_Front", "CAM_SG_Left"],
    "exit": ["CAM_SG_ExitGate", "CAM_SG_PlayerHeight_ExitGate", "CAM_SG_Right"],
    "dressing": ["CAM_SG_Ref_Main", "CAM_SG_PlayerHeight_Plaza", "CAM_SG_Village", "CAM_SG_PlayerHeight_Village"],
}
ZONE_MARKERS = {
    "summon": ["SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition"],
    "craft": ["CRAFT_Station", "PLAYER_INTERACT_Craft", "NPC_Craft"],
    "dungeon": ["DUNGEON_Entrance", "DUNGEON_Portal", "DUNGEON_Spawn", "DUNGEON_ExitPortal"],
    "exit": ["ISLAND_EXIT_ShadowGarden", "ISLAND_NEXT_ANCHOR_DemonSlayer", "GATE_DemonSlayer"],
    "hall": ["MiningZone_ShadowGarden"],
}
# orcamento por zona: (tris, MeshParts estimadas, materiais NOVOS, colisoes COL_, luzes)
# total da ilha: <= 480k tris, <= ~680 MeshParts, <= ~1800 colisoes, <= 40 luzes (a noite pede luz local)
BUDGET = {
    # passe de acabamento (2026-09-29): folga para kits de livros/frascos, portas/janelas com caixilho e ruinas
    "terrain": (120000, 150, 8, 90, 0), "entry": (40000, 55, 4, 45, 5), "village": (88000, 110, 9, 90, 6),
    "castle": (160000, 190, 12, 175, 5), "hall": (64000, 62, 9, 40, 6), "summon": (38000, 52, 5, 42, 3),
    "craft": (84000, 74, 11, 75, 4), "dungeon": (95000, 100, 10, 155, 7), "water": (20000, 32, 3, 10, 0),
    "exit": (26000, 38, 4, 45, 3), "dressing": (90000, 150, 9, 160, 7),
}
# overhaul 06-08 (2026-09-29): craft 66k -> 84k tris. A alquimia e heroi por fora e por dentro e estava com a
# hierarquia de acabamento invertida (16.05): +cantaria/arcada cega/cunhais/contrafortes em lances (exterior ~+6k),
# portico com aduelas, telhado proprio e medalhao (+2k), vasos de bronze no lugar dos tanques (+2k), domo em escamas
# e frasco pintado com berco e mancais (+2k), lambril/pilastras/reboco, patas, carvoes e kit de vela (+4k). O teto
# da ilha e 700k (antes do overhaul ~640k): a ilha fica em ~662k. MeshParts e materiais novos seguem no limite antigo.
# setor 04b (2026-09-29, pedido do usuario: salao maior + trono melhor): hall 52k -> 64k tris, MeshParts 58 -> 62. O
# salao cresceu de 84 x 88 x 28 para 96 x 99 x 48 (mesma quantidade de tramos, cada um maior: silhar/abobada/vitrais
# ~+3k por escala) e ganhou a ABSIDE do trono dentro da torre-coroa: arco triunfal com pilares compostos, estrado de
# 4 degraus, abobada de nervuras da abside, vitrais e o trono novo (~+5k); revisao 04b-3: ROSACEA DA LUA de 18 no
# fundo, lancetas ao lado e o cordao na altura do arranque dos vitrais (~+2k). O castelo segue <= 160k.
# setor 09b (pedido do usuario: dungeon maior, cabe um grupo): dungeon 80k -> 95k tris (salas x1,84 de area, boca e
# tunel para 4-6 avatares; +10 pilastras, +18 arcadas, +8 tochas). Summon MeshParts 50 -> 52 (kit de lanterna 12).


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
    db_scene.moon()
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
    prefix_ok = [o.name for o in meshes if not o.name.startswith(("SG_", "VFX_", "GATE_", "SCALE_", "PREVIEW_"))]
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
    import sg_qa as db_qa
    db_qa.nav()
    db_qa.clear()
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
