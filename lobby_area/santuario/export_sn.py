# export_sn.py - exporta o lobby SANTUARIO DO DEUS-FERREIRO para o Roblox reaproveitando o export_roblox COMPARTILHADO
# (lobby_area/forja_mineradora/export_roblox.py e fm_lib: SO LEITURA, so configurados aqui; mesmo metodo do export_wb).
# uso: blender -b --factory-startup <build.blend> --python export_sn.py [-- <pasta_saida>]
#      (padrao lobby_area/santuario/export). SN_BUDGET=warn grava mesmo com orcamento estourado (padrao strict).
# Saida: LOBBY_SN_<colecao>_<ID6>.fbx + lobby_sn_data.json + montar_lobby_santuario.lua com raiz LOBBY_FORJA (os
# scripts do jogo procuram esse nome) + CONTRATO (Santuario.Portal1..6 com Disco/AreaId, LobbyRevision, GlobalTop100
# levado para as Tabuas dos Campeoes, posicoes do jogo) + VFX (particulas nos marcadores) + perfil de luz.
# Pintura assada: cada material SNB_<atlas> vira uma "textura" do export (PNG de textures/baked ligada no Base Color
# do FBX); o montar le o id que o 3D Importer subir para cada atlas.
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sn_lib as SL
import bpy
import sn_layout as L
from wb_lib import RB

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export")
os.environ["FM_EXPORT_DIR"] = OUT
os.environ["FM_BUDGET"] = os.environ.get("SN_BUDGET", "strict")
SL.register()
import fm_lib
import fm_mat_textures as TX
import export_roblox as ER
import sn_lights

# ------------------------------------------------------------------ atlas assados -> "texturas" do export
BAKED = os.path.join(HERE, "textures", "baked")
SNB = {}
for m in bpy.data.materials:
    if m.name.startswith("SNB_") and m.users:
        key = m.name.lower()
        png = os.path.join(BAKED, m.name + ".png")
        if not os.path.exists(png):
            print("AVISO: atlas sem PNG", m.name)
            continue
        SNB[key] = png
        TX.TEXTURES[key] = (os.path.basename(png), 1.0)
        fm_lib.MATS[m.name] = (fm_lib.S(255, 255, 255), 0.85, 0.0, 0, None, 0.0)
        if (m.name, key) not in fm_lib.TEX_RULES:
            fm_lib.TEX_RULES = ((m.name, key),) + tuple(fm_lib.TEX_RULES)
if ("SNB_", "SmoothPlastic", 0.0, True) not in fm_lib.RBX_RULES:
    fm_lib.RBX_RULES.insert(0, ("SNB_", "SmoothPlastic", 0.0, True))
_ens, _path = TX.ensure, TX.path


def _ensure(force=False, out_dir=None):
    hold = {k: TX.TEXTURES.pop(k) for k in list(TX.TEXTURES) if k in SNB}
    try:
        paths = _ens(force, out_dir)
    finally:
        TX.TEXTURES.update(hold)
    paths.update(SNB)
    return paths


def _p(key):
    return SNB[key] if key in SNB else _path(key)


TX.ensure, TX.path = _ensure, _p
print("ATLAS ASSADOS registrados:", len(SNB))

ER.OUT = OUT
ER.BUDGET_MODE = os.environ["FM_BUDGET"].lower()
ER.FBX_PREFIX = "LOBBY_SN"
ER.ROOT_NAME = "LOBBY_FORJA"
ER.DATA_FILE = "lobby_sn_data.json"
ER.LUA_FILE = "montar_lobby_santuario.lua"
ER.SERVER_SCRIPT = "LOBBY_FORJA_Servidor"
ER.MARKER_COLL = "15_GAMEPLAY_MARKERS"
ER.SPAWN_FALLBACK = False
ER.TITLE = "lobby Santuario do Deus-Ferreiro"
ER.GROUPS = ["02_TERRAIN", "03_TOWN", "04_FORGE", "05_SERVICES", "06_PORTALS", "07_EXIT", "09_VEGETATION"]
ER.SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "QA_", "PREVIEW_", "CAM_", "NPC_", "TMP_", "WB_VegK_")
ER.SKIP_NAMES = set()
ER.OWNERS = [("WB_Ter_", "terrain"), ("WB_Bg_", "backdrop"), ("WB_Town_", "town"), ("WB_Prop_", "props"),
             ("WB_Frg_", "forge"), ("WB_Shop_", "services"), ("WB_Rank_", "services"), ("PORTAL_", "portals"),
             ("WB_Court_", "portals"), ("WB_Exit_", "exit"), ("WB_Veg_", "vegetation")]
