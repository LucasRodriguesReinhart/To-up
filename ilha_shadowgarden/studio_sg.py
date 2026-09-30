# studio_sg.py - estudio de UMA zona da Ilha 3 (Shadow Garden): monta a ilha com a zona pedida em DETALHE (modulo sg_<zona>) e o resto
# em blockout, renderiza as cameras da zona, roda as rotas de navegacao, confere os marcadores obrigatorios e mede o
# orcamento (tris, MeshParts estimadas, materiais novos, colisoes, luzes).
# uso:
#   blender -b --factory-startup --python studio_db.py -- <zona> <pasta_saida_ABSOLUTA> [--cams CAM_A,CAM_B]
#           [--res 960x540] [--save] [--no-render] [--samples 16] [--all-detail]
# zonas: terrain entry village castle hall cave summon craft dungeon water exit dressing
# v4 (ONDA 0): a zona pedida entra em detalhe se tiver modulo em build_sg.ZONE_MODULES (os da v3 pelo sg_relocate);
# zona sem modulo (lista vazia) = BLOCKOUT v4 (mede o blockout).
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
    "castle": ["CAM_SG_Castle", "CAM_SG_Ref_Castle", "CAM_SG_PlayerHeight_Castle", "CAM_SG_Ref_Main", "CAM_SG_Back"],
    "hall": ["CAM_SG_MiningHall", "CAM_SG_PlayerHeight_MiningHall", "CAM_SG_Throne", "CAM_SG_ThroneWide"],
    "cave": ["CAM_SG_Cave", "CAM_SG_CavePortal", "CAM_SG_Spiral", "CAM_SG_SpiralCave", "CAM_SG_PlayerHeight_Dungeon"],
    "summon": ["CAM_SG_Summon", "CAM_SG_PlayerHeight_Summon"],
    "craft": ["CAM_SG_Craft", "CAM_SG_CraftInterior", "CAM_SG_PlayerHeight_Craft"],
    "dungeon": ["CAM_SG_DungeonRooms", "CAM_SG_PlayerHeight_DungeonRoom"],
    "village": ["CAM_SG_Village", "CAM_SG_Ref_Village", "CAM_SG_PlayerHeight_Plaza", "CAM_SG_PlayerHeight_Village",
                "CAM_SG_PlayerHeight_House"],
    "water": ["CAM_SG_Ref_Main", "CAM_SG_Front", "CAM_SG_Left"],
    "exit": ["CAM_SG_ExitGate", "CAM_SG_PlayerHeight_ExitGate", "CAM_SG_Right"],
    "dressing": ["CAM_SG_Ref_Main", "CAM_SG_PlayerHeight_Plaza", "CAM_SG_Village", "CAM_SG_PlayerHeight_Village"],
}
ZONE_MARKERS = {
    "summon": ["SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition"],
    "craft": ["CRAFT_Station", "PLAYER_INTERACT_Craft", "NPC_Craft"],
    "dungeon": ["DUNGEON_Spawn", "DUN_NEXT_R2", "DUN_NEXT_R3", "DUN_EXIT_R1", "DUN_EXIT_R3"],
    "cave": ["DUNGEON_Hall", "DUNGEON_Entrance", "DUNGEON_UI", "DUNGEON_Return", "CAVE_Zone", "THRONE_Stair_Bottom"],
    "exit": ["ISLAND_EXIT_ShadowGarden", "ISLAND_NEXT_ANCHOR_DemonSlayer", "GATE_DemonSlayer"],
    "hall": ["MiningZone_ShadowGarden", "THRONE_Rest", "THRONE_Park", "THRONE_Interact", "THRONE_Stair_Top"],
}
# orcamento por zona: (tris, MeshParts estimadas, materiais NOVOS, colisoes COL_, luzes)
# total da ilha: <= 480k tris, <= ~680 MeshParts, <= ~1800 colisoes, <= 40 luzes (a noite pede luz local)
BUDGET = {
    # v4 (ONDA 0, plano mestre aprovado 2026-09-30: static 860k / 870 MeshParts; superficie <= 700k / 720, subsolo
    # (salao sombrio + salas) <= 160k / 130, escondido no cliente por zona; interiores das casas por distancia)
    "terrain": (72000, 115, 8, 140, 0), "entry": (40000, 38, 4, 60, 5), "village": (100000, 108, 11, 230, 6),
    "castle": (170000, 125, 12, 260, 5), "hall": (80000, 58, 9, 80, 6), "cave": (70000, 60, 6, 260, 6),
    "summon": (29000, 44, 5, 42, 3), "craft": (84000, 74, 11, 75, 4), "dungeon": (78000, 64, 10, 160, 5),
    "water": (3000, 10, 3, 10, 0), "exit": (26000, 34, 4, 45, 3), "dressing": (80000, 107, 9, 160, 7),
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
# overhaul 14-16 (passe global): village 88k -> 90k (banzo da escada P1P2 com o chanfro 0,07 do kit da entrada, 16.01;
# +0,7k). Tetos do export_sg.BUDGET_OWNER alinhados com esta tabela (hall 66k, craft 86k, dungeon 98k, village 90k).
# setor 09b (pedido do usuario: dungeon maior, cabe um grupo): dungeon 80k -> 95k tris (salas x1,84 de area, boca e
# tunel para 4-6 avatares; +10 pilastras, +18 arcadas, +8 tochas). Summon MeshParts 50 -> 54 (kit de lanterna 12: vidro ambar + nucleo quente).
# setor 04c (pedido do usuario: "o assento do trono esta muito curto e feio"): hall 64k -> 65k tris. O trono virou
# catedra gotica (assento fundo de 3,6 com almofada espessa e queda de pano, base com rodape, arcada cega de 3 arcos
# e pes em garra, bracos com balaustre e voluta em espiral, espaldar ogival em capitone): 2,6k -> 4,2k tris; ja
# recuperados ~1,5k dentro do proprio trono (tornos n=6, espiral 17 passos, apoio varrido, capitone fechado com n-gonos).
# JARDINAGEM (2026-09-30, pedido do usuario: grama "bonemeal", flores, jardim do castelo e jardins da vila; orcamento
# autorizado pela coordenacao: grama + flores ate ~80k, ilha ate 750k): o campo de touceiras cobrindo o gramado visto
# das rotas + flores em manchas (sg_garden, chamado no fim do sg_veg) e o jardim de lua do patio (sg_court) ENTRAM NO
# VESTIR: dressing 90k/150 -> 125k/160 (medido ~116,6k tris / ~126 MeshParts estimadas; antes 39,5k / 96). Liquido da
# jardinagem na ilha ~78k (vestir +77,1k; floreiras da vila +1,0k, dentro dos 90k da vila). export_sg: static 750k e
# dono 'vegetation' 106k/82.


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
    detail_zone = B.zone_ready(zone)
    db_blockout.build(skip=({zone} if detail_zone else set()) | set(others))
    for z in others:
        for m in B.ZONE_MODULES[z]:
            try:
                B.run_module(m)
            except Exception:
                import traceback
                traceback.print_exc()
                print("STUDIO ERRO no modulo vizinho %s" % m)
    before = {o.name for o in bpy.data.objects}
    if not detail_zone:
        # zona em BLOCKOUT v4: mede o que o blockout dela criou (prefixo da zona)
        pre = {"terrain": ("SG_Ter_",), "entry": ("SG_Ent_",), "village": ("SG_Vil_", "COL_SG_VilHouse"),
               "castle": ("SG_Cas_", "COL_SG_Cas"), "hall": ("SG_Hall_", "COL_SG_Hall"), "cave": ("SG_Cave_", "COL_SG_Cave"),
               "summon": ("SG_Sum_",), "craft": ("SG_Craft_",), "dungeon": ("SG_Dun_", "COL_SG_Dun"),
               "water": ("SG_Water_",), "exit": ("SG_Exit_",), "dressing": ("SG_Veg_", "SG_Prop_")}[zone]
        before = {o.name for o in bpy.data.objects if not o.name.startswith(pre)}
        print("STUDIO AVISO: zona %s em BLOCKOUT v4 (sem modulo de detalhe na onda 0)" % zone)
    mods = []
    for m in (B.ZONE_MODULES[zone] if detail_zone else []):
        if os.path.exists(os.path.join(HERE, m + ".py")):
            t = time.time()
            try:
                mod = B.run_module(m)
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
    db_scene.neighbors()
    db_scene.tone_emissives()
    db_scene.sea()
    db_scene.islets()
    db_scene.clouds()
    db_scene.moon()
    db_scene.cameras()
    db_scene.scale_reference(visible=True)
    for mod in [m for m in mods if m.__name__ not in B.LEGACY]:
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
        want = cams or (ZONE_CAMS.get(zone, []) + [n for mod in mods if mod.__name__ not in B.LEGACY
                                                   for n in getattr(mod, "CAMS", {})])
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
