--[[
vfx_lobby_forja.lua   (gerado por export_vfx.py - vfx-forja-1 - nao editar a mao: ajuste export_vfx.py e reexporte)
VFX e MOVIMENTO do Lobby Vila-Forja - MONTAGEM

ONDE COLOCAR
  A) Command Bar do Studio (recomendado), UMA vez, depois de:
       1. importar LOBBY_*.fbx e rodar montar_lobby_forja.lua (colisoes, marcadores, luzes);
       2. importar export/LOBBY_VFX_MOVING.fbx com o 3D Importer (pode cair em qualquer lugar do workspace: este
          script acha as pecas pelo nome e as coloca na posicao certa, mesmo com o lobby deslocado ou girado).
     Depois salve o place: emissores, luzes, tags e atributos ficam gravados. Pode rodar de novo (idempotente).
  B) Ou como Script (nao LocalScript) em ServerScriptService: monta tudo ao iniciar o servidor.
     Nao ha nenhum loop por frame no servidor.
  E SEMPRE: vfx_lobby_forja_client.lua como LocalScript em StarterPlayer > StarterPlayerScripts. Ele gira a roda,
  as engrenagens e as espirais, bate o martinete, move o carrinho e faz pulsos/flicker - tudo no cliente.

O QUE ESTE SCRIPT CRIA
  <lobby>.VFX              pecas invisiveis com ParticleEmitters e luzes: fogo da lareira, fumaca da chamine,
                           faiscas das bigornas, respingos da roda, nevoa/espuma/fios das quedas, vortice e
                           particulas sugadas dos portais, brilhos dos cristais
  <lobby>.VFX_MOVING       modelos (streaming atomico) com as pecas moveis do LOBBY_VFX_MOVING.fbx
  ReplicatedStorage.LOBBY_FORJA_VFX       config (VFX_RootCF), molde do carrinho (MineCart), BindableEvent Evento
  ServerStorage.LOBBY_FORJA_VFX_ORIGINAIS malhas estaticas trocadas pelas versoes separadas (para desfazer, devolva)
  Tags (CollectionService): FORJA_Spin, FORJA_Hammer, FORJA_Pulse, FORJA_Flicker, FORJA_Burst, FORJA_Emitter

GANCHOS
  Rig real do Ignis: ponha a tag "FORJA_Ignis" no Model; um KeyframeMarker "Golpe" na animacao do martelo dispara
  as faiscas (parametro opcional = forca). Sem rig, o cliente usa um ritmo interno (toc-toc-TOC).
  Qualquer LocalScript: ReplicatedStorage.LOBBY_FORJA_VFX.Evento:Fire("ignis", 1.5)
  eventos: "ignis", "martinete", "portal:<Nome>", "carga"
]]

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")

local ROOT_NAMES = {"LOBBY_FORJA", "LOBBY_FORJA_PREVIEW"} -- o primeiro que existir no workspace
local RICO = false          -- mesmo valor do montar_lobby_forja.lua (so usado quando nao ha peca original para copiar)
local RECOLOR_SWIRL = true  -- disco das espirais mais saturado, para os bracos claros lerem (sem textura no Roblox)

if RunService:IsRunning() and not RunService:IsServer() then
  warn("[VFX Forja] vfx_lobby_forja.lua e a MONTAGEM (Command Bar ou Script de servidor), nao um LocalScript")
  return
end

