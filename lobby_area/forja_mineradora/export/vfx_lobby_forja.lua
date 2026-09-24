--[[
vfx_lobby_forja.lua   (gerado por export_vfx.py - vfx-forja-2 - nao editar a mao: ajuste export_vfx.py e reexporte)
VFX e MOVIMENTO do Lobby Vila-Forja - MONTAGEM

ORDEM (tudo do MESMO passe do export_all.py: o EXPORT_ID confere e este script ABORTA se nao bater)
  1. importar LOBBY_*.fbx e rodar montar_lobby_forja.lua (colisoes, marcadores, luzes, cores, EXPORT_ID, RICO);
  2. importar export/LOBBY_VFX_MOVING_<ID6>.fbx (DATA.fbx, o do MESMO passe) com o 3D Importer (pode cair em
     qualquer lugar do workspace: este script acha as pecas pelo nome e as coloca na posicao certa, mesmo com o lobby
     deslocado ou girado);
  3. rodar ESTE script na Command Bar (ou como Script em ServerScriptService) e salvar o place.
     Pode rodar de novo (idempotente). Nao ha nenhum loop por frame no servidor.
  E SEMPRE: vfx_lobby_forja_client.lua como LocalScript em StarterPlayer > StarterPlayerScripts.

O QUE ESTE SCRIPT CRIA
  <lobby>.VFX              pecas invisiveis com ParticleEmitters, Beams e o SurfaceGui das espirais: fogo da lareira,
                           pluma da torre (nucleo escuro, corpo, topo claro, brasas, faiscas), fumaca fina dos
                           respiros e de 4 chamines da vila, faiscas da bigorna, vapor da tempera, respingos da roda,
                           cachoeiras (Beam com estrias + nevoa/espuma), ondulacao do rio e do canal, portais
                           (espiral em SurfaceGui, particulas sugadas, pulso), brilhos dos cristais
  <lobby>.VFX_MOVING       modelos (streaming atomico) com as pecas moveis do LOBBY_VFX_MOVING.fbx
  ReplicatedStorage.LOBBY_FORJA_VFX       config (VFX_RootCF), molde do carrinho (MineCart), BindableEvent Evento
  ServerStorage.LOBBY_FORJA_VFX_ORIGINAIS malhas estaticas trocadas pelas versoes separadas (para desfazer, devolva)
  Tags: FORJA_Spin, FORJA_Hammer, FORJA_Pump, FORJA_Swirl, FORJA_Pulse, FORJA_Flicker, FORJA_Burst, FORJA_Emitter

GANCHOS
  Rig real do Ignis: tag "FORJA_Ignis" no Model; KeyframeMarker "Golpe" (parametro opcional = forca) dispara as
  faiscas. Sem rig, o cliente usa um ritmo interno (toc-toc-TOC) e a tempera chia a cada 3 ciclos.
  Qualquer LocalScript: ReplicatedStorage.LOBBY_FORJA_VFX.Evento:Fire("ignis", 1.5)
  eventos: "ignis", "tempera", "martinete", "foles", "roda:entra", "roda:sai", "portal:<Nome>", "carga"
]]

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")

local ROOT_NAMES = {"LOBBY_FORJA", "LOBBY_FORJA_PREVIEW"} -- o primeiro que existir no workspace
-- texturas de agua que o jogo ja usa (StylizedWater da Vila da Folha / Vale Capsule); troque aqui se quiser outras
local TEX_AGUA = {
  linhas = "rbxassetid://123614169905314",     -- rede de linhas claras: ondulacao do rio e do canal
  cachoeira = "rbxassetid://108982815970120",  -- estrias: quedas
}
-- sentido das texturas dos Beams: 1 = corre de Attachment0 (bocal/montante) para Attachment1 (base/jusante), a mesma
-- convencao das cachoeiras do StylizedWater; se a agua aparecer SUBINDO no Studio, troque para -1
local SENTIDO_AGUA = 1
-- espirais: vazio = usa a textura que o montar aplicou no disco PORTAL_<Nome>_Swirl (TextureID ou SurfaceAppearance)
local SWIRL_IMG = {Naruto = "", DragonBall = "", ShadowGarden = "", DemonSlayer = "", OnePiece = "", OnePunchMan = ""}

if RunService:IsRunning() and not RunService:IsServer() then
  warn("[VFX Forja] vfx_lobby_forja.lua e a MONTAGEM (Command Bar ou Script de servidor), nao um LocalScript")
  return
end

