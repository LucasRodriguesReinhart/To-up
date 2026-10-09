-- montar_lobby_santuario.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 06bf5662
-- 1) Importe os FBX LOBBY_SN_*_06bf56.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script LOBBY_FORJA_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = '06bf5662'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o lobby Santuario do Deus-Ferreiro INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('LOBBY_FORJA') or Instance.new('Model', workspace)
root.Name = 'LOBBY_FORJA'
root:SetAttribute('EXPORT_ID', EXPORT_ID); root:SetAttribute('RICO', RICO)
local CS = game:GetService('CollectionService')
local PS = game:GetService('PhysicsService')
local function folder(n) local f = root:FindFirstChild(n) or Instance.new('Folder'); f.Name = n; f.Parent = root; return f end
local COLF, MKF, LTF = folder('COLLISION'), folder('GAMEPLAY_MARKERS'), folder('LIGHTS')
local function cf(p, x, y) local px = Vector3.new(p[1],p[2],p[3]) + ROOT_OFFSET
  local vx = Vector3.new(x[1],x[2],x[3]); local vy = Vector3.new(y[1],y[2],y[3])
  return CFrame.fromMatrix(px, vx, vy) end
local function grupo(n) pcall(function() if not PS:IsCollisionGroupRegistered(n) then PS:RegisterCollisionGroup(n) end end) end
grupo('SoVisual'); grupo('Personagens')
pcall(function() PS:CollisionGroupSetCollidable('SoVisual', 'Personagens', false) end)
-- ids das texturas (rbxassetid://...). Vazio = usa o que o 3D Importer subiu (lido das MeshParts).
-- Alternativa: suba as PNG de textures/ pelo Asset Manager e cole os ids aqui.
local TEX = {
  ['P_DB_Swirl'] = '',  -- textures/T_swirl_db_v6.png (espiral, UV do disco)
  ['P_DS_Swirl'] = '',  -- textures/T_swirl_ds_v5.png (espiral, UV do disco)
  ['P_Naruto_Swirl'] = '',  -- textures/T_swirl_naruto_v5.png (espiral, UV do disco)
  ['P_OPM_Swirl'] = '',  -- textures/T_swirl_opm_v6.png (espiral, UV do disco)
  ['P_OP_Swirl'] = '',  -- textures/T_swirl_op_v4.png (espiral, UV do disco)
  ['P_Shadow_Swirl'] = '',  -- textures/T_swirl_shadow_v4.png (espiral, UV do disco)
  ['dirt'] = '',  -- textures/T_dirt_v3.png (10.0 studs por repeticao)
  ['grass'] = '',  -- textures/T_grass_v3.png (14.0 studs por repeticao)
  ['plaster'] = '',  -- textures/T_plaster_v3.png (8.0 studs por repeticao)
  ['rock'] = '',  -- textures/T_rock_v3.png (18.0 studs por repeticao)
  ['roof'] = '',  -- textures/T_roof_v3.png (5.0 studs por repeticao)
  ['sn_ashlar'] = '',  -- textures/SN_ashlar_v1.png (8.0 studs por repeticao)
  ['sn_ashlar_dark'] = '',  -- textures/SN_ashlar_dark_v1.png (8.0 studs por repeticao)
  ['sn_ashlar_moss'] = '',  -- textures/SN_ashlar_moss_v1.png (8.0 studs por repeticao)
  ['sn_basalt'] = '',  -- textures/SN_basalt_v1.png (14.0 studs por repeticao)
  ['sn_bronze'] = '',  -- textures/SN_bronze_v1.png (5.0 studs por repeticao)
  ['sn_carved'] = '',  -- textures/SN_carved_v1.png (8.0 studs por repeticao)
  ['sn_hills'] = '',  -- textures/SN_hills_v1.png (1.0 studs por repeticao)
  ['sn_moss'] = '',  -- textures/SN_moss_v1.png (8.0 studs por repeticao)
  ['sn_mountain'] = '',  -- textures/SN_mountain_v1.png (1.0 studs por repeticao)
  ['sn_plaza'] = '',  -- textures/SN_plaza_v1.png (10.0 studs por repeticao)
  ['sn_rock_far'] = '',  -- textures/SN_rock_far_v1.png (90.0 studs por repeticao)
  ['sn_rubble'] = '',  -- textures/SN_rubble_v1.png (6.0 studs por repeticao)
  ['sn_snow_far'] = '',  -- textures/SN_snow_far_v1.png (120.0 studs por repeticao)
  ['sn_wood_aged'] = '',  -- textures/SN_wood_aged_v1.png (6.0 studs por repeticao)
  ['snb_anvil_1'] = '',  -- textures/SNB_Anvil_1.png (1.0 studs por repeticao)
  ['snb_anvil_2'] = '',  -- textures/SNB_Anvil_2.png (1.0 studs por repeticao)
  ['snb_anvil_3'] = '',  -- textures/SNB_Anvil_3.png (1.0 studs por repeticao)
  ['snb_anvil_4'] = '',  -- textures/SNB_Anvil_4.png (1.0 studs por repeticao)
  ['snb_anvil_5'] = '',  -- textures/SNB_Anvil_5.png (1.0 studs por repeticao)
  ['snb_anvil_6'] = '',  -- textures/SNB_Anvil_6.png (1.0 studs por repeticao)
  ['snb_anvil_7'] = '',  -- textures/SNB_Anvil_7.png (1.0 studs por repeticao)
  ['snb_anvil_8'] = '',  -- textures/SNB_Anvil_8.png (1.0 studs por repeticao)
  ['snb_avenue'] = '',  -- textures/SNB_Avenue.png (1.0 studs por repeticao)
  ['snb_bridge'] = '',  -- textures/SNB_Bridge.png (1.0 studs por repeticao)
  ['snb_dais_1'] = '',  -- textures/SNB_Dais_1.png (1.0 studs por repeticao)
  ['snb_dais_2'] = '',  -- textures/SNB_Dais_2.png (1.0 studs por repeticao)
  ['snb_gate'] = '',  -- textures/SNB_Gate.png (1.0 studs por repeticao)
  ['snb_ground_1'] = '',  -- textures/SNB_Ground_1.png (1.0 studs por repeticao)
  ['snb_ground_2'] = '',  -- textures/SNB_Ground_2.png (1.0 studs por repeticao)
  ['snb_ground_3'] = '',  -- textures/SNB_Ground_3.png (1.0 studs por repeticao)
  ['snb_ground_4'] = '',  -- textures/SNB_Ground_4.png (1.0 studs por repeticao)
  ['snb_hall'] = '',  -- textures/SNB_Hall.png (1.0 studs por repeticao)
  ['snb_hammer_1'] = '',  -- textures/SNB_Hammer_1.png (1.0 studs por repeticao)
  ['snb_hammer_2'] = '',  -- textures/SNB_Hammer_2.png (1.0 studs por repeticao)
  ['snb_plaza_1'] = '',  -- textures/SNB_Plaza_1.png (1.0 studs por repeticao)
  ['snb_plaza_2'] = '',  -- textures/SNB_Plaza_2.png (1.0 studs por repeticao)
  ['snb_rank_1'] = '',  -- textures/SNB_Rank_1.png (1.0 studs por repeticao)
  ['snb_rank_2'] = '',  -- textures/SNB_Rank_2.png (1.0 studs por repeticao)
  ['snb_ruins'] = '',  -- textures/SNB_Ruins.png (1.0 studs por repeticao)
  ['snb_shop_1'] = '',  -- textures/SNB_Shop_1.png (1.0 studs por repeticao)
  ['snb_shop_2'] = '',  -- textures/SNB_Shop_2.png (1.0 studs por repeticao)
  ['snb_shopin'] = '',  -- textures/SNB_ShopIn.png (1.0 studs por repeticao)
  ['snb_shore'] = '',  -- textures/SNB_Shore.png (1.0 studs por repeticao)
  ['snb_spawn'] = '',  -- textures/SNB_Spawn.png (1.0 studs por repeticao)
  ['snb_tufts'] = '',  -- textures/SNB_Tufts.png (1.0 studs por repeticao)
  ['snb_veg_ancient'] = '',  -- textures/SNB_Veg_ancient.png (1.0 studs por repeticao)
  ['snb_veg_bush1'] = '',  -- textures/SNB_Veg_bush1.png (1.0 studs por repeticao)
  ['snb_veg_bushf'] = '',  -- textures/SNB_Veg_bushF.png (1.0 studs por repeticao)
  ['snb_veg_oak1'] = '',  -- textures/SNB_Veg_oak1.png (1.0 studs por repeticao)
  ['snb_veg_oak2'] = '',  -- textures/SNB_Veg_oak2.png (1.0 studs por repeticao)
  ['snb_veg_oak3'] = '',  -- textures/SNB_Veg_oak3.png (1.0 studs por repeticao)
  ['snb_veg_oakg'] = '',  -- textures/SNB_Veg_oakG.png (1.0 studs por repeticao)
  ['snb_veg_pine1'] = '',  -- textures/SNB_Veg_pine1.png (1.0 studs por repeticao)
  ['snb_veg_pine2'] = '',  -- textures/SNB_Veg_pine2.png (1.0 studs por repeticao)
  ['stone'] = '',  -- textures/T_stone_v3.png (6.0 studs por repeticao)
  ['wb_bark'] = '',  -- textures/WB_bark_v2.png (4.0 studs por repeticao)
  ['wb_canvas_blue'] = '',  -- textures/WB_canvas_blue_v2.png (4.0 studs por repeticao)
  ['wb_canvas_green'] = '',  -- textures/WB_canvas_green_v2.png (4.0 studs por repeticao)
  ['wb_canvas_red'] = '',  -- textures/WB_canvas_red_v2.png (4.0 studs por repeticao)
  ['wb_cobble'] = '',  -- textures/WB_cobble_v2.png (5.0 studs por repeticao)
  ['wb_crop'] = '',  -- textures/WB_crop_v2.png (16.0 studs por repeticao)
  ['wb_crop_gold'] = '',  -- textures/WB_crop_gold_v2.png (16.0 studs por repeticao)
  ['wb_dirt'] = '',  -- textures/WB_dirt_v2.png (10.0 studs por repeticao)
  ['wb_flag'] = '',  -- textures/WB_flag_v2.png (8.0 studs por repeticao)
  ['wb_grass'] = '',  -- textures/WB_grass_v2.png (14.0 studs por repeticao)
  ['wb_iron'] = '',  -- textures/WB_iron_v2.png (4.0 studs por repeticao)
  ['wb_leaf'] = '',  -- textures/WB_leaf_v2.png (7.0 studs por repeticao)
  ['wb_pine'] = '',  -- textures/WB_pine_v2.png (6.0 studs por repeticao)
  ['wb_plank'] = '',  -- textures/WB_plank_v2.png (5.0 studs por repeticao)
  ['wb_plank_light'] = '',  -- textures/WB_plank_light_v2.png (5.0 studs por repeticao)
  ['wb_plaster'] = '',  -- textures/WB_plaster_v2.png (9.0 studs por repeticao)
  ['wb_plaster_cream'] = '',  -- textures/WB_plaster_cream_v2.png (9.0 studs por repeticao)
  ['wb_plaster_ochre'] = '',  -- textures/WB_plaster_ochre_v2.png (9.0 studs por repeticao)
  ['wb_rock'] = '',  -- textures/WB_rock_v2.png (22.0 studs por repeticao)
  ['wb_roof'] = '',  -- textures/WB_roof_v2.png (6.0 studs por repeticao)
  ['wb_roof_dark'] = '',  -- textures/WB_roof_dark_v2.png (6.0 studs por repeticao)
  ['wb_roof_shingle'] = '',  -- textures/WB_roof_shingle_v2.png (6.0 studs por repeticao)
  ['wb_roof_slate'] = '',  -- textures/WB_roof_slate_v2.png (6.0 studs por repeticao)
  ['wb_snow'] = '',  -- textures/WB_snow_v2.png (30.0 studs por repeticao)
  ['wb_stone'] = '',  -- textures/WB_stone_v2.png (5.6 studs por repeticao)
  ['wb_stone_dark'] = '',  -- textures/WB_stone_dark_v2.png (5.6 studs por repeticao)
  ['wb_timber'] = '',  -- textures/WB_timber_v2.png (5.0 studs por repeticao)
  ['wb_water'] = '',  -- textures/WB_water_v2.png (20.0 studs por repeticao)
  ['wb_window'] = '',  -- textures/WB_window_v2.png (2.4 studs por repeticao)
  ['wood'] = '',  -- textures/T_wood_v3.png (5.0 studs por repeticao)
}
-- material/variante -> c = cor calibrada no Studio, m = Enum.Material (hibrido), t = transparencia,
--   s = CastShadow da familia, x = textura de detalhe, w = espiral
local MAT = {
  ['Bark_Dark'] = {c = Color3.fromRGB(86,60,46), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Emblem_Cream'] = {c = Color3.fromRGB(237,231,215), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Palm'] = {c = Color3.fromRGB(110,166,94), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Pine'] = {c = Color3.fromRGB(45,111,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Amber'] = {c = Color3.fromRGB(246,110,12), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Ball_Amber'] = {c = Color3.fromRGB(255,150,12), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Blue'] = {c = Color3.fromRGB(63,137,225), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Floor'] = {c = Color3.fromRGB(168,180,198), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Gold_Bright'] = {c = Color3.fromRGB(255,196,60), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Rim_Glow'] = {c = Color3.fromRGB(60,172,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_DB_Star_Red'] = {c = Color3.fromRGB(178,16,12), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DB_Swirl'] = {c = Color3.fromRGB(30,120,240), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = 'P_DB_Swirl'},
  ['P_DB_White'] = {c = Color3.fromRGB(243,243,239), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_GlicMid'] = {c = Color3.fromRGB(176,112,230), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_GlicTip'] = {c = Color3.fromRGB(214,160,238), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Glicinia'] = {c = Color3.fromRGB(146,84,220), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Glow'] = {c = Color3.fromRGB(185,12,22), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_DS_Gravel'] = {c = Color3.fromRGB(186,176,150), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['P_DS_Iron'] = {c = Color3.fromRGB(24,23,28), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Lacquer'] = {c = Color3.fromRGB(112,13,19), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Red'] = {c = Color3.fromRGB(206,69,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Swirl'] = {c = Color3.fromRGB(185,12,22), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = 'P_DS_Swirl'},
  ['P_Naruto_Cloth'] = {c = Color3.fromRGB(31,50,105), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['P_Naruto_Lacquer'] = {c = Color3.fromRGB(158,39,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_Naruto_Paper'] = {c = Color3.fromRGB(212,188,144), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_Naruto_Rim_Glow'] = {c = Color3.fromRGB(255,100,12), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_Naruto_Steel'] = {c = Color3.fromRGB(206,212,221), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_Naruto_Stone'] = {c = Color3.fromRGB(190,136,86), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_Naruto_Swirl'] = {c = Color3.fromRGB(255,115,20), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = 'P_Naruto_Swirl'},
  ['P_OPM_ConcreteDark'] = {c = Color3.fromRGB(63,64,68), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['P_OPM_ConcreteLight'] = {c = Color3.fromRGB(167,171,178), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['P_OPM_ConcreteMid'] = {c = Color3.fromRGB(103,105,111), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['P_OPM_Crater'] = {c = Color3.fromRGB(43,44,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_OPM_DarkGlassT'] = {c = Color3.fromRGB(48,63,85), m = Enum.Material.Glass, t = 0.0, s = true, x = nil, w = nil},
  ['P_OPM_Glow'] = {c = Color3.fromRGB(255,228,80), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_OPM_RebarSteel'] = {c = Color3.fromRGB(118,60,34), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_OPM_Red'] = {c = Color3.fromRGB(225,56,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_OPM_Swirl'] = {c = Color3.fromRGB(232,175,0), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = 'P_OPM_Swirl'},
  ['P_OPM_Yellow'] = {c = Color3.fromRGB(249,206,39), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_OP_Glow'] = {c = Color3.fromRGB(25,105,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_OP_Red'] = {c = Color3.fromRGB(206,75,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_OP_Swirl'] = {c = Color3.fromRGB(25,105,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = 'P_OP_Swirl'},
  ['P_SG_Core_Glow'] = {c = Color3.fromRGB(230,218,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_SG_Deadwood'] = {c = Color3.fromRGB(74,68,82), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['P_SG_Lilac_Glow'] = {c = Color3.fromRGB(184,155,250), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_SG_Marble'] = {c = Color3.fromRGB(48,46,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_SG_Moon_Glow'] = {c = Color3.fromRGB(139,92,246), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_SG_Obsidian'] = {c = Color3.fromRGB(26,22,36), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_SG_Rose'] = {c = Color3.fromRGB(98,40,170), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_SG_Silver'] = {c = Color3.fromRGB(181,184,196), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_SG_Violet'] = {c = Color3.fromRGB(22,12,40), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_Shadow_Glow'] = {c = Color3.fromRGB(150,60,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_Shadow_Swirl'] = {c = Color3.fromRGB(150,60,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = 'P_Shadow_Swirl'},
  ['Rope'] = {c = Color3.fromRGB(190,172,140), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['SNB_Anvil_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_1', w = nil},
  ['SNB_Anvil_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_2', w = nil},
  ['SNB_Anvil_3'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_3', w = nil},
  ['SNB_Anvil_4'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_4', w = nil},
  ['SNB_Anvil_5'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_5', w = nil},
  ['SNB_Anvil_6'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_6', w = nil},
  ['SNB_Anvil_7'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_7', w = nil},
  ['SNB_Anvil_8'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_anvil_8', w = nil},
  ['SNB_Avenue'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_avenue', w = nil},
  ['SNB_Bridge'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_bridge', w = nil},
  ['SNB_Dais_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_dais_1', w = nil},
  ['SNB_Dais_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_dais_2', w = nil},
  ['SNB_Gate'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_gate', w = nil},
  ['SNB_Ground_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_1', w = nil},
  ['SNB_Ground_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_2', w = nil},
  ['SNB_Ground_3'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_3', w = nil},
  ['SNB_Ground_4'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_4', w = nil},
  ['SNB_Hall'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hall', w = nil},
  ['SNB_Hammer_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hammer_1', w = nil},
  ['SNB_Hammer_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hammer_2', w = nil},
  ['SNB_Plaza_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_plaza_1', w = nil},
  ['SNB_Plaza_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_plaza_2', w = nil},
  ['SNB_Rank_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_rank_1', w = nil},
  ['SNB_Rank_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_rank_2', w = nil},
  ['SNB_Ruins'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ruins', w = nil},
  ['SNB_ShopIn'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_shopin', w = nil},
  ['SNB_Shop_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_shop_1', w = nil},
  ['SNB_Shop_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_shop_2', w = nil},
  ['SNB_Shore'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_shore', w = nil},
  ['SNB_Spawn'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_spawn', w = nil},
  ['SNB_Tufts'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_tufts', w = nil},
  ['SNB_Veg_ancient'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_ancient', w = nil},
  ['SNB_Veg_bush1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_bush1', w = nil},
  ['SNB_Veg_bushF'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_bushf', w = nil},
  ['SNB_Veg_oak1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_oak1', w = nil},
  ['SNB_Veg_oak2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_oak2', w = nil},
  ['SNB_Veg_oak3'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_oak3', w = nil},
  ['SNB_Veg_oakG'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_oakg', w = nil},
  ['SNB_Veg_pine1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_pine1', w = nil},
  ['SNB_Veg_pine2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_veg_pine2', w = nil},
  ['SN_CrystalAmber'] = {c = Color3.fromRGB(255,176,70), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_CrystalBlue'] = {c = Color3.fromRGB(120,210,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_CrystalRed'] = {c = Color3.fromRGB(255,80,70), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_CrystalViolet'] = {c = Color3.fromRGB(186,120,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_Hills'] = {c = Color3.fromRGB(112,164,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'sn_hills', w = nil},
  ['SN_Lava'] = {c = Color3.fromRGB(255,110,30), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_LavaHot'] = {c = Color3.fromRGB(255,214,110), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_Mountain'] = {c = Color3.fromRGB(140,150,168), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'sn_mountain', w = nil},
  ['SN_PineFar'] = {c = Color3.fromRGB(58,108,66), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['SN_PineFarDark'] = {c = Color3.fromRGB(44,86,58), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['SN_PineFarLight'] = {c = Color3.fromRGB(86,136,78), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['SN_Rune'] = {c = Color3.fromRGB(255,214,128), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_DS_Rock'] = {c = Color3.fromRGB(92,92,100), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Light'] = {c = Color3.fromRGB(156,148,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['WB_Fire'] = {c = Color3.fromRGB(255,150,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_FireCore'] = {c = Color3.fromRGB(255,236,150), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Ingot'] = {c = Color3.fromRGB(255,120,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_LampGlow'] = {c = Color3.fromRGB(255,214,130), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Water'] = {c = Color3.fromRGB(76,144,180), m = Enum.Material.SmoothPlastic, t = 0.15, s = false, x = 'wb_water', w = nil},
  ['Wood_Dark'] = {c = Color3.fromRGB(92,64,47), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Light'] = {c = Color3.fromRGB(148,110,80), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Plank'] = {c = Color3.fromRGB(126,92,66), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
}
local KEEP = {[Enum.Material.Neon]=true, [Enum.Material.Metal]=true, [Enum.Material.Glass]=true, [Enum.Material.CorrodedMetal]=true}
local function norm(n) n = string.gsub(n, '%.%d+$', ''); n = string.gsub(n, ' %(%d+%)$', ''); return n end
local function matOf(name)
  local s = string.match(name, '__(.+)$'); if not s then return nil end
  if MAT[s] then return MAT[s], s end
  s = string.gsub(string.gsub(s, '_%d+$', ''), '_g%d+_%d+$', '')  -- fatias _k e celulas _gX_Y
  if MAT[s] then return MAT[s], s end
  local best, bl = nil, 0   -- tolerante: maior prefixo conhecido (variantes/materiais novos)
  for k, v in pairs(MAT) do if #k > bl and string.sub(s, 1, #k) == k then best, bl = v, #k end end
  return best, s
end
-- FBX: indice -> arquivo
local FBX = {[1]='LOBBY_SN_02_TERRAIN_06bf56.fbx', [2]='LOBBY_SN_03_TOWN_06bf56.fbx', [3]='LOBBY_SN_04_FORGE_06bf56.fbx', [4]='LOBBY_SN_05_SERVICES_06bf56.fbx', [5]='LOBBY_SN_06_PORTALS_06bf56.fbx', [6]='LOBBY_SN_07_EXIT_06bf56.fbx', [7]='LOBBY_SN_09_VEGETATION_06bf56.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['WB_Bg_Forest__SN_PineFar__SN_PineFar']={505.936,65.895,316.882,802.355,128.235,655.164,1,false,'SN_PineFar','k',''},
  ['WB_Bg_Forest__SN_PineFarDark__SN_PineFarDark']={505.962,59.305,316.836,805.927,124.964,657.698,1,false,'SN_PineFarDark','k',''},
  ['WB_Bg_Forest__SN_PineFarLight__SN_PineFarLight']={505.907,71.009,316.934,798.187,129.971,652.207,1,false,'SN_PineFarLight','k',''},
  ['WB_Bg_Relief_0__SN_Hills__SN_Hills']={651.643,54.259,300.718,721.51,116.118,609.997,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_0__SN_Mountain__SN_Mountain']={1021.198,136.993,527.514,958.53,206.037,1065.523,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_1__SN_Hills__SN_Hills']={302.588,52.655,618.202,610.148,112.91,658.39,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_1__SN_Mountain__SN_Mountain']={527.101,146.213,1053.435,1062.813,201.392,895.439,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_2__SN_Hills__SN_Hills']={-309.841,53.061,606.393,627.594,113.722,635.763,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_2__SN_Mountain__SN_Mountain']={-526.862,144.274,1007.146,1062.549,218.847,983.434,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_3__SN_Hills__SN_Hills']={-866.908,53.163,310.856,1153.147,113.927,624.708,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_3__SN_Mountain__SN_Mountain']={-1008.42,142.758,526.762,980.381,217.988,1063.027,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_4__SN_Hills__SN_Hills']={-527.439,38.952,-255.926,478.276,85.504,518.199,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_4__SN_Mountain__SN_Mountain']={-1008.139,208.022,-530.489,985.438,339.272,1072.125,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_5__SN_Hills__SN_Hills']={-256.391,27.837,-510.121,518.058,63.274,440.131,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_5__SN_Mountain__SN_Mountain']={-529.722,262.733,-1006.825,1067.165,445.124,983.598,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_6__SN_Hills__SN_Hills']={258.795,44.211,-510.034,520.033,96.022,440.599,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_6__SN_Mountain__SN_Mountain']={528.256,259.906,-1007.829,1069.732,450.777,986.244,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_7__SN_Hills__SN_Hills']={650.827,51.44,-255.952,720.761,110.481,517.509,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_7__SN_Mountain__SN_Mountain']={1008.366,225.969,-528.024,979.109,385.916,1065.159,1,false,'SN_Mountain','k',''},
  ['WB_Ter_Ground__SNB_Ground_1__SNB_Ground_1']={-40.096,6.902,5.599,48.38,0.104,105.744,1,true,'SNB_Ground_1','',''},
  ['WB_Ter_Ground__SNB_Ground_2__SNB_Ground_2_g15_15']={-65.0,6.814,64.2,130.0,0.54,132.24,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground__SNB_Ground_2__SNB_Ground_2_g15_16']={-75.0,6.873,-23.324,150.0,0.322,208.781,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground__SNB_Ground_2__SNB_Ground_2_g16_15']={22.816,7.013,74.04,214.102,0.776,151.92,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground__SNB_Ground_2__SNB_Ground_2_g16_16']={15.786,6.98,-41.467,268.429,0.481,245.067,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground__SNB_Ground_3__SNB_Ground_3']={-39.936,6.89,-31.723,48.443,0.061,53.767,1,true,'SNB_Ground_3','',''},
  ['WB_Ter_Ground__SNB_Ground_4__SNB_Ground_4']={54.247,6.891,-3.42,60.833,0.061,102.111,1,true,'SNB_Ground_4','',''},
  ['WB_Ter_Shore__SNB_Shore__SNB_Shore_g15_17']={-13.667,3.6,-20.969,287.613,6.4,300.711,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore__SNB_Shore_g16_17']={62.836,3.6,-149.109,125.671,6.4,45.181,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore__SNB_Shore_g17_15']={30.253,3.6,78.303,248.882,6.4,158.959,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore__SNB_Shore_g17_16']={141.599,3.6,-60.867,29.648,6.4,122.803,1,true,'SNB_Shore','',''},
  ['WB_Ter_Water__WB_Water__WB_Water']={0.0,1.7,0.0,840.0,1.0,840.0,1,false,'WB_Water','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g14_15']={-137.476,8.464,25.398,14.745,4.493,98.878,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g14_16']={-135.855,10.95,-20.199,18.899,9.1,80.481,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g15_15']={-92.105,14.017,98.931,69.835,15.366,59.681,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g15_16']={-81.922,15.038,-86.022,93.99,17.624,137.176,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g16_14']={45.0,9.764,133.0,30.569,6.729,11.708,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g16_15']={31.929,9.237,58.024,204.783,13.08,141.66,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g16_16']={81.082,15.034,-69.379,95.019,17.632,134.755,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins__SNB_Ruins_g16_17']={102.428,14.045,-127.0,29.83,15.31,19.514,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SN_CrystalAmber__SN_CrystalAmber']={-6.352,9.203,6.758,260.858,6.254,210.458,2,false,'SN_CrystalAmber','',''},
  ['WB_Prop_Ruins__SN_CrystalBlue__SN_CrystalBlue']={-6.135,9.236,-72.603,273.476,6.133,159.219,2,false,'SN_CrystalBlue','',''},
  ['WB_Prop_Ruins__SN_Rune__SN_Rune']={107.137,8.055,16.23,2.791,3.889,6.885,2,false,'SN_Rune','',''},
  ['WB_Town_Plaza__SNB_Plaza_1__SNB_Plaza_1']={0.0,6.843,0.0,80.0,0.955,80.0,2,true,'SNB_Plaza_1','',''},
  ['WB_Town_Plaza__SNB_Plaza_2__SNB_Plaza_2']={0.0,6.735,0.0,82.8,1.07,82.8,2,true,'SNB_Plaza_2','',''},
  ['WB_Town_Plaza__SN_Rune__SN_Rune']={-1.367,7.08,0.0,73.275,0.18,77.6,2,false,'SN_Rune','',''},
  ['WB_Frg_Anvil__SNB_Anvil_1__SNB_Anvil_1']={-42.809,38.604,-111.784,79.613,63.933,58.496,3,true,'SNB_Anvil_1','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_2__SNB_Anvil_2']={0.0,45.123,-118.0,69.399,49.245,39.8,3,true,'SNB_Anvil_2','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_3__SNB_Anvil_3']={0.0,24.361,-112.05,148.0,34.723,59.9,3,true,'SNB_Anvil_3','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_4__SNB_Anvil_4']={0.0,9.025,-117.0,148.6,0.35,50.6,3,true,'SNB_Anvil_4','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_5__SNB_Anvil_5']={0.0,11.025,-117.0,142.6,0.35,44.6,3,true,'SNB_Anvil_5','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_6__SNB_Anvil_6']={0.0,14.1,-110.0,142.0,14.2,58.0,3,true,'SNB_Anvil_6','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_7__SNB_Anvil_7']={3.0,45.962,-117.752,98.0,48.475,38.496,3,true,'SNB_Anvil_7','','SN_Forja'},
  ['WB_Frg_Anvil__SNB_Anvil_8__SNB_Anvil_8']={37.771,38.754,-113.225,84.571,64.079,55.547,3,true,'SNB_Anvil_8','','SN_Forja'},
  ['WB_Frg_Anvil__SN_CrystalAmber__SN_CrystalAmber']={-63.326,14.979,-93.142,4.282,4.586,2.902,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Anvil__SN_CrystalBlue__SN_CrystalBlue']={57.837,15.399,-116.748,20.358,5.42,52.025,3,false,'SN_CrystalBlue','','SN_Forja'},
  ['WB_Frg_Anvil__SN_Lava__SN_Lava']={-2.743,33.9,-113.247,29.67,53.2,43.845,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Anvil__SN_LavaHot__SN_LavaHot']={19.503,38.6,-113.291,53.794,62.6,44.097,3,false,'SN_LavaHot','','SN_Forja'},
  ['WB_Frg_Anvil__SN_Rune__SN_Rune']={0.025,39.891,-118.0,70.17,27.318,34.6,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Frg_Anvil__WB_Fire__WB_Fire']={0.0,17.45,-95.0,141.653,2.1,1.509,3,false,'WB_Fire','','SN_Forja'},
  ['WB_Frg_Anvil__WB_FireCore__WB_FireCore']={0.0,17.1,-95.0,140.9,1.3,0.779,3,false,'WB_FireCore','','SN_Forja'},
  ['WB_Frg_Hall__SNB_Hall__SNB_Hall']={0.0,27.705,-65.979,39.0,42.611,53.159,3,true,'SNB_Hall','','SN_Forja'},
  ['WB_Frg_Hall__SN_CrystalAmber__SN_CrystalAmber']={-2.4,10.793,-43.175,25.265,0.306,0.306,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Hall__SN_CrystalBlue__SN_CrystalBlue']={0.8,10.793,-43.175,25.265,0.306,0.306,3,false,'SN_CrystalBlue','','SN_Forja'},
  ['WB_Frg_Hall__SN_Lava__SN_Lava']={1.958,7.375,-81.572,10.517,1.75,21.644,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Hall__SN_LavaHot__SN_LavaHot']={2.163,7.655,-82.067,8.726,1.59,20.424,3,false,'SN_LavaHot','','SN_Forja'},
  ['WB_Frg_Hall__WB_Fire__WB_Fire']={0.0,10.3,-57.464,36.653,4.0,34.437,3,false,'WB_Fire','','SN_Forja'},
  ['WB_Frg_Hall__WB_FireCore__WB_FireCore']={0.0,9.95,-57.353,35.9,3.2,33.485,3,false,'WB_FireCore','','SN_Forja'},
  ['WB_Frg_Hall__WB_Ingot__WB_Ingot']={13.65,8.885,-60.4,1.9,3.73,7.6,3,false,'WB_Ingot','','SN_Forja'},
  ['WB_Frg_Hall__WB_Water__WB_Water']={-12.6,9.175,-58.4,2.36,0.15,2.36,3,false,'WB_Water','','SN_Forja'},
  ['WB_Frg_Hammer__SNB_Hammer_1__SNB_Hammer_1']={107.517,11.733,-65.69,49.905,28.121,49.395,3,true,'SNB_Hammer_1','','SN_Forja'},
  ['WB_Frg_Hammer__SNB_Hammer_2__SNB_Hammer_2']={94.72,57.103,-80.93,37.128,97.011,65.852,3,true,'SNB_Hammer_2','','SN_Forja'},
  ['WB_Frg_Hammer__SN_CrystalAmber__SN_CrystalAmber']={79.225,104.867,-111.221,3.557,3.74,3.74,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Hammer__SN_Lava__SN_Lava']={104.597,7.06,-63.974,74.151,0.16,78.577,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Hammer__SN_Rune__SN_Rune']={100.303,11.216,-74.461,13.031,4.268,8.889,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Rank_Tablets__SNB_Rank_1__SNB_Rank_1']={64.152,27.115,60.596,62.182,41.33,54.238,4,true,'SNB_Rank_1','','SN_Tabuas'},
  ['WB_Rank_Tablets__SNB_Rank_2__SNB_Rank_2']={63.639,28.0,53.365,65.047,43.6,70.061,4,true,'SNB_Rank_2','','SN_Tabuas'},
  ['WB_Rank_Tablets__SN_CrystalBlue__SN_CrystalBlue']={57.83,9.243,49.348,44.103,3.877,53.989,4,false,'SN_CrystalBlue','','SN_Tabuas'},
  ['WB_Rank_Tablets__SN_Rune__SN_Rune']={68.79,20.05,55.331,41.199,16.989,42.284,4,false,'SN_Rune','','SN_Tabuas'},
  ['WB_Rank_Tablets__WB_Fire__WB_Fire']={65.727,12.65,55.151,41.826,2.1,49.399,4,false,'WB_Fire','','SN_Tabuas'},
  ['WB_Rank_Tablets__WB_FireCore__WB_FireCore']={65.727,12.3,55.151,41.036,1.3,48.621,4,false,'WB_FireCore','','SN_Tabuas'},
  ['WB_Shop_Inside__SNB_ShopIn__SNB_ShopIn']={75.164,14.975,-35.054,22.563,13.55,28.101,4,true,'SNB_ShopIn','','SN_Loja'},
  ['WB_Shop_Inside__SN_CrystalBlue__SN_CrystalBlue']={72.913,12.605,-45.115,1.587,1.974,1.57,4,false,'SN_CrystalBlue','','SN_Loja'},
  ['WB_Shop_Inside__WB_LampGlow__WB_LampGlow']={72.958,15.625,-34.02,5.023,7.35,9.86,4,false,'WB_LampGlow','','SN_Loja'},
  ['WB_Shop_Temple__SNB_Shop_1__SNB_Shop_1']={71.961,19.411,-32.884,38.074,26.181,41.738,4,true,'SNB_Shop_1','','SN_Loja'},
  ['WB_Shop_Temple__SNB_Shop_2__SNB_Shop_2']={71.5,19.751,-35.286,36.7,25.502,40.692,4,true,'SNB_Shop_2','','SN_Loja'},
  ['WB_Shop_Temple__WB_Fire__WB_Fire']={58.548,11.45,-27.301,9.127,2.1,17.737,4,false,'WB_Fire','','SN_Loja'},
  ['WB_Shop_Temple__WB_FireCore__WB_FireCore']={58.548,11.1,-27.301,8.503,1.3,17.129,4,false,'WB_FireCore','','SN_Loja'},
  ['PORTAL_DemonSlayer_Swirl__P_DS_Swirl']={-78.336,19.4,-17.315,3.712,15.0,14.644,5,false,'P_DS_Swirl','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Emblem_Cream']={-78.833,21.044,-17.731,13.374,25.028,22.823,5,false,'Emblem_Cream','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Glow']={-77.225,19.4,-17.12,3.843,15.5,15.24,5,false,'P_DS_Glow','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Gravel']={-76.127,9.316,-16.877,26.469,2.833,30.413,5,false,'P_DS_Gravel','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Iron']={-76.295,21.533,-18.019,17.154,25.865,23.754,5,true,'P_DS_Iron','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Lacquer']={-79.916,21.49,-18.019,9.913,25.78,23.587,5,true,'P_DS_Lacquer','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Red']={-75.661,19.368,-18.054,15.472,19.463,21.79,5,true,'P_DS_Red','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Stone_DS_Rock']={-76.42,10.175,-16.942,27.395,4.65,31.84,5,true,'Stone_DS_Rock','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__Bark_Dark']={-77.03,16.814,-4.589,3.535,18.217,3.228,5,false,'Bark_Dark','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicMid']={-78.345,24.64,-5.225,11.739,6.72,5.292,5,true,'P_DS_GlicMid','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicTip']={-77.641,21.688,-4.435,9.944,4.771,3.375,5,false,'P_DS_GlicTip','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_Glicinia']={-77.785,25.157,-5.265,10.791,5.986,5.902,5,true,'P_DS_Glicinia','','PORTAL_DemonSlayer'},
  ['PORTAL_DragonBall_Frame__P_DB_Amber']={-61.247,19.042,48.146,22.943,20.277,18.142,5,true,'P_DB_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Ball_Amber']={-63.773,22.915,41.852,7.656,24.77,18.048,5,true,'P_DB_Ball_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Blue']={-61.866,11.402,45.321,23.301,8.905,25.204,5,true,'P_DB_Blue','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Floor']={-62.62,8.94,46.337,27.946,0.32,29.075,5,true,'P_DB_Floor','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Gold_Bright']={-64.309,19.41,44.973,14.32,22.221,23.643,5,true,'P_DB_Gold_Bright','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Rim_Glow']={-63.907,19.4,47.288,9.83,15.566,12.862,5,false,'P_DB_Rim_Glow','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Star_Red']={-64.49,21.826,42.82,9.791,23.722,20.035,5,true,'P_DB_Star_Red','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_White']={-62.62,20.817,46.337,27.745,27.734,28.874,5,true,'P_DB_White','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Swirl__P_DB_Swirl']={-64.309,19.4,47.586,8.922,15.0,12.058,5,false,'P_DB_Swirl','','PORTAL_DragonBall'},
  ['PORTAL_Naruto_Bandana__Leaf_Pine']={-39.517,8.814,72.924,27.313,2.572,17.457,5,false,'Leaf_Pine','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Metal_Dark']={-37.457,23.057,70.626,26.864,26.687,14.281,5,true,'Metal_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Cloth']={-37.667,23.517,69.848,26.227,21.005,15.621,5,true,'P_Naruto_Cloth','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Lacquer']={-39.148,22.08,68.858,23.039,26.84,17.346,5,true,'P_Naruto_Lacquer','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Paper']={-45.241,10.2,61.368,6.56,3.2,6.678,5,false,'P_Naruto_Paper','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Rim_Glow']={-38.324,19.4,69.139,13.798,15.5,7.951,5,false,'P_Naruto_Rim_Glow','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Steel']={-33.263,20.654,68.544,17.48,26.793,4.743,5,true,'P_Naruto_Steel','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Stone']={-39.148,19.475,70.626,17.902,22.15,11.949,5,true,'P_Naruto_Stone','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Dark']={-38.009,17.45,68.57,34.649,19.5,32.778,5,true,'Stone_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Light']={-38.009,8.641,68.57,34.432,0.761,32.561,5,true,'Stone_Light','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Swirl__P_Naruto_Swirl']={-38.785,19.4,69.97,13.119,15.0,7.272,5,false,'P_Naruto_Swirl','','PORTAL_Naruto'},
  ['PORTAL_OnePiece_Pier__Emblem_Cream']={-63.132,25.174,-52.718,5.265,22.253,15.873,5,false,'Emblem_Cream','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Leaf_Palm']={-75.512,19.24,-45.653,8.188,1.955,8.153,5,false,'Leaf_Palm','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Metal_Dark']={-62.527,21.444,-47.117,28.469,26.208,30.496,5,true,'Metal_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Glow']={-63.252,19.4,-47.663,9.727,15.5,12.679,5,false,'P_OP_Glow','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Red']={-61.426,15.2,-59.558,2.021,2.7,2.453,5,false,'P_OP_Red','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Rope']={-62.533,19.578,-47.122,32.383,22.056,33.035,5,false,'Rope','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Dark']={-62.533,19.2,-47.124,32.298,24.0,32.891,5,true,'Wood_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Light']={-63.891,20.779,-48.145,16.284,23.444,21.197,5,true,'Wood_Light','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Plank']={-62.341,13.844,-46.988,30.825,11.912,31.096,5,true,'Wood_Plank','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Swirl__P_OP_Swirl']={-63.891,19.4,-48.145,9.027,15.0,11.98,5,false,'P_OP_Swirl','','PORTAL_OnePiece'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_ConcreteDark']={-38.584,19.669,-71.008,18.343,19.281,11.966,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Glow']={-38.554,31.02,-71.008,18.591,0.46,12.325,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Yellow']={-38.526,9.35,-70.982,20.506,0.8,13.528,5,false,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Swirl__P_OPM_Swirl']={-38.173,19.4,-70.305,13.182,15.0,7.157,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_SwirlBack__P_OPM_Swirl']={-39.27,19.4,-72.327,13.182,15.0,7.157,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteDark']={-37.409,21.225,-68.899,34.808,26.85,32.719,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteLight']={-37.409,19.975,-68.899,34.104,24.15,31.373,5,true,'P_OPM_ConcreteLight','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteMid']={-36.008,19.975,-71.531,18.34,22.95,18.418,5,true,'P_OPM_ConcreteMid','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Crater']={-38.732,19.539,-71.08,17.613,18.618,11.458,5,true,'P_OPM_Crater','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_DarkGlassT']={-38.554,30.8,-71.008,18.496,1.3,12.149,5,false,'P_OPM_DarkGlassT','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Glow']={-38.726,19.4,-71.142,15.437,16.24,10.259,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_RebarSteel']={-36.975,18.7,-72.273,16.772,18.916,16.76,5,true,'P_OPM_RebarSteel','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Red']={-37.334,31.676,-68.633,3.253,3.872,2.634,5,false,'P_OPM_Red','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Yellow']={-37.409,21.125,-68.899,34.848,26.45,32.76,5,true,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Core_Glow']={-74.511,23.695,15.963,9.402,21.506,25.637,5,false,'P_SG_Core_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Lilac_Glow']={-77.041,23.275,16.344,4.338,26.631,17.95,5,false,'P_SG_Lilac_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Moon_Glow']={-74.537,23.278,18.034,9.361,26.737,21.411,5,false,'P_SG_Moon_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Deadwood']={-77.485,12.508,3.786,2.19,8.559,2.467,5,false,'P_SG_Deadwood','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Marble']={-75.24,8.8,16.009,21.303,1.9,28.851,5,true,'P_SG_Marble','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Obsidian']={-78.447,23.38,16.695,9.481,29.46,25.964,5,true,'P_SG_Obsidian','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Rose']={-76.664,15.108,3.968,2.428,5.16,2.96,5,false,'P_SG_Rose','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Silver']={-75.24,23.85,16.009,21.492,30.58,29.041,5,true,'P_SG_Silver','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Violet']={-76.308,18.03,16.695,12.801,17.86,24.635,5,true,'P_SG_Violet','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_Shadow_Glow']={-77.665,19.4,16.509,3.711,15.5,15.264,5,false,'P_Shadow_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Swirl__P_Shadow_Swirl']={-78.507,19.4,16.633,3.629,15.0,14.672,5,false,'P_Shadow_Swirl','','PORTAL_ShadowGarden'},
  ['WB_Court_Dais__SNB_Dais_1__SNB_Dais_1']={-58.787,17.105,41.901,70.763,21.81,94.764,5,true,'SNB_Dais_1','',''},
  ['WB_Court_Dais__SNB_Dais_2__SNB_Dais_2']={-58.587,17.105,-44.979,71.754,21.81,86.998,5,true,'SNB_Dais_2','',''},
  ['WB_Court_Dais__SN_CrystalAmber__SN_CrystalAmber']={-57.95,10.398,-0.762,45.024,5.269,171.774,5,false,'SN_CrystalAmber','',''},
  ['WB_Court_Dais__SN_CrystalBlue__SN_CrystalBlue']={-74.148,10.035,-55.299,11.686,4.169,16.13,5,false,'SN_CrystalBlue','',''},
  ['WB_Court_Dais__SN_CrystalRed__SN_CrystalRed']={-90.311,10.263,-19.683,5.619,4.744,17.682,5,false,'SN_CrystalRed','',''},
  ['WB_Court_Dais__SN_CrystalViolet__SN_CrystalViolet']={-90.669,10.465,19.486,7.875,5.236,17.052,5,false,'SN_CrystalViolet','',''},
  ['WB_Court_Dais__SN_Rune__SN_Rune_g15_15']={-58.454,7.91,43.365,67.327,0.333,81.197,5,false,'SN_Rune','',''},
  ['WB_Court_Dais__SN_Rune__SN_Rune_g15_16']={-58.063,7.91,-43.886,67.779,0.333,80.838,5,false,'SN_Rune','',''},
  ['WB_Court_Dais__WB_Fire__WB_Fire']={-48.574,12.61,-0.08,44.295,2.1,131.185,5,false,'WB_Fire','',''},
  ['WB_Court_Dais__WB_FireCore__WB_FireCore']={-48.547,12.26,-0.12,43.654,1.3,130.497,5,false,'WB_FireCore','',''},
  ['WB_Exit_Avenue__SNB_Avenue__SNB_Avenue_0']={-0.093,15.675,117.25,41.522,18.95,57.5,6,true,'SNB_Avenue','',''},
  ['WB_Exit_Avenue__SNB_Avenue__SNB_Avenue_1']={2.445,15.675,117.25,36.455,18.95,57.5,6,true,'SNB_Avenue','',''},
  ['WB_Exit_Avenue__SN_Rune__SN_Rune']={0.0,7.04,118.75,2.798,0.1,49.498,6,false,'SN_Rune','',''},
  ['WB_Exit_Avenue__WB_Fire__WB_Fire']={0.0,11.25,119.5,26.053,2.1,19.509,6,false,'WB_Fire','',''},
  ['WB_Exit_Avenue__WB_FireCore__WB_FireCore']={0.0,10.9,119.5,25.3,1.3,18.779,6,false,'WB_FireCore','',''},
  ['WB_Exit_Bridge__SNB_Bridge__SNB_Bridge']={0.0,4.635,185.3,18.4,10.63,78.6,6,true,'SNB_Bridge','',''},
  ['WB_Exit_Bridge__WB_Fire__WB_Fire']={0.0,10.467,187.0,14.453,2.767,48.175,6,false,'WB_Fire','',''},
  ['WB_Exit_Bridge__WB_FireCore__WB_FireCore']={0.0,10.117,187.0,13.7,1.967,47.446,6,false,'WB_FireCore','',''},
  ['WB_Exit_Gate__SNB_Gate__SNB_Gate']={0.0,20.85,148.563,31.4,29.3,16.726,6,true,'SNB_Gate','','SN_Portao'},
  ['WB_Exit_Gate__WB_Fire__WB_Fire']={0.0,11.65,141.8,26.653,2.1,1.509,6,false,'WB_Fire','','SN_Portao'},
  ['WB_Exit_Gate__WB_FireCore__WB_FireCore']={0.0,11.3,141.8,25.9,1.3,0.779,6,false,'WB_FireCore','','SN_Portao'},
  ['WB_Exit_Spawn__SNB_Spawn__SNB_Spawn']={0.0,13.03,66.0,46.078,13.66,45.04,6,true,'SNB_Spawn','',''},
  ['WB_Exit_Spawn__SN_Rune__SN_Rune']={-0.019,14.658,60.891,38.886,9.215,15.096,6,false,'SN_Rune','',''},
  ['WB_Exit_Spawn__WB_Fire__WB_Fire']={0.0,14.75,66.0,31.453,2.1,29.509,6,false,'WB_Fire','',''},
  ['WB_Exit_Spawn__WB_FireCore__WB_FireCore']={0.0,14.4,66.0,30.7,1.3,28.779,6,false,'WB_FireCore','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g14_16']={-137.164,7.687,-50.63,18.578,2.001,91.919,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g15_14']={-38.649,7.72,138.237,45.661,2.169,15.423,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g15_15']={-71.078,7.828,63.626,111.372,2.573,127.405,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g15_16']={-23.06,7.883,-50.591,241.524,2.312,219.111,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g15_17']={-63.193,7.887,-145.213,101.477,2.282,34.565,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g16_14']={40.716,7.906,136.316,45.665,2.313,16.829,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g16_15']={80.416,7.975,16.158,129.78,2.704,224.166,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g16_16']={73.836,8.008,-64.224,107.917,2.527,127.648,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts__SNB_Tufts_g17_15']={136.314,7.982,39.326,16.803,2.461,73.092,7,true,'SNB_Tufts','',''},
  ['WB_Veg_ancient__SNB_Veg_ancient__SNB_Veg_ancient']={-96.197,31.253,-113.286,43.481,51.292,41.429,7,true,'SNB_Veg_ancient','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1__SNB_Veg_bush1_g15_15']={-67.697,8.642,31.356,133.149,3.302,164.35,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1__SNB_Veg_bush1_g15_16']={-101.878,8.581,-80.793,50.348,3.123,58.33,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1__SNB_Veg_bush1_g16_15']={81.807,8.658,31.995,108.641,3.284,95.761,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1__SNB_Veg_bush1_g16_16']={52.787,8.664,-74.748,146.206,3.265,148.502,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g14_15']={-134.271,8.694,36.47,13.299,3.204,57.443,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g14_16']={-134.43,8.715,-15.21,5.644,3.232,27.086,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g15_15']={-68.126,8.888,63.918,120.709,3.595,129.01,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g15_16']={-70.367,8.854,-42.911,109.404,3.505,87.214,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g15_17']={-5.574,8.745,-146.966,12.429,3.197,7.273,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g16_14']={28.232,8.913,136.622,40.425,3.583,7.598,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g16_15']={31.731,8.966,66.385,204.388,3.775,125.621,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g16_16']={70.974,8.965,-53.199,99.304,3.751,90.315,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF__SNB_Veg_bushF_g16_17']={44.348,8.925,-143.165,89.869,3.656,14.919,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g14_16']={-136.183,19.854,-47.267,21.76,27.493,89.249,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g15_14']={-51.171,17.854,132.202,17.755,23.397,11.216,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g15_15']={-76.992,19.927,64.344,91.328,27.784,131.181,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g15_16']={-102.546,19.945,-42.961,54.621,27.821,88.257,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g15_17']={-51.42,17.757,-155.354,18.273,23.19,17.206,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g16_14']={72.789,17.236,133.519,17.223,22.089,13.932,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g16_15']={69.933,19.697,63.996,120.148,27.297,131.816,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g16_16']={54.881,19.484,-43.259,51.053,26.504,89.473,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g16_17']={56.88,17.356,-147.493,67.192,22.343,32.495,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g17_15']={133.191,17.696,45.507,15.704,23.063,51.451,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1__SNB_Veg_oak1_g17_16']={137.971,17.482,-11.411,17.483,22.608,18.094,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2__SNB_Veg_oak2_g15_15']={-61.714,17.17,66.813,100.905,22.228,110.17,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2__SNB_Veg_oak2_g15_16']={-101.525,16.497,-48.223,43.35,20.787,49.606,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2__SNB_Veg_oak2_g16_15']={73.5,16.489,66.023,81.206,20.768,110.31,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3__SNB_Veg_oak3_g15_15']={-83.909,20.722,75.367,21.164,29.286,22.956,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3__SNB_Veg_oak3_g16_15']={86.817,20.9,56.01,68.651,29.661,117.54,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3__SNB_Veg_oak3_g16_16']={98.146,19.503,-4.669,47.938,26.722,13.935,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG__SNB_Veg_oakG_g15_15']={-64.798,17.748,69.115,109.979,23.259,80.215,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG__SNB_Veg_oakG_g16_15']={50.297,18.31,92.782,75.869,24.453,70.378,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG__SNB_Veg_oakG_g16_16']={86.087,18.465,-38.799,75.477,24.782,67.946,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g14_15']={-133.191,22.617,30.264,18.247,32.9,63.94,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g14_16']={-136.39,22.366,-49.77,22.846,32.377,99.345,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g15_15']={-78.77,24.061,63.729,103.822,35.902,130.871,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g15_17']={-47.966,22.201,-148.514,86.286,32.034,33.427,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g16_15']={44.729,23.832,91.875,172.663,35.428,115.733,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g16_16']={8.884,23.454,-42.859,282.243,34.641,176.471,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g16_17']={63.136,22.69,-142.794,58.635,33.051,36.719,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1__SNB_Veg_pine1_g17_16']={137.745,23.474,-52.432,25.075,34.682,107.231,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2__SNB_Veg_pine2_g15_15']={-48.939,19.796,30.449,178.75,27.299,228.245,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2__SNB_Veg_pine2_g15_16']={-58.145,20.844,-77.85,147.026,29.5,156.287,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2__SNB_Veg_pine2_g16_16']={75.659,18.483,-58.714,107.135,24.54,94.957,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2__SNB_Veg_pine2_g17_15']={140.269,19.615,26.982,15.091,26.918,40.596,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2__SNB_Veg_pine2_g17_16']={133.619,20.256,-25.4,15.912,28.264,28.328,7,true,'SNB_Veg_pine2','',''},
}

-- CONFERENCIA DA IMPORTACAO: nomes normalizados, achadas/esperadas por FBX, faltando, eixo > 2048, duplicadas
local ACH, DUP = {}, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local n = norm(d.Name)
    if MESH[n] then
      if ACH[n] and ACH[n] ~= d then DUP += 1
      else ACH[n] = d; if d.Name ~= n then d.Name = n end end
    end
  end
end
local POR, TOT, FALTA = {}, {}, {}
for n, e in pairs(MESH) do
  TOT[e[7]] = (TOT[e[7]] or 0) + 1
  if ACH[n] then POR[e[7]] = (POR[e[7]] or 0) + 1 else table.insert(FALTA, n) end
end
table.sort(FALTA)
local FBX_OK = true
for i, f in pairs(FBX) do
  local a, t = POR[i] or 0, TOT[i] or 0
  if t > 0 then
    local ok = a >= 0.9 * t
    if not ok then FBX_OK = false end
    print(string.format('IMPORT %-34s %4d / %4d %s', f, a, t, ok and 'ok' or '<-- FALTANDO (reimporte este FBX)'))
  end
end
if #FALTA > 0 then
  print(string.format('IMPORT: %d malhas faltando; as 20 primeiras:', #FALTA))
  for i = 1, math.min(20, #FALTA) do print('   ' .. FALTA[i]) end
end
if DUP > 0 then warn(string.format('IMPORT: %d MeshParts duplicadas (FBX importado 2 vezes?) - apague as sobras', DUP)) end
local GRANDE = 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') and math.max(d.Size.X, d.Size.Y, d.Size.Z) > 2048 then GRANDE += 1; warn('IMPORT: eixo > 2048: ' .. d:GetFullName()) end
end
print(string.format('IMPORT: %d MeshParts com eixo > 2048', GRANDE))


-- ALINHAMENTO: compara as MeshParts importadas com MESH (Procrustes discreto no plano XZ) e corrige
local function alinhar()
  if not FBX_OK then warn('ALINHAR: abortado - algum FBX tem menos de 90% das malhas (veja IMPORT acima)'); return end
  local parts = {}
  for n, d in pairs(ACH) do table.insert(parts, d) end
  if #parts < 3 then warn('ALINHAR: poucas MeshParts com nome conhecido - confira se o importador manteve os nomes'); return end
  -- centroides POR FBX (grupo): tolera o importador recentralizar cada arquivo separadamente
  local G = {}
  for _, p in ipairs(parts) do local e = MESH[p.Name]
    local g = G[e[7]]; if not g then g = {ca = Vector3.zero, ce = Vector3.zero, n = 0}; G[e[7]] = g end
    g.ca += p.Position; g.ce += Vector3.new(e[1], e[2], e[3]); g.n += 1 end
  for _, g in pairs(G) do g.ca /= g.n; g.ce /= g.n end
  local function rel(p) local e = MESH[p.Name]; local g = G[e[7]]
    return p.Position - g.ca, Vector3.new(e[1], e[2], e[3]) - g.ce end
  local sa, se = 0, 0
  for _, p in ipairs(parts) do local a, b = rel(p); sa += a.Magnitude; se += b.Magnitude end
  local escala = (se > 0) and (sa / se) or 1
  local best, bestErr, bestMirror = 0, math.huge, false
  for _, mir in ipairs({false, true}) do
    for k = 0, 3 do
      local R = CFrame.Angles(0, k * math.pi / 2, 0); local err = 0
      for _, p in ipairs(parts) do
        local a, b = rel(p)
        if mir then b = Vector3.new(-b.X, b.Y, b.Z) end
        err += (a - R:VectorToWorldSpace(b) * escala).Magnitude
      end
      if err < bestErr then best, bestErr, bestMirror = k, err, mir end
    end
  end
  if bestMirror then warn('ALINHAR: o importador ESPELHOU o lobby. Nao da para corrigir aqui: troque a matriz T no export_roblox.py / eixos do FBX.') end
  if best ~= 0 then warn(string.format('ALINHAR: importador girou %d graus em Y - corrigindo', best * 90)) end
  if math.abs(escala - 1) > 0.05 then warn(string.format('ALINHAR: escala do importador %.3f (m->stud?) - corrigindo Size', escala)) end
  local Rinv = CFrame.Angles(0, -best * math.pi / 2, 0)
  for _, p in ipairs(parts) do local e = MESH[p.Name]
    if math.abs(escala - 1) > 0.05 then p.Size = p.Size / escala end
    local rot = p.CFrame - p.CFrame.Position
    p.CFrame = CFrame.new(Vector3.new(e[1], e[2], e[3]) + ROOT_OFFSET) * Rinv * rot
  end
  print(string.format('ALINHAR: ok (giro %d, escala %.3f, espelho %s)', best * 90, escala, tostring(bestMirror)))
end
if ALINHAR then alinhar() end


-- texturas: le os ids que o 3D Importer subiu (TextureID ou SurfaceAppearance) por familia
local function lerMapa(d)
  local ok, v = pcall(function() return d.TextureID end)
  if ok and v and v ~= '' then return v end
  local sa = d:FindFirstChildOfClass('SurfaceAppearance')
  if sa then
    local ok2, v2 = pcall(function() return sa.ColorMap end)
    if ok2 and v2 and v2 ~= '' then return v2 end
    local ok3, v3 = pcall(function() return sa.ColorMapContent.Uri end)
    if ok3 and v3 and v3 ~= '' then return v3 end
  end
  return nil
end
local function porMapa(sa, id)
  local ok = pcall(function() sa.ColorMap = id end)
  if not ok then ok = pcall(function() sa.ColorMapContent = Content.fromUri(id) end) end
  return ok
end
local function entrada(d)
  local e = MESH[d.Name]
  if e and MAT[e[9]] then return MAT[e[9]], e end
  return matOf(d.Name), e
end
local achados = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local m = entrada(d)
    local key = m and (m.w or m.x)
    if key and (TEX[key] == nil or TEX[key] == '') then
      local id = lerMapa(d)
      if id then TEX[key] = id; achados[key] = id end
    end
  end
end
local nAch = 0
for k, v in pairs(achados) do nAch += 1; print('TEX encontrada', k, v) end
print(string.format('IMPORT: %d texturas encontradas nas MeshParts', nAch))
-- modelos de streaming: SKYLINE (persistente) e um Model Atomic por construcao/portal/forja
local MODELOS = {}
local function modelo(nome, modo)
  local m = MODELOS[nome]
  if m then return m end
  m = root:FindFirstChild(nome)
  if not (m and m:IsA('Model')) then m = Instance.new('Model'); m.Name = nome; m.Parent = root end
  pcall(function() m.ModelStreamingMode = modo end)
  MODELOS[nome] = m
  return m
end
-- aplica cor/material/sombra/textura por variante
local nOk, nSem, nTex, nSombra, nCasca = 0, 0, 0, 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local m, e = entrada(d)
    d.Anchored = true; d.CanCollide = false; d.CanTouch = false; d.CanQuery = false
    pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Box end)
    pcall(function() d.RenderFidelity = Enum.RenderFidelity.Automatic end)
    if m then
      nOk += 1
      d.Color = m.c; d.Transparency = m.t
      d.Material = (LISO and not KEEP[m.m]) and Enum.Material.SmoothPlastic or m.m
      if e then d.CastShadow = e[8] else d.CastShadow = m.s and (d.Size.Magnitude > 4) end
      if d.CastShadow then nSombra += 1 end
      local sa = d:FindFirstChildOfClass('SurfaceAppearance')
      local sw = m.w and TEX[m.w] or ''
      local tx = m.x and TEX[m.x] or ''
      if m.w and sw ~= '' then
        -- espiral do portal: textura sempre (sem ela o disco vira um circulo chapado)
        if sa then sa:Destroy() end
        d.TextureID = sw; d.Material = Enum.Material.SmoothPlastic; nTex += 1
      elseif RICO and tx ~= '' then
        d.TextureID = ''
        if not sa then sa = Instance.new('SurfaceAppearance') end
        sa.AlphaMode = Enum.AlphaMode.Overlay
        if porMapa(sa, tx) then sa.Parent = d; nTex += 1
        else sa:Destroy(); d.TextureID = tx; nTex += 1 end
      else
        d.TextureID = ''
        if sa then sa:Destroy() end
      end
    else
      nSem += 1
    end
    if e then
      local fl = e[10] or ''
      if CAMERA_CASCAS and string.find(fl, 'o', 1, true) then
        -- casca que oclui a camera: o Popper so considera pecas CanCollide/CanQuery e opacas; o grupo SoVisual
        -- colide com Default (raio da camera) e NAO com Personagens (quem anda sao as COL invisiveis)
        d.CanCollide = true; d.CanQuery = true; d.CollisionGroup = 'SoVisual'
        pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end)
        nCasca += 1
      else
        d.CollisionGroup = 'Default'
      end
      if string.find(fl, 'k', 1, true) then
        pcall(function() d.RenderFidelity = Enum.RenderFidelity.Performance end)
        d.Parent = modelo('SKYLINE', Enum.ModelStreamingMode.Persistent)
      elseif e[11] and e[11] ~= '' then
        d.Parent = modelo(e[11], Enum.ModelStreamingMode.Atomic)
      end
    end
  end
end
print(string.format('MATERIAIS: %d MeshParts com variante reconhecida, %d sem (ficaram como vieram), %d texturizadas, %d com sombra, %d cascas de camera', nOk, nSem, nTex, nSombra, nCasca))

-- colisoes: {nome, tipo, pos, eixoX, eixoY, tamanho, camera}
local COL = {
  {'COL_Anvil_001','Block',{0.0,8.1,-117.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{148.0,50.0,2.2},false},
  {'COL_Anvil_002','Block',{0.0,10.2,-117.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{142.0,44.0,2.0},false},
  {'COL_Anvil_003','Block',{0.0,12.1,-117.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{136.0,38.0,1.8},false},
  {'COL_Anvil_004','Block',{0.0,17.0,-118.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{94.0,44.0,8.0},false},
  {'COL_Anvil_005','Block',{0.0,32.0,-118.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{60.0,28.0,23.0},false},
  {'COL_Anvil_006','Block',{3.0,56.25,-118.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{98.0,38.0,26.5},false},
  {'COL_Court_001','Block',{-38.785,6.9,69.97},{0.875,0.0,0.485},{0.485,0.0,-0.875},{27.144,15.6,1.4},false},
  {'COL_Court_002','Block',{-38.785,6.9,69.97},{0.857,0.0,-0.515},{-0.515,0.0,-0.857},{27.144,15.6,1.4},false},
  {'COL_Court_003','Block',{-38.785,6.9,69.97},{-0.017,0.0,-1.0},{-1.0,0.0,0.017},{27.144,15.6,1.4},false},
  {'COL_Court_005','Block',{-38.785,7.2,69.97},{0.857,0.0,-0.515},{-0.515,0.0,-0.857},{24.186,13.9,2.0},false},
  {'COL_Court_006','Block',{-38.785,7.2,69.97},{-0.017,0.0,-1.0},{-1.0,0.0,0.017},{24.186,13.9,2.0},false},
  {'COL_Court_007','Block',{-54.418,17.16,74.452},{0.875,0.0,0.485},{0.485,0.0,-0.875},{2.8,2.8,18.0},true},
  {'COL_Court_008','Block',{-34.302,17.16,85.603},{0.875,0.0,0.485},{0.485,0.0,-0.875},{2.8,2.8,18.0},true},
  {'COL_Court_009','Block',{-64.309,6.9,47.586},{0.595,0.0,0.804},{0.804,0.0,-0.595},{27.144,15.6,1.4},false},
  {'COL_Court_010','Block',{-64.309,6.9,47.586},{0.994,0.0,-0.113},{-0.113,0.0,-0.994},{27.144,15.6,1.4},false},
  {'COL_Court_011','Block',{-64.309,6.9,47.586},{0.399,0.0,-0.917},{-0.917,0.0,-0.399},{27.144,15.6,1.4},false},
  {'COL_Court_012','Block',{-64.309,7.2,47.586},{0.595,0.0,0.804},{0.804,0.0,-0.595},{24.186,13.9,2.0},false},
  {'COL_Court_013','Block',{-64.309,7.2,47.586},{0.994,0.0,-0.113},{-0.113,0.0,-0.994},{24.186,13.9,2.0},false},
  {'COL_Court_014','Block',{-64.309,7.2,47.586},{0.399,0.0,-0.917},{-0.917,0.0,-0.399},{24.186,13.9,2.0},false},
  {'COL_Court_015','Block',{-80.393,17.16,45.182},{0.595,0.0,0.804},{0.804,0.0,-0.595},{2.8,2.8,18.0},true},
  {'COL_Court_016','Block',{-66.712,17.16,63.671},{0.595,0.0,0.804},{0.804,0.0,-0.595},{2.8,2.8,18.0},true},
  {'COL_Court_017','Block',{-78.252,6.9,16.633},{0.208,0.0,0.978},{0.978,0.0,-0.208},{27.144,15.6,1.4},false},
  {'COL_Court_018','Block',{-78.252,6.9,16.633},{0.951,0.0,0.309},{0.309,0.0,-0.951},{27.144,15.6,1.4},false},
  {'COL_Court_019','Block',{-78.252,6.9,16.633},{0.743,0.0,-0.669},{-0.669,0.0,-0.743},{27.144,15.6,1.4},false},
  {'COL_Court_020','Block',{-78.252,7.2,16.633},{0.208,0.0,0.978},{0.978,0.0,-0.208},{24.186,13.9,2.0},false},
  {'COL_Court_021','Block',{-78.252,7.2,16.633},{0.951,0.0,0.309},{0.309,0.0,-0.951},{24.186,13.9,2.0},false},
  {'COL_Court_022','Block',{-78.252,7.2,16.633},{0.743,0.0,-0.669},{-0.669,0.0,-0.743},{24.186,13.9,2.0},false},
  {'COL_Court_023','Block',{-91.891,17.16,7.775},{0.208,0.0,0.978},{0.978,0.0,-0.208},{2.8,2.8,18.0},true},
  {'COL_Court_024','Block',{-87.11,17.16,30.273},{0.208,0.0,0.978},{0.978,0.0,-0.208},{2.8,2.8,18.0},true},
  {'COL_Court_025','Block',{-78.104,6.9,-17.315},{-0.216,0.0,0.976},{0.976,0.0,0.216},{27.144,15.6,1.4},false},
  {'COL_Court_026','Block',{-78.104,6.9,-17.315},{0.737,0.0,0.676},{0.676,0.0,-0.737},{27.144,15.6,1.4},false},
  {'COL_Court_027','Block',{-78.104,6.9,-17.315},{0.954,0.0,-0.301},{-0.301,0.0,-0.954},{27.144,15.6,1.4},false},
  {'COL_Court_028','Block',{-78.104,7.2,-17.315},{-0.216,0.0,0.976},{0.976,0.0,0.216},{24.186,13.9,2.0},false},
  {'COL_Court_029','Block',{-78.104,7.2,-17.315},{0.737,0.0,0.676},{0.676,0.0,-0.737},{24.186,13.9,2.0},false},
  {'COL_Court_030','Block',{-78.104,7.2,-17.315},{0.954,0.0,-0.301},{-0.301,0.0,-0.954},{24.186,13.9,2.0},false},
  {'COL_Court_031','Block',{-86.842,17.16,-31.032},{-0.216,0.0,0.976},{0.976,0.0,0.216},{2.8,2.8,18.0},true},
  {'COL_Court_032','Block',{-91.82,17.16,-8.577},{-0.216,0.0,0.976},{0.976,0.0,0.216},{2.8,2.8,18.0},true},
  {'COL_Court_033','Block',{-63.891,6.9,-48.145},{-0.602,0.0,0.799},{0.799,0.0,0.602},{27.144,15.6,1.4},false},
  {'COL_Court_034','Block',{-63.891,6.9,-48.145},{0.391,0.0,0.921},{0.921,0.0,-0.391},{27.144,15.6,1.4},false},
  {'COL_Court_035','Block',{-63.891,6.9,-48.145},{0.993,0.0,0.122},{0.122,0.0,-0.993},{27.144,15.6,1.4},false},
  {'COL_Court_037','Block',{-63.891,7.2,-48.145},{0.391,0.0,0.921},{0.921,0.0,-0.391},{24.186,13.9,2.0},false},
  {'COL_Court_038','Block',{-63.891,7.2,-48.145},{0.993,0.0,0.122},{0.122,0.0,-0.993},{24.186,13.9,2.0},false},
  {'COL_Court_039','Block',{-66.154,17.16,-64.25},{-0.602,0.0,0.799},{0.799,0.0,0.602},{2.8,2.8,18.0},true},
  {'COL_Court_040','Block',{-79.996,17.16,-45.882},{-0.602,0.0,0.799},{0.799,0.0,0.602},{2.8,2.8,18.0},true},
  {'COL_Court_041','Block',{-38.173,6.9,-70.305},{-0.879,0.0,0.477},{0.477,0.0,0.879},{27.144,15.6,1.4},false},
  {'COL_Court_042','Block',{-38.173,6.9,-70.305},{-0.026,0.0,1.0},{1.0,0.0,0.026},{27.144,15.6,1.4},false},
  {'COL_Court_043','Block',{-38.173,6.9,-70.305},{0.853,0.0,0.522},{0.522,0.0,-0.853},{27.144,15.6,1.4},false},
  {'COL_Court_045','Block',{-38.173,7.2,-70.305},{-0.026,0.0,1.0},{1.0,0.0,0.026},{24.186,13.9,2.0},false},
  {'COL_Court_046','Block',{-38.173,7.2,-70.305},{0.853,0.0,0.522},{0.522,0.0,-0.853},{24.186,13.9,2.0},false},
  {'COL_Court_047','Block',{-33.554,17.16,-85.899},{-0.879,0.0,0.477},{0.477,0.0,0.879},{2.8,2.8,18.0},true},
  {'COL_Court_048','Block',{-53.766,17.16,-74.924},{-0.879,0.0,0.477},{0.477,0.0,0.879},{2.8,2.8,18.0},true},
  {'COL_Exit_001','Block',{0.0,8.13,51.15},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,3.86},false},
  {'COL_Exit_002','Block',{0.0,7.83,49.45},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,3.26},false},
  {'COL_Exit_003','Block',{0.0,7.53,47.75},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,2.66},false},
  {'COL_Exit_004','Block',{0.0,7.23,46.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,2.06},false},
  {'COL_Exit_005','Block',{0.0,6.93,44.35},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,1.46},false},
  {'COL_Exit_006','Block',{0.0,8.13,80.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,3.86},false},
  {'COL_Exit_007','Block',{0.0,7.83,82.55},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,3.26},false},
  {'COL_Exit_008','Block',{0.0,7.53,84.25},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,2.66},false},
  {'COL_Exit_009','Block',{0.0,7.23,85.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,2.06},false},
  {'COL_Exit_010','Block',{0.0,6.93,87.65},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.7,1.46},false},
  {'COL_Exit_011','Block',{0.0,8.1,66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{44.0,28.0,3.8},false},
  {'COL_Exit_012','Block',{-18.4,14.675,55.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.65,7.14,9.35},true},
  {'COL_Exit_013','Block',{18.4,14.675,55.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.65,7.14,9.35},true},
  {'COL_Exit_014','Block',{0.0,6.5,117.25},{1.0,0.0,0.0},{0.0,0.0,-1.0},{22.4,57.5,1.0},false},
  {'COL_Exit_015','Block',{-14.0,14.0,142.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_016','Block',{-14.0,14.0,133.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_017','Block',{-14.0,14.0,124.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_018','Block',{-14.0,14.0,115.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_019','Block',{-14.0,14.0,106.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_020','Block',{-14.0,14.0,97.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_021','Block',{14.0,14.0,142.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_022','Block',{14.0,14.0,133.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_023','Block',{14.0,14.0,124.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_024','Block',{14.0,14.0,115.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_025','Block',{14.0,14.0,106.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_026','Block',{14.0,14.0,97.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.0},true},
  {'COL_Exit_027','Block',{-12.5,15.0,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.4,5.4,16.0},true},
  {'COL_Exit_028','Block',{12.5,15.0,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.4,5.4,16.0},true},
  {'COL_Exit_029','Block',{0.0,6.117,157.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,11.667,1.6},false},
  {'COL_Exit_030','Block',{-7.55,8.217,157.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_031','Block',{7.55,8.217,157.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_032','Block',{0.0,5.95,169.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,11.667,1.6},false},
  {'COL_Exit_033','Block',{-7.55,8.05,169.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_034','Block',{7.55,8.05,169.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_035','Block',{0.0,5.783,181.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,11.667,1.6},false},
  {'COL_Exit_036','Block',{-7.55,7.883,181.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_037','Block',{7.55,7.883,181.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_038','Block',{0.0,5.617,192.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,11.667,1.6},false},
  {'COL_Exit_039','Block',{-7.55,7.717,192.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_040','Block',{7.55,7.717,192.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_041','Block',{0.0,5.45,204.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,11.667,1.6},false},
  {'COL_Exit_042','Block',{-7.55,7.55,204.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_043','Block',{7.55,7.55,204.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_044','Block',{0.0,5.283,216.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,11.667,1.6},false},
  {'COL_Exit_045','Block',{-7.55,7.383,216.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_046','Block',{7.55,7.383,216.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,11.667,2.6},false},
  {'COL_Exit_047','Block',{0.0,6.5,149.75},{1.0,0.0,0.0},{0.0,0.0,-1.0},{17.2,7.5,1.0},false},
  {'COL_Forge_001','Block',{0.0,6.52,-77.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{20.785,3.0,1.0},false},
  {'COL_Forge_002','Block',{0.0,6.52,-74.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{28.142,3.0,1.0},false},
  {'COL_Forge_003','Block',{0.0,6.52,-71.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{32.863,3.0,1.0},false},
  {'COL_Forge_004','Block',{0.0,6.52,-68.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{36.0,3.0,1.0},false},
  {'COL_Forge_005','Block',{0.0,6.52,-65.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{37.947,3.0,1.0},false},
  {'COL_Forge_006','Block',{0.0,6.52,-62.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{39.0,3.0,1.0},false},
  {'COL_Forge_007','Block',{0.0,6.52,-59.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{37.947,3.0,1.0},false},
  {'COL_Forge_008','Block',{0.0,6.52,-56.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{36.0,3.0,1.0},false},
  {'COL_Forge_009','Block',{0.0,6.52,-53.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{32.863,3.0,1.0},false},
  {'COL_Forge_010','Block',{0.0,6.52,-50.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{28.142,3.0,1.0},false},
  {'COL_Forge_012','Block',{0.0,6.52,-43.8},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{28.0,8.4,1.0},false},
  {'COL_Forge_013','Block',{-15.782,11.0,-56.719},{-0.317,0.0,-0.948},{-0.948,0.0,0.317},{4.142,3.5,8.0},false},
  {'COL_Forge_014','Block',{-16.566,11.0,-60.405},{-0.096,0.0,-0.995},{-0.995,0.0,0.096},{4.142,3.5,8.0},false},
  {'COL_Forge_015','Block',{-16.5,11.0,-64.172},{0.131,0.0,-0.991},{-0.991,0.0,-0.131},{4.142,3.5,8.0},false},
  {'COL_Forge_016','Block',{-15.588,11.0,-67.828},{0.35,0.0,-0.937},{-0.937,0.0,-0.35},{4.142,3.5,8.0},false},
  {'COL_Forge_017','Block',{-13.878,11.0,-71.186},{0.552,0.0,-0.834},{-0.834,0.0,-0.552},{4.142,3.5,8.0},false},
  {'COL_Forge_018','Block',{-11.456,11.0,-74.072},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{4.142,3.5,8.0},false},
  {'COL_Forge_019','Block',{-8.447,11.0,-76.34},{0.862,0.0,-0.508},{-0.508,0.0,-0.862},{4.142,3.5,8.0},false},
  {'COL_Forge_020','Block',{-5.004,11.0,-77.872},{0.954,0.0,-0.301},{-0.301,0.0,-0.954},{4.142,3.5,8.0},false},
  {'COL_Forge_021','Block',{-1.306,11.0,-78.591},{0.997,0.0,-0.078},{-0.078,0.0,-0.997},{4.142,3.5,8.0},false},
  {'COL_Forge_022','Block',{2.46,11.0,-78.46},{0.989,0.0,0.148},{0.148,0.0,-0.989},{4.142,3.5,8.0},false},
  {'COL_Forge_023','Block',{6.099,11.0,-77.484},{0.93,0.0,0.367},{0.367,0.0,-0.93},{4.142,3.5,8.0},false},
  {'COL_Forge_024','Block',{9.426,11.0,-75.715},{0.824,0.0,0.566},{0.566,0.0,-0.824},{4.142,3.5,8.0},false},
  {'COL_Forge_025','Block',{12.27,11.0,-73.243},{0.676,0.0,0.737},{0.737,0.0,-0.676},{4.142,3.5,8.0},false},
  {'COL_Forge_026','Block',{14.485,11.0,-70.195},{0.492,0.0,0.87},{0.87,0.0,-0.492},{4.142,3.5,8.0},false},
  {'COL_Forge_027','Block',{15.957,11.0,-66.727},{0.284,0.0,0.959},{0.959,0.0,-0.284},{4.142,3.5,8.0},false},
  {'COL_Forge_028','Block',{16.611,11.0,-63.016},{0.061,0.0,0.998},{0.998,0.0,-0.061},{4.142,3.5,8.0},false},
  {'COL_Forge_029','Block',{16.414,11.0,-59.253},{-0.165,0.0,0.986},{0.986,0.0,0.165},{4.142,3.5,8.0},false},
  {'COL_Forge_030','Block',{15.641,11.0,-56.152},{-0.35,0.0,0.937},{0.937,0.0,0.35},{2.978,3.5,8.0},false},
  {'COL_Forge_031','Block',{-15.181,20.0,-54.921},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.2,4.2,26.0},false},
  {'COL_Forge_032','Block',{15.181,20.0,-54.921},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.2,4.2,26.0},false},
  {'COL_Forge_033','Block',{-14.205,20.0,-70.876},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.2,4.2,26.0},false},
  {'COL_Forge_034','Block',{14.205,20.0,-70.876},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.2,4.2,26.0},false},
  {'COL_Forge_035','Block',{0.0,7.9,-74.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.0,9.0,1.8},false},
  {'COL_Forge_036','Block',{7.5,9.3,-73.0},{-0.866,0.0,0.5},{0.5,0.0,0.866},{4.0,7.6,4.6},false},
  {'COL_Forge_037','Block',{12.5,9.1,-44.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.4,5.0,4.2},false},
  {'COL_Forge_038','Block',{-7.5,9.3,-73.0},{-0.866,0.0,-0.5},{-0.5,0.0,0.866},{4.0,7.6,4.6},false},
  {'COL_Forge_039','Block',{-12.5,9.1,-44.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.4,5.0,4.2},false},
  {'COL_Hammer_001','Block',{106.0,14.0,-66.0},{-0.829,0.0,0.559},{0.559,0.0,0.829},{30.6,18.0,14.0},false},
  {'COL_Plaza_001','Block',{0.0,6.5,-35.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{35.327,4.0,1.0},false},
  {'COL_Plaza_002','Block',{0.0,6.5,-31.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{48.662,4.0,1.0},false},
  {'COL_Plaza_003','Block',{0.0,6.5,-27.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{57.966,4.0,1.0},false},
  {'COL_Plaza_004','Block',{0.0,6.5,-23.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{64.992,4.0,1.0},false},
  {'COL_Plaza_005','Block',{0.0,6.5,-19.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{70.427,4.0,1.0},false},
  {'COL_Plaza_006','Block',{0.0,6.5,-15.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{74.619,4.0,1.0},false},
  {'COL_Plaza_007','Block',{0.0,6.5,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{77.769,4.0,1.0},false},
  {'COL_Plaza_008','Block',{0.0,6.5,-7.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{80.0,4.0,1.0},false},
  {'COL_Plaza_009','Block',{0.0,6.5,-3.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{81.388,4.0,1.0},false},
  {'COL_Plaza_010','Block',{0.0,6.5,1.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{82.0,4.0,1.0},false},
  {'COL_Plaza_011','Block',{0.0,6.5,5.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{80.796,4.0,1.0},false},
  {'COL_Plaza_012','Block',{0.0,6.5,9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{78.994,4.0,1.0},false},
  {'COL_Plaza_013','Block',{0.0,6.5,13.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{76.315,4.0,1.0},false},
  {'COL_Plaza_014','Block',{0.0,6.5,17.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{72.664,4.0,1.0},false},
  {'COL_Plaza_015','Block',{0.0,6.5,21.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{67.882,4.0,1.0},false},
  {'COL_Plaza_016','Block',{0.0,6.5,25.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{61.709,4.0,1.0},false},
  {'COL_Plaza_017','Block',{0.0,6.5,29.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{53.666,4.0,1.0},false},
  {'COL_Plaza_018','Block',{0.0,6.5,33.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{42.708,4.0,1.0},false},
  {'COL_Plaza_019','Block',{0.0,6.5,37.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{25.298,4.0,1.0},false},
  {'COL_Portal_001','Block',{-38.009,7.9,68.57},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{27.2,22.4,1.4},false},
  {'COL_Portal_002','Block',{-39.148,8.41,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{10.746,10.746,2.42},false},
  {'COL_Portal_003','Block',{-39.148,8.41,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{13.984,5.776,2.42},false},
  {'COL_Portal_004','Block',{-39.148,8.41,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{5.776,13.984,2.42},false},
  {'COL_Portal_005','Block',{-39.148,8.925,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{9.191,9.191,3.45},false},
  {'COL_Portal_006','Block',{-39.148,8.925,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{11.96,4.94,3.45},false},
  {'COL_Portal_007','Block',{-39.148,8.925,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{4.94,11.96,3.45},false},
  {'COL_Portal_008','Block',{-39.148,9.425,70.626},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{11.2,5.2,4.45},false},
  {'COL_Portal_009','Block',{-36.016,11.719,72.362},{0.793,0.423,0.439},{-0.485,-0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_010','Block',{-33.388,14.067,73.819},{0.55,0.777,0.305},{-0.485,-0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_011','Block',{-31.926,17.494,74.629},{0.197,0.974,0.109},{-0.485,0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_012','Block',{-31.926,21.306,74.629},{-0.197,0.974,-0.109},{-0.485,0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_013','Block',{-42.281,11.719,68.889},{0.793,-0.423,0.439},{-0.485,0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_014','Block',{-44.909,14.067,67.432},{0.55,-0.777,0.305},{-0.485,0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_015','Block',{-46.371,17.494,66.622},{0.197,-0.974,0.109},{-0.485,-0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_016','Block',{-46.371,21.306,66.622},{-0.197,-0.974,-0.109},{-0.485,-0.0,0.875},{4.429,3.5,1.85},false},
  {'COL_Portal_017','Block',{-28.828,22.55,76.346},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{2.8,2.8,27.9},false},
  {'COL_Portal_018','Block',{-49.469,22.55,64.905},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{2.8,2.8,27.9},false},
  {'COL_Portal_019','Block',{-25.286,12.182,69.623},{0.977,-0.0,-0.214},{-0.202,0.334,-0.921},{1.8,1.8,9.0},false},
  {'COL_Portal_020','Block',{-45.382,10.2,62.482},{-0.934,0.0,-0.358},{-0.358,0.0,0.934},{5.6,3.6,3.2},false},
  {'COL_Portal_021','Block',{-62.62,8.15,46.337},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{26.2,12.2,1.9},false},
  {'COL_Portal_022','Block',{-62.62,8.15,46.337},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{14.8,21.4,1.9},false},
  {'COL_Portal_023','Block',{-64.309,9.3,47.586},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{21.6,5.2,1.4},false},
  {'COL_Portal_024','Block',{-64.309,9.3,47.586},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{17.2,9.4,1.4},false},
  {'COL_Portal_025','Block',{-64.309,9.3,47.586},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{10.8,12.0,1.4},false},
  {'COL_Portal_026','Block',{-62.62,8.15,46.337},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{22.0,17.4,1.9},false},
  {'COL_Portal_027','Block',{-64.309,9.3,47.586},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{18.4,8.4,1.4},false},
  {'COL_Portal_028','Block',{-60.046,12.878,54.817},{0.469,-0.616,0.633},{-0.804,-0.0,0.595},{2.588,5.451,5.066},false},
  {'COL_Portal_029','Block',{-62.174,9.722,51.878},{0.261,-0.899,0.352},{-0.804,-0.0,0.595},{2.934,5.525,5.144},false},
  {'COL_Portal_030','Block',{-62.024,11.873,50.463},{0.261,-0.899,0.352},{-0.804,0.0,0.595},{1.85,2.25,4.068},false},
  {'COL_Portal_031','Block',{-69.977,12.878,41.395},{-0.469,-0.616,-0.633},{-0.804,0.0,0.595},{2.588,5.451,5.066},false},
  {'COL_Portal_032','Block',{-67.789,9.722,44.29},{-0.261,-0.899,-0.352},{-0.804,0.0,0.595},{2.934,5.525,5.144},false},
  {'COL_Portal_033','Block',{-66.392,11.873,44.56},{-0.261,-0.899,-0.352},{-0.804,-0.0,0.595},{1.85,2.25,4.068},false},
  {'COL_Portal_034','Block',{-59.616,13.818,53.885},{0.559,-0.342,0.755},{-0.804,-0.0,0.595},{3.58,2.45,9.829},false},
  {'COL_Portal_035','Block',{-58.819,20.382,55.004},{0.589,0.139,0.796},{-0.804,0.0,0.595},{3.55,2.3,6.133},false},
  {'COL_Portal_036','Block',{-68.96,13.818,41.257},{-0.559,-0.342,-0.755},{-0.804,-0.0,0.595},{3.58,2.45,9.829},false},
  {'COL_Portal_037','Block',{-69.798,20.382,40.168},{-0.589,0.139,-0.796},{-0.804,0.0,0.595},{3.55,2.3,6.133},false},
  {'COL_Portal_038','Block',{-51.479,10.2,49.289},{0.367,0.0,0.93},{0.93,0.0,-0.367},{4.9,2.0,2.2},false},
  {'COL_Portal_039','Block',{-61.672,10.815,35.683},{-0.367,0.0,-0.93},{-0.93,0.0,0.367},{6.0,2.0,3.53},false},
  {'COL_Portal_040','Block',{-64.248,10.825,47.541},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{13.6,2.35,2.05},false},
  {'COL_Portal_041','Block',{-66.117,12.15,48.924},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{16.0,2.7,4.7},false},
  {'COL_Portal_042','Block',{-65.884,19.4,48.752},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{7.2,2.52,7.2},false},
  {'COL_Portal_043','Block',{-62.29,16.483,52.939},{-0.838,-0.074,-0.54},{0.165,-0.979,-0.122},{5.253,4.687,1.6},false},
  {'COL_Portal_044','Block',{-62.55,20.667,52.997},{-0.84,0.032,-0.542},{-0.072,-0.996,0.053},{5.026,5.279,1.6},false},
  {'COL_Portal_045','Block',{-68.838,16.483,44.09},{-0.271,0.074,-0.96},{0.165,-0.979,-0.122},{5.253,4.687,1.6},false},
  {'COL_Portal_046','Block',{-68.969,20.667,44.322},{-0.273,-0.032,-0.962},{-0.072,-0.996,0.053},{5.026,5.279,1.6},false},
  {'COL_Portal_047','Block',{-75.268,7.925,15.999},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{27.2,14.3,1.45},false},
  {'COL_Portal_048','Block',{-75.22,7.925,15.988},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{23.36,17.4,1.45},false},
  {'COL_Portal_049','Block',{-75.024,8.2,15.947},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{17.2,9.4,2.0},false},
  {'COL_Portal_050','Block',{-74.437,8.2,15.822},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{14.32,10.6,2.0},false},
  {'COL_Portal_051','Block',{-75.709,8.475,16.092},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{14.0,6.0,2.55},false},
  {'COL_Portal_052','Block',{-75.22,8.475,15.988},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{11.6,7.0,2.55},false},
  {'COL_Portal_053','Block',{-76.209,14.95,27.445},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{3.8,4.3,13.5},false},
  {'COL_Portal_054','Block',{-80.783,14.95,5.925},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{3.8,4.3,13.5},false},
  {'COL_Portal_055','Block',{-77.135,10.775,23.092},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{5.1,2.0,4.25},false},
  {'COL_Portal_056','Block',{-76.739,17.3,24.95},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{1.3,2.0,8.8},false},
  {'COL_Portal_057','Block',{-79.858,10.775,10.278},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{5.1,2.0,4.25},false},
  {'COL_Portal_058','Block',{-80.253,17.3,8.42},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{1.3,2.0,8.8},false},
  {'COL_Portal_059','Block',{-79.474,19.4,16.893},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{10.7,2.1,10.7},false},
  {'COL_Portal_060','Block',{-79.474,19.4,16.893},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{13.9,2.1,5.74},false},
  {'COL_Portal_061','Block',{-79.474,19.4,16.893},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{5.74,2.1,13.9},false},
  {'COL_Portal_062','Block',{-71.216,8.65,27.61},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{2.1,2.1,1.9},false},
  {'COL_Portal_063','Block',{-71.216,11.625,27.61},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{1.0,1.0,4.05},false},
  {'COL_Portal_064','Block',{-77.644,9.775,3.622},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{1.6,1.6,4.15},false},
  {'COL_Portal_065','Block',{-76.388,12.8,4.48},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{1.8,1.7,1.9},false},
  {'COL_Portal_066','Block',{-68.585,7.925,-15.205},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{6.0,5.7,1.45},false},
  {'COL_Portal_067','Block',{-71.953,8.2,-15.952},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{5.2,1.2,2.0},false},
  {'COL_Portal_068','Block',{-72.978,8.7,-16.179},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{4.6,1.1,3.0},false},
  {'COL_Portal_069','Block',{-70.464,10.775,-10.193},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.1,1.1,5.15},false},
  {'COL_Portal_070','Block',{-68.17,10.775,-20.542},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.1,1.1,5.15},false},
  {'COL_Portal_071','Block',{-77.772,13.7,-4.028},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.7,1.7,11.0},false},
  {'COL_Portal_072','Block',{-78.836,9.2,-17.477},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{10.0,8.3,4.0},false},
  {'COL_Portal_073','Block',{-80.562,9.0,-10.383},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{4.6,8.0,3.6},false},
  {'COL_Portal_074','Block',{-81.336,9.35,-7.584},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.2,7.7,4.3},false},
  {'COL_Portal_075','Block',{-81.634,9.8,-6.472},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.1,7.0,5.2},false},
  {'COL_Portal_076','Block',{-81.737,8.975,-5.317},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.2,10.1,3.55},false},
  {'COL_Portal_077','Block',{-79.9,14.9,-9.212},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{2.2,1.9,3.0},false},
  {'COL_Portal_078','Block',{-80.138,20.05,-8.138},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{2.8,1.9,7.3},false},
  {'COL_Portal_079','Block',{-83.192,12.8,-9.378},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{3.5,2.1,4.0},false},
  {'COL_Portal_080','Block',{-77.402,9.0,-24.637},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{4.6,8.0,3.6},false},
  {'COL_Portal_081','Block',{-76.921,9.35,-27.501},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.2,7.7,4.3},false},
  {'COL_Portal_082','Block',{-76.721,9.8,-28.634},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.1,7.0,5.2},false},
  {'COL_Portal_083','Block',{-76.326,8.975,-29.724},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{1.2,10.1,3.55},false},
  {'COL_Portal_084','Block',{-76.307,14.9,-25.418},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{2.2,1.9,3.0},false},
  {'COL_Portal_085','Block',{-76.069,20.05,-26.492},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{2.8,1.9,7.3},false},
  {'COL_Portal_086','Block',{-79.361,12.8,-26.659},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{3.5,2.1,4.0},false},
  {'COL_Portal_087','Block',{-74.247,8.95,-16.46},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{23.8,1.7,3.5},false},
  {'COL_Portal_088','Block',{-83.62,8.975,-18.538},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{23.8,2.1,3.55},false},
  {'COL_Portal_089','Block',{-80.398,19.2,-17.824},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{15.2,3.9,16.0},false},
  {'COL_Portal_090','Block',{-62.214,8.0,-46.881},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{22.8,21.4,1.6},false},
  {'COL_Portal_091','Block',{-69.375,9.6,-37.378},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{1.4,21.4,2.8},false},
  {'COL_Portal_092','Block',{-55.052,9.6,-56.385},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{1.4,21.4,2.8},false},
  {'COL_Portal_093','Block',{-63.891,8.55,-48.145},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{12.16,12.16,2.5},false},
  {'COL_Portal_094','Block',{-63.891,8.55,-48.145},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{15.824,6.536,2.5},false},
  {'COL_Portal_095','Block',{-63.891,8.55,-48.145},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{6.536,15.824,2.5},false},
  {'COL_Portal_096','Block',{-63.891,8.95,-48.145},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{9.332,9.332,3.3},false},
  {'COL_Portal_097','Block',{-63.891,8.95,-48.145},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{12.144,5.016,3.3},false},
  {'COL_Portal_098','Block',{-63.891,8.95,-48.145},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{5.016,12.144,3.3},false},
  {'COL_Portal_099','Block',{-62.559,14.0,-35.622},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{5.0,1.4,10.5},false},
  {'COL_Portal_100','Block',{-61.984,19.7,-59.981},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{1.4,1.4,23.0},false},
  {'COL_Portal_101','Block',{-50.928,10.3,-49.396},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{3.6,2.8,3.0},false},
  {'COL_Portal_102','Block',{-73.652,10.1,-47.487},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{2.4,2.4,2.6},false},
  {'COL_Portal_103','Block',{-54.201,10.1,-52.363},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{2.4,2.4,2.6},false},
  {'COL_Portal_104','Block',{-75.699,12.2,-44.772},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{1.6,1.6,8.0},false},
  {'COL_Portal_110','Block',{-65.528,18.8,-49.379},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{15.2,0.4,16.4},false},
  {'COL_Portal_111','Block',{-37.409,7.95,-68.899},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{27.6,22.4,1.5},false},
  {'COL_Portal_112','Block',{-36.694,8.925,-67.581},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{11.6,5.8,1.45},false},
  {'COL_Portal_113','Block',{-37.314,9.4,-68.723},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{10.0,3.2,2.4},false},
  {'COL_Portal_114','Block',{-46.31,20.275,-66.798},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{3.65,4.2,24.15},false},
  {'COL_Portal_115','Block',{-30.799,20.275,-75.219},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{3.65,4.2,24.15},false},
  {'COL_Portal_116','Block',{-38.554,28.775,-71.008},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{14.0,3.2,7.15},false},
  {'COL_Portal_117','Block',{-38.698,9.9,-71.272},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{7.2,2.6,3.4},false},
  {'COL_Portal_118','Block',{-43.355,10.5,-68.743},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{3.4,2.6,4.6},false},
  {'COL_Portal_119','Block',{-34.04,10.5,-73.801},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{3.4,2.6,4.6},false},
  {'COL_Portal_120','Block',{-39.103,18.4,-72.019},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{12.0,0.9,13.6},false},
  {'COL_Portal_121','Ramp',{-37.472,9.298,-75.093},{0.386,0.588,0.711},{0.879,0.0,-0.477},{2.08,3.4,0.8},false},
  {'COL_Portal_122','Block',{-35.495,9.119,-78.426},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{3.214,3.004,1.839},false},
  {'COL_Portal_123','Block',{-35.955,10.392,-78.723},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{1.212,1.948,0.768},false},
  {'COL_Portal_124','Block',{-39.734,8.912,-78.211},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{2.478,2.247,1.425},false},
  {'COL_Portal_125','Ramp',{-30.243,9.181,-72.676},{-0.331,0.719,-0.61},{-0.879,-0.0,0.477},{1.56,2.2,0.8},false},
  {'COL_Portal_126','Block',{-27.696,8.916,-71.591},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{1.515,1.426,1.433},false},
  {'COL_Portal_127','Block',{-28.3,9.824,-71.632},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{0.559,0.477,0.698},false},
  {'COL_Portal_128','Block',{-29.381,8.715,-69.214},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{0.898,0.966,1.03},false},
  {'COL_Portal_129','Block',{-41.931,9.675,-58.365},{0.609,0.0,-0.793},{-0.793,0.0,-0.609},{4.4,1.2,2.95},false},
  {'COL_Portal_130','Block',{-42.84,9.425,-62.764},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{0.8,0.8,2.45},false},
  {'COL_Portal_131','Block',{-44.475,9.279,-63.47},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{0.68,0.68,2.158},false},
  {'COL_Rank_001','Block',{64.348,7.0,53.994},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{68.0,26.0,1.2},false},
  {'COL_Rank_002','Block',{53.777,6.7,45.123},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{68.6,1.6,0.6},false},
  {'COL_Rank_003','Block',{50.242,18.6,82.626},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{3.4,3.4,22.0},true},
  {'COL_Rank_004','Block',{90.097,18.6,35.133},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{3.4,3.4,22.0},true},
  {'COL_Rank_005','Block',{72.161,27.6,60.55},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{68.0,3.2,40.0},true},
  {'COL_Rank_006','Block',{68.255,20.9,57.272},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{56.0,2.6,26.6},true},
  {'COL_Ruins_001','Block',{-42.596,13.8,-19.863},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_002','Block',{38.5,13.8,-26.958},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_003','Block',{45.399,13.8,-12.164},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_004','Block',{112.0,8.8,18.0},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{13.0,10.0,9.0},false},
  {'COL_Ruins_005','Block',{-113.342,9.4,-86.175},{0.489,0.0,-0.873},{-0.873,0.0,-0.489},{60.0,1.8,6.0},false},
  {'COL_Ruins_015','Block',{103.141,9.4,-126.266},{0.841,0.0,0.541},{0.541,0.0,-0.841},{36.0,1.8,6.0},false},
  {'COL_Ruins_021','Block',{115.652,9.4,72.58},{-0.514,0.0,0.857},{0.857,0.0,0.514},{48.0,1.8,6.0},false},
  {'COL_Ruins_029','Block',{-89.42,9.4,116.348},{0.857,0.0,0.514},{0.514,0.0,-0.857},{48.0,1.8,6.0},false},
  {'COL_Ruins_037','Block',{-138.932,9.4,-3.498},{0.045,0.0,-0.999},{-0.999,0.0,-0.045},{47.045,1.8,6.0},false},
  {'COL_Ruins_045','Block',{43.577,9.4,133.474},{-0.949,0.0,0.316},{0.316,0.0,0.949},{34.623,1.8,6.0},false},
  {'COL_Ruins_051','Block',{-117.064,11.5,-50.85},{-0.866,0.0,0.5},{0.5,0.0,0.866},{2.6,2.6,10.0},false},
  {'COL_Ruins_052','Block',{-126.936,11.5,-45.15},{-0.866,0.0,0.5},{0.5,0.0,0.866},{2.6,2.6,10.0},false},
  {'COL_Ruins_053','Block',{110.05,11.5,-133.356},{0.342,0.0,0.94},{0.94,0.0,-0.342},{2.6,2.6,10.0},false},
  {'COL_Ruins_054','Block',{113.95,11.5,-122.644},{0.342,0.0,0.94},{0.94,0.0,-0.342},{2.6,2.6,10.0},false},
  {'COL_Ruins_055','Block',{-61.01,11.5,112.387},{-0.174,0.0,0.985},{0.985,0.0,0.174},{2.6,2.6,10.0},false},
  {'COL_Ruins_056','Block',{-62.99,11.5,123.613},{-0.174,0.0,0.985},{0.985,0.0,0.174},{2.6,2.6,10.0},false},
  {'COL_Shop_001','Block',{71.961,6.9,-33.555},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{32.0,27.2,1.4},false},
  {'COL_Shop_002','Block',{72.233,7.9,-33.682},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{30.0,25.0,0.6},true},
  {'COL_Shop_003','Block',{81.931,14.9,-38.204},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{28.0,1.6,13.4},true},
  {'COL_Shop_004','Block',{81.074,14.9,-23.24},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{1.6,15.8,13.4},true},
  {'COL_Shop_005','Block',{72.759,14.9,-24.273},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{10.5,1.6,13.4},true},
  {'COL_Shop_006','Block',{69.917,14.9,-47.167},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{1.6,15.8,13.4},true},
  {'COL_Shop_007','Block',{65.363,14.9,-40.133},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{10.5,1.6,13.4},true},
  {'COL_Shop_008','Block',{69.061,19.4,-32.203},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{7.0,1.6,4.4},true},
  {'COL_Shop_009','Block',{75.284,9.9,-34.001},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{12.6,2.2,3.4},true},
  {'COL_Shop_010','Block',{80.481,13.2,-37.528},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{23.0,1.6,10.0},true},
  {'COL_Shop_011','Block',{67.619,14.9,-18.732},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{2.4,2.4,13.4},true},
  {'COL_Shop_012','Block',{64.576,14.9,-25.257},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{2.4,2.4,13.4},true},
  {'COL_Shop_013','Block',{60.857,14.9,-33.233},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{2.4,2.4,13.4},true},
  {'COL_Shop_014','Block',{57.815,14.9,-39.758},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{2.4,2.4,13.4},true},
  {'COL_Shop_015','Block',{74.055,10.0,-44.683},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{3.4,3.4,3.6},false},
  {'COL_Shop_016','Block',{72.958,27.1,-34.02},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{31.0,26.0,2.0},true},
  {'COL_Terrain_001','Block',{0.0,4.8,-160.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{150.0,8.0,4.0},false},
  {'COL_Terrain_002','Block',{0.0,4.8,-152.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{182.0,8.0,4.0},false},
  {'COL_Terrain_003','Block',{0.0,4.8,-144.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{214.0,8.0,4.0},false},
  {'COL_Terrain_004','Block',{0.0,4.8,-136.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{230.0,8.0,4.0},false},
  {'COL_Terrain_005','Block',{0.0,4.8,-128.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{242.0,8.0,4.0},false},
  {'COL_Terrain_006','Block',{0.0,4.8,-120.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{250.0,8.0,4.0},false},
  {'COL_Terrain_007','Block',{0.0,4.8,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{262.0,8.0,4.0},false},
  {'COL_Terrain_008','Block',{0.0,4.8,-104.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{270.0,8.0,4.0},false},
  {'COL_Terrain_009','Block',{0.0,4.8,-96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{282.0,8.0,4.0},false},
  {'COL_Terrain_010','Block',{0.0,4.8,-84.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{286.0,16.0,4.0},false},
  {'COL_Terrain_012','Block',{0.0,4.8,-68.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{290.0,16.0,4.0},false},
  {'COL_Terrain_014','Block',{0.0,4.8,-56.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{294.0,8.0,4.0},false},
  {'COL_Terrain_015','Block',{0.0,4.8,-20.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{298.0,64.0,4.0},false},
  {'COL_Terrain_023','Block',{0.0,4.8,28.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{294.0,32.0,4.0},false},
  {'COL_Terrain_027','Block',{0.0,4.8,48.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{290.0,8.0,4.0},false},
  {'COL_Terrain_028','Block',{0.0,4.8,56.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{282.0,8.0,4.0},false},
  {'COL_Terrain_029','Block',{0.0,4.8,64.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{274.0,8.0,4.0},false},
  {'COL_Terrain_030','Block',{0.0,4.8,72.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{270.0,8.0,4.0},false},
  {'COL_Terrain_031','Block',{0.0,4.8,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{262.0,8.0,4.0},false},
  {'COL_Terrain_032','Block',{0.0,4.8,88.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{258.0,8.0,4.0},false},
  {'COL_Terrain_033','Block',{0.0,4.8,96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{250.0,8.0,4.0},false},
  {'COL_Terrain_034','Block',{0.0,4.8,104.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{238.0,8.0,4.0},false},
  {'COL_Terrain_035','Block',{0.0,4.8,112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{218.0,8.0,4.0},false},
  {'COL_Terrain_036','Block',{0.0,4.8,120.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{198.0,8.0,4.0},false},
  {'COL_Terrain_037','Block',{0.0,4.8,128.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{182.0,8.0,4.0},false},
  {'COL_Terrain_038','Block',{0.0,4.8,136.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{162.0,8.0,4.0},false},
  {'COL_Terrain_039','Block',{0.0,4.8,144.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{138.0,8.0,4.0},false},
  {'COL_Terrain_040','Block',{0.0,4.8,149.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{54.0,2.0,4.0},false},
  {'COL_Veg_001','Block',{127.263,12.343,-17.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.129,2.129,11.086},false},
  {'COL_Veg_002','Block',{-122.965,12.138,18.979},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.05,2.05,10.676},false},
  {'COL_Veg_003','Block',{28.94,12.671,-71.861},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.254,2.254,11.742},false},
  {'COL_Veg_004','Block',{34.351,11.974,125.026},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.987,1.987,10.349},false},
  {'COL_Veg_005','Block',{-109.147,13.857,-8.109},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.71,2.71,14.115},false},
  {'COL_Veg_006','Block',{-118.534,12.113,65.501},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.04,2.04,10.626},false},
  {'COL_Veg_007','Block',{140.141,13.24,14.345},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.473,2.473,12.88},false},
  {'COL_Veg_008','Block',{133.582,13.562,-31.899},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.596,2.596,13.523},false},
  {'COL_Veg_009','Block',{139.925,12.671,40.478},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.254,2.254,11.742},false},
  {'COL_Veg_010','Block',{-125.272,12.128,-79.245},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.046,2.046,10.656},false},
  {'COL_Veg_011','Block',{-107.474,13.331,60.014},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.508,2.508,13.062},false},
  {'COL_Veg_012','Block',{-120.431,12.015,84.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.003,2.003,10.431},false},
  {'COL_Veg_013','Block',{-76.821,12.985,-70.03},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.375,2.375,12.369},false},
  {'COL_Veg_014','Block',{9.244,12.014,-149.763},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.002,2.002,10.427},false},
  {'COL_Veg_015','Block',{-131.657,12.638,-35.062},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.242,2.242,11.676},false},
  {'COL_Veg_016','Block',{108.817,12.466,-99.761},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.176,2.176,11.333},false},
  {'COL_Veg_017','Block',{25.658,13.105,131.475},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.421,2.421,12.61},false},
  {'COL_Veg_018','Block',{-20.968,12.133,138.277},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.048,2.048,10.666},false},
  {'COL_Veg_019','Block',{38.965,10.676,84.995},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.419,2.419,7.752},false},
  {'COL_Veg_020','Block',{-92.795,11.93,65.815},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.201,3.201,10.26},false},
  {'COL_Veg_021','Block',{-115.048,11.598,-31.883},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.994,2.994,9.595},false},
  {'COL_Veg_022','Block',{-86.787,10.723,-40.198},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.448,2.448,7.846},false},
  {'COL_Veg_023','Block',{106.313,11.191,37.536},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.74,2.74,8.781},false},
  {'COL_Veg_024','Block',{-17.42,10.694,116.002},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.43,2.43,7.789},false},
  {'COL_Veg_025','Block',{-55.389,10.792,99.483},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.491,2.491,7.983},false},
  {'COL_Veg_026','Block',{-57.291,11.401,84.535},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.871,2.871,9.201},false},
  {'COL_Veg_027','Block',{-106.131,10.72,-66.343},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.446,2.446,7.84},false},
  {'COL_Veg_028','Block',{99.278,10.763,83.025},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.473,2.473,7.927},false},
  {'COL_Veg_029','Block',{-32.121,10.983,100.717},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.61,2.61,8.365},false},
  {'COL_Veg_030','Block',{-104.762,11.02,18.948},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.633,2.633,8.441},false},
  {'COL_Veg_031','Block',{46.207,11.287,114.419},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,8.974},false},
  {'COL_Veg_032','Block',{79.466,11.593,18.887},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.991,2.991,9.586},false},
  {'COL_Veg_033','Block',{58.032,14.745,-150.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.051,3.051,15.89},false},
  {'COL_Veg_034','Block',{-128.089,13.46,33.649},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.557,2.557,13.32},false},
  {'COL_Veg_035','Block',{89.106,13.283,-108.209},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.49,2.49,12.966},false},
  {'COL_Veg_036','Block',{-86.14,13.865,-79.284},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.713,2.713,14.131},false},
  {'COL_Veg_037','Block',{-129.367,13.203,-92.284},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.459,2.459,12.806},false},
  {'COL_Veg_038','Block',{125.208,14.374,-99.951},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.908,2.908,15.148},false},
  {'COL_Veg_039','Block',{-127.421,14.709,7.474},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.037,3.037,15.817},false},
  {'COL_Veg_040','Block',{71.102,14.963,118.662},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.135,3.135,16.326},false},
  {'COL_Veg_041','Block',{121.716,14.777,43.237},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.063,3.063,15.954},false},
  {'COL_Veg_042','Block',{101.129,13.744,102.498},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.667,2.667,13.888},false},
  {'COL_Veg_043','Block',{-13.55,14.5,-156.236},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.957,2.957,15.401},false},
  {'COL_Veg_044','Block',{-87.528,14.006,103.142},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.767,2.767,14.412},false},
  {'COL_Veg_045','Block',{140.532,15.127,0.607},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.198,3.198,16.654},false},
  {'COL_Veg_046','Block',{86.981,13.91,-124.435},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.73,2.73,14.22},false},
  {'COL_Veg_047','Block',{54.715,15.116,122.171},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.193,3.193,16.632},false},
  {'COL_Veg_048','Block',{117.955,15.316,87.736},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.27,3.27,17.032},false},
  {'COL_Veg_049','Block',{-124.067,14.797,48.352},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.071,3.071,15.995},false},
  {'COL_Veg_050','Block',{-132.238,14.08,-67.148},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.795,2.795,14.56},false},
  {'COL_Veg_051','Block',{97.898,14.762,-98.56},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.058,3.058,15.925},false},
  {'COL_Veg_052','Block',{42.512,14.657,-152.111},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.017,3.017,15.715},false},
  {'COL_Veg_053','Block',{-134.41,13.657,54.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.633,2.633,13.714},false},
  {'COL_Veg_054','Block',{-34.587,13.425,127.789},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.544,2.544,13.249},false},
  {'COL_Veg_055','Block',{-133.614,14.079,-8.395},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.795,2.795,14.559},false},
  {'COL_Veg_056','Block',{140.647,15.137,-59.275},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.201,3.201,16.674},false},
  {'COL_Veg_057','Block',{-138.959,14.583,-55.423},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.989,2.989,15.566},false},
  {'COL_Veg_058','Block',{112.969,15.065,64.484},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.174,3.174,16.53},false},
  {'COL_Veg_059','Block',{130.106,13.593,-42.284},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.608,2.608,13.586},false},
  {'COL_Veg_060','Block',{105.033,13.512,-115.379},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.577,2.577,13.423},false},
  {'COL_Veg_061','Block',{17.859,13.295,142.384},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.494,2.494,12.991},false},
  {'COL_Veg_062','Block',{85.224,13.361,-95.395},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.519,2.519,13.122},false},
  {'COL_Veg_063','Block',{-79.684,15.43,112.906},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.314,3.314,17.261},false},
  {'COL_Veg_064','Block',{-83.118,13.92,-139.919},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.734,2.734,14.241},false},
  {'COL_Veg_065','Block',{41.048,13.766,-81.651},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.675,2.675,13.931},false},
  {'COL_Veg_066','Block',{-17.841,11.831,100.522},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.14,3.14,10.063},false},
  {'COL_Veg_067','Block',{-110.71,12.23,38.127},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.388,3.388,10.859},false},
  {'COL_Veg_068','Block',{66.581,11.69,92.961},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.052,3.052,9.78},false},
  {'COL_Veg_069','Block',{56.11,11.683,-62.866},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.047,3.047,9.765},false},
  {'COL_Veg_070','Block',{-103.024,11.994,72.958},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.241,3.241,10.387},false},
  {'COL_Veg_071','Block',{95.139,11.945,-13.44},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.21,3.21,10.289},false},
  {'COL_Veg_072','Block',{19.79,11.733,120.248},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.078,3.078,9.866},false},
  {'COL_Veg_073','Block',{78.984,12.509,66.496},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.562,3.562,11.417},false},
  {'COL_Veg_074','Block',{71.398,11.181,-65.729},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.734,2.734,8.762},false},
  {'COL_Veg_075','Block',{42.915,11.985,102.168},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.235,3.235,10.369},false},
  {'COL_Veg_076','Block',{113.866,12.585,-21.236},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.61,3.61,11.571},false},
  {'COL_Veg_077','Block',{102.065,13.684,58.252},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.296,4.296,13.769},false},
  {'COL_Veg_078','Block',{61.401,12.123,106.27},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.322,3.322,10.646},false},
  {'COL_Veg_079','Block',{83.39,13.017,2.661},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.879,3.879,12.434},false},
  {'COL_Veg_080','Block',{-83.865,13.597,76.321},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.242,4.242,13.595},false},
  {'COL_Veg_081','Block',{110.774,13.002,-1.937},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.87,3.87,12.405},false},
  {'COL_Veg_082','Block',{95.253,12.378,24.873},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.481,3.481,11.156},false},
  {'COL_Veg_083','Block',{137.74,12.056,-12.11},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.28,3.28,10.511},false},
  {'COL_Veg_084','Block',{22.371,12.368,108.089},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.474,3.474,11.136},false},
  {'COL_Veg_085','Block',{71.827,11.935,131.287},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.204,3.204,10.27},false},
  {'COL_Veg_086','Block',{-72.906,13.259,94.647},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.03,4.03,12.918},false},
  {'COL_Veg_087','Block',{-97.124,13.044,-48.201},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.897,3.897,12.489},false},
  {'COL_Veg_088','Block',{-41.356,12.171,115.755},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.352,3.352,10.742},false},
  {'COL_Veg_089','Block',{37.488,11.597,-43.947},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.993,2.993,9.594},false},
  {'COL_Veg_090','Block',{129.781,12.161,62.826},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.346,3.346,10.723},false},
  {'COL_Veg_091','Block',{-125.168,13.268,-25.557},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.036,4.036,12.935},false},
  {'COL_Veg_092','Block',{31.568,11.994,-155.285},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.241,3.241,10.388},false},
  {'COL_Veg_093','Block',{73.33,13.047,80.288},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.898,3.898,12.493},false},
  {'COL_Veg_094','Block',{82.651,11.983,-140.111},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.234,3.234,10.365},false},
  {'COL_Veg_095','Block',{-102.735,12.632,97.251},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.639,3.639,11.665},false},
  {'COL_Veg_096','Block',{80.058,13.144,93.828},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.958,3.958,12.687},false},
  {'COL_Veg_097','Block',{-51.245,12.239,127.725},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.394,3.394,10.878},false},
  {'COL_Veg_098','Block',{-113.204,12.598,94.941},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.618,3.618,11.596},false},
  {'COL_Veg_099','Block',{-112.861,11.727,4.803},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.075,3.075,9.855},false},
  {'COL_Veg_100','Block',{-85.382,13.244,-54.913},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.021,4.021,12.889},false},
  {'COL_Veg_101','Block',{64.558,11.495,-79.653},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.929,2.929,9.389},false},
  {'COL_Veg_102','Block',{19.782,12.35,89.953},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.463,3.463,11.1},false},
  {'COL_Veg_103','Block',{-50.983,12.191,-155.674},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.364,3.364,10.782},false},
  {'COL_Veg_104','Block',{90.143,12.713,99.348},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.69,3.69,11.826},false},
  {'COL_Veg_105','Block',{-90.881,12.039,45.877},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.269,3.269,10.478},false},
  {'COL_Veg_106','Block',{132.309,11.862,27.547},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.159,3.159,10.124},false},
  {'COL_Veg_107','Block',{70.175,13.146,3.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.96,3.96,12.691},false},
  {'COL_Veg_108','Block',{-137.537,12.643,-82.178},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.646,3.646,11.685},false},
  {'COL_Veg_109','Block',{-123.018,11.76,-7.784},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.095,3.095,9.921},false},
  {'COL_Veg_110','Block',{85.608,12.056,110.308},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.28,3.28,10.513},false},
  {'COL_Veg_111','Block',{-96.0,18.3,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.384,9.384,23.0},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'ForgeChimney',{0.0,12.0,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='AudioWorld: ambiente da forja'}},
  {'IGNIS_Anvil',{-0.9,7.0,-55.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='bigorna do golem'}},
  {'INTERACT_Ignis',{-0.9,13.79,-60.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['prompt_range']=18,['server_range']=22,['alvo']='belly (prompt do Main)'}},
  {'ISLE_Link',{0.0,6.0,222.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['kind']='ilha1'}},
  {'LETREIRO_Ignis',{-0.9,20.0,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='LetreiroIgnis'}},
  {'LETREIRO_Loja',{61.629,34.1,-28.738},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='LOJA DE MOCHILAS',['alcance']=170}},
  {'LETREIRO_Portal1',{-36.846,33.0,66.471},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='NARUTO',['alcance']=150}},
  {'LETREIRO_Portal2',{-61.093,33.0,45.207},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='DRAGON BALL',['alcance']=150}},
  {'LETREIRO_Portal3',{-74.339,33.0,15.801},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='SHADOW GARDEN',['alcance']=150}},
  {'LETREIRO_Portal4',{-74.199,33.0,-16.449},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='DEMON SLAYER',['alcance']=150}},
  {'LETREIRO_Portal5',{-60.696,33.0,-45.738},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ONE PIECE',['alcance']=150}},
  {'LETREIRO_Portal6',{-36.264,33.0,-66.79},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ONE PUNCH MAN',['alcance']=150}},
  {'LETREIRO_Ranking',{62.816,45.6,52.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='TABUAS DOS CAMPEOES',['alcance']=190}},
  {'NPC_Ignis',{-0.9,7.02,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['npc']='Ignis',['alvo']='workspace.NPCs.Ignis (Root)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'NPC_Vendedor',{76.583,8.2,-35.711},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{['kind']='npc',['olha']='porta'}},
  {'PLAYER_INTERACT_Ignis',{-0.9,7.02,-46.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'PLAYER_Loja',{71.146,8.2,-33.175},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{['kind']='padloja'}},
  {'PORTAL_DemonSlayer',{-77.518,19.4,-17.185},{0.216,0.0,-0.976},{-0.976,0.0,-0.216},{['destino']='DemonSlayer',['raio']=7.5,['touch']=true,['vm_portal']='DemonSlayer'}},
  {'PORTAL_DragonBall',{-63.826,19.4,47.229},{-0.595,0.0,-0.804},{-0.804,0.0,0.595},{['destino']='DragonBall',['raio']=7.5,['touch']=true,['vm_portal']='DragonBall'}},
  {'PORTAL_Naruto',{-38.494,19.4,69.445},{-0.875,0.0,-0.485},{-0.485,0.0,0.875},{['destino']='Naruto',['raio']=7.5,['touch']=true,['vm_portal']='Naruto'}},
  {'PORTAL_OnePiece',{-63.412,19.4,-47.784},{0.602,0.0,-0.799},{-0.799,0.0,-0.602},{['destino']='OnePiece',['raio']=7.5,['touch']=true,['vm_portal']='OnePiece'}},
  {'PORTAL_OnePunchMan',{-37.886,19.4,-69.778},{0.879,0.0,-0.477},{-0.477,0.0,-0.879},{['destino']='OnePunchMan',['raio']=7.5,['touch']=true,['vm_portal']='OnePunchMan'}},
  {'PORTAL_ShadowGarden',{-77.665,19.4,16.508},{-0.208,0.0,-0.978},{-0.978,0.0,0.208},{['destino']='ShadowGarden',['raio']=7.5,['touch']=true,['vm_portal']='ShadowGarden'}},
  {'SPAWN_Lobby',{0.0,10.1,64.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['kind']='spawn',['olha']='norte (forja)'}},
  {'TOP100_Origin',{67.412,7.6,56.565},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='LOBBY_FORJA.GlobalTop100 (OriginCF)',['nota']='quadros em z 0 e podios em z 9,5 do local',['face_x']=-0.766,['face_z']=-0.6428}},
  {'VFX_Anvil_Embers',{-3.5,53.0,-100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=10}},
  {'VFX_Anvil_Smoke',{-3.5,70.5,-118.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Brazier_AnvilE',{-70.0,17.0,-95.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_AnvilW',{70.0,17.0,-95.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Av_-1_1',{-12.2,10.8,128.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Av_-1_3',{-12.2,10.8,110.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Av_1_1',{12.2,10.8,128.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Av_1_3',{12.2,10.8,110.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Br_1_-1',{-6.4,10.35,163.667},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Br_1_1',{6.4,10.35,163.667},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Br_3_-1',{-6.4,10.017,187.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Br_3_1',{6.4,10.017,187.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Br_5_-1',{-6.4,9.683,210.333},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Br_5_1',{6.4,9.683,210.333},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_ForgeE',{17.5,10.8,-41.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_ForgeW',{-17.5,10.8,-41.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Gate_-1',{-12.5,11.2,141.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Gate_1',{12.5,11.2,141.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P1_-1',{-27.681,12.16,64.679},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P1_1',{-40.182,12.16,57.749},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P2_-1',{-52.01,12.16,47.376},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P2_1',{-60.512,12.16,35.886},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P3_-1',{-66.974,12.16,21.542},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P3_1',{-69.946,12.16,7.561},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P4_-1',{-69.877,12.16,-8.171},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P4_1',{-66.783,12.16,-22.126},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P5_-1',{-60.197,12.16,-36.413},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P5_1',{-51.595,12.16,-47.828},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P6_-1',{-39.677,12.16,-58.098},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P6_1',{-27.115,12.16,-64.918},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Rank_-1',{45.799,12.2,78.897},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Rank_1',{85.654,12.2,31.404},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Shop_-1',{62.351,11.0,-19.144},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Shop_1',{54.744,11.0,-35.458},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_-1_-1',{-14.9,14.3,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_-1_1',{14.9,14.3,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_1_-1',{-14.9,14.3,52.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_1_1',{14.9,14.3,52.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Dust_Forge',{0.0,15.0,-50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=3}},
  {'VFX_Dust_Plaza',{0.0,14.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=6}},
  {'VFX_Hammer_Embers',{112.0,7.4,-62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=3}},
  {'VFX_Hammer_Smoke',{106.0,7.8,-66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Hearth_Ember_C',{0.0,10.2,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=8}},
  {'VFX_Hearth_Fire_C',{0.0,8.6,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=16,['size']=3.4}},
  {'VFX_Leaves_ancient_11',{-96.0,35.32,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=16.56}},
  {'VFX_Leaves_oak1_10',{70.175,21.106,3.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=8.306999486138336}},
  {'VFX_Leaves_oak1_6',{137.74,18.649,-12.11},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.880186655912406}},
  {'VFX_Leaves_oak1_7',{37.488,17.615,-43.947},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.2794223348423825}},
  {'VFX_Leaves_oak1_8',{-102.735,19.949,97.251},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.635086295546843}},
  {'VFX_Leaves_oak1_9',{64.558,17.384,-79.653},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.1455746942813505}},
  {'VFX_Leaves_oak2_0',{38.965,17.48,84.995},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.201298808257201}},
  {'VFX_Leaves_oak2_1',{-55.389,17.799,99.483},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.386476281928049}},
  {'VFX_Leaves_oak2_2',{46.207,19.165,114.419},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.179455678546194}},
  {'VFX_Leaves_oak3_5',{102.065,21.028,58.252},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=8.261346817904585}},
  {'VFX_Leaves_oakG_3',{-17.841,19.278,100.522},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.24527281514135}},
  {'VFX_Leaves_oakG_4',{19.79,19.034,120.248},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.103628585150027}},
  {'VFX_Rune_Portal1',{-34.421,8.6,62.098},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal2',{-57.074,8.6,42.232},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal3',{-69.448,8.6,14.762},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal4',{-69.317,8.6,-15.367},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal5',{-56.703,8.6,-42.729},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal6',{-33.878,8.6,-62.396},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Spawn',{0.0,10.6,64.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=3}},
  {'VFX_Sparkle_Crystal_0',{66.0,10.8,-96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparkle',['rate']=3}},
  {'VFX_Sparkle_Crystal_1',{-70.0,10.4,-96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparkle',['rate']=3}},
  {'VFX_Sparkle_Crystal_2',{128.0,10.0,-8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparkle',['rate']=3}},
  {'VFX_Sparkle_Crystal_3',{-132.0,10.0,70.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparkle',['rate']=3}},
  {'VFX_Sparkle_Crystal_4',{96.0,9.6,110.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparkle',['rate']=3}},
  {'VFX_Sparkle_Crystal_5',{-40.0,10.4,-150.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparkle',['rate']=3}},
}
MKF:ClearAllChildren()
for _, m in ipairs(MK) do
  local p = Instance.new('Part'); p.Name = m[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false
  p.CanTouch = false; p.CastShadow = false; p.Transparency = 1; p.Size = Vector3.new(1,1,1); p.CFrame = cf(m[2], m[3], m[4])
  for k, v in pairs(m[5]) do p:SetAttribute(k, v) end
  p.Parent = MKF
end
-- luzes: {nome, tipo, pos, cor, alcance, brilho, sombra, noturna, direcao(spot), angulo(spot)}
-- noturna = Enabled false + atributo NightOnly (o ciclo dia/noite liga: for _, l in LIGHTS:GetDescendants() ...)
local LT = {
  {'L_P_DemonSlayer_Lamp_1','POINT',{-69.315,11.44,-11.218},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Lamp_2','POINT',{-67.562,11.44,-19.126},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Pad','POINT',{-71.27,12.7,-15.8},{255,129,129},12.6,0.71,false,false},
  {'L_P_DragonBall_Pad','POINT',{-58.682,12.7,43.422},{97,179,255},12.6,0.71,false,false},
  {'L_P_Naruto_Pad','POINT',{-35.391,12.7,63.847},{255,196,118},12.6,0.71,false,false},
  {'L_P_OnePiece_Pad','POINT',{-58.3,12.7,-43.932},{137,196,255},12.6,0.71,false,false},
  {'L_P_OnePunchMan_Pad','POINT',{-34.833,12.7,-64.154},{255,229,144},12.6,0.71,false,false},
  {'L_P_ShadowGarden_Candles','POINT',{-70.048,18.41,26.851},{203,137,255},9.5,0.49,false,false},
  {'L_P_ShadowGarden_Moon','POINT',{-75.184,31.02,15.674},{196,129,255},10.7,0.56,false,false},
  {'L_P_ShadowGarden_Pad','POINT',{-71.405,12.7,15.178},{206,137,255},12.6,0.71,false,false},
  {'L_Portal_DemonSlayer','POINT',{-75.175,19.4,-16.666},{255,129,129},14.0,1.0,false,false},
  {'L_Portal_DragonBall','POINT',{-61.897,19.4,45.801},{97,179,255},14.0,1.0,false,false},
  {'L_Portal_Naruto','POINT',{-37.33,19.4,67.346},{255,196,118},14.0,1.0,false,false},
  {'L_Portal_OnePiece','POINT',{-61.495,19.4,-46.34},{137,196,255},14.0,1.0,false,false},
  {'L_Portal_OnePunchMan','POINT',{-36.741,19.4,-67.669},{255,229,144},14.0,1.0,false,false},
  {'L_Portal_ShadowGarden','POINT',{-75.317,19.4,16.009},{206,137,255},14.0,1.0,false,false},
  {'L_SN_AnvilCrack','POINT',{-3.5,51.0,-99.0},{255,120,40},40.0,2.2,false,false},
  {'L_SN_Brazier_AnvilE','POINT',{-70.0,17.6,-95.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_AnvilW','POINT',{70.0,17.6,-95.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Av_-1_1','POINT',{-12.2,11.4,128.5},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Av_-1_3','POINT',{-12.2,11.4,110.5},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Av_1_1','POINT',{12.2,11.4,128.5},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Av_1_3','POINT',{12.2,11.4,110.5},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Br_1_-1','POINT',{-6.4,10.95,163.667},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Br_1_1','POINT',{6.4,10.95,163.667},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Br_3_-1','POINT',{-6.4,10.617,187.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Br_3_1','POINT',{6.4,10.617,187.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Br_5_-1','POINT',{-6.4,10.283,210.333},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Br_5_1','POINT',{6.4,10.283,210.333},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_ForgeE','POINT',{17.5,11.4,-41.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_ForgeW','POINT',{-17.5,11.4,-41.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Gate_-1','POINT',{-12.5,11.8,141.8},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Gate_1','POINT',{12.5,11.8,141.8},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P1_-1','POINT',{-27.681,12.76,64.679},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P1_1','POINT',{-40.182,12.76,57.749},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P2_-1','POINT',{-52.01,12.76,47.376},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P2_1','POINT',{-60.512,12.76,35.886},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P3_-1','POINT',{-66.974,12.76,21.542},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P3_1','POINT',{-69.946,12.76,7.561},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P4_-1','POINT',{-69.877,12.76,-8.171},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P4_1','POINT',{-66.783,12.76,-22.126},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P5_-1','POINT',{-60.197,12.76,-36.413},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P5_1','POINT',{-51.595,12.76,-47.828},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P6_-1','POINT',{-39.677,12.76,-58.098},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P6_1','POINT',{-27.115,12.76,-64.918},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Rank_-1','POINT',{45.799,12.8,78.897},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Rank_1','POINT',{85.654,12.8,31.404},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Shop_-1','POINT',{62.351,11.6,-19.144},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Shop_1','POINT',{54.744,11.6,-35.458},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Stair_-1_-1','POINT',{-14.9,14.9,80.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Stair_-1_1','POINT',{14.9,14.9,80.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Stair_1_-1','POINT',{-14.9,14.9,52.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Stair_1_1','POINT',{14.9,14.9,52.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Crystal_0','POINT',{66.0,12.6,-96.0},{255,170,80},14.0,1.0,false,false},
  {'L_SN_Crystal_1','POINT',{-70.0,12.0,-96.0},{255,170,80},14.0,1.0,false,false},
  {'L_SN_Crystal_2','POINT',{128.0,11.4,-8.0},{255,170,80},14.0,1.0,false,false},
  {'L_SN_Crystal_3','POINT',{-132.0,11.4,70.0},{255,170,80},14.0,1.0,false,false},
  {'L_SN_Crystal_4','POINT',{96.0,10.8,110.0},{255,170,80},14.0,1.0,false,false},
  {'L_SN_Crystal_5','POINT',{-40.0,12.0,-150.0},{255,170,80},14.0,1.0,false,false},
  {'L_SN_Hearth','POINT',{0.0,12.0,-72.0},{255,128,46},28.0,2.4,true,false},
  {'L_SN_ShopCounter','POINT',{73.612,12.55,-38.297},{255,200,130},16.0,0.9,false,false},
  {'L_SN_ShopLamp_-5','POINT',{75.071,18.65,-29.489},{255,200,130},16.0,0.9,false,false},
  {'L_SN_ShopLamp_5','POINT',{70.845,18.65,-38.552},{255,200,130},16.0,0.9,false,false},
  {'L_SN_ShopLegend','POINT',{74.055,15.2,-44.683},{140,190,255},12.0,1.2,false,false},
}
LTF:ClearAllChildren()
local nDia = 0
for _, l in ipairs(LT) do
  local a = Instance.new('Part'); a.Name = l[1]; a.Anchored = true; a.CanCollide = false; a.CanQuery = false
  a.CanTouch = false; a.CastShadow = false; a.Transparency = 1; a.Size = Vector3.new(0.5,0.5,0.5)
  local pos = Vector3.new(l[3][1], l[3][2], l[3][3]) + ROOT_OFFSET
  if l[2] == 'SPOT' and l[9] then a.CFrame = CFrame.lookAt(pos, pos + Vector3.new(l[9][1], l[9][2], l[9][3])) else a.CFrame = CFrame.new(pos) end
  local pl = Instance.new(l[2] == 'SPOT' and 'SpotLight' or 'PointLight')
  pl.Color = Color3.fromRGB(l[4][1], l[4][2], l[4][3]); pl.Range = l[5]; pl.Brightness = l[6]; pl.Shadows = l[7]
  pl.Enabled = not l[8]; if l[8] then a:SetAttribute('NightOnly', true); pl:SetAttribute('NightOnly', true) else nDia += 1 end
  if l[2] == 'SPOT' then pl.Face = Enum.NormalId.Front; if l[10] then pl.Angle = l[10] end end
  pl.Parent = a; a.Parent = LTF
end
-- rede de seguranca: quem cai do lobby volta ao ponto seguro mais proximo (spawn, RESPAWN_*, pes de escada)
local SAFE = {
  {'SPAWN_Lobby',{0.0,10.1,64.0}},
  {'SAFE_Spawn',{0.0,10.0,64.0}},
  {'SAFE_Praca',{0.0,7.0,0.0}},
  {'SAFE_PracaN',{0.0,7.0,-30.0}},
  {'SAFE_Forja',{-0.9,7.02,-44.0}},
  {'SAFE_Loja',{71.146,8.2,-33.175}},
  {'SAFE_Tabuas',{55.922,7.6,46.923}},
  {'SAFE_Avenida',{0.0,7.0,110.0}},
  {'SAFE_Portao',{0.0,7.0,150.0}},
  {'SAFE_Ponte1',{0.0,6.583,185.0}},
  {'SAFE_Ponte2',{0.0,6.083,215.0}},
  {'SAFE_Portal1',{-32.967,8.6,59.474}},
  {'SAFE_Portal2',{-54.662,9.1,40.448}},
  {'SAFE_Portal3',{-66.514,8.2,14.138}},
  {'SAFE_Portal4',{-66.388,8.65,-14.718}},
  {'SAFE_Portal5',{-54.307,8.8,-40.923}},
  {'SAFE_Portal6',{-32.447,8.7,-59.76}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(360,4,420); v.Position = Vector3.new(0.0,-25.0,29.0) + ROOT_OFFSET
  v:ClearAllChildren()
  for _, s in ipairs(SAFE) do local at = Instance.new('Attachment'); at.Name = s[1]; at.Parent = v
    at.WorldPosition = Vector3.new(s[2][1], s[2][2], s[2][3]) + ROOT_OFFSET end
  v.Parent = root end

-- Script de servidor: personagens no grupo 'Personagens' (atravessam as cascas SoVisual) + rede de quedas
do
  local SSS = game:GetService('ServerScriptService')
  local s = SSS:FindFirstChild('LOBBY_FORJA_Servidor') or Instance.new('Script')
  s.Name = 'LOBBY_FORJA_Servidor'
  s.Source = [==[
-- gerado por montar_lobby_santuario.lua (export_roblox.py) - nao editar a mao
local Players = game:GetService('Players')
local PhysicsService = game:GetService('PhysicsService')
local RunService = game:GetService('RunService')
pcall(function()
  for _, n in ipairs({'SoVisual', 'Personagens'}) do
    if not PhysicsService:IsCollisionGroupRegistered(n) then PhysicsService:RegisterCollisionGroup(n) end
  end
  PhysicsService:CollisionGroupSetCollidable('SoVisual', 'Personagens', false)
end)
local function grupo(inst) if inst:IsA('BasePart') then inst.CollisionGroup = 'Personagens' end end
local chao = setmetatable({}, {__mode = 'k'})   -- personagem -> Y do ultimo chao pisado
local function personagem(ch)
  for _, d in ipairs(ch:GetDescendants()) do grupo(d) end
  ch.DescendantAdded:Connect(grupo)
end
local function jogador(p)
  p.CharacterAdded:Connect(personagem)
  if p.Character then personagem(p.Character) end
end
Players.PlayerAdded:Connect(jogador)
for _, p in ipairs(Players:GetPlayers()) do jogador(p) end
-- rede de seguranca
local root = workspace:WaitForChild('LOBBY_FORJA', 60)
local catch = root and root:WaitForChild('VOID_CATCH', 60)
if not catch then return end
local seguros = {}
for _, a in ipairs(catch:GetChildren()) do if a:IsA('Attachment') then table.insert(seguros, a.WorldPosition) end end
local topo = catch.Position.Y + catch.Size.Y / 2
local ult = setmetatable({}, {__mode = 'k'})
local function dentro(p)
  local c, s = catch.Position, catch.Size
  return math.abs(p.X - c.X) <= s.X / 2 and math.abs(p.Z - c.Z) <= s.Z / 2
end
local function resgatar(ch)
  local hrp = ch:FindFirstChild('HumanoidRootPart'); if not hrp then return end
  local p = hrp.Position
  -- so quem caiu DO LOBBY (ultimo chao acima da rede): nao mexe em quem anda em areas mais baixas
  if not (chao[ch] and chao[ch] > topo + 8) or p.Y > topo or not dentro(p) then return end
  if ult[ch] and os.clock() - ult[ch] < 1 then return end
  ult[ch] = os.clock()
  local best, bd = nil, math.huge
  for _, s in ipairs(seguros) do
    local d = (Vector3.new(s.X, 0, s.Z) - Vector3.new(p.X, 0, p.Z)).Magnitude
    if d < bd then best, bd = s, d end
  end
  if not best then return end
  hrp.AssemblyLinearVelocity = Vector3.zero
  ch:PivotTo(CFrame.new(best + Vector3.new(0, 3.5, 0)) * (hrp.CFrame - hrp.CFrame.Position))
  chao[ch] = best.Y
end
catch.Touched:Connect(function(hit)
  local ch = hit.Parent
  if ch and ch:FindFirstChildOfClass('Humanoid') then resgatar(ch) end
end)
local acc = 0
RunService.Heartbeat:Connect(function(dt)
  acc += dt
  if acc < 0.2 then return end
  acc = 0
  for _, pl in ipairs(Players:GetPlayers()) do
    local ch = pl.Character
    local hum = ch and ch:FindFirstChildOfClass('Humanoid')
    local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
    if hum and hrp then
      if hum.FloorMaterial ~= Enum.Material.Air then chao[ch] = hrp.Position.Y end
      if hrp.Position.Y < topo then resgatar(ch) end
    end
  end
end)
]==]
  s.Parent = SSS
end

if APLICAR_LIGHTING then
  local Lg = game:GetService('Lighting')
  Lg.Brightness = 2.8
  Lg.ExposureCompensation = 0.0
  Lg.EnvironmentDiffuseScale = 0.6
  Lg.EnvironmentSpecularScale = 0.3
  Lg.ShadowSoftness = 0.35
  Lg.Ambient = Color3.fromRGB(118,112,106)
  Lg.OutdoorAmbient = Color3.fromRGB(160,158,152)
  Lg.ColorShift_Top = Color3.fromRGB(255,236,206)
  Lg.ColorShift_Bottom = Color3.fromRGB(36,32,30)
  Lg.ClockTime = 8.562
  Lg.GeographicLatitude = -7.973
  do local e = Lg:FindFirstChildOfClass('Atmosphere') or Instance.new('Atmosphere', Lg)
    e.Density = 0.28
    e.Offset = 0.2
    e.Color = Color3.fromRGB(206,214,228)
    e.Decay = Color3.fromRGB(150,166,200)
    e.Glare = 0.2
    e.Haze = 1.2
  end
  do local e = Lg:FindFirstChildOfClass('Sky') or Instance.new('Sky', Lg)
    e.SunAngularSize = 15
    e.MoonAngularSize = 11
    e.StarCount = 0
  end
  do local e = Lg:FindFirstChildOfClass('BloomEffect') or Instance.new('BloomEffect', Lg)
    e.Intensity = 0.38
    e.Size = 26
    e.Threshold = 1.25
  end
  do local e = Lg:FindFirstChildOfClass('SunRaysEffect') or Instance.new('SunRaysEffect', Lg)
    e.Intensity = 0.06
    e.Spread = 0.25
  end
  do local e = Lg:FindFirstChildOfClass('ColorCorrectionEffect') or Instance.new('ColorCorrectionEffect', Lg)
    e.Brightness = 0.02
    e.Contrast = 0.09
    e.Saturation = 0.14
    e.TintColor = Color3.fromRGB(255,248,236)
  end
  local d = Lg:GetSunDirection()
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (0.67, 0.53, -0.52) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
-- ================= CONTRATO DO JOGO (lobby Santuario do Deus-Ferreiro) =================
-- Santuario.Portal1..6: Model com Disco (gameplay, invisivel, sem colisao, CanTouch) e atributo AreaId; o Core.Main
-- liga o Touched (Santuario precisa ser filho DIRETO de LOBBY_FORJA). O AudioWorld reconhece Portal%d em Santuario.
local PORTAIS = {
  {1, 'Naruto', 1, Vector3.new(-37.864, 19.400, 68.308), Vector3.new(0.4848, 0, -0.8746)},
  {2, 'DragonBall', 2, Vector3.new(-62.781, 19.400, 46.456), Vector3.new(0.8039, 0, -0.5948)},
  {3, 'ShadowGarden', 3, Vector3.new(-76.393, 19.400, 16.238), Vector3.new(0.9781, 0, -0.2079)},
  {4, 'DemonSlayer', 4, Vector3.new(-76.249, 19.400, -16.904), Vector3.new(0.9763, 0, 0.2164)},
  {5, 'OnePiece', 5, Vector3.new(-62.373, 19.400, -47.002), Vector3.new(0.7986, 0, 0.6018)},
  {6, 'OnePunchMan', 6, Vector3.new(-37.266, 19.400, -68.636), Vector3.new(0.4772, 0, 0.8788)},
}
do
  local san = root:FindFirstChild('Santuario') or Instance.new('Folder'); san.Name = 'Santuario'; san.Parent = root
  for _, c in ipairs(san:GetChildren()) do if string.match(c.Name, '^Portal%d$') or c.Name == 'PortalKonoha' then c:Destroy() end end
  for _, p in ipairs(PORTAIS) do
    local m = Instance.new('Model'); m.Name = 'Portal' .. p[1]; m:SetAttribute('Tema', p[2])
    local d = Instance.new('Part'); d.Name = 'Disco'; d.Anchored = true; d.CanCollide = false; d.CanQuery = false
    d.CanTouch = true; d.CastShadow = false; d.Transparency = 1; d.Size = Vector3.new(14, 15, 1.2)
    local pos = p[4] + ROOT_OFFSET; d.CFrame = CFrame.lookAt(pos, pos + p[5]); d:SetAttribute('AreaId', p[3])
    d.Parent = m; m.PrimaryPart = d; m.Parent = san
  end
end
do local r = root:FindFirstChild('LobbyRevision') or Instance.new('Folder'); r.Name = 'LobbyRevision'
  r:SetAttribute('Santuario', EXPORT_ID); r.Parent = root end
-- GlobalTop100 (quadros Forca/Moedas): a GEOMETRIA e do Top100Builder/Controller; aqui so a ORIGEM nova (Tabuas
-- dos Campeoes, sudeste da praca). Se o modelo ja existe dentro do LOBBY_FORJA, e levado inteiro para la (PivotTo).
local TOP100_CF = CFrame.lookAt(Vector3.new(67.412, 7.600, 56.565), Vector3.new(66.646, 7.600, 55.922)) * CFrame.Angles(0, math.pi, 0)
root:SetAttribute('Top100Origin', TOP100_CF + ROOT_OFFSET)
do local t = root:FindFirstChild('GlobalTop100')
  if t and t:IsA('Model') then t:PivotTo(TOP100_CF + ROOT_OFFSET); print('GlobalTop100 levado as Tabuas dos Campeoes')
  else print('GlobalTop100 ausente: construa com Top100Builder.Build(root, {OriginCF = root:GetAttribute("Top100Origin")})') end end
-- POSICOES DO JOGO (POSICIONAR_JOGO = true move os objetos soltos; o Core.LobbyLayout e trocado a mao/MCP):
--   LobbyLayout.Spawn        = Vector3.new(0.0, 13.3, 64.0)
--   LobbyLayout.Shop         = Vector3.new(71.146, 11.7, -33.175)
--   LobbyLayout.ShopFacing   = Vector3.new(76.583, 11.7, -35.711)
--   LobbyLayout.Ignis        = Vector3.new(-0.9, 10.5, -46.0)
--   LobbyLayout.PortalIsland = Vector3.new(-51.968, 10.5, -1.815)
local POSICIONAR_JOGO = true
if POSICIONAR_JOGO then
  local function mv(inst, cf, what) if inst then pcall(function() if inst:IsA('Model') then inst:PivotTo(cf) else inst.CFrame = cf end end); print('posicionado', what) else print('NAO achei', what) end end
  local msp = workspace:FindFirstChild('Mystical Spawn Point'); mv(msp and msp:FindFirstChild('SpawnLobby'), CFrame.new(0.0, 10.1, 64.0) * CFrame.Angles(0, 0, 0) + ROOT_OFFSET, 'SpawnLobby')
  mv(workspace:FindFirstChild('MailBox'), CFrame.new(-13.0, 10.4, 62.0) * CFrame.Angles(0, -math.pi / 2, 0) + ROOT_OFFSET, 'MailBox')
  local lm = workspace:FindFirstChild('LojaMochilas'); mv(lm and lm:FindFirstChild('PadLoja'), CFrame.new(71.146, 8.299999999999999, -33.175) + ROOT_OFFSET, 'PadLoja')
  local npcs = workspace:FindFirstChild('NPCs'); local v = npcs and npcs:FindFirstChild('npc vendedor ')
  mv(v, CFrame.new(76.583, 11.2, -35.711) * CFrame.Angles(0, 2.0071, 0) + ROOT_OFFSET, 'npc vendedor ')
end
print(string.format('CONTRATO: Santuario com %d portais, LobbyRevision %s', #PORTAIS, EXPORT_ID))

-- ================= VFX (era medieval): particulas nos marcadores VFX_* (atributo 'particle') =================
do
  local VF = root:FindFirstChild('VFX') or Instance.new('Folder'); VF.Name = 'VFX'; VF.Parent = root
  VF:ClearAllChildren()
  local SMOKE = 'rbxasset://textures/particles/smoke_main.dds'
  local FIRE = 'rbxasset://textures/particles/fire_main.dds'
  local SPARK = 'rbxasset://textures/particles/sparkles_main.dds'
  local function ns(a, b) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(1, b)}) end
  local function ns3(a, m, b, tm) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(tm or 0.5, m), NumberSequenceKeypoint.new(1, b)}) end
  local function cs(a, b) return ColorSequence.new(a, b) end
  local KIND = {
    smoke_heavy = function(pe, size)
      pe.Texture = SMOKE; pe.Rate = 7; pe.Lifetime = NumberRange.new(4.5, 7); pe.Speed = NumberRange.new(6, 9)
      pe.Size = ns(3.0, 11.0); pe.Transparency = ns3(0.35, 0.6, 1.0, 0.6); pe.Color = cs(Color3.fromRGB(96, 92, 90), Color3.fromRGB(200, 196, 192))
      pe.Acceleration = Vector3.new(2.5, 1.5, -1.0); pe.SpreadAngle = Vector2.new(12, 12); pe.Rotation = NumberRange.new(0, 360)
      pe.RotSpeed = NumberRange.new(-20, 20); pe.Drag = 0.6; pe.LightInfluence = 1
    end,
    smoke_thin = function(pe, size)
      pe.Texture = SMOKE; pe.Rate = 2; pe.Lifetime = NumberRange.new(4, 6); pe.Speed = NumberRange.new(3, 5)
      pe.Size = ns(1.2, 5.0); pe.Transparency = ns3(0.5, 0.7, 1.0, 0.6); pe.Color = cs(Color3.fromRGB(150, 146, 144), Color3.fromRGB(220, 218, 216))
      pe.Acceleration = Vector3.new(2.0, 1.0, -0.8); pe.SpreadAngle = Vector2.new(10, 10); pe.Rotation = NumberRange.new(0, 360)
      pe.RotSpeed = NumberRange.new(-15, 15); pe.Drag = 0.6; pe.LightInfluence = 1
    end,
    fire = function(pe, size)
      size = size or 3.0
      pe.Texture = FIRE; pe.Rate = 16; pe.Lifetime = NumberRange.new(0.55, 0.95); pe.Speed = NumberRange.new(3, 5.5)
      pe.Size = ns3(size * 0.55, size, size * 0.2, 0.4); pe.Transparency = ns3(0.1, 0.25, 1.0, 0.6)
      pe.Color = cs(Color3.fromRGB(255, 228, 120), Color3.fromRGB(255, 96, 20)); pe.LightEmission = 1; pe.LightInfluence = 0
      pe.SpreadAngle = Vector2.new(18, 18); pe.Acceleration = Vector3.new(0, 6, 0); pe.Rotation = NumberRange.new(-30, 30)
      pe.RotSpeed = NumberRange.new(-40, 40); pe.Drag = 1.0; pe.ZOffset = 0.5
    end,
    ember = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 5; pe.Lifetime = NumberRange.new(1.2, 2.4); pe.Speed = NumberRange.new(5, 9)
      pe.Size = ns(0.35, 0.05); pe.Transparency = ns(0.0, 1.0); pe.Color = cs(Color3.fromRGB(255, 190, 90), Color3.fromRGB(255, 80, 20))
      pe.LightEmission = 1; pe.LightInfluence = 0; pe.SpreadAngle = Vector2.new(35, 35); pe.Acceleration = Vector3.new(0.5, -3, 0)
      pe.Drag = 1.5; pe.VelocityInheritance = 0
    end,
    water = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 24; pe.Lifetime = NumberRange.new(0.8, 1.2); pe.Speed = NumberRange.new(7, 10)
      pe.Size = ns(0.7, 0.2); pe.Transparency = ns(0.2, 1.0); pe.Color = cs(Color3.fromRGB(220, 240, 255), Color3.fromRGB(150, 200, 240))
      pe.LightEmission = 0.3; pe.SpreadAngle = Vector2.new(14, 14); pe.Acceleration = Vector3.new(0, -24, 0); pe.Drag = 0
    end,
    leaves = function(pe, size)
      pe.Texture = SMOKE; pe.Rate = 0.6; pe.Lifetime = NumberRange.new(4, 7); pe.Speed = NumberRange.new(0.5, 1.5)
      pe.Size = ns(0.55, 0.45); pe.Transparency = ns3(0.3, 0.3, 1.0, 0.85); pe.Color = cs(Color3.fromRGB(120, 170, 60), Color3.fromRGB(190, 150, 60))
      pe.SpreadAngle = Vector2.new(60, 60); pe.Acceleration = Vector3.new(1.2, -1.6, 0.6); pe.Drag = 0.8
      pe.Rotation = NumberRange.new(0, 360); pe.RotSpeed = NumberRange.new(-90, 90); pe.Shape = Enum.ParticleEmitterShape.Sphere
    end,
    rune = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 2; pe.Lifetime = NumberRange.new(2.5, 4); pe.Speed = NumberRange.new(0.6, 1.4)
      pe.Size = ns(0.25, 0.05); pe.Transparency = ns3(0.2, 0.3, 1.0, 0.6); pe.Color = cs(Color3.fromRGB(255, 226, 140), Color3.fromRGB(255, 180, 70))
      pe.LightEmission = 1; pe.LightInfluence = 0; pe.SpreadAngle = Vector2.new(25, 25); pe.Acceleration = Vector3.new(0, 1.2, 0)
      pe.Shape = Enum.ParticleEmitterShape.Box; pe.Drag = 0.4
    end,
    sparkle = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 3; pe.Lifetime = NumberRange.new(1.0, 1.8); pe.Speed = NumberRange.new(0.2, 0.5)
      pe.Size = ns3(0.05, 0.4, 0.05, 0.5); pe.Transparency = ns(0.1, 1.0); pe.Color = cs(Color3.fromRGB(200, 230, 255), Color3.fromRGB(140, 190, 255))
      pe.LightEmission = 1; pe.LightInfluence = 0; pe.SpreadAngle = Vector2.new(180, 180); pe.Shape = Enum.ParticleEmitterShape.Box
    end,
    dust = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 3; pe.Lifetime = NumberRange.new(4, 7); pe.Speed = NumberRange.new(0.2, 0.6)
      pe.Size = ns(0.12, 0.08); pe.Transparency = ns3(1.0, 0.55, 1.0, 0.5); pe.Color = cs(Color3.fromRGB(255, 220, 170), Color3.fromRGB(255, 200, 140))
      pe.LightEmission = 0.6; pe.SpreadAngle = Vector2.new(180, 180); pe.Shape = Enum.ParticleEmitterShape.Box; pe.Drag = 0.2
    end,
  }
  local n = 0
  for _, mk in ipairs(MKF:GetChildren()) do
    local kind = mk:GetAttribute('particle')
    if kind and KIND[kind] then
      local host = Instance.new('Part'); host.Name = mk.Name; host.Anchored = true; host.CanCollide = false; host.CanQuery = false
      host.CanTouch = false; host.CastShadow = false; host.Transparency = 1
      host.Size = (kind == 'leaves') and Vector3.new(10, 6, 10) or ((kind == 'dust') and Vector3.new(60, 16, 60) or (((kind == 'rune') or (kind == 'sparkle')) and Vector3.new(6, 2, 6) or Vector3.new(2, 1, 2)))
      host.CFrame = mk.CFrame
      local pe = Instance.new('ParticleEmitter'); KIND[kind](pe, mk:GetAttribute('size'))
      local rate = mk:GetAttribute('rate'); if rate then pe.Rate = rate end
      if kind == 'leaves' then local r = mk:GetAttribute('radius'); if r then host.Size = Vector3.new(r * 2, r, r * 2) end end
      pe.Parent = host; host.Parent = VF; n += 1
    end
  end
  print(string.format('VFX Santuario: %d emissores', n))
  -- tremor das luzes de fogo (fornalhas, forno, braseiros): LocalScript em StarterPlayerScripts
  local SP = game:GetService('StarterPlayer'):WaitForChild('StarterPlayerScripts')
  local old = SP:FindFirstChild('VFX_Santuario_Client'); if old then old:Destroy() end
  local ls = Instance.new('LocalScript'); ls.Name = 'VFX_Santuario_Client'
  ls.Source = [==[
local RS = game:GetService('RunService')
local root = workspace:WaitForChild('LOBBY_FORJA', 30); if not root then return end
local LT = root:WaitForChild('LIGHTS', 30); if not LT then return end
local fires = {}
for _, p in ipairs(LT:GetChildren()) do
  local n = p.Name
  if string.find(n, '^L_SN_Hearth') or string.find(n, '^L_SN_AnvilCrack') or string.find(n, '^L_SN_Brazier_') then
    local l = p:FindFirstChildOfClass('PointLight')
    if l then table.insert(fires, {l = l, b = l.Brightness, r = l.Range, ph = math.random() * 6.28}) end
  end
end
if #fires == 0 then return end
local t = 0
RS.RenderStepped:Connect(function(dt)
  t += dt
  for _, f in ipairs(fires) do
    local k = 1 + 0.10 * math.sin(t * 9.1 + f.ph) + 0.06 * math.sin(t * 23.7 + f.ph * 1.7) + 0.04 * math.noise(t * 4, f.ph)
    f.l.Brightness = f.b * k
    f.l.Range = f.r * (1 + 0.04 * math.sin(t * 7.3 + f.ph))
  end
end)
]==]
  ls.Parent = SP
end


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


print(string.format('LOBBY_FORJA montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
