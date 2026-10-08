# export_wb.py - exporta o lobby WOLFBERG para o Roblox reaproveitando o export_roblox COMPARTILHADO
# (lobby_area/forja_mineradora/export_roblox.py e fm_lib: SO LEITURA, so configurados aqui; mesmo metodo do export_vm).
# uso: blender -b --factory-startup lobby_wolfberg.blend --python export_wb.py [-- <pasta_saida>]
#      (padrao lobby_area/wolfberg/export). WB_BUDGET=warn grava mesmo com orcamento estourado (padrao strict).
# Saida: LOBBY_WB_<colecao>_<ID6>.fbx + lobby_wb_data.json + montar_lobby_wolfberg.lua com raiz LOBBY_FORJA (os
# scripts do jogo procuram esse nome) + CONTRATO (Santuario.Portal1..6 com Disco/AreaId, LobbyRevision, GlobalTop100
# levado para o Mural, posicoes do jogo) + VFX (particulas nos marcadores) + perfil de luz (APLICAR_LIGHTING).
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_lib as W
import bpy
import wb_layout as L
from wb_lib import RB

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("WB_BUDGET", "strict")
W.register()
import export_roblox as ER
try:
    import fm_portals                 # One Piece: materiais registrados no import (portais aprovados)
except Exception as e:
    print("fm_portals nao importado:", e)
import wb_lights

ER.OUT = OUT
ER.BUDGET_MODE = os.environ["FM_BUDGET"].lower()
ER.FBX_PREFIX = "LOBBY_WB"
ER.ROOT_NAME = "LOBBY_FORJA"
ER.DATA_FILE = "lobby_wb_data.json"
ER.LUA_FILE = "montar_lobby_wolfberg.lua"
ER.SERVER_SCRIPT = "LOBBY_FORJA_Servidor"
ER.MARKER_COLL = "15_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "lobby Wolfberg"
ER.GROUPS = ["02_TERRAIN", "03_TOWN", "04_FORGE", "05_SERVICES", "06_PORTALS", "07_EXIT", "09_VEGETATION"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "QA_", "PREVIEW_", "CAM_", "NPC_", "TMP_")
ER.SKIP_NAMES = set()
ER.OWNERS = [("WB_Ter_", "terrain"), ("WB_Bg_", "backdrop"), ("WB_Town_", "town"), ("WB_House_", "houses"),
             ("WB_Frg_", "forge"), ("WB_Shop_", "services"), ("WB_Rank_", "services"), ("PORTAL_", "portals"),
             ("WB_Court_", "portals"), ("WB_Exit_", "exit"), ("WB_Veg_", "vegetation"), ("WB_Prop_", "props")]
ER.BUDGET_OWNER = dict(L.BUDGET_OWNER)
ER.BUDGET = dict(L.BUDGET)
ER.FAR_GROUND = None
# rede de quedas: plato (x -218..134, z -136..154) + ponte ate z 222; topo em -23
ER.VOID_CATCH = {"size": [400, 4, 400], "y": -25.0, "center": (-42.0, -43.0)}      # center = (x, y) Blender
ER.SKYLINE_WHOLE = ("WB_Bg_",)
ER.SKYLINE_MODEL = ("WB_Bg_",)
ER.BACKGROUND = ("WB_Bg_",)
ER.CARVED = ("__nenhum__",)
ER.SHELL_OBJ = ("WB_Shop_Building", "WB_Frg_Hall", "WB_Rank_Hall")
ER.CAM_COL_AREAS = {"Shop": 5.0, "Forge": 5.0, "House": 5.0, "Rank": 5.0, "Exit": 5.0}
ER.NIGHT_ONLY = ER.NIGHT_ONLY + (wb_lights.NIGHT,)
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("WB_Fire", "WB_Ember", "WB_LampGlow", "WB_Ingot", "WB_Glass", "WB_Water",
                                     "WB_Cloth_", "WB_Flower", "WB_SignText", "WB_Canvas", "WB_Snow", "WB_FarMountain")