local DATA = {}
DATA.version = "vfx-forja-2"
DATA.exportId = "28656663"  -- EXPORT_ID do passe estatico (montar_lobby_forja.lua grava em root:GetAttribute('EXPORT_ID'))
DATA.fbx = "LOBBY_VFX_MOVING_286566.fbx"  -- FBX de movimento DESTE passe (3D Importer)
-- referencias para achar a transformacao do lobby (posicao canonica = export_roblox, Roblox = (x, z, -y))
DATA.refs = {
  {name = "VFX_Waterwheel_Rotate", pos = Vector3.new(62, 11, -20), x = Vector3.new(0, -1, 0), y = Vector3.new(0, 0, -1)},
  {name = "NPC_Ignis", pos = Vector3.new(0, 5, 5), x = Vector3.new(-1, 0, 0), y = Vector3.new(0, 0, 1)},
  {name = "RAIL_Start_Mine", pos = Vector3.new(-89.627, 4.02, 79.77), x = Vector3.new(1, 0, 0), y = Vector3.new(0, 0, -1)},
  {name = "PORTAL_Naruto", pos = Vector3.new(-108, 41.2, -112.4), x = Vector3.new(1, 0, 0), y = Vector3.new(0, 0, -1)},
}
-- pecas do LOBBY_VFX_MOVING.fbx: {nome, grupo, centro do bbox (canonico), tamanho (Roblox)}
DATA.movers = {
  {"VFX_Roda__Metal_Dark", "roda", Vector3.new(54.05, 11, -20), Vector3.new(20.5, 2.8, 2.8)},
  {"VFX_Roda__Metal_Iron", "roda", Vector3.new(47.5, 11, -20.327), Vector3.new(0.5, 3.864, 3.346)},
  {"VFX_Roda__Metal_Rust", "roda", Vector3.new(62, 11, -20), Vector3.new(4.6, 18.4, 18.399)},
  {"VFX_Roda__Wood_Dark_B", "roda", Vector3.new(56.05, 11, -19.999), Vector3.new(24.9, 18.7, 18.697)},
  {"VFX_Roda__Wood_Light", "roda", Vector3.new(53.988, 11, -20), Vector3.new(19.975, 17.231, 17.231)},
  {"VFX_Roda__Wood_Plank_B", "roda", Vector3.new(62, 11, -20), Vector3.new(3.8, 16.15, 16.15)},
  {"VFX_Fixa__Metal_Dark", "fixa", Vector3.new(48.162, 12.977, -15.125), Vector3.new(13.175, 15.493, 13.95)},
  {"VFX_Fixa__Metal_Iron", "fixa", Vector3.new(48, 10.6, -19.75), Vector3.new(12.4, 13.2, 9.9)},
  {"VFX_Fixa__Metal_Rust", "fixa", Vector3.new(51.55, 13.1, -20), Vector3.new(35.3, 6.4, 3.4)},
  {"VFX_Fixa__Wood_Dark", "fixa", Vector3.new(49.194, 15.48, -18.515), Vector3.new(18.518, 22.96, 21.81)},
  {"VFX_Fixa__Wood_Light", "fixa", Vector3.new(48, 18.55, -8.7), Vector3.new(0.18, 2.3, 0.18)},
  {"VFX_Fixa__Wood_Plank_B", "fixa", Vector3.new(62, 2.4, -20), Vector3.new(6, 2.4, 24)},
  {"VFX_EixoAlto__Metal_Dark", "eixo_alto", Vector3.new(44.4, 15.5, -20), Vector3.new(1.2, 0.865, 0.91)},
  {"VFX_EixoAlto__Wood_Dark", "eixo_alto", Vector3.new(39.05, 15.5, -19.995), Vector3.new(11.7, 3.716, 3.66)},
  {"VFX_EixoAlto__Wood_Light", "eixo_alto", Vector3.new(44.4, 15.5, -20), Vector3.new(0.8, 2.6, 2.6)},
  {"VFX_Martinete__Metal_Dark", "martinete", Vector3.new(47.5, 7.2, -16), Vector3.new(1.8, 2, 1.8)},
  {"VFX_Martinete__Wood_Dark", "martinete", Vector3.new(47.5, 8.5, -21), Vector3.new(0.9, 1.896, 10.09)},
  {"VFX_Foles__Leather_Bellows", "foles", Vector3.new(35.35, 7.965, -15.41), Vector3.new(2.52, 4.269, 10.02)},
  {"VFX_Foles__Metal_Dark", "foles", Vector3.new(35.35, 8.995, -16.133), Vector3.new(2.7, 2.771, 6.957)},
  {"VFX_Foles__Wood_Plank_C", "foles", Vector3.new(35.35, 8.45, -15.375), Vector3.new(2.55, 4.076, 10.287)},
  {"VFX_Carrinho__Metal_Dark", "carrinho", Vector3.new(-56.579, 5.915, 28.288), Vector3.new(3.854, 3.07, 4.098)},
  {"VFX_Carrinho__Metal_Rust", "carrinho", Vector3.new(-56.579, 6.05, 28.288), Vector3.new(4.005, 2.6, 4.005)},
  {"VFX_CarrinhoCarga__Crystal_Blue", "carga", Vector3.new(-56.447, 8.512, 28.034), Vector3.new(2.99, 2.819, 1.984)},
}
-- malhas estaticas trocadas: objeto + familias de material, da variante (Wood_Dark: pega Wood_Dark_B) quando o
-- export estatico nao funde materiais nesse objeto, senao GROSSAS (Wood, Metal); materiais que brilham
-- (DATA.exact) contam pelo nome exato. So troca se TODOS os grupos existirem (tudo ou nada).
DATA.sources = {
  {name = "WATER_Waterwheel", fams = {"Metal_Dark", "Metal_Rust", "Wood_Dark", "Wood_Light", "Wood_Plank"}, groups = {"roda", "fixa", "eixo_alto"}},
  {name = "BLD_WheelHouse", fams = {"Metal_Dark", "Metal_Iron", "Wood_Dark", "Wood_Light"}, groups = {"roda", "eixo_alto", "martinete", "fixa"}},
  {name = "FORGE_Bellows_Top", fams = {"Leather", "Metal", "Wood"}, groups = {"foles"}},
}
DATA.exact = {["Lantern_Glow"] = true, ["Metal_Heated"] = true}
DATA.groups = {
  ["roda"] = {kind = "spin", assembly = "RodaDagua", pivot = Vector3.new(62, 11, -20), axis = Vector3.new(-1, 0, 0), speed = 0.628},
  ["fixa"] = {kind = "fixed", assembly = "Fixas"},
  ["eixo_alto"] = {kind = "spin", assembly = "CasaDaRoda", pivot = Vector3.new(44.4, 15.5, -20), axis = Vector3.new(1, 0, 0), speed = 1.257},
  ["martinete"] = {kind = "hammer", assembly = "CasaDaRoda", pivot = Vector3.new(47.5, 9, -25), axis = Vector3.new(-1, 0, 0), speed = 0.628, camPhase = 1.571, cams = 3, rest = 0.03, lift = 0.16, event = "martinete"},
  ["foles"] = {kind = "pump", assembly = "ForjaFoles", pivot = Vector3.new(35.35, 6.6, -10.4), axis = Vector3.new(-1, 0, 0), speed = 0.628, rest = 0, lift = 0.209, k = 1, event = "foles"},
  ["carrinho"] = {kind = "cart"},
  ["carga"] = {kind = "load"},
}
-- cor calibrada do montar (mesma do export_roblox), Material, transparencia, textura de detalhe
DATA.mats = {
  ["Crystal_Blue"] = {c = Color3.fromRGB(30, 140, 230), m = Enum.Material.SmoothPlastic, t = 0, x = nil},
  ["Leather_Bellows"] = {c = Color3.fromRGB(89, 53, 36), m = Enum.Material.Fabric, t = 0, x = nil},
  ["Metal_Dark"] = {c = Color3.fromRGB(78, 76, 76), m = Enum.Material.Metal, t = 0, x = nil},
  ["Metal_Iron"] = {c = Color3.fromRGB(116, 114, 112), m = Enum.Material.Metal, t = 0, x = nil},
  ["Metal_Rust"] = {c = Color3.fromRGB(142, 88, 58), m = Enum.Material.CorrodedMetal, t = 0, x = nil},
  ["Wood_Dark"] = {c = Color3.fromRGB(92, 64, 47), m = Enum.Material.Wood, t = 0, x = "wood"},
  ["Wood_Dark_B"] = {c = Color3.fromRGB(109, 74, 49), m = Enum.Material.Wood, t = 0, x = "wood"},
  ["Wood_Light"] = {c = Color3.fromRGB(148, 110, 80), m = Enum.Material.Wood, t = 0, x = "wood"},
  ["Wood_Plank_B"] = {c = Color3.fromRGB(143, 105, 71), m = Enum.Material.Wood, t = 0, x = "wood"},
  ["Wood_Plank_C"] = {c = Color3.fromRGB(107, 86, 69), m = Enum.Material.Wood, t = 0, x = "wood"},
}
DATA.texRules = {{"Stone_", "stone"}, {"P_OPM_Concrete", "stone"}, {"Wood_", "wood"}, {"Bark", "wood"}, {"Roof", "roof"}, {"Cliff_Rock", "rock"}, {"Grass", "grass"}, {"Plaster", "plaster"}, {"Dirt", "dirt"}}
DATA.portals = {
  {key = "Naruto", idx = 0, center = Vector3.new(-108, 41.2, -113.9), normal = Vector3.new(0, 0, 1), radius = 7.5, thick = 1.8, swirl = "PORTAL_Naruto_Swirl", spin = -0.9,
   rims = {"PORTAL_Naruto_Bandana__P_Naruto_Rim_Glow"}, disc = Color3.fromRGB(255, 110, 16), arm = Color3.fromRGB(255, 196, 96), core3 = Color3.fromRGB(255, 244, 214)},
  {key = "DragonBall", idx = 1, center = Vector3.new(-76, 41.2, -113.9), normal = Vector3.new(0, 0, 1), radius = 7.5, thick = 1.8, swirl = "PORTAL_DragonBall_Swirl", spin = 1.25,
   rims = {"PORTAL_DragonBall_Frame__P_DB_Rim_Glow"}, disc = Color3.fromRGB(30, 120, 240), arm = Color3.fromRGB(150, 214, 255), core3 = Color3.fromRGB(236, 248, 255)},
  {key = "ShadowGarden", idx = 2, center = Vector3.new(-44, 41.2, -113.9), normal = Vector3.new(0, 0, 1), radius = 7.5, thick = 1.8, swirl = "PORTAL_ShadowGarden_Swirl", spin = -0.55,
   rims = {"PORTAL_ShadowGarden_MoonArch__P_Shadow_Glow"}, disc = Color3.fromRGB(118, 38, 214), arm = Color3.fromRGB(208, 158, 255), core3 = Color3.fromRGB(244, 232, 255)},
  {key = "DemonSlayer", idx = 3, center = Vector3.new(44, 41.2, -113.9), normal = Vector3.new(0, 0, 1), radius = 7.5, thick = 1.8, swirl = "PORTAL_DemonSlayer_Swirl", spin = 1.05,
   rims = {"PORTAL_DemonSlayer_Tsuba__P_DS_Glow"}, disc = Color3.fromRGB(206, 28, 40), arm = Color3.fromRGB(255, 150, 138), core3 = Color3.fromRGB(255, 234, 226)},
  {key = "OnePiece", idx = 4, center = Vector3.new(76, 41.2, -113.9), normal = Vector3.new(0, 0, 1), radius = 7.5, thick = 1.8, swirl = "PORTAL_OnePiece_Swirl", spin = -0.75,
   rims = {"PORTAL_OnePiece_Pier__P_OP_Glow"}, disc = Color3.fromRGB(24, 92, 226), arm = Color3.fromRGB(138, 204, 255), core3 = Color3.fromRGB(228, 246, 255)},
  {key = "OnePunchMan", idx = 5, center = Vector3.new(108, 41.2, -113.9), normal = Vector3.new(0, 0, 1), radius = 7.5, thick = 1.8, swirl = "PORTAL_OnePunchMan_Swirl", spin = 1.45,
   rims = {"PORTAL_OnePunchMan_Wall__P_OPM_Glow"}, disc = Color3.fromRGB(232, 175, 0), arm = Color3.fromRGB(255, 236, 120), core3 = Color3.fromRGB(255, 250, 225)},
}
DATA.portalInner = 2.3
DATA.fx = {
  anvil_hammer = {pos = Vector3.new(47.5, 7, -16)},
  anvil_ignis = {pos = Vector3.new(0.5, 8.9, 10)},
  chimney = {pos = Vector3.new(0, 74.5, -30), radius = 7.6},
  hearth = {pos = Vector3.new(0, 7.7, -1.4), size = Vector3.new(8.5, 0.4, 3.22), height = 5.3},
  mine = {pos = Vector3.new(-88.123, 8, 79.953), size = Vector3.new(20, 8, 20)},
  quench = {pos = Vector3.new(-5, 6.2, 10), size = Vector3.new(1.4, 0.2, 1.4)},
  shed = {pos = Vector3.new(109.447, 8.909, 32.911), size = Vector3.new(12.994, 5.542, 8.836)},
  wheel_in = {pos = Vector3.new(62, 11.15, -29)},
  wheel_mist = {pos = Vector3.new(62, 10.95, -28.8)},
  wheel_out = {pos = Vector3.new(62, 11.15, -11)},
}
DATA.vents = {
  {pos = Vector3.new(-31.816, 29.521, -10.062), size = Vector3.new(3.753, 0.3, 3.524), rate = 1.2},
}
DATA.smokes = {
  {marker = "VFX_Smoke_Shop", pos = Vector3.new(39, 18.786, 28.97), rate = 2},
  {marker = "VFX_Smoke_Cabin_West_A", pos = Vector3.new(-81.6, 20.474, 12.25), rate = 2},
  {marker = "VFX_Smoke_Cabin_East_A", pos = Vector3.new(110.8, 21.103, 14.25), rate = 2},
  {marker = "VFX_Smoke_Cabin_West_C", pos = Vector3.new(-71.25, 19.2, -27.2), rate = 2},
}
DATA.wheelWidth = 3.4
DATA.waterfalls = {
  {name = "Center", top = Vector3.new(-1.631, 29.057, -79.528), base = Vector3.new(-2.058, 13.2, -77.94), width = 3, out = Vector3.new(-0.26, 0, 0.966), lip = 1.644, c0 = 7.802, c1 = -4.757, o0 = 0.35, o1 = 0.35},
  {name = "Center_2", top = Vector3.new(0.078, 25.334, -77.973), base = Vector3.new(0.128, 13.2, -77.94), width = 3, out = Vector3.new(0, 0, 1), lip = 0.033, c0 = 0.8, c1 = -3.64, o0 = 0.35, o1 = 0.35},
  {name = "Center_3", top = Vector3.new(1.572, 25.334, -77.973), base = Vector3.new(2.462, 13.2, -77.94), width = 3, out = Vector3.new(0.999, 0, 0.037), lip = 0.891, c0 = 4.247, c1 = -3.64, o0 = 0.35, o1 = 0.35},
  {name = "NE", top = Vector3.new(129.817, 55.343, -80.34), base = Vector3.new(129.571, 31.25, -79.99), width = 3, out = Vector3.new(-0.575, 0, 0.818), lip = 0.427, c0 = 2.8, c1 = -7.228, o0 = 0.35, o1 = 0.6},
  {name = "NE_2", top = Vector3.new(131.137, 52.776, -80.104), base = Vector3.new(131.363, 31.25, -79.99), width = 3, out = Vector3.new(0.893, 0, 0.45), lip = 0.254, c0 = 6.3, c1 = -6.458, o0 = 0.35, o1 = 0.35},
  {name = "NE_3", top = Vector3.new(128.907, 30.816, -76.433), base = Vector3.new(128.499, 13.2, -75.14), width = 3, out = Vector3.new(-0.301, 0, 0.954), lip = 1.355, c0 = 6.398, c1 = -5.285, o0 = 0.35, o1 = 0.35},
  {name = "NE_4", top = Vector3.new(131.505, 30.816, -76.433), base = Vector3.new(132.119, 13.2, -75.14), width = 3, out = Vector3.new(0.429, 0, 0.903), lip = 1.431, c0 = 4.503, c1 = -5.285, o0 = 0.35, o1 = 0.35},
  {name = "NE_5", top = Vector3.new(130.249, 28.953, -75.563), base = Vector3.new(130.173, 13.2, -75.14), width = 3, out = Vector3.new(-0.176, 0, 0.984), lip = 0.43, c0 = 2.3, c1 = -4.726, o0 = 0.35, o1 = 0.35},
  {name = "NW", top = Vector3.new(-122.563, 47.339, -80.339), base = Vector3.new(-122.672, 31.25, -79.99), width = 3, out = Vector3.new(-0.299, 0, 0.954), lip = 0.366, c0 = 5.3, c1 = -4.827, o0 = 0.35, o1 = 0.35},
  {name = "NW_2", top = Vector3.new(-121.135, 47.339, -80.339), base = Vector3.new(-120.72, 31.25, -79.99), width = 3, out = Vector3.new(0.765, 0, 0.644), lip = 0.542, c0 = 4.8, c1 = -4.827, o0 = 0.35, o1 = 0.35},
  {name = "NW_3", top = Vector3.new(-122.795, 30.816, -76.433), base = Vector3.new(-123.204, 13.2, -75.14), width = 3, out = Vector3.new(-0.302, 0, 0.953), lip = 1.356, c0 = 5.398, c1 = -5.285, o0 = 0.35, o1 = 0.35},
  {name = "NW_4", top = Vector3.new(-120.231, 30.816, -76.433), base = Vector3.new(-119.707, 13.2, -75.14), width = 3, out = Vector3.new(0.376, 0, 0.927), lip = 1.395, c0 = 3.453, c1 = -5.285, o0 = 0.35, o1 = 0.35},
  {name = "NW_5", top = Vector3.new(-121.096, 26.67, -75.167), base = Vector3.new(-121.274, 13.2, -75.14), width = 3, out = Vector3.new(0, 0, 1), lip = 0.027, c0 = 0.8, c1 = -4.041, o0 = 0.35, o1 = 0.35},
  {name = "Queda", top = Vector3.new(-1.548, 49.967, -131.933), base = Vector3.new(-1.863, 29.3, -130.44), width = 3, out = Vector3.new(-0.206, 0, 0.978), lip = 1.526, c0 = 8.136, c1 = -6.2, o0 = 0.35, o1 = 0.35},
  {name = "Queda_2", top = Vector3.new(2.261, 49.903, -131.935), base = Vector3.new(2.274, 29.3, -130.792), width = 3, out = Vector3.new(0.012, 0, 1), lip = 1.143, c0 = 2.101, c1 = -6.181, o0 = 0.35, o1 = 0.35},
  {name = "Queda_3", top = Vector3.new(3.014, 49.903, -131.935), base = Vector3.new(3.087, 29.3, -130.792), width = 3, out = Vector3.new(0.064, 0, 0.998), lip = 1.146, c0 = 2.104, c1 = -6.181, o0 = 0.35, o1 = 0.35},
  {name = "Queda_4", top = Vector3.new(1.916, 47.778, -130.929), base = Vector3.new(2.57, 29.3, -130.44), width = 3, out = Vector3.new(0.801, 0, 0.598), lip = 0.817, c0 = 3.143, c1 = -5.543, o0 = 0.35, o1 = 0.35},
  {name = "Queda_5", top = Vector3.new(0.116, 45.098, -130.471), base = Vector3.new(0.325, 29.3, -130.44), width = 3, out = Vector3.new(0.989, 0, 0.145), lip = 0.211, c0 = 2.8, c1 = -4.739, o0 = 0.35, o1 = 0.35},
  {name = "Queda_6", top = Vector3.new(62, 11.641, -29.248), base = Vector3.new(62, 6.092, -27.864), width = 3, out = Vector3.new(0, 0, 1), lip = 1.384, c0 = 1.937, c1 = -2, o0 = 0.35, o1 = 0.35},
  {name = "South", top = Vector3.new(60.341, -1.614, 66.711), base = Vector3.new(59.882, -19.6, 67.31), width = 3, out = Vector3.new(-0.609, 0, 0.794), lip = 0.755, c0 = 2.056, c1 = -5.396, o0 = 0.35, o1 = 0.35},
  {name = "South_2", top = Vector3.new(61.184, -7.875, 67.31), base = Vector3.new(61.446, -19.6, 67.31), width = 3, out = Vector3.new(1, 0, 0), lip = 0.263, c0 = 2.8, c1 = -3.517, o0 = 0.35, o1 = 0.35},
  {name = "South_3", top = Vector3.new(62.758, -20.014, 71.411), base = Vector3.new(62.604, -44, 72.21), width = 3, out = Vector3.new(-0.19, 0, 0.982), lip = 0.814, c0 = 2.139, c1 = -7.196, o0 = 0.35, o1 = 0.35},
  {name = "South_4", top = Vector3.new(63.84, -23.773, 72.082), base = Vector3.new(63.685, -44, 72.21), width = 3, out = Vector3.new(-0.772, 0, 0.636), lip = 0.201, c0 = 1.8, c1 = -6.068, o0 = 0.35, o1 = 0.35},
  {name = "Spill", top = Vector3.new(57.736, 12.735, -61.307), base = Vector3.new(57.404, 2.8, -59.14), width = 3, out = Vector3.new(-0.151, 0, 0.988), lip = 2.192, c0 = 4.069, c1 = -2.981, o0 = 0.35, o1 = 0.35},
  {name = "Spill_2", top = Vector3.new(59.33, 10.43, -59.185), base = Vector3.new(59.185, 2.8, -59.14), width = 3, out = Vector3.new(0, 0, 1), lip = 0.045, c0 = 0.8, c1 = -2.289, o0 = 0.35, o1 = 0.35},
  {name = "TerraceE", top = Vector3.new(91.615, 32.471, -76.284), base = Vector3.new(91.529, 13.2, -75.09), width = 3, out = Vector3.new(-0.072, 0, 0.997), lip = 1.198, c0 = 2.177, c1 = -5.781, o0 = 0.35, o1 = 0.35},
  {name = "TerraceE_2", top = Vector3.new(92.589, 30.429, -75.481), base = Vector3.new(92.683, 13.2, -75.09), width = 3, out = Vector3.new(0.234, 0, 0.972), lip = 0.402, c0 = 1.8, c1 = -5.169, o0 = 0.35, o1 = 0.35},
  {name = "TerraceW", top = Vector3.new(-60.371, 32.471, -76.284), base = Vector3.new(-60.627, 13.2, -75.09), width = 3, out = Vector3.new(-0.21, 0, 0.978), lip = 1.222, c0 = 3.71, c1 = -5.781, o0 = 0.35, o1 = 0.35},
  {name = "TerraceW_2", top = Vector3.new(-59.642, 32.471, -76.284), base = Vector3.new(-59.253, 13.2, -75.09), width = 3, out = Vector3.new(0.31, 0, 0.951), lip = 1.256, c0 = 2.259, c1 = -5.781, o0 = 0.35, o1 = 0.35},
}
DATA.flows = {
  {name = "Rio", a = Vector3.new(62, 2.88, -46.7), b = Vector3.new(62, 2.88, 2.5), width = 6.4, speed = 4},
  {name = "Rio", a = Vector3.new(62, 2.33, 5.1), b = Vector3.new(62, 2.33, 42.5), width = 6.4, speed = 4},
  {name = "Rio", a = Vector3.new(62, 1.78, 45.1), b = Vector3.new(62, 1.78, 61.7), width = 6.4, speed = 4},
}
DATA.cartRest = CFrame.new(-56.579, 4.3, 28.288) * CFrame.Angles(0, 1.245, 0)