ER.BUDGET_OWNER = {"terrain": (40000, 60), "backdrop": (70000, 40), "town": (30000, 40), "props": (45000, 60),
                   "forge": (90000, 90), "services": (95000, 110), "portals": (110000, 170), "exit": (70000, 90),
                   "water": (6000, 8), "vegetation": (230000, 200)}
ER.BUDGET = {"static_tris": 760000, "static_meshes": 950, "vfx_tris": 12000, "vfx_meshes": 24, "total_tris": 772000,
             "total_meshes": 974, "materials": 150, "shadow_meshes": 380, "day_lights": 30, "col": 1100}
ER.FAR_GROUND = None
# rede de quedas: ilha dos portais (x -306..) + plato (..150, z -164..150) + ponte ate z 222; topo em -23
ER.VOID_CATCH = {"size": [480, 4, 420], "y": -25.0, "center": (-80.0, -29.0)}    # center = (x, y) Blender
ER.SKYLINE_WHOLE = ("WB_Bg_",)
ER.SKYLINE_MODEL = ("WB_Bg_",)
ER.BACKGROUND = ("WB_Bg_",)
ER.CARVED = ("__nenhum__",)
ER.SHELL_OBJ = ("WB_Shop_Temple", "WB_Rank_Tablets", "WB_Frg_Hall")
ER.CAM_COL_AREAS = {"Shop": 5.0, "Rank": 5.0, "Exit": 5.0, "Court": 5.0}
ER.NIGHT_ONLY = ER.NIGHT_ONLY + (sn_lights.NIGHT,)
ER.FOLD_PROTECT = ER.FOLD_PROTECT + ("SNB_", "SN_Lava", "SN_Rune", "SN_Crystal", "SN_Mountain", "SN_Hills", "WB_Fire",
                                     "WB_FireCore", "WB_Water", "SN_PineFar")
ER.lighting_cfg = sn_lights.lighting_cfg
_lights_er = ER.lights


def _lights_sn():
    out, demoted = _lights_er()
    sn_lights.apply_rbx(out)
    return out, demoted


ER.lights = _lights_sn


def safe_candidates():
    pts = [("SAFE_Spawn", L.SPAWN, L.Y_SPAWN), ("SAFE_Praca", (0, 0), L.Y_PLAZA), ("SAFE_PracaN", (0, -30), L.Y_PLAZA),
           ("SAFE_Forja", (-0.9, -44.0), L.Y_PLAZA), ("SAFE_Loja", L.SHOP_PLAYER, L.Y_SHOP),
           ("SAFE_Tabuas", (L.RANK_O[0] + L.RANK_FACE[0] * 15.0, L.RANK_O[1] + L.RANK_FACE[1] * 15.0), L.Y_RANK),
           ("SAFE_Avenida", (0, 110), L.Y_PLAZA), ("SAFE_Portao", (0, 150), L.Y_PLAZA),
           ("SAFE_Ponte1", (0, 185), L.Y_PLAZA - 0.5), ("SAFE_Ponte2", (0, 215), L.Y_ISLE + 0.2),
           ("SAFE_IlhaPatio", L.PORTAL_HUB, L.Y_PLAZA), ("SAFE_TrilhaOeste", (-100.0, 10.0), L.Y_GRASS)]
    for i in range(6):
        (x, z), (fx, fz) = L.portal_pos(i)
        pts.append(("SAFE_Portal%d" % (i + 1), (x + fx * 12.0, z + fz * 12.0), L.Y_PORTAL))
    return [(n, (x, -z), y) for n, (x, z), y in pts]


ER.SAFE_CANDIDATES = safe_candidates


