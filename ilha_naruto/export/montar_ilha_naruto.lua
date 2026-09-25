-- montar_ilha_naruto.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 1c2e6437
-- 1) Importe os FBX ILHA1_*_1c2e64.fbx (3D Importer) para dentro de workspace.ILHA_NARUTO. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script ILHA_NARUTO_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = '1c2e6437'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o ilha INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('ILHA_NARUTO') or Instance.new('Model', workspace)
root.Name = 'ILHA_NARUTO'
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
  ['Bark_Dark'] = {c = Color3.fromRGB(86,60,46), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Cliff_Rock_B'] = {c = Color3.fromRGB(157,148,136), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Dark'] = {c = Color3.fromRGB(102,96,90), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Dark_B'] = {c = Color3.fromRGB(87,82,79), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Tan'] = {c = Color3.fromRGB(164,134,104), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Tan_B'] = {c = Color3.fromRGB(178,148,116), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Tan_C'] = {c = Color3.fromRGB(142,116,92), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Tan_Dark'] = {c = Color3.fromRGB(112,90,72), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cliff_Rock_Tan_Top'] = {c = Color3.fromRGB(184,158,124), m = Enum.Material.Slate, t = 0.0, s = true, x = 'rock', w = nil},
  ['Cloth_Canvas'] = {c = Color3.fromRGB(225,212,188), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_EntRed'] = {c = Color3.fromRGB(182,34,32), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_Red'] = {c = Color3.fromRGB(196,80,75), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_Royal_Blue'] = {c = Color3.fromRGB(44,62,170), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VilLantern'] = {c = Color3.fromRGB(212,46,34), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VilNoren'] = {c = Color3.fromRGB(240,232,214), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Crystal_Blue'] = {c = Color3.fromRGB(30,140,230), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_DBGate_Orb'] = {c = Color3.fromRGB(255,140,20), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_DBGate_Star'] = {c = Color3.fromRGB(206,24,16), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_SumAmber_Glow'] = {c = Color3.fromRGB(255,160,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_SumPortal_Glow'] = {c = Color3.fromRGB(58,70,232), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_SumStar_Glow'] = {c = Color3.fromRGB(178,222,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_SumYellow_Glow'] = {c = Color3.fromRGB(255,228,120), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['DB_Energy_Glow'] = {c = Color3.fromRGB(255,132,30), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Dirt_Pit'] = {c = Color3.fromRGB(166,112,70), m = Enum.Material.Ground, t = 0.0, s = false, x = 'dirt', w = nil},
  ['Dirt_TerPatch'] = {c = Color3.fromRGB(122,78,48), m = Enum.Material.Ground, t = 0.0, s = false, x = 'dirt', w = nil},
  ['Emblem_Cream'] = {c = Color3.fromRGB(237,231,215), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Energy_Core_DB_Glow'] = {c = Color3.fromRGB(255,214,120), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_White'] = {c = Color3.fromRGB(236,232,220), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Foam'] = {c = Color3.fromRGB(236,244,250), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_Konoha'] = {c = Color3.fromRGB(112,170,62), m = Enum.Material.Grass, t = 0.0, s = false, x = 'grass', w = nil},
  ['Grass_Konoha_B'] = {c = Color3.fromRGB(98,156,56), m = Enum.Material.Grass, t = 0.0, s = false, x = 'grass', w = nil},
  ['Lantern_Glow'] = {c = Color3.fromRGB(255,146,56), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Broad'] = {c = Color3.fromRGB(122,160,58), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Pine'] = {c = Color3.fromRGB(45,111,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Pine_Light'] = {c = Color3.fromRGB(87,145,77), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Shadow'] = {c = Color3.fromRGB(36,77,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_DBGate_Glow'] = {c = Color3.fromRGB(255,214,112), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold'] = {c = Color3.fromRGB(222,170,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Iron'] = {c = Color3.fromRGB(116,114,112), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VilSteel'] = {c = Color3.fromRGB(198,206,216), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_Cream'] = {c = Color3.fromRGB(232,212,172), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'plaster', w = nil},
  ['Plaster_HouPeach'] = {c = Color3.fromRGB(240,206,164), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'plaster', w = nil},
  ['Roof_Blue'] = {c = Color3.fromRGB(62,84,138), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_Blue_B'] = {c = Color3.fromRGB(74,98,152), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_DBGate_Ridge'] = {c = Color3.fromRGB(36,40,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_DBGate_Tile'] = {c = Color3.fromRGB(66,80,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_EntJadeDark'] = {c = Color3.fromRGB(38,76,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_Green'] = {c = Color3.fromRGB(72,118,80), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Roof_Terracotta'] = {c = Color3.fromRGB(176,72,50), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'roof', w = nil},
  ['Rope'] = {c = Color3.fromRGB(190,172,140), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['Sakura_Pink'] = {c = Color3.fromRGB(255,140,191), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_EntLion'] = {c = Color3.fromRGB(112,116,126), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_EntLionMane'] = {c = Color3.fromRGB(172,175,184), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Paving_Warm'] = {c = Color3.fromRGB(206,188,158), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = 'stone', w = nil},
  ['Stone_Paving_Warm_B'] = {c = Color3.fromRGB(218,202,172), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = 'stone', w = nil},
  ['Stone_Paving_Warm_C'] = {c = Color3.fromRGB(188,170,142), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = 'stone', w = nil},
  ['Stone_SumBlock'] = {c = Color3.fromRGB(140,144,188), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_SumFloor_Pale'] = {c = Color3.fromRGB(212,194,236), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_TerGrout'] = {c = Color3.fromRGB(96,88,80), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Dark'] = {c = Color3.fromRGB(128,120,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light'] = {c = Color3.fromRGB(178,170,156), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light_B'] = {c = Color3.fromRGB(192,184,170), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light_C'] = {c = Color3.fromRGB(158,150,138), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_WtrVoid'] = {c = Color3.fromRGB(30,32,38), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Summon_Blue_Glow'] = {c = Color3.fromRGB(80,150,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Summon_Floor'] = {c = Color3.fromRGB(150,112,188), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Summon_Star_Glow'] = {c = Color3.fromRGB(255,186,60), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Summon_Stone'] = {c = Color3.fromRGB(112,112,150), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Summon_Stone_Dark'] = {c = Color3.fromRGB(80,80,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Water'] = {c = Color3.fromRGB(40,128,160), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Water_WtrFall'] = {c = Color3.fromRGB(104,184,232), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Water_WtrSheet'] = {c = Color3.fromRGB(190,228,252), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Window_Warm'] = {c = Color3.fromRGB(214,140,74), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wood_Dark'] = {c = Color3.fromRGB(92,64,47), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Dark_B'] = {c = Color3.fromRGB(109,74,49), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Dark_C'] = {c = Color3.fromRGB(77,60,52), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Lacquer_Red'] = {c = Color3.fromRGB(168,42,32), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Light'] = {c = Color3.fromRGB(148,110,80), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Plank'] = {c = Color3.fromRGB(126,92,66), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Plank_B'] = {c = Color3.fromRGB(143,105,71), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_VilLacquerDark'] = {c = Color3.fromRGB(118,30,24), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
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
local FBX = {[1]='ILHA1_02_TERRAIN_1c2e64.fbx', [2]='ILHA1_03_MINING_1c2e64.fbx', [3]='ILHA1_04_VILLAGE_1c2e64.fbx', [4]='ILHA1_05_SUMMON_1c2e64.fbx', [5]='ILHA1_06_WATER_1c2e64.fbx', [6]='ILHA1_07_NEXT_ISLAND_1c2e64.fbx', [7]='ILHA1_08_PURCHASE_GATES_1c2e64.fbx', [8]='ILHA1_09_PROPS_1c2e64.fbx', [9]='ILHA1_10_VEGETATION_1c2e64.fbx', [10]='ILHA1_12_VFX_HELPERS_1c2e64.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['ENT_Bridge__Cliff_Rock_Tan']={-0.252,-85.375,254.131,46.874,57.25,71.398,1,true,'Cliff_Rock_Tan','',''},
  ['ENT_Bridge__Cliff_Rock_Tan_Dark']={0.147,-91.499,255.35,42.957,45.002,64.029,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['ENT_Bridge__Lantern_Glow']={0.0,11.007,282.062,30.24,2.505,89.124,1,false,'Lantern_Glow','',''},
  ['ENT_Bridge__Metal_Gold']={0.0,12.275,262.0,27.77,2.15,79.24,1,true,'Metal_Gold','',''},
  ['ENT_Bridge__Stone_Paving_Warm']={1.225,6.083,275.355,47.688,0.665,106.553,1,false,'Stone_Paving_Warm','',''},
  ['ENT_Bridge__Stone_Paving_Warm_B']={-0.548,6.084,275.36,51.038,0.666,106.572,1,false,'Stone_Paving_Warm_B','',''},
  ['ENT_Bridge__Stone_Wall_Dark']={0.0,-21.495,274.55,48.0,70.61,108.9,1,true,'Stone_Wall_Dark','',''},
  ['ENT_Bridge__Stone_Wall_Light']={0.0,-21.62,273.825,30.792,67.56,106.65,1,true,'Stone_Wall_Light','',''},
  ['ENT_Bridge__Stone_Wall_Light_B']={-0.065,-21.62,274.575,30.663,67.56,105.15,1,true,'Stone_Wall_Light_B','',''},
  ['ENT_Bridge__Wood_Dark']={0.0,8.7,262.0,26.45,3.6,68.183,1,true,'Wood_Dark','',''},
  ['ENT_Bridge__Wood_Light']={0.0,8.7,262.0,26.45,3.6,75.8,1,true,'Wood_Light','',''},
  ['SKY_Islets__Bark_Dark']={2.34,23.467,537.618,934.031,107.347,708.259,1,false,'Bark_Dark','k',''},
  ['SKY_Islets__Cliff_Rock_Tan']={5.017,3.604,536.802,957.963,137.002,728.959,1,false,'Cliff_Rock_Tan','k',''},
  ['SKY_Islets__Cliff_Rock_Tan_Dark']={5.817,-5.958,538.016,952.627,136.567,724.991,1,false,'Cliff_Rock_Tan_Dark','k',''},
  ['SKY_Islets__Grass_Konoha']={3.528,19.9,537.989,963.294,101.0,732.094,1,false,'Grass_Konoha','k',''},
  ['SKY_Islets__Leaf_Broad']={2.337,28.409,537.336,936.878,107.554,712.245,1,false,'Leaf_Broad','k',''},
  ['SKY_Islets__Leaf_Shadow']={2.371,25.947,537.53,936.127,103.052,711.574,1,false,'Leaf_Shadow','k',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_g15_11']={-36.463,-16.839,614.445,181.036,194.323,66.251,1,true,'Cliff_Rock_Tan','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_g16_11']={80.155,-16.839,595.789,166.285,194.323,94.65,1,true,'Cliff_Rock_Tan','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_B']={16.621,-15.038,593.951,283.924,197.925,106.336,1,true,'Cliff_Rock_Tan_B','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_C']={16.388,-10.339,594.151,284.625,207.322,103.515,1,true,'Cliff_Rock_Tan_C','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_Dark_g15_11']={-61.2,-15.15,610.095,128.848,197.7,61.22,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_Dark_g16_11']={79.314,-15.15,590.015,162.181,197.7,101.381,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_Top_g15_11']={-29.359,23.639,613.244,194.224,146.424,67.667,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_Top_g16_11']={63.747,23.649,616.27,133.812,146.547,53.497,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Back_Massif__Cliff_Rock_Tan_Top_g17_11']={144.171,14.357,577.295,37.738,122.504,74.791,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Back_Massif__Grass_Konoha_g15_11']={-29.471,27.4,614.13,194.712,115.19,66.668,1,false,'Grass_Konoha','',''},
  ['TER_Back_Massif__Grass_Konoha_g16_11']={63.396,28.26,616.469,130.347,111.479,53.866,1,false,'Grass_Konoha','',''},
  ['TER_Back_Massif__Grass_Konoha_g17_11']={145.225,23.703,573.303,36.43,105.812,65.269,1,false,'Grass_Konoha','',''},
  ['TER_Back_Massif__Grass_Konoha_B_g15_11']={-38.593,28.182,614.292,170.781,111.636,66.491,1,false,'Grass_Konoha_B','',''},
  ['TER_Back_Massif__Grass_Konoha_B_g16_11']={79.264,28.123,591.701,162.083,111.754,102.228,1,false,'Grass_Konoha_B','',''},
  ['TER_Cliff_Core__Cliff_Rock_Tan_Dark']={4.005,-59.0,464.699,305.59,110.0,324.198,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan']={0.955,-58.96,433.646,335.102,110.08,304.268,1,true,'Cliff_Rock_Tan','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan_B']={1.455,-59.242,426.302,338.868,109.517,291.414,1,true,'Cliff_Rock_Tan_B','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan_C']={3.427,-59.396,421.024,329.855,109.208,277.384,1,true,'Cliff_Rock_Tan_C','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan_Dark']={1.207,-57.05,431.994,336.509,113.9,305.075,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan_Top_g14_12']={-138.098,-45.086,498.506,60.073,88.332,174.592,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan_Top_g15_13']={14.704,-47.06,417.164,312.416,85.28,275.473,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Cliffs_Lower__Cliff_Rock_Tan_Top_g16_13']={83.089,-45.549,397.643,172.746,89.258,230.627,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Cliffs_Lower__Grass_Konoha']={2.132,-20.676,419.485,338.298,41.512,274.695,1,false,'Grass_Konoha','',''},
  ['TER_Cliffs_Lower__Grass_Konoha_B']={0.055,-21.398,410.673,332.602,43.195,256.861,1,false,'Grass_Konoha_B','',''},
  ['TER_Cliffs_Upper__Cliff_Rock_Tan']={4.544,-5.338,436.864,311.849,34.921,277.105,1,true,'Cliff_Rock_Tan','',''},
  ['TER_Cliffs_Upper__Cliff_Rock_Tan_B']={3.918,-4.432,417.826,310.589,33.914,236.98,1,true,'Cliff_Rock_Tan_B','',''},
  ['TER_Cliffs_Upper__Cliff_Rock_Tan_C']={3.692,-5.001,414.905,312.336,35.036,233.399,1,true,'Cliff_Rock_Tan_C','',''},
  ['TER_Cliffs_Upper__Cliff_Rock_Tan_Dark']={4.533,-2.435,437.395,310.226,40.178,275.491,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Cliffs_Upper__Cliff_Rock_Tan_Top_g15_13']={-75.056,-5.086,405.83,154.141,21.833,215.123,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Cliffs_Upper__Cliff_Rock_Tan_Top_g16_13']={11.689,3.389,436.708,296.899,35.022,276.895,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Cliffs_Upper__Grass_Konoha']={3.605,0.192,423.139,311.857,31.776,229.74,1,false,'Grass_Konoha','',''},
  ['TER_Cliffs_Upper__Grass_Konoha_B']={4.016,2.485,430.472,310.81,27.191,245.42,1,false,'Grass_Konoha_B','',''},
  ['TER_Ground__Cliff_Rock_Tan_Dark']={4.002,9.05,456.15,306.996,25.7,308.5,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Ground__Grass_Konoha_B']={4.002,14.05,456.15,306.996,16.3,308.5,1,false,'Grass_Konoha_B','',''},
  ['TER_Guards__Stone_Wall_Dark_g15_12']={-0.213,17.435,447.179,236.573,15.07,217.842,1,true,'Stone_Wall_Dark','',''},
  ['TER_Guards__Stone_Wall_Dark_g16_12']={54.257,14.435,445.183,96.709,9.07,128.495,1,true,'Stone_Wall_Dark','',''},
  ['TER_Guards__Stone_Wall_Light_g15_11']={-62.25,20.42,532.544,112.2,8.45,46.812,1,true,'Stone_Wall_Light','',''},
  ['TER_Guards__Stone_Wall_Light_g15_12']={-57.068,14.42,447.575,102.003,8.45,133.844,1,true,'Stone_Wall_Light','',''},
  ['TER_Guards__Stone_Wall_Light_g16_11']={60.087,23.42,546.8,107.875,2.45,1.3,1,true,'Stone_Wall_Light','',''},
  ['TER_Guards__Stone_Wall_Light_g16_12']={21.756,14.42,423.847,192.25,8.45,170.833,1,true,'Stone_Wall_Light','',''},
  ['TER_Guards__Stone_Wall_Light_C']={2.13,17.42,444.704,225.041,14.45,205.492,1,true,'Stone_Wall_Light_C','',''},
  ['TER_Paths__Stone_Paving_Warm']={-6.508,14.284,477.217,250.716,16.409,188.234,1,false,'Stone_Paving_Warm','',''},
  ['TER_Paths__Stone_Paving_Warm_C']={-10.001,14.285,477.725,243.801,16.41,189.25,1,false,'Stone_Paving_Warm_C','',''},
  ['TER_Paths__Stone_TerGrout']={-6.526,14.11,477.725,250.952,16.42,189.45,1,true,'Stone_TerGrout','',''},
  ['TER_Pit_Floor__Dirt_Pit']={0.0,2.66,420.0,120.4,1.32,120.4,1,false,'Dirt_Pit','',''},
  ['TER_Pit_Floor__Dirt_TerPatch']={-4.001,3.21,421.966,105.597,0.22,113.839,1,false,'Dirt_TerPatch','',''},
  ['TER_Promontories__Cliff_Rock_Tan']={12.12,-60.65,379.946,342.41,106.699,173.505,1,true,'Cliff_Rock_Tan','',''},
  ['TER_Promontories__Cliff_Rock_Tan_B']={9.908,-60.65,378.621,340.235,106.699,173.488,1,true,'Cliff_Rock_Tan_B','',''},
  ['TER_Promontories__Cliff_Rock_Tan_C']={11.165,-60.65,377.636,339.128,106.699,166.832,1,true,'Cliff_Rock_Tan_C','',''},
  ['TER_Promontories__Cliff_Rock_Tan_Dark']={10.755,-59.05,377.439,341.553,109.9,174.09,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Promontories__Cliff_Rock_Tan_Top']={11.591,-35.486,378.657,343.284,61.132,176.141,1,true,'Cliff_Rock_Tan_Top','',''},
  ['TER_Promontories__Grass_Konoha']={11.298,-14.052,379.17,340.333,20.505,172.125,1,false,'Grass_Konoha','',''},
  ['TER_Promontories__Grass_Konoha_B']={10.977,-13.238,373.644,341.76,18.876,164.075,1,false,'Grass_Konoha_B','',''},
  ['TER_Retaining_Walls__Stone_Wall_Dark_g15_11']={-62.286,14.06,531.835,111.781,16.602,43.939,1,true,'Stone_Wall_Dark','',''},
  ['TER_Retaining_Walls__Stone_Wall_Dark_g15_12']={-54.664,9.599,447.761,111.272,13.482,132.094,1,true,'Stone_Wall_Dark','',''},
  ['TER_Retaining_Walls__Stone_Wall_Dark_g15_13']={-35.703,6.602,362.356,78.836,7.476,49.349,1,true,'Stone_Wall_Dark','',''},
  ['TER_Retaining_Walls__Stone_Wall_Dark_g16_11']={67.074,16.154,530.575,121.382,12.371,38.296,1,true,'Stone_Wall_Dark','',''},
  ['TER_Retaining_Walls__Stone_Wall_Dark_g16_12']={74.266,12.6,464.497,146.668,19.481,165.806,1,true,'Stone_Wall_Dark','',''},
  ['TER_Retaining_Walls__Stone_Wall_Dark_g16_13']={58.426,9.601,361.951,120.927,13.479,48.581,1,true,'Stone_Wall_Dark','',''},
  ['TER_Retaining_Walls__Stone_Wall_Light_g15_11']={-62.234,14.543,531.823,111.69,14.378,43.722,1,true,'Stone_Wall_Light','',''},
  ['TER_Retaining_Walls__Stone_Wall_Light_g15_12']={9.964,13.44,443.753,239.729,17.828,211.939,1,true,'Stone_Wall_Light','',''},
  ['TER_Retaining_Walls__Stone_Wall_Light_g16_12']={73.832,13.45,464.206,147.379,16.552,166.155,1,true,'Stone_Wall_Light','',''},
  ['TER_Retaining_Walls__Stone_Wall_Light_g16_13']={58.478,10.463,361.751,120.657,10.537,47.935,1,true,'Stone_Wall_Light','',''},
  ['TER_Retaining_Walls__Stone_Wall_Light_B_g15_12']={0.384,13.446,447.802,236.856,17.839,211.748,1,true,'Stone_Wall_Light_B','',''},
  ['TER_Retaining_Walls__Stone_Wall_Light_B_g16_12']={50.583,10.777,446.577,103.361,11.197,125.65,1,true,'Stone_Wall_Light_B','',''},
  ['TER_Ring_Paving__Stone_Paving_Warm_g15_12']={-38.824,10.225,444.949,83.217,0.29,125.648,1,false,'Stone_Paving_Warm','',''},
  ['TER_Ring_Paving__Stone_Paving_Warm_g15_13']={-35.158,10.225,362.797,73.065,0.289,46.47,1,false,'Stone_Paving_Warm','',''},
  ['TER_Ring_Paving__Stone_Paving_Warm_g16_12']={42.482,10.225,444.637,90.634,0.29,126.272,1,false,'Stone_Paving_Warm','',''},
  ['TER_Ring_Paving__Stone_Paving_Warm_g16_13']={36.147,10.225,363.085,73.67,0.29,47.047,1,false,'Stone_Paving_Warm','',''},
  ['TER_Ring_Paving__Stone_Paving_Warm_C']={3.517,10.225,422.902,167.429,0.29,166.673,1,false,'Stone_Paving_Warm_C','',''},
  ['TER_Ring_Paving__Stone_TerGrout']={3.443,6.425,423.443,169.687,7.45,169.687,1,true,'Stone_TerGrout','',''},
  ['TER_Stairs__Stone_Wall_Dark_g15_12']={-33.627,14.583,438.663,152.613,17.634,221.925,1,true,'Stone_Wall_Dark','',''},
  ['TER_Stairs__Stone_Wall_Dark_g16_12']={50.782,13.65,469.695,90.265,7.5,86.06,1,true,'Stone_Wall_Dark','',''},
  ['TER_Stairs__Stone_Wall_Light']={-7.136,13.575,437.95,205.783,15.75,220.05,1,true,'Stone_Wall_Light','',''},
  ['TER_Stairs__Stone_Wall_Light_B']={-11.263,13.95,440.534,197.296,16.5,218.283,1,true,'Stone_Wall_Light_B','',''},
  ['TER_Stream_Banks__Stone_Wall_Dark']={-110.085,4.759,415.338,26.42,3.319,141.129,1,true,'Stone_Wall_Dark','',''},
  ['TER_Stream_Banks__Stone_Wall_Light']={-109.408,4.76,421.924,27.653,3.32,164.617,1,true,'Stone_Wall_Light','',''},
  ['TER_Stream_Banks__Stone_Wall_Light_C']={-110.768,4.76,422.064,25.059,3.32,143.623,1,true,'Stone_Wall_Light_C','',''},
  ['TER_Stream_Bed__Cliff_Rock_Tan_Dark']={-109.101,-0.2,420.441,27.397,7.2,166.665,1,true,'Cliff_Rock_Tan_Dark','',''},
  ['TER_Streets__Stone_Paving_Warm_B_g15_11']={-49.224,19.285,535.14,102.885,6.41,49.12,1,false,'Stone_Paving_Warm_B','',''},
  ['TER_Streets__Stone_Paving_Warm_B_g16_11']={-3.261,19.284,503.802,194.811,6.408,111.796,1,false,'Stone_Paving_Warm_B','',''},
  ['TER_Streets__Stone_Paving_Warm_C']={0.005,19.284,506.673,192.342,6.408,106.055,1,false,'Stone_Paving_Warm_C','',''},
  ['TER_Streets__Stone_TerGrout']={-2.274,19.11,503.78,197.069,6.42,112.04,1,true,'Stone_TerGrout','',''},
  ['MINE_Core_Formation__Cliff_Rock_Dark']={0.182,6.578,418.747,19.911,8.635,14.962,2,true,'Cliff_Rock_Dark','',''},
  ['MINE_Core_Formation__Cliff_Rock_Dark_B']={-0.319,6.614,419.97,18.72,8.771,20.114,2,true,'Cliff_Rock_Dark_B','',''},
  ['MINE_Core_Formation__Dirt_Pit']={0.207,3.7,419.799,19.454,1.8,19.776,2,false,'Dirt_Pit','',''},
  ['MINE_Derricks__Cliff_Rock_Dark_B']={-0.085,5.975,419.868,68.081,6.15,80.246,2,true,'Cliff_Rock_Dark_B','',''},
  ['MINE_Derricks__Metal_Dark']={0.0,12.293,420.0,68.415,9.265,80.41,2,true,'Metal_Dark','',''},
  ['MINE_Derricks__Rope']={0.0,11.631,420.0,68.287,11.361,80.045,2,false,'Rope','',''},
  ['MINE_Derricks__Stone_Wall_Dark']={0.0,3.35,420.0,73.718,0.8,86.044,2,true,'Stone_Wall_Dark','',''},
  ['MINE_Derricks__Wood_Dark_B']={0.0,9.932,420.0,72.501,12.536,84.827,2,true,'Wood_Dark_B','',''},
  ['MINE_Derricks__Wood_Plank_B']={0.0,12.275,420.0,68.225,9.55,80.22,2,true,'Wood_Plank_B','',''},
  ['MINE_Pit_Fence__Lantern_Glow']={0.0,15.54,420.0,117.152,1.12,122.108,2,false,'Lantern_Glow','',''},
  ['MINE_Pit_Fence__Stone_Wall_Dark']={0.0,10.65,420.0,118.171,0.9,122.884,2,true,'Stone_Wall_Dark','',''},
  ['MINE_Pit_Fence__Wood_Dark']={0.0,13.515,420.085,122.727,6.63,122.718,2,true,'Wood_Dark','',''},
  ['MINE_Pit_Fence__Wood_Dark_B']={-0.125,13.515,419.885,122.306,6.63,122.658,2,true,'Wood_Dark_B','',''},
  ['MINE_Pit_Fence__Wood_Plank']={0.0,12.275,419.584,121.646,1.83,119.775,2,true,'Wood_Plank','',''},
  ['MINE_Pit_Fence__Wood_Plank_B']={0.0,12.275,420.0,122.171,1.83,121.665,2,true,'Wood_Plank_B','',''},
  ['MINE_Pit_Ramps__Wood_Dark']={-0.054,7.815,412.95,117.253,11.61,38.229,2,true,'Wood_Dark','',''},
  ['MINE_Pit_Ramps__Wood_Dark_B']={0.171,7.815,412.927,117.018,11.61,38.275,2,true,'Wood_Dark_B','',''},
  ['MINE_Pit_Ramps__Wood_Plank']={-0.021,8.019,413.226,116.818,10.462,38.445,2,true,'Wood_Plank','',''},
  ['MINE_Pit_Ramps__Wood_Plank_B']={-0.0,8.018,413.225,116.86,10.464,38.444,2,true,'Wood_Plank_B','',''},
  ['MINE_Pit_Rubble__Cliff_Rock_B']={4.045,3.271,419.002,94.428,0.702,109.62,2,true,'Cliff_Rock_B','',''},
  ['MINE_Pit_Stairs__Stone_Wall_Dark']={0.15,7.3,420.0,12.7,8.2,120.05,2,true,'Stone_Wall_Dark','',''},
  ['MINE_Pit_Stairs__Stone_Wall_Light']={0.075,7.425,420.0,13.05,8.45,120.4,2,true,'Stone_Wall_Light','',''},
  ['MINE_Pit_Stairs__Stone_Wall_Light_B']={0.0,7.425,420.0,12.9,8.45,120.4,2,true,'Stone_Wall_Light_B','',''},
  ['MINE_Props__Cliff_Rock_Dark']={-0.658,6.035,412.281,94.546,2.47,92.582,2,true,'Cliff_Rock_Dark','',''},
  ['MINE_Props__Crystal_Blue']={31.379,5.869,376.789,28.301,2.166,21.252,2,false,'Crystal_Blue','',''},
  ['MINE_Props__Lantern_Glow']={-7.384,7.9,423.453,95.522,0.92,106.053,2,false,'Lantern_Glow','',''},
  ['MINE_Props__Metal_Dark']={-3.564,6.334,423.48,104.19,6.292,107.041,2,true,'Metal_Dark','',''},
  ['MINE_Props__Wood_Dark_C']={-0.168,6.3,420.0,113.381,6.6,118.49,2,true,'Wood_Dark_C','',''},
  ['MINE_Props__Wood_Plank']={0.359,5.1,419.795,96.578,4.1,108.316,2,true,'Wood_Plank','',''},
  ['MINE_Ring_Toros__Lantern_Glow']={0.0,14.6,420.0,157.309,1.25,157.309,2,false,'Lantern_Glow','',''},
  ['MINE_Ring_Toros__Stone_Wall_Dark']={0.0,13.225,420.0,158.532,6.05,158.532,2,true,'Stone_Wall_Dark','',''},
  ['MINE_Ring_Toros__Stone_Wall_Light_C']={0.0,13.702,420.0,157.826,6.005,157.826,2,true,'Stone_Wall_Light_C','',''},
  ['ENT_Gate__Cloth_EntRed']={0.0,14.75,310.0,59.2,9.0,1.22,3,true,'Cloth_EntRed','','ENT_Gate'},
  ['ENT_Gate__Emblem_Cream']={0.0,16.05,310.0,58.6,2.4,0.62,3,false,'Emblem_Cream','','ENT_Gate'},
  ['ENT_Gate__Lantern_Glow']={0.0,21.7,309.3,16.551,2.9,2.262,3,false,'Lantern_Glow','','ENT_Gate'},
  ['ENT_Gate__Metal_Gold']={0.0,26.895,310.945,59.3,38.21,6.69,3,true,'Metal_Gold','','ENT_Gate'},
  ['ENT_Gate__Metal_Iron']={0.0,19.2,310.0,61.544,3.9,2.9,3,true,'Metal_Iron','','ENT_Gate'},
  ['ENT_Gate__Plaster_Cream']={0.0,16.25,310.0,46.6,15.5,1.2,3,true,'Plaster_Cream','','ENT_Gate'},
  ['ENT_Gate__Roof_EntJadeDark']={0.0,34.577,310.0,58.208,20.294,19.808,3,true,'Roof_EntJadeDark','','ENT_Gate'},
  ['ENT_Gate__Roof_Green']={0.0,33.548,310.0,56.983,18.096,18.591,3,true,'Roof_Green','','ENT_Gate'},
  ['ENT_Gate__Stone_Wall_Dark']={0.0,8.4,310.0,52.1,0.85,4.2,3,true,'Stone_Wall_Dark','','ENT_Gate'},
  ['ENT_Gate__Stone_Wall_Light']={0.0,7.3,310.0,52.4,2.2,4.6,3,true,'Stone_Wall_Light','','ENT_Gate'},
  ['ENT_Gate__Wood_Dark']={0.0,23.0,310.0,60.0,30.8,18.1,3,true,'Wood_Dark','','ENT_Gate'},
  ['ENT_Gate__Wood_Lacquer_Red']={0.0,23.15,310.0,51.8,29.7,4.6,3,true,'Wood_Lacquer_Red','','ENT_Gate'},
  ['ENT_Gate__Wood_Plank']={0.0,14.9,313.312,40.766,17.0,1.721,3,true,'Wood_Plank','','ENT_Gate'},
  ['ENT_Lions__Stone_EntLion']={0.0,14.025,304.146,44.468,6.85,5.133,3,true,'Stone_EntLion','',''},
  ['ENT_Lions__Stone_EntLionMane']={0.0,14.6,304.441,44.791,7.839,5.521,3,true,'Stone_EntLionMane','',''},
  ['ENT_Lions__Stone_Wall_Dark']={0.0,11.485,305.185,45.2,10.67,7.73,3,true,'Stone_Wall_Dark','',''},
  ['ENT_Lions__Stone_Wall_Light']={0.0,8.15,305.625,44.5,3.9,6.55,3,true,'Stone_Wall_Light','',''},
  ['VIL_Banners__Cloth_Red']={-0.0,22.0,519.0,26.2,7.0,0.2,3,false,'Cloth_Red','',''},
  ['VIL_Banners__Emblem_Cream']={-0.0,22.948,518.78,25.3,3.203,0.24,3,false,'Emblem_Cream','',''},
  ['VIL_Banners__Metal_Gold']={-0.0,23.5,519.365,28.15,7.4,1.17,3,true,'Metal_Gold','',''},
  ['VIL_Banners__Stone_Wall_Light']={-0.0,16.775,519.5,24.9,1.55,1.9,3,false,'Stone_Wall_Light','',''},
  ['VIL_Banners__Wood_Dark_B']={-0.0,21.95,519.415,27.2,8.9,0.73,3,false,'Wood_Dark_B','',''},
  ['VIL_House_East_01__Plaster_Cream']={-134.0,11.625,394.0,14.0,7.95,12.0,3,false,'Plaster_Cream','','VIL_House_East_01'},
  ['VIL_House_East_01__Roof_Terracotta']={-134.0,17.205,394.0,18.609,7.91,16.609,3,true,'Roof_Terracotta','','VIL_House_East_01'},
  ['VIL_House_East_01__Stone_Wall_Dark']={-134.0,1.5,394.0,15.8,12.6,13.8,3,false,'Stone_Wall_Dark','','VIL_House_East_01'},
  ['VIL_House_East_01__Stone_Wall_Light']={-134.05,1.975,393.95,16.3,12.35,14.3,3,true,'Stone_Wall_Light','','VIL_House_East_01'},
  ['VIL_House_East_01__Window_Warm']={-134.0,11.5,394.0,14.3,3.3,12.3,3,false,'Window_Warm','','VIL_House_East_01'},
  ['VIL_House_East_01__Wood_Dark']={-134.0,15.0,394.0,19.602,14.0,17.602,3,true,'Wood_Dark','','VIL_House_East_01'},
  ['VIL_House_East_02__Plaster_HouPeach']={-136.0,10.1,456.0,13.0,7.8,12.0,3,false,'Plaster_HouPeach','','VIL_House_East_02'},
  ['VIL_House_East_02__Roof_Green']={-136.0,15.705,456.0,17.609,7.71,16.609,3,true,'Roof_Green','','VIL_House_East_02'},
  ['VIL_House_East_02__Stone_Wall_Dark']={-136.0,6.3,456.0,13.9,1.8,12.9,3,false,'Stone_Wall_Dark','','VIL_House_East_02'},
  ['VIL_House_East_02__Window_Warm']={-136.0,10.1,456.0,13.3,3.3,12.3,3,false,'Window_Warm','','VIL_House_East_02'},
  ['VIL_House_East_02__Wood_Dark']={-136.0,13.75,456.0,18.601,13.3,17.602,3,true,'Wood_Dark','','VIL_House_East_02'},
  ['VIL_House_T1_01__Plaster_Cream']={-38.0,20.1,527.0,16.0,7.8,12.0,3,false,'Plaster_Cream','','VIL_House_T1_01'},
  ['VIL_House_T1_01__Roof_Green']={-37.6,24.95,527.0,19.823,9.22,16.624,3,true,'Roof_Green','','VIL_House_T1_01'},
  ['VIL_House_T1_01__Stone_Wall_Dark']={-38.0,16.3,527.0,16.9,1.8,12.9,3,false,'Stone_Wall_Dark','','VIL_House_T1_01'},
  ['VIL_House_T1_01__Window_Warm']={-38.0,19.95,527.0,16.3,3.6,12.3,3,false,'Window_Warm','','VIL_House_T1_01'},
  ['VIL_House_T1_01__Wood_Dark']={-37.4,23.75,527.0,20.401,13.3,17.602,3,true,'Wood_Dark','','VIL_House_T1_01'},
  ['VIL_House_T1_02__Plaster_HouPeach']={84.0,20.1,530.0,16.0,7.8,13.0,3,false,'Plaster_HouPeach','','VIL_House_T1_02'},
  ['VIL_House_T1_02__Roof_Terracotta']={84.0,25.708,530.0,20.596,7.716,17.596,3,true,'Roof_Terracotta','','VIL_House_T1_02'},
  ['VIL_House_T1_02__Stone_Wall_Dark']={84.0,16.3,530.0,16.9,1.8,13.9,3,false,'Stone_Wall_Dark','','VIL_House_T1_02'},
  ['VIL_House_T1_02__Window_Warm']={84.0,20.1,530.0,16.3,3.3,13.3,3,false,'Window_Warm','','VIL_House_T1_02'},
  ['VIL_House_T1_02__Wood_Dark']={84.0,23.75,530.0,21.602,13.3,18.602,3,true,'Wood_Dark','','VIL_House_T1_02'},
  ['VIL_House_T1_03__Plaster_Cream']={-83.5,20.1,528.0,15.0,7.8,13.0,3,false,'Plaster_Cream','','VIL_House_T1_03'},
  ['VIL_House_T1_03__Roof_Terracotta']={-82.903,25.43,528.0,18.416,8.26,17.609,3,true,'Roof_Terracotta','','VIL_House_T1_03'},
  ['VIL_House_T1_03__Stone_Wall_Dark']={-83.5,16.3,528.0,15.9,1.8,13.9,3,false,'Stone_Wall_Dark','','VIL_House_T1_03'},
  ['VIL_House_T1_03__Window_Warm']={-83.5,19.9,528.0,15.3,3.7,13.3,3,false,'Window_Warm','','VIL_House_T1_03'},
  ['VIL_House_T1_03__Wood_Dark']={-82.7,23.75,528.0,19.001,13.3,18.602,3,true,'Wood_Dark','','VIL_House_T1_03'},
  ['VIL_House_T1_04__Plaster_Cream']={112.0,20.1,504.0,14.0,7.8,12.0,3,false,'Plaster_Cream','','VIL_House_T1_04'},
  ['VIL_House_T1_04__Roof_Terracotta']={112.0,25.705,504.0,18.609,7.71,16.609,3,true,'Roof_Terracotta','','VIL_House_T1_04'},
  ['VIL_House_T1_04__Stone_Wall_Dark']={112.0,16.3,504.0,14.9,1.8,12.9,3,false,'Stone_Wall_Dark','','VIL_House_T1_04'},
  ['VIL_House_T1_04__Window_Warm']={112.0,20.1,504.0,14.3,3.3,12.3,3,false,'Window_Warm','','VIL_House_T1_04'},
  ['VIL_House_T1_04__Wood_Dark']={112.0,23.75,504.0,19.602,13.3,17.602,3,true,'Wood_Dark','','VIL_House_T1_04'},
  ['VIL_House_T2_01__Plaster_Cream']={98.0,30.2,580.0,16.0,16.0,14.0,3,false,'Plaster_Cream','','VIL_House_T2_01'},
  ['VIL_House_T2_01__Roof_Terracotta']={98.0,35.559,580.0,20.583,11.218,18.583,3,true,'Roof_Terracotta','','VIL_House_T2_01'},
  ['VIL_House_T2_01__Stone_Wall_Dark']={98.0,22.3,580.0,16.9,1.8,14.9,3,false,'Stone_Wall_Dark','','VIL_House_T2_01'},
  ['VIL_House_T2_01__Window_Warm']={98.0,30.8,580.0,16.3,12.7,14.3,3,false,'Window_Warm','','VIL_House_T2_01'},
  ['VIL_House_T2_01__Wood_Dark']={98.0,32.734,580.0,21.602,19.268,19.602,3,true,'Wood_Dark','','VIL_House_T2_01'},
  ['VIL_House_T2_02__Plaster_HouPeach']={-96.5,26.1,569.5,13.5,7.8,12.0,3,false,'Plaster_HouPeach','','VIL_House_T2_02'},
  ['VIL_House_T2_02__Roof_Terracotta']={-96.5,32.755,569.5,18.109,5.61,16.609,3,true,'Roof_Terracotta','','VIL_House_T2_02'},
  ['VIL_House_T2_02__Stone_Wall_Dark']={-96.5,22.3,569.5,14.4,1.8,12.9,3,false,'Stone_Wall_Dark','','VIL_House_T2_02'},
  ['VIL_House_T2_02__Window_Warm']={-96.5,26.1,569.5,13.8,3.3,12.3,3,false,'Window_Warm','','VIL_House_T2_02'},
  ['VIL_House_T2_02__Wood_Dark']={-96.5,29.75,569.5,19.102,13.3,17.602,3,true,'Wood_Dark','','VIL_House_T2_02'},
  ['VIL_House_T2_03__Plaster_Cream']={126.0,26.1,556.0,13.0,7.8,12.0,3,false,'Plaster_Cream','','VIL_House_T2_03'},
  ['VIL_House_T2_03__Roof_Terracotta']={126.0,31.705,556.0,17.609,7.71,16.609,3,true,'Roof_Terracotta','','VIL_House_T2_03'},
  ['VIL_House_T2_03__Stone_Wall_Dark']={126.0,22.3,556.0,13.9,1.8,12.9,3,false,'Stone_Wall_Dark','','VIL_House_T2_03'},
  ['VIL_House_T2_03__Window_Warm']={126.0,26.1,556.0,13.3,3.3,12.3,3,false,'Window_Warm','','VIL_House_T2_03'},
  ['VIL_House_T2_03__Wood_Dark']={126.0,29.75,556.0,18.602,13.3,17.602,3,true,'Wood_Dark','','VIL_House_T2_03'},
  ['VIL_House_Upper_01__Plaster_Cream']={64.0,75.08,622.5,9.0,6.4,8.0,3,false,'Plaster_Cream','','VIL_House_Upper_01'},
  ['VIL_House_Upper_01__Roof_Terracotta']={64.0,80.135,622.5,12.2,3.81,11.2,3,false,'Roof_Terracotta','','VIL_House_Upper_01'},
  ['VIL_House_Upper_01__Wood_Dark']={64.0,76.98,622.5,13.802,11.8,12.802,3,true,'Wood_Dark','','VIL_House_Upper_01'},
  ['VIL_House_Upper_02__Plaster_HouPeach']={51.5,74.88,628.5,8.0,6.0,7.5,3,false,'Plaster_HouPeach','','VIL_House_Upper_02'},
  ['VIL_House_Upper_02__Roof_Terracotta']={51.5,79.735,628.5,11.2,3.81,10.7,3,false,'Roof_Terracotta','','VIL_House_Upper_02'},
  ['VIL_House_Upper_02__Wood_Dark']={51.5,76.78,628.5,12.802,11.4,12.302,3,true,'Wood_Dark','','VIL_House_Upper_02'},
  ['VIL_House_Upper_03__Plaster_Cream']={-55.0,77.33,625.0,8.0,10.9,8.0,3,false,'Plaster_Cream','','VIL_House_Upper_03'},
  ['VIL_House_Upper_03__Roof_Terracotta']={-55.0,81.16,625.0,11.0,10.26,11.0,3,false,'Roof_Terracotta','','VIL_House_Upper_03'},
  ['VIL_House_Upper_03__Wood_Dark']={-55.0,80.485,625.0,12.357,18.81,12.357,3,true,'Wood_Dark','','VIL_House_Upper_03'},
  ['VIL_MainHall__Cloth_Canvas']={-0.0,29.375,583.414,36.574,11.29,28.777,3,true,'Cloth_Canvas','','VIL_MainHall'},
  ['VIL_MainHall__Cloth_Red']={0.006,32.088,576.263,35.92,16.916,42.706,3,true,'Cloth_Red','','VIL_MainHall'},
  ['VIL_MainHall__Cloth_Royal_Blue']={-0.012,28.148,595.064,25.821,7.88,5.476,3,false,'Cloth_Royal_Blue','','VIL_MainHall'},
  ['VIL_MainHall__Emblem_Cream']={-0.063,39.355,575.819,9.43,31.21,24.279,3,false,'Emblem_Cream','','VIL_MainHall'},
  ['VIL_MainHall__Lantern_Glow']={-0.0,37.93,568.775,17.3,8.5,27.65,3,false,'Lantern_Glow','','VIL_MainHall'},
  ['VIL_MainHall__Metal_Gold']={-0.0,44.615,576.044,26.382,41.77,34.388,3,true,'Metal_Gold','','VIL_MainHall'},
  ['VIL_MainHall__Plaster_Cream']={-0.0,40.1,580.0,40.999,34.6,41.0,3,true,'Plaster_Cream','','VIL_MainHall'},
  ['VIL_MainHall__Roof_Terracotta']={-0.0,47.75,580.0,52.0,23.1,52.097,3,true,'Roof_Terracotta','','VIL_MainHall'},
  ['VIL_MainHall__Stone_Wall_Dark']={-0.0,24.235,579.628,43.999,5.87,44.745,3,true,'Stone_Wall_Dark','','VIL_MainHall'},
  ['VIL_MainHall__Stone_Wall_Light']={-0.0,38.55,579.753,44.412,33.5,44.906,3,true,'Stone_Wall_Light','','VIL_MainHall'},
  ['VIL_MainHall__Window_Warm']={-0.0,36.925,580.958,41.34,17.45,39.368,3,false,'Window_Warm','','VIL_MainHall'},
  ['VIL_MainHall__Wood_Dark_B']={-0.0,38.835,580.0,52.0,31.23,52.0,3,true,'Wood_Dark_B','','VIL_MainHall'},
  ['VIL_MainHall__Wood_Lacquer_Red']={-0.0,40.3,580.36,42.429,34.0,42.42,3,true,'Wood_Lacquer_Red','','VIL_MainHall'},
  ['VIL_MainHall__Wood_Light']={0.718,25.186,576.235,36.953,3.558,24.73,3,true,'Wood_Light','','VIL_MainHall'},
  ['VIL_MainHall__Wood_Plank']={-0.062,27.811,580.0,38.265,8.819,38.42,3,true,'Wood_Plank','','VIL_MainHall'},
  ['VIL_MainHall__Wood_VilLacquerDark']={-0.0,41.65,580.0,52.3,11.8,52.3,3,true,'Wood_VilLacquerDark','','VIL_MainHall'},
  ['VIL_Mill__Lantern_Glow']={-97.15,17.2,433.7,12.1,1.9,11.4,3,false,'Lantern_Glow','','VIL_Mill'},
  ['VIL_Mill__Metal_Dark']={-99.3,13.963,433.4,16.8,15.526,27.8,3,true,'Metal_Dark','','VIL_Mill'},
  ['VIL_Mill__Roof_Terracotta']={-100.0,21.938,430.075,19.001,19.716,26.851,3,true,'Roof_Terracotta','','VIL_Mill'},
  ['VIL_Mill__Stone_Wall_Dark']={-100.002,12.313,432.275,14.138,13.426,29.45,3,true,'Stone_Wall_Dark','','VIL_Mill'},
  ['VIL_Mill__Stone_Wall_Light']={-99.54,8.691,432.002,15.079,4.982,18.126,3,true,'Stone_Wall_Light','','VIL_Mill'},
  ['VIL_Mill__Window_Warm']={-101.0,17.3,432.0,12.3,4.5,18.3,3,false,'Window_Warm','','VIL_Mill'},
  ['VIL_Mill__Wood_Dark']={-100.0,19.328,432.0,20.001,26.616,30.9,3,true,'Wood_Dark','','VIL_Mill'},
  ['VIL_Mill__Wood_Plank']={-99.55,17.959,433.309,14.9,23.518,27.723,3,true,'Wood_Plank','','VIL_Mill'},
  ['VIL_Ramen__Cloth_VilLantern']={38.0,26.374,523.586,21.1,12.009,9.873,3,true,'Cloth_VilLantern','','VIL_Ramen'},
  ['VIL_Ramen__Cloth_VilNoren']={38.0,28.1,520.28,17.85,2.403,0.192,3,false,'Cloth_VilNoren','','VIL_Ramen'},
  ['VIL_Ramen__Emblem_Cream']={38.0,26.108,527.102,15.8,12.456,11.297,3,false,'Emblem_Cream','','VIL_Ramen'},
  ['VIL_Ramen__Lantern_Glow']={38.0,22.94,524.955,21.18,10.98,12.69,3,false,'Lantern_Glow','','VIL_Ramen'},
  ['VIL_Ramen__Metal_Dark']={38.218,26.575,531.95,14.36,13.85,2.2,3,false,'Metal_Dark','','VIL_Ramen'},
  ['VIL_Ramen__Plaster_Cream']={38.0,24.6,529.062,18.25,11.3,8.125,3,false,'Plaster_Cream','','VIL_Ramen'},
  ['VIL_Ramen__Roof_Green']={37.993,31.545,527.025,23.401,5.454,17.458,3,true,'Roof_Green','','VIL_Ramen'},
  ['VIL_Ramen__Stone_Wall_Dark']={38.0,17.95,527.0,19.1,3.4,13.1,3,false,'Stone_Wall_Dark','','VIL_Ramen'},
  ['VIL_Ramen__Stone_Wall_Light']={38.0,15.9,527.0,18.8,1.0,12.8,3,false,'Stone_Wall_Light','','VIL_Ramen'},
  ['VIL_Ramen__Window_Warm']={38.0,23.325,529.15,18.5,5.45,3.7,3,false,'Window_Warm','','VIL_Ramen'},
  ['VIL_Ramen__Wood_Dark_B']={38.0,25.712,527.0,23.312,18.724,17.312,3,true,'Wood_Dark_B','','VIL_Ramen'},
  ['VIL_Ramen__Wood_Lacquer_Red']={38.0,26.189,525.054,13.87,15.118,6.892,3,true,'Wood_Lacquer_Red','','VIL_Ramen'},
  ['VIL_Ramen__Wood_Light']={38.0,25.173,527.004,17.526,17.287,11.536,3,true,'Wood_Light','','VIL_Ramen'},
  ['VIL_Ramen__Wood_Plank_B']={38.0,18.305,527.205,18.35,3.55,11.939,3,true,'Wood_Plank_B','','VIL_Ramen'},
  ['VIL_WaterTower__Metal_Dark']={-60.0,29.675,591.612,8.0,9.75,10.776,3,true,'Metal_Dark','','VIL_WaterTower'},
  ['VIL_WaterTower__Metal_Gold']={-59.004,44.225,583.516,2.992,14.05,19.968,3,false,'Metal_Gold','','VIL_WaterTower'},
  ['VIL_WaterTower__Plaster_Cream']={-58.0,35.8,574.0,24.4,26.4,24.4,3,true,'Plaster_Cream','','VIL_WaterTower'},
  ['VIL_WaterTower__Roof_Blue']={-58.0,41.625,577.75,31.8,13.55,39.3,3,true,'Roof_Blue','','VIL_WaterTower'},
  ['VIL_WaterTower__Roof_Blue_B']={-58.0,42.825,574.0,32.1,11.75,32.1,3,true,'Roof_Blue_B','','VIL_WaterTower'},
  ['VIL_WaterTower__Stone_Wall_Dark']={-58.0,22.7,578.375,27.2,2.8,35.95,3,true,'Stone_Wall_Dark','','VIL_WaterTower'},
  ['VIL_WaterTower__Stone_Wall_Light']={-58.0,22.6,574.0,27.71,1.6,27.46,3,true,'Stone_Wall_Light','','VIL_WaterTower'},
  ['VIL_WaterTower__Window_Warm']={-58.0,35.25,574.0,24.74,15.3,24.74,3,false,'Window_Warm','','VIL_WaterTower'},
  ['VIL_WaterTower__Wood_Dark_B']={-58.0,42.35,574.0,31.8,11.0,31.8,3,true,'Wood_Dark_B','','VIL_WaterTower'},
  ['VIL_WaterTower__Wood_Dark_C']={-58.0,32.722,577.384,31.062,21.045,37.831,3,true,'Wood_Dark_C','','VIL_WaterTower'},
  ['VIL_WaterTower__Wood_Lacquer_Red']={-58.0,33.4,574.0,25.355,21.2,25.355,3,true,'Wood_Lacquer_Red','','VIL_WaterTower'},
  ['VIL_WaterTower__Wood_Plank']={-60.0,32.295,593.0,7.722,6.191,7.722,3,true,'Wood_Plank','','VIL_WaterTower'},
  ['VIL_WeaponShop__Cloth_Royal_Blue']={58.0,34.669,572.555,8.7,14.358,23.11,3,false,'Cloth_Royal_Blue','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Lantern_Glow']={58.0,41.68,574.0,3.2,2.4,3.043,3,false,'Lantern_Glow','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Metal_Dark']={57.935,28.455,569.371,20.61,10.69,20.5,3,true,'Metal_Dark','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Metal_Gold']={62.059,37.727,578.951,11.238,27.047,10.838,3,true,'Metal_Gold','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Metal_VilSteel']={57.972,28.507,572.032,20.564,8.634,24.556,3,true,'Metal_VilSteel','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Plaster_Cream']={58.0,35.8,573.982,24.359,26.4,24.363,3,true,'Plaster_Cream','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Roof_Blue']={58.0,42.9,574.0,31.8,11.0,31.8,3,true,'Roof_Blue','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Roof_Blue_B']={58.0,42.825,574.0,32.1,11.75,32.1,3,true,'Roof_Blue_B','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Stone_Wall_Dark']={58.0,22.7,574.0,27.2,2.8,27.2,3,true,'Stone_Wall_Dark','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Stone_Wall_Light_B']={58.0,22.6,573.44,27.711,1.6,28.58,3,true,'Stone_Wall_Light_B','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Window_Warm']={58.0,35.25,575.287,24.622,15.3,22.048,3,false,'Window_Warm','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Wood_Dark']={58.0,33.71,574.0,31.062,22.18,31.062,3,true,'Wood_Dark','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Wood_Dark_B']={58.0,42.35,574.0,31.8,11.0,31.8,3,true,'Wood_Dark_B','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Wood_Lacquer_Red']={58.0,33.4,574.29,26.2,21.2,25.62,3,true,'Wood_Lacquer_Red','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Wood_Light']={60.689,24.663,574.0,15.378,3.715,13.18,3,false,'Wood_Light','','VIL_WeaponShop'},
  ['VIL_WeaponShop__Wood_Plank_B']={58.0,29.075,571.885,21.971,12.55,26.25,3,true,'Wood_Plank_B','','VIL_WeaponShop'},
  ['SUM_Banners__Cloth_Royal_Blue']={132.816,38.4,455.897,17.434,14.2,24.791,4,true,'Cloth_Royal_Blue','',''},
  ['SUM_Banners__Wood_Dark']={132.267,46.0,455.559,18.911,0.6,26.714,4,true,'Wood_Dark','',''},
  ['SUM_Constellation__Crystal_SumStar_Glow']={136.479,66.2,457.906,54.737,14.257,30.29,4,false,'Crystal_SumStar_Glow','',''},
  ['SUM_Constellation__Summon_Blue_Glow']={136.149,66.2,457.787,59.131,19.6,32.403,4,false,'Summon_Blue_Glow','',''},
  ['SUM_Crystals__Crystal_Blue']={128.337,25.782,452.715,17.898,11.485,22.465,4,false,'Crystal_Blue','',''},
  ['SUM_Plaza_Floor__Metal_Gold']={119.998,16.55,441.811,52.092,0.9,51.679,4,true,'Metal_Gold','',''},
  ['SUM_Plaza_Floor__Stone_Paving_Warm']={120.0,16.35,441.984,55.858,0.3,55.826,4,false,'Stone_Paving_Warm','',''},
  ['SUM_Plaza_Floor__Stone_Paving_Warm_C']={119.656,16.35,441.841,53.818,0.3,55.556,4,false,'Stone_Paving_Warm_C','',''},
  ['SUM_Plaza_Floor__Stone_SumFloor_Pale']={119.865,16.35,441.92,46.127,0.3,46.236,4,true,'Stone_SumFloor_Pale','',''},
  ['SUM_Plaza_Floor__Summon_Floor']={119.998,16.35,441.913,50.492,0.3,50.322,4,true,'Summon_Floor','',''},
  ['SUM_Plaza_Floor__Summon_Stone_Dark']={120.471,16.125,442.0,55.558,0.45,56.466,4,true,'Summon_Stone_Dark','',''},
  ['SUM_Plaza_Rail__Lantern_Glow']={119.639,21.185,440.516,53.958,2.081,51.298,4,false,'Lantern_Glow','',''},
  ['SUM_Plaza_Rail__Metal_Gold']={119.752,21.029,441.592,54.883,3.878,53.981,4,true,'Metal_Gold','',''},
  ['SUM_Plaza_Rail__Stone_Wall_Light']={119.865,18.573,441.729,55.541,4.245,54.763,4,true,'Stone_Wall_Light','',''},
  ['SUM_Plaza_Rail__Stone_Wall_Light_C']={118.852,18.573,440.54,53.515,4.245,52.385,4,true,'Stone_Wall_Light_C','',''},
  ['SUM_Sphere_Frame__Metal_Gold']={135.457,64.495,457.721,18.935,23.61,18.935,4,true,'Metal_Gold','',''},
  ['SUM_Sphere_Frame__Summon_Blue_Glow']={135.457,73.5,457.721,1.18,1.4,1.262,4,false,'Summon_Blue_Glow','',''},
  ['SUM_Tower_Glow__Crystal_SumPortal_Glow']={135.727,33.525,457.721,11.273,26.75,13.779,4,false,'Crystal_SumPortal_Glow','','SUM_Tower'},
  ['SUM_Tower_Glow__Crystal_SumStar_Glow']={135.797,34.333,457.721,11.24,21.834,13.95,4,false,'Crystal_SumStar_Glow','','SUM_Tower'},
  ['SUM_Tower_Glow__Lantern_Glow']={134.474,32.568,457.032,35.189,24.685,40.297,4,false,'Lantern_Glow','','SUM_Tower'},
  ['SUM_Tower_Glow__Summon_Blue_Glow']={130.524,33.675,453.619,21.884,34.95,17.077,4,false,'Summon_Blue_Glow','','SUM_Tower'},
  ['SUM_Tower_Gold__Metal_Gold']={134.474,36.52,457.032,40.809,39.54,45.819,4,true,'Metal_Gold','','SUM_Tower'},
  ['SUM_Tower_Stone__Stone_SumBlock']={134.474,34.93,457.032,38.671,36.06,43.779,4,true,'Stone_SumBlock','','SUM_Tower'},
  ['SUM_Tower_Stone__Summon_Stone']={134.474,34.604,457.032,38.253,37.712,43.361,4,true,'Summon_Stone','','SUM_Tower'},
  ['SUM_Tower_Stone__Summon_Stone_Dark']={134.506,34.15,457.063,40.442,36.9,45.456,4,true,'Summon_Stone_Dark','','SUM_Tower'},
  ['WATER_BackFalls__Cliff_Rock_Tan_Dark']={-0.213,48.14,611.209,179.92,52.845,19.557,5,true,'Cliff_Rock_Tan_Dark','',''},
  ['WATER_BackFalls__Foam_g15_11']={-80.127,47.109,606.588,17.781,51.244,15.237,5,false,'Foam','',''},
  ['WATER_BackFalls__Foam_g16_11']={55.04,47.048,606.23,65.127,51.364,17.465,5,false,'Foam','',''},
  ['WATER_BackFalls__Stone_Wall_Light']={0.663,22.497,595.063,176.995,1.794,16.222,5,true,'Stone_Wall_Light','',''},
  ['WATER_BackFalls__Stone_Wall_Light_B']={8.027,22.485,594.926,162.469,1.797,14.708,5,true,'Stone_Wall_Light_B','',''},
  ['WATER_BackFalls__Water']={-0.0,47.12,603.375,177.9,50.16,31.05,5,false,'Water','',''},
  ['WATER_BackFalls__Water_WtrFall']={0.091,45.835,602.818,167.659,47.229,13.118,5,false,'Water_WtrFall','',''},
  ['WATER_BackFalls__Water_WtrSheet']={-0.0,47.495,609.593,175.4,50.289,4.586,5,false,'Water_WtrSheet','',''},
  ['WATER_Canal_East__Cliff_Rock_Tan_Dark']={-115.337,4.499,422.77,14.253,1.57,137.435,5,true,'Cliff_Rock_Tan_Dark','',''},
  ['WATER_Canal_East__Foam']={-108.627,8.653,423.186,24.998,8.892,157.429,5,false,'Foam','',''},
  ['WATER_Canal_East__Stone_Wall_Light']={-105.092,13.024,509.89,36.457,19.648,184.275,5,true,'Stone_Wall_Light','',''},
  ['WATER_Canal_East__Stone_Wall_Light_B']={-107.255,13.5,513.863,32.214,20.6,173.743,5,true,'Stone_Wall_Light_B','',''},
  ['WATER_Canal_East__Water']={-103.673,13.3,476.597,38.153,18.2,249.094,5,false,'Water','',''},
  ['WATER_Canal_East__Water_WtrFall']={-104.073,13.47,472.663,32.916,18.1,253.022,5,false,'Water_WtrFall','',''},
  ['WATER_Canal_West__Foam']={140.53,19.392,544.228,4.791,6.345,5.603,5,false,'Foam','',''},
  ['WATER_Canal_West__Stone_Wall_Light']={122.838,19.494,543.099,68.979,7.811,113.534,5,true,'Stone_Wall_Light','',''},
  ['WATER_Canal_West__Stone_Wall_Light_B']={128.092,19.484,541.146,60.49,7.831,110.567,5,true,'Stone_Wall_Light_B','',''},
  ['WATER_Canal_West__Water']={122.809,19.2,543.14,70.182,6.4,111.479,5,false,'Water','',''},
  ['WATER_Canal_West__Water_WtrFall']={132.961,19.37,542.686,47.028,6.3,96.847,5,false,'Water_WtrFall','',''},
  ['WATER_SeaFalls__Foam_g15_11']={-126.46,-44.619,577.283,27.37,133.697,29.547,5,false,'Foam','',''},
  ['WATER_SeaFalls__Foam_g15_13']={-111.442,-53.792,337.928,28.882,116.746,28.8,5,false,'Foam','',''},
  ['WATER_SeaFalls__Foam_g16_13']={98.704,-57.073,339.468,23.987,108.206,24.06,5,false,'Foam','',''},
  ['WATER_SeaFalls__Foam_g17_12']={170.079,-47.878,497.807,29.102,128.317,28.554,5,false,'Foam','',''},
  ['WATER_SeaFalls__Stone_Wall_Dark']={88.706,-4.15,348.154,13.777,19.7,15.236,5,true,'Stone_Wall_Dark','',''},
  ['WATER_SeaFalls__Stone_WtrVoid']={90.204,-0.25,346.906,6.261,7.0,7.401,5,false,'Stone_WtrVoid','',''},
  ['WATER_SeaFalls__Water']={19.908,9.25,457.864,283.377,26.299,237.81,5,false,'Water','',''},
  ['WATER_SeaFalls__Water_WtrFall']={20.963,-45.985,458.198,296.621,126.463,246.765,5,false,'Water_WtrFall','',''},
  ['WATER_SeaFalls__Water_WtrSheet']={20.779,-43.871,459.751,295.691,132.058,256.716,5,false,'Water_WtrSheet','',''},
  ['WATER_Valley_Timber__Lantern_Glow']={-113.416,11.065,380.288,21.811,1.0,10.863,5,false,'Lantern_Glow','',''},
  ['WATER_Valley_Timber__Metal_Dark']={-118.0,15.2,432.0,17.2,2.1,1.96,5,false,'Metal_Dark','',''},
  ['WATER_Valley_Timber__Stone_Wall_Light_B']={-113.99,9.605,404.136,26.621,9.01,60.128,5,true,'Stone_Wall_Light_B','',''},
  ['WATER_Valley_Timber__Wood_Dark']={-114.765,10.441,405.528,24.67,11.318,61.866,5,true,'Wood_Dark','',''},
  ['WATER_Valley_Timber__Wood_Dark_B']={-114.162,10.532,405.369,23.826,8.836,57.461,5,true,'Wood_Dark_B','',''},
  ['WATER_Valley_Timber__Wood_Plank']={-113.42,7.238,380.284,21.738,2.731,9.584,5,true,'Wood_Plank','',''},
  ['EXIT_AnchorGuard__Metal_Dark']={-192.096,18.662,612.096,13.895,2.842,13.894,6,false,'Metal_Dark','','EXIT_AnchorGuard'},
  ['EXIT_AnchorGuard__Metal_Gold']={-192.096,19.05,612.096,14.354,2.6,14.354,6,false,'Metal_Gold','','EXIT_AnchorGuard'},
  ['EXIT_Bridge__Stone_Paving_Warm']={-129.834,2.817,550.791,78.988,27.035,74.954,6,false,'Stone_Paving_Warm','',''},
  ['EXIT_Bridge__Stone_Paving_Warm_B']={-131.186,2.817,549.833,73.873,27.034,78.988,6,false,'Stone_Paving_Warm_B','',''},
  ['EXIT_Bridge__Stone_Wall_Dark']={-130.473,2.075,550.473,80.684,28.15,80.684,6,true,'Stone_Wall_Dark','',''},
  ['EXIT_Bridge__Stone_Wall_Light_B']={-132.593,2.35,552.593,77.428,27.1,77.428,6,true,'Stone_Wall_Light_B','',''},
  ['EXIT_Islet__Stone_Paving_Warm']={-178.816,13.632,599.37,48.324,5.414,47.309,6,false,'Stone_Paving_Warm','',''},
  ['EXIT_Islet__Stone_Paving_Warm_B']={-175.161,13.631,598.852,38.891,5.412,48.395,6,false,'Stone_Paving_Warm_B','',''},
  ['EXIT_Islet__Stone_Wall_Dark']={-177.918,13.35,597.918,51.972,6.3,51.972,6,false,'Stone_Wall_Dark','',''},
  ['EXIT_Islet__Stone_Wall_Light_B']={-178.343,8.55,598.343,52.255,14.7,52.255,6,false,'Stone_Wall_Light_B','',''},
  ['EXIT_Islet_Walls__Lantern_Glow']={-190.858,25.3,610.858,18.102,2.2,18.102,6,false,'Lantern_Glow','',''},
  ['EXIT_Islet_Walls__Stone_Wall_Dark']={-178.024,22.375,598.024,50.912,12.35,50.912,6,false,'Stone_Wall_Dark','',''},
  ['EXIT_Islet_Walls__Stone_Wall_Light']={-178.024,21.448,598.024,50.487,9.905,50.487,6,false,'Stone_Wall_Light','',''},
  ['EXIT_Rails__Lantern_Glow']={-131.865,21.895,551.865,76.762,3.49,76.762,6,false,'Lantern_Glow','',''},
  ['EXIT_Rails__Stone_Wall_Dark']={-131.527,20.824,551.527,78.429,9.248,78.429,6,true,'Stone_Wall_Dark','',''},
  ['EXIT_Rails__Stone_Wall_Light']={-131.71,19.77,551.71,77.496,7.74,77.496,6,true,'Stone_Wall_Light','',''},
  ['EXIT_Rails__Wood_Dark']={-133.07,18.0,553.07,68.356,2.6,68.356,6,true,'Wood_Dark','',''},
  ['EXIT_Rails__Wood_Plank']={-132.805,18.47,552.805,72.945,1.78,72.945,6,true,'Wood_Plank','',''},
  ['EXIT_Rock__Cliff_Rock_Tan']={-159.256,-32.75,580.229,85.553,94.5,87.917,6,false,'Cliff_Rock_Tan','',''},
  ['EXIT_Rock__Cliff_Rock_Tan_Dark']={-159.836,-21.697,576.766,84.565,71.296,78.151,6,false,'Cliff_Rock_Tan_Dark','',''},
  ['EXIT_Rock__Grass_Konoha']={-175.136,13.462,596.703,56.45,3.876,57.639,6,false,'Grass_Konoha','',''},
  ['EXIT_Trail__DB_Energy_Glow']={-67.157,20.92,490.054,46.117,7.24,19.076,6,false,'DB_Energy_Glow','',''},
  ['EXIT_Trail__Lantern_Glow']={-67.161,18.15,490.054,46.84,7.6,19.846,6,false,'Lantern_Glow','',''},
  ['EXIT_Trail__Metal_Gold']={-67.161,18.54,490.054,47.122,9.88,20.127,6,true,'Metal_Gold','',''},
  ['EXIT_Trail__Stone_Wall_Dark']={-67.164,16.67,490.054,48.495,12.94,21.495,6,true,'Stone_Wall_Dark','',''},
  ['EXIT_Trail__Stone_Wall_Light']={-67.162,16.375,490.054,47.474,11.15,20.478,6,true,'Stone_Wall_Light','',''},
  ['GATE_DB_Barrier__DB_Energy_Glow']={-172.368,24.7,592.368,11.667,17.0,11.667,7,false,'DB_Energy_Glow','','GATE_DB'},
  ['GATE_DB_Barrier__Energy_Core_DB_Glow']={-172.353,25.247,592.368,10.185,13.266,10.155,7,false,'Energy_Core_DB_Glow','','GATE_DB'},
  ['GATE_DB_Court__Crystal_DBGate_Orb']={-168.529,21.48,588.529,27.047,2.493,27.047,7,false,'Crystal_DBGate_Orb','','GATE_DB'},
  ['GATE_DB_Court__Crystal_DBGate_Star']={-168.047,21.671,587.802,26.165,2.229,25.711,7,false,'Crystal_DBGate_Star','','GATE_DB'},
  ['GATE_DB_Court__Lantern_Glow']={-172.368,20.4,592.367,38.608,1.55,38.608,7,false,'Lantern_Glow','','GATE_DB'},
  ['GATE_DB_Court__Metal_Gold']={-172.368,21.1,592.367,40.229,3.5,40.229,7,false,'Metal_Gold','','GATE_DB'},
  ['GATE_DB_Court__Roof_DBGate_Ridge']={-172.368,23.332,592.368,40.27,3.873,40.27,7,false,'Roof_DBGate_Ridge','','GATE_DB'},
  ['GATE_DB_Court__Stone_Wall_Dark']={-172.368,20.99,592.367,39.598,9.59,39.598,7,false,'Stone_Wall_Dark','','GATE_DB'},
  ['GATE_DB_Court__Stone_Wall_Light']={-172.368,21.706,592.368,39.145,9.912,39.145,7,false,'Stone_Wall_Light','','GATE_DB'},
  ['GATE_DB_Court__Wood_Lacquer_Red']={-172.368,20.264,592.367,40.328,7.828,40.328,7,false,'Wood_Lacquer_Red','','GATE_DB'},
  ['GATE_DB_Frame__Crystal_DBGate_Orb']={-172.368,40.1,592.368,8.047,6.1,8.047,7,false,'Crystal_DBGate_Orb','','GATE_DB'},
  ['GATE_DB_Frame__Crystal_DBGate_Star']={-172.368,40.148,592.367,6.89,2.812,6.89,7,false,'Crystal_DBGate_Star','','GATE_DB'},
  ['GATE_DB_Frame__Metal_Gold']={-172.368,34.7,592.367,42.226,36.5,42.226,7,false,'Metal_Gold','','GATE_DB'},
  ['GATE_DB_Frame__Roof_DBGate_Ridge']={-172.368,44.339,592.367,39.606,5.218,39.606,7,false,'Roof_DBGate_Ridge','','GATE_DB'},
  ['GATE_DB_Frame__Roof_DBGate_Tile']={-172.368,44.031,592.367,38.608,4.262,38.608,7,false,'Roof_DBGate_Tile','','GATE_DB'},
  ['GATE_DB_Frame__Stone_Paving_Warm']={-172.367,25.2,592.368,14.142,18.2,14.142,7,false,'Stone_Paving_Warm','','GATE_DB'},
  ['GATE_DB_Frame__Stone_Wall_Dark']={-172.368,17.945,592.368,23.052,3.5,23.052,7,false,'Stone_Wall_Dark','','GATE_DB'},
  ['GATE_DB_Frame__Stone_Wall_Light_B']={-172.368,25.9,592.367,22.309,19.4,22.309,7,false,'Stone_Wall_Light_B','','GATE_DB'},
  ['GATE_DB_Frame__Wood_Lacquer_Red']={-172.368,33.975,592.367,28.058,26.95,28.058,7,false,'Wood_Lacquer_Red','','GATE_DB'},
  ['GATE_DB_Lock__Energy_Core_DB_Glow']={-172.368,24.48,592.368,3.606,3.4,3.606,7,false,'Energy_Core_DB_Glow','','GATE_DB'},
  ['GATE_DB_Lock__Metal_Dark']={-172.368,24.28,592.367,2.192,1.0,2.192,7,false,'Metal_Dark','','GATE_DB'},
  ['GATE_DB_Lock__Metal_Gold']={-172.368,25.443,592.368,3.889,4.625,3.889,7,false,'Metal_Gold','','GATE_DB'},
  ['GATE_DB_OpenGlow__Metal_DBGate_Glow']={-172.367,25.2,592.368,13.958,17.2,13.958,7,false,'Metal_DBGate_Glow','','GATE_DB'},
  ['PROP_Street_Lamps__Cloth_Red']={12.721,25.924,507.057,168.889,6.489,116.192,8,true,'Cloth_Red','',''},
  ['PROP_Street_Lamps__Lantern_Glow']={12.721,25.924,507.057,168.859,7.749,116.162,8,false,'Lantern_Glow','',''},
  ['PROP_Street_Lamps__Metal_Dark']={12.721,27.174,507.057,167.829,6.749,115.132,8,true,'Metal_Dark','',''},
  ['PROP_Street_Lamps__Roof_Terracotta']={13.066,28.174,508.004,171.625,6.499,117.766,8,true,'Roof_Terracotta','',''},
  ['PROP_Street_Lamps__Wood_Dark']={12.98,23.562,507.84,170.727,14.724,117.548,8,true,'Wood_Dark','',''},
  ['PROP_Street_Lamps__Wood_Dark_B']={12.963,23.674,507.702,171.322,14.949,117.272,8,true,'Wood_Dark_B','',''},
  ['PROP_Training_Yard__Dirt_Pit']={58.0,6.32,351.0,15.0,0.3,11.0,8,false,'Dirt_Pit','',''},
  ['PROP_Training_Yard__Metal_Iron']={48.5,8.1,348.025,1.212,1.212,2.37,8,false,'Metal_Iron','',''},
  ['PROP_Training_Yard__Rope']={58.0,8.65,354.0,13.64,2.15,3.64,8,false,'Rope','',''},
  ['PROP_Training_Yard__Wood_Dark_B']={57.013,8.387,351.0,17.425,4.375,11.45,8,true,'Wood_Dark_B','',''},
  ['PROP_Training_Yard__Wood_Plank']={58.0,8.9,351.0,15.3,5.4,11.3,8,false,'Wood_Plank','',''},
  ['PROP_Village_Misc__Metal_Dark']={-1.325,15.25,505.25,210.258,17.7,124.508,8,true,'Metal_Dark','',''},
  ['PROP_Village_Misc__Wood_Plank_B']={-1.325,10.15,510.422,210.23,28.3,134.823,8,true,'Wood_Plank_B','',''},
  ['VEG_Borda_L__Bark_Dark']={-131.921,10.224,472.798,19.508,9.316,100.995,9,true,'Bark_Dark','',''},
  ['VEG_Borda_L__Leaf_Broad']={-132.205,17.127,472.72,24.289,7.592,106.155,9,false,'Leaf_Broad','',''},
  ['VEG_Borda_L__Leaf_Shadow']={-132.209,14.137,472.523,23.144,2.285,104.295,9,false,'Leaf_Shadow','',''},
  ['VEG_Borda_O__Bark_Dark']={135.551,20.277,437.807,41.237,9.451,111.948,9,true,'Bark_Dark','',''},
  ['VEG_Borda_O__Leaf_Broad']={135.53,27.315,437.808,46.35,7.847,116.706,9,false,'Leaf_Broad','',''},
  ['VEG_Borda_O__Leaf_Shadow']={135.684,24.246,437.74,45.102,2.432,115.511,9,false,'Leaf_Shadow','',''},
  ['VEG_Borda_S__Bark_Dark']={-0.479,10.232,337.919,158.098,9.345,13.437,9,true,'Bark_Dark','',''},
  ['VEG_Borda_S__Leaf_Broad']={-1.052,17.123,337.738,162.861,7.619,19.442,9,false,'Leaf_Broad','',''},
  ['VEG_Borda_S__Leaf_Shadow']={-0.668,14.132,337.836,162.0,2.355,17.198,9,false,'Leaf_Shadow','',''},
  ['VEG_Bushes__Leaf_Broad']={20.858,11.006,436.253,244.824,31.188,230.785,9,false,'Leaf_Broad','',''},
  ['VEG_Bushes__Leaf_Pine']={18.136,11.099,436.976,240.184,31.445,231.561,9,false,'Leaf_Pine','',''},
  ['VEG_Entrada__Bark_Dark']={0.429,11.308,322.582,117.208,11.611,20.609,9,true,'Bark_Dark','',''},
  ['VEG_Entrada__Leaf_Broad']={-0.012,19.39,322.718,123.099,11.834,26.502,9,false,'Leaf_Broad','',''},
  ['VEG_Entrada__Leaf_Pine']={-40.041,16.63,319.835,9.321,8.073,9.983,9,false,'Leaf_Pine','',''},
  ['VEG_Entrada__Leaf_Shadow']={0.125,15.584,323.145,122.333,5.981,24.66,9,false,'Leaf_Shadow','',''},
  ['VEG_Flowers__Flower_White']={55.031,15.044,437.763,160.312,17.001,238.419,9,false,'Flower_White','',''},
  ['VEG_Flowers__Leaf_Broad']={55.171,14.794,438.053,161.403,18.188,239.927,9,false,'Leaf_Broad','',''},
  ['VEG_Flowers__Sakura_Pink']={64.721,20.145,490.871,85.083,7.139,131.749,9,true,'Sakura_Pink','',''},
  ['VEG_Leste__Bark_Dark']={-135.333,12.354,457.724,20.898,13.737,98.872,9,true,'Bark_Dark','',''},
  ['VEG_Leste__Leaf_Broad']={-134.791,20.273,458.045,25.01,14.028,103.53,9,false,'Leaf_Broad','',''},
  ['VEG_Leste__Leaf_Pine']={-144.558,19.235,442.267,9.203,13.344,9.439,9,false,'Leaf_Pine','',''},
  ['VEG_Leste__Leaf_Shadow']={-136.311,17.994,457.773,25.698,10.861,102.462,9,false,'Leaf_Shadow','',''},
  ['VEG_Plato__Bark_Dark']={0.79,51.42,612.533,190.845,59.706,18.793,9,true,'Bark_Dark','',''},
  ['VEG_Plato__Leaf_Broad']={1.307,58.656,612.683,196.588,59.302,24.511,9,false,'Leaf_Broad','',''},
  ['VEG_Plato__Leaf_Shadow']={1.1,55.232,612.755,195.208,53.018,22.454,9,false,'Leaf_Shadow','',''},
  ['VEG_SE__Bark_Dark']={-92.73,11.092,361.616,63.902,11.155,55.25,9,true,'Bark_Dark','',''},
  ['VEG_SE__Leaf_Broad']={-92.109,18.924,361.413,69.664,11.209,62.347,9,false,'Leaf_Broad','',''},
  ['VEG_SE__Leaf_Shadow']={-92.475,15.1,361.652,67.644,4.271,59.567,9,false,'Leaf_Shadow','',''},
  ['VEG_SO__Bark_Dark']={102.6,15.185,377.104,44.735,19.368,53.633,9,true,'Bark_Dark','',''},
  ['VEG_SO__Leaf_Broad']={103.111,22.146,377.396,49.812,17.038,58.242,9,false,'Leaf_Broad','',''},
  ['VEG_SO__Leaf_Pine']={102.695,20.964,372.819,42.318,16.698,52.304,9,false,'Leaf_Pine','',''},
  ['VEG_SO__Leaf_Shadow']={102.566,20.398,376.304,48.488,15.565,59.274,9,false,'Leaf_Shadow','',''},
  ['VEG_Shelf__Bark_Dark']={9.92,-17.002,418.982,333.946,46.578,250.905,9,true,'Bark_Dark','',''},
  ['VEG_Shelf__Leaf_Broad']={10.034,-12.139,418.787,337.956,46.086,254.654,9,false,'Leaf_Broad','',''},
  ['VEG_Shelf__Leaf_Pine']={11.222,-8.324,415.07,320.123,15.32,209.74,9,false,'Leaf_Pine','',''},
  ['VEG_Shelf__Leaf_Shadow']={9.798,-14.356,419.018,336.54,42.007,253.776,9,false,'Leaf_Shadow','',''},
  ['VEG_Summon__Bark_Dark']={122.2,21.033,412.202,44.518,11.142,16.417,9,true,'Bark_Dark','',''},
  ['VEG_Summon__Sakura_Pink']={122.215,26.505,411.937,50.37,7.174,22.078,9,true,'Sakura_Pink','',''},
  ['VEG_T1_N__Bark_Dark']={0.165,20.226,519.497,132.561,9.332,12.925,9,true,'Bark_Dark','',''},
  ['VEG_T1_N__Leaf_Broad']={0.285,26.966,519.137,137.904,7.859,17.533,9,false,'Leaf_Broad','',''},
  ['VEG_T1_N__Leaf_Shadow']={-0.113,24.038,519.079,136.766,2.524,15.79,9,false,'Leaf_Shadow','',''},
  ['VEG_T1_NO__Bark_Dark']={117.452,22.624,519.558,67.367,14.198,25.785,9,true,'Bark_Dark','',''},
  ['VEG_T1_NO__Leaf_Broad']={104.053,27.699,516.54,44.254,9.25,22.698,9,false,'Leaf_Broad','',''},
  ['VEG_T1_NO__Leaf_Pine']={132.566,29.68,524.214,45.713,13.975,23.559,9,false,'Leaf_Pine','',''},
  ['VEG_T1_NO__Leaf_Pine_Light']={132.959,33.59,523.761,39.57,9.022,17.168,9,false,'Leaf_Pine_Light','',''},
  ['VEG_T1_NO__Leaf_Shadow']={118.968,28.407,520.644,72.91,11.428,30.7,9,false,'Leaf_Shadow','',''},
  ['VEG_T2__Bark_Dark']={15.254,27.661,580.04,195.514,12.288,47.542,9,true,'Bark_Dark','',''},
  ['VEG_T2__Leaf_Broad']={13.544,35.184,577.989,198.338,11.595,47.472,9,false,'Leaf_Broad','',''},
  ['VEG_T2__Leaf_Pine']={23.629,34.042,584.244,182.326,11.42,44.55,9,false,'Leaf_Pine','',''},
  ['VEG_T2__Leaf_Shadow']={15.004,33.011,580.586,199.577,9.357,51.864,9,false,'Leaf_Shadow','',''},
  ['VEG_T2__Sakura_Pink']={-33.695,32.208,592.714,15.328,5.591,13.568,9,true,'Sakura_Pink','',''},
  ['VFX_GATE_DB_Orb_1__Crystal_DBGate_Orb']={-159.922,31.8,600.57,3.1,3.1,3.1,10,false,'Crystal_DBGate_Orb','',''},
  ['VFX_GATE_DB_Orb_1__Crystal_DBGate_Star']={-158.913,31.861,599.561,0.934,1.165,0.934,10,false,'Crystal_DBGate_Star','',''},
  ['VFX_GATE_DB_Orb_2__Crystal_DBGate_Orb']={-159.074,27.8,598.024,3.1,3.1,3.1,10,false,'Crystal_DBGate_Orb','',''},
  ['VFX_GATE_DB_Orb_2__Crystal_DBGate_Star']={-158.337,27.861,597.287,1.713,1.165,1.713,10,false,'Crystal_DBGate_Star','',''},
  ['VFX_GATE_DB_Orb_3__Crystal_DBGate_Orb']={-178.307,28.2,579.074,3.1,3.1,3.1,10,false,'Crystal_DBGate_Orb','',''},
  ['VFX_GATE_DB_Orb_3__Crystal_DBGate_Star']={-177.556,28.133,578.322,1.678,2.057,1.678,10,false,'Crystal_DBGate_Star','',''},
  ['VFX_GATE_DB_Orb_4__Crystal_DBGate_Orb']={-180.782,32.2,579.852,3.1,3.1,3.1,10,false,'Crystal_DBGate_Orb','',''},
  ['VFX_GATE_DB_Orb_4__Crystal_DBGate_Star']={-180.14,32.234,579.21,1.885,2.456,1.885,10,false,'Crystal_DBGate_Star','',''},
  ['VFX_SUM_Ring_1__Metal_Gold']={135.457,62.2,457.721,23.284,7.267,23.558,10,true,'Metal_Gold','',''},
  ['VFX_SUM_Ring_1__Summon_Star_Glow']={135.457,62.278,457.729,22.835,7.818,22.342,10,false,'Summon_Star_Glow','',''},
  ['VFX_SUM_Ring_2__Metal_Gold']={135.457,62.2,457.721,2.207,17.32,17.314,10,true,'Metal_Gold','',''},
  ['VFX_SUM_Ring_2__Summon_Star_Glow']={135.523,62.2,457.744,2.598,13.023,12.973,10,false,'Summon_Star_Glow','',''},
  ['VFX_SUM_Ring_3__Metal_Gold']={135.457,62.2,457.721,15.35,13.37,8.766,10,true,'Metal_Gold','',''},
  ['VFX_SUM_Ring_3__Summon_Star_Glow']={135.477,62.18,457.73,12.068,10.223,7.935,10,false,'Summon_Star_Glow','',''},
  ['VFX_SUM_Star__Crystal_SumAmber_Glow']={135.457,62.83,457.721,7.938,11.94,10.8,10,false,'Crystal_SumAmber_Glow','',''},
  ['VFX_SUM_Star__Crystal_SumYellow_Glow']={135.457,62.83,457.721,7.938,11.94,10.8,10,false,'Crystal_SumYellow_Glow','',''},
  ['VFX_VIL_MillCamshaft__Wood_Dark']={-100.2,14.2,436.9,10.8,4.149,4.2,10,true,'Wood_Dark','',''},
  ['VFX_VIL_MillGear__Wood_Dark']={-105.675,14.2,432.0,2.75,6.92,6.92,10,false,'Wood_Dark','',''},
  ['VFX_VIL_MillStamps__Metal_Dark']={-99.0,13.913,438.225,5.8,10.025,1.95,10,false,'Metal_Dark','',''},
  ['VFX_VIL_MillStamps__Wood_Dark']={-99.0,14.6,438.5,5.1,8.2,0.7,10,false,'Wood_Dark','',''},
  ['VFX_WATER_Wheel__Metal_Dark']={-118.0,15.15,432.0,6.5,3.0,3.0,10,false,'Metal_Dark','',''},
  ['VFX_WATER_Wheel__Wood_Dark']={-117.0,15.15,431.996,20.0,22.0,21.992,10,true,'Wood_Dark','',''},
  ['VFX_WATER_Wheel__Wood_Plank_B']={-118.0,15.15,432.0,3.7,22.0,21.819,10,true,'Wood_Plank_B','',''},
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
  {'COL_EntBridge_001','Block',{0.0,4.7,262.75},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{24.0,82.5,3.0},false},
  {'COL_EntBridge_002','Block',{13.2,10.7,261.85},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.4,80.7,15.0},false},
  {'COL_EntBridge_003','Block',{-13.2,10.7,261.85},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.4,80.7,15.0},false},
  {'COL_EntGate_001','Block',{12.3,17.7,310.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.6,4.6,23.0},false},
  {'COL_EntGate_002','Block',{24.6,15.1,310.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.2,3.2,17.8},false},
  {'COL_EntGate_003','Block',{18.65,15.1,310.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.3,2.6,17.8},false},
  {'COL_EntGate_004','Block',{15.473,14.9,313.312},{0.995,0.0,0.105},{0.105,0.0,-0.995},{9.8,1.0,17.0},false},
  {'COL_EntGate_005','Block',{-12.3,17.7,310.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.6,4.6,23.0},false},
  {'COL_EntGate_006','Block',{-24.6,15.1,310.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.2,3.2,17.8},false},
  {'COL_EntGate_007','Block',{-18.65,15.1,310.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.3,2.6,17.8},false},
  {'COL_EntGate_008','Block',{-15.473,14.9,313.312},{-0.995,0.0,0.105},{0.105,0.0,0.995},{9.8,1.0,17.0},false},
  {'COL_EntLions_001','Block',{20.0,8.45,304.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.2,4.4,4.5},false},
  {'COL_EntLions_002','Block',{20.0,14.5,304.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.4,4.4,7.6},false},
  {'COL_EntLions_003','Block',{20.0,8.2,307.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,2.6,4.0},false},
  {'COL_EntLions_004','Block',{-20.0,8.45,304.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.2,4.4,4.5},false},
  {'COL_EntLions_005','Block',{-20.0,14.5,304.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.4,4.4,7.6},false},
  {'COL_EntLions_006','Block',{-20.0,8.2,307.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,2.6,4.0},false},
  {'COL_EntPlaza_001','Block',{14.4,9.5,316.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,2.6,6.6},false},
  {'COL_EntPlaza_002','Block',{14.4,9.5,326.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,2.6,6.6},false},
  {'COL_EntPlaza_003','Block',{-14.4,9.5,316.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,2.6,6.6},false},
  {'COL_EntPlaza_004','Block',{-14.4,9.5,326.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,2.6,6.6},false},
  {'COL_ExitAnchorGuard_001','Block',{-192.662,19.2,612.661},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{18.6,1.4,6.0},false},
  {'COL_ExitAnchor_001','Block',{-183.151,22.2,618.566},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{3.6,3.6,12.0},false},
  {'COL_ExitAnchor_002','Block',{-198.566,22.2,603.151},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{3.6,3.6,12.0},false},
  {'COL_ExitBridge_001','Block',{-131.709,14.7,551.709},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{18.0,92.0,3.0},false},
  {'COL_ExitBridge_002','Block',{-126.476,18.3,558.639},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.2,88.4,4.2},false},
  {'COL_ExitBridge_003','Block',{-138.639,18.3,546.476},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.2,88.4,4.2},false},
  {'COL_ExitBridge_004','Block',{-94.586,20.2,528.728},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{3.2,3.2,8.0},false},
  {'COL_ExitBridge_005','Block',{-108.728,20.2,514.586},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{3.2,3.2,8.0},false},
  {'COL_ExitIslet_001','Block',{-178.024,14.7,598.024},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{30.0,40.0,3.0},false},
  {'COL_ExitIslet_002','Block',{-172.368,14.7,592.368},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{43.0,20.0,3.0},false},
  {'COL_ExitIslet_003','Block',{-155.963,18.2,592.65},{-0.707,0.0,0.707},{0.707,0.0,0.707},{1.6,5.6,4.0},false},
  {'COL_ExitIslet_004','Block',{-176.186,18.2,616.551},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.6,15.6,4.0},false},
  {'COL_ExitIslet_005','Block',{-182.126,18.2,621.359},{0.707,0.0,-0.707},{-0.707,0.0,-0.707},{1.6,2.0,4.0},false},
  {'COL_ExitIslet_006','Block',{-172.65,18.2,575.963},{0.707,0.0,-0.707},{-0.707,0.0,-0.707},{1.6,5.6,4.0},false},
  {'COL_ExitIslet_007','Block',{-196.551,18.2,596.186},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.6,15.6,4.0},false},
  {'COL_ExitIslet_008','Block',{-201.359,18.2,602.126},{-0.707,0.0,0.707},{0.707,0.0,0.707},{1.6,2.0,4.0},false},
  {'COL_ExitTrail_001','Block',{-60.256,13.7,481.043},{-0.788,0.0,-0.616},{-0.616,0.0,0.788},{2.3,2.3,7.0},false},
  {'COL_ExitTrail_002','Block',{-44.653,13.7,493.234},{-0.788,0.0,-0.616},{-0.616,0.0,0.788},{2.3,2.3,7.0},false},
  {'COL_ExitTrail_003','Block',{-64.812,19.7,486.875},{-0.788,0.0,-0.616},{-0.616,0.0,0.788},{2.3,2.3,7.0},false},
  {'COL_ExitTrail_004','Block',{-49.209,19.7,499.065},{-0.788,0.0,-0.616},{-0.616,0.0,0.788},{2.3,2.3,7.0},false},
  {'COL_ExitTrail_005','Block',{-89.661,19.7,497.216},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.3,2.3,7.0},false},
  {'COL_ExitValley_001','Block',{-128.173,6.95,548.173},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{19.6,6.0,17.5},false},
  {'COL_ExitValley_002','Block',{-103.778,9.95,523.778},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{18.0,10.0,11.5},false},
  {'COL_ExitValley_003','Block',{-122.87,9.95,542.87},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{18.0,10.0,11.5},false},
  {'COL_GateDB_001','Block',{-164.377,29.4,600.358},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{4.8,4.8,26.4},false},
  {'COL_GateDB_002','Block',{-166.216,25.225,598.519},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.3,2.2,18.05},false},
  {'COL_GateDB_003','Block',{-180.358,29.4,584.377},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{4.8,4.8,26.4},false},
  {'COL_GateDB_004','Block',{-178.519,25.225,586.216},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.3,2.2,18.05},false},
  {'COL_GateDB_005','Block',{-172.368,16.6,592.368},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{5.2,1.2,0.8},false},
  {'COL_GateDB_006','Block',{-169.822,16.812,594.913},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,1.2,1.223},false},
  {'COL_GateDB_007','Block',{-168.408,17.306,596.327},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,1.2,2.212},false},
  {'COL_GateDB_008','Block',{-167.117,18.267,597.618},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.65,1.2,4.134},false},
  {'COL_GateDB_009','Block',{-174.913,16.812,589.822},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,1.2,1.223},false},
  {'COL_GateDB_010','Block',{-176.327,17.306,588.408},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,1.2,2.212},false},
  {'COL_GateDB_011','Block',{-177.618,18.267,587.117},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.65,1.2,4.134},false},
  {'COL_GateDB_012','Block',{-157.943,21.5,601.136},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{5.0,5.0,10.6},false},
  {'COL_GateDB_013','Block',{-181.136,21.5,577.943},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{5.0,5.0,10.6},false},
  {'COL_GateDB_014','Block',{-153.615,18.2,598.855},{-0.969,0.0,0.248},{0.248,0.0,0.969},{1.0,7.69,4.0},false},
  {'COL_GateDB_015','Block',{-157.531,18.2,607.205},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.0,14.026,4.0},false},
  {'COL_GateDB_016','Block',{-165.88,18.2,611.12},{0.248,0.0,-0.969},{-0.969,0.0,-0.248},{1.0,7.69,4.0},false},
  {'COL_GateDB_017','Block',{-153.983,19.4,595.196},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,2.0,6.4},false},
  {'COL_GateDB_018','Block',{-169.539,19.4,610.752},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,2.0,6.4},false},
  {'COL_GateDB_019','Block',{-178.855,18.2,573.615},{0.248,0.0,-0.969},{-0.969,0.0,-0.248},{1.0,7.69,4.0},false},
  {'COL_GateDB_020','Block',{-187.205,18.2,577.531},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{1.0,14.026,4.0},false},
  {'COL_GateDB_021','Block',{-191.12,18.2,585.88},{-0.969,0.0,0.248},{0.248,0.0,0.969},{1.0,7.69,4.0},false},
  {'COL_GateDB_022','Block',{-175.196,19.4,573.983},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,2.0,6.4},false},
  {'COL_GateDB_023','Block',{-190.752,19.4,589.539},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{2.0,2.0,6.4},false},
  {'COL_HousesEast_001','Block',{-136.0,9.85,456.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{13.9,12.9,8.3},false},
  {'COL_HousesEast_002','Block',{-136.0,16.805,452.0},{-1.0,0.0,-0.0},{-0.0,0.515,0.857},{9.0,9.335,0.7},false},
  {'COL_HousesEast_003','Block',{-136.0,16.805,460.0},{-1.0,-0.0,-0.0},{-0.0,-0.515,0.857},{9.0,9.335,0.7},false},
  {'COL_HousesEast_004','Block',{-134.0,6.675,394.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{15.8,13.8,2.95},false},
  {'COL_HousesEast_005','Block',{-134.0,11.7,394.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.6,12.6,7.8},false},
  {'COL_HousesEast_006','Block',{-134.0,18.405,390.0},{-1.0,0.0,-0.0},{-0.0,0.515,0.857},{10.0,9.335,0.7},false},
  {'COL_HousesEast_007','Block',{-134.0,18.405,398.0},{-1.0,-0.0,-0.0},{-0.0,-0.515,0.857},{10.0,9.335,0.7},false},
  {'COL_HousesMill_001','Block',{-95.4,25.468,432.0},{-0.865,0.502,-0.0},{-0.0,-0.0,1.0},{10.635,13.2,0.7},true},
  {'COL_HousesMill_002','Block',{-104.6,25.468,432.0},{-0.865,-0.502,-0.0},{-0.0,0.0,1.0},{10.635,13.2,0.7},true},
  {'COL_HousesMill_003','Block',{-100.0,13.9,423.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.0,1.2,16.6},true},
  {'COL_HousesMill_004','Block',{-100.0,13.9,440.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.0,1.2,16.6},true},
  {'COL_HousesMill_005','Block',{-106.4,13.9,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.2,15.6,16.6},true},
  {'COL_HousesMill_006','Block',{-93.6,13.9,425.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.2,2.8,16.6},true},
  {'COL_HousesMill_007','Block',{-93.6,13.9,438.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.2,2.8,16.6},true},
  {'COL_HousesMill_008','Block',{-93.6,20.45,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.2,10.0,3.5},true},
  {'COL_HousesMill_009','Block',{-93.3,6.15,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.8,10.0,0.7},false},
  {'COL_HousesMill_010','Block',{-100.0,6.15,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.6,15.6,0.7},false},
  {'COL_HousesMill_011','Block',{-100.0,21.8,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.6,15.6,0.8},true},
  {'COL_HousesMill_012','Block',{-94.2,9.2,418.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,6.6},true},
  {'COL_HousesMill_013','Block',{-100.0,9.2,418.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,6.6},true},
  {'COL_HousesMill_014','Block',{-105.8,9.2,418.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,6.6},true},
  {'COL_HousesMill_015','Block',{-96.75,8.0,420.8},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.9,2.6,4.2},false},
  {'COL_HousesMill_016','Block',{-103.7,7.3,420.65},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.0,2.3,2.8},false},
  {'COL_HousesMill_017','Block',{-99.4,11.5,444.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.0,5.0,11.2},true},
  {'COL_HousesMill_018','Block',{-104.0,7.75,445.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.6,3.8,3.7},false},
  {'COL_HousesMill_019','Block',{-101.0,8.25,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,6.4,3.5},false},
  {'COL_HousesMill_020','Block',{-105.3,8.6,427.1},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,5.0,4.2},false},
  {'COL_HousesMill_021','Block',{-99.0,13.95,438.35},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.4,2.9,14.9},true},
  {'COL_HousesMill_022','Block',{-104.65,7.5,438.35},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.3,2.9,2.0},false},
  {'COL_HousesMill_023','Block',{-100.5,8.5,436.8},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.6,0.6,4.0},false},
  {'COL_HousesT1_001','Block',{-35.5,19.85,527.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.9,12.9,8.3},false},
  {'COL_HousesT1_002','Block',{-31.75,26.805,527.0},{-0.842,0.54,-0.0},{-0.0,0.0,1.0},{8.91,8.5,0.7},false},
  {'COL_HousesT1_003','Block',{-39.25,26.805,527.0},{-0.842,-0.54,-0.0},{-0.0,-0.0,1.0},{8.91,8.5,0.7},false},
  {'COL_HousesT1_004','Block',{-43.725,18.775,527.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.45,9.3,6.15},false},
  {'COL_HousesT1_005','Block',{84.0,19.85,530.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.9,13.9,8.3},false},
  {'COL_HousesT1_006','Block',{84.0,26.805,525.75},{-1.0,-0.0,-0.0},{-0.0,0.492,0.87},{11.5,9.767,0.7},false},
  {'COL_HousesT1_007','Block',{84.0,26.805,534.25},{-1.0,0.0,-0.0},{-0.0,-0.492,0.87},{11.5,9.767,0.7},false},
  {'COL_HousesT1_008','Block',{-82.0,19.85,528.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.9,13.9,8.3},false},
  {'COL_HousesT1_009','Block',{-78.0,26.805,528.0},{-0.857,0.515,-0.0},{-0.0,-0.0,1.0},{9.335,9.0,0.7},false},
  {'COL_HousesT1_010','Block',{-86.0,26.805,528.0},{-0.857,-0.515,-0.0},{-0.0,0.0,1.0},{9.335,9.0,0.7},false},
  {'COL_HousesT1_011','Block',{-89.725,18.975,529.85},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.45,8.6,6.55},false},
  {'COL_HousesT1_012','Block',{112.0,19.85,504.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.9,12.9,8.3},false},
  {'COL_HousesT1_013','Block',{112.0,26.805,500.0},{-1.0,0.0,-0.0},{-0.0,0.515,0.857},{10.0,9.335,0.7},false},
  {'COL_HousesT1_014','Block',{112.0,26.805,508.0},{-1.0,-0.0,-0.0},{-0.0,-0.515,0.857},{10.0,9.335,0.7},false},
  {'COL_HousesT2_001','Block',{98.0,25.85,580.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.9,14.9,8.3},false},
  {'COL_HousesT2_002','Block',{98.0,32.805,575.5},{-1.0,-0.0,-0.0},{-0.0,0.471,0.882},{11.0,10.205,0.7},false},
  {'COL_HousesT2_003','Block',{98.0,32.805,584.5},{-1.0,0.0,-0.0},{-0.0,-0.471,0.882},{11.0,10.205,0.7},false},
  {'COL_HousesT2_004','Block',{98.0,33.9,580.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.6,5.6,8.6},false},
  {'COL_HousesT2_005','Block',{-96.5,25.85,569.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.4,12.9,8.3},false},
  {'COL_HousesT2_006','Block',{-96.5,32.805,565.5},{-1.0,0.0,-0.0},{-0.0,0.515,0.857},{9.5,9.335,0.7},false},
  {'COL_HousesT2_007','Block',{-96.5,32.805,573.5},{-1.0,-0.0,-0.0},{-0.0,-0.515,0.857},{9.5,9.335,0.7},false},
  {'COL_HousesT2_008','Block',{126.0,25.85,556.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{13.9,12.9,8.3},false},
  {'COL_HousesT2_009','Block',{126.0,32.805,552.0},{-1.0,0.0,-0.0},{-0.0,0.515,0.857},{9.0,9.335,0.7},false},
  {'COL_HousesT2_010','Block',{126.0,32.805,560.0},{-1.0,-0.0,-0.0},{-0.0,-0.515,0.857},{9.0,9.335,0.7},false},
  {'COL_HousesUpper_001','Block',{64.0,74.83,622.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,8.8,6.9},false},
  {'COL_HousesUpper_002','Block',{51.5,74.63,628.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{8.8,8.3,6.5},false},
  {'COL_HousesUpper_003','Block',{-55.0,74.23,625.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{8.8,8.8,5.7},false},
  {'COL_MiningCore_001','Block',{0.0,5.5,420.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.0,16.0,4.6},false},
  {'COL_MiningCore_002','Block',{0.0,5.5,420.0},{-0.707,0.0,0.707},{0.707,0.0,0.707},{16.0,16.0,4.6},false},
  {'COL_MiningCore_003','Block',{0.0,7.125,420.0},{-0.924,0.0,0.383},{0.383,0.0,0.924},{10.0,10.0,7.85},false},
  {'COL_MiningCore_004','Block',{0.0,7.125,420.0},{-0.383,0.0,0.924},{0.924,0.0,0.383},{10.0,10.0,7.85},false},
  {'COL_MiningDerrick_001','Block',{-32.139,8.95,458.302},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{6.6,6.6,11.5},false},
  {'COL_MiningDerrick_002','Block',{32.139,8.95,458.302},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.6,6.6,11.5},false},
  {'COL_MiningDerrick_003','Block',{32.139,8.95,381.698},{-0.643,0.0,0.766},{0.766,0.0,0.643},{6.6,6.6,11.5},false},
  {'COL_MiningDerrick_004','Block',{-32.139,8.95,381.698},{0.643,0.0,0.766},{0.766,0.0,-0.643},{6.6,6.6,11.5},false},
  {'COL_MiningFence_001','Block',{13.367,12.7,479.164},{0.22,0.0,0.975},{0.975,0.0,-0.22},{0.9,15.922,5.0},false},
  {'COL_MiningFence_002','Block',{27.8,12.7,473.909},{0.458,0.0,0.889},{0.889,0.0,-0.458},{0.9,15.922,5.0},false},
  {'COL_MiningFence_003','Block',{40.45,12.7,465.197},{0.667,0.0,0.745},{0.745,0.0,-0.667},{0.9,15.922,5.0},false},
  {'COL_MiningFence_004','Block',{50.507,12.7,453.587},{0.833,0.0,0.554},{0.554,0.0,-0.833},{0.9,15.922,5.0},false},
  {'COL_MiningFence_005','Block',{57.324,12.7,439.823},{0.945,0.0,0.327},{0.327,0.0,-0.945},{0.9,15.922,5.0},false},
  {'COL_MiningFence_006','Block',{60.466,12.7,424.787},{0.997,0.0,0.079},{0.079,0.0,-0.997},{0.9,15.922,5.0},false},
  {'COL_MiningFence_007','Block',{59.729,12.7,409.445},{0.985,0.0,-0.174},{-0.174,0.0,-0.985},{0.9,15.922,5.0},false},
  {'COL_MiningFence_008','Block',{50.327,12.7,386.139},{0.83,0.0,-0.558},{-0.558,0.0,-0.83},{0.9,15.829,5.0},false},
  {'COL_MiningFence_009','Block',{40.277,12.7,374.645},{0.664,0.0,-0.748},{-0.748,0.0,-0.664},{0.9,15.829,5.0},false},
  {'COL_MiningFence_010','Block',{27.676,12.7,366.024},{0.456,0.0,-0.89},{-0.89,0.0,-0.456},{0.9,15.829,5.0},false},
  {'COL_MiningFence_011','Block',{13.322,12.7,360.823},{0.22,0.0,-0.976},{-0.976,0.0,-0.22},{0.9,15.829,5.0},false},
  {'COL_MiningFence_012','Block',{-13.322,12.7,360.823},{-0.22,0.0,-0.976},{-0.976,0.0,0.22},{0.9,15.829,5.0},false},
  {'COL_MiningFence_013','Block',{-27.676,12.7,366.024},{-0.456,0.0,-0.89},{-0.89,0.0,0.456},{0.9,15.829,5.0},false},
  {'COL_MiningFence_014','Block',{-40.277,12.7,374.645},{-0.664,0.0,-0.748},{-0.748,0.0,0.664},{0.9,15.829,5.0},false},
  {'COL_MiningFence_015','Block',{-50.327,12.7,386.138},{-0.83,0.0,-0.558},{-0.558,0.0,0.83},{0.9,15.829,5.0},false},
  {'COL_MiningFence_016','Block',{-59.729,12.7,409.445},{-0.985,0.0,-0.174},{-0.174,0.0,0.985},{0.9,15.922,5.0},false},
  {'COL_MiningFence_017','Block',{-60.466,12.7,424.787},{-0.997,0.0,0.079},{0.079,0.0,0.997},{0.9,15.922,5.0},false},
  {'COL_MiningFence_018','Block',{-57.324,12.7,439.823},{-0.945,0.0,0.327},{0.327,0.0,0.945},{0.9,15.922,5.0},false},
  {'COL_MiningFence_019','Block',{-50.507,12.7,453.587},{-0.833,0.0,0.554},{0.554,0.0,0.833},{0.9,15.922,5.0},false},
  {'COL_MiningFence_020','Block',{-40.45,12.7,465.197},{-0.667,0.0,0.745},{0.745,0.0,0.667},{0.9,15.922,5.0},false},
  {'COL_MiningFence_021','Block',{-27.8,12.7,473.909},{-0.458,0.0,0.889},{0.889,0.0,0.458},{0.9,15.922,5.0},false},
  {'COL_MiningFence_022','Block',{-13.367,12.7,479.164},{-0.22,0.0,0.975},{0.975,0.0,0.22},{0.9,15.922,5.0},false},
  {'COL_MiningLantern_001','Block',{-76.968,13.4,439.905},{-0.968,0.0,0.25},{0.25,0.0,0.968},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_002','Block',{-66.102,13.4,464.168},{-0.831,0.0,0.556},{0.556,0.0,0.831},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_003','Block',{-41.242,13.4,487.965},{-0.519,0.0,0.855},{0.855,0.0,0.519},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_004','Block',{-15.51,13.4,497.972},{-0.195,0.0,0.981},{0.981,0.0,0.195},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_005','Block',{15.51,13.4,497.972},{0.195,0.0,0.981},{0.981,0.0,-0.195},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_006','Block',{42.422,13.4,487.235},{0.534,0.0,0.846},{0.846,0.0,-0.534},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_007','Block',{66.102,13.4,464.168},{0.831,0.0,0.556},{0.556,0.0,-0.831},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_008','Block',{76.127,13.4,442.912},{0.958,0.0,0.288},{0.288,0.0,-0.958},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_009','Block',{77.972,13.4,404.49},{0.981,0.0,-0.195},{-0.195,0.0,-0.981},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_010','Block',{66.102,13.4,375.832},{0.831,0.0,-0.556},{-0.556,0.0,-0.831},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_011','Block',{44.168,13.4,353.898},{0.556,0.0,-0.831},{-0.831,0.0,-0.556},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_012','Block',{15.51,13.4,342.028},{0.195,0.0,-0.981},{-0.981,0.0,-0.195},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_013','Block',{-15.51,13.4,342.028},{-0.195,0.0,-0.981},{-0.981,0.0,0.195},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_014','Block',{-44.168,13.4,353.898},{-0.556,0.0,-0.831},{-0.831,0.0,0.556},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_015','Block',{-66.102,13.4,375.832},{-0.831,0.0,-0.556},{-0.556,0.0,0.831},{1.7,1.7,6.4},false},
  {'COL_MiningLantern_016','Block',{-77.972,13.4,404.49},{-0.981,0.0,-0.195},{-0.195,0.0,0.981},{1.7,1.7,6.4},false},
  {'COL_MiningProps_001','Block',{-44.336,5.0,454.639},{0.616,0.0,0.788},{0.788,0.0,-0.616},{11.069,2.6,3.6},false},
  {'COL_MiningProps_002','Block',{21.7,4.7,471.307},{0.927,0.0,-0.375},{-0.375,0.0,-0.927},{7.6,3.2,3.0},false},
  {'COL_MiningProps_003','Block',{47.172,5.1,451.818},{0.559,0.0,-0.829},{-0.829,0.0,-0.559},{7.2,1.8,3.8},false},
  {'COL_MiningProps_004','Block',{45.291,4.8,387.921},{-0.574,0.0,-0.819},{-0.819,0.0,0.574},{5.4,3.0,3.2},false},
  {'COL_MiningProps_005','Block',{19.119,4.7,367.471},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{5.6,3.0,3.0},false},
  {'COL_MiningRamp_001','Ramp',{-52.864,6.211,415.269},{0.085,0.211,-0.974},{-0.996,-0.0,-0.087},{33.2,8.0,1.0},false},
  {'COL_MiningRamp_002','Block',{-52.122,6.45,397.043},{-0.087,0.0,0.996},{0.996,0.0,0.087},{5.0,9.7,7.5},false},
  {'COL_MiningRamp_003','Block',{-47.124,12.4,397.28},{-0.087,0.0,0.996},{0.996,0.0,0.087},{4.6,0.6,4.4},false},
  {'COL_MiningRamp_004','Block',{-50.532,12.4,394.673},{0.996,0.0,0.087},{0.087,0.0,-0.996},{7.245,0.6,4.4},false},
  {'COL_MiningRamp_005','Block',{-48.652,9.116,414.74},{-0.085,-0.211,0.974},{0.996,0.0,0.087},{31.154,0.6,4.4},false},
  {'COL_MiningRamp_006','Block',{-56.985,8.954,414.763},{-0.085,-0.211,0.974},{0.996,-0.0,0.087},{29.619,0.6,4.4},false},
  {'COL_MiningRamp_007','Block',{-48.082,4.182,401.914},{-0.085,-0.211,0.974},{0.996,-0.0,0.087},{4.501,0.6,9.0},false},
  {'COL_MiningRamp_008','Ramp',{52.864,6.211,415.269},{-0.085,0.211,-0.974},{-0.996,0.0,0.087},{33.2,8.0,1.0},false},
  {'COL_MiningRamp_009','Block',{52.122,6.45,397.043},{0.087,0.0,0.996},{0.996,0.0,-0.087},{5.0,9.7,7.5},false},
  {'COL_MiningRamp_010','Block',{47.124,12.4,397.28},{0.087,0.0,0.996},{0.996,0.0,-0.087},{4.6,0.6,4.4},false},
  {'COL_MiningRamp_011','Block',{50.532,12.4,394.673},{0.996,0.0,-0.087},{-0.087,0.0,-0.996},{7.245,0.6,4.4},false},
  {'COL_MiningRamp_012','Block',{48.652,9.116,414.74},{0.085,-0.211,0.974},{0.996,-0.0,-0.087},{31.154,0.6,4.4},false},
  {'COL_MiningRamp_013','Block',{56.985,8.954,414.763},{0.085,-0.211,0.974},{0.996,-0.0,-0.087},{29.619,0.6,4.4},false},
  {'COL_MiningRamp_014','Block',{48.082,4.182,401.914},{0.085,-0.211,0.974},{0.996,-0.0,-0.087},{4.501,0.6,9.0},false},
  {'COL_MiningStairs_001','Ramp',{0.0,6.25,367.781},{0.0,0.437,-0.899},{-1.0,0.0,-0.0},{16.011,10.0,1.0},false},
  {'COL_MiningStairs_002','Block',{0.0,9.7,360.25},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{1.1,10.0,1.0},false},
  {'COL_MiningStairs_003','Ramp',{5.6,7.777,367.723},{0.0,0.437,-0.899},{-1.0,0.0,-0.0},{16.011,1.2,5.5},false},
  {'COL_MiningStairs_004','Ramp',{-5.6,7.777,367.723},{0.0,0.437,-0.899},{-1.0,0.0,-0.0},{16.011,1.2,5.5},false},
  {'COL_MiningStairs_005','Ramp',{-0.0,6.25,472.219},{0.0,0.437,0.899},{1.0,-0.0,-0.0},{16.011,10.0,1.0},false},
  {'COL_MiningStairs_006','Block',{-0.0,9.7,479.75},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.1,10.0,1.0},false},
  {'COL_MiningStairs_007','Ramp',{-5.6,7.777,472.277},{0.0,0.437,0.899},{1.0,0.0,-0.0},{16.011,1.2,5.5},false},
  {'COL_MiningStairs_008','Ramp',{5.6,7.777,472.277},{0.0,0.437,0.899},{1.0,0.0,-0.0},{16.011,1.2,5.5},false},
  {'COL_PropBench_001','Block',{20.0,23.181,551.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.8,1.2,1.4},false},
  {'COL_PropBench_002','Block',{-20.0,23.131,551.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.8,1.2,1.4},false},
  {'COL_PropCrate_001','Block',{-96.0,7.3,444.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_002','Block',{26.5,17.3,529.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_003','Block',{-48.2,17.3,524.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_004','Block',{73.8,17.3,526.75},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_005','Block',{-94.2,-2.9,524.75},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_006','Block',{102.8,17.3,501.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_007','Block',{87.8,23.3,576.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropCrate_008','Block',{-105.45,23.3,566.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.0,2.0,2.2},false},
  {'COL_PropLamp_001','Block',{9.0,20.5,532.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_002','Block',{-14.0,26.749,554.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_003','Block',{30.0,26.5,560.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_004','Block',{-30.0,26.5,560.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_005','Block',{44.0,20.5,538.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_006','Block',{72.0,20.5,520.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_007','Block',{-72.0,20.5,520.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_008','Block',{98.0,20.5,450.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_009','Block',{40.0,26.5,566.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropLamp_010','Block',{74.0,26.5,564.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.0,1.0,8.6},false},
  {'COL_PropTraining_001','Block',{64.0,8.9,353.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,5.4},false},
  {'COL_PropTraining_002','Block',{58.0,8.9,355.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,5.4},false},
  {'COL_PropTraining_003','Block',{52.0,8.9,353.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,5.4},false},
  {'COL_PropTraining_004','Block',{48.5,7.7,348.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.2,3.4,3.0},false},
  {'COL_PropTraining_005','Block',{58.0,7.1,345.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{15.0,0.6,1.8},false},
  {'COL_PropTraining_006','Block',{58.0,7.1,356.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{15.0,0.6,1.8},false},
  {'COL_Rim_001','Block',{18.5,9.7,301.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.0,1.2,9.0},false},
  {'COL_Rim_002','Block',{-18.5,9.7,301.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.0,1.2,9.0},false},
  {'COL_Rim_003','Block',{-29.5,9.7,303.45},{-0.937,0.0,0.349},{0.349,0.0,0.937},{12.739,1.2,9.0},false},
  {'COL_Rim_004','Block',{-45.5,9.7,312.25},{-0.841,0.0,0.541},{0.541,0.0,0.841},{25.965,1.2,9.0},false},
  {'COL_Rim_005','Block',{-66.0,9.7,325.5},{-0.838,0.0,0.545},{0.545,0.0,0.838},{24.854,1.2,9.0},false},
  {'COL_Rim_006','Block',{-86.0,9.7,336.0},{-0.928,0.0,0.371},{0.371,0.0,0.928},{22.541,1.2,9.0},false},
  {'COL_Rim_007','Block',{-104.0,9.7,348.0},{-0.707,0.0,0.707},{0.707,0.0,0.707},{23.627,1.2,9.0},false},
  {'COL_Rim_008','Block',{-121.0,9.7,366.0},{-0.669,0.0,0.743},{0.743,0.0,0.669},{27.907,1.2,9.0},false},
  {'COL_Rim_009','Block',{-137.0,9.7,392.0},{-0.401,0.0,0.916},{0.916,0.0,0.401},{35.928,1.2,9.0},false},
  {'COL_Rim_010','Block',{-147.0,9.7,427.0},{-0.156,0.0,0.988},{0.988,0.0,0.156},{39.471,1.2,9.0},false},
  {'COL_Rim_011','Block',{-148.0,9.7,465.0},{0.105,0.0,0.995},{0.995,0.0,-0.105},{39.21,1.2,9.0},false},
  {'COL_Rim_012','Block',{-139.0,9.7,501.0},{0.381,0.0,0.925},{0.925,0.0,-0.381},{37.77,1.2,9.0},false},
  {'COL_Rim_013','Block',{-129.222,9.7,525.222},{0.359,0.0,0.933},{0.933,0.0,-0.359},{16.476,1.2,9.0},false},
  {'COL_Rim_014','Block',{-118.167,25.7,567.0},{0.164,0.0,0.986},{0.986,0.0,-0.164},{27.359,1.2,9.0},false},
  {'COL_Rim_015','Block',{-108.0,25.7,595.0},{0.471,0.0,0.882},{0.882,0.0,-0.471},{35.0,1.2,9.0},false},
  {'COL_Rim_016','Block',{-82.0,75.5,617.0},{0.932,0.0,0.362},{0.362,0.0,-0.932},{39.626,1.2,9.0},false},
  {'COL_Rim_017','Block',{-32.0,75.5,626.0},{0.998,0.0,0.062},{0.062,0.0,-0.998},{65.125,1.2,9.0},false},
  {'COL_Rim_018','Block',{32.0,75.5,626.0},{0.998,0.0,-0.062},{-0.062,0.0,-0.998},{65.125,1.2,9.0},false},
  {'COL_Rim_019','Block',{84.0,75.5,617.0},{0.944,0.0,-0.33},{-0.33,0.0,-0.944},{43.379,1.2,9.0},false},
  {'COL_Rim_020','Block',{119.0,25.7,595.0},{0.707,0.0,-0.707},{-0.707,0.0,-0.707},{43.426,1.2,9.0},false},
  {'COL_Rim_021','Block',{142.0,25.7,560.0},{0.371,0.0,-0.928},{-0.928,0.0,-0.371},{44.081,1.2,9.0},false},
  {'COL_Rim_022','Block',{154.0,19.7,518.0},{0.179,0.0,-0.984},{-0.984,0.0,-0.179},{45.721,1.2,9.0},false},
  {'COL_Rim_023','Block',{158.0,19.7,473.0},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{47.0,1.2,9.0},false},
  {'COL_Rim_024','Block',{153.0,19.7,432.0},{-0.268,0.0,-0.964},{-0.964,0.0,0.268},{38.363,1.2,9.0},false},
  {'COL_Rim_025','Block',{137.0,19.7,399.0},{-0.591,0.0,-0.806},{-0.806,0.0,0.591},{38.202,1.2,9.0},false},
  {'COL_Rim_026','Block',{111.0,9.7,371.0},{-0.756,0.0,-0.655},{-0.655,0.0,0.756},{40.699,1.2,9.0},false},
  {'COL_Rim_027','Block',{86.0,9.7,346.0},{-0.64,0.0,-0.768},{-0.768,0.0,0.64},{32.241,1.2,9.0},false},
  {'COL_Rim_028','Block',{64.0,9.7,325.0},{-0.8,0.0,-0.6},{-0.6,0.0,0.8},{31.0,1.2,9.0},false},
  {'COL_Rim_029','Block',{43.5,9.7,310.75},{-0.851,0.0,-0.525},{-0.525,0.0,0.851},{20.981,1.2,9.0},false},
  {'COL_Rim_030','Block',{29.5,9.7,303.45},{-0.937,0.0,-0.349},{-0.349,0.0,0.937},{12.739,1.2,9.0},false},
  {'COL_SummonPlaza_001','Block',{120.0,15.85,415.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.402,4.0,1.3},false},
  {'COL_SummonPlaza_002','Block',{120.0,15.85,419.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{29.154,4.0,1.3},false},
  {'COL_SummonPlaza_003','Block',{120.0,15.85,423.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{39.486,4.0,1.3},false},
  {'COL_SummonPlaza_004','Block',{120.0,15.85,427.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{46.279,4.0,1.3},false},
  {'COL_SummonPlaza_005','Block',{120.788,15.85,431.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{49.365,4.0,1.3},false},
  {'COL_SummonPlaza_006','Block',{121.213,15.85,435.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{51.627,4.0,1.3},false},
  {'COL_SummonPlaza_007','Block',{121.313,15.85,439.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.236,4.0,1.3},false},
  {'COL_SummonPlaza_008','Block',{120.993,15.85,443.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{54.008,4.0,1.3},false},
  {'COL_SummonPlaza_009','Block',{120.229,15.85,447.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.889,4.0,1.3},false},
  {'COL_SummonPlaza_010','Block',{120.0,15.85,451.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{51.394,4.0,1.3},false},
  {'COL_SummonPlaza_011','Block',{120.0,15.85,455.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{46.907,4.0,1.3},false},
  {'COL_SummonPlaza_012','Block',{120.0,15.85,459.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{40.45,4.0,1.3},false},
  {'COL_SummonPlaza_013','Block',{120.0,15.85,463.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{30.644,4.0,1.3},false},
  {'COL_SummonPlaza_014','Block',{120.0,15.85,467.767},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.786,4.0,1.3},false},
  {'COL_SummonRail_001','Block',{93.746,18.45,447.044},{0.189,0.0,0.982},{0.982,0.0,-0.189},{7.174,1.3,4.4},false},
  {'COL_SummonRail_002','Block',{95.507,18.45,452.714},{0.401,0.0,0.916},{0.916,0.0,-0.401},{7.174,1.3,4.4},false},
  {'COL_SummonRail_003','Block',{109.069,18.45,465.987},{0.91,0.0,0.415},{0.415,0.0,-0.91},{11.926,1.3,4.4},false},
  {'COL_SummonRail_004','Block',{145.596,18.45,435.355},{-0.251,0.0,-0.968},{-0.968,0.0,0.251},{11.054,1.3,4.4},false},
  {'COL_SummonRail_005','Block',{141.486,18.45,426.583},{-0.583,0.0,-0.812},{-0.812,0.0,0.583},{11.054,1.3,4.4},false},
  {'COL_SummonRail_006','Block',{134.493,18.45,419.88},{-0.836,0.0,-0.548},{-0.548,0.0,0.836},{11.054,1.3,4.4},false},
  {'COL_SummonRail_007','Block',{125.555,18.45,416.145},{-0.978,0.0,-0.21},{-0.21,0.0,0.978},{11.054,1.3,4.4},false},
  {'COL_SummonRail_008','Block',{115.871,18.45,415.879},{-0.988,0.0,0.156},{0.156,0.0,0.988},{11.054,1.3,4.4},false},
  {'COL_SummonRail_009','Block',{106.742,18.45,419.119},{-0.865,0.0,0.501},{0.501,0.0,0.865},{11.054,1.3,4.4},false},
  {'COL_SummonRail_010','Block',{99.391,18.45,425.428},{-0.627,0.0,0.779},{0.779,0.0,0.627},{11.054,1.3,4.4},false},
  {'COL_SummonTower_001','Ramp',{124.664,17.753,450.163},{0.733,0.447,0.513},{0.574,0.0,-0.819},{8.944,7.6,1.0},false},
  {'COL_SummonTower_002','Block',{128.208,19.7,452.645},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.1,7.6,1.0},false},
  {'COL_SummonTower_003','Ramp',{122.178,19.26,453.794},{0.733,0.447,0.513},{0.574,-0.0,-0.819},{8.944,1.2,5.5},false},
  {'COL_SummonTower_004','Ramp',{127.226,19.26,446.585},{0.733,0.447,0.513},{0.574,-0.0,-0.819},{8.944,1.2,5.5},false},
  {'COL_SummonTower_005','Block',{127.118,16.3,467.538},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{15.65,20.9,1.4},false},
  {'COL_SummonTower_006','Block',{128.077,18.25,465.646},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{11.45,18.3,2.5},false},
  {'COL_SummonTower_007','Block',{141.831,16.3,446.527},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{15.65,20.9,1.4},false},
  {'COL_SummonTower_008','Block',{140.38,18.25,448.075},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{11.45,18.3,2.5},false},
  {'COL_SummonTower_009','Block',{138.591,17.55,459.915},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{10.0,10.85,3.9},false},
  {'COL_SummonTower_010','Block',{131.28,18.1,454.796},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{10.0,7.0,4.2},false},
  {'COL_SummonTower_011','Block',{137.71,36.05,459.298},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{17.2,8.7,33.1},false},
  {'COL_SummonTower_012','Block',{133.041,42.4,456.029},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{17.2,2.7,20.4},false},
  {'COL_SummonTower_013','Block',{130.706,33.3,454.394},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{8.0,3.0,2.2},false},
  {'COL_SummonTower_014','Block',{128.199,26.95,460.329},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,5.7,14.9},false},
  {'COL_SummonTower_015','Block',{130.123,33.35,465.339},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.2,2.2,27.7},false},
  {'COL_SummonTower_016','Block',{122.906,21.25,460.652},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{3.4,3.4,3.5},false},
  {'COL_SummonTower_017','Block',{119.274,19.05,453.286},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.5,1.5,5.7},false},
  {'COL_SummonTower_018','Block',{117.925,21.5,467.418},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,4.6,9.0},false},
  {'COL_SummonTower_019','Block',{130.376,21.5,476.136},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,4.6,9.0},false},
  {'COL_SummonTower_020','Block',{135.426,26.95,450.008},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,5.7,14.9},false},
  {'COL_SummonTower_021','Block',{140.792,33.35,450.103},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.2,2.2,27.7},false},
  {'COL_SummonTower_022','Block',{133.919,21.25,444.924},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{3.4,3.4,3.5},false},
  {'COL_SummonTower_023','Block',{125.756,19.05,444.03},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.5,1.5,5.7},false},
  {'COL_SummonTower_024','Block',{138.573,21.5,437.929},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,4.6,9.0},false},
  {'COL_SummonTower_025','Block',{151.024,21.5,446.647},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{4.6,4.6,9.0},false},
  {'COL_TerrainBed_001','Block',{-100.756,1.6,337.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.895,4.0,6.0},false},
  {'COL_TerrainBed_002','Block',{-101.269,1.6,341.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.87,4.0,6.0},false},
  {'COL_TerrainBed_003','Block',{-102.267,1.6,345.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.867,4.0,6.0},false},
  {'COL_TerrainBed_004','Block',{-103.266,1.6,349.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.863,4.0,6.0},false},
  {'COL_TerrainBed_005','Block',{-104.266,1.6,353.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.857,4.0,6.0},false},
  {'COL_TerrainBed_006','Block',{-105.301,1.6,357.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.921,4.0,6.0},false},
  {'COL_TerrainBed_007','Block',{-106.578,1.6,361.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.47,4.0,6.0},false},
  {'COL_TerrainBed_008','Block',{-107.97,1.6,365.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.789,4.0,6.0},false},
  {'COL_TerrainBed_009','Block',{-109.526,1.6,369.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.781,4.0,6.0},false},
  {'COL_TerrainBed_010','Block',{-111.081,1.6,373.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.773,4.0,6.0},false},
  {'COL_TerrainBed_011','Block',{-112.4,1.6,377.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.291,4.0,6.0},false},
  {'COL_TerrainBed_012','Block',{-113.543,1.6,381.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.458,4.0,6.0},false},
  {'COL_TerrainBed_013','Block',{-114.286,1.6,385.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.425,4.0,6.0},false},
  {'COL_TerrainBed_014','Block',{-115.013,1.6,389.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.423,4.0,6.0},false},
  {'COL_TerrainBed_015','Block',{-115.74,1.6,393.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.422,4.0,6.0},false},
  {'COL_TerrainBed_016','Block',{-116.468,1.6,397.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.42,4.0,6.0},false},
  {'COL_TerrainBed_017','Block',{-116.928,1.6,401.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.884,4.0,6.0},false},
  {'COL_TerrainBed_018','Block',{-117.127,1.6,405.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.687,4.0,6.0},false},
  {'COL_TerrainBed_019','Block',{-117.227,1.6,409.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.688,4.0,6.0},false},
  {'COL_TerrainBed_020','Block',{-117.327,1.6,413.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.688,4.0,6.0},false},
  {'COL_TerrainBed_021','Block',{-117.427,1.6,417.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.689,4.0,6.0},false},
  {'COL_TerrainBed_022','Block',{-117.527,1.6,421.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.69,4.0,6.0},false},
  {'COL_TerrainBed_023','Block',{-117.627,1.6,425.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.691,4.0,6.0},false},
  {'COL_TerrainBed_024','Block',{-117.727,1.6,429.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.692,4.0,6.0},false},
  {'COL_TerrainBed_025','Block',{-117.827,1.6,433.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.692,4.0,6.0},false},
  {'COL_TerrainBed_026','Block',{-117.927,1.6,439.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.693,8.0,6.0},false},
  {'COL_TerrainBed_028','Block',{-117.746,1.6,445.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_029','Block',{-117.546,1.6,449.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_030','Block',{-117.346,1.6,453.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_031','Block',{-117.146,1.6,457.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_032','Block',{-116.946,1.6,461.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_033','Block',{-116.746,1.6,465.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_034','Block',{-116.546,1.6,469.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_035','Block',{-116.346,1.6,473.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.8,4.0,6.0},false},
  {'COL_TerrainBed_036','Block',{-116.146,1.6,477.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.799,4.0,6.0},false},
  {'COL_TerrainBed_037','Block',{-115.59,1.6,481.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.512,4.0,6.0},false},
  {'COL_TerrainBed_038','Block',{-114.715,1.6,485.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.813,4.0,6.0},false},
  {'COL_TerrainBed_039','Block',{-113.663,1.6,489.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.961,4.0,6.0},false},
  {'COL_TerrainBed_040','Block',{-112.573,1.6,493.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.183,4.0,6.0},false},
  {'COL_TerrainBed_041','Block',{-111.377,1.6,497.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.192,4.0,6.0},false},
  {'COL_TerrainBed_042','Block',{-110.578,1.6,501.075},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.392,4.0,6.0},false},
  {'COL_TerrainBed_043','Block',{-113.395,1.6,503.424},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.359,0.699,6.0},false},
  {'COL_TerrainGuard_001','Block',{75.271,12.2,389.422},{-0.376,0.0,-0.926},{-0.926,0.0,0.376},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_002','Block',{72.819,12.2,383.97},{-0.443,0.0,-0.896},{-0.896,0.0,0.443},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_003','Block',{69.972,12.2,378.712},{-0.508,0.0,-0.861},{-0.861,0.0,0.508},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_004','Block',{66.746,12.2,373.679},{-0.57,0.0,-0.822},{-0.822,0.0,0.57},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_005','Block',{63.159,12.2,368.896},{-0.629,0.0,-0.777},{-0.777,0.0,0.629},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_006','Block',{59.23,12.2,364.389},{-0.684,0.0,-0.729},{-0.729,0.0,0.684},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_007','Block',{54.98,12.2,360.184},{-0.736,0.0,-0.677},{-0.677,0.0,0.736},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_008','Block',{50.432,12.2,356.303},{-0.784,0.0,-0.621},{-0.621,0.0,0.784},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_009','Block',{45.612,12.2,352.767},{-0.828,0.0,-0.561},{-0.561,0.0,0.828},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_010','Block',{40.544,12.2,349.595},{-0.867,0.0,-0.499},{-0.499,0.0,0.867},{5.983,1.2,4.0},false},
  {'COL_TerrainGuard_011','Block',{21.259,12.2,341.644},{-0.965,0.0,-0.262},{-0.262,0.0,0.965},{8.489,1.2,4.0},false},
  {'COL_TerrainGuard_012','Block',{12.973,12.2,339.854},{-0.987,0.0,-0.16},{-0.16,0.0,0.987},{8.489,1.2,4.0},false},
  {'COL_TerrainGuard_013','Block',{-12.973,12.2,339.854},{-0.987,0.0,0.16},{0.16,0.0,0.987},{8.489,1.2,4.0},false},
  {'COL_TerrainGuard_014','Block',{-21.259,12.2,341.644},{-0.965,0.0,0.262},{0.262,0.0,0.965},{8.489,1.2,4.0},false},
  {'COL_TerrainGuard_015','Block',{-40.52,12.2,349.579},{-0.867,0.0,0.499},{0.499,0.0,0.867},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_016','Block',{-45.542,12.2,352.718},{-0.828,0.0,0.561},{0.561,0.0,0.828},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_017','Block',{-50.321,12.2,356.214},{-0.785,0.0,0.619},{0.619,0.0,0.785},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_018','Block',{-54.834,12.2,360.049},{-0.738,0.0,0.675},{0.675,0.0,0.738},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_019','Block',{-59.055,12.2,364.202},{-0.687,0.0,0.727},{0.727,0.0,0.687},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_020','Block',{-62.962,12.2,368.652},{-0.632,0.0,0.775},{0.775,0.0,0.632},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_021','Block',{-66.535,12.2,373.374},{-0.574,0.0,0.819},{0.819,0.0,0.574},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_022','Block',{-69.755,12.2,378.345},{-0.513,0.0,0.859},{0.859,0.0,0.513},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_023','Block',{-72.604,12.2,383.536},{-0.449,0.0,0.894},{0.894,0.0,0.449},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_024','Block',{-75.067,12.2,388.921},{-0.383,0.0,0.924},{0.924,0.0,0.383},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_025','Block',{-77.131,12.2,394.472},{-0.314,0.0,0.949},{0.949,0.0,0.314},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_026','Block',{-78.786,12.2,400.158},{-0.244,0.0,0.97},{0.97,0.0,0.244},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_027','Block',{-80.022,12.2,405.949},{-0.173,0.0,0.985},{0.985,0.0,0.173},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_028','Block',{-80.833,12.2,411.815},{-0.101,0.0,0.995},{0.995,0.0,0.101},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_029','Block',{-81.214,12.2,417.725},{-0.028,0.0,1.0},{1.0,0.0,0.028},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_030','Block',{-81.164,12.2,423.646},{0.045,0.0,0.999},{0.999,0.0,-0.045},{5.926,1.2,4.0},false},
  {'COL_TerrainGuard_031','Block',{-78.707,12.2,440.099},{0.247,0.0,0.969},{0.969,0.0,-0.247},{6.625,1.2,4.0},false},
  {'COL_TerrainGuard_032','Block',{-76.809,12.2,446.44},{0.325,0.0,0.946},{0.946,0.0,-0.325},{6.625,1.2,4.0},false},
  {'COL_TerrainGuard_033','Block',{-74.401,12.2,452.606},{0.401,0.0,0.916},{0.916,0.0,-0.401},{6.625,1.2,4.0},false},
  {'COL_TerrainGuard_034','Block',{-77.803,18.2,462.599},{0.48,0.0,0.877},{0.877,0.0,-0.48},{8.371,1.2,4.0},false},
  {'COL_TerrainGuard_035','Block',{-73.446,18.2,469.735},{0.561,0.0,0.828},{0.828,0.0,-0.561},{8.371,1.2,4.0},false},
  {'COL_TerrainGuard_036','Block',{-68.436,18.2,476.43},{0.636,0.0,0.772},{0.772,0.0,-0.636},{8.371,1.2,4.0},false},
  {'COL_TerrainGuard_037','Block',{-62.819,18.2,482.624},{0.706,0.0,0.708},{0.708,0.0,-0.706},{8.371,1.2,4.0},false},
  {'COL_TerrainGuard_038','Block',{-45.264,18.2,496.263},{0.86,0.0,0.51},{0.51,0.0,-0.86},{9.055,1.2,4.0},false},
  {'COL_TerrainGuard_039','Block',{-37.262,18.2,500.477},{0.907,0.0,0.42},{0.42,0.0,-0.907},{9.055,1.2,4.0},false},
  {'COL_TerrainGuard_040','Block',{-28.873,18.2,503.853},{0.946,0.0,0.326},{0.326,0.0,-0.946},{9.055,1.2,4.0},false},
  {'COL_TerrainGuard_041','Block',{-20.183,18.2,506.357},{0.974,0.0,0.228},{0.228,0.0,-0.974},{9.055,1.2,4.0},false},
  {'COL_TerrainGuard_042','Block',{-11.284,18.2,507.964},{0.992,0.0,0.127},{0.127,0.0,-0.992},{9.055,1.2,4.0},false},
  {'COL_TerrainGuard_043','Block',{10.663,18.2,508.071},{0.993,0.0,-0.12},{-0.12,0.0,-0.993},{7.797,1.2,4.0},false},
  {'COL_TerrainGuard_044','Block',{18.347,18.2,506.796},{0.978,0.0,-0.207},{-0.207,0.0,-0.978},{7.797,1.2,4.0},false},
  {'COL_TerrainGuard_045','Block',{25.89,18.2,504.853},{0.956,0.0,-0.292},{-0.292,0.0,-0.956},{7.797,1.2,4.0},false},
  {'COL_TerrainGuard_046','Block',{33.233,18.2,502.255},{0.927,0.0,-0.375},{-0.375,0.0,-0.927},{7.797,1.2,4.0},false},
  {'COL_TerrainGuard_047','Block',{40.32,18.2,499.023},{0.891,0.0,-0.454},{-0.454,0.0,-0.891},{7.797,1.2,4.0},false},
  {'COL_TerrainGuard_048','Block',{47.096,18.2,495.181},{0.847,0.0,-0.531},{-0.531,0.0,-0.847},{7.797,1.2,4.0},false},
  {'COL_TerrainGuard_049','Block',{61.908,18.2,483.508},{0.716,0.0,-0.698},{-0.698,0.0,-0.716},{8.829,1.2,4.0},false},
  {'COL_TerrainGuard_050','Block',{67.909,18.2,477.047},{0.643,0.0,-0.766},{-0.766,0.0,-0.643},{8.829,1.2,4.0},false},
  {'COL_TerrainGuard_051','Block',{73.238,18.2,470.022},{0.564,0.0,-0.826},{-0.826,0.0,-0.564},{8.829,1.2,4.0},false},
  {'COL_TerrainGuard_052','Block',{77.843,18.2,462.502},{0.479,0.0,-0.878},{-0.878,0.0,-0.479},{8.829,1.2,4.0},false},
  {'COL_TerrainGuard_053','Block',{81.679,18.2,454.562},{0.39,0.0,-0.921},{-0.921,0.0,-0.39},{8.829,1.2,4.0},false},
  {'COL_TerrainGuard_054','Block',{84.707,18.2,446.281},{0.296,0.0,-0.955},{-0.955,0.0,-0.296},{8.829,1.2,4.0},false},
  {'COL_TerrainGuard_055','Block',{88.586,18.2,424.722},{0.053,0.0,-0.999},{-0.999,0.0,-0.053},{7.936,1.2,4.0},false},
  {'COL_TerrainGuard_056','Block',{88.653,18.2,416.794},{-0.036,0.0,-0.999},{-0.999,0.0,0.036},{7.936,1.2,4.0},false},
  {'COL_TerrainGuard_057','Block',{88.013,18.2,408.891},{-0.125,0.0,-0.992},{-0.992,0.0,0.125},{7.936,1.2,4.0},false},
  {'COL_TerrainGuard_058','Block',{86.67,18.2,401.077},{-0.213,0.0,-0.977},{-0.977,0.0,0.213},{7.936,1.2,4.0},false},
  {'COL_TerrainGuard_059','Block',{84.634,18.2,393.414},{-0.3,0.0,-0.954},{-0.954,0.0,0.3},{7.936,1.2,4.0},false},
  {'COL_TerrainGuard_060','Block',{60.4,24.2,546.8},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{107.2,1.2,4.0},false},
  {'COL_TerrainGuard_061','Block',{-59.163,24.2,546.8},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{104.726,1.2,4.0},false},
  {'COL_TerrainGuard_062','Block',{-114.966,24.2,549.534},{-0.707,0.0,0.707},{0.707,0.0,0.707},{8.732,2.2,4.0},false},
  {'COL_TerrainGuard_063','Block',{-118.2,24.2,554.137},{0.0,0.0,1.0},{1.0,0.0,-0.0},{2.326,2.2,4.0},false},
  {'COL_TerrainGuard_064','Block',{-107.2,18.2,493.236},{0.0,0.0,1.0},{1.0,0.0,-0.0},{42.472,1.2,4.0},false},
  {'COL_TerrainGuard_065','Block',{-107.2,18.2,542.964},{0.0,0.0,1.0},{1.0,0.0,-0.0},{6.072,1.2,4.0},false},
  {'COL_TerrainGuard_066','Block',{-89.085,18.2,464.006},{-0.899,0.0,0.438},{0.438,0.0,0.899},{21.92,1.2,4.0},false},
  {'COL_TerrainGuard_067','Block',{-106.079,18.2,472.294},{-0.899,0.0,0.438},{0.438,0.0,0.899},{2.495,1.2,4.0},false},
  {'COL_TerrainGuard_068','Block',{99.87,18.2,383.65},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{36.56,1.2,4.0},false},
  {'COL_TerrainGuard_069','Block',{-105.747,18.34,462.03},{-0.899,0.0,0.438},{0.438,0.0,0.899},{6.9,1.2,4.0},false},
  {'COL_TerrainGuard_070','Block',{-107.055,18.34,467.219},{0.438,0.0,0.899},{0.899,0.0,-0.438},{8.18,1.2,4.0},false},
  {'COL_TerrainRock_001','Block',{-118.7,13.7,560.925},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.4,16.15,17.0},false},
  {'COL_TerrainRock_002','Block',{-120.65,13.7,562.25},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.5,13.5,17.0},false},
  {'COL_TerrainStairs_001','Ramp',{-0.0,12.743,508.652},{0.0,0.404,0.915},{1.0,0.0,-0.0},{14.865,12.0,1.0},false},
  {'COL_TerrainStairs_002','Block',{-0.0,15.7,515.825},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.15,12.0,1.0},false},
  {'COL_TerrainStairs_003','Ramp',{-6.6,14.703,509.602},{0.0,0.404,0.915},{1.0,-0.0,-0.0},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_004','Block',{-6.6,10.925,503.35},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_005','Ramp',{6.6,14.703,509.602},{0.0,0.404,0.915},{1.0,-0.0,-0.0},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_006','Block',{6.6,10.925,503.35},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_007','Block',{-6.6,12.0,502.15},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_008','Block',{6.6,12.0,502.15},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_009','Ramp',{54.58,12.743,489.859},{0.563,0.404,0.721},{0.788,0.0,-0.616},{14.865,9.0,1.0},false},
  {'COL_TerrainStairs_010','Block',{58.996,15.7,495.511},{0.616,0.0,0.788},{0.788,0.0,-0.616},{1.15,9.0,1.0},false},
  {'COL_TerrainStairs_011','Ramp',{51.146,14.703,493.747},{0.563,0.404,0.721},{0.788,-0.0,-0.616},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_012','Block',{47.297,10.925,488.821},{0.616,0.0,0.788},{0.788,0.0,-0.616},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_013','Ramp',{59.183,14.703,487.468},{0.563,0.404,0.721},{0.788,0.0,-0.616},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_014','Block',{55.334,10.925,482.541},{0.616,0.0,0.788},{0.788,0.0,-0.616},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_015','Block',{46.558,12.0,487.875},{0.616,0.0,0.788},{0.788,0.0,-0.616},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_016','Block',{54.595,12.0,481.595},{0.616,0.0,0.788},{0.788,0.0,-0.616},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_017','Ramp',{-54.58,12.743,489.859},{-0.563,0.404,0.721},{0.788,0.0,0.616},{14.865,12.0,1.0},false},
  {'COL_TerrainStairs_018','Block',{-58.996,15.7,495.511},{-0.616,0.0,0.788},{0.788,0.0,0.616},{1.15,12.0,1.0},false},
  {'COL_TerrainStairs_019','Ramp',{-60.365,14.703,486.544},{-0.563,0.404,0.721},{0.788,0.0,0.616},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_020','Block',{-56.516,10.925,481.617},{-0.616,0.0,0.788},{0.788,0.0,0.616},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_021','Ramp',{-49.964,14.703,494.671},{-0.563,0.404,0.721},{0.788,-0.0,0.616},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_022','Block',{-46.115,10.925,489.744},{-0.616,0.0,0.788},{0.788,0.0,0.616},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_023','Block',{-55.777,12.0,480.672},{-0.616,0.0,0.788},{0.788,0.0,0.616},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_024','Block',{-45.376,12.0,488.798},{-0.616,0.0,0.788},{0.788,0.0,0.616},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_025','Ramp',{87.305,12.743,435.394},{0.901,0.404,0.159},{0.174,-0.0,-0.985},{14.865,12.0,1.0},false},
  {'COL_TerrainStairs_026','Block',{94.369,15.7,436.64},{0.985,0.0,0.174},{0.174,0.0,-0.985},{1.15,12.0,1.0},false},
  {'COL_TerrainStairs_027','Ramp',{87.095,14.703,442.059},{0.901,0.404,0.159},{0.174,-0.0,-0.985},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_028','Block',{80.938,10.925,440.973},{0.985,0.0,0.174},{0.174,0.0,-0.985},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_029','Ramp',{89.387,14.703,429.06},{0.901,0.404,0.159},{0.174,-0.0,-0.985},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_030','Block',{83.23,10.925,427.974},{0.985,0.0,0.174},{0.174,0.0,-0.985},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_031','Block',{79.756,12.0,440.765},{0.985,0.0,0.174},{0.174,0.0,-0.985},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_032','Block',{82.048,12.0,427.765},{0.985,0.0,0.174},{0.174,0.0,-0.985},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_033','Ramp',{-0.0,18.743,542.152},{-0.0,0.404,0.915},{1.0,0.0,0.0},{14.865,12.0,1.0},false},
  {'COL_TerrainStairs_034','Block',{-0.0,21.7,549.325},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.15,12.0,1.0},false},
  {'COL_TerrainStairs_035','Ramp',{-6.6,20.703,543.102},{0.0,0.404,0.915},{1.0,-0.0,-0.0},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_036','Block',{-6.6,16.925,536.85},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_037','Ramp',{6.6,20.703,543.102},{0.0,0.404,0.915},{1.0,-0.0,-0.0},{13.099,1.2,5.5},false},
  {'COL_TerrainStairs_038','Block',{6.6,16.925,536.85},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.75,1.2,2.45},false},
  {'COL_TerrainStairs_039','Block',{-6.6,18.0,535.65},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_040','Block',{6.6,18.0,535.65},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_041','Ramp',{0.0,7.748,332.613},{-0.0,0.426,0.905},{1.0,-0.0,0.0},{9.394,16.0,1.0},false},
  {'COL_TerrainStairs_042','Block',{0.0,9.7,337.225},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.15,16.0,1.0},false},
  {'COL_TerrainStairs_043','Ramp',{-8.6,9.713,333.573},{-0.0,0.426,0.905},{1.0,0.0,0.0},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_044','Block',{-8.6,6.95,329.85},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_045','Ramp',{8.6,9.713,333.573},{-0.0,0.426,0.905},{1.0,0.0,0.0},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_046','Block',{8.6,6.95,329.85},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_047','Block',{-8.6,8.0,328.65},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_048','Block',{8.6,8.0,328.65},{0.0,0.0,1.0},{1.0,0.0,-0.0},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_049','Ramp',{-85.604,7.748,432.0},{0.905,0.426,0.0},{0.0,0.0,-1.0},{9.394,8.0,1.0},false},
  {'COL_TerrainStairs_050','Block',{-80.992,9.7,432.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.15,8.0,1.0},false},
  {'COL_TerrainStairs_051','Ramp',{-84.644,9.713,436.6},{0.905,0.426,0.0},{0.0,0.0,-1.0},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_052','Block',{-88.367,6.95,436.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_053','Ramp',{-84.644,9.713,427.4},{0.905,0.426,0.0},{0.0,0.0,-1.0},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_054','Block',{-88.367,6.95,427.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_055','Ramp',{34.731,7.748,338.179},{-0.354,0.426,0.833},{0.921,0.0,0.391},{9.394,10.0,1.0},false},
  {'COL_TerrainStairs_056','Block',{32.929,9.7,342.424},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.15,10.0,1.0},false},
  {'COL_TerrainStairs_057','Ramp',{29.201,9.713,336.875},{-0.354,0.426,0.833},{0.921,0.0,0.391},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_058','Block',{30.656,6.95,333.448},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_059','Ramp',{39.511,9.713,341.251},{-0.354,0.426,0.833},{0.921,-0.0,0.391},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_060','Block',{40.965,6.95,337.824},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_061','Block',{31.125,8.0,332.343},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_062','Block',{41.434,8.0,336.719},{-0.391,0.0,0.921},{0.921,0.0,0.391},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_063','Block',{27.364,12.2,341.203},{-0.391,0.0,0.921},{0.921,0.0,0.391},{2.05,1.2,4.0},false},
  {'COL_TerrainStairs_064','Block',{37.673,12.2,345.579},{-0.391,0.0,0.921},{0.921,0.0,0.391},{2.05,1.2,4.0},false},
  {'COL_TerrainStairs_065','Block',{32.431,9.7,343.598},{-0.391,0.0,0.921},{0.921,0.0,0.391},{2.6,12.4,1.0},false},
  {'COL_TerrainStairs_066','Ramp',{-34.731,7.748,338.179},{0.354,0.426,0.833},{0.921,0.0,-0.391},{9.394,10.0,1.0},false},
  {'COL_TerrainStairs_067','Block',{-32.929,9.7,342.424},{0.391,0.0,0.921},{0.921,0.0,-0.391},{1.15,10.0,1.0},false},
  {'COL_TerrainStairs_068','Ramp',{-39.51,9.713,341.251},{0.354,0.426,0.833},{0.921,0.0,-0.391},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_069','Block',{-40.965,6.95,337.824},{0.391,0.0,0.921},{0.921,0.0,-0.391},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_070','Ramp',{-29.201,9.713,336.875},{0.354,0.426,0.833},{0.921,0.0,-0.391},{7.521,1.2,5.5},false},
  {'COL_TerrainStairs_071','Block',{-30.656,6.95,333.448},{0.391,0.0,0.921},{0.921,0.0,-0.391},{1.75,1.2,2.5},false},
  {'COL_TerrainStairs_072','Block',{-41.434,8.0,336.719},{0.391,0.0,0.921},{0.921,0.0,-0.391},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_073','Block',{-31.125,8.0,332.343},{0.391,0.0,0.921},{0.921,0.0,-0.391},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_074','Block',{-37.673,12.2,345.579},{0.391,0.0,0.921},{0.921,0.0,-0.391},{2.05,1.2,4.0},false},
  {'COL_TerrainStairs_075','Block',{-27.364,12.2,341.203},{0.391,0.0,0.921},{0.921,0.0,-0.391},{2.05,1.2,4.0},false},
  {'COL_TerrainStairs_076','Block',{-32.431,9.7,343.598},{0.391,0.0,0.921},{0.921,0.0,-0.391},{2.6,12.4,1.0},false},
  {'COL_TerrainStairs_077','Ramp',{-90.123,10.747,459.417},{-0.815,0.423,0.397},{0.438,-0.0,0.899},{23.666,8.0,1.0},false},
  {'COL_TerrainStairs_078','Block',{-100.078,15.7,464.272},{-0.899,0.0,0.438},{0.438,0.0,0.899},{1.125,8.0,1.0},false},
  {'COL_TerrainStairs_079','Ramp',{-92.981,12.701,455.693},{-0.815,0.423,0.397},{0.438,-0.0,0.899},{21.814,1.2,5.5},false},
  {'COL_TerrainStairs_080','Block',{-83.793,6.935,451.211},{-0.899,0.0,0.438},{0.438,0.0,0.899},{1.7,1.2,2.469},false},
  {'COL_TerrainStairs_081','Block',{-82.737,8.0,450.696},{-0.899,0.0,0.438},{0.438,0.0,0.899},{1.8,1.8,3.6},false},
  {'COL_TerrainStairs_082','Block',{-103.364,10.7,467.032},{-0.899,0.0,0.438},{0.438,0.0,0.899},{8.6,12.48,11.0},false},
  {'COL_TerrainWall_001','Block',{94.512,11.25,385.281},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{2.8,1.2,11.1},false},
  {'COL_TerrainWall_002','Block',{106.433,11.25,380.942},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{2.8,1.2,11.1},false},
  {'COL_TerrainWall_003','Block',{-108.3,11.25,485.936},{0.0,0.0,1.0},{1.0,0.0,-0.0},{2.8,1.2,11.1},false},
  {'COL_TerrainWall_004','Block',{-109.575,13.7,547.175},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.15,2.85,17.0},false},
  {'COL_TerrainWall_005','Block',{-113.833,13.7,550.167},{-0.707,0.0,0.707},{0.707,0.0,0.707},{10.687,2.6,17.0},false},
  {'COL_TerrainWall_006','Block',{145.7,19.45,545.1},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.3,3.3,7.1},false},
  {'COL_TerrainWall_007','Block',{-108.4,11.35,472.475},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.3,3.3,11.3},false},
  {'COL_TerrainWall_008','Block',{116.083,11.35,377.377},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{3.3,3.3,11.3},false},
  {'COL_TerrainWall_010','Block',{-93.016,10.7,466.257},{-0.899,0.0,0.438},{0.438,0.0,0.899},{31.761,1.6,11.0},false},
  {'COL_Terrain_001','Block',{104.59,2.2,422.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{90.182,5.0,8.0},false},
  {'COL_Terrain_002','Block',{-86.102,2.2,420.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.206,8.6,8.0},false},
  {'COL_Terrain_003','Block',{-134.161,2.2,422.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{23.482,5.0,8.0},false},
  {'COL_Terrain_004','Block',{105.168,2.2,427.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{91.803,5.0,8.0},false},
  {'COL_Terrain_005','Block',{-86.048,2.2,427.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.564,5.0,8.0},false},
  {'COL_Terrain_006','Block',{-134.619,2.2,427.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{24.146,5.0,8.0},false},
  {'COL_Terrain_007','Block',{105.544,2.2,432.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{93.828,5.0,8.0},false},
  {'COL_Terrain_008','Block',{-85.792,2.2,432.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{54.324,5.0,8.0},false},
  {'COL_Terrain_009','Block',{-135.076,2.2,432.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{24.81,5.0,8.0},false},
  {'COL_Terrain_010','Block',{105.702,2.2,437.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{96.291,5.0,8.0},false},
  {'COL_Terrain_011','Block',{-85.318,2.2,437.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{55.522,5.0,8.0},false},
  {'COL_Terrain_012','Block',{-135.534,2.2,437.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{25.474,5.0,8.0},false},
  {'COL_Terrain_013','Block',{105.617,2.2,442.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{99.237,5.0,8.0},false},
  {'COL_Terrain_014','Block',{-84.474,2.2,442.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{56.951,5.0,8.0},false},
  {'COL_Terrain_015','Block',{-135.93,2.2,442.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{26.261,5.0,8.0},false},
  {'COL_Terrain_016','Block',{105.288,2.2,447.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{102.674,5.0,8.0},false},
  {'COL_Terrain_017','Block',{-83.325,2.2,447.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{58.749,5.0,8.0},false},
  {'COL_Terrain_018','Block',{-136.067,2.2,447.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{27.034,5.0,8.0},false},
  {'COL_Terrain_019','Block',{104.672,2.2,452.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{106.655,5.0,8.0},false},
  {'COL_Terrain_020','Block',{-81.897,2.2,452.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{61.105,5.0,8.0},false},
  {'COL_Terrain_021','Block',{-135.679,2.2,452.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{26.758,5.0,8.0},false},
  {'COL_Terrain_022','Block',{103.039,2.2,457.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{109.922,5.0,8.0},false},
  {'COL_Terrain_023','Block',{-80.139,2.2,457.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{64.122,5.0,8.0},false},
  {'COL_Terrain_024','Block',{-135.291,2.2,457.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{26.482,5.0,8.0},false},
  {'COL_Terrain_025','Block',{100.996,2.2,462.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{114.008,5.0,8.0},false},
  {'COL_Terrain_026','Block',{-77.971,2.2,462.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{67.958,5.0,8.0},false},
  {'COL_Terrain_027','Block',{-134.903,2.2,462.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{26.205,5.0,8.0},false},
  {'COL_Terrain_028','Block',{98.419,2.2,467.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{119.162,5.0,8.0},false},
  {'COL_Terrain_029','Block',{-75.269,2.2,467.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{72.862,5.0,8.0},false},
  {'COL_Terrain_030','Block',{-134.514,2.2,467.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{25.929,5.0,8.0},false},
  {'COL_Terrain_031','Block',{95.081,2.2,472.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{125.837,5.0,8.0},false},
  {'COL_Terrain_032','Block',{-71.806,2.2,472.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{79.288,5.0,8.0},false},
  {'COL_Terrain_033','Block',{-134.126,2.2,472.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{25.653,5.0,8.0},false},
  {'COL_Terrain_034','Block',{90.263,2.2,477.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{135.475,5.0,8.0},false},
  {'COL_Terrain_035','Block',{-66.824,2.2,477.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{88.597,5.0,8.0},false},
  {'COL_Terrain_036','Block',{-133.738,2.2,477.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{25.377,5.0,8.0},false},
  {'COL_Terrain_037','Block',{24.08,2.2,482.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{267.84,5.0,8.0},false},
  {'COL_Terrain_038','Block',{-133.204,2.2,482.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{24.809,5.0,8.0},false},
  {'COL_Terrain_039','Block',{24.748,2.2,487.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{266.505,5.0,8.0},false},
  {'COL_Terrain_040','Block',{-131.6,2.2,487.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{23.899,5.0,8.0},false},
  {'COL_Terrain_041','Block',{25.498,2.2,492.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{265.004,5.0,8.0},false},
  {'COL_Terrain_042','Block',{-129.959,2.2,492.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{23.064,5.0,8.0},false},
  {'COL_Terrain_043','Block',{25.889,2.2,497.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{262.785,5.0,8.0},false},
  {'COL_Terrain_044','Block',{-128.214,2.2,497.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{22.437,5.0,8.0},false},
  {'COL_Terrain_045','Block',{25.45,2.2,502.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{261.846,5.0,8.0},false},
  {'COL_Terrain_046','Block',{-126.435,2.2,502.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{21.877,5.0,8.0},false},
  {'COL_Terrain_047','Block',{10.074,2.2,507.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{290.778,5.0,8.0},false},
  {'COL_Terrain_048','Block',{10.649,2.2,512.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{287.81,5.0,8.0},false},
  {'COL_Terrain_049','Block',{11.198,2.2,517.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{284.895,5.0,8.0},false},
  {'COL_Terrain_050','Block',{11.705,2.2,522.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{282.063,5.0,8.0},false},
  {'COL_Terrain_051','Block',{12.212,2.2,527.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{279.231,5.0,8.0},false},
  {'COL_Terrain_052','Block',{12.719,2.2,532.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{276.399,5.0,8.0},false},
  {'COL_Terrain_053','Block',{13.226,2.2,537.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{273.567,5.0,8.0},false},
  {'COL_Terrain_054','Block',{13.089,2.2,542.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{269.862,5.0,8.0},false},
  {'COL_Terrain_055','Block',{12.506,2.2,547.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{267.028,5.0,8.0},false},
  {'COL_Terrain_056','Block',{11.922,2.2,552.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{264.195,5.0,8.0},false},
  {'COL_Terrain_057','Block',{11.339,2.2,557.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{261.362,5.0,8.0},false},
  {'COL_Terrain_058','Block',{10.756,2.2,562.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{258.528,5.0,8.0},false},
  {'COL_Terrain_059','Block',{10.172,2.2,567.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{255.695,5.0,8.0},false},
  {'COL_Terrain_060','Block',{9.589,2.2,572.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{252.862,5.0,8.0},false},
  {'COL_Terrain_061','Block',{9.006,2.2,577.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{250.028,5.0,8.0},false},
  {'COL_Terrain_062','Block',{7.845,2.2,582.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{242.41,5.0,8.0},false},
  {'COL_Terrain_063','Block',{6.678,2.2,587.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{234.743,5.0,8.0},false},
  {'COL_Terrain_064','Block',{5.512,2.2,592.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{227.077,5.0,8.0},false},
  {'COL_Terrain_065','Block',{4.345,2.2,597.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{219.41,5.0,8.0},false},
  {'COL_Terrain_066','Block',{3.178,2.2,602.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{211.743,5.0,8.0},false},
  {'COL_Terrain_067','Block',{2.012,2.2,607.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{204.077,5.0,8.0},false},
  {'COL_Terrain_068','Block',{1.293,2.2,612.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{177.129,5.0,8.0},false},
  {'COL_Terrain_069','Block',{0.579,2.2,617.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{149.986,5.0,8.0},false},
  {'COL_Terrain_070','Block',{-0.0,2.2,622.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{97.6,5.0,8.0},false},
  {'COL_Terrain_071','Block',{-0.0,2.2,626.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,3.0,8.0},false},
  {'COL_Terrain_072','Block',{0.0,2.2,303.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{48.268,5.0,8.0},false},
  {'COL_Terrain_073','Block',{0.03,2.2,308.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{73.016,5.0,8.0},false},
  {'COL_Terrain_074','Block',{0.189,2.2,313.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{88.889,5.0,8.0},false},
  {'COL_Terrain_075','Block',{0.283,2.2,318.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{104.633,5.0,8.0},false},
  {'COL_Terrain_076','Block',{-0.251,2.2,323.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{119.036,5.0,8.0},false},
  {'COL_Terrain_077','Block',{-0.764,2.2,328.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{133.395,5.0,8.0},false},
  {'COL_Terrain_078','Block',{-1.277,2.2,333.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{147.754,5.0,8.0},false},
  {'COL_Terrain_079','Block',{-4.542,2.2,338.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{165.167,5.0,8.0},false},
  {'COL_Terrain_080','Block',{-7.103,2.2,343.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{178.623,5.0,8.0},false},
  {'COL_Terrain_081','Block',{-5.645,2.2,348.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{184.041,5.0,8.0},false},
  {'COL_Terrain_082','Block',{-4.189,2.2,353.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{189.461,5.0,8.0},false},
  {'COL_Terrain_083','Block',{52.325,2.2,358.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{84.767,5.0,8.0},false},
  {'COL_Terrain_084','Block',{-55.057,2.2,358.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{90.231,5.0,8.0},false},
  {'COL_Terrain_085','Block',{-112.034,2.2,358.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.741,5.0,8.0},false},
  {'COL_Terrain_086','Block',{62.831,2.2,363.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{74.3,5.0,8.0},false},
  {'COL_Terrain_087','Block',{-63.554,2.2,363.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{75.745,5.0,8.0},false},
  {'COL_Terrain_088','Block',{-115.254,2.2,363.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.302,5.0,8.0},false},
  {'COL_Terrain_089','Block',{69.988,2.2,368.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{71.524,5.0,8.0},false},
  {'COL_Terrain_090','Block',{-68.799,2.2,368.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{69.146,5.0,8.0},false},
  {'COL_Terrain_091','Block',{-118.474,2.2,368.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{5.863,5.0,8.0},false},
  {'COL_Terrain_092','Block',{75.965,2.2,373.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{71.108,5.0,8.0},false},
  {'COL_Terrain_093','Block',{-72.866,2.2,373.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{64.911,5.0,8.0},false},
  {'COL_Terrain_094','Block',{-121.693,2.2,373.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{8.423,5.0,8.0},false},
  {'COL_Terrain_095','Block',{81.25,2.2,378.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{72.078,5.0,8.0},false},
  {'COL_Terrain_096','Block',{-76.241,2.2,378.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{62.061,5.0,8.0},false},
  {'COL_Terrain_097','Block',{-124.332,2.2,378.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.729,5.0,8.0},false},
  {'COL_Terrain_098','Block',{86.052,2.2,383.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{74.012,5.0,8.0},false},
  {'COL_Terrain_099','Block',{-78.907,2.2,383.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{59.722,5.0,8.0},false},
  {'COL_Terrain_100','Block',{-125.88,2.2,383.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{13.009,5.0,8.0},false},
  {'COL_Terrain_101','Block',{89.961,2.2,388.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{75.671,5.0,8.0},false},
  {'COL_Terrain_102','Block',{-80.902,2.2,388.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{57.553,5.0,8.0},false},
  {'COL_Terrain_103','Block',{-127.428,2.2,388.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.288,5.0,8.0},false},
  {'COL_Terrain_104','Block',{93.024,2.2,393.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{76.879,5.0,8.0},false},
  {'COL_Terrain_105','Block',{-82.586,2.2,393.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{56.005,5.0,8.0},false},
  {'COL_Terrain_106','Block',{-128.976,2.2,393.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{15.568,5.0,8.0},false},
  {'COL_Terrain_107','Block',{95.812,2.2,398.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{78.635,5.0,8.0},false},
  {'COL_Terrain_108','Block',{-83.997,2.2,398.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{55.004,5.0,8.0},false},
  {'COL_Terrain_109','Block',{-130.387,2.2,398.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{17.119,5.0,8.0},false},
  {'COL_Terrain_110','Block',{98.345,2.2,403.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{80.904,5.0,8.0},false},
  {'COL_Terrain_111','Block',{-85.067,2.2,403.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{54.349,5.0,8.0},false},
  {'COL_Terrain_112','Block',{-131.544,2.2,403.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{19.181,5.0,8.0},false},
  {'COL_Terrain_113','Block',{100.659,2.2,408.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{83.609,5.0,8.0},false},
  {'COL_Terrain_114','Block',{-85.61,2.2,408.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.512,5.0,8.0},false},
  {'COL_Terrain_115','Block',{-132.7,2.2,408.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{21.243,5.0,8.0},false},
  {'COL_Terrain_116','Block',{102.753,2.2,413.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{86.754,5.0,8.0},false},
  {'COL_Terrain_117','Block',{-85.934,2.2,413.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.115,5.0,8.0},false},
  {'COL_Terrain_118','Block',{-133.375,2.2,413.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{22.34,5.0,8.0},false},
  {'COL_Terrain_119','Block',{104.09,2.2,418.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{89.182,3.6,8.0},false},
  {'COL_Terrain_121','Block',{-133.815,2.2,418.2},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{23.039,3.6,8.0},false},
  {'COL_Terrain_122','Block',{0.0,0.2,362.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{47.727,5.0,6.0},false},
  {'COL_Terrain_123','Block',{0.0,0.2,367.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{66.235,5.0,6.0},false},
  {'COL_Terrain_124','Block',{0.0,0.2,372.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{79.283,5.0,6.0},false},
  {'COL_Terrain_125','Block',{0.0,0.2,377.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{89.321,5.0,6.0},false},
  {'COL_Terrain_126','Block',{0.0,0.2,382.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{97.424,5.0,6.0},false},
  {'COL_Terrain_127','Block',{0.0,0.2,387.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{103.823,5.0,6.0},false},
  {'COL_Terrain_128','Block',{0.0,0.2,392.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{109.031,5.0,6.0},false},
  {'COL_Terrain_129','Block',{0.0,0.2,397.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{113.093,5.0,6.0},false},
  {'COL_Terrain_130','Block',{0.0,0.2,402.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{116.112,5.0,6.0},false},
  {'COL_Terrain_131','Block',{0.0,0.2,407.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{118.246,5.0,6.0},false},
  {'COL_Terrain_132','Block',{0.0,0.2,412.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{119.534,5.0,6.0},false},
  {'COL_Terrain_133','Block',{-0.0,0.2,420.037},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{119.999,10.0,6.0},false},
  {'COL_Terrain_135','Block',{-0.0,0.2,427.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{119.518,5.0,6.0},false},
  {'COL_Terrain_136','Block',{-0.0,0.2,432.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{118.22,5.0,6.0},false},
  {'COL_Terrain_137','Block',{-0.0,0.2,437.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{116.075,5.0,6.0},false},
  {'COL_Terrain_138','Block',{-0.0,0.2,442.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{113.046,5.0,6.0},false},
  {'COL_Terrain_139','Block',{-0.0,0.2,447.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{108.96,5.0,6.0},false},
  {'COL_Terrain_140','Block',{-0.0,0.2,452.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{103.739,5.0,6.0},false},
  {'COL_Terrain_141','Block',{-0.0,0.2,457.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{97.326,5.0,6.0},false},
  {'COL_Terrain_142','Block',{-0.0,0.2,462.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{89.189,5.0,6.0},false},
  {'COL_Terrain_143','Block',{-0.0,0.2,467.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{79.109,5.0,6.0},false},
  {'COL_Terrain_144','Block',{-0.0,0.2,472.537},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{66.001,5.0,6.0},false},
  {'COL_Terrain_145','Block',{-0.0,0.2,477.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{47.399,4.927,6.0},false},
  {'COL_Terrain_146','Block',{-70.848,6.45,424.644},{-0.998,0.0,0.065},{0.065,0.0,0.998},{22.0,11.149,7.5},false},
  {'COL_Terrain_147','Block',{-69.636,6.45,433.851},{-0.981,0.0,0.195},{0.195,0.0,0.981},{22.0,11.149,7.5},false},
  {'COL_Terrain_148','Block',{-67.232,6.45,442.822},{-0.947,0.0,0.321},{0.321,0.0,0.947},{22.0,11.149,7.5},false},
  {'COL_Terrain_149','Block',{-63.678,6.45,451.402},{-0.897,0.0,0.442},{0.442,0.0,0.897},{22.0,11.149,7.5},false},
  {'COL_Terrain_150','Block',{-59.034,6.45,459.445},{-0.831,0.0,0.556},{0.556,0.0,0.831},{22.0,11.149,7.5},false},
  {'COL_Terrain_151','Block',{-53.381,6.45,466.814},{-0.752,0.0,0.659},{0.659,0.0,0.752},{22.0,11.149,7.5},false},
  {'COL_Terrain_152','Block',{-46.814,6.45,473.381},{-0.659,0.0,0.752},{0.752,0.0,0.659},{22.0,11.149,7.5},false},
  {'COL_Terrain_153','Block',{-39.445,6.45,479.034},{-0.556,0.0,0.831},{0.831,0.0,0.556},{22.0,11.149,7.5},false},
  {'COL_Terrain_154','Block',{-31.403,6.45,483.678},{-0.442,0.0,0.897},{0.897,0.0,0.442},{22.0,11.149,7.5},false},
  {'COL_Terrain_155','Block',{-22.822,6.45,487.232},{-0.321,0.0,0.947},{0.947,0.0,0.321},{22.0,11.149,7.5},false},
  {'COL_Terrain_156','Block',{-13.851,6.45,489.636},{-0.195,0.0,0.981},{0.981,0.0,0.195},{22.0,11.149,7.5},false},
  {'COL_Terrain_157','Block',{-4.644,6.45,490.848},{-0.065,0.0,0.998},{0.998,0.0,0.065},{22.0,11.149,7.5},false},
  {'COL_Terrain_158','Block',{4.644,6.45,490.848},{0.065,0.0,0.998},{0.998,0.0,-0.065},{22.0,11.149,7.5},false},
  {'COL_Terrain_159','Block',{13.851,6.45,489.636},{0.195,0.0,0.981},{0.981,0.0,-0.195},{22.0,11.149,7.5},false},
  {'COL_Terrain_160','Block',{22.822,6.45,487.232},{0.321,0.0,0.947},{0.947,0.0,-0.321},{22.0,11.149,7.5},false},
  {'COL_Terrain_161','Block',{31.402,6.45,483.678},{0.442,0.0,0.897},{0.897,0.0,-0.442},{22.0,11.149,7.5},false},
  {'COL_Terrain_162','Block',{39.445,6.45,479.034},{0.556,0.0,0.831},{0.831,0.0,-0.556},{22.0,11.149,7.5},false},
  {'COL_Terrain_163','Block',{46.814,6.45,473.381},{0.659,0.0,0.752},{0.752,0.0,-0.659},{22.0,11.149,7.5},false},
  {'COL_Terrain_164','Block',{53.381,6.45,466.814},{0.752,0.0,0.659},{0.659,0.0,-0.752},{22.0,11.149,7.5},false},
  {'COL_Terrain_165','Block',{59.034,6.45,459.445},{0.831,0.0,0.556},{0.556,0.0,-0.831},{22.0,11.149,7.5},false},
  {'COL_Terrain_166','Block',{63.678,6.45,451.402},{0.897,0.0,0.442},{0.442,0.0,-0.897},{22.0,11.149,7.5},false},
  {'COL_Terrain_167','Block',{67.232,6.45,442.822},{0.947,0.0,0.321},{0.321,0.0,-0.947},{22.0,11.149,7.5},false},
  {'COL_Terrain_168','Block',{69.636,6.45,433.851},{0.981,0.0,0.195},{0.195,0.0,-0.981},{22.0,11.149,7.5},false},
  {'COL_Terrain_169','Block',{70.848,6.45,424.644},{0.998,0.0,0.065},{0.065,0.0,-0.998},{22.0,11.149,7.5},false},
  {'COL_Terrain_170','Block',{70.848,6.45,415.356},{0.998,0.0,-0.065},{-0.065,0.0,-0.998},{22.0,11.149,7.5},false},
  {'COL_Terrain_171','Block',{69.636,6.45,406.149},{0.981,0.0,-0.195},{-0.195,0.0,-0.981},{22.0,11.149,7.5},false},
  {'COL_Terrain_172','Block',{67.232,6.45,397.178},{0.947,0.0,-0.321},{-0.321,0.0,-0.947},{22.0,11.149,7.5},false},
  {'COL_Terrain_173','Block',{63.678,6.45,388.598},{0.897,0.0,-0.442},{-0.442,0.0,-0.897},{22.0,11.149,7.5},false},
  {'COL_Terrain_174','Block',{59.034,6.45,380.555},{0.831,0.0,-0.556},{-0.556,0.0,-0.831},{22.0,11.149,7.5},false},
  {'COL_Terrain_175','Block',{53.381,6.45,373.186},{0.752,0.0,-0.659},{-0.659,0.0,-0.752},{22.0,11.149,7.5},false},
  {'COL_Terrain_176','Block',{46.814,6.45,366.619},{0.659,0.0,-0.752},{-0.752,0.0,-0.659},{22.0,11.149,7.5},false},
  {'COL_Terrain_177','Block',{39.445,6.45,360.966},{0.556,0.0,-0.831},{-0.831,0.0,-0.556},{22.0,11.149,7.5},false},
  {'COL_Terrain_178','Block',{31.403,6.45,356.322},{0.442,0.0,-0.897},{-0.897,0.0,-0.442},{22.0,11.149,7.5},false},
  {'COL_Terrain_179','Block',{22.822,6.45,352.768},{0.321,0.0,-0.947},{-0.947,0.0,-0.321},{22.0,11.149,7.5},false},
  {'COL_Terrain_180','Block',{13.851,6.45,350.364},{0.195,0.0,-0.981},{-0.981,0.0,-0.195},{22.0,11.149,7.5},false},
  {'COL_Terrain_181','Block',{4.644,6.45,349.152},{0.065,0.0,-0.998},{-0.998,0.0,-0.065},{22.0,11.149,7.5},false},
  {'COL_Terrain_182','Block',{-4.644,6.45,349.152},{-0.065,0.0,-0.998},{-0.998,0.0,0.065},{22.0,11.149,7.5},false},
  {'COL_Terrain_183','Block',{-13.851,6.45,350.364},{-0.195,0.0,-0.981},{-0.981,0.0,0.195},{22.0,11.149,7.5},false},
  {'COL_Terrain_184','Block',{-22.822,6.45,352.768},{-0.321,0.0,-0.947},{-0.947,0.0,0.321},{22.0,11.149,7.5},false},
  {'COL_Terrain_185','Block',{-31.402,6.45,356.322},{-0.442,0.0,-0.897},{-0.897,0.0,0.442},{22.0,11.149,7.5},false},
  {'COL_Terrain_186','Block',{-39.445,6.45,360.966},{-0.556,0.0,-0.831},{-0.831,0.0,0.556},{22.0,11.149,7.5},false},
  {'COL_Terrain_187','Block',{-46.814,6.45,366.619},{-0.659,0.0,-0.752},{-0.752,0.0,0.659},{22.0,11.149,7.5},false},
  {'COL_Terrain_188','Block',{-53.381,6.45,373.186},{-0.752,0.0,-0.659},{-0.659,0.0,0.752},{22.0,11.149,7.5},false},
  {'COL_Terrain_189','Block',{-59.034,6.45,380.555},{-0.831,0.0,-0.556},{-0.556,0.0,0.831},{22.0,11.149,7.5},false},
  {'COL_Terrain_190','Block',{-63.678,6.45,388.598},{-0.897,0.0,-0.442},{-0.442,0.0,0.897},{22.0,11.149,7.5},false},
  {'COL_Terrain_191','Block',{-67.232,6.45,397.178},{-0.947,0.0,-0.321},{-0.321,0.0,0.947},{22.0,11.149,7.5},false},
  {'COL_Terrain_192','Block',{-69.636,6.45,406.149},{-0.981,0.0,-0.195},{-0.195,0.0,0.981},{22.0,11.149,7.5},false},
  {'COL_Terrain_193','Block',{-70.848,6.45,415.356},{-0.998,0.0,-0.065},{-0.065,0.0,0.998},{22.0,11.149,7.5},false},
  {'COL_Terrain_194','Block',{-73.671,7.7,461.894},{-0.869,0.0,0.494},{0.494,0.0,0.869},{6.5,11.55,5.0},false},
  {'COL_Terrain_195','Block',{-67.795,7.7,470.856},{-0.8,0.0,0.6},{0.6,0.0,0.8},{6.5,11.55,5.0},false},
  {'COL_Terrain_196','Block',{-60.835,7.7,479.005},{-0.718,0.0,0.696},{0.696,0.0,0.718},{6.5,11.55,5.0},false},
  {'COL_Terrain_197','Block',{-52.903,7.7,486.211},{-0.624,0.0,0.781},{0.781,0.0,0.624},{6.5,11.55,5.0},false},
  {'COL_Terrain_198','Block',{-44.124,7.7,492.358},{-0.521,0.0,0.854},{0.854,0.0,0.521},{6.5,11.55,5.0},false},
  {'COL_Terrain_199','Block',{-34.64,7.7,497.348},{-0.409,0.0,0.913},{0.913,0.0,0.409},{6.5,11.55,5.0},false},
  {'COL_Terrain_200','Block',{-24.602,7.7,501.101},{-0.29,0.0,0.957},{0.957,0.0,0.29},{6.5,11.55,5.0},false},
  {'COL_Terrain_201','Block',{-14.17,7.7,503.557},{-0.167,0.0,0.986},{0.986,0.0,0.167},{6.5,11.55,5.0},false},
  {'COL_Terrain_202','Block',{-3.512,7.7,504.677},{-0.041,0.0,0.999},{0.999,0.0,0.041},{6.5,11.55,5.0},false},
  {'COL_Terrain_203','Block',{7.202,7.7,504.443},{0.085,0.0,0.996},{0.996,0.0,-0.085},{6.5,11.55,5.0},false},
  {'COL_Terrain_204','Block',{17.801,7.7,502.859},{0.21,0.0,0.978},{0.978,0.0,-0.21},{6.5,11.55,5.0},false},
  {'COL_Terrain_205','Block',{28.116,7.7,499.95},{0.332,0.0,0.943},{0.943,0.0,-0.332},{6.5,11.55,5.0},false},
  {'COL_Terrain_206','Block',{37.981,7.7,495.763},{0.448,0.0,0.894},{0.894,0.0,-0.448},{6.5,11.55,5.0},false},
  {'COL_Terrain_207','Block',{47.238,7.7,490.364},{0.557,0.0,0.83},{0.83,0.0,-0.557},{6.5,11.55,5.0},false},
  {'COL_Terrain_208','Block',{55.74,7.7,483.84},{0.658,0.0,0.753},{0.753,0.0,-0.658},{6.5,11.55,5.0},false},
  {'COL_Terrain_209','Block',{63.351,7.7,476.295},{0.748,0.0,0.664},{0.664,0.0,-0.748},{6.5,11.55,5.0},false},
  {'COL_Terrain_210','Block',{69.949,7.7,467.85},{0.825,0.0,0.565},{0.565,0.0,-0.825},{6.5,11.55,5.0},false},
  {'COL_Terrain_211','Block',{75.429,7.7,458.64},{0.89,0.0,0.456},{0.456,0.0,-0.89},{6.5,11.55,5.0},false},
  {'COL_Terrain_212','Block',{79.702,7.7,448.812},{0.94,0.0,0.34},{0.34,0.0,-0.94},{6.5,11.55,5.0},false},
  {'COL_Terrain_213','Block',{82.701,7.7,438.524},{0.976,0.0,0.219},{0.219,0.0,-0.976},{6.5,11.55,5.0},false},
  {'COL_Terrain_214','Block',{84.377,7.7,427.939},{0.996,0.0,0.094},{0.094,0.0,-0.996},{6.5,11.55,5.0},false},
  {'COL_Terrain_215','Block',{84.705,7.7,417.227},{0.999,0.0,-0.033},{-0.033,0.0,-0.999},{6.5,11.55,5.0},false},
  {'COL_Terrain_216','Block',{83.677,7.7,406.56},{0.987,0.0,-0.159},{-0.159,0.0,-0.987},{6.5,11.55,5.0},false},
  {'COL_Terrain_217','Block',{81.312,7.7,396.107},{0.959,0.0,-0.282},{-0.282,0.0,-0.959},{6.5,11.55,5.0},false},
  {'COL_Terrain_218','Block',{115.557,10.7,381.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.899,3.0,11.0},false},
  {'COL_Terrain_219','Block',{113.167,10.7,384.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{23.603,3.0,11.0},false},
  {'COL_Terrain_220','Block',{110.334,10.7,387.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{34.421,3.0,11.0},false},
  {'COL_Terrain_221','Block',{107.312,10.7,390.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{44.864,3.0,11.0},false},
  {'COL_Terrain_222','Block',{108.154,10.7,393.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{47.58,3.0,11.0},false},
  {'COL_Terrain_223','Block',{109.661,10.7,396.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{48.966,3.0,11.0},false},
  {'COL_Terrain_224','Block',{111.119,10.7,399.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{50.451,3.0,11.0},false},
  {'COL_Terrain_225','Block',{112.537,10.7,402.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{52.015,3.0,11.0},false},
  {'COL_Terrain_226','Block',{113.873,10.7,405.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{53.743,3.0,11.0},false},
  {'COL_Terrain_227','Block',{115.177,10.7,408.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{55.536,3.0,11.0},false},
  {'COL_Terrain_228','Block',{116.422,10.7,411.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{57.444,3.0,11.0},false},
  {'COL_Terrain_229','Block',{117.61,10.7,414.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{59.469,3.0,11.0},false},
  {'COL_Terrain_230','Block',{118.288,10.7,417.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{60.594,3.0,11.0},false},
  {'COL_Terrain_231','Block',{118.704,10.7,420.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{61.429,3.0,11.0},false},
  {'COL_Terrain_232','Block',{119.098,10.7,423.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{62.308,3.0,11.0},false},
  {'COL_Terrain_233','Block',{119.455,10.7,426.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{63.26,3.0,11.0},false},
  {'COL_Terrain_234','Block',{123.882,10.7,429.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{56.073,3.0,11.0},false},
  {'COL_Terrain_235','Block',{124.289,10.7,432.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{56.924,3.0,11.0},false},
  {'COL_Terrain_236','Block',{124.442,10.7,435.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{58.287,3.0,11.0},false},
  {'COL_Terrain_237','Block',{124.594,10.7,438.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{59.649,3.0,11.0},false},
  {'COL_Terrain_238','Block',{124.746,10.7,441.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{61.011,3.0,11.0},false},
  {'COL_Terrain_239','Block',{124.898,10.7,444.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{62.374,3.0,11.0},false},
  {'COL_Terrain_240','Block',{88.958,10.7,444.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{8.149,3.0,11.0},false},
  {'COL_Terrain_241','Block',{120.475,10.7,447.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{72.887,3.0,11.0},false},
  {'COL_Terrain_242','Block',{120.383,10.7,450.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{74.738,3.0,11.0},false},
  {'COL_Terrain_243','Block',{119.953,10.7,453.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{76.094,3.0,11.0},false},
  {'COL_Terrain_244','Block',{119.344,10.7,456.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{77.313,3.0,11.0},false},
  {'COL_Terrain_245','Block',{118.644,10.7,459.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{78.712,3.0,11.0},false},
  {'COL_Terrain_246','Block',{117.888,10.7,462.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{80.224,3.0,11.0},false},
  {'COL_Terrain_247','Block',{-81.027,10.7,462.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{6.505,3.0,11.0},false},
  {'COL_Terrain_248','Block',{117.071,10.7,465.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{81.858,3.0,11.0},false},
  {'COL_Terrain_249','Block',{-83.274,10.7,465.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.314,3.0,11.0},false},
  {'COL_Terrain_250','Block',{116.152,10.7,468.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{83.696,3.0,11.0},false},
  {'COL_Terrain_251','Block',{-85.452,10.7,468.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{22.259,3.0,11.0},false},
  {'COL_Terrain_252','Block',{115.151,10.7,471.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{85.697,3.0,11.0},false},
  {'COL_Terrain_253','Block',{-87.525,10.7,471.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{30.414,3.0,11.0},false},
  {'COL_Terrain_254','Block',{114.067,10.7,474.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{87.865,3.0,11.0},false},
  {'COL_Terrain_255','Block',{-89.065,10.7,474.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{37.87,3.0,11.0},false},
  {'COL_Terrain_256','Block',{112.89,10.7,477.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{90.221,3.0,11.0},false},
  {'COL_Terrain_257','Block',{-87.877,10.7,477.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{40.245,3.0,11.0},false},
  {'COL_Terrain_258','Block',{111.592,10.7,480.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{92.816,3.0,11.0},false},
  {'COL_Terrain_259','Block',{-86.583,10.7,480.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{42.835,3.0,11.0},false},
  {'COL_Terrain_260','Block',{110.157,10.7,483.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{95.686,3.0,11.0},false},
  {'COL_Terrain_261','Block',{-85.164,10.7,483.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{45.671,3.0,11.0},false},
  {'COL_Terrain_262','Block',{108.802,10.7,486.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{98.396,3.0,11.0},false},
  {'COL_Terrain_263','Block',{-84.754,10.7,486.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{46.492,3.0,11.0},false},
  {'COL_Terrain_264','Block',{109.974,10.7,489.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{96.052,3.0,11.0},false},
  {'COL_Terrain_265','Block',{-85.926,10.7,491.056},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{44.149,6.0,11.0},false},
  {'COL_Terrain_266','Block',{110.579,10.7,492.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{94.841,3.0,11.0},false},
  {'COL_Terrain_268','Block',{109.691,10.7,495.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{96.251,3.0,11.0},false},
  {'COL_Terrain_269','Block',{49.417,10.7,495.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.017,3.0,11.0},false},
  {'COL_Terrain_270','Block',{-48.461,10.7,495.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.123,3.0,11.0},false},
  {'COL_Terrain_271','Block',{-84.783,10.7,495.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{46.434,3.0,11.0},false},
  {'COL_Terrain_272','Block',{107.499,10.7,498.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{99.546,3.0,11.0},false},
  {'COL_Terrain_273','Block',{48.082,10.7,498.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{11.375,3.0,11.0},false},
  {'COL_Terrain_274','Block',{-47.101,10.7,498.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.53,3.0,11.0},false},
  {'COL_Terrain_275','Block',{-82.863,10.7,498.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{50.274,3.0,11.0},false},
  {'COL_Terrain_276','Block',{96.542,10.7,501.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{120.368,3.0,11.0},false},
  {'COL_Terrain_277','Block',{-72.191,10.7,501.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{71.618,3.0,11.0},false},
  {'COL_Terrain_278','Block',{92.542,10.7,504.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{127.278,3.0,11.0},false},
  {'COL_Terrain_279','Block',{-68.415,10.7,504.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{79.17,3.0,11.0},false},
  {'COL_Terrain_280','Block',{86.822,10.7,507.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{137.626,3.0,11.0},false},
  {'COL_Terrain_281','Block',{-63.007,10.7,507.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{89.987,3.0,11.0},false},
  {'COL_Terrain_282','Block',{80.845,10.7,510.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{148.49,3.0,11.0},false},
  {'COL_Terrain_283','Block',{-57.3,10.7,513.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{101.4,9.0,11.0},false},
  {'COL_Terrain_284','Block',{80.572,10.7,513.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{147.944,3.0,11.0},false},
  {'COL_Terrain_286','Block',{80.299,10.7,516.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{147.399,3.0,11.0},false},
  {'COL_Terrain_288','Block',{22.727,10.7,519.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{261.453,3.0,11.0},false},
  {'COL_Terrain_289','Block',{22.454,10.7,522.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{260.908,3.0,11.0},false},
  {'COL_Terrain_290','Block',{22.181,10.7,525.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{260.363,3.0,11.0},false},
  {'COL_Terrain_291','Block',{21.909,10.7,528.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{259.817,3.0,11.0},false},
  {'COL_Terrain_292','Block',{21.636,10.7,531.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{259.272,3.0,11.0},false},
  {'COL_Terrain_293','Block',{21.363,10.7,534.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{258.726,3.0,11.0},false},
  {'COL_Terrain_294','Block',{21.09,10.7,537.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{258.181,3.0,11.0},false},
  {'COL_Terrain_295','Block',{20.599,10.7,540.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{257.198,3.0,11.0},false},
  {'COL_Terrain_296','Block',{19.999,10.7,543.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{255.998,3.0,11.0},false},
  {'COL_Terrain_297','Block',{19.399,10.7,546.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{254.798,3.0,11.0},false},
  {'COL_Terrain_298','Block',{18.799,10.7,549.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{253.598,3.0,11.0},false},
  {'COL_Terrain_299','Block',{18.199,10.7,552.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{252.398,3.0,11.0},false},
  {'COL_Terrain_300','Block',{17.599,10.7,555.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{251.198,3.0,11.0},false},
  {'COL_Terrain_301','Block',{16.999,10.7,558.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{249.998,3.0,11.0},false},
  {'COL_Terrain_302','Block',{16.399,10.7,561.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{248.798,3.0,11.0},false},
  {'COL_Terrain_303','Block',{15.799,10.7,564.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{247.598,3.0,11.0},false},
  {'COL_Terrain_304','Block',{15.199,10.7,567.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{246.398,3.0,11.0},false},
  {'COL_Terrain_305','Block',{14.599,10.7,570.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{245.198,3.0,11.0},false},
  {'COL_Terrain_306','Block',{13.999,10.7,573.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{243.998,3.0,11.0},false},
  {'COL_Terrain_307','Block',{13.399,10.7,576.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{242.798,3.0,11.0},false},
  {'COL_Terrain_308','Block',{12.497,10.7,579.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{240.994,3.0,11.0},false},
  {'COL_Terrain_309','Block',{10.997,10.7,582.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{237.994,3.0,11.0},false},
  {'COL_Terrain_310','Block',{9.497,10.7,585.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{234.994,3.0,11.0},false},
  {'COL_Terrain_311','Block',{7.997,10.7,588.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{231.994,3.0,11.0},false},
  {'COL_Terrain_312','Block',{6.497,10.7,591.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{228.994,3.0,11.0},false},
  {'COL_Terrain_313','Block',{5.265,10.7,594.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{225.457,3.0,11.0},false},
  {'COL_Terrain_314','Block',{4.565,10.7,597.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{220.857,3.0,11.0},false},
  {'COL_Terrain_315','Block',{3.865,10.7,600.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{216.257,3.0,11.0},false},
  {'COL_Terrain_316','Block',{3.165,10.7,603.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{211.657,3.0,11.0},false},
  {'COL_Terrain_317','Block',{2.465,10.7,606.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{207.057,3.0,11.0},false},
  {'COL_Terrain_318','Block',{1.856,10.7,609.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{198.539,3.0,11.0},false},
  {'COL_Terrain_319','Block',{1.428,10.7,612.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{182.253,3.0,11.0},false},
  {'COL_Terrain_320','Block',{0.999,10.7,615.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{165.967,3.0,11.0},false},
  {'COL_Terrain_321','Block',{0.571,10.7,618.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{149.682,3.0,11.0},false},
  {'COL_Terrain_322','Block',{0.142,10.7,621.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{133.396,3.0,11.0},false},
  {'COL_Terrain_323','Block',{-0.0,10.7,624.556},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{63.808,3.0,11.0},false},
  {'COL_Terrain_324','Block',{-0.0,10.7,627.028},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.944,11.0},false},
  {'COL_Terrain_325','Block',{-80.819,10.7,464.27},{-0.877,0.0,0.48},{0.48,0.0,0.877},{8.3,9.524,11.0},false},
  {'COL_Terrain_326','Block',{-76.272,10.7,471.712},{-0.828,0.0,0.561},{0.561,0.0,0.828},{8.3,9.524,11.0},false},
  {'COL_Terrain_327','Block',{-71.042,10.7,478.691},{-0.771,0.0,0.637},{0.637,0.0,0.771},{8.3,9.524,11.0},false},
  {'COL_Terrain_328','Block',{-65.175,10.7,485.144},{-0.707,0.0,0.707},{0.707,0.0,0.707},{8.3,9.524,11.0},false},
  {'COL_Terrain_329','Block',{-47.128,10.7,499.187},{-0.511,0.0,0.859},{0.859,0.0,0.511},{8.3,10.291,11.0},false},
  {'COL_Terrain_330','Block',{-38.769,10.7,503.598},{-0.421,0.0,0.907},{0.907,0.0,0.421},{8.3,10.291,11.0},false},
  {'COL_Terrain_331','Block',{-30.001,10.7,507.13},{-0.326,0.0,0.946},{0.946,0.0,0.326},{8.3,10.291,11.0},false},
  {'COL_Terrain_332','Block',{-20.918,10.7,509.744},{-0.227,0.0,0.974},{0.974,0.0,0.227},{8.3,10.291,11.0},false},
  {'COL_Terrain_333','Block',{-11.615,10.7,511.415},{-0.126,0.0,0.992},{0.992,0.0,0.126},{8.3,10.291,11.0},false},
  {'COL_Terrain_334','Block',{10.963,10.7,511.496},{0.119,0.0,0.993},{0.993,0.0,-0.119},{8.3,8.915,11.0},false},
  {'COL_Terrain_335','Block',{18.994,10.7,510.171},{0.206,0.0,0.979},{0.979,0.0,-0.206},{8.3,8.915,11.0},false},
  {'COL_Terrain_336','Block',{26.878,10.7,508.143},{0.292,0.0,0.957},{0.957,0.0,-0.292},{8.3,8.915,11.0},false},
  {'COL_Terrain_337','Block',{34.551,10.7,505.427},{0.375,0.0,0.927},{0.927,0.0,-0.375},{8.3,8.915,11.0},false},
  {'COL_Terrain_338','Block',{41.955,10.7,502.045},{0.455,0.0,0.89},{0.89,0.0,-0.455},{8.3,8.915,11.0},false},
  {'COL_Terrain_339','Block',{49.031,10.7,498.023},{0.532,0.0,0.847},{0.847,0.0,-0.532},{8.3,8.915,11.0},false},
  {'COL_Terrain_340','Block',{64.229,10.7,486.078},{0.697,0.0,0.717},{0.717,0.0,-0.697},{8.3,10.038,11.0},false},
  {'COL_Terrain_341','Block',{70.505,10.7,479.336},{0.765,0.0,0.644},{0.644,0.0,-0.765},{8.3,10.038,11.0},false},
  {'COL_Terrain_342','Block',{76.076,10.7,472.001},{0.826,0.0,0.564},{0.564,0.0,-0.826},{8.3,10.038,11.0},false},
  {'COL_Terrain_343','Block',{80.887,10.7,464.146},{0.878,0.0,0.479},{0.479,0.0,-0.878},{8.3,10.038,11.0},false},
  {'COL_Terrain_344','Block',{84.89,10.7,455.851},{0.921,0.0,0.389},{0.389,0.0,-0.921},{8.3,10.038,11.0},false},
  {'COL_Terrain_345','Block',{88.045,10.7,447.197},{0.955,0.0,0.295},{0.295,0.0,-0.955},{8.3,10.038,11.0},false},
  {'COL_Terrain_346','Block',{92.013,10.7,425.03},{0.999,0.0,0.055},{0.055,0.0,-0.999},{8.3,9.044,11.0},false},
  {'COL_Terrain_347','Block',{92.093,10.7,416.767},{0.999,0.0,-0.035},{-0.035,0.0,-0.999},{8.3,9.044,11.0},false},
  {'COL_Terrain_348','Block',{91.433,10.7,408.529},{0.992,0.0,-0.124},{-0.124,0.0,-0.992},{8.3,9.044,11.0},false},
  {'COL_Terrain_349','Block',{90.038,10.7,400.384},{0.977,0.0,-0.213},{-0.213,0.0,-0.977},{8.3,9.044,11.0},false},
  {'COL_Terrain_350','Block',{87.919,10.7,392.397},{0.954,0.0,-0.3},{-0.3,0.0,-0.954},{8.3,9.044,11.0},false},
  {'COL_Terrain_351','Block',{-86.603,10.7,467.137},{-0.878,0.0,0.478},{0.478,0.0,0.878},{5.0,9.436,11.0},false},
  {'COL_Terrain_355','Block',{-64.649,10.7,494.448},{-0.656,0.0,0.755},{0.755,0.0,0.656},{5.0,9.436,11.0},false},
  {'COL_Terrain_356','Block',{-57.751,10.7,499.918},{-0.586,0.0,0.811},{0.811,0.0,0.586},{5.0,9.436,11.0},false},
  {'COL_Terrain_362','Block',{-8.846,10.7,518.202},{-0.09,0.0,0.996},{0.996,0.0,0.09},{5.0,9.436,11.0},false},
  {'COL_Terrain_363','Block',{-0.051,10.7,518.6},{-0.001,0.0,1.0},{1.0,0.0,0.001},{5.0,9.436,11.0},false},
  {'COL_Terrain_364','Block',{8.745,10.7,518.211},{0.089,0.0,0.996},{0.996,0.0,-0.089},{5.0,9.436,11.0},false},
  {'COL_Terrain_370','Block',{57.669,10.7,499.977},{0.585,0.0,0.811},{0.811,0.0,-0.585},{5.0,9.436,11.0},false},
  {'COL_Terrain_371','Block',{64.573,10.7,494.514},{0.655,0.0,0.756},{0.756,0.0,-0.655},{5.0,9.436,11.0},false},
  {'COL_Terrain_378','Block',{95.969,10.7,442.624},{0.973,0.0,0.229},{0.229,0.0,-0.973},{5.0,9.436,11.0},false},
  {'COL_Terrain_379','Block',{97.605,10.7,433.973},{0.99,0.0,0.142},{0.142,0.0,-0.99},{5.0,9.436,11.0},false},
  {'COL_Terrain_384','Block',{94.067,10.7,390.447},{0.954,0.0,-0.3},{-0.3,0.0,-0.954},{5.0,9.436,11.0},false},
  {'COL_Terrain_385','Block',{76.51,18.7,547.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{139.82,3.0,7.0},false},
  {'COL_Terrain_386','Block',{-58.9,18.7,547.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{104.6,3.0,7.0},false},
  {'COL_Terrain_387','Block',{75.91,18.7,550.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{138.62,3.0,7.0},false},
  {'COL_Terrain_388','Block',{-60.4,18.7,550.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{107.6,3.0,7.0},false},
  {'COL_Terrain_389','Block',{13.41,18.7,553.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{261.22,3.0,7.0},false},
  {'COL_Terrain_390','Block',{12.41,18.7,556.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{260.82,3.0,7.0},false},
  {'COL_Terrain_391','Block',{11.81,18.7,559.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{259.62,3.0,7.0},false},
  {'COL_Terrain_392','Block',{11.21,18.7,562.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{258.42,3.0,7.0},false},
  {'COL_Terrain_393','Block',{10.61,18.7,565.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{257.22,3.0,7.0},false},
  {'COL_Terrain_394','Block',{10.172,18.7,568.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{255.695,3.0,7.0},false},
  {'COL_Terrain_395','Block',{9.822,18.7,571.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{253.995,3.0,7.0},false},
  {'COL_Terrain_396','Block',{9.472,18.7,574.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{252.295,3.0,7.0},false},
  {'COL_Terrain_397','Block',{9.122,18.7,577.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{250.595,3.0,7.0},false},
  {'COL_Terrain_398','Block',{8.545,18.7,580.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{247.01,3.0,7.0},false},
  {'COL_Terrain_399','Block',{7.845,18.7,583.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{242.41,3.0,7.0},false},
  {'COL_Terrain_400','Block',{7.145,18.7,586.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{237.81,3.0,7.0},false},
  {'COL_Terrain_401','Block',{6.445,18.7,589.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{233.21,3.0,7.0},false},
  {'COL_Terrain_402','Block',{5.745,18.7,592.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{228.61,3.0,7.0},false},
  {'COL_Terrain_403','Block',{5.045,18.7,595.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{224.01,3.0,7.0},false},
  {'COL_Terrain_404','Block',{4.345,18.7,598.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{219.41,3.0,7.0},false},
  {'COL_Terrain_405','Block',{3.645,18.7,601.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{214.81,3.0,7.0},false},
  {'COL_Terrain_406','Block',{2.945,18.7,604.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{210.21,3.0,7.0},false},
  {'COL_Terrain_407','Block',{2.245,18.7,607.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{205.61,3.0,7.0},false},
  {'COL_Terrain_408','Block',{1.721,18.7,610.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{193.414,3.0,7.0},false},
  {'COL_Terrain_409','Block',{1.293,18.7,613.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{177.129,3.0,7.0},false},
  {'COL_Terrain_410','Block',{0.864,18.7,616.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{160.843,3.0,7.0},false},
  {'COL_Terrain_411','Block',{0.436,18.7,619.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{144.557,3.0,7.0},false},
  {'COL_Terrain_412','Block',{0.007,18.7,622.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{128.271,3.0,7.0},false},
  {'COL_Terrain_413','Block',{-0.0,18.7,625.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{33.6,3.0,7.0},false},
  {'COL_Terrain_414','Block',{-0.0,18.7,627.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.0,7.0},false},
  {'COL_Terrain_415','Block',{-0.0,19.2,550.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{14.0,2.6,6.0},false},
  {'COL_Terrain_416','Block',{2.922,46.6,609.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{210.057,6.0,50.8},false},
  {'COL_Terrain_417','Block',{1.707,46.6,615.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{192.871,6.0,50.8},false},
  {'COL_Terrain_418','Block',{0.85,46.6,621.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{160.3,6.0,50.8},false},
  {'COL_Terrain_419','Block',{-0.0,46.6,626.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{126.4,4.0,50.8},false},
  {'COL_VegTrunk_001','Block',{-40.41,9.7,319.978},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_002','Block',{-35.479,9.7,314.314},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_003','Block',{56.01,9.7,324.632},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_004','Block',{-54.373,9.7,329.588},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_005','Block',{104.311,9.7,376.699},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_006','Block',{101.705,9.7,367.17},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_007','Block',{95.155,9.7,379.89},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_008','Block',{91.431,9.7,369.16},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_009','Block',{82.676,9.7,360.405},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_010','Block',{85.936,9.7,351.115},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_011','Block',{116.756,19.7,403.018},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_012','Block',{120.237,19.7,395.984},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_013','Block',{123.947,19.7,401.345},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_014','Block',{-64.344,9.7,334.881},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_015','Block',{-90.493,9.7,352.329},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_016','Block',{-82.233,9.7,345.693},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_017','Block',{-122.8,9.7,373.954},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_018','Block',{-95.881,9.7,388.232},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_019','Block',{-141.006,9.7,418.077},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_020','Block',{-138.583,9.7,411.55},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_021','Block',{-137.348,9.7,477.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_022','Block',{-144.644,9.7,441.776},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_023','Block',{-126.806,9.7,502.619},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_024','Block',{-134.099,9.7,504.967},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_025','Block',{141.36,19.7,416.232},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_026','Block',{103.254,19.7,407.51},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_027','Block',{110.005,19.7,519.026},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_028','Block',{114.711,19.7,530.221},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_029','Block',{121.577,19.7,521.299},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_030','Block',{123.055,19.7,531.312},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_031','Block',{149.98,19.7,518.051},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_032','Block',{85.957,19.7,507.681},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_033','Block',{22.484,19.7,524.233},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_034','Block',{-21.856,19.7,522.008},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_035','Block',{63.622,19.7,516.964},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_036','Block',{-63.941,19.7,515.214},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_037','Block',{-33.96,25.7,593.376},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_038','Block',{-63.175,25.7,601.584},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_039','Block',{110.87,25.7,566.038},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_040','Block',{-80.071,25.7,559.591},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_041','Block',{-77.163,9.7,337.945},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_042','Block',{-138.761,9.7,425.418},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_043','Block',{-137.198,9.7,486.957},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_044','Block',{-134.121,9.7,497.926},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_045','Block',{-124.341,9.7,520.775},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_046','Block',{152.139,19.7,490.662},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_047','Block',{149.369,19.7,471.735},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_048','Block',{153.389,19.7,454.365},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_049','Block',{131.349,19.7,401.49},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_050','Block',{124.208,19.7,389.049},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_051','Block',{117.788,19.7,384.752},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_052','Block',{76.468,9.7,342.367},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VegTrunk_053','Block',{67.298,9.7,334.484},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.6,1.6,7.0},false},
  {'COL_VillageBanners_001','Block',{11.5,21.7,519.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.9,1.9,11.0},false},
  {'COL_VillageBanners_002','Block',{11.5,22.0,519.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.2,0.6,7.0},false},
  {'COL_VillageBanners_003','Block',{-11.5,21.7,519.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.9,1.9,11.0},false},
  {'COL_VillageBanners_004','Block',{-11.5,22.0,519.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.2,0.6,7.0},false},
  {'COL_VillageHall_001','Block',{-8.503,22.8,560.689},{-0.915,0.0,0.403},{0.403,0.0,0.915},{7.772,1.8,1.2},true},
  {'COL_VillageHall_002','Block',{-14.469,22.8,564.643},{-0.728,0.0,0.686},{0.686,0.0,0.728},{7.772,1.8,1.2},true},
  {'COL_VillageHall_003','Block',{-18.771,22.8,570.363},{-0.457,0.0,0.89},{0.89,0.0,0.457},{7.772,1.8,1.2},true},
  {'COL_VillageHall_004','Block',{-20.912,22.8,577.192},{-0.133,0.0,0.991},{0.991,0.0,0.133},{7.772,1.8,1.2},true},
  {'COL_VillageHall_005','Block',{-20.648,22.8,584.345},{0.206,0.0,0.979},{0.979,0.0,-0.206},{7.772,1.8,1.2},true},
  {'COL_VillageHall_006','Block',{-18.008,22.8,590.997},{0.521,0.0,0.853},{0.853,0.0,-0.521},{7.772,1.8,1.2},true},
  {'COL_VillageHall_007','Block',{-13.296,22.8,596.384},{0.776,0.0,0.63},{0.63,0.0,-0.776},{7.772,1.8,1.2},true},
  {'COL_VillageHall_008','Block',{-7.054,22.8,599.886},{0.942,0.0,0.334},{0.334,0.0,-0.942},{7.772,1.8,1.2},true},
  {'COL_VillageHall_009','Block',{-0.0,22.8,601.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.772,1.8,1.2},true},
  {'COL_VillageHall_010','Block',{7.054,22.8,599.886},{0.942,0.0,-0.334},{-0.334,0.0,-0.942},{7.772,1.8,1.2},true},
  {'COL_VillageHall_011','Block',{13.295,22.8,596.384},{0.776,0.0,-0.63},{-0.63,0.0,-0.776},{7.772,1.8,1.2},true},
  {'COL_VillageHall_012','Block',{18.008,22.8,590.997},{0.521,0.0,-0.853},{-0.853,0.0,-0.521},{7.772,1.8,1.2},true},
  {'COL_VillageHall_013','Block',{20.648,22.8,584.345},{0.206,0.0,-0.979},{-0.979,0.0,-0.206},{7.772,1.8,1.2},true},
  {'COL_VillageHall_014','Block',{20.912,22.8,577.192},{-0.133,0.0,-0.991},{-0.991,0.0,0.133},{7.772,1.8,1.2},true},
  {'COL_VillageHall_015','Block',{18.771,22.8,570.363},{-0.457,0.0,-0.89},{-0.89,0.0,0.457},{7.772,1.8,1.2},true},
  {'COL_VillageHall_016','Block',{14.469,22.8,564.643},{-0.728,0.0,-0.686},{-0.686,0.0,0.728},{7.772,1.8,1.2},true},
  {'COL_VillageHall_017','Block',{8.503,22.8,560.689},{-0.915,0.0,-0.403},{-0.403,0.0,0.915},{7.772,1.8,1.2},true},
  {'COL_VillageHall_018','Block',{-9.321,22.91,582.498},{0.259,0.0,0.966},{0.966,0.0,-0.259},{10.343,19.3,1.42},true},
  {'COL_VillageHall_019','Block',{-6.824,22.91,586.824},{0.707,0.0,0.707},{0.707,0.0,-0.707},{10.343,19.3,1.42},true},
  {'COL_VillageHall_020','Block',{-2.498,22.91,589.321},{0.966,0.0,0.259},{0.259,0.0,-0.966},{10.343,19.3,1.42},true},
  {'COL_VillageHall_021','Block',{2.498,22.91,589.321},{0.966,0.0,-0.259},{-0.259,0.0,-0.966},{10.343,19.3,1.42},true},
  {'COL_VillageHall_022','Block',{6.824,22.91,586.824},{0.707,0.0,-0.707},{-0.707,0.0,-0.707},{10.343,19.3,1.42},true},
  {'COL_VillageHall_023','Block',{9.321,22.91,582.498},{0.259,0.0,-0.966},{-0.966,0.0,-0.259},{10.343,19.3,1.42},true},
  {'COL_VillageHall_024','Block',{9.321,22.91,577.502},{-0.259,0.0,-0.966},{-0.966,0.0,0.259},{10.343,19.3,1.42},true},
  {'COL_VillageHall_025','Block',{6.824,22.91,573.176},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{10.343,19.3,1.42},true},
  {'COL_VillageHall_026','Block',{2.498,22.91,570.679},{-0.966,0.0,-0.259},{-0.259,0.0,0.966},{10.343,19.3,1.42},true},
  {'COL_VillageHall_027','Block',{-2.498,22.91,570.679},{-0.966,0.0,0.259},{0.259,0.0,0.966},{10.343,19.3,1.42},true},
  {'COL_VillageHall_028','Block',{-6.824,22.91,573.176},{-0.707,0.0,0.707},{0.707,0.0,0.707},{10.343,19.3,1.42},true},
  {'COL_VillageHall_029','Block',{-9.321,22.91,577.502},{-0.259,0.0,0.966},{0.966,0.0,0.259},{10.343,19.3,1.42},true},
  {'COL_VillageHall_030','Block',{-0.0,22.5,558.15},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.0,1.7,0.6},true},
  {'COL_VillageHall_031','Block',{-0.0,22.8,561.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.0,5.0,1.2},true},
  {'COL_VillageHall_032','Block',{-8.115,30.75,561.666},{-0.914,0.0,0.405},{0.405,0.0,0.914},{7.388,1.7,14.7},true},
  {'COL_VillageHall_033','Block',{-13.774,30.75,565.43},{-0.727,0.0,0.687},{0.687,0.0,0.727},{7.388,1.7,14.7},true},
  {'COL_VillageHall_034','Block',{-17.85,30.75,570.868},{-0.455,0.0,0.89},{0.89,0.0,0.455},{7.388,1.7,14.7},true},
  {'COL_VillageHall_035','Block',{-19.875,30.75,577.356},{-0.132,0.0,0.991},{0.991,0.0,0.132},{7.388,1.7,14.7},true},
  {'COL_VillageHall_036','Block',{-19.616,30.75,584.147},{0.207,0.0,0.978},{0.978,0.0,-0.207},{7.388,1.7,14.7},true},
  {'COL_VillageHall_037','Block',{-17.104,30.75,590.462},{0.522,0.0,0.853},{0.853,0.0,-0.522},{7.388,1.7,14.7},true},
  {'COL_VillageHall_038','Block',{-12.626,30.75,595.575},{0.777,0.0,0.63},{0.63,0.0,-0.777},{7.388,1.7,14.7},true},
  {'COL_VillageHall_039','Block',{-6.698,30.75,598.898},{0.943,0.0,0.334},{0.334,0.0,-0.943},{7.388,1.7,14.7},true},
  {'COL_VillageHall_040','Block',{-0.0,30.75,600.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.388,1.7,14.7},true},
  {'COL_VillageHall_041','Block',{6.698,30.75,598.898},{0.943,0.0,-0.334},{-0.334,0.0,-0.943},{7.388,1.7,14.7},true},
  {'COL_VillageHall_042','Block',{12.626,30.75,595.575},{0.777,0.0,-0.63},{-0.63,0.0,-0.777},{7.388,1.7,14.7},true},
  {'COL_VillageHall_043','Block',{17.104,30.75,590.462},{0.522,0.0,-0.853},{-0.853,0.0,-0.522},{7.388,1.7,14.7},true},
  {'COL_VillageHall_044','Block',{19.616,30.75,584.147},{0.207,0.0,-0.978},{-0.978,0.0,-0.207},{7.388,1.7,14.7},true},
  {'COL_VillageHall_045','Block',{19.875,30.75,577.356},{-0.132,0.0,-0.991},{-0.991,0.0,0.132},{7.388,1.7,14.7},true},
  {'COL_VillageHall_046','Block',{17.85,30.75,570.868},{-0.455,0.0,-0.89},{-0.89,0.0,0.455},{7.388,1.7,14.7},true},
  {'COL_VillageHall_047','Block',{13.774,30.75,565.43},{-0.727,0.0,-0.687},{-0.687,0.0,0.727},{7.388,1.7,14.7},true},
  {'COL_VillageHall_048','Block',{8.115,30.75,561.666},{-0.914,0.0,-0.405},{-0.405,0.0,0.914},{7.388,1.7,14.7},true},
  {'COL_VillageHall_049','Block',{-0.0,36.95,560.15},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.0,2.1,2.3},true},
  {'COL_VillageHall_050','Block',{-7.097,29.9,560.501},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.2,2.2,13.0},true},
  {'COL_VillageHall_051','Block',{7.097,29.9,560.501},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.2,2.2,13.0},true},
  {'COL_VillageHall_052','Block',{6.634,29.6,562.719},{-0.574,0.0,0.819},{0.819,0.0,0.574},{0.4,4.6,12.2},true},
  {'COL_VillageHall_053','Block',{-6.634,29.6,562.719},{-0.574,0.0,-0.819},{-0.819,0.0,0.574},{0.4,4.6,12.2},true},
  {'COL_VillageHall_054','Block',{-0.0,25.37,586.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.4,4.0,3.5},true},
  {'COL_VillageHall_055','Block',{-11.474,28.07,593.674},{0.766,0.0,0.643},{0.643,0.0,-0.766},{3.6,1.5,8.9},true},
  {'COL_VillageHall_056','Block',{-6.105,28.07,596.773},{0.94,0.0,0.342},{0.342,0.0,-0.94},{3.6,1.5,8.9},true},
  {'COL_VillageHall_057','Block',{6.105,28.07,596.773},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{3.6,1.5,8.9},true},
  {'COL_VillageHall_058','Block',{11.474,28.07,593.674},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{3.6,1.5,8.9},true},
  {'COL_VillageHall_059','Block',{-12.288,30.32,585.09},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_060','Block',{-5.09,30.32,592.288},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_061','Block',{5.09,30.32,592.288},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_062','Block',{12.288,30.32,585.09},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_063','Block',{12.288,30.32,574.91},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_064','Block',{5.09,30.32,567.712},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_065','Block',{-5.09,30.32,567.712},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_066','Block',{-12.288,30.32,574.91},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.7,1.7,13.4},true},
  {'COL_VillageHall_067','Block',{17.53,24.47,576.909},{-0.174,0.0,-0.985},{-0.985,0.0,0.174},{4.4,1.6,1.7},false},
  {'COL_VillageHall_068','Block',{-17.53,24.47,576.909},{-0.174,0.0,0.985},{0.985,0.0,0.174},{4.4,1.6,1.7},false},
  {'COL_VillageRamen_001','Block',{38.0,16.175,527.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{18.8,12.8,1.15},true},
  {'COL_VillageRamen_002','Block',{46.95,23.5,529.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,8.4,13.5},true},
  {'COL_VillageRamen_003','Block',{29.05,23.5,529.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,8.4,13.5},true},
  {'COL_VillageRamen_004','Block',{38.0,23.5,532.95},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{18.8,0.8,13.5},true},
  {'COL_VillageRamen_005','Block',{47.0,23.5,521.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,13.5},true},
  {'COL_VillageRamen_006','Block',{42.5,23.5,521.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,13.5},true},
  {'COL_VillageRamen_007','Block',{33.5,23.5,521.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,13.5},true},
  {'COL_VillageRamen_008','Block',{29.0,23.5,521.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{0.9,0.9,13.5},true},
  {'COL_VillageRamen_009','Block',{38.0,18.45,528.15},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.2,1.7,3.4},true},
  {'COL_VillageRamen_010','Block',{38.1,18.35,531.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{16.6,1.4,3.2},true},
  {'COL_VillageShop_001','Block',{51.833,22.5,576.554},{0.383,0.0,0.924},{0.924,0.0,-0.383},{11.06,13.35,0.6},true},
  {'COL_VillageShop_002','Block',{55.446,22.5,580.167},{0.924,0.0,0.383},{0.383,0.0,-0.924},{11.06,13.35,0.6},true},
  {'COL_VillageShop_003','Block',{60.554,22.5,580.167},{0.924,0.0,-0.383},{-0.383,0.0,-0.924},{11.06,13.35,0.6},true},
  {'COL_VillageShop_004','Block',{64.167,22.5,576.554},{0.383,0.0,-0.924},{-0.924,0.0,-0.383},{11.06,13.35,0.6},true},
  {'COL_VillageShop_005','Block',{64.167,22.5,571.446},{-0.383,0.0,-0.924},{-0.924,0.0,0.383},{11.06,13.35,0.6},true},
  {'COL_VillageShop_006','Block',{60.554,22.5,567.833},{-0.924,0.0,-0.383},{-0.383,0.0,0.924},{11.06,13.35,0.6},true},
  {'COL_VillageShop_007','Block',{55.446,22.5,567.833},{-0.924,0.0,0.383},{0.383,0.0,0.924},{11.06,13.35,0.6},true},
  {'COL_VillageShop_008','Block',{51.833,22.5,571.446},{-0.383,0.0,0.924},{0.924,0.0,0.383},{11.06,13.35,0.6},true},
  {'COL_VillageShop_009','Block',{52.769,22.61,575.7},{0.309,0.0,0.951},{0.951,0.0,-0.309},{7.148,11.0,0.82},true},
  {'COL_VillageShop_010','Block',{54.767,22.61,578.45},{0.809,0.0,0.588},{0.588,0.0,-0.809},{7.148,11.0,0.82},true},
  {'COL_VillageShop_011','Block',{58.0,22.61,579.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.148,11.0,0.82},true},
  {'COL_VillageShop_012','Block',{61.233,22.61,578.45},{0.809,0.0,-0.588},{-0.588,0.0,-0.809},{7.148,11.0,0.82},true},
  {'COL_VillageShop_013','Block',{63.231,22.61,575.7},{0.309,0.0,-0.951},{-0.951,0.0,-0.309},{7.148,11.0,0.82},true},
  {'COL_VillageShop_014','Block',{63.231,22.61,572.3},{-0.309,0.0,-0.951},{-0.951,0.0,0.309},{7.148,11.0,0.82},true},
  {'COL_VillageShop_015','Block',{61.233,22.61,569.55},{-0.809,0.0,-0.588},{-0.588,0.0,0.809},{7.148,11.0,0.82},true},
  {'COL_VillageShop_016','Block',{58.0,22.61,568.5},{-1.0,0.0,0.0},{0.0,0.0,1.0},{7.148,11.0,0.82},true},
  {'COL_VillageShop_017','Block',{54.767,22.61,569.55},{-0.809,0.0,0.588},{0.588,0.0,0.809},{7.148,11.0,0.82},true},
  {'COL_VillageShop_018','Block',{52.769,22.61,572.3},{-0.309,0.0,0.951},{0.951,0.0,0.309},{7.148,11.0,0.82},true},
  {'COL_VillageShop_019','Block',{58.0,22.5,561.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.7,2.6,0.6},true},
  {'COL_VillageShop_020','Block',{58.0,22.35,559.775},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.7,1.25,0.3},true},
  {'COL_VillageShop_021','Block',{50.449,30.85,564.998},{-0.766,0.0,0.643},{0.643,0.0,0.766},{7.16,1.5,16.1},true},
  {'COL_VillageShop_022','Block',{46.883,30.85,570.195},{-0.324,0.0,0.946},{0.946,0.0,0.324},{7.16,1.5,16.1},true},
  {'COL_VillageShop_023','Block',{46.516,30.85,576.486},{0.212,0.0,0.977},{0.977,0.0,-0.212},{7.16,1.5,16.1},true},
  {'COL_VillageShop_024','Block',{49.453,30.85,582.063},{0.686,0.0,0.727},{0.727,0.0,-0.686},{7.16,1.5,16.1},true},
  {'COL_VillageShop_025','Block',{54.849,30.85,585.32},{0.963,0.0,0.268},{0.268,0.0,-0.963},{7.16,1.5,16.1},true},
  {'COL_VillageShop_026','Block',{61.151,30.85,585.32},{0.963,0.0,-0.268},{-0.268,0.0,-0.963},{7.16,1.5,16.1},true},
  {'COL_VillageShop_027','Block',{66.547,30.85,582.063},{0.686,0.0,-0.727},{-0.727,0.0,-0.686},{7.16,1.5,16.1},true},
  {'COL_VillageShop_028','Block',{69.484,30.85,576.486},{0.212,0.0,-0.977},{-0.977,0.0,-0.212},{7.16,1.5,16.1},true},
  {'COL_VillageShop_029','Block',{69.117,30.85,570.195},{-0.324,0.0,-0.946},{-0.946,0.0,0.324},{7.16,1.5,16.1},true},
  {'COL_VillageShop_030','Block',{65.551,30.85,564.998},{-0.766,0.0,-0.643},{-0.643,0.0,0.766},{7.16,1.5,16.1},true},
  {'COL_VillageShop_031','Block',{58.0,37.25,562.35},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.1,2.1,3.3},true},
  {'COL_VillageShop_032','Block',{64.2,29.35,563.261},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.8,1.8,13.1},true},
  {'COL_VillageShop_033','Block',{63.956,29.1,565.656},{-0.707,0.0,0.707},{0.707,0.0,0.707},{0.4,4.4,12.5},true},
  {'COL_VillageShop_034','Block',{51.8,29.35,563.261},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{1.8,1.8,13.1},true},
  {'COL_VillageShop_035','Block',{52.044,29.1,565.656},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{0.4,4.4,12.5},true},
  {'COL_VillageShop_036','Block',{58.0,24.77,578.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{9.6,2.0,3.5},true},
  {'COL_VillageShop_037','Block',{58.0,26.52,584.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.4,0.8,7.0},true},
  {'COL_VillageShop_038','Block',{68.3,26.52,574.0},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{5.2,0.8,7.0},true},
  {'COL_VillageShop_039','Block',{47.7,26.52,574.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{5.2,0.8,7.0},true},
  {'COL_VillageShop_040','Block',{65.722,25.52,580.034},{0.616,0.0,-0.788},{-0.788,0.0,-0.616},{4.2,1.8,5.0},true},
  {'COL_VillageShop_041','Block',{50.277,25.52,580.034},{0.616,0.0,0.788},{0.788,0.0,-0.616},{4.2,1.8,5.0},true},
  {'COL_VillageShop_042','Block',{65.2,24.32,569.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.2,2.2,2.6},false},
  {'COL_VillageShop_043','Block',{50.8,24.32,569.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.2,2.2,2.6},false},
  {'COL_VillageTower_001','Block',{-64.448,22.5,575.728},{0.259,0.0,0.966},{0.966,0.0,-0.259},{7.154,13.35,0.6},false},
  {'COL_VillageTower_002','Block',{-62.72,22.5,578.72},{0.707,0.0,0.707},{0.707,0.0,-0.707},{7.154,13.35,0.6},false},
  {'COL_VillageTower_003','Block',{-59.728,22.5,580.448},{0.966,0.0,0.259},{0.259,0.0,-0.966},{7.154,13.35,0.6},false},
  {'COL_VillageTower_004','Block',{-56.272,22.5,580.448},{0.966,0.0,-0.259},{-0.259,0.0,-0.966},{7.154,13.35,0.6},false},
  {'COL_VillageTower_005','Block',{-53.28,22.5,578.72},{0.707,0.0,-0.707},{-0.707,0.0,-0.707},{7.154,13.35,0.6},false},
  {'COL_VillageTower_006','Block',{-51.552,22.5,575.728},{0.259,0.0,-0.966},{-0.966,0.0,-0.259},{7.154,13.35,0.6},false},
  {'COL_VillageTower_007','Block',{-51.552,22.5,572.272},{-0.259,0.0,-0.966},{-0.966,0.0,0.259},{7.154,13.35,0.6},false},
  {'COL_VillageTower_008','Block',{-53.28,22.5,569.28},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{7.154,13.35,0.6},false},
  {'COL_VillageTower_009','Block',{-56.272,22.5,567.552},{-0.966,0.0,-0.259},{-0.259,0.0,0.966},{7.154,13.35,0.6},false},
  {'COL_VillageTower_010','Block',{-59.728,22.5,567.552},{-0.966,0.0,0.259},{0.259,0.0,0.966},{7.154,13.35,0.6},false},
  {'COL_VillageTower_011','Block',{-62.72,22.5,569.28},{-0.707,0.0,0.707},{0.707,0.0,0.707},{7.154,13.35,0.6},false},
  {'COL_VillageTower_012','Block',{-64.448,22.5,572.272},{-0.259,0.0,0.966},{0.966,0.0,0.259},{7.154,13.35,0.6},false},
  {'COL_VillageTower_013','Block',{-63.728,30.85,576.373},{0.383,0.0,0.924},{0.924,0.0,-0.383},{10.272,12.4,16.1},false},
  {'COL_VillageTower_014','Block',{-60.373,30.85,579.728},{0.924,0.0,0.383},{0.383,0.0,-0.924},{10.272,12.4,16.1},false},
  {'COL_VillageTower_015','Block',{-55.627,30.85,579.728},{0.924,0.0,-0.383},{-0.383,0.0,-0.924},{10.272,12.4,16.1},false},
  {'COL_VillageTower_016','Block',{-52.272,30.85,576.373},{0.383,0.0,-0.924},{-0.924,0.0,-0.383},{10.272,12.4,16.1},false},
  {'COL_VillageTower_017','Block',{-52.272,30.85,571.627},{-0.383,0.0,-0.924},{-0.924,0.0,0.383},{10.272,12.4,16.1},false},
  {'COL_VillageTower_018','Block',{-55.627,30.85,568.272},{-0.924,0.0,-0.383},{-0.383,0.0,0.924},{10.272,12.4,16.1},false},
  {'COL_VillageTower_019','Block',{-60.373,30.85,568.272},{-0.924,0.0,0.383},{0.383,0.0,0.924},{10.272,12.4,16.1},false},
  {'COL_VillageTower_020','Block',{-63.728,30.85,571.627},{-0.383,0.0,0.924},{0.924,0.0,0.383},{10.272,12.4,16.1},false},
  {'COL_VillageTower_021','Block',{-60.0,29.75,593.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{7.0,7.0,15.1},false},
  {'COL_WaterFootbridge_001','Ramp',{-104.967,6.327,381.824},{-0.931,0.324,-0.169},{-0.179,0.0,0.984},{3.7,6.0,1.0},false},
  {'COL_WaterFootbridge_002','Ramp',{-108.37,7.354,381.205},{-0.954,0.243,-0.174},{-0.179,-0.0,0.984},{3.609,6.0,1.0},false},
  {'COL_WaterFootbridge_003','Ramp',{-111.739,7.941,380.593},{-0.98,0.091,-0.178},{-0.179,-0.0,0.984},{3.515,6.0,1.0},false},
  {'COL_WaterFootbridge_004','Ramp',{-115.093,7.941,379.983},{-0.98,-0.091,-0.178},{-0.179,0.0,0.984},{3.515,6.0,1.0},false},
  {'COL_WaterFootbridge_005','Ramp',{-118.462,7.354,379.371},{-0.954,-0.243,-0.174},{-0.179,0.0,0.984},{3.609,6.0,1.0},false},
  {'COL_WaterFootbridge_006','Ramp',{-121.865,6.327,378.752},{-0.931,-0.324,-0.169},{-0.179,-0.0,0.984},{3.7,6.0,1.0},false},
  {'COL_WaterFootbridge_007','Block',{-112.835,9.4,377.09},{-0.984,0.0,-0.179},{-0.179,0.0,0.984},{20.6,0.6,7.4},false},
  {'COL_WaterFootbridge_008','Block',{-113.997,9.4,383.486},{-0.984,0.0,-0.179},{-0.179,0.0,0.984},{20.6,0.6,7.4},false},
  {'COL_WaterWheel_001','Block',{-110.4,10.675,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.4,4.4,9.95},false},
  {'COL_WaterWheel_002','Block',{-125.6,10.675,432.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{3.4,4.4,9.95},false},
  {'COL_GateDBLock_001','GateLock',{-172.368,25.2,592.368},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{16.6,1.4,18.0},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'GATE_DB',{-172.368,16.2,592.368},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['open_w']=16.0,['open_h']=18.0,['deck_w']=18.0,['area_id']=2,['key']='DB',['fwd_x']=-0.7071,['fwd_z']=0.7071}},
  {'GATE_DB_EXIT',{-180.853,16.4,600.853},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['gate']='DB',['fwd_x']=-0.7071,['fwd_z']=0.7071}},
  {'GATE_DB_INTERACT',{-167.418,16.4,587.418},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['gate']='DB',['radius']=10.0,['fwd_x']=-0.7071,['fwd_z']=0.7071}},
  {'GATE_DB_LOCKED',{-172.368,25.2,592.368},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['gate']='DB',['state_default']='locked',['fwd_x']=-0.7071,['fwd_z']=0.7071}},
  {'GATE_DB_OpenFX',{-172.368,25.2,592.368},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['gate']='DB',['state']='unlocked',['fx']='abertura',['fwd_x']=-0.7071,['fwd_z']=0.7071}},
  {'GP_Zone_Pit',{0.0,3.2,420.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['radius']=56.0,['floor']=3.2,['kind']='mining',['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ISLAND_EXIT_Naruto',{-96.0,16.2,516.0},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['width']=18.0,['deck_z']=16.2,['heading_deg']=135.0,['fwd_x']=-0.7071,['fwd_z']=0.7071,['heading_deg_local']=45.0}},
  {'ISLAND_NEXT_ANCHOR',{-192.167,16.2,612.167},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['width']=18.0,['deck_z']=16.2,['clear_h']=22.0,['heading_deg']=135.0,['next_area']=2,['guard']='PROVISORIO: EXIT_AnchorGuard (visual) + COL_ExitAnchorGuard_* (COL), next_island_guard=True',['guard_note']='a integracao da Ilha 2 REMOVE o guarda (visual + COL) quando a ponte seguinte encosta aqui',['fwd_x']=-0.7071,['fwd_z']=0.7071,['heading_deg_local']=45.0}},
  {'NPC_MainHall',{-0.0,23.62,589.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['floor']=23.619999999999997,['fwd_x']=0.0,['fwd_z']=-1.0}},
  {'NPC_Mill',{-103.5,6.5,432.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{['note']='vendedor do posto do minerador (atras do balcao atravessado, olha para a porta oeste)',['fwd_x']=1.0,['fwd_z']=-0.0}},
  {'NPC_Ramen',{38.0,16.75,530.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['floor']=16.75,['fwd_x']=0.0,['fwd_z']=-1.0}},
  {'NPC_WeaponShop',{58.0,23.02,581.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['floor']=23.02,['fwd_x']=0.0,['fwd_z']=-1.0}},
  {'ORE_COMMON_01',{-45.82,3.2,424.01},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_02',{-44.06,3.2,436.22},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_03',{-47.32,3.2,444.74},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_04',{-35.87,3.2,448.79},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_05',{-24.0,3.2,462.91},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_06',{-17.41,3.2,468.14},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_07',{-8.28,3.2,467.48},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_08',{8.88,3.2,470.34},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_09',{11.84,3.2,462.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_10',{22.39,3.2,463.02},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_11',{38.59,3.2,453.7},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_12',{36.0,3.2,445.83},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_13',{44.33,3.2,443.75},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_14',{44.23,3.2,423.77},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_15',{48.32,3.2,415.77},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_16',{48.96,3.2,405.73},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_17',{40.8,3.2,398.76},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_18',{37.82,3.2,389.64},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_19',{23.27,3.2,376.69},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_20',{14.08,3.2,374.47},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_21',{8.66,3.2,367.57},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_22',{-8.7,3.2,375.09},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_23',{-17.46,3.2,373.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_24',{-26.41,3.2,373.49},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_25',{-35.25,3.2,390.19},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_26',{-41.96,3.2,396.37},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_27',{-47.37,3.2,402.59},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_COMMON_28',{-46.29,3.2,410.83},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_01',{-23.25,3.2,430.88},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_02',{-10.89,3.2,442.76},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_03',{10.14,3.2,441.75},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_04',{20.21,3.2,431.62},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_05',{22.55,3.2,411.79},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_06',{10.58,3.2,397.51},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_07',{-10.14,3.2,398.25},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_EPIC_08',{-22.55,3.2,411.79},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_SUPERLEGENDARY_01',{-11.31,3.2,431.31},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_SUPERLEGENDARY_02',{11.31,3.2,408.69},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_01',{-31.82,3.2,421.04},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_02',{-31.6,3.2,441.11},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_03',{-18.89,3.2,448.27},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_04',{-7.41,3.2,457.27},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_05',{6.63,3.2,453.35},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_06',{21.11,3.2,451.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_07',{28.27,3.2,438.89},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_08',{37.24,3.2,433.82},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_09',{33.35,3.2,413.37},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_10',{31.6,3.2,398.89},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_11',{18.89,3.2,391.73},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_12',{7.41,3.2,382.73},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_13',{-6.63,3.2,386.65},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_14',{-21.11,3.2,388.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_15',{-28.27,3.2,401.11},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'ORE_UNCOMMON_16',{-37.27,3.2,412.59},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PATH_ENTRY_CENTER',{0.0,3.2,376.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['waypoints']='0.00,6.20,320.00;0.00,10.20,334.00;0.00,10.20,356.00;0.00,3.20,376.00;0.00,3.20,402.00',['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PATH_ENTRY_CENTER_00',{0.0,6.2,320.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PATH_ENTRY_CENTER_01',{0.0,10.2,334.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PATH_ENTRY_CENTER_02',{0.0,10.2,356.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PATH_ENTRY_CENTER_03',{0.0,3.2,376.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PATH_ENTRY_CENTER_04',{0.0,3.2,402.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PLAYER_INTERACT_MainHall',{-0.0,23.62,582.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['floor']=23.619999999999997,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PLAYER_INTERACT_Mill',{-97.5,6.5,432.0},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{['note']='frente do balcao, no eixo da porta (y 12), dentro do moinho',['fwd_x']=-1.0,['fwd_z']=-0.0}},
  {'PLAYER_INTERACT_Ramen',{38.0,16.75,523.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['floor']=16.75,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PLAYER_INTERACT_WeaponShop',{58.0,23.02,574.9},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['floor']=23.02,['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'PURCHASE_UI_ANCHOR_DB',{-170.6,30.2,590.6},{0.707,0.0,0.707},{0.707,0.0,-0.707},{['gate']='DB',['faces']='approach',['ui']='BillboardGui preco/requisito',['fwd_x']=0.7071,['fwd_z']=-0.7071}},
  {'SUMMON_Interact',{132.59,20.32,455.713},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{['radius']=6.0,['portal_plane_v']=-1.4,['note']='patamar do portal, 1,9 a frente do plano da energia (ProximityPrompt da invocacao)',['fwd_x']=-0.8192,['fwd_z']=-0.5736}},
  {'SUMMON_Main',{133.0,16.2,456.0},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{['face_deg']=-35.0,['height']=60.1,['free_zone_w']=14.0,['note']='raiz da torre de invocacao (+Y local = frente); zona livre na frente: v local em free_zone_v',['star_pivot_x']=135.457,['star_pivot_y']=62.2,['star_pivot_z']=457.721,['fwd_x']=-0.8192,['fwd_z']=-0.5736}},
  {'SUMMON_PlayerPosition',{130.215,20.32,454.05},{-0.574,0.0,0.819},{0.819,0.0,0.574},{['note']='jogador no patamar olhando o portal; camera da animacao atras dele, sobre a escada (livre)',['camera_pos_x']=121.61,['camera_pos_y']=25.7,['camera_pos_z']=448.03,['camera_look_x']=-134.15,['camera_look_y']=36.8,['camera_look_z']=25.7,['fwd_x']=0.8192,['fwd_z']=0.5736}},
  {'WORLD_ENTRY_Naruto',{0.0,6.4,320.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['note']='chegada da ilha (logo depois do portao, olhando o fosso)',['fwd_x']=-0.0,['fwd_z']=1.0}},
  {'WORLD_FROM_LOBBY',{0.0,6.2,222.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{['width']=24.0,['deck_z']=6.2,['note']='ponta do patamar da ponte do lobby (Roblox z 222)',['fwd_x']=-0.0,['fwd_z']=1.0}},
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
  {'L_Entrance_GateLantern_E','POINT',{-7.2,21.7,309.3},{255,206,149},7.7,0.4,false,true},
  {'L_Entrance_GateLantern_W','POINT',{7.2,21.7,309.3},{255,206,149},7.7,0.4,false,true},
  {'L_Entrance_Plaza_E','POINT',{-14.4,10.4,316.5},{255,206,149},7.4,0.39,false,true},
  {'L_Entrance_Plaza_W','POINT',{14.4,10.4,316.5},{255,206,149},7.4,0.39,false,true},
  {'L_Exit_Anchor_L','POINT',{-183.151,25.3,618.566},{255,209,149},7.7,0.4,false,true},
  {'L_Exit_Anchor_R','POINT',{-198.566,25.3,603.151},{255,209,149},7.7,0.4,false,true},
  {'L_GateDB_Barrier','POINT',{-170.246,25.2,590.246},{255,196,118},9.0,0.46,false,false},
  {'L_GateDB_Lantern_L','POINT',{-153.983,20.35,595.196},{255,206,149},7.0,0.38,false,true},
  {'L_GateDB_Lantern_R','POINT',{-175.196,20.35,573.983},{255,206,149},7.0,0.38,false,true},
  {'L_Houses_MillCounter','POINT',{-102.5,16.7,432.0},{255,212,153},9.2,0.47,false,false},
  {'L_Houses_MillDoor','POINT',{-91.6,15.85,438.9},{255,206,144},7.4,0.39,false,false},
  {'L_Houses_MillInterior','POINT',{-97.5,16.2,431.0},{255,212,153},11.6,0.62,false,false},
  {'L_Lantern_Rua_00','POINT',{8.88,22.8,530.505},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_03','POINT',{-13.844,29.049,552.508},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_04','POINT',{29.686,28.8,558.533},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_05','POINT',{-29.686,28.8,558.533},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_06','POINT',{43.476,22.8,536.595},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_08','POINT',{71.124,22.8,518.783},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_09','POINT',{-71.124,22.8,518.783},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_11','POINT',{96.566,22.8,449.561},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_12','POINT',{39.604,28.8,564.553},{255,196,149},7.7,0.4,false,true},
  {'L_Lantern_Rua_13','POINT',{73.314,28.8,562.666},{255,196,149},7.7,0.4,false,true},
  {'L_Mining_Core_Glow','POINT',{0.0,10.2,420.0},{255,234,196},12.2,0.68,false,false},
  {'L_Mining_Gate_N','POINT',{-5.791,15.65,480.624},{255,206,144},7.7,0.4,false,true},
  {'L_Mining_Gate_S','POINT',{5.791,15.65,359.376},{255,206,144},7.7,0.4,false,true},
  {'L_Summon_Lantern_L','POINT',{117.925,23.223,467.418},{255,206,144},9.7,0.5,false,true},
  {'L_Summon_Lantern_R','POINT',{138.573,23.223,437.929},{255,206,144},9.7,0.5,false,true},
  {'L_Summon_Portal','POINT',{131.689,25.2,455.082},{162,191,255},19.1,1.43,false,false},
  {'L_Summon_Star','POINT',{135.457,62.2,457.721},{255,223,158},20.0,1.5,false,false},
  {'L_Village_HallDesk','POINT',{-0.0,33.2,583.0},{255,226,188},17.2,1.18,false,false},
  {'L_Village_HallInterior','POINT',{-0.0,35.8,580.0},{255,221,179},20.0,1.5,false,false},
  {'L_Village_Ramen','POINT',{38.0,26.4,529.5},{255,218,173},15.6,0.99,false,false},
  {'L_Village_ShopInterior','POINT',{58.0,34.7,574.0},{255,223,184},20.0,1.5,false,false},
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
-- chao do vale distante (o plano de 2400 studs do Blender NAO e exportado: era coplanar e dava z-fighting)
do local g = root:FindFirstChild('FAR_GROUND') or Instance.new('Part'); g.Name = 'FAR_GROUND'
  g.Anchored = true; g.CanCollide = false; g.CanTouch = false; g.CanQuery = false; g.CastShadow = false
  g.Size = Vector3.new(2048,2,2048); g.Position = Vector3.new(0.0,-111.0,420.0) + ROOT_OFFSET
  g.Color = Color3.fromRGB(38,128,196); g.Material = Enum.Material.SmoothPlastic
  local sk = root:FindFirstChild('SKYLINE'); g.Parent = sk or root end
-- rede de seguranca: quem cai do lobby volta ao ponto seguro mais proximo (spawn, RESPAWN_*, pes de escada)
local SAFE = {
  {'SAFE_Entrada',{0.0,6.2,320.0}},
  {'SAFE_Anel_S',{0.0,10.2,350.0}},
  {'SAFE_Anel_N',{-0.0,10.2,491.0}},
  {'SAFE_Anel_L',{-71.0,10.2,414.0}},
  {'SAFE_Anel_O',{71.0,10.2,414.0}},
  {'SAFE_Fosso',{0.0,3.2,390.0}},
  {'SAFE_T1',{-0.0,16.2,528.0}},
  {'SAFE_T2',{-0.0,22.2,554.0}},
  {'SAFE_Summon',{112.0,16.5,440.0}},
  {'SAFE_Moinho',{-86.0,8.114,432.0}},
  {'SAFE_Vale_Leste',{-126.0,6.2,410.0}},
  {'SAFE_Ilhota',{-168.125,16.2,588.125}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(420,4,440); v.Position = Vector3.new(0.0,-40.0,430.0) + ROOT_OFFSET
  v:ClearAllChildren()
  for _, s in ipairs(SAFE) do local at = Instance.new('Attachment'); at.Name = s[1]; at.Parent = v
    at.WorldPosition = Vector3.new(s[2][1], s[2][2], s[2][3]) + ROOT_OFFSET end
  v.Parent = root end

-- Script de servidor: personagens no grupo 'Personagens' (atravessam as cascas SoVisual) + rede de quedas
do
  local SSS = game:GetService('ServerScriptService')
  local s = SSS:FindFirstChild('ILHA_NARUTO_Servidor') or Instance.new('Script')
  s.Name = 'ILHA_NARUTO_Servidor'
  s.Source = [==[
-- gerado por montar_ilha_naruto.lua (export_roblox.py) - nao editar a mao
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
local root = workspace:WaitForChild('ILHA_NARUTO', 60)
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
  Lg.GeographicLatitude = -14.894
  Lg.ClockTime = 9.834
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
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (0.42, 0.66, -0.62) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
root.WorldPivot = CFrame.new(ROOT_OFFSET)
-- ===== pecas moveis (VFX_*) =====
local VFX = {
  ['VFX_GATE_DB_Orb_1'] = {p = Vector3.new(-159.922,31.800,600.570), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 4.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_DB_Orb_2'] = {p = Vector3.new(-159.074,27.800,598.024), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_DB_Orb_3'] = {p = Vector3.new(-178.307,28.200,579.074), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 6.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_DB_Orb_4'] = {p = Vector3.new(-180.782,32.200,579.852), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 7.000, bob = 0.600, rate = 0.000},
  ['VFX_SUM_Ring_1'] = {p = Vector3.new(135.457,62.200,457.721), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 2.000, bob = 0.000, rate = 0.000},
  ['VFX_SUM_Ring_2'] = {p = Vector3.new(135.457,62.200,457.721), a = Vector3.new(0.0000,-1.0000,0.0000), rpm = 4.000, bob = 0.000, rate = 0.000},
  ['VFX_SUM_Ring_3'] = {p = Vector3.new(135.457,62.200,457.721), a = Vector3.new(0.0740,0.5300,-0.8450), rpm = 6.000, bob = 0.000, rate = 0.000},
  ['VFX_SUM_Star'] = {p = Vector3.new(135.457,62.200,457.721), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.000, rate = 0.000},
  ['VFX_VIL_MillCamshaft'] = {p = Vector3.new(-105.000,14.200,436.900), a = Vector3.new(-1.0000,0.0000,-0.0000), rpm = 8.333, bob = 0.000, rate = 0.000},
  ['VFX_VIL_MillGear'] = {p = Vector3.new(-118.000,14.200,432.000), a = Vector3.new(-1.0000,0.0000,-0.0000), rpm = -4.000, bob = 0.000, rate = 0.000},
  ['VFX_VIL_MillStamps'] = {p = Vector3.new(-99.000,8.900,438.500), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 0.000, bob = 1.200, rate = 0.278},
  ['VFX_WATER_Wheel'] = {p = Vector3.new(-118.000,15.150,432.000), a = Vector3.new(-1.0000,0.0000,-0.0000), rpm = -4.000, bob = 0.000, rate = 0.000},
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
  if (d:IsA('BasePart') or d:IsA('Model')) and (string.match(d.Name, '^EXIT_AnchorGuard') or string.match(d.Name, '^COL_ExitAnchorGuard_')) then
    d:SetAttribute('next_island_guard', true)
    d:SetAttribute('removed_by', 'integracao da Ilha 2 (ponte seguinte encosta em ISLAND_NEXT_ANCHOR)')
    CS:AddTag(d, 'GuardaProximaIlha'); nG += 1 end
end
print(string.format('%d pecas da guarda da ancora marcadas (GuardaProximaIlha)', nG))
print(string.format('ILHA_NARUTO montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
