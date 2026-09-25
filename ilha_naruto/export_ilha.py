# export_ilha.py - exporta a Ilha 1 (Naruto) para o Roblox reaproveitando o export_roblox do lobby.
# uso: blender -b ilha_naruto.blend --python export_ilha.py [-- <pasta_saida>]      (padrao ilha_naruto/export)
#      IL_BUDGET=warn grava mesmo com orcamento estourado (padrao strict: falha sem gravar)
# O que faz (sem salvar o .blend):
#   1. tira da cena a GALERIA dos 4 portoes de compra (eles saem pelo export_portoes.py, como assets separados);
#   2. leva a ilha do referencial de projeto para o MUNDO do lobby: giro de 180 graus + (0, -420, 0) no Blender
#      -> Roblox = (-x_local, z, 420 + y_local). A ponta da ponte de chegada cai em Roblox z 222 (fim da ponte do lobby);
#   3. roda export_roblox.main() com a identidade da ilha (ILHA1_<colecao>_<ID6>.fbx, ilha_data.json,
#      montar_ilha_naruto.lua, Model workspace.ILHA_NARUTO) + um bloco Lua proprio:
#      - pecas moveis VFX_* (aneis/estrela do summon, roda d'agua, esferas do portao) -> LocalScript que gira/flutua;
#      - portoes de compra: atributos e tag 'PortaoCompra' nas pecas LOCKED + ModuleScript
#        ReplicatedStorage.PortoesCompra com Estado(chave, desbloqueado) (vale no servidor ou so no cliente de quem pagou).
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy
from mathutils import Matrix, Vector
import il_layout as L
import il_gate_std as GS

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("IL_BUDGET", "strict")
import export_roblox as ER
ER.OUT = OUT
ER.BUDGET_MODE = os.environ["FM_BUDGET"].lower()

WORLD = Matrix.Translation(Vector(L.WORLD_OFFSET)) @ Matrix.Rotation(math.radians(L.WORLD_YAW_DEG), 4, "Z")


def to_world_xy(x, y):
    v = WORLD @ Vector((x, y, 0.0))
    return (v.x, v.y)


# ------------------------------------------------------------------ 1) galeria fora
def gallery_names():
    keys = GS.GALLERY_ORDER
    pat = re.compile(r"^(GATEGAL_|CAM_Gate|COL_GateGal)|^(GATE_|VFX_GATE_|COL_Gate|PURCHASE_UI_ANCHOR_|L_Gate_?)(%s)"
                     % "|".join(keys))
    return [o.name for o in bpy.data.objects if pat.match(o.name)]


def drop_gallery():
    names = gallery_names()
    for n in names:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    # qualquer sobra longe da ilha (x local > 500) tambem sai
    far = [o for o in bpy.data.objects if o.type in ("MESH", "EMPTY", "LIGHT") and o.parent is None
           and o.matrix_world.translation.x > 500.0 and not o.name.startswith(("SKY_", "SUN_"))]
    for o in far:
        bpy.data.objects.remove(o, do_unlink=True)
    return len(names) + len(far)


# ------------------------------------------------------------------ 2) referencial de projeto -> mundo do lobby
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
    # marcadores: direcao de AVANCO (+Y local do marcador) ja no Roblox, como atributos escalares fwd_x/fwd_z
    # (a Part do marcador usa CFrame.fromMatrix(pos, X, Y): o avanco e o UpVector dela; os atributos evitam a duvida)
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
                o["heading_deg"] = round(math.degrees(math.atan2(-f.y, f.x)), 3)   # no plano XZ do Roblox
    return n


