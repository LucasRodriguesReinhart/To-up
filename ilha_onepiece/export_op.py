# export_op.py - exporta a Ilha 5 (ONE PIECE / WANO) para o Roblox reaproveitando o export_roblox do lobby (como as
# Ilhas 1 a 4; o export_roblox e o fm_lib NAO sao editados: so configurados aqui).
# uso: blender -b ilha_onepiece.blend --python export_op.py [-- <pasta_saida>]   (padrao ilha_onepiece/export)
#      OP_BUDGET=warn grava mesmo com orcamento estourado (padrao strict: falha sem gravar)
# O que faz (sem salvar o .blend):
#   1. leva a ilha do referencial de projeto para o MUNDO do lobby com a matriz de encaixe (op_layout.world_matrix):
#      W5 = T(ancora da Ilha 4) . Rz(145) . T(-WORLD_FROM_PREV). WORLD_FROM_PREV cai EXATAMENTE na
#      ISLAND_NEXT_ANCHOR_OnePiece da Ilha 4 em Roblox (-2054,391; 80,2; 1551,759) - conferido no fim (CONEXAO);
#   2. roda export_roblox.main() com a identidade da ilha (ILHA5_<colecao>_<ID6>.fbx, ilha5_data.json,
#      montar_ilha_onepiece.lua, Model workspace.ILHA_ONEPIECE, ILHA_ONEPIECE_Servidor desligado; a fonte no Studio e
#      ServerStorage.IlhaOnePiece, o nome que a Demon Slayer espera em FONTE_PROXIMA) + o bloco Lua comum das ilhas:
#      pecas moveis VFX_* -> tag IlhaMovel; portao One Punch Man -> tag PortaoCompra; guarda provisoria da ancora One
#      Punch Man (OP_Exit_AnchorGuard + COL_OPAnchorGuard_*) -> tag GuardaProximaIlha.
#   Proxies de minerio do blockout (OP_Plz_OreProxy) e stubs do QA NUNCA entram.
# ACRESCIMO M2 (agente do trecho, pontual): export SO DE UM TRECHO para validar no Studio sem a ilha inteira.
#   OP_EXPORT_ONLY=<prefixo,prefixo,...>  so as MALHAS e LUZES cujo nome comeca com um dos prefixos sao exportadas;
#                 colisoes COL_* e marcadores ficam TODOS (piso, escadas, guardas, portao e rotas funcionam no Play).
#   OP_EXPORT_TAG=<sufixo>  muda a identidade para nao colidir com a ilha: ILHA5<sufixo>_*.fbx, Model
#                 workspace.ILHA_ONEPIECE_<sufixo>, ilha5_<sufixo>_data.json, montar_ilha_onepiece_<sufixo>.lua.
#   ex.: OP_EXPORT_ONLY=OP_Cap_M2,OP_Plz_M2,OP_Ter_ OP_EXPORT_TAG=M2 ./run.sh export export_m2
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import op_lib as DL
import bpy
from mathutils import Matrix, Vector
import op_layout as L

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("OP_BUDGET", "strict")
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
            # M6c: outras listas de pontos '<algo>_waypoints' (hoje so a 'spout_waypoints' da cachoeira do castelo)
            # ficavam no referencial LOCAL e o roblox/OnePieceIsland.lua convertia sozinho. Agora o export grava TAMBEM
            # '<chave>_world' ja no mundo do Roblox; a chave local fica como estava (um OnePieceIsland antigo no Studio
            # continua certo: nao ha conversao dupla). O OnePieceIsland novo prefere a '_world' e so converte se ela
            # faltar.
            for k in [k for k in o.keys() if k.endswith("_waypoints") and isinstance(o[k], str)]:
                pts = []
                for t in str(o[k]).split(";"):
                    x, y, z = (float(v) for v in t.split(","))
                    pts.append("%.2f,%.2f,%.2f" % tuple(ER.to_rbx(WORLD @ Vector((x, y, z)))))
                o[k + "_world"] = ";".join(pts)
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
ER.FBX_PREFIX = "ILHA5"
ER.ROOT_NAME = "ILHA_ONEPIECE"
ER.DATA_FILE = "ilha5_data.json"
ER.LUA_FILE = "montar_ilha_onepiece.lua"
ER.SERVER_SCRIPT = "ILHA_ONEPIECE_Servidor"
ER.MARKER_COLL = "14_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "ilha5"
_TAG = os.environ.get("OP_EXPORT_TAG", "").strip()
if _TAG:                                       # (M2) identidade separada para o export de um trecho
    ER.FBX_PREFIX = "ILHA5" + _TAG
    ER.ROOT_NAME = "ILHA_ONEPIECE_" + _TAG
    ER.DATA_FILE = "ilha5_%s_data.json" % _TAG.lower()
    ER.LUA_FILE = "montar_ilha_onepiece_%s.lua" % _TAG.lower()
    ER.SERVER_SCRIPT = "ILHA_ONEPIECE_%s_Servidor" % _TAG
    ER.TITLE = "ilha5_" + _TAG.lower()
