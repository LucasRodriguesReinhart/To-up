# export_all.py - exportacao COMPLETA do Lobby Vila-Forja para o Roblox, num passe so:
#   1) export_roblox.main()  -> LOBBY_<colecao>*.fbx, lobby_data.json, montar_lobby_forja.lua        (estatico)
#   2) export_vfx.main()     -> LOBBY_VFX_MOVING*.fbx, vfx_lobby_forja.lua, vfx_lobby_forja_client.lua (movimento)
# no MESMO processo e na MESMA pasta: os nomes das variantes (Wood_Dark_B...) e o EXPORT_ID batem, e a montagem do
# VFX recusa um lobby de outro passe (root:GetAttribute('EXPORT_ID') ~= DATA.exportId). Rode sempre este em vez dos
# dois separados.
# uso: blender -b lobby_forja_mineradora.blend --python export_all.py [-- <pasta_saida>]   (padrao ./export)
import sys, os, json, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# a pasta de saida vale para os dois exportadores (o export_roblox so le o argv quando roda sozinho)
_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if _argv:
    os.environ["FM_EXPORT_DIR"] = os.path.abspath(_argv[0])
import export_roblox as ER
if _argv:
    ER.OUT = os.environ["FM_EXPORT_DIR"]
os.environ["FM_VFX_OUT"] = ER.OUT
import export_vfx as EV
EV.OUT = ER.OUT

os.makedirs(ER.OUT, exist_ok=True)
for old in glob.glob(os.path.join(ER.OUT, "LOBBY_VFX_MOVING*.fbx")):
    os.remove(old)          # nunca deixa um FBX de movimento de outro passe ao lado do estatico novo
ER.main()
export_id = None
try:
    with open(os.path.join(ER.OUT, "lobby_data.json"), encoding="utf-8") as fh:
        export_id = json.load(fh).get("export_id")
except (OSError, ValueError):
    pass
ctx = EV.main(export_id=export_id)
print("EXPORT ALL OK -> %s (EXPORT_ID %s)" % (ER.OUT, ctx.get("export_id") or "-"))