ER.lighting_cfg = wb_lights.lighting_cfg
_lights_er = ER.lights


def _lights_wb():
    out, demoted = _lights_er()
    wb_lights.apply_rbx(out)
    return out, demoted


ER.lights = _lights_wb


def safe_candidates():
    pts = [("SAFE_Spawn", (0, 32), L.Y_PAVE), ("SAFE_Praca", (0, 0), L.Y_PAVE), ("SAFE_PracaNW", (-20, -30), L.Y_PAVE),
           ("SAFE_Loja", (48, -9), L.Y_PAVE), ("SAFE_Mural", (-30, -11), L.Y_PAVE), ("SAFE_RuaOeste", (-66, 44), L.Y_PAVE),
           ("SAFE_PatioEntrada", (-100, 58), L.Y_PAVE), ("SAFE_Patio", (-134, 62), L.Y_PAVE),
           ("SAFE_RuaSul1", (0, 80), L.Y_PAVE), ("SAFE_RuaSul2", (0, 120), L.Y_PAVE), ("SAFE_Portao", (0, 150), L.Y_PAVE),
           ("SAFE_Ponte1", (0, 185), L.Y_PAVE - 0.5), ("SAFE_Ponte2", (0, 210), L.Y_ISLE + 0.2),
           ("SAFE_Forja", (0, -44), L.Y_PAVE)]
    for i in range(6):
        (x, z), (fx, fz) = L.portal_pos(i)
        pts.append(("SAFE_Portal%d" % (i + 1), (x + fx * 9.0, z + fz * 9.0), L.Y_PORTAL))
    return [(n, (x, -z), y) for n, (x, z), y in pts]


ER.SAFE_CANDIDATES = safe_candidates


def atomic(name):
    if name.startswith("WB_Frg_"):
        return "WB_Forja"
    if name.startswith("WB_Shop_"):
        return "WB_Loja"
    if name.startswith("WB_Rank_"):
        return "WB_Mural"
    if name.startswith("WB_Exit_Gate"):
        return "WB_Portao"
    m = re.match(r"^(WB_House_[A-Za-z0-9]+)", name)
    if m:
        return m.group(1)
    if name.startswith("PORTAL_"):
        return "PORTAL_" + name.split("_")[1]
    return ""


ER.atomic_model = atomic


