-- montar_ilha_onepiece_m2.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID c4809001
-- 1) Importe os FBX ILHA5M2_*_c48090.fbx (3D Importer) para dentro de workspace.ILHA_ONEPIECE_M2. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script ILHA_ONEPIECE_M2_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = 'c4809001'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o ilha5_m2 INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('ILHA_ONEPIECE_M2') or Instance.new('Model', workspace)
root.Name = 'ILHA_ONEPIECE_M2'
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
  ['Cliff_OP_Cool'] = {c = Color3.fromRGB(136,138,146), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Dark'] = {c = Color3.fromRGB(94,98,108), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Moss'] = {c = Color3.fromRGB(90,128,70), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Void'] = {c = Color3.fromRGB(38,40,48), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_OP_Warm'] = {c = Color3.fromRGB(178,170,156), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Indigo'] = {c = Color3.fromRGB(44,52,96), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_Red'] = {c = Color3.fromRGB(176,40,34), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_OP_White'] = {c = Color3.fromRGB(236,232,222), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Dirt_OP'] = {c = Color3.fromRGB(168,140,104), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Dirt_OP_Dark'] = {c = Color3.fromRGB(112,92,70), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Glass_OP_Lantern'] = {c = Color3.fromRGB(232,160,96), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_OP'] = {c = Color3.fromRGB(108,156,74), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_OP_B'] = {c = Color3.fromRGB(96,142,68), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_OP_Deep'] = {c = Color3.fromRGB(72,120,56), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_OP_Gold'] = {c = Color3.fromRGB(220,172,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_OP_Iron'] = {c = Color3.fromRGB(70,70,74), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_OP'] = {c = Color3.fromRGB(234,228,212), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_OP_Shop'] = {c = Color3.fromRGB(214,196,164), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Blue'] = {c = Color3.fromRGB(46,58,92), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_OP_Ridge'] = {c = Color3.fromRGB(30,36,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP'] = {c = Color3.fromRGB(160,154,142), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_B'] = {c = Color3.fromRGB(148,144,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Dark'] = {c = Color3.fromRGB(100,98,96), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Inlay'] = {c = Color3.fromRGB(150,128,98), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_OP_Path'] = {c = Color3.fromRGB(206,196,172), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Plaza'] = {c = Color3.fromRGB(196,186,162), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_OP_Wall'] = {c = Color3.fromRGB(182,174,158), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Window_OP_Warm'] = {c = Color3.fromRGB(250,212,160), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wood_OP_Dark'] = {c = Color3.fromRGB(66,46,34), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
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
local FBX = {[1]='ILHA5M2_02_TERRAIN_c48090.fbx', [2]='ILHA5M2_03_PLAZA_c48090.fbx', [3]='ILHA5M2_04_CASTLE.fbx', [4]='ILHA5M2_05_CAPITAL_c48090.fbx', [5]='ILHA5M2_06_SUMMON.fbx', [6]='ILHA5M2_07_WATER.fbx', [7]='ILHA5M2_08_NEXT_ISLAND.fbx', [8]='ILHA5M2_08_PURCHASE_GATES.fbx', [9]='ILHA5M2_09_PROPS.fbx', [10]='ILHA5M2_10_VEGETATION.fbx', [11]='ILHA5M2_12_VFX_HELPERS.fbx', [12]='ILHA5M2_16_HARBOR.fbx', [13]='ILHA5M2_17_LANDMARKS.fbx', [14]='ILHA5M2_18_ENTRY.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['OP_Ter_CastleRock__Cliff_OP_Cool']={-2325.148,114.895,1938.399,42.047,39.791,30.317,1,true,'Cliff_OP_Cool','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Dark']={-2325.947,115.45,1939.939,11.649,40.9,10.913,1,true,'Cliff_OP_Dark','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Moss']={-2324.617,133.698,1937.682,40.986,4.704,28.884,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Void']={-2328.331,131.2,1942.986,5.57,5.6,3.9,1,false,'Cliff_OP_Void','',''},
  ['OP_Ter_CastleRock__Cliff_OP_Warm']={-2324.617,114.895,1937.682,40.986,39.791,28.884,1,true,'Cliff_OP_Warm','',''},
  ['OP_Ter_CastleRock__Grass_OP_Deep']={-2325.205,135.975,1938.481,42.162,0.15,30.481,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_CastleRock__Stone_OP']={-2326.152,133.42,1940.119,11.24,4.84,10.552,1,false,'Stone_OP','',''},
  ['OP_Ter_CastleWall__Stone_OP_Dark']={-2292.465,117.151,2003.99,57.767,37.098,82.202,1,true,'Stone_OP_Dark','',''},
  ['OP_Ter_CastleWall__Stone_OP_Path']={-2292.932,130.045,2003.663,58.596,12.75,82.849,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_CastleWall__Stone_OP_Wall']={-2292.565,117.126,2003.894,57.488,36.908,81.894,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Cliff__Cliff_OP_Cool']={-2286.583,65.883,1846.991,574.542,61.767,544.115,1,true,'Cliff_OP_Cool','',''},
  ['OP_Ter_Cliff__Cliff_OP_Dark']={-2286.583,46.75,1833.963,574.542,113.5,582.058,1,true,'Cliff_OP_Dark','',''},
  ['OP_Ter_Cliff__Cliff_OP_Moss']={-2286.966,95.0,1849.221,571.062,107.0,544.946,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Cliff__Cliff_OP_Warm']={-2285.828,90.474,1850.85,568.957,114.948,548.284,1,true,'Cliff_OP_Warm','',''},
  ['OP_Ter_Cliff__Dirt_OP_Dark']={-2258.565,95.231,1768.896,498.745,16.938,41.209,1,false,'Dirt_OP_Dark','',''},
  ['OP_Ter_Cliff__Grass_OP_Deep']={-2286.042,95.45,1848.805,567.431,107.8,544.115,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Cliff__Stone_OP']={-2356.884,66.725,1643.446,208.24,50.35,199.87,1,true,'Stone_OP','',''},
  ['OP_Ter_Cliff__Stone_OP_Path']={-2357.055,66.6,1642.091,209.254,50.2,198.217,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_Cliff__Stone_OP_Wall']={-2357.501,62.34,1641.69,210.146,53.681,197.414,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Ground__Cliff_OP_Cool']={-2283.597,89.75,1829.532,558.456,119.5,558.568,1,true,'Cliff_OP_Cool','',''},
  ['OP_Ter_Ground__Cliff_OP_Moss']={-2287.325,95.925,1830.912,560.1,108.15,572.779,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Ground__Dirt_OP']={-2291.586,93.9,1863.22,541.214,12.6,490.382,1,false,'Dirt_OP','',''},
  ['OP_Ter_Ground__Dirt_OP_Dark']={-2283.597,95.6,1829.532,558.456,107.8,558.568,1,false,'Dirt_OP_Dark','',''},
  ['OP_Ter_Ground__Grass_OP']={-2290.188,93.9,1864.001,543.0,12.6,486.683,1,false,'Grass_OP','',''},
  ['OP_Ter_Ground__Grass_OP_B']={-2286.748,94.2,1867.143,541.763,12.0,478.772,1,false,'Grass_OP_B','',''},
  ['OP_Ter_Ground__Grass_OP_Deep_g-4_2']={-2340.697,95.925,1890.082,441.649,108.15,454.312,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Ground__Grass_OP_Deep_g-4_3']={-2287.208,72.75,1796.354,561.127,61.8,504.928,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Ground__Stone_OP']={-2346.495,41.9,1648.229,215.415,0.6,194.652,1,true,'Stone_OP','',''},
  ['OP_Ter_Ground__Stone_OP_Path']={-2274.879,100.4,1849.11,334.605,71.6,475.055,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Dark']={-2204.382,89.995,1756.799,224.007,4.33,120.632,1,true,'Stone_OP_Dark','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Path']={-2115.953,92.15,1800.066,47.701,0.4,34.072,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Wall_g-2_2']={-2204.223,89.995,1756.347,224.604,4.33,121.018,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_M2_Arrimo__Stone_OP_Wall_g-1_2']={-2149.987,89.995,1775.102,53.019,4.33,36.732,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Piers__Wood_OP_Dark']={-2378.914,41.3,1614.081,102.316,1.6,145.625,1,true,'Wood_OP_Dark','',''},
  ['OP_Ter_Piers__Wood_OP_Mid']={-2378.898,41.75,1614.081,101.438,0.9,144.715,1,true,'Wood_OP_Mid','',''},
  ['OP_Ter_Rocks__Cliff_OP_Cool']={-2366.38,88.5,1875.968,715.564,129.0,531.348,1,true,'Cliff_OP_Cool','',''},
  ['OP_Ter_Rocks__Cliff_OP_Dark']={-2501.913,92.562,1617.771,49.881,25.123,35.833,1,false,'Cliff_OP_Dark','',''},
  ['OP_Ter_Rocks__Cliff_OP_Moss']={-2366.452,92.667,1867.813,713.744,99.667,534.36,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Rocks__Cliff_OP_Warm']={-2365.264,103.294,1875.443,712.68,154.568,529.509,1,true,'Cliff_OP_Warm','',''},
  ['OP_Ter_Rocks__Grass_OP_Deep']={-2364.822,119.338,1870.189,709.499,125.682,516.724,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Walls__Cliff_OP_Cool']={-2282.807,95.143,1846.63,548.631,107.986,497.397,1,true,'Cliff_OP_Cool','',''},
  ['OP_Ter_Walls__Cliff_OP_Moss']={-2282.805,105.045,1846.641,548.718,89.209,497.489,1,true,'Cliff_OP_Moss','',''},
  ['OP_Ter_Walls__Cliff_OP_Warm']={-2282.807,95.799,1846.633,548.653,106.798,497.42,1,true,'Cliff_OP_Warm','',''},
  ['OP_Ter_Walls__Dirt_OP_Dark']={-2288.298,88.95,1851.141,372.575,94.9,467.861,1,false,'Dirt_OP_Dark','',''},
  ['OP_Ter_Walls__Grass_OP_Deep']={-2282.805,117.675,1846.641,548.718,64.05,497.489,1,false,'Grass_OP_Deep','',''},
  ['OP_Ter_Walls__Stone_OP_Dark']={-2243.116,88.75,1859.523,453.79,93.9,497.861,1,true,'Stone_OP_Dark','',''},
  ['OP_Ter_Walls__Stone_OP_Path']={-2243.07,100.645,1859.718,454.45,71.55,498.244,1,true,'Stone_OP_Path','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-3_1']={-2374.833,111.725,1855.698,113.816,47.71,128.779,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-3_2']={-2380.428,78.225,1753.342,179.331,26.71,182.528,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-3_3']={-2342.333,64.725,1638.104,77.758,45.71,54.628,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-2_0']={-2185.906,111.25,1946.957,339.6,48.66,323.413,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-2_3']={-2213.248,64.725,1654.827,183.936,45.71,75.713,1,true,'Stone_OP_Wall','',''},
  ['OP_Ter_Walls__Stone_OP_Wall_g-1_0']={-2099.956,93.352,1941.734,153.86,12.457,177.079,1,false,'Stone_OP_Wall','',''},
  ['OP_Plz_M2_Borda__Cloth_OP_Indigo']={-2247.936,105.738,1825.795,254.3,3.687,241.102,2,true,'Cloth_OP_Indigo','',''},
  ['OP_Plz_M2_Borda__Cloth_OP_White']={-2247.935,104.065,1825.754,254.35,11.89,241.4,2,true,'Cloth_OP_White','',''},
  ['OP_Plz_M2_Borda__Glass_OP_Lantern']={-2246.894,97.768,1826.118,139.665,2.935,174.747,2,false,'Glass_OP_Lantern','',''},
  ['OP_Plz_M2_Borda__Metal_OP_Gold']={-2247.932,109.725,1825.767,254.563,2.85,241.609,2,true,'Metal_OP_Gold','',''},
  ['OP_Plz_M2_Borda__Metal_OP_Iron']={-2247.93,96.773,1825.751,255.243,7.933,242.441,2,true,'Metal_OP_Iron','',''},
  ['OP_Plz_M2_Borda__Roof_OP_Ridge']={-2298.735,99.878,1900.718,37.85,0.724,27.413,2,true,'Roof_OP_Ridge','',''},
  ['OP_Plz_M2_Borda__Stone_OP']={-2244.392,95.91,1823.4,262.281,7.82,246.971,2,true,'Stone_OP','',''},
  ['OP_Plz_M2_Borda__Stone_OP_B']={-2247.04,95.41,1824.57,257.756,6.82,245.62,2,true,'Stone_OP_B','',''},
  ['OP_Plz_M2_Borda__Stone_OP_Dark']={-2204.943,93.135,1756.303,221.361,2.17,118.927,2,true,'Stone_OP_Dark','',''},
  ['OP_Plz_M2_Borda__Stone_OP_Path']={-2204.958,94.93,1756.299,221.865,1.4,119.492,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_M2_Borda__Stone_OP_Wall']={-2204.971,93.5,1756.289,221.891,2.9,119.596,2,true,'Stone_OP_Wall','',''},
  ['OP_Plz_M2_Borda__Window_OP_Warm']={-2298.735,98.94,1900.718,35.984,1.18,25.547,2,false,'Window_OP_Warm','',''},
  ['OP_Plz_M2_Borda__Wood_OP_Dark']={-2247.932,101.45,1825.767,254.443,17.7,241.492,2,true,'Wood_OP_Dark','',''},
  ['OP_Plz_M2_Faixa__Stone_OP']={-2210.412,92.125,1766.995,178.624,0.45,126.061,2,true,'Stone_OP','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_B']={-2198.97,92.125,1775.32,166.057,0.45,116.917,2,true,'Stone_OP_B','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Inlay']={-2247.113,92.09,1826.994,25.994,0.38,25.994,2,false,'Stone_OP_Inlay','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Path']={-2199.341,92.125,1775.139,137.325,0.45,145.492,2,true,'Stone_OP_Path','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Plaza_g-2_1']={-2214.952,92.125,1812.753,86.717,0.45,50.876,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Plaza_g-2_2']={-2223.309,92.125,1746.543,184.44,0.45,99.948,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_M2_Faixa__Stone_OP_Plaza_g-1_1']={-2147.386,92.125,1821.909,65.65,0.45,67.569,2,true,'Stone_OP_Plaza','',''},
  ['OP_Plz_M2_PisoProvisorio__Stone_OP_Plaza']={-2252.604,92.125,1838.165,253.139,0.45,230.314,2,true,'Stone_OP_Plaza','',''},
  ['OP_Cap_M2_Escadaria__Cloth_OP_Red']={-2164.518,94.9,1709.036,36.718,1.2,24.11,4,true,'Cloth_OP_Red','',''},
  ['OP_Cap_M2_Escadaria__Glass_OP_Lantern']={-2172.014,93.155,1722.367,51.771,3.97,50.833,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_M2_Escadaria__Metal_OP_Iron']={-2172.09,92.89,1722.455,50.95,6.52,50.026,4,true,'Metal_OP_Iron','',''},
  ['OP_Cap_M2_Escadaria__Roof_OP_Ridge']={-2172.777,94.968,1723.339,52.112,6.003,50.756,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_M2_Escadaria__Stone_OP_B']={-2175.685,90.953,1727.572,57.96,6.106,59.234,4,true,'Stone_OP_B','',''},
  ['OP_Cap_M2_Escadaria__Stone_OP_Dark']={-2189.36,90.286,1743.456,30.018,4.772,25.518,4,true,'Stone_OP_Dark','',''},
  ['OP_Cap_M2_Escadaria__Stone_OP_Path']={-2188.385,91.498,1743.206,32.373,5.603,27.854,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_M2_Escadaria__Window_OP_Warm']={-2185.425,91.44,1738.894,24.95,1.08,17.779,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_M2_Escadaria__Wood_OP_Dark']={-2172.152,92.865,1722.505,52.22,9.33,51.282,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_M2_Lojas__Cloth_OP_Indigo']={-2159.967,95.275,1703.384,38.624,7.15,37.27,4,true,'Cloth_OP_Indigo','',''},
  ['OP_Cap_M2_Lojas__Cloth_OP_Red']={-2159.469,95.2,1702.338,42.204,7.0,40.568,4,true,'Cloth_OP_Red','',''},
  ['OP_Cap_M2_Lojas__Cloth_OP_White']={-2159.967,94.19,1703.384,38.223,4.98,36.864,4,true,'Cloth_OP_White','',''},
  ['OP_Cap_M2_Lojas__Glass_OP_Lantern']={-2160.044,97.575,1700.64,41.107,1.68,37.224,4,false,'Glass_OP_Lantern','',''},
  ['OP_Cap_M2_Lojas__Metal_OP_Gold']={-2142.594,104.19,1703.634,10.438,0.78,13.439,4,true,'Metal_OP_Gold','',''},
  ['OP_Cap_M2_Lojas__Metal_OP_Iron']={-2159.821,96.95,1701.489,43.106,6.4,39.974,4,true,'Metal_OP_Iron','',''},
  ['OP_Cap_M2_Lojas__Plaster_OP']={-2153.396,104.107,1695.465,67.182,24.815,56.357,4,true,'Plaster_OP','',''},
  ['OP_Cap_M2_Lojas__Plaster_OP_Shop']={-2162.386,99.102,1703.979,85.165,18.603,72.272,4,true,'Plaster_OP_Shop','',''},
  ['OP_Cap_M2_Lojas__Roof_OP_Blue']={-2162.456,106.909,1703.87,96.421,20.411,80.451,4,true,'Roof_OP_Blue','',''},
  ['OP_Cap_M2_Lojas__Roof_OP_Ridge']={-2162.456,110.059,1703.554,98.552,18.018,66.717,4,true,'Roof_OP_Ridge','',''},
  ['OP_Cap_M2_Lojas__Stone_OP']={-2162.387,88.5,1703.671,87.508,1.4,73.999,4,true,'Stone_OP','',''},
  ['OP_Cap_M2_Lojas__Stone_OP_B']={-2162.387,90.3,1709.282,85.951,5.0,61.687,4,true,'Stone_OP_B','',''},
  ['OP_Cap_M2_Lojas__Stone_OP_Dark']={-2159.713,90.255,1702.347,39.117,4.79,37.198,4,true,'Stone_OP_Dark','',''},
  ['OP_Cap_M2_Lojas__Window_OP_Warm']={-2162.195,97.3,1706.284,77.605,15.0,54.244,4,false,'Window_OP_Warm','',''},
  ['OP_Cap_M2_Lojas__Wood_OP_Dark']={-2162.456,102.882,1703.87,97.22,27.565,80.451,4,true,'Wood_OP_Dark','',''},
  ['OP_Cap_M2_Lojas__Wood_OP_Lacquer']={-2142.57,102.08,1703.645,10.567,3.76,13.541,4,true,'Wood_OP_Lacquer','',''},
  ['OP_Cap_M2_Lojas__Wood_OP_Mid']={-2160.142,94.925,1703.746,45.321,10.75,42.376,4,true,'Wood_OP_Mid','',''},
  ['OP_Cap_M2_Rua__Stone_OP']={-2167.328,88.125,1713.017,64.511,0.45,60.14,4,true,'Stone_OP','',''},
  ['OP_Cap_M2_Rua__Stone_OP_B']={-2168.015,88.125,1704.115,44.032,0.45,54.107,4,true,'Stone_OP_B','',''},
  ['OP_Cap_M2_Rua__Stone_OP_Path']={-2166.697,88.125,1714.85,60.267,0.45,68.376,4,true,'Stone_OP_Path','',''},
  ['OP_Cap_M2_Rua__Stone_OP_Plaza']={-2166.812,88.125,1712.149,57.513,0.45,65.915,4,true,'Stone_OP_Plaza','',''},
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
  {'COL_OP_CapHouseB1_001','Block',{-2114.548,92.2,1731.818},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.4,16.4,8.0},true},
  {'COL_OP_CapHouseB2_001','Block',{-2131.346,95.5,1762.782},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.4,18.4,14.6},true},
  {'COL_OP_CapHouseB3_001','Block',{-2203.507,92.2,1667.086},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.4,18.4,8.0},true},
  {'COL_OP_CapHouseB4_001','Block',{-2226.777,95.5,1689.858},{-0.574,0.0,0.819},{0.819,0.0,0.574},{22.4,16.4,14.6},true},
  {'COL_OP_CapHouseB5_001','Block',{-2224.805,92.2,1652.173},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.4,16.4,8.0},true},
  {'COL_OP_CapHouseB6_001','Block',{-2245.78,95.5,1671.668},{-0.574,0.0,0.819},{0.819,0.0,0.574},{20.4,18.4,14.6},true},
  {'COL_OP_CapHouseB7_001','Block',{-2250.201,92.2,1646.599},{-0.574,0.0,0.819},{0.819,0.0,0.574},{16.4,14.4,8.0},true},
  {'COL_OP_CapHouseC1_001','Block',{-2132.65,88.5,1710.597},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.6,22.6,1.2},true},
  {'COL_OP_CapHouseC1_002','Block',{-2132.65,98.65,1710.597},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.0,22.0,19.1},true},
  {'COL_OP_CapHouseC2_001','Block',{-2140.517,88.5,1727.063},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.6,26.6,1.2},true},
  {'COL_OP_CapHouseC2_002','Block',{-2140.517,94.6,1727.063},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.0,26.0,11.0},true},
  {'COL_OP_CapHouseC4_001','Block',{-2158.215,95.75,1748.852},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{16.4,24.4,15.1},true},
  {'COL_OP_CapHouseC5_001','Block',{-2174.918,88.5,1678.559},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.6,20.6,1.2},true},
  {'COL_OP_CapHouseC5_002','Block',{-2174.918,98.0,1678.559},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.0,20.0,17.8},true},
  {'COL_OP_CapHouseC6_001','Block',{-2189.092,88.55,1691.829},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.6,28.6,1.3},true},
  {'COL_OP_CapHouseC6_002','Block',{-2189.092,95.45,1691.829},{-0.574,0.0,0.819},{0.819,0.0,0.574},{18.0,28.0,12.5},true},
  {'COL_OP_CapHouseC7_001','Block',{-2199.499,99.05,1710.178},{-0.574,0.0,0.819},{0.819,0.0,0.574},{16.4,22.4,21.7},true},
  {'COL_OP_CapHouseN1_001','Block',{-2421.607,96.95,1814.681},{-0.574,0.0,0.819},{0.819,0.0,0.574},{24.4,22.4,9.5},true},
  {'COL_OP_CapHouseN2_001','Block',{-2439.46,99.5,1770.44},{0.819,0.0,0.574},{0.574,0.0,-0.819},{20.4,16.4,14.6},true},
  {'COL_OP_CapHouseN3_001','Block',{-2454.377,96.2,1816.151},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.4,14.4,8.0},true},
  {'COL_OP_CapHouseN4_001','Block',{-2453.549,96.2,1755.692},{0.819,0.0,0.574},{0.574,0.0,-0.819},{14.4,12.4,8.0},true},
  {'COL_OP_CapHouseN5_001','Block',{-2399.166,99.75,1852.369},{0.819,0.0,0.574},{0.574,0.0,-0.819},{18.4,14.4,15.1},true},
  {'COL_OP_CapHouseS1_001','Block',{-2086.041,92.2,1746.896},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.4,16.4,8.0},true},
  {'COL_OP_CapHouseS2_001','Block',{-2057.042,92.2,1764.759},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.4,16.4,8.0},true},
  {'COL_OP_CapHouseS3_001','Block',{-2099.154,95.5,1786.545},{0.819,0.0,0.574},{0.574,0.0,-0.819},{24.4,16.4,14.6},true},
  {'COL_OP_CapHouseS4_001','Block',{-2047.054,92.2,1813.259},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.4,18.4,8.0},true},
  {'COL_OP_CapHouseS5_001','Block',{-2081.46,92.2,1801.375},{0.819,0.0,0.574},{0.574,0.0,-0.819},{16.4,14.4,8.0},true},
  {'COL_OP_CapHouseU1_001','Block',{-2190.775,108.0,2008.052},{0.819,0.0,0.574},{0.574,0.0,-0.819},{34.4,22.4,15.6},true},
  {'COL_OP_CapHouseU2_001','Block',{-2239.769,108.0,2039.668},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{26.4,22.4,15.6},true},
  {'COL_OP_CapHouseU3_001','Block',{-2207.333,104.2,2077.029},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{24.4,20.4,8.0},true},
  {'COL_OP_CapHouseU4_001','Block',{-2158.338,104.2,2045.414},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{18.4,22.4,8.0},true},
  {'COL_OP_CapHouseU5_001','Block',{-2174.982,104.95,2085.398},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseU5_002','Block',{-2183.666,104.95,2079.318},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseU5_003','Block',{-2167.755,104.95,2075.077},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseU5_004','Block',{-2176.438,104.95,2068.997},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW1_001','Block',{-2088.84,99.75,1845.039},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{26.4,30.4,15.1},true},
  {'COL_OP_CapHouseW2_001','Block',{-2110.062,96.2,1875.348},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{24.4,32.4,8.0},true},
  {'COL_OP_CapHouseW3_001','Block',{-2133.342,96.95,1914.348},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW3_002','Block',{-2148.578,96.95,1903.68},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW3_003','Block',{-2127.434,96.95,1905.911},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW3_004','Block',{-2142.67,96.95,1895.242},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW3_005','Block',{-2121.526,96.95,1897.474},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW3_006','Block',{-2136.762,96.95,1886.805},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.0,1.0,7.5},true},
  {'COL_OP_CapHouseW4_001','Block',{-2150.786,103.05,1933.508},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{24.4,32.4,21.7},true},
  {'COL_OP_CapHouseW5_001','Block',{-2170.861,99.5,1962.178},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{26.4,28.4,14.6},true},
  {'COL_OP_CapHouseX1_001','Block',{-2044.116,96.2,1891.004},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{22.4,22.4,8.0},true},
  {'COL_OP_CapHouseX2_001','Block',{-2077.711,99.5,1940.727},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{26.4,24.4,14.6},true},
  {'COL_OP_CapHouseX3_001','Block',{-2110.651,96.2,1986.026},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{22.4,22.4,8.0},true},
  {'COL_OP_CapTorii_001','Block',{-2406.259,97.9,1831.117},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.68,1.68,11.4},false},
  {'COL_OP_CapTorii_002','Block',{-2400.913,97.9,1823.483},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{1.68,1.68,11.4},false},
  {'COL_OP_CasCourtGate_001','Block',{-2311.373,141.2,2057.894},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,10.0},false},
  {'COL_OP_CasCourtGate_002','Block',{-2325.79,141.2,2047.799},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,10.0},false},
  {'COL_OP_CasGate_001','Block',{-2292.7,105.7,1925.574},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.2,6.4,15.0},true},
  {'COL_OP_CasGate_002','Block',{-2324.156,105.7,1903.549},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{3.2,6.4,15.0},true},
  {'COL_OP_CasKeepCeil_001','Block',{-2354.945,148.5,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{52.2,42.2,0.6},false},
  {'COL_OP_CasKeepUpper_001','Block',{-2354.945,174.2,1980.995},{0.819,0.0,0.574},{0.574,0.0,-0.819},{56.0,46.0,40.0},true},
  {'COL_OP_CasKeep_001','Block',{-2377.062,146.7,1965.508},{0.819,0.0,0.574},{0.574,0.0,-0.819},{2.0,46.0,21.0},true},
  {'COL_OP_CasKeep_002','Block',{-2332.828,146.7,1996.481},{0.819,0.0,0.574},{0.574,0.0,-0.819},{2.0,46.0,21.0},true},
  {'COL_OP_CasKeep_003','Block',{-2367.564,146.7,1999.016},{0.819,0.0,0.574},{0.574,0.0,-0.819},{56.0,2.0,21.0},true},
  {'COL_OP_CasKeep_004','Block',{-2355.023,146.7,1954.083},{0.819,0.0,0.574},{0.574,0.0,-0.819},{25.0,2.0,21.0},true},
  {'COL_OP_CasKeep_005','Block',{-2329.629,146.7,1971.864},{0.819,0.0,0.574},{0.574,0.0,-0.819},{25.0,2.0,21.0},true},
  {'COL_OP_CasKeep_006','Block',{-2342.326,151.2,1962.973},{0.819,0.0,0.574},{0.574,0.0,-0.819},{6.0,2.0,12.0},true},
  {'COL_OP_CasTurret_001','Block',{-2379.513,144.2,1914.961},{0.819,0.0,0.574},{0.574,0.0,-0.819},{13.0,13.0,16.0},true},
  {'COL_OP_CasWall_001','Block',{-2418.512,138.7,1943.809},{-0.574,0.0,0.819},{0.819,0.0,0.574},{61.0,1.4,5.0},false},
  {'COL_OP_CasWall_002','Block',{-2438.45,138.7,1982.654},{-0.191,0.0,0.982},{0.982,0.0,0.191},{30.547,1.4,5.0},false},
  {'COL_OP_CasWall_003','Block',{-2426.53,138.7,2011.943},{0.697,0.0,0.717},{0.717,0.0,-0.697},{43.755,1.4,5.0},false},
  {'COL_OP_CasWall_004','Block',{-2386.576,138.7,2043.568},{0.838,0.0,0.546},{0.546,0.0,-0.838},{61.033,1.4,5.0},false},
  {'COL_OP_CasWall_005','Block',{-2337.888,138.7,2067.923},{0.947,0.0,0.321},{0.321,0.0,-0.947},{51.0,1.4,5.0},false},
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
  {'COL_OP_ExitBridge_001','Ramp',{-2468.676,87.2,1710.172},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{92.0,18.0,2.0},false},
  {'COL_OP_ExitBridge_002','Ramp',{-2465.393,89.95,1701.151},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{88.0,1.2,4.5},false},
  {'COL_OP_ExitBridge_003','Ramp',{-2471.959,89.95,1719.193},{-0.94,0.0,-0.342},{-0.342,0.0,0.94},{88.0,1.2,4.5},false},
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
  {'COL_OP_PortHouseH1_001','Block',{-2259.862,50.35,1608.094},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.4,16.4,16.3},true},
  {'COL_OP_PortHouseH2_001','Block',{-2304.588,46.525,1574.335},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{20.4,14.4,8.65},true},
  {'COL_OP_PortHouseH3_001','Block',{-2336.22,73.35,1647.406},{0.819,0.0,0.574},{0.574,0.0,-0.819},{24.4,14.4,16.3},true},
  {'COL_OP_PortHouseH4_001','Block',{-2350.208,46.95,1551.792},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.0,1.0,7.5},true},
  {'COL_OP_PortHouseH4_002','Block',{-2339.886,46.95,1559.019},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.0,1.0,7.5},true},
  {'COL_OP_PortHouseH4_003','Block',{-2354.968,46.95,1558.591},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.0,1.0,7.5},true},
  {'COL_OP_PortHouseH4_004','Block',{-2344.647,46.95,1565.818},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.0,1.0,7.5},true},
  {'COL_OP_PortHouseH4_005','Block',{-2359.729,46.95,1565.39},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.0,1.0,7.5},true},
  {'COL_OP_PortHouseH4_006','Block',{-2349.407,46.95,1572.617},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.0,1.0,7.5},true},
  {'COL_OP_PropBanner_001','Block',{-2172.554,100.2,1763.227},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_002','Block',{-2212.692,100.2,1735.122},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,16.0},false},
  {'COL_OP_PropBanner_003','Block',{-2120.95,101.2,1817.672},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_004','Block',{-2281.503,101.2,1705.251},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_005','Block',{-2223.208,101.2,1946.278},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropBanner_006','Block',{-2374.914,101.2,1835.169},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.9,1.9,18.0},false},
  {'COL_OP_PropLamp_001','Block',{-2289.194,101.2,1927.541},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.0},false},
  {'COL_OP_PropLamp_002','Block',{-2327.203,101.2,1900.927},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.0},false},
  {'COL_OP_PropLamp_003','Block',{-2298.748,139.2,1998.37},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.0},false},
  {'COL_OP_PropLamp_004','Block',{-2382.302,139.2,1939.865},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.0},false},
  {'COL_OP_PropLamp_005','Block',{-2318.02,45.45,1555.163},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.5},false},
  {'COL_OP_PropLamp_006','Block',{-2349.979,68.45,1618.24},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.5},false},
  {'COL_OP_PropLamp_007','Block',{-2420.77,45.45,1680.983},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.5},false},
  {'COL_OP_PropLamp_008','Block',{-2511.556,91.45,1681.794},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.5},false},
  {'COL_OP_PropLamp_009','Block',{-2519.765,91.45,1704.347},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.8,0.8,6.5},false},
  {'COL_OP_PropLamp_010','Block',{-2173.465,90.4,1747.269},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,1.7,4.4},false},
  {'COL_OP_PropLamp_011','Block',{-2197.384,90.4,1730.52},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,1.7,4.4},false},
  {'COL_OP_PropLamp_012','Block',{-2147.64,92.7,1698.88},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_013','Block',{-2167.629,92.7,1699.533},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_014','Block',{-2160.832,92.7,1717.721},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_015','Block',{-2181.395,92.7,1719.192},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{0.9,0.9,9.0},false},
  {'COL_OP_PropLamp_016','Block',{-2281.328,96.0,1912.906},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropLamp_017','Block',{-2316.142,96.0,1888.529},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.1,1.1,7.6},false},
  {'COL_OP_PropToro_001','Block',{-2177.567,96.0,1761.67},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,7.6},false},
  {'COL_OP_PropToro_002','Block',{-2209.514,96.0,1739.301},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.8,2.8,7.6},false},
  {'COL_OP_ShipCabin_001','Block',{-2433.055,49.2,1660.173},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.0,10.0,6.0},true},
  {'COL_OP_ShipMast_001','Block',{-2404.376,50.2,1619.215},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_ShipMast_002','Block',{-2419.289,50.2,1640.513},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
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
  {'COL_OP_Terrain_371','Block',{-2317.783,36.1,1606.602},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{123.397,8.0,12.2},false},
  {'COL_OP_Terrain_372','Block',{-2312.705,36.1,1619.923},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.997,8.0,12.2},false},
  {'COL_OP_Terrain_373','Block',{-2317.458,36.1,1626.362},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.598,8.0,12.2},false},
  {'COL_OP_Terrain_374','Block',{-2322.21,36.1,1632.8},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{98.198,8.0,12.2},false},
  {'COL_OP_Terrain_375','Block',{-2390.618,36.1,1648.381},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{28.0,96.0,12.2},false},
  {'COL_OP_Terrain_387','Block',{-2431.015,36.1,1716.536},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.0,61.999,12.2},false},
  {'COL_OP_Terrain_395','Block',{-2392.905,45.2,1602.832},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{11.925,8.0,2.0},false},
  {'COL_OP_Terrain_396','Block',{-2397.493,45.2,1609.385},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.241,8.0,2.0},false},
  {'COL_OP_Terrain_397','Block',{-2402.082,45.2,1615.938},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.483,8.0,2.0},false},
  {'COL_OP_Terrain_398','Block',{-2406.671,45.2,1622.492},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.726,8.0,2.0},false},
  {'COL_OP_Terrain_399','Block',{-2411.259,45.2,1629.045},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.968,8.0,2.0},false},
  {'COL_OP_Terrain_400','Block',{-2415.848,45.2,1635.598},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.211,8.0,2.0},false},
  {'COL_OP_Terrain_401','Block',{-2420.437,45.2,1642.151},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.453,8.0,2.0},false},
  {'COL_OP_Terrain_402','Block',{-2425.025,45.2,1648.704},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.695,8.0,2.0},false},
  {'COL_OP_Terrain_403','Block',{-2430.187,45.2,1656.077},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.938,10.0,2.0},false},
  {'COL_OP_Terrain_405','Block',{-2145.819,57.1,1682.332},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{18.5,10.8,54.2},false},
  {'COL_OP_Terrain_406','Block',{-2191.418,59.1,1747.454},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{30.5,1.8,58.2},false},
  {'COL_OP_Terrain_407','Block',{-2076.737,59.1,1827.755},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{12.5,1.8,58.2},false},
  {'COL_OP_Terrain_408','Block',{-2206.829,61.1,1962.507},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{13.05,7.8,62.2},false},
  {'COL_OP_Terrain_409','Block',{-2307.052,61.1,1912.595},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{32.5,13.0,62.2},false},
  {'COL_OP_Terrain_410','Block',{-2283.204,64.1,2002.54},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.25,1.0,68.2},false},
  {'COL_OP_Terrain_411','Block',{-2303.697,73.6,2031.589},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{14.5,45.9,87.2},false},
  {'COL_OP_Terrain_412','Block',{-2324.264,47.6,1680.193},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.2,14.5,35.2},false},
  {'COL_OP_TreeRoot_001','Block',{-2433.365,142.02,1978.671},{-0.716,0.0,-0.698},{-0.698,0.0,0.716},{5.777,9.175,11.64},false},
  {'COL_OP_TreeRoot_002','Block',{-2436.769,141.707,1975.346},{-0.714,0.0,-0.7},{-0.7,0.0,0.714},{5.19,8.002,11.014},false},
  {'COL_OP_TreeRoot_003','Block',{-2438.777,141.765,1986.697},{-1.0,0.0,-0.013},{-0.013,0.0,1.0},{5.051,7.799,11.129},false},
  {'COL_OP_TreeRoot_004','Block',{-2436.629,141.207,1991.671},{-0.931,0.0,0.364},{0.364,0.0,0.931},{4.836,7.385,10.014},false},
  {'COL_OP_TreeRoot_005','Block',{-2423.802,140.562,1999.595},{0.102,0.0,0.995},{0.995,0.0,-0.102},{7.83,6.897,8.725},false},
  {'COL_OP_TreeRoot_006','Block',{-2423.134,138.207,2005.031},{0.142,0.0,0.99},{0.99,0.0,-0.142},{6.768,4.772,4.014},false},
  {'COL_OP_TreeRoot_007','Block',{-2416.236,141.176,1996.829},{0.66,0.0,0.752},{0.752,0.0,-0.66},{8.617,8.003,9.952},false},
  {'COL_OP_TreeRoot_008','Block',{-2412.255,139.087,2000.978},{0.725,0.0,0.689},{0.689,0.0,-0.725},{7.686,6.187,5.775},false},
  {'COL_OP_TreeRoot_009','Block',{-2407.91,137.46,2004.736},{0.786,0.0,0.618},{0.618,0.0,-0.786},{6.836,4.455,2.52},false},
  {'COL_OP_TreeRoot_010','Block',{-2403.249,136.67,2008.155},{0.824,0.0,0.566},{0.566,0.0,-0.824},{6.033,2.778,0.94},false},
  {'COL_OP_TreeRoot_011','Block',{-2415.226,140.912,1978.744},{0.773,0.0,-0.634},{-0.634,0.0,-0.773},{7.96,7.229,9.424},false},
  {'COL_OP_TreeRoot_012','Block',{-2410.878,138.699,1975.511},{0.83,0.0,-0.557},{-0.557,0.0,-0.83},{7.006,5.344,4.998},false},
  {'COL_OP_TreeRoot_013','Block',{-2406.24,137.071,1972.691},{0.876,0.0,-0.483},{-0.483,0.0,-0.876},{6.132,3.547,1.742},false},
  {'COL_OP_TreeRoot_014','Block',{-2419.977,141.423,1974.812},{0.386,0.0,-0.922},{-0.922,0.0,-0.386},{8.386,7.701,10.447},false},
  {'COL_OP_TreeRoot_015','Block',{-2417.842,139.463,1969.561},{0.367,0.0,-0.93},{-0.93,0.0,-0.367},{7.613,6.16,6.526},false},
  {'COL_OP_TreeRoot_016','Block',{-2415.823,137.872,1964.266},{0.345,0.0,-0.938},{-0.938,0.0,-0.345},{6.879,4.69,3.344},false},
  {'COL_OP_TreeRoot_017','Block',{-2413.918,136.809,1958.928},{0.327,0.0,-0.945},{-0.945,0.0,-0.327},{6.168,3.265,1.217},false},
  {'COL_OP_TreeTrunk_001','Block',{-2424.99,150.2,1986.883},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.0,22.0,28.0},true},
  {'COL_OP_TreeTrunk_002','Block',{-2424.99,150.2,1986.883},{-0.985,0.0,0.174},{0.174,0.0,0.985},{22.0,22.0,28.0},true},
  {'COL_OP_TreeTrunk_003','Block',{-2426.587,170.2,1983.934},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{19.0,19.0,16.0},true},
  {'COL_OP_VegTrunk_001','Block',{-2145.926,92.2,1745.249},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_002','Block',{-2193.732,104.2,2064.579},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_003','Block',{-2241.25,104.2,2080.138},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_004','Block',{-2408.831,96.2,1838.277},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_005','Block',{-2388.165,92.2,1686.722},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_006','Block',{-2535.303,92.2,1715.539},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_007','Block',{-2038.856,92.2,1770.168},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,8.0},false},
  {'COL_OP_VegTrunk_008','Block',{-2301.87,138.0,2062.106},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,8.0},false},
  {'COL_OP_VegTrunk_009','Block',{-2136.381,104.2,2031.49},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,8.0},false},
  {'COL_OP_VegTrunk_010','Block',{-2051.739,96.2,1921.069},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.6,1.6,8.0},false},
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
  {'FX_Fall_Castle_Base',{-2321.104,97.3,1932.665},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_base',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_Castle_Lip',{-2324.545,132.2,1937.58},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_borda',['width']=7.0,['drop']=34.6,['note']='CACHOEIRA DO CASTELO: nasce na rocha sob a varanda vermelha e cai na bacia do adro (agua do Roblox)',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_E_Base',{-2497.132,36.4,1750.812},{0.999,0.0,-0.033},{-0.033,0.0,-0.999},{['fx']='espuma_mar',['fwd_x']=-0.0326,['fwd_z']=-0.9995}},
  {'FX_Fall_E_Lip',{-2499.426,91.6,1754.088},{0.999,0.0,-0.033},{-0.033,0.0,-0.999},{['fx']='nevoa_borda',['width']=6.0,['drop']=55.6,['note']='queda E: canal -> enseada do porto',['fwd_x']=-0.0326,['fwd_z']=-0.9995}},
  {'FX_Fall_W_Base',{-2009.367,36.4,1790.817},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='espuma_mar',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Fall_W_Lip',{-2011.661,87.6,1794.094},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='nevoa_borda',['width']=6.0,['drop']=51.6,['note']='queda W: canal -> mar (falesia SO)',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Mist_CastleFall',{-2318.236,99.2,1928.569},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fx']='nevoa_baixa',['radius']=14.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'FX_Petals_Tree',{-2323.378,283.7,2024.828},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fx']='petalas',['Dist']=320.0,['radius']=40.0,['note']='UM emissor de petalas na copa (discreto)',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'FX_Spring_W',{-2152.76,97.2,1995.605},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['fx']='bica',['note']='nascente do canal oeste: bica no arrimo do terraco alto',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'FX_Weir_E',{-2398.022,97.6,1875.144},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fx']='degrau_agua',['drop']=6.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'FX_Weir_W',{-2047.796,91.6,1845.7},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['fx']='degrau_agua',['drop']=4.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
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
  {'WATER_Basin',{-2319.383,97.6,1930.207},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['shape']='poligono',['level']=97.60000000000001,['floor']=96.00000000000001,['sx']=40.0,['sy']=15.0,['waypoints']='-2300.62,97.60,1934.80;-2330.11,97.60,1914.15;-2336.34,97.60,1919.56;-2335.44,97.60,1928.73;-2312.50,97.60,1944.79;-2303.57,97.60,1942.50',['note']='bacia do adro ao pe da cachoeira do castelo',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'WATER_CanalE',{-2334.128,97.6,1919.883},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['waypoints']='-2334.13,97.60,1919.88;-2394.74,97.60,1877.44;-2401.30,91.60,1872.85;-2473.96,91.60,1823.19;-2523.11,91.60,1788.78;-2501.15,91.60,1756.55',['widths']='6.0,6.0,6.0,6.0,6.0,6.0',['note']='canal de pedra (agua do Roblox); degraus nos FX_Weir_*',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'WATER_CanalW',{-2152.187,91.6,1994.786},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['waypoints']='-2152.19,91.60,1994.79;-2124.08,91.60,1954.65;-2085.08,91.60,1898.94;-2049.52,91.60,1848.16;-2046.08,87.60,1843.24;-2033.46,87.60,1825.22;-2013.95,87.60,1797.37',['widths']='8.0,8.0,8.0,8.0,8.0,8.0,8.0',['note']='canal de pedra (agua do Roblox); degraus nos FX_Weir_*',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'WATER_Sea',{-2321.499,36.0,1828.622},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['shape']='quadrado',['level']=36.0,['size']=2200.0,['client_only']=true,['area']=5,['color']='48,176,196',['note']='mar LOCAL turquesa de Wano: so no cliente e so com o jogador na area 5 (como o mar de nuvens da DS); esconde a quilha; vista de Wano, a DS aparece como ilha saindo do mar (topo da quilha DS 53,6 > 46)',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
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
  {'L_OPCap_Win_M2C1','POINT',{-2127.144,95.8,1702.733},{255,209,162},6.0,0.34,false,true},
  {'L_OPCap_Win_M2C2','POINT',{-2149.637,93.85,1714.634},{255,209,162},6.0,0.34,false,true},
  {'L_OPCap_Win_M2C5','POINT',{-2176.0,95.8,1688.3},{255,209,162},6.0,0.34,false,true},
  {'L_OPCap_Win_M2C6','POINT',{-2192.428,95.9,1702.433},{255,209,162},6.0,0.34,false,true},
  {'L_OPProp_Lamp_M2Esc_0','POINT',{-2173.465,91.44,1747.269},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Lamp_M2Esc_1','POINT',{-2197.384,91.44,1730.52},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Lamp_M2Rua_0','POINT',{-2147.64,94.95,1698.88},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_1','POINT',{-2167.629,94.95,1699.533},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_2','POINT',{-2160.832,94.95,1717.721},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_M2Rua_3','POINT',{-2181.395,94.95,1719.192},{255,209,162},5.2,0.33,false,true},
  {'L_OPProp_Lamp_PracaN_0','POINT',{-2281.328,98.94,1912.906},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Lamp_PracaN_1','POINT',{-2316.142,98.94,1888.529},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Toro_M2_0','POINT',{-2177.567,96.98,1761.67},{255,209,162},5.1,0.32,false,true},
  {'L_OPProp_Toro_M2_1','POINT',{-2209.514,96.98,1739.301},{255,209,162},5.1,0.32,false,true},
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
  local s = SSS:FindFirstChild('ILHA_ONEPIECE_M2_Servidor') or Instance.new('Script')
  s.Name = 'ILHA_ONEPIECE_M2_Servidor'
  s.Source = [==[
-- gerado por montar_ilha_onepiece_m2.lua (export_roblox.py) - nao editar a mao
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
local root = workspace:WaitForChild('ILHA_ONEPIECE_M2', 60)
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
root.WorldPivot = CFrame.new(ROOT_OFFSET)
-- ===== pecas moveis (VFX_*) =====
local VFX = {
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
print(string.format('ILHA_ONEPIECE_M2 montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