local function log(fmt, ...) print("[VFX Forja] " .. string.format(fmt, ...)) end
local function warnf(fmt, ...) warn("[VFX Forja] " .. string.format(fmt, ...)) end

-- ---------------------------------------------------------------- raiz, passe de exportacao e transformacao
local root
for _, n in ipairs(ROOT_NAMES) do
  root = workspace:FindFirstChild(n)
  if root then break end
end
if not root then
  warnf("lobby nao encontrado no workspace (%s)", table.concat(ROOT_NAMES, ", "))
  return
end
local rootId = root:GetAttribute("EXPORT_ID")
if rootId ~= DATA.exportId then
  warnf("EXPORT_ID nao confere: lobby = %s, VFX = %s. O estatico (LOBBY_*.fbx + montar_lobby_forja.lua) e o VFX "
    .. "(LOBBY_VFX_MOVING.fbx + este script) tem que sair do MESMO export_all.py. Nada foi alterado.",
    tostring(rootId), tostring(DATA.exportId))
  return
end
if rootId == nil then log("montar sem EXPORT_ID: conferencia de passe desligada (reexporte com o export_all.py)") end
local RICO = root:GetAttribute("RICO") == true

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
-- nome sem o sufixo que o 3D Importer poe em nomes repetidos ('.001', ' (1)')
local function norm(n) return (string.gsub(string.gsub(n, "%.%d+$", ""), " %(%d+%)$", "")) end
-- material do nome "<objeto>__<material>[_k][_gX_Y]" (fatias _k e celulas _gX_Y do export estatico)
local function matOf(name)
  local s = string.match(norm(name), "__(.+)$")
  if not s then return nil end
  s = string.gsub(s, "_g%-?%d+_%-?%d+$", "")
  s = string.gsub(s, "_%d+$", "")
  s = string.gsub(s, "_g%-?%d+_%-?%d+$", "")
  return s