_ONLY = tuple(p.strip() for p in os.environ.get("OP_EXPORT_ONLY", "").split(",") if p.strip())
ER.GROUPS = ["02_TERRAIN", "03_PLAZA", "04_CASTLE", "05_CAPITAL", "06_SUMMON", "07_WATER", "08_NEXT_ISLAND",
             "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "12_VFX_HELPERS", "16_HARBOR", "17_LANDMARKS",
             "18_ENTRY"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "NPC_", "CAM_", "PREVIEW_", "GATEGAL_", "OP_Plz_OreProxy")
ER.SKIP_NAMES = set()
ER.OWNERS = [("OP_Ter_", "terrain"), ("OP_Ent_", "entry"), ("OP_Cap_", "capital"), ("OP_Plz_", "plaza"),
             ("OP_Cas_", "castle"), ("OP_Tree_", "tree"), ("OP_Port_", "harbor"), ("OP_Ship_", "ship"),
             ("OP_Sum_", "summon"), ("OP_Exit_", "exit"), ("GATE_", "gate_opm"), ("OP_Lmk_", "landmarks"),
             ("OP_Water_", "water"), ("VFX_", "vfx"), ("OP_Veg_", "vegetation"), ("OP_Prop_", "props")]
# tetos por dono = PLANO_OP secao 9 + ~8% de folga do export (fatias por material/celula), como na DS
# M4 op_plaza (acrescimo pontual): teto do plaza 21,6k -> 34k tris por decisao do lead (faixa sul do M2 ja gastava
# 17,9k; o resto do piso em aneis/eixo/campos + mureta leva a 32,5k) e 26 -> 36 MeshParts (piso de 232 x 194 fatiado
# em celulas de 128 x 4 tons de pedra; medido 30). Estandartes/postes/bancos da borda contam no dono props (OP_Prop_Plz_).
# M6c (integracao): a M6b do castelo (patio em lajes + cascalho, guardas de pedra nas subidas, torreoes e base em
# fiadas, itens 24-30 da auditoria) levou o castelo a 82,0k: teto 75,6k -> 84k, pago pela folga da capital
# (198k -> 189,6k; usa 178,3k depois do K.cull_hidden). Soma dos tetos e teto global (640k) inalterados.
ER.BUDGET_OWNER = {"terrain": (108000, 81), "entry": (32400, 35), "capital": (189600, 145), "plaza": (34000, 36),
                   "castle": (84000, 59), "tree": (43200, 32), "harbor": (41000, 43), "ship": (19400, 17),
                   "summon": (36700, 43), "exit": (19400, 26), "gate_opm": (30300, 41), "landmarks": (15100, 15),
                   "water": (10800, 17), "props": (27000, 38), "vegetation": (48600, 49), "vfx": (16200, 32)}
# PLANO_OP secao 9: <= 620k tris / 650 MeshParts estaticos + reserva VFX 15k / 30
ER.BUDGET = {"static_tris": 640000, "static_meshes": 650, "vfx_tris": 15000, "vfx_meshes": 30, "total_tris": 655000,
             "total_meshes": 680, "materials": 110, "shadow_meshes": 260, "day_lights": 36, "col": 1300}
