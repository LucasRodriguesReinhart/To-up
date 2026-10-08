-- montar_lobby_wolfberg.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 0ab85aff
-- 1) Importe os FBX LOBBY_WB_*_0ab85a.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador
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
local EXPORT_ID = '0ab85aff'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o lobby Wolfberg INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
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
  ['stone'] = '',  -- textures/T_stone_v3.png (6.0 studs por repeticao)
  ['wb_bark'] = '',  -- textures/WB_bark_v1.png (4.0 studs por repeticao)
  ['wb_canvas_blue'] = '',  -- textures/WB_canvas_blue_v1.png (4.0 studs por repeticao)
  ['wb_canvas_green'] = '',  -- textures/WB_canvas_green_v1.png (4.0 studs por repeticao)
  ['wb_canvas_red'] = '',  -- textures/WB_canvas_red_v1.png (4.0 studs por repeticao)
  ['wb_cobble'] = '',  -- textures/WB_cobble_v1.png (6.0 studs por repeticao)
  ['wb_crop'] = '',  -- textures/WB_crop_v1.png (12.0 studs por repeticao)
  ['wb_dirt'] = '',  -- textures/WB_dirt_v1.png (8.0 studs por repeticao)
  ['wb_flag'] = '',  -- textures/WB_flag_v1.png (8.0 studs por repeticao)
  ['wb_grass'] = '',  -- textures/WB_grass_v1.png (10.0 studs por repeticao)
  ['wb_iron'] = '',  -- textures/WB_iron_v1.png (4.0 studs por repeticao)
  ['wb_leaf'] = '',  -- textures/WB_leaf_v1.png (6.0 studs por repeticao)
  ['wb_pine'] = '',  -- textures/WB_pine_v1.png (6.0 studs por repeticao)
  ['wb_plank'] = '',  -- textures/WB_plank_v1.png (4.0 studs por repeticao)
  ['wb_plaster'] = '',  -- textures/WB_plaster_v1.png (8.0 studs por repeticao)
  ['wb_plaster_ochre'] = '',  -- textures/WB_plaster_ochre_v1.png (8.0 studs por repeticao)
  ['wb_rock'] = '',  -- textures/WB_rock_v1.png (16.0 studs por repeticao)
  ['wb_roof'] = '',  -- textures/WB_roof_v1.png (4.0 studs por repeticao)
  ['wb_roof_dark'] = '',  -- textures/WB_roof_dark_v1.png (4.0 studs por repeticao)
  ['wb_stone'] = '',  -- textures/WB_stone_v1.png (6.0 studs por repeticao)
  ['wb_stone_dark'] = '',  -- textures/WB_stone_dark_v1.png (6.0 studs por repeticao)
  ['wb_timber'] = '',  -- textures/WB_timber_v1.png (4.0 studs por repeticao)
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
  ['Stone_DS_Rock'] = {c = Color3.fromRGB(92,92,100), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Light'] = {c = Color3.fromRGB(156,148,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['WB_Apple'] = {c = Color3.fromRGB(200,48,40), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Bark'] = {c = Color3.fromRGB(96,66,44), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_bark', w = nil},
  ['WB_Brass'] = {c = Color3.fromRGB(196,150,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Bread'] = {c = Color3.fromRGB(214,160,90), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_CanvasBlue'] = {c = Color3.fromRGB(70,100,160), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_canvas_blue', w = nil},
  ['WB_CanvasGreen'] = {c = Color3.fromRGB(86,136,80), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_canvas_green', w = nil},
  ['WB_CanvasRed'] = {c = Color3.fromRGB(200,70,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_canvas_red', w = nil},
  ['WB_Cloth_Blue'] = {c = Color3.fromRGB(56,86,150), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Cloth_Cream'] = {c = Color3.fromRGB(228,214,180), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Cloth_Gold'] = {c = Color3.fromRGB(214,170,70), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Cloth_Green'] = {c = Color3.fromRGB(60,120,70), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Cloth_Purple'] = {c = Color3.fromRGB(110,60,150), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Cloth_Red'] = {c = Color3.fromRGB(176,54,44), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Cobble'] = {c = Color3.fromRGB(160,146,128), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_cobble', w = nil},
  ['WB_Crop'] = {c = Color3.fromRGB(150,170,70), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_crop', w = nil},
  ['WB_Dark'] = {c = Color3.fromRGB(30,26,24), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Dirt'] = {c = Color3.fromRGB(150,118,82), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_dirt', w = nil},
  ['WB_Ember'] = {c = Color3.fromRGB(255,90,20), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_FarMountain'] = {c = Color3.fromRGB(108,128,168), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Fire'] = {c = Color3.fromRGB(255,150,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Flag'] = {c = Color3.fromRGB(178,166,146), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_flag', w = nil},
  ['WB_FlowerPink'] = {c = Color3.fromRGB(230,110,160), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['WB_FlowerRed'] = {c = Color3.fromRGB(214,50,50), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['WB_FlowerWhite'] = {c = Color3.fromRGB(236,232,220), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['WB_FlowerYellow'] = {c = Color3.fromRGB(240,200,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Glass'] = {c = Color3.fromRGB(60,70,90), m = Enum.Material.Glass, t = 0.3, s = true, x = nil, w = nil},
  ['WB_Grass'] = {c = Color3.fromRGB(104,160,58), m = Enum.Material.Grass, t = 0.0, s = true, x = 'wb_grass', w = nil},
  ['WB_Grass_Hill'] = {c = Color3.fromRGB(112,160,72), m = Enum.Material.Grass, t = 0.0, s = true, x = 'wb_grass', w = nil},
  ['WB_Ingot'] = {c = Color3.fromRGB(255,120,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Iron'] = {c = Color3.fromRGB(74,72,76), m = Enum.Material.Metal, t = 0.0, s = true, x = 'wb_iron', w = nil},
  ['WB_LampGlow'] = {c = Color3.fromRGB(255,214,130), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Leaf'] = {c = Color3.fromRGB(84,150,62), m = Enum.Material.Grass, t = 0.0, s = true, x = 'wb_leaf', w = nil},
  ['WB_Leather'] = {c = Color3.fromRGB(120,72,44), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_LeatherDark'] = {c = Color3.fromRGB(70,42,28), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Paper'] = {c = Color3.fromRGB(236,226,196), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Pine'] = {c = Color3.fromRGB(46,104,66), m = Enum.Material.Grass, t = 0.0, s = true, x = 'wb_pine', w = nil},
  ['WB_Plank'] = {c = Color3.fromRGB(150,104,64), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_plank', w = nil},
  ['WB_Plank_Light'] = {c = Color3.fromRGB(184,140,92), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_plank', w = nil},
  ['WB_Plaster'] = {c = Color3.fromRGB(222,204,170), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_plaster', w = nil},
  ['WB_Plaster_Ochre'] = {c = Color3.fromRGB(214,188,146), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_plaster', w = nil},
  ['WB_Rock'] = {c = Color3.fromRGB(132,122,112), m = Enum.Material.Slate, t = 0.0, s = true, x = 'wb_rock', w = nil},
  ['WB_Roof'] = {c = Color3.fromRGB(170,80,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_roof', w = nil},
  ['WB_Roof_Dark'] = {c = Color3.fromRGB(136,62,40), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_roof_dark', w = nil},
  ['WB_Rope'] = {c = Color3.fromRGB(190,160,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_SignText'] = {c = Color3.fromRGB(240,220,170), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['WB_Snow'] = {c = Color3.fromRGB(230,234,240), m = Enum.Material.Snow, t = 0.0, s = false, x = nil, w = nil},
  ['WB_Stone'] = {c = Color3.fromRGB(152,144,132), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_stone', w = nil},
  ['WB_Stone_Dark'] = {c = Color3.fromRGB(108,102,98), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_stone_dark', w = nil},
  ['WB_Timber'] = {c = Color3.fromRGB(88,60,40), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'wb_timber', w = nil},
  ['WB_Water'] = {c = Color3.fromRGB(70,150,190), m = Enum.Material.SmoothPlastic, t = 0.2, s = false, x = nil, w = nil},
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
local FBX = {[1]='LOBBY_WB_02_TERRAIN_0ab85a.fbx', [2]='LOBBY_WB_03_TOWN_0ab85a.fbx', [3]='LOBBY_WB_04_FORGE_0ab85a.fbx', [4]='LOBBY_WB_05_SERVICES_0ab85a.fbx', [5]='LOBBY_WB_06_PORTALS_0ab85a.fbx', [6]='LOBBY_WB_07_EXIT_0ab85a.fbx', [7]='LOBBY_WB_09_VEGETATION_0ab85a.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['WB_Bg_Forest__WB_Bark__WB_Bark']={6.021,51.755,0.844,1185.416,61.53,1274.099,1,false,'WB_Bark','k',''},
  ['WB_Bg_Forest__WB_Leaf__WB_Leaf']={-0.275,61.374,-10.064,1186.282,63.262,1212.591,1,false,'WB_Leaf','k',''},
  ['WB_Bg_Forest__WB_Pine__WB_Pine']={7.273,66.067,1.027,1194.193,77.558,1281.752,1,false,'WB_Pine','k',''},
  ['WB_Bg_Hills__WB_Crop__WB_Crop']={-20.564,33.366,33.182,1149.249,22.203,1028.188,1,false,'WB_Crop','k',''},
  ['WB_Bg_Hills__WB_Dirt__WB_Dirt']={-4.283,33.366,43.648,1088.951,22.203,985.7,1,false,'WB_Dirt','k',''},
  ['WB_Bg_Hills__WB_Grass_Hill__WB_Grass_Hill']={11.487,1.2,-17.041,1286.71,154.61,1372.045,1,false,'WB_Grass_Hill','k',''},
  ['WB_Bg_Mountains__WB_FarMountain__WB_FarMountain_0']={-685.17,158.964,590.768,1473.62,317.528,1483.007,1,false,'WB_FarMountain','k',''},
  ['WB_Bg_Mountains__WB_FarMountain__WB_FarMountain_1']={-684.445,225.803,-726.172,1461.734,451.206,1188.414,1,false,'WB_FarMountain','k',''},
  ['WB_Bg_Mountains__WB_FarMountain__WB_FarMountain_2']={699.155,169.369,829.136,1380.431,338.337,1178.672,1,false,'WB_FarMountain','k',''},
  ['WB_Bg_Mountains__WB_FarMountain__WB_FarMountain_3']={712.002,265.54,-523.526,1381.344,530.68,1592.193,1,false,'WB_FarMountain','k',''},
  ['WB_Bg_Mountains__WB_Rock__WB_Rock']={-11.543,154.621,40.305,1747.067,308.841,1663.576,1,false,'WB_Rock','k',''},
  ['WB_Bg_Mountains__WB_Snow__WB_Snow_0']={-765.898,213.786,436.462,1053.903,208.684,995.298,1,false,'WB_Snow','k',''},
  ['WB_Bg_Mountains__WB_Snow__WB_Snow_1']={-429.73,307.567,-682.884,947.473,288.478,1058.871,1,false,'WB_Snow','k',''},
  ['WB_Bg_Mountains__WB_Snow__WB_Snow_2']={859.804,235.618,344.923,726.526,206.639,1678.326,1,false,'WB_Snow','k',''},
  ['WB_Bg_Mountains__WB_Snow__WB_Snow_3']={544.604,349.397,-844.243,1060.479,363.766,736.153,1,false,'WB_Snow','k',''},
  ['WB_Ter_Paving__WB_Brass__WB_Brass']={-28.0,7.15,8.5,158.8,0.14,113.8,1,true,'WB_Brass','',''},
  ['WB_Ter_Paving__WB_Cobble__WB_Cobble']={-60.0,6.65,51.0,228.0,0.7,182.0,1,true,'WB_Cobble','',''},
  ['WB_Ter_Paving__WB_Dirt__WB_Dirt']={0.0,6.55,-69.0,80.0,0.7,46.0,1,true,'WB_Dirt','',''},
  ['WB_Ter_Paving__WB_Flag__WB_Flag']={0.0,6.89,51.0,18.0,0.38,178.0,1,true,'WB_Flag','',''},
  ['WB_Ter_Paving__WB_Grass__WB_Grass']={5.463,6.96,0.278,92.038,0.32,79.613,1,true,'WB_Grass','',''},
  ['WB_Ter_Paving__WB_LampGlow__WB_LampGlow']={-28.0,7.11,8.5,157.6,0.06,112.6,1,false,'WB_LampGlow','',''},
  ['WB_Ter_Paving__WB_Stone__WB_Stone']={-167.775,7.35,62.0,80.45,1.7,147.808,1,true,'WB_Stone','',''},
  ['WB_Ter_Paving__WB_Stone_Dark__WB_Stone_Dark']={-60.025,7.15,49.775,228.95,0.9,180.45,1,true,'WB_Stone_Dark','',''},
  ['WB_Ter_Plateau__WB_Grass__WB_Grass']={-49.588,6.5,10.12,370.392,0.6,295.504,1,true,'WB_Grass','',''},
  ['WB_Ter_Plateau__WB_Rock__WB_Rock_g14_16']={-175.535,-0.009,-36.5,100.931,79.982,93.0,1,true,'WB_Rock','',''},
  ['WB_Ter_Plateau__WB_Rock__WB_Rock_g15_16']={-54.507,1.814,12.987,369.724,83.629,297.974,1,true,'WB_Rock','',''},
  ['WB_Ter_Plateau__WB_Rock__WB_Rock_g15_17']={-20.834,0.816,-134.397,121.667,81.631,16.363,1,true,'WB_Rock','',''},
  ['WB_Ter_Plateau__WB_Rock__WB_Rock_g16_16']={22.01,2.099,-28.968,244.021,84.198,214.064,1,true,'WB_Rock','',''},
  ['WB_Ter_Plateau__WB_Rock__WB_Rock_g16_17']={10.0,-0.232,-132.289,172.0,79.537,24.577,1,true,'WB_Rock','',''},
  ['WB_Ter_Plateau__WB_Water__WB_Water']={0.0,1.7,0.0,840.0,1.0,840.0,1,false,'WB_Water','',''},
  ['WB_House_FE__WB_Dark__WB_Dark']={49.394,24.603,-73.983,11.975,23.606,5.365,2,false,'WB_Dark','','WB_House_FE'},
  ['WB_House_FE__WB_FlowerPink__WB_FlowerPink']={48.252,17.15,-80.0,15.234,0.694,24.099,2,false,'WB_FlowerPink','','WB_House_FE'},
  ['WB_House_FE__WB_FlowerYellow__WB_FlowerYellow']={47.745,17.13,-80.0,14.129,0.679,23.809,2,false,'WB_FlowerYellow','','WB_House_FE'},
  ['WB_House_FE__WB_Glass__WB_Glass']={50.0,18.016,-80.0,17.337,14.832,22.792,2,true,'WB_Glass','','WB_House_FE'},
  ['WB_House_FE__WB_Iron__WB_Iron']={41.629,13.985,-79.8,3.967,11.11,14.425,2,true,'WB_Iron','','WB_House_FE'},
  ['WB_House_FE__WB_LampGlow__WB_LampGlow']={41.637,13.2,-78.601,0.648,1.4,0.648,2,false,'WB_LampGlow','','WB_House_FE'},
  ['WB_House_FE__WB_Leaf__WB_Leaf']={48.292,16.874,-80.0,15.316,0.861,24.403,2,true,'WB_Leaf','','WB_House_FE'},
  ['WB_House_FE__WB_Plank__WB_Plank']={49.27,13.49,-80.0,19.729,12.58,24.519,2,true,'WB_Plank','','WB_House_FE'},
  ['WB_House_FE__WB_Plaster__WB_Plaster']={50.0,23.044,-80.0,17.556,16.089,23.037,2,true,'WB_Plaster','','WB_House_FE'},
  ['WB_House_FE__WB_Roof__WB_Roof']={50.0,27.424,-80.0,20.768,12.081,26.075,2,true,'WB_Roof','','WB_House_FE'},
  ['WB_House_FE__WB_Roof_Dark__WB_Roof_Dark']={50.0,33.486,-80.0,3.455,0.6,24.831,2,false,'WB_Roof_Dark','','WB_House_FE'},
  ['WB_House_FE__WB_SignText__WB_SignText']={41.205,17.841,-86.793,3.621,0.533,0.753,2,false,'WB_SignText','','WB_House_FE'},
  ['WB_House_FE__WB_Stone__WB_Stone']={50.0,21.653,-80.0,15.613,27.706,21.094,2,true,'WB_Stone','','WB_House_FE'},
  ['WB_House_FE__WB_Stone_Dark__WB_Stone_Dark']={50.0,21.253,-80.0,16.476,29.506,21.957,2,true,'WB_Stone_Dark','','WB_House_FE'},
  ['WB_House_FE__WB_Timber__WB_Timber']={49.892,19.081,-80.0,21.293,21.503,26.101,2,true,'WB_Timber','','WB_House_FE'},
  ['WB_House_FW__WB_Dark__WB_Dark']={-49.402,25.618,-84.012,13.57,25.635,8.242,2,true,'WB_Dark','','WB_House_FW'},
  ['WB_House_FW__WB_FlowerRed__WB_FlowerRed']={-49.303,17.165,-82.0,16.636,0.604,21.35,2,false,'WB_FlowerRed','','WB_House_FW'},
  ['WB_House_FW__WB_FlowerYellow__WB_FlowerYellow']={-49.207,17.128,-82.0,16.367,0.643,21.385,2,false,'WB_FlowerYellow','','WB_House_FW'},
  ['WB_House_FW__WB_Glass__WB_Glass']={-50.0,18.245,-82.0,16.651,15.29,20.143,2,true,'WB_Glass','','WB_House_FW'},
  ['WB_House_FW__WB_Iron__WB_Iron']={-42.065,11.915,-84.396,1.911,6.97,6.704,2,false,'WB_Iron','','WB_House_FW'},
  ['WB_House_FW__WB_LampGlow__WB_LampGlow']={-41.563,13.2,-81.498,0.648,1.4,0.648,2,false,'WB_LampGlow','','WB_House_FW'},
  ['WB_House_FW__WB_Leaf__WB_Leaf']={-49.321,16.92,-82.0,17.022,0.881,21.869,2,true,'WB_Leaf','','WB_House_FW'},
  ['WB_House_FW__WB_Plank__WB_Plank']={-50.0,13.49,-82.0,18.51,12.58,22.812,2,true,'WB_Plank','','WB_House_FW'},
  ['WB_House_FW__WB_Plaster_Ochre__WB_Plaster_Ochre']={-50.0,24.085,-82.0,17.39,18.171,21.044,2,true,'WB_Plaster_Ochre','','WB_House_FW'},
  ['WB_House_FW__WB_Roof_Dark__WB_Roof_Dark']={-50.0,28.6,-82.0,20.429,14.43,24.259,2,true,'WB_Roof_Dark','','WB_House_FW'},
  ['WB_House_FW__WB_Stone__WB_Stone']={-50.0,22.668,-82.0,15.446,29.735,19.1,2,true,'WB_Stone','','WB_House_FW'},
  ['WB_House_FW__WB_Stone_Dark__WB_Stone_Dark']={-49.576,22.268,-82.0,17.159,31.535,19.964,2,true,'WB_Stone_Dark','','WB_House_FW'},
  ['WB_House_FW__WB_Timber__WB_Timber']={-50.0,19.976,-82.0,20.454,23.293,24.565,2,true,'WB_Timber','','WB_House_FW'},
  ['WB_House_PAD__WB_Dark__WB_Dark']={-53.595,25.494,-62.729,10.778,25.389,11.024,2,false,'WB_Dark','','WB_House_PAD'},
  ['WB_House_PAD__WB_FlowerRed__WB_FlowerRed']={-57.172,20.222,-57.577,19.679,6.833,25.301,2,false,'WB_FlowerRed','','WB_House_PAD'},
  ['WB_House_PAD__WB_FlowerYellow__WB_FlowerYellow']={-56.542,20.178,-56.478,18.922,6.818,20.936,2,false,'WB_FlowerYellow','','WB_House_PAD'},
  ['WB_House_PAD__WB_Glass__WB_Glass']={-58.0,18.194,-58.0,20.795,15.187,25.685,2,true,'WB_Glass','','WB_House_PAD'},
  ['WB_House_PAD__WB_Iron__WB_Iron']={-51.585,13.985,-53.716,6.82,11.11,14.132,2,true,'WB_Iron','','WB_House_PAD'},
  ['WB_House_PAD__WB_LampGlow__WB_LampGlow']={-49.682,13.2,-54.624,0.805,1.4,0.805,2,false,'WB_LampGlow','','WB_House_PAD'},
  ['WB_House_PAD__WB_Leaf__WB_Leaf']={-56.949,19.931,-57.633,20.014,7.005,25.48,2,true,'WB_Leaf','','WB_House_PAD'},
  ['WB_House_PAD__WB_Plank__WB_Plank']={-58.0,16.285,-58.0,22.684,18.17,28.524,2,true,'WB_Plank','','WB_House_PAD'},
  ['WB_House_PAD__WB_Plaster__WB_Plaster']={-58.0,23.852,-58.0,24.776,17.705,27.012,2,true,'WB_Plaster','','WB_House_PAD'},
  ['WB_House_PAD__WB_Roof__WB_Roof']={-58.0,28.303,-58.0,28.692,13.847,30.848,2,true,'WB_Roof','','WB_House_PAD'},
  ['WB_House_PAD__WB_Roof_Dark__WB_Roof_Dark']={-55.777,32.079,-58.0,16.789,6.979,22.808,2,false,'WB_Roof_Dark','','WB_House_PAD'},
  ['WB_House_PAD__WB_SignText__WB_SignText']={-53.573,17.847,-47.401,3.299,0.597,2.012,2,false,'WB_SignText','','WB_House_PAD'},
  ['WB_House_PAD__WB_Stone__WB_Stone']={-58.0,22.544,-58.0,22.361,29.489,24.597,2,true,'WB_Stone','','WB_House_PAD'},
  ['WB_House_PAD__WB_Stone_Dark__WB_Stone_Dark']={-58.0,22.144,-58.0,23.434,31.289,25.67,2,true,'WB_Stone_Dark','','WB_House_PAD'},
  ['WB_House_PAD__WB_Timber__WB_Timber']={-58.0,19.776,-58.0,28.979,22.892,30.992,2,true,'WB_Timber','','WB_House_PAD'},
  ['WB_House_S1E__WB_Dark__WB_Dark']={21.845,29.629,67.9,13.39,33.658,5.6,2,true,'WB_Dark','','WB_House_S1E'},
  ['WB_House_S1E__WB_FlowerPink__WB_FlowerPink']={20.836,20.412,64.0,15.953,7.134,22.429,2,false,'WB_FlowerPink','','WB_House_S1E'},
  ['WB_House_S1E__WB_FlowerYellow__WB_FlowerYellow']={20.607,20.413,64.0,15.524,7.024,22.338,2,false,'WB_FlowerYellow','','WB_House_S1E'},
  ['WB_House_S1E__WB_Glass__WB_Glass']={22.0,21.651,64.0,16.78,22.102,20.78,2,true,'WB_Glass','','WB_House_S1E'},
  ['WB_House_S1E__WB_Iron__WB_Iron']={14.127,11.915,67.065,1.993,6.97,6.57,2,false,'WB_Iron','','WB_House_S1E'},
  ['WB_House_S1E__WB_LampGlow__WB_LampGlow']={13.55,13.2,64.2,0.6,1.4,0.6,2,false,'WB_LampGlow','','WB_House_S1E'},
  ['WB_House_S1E__WB_Leaf__WB_Leaf']={20.867,20.114,64.0,16.217,7.403,22.52,2,true,'WB_Leaf','','WB_House_S1E'},
  ['WB_House_S1E__WB_Plank__WB_Plank']={21.42,16.74,64.0,18.64,19.08,22.48,2,true,'WB_Plank','','WB_House_S1E'},
  ['WB_House_S1E__WB_Plaster__WB_Plaster']={22.0,28.045,64.0,16.88,26.09,20.88,2,true,'WB_Plaster','','WB_House_S1E'},
  ['WB_House_S1E__WB_Roof__WB_Roof']={22.0,35.696,64.0,19.68,15.628,23.866,2,true,'WB_Roof','','WB_House_S1E'},
  ['WB_House_S1E__WB_Roof_Dark__WB_Roof_Dark']={22.0,43.538,64.0,19.88,0.6,1.4,2,false,'WB_Roof_Dark','','WB_House_S1E'},
  ['WB_House_S1E__WB_Stone__WB_Stone']={22.0,26.679,64.0,14.0,37.758,18.0,2,true,'WB_Stone','','WB_House_S1E'},
  ['WB_House_S1E__WB_Stone_Dark__WB_Stone_Dark']={21.5,26.279,64.0,15.8,39.558,19.0,2,true,'WB_Stone_Dark','','WB_House_S1E'},
  ['WB_House_S1E__WB_Timber__WB_Timber']={21.945,23.836,64.0,19.79,31.013,24.18,2,true,'WB_Timber','','WB_House_S1E'},
  ['WB_House_S1W__WB_Dark__WB_Dark']={-20.775,25.087,70.9,12.25,24.574,16.2,2,true,'WB_Dark','','WB_House_S1W'},
  ['WB_House_S1W__WB_FlowerRed__WB_FlowerRed']={-13.218,23.339,69.929,0.448,0.669,10.857,2,false,'WB_FlowerRed','','WB_House_S1W'},
  ['WB_House_S1W__WB_FlowerYellow__WB_FlowerYellow']={-19.647,20.143,70.0,13.397,6.658,23.167,2,false,'WB_FlowerYellow','','WB_House_S1W'},
  ['WB_House_S1W__WB_Glass__WB_Glass']={-22.0,18.117,70.0,16.7,15.033,21.7,2,true,'WB_Glass','','WB_House_S1W'},
  ['WB_House_S1W__WB_Iron__WB_Iron']={-13.627,11.915,66.435,1.993,6.97,6.57,2,false,'WB_Iron','','WB_House_S1W'},
  ['WB_House_S1W__WB_LampGlow__WB_LampGlow']={-13.05,13.2,69.3,0.6,1.4,0.6,2,false,'WB_LampGlow','','WB_House_S1W'},
  ['WB_House_S1W__WB_Leaf__WB_Leaf']={-19.659,19.975,70.0,13.809,7.053,23.525,2,true,'WB_Leaf','','WB_House_S1W'},
  ['WB_House_S1W__WB_Plank__WB_Plank']={-21.75,16.285,70.0,17.9,18.17,23.4,2,true,'WB_Plank','','WB_House_S1W'},
  ['WB_House_S1W__WB_Plaster_Ochre__WB_Plaster_Ochre']={-22.0,23.503,70.0,16.8,17.007,21.8,2,true,'WB_Plaster_Ochre','','WB_House_S1W'},
  ['WB_House_S1W__WB_Roof__WB_Roof']={-22.0,27.904,70.0,19.786,13.044,24.6,2,true,'WB_Roof','','WB_House_S1W'},
  ['WB_House_S1W__WB_Roof_Dark__WB_Roof_Dark']={-17.725,31.672,70.0,9.95,6.164,24.8,2,false,'WB_Roof_Dark','','WB_House_S1W'},
  ['WB_House_S1W__WB_Stone__WB_Stone']={-22.0,22.137,70.0,15.0,28.674,20.0,2,true,'WB_Stone','','WB_House_S1W'},
  ['WB_House_S1W__WB_Stone_Dark__WB_Stone_Dark']={-21.5,21.737,70.0,16.8,30.474,21.0,2,true,'WB_Stone_Dark','','WB_House_S1W'},
  ['WB_House_S1W__WB_Timber__WB_Timber']={-22.0,19.476,70.0,20.1,22.292,24.6,2,true,'WB_Timber','','WB_House_S1W'},
  ['WB_House_S2E__WB_Dark__WB_Dark']={20.775,24.976,97.9,12.25,24.352,6.2,2,false,'WB_Dark','','WB_House_S2E'},
  ['WB_House_S2E__WB_FlowerYellow__WB_FlowerYellow']={19.716,17.142,92.0,13.615,0.64,23.32,2,false,'WB_FlowerYellow','','WB_House_S2E'},
  ['WB_House_S2E__WB_Glass__WB_Glass']={22.0,18.096,92.0,16.7,14.992,21.7,2,true,'WB_Glass','','WB_House_S2E'},
  ['WB_House_S2E__WB_Iron__WB_Iron']={13.627,11.915,95.565,1.993,6.97,6.57,2,false,'WB_Iron','','WB_House_S2E'},
  ['WB_House_S2E__WB_LampGlow__WB_LampGlow']={13.05,13.2,92.7,0.6,1.4,0.6,2,false,'WB_LampGlow','','WB_House_S2E'},
  ['WB_House_S2E__WB_Leaf__WB_Leaf']={19.683,16.885,92.0,13.7,0.854,23.433,2,true,'WB_Leaf','','WB_House_S2E'},
  ['WB_House_S2E__WB_Plank__WB_Plank']={21.75,13.49,92.0,17.9,12.58,23.4,2,true,'WB_Plank','','WB_House_S2E'},
  ['WB_House_S2E__WB_Plaster_Ochre__WB_Plaster_Ochre']={22.0,23.408,92.0,16.8,16.816,21.8,2,true,'WB_Plaster_Ochre','','WB_House_S2E'},
  ['WB_House_S2E__WB_Roof_Dark__WB_Roof_Dark']={22.0,27.958,92.0,19.788,13.149,24.8,2,true,'WB_Roof_Dark','','WB_House_S2E'},
  ['WB_House_S2E__WB_Stone__WB_Stone']={22.0,22.026,92.0,15.0,28.452,20.0,2,true,'WB_Stone','','WB_House_S2E'},
  ['WB_House_S2E__WB_Stone_Dark__WB_Stone_Dark']={21.5,21.626,92.0,16.8,30.252,21.0,2,true,'WB_Stone_Dark','','WB_House_S2E'},
  ['WB_House_S2E__WB_Timber__WB_Timber']={22.0,19.394,92.0,20.1,22.128,24.6,2,true,'WB_Timber','','WB_House_S2E'},
  ['WB_House_S2W__WB_Dark__WB_Dark']={-23.845,31.054,95.4,15.39,36.508,10.2,2,true,'WB_Dark','','WB_House_S2W'},
  ['WB_House_S2W__WB_FlowerYellow__WB_FlowerYellow']={-21.401,20.38,98.0,15.132,7.224,26.37,2,false,'WB_FlowerYellow','','WB_House_S2W'},
  ['WB_House_S2W__WB_Glass__WB_Glass']={-24.0,21.961,98.0,18.78,22.721,24.78,2,true,'WB_Glass','','WB_House_S2W'},
  ['WB_House_S2W__WB_Iron__WB_Iron']={-14.8,13.985,98.635,3.12,11.11,15.97,2,true,'WB_Iron','','WB_House_S2W'},
  ['WB_House_S2W__WB_LampGlow__WB_LampGlow']={-14.55,13.2,96.8,0.6,1.4,0.6,2,false,'WB_LampGlow','','WB_House_S2W'},
  ['WB_House_S2W__WB_Leaf__WB_Leaf']={-21.344,20.16,98.0,15.19,7.341,26.608,2,true,'WB_Leaf','','WB_House_S2W'},
  ['WB_House_S2W__WB_Plank__WB_Plank']={-23.37,16.74,98.0,20.74,19.08,26.48,2,true,'WB_Plank','','WB_House_S2W'},
  ['WB_House_S2W__WB_Plaster__WB_Plaster']={-24.0,29.453,98.0,18.88,28.907,24.88,2,true,'WB_Plaster','','WB_House_S2W'},
  ['WB_House_S2W__WB_Roof__WB_Roof']={-24.0,37.119,98.0,21.68,18.474,27.864,2,true,'WB_Roof','','WB_House_S2W'},
  ['WB_House_S2W__WB_Roof_Dark__WB_Roof_Dark']={-24.0,46.388,98.0,21.88,0.6,1.4,2,false,'WB_Roof_Dark','','WB_House_S2W'},
  ['WB_House_S2W__WB_SignText__WB_SignText']={-14.8,17.841,106.5,3.633,0.533,0.46,2,false,'WB_SignText','','WB_House_S2W'},
  ['WB_House_S2W__WB_Stone__WB_Stone']={-24.0,28.104,98.0,16.0,40.608,22.0,2,true,'WB_Stone','','WB_House_S2W'},
  ['WB_House_S2W__WB_Stone_Dark__WB_Stone_Dark']={-23.5,27.704,98.0,17.8,42.408,23.0,2,true,'WB_Stone_Dark','','WB_House_S2W'},
  ['WB_House_S2W__WB_Timber__WB_Timber']={-23.845,25.048,98.0,21.99,33.436,28.18,2,true,'WB_Timber','','WB_House_S2W'},
  ['WB_House_S3E__WB_Dark__WB_Dark']={20.9,24.115,125.15,11.5,22.629,5.7,2,false,'WB_Dark','','WB_House_S3E'},
  ['WB_House_S3E__WB_FlowerRed__WB_FlowerRed']={21.179,16.966,120.0,15.571,13.315,21.19,2,false,'WB_FlowerRed','','WB_House_S3E'},
  ['WB_House_S3E__WB_FlowerYellow__WB_FlowerYellow']={20.878,14.025,120.0,14.924,6.942,20.981,2,false,'WB_FlowerYellow','','WB_House_S3E'},
  ['WB_House_S3E__WB_Glass__WB_Glass']={22.0,17.935,120.0,15.7,14.67,19.7,2,true,'WB_Glass','','WB_House_S3E'},
  ['WB_House_S3E__WB_Iron__WB_Iron']={14.127,11.915,123.065,1.993,6.97,6.57,2,false,'WB_Iron','','WB_House_S3E'},
  ['WB_House_S3E__WB_LampGlow__WB_LampGlow']={13.55,13.2,120.2,0.6,1.4,0.6,2,false,'WB_LampGlow','','WB_House_S3E'},
  ['WB_House_S3E__WB_Leaf__WB_Leaf']={21.098,16.696,120.0,15.659,13.518,21.489,2,true,'WB_Leaf','','WB_House_S3E'},
  ['WB_House_S3E__WB_Plank__WB_Plank']={21.868,16.285,120.0,17.137,18.17,21.524,2,true,'WB_Plank','','WB_House_S3E'},
  ['WB_House_S3E__WB_Plaster_Ochre__WB_Plaster_Ochre']={22.0,20.18,120.0,15.8,20.159,19.8,2,true,'WB_Plaster_Ochre','','WB_House_S3E'},
  ['WB_House_S3E__WB_Roof__WB_Roof']={22.0,26.948,120.0,18.8,11.119,22.6,2,true,'WB_Roof','','WB_House_S3E'},
  ['WB_House_S3E__WB_Roof_Dark__WB_Roof_Dark']={17.975,30.7,120.0,9.45,4.22,22.8,2,false,'WB_Roof_Dark','','WB_House_S3E'},
  ['WB_House_S3E__WB_Stone__WB_Stone']={22.0,21.165,120.0,14.0,26.729,18.0,2,true,'WB_Stone','','WB_House_S3E'},
  ['WB_House_S3E__WB_Stone_Dark__WB_Stone_Dark']={21.5,20.765,120.0,15.8,28.529,18.8,2,true,'WB_Stone_Dark','','WB_House_S3E'},
  ['WB_House_S3E__WB_Timber__WB_Timber']={22.0,18.725,120.0,19.1,20.789,22.6,2,true,'WB_Timber','','WB_House_S3E'},
  ['WB_House_S3W__WB_Dark__WB_Dark']={-20.575,25.062,123.9,12.85,24.523,9.2,2,false,'WB_Dark','','WB_House_S3W'},
  ['WB_House_S3W__WB_FlowerPink__WB_FlowerPink']={-20.135,17.144,126.0,15.425,0.655,21.183,2,false,'WB_FlowerPink','','WB_House_S3W'},
  ['WB_House_S3W__WB_FlowerRed__WB_FlowerRed']={-13.604,10.657,128.239,0.59,0.561,6.621,2,false,'WB_FlowerRed','','WB_House_S3W'},
  ['WB_House_S3W__WB_FlowerYellow__WB_FlowerYellow']={-19.661,13.946,126.0,14.528,7.052,21.274,2,false,'WB_FlowerYellow','','WB_House_S3W'},
  ['WB_House_S3W__WB_Glass__WB_Glass']={-21.0,18.138,126.0,15.7,15.075,19.7,2,true,'WB_Glass','','WB_House_S3W'},
  ['WB_House_S3W__WB_Iron__WB_Iron']={-13.127,11.915,122.935,1.993,6.97,6.57,2,false,'WB_Iron','','WB_House_S3W'},
  ['WB_House_S3W__WB_LampGlow__WB_LampGlow']={-12.55,13.2,125.8,0.6,1.4,0.6,2,false,'WB_LampGlow','','WB_House_S3W'},
  ['WB_House_S3W__WB_Leaf__WB_Leaf']={-20.169,13.641,126.0,15.742,7.366,21.421,2,true,'WB_Leaf','','WB_House_S3W'},
  ['WB_House_S3W__WB_Plank__WB_Plank']={-20.868,13.49,126.0,17.137,12.58,21.524,2,true,'WB_Plank','','WB_House_S3W'},
  ['WB_House_S3W__WB_Plaster__WB_Plaster']={-21.0,21.148,126.0,15.8,22.096,19.8,2,true,'WB_Plaster','','WB_House_S3W'},
  ['WB_House_S3W__WB_Roof__WB_Roof']={-21.0,27.898,126.0,18.6,13.017,22.803,2,true,'WB_Roof','','WB_House_S3W'},
  ['WB_House_S3W__WB_Roof_Dark__WB_Roof_Dark']={-21.0,34.403,126.0,18.8,0.6,1.4,2,false,'WB_Roof_Dark','','WB_House_S3W'},
  ['WB_House_S3W__WB_Stone__WB_Stone']={-21.0,22.112,126.0,14.0,28.623,18.0,2,true,'WB_Stone','','WB_House_S3W'},
  ['WB_House_S3W__WB_Stone_Dark__WB_Stone_Dark']={-20.5,21.712,126.0,15.8,30.423,18.8,2,true,'WB_Stone_Dark','','WB_House_S3W'},
  ['WB_House_S3W__WB_Timber__WB_Timber']={-21.0,19.557,126.0,18.6,22.455,23.1,2,true,'WB_Timber','','WB_House_S3W'},
  ['WB_House_SE__WB_Dark__WB_Dark']={62.229,27.719,29.367,11.348,29.837,10.785,2,true,'WB_Dark','','WB_House_SE'},
  ['WB_House_SE__WB_FlowerPink__WB_FlowerPink']={64.517,23.618,23.969,19.296,0.677,25.581,2,false,'WB_FlowerPink','','WB_House_SE'},
  ['WB_House_SE__WB_FlowerRed__WB_FlowerRed']={64.622,23.46,23.781,18.929,13.369,24.597,2,false,'WB_FlowerRed','','WB_House_SE'},
  ['WB_House_SE__WB_FlowerYellow__WB_FlowerYellow']={64.743,23.464,23.568,19.947,13.331,25.716,2,false,'WB_FlowerYellow','','WB_House_SE'},
  ['WB_House_SE__WB_Glass__WB_Glass']={66.0,21.259,24.0,21.491,21.318,26.232,2,true,'WB_Glass','','WB_House_SE'},
  ['WB_House_SE__WB_Iron__WB_Iron']={57.644,11.915,24.303,2.318,6.97,6.811,2,false,'WB_Iron','','WB_House_SE'},
  ['WB_House_SE__WB_LampGlow__WB_LampGlow']={57.395,13.2,21.44,0.775,1.4,0.775,2,false,'WB_LampGlow','','WB_House_SE'},
  ['WB_House_SE__WB_Leaf__WB_Leaf']={64.69,23.22,23.781,19.976,13.589,26.259,2,true,'WB_Leaf','','WB_House_SE'},
  ['WB_House_SE__WB_Plank__WB_Plank']={65.984,19.535,24.0,23.19,24.67,29.119,2,true,'WB_Plank','','WB_House_SE'},
  ['WB_House_SE__WB_Plaster__WB_Plaster']={66.0,26.265,24.0,24.902,22.529,27.773,2,true,'WB_Plaster','','WB_House_SE'},
  ['WB_House_SE__WB_Roof__WB_Roof']={66.0,33.807,24.0,28.711,11.834,31.465,2,true,'WB_Roof','','WB_House_SE'},
  ['WB_House_SE__WB_Roof_Dark__WB_Roof_Dark']={63.099,37.554,24.0,16.398,4.927,24.658,2,true,'WB_Roof_Dark','','WB_House_SE'},
  ['WB_House_SE__WB_Stone__WB_Stone']={66.0,24.769,24.0,21.18,33.937,24.052,2,true,'WB_Stone','','WB_House_SE'},
  ['WB_House_SE__WB_Stone_Dark__WB_Stone_Dark']={65.943,24.369,24.0,22.328,35.737,25.085,2,true,'WB_Stone_Dark','','WB_House_SE'},
  ['WB_House_SE__WB_Timber__WB_Timber']={66.0,22.306,24.0,28.987,27.951,31.571,2,true,'WB_Timber','','WB_House_SE'},
  ['WB_House_SW__WB_Dark__WB_Dark']={-48.228,25.299,61.318,8.299,24.997,14.836,2,true,'WB_Dark','','WB_House_SW'},
  ['WB_House_SW__WB_FlowerRed__WB_FlowerRed']={-46.0,17.141,59.994,23.728,0.704,15.333,2,false,'WB_FlowerRed','','WB_House_SW'},
  ['WB_House_SW__WB_FlowerYellow__WB_FlowerYellow']={-38.83,17.162,53.96,7.681,0.635,1.211,2,false,'WB_FlowerYellow','','WB_House_SW'},
  ['WB_House_SW__WB_Glass__WB_Glass']={-46.0,18.197,62.0,22.552,15.195,18.045,2,true,'WB_Glass','','WB_House_SW'},
  ['WB_House_SW__WB_Iron__WB_Iron']={-48.613,11.915,53.524,6.739,6.97,1.922,2,false,'WB_Iron','','WB_House_SW'},
  ['WB_House_SW__WB_LampGlow__WB_LampGlow']={-45.707,13.2,53.027,0.663,1.4,0.663,2,false,'WB_LampGlow','','WB_House_SW'},
  ['WB_House_SW__WB_Leaf__WB_Leaf']={-46.0,16.869,59.989,24.073,0.905,15.43,2,true,'WB_Leaf','','WB_House_SW'},
  ['WB_House_SW__WB_Plank__WB_Plank']={-46.0,13.49,61.818,24.97,12.58,19.415,2,true,'WB_Plank','','WB_House_SW'},
  ['WB_House_SW__WB_Plaster_Ochre__WB_Plaster_Ochre']={-46.0,23.87,62.0,23.522,17.741,19.105,2,true,'WB_Plaster_Ochre','','WB_House_SW'},
  ['WB_House_SW__WB_Roof__WB_Roof']={-46.0,28.141,62.0,26.821,13.499,22.22,2,true,'WB_Roof','','WB_House_SW'},
  ['WB_House_SW__WB_Roof_Dark__WB_Roof_Dark']={-46.0,34.877,62.0,3.578,0.6,19.833,2,false,'WB_Roof_Dark','','WB_House_SW'},
  ['WB_House_SW__WB_Stone__WB_Stone']={-46.0,22.349,62.0,21.534,29.097,17.117,2,true,'WB_Stone','','WB_House_SW'},
  ['WB_House_SW__WB_Stone_Dark__WB_Stone_Dark']={-46.0,21.949,61.629,22.418,30.897,18.742,2,true,'WB_Stone_Dark','','WB_House_SW'},
  ['WB_House_SW__WB_Timber__WB_Timber']={-46.0,19.792,62.0,27.111,22.923,22.252,2,true,'WB_Timber','','WB_House_SW'},
  ['WB_House_TAV__WB_Dark__WB_Dark']={58.61,30.809,-45.531,11.024,36.018,17.932,2,true,'WB_Dark','','WB_House_TAV'},
  ['WB_House_TAV__WB_FlowerRed__WB_FlowerRed']={48.766,10.655,-45.874,4.463,0.727,6.626,2,false,'WB_FlowerRed','','WB_House_TAV'},
  ['WB_House_TAV__WB_FlowerYellow__WB_FlowerYellow']={57.53,17.145,-48.0,25.956,13.671,33.55,2,false,'WB_FlowerYellow','','WB_House_TAV'},
  ['WB_House_TAV__WB_Glass__WB_Glass']={58.0,21.925,-48.0,26.169,22.65,32.685,2,true,'WB_Glass','','WB_House_TAV'},
  ['WB_House_TAV__WB_Iron__WB_Iron']={49.276,13.985,-44.139,11.867,11.11,14.793,2,true,'WB_Iron','','WB_House_TAV'},
  ['WB_House_TAV__WB_LampGlow__WB_LampGlow']={50.609,13.2,-41.125,0.831,1.4,0.831,2,false,'WB_LampGlow','','WB_House_TAV'},
  ['WB_House_TAV__WB_Leaf__WB_Leaf']={57.632,16.908,-48.0,26.275,13.893,33.607,2,true,'WB_Leaf','','WB_House_TAV'},
  ['WB_House_TAV__WB_Plank__WB_Plank']={57.643,16.74,-48.0,29.015,19.08,34.818,2,true,'WB_Plank','','WB_House_TAV'},
  ['WB_House_TAV__WB_Plaster_Ochre__WB_Plaster_Ochre']={58.0,26.842,-48.0,31.36,33.484,33.379,2,true,'WB_Plaster_Ochre','','WB_House_TAV'},
  ['WB_House_TAV__WB_Roof_Dark__WB_Roof_Dark']={58.0,37.042,-48.0,35.343,18.312,37.419,2,true,'WB_Roof_Dark','','WB_House_TAV'},
  ['WB_House_TAV__WB_SignText__WB_SignText']={44.68,17.845,-50.631,3.474,0.602,2.479,2,false,'WB_SignText','','WB_House_TAV'},
  ['WB_House_TAV__WB_Stone__WB_Stone']={58.0,27.859,-48.0,27.372,40.118,29.392,2,true,'WB_Stone','','WB_House_TAV'},
  ['WB_House_TAV__WB_Stone_Dark__WB_Stone_Dark']={58.0,27.459,-48.0,28.48,41.918,30.499,2,true,'WB_Stone_Dark','','WB_House_TAV'},
  ['WB_House_TAV__WB_Timber__WB_Timber']={58.0,24.909,-48.0,35.51,33.158,37.674,2,true,'WB_Timber','','WB_House_TAV'},
  ['WB_House_W1__WB_Dark__WB_Dark']={-80.413,25.525,29.99,19.47,25.45,7.818,2,true,'WB_Dark','','WB_House_W1'},
  ['WB_House_W1__WB_FlowerRed__WB_FlowerRed']={-80.0,16.998,29.894,24.548,13.393,20.126,2,false,'WB_FlowerRed','','WB_House_W1'},
  ['WB_House_W1__WB_FlowerYellow__WB_FlowerYellow']={-80.0,16.957,29.718,19.64,13.258,16.744,2,false,'WB_FlowerYellow','','WB_House_W1'},
  ['WB_House_W1__WB_Glass__WB_Glass']={-80.0,18.199,28.0,23.45,15.199,22.788,2,true,'WB_Glass','','WB_House_W1'},
  ['WB_House_W1__WB_Iron__WB_Iron']={-73.892,11.915,34.637,5.92,6.97,4.077,2,false,'WB_Iron','','WB_House_W1'},
  ['WB_House_W1__WB_LampGlow__WB_LampGlow']={-76.202,13.2,36.134,0.772,1.4,0.772,2,false,'WB_LampGlow','','WB_House_W1'},
  ['WB_House_W1__WB_Leaf__WB_Leaf']={-80.0,16.734,29.895,24.57,13.488,20.229,2,true,'WB_Leaf','','WB_House_W1'},
  ['WB_House_W1__WB_Plank__WB_Plank']={-80.0,16.285,28.021,25.183,18.17,24.478,2,true,'WB_Plank','','WB_House_W1'},
  ['WB_House_W1__WB_Plaster__WB_Plaster']={-80.0,21.428,28.0,26.311,22.657,23.385,2,true,'WB_Plaster','','WB_House_W1'},
  ['WB_House_W1__WB_Roof__WB_Roof']={-80.0,28.333,28.0,29.978,13.907,27.157,2,true,'WB_Roof','','WB_House_W1'},
  ['WB_House_W1__WB_Roof_Dark__WB_Roof_Dark']={-80.0,32.11,30.746,23.713,7.04,15.511,2,false,'WB_Roof_Dark','','WB_House_W1'},
  ['WB_House_W1__WB_Stone__WB_Stone']={-80.0,22.575,28.0,23.993,29.55,21.067,2,true,'WB_Stone','','WB_House_W1'},
  ['WB_House_W1__WB_Stone_Dark__WB_Stone_Dark']={-80.0,22.175,28.0,25.023,31.35,22.097,2,true,'WB_Stone_Dark','','WB_House_W1'},
  ['WB_House_W1__WB_Timber__WB_Timber']={-80.0,19.798,28.0,30.091,22.937,27.458,2,true,'WB_Timber','','WB_House_W1'},
  ['WB_House_W2__WB_Dark__WB_Dark']={-75.911,30.851,70.84,11.008,36.103,13.249,2,true,'WB_Dark','','WB_House_W2'},
  ['WB_House_W2__WB_FlowerPink__WB_FlowerPink']={-72.0,17.132,68.322,19.702,0.701,20.155,2,false,'WB_FlowerPink','','WB_House_W2'},
  ['WB_House_W2__WB_FlowerRed__WB_FlowerRed']={-72.885,10.654,61.913,5.994,0.636,2.656,2,false,'WB_FlowerRed','','WB_House_W2'},
  ['WB_House_W2__WB_FlowerYellow__WB_FlowerYellow']={-72.0,17.163,67.983,25.617,13.627,21.57,2,false,'WB_FlowerYellow','','WB_House_W2'},
  ['WB_House_W2__WB_Glass__WB_Glass']={-72.0,21.906,70.0,24.624,22.611,24.407,2,true,'WB_Glass','','WB_House_W2'},
  ['WB_House_W2__WB_Iron__WB_Iron']={-78.232,11.915,63.502,5.872,6.97,4.195,2,false,'WB_Iron','','WB_House_W2'},
  ['WB_House_W2__WB_LampGlow__WB_LampGlow']={-75.974,13.2,61.95,0.78,1.4,0.78,2,false,'WB_LampGlow','','WB_House_W2'},
  ['WB_House_W2__WB_Leaf__WB_Leaf']={-72.0,16.883,68.045,25.504,13.838,21.492,2,true,'WB_Leaf','','WB_House_W2'},
  ['WB_House_W2__WB_Plank__WB_Plank']={-72.0,16.74,69.993,26.351,19.08,26.119,2,true,'WB_Plank','','WB_House_W2'},
  ['WB_House_W2__WB_Plaster_Ochre__WB_Plaster_Ochre']={-72.0,26.753,70.0,27.884,33.305,25.099,2,true,'WB_Plaster_Ochre','','WB_House_W2'},
  ['WB_House_W2__WB_Roof_Dark__WB_Roof_Dark']={-72.0,37.081,70.0,31.689,18.403,28.804,2,true,'WB_Roof_Dark','','WB_House_W2'},
  ['WB_House_W2__WB_Stone__WB_Stone']={-72.0,27.901,70.0,24.14,40.203,21.355,2,true,'WB_Stone','','WB_House_W2'},
  ['WB_House_W2__WB_Stone_Dark__WB_Stone_Dark']={-72.0,27.501,70.0,25.18,42.003,22.395,2,true,'WB_Stone_Dark','','WB_House_W2'},
  ['WB_House_W2__WB_Timber__WB_Timber']={-72.0,24.832,70.0,31.988,33.004,28.924,2,true,'WB_Timber','','WB_House_W2'},
  ['WB_Town_Plaza__WB_Apple__WB_Apple']={42.908,10.6,4.0,1.578,0.8,6.8,2,false,'WB_Apple','',''},
  ['WB_Town_Plaza__WB_Brass__WB_Brass']={-26.0,9.5,8.0,2.908,0.512,2.908,2,false,'WB_Brass','',''},
  ['WB_Town_Plaza__WB_Bread__WB_Bread']={32.658,10.65,24.0,2.854,0.8,6.9,2,false,'WB_Bread','',''},
  ['WB_Town_Plaza__WB_CanvasBlue__WB_CanvasBlue']={43.962,11.386,4.0,7.824,6.772,9.6,2,false,'WB_CanvasBlue','',''},
  ['WB_Town_Plaza__WB_CanvasGreen__WB_CanvasGreen']={35.962,11.386,-16.0,7.824,6.772,9.6,2,false,'WB_CanvasGreen','',''},
  ['WB_Town_Plaza__WB_CanvasRed__WB_CanvasRed']={33.962,11.386,24.0,7.824,6.772,9.6,2,false,'WB_CanvasRed','',''},
  ['WB_Town_Plaza__WB_Cloth_Blue__WB_Cloth_Blue']={22.083,12.5,10.915,27.366,5.4,60.73,2,true,'WB_Cloth_Blue','',''},
  ['WB_Town_Plaza__WB_Cloth_Cream__WB_Cloth_Cream']={8.1,9.242,1.962,73.412,4.425,71.688,2,true,'WB_Cloth_Cream','',''},
  ['WB_Town_Plaza__WB_Cloth_Gold__WB_Cloth_Gold']={0.0,12.88,41.2,20.088,1.144,0.32,2,false,'WB_Cloth_Gold','',''},
  ['WB_Town_Plaza__WB_Cloth_Red__WB_Cloth_Red']={-9.5,12.5,41.2,2.2,5.4,0.16,2,false,'WB_Cloth_Red','',''},
  ['WB_Town_Plaza__WB_Dark__WB_Dark']={-9.0,7.75,96.0,4.2,0.5,4.2,2,false,'WB_Dark','',''},
  ['WB_Town_Plaza__WB_FlowerYellow__WB_FlowerYellow']={43.308,10.6,3.5,1.544,0.76,6.76,2,false,'WB_FlowerYellow','',''},
  ['WB_Town_Plaza__WB_Iron__WB_Iron']={7.0,11.682,1.15,92.266,8.636,76.566,2,true,'WB_Iron','',''},
  ['WB_Town_Plaza__WB_LampGlow__WB_LampGlow']={4.883,13.9,2.184,80.496,3.8,71.432,2,false,'WB_LampGlow','',''},
  ['WB_Town_Plaza__WB_Plank__WB_Plank']={4.502,11.8,29.75,97.404,9.6,133.7,2,true,'WB_Plank','',''},
  ['WB_Town_Plaza__WB_Roof__WB_Roof']={-9.0,16.994,96.0,4.0,4.19,8.423,2,false,'WB_Roof','',''},
  ['WB_Town_Plaza__WB_Roof_Dark__WB_Roof_Dark']={-9.0,19.152,96.0,4.2,0.6,1.4,2,false,'WB_Roof_Dark','',''},
  ['WB_Town_Plaza__WB_SignText__WB_SignText']={14.205,12.668,31.613,16.55,6.568,22.595,2,true,'WB_SignText','',''},
  ['WB_Town_Plaza__WB_Stone__WB_Stone']={-19.234,11.8,50.266,26.467,10.2,97.467,2,true,'WB_Stone','',''},
  ['WB_Town_Plaza__WB_Stone_Dark__WB_Stone_Dark']={4.963,8.25,32.19,83.763,3.7,134.221,2,true,'WB_Stone_Dark','',''},
  ['WB_Town_Plaza__WB_Timber__WB_Timber']={4.449,12.5,31.7,97.737,12.0,134.0,2,true,'WB_Timber','',''},
  ['WB_Town_Plaza__WB_Water__WB_Water']={-26.0,11.225,8.0,9.978,7.25,9.978,2,false,'WB_Water','',''},
  ['WB_Frg_Hall__WB_Bark__WB_Bark']={0.096,9.046,-47.903,43.895,1.848,3.289,3,true,'WB_Bark','','WB_Forja'},
  ['WB_Frg_Hall__WB_Cloth_Cream__WB_Cloth_Cream']={0.0,7.961,-82.8,16.536,1.858,1.736,3,true,'WB_Cloth_Cream','','WB_Forja'},
  ['WB_Frg_Hall__WB_Dark__WB_Dark']={0.0,35.8,-65.3,46.0,58.2,38.2,3,true,'WB_Dark','','WB_Forja'},
  ['WB_Frg_Hall__WB_Ember__WB_Ember']={0.0,8.1,-65.6,43.6,2.2,36.8,3,false,'WB_Ember','','WB_Forja'},
  ['WB_Frg_Hall__WB_Fire__WB_Fire']={-0.05,11.1,-66.2,42.7,5.0,39.0,3,false,'WB_Fire','','WB_Forja'},
  ['WB_Frg_Hall__WB_FlowerRed__WB_FlowerRed']={0.0,19.165,-60.112,55.411,0.906,29.707,3,false,'WB_FlowerRed','','WB_Forja'},
  ['WB_Frg_Hall__WB_FlowerYellow__WB_FlowerYellow']={0.0,19.175,-59.588,55.266,0.806,28.338,3,false,'WB_FlowerYellow','','WB_Forja'},
  ['WB_Frg_Hall__WB_Glass__WB_Glass']={0.0,30.599,-66.0,53.9,23.199,41.9,3,true,'WB_Glass','','WB_Forja'},
  ['WB_Frg_Hall__WB_Ingot__WB_Ingot']={0.0,15.15,-66.0,23.2,7.7,29.4,3,false,'WB_Ingot','','WB_Forja'},
  ['WB_Frg_Hall__WB_Iron__WB_Iron']={0.0,16.993,-63.89,48.799,20.014,38.82,3,true,'WB_Iron','','WB_Forja'},
  ['WB_Frg_Hall__WB_LampGlow__WB_LampGlow']={0.0,15.2,-44.9,26.6,1.4,0.6,3,false,'WB_LampGlow','','WB_Forja'},
  ['WB_Frg_Hall__WB_Leaf__WB_Leaf']={0.0,18.911,-60.161,55.428,1.083,30.039,3,true,'WB_Leaf','','WB_Forja'},
  ['WB_Frg_Hall__WB_Plank__WB_Plank']={0.0,24.099,-64.5,55.6,34.199,38.6,3,true,'WB_Plank','','WB_Forja'},
  ['WB_Frg_Hall__WB_Plaster_Ochre__WB_Plaster_Ochre']={0.0,36.447,-66.0,54.0,38.894,41.9,3,true,'WB_Plaster_Ochre','','WB_Forja'},
  ['WB_Frg_Hall__WB_Roof__WB_Roof']={0.0,41.592,-66.0,58.085,34.537,45.2,3,true,'WB_Roof','','WB_Forja'},
  ['WB_Frg_Hall__WB_Roof_Dark__WB_Roof_Dark']={0.0,58.899,-66.0,1.4,0.6,45.4,3,true,'WB_Roof_Dark','','WB_Forja'},
  ['WB_Frg_Hall__WB_SignText__WB_SignText']={0.008,33.679,-44.88,17.087,1.713,0.14,3,true,'WB_SignText','','WB_Forja'},
  ['WB_Frg_Hall__WB_Stone__WB_Stone']={0.0,35.0,-63.0,56.0,58.0,46.0,3,true,'WB_Stone','','WB_Forja'},
  ['WB_Frg_Hall__WB_Stone_Dark__WB_Stone_Dark']={0.0,35.6,-65.0,48.6,57.8,39.2,3,true,'WB_Stone_Dark','','WB_Forja'},
  ['WB_Frg_Hall__WB_Timber__WB_Timber']={0.0,30.097,-66.0,58.0,46.195,45.2,3,true,'WB_Timber','','WB_Forja'},
  ['WB_Rank_Hall__WB_Brass__WB_Brass']={-49.775,29.237,-11.0,23.45,43.726,66.3,4,true,'WB_Brass','','WB_Mural'},
  ['WB_Rank_Hall__WB_Cloth_Blue__WB_Cloth_Blue']={-51.56,30.85,-11.0,22.68,15.3,62.92,4,true,'WB_Cloth_Blue','','WB_Mural'},
  ['WB_Rank_Hall__WB_Cloth_Gold__WB_Cloth_Gold']={-50.966,32.377,-11.0,21.651,8.355,63.52,4,true,'WB_Cloth_Gold','','WB_Mural'},
  ['WB_Rank_Hall__WB_Cloth_Red__WB_Cloth_Red']={-51.37,29.6,-11.0,22.46,17.8,63.36,4,true,'WB_Cloth_Red','','WB_Mural'},
  ['WB_Rank_Hall__WB_Cobble__WB_Cobble']={-50.5,7.475,-11.0,17.6,0.25,60.6,4,true,'WB_Cobble','','WB_Mural'},
  ['WB_Rank_Hall__WB_Dirt__WB_Dirt']={-61.0,7.75,-11.0,5.8,0.1,67.6,4,true,'WB_Dirt','','WB_Mural'},
  ['WB_Rank_Hall__WB_Ember__WB_Ember']={-42.4,9.7,-11.0,2.6,0.4,68.473,4,false,'WB_Ember','','WB_Mural'},
  ['WB_Rank_Hall__WB_Fire__WB_Fire']={-42.4,11.1,-11.0,2.5,2.6,68.5,4,false,'WB_Fire','','WB_Mural'},
  ['WB_Rank_Hall__WB_FlowerPink__WB_FlowerPink']={-62.754,8.458,-11.0,9.902,0.804,68.216,4,false,'WB_FlowerPink','','WB_Mural'},
  ['WB_Rank_Hall__WB_FlowerRed__WB_FlowerRed']={-64.595,8.724,-10.817,6.511,1.227,67.811,4,false,'WB_FlowerRed','','WB_Mural'},
  ['WB_Rank_Hall__WB_FlowerWhite__WB_FlowerWhite']={-66.626,8.824,-22.65,1.787,0.728,31.721,4,false,'WB_FlowerWhite','','WB_Mural'},
  ['WB_Rank_Hall__WB_FlowerYellow__WB_FlowerYellow']={-59.531,8.399,-10.834,1.766,0.694,65.957,4,false,'WB_FlowerYellow','','WB_Mural'},
  ['WB_Rank_Hall__WB_Glass__WB_Glass']={-53.0,41.989,-11.0,1.6,1.8,62.3,4,true,'WB_Glass','','WB_Mural'},
  ['WB_Rank_Hall__WB_Iron__WB_Iron']={-51.775,21.877,-11.0,23.35,28.047,70.4,4,true,'WB_Iron','','WB_Mural'},
  ['WB_Rank_Hall__WB_LampGlow__WB_LampGlow']={-42.0,17.1,-11.0,0.6,1.4,53.2,4,false,'WB_LampGlow','','WB_Mural'},
  ['WB_Rank_Hall__WB_Leaf__WB_Leaf']={-62.778,7.955,-11.042,11.057,2.335,68.497,4,true,'WB_Leaf','','WB_Mural'},
  ['WB_Rank_Hall__WB_Plank__WB_Plank']={-51.65,29.55,-11.0,23.3,18.5,62.96,4,true,'WB_Plank','','WB_Mural'},
  ['WB_Rank_Hall__WB_Plank_Light__WB_Plank_Light']={-56.25,23.004,-11.0,1.8,29.007,53.9,4,true,'WB_Plank_Light','','WB_Mural'},
  ['WB_Rank_Hall__WB_Plaster_Ochre__WB_Plaster_Ochre']={-53.025,42.585,-11.0,21.95,7.369,62.3,4,true,'WB_Plaster_Ochre','','WB_Mural'},
  ['WB_Rank_Hall__WB_Roof_Dark__WB_Roof_Dark']={-53.0,44.001,-11.0,26.255,8.959,66.6,4,true,'WB_Roof_Dark','','WB_Mural'},
  ['WB_Rank_Hall__WB_SignText__WB_SignText']={-48.62,36.302,-10.823,17.44,4.404,31.621,4,true,'WB_SignText','','WB_Mural'},
  ['WB_Rank_Hall__WB_Stone__WB_Stone']={-52.3,22.4,-11.0,23.4,31.6,62.0,4,true,'WB_Stone','','WB_Mural'},
  ['WB_Rank_Hall__WB_Stone_Dark__WB_Stone_Dark']={-52.05,22.6,-11.0,27.7,32.6,69.2,4,true,'WB_Stone_Dark','','WB_Mural'},
  ['WB_Rank_Hall__WB_Timber__WB_Timber']={-53.0,27.453,-11.0,26.5,39.905,66.4,4,true,'WB_Timber','','WB_Mural'},
  ['WB_Shop_Building__WB_Bark__WB_Bark']={65.0,7.971,-23.4,3.819,2.258,2.0,4,false,'WB_Bark','','WB_Loja'},
  ['WB_Shop_Building__WB_Brass__WB_Brass']={65.064,13.201,-9.976,24.674,9.303,22.012,4,true,'WB_Brass','','WB_Loja'},
  ['WB_Shop_Building__WB_CanvasRed__WB_CanvasRed']={52.735,16.079,-15.5,2.69,2.109,7.0,4,false,'WB_CanvasRed','','WB_Loja'},
  ['WB_Shop_Building__WB_Cloth_Blue__WB_Cloth_Blue']={65.912,14.445,-9.348,25.6,8.99,22.495,4,true,'WB_Cloth_Blue','','WB_Loja'},
  ['WB_Shop_Building__WB_Cloth_Cream__WB_Cloth_Cream']={68.462,12.59,-8.476,19.936,10.32,21.364,4,true,'WB_Cloth_Cream','','WB_Loja'},
  ['WB_Shop_Building__WB_Cloth_Gold__WB_Cloth_Gold']={68.368,13.23,-11.95,20.535,11.42,14.7,4,false,'WB_Cloth_Gold','','WB_Loja'},
  ['WB_Shop_Building__WB_Cloth_Green__WB_Cloth_Green']={65.865,14.445,-9.582,25.743,8.99,21.365,4,true,'WB_Cloth_Green','','WB_Loja'},
  ['WB_Shop_Building__WB_Cloth_Purple__WB_Cloth_Purple']={67.206,14.865,-11.782,23.012,2.93,16.965,4,false,'WB_Cloth_Purple','','WB_Loja'},
  ['WB_Shop_Building__WB_Cloth_Red__WB_Cloth_Red']={65.859,12.85,-10.629,25.73,10.82,19.932,4,true,'WB_Cloth_Red','','WB_Loja'},
  ['WB_Shop_Building__WB_Dark__WB_Dark']={72.023,26.2,-4.815,10.554,30.2,7.229,4,true,'WB_Dark','','WB_Loja'},
  ['WB_Shop_Building__WB_FlowerPink__WB_FlowerPink']={66.905,23.923,-23.28,18.397,0.644,0.566,4,false,'WB_FlowerPink','','WB_Loja'},
  ['WB_Shop_Building__WB_FlowerRed__WB_FlowerRed']={63.95,20.59,-8.993,23.112,21.854,27.368,4,false,'WB_FlowerRed','','WB_Loja'},
  ['WB_Shop_Building__WB_FlowerYellow__WB_FlowerYellow']={64.654,20.53,-8.978,24.384,22.014,29.136,4,false,'WB_FlowerYellow','','WB_Loja'},
  ['WB_Shop_Building__WB_Glass__WB_Glass']={67.0,28.927,-9.0,27.7,10.053,27.7,4,true,'WB_Glass','','WB_Loja'},
  ['WB_Shop_Building__WB_Iron__WB_Iron']={65.335,13.435,-10.765,28.19,12.41,27.73,4,true,'WB_Iron','','WB_Loja'},
  ['WB_Shop_Building__WB_LampGlow__WB_LampGlow']={62.575,16.62,-9.0,20.65,3.44,21.3,4,false,'WB_LampGlow','','WB_Loja'},
  ['WB_Shop_Building__WB_Leaf__WB_Leaf']={64.585,20.063,-8.964,24.656,22.565,29.417,4,true,'WB_Leaf','','WB_Loja'},
  ['WB_Shop_Building__WB_Leather__WB_Leather']={76.15,13.137,-6.327,5.099,11.607,18.392,4,true,'WB_Leather','','WB_Loja'},
  ['WB_Shop_Building__WB_LeatherDark__WB_LeatherDark']={65.866,13.639,-9.541,26.126,11.141,22.737,4,true,'WB_LeatherDark','','WB_Loja'},
  ['WB_Shop_Building__WB_Paper__WB_Paper']={66.9,11.41,-6.3,1.803,0.3,2.501,4,false,'WB_Paper','','WB_Loja'},
  ['WB_Shop_Building__WB_Plank__WB_Plank']={66.1,20.035,-9.511,30.2,26.47,30.422,4,true,'WB_Plank','','WB_Loja'},
  ['WB_Shop_Building__WB_Plank_Light__WB_Plank_Light']={63.9,11.565,-8.574,14.9,8.33,22.849,4,true,'WB_Plank_Light','','WB_Loja'},
  ['WB_Shop_Building__WB_Plaster__WB_Plaster']={67.0,24.858,-9.0,27.8,33.916,27.8,4,true,'WB_Plaster','','WB_Loja'},
  ['WB_Shop_Building__WB_Roof__WB_Roof']={67.0,36.548,-9.0,30.823,14.497,30.6,4,true,'WB_Roof','','WB_Loja'},
  ['WB_Shop_Building__WB_Roof_Dark__WB_Roof_Dark']={59.975,40.273,-9.0,15.45,7.566,30.8,4,true,'WB_Roof_Dark','','WB_Loja'},
  ['WB_Shop_Building__WB_Rope__WB_Rope']={72.0,7.85,0.8,2.276,0.9,2.212,4,false,'WB_Rope','','WB_Loja'},
  ['WB_Shop_Building__WB_SignText__WB_SignText']={52.8,18.382,-9.521,3.686,1.414,18.702,4,true,'WB_SignText','','WB_Loja'},
  ['WB_Shop_Building__WB_Stone__WB_Stone']={67.0,23.75,-9.0,26.0,33.3,26.0,4,true,'WB_Stone','','WB_Loja'},
  ['WB_Shop_Building__WB_Stone_Dark__WB_Stone_Dark']={65.725,23.45,-9.0,29.45,34.9,26.9,4,true,'WB_Stone_Dark','','WB_Loja'},
  ['WB_Shop_Building__WB_Timber__WB_Timber']={66.7,23.331,-9.27,31.7,33.665,31.14,4,true,'WB_Timber','','WB_Loja'},
  ['WB_Shop_Glass__WB_Glass__WB_Glass']={66.19,14.425,-9.0,26.5,8.65,24.88,4,true,'WB_Glass','','WB_Loja'},
  ['PORTAL_DemonSlayer_Swirl__P_DS_Swirl']={-188.116,19.4,47.035,4.315,15.0,14.454,5,false,'P_DS_Swirl','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Emblem_Cream']={-188.544,21.044,46.633,14.061,25.028,22.911,5,false,'Emblem_Cream','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Glow']={-187.096,19.4,47.276,4.624,15.5,15.069,5,false,'P_DS_Glow','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Gravel']={-186.012,9.316,47.576,27.543,2.833,31.157,5,false,'P_DS_Gravel','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Iron']={-186.362,21.533,46.166,17.807,25.865,23.426,5,true,'P_DS_Iron','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Lacquer']={-189.774,21.49,46.166,10.981,25.78,23.266,5,true,'P_DS_Lacquer','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Red']={-185.739,19.368,46.122,16.083,19.463,21.556,5,true,'P_DS_Red','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Stone_DS_Rock']={-186.301,10.175,47.496,28.517,4.65,32.591,5,true,'Stone_DS_Rock','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__Bark_Dark']={-187.583,16.814,59.761,3.536,18.217,3.263,5,false,'Bark_Dark','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicMid']={-188.863,24.64,59.186,11.617,6.72,5.553,5,true,'P_DS_GlicMid','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicTip']={-188.19,21.688,59.962,9.863,4.771,3.679,5,false,'P_DS_GlicTip','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_Glicinia']={-188.303,25.157,59.189,10.662,5.986,6.104,5,true,'P_DS_Glicinia','','PORTAL_DemonSlayer'},
  ['PORTAL_DragonBall_Frame__P_DB_Amber']={-169.741,19.042,103.295,24.065,20.277,16.67,5,true,'P_DB_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Ball_Amber']={-172.548,22.915,96.834,6.593,24.77,18.142,5,true,'P_DB_Ball_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Blue']={-170.423,11.402,99.979,24.039,8.905,24.674,5,true,'P_DB_Blue','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Floor']={-171.102,8.94,101.098,28.788,0.32,28.588,5,true,'P_DB_Floor','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Gold_Bright']={-172.548,19.41,99.398,16.907,22.221,22.628,5,true,'P_DB_Gold_Bright','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Rim_Glow']={-172.204,19.4,102.258,11.695,15.566,11.151,5,false,'P_DB_Rim_Glow','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Star_Red']={-173.039,21.826,97.763,9.488,23.722,20.124,5,true,'P_DB_Star_Red','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_White']={-171.102,20.817,101.098,28.587,27.734,28.387,5,true,'P_DB_White','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Swirl__P_DB_Swirl']={-172.548,19.4,102.621,10.881,15.0,10.325,5,false,'P_DB_Swirl','','PORTAL_DragonBall'},
  ['PORTAL_Naruto_Bandana__Leaf_Pine']={-146.353,8.814,120.077,27.984,2.572,11.211,5,false,'Leaf_Pine','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Metal_Dark']={-145.363,23.057,116.857,27.653,26.687,8.976,5,true,'Metal_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Cloth']={-145.883,23.517,116.512,27.331,21.005,9.493,5,true,'P_Naruto_Cloth','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Lacquer']={-146.283,22.08,113.587,25.437,26.84,15.121,5,true,'P_Naruto_Lacquer','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Paper']={-154.747,10.2,110.207,5.385,3.2,5.883,5,false,'P_Naruto_Paper','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Rim_Glow']={-145.914,19.4,115.745,15.24,15.5,3.843,5,false,'P_Naruto_Rim_Glow','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Steel']={-141.359,20.654,113.606,17.668,26.793,5.419,5,true,'P_Naruto_Steel','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Stone']={-146.283,19.475,117.405,18.99,22.15,7.414,5,true,'P_Naruto_Stone','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Dark']={-145.774,17.45,115.11,31.404,19.5,27.756,5,true,'Stone_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Light']={-145.774,8.641,115.111,31.213,0.761,27.565,5,true,'Stone_Light','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Swirl__P_Naruto_Swirl']={-146.121,19.4,116.905,14.644,15.0,3.712,5,false,'P_Naruto_Swirl','','PORTAL_Naruto'},
  ['PORTAL_OnePiece_Pier__Emblem_Cream']={-171.048,25.174,16.991,7.703,22.253,14.932,5,false,'Emblem_Cream','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Leaf_Palm']={-184.433,19.24,21.937,8.245,1.955,7.973,5,false,'Leaf_Palm','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Metal_Dark']={-171.372,21.444,22.618,29.952,26.208,29.571,5,true,'Metal_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Glow']={-171.998,19.4,21.96,11.587,15.5,11.031,5,false,'P_OP_Glow','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Red']={-168.234,15.2,10.53,2.299,2.7,2.218,5,false,'P_OP_Red','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Rope']={-171.378,19.578,22.612,33.081,22.056,32.958,5,false,'Rope','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Dark']={-171.377,19.2,22.635,32.953,24.0,32.846,5,true,'Wood_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Light']={-172.548,20.779,21.379,19.38,23.444,18.456,5,true,'Wood_Light','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Plank']={-171.235,13.844,22.825,31.322,11.912,31.194,5,true,'Wood_Plank','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Swirl__P_OP_Swirl']={-172.548,19.4,21.379,10.881,15.0,10.325,5,false,'P_OP_Swirl','','PORTAL_OnePiece'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_ConcreteDark']={-146.326,19.669,6.546,19.346,19.281,7.328,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Glow']={-146.294,31.02,6.546,19.524,0.46,7.67,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Yellow']={-146.269,9.35,6.518,21.57,0.8,8.47,5,false,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Swirl__P_OPM_Swirl']={-146.121,19.4,7.095,14.644,15.0,3.712,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_SwirlBack__P_OPM_Swirl']={-146.618,19.4,5.082,14.644,15.0,3.247,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteDark']={-145.774,21.225,8.89,31.675,26.85,27.723,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteLight']={-145.774,19.975,8.889,31.413,24.15,26.246,5,true,'P_OPM_ConcreteLight','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteMid']={-144.307,19.975,6.255,19.109,22.95,16.32,5,true,'P_OPM_ConcreteMid','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Crater']={-146.483,19.539,6.5,18.579,18.618,7.017,5,true,'P_OPM_Crater','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_DarkGlassT']={-146.294,30.8,6.546,19.481,1.3,7.475,5,false,'P_OPM_DarkGlassT','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Glow']={-146.464,19.4,6.448,16.198,16.24,6.404,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_RebarSteel']={-145.182,18.7,5.234,17.746,18.916,13.32,5,true,'P_OPM_RebarSteel','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Red']={-145.72,31.676,9.201,3.404,3.872,1.854,5,false,'P_OPM_Red','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Yellow']={-145.774,21.125,8.89,31.751,26.45,27.799,5,true,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Core_Glow']={-183.994,23.695,76.016,10.355,21.506,25.157,5,false,'P_SG_Core_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Lilac_Glow']={-186.624,23.275,76.594,5.122,26.631,17.699,5,false,'P_SG_Lilac_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Moon_Glow']={-184.161,23.278,78.13,10.594,26.737,20.846,5,false,'P_SG_Moon_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Deadwood']={-187.951,12.508,64.096,2.206,8.559,2.436,5,false,'P_SG_Deadwood','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Marble']={-185.003,8.8,76.164,22.272,1.9,29.097,5,true,'P_SG_Marble','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Obsidian']={-188.156,23.38,77.046,10.894,29.46,25.797,5,true,'P_SG_Obsidian','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Rose']={-187.157,15.108,64.241,2.482,5.16,2.928,5,false,'P_SG_Rose','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Silver']={-185.003,23.85,76.164,22.487,30.58,29.311,5,true,'P_SG_Silver','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Violet']={-186.0,18.03,77.046,14.161,17.86,24.394,5,true,'P_SG_Violet','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_Shadow_Glow']={-187.385,19.4,76.806,4.624,15.5,15.069,5,false,'P_Shadow_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Swirl__P_Shadow_Swirl']={-188.116,19.4,76.965,4.315,15.0,14.454,5,false,'P_Shadow_Swirl','','PORTAL_ShadowGarden'},
  ['WB_Court_Decor__WB_Brass__WB_Brass']={-165.799,20.5,62.0,63.198,0.84,142.835,5,true,'WB_Brass','',''},
  ['WB_Court_Decor__WB_Cloth_Blue__WB_Cloth_Blue']={-172.675,15.9,2.429,2.471,6.8,1.599,5,false,'WB_Cloth_Blue','',''},
  ['WB_Court_Decor__WB_Cloth_Gold__WB_Cloth_Gold']={-145.651,15.9,62.0,105.461,6.8,142.147,5,true,'WB_Cloth_Gold','',''},
  ['WB_Court_Decor__WB_Cloth_Green__WB_Cloth_Green']={-197.832,15.9,30.857,1.435,6.8,2.558,5,false,'WB_Cloth_Green','',''},
  ['WB_Court_Decor__WB_Cloth_Purple__WB_Cloth_Purple']={-197.832,15.9,93.143,1.435,6.8,2.558,5,false,'WB_Cloth_Purple','',''},
  ['WB_Court_Decor__WB_Cloth_Red__WB_Cloth_Red']={-133.335,15.9,62.0,81.15,6.8,142.455,5,true,'WB_Cloth_Red','',''},
  ['WB_Court_Decor__WB_Iron__WB_Iron']={-143.397,15.803,62.0,101.886,16.606,106.634,5,true,'WB_Iron','',''},
  ['WB_Court_Decor__WB_LampGlow__WB_LampGlow']={-142.805,19.188,62.0,100.39,9.576,104.469,5,false,'WB_LampGlow','',''},
  ['WB_Court_Decor__WB_Plank__WB_Plank']={-94.576,16.45,59.581,5.651,11.1,26.038,5,false,'WB_Plank','',''},
  ['WB_Court_Decor__WB_SignText__WB_SignText']={-94.599,15.976,58.463,5.925,9.684,24.111,5,true,'WB_SignText','',''},
  ['WB_Court_Decor__WB_Stone__WB_Stone']={-93.0,12.95,62.0,2.2,10.1,19.2,5,false,'WB_Stone','',''},
  ['WB_Court_Decor__WB_Stone_Dark__WB_Stone_Dark']={-144.673,12.6,62.0,106.945,12.8,143.809,5,true,'WB_Stone_Dark','',''},
  ['WB_Court_Decor__WB_Timber__WB_Timber']={-145.144,14.45,62.0,107.287,13.9,142.555,5,true,'WB_Timber','',''},
  ['WB_Court_Garden__WB_FlowerPink__WB_FlowerPink']={-171.951,9.17,60.773,40.78,1.486,152.464,5,false,'WB_FlowerPink','',''},
  ['WB_Court_Garden__WB_FlowerRed__WB_FlowerRed']={-152.129,9.347,44.591,121.106,2.055,120.154,5,false,'WB_FlowerRed','',''},
  ['WB_Court_Garden__WB_FlowerWhite__WB_FlowerWhite']={-107.948,9.351,25.158,2.934,0.887,1.026,5,false,'WB_FlowerWhite','',''},
  ['WB_Court_Garden__WB_FlowerYellow__WB_FlowerYellow']={-155.506,9.231,58.412,112.438,1.667,138.989,5,false,'WB_FlowerYellow','',''},
  ['WB_Court_Garden__WB_Leaf__WB_Leaf']={-151.868,8.374,63.344,121.6,3.216,159.583,5,true,'WB_Leaf','',''},
  ['WB_Court_Garden__WB_Stone__WB_Stone']={-176.212,5.756,62.406,91.904,5.22,179.367,5,true,'WB_Stone','',''},
  ['WB_Court_Garden__WB_Stone_Dark__WB_Stone_Dark']={-151.838,6.9,62.0,126.676,0.5,162.394,5,true,'WB_Stone_Dark','',''},
  ['WB_Exit_Bridge__WB_Cobble__WB_Cobble']={0.0,6.2,185.0,24.0,1.6,74.0,6,true,'WB_Cobble','',''},
  ['WB_Exit_Bridge__WB_Iron__WB_Iron']={0.0,13.651,190.55,25.48,7.523,61.94,6,true,'WB_Iron','',''},
  ['WB_Exit_Bridge__WB_LampGlow__WB_LampGlow']={0.0,16.001,190.55,22.8,2.423,61.7,6,false,'WB_LampGlow','',''},
  ['WB_Exit_Bridge__WB_Stone__WB_Stone']={0.0,3.7,184.7,26.6,12.399,74.6,6,true,'WB_Stone','',''},
  ['WB_Exit_Bridge__WB_Stone_Dark__WB_Stone_Dark']={0.0,6.125,184.725,27.0,9.249,74.95,6,true,'WB_Stone_Dark','',''},
  ['WB_Exit_Gate__WB_Cloth_Blue__WB_Cloth_Blue']={12.5,24.7,147.0,2.6,7.2,0.16,6,false,'WB_Cloth_Blue','','WB_Portao'},
  ['WB_Exit_Gate__WB_Cloth_Gold__WB_Cloth_Gold']={0.0,34.747,144.63,26.286,20.506,5.06,6,true,'WB_Cloth_Gold','','WB_Portao'},
  ['WB_Exit_Gate__WB_Cloth_Red__WB_Cloth_Red']={-12.5,24.7,147.0,2.6,7.2,0.16,6,false,'WB_Cloth_Red','','WB_Portao'},
  ['WB_Exit_Gate__WB_Cobble__WB_Cobble']={0.0,6.65,145.0,16.0,0.7,6.0,6,false,'WB_Cobble','','WB_Portao'},
  ['WB_Exit_Gate__WB_Dark__WB_Dark']={0.0,21.5,141.65,34.041,11.0,8.583,6,true,'WB_Dark','','WB_Portao'},
  ['WB_Exit_Gate__WB_Dirt__WB_Dirt']={0.0,6.725,144.525,58.8,0.45,3.15,6,true,'WB_Dirt','','WB_Portao'},
  ['WB_Exit_Gate__WB_FlowerPink__WB_FlowerPink']={-4.614,8.775,144.341,49.207,0.784,1.9,6,false,'WB_FlowerPink','','WB_Portao'},
  ['WB_Exit_Gate__WB_FlowerRed__WB_FlowerRed']={4.83,8.863,144.562,48.028,1.105,1.59,6,false,'WB_FlowerRed','','WB_Portao'},
  ['WB_Exit_Gate__WB_FlowerYellow__WB_FlowerYellow']={-1.447,8.812,144.588,48.776,0.825,1.991,6,false,'WB_FlowerYellow','','WB_Portao'},
  ['WB_Exit_Gate__WB_Iron__WB_Iron']={0.0,27.22,142.0,28.24,36.64,13.74,6,true,'WB_Iron','','WB_Portao'},
  ['WB_Exit_Gate__WB_LampGlow__WB_LampGlow']={0.0,16.6,142.0,19.8,1.4,13.5,6,false,'WB_LampGlow','','WB_Portao'},
  ['WB_Exit_Gate__WB_Leaf__WB_Leaf']={-0.207,7.991,144.286,59.065,2.095,3.6,6,true,'WB_Leaf','','WB_Portao'},
  ['WB_Exit_Gate__WB_Plank__WB_Plank']={0.0,16.725,142.0,15.76,18.95,11.24,6,true,'WB_Plank','','WB_Portao'},
  ['WB_Exit_Gate__WB_Roof_Dark__WB_Roof_Dark']={0.0,37.95,142.0,37.0,10.3,12.0,6,true,'WB_Roof_Dark','','WB_Portao'},
  ['WB_Exit_Gate__WB_SignText__WB_SignText']={-0.026,25.036,142.0,12.549,1.594,11.46,6,true,'WB_SignText','','WB_Portao'},
  ['WB_Exit_Gate__WB_Stone__WB_Stone']={0.0,19.65,142.0,60.0,27.1,10.0,6,true,'WB_Stone','','WB_Portao'},
  ['WB_Exit_Gate__WB_Stone_Dark__WB_Stone_Dark']={0.0,19.25,142.0,62.4,27.3,11.1,6,true,'WB_Stone_Dark','','WB_Portao'},
  ['WB_Exit_Gate__WB_Timber__WB_Timber']={0.0,18.98,142.0,28.762,19.32,11.44,6,true,'WB_Timber','','WB_Portao'},
  ['WB_Veg_Trees__WB_Bark__WB_Bark_g16_15']={11.596,12.135,74.074,221.514,11.817,141.998,7,true,'WB_Bark','',''},
  ['WB_Veg_Trees__WB_Bark__WB_Bark_g16_16']={-48.071,14.1,-5.506,340.691,15.83,241.462,7,true,'WB_Bark','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g14_15']={-208.737,18.363,37.695,29.779,11.582,55.628,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g14_16']={-141.173,19.512,-58.047,28.159,11.184,33.614,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g15_15']={-56.568,21.033,67.736,104.238,14.426,105.414,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g15_16']={-73.164,19.765,-93.794,110.054,13.131,60.672,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g16_14']={40.724,20.357,137.18,17.027,12.633,16.312,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g16_15']={64.171,20.733,63.979,121.484,14.171,124.677,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Leaf__WB_Leaf_g16_16']={97.868,20.737,-57.628,59.225,14.081,116.011,7,true,'WB_Leaf','',''},
  ['WB_Veg_Trees__WB_Pine__WB_Pine_g14_16']={-158.598,24.127,-35.583,70.433,25.144,79.73,7,true,'WB_Pine','',''},
  ['WB_Veg_Trees__WB_Pine__WB_Pine_g15_14']={-60.766,22.939,137.076,85.639,23.129,25.206,7,true,'WB_Pine','',''},
  ['WB_Veg_Trees__WB_Pine__WB_Pine_g15_16']={-107.47,32.092,-40.712,221.295,40.597,182.071,7,true,'WB_Pine','',''},
  ['WB_Veg_Trees__WB_Pine__WB_Pine_g16_15']={75.692,24.749,69.591,101.705,26.884,143.726,7,true,'WB_Pine','',''},
  ['WB_Veg_Trees__WB_Pine__WB_Pine_g16_16']={22.741,32.279,-0.806,201.201,39.334,268.083,7,true,'WB_Pine','',''},
  ['WB_Veg_Tufts__WB_FlowerPink__WB_FlowerPink_g15_15']={4.735,8.556,50.378,141.352,2.254,172.439,7,false,'WB_FlowerPink','',''},
  ['WB_Veg_Tufts__WB_FlowerPink__WB_FlowerPink_g15_16']={-45.581,8.259,-40.464,47.595,1.487,41.107,7,false,'WB_FlowerPink','',''},
  ['WB_Veg_Tufts__WB_FlowerPink__WB_FlowerPink_g16_15']={33.777,8.213,64.171,67.444,1.657,93.977,7,false,'WB_FlowerPink','',''},
  ['WB_Veg_Tufts__WB_FlowerRed__WB_FlowerRed_g15_15']={4.445,8.579,37.724,139.736,2.251,190.881,7,false,'WB_FlowerRed','',''},
  ['WB_Veg_Tufts__WB_FlowerRed__WB_FlowerRed_g16_15']={26.459,8.65,76.151,33.742,2.508,81.41,7,false,'WB_FlowerRed','',''},
  ['WB_Veg_Tufts__WB_FlowerWhite__WB_FlowerWhite']={2.04,7.941,32.621,137.98,1.102,178.424,7,false,'WB_FlowerWhite','',''},
  ['WB_Veg_Tufts__WB_FlowerYellow__WB_FlowerYellow']={4.737,7.935,36.974,142.116,1.11,194.232,7,false,'WB_FlowerYellow','',''},
  ['WB_Veg_Tufts__WB_Leaf__WB_Leaf_g15_15']={-27.86,8.114,82.276,88.657,2.741,115.992,7,true,'WB_Leaf','',''},
  ['WB_Veg_Tufts__WB_Leaf__WB_Leaf_g15_16']={-43.153,7.754,-38.305,56.401,2.022,47.624,7,true,'WB_Leaf','',''},
  ['WB_Veg_Tufts__WB_Leaf__WB_Leaf_g16_15']={37.79,8.136,64.051,76.734,2.785,116.347,7,true,'WB_Leaf','',''},
  ['WB_Veg_Tufts__WB_Leaf__WB_Leaf_g16_16']={58.855,7.777,-21.78,33.35,2.068,35.691,7,true,'WB_Leaf','',''},
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
  {'COL_CourtRing_001','Block',{-131.525,6.7,118.696},{0.044,0.0,0.999},{0.999,0.0,-0.044},{34.5,7.056,3.0},false},
  {'COL_CourtRing_002','Block',{-136.475,6.7,118.696},{-0.044,0.0,0.999},{0.999,0.0,0.044},{34.5,7.056,3.0},false},
  {'COL_CourtRing_003','Block',{-141.407,6.7,118.264},{-0.131,0.0,0.991},{0.991,0.0,0.131},{34.5,7.056,3.0},false},
  {'COL_CourtRing_004','Block',{-146.283,6.7,117.405},{-0.216,0.0,0.976},{0.976,0.0,0.216},{34.5,7.056,3.0},false},
  {'COL_CourtRing_005','Block',{-151.065,6.7,116.123},{-0.301,0.0,0.954},{0.954,0.0,0.301},{34.5,7.056,3.0},false},
  {'COL_CourtRing_006','Block',{-155.717,6.7,114.43},{-0.383,0.0,0.924},{0.924,0.0,0.383},{34.5,7.056,3.0},false},
  {'COL_CourtRing_007','Block',{-160.204,6.7,112.338},{-0.462,0.0,0.887},{0.887,0.0,0.462},{34.5,7.056,3.0},false},
  {'COL_CourtRing_008','Block',{-164.492,6.7,109.862},{-0.537,0.0,0.843},{0.843,0.0,0.537},{34.5,7.056,3.0},false},
  {'COL_CourtRing_009','Block',{-168.547,6.7,107.023},{-0.609,0.0,0.793},{0.793,0.0,0.609},{34.5,7.056,3.0},false},
  {'COL_CourtRing_010','Block',{-172.34,6.7,103.84},{-0.676,0.0,0.737},{0.737,0.0,0.676},{34.5,7.056,3.0},false},
  {'COL_CourtRing_011','Block',{-175.84,6.7,100.34},{-0.737,0.0,0.676},{0.676,0.0,0.737},{34.5,7.056,3.0},false},
  {'COL_CourtRing_012','Block',{-179.023,6.7,96.547},{-0.793,0.0,0.609},{0.609,0.0,0.793},{34.5,7.056,3.0},false},
  {'COL_CourtRing_013','Block',{-181.862,6.7,92.492},{-0.843,0.0,0.537},{0.537,0.0,0.843},{34.5,7.056,3.0},false},
  {'COL_CourtRing_014','Block',{-184.338,6.7,88.204},{-0.887,0.0,0.462},{0.462,0.0,0.887},{34.5,7.056,3.0},false},
  {'COL_CourtRing_015','Block',{-186.43,6.7,83.717},{-0.924,0.0,0.383},{0.383,0.0,0.924},{34.5,7.056,3.0},false},
  {'COL_CourtRing_016','Block',{-188.123,6.7,79.065},{-0.954,0.0,0.301},{0.301,0.0,0.954},{34.5,7.056,3.0},false},
  {'COL_CourtRing_017','Block',{-189.405,6.7,74.283},{-0.976,0.0,0.216},{0.216,0.0,0.976},{34.5,7.056,3.0},false},
  {'COL_CourtRing_018','Block',{-190.264,6.7,69.407},{-0.991,0.0,0.131},{0.131,0.0,0.991},{34.5,7.056,3.0},false},
  {'COL_CourtRing_019','Block',{-190.696,6.7,64.475},{-0.999,0.0,0.044},{0.044,0.0,0.999},{34.5,7.056,3.0},false},
  {'COL_CourtRing_020','Block',{-190.696,6.7,59.525},{-0.999,0.0,-0.044},{-0.044,0.0,0.999},{34.5,7.056,3.0},false},
  {'COL_CourtRing_021','Block',{-190.264,6.7,54.593},{-0.991,0.0,-0.131},{-0.131,0.0,0.991},{34.5,7.056,3.0},false},
  {'COL_CourtRing_022','Block',{-189.405,6.7,49.717},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{34.5,7.056,3.0},false},
  {'COL_CourtRing_023','Block',{-188.123,6.7,44.935},{-0.954,0.0,-0.301},{-0.301,0.0,0.954},{34.5,7.056,3.0},false},
  {'COL_CourtRing_024','Block',{-186.43,6.7,40.283},{-0.924,0.0,-0.383},{-0.383,0.0,0.924},{34.5,7.056,3.0},false},
  {'COL_CourtRing_025','Block',{-184.338,6.7,35.796},{-0.887,0.0,-0.462},{-0.462,0.0,0.887},{34.5,7.056,3.0},false},
  {'COL_CourtRing_026','Block',{-181.862,6.7,31.508},{-0.843,0.0,-0.537},{-0.537,0.0,0.843},{34.5,7.056,3.0},false},
  {'COL_CourtRing_027','Block',{-179.023,6.7,27.453},{-0.793,0.0,-0.609},{-0.609,0.0,0.793},{34.5,7.056,3.0},false},
  {'COL_CourtRing_028','Block',{-175.84,6.7,23.66},{-0.737,0.0,-0.676},{-0.676,0.0,0.737},{34.5,7.056,3.0},false},
  {'COL_CourtRing_029','Block',{-172.34,6.7,20.16},{-0.676,0.0,-0.737},{-0.737,0.0,0.676},{34.5,7.056,3.0},false},
  {'COL_CourtRing_030','Block',{-168.547,6.7,16.977},{-0.609,0.0,-0.793},{-0.793,0.0,0.609},{34.5,7.056,3.0},false},
  {'COL_CourtRing_031','Block',{-164.492,6.7,14.138},{-0.537,0.0,-0.843},{-0.843,0.0,0.537},{34.5,7.056,3.0},false},
  {'COL_CourtRing_032','Block',{-160.204,6.7,11.662},{-0.462,0.0,-0.887},{-0.887,0.0,0.462},{34.5,7.056,3.0},false},
  {'COL_CourtRing_033','Block',{-155.717,6.7,9.57},{-0.383,0.0,-0.924},{-0.924,0.0,0.383},{34.5,7.056,3.0},false},
  {'COL_CourtRing_034','Block',{-151.065,6.7,7.877},{-0.301,0.0,-0.954},{-0.954,0.0,0.301},{34.5,7.056,3.0},false},
  {'COL_CourtRing_035','Block',{-146.283,6.7,6.595},{-0.216,0.0,-0.976},{-0.976,0.0,0.216},{34.5,7.056,3.0},false},
  {'COL_CourtRing_036','Block',{-141.407,6.7,5.736},{-0.131,0.0,-0.991},{-0.991,0.0,0.131},{34.5,7.056,3.0},false},
  {'COL_CourtRing_037','Block',{-136.475,6.7,5.304},{-0.044,0.0,-0.999},{-0.999,0.0,0.044},{34.5,7.056,3.0},false},
  {'COL_CourtRing_038','Block',{-131.525,6.7,5.304},{0.044,0.0,-0.999},{-0.999,0.0,-0.044},{34.5,7.056,3.0},false},
  {'COL_Court_001','Block',{-169.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,38.267,3.0},false},
  {'COL_Court_002','Block',{-159.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,61.609,3.0},false},
  {'COL_Court_003','Block',{-149.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,73.424,3.0},false},
  {'COL_Court_004','Block',{-134.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{20.0,78.683,3.0},false},
  {'COL_Court_006','Block',{-119.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,73.424,3.0},false},
  {'COL_Court_007','Block',{-109.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,61.609,3.0},false},
  {'COL_Court_008','Block',{-99.0,5.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,38.267,3.0},false},
  {'COL_Court_009','Block',{-93.0,12.6,53.5},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.0,3.0,12.8},false},
  {'COL_Court_010','Block',{-93.0,12.6,70.5},{-0.0,0.0,1.0},{1.0,0.0,0.0},{3.0,3.0,12.8},false},
  {'COL_Court_011','Block',{-93.0,20.5,62.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{20.8,1.8,3.0},false},
  {'COL_Court_012','Block',{-92.0,13.0,50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.6,1.6,12.0},false},
  {'COL_Court_013','Block',{-142.084,7.025,98.465},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{10.0,1.7,0.85},false},
  {'COL_Court_014','Block',{-142.495,7.225,100.32},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{10.0,2.1,1.25},false},
  {'COL_Court_015','Block',{-142.971,7.425,102.467},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{10.0,2.3,1.65},false},
  {'COL_Court_016','Block',{-159.71,7.025,89.093},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{10.0,1.7,0.85},false},
  {'COL_Court_017','Block',{-161.018,7.225,90.471},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{10.0,2.1,1.25},false},
  {'COL_Court_018','Block',{-162.532,7.425,92.067},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{10.0,2.3,1.65},false},
  {'COL_Court_019','Block',{-169.992,7.025,71.981},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{10.0,1.7,0.85},false},
  {'COL_Court_020','Block',{-171.822,7.225,72.489},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{10.0,2.1,1.25},false},
  {'COL_Court_021','Block',{-173.942,7.425,73.077},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{10.0,2.3,1.65},false},
  {'COL_Court_022','Block',{-169.992,7.025,52.019},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{10.0,1.7,0.85},false},
  {'COL_Court_023','Block',{-171.822,7.225,51.511},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{10.0,2.1,1.25},false},
  {'COL_Court_024','Block',{-173.942,7.425,50.923},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{10.0,2.3,1.65},false},
  {'COL_Court_025','Block',{-159.71,7.025,34.907},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{10.0,1.7,0.85},false},
  {'COL_Court_026','Block',{-161.018,7.225,33.529},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{10.0,2.1,1.25},false},
  {'COL_Court_027','Block',{-162.532,7.425,31.933},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{10.0,2.3,1.65},false},
  {'COL_Court_028','Block',{-142.084,7.025,25.535},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{10.0,1.7,0.85},false},
  {'COL_Court_029','Block',{-142.495,7.225,23.68},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{10.0,2.1,1.25},false},
  {'COL_Court_030','Block',{-142.971,7.425,21.533},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{10.0,2.3,1.65},false},
  {'COL_Court_031','Block',{-162.168,12.7,114.977},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_032','Block',{-185.43,12.7,92.902},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_033','Block',{-194.0,12.7,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_034','Block',{-185.43,12.7,31.098},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_035','Block',{-162.168,12.7,9.023},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_036','Block',{-99.742,11.5,77.253},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_037','Block',{-102.911,11.5,41.03},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Court_038','Block',{-134.62,14.2,132.997},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.0},false},
  {'COL_Court_039','Block',{-171.097,14.2,122.537},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.0},false},
  {'COL_Court_040','Block',{-196.978,14.2,94.784},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.0},false},
  {'COL_Court_041','Block',{-196.978,14.2,29.216},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.0},false},
  {'COL_Court_042','Block',{-171.097,14.2,1.463},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.0},false},
  {'COL_Court_043','Block',{-134.62,14.2,-8.997},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.0},false},
  {'COL_Court_044','Block',{-131.238,8.0,141.094},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_045','Block',{-144.956,8.0,140.865},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_046','Block',{-154.531,8.0,136.527},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_047','Block',{-167.794,8.0,133.365},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_048','Block',{-175.488,8.0,127.105},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_049','Block',{-183.485,8.0,121.163},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_050','Block',{-191.366,8.0,113.381},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_051','Block',{-200.918,8.0,105.642},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_052','Block',{-205.073,8.0,94.731},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_053','Block',{-210.102,8.0,86.312},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_054','Block',{-209.61,8.0,73.99},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_055','Block',{-211.588,8.0,64.404},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_056','Block',{-210.37,8.0,53.751},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_057','Block',{-208.14,8.0,43.639},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_058','Block',{-205.735,8.0,33.014},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_059','Block',{-199.629,8.0,21.371},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_060','Block',{-192.672,8.0,10.163},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_061','Block',{-184.052,8.0,2.993},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_062','Block',{-175.108,8.0,-4.416},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_063','Block',{-164.597,8.0,-9.92},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_064','Block',{-152.967,8.0,-14.631},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_065','Block',{-142.89,8.0,-14.026},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.0,3.0,2.4},false},
  {'COL_Court_066','Block',{-133.337,7.149,149.137},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.923,4.723,1.919},false},
  {'COL_Court_067','Block',{-158.72,7.257,146.061},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.571,5.493,2.514},false},
  {'COL_Court_068','Block',{-175.205,7.073,137.161},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.319,3.063,1.499},false},
  {'COL_Court_069','Block',{-201.012,7.199,118.648},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.273,4.5,2.193},false},
  {'COL_Court_070','Block',{-210.022,7.12,98.667},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.988,4.892,1.759},false},
  {'COL_Court_071','Block',{-215.911,7.186,84.658},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.949,5.835,2.125},false},
  {'COL_Court_072','Block',{-217.935,7.322,56.172},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.766,6.16,2.871},false},
  {'COL_Court_073','Block',{-215.128,7.209,31.39},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.851,5.062,2.247},false},
  {'COL_Court_074','Block',{-211.389,7.138,20.469},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.79,4.594,1.86},false},
  {'COL_Court_075','Block',{-190.824,7.246,-4.881},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.254,4.985,2.45},false},
  {'COL_Court_076','Block',{-178.316,7.253,-9.487},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.895,6.854,2.492},false},
  {'COL_Court_077','Block',{-148.559,7.23,-24.106},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.075,5.075,2.365},false},
  {'COL_Court_078','Block',{-124.665,7.9,17.026},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_079','Block',{-120.774,7.9,19.529},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_080','Block',{-113.778,7.9,21.161},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_081','Block',{-107.951,7.9,25.514},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_082','Block',{-101.886,7.9,29.259},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_083','Block',{-96.366,7.9,36.386},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_084','Block',{-92.799,7.9,79.643},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_085','Block',{-95.667,7.9,83.811},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_086','Block',{-100.292,7.9,91.042},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_087','Block',{-104.139,7.9,96.66},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_088','Block',{-112.006,7.9,100.068},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_089','Block',{-117.292,7.9,103.473},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Court_090','Block',{-124.242,7.9,104.526},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,2.2},false},
  {'COL_Exit_001','Block',{12.5,19.5,142.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.4,9.4,28.0},true},
  {'COL_Exit_002','Block',{-12.5,19.5,142.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.4,9.4,28.0},true},
  {'COL_Exit_003','Block',{7.63,14.4,141.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.6,8.0,14.8},true},
  {'COL_Exit_004','Block',{-7.63,14.4,141.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.6,8.0,14.8},true},
  {'COL_Exit_005','Block',{21.25,8.4,142.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{18.5,2.1,4.6},false},
  {'COL_Exit_006','Block',{23.45,7.0,144.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.7,3.6,1.0},false},
  {'COL_Exit_007','Block',{-21.25,8.4,142.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{18.5,2.1,4.6},false},
  {'COL_Exit_008','Block',{-23.45,7.0,144.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.7,3.6,1.0},false},
  {'COL_Exit_009','Block',{0.0,6.5,145.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.0,6.0,1.0},false},
  {'COL_Exit_010','Block',{0.0,26.3,142.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.4,10.8,6.6},true},
  {'COL_Exit_011','Block',{7.2,18.0,137.45},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.1,8.0},true},
  {'COL_Exit_012','Block',{-7.2,18.0,137.45},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.1,8.0},true},
  {'COL_Exit_013','Block',{7.2,18.0,146.55},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.1,8.0},true},
  {'COL_Exit_014','Block',{-7.2,18.0,146.55},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.1,8.0},true},
  {'COL_Exit_015','Ramp',{8.4,7.449,177.679},{-0.0,-0.014,1.0},{1.0,0.0,0.0},{60.606,1.0,3.1},false},
  {'COL_Exit_016','Ramp',{10.39,7.012,209.99},{0.707,-0.01,0.707},{0.707,0.0,-0.707},{5.657,1.0,3.1},false},
  {'COL_Exit_017','Ramp',{12.4,6.924,216.479},{-0.0,-0.014,1.0},{1.0,0.0,0.0},{9.001,1.0,3.1},false},
  {'COL_Exit_018','Block',{12.4,7.612,221.1},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,4.6},false},
  {'COL_Exit_019','Ramp',{-8.4,7.449,177.679},{-0.0,-0.014,1.0},{1.0,0.0,0.0},{60.606,1.0,3.1},false},
  {'COL_Exit_020','Ramp',{-10.39,7.012,209.99},{-0.707,-0.01,0.707},{0.707,0.0,0.707},{5.657,1.0,3.1},false},
  {'COL_Exit_021','Ramp',{-12.4,6.924,216.479},{-0.0,-0.014,1.0},{1.0,0.0,0.0},{9.001,1.0,3.1},false},
  {'COL_Exit_022','Block',{-12.4,7.612,221.1},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,4.6},false},
  {'COL_Exit_023','Block',{-8.4,14.038,160.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.4,1.4,8.0},true},
  {'COL_Exit_024','Block',{8.4,13.714,184.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.4,1.4,8.0},true},
  {'COL_Exit_025','Block',{-8.4,13.389,208.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.4,1.4,8.0},true},
  {'COL_Exit_026','Block',{12.4,13.812,221.1},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.4,1.4,8.0},true},
  {'COL_Exit_027','Block',{-12.4,13.812,221.1},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.4,1.4,8.0},true},
  {'COL_Exit_028','Ramp',{-0.0,5.75,184.99},{-0.0,-0.014,1.0},{1.0,0.0,0.0},{74.007,16.0,1.5},false},
  {'COL_Exit_029','Ramp',{-0.0,5.345,214.99},{-0.0,-0.014,1.0},{1.0,0.0,0.0},{14.001,24.0,1.5},false},
  {'COL_Forge_001','Block',{0.0,5.5,-63.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{54.0,46.0,3.0},false},
  {'COL_Forge_007','Block',{20.0,15.75,-66.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{15.0,40.0,17.5},true},
  {'COL_Forge_008','Block',{-20.0,15.75,-66.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{15.0,40.0,17.5},true},
  {'COL_Forge_009','Block',{13.0,20.0,-47.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.0,3.0,26.0},true},
  {'COL_Forge_010','Block',{-13.0,20.0,-47.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.0,3.0,26.0},true},
  {'COL_Forge_011','Block',{13.0,20.0,-66.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.0,3.0,26.0},true},
  {'COL_Forge_012','Block',{-13.0,20.0,-66.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.0,3.0,26.0},true},
  {'COL_Forge_013','Block',{0.0,20.0,-84.3},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{28.0,3.4,26.0},true},
  {'COL_Forge_014','Block',{0.0,9.1,-82.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{28.0,5.5,4.2},false},
  {'COL_Forge_015','Block',{11.7,13.0,-77.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,15.0,12.0},true},
  {'COL_Forge_016','Block',{-11.7,13.0,-77.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,15.0,12.0},true},
  {'COL_Grass_001','Block',{-224.0,4.8,46.889},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,78.667,4.0},false},
  {'COL_Grass_002','Block',{-208.0,4.8,53.615},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,131.231,4.0},false},
  {'COL_Grass_003','Block',{-192.0,4.8,50.812},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,164.735,4.0},false},
  {'COL_Grass_004','Block',{-176.0,4.8,51.638},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,190.98,4.0},false},
  {'COL_Grass_005','Block',{-160.0,4.8,47.535},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,205.293,4.0},false},
  {'COL_Grass_006','Block',{-144.0,4.8,43.069},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,218.879,4.0},false},
  {'COL_Grass_007','Block',{-128.0,4.8,36.974},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,235.725,4.0},false},
  {'COL_Grass_008','Block',{-112.0,4.8,27.867},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,253.067,4.0},false},
  {'COL_Grass_009','Block',{-96.0,4.8,17.933},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,266.533,4.0},false},
  {'COL_Grass_010','Block',{-80.0,4.8,9.667},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,276.667,4.0},false},
  {'COL_Grass_011','Block',{-64.0,4.8,8.753},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,282.334,4.0},false},
  {'COL_Grass_012','Block',{-48.0,4.8,9.437},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,284.806,4.0},false},
  {'COL_Grass_013','Block',{-32.0,4.8,10.121},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,287.277,4.0},false},
  {'COL_Grass_014','Block',{-16.0,4.8,9.766},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,287.669,4.0},false},
  {'COL_Grass_015','Block',{0.0,4.8,9.261},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,287.764,4.0},false},
  {'COL_Grass_016','Block',{16.0,4.8,8.757},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,287.858,4.0},false},
  {'COL_Grass_017','Block',{32.0,4.8,8.252},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,287.953,4.0},false},
  {'COL_Grass_018','Block',{48.0,4.8,7.752},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,282.932,4.0},false},
  {'COL_Grass_019','Block',{64.0,4.8,7.255},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,272.795,4.0},false},
  {'COL_Grass_020','Block',{80.0,4.8,6.758},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,262.658,4.0},false},
  {'COL_Grass_021','Block',{96.0,4.8,1.75},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,243.5,4.0},false},
  {'COL_Grass_022','Block',{112.0,4.8,1.35},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,204.3,4.0},false},
  {'COL_Grass_023','Block',{127.0,4.8,-11.625},{1.0,0.0,0.0},{0.0,0.0,-1.0},{14.0,131.25,4.0},false},
  {'COL_House_001','Block',{58.0,17.5,-48.0},{-0.548,0.0,-0.836},{-0.836,0.0,0.548},{27.18,20.18,23.0},true},
  {'COL_House_002','Block',{-58.0,14.25,-58.0},{-0.447,0.0,0.894},{0.894,0.0,0.447},{22.1,17.1,16.5},true},
  {'COL_House_003','Block',{-46.0,14.25,62.0},{0.994,0.0,0.11},{0.11,0.0,-0.994},{22.1,17.1,16.5},true},
  {'COL_House_004','Block',{66.0,17.5,24.0},{0.359,0.0,-0.933},{-0.933,0.0,-0.359},{23.18,18.18,23.0},true},
  {'COL_House_005','Block',{-50.0,14.25,-82.0},{-0.083,0.0,0.997},{0.997,0.0,0.083},{20.1,16.1,16.5},true},
  {'COL_House_006','Block',{50.0,14.25,-80.0},{-0.083,0.0,-0.997},{-0.997,0.0,0.083},{22.1,16.1,16.5},true},
  {'COL_House_007','Block',{-80.0,14.25,28.0},{-0.936,0.0,0.351},{0.351,0.0,0.936},{22.1,17.1,16.5},true},
  {'COL_House_008','Block',{-72.0,17.5,70.0},{0.928,0.0,-0.371},{-0.371,0.0,-0.928},{23.18,18.18,23.0},true},
  {'COL_House_009','Block',{-22.0,14.25,70.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{22.1,17.1,16.5},true},
  {'COL_House_010','Block',{22.0,17.5,64.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{21.18,17.18,23.0},true},
  {'COL_House_011','Block',{-24.0,17.5,98.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{25.18,19.18,23.0},true},
  {'COL_House_012','Block',{22.0,14.25,92.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{22.1,17.1,16.5},true},
  {'COL_House_013','Block',{-21.0,14.25,126.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{20.1,16.1,16.5},true},
  {'COL_House_014','Block',{22.0,14.25,120.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{20.1,16.1,16.5},true},
  {'COL_Plaza_001','Block',{0.0,5.5,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{80.0,80.0,3.0},false},
  {'COL_Plaza_009','Block',{45.0,5.5,1.875},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,76.25,3.0},false},
  {'COL_Plaza_010','Block',{52.0,5.5,-2.333},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,52.667,3.0},false},
  {'COL_Plaza_011','Block',{-26.0,8.0,8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{14.7,14.7,2.6},false},
  {'COL_Plaza_012','Block',{-26.0,11.0,8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.6,4.6,8.0},false},
  {'COL_Portal_001','Block',{-145.774,7.9,115.11},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{27.2,22.4,1.4},false},
  {'COL_Portal_002','Block',{-146.283,8.41,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{10.746,10.746,2.42},false},
  {'COL_Portal_003','Block',{-146.283,8.41,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{13.984,5.776,2.42},false},
  {'COL_Portal_004','Block',{-146.283,8.41,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{5.776,13.984,2.42},false},
  {'COL_Portal_005','Block',{-146.283,8.925,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{9.191,9.191,3.45},false},
  {'COL_Portal_006','Block',{-146.283,8.925,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{11.96,4.94,3.45},false},
  {'COL_Portal_007','Block',{-146.283,8.925,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{4.94,11.96,3.45},false},
  {'COL_Portal_008','Block',{-146.283,9.425,117.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{11.2,5.2,4.45},false},
  {'COL_Portal_009','Block',{-142.786,11.719,118.18},{0.885,0.423,0.196},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_010','Block',{-139.853,14.067,118.83},{0.614,0.777,0.136},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_011','Block',{-138.221,17.494,119.192},{0.22,0.974,0.049},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_012','Block',{-138.221,21.306,119.192},{-0.22,0.974,-0.049},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_013','Block',{-149.78,11.719,116.63},{0.885,-0.423,0.196},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_014','Block',{-152.713,14.067,115.979},{0.614,-0.777,0.136},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_015','Block',{-154.345,17.494,115.617},{0.22,-0.974,0.049},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_016','Block',{-154.345,21.306,115.617},{-0.22,-0.974,-0.049},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_017','Block',{-134.763,22.55,119.959},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{2.8,2.8,27.9},false},
  {'COL_Portal_018','Block',{-157.803,22.55,114.851},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{2.8,2.8,27.9},false},
  {'COL_Portal_019','Block',{-133.276,12.182,112.507},{0.876,-0.0,-0.482},{-0.455,0.334,-0.826},{1.8,1.8,9.0},false},
  {'COL_Portal_020','Block',{-154.573,10.2,111.367},{-0.997,0.0,-0.078},{-0.078,0.0,0.997},{5.6,3.6,3.2},false},
  {'COL_Portal_021','Block',{-171.102,8.15,101.098},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{26.2,12.2,1.9},false},
  {'COL_Portal_022','Block',{-171.102,8.15,101.098},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{14.8,21.4,1.9},false},
  {'COL_Portal_023','Block',{-172.548,9.3,102.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{21.6,5.2,1.4},false},
  {'COL_Portal_024','Block',{-172.548,9.3,102.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{17.2,9.4,1.4},false},
  {'COL_Portal_025','Block',{-172.548,9.3,102.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{10.8,12.0,1.4},false},
  {'COL_Portal_026','Block',{-171.102,8.15,101.098},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{22.0,17.4,1.9},false},
  {'COL_Portal_027','Block',{-172.548,9.3,102.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{18.4,8.4,1.4},false},
  {'COL_Portal_028','Block',{-167.094,12.878,109.002},{0.572,-0.616,0.542},{-0.688,-0.0,0.725},{2.588,5.451,5.066},false},
  {'COL_Portal_029','Block',{-169.7,9.722,106.477},{0.318,-0.899,0.302},{-0.688,-0.0,0.725},{2.934,5.525,5.144},false},
  {'COL_Portal_030','Block',{-169.799,11.873,105.057},{0.318,-0.899,0.302},{-0.688,-0.0,0.725},{1.85,2.25,4.068},false},
  {'COL_Portal_031','Block',{-179.205,12.878,97.509},{-0.572,-0.616,-0.542},{-0.688,-0.0,0.725},{2.588,5.451,5.066},false},
  {'COL_Portal_032','Block',{-176.548,9.722,99.979},{-0.318,-0.899,-0.302},{-0.688,-0.0,0.725},{2.934,5.525,5.144},false},
  {'COL_Portal_033','Block',{-175.125,11.873,100.003},{-0.318,-0.899,-0.302},{-0.688,0.0,0.725},{1.85,2.25,4.068},false},
  {'COL_Portal_034','Block',{-166.833,13.818,108.009},{0.682,-0.342,0.647},{-0.688,-0.0,0.725},{3.58,2.45,9.829},false},
  {'COL_Portal_035','Block',{-165.854,20.382,108.973},{0.718,0.139,0.682},{-0.688,-0.0,0.725},{3.55,2.3,6.133},false},
  {'COL_Portal_036','Block',{-178.228,13.818,97.196},{-0.682,-0.342,-0.647},{-0.688,0.0,0.725},{3.58,2.45,9.829},false},
  {'COL_Portal_037','Block',{-179.242,20.382,96.269},{-0.718,0.139,-0.682},{-0.688,-0.0,0.725},{3.55,2.3,6.133},false},
  {'COL_Portal_038','Block',{-159.618,10.2,102.07},{0.522,0.0,0.853},{0.853,0.0,-0.522},{4.9,2.0,2.2},false},
  {'COL_Portal_039','Block',{-172.018,10.815,90.441},{-0.522,0.0,-0.853},{-0.853,0.0,0.522},{6.0,2.0,3.53},false},
  {'COL_Portal_040','Block',{-172.496,10.825,102.567},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{13.6,2.35,2.05},false},
  {'COL_Portal_041','Block',{-174.097,12.15,104.253},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{16.0,2.7,4.7},false},
  {'COL_Portal_042','Block',{-173.897,19.4,104.043},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{7.2,2.52,7.2},false},
  {'COL_Portal_043','Block',{-169.63,16.483,107.542},{-0.919,-0.074,-0.386},{0.141,-0.979,-0.149},{5.253,4.687,1.6},false},
  {'COL_Portal_044','Block',{-169.877,20.667,107.645},{-0.921,0.032,-0.388},{-0.061,-0.996,0.065},{5.026,5.279,1.6},false},
  {'COL_Portal_045','Block',{-177.615,16.483,99.965},{-0.434,0.074,-0.898},{0.141,-0.979,-0.149},{5.253,4.687,1.6},false},
  {'COL_Portal_046','Block',{-177.705,20.667,100.217},{-0.435,-0.032,-0.9},{-0.061,-0.996,0.065},{5.026,5.279,1.6},false},
  {'COL_Portal_047','Block',{-185.024,7.925,76.15},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{27.2,14.3,1.45},false},
  {'COL_Portal_048','Block',{-184.976,7.925,76.137},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{23.36,17.4,1.45},false},
  {'COL_Portal_049','Block',{-184.783,8.2,76.083},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{17.2,9.4,2.0},false},
  {'COL_Portal_050','Block',{-184.205,8.2,75.923},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{14.32,10.6,2.0},false},
  {'COL_Portal_051','Block',{-185.458,8.475,76.271},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{14.0,6.0,2.55},false},
  {'COL_Portal_052','Block',{-184.976,8.475,76.137},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{11.6,7.0,2.55},false},
  {'COL_Portal_053','Block',{-185.265,14.95,87.632},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{3.8,4.3,13.5},false},
  {'COL_Portal_054','Block',{-191.144,14.95,66.432},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{3.8,4.3,13.5},false},
  {'COL_Portal_055','Block',{-186.454,10.775,83.344},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{5.1,2.0,4.25},false},
  {'COL_Portal_056','Block',{-185.946,17.3,85.175},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.3,2.0,8.8},false},
  {'COL_Portal_057','Block',{-189.955,10.775,70.72},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{5.1,2.0,4.25},false},
  {'COL_Portal_058','Block',{-190.462,17.3,68.889},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.3,2.0,8.8},false},
  {'COL_Portal_059','Block',{-189.168,19.4,77.299},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{10.7,2.1,10.7},false},
  {'COL_Portal_060','Block',{-189.168,19.4,77.299},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{13.9,2.1,5.74},false},
  {'COL_Portal_061','Block',{-189.168,19.4,77.299},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{5.74,2.1,13.9},false},
  {'COL_Portal_062','Block',{-180.27,8.65,87.492},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{2.1,2.1,1.9},false},
  {'COL_Portal_063','Block',{-180.27,11.625,87.492},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.0,1.0,4.05},false},
  {'COL_Portal_064','Block',{-188.151,9.775,63.942},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.6,1.6,4.15},false},
  {'COL_Portal_065','Block',{-186.845,12.8,64.721},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.8,1.7,1.9},false},
  {'COL_Portal_066','Block',{-178.568,7.925,49.64},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{6.0,5.7,1.45},false},
  {'COL_Portal_067','Block',{-181.892,8.2,48.718},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{5.2,1.2,2.0},false},
  {'COL_Portal_068','Block',{-182.904,8.7,48.438},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{4.6,1.1,3.0},false},
  {'COL_Portal_069','Block',{-180.707,10.775,54.547},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,1.1,5.15},false},
  {'COL_Portal_070','Block',{-177.874,10.775,44.333},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,1.1,5.15},false},
  {'COL_Portal_071','Block',{-188.327,13.7,60.321},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.7,1.7,11.0},false},
  {'COL_Portal_072','Block',{-188.686,9.2,46.834},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{10.0,8.3,4.0},false},
  {'COL_Portal_073','Block',{-190.781,9.0,53.829},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{4.6,8.0,3.6},false},
  {'COL_Portal_074','Block',{-191.701,9.35,56.583},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,7.7,4.3},false},
  {'COL_Portal_075','Block',{-192.056,9.8,57.678},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,7.0,5.2},false},
  {'COL_Portal_076','Block',{-192.219,8.975,58.826},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,10.1,3.55},false},
  {'COL_Portal_077','Block',{-190.181,14.9,55.033},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.2,1.9,3.0},false},
  {'COL_Portal_078','Block',{-190.475,20.05,56.093},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.8,1.9,7.3},false},
  {'COL_Portal_079','Block',{-193.46,12.8,54.694},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{3.5,2.1,4.0},false},
  {'COL_Portal_080','Block',{-186.88,9.0,39.76},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{4.6,8.0,3.6},false},
  {'COL_Portal_081','Block',{-186.249,9.35,36.925},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,7.7,4.3},false},
  {'COL_Portal_082','Block',{-185.99,9.8,35.803},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,7.0,5.2},false},
  {'COL_Portal_083','Block',{-185.538,8.975,34.735},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,10.1,3.55},false},
  {'COL_Portal_084','Block',{-185.745,14.9,39.037},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.2,1.9,3.0},false},
  {'COL_Portal_085','Block',{-185.451,20.05,37.977},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.8,1.9,7.3},false},
  {'COL_Portal_086','Block',{-188.73,12.8,37.638},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{3.5,2.1,4.0},false},
  {'COL_Portal_087','Block',{-184.157,8.95,48.09},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{23.8,1.7,3.5},false},
  {'COL_Portal_088','Block',{-193.408,8.975,45.525},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{23.8,2.1,3.55},false},
  {'COL_Portal_089','Block',{-190.228,19.2,46.407},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{15.2,3.9,16.0},false},
  {'COL_Portal_090','Block',{-171.102,8.0,22.902},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{22.8,21.4,1.6},false},
  {'COL_Portal_091','Block',{-179.734,9.6,31.094},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.4,21.4,2.8},false},
  {'COL_Portal_092','Block',{-162.47,9.6,14.711},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.4,21.4,2.8},false},
  {'COL_Portal_093','Block',{-172.548,8.55,21.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{12.16,12.16,2.5},false},
  {'COL_Portal_094','Block',{-172.548,8.55,21.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{15.824,6.536,2.5},false},
  {'COL_Portal_095','Block',{-172.548,8.55,21.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{6.536,15.824,2.5},false},
  {'COL_Portal_096','Block',{-172.548,8.95,21.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{9.332,9.332,3.3},false},
  {'COL_Portal_097','Block',{-172.548,8.95,21.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{12.144,5.016,3.3},false},
  {'COL_Portal_098','Block',{-172.548,8.95,21.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{5.016,12.144,3.3},false},
  {'COL_Portal_099','Block',{-173.301,14.0,33.95},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{5.0,1.4,10.5},false},
  {'COL_Portal_100','Block',{-168.714,19.7,10.02},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.4,1.4,23.0},false},
  {'COL_Portal_101','Block',{-159.556,10.3,22.285},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{3.6,2.8,3.0},false},
  {'COL_Portal_102','Block',{-182.284,10.1,20.417},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{2.4,2.4,2.6},false},
  {'COL_Portal_103','Block',{-162.295,10.1,18.818},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{2.4,2.4,2.6},false},
  {'COL_Portal_104','Block',{-184.75,12.2,22.757},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.6,1.6,8.0},false},
  {'COL_Portal_110','Block',{-173.959,18.8,19.892},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{15.2,0.4,16.4},false},
  {'COL_Portal_111','Block',{-145.774,7.95,8.89},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{27.6,22.4,1.5},false},
  {'COL_Portal_112','Block',{-145.45,8.925,10.354},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{11.6,5.8,1.45},false},
  {'COL_Portal_113','Block',{-145.731,9.4,9.085},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{10.0,3.2,2.4},false},
  {'COL_Portal_114','Block',{-154.91,20.275,8.456},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.65,4.2,24.15},false},
  {'COL_Portal_115','Block',{-137.678,20.275,4.636},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.65,4.2,24.15},false},
  {'COL_Portal_116','Block',{-146.294,28.775,6.546},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{14.0,3.2,7.15},false},
  {'COL_Portal_117','Block',{-146.359,9.9,6.253},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{7.2,2.6,3.4},false},
  {'COL_Portal_118','Block',{-151.533,10.5,7.401},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.4,2.6,4.6},false},
  {'COL_Portal_119','Block',{-141.184,10.5,5.106},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.4,2.6,4.6},false},
  {'COL_Portal_120','Block',{-146.543,18.4,5.424},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{12.0,0.9,13.6},false},
  {'COL_Portal_121','Ramp',{-144.128,9.298,2.918},{0.175,0.588,0.79},{0.976,-0.0,-0.216},{2.08,3.4,0.8},false},
  {'COL_Portal_122','Block',{-141.308,9.119,0.259},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.214,3.004,1.839},false},
  {'COL_Portal_123','Block',{-141.669,10.392,-0.153},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{1.212,1.948,0.768},false},
  {'COL_Portal_124','Block',{-145.443,8.912,-0.703},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{2.478,2.247,1.425},false},
  {'COL_Portal_125','Ramp',{-137.845,9.181,7.234},{-0.15,0.719,-0.678},{-0.976,-0.0,0.216},{1.56,2.2,0.8},false},
  {'COL_Portal_126','Block',{-135.696,8.916,8.979},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{1.515,1.426,1.433},false},
  {'COL_Portal_127','Block',{-136.265,9.824,8.774},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.559,0.477,0.698},false},
  {'COL_Portal_128','Block',{-137.97,8.715,10.8},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.898,0.966,1.03},false},
  {'COL_Portal_129','Block',{-153.024,9.675,17.769},{0.804,0.0,-0.595},{-0.595,0.0,-0.804},{4.4,1.2,2.95},false},
  {'COL_Portal_130','Block',{-152.686,9.425,13.29},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.8,0.8,2.45},false},
  {'COL_Portal_131','Block',{-154.063,9.279,12.161},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.68,0.68,2.158},false},
  {'COL_Rank_001','Block',{-50.5,7.0,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{19.0,62.0,1.2},false},
  {'COL_Rank_002','Block',{-40.25,6.9,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.5,62.0,1.0},false},
  {'COL_Rank_003','Block',{-60.65,25.562,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.7,62.0,37.923},true},
  {'COL_Rank_004','Block',{-64.95,19.1,-31.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.9,2.4,25.0},true},
  {'COL_Rank_005','Block',{-64.95,19.1,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.9,2.4,25.0},true},
  {'COL_Rank_006','Block',{-64.95,19.1,9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.9,2.4,25.0},true},
  {'COL_Rank_007','Block',{-56.8,20.65,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,55.0,26.1},true},
  {'COL_Rank_009','Block',{-42.0,23.7,-40.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.4,3.4,32.8},true},
  {'COL_Rank_010','Block',{-42.0,23.7,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.4,3.4,32.8},true},
  {'COL_Rank_011','Block',{-42.0,23.7,18.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.4,3.4,32.8},true},
  {'COL_Rank_012','Block',{-42.4,7.05,-44.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.2,3.2,1.1},false},
  {'COL_Rank_013','Block',{-42.4,9.2,-44.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.4,4.4,3.2},false},
  {'COL_Rank_014','Block',{-42.4,7.05,22.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.2,3.2,1.1},false},
  {'COL_Rank_015','Block',{-42.4,9.2,22.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.4,4.4,3.2},false},
  {'COL_Rank_016','Block',{-61.0,7.25,-43.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.6,2.8,1.5},false},
  {'COL_Rank_017','Block',{-61.0,7.25,21.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.6,2.8,1.5},false},
  {'COL_RoadS_001','Block',{0.0,5.5,91.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,102.0,3.0},false},
  {'COL_RoadW_001','Block',{-98.473,5.5,58.869},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,11.606,3.0},false},
  {'COL_RoadW_002','Block',{-88.473,5.5,55.443},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,16.06,3.0},false},
  {'COL_RoadW_003','Block',{-78.473,5.5,50.238},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,15.641,3.0},false},
  {'COL_RoadW_004','Block',{-68.473,5.5,45.256},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,15.596,3.0},false},
  {'COL_RoadW_005','Block',{-58.473,5.5,41.104},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,14.99,3.0},false},
  {'COL_RoadW_006','Block',{-48.473,5.5,37.258},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,14.995,3.0},false},
  {'COL_RoadW_007','Block',{-40.48,5.5,37.218},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.986,8.932,3.0},false},
  {'COL_Shop_001','Block',{65.8,8.4,-23.4},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{6.6,2.6,2.6},false},
  {'COL_Shop_002','Block',{78.4,8.4,-23.6},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{2.4,2.4,2.6},false},
  {'COL_Shop_003','Block',{54.6,13.95,-17.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,10.0,14.1},true},
  {'COL_Shop_004','Block',{54.6,13.95,-1.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,10.0,14.1},true},
  {'COL_Shop_005','Block',{54.6,18.7,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,6.0,4.6},true},
  {'COL_Shop_006','Block',{79.4,13.95,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,26.0,14.1},true},
  {'COL_Shop_007','Block',{67.0,13.95,-21.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{23.6,1.2,14.1},true},
  {'COL_Shop_008','Block',{67.0,13.95,3.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{23.6,1.2,14.1},true},
  {'COL_Shop_009','Block',{53.35,12.05,-15.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.3,6.6,10.3},true},
  {'COL_Shop_010','Block',{67.0,6.9,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{23.6,23.6,1.0},false},
  {'COL_Shop_011','Block',{54.6,6.9,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,6.0,1.0},false},
  {'COL_Shop_012','Block',{53.1,6.9,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,8.0,1.0},false},
  {'COL_Shop_013','Block',{51.6,6.8,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,8.8,0.8},false},
  {'COL_Shop_014','Block',{67.0,9.25,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.8,23.6,3.7},false},
  {'COL_Shop_015','Block',{72.85,9.25,-19.15},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.7,3.3,3.7},false},
  {'COL_Shop_016','Block',{78.0,12.4,-16.55},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.6,8.5,10.0},true},
  {'COL_Shop_017','Block',{78.0,12.4,-1.45},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.6,8.5,10.0},true},
  {'COL_Shop_018','Block',{58.6,11.6,-19.35},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.2,2.9,8.4},true},
  {'COL_Shop_019','Block',{63.2,11.6,-19.35},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.2,2.9,8.4},true},
  {'COL_Shop_020','Block',{60.75,11.1,1.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.9,3.4,7.4},true},
  {'COL_Shop_021','Block',{68.6,14.5,-0.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.2,7.4,0.4},true},
  {'COL_Shop_022','Block',{74.9,9.0,1.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.4,3.4,3.2},false},
  {'COL_Shop_023','Block',{72.0,7.8,1.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.2,0.8},false},
  {'COL_Shop_024','Block',{70.5,8.6,-3.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,1.8,2.4},false},
  {'COL_Shop_025','Block',{56.4,8.7,-19.55},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.5,2.6},false},
  {'COL_Town_001','Block',{34.0,8.7,24.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{9.0,6.0,3.4},false},
  {'COL_Town_002','Block',{44.0,8.7,4.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{9.0,6.0,3.4},false},
  {'COL_Town_003','Block',{36.0,8.7,-16.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{9.0,6.0,3.4},false},
  {'COL_Town_004','Block',{-30.0,9.5,-32.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{7.0,8.0,5.0},false},
  {'COL_Town_005','Block',{-38.0,8.3,-36.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_006','Block',{-36.5,8.3,-33.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_007','Block',{-37.5,8.1,-30.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.2},false},
  {'COL_Town_008','Block',{46.0,8.3,-30.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_009','Block',{48.5,8.3,-28.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_010','Block',{47.0,8.1,36.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.2},false},
  {'COL_Town_011','Block',{-30.0,8.3,38.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_012','Block',{-27.4,8.3,38.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_013','Block',{52.0,8.1,-6.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.2},false},
  {'COL_Town_014','Block',{52.0,8.3,-3.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.6},false},
  {'COL_Town_015','Block',{-9.5,11.5,38.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_016','Block',{9.5,11.5,38.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_017','Block',{-36.0,11.5,-8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_018','Block',{36.0,11.5,-34.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_019','Block',{-20.0,11.5,30.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_020','Block',{22.0,11.5,32.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_021','Block',{46.0,11.5,14.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_022','Block',{-36.0,11.5,26.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,1.4,9.0},false},
  {'COL_Town_023','Block',{-23.5,8.7,40.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{33.0,0.8,3.4},false},
  {'COL_Town_024','Block',{25.5,8.7,40.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{37.0,0.8,3.4},false},
  {'COL_Town_025','Block',{13.0,12.0,42.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,1.6,10.0},false},
  {'COL_Town_026','Block',{19.0,11.5,24.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,9.0},false},
  {'COL_Town_027','Block',{-9.0,8.4,96.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{6.8,6.8,3.4},false},
  {'COL_Veg_001','Block',{-30.0,11.028,50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.613},false},
  {'COL_Veg_002','Block',{56.0,11.595,48.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.767},false},
  {'COL_Veg_003','Block',{-13.0,11.536,50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.647},false},
  {'COL_Veg_004','Block',{12.0,11.367,108.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.304},false},
  {'COL_Veg_005','Block',{-14.0,11.083,113.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.725},false},
  {'COL_Veg_006','Block',{-56.0,11.706,96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.994},false},
  {'COL_Veg_007','Block',{-100.0,11.722,24.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,10.027},false},
  {'COL_Veg_008','Block',{86.0,11.403,-8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.377},false},
  {'COL_Veg_009','Block',{-61.646,14.298,-113.727},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,14.995},false},
  {'COL_Veg_010','Block',{-58.731,12.723,-116.348},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.846},false},
  {'COL_Veg_011','Block',{-37.893,12.699,-123.876},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.798},false},
  {'COL_Veg_012','Block',{-33.639,10.978,-115.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.511},false},
  {'COL_Veg_013','Block',{-25.73,11.069,-116.285},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.697},false},
  {'COL_Veg_014','Block',{-10.291,12.708,-120.634},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.815},false},
  {'COL_Veg_015','Block',{3.203,15.409,-124.293},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,17.219},false},
  {'COL_Veg_016','Block',{14.33,14.716,-124.483},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,15.833},false},
  {'COL_Veg_017','Block',{16.364,15.277,-125.262},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,16.954},false},
  {'COL_Veg_018','Block',{34.546,13.719,-120.894},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,13.838},false},
  {'COL_Veg_019','Block',{45.564,14.682,-114.507},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,15.765},false},
  {'COL_Veg_020','Block',{56.068,14.77,-116.573},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,15.939},false},
  {'COL_Veg_021','Block',{58.963,13.124,-116.583},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,12.648},false},
  {'COL_Veg_022','Block',{67.038,14.332,-117.57},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,15.064},false},
  {'COL_Veg_023','Block',{76.61,11.419,-105.75},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.409},false},
  {'COL_Veg_024','Block',{90.38,11.615,-106.605},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.808},false},
  {'COL_Veg_025','Block',{100.067,15.161,-100.565},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,16.722},false},
  {'COL_Veg_026','Block',{102.072,10.755,-85.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.057},false},
  {'COL_Veg_027','Block',{110.025,15.027,-85.163},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,16.455},false},
  {'COL_Veg_028','Block',{111.052,13.095,-73.566},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,12.59},false},
  {'COL_Veg_029','Block',{113.665,11.386,-64.827},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.341},false},
  {'COL_Veg_030','Block',{115.266,12.257,-47.336},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.914},false},
  {'COL_Veg_031','Block',{115.809,11.532,-39.973},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.639},false},
  {'COL_Veg_032','Block',{119.449,10.913,-20.835},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.378},false},
  {'COL_Veg_033','Block',{117.296,12.171,-11.149},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.741},false},
  {'COL_Veg_034','Block',{113.795,12.503,4.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.407},false},
  {'COL_Veg_035','Block',{115.893,11.558,10.546},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.692},false},
  {'COL_Veg_036','Block',{113.866,11.694,15.81},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.787},false},
  {'COL_Veg_037','Block',{121.353,11.877,27.351},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.155},false},
  {'COL_Veg_038','Block',{116.236,11.168,38.29},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,8.736},false},
  {'COL_Veg_039','Block',{116.152,12.222,50.11},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.844},false},
  {'COL_Veg_040','Block',{113.493,11.728,66.648},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.856},false},
  {'COL_Veg_041','Block',{112.972,10.853,64.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.256},false},
  {'COL_Veg_042','Block',{105.085,11.419,79.949},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.238},false},
  {'COL_Veg_043','Block',{97.898,12.696,94.533},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.793},false},
  {'COL_Veg_044','Block',{99.174,11.624,96.357},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.828},false},
  {'COL_Veg_045','Block',{91.155,10.927,107.437},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,8.255},false},
  {'COL_Veg_046','Block',{82.072,12.786,119.179},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.973},false},
  {'COL_Veg_047','Block',{73.412,11.401,118.131},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.372},false},
  {'COL_Veg_048','Block',{63.086,11.685,122.166},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.771},false},
  {'COL_Veg_049','Block',{50.84,10.898,130.312},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,8.195},false},
  {'COL_Veg_050','Block',{40.918,11.362,137.208},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.292},false},
  {'COL_Veg_051','Block',{30.481,12.064,135.542},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.527},false},
  {'COL_Veg_052','Block',{-23.135,12.029,143.635},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.459},false},
  {'COL_Veg_053','Block',{-37.775,11.425,143.465},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.25},false},
  {'COL_Veg_054','Block',{-41.353,10.959,132.517},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,8.318},false},
  {'COL_Veg_055','Block',{-54.99,11.016,138.41},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,8.433},false},
  {'COL_Veg_056','Block',{-72.801,12.083,129.775},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.566},false},
  {'COL_Veg_057','Block',{-78.475,11.308,140.244},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.017},false},
  {'COL_Veg_058','Block',{-91.244,11.996,139.845},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.392},false},
  {'COL_Veg_059','Block',{-98.261,11.674,144.098},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.748},false},
  {'COL_Veg_060','Block',{-216.106,10.783,57.865},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.114},false},
  {'COL_Veg_061','Block',{-213.18,11.742,45.149},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.884},false},
  {'COL_Veg_062','Block',{-200.605,10.657,17.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,7.856},false},
  {'COL_Veg_063','Block',{-203.174,11.34,8.598},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.079},false},
  {'COL_Veg_064','Block',{-188.453,12.106,0.614},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.613},false},
  {'COL_Veg_065','Block',{-182.749,11.617,-8.403},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.634},false},
  {'COL_Veg_066','Block',{-183.118,12.455,-20.276},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.309},false},
  {'COL_Veg_067','Block',{-168.902,12.056,-24.053},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,10.513},false},
  {'COL_Veg_068','Block',{-172.75,12.502,-31.575},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.404},false},
  {'COL_Veg_069','Block',{-162.014,12.355,-41.551},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,11.111},false},
  {'COL_Veg_070','Block',{-147.924,11.001,-48.858},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.558},false},
  {'COL_Veg_071','Block',{-144.471,11.504,-54.455},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,9.408},false},
  {'COL_Veg_072','Block',{-134.903,11.123,-58.191},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,8.646},false},
  {'COL_Veg_073','Block',{-123.356,15.494,-66.591},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,17.389},false},
  {'COL_Veg_074','Block',{-120.794,10.971,-71.282},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,8.497},false},
  {'COL_Veg_075','Block',{-112.675,14.963,-72.413},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,16.327},false},
  {'COL_Veg_076','Block',{-99.879,14.283,-82.442},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,14.966},false},
  {'COL_Veg_077','Block',{-99.327,15.29,-89.671},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,16.981},false},
  {'COL_Veg_078','Block',{-87.313,13.296,-105.638},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,12.992},false},
  {'COL_Veg_079','Block',{-75.552,11.283,-116.354},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,9.132},false},
  {'COL_Well_001','Block',{0.0,5.5,96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,16.0,3.0},false},
  {'COL_YardE_001','Block',{33.5,5.5,-69.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{13.0,46.0,3.0},false},
  {'COL_YardW_001','Block',{-33.5,5.5,-69.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{13.0,46.0,3.0},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'DOOR_Shop',{54.0,7.4,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['largura']=6.0,['altura']=9.0,['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'ForgeChimney',{19.0,64.0,-64.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='AudioWorld: ambiente da chamine'}},
  {'IGNIS_Anvil',{-0.9,7.0,-55.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='bigorna do golem (colisao da sessao Ignis)'}},
  {'INTERACT_Ignis',{-0.9,13.79,-60.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['prompt_range']=18,['server_range']=22,['alvo']='belly (prompt do Main)'}},
  {'INTERACT_Shop',{72.0,10.6,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['prompt_range']=12}},
  {'ISLE_LINK_Area1',{0.0,6.0,222.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='fim da ponte = borda da praca de chegada da Area 1 (z 222, piso 6)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'LAYOUT_Ignis',{-0.9,10.5,-46.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['lobbylayout']='Ignis',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'LAYOUT_PortalIsland',{-104.0,10.5,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['lobbylayout']='PortalIsland',['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'LAYOUT_Shop',{62.0,10.9,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['lobbylayout']='Shop',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'LAYOUT_ShopFacing',{72.0,10.9,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['lobbylayout']='ShopFacing',['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'LAYOUT_Spawn',{0.0,10.3,32.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['lobbylayout']='Spawn',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'LETREIRO_Correio',{-15.0,15.0,36.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='CORREIO',['icone']='carta',['alcance']=170}},
  {'LETREIRO_Ignis',{-0.9,20.0,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='LetreiroIgnis'}},
  {'LETREIRO_Loja',{54.0,24.0,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='LOJA DE MOCHILAS',['icone']='mochila',['alcance']=170}},
  {'LETREIRO_Mundos',{-93.0,25.0,62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='CAMINHO DOS MUNDOS',['icone']='portal',['alcance']=170}},
  {'LETREIRO_Mural',{-50.0,43.6,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['texto']='CAMPEOES',['icone']='trofeu',['alcance']=170}},
  {'LOBBY_GATE_Ilha1',{0.0,7.0,142.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='portao da ponte da Ilha 1 (Vila da Folha)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'MAILBOX_Correio',{-15.0,7.4,36.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='workspace.MailBox',['prompt']='Enviar Feedback',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'NPC_Ignis',{-0.9,7.0,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['npc']='Ignis',['alvo']='workspace.NPCs.Ignis (Root)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0,['nota']='Root (-0,9; 7; -60,7) olhando +Z; bigorna a +5 em Z'}},
  {'NPC_Shop',{72.0,7.4,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['npc']='npc vendedor ',['prompt']='LojaPrompt (Comprar, 12/18)',['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0,['nota']='atras do balcao (tampo em x 67), chao livre x 70..74 z -12..-6'}},
  {'PADLOJA_Shop',{62.0,7.45,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='workspace.LojaMochilas.PadLoja (10x0,2x10, so marca)',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'PLAYER_INTERACT_Ignis',{-0.9,7.0,-46.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['note']='chao livre e plano na cota 7 de z -52,7 a -40',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'PLAYER_INTERACT_Shop',{62.0,7.4,-9.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0,['nota']='chao livre e plano x 60..64 z -12..-6'}},
  {'PORTAL_DemonSlayer',{-187.385,19.4,47.195},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{['destino']='DemonSlayer',['raio']=7.5,['touch']=true,['vm_portal']='DemonSlayer'}},
  {'PORTAL_DragonBall',{-172.135,19.4,102.186},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{['destino']='DragonBall',['raio']=7.5,['touch']=true,['vm_portal']='DragonBall'}},
  {'PORTAL_Naruto',{-145.991,19.4,116.087},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{['destino']='Naruto',['raio']=7.5,['touch']=true,['vm_portal']='Naruto'}},
  {'PORTAL_OnePiece',{-172.135,19.4,21.814},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{['destino']='OnePiece',['raio']=7.5,['touch']=true,['vm_portal']='OnePiece'}},
  {'PORTAL_OnePunchMan',{-145.991,19.4,7.913},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{['destino']='OnePunchMan',['raio']=7.5,['touch']=true,['vm_portal']='OnePunchMan'}},
  {'PORTAL_ShadowGarden',{-187.385,19.4,76.805},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{['destino']='ShadowGarden',['raio']=7.5,['touch']=true,['vm_portal']='ShadowGarden'}},
  {'SPAWNLOBBY_Part',{0.0,7.1,32.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='workspace[\'Mystical Spawn Point\'].SpawnLobby',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'SPAWN_Lobby',{0.0,7.0,32.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['kind']='spawn',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0,['note']='na praca, atras da cerca, olhando a forja'}},
  {'TOP100_Origin',{-58.0,7.6,-11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='LOBBY_FORJA.GlobalTop100 (OriginCF)',['nota']='quadros em z 0 e podios em z 9,5 do referencial local',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'VFX_Brazier_Fire_N',{-42.4,9.9,-44.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=2.0}},
  {'VFX_Brazier_Fire_S',{-42.4,9.9,22.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=8,['size']=2.0}},
  {'VFX_Chimney_Smoke_L',{19.0,65.2,-68.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_heavy',['rate']=8}},
  {'VFX_Chimney_Smoke_R',{-19.0,65.2,-68.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_heavy',['rate']=8}},
  {'VFX_Fountain_Splash',{-26.0,16.7,8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='water',['rate']=20}},
  {'VFX_Furnace_Fire',{0.0,9.2,-83.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=18,['size']=4.0}},
  {'VFX_Hearth_Ember_L',{19.0,9.8,-48.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=6}},
  {'VFX_Hearth_Ember_R',{-19.0,9.8,-48.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='ember',['rate']=6}},
  {'VFX_Hearth_Fire_L',{19.0,9.4,-48.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=14,['size']=3.0}},
  {'VFX_Hearth_Fire_R',{-19.0,9.4,-48.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['rate']=14,['size']=3.0}},
  {'VFX_Leaves_0_0',{-30.0,18.545,50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.5771151261197724}},
  {'VFX_Leaves_0_0.001',{56.0,20.119,48.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.458808432685513}},
  {'VFX_Leaves_0_0.002',{-13.0,19.955,50.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.366799899879931}},
  {'VFX_Leaves_0_0.003',{12.0,19.487,108.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.104888793056518}},
  {'VFX_Leaves_0_0.004',{-14.0,18.698,113.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.662904104461757}},
  {'VFX_Leaves_0_0.005',{-56.0,20.428,96.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.631624041776414}},
  {'VFX_Leaves_0_0.006',{-100.0,20.474,24.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.657195227281758}},
  {'VFX_Leaves_0_0.007',{86.0,19.587,-8.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.160926482591157}},
  {'VFX_Leaves_0_0.008',{-33.639,18.405,-115.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.498990356616798}},
  {'VFX_Leaves_0_0.009',{-25.73,18.659,-116.285},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.641254357923907}},
  {'VFX_Leaves_0_0.010',{76.61,19.631,-105.75},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.185391227008713}},
  {'VFX_Leaves_0_0.011',{90.38,20.175,-106.605},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.4899105984405345}},
  {'VFX_Leaves_0_0.012',{102.072,17.787,-85.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.152651511906476}},
  {'VFX_Leaves_0_0.013',{113.665,19.538,-64.827},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.133024186073482}},
  {'VFX_Leaves_0_0.014',{115.809,19.944,-39.973},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.360840706672625}},
  {'VFX_Leaves_0_0.015',{119.449,18.224,-20.835},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.397401822158513}},
  {'VFX_Leaves_0_0.016',{115.893,20.017,10.546},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.401419486349098}},
  {'VFX_Leaves_0_0.017',{112.972,18.059,64.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.304881995465778}},
  {'VFX_Leaves_0_0.018',{99.174,20.201,96.357},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.50474703541626}},
  {'VFX_Leaves_0_0.019',{73.412,19.58,118.131},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.156654686646046}},
  {'VFX_Leaves_0_0.020',{40.918,19.471,137.208},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=7.0959162819194415}},
  {'VFX_Leaves_0_0.021',{-216.106,17.865,57.865},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.196333059784298}},
  {'VFX_Leaves_0_0.022',{-200.605,17.513,17.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=5.999305259008285}},
  {'VFX_Leaves_0_0.023',{-147.924,18.47,-48.858},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.5354450860101805}},
  {'VFX_Leaves_0_0.024',{-120.794,18.387,-71.282},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.488763222761785}},
  {'VFX_Leaves_0_0.025',{-75.552,19.252,-116.354},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='leaves',['rate']=1,['radius']=6.973308424625506}},
  {'VFX_Smoke_House_FE',{54.626,36.506,-72.057},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_FW',{-55.431,38.535,-80.646},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_PAD',{-58.045,38.289,-67.302},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_S1E',{27.84,46.558,65.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_S1W',{-26.2,37.474,78.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_S2E',{26.2,37.252,100.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_S2W',{-30.84,49.408,99.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_S3E',{25.95,35.529,127.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_S3W',{-26.3,37.423,127.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_SE',{66.999,42.737,33.855},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_SHOP',{76.5,41.4,-2.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_SW',{-44.852,37.897,67.963},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_TAV',{63.153,48.918,-53.528},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_W1',{-89.246,38.35,26.982},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
  {'VFX_Smoke_House_W2',{-71.317,49.003,76.555},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke_thin',['rate']=2}},
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
  {'L_P_DemonSlayer_Lamp_1','POINT',{-179.506,11.44,53.583},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Lamp_2','POINT',{-177.341,11.44,45.778},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Pad','POINT',{-181.218,12.7,48.905},{255,129,129},12.6,0.71,false,false},
  {'L_P_DragonBall_Pad','POINT',{-167.729,12.7,97.543},{97,179,255},12.6,0.71,false,false},
  {'L_P_Naruto_Pad','POINT',{-144.606,12.7,109.839},{255,196,118},12.6,0.71,false,false},
  {'L_P_OnePiece_Pad','POINT',{-167.729,12.7,26.457},{137,196,255},12.6,0.71,false,false},
  {'L_P_OnePunchMan_Pad','POINT',{-144.606,12.7,14.162},{255,229,144},12.6,0.71,false,false},
  {'L_P_ShadowGarden_Candles','POINT',{-179.151,18.41,86.663},{203,137,255},9.5,0.49,false,false},
  {'L_P_ShadowGarden_Moon','POINT',{-184.96,31.02,75.821},{196,129,255},10.7,0.56,false,false},
  {'L_P_ShadowGarden_Pad','POINT',{-181.218,12.7,75.095},{206,137,255},12.6,0.71,false,false},
  {'L_Portal_DemonSlayer','POINT',{-185.072,19.4,47.836},{255,129,129},14.0,1.0,false,false},
  {'L_Portal_DragonBall','POINT',{-170.483,19.4,100.445},{97,179,255},14.0,1.0,false,false},
  {'L_Portal_Naruto','POINT',{-145.471,19.4,113.744},{255,196,118},14.0,1.0,false,false},
  {'L_Portal_OnePiece','POINT',{-170.483,19.4,23.555},{137,196,255},14.0,1.0,false,false},
  {'L_Portal_OnePunchMan','POINT',{-145.471,19.4,10.256},{255,229,144},14.0,1.0,false,false},
  {'L_Portal_ShadowGarden','POINT',{-185.072,19.4,76.164},{206,137,255},14.0,1.0,false,false},
  {'L_WB_Brazier_N','POINT',{-42.4,10.9,-44.0},{255,130,50},18.0,1.4,false,false},
  {'L_WB_Brazier_S','POINT',{-42.4,10.9,22.0},{255,130,50},18.0,1.4,false,false},
  {'L_WB_Furnace','POINT',{0.0,12.0,-82.0},{255,112,36},30.0,2.0,true,false},
  {'L_WB_Hearth_L','POINT',{19.0,10.8,-48.0},{255,128,46},26.0,2.4,true,false},
  {'L_WB_Hearth_R','POINT',{-19.0,10.8,-48.0},{255,128,46},26.0,2.4,true,false},
  {'L_WB_Lamp_Bridge_0','POINT',{-7.1,16.188,160.0},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Bridge_1','POINT',{7.1,15.864,184.0},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Bridge_2','POINT',{-7.1,15.539,208.0},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Bridge_3','POINT',{11.1,16.562,221.1},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Bridge_4','POINT',{-11.1,16.562,221.1},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_0','POINT',{-161.558,16.35,113.829},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_1','POINT',{-184.316,16.35,92.233},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_2','POINT',{-192.7,16.35,62.0},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_3','POINT',{-184.316,16.35,31.767},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_4','POINT',{-161.558,16.35,10.171},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_5','POINT',{-100.93,15.15,76.724},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_6','POINT',{-103.989,15.15,41.757},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_Gate_0','POINT',{-93.0,23.131,53.5},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Court_Gate_1','POINT',{-93.0,23.131,70.5},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Forge_L','POINT',{13.0,15.25,-44.9},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Forge_R','POINT',{-13.0,15.25,-44.9},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Gate_0','POINT',{9.6,16.65,148.45},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Gate_1','POINT',{-9.6,16.65,148.45},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Gate_2','POINT',{-9.6,16.65,135.55},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Gate_3','POINT',{9.6,16.65,135.55},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_0','POINT',{-9.191,15.15,37.537},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_1','POINT',{9.191,15.15,37.537},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_2','POINT',{-34.731,15.15,-7.718},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_3','POINT',{35.055,15.15,-33.107},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_4','POINT',{-19.279,15.15,28.918},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_5','POINT',{21.264,15.15,30.929},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_6','POINT',{44.756,15.15,13.621},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Plaza_7','POINT',{-34.946,15.15,25.239},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Rank_0','POINT',{-42.0,17.15,-37.3},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Rank_1','POINT',{-42.0,17.15,-13.7},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Rank_2','POINT',{-42.0,17.15,-8.3},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Rank_3','POINT',{-42.0,17.15,15.3},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Shop_Door','POINT',{52.55,16.75,-4.4},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Lamp_Shop_Wall','POINT',{72.6,15.65,1.35},{255,190,110},14.0,0.8,false,true},
  {'L_WB_Shop_Chandelier','POINT',{66.5,17.9,-9.0},{255,200,130},16.0,0.9,false,false},
  {'L_WB_Shop_Lamp_N','POINT',{67.3,15.85,-19.35},{255,200,130},16.0,0.9,false,false},
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
  {'SPAWN_Lobby',{0.0,7.0,32.0}},
  {'SAFE_Spawn',{0.0,7.0,32.0}},
  {'SAFE_Praca',{0.0,7.0,0.0}},
  {'SAFE_PracaNW',{-20.0,7.0,-30.0}},
  {'SAFE_Loja',{48.0,7.0,-9.0}},
  {'SAFE_Mural',{-30.0,7.0,-11.0}},
  {'SAFE_RuaOeste',{-66.0,7.0,44.0}},
  {'SAFE_PatioEntrada',{-104.0,7.0,62.0}},
  {'SAFE_Patio',{-134.0,7.0,62.0}},
  {'SAFE_RuaSul1',{0.0,7.0,80.0}},
  {'SAFE_RuaSul2',{0.0,7.0,120.0}},
  {'SAFE_Portao',{0.0,6.973,150.0}},
  {'SAFE_Ponte1',{0.0,6.5,185.0}},
  {'SAFE_Ponte2',{0.0,6.162,210.0}},
  {'SAFE_Forja',{0.0,7.0,-44.0}},
  {'SAFE_Portal1',{-144.173,8.6,107.886}},
  {'SAFE_Portal2',{-166.353,9.1,96.093}},
  {'SAFE_Portal3',{-179.291,9.2,74.56}},
  {'SAFE_Portal4',{-179.291,8.65,49.44}},
  {'SAFE_Portal5',{-166.353,8.8,27.907}},
  {'SAFE_Portal6',{-144.173,8.7,16.114}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(420,4,400); v.Position = Vector3.new(-49.0,-25.0,43.0) + ROOT_OFFSET
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
-- gerado por montar_lobby_wolfberg.lua (export_roblox.py) - nao editar a mao
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
  Lg.Brightness = 2.6
  Lg.ExposureCompensation = -0.1
  Lg.EnvironmentDiffuseScale = 0.55
  Lg.EnvironmentSpecularScale = 0.35
  Lg.ShadowSoftness = 0.3
  Lg.Ambient = Color3.fromRGB(110,102,94)
  Lg.OutdoorAmbient = Color3.fromRGB(156,150,140)
  Lg.ColorShift_Top = Color3.fromRGB(255,232,200)
  Lg.ColorShift_Bottom = Color3.fromRGB(40,30,20)
  Lg.ClockTime = 14.495
  Lg.GeographicLatitude = 59.443
  do local e = Lg:FindFirstChildOfClass('Atmosphere') or Instance.new('Atmosphere', Lg)
    e.Density = 0.3
    e.Offset = 0.15
    e.Color = Color3.fromRGB(214,206,190)
    e.Decay = Color3.fromRGB(128,148,190)
    e.Glare = 0.25
    e.Haze = 1.3
  end
  do local e = Lg:FindFirstChildOfClass('Sky') or Instance.new('Sky', Lg)
    e.SunAngularSize = 16
    e.MoonAngularSize = 11
    e.StarCount = 0
  end
  do local e = Lg:FindFirstChildOfClass('BloomEffect') or Instance.new('BloomEffect', Lg)
    e.Intensity = 0.3
    e.Size = 28
    e.Threshold = 1.4
  end
  do local e = Lg:FindFirstChildOfClass('SunRaysEffect') or Instance.new('SunRaysEffect', Lg)
    e.Intensity = 0.08
    e.Spread = 0.2
  end
  do local e = Lg:FindFirstChildOfClass('ColorCorrectionEffect') or Instance.new('ColorCorrectionEffect', Lg)
    e.Brightness = 0.02
    e.Contrast = 0.08
    e.Saturation = 0.12
    e.TintColor = Color3.fromRGB(255,246,232)
  end
  local d = Lg:GetSunDirection()
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (-0.49, 0.64, 0.59) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
-- ================= CONTRATO DO JOGO (lobby Wolfberg) =================
-- Santuario.Portal1..6: Model com Disco (gameplay, invisivel, sem colisao, CanTouch) e atributo AreaId; o Core.Main
-- liga o Touched (Santuario precisa ser filho DIRETO de LOBBY_FORJA). O AudioWorld reconhece Portal%d em Santuario.
local PORTAIS = {
  {1, 'Naruto', 1, Vector3.new(-145.709, 19.400, 114.818), Vector3.new(0.2164, 0, -0.9763)},
  {2, 'DragonBall', 2, Vector3.new(-171.240, 19.400, 101.243), Vector3.new(0.6884, 0, -0.7254)},
  {3, 'ShadowGarden', 3, Vector3.new(-186.132, 19.400, 76.458), Vector3.new(0.9636, 0, -0.2672)},
  {4, 'DemonSlayer', 4, Vector3.new(-186.132, 19.400, 47.542), Vector3.new(0.9636, 0, 0.2672)},
  {5, 'OnePiece', 5, Vector3.new(-171.240, 19.400, 22.757), Vector3.new(0.6884, 0, 0.7254)},
  {6, 'OnePunchMan', 6, Vector3.new(-145.709, 19.400, 9.182), Vector3.new(0.2164, 0, 0.9763)},
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
  r:SetAttribute('Wolfberg', EXPORT_ID); r.Parent = root end
-- GlobalTop100 (quadros Forca/Moedas): a GEOMETRIA e do Top100Builder/Controller; aqui so a ORIGEM nova (Mural dos
-- Campeoes, oeste da praca). Se o modelo ja existe dentro do LOBBY_FORJA, e levado inteiro para la (PivotTo).
local TOP100_CF = CFrame.lookAt(Vector3.new(-58.000, 7.600, -11.000), Vector3.new(-57.000, 7.600, -11.000)) * CFrame.Angles(0, math.pi, 0)
root:SetAttribute('Top100Origin', TOP100_CF + ROOT_OFFSET)
do local t = root:FindFirstChild('GlobalTop100')
  if t and t:IsA('Model') then t:PivotTo(TOP100_CF + ROOT_OFFSET); print('GlobalTop100 levado ao Mural dos Campeoes')
  else print('GlobalTop100 ausente: construa com Top100Builder.Build(root, {OriginCF = root:GetAttribute("Top100Origin")})') end end
-- POSICOES DO JOGO (POSICIONAR_JOGO = true move os objetos soltos; o Core.LobbyLayout e trocado a mao/MCP):
--   LobbyLayout.Spawn        = Vector3.new(0.0, 10.3, 32.0)
--   LobbyLayout.Shop         = Vector3.new(62.0, 10.9, -9.0)
--   LobbyLayout.ShopFacing   = Vector3.new(72.0, 10.9, -9.0)
--   LobbyLayout.Ignis        = Vector3.new(-0.9, 10.5, -46.0)
--   LobbyLayout.PortalIsland = Vector3.new(-104.0, 10.5, 62.0)
local POSICIONAR_JOGO = true
if POSICIONAR_JOGO then
  local function mv(inst, cf, what) if inst then pcall(function() if inst:IsA('Model') then inst:PivotTo(cf) else inst.CFrame = cf end end); print('posicionado', what) else print('NAO achei', what) end end
  local msp = workspace:FindFirstChild('Mystical Spawn Point'); mv(msp and msp:FindFirstChild('SpawnLobby'), CFrame.new(0.0, 7.1, 32.0) * CFrame.Angles(0, 0, 0) + ROOT_OFFSET, 'SpawnLobby')
  mv(workspace:FindFirstChild('MailBox'), CFrame.new(-15.0, 7.4, 36.0) * CFrame.Angles(0, -math.pi / 2, 0) + ROOT_OFFSET, 'MailBox')
  local lm = workspace:FindFirstChild('LojaMochilas'); mv(lm and lm:FindFirstChild('PadLoja'), CFrame.new(62.0, 7.5, -9.0) + ROOT_OFFSET, 'PadLoja')
  local npcs = workspace:FindFirstChild('NPCs'); local v = npcs and npcs:FindFirstChild('npc vendedor ')
  mv(v, CFrame.new(72.0, 10.4, -9.0) * CFrame.Angles(0, math.pi / 2, 0) + ROOT_OFFSET, 'npc vendedor ')
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
      host.Size = (kind == 'leaves') and Vector3.new(10, 6, 10) or ((kind == 'dust') and Vector3.new(20, 14, 24) or Vector3.new(2, 1, 2))
      host.CFrame = mk.CFrame
      local pe = Instance.new('ParticleEmitter'); KIND[kind](pe, mk:GetAttribute('size'))
      local rate = mk:GetAttribute('rate'); if rate then pe.Rate = rate end
      if kind == 'leaves' then local r = mk:GetAttribute('radius'); if r then host.Size = Vector3.new(r * 2, r, r * 2) end end
      pe.Parent = host; host.Parent = VF; n += 1
    end
  end
  print(string.format('VFX Wolfberg: %d emissores', n))
  -- tremor das luzes de fogo (fornalhas, forno, braseiros): LocalScript em StarterPlayerScripts
  local SP = game:GetService('StarterPlayer'):WaitForChild('StarterPlayerScripts')
  local old = SP:FindFirstChild('VFX_Wolfberg_Client'); if old then old:Destroy() end
  local ls = Instance.new('LocalScript'); ls.Name = 'VFX_Wolfberg_Client'
  ls.Source = [==[
local RS = game:GetService('RunService')
local root = workspace:WaitForChild('LOBBY_FORJA', 30); if not root then return end
local LT = root:WaitForChild('LIGHTS', 30); if not LT then return end
local fires = {}
for _, p in ipairs(LT:GetChildren()) do
  local n = p.Name
  if string.find(n, '^L_WB_Hearth_') or string.find(n, '^L_WB_Furnace') or string.find(n, '^L_WB_Brazier_') then
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
      local fr = Instance.new('Frame'); fr.Size = UDim2.fromScale(1, 1); fr.BackgroundColor3 = Color3.fromRGB(74, 48, 30)
      fr.BackgroundTransparency = 0.08; fr.BorderSizePixel = 0; fr.Parent = bg
      local uc = Instance.new('UICorner'); uc.CornerRadius = UDim.new(0, 10); uc.Parent = fr
      local st = Instance.new('UIStroke'); st.Color = Color3.fromRGB(236, 200, 120); st.Thickness = 2.5; st.Parent = fr
      local tl = Instance.new('TextLabel'); tl.Size = UDim2.new(1, -16, 1, -8); tl.Position = UDim2.new(0, 8, 0, 4)
      tl.BackgroundTransparency = 1; tl.Text = txt; tl.TextColor3 = Color3.fromRGB(246, 226, 176); tl.TextScaled = true
      tl.Font = Enum.Font.FredokaOne; tl.TextStrokeTransparency = 0.4; tl.TextStrokeColor3 = Color3.fromRGB(30, 18, 10)
      tl.Parent = fr
      bg.Parent = mk; n += 1
    end
  end
  print(string.format('Letreiros das estacoes: %d', n))
end


print(string.format('LOBBY_FORJA montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