end
local function objOf(name) return string.match(norm(name), "^(.-)__") end
local function coarse(m)
  if not m then return nil end
  if DATA.exact[m] then return m end
  return string.match(m, "^([^_]+)") or m
end
local function famKey(m) return m and (string.match(m, "^(.-)_[A-Z]$") or m) end
local function texKey(m)
  if not m then return nil end
  for _, r in ipairs(DATA.texRules) do
    if string.sub(m, 1, #r[1]) == r[1] then return r[2] end
  end
  return nil
end
local function lerMapa(d)
  local ok, v = pcall(function() return d.TextureID end)
  if ok and v and v ~= "" then return v end
  local sa = d:FindFirstChildOfClass("SurfaceAppearance")
  if sa then
    local ok2, v2 = pcall(function() return sa.ColorMap end)
    if ok2 and v2 and v2 ~= "" then return v2 end
    local ok3, v3 = pcall(function() return sa.ColorMapContent.Uri end)
    if ok3 and v3 and v3 ~= "" then return v3 end
  end
  return nil
end

-- ---------------------------------------------------------------- pecas moveis (LOBBY_VFX_MOVING.fbx)
local wanted, ours = {}, {}
for _, m in ipairs(DATA.movers) do
  wanted[m[1]] = {group = m[2], home = m[3], size = m[4]}
  ours[objOf(m[1])] = true
end
-- so mexe em MeshParts deste exportador (grupos atuais + nomes da versao vfx-forja-1)
local LEGACY = {"VFX_RodaDagua", "VFX_CasaRoda", "VFX_Espiral_", "VFX_Carrinho"}
local function isOurs(name)
  local o = objOf(name)
  if not o then return false end
  if ours[o] then return true end
  for _, pre in ipairs(LEGACY) do
    if string.sub(o, 1, #pre) == pre then return true end
  end
  return false
end
local function sorted3(v)
  local t = {v.X, v.Y, v.Z}
  table.sort(t)
  return t
end
local function sizeErr(a, b)
  local s, w = sorted3(a), sorted3(b)
  return math.abs(s[1] - w[1]) + math.abs(s[2] - w[2]) + math.abs(s[3] - w[3]), 0.06 * (w[1] + w[2] + w[3]) + 0.3
end
local found, cands = {}, {}
-- nome exato E tamanho do bbox (mesmo nome com outro tamanho = peca de outro passe -> vira candidata)
local function scan(container, parked)
  for _, d in ipairs(container:GetDescendants()) do
    if d:IsA("MeshPart") and string.sub(d.Name, 1, 4) == "VFX_" and isOurs(d.Name) then
      local w = wanted[d.Name]
      local e, tol
      if w then e, tol = sizeErr(d.Size, w.size) end
      if w and e <= tol then
        if not found[d.Name] then
          found[d.Name] = d
        elseif found[d.Name] ~= d and not parked then
          d.Parent = ORIG -- duplicata (FBX importado duas vezes)
        end
      elseif not parked then
        table.insert(cands, d)
      end
    end
  end
end
scan(workspace)
scan(CFG)
scan(ORIG, true) -- pecas guardadas por uma montagem anterior (FBX incompleto na vez passada)
-- nome exato nao achado: mesmo objeto + mesma familia de material + mesmo tamanho (variante renomeada)
local nRen = 0
for _, m in ipairs(DATA.movers) do
  if not found[m[1]] then
    local o, f = objOf(m[1]), coarse(matOf(m[1]))
    local best, be, tol
    for i, d in ipairs(cands) do
      if objOf(d.Name) == o and coarse(matOf(d.Name)) == f then
        local e, t = sizeErr(d.Size, m[4])
        if not be or e < be then best, be, tol = i, e, t end
      end
    end
    if best and be <= tol then
      local d = table.remove(cands, best)
      d.Name = m[1]
      found[m[1]] = d
      nRen += 1
    end
  end
end
local nStale = 0
for _, d in ipairs(cands) do
  d.Parent = ORIG -- peca VFX de outro passe (nome/tamanho nao batem): fora da cena
  nStale += 1
end
if nRen > 0 then log("%d pecas moveis casadas por objeto + familia + tamanho (variante renomeada)", nRen) end
if nStale > 0 then warnf("%d MeshParts VFX_ de outro passe guardadas em ServerStorage (importe %s)", nStale, DATA.fbx) end

local groupCount, groupTotal = {}, {}
for _, m in ipairs(DATA.movers) do
  groupTotal[m[2]] = (groupTotal[m[2]] or 0) + 1
  if found[m[1]] then groupCount[m[2]] = (groupCount[m[2]] or 0) + 1 end
end
local function groupOk(g) return groupTotal[g] ~= nil and groupCount[g] == groupTotal[g] end

-- aparencia: copia de uma peca estatica com o mesmo material (cor, Material, textura: identica ao que o montar
-- aplicou, inclusive no modo RICO); sem peca-modelo, usa DATA.mats + a textura de uma peca da mesma familia
local looks, looksFam, texParts = {}, {}, {}
local function addLook(d)
  if not d:IsA("MeshPart") or wanted[d.Name] or string.sub(d.Name, 1, 4) == "VFX_" then return end
  local m = matOf(d.Name)
  if not m then return end
  looks[m] = looks[m] or d
  local fk = famKey(m)
  looksFam[fk] = looksFam[fk] or d
  local tk = texKey(m)
  if tk and not texParts[tk] and d:FindFirstChildOfClass("SurfaceAppearance") then texParts[tk] = d end
end
for _, d in ipairs(root:GetDescendants()) do addLook(d) end
for _, d in ipairs(ORIG:GetDescendants()) do addLook(d) end
local function applyLook(p, mat)
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  for _, c in ipairs(p:GetChildren()) do
    if c:IsA("SurfaceAppearance") then c:Destroy() end
  end
  local e = DATA.mats[mat]
  local src = looks[mat] or looksFam[famKey(mat)]
  if src then
    p.Color = src.Color
    p.Material = src.Material
    p.MaterialVariant = src.MaterialVariant
    p.Transparency = src.Transparency
    p.Reflectance = src.Reflectance
    p.CastShadow = src.CastShadow
    local sa = src:FindFirstChildOfClass("SurfaceAppearance")
    if sa then sa:Clone().Parent = p end
    p.TextureID = src.TextureID
  elseif e then
    p.Color = e.c
    p.Material = e.m
    p.Transparency = e.t
    local tp = RICO and e.x and texParts[e.x]
    local sa = tp and tp:FindFirstChildOfClass("SurfaceAppearance")
    if sa then sa:Clone().Parent = p end
    p.TextureID = ""
  else
    p.TextureID = ""
  end
end

-- fontes: esconde as malhas estaticas (objeto + familia) SO se TODAS as pecas de maquina existirem (tudo ou nada:
-- a malha FIXA e compartilhada; meia troca deixaria peca duplicada ou buraco)
local machineGroups, machineOk, missing = {}, true, {}
for _, s in ipairs(DATA.sources) do
  for _, g in ipairs(s.groups) do
    machineGroups[g] = true
    if groupTotal[g] and not groupOk(g) then
      machineOk = false
      missing[g] = groupTotal[g] - (groupCount[g] or 0)
    end
  end
end
if machineOk then
  for _, s in ipairs(DATA.sources) do
    local fams = {}
    for _, f in ipairs(s.fams) do fams[f] = true end
    local moved = 0
    for _, d in ipairs(root:GetDescendants()) do
      local m = d:IsA("MeshPart") and not wanted[d.Name] and objOf(d.Name) == s.name and matOf(d.Name)
      -- fams: familia GROSSA (Metal) ou da variante (Metal_Dark), conforme o export estatico funde materiais ou nao
      if m and (fams[coarse(m)] or fams[famKey(m)]) then
        d.Parent = ORIG
        moved += 1
      end
    end
    log("%s: %d malhas estaticas guardadas em ServerStorage (familias %s)", s.name, moved, table.concat(s.fams, ", "))
  end
else
  local t = {}
  for g, n in pairs(missing) do table.insert(t, g .. " (faltam " .. n .. ")") end
  warnf("%s incompleto: %s. Roda, engrenagens, martinete e fole ficam ESTATICOS "
    .. "(importe o FBX deste mesmo export e rode de novo)", DATA.fbx, table.concat(t, ", "))
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
local nMov = 0
for name, part in pairs(found) do
  local w = wanted[name]
  local g = DATA.groups[w.group]
  clearTags(part)
  applyLook(part, matOf(name))
  local home = rootCF * CFrame.new(w.home)
  part.CFrame = home
  if not g then
    part.Parent = MOVF
  elseif g.kind == "cart" or g.kind == "load" then
    table.insert(cartParts, {part, g.kind == "load"})
  elseif machineGroups[w.group] and not machineOk then
    part.Parent = ORIG -- maquina incompleta: nao mostra meia roda
  else
    part.Parent = assembly(g.assembly or "Pecas")
    nMov += 1
    if g.kind == "spin" then
      setMotion(part, home, g)
      CollectionService:AddTag(part, "FORJA_Spin")
    elseif g.kind == "hammer" then
      setMotion(part, home, g)
      part:SetAttribute("VFX_CamPhase", g.camPhase)
      part:SetAttribute("VFX_Cams", g.cams)
      part:SetAttribute("VFX_Rest", g.rest)
      part:SetAttribute("VFX_Lift", g.lift)
      part:SetAttribute("VFX_Event", g.event)
      CollectionService:AddTag(part, "FORJA_Hammer")
    elseif g.kind == "pump" then
      setMotion(part, home, g)
      part:SetAttribute("VFX_Rest", g.rest)
      part:SetAttribute("VFX_Lift", g.lift)
      part:SetAttribute("VFX_K", g.k)
      part:SetAttribute("VFX_Event", g.event)
      CollectionService:AddTag(part, "FORJA_Pump")
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

-- peca invisivel; posC canonico (ou cfW = CFrame do mundo); lookC = direcao da face Front (canonica)
local function host(name, posC, size, lookC, cfW)
  local p = Instance.new("Part")
  p.Name = name
  p.Size = size
  if cfW then
    p.CFrame = cfW
  else
    local cf = CFrame.new(posC)
    if lookC then cf = CFrame.lookAt(posC, posC + lookC) end
    p.CFrame = WCF(cf)
  end
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
local function attW(parent, name, cfC) -- CFrame canonico -> mundo
  local a = Instance.new("Attachment")
  a.Name = name
  a.Parent = parent
  a.WorldCFrame = WCF(cfC)
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
local function beam(parent, name, a0, a1, p)
  local b = Instance.new("Beam")
  b.Name = name
  b.Attachment0 = a0
  b.Attachment1 = a1
  b.FaceCamera = false
  b.Segments = p.segments or 12
  b.Texture = p.tex
  b.TextureMode = Enum.TextureMode.Wrap
  b.TextureLength = p.len or 6
  b.TextureSpeed = (p.speed or 1) * SENTIDO_AGUA
  b.Width0 = p.w0
  b.Width1 = p.w1 or p.w0
  b.CurveSize0 = p.c0 or 0
  b.CurveSize1 = p.c1 or 0
  b.LightEmission = p.emission or 0
  b.LightInfluence = p.influence or 1
  b.Color = CS(p.color or RGB(255, 255, 255))
  b.Transparency = NS(p.transp or 0)
  b.ZOffset = p.zoff or 0
  b.Parent = parent
  return b
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
local nEm, nBeam = 0, 0
local function count(n) nEm += n end

-- ---------------------------------------------------------------- FORJA (quente)
if FX.hearth then
  -- lamina no leito de brasas; hk = altura das chamas (props do VFX_Hearth_Fire) / 3,5 studs do ajuste original
  local hk = math.clamp((FX.hearth.height or 3.5) / 3.5, 0.7, 1.8)
  local sk = 0.6 + 0.4 * hk
  local h = host("Lareira_Fogo", FX.hearth.pos, FX.hearth.size)
  -- continuo + rajada a cada golpe do fole ("foles")
  emitter(h, "Chamas", {tex = TEX.dot, color = {{0, RGB(255, 246, 196)}, {0.25, RGB(255, 196, 78)}, {0.6, RGB(255, 112, 32)}, {1, RGB(150, 34, 12)}},
    size = {{0, 1.3 * sk}, {0.35, 2.2 * sk}, {1, 0.35}}, transp = {{0, 0.45}, {0.18, 0.08}, {0.75, 0.45}, {1, 1}},
    life = {0.55, 1.05}, rate = 30, speed = {2.5 * hk, 5 * hk}, spread = 12, accel = Vector3.new(0, 3.5 * hk, 0), drag = 0.6,
    emission = 1, bright = 2, rot = {0, 360}, rotspeed = {-40, 40}, zoff = 0.4, maxd = 320, event = "foles", count = 6})
  emitter(h, "Linguas", {tex = TEX.fire, color = {{0, RGB(255, 226, 150)}, {0.5, RGB(255, 132, 40)}, {1, RGB(190, 46, 18)}},
    size = {{0, 2.2 * sk}, {0.5, 3.0 * sk}, {1, 0.8}}, transp = {{0, 0.55}, {0.3, 0.2}, {1, 1}},
    life = {0.4, 0.8}, rate = 10, speed = {3 * hk, 6 * hk}, spread = 8, emission = 0.9, bright = 1.6, rot = {-25, 25}, maxd = 320})
  emitter(h, "Brasas", {tex = TEX.dot, color = RGB(255, 168, 60), size = {{0, 0.3}, {1, 0}}, transp = {{0, 0}, {0.8, 0.2}, {1, 1}},
    life = {0.9, 1.8}, rate = 5, speed = {2.5 * hk, 5 * hk}, spread = 25, accel = Vector3.new(0, 2, 1.4), drag = 0.4,
    emission = 1, bright = 3, maxd = 260, event = "foles", count = 6})
  count(3)
end
-- pluma da torre: nucleo escuro + corpo cinza que deriva + topo claro e transparente; brasas e faiscas
if FX.chimney then
  local r = FX.chimney.radius
  local h = host("Chamine_Pluma", FX.chimney.pos, Vector3.new(r * 1.3, 1, r * 1.3))
  emitter(h, "Nucleo", {tex = TEX.smoke, color = {{0, RGB(40, 36, 34)}, {1, RGB(72, 66, 62)}},
    size = {{0, 6}, {1, 18}}, transp = {{0, 1}, {0.05, 0.12}, {0.6, 0.4}, {1, 1}}, life = {4.5, 6.5}, rate = 3,
    speed = {8, 11}, spread = 6, accel = Vector3.new(1.2, 0.8, 0), drag = 0.3, influence = 1, rot = {0, 360},
    rotspeed = {-14, 14}, maxd = 3000})
  emitter(h, "Corpo", {tex = TEX.smoke, color = {{0, RGB(96, 90, 86)}, {0.5, RGB(128, 122, 118)}, {1, RGB(160, 156, 154)}},
    size = {{0, 10}, {0.4, 18}, {1, 28}}, transp = {{0, 1}, {0.08, 0.32}, {0.6, 0.5}, {1, 1}}, life = {7, 10}, rate = 3.5,
    speed = {6, 9}, spread = 10, accel = Vector3.new(2, 1.5, 0), drag = 0.25, influence = 1, rot = {0, 360},
    rotspeed = {-10, 10}, maxd = 3000})
  local top = host("Chamine_PlumaTopo", FX.chimney.pos + Vector3.new(0, 7, 0), Vector3.new(r * 1.8, 2, r * 1.8))
  emitter(top, "Topo", {tex = TEX.smoke, color = {{0, RGB(178, 174, 172)}, {1, RGB(216, 214, 214)}},
    size = {{0, 14}, {1, 40}}, transp = {{0, 1}, {0.15, 0.62}, {0.7, 0.78}, {1, 1}}, life = {9, 12}, rate = 1.6,
    speed = {4, 6}, spread = 14, accel = Vector3.new(2.6, 1.0, 0), drag = 0.2, influence = 1, rot = {0, 360},
    rotspeed = {-8, 8}, maxd = 3000})
  emitter(h, "Brasas", {tex = TEX.dot, color = {{0, RGB(255, 214, 120)}, {1, RGB(255, 96, 24)}}, size = {{0, 0.55}, {1, 0}},
    transp = {{0, 0}, {0.8, 0.2}, {1, 1}}, life = {2, 3.5}, rate = 4, speed = {9, 15}, spread = 22,
    accel = Vector3.new(1.5, -3, 0), drag = 0.5, emission = 1, bright = 3, maxd = 900})
  emitter(h, "Faiscas", {tex = TEX.dot, color = {{0, RGB(255, 236, 170)}, {1, RGB(255, 120, 30)}}, size = {{0, 0.4}, {1, 0.05}},
    transp = {{0, 0}, {1, 1}}, life = {0.8, 1.4}, rate = 2, speed = {18, 26}, spread = 18, accel = Vector3.new(0, -12, 0),
    drag = 0.8, emission = 1, bright = 4, orient = Enum.ParticleOrientation.VelocityParallel, squash = 1.6, maxd = 900,
    event = "foles", count = 10})
  count(5)
end
-- fumaca fina nos respiros do telhado da forja
for i, v in ipairs(DATA.vents) do
  local h = host("Respiro_" .. i, v.pos, v.size)
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(150, 146, 142)}, {1, RGB(180, 178, 176)}},
    size = {{0, 1.4}, {1, 6}}, transp = {{0, 1}, {0.12, 0.55}, {1, 1}}, life = {4, 6}, rate = v.rate, speed = {2, 3.5},
    spread = 12, accel = Vector3.new(1.2, 0.6, 0), drag = 0.3, influence = 1, rot = {0, 360}, rotspeed = {-12, 12}, maxd = 600})
  count(1)
