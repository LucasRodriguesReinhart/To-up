-- montar_vm_trecho.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID ad92449f
-- 1) Importe os FBX VM_TRECHO_*_ad9244.fbx (3D Importer) para dentro de workspace.VM_TRECHO_V1. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script VM_TRECHO_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = 'ad92449f'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o trecho V1 da Vila Medieval (praca -> ponte) INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('VM_TRECHO_V1') or Instance.new('Model', workspace)
root.Name = 'VM_TRECHO_V1'
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
  ['Cloth_VM_Cream'] = {c = Color3.fromRGB(232,220,196), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VM_Red'] = {c = Color3.fromRGB(176,54,44), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Flower_VM_Pink'] = {c = Color3.fromRGB(232,128,168), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_VM_Red'] = {c = Color3.fromRGB(214,62,58), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_VM_Yellow'] = {c = Color3.fromRGB(240,196,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_VM'] = {c = Color3.fromRGB(98,168,62), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Tuft'] = {c = Color3.fromRGB(92,168,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_VM_Bronze'] = {c = Color3.fromRGB(176,138,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VM_Iron'] = {c = Color3.fromRGB(70,70,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_VM_Cream'] = {c = Color3.fromRGB(235,225,200), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_VM_Ochre'] = {c = Color3.fromRGB(226,208,176), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_VM_Peach'] = {c = Color3.fromRGB(232,210,186), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta'] = {c = Color3.fromRGB(200,110,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta_B'] = {c = Color3.fromRGB(182,96,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta_C'] = {c = Color3.fromRGB(214,126,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_Paving_VM'] = {c = Color3.fromRGB(178,166,146), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_Cob'] = {c = Color3.fromRGB(190,172,144), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_CobB'] = {c = Color3.fromRGB(166,150,126), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_Edge'] = {c = Color3.fromRGB(140,132,120), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_Joint'] = {c = Color3.fromRGB(108,100,90), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_VM_Base'] = {c = Color3.fromRGB(124,130,142), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Dark'] = {c = Color3.fromRGB(96,100,112), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Grey'] = {c = Color3.fromRGB(120,123,130), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Mortar'] = {c = Color3.fromRGB(70,72,84), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Trim'] = {c = Color3.fromRGB(160,158,150), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Warm'] = {c = Color3.fromRGB(132,126,120), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Water_VM'] = {c = Color3.fromRGB(64,150,190), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Window_VM_Lamp'] = {c = Color3.fromRGB(238,204,146), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_VM_Plank'] = {c = Color3.fromRGB(128,88,58), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_VM_Timber'] = {c = Color3.fromRGB(74,50,36), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
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
local FBX = {[1]='VM_TRECHO_02_TERRAIN_ad9244.fbx', [2]='VM_TRECHO_03_TOWN_ad9244.fbx', [3]='VM_TRECHO_04_FORGE.fbx', [4]='VM_TRECHO_05_SERVICES.fbx', [5]='VM_TRECHO_06_PORTALS.fbx', [6]='VM_TRECHO_07_EXIT.fbx', [7]='VM_TRECHO_08_WATER_ad9244.fbx', [8]='VM_TRECHO_09_VEGETATION.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['VM_Ter_TCanal__Stone_VM_Grey']={0.011,4.963,-12.0,59.992,5.786,14.118,1,true,'Stone_VM_Grey','',''},
  ['VM_Ter_TCanal__Stone_VM_Mortar']={0.0,4.265,-12.0,60.0,7.33,14.0,1,true,'Stone_VM_Mortar','',''},
  ['VM_Ter_TCanal__Stone_VM_Trim']={0.0,7.52,-12.0,60.12,1.4,14.28,1,true,'Stone_VM_Trim','',''},
  ['VM_Ter_TCanal__Stone_VM_Warm']={0.569,4.482,-12.0,58.723,4.82,13.24,1,true,'Stone_VM_Warm','',''},
  ['VM_Ter_TGround__Grass_VM']={0.0,5.8,0.0,88.0,2.0,80.0,1,false,'Grass_VM','',''},
  ['VM_Ter_TGround__Stone_Paving_VM']={0.0,6.33,0.0,56.0,1.339,80.0,1,false,'Stone_Paving_VM','',''},
  ['VM_Ter_TGround__Stone_VM_Dark']={0.0,0.3,-12.0,88.0,0.6,14.0,1,true,'Stone_VM_Dark','',''},
  ['VM_House_PNE__Plaster_VM_Peach']={30.25,20.616,12.5,13.5,13.232,11.8,2,true,'Plaster_VM_Peach','','VM_House_PNE'},
  ['VM_House_PNE__Roof_VM_Terracotta_B']={30.66,23.481,12.457,14.98,10.176,15.505,2,true,'Roof_VM_Terracotta_B','','VM_House_PNE'},
  ['VM_House_PNE__Roof_VM_Terracotta_C']={30.675,23.163,12.475,14.65,9.557,15.577,2,true,'Roof_VM_Terracotta_C','','VM_House_PNE'},
  ['VM_House_PNE__Stone_VM_Grey']={30.383,17.477,12.47,13.955,23.554,12.46,2,true,'Stone_VM_Grey','','VM_House_PNE'},
  ['VM_House_PNE__Stone_VM_Mortar']={30.325,17.737,12.5,12.81,24.074,11.26,2,false,'Stone_VM_Mortar','','VM_House_PNE'},
  ['VM_House_PNE__Wood_VM_Timber']={30.675,16.982,12.5,15.17,22.065,15.632,2,true,'Wood_VM_Timber','','VM_House_PNE'},
  ['VM_House_PNW__Plaster_VM_Peach']={-28.95,21.124,13.4,12.0,14.249,11.8,2,true,'Plaster_VM_Peach','','VM_House_PNW'},
  ['VM_House_PNW__Roof_VM_Terracotta']={-29.259,23.924,13.415,15.084,11.387,14.13,2,true,'Roof_VM_Terracotta','','VM_House_PNW'},
  ['VM_House_PNW__Roof_VM_Terracotta_C']={-28.928,23.558,13.4,15.856,10.784,13.8,2,true,'Roof_VM_Terracotta_C','','VM_House_PNW'},
  ['VM_House_PNW__Stone_VM_Mortar']={-29.025,18.261,13.4,11.31,25.122,11.26,2,false,'Stone_VM_Mortar','','VM_House_PNW'},
  ['VM_House_PNW__Stone_VM_Warm']={-29.091,18.001,13.37,12.439,24.602,12.46,2,true,'Stone_VM_Warm','','VM_House_PNW'},
  ['VM_House_PNW__Wood_VM_Timber']={-28.95,17.477,13.4,15.865,23.054,14.32,2,true,'Wood_VM_Timber','','VM_House_PNW'},
  ['VM_House_S0E__Plaster_VM_Cream']={16.6,24.065,-0.75,11.4,20.131,9.5,2,true,'Plaster_VM_Cream','','VM_House_S0E'},
  ['VM_House_S0E__Roof_VM_Terracotta']={16.657,29.463,-1.175,15.188,10.716,10.65,2,true,'Roof_VM_Terracotta','','VM_House_S0E'},
  ['VM_House_S0E__Roof_VM_Terracotta_C']={16.245,29.802,-1.19,14.539,11.417,10.98,2,true,'Roof_VM_Terracotta_C','','VM_House_S0E'},
  ['VM_House_S0E__Stone_VM_Mortar']={16.6,21.208,-0.825,10.86,31.016,8.81,2,true,'Stone_VM_Mortar','','VM_House_S0E'},
  ['VM_House_S0E__Stone_VM_Warm']={16.93,20.948,-0.58,11.46,30.496,10.56,2,true,'Stone_VM_Warm','','VM_House_S0E'},
  ['VM_House_S0E__Wood_VM_Timber']={16.6,20.413,-1.062,15.275,28.927,11.397,2,true,'Wood_VM_Timber','','VM_House_S0E'},
  ['VM_House_S0W__Plaster_VM_Peach']={-17.0,20.281,-1.2,10.8,12.561,8.6,2,true,'Plaster_VM_Peach','','VM_House_S0W'},
  ['VM_House_S0W__Roof_VM_Terracotta']={-17.01,22.991,-0.658,13.08,9.953,11.151,2,true,'Roof_VM_Terracotta','','VM_House_S0W'},
  ['VM_House_S0W__Roof_VM_Terracotta_C']={-17.0,22.594,-1.233,12.8,9.316,12.402,2,true,'Roof_VM_Terracotta_C','','VM_House_S0W'},
  ['VM_House_S0W__Stone_VM_Base']={-17.03,9.8,-1.353,11.46,8.2,9.013,2,true,'Stone_VM_Base','','VM_House_S0W'},
  ['VM_House_S0W__Stone_VM_Mortar']={-17.0,14.391,-1.275,10.26,17.381,7.91,2,false,'Stone_VM_Mortar','','VM_House_S0W'},
  ['VM_House_S0W__Wood_VM_Timber']={-17.0,16.619,-1.2,13.32,21.338,12.494,2,true,'Wood_VM_Timber','','VM_House_S0W'},
  ['VM_House_S1E__Plaster_VM_Ochre']={17.65,21.288,9.9,11.9,14.575,12.0,2,true,'Plaster_VM_Ochre','','VM_House_S1E'},
  ['VM_House_S1E__Roof_VM_Terracotta']={17.21,24.036,9.898,13.38,11.84,15.674,2,true,'Roof_VM_Terracotta','','VM_House_S1E'},
  ['VM_House_S1E__Roof_VM_Terracotta_B']={17.225,23.668,9.908,13.05,11.192,15.777,2,true,'Roof_VM_Terracotta_B','','VM_House_S1E'},
  ['VM_House_S1E__Stone_VM_Mortar']={17.575,18.43,9.975,11.21,25.46,11.31,2,true,'Stone_VM_Mortar','','VM_House_S1E'},
  ['VM_House_S1E__Stone_VM_Warm']={17.598,18.17,10.035,12.196,24.94,12.45,2,true,'Stone_VM_Warm','','VM_House_S1E'},
  ['VM_House_S1E__Wood_VM_Timber']={16.88,17.636,9.9,14.26,23.372,15.875,2,true,'Wood_VM_Timber','','VM_House_S1E'},
  ['VM_House_S1W__Plaster_VM_Cream']={-16.8,24.267,9.5,12.4,20.535,13.0,2,true,'Plaster_VM_Cream','','VM_House_S1W'},
  ['VM_House_S1W__Roof_VM_Terracotta']={-16.821,29.693,9.925,16.201,11.082,14.15,2,true,'Roof_VM_Terracotta','','VM_House_S1W'},
  ['VM_House_S1W__Roof_VM_Terracotta_B']={-17.156,30.043,9.94,15.472,11.719,14.48,2,true,'Roof_VM_Terracotta_B','','VM_House_S1W'},
  ['VM_House_S1W__Stone_VM_Grey']={-16.976,21.144,9.631,12.153,30.888,13.457,2,true,'Stone_VM_Grey','','VM_House_S1W'},
  ['VM_House_S1W__Stone_VM_Mortar']={-16.725,21.404,9.575,11.71,31.408,12.31,2,true,'Stone_VM_Mortar','','VM_House_S1W'},
  ['VM_House_S1W__Wood_VM_Timber']={-16.8,20.62,9.925,16.265,29.34,14.67,2,true,'Wood_VM_Timber','','VM_House_S1W'},
  ['VM_Town_Medallion__Metal_VM_Bronze']={0.0,5.695,50.0,17.6,0.71,17.6,2,true,'Metal_VM_Bronze','',''},
  ['VM_Town_Medallion__Metal_VM_Iron']={-0.65,5.735,50.175,8.34,0.39,4.59,2,false,'Metal_VM_Iron','',''},
  ['VM_Town_Medallion__Stone_Paving_VM_Edge']={0.0,5.625,50.0,18.0,0.57,18.0,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_Medallion__Stone_Paving_VM_Joint']={0.0,5.115,50.0,17.964,0.85,17.964,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_Medallion__Stone_VM_Base']={0.0,5.61,50.0,18.0,0.54,18.0,2,false,'Stone_VM_Base','',''},
  ['VM_Town_Medallion__Stone_VM_Trim']={0.0,5.455,50.0,14.159,0.43,14.159,2,false,'Stone_VM_Trim','',''},
  ['VM_Town_TBridge__Metal_VM_Iron']={0.0,10.17,1.2,21.572,2.76,1.372,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_TBridge__Stone_VM_Dark']={0.0,4.625,-12.0,20.3,3.25,13.008,2,true,'Stone_VM_Dark','',''},
  ['VM_Town_TBridge__Stone_VM_Grey']={0.0,7.133,-10.0,23.3,4.494,25.5,2,true,'Stone_VM_Grey','',''},
  ['VM_Town_TBridge__Stone_VM_Mortar']={0.0,5.0,-10.405,22.18,8.8,25.19,2,true,'Stone_VM_Mortar','',''},
  ['VM_Town_TBridge__Stone_VM_Trim']={0.0,6.474,-10.0,22.48,6.852,24.4,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_TBridge__Window_VM_Lamp']={0.0,9.6,1.2,21.04,1.2,0.84,2,false,'Window_VM_Lamp','',''},
  ['VM_Town_TDress__Cloth_VM_Cream']={11.177,13.703,-0.75,2.294,1.805,6.31,2,false,'Cloth_VM_Cream','',''},
  ['VM_Town_TDress__Cloth_VM_Red']={11.177,13.703,-0.75,2.294,1.805,8.11,2,false,'Cloth_VM_Red','',''},
  ['VM_Town_TDress__Flower_VM_Pink']={1.009,12.166,6.939,73.538,11.659,26.231,2,false,'Flower_VM_Pink','',''},
  ['VM_Town_TDress__Flower_VM_Red']={-0.698,17.324,5.232,38.061,22.256,23.159,2,false,'Flower_VM_Red','',''},
  ['VM_Town_TDress__Flower_VM_Yellow']={1.022,17.333,6.915,73.481,22.157,26.324,2,false,'Flower_VM_Yellow','',''},
  ['VM_Town_TDress__Leaf_VM_Tuft']={1.028,21.617,6.873,73.348,13.119,26.337,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_TDress__Metal_VM_Bronze']={9.945,14.4,-4.6,1.119,0.999,0.34,2,false,'Metal_VM_Bronze','',''},
  ['VM_Town_TDress__Metal_VM_Iron']={-0.615,12.235,6.865,59.84,7.11,23.151,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_TDress__Wood_VM_Plank']={9.885,14.39,-4.6,1.89,1.72,0.48,2,false,'Wood_VM_Plank','',''},
  ['VM_Town_TEdges__Leaf_VM_Tuft']={0.397,6.462,7.549,69.127,1.724,25.043,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_TProps__Metal_VM_Iron']={0.0,11.795,17.831,55.485,11.83,27.822,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_TProps__Stone_VM_Warm']={0.0,6.21,24.4,55.5,0.8,14.7,2,true,'Stone_VM_Warm','',''},
  ['VM_Town_TProps__Window_VM_Lamp']={0.0,15.56,24.4,55.0,1.6,14.2,2,true,'Window_VM_Lamp','',''},
  ['VM_Town_TProps__Wood_VM_Plank']={-11.278,7.86,13.586,47.173,4.22,22.549,2,true,'Wood_VM_Plank','',''},
  ['VM_Town_TProps__Wood_VM_Timber']={-11.511,7.92,13.595,47.187,4.34,22.917,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_Cob']={0.646,6.608,4.536,62.589,1.676,51.037,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_CobB']={0.654,6.599,5.193,62.561,1.656,52.36,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_Edge']={0.1,5.835,5.943,22.78,0.57,18.215,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_Joint']={0.65,6.39,5.2,62.6,1.68,52.4,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Water_TCanal__Water_VM']={0.0,1.6,-12.0,88.0,2.0,12.0,7,false,'Water_VM','',''},
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
  {'COL_Bridge_001','Ramp',{0.0,6.204,-4.563},{-0.0,0.126,-0.992},{-1.0,0.0,0.0},{11.089,18.0,1.0},false},
  {'COL_Bridge_002','Ramp',{-0.0,6.7,-15.482},{-0.0,-0.036,-0.999},{-1.0,0.0,0.0},{11.007,18.0,1.0},false},
  {'COL_Bridge_003','Block',{-10.0,9.7,-10.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,22.0,7.4},false},
  {'COL_Bridge_004','Block',{10.0,9.7,-10.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,22.0,7.4},false},
  {'COL_Canal_001','Block',{-70.0,9.0,-5.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{118.0,1.0,6.0},false},
  {'COL_Canal_002','Block',{-70.0,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{118.0,1.0,6.0},false},
  {'COL_Canal_003','Block',{88.5,9.0,-5.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{155.0,1.0,6.0},false},
  {'COL_Canal_004','Block',{88.5,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{155.0,1.0,6.0},false},
  {'COL_House_019','Block',{-17.0,13.6,-1.2},{-0.0,0.0,1.0},{1.0,0.0,0.0},{8.8,11.0,15.8},true},
  {'COL_House_020','Block',{-16.8,16.6,9.5},{-0.0,0.0,1.0},{1.0,0.0,0.0},{13.2,12.6,21.8},true},
  {'COL_House_021','Block',{-28.95,13.6,13.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.2,12.0,15.8},true},
  {'COL_House_022','Block',{16.6,16.6,-0.75},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{9.7,11.6,21.8},true},
  {'COL_House_023','Block',{17.65,13.6,9.9},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{12.2,12.1,15.8},true},
  {'COL_House_024','Block',{30.25,13.6,12.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{13.7,12.0,15.8},true},
  {'COL_TGround_001','Block',{0.0,4.0,17.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{88.0,45.0,4.0},false},
  {'COL_TGround_002','Block',{0.0,5.0,-29.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{88.0,21.0,4.0},false},
  {'COL_TProps_001','Block',{-10.6,10.5,17.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_002','Block',{10.6,10.5,17.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_003','Block',{-27.0,10.5,31.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_004','Block',{27.0,10.5,31.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_005','Block',{11.2,7.15,4.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,5.3,2.3},false},
  {'COL_TProps_006','Block',{-20.6,7.7,22.0},{-0.482,0.0,-0.876},{-0.876,0.0,0.482},{7.0,4.6,3.4},false},
  {'COL_TProps_007','Block',{-25.05,7.15,21.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.1,2.8,2.3},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
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
  {'L_VM_Lamp_P1','POINT',{-10.1,9.65,1.2},{255,223,173},5.8,0.34,false,true},
  {'L_VM_Lamp_P2','POINT',{10.1,9.65,1.2},{255,223,173},5.8,0.34,false,true},
  {'L_VM_Lamp_T1','POINT',{-10.6,15.61,17.8},{255,223,173},5.8,0.34,false,true},
  {'L_VM_Lamp_T2','POINT',{10.6,15.61,17.8},{255,223,173},5.8,0.34,false,true},
  {'L_VM_Lamp_T3','POINT',{-27.0,15.61,31.0},{255,223,173},5.8,0.34,false,true},
  {'L_VM_Lamp_T4','POINT',{27.0,15.61,31.0},{255,223,173},5.8,0.34,false,true},
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
}

if APLICAR_LIGHTING then
  local Lg = game:GetService('Lighting')
  Lg.GeographicLatitude = 47.564
  Lg.ClockTime = 15.8
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
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (-0.77, 0.50, 0.41) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
print(string.format('VM_TRECHO_V1 montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
