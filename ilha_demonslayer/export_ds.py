# export_ds.py - exporta a Ilha 4 (DEMON SLAYER) para o Roblox reaproveitando o export_roblox do lobby (como as Ilhas
# 1, 2 e 3; o export_roblox e o fm_lib NAO sao editados: so configurados aqui).
# uso: blender -b ilha_demonslayer.blend --python export_ds.py [-- <pasta_saida>]   (padrao ilha_demonslayer/export)
#      DS_BUDGET=warn grava mesmo com orcamento estourado (padrao strict: falha sem gravar)
# O que faz (sem salvar o .blend):
#   1. leva a ilha do referencial de projeto para o MUNDO do lobby com a matriz de encaixe (ds_layout.world_matrix):
#      W4 = T(ancora da Ilha 3) . Rz(130) . T(-WORLD_FROM_PREV). WORLD_FROM_PREV cai EXATAMENTE na
#      ISLAND_NEXT_ANCHOR_DemonSlayer da Ilha 3 em Roblox (-1534,49; 52,2; 962,44) - conferido no fim (CONEXAO);
#   2. roda export_roblox.main() com a identidade da ilha (ILHA4_<colecao>_<ID6>.fbx, ilha4_data.json,
#      montar_ilha_demonslayer.lua, Model workspace.ILHA_DEMONSLAYER, ILHA_DEMONSLAYER_Servidor desligado) + o bloco Lua
#      comum das ilhas: pecas moveis VFX_* -> tag IlhaMovel; portao One Piece -> tag PortaoCompra; guarda provisoria da
#      ancora One Piece (DS_Exit_AnchorGuard + COL_DSAnchorGuard_*) -> tag GuardaProximaIlha.
#   Proxies de minerio do blockout (DS_Clr_OreProxy) e stubs do QA NUNCA entram.
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ds_lib as DL
import bpy
from mathutils import Matrix, Vector
import ds_layout as L

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("DS_BUDGET", "strict")
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
ER.FBX_PREFIX = "ILHA4"
ER.ROOT_NAME = "ILHA_DEMONSLAYER"
ER.DATA_FILE = "ilha4_data.json"
ER.LUA_FILE = "montar_ilha_demonslayer.lua"
ER.SERVER_SCRIPT = "ILHA_DEMONSLAYER_Servidor"
ER.MARKER_COLL = "14_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "ilha4"
ER.GROUPS = ["02_TERRAIN", "03_CLEARING", "04_FORGE", "05_VILLAGE", "06_SUMMON", "07_WATER", "08_NEXT_ISLAND",
             "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "12_VFX_HELPERS", "18_ENTRY"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "NPC_", "CAM_", "PREVIEW_", "GATEGAL_", "DS_Clr_OreProxy")
ER.SKIP_NAMES = set()
ER.OWNERS = [("DS_Ter_", "terrain"), ("DS_Clr_", "terrain"), ("DS_Ent_", "entry"), ("DS_Vil_", "village"),
             ("DS_Frg_", "forge"), ("DS_Sum_", "summon"), ("DS_Exit_", "exit"), ("GATE_", "gate_op"),
             ("DS_Water_", "water"), ("VFX_", "vfx"), ("DS_Veg_", "vegetation"), ("DS_Prop_", "props")]
# tetos por dono = PLANO_DS secao 7 + ~8% de folga do export (fatias por material/celula), como na SG
# ONDA 4b (densidade do terreno: musgo escorrendo, tons de grama, manchas da clareira): terrain 99,2k/65 -> teto
# 112k/75 (acrescimo pontual combinado com o lead; total da ilha <= 590k/600 com veg +50k/+43 e props +22k/+30)
# ONDA 4b (densidade de props: ~100 lanternas de caminho leves, cercas baixas em setores, bancos/placas/lenha):
# props 25,4k/27 -> teto 48k/57 (acrescimo pontual combinado com o lead; medido no export: ~46,2k / 46)
ER.BUDGET_OWNER = {"terrain": (112000, 75), "entry": (34600, 37), "village": (118800, 113), "forge": (129600, 103),
                   "summon": (34600, 43), "exit": (25900, 32), "gate_op": (30300, 41), "water": (6500, 13),
                   "props": (48000, 57), "vegetation": (118000, 95), "vfx": (16200, 32)}
# ONDA 4b (densidade da vegetacao, agente 4b-VEG): vegetation 75,6k/76 -> teto 118k/95 (acrescimo pontual do lead;
# fileiras/molduras de arvores leves, franja das falesias, pe de muro, bambuzal 23 -> 29 touceiras)
# PLANO_DS secao 7: <= 600k tris / 650 MeshParts estaticos + reserva VFX 15k / 30
ER.BUDGET = {"static_tris": 600000, "static_meshes": 650, "vfx_tris": 15000, "vfx_meshes": 30, "total_tris": 615000,
             "total_meshes": 680, "materials": 110, "shadow_meshes": 260, "day_lights": 36, "col": 1300}
_CX, _CY = to_world_xy(10.0, 300.0)           # meio da ilha (para sombras / rede)
ER.FAR_GROUND = None                 # o mar de nuvens da area 4 e feito no cliente (em -60, so na area 4)
# rede de seguranca embaixo da ilha: abaixo da quilha (-34) e acima do mar de nuvens (-60); caixa alinhada ao mundo
# que cobre a ilha girada 130 (contorno ~600 x 390) com as duas pontes e a cabeceira
ER.VOID_CATCH = {"size": [820, 4, 820], "y": -45.0, "center": (_CX, _CY)}
ER.SKYLINE_WHOLE = ("__nenhum__",)
ER.SKYLINE_MODEL = ("__nenhum__",)
ER.BACKGROUND = ("__nenhum__",)
ER.CARVED = ("__nenhum__",)
ER.NO_FOLD_OBJ = ("VFX_",)
ER.SHELL_OBJ = ()
ER.CAM_COL_AREAS = {"DS_FrgHall": 5.0, "DS_FrgTower": 5.0, "DS_FrgWorkshop": 5.0, "DS_FrgEast": 5.0,
                    "DS_SumShelter": 5.0, "DSSumTower": 5.0}
for _h in L.HOUSES:
    ER.CAM_COL_AREAS["DS_VilHouse%s" % _h[0]] = 5.0
ER.NIGHT_ONLY = ("L_DSProp_",)
ER.LIGHT_KEEP = ("L_DSFrg", "L_DSSum", "GateOnePiece", "L_Gate_OnePiece")
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Fire_DS", "Ember_DS", "Glass_DS_Lantern", "Window_DS", "Wisteria_DS",
                                     "Metal_Gold", "Crystal_Sum", "Energy_Core", "Wood_DS_Lacquer", "Cloth_DS_Red",
                                     "P_OP_")