end
local function anvilFX(name, posC, event, sparks, speedMax, peak, loop)
  local h = host(name, posC, Vector3.new(0.6, 0.2, 0.6))
  local a = att(h, "Topo")
  emitter(a, "Faiscas", {tex = TEX.dot, color = {{0, RGB(255, 250, 214)}, {0.4, RGB(255, 192, 82)}, {1, RGB(255, 108, 30)}},
    size = {{0, 0.28}, {1, 0.06}}, transp = {{0, 0}, {0.7, 0.1}, {1, 1}}, life = {0.3, 0.75}, speed = {speedMax * 0.5, speedMax},
    spread = 75, accel = Vector3.new(0, -60, 0), drag = 1.4, emission = 1, bright = 4,
    orient = Enum.ParticleOrientation.VelocityParallel, squash = 2, event = event, count = sparks})
  emitter(a, "Brilho", {tex = TEX.dot, color = RGB(255, 204, 128), size = {{0, 2.2}, {1, 5}}, transp = {{0, 0.35}, {1, 1}},
    life = {0.16}, speed = {0}, emission = 1, bright = 3, event = event, count = 1})
  if loop then
    -- faiscas miudas em loop: a bigorna nunca fica "morta" entre os golpes
    emitter(a, "FaiscasLoop", {tex = TEX.dot, color = {{0, RGB(255, 236, 180)}, {1, RGB(255, 120, 36)}},
      size = {{0, 0.18}, {1, 0.04}}, transp = {{0, 0}, {1, 1}}, life = {0.25, 0.55}, rate = loop, speed = {5, 10},
      spread = 60, accel = Vector3.new(0, -50, 0), drag = 1.2, emission = 1, bright = 3,
      orient = Enum.ParticleOrientation.VelocityParallel, squash = 1.5, maxd = 220})
  end
  flashLight(h, RGB(255, 160, 70), 14, peak, event)
  count(loop and 3 or 2)
  return h, a
