# export_db.py - exporta a Ilha 2 (Dragon Ball) para o Roblox reaproveitando o export_roblox do lobby (como a Ilha 1).
# uso: blender -b ilha_dragonball.blend --python export_db.py [-- <pasta_saida>]      (padrao ilha_dragonball/export)
#      DB_BUDGET=warn grava mesmo com orcamento estourado (padrao strict: falha sem gravar)
# O que faz (sem salvar o .blend):
#   1. leva a ilha do referencial de projeto para o MUNDO do lobby com a matriz de encaixe (db_layout.world_matrix):
#      W2 = T(ancora da Ilha 1) . Rz(135) . T(-WORLD_FROM_PREV). WORLD_FROM_PREV cai EXATAMENTE na ISLAND_NEXT_ANCHOR da
#      Ilha 1 em Roblox (-192,17; 16,2; 612,17);
#   2. roda export_roblox.main() com a identidade da ilha (ILHA2_<colecao>_<ID6>.fbx, ilha2_data.json,
#      montar_ilha_dragonball.lua, Model workspace.ILHA_DRAGONBALL) + bloco Lua proprio:
#      - pecas moveis VFX_* -> tag IlhaMovel e o MESMO LocalScript da Ilha 1 (ILHA_NARUTO_Movel; generico por tag e dono:
#        um so script anima as duas ilhas, nada gira dobrado);
#      - portao Shadow Garden: tag PortaoCompra (mesmo ModuleScript ReplicatedStorage.PortoesCompra da Ilha 1);
#      - guarda provisoria da ancora (DB_Exit_AnchorGuard + COL_DBAnchorGuard_*): tag GuardaProximaIlha.
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db_lib as DL
import bpy
from mathutils import Matrix, Vector
import db_layout as L

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("DB_BUDGET", "strict")
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
    for o in bpy.data.objects:          # propriedades de pivo das pecas moveis (em coordenadas locais do projeto)
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
ER.FBX_PREFIX = "ILHA2"
ER.ROOT_NAME = "ILHA_DRAGONBALL"
ER.DATA_FILE = "ilha2_data.json"
ER.LUA_FILE = "montar_ilha_dragonball.lua"
ER.SERVER_SCRIPT = "ILHA_DRAGONBALL_Servidor"
ER.MARKER_COLL = "14_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "ilha2"
ER.GROUPS = ["02_TERRAIN", "03_MINING_ZONE", "04_CAPSULE_LANDMARK", "05_TECH_VILLAGE", "06_SUMMON", "07_WATER",
             "08_NEXT_ISLAND", "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "12_VFX_HELPERS"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "NPC_", "DB_Sky_Sea", "DB_Sky_Clouds", "GATEGAL_", "CAM_", "DB_Mine_OreProxy")
ER.SKIP_NAMES = set()
ER.OWNERS = [("DB_Ter_", "terrain"), ("DB_Sky_", "terrain"), ("DB_Mine_", "mining"), ("DB_Ent_", "entrance"),
             ("DB_Cap_", "capsule"), ("DB_Hub_", "village"), ("DB_Twr_", "towers"), ("DB_Sum_", "summon"),
             ("DB_Water_", "water"), ("DB_Exit_", "exit"), ("GATE_", "gate_sg"), ("VFX_", "vfx"),
             ("DB_Veg_", "vegetation"), ("DB_Prop_", "props")]
ER.BUDGET_OWNER = {"terrain": (110000, 135), "mining": (38000, 50), "entrance": (38000, 50), "capsule": (65000, 88),
                   "village": (60000, 92), "towers": (38000, 60), "summon": (44000, 56), "water": (22000, 34),
                   "exit": (28000, 40), "gate_sg": (26000, 36), "vfx": (14000, 30), "vegetation": (40000, 60),
                   "props": (26000, 45)}
ER.BUDGET = {"static_tris": 480000, "static_meshes": 680, "vfx_tris": 0, "vfx_meshes": 0, "total_tris": 480000,
             "total_meshes": 680, "materials": 115, "shadow_meshes": 300, "day_lights": 40, "col": 1350}
cx, cy = to_world_xy(0.0, 0.0)
ER.FAR_GROUND = None                 # o mar distante ja vem da Ilha 1 (um so FAR_GROUND no mundo)
ER.VOID_CATCH = {"size": [440, 4, 460], "y": -40.0, "center": (cx, cy)}
ER.SKYLINE_WHOLE = ("DB_Sky_Islets",)
ER.SKYLINE_MODEL = ("DB_Sky_Islets",)
ER.BACKGROUND = ("DB_Sky_Islets",)
ER.CARVED = ("__nenhum__",)
ER.NO_FOLD_OBJ = ("VFX_",)
ER.SHELL_OBJ = ()
ER.CAM_COL_AREAS = {"DB_CapShell": 5.0, "DB_CapWall": 5.0, "DB_HubWorkshop": 5.0, "DB_HubMarket": 5.0}
ER.NIGHT_ONLY = ("L_DBEnt_Lantern", "L_DBProp_", "L_DBLant", "L_DBPath", "L_DBBridge", "L_DBExit_Lantern")
ER.LIGHT_KEEP = ("L_DBSum", "L_DBCap", "GateShadowGarden", "L_Gate_ShadowGarden")
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Summon_", "DB_Energy", "Metal_Gold", "Energy_Core", "DB_Cyan", "DB_Ball",
                                     "DB_Star", "Glass_DB")