_CX, _CY = to_world_xy(60.0, 250.0)            # meio da ilha (sombras / rede)
ER.FAR_GROUND = None                 # o mar local de Wano e feito no cliente (WATER_Sea, so na area 5)
# rede de seguranca embaixo da ilha: abaixo da quilha (-10) e do mar local (36); caixa alinhada ao mundo que cobre a
# ilha girada 145 (contorno ~590 x 500 + esporao da espada) com as pontes
ER.VOID_CATCH = {"size": [980, 4, 980], "y": -30.0, "center": (_CX, _CY)}
ER.SKYLINE_WHOLE = ("__nenhum__",)
ER.SKYLINE_MODEL = ("__nenhum__",)
ER.BACKGROUND = ("__nenhum__",)
ER.CARVED = ("__nenhum__",)
ER.NO_FOLD_OBJ = ("VFX_",)
ER.SHELL_OBJ = ()
ER.CAM_COL_AREAS = {"OP_CasKeep": 5.0, "OP_CasKeepUpper": 5.0, "OP_CasTurret": 5.0, "OP_CasGate": 5.0,
                    "OP_TreeTrunk": 5.0, "OPSumTower": 5.0, "OP_ShipCabin": 5.0}
for _b in L.BUILDINGS:
    ER.CAM_COL_AREAS[("OP_PortHouse" if _b[0].startswith("H") else "OP_CapHouse") + _b[0]] = 5.0
# M4 op_capital (acrescimo pontual): casas novas da capital (fora do L.BUILDINGS), casa de cha e pavilhoes -> camera
for _o in bpy.data.objects:
    if _o.name.startswith(("COL_OP_CapHouse", "COL_OP_CapPav", "COL_OP_CapShrineDeck")):
        ER.CAM_COL_AREAS.setdefault(re.sub(r"^COL_(.*)_\d+$", r"\1", _o.name), 5.0)
ER.NIGHT_ONLY = ("L_OPProp_", "L_OPCap_Win_")
ER.LIGHT_KEEP = ("L_OPCas", "L_OPSum", "GateOnePunchMan", "L_Gate_OnePunchMan")
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Glass_OP_Lantern", "Window_OP", "Flower_OP", "Metal_OP_Gold", "Wood_OP_Lacquer",
                                     "Metal_Gold", "Crystal_Sum", "Energy_Core", "Energy_OPM", "Cloth_OP_Red", "P_OPM_", "P_Gold_")

# ------------------------------------------------------------------ luzes de interior (override so desta ilha)
# O export compartilhado corta toda PointLight para Range <= 20 / Brightness <= 1,5 (lanterna de rua). O salao do
# terreo da torre (acessivel) precisa de luz que chegue nas paredes de um comodo de 50 x 42: override por prefixo.
# M4 op_lights (acrescimo pontual): a casa de cha (op_capital, interior acessivel 16 x 20, pe-direito 11) com o corte
# comum ficava com Range 9,0 / Brightness 0,46 para uma luz no meio do salao (as paredes do fundo a 10-11): Range 14.
INTERIOR_LIGHTS = (("L_OPCas_Hall_", 18.0, 0.8), ("L_OPCap_Int_", 14.0, 0.6))
INTERIOR_BR_K = 0.75
_ER_LIGHTS = ER.lights


def _lights():
    out, demoted = _ER_LIGHTS()
    for l in out:
        rule = next((r for r in INTERIOR_LIGHTS if l["name"].startswith(r[0])), None)
        ob = bpy.data.objects.get(l["name"])
        if rule is None or ob is None:
            continue
        e = ob.data.energy
        r0 = min(60.0, 8.0 + math.sqrt(e) * 1.1)
        b0 = min(4.0, 0.6 + e / 800.0)
        rng, br = round(min(rule[1], r0), 1), round(min(rule[2], INTERIOR_BR_K * b0), 2)
        print("LUZ_OP %-26s E %6.0f  Range %5.1f -> %5.1f  Brightness %4.2f -> %4.2f" % (l["name"], e, l["range"], rng,
                                                                                     l["brightness"], br))
        l["range"], l["brightness"] = rng, br
    return out, demoted


ER.lights = _lights


def atomic(name):
    """Model Atomic por construcao/marco (streaming sem pecas pela metade)"""
    for pre in ("OP_Cas_", "OP_Tree_", "OP_Sum_", "OP_Ent_", "OP_Ship_", "OP_Lmk_", "GATE_OnePunchMan",
                "OP_Exit_AnchorGuard"):
        if name.startswith(pre):
            return pre.rstrip("_")
    return ""


ER.atomic_model = atomic
ER.SAFE_CANDIDATES = lambda: []      # os SAFE_* sao marcadores do op_core
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
    n = sum(1 for c in out if c["name"].startswith("COL_GateOnePunchManLock_"))
    assert n == 1, "portao OnePunchMan com %d colisoes de bloqueio" % n
    return out