end
anvilFX("Bigorna_Ignis", FX.anvil_ignis.pos, "ignis", 14, 26, 4, 2.5)
local _, ah = anvilFX("Bigorna_Martinete", FX.anvil_hammer.pos, "martinete", 9, 18, 3)
emitter(ah, "Po", {tex = TEX.smoke, color = RGB(128, 118, 108), size = {{0, 0.8}, {1, 2.6}}, transp = {{0, 0.5}, {1, 1}},
  life = {0.6, 1.1}, speed = {2, 4}, spread = 80, accel = Vector3.new(0, 1, 0), drag = 2, influence = 1,
  event = "martinete", count = 4})
count(1)
if FX.quench then
  local q = host("Tempera_Vapor", FX.quench.pos, FX.quench.size)
  emitter(q, "Vapor", {tex = TEX.smoke, color = RGB(236, 240, 244), size = {{0, 0.8}, {1, 3.6}},
    transp = {{0, 1}, {0.15, 0.55}, {1, 1}}, life = {1.6, 2.6}, rate = 1.5, speed = {1.5, 3}, spread = 18,
    accel = Vector3.new(0.4, 1.4, 0), drag = 0.6, influence = 0.8, rot = {0, 360}, rotspeed = {-30, 30}, maxd = 260})
  emitter(q, "Chiado", {tex = TEX.smoke, color = RGB(246, 248, 250), size = {{0, 1.2}, {1, 5.5}},
    transp = {{0, 0.35}, {1, 1}}, life = {1.2, 2.2}, speed = {3, 6}, spread = 25, accel = Vector3.new(0.4, 2.5, 0),
    drag = 0.8, influence = 0.8, rot = {0, 360}, rotspeed = {-40, 40}, event = "tempera", count = 14})
  count(2)
end

