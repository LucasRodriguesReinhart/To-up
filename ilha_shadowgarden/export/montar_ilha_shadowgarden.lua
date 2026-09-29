-- montar_ilha_shadowgarden.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID ac1e1ae5
-- 1) Importe os FBX ILHA3_*_ac1e1a.fbx (3D Importer) para dentro de workspace.ILHA_SHADOWGARDEN. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script ILHA_SHADOWGARDEN_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = 'ac1e1ae5'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o ilha3 INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('ILHA_SHADOWGARDEN') or Instance.new('Model', workspace)
root.Name = 'ILHA_SHADOWGARDEN'
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
  ['wood'] = '',  -- textures/T_wood_v3.png (5.0 studs por repeticao)
}
-- material/variante -> c = cor calibrada no Studio, m = Enum.Material (hibrido), t = transparencia,
--   s = CastShadow da familia, x = textura de detalhe, w = espiral
local MAT = {
  ['Bark'] = {c = Color3.fromRGB(120,98,76), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Cliff_Rock_SG'] = {c = Color3.fromRGB(66,60,90), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_SGDunBasalt'] = {c = Color3.fromRGB(32,24,58), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_SG_B'] = {c = Color3.fromRGB(56,52,80), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_SG_C'] = {c = Color3.fromRGB(76,70,100), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_SG_Dark'] = {c = Color3.fromRGB(40,36,58), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_SG_Top'] = {c = Color3.fromRGB(100,96,126), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cloth_Canvas'] = {c = Color3.fromRGB(225,212,188), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_SGCraftBook'] = {c = Color3.fromRGB(96,58,56), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_SG_Navy'] = {c = Color3.fromRGB(32,38,78), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_SG_Purple'] = {c = Color3.fromRGB(66,22,112), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Dirt_SG'] = {c = Color3.fromRGB(64,58,60), m = Enum.Material.Ground, t = 0.0, s = false, x = 'dirt', w = nil},
  ['Energy_Core_DemonSlayer_Glow'] = {c = Color3.fromRGB(255,150,120), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Foam'] = {c = Color3.fromRGB(236,244,250), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Glass_SGCraftAmber'] = {c = Color3.fromRGB(150,116,80), m = Enum.Material.Glass, t = 0.3, s = false, x = nil, w = nil},
  ['Glass_SGCraftPale'] = {c = Color3.fromRGB(92,104,132), m = Enum.Material.Glass, t = 0.3, s = false, x = nil, w = nil},
  ['Glass_SGCraftSage'] = {c = Color3.fromRGB(104,128,118), m = Enum.Material.Glass, t = 0.3, s = false, x = nil, w = nil},
  ['Glass_SGHallMoon'] = {c = Color3.fromRGB(96,124,186), m = Enum.Material.Glass, t = 0.3, s = false, x = nil, w = nil},
  ['Glass_SGHallViolet'] = {c = Color3.fromRGB(112,56,196), m = Enum.Material.Glass, t = 0.3, s = false, x = nil, w = nil},
  ['Glass_SG_Rose'] = {c = Color3.fromRGB(96,70,150), m = Enum.Material.Glass, t = 0.3, s = false, x = nil, w = nil},
  ['Grass_SG'] = {c = Color3.fromRGB(46,70,64), m = Enum.Material.Grass, t = 0.0, s = false, x = 'grass', w = nil},
  ['Lantern_Glow'] = {c = Color3.fromRGB(255,146,56), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_GateDS_Wisteria'] = {c = Color3.fromRGB(176,132,232), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_SGPropBloom'] = {c = Color3.fromRGB(98,66,132), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_SGVegMoon'] = {c = Color3.fromRGB(66,96,104), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_SGVegShade'] = {c = Color3.fromRGB(16,24,30), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_SG_Pine'] = {c = Color3.fromRGB(30,50,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leather'] = {c = Color3.fromRGB(149,111,80), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Brass'] = {c = Color3.fromRGB(186,148,90), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_GateDS_Blade'] = {c = Color3.fromRGB(206,214,226), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold'] = {c = Color3.fromRGB(222,170,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_SG_BlackIron'] = {c = Color3.fromRGB(26,24,34), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_SG_Iron'] = {c = Color3.fromRGB(56,58,68), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_SG_Silver'] = {c = Color3.fromRGB(176,182,198), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Black'] = {c = Color3.fromRGB(75,63,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Glow'] = {c = Color3.fromRGB(185,12,22), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Plaster_Cream'] = {c = Color3.fromRGB(232,212,172), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'plaster', w = nil},
  ['Plaster_SGVil'] = {c = Color3.fromRGB(96,88,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'plaster', w = nil},
  ['Roof_Blue'] = {c = Color3.fromRGB(62,84,138), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_SG_Navy'] = {c = Color3.fromRGB(28,22,44), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_SG_Slate'] = {c = Color3.fromRGB(34,34,46), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['SG_Crystal_Glow'] = {c = Color3.fromRGB(146,84,246), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_DunVoid_Glow'] = {c = Color3.fromRGB(46,26,104), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_Moon_Glow'] = {c = Color3.fromRGB(170,200,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_Rune_Glow'] = {c = Color3.fromRGB(196,150,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_SumPortal_Glow'] = {c = Color3.fromRGB(78,58,206), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_SumStar_Glow'] = {c = Color3.fromRGB(228,208,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_VioletDeep_Glow'] = {c = Color3.fromRGB(110,50,210), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_Violet_Glow'] = {c = Color3.fromRGB(150,100,235), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['SG_WaterMist_Glow'] = {c = Color3.fromRGB(140,105,225), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Paving_SG'] = {c = Color3.fromRGB(94,92,114), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = 'stone', w = nil},
  ['Stone_SGCasInterior'] = {c = Color3.fromRGB(104,104,120), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SGCraftDark'] = {c = Color3.fromRGB(54,52,74), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SGDunCaveDeep'] = {c = Color3.fromRGB(40,24,74), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SGDunVault'] = {c = Color3.fromRGB(34,38,62), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SGHallNiche'] = {c = Color3.fromRGB(40,26,64), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SGHallVault'] = {c = Color3.fromRGB(22,26,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SGVilCobble'] = {c = Color3.fromRGB(72,76,92), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Block'] = {c = Color3.fromRGB(92,96,114), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Block_B'] = {c = Color3.fromRGB(84,88,104), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Castle'] = {c = Color3.fromRGB(78,82,102), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Castle_B'] = {c = Color3.fromRGB(70,74,94), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Floor'] = {c = Color3.fromRGB(66,68,84), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_MarbleBlack'] = {c = Color3.fromRGB(36,32,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Obsidian'] = {c = Color3.fromRGB(22,20,30), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Trim'] = {c = Color3.fromRGB(150,154,170), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SG_Violet'] = {c = Color3.fromRGB(78,62,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Dark'] = {c = Color3.fromRGB(128,120,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light'] = {c = Color3.fromRGB(178,170,156), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Water_Fall'] = {c = Color3.fromRGB(170,212,236), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Water_SG'] = {c = Color3.fromRGB(64,96,196), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Window_Warm'] = {c = Color3.fromRGB(214,140,74), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wood_Dark'] = {c = Color3.fromRGB(92,64,47), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Lacquer_Red'] = {c = Color3.fromRGB(168,42,32), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_SG_Dark'] = {c = Color3.fromRGB(58,44,40), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
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
local FBX = {[1]='ILHA3_02_TERRAIN_ac1e1a.fbx', [2]='ILHA3_03_MINING_HALL_ac1e1a.fbx', [3]='ILHA3_04_CASTLE_ac1e1a.fbx', [4]='ILHA3_05_VILLAGE_ac1e1a.fbx', [5]='ILHA3_06_SUMMON_ac1e1a.fbx', [6]='ILHA3_07_WATER_ac1e1a.fbx', [7]='ILHA3_08_NEXT_ISLAND_ac1e1a.fbx', [8]='ILHA3_08_PURCHASE_GATES_ac1e1a.fbx', [9]='ILHA3_09_PROPS_ac1e1a.fbx', [10]='ILHA3_10_VEGETATION_ac1e1a.fbx', [11]='ILHA3_12_VFX_HELPERS_ac1e1a.fbx', [12]='ILHA3_16_CRAFT_ac1e1a.fbx', [13]='ILHA3_17_DUNGEON_ac1e1a.fbx', [14]='ILHA3_18_ENTRY_ac1e1a.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['SG_Sky_Islets__Cliff_Rock_SG']={-1008.925,52.82,483.644,584.46,116.186,892.694,1,false,'Cliff_Rock_SG','k',''},
  ['SG_Sky_Islets__Cliff_Rock_SG_B']={-904.423,53.887,557.729,798.827,75.27,756.33,1,false,'Cliff_Rock_SG_B','k',''},
  ['SG_Sky_Islets__Cliff_Rock_SG_Dark']={-903.915,43.829,487.868,795.107,119.024,894.219,1,false,'Cliff_Rock_SG_Dark','k',''},
  ['SG_Sky_Islets__Foam']={-903.664,46.797,513.958,772.843,127.581,577.345,1,false,'Foam','k',''},
  ['SG_Sky_Islets__Grass_SG']={-904.385,69.9,487.309,801.953,81.0,900.833,1,false,'Grass_SG','k',''},
  ['SG_Sky_Islets__Leaf_SG_Pine']={-905.737,77.771,488.684,787.372,91.864,892.475,1,false,'Leaf_SG_Pine','k',''},
  ['SG_Sky_Islets__SG_Crystal_Glow']={-907.801,45.822,487.167,789.112,134.912,886.43,1,false,'SG_Crystal_Glow','k',''},
  ['SG_Sky_Islets__Water_SG']={-903.373,47.398,514.123,771.511,126.205,576.694,1,false,'Water_SG','k',''},
  ['SG_Sky_Islets__Wood_SG_Dark']={-905.395,72.815,489.0,783.435,84.935,888.783,1,false,'Wood_SG_Dark','k',''},
  ['SG_Ter_Cliff_E__Cliff_Rock_SG']={-690.602,-19.038,487.312,135.799,151.676,136.173,1,true,'Cliff_Rock_SG','',''},
  ['SG_Ter_Cliff_E__Cliff_Rock_SG_C']={-677.255,-19.956,500.713,112.156,111.843,99.244,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Cliff_E__Cliff_Rock_SG_Dark']={-696.607,-34.379,487.943,150.86,147.489,141.525,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_E__Cliff_Rock_SG_Top']={-667.195,37.473,480.177,92.037,41.054,121.903,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Cliff_E__Grass_SG']={-696.607,37.923,487.943,150.86,40.154,141.525,1,false,'Grass_SG','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_B']={-922.667,-2.327,488.042,227.872,186.254,205.098,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_C']={-928.613,-7.252,497.626,192.077,173.974,146.727,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_Dark_g8_11']={-898.075,-15.636,531.835,252.077,142.358,145.399,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_Dark_g8_12']={-904.32,-3.083,494.988,264.566,158.577,219.093,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_Dark_g9_11']={-886.293,-37.313,522.785,228.513,143.026,163.498,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_Dark_g9_12']={-885.878,-35.062,495.098,227.683,138.524,218.872,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_N__Cliff_Rock_SG_Top']={-966.969,58.637,488.042,139.269,66.726,205.098,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Cliff_N__Grass_SG']={-903.121,59.087,486.216,262.168,65.826,201.108,1,false,'Grass_SG','',''},
  ['SG_Ter_Cliff_NE__Cliff_Rock_SG']={-803.557,-5.201,450.335,188.349,177.437,147.297,1,true,'Cliff_Rock_SG','',''},
  ['SG_Ter_Cliff_NE__Cliff_Rock_SG_B']={-807.904,2.218,439.596,171.189,173.164,117.5,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Cliff_NE__Cliff_Rock_SG_Dark_g9_12']={-835.115,-17.618,470.19,237.885,181.647,187.008,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_NE__Cliff_Rock_SG_Dark_g10_12']={-741.832,-34.371,481.185,64.899,137.141,155.042,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_NE__Cliff_Rock_SG_Top']={-803.557,55.645,399.65,188.349,68.709,45.927,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Cliff_NE__Grass_SG']={-807.204,61.772,471.82,190.474,56.457,173.772,1,false,'Grass_SG','',''},
  ['SG_Ter_Cliff_NW__Cliff_Rock_SG_B']={-889.416,0.131,624.043,208.056,189.339,119.983,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Cliff_NW__Cliff_Rock_SG_C']={-911.037,8.31,625.834,173.275,144.307,91.466,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Cliff_NW__Cliff_Rock_SG_Dark_g8_11']={-896.224,-0.941,594.892,248.375,158.989,93.375,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_NW__Cliff_Rock_SG_Dark_g9_10']={-836.962,-5.014,621.37,129.851,125.636,125.329,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_NW__Cliff_Rock_SG_Dark_g9_11']={-886.293,-37.109,620.571,228.513,142.619,126.439,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_NW__Cliff_Rock_SG_Top']={-911.931,56.556,635.631,171.488,78.887,96.808,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Cliff_NW__Grass_SG']={-886.293,58.784,621.37,228.513,74.432,125.329,1,false,'Grass_SG','',''},
  ['SG_Ter_Cliff_S__Cliff_Rock_SG_B']={-675.449,-30.145,604.774,150.665,132.199,122.73,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Cliff_S__Cliff_Rock_SG_C']={-675.787,-31.379,596.069,119.864,119.441,104.102,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Cliff_S__Cliff_Rock_SG_Dark']={-686.076,-37.227,605.948,171.921,142.854,127.588,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_S__Cliff_Rock_SG_Top']={-644.773,27.134,604.774,89.313,19.639,122.73,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Cliff_S__Grass_SG']={-686.899,31.277,605.948,170.276,11.354,127.588,1,false,'Grass_SG','',''},
  ['SG_Ter_Cliff_W__Cliff_Rock_SG_B']={-762.943,-19.77,653.151,131.558,149.139,127.444,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Cliff_W__Cliff_Rock_SG_C']={-756.326,-24.146,649.139,140.551,135.131,124.133,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Cliff_W__Cliff_Rock_SG_Dark']={-756.199,-33.716,637.789,140.295,150.299,158.167,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Cliff_W__Cliff_Rock_SG_Top']={-757.386,40.747,691.487,142.671,30.505,50.772,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Cliff_W__Grass_SG']={-755.59,41.285,636.703,139.077,29.429,155.994,1,false,'Grass_SG','',''},
  ['SG_Ter_Crystals__SG_Crystal_Glow']={-813.559,-15.064,557.438,418.993,95.909,350.742,1,false,'SG_Crystal_Glow','',''},
  ['SG_Ter_Crystals__SG_VioletDeep_Glow']={-812.485,23.853,543.753,418.502,14.213,319.083,1,false,'SG_VioletDeep_Glow','',''},
  ['SG_Ter_Mounds__Cliff_Rock_SG_B']={-940.465,53.747,514.967,149.961,42.295,267.293,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Mounds__Cliff_Rock_SG_C']={-931.773,49.911,510.961,136.75,34.623,256.358,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Mounds__Cliff_Rock_SG_Top']={-939.422,56.047,514.967,152.047,39.695,267.293,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Mounds__Grass_SG']={-939.422,56.547,514.967,152.047,38.695,267.293,1,false,'Grass_SG','',''},
  ['SG_Ter_SummonIsle__Cliff_Rock_SG_C']={-767.255,-2.209,721.928,44.748,66.503,52.263,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_SummonIsle__Cliff_Rock_SG_Dark']={-767.319,-10.636,721.201,44.875,98.473,53.717,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_SummonIsle__Cliff_Rock_SG_Top']={-767.255,7.375,725.765,44.748,49.336,44.589,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_SummonIsle__Stone_Paving_SG']={-767.457,40.2,725.639,43.672,0.0,43.672,1,false,'Stone_Paving_SG','',''},
  ['SG_Ter_SummonIsle__Stone_SG_Block']={-767.472,35.8,725.593,43.989,5.44,43.923,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_SummonIsle__Stone_SG_Block_B']={-767.347,35.8,725.711,43.863,5.44,43.787,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_SummonIsle__Stone_SG_Trim']={-767.457,39.4,725.639,43.672,1.6,43.672,1,true,'Stone_SG_Trim','',''},
  ['SG_Ter_Terrace_Entry__Cliff_Rock_SG_Dark']={-637.978,28.1,627.245,72.295,16.2,58.044,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Terrace_Entry__Grass_SG']={-629.57,30.2,627.245,55.479,8.0,58.044,1,false,'Grass_SG','',''},
  ['SG_Ter_Terrace_Entry__Stone_Paving_SG']={-639.786,32.2,625.401,68.681,8.0,48.018,1,false,'Stone_Paving_SG','',''},
  ['SG_Ter_Terrace_Entry__Stone_SG_Block']={-638.193,30.725,627.203,66.416,10.09,45.325,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Terrace_Entry__Stone_SG_Block_B']={-643.123,30.725,623.486,62.148,10.09,45.121,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_Terrace_P1__Cliff_Rock_SG_Dark']={-716.887,34.6,572.651,154.074,3.2,245.372,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Terrace_P1__Stone_Paving_SG']={-716.887,36.2,572.651,154.074,0.0,245.372,1,false,'Stone_Paving_SG','',''},
  ['SG_Ter_Terrace_P2__Cliff_Rock_SG']={-777.681,37.44,549.701,167.905,9.279,285.696,1,true,'Cliff_Rock_SG','',''},
  ['SG_Ter_Terrace_P2__Cliff_Rock_SG_B']={-781.306,37.101,551.898,157.593,8.602,275.691,1,true,'Cliff_Rock_SG_B','',''},
  ['SG_Ter_Terrace_P2__Cliff_Rock_SG_Dark']={-778.406,38.6,550.394,161.02,11.2,274.352,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Terrace_P2__Cliff_Rock_SG_Top']={-777.681,39.1,549.701,167.905,7.559,285.696,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Terrace_P2__Grass_SG']={-778.537,41.636,549.629,166.193,5.129,279.937,1,false,'Grass_SG','',''},
  ['SG_Ter_Terrace_P3__Cliff_Rock_SG']={-887.479,40.242,469.009,241.384,14.885,155.576,1,true,'Cliff_Rock_SG','',''},
  ['SG_Ter_Terrace_P3__Cliff_Rock_SG_C']={-888.945,39.99,470.157,222.864,14.381,150.953,1,true,'Cliff_Rock_SG_C','',''},
  ['SG_Ter_Terrace_P3__Cliff_Rock_SG_Dark']={-883.59,42.6,510.724,241.404,19.2,229.591,1,true,'Cliff_Rock_SG_Dark','',''},
  ['SG_Ter_Terrace_P3__Cliff_Rock_SG_Top']={-887.479,45.558,469.009,241.384,5.854,155.576,1,true,'Cliff_Rock_SG_Top','',''},
  ['SG_Ter_Terrace_P3__Grass_SG']={-886.715,46.031,468.427,239.856,4.908,154.413,1,false,'Grass_SG','',''},
  ['SG_Ter_Terrace_P3__Stone_Paving_SG']={-883.59,52.2,510.724,241.404,0.0,229.591,1,false,'Stone_Paving_SG','',''},
  ['SG_Ter_Wall_P1__Stone_SG_Block']={-713.289,36.29,572.204,149.274,4.82,247.001,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P1__Stone_SG_Block_B']={-713.308,36.29,572.807,149.413,4.82,247.567,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_Wall_P1__Stone_SG_Trim']={-713.023,36.45,572.727,150.185,5.1,249.32,1,true,'Stone_SG_Trim','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Block_g9_10']={-814.091,41.45,659.654,91.4,10.5,58.189,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Block_g10_11']={-778.406,41.45,540.134,162.769,10.5,218.374,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Block_g10_12']={-732.423,41.49,478.143,71.592,10.42,132.396,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Block_B']={-778.493,41.45,550.403,163.083,10.5,275.077,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Trim_g9_10']={-809.69,40.45,653.508,102.597,13.1,71.979,1,true,'Stone_SG_Trim','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Trim_g10_11']={-778.406,41.59,558.079,163.492,10.82,254.659,1,true,'Stone_SG_Trim','',''},
  ['SG_Ter_Wall_P2__Stone_SG_Trim_g10_12']={-732.259,40.45,478.002,72.314,13.1,133.135,1,true,'Stone_SG_Trim','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Block_g8_11']={-954.068,49.69,544.591,102.686,10.02,69.462,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Block_g8_12']={-947.151,49.69,473.026,105.874,10.02,92.268,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Block_g9_12']={-830.482,49.45,507.432,135.943,10.5,225.374,1,true,'Stone_SG_Block','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Block_B_g8_11']={-953.727,49.69,545.053,101.935,10.02,69.003,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Block_B_g8_12']={-945.885,49.69,470.826,102.855,10.02,85.789,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Block_B_g9_12']={-830.45,49.49,505.62,135.958,10.42,219.953,1,true,'Stone_SG_Block_B','',''},
  ['SG_Ter_Wall_P3__Stone_SG_Trim']={-883.577,44.45,507.08,245.355,21.1,226.419,1,true,'Stone_SG_Trim','',''},
  ['SG_Hall_Altar__Cloth_SG_Purple']={-940.944,61.8,497.199,10.713,10.5,24.848,2,false,'Cloth_SG_Purple','','SG_Hall'},
  ['SG_Hall_Altar__Glass_SGHallMoon']={-941.749,67.4,496.857,7.81,8.0,17.956,2,false,'Glass_SGHallMoon','','SG_Hall'},
  ['SG_Hall_Altar__Glass_SGHallViolet']={-941.721,68.4,496.869,6.81,10.4,15.494,2,false,'Glass_SGHallViolet','','SG_Hall'},
  ['SG_Hall_Altar__Metal_SG_BlackIron']={-940.99,66.65,497.179,11.158,6.9,25.792,2,false,'Metal_SG_BlackIron','','SG_Hall'},
  ['SG_Hall_Altar__Metal_SG_Silver']={-940.483,66.715,497.394,13.528,16.97,30.89,2,false,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Altar__SG_Rune_Glow']={-940.755,67.043,497.279,10.068,8.738,23.587,2,false,'SG_Rune_Glow','','SG_Hall'},
  ['SG_Hall_Altar__SG_VioletDeep_Glow']={-940.506,69.225,497.385,17.42,11.75,35.619,2,false,'SG_VioletDeep_Glow','','SG_Hall'},
  ['SG_Hall_Altar__Stone_SGHallNiche']={-941.818,64.1,496.828,10.655,22.0,24.748,2,false,'Stone_SGHallNiche','','SG_Hall'},
  ['SG_Hall_Altar__Stone_SG_Castle_B']={-940.823,61.5,497.14,16.224,14.8,34.683,2,false,'Stone_SG_Castle_B','','SG_Hall'},
  ['SG_Hall_Altar__Stone_SG_Obsidian']={-940.529,64.1,497.375,17.343,23.8,35.674,2,true,'Stone_SG_Obsidian','','SG_Hall'},
  ['SG_Hall_Altar__Stone_SG_Trim']={-940.529,65.7,497.375,17.437,23.8,35.874,2,true,'Stone_SG_Trim','','SG_Hall'},
  ['SG_Hall_Altar__Stone_SG_Violet']={-941.128,70.75,497.121,13.364,12.1,28.464,2,false,'Stone_SG_Violet','','SG_Hall'},
  ['SG_Hall_Banners__Cloth_SG_Purple']={-901.407,65.75,513.98,66.969,8.6,86.776,2,true,'Cloth_SG_Purple','','SG_Hall'},
  ['SG_Hall_Banners__Metal_SG_BlackIron']={-901.407,70.2,513.98,68.508,0.28,90.509,2,true,'Metal_SG_BlackIron','','SG_Hall'},
  ['SG_Hall_Banners__Metal_SG_Silver']={-901.407,66.643,513.98,68.306,7.634,87.51,2,true,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Banners__SG_Rune_Glow']={-901.407,67.104,513.98,65.634,1.385,85.791,2,false,'SG_Rune_Glow','','SG_Hall'},
  ['SG_Hall_Banners__Stone_SG_Obsidian']={-901.407,68.17,513.98,66.987,3.2,86.784,2,true,'Stone_SG_Obsidian','','SG_Hall'},
  ['SG_Hall_Floor__Cloth_SG_Purple']={-899.981,52.02,514.585,79.715,0.44,36.853,2,true,'Cloth_SG_Purple','','SG_Hall'},
  ['SG_Hall_Floor__Metal_SG_Silver']={-902.328,52.022,513.589,102.149,0.445,101.09,2,true,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Floor__SG_Rune_Glow']={-901.403,52.19,515.142,8.95,0.08,6.587,2,false,'SG_Rune_Glow','','SG_Hall'},
  ['SG_Hall_Floor__Stone_SG_MarbleBlack']={-902.328,52.0,513.589,101.494,0.4,100.434,2,true,'Stone_SG_MarbleBlack','','SG_Hall'},
  ['SG_Hall_Floor__Stone_SG_Obsidian']={-901.407,52.0,513.98,113.825,0.4,111.705,2,true,'Stone_SG_Obsidian','','SG_Hall'},
  ['SG_Hall_Ironwork__Lantern_Glow']={-902.091,66.912,513.98,104.328,11.925,97.365,2,false,'Lantern_Glow','','SG_Hall'},
  ['SG_Hall_Ironwork__Metal_SG_BlackIron']={-902.091,69.514,513.98,105.81,18.429,98.807,2,true,'Metal_SG_BlackIron','','SG_Hall'},
  ['SG_Hall_Ironwork__Metal_SG_Silver']={-901.407,72.63,513.98,50.207,2.06,46.322,2,true,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Piers__Metal_SG_BlackIron']={-901.407,68.35,513.98,107.899,1.9,105.568,2,true,'Metal_SG_BlackIron','','SG_Hall'},
  ['SG_Hall_Piers__Metal_SG_Silver']={-901.407,69.698,513.98,108.161,0.795,105.83,2,true,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Piers__SG_VioletDeep_Glow']={-901.407,71.025,513.98,113.825,0.25,111.705,2,false,'SG_VioletDeep_Glow','','SG_Hall'},
  ['SG_Hall_Piers__Stone_SGHallNiche']={-901.407,61.35,513.98,111.949,16.5,107.287,2,true,'Stone_SGHallNiche','','SG_Hall'},
  ['SG_Hall_Piers__Stone_SG_Castle']={-902.512,66.575,513.98,111.615,26.95,111.705,2,true,'Stone_SG_Castle','','SG_Hall'},
  ['SG_Hall_Piers__Stone_SG_Castle_B']={-897.633,66.47,512.775,106.276,26.741,107.42,2,true,'Stone_SG_Castle_B','','SG_Hall'},
  ['SG_Hall_Piers__Stone_SG_Obsidian']={-901.407,61.9,513.98,113.825,19.4,111.705,2,true,'Stone_SG_Obsidian','','SG_Hall'},
  ['SG_Hall_Piers__Stone_SG_Trim']={-901.407,65.3,513.98,113.825,24.4,111.705,2,true,'Stone_SG_Trim','','SG_Hall'},
  ['SG_Hall_Throne__Cloth_SG_Purple']={-940.446,57.45,497.39,3.938,9.6,4.73,2,false,'Cloth_SG_Purple','','SG_Hall'},
  ['SG_Hall_Throne__Metal_SG_Silver']={-939.415,58.1,497.961,8.584,11.3,18.541,2,false,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Throne__Stone_SG_Obsidian']={-940.483,57.65,497.394,10.629,11.1,19.582,2,false,'Stone_SG_Obsidian','','SG_Hall'},
  ['SG_Hall_Vault__Metal_SG_Silver']={-901.407,76.946,513.98,101.024,6.509,104.307,2,true,'Metal_SG_Silver','','SG_Hall'},
  ['SG_Hall_Vault__SG_Rune_Glow']={-901.406,78.76,514.195,70.69,0.08,30.702,2,false,'SG_Rune_Glow','','SG_Hall'},
  ['SG_Hall_Vault__Stone_SGHallVault']={-901.407,76.325,513.98,113.825,8.25,111.705,2,true,'Stone_SGHallVault','','SG_Hall'},
  ['SG_Hall_Vault__Stone_SG_Obsidian']={-901.407,76.417,513.98,112.986,7.567,111.199,2,true,'Stone_SG_Obsidian','','SG_Hall'},
  ['SG_Hall_Windows__Glass_SGHallMoon']={-901.407,73.85,513.98,89.852,8.1,101.455,2,false,'Glass_SGHallMoon','','SG_Hall'},
  ['SG_Hall_Windows__Glass_SGHallViolet']={-901.407,76.3,513.98,85.802,1.6,99.736,2,false,'Glass_SGHallViolet','','SG_Hall'},
  ['SG_Hall_Windows__Metal_SG_BlackIron']={-901.407,71.9,513.98,89.657,0.2,100.995,2,true,'Metal_SG_BlackIron','','SG_Hall'},
  ['SG_Hall_Windows__Stone_SG_Trim']={-901.407,73.9,513.98,91.364,9.1,102.172,2,true,'Stone_SG_Trim','','SG_Hall'},
  ['SG_Cas_Alas__Bark']={-948.567,111.733,526.748,63.02,13.467,153.035,3,true,'Bark','','SG_Cas'},
  ['SG_Cas_Alas__Leaf_SG_Pine']={-948.451,114.471,526.862,65.337,16.371,155.318,3,false,'Leaf_SG_Pine','','SG_Cas'},
  ['SG_Cas_Alas__Metal_SG_Silver']={-914.277,100.675,526.725,144.181,91.85,181.22,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Alas__Roof_SG_Navy']={-913.994,103.796,526.725,144.227,80.407,180.8,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Alas__Stone_SG_Castle']={-914.466,82.6,526.725,142.962,62.8,180.38,3,true,'Stone_SG_Castle','','SG_Cas'},
  ['SG_Cas_Alas__Stone_SG_Obsidian']={-914.573,75.2,526.725,144.749,84.4,182.38,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Alas__Stone_SG_Violet']={-918.387,86.1,526.725,137.321,59.8,182.58,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Alas__Window_Warm']={-917.797,80.8,526.725,135.156,49.2,179.085,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Cas_Coroa__Metal_SG_Silver']={-960.32,134.375,488.975,36.146,156.45,36.146,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Coroa__Roof_SG_Navy']={-960.32,169.5,488.975,34.329,82.6,34.329,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Coroa__SG_VioletDeep_Glow']={-960.32,135.6,488.975,34.412,156.8,34.412,3,false,'SG_VioletDeep_Glow','','SG_Cas'},
  ['SG_Cas_Coroa__Stone_SG_Castle_B']={-960.32,120.4,488.975,34.975,137.2,34.975,3,true,'Stone_SG_Castle_B','','SG_Cas'},
  ['SG_Cas_Coroa__Stone_SG_Obsidian']={-960.32,121.0,488.975,36.016,138.4,36.016,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Coroa__Stone_SG_Violet']={-960.32,143.2,488.975,33.768,94.0,33.768,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Coroa__Window_Warm']={-964.833,81.7,488.475,22.041,11.0,30.061,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Cas_Emblema__Metal_SG_Silver']={-856.785,90.353,532.919,13.391,70.406,29.683,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Emblema__SG_Rune_Glow']={-856.192,110.2,533.171,5.825,14.06,13.083,3,false,'SG_Rune_Glow','','SG_Cas'},
  ['SG_Cas_Emblema__SG_VioletDeep_Glow']={-855.474,87.415,533.476,14.595,69.47,32.609,3,false,'SG_VioletDeep_Glow','','SG_Cas'},
  ['SG_Cas_Emblema__Stone_SG_Obsidian']={-856.023,90.127,533.205,16.48,75.853,33.937,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Emblema__Stone_SG_Violet']={-857.085,97.2,532.792,11.997,54.0,27.733,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Escadas__Stone_Paving_SG']={-782.804,48.2,504.571,65.016,8.0,122.686,3,false,'Stone_Paving_SG','','SG_Cas'},
  ['SG_Cas_Escadas__Stone_SG_Block']={-782.804,48.8,504.571,65.862,9.2,124.856,3,true,'Stone_SG_Block','','SG_Cas'},
  ['SG_Cas_Escadas__Stone_SG_Block_B']={-782.022,48.4,504.903,51.778,8.4,122.863,3,true,'Stone_SG_Block_B','','SG_Cas'},
  ['SG_Cas_Estandartes__Cloth_SG_Purple']={-837.433,81.25,535.777,69.592,28.2,104.104,3,true,'Cloth_SG_Purple','','SG_Cas'},
  ['SG_Cas_Estandartes__Metal_Gold']={-837.406,82.77,535.789,69.647,25.16,104.128,3,true,'Metal_Gold','','SG_Cas'},
  ['SG_Cas_Estandartes__Metal_SG_BlackIron']={-837.479,90.35,535.757,70.038,10.58,105.048,3,true,'Metal_SG_BlackIron','','SG_Cas'},
  ['SG_Cas_Estandartes__Metal_SG_Silver']={-837.479,86.743,535.757,70.243,18.035,105.392,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Estandartes__SG_Rune_Glow']={-837.19,84.203,535.857,68.655,12.271,101.897,3,false,'SG_Rune_Glow','','SG_Cas'},
  ['SG_Cas_Estandartes__Stone_SG_Obsidian']={-837.415,86.475,535.785,69.636,16.35,104.138,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Fachada__Metal_SG_Silver']={-855.75,99.975,533.359,24.471,90.45,47.782,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Fachada__Roof_SG_Navy']={-855.75,110.9,533.359,24.231,65.4,47.542,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Fachada__SG_Rune_Glow']={-856.859,74.5,532.888,1.667,3.949,3.688,3,false,'SG_Rune_Glow','','SG_Cas'},
  ['SG_Cas_Fachada__SG_VioletDeep_Glow']={-856.762,88.85,532.929,5.617,16.7,12.95,3,false,'SG_VioletDeep_Glow','','SG_Cas'},
  ['SG_Cas_Fachada__Stone_SG_Castle_B']={-855.75,87.0,533.359,23.591,70.4,46.902,3,true,'Stone_SG_Castle_B','','SG_Cas'},
  ['SG_Cas_Fachada__Stone_SG_Obsidian']={-855.75,87.7,533.359,24.791,71.8,48.102,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Fachada__Stone_SG_Violet']={-855.75,87.9,533.359,25.091,71.4,48.402,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Fachada__Window_Warm']={-853.01,99.8,534.522,17.764,3.2,41.425,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Cas_Muralha__Lantern_Glow']={-807.991,63.402,539.086,65.949,8.315,153.884,3,false,'Lantern_Glow','','SG_Cas'},
  ['SG_Cas_Muralha__Metal_Gold']={-807.991,63.631,539.086,66.421,9.779,154.356,3,true,'Metal_Gold','','SG_Cas'},
  ['SG_Cas_Muralha__Metal_SG_BlackIron']={-818.995,61.905,547.742,14.944,17.79,20.852,3,true,'Metal_SG_BlackIron','','SG_Cas'},
  ['SG_Cas_Muralha__Metal_SG_Silver']={-817.727,81.875,533.286,110.782,69.45,197.079,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Muralha__Roof_SG_Navy']={-818.043,92.7,533.286,109.909,41.8,196.839,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Muralha__Stone_SG_Block']={-832.168,49.7,531.435,139.112,33.4,195.771,3,true,'Stone_SG_Block','','SG_Cas'},
  ['SG_Cas_Muralha__Stone_SG_Block_B']={-839.182,49.7,538.595,127.386,33.4,173.271,3,true,'Stone_SG_Block_B','','SG_Cas'},
  ['SG_Cas_Muralha__Stone_SG_Castle']={-818.168,67.7,533.416,108.999,41.0,195.939,3,true,'Stone_SG_Castle','','SG_Cas'},
  ['SG_Cas_Muralha__Stone_SG_Obsidian_g9_11']={-832.692,62.5,533.566,141.816,59.0,197.639,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Muralha__Stone_SG_Obsidian_g9_12']={-789.634,59.3,489.217,50.222,31.4,111.532,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Muralha__Stone_SG_Violet']={-818.293,80.15,533.541,110.949,20.9,197.889,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Muralha__Window_Warm']={-816.749,72.2,533.82,105.655,24.0,187.762,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Cas_Nave__Glass_SGHallMoon']={-896.045,73.85,513.98,102.241,8.1,105.376,3,false,'Glass_SGHallMoon','','SG_Cas'},
  ['SG_Cas_Nave__Metal_SG_Silver']={-901.407,102.175,513.98,125.787,94.85,123.668,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Nave__Roof_SG_Navy']={-901.407,110.175,513.98,108.489,28.95,118.944,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Nave__SG_VioletDeep_Glow']={-901.407,106.3,513.98,72.339,7.4,64.106,3,false,'SG_VioletDeep_Glow','','SG_Cas'},
  ['SG_Cas_Nave__Stone_SGCasInterior']={-901.407,82.0,513.98,123.528,60.4,121.408,3,true,'Stone_SGCasInterior','','SG_Cas'},
  ['SG_Cas_Nave__Stone_SG_Castle']={-901.407,97.95,513.98,124.314,92.3,122.195,3,true,'Stone_SG_Castle','','SG_Cas'},
  ['SG_Cas_Nave__Stone_SG_Castle_B']={-898.733,83.5,514.761,111.601,63.4,120.632,3,true,'Stone_SG_Castle_B','','SG_Cas'},
  ['SG_Cas_Nave__Stone_SG_Obsidian']={-901.407,98.344,513.98,125.787,93.089,123.668,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Nave__Stone_SG_Trim']={-901.407,79.7,513.98,113.825,1.0,111.705,3,true,'Stone_SG_Trim','','SG_Cas'},
  ['SG_Cas_Nave__Stone_SG_Violet']={-901.407,92.3,513.98,124.432,45.0,122.471,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Nave__Window_Warm']={-901.407,95.35,513.98,122.021,12.5,115.939,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Cas_Telhados__Metal_SG_Silver']={-898.328,137.784,524.145,97.301,53.833,59.393,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Telhados__Roof_SG_Navy']={-901.407,125.517,513.98,123.519,75.166,123.878,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Telhados__SG_VioletDeep_Glow']={-906.93,165.6,511.636,0.593,2.2,0.593,3,false,'SG_VioletDeep_Glow','','SG_Cas'},
  ['SG_Cas_Telhados__Stone_SG_Castle']={-901.407,109.298,513.98,85.131,38.95,94.244,3,true,'Stone_SG_Castle','','SG_Cas'},
  ['SG_Cas_Telhados__Stone_SG_Obsidian']={-901.407,135.736,513.98,61.417,22.727,45.841,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Telhados__Stone_SG_Violet']={-901.407,126.351,513.98,62.179,3.956,46.39,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Telhados__Window_Warm']={-901.407,92.723,513.98,83.01,2.4,93.691,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Cas_Torres__Bark']={-904.718,105.85,518.634,118.708,28.7,126.294,3,true,'Bark','','SG_Cas'},
  ['SG_Cas_Torres__Leaf_SG_Pine']={-904.573,108.243,518.662,121.082,30.771,128.407,3,false,'Leaf_SG_Pine','','SG_Cas'},
  ['SG_Cas_Torres__Metal_SG_Silver']={-899.676,110.975,518.36,144.261,111.65,147.44,3,true,'Metal_SG_Silver','','SG_Cas'},
  ['SG_Cas_Torres__Roof_SG_Navy']={-900.041,140.3,517.995,143.291,44.6,146.47,3,true,'Roof_SG_Navy','','SG_Cas'},
  ['SG_Cas_Torres__SG_VioletDeep_Glow']={-898.596,97.59,518.225,144.257,89.82,145.005,3,false,'SG_VioletDeep_Glow','','SG_Cas'},
  ['SG_Cas_Torres__Stone_SG_Castle']={-899.576,89.6,518.46,143.221,68.8,146.4,3,true,'Stone_SG_Castle','','SG_Cas'},
  ['SG_Cas_Torres__Stone_SG_Obsidian']={-899.081,95.12,518.56,146.012,86.64,148.4,3,true,'Stone_SG_Obsidian','','SG_Cas'},
  ['SG_Cas_Torres__Stone_SG_Violet']={-899.576,108.325,518.46,145.421,36.55,148.6,3,true,'Stone_SG_Violet','','SG_Cas'},
  ['SG_Cas_Torres__Window_Warm']={-899.913,88.7,518.123,141.623,37.0,144.802,3,false,'Window_Warm','','SG_Cas'},
  ['SG_Vil_Fountain__Lantern_Glow']={-702.576,40.81,598.372,13.244,1.02,13.244,4,false,'Lantern_Glow','',''},
  ['SG_Vil_Fountain__Metal_Gold']={-702.576,41.083,598.372,13.596,1.914,13.596,4,false,'Metal_Gold','',''},
  ['SG_Vil_Fountain__Metal_SG_Silver']={-702.576,43.019,598.372,15.689,12.199,13.752,4,false,'Metal_SG_Silver','',''},
  ['SG_Vil_Fountain__SG_Rune_Glow']={-702.576,37.5,598.372,15.244,0.79,7.066,4,false,'SG_Rune_Glow','',''},
  ['SG_Vil_Fountain__Stone_SG_Castle']={-702.576,40.86,598.372,13.896,8.68,13.896,4,false,'Stone_SG_Castle','',''},
  ['SG_Vil_Fountain__Stone_SG_Obsidian']={-702.576,44.136,598.372,15.57,15.022,13.908,4,false,'Stone_SG_Obsidian','',''},
  ['SG_Vil_Fountain__Stone_SG_Trim']={-702.576,40.75,598.372,15.225,9.3,14.987,4,false,'Stone_SG_Trim','',''},
  ['SG_Vil_Fountain__Water_SG']={-702.576,41.725,598.372,12.069,7.15,12.069,4,false,'Water_SG','',''},
  ['SG_Vil_HouseDress__Cloth_SG_Purple']={-756.683,48.35,583.451,113.103,12.2,125.922,4,true,'Cloth_SG_Purple','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Lantern_Glow']={-742.411,44.986,592.274,150.645,9.956,162.828,4,false,'Lantern_Glow','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Leaf_SGPropBloom_g10_10']={-732.797,41.042,660.822,49.157,8.201,34.875,4,false,'Leaf_SGPropBloom','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Leaf_SGPropBloom_g10_11']={-742.028,45.042,586.195,151.753,16.201,150.516,4,false,'Leaf_SGPropBloom','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Leaf_SG_Pine']={-742.058,44.83,594.598,151.899,16.12,167.542,4,false,'Leaf_SG_Pine','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Metal_Gold']={-742.426,47.13,592.274,151.016,14.639,163.23,4,true,'Metal_Gold','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Metal_SG_BlackIron']={-742.195,46.165,593.55,152.51,17.149,165.827,4,true,'Metal_SG_BlackIron','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Metal_SG_Silver']={-756.683,49.572,583.451,114.44,10.576,126.655,4,true,'Metal_SG_Silver','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__SG_Rune_Glow']={-756.683,49.06,583.451,112.101,9.147,125.078,4,false,'SG_Rune_Glow','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Stone_SG_Obsidian']={-742.07,45.27,594.598,152.171,18.26,167.849,4,true,'Stone_SG_Obsidian','','SG_Vil_HouseDress'},
  ['SG_Vil_HouseDress__Wood_SG_Dark']={-741.424,45.43,600.366,150.128,14.4,152.354,4,true,'Wood_SG_Dark','','SG_Vil_HouseDress'},
  ['SG_Vil_Houses_P1E__Cliff_Rock_SG_Dark']={-708.442,60.2,521.25,0.918,0.8,0.918,4,false,'Cliff_Rock_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Metal_SG_Iron']={-682.096,53.85,539.555,53.367,24.9,54.481,4,true,'Metal_SG_Iron','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Plaster_SGVil']={-684.385,47.8,539.556,57.492,21.2,56.817,4,true,'Plaster_SGVil','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Roof_SG_Slate']={-684.726,52.867,539.559,60.127,22.467,59.438,4,true,'Roof_SG_Slate','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Stone_SG_Block']={-685.912,46.4,539.556,54.133,21.2,57.019,4,true,'Stone_SG_Block','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Stone_SG_Block_B']={-687.278,49.3,539.556,51.4,23.4,57.019,4,true,'Stone_SG_Block_B','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Stone_SG_Castle']={-685.912,45.1,539.556,53.556,15.8,56.442,4,true,'Stone_SG_Castle','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Stone_SG_Obsidian']={-684.199,47.925,539.556,57.9,24.25,57.36,4,true,'Stone_SG_Obsidian','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Stone_SG_Trim']={-684.195,49.1,539.556,57.644,24.6,57.097,4,true,'Stone_SG_Trim','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Window_Warm']={-683.983,46.654,539.556,56.306,15.109,54.965,4,false,'Window_Warm','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1E__Wood_SG_Dark']={-684.586,48.194,539.557,60.276,21.989,59.741,4,true,'Wood_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Cliff_Rock_SG_Dark']={-762.28,62.6,643.644,0.918,0.8,0.918,4,false,'Cliff_Rock_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Metal_SG_Iron']={-734.097,51.525,663.045,63.965,20.249,38.312,4,true,'Metal_SG_Iron','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Plaster_SGVil']={-732.576,47.8,661.663,69.626,21.2,42.912,4,true,'Plaster_SGVil','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Roof_SG_Slate']={-732.4,50.187,661.486,72.611,17.106,45.918,4,true,'Roof_SG_Slate','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Stone_SG_Block']={-732.797,48.9,650.017,69.761,22.6,20.198,4,true,'Stone_SG_Block','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Stone_SG_Block_B']={-732.797,50.5,658.322,69.761,22.6,31.153,4,true,'Stone_SG_Block_B','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Stone_SG_Castle']={-732.797,40.4,650.017,69.184,6.4,19.621,4,true,'Stone_SG_Castle','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Stone_SG_Obsidian']={-732.797,48.325,661.663,70.102,25.05,43.83,4,true,'Stone_SG_Obsidian','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Stone_SG_Trim']={-732.797,49.5,661.041,69.839,25.4,42.324,4,true,'Stone_SG_Trim','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Window_Warm']={-732.673,46.335,661.663,67.438,14.47,39.982,4,false,'Window_Warm','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P1W__Wood_SG_Dark']={-732.51,48.19,661.596,72.687,21.98,45.986,4,true,'Wood_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Cliff_Rock_SG_Dark']={-743.144,63.4,533.984,0.918,0.8,0.918,4,false,'Cliff_Rock_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Metal_SG_Iron']={-762.635,59.4,525.082,39.916,20.0,36.047,4,true,'Metal_SG_Iron','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Plaster_SGVil']={-762.929,55.3,524.957,48.03,20.2,38.133,4,true,'Plaster_SGVil','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Roof_SG_Slate']={-762.915,57.697,524.963,51.395,16.127,40.769,4,true,'Roof_SG_Slate','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Stone_SG_Block']={-764.417,56.8,523.609,44.748,22.4,35.641,4,true,'Stone_SG_Block','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Stone_SG_Castle_B']={-779.556,48.3,513.554,13.894,6.2,14.953,4,false,'Stone_SG_Castle_B','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Stone_SG_Obsidian']={-762.708,55.425,525.05,48.506,23.25,38.863,4,true,'Stone_SG_Obsidian','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Stone_SG_Trim']={-763.096,56.6,524.428,47.469,23.6,37.357,4,true,'Stone_SG_Trim','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Window_Warm']={-762.929,54.235,524.687,46.038,14.27,35.742,4,false,'Window_Warm','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2E__Wood_SG_Dark']={-762.922,55.696,524.959,51.237,20.992,41.064,4,true,'Wood_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Cliff_Rock_SG_Dark']={-819.934,69.8,614.828,0.918,0.8,0.918,4,false,'Cliff_Rock_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Metal_SG_Iron']={-803.027,59.75,635.601,47.165,20.7,54.531,4,true,'Metal_SG_Iron','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Plaster_SGVil']={-802.005,55.8,634.982,51.825,21.2,62.66,4,true,'Plaster_SGVil','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Roof_SG_Slate']={-801.824,60.229,634.991,54.817,21.192,66.03,4,true,'Roof_SG_Slate','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Stone_SG_Block']={-802.226,57.3,633.411,51.96,23.4,60.094,4,true,'Stone_SG_Block','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Stone_SG_Block_B']={-802.226,48.4,623.499,51.96,5.6,32.815,4,true,'Stone_SG_Block_B','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Stone_SG_Castle']={-802.226,48.4,621.635,51.383,6.4,35.966,4,true,'Stone_SG_Castle','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Stone_SG_Obsidian']={-802.226,55.925,634.982,52.301,24.25,63.578,4,true,'Stone_SG_Obsidian','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Stone_SG_Trim']={-802.226,57.1,634.36,52.039,24.6,62.072,4,true,'Stone_SG_Trim','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Window_Warm']={-802.103,54.474,634.982,49.637,14.748,59.731,4,false,'Window_Warm','','SG_Vil_Houses'},
  ['SG_Vil_Houses_P2W__Wood_SG_Dark']={-801.937,56.191,634.987,54.89,21.983,65.873,4,true,'Wood_SG_Dark','','SG_Vil_Houses'},
  ['SG_Vil_Lamps__Lantern_Glow']={-733.789,48.5,593.975,73.511,9.7,92.75,4,false,'Lantern_Glow','',''},
  ['SG_Vil_Lamps__Metal_Gold']={-733.789,48.82,593.974,74.101,11.46,93.34,4,true,'Metal_Gold','',''},
  ['SG_Vil_Lamps__Metal_SG_BlackIron']={-733.789,49.175,593.975,72.79,24.15,92.029,4,true,'Metal_SG_BlackIron','',''},
  ['SG_Vil_Lamps__Metal_SG_Silver']={-746.208,57.795,579.853,9.428,7.33,20.258,4,false,'Metal_SG_Silver','',''},
  ['SG_Vil_Lamps__Stone_SG_Obsidian']={-733.789,40.65,593.974,73.97,8.9,93.209,4,true,'Stone_SG_Obsidian','',''},
  ['SG_Vil_Lamps__Stone_SG_Violet']={-746.208,45.2,579.853,9.856,0.2,21.088,4,false,'Stone_SG_Violet','',''},
  ['SG_Vil_Plaza__SG_VioletDeep_Glow']={-702.576,36.225,598.372,48.013,0.25,20.59,4,false,'SG_VioletDeep_Glow','',''},
  ['SG_Vil_Plaza__Stone_Paving_SG']={-702.576,36.11,598.372,51.998,0.32,51.998,4,false,'Stone_Paving_SG','',''},
  ['SG_Vil_Plaza__Stone_SGVilCobble']={-702.576,36.2,598.372,32.799,0.2,32.799,4,true,'Stone_SGVilCobble','',''},
  ['SG_Vil_Plaza__Stone_SG_Castle_B']={-702.576,36.2,598.372,45.823,0.22,45.823,4,true,'Stone_SG_Castle_B','',''},
  ['SG_Vil_Plaza__Stone_SG_Obsidian']={-702.576,36.22,598.372,48.333,0.24,21.345,4,true,'Stone_SG_Obsidian','',''},
  ['SG_Vil_Plaza__Stone_SG_Trim']={-702.576,36.215,598.372,51.998,0.23,51.998,4,true,'Stone_SG_Trim','',''},
  ['SG_Vil_StairP1P2__Stone_Paving_SG']={-736.175,40.2,584.112,22.038,8.0,21.429,4,false,'Stone_Paving_SG','',''},
  ['SG_Vil_StairP1P2__Stone_SG_Block']={-780.35,40.969,616.99,108.105,9.538,120.195,4,true,'Stone_SG_Block','',''},
  ['SG_Vil_StairP1P2__Stone_SG_Block_B']={-778.481,40.969,620.38,107.497,9.538,117.095,4,true,'Stone_SG_Block_B','',''},
  ['SG_Vil_Streets_P1__Stone_SGVilCobble']={-710.633,36.1,589.757,88.536,0.3,197.445,4,true,'Stone_SGVilCobble','',''},
  ['SG_Vil_Streets_P1__Stone_SG_Block']={-709.968,36.25,588.85,87.236,0.34,195.725,4,true,'Stone_SG_Block','',''},
  ['SG_Vil_Streets_P1__Stone_SG_Block_B']={-712.514,36.25,589.787,84.819,0.34,195.662,4,true,'Stone_SG_Block_B','',''},
  ['SG_Vil_Streets_P1__Stone_SG_Floor']={-710.672,36.188,589.662,85.76,0.175,196.327,4,true,'Stone_SG_Floor','',''},
  ['SG_Vil_Streets_P2__Stone_SGVilCobble']={-772.341,44.1,542.621,107.565,0.3,252.556,4,true,'Stone_SGVilCobble','',''},
  ['SG_Vil_Streets_P2__Stone_SG_Block']={-772.192,44.25,547.168,103.365,0.34,243.554,4,true,'Stone_SG_Block','',''},
  ['SG_Vil_Streets_P2__Stone_SG_Block_B']={-772.538,44.25,541.51,107.209,0.34,248.529,4,true,'Stone_SG_Block_B','',''},
  ['SG_Vil_Streets_P2__Stone_SG_Floor']={-772.337,44.188,542.631,104.795,0.175,251.403,4,true,'Stone_SG_Floor','',''},
  ['SG_Vil_Streets_P3__Stone_SGVilCobble']={-796.062,52.1,464.777,58.495,0.3,67.889,4,true,'Stone_SGVilCobble','',''},
  ['SG_Sum_Balustrade__Stone_SG_Block']={-767.449,39.25,714.618,43.41,6.3,62.118,5,true,'Stone_SG_Block','','SG_Sum'},
  ['SG_Sum_Balustrade__Stone_SG_Block_B']={-766.365,39.6,714.876,44.907,7.0,63.816,5,true,'Stone_SG_Block_B','','SG_Sum'},
  ['SG_Sum_Balustrade__Stone_SG_Trim']={-766.507,41.775,714.871,45.584,8.05,64.201,5,true,'Stone_SG_Trim','','SG_Sum'},
  ['SG_Sum_Base__Stone_Paving_SG']={-768.518,42.2,727.118,13.944,4.0,17.295,5,false,'Stone_Paving_SG','','SG_Sum'},
  ['SG_Sum_Base__Stone_SG_Block']={-770.496,41.75,732.834,30.664,4.3,25.732,5,false,'Stone_SG_Block','','SG_Sum'},
  ['SG_Sum_Base__Stone_SG_Block_B']={-770.969,42.35,732.198,29.719,5.5,28.479,5,false,'Stone_SG_Block_B','','SG_Sum'},
  ['SG_Sum_Base__Stone_SG_Castle']={-770.611,42.0,733.382,28.535,2.2,24.467,5,false,'Stone_SG_Castle','','SG_Sum'},
  ['SG_Sum_Base__Stone_SG_Floor']={-770.618,42.19,733.356,29.135,2.58,25.001,5,false,'Stone_SG_Floor','','SG_Sum'},
  ['SG_Sum_Base__Stone_SG_Trim']={-766.571,43.365,723.553,12.783,4.19,11.714,5,false,'Stone_SG_Trim','','SG_Sum'},
  ['SG_Sum_BaseTrim__Metal_SG_Silver']={-767.496,42.25,725.731,18.907,0.84,8.028,5,false,'Metal_SG_Silver','','SG_Sum'},
  ['SG_Sum_BaseTrim__Stone_SG_Trim']={-770.623,43.275,733.344,29.477,0.45,25.309,5,false,'Stone_SG_Trim','','SG_Sum'},
  ['SG_Sum_Bridge__Stone_Paving_SG']={-754.319,38.025,695.752,20.19,4.35,24.097,5,false,'Stone_Paving_SG','','SG_Sum'},
  ['SG_Sum_Bridge__Stone_SG_Block']={-755.106,32.125,696.309,21.58,18.85,26.058,5,false,'Stone_SG_Block','','SG_Sum'},
  ['SG_Sum_Bridge__Stone_SG_Trim']={-755.06,34.941,696.521,21.949,13.938,25.752,5,false,'Stone_SG_Trim','','SG_Sum'},
  ['SG_Sum_FloorInlay__Stone_SG_Block']={-767.495,40.18,724.165,41.218,0.16,38.347,5,true,'Stone_SG_Block','','SG_Sum'},
  ['SG_Sum_FloorInlay__Stone_SG_Block_B']={-767.457,40.175,725.153,41.294,0.15,40.021,5,true,'Stone_SG_Block_B','','SG_Sum'},
  ['SG_Sum_FloorInlay__Stone_SG_Floor']={-764.136,40.175,717.233,22.892,0.15,21.729,5,false,'Stone_SG_Floor','','SG_Sum'},
  ['SG_Sum_OrderDressing__Cloth_SG_Purple']={-759.773,45.65,707.611,17.99,6.2,7.789,5,false,'Cloth_SG_Purple','','SG_Sum'},
  ['SG_Sum_OrderDressing__Lantern_Glow']={-767.723,43.215,724.685,39.94,1.53,34.011,5,false,'Lantern_Glow','','SG_Sum'},
  ['SG_Sum_OrderDressing__Metal_Gold']={-767.709,45.469,722.816,40.408,6.561,38.319,5,true,'Metal_Gold','','SG_Sum'},
  ['SG_Sum_OrderDressing__Metal_SG_BlackIron']={-759.856,45.82,707.798,18.826,6.44,8.24,5,false,'Metal_SG_BlackIron','','SG_Sum'},
  ['SG_Sum_OrderDressing__Metal_SG_Silver']={-767.703,45.58,722.771,40.616,7.16,38.662,5,true,'Metal_SG_Silver','','SG_Sum'},
  ['SG_Sum_OrderDressing__SG_Rune_Glow']={-759.61,46.668,707.178,16.779,1.468,7.174,5,false,'SG_Rune_Glow','','SG_Sum'},
  ['SG_Sum_OrderDressing__Stone_SG_Obsidian']={-767.696,44.395,722.825,40.823,8.39,38.807,5,true,'Stone_SG_Obsidian','','SG_Sum'},
  ['SG_Sum_Sphere_Frame__Metal_SG_Silver']={-771.559,88.495,735.304,18.943,23.61,18.943,5,false,'Metal_SG_Silver','','SG_Sum'},
  ['SG_Sum_Sphere_Frame__SG_Violet_Glow']={-771.559,97.5,735.304,1.367,1.4,1.326,5,false,'SG_Violet_Glow','','SG_Sum'},
  ['SG_Sum_Tower_Banners__Cloth_SG_Purple']={-770.301,63.05,732.718,27.806,12.6,12.792,5,false,'Cloth_SG_Purple','','SG_Sum'},
  ['SG_Sum_Tower_Banners__SG_Rune_Glow']={-770.432,64.964,732.861,26.034,2.238,11.555,5,false,'SG_Rune_Glow','','SG_Sum'},
  ['SG_Sum_Tower_Banners__Stone_SG_Obsidian']={-770.299,66.486,732.704,27.821,4.768,12.824,5,false,'Stone_SG_Obsidian','','SG_Sum'},
  ['SG_Sum_Tower_Banners__Wood_SG_Dark']={-770.087,70.0,732.917,30.02,0.6,15.543,5,false,'Wood_SG_Dark','','SG_Sum'},
  ['SG_Sum_Tower_Glow__Lantern_Glow']={-769.644,57.95,731.785,21.744,20.9,17.475,5,false,'Lantern_Glow','','SG_Sum'},
  ['SG_Sum_Tower_Glow__SG_SumPortal_Glow']={-771.559,57.525,735.911,14.824,26.75,11.198,5,false,'SG_SumPortal_Glow','','SG_Sum'},
  ['SG_Sum_Tower_Glow__SG_SumStar_Glow']={-771.559,58.333,735.828,15.194,21.834,11.712,5,false,'SG_SumStar_Glow','','SG_Sum'},
  ['SG_Sum_Tower_Glow__SG_Violet_Glow']={-771.05,59.6,734.938,7.461,31.1,13.988,5,false,'SG_Violet_Glow','','SG_Sum'},
  ['SG_Sum_Tower_Silver__Metal_SG_BlackIron']={-770.215,69.5,732.603,28.645,0.28,13.388,5,false,'Metal_SG_BlackIron','','SG_Sum'},
  ['SG_Sum_Tower_Silver__Metal_SG_Silver']={-769.654,61.895,733.435,31.965,36.79,24.054,5,true,'Metal_SG_Silver','','SG_Sum'},
  ['SG_Sum_Tower_Stone__Metal_SG_Iron']={-768.199,48.3,727.388,20.034,2.6,9.862,5,false,'Metal_SG_Iron','','SG_Sum'},
  ['SG_Sum_Tower_Stone__Stone_SG_Block']={-769.92,60.25,733.402,25.048,33.42,23.464,5,false,'Stone_SG_Block','','SG_Sum'},
  ['SG_Sum_Tower_Stone__Stone_SG_Castle']={-770.225,60.48,733.708,24.044,33.96,22.46,5,false,'Stone_SG_Castle','','SG_Sum'},
  ['SG_Sum_Tower_Stone__Stone_SG_Floor']={-769.495,60.05,733.107,24.723,33.1,23.399,5,false,'Stone_SG_Floor','','SG_Sum'},
  ['SG_Water_Fall_East__Cliff_Rock_SG_Dark']={-661.277,35.08,460.119,3.161,0.3,1.757,6,false,'Cliff_Rock_SG_Dark','',''},
  ['SG_Water_Fall_East__Foam']={-653.916,-15.246,447.679,31.087,102.533,25.224,6,false,'Foam','',''},
  ['SG_Water_Fall_East__SG_Moon_Glow']={-653.291,-9.991,445.832,11.694,89.984,12.453,6,false,'SG_Moon_Glow','',''},
  ['SG_Water_Fall_East__SG_WaterMist_Glow']={-655.367,-15.703,446.294,24.505,102.481,20.179,6,false,'SG_WaterMist_Glow','',''},
  ['SG_Water_Fall_East__Water_Fall']={-652.174,-12.309,446.181,18.034,95.101,12.851,6,false,'Water_Fall','',''},
  ['SG_Water_Fall_East__Water_SG']={-653.909,-12.072,449.636,22.853,95.857,22.126,6,false,'Water_SG','',''},
  ['SG_Water_Fall_North__Cliff_Rock_SG_Dark']={-1010.168,51.08,521.595,0.717,0.3,3.224,6,false,'Cliff_Rock_SG_Dark','',''},
  ['SG_Water_Fall_North__Foam']={-1025.827,-7.69,520.402,31.643,118.312,38.262,6,false,'Foam','',''},
  ['SG_Water_Fall_North__SG_Moon_Glow']={-1028.755,-0.749,521.141,18.609,103.489,11.1,6,false,'SG_Moon_Glow','',''},
  ['SG_Water_Fall_North__SG_WaterMist_Glow']={-1028.754,-7.703,521.637,25.256,118.681,28.755,6,false,'SG_WaterMist_Glow','',''},
  ['SG_Water_Fall_North__Water_Fall']={-1028.701,-4.274,521.483,19.182,111.158,17.191,6,false,'Water_Fall','',''},
  ['SG_Water_Fall_North__Water_SG']={-1023.971,-4.227,519.429,28.506,111.546,28.091,6,false,'Water_SG','',''},
  ['SG_Water_Fall_South__Cliff_Rock_SG']={-655.593,28.082,646.652,13.644,15.764,5.365,6,false,'Cliff_Rock_SG','',''},
  ['SG_Water_Fall_South__Cliff_Rock_SG_Dark']={-655.534,31.5,645.367,5.193,3.8,2.848,6,false,'Cliff_Rock_SG_Dark','',''},
  ['SG_Water_Fall_South__Cliff_Rock_SG_Top']={-655.646,34.707,646.234,13.294,3.014,4.358,6,false,'Cliff_Rock_SG_Top','',''},
  ['SG_Water_Fall_South__Foam']={-655.846,-17.323,652.194,30.019,95.23,11.101,6,false,'Foam','',''},
  ['SG_Water_Fall_South__SG_Moon_Glow']={-656.028,-9.424,651.603,4.692,78.851,3.487,6,false,'SG_Moon_Glow','',''},
  ['SG_Water_Fall_South__SG_WaterMist_Glow']={-656.459,-18.564,650.661,23.84,97.582,12.107,6,false,'SG_WaterMist_Glow','',''},
  ['SG_Water_Fall_South__Water_Fall']={-656.186,-14.896,651.671,12.602,89.882,4.053,6,false,'Water_Fall','',''},
  ['SG_Water_Fall_South__Water_SG']={-655.426,-14.868,649.672,19.973,90.275,7.77,6,false,'Water_SG','',''},
  ['SG_Water_Fall_West__Cliff_Rock_SG_Dark']={-819.889,43.08,680.245,3.161,0.3,1.757,6,false,'Cliff_Rock_SG_Dark','',''},
  ['SG_Water_Fall_West__Foam']={-822.678,-11.653,689.824,33.516,110.238,20.31,6,false,'Foam','',''},
  ['SG_Water_Fall_West__SG_Moon_Glow']={-823.463,-3.945,688.459,6.669,94.357,8.258,6,false,'SG_Moon_Glow','',''},
  ['SG_Water_Fall_West__SG_WaterMist_Glow']={-823.498,-12.109,686.967,24.242,110.857,16.599,6,false,'SG_WaterMist_Glow','',''},
  ['SG_Water_Fall_West__Water_Fall']={-825.292,-8.27,688.257,18.466,103.168,10.961,6,false,'Water_Fall','',''},
  ['SG_Water_Fall_West__Water_SG']={-822.596,-8.227,686.838,24.672,103.546,14.346,6,false,'Water_SG','',''},
  ['SG_Exit_AnchorGuard__P_DS_Black']={-683.604,45.7,323.322,16.673,3.0,7.348,7,false,'P_DS_Black','','SG_Exit_AnchorGuard'},
  ['SG_Exit_Bridge__Cliff_Rock_SG']={-690.594,28.978,342.963,40.821,23.045,40.518,7,false,'Cliff_Rock_SG','',''},
  ['SG_Exit_Bridge__Cliff_Rock_SG_C']={-686.706,33.822,339.738,24.015,13.356,24.527,7,false,'Cliff_Rock_SG_C','',''},
  ['SG_Exit_Bridge__Cliff_Rock_SG_Dark']={-697.202,-1.75,362.837,54.037,84.5,85.616,7,false,'Cliff_Rock_SG_Dark','',''},
  ['SG_Exit_Bridge__Stone_Paving_SG']={-700.646,44.025,370.078,61.179,0.35,103.156,7,false,'Stone_Paving_SG','',''},
  ['SG_Exit_Bridge__Stone_SG_Block']={-703.1,12.925,373.141,65.386,61.85,108.583,7,true,'Stone_SG_Block','',''},
  ['SG_Exit_Bridge__Stone_SG_Floor']={-701.804,43.835,373.139,61.124,0.77,98.13,7,true,'Stone_SG_Floor','',''},
  ['SG_Exit_Bridge__Stone_SG_Trim']={-701.99,22.72,371.01,64.365,43.04,105.02,7,true,'Stone_SG_Trim','',''},
  ['SG_Exit_Head__Cloth_SG_Purple']={-725.977,52.75,423.152,24.388,5.2,10.517,7,false,'Cloth_SG_Purple','',''},
  ['SG_Exit_Head__Lantern_Glow']={-725.136,51.85,421.173,16.514,1.2,7.613,7,false,'Lantern_Glow','',''},
  ['SG_Exit_Head__Metal_Gold']={-725.988,53.166,423.18,24.411,4.368,10.572,7,false,'Metal_Gold','',''},
  ['SG_Exit_Head__Metal_SG_Iron']={-725.957,57.535,422.371,25.332,12.93,12.435,7,false,'Metal_SG_Iron','',''},
  ['SG_Exit_Head__Metal_SG_Silver']={-725.957,54.269,423.106,25.685,2.983,11.159,7,false,'Metal_SG_Silver','',''},
  ['SG_Exit_Head__Roof_SG_Slate']={-725.136,60.4,421.173,26.419,4.2,13.704,7,false,'Roof_SG_Slate','',''},
  ['SG_Exit_Head__SG_Rune_Glow']={-726.057,53.628,423.341,23.255,1.231,9.927,7,false,'SG_Rune_Glow','',''},
  ['SG_Exit_Head__Stone_Paving_SG']={-725.937,44.065,423.06,27.829,0.33,18.981,7,false,'Stone_Paving_SG','',''},
  ['SG_Exit_Head__Stone_SG_Block_B']={-725.136,44.5,421.173,27.506,1.6,14.79,7,false,'Stone_SG_Block_B','',''},
  ['SG_Exit_Head__Stone_SG_Castle_B']={-725.156,52.05,421.481,26.079,11.9,13.941,7,false,'Stone_SG_Castle_B','',''},
  ['SG_Exit_Head__Stone_SG_Trim']={-725.987,51.1,423.383,29.566,14.4,20.173,7,false,'Stone_SG_Trim','',''},
  ['SG_Exit_Rails__Lantern_Glow']={-715.758,49.112,397.702,32.044,1.925,42.428,7,false,'Lantern_Glow','',''},
  ['SG_Exit_Rails__Metal_Gold']={-715.877,49.719,399.357,32.337,2.871,39.649,7,true,'Metal_Gold','',''},
  ['SG_Exit_Rails__Metal_SG_Silver']={-715.877,48.23,399.357,32.573,0.27,39.885,7,true,'Metal_SG_Silver','',''},
  ['SG_Exit_Rails__P_DS_Black']={-694.509,49.305,352.213,48.709,4.51,67.203,7,false,'P_DS_Black','',''},
  ['SG_Exit_Rails__Stone_SG_Block']={-698.332,44.275,372.001,56.637,4.75,101.343,7,true,'Stone_SG_Block','',''},
  ['SG_Exit_Rails__Stone_SG_Block_B']={-701.75,43.875,367.385,63.441,3.95,95.572,7,true,'Stone_SG_Block_B','',''},
  ['SG_Exit_Rails__Stone_SG_Castle_B']={-696.018,45.75,352.213,45.234,2.6,66.744,7,false,'Stone_SG_Castle_B','',''},
  ['SG_Exit_Rails__Stone_SG_Obsidian']={-715.877,47.195,399.357,32.809,1.8,40.121,7,true,'Stone_SG_Obsidian','',''},
  ['SG_Exit_Rails__Stone_SG_Trim']={-701.773,45.725,370.66,63.718,3.75,104.163,7,true,'Stone_SG_Trim','',''},
  ['SG_Exit_Rails__Wood_Lacquer_Red']={-694.226,48.5,352.162,47.933,6.7,65.962,7,false,'Wood_Lacquer_Red','',''},
  ['GATE_DemonSlayer_Barrier__Energy_Core_DemonSlayer_Glow']={-694.413,53.086,348.74,12.528,13.19,6.375,8,false,'Energy_Core_DemonSlayer_Glow','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Barrier__P_DS_Glow']={-694.388,53.2,348.729,14.924,18.0,6.712,8,false,'P_DS_Glow','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Lantern_Glow']={-695.612,54.84,352.406,28.727,13.52,19.689,8,false,'Lantern_Glow','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Leaf_GateDS_Wisteria']={-694.42,66.025,348.643,29.262,2.904,18.175,8,false,'Leaf_GateDS_Wisteria','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Metal_GateDS_Blade']={-696.505,62.299,351.08,31.035,20.257,18.659,8,false,'Metal_GateDS_Blade','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Metal_Gold']={-695.763,60.535,349.379,33.54,28.03,24.643,8,false,'Metal_Gold','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__P_DS_Black']={-696.249,58.125,349.19,34.143,27.85,23.744,8,false,'P_DS_Black','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Plaster_Cream']={-694.388,68.25,348.729,18.316,3.3,8.302,8,false,'Plaster_Cream','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Roof_Blue']={-695.192,60.658,349.946,31.108,21.625,26.149,8,false,'Roof_Blue','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Stone_Dark']={-693.331,44.35,346.016,24.542,1.5,17.628,8,false,'Stone_Dark','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Stone_Wall_Dark']={-695.814,46.725,352.089,38.257,6.25,26.124,8,false,'Stone_Wall_Dark','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Stone_Wall_Light']={-696.224,46.575,351.762,34.618,5.95,21.474,8,false,'Stone_Wall_Light','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Wood_Dark']={-694.388,68.4,348.729,29.374,3.6,18.354,8,false,'Wood_Dark','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Frame__Wood_Lacquer_Red']={-696.505,55.85,349.263,33.195,21.5,23.609,8,false,'Wood_Lacquer_Red','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Lock__Energy_Core_DemonSlayer_Glow']={-694.388,52.48,348.729,4.059,3.4,2.628,8,false,'Energy_Core_DemonSlayer_Glow','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Lock__Metal_Dark']={-694.388,52.28,348.729,1.476,1.0,2.589,8,false,'Metal_Dark','','GATE_DemonSlayer'},
  ['GATE_DemonSlayer_Lock__Metal_Gold']={-694.388,53.443,348.729,3.844,4.625,3.367,8,false,'Metal_Gold','','GATE_DemonSlayer'},
  ['SG_Prop_Court__Dirt_SG']={-828.917,52.46,544.748,37.138,0.72,70.251,9,false,'Dirt_SG','',''},
  ['SG_Prop_Court__Lantern_Glow']={-830.988,60.5,543.869,7.678,1.5,16.579,9,false,'Lantern_Glow','',''},
  ['SG_Prop_Court__Leaf_SGPropBloom']={-828.917,53.06,544.748,32.989,0.868,67.275,9,false,'Leaf_SGPropBloom','',''},
  ['SG_Prop_Court__Leaf_SGVegMoon']={-828.917,58.8,544.748,36.65,10.8,69.848,9,false,'Leaf_SGVegMoon','',''},
  ['SG_Prop_Court__Leaf_SG_Pine']={-828.917,58.45,544.748,36.76,11.5,69.895,9,false,'Leaf_SG_Pine','',''},
  ['SG_Prop_Court__Metal_SG_BlackIron']={-838.812,58.075,540.548,24.215,9.95,24.109,9,true,'Metal_SG_BlackIron','',''},
  ['SG_Prop_Court__Metal_SG_Silver']={-841.831,60.86,537.031,28.607,14.48,40.328,9,true,'Metal_SG_Silver','',''},
  ['SG_Prop_Court__SG_Rune_Glow']={-847.097,59.233,537.031,18.5,10.783,40.752,9,false,'SG_Rune_Glow','',''},
  ['SG_Prop_Court__Stone_SG_Block_B']={-826.615,52.95,545.725,49.557,1.7,90.088,9,true,'Stone_SG_Block_B','',''},
  ['SG_Prop_Court__Stone_SG_Obsidian']={-829.873,59.25,545.725,56.4,14.3,90.416,9,true,'Stone_SG_Obsidian','',''},
  ['SG_Prop_Court__Stone_SG_Trim']={-847.445,58.813,537.031,21.039,10.276,42.595,9,true,'Stone_SG_Trim','',''},
  ['SG_Prop_Court__Stone_SG_Violet']={-833.295,54.15,544.748,48.582,2.9,72.939,9,true,'Stone_SG_Violet','',''},
  ['SG_Prop_Court__Wood_SG_Dark']={-828.906,54.125,544.72,19.907,4.05,45.851,9,true,'Wood_SG_Dark','',''},
  ['SG_Prop_GateArch__Metal_SG_BlackIron']={-794.628,53.275,559.302,8.525,15.95,18.486,9,true,'Metal_SG_BlackIron','',''},
  ['SG_Prop_GateArch__Metal_SG_Silver']={-794.628,57.795,559.302,8.491,7.33,18.048,9,false,'Metal_SG_Silver','',''},
  ['SG_Prop_GateArch__SG_Rune_Glow']={-794.628,52.1,559.302,7.181,1.0,15.817,9,false,'SG_Rune_Glow','',''},
  ['SG_Prop_GateArch__Stone_SG_Obsidian']={-794.628,44.6,559.302,9.312,1.0,19.273,9,false,'Stone_SG_Obsidian','',''},
  ['SG_Prop_GateArch__Stone_SG_Violet']={-794.628,45.2,559.302,8.919,0.2,18.879,9,false,'Stone_SG_Violet','',''},
  ['SG_Prop_NobleAxis_P1__Cloth_SG_Purple']={-725.58,44.95,588.609,10.361,7.4,24.019,9,false,'Cloth_SG_Purple','',''},
  ['SG_Prop_NobleAxis_P1__Metal_Gold']={-725.552,45.542,588.62,10.416,6.216,24.043,9,false,'Metal_Gold','',''},
  ['SG_Prop_NobleAxis_P1__Metal_SG_BlackIron']={-725.626,44.1,588.589,10.807,13.2,24.963,9,false,'Metal_SG_BlackIron','',''},
  ['SG_Prop_NobleAxis_P1__Metal_SG_Silver']={-693.715,44.075,598.854,74.834,15.85,45.837,9,true,'Metal_SG_Silver','',''},
  ['SG_Prop_NobleAxis_P1__SG_Rune_Glow']={-725.391,46.136,588.689,9.68,1.598,22.673,9,false,'SG_Rune_Glow','',''},
  ['SG_Prop_NobleAxis_P1__SG_VioletDeep_Glow']={-688.0,36.2,604.559,80.774,0.1,34.495,9,false,'SG_VioletDeep_Glow','',''},
  ['SG_Prop_NobleAxis_P1__Stone_SG_MarbleBlack']={-688.474,36.825,601.69,85.395,1.35,49.097,9,true,'Stone_SG_MarbleBlack','',''},
  ['SG_Prop_NobleAxis_P1__Stone_SG_Obsidian']={-688.378,42.215,601.895,86.111,12.43,50.611,9,true,'Stone_SG_Obsidian','',''},
  ['SG_Prop_NobleAxis_P1__Stone_SG_Trim']={-688.0,36.2,604.559,85.353,0.1,45.284,9,true,'Stone_SG_Trim','',''},
  ['SG_Prop_NobleAxis_P2P3__Lantern_Glow']={-767.933,47.55,570.632,45.977,1.7,31.778,9,false,'Lantern_Glow','',''},
  ['SG_Prop_NobleAxis_P2P3__Metal_Gold']={-767.933,48.005,570.632,46.567,3.19,32.368,9,true,'Metal_Gold','',''},
  ['SG_Prop_NobleAxis_P2P3__Metal_SG_Silver']={-797.361,48.2,558.052,105.687,8.1,57.792,9,true,'Metal_SG_Silver','',''},
  ['SG_Prop_NobleAxis_P2P3__SG_VioletDeep_Glow']={-800.611,48.2,556.762,113.296,8.1,48.299,9,false,'SG_VioletDeep_Glow','',''},
  ['SG_Prop_NobleAxis_P2P3__Stone_SG_Floor']={-838.637,52.165,540.134,41.361,0.13,84.647,9,true,'Stone_SG_Floor','',''},
  ['SG_Prop_NobleAxis_P2P3__Stone_SG_MarbleBlack']={-800.806,48.198,556.302,117.358,8.095,58.083,9,true,'Stone_SG_MarbleBlack','',''},
  ['SG_Prop_NobleAxis_P2P3__Stone_SG_Obsidian']={-800.806,48.125,543.38,118.266,8.25,87.397,9,true,'Stone_SG_Obsidian','',''},
  ['SG_Prop_NobleAxis_P2P3__Stone_SG_Trim']={-800.806,48.2,542.058,118.266,8.1,88.496,9,true,'Stone_SG_Trim','',''},
  ['SG_Prop_NobleAxis_P2P3__Stone_SG_Violet']={-838.812,52.16,540.548,12.58,0.12,12.58,9,false,'Stone_SG_Violet','',''},
  ['SG_Prop_Plaza__Lantern_Glow']={-702.576,44.5,598.372,45.139,1.7,45.139,9,false,'Lantern_Glow','',''},
  ['SG_Prop_Plaza__Metal_Gold']={-702.576,44.82,598.372,45.729,3.46,45.729,9,true,'Metal_Gold','',''},
  ['SG_Prop_Plaza__Metal_SG_BlackIron']={-702.576,40.1,598.372,44.418,6.0,44.418,9,true,'Metal_SG_BlackIron','',''},
  ['SG_Prop_Plaza__Stone_SG_Block']={-702.576,36.82,598.372,48.051,1.25,39.955,9,true,'Stone_SG_Block','',''},
  ['SG_Prop_Plaza__Stone_SG_Obsidian']={-702.576,36.65,598.372,45.598,0.9,45.598,9,true,'Stone_SG_Obsidian','',''},
  ['SG_Prop_Plaza__Stone_SG_Trim']={-702.576,37.66,598.372,48.353,0.42,40.527,9,true,'Stone_SG_Trim','',''},
  ['SG_Prop_RouteLamps__Lantern_Glow']={-733.331,48.5,565.765,141.244,9.7,148.417,9,false,'Lantern_Glow','',''},
  ['SG_Prop_RouteLamps__Metal_Gold']={-733.331,48.82,565.765,141.834,11.46,149.007,9,true,'Metal_Gold','',''},
  ['SG_Prop_RouteLamps__Metal_SG_BlackIron']={-733.331,44.1,565.765,140.523,14.0,147.696,9,true,'Metal_SG_BlackIron','',''},
  ['SG_Prop_RouteLamps__Stone_SG_Obsidian']={-733.331,40.65,565.765,141.703,8.9,148.876,9,true,'Stone_SG_Obsidian','',''},
  ['SG_Veg_Pines_East__Grass_SG']={-787.655,34.478,410.282,0.609,0.812,0.571,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_East__Leaf_SGVegMoon']={-779.512,44.985,413.008,24.025,14.471,7.748,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_East__Leaf_SGVegShade']={-779.175,40.697,412.376,28.401,14.388,12.16,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_East__Leaf_SG_Pine']={-779.175,42.351,412.376,28.401,17.697,12.16,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_East__Wood_SG_Dark']={-778.244,37.72,413.066,22.085,8.273,6.021,10,false,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_North__Grass_SG']={-990.035,34.693,533.126,49.908,1.339,153.017,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_North__Leaf_SGVegMoon']={-989.504,65.71,532.447,53.187,55.553,159.96,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_North__Leaf_SGVegShade']={-989.653,61.332,532.86,59.027,55.846,162.357,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_North__Leaf_SG_Pine_g8_11']={-989.567,62.948,577.434,59.2,59.079,73.208,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_North__Leaf_SG_Pine_g8_12']={-998.611,43.702,480.426,28.849,20.195,57.488,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_North__Wood_SG_Dark']={-988.209,58.453,533.023,50.816,49.758,156.653,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_NorthE__Grass_SG']={-958.803,34.715,430.308,58.435,1.368,44.562,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_NorthE__Leaf_SGVegMoon']={-936.363,61.104,428.692,103.96,43.703,46.524,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_NorthE__Leaf_SGVegShade']={-935.754,56.387,429.146,108.795,46.72,51.454,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_NorthE__Leaf_SG_Pine']={-935.754,57.609,429.146,108.795,49.165,51.454,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_NorthE__Wood_SG_Dark']={-935.706,54.388,428.694,103.341,41.612,44.276,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_South__Grass_SG']={-661.238,31.699,649.466,106.927,11.319,95.347,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_South__Leaf_SGVegMoon']={-660.947,43.089,644.698,109.833,26.836,107.09,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_South__Leaf_SGVegShade']={-660.485,37.943,644.367,113.586,24.318,109.981,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_South__Leaf_SG_Pine']={-660.485,40.515,644.367,113.586,29.682,109.981,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_South__Wood_SG_Dark']={-660.071,35.204,644.33,108.413,19.23,104.274,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_SouthE__Grass_SG']={-642.463,35.775,527.427,18.527,3.976,125.452,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_SouthE__Leaf_SGVegMoon']={-663.181,47.372,516.813,60.812,14.178,151.553,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_SouthE__Leaf_SGVegShade']={-662.503,41.569,517.547,65.576,16.378,155.868,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_SouthE__Leaf_SG_Pine']={-662.503,43.347,517.547,65.576,19.933,155.868,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_SouthE__Wood_SG_Dark']={-663.356,38.396,516.326,59.299,10.172,148.443,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_VillageE__Grass_SG']={-750.017,48.557,488.3,87.422,9.057,138.873,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_VillageE__Leaf_SGVegMoon']={-750.266,60.566,487.884,90.251,25.216,139.068,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_VillageE__Leaf_SGVegShade']={-749.626,55.732,486.763,96.887,24.886,141.31,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_VillageE__Leaf_SG_Pine']={-749.626,57.638,486.763,96.887,28.698,141.31,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_VillageE__Stone_SG_Trim']={-792.209,52.33,427.333,3.8,0.42,3.8,10,false,'Stone_SG_Trim','',''},
  ['SG_Veg_Pines_VillageE__Wood_SG_Dark']={-748.881,52.347,487.882,88.622,17.526,136.826,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_VillageS__Grass_SG']={-719.22,36.73,568.106,102.619,1.39,214.302,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_VillageS__Leaf_SGVegMoon']={-719.84,49.377,568.082,102.987,13.698,216.643,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_VillageS__Leaf_SGVegShade']={-719.136,43.629,568.081,109.021,16.439,220.498,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_VillageS__Leaf_SG_Pine']={-719.136,45.251,568.081,109.021,19.683,220.498,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_VillageS__Stone_SG_Trim']={-719.22,36.33,567.911,103.379,0.42,214.673,10,true,'Stone_SG_Trim','',''},
  ['SG_Veg_Pines_VillageS__Wood_SG_Dark']={-719.226,40.146,567.804,101.221,9.129,212.683,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_VillageW__Grass_SG']={-809.058,44.711,616.93,83.117,1.367,74.402,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_VillageW__Leaf_SGVegMoon']={-808.455,56.956,617.557,84.393,18.161,78.889,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_VillageW__Leaf_SGVegShade']={-809.21,52.722,617.727,88.656,18.334,83.402,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_VillageW__Leaf_SG_Pine']={-809.21,54.178,617.727,88.656,21.245,83.402,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_VillageW__Wood_SG_Dark']={-807.781,48.531,618.159,82.964,9.896,76.098,10,true,'Wood_SG_Dark','',''},
  ['SG_Veg_Pines_West__Grass_SG']={-906.174,35.994,633.157,96.38,3.938,51.521,10,false,'Grass_SG','',''},
  ['SG_Veg_Pines_West__Leaf_SGVegMoon']={-907.36,48.501,633.839,101.89,22.184,59.383,10,false,'Leaf_SGVegMoon','',''},
  ['SG_Veg_Pines_West__Leaf_SGVegShade']={-907.219,43.303,633.209,106.482,22.118,64.121,10,false,'Leaf_SGVegShade','',''},
  ['SG_Veg_Pines_West__Leaf_SG_Pine']={-907.219,45.2,633.209,106.482,25.911,64.121,10,false,'Leaf_SG_Pine','',''},
  ['SG_Veg_Pines_West__Wood_SG_Dark']={-905.874,39.779,633.708,99.605,12.41,57.565,10,true,'Wood_SG_Dark','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_1__Metal_Gold']={-708.035,59.8,347.608,2.695,2.8,1.45,11,false,'Metal_Gold','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_1__P_DS_Glow']={-708.035,59.8,347.608,2.376,2.36,1.401,11,false,'P_DS_Glow','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_2__Metal_Gold']={-709.123,55.0,351.708,2.695,2.8,1.45,11,false,'Metal_Gold','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_2__P_DS_Glow']={-709.123,55.0,351.708,2.376,2.36,1.401,11,false,'P_DS_Glow','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_3__Metal_Gold']={-686.294,55.3,361.398,2.695,2.8,1.45,11,false,'Metal_Gold','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_3__P_DS_Glow']={-686.294,55.3,361.398,2.376,2.36,1.401,11,false,'P_DS_Glow','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_4__Metal_Gold']={-684.101,60.1,357.766,2.695,2.8,1.45,11,false,'Metal_Gold','',''},
  ['VFX_GATE_DemonSlayer_Tsuba_4__P_DS_Glow']={-684.101,60.1,357.766,2.376,2.36,1.401,11,false,'P_DS_Glow','',''},
  ['VFX_SGCRAFT_Ring_1__SG_VioletDeep_Glow']={-730.008,81.6,488.958,15.782,5.522,16.324,11,false,'SG_VioletDeep_Glow','',''},
  ['VFX_SGCRAFT_Ring_2__SG_VioletDeep_Glow']={-730.008,81.6,488.958,19.932,11.712,17.559,11,false,'SG_VioletDeep_Glow','',''},
  ['VFX_SGDUN_MouthCrystal__SG_Crystal_Glow']={-829.797,77.996,435.74,3.222,6.6,3.222,11,false,'SG_Crystal_Glow','',''},
  ['VFX_SGDUN_Portal__SG_Violet_Glow']={-855.634,59.84,424.565,4.123,10.066,9.359,11,false,'SG_Violet_Glow','',''},
  ['VFX_SGSUM_Ring_1__Metal_SG_Silver']={-771.559,86.2,735.304,23.662,7.267,23.151,11,false,'Metal_SG_Silver','',''},
  ['VFX_SGSUM_Ring_1__SG_SumStar_Glow']={-771.559,86.278,735.282,23.241,7.818,22.255,11,false,'SG_SumStar_Glow','',''},
  ['VFX_SGSUM_Ring_2__Metal_SG_Silver']={-771.56,86.2,735.304,17.275,17.32,2.806,11,false,'Metal_SG_Silver','',''},
  ['VFX_SGSUM_Ring_2__SG_SumStar_Glow']={-771.527,86.2,735.363,12.925,13.023,3.017,11,false,'SG_SumStar_Glow','',''},
  ['VFX_SGSUM_Ring_3__Metal_SG_Silver']={-771.559,86.2,735.304,8.826,13.37,15.313,11,false,'Metal_SG_Silver','',''},
  ['VFX_SGSUM_Ring_3__SG_SumStar_Glow']={-771.562,86.18,735.277,8.263,10.223,12.199,11,false,'SG_SumStar_Glow','',''},
  ['VFX_SGSUM_Star__SG_SumStar_Glow']={-771.559,86.83,735.304,11.908,11.94,5.733,11,false,'SG_SumStar_Glow','',''},
  ['VFX_SGSUM_Star__SG_Violet_Glow']={-771.559,86.83,735.304,11.908,11.94,5.733,11,false,'SG_Violet_Glow','',''},
  ['SG_Craft_Cauldron__Metal_Gold']={-730.008,48.313,488.958,6.725,4.246,6.452,12,false,'Metal_Gold','','SG_Craft'},
  ['SG_Craft_Cauldron__Metal_SG_Iron']={-730.008,48.207,488.958,6.4,4.302,6.4,12,false,'Metal_SG_Iron','','SG_Craft'},
  ['SG_Craft_Cauldron__Metal_SG_Silver']={-730.008,48.655,488.958,4.227,1.656,7.243,12,false,'Metal_SG_Silver','','SG_Craft'},
  ['SG_Craft_Cauldron__SG_Rune_Glow']={-730.008,49.449,488.958,5.201,6.002,6.771,12,false,'SG_Rune_Glow','','SG_Craft'},
  ['SG_Craft_Cauldron__SG_VioletDeep_Glow']={-730.008,45.94,488.958,7.68,0.12,7.68,12,false,'SG_VioletDeep_Glow','','SG_Craft'},
  ['SG_Craft_Cauldron__SG_Violet_Glow']={-730.008,48.484,488.958,5.201,3.929,5.201,12,false,'SG_Violet_Glow','','SG_Craft'},
  ['SG_Craft_Cauldron__Stone_SG_Obsidian']={-730.008,47.493,488.958,7.6,3.986,7.6,12,false,'Stone_SG_Obsidian','','SG_Craft'},
  ['SG_Craft_Cauldron__Wood_SG_Dark']={-730.912,50.8,486.597,1.095,2.779,1.974,12,false,'Wood_SG_Dark','','SG_Craft'},
  ['SG_Craft_Dome__Glass_SG_Rose']={-730.008,86.593,488.958,10.759,9.865,10.825,12,false,'Glass_SG_Rose','','SG_Craft'},
  ['SG_Craft_Dome__Metal_SG_Silver']={-730.008,78.625,488.958,30.146,30.9,30.146,12,true,'Metal_SG_Silver','','SG_Craft'},
  ['SG_Craft_Dome__Roof_SG_Navy']={-730.008,68.45,488.958,31.364,10.5,31.364,12,true,'Roof_SG_Navy','','SG_Craft'},
  ['SG_Craft_Dome__SG_VioletDeep_Glow']={-730.008,74.71,488.958,5.797,2.22,5.797,12,false,'SG_VioletDeep_Glow','','SG_Craft'},
  ['SG_Craft_Dome__SG_Violet_Glow']={-730.008,78.9,488.958,10.719,5.4,10.785,12,false,'SG_Violet_Glow','','SG_Craft'},
  ['SG_Craft_Dome__Stone_SG_Obsidian']={-730.008,74.6,488.958,6.2,3.6,6.2,12,false,'Stone_SG_Obsidian','','SG_Craft'},
  ['SG_Craft_Dome__Stone_SG_Violet']={-730.008,74.603,488.958,6.705,3.595,6.705,12,false,'Stone_SG_Violet','','SG_Craft'},
  ['SG_Craft_Dome__Window_Warm']={-730.008,74.71,488.958,5.774,2.22,5.774,12,false,'Window_Warm','','SG_Craft'},
  ['SG_Craft_Furnishings__Cloth_Canvas']={-730.008,48.174,489.477,26.055,7.992,21.411,12,false,'Cloth_Canvas','','SG_Craft'},
  ['SG_Craft_Furnishings__Cloth_SGCraftBook']={-729.999,49.225,488.164,26.057,9.05,24.226,12,true,'Cloth_SGCraftBook','','SG_Craft'},
  ['SG_Craft_Furnishings__Cloth_SG_Navy']={-730.006,49.316,489.04,26.054,10.133,26.04,12,true,'Cloth_SG_Navy','','SG_Craft'},
  ['SG_Craft_Furnishings__Cloth_SG_Purple']={-727.3,54.25,481.916,20.863,7.6,10.289,12,false,'Cloth_SG_Purple','','SG_Craft'},
  ['SG_Craft_Furnishings__Glass_SGCraftAmber']={-730.006,48.632,487.484,25.839,7.864,23.111,12,false,'Glass_SGCraftAmber','','SG_Craft'},
  ['SG_Craft_Furnishings__Glass_SGCraftPale']={-730.084,48.24,487.509,25.734,7.08,22.457,12,false,'Glass_SGCraftPale','','SG_Craft'},
  ['SG_Craft_Furnishings__Glass_SGCraftSage']={-729.924,48.492,487.946,25.788,7.584,22.628,12,false,'Glass_SGCraftSage','','SG_Craft'},
  ['SG_Craft_Furnishings__Glass_SG_Rose']={-724.282,47.89,479.184,0.779,1.1,0.768,12,false,'Glass_SG_Rose','','SG_Craft'},
  ['SG_Craft_Furnishings__Lantern_Glow']={-730.043,52.665,487.79,25.815,10.912,21.089,12,false,'Lantern_Glow','','SG_Craft'},
  ['SG_Craft_Furnishings__Leather']={-730.012,49.523,487.609,26.031,9.646,23.337,12,false,'Leather','','SG_Craft'},
  ['SG_Craft_Furnishings__Metal_Brass']={-728.969,48.615,478.017,5.337,3.27,2.464,12,false,'Metal_Brass','','SG_Craft'},
  ['SG_Craft_Furnishings__Metal_Gold']={-729.653,51.15,489.158,25.571,13.8,25.805,12,true,'Metal_Gold','','SG_Craft'},
  ['SG_Craft_Furnishings__Metal_SG_BlackIron']={-729.965,57.19,487.892,26.599,26.02,24.636,12,true,'Metal_SG_BlackIron','','SG_Craft'},
  ['SG_Craft_Furnishings__Metal_SG_Silver']={-728.338,51.18,487.704,23.538,14.56,22.707,12,false,'Metal_SG_Silver','','SG_Craft'},
  ['SG_Craft_Furnishings__SG_Rune_Glow']={-727.82,50.232,485.753,21.039,11.956,16.835,12,false,'SG_Rune_Glow','','SG_Craft'},
  ['SG_Craft_Furnishings__SG_VioletDeep_Glow']={-730.0,52.677,488.958,25.983,16.846,20.915,12,false,'SG_VioletDeep_Glow','','SG_Craft'},
  ['SG_Craft_Furnishings__Stone_SG_MarbleBlack']={-730.008,57.55,488.958,27.394,27.3,27.394,12,true,'Stone_SG_MarbleBlack','','SG_Craft'},
  ['SG_Craft_Furnishings__Stone_SG_Obsidian']={-730.008,52.75,488.948,26.699,17.7,26.718,12,true,'Stone_SG_Obsidian','','SG_Craft'},
  ['SG_Craft_Furnishings__Stone_SG_Trim']={-730.008,58.956,488.958,25.516,23.952,25.516,12,true,'Stone_SG_Trim','','SG_Craft'},
  ['SG_Craft_Furnishings__Stone_SG_Violet']={-730.008,61.597,488.958,26.699,18.395,26.699,12,true,'Stone_SG_Violet','','SG_Craft'},
  ['SG_Craft_Furnishings__Window_Warm']={-730.008,57.35,483.018,26.693,7.5,14.813,12,false,'Window_Warm','','SG_Craft'},
  ['SG_Craft_Furnishings__Wood_SG_Dark']={-730.008,49.7,487.893,26.64,11.0,25.014,12,true,'Wood_SG_Dark','','SG_Craft'},
  ['SG_Craft_Shell__Cloth_SG_Purple']={-736.708,56.95,504.745,13.249,8.2,5.79,12,false,'Cloth_SG_Purple','','SG_Craft'},
  ['SG_Craft_Shell__Dirt_SG']={-730.008,44.825,488.958,37.804,0.15,37.804,12,false,'Dirt_SG','','SG_Craft'},
  ['SG_Craft_Shell__Lantern_Glow']={-737.353,51.7,506.264,13.159,1.7,6.378,12,false,'Lantern_Glow','','SG_Craft'},
  ['SG_Craft_Shell__Metal_Gold']={-737.156,55.67,505.799,14.144,10.76,7.898,12,false,'Metal_Gold','','SG_Craft'},
  ['SG_Craft_Shell__Metal_SG_BlackIron']={-730.008,53.22,491.176,31.395,16.24,35.832,12,true,'Metal_SG_BlackIron','','SG_Craft'},
  ['SG_Craft_Shell__Metal_SG_Silver']={-730.008,64.798,490.387,32.198,14.403,35.055,12,true,'Metal_SG_Silver','','SG_Craft'},
  ['SG_Craft_Shell__SG_Crystal_Glow']={-730.01,46.374,488.945,37.155,3.952,37.145,12,false,'SG_Crystal_Glow','','SG_Craft'},
  ['SG_Craft_Shell__SG_Rune_Glow']={-736.788,58.248,504.933,12.462,0.906,5.346,12,false,'SG_Rune_Glow','','SG_Craft'},
  ['SG_Craft_Shell__SG_VioletDeep_Glow']={-730.008,54.15,489.834,32.0,13.9,33.752,12,false,'SG_VioletDeep_Glow','','SG_Craft'},
  ['SG_Craft_Shell__Stone_SGCraftDark']={-730.008,56.75,490.482,31.969,25.7,35.016,12,true,'Stone_SGCraftDark','','SG_Craft'},
  ['SG_Craft_Shell__Stone_SG_Castle']={-730.008,52.85,488.958,33.163,17.3,33.163,12,true,'Stone_SG_Castle','','SG_Craft'},
  ['SG_Craft_Shell__Stone_SG_Obsidian']={-730.008,53.0,489.739,38.325,18.4,39.887,12,true,'Stone_SG_Obsidian','','SG_Craft'},
  ['SG_Craft_Shell__Stone_SG_Violet']={-730.008,57.626,490.16,33.46,25.253,35.865,12,true,'Stone_SG_Violet','','SG_Craft'},
  ['SG_Craft_Shell__Window_Warm']={-730.008,57.3,481.932,31.075,7.6,17.023,12,false,'Window_Warm','','SG_Craft'},
  ['SG_Dun_Approach_Floor__SG_Rune_Glow']={-830.592,52.295,435.236,4.067,0.13,6.973,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Approach_Floor__SG_VioletDeep_Glow']={-819.165,52.29,440.252,37.056,0.12,24.362,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_Approach_Floor__Stone_SG_MarbleBlack']={-822.198,52.215,434.739,43.737,0.23,43.122,13,true,'Stone_SG_MarbleBlack','','SG_Dun'},
  ['SG_Dun_Approach_Floor__Stone_SG_Obsidian']={-822.267,52.225,434.747,44.489,0.55,44.767,13,true,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Approach_Guard__Metal_SG_BlackIron']={-825.707,56.919,437.411,22.378,5.291,33.356,13,true,'Metal_SG_BlackIron','','SG_Dun'},
  ['SG_Dun_Approach_Guard__Metal_SG_Silver']={-821.673,55.625,439.942,19.54,0.25,31.991,13,false,'Metal_SG_Silver','','SG_Dun'},
  ['SG_Dun_Approach_Guard__SG_Crystal_Glow']={-821.673,57.75,439.942,18.05,3.6,30.501,13,false,'SG_Crystal_Glow','','SG_Dun'},
  ['SG_Dun_Approach_Guard__SG_Rune_Glow']={-821.656,54.456,439.928,16.555,1.316,27.451,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Approach_Guard__SG_VioletDeep_Glow']={-821.674,53.41,439.942,19.016,0.22,31.466,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_Approach_Guard__Stone_SGDunVault']={-821.674,54.15,439.942,18.885,2.7,31.335,13,false,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Approach_Guard__Stone_SG_Obsidian']={-821.674,54.075,439.942,19.934,4.15,32.384,13,true,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Cave_Body__Cliff_Rock_SGDunBasalt']={-854.459,71.2,425.295,46.129,48.0,39.484,13,true,'Cliff_Rock_SGDunBasalt','','SG_Dun'},
  ['SG_Dun_Cave_Body__Grass_SG']={-854.887,88.746,424.465,42.2,34.348,37.975,13,false,'Grass_SG','','SG_Dun'},
  ['SG_Dun_Cave_Body__SG_Crystal_Glow']={-842.446,79.609,424.639,23.555,13.35,40.491,13,false,'SG_Crystal_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Body__SG_VioletDeep_Glow']={-853.5,76.205,424.649,42.339,36.181,40.775,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Body__Stone_SG_Obsidian']={-853.582,76.56,422.805,45.419,58.72,46.451,13,true,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Cave_Interior__SG_Crystal_Glow']={-846.719,59.287,429.474,21.31,15.437,23.829,13,false,'SG_Crystal_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Interior__SG_VioletDeep_Glow']={-841.671,52.275,430.7,16.897,0.15,15.805,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Interior__Stone_SGDunCaveDeep']={-851.609,61.841,426.817,20.343,20.082,21.381,13,false,'Stone_SGDunCaveDeep','','SG_Dun'},
  ['SG_Dun_Cave_Interior__Stone_SG_MarbleBlack']={-841.705,52.21,430.977,18.904,0.22,20.607,13,false,'Stone_SG_MarbleBlack','','SG_Dun'},
  ['SG_Dun_Cave_Interior__Stone_SG_Obsidian']={-846.041,63.775,429.027,29.784,26.246,27.92,13,false,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__Metal_SG_BlackIron']={-829.958,81.225,435.671,0.526,0.941,0.371,13,false,'Metal_SG_BlackIron','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__Metal_SG_Silver']={-830.947,82.6,435.251,0.921,1.1,0.921,13,false,'Metal_SG_Silver','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__SG_Rune_Glow']={-831.694,67.99,434.913,9.242,26.6,21.562,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__SG_VioletDeep_Glow']={-831.72,67.56,434.923,9.898,30.051,23.071,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__Stone_SGDunVault']={-833.847,57.815,434.021,14.066,7.129,25.139,13,false,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__Stone_SG_Obsidian']={-833.737,67.15,433.942,15.223,30.5,27.192,13,true,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Cave_Mouth__Stone_SG_Violet']={-833.907,67.496,434.021,14.422,31.191,25.692,13,true,'Stone_SG_Violet','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Cloth_SG_Purple']={-830.855,66.45,435.29,13.487,10.4,31.383,13,false,'Cloth_SG_Purple','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Lantern_Glow']={-817.505,55.55,439.183,34.619,1.7,28.844,13,false,'Lantern_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Metal_Gold']={-818.75,63.03,436.749,37.698,17.24,34.302,13,true,'Metal_Gold','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Metal_SG_BlackIron']={-830.901,71.8,435.271,13.932,0.28,32.327,13,false,'Metal_SG_BlackIron','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Metal_SG_Silver']={-819.606,65.598,436.483,39.673,22.795,35.096,13,true,'Metal_SG_Silver','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__SG_Rune_Glow']={-830.666,68.056,435.37,12.805,1.598,30.037,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__SG_VioletDeep_Glow']={-832.202,68.0,434.799,15.033,26.8,31.049,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Stone_SGDunVault']={-832.696,63.95,434.509,16.308,20.1,32.732,13,true,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Stone_SG_Obsidian']={-820.572,64.3,435.825,41.867,24.8,36.675,13,true,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Cave_Pillars__Stone_SG_Violet']={-832.696,53.75,434.509,17.095,0.3,33.519,13,false,'Stone_SG_Violet','','SG_Dun'},
  ['SG_Dun_Cave_Pines__Leaf_SGVegShade']={-857.365,84.369,422.552,39.101,26.792,35.204,13,false,'Leaf_SGVegShade','','SG_Dun'},
  ['SG_Dun_Cave_Pines__Leaf_SG_Pine']={-857.365,85.323,422.552,39.101,28.699,35.204,13,false,'Leaf_SG_Pine','','SG_Dun'},
  ['SG_Dun_Cave_Pines__Wood_SG_Dark']={-857.085,82.793,422.765,35.423,24.615,31.125,13,true,'Wood_SG_Dark','','SG_Dun'},
  ['SG_Dun_House_Portal__Metal_SG_BlackIron']={-855.608,59.6,424.784,6.409,14.0,13.286,13,false,'Metal_SG_BlackIron','','SG_Dun'},
  ['SG_Dun_House_Portal__SG_DunVoid_Glow']={-855.893,59.6,424.663,4.521,11.1,10.296,13,false,'SG_DunVoid_Glow','','SG_Dun'},
  ['SG_Dun_House_Portal__SG_VioletDeep_Glow']={-855.316,59.6,424.965,5.359,12.798,10.69,13,false,'SG_VioletDeep_Glow','','SG_Dun'},
  ['SG_Dun_House_Portal__Stone_SG_Obsidian']={-855.523,60.85,424.839,6.325,15.7,14.36,13,false,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_R3_ExitSpiral__SG_Violet_Glow']={-868.891,12.242,456.951,8.455,9.399,3.74,13,false,'SG_Violet_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Floor__Metal_SG_Silver']={-876.852,5.8,476.603,6.4,0.4,6.4,13,false,'Metal_SG_Silver','','SG_Dun'},
  ['SG_Dun_Rooms_Floor__SG_Rune_Glow']={-876.966,5.965,476.597,12.087,0.13,12.311,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Floor__Stone_SGDunVault']={-876.852,5.8,476.603,13.999,0.4,13.999,13,false,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Rooms_Floor__Stone_SG_Block_B']={-891.421,5.625,514.483,86.831,0.45,133.454,13,true,'Stone_SG_Block_B','','SG_Dun'},
  ['SG_Dun_Rooms_Floor__Stone_SG_Floor']={-891.421,5.8,514.483,86.831,0.4,133.454,13,true,'Stone_SG_Floor','','SG_Dun'},
  ['SG_Dun_Rooms_Floor__Stone_SG_Trim']={-891.421,5.8,514.483,84.209,0.4,130.832,13,true,'Stone_SG_Trim','','SG_Dun'},
  ['SG_Dun_Rooms_Iron__Lantern_Glow']={-894.048,19.125,515.264,67.32,8.95,120.414,13,false,'Lantern_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Iron__Metal_SG_Iron']={-894.307,19.865,515.264,68.335,13.87,121.901,13,true,'Metal_SG_Iron','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__Metal_SG_Silver']={-894.825,21.628,518.946,21.576,2.535,46.78,13,true,'Metal_SG_Silver','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__SG_Rune_Glow']={-894.825,21.5,518.946,20.916,1.702,46.254,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__Stone_SGDunVault']={-891.421,15.55,514.483,84.331,17.3,130.954,13,true,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__Stone_SG_Castle']={-894.051,12.0,514.483,81.57,10.2,133.454,13,true,'Stone_SG_Castle','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__Stone_SG_Castle_B']={-889.37,12.0,515.264,82.729,10.2,126.422,13,true,'Stone_SG_Castle_B','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__Stone_SG_Obsidian']={-894.825,21.5,518.946,21.8,2.8,46.383,13,true,'Stone_SG_Obsidian','','SG_Dun'},
  ['SG_Dun_Rooms_Kit__Stone_SG_Trim']={-891.421,15.45,514.483,86.831,18.9,133.454,13,true,'Stone_SG_Trim','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__Metal_SG_Silver']={-893.262,12.548,515.264,59.622,12.504,119.476,13,true,'Metal_SG_Silver','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__SG_DunVoid_Glow']={-918.033,12.2,573.625,9.559,10.3,4.208,13,false,'SG_DunVoid_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__SG_Rune_Glow']={-893.262,5.93,515.264,62.01,0.2,115.733,13,false,'SG_Rune_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__SG_Violet_Glow']={-918.222,12.257,573.328,8.564,9.395,3.786,13,false,'SG_Violet_Glow','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__Stone_SGDunVault']={-893.262,12.75,515.264,62.345,13.5,123.061,13,true,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__Stone_SG_Castle_B']={-893.262,12.2,515.264,61.665,13.0,122.169,13,true,'Stone_SG_Castle_B','','SG_Dun'},
  ['SG_Dun_Rooms_Portals__Stone_SG_Trim']={-893.262,13.05,515.264,63.45,14.1,123.53,13,true,'Stone_SG_Trim','','SG_Dun'},
  ['SG_Dun_Rooms_Shell__Stone_SG_Castle']={-891.421,16.7,514.483,92.076,22.6,138.699,13,true,'Stone_SG_Castle','','SG_Dun'},
  ['SG_Dun_Rooms_Vault__Stone_SGDunVault']={-891.421,22.975,514.483,86.831,9.95,133.454,13,true,'Stone_SGDunVault','','SG_Dun'},
  ['SG_Dun_Rooms_Vault__Stone_SG_Trim']={-891.426,22.653,514.485,86.389,10.094,133.191,13,true,'Stone_SG_Trim','','SG_Dun'},
  ['SG_Ent_Bridge__Cliff_Rock_SG_Dark']={-593.265,-46.0,644.769,29.975,24.0,24.071,14,false,'Cliff_Rock_SG_Dark','','SG_Ent'},
  ['SG_Ent_Bridge__Stone_Paving_SG']={-594.876,28.035,644.085,37.235,0.37,27.592,14,false,'Stone_Paving_SG','','SG_Ent'},
  ['SG_Ent_Bridge__Stone_SG_Block_B']={-596.617,-3.075,642.084,42.75,61.85,37.357,14,false,'Stone_SG_Block_B','','SG_Ent'},
  ['SG_Ent_Bridge__Stone_SG_Floor']={-594.876,27.7,644.085,38.33,0.5,29.853,14,false,'Stone_SG_Floor','','SG_Ent'},
  ['SG_Ent_Bridge__Stone_SG_Obsidian']={-594.876,28.025,644.085,38.201,0.35,29.799,14,false,'Stone_SG_Obsidian','','SG_Ent'},
  ['SG_Ent_Bridge__Stone_SG_Trim']={-594.416,5.975,644.673,38.777,41.55,33.469,14,false,'Stone_SG_Trim','','SG_Ent'},
  ['SG_Ent_Parapets__Cloth_SG_Purple']={-592.887,38.445,644.929,8.72,8.0,20.153,14,false,'Cloth_SG_Purple','','SG_Ent'},
  ['SG_Ent_Parapets__Lantern_Glow']={-626.318,36.911,629.608,95.489,10.328,57.957,14,false,'Lantern_Glow','','SG_Ent'},
  ['SG_Ent_Parapets__Metal_Gold']={-626.318,37.423,629.608,95.99,11.845,58.459,14,true,'Metal_Gold','','SG_Ent'},
  ['SG_Ent_Parapets__Metal_SG_BlackIron']={-592.933,37.395,644.909,9.166,12.4,21.097,14,false,'Metal_SG_BlackIron','','SG_Ent'},
  ['SG_Ent_Parapets__Metal_SG_Silver']={-626.575,38.37,629.498,86.53,12.55,54.636,14,true,'Metal_SG_Silver','','SG_Ent'},
  ['SG_Ent_Parapets__SG_Rune_Glow']={-592.699,39.715,645.009,8.112,1.385,18.978,14,false,'SG_Rune_Glow','','SG_Ent'},
  ['SG_Ent_Parapets__Stone_SG_Castle']={-624.918,32.675,630.202,99.353,11.95,60.072,14,true,'Stone_SG_Castle','','SG_Ent'},
  ['SG_Ent_Parapets__Stone_SG_Castle_B']={-614.89,33.5,634.759,73.561,11.3,50.715,14,true,'Stone_SG_Castle_B','','SG_Ent'},
  ['SG_Ent_Parapets__Stone_SG_Obsidian']={-626.318,35.698,629.608,96.154,12.995,58.622,14,true,'Stone_SG_Obsidian','','SG_Ent'},
  ['SG_Ent_Parapets__Stone_SG_Trim']={-624.918,34.722,630.202,99.608,9.755,60.466,14,true,'Stone_SG_Trim','','SG_Ent'},
  ['SG_Ent_Porticos__Cloth_SG_Purple']={-637.899,49.65,625.579,46.755,23.0,39.353,14,true,'Cloth_SG_Purple','','SG_Ent'},
  ['SG_Ent_Porticos__Lantern_Glow']={-636.91,36.15,626.131,46.645,9.3,37.797,14,false,'Lantern_Glow','','SG_Ent'},
  ['SG_Ent_Porticos__Metal_Gold']={-637.871,50.37,625.591,46.81,21.56,39.377,14,true,'Metal_Gold','','SG_Ent'},
  ['SG_Ent_Porticos__Metal_SG_Iron']={-637.569,46.37,625.559,48.665,30.14,40.297,14,true,'Metal_SG_Iron','','SG_Ent'},
  ['SG_Ent_Porticos__Metal_SG_Silver']={-638.675,55.15,625.559,49.269,43.3,40.641,14,true,'Metal_SG_Silver','','SG_Ent'},
  ['SG_Ent_Porticos__Roof_SG_Navy']={-640.281,63.3,624.561,49.869,24.0,40.81,14,true,'Roof_SG_Navy','','SG_Ent'},
  ['SG_Ent_Porticos__SG_Rune_Glow']={-637.678,52.512,625.734,46.083,18.288,38.028,14,false,'SG_Rune_Glow','','SG_Ent'},
  ['SG_Ent_Porticos__Stone_SG_Block_B']={-639.289,31.05,624.97,53.469,11.7,43.243,14,true,'Stone_SG_Block_B','','SG_Ent'},
  ['SG_Ent_Porticos__Stone_SG_Castle']={-639.573,47.25,624.54,52.615,36.1,42.098,14,true,'Stone_SG_Castle','','SG_Ent'},
  ['SG_Ent_Porticos__Stone_SG_Obsidian']={-638.883,52.838,625.587,48.805,18.624,39.387,14,true,'Stone_SG_Obsidian','','SG_Ent'},
  ['SG_Ent_Porticos__Stone_SG_Trim']={-639.334,48.9,624.925,53.904,40.0,43.678,14,true,'Stone_SG_Trim','','SG_Ent'},
  ['SG_Ent_Porticos__Stone_SG_Violet']={-658.391,59.84,617.126,10.01,0.24,18.889,14,false,'Stone_SG_Violet','','SG_Ent'},
  ['SG_Ent_Stair__Stone_SG_Block']={-638.365,32.55,625.626,22.272,7.34,22.887,14,false,'Stone_SG_Block','','SG_Ent'},
  ['SG_Ent_Stair__Stone_SG_Castle_B']={-639.06,32.2,625.331,23.74,8.0,23.661,14,false,'Stone_SG_Castle_B','','SG_Ent'},
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
  {'COL_GateDemonSlayer_001','Block',{-703.409,55.925,344.9},{0.921,0.0,0.391},{0.391,0.0,-0.921},{3.6,3.6,23.45},false},
  {'COL_GateDemonSlayer_002','Block',{-700.908,51.4,339.008},{0.921,0.0,0.391},{0.391,0.0,-0.921},{2.8,2.8,15.6},false},
  {'COL_GateDemonSlayer_003','Block',{-685.367,55.925,352.558},{0.921,0.0,0.391},{0.391,0.0,-0.921},{3.6,3.6,23.45},false},
  {'COL_GateDemonSlayer_004','Block',{-682.866,51.4,346.666},{0.921,0.0,0.391},{0.391,0.0,-0.921},{2.8,2.8,15.6},false},
  {'COL_GateDemonSlayer_005','Block',{-694.388,43.975,348.729},{0.921,0.0,0.391},{0.391,0.0,-0.921},{22.0,10.0,0.75},false},
  {'COL_GateDemonSlayer_006','Block',{-709.161,44.2,346.423},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.0,13.1,1.2},false},
  {'COL_GateDemonSlayer_007','Block',{-710.124,45.05,347.155},{0.921,0.0,0.391},{0.391,0.0,-0.921},{5.2,5.2,0.5},false},
  {'COL_GateDemonSlayer_008','Block',{-710.124,49.7,347.155},{0.921,0.0,0.391},{0.391,0.0,-0.921},{4.0,4.0,9.8},false},
  {'COL_GateDemonSlayer_009','Block',{-709.123,48.05,351.708},{0.921,0.0,0.391},{0.391,0.0,-0.921},{2.0,2.0,6.5},false},
  {'COL_GateDemonSlayer_010','Block',{-682.466,44.2,357.754},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.0,13.1,1.2},false},
  {'COL_GateDemonSlayer_011','Block',{-682.324,45.05,358.955},{0.921,0.0,0.391},{0.391,0.0,-0.921},{5.2,5.2,0.5},false},
  {'COL_GateDemonSlayer_012','Block',{-682.324,49.7,358.955},{0.921,0.0,0.391},{0.391,0.0,-0.921},{4.0,4.0,9.8},false},
  {'COL_GateDemonSlayer_013','Block',{-686.294,48.05,361.398},{0.921,0.0,0.391},{0.391,0.0,-0.921},{2.0,2.0,6.5},false},
  {'COL_SGAnchorGuard_001','Block',{-683.214,48.2,322.402},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,20.0,9.0},false},
  {'COL_SG_Arrival_001','Block',{-594.876,27.2,644.085},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{38.0,18.0,2.0},false},
  {'COL_SG_Arrival_002','Block',{-591.125,29.95,635.248},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{34.0,1.2,4.5},false},
  {'COL_SG_Arrival_003','Block',{-598.627,29.95,652.922},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{34.0,1.2,4.5},false},
  {'COL_SG_CasButtress_001','Block',{-885.678,61.95,572.475},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_002','Block',{-848.405,61.95,484.658},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_003','Block',{-902.861,61.95,565.182},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_004','Block',{-865.588,61.95,477.364},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_005','Block',{-920.044,61.95,557.888},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_006','Block',{-882.771,61.95,470.071},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_007','Block',{-937.227,61.95,550.595},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_008','Block',{-899.954,61.95,462.778},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_009','Block',{-954.41,61.95,543.302},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasButtress_010','Block',{-917.137,61.95,455.485},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.4,3.2,20.5},false},
  {'COL_SG_CasCrown_001','Block',{-966.56,61.7,473.533},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{3.2,3.0,20.0},false},
  {'COL_SG_CasCrown_002','Block',{-975.762,61.7,495.214},{-0.927,0.0,0.375},{0.375,0.0,0.927},{3.2,3.0,20.0},false},
  {'COL_SG_CasCrown_003','Block',{-954.081,61.7,504.417},{0.375,0.0,0.927},{0.927,0.0,-0.375},{3.2,3.0,20.0},false},
  {'COL_SG_CasCrown_004','Block',{-944.878,61.7,482.735},{0.927,0.0,-0.375},{-0.375,0.0,-0.927},{3.2,3.0,20.0},false},
  {'COL_SG_CasCrown_005','Block',{-960.32,114.85,488.975},{-0.122,0.0,-0.993},{-0.993,0.0,0.122},{30.91,8.332,126.3},false},
  {'COL_SG_CasCrown_006','Block',{-960.32,114.85,488.975},{-0.602,0.0,-0.799},{-0.799,0.0,0.602},{30.91,8.332,126.3},false},
  {'COL_SG_CasCrown_007','Block',{-960.32,114.85,488.975},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{30.91,8.332,126.3},false},
  {'COL_SG_CasCrown_008','Block',{-960.32,114.85,488.975},{-0.993,0.0,0.122},{0.122,0.0,0.993},{30.91,8.332,126.3},false},
  {'COL_SG_CasCrown_009','Block',{-960.32,114.85,488.975},{-0.799,0.0,0.602},{0.602,0.0,0.799},{30.91,8.332,126.3},false},
  {'COL_SG_CasCrown_010','Block',{-960.32,114.85,488.975},{-0.391,0.0,0.921},{0.921,0.0,0.391},{30.91,8.332,126.3},false},
  {'COL_SG_CasCurtain_001','Block',{-866.263,56.95,616.563},{-0.904,0.0,-0.428},{-0.428,0.0,0.904},{52.441,3.4,10.5},false},
  {'COL_SG_CasCurtain_002','Block',{-894.927,56.95,593.061},{-0.423,0.0,-0.906},{-0.906,0.0,0.423},{30.307,3.4,10.5},false},
  {'COL_SG_CasFacTurret_001','Block',{-864.345,61.7,553.61},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{6.4,6.4,20.0},false},
  {'COL_SG_CasFacTurret_002','Block',{-847.154,61.7,513.107},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{6.4,6.4,20.0},false},
  {'COL_SG_CasHallCeil_001','Block',{-901.407,81.2,513.98},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{92.0,96.0,2.0},true},
  {'COL_SG_CasHall_001','Block',{-869.613,69.95,556.806},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{38.0,4.0,36.5},true},
  {'COL_SG_CasHall_002','Block',{-859.064,78.95,531.952},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{16.0,4.0,18.5},true},
  {'COL_SG_CasHall_003','Block',{-848.515,69.95,507.098},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{38.0,4.0,36.5},true},
  {'COL_SG_CasHall_004','Block',{-943.751,69.95,496.007},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{92.0,4.0,36.5},true},
  {'COL_SG_CasHall_005','Block',{-918.598,69.95,554.482},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.0,88.0,36.5},true},
  {'COL_SG_CasHall_006','Block',{-884.216,69.95,473.477},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.0,88.0,36.5},true},
  {'COL_SG_CasPorch_001','Block',{-860.02,64.45,543.931},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.4,3.6,25.5},false},
  {'COL_SG_CasPorch_002','Block',{-851.112,64.45,522.943},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.4,3.6,25.5},false},
  {'COL_SG_CasTower_001','Block',{-820.349,65.95,563.593},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_002','Block',{-820.349,65.95,563.593},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_003','Block',{-820.349,65.95,563.593},{-0.927,0.0,0.375},{0.375,0.0,0.927},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_004','Block',{-820.349,65.95,563.593},{-0.391,0.0,0.921},{0.921,0.0,0.391},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_005','Block',{-809.409,65.95,537.819},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_006','Block',{-809.409,65.95,537.819},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_007','Block',{-809.409,65.95,537.819},{-0.927,0.0,0.375},{0.375,0.0,0.927},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_008','Block',{-809.409,65.95,537.819},{-0.391,0.0,0.921},{0.921,0.0,0.391},{11.88,4.971,44.5},false},
  {'COL_SG_CasTower_009','Block',{-774.603,56.95,456.327},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_010','Block',{-774.603,56.95,456.327},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_011','Block',{-774.603,56.95,456.327},{-0.927,0.0,0.375},{0.375,0.0,0.927},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_012','Block',{-774.603,56.95,456.327},{-0.391,0.0,0.921},{0.921,0.0,0.391},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_013','Block',{-767.269,56.95,439.047},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_014','Block',{-767.269,56.95,439.047},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_015','Block',{-767.269,56.95,439.047},{-0.927,0.0,0.375},{0.375,0.0,0.927},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_016','Block',{-767.269,56.95,439.047},{-0.391,0.0,0.921},{0.921,0.0,0.391},{6.652,2.805,26.5},false},
  {'COL_SG_CasTower_017','Block',{-846.147,57.95,624.886},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{12.01,5.025,28.5},false},
  {'COL_SG_CasTower_018','Block',{-846.147,57.95,624.886},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{12.01,5.025,28.5},false},
  {'COL_SG_CasTower_019','Block',{-846.147,57.95,624.886},{-0.927,0.0,0.375},{0.375,0.0,0.927},{12.01,5.025,28.5},false},
  {'COL_SG_CasTower_020','Block',{-846.147,57.95,624.886},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.01,5.025,28.5},false},
  {'COL_SG_CasTower_021','Block',{-832.851,58.45,593.05},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_022','Block',{-832.851,58.45,593.05},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_023','Block',{-832.851,58.45,593.05},{-0.927,0.0,0.375},{0.375,0.0,0.927},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_024','Block',{-832.851,58.45,593.05},{-0.391,0.0,0.921},{0.921,0.0,0.391},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_025','Block',{-790.655,58.45,493.634},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_026','Block',{-790.655,58.45,493.634},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_027','Block',{-790.655,58.45,493.634},{-0.927,0.0,0.375},{0.375,0.0,0.927},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_028','Block',{-790.655,58.45,493.634},{-0.391,0.0,0.921},{0.921,0.0,0.391},{8.5,3.571,29.5},false},
  {'COL_SG_CasTower_029','Block',{-867.168,63.95,617.593},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{10.163,4.26,24.5},false},
  {'COL_SG_CasTower_030','Block',{-867.168,63.95,617.593},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{10.163,4.26,24.5},false},
  {'COL_SG_CasTower_031','Block',{-867.168,63.95,617.593},{-0.927,0.0,0.375},{0.375,0.0,0.927},{10.163,4.26,24.5},false},
  {'COL_SG_CasTower_032','Block',{-867.168,63.95,617.593},{-0.391,0.0,0.921},{0.921,0.0,0.391},{10.163,4.26,24.5},false},
  {'COL_SG_CasTower_033','Block',{-880.162,87.85,581.66},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_034','Block',{-880.162,87.85,581.66},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_035','Block',{-880.162,87.85,581.66},{-0.927,0.0,0.375},{0.375,0.0,0.927},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_036','Block',{-880.162,87.85,581.66},{-0.391,0.0,0.921},{0.921,0.0,0.391},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_037','Block',{-837.966,87.85,482.244},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_038','Block',{-837.966,87.85,482.244},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_039','Block',{-837.966,87.85,482.244},{-0.927,0.0,0.375},{0.375,0.0,0.927},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_040','Block',{-837.966,87.85,482.244},{-0.391,0.0,0.921},{0.921,0.0,0.391},{18.478,7.704,72.3},false},
  {'COL_SG_CasTower_041','Block',{-966.187,69.95,538.629},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{9.239,3.877,36.5},false},
  {'COL_SG_CasTower_042','Block',{-966.187,69.95,538.629},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{9.239,3.877,36.5},false},
  {'COL_SG_CasTower_043','Block',{-966.187,69.95,538.629},{-0.927,0.0,0.375},{0.375,0.0,0.927},{9.239,3.877,36.5},false},
  {'COL_SG_CasTower_044','Block',{-966.187,69.95,538.629},{-0.391,0.0,0.921},{0.921,0.0,0.391},{9.239,3.877,36.5},false},
  {'COL_SG_CasTower_046','Block',{-928.679,69.95,450.26},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{9.239,3.877,36.5},false},
  {'COL_SG_CasTower_047','Block',{-928.679,69.95,450.26},{-0.927,0.0,0.375},{0.375,0.0,0.927},{9.239,3.877,36.5},false},
  {'COL_SG_CasTower_048','Block',{-928.679,69.95,450.26},{-0.391,0.0,0.921},{0.921,0.0,0.391},{9.239,3.877,36.5},false},
  {'COL_SG_CasWall_001','Block',{-832.07,57.95,591.209},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{72.0,6.0,12.5},true},
  {'COL_SG_CasWall_002','Block',{-792.609,57.95,498.237},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{98.0,6.0,12.5},true},
  {'COL_SG_CasWall_003','Block',{-767.213,57.95,438.403},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{8.0,6.0,12.5},true},
  {'COL_SG_CasWall_004','Block',{-814.787,72.0,550.745},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{16.0,9.0,3.6},true},
  {'COL_SG_CasWingE_001','Block',{-884.382,58.95,463.63},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{14.0,84.0,14.5},false},
  {'COL_SG_CasWingTower_001','Block',{-917.353,81.85,610.415},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{12.01,5.025,60.3},false},
  {'COL_SG_CasWingTower_002','Block',{-917.353,81.85,610.415},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{12.01,5.025,60.3},false},
  {'COL_SG_CasWingTower_003','Block',{-917.353,81.85,610.415},{-0.927,0.0,0.375},{0.375,0.0,0.927},{12.01,5.025,60.3},false},
  {'COL_SG_CasWingTower_004','Block',{-917.353,81.85,610.415},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.01,5.025,60.3},false},
  {'COL_SG_CasWingTower_005','Block',{-979.948,76.85,583.847},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{11.087,4.642,50.3},false},
  {'COL_SG_CasWingTower_006','Block',{-979.948,76.85,583.847},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{11.087,4.642,50.3},false},
  {'COL_SG_CasWingTower_007','Block',{-979.948,76.85,583.847},{-0.927,0.0,0.375},{0.375,0.0,0.927},{11.087,4.642,50.3},false},
  {'COL_SG_CasWingTower_008','Block',{-979.948,76.85,583.847},{-0.391,0.0,0.921},{0.921,0.0,0.391},{11.087,4.642,50.3},false},
  {'COL_SG_CasWingTower_009','Block',{-973.22,82.85,555.198},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{12.01,5.025,62.3},false},
  {'COL_SG_CasWingTower_010','Block',{-973.22,82.85,555.198},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{12.01,5.025,62.3},false},
  {'COL_SG_CasWingTower_011','Block',{-973.22,82.85,555.198},{-0.927,0.0,0.375},{0.375,0.0,0.927},{12.01,5.025,62.3},false},
  {'COL_SG_CasWingTower_012','Block',{-973.22,82.85,555.198},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.01,5.025,62.3},false},
  {'COL_SG_CasWingTower_013','Block',{-927.785,78.85,443.035},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{12.01,5.025,54.3},false},
  {'COL_SG_CasWingTower_014','Block',{-927.785,78.85,443.035},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{12.01,5.025,54.3},false},
  {'COL_SG_CasWingTower_015','Block',{-927.785,78.85,443.035},{-0.927,0.0,0.375},{0.375,0.0,0.927},{12.01,5.025,54.3},false},
  {'COL_SG_CasWingTower_016','Block',{-927.785,78.85,443.035},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.01,5.025,54.3},false},
  {'COL_SG_CasWingW_001','Block',{-942.008,68.95,581.482},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{32.0,68.0,34.5},false},
  {'COL_SG_CraftBench_001','Block',{-725.514,45.45,478.372},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.7,2.6,3.5},false},
  {'COL_SG_CraftButtress_001','Block',{-723.61,49.05,473.884},{0.921,0.0,0.391},{0.391,0.0,-0.921},{1.9,1.95,10.7},false},
  {'COL_SG_CraftButtress_002','Block',{-736.142,49.05,473.775},{0.927,0.0,-0.375},{-0.375,0.0,-0.927},{1.9,1.95,10.7},false},
  {'COL_SG_CraftButtress_003','Block',{-745.081,49.05,482.56},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.95,10.7},false},
  {'COL_SG_CraftButtress_004','Block',{-745.19,49.05,495.093},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{1.9,1.95,10.7},false},
  {'COL_SG_CraftButtress_005','Block',{-723.873,49.05,504.14},{-0.927,0.0,0.375},{0.375,0.0,0.927},{1.9,1.95,10.7},false},
  {'COL_SG_CraftButtress_006','Block',{-714.934,49.05,495.356},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.9,1.95,10.7},false},
  {'COL_SG_CraftButtress_007','Block',{-714.825,49.05,482.823},{0.375,0.0,0.927},{0.927,0.0,-0.375},{1.9,1.95,10.7},false},
  {'COL_SG_CraftCauldron_001','Block',{-730.008,48.0,488.958},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{6.467,2.729,5.0},false},
  {'COL_SG_CraftCauldron_002','Block',{-730.008,48.0,488.958},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{6.467,2.729,5.0},false},
  {'COL_SG_CraftCauldron_003','Block',{-730.008,48.0,488.958},{-0.927,0.0,0.375},{0.375,0.0,0.927},{6.467,2.729,5.0},false},
  {'COL_SG_CraftCauldron_004','Block',{-730.008,48.0,488.958},{-0.391,0.0,0.921},{0.921,0.0,0.391},{6.467,2.729,5.0},false},
  {'COL_SG_CraftChest_001','Block',{-740.188,44.7,494.115},{-0.492,0.0,-0.87},{-0.87,0.0,0.492},{3.25,1.5,2.0},false},
  {'COL_SG_CraftDais_001','Block',{-730.008,44.4,488.958},{0.087,0.0,-0.996},{-0.996,0.0,-0.087},{12.269,4.036,1.0},false},
  {'COL_SG_CraftDais_002','Block',{-730.008,44.4,488.958},{-0.515,0.0,-0.857},{-0.857,0.0,0.515},{12.269,4.036,1.0},false},
  {'COL_SG_CraftDais_003','Block',{-730.008,44.4,488.958},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{12.269,4.036,1.0},false},
  {'COL_SG_CraftDais_004','Block',{-730.008,44.4,488.958},{-0.974,0.0,0.225},{0.225,0.0,0.974},{12.269,4.036,1.0},false},
  {'COL_SG_CraftDais_005','Block',{-730.008,44.4,488.958},{-0.656,0.0,0.755},{0.755,0.0,0.656},{12.269,4.036,1.0},false},
  {'COL_SG_CraftDais_006','Block',{-730.008,45.25,488.958},{0.087,0.0,-0.996},{-0.996,0.0,-0.087},{9.606,3.171,0.7},false},
  {'COL_SG_CraftDais_007','Block',{-730.008,45.25,488.958},{-0.515,0.0,-0.857},{-0.857,0.0,0.515},{9.606,3.171,0.7},false},
  {'COL_SG_CraftDais_008','Block',{-730.008,45.25,488.958},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{9.606,3.171,0.7},false},
  {'COL_SG_CraftDais_009','Block',{-730.008,45.25,488.958},{-0.974,0.0,0.225},{0.225,0.0,0.974},{9.606,3.171,0.7},false},
  {'COL_SG_CraftDais_010','Block',{-730.008,45.25,488.958},{-0.656,0.0,0.755},{0.755,0.0,0.656},{9.606,3.171,0.7},false},
  {'COL_SG_CraftLanternPost_001','Block',{-731.462,47.6,508.764},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.2,1.2,7.2},false},
  {'COL_SG_CraftLanternPost_002','Block',{-743.244,47.6,503.763},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.2,1.2,7.2},false},
  {'COL_SG_CraftLanternPost_003','Block',{-736.436,46.85,493.803},{-0.799,0.0,0.602},{0.602,0.0,0.799},{1.0,1.0,5.6},false},
  {'COL_SG_CraftLanternPost_004','Block',{-729.026,46.85,496.948},{0.122,0.0,0.993},{0.993,0.0,-0.122},{1.0,1.0,5.6},false},
  {'COL_SG_CraftLectern_001','Block',{-727.253,45.75,499.607},{-0.968,0.0,0.25},{0.25,0.0,0.968},{1.7,1.5,4.1},false},
  {'COL_SG_CraftPortal_001','Block',{-729.877,52.95,504.711},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{4.55,5.3,18.5},false},
  {'COL_SG_CraftPortal_002','Block',{-733.26,54.762,503.275},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{1.2,5.3,0.877},false},
  {'COL_SG_CraftPortal_003','Block',{-732.339,54.146,503.666},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.8,5.3,2.109},false},
  {'COL_SG_CraftPortal_004','Block',{-741.43,52.95,499.808},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{4.55,5.3,18.5},false},
  {'COL_SG_CraftPortal_005','Block',{-738.047,54.762,501.244},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{1.2,5.3,0.877},false},
  {'COL_SG_CraftPortal_006','Block',{-738.967,54.146,500.853},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.8,5.3,2.109},false},
  {'COL_SG_CraftPortal_007','Block',{-735.653,58.7,502.259},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{8.0,5.3,7.0},false},
  {'COL_SG_CraftRoof_001','Block',{-730.008,63.2,488.958},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{30.303,12.602,2.0},true},
  {'COL_SG_CraftRoof_002','Block',{-730.008,63.2,488.958},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{30.303,12.602,2.0},true},
  {'COL_SG_CraftRoof_003','Block',{-730.008,63.2,488.958},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{30.303,12.602,2.0},true},
  {'COL_SG_CraftRoof_004','Block',{-730.008,63.2,488.958},{-0.713,0.0,0.701},{0.701,0.0,0.713},{30.303,12.602,2.0},true},
  {'COL_SG_CraftShelf_001','Block',{-738.885,48.52,479.925},{0.713,0.0,-0.701},{-0.701,0.0,-0.713},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_002','Block',{-740.921,48.52,482.53},{0.508,0.0,-0.862},{-0.862,0.0,-0.508},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_003','Block',{-742.212,48.52,485.574},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_004','Block',{-742.672,48.52,488.848},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_005','Block',{-721.13,48.52,497.991},{-0.713,0.0,0.701},{0.701,0.0,0.713},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_006','Block',{-719.095,48.52,495.386},{-0.508,0.0,0.862},{0.862,0.0,0.508},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_007','Block',{-717.803,48.52,492.342},{-0.267,0.0,0.964},{0.964,0.0,0.267},{3.458,1.34,9.64},false},
  {'COL_SG_CraftShelf_008','Block',{-717.343,48.52,489.068},{-0.009,0.0,1.0},{1.0,0.0,0.009},{3.458,1.34,9.64},false},
  {'COL_SG_CraftTable_001','Block',{-732.662,45.34,478.696},{0.968,0.0,-0.25},{-0.25,0.0,-0.968},{4.0,2.3,3.28},false},
  {'COL_SG_CraftTable_002','Block',{-720.782,45.34,483.738},{0.492,0.0,0.87},{0.87,0.0,-0.492},{4.0,2.3,3.28},false},
  {'COL_SG_CraftWall_001','Block',{-726.377,52.95,502.996},{0.25,0.0,0.968},{0.968,0.0,-0.25},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_002','Block',{-722.867,52.95,501.578},{0.492,0.0,0.87},{0.87,0.0,-0.492},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_003','Block',{-719.844,52.95,499.3},{0.701,0.0,0.713},{0.713,0.0,-0.701},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_004','Block',{-717.514,52.95,496.317},{0.862,0.0,0.508},{0.508,0.0,-0.862},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_005','Block',{-716.035,52.95,492.833},{0.964,0.0,0.267},{0.267,0.0,-0.964},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_006','Block',{-715.508,52.95,489.084},{1.0,0.0,0.009},{0.009,0.0,-1.0},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_007','Block',{-715.969,52.95,485.327},{0.968,0.0,-0.25},{-0.25,0.0,-0.968},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_008','Block',{-717.388,52.95,481.817},{0.87,0.0,-0.492},{-0.492,0.0,-0.87},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_009','Block',{-719.666,52.95,478.794},{0.713,0.0,-0.701},{-0.701,0.0,-0.713},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_010','Block',{-722.649,52.95,476.464},{0.508,0.0,-0.862},{-0.862,0.0,-0.508},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_011','Block',{-726.133,52.95,474.985},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_012','Block',{-729.881,52.95,474.458},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_013','Block',{-733.638,52.95,474.92},{-0.25,0.0,-0.968},{-0.968,0.0,0.25},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_014','Block',{-737.148,52.95,476.338},{-0.492,0.0,-0.87},{-0.87,0.0,0.492},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_015','Block',{-740.171,52.95,478.616},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_016','Block',{-742.501,52.95,481.599},{-0.862,0.0,-0.508},{-0.508,0.0,0.862},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_017','Block',{-743.98,52.95,485.083},{-0.964,0.0,-0.267},{-0.267,0.0,0.964},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_018','Block',{-744.507,52.95,488.832},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_019','Block',{-744.046,52.95,492.589},{-0.968,0.0,0.25},{0.25,0.0,0.968},{2.2,4.172,18.5},true},
  {'COL_SG_CraftWall_020','Block',{-742.628,52.95,496.098},{-0.87,0.0,0.492},{0.492,0.0,0.87},{2.2,4.172,18.5},true},
  {'COL_SG_DunApproach_001','Block',{-838.752,64.05,448.777},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.2,4.2,24.3},false},
  {'COL_SG_DunApproach_002','Block',{-826.64,64.05,420.241},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.2,4.2,24.3},false},
  {'COL_SG_DunApproach_003','Block',{-834.126,54.65,446.069},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,5.5},false},
  {'COL_SG_DunApproach_004','Block',{-825.375,54.65,425.449},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,5.5},false},
  {'COL_SG_DunApproach_005','Block',{-805.963,54.65,452.917},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,5.5},false},
  {'COL_SG_DunApproach_006','Block',{-800.884,54.65,440.95},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,5.5},false},
  {'COL_SG_DunApproach_007','Block',{-829.87,55.45,450.374},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,7.1},false},
  {'COL_SG_DunApproach_008','Block',{-819.321,55.45,425.52},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,7.1},false},
  {'COL_SG_DunApproach_009','Block',{-825.589,55.45,454.364},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,7.1},false},
  {'COL_SG_DunApproach_010','Block',{-813.477,55.45,425.828},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,7.1},false},
  {'COL_SG_DunHouse_001','Block',{-841.203,70.55,442.522},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.6,3.0,37.7},true},
  {'COL_SG_DunHouse_002','Block',{-832.842,70.55,422.823},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.6,3.0,37.7},true},
  {'COL_SG_DunHouse_003','Block',{-837.023,81.7,432.673},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{16.8,3.0,15.4},true},
  {'COL_SG_DunHouse_004','Block',{-858.194,70.55,423.686},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{26.0,3.0,37.7},true},
  {'COL_SG_DunHouse_005','Block',{-852.102,70.55,438.765},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.0,20.0,37.7},true},
  {'COL_SG_DunHouse_006','Block',{-843.115,70.55,417.594},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.0,20.0,37.7},true},
  {'COL_SG_DunHouse_007','Block',{-847.609,75.2,428.18},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{20.0,20.0,2.0},true},
  {'COL_SG_DunHouse_008','Block',{-849.081,52.15,427.554},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{15.6,2.0,0.9},true},
  {'COL_SG_DunHouse_009','Block',{-853.408,52.35,425.718},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{20.0,7.4,1.3},true},
  {'COL_SG_DunHouse_010','Block',{-856.324,54.95,432.845},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.6,2.6,5.5},true},
  {'COL_SG_DunHouse_011','Block',{-850.307,54.95,418.669},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.6,2.6,5.5},true},
  {'COL_SG_DunHouse_012','Block',{-845.142,58.95,439.004},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,7.0,14.5},true},
  {'COL_SG_DunHouse_013','Block',{-838.109,58.95,422.435},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,7.0,14.5},true},
  {'COL_SG_DunHouse_014','Block',{-854.288,58.95,434.959},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.3,13.0,14.5},true},
  {'COL_SG_DunHouse_015','Block',{-847.373,58.95,418.665},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.3,13.0,14.5},true},
  {'COL_SG_DunKit_001','Block',{-902.413,11.75,579.44},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_002','Block',{-889.403,11.75,548.787},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_003','Block',{-933.066,11.75,566.429},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_004','Block',{-920.056,11.75,535.776},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_005','Block',{-897.838,11.75,569.812},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_006','Block',{-893.149,11.75,558.766},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_007','Block',{-929.319,11.75,556.45},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_008','Block',{-924.631,11.75,545.404},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_009','Block',{-909.171,11.75,577.061},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_010','Block',{-926.66,11.75,569.637},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_011','Block',{-897.373,11.75,544.915},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_012','Block',{-911.733,11.75,538.82},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_013','Block',{-883.884,11.75,546.023},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_014','Block',{-867.748,11.75,508.006},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_015','Block',{-921.901,11.75,529.887},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_016','Block',{-905.765,11.75,491.87},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_017','Block',{-879.7,11.75,537.316},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_018','Block',{-871.104,11.75,517.065},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_019','Block',{-918.545,11.75,520.828},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_020','Block',{-909.95,11.75,500.577},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_021','Block',{-895.889,11.75,541.417},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_022','Block',{-910.249,11.75,535.322},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_023','Block',{-879.401,11.75,502.571},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_024','Block',{-893.761,11.75,496.476},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_025','Block',{-865.912,11.75,503.679},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_026','Block',{-849.775,11.75,465.662},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_027','Block',{-903.929,11.75,487.543},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_028','Block',{-887.793,11.75,449.526},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.7,2.7,12.5},false},
  {'COL_SG_DunKit_029','Block',{-861.727,11.75,494.972},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_030','Block',{-857.429,11.75,484.847},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_031','Block',{-853.132,11.75,474.721},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_032','Block',{-900.573,11.75,478.485},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_033','Block',{-896.275,11.75,468.359},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_034','Block',{-891.977,11.75,458.233},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,1.8,12.5},false},
  {'COL_SG_DunKit_035','Block',{-877.916,11.75,499.073},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_036','Block',{-892.276,11.75,492.978},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_037','Block',{-859.863,11.75,460.892},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunKit_038','Block',{-877.353,11.75,453.468},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,3.6,12.5},false},
  {'COL_SG_DunMouth_001','Block',{-838.207,58.2,444.934},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.3,5.0,13.0},false},
  {'COL_SG_DunMouth_002','Block',{-829.026,58.2,423.302},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.3,5.0,13.0},false},
  {'COL_SG_DunPortal_001','Block',{-855.801,59.8,424.702},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{14.0,2.2,13.6},false},
  {'COL_SG_DunPortal_002','Block',{-917.925,11.95,573.372},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.75,13.0,12.9},false},
  {'COL_SG_DunPortal_003','Block',{-868.599,11.95,457.157},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.75,13.0,12.9},false},
  {'COL_SG_DunRock_001','Block',{-847.502,65.95,441.75},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.5,14.8,28.5},false},
  {'COL_SG_DunRock_002','Block',{-866.758,65.95,436.184},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{9.3,25.0,28.5},false},
  {'COL_SG_DunRock_003','Block',{-837.773,66.95,418.829},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.5,14.8,30.5},false},
  {'COL_SG_DunRock_004','Block',{-853.647,66.95,407.855},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{12.3,23.0,30.5},false},
  {'COL_SG_DunRock_005','Block',{-866.433,68.45,420.19},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{20.4,18.1,33.5},false},
  {'COL_SG_DunRoom_001','Block',{-903.811,23.0,540.118},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,12.0,10.0},true},
  {'COL_SG_DunRoom_002','Block',{-885.838,23.0,497.775},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,12.0,10.0},true},
  {'COL_SG_DunRoom_003','Block',{-918.658,16.7,575.098},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,40.0,22.6},true},
  {'COL_SG_DunRoom_004','Block',{-929.115,16.7,551.105},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{38.0,2.0,22.6},true},
  {'COL_SG_DunRoom_005','Block',{-894.135,16.7,565.952},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{38.0,2.0,22.6},true},
  {'COL_SG_DunRoom_006','Block',{-915.997,16.7,509.96},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{44.0,2.0,22.6},true},
  {'COL_SG_DunRoom_007','Block',{-873.653,16.7,527.933},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{44.0,2.0,22.6},true},
  {'COL_SG_DunRoom_008','Block',{-897.633,16.7,466.696},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{46.0,2.0,22.6},true},
  {'COL_SG_DunRoom_009','Block',{-855.29,16.7,484.668},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{46.0,2.0,22.6},true},
  {'COL_SG_DunRoom_010','Block',{-867.866,16.7,455.431},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,48.0,22.6},true},
  {'COL_SG_DunRoom_011','Block',{-890.003,16.7,545.979},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,18.0,22.6},true},
  {'COL_SG_DunRoom_012','Block',{-917.619,16.7,534.258},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,18.0,22.6},true},
  {'COL_SG_DunRoom_013','Block',{-872.031,16.7,503.635},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,18.0,22.6},true},
  {'COL_SG_DunRoom_014','Block',{-899.646,16.7,491.914},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.0,18.0,22.6},true},
  {'COL_SG_DunRoom_015','Block',{-893.262,5.0,515.264},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{132.0,48.0,2.0},true},
  {'COL_SG_DunRoom_016','Block',{-893.262,28.75,515.264},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{132.0,48.0,1.5},true},
  {'COL_SG_EntPortico_001','Block',{-625.986,38.7,643.156},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.8,3.8,21.0},false},
  {'COL_SG_EntPortico_002','Block',{-624.973,30.8,643.586},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.0,6.2,5.2},false},
  {'COL_SG_EntPortico_003','Block',{-617.156,38.7,622.353},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.8,3.8,21.0},false},
  {'COL_SG_EntPortico_004','Block',{-616.143,30.8,622.782},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.0,6.2,5.2},false},
  {'COL_SG_EntPortico_005','Block',{-662.924,49.7,627.804},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.6,4.6,27.0},false},
  {'COL_SG_EntPortico_006','Block',{-661.911,38.8,628.234},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.8,7.0,5.2},false},
  {'COL_SG_EntPortico_007','Block',{-653.859,49.7,606.448},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.6,4.6,27.0},false},
  {'COL_SG_EntPortico_008','Block',{-652.847,38.8,606.878},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.8,7.0,5.2},false},
  {'COL_SG_ExitBridge_001','Block',{-711.579,43.2,389.231},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{68.0,18.0,2.0},false},
  {'COL_SG_ExitBridge_002','Block',{-702.742,45.95,392.982},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{64.0,1.2,4.5},false},
  {'COL_SG_ExitBridge_003','Block',{-720.416,45.95,385.481},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{64.0,1.2,4.5},false},
  {'COL_SG_ExitHead_001','Block',{-714.09,51.25,425.862},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.2,4.2,14.1},false},
  {'COL_SG_ExitHead_002','Block',{-736.183,51.25,416.485},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.2,4.2,14.1},false},
  {'COL_SG_Fountain_001','Block',{-702.576,37.0,598.372},{0.139,0.0,-0.99},{-0.99,0.0,-0.139},{13.523,3.673,3.6},false},
  {'COL_SG_Fountain_002','Block',{-702.576,37.0,598.372},{-0.375,0.0,-0.927},{-0.927,0.0,0.375},{13.523,3.673,3.6},false},
  {'COL_SG_Fountain_003','Block',{-702.576,37.0,598.372},{-0.788,0.0,-0.616},{-0.616,0.0,0.788},{13.523,3.673,3.6},false},
  {'COL_SG_Fountain_004','Block',{-702.576,37.0,598.372},{-0.99,0.0,-0.139},{-0.139,0.0,0.99},{13.523,3.673,3.6},false},
  {'COL_SG_Fountain_005','Block',{-702.576,37.0,598.372},{-0.927,0.0,0.375},{0.375,0.0,0.927},{13.523,3.673,3.6},false},
  {'COL_SG_Fountain_006','Block',{-702.576,37.0,598.372},{-0.616,0.0,0.788},{0.788,0.0,0.616},{13.523,3.673,3.6},false},
  {'COL_SG_Guard_001','Block',{-828.653,53.55,592.116},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{71.8,1.0,3.7},false},
  {'COL_SG_Guard_009','Block',{-789.387,53.55,499.604},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{96.799,1.0,3.7},false},
  {'COL_SG_Guard_019','Block',{-764.186,53.55,440.231},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{7.8,1.0,3.7},false},
  {'COL_SG_Guard_020','Block',{-783.983,53.55,424.27},{-0.886,0.0,-0.464},{-0.464,0.0,0.886},{48.96,1.0,3.7},false},
  {'COL_SG_Guard_025','Block',{-833.671,53.55,404.168},{-0.956,0.0,-0.294},{-0.294,0.0,0.956},{58.104,1.0,3.7},false},
  {'COL_SG_Guard_031','Block',{-870.984,53.55,405.625},{-0.644,0.0,0.765},{0.765,0.0,0.644},{26.995,1.0,3.7},false},
  {'COL_SG_Guard_034','Block',{-887.376,53.55,433.571},{-0.391,0.0,0.921},{0.921,0.0,0.391},{37.8,1.0,3.7},false},
  {'COL_SG_Guard_038','Block',{-926.893,53.55,439.581},{-0.941,0.0,-0.338},{-0.338,0.0,0.941},{69.913,1.0,3.7},false},
  {'COL_SG_Guard_045','Block',{-982.678,53.55,478.942},{-0.391,0.0,0.921},{0.921,0.0,0.391},{111.8,1.0,3.7},false},
  {'COL_SG_Guard_057','Block',{-952.349,53.55,555.892},{0.907,0.0,0.422},{0.422,0.0,-0.907},{115.868,1.0,3.7},false},
  {'COL_SG_Guard_077','Block',{-774.21,45.55,653.246},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{75.8,1.0,3.7},false},
  {'COL_SG_Guard_085','Block',{-752.916,45.55,603.078},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{32.8,1.0,3.7},false},
  {'COL_SG_Guard_089','Block',{-734.162,45.55,558.893},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{30.8,1.0,3.7},false},
  {'COL_SG_Guard_092','Block',{-712.869,45.55,508.725},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{77.8,1.0,3.7},false},
  {'COL_SG_Guard_100','Block',{-699.305,45.55,455.488},{-0.114,0.0,-0.993},{-0.993,0.0,0.114},{34.268,1.0,3.7},false},
  {'COL_SG_Guard_104','Block',{-705.803,45.55,431.183},{-0.563,0.0,-0.826},{-0.826,0.0,0.563},{16.403,1.0,3.7},false},
  {'COL_SG_Guard_106','Block',{-712.84,45.55,422.916},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{4.8,1.0,3.7},false},
  {'COL_SG_Guard_107','Block',{-734.472,45.55,413.734},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{3.8,1.0,3.7},false},
  {'COL_SG_Guard_108','Block',{-747.857,45.55,413.824},{-0.995,0.0,0.101},{0.101,0.0,0.995},{22.588,1.0,3.7},false},
  {'COL_SG_Guard_111','Block',{-763.849,45.55,424.079},{-0.391,0.0,0.921},{0.921,0.0,0.391},{19.8,1.0,3.7},false},
  {'COL_SG_Guard_113','Block',{-853.711,45.55,635.798},{-0.391,0.0,0.921},{0.921,0.0,0.391},{27.8,1.0,3.7},false},
  {'COL_SG_Guard_116','Block',{-845.407,45.55,661.932},{0.75,0.0,0.662},{0.662,0.0,-0.75},{37.722,1.0,3.7},false},
  {'COL_SG_Guard_120','Block',{-810.524,45.55,681.335},{0.953,0.0,0.304},{0.304,0.0,-0.953},{42.981,1.0,3.7},false},
  {'COL_SG_Guard_125','Block',{-765.076,41.55,703.301},{-0.997,0.0,-0.074},{-0.074,0.0,0.997},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_126','Block',{-768.012,41.55,703.181},{-0.998,0.0,0.057},{0.057,0.0,0.998},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_127','Block',{-770.939,41.55,703.446},{-0.982,0.0,0.187},{0.187,0.0,0.982},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_128','Block',{-773.806,41.55,704.09},{-0.95,0.0,0.313},{0.313,0.0,0.95},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_129','Block',{-776.564,41.55,705.103},{-0.901,0.0,0.434},{0.434,0.0,0.901},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_130','Block',{-779.167,41.55,706.468},{-0.836,0.0,0.548},{0.548,0.0,0.836},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_131','Block',{-781.569,41.55,708.16},{-0.758,0.0,0.653},{0.653,0.0,0.758},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_132','Block',{-783.729,41.55,710.151},{-0.666,0.0,0.746},{0.746,0.0,0.666},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_133','Block',{-785.612,41.55,712.408},{-0.563,0.0,0.827},{0.827,0.0,0.563},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_134','Block',{-787.183,41.55,714.891},{-0.45,0.0,0.893},{0.893,0.0,0.45},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_135','Block',{-788.417,41.55,717.558},{-0.33,0.0,0.944},{0.944,0.0,0.33},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_136','Block',{-789.293,41.55,720.363},{-0.204,0.0,0.979},{0.979,0.0,0.204},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_137','Block',{-789.795,41.55,723.258},{-0.074,0.0,0.997},{0.997,0.0,0.074},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_138','Block',{-789.914,41.55,726.194},{0.057,0.0,0.998},{0.998,0.0,-0.057},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_139','Block',{-789.65,41.55,729.121},{0.187,0.0,0.982},{0.982,0.0,-0.187},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_140','Block',{-789.005,41.55,731.987},{0.313,0.0,0.95},{0.95,0.0,-0.313},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_141','Block',{-787.992,41.55,734.746},{0.434,0.0,0.901},{0.901,0.0,-0.434},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_142','Block',{-786.628,41.55,737.348},{0.548,0.0,0.836},{0.836,0.0,-0.548},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_143','Block',{-784.936,41.55,739.75},{0.653,0.0,0.758},{0.758,0.0,-0.653},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_144','Block',{-782.944,41.55,741.911},{0.746,0.0,0.666},{0.666,0.0,-0.746},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_145','Block',{-780.688,41.55,743.794},{0.827,0.0,0.563},{0.563,0.0,-0.827},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_146','Block',{-778.205,41.55,745.365},{0.893,0.0,0.45},{0.45,0.0,-0.893},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_147','Block',{-775.538,41.55,746.599},{0.944,0.0,0.33},{0.33,0.0,-0.944},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_148','Block',{-772.733,41.55,747.475},{0.979,0.0,0.204},{0.204,0.0,-0.979},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_149','Block',{-769.838,41.55,747.977},{0.997,0.0,0.074},{0.074,0.0,-0.997},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_150','Block',{-766.902,41.55,748.096},{0.998,0.0,-0.057},{-0.057,0.0,-0.998},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_151','Block',{-763.975,41.55,747.832},{0.982,0.0,-0.187},{-0.187,0.0,-0.982},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_152','Block',{-761.108,41.55,747.187},{0.95,0.0,-0.313},{-0.313,0.0,-0.95},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_153','Block',{-758.35,41.55,746.174},{0.901,0.0,-0.434},{-0.434,0.0,-0.901},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_154','Block',{-755.747,41.55,744.81},{0.836,0.0,-0.548},{-0.548,0.0,-0.836},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_155','Block',{-753.345,41.55,743.117},{0.758,0.0,-0.653},{-0.653,0.0,-0.758},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_156','Block',{-751.184,41.55,741.126},{0.666,0.0,-0.746},{-0.746,0.0,-0.666},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_157','Block',{-749.302,41.55,738.87},{0.563,0.0,-0.827},{-0.827,0.0,-0.563},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_158','Block',{-747.73,41.55,736.387},{0.45,0.0,-0.893},{-0.893,0.0,-0.45},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_159','Block',{-746.496,41.55,733.72},{0.33,0.0,-0.944},{-0.944,0.0,-0.33},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_160','Block',{-745.621,41.55,730.915},{0.204,0.0,-0.979},{-0.979,0.0,-0.204},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_161','Block',{-745.119,41.55,728.02},{0.074,0.0,-0.997},{-0.997,0.0,-0.074},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_162','Block',{-744.999,41.55,725.083},{-0.057,0.0,-0.998},{-0.998,0.0,0.057},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_163','Block',{-745.264,41.55,722.157},{-0.187,0.0,-0.982},{-0.982,0.0,0.187},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_164','Block',{-745.908,41.55,719.29},{-0.313,0.0,-0.95},{-0.95,0.0,0.313},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_165','Block',{-746.921,41.55,716.532},{-0.434,0.0,-0.901},{-0.901,0.0,0.434},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_166','Block',{-748.286,41.55,713.929},{-0.548,0.0,-0.836},{-0.836,0.0,0.548},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_167','Block',{-749.978,41.55,711.527},{-0.653,0.0,-0.758},{-0.758,0.0,0.653},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_168','Block',{-751.97,41.55,709.366},{-0.746,0.0,-0.666},{-0.666,0.0,0.746},{2.239,1.0,3.7},false},
  {'COL_SG_Guard_169','Block',{-650.987,37.55,631.675},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.8,1.0,3.7},false},
  {'COL_SG_Guard_170','Block',{-642.782,37.55,612.345},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.8,1.0,3.7},false},
  {'COL_SG_Guard_171','Block',{-653.047,37.55,605.815},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{23.8,1.0,3.7},false},
  {'COL_SG_Guard_174','Block',{-663.275,37.55,628.633},{0.921,0.0,0.391},{0.391,0.0,-0.921},{22.8,1.0,3.7},false},
  {'COL_SG_Guard_177','Block',{-728.565,37.55,694.466},{0.988,0.0,0.156},{0.156,0.0,-0.988},{16.262,1.0,3.7},false},
  {'COL_SG_Guard_179','Block',{-707.636,37.55,682.74},{0.675,0.0,-0.738},{-0.738,0.0,-0.675},{35.854,1.0,3.7},false},
  {'COL_SG_Guard_183','Block',{-686.929,37.55,652.298},{0.439,0.0,-0.899},{-0.899,0.0,-0.439},{37.851,1.0,3.7},false},
  {'COL_SG_Guard_187','Block',{-676.205,37.55,629.663},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{11.8,1.0,3.7},false},
  {'COL_SG_Guard_189','Block',{-662.14,37.55,596.524},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{11.8,1.0,3.7},false},
  {'COL_SG_Guard_191','Block',{-653.259,37.55,573.106},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{37.851,1.0,3.7},false},
  {'COL_SG_Guard_195','Block',{-643.044,37.55,533.879},{0.167,0.0,-0.986},{-0.986,0.0,-0.167},{42.97,1.0,3.7},false},
  {'COL_SG_Guard_200','Block',{-644.418,37.55,493.871},{-0.27,0.0,-0.963},{-0.963,0.0,0.27},{38.208,1.0,3.7},false},
  {'COL_SG_Guard_204','Block',{-660.052,37.55,464.051},{-0.692,0.0,-0.722},{-0.722,0.0,0.692},{30.248,1.0,3.7},false},
  {'COL_SG_Guard_207','Block',{-682.024,37.55,451.076},{-0.991,0.0,-0.135},{-0.135,0.0,0.991},{22.567,1.0,3.7},false},
  {'COL_SG_Guard_210','Block',{-696.317,37.55,454.372},{-0.391,0.0,0.921},{0.921,0.0,0.391},{10.8,1.0,3.7},false},
  {'COL_SG_Guard_211','Block',{-781.476,37.55,685.907},{1.0,0.0,-0.017},{-0.017,0.0,-1.0},{13.241,1.0,3.7},false},
  {'COL_SG_Guard_213','Block',{-768.442,37.55,684.182},{0.963,0.0,-0.27},{-0.27,0.0,-0.963},{12.539,1.0,3.7},false},
  {'COL_SG_Guard_215','Block',{-759.792,37.55,683.265},{0.921,0.0,0.391},{0.391,0.0,-0.921},{5.8,1.0,3.7},false},
  {'COL_SG_Guard_216','Block',{-740.922,37.55,691.275},{0.921,0.0,0.391},{0.391,0.0,-0.921},{8.8,1.0,3.7},false},
  {'COL_SG_Guard_217','Block',{-614.557,29.55,648.224},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.8,1.0,3.7},false},
  {'COL_SG_Guard_218','Block',{-605.766,29.55,627.513},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.8,1.0,3.7},false},
  {'COL_SG_Guard_219','Block',{-614.915,29.55,620.914},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{21.8,1.0,3.7},false},
  {'COL_SG_Guard_222','Block',{-627.134,29.55,618.987},{-0.391,0.0,0.921},{0.921,0.0,0.391},{3.8,1.0,3.7},false},
  {'COL_SG_Guard_223','Block',{-635.534,29.55,638.778},{-0.391,0.0,0.921},{0.921,0.0,0.391},{2.8,1.0,3.7},false},
  {'COL_SG_Guard_224','Block',{-625.925,29.55,645.572},{0.921,0.0,0.391},{0.391,0.0,-0.921},{20.8,1.0,3.7},false},
  {'COL_SG_HallAltar_001','Block',{-946.937,58.2,512.471},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.8,3.0,13.0},false},
  {'COL_SG_HallAltar_002','Block',{-934.122,58.2,482.278},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{4.8,3.0,13.0},false},
  {'COL_SG_HallDoor_001','Block',{-864.895,60.95,539.037},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.6,1.2,18.5},false},
  {'COL_SG_HallDoor_002','Block',{-858.019,60.95,522.836},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.6,1.2,18.5},false},
  {'COL_SG_HallPier_001','Block',{-882.826,61.95,565.755},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_002','Block',{-900.009,61.95,558.462},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_003','Block',{-917.192,61.95,551.169},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_004','Block',{-934.375,61.95,543.875},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_005','Block',{-951.558,61.95,536.582},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_006','Block',{-877.911,61.95,568.167},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.6,2.4,20.5},false},
  {'COL_SG_HallPier_007','Block',{-956.707,61.95,534.723},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.6,2.4,20.5},false},
  {'COL_SG_HallPier_008','Block',{-851.257,61.95,491.377},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_009','Block',{-868.44,61.95,484.084},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_010','Block',{-885.623,61.95,476.791},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_011','Block',{-902.806,61.95,469.498},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_012','Block',{-919.989,61.95,462.205},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,4.6,20.5},false},
  {'COL_SG_HallPier_013','Block',{-846.108,61.95,493.237},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.6,2.4,20.5},false},
  {'COL_SG_HallPier_014','Block',{-924.904,61.95,459.793},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.6,2.4,20.5},false},
  {'COL_SG_HallThrone_001','Block',{-940.483,52.175,497.394},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{20.0,3.1,0.95},false},
  {'COL_SG_HallThrone_002','Block',{-940.805,52.4,497.258},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{16.8,2.4,1.4},false},
  {'COL_SG_HallThrone_003','Block',{-941.105,52.625,497.131},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{13.6,1.75,1.85},false},
  {'COL_SG_HallThrone_004','Block',{-941.105,57.35,497.131},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{7.0,1.75,7.6},false},
  {'COL_SG_Islet_001','Block',{-673.173,42.7,351.215},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{22.007,3.0,3.0},false},
  {'COL_SG_Islet_002','Block',{-675.935,42.7,350.043},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{29.826,3.0,3.0},false},
  {'COL_SG_Islet_003','Block',{-678.696,42.7,348.871},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{34.959,3.0,3.0},false},
  {'COL_SG_Islet_004','Block',{-681.458,42.7,347.699},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{38.892,3.0,3.0},false},
  {'COL_SG_Islet_005','Block',{-684.219,42.7,346.527},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{41.377,3.0,3.0},false},
  {'COL_SG_Islet_006','Block',{-686.981,42.7,345.354},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{42.934,3.0,3.0},false},
  {'COL_SG_Islet_007','Block',{-689.742,42.7,344.182},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{43.724,3.0,3.0},false},
  {'COL_SG_Islet_008','Block',{-692.504,42.7,343.01},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{43.868,3.0,3.0},false},
  {'COL_SG_Islet_009','Block',{-695.265,42.7,341.838},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{43.46,3.0,3.0},false},
  {'COL_SG_Islet_010','Block',{-698.027,42.7,340.666},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{42.67,3.0,3.0},false},
  {'COL_SG_Islet_011','Block',{-700.789,42.7,339.494},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{40.549,3.0,3.0},false},
  {'COL_SG_Islet_012','Block',{-703.55,42.7,338.322},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{38.028,3.0,3.0},false},
  {'COL_SG_Islet_013','Block',{-706.312,42.7,337.15},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{33.424,3.0,3.0},false},
  {'COL_SG_Islet_014','Block',{-709.073,42.7,335.978},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{27.22,3.0,3.0},false},
  {'COL_SG_Islet_015','Block',{-711.374,42.7,335.001},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{17.184,2.0,3.0},false},
  {'COL_SG_Islet_016','Block',{-685.402,43.2,327.557},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{10.0,18.0,2.0},false},
  {'COL_SG_Islet_017','Block',{-698.931,45.55,323.225},{-0.945,0.0,0.326},{0.326,0.0,0.945},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_018','Block',{-707.998,45.55,329.345},{-0.656,0.0,0.755},{0.755,0.0,0.656},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_019','Block',{-712.791,45.55,339.18},{-0.19,0.0,0.982},{0.982,0.0,0.19},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_020','Block',{-712.024,45.55,350.092},{0.326,0.0,0.945},{0.945,0.0,-0.326},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_021','Block',{-709.494,45.55,356.356},{0.602,0.0,0.799},{0.799,0.0,-0.602},{3.078,1.0,3.7},false},
  {'COL_SG_Islet_022','Block',{-685.157,45.55,363.186},{0.945,0.0,-0.326},{-0.326,0.0,-0.945},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_023','Block',{-676.089,45.55,357.066},{0.656,0.0,-0.755},{-0.755,0.0,-0.656},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_024','Block',{-671.297,45.55,347.232},{0.19,0.0,-0.982},{-0.982,0.0,-0.19},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_025','Block',{-672.063,45.55,336.319},{-0.326,0.0,-0.945},{-0.945,0.0,0.326},{12.126,1.0,3.7},false},
  {'COL_SG_Islet_026','Block',{-674.594,45.55,330.055},{-0.602,0.0,-0.799},{-0.799,0.0,0.602},{3.078,1.0,3.7},false},
  {'COL_SG_Islet_027','Block',{-676.565,45.8,331.308},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{10.0,1.2,4.2},false},
  {'COL_SG_Islet_028','Block',{-694.239,45.8,323.806},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{10.0,1.2,4.2},false},
  {'COL_SG_PropArch_001','Block',{-798.3,49.7,567.955},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.4,1.4,11.0},false},
  {'COL_SG_PropArch_002','Block',{-790.955,49.7,550.649},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.4,1.4,11.0},false},
  {'COL_SG_PropBench_001','Block',{-717.177,37.04,580.343},{-0.777,0.0,0.629},{0.629,0.0,0.777},{5.0,1.7,1.67},false},
  {'COL_SG_PropBench_002','Block',{-725.688,37.04,600.395},{0.087,0.0,0.996},{0.996,0.0,-0.087},{5.0,1.7,1.67},false},
  {'COL_SG_PropBench_003','Block',{-687.975,37.04,616.402},{0.777,0.0,-0.629},{-0.629,0.0,-0.777},{5.0,1.7,1.67},false},
  {'COL_SG_PropBench_004','Block',{-679.464,37.04,596.35},{-0.087,0.0,-0.996},{-0.996,0.0,0.087},{5.0,1.7,1.67},false},
  {'COL_SG_PropCourtLamp_001','Block',{-834.27,56.7,551.601},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.0,1.0,9.0},false},
  {'COL_SG_PropCourtLamp_002','Block',{-827.706,56.7,536.136},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.0,1.0,9.0},false},
  {'COL_SG_PropCourtLamp_003','Block',{-849.919,56.7,544.959},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.0,1.0,9.0},false},
  {'COL_SG_PropCourtLamp_004','Block',{-843.355,56.7,529.495},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.0,1.0,9.0},false},
  {'COL_SG_PropLamp_001','Block',{-711.417,40.7,576.491},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_PropLamp_002','Block',{-724.457,40.7,607.214},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_PropLamp_003','Block',{-693.735,40.7,620.254},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_PropLamp_004','Block',{-680.695,40.7,589.531},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_PropLamp_005','Block',{-803.264,48.7,639.285},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_PropLamp_006','Block',{-663.397,40.7,492.244},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_PropLantern_001','Block',{-751.571,46.0,585.833},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,3.6},false},
  {'COL_SG_PropLantern_002','Block',{-745.632,46.0,571.841},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,3.6},false},
  {'COL_SG_PropLantern_003','Block',{-764.458,46.0,580.363},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,3.6},false},
  {'COL_SG_PropLantern_004','Block',{-758.52,46.0,566.371},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,3.6},false},
  {'COL_SG_PropLantern_005','Block',{-790.233,46.0,569.423},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,3.6},false},
  {'COL_SG_PropLantern_006','Block',{-784.294,46.0,555.431},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.9,1.9,3.6},false},
  {'COL_SG_PropMast_001','Block',{-730.45,43.2,599.034},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,14.0},false},
  {'COL_SG_PropMast_002','Block',{-721.464,43.2,577.862},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,14.0},false},
  {'COL_SG_PropMuret_001','Block',{-844.197,53.1,587.148},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.5,15.0,2.0},false},
  {'COL_SG_PropMuret_002','Block',{-809.034,53.1,504.301},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.5,15.0,2.0},false},
  {'COL_SG_PropObelisk_001','Block',{-855.302,59.7,556.362},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,3.6,15.0},false},
  {'COL_SG_PropObelisk_002','Block',{-838.892,59.7,517.701},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.6,3.6,15.0},false},
  {'COL_SG_PropParterre_001','Block',{-838.489,53.05,567.301},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{25.0,11.5,1.9},false},
  {'COL_SG_PropParterre_002','Block',{-819.344,53.05,522.195},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{25.0,11.5,1.9},false},
  {'COL_SG_PropStatue_001','Block',{-856.123,57.7,546.78},{0.996,0.0,0.087},{0.087,0.0,-0.996},{3.6,3.6,11.0},false},
  {'COL_SG_PropStatue_002','Block',{-846.355,57.7,523.767},{0.755,0.0,0.656},{0.656,0.0,-0.755},{3.6,3.6,11.0},false},
  {'COL_SG_StairEastP3_001','Ramp',{-759.947,47.748,452.35},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,12.0,1.0},false},
  {'COL_SG_StairEastP3_002','Block',{-768.105,51.7,448.888},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{1.15,12.0,1.0},false},
  {'COL_SG_StairEastP3_003','Ramp',{-757.473,49.314,446.231},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,1.2,5.5},false},
  {'COL_SG_StairEastP3_004','Ramp',{-762.63,49.314,458.382},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,1.2,5.5},false},
  {'COL_SG_StairEntry_001','Ramp',{-638.419,31.743,625.603},{-0.841,0.406,-0.357},{-0.391,-0.0,0.921},{19.698,18.0,1.0},false},
  {'COL_SG_StairEntry_002','Block',{-647.069,35.7,621.932},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{1.2,18.0,1.0},false},
  {'COL_SG_StairEntry_003','Ramp',{-634.835,33.361,616.696},{-0.841,0.406,-0.357},{-0.391,-0.0,0.921},{19.698,1.2,5.5},false},
  {'COL_SG_StairEntry_004','Ramp',{-642.336,33.361,634.37},{-0.841,0.406,-0.357},{-0.391,-0.0,0.921},{19.698,1.2,5.5},false},
  {'COL_SG_StairGate_001','Ramp',{-803.707,47.748,555.448},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,16.0,1.0},false},
  {'COL_SG_StairGate_002','Block',{-811.864,51.7,551.986},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{1.15,16.0,1.0},false},
  {'COL_SG_StairGate_003','Ramp',{-800.45,49.314,547.488},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,1.2,5.5},false},
  {'COL_SG_StairGate_004','Ramp',{-807.171,49.314,563.321},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,1.2,5.5},false},
  {'COL_SG_StairP1P2_001','Ramp',{-735.588,39.748,584.36},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,16.0,1.0},false},
  {'COL_SG_StairP1P2_002','Block',{-743.746,43.7,580.898},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{1.15,16.0,1.0},false},
  {'COL_SG_StairP1P2_003','Ramp',{-732.332,41.314,576.4},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,1.2,5.5},false},
  {'COL_SG_StairP1P2_004','Ramp',{-739.052,41.314,592.233},{-0.833,0.426,-0.354},{-0.391,-0.0,0.921},{18.788,1.2,5.5},false},
  {'COL_SG_StairSummon_001','Ramp',{-756.952,37.748,700.889},{-0.354,0.426,0.833},{0.921,-0.0,0.391},{9.394,12.0,1.0},false},
  {'COL_SG_StairSummon_002','Block',{-758.754,39.7,705.134},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.15,12.0,1.0},false},
  {'COL_SG_StairSummon_003','Ramp',{-763.071,39.314,698.414},{-0.354,0.426,0.833},{0.921,-0.0,0.391},{9.394,1.2,5.5},false},
  {'COL_SG_StairSummon_004','Ramp',{-750.921,39.314,703.571},{-0.354,0.426,0.833},{0.921,-0.0,0.391},{9.394,1.2,5.5},false},
  {'COL_SG_SumPodium_001','Block',{-778.621,41.55,729.481},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.55,15.898,3.9},false},
  {'COL_SG_SumPodium_002','Block',{-762.466,41.55,736.338},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.55,15.898,3.9},false},
  {'COL_SG_SumPodium_003','Block',{-772.291,41.55,737.029},{0.921,0.0,0.391},{0.391,0.0,-0.921},{10.0,6.948,3.9},false},
  {'COL_SG_SumPodium_004','Block',{-774.022,41.55,741.107},{0.921,0.0,0.391},{0.391,0.0,-0.921},{18.0,1.913,3.9},false},
  {'COL_SG_SumPodium_005','Block',{-774.69,41.55,742.68},{0.921,0.0,0.391},{0.391,0.0,-0.921},{10.0,1.504,3.9},false},
  {'COL_SG_SumPodium_006','Block',{-782.301,40.3,727.788},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.55,16.756,1.4},false},
  {'COL_SG_SumPodium_007','Block',{-775.407,40.3,721.911},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.55,0.55,1.4},false},
  {'COL_SG_SumPodium_008','Block',{-758.69,40.3,737.81},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.55,16.756,1.4},false},
  {'COL_SG_SumPodium_009','Block',{-759.252,40.3,728.768},{0.921,0.0,0.391},{0.391,0.0,-0.921},{7.55,0.55,1.4},false},
  {'COL_SG_SumStair_001','Ramp',{-766.411,41.753,723.175},{-0.349,0.447,0.823},{0.921,-0.0,0.391},{8.944,7.6,1.0},false},
  {'COL_SG_SumStair_002','Block',{-768.102,43.7,727.158},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.1,7.6,1.0},false},
  {'COL_SG_SumStair_003','Ramp',{-770.479,43.26,721.499},{-0.349,0.447,0.823},{0.921,-0.0,0.391},{8.944,1.2,5.5},false},
  {'COL_SG_SumStair_004','Ramp',{-762.379,43.26,724.937},{-0.349,0.447,0.823},{0.921,-0.0,0.391},{8.944,1.2,5.5},false},
  {'COL_SG_SumTower_001','Block',{-772.634,60.05,737.836},{0.921,0.0,0.391},{0.391,0.0,-0.921},{17.2,8.7,33.1},false},
  {'COL_SG_SumTower_002','Block',{-770.407,66.4,732.589},{0.921,0.0,0.391},{0.391,0.0,-0.921},{17.2,2.7,20.4},false},
  {'COL_SG_SumTower_003','Block',{-769.293,57.3,729.965},{0.921,0.0,0.391},{0.391,0.0,-0.921},{8.0,3.0,2.2},false},
  {'COL_SG_SumTower_004','Block',{-775.62,50.95,728.746},{0.921,0.0,0.391},{0.391,0.0,-0.921},{4.6,5.7,14.9},false},
  {'COL_SG_SumTower_005','Block',{-780.12,57.35,731.671},{0.921,0.0,0.391},{0.391,0.0,-0.921},{4.2,2.2,27.7},false},
  {'COL_SG_SumTower_006','Block',{-777.036,47.75,723.637},{0.921,0.0,0.391},{0.391,0.0,-0.921},{3.4,3.4,8.5},false},
  {'COL_SG_SumTower_007','Block',{-764.021,50.95,733.669},{0.921,0.0,0.391},{0.391,0.0,-0.921},{4.6,5.7,14.9},false},
  {'COL_SG_SumTower_008','Block',{-762.998,57.35,738.938},{0.921,0.0,0.391},{0.391,0.0,-0.921},{4.2,2.2,27.7},false},
  {'COL_SG_SumTower_009','Block',{-759.362,47.75,731.138},{0.921,0.0,0.391},{0.391,0.0,-0.921},{3.4,3.4,8.5},false},
  {'COL_SG_SumTower_010','Block',{-769.567,42.1,730.609},{0.921,0.0,0.391},{0.391,0.0,-0.921},{10.0,7.0,4.2},false},
  {'COL_SG_SummonBridge_001','Block',{-753.196,35.2,692.04},{-0.391,0.0,0.921},{0.921,0.0,0.391},{16.0,12.0,2.0},false},
  {'COL_SG_SummonBridge_002','Block',{-759.271,37.95,689.461},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.0,1.2,4.5},false},
  {'COL_SG_SummonBridge_003','Block',{-747.121,37.95,694.619},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.0,1.2,4.5},false},
  {'COL_SG_TerButtress_001','Block',{-835.191,47.9,609.439},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.45},false},
  {'COL_SG_TerButtress_002','Block',{-823.079,47.9,580.903},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.45},false},
  {'COL_SG_TerButtress_003','Block',{-799.441,47.9,525.211},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.45},false},
  {'COL_SG_TerButtress_004','Block',{-792.018,47.9,507.722},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.45},false},
  {'COL_SG_TerButtress_005','Block',{-781.859,47.9,483.788},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.45},false},
  {'COL_SG_TerButtress_006','Block',{-775.217,47.9,468.14},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.45},false},
  {'COL_SG_TerButtress_007','Block',{-783.433,39.85,676.897},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_008','Block',{-776.303,39.85,660.098},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_009','Block',{-769.172,39.85,643.299},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_010','Block',{-762.042,39.85,626.499},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_011','Block',{-750.142,39.85,598.462},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_012','Block',{-735.555,39.85,564.096},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_013','Block',{-723.411,39.85,535.483},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_014','Block',{-715.792,39.85,517.533},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_015','Block',{-708.173,39.85,499.583},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerButtress_016','Block',{-700.555,39.85,481.633},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{3.2,2.5,7.35},false},
  {'COL_SG_TerMound_001','Block',{-1002.345,54.25,562.391},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{19.956,8.316,43.5},false},
  {'COL_SG_TerMound_002','Block',{-1002.345,54.25,562.391},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{19.956,8.316,43.5},false},
  {'COL_SG_TerMound_003','Block',{-1002.345,54.25,562.391},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{19.956,8.316,43.5},false},
  {'COL_SG_TerMound_004','Block',{-1002.345,54.25,562.391},{-0.713,0.0,0.701},{0.701,0.0,0.713},{19.956,8.316,43.5},false},
  {'COL_SG_TerMound_005','Block',{-904.627,52.25,419.187},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{26.608,11.071,39.5},false},
  {'COL_SG_TerMound_006','Block',{-904.627,52.25,419.187},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{26.608,11.071,39.5},false},
  {'COL_SG_TerMound_007','Block',{-904.627,52.25,419.187},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{26.608,11.071,39.5},false},
  {'COL_SG_TerMound_008','Block',{-904.627,52.25,419.187},{-0.713,0.0,0.701},{0.701,0.0,0.713},{26.608,11.071,39.5},false},
  {'COL_SG_TerMound_009','Block',{-928.614,49.25,393.797},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{19.956,8.316,33.5},false},
  {'COL_SG_TerMound_010','Block',{-928.614,49.25,393.797},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{19.956,8.316,33.5},false},
  {'COL_SG_TerMound_011','Block',{-928.614,49.25,393.797},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{19.956,8.316,33.5},false},
  {'COL_SG_TerMound_012','Block',{-928.614,49.25,393.797},{-0.713,0.0,0.701},{0.701,0.0,0.713},{19.956,8.316,33.5},false},
  {'COL_SG_TerMound_013','Block',{-873.141,45.25,636.785},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{16.63,6.938,25.5},false},
  {'COL_SG_TerMound_014','Block',{-873.141,45.25,636.785},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{16.63,6.938,25.5},false},
  {'COL_SG_TerMound_015','Block',{-873.141,45.25,636.785},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{16.63,6.938,25.5},false},
  {'COL_SG_TerMound_016','Block',{-873.141,45.25,636.785},{-0.713,0.0,0.701},{0.701,0.0,0.713},{16.63,6.938,25.5},false},
  {'COL_SG_TerSpire_001','Block',{-888.443,42.5,391.294},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{16.26,6.785,20.0},false},
  {'COL_SG_TerSpire_002','Block',{-888.443,42.5,391.294},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{16.26,6.785,20.0},false},
  {'COL_SG_TerSpire_003','Block',{-888.443,42.5,391.294},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{16.26,6.785,20.0},false},
  {'COL_SG_TerSpire_004','Block',{-888.443,42.5,391.294},{-0.713,0.0,0.701},{0.701,0.0,0.713},{16.26,6.785,20.0},false},
  {'COL_SG_Terrain_001','Block',{-805.844,48.2,529.421},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{205.761,6.0,8.0},false},
  {'COL_SG_Terrain_002','Block',{-811.224,48.2,526.738},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{206.006,6.0,8.0},false},
  {'COL_SG_Terrain_003','Block',{-816.604,48.2,524.056},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{206.251,6.0,8.0},false},
  {'COL_SG_Terrain_004','Block',{-821.983,48.2,521.373},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{206.496,6.0,8.0},false},
  {'COL_SG_Terrain_005','Block',{-827.363,48.2,518.691},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{206.741,6.0,8.0},false},
  {'COL_SG_Terrain_006','Block',{-832.742,48.2,516.009},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{206.986,6.0,8.0},false},
  {'COL_SG_Terrain_007','Block',{-838.122,48.2,513.326},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{207.231,6.0,8.0},false},
  {'COL_SG_Terrain_008','Block',{-843.501,48.2,510.644},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{207.475,6.0,8.0},false},
  {'COL_SG_Terrain_009','Block',{-848.135,48.2,506.204},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{203.033,6.0,8.0},false},
  {'COL_SG_Terrain_010','Block',{-852.724,48.2,501.66},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{197.012,6.0,8.0},false},
  {'COL_SG_Terrain_011','Block',{-857.314,48.2,497.116},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{190.992,6.0,8.0},false},
  {'COL_SG_Terrain_012','Block',{-862.402,48.2,493.747},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{187.524,6.0,8.0},false},
  {'COL_SG_Terrain_013','Block',{-868.006,48.2,491.594},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{186.697,6.0,8.0},false},
  {'COL_SG_Terrain_014','Block',{-873.61,48.2,489.44},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{185.869,6.0,8.0},false},
  {'COL_SG_Terrain_015','Block',{-879.214,48.2,487.286},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{185.041,6.0,8.0},false},
  {'COL_SG_Terrain_016','Block',{-884.818,48.2,485.132},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{184.214,6.0,8.0},false},
  {'COL_SG_Terrain_017','Block',{-890.422,48.2,482.978},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{183.386,6.0,8.0},false},
  {'COL_SG_Terrain_018','Block',{-896.61,48.2,482.201},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{179.569,6.0,8.0},false},
  {'COL_SG_Terrain_019','Block',{-905.902,48.2,488.736},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{159.863,6.0,8.0},false},
  {'COL_SG_Terrain_020','Block',{-919.53,48.2,505.487},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{117.96,6.0,8.0},false},
  {'COL_SG_Terrain_021','Block',{-925.079,48.2,503.206},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{117.41,6.0,8.0},false},
  {'COL_SG_Terrain_022','Block',{-930.629,48.2,500.924},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{116.861,6.0,8.0},false},
  {'COL_SG_Terrain_023','Block',{-936.179,48.2,498.642},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{116.311,6.0,8.0},false},
  {'COL_SG_Terrain_024','Block',{-941.728,48.2,496.361},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{115.761,6.0,8.0},false},
  {'COL_SG_Terrain_025','Block',{-947.278,48.2,494.079},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{115.211,6.0,8.0},false},
  {'COL_SG_Terrain_026','Block',{-952.828,48.2,491.797},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{114.662,6.0,8.0},false},
  {'COL_SG_Terrain_027','Block',{-958.377,48.2,489.516},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{114.112,6.0,8.0},false},
  {'COL_SG_Terrain_028','Block',{-963.927,48.2,487.234},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{113.562,6.0,8.0},false},
  {'COL_SG_Terrain_029','Block',{-969.477,48.2,484.952},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{113.012,6.0,8.0},false},
  {'COL_SG_Terrain_030','Block',{-975.026,48.2,482.671},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{112.463,6.0,8.0},false},
  {'COL_SG_Terrain_032','Block',{-805.248,48.2,529.808},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{206.4,4.6,8.0},false},
  {'COL_SG_Terrain_033','Block',{-785.728,48.2,426.517},{-0.886,0.0,-0.464},{-0.464,0.0,0.886},{49.563,4.6,8.0},false},
  {'COL_SG_Terrain_034','Block',{-834.974,48.2,406.696},{-0.956,0.0,-0.294},{-0.294,0.0,0.956},{58.71,4.6,8.0},false},
  {'COL_SG_Terrain_035','Block',{-869.167,48.2,407.814},{-0.644,0.0,0.765},{0.765,0.0,0.644},{27.603,4.6,8.0},false},
  {'COL_SG_Terrain_036','Block',{-884.994,48.2,435.125},{-0.391,0.0,0.921},{0.921,0.0,0.391},{38.4,4.6,8.0},false},
  {'COL_SG_Terrain_037','Block',{-928.31,48.2,442.047},{-0.941,0.0,-0.338},{-0.338,0.0,0.941},{70.514,4.6,8.0},false},
  {'COL_SG_Terrain_038','Block',{-980.296,48.2,480.496},{-0.391,0.0,0.921},{0.921,0.0,0.391},{112.4,4.6,8.0},false},
  {'COL_SG_Terrain_039','Block',{-950.713,48.2,553.564},{0.907,0.0,0.422},{0.422,0.0,-0.907},{116.469,4.6,8.0},false},
  {'COL_SG_Terrain_040','Block',{-891.302,48.2,591.37},{0.423,0.0,0.906},{0.906,0.0,-0.423},{27.307,4.6,8.0},false},
  {'COL_SG_Terrain_041','Block',{-864.552,48.2,612.948},{0.904,0.0,0.428},{0.428,0.0,-0.904},{49.441,4.6,8.0},false},
  {'COL_SG_Terrain_042','Block',{-746.354,40.2,578.659},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{234.093,6.0,8.0},false},
  {'COL_SG_Terrain_043','Block',{-749.917,40.2,571.699},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{245.239,6.0,8.0},false},
  {'COL_SG_Terrain_044','Block',{-753.481,40.2,564.738},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{256.386,6.0,8.0},false},
  {'COL_SG_Terrain_045','Block',{-757.275,40.2,558.32},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{266.354,6.0,8.0},false},
  {'COL_SG_Terrain_046','Block',{-762.154,40.2,554.457},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{270.769,6.0,8.0},false},
  {'COL_SG_Terrain_047','Block',{-767.032,40.2,550.594},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{275.185,6.0,8.0},false},
  {'COL_SG_Terrain_048','Block',{-772.545,40.2,548.226},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{276.354,6.0,8.0},false},
  {'COL_SG_Terrain_049','Block',{-777.872,40.2,545.42},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{275.35,6.0,8.0},false},
  {'COL_SG_Terrain_050','Block',{-783.004,40.2,542.155},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{273.35,6.0,8.0},false},
  {'COL_SG_Terrain_051','Block',{-788.239,40.2,539.131},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{270.827,6.0,8.0},false},
  {'COL_SG_Terrain_052','Block',{-794.016,40.2,537.385},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{265.527,6.0,8.0},false},
  {'COL_SG_Terrain_053','Block',{-799.793,40.2,535.639},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{260.228,6.0,8.0},false},
  {'COL_SG_Terrain_054','Block',{-805.57,40.2,533.893},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{254.927,6.0,8.0},false},
  {'COL_SG_Terrain_056','Block',{-776.592,40.2,651.692},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{76.4,4.6,8.0},false},
  {'COL_SG_Terrain_058','Block',{-715.251,40.2,507.171},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{78.4,4.6,8.0},false},
  {'COL_SG_Terrain_059','Block',{-702.145,40.2,455.303},{-0.114,0.0,-0.993},{-0.993,0.0,0.114},{34.882,4.6,8.0},false},
  {'COL_SG_Terrain_060','Block',{-708.41,40.2,432.33},{-0.563,0.0,-0.826},{-0.826,0.0,0.563},{17.043,4.6,8.0},false},
  {'COL_SG_Terrain_061','Block',{-724.98,40.2,420.805},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{28.4,4.6,8.0},false},
  {'COL_SG_Terrain_062','Block',{-748.09,40.2,416.662},{-0.995,0.0,0.101},{0.101,0.0,0.995},{23.225,4.6,8.0},false},
  {'COL_SG_Terrain_063','Block',{-807.179,40.2,533.334},{-0.391,0.0,0.921},{0.921,0.0,0.391},{254.4,4.6,8.0},false},
  {'COL_SG_Terrain_064','Block',{-843.169,40.2,660.172},{0.75,0.0,0.662},{0.662,0.0,-0.75},{38.347,4.6,8.0},false},
  {'COL_SG_Terrain_065','Block',{-809.195,40.2,678.82},{0.953,0.0,0.304},{0.304,0.0,-0.953},{43.586,4.6,8.0},false},
  {'COL_SG_Terrain_066','Block',{-767.457,36.2,725.639},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_067','Block',{-767.457,36.2,725.639},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_068','Block',{-767.457,36.2,725.639},{-0.25,0.0,-0.968},{-0.968,0.0,0.25},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_069','Block',{-767.457,36.2,725.639},{-0.492,0.0,-0.87},{-0.87,0.0,0.492},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_070','Block',{-767.457,36.2,725.639},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_071','Block',{-767.457,36.2,725.639},{-0.862,0.0,-0.508},{-0.508,0.0,0.862},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_072','Block',{-767.457,36.2,725.639},{-0.964,0.0,-0.267},{-0.267,0.0,0.964},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_073','Block',{-767.457,36.2,725.639},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_074','Block',{-767.457,36.2,725.639},{-0.968,0.0,0.25},{0.25,0.0,0.968},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_075','Block',{-767.457,36.2,725.639},{-0.87,0.0,0.492},{0.492,0.0,0.87},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_076','Block',{-767.457,36.2,725.639},{-0.713,0.0,0.701},{0.701,0.0,0.713},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_077','Block',{-767.457,36.2,725.639},{-0.508,0.0,0.862},{0.862,0.0,0.508},{43.624,5.793,8.0},false},
  {'COL_SG_Terrain_078','Block',{-661.153,32.2,615.954},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{24.0,30.0,8.0},false},
  {'COL_SG_Terrain_079','Block',{-672.199,32.2,611.266},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{49.9,6.0,8.0},false},
  {'COL_SG_Terrain_080','Block',{-676.641,32.2,606.374},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{152.485,6.0,8.0},false},
  {'COL_SG_Terrain_081','Block',{-680.591,32.2,600.323},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{194.538,6.0,8.0},false},
  {'COL_SG_Terrain_082','Block',{-685.926,32.2,597.536},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{208.575,6.0,8.0},false},
  {'COL_SG_Terrain_083','Block',{-690.277,32.2,592.43},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{217.575,6.0,8.0},false},
  {'COL_SG_Terrain_084','Block',{-694.625,32.2,587.319},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{226.563,6.0,8.0},false},
  {'COL_SG_Terrain_085','Block',{-698.691,32.2,581.542},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{234.021,6.0,8.0},false},
  {'COL_SG_Terrain_086','Block',{-703.712,32.2,578.014},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{236.593,6.0,8.0},false},
  {'COL_SG_Terrain_087','Block',{-708.733,32.2,574.486},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{239.164,6.0,8.0},false},
  {'COL_SG_Terrain_088','Block',{-713.754,32.2,570.958},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{241.736,6.0,8.0},false},
  {'COL_SG_Terrain_089','Block',{-719.095,32.2,568.185},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{245.947,6.0,8.0},false},
  {'COL_SG_Terrain_090','Block',{-725.648,32.2,568.269},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{250.272,6.0,8.0},false},
  {'COL_SG_Terrain_091','Block',{-732.148,32.2,568.225},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{251.995,6.0,8.0},false},
  {'COL_SG_Terrain_092','Block',{-738.511,32.2,567.861},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{253.026,6.0,8.0},false},
  {'COL_SG_Terrain_094','Block',{-727.62,32.2,691.781},{0.988,0.0,0.156},{0.156,0.0,-0.988},{16.892,4.6,8.0},false},
  {'COL_SG_Terrain_095','Block',{-709.365,32.2,680.481},{0.675,0.0,-0.738},{-0.738,0.0,-0.675},{36.456,4.6,8.0},false},
  {'COL_SG_Terrain_096','Block',{-689.225,32.2,650.621},{0.439,0.0,-0.899},{-0.899,0.0,-0.439},{38.453,4.6,8.0},false},
  {'COL_SG_Terrain_098','Block',{-655.719,32.2,571.679},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{38.453,4.6,8.0},false},
  {'COL_SG_Terrain_099','Block',{-645.72,32.2,532.916},{0.167,0.0,-0.986},{-0.986,0.0,-0.167},{43.574,4.6,8.0},false},
  {'COL_SG_Terrain_100','Block',{-647.25,32.2,494.14},{-0.27,0.0,-0.963},{-0.963,0.0,0.27},{38.819,4.6,8.0},false},
  {'COL_SG_Terrain_101','Block',{-662.424,32.2,465.622},{-0.692,0.0,-0.722},{-0.722,0.0,0.692},{30.863,4.6,8.0},false},
  {'COL_SG_Terrain_102','Block',{-682.915,32.2,453.78},{-0.991,0.0,-0.135},{-0.135,0.0,0.991},{23.204,4.6,8.0},false},
  {'COL_SG_Terrain_103','Block',{-741.796,32.2,568.689},{-0.391,0.0,0.921},{0.921,0.0,0.391},{256.4,4.6,8.0},false},
  {'COL_SG_Terrain_104','Block',{-784.115,32.2,683.151},{1.0,0.0,-0.017},{-0.017,0.0,-1.0},{20.098,4.6,8.0},false},
  {'COL_SG_Terrain_105','Block',{-768.684,32.2,681.342},{0.963,0.0,-0.27},{-0.27,0.0,-0.963},{13.206,4.6,8.0},false},
  {'COL_SG_Terrain_107','Block',{-620.65,24.2,633.145},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{26.0,22.0,8.0},false},
  {'COL_SG_VegTrunk_001','Block',{-688.407,39.7,630.213},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.506,1.506,7.0},false},
  {'COL_SG_VegTrunk_002','Block',{-669.431,39.7,582.986},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.771,1.771,7.0},false},
  {'COL_SG_VegTrunk_003','Block',{-670.861,39.7,587.903},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.386,1.386,7.0},false},
  {'COL_SG_VegTrunk_004','Block',{-746.616,39.7,622.754},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.671,1.671,7.0},false},
  {'COL_SG_VegTrunk_005','Block',{-746.17,39.7,627.638},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.319,1.319,7.0},false},
  {'COL_SG_VegTrunk_006','Block',{-716.698,39.7,549.033},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.966,1.966,7.0},false},
  {'COL_SG_VegTrunk_007','Block',{-714.691,39.7,554.166},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.674,1.674,7.0},false},
  {'COL_SG_VegTrunk_008','Block',{-763.618,39.7,673.348},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.594,1.594,7.0},false},
  {'COL_SG_VegTrunk_009','Block',{-769.01,39.7,673.254},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.797,1.797,7.0},false},
  {'COL_SG_VegTrunk_010','Block',{-681.069,39.7,462.475},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.04,2.04,7.0},false},
  {'COL_SG_VegTrunk_011','Block',{-681.052,39.7,471.087},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.843,1.843,7.0},false},
  {'COL_SG_VegTrunk_012','Block',{-685.979,39.7,472.071},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.341,1.341,7.0},false},
  {'COL_SG_VegTrunk_013','Block',{-842.335,47.7,650.347},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.891,1.891,7.0},false},
  {'COL_SG_VegTrunk_014','Block',{-839.959,47.7,655.365},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.698,1.698,7.0},false},
  {'COL_SG_VegTrunk_015','Block',{-832.995,47.7,653.039},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.367,2.367,7.0},false},
  {'COL_SG_VegTrunk_016','Block',{-848.36,47.7,653.95},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.964,1.964,7.0},false},
  {'COL_SG_VegTrunk_017','Block',{-836.515,47.7,646.439},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.406,1.406,7.0},false},
  {'COL_SG_VegTrunk_018','Block',{-786.798,47.7,647.104},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.455,1.455,7.0},false},
  {'COL_SG_VegTrunk_019','Block',{-784.552,47.7,648.507},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.239,1.239,7.0},false},
  {'COL_SG_VegTrunk_020','Block',{-830.293,47.7,626.483},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.455,1.455,7.0},false},
  {'COL_SG_VegTrunk_021','Block',{-810.119,47.7,586.037},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.671,1.671,7.0},false},
  {'COL_SG_VegTrunk_022','Block',{-809.764,47.7,580.935},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.663,1.663,7.0},false},
  {'COL_SG_VegTrunk_023','Block',{-766.825,47.7,603.603},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.455,1.455,7.0},false},
  {'COL_SG_VegTrunk_024','Block',{-750.6,47.7,554.816},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.455,1.455,7.0},false},
  {'COL_SG_VegTrunk_025','Block',{-745.99,47.7,555.893},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.264,1.264,7.0},false},
  {'COL_SG_VegTrunk_026','Block',{-788.103,47.7,531.096},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.966,1.966,7.0},false},
  {'COL_SG_VegTrunk_027','Block',{-782.587,47.7,533.144},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.634,1.634,7.0},false},
  {'COL_SG_VegTrunk_028','Block',{-727.986,47.7,519.685},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.455,1.455,7.0},false},
  {'COL_SG_VegTrunk_029','Block',{-766.95,47.7,488.45},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.733,1.733,7.0},false},
  {'COL_SG_VegTrunk_030','Block',{-766.813,47.7,482.553},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.003,2.003,7.0},false},
  {'COL_SG_VegTrunk_031','Block',{-749.525,47.7,427.248},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.652,1.652,7.0},false},
  {'COL_SG_VegTrunk_032','Block',{-753.222,47.7,420.336},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.747,1.747,7.0},false},
  {'COL_SG_VegTrunk_033','Block',{-754.009,47.7,430.306},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.568,1.568,7.0},false},
  {'COL_SG_VegTrunk_034','Block',{-710.429,47.7,445.451},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.824,1.824,7.0},false},
  {'COL_SG_VegTrunk_035','Block',{-705.409,47.7,449.278},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.822,1.822,7.0},false},
  {'COL_SG_VegTrunk_036','Block',{-792.209,55.7,427.333},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.137,2.137,7.0},false},
  {'COL_SG_VilFountainPanel_001','Block',{-696.017,37.4,601.156},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.2,1.05,2.4},false},
  {'COL_SG_VilFountainPanel_002','Block',{-709.135,37.4,595.589},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{2.2,1.05,2.4},false},
  {'COL_SG_VilHouse_001','Block',{-705.689,44.81,651.368},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{14.7,11.98,18.02},false},
  {'COL_SG_VilHouse_002','Block',{-720.164,42.595,675.642},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{12.7,10.7,13.59},false},
  {'COL_SG_VilHouse_003','Block',{-760.073,44.895,647.84},{0.921,0.0,0.391},{0.391,0.0,-0.921},{11.5,12.7,18.19},false},
  {'COL_SG_VilHouse_004','Block',{-675.332,44.4,563.875},{0.009,0.0,-1.0},{-1.0,0.0,-0.009},{5.174,2.193,17.2},false},
  {'COL_SG_VilHouse_005','Block',{-675.332,44.4,563.875},{-0.701,0.0,-0.713},{-0.713,0.0,0.701},{5.174,2.193,17.2},false},
  {'COL_SG_VilHouse_006','Block',{-675.332,44.4,563.875},{-1.0,0.0,-0.009},{-0.009,0.0,1.0},{5.174,2.193,17.2},false},
  {'COL_SG_VilHouse_007','Block',{-675.332,44.4,563.875},{-0.713,0.0,0.701},{0.701,0.0,0.713},{5.174,2.193,17.2},false},
  {'COL_SG_VilHouse_008','Block',{-666.619,45.165,559.317},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{14.7,11.98,18.73},false},
  {'COL_SG_VilHouse_009','Block',{-661.333,42.805,526.797},{-0.993,0.0,0.122},{0.122,0.0,0.993},{10.7,12.7,14.01},false},
  {'COL_SG_VilHouse_010','Block',{-705.595,44.5,518.874},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.7,11.98,17.4},false},
  {'COL_SG_VilHouse_011','Block',{-784.019,53.02,631.158},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{14.7,11.98,18.44},false},
  {'COL_SG_VilHouse_012','Block',{-795.593,50.925,658.836},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{10.7,12.7,14.25},false},
  {'COL_SG_VilHouse_013','Block',{-820.602,52.94,611.285},{0.921,0.0,0.391},{0.391,0.0,-0.921},{11.5,12.7,18.28},false},
  {'COL_SG_VilHouse_014','Block',{-745.861,50.375,536.547},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{12.7,10.7,13.15},false},
  {'COL_SG_VilHouse_015','Block',{-779.409,52.71,513.617},{-0.391,0.0,0.921},{0.921,0.0,0.391},{12.7,11.98,17.82},false},
  {'COL_SG_VilLamp_001','Block',{-750.35,49.7,589.61},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.4,1.4,11.0},false},
  {'COL_SG_VilLamp_002','Block',{-742.067,49.7,570.095},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.4,1.4,11.0},false},
  {'COL_SG_VilLamp_003','Block',{-769.856,48.7,561.342},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_VilLamp_004','Block',{-723.034,40.7,639.661},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_VilLamp_005','Block',{-697.722,40.7,548.288},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{1.2,1.2,9.0},false},
  {'COL_SG_VilPlanter_001','Block',{-708.724,36.6,644.16},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_002','Block',{-712.983,36.6,654.193},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_003','Block',{-723.737,36.6,669.292},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_004','Block',{-727.214,36.6,677.484},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_005','Block',{-756.869,36.6,654.034},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_006','Block',{-753.392,36.6,645.841},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_007','Block',{-669.654,36.6,552.108},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_008','Block',{-667.602,36.6,523.084},{-0.993,0.0,0.122},{0.122,0.0,0.993},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_009','Block',{-666.518,36.6,531.917},{-0.993,0.0,0.122},{0.122,0.0,0.993},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_010','Block',{-702.17,36.6,525.162},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_011','Block',{-698.693,36.6,516.969},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_012','Block',{-787.054,44.6,623.949},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_013','Block',{-791.313,44.6,633.983},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_014','Block',{-799.166,44.6,652.485},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_015','Block',{-802.643,44.6,660.678},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_016','Block',{-817.398,44.6,617.479},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_017','Block',{-813.921,44.6,609.287},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_018','Block',{-749.434,44.6,530.196},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_019','Block',{-752.911,44.6,538.388},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_020','Block',{-775.983,44.6,519.905},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_SG_VilPlanter_021','Block',{-772.506,44.6,511.712},{0.921,0.0,0.391},{0.391,0.0,-0.921},{0.9,1.95,1.0},false},
  {'COL_GateDemonSlayerLock_001','GateLock',{-694.388,53.2,348.729},{0.921,0.0,0.391},{0.391,0.0,-0.921},{16.6,1.4,18.0},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'AUDIO_Craft',{-730.008,47.2,488.958},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='fire',['range']=26.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_DungeonPortal',{-854.973,58.2,425.054},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='energy',['range']=34.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_DungeonRooms',{-894.043,12.0,517.105},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='wind',['range']=70.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_Fountain',{-702.576,38.2,598.372},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='water',['range']=40.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_HallAmbience',{-901.407,58.2,513.98},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='wind',['range']=60.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_Summon',{-770.387,46.2,732.543},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='energy',['range']=36.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_Waterfall_1',{-820.983,33.2,682.823},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='water',['range']=60.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_Waterfall_2',{-658.698,25.2,454.044},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='water',['range']=60.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_Waterfall_3',{-1017.458,41.2,521.213},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='water',['range']=60.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'AUDIO_Waterfall_4',{-655.662,20.2,646.53},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['family']='water',['range']=60.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'CRAFT_Station',{-730.008,44.2,488.958},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{['note']='caldeirao/bancada do alquimista: ProximityPrompt \'Craft\' abre a pagina de receitas',['fwd_x']=-0.3907,['fwd_z']=0.9205}},
  {'DUNGEON_Entrance',{-849.45,52.2,427.398},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=6.0,['note']='zona/prompt de entrada na corrida (so com ENTRY_OPEN)',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUNGEON_ExitPortal',{-869.819,6.0,460.033},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{['note']='portal de volta (aparece em FINISHING/FINISHED)',['fwd_x']=-0.3907,['fwd_z']=0.9205}},
  {'DUNGEON_Portal',{-854.973,52.2,425.054},{-0.391,0.0,0.921},{0.921,0.0,0.391},{['note']='portal espiral no fundo da portaria (encara o sul)',['fwd_x']=0.9205,['fwd_z']=0.3907}},
  {'DUNGEON_Return',{-828.278,52.4,436.384},{-0.391,0.0,0.921},{0.921,0.0,0.391},{['note']='para onde o jogador volta ao sair/terminar (patio, em frente a porta)',['fwd_x']=0.9205,['fwd_z']=0.3907}},
  {'DUNGEON_Spawn',{-915.141,6.2,566.813},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'DUNGEON_UI',{-834.813,67.65,433.61},{-0.391,0.0,0.921},{0.921,0.0,0.391},{['ui']='BillboardGui: estado e contagem da dungeon (XX:00 / XX:30)',['fwd_x']=0.9205,['fwd_z']=0.3907}},
  {'DUN_ORE_R2_COMMON_02',{-903.064,6.0,505.238},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_COMMON_03',{-905.871,6.0,514.258},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_COMMON_05',{-902.698,6.0,528.0},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_COMMON_06',{-896.224,6.0,534.887},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_COMMON_08',{-880.096,6.0,525.198},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_COMMON_09',{-883.132,6.0,516.251},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_UNCOMMON_01',{-893.782,6.0,506.994},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_UNCOMMON_04',{-910.409,6.0,522.544},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_UNCOMMON_07',{-888.641,6.0,529.23},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R2_UNCOMMON_10',{-884.331,6.0,506.866},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=2.8,['room']='R2',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_EPIC_11',{-878.56,6.0,462.711},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_EPIC_12',{-889.739,6.0,471.133},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_EPIC_13',{-888.031,6.0,485.024},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_EPIC_14',{-875.144,6.0,490.494},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_EPIC_15',{-863.965,6.0,482.073},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_EPIC_16',{-865.673,6.0,468.181},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ORE_R3_SUPERLEGENDARY_17',{-876.852,6.0,476.603},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['room']='R3',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ROOM_R1',{-911.234,6.0,557.608},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['sx']=36.0,['sy']=36.0,['floor']=6.0,['ceil']=28.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ROOM_R2',{-894.825,6.0,518.946},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['sx']=44.0,['sy']=44.0,['floor']=6.0,['ceil']=28.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'DUN_ROOM_R3',{-876.852,6.0,476.603},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['sx']=44.0,['sy']=44.0,['floor']=6.0,['ceil']=28.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_1_Base',{-823.366,-60.0,688.438},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_base',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_1_Lip',{-821.764,42.2,684.664},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_2_Base',{-654.127,-60.0,443.274},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_base',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_2_Lip',{-657.917,34.2,452.203},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_3_Base',{-1035.214,-60.0,520.303},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_base',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_3_Lip',{-1019.455,50.2,521.109},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_4_Base',{-655.92,-60.0,651.743},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_base',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'FX_Fall_4_Lip',{-655.767,29.2,648.527},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fx']='nevoa_borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GATE_DemonSlayer',{-694.388,44.2,348.729},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['open_w']=16.0,['open_h']=18.0,['deck_w']=18.0,['area_id']=4,['key']='DemonSlayer',['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'GATE_DemonSlayer_EXIT',{-689.699,44.4,337.682},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['gate']='DemonSlayer',['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'GATE_DemonSlayer_INTERACT',{-697.123,44.4,355.172},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['gate']='DemonSlayer',['radius']=10.0,['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'GATE_DemonSlayer_LOCKED',{-694.388,53.2,348.729},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['gate']='DemonSlayer',['state_default']='locked',['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'GATE_DemonSlayer_OpenFX',{-694.388,53.2,348.729},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['gate']='DemonSlayer',['state']='unlocked',['fx']='abertura',['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'GP_Block_01',{-862.746,52.2,530.389},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=7.0,['kind']='porta',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_02',{-867.348,52.2,528.436},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=7.0,['kind']='porta',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_03',{-871.951,52.2,526.482},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=7.0,['kind']='porta',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_04',{-878.904,52.2,565.899},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_05',{-954.386,52.2,533.861},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_06',{-878.904,52.2,565.899},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_07',{-848.429,52.2,494.099},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_08',{-875.856,52.2,558.719},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_09',{-951.339,52.2,526.681},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_10',{-886.452,52.2,562.695},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_11',{-855.977,52.2,490.895},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_12',{-872.809,52.2,551.539},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_13',{-948.291,52.2,519.501},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_14',{-894.0,52.2,559.491},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_15',{-863.525,52.2,487.691},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_16',{-869.761,52.2,544.359},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_17',{-945.244,52.2,512.321},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_18',{-901.548,52.2,556.287},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_19',{-871.073,52.2,484.487},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_20',{-866.714,52.2,537.179},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_21',{-942.196,52.2,505.141},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_22',{-909.097,52.2,553.084},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_23',{-878.622,52.2,481.283},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_24',{-863.666,52.2,529.999},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_25',{-939.149,52.2,497.961},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_26',{-916.645,52.2,549.88},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_27',{-886.17,52.2,478.08},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_28',{-860.619,52.2,522.819},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_29',{-936.101,52.2,490.781},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_30',{-924.193,52.2,546.676},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_31',{-893.718,52.2,474.876},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_32',{-857.571,52.2,515.639},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_33',{-933.054,52.2,483.601},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_34',{-931.741,52.2,543.472},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_35',{-901.266,52.2,471.672},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_36',{-854.524,52.2,508.459},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_37',{-930.006,52.2,476.421},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_38',{-939.29,52.2,540.268},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_39',{-908.815,52.2,468.468},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_40',{-851.476,52.2,501.279},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_41',{-926.958,52.2,469.241},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_42',{-946.838,52.2,537.065},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_43',{-916.363,52.2,465.265},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_44',{-848.429,52.2,494.099},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_45',{-923.911,52.2,462.061},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_46',{-954.386,52.2,533.861},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'GP_Block_47',{-923.911,52.2,462.061},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ISLAND_EXIT_ShadowGarden',{-724.082,44.2,418.688},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['width']=18.0,['deck_z']=44.2,['heading_deg']=-67.002,['fwd_x']=0.3907,['fwd_z']=-0.9205,['heading_deg_local']=0.0}},
  {'ISLAND_NEXT_ANCHOR_DemonSlayer',{-683.448,44.2,322.954},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['width']=18.0,['deck_z']=44.2,['clear_h']=22.0,['heading_deg']=-67.002,['next_area']=4,['next_key']='DemonSlayer',['fwd_roblox']='0.3907,0.0000,-0.9205',['guard']='PROVISORIO: COL_SGAnchorGuard_* (next_island_guard=True)',['guard_note']='a integracao da ilha Demon Slayer REMOVE o guarda quando a ponte seguinte encosta aqui',['fwd_x']=0.3907,['fwd_z']=-0.9205,['heading_deg_local']=0.0}},
  {'MiningZone_ShadowGarden',{-902.328,52.2,513.589},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['kind']='mining',['floor']=52.2,['sx']=76.0,['sy']=78.0,['ceil']=80.2,['note']='Mining Hall (dentro do castelo); o jogo usa ORE_* + grade hexagonal + bloqueios GP_Block_*',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'NPC_Craft',{-727.663,44.9,483.435},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{['note']='alquimista atras do caldeirao, olhando a porta',['fwd_x']=-0.3907,['fwd_z']=0.9205}},
  {'ORE_COMMON_01',{-898.986,52.2,523.427},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_02',{-917.141,52.2,543.651},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_03',{-890.92,52.2,503.374},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_04',{-902.976,52.2,532.444},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_05',{-887.038,52.2,494.637},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_06',{-907.057,52.2,541.521},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_07',{-888.068,52.2,520.815},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_08',{-884.676,52.2,511.391},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_09',{-892.146,52.2,530.654},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_10',{-880.435,52.2,502.654},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_11',{-896.81,52.2,541.156},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_12',{-875.991,52.2,492.003},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_13',{-877.854,52.2,520.989},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_14',{-900.918,52.2,550.732},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_15',{-881.792,52.2,530.344},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_16',{-873.556,52.2,511.298},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_17',{-886.36,52.2,539.291},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_18',{-869.778,52.2,501.169},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_19',{-890.489,52.2,548.608},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_20',{-875.6,52.2,538.611},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_21',{-863.534,52.2,509.545},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_22',{-880.368,52.2,547.363},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_23',{-860.394,52.2,499.894},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_COMMON_24',{-883.606,52.2,557.885},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_01',{-923.682,52.2,489.034},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_02',{-936.434,52.2,518.287},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_03',{-920.405,52.2,479.855},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_04',{-939.37,52.2,527.915},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_05',{-920.912,52.2,507.874},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_06',{-917.457,52.2,497.38},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_07',{-925.42,52.2,517.367},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_EPIC_08',{-912.536,52.2,488.192},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_SUPERLEGENDARY_01',{-927.64,52.2,499.076},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_SUPERLEGENDARY_02',{-932.141,52.2,508.377},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_01',{-929.825,52.2,527.056},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_02',{-909.431,52.2,478.06},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_03',{-915.71,52.2,514.84},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_04',{-910.742,52.2,506.487},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_05',{-933.088,52.2,535.894},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_06',{-906.451,52.2,496.326},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_07',{-918.678,52.2,525.389},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_08',{-902.628,52.2,487.346},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_09',{-904.613,52.2,514.596},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_10',{-923.009,52.2,535.055},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_11',{-901.537,52.2,504.713},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_12',{-908.806,52.2,523.604},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_13',{-896.142,52.2,495.661},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_14',{-913.433,52.2,533.84},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_15',{-893.218,52.2,486.136},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'ORE_UNCOMMON_16',{-894.152,52.2,513.702},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER',{-866.428,52.2,528.827},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['waypoints']='-667.60,36.20,613.22;-689.69,36.20,603.84;-716.47,36.20,605.51;-726.51,36.20,588.21;-746.76,44.20,579.62;-792.79,44.20,560.08;-814.88,52.20,550.71;-848.02,52.20,536.64;-866.43,52.20,528.83;-884.84,52.20,521.01',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_00',{-667.596,36.2,613.219},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_01',{-689.689,36.2,603.842},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_02',{-716.47,36.2,605.511},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_03',{-726.509,36.2,588.214},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_04',{-746.761,44.2,579.618},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_05',{-792.787,44.2,560.083},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_06',{-814.879,52.2,550.706},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_07',{-848.018,52.2,536.641},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_08',{-866.428,52.2,528.827},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PATH_ENTRY_CENTER_09',{-884.838,52.2,521.013},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'PLAYER_INTERACT_Craft',{-731.961,45.6,493.561},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['radius']=8.0,['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'PURCHASE_UI_ANCHOR_DemonSlayer',{-695.365,58.2,351.03},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{['gate']='DemonSlayer',['faces']='approach',['ui']='BillboardGui preco/requisito',['fwd_x']=-0.3907,['fwd_z']=0.9205}},
  {'SUMMON_Interact',{-767.652,40.2,726.099},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['note']='gabinete invisivel do Gacha_sombra (prompt Invocar)',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'SUMMON_Main',{-770.387,40.2,732.543},{0.921,0.0,0.391},{0.391,0.0,-0.921},{['note']='torre de invocacao (familia das Ilhas 1 e 2), frente para +X (ponte)',['fwd_x']=0.3907,['fwd_z']=-0.9205}},
  {'SUMMON_PlayerPosition',{-764.136,40.2,717.814},{-0.921,0.0,-0.391},{-0.391,0.0,0.921},{['note']='onde o jogador fica olhando a torre (pad do gacha)',['fwd_x']=-0.3907,['fwd_z']=0.9205}},
  {'WORLD_ENTRY_ShadowGarden',{-667.596,36.4,613.219},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['note']='chegada da ilha (depois do portico B, olhando a praca e o castelo)',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
  {'WORLD_FROM_PREV',{-579.227,28.2,650.727},{0.391,0.0,-0.921},{-0.921,0.0,-0.391},{['width']=18.0,['deck_z']=28.2,['prev']='ISLAND_NEXT_ANCHOR_ShadowGarden (Ilha 2 Dragon Ball)',['note']='centro da borda do tabuleiro da ponte de chegada; avanco +Y (para dentro da ilha)',['fwd_x']=-0.9205,['fwd_z']=-0.3907}},
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
  {'L_SGCas_Door','POINT',{-852.62,63.2,534.687},{255,221,179},13.0,0.74,false,false},
  {'L_SGCas_EastGap','POINT',{-764.676,59.2,450.343},{255,221,179},10.3,0.54,false,false},
  {'L_SGCas_Emblem','POINT',{-848.938,92.2,536.25},{206,179,255},14.7,0.89,false,false},
  {'L_SGCas_Gate','POINT',{-807.515,61.2,553.832},{255,221,179},12.2,0.68,false,false},
  {'L_SGCraft_Bench','POINT',{-726.413,51.8,480.489},{255,215,170},14.3,0.86,false,false},
  {'L_SGCraft_Cauldron','POINT',{-730.008,51.6,488.958},{221,188,255},9.7,0.5,false,false},
  {'L_SGCraft_Chandelier','POINT',{-730.008,59.8,488.958},{243,223,255},12.6,0.71,false,false},
  {'L_SGCraft_DoorLantern','POINT',{-737.353,52.2,506.264},{255,215,170},9.9,0.51,false,false},
  {'L_SGDun_Approach','POINT',{-822.755,61.2,438.729},{206,166,255},20.0,1.5,false,false},
  {'L_SGDun_MouthWarm','POINT',{-828.738,57.2,436.189},{255,212,162},16.7,1.11,false,false},
  {'L_SGDun_Portal','POINT',{-852.211,59.7,426.226},{209,173,255},16.1,1.05,false,false},
  {'L_SGDun_R1_Portal','POINT',{-915.923,13.0,568.654},{209,173,255},20.0,1.5,false,false},
  {'L_SGDun_R2_ChandelierE','POINT',{-890.527,21.8,508.821},{255,215,170},20.0,1.5,false,false},
  {'L_SGDun_R2_ChandelierW','POINT',{-899.122,21.8,529.072},{255,215,170},20.0,1.5,false,false},
  {'L_SGDun_R3_Altar','POINT',{-876.852,21.0,476.603},{255,215,170},20.0,1.5,false,false},
  {'L_SGEnt_PorticoA_E_Lantern','POINT',{-614.21,32.15,623.603},{255,209,158},9.7,0.5,false,false},
  {'L_SGEnt_PorticoA_W_Lantern','POINT',{-623.04,32.15,644.407},{255,209,158},9.7,0.5,false,false},
  {'L_SGEnt_PorticoB_E_Lantern','POINT',{-650.545,40.15,607.855},{255,209,158},9.7,0.5,false,false},
  {'L_SGEnt_PorticoB_W_Lantern','POINT',{-659.61,40.15,629.211},{255,209,158},9.7,0.5,false,false},
  {'L_SGExit_Head_N','POINT',{-732.869,51.85,417.891},{255,209,158},9.7,0.5,false,false},
  {'L_SGExit_Head_S','POINT',{-717.404,51.85,424.455},{255,209,158},9.7,0.5,false,false},
  {'L_SGHall_Chandelier_NE','POINT',{-912.73,71.5,492.879},{255,215,170},20.0,1.5,false,false},
  {'L_SGHall_Chandelier_NW','POINT',{-924.451,71.5,520.494},{255,215,170},20.0,1.5,false,false},
  {'L_SGHall_Chandelier_SE','POINT',{-878.364,71.5,507.465},{255,215,170},20.0,1.5,false,false},
  {'L_SGHall_Chandelier_SW','POINT',{-890.085,71.5,535.081},{255,215,170},20.0,1.5,false,false},
  {'L_SGHall_Moon_W','POINT',{-924.064,74.2,543.472},{200,215,255},18.2,1.3,false,false},
  {'L_SGHall_Throne','POINT',{-935.927,64.2,499.328},{203,162,255},20.0,1.5,false,false},
  {'L_SGProp_Court_Violet','POINT',{-848.478,59.2,536.445},{206,173,255},10.7,0.56,false,true},
  {'L_SGProp_P1_EastEnd','POINT',{-663.397,44.5,492.244},{255,218,173},9.5,0.49,false,true},
  {'L_SGProp_P2_West','POINT',{-803.264,52.5,639.285},{255,218,173},9.5,0.49,false,true},
  {'L_SGProp_Plaza_NE','POINT',{-711.417,44.5,576.491},{255,218,173},9.5,0.49,false,true},
  {'L_SGProp_Plaza_NW','POINT',{-724.457,44.5,607.214},{255,218,173},9.5,0.49,false,true},
  {'L_SGSum_Core','POINT',{-771.559,86.2,735.304},{206,177,255},20.0,1.5,false,false},
  {'L_SGSum_Lantern_N','POINT',{-759.362,48.3,731.138},{255,209,158},10.3,0.54,false,false},
  {'L_SGSum_Lantern_S','POINT',{-777.036,48.3,723.637},{255,209,158},10.3,0.54,false,false},
  {'L_SGVil_Lamp_00','POINT',{-749.862,52.1,588.46},{255,218,170},9.0,0.46,false,true},
  {'L_SGVil_Lamp_01','POINT',{-742.555,52.1,571.246},{255,218,170},9.0,0.46,false,true},
  {'L_SGVil_Lamp_02','POINT',{-769.856,52.5,561.342},{255,218,170},9.0,0.46,false,true},
  {'L_SGVil_Lamp_03','POINT',{-723.034,44.5,639.661},{255,218,170},9.0,0.46,false,true},
  {'L_SGVil_Lamp_04','POINT',{-697.722,44.5,548.288},{255,218,170},9.0,0.46,false,true},
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
  {'SAFE_Entrada',{-667.596,36.2,613.219}},
  {'SAFE_Praca',{-682.325,36.2,606.968}},
  {'SAFE_Vila_P1_O',{-733.383,36.2,650.478}},
  {'SAFE_Vila_P1_L',{-684.935,36.2,536.334}},
  {'SAFE_Vila_P2',{-778.979,44.2,565.944}},
  {'SAFE_Vila_P2_O',{-810.235,44.2,639.585}},
  {'SAFE_Patio_Castelo',{-838.812,52.2,540.548}},
  {'SAFE_Salao',{-884.838,52.2,521.013}},
  {'SAFE_Dungeon',{-827.357,52.2,436.775}},
  {'SAFE_Craft',{-755.536,44.2,510.713}},
  {'SAFE_Summon',{-762.768,40.2,714.593}},
  {'SAFE_Saida',{-734.631,44.2,443.542}},
  {'SAFE_Ilhota',{-696.732,44.2,354.252}},
  {'SAFE_Ponte_Chegada',{-599.478,28.2,642.131}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(420,4,480); v.Position = Vector3.new(-811.1968994140625,-40.0,552.2689819335938) + ROOT_OFFSET
  v:ClearAllChildren()
  for _, s in ipairs(SAFE) do local at = Instance.new('Attachment'); at.Name = s[1]; at.Parent = v
    at.WorldPosition = Vector3.new(s[2][1], s[2][2], s[2][3]) + ROOT_OFFSET end
  v.Parent = root end

-- Script de servidor: personagens no grupo 'Personagens' (atravessam as cascas SoVisual) + rede de quedas
do
  local SSS = game:GetService('ServerScriptService')
  local s = SSS:FindFirstChild('ILHA_SHADOWGARDEN_Servidor') or Instance.new('Script')
  s.Name = 'ILHA_SHADOWGARDEN_Servidor'
  s.Source = [==[
-- gerado por montar_ilha_shadowgarden.lua (export_roblox.py) - nao editar a mao
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
local root = workspace:WaitForChild('ILHA_SHADOWGARDEN', 60)
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
  Lg.GeographicLatitude = 35.033
  Lg.ClockTime = 14.95
  Lg.EnvironmentDiffuseScale = 0.4
  Lg.EnvironmentSpecularScale = 0.5
  Lg.Brightness = 2.5
  Lg.ExposureCompensation = 0.0
  Lg.ShadowSoftness = 0.2
  Lg.OutdoorAmbient = Color3.fromRGB(118,128,152)
  Lg.Ambient = Color3.fromRGB(90,92,104)
  Lg.ColorShift_Top = Color3.fromRGB(255,236,210)
  do local e = Lg:FindFirstChildOfClass('ColorCorrectionEffect') or Instance.new('ColorCorrectionEffect', Lg)
    e.Saturation = 0.15
    e.Contrast = 0.12
    e.TintColor = Color3.fromRGB(255,246,236)
  end
  do local e = Lg:FindFirstChildOfClass('BloomEffect') or Instance.new('BloomEffect', Lg)
    e.Threshold = 1.3
    e.Intensity = 0.6
    e.Size = 28
  end
  do local e = Lg:FindFirstChildOfClass('Atmosphere') or Instance.new('Atmosphere', Lg)
    e.Density = 0.34
    e.Offset = 0.05
    e.Haze = 1.8
    e.Glare = 0.1
    e.Color = Color3.fromRGB(199,214,235)
    e.Decay = Color3.fromRGB(106,128,168)
  end
  local d = Lg:GetSunDirection()
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (-0.68, 0.70, 0.20) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
root.WorldPivot = CFrame.new(ROOT_OFFSET)
-- ===== pecas moveis (VFX_*) =====
local VFX = {
  ['VFX_GATE_DemonSlayer_Tsuba_1'] = {p = Vector3.new(-708.035,59.800,347.608), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -4.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_DemonSlayer_Tsuba_2'] = {p = Vector3.new(-709.123,55.000,351.708), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_DemonSlayer_Tsuba_3'] = {p = Vector3.new(-686.294,55.300,361.398), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -6.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_DemonSlayer_Tsuba_4'] = {p = Vector3.new(-684.101,60.100,357.766), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 7.000, bob = 0.600, rate = 0.000},
  ['VFX_SGCRAFT_Ring_1'] = {p = Vector3.new(-730.008,81.600,488.958), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 4.200, bob = 0.000, rate = 0.000},
  ['VFX_SGCRAFT_Ring_2'] = {p = Vector3.new(-730.008,81.600,488.958), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -3.400, bob = 0.000, rate = 0.000},
  ['VFX_SGDUN_MouthCrystal'] = {p = Vector3.new(-829.797,77.600,435.740), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 4.000, bob = 0.000, rate = 0.000},
  ['VFX_SGDUN_Portal'] = {p = Vector3.new(-855.525,59.600,424.819), a = Vector3.new(0.9210,0.0000,0.3910), rpm = 5.000, bob = 0.000, rate = 0.000},
  ['VFX_SGSUM_Ring_1'] = {p = Vector3.new(-771.559,86.200,735.304), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 2.000, bob = 0.000, rate = 0.000},
  ['VFX_SGSUM_Ring_2'] = {p = Vector3.new(-771.559,86.200,735.304), a = Vector3.new(0.0000,-1.0000,0.0000), rpm = 4.000, bob = 0.000, rate = 0.000},
  ['VFX_SGSUM_Ring_3'] = {p = Vector3.new(-771.559,86.200,735.304), a = Vector3.new(0.8420,0.5300,-0.1030), rpm = 6.000, bob = 0.000, rate = 0.000},
  ['VFX_SGSUM_Star'] = {p = Vector3.new(-771.559,86.200,735.304), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.000, rate = 0.000},
}
local nV = 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then local o = string.match(d.Name, '^(VFX_[%w_]-)__')
    local v = o and VFX[o]
    if v then local rel = root:GetPivot():ToObjectSpace(CFrame.new(v.p + ROOT_OFFSET))
      d:SetAttribute('pivot_rel', rel.Position); d:SetAttribute('axis_rel', v.a); d:SetAttribute('rpm', v.rpm)
      d:SetAttribute('bob', v.bob); d:SetAttribute('rate', v.rate); d:SetAttribute('cf0_rel', root:GetPivot():ToObjectSpace(d.CFrame))
      d:SetAttribute('movel_de', root.Name); CS:AddTag(d, 'IlhaMovel'); nV += 1 end end
end
do local SPS = game:GetService('StarterPlayer'):FindFirstChildOfClass('StarterPlayerScripts')
  local s = SPS:FindFirstChild('ILHA_NARUTO_Movel') or Instance.new('LocalScript'); s.Name = 'ILHA_NARUTO_Movel'
  s.Source = [==[
-- gerado pelo montar da ilha/portoes: gira/flutua as pecas com a tag IlhaMovel (so visual, no cliente).
-- Tudo e relativo ao pivo do Model dono (atributo movel_de): o Model pode ser movido com PivotTo.
local CS = game:GetService('CollectionService'); local RS = game:GetService('RunService')
local t0 = os.clock()
RS.RenderStepped:Connect(function()
  local t = os.clock() - t0
  for _, d in ipairs(CS:GetTagged('IlhaMovel')) do
    local dono = d:FindFirstAncestor(d:GetAttribute('movel_de') or '')
    local cf0, p, a = d:GetAttribute('cf0_rel'), d:GetAttribute('pivot_rel'), d:GetAttribute('axis_rel')
    if dono and cf0 and p and a and a.Magnitude > 0 then
      local ang = t * (d:GetAttribute('rpm') or 0) * math.pi / 30
      local amp, rate = d:GetAttribute('bob') or 0, d:GetAttribute('rate') or 0
      local bob
      if rate > 0 then  -- pilao: sobe devagar (70% do ciclo) e cai rapido (30%)
        local f = (t * rate) % 1
        bob = amp * ((f < 0.7) and (f / 0.7) or (1 - (f - 0.7) / 0.3))
      else
        bob = math.sin(t * 1.6 + p.X * 0.1) * amp
      end
      local r = CFrame.fromAxisAngle(a.Unit, ang)
      d.CFrame = dono:GetPivot() * (CFrame.new(p + Vector3.new(0, bob, 0)) * r * CFrame.new(-p) * cf0)
    end
  end
end)
]==]
  s.Parent = SPS end
print(string.format('%d pecas moveis marcadas (IlhaMovel)', nV))
-- ===== portoes de compra (LOCKED/UNLOCKED) =====
local nP = 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local k, part = string.match(d.Name, '^GATE_(%w+)_(%a+)')
    if k and (part == 'Barrier' or part == 'Lock' or part == 'OpenGlow') then
      if part == 'Barrier' then d.Transparency = 0.2 end   -- energia: da para ver o outro lado
      d:SetAttribute('gate', k); d:SetAttribute('gate_part', string.lower(part)); d:SetAttribute('t0', d.Transparency)
      if part == 'OpenGlow' then d.Transparency = 1 end
      CS:AddTag(d, 'PortaoCompra'); nP += 1 end
  elseif d:IsA('Part') and d.Parent == COLF then
    local k = string.match(d.Name, '^COL_Gate(%w-)Lock_')
    if k then d:SetAttribute('gate', k); d:SetAttribute('gate_part', 'lockcol'); CS:AddTag(d, 'PortaoCompra'); nP += 1
      local mdl = root:FindFirstChild('GATE_' .. k)   -- Model atomico do portao: bloqueio carrega junto
      if mdl and mdl:IsA('Model') then d.Parent = mdl end end
  end
end
do local RepS = game:GetService('ReplicatedStorage')
  local m = RepS:FindFirstChild('PortoesCompra') or Instance.new('ModuleScript'); m.Name = 'PortoesCompra'
  m.Source = [==[
-- gerado pelo montar da ilha/portoes. Estado de um portao de compra (DB, ShadowGarden, DemonSlayer, OnePiece,
-- OnePunchMan). No SERVIDOR vale para todos; num LocalScript vale so para aquele jogador (quem pagou).
--   require(game.ReplicatedStorage.PortoesCompra).Estado('DB', true)   -- desbloqueia
local CS = game:GetService('CollectionService')
local M = {}
local estado = {}   -- chave -> desbloqueado (sobrevive ao streaming: pecas que chegam depois recebem o estado)
local function aplicar(d)
  local chave = d:GetAttribute('gate'); local desb = estado[chave]
  if desb == nil then return end
  local p = d:GetAttribute('gate_part')
  if p == 'barrier' or p == 'lock' then d.Transparency = desb and 1 or (d:GetAttribute('t0') or 0)
  elseif p == 'openglow' then d.Transparency = desb and 0 or 1
  elseif p == 'lockcol' then d.CanCollide = not desb end
end
function M.Estado(chave, desbloqueado)
  estado[chave] = desbloqueado and true or false
  for _, d in ipairs(CS:GetTagged('PortaoCompra')) do if d:GetAttribute('gate') == chave then aplicar(d) end end
end
function M.Reaplicar() for _, d in ipairs(CS:GetTagged('PortaoCompra')) do aplicar(d) end end
CS:GetInstanceAddedSignal('PortaoCompra'):Connect(aplicar)
function M.Chaves() local s = {} for _, d in ipairs(CS:GetTagged('PortaoCompra')) do s[d:GetAttribute('gate')] = true end return s end
return M
]==]
  m.Parent = RepS end
print(string.format('%d pecas de portao de compra marcadas (PortaoCompra)', nP))
-- ===== guarda provisoria da ancora: a integracao da Ilha 2 APAGA estas pecas ao encostar a ponte seguinte =====
local nG = 0
for _, d in ipairs(root:GetDescendants()) do
  if (d:IsA('BasePart') or d:IsA('Model')) and (string.match(d.Name, '^SG_Exit_AnchorGuard') or string.match(d.Name, '^COL_SGAnchorGuard_')) then
    d:SetAttribute('next_island_guard', true)
    d:SetAttribute('removed_by', 'integracao da ilha Demon Slayer (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_DemonSlayer)')
    CS:AddTag(d, 'GuardaProximaIlha'); nG += 1 end
end
print(string.format('%d pecas da guarda da ancora marcadas (GuardaProximaIlha)', nG))
print(string.format('ILHA_SHADOWGARDEN montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
