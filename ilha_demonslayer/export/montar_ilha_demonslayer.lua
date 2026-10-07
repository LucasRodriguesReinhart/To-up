-- montar_ilha_demonslayer.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 9cc4bef4
-- 1) Importe os FBX ILHA4_*_9cc4be.fbx (3D Importer) para dentro de workspace.ILHA_DEMONSLAYER. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script ILHA_DEMONSLAYER_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = '9cc4bef4'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o ilha4 INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('ILHA_DEMONSLAYER') or Instance.new('Model', workspace)
root.Name = 'ILHA_DEMONSLAYER'
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
  ['Bamboo_DS'] = {c = Color3.fromRGB(90,116,56), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Bamboo_DS_Dry'] = {c = Color3.fromRGB(170,160,104), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Bark_DS'] = {c = Color3.fromRGB(70,52,40), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Cliff_DS'] = {c = Color3.fromRGB(70,74,82), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_DS_B'] = {c = Color3.fromRGB(80,75,69), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_DS_Dark'] = {c = Color3.fromRGB(46,49,57), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_DS_Moss'] = {c = Color3.fromRGB(60,86,52), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_DS_Ai'] = {c = Color3.fromRGB(52,70,108), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_DS_Indigo'] = {c = Color3.fromRGB(46,40,86), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_DS_Red'] = {c = Color3.fromRGB(150,36,30), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_GateOP_Straw'] = {c = Color3.fromRGB(236,200,112), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_Red'] = {c = Color3.fromRGB(196,80,75), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Crystal_Blue_Core'] = {c = Color3.fromRGB(70,200,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Crystal_SumPortal_Glow'] = {c = Color3.fromRGB(58,70,232), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Dirt_DS'] = {c = Color3.fromRGB(132,106,76), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Dirt_DS_Dark'] = {c = Color3.fromRGB(98,80,60), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Ember_DS_Glow'] = {c = Color3.fromRGB(255,84,24), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Emblem_Cream'] = {c = Color3.fromRGB(237,231,215), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Energy_Core_OnePiece_Glow'] = {c = Color3.fromRGB(140,214,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Fire_DS_Glow'] = {c = Color3.fromRGB(255,122,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Glass_DS_Lantern'] = {c = Color3.fromRGB(214,144,88), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_DS'] = {c = Color3.fromRGB(84,118,62), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_DS_B'] = {c = Color3.fromRGB(76,108,58), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_DS_Deep'] = {c = Color3.fromRGB(56,90,46), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_DS_Dry'] = {c = Color3.fromRGB(112,118,70), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_DS_Bamboo'] = {c = Color3.fromRGB(94,130,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_DS_Broad'] = {c = Color3.fromRGB(46,84,48), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_DS_Cedar'] = {c = Color3.fromRGB(34,66,46), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_DS_Shrub'] = {c = Color3.fromRGB(66,104,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Brass'] = {c = Color3.fromRGB(186,148,90), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_DS_Brass'] = {c = Color3.fromRGB(176,138,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_DS_Iron'] = {c = Color3.fromRGB(64,62,60), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_DS_Rust'] = {c = Color3.fromRGB(112,66,42), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_DS_Steel'] = {c = Color3.fromRGB(150,158,170), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold'] = {c = Color3.fromRGB(222,170,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold_DS'] = {c = Color3.fromRGB(158,118,56), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_DS_Black'] = {c = Color3.fromRGB(75,63,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_OP_Blue'] = {c = Color3.fromRGB(80,124,188), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['P_OP_Glow'] = {c = Color3.fromRGB(25,105,255), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Plaster_DS'] = {c = Color3.fromRGB(228,216,192), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_DS_Ash'] = {c = Color3.fromRGB(214,210,198), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_DS_Clay'] = {c = Color3.fromRGB(184,152,120), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_DS_Kura'] = {c = Color3.fromRGB(238,234,224), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_DS_Ochre'] = {c = Color3.fromRGB(222,204,172), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_DS_Shoji'] = {c = Color3.fromRGB(204,196,176), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_DS_Ridge'] = {c = Color3.fromRGB(38,42,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_DS_Tile'] = {c = Color3.fromRGB(52,58,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Rope'] = {c = Color3.fromRGB(190,172,140), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['Rope_DS_Straw'] = {c = Color3.fromRGB(186,160,106), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_DS'] = {c = Color3.fromRGB(124,120,112), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_B'] = {c = Color3.fromRGB(112,108,100), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_Brick'] = {c = Color3.fromRGB(150,98,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_Dark'] = {c = Color3.fromRGB(72,70,70), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_Ishi'] = {c = Color3.fromRGB(100,98,92), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_IshiD'] = {c = Color3.fromRGB(86,84,80), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_Laje'] = {c = Color3.fromRGB(136,125,108), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_Path'] = {c = Color3.fromRGB(156,146,128), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_DS_Soot'] = {c = Color3.fromRGB(44,40,40), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_Wall_Dark'] = {c = Color3.fromRGB(128,120,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light'] = {c = Color3.fromRGB(178,170,156), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Summon_DSStar_Glow'] = {c = Color3.fromRGB(162,94,34), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Summon_DSViolet_Glow'] = {c = Color3.fromRGB(96,68,166), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Water_DS_Trough'] = {c = Color3.fromRGB(36,50,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Window_DS_Warm'] = {c = Color3.fromRGB(255,204,140), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wisteria_DS'] = {c = Color3.fromRGB(150,110,205), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wisteria_DS_Deep'] = {c = Color3.fromRGB(112,76,170), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wisteria_DS_Light'] = {c = Color3.fromRGB(186,156,230), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Wood_DS_Dark'] = {c = Color3.fromRGB(58,40,30), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_DS_Lacquer'] = {c = Color3.fromRGB(150,38,30), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_DS_Mid'] = {c = Color3.fromRGB(104,72,48), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_Dark'] = {c = Color3.fromRGB(92,64,47), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_GateOP_Helm'] = {c = Color3.fromRGB(188,110,52), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
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
local FBX = {[1]='ILHA4_02_TERRAIN_9cc4be.fbx', [2]='ILHA4_03_CLEARING_9cc4be.fbx', [3]='ILHA4_04_FORGE_9cc4be.fbx', [4]='ILHA4_05_VILLAGE_9cc4be.fbx', [5]='ILHA4_06_SUMMON_9cc4be.fbx', [6]='ILHA4_07_WATER_9cc4be.fbx', [7]='ILHA4_08_NEXT_ISLAND_9cc4be.fbx', [8]='ILHA4_08_PURCHASE_GATES_9cc4be.fbx', [9]='ILHA4_09_PROPS_9cc4be.fbx', [10]='ILHA4_10_VEGETATION_9cc4be.fbx', [11]='ILHA4_12_VFX_HELPERS_9cc4be.fbx', [12]='ILHA4_18_ENTRY_9cc4be.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['DS_Ter_Bodies__Cliff_DS_Dark']={-1838.059,61.7,1241.8,482.205,35.4,487.67,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Bodies__Dirt_DS_Dark']={-1838.059,66.55,1241.8,482.205,26.3,487.67,1,false,'Dirt_DS_Dark','',''},
  ['DS_Ter_Cliff__Cliff_DS']={-1847.407,64.631,1244.009,521.682,95.105,503.565,1,true,'Cliff_DS','',''},
  ['DS_Ter_Cliff__Cliff_DS_B']={-1846.83,67.244,1244.095,521.552,96.491,504.669,1,true,'Cliff_DS_B','',''},
  ['DS_Ter_Cliff__Cliff_DS_Dark_g-1_5']={-2046.756,52.112,1286.565,122.984,67.415,270.561,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Cliff__Cliff_DS_Dark_g0_4']={-1817.315,52.505,1263.38,462.521,66.631,466.1,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Cliff__Cliff_DS_Dark_g0_7']={-1806.672,41.712,1071.94,386.734,48.216,160.359,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Cliff__Cliff_DS_Dark_g1_4']={-1771.192,41.341,1310.313,300.509,48.957,318.622,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Cliff__Cliff_DS_Moss']={-1850.406,75.685,1242.511,513.017,80.58,501.5,1,true,'Cliff_DS_Moss','',''},
  ['DS_Ter_Cliff__Grass_DS_Deep']={-1847.151,79.911,1244.338,522.194,68.944,504.185,1,false,'Grass_DS_Deep','',''},
  ['DS_Ter_Grass__Grass_DS_g1_5']={-1930.908,70.38,1315.807,288.599,20.0,337.406,1,false,'Grass_DS','',''},
  ['DS_Ter_Grass__Grass_DS_g2_6']={-1809.029,62.495,1196.657,355.062,15.769,355.94,1,false,'Grass_DS','',''},
  ['DS_Ter_Grass__Grass_DS_g2_7']={-1711.019,57.38,1075.663,160.572,6.0,153.237,1,false,'Grass_DS','',''},
  ['DS_Ter_Grass__Grass_DS_B_g0_5']={-1996.918,75.23,1334.356,157.279,10.3,148.504,1,false,'Grass_DS_B','',''},
  ['DS_Ter_Grass__Grass_DS_B_g1_5']={-1919.739,70.23,1268.013,258.391,20.3,433.685,1,false,'Grass_DS_B','',''},
  ['DS_Ter_Grass__Grass_DS_B_g2_5']={-1739.249,63.23,1326.937,107.501,6.3,95.901,1,false,'Grass_DS_B','',''},
  ['DS_Ter_Grass__Grass_DS_B_g2_6']={-1777.618,62.403,1154.111,292.933,15.954,253.891,1,false,'Grass_DS_B','',''},
  ['DS_Ter_Grass__Grass_DS_B_g2_7']={-1709.703,57.23,1075.488,164.14,6.3,153.587,1,false,'Grass_DS_B','',''},
  ['DS_Ter_Grass__Grass_DS_Deep']={-1839.459,66.49,1240.829,423.03,27.78,478.396,1,false,'Grass_DS_Deep','',''},
  ['DS_Ter_Grass__Grass_DS_Dry']={-1902.392,75.38,1269.91,185.907,10.0,370.655,1,false,'Grass_DS_Dry','',''},
  ['DS_Ter_Ground__Dirt_DS']={-1823.535,66.95,1240.476,392.751,26.5,484.946,1,false,'Dirt_DS','',''},
  ['DS_Ter_Ground__Dirt_DS_Dark']={-1838.063,66.95,1247.752,482.12,26.5,475.689,1,false,'Dirt_DS_Dark','',''},
  ['DS_Ter_Ishigaki__Stone_DS']={-1807.308,66.95,1219.425,397.408,26.32,330.512,1,true,'Stone_DS','',''},
  ['DS_Ter_Ishigaki__Stone_DS_B_g1_5']={-1847.915,70.332,1327.108,315.788,21.337,209.719,1,true,'Stone_DS_B','',''},
  ['DS_Ter_Ishigaki__Stone_DS_B_g3_7']={-1656.335,61.326,1094.097,95.285,15.251,90.872,1,false,'Stone_DS_B','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Dark']={-1807.296,66.95,1219.562,397.561,26.5,330.401,1,true,'Stone_DS_Dark','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Ishi_g0_5']={-1939.692,74.949,1305.096,42.463,10.562,33.487,1,true,'Stone_DS_Ishi','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Ishi_g0_6']={-1961.599,69.932,1188.911,86.092,20.61,180.777,1,true,'Stone_DS_Ishi','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Ishi_g1_5']={-1805.659,70.399,1351.754,231.216,21.402,146.202,1,true,'Stone_DS_Ishi','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Ishi_g1_6']={-1858.201,64.977,1266.284,126.072,10.563,30.461,1,true,'Stone_DS_Ishi','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Ishi_g2_6']={-1742.349,62.947,1254.346,97.859,6.592,53.838,1,true,'Stone_DS_Ishi','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Ishi_g3_7']={-1657.79,61.325,1093.416,96.391,15.325,91.109,1,false,'Stone_DS_Ishi','',''},
  ['DS_Ter_Ishigaki__Stone_DS_IshiD']={-1808.222,67.5,1224.071,393.581,27.6,349.893,1,true,'Stone_DS_IshiD','',''},
  ['DS_Ter_Ishigaki__Stone_DS_Path']={-1807.587,70.25,1219.792,398.302,20.579,330.648,1,true,'Stone_DS_Path','',''},
  ['DS_Ter_Keel__Cliff_DS_Dark']={-1846.282,-0.496,1244.295,511.364,88.991,494.474,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Moss__Cliff_DS_Moss']={-1847.896,75.78,1244.351,519.473,91.774,503.697,1,true,'Cliff_DS_Moss','',''},
  ['DS_Ter_Moss__Grass_DS_Deep']={-1850.119,77.86,1239.313,498.86,63.758,486.998,1,false,'Grass_DS_Deep','',''},
  ['DS_Ter_Paving__Stone_DS_Laje_g1_5']={-1878.68,80.155,1356.32,76.467,0.45,78.178,1,true,'Stone_DS_Laje','',''},
  ['DS_Ter_Paving__Stone_DS_Laje_g2_7']={-1713.237,57.594,1072.83,99.24,5.492,86.065,1,true,'Stone_DS_Laje','',''},
  ['DS_Ter_Paving__Stone_DS_Laje_g3_7']={-1632.299,57.16,1050.652,64.485,6.36,74.828,1,false,'Stone_DS_Laje','',''},
  ['DS_Ter_RockWalls__Cliff_DS']={-1942.751,73.973,1262.818,275.93,29.547,380.838,1,true,'Cliff_DS','',''},
  ['DS_Ter_RockWalls__Cliff_DS_B']={-1944.333,74.027,1264.316,281.825,29.654,383.039,1,true,'Cliff_DS_B','',''},
  ['DS_Ter_RockWalls__Cliff_DS_Moss']={-1944.807,76.097,1264.125,280.509,26.226,383.132,1,true,'Cliff_DS_Moss','',''},
  ['DS_Ter_RockWalls__Grass_DS_Deep']={-1940.302,77.356,1268.988,271.032,23.708,372.981,1,false,'Grass_DS_Deep','',''},
  ['DS_Ter_Rocks__Cliff_DS_g-1_5']={-1947.286,83.983,1219.539,307.458,77.966,397.09,1,true,'Cliff_DS','',''},
  ['DS_Ter_Rocks__Cliff_DS_g0_4']={-1821.548,86.957,1264.236,455.94,82.514,439.013,1,true,'Cliff_DS','',''},
  ['DS_Ter_Rocks__Cliff_DS_g0_5']={-2014.252,101.39,1367.801,72.602,54.781,83.565,1,false,'Cliff_DS','',''},
  ['DS_Ter_Rocks__Cliff_DS_B_g-1_5']={-1946.559,81.507,1215.929,310.783,73.014,394.648,1,true,'Cliff_DS_B','',''},
  ['DS_Ter_Rocks__Cliff_DS_B_g0_4']={-1983.699,99.843,1440.902,130.917,51.686,69.319,1,false,'Cliff_DS_B','',''},
  ['DS_Ter_Rocks__Cliff_DS_B_g0_5']={-1823.938,86.743,1247.891,452.787,77.886,435.639,1,true,'Cliff_DS_B','',''},
  ['DS_Ter_Rocks__Cliff_DS_Dark']={-1846.466,50.413,1243.839,504.457,66.574,490.732,1,true,'Cliff_DS_Dark','',''},
  ['DS_Ter_Rocks__Cliff_DS_Moss_g-1_5']={-2031.601,88.409,1283.49,140.699,64.164,294.323,1,true,'Cliff_DS_Moss','',''},
  ['DS_Ter_Rocks__Cliff_DS_Moss_g0_4']={-1989.844,101.751,1439.721,141.561,50.591,71.681,1,false,'Cliff_DS_Moss','',''},
  ['DS_Ter_Rocks__Cliff_DS_Moss_g0_5']={-1864.888,91.692,1372.678,391.474,70.71,186.064,1,true,'Cliff_DS_Moss','',''},
  ['DS_Ter_Rocks__Cliff_DS_Moss_g1_7']={-1796.861,61.609,1150.149,398.633,23.62,263.088,1,true,'Cliff_DS_Moss','',''},
  ['DS_Ter_Rocks__Grass_DS_Deep']={-1847.765,90.259,1252.368,508.373,78.72,462.748,1,false,'Grass_DS_Deep','',''},
  ['DS_Ter_Rocks__Stone_DS_Dark']={-1881.784,56.425,1064.198,18.467,6.35,25.355,1,true,'Stone_DS_Dark','',''},
  ['DS_Clr_EdgeRocks__Stone_DS']={-1837.907,60.7,1169.168,265.628,2.8,214.891,2,true,'Stone_DS','',''},
  ['DS_Clr_EdgeRocks__Stone_DS_B']={-1826.585,60.55,1187.476,240.362,2.5,170.423,2,true,'Stone_DS_B','',''},
  ['DS_Clr_Floor__Dirt_DS_g1_6']={-1843.182,60.08,1165.385,288.764,0.76,229.417,2,false,'Dirt_DS','',''},
  ['DS_Clr_Floor__Dirt_DS_g2_7']={-1743.629,60.08,1109.086,105.353,0.76,116.818,2,false,'Dirt_DS','',''},
  ['DS_Clr_Floor__Dirt_DS_Dark']={-1832.616,59.95,1166.765,290.969,0.5,226.626,2,false,'Dirt_DS_Dark','',''},
  ['DS_Clr_Floor__Grass_DS']={-1836.729,60.38,1165.788,300.373,0.0,228.468,2,false,'Grass_DS','',''},
  ['DS_Clr_Floor__Grass_DS_B']={-1839.243,60.23,1164.833,295.346,0.3,227.257,2,false,'Grass_DS_B','',''},
  ['DS_Clr_Floor__Grass_DS_Deep']={-1832.37,60.38,1165.823,281.797,0.0,228.433,2,false,'Grass_DS_Deep','',''},
  ['DS_Clr_Floor__Grass_DS_Dry']={-1837.877,60.38,1164.129,248.796,0.0,192.921,2,false,'Grass_DS_Dry','',''},
  ['DS_Frg_Coal__Glass_DS_Lantern']={-1864.661,85.425,1359.584,1.042,0.515,1.042,3,false,'Glass_DS_Lantern','','DS_Frg'},
  ['DS_Frg_Coal__Metal_DS_Iron']={-1855.885,84.095,1371.37,17.945,6.41,38.54,3,true,'Metal_DS_Iron','','DS_Frg'},
  ['DS_Frg_Coal__Plaster_DS_Clay']={-1850.466,81.87,1369.947,32.945,3.64,23.966,3,true,'Plaster_DS_Clay','','DS_Frg'},
  ['DS_Frg_Coal__Roof_DS_Ridge']={-1845.906,95.62,1369.955,15.122,3.174,17.309,3,true,'Roof_DS_Ridge','','DS_Frg'},
  ['DS_Frg_Coal__Roof_DS_Tile']={-1849.346,87.536,1365.709,35.078,14.492,36.506,3,true,'Roof_DS_Tile','','DS_Frg'},
  ['DS_Frg_Coal__Rope_DS_Straw']={-1849.265,81.588,1357.995,31.416,2.776,21.127,3,false,'Rope_DS_Straw','','DS_Frg'},
  ['DS_Frg_Coal__Stone_DS_Brick']={-1845.402,82.31,1369.146,11.556,4.42,10.822,3,true,'Stone_DS_Brick','','DS_Frg'},
  ['DS_Frg_Coal__Stone_DS_Dark']={-1845.546,82.45,1369.634,11.494,4.7,11.23,3,false,'Stone_DS_Dark','','DS_Frg'},
  ['DS_Frg_Coal__Window_DS_Warm']={-1864.661,85.425,1359.584,1.042,1.03,1.042,3,false,'Window_DS_Warm','','DS_Frg'},
  ['DS_Frg_Coal__Wood_DS_Dark']={-1851.655,87.272,1378.389,48.038,14.343,53.161,3,true,'Wood_DS_Dark','','DS_Frg'},
  ['DS_Frg_Coal__Wood_DS_Mid']={-1851.601,81.466,1378.118,46.674,2.568,52.248,3,true,'Wood_DS_Mid','','DS_Frg'},
  ['DS_Frg_Ground__Dirt_DS']={-1954.336,80.23,1310.056,81.687,0.22,89.312,3,false,'Dirt_DS','','DS_Frg'},
  ['DS_Frg_Ground__Dirt_DS_Dark']={-1965.063,79.825,1308.069,118.061,0.75,131.866,3,false,'Dirt_DS_Dark','','DS_Frg'},
  ['DS_Frg_Ground__Glass_DS_Lantern']={-1945.442,80.016,1289.62,53.824,12.532,21.971,3,false,'Glass_DS_Lantern','','DS_Frg'},
  ['DS_Frg_Ground__Metal_DS_Iron']={-1965.526,87.531,1284.96,12.989,0.737,12.003,3,false,'Metal_DS_Iron','','DS_Frg'},
  ['DS_Frg_Ground__Stone_DS']={-1961.185,70.675,1303.614,113.543,21.55,125.068,3,true,'Stone_DS','','DS_Frg'},
  ['DS_Frg_Ground__Stone_DS_B']={-1959.931,70.675,1301.629,111.214,21.55,124.861,3,true,'Stone_DS_B','','DS_Frg'},
  ['DS_Frg_Ground__Stone_DS_Dark']={-1961.73,74.64,1304.77,113.331,29.48,123.513,3,true,'Stone_DS_Dark','','DS_Frg'},
  ['DS_Frg_Ground__Stone_DS_Laje']={-1966.549,75.117,1311.374,114.654,10.555,124.228,3,true,'Stone_DS_Laje','','DS_Frg'},
  ['DS_Frg_Ground__Stone_DS_Path']={-1937.577,70.535,1289.728,65.301,19.731,78.31,3,true,'Stone_DS_Path','','DS_Frg'},
  ['DS_Frg_Ground__Window_DS_Warm']={-1965.526,86.025,1284.96,13.655,1.03,12.651,3,false,'Window_DS_Warm','','DS_Frg'},
  ['DS_Frg_Ground__Wood_DS_Dark']={-1941.255,79.58,1300.69,266.835,18.76,167.624,3,true,'Wood_DS_Dark','','DS_Frg'},
  ['DS_Frg_Ground__Wood_DS_Mid']={-1941.255,77.34,1300.7,267.319,11.28,168.116,3,true,'Wood_DS_Mid','','DS_Frg'},
  ['DS_Frg_Hall__Metal_DS_Iron']={-1996.672,86.29,1321.917,2.206,0.7,2.174,3,false,'Metal_DS_Iron','','DS_Frg'},
  ['DS_Frg_Hall__Plaster_DS_Clay']={-1983.396,94.055,1339.116,51.173,23.91,52.653,3,true,'Plaster_DS_Clay','','DS_Frg'},
  ['DS_Frg_Hall__Plaster_DS_Shoji']={-1984.384,97.937,1340.88,38.484,27.374,36.447,3,true,'Plaster_DS_Shoji','','DS_Frg'},
  ['DS_Frg_Hall__Roof_DS_Ridge']={-1983.396,106.14,1339.116,65.238,18.832,66.717,3,true,'Roof_DS_Ridge','','DS_Frg'},
  ['DS_Frg_Hall__Roof_DS_Tile']={-1983.396,104.64,1339.116,63.362,18.448,64.841,3,true,'Roof_DS_Tile','','DS_Frg'},
  ['DS_Frg_Hall__Rope_DS_Straw']={-1968.351,92.795,1326.595,10.161,3.881,11.886,3,false,'Rope_DS_Straw','','DS_Frg'},
  ['DS_Frg_Hall__Stone_DS']={-1970.105,80.25,1327.964,11.862,0.7,12.651,3,false,'Stone_DS','','DS_Frg'},
  ['DS_Frg_Hall__Stone_DS_Brick']={-1970.171,86.815,1327.92,11.555,12.37,12.547,3,true,'Stone_DS_Brick','','DS_Frg'},
  ['DS_Frg_Hall__Stone_DS_Dark']={-1983.396,89.93,1339.116,53.461,19.66,54.941,3,true,'Stone_DS_Dark','','DS_Frg'},
  ['DS_Frg_Hall__Stone_DS_Soot']={-1983.396,95.862,1339.116,52.732,31.524,54.211,3,true,'Stone_DS_Soot','','DS_Frg'},
  ['DS_Frg_Hall__Window_DS_Warm']={-1982.8,86.45,1339.049,41.499,4.4,43.326,3,false,'Window_DS_Warm','','DS_Frg'},
  ['DS_Frg_Hall__Wood_DS_Dark']={-1983.396,97.497,1339.116,64.042,32.194,65.521,3,true,'Wood_DS_Dark','','DS_Frg'},
  ['DS_Frg_Hall__Wood_DS_Mid']={-1983.396,86.38,1339.116,51.235,8.56,52.714,3,true,'Wood_DS_Mid','','DS_Frg'},
  ['DS_Frg_Houses__Cloth_DS_Red']={-1943.137,88.876,1373.217,11.834,3.648,13.995,3,false,'Cloth_DS_Red','','DS_Frg'},
  ['DS_Frg_Houses__Metal_DS_Iron']={-1942.915,86.29,1374.649,9.749,0.5,11.233,3,false,'Metal_DS_Iron','','DS_Frg'},
  ['DS_Frg_Houses__Plaster_DS_Ash']={-1951.503,93.954,1380.236,33.748,23.709,34.857,3,true,'Plaster_DS_Ash','','DS_Frg'},
  ['DS_Frg_Houses__Plaster_DS_Clay']={-2012.541,113.075,1315.272,18.101,32.35,18.101,3,true,'Plaster_DS_Clay','','DS_Frg'},
  ['DS_Frg_Houses__Roof_DS_Ridge']={-1977.969,117.912,1352.084,99.619,42.895,104.099,3,true,'Roof_DS_Ridge','','DS_Frg'},
  ['DS_Frg_Houses__Roof_DS_Tile']={-1977.969,114.457,1352.084,97.743,46.806,102.223,3,true,'Roof_DS_Tile','','DS_Frg'},
  ['DS_Frg_Houses__Stone_DS']={-1978.453,112.936,1351.565,91.401,66.152,95.89,3,true,'Stone_DS','','DS_Frg'},
  ['DS_Frg_Houses__Stone_DS_B']={-1978.949,112.936,1351.198,90.103,66.152,94.741,3,true,'Stone_DS_B','','DS_Frg'},
  ['DS_Frg_Houses__Stone_DS_Dark']={-1978.04,114.8,1352.014,89.684,70.0,94.165,3,true,'Stone_DS_Dark','','DS_Frg'},
  ['DS_Frg_Houses__Stone_DS_Path']={-1941.515,81.0,1371.996,11.885,2.1,13.715,3,true,'Stone_DS_Path','','DS_Frg'},
  ['DS_Frg_Houses__Stone_DS_Soot']={-2012.541,140.7,1315.272,8.312,23.0,8.312,3,true,'Stone_DS_Soot','','DS_Frg'},
  ['DS_Frg_Houses__Window_DS_Warm']={-1978.113,103.125,1349.865,79.502,37.75,85.026,3,false,'Window_DS_Warm','','DS_Frg'},
  ['DS_Frg_Houses__Wood_DS_Dark']={-1977.956,109.405,1352.098,98.446,56.01,102.926,3,true,'Wood_DS_Dark','','DS_Frg'},
  ['DS_Frg_Houses__Wood_DS_Mid']={-1975.75,98.7,1351.943,86.26,33.8,91.302,3,true,'Wood_DS_Mid','','DS_Frg'},
  ['DS_Frg_Mill__Metal_DS_Iron']={-2013.612,88.594,1288.792,8.82,5.709,22.562,3,false,'Metal_DS_Iron','','DS_Frg'},
  ['DS_Frg_Mill__Plaster_DS']={-2018.184,86.175,1286.067,6.401,8.55,7.547,3,false,'Plaster_DS','','DS_Frg'},
  ['DS_Frg_Mill__Plaster_DS_Clay']={-2023.125,90.4,1290.213,30.657,17.0,30.711,3,true,'Plaster_DS_Clay','','DS_Frg'},
  ['DS_Frg_Mill__Roof_DS_Ridge']={-2027.863,99.146,1285.192,31.687,11.991,29.278,3,true,'Roof_DS_Ridge','','DS_Frg'},
  ['DS_Frg_Mill__Roof_DS_Tile']={-2051.546,92.25,1287.594,94.643,21.7,43.373,3,true,'Roof_DS_Tile','','DS_Frg'},
  ['DS_Frg_Mill__Stone_DS']={-2053.16,91.765,1282.9,93.049,24.67,47.368,3,true,'Stone_DS','','DS_Frg'},
  ['DS_Frg_Mill__Stone_DS_B']={-2053.278,91.765,1282.917,92.812,24.67,47.571,3,true,'Stone_DS_B','','DS_Frg'},
  ['DS_Frg_Mill__Stone_DS_Dark']={-2023.125,80.35,1290.213,32.234,1.1,32.234,3,true,'Stone_DS_Dark','','DS_Frg'},
  ['DS_Frg_Mill__Stone_DS_Path']={-2014.445,80.9,1301.007,4.453,1.9,5.175,3,false,'Stone_DS_Path','','DS_Frg'},
  ['DS_Frg_Mill__Window_DS_Warm']={-2024.568,85.175,1292.389,18.258,6.55,23.269,3,false,'Window_DS_Warm','','DS_Frg'},
  ['DS_Frg_Mill__Wood_DS_Dark']={-2050.551,92.015,1287.594,92.654,24.23,43.373,3,true,'Wood_DS_Dark','','DS_Frg'},
  ['DS_Frg_Mill__Wood_DS_Mid']={-2052.306,92.778,1288.004,87.593,22.356,33.851,3,true,'Wood_DS_Mid','','DS_Frg'},
  ['DS_Frg_Smithy__Cloth_DS_Indigo']={-1969.926,82.592,1327.333,27.432,1.927,24.437,3,true,'Cloth_DS_Indigo','','DS_Frg'},
  ['DS_Frg_Smithy__Cloth_DS_Red']={-1969.926,83.451,1332.819,27.432,3.644,35.407,3,true,'Cloth_DS_Red','','DS_Frg'},
  ['DS_Frg_Smithy__Dirt_DS_Dark']={-1925.521,82.12,1343.088,166.009,4.24,59.104,3,false,'Dirt_DS_Dark','','DS_Frg'},
  ['DS_Frg_Smithy__Ember_DS_Glow']={-1924.099,81.475,1338.148,165.146,2.55,58.532,3,false,'Ember_DS_Glow','','DS_Frg'},
  ['DS_Frg_Smithy__Fire_DS_Glow']={-1989.87,83.65,1344.061,2.611,1.9,2.754,3,false,'Fire_DS_Glow','','DS_Frg'},
  ['DS_Frg_Smithy__Glass_DS_Lantern']={-1967.921,88.5,1326.132,11.6,0.293,13.671,3,false,'Glass_DS_Lantern','','DS_Frg'},
  ['DS_Frg_Smithy__Metal_DS_Brass']={-1970.494,83.506,1332.533,27.119,4.053,41.915,3,true,'Metal_DS_Brass','','DS_Frg'},
  ['DS_Frg_Smithy__Metal_DS_Iron']={-1971.374,84.812,1332.821,57.96,9.215,36.051,3,true,'Metal_DS_Iron','','DS_Frg'},
  ['DS_Frg_Smithy__Metal_DS_Steel']={-1964.959,82.46,1328.602,44.371,1.828,33.541,3,true,'Metal_DS_Steel','','DS_Frg'},
  ['DS_Frg_Smithy__Plaster_DS_Clay']={-1989.495,98.608,1344.451,16.272,20.217,15.804,3,true,'Plaster_DS_Clay','','DS_Frg'},
  ['DS_Frg_Smithy__Plaster_DS_Kura']={-1971.664,84.638,1332.821,30.82,6.276,35.34,3,true,'Plaster_DS_Kura','','DS_Frg'},
  ['DS_Frg_Smithy__Rope_DS_Straw']={-1972.183,84.363,1343.743,60.093,8.146,18.093,3,false,'Rope_DS_Straw','','DS_Frg'},
  ['DS_Frg_Smithy__Stone_DS_Brick']={-1990.177,84.45,1318.264,35.738,8.7,67.17,3,true,'Stone_DS_Brick','','DS_Frg'},
  ['DS_Frg_Smithy__Stone_DS_Dark']={-1996.133,84.1,1328.771,24.171,1.9,43.669,3,true,'Stone_DS_Dark','','DS_Frg'},
  ['DS_Frg_Smithy__Stone_DS_Soot']={-1974.701,88.3,1330.619,65.119,16.4,45.699,3,true,'Stone_DS_Soot','','DS_Frg'},
  ['DS_Frg_Smithy__Water_DS_Trough']={-1972.929,80.885,1316.735,67.187,1.53,62.378,3,false,'Water_DS_Trough','','DS_Frg'},
  ['DS_Frg_Smithy__Window_DS_Warm']={-1967.921,88.5,1326.132,11.57,0.88,13.641,3,false,'Window_DS_Warm','','DS_Frg'},
  ['DS_Frg_Smithy__Wood_DS_Dark']={-1975.3,93.086,1320.447,68.642,25.931,74.883,3,true,'Wood_DS_Dark','','DS_Frg'},
  ['DS_Frg_Smithy__Wood_DS_Mid']={-1975.358,83.272,1316.541,68.813,6.156,67.358,3,true,'Wood_DS_Mid','','DS_Frg'},
  ['DS_Vil_HouseV1__Cloth_DS_Indigo']={-1667.658,67.24,1159.632,12.681,7.36,12.145,4,false,'Cloth_DS_Indigo','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Ember_DS_Glow']={-1664.621,65.193,1158.218,0.413,0.226,0.514,4,false,'Ember_DS_Glow','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Glass_DS_Lantern']={-1667.982,69.41,1158.921,6.219,0.327,8.38,4,false,'Glass_DS_Lantern','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Metal_DS_Iron']={-1666.894,68.06,1158.921,7.317,6.4,7.307,4,true,'Metal_DS_Iron','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Plaster_DS_Ochre']={-1668.353,67.788,1158.255,15.784,15.675,17.259,4,true,'Plaster_DS_Ochre','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Roof_DS_Ridge']={-1667.818,71.799,1159.036,27.503,13.639,28.486,4,true,'Roof_DS_Ridge','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Roof_DS_Tile']={-1667.818,73.702,1159.036,25.553,4.947,26.535,4,true,'Roof_DS_Tile','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Stone_DS']={-1667.818,60.53,1159.159,18.196,1.34,18.932,4,true,'Stone_DS','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Stone_DS_B']={-1668.275,63.365,1158.662,16.817,7.01,18.43,4,true,'Stone_DS_B','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Stone_DS_Dark']={-1667.818,64.11,1159.036,17.447,8.62,18.429,4,true,'Stone_DS_Dark','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Window_DS_Warm']={-1667.368,66.975,1158.921,7.402,5.85,8.336,4,false,'Window_DS_Warm','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Wood_DS_Dark']={-1667.818,68.21,1159.036,26.27,15.081,27.252,4,true,'Wood_DS_Dark','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV1__Wood_DS_Mid']={-1669.227,66.275,1157.841,17.598,9.89,17.75,4,true,'Wood_DS_Mid','','DS_Vil_HouseV1'},
  ['DS_Vil_HouseV2__Cloth_DS_Indigo']={-1686.743,69.276,1188.452,3.346,3.648,5.396,4,false,'Cloth_DS_Indigo','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Metal_DS_Iron']={-1685.474,66.69,1187.753,1.338,0.5,2.598,4,false,'Metal_DS_Iron','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Plaster_DS']={-1676.853,71.691,1194.162,26.672,18.382,25.207,4,true,'Plaster_DS','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Roof_DS_Ridge']={-1676.853,79.238,1194.162,39.762,9.273,38.298,4,true,'Roof_DS_Ridge','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Roof_DS_Tile']={-1676.853,77.437,1194.162,37.751,7.99,36.287,4,true,'Roof_DS_Tile','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Stone_DS']={-1676.71,60.83,1193.426,30.56,1.94,30.296,4,true,'Stone_DS','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Stone_DS_B']={-1676.785,60.83,1194.23,30.137,1.94,28.402,4,true,'Stone_DS_B','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Stone_DS_Dark']={-1676.853,60.65,1194.162,29.255,1.7,27.791,4,true,'Stone_DS_Dark','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Stone_DS_Path']={-1679.276,61.2,1185.278,23.017,2.5,8.831,4,true,'Stone_DS_Path','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Window_DS_Warm']={-1678.253,67.705,1192.966,22.391,6.11,20.719,4,false,'Window_DS_Warm','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Wood_DS_Dark']={-1676.853,70.753,1194.162,38.483,20.506,37.018,4,true,'Wood_DS_Dark','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV2__Wood_DS_Mid']={-1675.785,66.495,1192.402,28.877,9.13,28.196,4,true,'Wood_DS_Mid','','DS_Vil_HouseV2'},
  ['DS_Vil_HouseV3__Metal_DS_Iron']={-1703.305,68.794,1222.061,16.991,5.709,7.866,4,false,'Metal_DS_Iron','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Plaster_DS']={-1703.127,66.375,1225.013,3.718,8.55,6.908,4,false,'Plaster_DS','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Plaster_DS_Ash']={-1700.944,70.65,1226.125,20.446,17.1,22.002,4,true,'Plaster_DS_Ash','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Roof_DS_Ridge']={-1700.944,79.022,1226.125,12.888,6.344,21.806,4,true,'Roof_DS_Ridge','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Roof_DS_Tile']={-1700.944,75.636,1226.125,28.075,8.272,28.818,4,true,'Roof_DS_Tile','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Stone_DS']={-1700.944,60.955,1225.58,22.573,2.19,24.919,4,true,'Stone_DS','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Stone_DS_B']={-1701.158,60.63,1226.125,19.474,1.54,24.321,4,true,'Stone_DS_B','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Stone_DS_Dark']={-1700.944,60.45,1226.125,21.83,1.3,23.578,4,true,'Stone_DS_Dark','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Window_DS_Warm']={-1699.743,65.75,1228.849,10.407,7.3,14.012,4,false,'Window_DS_Warm','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Wood_DS_Dark']={-1700.944,69.775,1226.125,28.075,19.109,28.818,4,true,'Wood_DS_Dark','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV3__Wood_DS_Mid']={-1701.641,66.365,1226.304,20.811,9.129,20.807,4,true,'Wood_DS_Mid','','DS_Vil_HouseV3'},
  ['DS_Vil_HouseV4__Metal_DS_Iron']={-1736.591,75.985,1269.139,13.374,14.67,14.635,4,true,'Metal_DS_Iron','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Plaster_DS_Kura']={-1736.648,80.086,1269.139,24.385,22.972,24.37,4,true,'Plaster_DS_Kura','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Roof_DS_Ridge']={-1736.648,81.815,1269.139,17.692,25.243,17.939,4,true,'Roof_DS_Ridge','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Roof_DS_Tile']={-1736.648,84.025,1269.139,24.462,15.936,24.425,4,true,'Roof_DS_Tile','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Stone_DS']={-1737.026,67.25,1269.172,19.797,2.78,20.356,4,true,'Stone_DS','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Stone_DS_B']={-1735.068,67.23,1269.139,17.392,2.74,20.98,4,true,'Stone_DS_B','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Stone_DS_Dark']={-1736.648,67.05,1269.139,19.431,2.5,19.678,4,false,'Stone_DS_Dark','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Stone_DS_Path']={-1729.171,67.05,1263.185,4.768,2.2,4.224,4,false,'Stone_DS_Path','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Window_DS_Warm']={-1731.957,81.9,1269.721,1.915,2.8,11.28,4,false,'Window_DS_Warm','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV4__Wood_DS_Dark']={-1736.648,82.768,1269.139,24.462,17.449,24.425,4,true,'Wood_DS_Dark','','DS_Vil_HouseV4'},
  ['DS_Vil_HouseV5__Cloth_DS_Indigo']={-1769.331,75.476,1281.715,5.198,3.648,3.687,4,false,'Cloth_DS_Indigo','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Metal_DS_Iron']={-1767.883,72.89,1281.643,2.271,0.5,1.87,4,false,'Metal_DS_Iron','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Plaster_DS_Ochre']={-1764.622,82.136,1288.695,25.703,26.871,24.084,4,true,'Plaster_DS_Ochre','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Roof_DS_Ridge']={-1764.622,94.117,1288.695,39.006,8.896,37.387,4,true,'Roof_DS_Ridge','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Roof_DS_Tile']={-1764.622,87.888,1288.695,37.042,16.466,35.423,4,true,'Roof_DS_Tile','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Stone_DS']={-1764.622,66.93,1288.785,29.467,2.14,27.75,4,true,'Stone_DS','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Stone_DS_B']={-1764.388,66.93,1288.606,28.687,2.14,27.75,4,true,'Stone_DS_B','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Stone_DS_Dark']={-1764.622,66.75,1288.695,28.408,1.9,26.788,4,true,'Stone_DS_Dark','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Stone_DS_Path']={-1770.686,67.3,1279.123,5.503,2.7,6.574,4,false,'Stone_DS_Path','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Window_DS_Warm']={-1763.317,78.275,1288.122,21.127,18.65,17.904,4,false,'Window_DS_Warm','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Wood_DS_Dark']={-1764.622,81.848,1288.695,37.754,27.696,36.135,4,true,'Wood_DS_Dark','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV5__Wood_DS_Mid']={-1765.308,75.4,1287.611,26.698,14.0,26.318,4,true,'Wood_DS_Mid','','DS_Vil_HouseV5'},
  ['DS_Vil_HouseV6__Bamboo_DS_Dry']={-1802.997,72.45,1324.33,59.568,12.7,60.778,4,true,'Bamboo_DS_Dry','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Cloth_DS_Indigo']={-1787.741,72.54,1342.516,27.729,7.36,24.56,4,true,'Cloth_DS_Indigo','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Ember_DS_Glow']={-1797.788,69.1,1338.735,1.422,0.252,0.729,4,false,'Ember_DS_Glow','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Glass_DS_Lantern']={-1803.481,70.005,1339.156,18.396,3.63,28.72,4,false,'Glass_DS_Lantern','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Metal_DS_Iron']={-1800.163,70.37,1325.428,39.85,6.18,41.516,4,true,'Metal_DS_Iron','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Plaster_DS']={-1799.757,74.225,1327.528,53.099,14.05,55.872,4,true,'Plaster_DS','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Plaster_DS_Shoji']={-1790.637,75.91,1338.59,21.654,10.18,18.188,4,true,'Plaster_DS_Shoji','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Roof_DS_Ridge']={-1796.344,80.721,1330.974,60.9,23.434,63.608,4,true,'Roof_DS_Ridge','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Roof_DS_Tile']={-1796.948,80.205,1330.306,60.232,19.58,63.069,4,true,'Roof_DS_Tile','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Stone_DS']={-1798.921,68.53,1328.357,55.003,5.34,57.822,4,true,'Stone_DS','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Stone_DS_B']={-1796.153,68.04,1328.638,52.262,4.36,57.631,4,true,'Stone_DS_B','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Stone_DS_Dark']={-1790.315,69.225,1338.973,37.077,6.85,35.844,4,true,'Stone_DS_Dark','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Stone_DS_Path']={-1794.01,66.875,1318.836,43.594,1.85,21.297,4,true,'Stone_DS_Path','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Window_DS_Warm']={-1789.025,74.625,1340.012,30.092,10.95,29.361,4,false,'Window_DS_Warm','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Wood_DS_Dark']={-1799.814,77.785,1328.057,66.638,23.57,68.241,4,true,'Wood_DS_Dark','','DS_Vil_HouseV6'},
  ['DS_Vil_HouseV6__Wood_DS_Mid']={-1795.765,73.96,1329.15,51.578,14.92,52.69,4,true,'Wood_DS_Mid','','DS_Vil_HouseV6'},
  ['DS_Vil_StreetHigh__Dirt_DS']={-1783.334,65.92,1269.142,104.714,0.64,66.825,4,false,'Dirt_DS','',''},
  ['DS_Vil_StreetHigh__Glass_DS_Lantern']={-1779.669,72.025,1276.384,93.499,0.515,62.236,4,false,'Glass_DS_Lantern','',''},
  ['DS_Vil_StreetHigh__Metal_DS_Iron']={-1779.659,73.531,1276.397,92.852,0.737,61.593,4,true,'Metal_DS_Iron','',''},
  ['DS_Vil_StreetHigh__Roof_DS_Tile']={-1779.182,73.953,1276.889,96.313,2.853,65.106,4,true,'Roof_DS_Tile','',''},
  ['DS_Vil_StreetHigh__Stone_DS']={-1794.833,73.325,1283.982,127.776,14.85,76.085,4,true,'Stone_DS','',''},
  ['DS_Vil_StreetHigh__Stone_DS_B']={-1817.204,71.769,1287.048,72.095,11.739,69.739,4,true,'Stone_DS_B','',''},
  ['DS_Vil_StreetHigh__Stone_DS_Dark']={-1842.734,72.89,1307.244,30.522,13.98,27.86,4,true,'Stone_DS_Dark','',''},
  ['DS_Vil_StreetHigh__Stone_DS_Laje']={-1781.956,66.315,1272.627,99.523,0.45,70.981,4,true,'Stone_DS_Laje','',''},
  ['DS_Vil_StreetHigh__Stone_DS_Path']={-1787.969,73.075,1279.976,140.104,14.25,82.458,4,true,'Stone_DS_Path','',''},
  ['DS_Vil_StreetHigh__Window_DS_Warm']={-1779.669,72.025,1276.384,93.499,1.03,62.236,4,false,'Window_DS_Warm','',''},
  ['DS_Vil_StreetHigh__Wood_DS_Dark']={-1783.858,70.467,1269.526,105.165,8.985,79.337,4,true,'Wood_DS_Dark','',''},
  ['DS_Vil_StreetHigh__Wood_DS_Mid']={-1788.142,67.89,1258.713,96.429,1.4,57.385,4,true,'Wood_DS_Mid','',''},
  ['DS_Vil_StreetLow__Bamboo_DS_Dry']={-1738.315,64.376,1188.349,4.772,3.173,14.26,4,false,'Bamboo_DS_Dry','',''},
  ['DS_Vil_StreetLow__Dirt_DS']={-1696.378,59.92,1172.682,60.483,0.64,122.407,4,false,'Dirt_DS','',''},
  ['DS_Vil_StreetLow__Glass_DS_Lantern']={-1707.262,64.34,1181.17,71.031,7.485,104.717,4,false,'Glass_DS_Lantern','',''},
  ['DS_Vil_StreetLow__Metal_DS_Iron']={-1704.47,66.415,1181.158,64.902,6.57,104.135,4,true,'Metal_DS_Iron','',''},
  ['DS_Vil_StreetLow__Roof_DS_Ridge']={-1736.613,68.285,1188.31,9.414,5.391,18.035,4,true,'Roof_DS_Ridge','',''},
  ['DS_Vil_StreetLow__Roof_DS_Tile']={-1705.882,67.688,1181.711,72.454,6.985,107.592,4,true,'Roof_DS_Tile','',''},
  ['DS_Vil_StreetLow__Stone_DS']={-1734.257,63.325,1192.536,140.023,6.85,129.522,4,true,'Stone_DS','',''},
  ['DS_Vil_StreetLow__Stone_DS_B']={-1734.465,63.325,1194.104,139.393,6.85,126.206,4,true,'Stone_DS_B','',''},
  ['DS_Vil_StreetLow__Stone_DS_Dark']={-1734.925,62.89,1194.214,136.96,5.98,124.713,4,true,'Stone_DS_Dark','',''},
  ['DS_Vil_StreetLow__Stone_DS_Laje']={-1704.647,60.305,1173.297,72.45,0.47,119.766,4,true,'Stone_DS_Laje','',''},
  ['DS_Vil_StreetLow__Stone_DS_Path']={-1737.031,63.075,1184.668,132.993,6.25,143.857,4,true,'Stone_DS_Path','',''},
  ['DS_Vil_StreetLow__Window_DS_Warm']={-1694.88,66.925,1181.17,46.267,2.83,104.717,4,false,'Window_DS_Warm','',''},
  ['DS_Vil_StreetLow__Wood_DS_Dark']={-1705.996,65.368,1181.703,72.226,10.785,107.12,4,true,'Wood_DS_Dark','',''},
  ['DS_Vil_StreetLow__Wood_DS_Mid']={-1714.138,62.705,1186.043,52.735,3.19,22.931,4,true,'Wood_DS_Mid','',''},
  ['DS_Sum_Cloth__Cloth_DS_Indigo']={-1963.38,85.985,1080.619,36.865,27.03,23.206,5,true,'Cloth_DS_Indigo','','DS_Sum'},
  ['DS_Sum_Cloth__Wood_DS_Dark']={-1958.664,100.0,1079.273,25.035,0.6,21.118,5,true,'Wood_DS_Dark','','DS_Sum'},
  ['DS_Sum_Glow__Crystal_SumPortal_Glow']={-1961.113,87.525,1076.298,13.162,26.75,11.653,5,false,'Crystal_SumPortal_Glow','','DS_Sum'},
  ['DS_Sum_Glow__Glass_DS_Lantern']={-1957.258,85.516,1088.818,50.445,26.583,39.013,5,false,'Glass_DS_Lantern','','DS_Sum'},
  ['DS_Sum_Glow__Summon_DSStar_Glow']={-1961.113,88.333,1076.308,13.248,21.834,11.547,5,false,'Summon_DSStar_Glow','','DS_Sum'},
  ['DS_Sum_Glow__Summon_DSViolet_Glow']={-1960.728,89.6,1076.698,10.546,31.1,12.136,5,false,'Summon_DSViolet_Glow','','DS_Sum'},
  ['DS_Sum_Metal__Metal_DS_Iron']={-1966.891,86.805,1078.188,31.711,26.03,18.207,5,true,'Metal_DS_Iron','','DS_Sum'},
  ['DS_Sum_Metal__Metal_Gold_DS']={-1949.86,87.087,1096.716,73.938,46.406,71.304,5,true,'Metal_Gold_DS','','DS_Sum'},
  ['DS_Sum_Sphere_Frame__Metal_Gold_DS']={-1961.113,118.495,1076.308,19.127,23.61,19.127,5,true,'Metal_Gold_DS','','DS_Sum'},
  ['DS_Sum_Sphere_Frame__Summon_DSViolet_Glow']={-1961.113,127.5,1076.308,1.201,1.4,1.103,5,false,'Summon_DSViolet_Glow','','DS_Sum'},
  ['DS_Sum_Stone__Cliff_DS']={-1961.257,90.25,1076.135,21.873,33.42,21.448,5,true,'Cliff_DS','','DS_Sum'},
  ['DS_Sum_Stone__Stone_DS']={-1943.76,68.844,1098.058,68.121,18.669,76.127,5,true,'Stone_DS','','DS_Sum'},
  ['DS_Sum_Stone__Stone_DS_B']={-1947.172,68.595,1093.819,57.72,18.17,64.074,5,true,'Stone_DS_B','','DS_Sum'},
  ['DS_Sum_Stone__Stone_DS_Dark']={-1951.279,83.53,1094.016,70.326,47.86,67.796,5,true,'Stone_DS_Dark','','DS_Sum'},
  ['DS_Sum_Stone__Stone_DS_Path']={-1941.218,67.435,1099.883,45.392,13.531,51.127,5,true,'Stone_DS_Path','','DS_Sum'},
  ['DS_Sum_Wisteria__Bark_DS']={-1954.107,74.827,1084.955,55.754,10.065,49.348,5,true,'Bark_DS','','DS_Sum'},
  ['DS_Sum_Wisteria__Leaf_DS_Broad']={-1954.126,79.448,1085.079,59.305,2.379,53.063,5,false,'Leaf_DS_Broad','','DS_Sum'},
  ['DS_Sum_Wisteria__Wisteria_DS']={-1953.959,77.746,1085.06,57.817,2.286,51.116,5,false,'Wisteria_DS','','DS_Sum'},
  ['DS_Sum_Wisteria__Wisteria_DS_Deep']={-1954.116,78.617,1084.885,59.699,2.817,53.253,5,false,'Wisteria_DS_Deep','','DS_Sum'},
  ['DS_Sum_Wisteria__Wisteria_DS_Light']={-1953.908,76.805,1085.189,57.915,2.932,51.13,5,false,'Wisteria_DS_Light','','DS_Sum'},
  ['DS_Sum_Wood__Roof_DS_Ridge']={-1981.872,79.316,1086.416,11.47,3.908,11.547,5,true,'Roof_DS_Ridge','','DS_Sum'},
  ['DS_Sum_Wood__Roof_DS_Tile']={-1981.872,78.72,1086.416,12.03,3.46,12.202,5,false,'Roof_DS_Tile','','DS_Sum'},
  ['DS_Sum_Wood__Wood_DS_Dark']={-1949.702,69.799,1092.362,76.661,20.402,83.877,5,true,'Wood_DS_Dark','','DS_Sum'},
  ['DS_Sum_Wood__Wood_DS_Mid']={-1949.406,66.128,1092.329,75.498,12.044,83.405,5,true,'Wood_DS_Mid','','DS_Sum'},
  ['DS_Water_Stone__Bamboo_DS_Dry']={-1909.616,61.125,1124.019,1.885,2.25,0.804,6,false,'Bamboo_DS_Dry','',''},
  ['DS_Water_Stone__Cliff_DS']={-1963.335,70.275,1170.177,113.7,21.65,94.092,6,true,'Cliff_DS','',''},
  ['DS_Water_Stone__Cliff_DS_B']={-1961.298,70.371,1171.23,108.958,21.842,96.543,6,true,'Cliff_DS_B','',''},
  ['DS_Water_Stone__Cliff_DS_Moss']={-1946.002,68.062,1134.913,146.233,27.476,168.954,6,true,'Cliff_DS_Moss','',''},
  ['DS_Water_Stone__Dirt_DS']={-1992.44,60.542,1199.907,52.586,0.923,39.78,6,false,'Dirt_DS','',''},
  ['DS_Water_Stone__Dirt_DS_Dark']={-1991.814,60.487,1196.732,50.922,1.054,43.128,6,false,'Dirt_DS_Dark','',''},
  ['DS_Water_Stone__Grass_DS_B']={-1980.74,60.547,1188.572,32.404,0.934,30.919,6,false,'Grass_DS_B','',''},
  ['DS_Water_Stone__Stone_DS_g0_6']={-1982.122,70.161,1193.396,125.394,21.622,136.94,6,true,'Stone_DS','',''},
  ['DS_Water_Stone__Stone_DS_g1_7']={-1896.294,60.053,1102.612,48.41,1.407,56.737,6,true,'Stone_DS','',''},
  ['DS_Water_Stone__Stone_DS_B']={-1957.756,70.169,1170.873,174.206,21.638,189.015,6,true,'Stone_DS_B','',''},
  ['DS_Water_Stone__Stone_DS_Dark']={-1945.206,66.902,1133.521,144.764,28.203,166.875,6,true,'Stone_DS_Dark','',''},
  ['DS_Exit_AnchorGuard__Bamboo_DS_Dry']={-2054.068,82.617,1551.238,16.166,1.894,11.519,7,false,'Bamboo_DS_Dry','','DS_Exit_AnchorGuard'},
  ['DS_Exit_AnchorGuard__Plaster_DS_Kura']={-2054.076,81.277,1551.308,8.739,1.955,6.136,7,false,'Plaster_DS_Kura','','DS_Exit_AnchorGuard'},
  ['DS_Exit_Bridge__Metal_DS_Rust']={-2032.39,84.99,1518.399,70.76,1.8,85.421,7,false,'Metal_DS_Rust','',''},
  ['DS_Exit_Bridge__Stone_DS']={-2045.69,80.33,1538.582,44.179,0.58,45.074,7,false,'Stone_DS','',''},
  ['DS_Exit_Bridge__Stone_DS_B']={-2043.206,80.33,1539.607,43.9,0.58,42.986,7,false,'Stone_DS_B','',''},
  ['DS_Exit_Bridge__Stone_DS_Dark']={-2045.787,80.15,1539.471,33.427,0.4,35.932,7,false,'Stone_DS_Dark','',''},
  ['DS_Exit_Bridge__Stone_DS_Path']={-2047.959,80.15,1540.749,35.202,0.4,37.1,7,false,'Stone_DS_Path','',''},
  ['DS_Exit_Bridge__Wood_DS_Dark']={-2032.1,77.025,1517.95,70.948,15.25,85.929,7,false,'Wood_DS_Dark','',''},
  ['DS_Exit_Bridge__Wood_DS_Mid']={-2021.009,76.898,1504.084,47.488,6.805,56.967,7,false,'Wood_DS_Mid','',''},
  ['DS_Exit_Ferns__Leaf_DS_Shrub']={-2012.57,74.709,1490.735,40.214,9.826,37.891,7,false,'Leaf_DS_Shrub','',''},
  ['DS_Exit_Path__Glass_DS_Lantern']={-1939.016,85.965,1435.677,88.125,0.515,51.584,7,false,'Glass_DS_Lantern','',''},
  ['DS_Exit_Path__Metal_DS_Iron']={-1939.042,87.471,1435.714,87.556,0.737,50.992,7,false,'Metal_DS_Iron','',''},
  ['DS_Exit_Path__Stone_DS_B']={-1951.753,84.55,1446.919,117.458,9.54,75.915,7,false,'Stone_DS_B','',''},
  ['DS_Exit_Path__Stone_DS_Path']={-1947.612,80.35,1438.498,117.872,0.82,84.771,7,false,'Stone_DS_Path','',''},
  ['DS_Exit_Path__Window_DS_Warm']={-1939.016,85.965,1435.677,88.125,1.03,51.584,7,false,'Window_DS_Warm','',''},
  ['DS_Exit_Path__Wood_DS_Dark']={-1938.449,84.67,1435.656,90.354,8.46,52.26,7,false,'Wood_DS_Dark','',''},
  ['DS_Exit_Rock__Cliff_DS']={-2041.629,0.401,1530.734,74.788,137.199,81.767,7,false,'Cliff_DS','',''},
  ['DS_Exit_Rock__Cliff_DS_B']={-2041.633,-3.95,1531.062,73.795,142.1,83.044,7,false,'Cliff_DS_B','',''},
  ['DS_Exit_Rock__Cliff_DS_Dark']={-2040.691,-3.117,1530.269,67.452,134.58,78.307,7,false,'Cliff_DS_Dark','',''},
  ['DS_Exit_Rock__Cliff_DS_Moss']={-2041.437,68.45,1529.913,61.843,2.7,70.081,7,false,'Cliff_DS_Moss','',''},
  ['DS_Exit_Rock__Stone_DS']={-2028.928,73.027,1514.423,80.027,13.926,97.63,7,false,'Stone_DS','',''},
  ['DS_Exit_Rock__Stone_DS_B']={-2029.601,73.035,1514.545,80.636,13.925,94.715,7,false,'Stone_DS_B','',''},
  ['DS_Exit_Rock__Stone_DS_Dark']={-2029.385,72.99,1514.413,80.628,14.02,97.253,7,false,'Stone_DS_Dark','',''},
  ['DS_Exit_Torii__P_DS_Black']={-1999.578,90.825,1475.403,20.261,19.45,14.863,7,false,'P_DS_Black','',''},
  ['DS_Exit_Torii__Roof_DS_Tile']={-1999.578,100.43,1475.403,21.37,3.181,16.15,7,false,'Roof_DS_Tile','',''},
  ['DS_Exit_Torii__Stone_DS_Dark']={-1999.578,80.55,1475.403,15.373,1.3,11.935,7,false,'Stone_DS_Dark','',''},
  ['DS_Exit_Torii__Wood_DS_Lacquer']={-1999.578,90.056,1475.403,16.639,17.813,12.051,7,false,'Wood_DS_Lacquer','',''},
  ['GATE_OnePiece_Barrier__Energy_Core_OnePiece_Glow']={-2043.99,88.611,1537.031,11.574,13.269,8.786,8,false,'Energy_Core_OnePiece_Glow','','GATE_OnePiece'},
  ['GATE_OnePiece_Barrier__P_OP_Glow']={-2044.067,89.2,1537.014,13.393,18.0,9.587,8,false,'P_OP_Glow','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Cloth_GateOP_Straw']={-2044.076,106.093,1537.008,5.355,2.369,5.377,8,false,'Cloth_GateOP_Straw','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Cloth_Red']={-2044.067,103.59,1537.014,3.167,5.466,3.637,8,false,'Cloth_Red','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Crystal_Blue_Core']={-2042.532,87.442,1534.144,28.807,6.725,24.222,8,false,'Crystal_Blue_Core','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Emblem_Cream']={-2044.067,101.6,1537.014,4.873,3.96,4.598,8,false,'Emblem_Cream','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Metal_Brass']={-2042.108,93.175,1534.364,30.012,21.45,24.139,8,false,'Metal_Brass','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Metal_Dark']={-2042.325,86.327,1537.218,29.971,12.255,28.494,8,false,'Metal_Dark','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__P_OP_Blue']={-2041.371,92.9,1533.164,28.974,21.0,21.557,8,false,'P_OP_Blue','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Rope']={-2042.359,85.855,1536.319,29.982,5.35,25.844,8,false,'Rope','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Stone_Wall_Dark']={-2041.973,82.725,1534.024,37.003,6.25,31.38,8,false,'Stone_Wall_Dark','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Stone_Wall_Light']={-2041.371,82.575,1533.618,31.981,5.95,25.472,8,false,'Stone_Wall_Light','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Wood_Dark']={-2044.902,85.515,1540.401,24.975,11.83,23.032,8,false,'Wood_Dark','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Wood_GateOP_Helm']={-2042.018,95.798,1533.628,29.415,19.905,24.826,8,false,'Wood_GateOP_Helm','','GATE_OnePiece'},
  ['GATE_OnePiece_Frame__Wood_Plank']={-2040.826,86.725,1532.386,25.545,2.85,18.589,8,false,'Wood_Plank','','GATE_OnePiece'},
  ['GATE_OnePiece_Lock__Energy_Core_OnePiece_Glow']={-2044.067,88.48,1537.014,3.883,3.4,3.22,8,false,'Energy_Core_OnePiece_Glow','','GATE_OnePiece'},
  ['GATE_OnePiece_Lock__Metal_Dark']={-2044.067,88.28,1537.014,1.901,1.0,2.417,8,false,'Metal_Dark','','GATE_OnePiece'},
  ['GATE_OnePiece_Lock__Metal_Gold']={-2044.067,89.442,1537.014,3.941,4.625,3.72,8,false,'Metal_Gold','','GATE_OnePiece'},
  ['DS_Prop_Clearing__Bamboo_DS_Dry']={-1727.683,61.049,1173.88,2.531,1.458,2.76,9,false,'Bamboo_DS_Dry','',''},
  ['DS_Prop_Clearing__Metal_DS_Iron']={-1725.762,61.818,1171.589,4.221,3.099,4.443,9,false,'Metal_DS_Iron','',''},
  ['DS_Prop_Clearing__Rope_DS_Straw']={-1829.451,61.381,1156.16,205.848,1.412,189.336,9,false,'Rope_DS_Straw','',''},
  ['DS_Prop_Clearing__Water_DS_Trough']={-1728.176,60.617,1173.259,1.248,0.05,1.223,9,false,'Water_DS_Trough','',''},
  ['DS_Prop_Clearing__Wood_DS_Dark_g2_6']={-1748.95,61.68,1187.26,51.509,3.08,68.47,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_Clearing__Wood_DS_Dark_g2_7']={-1833.993,61.67,1162.988,197.062,3.06,219.131,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_Clearing__Wood_DS_Mid']={-1828.149,61.579,1156.161,208.711,3.478,189.596,9,true,'Wood_DS_Mid','',''},
  ['DS_Prop_Forge__Bamboo_DS_Dry']={-1997.346,81.63,1268.514,26.393,2.602,9.123,9,true,'Bamboo_DS_Dry','',''},
  ['DS_Prop_Forge__Metal_DS_Iron']={-1994.828,81.125,1283.481,2.812,0.31,2.74,9,false,'Metal_DS_Iron','',''},
  ['DS_Prop_Forge__Rope_DS_Straw']={-1965.616,81.759,1313.432,79.789,4.218,110.341,9,false,'Rope_DS_Straw','',''},
  ['DS_Prop_Forge__Stone_DS_Soot']={-1967.365,81.745,1313.513,83.162,3.598,110.19,9,true,'Stone_DS_Soot','',''},
  ['DS_Prop_Forge__Water_DS_Trough']={-2009.888,80.523,1272.426,1.029,0.05,1.021,9,false,'Water_DS_Trough','',''},
  ['DS_Prop_Forge__Wood_DS_Dark']={-1971.695,81.88,1314.672,75.836,4.48,104.482,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_Forge__Wood_DS_Mid']={-1968.177,81.789,1313.304,84.499,4.351,109.993,9,true,'Wood_DS_Mid','',''},
  ['DS_Prop_Lamps__Glass_DS_Lantern']={-1780.495,63.607,1142.457,273.89,5.592,236.065,9,false,'Glass_DS_Lantern','',''},
  ['DS_Prop_Lamps__Metal_DS_Iron']={-1780.523,65.113,1142.484,273.279,5.814,235.456,9,true,'Metal_DS_Iron','',''},
  ['DS_Prop_Lamps__Roof_DS_Tile']={-1780.122,62.297,1142.908,276.354,14.407,239.59,9,true,'Roof_DS_Tile','',''},
  ['DS_Prop_Lamps__Window_DS_Warm']={-1780.495,63.607,1142.457,273.89,6.107,236.065,9,false,'Window_DS_Warm','',''},
  ['DS_Prop_Lamps__Wood_DS_Dark']={-1780.016,62.312,1142.872,275.515,13.537,238.933,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathFences__Wood_DS_Dark_g0_6']={-1902.098,66.39,1186.988,137.539,12.5,228.645,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathFences__Wood_DS_Dark_g1_6']={-1848.407,66.39,1255.609,106.246,12.5,52.15,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathFences__Wood_DS_Dark_g2_7']={-1699.744,58.789,1102.286,91.994,8.062,152.191,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLamps_SulClr__Glass_DS_Lantern']={-1803.189,60.805,1152.288,302.647,8.211,245.507,9,false,'Glass_DS_Lantern','',''},
  ['DS_Prop_PathLamps_SulClr__Stone_DS_Path_g1_7']={-1877.705,61.857,1151.277,155.042,5.035,164.44,9,true,'Stone_DS_Path','',''},
  ['DS_Prop_PathLamps_SulClr__Stone_DS_Path_g2_7']={-1779.495,59.498,1151.499,255.546,9.658,247.433,9,true,'Stone_DS_Path','',''},
  ['DS_Prop_PathLamps_SulClr__Window_DS_Warm']={-1803.189,60.781,1152.288,302.647,8.844,245.507,9,false,'Window_DS_Warm','',''},
  ['DS_Prop_PathLamps_SulClr__Wood_DS_Dark_g1_6']={-1868.659,63.247,1218.775,151.181,5.613,113.853,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLamps_SulClr__Wood_DS_Dark_g2_6']={-1743.925,63.292,1183.734,57.465,5.344,52.058,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLamps_SulClr__Wood_DS_Dark_g2_7']={-1776.71,60.831,1077.512,251.143,9.908,98.802,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLamps_VilaForja__Glass_DS_Lantern']={-1831.303,74.18,1296.099,325.396,20.769,346.156,9,false,'Glass_DS_Lantern','',''},
  ['DS_Prop_PathLamps_VilaForja__Stone_DS_Path']={-1830.793,72.055,1296.726,327.907,24.429,346.987,9,true,'Stone_DS_Path','',''},
  ['DS_Prop_PathLamps_VilaForja__Window_DS_Warm']={-1831.303,74.214,1296.099,325.396,21.287,346.156,9,false,'Window_DS_Warm','',''},
  ['DS_Prop_PathLamps_VilaForja__Wood_DS_Dark_g1_5']={-1880.636,76.563,1376.398,179.443,19.886,186.562,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLamps_VilaForja__Wood_DS_Dark_g2_6']={-1726.151,66.442,1201.283,117.755,12.005,157.815,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLife__Bamboo_DS_Dry']={-1798.183,70.446,1265.111,152.12,20.117,155.296,9,true,'Bamboo_DS_Dry','',''},
  ['DS_Prop_PathLife__Stone_DS_Path']={-1780.748,70.03,1230.867,269.964,19.82,303.398,9,true,'Stone_DS_Path','',''},
  ['DS_Prop_PathLife__Wood_DS_Dark']={-1792.647,71.395,1245.438,293.321,27.989,432.965,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_PathLife__Wood_DS_Mid']={-1791.915,71.79,1245.438,295.016,25.779,433.214,9,true,'Wood_DS_Mid','',''},
  ['DS_Prop_Village__Bamboo_DS_Dry']={-1709.904,65.855,1237.161,127.898,11.335,158.826,9,true,'Bamboo_DS_Dry','',''},
  ['DS_Prop_Village__Cloth_DS_Ai']={-1725.449,66.555,1235.436,98.337,9.59,157.137,9,true,'Cloth_DS_Ai','',''},
  ['DS_Prop_Village__Dirt_DS_Dark']={-1711.554,63.68,1236.585,128.413,6.92,96.112,9,false,'Dirt_DS_Dark','',''},
  ['DS_Prop_Village__Metal_DS_Iron']={-1696.434,64.424,1221.766,78.53,8.332,58.471,9,true,'Metal_DS_Iron','',''},
  ['DS_Prop_Village__Rope_DS_Straw']={-1723.444,66.033,1248.584,102.549,10.634,134.404,9,false,'Rope_DS_Straw','',''},
  ['DS_Prop_Village__Stone_DS_B']={-1724.402,64.475,1235.527,152.794,8.61,153.899,9,true,'Stone_DS_B','',''},
  ['DS_Prop_Village__Water_DS_Trough']={-1706.224,64.137,1235.395,120.247,7.634,85.598,9,false,'Water_DS_Trough','',''},
  ['DS_Prop_Village__Wood_DS_Dark']={-1739.785,64.494,1219.76,127.891,8.549,131.361,9,true,'Wood_DS_Dark','',''},
  ['DS_Prop_Village__Wood_DS_Mid']={-1724.962,64.483,1219.961,157.784,8.567,132.017,9,true,'Wood_DS_Mid','',''},
  ['DS_Veg_Bamboo__Bamboo_DS_0']={-1749.332,69.952,1057.562,73.7,26.122,63.686,10,true,'Bamboo_DS','',''},
  ['DS_Veg_Bamboo__Bamboo_DS_1']={-1692.776,68.446,1051.409,41.342,27.175,77.247,10,false,'Bamboo_DS','',''},
  ['DS_Veg_Bamboo__Bamboo_DS_Dry']={-1728.086,62.047,1052.068,108.601,14.228,72.635,10,true,'Bamboo_DS_Dry','',''},
  ['DS_Veg_Bamboo__Leaf_DS_Bamboo']={-1728.945,72.734,1051.387,119.276,23.219,82.953,10,false,'Leaf_DS_Bamboo','',''},
  ['DS_Veg_Carvao__Bark_DS']={-1915.796,91.442,1422.962,152.999,26.047,57.79,10,false,'Bark_DS','',''},
  ['DS_Veg_Carvao__Leaf_DS_Broad_g0_4']={-1958.645,98.438,1427.4,80.407,22.46,46.486,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Carvao__Leaf_DS_Broad_g1_4']={-1865.932,83.171,1430.164,110.312,29.562,46.361,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Carvao__Leaf_DS_Broad_g1_5']={-1904.001,88.078,1400.805,186.45,39.21,20.964,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Carvao__Leaf_DS_Cedar_g0_4']={-1956.038,90.809,1430.284,73.485,23.689,47.758,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Carvao__Leaf_DS_Cedar_g1_4']={-1908.921,78.314,1424.186,164.885,52.133,59.953,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Carvao__Leaf_DS_Shrub']={-1874.676,80.334,1432.25,104.179,26.276,46.049,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Clareira__Bark_DS']={-1739.818,70.471,1132.735,80.907,22.493,162.809,10,true,'Bark_DS','',''},
  ['DS_Veg_Clareira__Leaf_DS_Broad_g2_6']={-1738.167,72.701,1183.297,88.189,25.726,67.39,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Clareira__Leaf_DS_Broad_g2_7']={-1738.643,73.257,1101.104,92.25,26.455,108.03,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Clareira__Leaf_DS_Cedar']={-1742.711,69.331,1131.949,88.331,19.889,161.011,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Clareira__Leaf_DS_Shrub']={-1726.459,66.979,1122.024,74.959,14.999,103.982,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_ClareiraL__Bark_DS']={-1844.744,65.82,1053.439,136.303,32.28,60.637,10,true,'Bark_DS','',''},
  ['DS_Veg_ClareiraL__Leaf_DS_Broad']={-1858.14,68.116,1054.153,154.167,37.664,70.109,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_ClareiraL__Leaf_DS_Cedar']={-1847.876,63.57,1049.835,153.907,31.62,73.01,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_ClareiraL__Leaf_DS_Shrub']={-1866.829,65.361,1050.518,148.176,23.093,52.537,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_ClareiraN__Bark_DS']={-1890.711,70.149,1246.249,122.405,22.168,110.431,10,true,'Bark_DS','',''},
  ['DS_Veg_ClareiraN__Leaf_DS_Broad']={-1892.664,73.484,1248.457,122.755,27.343,116.979,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_ClareiraN__Leaf_DS_Cedar']={-1892.92,71.362,1254.855,112.515,23.875,102.045,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_ClareiraN__Leaf_DS_Shrub_g0_6']={-1954.616,66.65,1208.823,40.377,14.339,40.736,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_ClareiraN__Leaf_DS_Shrub_g1_6']={-1845.358,67.748,1255.896,122.895,15.536,63.991,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Entrada__Bark_DS']={-1667.713,66.661,1047.24,110.171,28.637,105.661,10,false,'Bark_DS','',''},
  ['DS_Veg_Entrada__Leaf_DS_Broad']={-1671.793,60.031,1044.757,85.48,35.824,109.105,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Entrada__Leaf_DS_Cedar']={-1671.148,64.463,1045.911,114.389,40.074,95.173,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Entrada__Leaf_DS_Shrub']={-1678.763,64.551,1069.825,101.825,35.1,108.46,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Forja__Bark_DS']={-2018.122,85.772,1274.299,109.08,32.224,98.924,10,true,'Bark_DS','',''},
  ['DS_Veg_Forja__Leaf_DS_Broad']={-2010.682,84.751,1272.128,126.538,29.779,99.892,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Forja__Leaf_DS_Cedar']={-1979.935,76.296,1283.629,119.047,12.575,88.874,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Forja__Leaf_DS_Shrub']={-1988.306,87.812,1274.926,178.292,35.664,106.466,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_ForjaL__Bark_DS']={-2048.031,79.167,1227.895,64.115,41.585,113.494,10,true,'Bark_DS','',''},
  ['DS_Veg_ForjaL__Leaf_DS_Broad']={-2055.429,86.187,1225.359,87.406,34.006,116.907,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_ForjaL__Leaf_DS_Cedar']={-2051.486,82.302,1229.854,62.647,41.395,114.294,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_ForjaL__Leaf_DS_Shrub']={-2043.656,74.218,1201.511,66.186,12.909,64.225,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Fundo__Bark_DS']={-2055.199,106.773,1361.98,91.451,46.547,100.004,10,false,'Bark_DS','',''},
  ['DS_Veg_Fundo__Leaf_DS_Broad']={-2064.593,115.993,1363.286,80.039,25.839,109.885,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Fundo__Leaf_DS_Cedar']={-2053.848,108.602,1367.042,94.727,43.197,111.075,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Fundo__Leaf_DS_Shrub']={-2093.314,105.374,1355.73,12.721,13.579,28.639,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_FundoL__Bark_DS']={-2101.058,111.794,1291.733,3.048,6.628,1.451,10,false,'Bark_DS','',''},
  ['DS_Veg_FundoL__Leaf_DS_Broad']={-2100.034,107.489,1291.257,6.271,7.528,12.149,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_FundoL__Leaf_DS_Cedar']={-2102.149,114.534,1291.486,7.791,4.218,10.738,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Leste__Leaf_DS_Broad']={-1763.556,49.839,1028.001,5.66,16.959,7.26,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_SW__Bark_DS']={-1634.492,75.137,1149.06,23.683,33.763,90.022,10,false,'Bark_DS','',''},
  ['DS_Veg_SW__Leaf_DS_Broad']={-1624.121,73.09,1142.178,31.89,29.906,94.225,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_SW__Leaf_DS_Cedar']={-1636.031,75.249,1143.058,26.321,40.898,84.297,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_SW__Leaf_DS_Shrub']={-1635.89,62.104,1164.746,34.446,9.212,69.691,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Saida__Bark_DS']={-1973.794,90.105,1465.997,43.522,22.551,46.92,10,false,'Bark_DS','',''},
  ['DS_Veg_Saida__Leaf_DS_Broad']={-1963.278,75.552,1479.679,23.405,28.116,27.934,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Saida__Leaf_DS_Cedar']={-1985.786,94.382,1448.487,25.289,21.997,17.296,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Saida__Leaf_DS_Shrub']={-1964.653,85.072,1477.717,30.621,16.8,28.744,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Summon__Bark_DS']={-1958.599,69.597,1106.615,89.604,35.446,137.671,10,true,'Bark_DS','',''},
  ['DS_Veg_Summon__Leaf_DS_Broad']={-1959.281,71.469,1106.323,100.176,38.792,145.576,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Summon__Leaf_DS_Cedar']={-1959.922,72.94,1104.585,92.376,36.121,140.137,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_Summon__Leaf_DS_Shrub']={-1953.285,71.981,1120.309,85.754,27.604,111.46,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_VilaAlta__Bark_DS']={-1782.722,80.698,1315.452,128.461,36.324,142.585,10,true,'Bark_DS','',''},
  ['DS_Veg_VilaAlta__Leaf_DS_Broad']={-1784.61,76.008,1334.138,125.697,32.246,143.066,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_VilaAlta__Leaf_DS_Cedar_g1_5']={-1817.804,81.19,1343.48,51.788,42.381,127.833,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_VilaAlta__Leaf_DS_Cedar_g2_5']={-1766.026,70.226,1309.319,101.942,34.308,161.191,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_VilaAlta__Leaf_DS_Shrub_g1_5']={-1828.607,77.229,1343.701,73.672,34.139,117.802,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_VilaAlta__Leaf_DS_Shrub_g2_5']={-1764.651,68.406,1294.362,101.95,31.7,105.505,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_VilaBaixa__Bark_DS']={-1698.233,73.22,1237.311,134.716,30.001,139.122,10,true,'Bark_DS','',''},
  ['DS_Veg_VilaBaixa__Leaf_DS_Broad']={-1697.375,67.498,1243.68,144.807,35.545,153.016,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_VilaBaixa__Leaf_DS_Cedar']={-1693.703,67.106,1246.353,146.221,50.549,125.131,10,false,'Leaf_DS_Cedar','',''},
  ['DS_Veg_VilaBaixa__Leaf_DS_Shrub']={-1689.688,63.563,1237.735,133.223,29.918,147.864,10,false,'Leaf_DS_Shrub','',''},
  ['DS_Veg_Wisteria__Bark_DS']={-1773.397,67.223,1192.352,88.447,17.024,288.576,10,true,'Bark_DS','',''},
  ['DS_Veg_Wisteria__Leaf_DS_Broad_g1_5']={-1813.772,75.464,1332.029,14.466,1.929,12.237,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Wisteria__Leaf_DS_Broad_g2_7']={-1732.745,70.134,1052.869,12.062,2.051,14.988,10,false,'Leaf_DS_Broad','',''},
  ['DS_Veg_Wisteria__Wisteria_DS_g1_5']={-1813.633,73.514,1331.923,13.66,1.833,11.497,10,false,'Wisteria_DS','',''},
  ['DS_Veg_Wisteria__Wisteria_DS_g2_7']={-1733.202,68.09,1052.382,10.799,2.066,14.755,10,false,'Wisteria_DS','',''},
  ['DS_Veg_Wisteria__Wisteria_DS_Deep_g1_5']={-1813.621,74.608,1331.984,13.834,2.372,11.777,10,false,'Wisteria_DS_Deep','',''},
  ['DS_Veg_Wisteria__Wisteria_DS_Deep_g2_7']={-1733.108,69.261,1052.441,10.991,2.862,14.973,10,false,'Wisteria_DS_Deep','',''},
  ['DS_Veg_Wisteria__Wisteria_DS_Light_g1_5']={-1813.488,72.49,1331.914,13.388,1.658,11.387,10,false,'Wisteria_DS_Light','',''},
  ['DS_Veg_Wisteria__Wisteria_DS_Light_g2_7']={-1733.243,66.745,1052.317,10.867,2.471,14.628,10,false,'Wisteria_DS_Light','',''},
  ['VFX_DSSUM_Ring_1__Metal_Gold_DS']={-1961.113,116.2,1076.308,23.507,7.267,23.35,11,true,'Metal_Gold_DS','',''},
  ['VFX_DSSUM_Ring_1__Summon_DSStar_Glow']={-1961.115,116.278,1076.308,22.357,7.818,22.82,11,false,'Summon_DSStar_Glow','',''},
  ['VFX_DSSUM_Ring_2__Metal_Gold_DS']={-1961.112,116.2,1076.307,6.581,17.32,16.514,11,true,'Metal_Gold_DS','',''},
  ['VFX_DSSUM_Ring_2__Summon_DSStar_Glow']={-1961.128,116.2,1076.278,5.629,13.023,12.357,11,false,'Summon_DSStar_Glow','',''},
  ['VFX_DSSUM_Ring_3__Metal_Gold_DS']={-1961.113,116.2,1076.308,14.871,13.37,9.793,11,true,'Metal_Gold_DS','',''},
  ['VFX_DSSUM_Ring_3__Summon_DSStar_Glow']={-1961.134,116.18,1076.345,12.787,10.223,10.13,11,false,'Summon_DSStar_Glow','',''},
  ['VFX_DSSUM_Star__Metal_Gold_DS']={-1961.113,116.83,1076.308,10.195,11.94,8.759,11,false,'Metal_Gold_DS','',''},
  ['VFX_DSSUM_Star__Summon_DSStar_Glow']={-1961.113,116.83,1076.308,10.195,11.94,8.759,11,false,'Summon_DSStar_Glow','',''},
  ['VFX_DS_KineAxle__Wood_DS_Dark']={-2040.336,91.077,1274.369,13.291,2.992,15.505,11,false,'Wood_DS_Dark','',''},
  ['VFX_DS_KineAxle__Wood_DS_Mid']={-2037.154,91.2,1278.161,6.76,1.44,7.667,11,false,'Wood_DS_Mid','',''},
  ['VFX_DS_Kine_A__Wood_DS_Dark']={-2035.704,87.0,1277.886,3.291,11.1,2.936,11,false,'Wood_DS_Dark','',''},
  ['VFX_DS_Kine_A__Wood_DS_Mid']={-2034.833,89.85,1277.193,1.127,13.9,1.127,11,false,'Wood_DS_Mid','',''},
  ['VFX_DS_Kine_B__Wood_DS_Dark']={-2038.083,87.0,1275.052,3.291,11.1,2.936,11,false,'Wood_DS_Dark','',''},
  ['VFX_DS_Kine_B__Wood_DS_Mid']={-2037.212,89.85,1274.358,1.127,13.9,1.127,11,false,'Wood_DS_Mid','',''},
  ['VFX_DS_Wheel__Wood_DS_Dark']={-2044.064,91.2,1269.926,17.892,20.0,15.92,11,true,'Wood_DS_Dark','',''},
  ['VFX_DS_Wheel__Wood_DS_Mid']={-2044.064,91.2,1269.926,17.552,20.185,15.464,11,true,'Wood_DS_Mid','',''},
  ['VFX_GATE_OnePiece_Hat_1__Cloth_GateOP_Straw']={-2030.951,95.944,1540.948,2.889,1.089,2.889,11,false,'Cloth_GateOP_Straw','',''},
  ['VFX_GATE_OnePiece_Hat_1__Cloth_Red']={-2030.951,95.75,1540.948,1.655,0.24,1.655,11,false,'Cloth_Red','',''},
  ['VFX_GATE_OnePiece_Hat_2__Cloth_GateOP_Straw']={-2029.034,91.144,1537.164,2.889,1.089,2.889,11,false,'Cloth_GateOP_Straw','',''},
  ['VFX_GATE_OnePiece_Hat_2__Cloth_Red']={-2029.034,90.95,1537.164,1.655,0.24,1.654,11,false,'Cloth_Red','',''},
  ['VFX_GATE_OnePiece_Hat_3__Cloth_GateOP_Straw']={-2049.349,91.444,1522.939,2.889,1.089,2.889,11,false,'Cloth_GateOP_Straw','',''},
  ['VFX_GATE_OnePiece_Hat_3__Cloth_Red']={-2049.349,91.25,1522.939,1.655,0.24,1.655,11,false,'Cloth_Red','',''},
  ['VFX_GATE_OnePiece_Hat_4__Cloth_GateOP_Straw']={-2052.25,96.244,1526.035,2.889,1.089,2.889,11,false,'Cloth_GateOP_Straw','',''},
  ['VFX_GATE_OnePiece_Hat_4__Cloth_Red']={-2052.25,96.05,1526.035,1.655,0.24,1.654,11,false,'Cloth_Red','',''},
  ['VFX_GATE_OnePiece_Needle__Crystal_Blue_Core']={-2042.948,101.775,1535.417,0.606,2.75,0.508,11,false,'Crystal_Blue_Core','',''},
  ['DS_Ent_Bridge__Glass_DS_Lantern']={-1572.796,59.2,994.582,59.102,1.74,25.502,12,false,'Glass_DS_Lantern','','DS_Ent'},
  ['DS_Ent_Bridge__Metal_DS_Rust']={-1580.198,58.805,1002.424,74.414,5.49,63.65,12,false,'Metal_DS_Rust','','DS_Ent'},
  ['DS_Ent_Bridge__Stone_DS']={-1538.896,55.28,966.177,21.868,3.34,23.144,12,false,'Stone_DS','','DS_Ent'},
  ['DS_Ent_Bridge__Stone_DS_Dark']={-1565.537,55.505,981.389,75.507,11.09,53.777,12,false,'Stone_DS_Dark','','DS_Ent'},
  ['DS_Ent_Bridge__Window_DS_Warm']={-1572.796,59.2,994.582,59.102,2.28,25.502,12,false,'Window_DS_Warm','','DS_Ent'},
  ['DS_Ent_Bridge__Wood_DS_Dark']={-1576.585,51.43,997.637,81.852,18.14,73.284,12,false,'Wood_DS_Dark','','DS_Ent'},
  ['DS_Ent_Bridge__Wood_DS_Mid']={-1576.511,50.349,997.7,80.336,7.789,71.536,12,false,'Wood_DS_Mid','','DS_Ent'},
  ['DS_Ent_BridgeRock__Cliff_DS']={-1556.967,-18.566,981.846,56.728,112.868,52.913,12,false,'Cliff_DS','','DS_Ent'},
  ['DS_Ent_BridgeRock__Cliff_DS_B']={-1556.645,-12.82,982.666,55.961,124.36,52.649,12,false,'Cliff_DS_B','','DS_Ent'},
  ['DS_Ent_BridgeRock__Cliff_DS_Dark']={-1556.359,-14.263,981.806,53.987,119.353,49.453,12,false,'Cliff_DS_Dark','','DS_Ent'},
  ['DS_Ent_BridgeRock__Cliff_DS_Moss']={-1557.137,46.06,981.046,49.498,8.2,44.938,12,false,'Cliff_DS_Moss','','DS_Ent'},
  ['DS_Ent_BridgeRock__Stone_DS']={-1609.171,45.54,1024.277,24.522,13.374,24.75,12,false,'Stone_DS','','DS_Ent'},
  ['DS_Ent_BridgeRock__Stone_DS_B']={-1609.167,45.834,1025.373,23.625,13.952,25.853,12,false,'Stone_DS_B','','DS_Ent'},
  ['DS_Ent_BridgeRock__Stone_DS_Dark']={-1609.183,45.535,1025.115,24.225,13.45,25.901,12,false,'Stone_DS_Dark','','DS_Ent'},
  ['DS_Ent_Court__Stone_DS_B']={-1639.542,57.325,1066.254,20.175,6.85,20.114,12,false,'Stone_DS_B','','DS_Ent'},
  ['DS_Ent_Court__Stone_DS_Dark']={-1639.549,56.89,1066.26,18.708,5.98,18.4,12,false,'Stone_DS_Dark','','DS_Ent'},
  ['DS_Ent_Court__Stone_DS_Path']={-1639.49,57.425,1066.21,18.88,5.55,18.562,12,false,'Stone_DS_Path','','DS_Ent'},
  ['DS_Ent_Court__Wood_DS_Dark']={-1611.668,55.52,1032.161,28.042,2.76,43.379,12,false,'Wood_DS_Dark','','DS_Ent'},
  ['DS_Ent_Ferns__Leaf_DS_Shrub']={-1607.933,49.5,1026.299,90.451,13.699,80.34,12,false,'Leaf_DS_Shrub','','DS_Ent'},
  ['DS_Ent_Torii__P_DS_Black']={-1617.226,64.825,1031.864,16.411,19.45,19.12,12,false,'P_DS_Black','','DS_Ent'},
  ['DS_Ent_Torii__Roof_DS_Tile']={-1617.226,74.43,1031.864,17.667,3.181,20.287,12,false,'Roof_DS_Tile','','DS_Ent'},
  ['DS_Ent_Torii__Stone_DS_Dark']={-1617.226,54.55,1031.864,12.814,1.3,14.539,12,false,'Stone_DS_Dark','','DS_Ent'},
  ['DS_Ent_Torii__Wood_DS_Lacquer']={-1617.226,64.056,1031.864,13.36,17.813,15.662,12,false,'Wood_DS_Lacquer','','DS_Ent'},
  ['DS_Ent_Toro__Glass_DS_Lantern']={-1623.355,58.462,1037.006,16.468,1.182,19.378,12,false,'Glass_DS_Lantern','','DS_Ent'},
  ['DS_Ent_Toro__Stone_DS']={-1623.355,57.552,1037.006,19.056,7.076,21.891,12,false,'Stone_DS','','DS_Ent'},
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
  {'COL_DSAnchorGuard_001','Block',{-2054.735,84.2,1552.25},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,20.0,9.0},false},
  {'COL_DSSumTower_001','Ramp',{-1952.643,71.753,1086.401},{-0.575,0.447,-0.685},{-0.766,-0.0,0.643},{8.944,7.6,1.0},false},
  {'COL_DSSumTower_002','Block',{-1955.424,73.7,1083.087},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.1,7.6,1.0},true},
  {'COL_DSSumTower_003','Ramp',{-1949.302,73.26,1083.538},{-0.575,0.447,-0.685},{-0.766,0.0,0.643},{8.944,1.2,5.5},false},
  {'COL_DSSumTower_004','Ramp',{-1956.043,73.26,1089.194},{-0.575,0.447,-0.685},{-0.766,0.0,0.643},{8.944,1.2,5.5},false},
  {'COL_DSSumTower_005','Block',{-1949.002,75.8,1075.806},{-0.766,0.0,0.643},{0.643,0.0,0.766},{2.0,2.0,4.6},false},
  {'COL_DSSumTower_006','Block',{-1963.71,75.8,1088.147},{-0.766,0.0,0.643},{0.643,0.0,0.766},{2.0,2.0,4.6},false},
  {'COL_DSSumTower_007','Block',{-1917.313,61.4,1118.207},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,2.4},false},
  {'COL_DSSumTower_008','Block',{-1927.456,61.4,1126.717},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,2.4},false},
  {'COL_DSSumTower_009','Block',{-1962.88,90.05,1074.201},{-0.766,0.0,0.643},{0.643,0.0,0.766},{17.2,8.7,33.1},true},
  {'COL_DSSumTower_010','Block',{-1959.216,96.4,1078.567},{-0.766,0.0,0.643},{0.643,0.0,0.766},{17.2,2.7,20.4},true},
  {'COL_DSSumTower_011','Block',{-1957.384,87.3,1080.751},{-0.766,0.0,0.643},{0.643,0.0,0.766},{8.0,3.0,2.2},true},
  {'COL_DSSumTower_012','Block',{-1953.426,80.95,1075.667},{-0.766,0.0,0.643},{0.643,0.0,0.766},{4.6,5.7,14.9},true},
  {'COL_DSSumTower_013','Block',{-1953.988,87.35,1070.33},{-0.766,0.0,0.643},{0.643,0.0,0.766},{4.2,2.2,27.7},true},
  {'COL_DSSumTower_014','Block',{-1963.078,80.95,1083.766},{-0.766,0.0,0.643},{0.643,0.0,0.766},{4.6,5.7,14.9},true},
  {'COL_DSSumTower_015','Block',{-1968.237,87.35,1082.286},{-0.766,0.0,0.643},{0.643,0.0,0.766},{4.2,2.2,27.7},true},
  {'COL_DSSumTower_016','Block',{-1953.22,70.25,1070.468},{-0.766,0.0,0.643},{0.643,0.0,0.766},{9.6,18.0,1.3},true},
  {'COL_DSSumTower_017','Block',{-1954.369,70.25,1071.432},{-0.766,0.0,0.643},{0.643,0.0,0.766},{6.6,24.0,1.3},true},
  {'COL_DSSumTower_018','Block',{-1953.992,71.65,1070.986},{-0.766,0.0,0.643},{0.643,0.0,0.766},{7.75,20.1,4.1},true},
  {'COL_DSSumTower_019','Block',{-1968.234,70.25,1083.067},{-0.766,0.0,0.643},{0.643,0.0,0.766},{9.6,18.0,1.3},true},
  {'COL_DSSumTower_020','Block',{-1967.085,70.25,1082.102},{-0.766,0.0,0.643},{0.643,0.0,0.766},{6.6,24.0,1.3},true},
  {'COL_DSSumTower_021','Block',{-1967.59,71.65,1082.395},{-0.766,0.0,0.643},{0.643,0.0,0.766},{7.75,20.1,4.1},true},
  {'COL_DSSumTower_022','Block',{-1967.846,70.25,1068.283},{-0.766,0.0,0.643},{0.643,0.0,0.766},{10.0,1.85,1.3},true},
  {'COL_DSSumTower_023','Block',{-1963.668,71.55,1073.263},{-0.766,0.0,0.643},{0.643,0.0,0.766},{10.0,11.15,3.9},true},
  {'COL_DSSumTower_024','Block',{-1957.834,72.1,1080.214},{-0.766,0.0,0.643},{0.643,0.0,0.766},{10.0,7.0,4.2},true},
  {'COL_DSSumTower_025','Block',{-1932.443,72.7,1095.851},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,5.0},true},
  {'COL_DSSumTower_026','Block',{-1946.844,72.7,1107.936},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,5.0},true},
  {'COL_DS_Arrival_001','Ramp',{-1572.811,52.2,994.595},{-0.766,0.02,0.643},{0.643,0.0,0.766},{104.021,18.0,2.0},false},
  {'COL_DS_Arrival_002','Ramp',{-1579.001,54.95,987.257},{-0.766,0.02,0.643},{0.643,-0.0,0.766},{100.02,1.2,4.5},false},
  {'COL_DS_Arrival_003','Ramp',{-1566.659,54.95,1001.965},{-0.766,0.02,0.643},{0.643,-0.0,0.766},{100.02,1.2,4.5},false},
  {'COL_DS_ClrRock_007','Block',{-1715.367,61.0,1163.82},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.08,3.36,2.2},false},
  {'COL_DS_ClrRock_008','Block',{-1785.447,60.8,1226.54},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.06,2.52,1.8},false},
  {'COL_DS_ClrRock_009','Block',{-1820.043,61.15,1256.874},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.76,3.92,2.5},false},
  {'COL_DS_ClrRock_010','Block',{-1830.813,60.95,1063.574},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.74,3.08,2.1},false},
  {'COL_DS_ClrRock_011','Block',{-1882.015,60.75,1105.232},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.89,2.38,1.7},false},
  {'COL_DS_ClrRock_012','Block',{-1878.368,60.85,1274.485},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.4,2.8,1.9},false},
  {'COL_DS_ClrRock_013','Block',{-1945.165,60.9,1210.437},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.91,3.22,2.0},false},
  {'COL_DS_EntTorii_001','Block',{-1612.727,63.2,1037.226},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.3,2.3,18.0},false},
  {'COL_DS_EntTorii_002','Block',{-1621.726,63.2,1026.502},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.3,2.3,18.0},false},
  {'COL_DS_EntToro_001','Block',{-1615.641,57.434,1046.199},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.548,2.548,6.468},false},
  {'COL_DS_EntToro_002','Block',{-1631.068,57.434,1027.814},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.548,2.548,6.468},false},
  {'COL_DS_ExitBridge_001','Ramp',{-2021.124,79.2,1504.248},{-0.574,0.0,0.819},{0.819,0.0,0.574},{60.0,18.0,2.0},false},
  {'COL_DS_ExitBridge_002','Ramp',{-2028.988,81.95,1498.742},{-0.574,0.0,0.819},{0.819,0.0,0.574},{56.0,1.2,4.5},false},
  {'COL_DS_ExitBridge_003','Ramp',{-2013.26,81.95,1509.754},{-0.574,0.0,0.819},{0.819,0.0,0.574},{56.0,1.2,4.5},false},
  {'COL_DS_ExitLamp_001','Block',{-1893.851,84.5,1411.398},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_ExitLamp_002','Block',{-1935.417,84.5,1450.927},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_ExitLamp_003','Block',{-1983.112,84.5,1459.18},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_ExitTorii_001','Block',{-1993.844,89.2,1479.418},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.3,2.3,18.0},false},
  {'COL_DS_ExitTorii_002','Block',{-2005.312,89.2,1471.388},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.3,2.3,18.0},false},
  {'COL_DS_FrgCoal_001','Block',{-1845.524,82.6,1369.634},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{10.6,10.6,4.8},false},
  {'COL_DS_FrgCoal_002','Block',{-1841.578,82.0,1366.323},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.6,1.2,3.6},false},
  {'COL_DS_FrgCoal_003','Block',{-1834.636,84.9,1370.941},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,9.4},false},
  {'COL_DS_FrgCoal_004','Block',{-1846.893,84.9,1381.226},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,9.4},false},
  {'COL_DS_FrgCoal_005','Block',{-1844.921,84.9,1358.684},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,9.4},false},
  {'COL_DS_FrgCoal_006','Block',{-1857.177,84.9,1368.969},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,9.4},false},
  {'COL_DS_FrgCoal_007','Block',{-1851.053,81.82,1400.381},{-0.294,0.0,-0.956},{-0.956,0.0,0.294},{8.8,2.4,3.24},false},
  {'COL_DS_FrgCoal_008','Block',{-1831.613,81.49,1393.99},{-0.766,0.0,0.643},{0.643,0.0,0.766},{8.2,2.4,2.58},false},
  {'COL_DS_FrgCoal_009','Block',{-1871.992,81.49,1380.094},{-0.812,0.0,-0.583},{-0.583,0.0,0.812},{7.2,2.4,2.58},false},
  {'COL_DS_FrgCoal_010','Block',{-1846.989,80.8,1390.445},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,1.2},false},
  {'COL_DS_FrgCoal_011','Block',{-1853.032,81.55,1349.173},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.4,1.8,2.7},false},
  {'COL_DS_FrgCoal_012','Block',{-1834.774,81.55,1360.353},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.4,1.8,2.7},false},
  {'COL_DS_FrgCoal_013','Block',{-1854.691,80.9,1358.397},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.2,1.2,1.4},false},
  {'COL_DS_FrgCoal_014','Block',{-1864.595,81.4,1353.229},{-0.963,0.0,-0.269},{-0.269,0.0,0.963},{4.4,2.6,2.4},false},
  {'COL_DS_FrgCoal_015','Block',{-1866.04,84.2,1360.741},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.6,1.6,8.0},false},
  {'COL_DS_FrgEast_001','Block',{-2023.125,80.7,1290.213},{0.643,0.0,0.766},{0.766,0.0,-0.643},{23.2,23.2,1.0},true},
  {'COL_DS_FrgEast_002','Block',{-2023.125,86.7,1290.213},{0.643,0.0,0.766},{0.766,0.0,-0.643},{22.0,22.0,11.0},true},
  {'COL_DS_FrgFlume_001','Block',{-2066.47,83.38,1282.635},{-0.48,0.0,-0.877},{-0.877,0.0,0.48},{3.8,1.0,6.0},false},
  {'COL_DS_FrgFlume_002','Block',{-2060.506,83.38,1279.371},{-0.48,0.0,-0.877},{-0.877,0.0,0.48},{3.8,1.0,6.0},false},
  {'COL_DS_FrgFlume_003','Block',{-2054.542,83.2,1276.107},{-0.48,0.0,-0.877},{-0.877,0.0,0.48},{3.8,1.0,6.0},false},
  {'COL_DS_FrgHall_001','Block',{-1969.383,88.3,1355.816},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.6,33.2,16.2},true},
  {'COL_DS_FrgHall_002','Block',{-1997.408,88.3,1322.417},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.6,33.2,16.2},true},
  {'COL_DS_FrgHall_003','Block',{-1995.499,88.3,1349.272},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{45.2,1.6,16.2},true},
  {'COL_DS_FrgHall_004','Block',{-1960.815,88.3,1341.447},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.6,1.6,16.2},true},
  {'COL_DS_FrgHall_005','Block',{-1965.609,90.0,1334.178},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.7,4.7,19.6},true},
  {'COL_DS_FrgHall_006','Block',{-1981.77,88.3,1316.474},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.6,1.6,16.2},true},
  {'COL_DS_FrgHall_007','Block',{-1975.443,90.0,1322.457},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.7,4.7,19.6},true},
  {'COL_DS_FrgHall_008','Block',{-1970.526,95.425,1328.318},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{10.5,4.7,8.75},true},
  {'COL_DS_FrgHall_009','Block',{-1981.634,80.2,1337.638},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{42.4,35.6,0.8},true},
  {'COL_DS_FrgHall_010','Block',{-1989.984,82.0,1344.644},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{8.8,8.4,3.2},true},
  {'COL_DS_FrgHall_011','Block',{-1993.507,84.6,1347.601},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{10.2,1.6,8.0},true},
  {'COL_DS_FrgHall_012','Block',{-1981.715,82.0,1347.497},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.6,6.6,2.8},true},
  {'COL_DS_FrgHall_013','Block',{-1984.162,81.6,1339.759},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.4,2.0,2.0},false},
  {'COL_DS_FrgHall_014','Block',{-1987.628,81.35,1333.139},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.6,2.6,1.5},false},
  {'COL_DS_FrgHall_015','Block',{-1994.562,81.3,1338.565},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.6,6.6,1.4},true},
  {'COL_DS_FrgHall_016','Block',{-2000.786,81.6,1336.282},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.6,1.6,2.0},false},
  {'COL_DS_FrgHall_017','Block',{-1973.261,88.1,1344.972},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.3,1.3,15.0},true},
  {'COL_DS_FrgHall_018','Block',{-1987.402,88.1,1328.119},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.3,1.3,15.0},true},
  {'COL_DS_FrgHall_019','Block',{-1984.907,82.3,1323.936},{-0.812,0.0,-0.583},{-0.583,0.0,0.812},{3.4,2.6,3.4},false},
  {'COL_DS_FrgMill_001','Block',{-2044.064,90.7,1269.926},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{7.8,25.0,21.0},false},
  {'COL_DS_FrgMill_002','Block',{-2036.344,88.2,1275.392},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{11.3,3.6,16.0},false},
  {'COL_DS_FrgMill_003','Block',{-2029.421,89.0,1276.176},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,17.6},false},
  {'COL_DS_FrgMill_004','Block',{-2040.299,89.0,1285.303},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,17.6},false},
  {'COL_DS_FrgMill_005','Block',{-2035.913,89.0,1268.439},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,17.6},false},
  {'COL_DS_FrgMill_006','Block',{-2046.791,89.0,1277.566},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,17.6},false},
  {'COL_DS_FrgProp_001','Block',{-1958.381,82.0,1337.969},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.2,3.2,3.6},false},
  {'COL_DS_FrgProp_002','Block',{-1977.922,82.0,1314.681},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.2,3.2,3.6},false},
  {'COL_DS_FrgProp_003','Block',{-2007.303,81.0,1285.422},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.6,3.0,1.6},false},
  {'COL_DS_FrgProp_004','Block',{-1943.429,81.1,1344.742},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,1.8},false},
  {'COL_DS_FrgProp_005','Block',{-1941.801,80.6,1345.845},{0.75,0.0,0.661},{0.661,0.0,-0.75},{1.7,1.0,0.8},false},
  {'COL_DS_FrgProp_006','Block',{-1943.65,81.2,1351.324},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.6,1.4,2.0},false},
  {'COL_DS_FrgProp_007','Block',{-1919.01,73.2,1300.103},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.4,2.4,6.0},false},
  {'COL_DS_FrgProp_008','Block',{-1924.978,71.1,1292.056},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.2,2.0,1.8},false},
  {'COL_DS_FrgProp_009','Block',{-1957.998,84.5,1292.22},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_FrgProp_010','Block',{-1973.054,84.5,1277.7},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_FrgTower_001','Block',{-2012.541,105.2,1315.272},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{17.2,17.2,50.0},true},
  {'COL_DS_FrgTower_002','Block',{-2005.8,82.6,1309.616},{0.643,0.0,0.766},{0.766,0.0,-0.643},{5.6,2.0,4.9},false},
  {'COL_DS_FrgWorkshop_001','Block',{-1951.503,80.8,1380.236},{0.643,0.0,0.766},{0.766,0.0,-0.643},{31.2,22.2,1.2},true},
  {'COL_DS_FrgWorkshop_002','Block',{-1951.503,90.2,1380.236},{0.643,0.0,0.766},{0.766,0.0,-0.643},{30.0,21.0,17.6},true},
  {'COL_DS_Guard_001','Block',{-1919.728,71.55,1073.711},{-0.454,0.0,-0.891},{-0.891,0.0,0.454},{26.457,1.0,3.7},false},
  {'COL_DS_Guard_004','Block',{-1937.334,71.55,1055.401},{-0.888,0.0,-0.46},{-0.46,0.0,0.888},{25.8,1.0,3.7},false},
  {'COL_DS_Guard_007','Block',{-1961.208,71.55,1055.016},{-0.891,0.0,0.454},{0.454,0.0,0.891},{26.457,1.0,3.7},false},
  {'COL_DS_Guard_010','Block',{-1980.859,71.55,1072.479},{-0.543,0.0,0.84},{0.84,0.0,0.543},{26.996,1.0,3.7},false},
  {'COL_DS_Guard_013','Block',{-1985.477,71.55,1095.883},{0.268,0.0,0.963},{0.963,0.0,-0.268},{23.959,1.0,3.7},false},
  {'COL_DS_Guard_016','Block',{-1971.676,71.55,1115.995},{0.799,0.0,0.602},{0.602,0.0,-0.799},{26.457,1.0,3.7},false},
  {'COL_DS_Guard_019','Block',{-1950.796,71.55,1116.604},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{24.8,1.0,3.7},false},
  {'COL_DS_Guard_022','Block',{-1923.219,71.55,1093.464},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{22.8,1.0,3.7},false},
  {'COL_DS_Guard_025','Block',{-1828.718,81.55,1352.328},{-0.571,0.0,-0.821},{-0.821,0.0,0.571},{78.118,1.0,3.7},false},
  {'COL_DS_Guard_033','Block',{-1872.289,81.55,1308.633},{-0.984,0.0,-0.177},{-0.177,0.0,0.984},{31.033,1.0,3.7},false},
  {'COL_DS_Guard_036','Block',{-1909.935,81.55,1313.641},{-0.94,0.0,0.342},{0.342,0.0,0.94},{46.601,1.0,3.7},false},
  {'COL_DS_Guard_041','Block',{-1944.702,81.55,1304.728},{-0.597,0.0,-0.802},{-0.802,0.0,0.597},{43.872,1.0,3.7},false},
  {'COL_DS_Guard_046','Block',{-1990.178,81.55,1243.677},{-0.597,0.0,-0.802},{-0.802,0.0,0.597},{79.933,1.0,3.7},false},
  {'COL_DS_Guard_054','Block',{-2022.695,81.55,1210.25},{-0.996,0.0,-0.087},{-0.087,0.0,0.996},{16.71,1.0,3.7},false},
  {'COL_DS_Guard_056','Block',{-2045.607,81.55,1222.234},{-0.731,0.0,0.682},{0.682,0.0,0.731},{37.851,1.0,3.7},false},
  {'COL_DS_Guard_060','Block',{-2069.49,81.55,1249.98},{-0.554,0.0,0.833},{0.833,0.0,0.554},{35.227,1.0,3.7},false},
  {'COL_DS_Guard_064','Block',{-2064.277,81.55,1290.06},{0.532,0.0,0.847},{0.847,0.0,-0.532},{58.34,1.0,3.7},false},
  {'COL_DS_Guard_070','Block',{-2011.676,81.55,1362.172},{0.617,0.0,0.787},{0.787,0.0,-0.617},{119.866,1.0,3.7},false},
  {'COL_DS_Guard_082','Block',{-1971.098,81.55,1418.761},{0.342,0.0,0.94},{0.94,0.0,-0.342},{20.138,1.0,3.7},false},
  {'COL_DS_Guard_084','Block',{-1919.96,81.55,1452.3},{0.973,0.0,-0.232},{-0.232,0.0,-0.973},{20.997,1.0,3.7},false},
  {'COL_DS_Guard_086','Block',{-1891.273,81.55,1440.498},{0.888,0.0,-0.459},{-0.459,0.0,-0.888},{40.8,1.0,3.7},false},
  {'COL_DS_Guard_090','Block',{-1856.069,81.55,1420.169},{0.84,0.0,-0.543},{-0.543,0.0,-0.84},{40.104,1.0,3.7},false},
  {'COL_DS_Guard_094','Block',{-1823.124,81.55,1397.146},{0.797,0.0,-0.604},{-0.604,0.0,-0.797},{39.849,1.0,3.7},false},
  {'COL_DS_Guard_098','Block',{-1928.71,81.55,1456.405},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.8,1.0,3.7},false},
  {'COL_DS_Guard_099','Block',{-1989.085,81.55,1441.148},{-0.835,0.0,0.551},{0.551,0.0,0.835},{51.131,1.0,3.7},false},
  {'COL_DS_Guard_104','Block',{-2010.133,81.55,1465.249},{0.11,0.0,0.994},{0.994,0.0,-0.11},{19.343,1.0,3.7},false},
  {'COL_DS_Guard_106','Block',{-1985.119,81.55,1484.377},{0.988,0.0,-0.157},{-0.157,0.0,-0.988},{23.11,1.0,3.7},false},
  {'COL_DS_Guard_109','Block',{-1959.94,81.55,1477.768},{0.942,0.0,-0.337},{-0.337,0.0,-0.942},{28.564,1.0,3.7},false},
  {'COL_DS_Guard_112','Block',{-1936.741,81.55,1466.348},{0.819,0.0,-0.574},{-0.574,0.0,-0.819},{22.883,1.0,3.7},false},
  {'COL_DS_Guard_115','Block',{-1860.098,71.55,1303.31},{-0.871,0.0,-0.492},{-0.492,0.0,0.871},{15.878,1.0,3.7},false},
  {'COL_DS_Guard_117','Block',{-1873.391,71.55,1290.602},{-0.571,0.0,-0.821},{-0.821,0.0,0.571},{21.887,1.0,3.7},false},
  {'COL_DS_Guard_120','Block',{-1891.878,71.55,1271.973},{-0.794,0.0,-0.608},{-0.608,0.0,0.794},{30.508,1.0,3.7},false},
  {'COL_DS_Guard_123','Block',{-1925.982,71.55,1240.65},{-0.68,0.0,-0.733},{-0.733,0.0,0.68},{29.836,1.0,3.7},false},
  {'COL_DS_Guard_126','Block',{-1944.033,71.55,1221.83},{-0.71,0.0,-0.705},{-0.705,0.0,0.71},{21.886,1.0,3.7},false},
  {'COL_DS_Guard_129','Block',{-1964.881,71.55,1213.835},{-1.0,0.0,0.023},{0.023,0.0,1.0},{25.388,1.0,3.7},false},
  {'COL_DS_Guard_132','Block',{-1984.373,71.55,1213.931},{-0.999,0.0,-0.035},{-0.035,0.0,0.999},{13.219,1.0,3.7},false},
  {'COL_DS_Guard_134','Block',{-1998.915,71.55,1217.807},{-0.866,0.0,0.5},{0.5,0.0,0.866},{17.047,1.0,3.7},false},
  {'COL_DS_Guard_136','Block',{-1708.583,67.55,1263.23},{-0.622,0.0,-0.783},{-0.783,0.0,0.622},{59.821,1.0,3.7},false},
  {'COL_DS_Guard_142','Block',{-1734.711,67.55,1230.327},{-0.622,0.0,-0.783},{-0.783,0.0,0.622},{3.801,1.0,3.7},false},
  {'COL_DS_Guard_143','Block',{-1751.163,67.55,1228.972},{-0.999,0.0,0.055},{0.055,0.0,0.999},{29.8,1.0,3.7},false},
  {'COL_DS_Guard_146','Block',{-1779.534,67.55,1238.161},{-0.837,0.0,0.547},{0.547,0.0,0.837},{31.016,1.0,3.7},false},
  {'COL_DS_Guard_149','Block',{-1803.986,67.55,1254.136},{-0.837,0.0,0.547},{0.547,0.0,0.837},{10.872,1.0,3.7},false},
  {'COL_DS_Guard_150','Block',{-1824.34,67.55,1272.825},{-0.705,0.0,0.71},{0.71,0.0,0.705},{43.977,1.0,3.7},false},
  {'COL_DS_Guard_155','Block',{-1847.159,67.55,1297.846},{-0.608,0.0,0.794},{0.794,0.0,0.608},{23.337,1.0,3.7},false},
  {'COL_DS_Guard_158','Block',{-1789.378,67.55,1375.248},{0.877,0.0,-0.48},{-0.48,0.0,-0.877},{40.572,1.0,3.7},false},
  {'COL_DS_Guard_162','Block',{-1755.715,67.55,1353.002},{0.782,0.0,-0.623},{-0.623,0.0,-0.782},{39.812,1.0,3.7},false},
  {'COL_DS_Guard_166','Block',{-1725.803,67.55,1327.937},{0.749,0.0,-0.663},{-0.663,0.0,-0.749},{37.813,1.0,3.7},false},
  {'COL_DS_Guard_170','Block',{-1700.982,67.55,1301.354},{0.598,0.0,-0.801},{-0.801,0.0,-0.598},{34.701,1.0,3.7},false},
  {'COL_DS_Guard_174','Block',{-1636.976,61.55,1079.113},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{9.8,1.0,3.7},false},
  {'COL_DS_Guard_175','Block',{-1652.724,61.55,1060.345},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.8,1.0,3.7},false},
  {'COL_DS_Guard_177','Block',{-1669.264,61.55,1060.684},{-0.891,0.0,0.454},{0.454,0.0,0.891},{26.457,1.0,3.7},false},
  {'COL_DS_Guard_180','Block',{-1686.066,61.55,1071.222},{-0.722,0.0,0.692},{0.692,0.0,0.722},{12.827,1.0,3.7},false},
  {'COL_DS_Guard_182','Block',{-1807.684,61.55,1050.192},{-1.0,0.0,0.003},{0.003,0.0,1.0},{30.026,1.0,3.7},false},
  {'COL_DS_Guard_185','Block',{-1839.276,61.55,1057.181},{-0.916,0.0,0.401},{0.401,0.0,0.916},{35.227,1.0,3.7},false},
  {'COL_DS_Guard_189','Block',{-1866.653,61.55,1069.679},{-0.899,0.0,0.438},{0.438,0.0,0.899},{24.507,1.0,3.7},false},
  {'COL_DS_Guard_192','Block',{-1889.908,61.55,1077.655},{-0.98,0.0,0.197},{0.197,0.0,0.98},{24.858,1.0,3.7},false},
  {'COL_DS_Guard_195','Block',{-1908.241,61.55,1083.148},{-0.884,0.0,0.468},{0.468,0.0,0.884},{13.072,1.0,3.7},false},
  {'COL_DS_Guard_197','Block',{-1959.569,61.55,1130.007},{-0.139,0.0,0.99},{0.99,0.0,0.139},{12.184,1.0,3.7},false},
  {'COL_DS_Guard_199','Block',{-1973.444,61.55,1151.181},{-0.662,0.0,0.749},{0.749,0.0,0.662},{40.236,1.0,3.7},false},
  {'COL_DS_Guard_203','Block',{-2003.731,61.55,1185.086},{-0.67,0.0,0.743},{0.743,0.0,0.67},{50.278,1.0,3.7},false},
  {'COL_DS_Guard_208','Block',{-2018.732,61.55,1207.55},{0.643,0.0,0.766},{0.766,0.0,-0.643},{7.8,1.0,3.7},false},
  {'COL_DS_Guard_209','Block',{-2004.974,61.55,1220.289},{0.923,0.0,-0.385},{-0.385,0.0,-0.923},{4.991,1.0,3.7},false},
  {'COL_DS_Guard_210','Block',{-1675.395,61.55,1271.258},{0.683,0.0,-0.731},{-0.731,0.0,-0.683},{40.089,1.0,3.7},false},
  {'COL_DS_Guard_214','Block',{-1650.361,61.55,1241.9},{0.608,0.0,-0.794},{-0.794,0.0,-0.608},{36.653,1.0,3.7},false},
  {'COL_DS_Guard_218','Block',{-1634.4,61.55,1212.313},{0.289,0.0,-0.957},{-0.957,0.0,-0.289},{30.862,1.0,3.7},false},
  {'COL_DS_Guard_221','Block',{-1633.272,61.55,1181.972},{-0.232,0.0,-0.973},{-0.973,0.0,0.232},{31.095,1.0,3.7},false},
  {'COL_DS_Guard_224','Block',{-1642.467,61.55,1153.722},{-0.399,0.0,-0.917},{-0.917,0.0,0.399},{27.955,1.0,3.7},false},
  {'COL_DS_Guard_227','Block',{-1651.885,61.55,1131.635},{-0.382,0.0,-0.924},{-0.924,0.0,0.382},{19.676,1.0,3.7},false},
  {'COL_DS_Guard_229','Block',{-1648.822,61.55,1111.409},{0.543,0.0,-0.84},{-0.84,0.0,-0.543},{26.996,1.0,3.7},false},
  {'COL_DS_Guard_232','Block',{-1637.774,61.55,1091.77},{0.398,0.0,-0.918},{-0.918,0.0,-0.398},{17.636,1.0,3.7},false},
  {'COL_DS_Guard_234','Block',{-1632.122,55.55,1005.611},{-0.881,0.0,-0.473},{-0.473,0.0,0.881},{14.936,1.0,3.7},false},
  {'COL_DS_Guard_236','Block',{-1651.116,55.55,999.696},{-0.985,0.0,-0.172},{-0.172,0.0,0.985},{24.605,1.0,3.7},false},
  {'COL_DS_Guard_239','Block',{-1668.938,55.708,998.643},{-0.973,0.0,0.232},{0.232,0.0,0.973},{10.824,1.0,3.7},false},
  {'COL_DS_Guard_240','Block',{-1678.687,56.225,1000.972},{-0.973,0.0,0.232},{0.232,0.0,0.973},{10.824,1.0,3.7},false},
  {'COL_DS_Guard_241','Block',{-1687.462,56.639,1003.068},{-0.973,0.0,0.232},{0.232,0.0,0.973},{8.819,1.0,3.7},false},
  {'COL_DS_Guard_242','Block',{-1696.685,57.278,1007.091},{-0.832,0.0,0.554},{0.554,0.0,0.832},{10.862,1.0,3.7},false},
  {'COL_DS_Guard_243','Block',{-1705.059,57.855,1012.667},{-0.832,0.0,0.554},{0.554,0.0,0.832},{10.862,1.0,3.7},false},
  {'COL_DS_Guard_244','Block',{-1713.434,58.431,1018.244},{-0.832,0.0,0.554},{0.554,0.0,0.832},{10.862,1.0,3.7},false},
  {'COL_DS_Guard_245','Block',{-1719.715,58.72,1022.427},{-0.832,0.0,0.554},{0.554,0.0,0.832},{5.831,1.0,3.7},false},
  {'COL_DS_Guard_246','Block',{-1727.349,59.328,1026.108},{-0.938,0.0,0.348},{0.348,0.0,0.938},{11.052,1.0,3.7},false},
  {'COL_DS_Guard_247','Block',{-1736.962,59.885,1029.673},{-0.938,0.0,0.348},{0.348,0.0,0.938},{11.052,1.0,3.7},false},
  {'COL_DS_Guard_248','Block',{-1745.614,60.331,1032.881},{-0.938,0.0,0.348},{0.348,0.0,0.938},{9.002,1.0,3.7},false},
  {'COL_DS_Guard_249','Block',{-1755.119,60.719,1033.359},{-0.968,0.0,-0.25},{-0.25,0.0,0.968},{11.123,1.0,3.7},false},
  {'COL_DS_Guard_250','Block',{-1765.115,61.065,1030.781},{-0.968,0.0,-0.25},{-0.25,0.0,0.968},{11.123,1.0,3.7},false},
  {'COL_DS_Guard_251','Block',{-1772.112,61.203,1028.976},{-0.968,0.0,-0.25},{-0.25,0.0,0.968},{4.929,1.0,3.7},false},
  {'COL_DS_Guard_252','Block',{-1783.171,61.525,1025.163},{-0.936,0.0,-0.353},{-0.353,0.0,0.936},{18.138,1.0,3.7},false},
  {'COL_DS_Guard_254','Block',{-1792.738,61.55,1036.433},{0.012,0.0,1.0},{1.0,0.0,-0.012},{27.195,1.0,3.7},false},
  {'COL_DS_Guard_257','Block',{-1652.689,56.992,1051.83},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{10.8,1.0,3.7},false},
  {'COL_DS_Guard_258','Block',{-1600.752,55.55,1038.274},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{13.8,1.0,3.7},false},
  {'COL_DS_Guard_260','Block',{-1620.678,55.55,1014.527},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{11.8,1.0,3.7},false},
  {'COL_DS_Guard_262','Block',{-1625.87,55.55,1009.537},{-0.957,0.0,0.289},{0.289,0.0,0.957},{1.815,1.0,3.7},false},
  {'COL_DS_Guard_263','Block',{-1644.297,55.55,1053.274},{0.643,0.0,0.766},{0.766,0.0,-0.643},{12.8,1.0,3.7},false},
  {'COL_DS_Guard_265','Block',{-1621.011,55.55,1064.145},{0.94,0.0,-0.342},{-0.342,0.0,-0.94},{23.191,1.0,3.7},false},
  {'COL_DS_Guard_268','Block',{-1603.26,55.55,1052.245},{0.625,0.0,-0.781},{-0.781,0.0,-0.625},{20.176,1.0,3.7},false},
  {'COL_DS_PierGuard_001','Block',{-2058.566,81.8,1530.524},{-0.574,0.0,0.819},{0.819,0.0,0.574},{31.2,1.2,4.2},false},
  {'COL_DS_PierGuard_002','Block',{-2047.407,81.8,1519.294},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,6.6,4.2},false},
  {'COL_DS_PierGuard_003','Block',{-2065.302,81.8,1544.851},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,6.6,4.2},false},
  {'COL_DS_PierGuard_004','Block',{-2033.009,81.8,1548.419},{-0.574,0.0,0.819},{0.819,0.0,0.574},{31.2,1.2,4.2},false},
  {'COL_DS_PierGuard_005','Block',{-2026.273,81.8,1534.092},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,6.6,4.2},false},
  {'COL_DS_PierGuard_006','Block',{-2044.168,81.8,1559.649},{-0.574,0.0,0.819},{0.819,0.0,0.574},{1.2,6.6,4.2},false},
  {'COL_DS_Pier_001','Block',{-2045.787,76.2,1539.471},{-0.574,0.0,0.819},{0.819,0.0,0.574},{31.0,30.0,8.0},false},
  {'COL_DS_PondGuard_001','Block',{-1972.901,61.55,1186.716},{-0.508,0.0,-0.861},{-0.861,0.0,0.508},{25.131,1.0,3.7},false},
  {'COL_DS_PondGuard_002','Block',{-1987.906,61.55,1179.725},{-0.93,0.0,0.368},{0.368,0.0,0.93},{19.774,1.0,3.7},false},
  {'COL_DS_PondGuard_003','Block',{-2007.255,61.55,1194.003},{-0.698,0.0,0.716},{0.716,0.0,0.698},{30.95,1.0,3.7},false},
  {'COL_DS_PondGuard_004','Block',{-2012.701,61.55,1211.626},{0.597,0.0,0.802},{0.802,0.0,-0.597},{17.829,1.0,3.7},false},
  {'COL_DS_PondGuard_005','Block',{-2000.268,61.55,1215.553},{0.93,0.0,-0.368},{-0.368,0.0,-0.93},{16.611,1.0,3.7},false},
  {'COL_DS_PondGuard_006','Block',{-1984.216,61.55,1210.569},{0.973,0.0,-0.232},{-0.232,0.0,-0.973},{18.689,1.0,3.7},false},
  {'COL_DS_PondGuard_007','Block',{-1971.118,61.55,1202.843},{0.614,0.0,-0.789},{-0.789,0.0,-0.614},{15.118,1.0,3.7},false},
  {'COL_DS_PropFence_001','Block',{-1661.398,61.64,1076.36},{-0.829,0.0,0.559},{0.559,0.0,0.829},{18.017,0.5,3.0},false},
  {'COL_DS_PropFence_002','Block',{-1677.516,61.64,1086.469},{-0.892,0.0,0.452},{0.452,0.0,0.892},{6.871,0.5,3.0},false},
  {'COL_DS_PropFence_003','Block',{-1700.236,61.64,1096.635},{-0.934,0.0,0.356},{0.356,0.0,0.934},{19.762,0.5,3.0},false},
  {'COL_DS_PropFence_004','Block',{-1720.62,61.79,1103.857},{-0.951,0.0,0.31},{0.31,0.0,0.951},{8.299,0.5,3.0},false},
  {'COL_DS_PropFence_005','Block',{-1662.772,56.258,1026.993},{-0.994,0.0,0.11},{0.11,0.0,0.994},{10.4,0.5,3.0},false},
  {'COL_DS_PropFence_006','Block',{-1672.712,56.738,1028.092},{-0.994,0.0,0.11},{0.11,0.0,0.994},{10.4,0.5,3.0},false},
  {'COL_DS_PropFence_007','Block',{-1681.598,57.218,1029.511},{-0.976,0.0,0.217},{0.217,0.0,0.976},{8.424,0.5,3.0},false},
  {'COL_DS_PropFence_008','Block',{-1685.983,57.218,1030.557},{-0.935,0.0,0.354},{0.354,0.0,0.935},{1.4,0.5,3.0},false},
  {'COL_DS_PropFence_009','Block',{-1718.716,59.317,1042.932},{-0.935,0.0,0.353},{0.353,0.0,0.935},{9.389,0.5,3.0},false},
  {'COL_DS_PropFence_010','Block',{-1727.602,59.807,1046.277},{-0.936,0.0,0.351},{0.351,0.0,0.936},{10.4,0.5,3.0},false},
  {'COL_DS_PropFence_011','Block',{-1741.178,60.623,1051.369},{-0.936,0.0,0.351},{0.351,0.0,0.936},{9.4,0.5,3.0},false},
  {'COL_DS_PropFence_012','Block',{-1687.618,57.848,1040.37},{-0.935,0.0,0.354},{0.354,0.0,0.935},{9.4,0.5,3.0},false},
  {'COL_DS_PropFence_013','Block',{-1696.037,58.338,1043.553},{-0.935,0.0,0.354},{0.354,0.0,0.935},{9.4,0.5,3.0},false},
  {'COL_DS_PropFence_014','Block',{-1703.987,58.828,1046.559},{-0.935,0.0,0.354},{0.354,0.0,0.935},{8.4,0.5,3.0},false},
  {'COL_DS_PropFence_015','Block',{-1727.601,61.82,1170.201},{-0.731,0.0,0.682},{0.682,0.0,0.731},{23.4,0.5,3.0},false},
  {'COL_DS_PropFence_016','Block',{-1797.546,61.64,1231.47},{-0.766,0.0,0.643},{0.643,0.0,0.766},{11.4,0.5,3.0},false},
  {'COL_DS_PropFence_017','Block',{-1836.211,61.82,1262.353},{-0.797,0.0,0.604},{0.604,0.0,0.797},{32.4,0.5,3.0},false},
  {'COL_DS_PropFence_018','Block',{-1836.248,61.64,1074.467},{-0.882,0.0,0.471},{0.471,0.0,0.882},{10.351,0.5,3.0},false},
  {'COL_DS_PropFence_019','Block',{-1841.838,61.64,1077.708},{-0.801,0.0,0.598},{0.598,0.0,0.801},{3.4,0.5,3.0},false},
  {'COL_DS_PropFence_020','Block',{-1877.121,61.64,1105.581},{-0.747,0.0,0.664},{0.664,0.0,0.747},{15.4,0.5,3.0},false},
  {'COL_DS_PropFence_021','Block',{-1939.758,61.64,1160.689},{-0.712,0.0,0.702},{0.702,0.0,0.712},{26.332,0.5,3.0},false},
  {'COL_DS_PropFence_022','Block',{-1950.583,61.64,1173.461},{-0.398,0.0,0.918},{0.918,0.0,0.398},{8.4,0.5,3.0},false},
  {'COL_DS_PropFence_023','Block',{-1935.748,61.82,1216.983},{-0.71,0.0,-0.705},{-0.705,0.0,0.71},{19.4,0.5,3.0},false},
  {'COL_DS_PropFence_024','Block',{-1951.635,61.82,1203.345},{-0.809,0.0,-0.587},{-0.587,0.0,0.809},{13.4,0.5,3.0},false},
  {'COL_DS_PropFence_025','Block',{-1876.172,71.64,1291.571},{-0.581,0.0,-0.814},{-0.814,0.0,0.581},{23.47,0.5,3.0},false},
  {'COL_DS_PropFence_026','Block',{-1892.028,71.64,1274.852},{-0.781,0.0,-0.625},{-0.625,0.0,0.781},{23.855,0.5,3.0},false},
  {'COL_DS_PropFence_027','Block',{-1936.834,71.558,1232.165},{-0.71,0.0,-0.704},{-0.704,0.0,0.71},{44.584,0.5,3.0},false},
  {'COL_DS_PropFence_028','Block',{-1961.532,71.558,1215.947},{-0.997,0.0,-0.073},{-0.073,0.0,0.997},{18.475,0.5,3.0},false},
  {'COL_DS_PropPath_001','Block',{-1654.34,56.779,1035.015},{0.994,0.0,-0.11},{-0.11,0.0,-0.994},{1.44,1.44,3.701},false},
  {'COL_DS_PropPath_002','Block',{-1709.788,59.426,1039.878},{-0.935,0.0,0.354},{0.354,0.0,0.935},{1.44,1.44,3.734},false},
  {'COL_DS_PropPath_003','Block',{-1754.328,62.026,1066.084},{0.877,0.0,-0.48},{-0.48,0.0,-0.877},{1.44,1.44,3.653},false},
  {'COL_DS_PropPath_004','Block',{-1725.684,62.07,1128.372},{0.726,0.0,0.687},{0.687,0.0,-0.726},{1.44,1.44,3.739},false},
  {'COL_DS_PropPath_005','Block',{-1733.257,62.15,1123.794},{0.738,0.0,0.674},{0.674,0.0,-0.738},{1.44,1.44,3.901},false},
  {'COL_DS_PropPath_006','Block',{-1765.168,61.675,1092.723},{0.752,0.0,0.659},{0.659,0.0,-0.752},{1.44,1.44,3.949},false},
  {'COL_DS_PropPath_007','Block',{-1781.46,62.024,1078.565},{0.809,0.0,0.587},{0.587,0.0,-0.809},{1.44,1.44,3.648},false},
  {'COL_DS_PropPath_008','Block',{-1744.7,62.363,1185.148},{0.753,0.0,-0.658},{-0.658,0.0,-0.753},{1.44,1.44,3.967},false},
  {'COL_DS_PropPath_009','Block',{-1777.642,62.224,1217.118},{0.753,0.0,-0.658},{-0.658,0.0,-0.753},{1.44,1.44,3.689},false},
  {'COL_DS_PropPath_010','Block',{-1823.167,62.383,1251.722},{0.797,0.0,-0.604},{-0.604,0.0,-0.797},{1.44,1.44,4.007},false},
  {'COL_DS_PropPath_011','Block',{-1847.436,62.215,1081.137},{0.801,0.0,-0.598},{-0.598,0.0,-0.801},{1.44,1.44,3.671},false},
  {'COL_DS_PropPath_012','Block',{-1886.707,62.02,1114.103},{0.747,0.0,-0.664},{-0.664,0.0,-0.747},{1.44,1.44,3.64},false},
  {'COL_DS_PropPath_013','Block',{-1913.987,62.4,1138.064},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{1.44,1.44,4.039},false},
  {'COL_DS_PropPath_014','Block',{-1928.684,62.391,1148.991},{0.722,0.0,-0.692},{-0.692,0.0,-0.722},{1.44,1.44,4.023},false},
  {'COL_DS_PropPath_015','Block',{-1953.932,62.116,1179.677},{0.398,0.0,-0.918},{-0.918,0.0,-0.398},{1.44,1.44,3.833},false},
  {'COL_DS_PropPath_016','Block',{-1905.879,62.295,1246.039},{0.696,0.0,0.718},{0.718,0.0,-0.696},{1.44,1.44,3.83},false},
  {'COL_DS_PropPath_017','Block',{-1890.908,82.07,1405.408},{0.605,0.0,-0.797},{-0.797,0.0,-0.605},{1.44,1.44,3.739},false},
  {'COL_DS_PropPath_018','Block',{-1911.981,82.314,1417.295},{-0.605,0.0,0.797},{0.797,0.0,0.605},{1.44,1.44,3.867},false},
  {'COL_DS_PropPath_019','Block',{-1936.883,82.237,1439.578},{-0.821,0.0,0.571},{0.571,0.0,0.821},{1.44,1.44,3.714},false},
  {'COL_DS_PropPath_020','Block',{-1946.856,82.355,1458.933},{0.821,0.0,-0.571},{-0.571,0.0,-0.821},{1.44,1.44,3.949},false},
  {'COL_DS_PropPath_021','Block',{-1993.394,81.658,1468.57},{-0.889,0.0,0.457},{0.457,0.0,0.889},{1.44,1.44,3.916},false},
  {'COL_DS_PropPath_022','Block',{-1789.401,61.1,1231.163},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.0,1.8,1.8},false},
  {'COL_DS_PropPath_023','Block',{-1716.905,58.361,1031.306},{0.643,0.0,0.766},{0.766,0.0,-0.643},{5.0,1.8,1.8},false},
  {'COL_DS_PropPath_024','Block',{-1937.149,81.1,1459.571},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.0,1.8,1.8},false},
  {'COL_DS_PropPath_025','Block',{-1646.64,63.18,1080.042},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.6,0.6,5.6},false},
  {'COL_DS_PropPath_026','Block',{-1914.857,63.18,1237.222},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.6,0.6,5.6},false},
  {'COL_DS_PropPath_027','Block',{-1890.232,82.5,1381.693},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.6,0.6,5.6},false},
  {'COL_DS_PropPath_028','Block',{-1723.221,61.3,1188.686},{-0.985,0.0,0.174},{0.174,0.0,0.985},{2.8,2.4,2.2},false},
  {'COL_DS_PropPath_029','Block',{-1814.847,67.48,1278.623},{-0.866,0.0,0.5},{0.5,0.0,0.866},{2.8,2.4,2.2},false},
  {'COL_DS_PropPath_030','Block',{-1873.978,80.8,1341.946},{-0.866,0.0,0.5},{0.5,0.0,0.866},{2.8,2.4,2.2},false},
  {'COL_DS_Prop_001','Block',{-1679.755,62.32,1205.188},{-0.866,0.0,-0.5},{-0.5,0.0,0.866},{6.8,2.0,4.0},false},
  {'COL_DS_Prop_002','Block',{-1703.022,61.72,1211.261},{0.219,0.0,-0.976},{-0.976,0.0,-0.219},{2.4,2.4,2.8},false},
  {'COL_DS_Prop_003','Block',{-1700.035,61.52,1212.447},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,2.4},false},
  {'COL_DS_Prop_004','Block',{-1719.038,67.62,1270.68},{0.643,0.0,0.766},{0.766,0.0,-0.643},{5.0,2.6,2.6},false},
  {'COL_DS_Prop_005','Block',{-1732.795,67.42,1257.551},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,2.2},false},
  {'COL_DS_Prop_006','Block',{-1734.822,67.42,1256.38},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,2.2},false},
  {'COL_DS_Prop_007','Block',{-1732.341,67.42,1255.603},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,2.2},false},
  {'COL_DS_Prop_008','Block',{-1732.684,66.94,1250.488},{0.469,0.0,0.883},{0.883,0.0,-0.469},{8.0,3.6,2.6},false},
  {'COL_DS_Prop_009','Block',{-1777.012,66.74,1284.99},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,2.2},false},
  {'COL_DS_Prop_010','Block',{-1740.304,61.7,1086.185},{-0.791,0.0,-0.611},{-0.611,0.0,0.791},{11.659,0.5,3.0},false},
  {'COL_DS_Prop_011','Block',{-1749.841,61.7,1079.176},{-0.818,0.0,-0.575},{-0.575,0.0,0.818},{12.819,0.5,3.0},false},
  {'COL_DS_Prop_012','Block',{-1778.407,61.7,1060.067},{-0.897,0.0,-0.442},{-0.442,0.0,0.897},{11.325,0.5,3.0},false},
  {'COL_DS_Prop_013','Block',{-1788.741,61.7,1055.685},{-0.94,0.0,-0.34},{-0.34,0.0,0.94},{11.96,0.5,3.0},false},
  {'COL_DS_Prop_014','Block',{-1758.947,61.7,1206.783},{-0.738,0.0,0.675},{0.675,0.0,0.738},{14.413,0.5,3.0},false},
  {'COL_DS_Prop_015','Block',{-1769.221,61.7,1216.319},{-0.728,0.0,0.685},{0.685,0.0,0.728},{14.423,0.5,3.0},false},
  {'COL_DS_Prop_016','Block',{-1891.092,61.7,1267.8},{-0.811,0.0,-0.585},{-0.585,0.0,0.811},{15.462,0.5,3.0},false},
  {'COL_DS_Prop_017','Block',{-1921.574,61.7,1240.574},{-0.67,0.0,-0.742},{-0.742,0.0,0.67},{16.911,0.5,3.0},false},
  {'COL_DS_Prop_018','Block',{-1725.583,61.72,1171.87},{-0.695,0.0,0.719},{0.719,0.0,0.695},{5.4,2.6,2.8},false},
  {'COL_DS_Prop_019','Block',{-2002.988,82.04,1262.872},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.6,6.4,3.8},false},
  {'COL_DS_Prop_020','Block',{-1998.654,80.84,1279.861},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.4,3.0,2.4},false},
  {'COL_DS_Prop_021','Block',{-1999.572,80.84,1261.965},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.6,2.6,1.4},false},
  {'COL_DS_Prop_022','Block',{-1994.852,80.64,1283.459},{-0.743,0.0,-0.669},{-0.669,0.0,0.743},{3.4,2.4,2.0},false},
  {'COL_DS_Prop_023','Block',{-1986.665,82.04,1266.146},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.8,2.0,3.8},false},
  {'COL_DS_Prop_024','Block',{-1927.284,80.84,1367.094},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.4,3.0,2.4},false},
  {'COL_DS_Prop_025','Block',{-1642.851,64.5,1079.735},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_Prop_026','Block',{-1730.953,64.68,1098.573},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_Prop_027','Block',{-1898.411,64.68,1261.801},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_Prop_028','Block',{-1915.181,64.5,1119.224},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_Prop_029','Block',{-1670.837,59.603,1023.979},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.0,1.0,8.6},false},
  {'COL_DS_StairOesteForja_001','Ramp',{-1842.212,72.743,1306.806},{-0.7,0.406,0.587},{0.643,-0.0,0.766},{34.471,10.0,1.0},false},
  {'COL_DS_StairOesteForja_002','Block',{-1854.571,79.7,1317.177},{-0.766,0.0,0.643},{0.643,0.0,0.766},{1.175,10.0,1.0},false},
  {'COL_DS_StairOesteForja_003','Ramp',{-1845.934,74.352,1302.619},{-0.7,0.406,0.587},{0.643,0.0,0.766},{34.471,1.2,5.5},false},
  {'COL_DS_StairOesteForja_004','Ramp',{-1838.734,74.352,1311.199},{-0.7,0.406,0.587},{0.643,0.0,0.766},{34.471,1.2,5.5},false},
  {'COL_DS_StairSubidaA_001','Ramp',{-1918.605,64.74,1263.864},{-0.704,0.393,0.591},{0.643,-0.0,0.766},{25.447,16.0,1.0},false},
  {'COL_DS_StairSubidaA_002','Block',{-1927.877,69.7,1271.644},{-0.766,0.0,0.643},{0.643,0.0,0.766},{1.2,16.0,1.0},false},
  {'COL_DS_StairSubidaA_003','Ramp',{-1924.286,66.379,1257.405},{-0.704,0.393,0.591},{0.643,0.0,0.766},{25.447,1.2,5.5},false},
  {'COL_DS_StairSubidaA_004','Ramp',{-1913.23,66.379,1270.581},{-0.704,0.393,0.591},{0.643,0.0,0.766},{25.447,1.2,5.5},false},
  {'COL_DS_StairSubidaB_001','Ramp',{-1955.948,74.74,1276.923},{-0.704,0.393,0.591},{0.643,0.0,0.766},{25.447,14.0,1.0},false},
  {'COL_DS_StairSubidaB_002','Block',{-1965.22,79.7,1284.703},{-0.766,0.0,0.643},{0.643,0.0,0.766},{1.2,14.0,1.0},false},
  {'COL_DS_StairSubidaB_003','Ramp',{-1960.986,76.379,1271.229},{-0.704,0.393,0.591},{0.643,0.0,0.766},{25.447,1.2,5.5},false},
  {'COL_DS_StairSubidaB_004','Ramp',{-1951.216,76.379,1282.873},{-0.704,0.393,0.591},{0.643,0.0,0.766},{25.447,1.2,5.5},false},
  {'COL_DS_StairSummon_001','Ramp',{-1930.067,64.742,1113.307},{-0.588,0.402,-0.701},{-0.766,-0.0,0.643},{24.851,12.0,1.0},false},
  {'COL_DS_StairSummon_002','Block',{-1937.627,69.7,1104.297},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.175,12.0,1.0},false},
  {'COL_DS_StairSummon_003','Ramp',{-1925.117,66.357,1108.938},{-0.588,0.402,-0.701},{-0.766,-0.0,0.643},{24.851,1.2,5.5},false},
  {'COL_DS_StairSummon_004','Ramp',{-1935.229,66.357,1117.422},{-0.588,0.402,-0.701},{-0.766,-0.0,0.643},{24.851,1.2,5.5},false},
  {'COL_DS_StairTrilha_001','Ramp',{-1639.0,56.738,1065.799},{-0.707,0.385,0.593},{0.643,0.0,0.766},{15.6,12.0,1.0},false},
  {'COL_DS_StairTrilha_002','Block',{-1644.828,59.7,1070.689},{-0.766,0.0,0.643},{0.643,0.0,0.766},{1.2,12.0,1.0},false},
  {'COL_DS_StairTrilha_003','Ramp',{-1643.405,58.389,1060.879},{-0.707,0.385,0.593},{0.643,0.0,0.766},{15.6,1.2,5.5},false},
  {'COL_DS_StairTrilha_004','Ramp',{-1634.92,58.389,1070.991},{-0.707,0.385,0.593},{0.643,0.0,0.766},{15.6,1.2,5.5},false},
  {'COL_DS_StairVilaAlta_001','Ramp',{-1727.543,62.738,1234.085},{-0.707,0.385,0.593},{0.643,0.0,0.766},{15.6,10.0,1.0},false},
  {'COL_DS_StairVilaAlta_002','Block',{-1733.371,65.7,1238.975},{-0.766,0.0,0.643},{0.643,0.0,0.766},{1.2,10.0,1.0},false},
  {'COL_DS_StairVilaAlta_003','Ramp',{-1731.305,64.389,1229.931},{-0.707,0.385,0.593},{0.643,-0.0,0.766},{15.6,1.2,5.5},false},
  {'COL_DS_StairVilaAlta_004','Ramp',{-1724.106,64.389,1238.511},{-0.707,0.385,0.593},{0.643,-0.0,0.766},{15.6,1.2,5.5},false},
  {'COL_DS_StairVilaClareira_001','Ramp',{-1796.199,62.738,1247.953},{0.593,0.385,0.707},{0.766,-0.0,-0.643},{15.6,8.0,1.0},false},
  {'COL_DS_StairVilaClareira_002','Block',{-1791.309,65.7,1253.781},{0.643,0.0,0.766},{0.766,0.0,-0.643},{1.2,8.0,1.0},false},
  {'COL_DS_StairVilaClareira_003','Ramp',{-1799.586,64.389,1251.072},{0.593,0.385,0.707},{0.766,-0.0,-0.643},{15.6,1.2,5.5},false},
  {'COL_DS_StairVilaClareira_004','Ramp',{-1792.539,64.389,1245.158},{0.593,0.385,0.707},{0.766,-0.0,-0.643},{15.6,1.2,5.5},false},
  {'COL_DS_SumBridge_001','Ramp',{-1915.786,60.376,1130.325},{-0.609,0.32,-0.726},{-0.766,0.0,0.643},{4.064,9.5,1.0},false},
  {'COL_DS_SumBridge_002','Ramp',{-1917.882,61.205,1127.828},{-0.637,0.139,-0.759},{-0.766,0.0,0.643},{2.878,9.5,1.0},false},
  {'COL_DS_SumBridge_003','Ramp',{-1919.624,61.205,1125.752},{-0.637,-0.139,-0.759},{-0.766,-0.0,0.643},{2.878,9.5,1.0},false},
  {'COL_DS_SumBridge_004','Ramp',{-1921.65,60.379,1123.337},{-0.606,-0.336,-0.722},{-0.766,0.0,0.643},{3.875,9.5,1.0},false},
  {'COL_DS_SumBridge_005','Block',{-1914.961,62.6,1123.608},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.74,0.6,4.8},false},
  {'COL_DS_SumBridge_006','Block',{-1922.545,62.6,1129.972},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.74,0.6,4.8},false},
  {'COL_DS_SumRail_001','Block',{-1921.405,71.6,1073.724},{-0.454,0.0,-0.891},{-0.891,0.0,0.454},{25.967,0.5,3.4},false},
  {'COL_DS_SumRail_002','Block',{-1938.382,71.6,1056.547},{-0.888,0.0,-0.46},{-0.46,0.0,0.888},{25.565,0.5,3.4},false},
  {'COL_DS_SumRail_003','Block',{-1961.094,71.6,1056.641},{-0.891,0.0,0.454},{0.454,0.0,0.891},{26.301,0.5,3.4},false},
  {'COL_DS_SumRail_004','Block',{-1979.824,71.6,1073.64},{-0.543,0.0,0.84},{0.84,0.0,0.543},{26.884,0.5,3.4},false},
  {'COL_DS_SumRail_005','Block',{-1983.612,71.6,1096.988},{0.268,0.0,0.963},{0.963,0.0,-0.268},{21.766,0.5,3.4},false},
  {'COL_DS_SumRail_006','Block',{-1970.546,71.6,1114.969},{0.799,0.0,0.602},{0.602,0.0,-0.799},{25.949,0.5,3.4},false},
  {'COL_DS_SumRail_007','Block',{-1952.183,71.6,1115.809},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{21.708,0.5,3.4},false},
  {'COL_DS_SumRail_008','Block',{-1923.762,71.6,1091.961},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{21.708,0.5,3.4},false},
  {'COL_DS_SumShelter_001','Block',{-1977.97,73.3,1087.254},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.7,0.7,6.2},true},
  {'COL_DS_SumShelter_002','Block',{-1981.724,73.3,1090.404},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.7,0.7,6.2},true},
  {'COL_DS_SumShelter_003','Block',{-1982.02,73.3,1082.428},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.7,0.7,6.2},true},
  {'COL_DS_SumShelter_004','Block',{-1985.773,73.3,1085.578},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.7,0.7,6.2},true},
  {'COL_DS_SumShelter_005','Block',{-1983.557,70.92,1087.83},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.4,1.6,1.45},false},
  {'COL_DS_SumShelter_006','Block',{-1983.802,71.9,1088.036},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.4,0.5,3.4},false},
  {'COL_DS_SumShelter_007','Block',{-1983.468,70.92,1083.97},{-0.766,0.0,0.643},{0.643,0.0,0.766},{4.3,1.6,1.45},false},
  {'COL_DS_SumShelter_008','Block',{-1983.673,71.9,1083.724},{-0.766,0.0,0.643},{0.643,0.0,0.766},{4.3,0.5,3.4},false},
  {'COL_DS_SumWisteria_001','Block',{-1931.061,73.95,1065.45},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,7.5},false},
  {'COL_DS_SumWisteria_002','Block',{-1977.023,73.95,1104.018},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.9,1.9,7.5},false},
  {'COL_DS_TerWall_001','Block',{-1949.6,65.2,1116.475},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{22.6,2.34,10.0},false},
  {'COL_DS_TerWall_003','Block',{-1922.406,65.2,1093.656},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{23.6,2.34,10.0},false},
  {'COL_DS_TerWall_005','Block',{-2010.791,70.2,1215.939},{-0.597,0.0,-0.802},{-0.802,0.0,0.597},{12.62,1.08,20.0},false},
  {'COL_DS_TerWall_006','Block',{-1860.294,65.2,1302.635},{-0.871,0.0,-0.492},{-0.492,0.0,0.871},{16.683,1.98,10.0},false},
  {'COL_DS_TerWall_007','Block',{-1869.975,65.2,1294.342},{-0.571,0.0,-0.821},{-0.821,0.0,0.571},{11.645,2.34,10.0},false},
  {'COL_DS_TerWall_009','Block',{-1891.47,65.2,1271.441},{-0.794,0.0,-0.608},{-0.608,0.0,0.794},{30.308,2.34,10.0},false},
  {'COL_DS_TerWall_011','Block',{-1925.831,65.2,1239.827},{-0.68,0.0,-0.733},{-0.733,0.0,0.68},{30.638,2.34,10.0},false},
  {'COL_DS_TerWall_014','Block',{-1939.999,65.2,1224.893},{-0.71,0.0,-0.705},{-0.705,0.0,0.71},{11.645,2.34,10.0},false},
  {'COL_DS_TerWall_016','Block',{-1965.409,65.2,1213.177},{-1.0,0.0,0.023},{0.023,0.0,1.0},{26.213,2.34,10.0},false},
  {'COL_DS_TerWall_018','Block',{-1984.873,65.2,1213.423},{-0.999,0.0,-0.035},{-0.035,0.0,0.999},{14.054,1.98,10.0},false},
  {'COL_DS_TerWall_019','Block',{-1997.401,65.2,1216.368},{-0.866,0.0,0.5},{0.5,0.0,0.866},{12.785,1.98,10.0},false},
  {'COL_DS_Terrain_001','Block',{-1925.237,58.1,1067.724},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{39.53,6.0,24.2},false},
  {'COL_DS_Terrain_002','Block',{-1933.102,58.1,1067.685},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{49.7,6.0,24.2},false},
  {'COL_DS_Terrain_003','Block',{-1938.143,58.1,1071.012},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{51.085,6.0,24.2},false},
  {'COL_DS_Terrain_004','Block',{-1943.184,58.1,1074.338},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{52.469,6.0,24.2},false},
  {'COL_DS_Terrain_005','Block',{-1948.225,58.1,1077.664},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{53.854,6.0,24.2},false},
  {'COL_DS_Terrain_006','Block',{-1955.565,58.1,1082.919},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{55.238,12.0,24.2},false},
  {'COL_DS_Terrain_008','Block',{-1961.865,58.1,1089.413},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{53.388,6.0,24.2},false},
  {'COL_DS_Terrain_009','Block',{-1965.868,58.1,1093.977},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{51.542,6.0,24.2},false},
  {'COL_DS_Terrain_010','Block',{-1969.87,58.1,1098.541},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{49.696,6.0,24.2},false},
  {'COL_DS_Terrain_011','Block',{-1973.873,58.1,1103.104},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{47.85,6.0,24.2},false},
  {'COL_DS_Terrain_012','Block',{-1975.413,58.1,1110.604},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{38.34,6.0,24.2},false},
  {'COL_DS_Terrain_013','Block',{-1923.237,58.1,1092.336},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.75,22.923,24.2},false},
  {'COL_DS_Terrain_017','Block',{-1951.904,58.1,1116.391},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.75,22.923,24.2},false},
  {'COL_DS_Terrain_021','Block',{-1831.741,63.1,1348.898},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{65.45,6.0,34.2},false},
  {'COL_DS_Terrain_022','Block',{-1833.061,63.1,1356.66},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{75.644,6.0,34.2},false},
  {'COL_DS_Terrain_023','Block',{-1837.706,63.1,1360.458},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{75.492,6.0,34.2},false},
  {'COL_DS_Terrain_024','Block',{-1842.399,63.1,1364.2},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{75.192,6.0,34.2},false},
  {'COL_DS_Terrain_025','Block',{-1847.092,63.1,1367.942},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{74.892,6.0,34.2},false},
  {'COL_DS_Terrain_026','Block',{-1851.784,63.1,1371.683},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{74.592,6.0,34.2},false},
  {'COL_DS_Terrain_027','Block',{-1856.477,63.1,1375.425},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{74.292,6.0,34.2},false},
  {'COL_DS_Terrain_028','Block',{-1861.17,63.1,1379.167},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{73.992,6.0,34.2},false},
  {'COL_DS_Terrain_029','Block',{-1865.89,63.1,1382.875},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{73.605,6.0,34.2},false},
  {'COL_DS_Terrain_030','Block',{-1870.728,63.1,1386.445},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{72.855,6.0,34.2},false},
  {'COL_DS_Terrain_031','Block',{-1875.565,63.1,1390.014},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{72.105,6.0,34.2},false},
  {'COL_DS_Terrain_032','Block',{-1880.402,63.1,1393.584},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{71.355,6.0,34.2},false},
  {'COL_DS_Terrain_033','Block',{-1885.24,63.1,1397.153},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{70.605,6.0,34.2},false},
  {'COL_DS_Terrain_034','Block',{-1890.077,63.1,1400.723},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{69.855,6.0,34.2},false},
  {'COL_DS_Terrain_035','Block',{-1894.914,63.1,1404.292},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{69.105,6.0,34.2},false},
  {'COL_DS_Terrain_036','Block',{-1899.853,63.1,1407.74},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{68.038,6.0,34.2},false},
  {'COL_DS_Terrain_037','Block',{-1904.883,63.1,1411.08},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.688,6.0,34.2},false},
  {'COL_DS_Terrain_038','Block',{-1909.914,63.1,1414.42},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{65.338,6.0,34.2},false},
  {'COL_DS_Terrain_039','Block',{-1914.944,63.1,1417.76},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{63.988,6.0,34.2},false},
  {'COL_DS_Terrain_040','Block',{-1919.974,63.1,1421.099},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{62.638,6.0,34.2},false},
  {'COL_DS_Terrain_041','Block',{-1925.004,63.1,1424.439},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{61.288,6.0,34.2},false},
  {'COL_DS_Terrain_042','Block',{-1930.034,63.1,1427.778},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{59.938,6.0,34.2},false},
  {'COL_DS_Terrain_043','Block',{-1935.521,63.1,1430.574},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{57.168,6.0,34.2},false},
  {'COL_DS_Terrain_044','Block',{-1941.081,63.1,1433.282},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{54.168,6.0,34.2},false},
  {'COL_DS_Terrain_045','Block',{-1946.642,63.1,1435.99},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{51.168,6.0,34.2},false},
  {'COL_DS_Terrain_046','Block',{-1952.202,63.1,1438.697},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{48.168,6.0,34.2},false},
  {'COL_DS_Terrain_047','Block',{-1957.385,63.1,1441.855},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{42.442,6.0,34.2},false},
  {'COL_DS_Terrain_049','Block',{-1862.412,63.1,1310.937},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{7.14,6.0,34.2},false},
  {'COL_DS_Terrain_050','Block',{-1869.323,63.1,1312.036},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{14.34,6.0,34.2},false},
  {'COL_DS_Terrain_051','Block',{-1876.233,63.1,1313.135},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{21.54,6.0,34.2},false},
  {'COL_DS_Terrain_052','Block',{-1882.026,63.1,1315.566},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{25.262,6.0,34.2},false},
  {'COL_DS_Terrain_053','Block',{-1887.323,63.1,1318.587},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{27.444,6.0,34.2},false},
  {'COL_DS_Terrain_054','Block',{-1892.62,63.1,1321.608},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{29.626,6.0,34.2},false},
  {'COL_DS_Terrain_055','Block',{-1897.918,63.1,1324.629},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{31.808,6.0,34.2},false},
  {'COL_DS_Terrain_056','Block',{-1903.216,63.1,1327.65},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{33.989,6.0,34.2},false},
  {'COL_DS_Terrain_057','Block',{-1908.513,63.1,1330.672},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{36.171,6.0,34.2},false},
  {'COL_DS_Terrain_058','Block',{-1913.811,63.1,1333.693},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{38.353,6.0,34.2},false},
  {'COL_DS_Terrain_059','Block',{-1964.447,63.1,1348.02},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{81.5,90.001,34.2},false},
  {'COL_DS_Terrain_074','Block',{-1990.122,63.1,1388.818},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{52.0,1.783,34.2},false},
  {'COL_DS_Terrain_075','Block',{-1914.143,63.1,1367.162},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.5,154.955,34.2},false},
  {'COL_DS_Terrain_101','Block',{-1993.393,63.1,1241.637},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{85.7,6.0,34.2},false},
  {'COL_DS_Terrain_102','Block',{-2002.216,63.1,1245.124},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{91.7,12.0,34.2},false},
  {'COL_DS_Terrain_104','Block',{-2009.024,63.1,1251.012},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{91.432,6.0,34.2},false},
  {'COL_DS_Terrain_105','Block',{-2013.519,63.1,1254.989},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{91.116,6.0,34.2},false},
  {'COL_DS_Terrain_106','Block',{-2018.014,63.1,1258.967},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{90.8,6.0,34.2},false},
  {'COL_DS_Terrain_107','Block',{-2022.508,63.1,1262.945},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{90.484,6.0,34.2},false},
  {'COL_DS_Terrain_108','Block',{-2027.003,63.1,1266.922},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{90.168,6.0,34.2},false},
  {'COL_DS_Terrain_109','Block',{-2031.498,63.1,1270.9},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{89.853,6.0,34.2},false},
  {'COL_DS_Terrain_110','Block',{-2035.678,63.1,1275.252},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{88.559,6.0,34.2},false},
  {'COL_DS_Terrain_111','Block',{-2039.708,63.1,1279.785},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{86.794,6.0,34.2},false},
  {'COL_DS_Terrain_112','Block',{-2043.737,63.1,1284.318},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{85.029,6.0,34.2},false},
  {'COL_DS_Terrain_113','Block',{-2047.766,63.1,1288.85},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{83.265,6.0,34.2},false},
  {'COL_DS_Terrain_114','Block',{-2051.795,63.1,1293.383},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{81.5,6.0,34.2},false},
  {'COL_DS_Terrain_115','Block',{-2055.712,63.1,1298.049},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{79.387,6.0,34.2},false},
  {'COL_DS_Terrain_116','Block',{-2045.073,63.1,1317.514},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{35.887,2.725,34.2},false},
  {'COL_DS_Terrain_117','Block',{-1997.576,63.1,1311.851},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{16.5,83.875,34.2},false},
  {'COL_DS_Terrain_131','Block',{-1942.67,63.1,1445.213},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{41.086,6.0,34.2},false},
  {'COL_DS_Terrain_132','Block',{-1950.37,63.1,1445.371},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{49.699,6.0,34.2},false},
  {'COL_DS_Terrain_133','Block',{-1955.356,63.1,1448.763},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{49.869,6.0,34.2},false},
  {'COL_DS_Terrain_134','Block',{-1960.343,63.1,1452.155},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{50.04,6.0,34.2},false},
  {'COL_DS_Terrain_135','Block',{-1965.425,63.1,1455.432},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{49.913,6.0,34.2},false},
  {'COL_DS_Terrain_136','Block',{-1970.958,63.1,1458.173},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{48.383,6.0,34.2},false},
  {'COL_DS_Terrain_137','Block',{-1976.491,63.1,1460.913},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{46.853,6.0,34.2},false},
  {'COL_DS_Terrain_138','Block',{-1982.024,63.1,1463.654},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{45.323,6.0,34.2},false},
  {'COL_DS_Terrain_139','Block',{-1987.557,63.1,1466.394},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{43.793,6.0,34.2},false},
  {'COL_DS_Terrain_140','Block',{-1993.389,63.1,1468.778},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{41.333,6.0,34.2},false},
  {'COL_DS_Terrain_141','Block',{-1999.146,63.1,1471.251},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{37.745,6.0,34.2},false},
  {'COL_DS_Terrain_142','Block',{-2003.019,63.1,1475.97},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{28.295,6.0,34.2},false},
  {'COL_DS_Terrain_143','Block',{-2006.258,63.1,1478.332},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{9.75,2.0,34.2},false},
  {'COL_DS_Terrain_144','Block',{-1860.301,58.1,1303.796},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{15.867,6.0,24.2},false},
  {'COL_DS_Terrain_145','Block',{-1875.553,58.1,1285.618},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{30.225,6.0,24.2},false},
  {'COL_DS_Terrain_146','Block',{-1881.27,58.1,1288.14},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.69,6.0,24.2},false},
  {'COL_DS_Terrain_147','Block',{-1888.18,58.1,1289.239},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{59.49,6.0,24.2},false},
  {'COL_DS_Terrain_148','Block',{-1895.09,58.1,1290.338},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{52.29,6.0,24.2},false},
  {'COL_DS_Terrain_149','Block',{-1902.001,58.1,1291.437},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{45.09,6.0,24.2},false},
  {'COL_DS_Terrain_150','Block',{-1907.822,58.1,1293.833},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{41.277,6.0,24.2},false},
  {'COL_DS_Terrain_151','Block',{-1913.12,58.1,1296.854},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{39.095,6.0,24.2},false},
  {'COL_DS_Terrain_152','Block',{-1918.417,58.1,1299.875},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{36.914,6.0,24.2},false},
  {'COL_DS_Terrain_153','Block',{-1923.715,58.1,1302.896},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{34.732,6.0,24.2},false},
  {'COL_DS_Terrain_154','Block',{-1929.012,58.1,1305.917},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{32.55,6.0,24.2},false},
  {'COL_DS_Terrain_155','Block',{-1934.31,58.1,1308.938},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{30.368,6.0,24.2},false},
  {'COL_DS_Terrain_157','Block',{-1936.579,58.1,1232.434},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{52.76,6.0,24.2},false},
  {'COL_DS_Terrain_158','Block',{-1942.718,58.1,1234.453},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{57.56,6.0,24.2},false},
  {'COL_DS_Terrain_159','Block',{-1948.857,58.1,1236.471},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{62.36,6.0,24.2},false},
  {'COL_DS_Terrain_160','Block',{-1955.012,58.1,1238.469},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{67.211,6.0,24.2},false},
  {'COL_DS_Terrain_161','Block',{-1961.344,58.1,1240.258},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{72.611,6.0,24.2},false},
  {'COL_DS_Terrain_162','Block',{-1967.092,58.1,1242.743},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{76.193,6.0,24.2},false},
  {'COL_DS_Terrain_163','Block',{-1972.028,58.1,1246.194},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{77.252,6.0,24.2},false},
  {'COL_DS_Terrain_164','Block',{-1979.263,58.1,1251.573},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{78.311,12.0,24.2},false},
  {'COL_DS_Terrain_167','Block',{-1941.164,58.1,1282.793},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{18.5,34.09,24.2},false},
  {'COL_DS_Terrain_173','Block',{-1709.955,56.1,1265.853},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{58.783,6.0,20.2},false},
  {'COL_DS_Terrain_174','Block',{-1714.097,56.1,1270.25},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{60.195,6.0,20.2},false},
  {'COL_DS_Terrain_175','Block',{-1718.24,56.1,1274.648},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{61.606,6.0,20.2},false},
  {'COL_DS_Terrain_176','Block',{-1722.382,56.1,1279.045},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{63.018,6.0,20.2},false},
  {'COL_DS_Terrain_177','Block',{-1726.525,56.1,1283.443},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{64.43,6.0,20.2},false},
  {'COL_DS_Terrain_178','Block',{-1730.693,56.1,1287.809},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{65.76,6.0,20.2},false},
  {'COL_DS_Terrain_179','Block',{-1735.239,56.1,1291.726},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{65.918,6.0,20.2},false},
  {'COL_DS_Terrain_180','Block',{-1739.784,56.1,1295.643},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.076,6.0,20.2},false},
  {'COL_DS_Terrain_181','Block',{-1744.33,56.1,1299.561},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.234,6.0,20.2},false},
  {'COL_DS_Terrain_182','Block',{-1748.875,56.1,1303.478},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.392,6.0,20.2},false},
  {'COL_DS_Terrain_183','Block',{-1753.421,56.1,1307.395},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.55,6.0,20.2},false},
  {'COL_DS_Terrain_184','Block',{-1762.563,56.1,1315.169},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.708,18.0,20.2},false},
  {'COL_DS_Terrain_187','Block',{-1771.826,56.1,1322.798},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.488,6.0,20.2},false},
  {'COL_DS_Terrain_188','Block',{-1776.47,56.1,1326.598},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.338,6.0,20.2},false},
  {'COL_DS_Terrain_189','Block',{-1781.115,56.1,1330.397},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.188,6.0,20.2},false},
  {'COL_DS_Terrain_190','Block',{-1785.759,56.1,1334.196},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{66.038,6.0,20.2},false},
  {'COL_DS_Terrain_191','Block',{-1790.404,56.1,1337.995},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{65.888,6.0,20.2},false},
  {'COL_DS_Terrain_192','Block',{-1795.076,56.1,1341.762},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{65.652,6.0,20.2},false},
  {'COL_DS_Terrain_193','Block',{-1800.058,56.1,1345.159},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{64.452,6.0,20.2},false},
  {'COL_DS_Terrain_194','Block',{-1805.04,56.1,1348.556},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{63.252,6.0,20.2},false},
  {'COL_DS_Terrain_195','Block',{-1810.022,56.1,1351.953},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{62.052,6.0,20.2},false},
  {'COL_DS_Terrain_196','Block',{-1815.004,56.1,1355.35},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{60.852,6.0,20.2},false},
  {'COL_DS_Terrain_197','Block',{-1819.986,56.1,1358.747},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{59.652,6.0,20.2},false},
  {'COL_DS_Terrain_198','Block',{-1816.505,56.1,1370.332},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{35.03,3.561,20.2},false},
  {'COL_DS_Terrain_199','Block',{-1739.185,56.1,1230.334},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{8.213,6.0,20.2},false},
  {'COL_DS_Terrain_200','Block',{-1745.227,56.1,1232.468},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.713,6.0,20.2},false},
  {'COL_DS_Terrain_201','Block',{-1751.27,56.1,1234.601},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{17.213,6.0,20.2},false},
  {'COL_DS_Terrain_202','Block',{-1802.515,56.1,1276.206},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{19.35,126.001,20.2},false},
  {'COL_DS_Terrain_223','Block',{-1851.409,56.1,1318.138},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{17.961,2.815,20.2},false},
  {'COL_DS_Terrain_224','Block',{-1765.794,56.1,1230.981},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.73,6.0,20.2},false},
  {'COL_DS_Terrain_225','Block',{-1770.622,56.1,1234.562},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.45,6.0,20.2},false},
  {'COL_DS_Terrain_226','Block',{-1775.45,56.1,1238.143},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.17,6.0,20.2},false},
  {'COL_DS_Terrain_227','Block',{-1780.277,56.1,1241.724},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.89,6.0,20.2},false},
  {'COL_DS_Terrain_228','Block',{-1785.105,56.1,1245.305},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.61,6.0,20.2},false},
  {'COL_DS_Terrain_229','Block',{-1788.225,56.1,1247.771},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.844,1.95,20.2},false},
  {'COL_DS_Terrain_230','Block',{-1799.95,56.1,1256.317},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{7.824,6.0,20.2},false},
  {'COL_DS_Terrain_231','Block',{-1806.995,56.1,1261.923},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{8.291,12.0,20.2},false},
  {'COL_DS_Terrain_233','Block',{-1813.711,56.1,1267.92},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{7.736,6.0,20.2},false},
  {'COL_DS_Terrain_234','Block',{-1818.132,56.1,1271.986},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{7.191,6.0,20.2},false},
  {'COL_DS_Terrain_235','Block',{-1822.553,56.1,1276.052},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.645,6.0,20.2},false},
  {'COL_DS_Terrain_236','Block',{-1826.974,56.1,1280.117},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{6.1,6.0,20.2},false},
  {'COL_DS_Terrain_237','Block',{-1831.395,56.1,1284.183},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.555,6.0,20.2},false},
  {'COL_DS_Terrain_238','Block',{-1835.816,56.1,1288.249},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.009,6.0,20.2},false},
  {'COL_DS_Terrain_239','Block',{-1840.237,56.1,1292.314},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{4.464,6.0,20.2},false},
  {'COL_DS_Terrain_240','Block',{-1844.434,56.1,1296.646},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.222,6.0,20.2},false},
  {'COL_DS_Terrain_241','Block',{-1848.602,56.1,1301.014},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.889,6.0,20.2},false},
  {'COL_DS_Terrain_242','Block',{-1851.448,56.1,1304.272},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.556,2.55,20.2},false},
  {'COL_DS_Terrain_243','Block',{-1788.639,56.1,1285.349},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.5,143.694,20.2},false},
  {'COL_DS_Terrain_267','Block',{-1638.62,53.1,1082.598},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{11.725,6.0,14.2},false},
  {'COL_DS_Terrain_268','Block',{-1642.253,53.1,1087.604},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{14.725,6.0,14.2},false},
  {'COL_DS_Terrain_269','Block',{-1646.005,53.1,1092.466},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{17.35,6.0,14.2},false},
  {'COL_DS_Terrain_270','Block',{-1650.008,53.1,1097.03},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{19.196,6.0,14.2},false},
  {'COL_DS_Terrain_271','Block',{-1654.011,53.1,1101.594},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{21.042,6.0,14.2},false},
  {'COL_DS_Terrain_272','Block',{-1658.014,53.1,1106.157},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{22.888,6.0,14.2},false},
  {'COL_DS_Terrain_273','Block',{-1662.017,53.1,1110.721},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{24.735,6.0,14.2},false},
  {'COL_DS_Terrain_274','Block',{-1660.553,53.1,1121.801},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{43.592,6.0,14.2},false},
  {'COL_DS_Terrain_275','Block',{-1658.644,53.1,1133.41},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{63.831,6.0,14.2},false},
  {'COL_DS_Terrain_276','Block',{-1658.478,53.1,1142.942},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{78.65,6.0,14.2},false},
  {'COL_DS_Terrain_277','Block',{-1659.217,53.1,1151.395},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{90.65,6.0,14.2},false},
  {'COL_DS_Terrain_278','Block',{-1660.8,53.1,1158.843},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{100.025,6.0,14.2},false},
  {'COL_DS_Terrain_279','Block',{-1664.136,53.1,1164.202},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{103.948,6.0,14.2},false},
  {'COL_DS_Terrain_280','Block',{-1667.471,53.1,1169.561},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{107.871,6.0,14.2},false},
  {'COL_DS_Terrain_281','Block',{-1670.807,53.1,1174.921},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{111.794,6.0,14.2},false},
  {'COL_DS_Terrain_282','Block',{-1674.142,53.1,1180.28},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{115.717,6.0,14.2},false},
  {'COL_DS_Terrain_283','Block',{-1678.303,53.1,1184.656},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{117.072,6.0,14.2},false},
  {'COL_DS_Terrain_284','Block',{-1682.471,53.1,1189.023},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{118.406,6.0,14.2},false},
  {'COL_DS_Terrain_285','Block',{-1686.638,53.1,1193.391},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{119.739,6.0,14.2},false},
  {'COL_DS_Terrain_286','Block',{-1690.806,53.1,1197.758},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{121.072,6.0,14.2},false},
  {'COL_DS_Terrain_287','Block',{-1694.974,53.1,1202.125},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{122.406,6.0,14.2},false},
  {'COL_DS_Terrain_288','Block',{-1699.141,53.1,1206.493},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{123.739,6.0,14.2},false},
  {'COL_DS_Terrain_289','Block',{-1703.501,53.1,1210.632},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{124.476,6.0,14.2},false},
  {'COL_DS_Terrain_290','Block',{-1707.862,53.1,1214.769},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{125.207,6.0,14.2},false},
  {'COL_DS_Terrain_291','Block',{-1712.223,53.1,1218.906},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{125.939,6.0,14.2},false},
  {'COL_DS_Terrain_292','Block',{-1716.584,53.1,1223.043},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{126.671,6.0,14.2},false},
  {'COL_DS_Terrain_293','Block',{-1720.945,53.1,1227.18},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{127.402,6.0,14.2},false},
  {'COL_DS_Terrain_294','Block',{-1725.307,53.1,1231.317},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{128.134,6.0,14.2},false},
  {'COL_DS_Terrain_295','Block',{-1729.783,53.1,1235.316},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{128.506,6.0,14.2},false},
  {'COL_DS_Terrain_296','Block',{-1758.027,53.1,1210.991},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{54.928,6.0,14.2},false},
  {'COL_DS_Terrain_297','Block',{-1764.132,53.1,1213.049},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{50.233,6.0,14.2},false},
  {'COL_DS_Terrain_298','Block',{-1770.238,53.1,1215.107},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{45.537,6.0,14.2},false},
  {'COL_DS_Terrain_299','Block',{-1776.343,53.1,1217.165},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{40.841,6.0,14.2},false},
  {'COL_DS_Terrain_300','Block',{-1782.012,53.1,1219.744},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{37.504,6.0,14.2},false},
  {'COL_DS_Terrain_301','Block',{-1786.84,53.1,1223.325},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{36.784,6.0,14.2},false},
  {'COL_DS_Terrain_302','Block',{-1791.667,53.1,1226.906},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{36.064,6.0,14.2},false},
  {'COL_DS_Terrain_303','Block',{-1796.495,53.1,1230.487},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{35.344,6.0,14.2},false},
  {'COL_DS_Terrain_304','Block',{-1801.323,53.1,1234.068},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{34.624,6.0,14.2},false},
  {'COL_DS_Terrain_305','Block',{-1806.15,53.1,1237.648},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{33.904,6.0,14.2},false},
  {'COL_DS_Terrain_306','Block',{-1810.978,53.1,1241.229},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{33.184,6.0,14.2},false},
  {'COL_DS_Terrain_307','Block',{-1815.806,53.1,1244.81},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{32.464,6.0,14.2},false},
  {'COL_DS_Terrain_308','Block',{-1820.458,53.1,1248.601},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{32.291,6.0,14.2},false},
  {'COL_DS_Terrain_309','Block',{-1824.879,53.1,1252.666},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{32.836,6.0,14.2},false},
  {'COL_DS_Terrain_310','Block',{-1829.3,53.1,1256.732},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{33.382,6.0,14.2},false},
  {'COL_DS_Terrain_311','Block',{-1833.721,53.1,1260.798},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{33.927,6.0,14.2},false},
  {'COL_DS_Terrain_312','Block',{-1838.141,53.1,1264.863},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{34.473,6.0,14.2},false},
  {'COL_DS_Terrain_313','Block',{-1842.562,53.1,1268.929},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{35.018,6.0,14.2},false},
  {'COL_DS_Terrain_314','Block',{-1846.983,53.1,1272.995},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{35.564,6.0,14.2},false},
  {'COL_DS_Terrain_315','Block',{-1851.097,53.1,1277.427},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{37.067,6.0,14.2},false},
  {'COL_DS_Terrain_316','Block',{-1855.05,53.1,1282.05},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{39.067,6.0,14.2},false},
  {'COL_DS_Terrain_317','Block',{-1859.004,53.1,1286.673},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{41.067,6.0,14.2},false},
  {'COL_DS_Terrain_318','Block',{-1863.461,53.1,1290.695},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{41.5,6.0,14.2},false},
  {'COL_DS_Terrain_319','Block',{-1868.341,53.1,1294.214},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{40.617,6.0,14.2},false},
  {'COL_DS_Terrain_320','Block',{-1656.248,53.1,1061.59},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{14.123,6.0,14.2},false},
  {'COL_DS_Terrain_321','Block',{-1661.29,53.1,1064.916},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{15.508,6.0,14.2},false},
  {'COL_DS_Terrain_322','Block',{-1666.331,53.1,1068.243},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{16.892,6.0,14.2},false},
  {'COL_DS_Terrain_323','Block',{-1671.372,53.1,1071.569},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{18.277,6.0,14.2},false},
  {'COL_DS_Terrain_324','Block',{-1676.099,53.1,1075.27},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{18.683,6.0,14.2},false},
  {'COL_DS_Terrain_325','Block',{-1680.63,53.1,1079.205},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{18.48,6.0,14.2},false},
  {'COL_DS_Terrain_326','Block',{-1685.098,53.1,1083.215},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{18.08,6.0,14.2},false},
  {'COL_DS_Terrain_327','Block',{-1689.565,53.1,1087.224},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{17.68,6.0,14.2},false},
  {'COL_DS_Terrain_328','Block',{-1694.033,53.1,1091.234},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{17.28,6.0,14.2},false},
  {'COL_DS_Terrain_329','Block',{-1698.501,53.1,1095.244},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{16.88,6.0,14.2},false},
  {'COL_DS_Terrain_330','Block',{-1702.621,53.1,1099.668},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{15.4,6.0,14.2},false},
  {'COL_DS_Terrain_331','Block',{-1706.575,53.1,1104.291},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{13.4,6.0,14.2},false},
  {'COL_DS_Terrain_332','Block',{-1719.841,53.1,1097.815},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{40.375,6.0,14.2},false},
  {'COL_DS_Terrain_333','Block',{-1732.207,53.1,1092.413},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{64.55,6.0,14.2},false},
  {'COL_DS_Terrain_334','Block',{-1742.159,53.1,1089.887},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{81.214,6.0,14.2},false},
  {'COL_DS_Terrain_335','Block',{-1750.887,53.1,1088.819},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{94.071,6.0,14.2},false},
  {'COL_DS_Terrain_336','Block',{-1758.795,53.1,1088.729},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{104.375,6.0,14.2},false},
  {'COL_DS_Terrain_337','Block',{-1764.998,53.1,1090.671},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{109.375,6.0,14.2},false},
  {'COL_DS_Terrain_338','Block',{-1771.201,53.1,1092.612},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{114.375,6.0,14.2},false},
  {'COL_DS_Terrain_339','Block',{-1777.405,53.1,1094.554},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{119.375,6.0,14.2},false},
  {'COL_DS_Terrain_340','Block',{-1783.27,53.1,1096.898},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{123.324,6.0,14.2},false},
  {'COL_DS_Terrain_341','Block',{-1788.433,53.1,1100.079},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{125.088,6.0,14.2},false},
  {'COL_DS_Terrain_342','Block',{-1793.597,53.1,1103.26},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{126.853,6.0,14.2},false},
  {'COL_DS_Terrain_343','Block',{-1798.76,53.1,1106.441},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{128.618,6.0,14.2},false},
  {'COL_DS_Terrain_344','Block',{-1803.924,53.1,1109.621},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{130.382,6.0,14.2},false},
  {'COL_DS_Terrain_345','Block',{-1809.087,53.1,1112.802},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{132.147,6.0,14.2},false},
  {'COL_DS_Terrain_346','Block',{-1814.195,53.1,1116.05},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{133.738,6.0,14.2},false},
  {'COL_DS_Terrain_347','Block',{-1819.273,53.1,1119.332},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{135.238,6.0,14.2},false},
  {'COL_DS_Terrain_348','Block',{-1824.351,53.1,1122.614},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{136.738,6.0,14.2},false},
  {'COL_DS_Terrain_349','Block',{-1829.43,53.1,1125.896},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{138.238,6.0,14.2},false},
  {'COL_DS_Terrain_350','Block',{-1834.883,53.1,1128.731},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{140.905,6.0,14.2},false},
  {'COL_DS_Terrain_351','Block',{-1840.531,53.1,1131.335},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{144.177,6.0,14.2},false},
  {'COL_DS_Terrain_352','Block',{-1846.179,53.1,1133.938},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{147.45,6.0,14.2},false},
  {'COL_DS_Terrain_353','Block',{-1851.827,53.1,1136.541},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{150.723,6.0,14.2},false},
  {'COL_DS_Terrain_354','Block',{-1856.842,53.1,1139.899},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{152.025,6.0,14.2},false},
  {'COL_DS_Terrain_355','Block',{-1861.852,53.1,1143.263},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{153.311,6.0,14.2},false},
  {'COL_DS_Terrain_356','Block',{-1887.272,53.1,1164.307},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{153.75,60.001,14.2},false},
  {'COL_DS_Terrain_366','Block',{-1911.959,53.1,1186.226},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{151.905,6.0,14.2},false},
  {'COL_DS_Terrain_367','Block',{-1914.82,53.1,1192.151},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{146.505,6.0,14.2},false},
  {'COL_DS_Terrain_368','Block',{-1918.656,53.1,1196.912},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{144.143,6.0,14.2},false},
  {'COL_DS_Terrain_369','Block',{-1922.964,53.1,1201.114},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{143.242,6.0,14.2},false},
  {'COL_DS_Terrain_370','Block',{-1927.271,53.1,1205.315},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{142.342,6.0,14.2},false},
  {'COL_DS_Terrain_371','Block',{-1931.578,53.1,1209.517},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{141.443,6.0,14.2},false},
  {'COL_DS_Terrain_372','Block',{-1935.885,53.1,1213.718},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{140.542,6.0,14.2},false},
  {'COL_DS_Terrain_373','Block',{-1940.192,53.1,1217.92},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{139.643,6.0,14.2},false},
  {'COL_DS_Terrain_374','Block',{-1950.846,53.1,1214.556},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{118.993,6.0,14.2},false},
  {'COL_DS_Terrain_375','Block',{-1975.305,53.1,1194.742},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{55.513,6.0,14.2},false},
  {'COL_DS_Terrain_376','Block',{-1981.174,53.1,1197.082},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{49.873,6.0,14.2},false},
  {'COL_DS_Terrain_377','Block',{-1987.043,53.1,1199.422},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{44.233,6.0,14.2},false},
  {'COL_DS_Terrain_378','Block',{-1992.913,53.1,1201.76},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{38.588,6.0,14.2},false},
  {'COL_DS_Terrain_379','Block',{-1998.975,53.1,1203.87},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{32.348,6.0,14.2},false},
  {'COL_DS_Terrain_380','Block',{-2004.65,53.1,1206.442},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{27.312,6.0,14.2},false},
  {'COL_DS_Terrain_381','Block',{-2009.579,53.1,1209.902},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{24.597,6.0,14.2},false},
  {'COL_DS_Terrain_382','Block',{-2012.976,53.1,1212.077},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{21.882,2.0,14.2},false},
  {'COL_DS_Terrain_383','Block',{-1766.858,53.1,1173.084},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{14.5,318.001,14.2},false},
  {'COL_DS_Terrain_437','Ramp',{-1628.965,51.2,1007.762},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,6.932,6.0},false},
  {'COL_DS_Terrain_438','Ramp',{-1633.887,51.2,1006.563},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,13.768,6.0},false},
  {'COL_DS_Terrain_439','Ramp',{-1637.765,51.2,1006.609},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,16.11,6.0},false},
  {'COL_DS_Terrain_440','Ramp',{-1641.621,51.2,1006.681},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,18.387,6.0},false},
  {'COL_DS_Terrain_441','Ramp',{-1645.477,51.2,1006.752},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,20.664,6.0},false},
  {'COL_DS_Terrain_442','Ramp',{-1649.062,51.2,1007.147},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,23.786,6.0},false},
  {'COL_DS_Terrain_443','Ramp',{-1652.409,51.2,1007.826},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,27.648,6.0},false},
  {'COL_DS_Terrain_444','Ramp',{-1655.325,51.2,1009.018},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,30.17,6.0},false},
  {'COL_DS_Terrain_445','Ramp',{-1658.008,51.2,1010.487},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,31.97,6.0},false},
  {'COL_DS_Terrain_446','Ramp',{-1660.78,51.261,1012.029},{-0.765,0.038,0.642},{0.643,0.0,0.766},{3.102,33.77,6.0},false},
  {'COL_DS_Terrain_447','Ramp',{-1663.508,51.407,1013.535},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,35.57,6.0},false},
  {'COL_DS_Terrain_448','Ramp',{-1664.845,51.58,1016.61},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,41.562,6.0},false},
  {'COL_DS_Terrain_449','Ramp',{-1665.456,51.753,1020.549},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,49.812,6.0},false},
  {'COL_DS_Terrain_450','Ramp',{-1666.066,51.926,1024.489},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,58.063,6.0},false},
  {'COL_DS_Terrain_451','Ramp',{-1668.81,52.099,1025.885},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,59.675,6.0},false},
  {'COL_DS_Terrain_452','Ramp',{-1671.591,52.272,1027.239},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,61.175,6.0},false},
  {'COL_DS_Terrain_453','Ramp',{-1674.002,52.445,1029.032},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,61.528,6.0},false},
  {'COL_DS_Terrain_454','Ramp',{-1676.407,52.618,1030.833},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,61.861,6.0},false},
  {'COL_DS_Terrain_455','Ramp',{-1678.816,52.792,1032.629},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,62.183,6.0},false},
  {'COL_DS_Terrain_456','Ramp',{-1681.444,52.965,1034.165},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,61.824,6.0},false},
  {'COL_DS_Terrain_457','Ramp',{-1684.072,53.138,1035.7},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,61.465,6.0},false},
  {'COL_DS_Terrain_458','Ramp',{-1686.7,53.311,1037.236},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,61.106,6.0},false},
  {'COL_DS_Terrain_459','Ramp',{-1689.327,53.484,1038.771},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,60.747,6.0},false},
  {'COL_DS_Terrain_460','Ramp',{-1691.955,53.657,1040.307},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,60.388,6.0},false},
  {'COL_DS_Terrain_461','Ramp',{-1694.583,53.83,1041.843},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,60.029,6.0},false},
  {'COL_DS_Terrain_462','Ramp',{-1697.211,54.003,1043.378},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,59.67,6.0},false},
  {'COL_DS_Terrain_463','Ramp',{-1699.839,54.176,1044.914},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,59.311,6.0},false},
  {'COL_DS_Terrain_464','Ramp',{-1702.304,54.349,1046.643},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,59.458,6.0},false},
  {'COL_DS_Terrain_465','Ramp',{-1704.878,54.522,1048.242},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,60.717,6.0},false},
  {'COL_DS_Terrain_466','Ramp',{-1707.456,54.695,1049.837},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,61.988,6.0},false},
  {'COL_DS_Terrain_467','Ramp',{-1710.034,54.868,1051.431},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,63.26,6.0},false},
  {'COL_DS_Terrain_468','Ramp',{-1712.613,55.042,1053.026},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,64.531,6.0},false},
  {'COL_DS_Terrain_469','Ramp',{-1715.191,55.215,1054.62},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,65.803,6.0},false},
  {'COL_DS_Terrain_470','Ramp',{-1717.769,55.388,1056.215},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,67.074,6.0},false},
  {'COL_DS_Terrain_471','Ramp',{-1720.347,55.561,1057.81},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,68.345,6.0},false},
  {'COL_DS_Terrain_472','Ramp',{-1722.925,55.734,1059.404},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,69.617,6.0},false},
  {'COL_DS_Terrain_473','Ramp',{-1725.422,55.907,1061.096},{-0.765,0.058,0.642},{0.643,0.0,0.766},{3.105,71.142,6.0},false},
  {'COL_DS_Terrain_474','Ramp',{-1728.397,56.08,1062.218},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,75.247,6.0},false},
  {'COL_DS_Terrain_475','Ramp',{-1731.724,56.253,1062.921},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,80.447,6.0},false},
  {'COL_DS_Terrain_476','Ramp',{-1735.05,56.426,1063.623},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,85.647,6.0},false},
  {'COL_DS_Terrain_477','Ramp',{-1738.377,56.599,1064.326},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,90.847,6.0},false},
  {'COL_DS_Terrain_478','Ramp',{-1741.703,56.772,1065.029},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,96.047,6.0},false},
  {'COL_DS_Terrain_479','Ramp',{-1745.422,56.945,1065.264},{-0.765,0.058,0.642},{0.643,-0.0,0.766},{3.105,101.5,6.0},false},
  {'COL_DS_Terrain_480','Ramp',{-1751.91,57.117,1062.195},{-0.765,0.057,0.642},{0.643,0.0,0.766},{3.105,99.125,6.0},false},
  {'COL_DS_Terrain_481','Ramp',{-1762.969,57.199,1053.422},{-0.766,0.001,0.643},{0.643,0.0,0.766},{3.1,82.133,6.0},false},
  {'COL_DS_Terrain_482','Ramp',{-1769.525,57.2,1050.272},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,71.389,6.0},false},
  {'COL_DS_Terrain_483','Ramp',{-1775.071,57.2,1048.33},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,57.494,6.0},false},
  {'COL_DS_Terrain_484','Ramp',{-1779.421,57.2,1047.813},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,43.778,6.0},false},
  {'COL_DS_Terrain_485','Ramp',{-1782.606,57.2,1048.683},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,33.683,6.0},false},
  {'COL_DS_Terrain_486','Ramp',{-1785.792,57.2,1049.554},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,23.587,6.0},false},
  {'COL_DS_Terrain_487','Ramp',{-1788.978,57.2,1050.424},{-0.766,0.0,0.643},{0.643,0.0,0.766},{3.1,13.492,6.0},false},
  {'COL_DS_Terrain_488','Ramp',{-1791.398,57.2,1050.652},{-0.766,0.0,0.643},{0.643,0.0,0.766},{1.1,3.397,6.0},false},
  {'COL_DS_Terrain_489','Block',{-1613.833,50.1,1028.129},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{47.74,6.0,8.2},false},
  {'COL_DS_Terrain_490','Block',{-1618.87,50.1,1031.461},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{51.511,6.0,8.2},false},
  {'COL_DS_Terrain_491','Block',{-1623.331,50.1,1035.479},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{53.49,6.0,8.2},false},
  {'COL_DS_Terrain_492','Block',{-1627.814,50.1,1039.47},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{53.231,6.0,8.2},false},
  {'COL_DS_Terrain_493','Block',{-1632.574,50.1,1043.132},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{51.522,6.0,8.2},false},
  {'COL_DS_Terrain_494','Block',{-1637.679,50.1,1046.383},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{48.74,6.0,8.2},false},
  {'COL_DS_Terrain_495','Block',{-1641.367,50.1,1051.322},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{41.551,6.0,8.2},false},
  {'COL_DS_Terrain_496','Block',{-1644.904,50.1,1070.753},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{14.5,0.4,8.2},false},
  {'COL_DS_Terrain_497','Block',{-1731.954,53.1,1237.786},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{12.5,4.299,14.2},false},
  {'COL_DS_Terrain_498','Block',{-1793.401,53.1,1251.287},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{7.11,10.5,14.2},false},
  {'COL_DS_Terrain_499','Block',{-1937.57,53.1,1104.364},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.75,14.5,14.2},false},
  {'COL_DS_Terrain_500','Block',{-1918.91,53.1,1264.12},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{18.5,24.011,14.2},false},
  {'COL_DS_Terrain_501','Block',{-1963.62,58.1,1283.36},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{16.5,4.777,24.2},false},
  {'COL_DS_VegBamboo_001','Block',{-1674.372,59.327,1020.421},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_002','Block',{-1677.284,59.316,1016.633},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_003','Block',{-1680.117,59.603,1021.013},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_004','Block',{-1687.417,60.901,1047.301},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_005','Block',{-1684.671,60.631,1043.303},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_006','Block',{-1684.324,60.908,1051.197},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_007','Block',{-1693.027,61.136,1046.955},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_008','Block',{-1711.4,61.461,1033.818},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_009','Block',{-1712.594,61.303,1028.152},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_010','Block',{-1716.053,61.784,1036.985},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_011','Block',{-1721.035,62.854,1059.911},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_012','Block',{-1723.925,63.134,1064.02},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_013','Block',{-1715.905,62.724,1062.512},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_014','Block',{-1747.949,63.577,1047.332},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_015','Block',{-1742.177,63.27,1045.932},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_016','Block',{-1746.738,63.329,1042.085},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_017','Block',{-1680.394,60.918,1056.149},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_018','Block',{-1678.974,60.665,1051.002},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_019','Block',{-1681.915,61.19,1061.655},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_020','Block',{-1701.597,62.418,1071.33},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_021','Block',{-1696.799,62.103,1068.531},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_022','Block',{-1706.74,62.571,1069.307},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_023','Block',{-1717.165,63.688,1087.003},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_024','Block',{-1711.524,63.456,1087.492},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_025','Block',{-1716.177,63.455,1081.91},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_026','Block',{-1721.826,63.836,1085.452},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_027','Block',{-1782.623,64.38,1040.107},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_028','Block',{-1779.389,64.38,1036.292},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegBamboo_029','Block',{-1778.273,64.38,1043.16},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegPergola_001','Block',{-1732.151,64.156,1046.595},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,10.609},false},
  {'COL_DS_VegPergola_002','Block',{-1737.02,64.297,1048.421},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,10.326},false},
  {'COL_DS_VegPergola_003','Block',{-1728.218,64.263,1057.081},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,10.394},false},
  {'COL_DS_VegPergola_004','Block',{-1733.086,64.405,1058.907},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,10.111},false},
  {'COL_DS_VegTrunk_001','Block',{-1704.396,64.38,1152.003},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.34,3.34,8.0},false},
  {'COL_DS_VegTrunk_002','Block',{-1810.5,62.922,1050.445},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.43,3.43,8.0},false},
  {'COL_DS_VegTrunk_003','Block',{-1954.859,64.38,1164.658},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.457,2.457,8.0},false},
  {'COL_DS_VegTrunk_004','Block',{-1645.938,64.38,1173.443},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.8,2.8,8.0},false},
  {'COL_DS_VegTrunk_005','Block',{-1667.995,64.38,1238.945},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.16,3.16,8.0},false},
  {'COL_DS_VegTrunk_006','Block',{-1750.375,70.38,1336.789},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.16,3.16,8.0},false},
  {'COL_DS_VegTrunk_007','Block',{-1727.244,70.38,1323.907},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.62,2.62,8.0},false},
  {'COL_DS_VegTrunk_008','Block',{-1853.408,62.899,1045.981},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.71,2.71,8.0},false},
  {'COL_DS_VegTrunk_009','Block',{-1934.97,72.909,1045.234},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.98,2.98,8.0},false},
  {'COL_DS_VegTrunk_010','Block',{-1984.17,88.0,1412.869},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.52,3.52,8.0},false},
  {'COL_DS_VegTrunk_011','Block',{-2039.889,109.505,1368.245},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.7,3.7,8.0},false},
  {'COL_DS_VegTrunk_012','Block',{-2065.161,88.0,1316.347},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.16,3.16,8.0},false},
  {'COL_DS_VegTrunk_013','Block',{-1615.562,67.147,1069.629},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,7.0},false},
  {'COL_DS_VegTrunk_014','Block',{-1865.512,63.88,1289.806},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,7.0},false},
  {'COL_DS_VegTrunk_015','Block',{-1775.381,69.785,1362.994},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.0,2.0,7.0},false},
  {'COL_DS_VegTrunk_016','Block',{-1706.49,69.88,1289.522},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_017','Block',{-1713.482,69.88,1304.527},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_018','Block',{-1728.732,69.88,1300.353},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_019','Block',{-1680.198,63.88,1264.85},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_020','Block',{-1642.442,63.7,1222.726},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_021','Block',{-1960.29,83.88,1431.993},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_022','Block',{-1889.109,83.88,1429.703},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_023','Block',{-1907.247,83.88,1442.312},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_024','Block',{-1976.896,83.88,1443.317},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_025','Block',{-1994.788,83.88,1453.109},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_026','Block',{-1730.32,62.226,1058.88},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.6,1.6,6.0},false},
  {'COL_DS_VegTrunk_027','Block',{-1813.86,69.2,1335.494},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.6,1.6,6.0},false},
  {'COL_DS_VegTrunk_028','Block',{-1717.667,63.7,1186.332},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.34,2.34,7.0},false},
  {'COL_DS_VegTrunk_029','Block',{-1761.442,69.7,1236.118},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.34,2.34,7.0},false},
  {'COL_DS_VegTrunk_030','Block',{-1777.831,69.88,1244.951},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,7.0},false},
  {'COL_DS_VegTrunk_031','Block',{-1812.822,69.7,1271.702},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.42,2.42,7.0},false},
  {'COL_DS_VegTrunk_032','Block',{-1836.191,69.807,1327.862},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.26,2.26,7.0},false},
  {'COL_DS_VegTrunk_033','Block',{-1726.392,63.7,1160.016},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.884,1.884,7.0},false},
  {'COL_DS_VegTrunk_034','Block',{-1777.69,63.7,1210.893},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.825,1.825,7.0},false},
  {'COL_DS_VegTrunk_035','Block',{-1832.92,63.88,1253.973},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.1,2.1,7.0},false},
  {'COL_DS_VegTrunk_036','Block',{-1852.269,63.88,1268.251},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.34,2.34,7.0},false},
  {'COL_DS_VegTrunk_037','Block',{-1776.935,63.88,1056.221},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.42,2.42,7.0},false},
  {'COL_DS_VegTrunk_038','Block',{-1917.434,63.88,1100.359},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.18,2.18,7.0},false},
  {'COL_DS_VegTrunk_039','Block',{-1945.183,63.88,1129.517},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.02,2.02,7.0},false},
  {'COL_DS_VegTrunk_040','Block',{-1742.047,63.88,1091.215},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.1,2.1,7.0},false},
  {'COL_DS_VegTrunk_041','Block',{-1751.743,63.88,1084.688},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.02,2.02,7.0},false},
  {'COL_DS_VegTrunk_042','Block',{-1912.832,63.88,1230.301},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.26,2.26,7.0},false},
  {'COL_DS_VegTrunk_043','Block',{-1925.195,63.7,1209.345},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.34,2.34,7.0},false},
  {'COL_DS_VegTrunk_044','Block',{-1948.036,63.88,1194.57},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.94,1.94,7.0},false},
  {'COL_DS_VegTrunk_045','Block',{-1895.96,73.88,1297.079},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.26,2.26,7.0},false},
  {'COL_DS_VegTrunk_046','Block',{-1920.543,83.88,1448.247},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.94,1.94,7.0},false},
  {'COL_DS_VegTrunk_047','Block',{-1955.041,83.88,1469.362},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.94,1.94,7.0},false},
  {'COL_DS_VegTrunk_048','Block',{-1917.638,83.7,1398.815},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.26,2.26,7.0},false},
  {'COL_DS_VilFence_001','Block',{-1689.984,61.5,1178.918},{-0.444,0.0,0.896},{0.896,0.0,0.444},{9.299,0.7,2.8},false},
  {'COL_DS_VilFence_006','Block',{-1694.649,61.5,1188.33},{-0.444,0.0,0.896},{0.896,0.0,0.444},{2.311,0.7,2.8},false},
  {'COL_DS_VilFence_007','Block',{-1695.546,61.5,1190.132},{-0.447,0.0,0.894},{0.894,0.0,0.447},{2.315,0.7,2.8},false},
  {'COL_DS_VilFence_008','Block',{-1697.353,61.5,1193.718},{-0.451,0.0,0.893},{0.893,0.0,0.451},{6.315,0.7,2.8},false},
  {'COL_DS_VilGarden_001','Block',{-1823.113,68.4,1314.277},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.2,7.6,4.4},false},
  {'COL_DS_VilGarden_002','Block',{-1829.586,67.8,1319.709},{-0.766,0.0,0.643},{0.643,0.0,0.766},{8.9,0.7,3.4},false},
  {'COL_DS_VilGarden_003','Block',{-1808.941,68.4,1302.386},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.2,7.6,4.4},false},
  {'COL_DS_VilGarden_004','Block',{-1802.468,67.8,1296.954},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{8.9,0.7,3.4},false},
  {'COL_DS_VilGarden_005','Block',{-1812.35,71.0,1305.246},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,9.6},false},
  {'COL_DS_VilGarden_006','Block',{-1819.704,71.0,1311.417},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{1.4,1.4,9.6},false},
  {'COL_DS_VilGarden_007','Block',{-1786.125,67.8,1309.741},{0.643,0.0,0.766},{0.766,0.0,-0.643},{39.7,0.7,3.4},false},
  {'COL_DS_VilGarden_008','Block',{-1819.831,67.8,1338.024},{0.643,0.0,0.766},{0.766,0.0,-0.643},{39.7,0.7,3.4},false},
  {'COL_DS_VilGarden_009','Block',{-1812.256,68.2,1325.271},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.0,3.0,4.0},false},
  {'COL_DS_VilGarden_010','Block',{-1809.13,70.2,1333.352},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.8,0.8,8.0},false},
  {'COL_DS_VilGarden_011','Block',{-1814.033,70.2,1337.466},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.8,0.8,8.0},false},
  {'COL_DS_VilGarden_012','Block',{-1813.758,70.2,1327.837},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.8,0.8,8.0},false},
  {'COL_DS_VilGarden_013','Block',{-1818.661,70.2,1331.951},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.8,0.8,8.0},false},
  {'COL_DS_VilHokora_001','Block',{-1738.754,62.5,1195.844},{0.866,0.0,-0.5},{-0.5,0.0,-0.866},{4.8,4.4,4.6},false},
  {'COL_DS_VilHouseV1_001','Block',{-1667.818,60.73,1159.036},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{15.2,11.2,2.26},true},
  {'COL_DS_VilHouseV1_003','Block',{-1673.339,66.93,1159.076},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{0.8,1.0,10.14},true},
  {'COL_DS_VilHouseV1_004','Block',{-1669.668,66.93,1153.834},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{0.8,1.0,10.14},true},
  {'COL_DS_VilHouseV1_006','Block',{-1664.132,66.93,1161.617},{-0.574,0.0,0.819},{0.819,0.0,0.574},{14.0,1.0,10.14},true},
  {'COL_DS_VilHouseV1_007','Block',{-1667.776,66.93,1151.131},{0.819,0.0,0.574},{0.574,0.0,-0.819},{1.0,1.0,10.14},true},
  {'COL_DS_VilHouseV1_008','Block',{-1661.55,66.93,1155.49},{0.819,0.0,0.574},{0.574,0.0,-0.819},{3.8,1.0,10.14},true},
  {'COL_DS_VilHouseV1_009','Block',{-1669.662,66.93,1165.68},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{5.4,1.0,10.14},true},
  {'COL_DS_VilHouseV1_010','Block',{-1675.232,66.93,1161.78},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{1.0,1.0,10.14},true},
  {'COL_DS_VilHouseV1_011','Block',{-1672.978,60.675,1155.423},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{14.0,2.6,1.75},true},
  {'COL_DS_VilHouseV1_012','Ramp',{-1675.609,60.394,1153.58},{0.787,0.276,0.551},{0.574,0.0,-0.819},{4.89,5.6,1.0},false},
  {'COL_DS_VilHouseV1_013','Block',{-1664.832,63.33,1160.089},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{6.1,2.1,2.94},true},
  {'COL_DS_VilHouseV1_014','Block',{-1669.531,62.73,1163.574},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{2.0,5.0,1.74},false},
  {'COL_DS_VilHouseV1_015','Block',{-1663.336,62.73,1155.948},{0.574,0.0,-0.819},{-0.819,0.0,-0.574},{2.0,3.8,1.74},false},
  {'COL_DS_VilHouseV1_016','Ramp',{-1663.721,60.555,1150.744},{-0.544,0.315,0.777},{0.819,0.0,0.574},{5.268,5.2,1.0},false},
  {'COL_DS_VilHouseV2_001','Block',{-1676.853,61.0,1194.162},{0.5,0.0,-0.866},{-0.866,0.0,-0.5},{19.2,23.2,1.6},true},
  {'COL_DS_VilHouseV2_002','Block',{-1676.853,68.05,1194.162},{0.5,0.0,-0.866},{-0.866,0.0,-0.5},{18.0,22.0,12.5},true},
  {'COL_DS_VilHouseV2_003','Block',{-1671.603,60.975,1185.069},{0.866,0.0,0.5},{0.5,0.0,-0.866},{22.0,3.0,2.35},true},
  {'COL_DS_VilHouseV2_004','Ramp',{-1688.488,60.874,1187.445},{0.781,0.432,0.451},{0.5,-0.0,-0.866},{5.211,6.0,1.0},false},
  {'COL_DS_VilHouseV3_001','Block',{-1700.944,60.8,1226.125},{0.454,0.0,-0.891},{-0.891,0.0,-0.454},{19.2,15.2,1.2},true},
  {'COL_DS_VilHouseV3_002','Block',{-1700.944,68.15,1226.125},{0.454,0.0,-0.891},{-0.891,0.0,-0.454},{18.0,14.0,13.5},true},
  {'COL_DS_VilHouseV4_001','Block',{-1736.648,67.4,1269.139},{0.643,0.0,0.766},{0.766,0.0,-0.643},{15.2,13.2,2.4},true},
  {'COL_DS_VilHouseV4_002','Block',{-1736.648,78.1,1269.139},{0.643,0.0,0.766},{0.766,0.0,-0.643},{14.0,12.0,19.0},true},
  {'COL_DS_VilHouseV5_001','Block',{-1764.622,67.1,1288.695},{0.829,0.0,-0.559},{-0.559,0.0,-0.829},{23.2,17.2,1.8},true},
  {'COL_DS_VilHouseV5_002','Block',{-1764.622,78.7,1288.695},{0.829,0.0,-0.559},{-0.559,0.0,-0.829},{22.0,16.0,21.4},true},
  {'COL_DS_VilHouseV5_003','Ramp',{-1770.448,66.982,1280.058},{0.496,0.462,0.735},{0.829,-0.0,-0.559},{5.3,6.0,1.0},false},
  {'COL_DS_VilHouseV6_001','Block',{-1790.315,67.23,1338.973},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{31.2,21.2,3.26},true},
  {'COL_DS_VilHouseV6_002','Block',{-1796.422,81.15,1331.696},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{8.6,1.0,2.1},true},
  {'COL_DS_VilHouseV6_003','Block',{-1803.814,75.53,1337.899},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{10.7,1.0,13.34},true},
  {'COL_DS_VilHouseV6_004','Block',{-1789.029,75.53,1325.493},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{10.7,1.0,13.34},true},
  {'COL_DS_VilHouseV6_005','Block',{-1784.209,75.53,1346.251},{-0.766,0.0,0.643},{0.643,0.0,0.766},{30.0,1.0,13.34},true},
  {'COL_DS_VilHouseV6_006','Block',{-1779.208,75.53,1329.653},{0.643,0.0,0.766},{0.766,0.0,-0.643},{20.0,1.0,13.34},true},
  {'COL_DS_VilHouseV6_007','Block',{-1801.423,75.53,1348.294},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{20.0,1.0,13.34},true},
  {'COL_DS_VilHouseV6_008','Block',{-1796.546,67.175,1329.059},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{33.2,3.2,2.75},true},
  {'COL_DS_VilHouseV6_009','Block',{-1777.599,67.175,1328.303},{0.643,0.0,0.766},{0.766,0.0,-0.643},{20.0,3.2,2.75},true},
  {'COL_DS_VilHouseV6_010','Ramp',{-1799.974,66.928,1327.463},{0.575,0.447,0.685},{0.766,-0.0,-0.643},{5.255,6.0,1.0},false},
  {'COL_DS_VilHouseV6_011','Block',{-1797.742,70.06,1338.678},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{4.0,4.0,2.4},false},
  {'COL_DS_VilHouseV6_012','Block',{-1804.101,74.43,1344.014},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{0.9,0.9,11.14},true},
  {'COL_DS_VilHouseV6_013','Block',{-1782.958,74.43,1326.273},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{0.9,0.9,11.14},true},
  {'COL_DS_VilHouseV6_014','Block',{-1797.378,75.03,1344.247},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{10.6,0.8,12.34},true},
  {'COL_DS_VilHouseV6_015','Block',{-1783.896,75.03,1332.934},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{10.6,0.8,12.34},true},
  {'COL_DS_VilHouseV6_016','Block',{-1787.455,69.04,1342.382},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{28.2,9.3,0.36},true},
  {'COL_DS_VilHouseV6_017','Block',{-1783.684,69.47,1343.298},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{12.0,3.05,0.5},true},
  {'COL_DS_VilHouseV6_018','Block',{-1784.96,70.66,1324.82},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{1.8,3.3,3.6},false},
  {'COL_DS_VilHouseV6_019','Block',{-1805.273,72.51,1341.995},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{1.4,3.2,7.3},true},
  {'COL_DS_VilLamp_001','Block',{-1670.414,65.4,1132.115},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,10.4},false},
  {'COL_DS_VilLamp_002','Block',{-1680.652,65.4,1128.675},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,10.4},false},
  {'COL_DS_VilLamp_003','Block',{-1701.397,64.5,1168.023},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_VilLamp_004','Block',{-1716.599,64.5,1234.693},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_VilLamp_005','Block',{-1782.092,70.5,1253.096},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_VilLamp_006','Block',{-1731.859,70.5,1246.844},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_VilLamp_007','Block',{-1824.924,70.5,1308.618},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_VilLamp_008','Block',{-1809.727,70.5,1297.171},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.9,0.9,8.6},false},
  {'COL_DS_VilMarker_001','Block',{-1666.115,63.35,1132.504},{0.318,0.0,-0.948},{-0.948,0.0,-0.318},{1.6,1.4,6.3},false},
  {'COL_DS_VilWell_001','Block',{-1736.174,61.5,1182.584},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{5.4,5.4,2.6},false},
  {'COL_DS_VilWell_002','Block',{-1733.798,64.0,1184.247},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.7,0.7,7.6},false},
  {'COL_DS_VilWell_003','Block',{-1738.549,64.0,1180.92},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{0.7,0.7,7.6},false},
  {'COL_DS_WaterStone_001','Block',{-1967.212,61.075,1195.519},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{3.68,2.99,2.55},false},
  {'COL_DS_WaterStone_002','Block',{-1981.221,60.75,1176.335},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.56,2.08,1.9},false},
  {'COL_DS_WaterTsukubai_001','Block',{-1908.595,60.66,1124.271},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{2.2,2.0,1.22},false},
  {'COL_GateOnePiece_001','Block',{-2035.63,85.8,1542.922},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.5,4.5,11.2},false},
  {'COL_GateOnePiece_002','Block',{-2039.071,84.65,1547.837},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.9,2.9,10.1},false},
  {'COL_GateOnePiece_003','Block',{-2052.504,85.8,1531.106},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.5,4.5,11.2},false},
  {'COL_GateOnePiece_004','Block',{-2055.946,84.65,1536.021},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.9,2.9,10.1},false},
  {'COL_GateOnePiece_005','Block',{-2034.844,85.3,1549.82},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.6,1.9,11.4},false},
  {'COL_GateOnePiece_006','Block',{-2044.067,79.975,1537.014},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{22.0,10.0,0.75},false},
  {'COL_GateOnePiece_007','Block',{-2030.096,80.2,1542.341},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.0,13.1,1.2},false},
  {'COL_GateOnePiece_008','Block',{-2029.002,81.05,1541.825},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{5.2,5.2,0.5},false},
  {'COL_GateOnePiece_009','Block',{-2029.002,84.85,1541.825},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.0,4.0,8.1},false},
  {'COL_GateOnePiece_010','Block',{-2029.034,84.05,1537.164},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,6.5},false},
  {'COL_GateOnePiece_011','Block',{-2053.851,80.2,1525.707},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{7.0,13.1,1.2},false},
  {'COL_GateOnePiece_012','Block',{-2053.74,81.05,1524.503},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{5.2,5.2,0.5},false},
  {'COL_GateOnePiece_013','Block',{-2053.74,84.85,1524.503},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{4.0,4.0,8.1},false},
  {'COL_GateOnePiece_014','Block',{-2049.349,84.05,1522.939},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{2.0,2.0,6.5},false},
  {'COL_GateOnePieceLock_001','GateLock',{-2044.067,89.2,1537.014},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{16.6,1.4,18.0},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'AUDIO_Bamboo',{-1704.521,61.2,1039.842},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='wind',['range']=50.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Cascade',{-2010.924,66.2,1210.788},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='water',['range']=50.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Clearing',{-1835.365,68.2,1156.161},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='wind',['range']=120.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Forge',{-1969.607,84.2,1327.546},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='fire',['range']=40.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Pond',{-1984.912,61.2,1194.183},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='water',['range']=30.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Summon',{-1959.184,76.2,1078.606},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='energy',['range']=36.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Village',{-1730.67,70.2,1257.595},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='wind',['range']=60.0,['volume']='baixo',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'AUDIO_Waterwheel',{-2044.064,91.2,1269.926},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['family']='water',['range']=30.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'FX_Fall_1_Base',{-2010.771,60.32,1210.66},{0.643,0.0,0.766},{0.766,0.0,-0.643},{['fx']='nevoa_base',['width']=6.5,['level']=60.32,['note']='pe da cascata na lagoa, entre as pedras grandes N1/N2',['cor']='214,228,248',['tam']=10.4,['vida']=2.6,['vel']=2.5,['transp']=0.55,['infl']=0.9,['luz']=0.1,['tex']='nevoa',['rate']=14.0,['Dist']=260.0,['vfx']='emissor',['fwd_x']=0.766,['fwd_z']=-0.6428}},
  {'FX_Fall_1_Lip',{-2012.686,80.36,1212.266},{0.643,0.0,0.766},{0.766,0.0,-0.643},{['fx']='nevoa_borda',['kind']='bica',['width']=3.0,['drop']=20.04,['water_level_up']=80.64,['face_y_local']=428.1,['waypoints']='-2012.69,80.50,1212.27;-2012.49,77.50,1212.11;-2012.11,70.45,1211.78;-2011.19,70.15,1211.01;-2010.88,66.00,1210.76;-2010.77,60.32,1210.66',['widths']='3.0,3.6,4.2,4.6,5.0,5.6',['note']='ponta da soleira de pedra escura (no nivel da PEDRA; a lamina de 0,28 corre por cima) entre as 2 pedras-guarda do muro da forja; cortina medida: bica -> degrau de rocha (70,35) -> lagoa (60,32)',['cor']='214,228,248',['tam']=1.5,['vida']=2.6,['vel']=2.5,['transp']=0.55,['infl']=0.9,['luz']=0.1,['tex']='nevoa',['rate']=3.0,['Dist']=220.0,['vfx']='emissor',['fwd_x']=0.766,['fwd_z']=-0.6428}},
  {'FX_Fall_1_Step',{-2011.23,70.35,1211.045},{0.643,0.0,0.766},{0.766,0.0,-0.643},{['fx']='espuma_degrau',['width']=4.6,['jump']=1.3,['note']='degrau de rocha no meio da queda: a cortina bate no topo e passa por cima da borda da frente',['cor']='214,228,248',['tam']=3.68,['vida']=2.6,['vel']=2.5,['transp']=0.55,['infl']=0.9,['luz']=0.1,['tex']='nevoa',['rate']=8.0,['Dist']=200.0,['vfx']='emissor',['fwd_x']=0.766,['fwd_z']=-0.6428}},
  {'FX_Fall_2_Base',{-1890.399,12.0,1049.346},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{['fx']='nevoa_base',['width']=3.2,['note']='a cortina some na nevoa (abaixo so o mar de nuvens); medida contra a quilha no build',['cor']='214,228,248',['tam']=5.12,['vida']=2.6,['vel']=2.5,['transp']=0.55,['infl']=0.9,['luz']=0.1,['tex']='nevoa',['rate']=6.0,['Dist']=420.0,['vfx']='emissor',['fwd_x']=-0.6428,['fwd_z']=-0.766}},
  {'FX_Fall_2_Lip',{-1889.242,53.92,1050.725},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{['fx']='nevoa_borda',['kind']='bica',['width']=1.4,['drop']=41.92,['water_level_up']=54.22,['waypoints']='-1889.24,54.04,1050.72;-1889.69,52.52,1050.19;-1890.01,47.00,1049.81;-1890.21,38.00,1049.58;-1890.34,26.00,1049.42;-1890.40,12.00,1049.35',['widths']='1.4,1.5,1.6,1.8,2.0,2.3',['note']='sangradouro fino: ponta da bica em balanco na borda leste (ravina); unica queda para fora',['cor']='214,228,248',['tam']=0.7,['vida']=2.6,['vel']=2.5,['transp']=0.55,['infl']=0.9,['luz']=0.1,['tex']='nevoa',['rate']=2.0,['Dist']=260.0,['vfx']='emissor',['fwd_x']=-0.6428,['fwd_z']=-0.766}},
  {'FX_Forge_Embers',{-1969.162,85.43,1327.173},{0.643,0.0,0.766},{0.766,0.0,-0.643},{['fx']='brasas',['Dist']=120.0,['width']=10.0,['height']=9.0,['tex']='brilho',['cor']='255,140,60',['cor_fim']='255,72,24',['rate']=6.0,['vida']=2.2,['vel']=2.6,['tam']=0.28,['fim']=0.15,['transp']=0.15,['luz']=1.0,['infl']=0.0,['spread']='28,28',['acc_up']=2.6,['drift']=0.6,['area']='6.5,3,1.2',['forma']='Box',['note']='face do arco de tijolo MEDIDA; sai para fora (fwd = sul, a clareira) e sobe',['vfx']='emissor',['fwd_x']=0.766,['fwd_z']=-0.6428}},
  {'FX_Forge_Smoke',{-2012.541,151.4,1315.272},{0.262,0.0,-0.965},{-0.965,0.0,-0.262},{['fx']='fumaca',['Dist']=400.0,['note']='topo MEDIDO da coroa da chamine (sai de dentro do coroamento); deriva = fwd do marcador',['tex']='fumaca',['cor']='96,90,88',['cor_ini']='138,96,70',['rate']=3.0,['vida']=9.0,['vel']=3.5,['tam']=4.5,['fim']=2.6,['transp']=0.55,['luz']=0.05,['infl']=1.0,['spread']='10,10',['acc_up']=1.3,['drift']=0.5,['area']='3.4,1,3.4',['forma']='Box',['vfx']='emissor',['fwd_x']=-0.965,['fwd_z']=-0.2621}},
  {'FX_Forge_Smoke_Vent',{-1983.396,109.874,1339.116},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fx']='fumaca',['tex']='fumaca',['cor']='104,98,94',['rate']=1.6,['vida']=6.0,['vel']=1.6,['tam']=3.2,['fim']=2.4,['transp']=0.68,['luz']=0.0,['infl']=1.0,['spread']='70,20',['acc_up']=1.0,['drift']=0.4,['area']='12.8,2.9,4.4',['forma']='Box',['Dist']=300.0,['note']='NOVO (onda 3c): lanternim de fumaca (kemuri-dashi) na cumeeira do salao; ripas medidas no ds_forge',['vfx']='emissor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'FX_Mist_Bamboo',{-1706.299,58.631,1043.946},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fx']='nevoa_baixa',['radius']=30.0,['tex']='nevoa',['cor']='176,188,214',['rate']=1.2,['vida']=10.0,['vel']=0.5,['tam']=14.0,['fim']=1.3,['transp']=0.86,['luz']=0.0,['infl']=1.0,['spread']='90,10',['acc_up']=0.05,['drift']=0.3,['area']='40,1.5,40',['forma']='Box',['Dist']=260.0,['vfx']='emissor',['note']='onda 3c: assentado no chao medido + 1,2; nevoa < 2,5 de altura',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'FX_Mist_Ravine',{-1882.91,58.2,1060.294},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fx']='nevoa_baixa',['radius']=14.0,['note']='nevoa dos 3 pocos do sangradouro | onda 3c: assentado no chao medido + 1,2; nevoa < 2,5 de altura',['tex']='nevoa',['cor']='176,188,214',['rate']=0.9,['vida']=10.0,['vel']=0.5,['tam']=14.0,['fim']=1.3,['transp']=0.86,['luz']=0.0,['infl']=1.0,['spread']='90,10',['acc_up']=0.05,['drift']=0.3,['area']='22,1.5,22',['forma']='Box',['Dist']=260.0,['vfx']='emissor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GATE_OnePiece',{-2044.067,80.2,1537.014},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['open_w']=16.0,['open_h']=18.0,['deck_w']=18.0,['area_id']=5,['key']='OnePiece',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GATE_OnePiece_EXIT',{-2050.95,80.4,1546.844},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['gate']='OnePiece',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GATE_OnePiece_INTERACT',{-2040.052,80.4,1531.28},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['gate']='OnePiece',['radius']=10.0,['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GATE_OnePiece_LOCKED',{-2044.067,89.2,1537.014},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['gate']='OnePiece',['state_default']='locked',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GATE_OnePiece_OpenFX',{-2044.067,89.2,1537.014},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['gate']='OnePiece',['state']='unlocked',['fx']='abertura',['fwd_x']=-0.5736,['fwd_z']=0.8192}},
  {'GP_Block_01',{-1737.689,60.2,1151.22},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_02',{-1857.192,60.2,1251.495},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_03',{-1813.538,60.2,1060.826},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_04',{-1744.01,60.2,1143.687},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_05',{-1863.512,60.2,1243.962},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_06',{-1747.647,60.2,1159.576},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_07',{-1823.496,60.2,1069.183},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_08',{-1750.33,60.2,1136.154},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_09',{-1869.833,60.2,1236.429},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_10',{-1757.606,60.2,1167.932},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_11',{-1833.455,60.2,1077.539},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_12',{-1756.651,60.2,1128.621},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_13',{-1876.154,60.2,1228.896},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_14',{-1767.564,60.2,1176.288},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_15',{-1843.413,60.2,1085.895},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_16',{-1762.972,60.2,1121.089},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_17',{-1882.475,60.2,1221.363},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_18',{-1777.523,60.2,1184.645},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_19',{-1853.372,60.2,1094.251},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_20',{-1769.292,60.2,1113.556},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_21',{-1888.795,60.2,1213.831},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_22',{-1787.482,60.2,1193.001},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_23',{-1863.331,60.2,1102.608},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_24',{-1775.613,60.2,1106.023},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_25',{-1895.116,60.2,1206.298},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_26',{-1797.44,60.2,1201.357},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_27',{-1873.289,60.2,1110.964},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_28',{-1781.934,60.2,1098.49},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_29',{-1901.437,60.2,1198.765},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_30',{-1807.399,60.2,1209.713},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_31',{-1883.248,60.2,1119.32},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_32',{-1788.255,60.2,1090.958},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_33',{-1907.758,60.2,1191.232},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_34',{-1817.357,60.2,1218.07},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_35',{-1893.206,60.2,1127.676},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_36',{-1794.575,60.2,1083.425},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_37',{-1914.078,60.2,1183.7},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_38',{-1827.316,60.2,1226.426},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_39',{-1903.165,60.2,1136.033},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_40',{-1800.896,60.2,1075.892},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_41',{-1920.399,60.2,1176.167},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_42',{-1837.275,60.2,1234.782},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_43',{-1913.124,60.2,1144.389},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_44',{-1807.217,60.2,1068.359},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_45',{-1926.72,60.2,1168.634},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_46',{-1847.233,60.2,1243.138},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_47',{-1923.082,60.2,1152.745},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_48',{-1933.041,60.2,1161.101},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.5,['kind']='borda',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_49',{-1748.959,60.2,1150.234},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_50',{-1756.62,60.2,1156.661},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_51',{-1764.28,60.2,1163.089},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_52',{-1771.941,60.2,1169.517},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_53',{-1833.224,60.2,1220.94},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_54',{-1840.885,60.2,1227.368},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_55',{-1848.545,60.2,1233.796},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_56',{-1856.206,60.2,1240.224},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_57',{-1755.387,60.2,1142.573},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_58',{-1763.048,60.2,1149.001},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_59',{-1854.973,60.2,1226.135},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_60',{-1862.634,60.2,1232.563},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_61',{-1761.815,60.2,1134.913},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_62',{-1869.061,60.2,1224.903},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_63',{-1800.382,60.2,1088.95},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_64',{-1907.629,60.2,1178.94},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_65',{-1806.81,60.2,1081.29},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_66',{-1814.471,60.2,1087.718},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_67',{-1906.396,60.2,1164.852},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_68',{-1914.057,60.2,1171.28},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_69',{-1813.238,60.2,1073.629},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_70',{-1820.899,60.2,1080.057},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_71',{-1828.559,60.2,1086.485},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_72',{-1836.219,60.2,1092.913},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_73',{-1897.503,60.2,1144.336},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_74',{-1905.163,60.2,1150.764},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_75',{-1912.824,60.2,1157.192},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_76',{-1920.484,60.2,1163.619},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=6.0,['kind']='canto',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_77',{-1755.907,60.2,1140.398},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.0,['kind']='corredor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_78',{-1767.177,60.2,1139.412},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.0,['kind']='corredor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_79',{-1790.617,60.2,1099.032},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.0,['kind']='corredor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_80',{-1871.113,60.2,1224.014},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.0,['kind']='corredor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'GP_Block_81',{-1864.985,60.2,1218.871},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['radius']=5.0,['kind']='corredor',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ISLAND_EXIT_DemonSlayer',{-2005.064,80.2,1481.312},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['width']=18.0,['deck_z']=80.2,['heading_deg']=125.0,['note']='cabeca da ponte de saida (56, T4), depois do torii de saida',['fwd_x']=-0.5736,['fwd_z']=0.8192,['heading_deg_local']=105.0}},
  {'ISLAND_NEXT_ANCHOR_OnePiece',{-2054.391,80.2,1551.759},{-0.819,0.0,-0.574},{-0.574,0.0,0.819},{['width']=18.0,['deck_z']=80.2,['clear_h']=22.0,['heading_deg']=125.0,['next_area']=5,['next_key']='OnePiece',['fwd_roblox']='-0.5736,0.0000,0.8192',['pos_roblox']='-2054.39,80.20,1551.76',['orientation_roblox']='0,145.0,0',['guard']='PROVISORIO: COL_DSAnchorGuard_* + DS_Exit_AnchorGuard (next_island_guard=True)',['guard_note']='a integracao da One Piece REMOVE a guarda quando a ponte seguinte encosta aqui',['fwd_x']=-0.5736,['fwd_z']=0.8192,['heading_deg_local']=105.0}},
  {'MiningZone_DemonSlayer',{-1835.365,60.2,1156.161},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['kind']='mining',['floor']=60.2,['sx']=112.0,['sy']=150.0,['open_sky']=true,['note']='clareira natural a CEU ABERTO (sem \'ceil\': o script usa piso + 28); o jogo usa ORE_* + grade hexagonal + bloqueios GP_Block_*; frente = +Y local',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_01',{-1822.605,60.2,1175.739},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_02',{-1827.309,60.2,1152.351},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_03',{-1858.641,60.2,1131.921},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_04',{-1813.924,60.2,1187.096},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_05',{-1818.654,60.2,1162.307},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_06',{-1835.898,60.2,1140.108},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_07',{-1867.473,60.2,1120.991},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_08',{-1844.582,60.2,1129.837},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_09',{-1809.039,60.2,1172.646},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_10',{-1821.845,60.2,1138.576},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_11',{-1853.279,60.2,1119.472},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_12',{-1813.792,60.2,1148.842},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_13',{-1799.28,60.2,1183.437},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_14',{-1830.805,60.2,1128.302},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_15',{-1804.333,60.2,1159.415},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_16',{-1840.873,60.2,1117.377},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_17',{-1808.573,60.2,1135.755},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_18',{-1794.297,60.2,1170.862},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_19',{-1816.559,60.2,1125.46},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_20',{-1848.143,60.2,1106.442},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_21',{-1786.651,60.2,1181.312},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_22',{-1799.173,60.2,1147.409},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_23',{-1826.121,60.2,1114.189},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_24',{-1790.552,60.2,1158.321},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_25',{-1835.748,60.2,1104.474},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_26',{-1803.556,60.2,1123.439},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_27',{-1781.539,60.2,1167.989},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_28',{-1794.42,60.2,1132.756},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_29',{-1813.192,60.2,1111.721},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_30',{-1786.002,60.2,1144.281},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_31',{-1822.047,60.2,1101.059},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_32',{-1789.896,60.2,1121.127},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_33',{-1776.728,60.2,1154.867},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_34',{-1798.279,60.2,1109.129},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_35',{-1780.676,60.2,1130.544},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_36',{-1806.915,60.2,1098.791},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_37',{-1772.18,60.2,1142.644},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_COMMON_38',{-1785.289,60.2,1107.576},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='COMMON',['radius']=2.6,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_01',{-1873.168,60.2,1209.695},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_02',{-1900.394,60.2,1177.217},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_03',{-1877.657,60.2,1186.034},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_04',{-1867.822,60.2,1196.136},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_05',{-1886.518,60.2,1173.98},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_06',{-1860.281,60.2,1206.4},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_07',{-1896.14,60.2,1164.457},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_08',{-1851.078,60.2,1217.476},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_09',{-1863.916,60.2,1181.906},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_EPIC_10',{-1873.327,60.2,1171.763},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='EPIC',['radius']=3.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_SUPERLEGENDARY_01',{-1883.22,60.2,1198.026},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_SUPERLEGENDARY_02',{-1891.995,60.2,1187.009},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='SUPERLEGENDARY',['radius']=4.4,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_01',{-1854.353,60.2,1193.333},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_02',{-1881.882,60.2,1161.801},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_03',{-1846.357,60.2,1203.515},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_04',{-1860.091,60.2,1169.755},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_05',{-1890.2,60.2,1150.426},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_06',{-1837.532,60.2,1215.091},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_07',{-1849.709,60.2,1180.65},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_08',{-1867.955,60.2,1159.435},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_09',{-1841.566,60.2,1190.37},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_10',{-1877.687,60.2,1148.738},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_11',{-1833.181,60.2,1201.623},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_12',{-1845.748,60.2,1168.149},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_13',{-1886.944,60.2,1137.551},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_14',{-1854.553,60.2,1156.427},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_15',{-1836.496,60.2,1178.335},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_16',{-1863.348,60.2,1146.288},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_17',{-1827.623,60.2,1188.644},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_18',{-1841.179,60.2,1154.552},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_19',{-1872.401,60.2,1135.374},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_20',{-1831.728,60.2,1164.244},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_21',{-1818.034,60.2,1199.357},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'ORE_UNCOMMON_22',{-1849.631,60.2,1143.733},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['rarity']='UNCOMMON',['radius']=3.0,['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER',{-1835.365,60.2,1156.161},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['waypoints']='-1627.95,54.20,1040.86;-1631.73,54.20,1059.70;-1646.28,60.20,1071.91;-1680.78,60.20,1093.03;-1718.34,60.20,1116.71;-1783.59,60.20,1132.30;-1835.37,60.20,1156.16;-1889.50,60.20,1239.44;-1909.41,60.20,1256.15;-1928.57,70.20,1272.22;-1945.99,70.20,1268.57;-1965.91,80.20,1285.28;-1963.78,80.20,1309.60;-1966.54,80.20,1324.97',['note']='patio -> Trilha -> antecampo -> centro da clareira -> pe da subida -> patio da forja',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_00',{-1627.951,54.2,1040.863},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_01',{-1631.728,54.2,1059.697},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_02',{-1646.283,60.2,1071.91},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_03',{-1680.781,60.2,1093.026},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_04',{-1718.344,60.2,1116.712},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_05',{-1783.59,60.2,1132.298},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_06',{-1835.365,60.2,1156.161},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_07',{-1889.498,60.2,1239.441},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_08',{-1909.415,60.2,1256.153},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_09',{-1928.566,70.2,1272.223},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_10',{-1945.992,70.2,1268.569},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_11',{-1965.909,80.2,1285.281},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_12',{-1963.778,80.2,1309.601},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PATH_ENTRY_CENTER_13',{-1966.543,80.2,1324.975},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'PURCHASE_UI_ANCHOR_OnePiece',{-2042.633,94.2,1534.966},{0.819,0.0,0.574},{0.574,0.0,-0.819},{['gate']='OnePiece',['faces']='approach',['ui']='BillboardGui preco/requisito',['fwd_x']=0.5736,['fwd_z']=-0.8192}},
  {'SAFE_Cabeceira',{-2045.787,80.2,1539.471},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Clareira_N',{-1904.925,60.2,1221.056},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Clareira_S',{-1752.949,60.2,1106.586},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Entrada',{-1629.483,54.2,1042.149},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Forja_Patio',{-1957.35,80.2,1317.262},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Patamar',{-1932.397,70.2,1275.437},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Patio_Carvao',{-1860.897,80.2,1366.869},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Ponte_Chegada',{-1565.135,53.0,988.154},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Saida',{-1968.883,80.2,1465.312},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Summon',{-1947.614,70.2,1092.395},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Trilha',{-1664.668,60.2,1087.337},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Vila_Alta',{-1766.507,66.2,1261.558},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SAFE_Vila_Baixa',{-1687.384,60.2,1184.723},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='ponto seguro da rede de quedas',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SUMMON_Interact',{-1954.685,70.2,1083.968},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='gabinete invisivel do Gacha_nichirin (prompt Invocar)',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'SUMMON_Main',{-1959.184,70.2,1078.606},{-0.766,0.0,0.643},{0.643,0.0,0.766},{['note']='torre de invocacao AMS (estrela + aneis + torre + nucleo, familia da Ilha 1), frente para -X local (oeste: clareira e entrada)',['fwd_x']=0.6428,['fwd_z']=0.766}},
  {'SUMMON_PlayerPosition',{-1948.9,70.2,1090.862},{0.766,0.0,-0.643},{-0.643,0.0,-0.766},{['note']='onde o jogador fica olhando a torre (pad do gacha)',['fwd_x']=-0.6428,['fwd_z']=-0.766}},
  {'WATER_Channel',{-1978.905,60.32,1181.428},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['level']=60.32,['floor']=59.7,['depth']=0.62,['rim']=60.65,['waypoints']='-1978.90,60.32,1181.43;-1949.33,60.32,1152.58;-1918.69,60.32,1126.87;-1890.86,60.32,1100.91;-1874.16,60.32,1080.37;-1875.64,60.32,1075.08;-1877.57,60.32,1070.70;-1879.27,60.32,1066.50;-1879.68,60.32,1065.55;-1879.97,57.62,1065.02;-1881.26,57.62,1062.57;-1882.76,57.62,1060.16;-1883.45,57.62,1059.18;-1883.79,54.22,1058.68;-1885.72,54.22,1055.86;-1887.71,54.22,1052.70;-1889.24,54.04,1050.72',['widths']='3.0,3.0,3.0,3.0,3.0,3.0,2.4,2.4,2.4,2.4,2.4,2.4,2.4,2.4,2.4,2.4,1.6',['pools']='60.32/59.60;57.62/57.00;54.22/53.60',['note']='canal de cantaria pela margem leste da clareira (sob a pontezinha do summon) + sangradouro em 3 pocos na ravina; os pares de pontos com cota diferente sao as soleiras (queda curta)',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'WATER_Flume',{-2095.169,103.5,1302.365},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['waypoints']='-2095.17,103.50,1302.37;-2072.43,102.40,1285.90;-2054.54,101.80,1276.11;-2047.54,101.60,1272.32',['widths']='2.0,2.0,2.0,2.0',['note']='aqueduto de madeira: nascente -> bico 4,2 ao norte do topo da roda (a agua cai nas cacambas); poco da roda (pit_rect, agua pit_level) -> saida no muro leste x 95,2, y 482 +- 1,75 -> calha ds_water',['pit_level']=80.64,['pit_rect']='89.3,476.7,94.7,499.3',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'WATER_Pond',{-1988.776,60.32,1196.003},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['shape']='poligono',['level']=60.32,['floor']=59.7,['depth']=0.62,['rim_min']=60.65,['sx']=31.7,['sy']=47.5,['waypoints']='-1967.26,60.32,1196.86;-1969.63,60.32,1193.11;-1971.92,60.32,1188.51;-1974.66,60.32,1184.93;-1976.56,60.32,1181.43;-1977.93,60.32,1182.59;-1979.86,60.32,1180.29;-1978.10,60.32,1178.81;-1979.96,60.32,1176.59;-1985.73,60.32,1178.42;-1992.57,60.32,1181.16;-1997.62,60.32,1184.48;-2003.11,60.32,1189.61;-2008.08,60.32,1195.35;-2013.00,60.32,1199.61;-2016.65,60.32,1204.89;-2014.49,60.32,1208.56;-2011.26,60.32,1213.03;-2007.80,60.32,1217.31;-2002.76,60.32,1216.47;-1996.24,60.32,1214.13;-1987.85,60.32,1211.53;-1979.87,60.32,1209.53;-1975.33,60.32,1207.16;-1971.38,60.32,1202.54;-1968.52,60.32,1199.10',['mouth']='116.40,381.20;119.40,381.20',['note']='contorno DESENHADO da agua (dentro do barranco e das pedras); a boca do canal fica fora (o canal comeca na linha da boca)',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'WATER_Tailrace',{-2042.047,80.64,1263.757},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['level']=80.64,['floor']=79.7,['depth']=0.94,['rim']=80.96,['waypoints']='-2042.05,80.64,1263.76;-2041.85,80.64,1244.57;-2027.32,80.64,1224.54;-2014.07,80.64,1213.42;-2012.69,80.50,1212.27',['widths']='3.0,3.0,3.0,3.0,2.4',['note']='calha de cantaria do terraco da forja: cabeca em TAILRACE[0] (a agua da roda chega ali) -> bica da cascata (o ultimo trecho desce para a soleira)',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'WORLD_ENTRY_DemonSlayer',{-1627.951,54.4,1040.863},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['note']='chegada da ilha (patio do torii, olhando a escada da trilha e a clareira)',['fwd_x']=-0.766,['fwd_z']=0.6428}},
  {'WORLD_FROM_PREV',{-1534.493,52.2,962.443},{-0.643,0.0,-0.766},{-0.766,0.0,0.643},{['width']=18.0,['deck_z']=52.2,['prev']='ISLAND_NEXT_ANCHOR_DemonSlayer (Ilha 3 Shadow Garden)',['bridge_len']=100.0,['note']='centro da borda do tabuleiro da ponte de chegada (reta de 100, sobe 2 ate o patio T0); avanco = frente; tem de cair EXATO na ancora da Ilha 3',['fwd_x']=-0.766,['fwd_z']=0.6428}},
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
  {'L_DSFrg_East','POINT',{-2034.448,86.25,1296.32},{255,209,158},9.7,0.5,false,false},
  {'L_DSFrg_Furnace','POINT',{-1989.83,84.2,1344.516},{255,179,105},28.0,2.5,false,false},
  {'L_DSFrg_FurnaceMouth','POINT',{-1969.607,84.8,1327.546},{255,188,124},28.0,2.0,false,false},
  {'L_DSFrg_Kiln','POINT',{-1840.391,81.4,1365.327},{255,179,105},8.5,0.44,false,false},
  {'L_DSFrg_TowerWin','POINT',{-2012.541,121.0,1315.272},{255,209,158},12.2,0.68,false,false},
  {'L_DSFrg_Workshop','POINT',{-1945.936,97.075,1368.046},{255,209,158},9.7,0.5,false,false},
  {'L_DSProp_Lamp_Antecampo','POINT',{-1730.623,66.145,1100.444},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Bambu','POINT',{-1720.014,62.033,1050.64},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_Bambuzal','POINT',{-1669.191,61.068,1024.93},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Bridge_L','POINT',{-1566.818,59.2,1001.707},{255,209,158},7.7,0.4,false,true},
  {'L_DSProp_Lamp_Bridge_R','POINT',{-1578.774,59.2,987.458},{255,209,158},7.7,0.4,false,true},
  {'L_DSProp_Lamp_Carvao','POINT',{-1875.558,83.611,1331.849},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_ClrLToro','POINT',{-1873.201,62.425,1102.096},{255,209,158},6.0,0.34,false,true},
  {'L_DSProp_Lamp_ClrN','POINT',{-1934.415,64.606,1218.306},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_ClrNO','POINT',{-1876.323,64.439,1272.531},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_ClrOToro','POINT',{-1777.642,62.444,1217.118},{255,209,158},6.0,0.34,false,true},
  {'L_DSProp_Lamp_ClrSE','POINT',{-1801.098,63.837,1069.847},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_ClrSOToro','POINT',{-1733.257,62.386,1123.794},{255,209,158},6.0,0.34,false,true},
  {'L_DSProp_Lamp_Exit_0','POINT',{-1895.464,85.965,1410.394},{255,209,158},7.4,0.39,false,true},
  {'L_DSProp_Lamp_Exit_1','POINT',{-1936.441,85.965,1449.327},{255,209,158},7.4,0.39,false,true},
  {'L_DSProp_Lamp_Exit_2','POINT',{-1982.626,85.965,1461.016},{255,209,158},7.4,0.39,false,true},
  {'L_DSProp_Lamp_FrgCoal','POINT',{-1864.661,85.425,1359.584},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_FrgMouth_L','POINT',{-1962.522,88.5,1332.567},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_FrgMouth_R','POINT',{-1973.321,88.5,1319.697},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_FrgOeste','POINT',{-1911.932,83.864,1358.731},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_FrgPatamar','POINT',{-1919.01,74.349,1300.103},{255,209,158},5.5,0.33,false,true},
  {'L_DSProp_Lamp_FrgSubida_L','POINT',{-1959.22,86.025,1290.764},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_FrgSubida_R','POINT',{-1971.832,86.025,1279.156},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_PeSubida','POINT',{-1897.761,66.145,1260.015},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_SumMirante','POINT',{-1981.872,74.492,1086.416},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_SumTop_0','POINT',{-1932.443,72.675,1095.851},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_SumTop_1','POINT',{-1946.844,72.675,1107.936},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_SummonFoot','POINT',{-1916.966,65.965,1119.873},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Trilha','POINT',{-1644.072,65.965,1078.279},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_TrilhaMeio','POINT',{-1678.478,64.33,1098.116},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_VilAlta','POINT',{-1792.34,70.353,1284.542},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_VilRua','POINT',{-1711.759,64.445,1197.395},{255,209,158},7.0,0.38,false,true},
  {'L_DSProp_Lamp_Vil_AltaFoot','POINT',{-1717.512,66.025,1233.026},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_AltaTop','POINT',{-1733.433,72.025,1245.78},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_Clareira','POINT',{-1783.928,72.025,1253.587},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_GateL','POINT',{-1672.215,67.825,1131.509},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_GateR','POINT',{-1678.851,67.825,1129.28},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_Low','POINT',{-1700.576,66.025,1169.736},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_OesteForja','POINT',{-1825.91,72.025,1306.994},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Lamp_Vil_V6Gate','POINT',{-1811.13,72.025,1298.452},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Toro_In_L','POINT',{-1615.641,58.492,1046.199},{255,209,158},6.5,0.36,false,true},
  {'L_DSProp_Toro_In_R','POINT',{-1631.068,58.492,1027.814},{255,209,158},6.5,0.36,false,true},
  {'L_DSSum_Core','POINT',{-1958.156,79.2,1079.831},{162,191,255},11.0,0.58,false,false},
  {'L_DSSum_Lamp_L','POINT',{-1949.002,76.113,1075.806},{255,209,158},7.7,0.4,false,false},
  {'L_DSSum_Lamp_R','POINT',{-1963.71,76.113,1088.147},{255,209,158},7.7,0.4,false,false},
  {'L_DSSum_Star','POINT',{-1961.113,116.2,1076.308},{255,218,162},7.7,0.4,false,false},
  {'L_DSVil_V1_Chochin','POINT',{-1667.982,69.36,1158.921},{255,209,158},12.0,0.56,false,false},
  {'L_DSVil_V6_Andon','POINT',{-1795.198,70.92,1352.6},{255,209,158},14.0,0.56,false,false},
  {'L_DSVil_V6_Irori','POINT',{-1797.742,71.86,1338.678},{255,197,144},14.0,0.67,false,false},
  {'L_DSVil_Win_V2','POINT',{-1665.941,66.85,1200.462},{255,209,158},9.0,0.46,false,false},
  {'L_DSVil_Win_V3','POINT',{-1693.281,66.45,1230.029},{255,209,158},9.0,0.46,false,false},
  {'L_DSVil_Win_V4','POINT',{-1732.818,81.9,1265.925},{255,209,158},9.0,0.46,false,false},
  {'L_DSVil_Win_V5','POINT',{-1773.439,86.4,1283.063},{255,209,158},9.0,0.46,false,false},
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
  {'SAFE_Cabeceira',{-2045.787,80.2,1539.471}},
  {'SAFE_Clareira_N',{-1904.925,60.2,1221.056}},
  {'SAFE_Clareira_S',{-1752.949,60.2,1106.586}},
  {'SAFE_Entrada',{-1629.483,54.2,1042.149}},
  {'SAFE_Forja_Patio',{-1957.35,80.2,1317.262}},
  {'SAFE_Patamar',{-1932.397,70.2,1275.437}},
  {'SAFE_Patio_Carvao',{-1860.897,80.2,1366.869}},
  {'SAFE_Ponte_Chegada',{-1565.135,53.0,988.154}},
  {'SAFE_Saida',{-1968.883,80.2,1465.312}},
  {'SAFE_Summon',{-1947.614,70.2,1092.395}},
  {'SAFE_Trilha',{-1664.668,60.2,1087.337}},
  {'SAFE_Vila_Alta',{-1766.507,66.2,1261.558}},
  {'SAFE_Vila_Baixa',{-1687.384,60.2,1184.723}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(820,4,820); v.Position = Vector3.new(-1847.339111328125,-45.0,1211.8974609375) + ROOT_OFFSET
  v:ClearAllChildren()
  for _, s in ipairs(SAFE) do local at = Instance.new('Attachment'); at.Name = s[1]; at.Parent = v
    at.WorldPosition = Vector3.new(s[2][1], s[2][2], s[2][3]) + ROOT_OFFSET end
  v.Parent = root end

-- Script de servidor: personagens no grupo 'Personagens' (atravessam as cascas SoVisual) + rede de quedas
do
  local SSS = game:GetService('ServerScriptService')
  local s = SSS:FindFirstChild('ILHA_DEMONSLAYER_Servidor') or Instance.new('Script')
  s.Name = 'ILHA_DEMONSLAYER_Servidor'
  s.Source = [==[
-- gerado por montar_ilha_demonslayer.lua (export_roblox.py) - nao editar a mao
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
local root = workspace:WaitForChild('ILHA_DEMONSLAYER', 60)
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
  Lg.GeographicLatitude = 22.584
  Lg.ClockTime = 8.466
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
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (0.80, 0.60, -0.02) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
root.WorldPivot = CFrame.new(ROOT_OFFSET)
-- ===== pecas moveis (VFX_*) =====
local VFX = {
  ['VFX_DS_Kine_A'] = {p = Vector3.new(-2034.833,81.900,1277.193), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 0.000, bob = 1.600, rate = 0.100},
  ['VFX_DS_Kine_B'] = {p = Vector3.new(-2037.212,81.900,1274.358), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 0.000, bob = 1.600, rate = 0.150},
  ['VFX_DS_KineAxle'] = {p = Vector3.new(-2044.064,91.200,1269.926), a = Vector3.new(-0.6430,0.0000,-0.7660), rpm = 3.000, bob = 0.000, rate = 0.000},
  ['VFX_DS_Wheel'] = {p = Vector3.new(-2044.064,91.200,1269.926), a = Vector3.new(-0.6430,0.0000,-0.7660), rpm = 3.000, bob = 0.000, rate = 0.000},
  ['VFX_DSSUM_Ring_1'] = {p = Vector3.new(-1961.113,116.200,1076.308), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 2.000, bob = 0.000, rate = 0.000},
  ['VFX_DSSUM_Ring_2'] = {p = Vector3.new(-1961.113,116.200,1076.308), a = Vector3.new(0.0000,-1.0000,0.0000), rpm = 4.000, bob = 0.000, rate = 0.000},
  ['VFX_DSSUM_Ring_3'] = {p = Vector3.new(-1961.113,116.200,1076.308), a = Vector3.new(-0.2900,0.5300,0.7970), rpm = 6.000, bob = 0.000, rate = 0.000},
  ['VFX_DSSUM_Star'] = {p = Vector3.new(-1961.113,116.200,1076.308), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.000, rate = 0.000},
  ['VFX_GATE_OnePiece_Hat_1'] = {p = Vector3.new(-2030.951,95.800,1540.948), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -4.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePiece_Hat_2'] = {p = Vector3.new(-2029.034,91.000,1537.164), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePiece_Hat_3'] = {p = Vector3.new(-2049.349,91.300,1522.939), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -6.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePiece_Hat_4'] = {p = Vector3.new(-2052.250,96.100,1526.035), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 7.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePiece_Needle'] = {p = Vector3.new(-2042.948,101.600,1535.417), a = Vector3.new(0.5740,0.0000,-0.8190), rpm = 3.000, bob = 0.000, rate = 0.000},
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
  if (d:IsA('BasePart') or d:IsA('Model')) and (string.match(d.Name, '^DS_Exit_AnchorGuard') or string.match(d.Name, '^COL_DSAnchorGuard_')) then
    d:SetAttribute('next_island_guard', true)
    d:SetAttribute('removed_by', 'integracao da ilha One Piece (ponte seguinte encosta em ISLAND_NEXT_ANCHOR_OnePiece)')
    CS:AddTag(d, 'GuardaProximaIlha'); nG += 1 end
end
print(string.format('%d pecas da guarda da ancora marcadas (GuardaProximaIlha)', nG))
print(string.format('ILHA_DEMONSLAYER montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
