# export_sg.py - exporta a Ilha 3 (Shadow Garden) para o Roblox reaproveitando o export_roblox do lobby (como as Ilhas
# 1 e 2). uso: blender -b ilha_shadowgarden.blend --python export_sg.py [-- <pasta_saida>]   (padrao ilha_shadowgarden/export)
#      SG_BUDGET=warn grava mesmo com orcamento estourado (padrao strict: falha sem gravar)
# O que faz (sem salvar o .blend):
#   1. leva a ilha do referencial de projeto para o MUNDO do lobby com a matriz de encaixe (sg_layout.world_matrix):
#      W3 = T(ancora da Ilha 2) . Rz(67) . T(-WORLD_FROM_PREV). WORLD_FROM_PREV cai EXATAMENTE na
#      ISLAND_NEXT_ANCHOR_ShadowGarden da Ilha 2 em Roblox (-579,227; 28,2; 650,727);
#   2. roda export_roblox.main() com a identidade da ilha (ILHA3_<colecao>_<ID6>.fbx, ilha3_data.json,
#      montar_ilha_shadowgarden.lua, Model workspace.ILHA_SHADOWGARDEN) + o bloco Lua comum das ilhas:
#      - pecas moveis VFX_* -> tag IlhaMovel (mesmo LocalScript das Ilhas 1 e 2);
#      - portao Demon Slayer: tag PortaoCompra (mesmo ModuleScript ReplicatedStorage.PortoesCompra);
#      - guarda provisoria da ancora (SG_Exit_AnchorGuard + COL_SGAnchorGuard_*): tag GuardaProximaIlha.
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_lib as SL
import bpy
from mathutils import Matrix, Vector
import sg_layout as L

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("SG_BUDGET", "strict")
import export_roblox as ER
ER.OUT = OUT
ER.BUDGET_MODE = os.environ["FM_BUDGET"].lower()

WORLD = L.world_matrix()


def to_world_xy(x, y):
    v = WORLD @ Vector((x, y, 0.0))
    return (v.x, v.y)