-- ---------------------------------------------------------------- AGUA (frio): roda, quedas, correntes
do
  local ww = DATA.wheelWidth
  local o = host("Roda_Respingo", FX.wheel_out.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(o, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.45}, {1, 0.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {0.5, 0.9}, rate = 10, speed = {6, 11}, spread = 30, accel = Vector3.new(0, -40, 3), drag = 0.5,
    emission = 0.3, influence = 0.6, orient = Enum.ParticleOrientation.VelocityParallel, squash = 0.8, maxd = 300})
  -- rajada sincronizada com a pa que sai da agua (evento do cliente, pela fase da roda)
  emitter(o, "Pa", {tex = TEX.dot, color = RGB(236, 248, 255), size = {{0, 0.55}, {1, 0.2}}, transp = {{0, 0.1}, {1, 1}},
    life = {0.5, 0.9}, speed = {7, 12}, spread = 25, accel = Vector3.new(0, -40, 2), drag = 0.5, emission = 0.3,
    influence = 0.6, orient = Enum.ParticleOrientation.VelocityParallel, squash = 0.8, event = "roda:sai", count = 9})
  local i = host("Roda_Entrada", FX.wheel_in.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(i, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.4}, {1, 0.15}}, transp = {{0, 0.2}, {1, 1}},
    life = {0.35, 0.6}, rate = 4, speed = {3, 6}, spread = 40, accel = Vector3.new(0, -40, 0), drag = 0.5,
    emission = 0.3, influence = 0.6, maxd = 300})
  emitter(i, "Pa", {tex = TEX.dot, color = RGB(236, 248, 255), size = {{0, 0.5}, {1, 0.15}}, transp = {{0, 0.1}, {1, 1}},
    life = {0.35, 0.6}, speed = {4, 8}, spread = 45, accel = Vector3.new(0, -40, 0), drag = 0.5, emission = 0.3,
    influence = 0.6, event = "roda:entra", count = 6})
  local m = host("Roda_Nevoa", FX.wheel_mist.pos, Vector3.new(ww + 1, 0.5, 4))
  emitter(m, "Espuma", {tex = TEX.smoke, color = RGB(240, 248, 255), size = {{0, 1.5}, {1, 4.5}}, transp = {{0, 0.5}, {1, 1}},
    life = {1.2, 2}, rate = 4, speed = {1, 2.5}, spread = 40, drag = 1, influence = 0.7, rot = {0, 360}, maxd = 300})
  count(5)
end
-- cachoeiras: 2 Beams com estrias (corpo + brilho) seguindo a queda + nevoa e espuma na base
for _, wf in ipairs(DATA.waterfalls) do
  local w = wf.width
  local out = wf.out
  local lat = UP:Cross(out).Unit
  -- curva ajustada no export (fit_beam): corre na frente da cortina de agua do bocal ate a base
  local top = wf.top + out * (wf.o0 or 0.35)
  local base = wf.base + out * (wf.o1 or 0.35)
  local fall = top.Y - base.Y
  local hb = host("Queda_" .. wf.name, (top + base) / 2, Vector3.new(1, 1, 1))
  local a0 = attW(hb, "Topo", CFrame.fromMatrix(top, out, lat))
  local a1 = attW(hb, "Base", CFrame.fromMatrix(base, UP, lat))
  local c0 = wf.c0 or math.clamp(wf.lip * 1.4, 0.8, 6)
  local c1 = wf.c1 or -math.clamp(fall * 0.3, 2, 24)
  beam(hb, "Agua", a0, a1, {tex = TEX_AGUA.cachoeira, len = 6, speed = 1.2, w0 = w, w1 = w * 1.08, c0 = c0, c1 = c1,
    emission = 0.3, influence = 0.7, color = {{0, RGB(214, 240, 255)}, {1, RGB(176, 222, 246)}},
    transp = {{0, 0.3}, {0.08, 0.06}, {0.9, 0.1}, {1, 0.45}}, zoff = 0.3, segments = 16})
  beam(hb, "Brilho", a0, a1, {tex = TEX_AGUA.cachoeira, len = 9, speed = 2, w0 = w * 0.6, w1 = w * 0.7, c0 = c0 * 1.05,
    c1 = c1 * 0.95, emission = 0.45, influence = 0.4, color = RGB(255, 255, 255), transp = {{0, 0.5}, {1, 0.7}},
    zoff = 0.5, segments = 16})
  nBeam += 2
  local b = host("Queda_" .. wf.name .. "_Base", base + Vector3.new(0, 0.3, 0), Vector3.new(w + 1.5, 0.6, 3), wf.out)
  emitter(b, "Nevoa", {tex = TEX.smoke, color = RGB(236, 245, 255), size = {{0, math.clamp(w * 0.45, 3, 7)}, {1, math.clamp(w * 1.15, 6, 14)}},
    transp = {{0, 0.72}, {0.3, 0.55}, {1, 1}}, life = {2.5, 4}, rate = math.clamp(w * 0.35, 1.5, 4), speed = {1.5, 3.5},
    spread = 45, accel = Vector3.new(0, 0.6, 0), drag = 0.6, influence = 0.8, rot = {0, 360}, rotspeed = {-10, 10}, maxd = 650})
  emitter(b, "Espuma", {tex = TEX.smoke, color = RGB(250, 253, 255), size = {{0, 1.4}, {1, 3.2}}, transp = {{0, 0.25}, {1, 1}},
    life = {0.6, 1.1}, rate = math.clamp(w * 1.4, 5, 12), speed = {4, 8}, spread = 35, accel = Vector3.new(0, -18, 0),
    drag = 0.8, influence = 0.7, rot = {0, 360}, maxd = 450})
  count(2)
end
-- rio (-Y) e canal (para o vertedouro): ondulacao rolando no sentido do fluxo (Beam deitado na agua)
for _, f in ipairs(DATA.flows) do
  local dir = (f.b - f.a).Unit
  local lat = UP:Cross(dir).Unit
  local h = host("Corrente_" .. f.name, (f.a + f.b) / 2, Vector3.new(1, 1, 1))
  local a0 = attW(h, "Montante", CFrame.fromMatrix(f.a, dir, lat))
  local a1 = attW(h, "Jusante", CFrame.fromMatrix(f.b, dir, lat))
  beam(h, "Ondulacao", a0, a1, {tex = TEX_AGUA.linhas, len = 16, speed = f.speed / 16, w0 = f.width, emission = 0.12,
    influence = 0.9, color = RGB(236, 248, 255), transp = {{0, 1}, {0.04, 0.6}, {0.96, 0.6}, {1, 1}}, segments = 2,
    zoff = 0.05})
  nBeam += 1
end