# ------------------------------------------------------------------ 3) identidade e orcamento da ilha
ER.FBX_PREFIX = "ILHA1"
ER.ROOT_NAME = "ILHA_NARUTO"
ER.DATA_FILE = "ilha_data.json"
ER.LUA_FILE = "montar_ilha_naruto.lua"
ER.SERVER_SCRIPT = "ILHA_NARUTO_Servidor"
ER.MARKER_COLL = "14_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "ilha"
ER.GROUPS = ["02_TERRAIN", "03_MINING", "04_VILLAGE", "05_SUMMON", "06_WATER", "07_NEXT_ISLAND",
             "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "12_VFX_HELPERS"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "NPC_", "SKY_Sea", "SKY_Clouds", "GATEGAL_", "CAM_", "MINE_Ore_")
ER.SKIP_NAMES = set()
ER.OWNERS = [("TER_", "terrain"), ("SKY_", "terrain"), ("MINE_", "mining"), ("ENT_", "entrance"),
             ("VIL_", "village"), ("SUM_", "summon"), ("WATER_", "water"), ("EXIT_", "exit"), ("GATE_", "gate_db"),
             ("VFX_", "vfx"), ("VEG_", "vegetation"), ("PROP_", "props")]
ER.BUDGET_OWNER = {"terrain": (110000, 130), "mining": (48000, 70), "entrance": (32000, 42), "village": (100000, 150),
                   "summon": (38000, 48), "water": (24000, 38), "exit": (22000, 32), "gate_db": (26000, 34),
                   "vfx": (12000, 28), "vegetation": (45000, 60), "props": (26000, 45)}
ER.BUDGET = {"static_tris": 470000, "static_meshes": 660, "vfx_tris": 0, "vfx_meshes": 0, "total_tris": 470000,
             "total_meshes": 660, "materials": 110, "shadow_meshes": 300, "day_lights": 36, "col": 1150}
cx, cy = to_world_xy(0.0, 0.0)
ER.FAR_GROUND = {"size": [2048, 2, 2048], "top_z": L.SEA, "material": "Sea_Water", "center": (cx, cy)}
ER.VOID_CATCH = {"size": [420, 4, 440], "y": -40.0, "center": (cx, cy - 10.0)}
ER.SKYLINE_WHOLE = ("SKY_Islets",)
ER.SKYLINE_MODEL = ("SKY_Islets",)
ER.BACKGROUND = ("SKY_Islets",)
ER.CARVED = ("__nenhum__",)
ER.NO_FOLD_OBJ = ("VFX_",)
# camera: as PAREDES de colisao dos interiores ganham a tag CamOccluder (o Popper respeita a tag, como no lobby).
# Sem cascas visuais: props internos (balcao, estantes) nao podem ocluir a camera nem pesar na fisica do celular.
ER.SHELL_OBJ = ()
ER.CAM_COL_AREAS = {"VillageHall": 5.0, "VillageShop": 5.0, "VillageRamen": 5.0, "HousesMill": 5.0}
# lanternas externas: so a noite (de dia so interiores, nucleo do fosso, summon e barreira)
ER.NIGHT_ONLY = ("L_Lantern", "L_Toro", "L_Ring", "L_Bridge", "L_Path", "L_Entrance_", "L_Exit_Anchor",
                 "L_GateDB_Lantern", "L_Mining_Gate", "L_Summon_Lantern")
ER.LIGHT_KEEP = ("L_Summon_Portal", "L_Summon_Star", "L_GateDB_Barrier", "L_Village_Hall", "L_Houses_Mill")
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Summon_", "DB_Energy", "Metal_Gold", "Energy_Core")


def atomic(name):
    """Model Atomic por construcao/marco (streaming sem pecas pela metade)"""
    for pre in ("VIL_MainHall", "VIL_WeaponShop", "VIL_WaterTower", "VIL_Ramen", "VIL_Mill", "SUM_Tower", "ENT_Gate",
                "GATE_DB", "EXIT_AnchorGuard"):
        if name.startswith(pre):
            return pre
    m = re.match(r"^(VIL_House_[A-Za-z0-9]+_\d+)", name)
    return m.group(1) if m else ""


ER.atomic_model = atomic


def safe_candidates():
    pts = [("SAFE_Entrada", (0.0, -100.0), L.G), ("SAFE_Anel_S", (0.0, -70.0), L.RING),
           ("SAFE_Anel_N", (0.0, 71.0), L.RING), ("SAFE_Anel_L", (71.0, -6.0), L.RING),
           ("SAFE_Anel_O", (-71.0, -6.0), L.RING), ("SAFE_Fosso", (0.0, -30.0), L.PIT),
           ("SAFE_T1", (0.0, 108.0), L.T1), ("SAFE_T2", (0.0, 134.0), L.T2), ("SAFE_Summon", (-112.0, 20.0), L.T1),
           ("SAFE_Moinho", (86.0, 12.0), L.G), ("SAFE_Vale_Leste", (126.0, -10.0), L.G),
           ("SAFE_Ilhota", L.exit_point(L.EXIT_BRIDGE_LEN + 6.0), L.EXIT_Z)]
    return [(n, to_world_xy(*p), z) for n, p, z in pts]


ER.SAFE_CANDIDATES = safe_candidates

# sombra: o export_roblox mede a distancia da ORIGEM do lobby (SHADOW_DIST 220); a ilha fica a 420 dali e saia
# inteira sem sombra. Aqui a distancia e medida do CENTRO DA ILHA.
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

# colisao de bloqueio dos portoes: fora da deduplicacao (uma caixa da moldura "coberta" por ela sumiria e, depois do
# desbloqueio, abriria um buraco); volta intacta e conferida (1 por portao)
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
    gates = {o["key"] if "key" in o.keys() else o.name[5:] for o in bpy.data.objects
             if o.type == "EMPTY" and re.match(r"^GATE_[A-Za-z]+$", o.name)}
    for g in gates:
        n = sum(1 for c in out if c["name"].startswith("COL_Gate%sLock_" % g))
        assert n == 1, "portao %s com %d colisoes de bloqueio" % (g, n)
    return out


ER.collisions = _collisions


import export_ilha_lua as XL


def main():
    print("EXPORT_ILHA: %d materiais Glow -> Neon" % XL.neon_rules())
    n_gal = drop_gallery()
    for o in [o for o in bpy.data.objects if o.name.startswith("COL_MineOre")]:
        bpy.data.objects.remove(o, do_unlink=True)
    n_w = to_world()
    vfx = XL.vfx_list(ER)
    ER.EXTRA_LUA = XL.extra_lua(ER, vfx)
    print("EXPORT_ILHA: galeria fora (%d objetos), %d raizes levadas ao mundo, %d pecas moveis" % (n_gal, n_w, len(vfx)))
    ER.main()
    # resumo da conexao com as proximas ilhas (Roblox)
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        want = {"WORLD_FROM_LOBBY", "WORLD_ENTRY_Naruto", "ISLAND_EXIT_Naruto", "ISLAND_NEXT_ANCHOR", "GATE_DB",
                "SUMMON_Main"}
        con = {m["name"]: m for m in data["markers"] if m["name"] in want}
        json.dump(con, open(os.path.join(OUT, "conexao_roblox.json"), "w", encoding="utf-8"), indent=1)
        for k in sorted(con):
            print("CONEXAO %-22s pos %s  eixoY %s" % (k, con[k]["pos"], con[k]["y"]))
    except Exception as e:
        print("CONEXAO: nao consegui resumir:", e)


main()