local DATA = {}
DATA.version = 'vfx-forja-1'
-- referencias para achar a transformacao do lobby (posicao canonica = export_roblox, Roblox = (x, z, -y))
DATA.refs = {
  {name = 'VFX_Waterwheel_Rotate', pos = Vector3.new(62, 11, -20), x = Vector3.new(0, -1, 0), y = Vector3.new(0, 0, -1)},
  {name = 'NPC_Ignis', pos = Vector3.new(0, 5, 5), x = Vector3.new(-1, 0, 0), y = Vector3.new(0, 0, 1)},
  {name = 'RAIL_Start_Mine', pos = Vector3.new(-89.627, 4.02, 79.77), x = Vector3.new(1, 0, 0), y = Vector3.new(0, 0, -1)},
  {name = 'PORTAL_Naruto', pos = Vector3.new(-108, 41.2, -112.4), x = Vector3.new(1, 0, 0), y = Vector3.new(0, 0, -1)},
}
-- pecas do LOBBY_VFX_MOVING.fbx: {nome, grupo, centro do bbox (canonico)}
DATA.movers = {
  {'VFX_RodaDagua__Wood_Dark', 'roda', Vector3.new(62, 11, -19.999)},
  {'VFX_RodaDagua__Metal_Iron', 'roda', Vector3.new(62, 11, -20)},
  {'VFX_RodaDagua__Wood_Light', 'roda', Vector3.new(62, 11, -20)},
  {'VFX_RodaDagua__Metal_Dark', 'roda', Vector3.new(62, 11, -20)},
  {'VFX_RodaDagua__Wood_Plank', 'roda', Vector3.new(62, 11, -20)},
  {'VFX_RodaDaguaFixa__Wood_Dark', 'roda_fixa', Vector3.new(51.2, 8.35, -20)},
  {'VFX_RodaDaguaFixa__Metal_Iron', 'roda_fixa', Vector3.new(51.55, 13.1, -20)},
  {'VFX_RodaDaguaFixa__Wood_Plank', 'roda_fixa', Vector3.new(62, 2.4, -20)},
  {'VFX_CasaRodaEixo__Stone_Dark', 'eixo_baixo', Vector3.new(45.775, 11, -20)},
  {'VFX_CasaRodaEixo__Wood_Light', 'eixo_baixo', Vector3.new(44.4, 11, -20)},
  {'VFX_CasaRodaEixo__Metal_Dark', 'eixo_baixo', Vector3.new(44.4, 11, -20)},
  {'VFX_CasaRodaEixo__Wood_Dark', 'eixo_baixo', Vector3.new(44.4, 11, -20)},
  {'VFX_CasaRodaEixo__Metal_Iron', 'eixo_baixo', Vector3.new(47.5, 11, -20.339)},
  {'VFX_CasaRodaPinhao__Stone_Dark', 'pinhao', Vector3.new(44.4, 15.5, -20)},
  {'VFX_CasaRodaPinhao__Metal_Dark', 'pinhao', Vector3.new(44.4, 15.5, -20)},
  {'VFX_CasaRodaPinhao__Wood_Light', 'pinhao', Vector3.new(44.4, 15.5, -20)},
  {'VFX_CasaRodaPinhao__Wood_Dark', 'pinhao', Vector3.new(44.4, 15.5, -20)},
  {'VFX_CasaRodaMartinete__Stone_Dark', 'martinete', Vector3.new(47.5, 7.82, -20.568)},
  {'VFX_CasaRodaMartinete__Wood_Dark', 'martinete', Vector3.new(47.5, 8.5, -21)},
  {'VFX_CasaRodaMartinete__Metal_Dark', 'martinete', Vector3.new(47.5, 7.2, -16)},
  {'VFX_CasaRodaFixa__Stone_Dark', 'casa_fixa', Vector3.new(48.118, 14.015, -19.575)},
  {'VFX_CasaRodaFixa__Wood_Dark', 'casa_fixa', Vector3.new(48.45, 14.515, -19.75)},
  {'VFX_CasaRodaFixa__Metal_Dark', 'casa_fixa', Vector3.new(51.239, 12.825, -15.161)},
  {'VFX_CasaRodaFixa__Metal_Iron', 'casa_fixa', Vector3.new(47.5, 5.3, -16)},
  {'VFX_Espiral_Naruto__VFXP_Naruto_Braco', 'espiral_Naruto', Vector3.new(-108.001, 41.2, -113)},
  {'VFX_Espiral_Naruto__VFXP_Naruto_Nucleo', 'nucleo_Naruto', Vector3.new(-108, 41.2, -112.775)},
  {'VFX_Espiral_DragonBall__VFXP_DragonBall_Braco', 'espiral_DragonBall', Vector3.new(-76.001, 41.2, -113)},
  {'VFX_Espiral_DragonBall__VFXP_DragonBall_Nucleo', 'nucleo_DragonBall', Vector3.new(-76, 41.2, -112.775)},
  {'VFX_Espiral_ShadowGarden__VFXP_ShadowGarden_Braco', 'espiral_ShadowGarden', Vector3.new(-44.001, 41.2, -113)},
  {'VFX_Espiral_ShadowGarden__VFXP_ShadowGarden_Nucleo', 'nucleo_ShadowGarden', Vector3.new(-44, 41.2, -112.775)},
  {'VFX_Espiral_DemonSlayer__VFXP_DemonSlayer_Braco', 'espiral_DemonSlayer', Vector3.new(43.999, 41.2, -113)},
  {'VFX_Espiral_DemonSlayer__VFXP_DemonSlayer_Nucleo', 'nucleo_DemonSlayer', Vector3.new(44, 41.2, -112.775)},
  {'VFX_Espiral_OnePiece__VFXP_OnePiece_Braco', 'espiral_OnePiece', Vector3.new(75.999, 41.2, -113)},
  {'VFX_Espiral_OnePiece__VFXP_OnePiece_Nucleo', 'nucleo_OnePiece', Vector3.new(76, 41.2, -112.775)},
  {'VFX_Espiral_OnePunchMan__VFXP_OnePunchMan_Braco', 'espiral_OnePunchMan', Vector3.new(107.999, 41.2, -113)},
  {'VFX_Espiral_OnePunchMan__VFXP_OnePunchMan_Nucleo', 'nucleo_OnePunchMan', Vector3.new(108, 41.2, -112.775)},
  {'VFX_Carrinho__Metal_Iron', 'carrinho', Vector3.new(-56.579, 6.05, 28.288)},
  {'VFX_Carrinho__Metal_Dark', 'carrinho', Vector3.new(-56.579, 5.915, 28.288)},
  {'VFX_Carrinho__Wood_Plank', 'carrinho', Vector3.new(-56.579, 6.75, 28.288)},
  {'VFX_CarrinhoCarga__Crystal_Blue', 'carga', Vector3.new(-56.447, 8.52, 28.377)},
  {'VFX_CarrinhoCarga__Crystal_Purple', 'carga', Vector3.new(-56.553, 7.907, 27.402)},
}
-- malhas estaticas substituidas quando TODAS as pecas dos grupos existem
DATA.sources = {
  {name = 'WATER_Waterwheel', mats = {'Metal_Dark', 'Metal_Iron', 'Wood_Dark', 'Wood_Light', 'Wood_Plank'}, groups = {'roda', 'roda_fixa'}},
  {name = 'BLD_WheelHouse', mats = {'Metal_Dark', 'Metal_Iron', 'Stone_Dark', 'Wood_Dark', 'Wood_Light'}, groups = {'eixo_baixo', 'pinhao', 'martinete', 'casa_fixa'}},
}
DATA.groups = {
  ['roda'] = {kind = 'spin', assembly = 'RodaDagua', pivot = Vector3.new(62, 11, -20), axis = Vector3.new(-1, 0, 0), speed = 0.628},
  ['roda_fixa'] = {kind = 'fixed', assembly = 'RodaDagua'},
  ['eixo_baixo'] = {kind = 'spin', assembly = 'CasaDaRoda', pivot = Vector3.new(62, 11, -20), axis = Vector3.new(-1, 0, 0), speed = 0.628},
  ['pinhao'] = {kind = 'spin', assembly = 'CasaDaRoda', pivot = Vector3.new(44.4, 15.5, -20), axis = Vector3.new(1, 0, 0), speed = 1.257},
  ['martinete'] = {kind = 'hammer', assembly = 'CasaDaRoda', pivot = Vector3.new(47.5, 9, -25), axis = Vector3.new(-1, 0, 0), speed = 0.628, camPhase = 1.571, cams = 3, rest = 0.03, lift = 0.16, event = 'martinete'},
  ['casa_fixa'] = {kind = 'fixed', assembly = 'CasaDaRoda'},
  ['espiral_Naruto'] = {kind = 'spin', assembly = 'Portal_Naruto', pivot = Vector3.new(-108, 41.2, -113), axis = Vector3.new(0, 0, 1), speed = 0.85, portal = 'Naruto', inner = true, innerScale = 0.55, innerSpeed = 2.3, noShadow = true},
  ['nucleo_Naruto'] = {kind = 'core', assembly = 'Portal_Naruto', portal = 'Naruto', noShadow = true},
  ['espiral_DragonBall'] = {kind = 'spin', assembly = 'Portal_DragonBall', pivot = Vector3.new(-76, 41.2, -113), axis = Vector3.new(0, 0, 1), speed = 0.85, portal = 'DragonBall', inner = true, innerScale = 0.55, innerSpeed = 2.3, noShadow = true},
  ['nucleo_DragonBall'] = {kind = 'core', assembly = 'Portal_DragonBall', portal = 'DragonBall', noShadow = true},
  ['espiral_ShadowGarden'] = {kind = 'spin', assembly = 'Portal_ShadowGarden', pivot = Vector3.new(-44, 41.2, -113), axis = Vector3.new(0, 0, 1), speed = 0.85, portal = 'ShadowGarden', inner = true, innerScale = 0.55, innerSpeed = 2.3, noShadow = true},
  ['nucleo_ShadowGarden'] = {kind = 'core', assembly = 'Portal_ShadowGarden', portal = 'ShadowGarden', noShadow = true},
  ['espiral_DemonSlayer'] = {kind = 'spin', assembly = 'Portal_DemonSlayer', pivot = Vector3.new(44, 41.2, -113), axis = Vector3.new(0, 0, 1), speed = 0.85, portal = 'DemonSlayer', inner = true, innerScale = 0.55, innerSpeed = 2.3, noShadow = true},
  ['nucleo_DemonSlayer'] = {kind = 'core', assembly = 'Portal_DemonSlayer', portal = 'DemonSlayer', noShadow = true},
  ['espiral_OnePiece'] = {kind = 'spin', assembly = 'Portal_OnePiece', pivot = Vector3.new(76, 41.2, -113), axis = Vector3.new(0, 0, 1), speed = 0.85, portal = 'OnePiece', inner = true, innerScale = 0.55, innerSpeed = 2.3, noShadow = true},
  ['nucleo_OnePiece'] = {kind = 'core', assembly = 'Portal_OnePiece', portal = 'OnePiece', noShadow = true},
  ['espiral_OnePunchMan'] = {kind = 'spin', assembly = 'Portal_OnePunchMan', pivot = Vector3.new(108, 41.2, -113), axis = Vector3.new(0, 0, 1), speed = 0.85, portal = 'OnePunchMan', inner = true, innerScale = 0.55, innerSpeed = 2.3, noShadow = true},
  ['nucleo_OnePunchMan'] = {kind = 'core', assembly = 'Portal_OnePunchMan', portal = 'OnePunchMan', noShadow = true},
  ['carrinho'] = {kind = 'cart'},
  ['carga'] = {kind = 'load'},
}
DATA.mats = {
  ['Crystal_Blue'] = {c = Color3.fromRGB(56, 144, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['Crystal_Purple'] = {c = Color3.fromRGB(170, 80, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['Metal_Dark'] = {c = Color3.fromRGB(85, 85, 89), m = Enum.Material.Metal, r = Enum.Material.Metal, t = 0},
  ['Metal_Iron'] = {c = Color3.fromRGB(124, 124, 129), m = Enum.Material.Metal, r = Enum.Material.Metal, t = 0},
  ['Stone_Dark'] = {c = Color3.fromRGB(97, 95, 97), m = Enum.Material.SmoothPlastic, r = Enum.Material.Slate, t = 0},
  ['VFXP_DemonSlayer_Braco'] = {c = Color3.fromRGB(255, 150, 138), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_DemonSlayer_Nucleo'] = {c = Color3.fromRGB(255, 234, 226), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_DragonBall_Braco'] = {c = Color3.fromRGB(255, 232, 150), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_DragonBall_Nucleo'] = {c = Color3.fromRGB(255, 251, 228), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_Naruto_Braco'] = {c = Color3.fromRGB(255, 178, 204), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_Naruto_Nucleo'] = {c = Color3.fromRGB(255, 238, 244), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_OnePiece_Braco'] = {c = Color3.fromRGB(138, 204, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_OnePiece_Nucleo'] = {c = Color3.fromRGB(228, 246, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_OnePunchMan_Braco'] = {c = Color3.fromRGB(176, 242, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_OnePunchMan_Nucleo'] = {c = Color3.fromRGB(236, 252, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_ShadowGarden_Braco'] = {c = Color3.fromRGB(208, 158, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['VFXP_ShadowGarden_Nucleo'] = {c = Color3.fromRGB(244, 232, 255), m = Enum.Material.Neon, r = Enum.Material.Neon, t = 0},
  ['Wood_Dark'] = {c = Color3.fromRGB(105, 72, 48), m = Enum.Material.SmoothPlastic, r = Enum.Material.Wood, t = 0},
  ['Wood_Light'] = {c = Color3.fromRGB(162, 118, 80), m = Enum.Material.SmoothPlastic, r = Enum.Material.Wood, t = 0},
  ['Wood_Plank'] = {c = Color3.fromRGB(139, 101, 66), m = Enum.Material.SmoothPlastic, r = Enum.Material.WoodPlanks, t = 0},
}
DATA.portals = {
  {key = 'Naruto', idx = 0, center = Vector3.new(-108, 41.2, -113), normal = Vector3.new(0, 0, 1), radius = 7.5, swirl = 'PORTAL_Naruto_Swirl', arms = 'VFX_Espiral_Naruto__VFXP_Naruto_Braco', core = 'VFX_Espiral_Naruto__VFXP_Naruto_Nucleo',
   disc = Color3.fromRGB(232, 52, 96), arm = Color3.fromRGB(255, 178, 204), core3 = Color3.fromRGB(255, 238, 244)},
  {key = 'DragonBall', idx = 1, center = Vector3.new(-76, 41.2, -113), normal = Vector3.new(0, 0, 1), radius = 7.5, swirl = 'PORTAL_DragonBall_Swirl', arms = 'VFX_Espiral_DragonBall__VFXP_DragonBall_Braco', core = 'VFX_Espiral_DragonBall__VFXP_DragonBall_Nucleo',
   disc = Color3.fromRGB(255, 146, 18), arm = Color3.fromRGB(255, 232, 150), core3 = Color3.fromRGB(255, 251, 228)},
  {key = 'ShadowGarden', idx = 2, center = Vector3.new(-44, 41.2, -113), normal = Vector3.new(0, 0, 1), radius = 7.5, swirl = 'PORTAL_ShadowGarden_Swirl', arms = 'VFX_Espiral_ShadowGarden__VFXP_ShadowGarden_Braco', core = 'VFX_Espiral_ShadowGarden__VFXP_ShadowGarden_Nucleo',
   disc = Color3.fromRGB(118, 38, 214), arm = Color3.fromRGB(208, 158, 255), core3 = Color3.fromRGB(244, 232, 255)},
  {key = 'DemonSlayer', idx = 3, center = Vector3.new(44, 41.2, -113), normal = Vector3.new(0, 0, 1), radius = 7.5, swirl = 'PORTAL_DemonSlayer_Swirl', arms = 'VFX_Espiral_DemonSlayer__VFXP_DemonSlayer_Braco', core = 'VFX_Espiral_DemonSlayer__VFXP_DemonSlayer_Nucleo',
   disc = Color3.fromRGB(206, 28, 40), arm = Color3.fromRGB(255, 150, 138), core3 = Color3.fromRGB(255, 234, 226)},
  {key = 'OnePiece', idx = 4, center = Vector3.new(76, 41.2, -113), normal = Vector3.new(0, 0, 1), radius = 7.5, swirl = 'PORTAL_OnePiece_Swirl', arms = 'VFX_Espiral_OnePiece__VFXP_OnePiece_Braco', core = 'VFX_Espiral_OnePiece__VFXP_OnePiece_Nucleo',
   disc = Color3.fromRGB(24, 92, 226), arm = Color3.fromRGB(138, 204, 255), core3 = Color3.fromRGB(228, 246, 255)},
  {key = 'OnePunchMan', idx = 5, center = Vector3.new(108, 41.2, -113), normal = Vector3.new(0, 0, 1), radius = 7.5, swirl = 'PORTAL_OnePunchMan_Swirl', arms = 'VFX_Espiral_OnePunchMan__VFXP_OnePunchMan_Braco', core = 'VFX_Espiral_OnePunchMan__VFXP_OnePunchMan_Nucleo',
   disc = Color3.fromRGB(16, 168, 236), arm = Color3.fromRGB(176, 242, 255), core3 = Color3.fromRGB(236, 252, 255)},
}
DATA.fx = {
  anvil_hammer = {pos = Vector3.new(47.5, 7, -16)},
  anvil_ignis = {pos = Vector3.new(0.5, 8.925, 10)},
  chimney = {pos = Vector3.new(0, 96.5, -30), radius = 7.6},
  hearth = {pos = Vector3.new(-0.212, 7.648, -1.775), size = Vector3.new(9.023, 0.4, 4.361)},
  hearth_chimney = {pos = Vector3.new(0, 25.4, -1), size = Vector3.new(3.2, 0.4, 2.2)},
  mine = {pos = Vector3.new(-91.042, 8, 84.012), size = Vector3.new(20, 8, 20)},
  shed = {pos = Vector3.new(112.005, 7.85, 34.776), size = Vector3.new(12.736, 3.475, 5.245)},
  wheel_in = {pos = Vector3.new(62, 3, -23.709)},
  wheel_mist = {pos = Vector3.new(62, 2.8, -11.5)},
  wheel_out = {pos = Vector3.new(62, 3, -16.291)},
}
DATA.wheelWidth = 3.4
DATA.waterfalls = {
  {name = 'Center', top = Vector3.new(0, 29.197, -79.705), base = Vector3.new(0, 13.2, -78.075), width = 5.8, out = Vector3.new(0, 0, 1)},
  {name = 'NE', top = Vector3.new(130, 72.081, -83.095), base = Vector3.new(130, 13.2, -75.675), width = 8, out = Vector3.new(0, 0, 1)},
  {name = 'NW', top = Vector3.new(-121, 58.05, -82.082), base = Vector3.new(-121, 13.2, -80.075), width = 7, out = Vector3.new(0, 0, 1)},
  {name = 'South', top = Vector3.new(62, 2.769, 62.411), base = Vector3.new(62, -44, 65.425), width = 7, out = Vector3.new(0, 0, 1)},
  {name = 'Spill', top = Vector3.new(60, 12.95, -61.56), base = Vector3.new(60, 2.8, -58.975), width = 7, out = Vector3.new(0, 0, 1)},
}
DATA.cartRest = CFrame.new(-56.579, 4.3, 28.288) * CFrame.Angles(0, 1.245, 0)

local function log(fmt, ...) print("[VFX Forja] " .. string.format(fmt, ...)) end
local function warnf(fmt, ...) warn("[VFX Forja] " .. string.format(fmt, ...)) end

-- ---------------------------------------------------------------- raiz e transformacao do lobby
local root
for _, n in ipairs(ROOT_NAMES) do
  root = workspace:FindFirstChild(n)
  if root then break end
end
if not root then
  warnf("lobby nao encontrado no workspace (%s)", table.concat(ROOT_NAMES, ", "))
  return
end

local markers = root:FindFirstChild("GAMEPLAY_MARKERS")
local rootCF, refName
for _, r in ipairs(DATA.refs) do
  local p = markers and markers:FindFirstChild(r.name)
  if p and p:IsA("BasePart") then
    rootCF = p.CFrame * CFrame.fromMatrix(r.pos, r.x, r.y):Inverse()
    refName = r.name
    break
  end
end
if not rootCF then
  -- sem marcadores: usa o disco do portal Naruto (centro canonico conhecido)
  local p = root:FindFirstChild("PORTAL_Naruto_Swirl__P_Naruto_Swirl", true)
  local pc = DATA.portals[1] and DATA.portals[1].center
  if p and pc then
    rootCF = p.CFrame * CFrame.new(-pc)
    refName = p.Name
  else
    rootCF = CFrame.new()
    refName = "origem"
    warnf("nenhuma referencia achada (rode montar_lobby_forja.lua antes); usando a origem")
  end
end
for _, r in ipairs(DATA.refs) do
  local p = markers and markers:FindFirstChild(r.name)
  if p and p:IsA("BasePart") and r.name ~= refName then
    local err = ((rootCF * r.pos) - p.Position).Magnitude
    if err > 1 then warnf("marcador %s fora do lugar esperado (%.1f studs) - confira", r.name, err) end
  end
end
local function W(v) return rootCF * v end
local function WV(v) return rootCF:VectorToWorldSpace(v) end
local function WCF(cf) return rootCF * cf end

local function folder(parent, name, class)
  local f = parent:FindFirstChild(name)
  if not f then
    f = Instance.new(class or "Folder")
    f.Name = name
    f.Parent = parent
  end
  return f
end
local VFXF = folder(root, "VFX")
VFXF:ClearAllChildren()
local MOVF = folder(root, "VFX_MOVING")
local ORIG = folder(ServerStorage, "LOBBY_FORJA_VFX_ORIGINAIS")
local CFG = folder(ReplicatedStorage, "LOBBY_FORJA_VFX")
local EV = CFG:FindFirstChild("Evento")
if not EV then
  EV = Instance.new("BindableEvent")
  EV.Name = "Evento"
  EV.Parent = CFG
end

local function clearTags(inst)
  for _, t in ipairs(CollectionService:GetTags(inst)) do
    if string.sub(t, 1, 6) == "FORJA_" then CollectionService:RemoveTag(inst, t) end
  end
end
local function matOf(name)
  return string.match(name, "__(.-)_%d+$") or string.match(name, "__(.+)$")
end

-- ---------------------------------------------------------------- pecas moveis (LOBBY_VFX_MOVING.fbx)
local wanted = {}
for _, m in ipairs(DATA.movers) do wanted[m[1]] = {group = m[2], home = m[3]} end
local found = {}
local function scan(container)
  for _, d in ipairs(container:GetDescendants()) do
    if d:IsA("MeshPart") and wanted[d.Name] then
      if found[d.Name] and found[d.Name] ~= d then
        d.Parent = ORIG -- duplicata (FBX importado duas vezes)
      else
        found[d.Name] = d
      end
    end
  end
end
scan(workspace)
scan(CFG)
local groupCount, groupTotal = {}, {}
for _, m in ipairs(DATA.movers) do
  groupTotal[m[2]] = (groupTotal[m[2]] or 0) + 1
  if found[m[1]] then groupCount[m[2]] = (groupCount[m[2]] or 0) + 1 end
end
local function groupOk(g) return groupTotal[g] ~= nil and groupCount[g] == groupTotal[g] end

-- aparencia: copia de uma peca original com o mesmo material (fica identica ao que o montar aplicou)
local looks = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and not wanted[d.Name] then
    local m = matOf(d.Name)
    if m and not looks[m] then looks[m] = d end
  end
end
for _, d in ipairs(ORIG:GetDescendants()) do
  if d:IsA("MeshPart") then
    local m = matOf(d.Name)
    if m and not looks[m] then looks[m] = d end
  end
end
local function applyLook(p, mat)
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  local e = DATA.mats[mat]
  local src = looks[mat]
  if src and not string.find(mat, "^VFXP_") then
    p.Color = src.Color
    p.Material = src.Material
    p.MaterialVariant = src.MaterialVariant
    p.Transparency = src.Transparency
    p.Reflectance = src.Reflectance
  elseif e then
    p.Color = e.c
    p.Material = RICO and e.r or e.m
    p.Transparency = e.t
  end
  p.TextureID = ""
end

-- fontes completas: esconde as malhas estaticas originais; incompletas: nao anima (evita peca duplicada)
local sourceOk = {}
local byName = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and not wanted[d.Name] then
    local base = string.match(d.Name, "^(.-)_%d+$")
    for _, key in ipairs({d.Name, base}) do
      if key then
        byName[key] = byName[key] or {}
        table.insert(byName[key], d)
      end
    end
  end
end
for _, s in ipairs(DATA.sources) do
  local ok = true
  for _, g in ipairs(s.groups) do
    if groupTotal[g] and not groupOk(g) then ok = false end
  end
  sourceOk[s.name] = ok
  if ok then
    local moved = 0
    for _, mat in ipairs(s.mats) do
      for _, d in ipairs(byName[s.name .. "__" .. mat] or {}) do
        if d.Parent ~= ORIG then
          d.Parent = ORIG
          moved += 1
        end
      end
    end
    log("%s: %d malhas originais guardadas em ServerStorage (substituidas pelas pecas separadas)", s.name, moved)
  else
    warnf("%s: LOBBY_VFX_MOVING.fbx incompleto; a peca fica estatica (importe o FBX e rode de novo)", s.name)
  end
end
local groupSource = {}
for _, s in ipairs(DATA.sources) do
  for _, g in ipairs(s.groups) do groupSource[g] = s.name end
end

local assemblies = {}
local function assembly(name)
  local m = assemblies[name]
  if not m then
    m = MOVF:FindFirstChild(name)
    if not m then
      m = Instance.new("Model")
      m.Name = name
      m.Parent = MOVF
    end
    pcall(function() m.ModelStreamingMode = Enum.ModelStreamingMode.Atomic end)
    assemblies[name] = m
  end
  return m
end

local function setMotion(p, home, g)
  p:SetAttribute("VFX_Home", home)
  p:SetAttribute("VFX_Pivot", W(g.pivot))
  p:SetAttribute("VFX_Axis", WV(g.axis).Unit)
  p:SetAttribute("VFX_Speed", g.speed)
  p:SetAttribute("VFX_Phase", 0)
end

local cartParts = {}
local portalArms, portalCore = {}, {}
local nMov = 0
for name, part in pairs(found) do
  local w = wanted[name]
  local g = DATA.groups[w.group]
  local mat = matOf(name)
  clearTags(part)
  applyLook(part, mat)
  local home = rootCF * CFrame.new(w.home)
  part.CFrame = home
  part.CastShadow = not (g and g.noShadow)
  if not g then
    part.Parent = MOVF
  elseif g.kind == "cart" or g.kind == "load" then
    table.insert(cartParts, {part, g.kind == "load"})
  elseif groupSource[w.group] and not sourceOk[groupSource[w.group]] then
    part.Parent = ORIG -- fonte incompleta: nao mostra meia roda
  else
    part.Parent = assembly(g.assembly)
    nMov += 1
    if g.kind == "spin" then
      setMotion(part, home, g)
      if g.portal then part:SetAttribute("VFX_Portal", g.portal) end
      if g.inner then
        part:SetAttribute("VFX_Inner", true)
        part:SetAttribute("VFX_InnerScale", g.innerScale)
        part:SetAttribute("VFX_InnerSpeed", g.innerSpeed)
        portalArms[g.portal] = part
      end
      CollectionService:AddTag(part, "FORJA_Spin")
    elseif g.kind == "hammer" then
      setMotion(part, home, g)
      part:SetAttribute("VFX_CamPhase", g.camPhase)
      part:SetAttribute("VFX_Cams", g.cams)
      part:SetAttribute("VFX_Rest", g.rest)
      part:SetAttribute("VFX_Lift", g.lift)
      part:SetAttribute("VFX_Event", g.event)
      CollectionService:AddTag(part, "FORJA_Hammer")
    elseif g.kind == "core" then
      portalCore[g.portal] = part
    end
  end
end

-- ---------------------------------------------------------------- molde do carrinho (o cliente clona)
local oldTpl = CFG:FindFirstChild("MineCart")
local tpl = Instance.new("Model")
tpl.Name = "MineCart"
local restCF = WCF(DATA.cartRest)
local function mkPart(parent, name, size, cf, color, material, shape)
  local p = Instance.new("Part")
  p.Name = name
  if shape then p.Shape = shape end
  p.Size = size
  p.CFrame = cf
  p.Color = color
  p.Material = material
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  p.TopSurface = Enum.SurfaceType.Smooth
  p.BottomSurface = Enum.SurfaceType.Smooth
  p.Parent = parent
  return p
end
if #cartParts > 0 then
  for _, cp in ipairs(cartParts) do
    cp[1].Parent = tpl
    cp[1]:SetAttribute("VFX_Load", cp[2])
  end
else
  -- sem o FBX: carrinho simples em Parts
  local iron, dark = Color3.fromRGB(88, 88, 94), Color3.fromRGB(52, 52, 56)
  mkPart(tpl, "Chassi", Vector3.new(3.4, 0.35, 2.2), restCF * CFrame.new(0, 0.8, 0), dark, Enum.Material.Metal)
  mkPart(tpl, "Cacamba", Vector3.new(3.2, 1.6, 2.5), restCF * CFrame.new(0, 1.85, 0), iron, Enum.Material.Metal)
  for sx = -1, 1, 2 do
    for sz = -1, 1, 2 do
      mkPart(tpl, "Roda", Vector3.new(0.3, 1.24, 1.24), restCF * CFrame.new(sx * 1.1, 0.4, sz * 1.25) *
        CFrame.Angles(0, math.pi / 2, 0), dark, Enum.Material.Metal, Enum.PartType.Cylinder)
    end
  end
  for i = 1, 3 do
    local c = mkPart(tpl, "Cristal", Vector3.new(0.7, 1.4 + i * 0.2, 0.7), restCF * CFrame.new(-0.8 + i * 0.45, 3.0, 0.25 * (i - 2)) *
      CFrame.Angles(0.2 * (i - 2), 0, 0.25), Color3.fromRGB(56, 145, 255), Enum.Material.Neon)
    c:SetAttribute("VFX_Load", true)
  end
end
tpl.WorldPivot = restCF
tpl:SetAttribute("VFX_RestCF", restCF)
if oldTpl then oldTpl:Destroy() end
tpl.Parent = CFG

-- ---------------------------------------------------------------- utilitarios de particulas
local TEX = {
  dot = "rbxasset://textures/particles/explosion01_implosion_main.dds",   -- ponto macio
  ring = "rbxasset://textures/particles/explosion01_shockwave_main.dds",  -- anel
  smoke = "rbxasset://textures/particles/smoke_main.dds",
  fire = "rbxasset://textures/particles/fire_main.dds",
  star = "rbxasset://textures/particles/sparkles_main.dds",
  vortex = "rbxasset://textures/particles/forcefield_vortex_main.dds",
}
local function RGB(r, g, b) return Color3.fromRGB(r, g, b) end
local function NS(t)
  if type(t) == "number" then return NumberSequence.new(t) end
  local k = {}
  for _, p in ipairs(t) do table.insert(k, NumberSequenceKeypoint.new(p[1], p[2])) end
  return NumberSequence.new(k)
end
local function CS(t)
  if typeof(t) == "Color3" then return ColorSequence.new(t) end
  local k = {}
  for _, p in ipairs(t) do table.insert(k, ColorSequenceKeypoint.new(p[1], p[2])) end
  return ColorSequence.new(k)
end
local function NR(t) return NumberRange.new(t[1], t[2] or t[1]) end

local function host(name, posC, size, lookC)
  local p = Instance.new("Part")
  p.Name = name
  p.Size = size
  local cf = CFrame.new(posC)
  if lookC then cf = CFrame.lookAt(posC, posC + lookC) end
  p.CFrame = WCF(cf)
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  p.CastShadow = false
  p.Transparency = 1
  p.Locked = true
  p.Parent = VFXF
  return p
end
local function att(parent, name, cf)
  local a = Instance.new("Attachment")
  a.Name = name
  a.CFrame = cf or CFrame.new()
  a.Parent = parent
  return a
end
local function emitter(parent, name, p)
  local e = Instance.new("ParticleEmitter")
  e.Name = name
  e.Texture = p.tex or TEX.dot
  e.Color = CS(p.color or RGB(255, 255, 255))
  e.Size = NS(p.size or 1)
  e.Transparency = NS(p.transp or 0)
  e.Lifetime = NR(p.life)
  e.Rate = p.rate or 0
  e.Speed = NR(p.speed or {0})
  e.SpreadAngle = Vector2.new(p.spread or 0, p.spread2 or p.spread or 0)
  e.Acceleration = p.accel and WV(p.accel) or Vector3.zero
  e.Drag = p.drag or 0
  e.LightEmission = p.emission or 0
  e.LightInfluence = p.influence or 0
  e.Brightness = p.bright or 1
  e.Rotation = NR(p.rot or {0})
  e.RotSpeed = NR(p.rotspeed or {0})
  e.EmissionDirection = p.dir or Enum.NormalId.Top
  e.Shape = Enum.ParticleEmitterShape.Box
  e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
  e.Orientation = p.orient or Enum.ParticleOrientation.FacingCamera
  if p.squash then e.Squash = NS(p.squash) end
  e.ZOffset = p.zoff or 0
  e.LockedToPart = p.locked or false
  e.Parent = parent
  if (p.rate or 0) > 0 then
    e:SetAttribute("VFX_MaxDist", p.maxd or 400)
    CollectionService:AddTag(e, "FORJA_Emitter")
  end
  if p.event then
    e:SetAttribute("VFX_Event", p.event)
    e:SetAttribute("VFX_Count", p.count or 8)
    CollectionService:AddTag(e, "FORJA_Burst")
  end
  return e
end
local function flashLight(parent, color, range, peak, event)
  local l = Instance.new("PointLight")
  l.Name = "Clarao"
  l.Color = color
  l.Range = range
  l.Brightness = 0
  l.Shadows = false
  l:SetAttribute("VFX_Kind", "flash")
  l:SetAttribute("VFX_Event", event)
  l:SetAttribute("VFX_Base", peak)
  l.Parent = parent
  CollectionService:AddTag(l, "FORJA_Flicker")
  return l
end
local UP = Vector3.new(0, 1, 0)
local FX = DATA.fx
local nEm = 0
local function count(n) nEm += n end

-- ---------------------------------------------------------------- FORJA (quente)
if FX.hearth then
  local h = host("Lareira_Fogo", FX.hearth.pos, FX.hearth.size)
  emitter(h, "Chamas", {tex = TEX.dot, color = {{0, RGB(255, 246, 196)}, {0.25, RGB(255, 196, 78)}, {0.6, RGB(255, 112, 32)}, {1, RGB(150, 34, 12)}},
    size = {{0, 1.3}, {0.35, 2.2}, {1, 0.35}}, transp = {{0, 0.45}, {0.18, 0.08}, {0.75, 0.45}, {1, 1}},
    life = {0.55, 1.05}, rate = 30, speed = {2.5, 5}, spread = 12, accel = Vector3.new(0, 3.5, 0), drag = 0.6,
    emission = 1, bright = 2, rot = {0, 360}, rotspeed = {-40, 40}, zoff = 0.4, maxd = 320})
  emitter(h, "Linguas", {tex = TEX.fire, color = {{0, RGB(255, 226, 150)}, {0.5, RGB(255, 132, 40)}, {1, RGB(190, 46, 18)}},
    size = {{0, 2.2}, {0.5, 3.0}, {1, 0.8}}, transp = {{0, 0.55}, {0.3, 0.2}, {1, 1}},
    life = {0.4, 0.8}, rate = 10, speed = {3, 6}, spread = 8, emission = 0.9, bright = 1.6, rot = {-25, 25}, maxd = 320})
  emitter(h, "Brasas", {tex = TEX.dot, color = RGB(255, 168, 60), size = {{0, 0.3}, {1, 0}}, transp = {{0, 0}, {0.8, 0.2}, {1, 1}},
    life = {0.9, 1.8}, rate = 5, speed = {2.5, 5}, spread = 25, accel = Vector3.new(0, 2, 1.4), drag = 0.4,
    emission = 1, bright = 3, maxd = 260})
  count(3)
end
if FX.chimney then
  local r = FX.chimney.radius
  local h = host("Chamine_Fumaca", FX.chimney.pos, Vector3.new(r, 1, r))
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(66, 58, 54)}, {0.5, RGB(94, 88, 84)}, {1, RGB(142, 138, 136)}},
    size = {{0, 5}, {0.25, 10}, {1, 28}}, transp = {{0, 1}, {0.06, 0.3}, {0.55, 0.45}, {1, 1}},
    life = {9, 13}, rate = 4.5, speed = {7, 10}, spread = 8, accel = Vector3.new(1.4, 0.3, -0.65), drag = 0.25,
    influence = 1, rot = {0, 360}, rotspeed = {-12, 12}, maxd = 3000})
  emitter(h, "Fagulhas", {tex = TEX.dot, color = RGB(255, 150, 50), size = {{0, 0.45}, {1, 0}}, transp = {{0, 0}, {1, 1}},
    life = {1.5, 3}, rate = 3, speed = {9, 14}, spread = 20, accel = Vector3.new(1.5, -2, -0.6), drag = 0.5,
    emission = 1, bright = 3, maxd = 700})
  count(2)
end
if FX.hearth_chimney then
  local h = host("Lareira_Fumaca", FX.hearth_chimney.pos, FX.hearth_chimney.size)
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(120, 114, 110)}, {1, RGB(172, 168, 166)}},
    size = {{0, 1.6}, {1, 7}}, transp = {{0, 1}, {0.1, 0.55}, {1, 1}}, life = {4, 6}, rate = 1.8, speed = {3, 5},
    spread = 10, accel = Vector3.new(0.8, 0.3, -0.35), influence = 1, rot = {0, 360}, rotspeed = {-15, 15}, maxd = 500})
  count(1)