# ------------------------------------------------------------------ luz da boca da fornalha (override so desta ilha)
# O export compartilhado corta toda PointLight para Range <= 20 / Brightness <= 1,5 (lanterna de rua). A boca da
# fornalha e a luz principal da forja (PLANO secao 10: ~Range 28): override por prefixo, mesma leitura da energia
# (R0 = min(60; 8 + 1,1 sqrt(E)), B0 = min(4; 0,6 + E / 800)), como o INTERIOR_LIGHTS da SG.
# ACRESCIMO ONDA 3c (ds_lights, passe global de luz): a PRIMEIRA regra que casa vale, entao as especificas vem antes.
#   - boca da fornalha (L_DSFrg_FurnaceMouth, que o prefixo L_DSFrg_Furnace ja pegava) com regra propria: Range 28,
#     Brightness ate 2,0 (com E 2000 do ds_lights -> 2,0: a luz mais forte de FORA da ilha, o posto 1 do PLANO sec. 10);
#   - interiores entraveis V6 (casa principal, irori + andon) e V1 (chaya): sem override o corte 0,35 / 0,5 deixa a luz
#     do comodo em Range 7-8 / Brightness 0,4 (nao chega nas paredes de um comodo de 18-24); com override: Range 12-14,
#     Brightness ~0,6-0,7 (E 140-240 do ds_lights), ainda abaixo das janelas da forja.
INTERIOR_LIGHTS = (("L_DSFrg_FurnaceMouth", 28.0, 2.0), ("L_DSFrg_Furnace", 28.0, 2.5),
                   ("L_DSVil_V6_", 14.0, 0.8), ("L_DSVil_V1_", 12.0, 0.8))
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
        print("LUZ_DS %-26s E %6.0f  Range %5.1f -> %5.1f  Brightness %4.2f -> %4.2f" % (l["name"], e, l["range"], rng,
                                                                                     l["brightness"], br))
        l["range"], l["brightness"] = rng, br
    return out, demoted