ER.collisions = _collisions

import export_ilha_lua as XL


def extra_lua(vfx):
    s = XL.extra_lua(ER, vfx)
    s = s.replace("'^EXIT_AnchorGuard'", "'^OP_Exit_AnchorGuard'").replace(
        "string.match(d.Name, '^COL_ExitAnchorGuard_')", "string.match(d.Name, '^COL_OPAnchorGuard_')")
    s = s.replace("integracao da Ilha 2 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR)",
                  "integracao da ilha One Punch Man (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_OnePunchMan)")
    return s


# M6c: nomes de malha <= 48 (o importador trunca com '...' acima de ~50 e o montar procura o nome exato). So o portao One
# Punch Man passava: 'GATE_OnePunchMan_Barrier__Energy_Core_OnePunchMan_Glow' (54) e '..._Lock__...' (51). O objeto
# nao muda (o montar casa '^GATE_(%w+)_(%a+)' e a chave OnePunchMan); o MATERIAL ganha um nome curto SO no export, com a
# mesma cor/regra (MATS, RBX_CAL, variante) - o asset da galeria e o Neon dele (item 50) ficam como estao.
MAT_SHORT = {"Energy_Core_OnePunchMan_Glow": "Energy_OPM_Glow"}


def short_materials():
    import fm_lib
    n = 0
    for old, new in MAT_SHORT.items():
        m = bpy.data.materials.get(old)
        if m is None:
            continue
        for tab in (fm_lib.MATS, fm_lib.RBX_CAL, getattr(fm_lib, "VARIANT_OF", {})):
            if old in tab:
                tab[new] = tab[old]
        m.name = new
        n += 1
    return n


def main():
    print("EXPORT_OP: %d materiais com nome curto (nomes de malha <= 48)" % short_materials())
    print("EXPORT_OP: %d materiais Glow -> Neon" % XL.neon_rules())
    gone = [o for o in bpy.data.objects if o.name.startswith(("OP_Plz_OreProxy", "COL_QA_"))]
    for o in gone:
        bpy.data.objects.remove(o, do_unlink=True)
    print("EXPORT_OP: %d proxies de minerio / stubs de QA removidos" % len(gone))
    if _ONLY:                                  # (M2) export so do trecho: malhas/luzes fora dos prefixos saem
        gone = [o for o in bpy.data.objects if o.type in ("MESH", "LIGHT", "CURVE") and not o.name.startswith("COL_")
                and not o.name.startswith(_ONLY)]
        for o in gone:
            bpy.data.objects.remove(o, do_unlink=True)
        print("EXPORT_OP: OP_EXPORT_ONLY=%s -> %d malhas/luzes fora do trecho removidas" % (",".join(_ONLY), len(gone)))
    n_w = to_world()
    vfx = XL.vfx_list(ER)
    ER.EXTRA_LUA = extra_lua(vfx)
    print("EXPORT_OP: %d raizes levadas ao mundo, %d pecas moveis" % (n_w, len(vfx)))
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        want = {"WORLD_FROM_PREV", "WORLD_ENTRY_OnePiece", "ISLAND_EXIT_OnePiece", "ISLAND_NEXT_ANCHOR_OnePunchMan",
                "GATE_OnePunchMan", "SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition", "MiningZone_OnePiece",
                "WATER_Sea"}
        con = {m["name"]: m for m in data["markers"] if m["name"] in want}
        json.dump(con, open(os.path.join(OUT, "conexao_roblox.json"), "w", encoding="utf-8"), indent=1)
        for k in sorted(con):
            print("CONEXAO %-32s pos %s  eixoY %s" % (k, con[k]["pos"], con[k]["y"]))
        wp = con.get("WORLD_FROM_PREV")
        if wp:
            d = math.dist(wp["pos"], L.A_RBX)
            print("CONEXAO WORLD_FROM_PREV x ancora da Ilha 4 %s: distancia %.4f %s" % (list(L.A_RBX), d,
                                                                                    "OK" if d < 1e-2 else "FALHA"))
            f = (wp["y"][0], wp["y"][2])
            print("CONEXAO frente WORLD_FROM_PREV (%.4f, %.4f) x frente da ancora (%.4f, %.4f)" % (f + (L.A_FWD[0], L.A_FWD[2])))
    except Exception as e:
        print("CONEXAO: nao consegui resumir:", e)


main()