end
local function anvilFX(name, posC, event, sparks, speedMax, peak)
  local h = host(name, posC, Vector3.new(0.6, 0.2, 0.6))
  local a = att(h, "Topo")
  emitter(a, "Faiscas", {tex = TEX.dot, color = {{0, RGB(255, 250, 214)}, {0.4, RGB(255, 192, 82)}, {1, RGB(255, 108, 30)}},
    size = {{0, 0.28}, {1, 0.06}}, transp = {{0, 0}, {0.7, 0.1}, {1, 1}}, life = {0.3, 0.75}, speed = {speedMax * 0.5, speedMax},
    spread = 75, accel = Vector3.new(0, -60, 0), drag = 1.4, emission = 1, bright = 4,
    orient = Enum.ParticleOrientation.VelocityParallel, squash = 2, event = event, count = sparks})
  emitter(a, "Brilho", {tex = TEX.dot, color = RGB(255, 204, 128), size = {{0, 2.2}, {1, 5}}, transp = {{0, 0.35}, {1, 1}},
    life = {0.16}, speed = {0}, emission = 1, bright = 3, event = event, count = 1})
  flashLight(h, RGB(255, 160, 70), 14, peak, event)
  count(2)
  return h, a
end
anvilFX("Bigorna_Ignis", FX.anvil_ignis.pos, "ignis", 14, 26, 4)
local _, ah = anvilFX("Bigorna_Martinete", FX.anvil_hammer.pos, "martinete", 9, 18, 3)
emitter(ah, "Po", {tex = TEX.smoke, color = RGB(128, 118, 108), size = {{0, 0.8}, {1, 2.6}}, transp = {{0, 0.5}, {1, 1}},
  life = {0.6, 1.1}, speed = {2, 4}, spread = 80, accel = Vector3.new(0, 1, 0), drag = 2, influence = 1,
  event = "martinete", count = 4})
