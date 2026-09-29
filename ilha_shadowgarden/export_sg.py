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
             ("SG_Cas_", "castle"), ("SG_Hall_", "hall"), ("SG_Sum_", "summon"), ("SG_Craft_", "craft"),
             ("SG_Dun_", "dungeon"), ("SG_Water_", "water"), ("SG_Exit_", "exit"), ("GATE_", "gate_ds"),
             ("VFX_", "vfx"), ("SG_Veg_", "vegetation"), ("SG_Prop_", "props")]
# tetos por dono = orcamento das zonas (REFINAMENTO_BRIEF.md) + ~8% de folga do export (fatias por material/celula)
ER.BUDGET_OWNER = {"terrain": (130000, 165), "entry": (44000, 60), "village": (76000, 110), "castle": (162000, 195),
                   "hall": (44000, 55), "summon": (42000, 55), "craft": (54000, 66), "dungeon": (86000, 108),
                   "water": (22000, 35), "exit": (28000, 42), "gate_ds": (30000, 40), "vfx": (18000, 50),
                   "vegetation": (34000, 62), "props": (70000, 110)}
ER.BUDGET = {"static_tris": 560000, "static_meshes": 800, "vfx_tris": 18000, "vfx_meshes": 50, "total_tris": 578000,
             "total_meshes": 850, "materials": 130, "shadow_meshes": 320, "day_lights": 42, "col": 1800}
cx, cy = to_world_xy(0.0, -10.0)
ER.FAR_GROUND = None                 # o mar distante ja vem da Ilha 1 (um so FAR_GROUND no mundo)
# rede de seguranca embaixo da ilha: ABAIXO das salas da masmorra (piso 6,0 dentro da rocha)
ER.VOID_CATCH = {"size": [420, 4, 480], "y": -40.0, "center": (cx, cy)}
ER.SKYLINE_WHOLE = ("SG_Sky_Islets",)
ER.SKYLINE_MODEL = ("SG_Sky_Islets",)
ER.BACKGROUND = ("SG_Sky_Islets",)
ER.CARVED = ("__nenhum__",)
ER.NO_FOLD_OBJ = ("VFX_",)
ER.SHELL_OBJ = ()
# colisoes que tambem seguram a CAMERA (teto do Mining Hall, paredes de salas/predios entraveis)
ER.CAM_COL_AREAS = {"SG_CasHall": 5.0, "SG_CasHallCeil": 1.0, "SG_CasWall": 5.0, "SG_DunRoom": 1.0,
                    "SG_DunHouse": 5.0, "SG_DunHouseRoof": 1.0, "SG_CraftWall": 5.0, "SG_CraftRoof": 1.0}
ER.NIGHT_ONLY = ("L_SGProp_", "L_SGVil_Lamp", "L_SGExit_Lantern")
ER.LIGHT_KEEP = ("L_SGHall", "L_SGSum", "L_SGDun", "L_SGCraft", "L_SGCas", "GateDemonSlayer", "L_Gate_DemonSlayer")
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("SG_Violet", "SG_Moon", "Glass_SG", "Energy_Core", "Metal_Gold", "P_DS_")


def atomic(name):
    """Model Atomic por construcao/marco (streaming sem pecas pela metade)"""
    for pre in ("SG_Cas_", "SG_Hall_", "SG_Sum_", "SG_Craft_", "SG_Dun_", "SG_Ent_", "GATE_DemonSlayer",
                "SG_Exit_AnchorGuard"):
        if name.startswith(pre):
            return pre.rstrip("_")
    m = re.match(r"^(SG_Vil_House[A-Za-z0-9]*)", name)
    return m.group(1) if m else ""


ER.atomic_model = atomic


def safe_candidates():
    sx, sy = L.SUMMON_C
    pts = [("SAFE_Entrada", L.ENTRY_SPAWN, L.P1), ("SAFE_Praca", (0.0, -150.0), L.P1),
           ("SAFE_Vila_P1_O", (-60.0, -120.0), L.P1), ("SAFE_Vila_P1_L", (64.0, -120.0), L.P1),
           ("SAFE_Vila_P2", (0.0, -45.0), L.P2), ("SAFE_Vila_P2_O", (-80.0, -45.0), L.P2),
           ("SAFE_Patio_Castelo", (0.0, 20.0), L.P3), ("SAFE_Salao", (0.0, 70.0), L.HALL),
           ("SAFE_Dungeon", (100.0, 50.0), L.P3), ("SAFE_Craft", (60.0, -45.0), L.P2),
           ("SAFE_Summon", (sx + 12.0, sy), L.SUM), ("SAFE_Saida", (130.0, -38.0), L.EXIT_Z),
           ("SAFE_Ilhota", L.exit_point(L.EXIT_BRIDGE_LEN + 6.0), L.EXIT_Z),
           ("SAFE_Ponte_Chegada", (0.0, -240.0), L.DECK)]
    return [(n, to_world_xy(*p), z) for n, p, z in pts]


ER.SAFE_CANDIDATES = safe_candidates

_CX, _CY = to_world_xy(0.0, -10.0)
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
                "DUNGEON_Spawn"}
        con = {m["name"]: m for m in data["markers"] if m["name"] in want}
        json.dump(con, open(os.path.join(OUT, "conexao_roblox.json"), "w", encoding="utf-8"), indent=1)
        for k in sorted(con):
            print("CONEXAO %-34s pos %s  eixoY %s" % (k, con[k]["pos"], con[k]["y"]))
    except Exception as e:
        print("CONEXAO: nao consegui resumir:", e)


main()
