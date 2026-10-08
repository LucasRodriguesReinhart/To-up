# export_vm.py - exporta o lobby VILA MEDIEVAL para o Roblox reaproveitando o export_roblox COMPARTILHADO do lobby
# (lobby_area/forja_mineradora/export_roblox.py e fm_lib: SO LEITURA, so configurados aqui - mesmo metodo das ilhas).
# uso: blender -b --factory-startup lobby_vila_medieval.blend --python export_vm.py [-- <pasta_saida>]
#      (padrao lobby_area/vila_medieval/export). VM_BUDGET=warn grava mesmo com orcamento estourado (padrao strict).
# Saida: LOBBY_VM_<colecao>_<ID6>.fbx + lobby_vm_data.json + montar_lobby_vila_medieval.lua com raiz LOBBY_FORJA (os
# scripts do jogo procuram esse nome) + bloco de CONTRATO (Santuario.Portal1..6 com Disco/AreaId, LobbyRevision,
# GlobalTop100 levado para a origem nova, VOID_CATCH com pontos seguros da vila, Script LOBBY_FORJA_Servidor).
# Volumes de QA (QA_*), previas (PREVIEW_*), bonecos (SCALE_*) e cameras NUNCA entram.
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vm_lib as VL
import bpy
import vm_layout as L
import vm_core

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("VM_BUDGET", "strict")
import export_roblox as ER
import fm_portals                     # One Piece: materiais registrados no import
ER.OUT = OUT
ER.BUDGET_MODE = os.environ["FM_BUDGET"].lower()

# ------------------------------------------------------------------ identidade
ER.FBX_PREFIX = "LOBBY_VM"
ER.ROOT_NAME = "LOBBY_FORJA"                       # contrato: CircularEffects, Top100, PetsSeguidores, MiningLoading...
ER.DATA_FILE = "lobby_vm_data.json"
ER.LUA_FILE = "montar_lobby_vila_medieval.lua"
ER.SERVER_SCRIPT = "LOBBY_FORJA_Servidor"          # rede de quedas + grupo Personagens (mesma regra de hoje)
ER.MARKER_COLL = "15_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "lobby Vila Medieval"
ER.GROUPS = list(VL.EXPORT_GROUPS)
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "QA_", "PREVIEW_", "CAM_", "NPC_", "TMP_")
ER.SKIP_NAMES = set()
ER.OWNERS = list(VL.OWNER_PREFIX)
ER.BUDGET_OWNER = dict(L.BUDGET_OWNER)
ER.BUDGET = dict(L.BUDGET)
ER.FAR_GROUND = None                                 # CeuSombras tolera a ausencia do FAR_GROUND
# rede de quedas: cobre o plato (x -224..168, z -126..153) e a ponte (ate z 222); topo em -23 (piso 6: queda > 8)
ER.VOID_CATCH = {"size": [470, 4, 420], "y": -25.0, "center": (-28.0, -48.0)}     # center = (x, y) Blender
ER.SKYLINE_WHOLE = ("VM_Bg_",)
ER.SKYLINE_MODEL = ("VM_Bg_", "VM_Ter_Hills")
ER.BACKGROUND = ("VM_Bg_", "VM_Ter_Hills")
ER.CARVED = ("__nenhum__",)
ER.SHELL_OBJ = ("VM_Shop_Building", "VM_Frg_Hall")
ER.CAM_COL_AREAS = {"Shop": 5.0, "Forge": 5.0, "House": 5.0, "RankHall": 5.0}
ER.NIGHT_ONLY = ER.NIGHT_ONLY + ("L_VM_Lamp",)
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("Forge_Glow_VM", "Metal_VM_Bronze", "Cloth_VM", "Window_VM")
ER.SAFE_CANDIDATES = vm_core.safe_candidates


def atomic(name):
    if name.startswith("VM_Frg_"):
        return "VM_Forja"
    if name.startswith(("VM_Shop_", "VM_Rank_", "VM_Exit_Gate")):
        return name.split("_")[0] + "_" + name.split("_")[1]
    m = re.match(r"^(VM_House_[A-Za-z0-9]+)", name)
    if m:
        return m.group(1)
    if name.startswith("PORTAL_"):
        return "PORTAL_" + name.split("_")[1]
    return ""


ER.atomic_model = atomic


