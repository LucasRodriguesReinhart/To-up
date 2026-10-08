-- montar_lobby_vila_medieval.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 2856eacf
-- 1) Importe os FBX LOBBY_VM_*_2856ea.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador
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
local EXPORT_ID = '2856eacf'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o lobby Vila Medieval INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
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
  ['wood'] = '',  -- textures/T_wood_v3.png (5.0 studs por repeticao)
}
-- material/variante -> c = cor calibrada no Studio, m = Enum.Material (hibrido), t = transparencia,
--   s = CastShadow da familia, x = textura de detalhe, w = espiral
local MAT = {
  ['Bark_Dark'] = {c = Color3.fromRGB(86,60,46), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Bark_VM'] = {c = Color3.fromRGB(96,66,44), m = Enum.Material.Wood, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_VM_Far'] = {c = Color3.fromRGB(150,166,192), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cliff_VM_FarSnow'] = {c = Color3.fromRGB(226,232,240), m = Enum.Material.Snow, t = 0.0, s = false, x = nil, w = nil},
  ['Cliff_VM_Rock'] = {c = Color3.fromRGB(122,124,132), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VM_Blue'] = {c = Color3.fromRGB(56,86,150), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VM_Red'] = {c = Color3.fromRGB(176,54,44), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Dirt_VM'] = {c = Color3.fromRGB(150,122,88), m = Enum.Material.Ground, t = 0.0, s = false, x = nil, w = nil},
  ['Emblem_Cream'] = {c = Color3.fromRGB(237,231,215), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Forge_Glow_VM'] = {c = Color3.fromRGB(255,128,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_VM'] = {c = Color3.fromRGB(98,168,62), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_VM_Hill'] = {c = Color3.fromRGB(112,160,72), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Lantern_Glow'] = {c = Color3.fromRGB(255,146,56), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Palm'] = {c = Color3.fromRGB(110,166,94), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Pine'] = {c = Color3.fromRGB(45,111,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Pine'] = {c = Color3.fromRGB(46,104,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Round'] = {c = Color3.fromRGB(84,150,62), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VM_Bronze'] = {c = Color3.fromRGB(176,138,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VM_Iron'] = {c = Color3.fromRGB(70,70,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
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
  ['Plaster_VM_Cream'] = {c = Color3.fromRGB(235,225,200), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_VM_Ochre'] = {c = Color3.fromRGB(226,208,176), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Plaster_VM_Peach'] = {c = Color3.fromRGB(232,210,186), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Ridge'] = {c = Color3.fromRGB(150,78,44), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta'] = {c = Color3.fromRGB(200,110,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta_B'] = {c = Color3.fromRGB(182,96,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Rope'] = {c = Color3.fromRGB(190,172,140), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_DS_Rock'] = {c = Color3.fromRGB(92,92,100), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Light'] = {c = Color3.fromRGB(156,148,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Paving_VM'] = {c = Color3.fromRGB(178,166,146), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_Edge'] = {c = Color3.fromRGB(140,132,120), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_VM_Base'] = {c = Color3.fromRGB(124,130,142), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Dark'] = {c = Color3.fromRGB(96,100,112), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Trim'] = {c = Color3.fromRGB(160,158,150), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Water_VM'] = {c = Color3.fromRGB(64,150,190), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Window_VM_Dark'] = {c = Color3.fromRGB(54,62,80), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Wood_Dark'] = {c = Color3.fromRGB(92,64,47), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Light'] = {c = Color3.fromRGB(148,110,80), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
  ['Wood_Plank'] = {c = Color3.fromRGB(126,92,66), m = Enum.Material.Wood, t = 0.0, s = true, x = 'wood', w = nil},
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
local FBX = {[1]='LOBBY_VM_02_TERRAIN_2856ea.fbx', [2]='LOBBY_VM_03_TOWN_2856ea.fbx', [3]='LOBBY_VM_04_FORGE_2856ea.fbx', [4]='LOBBY_VM_05_SERVICES_2856ea.fbx', [5]='LOBBY_VM_06_PORTALS_2856ea.fbx', [6]='LOBBY_VM_07_EXIT_2856ea.fbx', [7]='LOBBY_VM_08_WATER_2856ea.fbx', [8]='LOBBY_VM_09_VEGETATION_2856ea.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['VM_Bg_Mountains__Cliff_VM_Far']={-37.212,88.948,-211.813,1919.056,297.896,1494.601,1,false,'Cliff_VM_Far','k',''},
  ['VM_Bg_Mountains__Cliff_VM_FarSnow']={-35.457,152.169,-185.043,1658.645,171.454,1228.512,1,false,'Cliff_VM_FarSnow','k',''},
  ['VM_Ter_CanalWalls__Stone_VM_Base']={18.5,4.35,-45.0,295.0,7.5,80.0,1,true,'Stone_VM_Base','',''},
  ['VM_Ter_CanalWalls__Stone_VM_Trim']={18.5,7.04,-12.0,295.0,2.12,14.1,1,true,'Stone_VM_Trim','',''},
  ['VM_Ter_Cliffs__Cliff_VM_Rock']={-27.46,-15.398,13.917,403.855,37.205,292.64,1,true,'Cliff_VM_Rock','',''},
  ['VM_Ter_Ground__Cliff_VM_Rock']={-28.0,3.1,13.5,392.0,5.8,279.0,1,true,'Cliff_VM_Rock','',''},
  ['VM_Ter_Ground__Grass_VM']={-28.0,5.9,13.5,392.0,1.8,279.0,1,false,'Grass_VM','',''},
  ['VM_Ter_Ground__Stone_VM_Dark']={18.226,0.4,-45.0,297.852,0.4,80.0,1,true,'Stone_VM_Dark','',''},
  ['VM_Ter_Hills__Bark_VM']={-32.0,40.946,-52.022,577.63,54.019,510.0,1,false,'Bark_VM','k',''},
  ['VM_Ter_Hills__Grass_VM_Hill']={-24.467,-5.148,-71.677,765.106,140.413,638.392,1,false,'Grass_VM_Hill','k',''},
  ['VM_Ter_Hills__Leaf_VM_Pine']={-31.756,49.861,-51.065,587.256,65.82,520.928,1,false,'Leaf_VM_Pine','k',''},
  ['VM_House_E1__Plaster_VM_Cream']={62.0,23.864,86.0,19.348,21.728,21.172,2,true,'Plaster_VM_Cream','','VM_House_E1'},
  ['VM_House_E1__Roof_VM_Ridge']={60.127,34.391,86.0,10.025,2.513,19.751,2,false,'Roof_VM_Ridge','','VM_House_E1'},
  ['VM_House_E1__Roof_VM_Terracotta']={62.0,29.382,86.0,22.915,11.822,23.931,2,true,'Roof_VM_Terracotta','','VM_House_E1'},
  ['VM_House_E1__Stone_VM_Base']={62.0,21.864,85.965,15.261,30.128,16.734,2,true,'Stone_VM_Base','','VM_House_E1'},
  ['VM_House_E1__Stone_VM_Dark']={62.0,21.689,85.996,15.998,31.378,17.41,2,true,'Stone_VM_Dark','','VM_House_E1'},
  ['VM_House_E1__Stone_VM_Trim']={62.0,10.1,86.0,15.752,5.15,17.155,2,false,'Stone_VM_Trim','','VM_House_E1'},
  ['VM_House_E1__Window_VM_Dark']={62.0,22.601,86.0,18.971,15.262,16.842,2,false,'Window_VM_Dark','','VM_House_E1'},
  ['VM_House_E1__Wood_VM_Plank']={56.163,10.0,87.592,1.535,6.4,3.991,2,false,'Wood_VM_Plank','','VM_House_E1'},
  ['VM_House_E1__Wood_VM_Timber']={62.0,19.0,86.0,19.984,12.0,21.387,2,true,'Wood_VM_Timber','','VM_House_E1'},
  ['VM_House_E2__Plaster_VM_Peach']={70.0,20.672,108.0,13.2,15.344,14.6,2,false,'Plaster_VM_Peach','','VM_House_E2'},
  ['VM_House_E2__Roof_VM_Ridge']={70.0,28.764,108.0,15.6,1.0,1.0,2,false,'Roof_VM_Ridge','','VM_House_E2'},
  ['VM_House_E2__Roof_VM_Terracotta_B']={70.0,23.19,108.0,15.2,11.438,17.752,2,false,'Roof_VM_Terracotta_B','','VM_House_E2'},
  ['VM_House_E2__Stone_VM_Base']={70.0,18.672,108.0,11.0,23.744,13.0,2,false,'Stone_VM_Base','','VM_House_E2'},
  ['VM_House_E2__Stone_VM_Dark']={70.0,18.497,108.0,11.6,24.994,13.6,2,true,'Stone_VM_Dark','','VM_House_E2'},
  ['VM_House_E2__Stone_VM_Trim']={70.0,10.1,108.0,11.4,5.15,13.4,2,false,'Stone_VM_Trim','','VM_House_E2'},
  ['VM_House_E2__Window_VM_Dark']={70.0,16.12,108.0,13.5,2.3,11.333,2,false,'Window_VM_Dark','','VM_House_E2'},
  ['VM_House_E2__Wood_VM_Plank']={64.45,10.0,108.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_E2'},
  ['VM_House_E2__Wood_VM_Timber']={70.0,20.298,108.0,13.4,14.596,15.31,2,true,'Wood_VM_Timber','','VM_House_E2'},
  ['VM_House_E3__Plaster_VM_Ochre']={70.0,20.032,130.0,14.227,14.064,17.43,2,false,'Plaster_VM_Ochre','','VM_House_E3'},
  ['VM_House_E3__Roof_VM_Ridge']={70.0,27.484,130.0,2.942,1.0,18.602,2,false,'Roof_VM_Ridge','','VM_House_E3'},
  ['VM_House_E3__Roof_VM_Terracotta']={70.0,22.55,130.0,17.57,10.159,19.749,2,false,'Roof_VM_Terracotta','','VM_House_E3'},
  ['VM_House_E3__Stone_VM_Base']={70.0,18.032,130.0,12.405,22.464,15.075,2,false,'Stone_VM_Base','','VM_House_E3'},
  ['VM_House_E3__Stone_VM_Dark']={70.0,17.857,130.0,13.065,23.714,15.734,2,true,'Stone_VM_Dark','','VM_House_E3'},
  ['VM_House_E3__Stone_VM_Trim']={70.0,10.1,130.0,12.845,5.15,15.514,2,false,'Stone_VM_Trim','','VM_House_E3'},
  ['VM_House_E3__Window_VM_Dark']={70.0,16.12,130.0,14.682,2.3,13.347,2,false,'Window_VM_Dark','','VM_House_E3'},
  ['VM_House_E3__Wood_VM_Plank']={64.48,10.0,129.419,0.916,6.4,4.03,2,false,'Wood_VM_Plank','','VM_House_E3'},
  ['VM_House_E3__Wood_VM_Timber']={70.0,16.0,130.0,14.907,6.0,17.577,2,true,'Wood_VM_Timber','','VM_House_E3'},
  ['VM_House_N1E__Plaster_VM_Cream']={21.0,24.544,-29.0,14.2,21.088,15.8,2,false,'Plaster_VM_Cream','','VM_House_N1E'},
  ['VM_House_N1E__Roof_VM_Ridge']={17.938,34.991,-29.0,7.125,2.033,18.2,2,false,'Roof_VM_Ridge','','VM_House_N1E'},
  ['VM_House_N1E__Roof_VM_Terracotta']={21.0,30.062,-29.0,17.352,11.182,17.8,2,false,'Roof_VM_Terracotta','','VM_House_N1E'},
  ['VM_House_N1E__Stone_VM_Base']={21.0,22.544,-28.8,11.0,29.488,12.4,2,true,'Stone_VM_Base','','VM_House_N1E'},
  ['VM_House_N1E__Stone_VM_Dark']={21.0,22.369,-28.825,11.6,30.738,12.95,2,true,'Stone_VM_Dark','','VM_House_N1E'},
  ['VM_House_N1E__Stone_VM_Trim']={21.0,11.1,-29.0,11.4,5.15,12.4,2,false,'Stone_VM_Trim','','VM_House_N1E'},
  ['VM_House_N1E__Window_VM_Dark']={21.0,23.521,-29.0,15.1,15.102,11.733,2,false,'Window_VM_Dark','','VM_House_N1E'},
  ['VM_House_N1E__Wood_VM_Plank']={15.45,11.0,-29.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_N1E'},
  ['VM_House_N1E__Wood_VM_Timber']={21.0,20.0,-29.0,14.91,12.0,15.91,2,true,'Wood_VM_Timber','','VM_House_N1E'},
  ['VM_House_N1W__Plaster_VM_Peach']={-22.0,21.672,-29.0,13.2,15.344,14.6,2,false,'Plaster_VM_Peach','','VM_House_N1W'},
  ['VM_House_N1W__Roof_VM_Ridge']={-22.0,29.764,-29.0,15.6,1.0,1.0,2,false,'Roof_VM_Ridge','','VM_House_N1W'},
  ['VM_House_N1W__Roof_VM_Terracotta_B']={-22.0,24.19,-29.0,15.2,11.438,17.752,2,false,'Roof_VM_Terracotta_B','','VM_House_N1W'},
  ['VM_House_N1W__Stone_VM_Base']={-22.0,19.672,-29.0,11.0,23.744,13.0,2,false,'Stone_VM_Base','','VM_House_N1W'},
  ['VM_House_N1W__Stone_VM_Dark']={-22.0,19.497,-29.0,11.6,24.994,13.6,2,true,'Stone_VM_Dark','','VM_House_N1W'},
  ['VM_House_N1W__Stone_VM_Trim']={-22.0,11.1,-29.0,11.4,5.15,13.4,2,false,'Stone_VM_Trim','','VM_House_N1W'},
  ['VM_House_N1W__Window_VM_Dark']={-22.0,17.12,-29.0,13.5,2.3,11.333,2,false,'Window_VM_Dark','','VM_House_N1W'},
  ['VM_House_N1W__Wood_VM_Plank']={-16.45,11.0,-29.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_N1W'},
  ['VM_House_N1W__Wood_VM_Timber']={-22.0,21.298,-29.0,13.4,14.596,15.31,2,true,'Wood_VM_Timber','','VM_House_N1W'},
  ['VM_House_N2E__Plaster_VM_Cream']={50.0,21.672,-34.0,17.884,15.344,18.619,2,true,'Plaster_VM_Cream','','VM_House_N2E'},
  ['VM_House_N2E__Roof_VM_Ridge']={50.0,29.764,-34.0,14.733,1.0,7.064,2,false,'Roof_VM_Ridge','','VM_House_N2E'},
  ['VM_House_N2E__Roof_VM_Terracotta']={50.0,24.19,-34.0,20.964,11.438,22.304,2,true,'Roof_VM_Terracotta','','VM_House_N2E'},
  ['VM_House_N2E__Stone_VM_Base']={50.0,19.672,-34.0,15.232,23.744,16.282,2,true,'Stone_VM_Base','','VM_House_N2E'},
  ['VM_House_N2E__Stone_VM_Dark']={50.0,19.497,-34.0,16.019,24.994,17.07,2,true,'Stone_VM_Dark','','VM_House_N2E'},
  ['VM_House_N2E__Stone_VM_Trim']={50.0,11.1,-34.0,15.757,5.15,16.807,2,false,'Stone_VM_Trim','','VM_House_N2E'},
  ['VM_House_N2E__Window_VM_Dark']={50.0,17.12,-34.0,16.873,2.3,15.735,2,false,'Window_VM_Dark','','VM_House_N2E'},
  ['VM_House_N2E__Wood_VM_Plank']={44.899,11.0,-36.186,2.035,6.4,3.874,2,false,'Wood_VM_Plank','','VM_House_N2E'},
  ['VM_House_N2E__Wood_VM_Timber']={50.0,21.298,-34.0,18.153,14.596,19.204,2,true,'Wood_VM_Timber','','VM_House_N2E'},
  ['VM_House_N2W__Plaster_VM_Ochre']={-46.0,21.352,-44.0,13.6,14.704,16.2,2,false,'Plaster_VM_Ochre','','VM_House_N2W'},
  ['VM_House_N2W__Roof_VM_Ridge']={-46.0,29.124,-44.0,1.0,1.0,18.6,2,false,'Roof_VM_Ridge','','VM_House_N2W'},
  ['VM_House_N2W__Roof_VM_Terracotta']={-46.0,23.87,-44.0,16.752,10.798,18.2,2,false,'Roof_VM_Terracotta','','VM_House_N2W'},
  ['VM_House_N2W__Stone_VM_Base']={-46.0,19.352,-44.0,12.0,23.104,14.0,2,false,'Stone_VM_Base','','VM_House_N2W'},
  ['VM_House_N2W__Stone_VM_Dark']={-46.0,19.177,-44.0,12.6,24.354,14.6,2,true,'Stone_VM_Dark','','VM_House_N2W'},
  ['VM_House_N2W__Stone_VM_Trim']={-46.0,11.1,-44.0,12.4,5.15,14.4,2,false,'Stone_VM_Trim','','VM_House_N2W'},
  ['VM_House_N2W__Window_VM_Dark']={-46.0,17.12,-44.0,14.5,2.3,12.0,2,false,'Window_VM_Dark','','VM_House_N2W'},
  ['VM_House_N2W__Wood_VM_Plank']={-39.95,11.0,-44.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_N2W'},
  ['VM_House_N2W__Wood_VM_Timber']={-46.0,17.0,-44.0,14.31,6.0,16.31,2,true,'Wood_VM_Timber','','VM_House_N2W'},
  ['VM_House_PNE__Plaster_VM_Cream']={38.0,20.352,21.0,21.246,14.704,21.924,2,true,'Plaster_VM_Cream','','VM_House_PNE'},
  ['VM_House_PNE__Roof_VM_Ridge']={38.0,27.751,21.0,12.686,1.745,16.188,2,false,'Roof_VM_Ridge','','VM_House_PNE'},
  ['VM_House_PNE__Roof_VM_Terracotta']={38.0,22.87,21.0,24.965,10.798,25.426,2,true,'Roof_VM_Terracotta','','VM_House_PNE'},
  ['VM_House_PNE__Stone_VM_Base']={38.0,18.352,21.0,18.64,23.104,19.204,2,true,'Stone_VM_Base','','VM_House_PNE'},
  ['VM_House_PNE__Stone_VM_Dark']={38.0,18.177,21.0,19.48,24.354,20.045,2,true,'Stone_VM_Dark','','VM_House_PNE'},
  ['VM_House_PNE__Stone_VM_Trim']={38.0,10.1,21.0,19.2,5.15,19.765,2,false,'Stone_VM_Trim','','VM_House_PNE'},
  ['VM_House_PNE__Window_VM_Dark']={38.0,19.473,21.0,19.211,9.006,18.866,2,false,'Window_VM_Dark','','VM_House_PNE'},
  ['VM_House_PNE__Wood_VM_Plank']={33.191,10.0,24.67,2.824,6.4,3.483,2,false,'Wood_VM_Plank','','VM_House_PNE'},
  ['VM_House_PNE__Wood_VM_Timber']={38.0,16.0,21.0,21.712,6.0,22.276,2,true,'Wood_VM_Timber','','VM_House_PNE'},
  ['VM_House_PNW__Plaster_VM_Peach']={-38.0,24.504,21.0,22.995,23.007,23.259,2,true,'Plaster_VM_Peach','','VM_House_PNW'},
  ['VM_House_PNW__Roof_VM_Ridge']={-38.0,36.427,21.0,15.075,1.0,11.836,2,false,'Roof_VM_Ridge','','VM_House_PNW'},
  ['VM_House_PNW__Roof_VM_Terracotta']={-38.0,30.022,21.0,26.497,13.102,26.977,2,true,'Roof_VM_Terracotta','','VM_House_PNW'},
  ['VM_House_PNW__Stone_VM_Base']={-38.0,22.504,21.0,18.033,31.407,18.409,2,true,'Stone_VM_Base','','VM_House_PNW'},
  ['VM_House_PNW__Stone_VM_Dark']={-38.0,22.329,21.0,18.874,32.657,19.25,2,true,'Stone_VM_Dark','','VM_House_PNW'},
  ['VM_House_PNW__Stone_VM_Trim']={-38.0,10.1,21.0,18.593,5.15,18.97,2,false,'Stone_VM_Trim','','VM_House_PNW'},
  ['VM_House_PNW__Window_VM_Dark']={-38.0,19.12,21.0,20.726,8.3,20.155,2,true,'Window_VM_Dark','','VM_House_PNW'},
  ['VM_House_PNW__Wood_VM_Plank']={-33.191,10.0,24.67,2.824,6.4,3.483,2,false,'Wood_VM_Plank','','VM_House_PNW'},
  ['VM_House_PNW__Wood_VM_Timber']={-38.0,24.063,21.0,23.348,22.127,23.724,2,true,'Wood_VM_Timber','','VM_House_PNW'},
  ['VM_House_PSW__Plaster_VM_Ochre']={-38.0,20.352,84.0,20.937,14.704,21.141,2,true,'Plaster_VM_Ochre','','VM_House_PSW'},
  ['VM_House_PSW__Roof_VM_Ridge']={-38.0,28.124,84.0,13.148,1.0,14.528,2,false,'Roof_VM_Ridge','','VM_House_PSW'},
  ['VM_House_PSW__Roof_VM_Terracotta']={-38.0,22.87,84.0,24.62,10.798,24.733,2,true,'Roof_VM_Terracotta','','VM_House_PSW'},
  ['VM_House_PSW__Stone_VM_Base']={-38.0,18.352,84.0,18.278,23.104,18.435,2,true,'Stone_VM_Base','','VM_House_PSW'},
  ['VM_House_PSW__Stone_VM_Dark']={-38.0,18.177,84.0,19.125,24.354,19.282,2,true,'Stone_VM_Dark','','VM_House_PSW'},
  ['VM_House_PSW__Stone_VM_Trim']={-38.0,10.1,84.0,18.843,5.15,19.0,2,false,'Stone_VM_Trim','','VM_House_PSW'},
  ['VM_House_PSW__Window_VM_Dark']={-38.0,16.12,84.0,18.808,2.3,18.611,2,false,'Window_VM_Dark','','VM_House_PSW'},
  ['VM_House_PSW__Wood_VM_Plank']={-33.491,10.0,79.966,3.04,6.4,3.314,2,false,'Wood_VM_Plank','','VM_House_PSW'},
  ['VM_House_PSW__Wood_VM_Timber']={-38.0,16.0,84.0,21.359,6.0,21.516,2,true,'Wood_VM_Timber','','VM_House_PSW'},
  ['VM_House_R1__Plaster_VM_Cream']={-58.0,20.032,76.0,16.2,14.064,12.6,2,false,'Plaster_VM_Cream','','VM_House_R1'},
  ['VM_House_R1__Roof_VM_Ridge']={-58.0,27.484,76.0,18.6,1.0,1.0,2,false,'Roof_VM_Ridge','','VM_House_R1'},
  ['VM_House_R1__Roof_VM_Terracotta']={-58.0,22.55,76.0,18.2,10.159,15.752,2,false,'Roof_VM_Terracotta','','VM_House_R1'},
  ['VM_House_R1__Stone_VM_Base']={-58.0,18.032,76.0,14.0,22.464,11.0,2,false,'Stone_VM_Base','','VM_House_R1'},
  ['VM_House_R1__Stone_VM_Dark']={-58.0,17.857,76.0,14.6,23.714,11.6,2,true,'Stone_VM_Dark','','VM_House_R1'},
  ['VM_House_R1__Stone_VM_Trim']={-58.0,10.1,76.0,14.4,5.15,11.4,2,false,'Stone_VM_Trim','','VM_House_R1'},
  ['VM_House_R1__Window_VM_Dark']={-58.0,16.12,76.0,12.0,2.3,13.5,2,false,'Window_VM_Dark','','VM_House_R1'},
  ['VM_House_R1__Wood_VM_Plank']={-58.0,10.0,70.45,4.0,6.4,0.5,2,false,'Wood_VM_Plank','','VM_House_R1'},
  ['VM_House_R1__Wood_VM_Timber']={-58.0,16.0,76.0,16.31,6.0,13.31,2,true,'Wood_VM_Timber','','VM_House_R1'},
  ['VM_House_R2__Plaster_VM_Peach']={-80.0,24.184,87.0,16.2,22.368,14.8,2,true,'Plaster_VM_Peach','','VM_House_R2'},
  ['VM_House_R2__Roof_VM_Ridge']={-80.0,35.788,87.0,1.0,1.0,17.2,2,false,'Roof_VM_Ridge','','VM_House_R2'},
  ['VM_House_R2__Roof_VM_Terracotta']={-80.0,29.702,87.0,19.352,12.462,16.8,2,false,'Roof_VM_Terracotta','','VM_House_R2'},
  ['VM_House_R2__Stone_VM_Base']={-80.0,22.184,87.2,13.0,30.768,11.4,2,true,'Stone_VM_Base','','VM_House_R2'},
  ['VM_House_R2__Stone_VM_Dark']={-80.0,22.009,87.175,13.6,32.018,11.95,2,true,'Stone_VM_Dark','','VM_House_R2'},
  ['VM_House_R2__Stone_VM_Trim']={-80.0,10.1,87.0,13.4,5.15,11.4,2,false,'Stone_VM_Trim','','VM_House_R2'},
  ['VM_House_R2__Window_VM_Dark']={-80.0,19.12,87.0,12.4,8.3,15.1,2,false,'Window_VM_Dark','','VM_House_R2'},
  ['VM_House_R2__Wood_VM_Plank']={-80.0,10.0,81.45,4.0,6.4,0.5,2,false,'Wood_VM_Plank','','VM_House_R2'},
  ['VM_House_R2__Wood_VM_Timber']={-80.0,23.769,87.0,16.91,21.538,15.0,2,true,'Wood_VM_Timber','','VM_House_R2'},
  ['VM_House_S1E__Plaster_VM_Ochre']={22.0,20.672,6.0,13.2,15.344,14.6,2,false,'Plaster_VM_Ochre','','VM_House_S1E'},
  ['VM_House_S1E__Roof_VM_Ridge']={22.0,28.764,6.0,15.6,1.0,1.0,2,false,'Roof_VM_Ridge','','VM_House_S1E'},
  ['VM_House_S1E__Roof_VM_Terracotta_B']={22.0,23.19,6.0,15.2,11.438,17.752,2,false,'Roof_VM_Terracotta_B','','VM_House_S1E'},
  ['VM_House_S1E__Stone_VM_Base']={22.0,18.672,6.0,11.0,23.744,13.0,2,false,'Stone_VM_Base','','VM_House_S1E'},
  ['VM_House_S1E__Stone_VM_Dark']={22.0,18.497,6.0,11.6,24.994,13.6,2,true,'Stone_VM_Dark','','VM_House_S1E'},
  ['VM_House_S1E__Stone_VM_Trim']={22.0,10.1,6.0,11.4,5.15,13.4,2,false,'Stone_VM_Trim','','VM_House_S1E'},
  ['VM_House_S1E__Window_VM_Dark']={22.0,16.12,6.0,13.5,2.3,11.333,2,false,'Window_VM_Dark','','VM_House_S1E'},
  ['VM_House_S1E__Wood_VM_Plank']={16.45,10.0,6.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_S1E'},
  ['VM_House_S1E__Wood_VM_Timber']={22.0,20.298,6.0,13.4,14.596,15.31,2,true,'Wood_VM_Timber','','VM_House_S1E'},
  ['VM_House_S1W__Plaster_VM_Cream']={-22.0,23.544,6.0,14.2,21.088,17.8,2,true,'Plaster_VM_Cream','','VM_House_S1W'},
  ['VM_House_S1W__Roof_VM_Ridge']={-18.938,33.991,6.0,7.125,2.033,20.2,2,false,'Roof_VM_Ridge','','VM_House_S1W'},
  ['VM_House_S1W__Roof_VM_Terracotta']={-22.0,29.062,6.0,17.352,11.182,19.8,2,false,'Roof_VM_Terracotta','','VM_House_S1W'},
  ['VM_House_S1W__Stone_VM_Base']={-22.0,21.544,6.2,11.0,29.488,14.4,2,true,'Stone_VM_Base','','VM_House_S1W'},
  ['VM_House_S1W__Stone_VM_Dark']={-22.0,21.369,6.175,11.6,30.738,14.95,2,true,'Stone_VM_Dark','','VM_House_S1W'},
  ['VM_House_S1W__Stone_VM_Trim']={-22.0,10.1,6.0,11.4,5.15,14.4,2,false,'Stone_VM_Trim','','VM_House_S1W'},
  ['VM_House_S1W__Window_VM_Dark']={-22.0,22.521,6.0,15.1,15.102,13.067,2,false,'Window_VM_Dark','','VM_House_S1W'},
  ['VM_House_S1W__Wood_VM_Plank']={-16.45,10.0,6.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_S1W'},
  ['VM_House_S1W__Wood_VM_Timber']={-22.0,19.0,6.0,14.91,12.0,17.91,2,true,'Wood_VM_Timber','','VM_House_S1W'},
  ['VM_House_SH1__Plaster_VM_Ochre']={66.0,20.672,70.0,17.14,15.344,18.025,2,false,'Plaster_VM_Ochre','','VM_House_SH1'},
  ['VM_House_SH1__Roof_VM_Ridge']={66.0,28.764,70.0,15.116,1.0,5.882,2,false,'Roof_VM_Ridge','','VM_House_SH1'},
  ['VM_House_SH1__Roof_VM_Terracotta_B']={66.0,23.19,70.0,20.034,11.438,21.647,2,true,'Roof_VM_Terracotta_B','','VM_House_SH1'},
  ['VM_House_SH1__Stone_VM_Base']={66.0,18.672,70.0,14.546,23.744,15.811,2,true,'Stone_VM_Base','','VM_House_SH1'},
  ['VM_House_SH1__Stone_VM_Dark']={66.0,18.497,70.0,15.305,24.994,16.57,2,true,'Stone_VM_Dark','','VM_House_SH1'},
  ['VM_House_SH1__Stone_VM_Trim']={66.0,10.1,70.0,15.052,5.15,16.317,2,false,'Stone_VM_Trim','','VM_House_SH1'},
  ['VM_House_SH1__Window_VM_Dark']={66.0,16.12,70.0,16.391,2.3,15.021,2,false,'Window_VM_Dark','','VM_House_SH1'},
  ['VM_House_SH1__Wood_VM_Plank']={60.735,10.0,68.245,1.739,6.4,3.953,2,false,'Wood_VM_Plank','','VM_House_SH1'},
  ['VM_House_SH1__Wood_VM_Timber']={66.0,20.298,70.0,17.377,14.596,18.642,2,true,'Wood_VM_Timber','','VM_House_SH1'},
  ['VM_House_W0__Plaster_VM_Cream']={33.0,20.352,103.0,14.135,14.704,14.506,2,false,'Plaster_VM_Cream','','VM_House_W0'},
  ['VM_House_W0__Roof_VM_Ridge']={33.0,28.124,103.0,15.632,1.0,2.109,2,false,'Roof_VM_Ridge','','VM_House_W0'},
  ['VM_House_W0__Roof_VM_Terracotta']={33.0,22.87,103.0,16.355,10.798,17.792,2,false,'Roof_VM_Terracotta','','VM_House_W0'},
  ['VM_House_W0__Stone_VM_Base']={33.0,18.352,103.0,11.827,23.104,12.753,2,false,'Stone_VM_Base','','VM_House_W0'},
  ['VM_House_W0__Stone_VM_Dark']={33.0,18.177,103.0,12.468,24.354,13.394,2,true,'Stone_VM_Dark','','VM_House_W0'},
  ['VM_House_W0__Stone_VM_Trim']={33.0,10.1,103.0,12.254,5.15,13.181,2,false,'Stone_VM_Trim','','VM_House_W0'},
  ['VM_House_W0__Window_VM_Dark']={33.0,16.12,103.0,14.226,2.3,11.601,2,false,'Window_VM_Dark','','VM_House_W0'},
  ['VM_House_W0__Wood_VM_Plank']={38.536,10.0,103.395,0.784,6.4,4.025,2,false,'Wood_VM_Plank','','VM_House_W0'},
  ['VM_House_W0__Wood_VM_Timber']={33.0,20.004,103.0,14.267,14.007,15.193,2,true,'Wood_VM_Timber','','VM_House_W0'},
  ['VM_House_W1__Plaster_VM_Peach']={32.0,23.864,125.0,16.062,21.728,17.576,2,true,'Plaster_VM_Peach','','VM_House_W1'},
  ['VM_House_W1__Roof_VM_Ridge']={35.006,34.391,125.0,8.02,2.513,19.226,2,false,'Roof_VM_Ridge','','VM_House_W1'},
  ['VM_House_W1__Roof_VM_Terracotta']={32.0,29.382,125.0,19.314,11.822,19.739,2,true,'Roof_VM_Terracotta','','VM_House_W1'},
  ['VM_House_W1__Stone_VM_Base']={32.0,21.864,124.832,12.667,30.128,13.949,2,true,'Stone_VM_Base','','VM_House_W1'},
  ['VM_House_W1__Stone_VM_Dark']={32.0,21.689,124.858,13.297,31.378,14.527,2,true,'Stone_VM_Dark','','VM_House_W1'},
  ['VM_House_W1__Stone_VM_Trim']={32.0,10.1,125.0,13.087,5.15,14.033,2,false,'Stone_VM_Trim','','VM_House_W1'},
  ['VM_House_W1__Window_VM_Dark']={32.0,22.601,125.0,16.729,15.262,13.229,2,false,'Window_VM_Dark','','VM_House_W1'},
  ['VM_House_W1__Wood_VM_Plank']={38.042,10.0,125.318,0.71,6.4,4.021,2,false,'Wood_VM_Plank','','VM_House_W1'},
  ['VM_House_W1__Wood_VM_Timber']={32.0,19.0,125.0,16.755,12.0,17.701,2,true,'Wood_VM_Timber','','VM_House_W1'},
  ['VM_House_W2__Plaster_VM_Ochre']={30.0,20.032,142.0,12.2,14.064,12.6,2,false,'Plaster_VM_Ochre','','VM_House_W2'},
  ['VM_House_W2__Roof_VM_Ridge']={30.0,27.484,142.0,14.6,1.0,1.0,2,false,'Roof_VM_Ridge','','VM_House_W2'},
  ['VM_House_W2__Roof_VM_Terracotta_B']={30.0,22.55,142.0,14.2,10.159,15.752,2,false,'Roof_VM_Terracotta_B','','VM_House_W2'},
  ['VM_House_W2__Stone_VM_Base']={30.0,18.032,142.0,10.0,22.464,11.0,2,false,'Stone_VM_Base','','VM_House_W2'},
  ['VM_House_W2__Stone_VM_Dark']={30.0,17.857,142.0,10.6,23.714,11.6,2,false,'Stone_VM_Dark','','VM_House_W2'},
  ['VM_House_W2__Stone_VM_Trim']={30.0,10.1,142.0,10.4,5.15,11.4,2,false,'Stone_VM_Trim','','VM_House_W2'},
  ['VM_House_W2__Window_VM_Dark']={30.0,16.12,142.0,12.5,2.3,7.9,2,false,'Window_VM_Dark','','VM_House_W2'},
  ['VM_House_W2__Wood_VM_Plank']={35.05,10.0,142.0,0.5,6.4,4.0,2,false,'Wood_VM_Plank','','VM_House_W2'},
  ['VM_House_W2__Wood_VM_Timber']={30.0,19.709,142.0,12.4,13.419,13.31,2,true,'Wood_VM_Timber','','VM_House_W2'},
  ['VM_Town_Bridge__Stone_Paving_VM']={0.0,6.1,-9.974,18.0,2.628,22.396,2,false,'Stone_Paving_VM','',''},
  ['VM_Town_Bridge__Stone_VM_Base']={0.0,4.65,-10.0,20.6,8.1,22.0,2,true,'Stone_VM_Base','',''},
  ['VM_Town_Bridge__Stone_VM_Dark']={0.0,8.7,-10.0,21.0,2.6,23.8,2,true,'Stone_VM_Dark','',''},
  ['VM_Town_Bridge__Stone_VM_Trim']={0.0,4.6,-12.0,20.6,4.7,15.9,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_Medallion__Metal_VM_Bronze']={-1.342,5.95,49.089,10.444,0.12,10.427,2,false,'Metal_VM_Bronze','',''},
  ['VM_Town_Medallion__Stone_Paving_VM']={0.0,5.69,50.0,15.2,0.4,15.2,2,false,'Stone_Paving_VM','',''},
  ['VM_Town_Medallion__Stone_Paving_VM_Edge']={0.0,5.74,50.0,18.0,0.4,18.0,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_Plaza__Stone_Paving_VM']={0.0,5.86,50.0,72.0,0.4,72.0,2,false,'Stone_Paving_VM','',''},
  ['VM_Town_Plaza__Stone_Paving_VM_Edge']={0.0,6.12,50.0,72.0,0.12,72.0,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_Props__Lantern_Glow']={-17.0,16.4,55.0,151.1,2.5,171.1,2,false,'Lantern_Glow','',''},
  ['VM_Town_Props__Metal_VM_Iron']={-17.0,12.325,55.0,151.6,11.65,171.6,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_Props__Stone_VM_Dark']={-17.0,6.9,55.0,151.2,1.8,171.2,2,true,'Stone_VM_Dark','',''},
  ['VM_Town_Props__Wood_VM_Plank']={16.663,7.7,29.5,95.526,3.4,153.2,2,true,'Wood_VM_Plank','',''},
  ['VM_Town_Props__Wood_VM_Timber']={57.142,7.9,100.07,5.977,3.8,10.044,2,false,'Wood_VM_Timber','',''},
  ['VM_Town_Spawn__Metal_VM_Bronze']={0.0,9.66,94.0,14.0,0.12,14.0,2,true,'Metal_VM_Bronze','',''},
  ['VM_Town_Spawn__Stone_Paving_VM']={0.0,9.45,100.0,39.4,0.3,23.64,2,false,'Stone_Paving_VM','',''},
  ['VM_Town_Spawn__Stone_VM_Base']={0.0,7.35,100.0,40.0,3.9,24.0,2,true,'Stone_VM_Base','',''},
  ['VM_Town_SpawnParapet__Stone_VM_Base']={0.0,10.374,100.0,39.8,1.549,23.8,2,true,'Stone_VM_Base','',''},
  ['VM_Town_SpawnStairs__Stone_VM_Base']={0.0,8.4,84.0,22.4,4.8,8.05,2,true,'Stone_VM_Base','',''},
  ['VM_Town_SpawnStairs__Stone_VM_Trim']={0.0,7.8,84.0,20.0,3.6,8.15,2,false,'Stone_VM_Trim','',''},
  ['VM_Town_Streets__Dirt_VM']={26.958,5.73,114.038,27.182,0.26,7.923,2,false,'Dirt_VM','',''},
  ['VM_Town_Streets__Stone_Paving_VM']={-22.006,6.27,48.387,168.011,1.46,196.773,2,false,'Stone_Paving_VM','',''},
  ['VM_Town_Streets__Stone_Paving_VM_Edge']={-23.511,6.54,55.386,165.002,1.2,182.771,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Frg_Chimney__Forge_Glow_VM']={0.0,92.6,-86.0,8.0,0.4,8.0,3,false,'Forge_Glow_VM','','VM_Forja'},
  ['VM_Frg_Chimney__Stone_VM_Dark']={0.0,50.5,-84.0,13.0,87.0,17.0,3,true,'Stone_VM_Dark','','VM_Forja'},
  ['VM_Frg_Chimney__Stone_VM_Trim']={0.0,34.6,-86.0,14.0,1.2,14.0,3,false,'Stone_VM_Trim','','VM_Forja'},
  ['VM_Frg_Hall__Forge_Glow_VM']={-1.0,10.1,-72.5,6.0,3.0,0.2,3,false,'Forge_Glow_VM','','VM_Forja'},
  ['VM_Frg_Hall__Metal_VM_Bronze']={-1.85,37.9,-48.7,6.3,1.8,0.3,3,false,'Metal_VM_Bronze','','VM_Forja'},
  ['VM_Frg_Hall__Plaster_VM_Cream']={-1.0,42.853,-51.2,34.0,15.307,0.8,3,true,'Plaster_VM_Cream','o','VM_Forja'},
  ['VM_Frg_Hall__Roof_VM_Ridge']={-1.0,51.047,-64.5,1.0,1.0,34.6,3,true,'Roof_VM_Ridge','','VM_Forja'},
  ['VM_Frg_Hall__Roof_VM_Terracotta']={-1.0,42.583,-64.5,37.802,17.416,34.2,3,true,'Roof_VM_Terracotta','o','VM_Forja'},
  ['VM_Frg_Hall__Stone_VM_Base']={-1.0,20.0,-77.6,30.0,26.0,1.2,3,true,'Stone_VM_Base','o','VM_Forja'},
  ['VM_Frg_Hall__Stone_VM_Dark']={-1.0,14.75,-63.175,35.8,15.5,27.75,3,true,'Stone_VM_Dark','o','VM_Forja'},
  ['VM_Frg_Hall__Stone_VM_Trim']={-1.0,6.799,-63.5,30.0,0.399,27.0,3,true,'Stone_VM_Trim','','VM_Forja'},
  ['VM_Frg_Hall__Wood_VM_Plank']={-0.9,37.6,-49.1,12.0,4.4,0.6,3,false,'Wood_VM_Plank','','VM_Forja'},
  ['VM_Frg_Hall__Wood_VM_Timber']={-1.0,28.332,-62.1,35.2,42.665,25.0,3,true,'Wood_VM_Timber','o','VM_Forja'},
  ['VM_Frg_Props__Dirt_VM']={-1.5,8.0,-49.5,54.326,2.6,3.769,3,false,'Dirt_VM','','VM_Forja'},
  ['VM_Frg_Props__Metal_VM_Bronze']={15.2,7.3,-46.0,3.4,0.6,2.2,3,false,'Metal_VM_Bronze','','VM_Forja'},
  ['VM_Frg_Props__Metal_VM_Iron']={-1.0,11.7,-46.4,48.455,1.029,0.5,3,true,'Metal_VM_Iron','','VM_Forja'},
  ['VM_Frg_Props__Wood_VM_Timber']={-1.0,9.4,-46.963,48.2,4.8,1.475,3,true,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Frg_Wheel__Metal_VM_Iron']={34.0,9.4,-66.0,6.0,1.8,1.8,3,false,'Metal_VM_Iron','','VM_Forja'},
  ['VM_Frg_Wheel__Wood_VM_Plank']={36.0,9.4,-66.0,3.0,16.0,16.0,3,false,'Wood_VM_Plank','','VM_Forja'},
  ['VM_Frg_Wheel__Wood_VM_Timber']={36.0,9.4,-66.0,0.8,14.25,14.25,3,false,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Frg_WingE__Plaster_VM_Cream']={22.5,27.042,-70.0,18.6,20.083,38.2,3,true,'Plaster_VM_Cream','','VM_Forja'},
  ['VM_Frg_WingE__Roof_VM_Ridge']={22.5,37.503,-70.0,1.0,1.0,40.6,3,true,'Roof_VM_Ridge','','VM_Forja'},
  ['VM_Frg_WingE__Roof_VM_Terracotta']={22.5,31.117,-70.0,21.736,13.083,40.2,3,true,'Roof_VM_Terracotta','','VM_Forja'},
  ['VM_Frg_WingE__Stone_VM_Base']={22.5,12.0,-70.0,17.0,10.0,36.0,3,true,'Stone_VM_Base','','VM_Forja'},
  ['VM_Frg_WingE__Stone_VM_Trim']={22.5,12.0,-70.0,17.6,9.6,36.6,3,true,'Stone_VM_Trim','','VM_Forja'},
  ['VM_Frg_WingE__Window_VM_Dark']={22.5,21.5,-50.95,13.333,2.8,0.5,3,false,'Window_VM_Dark','','VM_Forja'},
  ['VM_Frg_WingE__Wood_VM_Plank']={22.5,10.5,-51.8,5.0,7.0,0.5,3,false,'Wood_VM_Plank','','VM_Forja'},
  ['VM_Frg_WingE__Wood_VM_Timber']={22.435,21.5,-69.935,19.18,9.0,38.18,3,true,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Frg_WingW__Plaster_VM_Cream']={-25.0,31.84,-70.0,19.6,11.679,38.2,3,true,'Plaster_VM_Cream','','VM_Forja'},
  ['VM_Frg_WingW__Plaster_VM_Ochre']={-25.0,21.5,-70.0,19.6,9.0,37.6,3,true,'Plaster_VM_Ochre','','VM_Forja'},
  ['VM_Frg_WingW__Roof_VM_Ridge']={-25.0,38.099,-70.0,1.0,1.0,40.6,3,true,'Roof_VM_Ridge','','VM_Forja'},
  ['VM_Frg_WingW__Roof_VM_Terracotta_B']={-25.0,31.415,-70.0,22.736,13.678,40.2,3,true,'Roof_VM_Terracotta_B','','VM_Forja'},
  ['VM_Frg_WingW__Stone_VM_Base']={-25.0,12.0,-70.0,18.0,10.0,36.0,3,true,'Stone_VM_Base','','VM_Forja'},
  ['VM_Frg_WingW__Stone_VM_Trim']={-25.0,12.0,-70.0,18.6,9.6,36.6,3,true,'Stone_VM_Trim','','VM_Forja'},
  ['VM_Frg_WingW__Window_VM_Dark']={-25.0,21.5,-50.95,14.0,2.8,0.5,3,false,'Window_VM_Dark','','VM_Forja'},
  ['VM_Frg_WingW__Wood_VM_Plank']={-25.0,10.5,-51.8,5.0,7.0,0.5,3,false,'Wood_VM_Plank','','VM_Forja'},
  ['VM_Frg_WingW__Wood_VM_Timber']={-24.935,21.5,-69.935,20.18,9.0,38.18,3,true,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Rank_Hall__Plaster_VM_Cream']={-89.183,24.864,8.078,46.228,21.728,31.404,4,true,'Plaster_VM_Cream','','VM_Rank'},
  ['VM_Rank_Hall__Roof_VM_Ridge']={-89.183,35.391,8.078,42.767,2.513,19.338,4,true,'Roof_VM_Ridge','','VM_Rank'},
  ['VM_Rank_Hall__Roof_VM_Terracotta']={-89.183,30.382,8.078,49.319,11.822,35.091,4,true,'Roof_VM_Terracotta','','VM_Rank'},
  ['VM_Rank_Hall__Stone_VM_Base']={-89.183,22.364,8.078,41.468,31.128,26.954,4,true,'Stone_VM_Base','','VM_Rank'},
  ['VM_Rank_Hall__Stone_VM_Dark']={-89.183,22.189,8.078,42.257,32.378,27.743,4,true,'Stone_VM_Dark','','VM_Rank'},
  ['VM_Rank_Hall__Stone_VM_Trim']={-89.183,10.6,8.078,41.994,6.15,27.48,4,true,'Stone_VM_Trim','','VM_Rank'},
  ['VM_Rank_Hall__Window_VM_Dark']={-89.183,23.601,8.078,34.298,15.262,26.886,4,true,'Window_VM_Dark','','VM_Rank'},
  ['VM_Rank_Hall__Wood_VM_Plank']={-86.771,10.0,13.626,3.868,6.4,2.053,4,false,'Wood_VM_Plank','','VM_Rank'},
  ['VM_Rank_Hall__Wood_VM_Timber']={-89.183,19.6,8.078,46.499,12.8,31.986,4,true,'Wood_VM_Timber','','VM_Rank'},
  ['VM_Rank_Stage__Cloth_VM_Blue']={-79.694,20.4,29.904,60.646,12.0,26.591,4,true,'Cloth_VM_Blue','','VM_Rank'},
  ['VM_Rank_Stage__Stone_VM_Base']={-81.209,5.4,26.419,61.165,1.2,41.468,4,true,'Stone_VM_Base','','VM_Rank'},
  ['VM_Rank_Stage__Stone_VM_Trim']={-81.209,6.2,26.419,59.849,0.4,40.152,4,true,'Stone_VM_Trim','','VM_Rank'},
  ['VM_Rank_Stage__Wood_VM_Timber']={-78.418,17.4,32.839,56.34,22.0,25.239,4,true,'Wood_VM_Timber','','VM_Rank'},
  ['VM_Shop_Building__Cloth_VM_Red']={60.6,19.9,43.0,2.956,9.201,8.0,4,false,'Cloth_VM_Red','','VM_Shop'},
  ['VM_Shop_Building__Plaster_VM_Cream']={76.0,23.9,43.0,28.0,23.0,26.0,4,true,'Plaster_VM_Cream','o','VM_Shop'},
  ['VM_Shop_Building__Roof_VM_Ridge']={76.0,35.82,43.0,31.2,1.0,1.0,4,true,'Roof_VM_Ridge','','VM_Shop'},
  ['VM_Shop_Building__Roof_VM_Terracotta']={76.0,28.55,43.0,30.8,14.895,29.295,4,true,'Roof_VM_Terracotta','o','VM_Shop'},
  ['VM_Shop_Building__Stone_Paving_VM']={76.0,6.2,43.0,28.0,0.4,26.0,4,false,'Stone_Paving_VM','','VM_Shop'},
  ['VM_Shop_Building__Stone_VM_Base']={76.0,9.4,43.0,28.0,6.0,26.0,4,true,'Stone_VM_Base','o','VM_Shop'},
  ['VM_Shop_Building__Window_VM_Dark']={61.2,10.8,43.0,1.2,4.8,19.4,4,false,'Window_VM_Dark','','VM_Shop'},
  ['VM_Shop_Building__Wood_VM_Plank']={68.5,15.65,43.0,15.0,18.5,12.0,4,false,'Wood_VM_Plank','o','VM_Shop'},
  ['VM_Shop_Building__Wood_VM_Timber']={74.6,14.4,43.0,28.8,16.0,26.45,4,true,'Wood_VM_Timber','o','VM_Shop'},
  ['PORTAL_DemonSlayer_Swirl__P_DS_Swirl']={-182.116,18.4,57.035,4.315,15.0,14.454,5,false,'P_DS_Swirl','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Emblem_Cream']={-182.544,20.044,56.633,14.061,25.028,22.911,5,false,'Emblem_Cream','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Glow']={-181.096,18.4,57.276,4.624,15.5,15.069,5,false,'P_DS_Glow','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Gravel']={-180.012,8.316,57.576,27.543,2.833,31.157,5,false,'P_DS_Gravel','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Iron']={-180.362,20.533,56.166,17.807,25.865,23.426,5,true,'P_DS_Iron','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Lacquer']={-183.774,20.49,56.166,10.981,25.78,23.266,5,true,'P_DS_Lacquer','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__P_DS_Red']={-179.739,18.368,56.122,16.083,19.463,21.556,5,true,'P_DS_Red','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Tsuba__Stone_DS_Rock']={-180.301,9.175,57.496,28.517,4.65,32.591,5,true,'Stone_DS_Rock','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__Bark_Dark']={-181.583,15.814,69.761,3.536,18.217,3.263,5,false,'Bark_Dark','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicMid']={-182.863,23.64,69.186,11.617,6.72,5.553,5,true,'P_DS_GlicMid','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_GlicTip']={-182.19,20.688,69.962,9.863,4.771,3.679,5,false,'P_DS_GlicTip','','PORTAL_DemonSlayer'},
  ['PORTAL_DemonSlayer_Wisteria__P_DS_Glicinia']={-182.303,24.157,69.189,10.662,5.986,6.104,5,true,'P_DS_Glicinia','','PORTAL_DemonSlayer'},
  ['PORTAL_DragonBall_Frame__P_DB_Amber']={-163.741,18.042,113.295,24.065,20.277,16.67,5,true,'P_DB_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Ball_Amber']={-166.548,21.915,106.834,6.593,24.77,18.142,5,true,'P_DB_Ball_Amber','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Blue']={-164.423,10.402,109.979,24.039,8.905,24.674,5,true,'P_DB_Blue','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Floor']={-165.102,7.94,111.098,28.788,0.32,28.588,5,true,'P_DB_Floor','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Gold_Bright']={-166.548,18.41,109.398,16.907,22.221,22.628,5,true,'P_DB_Gold_Bright','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Rim_Glow']={-166.204,18.4,112.258,11.695,15.566,11.151,5,false,'P_DB_Rim_Glow','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_Star_Red']={-167.039,20.826,107.763,9.488,23.722,20.124,5,true,'P_DB_Star_Red','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Frame__P_DB_White']={-165.102,19.817,111.098,28.587,27.734,28.387,5,true,'P_DB_White','','PORTAL_DragonBall'},
  ['PORTAL_DragonBall_Swirl__P_DB_Swirl']={-166.548,18.4,112.621,10.881,15.0,10.325,5,false,'P_DB_Swirl','','PORTAL_DragonBall'},
  ['PORTAL_Naruto_Bandana__Leaf_Pine']={-140.353,7.814,130.077,27.984,2.572,11.211,5,false,'Leaf_Pine','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Metal_Dark']={-139.363,22.057,126.857,27.653,26.687,8.976,5,true,'Metal_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Cloth']={-139.883,22.517,126.512,27.331,21.005,9.493,5,true,'P_Naruto_Cloth','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Lacquer']={-140.283,21.08,123.587,25.437,26.84,15.121,5,true,'P_Naruto_Lacquer','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Paper']={-148.747,9.2,120.207,5.385,3.2,5.883,5,false,'P_Naruto_Paper','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Rim_Glow']={-139.914,18.4,125.745,15.24,15.5,3.843,5,false,'P_Naruto_Rim_Glow','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Steel']={-135.359,19.654,123.606,17.668,26.793,5.419,5,true,'P_Naruto_Steel','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__P_Naruto_Stone']={-140.283,18.475,127.405,18.99,22.15,7.414,5,true,'P_Naruto_Stone','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Dark']={-139.774,16.45,125.11,31.404,19.5,27.756,5,true,'Stone_Dark','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Bandana__Stone_Light']={-139.774,7.641,125.111,31.213,0.761,27.565,5,true,'Stone_Light','','PORTAL_Naruto'},
  ['PORTAL_Naruto_Swirl__P_Naruto_Swirl']={-140.121,18.4,126.905,14.644,15.0,3.712,5,false,'P_Naruto_Swirl','','PORTAL_Naruto'},
  ['PORTAL_OnePiece_Pier__Emblem_Cream']={-165.048,24.174,26.991,7.703,22.253,14.932,5,false,'Emblem_Cream','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Leaf_Palm']={-178.433,18.24,31.937,8.245,1.955,7.973,5,false,'Leaf_Palm','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Metal_Dark']={-165.372,20.444,32.618,29.952,26.208,29.571,5,true,'Metal_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Glow']={-165.998,18.4,31.96,11.587,15.5,11.031,5,false,'P_OP_Glow','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__P_OP_Red']={-162.234,14.2,20.53,2.299,2.7,2.218,5,false,'P_OP_Red','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Rope']={-165.378,18.578,32.612,33.081,22.056,32.958,5,false,'Rope','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Dark']={-165.377,18.2,32.635,32.953,24.0,32.846,5,true,'Wood_Dark','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Light']={-166.548,19.779,31.379,19.38,23.444,18.456,5,true,'Wood_Light','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Pier__Wood_Plank']={-165.235,12.844,32.825,31.322,11.912,31.194,5,true,'Wood_Plank','','PORTAL_OnePiece'},
  ['PORTAL_OnePiece_Swirl__P_OP_Swirl']={-166.548,18.4,31.379,10.881,15.0,10.325,5,false,'P_OP_Swirl','','PORTAL_OnePiece'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_ConcreteDark']={-140.326,18.669,16.546,19.346,19.281,7.328,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Glow']={-140.294,30.02,16.546,19.524,0.46,7.67,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Decal__P_OPM_Yellow']={-140.269,8.35,16.518,21.57,0.8,8.47,5,false,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Swirl__P_OPM_Swirl']={-140.121,18.4,17.095,14.644,15.0,3.712,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_SwirlBack__P_OPM_Swirl']={-140.618,18.4,15.082,14.644,15.0,3.247,5,false,'P_OPM_Swirl','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteDark']={-139.774,20.225,18.89,31.675,26.85,27.723,5,true,'P_OPM_ConcreteDark','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteLight']={-139.774,18.975,18.889,31.413,24.15,26.246,5,true,'P_OPM_ConcreteLight','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_ConcreteMid']={-138.307,18.975,16.255,19.109,22.95,16.32,5,true,'P_OPM_ConcreteMid','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Crater']={-140.483,18.539,16.5,18.579,18.618,7.017,5,true,'P_OPM_Crater','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_DarkGlassT']={-140.294,29.8,16.546,19.481,1.3,7.475,5,false,'P_OPM_DarkGlassT','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Glow']={-140.464,18.4,16.448,16.198,16.24,6.404,5,false,'P_OPM_Glow','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_RebarSteel']={-139.182,17.7,15.234,17.746,18.916,13.32,5,true,'P_OPM_RebarSteel','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Red']={-139.72,30.676,19.201,3.404,3.872,1.854,5,false,'P_OPM_Red','','PORTAL_OnePunchMan'},
  ['PORTAL_OnePunchMan_Wall__P_OPM_Yellow']={-139.774,20.125,18.89,31.751,26.45,27.799,5,true,'P_OPM_Yellow','','PORTAL_OnePunchMan'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Core_Glow']={-177.994,22.695,86.016,10.355,21.506,25.157,5,false,'P_SG_Core_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Lilac_Glow']={-180.624,22.275,86.594,5.122,26.631,17.699,5,false,'P_SG_Lilac_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Glow__P_SG_Moon_Glow']={-178.161,22.278,88.13,10.594,26.737,20.846,5,false,'P_SG_Moon_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Deadwood']={-181.951,11.508,74.096,2.206,8.559,2.436,5,false,'P_SG_Deadwood','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Marble']={-179.003,7.8,86.164,22.272,1.9,29.097,5,true,'P_SG_Marble','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Obsidian']={-182.156,22.38,87.046,10.894,29.46,25.797,5,true,'P_SG_Obsidian','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Rose']={-181.157,14.108,74.241,2.482,5.16,2.928,5,false,'P_SG_Rose','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Silver']={-179.003,22.85,86.164,22.487,30.58,29.311,5,true,'P_SG_Silver','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_SG_Violet']={-180.0,17.03,87.046,14.161,17.86,24.394,5,true,'P_SG_Violet','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_MoonArch__P_Shadow_Glow']={-181.385,18.4,86.806,4.624,15.5,15.069,5,false,'P_Shadow_Glow','','PORTAL_ShadowGarden'},
  ['PORTAL_ShadowGarden_Swirl__P_Shadow_Swirl']={-182.116,18.4,86.965,4.315,15.0,14.454,5,false,'P_Shadow_Swirl','','PORTAL_ShadowGarden'},
  ['VM_Court_Floor__Stone_Paving_VM']={-144.9,6.43,72.0,113.8,1.54,147.576,5,false,'Stone_Paving_VM','',''},
  ['VM_Court_Floor__Stone_VM_Base']={-161.775,6.15,72.0,80.45,1.5,147.976,5,true,'Stone_VM_Base','',''},
  ['VM_Court_Floor__Stone_VM_Dark']={-148.342,19.7,72.0,47.917,1.0,88.615,5,true,'Stone_VM_Dark','',''},
  ['VM_Court_Floor__Stone_VM_Trim']={-148.213,12.43,72.0,47.573,13.54,87.984,5,true,'Stone_VM_Trim','',''},
  ['VM_Exit_Bridge__Lantern_Glow']={24.5,14.6,189.5,64.1,1.5,60.1,6,false,'Lantern_Glow','',''},
  ['VM_Exit_Bridge__Metal_VM_Iron']={24.5,10.0,189.5,63.5,8.0,59.5,6,true,'Metal_VM_Iron','',''},
  ['VM_Exit_Bridge__Stone_Paving_VM']={23.0,5.2,184.0,70.0,1.6,76.0,6,false,'Stone_Paving_VM','',''},
  ['VM_Exit_Bridge__Stone_VM_Base']={23.0,-14.9,183.998,72.4,45.0,76.005,6,true,'Stone_VM_Base','',''},
  ['VM_Exit_Bridge__Stone_VM_Dark']={25.0,-45.4,187.5,55.0,16.0,56.0,6,true,'Stone_VM_Dark','',''},
  ['VM_Exit_Gate__Roof_VM_Ridge']={50.0,22.598,148.0,22.0,1.0,1.0,6,false,'Roof_VM_Ridge','','VM_Exit'},
  ['VM_Exit_Gate__Roof_VM_Terracotta']={50.0,24.955,148.0,32.0,10.089,7.6,6,true,'Roof_VM_Terracotta','','VM_Exit'},
  ['VM_Exit_Gate__Stone_VM_Base']={50.0,14.0,148.0,30.4,16.0,6.0,6,true,'Stone_VM_Base','','VM_Exit'},
  ['VM_Exit_Gate__Stone_VM_Trim']={50.0,22.5,148.0,31.4,1.0,7.0,6,true,'Stone_VM_Trim','','VM_Exit'},
  ['VM_Exit_Gate__Wood_VM_Timber']={50.0,17.95,148.225,20.0,5.1,2.85,6,false,'Wood_VM_Timber','','VM_Exit'},
  ['VM_Water_Canal__Water_VM']={18.5,-13.7,-45.0,300.0,32.6,78.0,7,false,'Water_VM','',''},
  ['VM_Veg_Trees_NE__Bark_VM']={82.598,11.748,-75.148,160.038,9.896,92.432,8,true,'Bark_VM','',''},
  ['VM_Veg_Trees_NE__Leaf_VM_Pine']={88.748,22.879,-75.039,155.117,25.32,100.313,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_Trees_NE__Leaf_VM_Round']={83.177,18.922,-75.372,169.779,14.829,100.519,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_Trees_NW__Bark_VM']={-64.745,11.65,-76.688,117.796,9.7,89.409,8,true,'Bark_VM','',''},
  ['VM_Veg_Trees_NW__Leaf_VM_Pine']={-65.205,23.204,-79.529,128.558,26.02,94.631,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_Trees_NW__Leaf_VM_Round']={-65.631,18.645,-76.387,124.139,14.1,94.913,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_Trees_SE__Bark_VM']={82.009,10.565,75.48,163.17,9.53,134.667,8,true,'Bark_VM','',''},
  ['VM_Veg_Trees_SE__Leaf_VM_Pine']={81.554,21.873,76.394,173.12,25.594,143.269,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_Trees_SE__Leaf_VM_Round']={82.075,17.302,73.003,170.467,14.042,138.137,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_Trees_SW__Bark_VM']={-118.237,10.211,73.858,197.43,8.822,134.177,8,true,'Bark_VM','',''},
  ['VM_Veg_Trees_SW__Leaf_VM_Pine']={-127.357,21.098,72.495,189.077,24.054,140.232,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_Trees_SW__Leaf_VM_Round']={-118.057,16.758,104.748,206.595,12.798,79.044,8,false,'Leaf_VM_Round','',''},
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
  {'COL_CourtPillar_001','Block',{-125.75,13.2,114.941},{0.052,0.0,-0.999},{-0.999,0.0,-0.052},{2.0,2.0,12.0},false},
  {'COL_CourtPillar_002','Block',{-148.187,13.2,109.967},{-0.469,0.0,-0.883},{-0.883,0.0,0.469},{2.0,2.0,12.0},false},
  {'COL_CourtPillar_003','Block',{-164.858,13.2,94.147},{-0.857,0.0,-0.515},{-0.515,0.0,0.857},{2.0,2.0,12.0},false},
  {'COL_CourtPillar_004','Block',{-171.0,13.2,72.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{2.0,2.0,12.0},false},
  {'COL_CourtPillar_005','Block',{-164.858,13.2,49.853},{-0.857,0.0,0.515},{0.515,0.0,0.857},{2.0,2.0,12.0},false},
  {'COL_CourtPillar_006','Block',{-148.187,13.2,34.033},{-0.469,0.0,0.883},{0.883,0.0,0.469},{2.0,2.0,12.0},false},
  {'COL_CourtPillar_007','Block',{-125.75,13.2,29.059},{0.052,0.0,0.999},{0.999,0.0,-0.052},{2.0,2.0,12.0},false},
  {'COL_CourtStep_001','Block',{-126.233,5.1,112.461},{0.044,0.0,0.999},{0.999,0.0,-0.044},{1.2,4.673,3.0},false},
  {'COL_CourtStep_002','Block',{-129.767,5.1,112.461},{-0.044,0.0,0.999},{0.999,0.0,0.044},{1.2,4.673,3.0},false},
  {'COL_CourtStep_003','Block',{-133.286,5.1,112.154},{-0.131,0.0,0.991},{0.991,0.0,0.131},{1.2,4.673,3.0},false},
  {'COL_CourtStep_004','Block',{-136.766,5.1,111.54},{-0.216,0.0,0.976},{0.976,0.0,0.216},{1.2,4.673,3.0},false},
  {'COL_CourtStep_005','Block',{-140.179,5.1,110.626},{-0.301,0.0,0.954},{0.954,0.0,0.301},{1.2,4.673,3.0},false},
  {'COL_CourtStep_006','Block',{-143.499,5.1,109.417},{-0.383,0.0,0.924},{0.924,0.0,0.383},{1.2,4.673,3.0},false},
  {'COL_CourtStep_007','Block',{-146.701,5.1,107.924},{-0.462,0.0,0.887},{0.887,0.0,0.462},{1.2,4.673,3.0},false},
  {'COL_CourtStep_008','Block',{-149.761,5.1,106.157},{-0.537,0.0,0.843},{0.843,0.0,0.537},{1.2,4.673,3.0},false},
  {'COL_CourtStep_009','Block',{-152.655,5.1,104.131},{-0.609,0.0,0.793},{0.793,0.0,0.609},{1.2,4.673,3.0},false},
  {'COL_CourtStep_010','Block',{-155.361,5.1,101.86},{-0.676,0.0,0.737},{0.737,0.0,0.676},{1.2,4.673,3.0},false},
  {'COL_CourtStep_011','Block',{-157.86,5.1,99.361},{-0.737,0.0,0.676},{0.676,0.0,0.737},{1.2,4.673,3.0},false},
  {'COL_CourtStep_012','Block',{-160.131,5.1,96.655},{-0.793,0.0,0.609},{0.609,0.0,0.793},{1.2,4.673,3.0},false},
  {'COL_CourtStep_013','Block',{-162.157,5.1,93.761},{-0.843,0.0,0.537},{0.537,0.0,0.843},{1.2,4.673,3.0},false},
  {'COL_CourtStep_014','Block',{-163.924,5.1,90.701},{-0.887,0.0,0.462},{0.462,0.0,0.887},{1.2,4.673,3.0},false},
  {'COL_CourtStep_015','Block',{-165.417,5.1,87.499},{-0.924,0.0,0.383},{0.383,0.0,0.924},{1.2,4.673,3.0},false},
  {'COL_CourtStep_016','Block',{-166.626,5.1,84.179},{-0.954,0.0,0.301},{0.301,0.0,0.954},{1.2,4.673,3.0},false},
  {'COL_CourtStep_017','Block',{-167.54,5.1,80.766},{-0.976,0.0,0.216},{0.216,0.0,0.976},{1.2,4.673,3.0},false},
  {'COL_CourtStep_018','Block',{-168.154,5.1,77.286},{-0.991,0.0,0.131},{0.131,0.0,0.991},{1.2,4.673,3.0},false},
  {'COL_CourtStep_019','Block',{-168.461,5.1,73.767},{-0.999,0.0,0.044},{0.044,0.0,0.999},{1.2,4.673,3.0},false},
  {'COL_CourtStep_020','Block',{-168.461,5.1,70.233},{-0.999,0.0,-0.044},{-0.044,0.0,0.999},{1.2,4.673,3.0},false},
  {'COL_CourtStep_021','Block',{-168.154,5.1,66.714},{-0.991,0.0,-0.131},{-0.131,0.0,0.991},{1.2,4.673,3.0},false},
  {'COL_CourtStep_022','Block',{-167.54,5.1,63.234},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{1.2,4.673,3.0},false},
  {'COL_CourtStep_023','Block',{-166.626,5.1,59.821},{-0.954,0.0,-0.301},{-0.301,0.0,0.954},{1.2,4.673,3.0},false},
  {'COL_CourtStep_024','Block',{-165.417,5.1,56.501},{-0.924,0.0,-0.383},{-0.383,0.0,0.924},{1.2,4.673,3.0},false},
  {'COL_CourtStep_025','Block',{-163.924,5.1,53.299},{-0.887,0.0,-0.462},{-0.462,0.0,0.887},{1.2,4.673,3.0},false},
  {'COL_CourtStep_026','Block',{-162.157,5.1,50.239},{-0.843,0.0,-0.537},{-0.537,0.0,0.843},{1.2,4.673,3.0},false},
  {'COL_CourtStep_027','Block',{-160.131,5.1,47.345},{-0.793,0.0,-0.609},{-0.609,0.0,0.793},{1.2,4.673,3.0},false},
  {'COL_CourtStep_028','Block',{-157.86,5.1,44.639},{-0.737,0.0,-0.676},{-0.676,0.0,0.737},{1.2,4.673,3.0},false},
  {'COL_CourtStep_029','Block',{-155.361,5.1,42.14},{-0.676,0.0,-0.737},{-0.737,0.0,0.676},{1.2,4.673,3.0},false},
  {'COL_CourtStep_030','Block',{-152.655,5.1,39.869},{-0.609,0.0,-0.793},{-0.793,0.0,0.609},{1.2,4.673,3.0},false},
  {'COL_CourtStep_031','Block',{-149.761,5.1,37.843},{-0.537,0.0,-0.843},{-0.843,0.0,0.537},{1.2,4.673,3.0},false},
  {'COL_CourtStep_032','Block',{-146.701,5.1,36.076},{-0.462,0.0,-0.887},{-0.887,0.0,0.462},{1.2,4.673,3.0},false},
  {'COL_CourtStep_033','Block',{-143.499,5.1,34.583},{-0.383,0.0,-0.924},{-0.924,0.0,0.383},{1.2,4.673,3.0},false},
  {'COL_CourtStep_034','Block',{-140.179,5.1,33.374},{-0.301,0.0,-0.954},{-0.954,0.0,0.301},{1.2,4.673,3.0},false},
  {'COL_CourtStep_035','Block',{-136.766,5.1,32.46},{-0.216,0.0,-0.976},{-0.976,0.0,0.216},{1.2,4.673,3.0},false},
  {'COL_CourtStep_036','Block',{-133.286,5.1,31.846},{-0.131,0.0,-0.991},{-0.991,0.0,0.131},{1.2,4.673,3.0},false},
  {'COL_CourtStep_037','Block',{-129.767,5.1,31.539},{-0.044,0.0,-0.999},{-0.999,0.0,0.044},{1.2,4.673,3.0},false},
  {'COL_CourtStep_038','Block',{-126.233,5.1,31.539},{0.044,0.0,-0.999},{-0.999,0.0,-0.044},{1.2,4.673,3.0},false},
  {'COL_Court_001','Block',{-125.492,5.7,129.445},{0.044,0.0,0.999},{0.999,0.0,-0.044},{33.0,6.843,3.0},false},
  {'COL_Court_002','Block',{-130.508,5.7,129.445},{-0.044,0.0,0.999},{0.999,0.0,0.044},{33.0,6.843,3.0},false},
  {'COL_Court_003','Block',{-135.505,5.7,129.008},{-0.131,0.0,0.991},{0.991,0.0,0.131},{33.0,6.843,3.0},false},
  {'COL_Court_004','Block',{-140.445,5.7,128.137},{-0.216,0.0,0.976},{0.976,0.0,0.216},{33.0,6.843,3.0},false},
  {'COL_Court_005','Block',{-145.291,5.7,126.839},{-0.301,0.0,0.954},{0.954,0.0,0.301},{33.0,6.843,3.0},false},
  {'COL_Court_006','Block',{-150.004,5.7,125.123},{-0.383,0.0,0.924},{0.924,0.0,0.383},{33.0,6.843,3.0},false},
  {'COL_Court_007','Block',{-154.551,5.7,123.003},{-0.462,0.0,0.887},{0.887,0.0,0.462},{33.0,6.843,3.0},false},
  {'COL_Court_008','Block',{-158.895,5.7,120.495},{-0.537,0.0,0.843},{0.843,0.0,0.537},{33.0,6.843,3.0},false},
  {'COL_Court_009','Block',{-163.004,5.7,117.618},{-0.609,0.0,0.793},{0.793,0.0,0.609},{33.0,6.843,3.0},false},
  {'COL_Court_010','Block',{-166.846,5.7,114.393},{-0.676,0.0,0.737},{0.737,0.0,0.676},{33.0,6.843,3.0},false},
  {'COL_Court_011','Block',{-170.393,5.7,110.846},{-0.737,0.0,0.676},{0.676,0.0,0.737},{33.0,6.843,3.0},false},
  {'COL_Court_012','Block',{-173.618,5.7,107.004},{-0.793,0.0,0.609},{0.609,0.0,0.793},{33.0,6.843,3.0},false},
  {'COL_Court_013','Block',{-176.495,5.7,102.895},{-0.843,0.0,0.537},{0.537,0.0,0.843},{33.0,6.843,3.0},false},
  {'COL_Court_014','Block',{-179.003,5.7,98.551},{-0.887,0.0,0.462},{0.462,0.0,0.887},{33.0,6.843,3.0},false},
  {'COL_Court_015','Block',{-181.123,5.7,94.004},{-0.924,0.0,0.383},{0.383,0.0,0.924},{33.0,6.843,3.0},false},
  {'COL_Court_016','Block',{-182.839,5.7,89.291},{-0.954,0.0,0.301},{0.301,0.0,0.954},{33.0,6.843,3.0},false},
  {'COL_Court_017','Block',{-184.137,5.7,84.445},{-0.976,0.0,0.216},{0.216,0.0,0.976},{33.0,6.843,3.0},false},
  {'COL_Court_018','Block',{-185.008,5.7,79.505},{-0.991,0.0,0.131},{0.131,0.0,0.991},{33.0,6.843,3.0},false},
  {'COL_Court_019','Block',{-185.445,5.7,74.508},{-0.999,0.0,0.044},{0.044,0.0,0.999},{33.0,6.843,3.0},false},
  {'COL_Court_020','Block',{-185.445,5.7,69.492},{-0.999,0.0,-0.044},{-0.044,0.0,0.999},{33.0,6.843,3.0},false},
  {'COL_Court_021','Block',{-185.008,5.7,64.495},{-0.991,0.0,-0.131},{-0.131,0.0,0.991},{33.0,6.843,3.0},false},
  {'COL_Court_022','Block',{-184.137,5.7,59.555},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{33.0,6.843,3.0},false},
  {'COL_Court_023','Block',{-182.839,5.7,54.709},{-0.954,0.0,-0.301},{-0.301,0.0,0.954},{33.0,6.843,3.0},false},
  {'COL_Court_024','Block',{-181.123,5.7,49.996},{-0.924,0.0,-0.383},{-0.383,0.0,0.924},{33.0,6.843,3.0},false},
  {'COL_Court_025','Block',{-179.003,5.7,45.449},{-0.887,0.0,-0.462},{-0.462,0.0,0.887},{33.0,6.843,3.0},false},
  {'COL_Court_026','Block',{-176.495,5.7,41.105},{-0.843,0.0,-0.537},{-0.537,0.0,0.843},{33.0,6.843,3.0},false},
  {'COL_Court_027','Block',{-173.618,5.7,36.996},{-0.793,0.0,-0.609},{-0.609,0.0,0.793},{33.0,6.843,3.0},false},
  {'COL_Court_028','Block',{-170.393,5.7,33.154},{-0.737,0.0,-0.676},{-0.676,0.0,0.737},{33.0,6.843,3.0},false},
  {'COL_Court_029','Block',{-166.846,5.7,29.607},{-0.676,0.0,-0.737},{-0.737,0.0,0.676},{33.0,6.843,3.0},false},
  {'COL_Court_030','Block',{-163.004,5.7,26.382},{-0.609,0.0,-0.793},{-0.793,0.0,0.609},{33.0,6.843,3.0},false},
  {'COL_Court_031','Block',{-158.895,5.7,23.505},{-0.537,0.0,-0.843},{-0.843,0.0,0.537},{33.0,6.843,3.0},false},
  {'COL_Court_032','Block',{-154.551,5.7,20.997},{-0.462,0.0,-0.887},{-0.887,0.0,0.462},{33.0,6.843,3.0},false},
  {'COL_Court_033','Block',{-150.004,5.7,18.877},{-0.383,0.0,-0.924},{-0.924,0.0,0.383},{33.0,6.843,3.0},false},
  {'COL_Court_034','Block',{-145.291,5.7,17.161},{-0.301,0.0,-0.954},{-0.954,0.0,0.301},{33.0,6.843,3.0},false},
  {'COL_Court_035','Block',{-140.445,5.7,15.863},{-0.216,0.0,-0.976},{-0.976,0.0,0.216},{33.0,6.843,3.0},false},
  {'COL_Court_036','Block',{-135.505,5.7,14.992},{-0.131,0.0,-0.991},{-0.991,0.0,0.131},{33.0,6.843,3.0},false},
  {'COL_Court_037','Block',{-130.508,5.7,14.555},{-0.044,0.0,-0.999},{-0.999,0.0,0.044},{33.0,6.843,3.0},false},
  {'COL_Court_038','Block',{-125.492,5.7,14.555},{0.044,0.0,-0.999},{-0.999,0.0,-0.044},{33.0,6.843,3.0},false},
  {'COL_Edge_001','Block',{-1.0,8.0,-126.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{251.5,2.0,20.0},false},
  {'COL_Edge_002','Block',{145.0,8.0,-111.0},{0.814,0.0,0.581},{0.581,0.0,-0.814},{53.114,2.0,20.0},false},
  {'COL_Edge_003','Block',{167.0,8.0,-17.0},{0.013,0.0,1.0},{1.0,0.0,-0.013},{159.513,2.0,20.0},false},
  {'COL_Edge_004','Block',{159.0,8.0,90.0},{-0.306,0.0,0.952},{0.952,0.0,0.306},{60.322,2.0,20.0},false},
  {'COL_Edge_005','Block',{127.0,8.0,132.0},{-0.854,0.0,0.52},{0.52,0.0,0.854},{55.352,2.0,20.0},false},
  {'COL_Edge_006','Block',{84.0,8.0,149.5},{-0.985,0.0,0.172},{0.172,0.0,0.985},{42.108,2.0,20.0},false},
  {'COL_Edge_007','Block',{39.0,8.0,153.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.5,2.0,20.0},false},
  {'COL_Edge_008','Block',{62.0,8.0,153.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.5,2.0,20.0},false},
  {'COL_Edge_009','Block',{25.0,8.0,150.0},{-0.974,0.0,-0.225},{-0.225,0.0,0.974},{28.183,2.0,20.0},false},
  {'COL_Edge_010','Block',{-9.0,8.0,144.0},{-0.99,0.0,-0.141},{-0.141,0.0,0.99},{43.926,2.0,20.0},false},
  {'COL_Edge_011','Block',{-57.0,8.0,145.5},{-0.986,0.0,0.164},{0.164,0.0,0.986},{56.245,2.0,20.0},false},
  {'COL_Edge_012','Block',{-117.0,8.0,151.5},{-0.999,0.0,0.045},{0.045,0.0,0.999},{67.568,2.0,20.0},false},
  {'COL_Edge_013','Block',{-173.0,8.0,145.0},{-0.944,0.0,-0.329},{-0.329,0.0,0.944},{50.203,2.0,20.0},false},
  {'COL_Edge_014','Block',{-209.0,8.0,116.5},{-0.536,0.0,-0.845},{-0.845,0.0,0.536},{50.049,2.0,20.0},false},
  {'COL_Edge_015','Block',{-223.0,8.0,68.0},{-0.036,0.0,-0.999},{-0.999,0.0,0.036},{57.536,2.0,20.0},false},
  {'COL_Edge_016','Block',{-216.0,8.0,23.0},{0.426,0.0,-0.905},{-0.905,0.0,-0.426},{39.077,2.0,20.0},false},
  {'COL_Edge_017','Block',{-193.0,8.0,2.0},{0.966,0.0,-0.258},{-0.258,0.0,-0.966},{32.548,2.0,20.0},false},
  {'COL_Edge_018','Block',{-154.5,8.0,-2.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{48.5,2.0,20.0},false},
  {'COL_Edge_019','Block',{-130.0,8.0,-12.0},{0.1,0.0,-0.995},{-0.995,0.0,-0.1},{21.6,2.0,20.0},false},
  {'COL_Edge_020','Block',{-128.5,8.0,-41.0},{0.026,0.0,-1.0},{-1.0,0.0,-0.026},{39.513,2.0,20.0},false},
  {'COL_Edge_021','Block',{-127.0,8.0,-93.0},{0.03,0.0,-1.0},{-1.0,0.0,-0.03},{67.53,2.0,20.0},false},
  {'COL_Forge_001','Block',{-25.0,16.5,-70.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{18.0,36.0,20.0},true},
  {'COL_Forge_002','Block',{22.5,16.5,-70.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{17.0,36.0,20.0},true},
  {'COL_Forge_003','Block',{0.0,50.5,-86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{13.0,13.0,87.0},true},
  {'COL_Forge_004','Block',{-1.0,21.0,-77.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{34.0,1.2,28.0},true},
  {'COL_Forge_005','Block',{-1.0,10.25,-74.75},{1.0,0.0,0.0},{0.0,0.0,-1.0},{13.0,4.5,6.5},true},
  {'COL_Forge_006','Block',{-17.2,21.0,-51.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.4,3.4,28.0},true},
  {'COL_Forge_007','Block',{15.2,21.0,-51.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.4,3.4,28.0},true},
  {'COL_Gate_001','Block',{37.8,14.0,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.0,6.0,16.0},false},
  {'COL_Gate_002','Block',{62.2,14.0,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.0,6.0,16.0},false},
  {'COL_GroundN_001','Block',{-48.65,5.0,-72.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{161.3,107.0,4.0},false},
  {'COL_GroundN_022','Block',{36.0,5.0,-105.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,41.0,4.0},false},
  {'COL_GroundN_024','Block',{83.35,5.0,-72.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{86.7,107.0,4.0},false},
  {'COL_GroundN_035','Block',{130.7,5.0,-70.107},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,102.214,4.0},false},
  {'COL_GroundN_036','Block',{138.7,5.0,-67.25},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,96.5,4.0},false},
  {'COL_GroundN_037','Block',{146.7,5.0,-64.393},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,90.786,4.0},false},
  {'COL_GroundN_038','Block',{154.7,5.0,-61.536},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,85.071,4.0},false},
  {'COL_GroundN_039','Block',{162.7,5.0,-58.679},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,79.357,4.0},false},
  {'COL_Ground_001','Block',{-220.0,4.0,65.327},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,67.654,4.0},false},
  {'COL_Ground_002','Block',{-212.0,4.0,63.135},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,97.269,4.0},false},
  {'COL_Ground_003','Block',{-204.0,4.0,64.659},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,119.451,4.0},false},
  {'COL_Ground_004','Block',{-196.0,4.0,69.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,134.2,4.0},false},
  {'COL_Ground_005','Block',{-188.0,4.0,70.225},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,139.116,4.0},false},
  {'COL_Ground_006','Block',{-180.0,4.0,70.549},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,144.032,4.0},false},
  {'COL_Ground_007','Block',{-172.0,4.0,71.674},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,147.348,4.0},false},
  {'COL_Ground_008','Block',{-164.0,4.0,73.065},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,150.13,4.0},false},
  {'COL_Ground_009','Block',{-156.0,4.0,74.457},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,152.913,4.0},false},
  {'COL_Ground_010','Block',{-148.0,4.0,75.455},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,154.909,4.0},false},
  {'COL_Ground_011','Block',{-140.0,4.0,75.273},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,154.545,4.0},false},
  {'COL_Ground_012','Block',{-132.0,4.0,75.091},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,154.182,4.0},false},
  {'COL_Ground_013','Block',{-124.0,4.0,73.409},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,156.818,4.0},false},
  {'COL_Ground_014','Block',{-116.0,4.0,73.227},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,156.455,4.0},false},
  {'COL_Ground_015','Block',{-108.0,4.0,73.045},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,156.091,4.0},false},
  {'COL_Ground_016','Block',{-100.0,4.0,72.864},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,155.727,4.0},false},
  {'COL_Ground_017','Block',{-92.0,4.0,72.682},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,155.364,4.0},false},
  {'COL_Ground_018','Block',{-84.0,4.0,72.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,155.0,4.0},false},
  {'COL_Ground_019','Block',{-76.0,4.0,71.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,153.667,4.0},false},
  {'COL_Ground_020','Block',{-68.0,4.0,71.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,152.333,4.0},false},
  {'COL_Ground_021','Block',{-60.0,4.0,70.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,151.0,4.0},false},
  {'COL_Ground_022','Block',{-52.0,4.0,69.833},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,149.667,4.0},false},
  {'COL_Ground_023','Block',{-44.0,4.0,69.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,148.333,4.0},false},
  {'COL_Ground_024','Block',{-36.0,4.0,68.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,147.0,4.0},false},
  {'COL_Ground_025','Block',{-28.0,4.0,68.143},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,146.286,4.0},false},
  {'COL_Ground_026','Block',{-20.0,4.0,68.714},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,147.429,4.0},false},
  {'COL_Ground_027','Block',{-12.0,4.0,69.286},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,148.571,4.0},false},
  {'COL_Ground_028','Block',{-4.0,4.0,69.857},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,149.714,4.0},false},
  {'COL_Ground_029','Block',{4.0,4.0,70.429},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,150.857,4.0},false},
  {'COL_Ground_030','Block',{12.0,4.0,71.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,152.0,4.0},false},
  {'COL_Ground_031','Block',{20.0,4.0,71.923},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,153.846,4.0},false},
  {'COL_Ground_032','Block',{28.0,4.0,72.846},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,155.692,4.0},false},
  {'COL_Ground_033','Block',{36.0,4.0,73.769},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,157.538,4.0},false},
  {'COL_Ground_034','Block',{52.0,4.0,74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{24.0,158.0,4.0},false},
  {'COL_Ground_037','Block',{68.0,4.0,73.65},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,157.3,4.0},false},
  {'COL_Ground_038','Block',{76.0,4.0,72.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,155.9,4.0},false},
  {'COL_Ground_039','Block',{84.0,4.0,72.25},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,154.5,4.0},false},
  {'COL_Ground_040','Block',{92.0,4.0,71.55},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,153.1,4.0},false},
  {'COL_Ground_041','Block',{100.0,4.0,70.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,151.7,4.0},false},
  {'COL_Ground_042','Block',{108.0,4.0,69.283},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,148.565,4.0},false},
  {'COL_Ground_043','Block',{116.0,4.0,66.848},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,143.696,4.0},false},
  {'COL_Ground_044','Block',{124.0,4.0,64.413},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,138.826,4.0},false},
  {'COL_Ground_045','Block',{132.0,4.0,61.978},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,133.957,4.0},false},
  {'COL_Ground_046','Block',{140.0,4.0,59.543},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,129.087,4.0},false},
  {'COL_Ground_047','Block',{148.0,4.0,57.109},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,124.217,4.0},false},
  {'COL_Ground_048','Block',{156.0,4.0,47.167},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,104.333,4.0},false},
  {'COL_Ground_049','Block',{164.0,4.0,34.722},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,79.444,4.0},false},
  {'COL_House_001','Block',{-22.0,15.5,6.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{15.8,12.8,21.0},true},
  {'COL_House_002','Block',{22.0,12.5,6.0},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{14.8,12.8,15.0},true},
  {'COL_House_003','Block',{-38.0,15.5,21.0},{-0.607,0.0,0.795},{0.795,0.0,0.607},{15.8,13.8,21.0},true},
  {'COL_House_004','Block',{38.0,12.5,21.0},{-0.607,0.0,-0.795},{-0.795,0.0,0.607},{16.8,13.8,15.0},true},
  {'COL_House_005','Block',{-38.0,12.5,84.0},{0.667,0.0,0.745},{0.745,0.0,-0.667},{15.8,13.8,15.0},true},
  {'COL_House_006','Block',{-22.0,13.5,-29.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{14.8,12.8,15.0},true},
  {'COL_House_007','Block',{21.0,16.5,-29.0},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{13.8,12.8,21.0},true},
  {'COL_House_008','Block',{-46.0,13.5,-44.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{15.8,13.8,15.0},true},
  {'COL_House_009','Block',{50.0,13.5,-34.0},{0.394,0.0,-0.919},{-0.919,0.0,-0.394},{14.8,12.8,15.0},true},
  {'COL_House_010','Block',{62.0,15.5,86.0},{-0.263,0.0,-0.965},{-0.965,0.0,0.263},{15.8,13.8,21.0},true},
  {'COL_House_011','Block',{70.0,12.5,108.0},{0.0,0.0,-1.0},{-1.0,0.0,-0.0},{14.8,12.8,15.0},true},
  {'COL_House_012','Block',{70.0,12.5,130.0},{0.105,0.0,-0.995},{-0.995,0.0,-0.105},{15.8,12.8,15.0},true},
  {'COL_House_013','Block',{33.0,12.5,103.0},{-0.071,0.0,0.997},{0.997,0.0,0.071},{13.8,12.8,15.0},true},
  {'COL_House_014','Block',{32.0,15.5,125.0},{-0.053,0.0,0.999},{0.999,0.0,0.053},{14.8,13.8,21.0},true},
  {'COL_House_015','Block',{30.0,12.5,142.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{12.8,11.8,15.0},true},
  {'COL_House_016','Block',{-58.0,12.5,76.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{15.8,12.8,15.0},true},
  {'COL_House_017','Block',{-80.0,15.5,87.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{14.8,12.8,21.0},true},
  {'COL_House_018','Block',{66.0,12.5,70.0},{0.316,0.0,-0.949},{-0.949,0.0,-0.316},{14.8,12.8,15.0},true},
  {'COL_IsleBridgeBar_001','Block',{58.6,9.0,154.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{16.6,1.2,6.0},false},
  {'COL_IsleBridgeBar_002','Block',{41.4,9.0,154.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{16.6,1.2,6.0},false},
  {'COL_IsleBridgeBar_003','Block',{55.659,9.0,172.22},{-0.316,0.0,0.949},{0.949,0.0,0.316},{16.411,1.2,6.0},false},
  {'COL_IsleBridgeBar_004','Block',{39.341,9.0,166.78},{-0.316,0.0,0.949},{0.949,0.0,0.316},{16.411,1.2,6.0},false},
  {'COL_IsleBridgeBar_005','Block',{45.53,9.0,189.597},{-0.651,0.0,0.759},{0.759,0.0,0.651},{19.039,1.2,6.0},false},
  {'COL_IsleBridgeBar_006','Block',{32.47,9.0,178.403},{-0.651,0.0,0.759},{0.759,0.0,0.651},{19.039,1.2,6.0},false},
  {'COL_IsleBridgeBar_007','Block',{29.872,9.0,203.587},{-0.824,0.0,0.567},{0.567,0.0,0.824},{20.016,1.2,6.0},false},
  {'COL_IsleBridgeBar_008','Block',{20.128,9.0,189.413},{-0.824,0.0,0.567},{0.567,0.0,0.824},{20.016,1.2,6.0},false},
  {'COL_IsleBridgeBar_009','Block',{15.333,9.0,212.928},{-0.864,0.0,0.504},{0.504,0.0,0.864},{14.492,1.2,6.0},false},
  {'COL_IsleBridgeBar_010','Block',{6.667,9.0,198.072},{-0.864,0.0,0.504},{0.504,0.0,0.864},{14.492,1.2,6.0},false},
  {'COL_IsleBridgeBar_011','Block',{7.872,9.0,217.715},{-0.781,0.0,0.625},{0.625,0.0,0.781},{7.003,1.2,6.0},false},
  {'COL_IsleBridgeBar_012','Block',{-2.872,9.0,204.285},{-0.781,0.0,0.625},{0.625,0.0,0.781},{7.003,1.2,6.0},false},
  {'COL_IsleBridge_001','Block',{50.0,4.5,154.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{17.0,16.0,3.0},false},
  {'COL_IsleBridge_002','Block',{47.5,4.5,169.5},{-0.316,0.0,0.949},{0.949,0.0,0.316},{16.811,16.0,3.0},false},
  {'COL_IsleBridge_003','Block',{39.0,4.5,184.0},{-0.651,0.0,0.759},{0.759,0.0,0.651},{19.439,16.0,3.0},false},
  {'COL_IsleBridge_004','Block',{25.0,4.5,196.5},{-0.824,0.0,0.567},{0.567,0.0,0.824},{20.416,16.0,3.0},false},
  {'COL_IsleBridge_005','Block',{11.0,4.5,205.5},{-0.864,0.0,0.504},{0.504,0.0,0.864},{14.892,16.0,3.0},false},
  {'COL_IsleBridge_006','Block',{2.5,4.5,211.0},{-0.781,0.0,0.625},{0.625,0.0,0.781},{7.403,16.0,3.0},false},
  {'COL_IsleLandingBar_001','Block',{-12.6,9.0,217.25},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,9.5,6.0},false},
  {'COL_IsleLandingBar_002','Block',{12.6,9.0,217.25},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,9.5,6.0},false},
  {'COL_IsleLanding_001','Block',{0.0,4.5,217.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{24.0,10.0,3.0},false},
  {'COL_Portal_001','Block',{-139.774,6.9,125.11},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{27.2,22.4,1.4},false},
  {'COL_Portal_002','Block',{-140.283,7.41,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{10.746,10.746,2.42},false},
  {'COL_Portal_003','Block',{-140.283,7.41,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{13.984,5.776,2.42},false},
  {'COL_Portal_004','Block',{-140.283,7.41,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{5.776,13.984,2.42},false},
  {'COL_Portal_005','Block',{-140.283,7.925,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{9.191,9.191,3.45},false},
  {'COL_Portal_006','Block',{-140.283,7.925,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{11.96,4.94,3.45},false},
  {'COL_Portal_007','Block',{-140.283,7.925,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{4.94,11.96,3.45},false},
  {'COL_Portal_008','Block',{-140.283,8.425,127.405},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{11.2,5.2,4.45},false},
  {'COL_Portal_009','Block',{-136.786,10.719,128.18},{0.885,0.423,0.196},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_010','Block',{-133.853,13.067,128.83},{0.614,0.777,0.136},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_011','Block',{-132.221,16.494,129.192},{0.22,0.974,0.049},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_012','Block',{-132.221,20.306,129.192},{-0.22,0.974,-0.049},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_013','Block',{-143.78,10.719,126.63},{0.885,-0.423,0.196},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_014','Block',{-146.713,13.067,125.979},{0.614,-0.777,0.136},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_015','Block',{-148.345,16.494,125.617},{0.22,-0.974,0.049},{-0.216,0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_016','Block',{-148.345,20.306,125.617},{-0.22,-0.974,-0.049},{-0.216,-0.0,0.976},{4.429,3.5,1.85},false},
  {'COL_Portal_017','Block',{-128.763,21.55,129.959},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{2.8,2.8,27.9},false},
  {'COL_Portal_018','Block',{-151.803,21.55,124.851},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{2.8,2.8,27.9},false},
  {'COL_Portal_019','Block',{-127.276,11.182,122.507},{0.876,-0.0,-0.482},{-0.455,0.334,-0.826},{1.8,1.8,9.0},false},
  {'COL_Portal_020','Block',{-148.573,9.2,121.367},{-0.997,0.0,-0.078},{-0.078,0.0,0.997},{5.6,3.6,3.2},false},
  {'COL_Portal_021','Block',{-165.102,7.15,111.098},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{26.2,12.2,1.9},false},
  {'COL_Portal_022','Block',{-165.102,7.15,111.098},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{14.8,21.4,1.9},false},
  {'COL_Portal_023','Block',{-166.548,8.3,112.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{21.6,5.2,1.4},false},
  {'COL_Portal_024','Block',{-166.548,8.3,112.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{17.2,9.4,1.4},false},
  {'COL_Portal_025','Block',{-166.548,8.3,112.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{10.8,12.0,1.4},false},
  {'COL_Portal_026','Block',{-165.102,7.15,111.098},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{22.0,17.4,1.9},false},
  {'COL_Portal_027','Block',{-166.548,8.3,112.621},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{18.4,8.4,1.4},false},
  {'COL_Portal_028','Block',{-161.094,11.878,119.002},{0.572,-0.616,0.542},{-0.688,-0.0,0.725},{2.588,5.451,5.066},false},
  {'COL_Portal_029','Block',{-163.7,8.722,116.477},{0.318,-0.899,0.302},{-0.688,-0.0,0.725},{2.934,5.525,5.144},false},
  {'COL_Portal_030','Block',{-163.799,10.873,115.057},{0.318,-0.899,0.302},{-0.688,-0.0,0.725},{1.85,2.25,4.068},false},
  {'COL_Portal_031','Block',{-173.205,11.878,107.509},{-0.572,-0.616,-0.542},{-0.688,-0.0,0.725},{2.588,5.451,5.066},false},
  {'COL_Portal_032','Block',{-170.548,8.722,109.979},{-0.318,-0.899,-0.302},{-0.688,-0.0,0.725},{2.934,5.525,5.144},false},
  {'COL_Portal_033','Block',{-169.125,10.873,110.003},{-0.318,-0.899,-0.302},{-0.688,0.0,0.725},{1.85,2.25,4.068},false},
  {'COL_Portal_034','Block',{-160.833,12.818,118.009},{0.682,-0.342,0.647},{-0.688,-0.0,0.725},{3.58,2.45,9.829},false},
  {'COL_Portal_035','Block',{-159.854,19.382,118.973},{0.718,0.139,0.682},{-0.688,-0.0,0.725},{3.55,2.3,6.133},false},
  {'COL_Portal_036','Block',{-172.228,12.818,107.196},{-0.682,-0.342,-0.647},{-0.688,0.0,0.725},{3.58,2.45,9.829},false},
  {'COL_Portal_037','Block',{-173.242,19.382,106.269},{-0.718,0.139,-0.682},{-0.688,-0.0,0.725},{3.55,2.3,6.133},false},
  {'COL_Portal_038','Block',{-153.618,9.2,112.07},{0.522,0.0,0.853},{0.853,0.0,-0.522},{4.9,2.0,2.2},false},
  {'COL_Portal_039','Block',{-166.018,9.815,100.441},{-0.522,0.0,-0.853},{-0.853,0.0,0.522},{6.0,2.0,3.53},false},
  {'COL_Portal_040','Block',{-166.496,9.825,112.567},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{13.6,2.35,2.05},false},
  {'COL_Portal_041','Block',{-168.097,11.15,114.253},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{16.0,2.7,4.7},false},
  {'COL_Portal_042','Block',{-167.897,18.4,114.043},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{7.2,2.52,7.2},false},
  {'COL_Portal_043','Block',{-163.63,15.483,117.542},{-0.919,-0.074,-0.386},{0.141,-0.979,-0.149},{5.253,4.687,1.6},false},
  {'COL_Portal_044','Block',{-163.877,19.667,117.645},{-0.921,0.032,-0.388},{-0.061,-0.996,0.065},{5.026,5.279,1.6},false},
  {'COL_Portal_045','Block',{-171.615,15.483,109.965},{-0.434,0.074,-0.898},{0.141,-0.979,-0.149},{5.253,4.687,1.6},false},
  {'COL_Portal_046','Block',{-171.705,19.667,110.217},{-0.435,-0.032,-0.9},{-0.061,-0.996,0.065},{5.026,5.279,1.6},false},
  {'COL_Portal_047','Block',{-179.024,6.925,86.15},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{27.2,14.3,1.45},false},
  {'COL_Portal_048','Block',{-178.976,6.925,86.137},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{23.36,17.4,1.45},false},
  {'COL_Portal_049','Block',{-178.783,7.2,86.083},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{17.2,9.4,2.0},false},
  {'COL_Portal_050','Block',{-178.205,7.2,85.923},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{14.32,10.6,2.0},false},
  {'COL_Portal_051','Block',{-179.458,7.475,86.271},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{14.0,6.0,2.55},false},
  {'COL_Portal_052','Block',{-178.976,7.475,86.137},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{11.6,7.0,2.55},false},
  {'COL_Portal_053','Block',{-179.265,13.95,97.632},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{3.8,4.3,13.5},false},
  {'COL_Portal_054','Block',{-185.144,13.95,76.432},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{3.8,4.3,13.5},false},
  {'COL_Portal_055','Block',{-180.454,9.775,93.344},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{5.1,2.0,4.25},false},
  {'COL_Portal_056','Block',{-179.946,16.3,95.175},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.3,2.0,8.8},false},
  {'COL_Portal_057','Block',{-183.955,9.775,80.72},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{5.1,2.0,4.25},false},
  {'COL_Portal_058','Block',{-184.462,16.3,78.889},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.3,2.0,8.8},false},
  {'COL_Portal_059','Block',{-183.168,18.4,87.299},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{10.7,2.1,10.7},false},
  {'COL_Portal_060','Block',{-183.168,18.4,87.299},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{13.9,2.1,5.74},false},
  {'COL_Portal_061','Block',{-183.168,18.4,87.299},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{5.74,2.1,13.9},false},
  {'COL_Portal_062','Block',{-174.27,7.65,97.492},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{2.1,2.1,1.9},false},
  {'COL_Portal_063','Block',{-174.27,10.625,97.492},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.0,1.0,4.05},false},
  {'COL_Portal_064','Block',{-182.151,8.775,73.942},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.6,1.6,4.15},false},
  {'COL_Portal_065','Block',{-180.845,11.8,74.721},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{1.8,1.7,1.9},false},
  {'COL_Portal_066','Block',{-172.568,6.925,59.64},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{6.0,5.7,1.45},false},
  {'COL_Portal_067','Block',{-175.892,7.2,58.718},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{5.2,1.2,2.0},false},
  {'COL_Portal_068','Block',{-176.904,7.7,58.438},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{4.6,1.1,3.0},false},
  {'COL_Portal_069','Block',{-174.707,9.775,64.547},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,1.1,5.15},false},
  {'COL_Portal_070','Block',{-171.874,9.775,54.333},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,1.1,5.15},false},
  {'COL_Portal_071','Block',{-182.327,12.7,70.321},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.7,1.7,11.0},false},
  {'COL_Portal_072','Block',{-182.686,8.2,56.834},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{10.0,8.3,4.0},false},
  {'COL_Portal_073','Block',{-184.781,8.0,63.829},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{4.6,8.0,3.6},false},
  {'COL_Portal_074','Block',{-185.701,8.35,66.583},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,7.7,4.3},false},
  {'COL_Portal_075','Block',{-186.056,8.8,67.678},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,7.0,5.2},false},
  {'COL_Portal_076','Block',{-186.219,7.975,68.826},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,10.1,3.55},false},
  {'COL_Portal_077','Block',{-184.181,13.9,65.033},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.2,1.9,3.0},false},
  {'COL_Portal_078','Block',{-184.475,19.05,66.093},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.8,1.9,7.3},false},
  {'COL_Portal_079','Block',{-187.46,11.8,64.694},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{3.5,2.1,4.0},false},
  {'COL_Portal_080','Block',{-180.88,8.0,49.76},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{4.6,8.0,3.6},false},
  {'COL_Portal_081','Block',{-180.249,8.35,46.925},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,7.7,4.3},false},
  {'COL_Portal_082','Block',{-179.99,8.8,45.803},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.1,7.0,5.2},false},
  {'COL_Portal_083','Block',{-179.538,7.975,44.735},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{1.2,10.1,3.55},false},
  {'COL_Portal_084','Block',{-179.745,13.9,49.037},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.2,1.9,3.0},false},
  {'COL_Portal_085','Block',{-179.451,19.05,47.977},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{2.8,1.9,7.3},false},
  {'COL_Portal_086','Block',{-182.73,11.8,47.638},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{3.5,2.1,4.0},false},
  {'COL_Portal_087','Block',{-178.157,7.95,58.09},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{23.8,1.7,3.5},false},
  {'COL_Portal_088','Block',{-187.408,7.975,55.525},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{23.8,2.1,3.55},false},
  {'COL_Portal_089','Block',{-184.228,18.2,56.407},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{15.2,3.9,16.0},false},
  {'COL_Portal_090','Block',{-165.102,7.0,32.902},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{22.8,21.4,1.6},false},
  {'COL_Portal_091','Block',{-173.734,8.6,41.094},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.4,21.4,2.8},false},
  {'COL_Portal_092','Block',{-156.47,8.6,24.711},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.4,21.4,2.8},false},
  {'COL_Portal_093','Block',{-166.548,7.55,31.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{12.16,12.16,2.5},false},
  {'COL_Portal_094','Block',{-166.548,7.55,31.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{15.824,6.536,2.5},false},
  {'COL_Portal_095','Block',{-166.548,7.55,31.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{6.536,15.824,2.5},false},
  {'COL_Portal_096','Block',{-166.548,7.95,31.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{9.332,9.332,3.3},false},
  {'COL_Portal_097','Block',{-166.548,7.95,31.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{12.144,5.016,3.3},false},
  {'COL_Portal_098','Block',{-166.548,7.95,31.379},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{5.016,12.144,3.3},false},
  {'COL_Portal_099','Block',{-167.301,13.0,43.95},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{5.0,1.4,10.5},false},
  {'COL_Portal_100','Block',{-162.714,18.7,20.02},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.4,1.4,23.0},false},
  {'COL_Portal_101','Block',{-153.556,9.3,32.285},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{3.6,2.8,3.0},false},
  {'COL_Portal_102','Block',{-176.284,9.1,30.417},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{2.4,2.4,2.6},false},
  {'COL_Portal_103','Block',{-156.295,9.1,28.818},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{2.4,2.4,2.6},false},
  {'COL_Portal_104','Block',{-178.75,11.2,32.757},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{1.6,1.6,8.0},false},
  {'COL_Portal_110','Block',{-167.959,17.8,29.892},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{15.2,0.4,16.4},false},
  {'COL_Portal_111','Block',{-139.774,6.95,18.89},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{27.6,22.4,1.5},false},
  {'COL_Portal_112','Block',{-139.45,7.925,20.354},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{11.6,5.8,1.45},false},
  {'COL_Portal_113','Block',{-139.731,8.4,19.085},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{10.0,3.2,2.4},false},
  {'COL_Portal_114','Block',{-148.91,19.275,18.456},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.65,4.2,24.15},false},
  {'COL_Portal_115','Block',{-131.678,19.275,14.636},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.65,4.2,24.15},false},
  {'COL_Portal_116','Block',{-140.294,27.775,16.546},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{14.0,3.2,7.15},false},
  {'COL_Portal_117','Block',{-140.359,8.9,16.253},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{7.2,2.6,3.4},false},
  {'COL_Portal_118','Block',{-145.533,9.5,17.401},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.4,2.6,4.6},false},
  {'COL_Portal_119','Block',{-135.184,9.5,15.106},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.4,2.6,4.6},false},
  {'COL_Portal_120','Block',{-140.543,17.4,15.424},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{12.0,0.9,13.6},false},
  {'COL_Portal_121','Ramp',{-138.128,8.298,12.918},{0.175,0.588,0.79},{0.976,-0.0,-0.216},{2.08,3.4,0.8},false},
  {'COL_Portal_122','Block',{-135.308,8.119,10.259},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{3.214,3.004,1.839},false},
  {'COL_Portal_123','Block',{-135.669,9.392,9.847},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{1.212,1.948,0.768},false},
  {'COL_Portal_124','Block',{-139.443,7.912,9.297},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{2.478,2.247,1.425},false},
  {'COL_Portal_125','Ramp',{-131.845,8.181,17.234},{-0.15,0.719,-0.678},{-0.976,-0.0,0.216},{1.56,2.2,0.8},false},
  {'COL_Portal_126','Block',{-129.696,7.916,18.979},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{1.515,1.426,1.433},false},
  {'COL_Portal_127','Block',{-130.265,8.824,18.774},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.559,0.477,0.698},false},
  {'COL_Portal_128','Block',{-131.97,7.715,20.8},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.898,0.966,1.03},false},
  {'COL_Portal_129','Block',{-147.024,8.675,27.769},{0.804,0.0,-0.595},{-0.595,0.0,-0.804},{4.4,1.2,2.95},false},
  {'COL_Portal_130','Block',{-146.686,8.425,23.29},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.8,0.8,2.45},false},
  {'COL_Portal_131','Block',{-148.063,8.279,22.161},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{0.68,0.68,2.158},false},
  {'COL_Race_001','Block',{32.5,10.0,-51.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,67.0,6.0},false},
  {'COL_Race_002','Block',{39.5,10.0,-51.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,67.0,6.0},false},
  {'COL_Race_003','Block',{36.0,10.0,-84.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,1.0,6.0},false},
  {'COL_RankHall_001','Block',{-89.183,16.0,8.078},{-0.917,0.0,0.399},{0.399,0.0,0.917},{41.8,13.8,22.0},true},
  {'COL_Rank_001','Block',{-81.209,4.9,26.419},{-0.917,0.0,0.399},{0.399,0.0,0.917},{58.0,20.0,3.0},false},
  {'COL_ShopFloor_001','Block',{76.0,4.9,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,26.0,3.0},false},
  {'COL_Shop_001','Block',{62.5,14.4,35.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,10.0,16.0},true},
  {'COL_Shop_002','Block',{62.5,14.4,51.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,10.0,16.0},true},
  {'COL_Shop_003','Block',{89.5,14.4,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,26.0,16.0},true},
  {'COL_Shop_004','Block',{76.0,14.4,30.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.0,16.0},true},
  {'COL_Shop_005','Block',{76.0,14.4,55.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.0,16.0},true},
  {'COL_Shop_006','Block',{62.5,18.9,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,6.0,7.0},true},
  {'COL_Shop_007','Block',{76.0,23.4,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,26.0,2.0},true},
  {'COL_Shop_008','Block',{75.0,8.2,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,12.0,3.6},false},
  {'COL_Shop_009','Block',{88.25,11.4,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.5,20.0,10.0},true},
  {'COL_Shop_010','Block',{61.1,10.1,36.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,7.2,7.4},true},
  {'COL_Shop_011','Block',{61.1,10.1,49.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,7.2,7.4},true},
  {'COL_SpawnPar_001','Block',{-13.677,11.3,88.6},{-1.0,0.0,0.0},{0.0,0.0,1.0},{5.626,1.0,3.4},false},
  {'COL_SpawnPar_002','Block',{-17.945,11.3,90.025},{-0.714,0.0,0.7},{0.7,0.0,0.714},{4.073,1.0,3.4},false},
  {'COL_SpawnPar_003','Block',{-19.4,11.3,100.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{17.1,1.0,3.4},false},
  {'COL_SpawnPar_004','Block',{-17.945,11.3,109.975},{0.714,0.0,0.7},{0.7,0.0,-0.714},{4.073,1.0,3.4},false},
  {'COL_SpawnPar_005','Block',{0.0,11.3,111.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{32.98,1.0,3.4},false},
  {'COL_SpawnPar_006','Block',{17.945,11.3,109.975},{0.714,0.0,-0.7},{-0.7,0.0,-0.714},{4.073,1.0,3.4},false},
  {'COL_SpawnPar_007','Block',{19.4,11.3,100.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{17.1,1.0,3.4},false},
  {'COL_SpawnPar_008','Block',{17.945,11.3,90.025},{-0.714,0.0,-0.7},{-0.7,0.0,0.714},{4.073,1.0,3.4},false},
  {'COL_SpawnPar_009','Block',{13.677,11.3,88.6},{-1.0,0.0,0.0},{0.0,0.0,1.0},{5.626,1.0,3.4},false},
  {'COL_Spawn_001','Block',{-18.0,7.7,100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,22.0,3.8},false},
  {'COL_Spawn_002','Block',{0.0,7.7,100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{32.0,24.0,3.8},false},
  {'COL_Spawn_010','Block',{18.0,7.7,100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,22.0,3.8},false},
  {'COL_Spawn_011','Ramp',{0.0,7.344,83.405},{-0.0,0.41,0.912},{1.0,0.0,0.0},{8.773,20.0,1.0},false},
  {'COL_Spawn_012','Block',{0.0,9.1,87.75},{-0.0,0.0,1.0},{1.0,0.0,0.0},{1.1,20.0,1.0},false},
  {'COL_Spawn_013','Ramp',{-10.6,8.918,83.497},{-0.0,0.41,0.912},{1.0,0.0,0.0},{8.773,1.2,5.5},false},
  {'COL_Spawn_014','Ramp',{10.6,8.918,83.497},{-0.0,0.41,0.912},{1.0,0.0,0.0},{8.773,1.2,5.5},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'DOOR_Shop',{62.0,6.4,43.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{['largura']=6,['altura']=9,['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'ForgeChimney',{0.0,94.0,-86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='AudioWorld: ambiente da chamine',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'IGNIS_Anvil',{-0.9,7.0,-55.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='bigorna do golem (colisao da sessao Ignis)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'INTERACT_Ignis',{-0.9,13.79,-60.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['prompt_range']=18,['server_range']=22,['alvo']='belly (prompt do Main)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'INTERACT_Shop',{78.0,9.6,43.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{['prompt_range']=12,['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'ISLE_LINK_Area1',{0.0,6.0,222.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='fim da ponte = borda da praca de chegada da Area 1 (z 222, piso 6)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'LAYOUT_Ignis',{-0.9,10.5,-46.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['lobbylayout']='Ignis',['nota']='posicao de HRP do Core.LobbyLayout',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'LAYOUT_PortalIsland',{-112.0,9.5,72.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{['lobbylayout']='PortalIsland',['nota']='posicao de HRP do Core.LobbyLayout',['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'LAYOUT_Shop',{69.0,9.9,43.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{['lobbylayout']='Shop',['nota']='posicao de HRP do Core.LobbyLayout',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'LAYOUT_ShopFacing',{78.0,9.9,43.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{['lobbylayout']='ShopFacing',['nota']='posicao de HRP do Core.LobbyLayout',['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'LAYOUT_Spawn',{0.0,12.9,94.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['lobbylayout']='Spawn',['nota']='posicao de HRP do Core.LobbyLayout',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'LETREIRO_Ignis',{-0.9,20.0,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['alvo']='LetreiroIgnis',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'LOBBY_GATE_Ilha1',{50.0,6.0,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='portao da ponte da Ilha 1 (Vila da Folha)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'MAILBOX_Correio',{-14.0,9.6,100.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{['alvo']='workspace.MailBox',['prompt']='Enviar Feedback',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'NPC_Ignis',{-0.9,7.0,-60.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['npc']='Ignis',['alvo']='workspace.NPCs.Ignis (Root)',['nota']='Root (-0,9; 7; -60,7) olhando +Z; bigorna a +5 em Z',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'NPC_Shop',{78.0,6.4,43.0},{0.0,0.0,1.0},{1.0,0.0,-0.0},{['npc']='npc vendedor ',['prompt']='LojaPrompt (Comprar, 12/18)',['face_x']=-1.0,['face_z']=0.0,['yaw_deg']=90.0}},
  {'PADLOJA_Shop',{69.0,6.45,43.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{['alvo']='workspace.LojaMochilas.PadLoja (10x0,2x10, so marca)',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'PLAYER_INTERACT_Ignis',{-0.9,7.0,-44.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['note']='chao livre e plano na cota 7 de z -52,7 a -40 (envoltoria do golem)',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'PLAYER_INTERACT_Shop',{69.0,6.4,43.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'PORTAL_DemonSlayer',{-181.385,18.4,57.195},{0.267,0.0,-0.964},{-0.964,0.0,-0.267},{['destino']='DemonSlayer',['raio']=7.5,['touch']=true,['vm_portal']='DemonSlayer'}},
  {'PORTAL_DragonBall',{-166.135,18.4,112.186},{-0.725,0.0,-0.688},{-0.688,0.0,0.725},{['destino']='DragonBall',['raio']=7.5,['touch']=true,['vm_portal']='DragonBall'}},
  {'PORTAL_Naruto',{-139.991,18.4,126.087},{-0.976,0.0,-0.216},{-0.216,0.0,0.976},{['destino']='Naruto',['raio']=7.5,['touch']=true,['vm_portal']='Naruto'}},
  {'PORTAL_OnePiece',{-166.135,18.4,31.814},{0.725,0.0,-0.688},{-0.688,0.0,-0.725},{['destino']='OnePiece',['raio']=7.5,['touch']=true,['vm_portal']='OnePiece'}},
  {'PORTAL_OnePunchMan',{-139.991,18.4,17.913},{0.976,0.0,-0.216},{-0.216,0.0,-0.976},{['destino']='OnePunchMan',['raio']=7.5,['touch']=true,['vm_portal']='OnePunchMan'}},
  {'PORTAL_ShadowGarden',{-181.385,18.4,86.805},{-0.267,0.0,-0.964},{-0.964,0.0,0.267},{['destino']='ShadowGarden',['raio']=7.5,['touch']=true,['vm_portal']='ShadowGarden'}},
  {'REBIRTH_Spot',{-26.0,6.0,74.0},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{['alvo']='workspace.Rebirth (sugestao: canto sudoeste da praca)',['face_x']=0.7071,['face_z']=-0.7071,['yaw_deg']=-45.0}},
  {'SPAWNLOBBY_Part',{0.0,9.7,94.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['alvo']='workspace[\'Mystical Spawn Point\'].SpawnLobby (Position da placa 10x0,2x10)',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'SPAWN_Lobby',{0.0,9.6,94.0},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['kind']='spawn',['note']='terraco do spawn, olhando a forja (-Z)',['face_x']=0.0,['face_z']=-1.0,['yaw_deg']=0.0}},
  {'TOP100_Origin',{-84.0,6.4,20.0},{0.917,0.0,-0.399},{-0.399,0.0,-0.917},{['alvo']='LOBBY_FORJA.GlobalTop100 (OriginCF)',['nota']='quadros em z 0 e podios em z 9,5 do referencial local',['face_x']=0.3987,['face_z']=0.9171,['yaw_deg']=-156.5}},
  {'VFX_Chimney_Smoke_Emitter',{0.0,94.5,-86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke',['rate']=6,['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'VFX_Hearth_Fire',{-0.9,9.5,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'VFX_TripHammer',{24.0,8.0,-70.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{['anim']='martelo-pilao movido pela roda (V3)',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0}},
  {'VFX_Waterwheel_Rotate',{36.0,9.4,-66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['axis']='X',['rpm']=6,['raio']=7.5,['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
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
  {'L_P_DemonSlayer_Lamp_1','POINT',{-173.506,10.44,63.583},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Lamp_2','POINT',{-171.341,10.44,55.778},{255,137,97},4.5,0.31,false,false},
  {'L_P_DemonSlayer_Pad','POINT',{-175.218,11.7,58.905},{255,129,129},12.6,0.71,false,false},
  {'L_P_DragonBall_Pad','POINT',{-161.729,11.7,107.543},{97,179,255},12.6,0.71,false,false},
  {'L_P_Naruto_Pad','POINT',{-138.606,11.7,119.839},{255,196,118},12.6,0.71,false,false},
  {'L_P_OnePiece_Pad','POINT',{-161.729,11.7,36.457},{137,196,255},12.6,0.71,false,false},
  {'L_P_OnePunchMan_Pad','POINT',{-138.606,11.7,24.162},{255,229,144},12.6,0.71,false,false},
  {'L_P_ShadowGarden_Candles','POINT',{-173.151,17.41,96.663},{203,137,255},9.5,0.49,false,false},
  {'L_P_ShadowGarden_Moon','POINT',{-178.96,30.02,85.821},{196,129,255},10.7,0.56,false,false},
  {'L_P_ShadowGarden_Pad','POINT',{-175.218,11.7,85.095},{206,137,255},12.6,0.71,false,false},
  {'L_Portal_DemonSlayer','POINT',{-179.072,18.4,57.836},{255,129,129},14.0,1.0,false,false},
  {'L_Portal_DragonBall','POINT',{-164.483,18.4,110.445},{97,179,255},14.0,1.0,false,false},
  {'L_Portal_Naruto','POINT',{-139.471,18.4,123.744},{255,196,118},14.0,1.0,false,false},
  {'L_Portal_OnePiece','POINT',{-164.483,18.4,33.555},{137,196,255},14.0,1.0,false,false},
  {'L_Portal_OnePunchMan','POINT',{-139.471,18.4,20.256},{255,229,144},14.0,1.0,false,false},
  {'L_Portal_ShadowGarden','POINT',{-179.072,18.4,86.164},{206,137,255},14.0,1.0,false,false},
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
  {'SPAWN_Lobby',{0.0,9.6,94.0}},
  {'SAFE_Spawn',{0.0,9.6,98.0}},
  {'SAFE_Praca',{0.0,6.0,66.0}},
  {'SAFE_PracaOeste',{-26.0,6.0,50.0}},
  {'SAFE_RuaSul',{0.0,6.0,8.0}},
  {'SAFE_RuaNorte',{0.0,7.0,-28.0}},
  {'SAFE_Largo',{0.0,7.0,-42.0}},
  {'SAFE_Loja',{48.0,6.0,43.0}},
  {'SAFE_Ranking',{-60.0,6.0,46.0}},
  {'SAFE_RuaOeste',{-84.0,6.0,64.0}},
  {'SAFE_Patio',{-118.0,6.0,72.0}},
  {'SAFE_RuaSE',{48.0,6.0,108.0}},
  {'SAFE_Portao',{50.0,6.0,140.0}},
  {'SAFE_Ponte1',{45.0,6.0,177.0}},
  {'SAFE_Ponte2',{17.0,6.0,202.0}},
  {'SAFE_Portal1',{-138.173,7.6,117.886}},
  {'SAFE_Portal2',{-160.353,8.1,106.093}},
  {'SAFE_Portal3',{-173.291,8.2,84.56}},
  {'SAFE_Portal4',{-173.291,7.65,59.44}},
  {'SAFE_Portal5',{-160.353,7.8,37.907}},
  {'SAFE_Portal6',{-138.173,7.7,26.114}},
}
do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'
  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false
  v.Size = Vector3.new(470,4,420); v.Position = Vector3.new(-28.0,-25.0,48.0) + ROOT_OFFSET
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
-- gerado por montar_lobby_vila_medieval.lua (export_roblox.py) - nao editar a mao
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
  Lg.GeographicLatitude = 53.448
  Lg.ClockTime = 13.929
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
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (-0.42, 0.76, 0.50) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
-- ================= CONTRATO DO JOGO (lobby Vila Medieval) =================
-- Santuario.Portal1..6: Model com Disco (gameplay, invisivel, sem colisao, CanTouch) e atributo AreaId; o Core.Main
-- liga o Touched (Santuario precisa ser filho DIRETO de LOBBY_FORJA). O AudioWorld reconhece Portal%d em Santuario.
local PORTAIS = {
  {1, 'Naruto', 1, Vector3.new(-139.709, 18.400, 124.818), Vector3.new(0.2164, 0, -0.9763)},
  {2, 'DragonBall', 2, Vector3.new(-165.240, 18.400, 111.243), Vector3.new(0.6884, 0, -0.7254)},
  {3, 'ShadowGarden', 3, Vector3.new(-180.132, 18.400, 86.458), Vector3.new(0.9636, 0, -0.2672)},
  {4, 'DemonSlayer', 4, Vector3.new(-180.132, 18.400, 57.542), Vector3.new(0.9636, 0, 0.2672)},
  {5, 'OnePiece', 5, Vector3.new(-165.240, 18.400, 32.757), Vector3.new(0.6884, 0, 0.7254)},
  {6, 'OnePunchMan', 6, Vector3.new(-139.709, 18.400, 19.182), Vector3.new(0.2164, 0, 0.9763)},
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
-- LobbyRevision (o LobbyServices exige o filho): mantem o existente, so marca a revisao
do local r = root:FindFirstChild('LobbyRevision') or Instance.new('Folder'); r.Name = 'LobbyRevision'
  r:SetAttribute('VilaMedieval', EXPORT_ID); r.Parent = root end
-- GlobalTop100 (pódios Forca/Moedas): a GEOMETRIA e do Top100Builder/Controller; aqui so a ORIGEM nova (palco do
-- ranking, oeste). Se o modelo ja existe dentro do LOBBY_FORJA, e levado inteiro para la (PivotTo).
local TOP100_CF = CFrame.lookAt(Vector3.new(-84.000, 6.400, 20.000), Vector3.new(-83.601, 6.400, 20.917)) * CFrame.Angles(0, math.pi, 0)
root:SetAttribute('Top100Origin', TOP100_CF + ROOT_OFFSET)
do local t = root:FindFirstChild('GlobalTop100')
  if t and t:IsA('Model') then t:PivotTo(TOP100_CF + ROOT_OFFSET); print('GlobalTop100 levado ao palco do ranking')
  else print('GlobalTop100 ausente: construa com Top100Builder.Build(root, {OriginCF = root:GetAttribute("Top100Origin")})') end end
-- valores NOVOS do ServerScriptService.Core.LobbyLayout (o lead troca no Studio) e posicoes dos objetos soltos
--   Spawn        = Vector3.new(0.0, 12.9, 94.0)
--   Shop         = Vector3.new(69.0, 9.9, 43.0)
--   ShopFacing   = Vector3.new(78.0, 9.9, 43.0)
--   Ignis        = Vector3.new(-0.9, 10.5, -46.0)
--   PortalIsland = Vector3.new(-112.0, 9.5, 72.0)
--   SpawnLobby (placa) = (0.0, 9.7, 94.0); MailBox = (-14.0, 9.6, 100.0); Ignis Root (-0.9, 7, -60.7) olhando +Z
print(string.format('CONTRATO: Santuario com %d portais, LobbyRevision %s', #PORTAIS, EXPORT_ID))

print(string.format('LOBBY_FORJA montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