ER.lights = _lights


def atomic(name):
    """Model Atomic por construcao/marco (streaming sem pecas pela metade)"""
    for pre in ("DS_Frg_", "DS_Sum_", "DS_Ent_", "GATE_OnePiece", "DS_Exit_AnchorGuard"):
        if name.startswith(pre):
            return pre.rstrip("_")
    m = re.match(r"^(DS_Vil_House[A-Za-z0-9]*)", name)
    return m.group(1) if m else ""


ER.atomic_model = atomic
ER.SAFE_CANDIDATES = lambda: []      # os SAFE_* sao marcadores do ds_core (o export usa os marcadores SAFE_*)
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
    n = sum(1 for c in out if c["name"].startswith("COL_GateOnePieceLock_"))
    assert n == 1, "portao OnePiece com %d colisoes de bloqueio" % n
    return out


ER.collisions = _collisions

import export_ilha_lua as XL


def extra_lua(vfx):
    s = XL.extra_lua(ER, vfx)
    s = s.replace("'^EXIT_AnchorGuard'", "'^DS_Exit_AnchorGuard'").replace(
        "string.match(d.Name, '^COL_ExitAnchorGuard_')", "string.match(d.Name, '^COL_DSAnchorGuard_')")
    s = s.replace("integracao da Ilha 2 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR)",
                  "integracao da ilha One Piece (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_OnePiece)")
    return s


def main():
    print("EXPORT_DS: %d materiais Glow -> Neon" % XL.neon_rules())
    gone = [o for o in bpy.data.objects if o.name.startswith(("DS_Clr_OreProxy", "COL_QA_"))]
    for o in gone:
        bpy.data.objects.remove(o, do_unlink=True)
    print("EXPORT_DS: %d proxies de minerio / stubs de QA removidos" % len(gone))
    n_w = to_world()
    vfx = XL.vfx_list(ER)
    ER.EXTRA_LUA = extra_lua(vfx)
    print("EXPORT_DS: %d raizes levadas ao mundo, %d pecas moveis" % (n_w, len(vfx)))
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        want = {"WORLD_FROM_PREV", "WORLD_ENTRY_DemonSlayer", "ISLAND_EXIT_DemonSlayer", "ISLAND_NEXT_ANCHOR_OnePiece",
                "GATE_OnePiece", "SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition", "MiningZone_DemonSlayer"}
        con = {m["name"]: m for m in data["markers"] if m["name"] in want}
        json.dump(con, open(os.path.join(OUT, "conexao_roblox.json"), "w", encoding="utf-8"), indent=1)
        for k in sorted(con):
            print("CONEXAO %-30s pos %s  eixoY %s" % (k, con[k]["pos"], con[k]["y"]))
        wp = con.get("WORLD_FROM_PREV")
        if wp:
            d = math.dist(wp["pos"], L.A_RBX)
            print("CONEXAO WORLD_FROM_PREV x ancora da Ilha 3 %s: distancia %.4f %s" % (list(L.A_RBX), d,
                                                                                    "OK" if d < 1e-2 else "FALHA"))
    except Exception as e:
        print("CONEXAO: nao consegui resumir:", e)


main()