count(1)

-- ---------------------------------------------------------------- AGUA (frio): roda e quedas
do
  local ww = DATA.wheelWidth
  local o = host("Roda_Respingo", FX.wheel_out.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(o, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.45}, {1, 0.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {0.5, 0.9}, rate = 22, speed = {6, 11}, spread = 30, accel = Vector3.new(0, -40, 3), drag = 0.5,
    emission = 0.3, influence = 0.6, orient = Enum.ParticleOrientation.VelocityParallel, squash = 0.8, maxd = 300})
  local i = host("Roda_Entrada", FX.wheel_in.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(i, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.4}, {1, 0.15}}, transp = {{0, 0.2}, {1, 1}},
    life = {0.35, 0.6}, rate = 10, speed = {3, 6}, spread = 40, accel = Vector3.new(0, -40, 0), drag = 0.5,
    emission = 0.3, influence = 0.6, maxd = 300})
  local m = host("Roda_Nevoa", FX.wheel_mist.pos, Vector3.new(ww + 1, 0.5, 4))
  emitter(m, "Espuma", {tex = TEX.smoke, color = RGB(240, 248, 255), size = {{0, 1.5}, {1, 4.5}}, transp = {{0, 0.5}, {1, 1}},
    life = {1.2, 2}, rate = 4, speed = {1, 2.5}, spread = 40, drag = 1, influence = 0.7, rot = {0, 360}, maxd = 300})
  count(3)
