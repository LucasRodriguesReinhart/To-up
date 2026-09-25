# export_portoes.py - exporta UM portao de compra como asset avulso (para encaixar na saida de qualquer ilha).
# uso: blender -b ilha_naruto.blend --python export_portoes.py -- <Chave> [<pasta_saida>]
#      Chave: DB | ShadowGarden | DemonSlayer | OnePiece | OnePunchMan     (padrao: export/portoes/<Chave>)
#      IL_BUDGET=warn grava mesmo com orcamento estourado
# O portao sai CENTRADO: o marcador GATE_<Chave> vira a origem e o avanco (+Y do portao) vira o LookVector (-Z) do
# Roblox. No Studio, depois do montar:
#     workspace.PORTAO_<Chave>:PivotTo(CFrame.lookAt(pos, pos + avanco))
# pos = centro do vao no nivel do piso; avanco = direcao de quem atravessa (ex.: atributos fwd_x/fwd_z de uma ancora).
# Sai tudo junto (malhas, colisoes, marcadores GATE_/PURCHASE_UI_ANCHOR_, luzes, pecas moveis) e o contrato
# LOCKED/UNLOCKED e o mesmo da ilha (tag PortaoCompra + ReplicatedStorage.PortoesCompra).
import sys, os, re, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
KEY = argv[0] if argv else "DB"
OUT = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(HERE, "export", "portoes", KEY)
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("IL_BUDGET", "strict")
import export_roblox as ER
import export_ilha_lua as XL
ER.OUT = OUT
ER.BUDGET_MODE = os.environ["FM_BUDGET"].lower()

PAT = re.compile(r"^(GATE_%s(_|$)|VFX_GATE_%s_|COL_Gate%s|PURCHASE_UI_ANCHOR_%s$|L_Gate_?%s)" % ((re.escape(KEY),) * 5))


def main():
    root = bpy.data.objects.get("GATE_%s" % KEY)
    if root is None:
        print("PORTAO: marcador GATE_%s nao existe neste .blend" % KEY)
        sys.exit(2)
    keep = {o.name for o in bpy.data.objects if PAT.match(o.name)}
    for o in list(bpy.data.objects):
        if o.name in keep or o.name.startswith("SUN_"):
            continue
        bpy.data.objects.remove(o, do_unlink=True)
    inv = root.matrix_world.inverted()
    for o in list(bpy.data.objects):
        if o.parent is None and not o.name.startswith("SUN_"):
            o.matrix_world = inv @ o.matrix_world
    for o in bpy.data.objects:
        if "pivot" in o.keys():
            o["pivot"] = tuple(inv @ Vector(o["pivot"]))
        if "axis" in o.keys():
            o["axis"] = tuple(inv.to_3x3() @ Vector(o["axis"]))
    bpy.context.view_layer.update()
    ER.FBX_PREFIX = "PORTAO_%s" % KEY
    ER.ROOT_NAME = "PORTAO_%s" % KEY
    ER.DATA_FILE = "portao_%s.json" % KEY
    ER.LUA_FILE = "montar_portao_%s.lua" % KEY
    ER.SERVER_SCRIPT = "PORTAO_%s_Servidor" % KEY
    ER.MARKER_COLL = "14_GAMEPLAY_MARKERS"
    ER.SPAWN_FALLBACK = False
    ER.NET = False
    ER.TITLE = "portao"
    ER.GROUPS = ["08_PURCHASE_GATES", "12_VFX_HELPERS"]
    ER.SKIP_PREFIX = ("COL_", "SCALE_", "GATEGAL_", "CAM_")
    ER.OWNERS = [("GATE_", "portao"), ("VFX_", "vfx")]
    ER.BUDGET_OWNER = {"portao": (26000, 36), "vfx": (6000, 12)}
    ER.BUDGET = {"static_tris": 32000, "static_meshes": 48, "vfx_tris": 0, "vfx_meshes": 0, "total_tris": 32000,
                 "total_meshes": 48, "materials": 40, "shadow_meshes": 30, "day_lights": 4, "col": 60}
    ER.FAR_GROUND = None
    ER.VOID_CATCH = {"size": [1, 1, 1], "y": -9999.0, "center": (0.0, 0.0)}
    ER.SAFE_CANDIDATES = lambda: []
    ER.SKYLINE_WHOLE = ("__nenhum__",)
    ER.SKYLINE_MODEL = ("__nenhum__",)
    ER.BACKGROUND = ("__nenhum__",)
    ER.NO_FOLD_OBJ = ("VFX_",)
    ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Summon_", "DB_Energy", "Metal_Gold")
    ER.atomic_model = lambda name: "PORTAO"
    vfx = XL.vfx_list(ER)
    ER.EXTRA_LUA = XL.extra_lua(ER, vfx)
    print("PORTAO %s: %d objetos, %d pecas moveis" % (KEY, len(bpy.data.objects), len(vfx)))
    ER.main()


main()