def atomic(name):
    if name.startswith("WB_Frg_"):
        return "SN_Forja"
    if name.startswith("WB_Shop_"):
        return "SN_Loja"
    if name.startswith("WB_Rank_"):
        return "SN_Tabuas"
    if name.startswith("WB_Exit_Gate"):
        return "SN_Portao"
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
    A("-- ================= CONTRATO DO JOGO (lobby Santuario do Deus-Ferreiro) =================")
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
    A("  r:SetAttribute('Santuario', EXPORT_ID); r.Parent = root end")
    A("-- GlobalTop100 (quadros Forca/Moedas): a GEOMETRIA e do Top100Builder/Controller; aqui so a ORIGEM nova (Tabuas")
    A("-- dos Campeoes, sudeste da praca). Se o modelo ja existe dentro do LOBBY_FORJA, e levado inteiro para la (PivotTo).")
    A("local TOP100_CF = CFrame.lookAt(Vector3.new(%.3f, %.3f, %.3f), Vector3.new(%.3f, %.3f, %.3f)) * CFrame.Angles(0, math.pi, 0)"
      % (ox, L.Y_RANK, oz, ox + fx, L.Y_RANK, oz + fz))
    A("root:SetAttribute('Top100Origin', TOP100_CF + ROOT_OFFSET)")
    A("do local t = root:FindFirstChild('GlobalTop100')")
    A("  if t and t:IsA('Model') then t:PivotTo(TOP100_CF + ROOT_OFFSET); print('GlobalTop100 levado as Tabuas dos Campeoes')")
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
    sfx, sfz = L.SHOP_FACE
    yaw = math.atan2(-sfx, -sfz)
    A("  local npcs = workspace:FindFirstChild('NPCs'); local v = npcs and npcs:FindFirstChild('npc vendedor ')")
    A("  mv(v, CFrame.new(%s, %s, %s) * CFrame.Angles(0, %.4f, 0) + ROOT_OFFSET, 'npc vendedor ')" % (nx, L.Y_SHOP + 3.0, nz, yaw))
    A("end")
    A("print(string.format('CONTRATO: Santuario com %d portais, LobbyRevision %s', #PORTAIS, EXPORT_ID))")
    A(sn_lights.vfx_lua())
    A(LETREIRO_LUA)
    A(PINTURA_LUA)
    return "\n".join(s) + "\n"


LETREIRO_LUA = r"""
-- ================= placas flutuantes das estacoes (marcadores LETREIRO_* com atributo 'texto') =================
do
  local n = 0
  for _, mk in ipairs(MKF:GetChildren()) do
    local txt = mk:GetAttribute('texto')
    if txt and string.sub(mk.Name, 1, 9) == 'LETREIRO_' then
      local old = mk:FindFirstChildOfClass('BillboardGui'); if old then old:Destroy() end
      local bg = Instance.new('BillboardGui'); bg.Name = 'Letreiro'; bg.Size = UDim2.new(0, 18 + 11 * #txt, 0, 44)
      bg.MaxDistance = mk:GetAttribute('alcance') or 170; bg.AlwaysOnTop = false; bg.LightInfluence = 0.3
      local fr = Instance.new('Frame'); fr.Size = UDim2.fromScale(1, 1); fr.BackgroundColor3 = Color3.fromRGB(46, 40, 52)
      fr.BackgroundTransparency = 0.12; fr.BorderSizePixel = 0; fr.Parent = bg
      local uc = Instance.new('UICorner'); uc.CornerRadius = UDim.new(0, 10); uc.Parent = fr
      local st = Instance.new('UIStroke'); st.Color = Color3.fromRGB(244, 196, 98); st.Thickness = 2.5; st.Parent = fr
      local tl = Instance.new('TextLabel'); tl.Size = UDim2.new(1, -16, 1, -8); tl.Position = UDim2.new(0, 8, 0, 4)
      tl.BackgroundTransparency = 1; tl.Text = txt; tl.TextColor3 = Color3.fromRGB(255, 232, 170); tl.TextScaled = true
      tl.Font = Enum.Font.FredokaOne; tl.TextStrokeTransparency = 0.4; tl.TextStrokeColor3 = Color3.fromRGB(30, 18, 10)
      tl.Parent = fr
      bg.Parent = mk; n += 1
    end
  end
  print(string.format('Letreiros das estacoes: %d', n))
end
"""