end
for _, wf in ipairs(DATA.waterfalls) do
  local w = wf.width
  local h = (wf.top - wf.base).Magnitude
  local b = host("Queda_" .. wf.name .. "_Base", wf.base + Vector3.new(0, 0.3, 0), Vector3.new(w + 1.5, 0.6, 3), wf.out)
  emitter(b, "Nevoa", {tex = TEX.smoke, color = RGB(236, 245, 255), size = {{0, math.clamp(w * 0.45, 3, 7)}, {1, math.clamp(w * 1.15, 6, 14)}},
    transp = {{0, 0.72}, {0.3, 0.55}, {1, 1}}, life = {2.5, 4}, rate = math.clamp(w * 0.35, 1.5, 4), speed = {1.5, 3.5},
    spread = 45, accel = Vector3.new(0, 0.6, 0), drag = 0.6, influence = 0.8, rot = {0, 360}, rotspeed = {-10, 10}, maxd = 650})
  emitter(b, "Espuma", {tex = TEX.smoke, color = RGB(250, 253, 255), size = {{0, 1.4}, {1, 3.2}}, transp = {{0, 0.25}, {1, 1}},
    life = {0.6, 1.1}, rate = math.clamp(w * 1.4, 5, 12), speed = {4, 8}, spread = 35, accel = Vector3.new(0, -18, 0),
    drag = 0.8, influence = 0.7, rot = {0, 360}, maxd = 450})
  local t = host("Queda_" .. wf.name .. "_Fios", wf.top + wf.out * 0.7, Vector3.new(w * 0.75, 0.3, 0.5), wf.out)
  emitter(t, "Fios", {tex = TEX.dot, color = RGB(220, 238, 255), size = {{0, 0.55}, {1, 0.3}}, transp = {{0, 0.4}, {0.8, 0.55}, {1, 1}},
    life = {math.min(1.6, math.sqrt(2 * h / 40))}, rate = math.clamp(w * 1.2, 4, 10), speed = {3, 6}, spread = 4, spread2 = 10,
    dir = Enum.NormalId.Bottom, accel = Vector3.new(0, -40, 0) + wf.out * 1.5, emission = 0.4, influence = 0.5,
    orient = Enum.ParticleOrientation.VelocityParallel, squash = 2.5, maxd = 450})
  count(3)