-- ---------------------------------------------------------------- PORTAIS: espiral em SurfaceGui + sugadas + aro
local nSwirl, nSug, nRim = 0, 0, 0
for _, p in ipairs(DATA.portals) do
  local key, R, n = p.key, p.radius, p.normal
  local u = UP:Cross(n).Unit
  local v = n:Cross(u).Unit
  local discs = {}
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA("MeshPart") and string.sub(d.Name, 1, #p.swirl + 2) == p.swirl .. "__" then table.insert(discs, d) end
  end
  -- disco modelado: gira no mesmo relogio (leitura de tras e de lado; de frente o SurfaceGui cobre)
  for _, d in ipairs(discs) do
    clearTags(d)
    d:SetAttribute("VFX_Home", d.CFrame)
    d:SetAttribute("VFX_Pivot", W(p.center))
    d:SetAttribute("VFX_Axis", WV(n).Unit)
    d:SetAttribute("VFX_Speed", p.spin)
    d:SetAttribute("VFX_Phase", 0)
    d:SetAttribute("VFX_Portal", key)
    CollectionService:AddTag(d, "FORJA_Spin")
  end
  -- espiral: SurfaceGui na face voltada ao jogador, sem luz do sol (brilha de dia); 2 ImageLabels girando
  local img = SWIRL_IMG[key] or ""
  if img == "" and discs[1] then img = lerMapa(discs[1]) or "" end
  if img ~= "" then
    local h = host("Portal_" .. key .. "_Espiral", p.center + n * (p.thick / 2 + 0.08), Vector3.new(R * 2.04, R * 2.04, 0.05), n)
    local sg = Instance.new("SurfaceGui")
    sg.Name = "Espiral"
    sg.Face = Enum.NormalId.Front
    sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    sg.PixelsPerStud = 32
    sg.LightInfluence = 0
    sg.Brightness = 2.4
    sg.MaxDistance = 700
    sg.ClipsDescendants = false
    sg.Parent = h
    local function label(name, scale, transp, z)
      local l = Instance.new("ImageLabel")
      l.Name = name
      l.BackgroundTransparency = 1
      l.AnchorPoint = Vector2.new(0.5, 0.5)
      l.Position = UDim2.fromScale(0.5, 0.5)
      l.Size = UDim2.fromScale(scale, scale)
      l.Image = img
      l.ImageTransparency = transp
      l.ZIndex = z
      l.Parent = sg
      return l
    end
    label("Externa", 1, 0, 1)
    label("Interna", 0.55, 0.22, 2)
    h:SetAttribute("VFX_Speed", p.spin)
    h:SetAttribute("VFX_InnerMul", DATA.portalInner)
    h:SetAttribute("VFX_Portal", key)
    h:SetAttribute("VFX_Bright", 2.4)
    CollectionService:AddTag(h, "FORJA_Swirl")
    nSwirl += 1
  else
    warnf("portal %s: disco sem textura de espiral (rode o montar com a textura ou preencha SWIRL_IMG) - so o disco gira", key)
  end
  -- particulas sugadas: presas no disco que gira (nascem no aro e correm para o centro, na cor do portal)
  local ringHost = discs[1]
  local ph = host("Portal_" .. key, p.center, Vector3.new(1, 1, 1))
  if not ringHost then ringHost = ph end
  for _, c in ipairs(ringHost:GetChildren()) do
    if c:IsA("Attachment") and string.sub(c.Name, 1, 7) == "Sugada_" then c:Destroy() end
  end
  local f = p.thick / 2 + 0.45
  local wc, wn, wu, wv = W(p.center), WV(n).Unit, WV(u).Unit, WV(v).Unit
  for k = 0, 2 do
    local ang = math.pi * 2 * k / 3 + 0.4
    local pos = wc + (wu * math.cos(ang) + wv * math.sin(ang)) * R * 0.92 + wn * f
    local a = Instance.new("Attachment")
    a.Name = "Sugada_" .. k
    a.Parent = ringHost
    a.WorldCFrame = CFrame.lookAt(pos, wc + wn * f)
    emitter(a, "Sugadas", {tex = TEX.star, color = {{0, p.arm}, {1, p.core3}}, size = {{0, 0.15}, {0.2, 0.75}, {1, 0.1}},
      transp = {{0, 1}, {0.15, 0.1}, {1, 0.35}}, life = {1.15}, rate = 5, speed = {R * 0.92 / 1.15 * 0.95},
      spread = 6, dir = Enum.NormalId.Front, emission = 1, bright = 2, zoff = 0.3, maxd = 450})
    count(1)
    nSug += 1
  end
  local fa = att(ph, "Frente", CFrame.lookAt(n * 0.35, n * 1.35)) -- espaco local do host = canonico
  emitter(fa, "Pulso", {tex = TEX.ring, color = p.core3, size = {{0, 3}, {1, 2 * R * 1.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {1.1}, speed = {0.3}, dir = Enum.NormalId.Front, orient = Enum.ParticleOrientation.VelocityPerpendicular,
    emission = 1, bright = 2, event = "portal:" .. key, count = 1})
  count(1)
  -- aro Neon (geometria do portal): pulsa junto com o portal
  local rimSet = {}
  for _, r in ipairs(p.rims) do rimSet[r] = true end
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA("MeshPart") then
      local base = string.match(d.Name, "^(.-)_%d+$")
      if rimSet[d.Name] or (base and rimSet[base]) then
        clearTags(d)
        d:SetAttribute("VFX_Kind", "portalrim")
        d:SetAttribute("VFX_Event", "portal:" .. key)
        d:SetAttribute("VFX_BaseColor", d.Color)
        CollectionService:AddTag(d, "FORJA_Pulse")
        nRim += 1
      end
    end
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

-- ---------------------------------------------------------------- VILA: fumaca fina em poucas chamines
for _, s in ipairs(DATA.smokes) do
  local mkp = markers and markers:FindFirstChild(s.marker)
  local rate = (mkp and tonumber(mkp:GetAttribute("rate"))) or s.rate or 2
  local nm = "Chamine_" .. string.sub(s.marker, 11)
  local h
  if mkp and mkp:IsA("BasePart") then
    h = host(nm, nil, Vector3.new(0.8, 0.3, 0.8), nil, CFrame.new(mkp.Position))
  else
    h = host(nm, s.pos, Vector3.new(0.8, 0.3, 0.8))
  end
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(150, 146, 142)}, {1, RGB(186, 184, 182)}},
    size = {{0, 1.2}, {1, 5}}, transp = {{0, 1}, {0.12, 0.5}, {1, 1}}, life = {5, 7}, rate = rate, speed = {2, 3.2},
    spread = 8, accel = Vector3.new(1.2, 0.4, 0), drag = 0.3, influence = 1, rot = {0, 360}, rotspeed = {-12, 12}, maxd = 700})
  count(1)
end

-- ---------------------------------------------------------------- tags das pecas estaticas (pulsos e flicker)
local nPulse, nLight = 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and d.Parent ~= ORIG and not CollectionService:HasTag(d, "FORJA_Spin") then
    local n = d.Name
    local kind, event, amp
    if string.find(n, "__Crystal_", 1, true) then
      kind = "crystal"
    elseif string.find(n, "__Metal_Heated", 1, true) then
      kind = "heat"
      if string.sub(n, 1, 12) == "FORGE_Anvil_" then event = "ignis"
      elseif string.sub(n, 1, 15) == "BLD_WheelHouse_" then event = "martinete" end
    elseif string.find(n, "__Ember_Glow", 1, true) then
      kind = "heat"
      if string.sub(n, 1, 12) == "FORGE_Anvil_" then event = "ignis" end
    elseif string.find(n, "__Fire_Glow_", 1, true) then
      kind = "ember"
    elseif string.sub(n, 1, 6) == "FORGE_" and (string.find(n, "__Forge_Glow_Soft", 1, true) or string.find(n, "__Forge_Emissive", 1, true)) then
      kind, amp = "ember", 0.5
    elseif string.find(n, "__Lantern_Glow", 1, true) then
      kind = "lantern"
    end
    if kind and CollectionService:HasTag(d, "FORJA_Pulse") and d:GetAttribute("VFX_Kind") == "portalrim" then
      kind = nil -- aro de portal ja marcado acima
    end
    if kind then
      if CollectionService:HasTag(d, "FORJA_Pulse") then CollectionService:RemoveTag(d, "FORJA_Pulse") end
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event or "")
      d:SetAttribute("VFX_Amp", amp or 1)
      d:SetAttribute("VFX_BaseColor", d:GetAttribute("VFX_BaseColor") or d.Color)
      CollectionService:AddTag(d, "FORJA_Pulse")
      nPulse += 1
    end
  elseif (d:IsA("PointLight") or d:IsA("SpotLight")) and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "LIGHTS" then
    local n = d.Parent.Name
    local kind, event = "lantern", ""
    if string.sub(n, 1, 9) == "L_Portal_" then
      kind, event = "portal", "portal:" .. string.sub(n, 10)
    elseif string.sub(n, 1, 12) == "L_HearthLamp" then
      kind = "lantern"                                   -- lanternas ao lado da boca: nao sao fogo
    elseif n == "L_Hearth_Fire" then
      kind, event = "fire", "foles"                      -- respira com o fole (1,3x no golpe)
    elseif string.sub(n, 1, 8) == "L_Hearth" or string.sub(n, 1, 9) == "L_Furnace" or n == "L_DS_Oni"
      or string.sub(n, 1, 12) == "L_DS_Brazier" or string.sub(n, 1, 13) == "L_Tower_Crown" then
      kind = "fire"                                      -- (rever L_DS_* quando o Demon Slayer for redesenhado)
    elseif n == "L_Mine_Chamber" or n == "L_Mine_Tunnel" or n == "L_Shed_Light" then
      kind = "crystal"
    elseif n == "L_Hall_Fill" or n == "L_Shop_Fill" or n == "L_Konoha_Gate" then
      kind = nil
    end
    if CollectionService:HasTag(d, "FORJA_Flicker") then CollectionService:RemoveTag(d, "FORJA_Flicker") end
    if kind then
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event)
      d:SetAttribute("VFX_Base", d:GetAttribute("VFX_Base") or d.Brightness)
      CollectionService:AddTag(d, "FORJA_Flicker")
      nLight += 1
    end
  end
end

CFG:SetAttribute("VFX_Version", DATA.version)
CFG:SetAttribute("VFX_ExportId", DATA.exportId or "")
CFG:SetAttribute("VFX_RootCF", rootCF)
CFG:SetAttribute("VFX_Root", root:GetFullName())
CFG:SetAttribute("VFX_Ready", true)
log("pronto (%s): referencia %s | %d pecas moveis%s, %d emissores, %d beams, %d espirais, %d sugadas, %d aros, %d pulsos, %d luzes, carrinho %s",
  DATA.version, refName, nMov, machineOk and "" or " (maquinas ESTATICAS: FBX incompleto)", nEm, nBeam, nSwirl, nSug,
  nRim, nPulse, nLight, (#cartParts > 0) and "malha" or "Parts")
