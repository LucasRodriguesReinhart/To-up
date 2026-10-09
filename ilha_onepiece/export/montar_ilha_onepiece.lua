-- montar_ilha_onepiece.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 37998c7c
-- 1) Importe os FBX ILHA5_*_37998c.fbx (3D Importer) para dentro de workspace.ILHA_ONEPIECE. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script ILHA_ONEPIECE_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = '37998c7c'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o ilha5 INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('ILHA_ONEPIECE') or Instance.new('Model', workspace)
root.Name = 'ILHA_ONEPIECE'
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
  ['Bark_OP'] = {c = Color3.fromRGB(98,74,56), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Cliff_OP'] = {c = Color3.fromRGB(132,134,140), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Crevice'] = {c = Color3.fromRGB(66,72,90), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Dark'] = {c = Color3.fromRGB(94,98,108), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Face'] = {c = Color3.fromRGB(121,121,129), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Moss'] = {c = Color3.fromRGB(90,128,70), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Shade'] = {c = Color3.fromRGB(97,103,121), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Void'] = {c = Color3.fromRGB(38,40,48), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Black'] = {c = Color3.fromRGB(34,32,38), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Indigo'] = {c = Color3.fromRGB(44,52,96), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Red'] = {c = Color3.fromRGB(176,40,34), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Sail'] = {c = Color3.fromRGB(236,226,200), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Straw'] = {c = Color3.fromRGB(226,184,86), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_White'] = {c = Color3.fromRGB(236,232,222), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Crystal_SumPortal_Glow'] = {c = Color3.fromRGB(58,70,232), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Dirt_OP'] = {c = Color3.fromRGB(168,140,104), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Dirt_OP_Dark'] = {c = Color3.fromRGB(112,92,70), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Energy_OPM_Glow'] = {c = Color3.fromRGB(255,226,140), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_OP_Blossom'] = {c = Color3.fromRGB(240,150,198), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_OP_Deep'] = {c = Color3.fromRGB(206,108,164), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_OP_Light'] = {c = Color3.fromRGB(250,196,224), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Glass_OP_Lantern'] = {c = Color3.fromRGB(232,160,96), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_OP'] = {c = Color3.fromRGB(108,156,74), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_OP_B'] = {c = Color3.fromRGB(96,142,68), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_OP_Deep'] = {c = Color3.fromRGB(72,120,56), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_OP'] = {c = Color3.fromRGB(66,122,62), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_OP_Pine'] = {c = Color3.fromRGB(44,94,62), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Brass'] = {c = Color3.fromRGB(186,148,90), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_GateOPM_Red'] = {c = Color3.fromRGB(208,36,30), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold'] = {c = Color3.fromRGB(222,170,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold_OPOld'] = {c = Color3.fromRGB(176,134,62), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_OP_Gold'] = {c = Color3.fromRGB(220,172,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_OP_Iron'] = {c = Color3.fromRGB(70,70,74), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_OP_Steel'] = {c = Color3.fromRGB(176,184,196), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_Gold_Glow'] = {c = Color3.fromRGB(255,195,30), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_OPM_DarkGlass'] = {c = Color3.fromRGB(22,34,62), m = Enum.Material.Glass, t = 0.0, s = true, x = nil, w = nil},
  ['P_Red_Glow'] = {c = Color3.fromRGB(185,12,22), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Plaster_OP'] = {c = Color3.fromRGB(234,228,212), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_OP_Shop'] = {c = Color3.fromRGB(214,196,164), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_OP_Warm'] = {c = Color3.fromRGB(226,210,182), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Blue'] = {c = Color3.fromRGB(46,58,92), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Green'] = {c = Color3.fromRGB(58,104,84), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Red'] = {c = Color3.fromRGB(150,62,46), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Ridge'] = {c = Color3.fromRGB(30,36,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Shingle'] = {c = Color3.fromRGB(92,70,52), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Rope'] = {c = Color3.fromRGB(190,172,140), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_OP'] = {c = Color3.fromRGB(160,154,142), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_B'] = {c = Color3.fromRGB(148,144,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Court'] = {c = Color3.fromRGB(158,150,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Dark'] = {c = Color3.fromRGB(100,98,96), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Inlay'] = {c = Color3.fromRGB(150,128,98), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_OP_Path'] = {c = Color3.fromRGB(172,164,148), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Plaza'] = {c = Color3.fromRGB(164,156,140), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Wall'] = {c = Color3.fromRGB(160,154,144), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_Wall_Dark'] = {c = Color3.fromRGB(128,120,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light'] = {c = Color3.fromRGB(178,170,156), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Summon_Blue_Glow'] = {c = Color3.fromRGB(80,150,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Summon_OPStar_Glow'] = {c = Color3.fromRGB(196,120,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Window_OP_Warm'] = {c = Color3.fromRGB(250,212,160), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wood_OP_Dark'] = {c = Color3.fromRGB(66,46,34), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_OP_Hull'] = {c = Color3.fromRGB(104,66,42), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_OP_Lacquer'] = {c = Color3.fromRGB(186,42,34), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_OP_Mid'] = {c = Color3.fromRGB(128,92,60), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
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
local FBX = {[1]='ILHA5_02_TERRAIN_37998c.fbx', [2]='ILHA5_03_PLAZA_37998c.fbx', [3]='ILHA5_04_CASTLE_37998c.fbx', [4]='ILHA5_05_CAPITAL_37998c.fbx', [5]='ILHA5_06_SUMMON_37998c.fbx', [6]='ILHA5_07_WATER_37998c.fbx', [7]='ILHA5_08_NEXT_ISLAND_37998c.fbx', [8]='ILHA5_08_PURCHASE_GATES_37998c.fbx', [9]='ILHA5_09_PROPS_37998c.fbx', [10]='ILHA5_10_VEGETATION_37998c.fbx', [11]='ILHA5_12_VFX_HELPERS_37998c.fbx', [12]='ILHA5_16_HARBOR_37998c.fbx', [13]='ILHA5_17_LANDMARKS_37998c.fbx', [14]='ILHA5_18_ENTRY_37998c.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['OP_Ter_CastleRock__Cliff_OP_Crevice']={-2324.666,115.15,1937.678,43.011,41.5,31.759,1,true,'Cliff_OP_Crevice','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Dark']={-2323.27,114.75,1935.825,41.72,42.3,29.927,1,true,'Cliff_OP_Dark','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Face']={-2324.534,124.323,1937.12,41.141,20.869,30.122,1,true,'Cliff_OP_Face','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Moss']={-2324.505,118.891,1937.447,43.332,34.317,32.222,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Shade']={-2323.435,114.847,1936.372,41.848,39.693,30.799,1,true,'Cliff_OP_Shade','',''},
  ['OP_Ter_CastleRock__Grass_OP_Deep']={-2325.383,135.975,1938.586,41.806,0.15,30.269,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_CastleRock__Stone_OP']={-2326.152,133.42,1940.119,11.24,4.84,10.552,1,false,'Stone_OP','',''},
  ['OP_Ter_CastleWall__Stone_OP_Dark']={-2292.906,117.401,2003.665,58.649,37.598,82.853,1,true,'Stone_OP_Dark','',''},
  ['OP_Ter_CastleWall__Stone_OP_Path']={-2292.932,129.825,2003.663,58.596,12.75,82.849,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_CastleWall__Stone_OP_Wall']={-2292.549,117.126,2003.924,57.52,36.908,81.955,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Cliff__Cliff_OP_Crevice']={-2289.427,91.537,1849.115,563.99,113.074,543.205,1,true,'Cliff_OP_Crevice','',''},
  ['OP_Ter_Cliff__Cliff_OP_Dark']={-2286.585,46.75,1833.594,576.058,113.5,582.128,1,true,'Cliff_OP_Dark','',''},
  ['OP_Ter_Cliff__Cliff_OP_Face']={-2285.415,90.537,1852.014,569.639,115.074,545.287,1,true,'Cliff_OP_Face','',''},
  ['OP_Ter_Cliff__Cliff_OP_Moss']={-2286.641,96.097,1849.008,571.92,105.106,544.695,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Cliff__Cliff_OP_Shade']={-2286.585,92.35,1847.532,576.058,114.7,542.71,1,true,'Cliff_OP_Shade','',''},
  ['OP_Ter_Cliff__Dirt_OP_Dark']={-2011.13,87.317,1783.56,4.679,0.633,15.878,1,false,'Dirt_OP_Dark','',''},
  ['OP_Ter_Cliff__Grass_OP_Deep']={-2285.677,115.786,1849.875,568.041,67.827,541.705,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Cliff__Stone_OP']={-2354.358,66.8,1642.02,210.012,50.2,197.785,1,true,'Stone_OP','',''},
  ['OP_Ter_Cliff__Stone_OP_Path']={-2355.146,66.675,1640.442,212.275,50.05,195.725,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_Cliff__Stone_OP_Wall']={-2355.641,62.442,1639.506,213.264,53.885,193.852,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Ground__Cliff_OP_Moss']={-2287.325,96.0,1830.912,560.1,108.0,572.779,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Ground__Cliff_OP_Shade']={-2286.067,89.9,1829.541,563.395,119.8,557.932,1,true,'Cliff_OP_Shade','',''},
  ['OP_Ter_Ground__Dirt_OP']={-2289.098,88.75,1829.674,546.685,94.6,558.198,1,false,'Dirt_OP','',''},
  ['OP_Ter_Ground__Dirt_OP_Dark']={-2264.978,90.25,1873.495,521.217,10.3,247.17,1,false,'Dirt_OP_Dark','',''},
  ['OP_Ter_Ground__Grass_OP']={-2290.317,94.2,1863.401,543.753,12.0,490.745,1,false,'Grass_OP','',''},
  ['OP_Ter_Ground__Grass_OP_B']={-2286.778,94.2,1865.63,541.932,12.0,483.345,1,false,'Grass_OP_B','',''},
  ['OP_Ter_Ground__Grass_OP_Deep_g-4_2']={-2340.903,96.0,1890.082,442.061,108.0,454.312,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Ground__Grass_OP_Deep_g-4_3']={-2287.208,72.9,1796.354,561.127,61.8,504.928,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Ground__Stone_OP_g-3_3']={-2376.549,42.11,1648.306,150.567,0.42,196.442,1,true,'Stone_OP','',''},
  ['OP_Ter_Ground__Stone_OP_g-2_3']={-2336.846,42.11,1644.55,193.829,0.42,179.413,1,true,'Stone_OP','',''},
  ['OP_Ter_Ground__Stone_OP_B_g-3_3']={-2378.278,42.11,1647.932,153.003,0.42,190.307,1,true,'Stone_OP_B','',''},
  ['OP_Ter_Ground__Stone_OP_B_g-2_3']={-2336.412,42.11,1644.196,195.547,0.42,170.838,1,true,'Stone_OP_B','',''},
  ['OP_Ter_Ground__Stone_OP_Path']={-2281.567,89.05,1820.691,347.981,94.3,531.894,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Dark']={-2204.382,89.995,1756.799,224.007,4.33,120.632,1,true,'Stone_OP_Dark','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Path']={-2115.953,92.15,1800.066,47.701,0.4,34.072,1,false,'Stone_OP_Path','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Wall_g-2_2']={-2204.223,89.995,1756.347,224.604,4.33,121.018,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Wall_g-1_2']={-2149.987,89.995,1775.102,53.019,4.33,36.732,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Rocks__Cliff_OP_Crevice']={-2294.855,71.825,2004.794,516.264,91.63,228.262,1,true,'Cliff_OP_Crevice','',''},
  ['OP_Ter_Rocks__Cliff_OP_Dark']={-2501.913,92.562,1617.771,49.881,25.123,35.833,1,false,'Cliff_OP_Dark','',''},
  ['OP_Ter_Rocks__Cliff_OP_Face']={-2365.264,103.294,1878.977,712.68,154.568,536.577,1,true,'Cliff_OP_Face','',''},
  ['OP_Ter_Rocks__Cliff_OP_Moss']={-2366.274,90.929,1873.597,714.1,103.142,545.927,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Rocks__Cliff_OP_Shade']={-2365.63,88.5,1879.589,717.064,129.0,538.592,1,true,'Cliff_OP_Shade','',''},
  ['OP_Ter_Rocks__Grass_OP_Deep']={-2364.822,114.583,1872.534,709.499,135.191,521.415,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Walls__Cliff_OP_Face']={-2269.808,95.675,1845.825,522.655,106.949,495.804,1,true,'Cliff_OP_Face','',''},
  ['OP_Ter_Walls__Cliff_OP_Moss']={-2269.741,107.081,1845.783,522.591,85.139,495.773,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Walls__Cliff_OP_Shade']={-2269.772,94.39,1845.829,522.561,106.181,495.795,1,true,'Cliff_OP_Shade','',''},
  ['OP_Ter_Walls__Dirt_OP_Dark']={-2288.298,88.85,1851.486,372.575,95.1,468.55,1,false,'Dirt_OP_Dark','',''},
  ['OP_Ter_Walls__Grass_OP_Deep']={-2270.364,117.675,1846.145,523.836,64.05,496.497,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Walls__Stone_OP_Dark']={-2231.016,88.65,1814.934,415.762,94.1,408.684,1,true,'Stone_OP_Dark','',''},
  ['OP_Ter_Walls__Stone_OP_Path']={-2231.186,100.535,1815.039,416.724,71.33,408.887,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-3_1']={-2357.422,111.725,1855.718,78.987,47.71,128.739,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-3_2']={-2367.65,78.225,1727.629,130.87,26.71,130.92,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-3_3']={-2363.425,66.625,1682.534,150.83,49.91,143.523,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-2_0']={-2203.62,111.725,1909.26,304.173,47.71,185.641,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-2_3']={-2213.252,64.625,1654.808,183.929,45.91,75.75,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-1_0']={-2100.119,93.325,1936.249,154.082,12.51,166.088,1,false,'Stone_OP_Wall','',''},
  ['OP_Plz_M2_Borda__Cloth_OP_Indigo']={-2247.936,105.738,1825.795,254.3,3.687,241.102,2,true,'Cloth_OP_Indigo','',''},
  ['OP_Plz_M2_Borda__Cloth_OP_White']={-2247.935,104.065,1825.754,254.35,11.89,241.4,2,true,'Cloth_OP_White','',''},
  ['OP_Plz_M2_Borda__Glass_OP_Lantern']={-2246.894,97.768,1826.118,139.665,2.935,174.747,2,false,'Glass_OP_Lantern','',''},
  ['OP_Plz_M2_Borda__Metal_OP_Gold']={-2247.932,109.725,1825.767,254.563,2.85,241.609,2,true,'Metal_OP_Gold','',''},
  ['OP_Plz_M2_Borda__Metal_OP_Iron']={-2247.93,96.773,1825.751,255.243,7.933,242.441,2,true,'Metal_OP_Iron','',''},
  ['OP_Plz_M2_Borda__Roof_OP_Ridge']={-2298.735,99.878,1900.718,37.85,0.724,27.413,2,true,'Roof_OP_Ridge','',''},
  ['OP_Plz_M2_Borda__Stone_OP']={-2244.392,95.91,1823.4,262.281,7.82,246.971,2,true,'Stone_OP','',''},
  ['OP_Plz_M2_Borda__Stone_OP_B']={-2247.04,95.41,1824.57,257.756,6.82,245.62,2,true,'Stone_OP_B','',''},
  ['OP_Plz_M2_Borda__Stone_OP_Path']={-2204.958,94.93,1756.296,221.733,1.4,119.374,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_M2_Borda__Stone_OP_Wall']={-2204.971,93.5,1756.289,221.891,2.9,119.596,2,true,'Stone_OP_Wall','',''},
  ['OP_Plz_M2_Borda__Window_OP_Warm']={-2298.735,98.94,1900.718,35.984,1.18,25.547,2,false,'Window_OP_Warm','',''},
  ['OP_Plz_M2_Borda__Wood_OP_Dark']={-2247.932,101.48,1825.767,254.443,17.64,241.492,2,true,'Wood_OP_Dark','',''},
  ['OP_Plz_M2_Faixa__Stone_OP']={-2210.412,92.125,1766.995,178.624,0.45,126.061,2,true,'Stone_OP','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_B']={-2198.97,92.125,1775.32,166.057,0.45,116.917,2,true,'Stone_OP_B','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Inlay']={-2247.113,92.09,1826.994,25.994,0.38,25.994,2,false,'Stone_OP_Inlay','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Path']={-2199.341,92.125,1775.139,137.325,0.45,145.492,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Plaza_g-2_1']={-2214.952,92.125,1812.753,86.717,0.45,50.876,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Plaza_g-2_2']={-2223.309,92.125,1746.543,184.44,0.45,99.948,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Plaza_g-1_1']={-2147.386,92.125,1821.909,65.65,0.45,67.569,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_Mureta__Stone_OP_B']={-2228.78,93.16,1820.035,188.513,2.22,182.9,2,true,'Stone_OP_B','',''},
  ['OP_Plz_Mureta__Stone_OP_Path']={-2251.353,94.53,1817.302,234.059,2.2,190.379,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_Mureta__Stone_OP_Wall']={-2251.394,93.5,1817.273,234.184,2.9,190.455,2,true,'Stone_OP_Wall','',''},
  ['OP_Plz_Piso__Stone_OP']={-2254.38,92.125,1837.993,249.585,0.45,229.971,2,true,'Stone_OP','',''},
  ['OP_Plz_Piso__Stone_OP_B']={-2251.426,92.125,1840.132,250.784,0.45,225.072,2,true,'Stone_OP_B','',''},
  ['OP_Plz_Piso__Stone_OP_Path_g-3_1']={-2340.119,92.125,1846.117,78.107,0.45,115.996,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_Piso__Stone_OP_Path_g-2_1']={-2245.181,92.125,1838.588,237.31,0.45,229.469,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_Piso__Stone_OP_Plaza_g-3_1']={-2338.356,92.125,1843.876,74.494,0.45,110.666,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_Piso__Stone_OP_Plaza_g-2_1']={-2244.223,92.125,1837.847,229.714,0.45,224.011,2,true,'Stone_OP_Plaza','',''},
  ['OP_Cas_Adro__Cloth_OP_Indigo']={-2324.964,124.879,1937.916,31.15,10.158,21.657,3,false,'Cloth_OP_Indigo','','OP_Cas'},
  ['OP_Cas_Adro__Cloth_OP_Red']={-2306.765,104.75,1912.186,45.574,1.2,32.215,3,true,'Cloth_OP_Red','','OP_Cas'},
  ['OP_Cas_Adro__Cloth_OP_White']={-2324.964,126.199,1937.916,31.504,14.598,21.804,3,false,'Cloth_OP_White','','OP_Cas'},
  ['OP_Cas_Adro__Glass_OP_Lantern']={-2305.91,113.235,1954.301,47.344,17.45,116.506,3,false,'Glass_OP_Lantern','','OP_Cas'},
  ['OP_Cas_Adro__Metal_OP_Gold']={-2315.375,122.789,1925.553,52.819,21.378,48.209,3,true,'Metal_OP_Gold','','OP_Cas'},
  ['OP_Cas_Adro__Metal_OP_Iron']={-2295.637,116.149,1933.26,90.854,35.098,73.441,3,true,'Metal_OP_Iron','','OP_Cas'},
  ['OP_Cas_Adro__Roof_OP_Blue']={-2289.253,112.704,1935.835,84.741,7.529,74.923,3,true,'Roof_OP_Blue','','OP_Cas'},
  ['OP_Cas_Adro__Roof_OP_Ridge']={-2288.88,112.855,1934.203,82.25,11.136,75.125,3,true,'Roof_OP_Ridge','','OP_Cas'},
  ['OP_Cas_Adro__Stone_OP']={-2289.488,115.155,1975.648,78.712,46.51,158.086,3,true,'Stone_OP','','OP_Cas'},
  ['OP_Cas_Adro__Stone_OP_B']={-2291.218,107.237,1956.557,57.37,30.673,113.503,3,true,'Stone_OP_B','','OP_Cas'},
  ['OP_Cas_Adro__Stone_OP_Dark']={-2294.74,114.824,1975.79,85.525,45.847,157.866,3,true,'Stone_OP_Dark','','OP_Cas'},
  ['OP_Cas_Adro__Stone_OP_Path']={-2294.595,115.78,1975.971,85.844,46.3,157.467,3,true,'Stone_OP_Path','','OP_Cas'},
  ['OP_Cas_Adro__Stone_OP_Wall']={-2294.466,117.824,1982.955,85.784,39.847,140.886,3,true,'Stone_OP_Wall','','OP_Cas'},
  ['OP_Cas_Adro__Wood_OP_Dark']={-2294.085,115.999,1934.629,94.405,34.798,77.335,3,true,'Wood_OP_Dark','','OP_Cas'},
  ['OP_Cas_Adro__Wood_OP_Lacquer']={-2309.676,106.6,1916.769,37.417,16.2,28.156,3,true,'Wood_OP_Lacquer','','OP_Cas'},
  ['OP_Cas_Court__Glass_OP_Lantern']={-2338.311,141.084,1957.239,20.722,1.372,14.933,3,false,'Glass_OP_Lantern','','OP_Cas'},
  ['OP_Cas_Court__Metal_OP_Gold']={-2330.593,140.29,1946.64,85.92,0.78,62.543,3,true,'Metal_OP_Gold','','OP_Cas'},
  ['OP_Cas_Court__Metal_OP_Iron']={-2317.721,137.1,2051.618,16.814,1.0,12.517,3,false,'Metal_OP_Iron','','OP_Cas'},
  ['OP_Cas_Court__Plaster_OP_g-3_1']={-2407.406,146.324,1954.113,67.647,20.847,90.63,3,true,'Plaster_OP','','OP_Cas'},
  ['OP_Cas_Court__Plaster_OP_g-2_0']={-2361.246,144.7,2002.647,159.967,17.6,169.158,3,true,'Plaster_OP','','OP_Cas'},
  ['OP_Cas_Court__Roof_OP_Blue_g-3_-1']={-2341.252,144.688,2066.724,83.147,7.941,40.881,3,false,'Roof_OP_Blue','','OP_Cas'},
  ['OP_Cas_Court__Roof_OP_Blue_g-3_0']={-2360.728,146.828,1991.572,162.918,15.184,148.868,3,true,'Roof_OP_Blue','','OP_Cas'},
  ['OP_Cas_Court__Roof_OP_Blue_g-3_1']={-2383.615,148.467,1914.514,25.136,17.661,16.421,3,false,'Roof_OP_Blue','','OP_Cas'},
  ['OP_Cas_Court__Roof_OP_Ridge']={-2359.821,150.45,1995.746,162.982,17.601,180.778,3,true,'Roof_OP_Ridge','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP']={-2359.389,133.763,1996.324,166.311,20.666,182.36,3,true,'Stone_OP','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP_B']={-2358.011,133.763,1995.61,162.201,20.666,181.972,3,true,'Stone_OP_B','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP_Court']={-2364.439,136.12,2000.612,155.351,0.44,171.34,3,true,'Stone_OP_Court','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP_Dark']={-2339.355,130.992,1949.925,99.231,11.557,87.29,3,true,'Stone_OP_Dark','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP_Path']={-2361.17,136.81,1997.292,161.18,1.08,178.781,3,true,'Stone_OP_Path','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP_Plaza']={-2354.289,136.305,1996.54,93.669,0.07,124.409,3,true,'Stone_OP_Plaza','','OP_Cas'},
  ['OP_Cas_Court__Stone_OP_Wall']={-2333.736,130.0,1949.403,114.847,13.6,89.392,3,true,'Stone_OP_Wall','','OP_Cas'},
  ['OP_Cas_Court__Wood_OP_Dark_g-3_-1']={-2356.422,142.38,2056.855,113.791,11.759,60.619,3,false,'Wood_OP_Dark','','OP_Cas'},
  ['OP_Cas_Court__Wood_OP_Dark_g-3_0']={-2365.405,145.263,1989.613,153.336,17.327,144.95,3,true,'Wood_OP_Dark','','OP_Cas'},
  ['OP_Cas_Court__Wood_OP_Dark_g-3_1']={-2406.63,147.048,1967.531,71.114,19.697,123.319,3,true,'Wood_OP_Dark','','OP_Cas'},
  ['OP_Cas_Court__Wood_OP_Dark_g-2_0']={-2302.051,144.308,2020.274,46.527,14.216,90.275,3,true,'Wood_OP_Dark','','OP_Cas'},
  ['OP_Cas_Court__Wood_OP_Lacquer']={-2330.593,138.08,1946.647,86.001,3.96,62.638,3,true,'Wood_OP_Lacquer','','OP_Cas'},
  ['OP_Cas_Keep__Cloth_OP_Indigo']={-2366.743,142.8,1997.845,1.471,1.576,1.147,3,false,'Cloth_OP_Indigo','','OP_Cas'},
  ['OP_Cas_Keep__Cloth_OP_White']={-2358.386,142.85,1985.706,21.408,7.1,25.916,3,false,'Cloth_OP_White','','OP_Cas'},
  ['OP_Cas_Keep__Glass_OP_Lantern']={-2358.386,145.45,1983.207,21.515,0.76,21.025,3,false,'Glass_OP_Lantern','','OP_Cas'},
  ['OP_Cas_Keep__Metal_OP_Gold']={-2355.466,179.579,1979.91,41.303,83.758,48.235,3,true,'Metal_OP_Gold','','OP_Cas'},
  ['OP_Cas_Keep__Metal_OP_Iron']={-2351.566,142.35,1974.341,33.42,11.7,37.013,3,false,'Metal_OP_Iron','','OP_Cas'},
  ['OP_Cas_Keep__Plaster_OP']={-2354.945,174.417,1980.995,72.257,76.435,69.801,3,true,'Plaster_OP','','OP_Cas'},
  ['OP_Cas_Keep__Plaster_OP_Warm']={-2354.945,143.225,1980.995,66.686,11.65,64.23,3,true,'Plaster_OP_Warm','','OP_Cas'},
  ['OP_Cas_Keep__Roof_OP_Blue']={-2354.945,179.971,1980.995,85.66,66.528,83.696,3,true,'Roof_OP_Blue','','OP_Cas'},
  ['OP_Cas_Keep__Roof_OP_Ridge']={-2354.945,183.491,1980.995,87.424,64.793,85.46,3,true,'Roof_OP_Ridge','','OP_Cas'},
  ['OP_Cas_Keep__Stone_OP']={-2354.676,138.05,1980.995,78.896,4.44,76.979,3,true,'Stone_OP','','OP_Cas'},
  ['OP_Cas_Keep__Stone_OP_B']={-2351.074,138.4,1966.877,32.883,5.0,47.666,3,true,'Stone_OP_B','','OP_Cas'},
  ['OP_Cas_Keep__Stone_OP_Dark']={-2355.963,137.95,1980.995,77.4,4.64,70.686,3,true,'Stone_OP_Dark','','OP_Cas'},
  ['OP_Cas_Keep__Stone_OP_Path']={-2354.945,138.575,1980.995,75.041,5.35,72.6,3,true,'Stone_OP_Path','','OP_Cas'},
  ['OP_Cas_Keep__Stone_OP_Wall']={-2354.943,137.95,1980.985,75.276,4.64,72.22,3,true,'Stone_OP_Wall','','OP_Cas'},
  ['OP_Cas_Keep__Window_OP_Warm']={-2354.945,143.5,1980.779,61.9,3.0,56.718,3,false,'Window_OP_Warm','','OP_Cas'},
  ['OP_Cas_Keep__Wood_OP_Dark']={-2354.945,174.342,1980.995,86.448,76.885,84.484,3,true,'Wood_OP_Dark','','OP_Cas'},
  ['OP_Cas_Keep__Wood_OP_Lacquer']={-2354.969,197.23,1980.995,38.494,3.56,37.709,3,true,'Wood_OP_Lacquer','','OP_Cas'},
  ['OP_Cas_Keep__Wood_OP_Mid']={-2354.945,166.05,1980.995,66.932,59.0,64.476,3,true,'Wood_OP_Mid','','OP_Cas'},
  ['OP_Tree_Bloom__Flower_OP_Blossom_g-4_0']={-2454.482,228.833,1954.014,47.969,59.046,67.018,3,false,'Flower_OP_Blossom','','OP_Tree'},
  ['OP_Tree_Bloom__Flower_OP_Blossom_g-3_0']={-2361.341,233.263,1998.64,145.201,103.959,124.627,3,false,'Flower_OP_Blossom','','OP_Tree'},
  ['OP_Tree_Bloom__Flower_OP_Deep_g-4_0']={-2454.3,226.249,1954.014,48.333,59.407,67.018,3,false,'Flower_OP_Deep','','OP_Tree'},
  ['OP_Tree_Bloom__Flower_OP_Deep_g-3_0']={-2361.554,228.062,1998.64,145.627,100.259,124.627,3,false,'Flower_OP_Deep','','OP_Tree'},
  ['OP_Tree_Bloom__Flower_OP_Light_g-4_0']={-2454.3,231.383,1954.014,48.333,60.625,67.018,3,false,'Flower_OP_Light','','OP_Tree'},
  ['OP_Tree_Bloom__Flower_OP_Light_g-3_0']={-2361.554,235.741,1998.64,145.627,101.702,124.627,3,false,'Flower_OP_Light','','OP_Tree'},
  ['OP_Tree_Branches__Bark_OP_g-4_0']={-2448.486,209.473,1960.122,36.724,85.633,47.089,3,true,'Bark_OP','','OP_Tree'},
  ['OP_Tree_Branches__Bark_OP_g-3_0']={-2369.644,217.322,1990.833,126.752,95.379,76.391,3,true,'Bark_OP','','OP_Tree'},
  ['OP_Tree_Trunk__Bark_OP_g-4_0']={-2446.275,187.846,1968.208,41.44,137.651,68.161,3,true,'Bark_OP','','OP_Tree'},
  ['OP_Tree_Trunk__Bark_OP_g-3_0']={-2369.055,193.925,1985.847,132.571,131.116,101.507,3,true,'Bark_OP','','OP_Tree'},
  ['OP_Tree_Trunk__Bark_OP_g-2_0']={-2300.435,201.768,2030.501,9.237,47.156,15.748,3,false,'Bark_OP','','OP_Tree'},
  ['OP_Tree_Trunk__Cliff_OP']={-2444.231,121.148,1980.984,30.786,12.633,45.874,3,false,'Cliff_OP','','OP_Tree'},
  ['OP_Tree_Trunk__Cliff_OP_Moss']={-2444.231,127.65,1980.984,30.786,8.965,45.874,3,false,'Cliff_OP_Moss','','OP_Tree'},
  ['OP_Cap_Bairro__Cloth_OP_Indigo']={-2080.76,95.275,1785.984,91.087,7.15,78.529,4,false,'Cloth_OP_Indigo','',''},
  ['OP_Cap_Bairro__Cloth_OP_Red']={-2088.495,94.01,1770.133,75.677,4.62,24.378,4,false,'Cloth_OP_Red','',''},
  ['OP_Cap_Bairro__Cloth_OP_White']={-2080.76,94.19,1785.988,90.681,4.98,78.136,4,false,'Cloth_OP_White','',''},
  ['OP_Cap_Bairro__Dirt_OP']={-2087.599,88.2,1775.846,136.333,0.6,134.259,4,false,'Dirt_OP','',''},
  ['OP_Cap_Bairro__Glass_OP_Lantern']={-2052.473,94.27,1780.898,3.695,0.48,2.909,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_Bairro__Metal_OP_Iron']={-2084.001,92.56,1791.994,82.371,5.92,65.03,4,false,'Metal_OP_Iron','',''},
  ['OP_Cap_Bairro__Plaster_OP']={-2087.563,101.501,1769.627,116.831,23.402,103.484,4,false,'Plaster_OP','',''},
  ['OP_Cap_Bairro__Plaster_OP_Warm']={-2085.531,97.691,1764.754,119.78,15.783,96.804,4,false,'Plaster_OP_Warm','',''},
  ['OP_Cap_Bairro__Roof_OP_Blue']={-2085.674,104.638,1770.145,127.008,16.663,117.311,4,false,'Roof_OP_Blue','',''},
  ['OP_Cap_Bairro__Roof_OP_Green']={-2086.74,106.203,1772.005,60.407,15.1,67.936,4,false,'Roof_OP_Green','',''},
  ['OP_Cap_Bairro__Roof_OP_Ridge']={-2085.653,105.923,1766.31,114.218,18.233,111.25,4,false,'Roof_OP_Ridge','',''},
  ['OP_Cap_Bairro__Stone_OP']={-2091.688,88.6,1770.696,133.203,1.6,111.031,4,false,'Stone_OP','',''},
  ['OP_Cap_Bairro__Stone_OP_B']={-2084.362,88.6,1778.065,94.375,1.6,72.757,4,false,'Stone_OP_B','',''},
  ['OP_Cap_Bairro__Stone_OP_Path']={-2096.023,89.7,1775.518,130.914,3.6,92.352,4,false,'Stone_OP_Path','',''},
  ['OP_Cap_Bairro__Stone_OP_Plaza']={-2092.123,88.125,1779.334,100.009,0.45,79.673,4,false,'Stone_OP_Plaza','',''},
  ['OP_Cap_Bairro__Stone_OP_Wall']={-2034.76,89.42,1766.933,8.5,2.8,9.417,4,false,'Stone_OP_Wall','',''},
  ['OP_Cap_Bairro__Window_OP_Warm']={-2085.959,97.0,1773.056,116.093,14.4,102.337,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_Bairro__Wood_OP_Dark']={-2085.674,100.836,1770.145,127.008,25.032,117.311,4,false,'Wood_OP_Dark','',''},
  ['OP_Cap_Bairro__Wood_OP_Mid']={-2085.84,100.146,1770.996,119.196,21.193,109.32,4,false,'Wood_OP_Mid','',''},
  ['OP_Cap_Leste__Cloth_OP_Indigo']={-2207.293,95.325,1703.852,126.066,7.25,89.151,4,true,'Cloth_OP_Indigo','',''},
  ['OP_Cap_Leste__Cloth_OP_Red']={-2205.326,94.95,1699.002,117.404,6.5,102.988,4,true,'Cloth_OP_Red','',''},
  ['OP_Cap_Leste__Cloth_OP_White']={-2207.293,94.24,1703.854,125.683,5.08,88.747,4,true,'Cloth_OP_White','',''},
  ['OP_Cap_Leste__Dirt_OP']={-2231.189,88.2,1671.794,101.652,0.6,109.047,4,false,'Dirt_OP','',''},
  ['OP_Cap_Leste__Glass_OP_Lantern']={-2215.176,95.972,1696.281,97.766,3.885,97.607,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_Leste__Metal_OP_Gold']={-2197.185,120.518,1710.935,10.265,5.773,9.128,4,false,'Metal_OP_Gold','',''},
  ['OP_Cap_Leste__Metal_OP_Iron']={-2205.488,94.625,1699.282,116.167,10.05,102.626,4,true,'Metal_OP_Iron','',''},
  ['OP_Cap_Leste__Plaster_OP']={-2209.755,105.871,1698.415,129.468,31.943,124.402,4,true,'Plaster_OP','',''},
  ['OP_Cap_Leste__Plaster_OP_Shop']={-2192.026,97.031,1719.814,94.951,14.263,83.441,4,true,'Plaster_OP_Shop','',''},
  ['OP_Cap_Leste__Plaster_OP_Warm']={-2233.867,98.726,1650.673,83.104,13.953,50.308,4,true,'Plaster_OP_Warm','',''},
  ['OP_Cap_Leste__Roof_OP_Blue']={-2226.237,103.62,1671.198,74.242,23.64,98.302,4,true,'Roof_OP_Blue','',''},
  ['OP_Cap_Leste__Roof_OP_Green']={-2158.133,105.68,1748.909,34.826,17.944,33.696,4,false,'Roof_OP_Green','',''},
  ['OP_Cap_Leste__Roof_OP_Red']={-2231.837,110.416,1686.476,96.889,24.053,78.144,4,true,'Roof_OP_Red','',''},
  ['OP_Cap_Leste__Roof_OP_Ridge']={-2210.46,110.601,1698.352,141.252,27.59,136.585,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_Leste__Stone_OP']={-2231.09,90.24,1698.726,175.422,4.88,127.959,4,true,'Stone_OP','',''},
  ['OP_Cap_Leste__Stone_OP_B']={-2236.766,90.24,1693.562,167.207,4.88,137.197,4,true,'Stone_OP_B','',''},
  ['OP_Cap_Leste__Stone_OP_Path']={-2250.471,89.7,1684.31,128.174,3.6,93.56,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_Leste__Stone_OP_Plaza']={-2254.098,88.125,1690.266,113.454,0.45,87.502,4,true,'Stone_OP_Plaza','',''},
  ['OP_Cap_Leste__Stone_OP_Wall']={-2264.209,89.42,1642.894,8.275,2.8,10.805,4,false,'Stone_OP_Wall','',''},
  ['OP_Cap_Leste__Window_OP_Warm']={-2210.145,101.6,1693.229,120.411,23.4,131.93,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_Leste__Wood_OP_Dark']={-2210.302,105.156,1694.102,139.96,33.673,144.109,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_Leste__Wood_OP_Mid']={-2209.985,93.475,1693.835,130.901,7.85,135.432,4,true,'Wood_OP_Mid','',''},
  ['OP_Cap_M2_Escadaria__Cloth_OP_Red']={-2164.518,94.9,1709.036,36.718,1.2,24.11,4,false,'Cloth_OP_Red','',''},
  ['OP_Cap_M2_Escadaria__Glass_OP_Lantern']={-2172.014,93.155,1722.367,51.771,3.97,50.833,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_M2_Escadaria__Metal_OP_Iron']={-2172.09,92.89,1722.455,50.95,6.52,50.026,4,true,'Metal_OP_Iron','',''},
  ['OP_Cap_M2_Escadaria__Roof_OP_Ridge']={-2172.777,94.968,1723.339,52.112,6.003,50.756,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_M2_Escadaria__Stone_OP_B']={-2175.685,90.953,1727.572,57.96,6.106,59.234,4,true,'Stone_OP_B','',''},
  ['OP_Cap_M2_Escadaria__Stone_OP_Dark']={-2189.36,90.286,1743.456,30.018,4.772,25.518,4,false,'Stone_OP_Dark','',''},
  ['OP_Cap_M2_Escadaria__Stone_OP_Path']={-2188.385,91.498,1743.206,32.373,5.603,27.854,4,false,'Stone_OP_Path','',''},
  ['OP_Cap_M2_Escadaria__Window_OP_Warm']={-2185.425,91.44,1738.894,24.95,1.08,17.779,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_M2_Escadaria__Wood_OP_Dark']={-2172.152,92.865,1722.505,52.22,9.33,51.282,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_M2_Lojas__Cloth_OP_Indigo']={-2159.967,95.275,1703.384,38.624,7.15,37.27,4,false,'Cloth_OP_Indigo','',''},
  ['OP_Cap_M2_Lojas__Cloth_OP_Red']={-2159.469,95.2,1702.338,42.204,7.0,40.568,4,false,'Cloth_OP_Red','',''},
  ['OP_Cap_M2_Lojas__Cloth_OP_White']={-2159.967,94.19,1703.384,38.223,4.98,36.864,4,false,'Cloth_OP_White','',''},
  ['OP_Cap_M2_Lojas__Glass_OP_Lantern']={-2160.044,97.575,1700.64,41.107,1.68,37.224,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_M2_Lojas__Metal_OP_Gold']={-2142.594,104.19,1703.634,10.438,0.78,13.439,4,false,'Metal_OP_Gold','',''},
  ['OP_Cap_M2_Lojas__Metal_OP_Iron']={-2159.821,96.95,1701.489,43.106,6.4,39.974,4,false,'Metal_OP_Iron','',''},
  ['OP_Cap_M2_Lojas__Plaster_OP']={-2153.396,104.107,1695.465,67.182,24.815,56.357,4,true,'Plaster_OP','',''},
  ['OP_Cap_M2_Lojas__Plaster_OP_Shop']={-2162.386,99.102,1703.979,85.165,18.603,72.272,4,true,'Plaster_OP_Shop','',''},
  ['OP_Cap_M2_Lojas__Roof_OP_Blue']={-2162.456,106.909,1703.87,96.421,20.411,80.451,4,true,'Roof_OP_Blue','',''},
  ['OP_Cap_M2_Lojas__Roof_OP_Ridge']={-2162.456,110.059,1703.554,98.552,18.018,66.717,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_M2_Lojas__Stone_OP']={-2162.387,88.5,1703.671,87.508,1.4,73.999,4,true,'Stone_OP','',''},
  ['OP_Cap_M2_Lojas__Stone_OP_B']={-2162.387,90.19,1709.282,85.951,4.78,61.687,4,true,'Stone_OP_B','',''},
  ['OP_Cap_M2_Lojas__Stone_OP_Dark']={-2159.713,90.255,1702.347,39.117,4.79,37.198,4,false,'Stone_OP_Dark','',''},
  ['OP_Cap_M2_Lojas__Window_OP_Warm']={-2162.597,97.3,1706.284,78.409,15.0,54.244,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_M2_Lojas__Wood_OP_Dark']={-2162.456,102.882,1703.87,97.22,27.565,80.451,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_M2_Lojas__Wood_OP_Lacquer']={-2142.57,102.08,1703.645,10.567,3.76,13.541,4,false,'Wood_OP_Lacquer','',''},
  ['OP_Cap_M2_Lojas__Wood_OP_Mid']={-2160.142,94.925,1703.746,45.321,10.75,42.376,4,true,'Wood_OP_Mid','',''},
  ['OP_Cap_M2_Rua__Stone_OP']={-2167.328,88.125,1713.017,64.511,0.45,60.14,4,true,'Stone_OP','',''},
  ['OP_Cap_M2_Rua__Stone_OP_B']={-2168.015,88.125,1704.115,44.032,0.45,54.107,4,true,'Stone_OP_B','',''},
  ['OP_Cap_M2_Rua__Stone_OP_Path']={-2166.697,88.125,1714.85,60.267,0.45,68.376,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_M2_Rua__Stone_OP_Plaza']={-2166.812,88.125,1712.149,57.513,0.45,65.915,4,true,'Stone_OP_Plaza','',''},
  ['OP_Cap_NE__Cloth_OP_Indigo']={-2423.091,100.615,1813.304,68.55,4.67,77.118,4,true,'Cloth_OP_Indigo','',''},
  ['OP_Cap_NE__Cloth_OP_Red']={-2401.143,100.275,1836.458,17.716,7.57,33.396,4,false,'Cloth_OP_Red','',''},
  ['OP_Cap_NE__Cloth_OP_White']={-2423.086,100.45,1813.304,68.158,3.841,76.717,4,true,'Cloth_OP_White','',''},
  ['OP_Cap_NE__Dirt_OP']={-2423.135,92.2,1798.705,102.514,0.6,117.812,4,false,'Dirt_OP','',''},
  ['OP_Cap_NE__Glass_OP_Lantern']={-2410.958,96.532,1822.138,7.425,1.156,10.085,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_NE__Metal_OP_Gold']={-2418.82,101.66,1818.075,34.83,9.921,27.527,4,true,'Metal_OP_Gold','',''},
  ['OP_Cap_NE__Metal_OP_Iron']={-2411.4,96.098,1831.607,36.669,6.483,43.297,4,true,'Metal_OP_Iron','',''},
  ['OP_Cap_NE__Plaster_OP']={-2421.742,105.54,1813.372,90.772,19.581,99.918,4,true,'Plaster_OP','',''},
  ['OP_Cap_NE__Plaster_OP_Warm']={-2422.331,101.986,1805.075,94.941,12.472,91.521,4,true,'Plaster_OP_Warm','',''},
  ['OP_Cap_NE__Roof_OP_Blue']={-2438.195,104.355,1810.608,70.157,6.07,87.4,4,true,'Roof_OP_Blue','',''},
  ['OP_Cap_NE__Roof_OP_Red']={-2420.48,103.965,1810.913,97.639,23.831,112.922,4,true,'Roof_OP_Red','',''},
  ['OP_Cap_NE__Roof_OP_Ridge']={-2423.03,105.034,1810.917,94.152,24.268,114.537,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_NE__Stone_OP']={-2422.301,95.459,1811.712,96.111,7.318,105.581,4,true,'Stone_OP','',''},
  ['OP_Cap_NE__Stone_OP_B']={-2420.214,95.459,1805.712,90.847,7.318,95.137,4,true,'Stone_OP_B','',''},
  ['OP_Cap_NE__Stone_OP_Path']={-2419.057,92.4,1802.875,86.323,1.0,59.007,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_NE__Stone_OP_Plaza']={-2399.117,92.125,1812.583,49.62,0.45,39.606,4,true,'Stone_OP_Plaza','',''},
  ['OP_Cap_NE__Window_OP_Warm']={-2422.481,100.825,1811.107,80.446,13.35,100.63,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_NE__Wood_OP_Dark']={-2422.467,104.165,1810.913,101.613,22.631,112.922,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_NE__Wood_OP_Lacquer']={-2413.08,97.075,1820.464,26.264,8.95,23.526,4,false,'Wood_OP_Lacquer','',''},
  ['OP_Cap_NE__Wood_OP_Mid']={-2422.301,98.42,1811.323,93.801,10.08,104.049,4,true,'Wood_OP_Mid','',''},
  ['OP_Cap_Oeste__Cloth_OP_Indigo']={-2138.498,98.9,1890.839,89.098,8.1,126.966,4,true,'Cloth_OP_Indigo','',''},
  ['OP_Cap_Oeste__Cloth_OP_Red']={-2135.719,98.075,1886.677,85.118,6.45,114.755,4,true,'Cloth_OP_Red','',''},
  ['OP_Cap_Oeste__Cloth_OP_Straw']={-2153.957,94.75,1938.429,13.918,0.2,12.334,4,false,'Cloth_OP_Straw','',''},
  ['OP_Cap_Oeste__Cloth_OP_White']={-2138.647,98.24,1890.833,88.432,5.08,126.571,4,true,'Cloth_OP_White','',''},
  ['OP_Cap_Oeste__Dirt_OP']={-2127.302,92.2,1901.364,125.26,0.6,157.185,4,false,'Dirt_OP','',''},
  ['OP_Cap_Oeste__Glass_OP_Lantern']={-2137.691,98.271,1886.72,81.237,5.487,114.73,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_Oeste__Metal_OP_Gold']={-2105.154,96.422,1927.615,57.331,0.78,73.514,4,false,'Metal_OP_Gold','',''},
  ['OP_Cap_Oeste__Metal_OP_Iron']={-2136.835,98.175,1891.041,87.549,9.15,122.742,4,true,'Metal_OP_Iron','',''},
  ['OP_Cap_Oeste__Plaster_OP']={-2129.891,107.459,1903.236,113.857,27.118,148.655,4,true,'Plaster_OP','',''},
  ['OP_Cap_Oeste__Plaster_OP_Shop']={-2119.034,102.633,1886.877,94.765,18.466,118.461,4,true,'Plaster_OP_Shop','',''},
  ['OP_Cap_Oeste__Plaster_OP_Warm']={-2145.869,100.129,1926.177,85.178,12.459,103.921,4,true,'Plaster_OP_Warm','',''},
  ['OP_Cap_Oeste__Roof_OP_Blue']={-2131.292,109.729,1903.529,81.088,19.367,95.997,4,true,'Roof_OP_Blue','',''},
  ['OP_Cap_Oeste__Roof_OP_Green']={-2129.891,111.138,1903.236,124.139,20.86,158.937,4,true,'Roof_OP_Green','',''},
  ['OP_Cap_Oeste__Roof_OP_Ridge_g-1_0']={-2156.076,111.1,1947.873,50.594,20.187,71.266,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_Oeste__Roof_OP_Ridge_g-1_1']={-2129.848,112.0,1897.61,125.827,21.987,149.459,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_Oeste__Stone_OP']={-2136.527,94.85,1896.956,158.62,13.9,164.705,4,true,'Stone_OP','',''},
  ['OP_Cap_Oeste__Stone_OP_B']={-2140.736,94.983,1892.168,149.478,14.165,154.353,4,true,'Stone_OP_B','',''},
  ['OP_Cap_Oeste__Stone_OP_Dark']={-2141.291,94.131,1892.793,148.5,12.462,151.854,4,true,'Stone_OP_Dark','',''},
  ['OP_Cap_Oeste__Stone_OP_Path_g-2_0']={-2194.715,97.1,1947.947,42.059,10.4,43.383,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_Oeste__Stone_OP_Path_g-1_0']={-2142.224,92.35,1954.322,72.503,0.9,73.555,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_Oeste__Stone_OP_Path_g-1_1']={-2112.286,91.498,1869.037,117.347,5.603,107.98,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_Oeste__Stone_OP_Plaza']={-2129.649,92.125,1899.034,139.535,0.45,168.287,4,true,'Stone_OP_Plaza','',''},
  ['OP_Cap_Oeste__Window_OP_Warm']={-2129.939,100.825,1902.431,111.965,14.35,135.134,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_Oeste__Wood_OP_Dark']={-2129.692,106.459,1903.036,124.538,29.418,159.336,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_Oeste__Wood_OP_Lacquer']={-2105.154,94.02,1927.615,57.353,4.88,73.536,4,false,'Wood_OP_Lacquer','',''},
  ['OP_Cap_Oeste__Wood_OP_Mid']={-2129.957,97.44,1902.892,116.643,10.52,150.523,4,true,'Wood_OP_Mid','',''},
  ['OP_Cap_OesteFundo__Cloth_OP_Indigo']={-2116.566,104.99,1939.226,138.332,13.42,126.644,4,false,'Cloth_OP_Indigo','',''},
  ['OP_Cap_OesteFundo__Cloth_OP_Red']={-2223.545,106.27,2015.626,3.634,1.2,2.848,4,false,'Cloth_OP_Red','',''},
  ['OP_Cap_OesteFundo__Cloth_OP_White']={-2116.565,103.65,1939.222,137.928,10.24,126.252,4,false,'Cloth_OP_White','',''},
  ['OP_Cap_OesteFundo__Dirt_OP']={-2082.193,92.2,1936.124,123.44,0.6,156.926,4,false,'Dirt_OP','',''},
  ['OP_Cap_OesteFundo__Dirt_OP_Dark']={-2050.349,92.6,1911.239,22.745,0.5,31.686,4,false,'Dirt_OP_Dark','',''},
  ['OP_Cap_OesteFundo__Glass_OP_Lantern']={-2223.545,106.27,2015.626,3.695,0.48,2.909,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_OesteFundo__Metal_OP_Iron']={-2203.116,104.57,2008.903,43.579,5.94,15.372,4,false,'Metal_OP_Iron','',''},
  ['OP_Cap_OesteFundo__Plaster_OP']={-2142.999,111.769,1980.326,224.967,32.037,220.985,4,false,'Plaster_OP','',''},
  ['OP_Cap_OesteFundo__Plaster_OP_Warm']={-2123.389,106.466,1980.085,193.744,21.433,225.315,4,false,'Plaster_OP_Warm','',''},
  ['OP_Cap_OesteFundo__Roof_OP_Blue']={-2123.389,109.626,1980.085,203.468,16.213,235.04,4,false,'Roof_OP_Blue','',''},
  ['OP_Cap_OesteFundo__Roof_OP_Green_g-2_0']={-2216.474,119.124,2020.692,85.349,18.426,63.122,4,false,'Roof_OP_Green','',''},
  ['OP_Cap_OesteFundo__Roof_OP_Green_g-1_0']={-2149.448,109.97,1993.173,219.403,34.588,194.274,4,false,'Roof_OP_Green','',''},
  ['OP_Cap_OesteFundo__Roof_OP_Ridge']={-2140.403,116.204,1980.085,239.102,27.119,236.646,4,false,'Roof_OP_Ridge','',''},
  ['OP_Cap_OesteFundo__Stone_OP']={-2141.0,97.1,1980.085,231.309,10.6,227.658,4,false,'Stone_OP','',''},
  ['OP_Cap_OesteFundo__Stone_OP_B']={-2166.215,97.1,2000.651,179.323,10.6,163.938,4,false,'Stone_OP_B','',''},
  ['OP_Cap_OesteFundo__Stone_OP_Path']={-2141.397,96.225,1954.275,195.2,8.25,185.137,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_OesteFundo__Stone_OP_Plaza']={-2205.747,100.125,2013.589,54.461,0.45,75.646,4,false,'Stone_OP_Plaza','',''},
  ['OP_Cap_OesteFundo__Window_OP_Warm']={-2140.433,106.8,1974.99,224.131,20.8,196.091,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_OesteFundo__Wood_OP_Dark_g-2_-1']={-2215.003,113.982,2066.948,81.0,25.764,61.315,4,false,'Wood_OP_Dark','',''},
  ['OP_Cap_OesteFundo__Wood_OP_Dark_g-2_0']={-2213.931,114.379,2023.089,90.435,27.117,68.721,4,false,'Wood_OP_Dark','',''},
  ['OP_Cap_OesteFundo__Wood_OP_Dark_g-1_-1']={-2162.746,112.065,2066.754,40.717,21.93,47.11,4,false,'Wood_OP_Dark','',''},
  ['OP_Cap_OesteFundo__Wood_OP_Dark_g-1_0']={-2111.184,107.615,1962.712,143.941,30.83,193.724,4,false,'Wood_OP_Dark','',''},
  ['OP_Cap_OesteFundo__Wood_OP_Dark_g0_1']={-2038.284,100.826,1882.864,33.258,17.253,40.598,4,false,'Wood_OP_Dark','',''},
  ['OP_Cap_OesteFundo__Wood_OP_Mid']={-2141.0,102.196,1980.085,228.998,18.928,225.348,4,false,'Wood_OP_Mid','',''},
  ['OP_Sum_Cloth__Cloth_OP_Indigo']={-2385.037,110.4,1727.951,17.434,14.2,24.791,5,false,'Cloth_OP_Indigo','','OP_Sum'},
  ['OP_Sum_Cloth__Wood_OP_Dark']={-2384.489,118.0,1728.289,18.911,0.6,26.714,5,false,'Wood_OP_Dark','','OP_Sum'},
  ['OP_Sum_Garden__Bark_OP']={-2398.276,92.949,1712.384,55.409,10.049,87.19,5,true,'Bark_OP','','OP_Sum'},
  ['OP_Sum_Garden__Dirt_OP']={-2398.999,88.265,1712.291,60.783,0.33,92.805,5,false,'Dirt_OP','','OP_Sum'},
  ['OP_Sum_Garden__Leaf_OP']={-2398.351,93.867,1712.24,59.949,11.381,91.522,5,false,'Leaf_OP','','OP_Sum'},
  ['OP_Sum_Garden__Leaf_OP_Pine']={-2398.513,95.126,1712.15,61.396,8.423,93.105,5,false,'Leaf_OP_Pine','','OP_Sum'},
  ['OP_Sum_Glow__Crystal_SumPortal_Glow']={-2387.949,105.525,1726.127,11.273,26.75,13.779,5,false,'Crystal_SumPortal_Glow','','OP_Sum'},
  ['OP_Sum_Glow__Glass_OP_Lantern']={-2386.49,115.955,1726.916,15.7,1.91,18.367,5,false,'Glass_OP_Lantern','','OP_Sum'},
  ['OP_Sum_Glow__Summon_Blue_Glow']={-2387.29,107.6,1726.504,12.795,31.1,9.628,5,false,'Summon_Blue_Glow','','OP_Sum'},
  ['OP_Sum_Glow__Summon_OPStar_Glow']={-2388.018,106.333,1726.127,11.24,21.834,13.951,5,false,'Summon_OPStar_Glow','','OP_Sum'},
  ['OP_Sum_Metal__Metal_Gold_OPOld']={-2386.216,109.895,1728.924,24.98,36.79,28.445,5,true,'Metal_Gold_OPOld','','OP_Sum'},
  ['OP_Sum_Paving__Stone_OP']={-2376.662,88.33,1732.72,65.067,0.34,56.923,5,true,'Stone_OP','','OP_Sum'},
  ['OP_Sum_Paving__Stone_OP_B']={-2377.998,88.33,1730.032,64.041,0.34,54.052,5,true,'Stone_OP_B','','OP_Sum'},
  ['OP_Sum_Paving__Stone_OP_Dark']={-2372.115,88.34,1737.025,8.0,0.32,8.0,5,false,'Stone_OP_Dark','','OP_Sum'},
  ['OP_Sum_Paving__Stone_OP_Path']={-2377.92,88.33,1728.218,109.542,0.34,79.64,5,true,'Stone_OP_Path','','OP_Sum'},
  ['OP_Sum_Rail__Metal_Gold_OPOld']={-2384.964,92.005,1703.492,107.783,6.75,96.686,5,true,'Metal_Gold_OPOld','','OP_Sum'},
  ['OP_Sum_Rail__Wood_OP_Lacquer']={-2384.949,91.1,1703.544,107.532,6.0,96.51,5,true,'Wood_OP_Lacquer','','OP_Sum'},
  ['OP_Sum_Sphere_Frame__Metal_Gold_OPOld']={-2387.679,136.495,1726.127,18.935,23.61,18.935,5,false,'Metal_Gold_OPOld','','OP_Sum'},
  ['OP_Sum_Sphere_Frame__Summon_Blue_Glow']={-2387.679,145.5,1726.127,1.179,1.4,1.262,5,false,'Summon_Blue_Glow','','OP_Sum'},
  ['OP_Sum_Stone__Glass_OP_Lantern']={-2367.436,94.212,1739.995,40.221,3.232,35.591,5,false,'Glass_OP_Lantern','','OP_Sum'},
  ['OP_Sum_Stone__Stone_OP']={-2379.764,106.47,1737.822,84.197,36.98,58.313,5,true,'Stone_OP','','OP_Sum'},
  ['OP_Sum_Stone__Stone_OP_B']={-2371.39,92.186,1717.2,61.644,8.572,84.078,5,true,'Stone_OP_B','','OP_Sum'},
  ['OP_Sum_Stone__Stone_OP_Dark']={-2383.77,106.58,1716.193,92.301,37.76,101.702,5,true,'Stone_OP_Dark','','OP_Sum'},
  ['OP_Sum_Stone__Stone_OP_Path']={-2363.751,91.04,1744.608,50.969,4.987,43.318,5,true,'Stone_OP_Path','','OP_Sum'},
  ['OP_Water_Stone__Cliff_OP_Dark']={-2249.93,64.375,1868.274,507.621,68.75,254.507,6,true,'Cliff_OP_Dark','',''},
  ['OP_Water_Stone__Cliff_OP_Shade']={-2251.737,35.865,1770.471,514.096,11.73,56.839,6,true,'Cliff_OP_Shade','',''},
  ['OP_Water_Stone__Metal_OP_Iron']={-2032.31,92.56,1823.583,9.263,0.92,7.004,6,false,'Metal_OP_Iron','',''},
  ['OP_Water_Stone__Stone_OP_Dark']={-2265.605,92.325,1873.577,522.882,14.45,248.289,6,true,'Stone_OP_Dark','',''},
  ['OP_Water_Stone__Stone_OP_Path']={-2266.901,94.325,1873.229,528.308,12.55,251.513,6,true,'Stone_OP_Path','',''},
  ['OP_Water_Stone__Stone_OP_Wall_g-4_1']={-2480.206,90.825,1824.692,101.698,3.95,68.938,6,true,'Stone_OP_Wall','',''},
  ['OP_Water_Stone__Stone_OP_Wall_g-3_1']={-2415.326,94.4,1846.664,231.458,11.2,198.384,6,true,'Stone_OP_Wall','',''},
  ['OP_Water_Stone__Stone_OP_Wall_g-1_0']={-2080.344,91.06,1891.378,155.195,12.52,215.214,6,false,'Stone_OP_Wall','',''},
  ['OP_Water_Stone__Wood_OP_Dark']={-2033.873,91.232,1822.591,13.437,4.736,10.615,6,false,'Wood_OP_Dark','',''},
  ['OP_Exit_AnchorGuard__Wood_OP_Mid']={-2552.018,89.842,1679.838,7.77,3.476,20.274,7,false,'Wood_OP_Mid','','OP_Exit_AnchorGuard'},
  ['OP_Exit_Bridge__Glass_OP_Lantern']={-2486.187,92.984,1701.211,131.644,1.372,66.32,7,false,'Glass_OP_Lantern','',''},
  ['OP_Exit_Bridge__Metal_OP_Gold']={-2488.304,82.755,1701.588,135.946,24.719,65.634,7,true,'Metal_OP_Gold','',''},
  ['OP_Exit_Bridge__Roof_OP_Ridge']={-2466.068,93.461,1710.221,92.905,2.622,49.8,7,true,'Roof_OP_Ridge','',''},
  ['OP_Exit_Bridge__Stone_OP_Wall']={-2546.67,91.943,1681.784,13.723,8.106,30.602,7,false,'Stone_OP_Wall','',''},
  ['OP_Exit_Bridge__Wood_OP_Dark']={-2466.068,85.129,1710.221,92.015,17.31,48.91,7,true,'Wood_OP_Dark','',''},
  ['OP_Exit_Bridge__Wood_OP_Lacquer']={-2466.511,80.975,1710.068,92.121,23.55,48.376,7,true,'Wood_OP_Lacquer','',''},
  ['OP_Exit_Stone__Stone_OP_Dark']={-2487.747,59.6,1702.498,138.664,67.2,69.059,7,true,'Stone_OP_Dark','',''},
  ['OP_Exit_Stone__Stone_OP_Path']={-2488.853,87.38,1701.875,136.469,2.24,64.72,7,true,'Stone_OP_Path','',''},
  ['OP_Exit_Stone__Stone_OP_Wall']={-2487.538,65.1,1702.729,138.442,55.4,68.879,7,true,'Stone_OP_Wall','',''},
  ['GATE_OnePunchMan_Barrier__Energy_OPM_Glow']={-2530.696,97.242,1687.598,5.749,13.312,12.659,8,false,'Energy_OPM_Glow','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Barrier__P_Gold_Glow']={-2530.696,97.2,1687.598,5.942,18.0,15.206,8,false,'P_Gold_Glow','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Metal_Brass']={-2526.279,93.5,1689.206,13.661,9.7,31.711,8,false,'Metal_Brass','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Metal_Dark']={-2528.689,103.2,1687.461,25.777,30.0,32.624,8,false,'Metal_Dark','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Metal_GateOPM_Red']={-2526.859,100.15,1689.206,21.563,23.9,32.574,8,false,'Metal_GateOPM_Red','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Metal_Gold']={-2529.818,102.242,1688.075,23.309,23.584,33.674,8,false,'Metal_Gold','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__P_Gold_Glow']={-2529.519,99.95,1687.718,23.769,19.5,31.762,8,false,'P_Gold_Glow','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__P_OPM_DarkGlass']={-2532.472,101.95,1687.461,17.811,23.5,32.224,8,false,'P_OPM_DarkGlass','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__P_Red_Glow']={-2530.696,110.135,1685.956,7.521,17.33,22.672,8,false,'P_Red_Glow','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Stone_Dark']={-2527.928,91.025,1688.607,21.486,5.65,34.703,8,false,'Stone_Dark','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Stone_Wall_Dark']={-2527.266,88.2,1688.847,24.623,1.2,38.309,8,false,'Stone_Wall_Dark','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Frame__Stone_Wall_Light']={-2528.75,101.05,1689.081,25.112,26.9,35.293,8,false,'Stone_Wall_Light','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Lock__Energy_OPM_Glow']={-2530.696,96.48,1687.598,2.461,3.4,4.075,8,false,'Energy_OPM_Glow','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Lock__Metal_Dark']={-2530.696,96.28,1687.598,2.614,1.0,1.359,8,false,'Metal_Dark','','GATE_OnePunchMan'},
  ['GATE_OnePunchMan_Lock__Metal_Gold']={-2530.696,97.442,1687.598,3.256,4.625,3.794,8,false,'Metal_Gold','','GATE_OnePunchMan'},
  ['OP_Prop_Cidade__Cloth_OP_Indigo']={-2098.646,94.947,1849.039,64.703,7.527,235.674,9,true,'Cloth_OP_Indigo','',''},
  ['OP_Prop_Cidade__Cloth_OP_Red']={-2247.49,94.378,1733.74,348.943,6.39,171.035,9,true,'Cloth_OP_Red','',''},
  ['OP_Prop_Cidade__Cloth_OP_Straw']={-2145.97,92.725,1782.46,192.165,8.45,239.536,9,true,'Cloth_OP_Straw','',''},
  ['OP_Prop_Cidade__Cloth_OP_White']={-2240.881,94.692,1807.921,348.961,7.017,317.968,9,true,'Cloth_OP_White','',''},
  ['OP_Prop_Cidade__Glass_OP_Lantern']={-2149.848,96.02,1805.809,154.729,6.83,263.138,9,false,'Glass_OP_Lantern','',''},
  ['OP_Prop_Cidade__Metal_OP_Gold']={-2270.186,96.566,1763.797,291.189,6.568,111.519,9,true,'Metal_OP_Gold','',''},
  ['OP_Prop_Cidade__Metal_OP_Iron']={-2232.565,94.973,1805.8,366.357,11.933,262.349,9,true,'Metal_OP_Iron','',''},
  ['OP_Prop_Cidade__Roof_OP_Shingle']={-2240.658,97.0,1805.809,388.33,6.879,265.005,9,true,'Roof_OP_Shingle','',''},
  ['OP_Prop_Cidade__Stone_OP_B']={-2158.722,90.6,1805.795,137.606,4.8,263.755,9,true,'Stone_OP_B','',''},
  ['OP_Prop_Cidade__Stone_OP_Dark']={-2240.838,91.45,1807.748,385.905,6.6,320.031,9,true,'Stone_OP_Dark','',''},
  ['OP_Prop_Cidade__Stone_OP_Path']={-2240.22,91.4,1827.588,384.298,6.2,152.757,9,true,'Stone_OP_Path','',''},
  ['OP_Prop_Cidade__Window_OP_Warm']={-2158.727,97.14,1805.809,136.97,5.18,263.138,9,false,'Window_OP_Warm','',''},
  ['OP_Prop_Cidade__Wood_OP_Dark_g-1_0']={-2107.514,96.189,1944.402,41.434,7.402,46.156,9,false,'Wood_OP_Dark','',''},
  ['OP_Prop_Cidade__Wood_OP_Dark_g-1_1']={-2078.124,94.315,1847.708,60.927,11.15,115.769,9,false,'Wood_OP_Dark','',''},
  ['OP_Prop_Cidade__Wood_OP_Dark_g-1_2']={-2240.245,93.974,1773.976,386.977,10.972,254.223,9,true,'Wood_OP_Dark','',''},
  ['OP_Prop_Cidade__Wood_OP_Mid_g-1_1']={-2087.36,93.505,1878.819,78.334,9.41,177.126,9,false,'Wood_OP_Mid','',''},
  ['OP_Prop_Cidade__Wood_OP_Mid_g-1_2']={-2248.208,91.99,1736.259,367.011,6.98,178.595,9,true,'Wood_OP_Mid','',''},
  ['OP_Prop_Plz_Borda__Cloth_OP_Indigo']={-2246.122,104.894,1824.537,203.328,2.0,150.474,9,true,'Cloth_OP_Indigo','',''},
  ['OP_Prop_Plz_Borda__Cloth_OP_White']={-2246.122,103.065,1824.537,203.443,9.89,150.805,9,true,'Cloth_OP_White','',''},
  ['OP_Prop_Plz_Borda__Glass_OP_Lantern']={-2250.76,98.94,1835.459,232.759,0.59,195.271,9,false,'Glass_OP_Lantern','',''},
  ['OP_Prop_Plz_Borda__Metal_OP_Gold']={-2246.122,108.725,1824.537,200.518,0.85,146.471,9,true,'Metal_OP_Gold','',''},
  ['OP_Prop_Plz_Borda__Metal_OP_Iron']={-2250.76,96.773,1835.459,231.952,7.933,194.499,9,true,'Metal_OP_Iron','',''},
  ['OP_Prop_Plz_Borda__Roof_OP_Ridge']={-2250.76,99.878,1835.459,234.625,0.724,197.137,9,true,'Roof_OP_Ridge','',''},
  ['OP_Prop_Plz_Borda__Stone_OP_B']={-2250.769,92.595,1835.449,233.367,1.19,195.897,9,true,'Stone_OP_B','',''},
  ['OP_Prop_Plz_Borda__Window_OP_Warm']={-2250.76,98.94,1835.459,232.759,1.18,195.271,9,false,'Window_OP_Warm','',''},
  ['OP_Prop_Plz_Borda__Wood_OP_Dark_g-3_1']={-2343.426,100.3,1807.249,58.604,16.0,159.707,9,true,'Wood_OP_Dark','',''},
  ['OP_Prop_Plz_Borda__Wood_OP_Dark_g-2_0']={-2229.455,95.995,1935.005,92.253,7.39,27.703,9,true,'Wood_OP_Dark','',''},
  ['OP_Prop_Plz_Borda__Wood_OP_Dark_g-1_1']={-2152.746,100.3,1888.188,37.651,16.0,52.876,9,true,'Wood_OP_Dark','',''},
  ['OP_Prop_Plz_Borda__Wood_OP_Mid']={-2255.763,93.9,1838.092,234.091,0.2,221.647,9,true,'Wood_OP_Mid','',''},
  ['OP_Veg_Castelo__Flower_OP_Blossom']={-2269.991,128.513,2008.061,19.026,7.769,21.585,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Castelo__Flower_OP_Light']={-2269.991,130.727,2008.061,19.026,5.295,21.585,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Castelo__Leaf_OP']={-2408.612,111.055,2007.476,290.18,83.622,210.974,10,false,'Leaf_OP','',''},
  ['OP_Veg_Castelo__Leaf_OP_Pine']={-2411.034,139.014,1988.153,283.439,52.665,169.672,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Castelo__Wood_OP_Dark']={-2407.139,140.724,1999.218,282.925,46.909,138.528,10,true,'Wood_OP_Dark','',''},
  ['OP_Veg_Entrada__Flower_OP_Blossom']={-2171.306,104.635,1662.749,173.367,24.193,77.194,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Entrada__Flower_OP_Deep']={-2131.85,108.645,1660.984,94.453,12.855,73.664,10,false,'Flower_OP_Deep','',''},
  ['OP_Veg_Entrada__Flower_OP_Light']={-2171.746,105.82,1663.182,172.488,23.196,76.328,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Entrada__Leaf_OP']={-2156.914,77.126,1686.219,124.04,51.121,166.958,10,false,'Leaf_OP','',''},
  ['OP_Veg_Entrada__Leaf_OP_Pine']={-2146.991,80.044,1685.998,140.569,42.147,166.917,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Entrada__Wood_OP_Dark']={-2167.184,89.77,1660.23,176.17,35.659,84.159,10,true,'Wood_OP_Dark','',''},
  ['OP_Veg_Fundo__Flower_OP_Blossom']={-2437.794,117.978,1862.502,72.107,40.961,136.627,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Fundo__Flower_OP_Light']={-2437.615,119.966,1861.875,71.744,39.451,135.371,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Fundo__Leaf_OP']={-2482.11,97.624,1884.661,136.139,82.936,111.063,10,false,'Leaf_OP','',''},
  ['OP_Veg_Fundo__Leaf_OP_Pine']={-2484.615,106.243,1883.432,130.387,65.294,117.021,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Fundo__Wood_OP_Dark']={-2475.12,114.632,1865.49,135.842,45.582,137.925,10,true,'Wood_OP_Dark','',''},
  ['OP_Veg_FundoNorte__Flower_OP_Blossom']={-2533.976,128.128,1935.025,13.47,6.139,12.275,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_FundoNorte__Flower_OP_Light']={-2533.956,129.88,1935.025,11.492,4.074,12.275,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_FundoNorte__Leaf_OP']={-2505.857,124.795,1964.452,91.385,118.487,113.614,10,false,'Leaf_OP','',''},
  ['OP_Veg_FundoNorte__Leaf_OP_Pine']={-2580.91,128.35,1959.168,234.312,104.599,103.448,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_FundoNorte__Wood_OP_Dark']={-2580.795,124.255,1963.376,228.874,105.189,95.933,10,false,'Wood_OP_Dark','',''},
  ['OP_Veg_Leste__Flower_OP_Blossom']={-2286.42,75.098,1706.6,206.99,56.598,284.904,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Leste__Flower_OP_Light']={-2286.667,76.896,1706.6,206.498,54.442,284.904,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Leste__Leaf_OP']={-2396.292,80.178,1705.269,369.409,68.663,254.582,10,false,'Leaf_OP','',''},
  ['OP_Veg_Leste__Leaf_OP_Pine']={-2377.149,79.112,1681.706,399.215,65.978,292.454,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Leste__Wood_OP_Dark']={-2376.248,75.763,1691.943,394.086,68.832,307.048,10,true,'Wood_OP_Dark','',''},
  ['OP_Veg_Oeste__Flower_OP_Blossom']={-2118.927,100.059,1936.719,51.023,7.277,89.095,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Oeste__Flower_OP_Light']={-2118.927,101.328,1936.719,51.023,6.178,89.095,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Oeste__Leaf_OP']={-2175.951,122.809,2011.473,316.432,84.525,216.828,10,false,'Leaf_OP','',''},
  ['OP_Veg_Oeste__Leaf_OP_Pine']={-2177.303,117.689,2013.067,314.338,86.378,213.88,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Oeste__Wood_OP_Dark']={-2163.622,107.713,2005.061,282.648,33.048,220.899,10,false,'Wood_OP_Dark','',''},
  ['OP_Veg_Promontorio__Flower_OP_Blossom']={-2425.085,97.734,1700.487,241.414,9.329,55.59,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Promontorio__Flower_OP_Light']={-2425.085,99.507,1700.487,241.414,7.735,55.59,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Promontorio__Leaf_OP']={-2542.101,89.997,1768.19,69.439,62.256,136.391,10,false,'Leaf_OP','',''},
  ['OP_Veg_Promontorio__Leaf_OP_Pine']={-2538.729,102.061,1738.801,60.129,28.908,180.969,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Promontorio__Wood_OP_Dark']={-2436.28,101.418,1737.265,255.71,28.269,173.049,10,true,'Wood_OP_Dark','',''},
  ['OP_Veg_Sudoeste__Flower_OP_Blossom']={-2067.212,99.53,1791.497,104.836,14.135,173.296,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_Sudoeste__Flower_OP_Light']={-2066.566,100.905,1791.47,103.545,13.339,173.243,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_Sudoeste__Leaf_OP']={-2085.841,76.513,1776.881,173.814,46.058,292.859,10,false,'Leaf_OP','',''},
  ['OP_Veg_Sudoeste__Leaf_OP_Pine']={-2086.47,80.219,1777.411,172.286,53.373,289.302,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_Sudoeste__Wood_OP_Dark']={-2060.785,78.993,1792.365,109.134,54.079,165.25,10,false,'Wood_OP_Dark','',''},
  ['OP_Veg_TerracoAlto__Flower_OP_Blossom']={-2199.198,109.492,2041.554,79.924,10.212,132.705,10,false,'Flower_OP_Blossom','',''},
  ['OP_Veg_TerracoAlto__Flower_OP_Light']={-2199.198,110.884,2041.554,79.924,9.38,132.705,10,false,'Flower_OP_Light','',''},
  ['OP_Veg_TerracoAlto__Leaf_OP_g-2_-1']={-2190.594,104.003,2041.634,159.425,24.908,172.521,10,false,'Leaf_OP','',''},
  ['OP_Veg_TerracoAlto__Leaf_OP_g-1_0']={-2140.317,101.887,2017.321,74.685,18.724,64.883,10,false,'Leaf_OP','',''},
  ['OP_Veg_TerracoAlto__Leaf_OP_Pine']={-2185.906,103.077,2041.162,168.887,24.429,168.948,10,false,'Leaf_OP_Pine','',''},
  ['OP_Veg_TerracoAlto__Wood_OP_Dark']={-2185.161,105.009,2045.699,113.003,11.641,152.862,10,false,'Wood_OP_Dark','',''},
  ['VFX_GATE_OnePunchMan_Star_1__Metal_Gold']={-2531.101,103.8,1701.285,1.398,3.1,3.036,11,false,'Metal_Gold','',''},
  ['VFX_GATE_OnePunchMan_Star_1__P_Red_Glow']={-2531.101,103.8,1701.285,1.161,1.8,1.89,11,false,'P_Red_Glow','',''},
  ['VFX_GATE_OnePunchMan_Star_2__Metal_Gold']={-2526.949,99.0,1702.158,1.399,3.1,3.036,11,false,'Metal_Gold','',''},
  ['VFX_GATE_OnePunchMan_Star_2__P_Red_Glow']={-2526.949,99.0,1702.158,1.161,1.8,1.89,11,false,'P_Red_Glow','',''},
  ['VFX_GATE_OnePunchMan_Star_3__Metal_Gold']={-2518.467,99.3,1678.853,1.398,3.1,3.036,11,false,'Metal_Gold','',''},
  ['VFX_GATE_OnePunchMan_Star_3__P_Red_Glow']={-2518.467,99.3,1678.853,1.161,1.8,1.89,11,false,'P_Red_Glow','',''},
  ['VFX_GATE_OnePunchMan_Star_4__Metal_Gold']={-2522.209,104.1,1676.853,1.399,3.1,3.036,11,false,'Metal_Gold','',''},
  ['VFX_GATE_OnePunchMan_Star_4__P_Red_Glow']={-2522.209,104.1,1676.853,1.161,1.8,1.89,11,false,'P_Red_Glow','',''},
  ['VFX_OPSUM_Ring_1__Metal_Gold_OPOld']={-2387.679,134.2,1726.127,23.284,7.267,23.558,11,false,'Metal_Gold_OPOld','',''},
  ['VFX_OPSUM_Ring_1__Summon_OPStar_Glow']={-2387.679,134.278,1726.119,22.835,7.818,22.342,11,false,'Summon_OPStar_Glow','',''},
  ['VFX_OPSUM_Ring_2__Metal_Gold_OPOld']={-2387.679,134.2,1726.127,2.207,17.32,17.314,11,false,'Metal_Gold_OPOld','',''},
  ['VFX_OPSUM_Ring_2__Summon_OPStar_Glow']={-2387.744,134.2,1726.104,2.598,13.023,12.973,11,false,'Summon_OPStar_Glow','',''},
  ['VFX_OPSUM_Ring_3__Metal_Gold_OPOld']={-2387.679,134.2,1726.127,15.35,13.37,8.766,11,false,'Metal_Gold_OPOld','',''},
  ['VFX_OPSUM_Ring_3__Summon_OPStar_Glow']={-2387.698,134.18,1726.118,12.068,10.223,7.935,11,false,'Summon_OPStar_Glow','',''},
  ['VFX_OPSUM_Star__Metal_Gold_OPOld']={-2387.679,134.83,1726.127,7.938,11.94,10.8,11,false,'Metal_Gold_OPOld','',''},
  ['VFX_OPSUM_Star__Summon_OPStar_Glow']={-2387.679,134.83,1726.127,7.938,11.94,10.8,11,false,'Summon_OPStar_Glow','',''},
  ['VFX_OP_Wheel__Metal_OP_Iron']={-2033.833,92.4,1822.516,13.066,0.9,9.524,11,false,'Metal_OP_Iron','',''},
  ['VFX_OP_Wheel__Wood_OP_Dark']={-2032.31,92.4,1823.583,9.125,10.311,10.694,11,false,'Wood_OP_Dark','',''},
  ['VFX_OP_Wheel__Wood_OP_Mid']={-2032.31,92.4,1823.583,10.979,13.0,13.115,11,false,'Wood_OP_Mid','',''},
  ['OP_Port_Built__Cloth_OP_Red']={-2372.344,48.35,1613.567,3.634,1.2,2.848,12,false,'Cloth_OP_Red','',''},
  ['OP_Port_Built__Cloth_OP_Straw']={-2283.577,23.195,1615.588,49.857,42.71,58.437,12,true,'Cloth_OP_Straw','',''},
  ['OP_Port_Built__Glass_OP_Lantern']={-2324.312,47.077,1597.619,99.759,4.115,34.806,12,false,'Glass_OP_Lantern','',''},
  ['OP_Port_Built__Metal_OP_Gold']={-2317.167,80.48,1659.647,24.888,23.78,50.572,12,true,'Metal_OP_Gold','',''},
  ['OP_Port_Built__Metal_OP_Iron']={-2318.867,36.385,1609.981,109.674,70.51,66.66,12,true,'Metal_OP_Iron','',''},
  ['OP_Port_Built__Plaster_OP']={-2297.885,66.12,1613.621,102.852,44.64,91.297,12,true,'Plaster_OP','',''},
  ['OP_Port_Built__Plaster_OP_Warm']={-2304.588,50.671,1574.335,24.02,13.743,22.664,12,false,'Plaster_OP_Warm','',''},
  ['OP_Port_Built__Roof_OP_Blue']={-2298.832,69.546,1611.971,111.241,38.988,104.879,12,true,'Roof_OP_Blue','',''},
  ['OP_Port_Built__Roof_OP_Ridge']={-2310.824,68.406,1616.013,124.877,45.177,98.925,12,true,'Roof_OP_Ridge','',''},
  ['OP_Port_Built__Roof_OP_Shingle']={-2287.885,52.56,1644.627,28.939,3.853,27.615,12,false,'Roof_OP_Shingle','',''},
  ['OP_Port_Built__Stone_OP_B']={-2309.567,54.15,1611.444,127.444,24.7,97.994,12,true,'Stone_OP_B','',''},
  ['OP_Port_Built__Stone_OP_Dark']={-2323.596,64.88,1631.723,95.527,45.96,107.415,12,true,'Stone_OP_Dark','',''},
  ['OP_Port_Built__Stone_OP_Path']={-2323.43,66.398,1638.555,99.497,47.503,96.133,12,true,'Stone_OP_Path','',''},
  ['OP_Port_Built__Stone_OP_Wall']={-2323.577,65.775,1638.726,99.315,47.75,95.975,12,true,'Stone_OP_Wall','',''},
  ['OP_Port_Built__Window_OP_Warm']={-2312.208,47.09,1590.016,75.553,4.68,19.601,12,false,'Window_OP_Warm','',''},
  ['OP_Port_Built__Wood_OP_Dark']={-2308.744,44.265,1612.175,131.066,88.65,105.288,12,true,'Wood_OP_Dark','',''},
  ['OP_Port_Built__Wood_OP_Lacquer']={-2323.405,68.164,1638.812,95.833,47.022,92.322,12,true,'Wood_OP_Lacquer','',''},
  ['OP_Port_Built__Wood_OP_Mid']={-2299.704,38.655,1613.49,77.345,74.21,74.101,12,true,'Wood_OP_Mid','',''},
  ['OP_Port_Muralha__Stone_OP']={-2324.497,65.862,1645.515,88.439,47.924,81.876,12,true,'Stone_OP','',''},
  ['OP_Port_Muralha__Stone_OP_B']={-2328.08,67.916,1643.044,72.1,43.815,86.81,12,true,'Stone_OP_B','',''},
  ['OP_Port_Muralha__Stone_OP_Dark']={-2323.406,65.877,1639.063,97.159,47.954,94.35,12,true,'Stone_OP_Dark','',''},
  ['OP_Port_Muralha__Stone_OP_Path']={-2323.429,67.051,1639.166,97.504,46.326,94.75,12,true,'Stone_OP_Path','',''},
  ['OP_Port_Muralha__Stone_OP_Wall']={-2323.599,65.726,1639.122,97.072,47.653,94.666,12,true,'Stone_OP_Wall','',''},
  ['OP_Port_Piers__Cliff_OP_Moss']={-2387.81,36.35,1610.388,81.96,1.5,136.926,12,false,'Cliff_OP_Moss','',''},
  ['OP_Port_Piers__Cloth_OP_Indigo']={-2433.058,40.125,1693.302,6.007,1.25,6.611,12,false,'Cloth_OP_Indigo','',''},
  ['OP_Port_Piers__Cloth_OP_Red']={-2344.483,49.15,1565.932,9.831,1.1,13.662,12,false,'Cloth_OP_Red','',''},
  ['OP_Port_Piers__Glass_OP_Lantern']={-2344.483,49.15,1565.932,9.885,0.44,13.716,12,false,'Glass_OP_Lantern','',''},
  ['OP_Port_Piers__Metal_OP_Gold']={-2353.757,46.44,1557.518,28.83,1.68,31.286,12,false,'Metal_OP_Gold','',''},
  ['OP_Port_Piers__Metal_OP_Iron']={-2385.919,46.4,1632.745,91.901,8.0,146.487,12,true,'Metal_OP_Iron','',''},
  ['OP_Port_Piers__Roof_OP_Blue']={-2433.058,41.65,1693.302,8.845,1.279,9.55,12,false,'Roof_OP_Blue','',''},
  ['OP_Port_Piers__Roof_OP_Red']={-2349.808,53.264,1562.204,30.567,5.258,31.549,12,false,'Roof_OP_Red','',''},
  ['OP_Port_Piers__Roof_OP_Ridge']={-2384.549,49.973,1621.086,102.179,15.746,151.444,12,true,'Roof_OP_Ridge','',''},
  ['OP_Port_Piers__Rope']={-2395.575,46.136,1626.946,82.646,16.664,156.992,12,false,'Rope','',''},
  ['OP_Port_Piers__Stone_OP']={-2349.764,42.35,1562.224,22.063,0.9,23.034,12,false,'Stone_OP','',''},
  ['OP_Port_Piers__Wood_OP_Dark']={-2383.065,42.196,1623.863,109.072,26.393,165.259,12,true,'Wood_OP_Dark','',''},
  ['OP_Port_Piers__Wood_OP_Hull']={-2397.512,37.15,1623.322,80.019,2.5,151.301,12,true,'Wood_OP_Hull','',''},
  ['OP_Port_Piers__Wood_OP_Lacquer']={-2379.267,40.125,1613.823,100.422,22.25,143.921,12,true,'Wood_OP_Lacquer','',''},
  ['OP_Port_Piers__Wood_OP_Mid']={-2383.237,40.575,1620.24,108.689,9.05,156.926,12,true,'Wood_OP_Mid','',''},
  ['OP_Ship_Navio__Cloth_OP_Black']={-2417.773,75.403,1638.348,14.824,31.995,10.685,12,false,'Cloth_OP_Black','','OP_Ship'},
  ['OP_Ship_Navio__Cloth_OP_Red']={-2423.423,68.525,1642.273,38.855,35.55,55.931,12,true,'Cloth_OP_Red','','OP_Ship'},
  ['OP_Ship_Navio__Cloth_OP_Sail']={-2411.818,73.74,1629.071,36.166,31.08,36.258,12,false,'Cloth_OP_Sail','','OP_Ship'},
  ['OP_Ship_Navio__Cloth_OP_Straw']={-2417.831,79.873,1638.43,10.337,21.173,8.315,12,false,'Cloth_OP_Straw','','OP_Ship'},
  ['OP_Ship_Navio__Cloth_OP_White']={-2417.771,75.086,1638.345,14.456,30.703,10.588,12,false,'Cloth_OP_White','','OP_Ship'},
  ['OP_Ship_Navio__Glass_OP_Lantern']={-2433.943,53.237,1660.389,17.871,4.405,19.755,12,false,'Glass_OP_Lantern','','OP_Ship'},
  ['OP_Ship_Navio__Metal_OP_Gold']={-2413.885,53.49,1630.811,56.954,6.98,77.018,12,true,'Metal_OP_Gold','','OP_Ship'},
  ['OP_Ship_Navio__Metal_OP_Iron']={-2412.664,62.398,1629.271,59.83,54.746,81.405,12,true,'Metal_OP_Iron','','OP_Ship'},
  ['OP_Ship_Navio__Rope']={-2405.499,64.337,1623.127,53.722,52.866,81.178,12,false,'Rope','','OP_Ship'},
  ['OP_Ship_Navio__Window_OP_Warm']={-2432.446,49.8,1659.329,16.942,2.6,17.466,12,false,'Window_OP_Warm','','OP_Ship'},
  ['OP_Ship_Navio__Wood_OP_Dark']={-2410.705,61.225,1626.369,64.527,61.95,87.974,12,true,'Wood_OP_Dark','','OP_Ship'},
  ['OP_Ship_Navio__Wood_OP_Hull']={-2414.16,42.575,1631.733,56.753,23.15,75.167,12,true,'Wood_OP_Hull','','OP_Ship'},
  ['OP_Ship_Navio__Wood_OP_Lacquer']={-2414.026,51.065,1631.593,57.116,10.53,75.531,12,true,'Wood_OP_Lacquer','','OP_Ship'},
  ['OP_Ship_Navio__Wood_OP_Mid']={-2414.053,60.813,1631.657,55.782,37.774,74.489,12,true,'Wood_OP_Mid','','OP_Ship'},
  ['OP_Lmk_Pagoda__Cliff_OP_Face']={-2137.343,105.65,2094.756,46.766,107.3,53.232,13,false,'Cliff_OP_Face','','OP_Lmk'},
  ['OP_Lmk_Pagoda__Cliff_OP_Moss']={-2138.044,104.25,2090.765,36.992,105.5,48.914,13,false,'Cliff_OP_Moss','','OP_Lmk'},
  ['OP_Lmk_Pagoda__Cliff_OP_Shade']={-2136.873,41.0,2094.399,49.104,34.0,57.312,13,false,'Cliff_OP_Shade','','OP_Lmk'},
  ['OP_Lmk_Pagoda__Metal_OP_Gold']={-2135.079,200.135,2095.882,2.507,12.37,2.507,13,false,'Metal_OP_Gold','','OP_Lmk'},
  ['OP_Lmk_Pagoda__Roof_OP_Blue']={-2135.079,179.7,2095.882,26.202,29.8,26.202,13,false,'Roof_OP_Blue','','OP_Lmk'},
  ['OP_Lmk_Pagoda__Wood_OP_Dark']={-2135.079,175.094,2095.882,25.069,31.588,25.069,13,false,'Wood_OP_Dark','','OP_Lmk'},
  ['OP_Lmk_Pagoda__Wood_OP_Lacquer']={-2135.079,174.3,2095.882,15.599,30.0,15.599,13,false,'Wood_OP_Lacquer','','OP_Lmk'},
  ['OP_Lmk_Skull__Cliff_OP_Dark']={-2494.699,81.06,1623.264,64.889,106.12,57.992,13,false,'Cliff_OP_Dark','','OP_Lmk'},
  ['OP_Lmk_Skull__Cliff_OP_Moss']={-2497.011,90.939,1621.82,58.068,88.212,54.038,13,false,'Cliff_OP_Moss','','OP_Lmk'},
  ['OP_Lmk_Skull__Cliff_OP_Void']={-2482.048,127.092,1624.456,39.586,60.549,68.52,13,false,'Cliff_OP_Void','','OP_Lmk'},
  ['OP_Lmk_Skull__Glass_OP_Lantern']={-2475.617,113.7,1628.411,8.025,3.1,19.026,13,false,'Glass_OP_Lantern','','OP_Lmk'},
  ['OP_Lmk_Sword__Cliff_OP_Face']={-2707.71,100.446,1973.85,19.448,7.892,22.2,13,false,'Cliff_OP_Face','','OP_Lmk'},
  ['OP_Lmk_Sword__Metal_OP_Gold']={-2711.188,196.127,1975.319,15.73,35.741,50.224,13,false,'Metal_OP_Gold','','OP_Lmk'},
  ['OP_Lmk_Sword__Metal_OP_Steel']={-2709.288,135.959,1975.16,9.304,89.97,16.259,13,false,'Metal_OP_Steel','','OP_Lmk'},
  ['OP_Lmk_Sword__Wood_OP_Dark']={-2712.136,196.624,1975.583,6.198,22.634,5.454,13,false,'Wood_OP_Dark','','OP_Lmk'},
  ['OP_Ent_Bridge__Glass_OP_Lantern']={-2102.86,87.841,1620.98,57.523,3.618,69.84,14,false,'Glass_OP_Lantern','','OP_Ent'},
  ['OP_Ent_Bridge__Metal_OP_Gold']={-2088.794,85.057,1600.894,85.796,12.074,110.192,14,false,'Metal_OP_Gold','','OP_Ent'},
  ['OP_Ent_Bridge__Roof_OP_Ridge']={-2102.86,88.278,1620.98,59.152,4.948,71.468,14,false,'Roof_OP_Ridge','','OP_Ent'},
  ['OP_Ent_Bridge__Wood_OP_Dark']={-2089.239,84.382,1601.241,85.426,10.764,109.979,14,false,'Wood_OP_Dark','','OP_Ent'},
  ['OP_Ent_Bridge__Wood_OP_Lacquer']={-2088.806,83.54,1600.908,85.57,9.18,110.043,14,false,'Wood_OP_Lacquer','','OP_Ent'},
  ['OP_Ent_Court__Stone_OP']={-2133.116,86.211,1663.553,57.897,4.622,56.909,14,false,'Stone_OP','','OP_Ent'},
  ['OP_Ent_Court__Stone_OP_B']={-2131.305,85.32,1664.333,58.931,2.64,53.715,14,false,'Stone_OP_B','','OP_Ent'},
  ['OP_Ent_Court__Stone_OP_Dark']={-2132.648,86.878,1663.673,61.698,5.956,57.23,14,false,'Stone_OP_Dark','','OP_Ent'},
  ['OP_Ent_Court__Stone_OP_Path']={-2137.519,86.817,1669.433,36.279,5.434,43.855,14,false,'Stone_OP_Path','','OP_Ent'},
  ['OP_Ent_Lamps__Cloth_OP_Red']={-2095.985,90.763,1608.568,99.863,14.493,120.676,14,false,'Cloth_OP_Red','','OP_Ent'},
  ['OP_Ent_Lamps__Cloth_OP_White']={-2096.025,92.718,1608.6,99.452,6.978,120.496,14,false,'Cloth_OP_White','','OP_Ent'},
  ['OP_Ent_Lamps__Glass_OP_Lantern']={-2131.63,89.355,1662.737,39.411,2.11,38.635,14,false,'Glass_OP_Lantern','','OP_Ent'},
  ['OP_Ent_Lamps__Leaf_OP']={-2103.619,86.137,1618.924,115.386,13.5,141.632,14,false,'Leaf_OP','','OP_Ent'},
  ['OP_Ent_Lamps__Leaf_OP_Pine']={-2133.372,86.04,1663.582,55.198,2.054,49.81,14,false,'Leaf_OP_Pine','','OP_Ent'},
  ['OP_Ent_Lamps__Metal_OP_Gold']={-2096.002,96.018,1608.583,95.496,6.263,117.72,14,false,'Metal_OP_Gold','','OP_Ent'},
  ['OP_Ent_Lamps__Metal_OP_Iron']={-2127.235,85.183,1655.791,34.013,0.753,24.288,14,false,'Metal_OP_Iron','','OP_Ent'},
  ['OP_Ent_Lamps__Stone_OP']={-2100.083,85.517,1615.941,105.015,14.861,133.905,14,false,'Stone_OP','','OP_Ent'},
  ['OP_Ent_Lamps__Stone_OP_B']={-2131.22,88.474,1663.235,43.055,8.948,40.637,14,false,'Stone_OP_B','','OP_Ent'},
  ['OP_Ent_Lamps__Wood_OP_Dark']={-2127.235,91.73,1655.791,37.725,13.14,26.507,14,false,'Wood_OP_Dark','','OP_Ent'},
  ['OP_Ent_Torii__Glass_OP_Lantern']={-2128.956,99.727,1658.249,27.033,10.93,19.448,14,false,'Glass_OP_Lantern','','OP_Ent'},
  ['OP_Ent_Torii__Metal_OP_Gold']={-2128.956,101.714,1658.249,32.792,28.509,23.682,14,false,'Metal_OP_Gold','','OP_Ent'},
  ['OP_Ent_Torii__Metal_OP_Iron']={-2128.956,101.285,1658.249,25.17,9.79,17.658,14,false,'Metal_OP_Iron','','OP_Ent'},
  ['OP_Ent_Torii__Roof_OP_Blue']={-2128.956,113.35,1658.249,33.791,3.28,25.122,14,false,'Roof_OP_Blue','','OP_Ent'},
  ['OP_Ent_Torii__Roof_OP_Ridge']={-2128.956,100.449,1658.249,32.789,30.698,23.844,14,false,'Roof_OP_Ridge','','OP_Ent'},
  ['OP_Ent_Torii__Stone_OP_Dark']={-2128.956,84.59,1658.249,25.158,1.38,19.314,14,false,'Stone_OP_Dark','','OP_Ent'},
  ['OP_Ent_Torii__Wood_OP_Lacquer']={-2128.956,98.449,1658.249,27.046,26.598,19.377,14,false,'Wood_OP_Lacquer','','OP_Ent'},
  ['OP_Ent_Viaduct__Stone_OP']={-2092.114,54.333,1603.086,91.836,56.667,111.215,14,false,'Stone_OP','','OP_Ent'},
  ['OP_Ent_Viaduct__Stone_OP_B']={-2085.605,54.333,1604.071,78.028,56.667,112.5,14,false,'Stone_OP_B','','OP_Ent'},
  ['OP_Ent_Viaduct__Stone_OP_Dark']={-2091.987,54.533,1603.778,92.604,57.467,113.486,14,false,'Stone_OP_Dark','','OP_Ent'},
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
  {'COL_GateOnePunchMan_001','Block',{-2534.167,101.55,1697.136},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{4.3,6.1,26.7},false},
  {'COL_GateOnePunchMan_002','Block',{-2535.973,95.6,1701.002},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{4.2,4.35,14.8},false},
  {'COL_GateOnePunchMan_003','Block',{-2538.789,95.2,1696.093},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{2.3,4.6,15.2},false},
  {'COL_GateOnePunchMan_004','Block',{-2527.224,101.55,1678.06},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{4.3,6.1,26.7},false},
  {'COL_GateOnePunchMan_005','Block',{-2526.123,93.8,1673.938},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{4.2,4.35,11.2},false},
  {'COL_GateOnePunchMan_006','Block',{-2531.436,95.2,1675.889},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{2.3,4.6,15.2},false},
  {'COL_GateOnePunchMan_007','Block',{-2530.696,87.975,1687.598},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{22.0,10.0,0.75},false},
  {'COL_GateOnePunchMan_008','Block',{-2532.225,88.2,1702.472},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{7.0,13.1,1.2},false},
  {'COL_GateOnePunchMan_009','Block',{-2531.444,89.05,1703.395},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{5.2,5.2,0.5},false},
  {'COL_GateOnePunchMan_010','Block',{-2531.444,93.6,1703.395},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{4.0,4.0,9.6},false},
  {'COL_GateOnePunchMan_011','Block',{-2526.949,92.05,1702.158},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{2.0,2.0,6.5},false},
  {'COL_GateOnePunchMan_012','Block',{-2522.307,88.2,1675.221},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{7.0,13.1,1.2},false},
  {'COL_GateOnePunchMan_013','Block',{-2521.115,89.05,1675.016},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{5.2,5.2,0.5},false},
  {'COL_GateOnePunchMan_014','Block',{-2521.115,93.6,1675.016},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{4.0,4.0,9.6},false},
  {'COL_GateOnePunchMan_015','Block',{-2518.467,92.05,1678.853},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{2.0,2.0,6.5},false},
  {'COL_OPAnchorGuard_001','Block',{-2553.812,92.2,1679.185},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{1.2,20.0,9.0},false},
  {'COL_OPSumPine_001','Block',{-2375.629,91.5,1672.305},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.8,1.8,6.6},false},
  {'COL_OPSumPine_002','Block',{-2422.418,91.05,1753.075},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.8,1.8,5.7},false},
  {'COL_OPSumStair_001','Block',{-2355.955,89.3,1760.06},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,2.2},false},
  {'COL_OPSumStair_002','Block',{-2347.236,89.3,1747.609},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,2.2},false},
  {'COL_OPSumToro_001','Block',{-2347.882,92.1,1736.414},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.5,2.5,7.8},false},
  {'COL_OPSumToro_002','Block',{-2369.136,92.1,1757.179},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.5,2.5,7.8},false},
  {'COL_OPSumToro_003','Block',{-2361.398,92.1,1726.95},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.5,2.5,7.8},false},
  {'COL_OPSumToro_004','Block',{-2382.652,92.1,1747.715},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.5,2.5,7.8},false},
  {'COL_OPSumTower_001','Ramp',{-2376.885,89.753,1733.685},{-0.733,0.447,-0.513},{-0.574,-0.0,0.819},{8.944,7.6,1.0},false},
  {'COL_OPSumTower_002','Block',{-2380.429,91.7,1731.203},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,7.6,1.0},true},
  {'COL_OPSumTower_003','Ramp',{-2374.399,91.26,1730.054},{-0.733,0.447,-0.513},{-0.574,-0.0,0.819},{8.944,1.2,5.5},false},
  {'COL_OPSumTower_004','Ramp',{-2379.447,91.26,1737.263},{-0.733,0.447,-0.513},{-0.574,-0.0,0.819},{8.944,1.2,5.5},false},
  {'COL_OPSumTower_005','Block',{-2376.307,94.7,1722.614},{-0.574,0.0,0.819},{0.819,0.0,0.574},{2.2,2.2,6.4},true},
  {'COL_OPSumTower_006','Block',{-2387.091,94.7,1738.014},{-0.574,0.0,0.819},{0.819,0.0,0.574},{2.2,2.2,6.4},true},
  {'COL_OPSumTower_007','Block',{-2389.932,108.05,1724.55},{-0.574,0.0,0.819},{0.819,0.0,0.574},{17.2,8.7,33.1},true},
  {'COL_OPSumTower_008','Block',{-2385.262,114.4,1727.819},{-0.574,0.0,0.819},{0.819,0.0,0.574},{17.2,2.7,20.4},true},
  {'COL_OPSumTower_009','Block',{-2382.928,105.3,1729.454},{-0.574,0.0,0.819},{0.819,0.0,0.574},{8.0,3.0,2.2},true},
  {'COL_OPSumTower_010','Block',{-2380.42,98.95,1723.519},{-0.574,0.0,0.819},{0.819,0.0,0.574},{4.6,5.7,14.9},true},
  {'COL_OPSumTower_011','Block',{-2382.345,105.35,1718.509},{-0.574,0.0,0.819},{0.819,0.0,0.574},{4.2,2.2,27.7},true},
  {'COL_OPSumTower_012','Block',{-2387.647,98.95,1733.84},{-0.574,0.0,0.819},{0.819,0.0,0.574},{4.6,5.7,14.9},true},
  {'COL_OPSumTower_013','Block',{-2393.013,105.35,1733.745},{-0.574,0.0,0.819},{0.819,0.0,0.574},{4.2,2.2,27.7},true},
  {'COL_OPSumTower_014','Block',{-2381.452,88.25,1718.28},{-0.574,0.0,0.819},{0.819,0.0,0.574},{10.0,18.8,1.3},true},
  {'COL_OPSumTower_015','Block',{-2382.312,88.25,1719.508},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.0,24.8,1.3},true},
  {'COL_OPSumTower_016','Block',{-2382.193,90.65,1719.164},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.7,20.0,6.1},true},
  {'COL_OPSumTower_017','Block',{-2392.923,88.25,1734.663},{-0.574,0.0,0.819},{0.819,0.0,0.574},{10.0,18.8,1.3},true},
  {'COL_OPSumTower_018','Block',{-2392.063,88.25,1733.434},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.0,24.8,1.3},true},
  {'COL_OPSumTower_019','Block',{-2392.345,90.65,1733.663},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.7,20.0,6.1},true},
  {'COL_OPSumTower_020','Block',{-2396.403,88.25,1720.019},{-0.574,0.0,0.819},{0.819,0.0,0.574},{10.0,2.3,1.3},true},
  {'COL_OPSumTower_021','Block',{-2390.915,89.55,1723.861},{-0.574,0.0,0.819},{0.819,0.0,0.574},{10.0,11.1,3.9},true},
  {'COL_OPSumTower_022','Block',{-2383.501,90.1,1729.052},{-0.574,0.0,0.819},{0.819,0.0,0.574},{10.0,7.0,4.2},true},
  {'COL_OP_Arrival_001','Ramp',{-2088.825,81.201,1600.935},{-0.573,0.033,0.819},{0.819,-0.0,0.574},{124.069,18.0,2.0},false},
  {'COL_OP_Arrival_002','Ramp',{-2096.712,83.951,1595.463},{-0.573,0.033,0.819},{0.819,-0.0,0.574},{120.067,1.2,4.5},false},
  {'COL_OP_Arrival_003','Ramp',{-2080.985,83.951,1606.476},{-0.573,0.033,0.819},{0.819,-0.0,0.574},{120.067,1.2,4.5},false},
  {'COL_OP_CanalN_001','Ramp',{-2125.229,91.2,1956.286},{0.819,0.0,0.574},{0.574,0.0,-0.819},{16.0,10.0,2.0},false},
  {'COL_OP_CanalN_002','Ramp',{-2128.441,93.95,1960.873},{0.819,0.0,0.574},{0.574,0.0,-0.819},{12.0,1.2,4.5},false},
  {'COL_OP_CanalN_003','Ramp',{-2122.017,93.95,1951.699},{0.819,0.0,0.574},{0.574,0.0,-0.819},{12.0,1.2,4.5},false},
  {'COL_OP_CanalS_001','Ramp',{-2085.079,91.2,1898.945},{0.819,0.0,0.574},{0.574,0.0,-0.819},{16.0,10.0,2.0},false},
  {'COL_OP_CanalS_002','Ramp',{-2088.291,93.95,1903.532},{0.819,0.0,0.574},{0.574,0.0,-0.819},{12.0,1.2,4.5},false},
  {'COL_OP_CanalS_003','Ramp',{-2081.867,93.95,1894.358},{0.819,0.0,0.574},{0.574,0.0,-0.819},{12.0,1.2,4.5},false},
  {'COL_OP_CapBench_001','Block',{-2153.643,89.05,1740.578},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{6.0,1.8,1.7},false},
  {'COL_OP_CapBench_002','Block',{-2144.473,93.1,1900.084},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{5.0,1.6,1.6},false},
  {'COL_OP_CapBench_003','Block',{-2061.322,93.12,1903.372},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.6,1.6,1.6},false},
  {'COL_OP_CapBench_004','Block',{-2103.479,93.12,1963.58},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.6,1.6,1.6},false},
  {'COL_OP_CapBench_005','Block',{-2041.478,89.12,1775.657},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.6,1.6,1.6},false},
  {'COL_OP_CapBench_006','Block',{-2257.835,89.12,1640.765},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.4,1.6,1.6},false},
  {'COL_OP_CapChaMobilia_001','Block',{-2149.167,94.9,1929.453},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.6,9.4,3.2},false},
  {'COL_OP_CapChaMobilia_002','Block',{-2153.957,94.05,1938.429},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{6.4,12.85,1.5},false},
  {'COL_OP_CapChaMobilia_003','Block',{-2162.705,92.5,1926.383},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{6.8,1.0,0.6},false},
  {'COL_OP_CapHouseC1_001','Block',{-2132.65,88.5,1710.597},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.6,22.6,1.2},true},
  {'COL_OP_CapHouseC1_002','Block',{-2132.65,98.65,1710.597},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.0,22.0,19.1},true},
  {'COL_OP_CapHouseC2_001','Block',{-2140.517,88.5,1727.063},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.6,26.6,1.2},true},
  {'COL_OP_CapHouseC2_002','Block',{-2140.517,94.6,1727.063},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.0,26.0,11.0},true},
  {'COL_OP_CapHouseC4_001','Block',{-2158.215,93.8,1748.852},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.6,24.6,11.8},true},
  {'COL_OP_CapHouseC4_002','Block',{-2158.133,103.8,1748.909},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.0,20.6,8.2},true},
  {'COL_OP_CapHouseC5_001','Block',{-2174.918,88.5,1678.559},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.6,20.6,1.2},true},
  {'COL_OP_CapHouseC5_002','Block',{-2174.918,98.0,1678.559},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.0,20.0,17.8},true},
  {'COL_OP_CapHouseC6_001','Block',{-2189.092,88.55,1691.829},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.6,28.6,1.3},true},
  {'COL_OP_CapHouseC6_002','Block',{-2189.092,95.45,1691.829},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.0,28.0,12.5},true},
  {'COL_OP_CapHouseC7_001','Block',{-2199.499,88.55,1710.178},{-0.574,0.0,0.819},{0.819,0.0,0.574},{16.6,22.6,1.3},true},
  {'COL_OP_CapHouseC7_002','Block',{-2199.499,94.45,1710.178},{-0.574,0.0,0.819},{0.819,0.0,0.574},{16.0,22.0,10.5},true},
  {'COL_OP_CapHouseC7_003','Block',{-2199.499,103.9,1710.178},{-0.574,0.0,0.819},{0.819,0.0,0.574},{12.8,18.8,8.4},true},
  {'COL_OP_CapHouseC7_004','Block',{-2199.499,111.9,1710.178},{-0.574,0.0,0.819},{0.819,0.0,0.574},{9.6,15.6,7.6},true},
  {'COL_OP_CapHouseCha_001','Block',{-2152.998,92.65,1933.18},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.6,22.6,1.5},true},
  {'COL_OP_CapHouseCha_002','Block',{-2144.397,98.9,1939.202},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.0,1.0,11.0},true},
  {'COL_OP_CapHouseCha_003','Block',{-2157.873,98.9,1940.142},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,22.0,11.0},true},
  {'COL_OP_CapHouseCha_004','Block',{-2165.27,98.9,1932.4},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{5.2,1.0,11.0},true},
  {'COL_OP_CapHouseCha_005','Block',{-2148.122,98.9,1926.217},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,22.0,11.0},true},
  {'COL_OP_CapHouseCha_006','Block',{-2157.928,98.9,1921.915},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{5.2,1.0,11.0},true},
  {'COL_OP_CapHouseCha_007','Block',{-2161.517,102.2,1927.214},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.0,1.2,3.0},true},
  {'COL_OP_CapHouseE1_001','Block',{-2204.079,93.2,1655.699},{-0.574,0.0,0.819},{0.819,0.0,0.574},{16.6,18.6,10.6},true},
  {'COL_OP_CapHouseE4_001','Block',{-2227.35,93.5,1690.677},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.6,20.6,11.2},true},
  {'COL_OP_CapHouseE5_001','Block',{-2244.798,93.8,1677.239},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.6,22.6,11.8},true},
  {'COL_OP_CapHouseE5_002','Block',{-2244.626,103.7,1676.993},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.0,18.6,8.0},true},
  {'COL_OP_CapHouseE6_001','Block',{-2263.638,93.5,1664.047},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.6,18.6,11.2},true},
  {'COL_OP_CapHouseE7_001','Block',{-2225.296,93.4,1649.388},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.6,20.6,11.0},true},
  {'COL_OP_CapHouseE7_002','Block',{-2225.124,102.6,1649.142},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.0,17.4,7.4},true},
  {'COL_OP_CapHouseE8_001','Block',{-2241.925,93.1,1636.523},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.6,16.6,10.4},true},
  {'COL_OP_CapHouseN10_001','Block',{-2420.014,97.1,1842.044},{0.819,0.0,0.574},{0.574,0.0,-0.819},{14.6,12.6,10.4},true},
  {'COL_OP_CapHouseN1_001','Block',{-2431.028,96.95,1808.085},{-0.574,0.0,0.819},{0.819,0.0,0.574},{9.6,8.6,10.1},true},
  {'COL_OP_CapHouseN2_001','Block',{-2439.46,97.3,1770.44},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.6,15.6,10.8},true},
  {'COL_OP_CapHouseN3_001','Block',{-2454.377,97.2,1816.151},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.6,14.6,10.6},true},
  {'COL_OP_CapHouseN3_002','Block',{-2454.434,106.0,1816.233},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.0,11.8,7.0},true},
  {'COL_OP_CapHouseN5_001','Block',{-2399.739,97.55,1853.188},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.6,14.6,11.3},true},
  {'COL_OP_CapHouseN5_002','Block',{-2399.854,107.0,1853.352},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.0,11.6,7.6},true},
  {'COL_OP_CapHouseN6_001','Block',{-2417.507,97.1,1780.93},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.6,13.6,10.4},true},
  {'COL_OP_CapHouseN7_001','Block',{-2384.658,97.1,1800.268},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.6,12.6,10.4},true},
  {'COL_OP_CapHouseN8_001','Block',{-2461.009,97.0,1790.754},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.6,12.6,10.2},true},
  {'COL_OP_CapHouseN9_001','Block',{-2440.247,97.0,1829.097},{0.819,0.0,0.574},{0.574,0.0,-0.819},{16.6,11.6,10.2},true},
  {'COL_OP_CapHouseNW1_001','Block',{-2132.78,93.5,1764.83},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.6,21.6,11.2},true},
  {'COL_OP_CapHouseNW1_002','Block',{-2133.239,102.8,1765.486},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.0,19.4,7.4},true},
  {'COL_OP_CapHouseNW2_001','Block',{-2116.438,93.1,1778.104},{0.819,0.0,0.574},{0.574,0.0,-0.819},{14.6,20.6,10.4},true},
  {'COL_OP_CapHouseNW3_001','Block',{-2099.482,93.5,1788.756},{0.819,0.0,0.574},{0.574,0.0,-0.819},{20.6,20.6,11.2},true},
  {'COL_OP_CapHouseNW3_002','Block',{-2099.654,102.9,1789.002},{0.819,0.0,0.574},{0.574,0.0,-0.819},{20.0,17.4,7.6},true},
  {'COL_OP_CapHouseNW4_001','Block',{-2080.641,93.2,1801.949},{0.819,0.0,0.574},{0.574,0.0,-0.819},{16.6,18.6,10.6},true},
  {'COL_OP_CapHouseS4_001','Block',{-2048.201,93.9,1814.897},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.6,18.6,12.0},true},
  {'COL_OP_CapHouseS4_002','Block',{-2048.201,103.1,1814.897},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.0,18.0,6.4},true},
  {'COL_OP_CapHouseSW1_001','Block',{-2106.437,93.5,1728.952},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.6,20.6,11.2},true},
  {'COL_OP_CapHouseSW2_001','Block',{-2087.842,93.2,1740.751},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{15.6,18.6,10.6},true},
  {'COL_OP_CapHouseSW3_001','Block',{-2072.606,93.5,1753.861},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.6,18.6,11.2},true},
  {'COL_OP_CapHouseSW3_002','Block',{-2072.491,102.8,1753.697},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.0,15.6,7.4},true},
  {'COL_OP_CapHouseSW4_001','Block',{-2053.683,93.2,1763.449},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.6,16.6,10.6},true},
  {'COL_OP_CapHouseSW5_001','Block',{-2033.86,92.8,1782.212},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.6,12.6,9.8},true},
  {'COL_OP_CapHouseU1_001','Block',{-2189.71,106.4,2010.019},{0.819,0.0,0.574},{0.574,0.0,-0.819},{32.6,22.6,13.0},true},
  {'COL_OP_CapHouseU1_002','Block',{-2189.71,116.9,2010.019},{0.819,0.0,0.574},{0.574,0.0,-0.819},{32.0,17.2,8.0},true},
  {'COL_OP_CapHouseU2_001','Block',{-2240.916,105.95,2041.306},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{22.6,22.6,12.1},true},
  {'COL_OP_CapHouseU2_002','Block',{-2240.916,115.8,2041.306},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{22.0,18.4,7.6},true},
  {'COL_OP_CapHouseU3_001','Block',{-2206.842,105.3,2079.815},{0.819,0.0,0.574},{0.574,0.0,-0.819},{22.6,18.6,10.8},true},
  {'COL_OP_CapHouseU4_001','Block',{-2158.093,105.2,2046.806},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.6,20.6,10.6},true},
  {'COL_OP_CapHouseU4_002','Block',{-2158.093,114.0,2046.806},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.0,17.6,7.0},true},
  {'COL_OP_CapHouseU5_001','Block',{-2175.219,104.65,2079.983},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{12.6,10.6,9.5},true},
  {'COL_OP_CapHouseU5_002','Block',{-2175.219,112.2,2079.983},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{12.0,10.0,5.6},true},
  {'COL_OP_CapHouseW1_001','Block',{-2089.536,97.8,1845.162},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{25.6,28.6,11.8},true},
  {'COL_OP_CapHouseW1_002','Block',{-2089.29,107.7,1845.334},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{25.0,24.2,8.0},true},
  {'COL_OP_CapHouseW2_001','Block',{-2108.3,97.5,1871.088},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.6,26.6,11.2},true},
  {'COL_OP_CapHouseW2_002','Block',{-2107.727,106.9,1871.49},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.0,24.6,7.6},true},
  {'COL_OP_CapHouseW2b_001','Block',{-2114.282,97.2,1883.99},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{11.6,21.6,10.6},true},
  {'COL_OP_CapHouseW3b_001','Block',{-2116.62,97.0,1907.379},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.6,12.6,10.2},true},
  {'COL_OP_CapHouseW4_001','Block',{-2141.281,97.8,1918.189},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.6,28.6,11.8},true},
  {'COL_OP_CapHouseW4_002','Block',{-2141.281,107.8,1918.189},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.0,24.4,8.2},true},
  {'COL_OP_CapHouseW5_001','Block',{-2171.68,97.55,1961.604},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{24.6,26.6,11.3},true},
  {'COL_OP_CapHouseW5_002','Block',{-2171.271,107.0,1961.891},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{24.0,23.0,7.6},true},
  {'COL_OP_CapHouseX1_001','Block',{-2040.018,97.3,1881.666},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{24.6,18.6,10.8},true},
  {'COL_OP_CapHouseX2_001','Block',{-2074.761,97.5,1933.027},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{20.6,20.6,11.2},true},
  {'COL_OP_CapHouseX2_002','Block',{-2074.515,106.8,1933.199},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{20.0,17.4,7.4},true},
  {'COL_OP_CapHouseX2b_001','Block',{-2087.544,97.1,1952.154},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{17.6,19.6,10.4},true},
  {'COL_OP_CapHouseX3_001','Block',{-2112.33,97.3,1986.681},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{19.6,20.6,10.8},true},
  {'COL_OP_CapHouseX3b_001','Block',{-2124.457,97.0,2001.385},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{13.6,16.6,10.2},true},
  {'COL_OP_CapMureta_001','Block',{-2034.759,89.4,1766.933},{-0.656,0.0,-0.755},{-0.755,0.0,0.656},{11.0,1.4,2.4},false},
  {'COL_OP_CapMureta_002','Block',{-2264.209,89.4,1642.894},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,12.0,2.4},false},
  {'COL_OP_CapPav_001','Block',{-2126.737,92.75,1900.906},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{13.0,10.0,1.1},true},
  {'COL_OP_CapPav_002','Block',{-2122.887,95.3,1903.601},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{13.0,0.6,4.0},true},
  {'COL_OP_CapPav_003','Block',{-2130.293,95.3,1905.984},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{0.6,10.0,4.0},true},
  {'COL_OP_CapPav_004','Block',{-2123.181,95.3,1895.827},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{0.6,10.0,4.0},true},
  {'COL_OP_CapShrineDeck_001','Block',{-2418.74,92.9,1816.689},{-0.574,0.0,0.819},{0.819,0.0,0.574},{12.0,9.4,1.4},true},
  {'COL_OP_CapShrineDeck_002','Block',{-2422.345,95.6,1814.165},{-0.574,0.0,0.819},{0.819,0.0,0.574},{12.0,0.6,4.0},true},
  {'COL_OP_CapShrineDeck_003','Block',{-2415.471,95.6,1812.02},{-0.574,0.0,0.819},{0.819,0.0,0.574},{0.6,9.4,4.0},true},
  {'COL_OP_CapShrineDeck_004','Block',{-2422.01,95.6,1821.358},{-0.574,0.0,0.819},{0.819,0.0,0.574},{0.6,9.4,4.0},true},
  {'COL_OP_CapTorii_001','Block',{-2401.292,97.05,1824.023},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.4,1.4,9.4},false},
  {'COL_OP_CapTorii_002','Block',{-2405.88,97.05,1830.577},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.4,1.4,9.4},false},
  {'COL_OP_CasCourtGate_001','Block',{-2324.888,141.7,2046.599},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.9,1.9,11.0},false},
  {'COL_OP_CasCourtGate_002','Block',{-2326.937,139.8,2048.827},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,7.3},false},
  {'COL_OP_CasCourtGate_003','Block',{-2310.553,141.7,2056.636},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.9,1.9,11.0},false},
  {'COL_OP_CasCourtGate_004','Block',{-2311.946,139.8,2059.323},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,7.3},false},
  {'COL_OP_CasGate_001','Block',{-2325.032,106.45,1904.888},{0.819,0.0,0.574},{0.574,0.0,-0.819},{2.9,2.9,16.5},true},
  {'COL_OP_CasGate_002','Block',{-2327.359,103.7,1907.165},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.8,1.8,11.0},true},
  {'COL_OP_CasGate_003','Block',{-2293.659,106.45,1926.856},{0.819,0.0,0.574},{0.574,0.0,-0.819},{2.9,2.9,16.5},true},
  {'COL_OP_CasGate_004','Block',{-2295.003,103.7,1929.822},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.8,1.8,11.0},true},
  {'COL_OP_CasGate_005','Block',{-2262.508,104.2,1960.998},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.9,1.9,12.0},true},
  {'COL_OP_CasGate_006','Block',{-2251.45,104.2,1968.741},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.9,1.9,12.0},true},
  {'COL_OP_CasHall_001','Block',{-2354.371,136.175,1980.176},{0.819,0.0,0.574},{0.574,0.0,-0.819},{52.0,44.0,0.95},false},
  {'COL_OP_CasHall_002','Block',{-2341.007,136.16,1961.089},{0.819,0.0,0.574},{0.574,0.0,-0.819},{6.8,2.6,0.52},false},
  {'COL_OP_CasHall_003','Block',{-2345.906,141.15,1963.519},{0.819,0.0,0.574},{0.574,0.0,-0.819},{0.5,3.0,9.0},false},
  {'COL_OP_CasHall_004','Block',{-2341.614,141.15,1966.524},{0.819,0.0,0.574},{0.574,0.0,-0.819},{0.5,3.0,9.0},false},
  {'COL_OP_CasHall_005','Block',{-2372.968,142.2,1980.583},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,12.0},false},
  {'COL_OP_CasHall_006','Block',{-2367.232,142.2,1972.391},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,12.0},false},
  {'COL_OP_CasHall_007','Block',{-2361.497,142.2,1964.2},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,12.0},false},
  {'COL_OP_CasHall_008','Block',{-2348.394,142.2,1997.79},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,12.0},false},
  {'COL_OP_CasHall_009','Block',{-2342.658,142.2,1989.598},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,12.0},false},
  {'COL_OP_CasHall_010','Block',{-2336.922,142.2,1981.407},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,12.0},false},
  {'COL_OP_CasHall_011','Block',{-2364.983,136.975,1995.33},{0.819,0.0,0.574},{0.574,0.0,-0.819},{26.8,7.6,0.85},false},
  {'COL_OP_CasHall_012','Block',{-2372.462,139.75,1992.412},{0.819,0.0,0.574},{0.574,0.0,-0.819},{9.4,1.4,4.7},false},
  {'COL_OP_CasHall_013','Block',{-2359.683,139.75,2001.36},{0.819,0.0,0.574},{0.574,0.0,-0.819},{9.4,1.4,4.7},false},
  {'COL_OP_CasKeepCeil_001','Block',{-2354.945,149.05,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{52.0,42.0,0.8},false},
  {'COL_OP_CasKeepUpper_001','Block',{-2354.945,154.45,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{56.0,46.0,10.0},true},
  {'COL_OP_CasKeepUpper_002','Block',{-2354.945,168.7,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{44.0,36.0,17.0},true},
  {'COL_OP_CasKeepUpper_003','Block',{-2354.945,185.2,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{33.0,27.0,16.0},true},
  {'COL_OP_CasKeepUpper_004','Block',{-2354.945,200.7,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{23.0,20.0,15.0},true},
  {'COL_OP_CasKeep_001','Block',{-2355.023,147.7,1954.083},{0.819,0.0,0.574},{0.574,0.0,-0.819},{25.0,2.0,23.0},true},
  {'COL_OP_CasKeep_002','Block',{-2329.629,147.7,1971.864},{0.819,0.0,0.574},{0.574,0.0,-0.819},{25.0,2.0,23.0},true},
  {'COL_OP_CasKeep_003','Block',{-2342.326,152.425,1962.973},{0.819,0.0,0.574},{0.574,0.0,-0.819},{6.0,2.0,13.55},true},
  {'COL_OP_CasKeep_004','Block',{-2354.744,138.45,1951.593},{0.819,0.0,0.574},{0.574,0.0,-0.819},{27.4,2.4,4.5},true},
  {'COL_OP_CasKeep_005','Block',{-2327.385,138.45,1970.75},{0.819,0.0,0.574},{0.574,0.0,-0.819},{27.4,2.4,4.5},true},
  {'COL_OP_CasKeep_006','Block',{-2367.564,147.7,1999.016},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{56.0,2.0,23.0},true},
  {'COL_OP_CasKeep_007','Block',{-2368.826,138.45,2000.818},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{60.8,2.4,4.5},true},
  {'COL_OP_CasKeep_008','Block',{-2332.828,147.7,1996.481},{-0.574,0.0,0.819},{0.819,0.0,0.574},{42.0,2.0,23.0},true},
  {'COL_OP_CasKeep_009','Block',{-2331.026,138.45,1997.743},{-0.574,0.0,0.819},{0.819,0.0,0.574},{50.8,2.4,4.5},true},
  {'COL_OP_CasKeep_010','Block',{-2377.062,147.7,1965.508},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{42.0,2.0,23.0},true},
  {'COL_OP_CasKeep_011','Block',{-2378.864,138.45,1964.246},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{50.8,2.4,4.5},true},
  {'COL_OP_CasKeep_012','Block',{-2344.451,141.3,1956.419},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,10.2},true},
  {'COL_OP_CasKeep_013','Block',{-2335.441,141.3,1962.729},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.4,1.4,10.2},true},
  {'COL_OP_CasLamp_001','Block',{-2328.481,140.2,1964.122},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.0,3.0,8.0},false},
  {'COL_OP_CasLamp_002','Block',{-2348.141,140.2,1950.356},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.0,3.0,8.0},false},
  {'COL_OP_CasLamp_003','Block',{-2285.876,102.7,1926.812},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.2,1.2,9.0},false},
  {'COL_OP_CasLamp_004','Block',{-2327.653,102.7,1897.56},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.2,1.2,9.0},false},
  {'COL_OP_CasLamp_005','Block',{-2282.693,120.7,2012.054},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.6,2.6,7.0},false},
  {'COL_OP_CasTurret_001','Block',{-2380.086,145.85,1915.78},{0.994,0.0,-0.108},{-0.108,0.0,-0.994},{12.0,12.0,19.3},true},
  {'COL_OP_CasTurret_002','Block',{-2287.031,144.658,1983.38},{0.05,0.0,0.999},{0.999,0.0,-0.05},{10.0,10.0,16.916},true},
  {'COL_OP_EntBanner_001','Block',{-2111.016,91.2,1667.148},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,14.0},false},
  {'COL_OP_EntBanner_002','Block',{-2143.454,91.2,1644.434},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,14.0},false},
  {'COL_OP_EntStair_001','Block',{-2135.362,85.3,1682.391},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.7,1.5,2.2},false},
  {'COL_OP_EntStair_002','Block',{-2149.451,85.3,1672.525},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.7,1.5,2.2},false},
  {'COL_OP_EntTorii_001','Block',{-2119.208,97.2,1665.074},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.7,3.7,26.0},false},
  {'COL_OP_EntTorii_002','Block',{-2138.704,97.2,1651.423},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.7,3.7,26.0},false},
  {'COL_OP_EntToro_001','Block',{-2112.506,88.57,1661.954},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.22,3.22,8.74},false},
  {'COL_OP_EntToro_002','Block',{-2138.064,88.57,1644.058},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.22,3.22,8.74},false},
  {'COL_OP_EntToro_003','Block',{-2128.877,88.0,1681.499},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,7.6},false},
  {'COL_OP_EntToro_004','Block',{-2150.831,88.0,1666.127},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,7.6},false},
  {'COL_OP_ExitAbut_001','Block',{-2428.988,64.3,1724.059},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.15,27.0,44.2},false},
  {'COL_OP_ExitBridge_001','Ramp',{-2468.676,87.2,1710.172},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{92.0,18.0,2.0},false},
  {'COL_OP_ExitBridge_002','Ramp',{-2465.393,89.95,1701.151},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{88.0,1.2,4.5},false},
  {'COL_OP_ExitBridge_003','Ramp',{-2471.959,89.95,1719.193},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{88.0,1.2,4.5},false},
  {'COL_OP_ExitToro_001','Block',{-2541.882,91.4,1668.628},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.6,2.6,6.6},false},
  {'COL_OP_ExitToro_002','Block',{-2551.459,91.4,1694.94},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.6,2.6,6.6},false},
  {'COL_OP_Gangway_001','Ramp',{-2403.172,42.979,1639.591},{-0.774,0.326,-0.542},{-0.574,-0.0,0.819},{14.809,5.0,2.0},false},
  {'COL_OP_Gangway_002','Ramp',{-2402.383,46.073,1636.359},{-0.774,0.326,-0.542},{-0.574,0.0,0.819},{12.27,1.2,4.5},false},
  {'COL_OP_Gangway_003','Ramp',{-2405.939,46.073,1641.438},{-0.774,0.326,-0.542},{-0.574,0.0,0.819},{12.27,1.2,4.5},false},
  {'COL_OP_Guard_001','Block',{-2295.816,137.55,1962.125},{-0.669,0.0,-0.743},{-0.743,0.0,0.669},{26.457,1.0,3.7},false},
  {'COL_OP_Guard_003','Block',{-2324.423,137.55,1938.276},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{47.801,1.0,3.7},false},
  {'COL_OP_Guard_007','Block',{-2356.486,137.55,1919.363},{-0.927,0.0,-0.375},{-0.375,0.0,0.927},{26.457,1.0,3.7},false},
  {'COL_OP_Guard_009','Block',{-2379.637,137.55,1915.229},{-0.994,0.0,0.108},{0.108,0.0,0.994},{21.048,1.0,3.7},false},
  {'COL_OP_Guard_011','Block',{-2413.471,137.55,1941.774},{-0.665,0.0,0.747},{0.747,0.0,0.665},{68.262,1.0,3.7},false},
  {'COL_OP_Guard_016','Block',{-2439.712,137.55,1982.349},{-0.205,0.0,0.979},{0.979,0.0,0.205},{30.248,1.0,3.7},false},
  {'COL_OP_Guard_019','Block',{-2428.247,137.55,2013.164},{0.697,0.0,0.717},{0.717,0.0,-0.697},{42.537,1.0,3.7},false},
  {'COL_OP_Guard_022','Block',{-2388.17,137.55,2045.037},{0.838,0.0,0.546},{0.546,0.0,-0.838},{59.833,1.0,3.7},false},
  {'COL_OP_Guard_027','Block',{-2341.389,137.55,2074.157},{0.862,0.0,0.506},{0.506,0.0,-0.862},{49.957,1.0,3.7},false},
  {'COL_OP_Guard_031','Block',{-2309.205,137.55,2073.452},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{33.8,1.0,3.7},false},
  {'COL_OP_Guard_034','Block',{-2304.204,137.55,2054.979},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.8,1.0,3.7},false},
  {'COL_OP_Guard_035','Block',{-2292.359,137.55,2004.065},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{10.8,1.0,3.7},false},
  {'COL_OP_Guard_036','Block',{-2286.532,137.55,1983.355},{-0.05,0.0,-0.999},{-0.999,0.0,0.05},{21.53,1.0,3.7},false},
  {'COL_OP_Guard_038','Block',{-2276.179,118.55,2006.238},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,1.0,3.7},false},
  {'COL_OP_Guard_039','Block',{-2286.34,118.55,2019.877},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.8,1.0,3.7},false},
  {'COL_OP_Guard_040','Block',{-2279.826,118.55,2014.061},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.8,1.0,3.7},false},
  {'COL_OP_Guard_041','Block',{-2160.255,101.55,1989.747},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{95.801,1.0,3.7},false},
  {'COL_OP_Guard_048','Block',{-2217.214,101.55,1961.945},{-0.985,0.0,0.174},{0.174,0.0,0.985},{5.043,1.0,3.7},false},
  {'COL_OP_Guard_049','Block',{-2234.149,101.55,1981.954},{-0.574,0.0,0.819},{0.819,0.0,0.574},{47.8,1.0,3.7},false},
  {'COL_OP_Guard_053','Block',{-2260.671,101.55,2023.249},{-0.506,0.0,0.862},{0.862,0.0,0.506},{49.957,1.0,3.7},false},
  {'COL_OP_Guard_057','Block',{-2268.912,101.55,2060.871},{0.3,0.0,0.954},{0.954,0.0,-0.3},{32.577,1.0,3.7},false},
  {'COL_OP_Guard_060','Block',{-2249.417,101.55,2090.801},{0.725,0.0,0.689},{0.689,0.0,-0.725},{40.236,1.0,3.7},false},
  {'COL_OP_Guard_063','Block',{-2217.725,101.55,2107.202},{0.993,0.0,0.121},{0.121,0.0,-0.993},{33.8,1.0,3.7},false},
  {'COL_OP_Guard_066','Block',{-2184.18,101.55,2100.166},{0.868,0.0,-0.497},{-0.497,0.0,-0.868},{37.361,1.0,3.7},false},
  {'COL_OP_Guard_069','Block',{-2150.669,101.55,2070.985},{0.649,0.0,-0.76},{-0.76,0.0,-0.649},{52.035,1.0,3.7},false},
  {'COL_OP_Guard_073','Block',{-2127.401,101.55,2034.552},{0.345,0.0,-0.939},{-0.939,0.0,-0.345},{34.966,1.0,3.7},false},
  {'COL_OP_Guard_076','Block',{-2257.983,99.55,1938.408},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{78.8,1.0,3.7},false},
  {'COL_OP_Guard_082','Block',{-2348.089,99.55,1875.315},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{80.8,1.0,3.7},false},
  {'COL_OP_Guard_088','Block',{-2390.017,99.55,1861.168},{-0.637,0.0,0.771},{0.771,0.0,0.637},{24.876,1.0,3.7},false},
  {'COL_OP_Guard_090','Block',{-2366.279,99.55,1894.319},{0.819,0.0,0.574},{0.574,0.0,-0.819},{76.799,1.0,3.7},false},
  {'COL_OP_Guard_096','Block',{-2332.489,99.55,1914.927},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{2.8,1.0,3.7},false},
  {'COL_OP_Guard_097','Block',{-2315.655,99.55,1924.883},{0.819,0.0,0.574},{0.574,0.0,-0.819},{38.8,1.0,3.7},false},
  {'COL_OP_Guard_100','Block',{-2299.968,99.55,1936.477},{-0.574,0.0,0.819},{0.819,0.0,0.574},{2.8,1.0,3.7},false},
  {'COL_OP_Guard_101','Block',{-2282.971,99.55,1951.43},{0.819,0.0,0.574},{0.574,0.0,-0.819},{42.8,1.0,3.7},false},
  {'COL_OP_Guard_104','Block',{-2267.08,99.55,1966.22},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.8,1.0,3.7},false},
  {'COL_OP_Guard_105','Block',{-2251.927,99.55,1982.934},{0.819,0.0,0.574},{0.574,0.0,-0.819},{15.8,1.0,3.7},false},
  {'COL_OP_Guard_107','Block',{-2235.091,99.55,1974.581},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{30.8,1.0,3.7},false},
  {'COL_OP_Guard_110','Block',{-2061.189,93.55,1836.933},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{24.8,1.0,3.7},false},
  {'COL_OP_Guard_112','Block',{-2089.86,93.55,1816.857},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{24.8,1.0,3.7},false},
  {'COL_OP_Guard_114','Block',{-2118.939,93.55,1796.496},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{45.8,1.0,3.7},false},
  {'COL_OP_Guard_118','Block',{-2158.259,93.55,1768.964},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{49.801,1.0,3.7},false},
  {'COL_OP_Guard_122','Block',{-2222.153,93.55,1724.226},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{49.801,1.0,3.7},false},
  {'COL_OP_Guard_126','Block',{-2257.485,93.55,1703.043},{-0.911,0.0,-0.413},{-0.413,0.0,0.911},{32.34,1.0,3.7},false},
  {'COL_OP_Guard_129','Block',{-2283.705,93.55,1697.952},{-0.985,0.0,0.174},{0.174,0.0,0.985},{22.399,1.0,3.7},false},
  {'COL_OP_Guard_131','Block',{-2305.534,93.55,1710.928},{-0.677,0.0,0.736},{0.736,0.0,0.677},{30.057,1.0,3.7},false},
  {'COL_OP_Guard_134','Block',{-2327.058,93.55,1738.055},{-0.574,0.0,0.819},{0.819,0.0,0.574},{38.8,1.0,3.7},false},
  {'COL_OP_Guard_137','Block',{-2357.457,93.55,1781.471},{-0.574,0.0,0.819},{0.819,0.0,0.574},{38.8,1.0,3.7},false},
  {'COL_OP_Guard_140','Block',{-2411.237,93.55,1767.618},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{105.801,1.0,3.7},false},
  {'COL_OP_Guard_148','Block',{-2465.037,93.55,1746.952},{-0.684,0.0,0.73},{0.73,0.0,0.684},{28.074,1.0,3.7},false},
  {'COL_OP_Guard_150','Block',{-2474.474,93.55,1773.879},{0.045,0.0,0.999},{0.999,0.0,-0.045},{32.577,1.0,3.7},false},
  {'COL_OP_Guard_153','Block',{-2472.93,93.55,1803.054},{0.064,0.0,0.998},{0.998,0.0,-0.064},{25.388,1.0,3.7},false},
  {'COL_OP_Guard_155','Block',{-2435.415,93.55,1842.247},{0.819,0.0,0.574},{0.574,0.0,-0.819},{89.799,1.0,3.7},false},
  {'COL_OP_Guard_162','Block',{-2395.338,93.55,1866.146},{0.711,0.0,-0.703},{-0.703,0.0,-0.711},{6.898,1.0,3.7},false},
  {'COL_OP_Guard_163','Block',{-2223.058,93.55,1962.555},{0.985,0.0,-0.174},{-0.174,0.0,-0.985},{3.926,1.0,3.7},false},
  {'COL_OP_Guard_164','Block',{-2143.297,93.55,1975.986},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{41.8,1.0,3.7},false},
  {'COL_OP_Guard_167','Block',{-2108.022,93.55,1925.609},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{58.801,1.0,3.7},false},
  {'COL_OP_Guard_172','Block',{-2068.159,93.55,1868.677},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{57.801,1.0,3.7},false},
  {'COL_OP_Guard_177','Block',{-2033.082,93.55,1864.01},{-0.751,0.0,-0.661},{-0.661,0.0,0.751},{36.015,1.0,3.7},false},
  {'COL_OP_Guard_180','Block',{-2063.571,93.55,1874.33},{-0.574,0.0,0.819},{0.819,0.0,0.574},{53.8,1.0,3.7},false},
  {'COL_OP_Guard_184','Block',{-2102.287,93.55,1929.623},{-0.574,0.0,0.819},{0.819,0.0,0.574},{58.8,1.0,3.7},false},
  {'COL_OP_Guard_189','Block',{-2137.562,93.55,1980.001},{-0.574,0.0,0.819},{0.819,0.0,0.574},{41.8,1.0,3.7},false},
  {'COL_OP_Guard_192','Block',{-2127.652,93.55,2010.403},{0.877,0.0,0.48},{0.48,0.0,-0.877},{20.923,1.0,3.7},false},
  {'COL_OP_Guard_194','Block',{-2104.723,93.55,2004.355},{0.746,0.0,-0.666},{-0.666,0.0,-0.746},{34.701,1.0,3.7},false},
  {'COL_OP_Guard_197','Block',{-2076.968,93.55,1973.624},{0.607,0.0,-0.795},{-0.795,0.0,-0.607},{47.842,1.0,3.7},false},
  {'COL_OP_Guard_201','Block',{-2050.308,93.55,1937.331},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{41.8,1.0,3.7},false},
  {'COL_OP_Guard_204','Block',{-2031.03,93.55,1905.566},{0.44,0.0,-0.898},{-0.898,0.0,-0.44},{32.176,1.0,3.7},false},
  {'COL_OP_Guard_207','Block',{-2021.818,93.55,1883.828},{0.265,0.0,-0.964},{-0.964,0.0,-0.265},{14.604,1.0,3.7},false},
  {'COL_OP_Guard_208','Block',{-2521.418,89.55,1660.646},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{45.8,1.0,3.7},false},
  {'COL_OP_Guard_212','Block',{-2547.276,89.55,1661.518},{-0.342,0.0,0.94},{0.94,0.0,0.342},{19.127,1.0,3.7},false},
  {'COL_OP_Guard_214','Block',{-2559.987,89.55,1696.44},{-0.342,0.0,0.94},{0.94,0.0,0.342},{18.109,1.0,3.7},false},
  {'COL_OP_Guard_216','Block',{-2541.383,89.55,1714.039},{0.94,0.0,0.342},{0.342,0.0,-0.94},{44.755,1.0,3.7},false},
  {'COL_OP_Guard_220','Block',{-2515.995,89.55,1712.994},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{19.127,1.0,3.7},false},
  {'COL_OP_Guard_222','Block',{-2503.284,89.55,1678.072},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{18.109,1.0,3.7},false},
  {'COL_OP_Guard_224','Block',{-2019.259,89.55,1780.0},{-0.438,0.0,-0.899},{-0.899,0.0,0.438},{20.362,1.0,3.7},false},
  {'COL_OP_Guard_226','Block',{-2038.389,89.55,1756.555},{-0.725,0.0,-0.689},{-0.689,0.0,0.725},{40.236,1.0,3.7},false},
  {'COL_OP_Guard_229','Block',{-2068.87,89.55,1730.262},{-0.789,0.0,-0.614},{-0.614,0.0,0.789},{39.849,1.0,3.7},false},
  {'COL_OP_Guard_232','Block',{-2101.068,89.55,1706.464},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{39.8,1.0,3.7},false},
  {'COL_OP_Guard_235','Block',{-2126.461,89.55,1688.684},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{21.8,1.0,3.7},false},
  {'COL_OP_Guard_237','Block',{-2157.59,89.55,1666.888},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{21.8,1.0,3.7},false},
  {'COL_OP_Guard_239','Block',{-2172.927,89.55,1657.287},{-0.892,0.0,-0.452},{-0.452,0.0,0.892},{13.932,1.0,3.7},false},
  {'COL_OP_Guard_240','Block',{-2189.864,89.55,1646.73},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{25.8,1.0,3.7},false},
  {'COL_OP_Guard_242','Block',{-2213.383,89.55,1631.444},{-0.855,0.0,-0.518},{-0.518,0.0,0.855},{29.864,1.0,3.7},false},
  {'COL_OP_Guard_245','Block',{-2236.191,89.55,1620.238},{-0.949,0.0,-0.314},{-0.314,0.0,0.949},{20.637,1.0,3.7},false},
  {'COL_OP_Guard_247','Block',{-2263.733,89.55,1638.932},{-0.602,0.0,0.798},{0.798,0.0,0.602},{55.836,1.0,3.7},false},
  {'COL_OP_Guard_251','Block',{-2288.767,89.55,1666.378},{-0.857,0.0,0.516},{0.516,0.0,0.857},{19.461,1.0,3.7},false},
  {'COL_OP_Guard_253','Block',{-2306.454,89.55,1669.875},{-0.982,0.0,-0.191},{-0.191,0.0,0.982},{19.461,1.0,3.7},false},
  {'COL_OP_Guard_255','Block',{-2319.142,89.55,1670.961},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.8,1.0,3.7},false},
  {'COL_OP_Guard_256','Block',{-2329.467,89.55,1685.706},{-0.574,0.0,0.819},{0.819,0.0,0.574},{3.8,1.0,3.7},false},
  {'COL_OP_Guard_257','Block',{-2352.731,89.55,1671.858},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{55.801,1.0,3.7},false},
  {'COL_OP_Guard_261','Block',{-2382.97,89.55,1662.831},{-0.652,0.0,0.758},{0.758,0.0,0.652},{19.895,1.0,3.7},false},
  {'COL_OP_Guard_263','Block',{-2406.23,89.55,1694.215},{-0.574,0.0,0.819},{0.819,0.0,0.574},{57.8,1.0,3.7},false},
  {'COL_OP_Guard_268','Block',{-2436.056,89.55,1736.811},{-0.574,0.0,0.819},{0.819,0.0,0.574},{9.8,1.0,3.7},false},
  {'COL_OP_Guard_269','Block',{-2439.203,89.55,1744.618},{0.033,0.0,0.999},{0.999,0.0,-0.033},{6.8,1.0,3.7},false},
  {'COL_OP_Guard_270','Block',{-2303.583,89.55,1706.273},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{17.8,1.0,3.7},false},
  {'COL_OP_Guard_272','Block',{-2292.978,89.55,1694.333},{0.777,0.0,-0.63},{-0.63,0.0,-0.777},{14.32,1.0,3.7},false},
  {'COL_OP_Guard_273','Block',{-2279.573,89.55,1691.52},{0.968,0.0,0.249},{0.249,0.0,-0.968},{16.883,1.0,3.7},false},
  {'COL_OP_Guard_276','Block',{-2253.913,89.55,1703.414},{0.869,0.0,0.495},{0.495,0.0,-0.869},{11.848,1.0,3.7},false},
  {'COL_OP_Guard_277','Block',{-2034.317,89.55,1820.347},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{55.801,1.0,3.7},false},
  {'COL_OP_Guard_281','Block',{-2016.621,89.55,1793.524},{0.358,0.0,-0.934},{-0.934,0.0,-0.358},{8.015,1.0,3.7},false},
  {'COL_OP_Guard_282','Block',{-2108.189,85.55,1659.972},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.8,1.0,3.7},false},
  {'COL_OP_Guard_284','Block',{-2137.269,85.55,1639.61},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{15.8,1.0,3.7},false},
  {'COL_OP_Guard_286','Block',{-2149.959,85.55,1640.415},{-0.671,0.0,0.742},{0.742,0.0,0.671},{15.916,1.0,3.7},false},
  {'COL_OP_Guard_288','Block',{-2159.875,85.55,1654.368},{-0.48,0.0,0.877},{0.877,0.0,0.48},{17.905,1.0,3.7},false},
  {'COL_OP_Guard_290','Block',{-2115.067,85.55,1686.353},{0.661,0.0,-0.751},{-0.751,0.0,-0.661},{16.898,1.0,3.7},false},
  {'COL_OP_Guard_292','Block',{-2105.485,85.55,1672.776},{0.468,0.0,-0.884},{-0.884,0.0,-0.468},{15.917,1.0,3.7},false},
  {'COL_OP_Guard_294','Block',{-2294.972,66.55,1651.262},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{26.8,1.0,3.7},false},
  {'COL_OP_Guard_296','Block',{-2334.292,66.55,1623.731},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{44.8,1.0,3.7},false},
  {'COL_OP_Guard_300','Block',{-2367.881,66.55,1630.73},{-0.574,0.0,0.819},{0.819,0.0,0.574},{49.8,1.0,3.7},false},
  {'COL_OP_Guard_304','Block',{-2379.518,66.55,1654.323},{0.819,0.0,0.574},{0.574,0.0,-0.819},{5.8,1.0,3.7},false},
  {'COL_OP_Guard_305','Block',{-2287.609,66.55,1663.875},{0.738,0.0,-0.675},{-0.675,0.0,-0.738},{10.02,1.0,3.7},false},
  {'COL_OP_Guard_306','Block',{-2249.156,43.55,1595.534},{-0.736,0.0,-0.677},{-0.677,0.0,0.736},{30.057,1.0,3.7},false},
  {'COL_OP_Guard_309','Block',{-2276.113,43.55,1572.941},{-0.789,0.0,-0.614},{-0.614,0.0,0.789},{39.849,1.0,3.7},false},
  {'COL_OP_Guard_312','Block',{-2302.929,43.55,1555.26},{-0.902,0.0,-0.431},{-0.431,0.0,0.902},{24.117,1.0,3.7},false},
  {'COL_OP_Guard_314','Block',{-2320.999,43.55,1552.216},{-0.932,0.0,0.363},{0.363,0.0,0.932},{14.192,1.0,3.7},false},
  {'COL_OP_Guard_315','Block',{-2337.148,43.55,1548.484},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{23.8,1.0,3.7},false},
  {'COL_OP_Guard_317','Block',{-2358.122,43.55,1555.772},{-0.574,0.0,0.819},{0.819,0.0,0.574},{35.8,1.0,3.7},false},
  {'COL_OP_Guard_320','Block',{-2358.78,43.55,1578.505},{0.819,0.0,0.574},{0.574,0.0,-0.819},{22.8,1.0,3.7},false},
  {'COL_OP_Guard_322','Block',{-2358.537,43.55,1598.208},{-0.574,0.0,0.819},{0.819,0.0,0.574},{33.8,1.0,3.7},false},
  {'COL_OP_Guard_325','Block',{-2372.384,43.55,1609.266},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{11.8,1.0,3.7},false},
  {'COL_OP_Guard_326','Block',{-2389.59,43.55,1621.634},{-0.574,0.0,0.819},{0.819,0.0,0.574},{39.8,1.0,3.7},false},
  {'COL_OP_Guard_329','Block',{-2416.835,43.55,1660.543},{-0.574,0.0,0.819},{0.819,0.0,0.574},{44.8,1.0,3.7},false},
  {'COL_OP_Guard_333','Block',{-2424.989,43.55,1683.522},{0.819,0.0,0.574},{0.574,0.0,-0.819},{10.8,1.0,3.7},false},
  {'COL_OP_Guard_334','Block',{-2428.801,43.55,1698.555},{-0.574,0.0,0.819},{0.819,0.0,0.574},{30.8,1.0,3.7},false},
  {'COL_OP_Guard_337','Block',{-2452.317,43.55,1732.14},{-0.574,0.0,0.819},{0.819,0.0,0.574},{10.8,1.0,3.7},false},
  {'COL_OP_Guard_339','Block',{-2378.74,43.55,1656.698},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.8,1.0,3.7},false},
  {'COL_OP_Guard_340','Block',{-2283.668,43.55,1660.398},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.8,1.0,3.7},false},
  {'COL_OP_Guard_341','Block',{-2273.462,43.55,1650.484},{0.614,0.0,-0.789},{-0.789,0.0,-0.614},{27.834,1.0,3.7},false},
  {'COL_OP_Guard_343','Block',{-2242.733,43.55,1611.583},{0.627,0.0,-0.779},{-0.779,0.0,-0.627},{12.827,1.0,3.7},false},
  {'COL_OP_Guard_344','Block',{-2389.931,47.55,1605.036},{-0.033,0.0,-0.999},{-0.999,0.0,0.033},{9.8,1.0,3.7},false},
  {'COL_OP_Guard_345','Block',{-2395.518,47.55,1600.636},{-0.95,0.0,0.311},{0.311,0.0,0.95},{8.8,1.0,3.7},false},
  {'COL_OP_Guard_346','Block',{-2419.565,47.55,1628.715},{-0.586,0.0,0.81},{0.81,0.0,0.586},{65.806,1.0,3.7},false},
  {'COL_OP_Guard_351','Block',{-2433.342,47.55,1660.582},{0.819,0.0,0.574},{0.574,0.0,-0.819},{12.8,1.0,3.7},false},
  {'COL_OP_Guard_352','Block',{-2417.929,47.55,1651.223},{0.561,0.0,-0.828},{-0.828,0.0,-0.561},{30.803,1.0,3.7},false},
  {'COL_OP_Guard_355','Block',{-2398.288,47.55,1622.248},{0.561,0.0,-0.828},{-0.828,0.0,-0.561},{28.803,1.0,3.7},false},
  {'COL_OP_PlzMureta_001','Block',{-2224.049,93.65,1724.667},{0.819,0.0,0.574},{0.574,0.0,-0.819},{49.0,1.6,2.9},false},
  {'COL_OP_PlzMureta_002','Block',{-2258.547,93.65,1704.154},{0.911,0.0,0.413},{0.413,0.0,-0.911},{33.158,1.6,2.9},false},
  {'COL_OP_PlzMureta_003','Block',{-2283.959,93.65,1699.469},{0.985,0.0,-0.174},{-0.174,0.0,-0.985},{23.227,1.6,2.9},false},
  {'COL_OP_PlzMureta_004','Block',{-2304.809,93.65,1712.281},{0.677,0.0,-0.736},{-0.736,0.0,-0.677},{30.865,1.6,2.9},false},
  {'COL_OP_PlzMureta_005','Block',{-2136.728,93.65,1785.81},{0.819,0.0,0.574},{0.574,0.0,-0.819},{103.0,1.6,2.9},false},
  {'COL_OP_PlzMureta_006','Block',{-2324.625,93.65,1737.458},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,36.37,2.9},false},
  {'COL_OP_PlzMureta_007','Block',{-2357.539,93.65,1784.465},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,35.6,2.9},false},
  {'COL_OP_PlzMureta_008','Block',{-2140.292,93.25,1874.934},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,18.6,2.1},false},
  {'COL_OP_PlzMureta_009','Block',{-2160.94,93.25,1904.424},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,18.6,2.1},false},
  {'COL_OP_PortBollard_001','Block',{-2380.29,42.95,1611.665},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,1.5},false},
  {'COL_OP_PortBollard_002','Block',{-2388.32,42.95,1623.133},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,1.5},false},
  {'COL_OP_PortBollard_003','Block',{-2396.924,42.95,1635.42},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,1.5},false},
  {'COL_OP_PortBollard_004','Block',{-2405.527,42.95,1647.708},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,1.5},false},
  {'COL_OP_PortBollard_005','Block',{-2415.852,42.95,1662.453},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,1.5},false},
  {'COL_OP_PortBollard_006','Block',{-2425.029,42.95,1675.559},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,1.5},false},
  {'COL_OP_PortHouseH1_001','Block',{-2259.862,42.7,1608.094},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.6,16.6,1.6},true},
  {'COL_OP_PortHouseH1_002','Block',{-2259.862,51.75,1608.094},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.0,16.0,16.5},true},
  {'COL_OP_PortHouseH2_001','Block',{-2304.588,42.5,1574.335},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.6,14.6,1.2},true},
  {'COL_OP_PortHouseH2_002','Block',{-2304.588,48.35,1574.335},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.0,14.0,10.5},true},
  {'COL_OP_PortHouseH3_001','Block',{-2336.22,65.7,1647.406},{0.819,0.0,0.574},{0.574,0.0,-0.819},{24.6,14.6,1.6},true},
  {'COL_OP_PortHouseH3_002','Block',{-2336.22,74.85,1647.406},{0.819,0.0,0.574},{0.574,0.0,-0.819},{24.0,14.0,16.7},true},
  {'COL_OP_PortHouseH4_001','Block',{-2349.808,42.8,1562.204},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.0,18.0,1.2},true},
  {'COL_OP_PortHouseH4_002','Block',{-2344.932,45.0,1555.241},{0.819,0.0,0.574},{0.574,0.0,-0.819},{14.0,0.5,3.2},true},
  {'COL_OP_PortHouseH4_003','Block',{-2354.683,45.0,1569.167},{0.819,0.0,0.574},{0.574,0.0,-0.819},{14.0,0.5,3.2},true},
  {'COL_OP_PortHouseH4_004','Block',{-2355.132,45.0,1558.476},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.0,0.5,3.2},true},
  {'COL_OP_PortHouseH4_005','Block',{-2341.156,45.0,1561.181},{-0.574,0.0,0.819},{0.819,0.0,0.574},{6.4,0.5,3.2},false},
  {'COL_OP_PortHouseH4_006','Block',{-2347.81,45.0,1570.683},{-0.574,0.0,0.819},{0.819,0.0,0.574},{6.4,0.5,3.2},false},
  {'COL_OP_PortHouseH5_001','Block',{-2291.939,46.2,1633.854},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.0,1.0,8.0},false},
  {'COL_OP_PortHouseH5_002','Block',{-2286.887,46.2,1637.391},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.0,1.0,8.0},false},
  {'COL_OP_PortHouseH5_003','Block',{-2281.426,46.2,1641.215},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.0,1.0,8.0},false},
  {'COL_OP_PortHouseH5_004','Block',{-2276.375,46.2,1644.752},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.0,1.0,8.0},false},
  {'COL_OP_PortHouseH5_005','Block',{-2291.613,46.2,1649.952},{0.819,0.0,0.574},{0.574,0.0,-0.819},{20.0,1.0,8.0},false},
  {'COL_OP_PortHouseH5_006','Block',{-2292.538,43.4,1641.858},{0.819,0.0,0.574},{0.574,0.0,-0.819},{3.8,6.6,2.4},false},
  {'COL_OP_PortHouseH5_007','Block',{-2283.871,43.15,1647.438},{0.819,0.0,0.574},{0.574,0.0,-0.819},{3.4,6.4,1.9},false},
  {'COL_OP_PortProp_001','Block',{-2372.344,46.5,1613.567},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,8.6},false},
  {'COL_OP_PortProp_002','Block',{-2349.401,46.5,1580.801},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.4,1.4,8.6},false},
  {'COL_OP_PortProp_003','Block',{-2364.672,67.4,1643.843},{-0.574,0.0,0.819},{0.819,0.0,0.574},{2.0,1.7,4.4},false},
  {'COL_OP_PortProp_004','Block',{-2372.243,67.4,1654.655},{-0.574,0.0,0.819},{0.819,0.0,0.574},{2.0,1.7,4.4},false},
  {'COL_OP_PortProp_005','Block',{-2274.947,44.4,1599.301},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,1.7,4.4},false},
  {'COL_OP_PortProp_006','Block',{-2285.76,44.4,1591.73},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,1.7,4.4},false},
  {'COL_OP_PortProp_007','Block',{-2261.748,43.4,1620.202},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{6.4,3.4,2.4},false},
  {'COL_OP_PortProp_008','Block',{-2305.868,43.5,1589.065},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.2,3.0,2.6},false},
  {'COL_OP_PortProp_009','Block',{-2316.533,43.0,1578.667},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,1.6},false},
  {'COL_OP_PortProp_010','Block',{-2325.037,66.05,1643.639},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.6,2.0,1.7},false},
  {'COL_OP_PortProp_011','Block',{-2337.497,66.15,1635.281},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.2,2.0,1.9},false},
  {'COL_OP_PropAndon_001','Block',{-2107.542,96.3,1901.039},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.1,1.1,7.6},false},
  {'COL_OP_PropAndon_002','Block',{-2090.827,96.3,1936.793},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.1,1.1,7.6},false},
  {'COL_OP_PropAndon_003','Block',{-2226.627,92.3,1674.825},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropBanca_001','Block',{-2105.222,89.9,1768.013},{0.819,0.0,0.574},{0.574,0.0,-0.819},{5.0,2.4,2.8},false},
  {'COL_OP_PropBanca_002','Block',{-2109.809,89.9,1764.801},{0.819,0.0,0.574},{0.574,0.0,-0.819},{5.0,2.4,2.8},false},
  {'COL_OP_PropBanca_003','Block',{-2069.67,89.9,1792.906},{0.819,0.0,0.574},{0.574,0.0,-0.819},{5.0,2.4,2.8},false},
  {'COL_OP_PropBanca_004','Block',{-2074.422,89.9,1789.579},{0.819,0.0,0.574},{0.574,0.0,-0.819},{5.0,2.4,2.8},false},
  {'COL_OP_PropBanca_005','Block',{-2095.979,89.9,1752.023},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{5.0,2.4,2.8},false},
  {'COL_OP_PropBanner_001','Block',{-2401.701,98.2,1820.075},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,12.0},false},
  {'COL_OP_PropBanner_002','Block',{-2409.731,98.2,1831.543},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,12.0},false},
  {'COL_OP_PropBanner_003','Block',{-2172.554,100.2,1763.227},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_004','Block',{-2212.692,100.2,1735.122},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_005','Block',{-2120.95,101.2,1817.672},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_006','Block',{-2281.503,101.2,1705.251},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_007','Block',{-2223.208,101.2,1946.278},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_008','Block',{-2374.914,101.2,1835.169},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_009','Block',{-2329.337,100.2,1751.597},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_010','Block',{-2346.085,100.2,1775.516},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_011','Block',{-2146.158,100.2,1879.128},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_012','Block',{-2159.006,100.2,1897.477},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBench_001','Block',{-2142.012,93.05,1873.729},{-0.574,0.0,0.819},{0.819,0.0,0.574},{9.0,1.8,1.7},false},
  {'COL_OP_PropBench_002','Block',{-2162.66,93.05,1903.219},{-0.574,0.0,0.819},{0.819,0.0,0.574},{9.0,1.8,1.7},false},
  {'COL_OP_PropBench_003','Block',{-2316.734,93.05,1730.635},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_004','Block',{-2361.473,93.05,1794.528},{-0.574,0.0,0.819},{0.819,0.0,0.574},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_005','Block',{-2272.342,93.05,1925.79},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_006','Block',{-2251.536,93.05,1937.917},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_007','Block',{-2331.321,93.05,1884.492},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_008','Block',{-2349.834,93.05,1869.088},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_009','Block',{-2216.695,93.05,1947.786},{-0.997,0.0,0.075},{0.075,0.0,0.997},{7.0,1.8,1.7},false},
  {'COL_OP_PropBench_010','Block',{-2371.023,93.05,1839.724},{-0.271,0.0,-0.963},{-0.963,0.0,0.271},{7.0,1.8,1.7},false},
  {'COL_OP_PropCarga_001','Block',{-2082.31,89.6,1785.154},{0.819,0.0,0.574},{0.574,0.0,-0.819},{3.0,2.6,2.2},false},
  {'COL_OP_PropCarga_002','Block',{-2057.11,89.6,1779.849},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.0,2.6,2.2},false},
  {'COL_OP_PropCarga_003','Block',{-2072.128,93.6,1849.416},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{3.0,2.6,2.2},false},
  {'COL_OP_PropCarga_004','Block',{-2091.629,93.6,1877.267},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{3.0,2.6,2.2},false},
  {'COL_OP_PropCarga_005','Block',{-2246.809,89.6,1648.729},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.0,2.6,2.2},false},
  {'COL_OP_PropCarga_006','Block',{-2240.503,89.6,1664.132},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.0,2.6,2.2},false},
  {'COL_OP_PropCarrinho_001','Block',{-2115.466,89.8,1739.232},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{6.8,3.6,2.6},false},
  {'COL_OP_PropCarrinho_002','Block',{-2124.774,93.8,1924.254},{-0.574,0.0,0.819},{0.819,0.0,0.574},{6.8,3.6,2.6},false},
  {'COL_OP_PropChozuya_001','Block',{-2430.932,94.0,1824.511},{0.819,0.0,0.574},{0.574,0.0,-0.819},{4.4,3.4,3.0},false},
  {'COL_OP_PropEma_001','Block',{-2421.36,94.3,1806.309},{-0.574,0.0,0.819},{0.819,0.0,0.574},{3.8,0.7,3.6},false},
  {'COL_OP_PropEstandarte_001','Block',{-2124.886,94.0,1732.636},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,11.0},false},
  {'COL_OP_PropEstandarte_002','Block',{-2129.026,94.0,1749.88},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,11.0},false},
  {'COL_OP_PropLamp_001','Block',{-2173.465,90.4,1747.269},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,1.7,4.4},false},
  {'COL_OP_PropLamp_002','Block',{-2197.384,90.4,1730.52},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,1.7,4.4},false},
  {'COL_OP_PropLamp_003','Block',{-2147.64,92.7,1698.88},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_004','Block',{-2167.629,92.7,1699.533},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_005','Block',{-2160.832,92.7,1717.721},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_006','Block',{-2181.395,92.7,1719.192},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_007','Block',{-2110.386,96.62,1848.264},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,8.6},false},
  {'COL_OP_PropLamp_008','Block',{-2176.462,96.62,1942.63},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,8.6},false},
  {'COL_OP_PropLamp_009','Block',{-2052.473,92.52,1780.898},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,8.4},false},
  {'COL_OP_PropLamp_010','Block',{-2223.545,104.52,2015.625},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,8.4},false},
  {'COL_OP_PropLamp_011','Block',{-2262.211,92.52,1648.932},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,8.4},false},
  {'COL_OP_PropLamp_012','Block',{-2281.328,96.0,1912.906},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_013','Block',{-2316.142,96.0,1888.529},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_014','Block',{-2321.323,96.0,1738.408},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_015','Block',{-2355.737,96.0,1787.558},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_016','Block',{-2134.965,96.0,1862.794},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_017','Block',{-2170.527,96.0,1913.581},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_018','Block',{-2366.554,96.0,1809.282},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_019','Block',{-2184.373,96.0,1922.198},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_020','Block',{-2262.398,96.0,1932.509},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_021','Block',{-2341.036,96.0,1877.446},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropPlaca_001','Block',{-2217.784,91.65,1709.094},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.6,0.6,6.3},false},
  {'COL_OP_PropPlaca_002','Block',{-2162.293,91.5,1733.056},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.6,0.6,6.3},false},
  {'COL_OP_PropPoco_001','Block',{-2065.809,89.7,1772.049},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.6,3.6,2.4},false},
  {'COL_OP_PropPoco_002','Block',{-2049.647,93.7,1902.391},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,3.6,2.4},false},
  {'COL_OP_PropPoste_001','Block',{-2099.774,92.7,1769.996},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,8.4},false},
  {'COL_OP_PropSaisen_001','Block',{-2416.774,94.2,1818.065},{-0.574,0.0,0.819},{0.819,0.0,0.574},{2.4,1.1,1.2},false},
  {'COL_OP_PropToro_001','Block',{-2133.411,95.3,1883.414},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.4,2.4,6.2},false},
  {'COL_OP_PropToro_002','Block',{-2407.746,95.7,1817.551},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.6,2.6,7.0},false},
  {'COL_OP_PropToro_003','Block',{-2414.17,95.7,1826.725},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.6,2.6,7.0},false},
  {'COL_OP_PropToro_004','Block',{-2177.567,96.0,1761.67},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,7.6},false},
  {'COL_OP_PropToro_005','Block',{-2209.514,96.0,1739.301},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,7.6},false},
  {'COL_OP_ShipCabin_001','Block',{-2432.367,50.0,1659.19},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{15.143,14.8,7.6},true},
  {'COL_OP_ShipMast_001','Block',{-2404.376,50.7,1619.215},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.2,2.2,9.0},false},
  {'COL_OP_ShipMast_002','Block',{-2419.289,50.7,1640.513},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.2,2.2,9.0},false},
  {'COL_OP_ShipProp_001','Block',{-2396.977,46.55,1608.648},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.0,5.0,0.7},false},
  {'COL_OP_ShipProp_002','Block',{-2425.599,47.35,1649.524},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,2.3},false},
  {'COL_OP_ShipProp_003','Block',{-2413.036,47.4,1621.209},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.4,7.0,2.4},false},
  {'COL_OP_StairAdro_001','Ramp',{-2306.244,94.738,1911.442},{-0.529,0.385,0.756},{0.819,-0.0,0.574},{15.6,30.0,1.0},false},
  {'COL_OP_StairAdro_002','Block',{-2310.608,97.7,1917.674},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,30.0,1.0},false},
  {'COL_OP_StairAdro_003','Ramp',{-2319.145,96.389,1902.668},{-0.529,0.385,0.756},{0.819,-0.0,0.574},{15.6,1.2,5.5},false},
  {'COL_OP_StairAdro_004','Ramp',{-2293.587,96.389,1920.564},{-0.529,0.385,0.756},{0.819,-0.0,0.574},{15.6,1.2,5.5},false},
  {'COL_OP_StairCasteloA_001','Ramp',{-2270.283,107.239,1983.869},{-0.528,0.389,0.755},{0.819,-0.0,0.574},{48.847,12.0,1.0},false},
  {'COL_OP_StairCasteloA_002','Block',{-2283.421,116.7,2002.632},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,12.0,1.0},false},
  {'COL_OP_StairCasteloA_003','Ramp',{-2275.807,108.884,1980.252},{-0.528,0.389,0.755},{0.819,-0.0,0.574},{48.847,1.2,5.5},false},
  {'COL_OP_StairCasteloA_004','Ramp',{-2264.994,108.884,1987.823},{-0.528,0.389,0.755},{0.819,-0.0,0.574},{48.847,1.2,5.5},false},
  {'COL_OP_StairCasteloB_001','Ramp',{-2303.55,126.239,2031.38},{-0.528,0.389,0.755},{0.819,-0.0,0.574},{48.847,12.0,1.0},false},
  {'COL_OP_StairCasteloB_002','Block',{-2316.688,135.7,2050.143},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,12.0,1.0},false},
  {'COL_OP_StairCasteloB_003','Ramp',{-2309.075,127.884,2027.763},{-0.528,0.389,0.755},{0.819,-0.0,0.574},{48.847,1.2,5.5},false},
  {'COL_OP_StairCasteloB_004','Ramp',{-2298.262,127.884,2035.334},{-0.528,0.389,0.755},{0.819,-0.0,0.574},{48.847,1.2,5.5},false},
  {'COL_OP_StairChegada_001','Ramp',{-2145.403,85.731,1681.737},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,16.0,1.0},false},
  {'COL_OP_StairChegada_002','Block',{-2148.744,87.7,1686.51},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,16.0,1.0},false},
  {'COL_OP_StairChegada_003','Ramp',{-2152.602,87.432,1677.025},{-0.538,0.347,0.768},{0.819,-0.0,0.574},{11.517,1.2,5.5},false},
  {'COL_OP_StairChegada_004','Ramp',{-2138.513,87.432,1686.891},{-0.538,0.347,0.768},{0.819,-0.0,0.574},{11.517,1.2,5.5},false},
  {'COL_OP_StairOesteAlta_001','Ramp',{-2203.573,95.736,1956.592},{-0.532,0.375,0.76},{0.819,-0.0,0.574},{21.355,12.0,1.0},false},
  {'COL_OP_StairOesteAlta_002','Block',{-2209.488,99.7,1965.04},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,12.0,1.0},false},
  {'COL_OP_StairOesteAlta_003','Ramp',{-2209.11,97.402,1952.993},{-0.532,0.375,0.76},{0.819,-0.0,0.574},{21.355,1.2,5.5},false},
  {'COL_OP_StairOesteAlta_004','Ramp',{-2198.297,97.402,1960.564},{-0.532,0.375,0.76},{0.819,-0.0,0.574},{21.355,1.2,5.5},false},
  {'COL_OP_StairPortoA_001','Ramp',{-2346.466,76.24,1664.647},{0.754,0.392,0.528},{0.574,-0.0,-0.819},{58.694,12.0,1.0},false},
  {'COL_OP_StairPortoA_002','Block',{-2324.018,87.7,1680.365},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.2,12.0,1.0},false},
  {'COL_OP_StairPortoA_003','Ramp',{-2350.087,77.88,1670.169},{0.754,0.392,0.528},{0.574,-0.0,-0.819},{58.694,1.2,5.5},false},
  {'COL_OP_StairPortoA_004','Ramp',{-2342.516,77.88,1659.356},{0.754,0.392,0.528},{0.574,-0.0,-0.819},{58.694,1.2,5.5},false},
  {'COL_OP_StairPortoB_001','Ramp',{-2295.752,53.24,1617.506},{-0.528,0.392,0.754},{0.819,-0.0,0.574},{58.694,12.0,1.0},false},
  {'COL_OP_StairPortoB_002','Block',{-2311.47,64.7,1639.954},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,12.0,1.0},false},
  {'COL_OP_StairPortoB_003','Ramp',{-2301.274,54.88,1613.886},{-0.528,0.392,0.754},{0.819,-0.0,0.574},{58.694,1.2,5.5},false},
  {'COL_OP_StairPortoB_004','Ramp',{-2290.461,54.88,1621.457},{-0.528,0.392,0.754},{0.819,-0.0,0.574},{58.694,1.2,5.5},false},
  {'COL_OP_StairPraca_001','Ramp',{-2188.421,89.731,1743.173},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,28.0,1.0},false},
  {'COL_OP_StairPraca_002','Block',{-2191.763,91.7,1747.946},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,28.0,1.0},false},
  {'COL_OP_StairPraca_003','Ramp',{-2200.535,91.432,1735.02},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,1.2,5.5},false},
  {'COL_OP_StairPraca_004','Ramp',{-2176.616,91.432,1751.769},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,1.2,5.5},false},
  {'COL_OP_StairSudoeste_001','Ramp',{-2073.74,89.731,1823.474},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,10.0,1.0},false},
  {'COL_OP_StairSudoeste_002','Block',{-2077.081,91.7,1828.247},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,10.0,1.0},false},
  {'COL_OP_StairSudoeste_003','Ramp',{-2078.482,91.432,1820.483},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,1.2,5.5},false},
  {'COL_OP_StairSudoeste_004','Ramp',{-2069.307,91.432,1826.907},{-0.538,0.347,0.768},{0.819,0.0,0.574},{11.517,1.2,5.5},false},
  {'COL_OP_StairSummon_001','Ramp',{-2347.317,89.731,1756.831},{0.768,0.347,0.538},{0.574,0.0,-0.819},{11.517,14.0,1.0},false},
  {'COL_OP_StairSummon_002','Block',{-2342.544,91.7,1760.172},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.2,14.0,1.0},false},
  {'COL_OP_StairSummon_003','Ramp',{-2351.455,91.432,1763.211},{0.768,0.347,0.538},{0.574,-0.0,-0.819},{11.517,1.2,5.5},false},
  {'COL_OP_StairSummon_004','Ramp',{-2342.736,91.432,1750.76},{0.768,0.347,0.538},{0.574,-0.0,-0.819},{11.517,1.2,5.5},false},
  {'COL_OP_Terrain_001','Block',{-2314.408,83.1,2069.771},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{11.75,34.94,106.2},false},
  {'COL_OP_Terrain_006','Block',{-2327.705,83.1,1941.471},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{103.745,8.0,106.2},false},
  {'COL_OP_Terrain_007','Block',{-2333.49,83.1,1947.187},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{119.11,8.0,106.2},false},
  {'COL_OP_Terrain_008','Block',{-2337.702,83.1,1954.003},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{130.215,8.0,106.2},false},
  {'COL_OP_Terrain_009','Block',{-2342.677,83.1,1960.287},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{131.156,8.0,106.2},false},
  {'COL_OP_Terrain_010','Block',{-2347.651,83.1,1966.57},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{132.097,8.0,106.2},false},
  {'COL_OP_Terrain_011','Block',{-2352.625,83.1,1972.853},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{133.038,8.0,106.2},false},
  {'COL_OP_Terrain_012','Block',{-2357.599,83.1,1979.136},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{133.979,8.0,106.2},false},
  {'COL_OP_Terrain_013','Block',{-2362.573,83.1,1985.42},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{134.921,8.0,106.2},false},
  {'COL_OP_Terrain_014','Block',{-2367.547,83.1,1991.703},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{135.862,8.0,106.2},false},
  {'COL_OP_Terrain_015','Block',{-2372.521,83.1,1997.986},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{136.803,8.0,106.2},false},
  {'COL_OP_Terrain_016','Block',{-2379.79,83.1,2007.546},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{137.744,16.0,106.2},false},
  {'COL_OP_Terrain_018','Block',{-2385.262,83.1,2018.364},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{134.3,8.0,106.2},false},
  {'COL_OP_Terrain_019','Block',{-2388.446,83.1,2025.9},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{130.871,8.0,106.2},false},
  {'COL_OP_Terrain_020','Block',{-2391.631,83.1,2033.437},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{127.443,8.0,106.2},false},
  {'COL_OP_Terrain_021','Block',{-2385.67,83.1,2044.935},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{104.488,4.0,106.2},false},
  {'COL_OP_Terrain_022','Block',{-2326.037,83.1,2063.495},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.5,32.0,106.2},false},
  {'COL_OP_Terrain_026','Block',{-2336.094,83.1,2076.658},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.125,1.1,106.2},false},
  {'COL_OP_Terrain_027','Block',{-2280.953,73.6,2013.273},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.75,16.0,87.2},false},
  {'COL_OP_Terrain_029','Block',{-2287.792,73.6,2009.094},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.25,15.0,87.2},false},
  {'COL_OP_Terrain_031','Block',{-2161.873,65.1,1994.108},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{96.854,8.0,70.2},false},
  {'COL_OP_Terrain_032','Block',{-2165.594,65.1,2001.269},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.972,8.0,70.2},false},
  {'COL_OP_Terrain_033','Block',{-2169.315,65.1,2008.429},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{101.09,8.0,70.2},false},
  {'COL_OP_Terrain_034','Block',{-2173.036,65.1,2015.59},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{103.207,8.0,70.2},false},
  {'COL_OP_Terrain_035','Block',{-2177.481,65.1,2022.243},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{103.558,8.0,70.2},false},
  {'COL_OP_Terrain_036','Block',{-2182.229,65.1,2028.685},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{103.168,8.0,70.2},false},
  {'COL_OP_Terrain_037','Block',{-2187.133,65.1,2035.017},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{102.399,8.0,70.2},false},
  {'COL_OP_Terrain_038','Block',{-2192.037,65.1,2041.35},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{101.63,8.0,70.2},false},
  {'COL_OP_Terrain_039','Block',{-2196.941,65.1,2047.683},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{100.861,8.0,70.2},false},
  {'COL_OP_Terrain_040','Block',{-2201.844,65.1,2054.015},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{100.091,8.0,70.2},false},
  {'COL_OP_Terrain_041','Block',{-2206.748,65.1,2060.348},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{99.322,8.0,70.2},false},
  {'COL_OP_Terrain_042','Block',{-2211.966,65.1,2066.46},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{97.785,8.0,70.2},false},
  {'COL_OP_Terrain_043','Block',{-2218.097,65.1,2071.934},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{94.021,8.0,70.2},false},
  {'COL_OP_Terrain_044','Block',{-2224.227,65.1,2077.407},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{90.256,8.0,70.2},false},
  {'COL_OP_Terrain_045','Block',{-2230.358,65.1,2082.881},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{86.491,8.0,70.2},false},
  {'COL_OP_Terrain_046','Block',{-2236.517,65.1,2088.334},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{82.656,8.0,70.2},false},
  {'COL_OP_Terrain_047','Block',{-2243.065,65.1,2093.515},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{57.441,8.0,70.2},false},
  {'COL_OP_Terrain_048','Block',{-2233.617,65.1,1984.463},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.75,56.0,70.2},false},
  {'COL_OP_Terrain_055','Block',{-2251.798,65.1,2010.797},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.326,8.0,70.2},false},
  {'COL_OP_Terrain_056','Block',{-2256.125,65.1,2017.534},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.686,8.0,70.2},false},
  {'COL_OP_Terrain_057','Block',{-2260.451,65.1,2024.271},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.046,8.0,70.2},false},
  {'COL_OP_Terrain_058','Block',{-2263.953,65.1,2029.83},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.406,5.125,70.2},false},
  {'COL_OP_Terrain_059','Block',{-2234.898,65.1,2001.328},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.5,88.0,70.2},false},
  {'COL_OP_Terrain_070','Block',{-2262.381,65.1,2040.682},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.382,8.0,70.2},false},
  {'COL_OP_Terrain_071','Block',{-2266.708,65.1,2047.418},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.742,8.0,70.2},false},
  {'COL_OP_Terrain_072','Block',{-2270.109,65.1,2054.802},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{10.845,8.0,70.2},false},
  {'COL_OP_Terrain_073','Block',{-2268.257,65.1,2061.222},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.445,0.392,70.2},false},
  {'COL_OP_Terrain_074','Block',{-2265.05,64.1,1948.719},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{77.75,24.0,68.2},false},
  {'COL_OP_Terrain_077','Block',{-2254.67,64.1,1975.52},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{30.0,8.0,68.2},false},
  {'COL_OP_Terrain_078','Block',{-2351.853,64.1,1878.173},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{80.386,8.0,68.2},false},
  {'COL_OP_Terrain_079','Block',{-2356.704,64.1,1884.543},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{81.026,8.0,68.2},false},
  {'COL_OP_Terrain_080','Block',{-2361.554,64.1,1890.913},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{81.666,8.0,68.2},false},
  {'COL_OP_Terrain_081','Block',{-2365.704,64.1,1893.5},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{77.996,1.0,68.2},false},
  {'COL_OP_Terrain_082','Block',{-2313.074,64.1,1921.197},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{32.5,8.0,68.2},false},
  {'COL_OP_Terrain_083','Block',{-2113.573,61.1,1911.954},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{23.75,182.0,62.2},false},
  {'COL_OP_Terrain_106','Block',{-2182.646,61.1,1864.809},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{118.5,184.0,62.2},false},
  {'COL_OP_Terrain_129','Block',{-2248.275,61.1,1936.05},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{92.7,8.0,62.2},false},
  {'COL_OP_Terrain_130','Block',{-2254.993,61.1,1938.671},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{84.7,4.0,62.2},false},
  {'COL_OP_Terrain_131','Block',{-2128.929,61.1,1902.301},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.5,180.2,62.2},false},
  {'COL_OP_Terrain_154','Block',{-2239.561,61.1,1717.529},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{82.7,8.0,62.2},false},
  {'COL_OP_Terrain_155','Block',{-2247.426,61.1,1721.788},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{90.7,8.0,62.2},false},
  {'COL_OP_Terrain_156','Block',{-2254.599,61.1,1726.532},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{97.01,8.0,62.2},false},
  {'COL_OP_Terrain_157','Block',{-2259.624,61.1,1732.779},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.077,8.0,62.2},false},
  {'COL_OP_Terrain_158','Block',{-2264.65,61.1,1739.026},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{99.143,8.0,62.2},false},
  {'COL_OP_Terrain_159','Block',{-2269.675,61.1,1745.274},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{100.21,8.0,62.2},false},
  {'COL_OP_Terrain_160','Block',{-2299.721,61.1,1787.716},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{100.75,96.0,62.2},false},
  {'COL_OP_Terrain_172','Block',{-2343.396,61.1,1849.913},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{100.95,55.999,62.2},false},
  {'COL_OP_Terrain_179','Block',{-2431.234,61.1,1827.473},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{107.624,8.0,62.2},false},
  {'COL_OP_Terrain_180','Block',{-2433.797,61.1,1835.445},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{99.769,8.0,62.2},false},
  {'COL_OP_Terrain_181','Block',{-2434.639,61.1,1840.959},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{91.915,2.0,62.2},false},
  {'COL_OP_Terrain_182','Block',{-2414.776,61.1,1770.634},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{106.936,8.0,62.2},false},
  {'COL_OP_Terrain_183','Block',{-2419.832,61.1,1776.86},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{108.079,8.0,62.2},false},
  {'COL_OP_Terrain_184','Block',{-2424.889,61.1,1783.085},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{109.221,8.0,62.2},false},
  {'COL_OP_Terrain_185','Block',{-2429.714,61.1,1789.473},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{109.8,8.0,62.2},false},
  {'COL_OP_Terrain_186','Block',{-2433.027,61.1,1796.919},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{106.684,8.0,62.2},false},
  {'COL_OP_Terrain_187','Block',{-2435.095,61.1,1805.237},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{100.531,8.0,62.2},false},
  {'COL_OP_Terrain_188','Block',{-2437.163,61.1,1813.555},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{94.377,8.0,62.2},false},
  {'COL_OP_Terrain_202','Block',{-2247.63,61.1,1827.731},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{30.5,194.2,62.2},false},
  {'COL_OP_Terrain_227','Block',{-2034.359,61.1,1866.096},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{37.411,8.0,62.2},false},
  {'COL_OP_Terrain_228','Block',{-2037.778,61.1,1873.469},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{40.268,8.0,62.2},false},
  {'COL_OP_Terrain_229','Block',{-2041.686,61.1,1880.498},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{41.93,8.0,62.2},false},
  {'COL_OP_Terrain_230','Block',{-2045.762,61.1,1887.41},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{43.18,8.0,62.2},false},
  {'COL_OP_Terrain_231','Block',{-2049.839,61.1,1894.322},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{44.43,8.0,62.2},false},
  {'COL_OP_Terrain_232','Block',{-2053.916,61.1,1901.234},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{45.68,8.0,62.2},false},
  {'COL_OP_Terrain_233','Block',{-2069.844,61.1,1924.261},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{46.0,48.0,62.2},false},
  {'COL_OP_Terrain_239','Block',{-2085.974,61.1,1947.149},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{45.831,8.0,62.2},false},
  {'COL_OP_Terrain_240','Block',{-2090.699,61.1,1953.607},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{45.498,8.0,62.2},false},
  {'COL_OP_Terrain_241','Block',{-2095.424,61.1,1960.065},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{45.165,8.0,62.2},false},
  {'COL_OP_Terrain_242','Block',{-2100.149,61.1,1966.522},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{44.831,8.0,62.2},false},
  {'COL_OP_Terrain_243','Block',{-2104.874,61.1,1972.98},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{44.498,8.0,62.2},false},
  {'COL_OP_Terrain_244','Block',{-2109.599,61.1,1979.438},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{44.165,8.0,62.2},false},
  {'COL_OP_Terrain_245','Block',{-2114.646,61.1,1985.67},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{43.047,8.0,62.2},false},
  {'COL_OP_Terrain_246','Block',{-2120.005,61.1,1991.684},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{41.165,8.0,62.2},false},
  {'COL_OP_Terrain_247','Block',{-2125.365,61.1,1997.697},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{39.282,8.0,62.2},false},
  {'COL_OP_Terrain_248','Block',{-2130.724,61.1,2003.71},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{37.4,8.0,62.2},false},
  {'COL_OP_Terrain_249','Block',{-2141.722,61.1,2002.113},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{17.55,2.0,62.2},false},
  {'COL_OP_Terrain_250','Block',{-2514.02,59.1,1664.19},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{31.8,8.0,58.2},false},
  {'COL_OP_Terrain_251','Block',{-2523.767,59.1,1667.131},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{48.681,8.0,58.2},false},
  {'COL_OP_Terrain_252','Block',{-2527.033,59.1,1674.61},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{49.74,8.0,58.2},false},
  {'COL_OP_Terrain_253','Block',{-2529.865,59.1,1682.393},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{49.74,8.0,58.2},false},
  {'COL_OP_Terrain_254','Block',{-2532.698,59.1,1690.176},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{49.74,8.0,58.2},false},
  {'COL_OP_Terrain_255','Block',{-2535.531,59.1,1697.959},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{49.74,8.0,58.2},false},
  {'COL_OP_Terrain_256','Block',{-2538.797,59.1,1705.438},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{48.681,8.0,58.2},false},
  {'COL_OP_Terrain_257','Block',{-2545.271,59.1,1710.671},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{39.79,8.0,58.2},false},
  {'COL_OP_Terrain_258','Block',{-2559.489,59.1,1706.818},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.79,1.997,58.2},false},
  {'COL_OP_Terrain_259','Block',{-2079.928,59.1,1726.76},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{140.417,8.0,58.2},false},
  {'COL_OP_Terrain_260','Block',{-2078.519,59.1,1737.513},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{155.06,8.0,58.2},false},
  {'COL_OP_Terrain_261','Block',{-2080.987,59.1,1745.551},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{160.238,8.0,58.2},false},
  {'COL_OP_Terrain_262','Block',{-2099.992,59.1,1773.14},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{160.75,59.0,58.2},false},
  {'COL_OP_Terrain_270','Block',{-2195.155,59.1,1646.077},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{103.917,8.0,58.2},false},
  {'COL_OP_Terrain_271','Block',{-2202.629,59.1,1650.61},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{110.963,8.0,58.2},false},
  {'COL_OP_Terrain_272','Block',{-2207.335,59.1,1657.081},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{111.248,8.0,58.2},false},
  {'COL_OP_Terrain_273','Block',{-2212.041,59.1,1663.552},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{111.534,8.0,58.2},false},
  {'COL_OP_Terrain_274','Block',{-2216.746,59.1,1670.024},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{111.82,8.0,58.2},false},
  {'COL_OP_Terrain_275','Block',{-2221.452,59.1,1676.495},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{112.105,8.0,58.2},false},
  {'COL_OP_Terrain_276','Block',{-2226.158,59.1,1682.966},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{112.391,8.0,58.2},false},
  {'COL_OP_Terrain_277','Block',{-2230.863,59.1,1689.438},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{112.677,8.0,58.2},false},
  {'COL_OP_Terrain_278','Block',{-2236.565,59.1,1695.211},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{115.394,8.0,58.2},false},
  {'COL_OP_Terrain_279','Block',{-2242.61,59.1,1700.745},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{118.95,8.0,58.2},false},
  {'COL_OP_Terrain_280','Block',{-2251.576,59.1,1704.233},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{129.638,8.0,58.2},false},
  {'COL_OP_Terrain_281','Block',{-2297.175,59.1,1682.07},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{45.333,8.0,58.2},false},
  {'COL_OP_Terrain_282','Block',{-2306.552,59.1,1685.271},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{33.643,8.0,58.2},false},
  {'COL_OP_Terrain_283','Block',{-2312.076,59.1,1691.169},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{31.357,8.0,58.2},false},
  {'COL_OP_Terrain_284','Block',{-2348.441,59.1,1742.615},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{30.8,117.999,58.2},false},
  {'COL_OP_Terrain_299','Block',{-2378.042,59.1,1659.629},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.095,8.0,58.2},false},
  {'COL_OP_Terrain_300','Block',{-2382.958,59.1,1665.953},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.895,8.0,58.2},false},
  {'COL_OP_Terrain_301','Block',{-2412.872,59.1,1708.324},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.3,95.733,58.2},false},
  {'COL_OP_Terrain_313','Block',{-2318.017,59.1,1671.271},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.2,7.283,58.2},false},
  {'COL_OP_Terrain_314','Block',{-2383.901,59.1,1718.548},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{54.9,116.75,58.2},false},
  {'COL_OP_Terrain_329','Block',{-2169.623,59.1,1716.326},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.5,72.2,58.2},false},
  {'COL_OP_Terrain_339','Block',{-2125.514,57.1,1653.334},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{53.987,8.0,54.2},false},
  {'COL_OP_Terrain_340','Block',{-2132.397,57.1,1663.164},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{55.987,16.0,54.2},false},
  {'COL_OP_Terrain_342','Block',{-2139.28,57.1,1672.994},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{54.211,8.0,54.2},false},
  {'COL_OP_Terrain_343','Block',{-2142.148,57.1,1677.089},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{52.433,2.0,54.2},false},
  {'COL_OP_Terrain_344','Block',{-2302.985,47.6,1651.145},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{41.239,8.0,35.2},false},
  {'COL_OP_Terrain_345','Block',{-2308.302,47.6,1657.188},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{39.461,8.0,35.2},false},
  {'COL_OP_Terrain_346','Block',{-2313.618,47.6,1663.232},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{37.683,8.0,35.2},false},
  {'COL_OP_Terrain_347','Block',{-2323.96,47.6,1665.757},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{23.638,8.0,35.2},false},
  {'COL_OP_Terrain_348','Block',{-2332.64,47.6,1674.329},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{19.25,16.0,35.2},false},
  {'COL_OP_Terrain_351','Block',{-2349.839,47.6,1643.974},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{43.75,50.0,35.2},false},
  {'COL_OP_Terrain_365','Block',{-2277.21,36.1,1576.414},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{96.503,8.0,12.2},false},
  {'COL_OP_Terrain_366','Block',{-2283.986,36.1,1581.436},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{101.83,8.0,12.2},false},
  {'COL_OP_Terrain_367','Block',{-2298.637,36.1,1580.943},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{125.33,8.0,12.2},false},
  {'COL_OP_Terrain_368','Block',{-2303.444,36.1,1587.344},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{124.797,8.0,12.2},false},
  {'COL_OP_Terrain_369','Block',{-2308.251,36.1,1593.744},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{124.263,8.0,12.2},false},
  {'COL_OP_Terrain_370','Block',{-2313.03,36.1,1600.163},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{123.798,8.0,12.2},false},
  {'COL_OP_Terrain_371','Block',{-2316.636,36.1,1604.964},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{123.397,4.0,12.2},false},
  {'COL_OP_Terrain_372','Block',{-2310.329,36.1,1616.704},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{99.198,8.0,12.2},false},
  {'COL_OP_Terrain_373','Block',{-2315.082,36.1,1623.143},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.798,8.0,12.2},false},
  {'COL_OP_Terrain_374','Block',{-2319.834,36.1,1629.581},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.397,8.0,12.2},false},
  {'COL_OP_Terrain_375','Block',{-2358.744,36.1,1613.323},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.0,10.0,12.2},false},
  {'COL_OP_Terrain_377','Block',{-2392.339,36.1,1650.839},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{28.0,90.0,12.2},false},
  {'COL_OP_Terrain_389','Block',{-2431.015,36.1,1716.536},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.0,61.999,12.2},false},
  {'COL_OP_Terrain_397','Block',{-2392.905,45.2,1602.832},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{11.925,8.0,2.0},false},
  {'COL_OP_Terrain_398','Block',{-2397.493,45.2,1609.385},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.241,8.0,2.0},false},
  {'COL_OP_Terrain_399','Block',{-2402.082,45.2,1615.938},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.483,8.0,2.0},false},
  {'COL_OP_Terrain_400','Block',{-2406.671,45.2,1622.492},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.726,8.0,2.0},false},
  {'COL_OP_Terrain_401','Block',{-2411.259,45.2,1629.045},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.968,8.0,2.0},false},
  {'COL_OP_Terrain_402','Block',{-2415.848,45.2,1635.598},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.211,8.0,2.0},false},
  {'COL_OP_Terrain_403','Block',{-2420.437,45.2,1642.151},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.453,8.0,2.0},false},
  {'COL_OP_Terrain_404','Block',{-2425.025,45.2,1648.704},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.695,8.0,2.0},false},
  {'COL_OP_Terrain_405','Block',{-2430.187,45.2,1656.077},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.938,10.0,2.0},false},
  {'COL_OP_Terrain_407','Block',{-2145.819,57.1,1682.332},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.5,10.8,54.2},false},
  {'COL_OP_Terrain_408','Block',{-2191.418,59.1,1747.454},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{30.5,1.8,58.2},false},
  {'COL_OP_Terrain_409','Block',{-2076.737,59.1,1827.755},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.5,1.8,58.2},false},
  {'COL_OP_Terrain_410','Block',{-2206.829,61.1,1962.507},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.05,7.8,62.2},false},
  {'COL_OP_Terrain_411','Block',{-2307.052,61.1,1912.595},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{32.5,13.0,62.2},false},
  {'COL_OP_Terrain_412','Block',{-2283.204,64.1,2002.54},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.25,1.0,68.2},false},
  {'COL_OP_Terrain_413','Block',{-2303.697,73.6,2031.589},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.5,45.9,87.2},false},
  {'COL_OP_Terrain_414','Block',{-2324.264,47.6,1680.193},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.2,14.5,35.2},false},
  {'COL_OP_TreeRoot_001','Block',{-2434.642,141.874,1977.424},{-0.716,0.0,-0.698},{-0.698,0.0,0.716},{9.345,9.175,11.347},false},
  {'COL_OP_TreeRoot_002','Block',{-2437.625,141.649,1986.712},{-1.0,0.0,-0.013},{-0.013,0.0,1.0},{7.663,8.417,10.898},false},
  {'COL_OP_TreeRoot_003','Block',{-2436.621,141.666,1991.684},{-0.931,0.0,0.364},{0.364,0.0,0.931},{7.281,7.701,10.932},false},
  {'COL_OP_TreeRoot_004','Block',{-2423.802,140.594,1999.595},{0.102,0.0,0.995},{0.995,0.0,-0.102},{7.83,6.897,8.788},false},
  {'COL_OP_TreeRoot_005','Block',{-2423.134,138.26,2005.031},{0.142,0.0,0.99},{0.99,0.0,-0.142},{6.768,4.772,4.119},false},
  {'COL_OP_TreeRoot_006','Block',{-2422.271,136.783,2010.442},{0.172,0.0,0.985},{0.985,0.0,-0.172},{5.759,2.745,1.166},false},
  {'COL_OP_TreeRoot_007','Block',{-2416.236,141.202,1996.829},{0.66,0.0,0.752},{0.752,0.0,-0.66},{8.617,8.003,10.005},false},
  {'COL_OP_TreeRoot_008','Block',{-2412.255,139.132,2000.978},{0.725,0.0,0.689},{0.689,0.0,-0.725},{7.686,6.187,5.864},false},
  {'COL_OP_TreeRoot_009','Block',{-2407.91,137.519,2004.736},{0.786,0.0,0.618},{0.618,0.0,-0.786},{6.836,4.455,2.638},false},
  {'COL_OP_TreeRoot_010','Block',{-2403.249,136.74,2008.155},{0.824,0.0,0.566},{0.566,0.0,-0.824},{6.033,2.778,1.08},false},
  {'COL_OP_TreeRoot_011','Block',{-2415.226,140.941,1978.744},{0.773,0.0,-0.634},{-0.634,0.0,-0.773},{7.96,7.229,9.481},false},
  {'COL_OP_TreeRoot_012','Block',{-2410.878,138.747,1975.511},{0.83,0.0,-0.557},{-0.557,0.0,-0.83},{7.006,5.344,5.095},false},
  {'COL_OP_TreeRoot_013','Block',{-2406.24,137.134,1972.691},{0.876,0.0,-0.483},{-0.483,0.0,-0.876},{6.132,3.547,1.867},false},
  {'COL_OP_TreeRoot_014','Block',{-2419.977,141.448,1974.812},{0.386,0.0,-0.922},{-0.922,0.0,-0.386},{8.386,7.701,10.496},false},
  {'COL_OP_TreeRoot_015','Block',{-2417.842,139.504,1969.561},{0.367,0.0,-0.93},{-0.93,0.0,-0.367},{7.613,6.16,6.609},false},
  {'COL_OP_TreeRoot_016','Block',{-2415.823,137.928,1964.266},{0.345,0.0,-0.938},{-0.938,0.0,-0.345},{6.879,4.69,3.455},false},
  {'COL_OP_TreeRoot_017','Block',{-2413.918,136.877,1958.928},{0.327,0.0,-0.945},{-0.945,0.0,-0.327},{6.168,3.265,1.353},false},
  {'COL_OP_TreeTrunk_001','Block',{-2424.99,150.2,1986.883},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.0,22.0,28.0},true},
  {'COL_OP_TreeTrunk_002','Block',{-2424.99,150.2,1986.883},{-0.985,0.0,0.174},{0.174,0.0,0.985},{22.0,22.0,28.0},true},
  {'COL_OP_TreeTrunk_003','Block',{-2426.587,170.2,1983.934},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{19.0,19.0,16.0},true},
  {'COL_OP_VegTrunk_001','Block',{-2113.003,95.7,1815.912},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.22,2.22,7.0},false},
  {'COL_OP_VegTrunk_002','Block',{-2229.603,103.7,1983.306},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.22,2.22,7.0},false},
  {'COL_OP_VegTrunk_003','Block',{-2381.469,95.7,1842.787},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_004','Block',{-2327.749,91.7,1728.027},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_005','Block',{-2178.163,103.7,2038.857},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_006','Block',{-2060.504,96.0,1916.152},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.958,1.958,7.0},false},
  {'COL_OP_VegTrunk_007','Block',{-2100.22,96.0,1975.955},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_008','Block',{-2046.48,92.0,1777.975},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.57,1.57,7.0},false},
  {'COL_OP_VegTrunk_009','Block',{-2184.053,103.7,1981.019},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.57,1.57,7.0},false},
  {'COL_OP_VegTrunk_010','Block',{-2182.59,103.7,2062.614},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.958,1.958,7.0},false},
  {'COL_OP_VegTrunk_011','Block',{-2446.182,96.0,1797.474},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_012','Block',{-2045.839,96.0,1910.551},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.958,1.958,7.0},false},
  {'COL_OP_VegTrunk_013','Block',{-2051.739,96.0,1921.069},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.958,1.958,7.0},false},
  {'COL_OP_VegTrunk_014','Block',{-2310.663,139.84,1961.339},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.242,2.242,7.0},false},
  {'COL_OP_VegTrunk_015','Block',{-2351.62,139.84,1932.661},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.242,2.242,7.0},false},
  {'COL_OP_VegTrunk_016','Block',{-2125.413,91.7,1694.404},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_017','Block',{-2156.597,91.7,1670.21},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.722,1.722,7.0},false},
  {'COL_OP_VegTrunk_018','Block',{-2171.905,91.7,1662.755},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.815,1.815,7.0},false},
  {'COL_OP_VegTrunk_019','Block',{-2056.95,92.0,1830.305},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.739,1.739,7.0},false},
  {'COL_OP_VegTrunk_020','Block',{-2311.152,91.7,1678.786},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_021','Block',{-2397.578,96.0,1791.596},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.736,1.736,7.0},false},
  {'COL_OP_VegTrunk_022','Block',{-2192.915,103.7,1969.959},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.699,1.699,7.0},false},
  {'COL_OP_VegTrunk_023','Block',{-2193.82,103.7,1982.521},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.822,1.822,7.0},false},
  {'COL_OP_VegTrunk_024','Block',{-2171.413,103.7,2021.267},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.647,1.647,7.0},false},
  {'COL_OP_VegTrunk_025','Block',{-2206.407,103.7,2021.25},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.767,1.767,7.0},false},
  {'COL_OP_VegTrunk_026','Block',{-2240.927,103.7,1999.657},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.78,1.78,7.0},false},
  {'COL_OP_VegTrunk_027','Block',{-2200.376,103.7,2055.574},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.757,1.757,7.0},false},
  {'COL_OP_VegTrunk_028','Block',{-2206.774,103.7,2061.086},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.676,1.676,7.0},false},
  {'COL_OP_VegTrunk_029','Block',{-2223.922,103.7,2063.231},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.83,1.83,7.0},false},
  {'COL_OP_VegTrunk_030','Block',{-2464.805,95.4,1748.034},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.077,2.077,7.0},false},
  {'COL_OP_VegTrunk_031','Block',{-2519.269,91.7,1715.61},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.524,2.524,7.0},false},
  {'COL_GateOnePunchManLock_001','GateLock',{-2530.696,97.2,1687.598},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{16.6,1.4,18.0},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'AUDIO_Castle',{-2341.179,142.2,1961.335},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='wind',['range']=60.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_CastleFall',{-2318.236,102.2,1928.569},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='water',['range']=60.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_FallE',{-2499.426,70.0,1754.088},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='water',['range']=60.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_FallW',{-2011.661,70.0,1794.094},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='water',['range']=55.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_Harbor',{-2372.263,46.2,1622.169},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='water',['range']=80.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_Plaza',{-2247.113,100.2,1826.994},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='wind',['range']=130.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_Street',{-2166.812,92.2,1712.313},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='wind',['range']=50.0,['volume']='baixo',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_Summon',{-2385.221,94.2,1727.848},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='energy',['range']=36.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'AUDIO_Wheel',{-2032.31,91.6,1823.583},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['family']='water',['range']=30.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'FX_Fall_Castle_Base',{-2321.792,97.6,1933.648},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_base',['width']=11.0,['level']=97.60000000000001,['note']='pe da cachoeira na bacia, na frente do degrau B, entre as pedras molhadas dos flancos',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=10.0,['tam']=7.5,['Dist']=260.0,['area']='11.0,2,5',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_Castle_Lip',{-2324.316,132.05,1937.252},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_borda',['kind']='cachoeira',['width']=6.4,['drop']=34.45,['water_level_up']=132.19,['waypoints']='-2324.29,132.19,1937.21;-2324.20,127.00,1937.09;-2324.14,112.00,1937.01;-2324.11,98.65,1936.96;-2323.20,98.62,1935.65;-2323.05,98.02,1935.45;-2321.99,98.00,1933.93;-2321.82,97.60,1933.69',['widths']='6.4,7.0,7.6,8.2,8.8,9.4,11.0,12.0',['spout_waypoints']='0.00,357.40,132.19;0.00,350.60,132.19',['spout_width']=5.0,['note']='frente do labio de pedra do op_terrain (topo medido 132,05; a lamina corre 0,14 acima, da boca escura da nascente em y 357,6 - \'spout_waypoints\' - ate a frente); cortina medida: labio -> degrau de espuma A (98,5) -> degrau B (97,9) -> bacia (97,6); folga da rocha >= 0,3',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=2.0,['tam']=3.0,['Dist']=260.0,['area']='6.4,1,1.2',['vfx']='emissor',['spout_waypoints_world']='-2328.22,132.19,1942.82;-2324.32,132.19,1937.25',['source_pos_x']=-2328.331,['source_pos_y']=131.2,['source_pos_z']=1942.986,['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_Castle_Step',{-2323.169,98.5,1935.614},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='espuma_degrau',['width']=8.8,['jump']=0.6,['note']='NOVO (op_water): borda da frente do degrau de espuma A; a cortina bate no topo, espalha e cai no degrau B (step2_pos) e na bacia',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=6.0,['tam']=5.0,['Dist']=240.0,['area']='8.8,1.2,2',['vfx']='emissor',['step2_pos_x']=-2321.964,['step2_pos_y']=97.9,['step2_pos_z']=1933.894,['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_E_Base',{-2495.985,36.0,1749.173},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='espuma_mar',['width']=8.2,['level']=36.0,['note']='pe da queda leste na enseada, entre as pedras de base',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=6.0,['tam']=9.0,['Dist']=420.0,['area']='8.2,2,6',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_E_Lip',{-2497.246,91.3,1750.976},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_borda',['kind']='bica',['width']=5.4,['drop']=55.3,['water_level_up']=91.60000000000001,['waypoints']='-2497.22,91.45,1750.93;-2497.07,88.80,1750.73;-2496.79,78.00,1750.32;-2496.44,62.00,1749.83;-2496.16,46.00,1749.42;-2495.99,36.00,1749.17',['widths']='5.4,5.8,6.4,7.0,7.6,8.2',['face_y_local']=298.0,['note']='ponta da soleira (91,3) em balanco 0,8 alem da face da garganta NE (298,0); cai na enseada do porto (rumo SUL medido na garganta; o M1 estimava SE)',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=1.5,['tam']=2.5,['Dist']=300.0,['area']='5.4,1,1.2',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_W_Base',{-2005.925,36.0,1785.902},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='espuma_mar',['width']=10.0,['level']=36.0,['note']='pe da queda oeste no mar local, entre as pedras de base',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=6.0,['tam']=10.0,['Dist']=420.0,['area']='10.0,2,6',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_W_Lip',{-2007.187,87.3,1787.704},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_borda',['kind']='bica',['width']=7.4,['drop']=51.3,['water_level_up']=87.60000000000001,['waypoints']='-2007.16,87.45,1787.66;-2007.02,84.80,1787.46;-2006.73,75.00,1787.05;-2006.38,60.00,1786.56;-2006.10,45.00,1786.15;-2005.92,36.00,1785.90',['widths']='7.4,7.8,8.4,9.0,9.6,10.4',['face_y_local']=47.0,['note']='ponta da soleira (87,3) em balanco 0,8 alem da face da garganta SO (47,0), entre 2 bochechas; cortina medida ate o mar (36)',['cor']='236,242,248',['vida']=2.6,['vel']=2.5,['transp']=0.6,['infl']=1.0,['luz']=0.05,['tex']='nevoa',['forma']='Box',['rate']=1.5,['tam']=2.8,['Dist']=300.0,['area']='7.4,1,1.2',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Mist_CastleFall',{-2322.595,98.8,1934.795},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fx']='nevoa_baixa',['radius']=11.0,['note']='nevoa do pe da cachoeira (degraus de espuma + bacia)',['tex']='nevoa',['cor']='232,238,246',['rate']=1.0,['vida']=10.0,['vel']=0.4,['tam']=9.0,['fim']=1.3,['transp']=0.9,['luz']=0.0,['infl']=1.0,['spread']='90,10',['acc_up']=0.05,['drift']=0.2,['area']='22,1.5,11',['forma']='Box',['Dist']=220.0,['vfx']='emissor',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'FX_Petals_Plaza',{-2267.188,105.7,1855.664},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='petalas',['rate']=16.0,['vida']=8.0,['Dist']=260.0,['area']='200.0,17.0,110.0',['note']='NOVO (op_vfx): deriva sobre a METADE NORTE da praca (5..22 acima do piso): as petalas vem do adro/arvore com o vento para a ponte; particula sem colisao, nao atrapalha a mineracao',['tex']='petala',['cor']='255,172,198',['cor_fim']='248,140,170',['vel']=1.0,['tam']=0.36,['fim']=0.7,['transp']=0.22,['luz']=0.0,['infl']=1.0,['spread']='180,180',['acc_up']=-1.1,['drift']=0.5,['rotv']=60.0,['forma']='Box',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Petals_Street',{-2159.355,100.7,1701.664},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='petalas',['rate']=5.0,['vida']=8.0,['Dist']=160.0,['area']='28.0,15.0,98.0',['note']='NOVO (op_vfx): rua de chegada + patio do torii (cerejeiras dos ombros de rocha e do recanto)',['tex']='petala',['cor']='255,172,198',['cor_fim']='248,140,170',['vel']=1.0,['tam']=0.36,['fim']=0.7,['transp']=0.22,['luz']=0.0,['infl']=1.0,['spread']='180,180',['acc_up']=-1.1,['drift']=0.5,['rotv']=60.0,['forma']='Box',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Petals_Tree',{-2312.443,163.921,2027.34},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='petalas',['Dist']=320.0,['radius']=40.0,['note']='REPOSTO pelo op_vfx (era 1 esfera no meio da copa a 284): caixa sob o lobo OESTE medido da copa, 3 abaixo das flores ate 150 (patio + 14); cai sobre a subida do castelo e o lado oeste do patio; fora da torre',['rate']=10.0,['vida']=11.0,['area']='46.0,27.4,30.2',['tex']='petala',['cor']='255,172,198',['cor_fim']='248,140,170',['vel']=1.0,['tam']=0.36,['fim']=0.7,['transp']=0.22,['luz']=0.0,['infl']=1.0,['spread']='180,180',['acc_up']=-1.1,['drift']=0.5,['rotv']=60.0,['forma']='Box',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Petals_TreeRoots',{-2437.979,171.761,1963.676},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='petalas',['rate']=8.0,['vida']=11.0,['Dist']=260.0,['area']='77.9,50.0,50.1',['note']='NOVO (op_vfx): caixa sob o lobo LESTE medido (sobre as raizes e a base da arvore)',['tex']='petala',['cor']='255,172,198',['cor_fim']='248,140,170',['vel']=1.0,['tam']=0.36,['fim']=0.7,['transp']=0.22,['luz']=0.0,['infl']=1.0,['spread']='180,180',['acc_up']=-1.1,['drift']=0.5,['rotv']=60.0,['forma']='Box',['vfx']='emissor',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Spring_W',{-2151.786,97.2,1994.213},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='bica',['kind']='bica',['width']=1.0,['drop']=5.6,['waypoints']='-2151.77,97.25,1994.20;-2151.61,95.60,1993.97;-2151.53,92.60,1993.84;-2151.50,91.60,1993.80',['widths']='1.0,1.1,1.3,1.5',['note']='ponta da bica de pedra (calha com abas) que sai do nicho escuro no arrimo do terraco alto; cai na cabeceira do canal oeste',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Weir_E',{-2394.909,97.6,1877.324},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{['fx']='degrau_agua',['drop']=6.0,['steps']=3,['width']=5.7,['tops']='97.30,95.30,93.30',['note']='borda da soleira (97,3) do degrau de 3 x 2 do canal leste; correnteza +X local',['fwd_x']=-0.8192,['fwd_z']=-0.5736}},
  {'FX_Weir_W',{-2049.173,91.6,1847.666},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='degrau_agua',['drop']=4.0,['steps']=2,['width']=7.7,['tops']='91.30,89.30',['note']='borda da soleira (91,3) do degrau de 2 x 2 do canal oeste; correnteza -Y local',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'GATE_OnePunchMan',{-2530.696,88.2,1687.598},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['open_w']=16.0,['open_h']=18.0,['deck_w']=18.0,['area_id']=6,['key']='OnePunchMan',['fwd_x']=-0.9397,['fwd_z']=-0.342}},
  {'GATE_OnePunchMan_EXIT',{-2541.972,88.4,1683.494},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['gate']='OnePunchMan',['fwd_x']=-0.9397,['fwd_z']=-0.342}},
  {'GATE_OnePunchMan_INTERACT',{-2524.118,88.4,1689.992},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['gate']='OnePunchMan',['radius']=10.0,['fwd_x']=-0.9397,['fwd_z']=-0.342}},
  {'GATE_OnePunchMan_LOCKED',{-2530.696,97.2,1687.598},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['gate']='OnePunchMan',['state_default']='locked',['fwd_x']=-0.9397,['fwd_z']=-0.342}},
  {'GATE_OnePunchMan_OpenFX',{-2530.696,97.2,1687.598},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['gate']='OnePunchMan',['state']='unlocked',['fx']='abertura',['fwd_x']=-0.9397,['fwd_z']=-0.342}},
  {'GP_Block_01',{-2146.264,92.2,1820.7},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_02',{-2218.535,92.2,1923.913},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_03',{-2275.69,92.2,1730.075},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_04',{-2157.05,92.2,1813.148},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_05',{-2229.321,92.2,1916.361},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_06',{-2152.287,92.2,1829.301},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_07',{-2281.713,92.2,1738.676},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_08',{-2167.835,92.2,1805.596},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_09',{-2240.106,92.2,1908.809},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_10',{-2158.31,92.2,1837.902},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_11',{-2287.736,92.2,1747.277},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_12',{-2178.621,92.2,1798.044},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_13',{-2250.892,92.2,1901.257},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_14',{-2164.332,92.2,1846.503},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_15',{-2293.758,92.2,1755.878},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_16',{-2189.406,92.2,1790.492},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_17',{-2261.677,92.2,1893.705},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_18',{-2170.354,92.2,1855.104},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_19',{-2299.781,92.2,1764.479},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_20',{-2200.192,92.2,1782.94},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_21',{-2272.462,92.2,1886.153},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_22',{-2176.377,92.2,1863.706},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_23',{-2305.803,92.2,1773.08},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_24',{-2210.977,92.2,1775.388},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_25',{-2283.248,92.2,1878.601},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_26',{-2182.4,92.2,1872.307},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_27',{-2311.826,92.2,1781.682},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_28',{-2221.763,92.2,1767.835},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_29',{-2294.033,92.2,1871.049},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_30',{-2188.422,92.2,1880.908},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_31',{-2317.848,92.2,1790.283},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_32',{-2232.548,92.2,1760.283},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_33',{-2304.819,92.2,1863.497},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_34',{-2194.445,92.2,1889.509},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_35',{-2323.871,92.2,1798.884},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_36',{-2243.334,92.2,1752.731},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_37',{-2315.604,92.2,1855.944},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_38',{-2200.467,92.2,1898.11},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_39',{-2329.893,92.2,1807.485},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_40',{-2254.119,92.2,1745.179},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_41',{-2326.39,92.2,1848.392},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_42',{-2206.49,92.2,1906.711},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_43',{-2335.916,92.2,1816.086},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_44',{-2264.905,92.2,1737.627},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_45',{-2337.176,92.2,1840.84},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_46',{-2212.512,92.2,1915.312},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_47',{-2341.938,92.2,1824.687},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_48',{-2347.961,92.2,1833.288},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_49',{-2157.406,92.2,1822.665},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_50',{-2163.142,92.2,1830.856},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_51',{-2168.878,92.2,1839.048},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_52',{-2209.028,92.2,1896.388},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_53',{-2214.764,92.2,1904.58},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_54',{-2220.5,92.2,1912.771},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_55',{-2165.598,92.2,1816.929},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_56',{-2171.333,92.2,1825.12},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_57',{-2222.955,92.2,1898.844},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_58',{-2228.691,92.2,1907.036},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_59',{-2173.789,92.2,1811.193},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_60',{-2236.883,92.2,1901.3},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_61',{-2181.981,92.2,1805.457},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_62',{-2245.074,92.2,1895.564},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_63',{-2247.513,92.2,1759.571},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_64',{-2310.606,92.2,1849.678},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_65',{-2255.704,92.2,1753.836},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_66',{-2318.798,92.2,1843.942},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_67',{-2263.896,92.2,1748.1},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_68',{-2269.632,92.2,1756.291},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_69',{-2321.254,92.2,1830.015},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_70',{-2326.989,92.2,1838.207},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_71',{-2272.087,92.2,1742.364},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_72',{-2277.823,92.2,1750.556},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_73',{-2283.559,92.2,1758.747},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_74',{-2323.709,92.2,1816.088},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_75',{-2329.445,92.2,1824.279},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_76',{-2335.181,92.2,1832.471},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ISLAND_EXIT_OnePiece',{-2427.33,88.2,1725.22},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['width']=18.0,['deck_z']=88.2,['heading_deg']=-160.0,['note']='cabeca da ponte vermelha de saida (88, T1) na borda leste do terraco do summon',['fwd_x']=-0.9397,['fwd_z']=-0.342,['heading_deg_local']=15.0}},
  {'ISLAND_NEXT_ANCHOR_OnePunchMan',{-2553.248,88.2,1679.39},{0.342,0.0,-0.94},{-0.94,0.0,-0.342},{['width']=18.0,['deck_z']=88.2,['clear_h']=22.0,['heading_deg']=-160.0,['next_area']=6,['next_key']='OnePunchMan',['fwd_roblox']='-0.9397,0.0000,-0.3420',['pos_roblox']='-2553.25,88.20,1679.39',['orientation_roblox']='0,70.0,0',['guard']='PROVISORIO: COL_OPAnchorGuard_* + OP_Exit_AnchorGuard (next_island_guard=True)',['guard_note']='One Punch Man (area 6) ainda nao existe: termino SEGURO. A integracao da area 6 REMOVE a guarda quando a ponte seguinte encosta aqui (nao ha passagem que leva a queda)',['fwd_x']=-0.9397,['fwd_z']=-0.342,['heading_deg_local']=15.0}},
  {'MiningZone_OnePiece',{-2247.113,92.2,1826.994},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['kind']='mining',['floor']=92.2,['sx']=152.0,['sy']=120.0,['open_sky']=true,['note']='PRACA central a CEU ABERTO (sem \'ceil\': o script usa piso + 28); o jogo usa ORE_* + grade hexagonal + bloqueios GP_Block_*; frente = +Y local (castelo); emblema de chao RENTE no centro (sem colisao)',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_01',{-2209.629,92.2,1860.931},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_02',{-2304.549,92.2,1795.383},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_03',{-2220.463,92.2,1838.379},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_04',{-2198.533,92.2,1868.481},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_05',{-2267.783,92.2,1805.013},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_06',{-2231.194,92.2,1816.691},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_07',{-2209.22,92.2,1847.166},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_08',{-2243.484,92.2,1807.952},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_09',{-2279.984,92.2,1797.507},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_10',{-2197.488,92.2,1855.394},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_11',{-2219.793,92.2,1823.771},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_12',{-2291.643,92.2,1789.295},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_13',{-2253.972,92.2,1799.619},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_14',{-2186.368,92.2,1863.766},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_15',{-2208.5,92.2,1832.765},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_16',{-2230.078,92.2,1802.579},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_17',{-2266.845,92.2,1792.009},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_18',{-2278.761,92.2,1783.434},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_19',{-2196.117,92.2,1840.361},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_20',{-2217.65,92.2,1810.354},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_21',{-2242.177,92.2,1793.009},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_22',{-2184.923,92.2,1849.079},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_23',{-2254.571,92.2,1785.551},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_24',{-2205.952,92.2,1818.509},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_25',{-2289.403,92.2,1775.078},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_26',{-2217.762,92.2,1796.444},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_27',{-2265.498,92.2,1777.62},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_28',{-2194.42,92.2,1826.448},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_29',{-2229.413,92.2,1787.053},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_30',{-2205.406,92.2,1804.949},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_31',{-2277.027,92.2,1769.974},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_32',{-2183.955,92.2,1834.533},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_33',{-2241.087,92.2,1779.928},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_34',{-2193.998,92.2,1812.717},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_35',{-2216.048,92.2,1782.141},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_36',{-2252.665,92.2,1771.236},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_37',{-2263.863,92.2,1764.005},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_COMMON_38',{-2227.253,92.2,1774.014},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_01',{-2284.523,92.2,1854.305},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_02',{-2249.172,92.2,1878.717},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_03',{-2296.125,92.2,1845.803},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_04',{-2260.192,92.2,1856.046},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_05',{-2237.753,92.2,1887.201},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_06',{-2308.689,92.2,1837.909},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_07',{-2271.774,92.2,1847.57},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_08',{-2249.197,92.2,1865.136},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_09',{-2283.249,92.2,1840.194},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_EPIC_10',{-2236.422,92.2,1873.044},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_SUPERLEGENDARY_01',{-2272.294,92.2,1862.661},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_SUPERLEGENDARY_02',{-2261.635,92.2,1870.905},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_01',{-2294.594,92.2,1831.97},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_02',{-2258.197,92.2,1841.988},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_03',{-2224.931,92.2,1882.104},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_04',{-2307.09,92.2,1824.624},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_05',{-2246.533,92.2,1850.522},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_06',{-2270.153,92.2,1833.555},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_07',{-2235.563,92.2,1858.654},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_08',{-2282.25,92.2,1826.562},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_09',{-2257.09,92.2,1829.127},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_10',{-2245.662,92.2,1837.092},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_11',{-2293.772,92.2,1818.384},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_12',{-2223.868,92.2,1866.551},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_13',{-2212.541,92.2,1875.532},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_14',{-2269.878,92.2,1820.087},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_15',{-2233.631,92.2,1844.369},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_16',{-2305.15,92.2,1809.685},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_17',{-2222.315,92.2,1853.001},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_18',{-2244.021,92.2,1822.091},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_19',{-2280.211,92.2,1811.778},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_20',{-2232.661,92.2,1831.217},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_21',{-2256.271,92.2,1814.514},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'ORE_UNCOMMON_22',{-2291.786,92.2,1803.954},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER',{-2247.113,92.2,1826.994},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['waypoints']='-2136.99,84.20,1669.72;-2142.15,84.20,1677.09;-2149.61,88.20,1687.74;-2180.58,88.20,1731.97;-2185.17,88.20,1738.53;-2193.20,92.20,1749.99;-2214.99,92.20,1781.12;-2247.11,92.20,1826.99;-2295.29,92.20,1895.80;-2301.60,92.20,1904.81;-2312.50,98.20,1920.38',['note']='patio do torii -> rua de chegada -> escadaria -> centro da praca -> adro do castelo',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_00',{-2136.986,84.2,1669.717},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_01',{-2142.148,84.2,1677.089},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_02',{-2149.605,88.2,1687.738},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_03',{-2180.578,88.2,1731.972},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_04',{-2185.167,88.2,1738.526},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_05',{-2193.197,92.2,1749.994},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_06',{-2214.992,92.2,1781.122},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_07',{-2247.113,92.2,1826.994},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_08',{-2295.293,92.2,1895.803},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_09',{-2301.603,92.2,1904.814},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PATH_ENTRY_CENTER_10',{-2312.5,98.2,1920.377},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'PURCHASE_UI_ANCHOR_OnePunchMan',{-2528.346,102.2,1688.453},{-0.342,0.0,0.94},{0.94,0.0,0.342},{['gate']='OnePunchMan',['faces']='approach',['ui']='BillboardGui preco/requisito',['fwd_x']=0.9397,['fwd_z']=0.342}},
  {'SAFE_Adro',{-2341.825,98.2,1892.52},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Bairro_Canal',{-2062.616,88.2,1790.154},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Cais',{-2319.01,42.2,1598.418},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Castelo',{-2351.019,136.2,2027.692},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Entrada',{-2136.986,84.2,1669.717},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_NE',{-2403.253,92.2,1788.469},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Oeste_Alem',{-2099.504,92.2,1947.442},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Ponte_Chegada',{-2088.806,82.2,1600.908},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Porto_Alto',{-2322.128,65.2,1637.741},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Praca_L',{-2325.751,92.2,1771.931},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Praca_N',{-2292.999,92.2,1892.526},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Praca_O',{-2168.474,92.2,1882.057},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Praca_S',{-2201.227,92.2,1761.462},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Promontorio',{-2517.54,88.2,1692.386},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Rua_Chegada',{-2163.371,88.2,1707.398},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Summon',{-2386.046,88.2,1763.894},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SAFE_Terraco_Alto',{-2225.674,100.2,2005.59},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SUMMON_Interact',{-2379.487,88.2,1731.863},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='gabinete invisivel do Gacha_mare (prompt Invocar)',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'SUMMON_Main',{-2385.221,88.2,1727.848},{-0.574,0.0,0.819},{0.819,0.0,0.574},{['note']='torre de invocacao AMS (estrela + aneis + torre + nucleo, familia da Ilha 1), frente para -X local (oeste: praca); terraco lateral na transicao para o porto',['fwd_x']=0.8192,['fwd_z']=0.5736}},
  {'SUMMON_PlayerPosition',{-2372.115,88.2,1737.025},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{['note']='onde o jogador fica olhando a torre (pad do gacha)',['fwd_x']=-0.8192,['fwd_z']=-0.5736}},
  {'WATER_Basin',{-2324.875,97.6,1927.119},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['shape']='poligono',['level']=97.60000000000001,['floor']=95.4,['depth']=2.2,['rim_min']=97.9,['sx']=39.44,['sy']=16.0,['waypoints']='-2300.81,97.60,1934.85;-2330.10,97.60,1914.34;-2333.21,97.60,1917.04;-2333.80,97.60,1916.63;-2337.07,97.60,1921.30;-2335.94,97.60,1922.09;-2335.13,97.60,1930.35;-2314.13,97.60,1945.06;-2303.68,97.60,1942.37',['note']='contorno DESENHADO da agua: buraco do terreno 0,15 para dentro (junta da cantaria) + fundo puxado ate o pe da rocha (351,15); a boca do canal leste (mouth_a/b) fica na borda leste; o leito e o do terreno (95,4) com o apron (96,9) e os degraus de espuma no fundo',['mouth_a_pos_x']=-2333.804,['mouth_a_pos_y']=97.6,['mouth_a_pos_z']=1916.631,['mouth_b_pos_x']=-2337.073,['mouth_b_pos_y']=97.6,['mouth_b_pos_z']=1921.3,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'WATER_CanalE',{-2335.439,97.6,1918.965},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{['level']=97.60000000000001,['level_low']=91.60000000000001,['floor']=95.4,['floor_low']=89.4,['rim']=98.50000000000001,['rim_low']=92.50000000000001,['waypoints']='-2335.44,97.60,1918.96;-2394.91,97.60,1877.32;-2395.07,95.45,1877.21;-2396.14,95.45,1876.46;-2396.30,93.45,1876.35;-2397.37,93.45,1875.60;-2397.53,91.60,1875.49;-2473.96,91.60,1823.19;-2523.11,91.60,1788.78;-2501.15,91.60,1756.55;-2497.70,91.60,1751.63;-2497.25,91.45,1750.98',['widths']='5.7,5.7,5.7,5.7,5.7,5.7,5.7,5.7,5.7,5.7,5.7,5.4',['note']='canal de cantaria: boca da bacia -> degrau 3 x 2 (FX_Weir_E) -> pe do rochedo NE -> curva -> bica da queda leste; pares de pontos com cota diferente = quedas curtas; ultimo ponto = ponta da bica',['fwd_x']=-0.8192,['fwd_z']=-0.5736}},
  {'WATER_CanalW',{-2152.502,91.6,1995.237},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['level']=91.60000000000001,['level_low']=87.60000000000001,['floor']=89.4,['floor_low']=85.4,['rim']=92.50000000000001,['rim_low']=88.50000000000001,['waypoints']='-2152.50,91.60,1995.24;-2124.08,91.60,1954.65;-2085.08,91.60,1898.94;-2049.17,91.60,1847.67;-2049.06,89.45,1847.50;-2048.37,89.45,1846.52;-2048.26,87.60,1846.36;-2033.46,87.60,1825.22;-2013.95,87.60,1797.37;-2007.65,87.60,1788.36;-2007.19,87.45,1787.70',['widths']='7.7,7.7,7.7,7.7,7.7,7.7,7.7,7.7,7.7,7.7,7.4',['note']='cabeceira no arrimo do terraco alto (bica FX_Spring_W) -> sob as pontes do plano (y 182, 252) -> degrau 2 x 2 (FX_Weir_W) -> roda d\'agua (wheel_pos: espuma onde as pas batem) -> bica da queda oeste',['wheel_pos_x']=-2032.31,['wheel_pos_y']=87.6,['wheel_pos_z']=1823.583,['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'WATER_Sea',{-2321.499,36.0,1828.622},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['shape']='quadrado',['level']=36.0,['size']=2200.0,['client_only']=true,['area']=5,['color']='48,176,196',['falls']='FX_Fall_W_Base;FX_Fall_E_Base',['note']='mar LOCAL turquesa de Wano: so no cliente e so com o jogador na area 5 (como o mar de nuvens da DS); esconde a quilha; vista de Wano, a DS aparece como ilha saindo do mar (topo da quilha DS 53,6 > 46). Conferido no op_water: as 2 quedas da borda terminam em 36 (pedras de base)',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'WORLD_ENTRY_OnePiece',{-2136.986,84.4,1669.717},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['note']='chegada da ilha (patio do grande torii, olhando a rua de chegada e o castelo)',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'WORLD_FROM_PREV',{-2054.391,80.2,1551.759},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['width']=18.0,['deck_z']=80.2,['prev']='ISLAND_NEXT_ANCHOR_OnePiece (Ilha 4 Demon Slayer, 9cc4bef4)',['bridge_len']=120.0,['note']='centro da borda do tabuleiro da ponte de chegada (reta de 120, sobe 4 ate o patio do torii); avanco = frente; tem de cair EXATO na ancora da Ilha 4',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
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
  {'L_OPCap_Int_Cha','POINT',{-2152.178,99.7,1933.753},{255,209,162},14.0,0.6,false,false},
  {'L_OPCap_Win_Cha','POINT',{-2146.918,98.1,1924.497},{255,209,162},6.5,0.36,false,true},
  {'L_OPCap_Win_M2C1','POINT',{-2127.144,95.8,1702.733},{255,209,162},6.5,0.36,false,true},
  {'L_OPCap_Win_M2C2','POINT',{-2149.637,93.85,1714.634},{255,209,162},6.5,0.36,false,true},
  {'L_OPCap_Win_M2C5','POINT',{-2176.0,95.8,1688.3},{255,209,162},6.5,0.36,false,true},
  {'L_OPCap_Win_M2C6','POINT',{-2200.667,95.9,1681.161},{255,209,162},6.5,0.36,false,true},
  {'L_OPCap_Win_M4C7','POINT',{-2190.488,103.4,1716.488},{255,209,162},6.5,0.36,false,true},
  {'L_OPCas_Hall_1','POINT',{-2349.783,143.6,1973.622},{255,215,173},18.0,0.69,false,false},
  {'L_OPCas_Hall_2','POINT',{-2368.216,143.6,1979.027},{255,215,173},18.0,0.69,false,false},
  {'L_OPCas_Hall_3','POINT',{-2348.557,143.6,1992.793},{255,215,173},18.0,0.69,false,false},
  {'L_OPProp_Lamp_Alem','POINT',{-2090.827,99.14,1936.793},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_BridgeHead_L','POINT',{-2114.832,89.004,1655.198},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_BridgeHead_R','POINT',{-2130.92,89.004,1643.933},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Bridge_L','POINT',{-2074.8,86.678,1598.026},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Bridge_R','POINT',{-2090.888,86.678,1586.761},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Cais','POINT',{-2107.542,99.14,1901.039},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cap_Bairro','POINT',{-2052.473,94.32,1780.898},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cap_Oeste','POINT',{-2110.386,98.52,1848.264},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cap_Porto','POINT',{-2262.211,94.32,1648.932},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cap_Terraco','POINT',{-2223.545,106.32,2015.625},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cas_Adro_0','POINT',{-2285.876,104.8,1926.812},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cas_Adro_1','POINT',{-2327.653,104.8,1897.56},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cas_Patamar','POINT',{-2282.693,121.412,2012.054},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Cas_Toro_0','POINT',{-2328.481,141.114,1964.122},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Lamp_Cas_Toro_1','POINT',{-2348.141,141.114,1950.356},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Lamp_M2Esc_0','POINT',{-2173.465,91.44,1747.269},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Esc_1','POINT',{-2197.384,91.44,1730.52},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_0','POINT',{-2147.64,94.95,1698.88},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_1','POINT',{-2167.629,94.95,1699.533},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_2','POINT',{-2160.832,94.95,1717.721},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_3','POINT',{-2181.395,94.95,1719.192},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Mercado','POINT',{-2099.774,94.5,1769.996},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_0','POINT',{-2321.323,98.94,1738.408},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_1','POINT',{-2355.737,98.94,1787.558},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_2','POINT',{-2134.965,98.94,1862.794},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_3','POINT',{-2170.527,98.94,1913.581},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_4','POINT',{-2366.554,98.94,1809.282},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_5','POINT',{-2184.373,98.94,1922.198},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_6','POINT',{-2262.398,98.94,1932.509},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Plz_7','POINT',{-2341.036,98.94,1877.446},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_PortoEscB_0','POINT',{-2274.947,45.29,1599.301},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_PortoEscB_1','POINT',{-2285.76,45.29,1591.73},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Porto_0','POINT',{-2372.344,48.4,1613.567},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Porto_1','POINT',{-2349.401,48.84,1580.801},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_PracaN_0','POINT',{-2281.328,98.94,1912.906},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_PracaN_1','POINT',{-2316.142,98.94,1888.529},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_Saida_0','POINT',{-2421.01,93.024,1717.07},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Saida_1','POINT',{-2504.409,93.024,1686.716},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Saida_2','POINT',{-2432.673,93.024,1733.726},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Saida_3','POINT',{-2511.126,93.024,1705.171},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Saida_Toro_0','POINT',{-2541.882,93.014,1668.628},{255,209,162},4.9,0.32,false,true},
  {'L_OPProp_Lamp_Saida_Toro_1','POINT',{-2551.459,93.014,1694.94},{255,209,162},4.9,0.32,false,true},
  {'L_OPProp_Lamp_Sum_0','POINT',{-2347.882,93.348,1736.414},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Sum_1','POINT',{-2369.136,93.348,1757.179},{255,209,162},6.2,0.35,false,true},
  {'L_OPProp_Lamp_Travessa','POINT',{-2226.627,95.14,1674.825},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Toro_Cap_NE','POINT',{-2414.17,96.562,1826.725},{255,209,162},4.9,0.32,false,true},
  {'L_OPProp_Toro_In_L','POINT',{-2112.506,89.682,1661.954},{255,209,162},5.4,0.33,false,true},
  {'L_OPProp_Toro_In_R','POINT',{-2138.064,89.682,1644.058},{255,209,162},5.4,0.33,false,true},
  {'L_OPProp_Toro_M2_0','POINT',{-2177.567,96.98,1761.67},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Toro_M2_1','POINT',{-2209.514,96.98,1739.301},{255,209,162},5.1,0.32,false,true},
  {'L_OPSum_Core','POINT',{-2383.911,97.2,1728.766},{162,191,255},12.6,0.71,false,false},
  {'L_OPSum_Lamp_L','POINT',{-2376.307,95.338,1722.614},{255,209,162},7.2,0.38,false,false},
  {'L_OPSum_Lamp_R','POINT',{-2387.091,95.338,1738.014},{255,209,162},7.2,0.38,false,false},
  {'L_OPSum_Star','POINT',{-2387.679,134.2,1726.127},{255,221,162},10.7,0.56,false,false},
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
  {'SAFE_Adro',{-2341.825,98.2,1892.52}},
  {'SAFE_Bairro_Canal',{-2062.616,88.2,1790.154}},
  {'SAFE_Cais',{-2319.01,42.2,1598.418}},
  {'SAFE_Castelo',{-2351.019,136.2,2027.692}},
  {'SAFE_Entrada',{-2136.986,84.2,1669.717}},
  {'SAFE_NE',{-2403.253,92.2,1788.469}},
  {'SAFE_Oeste_Alem',{-2099.504,92.2,1947.442}},
  {'SAFE_Ponte_Chegada',{-2088.806,82.2,1600.908}},
  {'SAFE_Porto_Alto',{-2322.128,65.2,1637.741}},
  {'SAFE_Praca_L',{-2325.751,92.2,1771.931}},
  {'SAFE_Praca_N',{-2292.999,92.2,1892.526}},
  {'SAFE_Praca_O',{-2168.474,92.2,1882.057}},
  {'SAFE_Praca_S',{-2201.227,92.2,1761.462}},
  {'SAFE_Promontorio',{-2517.54,88.2,1692.386}},
  {'SAFE_Rua_Chegada',{-2163.371,88.2,1707.398}},
  {'SAFE_Summon',{-2386.046,88.2,1763.894}},
  {'SAFE_Terraco_Alto',{-2225.674,100.2,2005.59}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(980,4,980); v.Position = Vector3.new(-2315.763427734375,-30.0,1820.4306640625) + ROOT_OFFSET
  v:ClearAllChildren()
  for _, s in ipairs(SAFE) do local at = Instance.new('Attachment'); at.Name = s[1]; at.Parent = v
    at.WorldPosition = Vector3.new(s[2][1], s[2][2], s[2][3]) + ROOT_OFFSET end
  v.Parent = root end

-- Script de servidor: personagens no grupo 'Personagens' (atravessam as cascas SoVisual) + rede de quedas
do
  local SSS = game:GetService('ServerScriptService')
  local s = SSS:FindFirstChild('ILHA_ONEPIECE_Servidor') or Instance.new('Script')
  s.Name = 'ILHA_ONEPIECE_Servidor'
  s.Source = [==[
-- gerado por montar_ilha_onepiece.lua (export_roblox.py) - nao editar a mao
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
local root = workspace:WaitForChild('ILHA_ONEPIECE', 60)
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
  Lg.GeographicLatitude = 9.97
  Lg.ClockTime = 9.064
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
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (0.68, 0.70, -0.23) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
root.WorldPivot = CFrame.new(ROOT_OFFSET)
-- ===== pecas moveis (VFX_*) =====
local VFX = {
  ['VFX_GATE_OnePunchMan_Star_1'] = {p = Vector3.new(-2531.101,103.800,1701.285), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -4.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePunchMan_Star_2'] = {p = Vector3.new(-2526.949,99.000,1702.158), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePunchMan_Star_3'] = {p = Vector3.new(-2518.467,99.300,1678.853), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -6.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePunchMan_Star_4'] = {p = Vector3.new(-2522.209,104.100,1676.853), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 7.000, bob = 0.600, rate = 0.000},
  ['VFX_OP_Wheel'] = {p = Vector3.new(-2032.310,92.400,1823.583), a = Vector3.new(0.8190,0.0000,0.5740), rpm = 4.000, bob = 0.000, rate = 0.000},
  ['VFX_OPSUM_Ring_1'] = {p = Vector3.new(-2387.679,134.200,1726.127), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 2.000, bob = 0.000, rate = 0.000},
  ['VFX_OPSUM_Ring_2'] = {p = Vector3.new(-2387.679,134.200,1726.127), a = Vector3.new(0.0000,-1.0000,0.0000), rpm = 4.000, bob = 0.000, rate = 0.000},
  ['VFX_OPSUM_Ring_3'] = {p = Vector3.new(-2387.679,134.200,1726.127), a = Vector3.new(-0.0740,0.5300,0.8450), rpm = 6.000, bob = 0.000, rate = 0.000},
  ['VFX_OPSUM_Star'] = {p = Vector3.new(-2387.679,134.200,1726.127), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.000, rate = 0.000},
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
  if (d:IsA('BasePart') or d:IsA('Model')) and (string.match(d.Name, '^OP_Exit_AnchorGuard') or string.match(d.Name, '^COL_OPAnchorGuard_')) then
    d:SetAttribute('next_island_guard', true)
    d:SetAttribute('removed_by', 'integracao da ilha One Punch Man (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_OnePunchMan)')
    CS:AddTag(d, 'GuardaProximaIlha'); nG += 1 end
end
print(string.format('%d pecas da guarda da ancora marcadas (GuardaProximaIlha)', nG))
print(string.format('ILHA_ONEPIECE montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