end

-- ---------------------------------------------------------------- PORTAIS (acentos)
for _, p in ipairs(DATA.portals) do
  local key = p.key
  local R = p.radius
  local n = p.normal
  local armPart = portalArms[key]
  -- disco original: gira junto (se ganhou detalhe no Blender, aparece girando) e fica mais saturado
  local swirlParts = {}
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA("MeshPart") and string.sub(d.Name, 1, #p.swirl + 2) == p.swirl .. "__" then table.insert(swirlParts, d) end
  end
  local g = DATA.groups["espiral_" .. key]
  for _, d in ipairs(swirlParts) do
    clearTags(d)
    d:SetAttribute("VFX_Home", d.CFrame)
    d:SetAttribute("VFX_Pivot", W(p.center))
    d:SetAttribute("VFX_Axis", WV(n).Unit)
    d:SetAttribute("VFX_Speed", g and g.speed or 0.85)
    d:SetAttribute("VFX_Phase", 0)
    d:SetAttribute("VFX_Portal", key)
    CollectionService:AddTag(d, "FORJA_Spin")
    if RECOLOR_SWIRL and armPart then d.Color = p.disc end
  end
  -- base do plano do portal (canonico = espaco local das pecas, que tem a orientacao da raiz)
  local u = UP:Cross(n).Unit
  local v = n:Cross(u).Unit
  -- particulas sugadas: presas no disco que gira (nascem ao longo do aro e correm para o centro)
  local ringHost = armPart or swirlParts[1]
  if ringHost then
    for _, c in ipairs(ringHost:GetChildren()) do
      if c:IsA("Attachment") and string.sub(c.Name, 1, 7) == "Sugada_" then c:Destroy() end
    end
    local f = 0.45
    for k = 0, 1 do
      local ang = math.pi * k
      local lp = u * (math.cos(ang) * R * 0.92) + v * (math.sin(ang) * R * 0.92) + n * f
      local a = att(ringHost, "Sugada_" .. k, CFrame.lookAt(lp, n * f))
      emitter(a, "Sugadas", {tex = TEX.star, color = {{0, p.arm}, {1, p.core3}}, size = {{0, 0.15}, {0.2, 0.75}, {1, 0.1}},
        transp = {{0, 1}, {0.15, 0.1}, {1, 0.35}}, life = {1.15}, rate = 6, speed = {R * 0.92 / 1.15 * 0.95},
        spread = 6, dir = Enum.NormalId.Front, emission = 1, bright = 2, zoff = 0.3, maxd = 450})
      count(1)
    end
  end
  local h = host("Portal_" .. key, p.center, Vector3.new(1, 1, 1))
  local fa = att(h, "Frente", CFrame.lookAt(n * 0.35, n * 1.35))
  emitter(fa, "Vortice", {tex = TEX.vortex, color = p.arm, size = {{0, 2 * R * 0.95}, {1, 2 * R * 0.55}},
    transp = {{0, 1}, {0.25, 0.45}, {0.75, 0.55}, {1, 1}}, life = {2.4, 3}, rate = 1.1, speed = {0.2},
    dir = Enum.NormalId.Front, orient = Enum.ParticleOrientation.VelocityPerpendicular, emission = 1, bright = 1.5,
    rot = {0, 360}, rotspeed = {60, 100}, zoff = 0.2, maxd = 450})
  emitter(fa, "Pulso", {tex = TEX.ring, color = p.core3, size = {{0, 3}, {1, 2 * R * 1.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {1.1}, speed = {0.3}, dir = Enum.NormalId.Front, orient = Enum.ParticleOrientation.VelocityPerpendicular,
    emission = 1, bright = 2, event = "portal:" .. key, count = 1})
  count(2)
  local core = portalCore[key]
  if core then
    core:SetAttribute("VFX_Kind", "portalcore")
    core:SetAttribute("VFX_Event", "portal:" .. key)
    core:SetAttribute("VFX_BaseColor", core.Color)
    CollectionService:AddTag(core, "FORJA_Pulse")
  end
end

-- ---------------------------------------------------------------- CRISTAIS (frio)
local function sparkles(name, e, rate)
  local h = host(name, e.pos, e.size)
  emitter(h, "Brilhos", {tex = TEX.star, color = {{0, RGB(150, 212, 255)}, {1, RGB(176, 124, 255)}},
    size = {{0, 0}, {0.3, 0.7}, {1, 0}}, transp = {{0, 0.2}, {1, 1}}, life = {0.8, 1.6}, rate = rate, speed = {0.2, 0.6},
    spread = 180, emission = 1, bright = 2, rotspeed = {-90, 90}, maxd = 220})
  count(1)
end
if FX.mine then sparkles("Mina_Brilhos", FX.mine, 5) end
if FX.shed then sparkles("Galpao_Brilhos", FX.shed, 2.5) end

-- ---------------------------------------------------------------- tags das pecas estaticas (pulsos e flicker)
local nPulse, nLight = 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and d.Parent ~= ORIG then
    local n = d.Name
    local kind, event
    if string.find(n, "__Crystal_", 1, true) then
      kind = "crystal"
    elseif string.find(n, "__Metal_Heated", 1, true) then
      kind = "heat"
      if string.sub(n, 1, 12) == "FORGE_Anvil_" then event = "ignis"
      elseif string.sub(n, 1, 15) == "BLD_WheelHouse_" then event = "martinete" end
    elseif string.find(n, "__Forge_Emissive", 1, true) and string.sub(n, 1, 6) == "FORGE_" then
      kind = "ember"
    elseif string.find(n, "__Lantern_Glow", 1, true) then
      kind = "lantern"
    end
    if kind then
      if CollectionService:HasTag(d, "FORJA_Pulse") then CollectionService:RemoveTag(d, "FORJA_Pulse") end
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event or "")
      d:SetAttribute("VFX_BaseColor", d.Color)
      CollectionService:AddTag(d, "FORJA_Pulse")
      nPulse += 1
    end
  elseif (d:IsA("PointLight") or d:IsA("SpotLight")) and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "LIGHTS" then
    local n = d.Parent.Name
    local kind, event = "lantern", ""
    if string.sub(n, 1, 9) == "L_Portal_" then
      kind, event = "portal", "portal:" .. string.sub(n, 10)
    elseif string.sub(n, 1, 8) == "L_Hearth" or string.sub(n, 1, 9) == "L_Furnace" or string.sub(n, 1, 12) == "L_DS_Brazier" then
      kind = "fire"
    elseif n == "L_Mine_Chamber" or n == "L_Mine_Tunnel" or n == "L_Shed_Light" then
      kind = "crystal"
    elseif n == "L_Hall_Fill" or n == "L_Shop_Fill" or n == "L_Konoha_Gate" then
      kind = nil
    end
    if CollectionService:HasTag(d, "FORJA_Flicker") then CollectionService:RemoveTag(d, "FORJA_Flicker") end
    if kind then
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event)
      d:SetAttribute("VFX_Base", d.Brightness)
      CollectionService:AddTag(d, "FORJA_Flicker")
      nLight += 1
    end
  end
end

CFG:SetAttribute("VFX_Version", DATA.version)
CFG:SetAttribute("VFX_RootCF", rootCF)
CFG:SetAttribute("VFX_Root", root:GetFullName())
CFG:SetAttribute("VFX_Ready", true)
log("pronto (%s): referencia %s | %d pecas moveis, %d emissores, %d pulsos, %d luzes com flicker, carrinho %s",
  DATA.version, refName, nMov, nEm, nPulse, nLight, (#cartParts > 0) and "malha" or "Parts")