# ------------------------------------------------------------------ bloco de contrato (Lua)
def contract_lua():
    import fm_lib
    rows = []
    for i, (key, aid) in enumerate(L.PORTALS):
        o = bpy.data.objects.get("PORTAL_" + key)
        (nx, nz), (fx, fz) = L.portal_pos(i)
        if o is not None:
            p = VL.R(o.matrix_world.translation)
        else:
            p = (nx, L.Y_PORTAL + 11.2, nz)
        c = (p[0] + fx * 1.3, p[1], p[2] + fz * 1.3)          # Disco 1,3 a frente da espiral (como hoje)
        rows.append("  {%d, '%s', %d, Vector3.new(%.3f, %.3f, %.3f), Vector3.new(%.4f, 0, %.4f)}," % (
            i + 1, key, aid, c[0], c[1], c[2], fx, fz))
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    lay = L.LOBBY_LAYOUT
    s = []
    A = s.append
    A("-- ================= CONTRATO DO JOGO (lobby Vila Medieval) =================")
    A("-- Santuario.Portal1..6: Model com Disco (gameplay, invisivel, sem colisao, CanTouch) e atributo AreaId; o Core.Main")
    A("-- liga o Touched (Santuario precisa ser filho DIRETO de LOBBY_FORJA). O AudioWorld reconhece Portal%d em Santuario.")
    A("local PORTAIS = {")
    s.extend(rows)
    A("}")
    A("do")
    A("  local san = root:FindFirstChild('Santuario') or Instance.new('Folder'); san.Name = 'Santuario'; san.Parent = root")
    A("  for _, c in ipairs(san:GetChildren()) do if string.match(c.Name, '^Portal%d$') or c.Name == 'PortalKonoha' then c:Destroy() end end")
    A("  for _, p in ipairs(PORTAIS) do")
    A("    local m = Instance.new('Model'); m.Name = 'Portal' .. p[1]; m:SetAttribute('Tema', p[2])")
    A("    local d = Instance.new('Part'); d.Name = 'Disco'; d.Anchored = true; d.CanCollide = false; d.CanQuery = false")
    A("    d.CanTouch = true; d.CastShadow = false; d.Transparency = 1; d.Size = Vector3.new(14, 15, 1.2)")
    A("    local pos = p[4] + ROOT_OFFSET; d.CFrame = CFrame.lookAt(pos, pos + p[5]); d:SetAttribute('AreaId', p[3])")
    A("    d.Parent = m; m.PrimaryPart = d; m.Parent = san")
    A("  end")
    A("end")
    A("-- LobbyRevision (o LobbyServices exige o filho): mantem o existente, so marca a revisao")
    A("do local r = root:FindFirstChild('LobbyRevision') or Instance.new('Folder'); r.Name = 'LobbyRevision'")
    A("  r:SetAttribute('VilaMedieval', EXPORT_ID); r.Parent = root end")
    A("-- GlobalTop100 (pódios Forca/Moedas): a GEOMETRIA e do Top100Builder/Controller; aqui so a ORIGEM nova (palco do")
    A("-- ranking, oeste). Se o modelo ja existe dentro do LOBBY_FORJA, e levado inteiro para la (PivotTo).")
    A("local TOP100_CF = CFrame.lookAt(Vector3.new(%.3f, %.3f, %.3f), Vector3.new(%.3f, %.3f, %.3f)) * CFrame.Angles(0, math.pi, 0)"
      % (ox, L.Y_RANK, oz, ox + fx, L.Y_RANK, oz + fz))
    A("root:SetAttribute('Top100Origin', TOP100_CF + ROOT_OFFSET)")
    A("do local t = root:FindFirstChild('GlobalTop100')")
    A("  if t and t:IsA('Model') then t:PivotTo(TOP100_CF + ROOT_OFFSET); print('GlobalTop100 levado ao palco do ranking')")
    A("  else print('GlobalTop100 ausente: construa com Top100Builder.Build(root, {OriginCF = root:GetAttribute(\"Top100Origin\")})') end end")
    A("-- valores NOVOS do ServerScriptService.Core.LobbyLayout (o lead troca no Studio) e posicoes dos objetos soltos")
    for k in ("Spawn", "Shop", "ShopFacing", "Ignis", "PortalIsland"):
        A("--   %-12s = Vector3.new(%s, %s, %s)" % ((k,) + tuple(lay[k])))
    A("--   SpawnLobby (placa) = (%s, %s, %s); MailBox = (%s, %s, %s); Ignis Root (-0.9, 7, -60.7) olhando +Z" % (
        L.SPAWN_LOBBY_PART + L.MAILBOX_POS))
    A("print(string.format('CONTRATO: Santuario com %d portais, LobbyRevision %s', #PORTAIS, EXPORT_ID))")
    return "\n".join(s) + "\n"


def main():
    gone = [o for o in bpy.data.objects if o.name.startswith(("QA_", "PREVIEW_", "SCALE_"))]
    for o in gone:
        bpy.data.objects.remove(o, do_unlink=True)
    print("EXPORT_VM: %d volumes de QA / previas / bonecos fora do export" % len(gone))
    ER.EXTRA_LUA = contract_lua()
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        print("EXPORT_VM: %d malhas, %d tris, %d COL, %d marcadores, %d luzes; id %s" % (
            len(data["meshes"]), sum(m["tris"] for m in data["meshes"]), len(data["collisions"]), len(data["markers"]),
            len(data["lights"]), data["export_id"]))
    except Exception as e:
        print("EXPORT_VM: resumo falhou:", e)


main()