# ------------------------------------------------------------------ bloco de contrato (Lua)
def contract_lua():
    rows = []
    for i, (key, aid) in enumerate(L.PORTALS):
        o = bpy.data.objects.get("PORTAL_" + key)
        (nx, nz), (fx, fz) = L.portal_pos(i)
        if o is not None:
            v = o.matrix_world.translation
            p = (v.x, v.z, -v.y)
        else:
            p = (nx, L.Y_PORTAL + 11.2, nz)
        c = (p[0] + fx * 1.3, p[1], p[2] + fz * 1.3)
        rows.append("  {%d, '%s', %d, Vector3.new(%.3f, %.3f, %.3f), Vector3.new(%.4f, 0, %.4f)}," % (
            i + 1, key, aid, c[0], c[1], c[2], fx, fz))
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    n = math.hypot(fx, fz)
    fx, fz = fx / n, fz / n
    lay = L.LOBBY_LAYOUT
    s = []
    A = s.append
    A("-- ================= CONTRATO DO JOGO (lobby Wolfberg) =================")
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
    A("do local r = root:FindFirstChild('LobbyRevision') or Instance.new('Folder'); r.Name = 'LobbyRevision'")
    A("  r:SetAttribute('Wolfberg', EXPORT_ID); r.Parent = root end")
    A("-- GlobalTop100 (quadros Forca/Moedas): a GEOMETRIA e do Top100Builder/Controller; aqui so a ORIGEM nova (Mural dos")
    A("-- Campeoes, oeste da praca). Se o modelo ja existe dentro do LOBBY_FORJA, e levado inteiro para la (PivotTo).")
    A("local TOP100_CF = CFrame.lookAt(Vector3.new(%.3f, %.3f, %.3f), Vector3.new(%.3f, %.3f, %.3f)) * CFrame.Angles(0, math.pi, 0)"
      % (ox, L.Y_RANK, oz, ox + fx, L.Y_RANK, oz + fz))
    A("root:SetAttribute('Top100Origin', TOP100_CF + ROOT_OFFSET)")
    A("do local t = root:FindFirstChild('GlobalTop100')")
    A("  if t and t:IsA('Model') then t:PivotTo(TOP100_CF + ROOT_OFFSET); print('GlobalTop100 levado ao Mural dos Campeoes')")
    A("  else print('GlobalTop100 ausente: construa com Top100Builder.Build(root, {OriginCF = root:GetAttribute(\"Top100Origin\")})') end end")
    A("-- POSICOES DO JOGO (POSICIONAR_JOGO = true move os objetos soltos; o Core.LobbyLayout e trocado a mao/MCP):")
    for k in ("Spawn", "Shop", "ShopFacing", "Ignis", "PortalIsland"):
        A("--   LobbyLayout.%-12s = Vector3.new(%s, %s, %s)" % ((k,) + tuple(lay[k])))
    A("local POSICIONAR_JOGO = true")
    A("if POSICIONAR_JOGO then")
    A("  local function mv(inst, cf, what) if inst then pcall(function() if inst:IsA('Model') then inst:PivotTo(cf) else inst.CFrame = cf end end); print('posicionado', what) else print('NAO achei', what) end end")
    sx, sy, sz = L.SPAWN_LOBBY_PART
    A("  local msp = workspace:FindFirstChild('Mystical Spawn Point'); mv(msp and msp:FindFirstChild('SpawnLobby'), CFrame.new(%s, %s, %s) * CFrame.Angles(0, 0, 0) + ROOT_OFFSET, 'SpawnLobby')" % (sx, sy, sz))
    mx, my, mz = L.MAILBOX_POS
    A("  mv(workspace:FindFirstChild('MailBox'), CFrame.new(%s, %s, %s) * CFrame.Angles(0, -math.pi / 2, 0) + ROOT_OFFSET, 'MailBox')" % (mx, my + 0.4, mz))
    px, pz = L.SHOP_PLAYER
    A("  local lm = workspace:FindFirstChild('LojaMochilas'); mv(lm and lm:FindFirstChild('PadLoja'), CFrame.new(%s, %s, %s) + ROOT_OFFSET, 'PadLoja')" % (px, L.Y_SHOP + 0.1, pz))
    nx, nz = L.SHOP_NPC
    A("  local npcs = workspace:FindFirstChild('NPCs'); local v = npcs and npcs:FindFirstChild('npc vendedor ')")
    A("  mv(v, CFrame.new(%s, %s, %s) * CFrame.Angles(0, math.pi / 2, 0) + ROOT_OFFSET, 'npc vendedor ')" % (nx, L.Y_SHOP + 3.0, nz))
    A("end")
    A("print(string.format('CONTRATO: Santuario com %d portais, LobbyRevision %s', #PORTAIS, EXPORT_ID))")
    A(wb_lights.vfx_lua())
    return "\n".join(s) + "\n"


def main():
    gone = [o for o in bpy.data.objects if o.name.startswith(("QA_", "PREVIEW_", "SCALE_", "CAM_"))]
    for o in gone:
        bpy.data.objects.remove(o, do_unlink=True)
    print("EXPORT_WB: %d volumes de QA / previas / cameras fora do export" % len(gone))
    ER.EXTRA_LUA = contract_lua()
    os.makedirs(OUT, exist_ok=True)
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        print("EXPORT_WB: %d malhas, %d tris, %d COL, %d marcadores, %d luzes; id %s" % (
            len(data["meshes"]), sum(m["tris"] for m in data["meshes"]), len(data["collisions"]), len(data["markers"]),
            len(data["lights"]), data["export_id"]))
    except Exception as e:
        print("EXPORT_WB: resumo falhou:", e)


main()
