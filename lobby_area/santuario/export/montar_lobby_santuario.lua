-- montar_lobby_santuario.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID c4718331
-- 1) Importe os FBX LOBBY_SN_*_c47183.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador
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
local EXPORT_ID = 'c4718331'
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
  ['snb_hall'] = '',  -- textures/SNB_Hall.png (1.0 studs por repeticao)
  ['snb_hammer_1'] = '',  -- textures/SNB_Hammer_1.png (1.0 studs por repeticao)
  ['snb_hammer_2'] = '',  -- textures/SNB_Hammer_2.png (1.0 studs por repeticao)
  ['snb_isle'] = '',  -- textures/SNB_Isle.png (1.0 studs por repeticao)
  ['snb_islebridge'] = '',  -- textures/SNB_IsleBridge.png (1.0 studs por repeticao)
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
  ['SNB_Hall'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hall', w = nil},
  ['SNB_Hammer_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hammer_1', w = nil},
  ['SNB_Hammer_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hammer_2', w = nil},
  ['SNB_Isle'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_isle', w = nil},
  ['SNB_IsleBridge'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_islebridge', w = nil},
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
  ['SN_RuneAmber'] = {c = Color3.fromRGB(255,176,70), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_RuneBlue'] = {c = Color3.fromRGB(90,170,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_RuneOrange'] = {c = Color3.fromRGB(255,130,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_RuneRed'] = {c = Color3.fromRGB(255,76,64), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_RuneViolet'] = {c = Color3.fromRGB(190,120,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_RuneYellow'] = {c = Color3.fromRGB(255,222,90), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
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
local FBX = {[1]='LOBBY_SN_02_TERRAIN_c47183.fbx', [2]='LOBBY_SN_03_TOWN_c47183.fbx', [3]='LOBBY_SN_04_FORGE_c47183.fbx', [4]='LOBBY_SN_05_SERVICES_c47183.fbx', [5]='LOBBY_SN_06_PORTALS_c47183.fbx', [6]='LOBBY_SN_07_EXIT_c47183.fbx', [7]='LOBBY_SN_09_VEGETATION_c47183.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['WB_Bg_Forest__SN_PineFar']={505.936,65.895,316.882,802.355,128.235,655.164,1,false,'SN_PineFar','k',''},
  ['WB_Bg_Forest_01__SN_PineFarDark']={505.962,59.305,316.836,805.927,124.964,657.698,1,false,'SN_PineFarDark','k',''},
  ['WB_Bg_Forest_02__SN_PineFarLight']={505.907,71.009,316.934,798.187,129.971,652.207,1,false,'SN_PineFarLight','k',''},
  ['WB_Bg_Relief_0__SN_Hills']={651.643,54.259,300.718,721.51,116.118,609.997,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_0_01__SN_Mountain']={1021.198,136.993,527.514,958.53,206.037,1065.523,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_1__SN_Hills']={302.588,52.655,618.202,610.148,112.91,658.39,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_1_01__SN_Mountain']={527.101,146.213,1053.435,1062.813,201.392,895.439,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_2__SN_Hills']={-309.841,53.061,606.393,627.594,113.722,635.763,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_2_01__SN_Mountain']={-526.862,144.274,1007.146,1062.549,218.847,983.434,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_3__SN_Hills']={-866.908,53.163,310.856,1153.147,113.927,624.708,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_3_01__SN_Mountain']={-1008.42,142.758,526.762,980.381,217.988,1063.027,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_4__SN_Hills']={-527.439,38.952,-255.926,478.276,85.504,518.199,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_4_01__SN_Mountain']={-1008.139,208.022,-530.489,985.438,339.272,1072.125,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_5__SN_Hills']={-256.391,27.837,-510.121,518.058,63.274,440.131,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_5_01__SN_Mountain']={-529.722,262.733,-1006.825,1067.165,445.124,983.598,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_6__SN_Hills']={258.795,44.211,-510.034,520.033,96.022,440.599,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_6_01__SN_Mountain']={528.256,259.906,-1007.829,1069.732,450.777,986.244,1,false,'SN_Mountain','k',''},
  ['WB_Bg_Relief_7__SN_Hills']={650.827,51.44,-255.952,720.761,110.481,517.509,1,false,'SN_Hills','k',''},
  ['WB_Bg_Relief_7_01__SN_Mountain']={1008.366,225.969,-528.024,979.109,385.916,1065.159,1,false,'SN_Mountain','k',''},
  ['WB_Ter_Ground__SNB_Ground_1']={-167.466,6.961,8.7,258.468,0.343,128.0,1,true,'SNB_Ground_1','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g15_15']={-65.0,6.871,64.2,130.0,0.653,132.24,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g15_16']={-15.786,6.968,-41.467,268.429,0.486,245.067,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g16_15']={22.816,7.013,74.04,214.102,0.776,151.92,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g16_16']={74.0,6.98,-23.324,152.0,0.481,208.781,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_02__SNB_Ground_3']={54.247,6.891,-3.441,60.833,0.061,102.068,1,true,'SNB_Ground_3','',''},
  ['WB_Ter_Shore__SNB_Shore_g14_15']={-191.392,3.6,48.783,129.539,6.4,104.117,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g14_16']={-195.352,3.6,0.013,216.116,6.4,258.746,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g15_14']={0.427,3.6,142.232,189.194,6.4,31.1,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g15_17']={-62.888,3.6,-149.377,125.776,6.4,43.895,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g16_17']={65.07,3.6,-142.85,130.14,6.4,57.699,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g17_16']={121.74,3.6,3.769,68.892,6.4,251.739,1,true,'SNB_Shore','',''},
  ['WB_Ter_Water__WB_Water']={0.0,1.7,0.0,840.0,1.0,840.0,1,false,'WB_Water','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g14_16']={-134.002,10.95,-53.0,15.192,9.1,34.313,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g15_15']={-75.724,15.034,69.342,102.598,17.632,118.859,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g15_16']={-77.843,15.034,-39.886,120.82,17.633,229.447,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g16_14']={45.0,9.764,133.0,30.569,6.729,11.708,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g16_15']={95.865,9.237,58.024,76.911,13.08,141.66,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g16_16']={81.768,14.989,-69.379,93.648,17.723,134.755,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins__SNB_Ruins_g16_17']={102.428,14.045,-127.0,29.83,15.31,19.514,2,true,'SNB_Ruins','',''},
  ['WB_Prop_Ruins_01__SN_CrystalAmber']={-6.352,9.203,6.758,260.858,6.254,210.458,2,false,'SN_CrystalAmber','',''},
  ['WB_Prop_Ruins_02__SN_CrystalBlue']={-4.068,9.236,-78.676,269.341,6.133,147.074,2,false,'SN_CrystalBlue','',''},
  ['WB_Prop_Ruins_03__SN_Rune']={107.137,8.055,16.23,2.791,3.889,6.885,2,false,'SN_Rune','',''},
  ['WB_Town_Plaza__SNB_Plaza_1']={0.0,6.843,0.0,80.0,0.955,80.0,2,true,'SNB_Plaza_1','',''},
  ['WB_Town_Plaza_01__SNB_Plaza_2']={0.0,6.735,0.0,82.8,1.07,82.8,2,true,'SNB_Plaza_2','',''},
  ['WB_Town_Plaza_02__SN_Rune']={-1.706,7.08,0.0,73.954,0.18,77.6,2,false,'SN_Rune','',''},
  ['WB_Frg_Anvil__SNB_Anvil_1']={-42.809,38.604,-111.784,79.613,63.933,58.496,3,true,'SNB_Anvil_1','','SN_Forja'},
  ['WB_Frg_Anvil_01__SNB_Anvil_2']={0.0,45.123,-118.0,69.399,49.245,39.8,3,true,'SNB_Anvil_2','','SN_Forja'},
  ['WB_Frg_Anvil_02__SNB_Anvil_3']={0.0,24.361,-112.05,148.0,34.723,59.9,3,true,'SNB_Anvil_3','','SN_Forja'},
  ['WB_Frg_Anvil_03__SNB_Anvil_4']={0.0,9.025,-117.0,148.6,0.35,50.6,3,true,'SNB_Anvil_4','','SN_Forja'},
  ['WB_Frg_Anvil_04__SNB_Anvil_5']={0.0,11.025,-117.0,142.6,0.35,44.6,3,true,'SNB_Anvil_5','','SN_Forja'},
  ['WB_Frg_Anvil_05__SNB_Anvil_6']={0.0,14.1,-110.0,142.0,14.2,58.0,3,true,'SNB_Anvil_6','','SN_Forja'},
  ['WB_Frg_Anvil_06__SNB_Anvil_7']={3.0,45.962,-117.752,98.0,48.475,38.496,3,true,'SNB_Anvil_7','','SN_Forja'},
  ['WB_Frg_Anvil_07__SNB_Anvil_8']={37.771,38.754,-113.225,84.571,64.079,55.547,3,true,'SNB_Anvil_8','','SN_Forja'},
  ['WB_Frg_Anvil_08__SN_CrystalAmber']={-63.326,14.979,-93.142,4.282,4.586,2.902,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Anvil_09__SN_CrystalBlue']={57.837,15.399,-116.748,20.358,5.42,52.025,3,false,'SN_CrystalBlue','','SN_Forja'},
  ['WB_Frg_Anvil_10__SN_Lava']={-2.743,33.9,-113.247,29.67,53.2,43.845,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Anvil_11__SN_LavaHot']={19.503,38.6,-113.291,53.794,62.6,44.097,3,false,'SN_LavaHot','','SN_Forja'},
  ['WB_Frg_Anvil_12__SN_Rune']={0.025,39.891,-118.0,70.17,27.318,34.6,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Frg_Anvil_13__WB_Fire']={0.0,17.45,-95.0,141.653,2.1,1.509,3,false,'WB_Fire','','SN_Forja'},
  ['WB_Frg_Anvil_14__WB_FireCore']={0.0,17.1,-95.0,140.9,1.3,0.779,3,false,'WB_FireCore','','SN_Forja'},
  ['WB_Frg_Hall__SNB_Hall']={0.0,27.705,-65.979,39.0,42.611,53.159,3,true,'SNB_Hall','','SN_Forja'},
  ['WB_Frg_Hall_01__SN_CrystalAmber']={-2.4,10.793,-43.175,25.265,0.306,0.306,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Hall_02__SN_CrystalBlue']={0.8,10.793,-43.175,25.265,0.306,0.306,3,false,'SN_CrystalBlue','','SN_Forja'},
  ['WB_Frg_Hall_03__SN_Lava']={1.958,7.375,-81.572,10.517,1.75,21.644,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Hall_04__SN_LavaHot']={2.163,7.655,-82.067,8.726,1.59,20.424,3,false,'SN_LavaHot','','SN_Forja'},
  ['WB_Frg_Hall_05__WB_Fire']={0.0,10.3,-57.464,36.653,4.0,34.437,3,false,'WB_Fire','','SN_Forja'},
  ['WB_Frg_Hall_06__WB_FireCore']={0.0,9.95,-57.353,35.9,3.2,33.485,3,false,'WB_FireCore','','SN_Forja'},
  ['WB_Frg_Hall_07__WB_Ingot']={13.65,8.885,-60.4,1.9,3.73,7.6,3,false,'WB_Ingot','','SN_Forja'},
  ['WB_Frg_Hall_08__WB_Water']={-12.6,9.175,-58.4,2.36,0.15,2.36,3,false,'WB_Water','','SN_Forja'},
  ['WB_Frg_Hammer__SNB_Hammer_1']={107.517,11.733,-65.69,49.905,28.121,49.395,3,true,'SNB_Hammer_1','','SN_Forja'},
  ['WB_Frg_Hammer_01__SNB_Hammer_2']={94.72,57.103,-80.93,37.128,97.011,65.852,3,true,'SNB_Hammer_2','','SN_Forja'},
  ['WB_Frg_Hammer_02__SN_CrystalAmber']={79.225,104.867,-111.221,3.557,3.74,3.74,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Hammer_03__SN_Lava']={104.597,7.06,-63.974,74.151,0.16,78.577,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Hammer_04__SN_Rune']={100.303,11.216,-74.461,13.031,4.268,8.889,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Rank_Tablets__SNB_Rank_1']={64.152,27.115,60.596,62.182,41.33,54.238,4,true,'SNB_Rank_1','','SN_Tabuas'},
  ['WB_Rank_Tablets_01__SNB_Rank_2']={63.639,28.0,53.365,65.047,43.6,70.061,4,true,'SNB_Rank_2','','SN_Tabuas'},
  ['WB_Rank_Tablets_02__SN_CrystalBlue']={57.83,9.243,49.348,44.103,3.877,53.989,4,false,'SN_CrystalBlue','','SN_Tabuas'},
  ['WB_Rank_Tablets_03__SN_Rune']={68.79,20.05,55.331,41.199,16.989,42.284,4,false,'SN_Rune','','SN_Tabuas'},
  ['WB_Rank_Tablets_04__WB_Fire']={65.727,12.65,55.151,41.826,2.1,49.399,4,false,'WB_Fire','','SN_Tabuas'},
  ['WB_Rank_Tablets_05__WB_FireCore']={65.727,12.3,55.151,41.036,1.3,48.621,4,false,'WB_FireCore','','SN_Tabuas'},
  ['WB_Shop_Inside__SNB_ShopIn']={75.164,14.975,-35.054,22.563,13.55,28.101,4,true,'SNB_ShopIn','','SN_Loja'},
  ['WB_Shop_Inside_01__SN_CrystalBlue']={72.913,12.605,-45.115,1.587,1.974,1.57,4,false,'SN_CrystalBlue','','SN_Loja'},
  ['WB_Shop_Inside_02__WB_LampGlow']={72.958,15.625,-34.02,5.023,7.35,9.86,4,false,'WB_LampGlow','','SN_Loja'},
  ['WB_Shop_Temple__SNB_Shop_1']={71.961,19.411,-32.884,38.074,26.181,41.738,4,true,'SNB_Shop_1','','SN_Loja'},
  ['WB_Shop_Temple_01__SNB_Shop_2']={71.5,19.751,-35.286,36.7,25.502,40.692,4,true,'SNB_Shop_2','','SN_Loja'},
  ['WB_Shop_Temple_02__WB_Fire']={58.548,11.45,-27.301,9.127,2.1,17.737,4,false,'WB_Fire','','SN_Loja'},
  ['WB_Shop_Temple_03__WB_FireCore']={58.548,11.1,-27.301,8.503,1.3,17.129,4,false,'WB_FireCore','','SN_Loja'},
  ['PORTAL_DemonSlayer_Swirl__P_DS_Swirl']={-274.962,19.4,-3.733,5.66,15.0,13.908,5,false,'P_DS_Swirl','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Emblem_Cream']={-275.342,21.044,-4.101,15.711,25.028,22.886,5,false,'Emblem_Cream','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Glow']={-274.107,19.4,-3.396,6.27,15.5,14.558,5,false,'P_DS_Glow','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Gravel']={-273.064,9.316,-2.975,29.607,2.833,32.475,5,false,'P_DS_Gravel','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Iron']={-273.758,21.533,-4.831,19.154,25.865,22.739,5,false,'P_DS_Iron','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Lacquer']={-276.737,21.49,-4.794,13.195,25.78,22.667,5,false,'P_DS_Lacquer','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Red']={-273.197,19.368,-5.012,17.281,19.463,20.846,5,false,'P_DS_Red','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Stone_DS_Rock']={-273.342,10.175,-3.087,30.676,4.65,33.908,5,false,'Stone_DS_Rock','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__Bark_Dark']={-276.052,16.814,8.872,3.529,18.217,3.308,5,false,'Bark_Dark','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicMid']={-277.256,24.64,8.443,11.243,6.72,6.09,5,false,'P_DS_GlicMid','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicTip']={-276.657,21.688,9.173,9.595,4.771,4.302,5,false,'P_DS_GlicTip','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_Glicinia']={-276.704,25.157,8.522,10.283,5.986,6.522,5,false,'P_DS_Glicinia','','PORTAL_DemonSlayer'},
  ['PORTAL_DragonBall_Frame__P_DB_Amber']={-250.94,19.042,51.113,24.278,20.277,12.619,5,false,'P_DB_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Ball_Amber']={-254.491,22.915,45.048,9.415,24.77,17.182,5,false,'P_DB_Ball_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Blue']={-252.039,11.402,47.451,23.948,8.905,22.223,5,false,'P_DB_Blue','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Floor']={-252.229,8.94,48.45,29.019,0.32,26.282,5,false,'P_DB_Floor','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Gold_Bright']={-253.083,19.41,46.192,20.557,22.221,18.839,5,false,'P_DB_Gold_Bright','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Rim_Glow']={-252.88,19.4,49.912,14.459,15.566,7.122,5,false,'P_DB_Rim_Glow','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Star_Red']={-254.32,21.826,45.725,8.47,23.722,18.613,5,false,'P_DB_Star_Red','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_White']={-252.229,20.817,48.45,28.818,27.734,26.081,5,false,'P_DB_White','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Swirl__P_DB_Swirl']={-253.083,19.4,50.369,13.703,15.0,6.102,5,false,'P_DB_Swirl','','PORTAL_DragonBall'},
  ['PORTAL_Naruto_Bandana__Leaf_Pine']={-220.631,8.814,53.18,26.789,2.572,17.238,5,false,'Leaf_Pine','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Metal_Dark']={-221.379,23.057,49.21,24.974,26.687,16.793,5,false,'Metal_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Cloth']={-221.837,23.517,49.145,26.069,21.005,16.764,5,false,'P_Naruto_Cloth','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Lacquer']={-221.836,22.08,49.338,25.453,26.84,16.139,5,false,'P_Naruto_Lacquer','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Paper']={-232.21,10.2,50.638,6.31,3.2,7.193,5,false,'P_Naruto_Paper','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Rim_Glow']={-221.959,19.4,50.574,14.735,15.5,5.771,5,false,'P_Naruto_Rim_Glow','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Steel']={-219.425,20.654,45.918,14.094,26.793,11.574,5,false,'P_Naruto_Steel','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Stone']={-221.379,19.475,52.172,18.687,22.15,9.559,5,false,'P_Naruto_Stone','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Dark']={-222.182,17.45,49.964,33.221,19.5,30.352,5,false,'Stone_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Light']={-222.182,8.641,49.964,33.016,0.761,30.147,5,false,'Stone_Light','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Swirl__P_Naruto_Swirl']={-221.635,19.4,51.508,14.095,15.0,5.212,5,false,'P_Naruto_Swirl','','PORTAL_Naruto'},
  ['PORTAL_OnePiece_Pier__Emblem_Cream']={-250.211,25.174,-29.806,11.978,22.253,12.17,5,false,'Emblem_Cream','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Leaf_Palm']={-264.504,19.24,-29.827,8.162,1.955,8.214,5,false,'Leaf_Palm','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Metal_Dark']={-252.388,21.444,-24.809,30.404,26.208,25.186,5,false,'Metal_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Glow']={-252.758,19.4,-25.638,14.362,15.5,6.761,5,false,'P_OP_Glow','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Red']={-245.395,15.2,-35.156,2.666,2.7,1.553,5,false,'P_OP_Red','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Rope']={-252.391,19.578,-24.816,31.676,22.056,30.144,5,false,'Rope','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Dark']={-252.392,19.2,-24.826,31.561,24.0,30.122,5,false,'Wood_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Light']={-253.084,20.779,-26.369,24.01,23.444,11.342,5,false,'Wood_Light','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Plank']={-252.363,13.844,-24.46,29.66,11.912,28.739,5,false,'Wood_Plank','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Swirl__P_OP_Swirl']={-253.083,19.4,-26.369,13.703,15.0,6.102,5,false,'P_OP_Swirl','','PORTAL_OnePiece'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_ConcreteDark']={-221.362,19.669,-28.23,18.997,19.281,9.619,5,false,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Glow']={-221.362,31.02,-28.219,19.273,0.46,9.95,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Yellow']={-221.401,9.35,-28.261,21.252,0.8,11.027,5,false,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Swirl__P_OPM_Swirl']={-221.635,19.4,-27.508,14.095,15.0,5.212,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_SwirlBack__P_OPM_Swirl']={-220.848,19.4,-29.628,14.095,15.0,5.13,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteDark']={-222.182,21.225,-25.964,33.469,26.85,30.361,5,false,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteLight']={-222.182,19.975,-25.964,32.995,24.15,28.931,5,false,'P_OPM_ConcreteLight','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteMid']={-220.563,19.975,-27.529,18.126,22.95,16.031,5,false,'P_OPM_ConcreteMid','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Crater']={-221.256,19.539,-28.307,18.191,18.618,9.23,5,false,'P_OPM_Crater','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_DarkGlassT']={-221.362,30.8,-28.219,19.205,1.3,9.762,5,false,'P_OPM_DarkGlassT','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Glow']={-221.189,19.4,-28.335,15.996,16.24,8.292,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_RebarSteel']={-220.624,18.7,-28.27,19.43,18.916,13.087,5,false,'P_OPM_RebarSteel','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Red']={-222.248,31.676,-25.806,3.603,3.872,1.884,5,false,'P_OPM_Red','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Yellow']={-222.182,21.125,-25.964,33.528,26.45,30.42,5,false,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Core_Glow']={-270.587,23.695,26.283,12.019,21.506,24.037,5,false,'P_SG_Core_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Lilac_Glow']={-273.653,23.275,27.213,7.078,26.631,17.057,5,false,'P_SG_Lilac_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Moon_Glow']={-271.043,23.278,28.457,12.835,26.737,19.608,5,false,'P_SG_Moon_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Deadwood']={-276.331,12.508,14.95,2.221,8.559,2.356,5,false,'P_SG_Deadwood','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Marble']={-272.105,8.8,26.61,23.85,1.9,29.265,5,false,'P_SG_Marble','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Obsidian']={-275.127,23.38,27.846,13.407,29.46,25.232,5,false,'P_SG_Obsidian','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Rose']={-275.593,15.108,15.025,2.559,5.16,2.839,5,false,'P_SG_Rose','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Silver']={-272.105,23.85,26.61,24.108,30.58,29.523,5,false,'P_SG_Silver','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Violet']={-272.962,18.03,27.846,16.545,17.86,23.706,5,false,'P_SG_Violet','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_Shadow_Glow']={-274.385,19.4,27.509,6.27,15.5,14.558,5,false,'P_Shadow_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Swirl__P_Shadow_Swirl']={-274.962,19.4,27.733,5.66,15.0,13.908,5,false,'P_Shadow_Swirl','','PORTAL_ShadowGarden'},
  ['WB_Court_Dais__SNB_Dais_1']={-246.536,17.105,37.803,90.795,21.81,61.173,5,false,'SNB_Dais_1','',''},
  ['WB_Court_Dais_01__SNB_Dais_2']={-248.305,17.105,-17.874,87.376,21.81,58.554,5,false,'SNB_Dais_2','',''},
  ['WB_Court_Dais_02__SN_CrystalAmber']={-237.287,10.238,12.148,57.733,4.895,109.573,5,false,'SN_CrystalAmber','',''},
  ['WB_Court_Dais_03__SN_CrystalBlue']={-257.873,10.159,-37.149,16.436,4.384,10.133,5,false,'SN_CrystalBlue','',''},
  ['WB_Court_Dais_04__SN_CrystalRed']={-286.457,10.17,-7.871,7.297,4.693,17.728,5,false,'SN_CrystalRed','',''},
  ['WB_Court_Dais_05__SN_CrystalViolet']={-286.449,10.177,32.457,9.517,4.621,18.29,5,false,'SN_CrystalViolet','',''},
  ['WB_Court_Dais_06__SN_Rune']={-248.309,7.91,12.0,80.219,0.333,105.805,5,false,'SN_Rune','',''},
  ['WB_Court_Dais_07__WB_Fire']={-243.555,12.61,11.97,51.769,2.1,67.177,5,false,'WB_Fire','',''},
  ['WB_Court_Dais_08__WB_FireCore']={-243.553,12.26,12.0,50.997,1.3,66.461,5,false,'WB_FireCore','',''},
  ['WB_Court_Isle__SNB_Isle']={-234.413,16.827,12.246,109.735,21.546,106.03,5,false,'SNB_Isle','',''},
  ['WB_Court_Isle_01__SN_CrystalAmber']={-257.525,18.125,32.654,46.824,23.68,45.078,5,false,'SN_CrystalAmber','',''},
  ['WB_Court_Isle_02__SN_CrystalBlue']={-275.037,9.431,9.77,13.209,6.452,79.241,5,false,'SN_CrystalBlue','',''},
  ['WB_Court_Isle_03__SN_RuneAmber']={-232.02,14.395,23.35,8.289,14.81,20.713,5,false,'SN_RuneAmber','',''},
  ['WB_Court_Isle_04__SN_RuneBlue']={-240.771,14.395,0.979,9.67,14.81,20.205,5,false,'SN_RuneBlue','',''},
  ['WB_Court_Isle_05__SN_RuneOrange']={-240.771,14.395,23.021,9.67,14.81,20.205,5,false,'SN_RuneOrange','',''},
  ['WB_Court_Isle_06__SN_RuneRed']={-247.192,14.395,7.621,20.471,14.81,8.985,5,false,'SN_RuneRed','',''},
  ['WB_Court_Isle_07__SN_RuneViolet']={-247.192,14.395,16.379,20.471,14.81,8.985,5,false,'SN_RuneViolet','',''},
  ['WB_Court_Isle_08__SN_RuneYellow']={-232.02,14.395,0.65,8.289,14.81,20.713,5,false,'SN_RuneYellow','',''},
  ['WB_Exit_Avenue__SNB_Avenue_0']={-0.093,15.675,117.25,41.522,18.95,57.5,6,true,'SNB_Avenue','',''},
  ['WB_Exit_Avenue__SNB_Avenue_1']={2.445,15.675,117.25,36.455,18.95,57.5,6,true,'SNB_Avenue','',''},
  ['WB_Exit_Avenue_01__SN_Rune']={0.0,7.04,118.75,2.798,0.1,49.498,6,false,'SN_Rune','',''},
  ['WB_Exit_Avenue_02__WB_Fire']={0.0,11.25,119.5,26.053,2.1,19.509,6,false,'WB_Fire','',''},
  ['WB_Exit_Avenue_03__WB_FireCore']={0.0,10.9,119.5,25.3,1.3,18.779,6,false,'WB_FireCore','',''},
  ['WB_Exit_Bridge__SNB_Bridge']={0.0,4.635,185.3,18.4,10.63,78.6,6,true,'SNB_Bridge','',''},
  ['WB_Exit_Bridge_01__WB_Fire']={0.0,10.467,187.0,14.453,2.767,48.175,6,false,'WB_Fire','',''},
  ['WB_Exit_Bridge_02__WB_FireCore']={0.0,10.117,187.0,13.7,1.967,47.446,6,false,'WB_FireCore','',''},
  ['WB_Exit_Gate__SNB_Gate']={0.0,20.85,148.563,31.4,29.3,16.726,6,true,'SNB_Gate','','SN_Portao'},
  ['WB_Exit_Gate_01__WB_Fire']={0.0,11.65,141.8,26.653,2.1,1.509,6,false,'WB_Fire','','SN_Portao'},
  ['WB_Exit_Gate_02__WB_FireCore']={0.0,11.3,141.8,25.9,1.3,0.779,6,false,'WB_FireCore','','SN_Portao'},
  ['WB_Exit_IsleBridge__SNB_IsleBridge']={-159.0,12.275,12.0,52.0,23.95,21.385,6,true,'SNB_IsleBridge','',''},
  ['WB_Exit_IsleBridge_01__WB_Fire']={-156.036,18.075,12.0,41.581,16.15,18.853,6,false,'WB_Fire','',''},
  ['WB_Exit_IsleBridge_02__WB_FireCore']={-156.03,17.725,12.0,40.84,15.35,18.1,6,false,'WB_FireCore','',''},
  ['WB_Exit_Spawn__SNB_Spawn']={0.0,13.03,66.0,46.078,13.66,45.04,6,true,'SNB_Spawn','',''},
  ['WB_Exit_Spawn_01__SN_Rune']={-0.019,14.658,60.891,38.886,9.215,15.096,6,false,'SN_Rune','',''},
  ['WB_Exit_Spawn_02__WB_Fire']={0.0,14.75,66.0,31.453,2.1,29.509,6,false,'WB_Fire','',''},
  ['WB_Exit_Spawn_03__WB_FireCore']={0.0,14.4,66.0,30.7,1.3,28.779,6,false,'WB_FireCore','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g14_15']={-211.136,7.822,13.146,164.981,2.151,96.375,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g14_16']={-180.798,7.878,-48.982,104.071,2.4,98.345,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g15_15']={-30.276,7.883,72.845,194.139,2.687,146.1,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g15_16']={-75.227,7.964,-63.917,101.974,2.457,128.242,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g15_17']={-44.119,7.876,-144.358,88.437,2.257,33.118,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g16_15']={71.093,7.937,63.064,113.854,2.53,126.565,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g16_16']={76.084,7.884,-63.526,103.99,2.394,127.464,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g16_17']={50.939,7.829,-146.827,102.063,2.17,28.842,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g17_15']={135.55,7.92,35.644,14.909,2.341,69.755,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g17_16']={137.238,7.902,-49.189,18.33,2.304,97.53,7,true,'SNB_Tufts','',''},
  ['WB_Veg_ancient__SNB_Veg_ancient']={-96.197,31.253,-113.286,43.481,51.292,41.429,7,true,'SNB_Veg_ancient','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g14_16']={-135.327,8.653,-52.239,15.633,3.258,23.01,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g15_15']={-75.282,8.646,35.92,106.396,3.281,73.445,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g15_16']={-57.864,8.715,-32.901,293.38,3.447,210.194,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g16_15']={48.642,8.638,88.006,50.969,3.254,104.892,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g16_16']={79.265,8.599,-34.081,106.138,3.206,53.064,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g14_15']={-191.5,8.472,10.737,15.161,2.663,19.818,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g15_15']={-52.19,8.918,61.4,105.555,3.655,116.776,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g15_16']={-70.776,8.959,-53.948,85.547,3.675,99.184,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g15_17']={-59.462,8.977,-146.727,24.57,3.639,9.045,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g16_14']={32.441,9.025,133.483,48.825,3.681,12.812,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g16_15']={56.011,8.975,76.812,142.372,3.781,120.763,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g16_16']={72.265,8.878,-69.395,112.759,3.591,118.331,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g16_17']={57.131,8.869,-138.923,88.661,3.576,22.667,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g17_16']={130.658,8.729,-29.156,6.387,3.21,53.547,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g14_15']={-199.192,17.591,24.559,17.641,22.84,18.529,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g14_16']={-168.979,18.753,-11.857,84.266,25.299,20.468,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g15_14']={-54.368,19.781,134.505,23.872,27.09,18.06,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g15_15']={-61.186,19.954,72.755,108.407,27.842,115.23,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g15_16']={-90.455,19.951,-47.818,77.951,27.834,85.802,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g16_15']={75.373,19.613,62.909,108.533,27.119,128.207,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g16_16']={73.47,17.662,-55.333,112.144,22.99,113.562,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g16_17']={18.529,19.831,-153.748,35.505,27.581,25.428,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g17_15']={135.684,19.334,42.35,18.826,26.528,89.035,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g17_16']={137.36,19.334,-55.159,22.676,26.528,113.539,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g15_15']={-74.685,17.225,70.298,108.861,22.346,117.625,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g15_16']={-80.013,15.505,-14.158,32.772,18.661,19.258,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g16_15']={50.554,17.4,51.432,165.85,22.722,160.5,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g16_16']={82.893,17.273,-33.567,93.344,22.448,71.625,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g15_15']={-60.705,20.712,67.087,54.801,29.265,81.017,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g15_16']={-68.62,20.624,-52.692,22.888,29.08,20.829,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g16_15']={57.879,20.036,100.114,20.693,27.843,20.485,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g16_16']={43.864,20.972,-66.929,50.493,29.812,24.047,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g15_15']={-63.89,18.301,99.961,82.218,24.433,61.611,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g15_16']={-71.193,15.815,-37.208,54.877,19.152,69.693,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g16_15']={94.927,15.527,86.651,13.584,18.541,13.61,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g16_16']={97.946,17.755,-18.295,17.686,23.274,18.3,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g14_15']={-113.508,22.906,69.814,188.862,33.501,147.847,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g14_16']={-158.149,22.153,-47.116,63.201,31.934,99.812,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g15_15']={-116.141,20.849,57.494,28.165,29.222,51.401,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g15_16']={-110.028,21.581,-81.708,38.022,30.745,27.376,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g15_17']={-39.423,23.218,-151.87,67.871,34.15,18.982,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g16_14']={22.493,24.177,134.557,30.607,36.145,19.837,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g16_17']={73.86,23.046,-147.759,69.141,33.791,36.575,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g17_15']={81.339,23.234,15.585,137.825,34.182,231.404,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2_g14_15']={-169.704,19.22,39.777,89.965,26.087,32.91,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2_g14_16']={-141.287,19.671,-36.615,16.368,27.035,42.069,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2_g15_15']={-37.661,20.174,86.66,186.525,28.093,85.9,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2_g15_16']={-74.324,20.203,-52.57,111.066,28.154,70.619,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2_g16_15']={86.819,18.266,80.963,76.668,24.084,97.295,7,true,'SNB_Veg_pine2','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2_g16_16']={85.777,20.619,-75.791,91.691,29.027,101.034,7,true,'SNB_Veg_pine2','',''},
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
  {'COL_Court_001','Block',{-221.635,6.9,51.467},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{26.1,15.0,1.4},false},
  {'COL_Court_002','Block',{-221.635,6.9,51.467},{0.174,0.0,-0.985},{-0.985,0.0,-0.174},{26.1,15.0,1.4},false},
  {'COL_Court_003','Block',{-221.635,6.9,51.467},{-0.766,0.0,-0.643},{-0.643,0.0,0.766},{26.1,15.0,1.4},false},
  {'COL_Court_005','Block',{-221.635,7.2,51.467},{0.174,0.0,-0.985},{-0.985,0.0,-0.174},{23.316,13.4,2.0},false},
  {'COL_Court_006','Block',{-221.635,7.2,51.467},{-0.766,0.0,-0.643},{-0.643,0.0,0.766},{23.316,13.4,2.0},false},
  {'COL_Court_007','Block',{-228.679,17.16,65.737},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{2.8,2.8,18.0},true},
  {'COL_Court_008','Block',{-207.066,17.16,57.87},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{2.8,2.8,18.0},true},
  {'COL_Court_009','Block',{-253.083,6.9,50.369},{0.914,0.0,0.407},{0.407,0.0,-0.914},{26.1,15.0,1.4},false},
  {'COL_Court_010','Block',{-253.083,6.9,50.369},{0.809,0.0,-0.588},{-0.588,0.0,-0.809},{26.1,15.0,1.4},false},
  {'COL_Court_011','Block',{-253.083,6.9,50.369},{-0.105,0.0,-0.995},{-0.995,0.0,0.105},{26.1,15.0,1.4},false},
  {'COL_Court_012','Block',{-253.083,7.2,50.369},{0.914,0.0,0.407},{0.407,0.0,-0.914},{23.316,13.4,2.0},false},
  {'COL_Court_013','Block',{-253.083,7.2,50.369},{0.809,0.0,-0.588},{-0.588,0.0,-0.809},{23.316,13.4,2.0},false},
  {'COL_Court_014','Block',{-253.083,7.2,50.369},{-0.105,0.0,-0.995},{-0.995,0.0,0.105},{23.316,13.4,2.0},false},
  {'COL_Court_015','Block',{-268.063,17.16,55.74},{0.914,0.0,0.407},{0.407,0.0,-0.914},{2.8,2.8,18.0},true},
  {'COL_Court_016','Block',{-247.051,17.16,65.095},{0.914,0.0,0.407},{0.407,0.0,-0.914},{2.8,2.8,18.0},true},
  {'COL_Court_017','Block',{-274.942,6.9,27.733},{0.375,0.0,0.927},{0.927,0.0,-0.375},{26.1,15.0,1.4},false},
  {'COL_Court_018','Block',{-274.942,6.9,27.733},{0.99,0.0,0.139},{0.139,0.0,-0.99},{26.1,15.0,1.4},false},
  {'COL_Court_019','Block',{-274.942,6.9,27.733},{0.616,0.0,-0.788},{-0.788,0.0,-0.616},{26.1,15.0,1.4},false},
  {'COL_Court_020','Block',{-274.942,7.2,27.733},{0.375,0.0,0.927},{0.927,0.0,-0.375},{23.316,13.4,2.0},false},
  {'COL_Court_021','Block',{-274.942,7.2,27.733},{0.99,0.0,0.139},{0.139,0.0,-0.99},{23.316,13.4,2.0},false},
  {'COL_Court_022','Block',{-274.942,7.2,27.733},{0.616,0.0,-0.788},{-0.788,0.0,-0.616},{23.316,13.4,2.0},false},
  {'COL_Court_023','Block',{-289.449,17.16,21.192},{0.375,0.0,0.927},{0.927,0.0,-0.375},{2.8,2.8,18.0},true},
  {'COL_Court_024','Block',{-280.833,17.16,42.517},{0.375,0.0,0.927},{0.927,0.0,-0.375},{2.8,2.8,18.0},true},
  {'COL_Court_025','Block',{-274.942,6.9,-3.733},{-0.375,0.0,0.927},{0.927,0.0,0.375},{26.1,15.0,1.4},false},
  {'COL_Court_026','Block',{-274.942,6.9,-3.733},{0.616,0.0,0.788},{0.788,0.0,-0.616},{26.1,15.0,1.4},false},
  {'COL_Court_027','Block',{-274.942,6.9,-3.733},{0.99,0.0,-0.139},{-0.139,0.0,-0.99},{26.1,15.0,1.4},false},
  {'COL_Court_028','Block',{-274.942,7.2,-3.733},{-0.375,0.0,0.927},{0.927,0.0,0.375},{23.316,13.4,2.0},false},
  {'COL_Court_029','Block',{-274.942,7.2,-3.733},{0.616,0.0,0.788},{0.788,0.0,-0.616},{23.316,13.4,2.0},false},
  {'COL_Court_030','Block',{-274.942,7.2,-3.733},{0.99,0.0,-0.139},{-0.139,0.0,-0.99},{23.316,13.4,2.0},false},
  {'COL_Court_031','Block',{-280.833,17.16,-18.517},{-0.375,0.0,0.927},{0.927,0.0,0.375},{2.8,2.8,18.0},true},
  {'COL_Court_032','Block',{-289.449,17.16,2.808},{-0.375,0.0,0.927},{0.927,0.0,0.375},{2.8,2.8,18.0},true},
  {'COL_Court_033','Block',{-253.083,6.9,-26.369},{-0.914,0.0,0.407},{0.407,0.0,0.914},{26.1,15.0,1.4},false},
  {'COL_Court_034','Block',{-253.083,6.9,-26.369},{-0.105,0.0,0.995},{0.995,0.0,0.105},{26.1,15.0,1.4},false},
  {'COL_Court_035','Block',{-253.083,6.9,-26.369},{0.809,0.0,0.588},{0.588,0.0,-0.809},{26.1,15.0,1.4},false},
  {'COL_Court_037','Block',{-253.083,7.2,-26.369},{-0.105,0.0,0.995},{0.995,0.0,0.105},{23.316,13.4,2.0},false},
  {'COL_Court_038','Block',{-253.083,7.2,-26.369},{0.809,0.0,0.588},{0.588,0.0,-0.809},{23.316,13.4,2.0},false},
  {'COL_Court_039','Block',{-247.051,17.16,-41.095},{-0.914,0.0,0.407},{0.407,0.0,0.914},{2.8,2.8,18.0},true},
  {'COL_Court_040','Block',{-268.063,17.16,-31.74},{-0.914,0.0,0.407},{0.407,0.0,0.914},{2.8,2.8,18.0},true},
  {'COL_Court_041','Block',{-221.635,6.9,-27.467},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{26.1,15.0,1.4},false},
  {'COL_Court_042','Block',{-221.635,6.9,-27.467},{-0.766,0.0,0.643},{0.643,0.0,0.766},{26.1,15.0,1.4},false},
  {'COL_Court_043','Block',{-221.635,6.9,-27.467},{0.174,0.0,0.985},{0.985,0.0,-0.174},{26.1,15.0,1.4},false},
  {'COL_Court_045','Block',{-221.635,7.2,-27.467},{-0.766,0.0,0.643},{0.643,0.0,0.766},{23.316,13.4,2.0},false},
  {'COL_Court_046','Block',{-221.635,7.2,-27.467},{0.174,0.0,0.985},{0.985,0.0,-0.174},{23.316,13.4,2.0},false},
  {'COL_Court_047','Block',{-207.066,17.16,-33.87},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{2.8,2.8,18.0},true},
  {'COL_Court_048','Block',{-228.679,17.16,-41.737},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{2.8,2.8,18.0},true},
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
  {'COL_Isle_001','Block',{-236.0,7.9,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.4,8.4,2.0},false},
  {'COL_Isle_002','Block',{-236.0,18.25,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,4.0,19.0},false},
  {'COL_Isle_003','Block',{-236.0,6.5,-6.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{26.533,4.0,1.0},false},
  {'COL_Isle_004','Block',{-236.0,6.5,-2.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{35.777,4.0,1.0},false},
  {'COL_Isle_005','Block',{-236.0,6.5,2.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{41.569,4.0,1.0},false},
  {'COL_Isle_006','Block',{-236.0,6.5,6.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{45.255,4.0,1.0},false},
  {'COL_Isle_007','Block',{-236.0,6.5,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{48.0,8.0,1.0},false},
  {'COL_Isle_009','Block',{-236.0,6.5,18.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{45.255,4.0,1.0},false},
  {'COL_Isle_010','Block',{-236.0,6.5,22.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{41.569,4.0,1.0},false},
  {'COL_Isle_011','Block',{-236.0,6.5,26.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{35.777,4.0,1.0},false},
  {'COL_Isle_012','Block',{-236.0,6.5,30.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{26.533,4.0,1.0},false},
  {'COL_Isle_013','Block',{-182.0,13.0,4.4},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.4,3.4,12.0},false},
  {'COL_Isle_014','Block',{-182.0,13.0,19.6},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.4,3.4,12.0},false},
  {'COL_Isle_015','Block',{-237.675,14.8,59.971},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_016','Block',{-270.528,14.8,45.344},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_017','Block',{-284.0,14.8,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_018','Block',{-270.528,14.8,-21.344},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_019','Block',{-237.675,14.8,-35.971},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_020','Block',{-159.0,8.3,18.55},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,0.9,2.6},false},
  {'COL_Isle_021','Block',{-159.0,8.3,5.45},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,0.9,2.6},false},
  {'COL_Isle_022','Block',{-159.0,6.2,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,14.0,1.6},false},
  {'COL_Isle_029','Block',{-138.0,6.5,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,15.2,1.0},false},
  {'COL_Isle_030','Block',{-180.0,6.5,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,15.2,1.0},false},
  {'COL_Isle_031','Block',{-136.0,14.0,3.4},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.2,3.2,14.0},false},
  {'COL_Isle_032','Block',{-136.0,14.0,20.6},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.2,3.2,14.0},false},
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
  {'COL_Portal_001','Block',{-222.182,7.9,49.964},{-0.94,0.0,0.342},{0.342,0.0,0.94},{27.2,22.4,1.4},false},
  {'COL_Portal_002','Block',{-221.379,8.41,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{10.746,10.746,2.42},false},
  {'COL_Portal_003','Block',{-221.379,8.41,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{13.984,5.776,2.42},false},
  {'COL_Portal_004','Block',{-221.379,8.41,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{5.776,13.984,2.42},false},
  {'COL_Portal_005','Block',{-221.379,8.925,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{9.191,9.191,3.45},false},
  {'COL_Portal_006','Block',{-221.379,8.925,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{11.96,4.94,3.45},false},
  {'COL_Portal_007','Block',{-221.379,8.925,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{4.94,11.96,3.45},false},
  {'COL_Portal_008','Block',{-221.379,9.425,52.172},{-0.94,0.0,0.342},{0.342,0.0,0.94},{11.2,5.2,4.45},false},
  {'COL_Portal_009','Block',{-218.013,11.719,50.947},{0.852,0.423,-0.31},{0.342,0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_010','Block',{-215.19,14.067,49.919},{0.591,0.777,-0.215},{0.342,0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_011','Block',{-213.619,17.494,49.348},{0.211,0.974,-0.077},{0.342,0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_012','Block',{-213.619,21.306,49.348},{-0.211,0.974,0.077},{0.342,-0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_013','Block',{-224.744,11.719,53.397},{0.852,-0.423,-0.31},{0.342,-0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_014','Block',{-227.568,14.067,54.425},{0.591,-0.777,-0.215},{0.342,-0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_015','Block',{-229.138,17.494,54.996},{0.211,-0.974,-0.077},{0.342,-0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_016','Block',{-229.138,21.306,54.996},{-0.211,-0.974,0.077},{0.342,0.0,0.94},{4.429,3.5,1.85},false},
  {'COL_Portal_017','Block',{-210.29,22.55,48.136},{-0.94,0.0,0.342},{0.342,0.0,0.94},{2.8,2.8,27.9},false},
  {'COL_Portal_018','Block',{-232.467,22.55,56.208},{-0.94,0.0,0.342},{0.342,0.0,0.94},{2.8,2.8,27.9},false},
  {'COL_Portal_019','Block',{-213.041,12.182,41.052},{0.479,-0.0,-0.878},{-0.827,0.334,-0.452},{1.8,1.8,9.0},false},
  {'COL_Portal_020','Block',{-231.614,10.2,51.534},{-0.883,0.0,0.469},{0.469,0.0,0.883},{5.6,3.6,3.2},false},
  {'COL_Portal_021','Block',{-252.229,8.15,48.45},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{26.2,12.2,1.9},false},
  {'COL_Portal_022','Block',{-252.229,8.15,48.45},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{14.8,21.4,1.9},false},
  {'COL_Portal_023','Block',{-253.083,9.3,50.369},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{21.6,5.2,1.4},false},
  {'COL_Portal_024','Block',{-253.083,9.3,50.369},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{17.2,9.4,1.4},false},
  {'COL_Portal_025','Block',{-253.083,9.3,50.369},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{10.8,12.0,1.4},false},
  {'COL_Portal_026','Block',{-252.229,8.15,48.45},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{22.0,17.4,1.9},false},
  {'COL_Portal_027','Block',{-253.083,9.3,50.369},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{18.4,8.4,1.4},false},
  {'COL_Portal_028','Block',{-245.812,12.878,54.563},{0.72,-0.616,0.321},{-0.407,0.0,0.914},{2.588,5.451,5.066},false},
  {'COL_Portal_029','Block',{-249.112,9.722,53.054},{0.4,-0.899,0.178},{-0.407,-0.0,0.914},{2.934,5.525,5.144},false},
  {'COL_Portal_030','Block',{-249.678,11.873,51.748},{0.4,-0.899,0.178},{-0.407,-0.0,0.914},{1.85,2.25,4.068},false},
  {'COL_Portal_031','Block',{-261.065,12.878,47.772},{-0.72,-0.616,-0.321},{-0.407,0.0,0.914},{2.588,5.451,5.066},false},
  {'COL_Portal_032','Block',{-257.736,9.722,49.214},{-0.4,-0.899,-0.178},{-0.407,-0.0,0.914},{2.934,5.525,5.144},false},
  {'COL_Portal_033','Block',{-256.386,11.873,48.761},{-0.4,-0.899,-0.178},{-0.407,-0.0,0.914},{1.85,2.25,4.068},false},
  {'COL_Portal_034','Block',{-245.897,13.818,53.541},{0.858,-0.342,0.382},{-0.407,-0.0,0.914},{3.58,2.45,9.829},false},
  {'COL_Portal_035','Block',{-244.653,20.382,54.122},{0.905,0.139,0.403},{-0.407,0.0,0.914},{3.55,2.3,6.133},false},
  {'COL_Portal_036','Block',{-260.248,13.818,47.151},{-0.858,-0.342,-0.382},{-0.407,-0.0,0.914},{3.58,2.45,9.829},false},
  {'COL_Portal_037','Block',{-261.513,20.382,46.615},{-0.905,0.139,-0.403},{-0.407,0.0,0.914},{3.55,2.3,6.133},false},
  {'COL_Portal_038','Block',{-241.078,10.2,45.534},{0.777,0.0,0.629},{0.629,0.0,-0.777},{4.9,2.0,2.2},false},
  {'COL_Portal_039','Block',{-256.649,10.815,38.71},{-0.777,0.0,-0.629},{-0.629,0.0,0.777},{6.0,2.0,3.53},false},
  {'COL_Portal_040','Block',{-253.052,10.825,50.3},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{13.6,2.35,2.05},false},
  {'COL_Portal_041','Block',{-253.998,12.15,52.424},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{16.0,2.7,4.7},false},
  {'COL_Portal_042','Block',{-253.88,19.4,52.159},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{7.2,2.52,7.2},false},
  {'COL_Portal_043','Block',{-248.69,16.483,54.034},{-0.996,-0.074,-0.057},{0.083,-0.979,-0.187},{5.253,4.687,1.6},false},
  {'COL_Portal_044','Block',{-248.888,20.667,54.213},{-0.998,0.032,-0.058},{-0.036,-0.996,0.081},{5.026,5.279,1.6},false},
  {'COL_Portal_045','Block',{-258.746,16.483,49.557},{-0.709,0.074,-0.702},{0.083,-0.979,-0.187},{5.253,4.687,1.6},false},
  {'COL_Portal_046','Block',{-258.746,20.667,49.824},{-0.711,-0.032,-0.703},{-0.036,-0.996,0.081},{5.026,5.279,1.6},false},
  {'COL_Portal_047','Block',{-272.114,7.925,26.591},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{27.2,14.3,1.45},false},
  {'COL_Portal_048','Block',{-272.067,7.925,26.572},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{23.36,17.4,1.45},false},
  {'COL_Portal_049','Block',{-271.882,8.2,26.497},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{17.2,9.4,2.0},false},
  {'COL_Portal_050','Block',{-271.326,8.2,26.273},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{14.32,10.6,2.0},false},
  {'COL_Portal_051','Block',{-272.531,8.475,26.76},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{14.0,6.0,2.55},false},
  {'COL_Portal_052','Block',{-272.067,8.475,26.572},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{11.6,7.0,2.55},false},
  {'COL_Portal_053','Block',{-271.053,14.95,38.026},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{3.8,4.3,13.5},false},
  {'COL_Portal_054','Block',{-279.294,14.95,17.628},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{3.8,4.3,13.5},false},
  {'COL_Portal_055','Block',{-272.72,10.775,33.9},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{5.1,2.0,4.25},false},
  {'COL_Portal_056','Block',{-272.008,17.3,35.662},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.3,2.0,8.8},false},
  {'COL_Portal_057','Block',{-277.627,10.775,21.754},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{5.1,2.0,4.25},false},
  {'COL_Portal_058','Block',{-278.339,17.3,19.992},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.3,2.0,8.8},false},
  {'COL_Portal_059','Block',{-276.101,19.4,28.202},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{10.7,2.1,10.7},false},
  {'COL_Portal_060','Block',{-276.101,19.4,28.202},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{13.9,2.1,5.74},false},
  {'COL_Portal_061','Block',{-276.101,19.4,28.202},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{5.74,2.1,13.9},false},
  {'COL_Portal_062','Block',{-266.106,8.65,37.322},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{2.1,2.1,1.9},false},
  {'COL_Portal_063','Block',{-266.106,11.625,37.322},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.0,1.0,4.05},false},
  {'COL_Portal_064','Block',{-276.602,9.775,14.815},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.6,1.6,4.15},false},
  {'COL_Portal_065','Block',{-275.216,12.8,15.441},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.8,1.7,1.9},false},
  {'COL_Portal_066','Block',{-265.902,7.925,-0.081},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{6.0,5.7,1.45},false},
  {'COL_Portal_067','Block',{-269.1,8.2,-1.373},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{5.2,1.2,2.0},false},
  {'COL_Portal_068','Block',{-270.074,8.7,-1.767},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{4.6,1.1,3.0},false},
  {'COL_Portal_069','Block',{-268.582,10.775,4.552},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.1,1.1,5.15},false},
  {'COL_Portal_070','Block',{-264.612,10.775,-5.276},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.1,1.1,5.15},false},
  {'COL_Portal_071','Block',{-276.807,13.7,9.426},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.7,1.7,11.0},false},
  {'COL_Portal_072','Block',{-275.637,9.2,-4.014},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{10.0,8.3,4.0},false},
  {'COL_Portal_073','Block',{-278.511,9.0,2.698},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{4.6,8.0,3.6},false},
  {'COL_Portal_074','Block',{-279.736,9.35,5.33},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.2,7.7,4.3},false},
  {'COL_Portal_075','Block',{-280.213,9.8,6.378},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.1,7.0,5.2},false},
  {'COL_Portal_076','Block',{-280.505,8.975,7.5},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.2,10.1,3.55},false},
  {'COL_Portal_077','Block',{-278.051,14.9,3.962},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.2,1.9,3.0},false},
  {'COL_Portal_078','Block',{-278.463,20.05,4.982},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.8,1.9,7.3},false},
  {'COL_Portal_079','Block',{-281.27,12.8,3.255},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{3.5,2.1,4.0},false},
  {'COL_Portal_080','Block',{-273.042,9.0,-10.839},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{4.6,8.0,3.6},false},
  {'COL_Portal_081','Block',{-272.094,9.35,-13.584},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.2,7.7,4.3},false},
  {'COL_Portal_082','Block',{-271.71,9.8,-14.669},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.1,7.0,5.2},false},
  {'COL_Portal_083','Block',{-271.14,8.975,-15.679},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.2,10.1,3.55},false},
  {'COL_Portal_084','Block',{-271.832,14.9,-11.429},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.2,1.9,3.0},false},
  {'COL_Portal_085','Block',{-271.42,20.05,-12.449},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.8,1.9,7.3},false},
  {'COL_Portal_086','Block',{-274.64,12.8,-13.157},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{3.5,2.1,4.0},false},
  {'COL_Portal_087','Block',{-271.279,8.95,-2.254},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{23.8,1.7,3.5},false},
  {'COL_Portal_088','Block',{-280.18,8.975,-5.85},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{23.8,2.1,3.55},false},
  {'COL_Portal_089','Block',{-277.121,19.2,-4.614},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{15.2,3.9,16.0},false},
  {'COL_Portal_090','Block',{-252.229,8.0,-24.45},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{22.8,21.4,1.6},false},
  {'COL_Portal_091','Block',{-263.1,9.6,-19.61},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.4,21.4,2.8},false},
  {'COL_Portal_092','Block',{-241.358,9.6,-29.291},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.4,21.4,2.8},false},
  {'COL_Portal_093','Block',{-253.083,8.55,-26.369},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{12.16,12.16,2.5},false},
  {'COL_Portal_094','Block',{-253.083,8.55,-26.369},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{15.824,6.536,2.5},false},
  {'COL_Portal_095','Block',{-253.083,8.55,-26.369},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{6.536,15.824,2.5},false},
  {'COL_Portal_096','Block',{-253.083,8.95,-26.369},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{9.332,9.332,3.3},false},
  {'COL_Portal_097','Block',{-253.083,8.95,-26.369},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{12.144,5.016,3.3},false},
  {'COL_Portal_098','Block',{-253.083,8.95,-26.369},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{5.016,12.144,3.3},false},
  {'COL_Portal_099','Block',{-257.99,14.0,-14.77},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{5.0,1.4,10.5},false},
  {'COL_Portal_100','Block',{-245.677,19.7,-35.796},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.4,1.4,23.0},false},
  {'COL_Portal_101','Block',{-241.139,10.3,-21.178},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{3.6,2.8,3.0},false},
  {'COL_Portal_102','Block',{-261.939,10.1,-30.526},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{2.4,2.4,2.6},false},
  {'COL_Portal_103','Block',{-242.563,10.1,-25.36},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{2.4,2.4,2.6},false},
  {'COL_Portal_104','Block',{-265.046,12.2,-29.143},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.6,1.6,8.0},false},
  {'COL_Portal_110','Block',{-253.917,18.8,-28.242},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{15.2,0.4,16.4},false},
  {'COL_Portal_111','Block',{-222.182,7.95,-25.964},{0.94,0.0,0.342},{0.342,0.0,-0.94},{27.6,22.4,1.5},false},
  {'COL_Portal_112','Block',{-222.695,8.925,-24.554},{0.94,0.0,0.342},{0.342,0.0,-0.94},{11.6,5.8,1.45},false},
  {'COL_Portal_113','Block',{-222.251,9.4,-25.776},{0.94,0.0,0.342},{0.342,0.0,-0.94},{10.0,3.2,2.4},false},
  {'COL_Portal_114','Block',{-229.654,20.275,-31.237},{0.94,0.0,0.342},{0.342,0.0,-0.94},{3.65,4.2,24.15},false},
  {'COL_Portal_115','Block',{-213.069,20.275,-25.201},{0.94,0.0,0.342},{0.342,0.0,-0.94},{3.65,4.2,24.15},false},
  {'COL_Portal_116','Block',{-221.362,28.775,-28.219},{0.94,0.0,0.342},{0.342,0.0,-0.94},{14.0,3.2,7.15},false},
  {'COL_Portal_117','Block',{-221.259,9.9,-28.501},{0.94,0.0,0.342},{0.342,0.0,-0.94},{7.2,2.6,3.4},false},
  {'COL_Portal_118','Block',{-226.239,10.5,-30.313},{0.94,0.0,0.342},{0.342,0.0,-0.94},{3.4,2.6,4.6},false},
  {'COL_Portal_119','Block',{-216.279,10.5,-26.688},{0.94,0.0,0.342},{0.342,0.0,-0.94},{3.4,2.6,4.6},false},
  {'COL_Portal_120','Block',{-220.968,18.4,-29.299},{0.94,0.0,0.342},{0.342,0.0,-0.94},{12.0,0.9,13.6},false},
  {'COL_Portal_121','Ramp',{-217.585,9.298,-30.115},{-0.277,0.588,0.76},{0.94,0.0,0.342},{2.08,3.4,0.8},false},
  {'COL_Portal_122','Block',{-213.779,9.119,-30.843},{0.94,0.0,0.342},{0.342,0.0,-0.94},{3.214,3.004,1.839},false},
  {'COL_Portal_123','Block',{-213.861,10.392,-31.384},{0.94,0.0,0.342},{0.342,0.0,-0.94},{1.212,1.948,0.768},false},
  {'COL_Portal_124','Block',{-216.749,8.912,-33.875},{0.94,0.0,0.342},{0.342,0.0,-0.94},{2.478,2.247,1.425},false},
  {'COL_Portal_125','Ramp',{-214.605,9.181,-23.099},{0.238,0.719,-0.653},{-0.94,-0.0,-0.342},{1.56,2.2,0.8},false},
  {'COL_Portal_126','Block',{-213.73,8.916,-20.473},{0.94,0.0,0.342},{0.342,0.0,-0.94},{1.515,1.426,1.433},false},
  {'COL_Portal_127','Block',{-214.1,9.824,-20.952},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.559,0.477,0.698},false},
  {'COL_Portal_128','Block',{-216.627,8.715,-20.159},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.898,0.966,1.03},false},
  {'COL_Portal_129','Block',{-233.068,9.675,-22.37},{0.998,0.0,-0.07},{-0.07,0.0,-0.998},{4.4,1.2,2.95},false},
  {'COL_Portal_130','Block',{-230.376,9.425,-25.966},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.8,0.8,2.45},false},
  {'COL_Portal_131','Block',{-230.93,9.279,-27.658},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.68,0.68,2.158},false},
  {'COL_Rank_001','Block',{64.348,7.0,53.994},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{68.0,26.0,1.2},false},
  {'COL_Rank_002','Block',{53.777,6.7,45.123},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{68.6,1.6,0.6},false},
  {'COL_Rank_003','Block',{50.242,18.6,82.626},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{3.4,3.4,22.0},true},
  {'COL_Rank_004','Block',{90.097,18.6,35.133},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{3.4,3.4,22.0},true},
  {'COL_Rank_005','Block',{72.161,27.6,60.55},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{68.0,3.2,40.0},true},
  {'COL_Rank_006','Block',{68.255,20.9,57.272},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{56.0,2.6,26.6},true},
  {'COL_Ruins_001','Block',{-26.958,13.8,38.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_002','Block',{-38.5,13.8,26.958},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_003','Block',{-45.399,13.8,12.164},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_004','Block',{-46.821,13.8,-4.096},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_005','Block',{-42.596,13.8,-19.863},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_006','Block',{-33.234,13.8,-33.234},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_007','Block',{-19.863,13.8,-42.596},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_008','Block',{38.5,13.8,-26.958},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_009','Block',{45.399,13.8,-12.164},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,15.0},false},
  {'COL_Ruins_010','Block',{112.0,8.8,18.0},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{13.0,10.0,9.0},false},
  {'COL_Ruins_011','Block',{-113.342,9.4,-86.175},{0.489,0.0,-0.873},{-0.873,0.0,-0.489},{60.0,1.8,6.0},false},
  {'COL_Ruins_021','Block',{103.141,9.4,-126.266},{0.841,0.0,0.541},{0.541,0.0,-0.841},{36.0,1.8,6.0},false},
  {'COL_Ruins_027','Block',{115.652,9.4,72.58},{-0.514,0.0,0.857},{0.857,0.0,0.514},{48.0,1.8,6.0},false},
  {'COL_Ruins_035','Block',{-89.42,9.4,116.348},{0.857,0.0,0.514},{0.514,0.0,-0.857},{48.0,1.8,6.0},false},
  {'COL_Ruins_043','Block',{-134.872,9.4,-53.726},{0.174,0.0,-0.985},{-0.985,0.0,-0.174},{36.0,1.8,6.0},false},
  {'COL_Ruins_049','Block',{43.577,9.4,133.474},{-0.949,0.0,0.316},{0.316,0.0,0.949},{34.623,1.8,6.0},false},
  {'COL_Ruins_055','Block',{-117.064,11.5,-50.85},{-0.866,0.0,0.5},{0.5,0.0,0.866},{2.6,2.6,10.0},false},
  {'COL_Ruins_056','Block',{-126.936,11.5,-45.15},{-0.866,0.0,0.5},{0.5,0.0,0.866},{2.6,2.6,10.0},false},
  {'COL_Ruins_057','Block',{110.05,11.5,-133.356},{0.342,0.0,0.94},{0.94,0.0,-0.342},{2.6,2.6,10.0},false},
  {'COL_Ruins_058','Block',{113.95,11.5,-122.644},{0.342,0.0,0.94},{0.94,0.0,-0.342},{2.6,2.6,10.0},false},
  {'COL_Ruins_059','Block',{-61.01,11.5,112.387},{-0.174,0.0,0.985},{0.985,0.0,0.174},{2.6,2.6,10.0},false},
  {'COL_Ruins_060','Block',{-62.99,11.5,123.613},{-0.174,0.0,0.985},{0.985,0.0,0.174},{2.6,2.6,10.0},false},
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
  {'COL_Terrain_041','Block',{-237.0,4.8,-51.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{48.0,8.0,4.0},false},
  {'COL_Terrain_042','Block',{-238.0,4.8,-43.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{70.0,8.0,4.0},false},
  {'COL_Terrain_043','Block',{-239.0,4.8,-35.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{88.0,8.0,4.0},false},
  {'COL_Terrain_044','Block',{-239.0,4.8,-27.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{100.0,8.0,4.0},false},
  {'COL_Terrain_045','Block',{-237.0,4.8,-19.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{112.0,8.0,4.0},false},
  {'COL_Terrain_046','Block',{-235.0,4.8,-11.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{120.0,8.0,4.0},false},
  {'COL_Terrain_047','Block',{-233.0,4.8,-3.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{124.0,8.0,4.0},false},
  {'COL_Terrain_048','Block',{-233.0,4.8,12.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{128.0,24.0,4.0},false},
  {'COL_Terrain_051','Block',{-234.0,4.8,28.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{126.0,8.0,4.0},false},
  {'COL_Terrain_052','Block',{-236.0,4.8,36.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{122.0,8.0,4.0},false},
  {'COL_Terrain_053','Block',{-237.0,4.8,44.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{116.0,8.0,4.0},false},
  {'COL_Terrain_054','Block',{-239.0,4.8,52.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{108.0,8.0,4.0},false},
  {'COL_Terrain_055','Block',{-239.0,4.8,60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{96.0,8.0,4.0},false},
  {'COL_Terrain_056','Block',{-240.0,4.8,68.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{78.0,8.0,4.0},false},
  {'COL_Veg_001','Block',{115.137,11.926,-17.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.199,3.199,10.253},false},
  {'COL_Veg_002','Block',{8.982,12.284,-150.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.422,3.422,10.968},false},
  {'COL_Veg_003','Block',{140.965,11.717,-39.209},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.068,3.068,9.833},false},
  {'COL_Veg_004','Block',{-198.214,12.109,24.803},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.313,3.313,10.619},false},
  {'COL_Veg_005','Block',{-45.697,13.272,108.089},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.039,4.039,12.945},false},
  {'COL_Veg_006','Block',{95.807,13.104,25.51},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.934,3.934,12.608},false},
  {'COL_Veg_007','Block',{-88.172,12.112,65.376},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.315,3.315,10.625},false},
  {'COL_Veg_008','Block',{106.632,13.002,43.237},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.87,3.87,12.403},false},
  {'COL_Veg_009','Block',{-72.399,12.636,63.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.641,3.641,11.671},false},
  {'COL_Veg_010','Block',{78.067,12.162,11.831},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.346,3.346,10.725},false},
  {'COL_Veg_011','Block',{78.82,11.847,118.765},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.15,3.15,10.095},false},
  {'COL_Veg_012','Block',{135.483,12.967,0.607},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.848,3.848,12.334},false},
  {'COL_Veg_013','Block',{-62.191,12.991,-34.075},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.863,3.863,12.382},false},
  {'COL_Veg_014','Block',{32.44,12.942,80.288},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.832,3.832,12.283},false},
  {'COL_Veg_015','Block',{134.883,11.502,14.345},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.934,2.934,9.403},false},
  {'COL_Veg_016','Block',{-112.423,12.063,-14.031},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.284,3.284,10.525},false},
  {'COL_Veg_017','Block',{-106.283,12.552,45.718},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.589,3.589,11.504},false},
  {'COL_Veg_018','Block',{-56.711,12.481,34.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.545,3.545,11.362},false},
  {'COL_Veg_019','Block',{-58.219,11.558,136.504},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.969,2.969,9.516},false},
  {'COL_Veg_020','Block',{-70.906,11.992,-81.211},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.24,3.24,10.383},false},
  {'COL_Veg_021','Block',{-93.841,13.271,-34.813},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.038,4.038,12.941},false},
  {'COL_Veg_022','Block',{-78.788,12.572,-39.429},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.602,3.602,11.545},false},
  {'COL_Veg_023','Block',{-77.41,12.024,101.455},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.26,3.26,10.448},false},
  {'COL_Veg_024','Block',{-201.468,12.681,-10.417},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.67,3.67,11.763},false},
  {'COL_Veg_025','Block',{138.777,12.374,-70.399},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.478,3.478,11.148},false},
  {'COL_Veg_026','Block',{-124.873,11.546,-14.78},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.961,2.961,9.492},false},
  {'COL_Veg_027','Block',{123.496,12.875,78.242},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.791,3.791,12.151},false},
  {'COL_Veg_028','Block',{90.245,12.839,59.454},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.768,3.768,12.078},false},
  {'COL_Veg_029','Block',{87.831,11.771,97.838},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.102,3.102,9.943},false},
  {'COL_Veg_030','Block',{28.678,12.081,-50.858},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.296,3.296,10.563},false},
  {'COL_Veg_031','Block',{-94.173,12.012,-50.413},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.252,3.252,10.425},false},
  {'COL_Veg_032','Block',{-52.307,13.201,125.592},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.994,3.994,12.803},false},
  {'COL_Veg_033','Block',{24.364,11.529,-80.878},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.951,2.951,9.457},false},
  {'COL_Veg_034','Block',{-91.107,13.151,92.958},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.963,3.963,12.702},false},
  {'COL_Veg_035','Block',{124.977,12.144,-103.503},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.335,3.335,10.689},false},
  {'COL_Veg_036','Block',{-98.514,13.14,25.375},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.956,3.956,12.68},false},
  {'COL_Veg_037','Block',{111.817,12.736,98.328},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.704,3.704,11.871},false},
  {'COL_Veg_038','Block',{-80.138,12.099,76.469},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.307,3.307,10.598},false},
  {'COL_Veg_039','Block',{96.639,11.904,9.989},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.185,3.185,10.208},false},
  {'COL_Veg_040','Block',{-30.806,13.184,50.16},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.984,3.984,12.769},false},
  {'COL_Veg_041','Block',{-114.712,12.933,-76.642},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.827,3.827,12.267},false},
  {'COL_Veg_042','Block',{25.388,13.212,-154.521},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.001,4.001,12.824},false},
  {'COL_Veg_043','Block',{-16.157,11.718,88.005},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.069,3.069,9.835},false},
  {'COL_Veg_044','Block',{-76.393,11.94,20.439},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.207,3.207,10.279},false},
  {'COL_Veg_045','Block',{45.437,11.981,-60.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.233,3.233,10.362},false},
  {'COL_Veg_046','Block',{29.023,12.044,118.662},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.272,3.272,10.489},false},
  {'COL_Veg_047','Block',{-27.328,10.797,125.026},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.494,2.494,7.994},false},
  {'COL_Veg_048','Block',{22.09,11.289,92.961},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.801,2.801,8.977},false},
  {'COL_Veg_049','Block',{-35.133,10.877,74.404},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.544,2.544,8.155},false},
  {'COL_Veg_050','Block',{-37.829,11.957,34.794},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.218,3.218,10.315},false},
  {'COL_Veg_051','Block',{89.853,10.916,-1.937},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.568,2.568,8.231},false},
  {'COL_Veg_052','Block',{-89.153,11.107,-16.84},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.687,2.687,8.614},false},
  {'COL_Veg_053','Block',{42.756,11.955,93.828},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.217,3.217,10.31},false},
  {'COL_Veg_054','Block',{72.226,11.945,83.025},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.211,3.211,10.29},false},
  {'COL_Veg_055','Block',{-123.036,10.652,28.232},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.404,2.404,7.704},false},
  {'COL_Veg_056','Block',{126.661,11.064,-21.522},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.66,2.66,8.527},false},
  {'COL_Veg_057','Block',{-88.376,10.98,37.367},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.608,2.608,8.359},false},
  {'COL_Veg_058','Block',{-69.627,10.811,-10.815},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.503,2.503,8.022},false},
  {'COL_Veg_059','Block',{98.059,10.983,72.77},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.61,2.61,8.366},false},
  {'COL_Veg_060','Block',{120.015,11.97,1.74},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.226,3.226,10.341},false},
  {'COL_Veg_061','Block',{-71.203,12.893,37.052},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.802,3.802,12.185},false},
  {'COL_Veg_062','Block',{-78.719,12.007,51.304},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.249,3.249,10.414},false},
  {'COL_Veg_063','Block',{59.403,13.028,-68.304},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.886,3.886,12.457},false},
  {'COL_Veg_064','Block',{-44.816,13.592,54.89},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.238,4.238,13.585},false},
  {'COL_Veg_065','Block',{58.22,13.263,99.348},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.033,4.033,12.925},false},
  {'COL_Veg_066','Block',{29.477,13.719,-65.729},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.318,4.318,13.839},false},
  {'COL_Veg_067','Block',{-63.289,12.273,99.527},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.415,3.415,10.947},false},
  {'COL_Veg_068','Block',{-67.716,13.549,-52.771},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.212,4.212,13.499},false},
  {'COL_Veg_069','Block',{-99.628,14.191,-76.657},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.838,2.838,14.781},false},
  {'COL_Veg_070','Block',{30.135,13.422,131.287},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.543,2.543,13.244},false},
  {'COL_Veg_071','Block',{17.16,15.489,134.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.336,3.336,17.377},false},
  {'COL_Veg_072','Block',{141.737,13.327,-21.922},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.506,2.506,13.053},false},
  {'COL_Veg_073','Block',{65.23,14.204,118.774},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.843,2.843,14.808},false},
  {'COL_Veg_074','Block',{48.473,14.923,-156.845},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.119,3.119,16.246},false},
  {'COL_Veg_075','Block',{84.112,14.694,-90.945},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.031,3.031,15.788},false},
  {'COL_Veg_076','Block',{134.551,15.017,40.478},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.155,3.155,16.434},false},
  {'COL_Veg_077','Block',{-14.815,15.009,-152.111},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.152,3.152,16.418},false},
  {'COL_Veg_078','Block',{131.292,13.788,24.429},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.683,2.683,13.977},false},
  {'COL_Veg_079','Block',{-138.643,13.948,43.871},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.745,2.745,14.297},false},
  {'COL_Veg_080','Block',{-65.826,13.231,-149.763},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.47,2.47,12.863},false},
  {'COL_Veg_081','Block',{141.375,14.444,27.821},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.935,2.935,15.287},false},
  {'COL_Veg_082','Block',{-128.773,13.5,-89.174},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.573,2.573,13.4},false},
  {'COL_Veg_083','Block',{-189.527,14.853,45.77},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.092,3.092,16.106},false},
  {'COL_Veg_084','Block',{-26.981,13.611,135.762},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.616,2.616,13.623},false},
  {'COL_Veg_085','Block',{-138.222,14.476,-66.911},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.948,2.948,15.353},false},
  {'COL_Veg_086','Block',{-141.807,14.613,23.79},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,15.625},false},
  {'COL_Veg_087','Block',{-182.31,13.486,-4.109},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.568,2.568,13.372},false},
  {'COL_Veg_088','Block',{-200.405,13.561,41.466},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.596,2.596,13.522},false},
  {'COL_Veg_089','Block',{-124.61,13.825,39.99},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.697,2.697,14.049},false},
  {'COL_Veg_090','Block',{-109.665,13.484,75.38},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.567,2.567,13.368},false},
  {'COL_Veg_091','Block',{100.332,13.775,-137.636},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.678,2.678,13.949},false},
  {'COL_Veg_092','Block',{48.115,13.744,-79.29},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.667,2.667,13.889},false},
  {'COL_Veg_093','Block',{-52.724,12.352,-23.509},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.132,2.132,11.104},false},
  {'COL_Veg_094','Block',{-139.016,11.938,-21.693},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.973,1.973,10.277},false},
  {'COL_Veg_095','Block',{-35.625,12.78,-71.861},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.296,2.296,11.96},false},
  {'COL_Veg_096','Block',{111.986,13.319,-99.951},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.503,2.503,13.038},false},
  {'COL_Veg_097','Block',{54.903,12.17,123.311},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.062,2.062,10.74},false},
  {'COL_Veg_098','Block',{-118.11,12.319,84.227},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.119,2.119,11.037},false},
  {'COL_Veg_099','Block',{75.064,12.562,102.498},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.213,2.213,11.524},false},
  {'COL_Veg_100','Block',{-124.722,13.166,51.157},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.444,2.444,12.732},false},
  {'COL_Veg_101','Block',{124.826,12.619,-31.899},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.235,2.235,11.639},false},
  {'COL_Veg_102','Block',{-42.171,13.088,-32.267},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.415,2.415,12.576},false},
  {'COL_Veg_103','Block',{-141.84,13.268,-49.92},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.484,2.484,12.935},false},
  {'COL_Veg_104','Block',{-52.24,12.608,-80.988},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.23,2.23,11.617},false},
  {'COL_Veg_105','Block',{-48.704,13.49,-59.721},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.569,2.569,13.38},false},
  {'COL_Veg_106','Block',{-121.851,13.535,-27.738},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.586,2.586,13.471},false},
  {'COL_Veg_107','Block',{-182.656,12.772,36.938},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.293,2.293,11.944},false},
  {'COL_Veg_108','Block',{99.44,12.608,-119.554},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.23,2.23,11.616},false},
  {'COL_Veg_109','Block',{-49.668,13.521,89.953},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.581,2.581,13.441},false},
  {'COL_Veg_110','Block',{-106.128,13.427,97.788},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.545,2.545,13.254},false},
  {'COL_Veg_111','Block',{-25.371,12.605,-48.016},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.229,2.229,11.61},false},
  {'COL_Veg_112','Block',{118.951,12.091,38.303},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.032,2.032,10.582},false},
  {'COL_Veg_113','Block',{-207.545,13.041,30.584},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.397,2.397,12.482},false},
  {'COL_Veg_114','Block',{-74.582,11.907,-66.068},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.961,1.961,10.214},false},
  {'COL_Veg_115','Block',{-50.939,12.995,-43.785},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.379,2.379,12.391},false},
  {'COL_Veg_116','Block',{-116.366,12.139,-64.236},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.05,2.05,10.678},false},
  {'COL_Veg_117','Block',{94.488,11.128,86.185},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.701,2.701,8.657},false},
  {'COL_Veg_118','Block',{-63.0,11.573,84.307},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.979,2.979,9.547},false},
  {'COL_Veg_119','Block',{-51.081,11.056,-9.813},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.656,2.656,8.512},false},
  {'COL_Veg_120','Block',{-90.795,11.271,-64.395},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.79,2.79,8.942},false},
  {'COL_Veg_121','Block',{-97.447,11.137,76.122},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.706,2.706,8.674},false},
  {'COL_Veg_122','Block',{-41.329,12.037,121.519},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.268,3.268,10.473},false},
  {'COL_Veg_123','Block',{97.732,12.233,-18.745},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.39,3.39,10.867},false},
  {'COL_Veg_124','Block',{-32.425,12.504,94.792},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.559,3.559,11.408},false},
  {'COL_Veg_125','Block',{-96.0,18.3,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.384,9.384,23.0},false},
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
  {'LETREIRO_Ilha',{-236.0,33.0,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ILHA DOS PORTAIS',['alcance']=240}},
  {'LETREIRO_Loja',{61.629,34.1,-28.738},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='LOJA DE MOCHILAS',['alcance']=170}},
  {'LETREIRO_Portal1',{-223.003,33.0,47.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='NARUTO',['alcance']=150}},
  {'LETREIRO_Portal2',{-251.456,33.0,46.715},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='DRAGON BALL',['alcance']=150}},
  {'LETREIRO_Portal3',{-271.233,33.0,26.235},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='SHADOW GARDEN',['alcance']=150}},
  {'LETREIRO_Portal4',{-271.233,33.0,-2.235},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='DEMON SLAYER',['alcance']=150}},
  {'LETREIRO_Portal5',{-251.456,33.0,-22.715},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ONE PIECE',['alcance']=150}},
  {'LETREIRO_Portal6',{-223.003,33.0,-23.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ONE PUNCH MAN',['alcance']=150}},
  {'LETREIRO_Ranking',{62.816,45.6,52.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='TABUAS DOS CAMPEOES',['alcance']=190}},
  {'NPC_Ignis',{-0.9,7.02,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['npc']='Ignis',['alvo']='workspace.NPCs.Ignis (Root)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'NPC_Vendedor',{76.583,8.2,-35.711},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{['kind']='npc',['olha']='porta'}},
  {'PLAYER_INTERACT_Ignis',{-0.9,7.02,-46.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'PLAYER_Loja',{71.146,8.2,-33.175},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{['kind']='padloja'}},
  {'PORTAL_DemonSlayer',{-274.385,19.4,-3.509},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{['destino']='DemonSlayer',['raio']=7.5,['touch']=true,['vm_portal']='DemonSlayer'}},
  {'PORTAL_DragonBall',{-252.839,19.4,49.821},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{['destino']='DragonBall',['raio']=7.5,['touch']=true,['vm_portal']='DragonBall'}},
  {'PORTAL_Naruto',{-221.84,19.4,50.903},{-0.94,0.0,0.342},{0.342,0.0,0.94},{['destino']='Naruto',['raio']=7.5,['touch']=true,['vm_portal']='Naruto'}},
  {'PORTAL_OnePiece',{-252.839,19.4,-25.821},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{['destino']='OnePiece',['raio']=7.5,['touch']=true,['vm_portal']='OnePiece'}},
  {'PORTAL_OnePunchMan',{-221.84,19.4,-26.903},{0.94,0.0,0.342},{0.342,0.0,-0.94},{['destino']='OnePunchMan',['raio']=7.5,['touch']=true,['vm_portal']='OnePunchMan'}},
  {'PORTAL_ShadowGarden',{-274.385,19.4,27.509},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{['destino']='ShadowGarden',['raio']=7.5,['touch']=true,['vm_portal']='ShadowGarden'}},
  {'SAFE_IlhaPonte',{-159.0,7.2,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['kind']='safe'}},
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
  {'VFX_Brazier_IsleBr_142_-1',{-142.0,10.6,6.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_142_1',{-142.0,10.6,17.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_176_-1',{-176.0,10.6,6.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_176_1',{-176.0,10.6,17.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleMain_-1',{-136.0,24.65,3.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleMain_1',{-136.0,24.65,20.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P1_-1',{-218.477,12.16,40.098},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P1_1',{-231.363,12.16,44.787},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P2_-1',{-242.913,12.16,44.384},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P2_1',{-255.44,12.16,38.807},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P3_-1',{-263.469,12.16,30.493},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P3_1',{-268.606,12.16,17.779},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P4_-1',{-268.606,12.16,6.221},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P4_1',{-263.469,12.16,-6.493},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P5_-1',{-255.44,12.16,-14.807},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P5_1',{-242.913,12.16,-20.384},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P6_-1',{-231.363,12.16,-20.787},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P6_1',{-218.477,12.16,-16.098},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Rank_-1',{45.799,12.2,78.897},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Rank_1',{85.654,12.2,31.404},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Shop_-1',{62.351,11.0,-19.144},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Shop_1',{54.744,11.0,-35.458},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_-1_-1',{-14.9,14.3,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_-1_1',{14.9,14.3,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_1_-1',{-14.9,14.3,52.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_1_1',{14.9,14.3,52.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Dust_Forge',{0.0,15.0,-50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=3}},
  {'VFX_Dust_Isle',{-236.0,15.0,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=4}},
  {'VFX_Dust_Plaza',{0.0,14.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=6}},
  {'VFX_Hammer_Embers',{112.0,7.4,-62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=3}},
  {'VFX_Hammer_Smoke',{106.0,7.8,-66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Hearth_Ember_C',{0.0,10.2,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=8}},
  {'VFX_Hearth_Fire_C',{0.0,8.6,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=16,['size']=3.4}},
  {'VFX_Leaves_ancient_15',{-96.0,35.32,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=16.56}},
  {'VFX_Leaves_oak1_0',{115.137,18.358,-17.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.710870774116368}},
  {'VFX_Leaves_oak1_1',{-88.172,18.777,65.376},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.954459638709261}},
  {'VFX_Leaves_oak1_2',{-62.191,20.758,-34.075},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=8.104887975355677}},
  {'VFX_Leaves_oak1_3',{-58.219,17.527,136.504},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.228643267859351}},
  {'VFX_Leaves_oak1_4',{138.777,19.367,-70.399},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.296960565702595}},
  {'VFX_Leaves_oak1_5',{-94.173,18.551,-50.413},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.823376383583922}},
  {'VFX_Leaves_oak1_6',{111.817,20.182,98.328},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.770129900290916}},
  {'VFX_Leaves_oak1_7',{-16.157,17.887,88.005},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.437563706228608}},
  {'VFX_Leaves_oak2_10',{126.661,18.548,-21.522},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.82162558804363}},
  {'VFX_Leaves_oak2_8',{-76.393,20.963,20.439},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=8.223567416448105}},
  {'VFX_Leaves_oak2_9',{-37.829,21.011,34.794},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=8.251737340945796}},
  {'VFX_Leaves_oak3_11',{-71.203,19.391,37.052},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.311065734661212}},
  {'VFX_Leaves_oak3_12',{-63.289,18.111,99.527},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.567958844610393}},
  {'VFX_Leaves_oakG_13',{94.488,17.534,86.185},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.232821263457283}},
  {'VFX_Leaves_oakG_14',{97.732,20.275,-18.745},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.824062140607545}},
  {'VFX_Rune_IsleStone',{-236.0,10.0,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=4}},
  {'VFX_Rune_Portal1',{-224.713,8.6,43.01},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal2',{-249.422,8.6,42.147},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal3',{-266.597,8.6,24.362},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal4',{-266.597,8.6,-0.362},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal5',{-249.422,8.6,-18.147},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal6',{-224.713,8.6,-19.01},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
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
  {'L_P_DemonSlayer_Lamp_1','POINT',{-267.28,11.44,3.73},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Lamp_2','POINT',{-264.245,11.44,-3.78},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Pad','POINT',{-268.451,12.7,-1.111},{255,129,129},12.6,0.71,false,false},
  {'L_P_DragonBall_Pad','POINT',{-250.236,12.7,43.974},{97,179,255},12.6,0.71,false,false},
  {'L_P_Naruto_Pad','POINT',{-224.029,12.7,44.889},{255,196,118},12.6,0.71,false,false},
  {'L_P_OnePiece_Pad','POINT',{-250.236,12.7,-19.974},{137,196,255},12.6,0.71,false,false},
  {'L_P_OnePunchMan_Pad','POINT',{-224.029,12.7,-20.889},{255,229,144},12.6,0.71,false,false},
  {'L_P_ShadowGarden_Candles','POINT',{-265.088,18.41,36.371},{203,137,255},9.5,0.49,false,false},
  {'L_P_ShadowGarden_Moon','POINT',{-272.087,31.02,26.257},{196,129,255},10.7,0.56,false,false},
  {'L_P_ShadowGarden_Pad','POINT',{-268.451,12.7,25.111},{206,137,255},12.6,0.71,false,false},
  {'L_Portal_DemonSlayer','POINT',{-272.16,19.4,-2.61},{255,129,129},14.0,1.0,false,false},
  {'L_Portal_DragonBall','POINT',{-251.863,19.4,47.628},{97,179,255},14.0,1.0,false,false},
  {'L_Portal_Naruto','POINT',{-222.661,19.4,48.648},{255,196,118},14.0,1.0,false,false},
  {'L_Portal_OnePiece','POINT',{-251.863,19.4,-23.628},{137,196,255},14.0,1.0,false,false},
  {'L_Portal_OnePunchMan','POINT',{-222.661,19.4,-24.648},{255,229,144},14.0,1.0,false,false},
  {'L_Portal_ShadowGarden','POINT',{-272.16,19.4,26.61},{206,137,255},14.0,1.0,false,false},
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
  {'L_SN_Brazier_IsleBr_142_-1','POINT',{-142.0,11.2,6.4},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_142_1','POINT',{-142.0,11.2,17.6},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_176_-1','POINT',{-176.0,11.2,6.4},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_176_1','POINT',{-176.0,11.2,17.6},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleMain_-1','POINT',{-136.0,25.25,3.4},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleMain_1','POINT',{-136.0,25.25,20.6},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P1_-1','POINT',{-218.477,12.76,40.098},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P1_1','POINT',{-231.363,12.76,44.787},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P2_-1','POINT',{-242.913,12.76,44.384},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P2_1','POINT',{-255.44,12.76,38.807},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P3_-1','POINT',{-263.469,12.76,30.493},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P3_1','POINT',{-268.606,12.76,17.779},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P4_-1','POINT',{-268.606,12.76,6.221},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P4_1','POINT',{-263.469,12.76,-6.493},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P5_-1','POINT',{-255.44,12.76,-14.807},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P5_1','POINT',{-242.913,12.76,-20.384},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P6_-1','POINT',{-231.363,12.76,-20.787},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P6_1','POINT',{-218.477,12.76,-16.098},{255,140,60},16.0,1.2,false,true},
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
  {'L_SN_IsleStone','POINT',{-236.0,27.75,12.0},{255,218,160},14.3,0.86,false,false},
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
  {'SAFE_IlhaPonte',{-159.0,7.2,12.0}},
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
  {'SAFE_IlhaPatio',{-222.0,7.0,12.0}},
  {'SAFE_TrilhaOeste',{-100.0,6.8,10.0}},
  {'SAFE_Portal1',{-225.739,8.6,40.191}},
  {'SAFE_Portal2',{-248.202,9.1,39.406}},
  {'SAFE_Portal3',{-263.816,8.2,23.238}},
  {'SAFE_Portal4',{-263.816,8.65,0.762}},
  {'SAFE_Portal5',{-248.202,8.8,-15.406}},
  {'SAFE_Portal6',{-225.739,8.7,-16.191}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(480,4,420); v.Position = Vector3.new(-80.0,-25.0,29.0) + ROOT_OFFSET
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
  {1, 'Naruto', 1, Vector3.new(-222.285, 19.400, 49.682), Vector3.new(-0.3420, 0, -0.9397)},
  {2, 'DragonBall', 2, Vector3.new(-252.310, 19.400, 48.633), Vector3.new(0.4067, 0, -0.9135)},
  {3, 'ShadowGarden', 3, Vector3.new(-273.180, 19.400, 27.022), Vector3.new(0.9272, 0, -0.3746)},
  {4, 'DemonSlayer', 4, Vector3.new(-273.180, 19.400, -3.022), Vector3.new(0.9272, 0, 0.3746)},
  {5, 'OnePiece', 5, Vector3.new(-252.310, 19.400, -24.633), Vector3.new(0.4067, 0, 0.9135)},
  {6, 'OnePunchMan', 6, Vector3.new(-222.285, 19.400, -25.682), Vector3.new(-0.3420, 0, 0.9397)},
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
--   LobbyLayout.PortalIsland = Vector3.new(-222.0, 10.5, 12.0)
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