PINTURA_LUA = r"""
-- ================= PINTURA ASSADA: os atlas SNB_* (e a serra/colinas pintadas) sao ColorMap COMPLETOS =================
-- o bloco de materiais acima so poe textura de detalhe com RICO = true; aqui o atlas entra SEMPRE como TextureID (a cor
-- da MeshPart e branca, entao o TextureID mostra a pintura como foi assada).
do
  local n, falta = 0, {}
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA('MeshPart') then
      local m = entrada(d)
      local key = m and m.x
      if key and (string.sub(key, 1, 4) == 'snb_' or key == 'sn_mountain' or key == 'sn_hills') then
        local id = TEX[key]
        if id and id ~= '' then
          local sa = d:FindFirstChildOfClass('SurfaceAppearance'); if sa then sa:Destroy() end
          d.TextureID = id; d.Color = Color3.new(1, 1, 1); n += 1
        else falta[key] = true end
      end
    end
  end
  local fl = {} for k in pairs(falta) do table.insert(fl, k) end
  print(string.format('PINTURA ASSADA: %d MeshParts com o atlas; sem id: %s', n, #fl > 0 and table.concat(fl, ', ') or 'nenhum'))
end
-- placas oficiais do jogo (CircularUI: MUNDOS / MOCHILAS / IGNIS) nas estacoes novas; sem letreiro duplicado
do
  local cu = root:FindFirstChild('CircularUI')
  if cu then
    local function at(n, p) local a = cu:FindFirstChild(n); if a and a:IsA('BasePart') then a.CFrame = CFrame.new(p + ROOT_OFFSET) end end
    at('Mundos', Vector3.new(MX_, 39, MZ_))
    at('Mochilas', Vector3.new(SX_, 35, SZ_))
    at('Ignis', Vector3.new(-0.9, 24, -52))
    for _, nm in ipairs({'LETREIRO_Ilha', 'LETREIRO_Loja', 'LETREIRO_Ignis'}) do
      local mk = MKF:FindFirstChild(nm); local bg = mk and mk:FindFirstChildOfClass('BillboardGui'); if bg then bg:Destroy() end
    end
    print('CircularUI: placas MUNDOS/MOCHILAS/IGNIS posicionadas')
  end
end
""".replace("MX_", "%.3f" % L.PORTAL_ISLE_C[0]).replace("MZ_", "%.3f" % L.PORTAL_ISLE_C[1]).replace(
    "SX_", "%.3f" % (L.SHOP_C[0] + L.SHOP_FACE[0] * 12.0)).replace("SZ_", "%.3f" % (L.SHOP_C[1] + L.SHOP_FACE[1] * 12.0))


def main():
    gone = [o for o in bpy.data.objects if o.name.startswith(("QA_", "PREVIEW_", "SCALE_", "CAM_"))]
    for o in gone:
        bpy.data.objects.remove(o, do_unlink=True)
    print("EXPORT_SN: %d volumes de QA / previas / cameras fora do export" % len(gone))
    # nomes curtos: o export nomeia "objeto__material" e os objetos do Build ja terminam em "__material" (nome dobrado,
    # ate 50 caracteres - o 3D Importer corta nomes longos com "..."): "A__B" -> "A" / "A_01" ...
    fam = {}
    for o in bpy.data.objects:
        if o.type == "MESH" and "__" in o.name and o.users_collection and not o.name.startswith(ER.SKIP_PREFIX):
            fam.setdefault(o.name.split("__")[0], []).append(o)
    for a_, obs in fam.items():
        for i, o in enumerate(sorted(obs, key=lambda o: o.name)):
            o.name = "%s_%02d" % (a_, i) if i else a_
    print("EXPORT_SN: %d familias de objetos renomeadas (nomes curtos)" % len(fam))
    ER.EXTRA_LUA = contract_lua()
    os.makedirs(OUT, exist_ok=True)
    ER.main()
    try:
        data = json.load(open(os.path.join(OUT, ER.DATA_FILE), encoding="utf-8"))
        print("EXPORT_SN: %d malhas, %d tris, %d COL, %d marcadores, %d luzes; id %s" % (
            len(data["meshes"]), sum(m["tris"] for m in data["meshes"]), len(data["collisions"]), len(data["markers"]),
            len(data["lights"]), data["export_id"]))
    except Exception as e:
        print("EXPORT_SN: resumo falhou:", e)


main()