def atomic(name):
    """Model Atomic por construcao/marco (streaming sem pecas pela metade)"""
    for pre in ("DB_Cap_", "DB_Sum_", "DB_Ent_Gate", "GATE_ShadowGarden", "DB_Exit_AnchorGuard", "DB_Hub_Market",
                "DB_Hub_Workshop", "DB_Hub_Dojo"):
        if name.startswith(pre):
            return pre.rstrip("_")
    m = re.match(r"^(DB_Hub_House[A-Za-z0-9]*|DB_Twr_[A-Za-z]+)", name)
    return m.group(1) if m else ""


ER.atomic_model = atomic


def safe_candidates():
    cxp, cyp = L.SUMMON_C
    pts = [("SAFE_Entrada", L.ENTRY_SPAWN, L.GROUND), ("SAFE_Prom_S", (0.0, -65.0), L.GROUND),
           ("SAFE_Prom_N", (0.0, 61.0), L.GROUND), ("SAFE_Prom_L", (73.0, 0.0), L.GROUND),
           ("SAFE_Prom_O", (-72.0, 0.0), L.GROUND), ("SAFE_Arena", (0.0, -20.0), L.ARENA),
           ("SAFE_Vila", (0.0, 96.0), L.HUB), ("SAFE_Capsule", (0.0, 128.0), L.HUB),
           ("SAFE_Summon", (cxp + 12.0, cyp), L.SUM), ("SAFE_Saida", L.EXIT_PATH[2], L.EXIT_Z),
           ("SAFE_Ilhota", L.exit_point(L.EXIT_BRIDGE_LEN + 6.0), L.EXIT_Z),
           ("SAFE_Ponte_Chegada", (0.0, -150.0), L.DECK)]
    return [(n, to_world_xy(*p), z) for n, p, z in pts]


ER.SAFE_CANDIDATES = safe_candidates

_CX, _CY = to_world_xy(0.0, 0.0)
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
    n = sum(1 for c in out if c["name"].startswith("COL_GateShadowGardenLock_"))
    assert n == 1, "portao ShadowGarden com %d colisoes de bloqueio" % n
    return out


ER.collisions = _collisions

import export_ilha_lua as XL


def extra_lua(vfx):
    s = XL.extra_lua(ER, vfx)
    s = s.replace("'^EXIT_AnchorGuard'", "'^DB_Exit_AnchorGuard'").replace("'^COL_ExitAnchorGuard_'",
                                                                           "'^COL_DBAnchorGuard_'")
    s = s.replace("integracao da Ilha 2 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR)",
                  "integracao da Ilha 3 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_ShadowGarden)")
    return s


def main():
    print("EXPORT_DB: %d materiais Glow -> Neon" % XL.neon_rules())
    # prova de desenvolvimento (proxies de minerio) NUNCA entra: nada de DB_Mine_OreProxy no export
    for o in [o for o in bpy.data.objects if o.name.startswith(("DB_Mine_OreProxy", "COL_QA_"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    n_w = to_world()
    vfx = XL.vfx_list(ER)
    ER.EXTRA_LUA = extra_lua(vfx)
    print("EXPORT_DB: %d raizes levadas ao mundo, %d pecas moveis" % (n_w, len(vfx)))
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        want = {"WORLD_FROM_PREV", "WORLD_ENTRY_DragonBall", "ISLAND_EXIT_DragonBall", "ISLAND_NEXT_ANCHOR_ShadowGarden",
                "GATE_ShadowGarden", "SUMMON_Main", "MiningZone_DragonBall"}
        con = {m["name"]: m for m in data["markers"] if m["name"] in want}
        json.dump(con, open(os.path.join(OUT, "conexao_roblox.json"), "w", encoding="utf-8"), indent=1)
        for k in sorted(con):
            print("CONEXAO %-34s pos %s  eixoY %s" % (k, con[k]["pos"], con[k]["y"]))
    except Exception as e:
        print("CONEXAO: nao consegui resumir:", e)


main()
