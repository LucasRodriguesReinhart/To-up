-- montar_lobby_santuario.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID d9f901f2
-- 1) Importe os FBX LOBBY_SN_*_d9f901.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador
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
local EXPORT_ID = 'd9f901f2'
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
  ['P_DB_Swirl'] = 'rbxassetid://88043972333635',  -- textures/T_swirl_db_v6.png (espiral, UV do disco)
  ['P_DS_Swirl'] = 'rbxassetid://103760430353568',  -- textures/T_swirl_ds_v5.png (espiral, UV do disco)
  ['P_Naruto_Swirl'] = 'rbxassetid://130296231803004',  -- textures/T_swirl_naruto_v5.png (espiral, UV do disco)
  ['P_OPM_Swirl'] = 'rbxassetid://114530148175372',  -- textures/T_swirl_opm_v6.png (espiral, UV do disco)
  ['P_OP_Swirl'] = 'rbxassetid://114350792676911',  -- textures/T_swirl_op_v4.png (espiral, UV do disco)
  ['P_Shadow_Swirl'] = 'rbxassetid://82596023817609',  -- textures/T_swirl_shadow_v4.png (espiral, UV do disco)
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
  ['snb_anvil_1'] = 'rbxassetid://84601895885458',  -- textures/SNB_Anvil_1.png (1.0 studs por repeticao)
  ['snb_anvil_2'] = 'rbxassetid://127033870800530',  -- textures/SNB_Anvil_2.png (1.0 studs por repeticao)
  ['snb_anvil_3'] = 'rbxassetid://80228695499599',  -- textures/SNB_Anvil_3.png (1.0 studs por repeticao)
  ['snb_anvil_4'] = 'rbxassetid://109256148628133',  -- textures/SNB_Anvil_4.png (1.0 studs por repeticao)
  ['snb_anvil_5'] = 'rbxassetid://95373876436942',  -- textures/SNB_Anvil_5.png (1.0 studs por repeticao)
  ['snb_anvil_6'] = 'rbxassetid://118596911413577',  -- textures/SNB_Anvil_6.png (1.0 studs por repeticao)
  ['snb_anvil_7'] = 'rbxassetid://82538457932340',  -- textures/SNB_Anvil_7.png (1.0 studs por repeticao)
  ['snb_anvil_8'] = 'rbxassetid://118055237099115',  -- textures/SNB_Anvil_8.png (1.0 studs por repeticao)
  ['snb_avenue'] = 'rbxassetid://70720474494449',  -- textures/SNB_Avenue.png (1.0 studs por repeticao)
  ['snb_bridge_1'] = 'rbxassetid://111715411583279',  -- textures/SNB_Bridge_1.png (1.0 studs por repeticao)
  ['snb_bridge_2'] = 'rbxassetid://82926581980307',  -- textures/SNB_Bridge_2.png (1.0 studs por repeticao)
  ['snb_dais'] = 'rbxassetid://113306458187994',  -- textures/SNB_Dais.png (1.0 studs por repeticao)
  ['snb_gate'] = 'rbxassetid://96620215199058',  -- textures/SNB_Gate.png (1.0 studs por repeticao)
  ['snb_ground_1'] = 'rbxassetid://76198799651228',  -- textures/SNB_Ground_1.png (1.0 studs por repeticao)
  ['snb_ground_2'] = 'rbxassetid://87833932055932',  -- textures/SNB_Ground_2.png (1.0 studs por repeticao)
  ['snb_ground_3'] = 'rbxassetid://105952539261633',  -- textures/SNB_Ground_3.png (1.0 studs por repeticao)
  ['snb_hall_1'] = 'rbxassetid://112329069365420',  -- textures/SNB_Hall_1.png (1.0 studs por repeticao)
  ['snb_hall_2'] = 'rbxassetid://111047594753469',  -- textures/SNB_Hall_2.png (1.0 studs por repeticao)
  ['snb_hammer_1'] = 'rbxassetid://139394458991535',  -- textures/SNB_Hammer_1.png (1.0 studs por repeticao)
  ['snb_hammer_2'] = 'rbxassetid://94932824579467',  -- textures/SNB_Hammer_2.png (1.0 studs por repeticao)
  ['snb_isle'] = 'rbxassetid://96793844729151',  -- textures/SNB_Isle.png (1.0 studs por repeticao)
  ['snb_islebridge'] = 'rbxassetid://91719712721855',  -- textures/SNB_IsleBridge.png (1.0 studs por repeticao)
  ['snb_plaza_1'] = 'rbxassetid://89372750609893',  -- textures/SNB_Plaza_1.png (1.0 studs por repeticao)
  ['snb_plaza_2'] = 'rbxassetid://106578643234905',  -- textures/SNB_Plaza_2.png (1.0 studs por repeticao)
  ['snb_rank_1'] = 'rbxassetid://123051482628029',  -- textures/SNB_Rank_1.png (1.0 studs por repeticao)
  ['snb_rank_2'] = 'rbxassetid://80707222440030',  -- textures/SNB_Rank_2.png (1.0 studs por repeticao)
  ['snb_ruins'] = 'rbxassetid://123781776033146',  -- textures/SNB_Ruins.png (1.0 studs por repeticao)
  ['snb_shop_1'] = 'rbxassetid://81206903593299',  -- textures/SNB_Shop_1.png (1.0 studs por repeticao)
  ['snb_shop_2'] = 'rbxassetid://82842270852407',  -- textures/SNB_Shop_2.png (1.0 studs por repeticao)
  ['snb_shopin'] = 'rbxassetid://131203240240500',  -- textures/SNB_ShopIn.png (1.0 studs por repeticao)
  ['snb_shore'] = 'rbxassetid://74428199556704',  -- textures/SNB_Shore.png (1.0 studs por repeticao)
  ['snb_spawn'] = 'rbxassetid://81511138149942',  -- textures/SNB_Spawn.png (1.0 studs por repeticao)
  ['snb_tufts'] = 'rbxassetid://103966444933182',  -- textures/SNB_Tufts.png (1.0 studs por repeticao)
  ['snb_veg_ancient'] = 'rbxassetid://101744868627935',  -- textures/SNB_Veg_ancient.png (1.0 studs por repeticao)
  ['snb_veg_bush1'] = 'rbxassetid://115952741162244',  -- textures/SNB_Veg_bush1.png (1.0 studs por repeticao)
  ['snb_veg_bushf'] = 'rbxassetid://76559025415368',  -- textures/SNB_Veg_bushF.png (1.0 studs por repeticao)
  ['snb_veg_oak1'] = 'rbxassetid://125064883914035',  -- textures/SNB_Veg_oak1.png (1.0 studs por repeticao)
  ['snb_veg_oak2'] = 'rbxassetid://93212471047107',  -- textures/SNB_Veg_oak2.png (1.0 studs por repeticao)
  ['snb_veg_oak3'] = 'rbxassetid://83958039033080',  -- textures/SNB_Veg_oak3.png (1.0 studs por repeticao)
  ['snb_veg_oakg'] = 'rbxassetid://101270400093925',  -- textures/SNB_Veg_oakG.png (1.0 studs por repeticao)
  ['snb_veg_pine1'] = 'rbxassetid://104941548852522',  -- textures/SNB_Veg_pine1.png (1.0 studs por repeticao)
  ['snb_veg_pine2'] = 'rbxassetid://75483774030830',  -- textures/SNB_Veg_pine2.png (1.0 studs por repeticao)
  ['stone'] = 'rbxassetid://88967435457544',  -- textures/T_stone_v3.png (6.0 studs por repeticao)
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
  ['wb_water'] = 'rbxassetid://90298974250965',  -- textures/WB_water_v2.png (20.0 studs por repeticao)
  ['wb_window'] = 'rbxassetid://102213621140219',  -- textures/WB_window_v2.png (2.4 studs por repeticao)
  ['wood'] = 'rbxassetid://72759716465697',  -- textures/T_wood_v3.png (5.0 studs por repeticao)
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
  ['SNB_Bridge_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_bridge_1', w = nil},
  ['SNB_Bridge_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_bridge_2', w = nil},
  ['SNB_Dais'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_dais', w = nil},
  ['SNB_Gate'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_gate', w = nil},
  ['SNB_Ground_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_1', w = nil},
  ['SNB_Ground_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_2', w = nil},
  ['SNB_Ground_3'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_ground_3', w = nil},
  ['SNB_Hall_1'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hall_1', w = nil},
  ['SNB_Hall_2'] = {c = Color3.fromRGB(255,255,255), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'snb_hall_2', w = nil},
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
  ['SN_Lava'] = {c = Color3.fromRGB(255,110,30), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SN_LavaHot'] = {c = Color3.fromRGB(255,214,110), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
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
  ['WB_Window'] = {c = Color3.fromRGB(236,176,86), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = 'wb_window', w = nil},
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
local FBX = {[1]='LOBBY_SN_02_TERRAIN_d9f901.fbx', [2]='LOBBY_SN_03_TOWN_d9f901.fbx', [3]='LOBBY_SN_04_FORGE_d9f901.fbx', [4]='LOBBY_SN_05_SERVICES_d9f901.fbx', [5]='LOBBY_SN_06_PORTALS_d9f901.fbx', [6]='LOBBY_SN_07_EXIT_d9f901.fbx', [7]='LOBBY_SN_09_VEGETATION_d9f901.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['WB_Ter_Ground__SNB_Ground_1']={-157.591,6.886,8.755,238.718,0.173,108.11,1,true,'SNB_Ground_1','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g15_15']={-65.0,6.871,64.2,130.0,0.653,132.24,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g15_16']={-15.786,6.968,-41.467,268.429,0.486,245.067,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g16_15']={22.816,7.013,74.04,214.102,0.776,151.92,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_01__SNB_Ground_2_g16_16']={74.0,6.98,-23.324,152.0,0.481,208.781,1,true,'SNB_Ground_2','',''},
  ['WB_Ter_Ground_02__SNB_Ground_3']={54.247,6.917,-3.441,60.833,0.114,102.068,1,true,'SNB_Ground_3','',''},
  ['WB_Ter_Shore__SNB_Shore_g14_15']={-185.807,-4.6,-0.03,197.025,22.8,258.919,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g14_16']={-192.893,-4.6,-59.353,131.786,22.8,124.672,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g15_14']={-0.197,-4.6,142.696,195.409,22.8,32.508,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g15_17']={-62.888,-4.6,-149.321,125.776,22.8,46.204,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g16_17']={64.804,-4.6,-143.427,129.608,22.8,58.854,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g17_15']={141.053,-4.6,49.683,29.185,22.8,101.719,1,true,'SNB_Shore','',''},
  ['WB_Ter_Shore__SNB_Shore_g17_16']={121.762,-4.6,1.526,68.936,22.8,255.621,1,true,'SNB_Shore','',''},
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
  ['WB_Town_Plaza_01__SNB_Plaza_2']={0.0,6.72,0.0,82.8,1.16,82.8,2,true,'SNB_Plaza_2','',''},
  ['WB_Town_Plaza_02__SN_Rune']={-1.706,7.1,0.0,73.954,0.38,77.6,2,false,'SN_Rune','',''},
  ['WB_Frg_Anvil__SNB_Anvil_1']={-42.809,38.604,-111.784,79.613,63.933,58.496,3,true,'SNB_Anvil_1','','SN_Forja'},
  ['WB_Frg_Anvil_01__SNB_Anvil_2']={0.0,45.123,-118.0,69.399,49.245,39.8,3,true,'SNB_Anvil_2','','SN_Forja'},
  ['WB_Frg_Anvil_02__SNB_Anvil_3']={0.0,24.361,-112.2,148.6,34.723,60.2,3,true,'SNB_Anvil_3','','SN_Forja'},
  ['WB_Frg_Anvil_03__SNB_Anvil_4']={0.0,11.055,-117.0,142.6,0.41,44.6,3,true,'SNB_Anvil_4','','SN_Forja'},
  ['WB_Frg_Anvil_04__SNB_Anvil_5']={0.0,12.855,-117.0,136.6,0.41,38.6,3,true,'SNB_Anvil_5','','SN_Forja'},
  ['WB_Frg_Anvil_05__SNB_Anvil_6']={0.0,38.22,-110.0,142.0,62.56,58.0,3,true,'SNB_Anvil_6','','SN_Forja'},
  ['WB_Frg_Anvil_06__SNB_Anvil_7']={1.0,67.413,-116.502,84.0,5.574,35.996,3,true,'SNB_Anvil_7','','SN_Forja'},
  ['WB_Frg_Anvil_07__SNB_Anvil_8']={37.771,38.754,-113.225,84.571,64.079,55.547,3,true,'SNB_Anvil_8','','SN_Forja'},
  ['WB_Frg_Anvil_08__SN_CrystalAmber']={-63.326,14.979,-93.142,4.282,4.586,2.902,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Anvil_09__SN_CrystalBlue']={57.837,15.399,-116.748,20.358,5.42,52.025,3,false,'SN_CrystalBlue','','SN_Forja'},
  ['WB_Frg_Anvil_10__SN_Lava']={-2.743,33.9,-113.247,29.67,53.2,43.845,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Anvil_11__SN_LavaHot']={19.503,38.57,-113.291,53.794,62.66,44.097,3,false,'SN_LavaHot','','SN_Forja'},
  ['WB_Frg_Anvil_12__SN_Rune']={0.025,39.891,-118.0,70.17,27.318,34.76,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Frg_Anvil_13__WB_Fire']={0.0,17.36,-95.0,141.653,2.28,1.509,3,false,'WB_Fire','','SN_Forja'},
  ['WB_Frg_Anvil_14__WB_FireCore']={0.0,17.1,-95.0,140.9,1.3,0.779,3,false,'WB_FireCore','','SN_Forja'},
  ['WB_Frg_Hall__SNB_Hall_1']={0.0,23.543,-60.45,49.2,34.406,42.1,3,true,'SNB_Hall_1','','SN_Forja'},
  ['WB_Frg_Hall_01__SNB_Hall_2']={0.136,27.765,-78.863,36.688,42.491,27.393,3,true,'SNB_Hall_2','','SN_Forja'},
  ['WB_Frg_Hall_02__SN_Lava']={0.0,20.755,-67.597,40.8,28.87,49.595,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Hall_03__SN_LavaHot']={2.163,7.565,-82.067,8.726,1.77,20.424,3,false,'SN_LavaHot','','SN_Forja'},
  ['WB_Frg_Hall_04__SN_Rune']={-0.021,20.692,-61.169,31.258,9.456,16.175,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Frg_Hall_05__WB_Fire']={0.0,10.24,-57.464,47.653,4.12,34.437,3,false,'WB_Fire','','SN_Forja'},
  ['WB_Frg_Hall_06__WB_FireCore']={0.0,9.92,-57.353,46.9,3.26,33.485,3,false,'WB_FireCore','','SN_Forja'},
  ['WB_Frg_Hall_07__WB_Ingot']={13.65,8.735,-60.4,1.9,4.03,7.6,3,false,'WB_Ingot','','SN_Forja'},
  ['WB_Frg_Hall_08__WB_Water']={-12.6,9.175,-58.4,2.36,0.15,2.36,3,false,'WB_Water','','SN_Forja'},
  ['WB_Frg_Hammer__SNB_Hammer_1']={107.517,11.733,-65.69,49.905,28.121,49.395,3,true,'SNB_Hammer_1','','SN_Forja'},
  ['WB_Frg_Hammer_01__SNB_Hammer_2']={125.037,57.103,-72.878,67.529,97.011,29.199,3,true,'SNB_Hammer_2','','SN_Forja'},
  ['WB_Frg_Hammer_02__SN_CrystalAmber']={156.355,104.867,-81.039,3.557,3.74,3.74,3,false,'SN_CrystalAmber','','SN_Forja'},
  ['WB_Frg_Hammer_03__SN_Lava']={104.597,7.06,-63.974,74.151,0.52,78.577,3,false,'SN_Lava','','SN_Forja'},
  ['WB_Frg_Hammer_04__SN_Rune']={115.585,11.216,-69.489,5.639,4.268,14.731,3,false,'SN_Rune','','SN_Forja'},
  ['WB_Rank_Tablets__SNB_Rank_1']={64.152,28.498,60.596,62.182,44.096,54.238,4,true,'SNB_Rank_1','','SN_Tabuas'},
  ['WB_Rank_Tablets_01__SNB_Rank_2']={63.639,28.346,53.365,65.047,44.292,70.061,4,true,'SNB_Rank_2','','SN_Tabuas'},
  ['WB_Rank_Tablets_02__SN_CrystalBlue']={57.83,9.243,49.348,44.103,3.877,53.989,4,false,'SN_CrystalBlue','','SN_Tabuas'},
  ['WB_Rank_Tablets_03__SN_Rune']={68.79,27.608,55.331,41.199,32.104,42.284,4,false,'SN_Rune','','SN_Tabuas'},
  ['WB_Rank_Tablets_04__WB_Fire']={65.727,12.56,55.151,41.826,2.28,49.399,4,false,'WB_Fire','','SN_Tabuas'},
  ['WB_Rank_Tablets_05__WB_FireCore']={65.727,12.3,55.151,41.036,1.3,48.621,4,false,'WB_FireCore','','SN_Tabuas'},
  ['WB_Shop_Inside__SNB_ShopIn']={75.164,14.915,-35.054,22.563,13.67,28.101,4,true,'SNB_ShopIn','','SN_Loja'},
  ['WB_Shop_Inside_01__SN_CrystalBlue']={72.913,12.605,-45.115,1.587,1.974,1.57,4,false,'SN_CrystalBlue','','SN_Loja'},
  ['WB_Shop_Inside_02__WB_LampGlow']={72.958,15.625,-34.02,5.023,7.35,9.86,4,false,'WB_LampGlow','','SN_Loja'},
  ['WB_Shop_Temple__SNB_Shop_1']={72.686,19.46,-33.894,39.281,26.28,42.377,4,true,'SNB_Shop_1','','SN_Loja'},
  ['WB_Shop_Temple_01__SNB_Shop_2']={70.696,19.8,-39.129,34.23,25.6,38.383,4,true,'SNB_Shop_2','','SN_Loja'},
  ['WB_Shop_Temple_02__SN_CrystalAmber']={77.807,19.442,-15.34,0.748,0.864,0.864,4,false,'SN_CrystalAmber','','SN_Loja'},
  ['WB_Shop_Temple_03__WB_LampGlow']={61.121,19.52,-46.155,0.877,1.54,0.877,4,false,'WB_LampGlow','','SN_Loja'},
  ['WB_Shop_Temple_04__WB_Window']={75.677,15.7,-35.288,22.033,1.9,30.672,4,false,'WB_Window','','SN_Loja'},
  ['PORTAL_DemonSlayer_Swirl__P_DS_Swirl']={-257.539,16.264,-0.737,4.075,10.8,10.014,5,false,'P_DS_Swirl','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Emblem_Cream']={-257.812,17.448,-1.001,11.312,18.02,16.478,5,false,'Emblem_Cream','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Glow']={-256.924,16.264,-0.493,4.514,11.16,10.481,5,false,'P_DS_Glow','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Gravel']={-256.172,9.004,-0.19,21.317,2.039,23.382,5,false,'P_DS_Gravel','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Iron']={-256.672,17.799,-1.526,13.791,18.623,16.372,5,false,'P_DS_Iron','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Lacquer']={-258.817,17.769,-1.5,9.5,18.561,16.32,5,false,'P_DS_Lacquer','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Red']={-256.268,16.241,-1.658,12.442,14.014,15.009,5,false,'P_DS_Red','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Stone_DS_Rock']={-256.373,9.622,-0.271,22.087,3.348,24.414,5,false,'Stone_DS_Rock','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__Bark_Dark']={-258.324,14.402,8.339,2.541,13.116,2.382,5,false,'Bark_Dark','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicMid']={-259.191,20.037,8.031,8.095,4.838,4.385,5,false,'P_DS_GlicMid','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicTip']={-258.759,17.911,8.556,6.908,3.435,3.098,5,false,'P_DS_GlicTip','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_Glicinia']={-258.793,20.409,8.087,7.404,4.31,4.696,5,false,'P_DS_Glicinia','','PORTAL_DemonSlayer'},
  ['PORTAL_DragonBall_Frame__P_DB_Amber']={-238.286,16.006,43.597,17.48,14.599,9.086,5,false,'P_DB_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Ball_Amber']={-240.843,18.795,39.23,6.779,17.834,12.371,5,false,'P_DB_Ball_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Blue']={-239.078,10.506,40.96,17.243,6.411,16.001,5,false,'P_DB_Blue','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Floor']={-239.214,8.733,41.679,20.894,0.23,18.923,5,false,'P_DB_Floor','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Gold_Bright']={-239.829,16.271,40.053,14.801,15.999,13.564,5,false,'P_DB_Gold_Bright','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Rim_Glow']={-239.683,16.264,42.732,10.41,11.208,5.128,5,false,'P_DB_Rim_Glow','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Star_Red']={-240.72,18.011,39.717,6.098,17.08,13.402,5,false,'P_DB_Star_Red','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_White']={-239.214,17.284,41.679,20.749,19.969,18.779,5,false,'P_DB_White','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Swirl__P_DB_Swirl']={-239.829,16.264,43.061,9.866,10.8,4.394,5,false,'P_DB_Swirl','','PORTAL_DragonBall'},
  ['PORTAL_Naruto_Bandana__Leaf_Pine']={-213.648,8.642,45.183,19.288,1.852,12.411,5,false,'Leaf_Pine','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Metal_Dark']={-214.187,18.897,42.324,17.981,19.214,12.091,5,true,'Metal_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Cloth']={-214.517,19.228,42.277,18.769,15.124,12.07,5,true,'P_Naruto_Cloth','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Lacquer']={-214.516,18.164,42.416,18.326,19.385,11.62,5,true,'P_Naruto_Lacquer','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Rim_Glow']={-214.605,16.264,43.307,10.609,11.16,4.155,5,false,'P_Naruto_Rim_Glow','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Steel']={-212.78,17.167,39.954,10.148,19.291,8.333,5,true,'P_Naruto_Steel','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Stone']={-214.187,16.288,44.457,13.455,16.008,6.883,5,true,'P_Naruto_Stone','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Dark']={-214.765,14.86,42.867,23.919,14.04,21.853,5,true,'Stone_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Light']={-214.765,9.518,42.867,23.771,2.549,21.706,5,true,'Stone_Light','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Swirl__P_Naruto_Swirl']={-214.371,16.264,43.979,10.149,10.8,3.752,5,false,'P_Naruto_Swirl','','PORTAL_Naruto'},
  ['PORTAL_OnePiece_Pier__Emblem_Cream']={-237.761,20.421,-21.535,8.624,16.022,8.762,5,false,'Emblem_Cream','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Leaf_Palm']={-248.052,16.148,-21.551,5.877,1.408,5.914,5,false,'Leaf_Palm','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Metal_Dark']={-239.329,17.736,-17.937,21.891,18.87,18.134,5,false,'Metal_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Glow']={-239.595,16.264,-18.534,10.341,11.16,4.868,5,false,'P_OP_Glow','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Red']={-234.293,13.24,-25.387,1.919,1.944,1.118,5,false,'P_OP_Red','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Rope']={-239.331,16.392,-17.942,22.807,15.881,21.703,5,false,'Rope','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Dark']={-239.331,16.12,-17.95,22.724,17.28,21.688,5,false,'Wood_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Light']={-239.83,17.257,-19.061,17.287,16.88,8.166,5,false,'Wood_Light','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Plank']={-239.31,12.264,-17.686,21.355,8.577,20.692,5,false,'Wood_Plank','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Swirl__P_OP_Swirl']={-239.829,16.264,-19.061,9.866,10.8,4.394,5,false,'P_OP_Swirl','','PORTAL_OnePiece'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_ConcreteDark']={-214.174,16.457,-20.499,13.678,13.882,6.926,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Glow']={-214.174,24.63,-20.491,13.877,0.331,7.164,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Yellow']={-214.203,9.028,-20.521,15.301,0.576,7.939,5,false,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Swirl__P_OPM_Swirl']={-214.371,16.264,-19.979,10.149,10.8,3.752,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_SwirlBack__P_OPM_Swirl']={-213.805,16.264,-21.506,10.149,10.8,3.694,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteDark']={-214.765,17.578,-18.867,24.097,19.332,21.86,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteLight']={-214.765,16.678,-18.867,23.869,17.388,20.83,5,true,'P_OPM_ConcreteLight','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteMid']={-213.6,16.648,-19.994,13.051,16.584,11.542,5,true,'P_OPM_ConcreteMid','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Crater']={-214.098,16.364,-20.554,13.097,13.405,6.645,5,true,'P_OPM_Crater','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_DarkGlassT']={-214.174,24.502,-20.491,13.828,0.996,7.028,5,false,'P_OPM_DarkGlassT','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Glow']={-214.05,16.264,-20.574,11.517,11.693,5.97,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_RebarSteel']={-213.643,15.76,-20.528,13.989,13.62,9.423,5,true,'P_OPM_RebarSteel','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Red']={-214.813,25.102,-18.753,2.594,2.788,1.357,5,false,'P_OPM_Red','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Yellow']={-214.765,17.506,-18.867,24.14,19.044,21.903,5,true,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Core_Glow']={-254.389,19.356,23.692,8.654,15.484,17.307,5,false,'P_SG_Core_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Lilac_Glow']={-256.596,19.054,24.362,5.096,19.174,12.281,5,false,'P_SG_Lilac_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Moon_Glow']={-254.717,19.057,25.257,9.241,19.251,14.118,5,false,'P_SG_Moon_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Deadwood']={-258.525,11.302,15.532,1.599,6.162,1.696,5,false,'P_SG_Deadwood','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Marble']={-255.482,8.632,23.927,17.172,1.368,21.071,5,false,'P_SG_Marble','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Obsidian']={-257.658,19.13,24.818,9.653,21.212,18.167,5,false,'P_SG_Obsidian','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Rose']={-257.993,13.174,15.586,1.843,3.715,2.044,5,false,'P_SG_Rose','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Silver']={-255.482,19.468,23.927,17.358,22.018,21.257,5,false,'P_SG_Silver','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Violet']={-256.099,15.278,24.818,11.912,12.859,17.069,5,false,'P_SG_Violet','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_Shadow_Glow']={-257.124,16.264,24.575,4.514,11.16,10.481,5,false,'P_Shadow_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Swirl__P_Shadow_Swirl']={-257.539,16.264,24.737,4.075,10.8,10.014,5,false,'P_Shadow_Swirl','','PORTAL_ShadowGarden'},
  ['WB_Court_Dais__SNB_Dais']={-234.577,17.105,12.011,79.285,21.81,97.521,5,false,'SNB_Dais','',''},
  ['WB_Court_Dais_01__SN_CrystalAmber']={-227.325,10.308,12.976,49.376,5.137,87.927,5,false,'SN_CrystalAmber','',''},
  ['WB_Court_Dais_02__SN_CrystalBlue']={-244.113,9.948,-27.123,15.911,4.284,10.227,5,false,'SN_CrystalBlue','',''},
  ['WB_Court_Dais_03__SN_CrystalRed']={-265.935,10.459,-4.201,8.318,5.082,17.871,5,false,'SN_CrystalRed','',''},
  ['WB_Court_Dais_04__SN_CrystalViolet']={-265.31,10.287,28.021,9.622,4.83,16.312,5,false,'SN_CrystalViolet','',''},
  ['WB_Court_Dais_05__SN_Rune']={-235.96,7.91,12.0,63.943,0.333,84.664,5,false,'SN_Rune','',''},
  ['WB_Court_Dais_06__WB_Fire']={-232.461,12.52,11.97,42.451,2.28,55.652,5,false,'WB_Fire','',''},
  ['WB_Court_Dais_07__WB_FireCore']={-232.459,12.26,12.0,41.678,1.3,54.936,5,false,'WB_FireCore','',''},
  ['WB_Court_Isle__SNB_Isle']={-225.413,16.202,12.246,91.735,20.296,90.039,5,false,'SNB_Isle','',''},
  ['WB_Court_Isle_01__SN_CrystalAmber']={-244.647,18.125,29.875,41.069,23.68,39.521,5,false,'SN_CrystalAmber','',''},
  ['WB_Court_Isle_02__SN_CrystalBlue']={-259.282,9.431,9.77,13.209,6.452,68.127,5,false,'SN_CrystalBlue','',''},
  ['WB_Court_Isle_03__SN_RuneAmber']={-222.875,14.395,21.001,6.579,14.81,16.015,5,false,'SN_RuneAmber','',''},
  ['WB_Court_Isle_04__SN_RuneBlue']={-229.754,14.395,3.263,7.636,14.81,15.637,5,false,'SN_RuneBlue','',''},
  ['WB_Court_Isle_05__SN_RuneOrange']={-229.754,14.395,20.737,7.636,14.81,15.637,5,false,'SN_RuneOrange','',''},
  ['WB_Court_Isle_06__SN_RuneRed']={-234.875,14.395,8.558,15.836,14.81,7.112,5,false,'SN_RuneRed','',''},
  ['WB_Court_Isle_07__SN_RuneViolet']={-234.875,14.395,15.442,15.836,14.81,7.112,5,false,'SN_RuneViolet','',''},
  ['WB_Court_Isle_08__SN_RuneYellow']={-222.875,14.395,2.999,6.579,14.81,16.015,5,false,'SN_RuneYellow','',''},
  ['WB_Exit_Avenue__SNB_Avenue_0']={-0.093,15.726,117.28,41.522,19.052,57.56,6,true,'SNB_Avenue','',''},
  ['WB_Exit_Avenue__SNB_Avenue_1']={2.445,15.726,117.22,36.455,19.052,57.56,6,true,'SNB_Avenue','',''},
  ['WB_Exit_Avenue_01__WB_Fire']={0.0,11.16,119.5,26.053,2.28,19.509,6,false,'WB_Fire','',''},
  ['WB_Exit_Avenue_02__WB_FireCore']={0.0,10.9,119.5,25.3,1.3,18.779,6,false,'WB_FireCore','',''},
  ['WB_Exit_Bridge__SNB_Bridge_1']={0.0,-3.132,204.5,17.2,25.497,40.2,6,true,'SNB_Bridge_1','',''},
  ['WB_Exit_Bridge_01__SNB_Bridge_2']={0.0,-2.965,166.5,18.4,25.83,41.0,6,true,'SNB_Bridge_2','',''},
  ['WB_Exit_Bridge_02__WB_Fire']={0.0,10.377,187.0,14.453,2.947,48.175,6,false,'WB_Fire','',''},
  ['WB_Exit_Bridge_03__WB_FireCore']={0.0,10.117,187.0,13.7,1.967,47.446,6,false,'WB_FireCore','',''},
  ['WB_Exit_Gate__SNB_Gate']={0.0,20.82,148.563,31.4,29.36,16.726,6,true,'SNB_Gate','','SN_Portao'},
  ['WB_Exit_Gate_01__WB_Fire']={0.0,11.56,141.8,26.653,2.28,1.509,6,false,'WB_Fire','','SN_Portao'},
  ['WB_Exit_Gate_02__WB_FireCore']={0.0,11.3,141.8,25.9,1.3,0.779,6,false,'WB_FireCore','','SN_Portao'},
  ['WB_Exit_IsleBridge__SNB_IsleBridge']={-159.0,5.649,12.0,52.0,41.097,21.385,6,true,'SNB_IsleBridge','',''},
  ['WB_Exit_IsleBridge_01__WB_Fire']={-156.036,17.985,12.0,41.581,16.33,18.853,6,false,'WB_Fire','',''},
  ['WB_Exit_IsleBridge_02__WB_FireCore']={-156.03,17.725,12.0,40.84,15.35,18.1,6,false,'WB_FireCore','',''},
  ['WB_Exit_Spawn__SNB_Spawn']={0.0,13.03,66.0,46.078,13.66,45.04,6,true,'SNB_Spawn','',''},
  ['WB_Exit_Spawn_01__SN_Rune']={-0.019,14.658,60.891,38.886,9.215,15.096,6,false,'SN_Rune','',''},
  ['WB_Exit_Spawn_02__WB_Fire']={0.0,14.66,66.0,31.453,2.28,29.509,6,false,'WB_Fire','',''},
  ['WB_Exit_Spawn_03__WB_FireCore']={0.0,14.4,66.0,30.7,1.3,28.779,6,false,'WB_FireCore','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g14_15']={-166.303,7.824,30.605,75.315,2.148,61.457,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g14_16']={-198.796,7.878,-23.606,140.067,2.4,149.097,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g15_15']={-24.742,7.82,72.895,190.204,2.593,146.001,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g15_16']={-12.11,7.957,-80.525,228.161,2.442,161.445,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g15_17']={-45.468,7.87,-144.013,91.064,2.267,32.427,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g16_15']={71.638,7.941,63.064,112.334,2.521,126.565,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g16_16']={76.084,7.871,-63.526,103.99,2.367,127.464,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g17_15']={135.953,7.841,35.644,14.101,2.182,69.755,7,true,'SNB_Tufts','',''},
  ['WB_Veg_Tufts__SNB_Tufts_g17_16']={137.238,7.836,-49.189,18.33,2.172,97.53,7,true,'SNB_Tufts','',''},
  ['WB_Veg_ancient__SNB_Veg_ancient']={-96.197,31.253,-113.286,43.481,51.292,41.429,7,true,'SNB_Veg_ancient','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g16_15']={-6.018,8.546,64.802,116.767,3.064,131.623,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bush1__SNB_Veg_bush1_g16_16']={-15.786,8.629,1.143,244.329,3.24,255.507,7,true,'SNB_Veg_bush1','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g14_15']={-186.54,8.674,12.213,5.442,3.132,20.542,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g15_15']={-30.343,8.951,71.978,115.412,3.716,136.842,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g15_16']={-84.594,8.912,-61.59,94.024,3.567,52.092,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g16_15']={69.781,8.639,33.63,109.514,2.984,24.099,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_bushF__SNB_Veg_bushF_g16_16']={69.879,8.916,-80.326,53.273,3.636,134.754,7,true,'SNB_Veg_bushF','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g14_16']={-139.271,19.029,-22.281,19.448,25.883,20.732,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g15_15']={-81.489,19.171,65.126,91.528,26.184,107.433,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g15_16']={-44.998,17.609,-47.97,33.766,22.879,65.671,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g16_15']={81.033,18.901,71.607,48.739,25.612,110.547,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g16_16']={84.362,19.458,-90.531,20.262,26.791,21.235,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak1__SNB_Veg_oak1_g16_17']={29.104,16.982,-153.357,55.78,21.551,22.618,7,true,'SNB_Veg_oak1','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g15_15']={-72.176,16.379,50.381,15.213,20.533,40.344,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g15_16']={-76.309,17.519,-48.727,44.754,22.976,47.474,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g16_15']={57.563,16.459,90.044,85.889,20.705,20.815,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak2__SNB_Veg_oak2_g16_16']={81.122,15.979,-38.555,83.311,19.675,56.147,7,true,'SNB_Veg_oak2','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g15_15']={-69.117,19.67,31.068,39.103,27.073,62.436,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g15_16']={-51.211,19.305,-9.775,18.381,26.305,21.047,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oak3__SNB_Veg_oak3_g16_15']={89.441,20.906,74.257,50.58,29.674,80.512,7,true,'SNB_Veg_oak3','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g14_15']={-197.719,16.035,24.511,14.802,19.621,15.087,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g15_15']={-44.569,18.022,105.306,52.384,23.841,57.974,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_oakG__SNB_Veg_oakG_g16_15']={77.764,16.845,11.455,15.763,21.341,15.976,7,true,'SNB_Veg_oakG','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g16_14']={5.008,24.226,71.571,277.063,36.246,145.698,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine1__SNB_Veg_pine1_g17_16']={95.104,22.921,-43.201,110.593,33.531,88.07,7,true,'SNB_Veg_pine1','',''},
  ['WB_Veg_pine2__SNB_Veg_pine2']={21.797,19.687,12.231,255.094,27.068,237.635,7,true,'SNB_Veg_pine2','',''},
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
  {'COL_Court_001','Block',{-214.371,6.9,43.95},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{20.184,11.6,1.4},false},
  {'COL_Court_002','Block',{-214.371,6.9,43.95},{0.174,0.0,-0.985},{-0.985,0.0,-0.174},{20.184,11.6,1.4},false},
  {'COL_Court_003','Block',{-214.371,6.9,43.95},{-0.766,0.0,-0.643},{-0.643,0.0,0.766},{20.184,11.6,1.4},false},
  {'COL_Court_005','Block',{-214.371,7.2,43.95},{0.174,0.0,-0.985},{-0.985,0.0,-0.174},{17.922,10.3,2.0},false},
  {'COL_Court_006','Block',{-214.371,7.2,43.95},{-0.766,0.0,-0.643},{-0.643,0.0,0.766},{17.922,10.3,2.0},false},
  {'COL_Court_007','Block',{-222.476,17.16,55.306},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{2.8,2.8,18.0},true},
  {'COL_Court_008','Block',{-200.863,17.16,47.44},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{2.8,2.8,18.0},true},
  {'COL_Court_009','Block',{-239.829,6.9,43.061},{0.914,0.0,0.407},{0.407,0.0,-0.914},{20.184,11.6,1.4},false},
  {'COL_Court_010','Block',{-239.829,6.9,43.061},{0.809,0.0,-0.588},{-0.588,0.0,-0.809},{20.184,11.6,1.4},false},
  {'COL_Court_011','Block',{-239.829,6.9,43.061},{-0.105,0.0,-0.995},{-0.995,0.0,0.105},{20.184,11.6,1.4},false},
  {'COL_Court_012','Block',{-239.829,7.2,43.061},{0.914,0.0,0.407},{0.407,0.0,-0.914},{17.922,10.3,2.0},false},
  {'COL_Court_013','Block',{-239.829,7.2,43.061},{0.809,0.0,-0.588},{-0.588,0.0,-0.809},{17.922,10.3,2.0},false},
  {'COL_Court_014','Block',{-239.829,7.2,43.061},{-0.105,0.0,-0.995},{-0.995,0.0,0.105},{17.922,10.3,2.0},false},
  {'COL_Court_015','Block',{-253.548,17.16,45.6},{0.914,0.0,0.407},{0.407,0.0,-0.914},{2.8,2.8,18.0},true},
  {'COL_Court_016','Block',{-232.536,17.16,54.955},{0.914,0.0,0.407},{0.407,0.0,-0.914},{2.8,2.8,18.0},true},
  {'COL_Court_017','Block',{-257.524,6.9,24.737},{0.375,0.0,0.927},{0.927,0.0,-0.375},{20.184,11.6,1.4},false},
  {'COL_Court_018','Block',{-257.524,6.9,24.737},{0.99,0.0,0.139},{0.139,0.0,-0.99},{20.184,11.6,1.4},false},
  {'COL_Court_019','Block',{-257.524,6.9,24.737},{0.616,0.0,-0.788},{-0.788,0.0,-0.616},{20.184,11.6,1.4},false},
  {'COL_Court_020','Block',{-257.524,7.2,24.737},{0.375,0.0,0.927},{0.927,0.0,-0.375},{17.922,10.3,2.0},false},
  {'COL_Court_021','Block',{-257.524,7.2,24.737},{0.99,0.0,0.139},{0.139,0.0,-0.99},{17.922,10.3,2.0},false},
  {'COL_Court_022','Block',{-257.524,7.2,24.737},{0.616,0.0,-0.788},{-0.788,0.0,-0.616},{17.922,10.3,2.0},false},
  {'COL_Court_023','Block',{-269.157,17.16,17.033},{0.375,0.0,0.927},{0.927,0.0,-0.375},{2.8,2.8,18.0},true},
  {'COL_Court_024','Block',{-260.541,17.16,38.359},{0.375,0.0,0.927},{0.927,0.0,-0.375},{2.8,2.8,18.0},true},
  {'COL_Court_025','Block',{-257.524,6.9,-0.737},{-0.375,0.0,0.927},{0.927,0.0,0.375},{20.184,11.6,1.4},false},
  {'COL_Court_026','Block',{-257.524,6.9,-0.737},{0.616,0.0,0.788},{0.788,0.0,-0.616},{20.184,11.6,1.4},false},
  {'COL_Court_027','Block',{-257.524,6.9,-0.737},{0.99,0.0,-0.139},{-0.139,0.0,-0.99},{20.184,11.6,1.4},false},
  {'COL_Court_028','Block',{-257.524,7.2,-0.737},{-0.375,0.0,0.927},{0.927,0.0,0.375},{17.922,10.3,2.0},false},
  {'COL_Court_029','Block',{-257.524,7.2,-0.737},{0.616,0.0,0.788},{0.788,0.0,-0.616},{17.922,10.3,2.0},false},
  {'COL_Court_030','Block',{-257.524,7.2,-0.737},{0.99,0.0,-0.139},{-0.139,0.0,-0.99},{17.922,10.3,2.0},false},
  {'COL_Court_031','Block',{-260.541,17.16,-14.359},{-0.375,0.0,0.927},{0.927,0.0,0.375},{2.8,2.8,18.0},true},
  {'COL_Court_032','Block',{-269.157,17.16,6.967},{-0.375,0.0,0.927},{0.927,0.0,0.375},{2.8,2.8,18.0},true},
  {'COL_Court_033','Block',{-239.829,6.9,-19.061},{-0.914,0.0,0.407},{0.407,0.0,0.914},{20.184,11.6,1.4},false},
  {'COL_Court_034','Block',{-239.829,6.9,-19.061},{-0.105,0.0,0.995},{0.995,0.0,0.105},{20.184,11.6,1.4},false},
  {'COL_Court_035','Block',{-239.829,6.9,-19.061},{0.809,0.0,0.588},{0.588,0.0,-0.809},{20.184,11.6,1.4},false},
  {'COL_Court_037','Block',{-239.829,7.2,-19.061},{-0.105,0.0,0.995},{0.995,0.0,0.105},{17.922,10.3,2.0},false},
  {'COL_Court_038','Block',{-239.829,7.2,-19.061},{0.809,0.0,0.588},{0.588,0.0,-0.809},{17.922,10.3,2.0},false},
  {'COL_Court_039','Block',{-232.536,17.16,-30.955},{-0.914,0.0,0.407},{0.407,0.0,0.914},{2.8,2.8,18.0},true},
  {'COL_Court_040','Block',{-253.548,17.16,-21.6},{-0.914,0.0,0.407},{0.407,0.0,0.914},{2.8,2.8,18.0},true},
  {'COL_Court_041','Block',{-214.371,6.9,-19.95},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{20.184,11.6,1.4},false},
  {'COL_Court_042','Block',{-214.371,6.9,-19.95},{-0.766,0.0,0.643},{0.643,0.0,0.766},{20.184,11.6,1.4},false},
  {'COL_Court_043','Block',{-214.371,6.9,-19.95},{0.174,0.0,0.985},{0.985,0.0,-0.174},{20.184,11.6,1.4},false},
  {'COL_Court_045','Block',{-214.371,7.2,-19.95},{-0.766,0.0,0.643},{0.643,0.0,0.766},{17.922,10.3,2.0},false},
  {'COL_Court_046','Block',{-214.371,7.2,-19.95},{0.174,0.0,0.985},{0.985,0.0,-0.174},{17.922,10.3,2.0},false},
  {'COL_Court_047','Block',{-200.863,17.16,-23.44},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{2.8,2.8,18.0},true},
  {'COL_Court_048','Block',{-222.476,17.16,-31.306},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{2.8,2.8,18.0},true},
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
  {'COL_Forge_037','Block',{12.6,11.1,-44.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.4,2.8,8.2},false},
  {'COL_Forge_038','Block',{-7.5,9.3,-73.0},{-0.866,0.0,-0.5},{-0.5,0.0,0.866},{4.0,7.6,4.6},false},
  {'COL_Forge_039','Block',{-12.6,11.1,-44.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.4,2.8,8.2},false},
  {'COL_Hammer_001','Block',{106.0,14.0,-66.0},{-0.342,0.0,-0.94},{-0.94,0.0,0.342},{30.6,18.0,14.0},false},
  {'COL_Isle_001','Block',{-226.0,7.9,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.4,8.4,2.0},false},
  {'COL_Isle_002','Block',{-226.0,18.25,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,4.0,19.0},false},
  {'COL_Isle_003','Block',{-226.0,6.5,-1.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{23.324,4.0,1.0},false},
  {'COL_Isle_004','Block',{-226.0,6.5,3.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{30.984,4.0,1.0},false},
  {'COL_Isle_005','Block',{-226.0,6.5,7.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{35.327,4.0,1.0},false},
  {'COL_Isle_006','Block',{-226.0,6.5,11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{38.0,4.0,1.0},false},
  {'COL_Isle_007','Block',{-226.0,6.5,15.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{36.661,4.0,1.0},false},
  {'COL_Isle_008','Block',{-226.0,6.5,19.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{33.466,4.0,1.0},false},
  {'COL_Isle_009','Block',{-226.0,6.5,23.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{27.713,4.0,1.0},false},
  {'COL_Isle_010','Block',{-226.0,6.5,27.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.971,4.0,1.0},false},
  {'COL_Isle_011','Block',{-182.0,13.0,4.4},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.4,3.4,12.0},false},
  {'COL_Isle_012','Block',{-182.0,13.0,19.6},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.4,3.4,12.0},false},
  {'COL_Isle_013','Block',{-227.396,14.8,51.976},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_014','Block',{-254.774,14.8,39.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_015','Block',{-266.0,14.8,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_016','Block',{-254.774,14.8,-15.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_017','Block',{-227.396,14.8,-27.976},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,17.0},false},
  {'COL_Isle_018','Block',{-159.0,8.3,18.55},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,0.9,2.6},false},
  {'COL_Isle_019','Block',{-159.0,8.3,5.45},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,0.9,2.6},false},
  {'COL_Isle_020','Block',{-159.0,6.2,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,14.0,1.6},false},
  {'COL_Isle_027','Block',{-138.0,6.5,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,15.2,1.0},false},
  {'COL_Isle_028','Block',{-180.0,6.5,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,15.2,1.0},false},
  {'COL_Isle_029','Block',{-136.0,14.0,3.4},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.2,3.2,14.0},false},
  {'COL_Isle_030','Block',{-136.0,14.0,20.6},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.2,3.2,14.0},false},
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
  {'COL_Portal_001','Block',{-214.765,7.984,42.867},{-0.94,0.0,0.342},{0.342,0.0,0.94},{19.584,16.128,1.008},false},
  {'COL_Portal_002','Block',{-214.187,8.351,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{7.737,7.737,1.742},false},
  {'COL_Portal_003','Block',{-214.187,8.351,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{10.068,4.159,1.742},false},
  {'COL_Portal_004','Block',{-214.187,8.351,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{4.159,10.068,1.742},false},
  {'COL_Portal_005','Block',{-214.187,8.722,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{6.618,6.618,2.484},false},
  {'COL_Portal_006','Block',{-214.187,8.722,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{8.611,3.557,2.484},false},
  {'COL_Portal_007','Block',{-214.187,8.722,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{3.557,8.611,2.484},false},
  {'COL_Portal_008','Block',{-214.187,9.082,44.457},{-0.94,0.0,0.342},{0.342,0.0,0.94},{8.064,3.744,3.204},false},
  {'COL_Portal_009','Block',{-211.763,10.734,43.575},{0.852,0.423,-0.31},{0.342,0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_010','Block',{-209.73,12.424,42.835},{0.591,0.777,-0.215},{0.342,0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_011','Block',{-208.6,14.891,42.423},{0.211,0.974,-0.077},{0.342,0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_012','Block',{-208.6,17.637,42.423},{-0.211,0.974,0.077},{0.342,0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_013','Block',{-216.61,10.734,45.339},{0.852,-0.423,-0.31},{0.342,-0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_014','Block',{-218.643,12.424,46.079},{0.591,-0.777,-0.215},{0.342,-0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_015','Block',{-219.774,14.891,46.491},{0.211,-0.974,-0.077},{0.342,-0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_016','Block',{-219.774,17.637,46.491},{-0.211,-0.974,0.077},{0.342,-0.0,0.94},{3.189,2.52,1.332},false},
  {'COL_Portal_017','Block',{-206.203,18.532,41.551},{-0.94,0.0,0.342},{0.342,0.0,0.94},{2.016,2.016,20.088},false},
  {'COL_Portal_018','Block',{-222.17,18.532,47.363},{-0.94,0.0,0.342},{0.342,0.0,0.94},{2.016,2.016,20.088},false},
  {'COL_Portal_019','Block',{-208.183,11.067,36.451},{0.479,-0.0,-0.878},{-0.827,0.334,-0.452},{1.296,1.296,6.48},false},
  {'COL_Portal_020','Block',{-221.556,9.64,43.998},{-0.883,0.0,0.469},{0.469,0.0,0.883},{4.032,2.592,2.304},false},
  {'COL_Portal_021','Block',{-239.214,8.164,41.679},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{18.864,8.784,1.368},false},
  {'COL_Portal_022','Block',{-239.214,8.164,41.679},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{10.656,15.408,1.368},false},
  {'COL_Portal_023','Block',{-239.829,8.992,43.061},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{15.552,3.744,1.008},false},
  {'COL_Portal_024','Block',{-239.829,8.992,43.061},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{12.384,6.768,1.008},false},
  {'COL_Portal_025','Block',{-239.829,8.992,43.061},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{7.776,8.64,1.008},false},
  {'COL_Portal_026','Block',{-239.214,8.164,41.679},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{15.84,12.528,1.368},false},
  {'COL_Portal_027','Block',{-239.829,8.992,43.061},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{13.248,6.048,1.008},false},
  {'COL_Portal_028','Block',{-234.594,11.568,46.081},{0.72,-0.616,0.321},{-0.407,0.0,0.914},{1.863,3.925,3.648},false},
  {'COL_Portal_029','Block',{-236.97,9.296,44.994},{0.4,-0.899,0.178},{-0.407,-0.0,0.914},{2.113,3.978,3.704},false},
  {'COL_Portal_030','Block',{-237.378,10.844,44.053},{0.4,-0.899,0.178},{-0.407,-0.0,0.914},{1.332,1.62,2.929},false},
  {'COL_Portal_031','Block',{-245.576,11.568,41.191},{-0.72,-0.616,-0.321},{-0.407,-0.0,0.914},{1.863,3.925,3.648},false},
  {'COL_Portal_032','Block',{-243.179,9.296,42.229},{-0.4,-0.899,-0.178},{-0.407,-0.0,0.914},{2.113,3.978,3.704},false},
  {'COL_Portal_033','Block',{-242.207,10.844,41.903},{-0.4,-0.899,-0.178},{-0.407,-0.0,0.914},{1.332,1.62,2.929},false},
  {'COL_Portal_034','Block',{-234.655,12.245,45.344},{0.858,-0.342,0.382},{-0.407,-0.0,0.914},{2.578,1.764,7.077},false},
  {'COL_Portal_035','Block',{-233.759,16.971,45.763},{0.905,0.139,0.403},{-0.407,0.0,0.914},{2.556,1.656,4.416},false},
  {'COL_Portal_036','Block',{-244.988,12.245,40.744},{-0.858,-0.342,-0.382},{-0.407,0.0,0.914},{2.578,1.764,7.077},false},
  {'COL_Portal_037','Block',{-245.899,16.971,40.358},{-0.905,0.139,-0.403},{-0.407,0.0,0.914},{2.556,1.656,4.416},false},
  {'COL_Portal_038','Block',{-231.186,9.64,39.579},{0.777,0.0,0.629},{0.629,0.0,-0.777},{3.528,1.44,1.584},false},
  {'COL_Portal_039','Block',{-242.397,10.083,34.666},{-0.777,0.0,-0.629},{-0.629,0.0,0.777},{4.32,1.44,2.542},false},
  {'COL_Portal_040','Block',{-239.807,10.09,43.011},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{9.792,1.692,1.476},false},
  {'COL_Portal_041','Block',{-240.488,11.044,44.54},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{11.52,1.944,3.384},false},
  {'COL_Portal_042','Block',{-240.403,16.264,44.35},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{5.184,1.814,5.184},false},
  {'COL_Portal_043','Block',{-236.666,14.164,45.699},{-0.996,-0.074,-0.057},{0.083,-0.979,-0.187},{3.782,3.375,1.152},false},
  {'COL_Portal_044','Block',{-236.809,17.176,45.828},{-0.998,0.032,-0.058},{-0.036,-0.996,0.081},{3.619,3.801,1.152},false},
  {'COL_Portal_045','Block',{-243.907,14.164,42.476},{-0.709,0.074,-0.702},{0.083,-0.979,-0.187},{3.782,3.375,1.152},false},
  {'COL_Portal_046','Block',{-243.907,17.176,42.668},{-0.711,-0.032,-0.703},{-0.036,-0.996,0.081},{3.619,3.801,1.152},false},
  {'COL_Portal_047','Block',{-255.488,8.002,23.914},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{19.584,10.296,1.044},false},
  {'COL_Portal_048','Block',{-255.455,8.002,23.901},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{16.819,12.528,1.044},false},
  {'COL_Portal_049','Block',{-255.321,8.2,23.847},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{12.384,6.768,1.44},false},
  {'COL_Portal_050','Block',{-254.921,8.2,23.685},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{10.31,7.632,1.44},false},
  {'COL_Portal_051','Block',{-255.789,8.398,24.035},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{10.08,4.32,1.836},false},
  {'COL_Portal_052','Block',{-255.455,8.398,23.901},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{8.352,5.04,1.836},false},
  {'COL_Portal_053','Block',{-254.724,13.06,32.147},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{2.736,3.096,9.72},false},
  {'COL_Portal_054','Block',{-260.658,13.06,17.461},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{2.736,3.096,9.72},false},
  {'COL_Portal_055','Block',{-255.925,10.054,29.177},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{3.672,1.44,3.06},false},
  {'COL_Portal_056','Block',{-255.412,14.752,30.445},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{0.936,1.44,6.336},false},
  {'COL_Portal_057','Block',{-259.458,10.054,20.431},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{3.672,1.44,3.06},false},
  {'COL_Portal_058','Block',{-259.97,14.752,19.163},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{0.936,1.44,6.336},false},
  {'COL_Portal_059','Block',{-258.359,16.264,25.074},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{7.704,1.512,7.704},false},
  {'COL_Portal_060','Block',{-258.359,16.264,25.074},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{10.008,1.512,4.133},false},
  {'COL_Portal_061','Block',{-258.359,16.264,25.074},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{4.133,1.512,10.008},false},
  {'COL_Portal_062','Block',{-251.163,8.524,31.64},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.512,1.512,1.368},false},
  {'COL_Portal_063','Block',{-251.163,10.666,31.64},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{0.72,0.72,2.916},false},
  {'COL_Portal_064','Block',{-258.72,9.334,15.435},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.152,1.152,2.988},false},
  {'COL_Portal_065','Block',{-257.722,11.512,15.886},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.296,1.224,1.368},false},
  {'COL_Portal_066','Block',{-251.015,8.002,1.893},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{4.32,4.104,1.044},false},
  {'COL_Portal_067','Block',{-253.319,8.2,0.963},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{3.744,0.864,1.44},false},
  {'COL_Portal_068','Block',{-254.02,8.56,0.679},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{3.312,0.792,2.16},false},
  {'COL_Portal_069','Block',{-252.946,10.054,5.229},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.792,0.792,3.708},false},
  {'COL_Portal_070','Block',{-250.087,10.054,-1.847},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.792,0.792,3.708},false},
  {'COL_Portal_071','Block',{-258.867,12.16,8.738},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.224,1.224,7.92},false},
  {'COL_Portal_072','Block',{-258.025,8.92,-0.939},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{7.2,5.976,2.88},false},
  {'COL_Portal_073','Block',{-260.094,8.776,3.894},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{3.312,5.76,2.592},false},
  {'COL_Portal_074','Block',{-260.976,9.028,5.789},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.864,5.544,3.096},false},
  {'COL_Portal_075','Block',{-261.32,9.352,6.544},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.792,5.04,3.744},false},
  {'COL_Portal_076','Block',{-261.53,8.758,7.352},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.864,7.272,2.556},false},
  {'COL_Portal_077','Block',{-259.763,13.024,4.804},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.584,1.368,2.16},false},
  {'COL_Portal_078','Block',{-260.06,16.732,5.539},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.016,1.368,5.256},false},
  {'COL_Portal_079','Block',{-262.081,11.512,4.295},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.52,1.512,2.88},false},
  {'COL_Portal_080','Block',{-256.156,8.776,-5.853},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{3.312,5.76,2.592},false},
  {'COL_Portal_081','Block',{-255.474,9.028,-7.829},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.864,5.544,3.096},false},
  {'COL_Portal_082','Block',{-255.197,9.352,-8.61},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.792,5.04,3.744},false},
  {'COL_Portal_083','Block',{-254.787,8.758,-9.338},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{0.864,7.272,2.556},false},
  {'COL_Portal_084','Block',{-255.286,13.024,-6.277},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{1.584,1.368,2.16},false},
  {'COL_Portal_085','Block',{-254.989,16.732,-7.012},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.016,1.368,5.256},false},
  {'COL_Portal_086','Block',{-257.307,11.512,-7.521},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{2.52,1.512,2.88},false},
  {'COL_Portal_087','Block',{-254.887,8.74,0.329},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{17.136,1.224,2.52},false},
  {'COL_Portal_088','Block',{-261.296,8.758,-2.261},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{17.136,1.512,2.556},false},
  {'COL_Portal_089','Block',{-259.093,16.12,-1.37},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{10.944,2.808,11.52},false},
  {'COL_Portal_090','Block',{-239.214,8.056,-17.679},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{16.416,15.408,1.152},false},
  {'COL_Portal_091','Block',{-247.041,9.208,-14.194},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.008,15.408,2.016},false},
  {'COL_Portal_092','Block',{-231.387,9.208,-21.164},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.008,15.408,2.016},false},
  {'COL_Portal_093','Block',{-239.829,8.452,-19.061},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{8.755,8.755,1.8},false},
  {'COL_Portal_094','Block',{-239.829,8.452,-19.061},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{11.393,4.706,1.8},false},
  {'COL_Portal_095','Block',{-239.829,8.452,-19.061},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{4.706,11.393,1.8},false},
  {'COL_Portal_096','Block',{-239.829,8.74,-19.061},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{6.719,6.719,2.376},false},
  {'COL_Portal_097','Block',{-239.829,8.74,-19.061},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{8.744,3.612,2.376},false},
  {'COL_Portal_098','Block',{-239.829,8.74,-19.061},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{3.612,8.744,2.376},false},
  {'COL_Portal_099','Block',{-243.362,12.376,-10.71},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{3.6,1.008,7.56},false},
  {'COL_Portal_100','Block',{-234.497,16.48,-25.848},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.008,1.008,16.56},false},
  {'COL_Portal_101','Block',{-231.229,9.712,-15.323},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{2.592,2.016,2.16},false},
  {'COL_Portal_102','Block',{-246.206,9.568,-22.054},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.728,1.728,1.872},false},
  {'COL_Portal_103','Block',{-232.255,9.568,-18.334},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.728,1.728,1.872},false},
  {'COL_Portal_104','Block',{-248.442,11.08,-21.058},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{1.152,1.152,5.76},false},
  {'COL_Portal_110','Block',{-240.429,15.832,-20.409},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{10.944,0.288,11.808},false},
  {'COL_Portal_111','Block',{-214.765,8.02,-18.867},{0.94,0.0,0.342},{0.342,0.0,-0.94},{19.872,16.128,1.08},false},
  {'COL_Portal_112','Block',{-215.135,8.722,-17.852},{0.94,0.0,0.342},{0.342,0.0,-0.94},{8.352,4.176,1.044},false},
  {'COL_Portal_113','Block',{-214.815,9.064,-18.732},{0.94,0.0,0.342},{0.342,0.0,-0.94},{7.2,2.304,1.728},false},
  {'COL_Portal_114','Block',{-220.145,16.894,-22.664},{0.94,0.0,0.342},{0.342,0.0,-0.94},{2.628,3.024,17.388},false},
  {'COL_Portal_115','Block',{-208.204,16.894,-18.318},{0.94,0.0,0.342},{0.342,0.0,-0.94},{2.628,3.024,17.388},false},
  {'COL_Portal_116','Block',{-214.174,23.014,-20.491},{0.94,0.0,0.342},{0.342,0.0,-0.94},{10.08,2.304,5.148},false},
  {'COL_Portal_117','Block',{-214.1,9.424,-20.694},{0.94,0.0,0.342},{0.342,0.0,-0.94},{5.184,1.872,2.448},false},
  {'COL_Portal_118','Block',{-217.686,9.856,-21.999},{0.94,0.0,0.342},{0.342,0.0,-0.94},{2.448,1.872,3.312},false},
  {'COL_Portal_119','Block',{-210.515,9.856,-19.389},{0.94,0.0,0.342},{0.342,0.0,-0.94},{2.448,1.872,3.312},false},
  {'COL_Portal_120','Block',{-213.891,15.544,-21.269},{0.94,0.0,0.342},{0.342,0.0,-0.94},{8.64,0.648,9.792},false},
  {'COL_Portal_121','Ramp',{-211.455,8.99,-21.856},{-0.277,0.588,0.76},{0.94,0.0,0.342},{1.498,2.448,0.576},false},
  {'COL_Portal_122','Block',{-208.715,8.862,-22.38},{0.94,0.0,0.342},{0.342,0.0,-0.94},{2.314,2.163,1.324},false},
  {'COL_Portal_123','Block',{-208.774,9.778,-22.77},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.873,1.402,0.553},false},
  {'COL_Portal_124','Block',{-210.853,8.713,-24.563},{0.94,0.0,0.342},{0.342,0.0,-0.94},{1.784,1.618,1.026},false},
  {'COL_Portal_125','Ramp',{-209.31,8.906,-16.804},{0.238,0.719,-0.653},{-0.94,0.0,-0.342},{1.123,1.584,0.576},false},
  {'COL_Portal_126','Block',{-208.68,8.716,-14.914},{0.94,0.0,0.342},{0.342,0.0,-0.94},{1.091,1.027,1.031},false},
  {'COL_Portal_127','Block',{-208.946,9.369,-15.259},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.403,0.343,0.503},false},
  {'COL_Portal_128','Block',{-210.766,8.571,-14.688},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.647,0.695,0.741},false},
  {'COL_Portal_129','Block',{-222.603,9.262,-16.28},{0.998,0.0,-0.07},{-0.07,0.0,-0.998},{3.168,0.864,2.124},false},
  {'COL_Portal_130','Block',{-220.664,9.082,-18.869},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.576,0.576,1.764},false},
  {'COL_Portal_131','Block',{-221.064,8.977,-20.087},{0.94,0.0,0.342},{0.342,0.0,-0.94},{0.49,0.49,1.553},false},
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
  {'COL_Shop_001','Block',{72.686,6.9,-33.894},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{34.0,27.6,1.4},false},
  {'COL_Shop_002','Block',{73.049,7.9,-34.063},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{32.0,24.8,0.6},true},
  {'COL_Shop_003','Block',{81.931,14.9,-38.204},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{28.0,1.6,13.4},true},
  {'COL_Shop_004','Block',{81.074,14.9,-23.24},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{1.6,15.8,13.4},true},
  {'COL_Shop_005','Block',{72.759,14.9,-24.273},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{10.5,1.6,13.4},true},
  {'COL_Shop_006','Block',{69.209,13.35,-22.894},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{1.0,6.0,10.3},true},
  {'COL_Shop_007','Block',{66.014,13.35,-23.831},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{5.4,1.0,10.3},true},
  {'COL_Shop_008','Block',{81.943,12.8,-20.666},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{5.4,5.4,9.0},true},
  {'COL_Shop_009','Block',{69.917,14.9,-47.167},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{1.6,15.8,13.4},true},
  {'COL_Shop_010','Block',{65.363,14.9,-40.133},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{10.5,1.6,13.4},true},
  {'COL_Shop_011','Block',{62.025,13.35,-38.301},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{1.0,6.0,10.3},true},
  {'COL_Shop_012','Block',{60.689,13.35,-35.25},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{5.4,1.0,10.3},true},
  {'COL_Shop_013','Block',{68.505,12.8,-49.487},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{5.4,5.4,9.0},true},
  {'COL_Shop_014','Block',{69.061,19.4,-32.203},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{7.0,1.6,4.4},true},
  {'COL_Shop_015','Block',{65.617,18.1,-30.597},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{18.0,6.0,1.2},true},
  {'COL_Shop_016','Block',{63.351,17.55,-29.541},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{7.2,1.0,1.9},true},
  {'COL_Shop_017','Block',{75.284,9.9,-34.001},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{12.6,2.2,3.4},true},
  {'COL_Shop_018','Block',{80.481,13.2,-37.528},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{23.0,1.6,10.0},true},
  {'COL_Shop_019','Block',{74.055,10.0,-44.683},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{3.4,3.4,3.6},false},
  {'COL_Shop_020','Block',{75.496,25.6,-35.204},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{29.0,16.8,8.0},true},
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
  {'COL_Terrain_041','Block',{-227.0,4.8,-41.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{44.0,8.0,4.0},false},
  {'COL_Terrain_042','Block',{-229.0,4.8,-33.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{64.0,8.0,4.0},false},
  {'COL_Terrain_043','Block',{-230.0,4.8,-25.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{78.0,8.0,4.0},false},
  {'COL_Terrain_044','Block',{-228.0,4.8,-17.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{90.0,8.0,4.0},false},
  {'COL_Terrain_045','Block',{-225.0,4.8,-9.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{100.0,8.0,4.0},false},
  {'COL_Terrain_046','Block',{-223.0,4.8,-1.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{104.0,8.0,4.0},false},
  {'COL_Terrain_047','Block',{-223.0,4.8,14.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{108.0,24.0,4.0},false},
  {'COL_Terrain_050','Block',{-225.0,4.8,30.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{104.0,8.0,4.0},false},
  {'COL_Terrain_051','Block',{-227.0,4.8,38.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{100.0,8.0,4.0},false},
  {'COL_Terrain_052','Block',{-229.0,4.8,46.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{92.0,8.0,4.0},false},
  {'COL_Terrain_053','Block',{-229.0,4.8,54.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{80.0,8.0,4.0},false},
  {'COL_Terrain_054','Block',{-229.0,4.8,60.755},{1.0,0.0,0.0},{0.0,0.0,-1.0},{56.0,4.11,4.0},false},
  {'COL_Veg_001','Block',{115.137,11.341,-17.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.834,2.834,9.082},false},
  {'COL_Veg_002','Block',{-71.203,10.86,37.052},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.533,2.533,8.119},false},
  {'COL_Veg_003','Block',{45.437,10.645,-60.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.399,2.399,7.689},false},
  {'COL_Veg_004','Block',{94.488,10.739,86.185},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.458,2.458,7.878},false},
  {'COL_Veg_005','Block',{22.09,11.579,92.961},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.982,2.982,9.558},false},
  {'COL_Veg_006','Block',{-72.399,11.539,63.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.957,2.957,9.478},false},
  {'COL_Veg_007','Block',{-62.191,12.103,-34.075},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.309,3.309,10.605},false},
  {'COL_Veg_008','Block',{-90.795,12.044,-64.395},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.272,3.272,10.487},false},
  {'COL_Veg_009','Block',{-76.393,12.476,20.439},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.542,3.542,11.353},false},
  {'COL_Veg_010','Block',{8.982,11.81,-150.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.126,3.126,10.02},false},
  {'COL_Veg_011','Block',{-52.724,12.119,-23.509},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.319,3.319,10.637},false},
  {'COL_Veg_012','Block',{-139.016,12.817,-21.693},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.755,3.755,12.034},false},
  {'COL_Veg_013','Block',{-45.697,12.573,108.089},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.602,3.602,11.546},false},
  {'COL_Veg_014','Block',{95.807,12.754,25.51},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.715,3.715,11.908},false},
  {'COL_Veg_015','Block',{-35.625,11.822,-71.861},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.133,3.133,10.043},false},
  {'COL_Veg_016','Block',{-88.172,12.887,65.376},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.798,3.798,12.174},false},
  {'COL_Veg_017','Block',{-118.11,12.211,84.227},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.377,3.377,10.823},false},
  {'COL_Veg_018','Block',{65.23,11.613,118.774},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.003,3.003,9.627},false},
  {'COL_Veg_019','Block',{48.473,11.765,-156.845},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.098,3.098,9.931},false},
  {'COL_Veg_020','Block',{84.112,13.028,-90.945},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.886,3.886,12.456},false},
  {'COL_Veg_021','Block',{-99.628,12.089,-76.657},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.031,2.031,10.577},false},
  {'COL_Veg_022','Block',{111.986,12.411,-99.951},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.155,2.155,11.223},false},
  {'COL_Veg_023','Block',{29.023,12.164,118.662},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.06,2.06,10.728},false},
  {'COL_Veg_024','Block',{54.903,13.276,123.311},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.487,2.487,12.951},false},
  {'COL_Veg_025','Block',{141.737,13.206,-21.922},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.46,2.46,12.813},false},
  {'COL_Veg_026','Block',{140.965,14.86,-39.209},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.095,3.095,16.121},false},
  {'COL_Veg_027','Block',{48.115,13.984,-79.29},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.759,2.759,14.368},false},
  {'COL_Veg_028','Block',{30.135,13.213,131.287},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.463,2.463,12.826},false},
  {'COL_Veg_029','Block',{17.16,15.513,134.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.346,3.346,17.426},false},
  {'COL_Veg_030','Block',{78.82,14.779,118.765},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.064,3.064,15.958},false},
  {'COL_Veg_031','Block',{135.483,13.796,0.607},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.686,2.686,13.992},false},
  {'COL_Veg_032','Block',{-124.722,14.399,51.157},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.918,2.918,15.198},false},
  {'COL_Veg_033','Block',{-198.214,11.38,24.803},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.858,2.858,9.161},false},
  {'COL_Veg_034','Block',{-27.328,12.366,125.026},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.473,3.473,11.131},false},
  {'COL_Veg_035','Block',{-63.0,11.702,84.307},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.059,3.059,9.805},false},
  {'COL_Veg_036','Block',{78.067,11.782,11.831},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.109,3.109,9.964},false},
  {'COL_Veg_037','Block',{106.632,11.921,43.237},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.195,3.195,10.242},false},
  {'COL_Veg_038','Block',{75.064,13.687,102.498},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.298,4.298,13.775},false},
  {'COL_Veg_039','Block',{-51.081,12.905,-9.813},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.81,3.81,12.211},false},
  {'COL_Veg_040','Block',{-78.719,13.084,51.304},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.921,3.921,12.567},false},
  {'COL_Veg_041','Block',{-96.0,18.3,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.384,9.384,23.0},false},
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
  {'LETREIRO_Ilha',{-226.0,33.0,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ILHA DOS PORTAIS',['alcance']=240}},
  {'LETREIRO_Loja',{61.629,34.1,-28.738},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='LOJA DE MOCHILAS',['alcance']=170}},
  {'LETREIRO_Portal1',{-215.356,27.4,41.243},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='NARUTO',['alcance']=150,['cor']='255,170,60',['icone']='brilho'}},
  {'LETREIRO_Portal2',{-238.658,27.4,40.43},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='DRAGON BALL',['alcance']=150,['cor']='255,150,40',['icone']='brilho'}},
  {'LETREIRO_Portal3',{-254.854,27.4,23.658},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='SHADOW GARDEN',['alcance']=150,['cor']='186,120,255',['icone']='brilho'}},
  {'LETREIRO_Portal4',{-254.854,27.4,0.342},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='DEMON SLAYER',['alcance']=150,['cor']='255,80,70',['icone']='brilho'}},
  {'LETREIRO_Portal5',{-238.658,27.4,-16.43},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ONE PIECE',['alcance']=150,['cor']='90,170,255',['icone']='brilho'}},
  {'LETREIRO_Portal6',{-215.356,27.4,-17.243},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='ONE PUNCH MAN',['alcance']=150,['cor']='255,210,90',['icone']='brilho'}},
  {'LETREIRO_Ranking',{62.816,45.6,52.708},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='CAMPEOES',['alcance']=190,['cor']='236,170,40',['icone']='trofeu'}},
  {'NPC_Ignis',{-0.9,7.02,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['npc']='Ignis',['alvo']='workspace.NPCs.Ignis (Root)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'NPC_Vendedor',{76.583,8.2,-35.711},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{['kind']='npc',['olha']='porta'}},
  {'PICK_SLOT_1',{-6.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='enferrujada',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_2',{-10.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='ferro',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_3',{-14.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='aco',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_4',{-18.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='rubi',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_5',{18.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='obsidiana',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_6',{14.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='runica',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_7',{10.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='estelar',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PICK_SLOT_8',{6.6,11.15,-44.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['picareta']='ignis',['caixa_w']=3.4,['caixa_h']=5.2,['face_x']=0.0,['face_z']=1.0}},
  {'PLAYER_INTERACT_Ignis',{-0.9,7.02,-46.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'PLAYER_Loja',{71.146,8.2,-33.175},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{['kind']='padloja'}},
  {'PORTAL_DemonSlayer',{-257.124,16.264,-0.575},{0.375,0.0,-0.927},{-0.927,0.0,-0.375},{['destino']='DemonSlayer',['raio']=7.5,['touch']=true,['vm_portal']='DemonSlayer'}},
  {'PORTAL_DragonBall',{-239.653,16.264,42.666},{-0.914,0.0,-0.407},{-0.407,0.0,0.914},{['destino']='DragonBall',['raio']=7.5,['touch']=true,['vm_portal']='DragonBall'}},
  {'PORTAL_Naruto',{-214.519,16.264,43.544},{-0.94,0.0,0.342},{0.342,0.0,0.94},{['destino']='Naruto',['raio']=7.5,['touch']=true,['vm_portal']='Naruto'}},
  {'PORTAL_OnePiece',{-239.653,16.264,-18.666},{0.914,0.0,-0.407},{-0.407,0.0,-0.914},{['destino']='OnePiece',['raio']=7.5,['touch']=true,['vm_portal']='OnePiece'}},
  {'PORTAL_OnePunchMan',{-214.519,16.264,-19.544},{0.94,0.0,0.342},{0.342,0.0,-0.94},{['destino']='OnePunchMan',['raio']=7.5,['touch']=true,['vm_portal']='OnePunchMan'}},
  {'PORTAL_ShadowGarden',{-257.124,16.264,24.575},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{['destino']='ShadowGarden',['raio']=7.5,['touch']=true,['vm_portal']='ShadowGarden'}},
  {'QUADRO_Coins',{76.026,7.6,46.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['metrica']='Coins',['tabua']='MOEDAS (moeda)'}},
  {'QUADRO_Strength',{58.798,7.6,66.83},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['metrica']='Strength',['tabua']='FORCA (martelo)'}},
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
  {'VFX_Brazier_ForgeE',{23.0,10.8,-41.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_ForgeW',{-23.0,10.8,-41.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Gate_-1',{-12.5,11.2,141.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Gate_1',{12.5,11.2,141.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_142_-1',{-142.0,10.6,6.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_142_1',{-142.0,10.6,17.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_176_-1',{-176.0,10.6,6.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleBr_176_1',{-176.0,10.6,17.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleMain_-1',{-136.0,24.65,3.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_IsleMain_1',{-136.0,24.65,20.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P1_-1',{-212.043,12.16,35.567},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P1_1',{-221.543,12.16,39.025},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P2_-1',{-232.331,12.16,38.648},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P2_1',{-241.567,12.16,34.536},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P3_-1',{-249.065,12.16,26.771},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P3_1',{-252.853,12.16,17.397},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P4_-1',{-252.853,12.16,6.603},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P4_1',{-249.065,12.16,-2.771},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P5_-1',{-241.567,12.16,-10.536},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P5_1',{-232.331,12.16,-14.648},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P6_-1',{-221.543,12.16,-15.025},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_P6_1',{-212.043,12.16,-11.567},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Rank_-1',{45.799,12.2,78.897},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Rank_1',{85.654,12.2,31.404},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_-1_-1',{-14.9,14.3,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_-1_1',{14.9,14.3,80.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_1_-1',{-14.9,14.3,52.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Brazier_Stair_1_1',{14.9,14.3,52.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=1.6}},
  {'VFX_Dust_Forge',{0.0,15.0,-50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=3}},
  {'VFX_Dust_Isle',{-226.0,15.0,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=4}},
  {'VFX_Dust_Plaza',{0.0,14.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='dust',['rate']=6}},
  {'VFX_Hammer_Embers',{112.0,7.4,-62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=3}},
  {'VFX_Hammer_Smoke',{106.0,7.8,-66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Hearth_Ember_C',{0.0,10.2,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=8}},
  {'VFX_Hearth_Fire_C',{0.0,8.6,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=16,['size']=3.4}},
  {'VFX_Leaves_ancient_6',{-96.0,35.32,-112.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=16.56}},
  {'VFX_Leaves_oak1_2',{-76.393,19.597,20.439},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.430771488974627}},
  {'VFX_Leaves_oak1_3',{-35.625,18.121,-71.861},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.573692072318419}},
  {'VFX_Leaves_oak2_0',{115.137,19.313,-17.786},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=7.265406852098314}},
  {'VFX_Leaves_oak2_1',{-62.191,21.412,-34.075},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=8.48436984959799}},
  {'VFX_Leaves_oak3_5',{106.632,17.383,43.237},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.145172782823461}},
  {'VFX_Leaves_oakG_4',{-198.214,18.16,24.803},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=0.6,['radius']=6.595843817701157}},
  {'VFX_Rune_IsleStone',{-226.0,10.0,12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=4}},
  {'VFX_Rune_Portal1',{-217.449,8.6,35.492},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal2',{-236.168,8.6,34.839},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal3',{-249.18,8.6,21.365},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal4',{-249.18,8.6,2.635},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal5',{-236.168,8.6,-10.839},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
  {'VFX_Rune_Portal6',{-217.449,8.6,-11.492},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='rune',['rate']=2}},
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
  {'L_P_DemonSlayer_Lamp_1','POINT',{-252.008,10.533,4.637},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Lamp_2','POINT',{-249.823,10.533,-0.77},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Pad','POINT',{-252.851,11.44,1.151},{255,129,129},12.6,0.71,false,false},
  {'L_P_DragonBall_Pad','POINT',{-237.779,11.44,38.456},{97,179,255},12.6,0.71,false,false},
  {'L_P_Naruto_Pad','POINT',{-216.095,11.44,39.214},{255,196,118},12.6,0.71,false,false},
  {'L_P_OnePiece_Pad','POINT',{-237.779,11.44,-14.456},{137,196,255},12.6,0.71,false,false},
  {'L_P_OnePunchMan_Pad','POINT',{-216.095,11.44,-15.213},{255,229,144},12.6,0.71,false,false},
  {'L_P_ShadowGarden_Candles','POINT',{-250.43,15.551,30.956},{203,137,255},9.5,0.49,false,false},
  {'L_P_ShadowGarden_Moon','POINT',{-255.469,24.63,23.673},{196,129,255},10.7,0.56,false,false},
  {'L_P_ShadowGarden_Pad','POINT',{-252.851,11.44,22.849},{206,137,255},12.6,0.71,false,false},
  {'L_Portal_DemonSlayer','POINT',{-255.522,16.264,0.073},{255,129,129},14.0,1.0,false,false},
  {'L_Portal_DragonBall','POINT',{-238.951,16.264,41.087},{97,179,255},14.0,1.0,false,false},
  {'L_Portal_Naruto','POINT',{-215.11,16.264,41.92},{255,196,118},14.0,1.0,false,false},
  {'L_Portal_OnePiece','POINT',{-238.95,16.264,-17.087},{137,196,255},14.0,1.0,false,false},
  {'L_Portal_OnePunchMan','POINT',{-215.11,16.264,-17.92},{255,229,144},14.0,1.0,false,false},
  {'L_Portal_ShadowGarden','POINT',{-255.522,16.264,23.927},{206,137,255},14.0,1.0,false,false},
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
  {'L_SN_Brazier_ForgeE','POINT',{23.0,11.4,-41.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_ForgeW','POINT',{-23.0,11.4,-41.0},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Gate_-1','POINT',{-12.5,11.8,141.8},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Gate_1','POINT',{12.5,11.8,141.8},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_142_-1','POINT',{-142.0,11.2,6.4},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_142_1','POINT',{-142.0,11.2,17.6},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_176_-1','POINT',{-176.0,11.2,6.4},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleBr_176_1','POINT',{-176.0,11.2,17.6},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleMain_-1','POINT',{-136.0,25.25,3.4},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_IsleMain_1','POINT',{-136.0,25.25,20.6},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P1_-1','POINT',{-212.043,12.76,35.567},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P1_1','POINT',{-221.543,12.76,39.025},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P2_-1','POINT',{-232.331,12.76,38.648},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P2_1','POINT',{-241.567,12.76,34.536},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P3_-1','POINT',{-249.065,12.76,26.771},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P3_1','POINT',{-252.853,12.76,17.397},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P4_-1','POINT',{-252.853,12.76,6.603},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P4_1','POINT',{-249.065,12.76,-2.771},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P5_-1','POINT',{-241.567,12.76,-10.536},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P5_1','POINT',{-232.331,12.76,-14.648},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P6_-1','POINT',{-221.543,12.76,-15.025},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_P6_1','POINT',{-212.043,12.76,-11.567},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Rank_-1','POINT',{45.799,12.8,78.897},{255,140,60},16.0,1.2,false,true},
  {'L_SN_Brazier_Rank_1','POINT',{85.654,12.8,31.404},{255,140,60},16.0,1.2,false,true},
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
  {'L_SN_IsleStone','POINT',{-226.0,27.75,12.0},{255,218,160},14.3,0.86,false,false},
  {'L_SN_ShopCounter','POINT',{73.612,12.55,-38.297},{255,200,130},16.0,0.9,false,false},
  {'L_SN_ShopLamp_-5','POINT',{75.071,18.65,-29.489},{255,200,130},16.0,0.9,false,false},
  {'L_SN_ShopLamp_5','POINT',{70.845,18.65,-38.552},{255,200,130},16.0,0.9,false,false},
  {'L_SN_ShopLantern','POINT',{61.121,19.575,-46.155},{255,200,130},16.0,0.9,false,false},
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
  {'SAFE_IlhaPatio',{-212.0,7.0,12.0}},
  {'SAFE_TrilhaOeste',{-100.0,6.8,10.0}},
  {'SAFE_Portal1',{-218.476,6.8,32.673}},
  {'SAFE_Portal2',{-234.948,6.8,32.098}},
  {'SAFE_Portal3',{-246.398,6.8,20.241}},
  {'SAFE_Portal4',{-246.398,6.8,3.759}},
  {'SAFE_Portal5',{-234.948,6.8,-8.098}},
  {'SAFE_Portal6',{-218.476,6.8,-8.673}},
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
  {1, 'Naruto', 1, Vector3.new(-214.964, 16.264, 42.322), Vector3.new(-0.3420, 0, -0.9397)},
  {2, 'DragonBall', 2, Vector3.new(-239.125, 16.264, 41.478), Vector3.new(0.4067, 0, -0.9135)},
  {3, 'ShadowGarden', 3, Vector3.new(-255.918, 16.264, 24.088), Vector3.new(0.9272, 0, -0.3746)},
  {4, 'DemonSlayer', 4, Vector3.new(-255.918, 16.264, -0.088), Vector3.new(0.9272, 0, 0.3746)},
  {5, 'OnePiece', 5, Vector3.new(-239.125, 16.264, -17.478), Vector3.new(0.4067, 0, 0.9135)},
  {6, 'OnePunchMan', 6, Vector3.new(-214.964, 16.264, -18.322), Vector3.new(-0.3420, 0, 0.9397)},
}
do
  local san = root:FindFirstChild('Santuario') or Instance.new('Folder'); san.Name = 'Santuario'; san.Parent = root
  for _, c in ipairs(san:GetChildren()) do if string.match(c.Name, '^Portal%d$') or c.Name == 'PortalKonoha' then c:Destroy() end end
  for _, p in ipairs(PORTAIS) do
    local m = Instance.new('Model'); m.Name = 'Portal' .. p[1]; m:SetAttribute('Tema', p[2])
    local d = Instance.new('Part'); d.Name = 'Disco'; d.Anchored = true; d.CanCollide = false; d.CanQuery = false
    d.CanTouch = true; d.CastShadow = false; d.Transparency = 1; d.Size = Vector3.new(10.08, 10.80, 1.2)
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

-- GlobalTop100: o modelo veio do lobby antigo com cada quadro num lugar (Forca 12 studs na frente das Tabuas, Moedas
-- atras do muro). Cada quadro (pe + moldura + painel + frisos + podios + ancoras dos podios) e encaixado na SUA tabua
-- pelo marcador QUADRO_<metrica>; moldura e pe ganham o tom de basalto da forja (sem a 'placa cinza' solta).
do local t = root:FindFirstChild('GlobalTop100')
  if t and t:IsA('Model') then
    local gp = t:FindFirstChild('GroundPivot'); if gp then gp.CFrame = TOP100_CF + ROOT_OFFSET end
    local rot = TOP100_CF - TOP100_CF.Position
    local n = 0
    for _, met in ipairs({'Strength', 'Coins'}) do
      local foot = t:FindFirstChild(met .. 'Foot'); local mk = MKF:FindFirstChild('QUADRO_' .. met)
      if foot and mk then
        local base = foot.CFrame * CFrame.new(0, -0.2, 0)
        local delta = (CFrame.new(mk.Position) * rot) * base:Inverse()
        for _, d in ipairs(t:GetDescendants()) do
          if d:IsA('BasePart') and string.sub(d.Name, 1, #met) == met then d.CFrame = delta * d.CFrame; n += 1 end
        end
        for _, nm in ipairs({met .. 'Frame', met .. 'Foot'}) do
          local q = t:FindFirstChild(nm); if q then q.Color = Color3.fromRGB(58, 50, 47); q.Material = Enum.Material.Slate end
        end
        for _, d in ipairs(t:GetChildren()) do
          if d:IsA('BasePart') and string.match(d.Name, '^' .. met .. 'Podium%d$') then d.Color = Color3.fromRGB(64, 56, 52); d.Material = Enum.Material.Slate end
        end
      else warn('GlobalTop100: faltou ' .. met .. 'Foot ou o marcador QUADRO_' .. met) end
    end
    print(string.format('GlobalTop100: %d pecas encaixadas nas Tabuas dos Campeoes', n))
  else print('GlobalTop100 ausente: construa com Top100Builder.Build(root, {OriginCF = root:GetAttribute(\"Top100Origin\")})') end
end

-- POSICOES DO JOGO (POSICIONAR_JOGO = true move os objetos soltos; o Core.LobbyLayout e trocado a mao/MCP):
--   LobbyLayout.Spawn        = Vector3.new(0.0, 13.3, 64.0)
--   LobbyLayout.Shop         = Vector3.new(71.146, 11.7, -33.175)
--   LobbyLayout.ShopFacing   = Vector3.new(76.583, 11.7, -35.711)
--   LobbyLayout.Ignis        = Vector3.new(-0.9, 10.5, -46.0)
--   LobbyLayout.PortalIsland = Vector3.new(-212.0, 10.5, 12.0)
local POSICIONAR_JOGO = true
if POSICIONAR_JOGO then
  local function mv(inst, cf, what) if inst then pcall(function() if inst:IsA('Model') then inst:PivotTo(cf) else inst.CFrame = cf end end); print('posicionado', what) else print('NAO achei', what) end end
  local msp = workspace:FindFirstChild('Mystical Spawn Point'); mv(msp and msp:FindFirstChild('SpawnLobby'), CFrame.new(0.0, 10.1, 64.0) * CFrame.Angles(0, 0, 0) + ROOT_OFFSET, 'SpawnLobby')
  mv(workspace:FindFirstChild('MailBox'), CFrame.new(-13.0, 10.4, 62.0) * CFrame.Angles(0, -math.pi / 2, 0) + ROOT_OFFSET, 'MailBox')
  local lm = workspace:FindFirstChild('LojaMochilas'); mv(lm and lm:FindFirstChild('PadLoja'), CFrame.new(71.146, 8.299999999999999, -33.175) + ROOT_OFFSET, 'PadLoja')
  local function acharVendedor()
    for _, c in ipairs(workspace:GetChildren()) do if c:IsA('Model') and c:GetAttribute('VendedorMochilas') then return c end end
    for _, n in ipairs({'Vebdedor suspeito', 'npc vendedor ', 'npc vendedor'}) do local c = workspace:FindFirstChild(n); if c then return c end end
    local npcs = workspace:FindFirstChild('NPCs'); return npcs and (npcs:FindFirstChild('npc vendedor ') or npcs:FindFirstChild('npc vendedor'))
  end
  local vend = acharVendedor(); local vh = vend and vend:FindFirstChild('HumanoidRootPart')
  if vend and vh then
    local pes = math.huge
    for _, d in ipairs(vend:GetDescendants()) do if d:IsA('BasePart') and (d.Name == 'LeftFoot' or d.Name == 'RightFoot') then pes = math.min(pes, d.Position.Y - d.Size.Y / 2) end end
    local alt = pes < math.huge and (vh.Position.Y - pes) or 3.0
    local p = Vector3.new(76.583, 8.20 + alt, -35.711) + ROOT_OFFSET
    local alvo = CFrame.lookAt(p, p + Vector3.new(-0.9063, 0, 0.4226))
    vend:PivotTo((alvo * vh.CFrame:Inverse()) * vend:GetPivot()); vend:SetAttribute('VendedorMochilas', true)
    print('posicionado vendedor de mochilas', vend.Name)
  else print('NAO achei o vendedor de mochilas') end
  local padL = workspace:FindFirstChild('LojaMochilas') and workspace.LojaMochilas:FindFirstChild('PadLoja')
  if padL then padL.CanTouch = false end   -- a loja abre pelo ProximityPrompt do vendedor, nao pelo toque
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


-- ================= LETREIROS no estilo dos simuladores (ref. 'Lovely Egg'): sem placa/fundo; texto branco gordo
-- (FredokaOne) com contorno grosso na cor da estacao, sombra deslocada e icone dos dois lados; tamanho em studs ======
do
ICONES = {trofeu = '\u{1F3C6}', brilho = '\u{2728}', mochila = '\u{1F392}', fogo = '\u{1F525}', mundo = '\u{1F30D}',
  martelo = '\u{1F528}', picareta = '\u{26CF}\u{FE0F}', coracao = '\u{2764}\u{FE0F}'}
function RGB_FOFO(s, def)
  local r, g, b = string.match(s or '', '(%d+)%s*,%s*(%d+)%s*,%s*(%d+)')
  if r then return Color3.fromRGB(tonumber(r), tonumber(g), tonumber(b)) end
  return def
end
local function _esc(c, k) return Color3.new(c.R * k, c.G * k, c.B * k) end
function ROTULO_FOFO(adornee, nome, txt, cor, icone, h, alcance, sub)
  local old = adornee:FindFirstChild(nome); if old then old:Destroy() end
  local n = utf8.len(txt) or #txt
  local ic = ICONES[icone or '']
  local w = h * (0.64 * n + (ic and 2.3 or 0.5))
  local hs = sub and 1.5 or 1.0
  local bg = Instance.new('BillboardGui'); bg.Name = nome; bg.Adornee = adornee; bg.Size = UDim2.fromScale(w, h * hs)
  bg.LightInfluence = 0; bg.AlwaysOnTop = false; bg.MaxDistance = alcance or 220; bg.ClipsDescendants = false
  local function lbl(t, x, y, sw, sh, col, st, th, z)
    local l = Instance.new('TextLabel'); l.BackgroundTransparency = 1; l.Text = t; l.Font = Enum.Font.FredokaOne
    l.TextScaled = true; l.TextColor3 = col; l.Position = UDim2.fromScale(x, y); l.Size = UDim2.fromScale(sw, sh)
    l.ZIndex = z or 2
    if st then local k = Instance.new('UIStroke'); k.Color = st; k.Thickness = th or 3; k.LineJoinMode = Enum.LineJoinMode.Round; k.Parent = l end
    l.Parent = bg; return l
  end
  local fy = 1 / hs
  local fi = ic and math.min(0.3, 1.05 * h / w) or 0
  local x0 = ic and fi or 0.03
  local tw = 1 - 2 * x0
  lbl(txt, x0 + 0.004, 0.09 * fy, tw, 0.9 * fy, _esc(cor, 0.42), _esc(cor, 0.42), 3.5, 1)     -- sombra
  lbl(txt, x0, 0.0, tw, 0.9 * fy, Color3.new(1, 1, 1), cor, 3, 2)                               -- texto
  if ic then
    lbl(ic, 0.0, 0.06 * fy, fi, 0.82 * fy, Color3.new(1, 1, 1), nil, nil, 3)
    lbl(ic, 1 - fi, 0.06 * fy, fi, 0.82 * fy, Color3.new(1, 1, 1), nil, nil, 3)
  end
  if sub then
    lbl(sub, 0.12, 0.93 * fy, 0.76, 1 - 0.95 * fy, Color3.fromRGB(255, 240, 190), _esc(cor, 0.55), 2.2, 2)
  end
  bg.Parent = adornee
  return bg
end
end
do
  local n = 0
  for _, mk in ipairs(MKF:GetChildren()) do
    local txt = mk:GetAttribute('texto')
    if txt and string.sub(mk.Name, 1, 9) == 'LETREIRO_' then
      local old = mk:FindFirstChild('Letreiro'); if old then old:Destroy() end
      local cor = RGB_FOFO(mk:GetAttribute('cor'), Color3.fromRGB(255, 120, 60))
      local h = string.sub(mk.Name, 1, 15) == 'LETREIRO_Portal' and 3.0 or 4.0
      ROTULO_FOFO(mk, 'Letreiro', txt, cor, mk:GetAttribute('icone'), h, mk:GetAttribute('alcance') or 170)
      n += 1
    end
  end
  print(string.format('Letreiros das estacoes (estilo fofo): %d', n))
end


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
-- placas oficiais do jogo (CircularUI: MUNDOS / MOCHILAS / IGNIS) nas estacoes novas, no MESMO estilo fofo dos
-- letreiros (o Layout.BuildServiceLabels do CircularGlobalLeaderboard so roda se alguem chamar; se rodar, refazer aqui)
do
  local cu = root:FindFirstChild('CircularUI')
  if cu then
    local function at(n, p) local a = cu:FindFirstChild(n); if a and a:IsA('BasePart') then a.CFrame = CFrame.new(p + ROOT_OFFSET) end return a end
    local mu = at('Mundos', Vector3.new(-226.000, 44, 12.000))
    local mo = at('Mochilas', Vector3.new(67.974, 34.50, -31.696))
    local ig = at('Ignis', Vector3.new(-0.9, 24, -52))
    if mu then ROTULO_FOFO(mu, 'ServiceLabel', 'MUNDOS', Color3.fromRGB(96, 120, 255), 'mundo', 5.2, 420) end
    if mo then ROTULO_FOFO(mo, 'ServiceLabel', 'MOCHILAS', Color3.fromRGB(236, 120, 40), 'mochila', 4.4, 400) end
    if ig then ROTULO_FOFO(ig, 'ServiceLabel', 'IGNIS', Color3.fromRGB(255, 84, 40), 'fogo', 4.8, 400, 'Vender \u{2022} Picaretas') end
    for _, nm in ipairs({'LETREIRO_Ilha', 'LETREIRO_Loja', 'LETREIRO_Ignis'}) do
      local mk = MKF:FindFirstChild(nm); local bg = mk and mk:FindFirstChildOfClass('BillboardGui'); if bg then bg:Destroy() end
    end
    print('CircularUI: placas MUNDOS/MOCHILAS/IGNIS posicionadas')
  end
end


-- ================= PICARETAS DO JOGO nas vitrines da forja (marcadores PICK_SLOT_*: picareta, caixa_w/h, face) =====
do
  local src = game:GetService('ServerStorage'):FindFirstChild('PicaretasBlender')
  local old = root:FindFirstChild('PicaretasExpostas'); if old then old:Destroy() end
  local pasta = Instance.new('Folder'); pasta.Name = 'PicaretasExpostas'
  local n, falta = 0, {}
  -- ordem do jogo da ESQUERDA para a DIREITA de quem olha a forja (olhando -Z, esquerda = -X)
  local ORDEM = {'enferrujada', 'ferro', 'aco', 'rubi', 'obsidiana', 'runica', 'estelar', 'ignis'}
  local slots = {}
  for _, mk in ipairs(MKF:GetChildren()) do
    if mk:GetAttribute('picareta') and string.sub(mk.Name, 1, 10) == 'PICK_SLOT_' then table.insert(slots, mk) end
  end
  table.sort(slots, function(a, b) return a.Position.X < b.Position.X end)
  if #slots == #ORDEM then for i, mk in ipairs(slots) do mk:SetAttribute('picareta', ORDEM[i]) end end
  for _, mk in ipairs(slots) do
    local nome = mk:GetAttribute('picareta')
    do
      local m0 = src and src:FindFirstChild(nome)
      if m0 and m0:IsA('Model') then
        local m = m0:Clone(); m.Name = 'Picareta_' .. nome
        for _, d in ipairs(m:GetDescendants()) do
          if d:IsA('LuaSourceContainer') then d:Destroy()
          elseif d:IsA('BasePart') then d.Anchored = true; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false end
        end
        local _, sz = m:GetBoundingBox()
        local k = math.min((mk:GetAttribute('caixa_w') or 3.4) / sz.X, (mk:GetAttribute('caixa_h') or 5.2) / sz.Y)
        m:ScaleTo(m:GetScale() * k)
        local bcf = m:GetBoundingBox()
        local off = m:GetPivot():ToObjectSpace(bcf)
        local face = Vector3.new(mk:GetAttribute('face_x') or 0, 0, mk:GetAttribute('face_z') or 1)
        m:PivotTo(CFrame.lookAt(mk.Position, mk.Position + face) * off:Inverse())
        m:SetAttribute('Vitrine', mk.Name)
        m.Parent = pasta; n += 1
      else table.insert(falta, tostring(nome)) end
    end
  end
  pasta.Parent = root
  print(string.format('Picaretas do jogo nas vitrines: %d (faltou: %s)', n, #falta > 0 and table.concat(falta, ', ') or 'nenhuma'))
end


print(string.format('LOBBY_FORJA montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