# ------------------------------------------------------------------ 1) referencial de projeto -> mundo do lobby
def to_world():
    n = 0
    for o in list(bpy.data.objects):
        if o.parent is None:
            o.matrix_world = WORLD @ o.matrix_world
            n += 1
    for o in bpy.data.objects:
        if "pivot" in o.keys():
            o["pivot"] = tuple(WORLD @ Vector(o["pivot"]))
        if "axis" in o.keys():
            o["axis"] = tuple(WORLD.to_3x3() @ Vector(o["axis"]))
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.type == "EMPTY" and o.users_collection and o.users_collection[0].name == ER.MARKER_COLL:
            if "waypoints" in o.keys():
                pts = []
                for t in str(o["waypoints"]).split(";"):
                    x, y, z = (float(v) for v in t.split(","))
                    pts.append("%.2f,%.2f,%.2f" % tuple(ER.to_rbx(WORLD @ Vector((x, y, z)))))
                o["waypoints"] = ";".join(pts)
            for k in list(o.keys()):
                v = o[k]
                if hasattr(v, "__len__") and not isinstance(v, str) and len(v) == 3:
                    try:
                        w = [float(c) for c in v]
                    except (TypeError, ValueError):
                        continue
                    if k.endswith(("pivot", "_pos", "center")):
                        w = ER.to_rbx(WORLD @ Vector(w))
                    for ax, c in zip("xyz", w):
                        o["%s_%s" % (k, ax)] = round(c, 3)
                    del o[k]
            f = (o.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
            o["fwd_x"] = round(f.x, 4)
            o["fwd_z"] = round(-f.y, 4)
            if "heading_deg" in o.keys():
                o["heading_deg_local"] = o["heading_deg"]
                o["heading_deg"] = round(math.degrees(math.atan2(-f.y, f.x)), 3)
    return n


# ------------------------------------------------------------------ 2) identidade e orcamento da ilha
ER.FBX_PREFIX = "ILHA3"
ER.ROOT_NAME = "ILHA_SHADOWGARDEN"
ER.DATA_FILE = "ilha3_data.json"
ER.LUA_FILE = "montar_ilha_shadowgarden.lua"
ER.SERVER_SCRIPT = "ILHA_SHADOWGARDEN_Servidor"
ER.MARKER_COLL = "14_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "ilha3"
ER.GROUPS = ["02_TERRAIN", "03_MINING_HALL", "04_CASTLE", "05_VILLAGE", "06_SUMMON", "07_WATER", "08_NEXT_ISLAND",
             "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "12_VFX_HELPERS", "16_CRAFT", "17_DUNGEON", "18_ENTRY"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "NPC_", "SG_Sky_Sea", "SG_Sky_Clouds", "GATEGAL_", "CAM_", "PREVIEW_",
                  "SG_Hall_OreProxy", "SG_Dun_OreProxy")
ER.SKIP_NAMES = set()
ER.OWNERS = [("SG_Ter_", "terrain"), ("SG_Sky_", "terrain"), ("SG_Ent_", "entry"), ("SG_Vil_", "village"),
             ("SG_Cas_", "castle"), ("SG_Hall_ThroneMov", "vfx"), ("SG_Hall_", "hall"), ("SG_Cave_", "cave"),
             ("SG_Sum_", "summon"), ("SG_Craft_", "craft"),
             ("SG_Dun_", "dungeon"), ("SG_Water_", "water"), ("SG_Exit_", "exit"), ("GATE_", "gate_ds"),
             ("VFX_", "vfx"), ("SG_Veg_", "vegetation"), ("SG_Prop_", "props")]
# tetos por dono = orcamento das zonas (REFINAMENTO_BRIEF.md) + ~8% de folga do export (fatias por material/celula)
# overhaul 14-16 (2026-09-29): tetos por dono alinhados com o studio_sg.BUDGET atual (+ folga do export). As zonas
# cresceram por pedido do usuario ou por acabamento heroi aprovado: hall 46k -> 66k (salao 96 x 99 x 48 + abside do
# trono, setor 04b), craft 64k -> 86k (alquimia heroi por dentro e por fora, setores 06-08), dungeon 86k -> 98k (salas
# para um grupo, setor 09b), village 82k -> 90k (kit de casas refeito, setor 02). O total da ilha segue <= 700k
# (static_tris) e <= 800 MeshParts; castle/terrain/props/summon ficaram bem abaixo dos tetos antigos.
# v4 (ONDA 0, plano mestre aprovado 2026-09-30): tetos por dono = studio_sg.BUDGET v4 + ~8% de folga do export.
# Superficie (render junto) <= 700k / 720; SUBSOLO (cave + dungeon) <= 160k / 130, escondido no cliente fora do subsolo.
# 'cave' e o dono novo (SG_Cave_: salao sombrio + poco da escada caracol); o trono movel (SG_Hall_ThroneMov) conta
# como peca movel (vfx).
ER.BUDGET_OWNER = {"terrain": (78000, 124), "entry": (44000, 42), "village": (118000, 117), "castle": (184000, 135),
                   "hall": (90000, 86), "cave": (76000, 65), "summon": (31500, 38), "craft": (86500, 68),
                   "dungeon": (84000, 70), "water": (4000, 12), "exit": (29000, 38), "gate_ds": (30000, 40),
                   "vfx": (18000, 50), "vegetation": (63000, 68), "props": (30000, 50)}
# ONDA 3 (integracao, 2026-10-01): tetos dos donos que mudaram = medido no export da ilha inteira + ~8% de folga:
# hall 83,6k / 79 MeshParts (arcada de 16 pilares, naves laterais, galerias; o salao 2x fatia em mais celulas de 128),
# village 109,0k / 105 (7 casas com interior), props 27,4k / 39 (chao do patio inteiro + terraco do mirante, onda 2),
# vegetation 58,2k / 61, summon 28,9k / 34, craft 80,0k / 62. O teto que manda continua o da ilha (ER.BUDGET:
# 860k tris / 870 MeshParts estaticos; medido 847k / 809).
# JARDINAGEM (2026-09-30, pedido do usuario, orcamento autorizado pela coordenacao: grama + flores ate ~80k e ilha ate
# 750k): o campo de tufos "bonemeal", as flores em manchas, os jardins das casas e o jardim de lua do patio
# (SG_Veg_Gdn_*, sg_garden) entram no dono 'vegetation': medido 96,6k tris / 74 MeshParts no estudio -> teto com ~10%.
# v4 (ONDA 0, plano mestre aprovado 2026-09-30): 860k / 870 estaticos (superficie <= 700k / 720 + subsolo <= 160k /
# 130), total com a reserva de VFX 880k / 910; luzes de dia 48 (salao sombrio 6 + casas 4)
ER.BUDGET = {"static_tris": 860000, "static_meshes": 870, "vfx_tris": 20000, "vfx_meshes": 40, "total_tris": 880000,
             "total_meshes": 910, "materials": 130, "shadow_meshes": 320, "day_lights": 48, "col": 1800}
cx, cy = to_world_xy(0.0, 20.0)
ER.FAR_GROUND = None                 # v4: o mar escuro da area 3 e feito no cliente (CeuSombras), 0,5 abaixo do da Ilha 1
# rede de seguranca embaixo da ilha (v4): ABAIXO das salas da masmorra (piso -72, fundo -76) e acima do mar (-111);
# caixa alinhada ao mundo que cobre a ilha girada 100 (contorno ~720 x 420 no mundo) com folga
ER.VOID_CATCH = {"size": [800, 4, 560], "y": -100.0, "center": (cx, cy)}
ER.SKYLINE_WHOLE = ("SG_Sky_Islets",)
ER.SKYLINE_MODEL = ("SG_Sky_Islets",)
ER.BACKGROUND = ("SG_Sky_Islets",)
ER.CARVED = ("__nenhum__",)
ER.NO_FOLD_OBJ = ("VFX_", "SG_Hall_ThroneMov")
ER.SHELL_OBJ = ()
# colisoes que tambem seguram a CAMERA (teto do Mining Hall, paredes de salas/predios entraveis)
ER.CAM_COL_AREAS = {"SG_CasHall": 5.0, "SG_CasHallCeil": 1.0, "SG_CasWall": 5.0, "SG_DunRoom": 1.0,
                    "SG_CaveWall": 2.0, "SG_CaveCeil": 1.0, "SG_CasCrown": 5.0, "SG_CasChancel": 5.0,
                    "SG_CasRetable": 5.0, "SG_SpiralGuard": 1.0, "SG_CraftWall": 5.0, "SG_CraftRoof": 1.0}
# ONDA 2: casas visitaveis (sg_village_int.collisions): paredes, torreao, forro e laje do andar seguram a camera
# (soco, escada e guarda nao)
for _h in L.HOUSES:
    ER.CAM_COL_AREAS.update({"SG_VilHouse%s" % _h[0]: 5.0, "SG_VilHouse%sTurret" % _h[0]: 5.0,
                             "SG_VilHouse%sRoof" % _h[0]: 1.0, "SG_VilHouse%sFloor" % _h[0]: 1.0})
ER.NIGHT_ONLY = ("L_SGProp_", "L_SGVil_Lamp", "L_SGExit_Lantern")
ER.LIGHT_KEEP = ("L_SGHall", "L_SGSum", "L_SGDun", "L_SGCraft", "L_SGCas", "L_SGCave", "GateDemonSlayer",
                 "L_Gate_DemonSlayer")
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("SG_Violet", "SG_Moon", "Glass_SG", "Energy_Core", "Metal_Gold", "P_DS_",
                                     "Metal_SG_Bronze",   # 14.04: o debrum de bronze nao funde no ferro
                                     "Leaf_SGPropBloom",  # 14.09: a flor fundia na pedra (TrimLow/Block_B) e sumia no jogo
                                     "Stone_SG_TrimLow",  # a borda de pedra dos canteiros fundia na folha (Leaf_SGVegMoon)
                                     # jardinagem: os 3 tons de lamina, o buxo e as flores do kit nao fundem (o tom e a
                                     # propria leitura do campo; nas floreiras a folhagem tem pouca area e ia para o reboco)
                                     "Leaf_SGGrass", "Leaf_SGBox", "Flower_SG")


def atomic(name):
    """Model Atomic por construcao/marco (streaming sem pecas pela metade)"""
    if name.startswith("SG_Hall_ThroneMov"):
        return "SG_Hall_ThroneMov"          # o TronoService move este Model inteiro (PivotTo / tween)
    # ONDA 3: Salao Sombrio + salas da masmorra num Model so, 'SUBSOLO' (filho direto de ILHA_SHADOWGARDEN): o
    # CeuSombras esconde ele de longe (HRP.Y > 46 e > 40 do poco) e o JardimSombrasIsland o inclui na caixa da area
    if name.startswith(("SG_Cave_", "SG_Dun_")):
        return "SUBSOLO"
    for pre in ("SG_Cas_", "SG_Hall_", "SG_Sum_", "SG_Craft_", "SG_Ent_", "GATE_DemonSlayer",
                "SG_Exit_AnchorGuard"):
        if name.startswith(pre):
            return pre.rstrip("_")
    m = re.match(r"^(SG_Vil_House[A-Za-z0-9]*)", name)
    return m.group(1) if m else ""


ER.atomic_model = atomic


def safe_candidates():
    sx, sy = L.SUMMON_C
    cx_, cy_ = L.PLAZA_C
    pts = [("SAFE_Entrada", L.ENTRY_SPAWN, L.P1), ("SAFE_Praca", (0.0, cy_ - 28.0), L.P1),
           ("SAFE_Vila_P1_O", (-60.0, cy_), L.P1), ("SAFE_Vila_P1_L", (64.0, cy_), L.P1),
           ("SAFE_Vila_P2", (0.0, -86.0), L.P2), ("SAFE_Vila_P2_O", (-100.0, -86.0), L.P2),
           ("SAFE_Patio_Castelo", (0.0, 20.0), L.P3), ("SAFE_Salao", (0.0, 96.0), L.HALL),
           ("SAFE_Cova", (0.0, 140.0), L.CAVE_FLOOR), ("SAFE_Galeria", (-30.0, 290.0), L.CAVE_GALLERY_Z),
           ("SAFE_Craft", (80.0, -86.0), L.P2), ("SAFE_Mirante", L.MIRANTE_E[:2], L.P3),
           ("SAFE_Summon", (sx + 12.0, sy), L.SUM), ("SAFE_Terraco_N", (-120.0, 300.0), L.P3),
           ("SAFE_Ilhota", L.exit_point(L.EXIT_BRIDGE_LEN + 6.0), L.EXIT_Z),
           ("SAFE_Ponte_Chegada", L.BRIDGE_PATH[-2], L.DECK)]
    return [(n, to_world_xy(*p), z) for n, p, z in pts]


ER.SAFE_CANDIDATES = safe_candidates

_CX, _CY = to_world_xy(0.0, 20.0)
_PF = ER.piece_flags


def _piece_flags(obname, mname, c, sz, tris):
    return _PF(obname, mname, c - Vector((_CX, _CY, 0.0)), sz, tris)


ER.piece_flags = _piece_flags


def _cap_shadows(pieces, limit):
    on = [p for p in pieces if p["shadow"]]
    if len(on) <= limit:
        return []
    rc = ER.to_rbx((_CX, _CY, 0.0))

    def prio(p):
        c = p["center_rbx"]
        return Vector(p["size_rbx"]).length / (1.0 + math.hypot(c[0] - rc[0], c[2] - rc[2]) / 110.0)
    on.sort(key=lambda p: (prio(p), p["name"]))
    cut = on[:len(on) - limit]
    for p in cut:
        p["shadow"] = False
    return [p["name"] for p in cut]


ER.cap_shadows = _cap_shadows

_COLS = ER.collisions


def _collisions(log):
    locks = [o for o in bpy.data.objects if o.name.startswith("COL_Gate") and "Lock_" in o.name]
    for o in locks:
        o.name = "LOCKTMP_" + o.name
    try:
        out = _COLS(log)
    finally:
        for o in locks:
            o.name = o.name[len("LOCKTMP_"):]
    for o in locks:
        b = ER._col_box(o)
        R = b["R"]
        out.append({"name": o.name, "kind": "GateLock", "pos": ER.to_rbx(b["c"]), "x": ER.to_rbx(R.col[0]),
                    "y": ER.to_rbx(R.col[1]), "size": [round(2 * b["h"].x, 3), round(2 * b["h"].y, 3),
                                                       round(2 * b["h"].z, 3)], "cam": False})
    n = sum(1 for c in out if c["name"].startswith("COL_GateDemonSlayerLock_"))
    assert n == 1, "portao DemonSlayer com %d colisoes de bloqueio" % n
    return out


ER.collisions = _collisions

import export_ilha_lua as XL


def extra_lua(vfx):
    s = XL.extra_lua(ER, vfx)
    s = s.replace("'^EXIT_AnchorGuard'", "'^SG_Exit_AnchorGuard'").replace(
        "string.match(d.Name, '^COL_ExitAnchorGuard_')", "string.match(d.Name, '^COL_SGAnchorGuard_')")
    s = s.replace("integracao da Ilha 2 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR)",
                  "integracao da ilha Demon Slayer (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_DemonSlayer)")
    return s


def main():
    print("EXPORT_SG: %d materiais Glow -> Neon" % XL.neon_rules())
    # proxies de minerio (se algum modulo criou para revisao) e stubs do QA NUNCA entram
    for o in [o for o in bpy.data.objects if o.name.startswith(("SG_Hall_OreProxy", "SG_Dun_OreProxy", "COL_QA_"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    n_w = to_world()
    vfx = XL.vfx_list(ER)
    ER.EXTRA_LUA = extra_lua(vfx)
    print("EXPORT_SG: %d raizes levadas ao mundo, %d pecas moveis" % (n_w, len(vfx)))
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        want = {"WORLD_FROM_PREV", "WORLD_ENTRY_ShadowGarden", "ISLAND_EXIT_ShadowGarden", "ISLAND_NEXT_ANCHOR_DemonSlayer",
                "GATE_DemonSlayer", "SUMMON_Main", "MiningZone_ShadowGarden", "CRAFT_Station", "DUNGEON_Entrance",
                "DUNGEON_Spawn", "DUNGEON_Hall", "THRONE_Rest", "THRONE_Park", "DUN_NEXT_R2", "DUN_NEXT_R3"}
        con = {m["name"]: m for m in data["markers"] if m["name"] in want}
        json.dump(con, open(os.path.join(OUT, "conexao_roblox.json"), "w", encoding="utf-8"), indent=1)
        for k in sorted(con):
            print("CONEXAO %-34s pos %s  eixoY %s" % (k, con[k]["pos"], con[k]["y"]))
    except Exception as e:
        print("CONEXAO: nao consegui resumir:", e)


main()
