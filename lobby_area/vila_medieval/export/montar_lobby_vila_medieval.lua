-- montar_lobby_vila_medieval.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 6c3d0295
-- 1) Importe os FBX LOBBY_VM_*_6c3d02.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador
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
local EXPORT_ID = '6c3d0295'
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
  ['Cliff_VM_Rock'] = {c = Color3.fromRGB(134,128,122), m = Enum.Material.Slate, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VM_Blue'] = {c = Color3.fromRGB(56,86,150), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VM_Cream'] = {c = Color3.fromRGB(232,220,196), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Cloth_VM_Red'] = {c = Color3.fromRGB(176,54,44), m = Enum.Material.Fabric, t = 0.0, s = true, x = nil, w = nil},
  ['Emblem_Cream'] = {c = Color3.fromRGB(237,231,215), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_VM_Pink'] = {c = Color3.fromRGB(232,128,168), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_VM_Red'] = {c = Color3.fromRGB(214,62,58), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Flower_VM_Yellow'] = {c = Color3.fromRGB(240,196,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Forge_Glow_VM'] = {c = Color3.fromRGB(255,128,40), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_VM'] = {c = Color3.fromRGB(98,168,62), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Grass_VM_Hill'] = {c = Color3.fromRGB(112,160,72), m = Enum.Material.Grass, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Palm'] = {c = Color3.fromRGB(110,166,94), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_Pine'] = {c = Color3.fromRGB(45,111,63), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Light'] = {c = Color3.fromRGB(132,186,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Pine'] = {c = Color3.fromRGB(46,104,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Round'] = {c = Color3.fromRGB(84,150,62), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Leaf_VM_Tuft'] = {c = Color3.fromRGB(92,168,56), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VM_Bronze'] = {c = Color3.fromRGB(176,138,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VM_Iron'] = {c = Color3.fromRGB(70,70,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_VM_Steel'] = {c = Color3.fromRGB(158,164,172), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
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
  ['Roof_VM_Terracotta'] = {c = Color3.fromRGB(200,110,60), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta_B'] = {c = Color3.fromRGB(182,96,54), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Roof_VM_Terracotta_C'] = {c = Color3.fromRGB(214,126,72), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Rope'] = {c = Color3.fromRGB(190,172,140), m = Enum.Material.Fabric, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_DS_Rock'] = {c = Color3.fromRGB(92,92,100), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Light'] = {c = Color3.fromRGB(156,148,136), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Paving_VM_Cob'] = {c = Color3.fromRGB(198,180,150), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_CobB'] = {c = Color3.fromRGB(174,158,132), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_Edge'] = {c = Color3.fromRGB(152,140,122), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Paving_VM_Joint'] = {c = Color3.fromRGB(112,100,86), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_VM_Base'] = {c = Color3.fromRGB(150,143,132), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Dark'] = {c = Color3.fromRGB(108,102,96), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Grey'] = {c = Color3.fromRGB(140,136,128), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Mortar'] = {c = Color3.fromRGB(72,68,66), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Trim'] = {c = Color3.fromRGB(178,170,154), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Stone_VM_Warm'] = {c = Color3.fromRGB(160,148,130), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
  ['Water_VM'] = {c = Color3.fromRGB(64,150,190), m = Enum.Material.SmoothPlastic, t = 0.0, s = false, x = nil, w = nil},
  ['Window_VM_Lamp'] = {c = Color3.fromRGB(238,204,146), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = nil, w = nil},
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
local FBX = {[1]='LOBBY_VM_02_TERRAIN_6c3d02.fbx', [2]='LOBBY_VM_03_TOWN_6c3d02.fbx', [3]='LOBBY_VM_04_FORGE_6c3d02.fbx', [4]='LOBBY_VM_05_SERVICES_6c3d02.fbx', [5]='LOBBY_VM_06_PORTALS_6c3d02.fbx', [6]='LOBBY_VM_07_EXIT_6c3d02.fbx', [7]='LOBBY_VM_08_WATER_6c3d02.fbx', [8]='LOBBY_VM_09_VEGETATION_6c3d02.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['VM_Bg_Mountains__Cliff_VM_Far']={-37.212,88.948,-211.813,1919.056,297.896,1494.601,1,false,'Cliff_VM_Far','k',''},
  ['VM_Bg_Mountains__Cliff_VM_FarSnow']={-35.457,152.169,-185.043,1658.645,171.454,1228.512,1,false,'Cliff_VM_FarSnow','k',''},
  ['VM_Ter_Canal2__Stone_VM_Grey_g15_16']={-79.75,4.484,-12.0,99.36,4.828,13.24,1,true,'Stone_VM_Grey','',''},
  ['VM_Ter_Canal2__Stone_VM_Grey_g16_16']={80.964,4.483,-12.0,101.788,4.821,13.24,1,true,'Stone_VM_Grey','',''},
  ['VM_Ter_Canal2__Stone_VM_Grey_g17_16']={145.808,4.477,-12.0,41.244,4.812,13.24,1,true,'Stone_VM_Grey','',''},
  ['VM_Ter_Canal2__Stone_VM_Mortar']={18.5,3.79,-12.0,296.0,6.38,13.7,1,true,'Stone_VM_Mortar','',''},
  ['VM_Ter_Canal2__Stone_VM_Trim_g15_16']={-79.75,6.677,-12.0,99.502,2.226,14.15,1,true,'Stone_VM_Trim','',''},
  ['VM_Ter_Canal2__Stone_VM_Trim_g16_16']={98.252,6.67,-12.0,136.505,2.219,14.15,1,true,'Stone_VM_Trim','',''},
  ['VM_Ter_Canal2__Stone_VM_Warm_g15_16']={-81.151,4.49,-12.0,96.559,4.805,13.24,1,true,'Stone_VM_Warm','',''},
  ['VM_Ter_Canal2__Stone_VM_Warm_g16_16']={98.25,4.486,-12.0,136.36,4.808,13.24,1,true,'Stone_VM_Warm','',''},
  ['VM_Ter_CanalWalls__Stone_VM_Base']={36.0,4.35,-51.475,8.0,7.5,67.05,1,true,'Stone_VM_Base','',''},
  ['VM_Ter_Cliffs__Cliff_VM_Rock']={-27.46,-15.398,13.917,403.855,37.205,292.64,1,true,'Cliff_VM_Rock','',''},
  ['VM_Ter_Ground__Cliff_VM_Rock']={-28.0,3.1,13.5,392.0,5.8,279.0,1,true,'Cliff_VM_Rock','',''},
  ['VM_Ter_Ground__Grass_VM']={-28.0,5.9,13.5,392.0,1.8,279.0,1,false,'Grass_VM','',''},
  ['VM_Ter_Ground__Stone_VM_Dark']={18.226,0.4,-45.0,297.852,0.4,80.0,1,true,'Stone_VM_Dark','',''},
  ['VM_Ter_Hills__Bark_VM']={-32.0,40.946,-52.022,577.63,54.019,510.0,1,false,'Bark_VM','k',''},
  ['VM_Ter_Hills__Grass_VM_Hill']={-24.467,-5.148,-71.677,765.106,140.413,638.392,1,false,'Grass_VM_Hill','k',''},
  ['VM_Ter_Hills__Leaf_VM_Pine']={-31.756,49.861,-51.065,587.256,65.82,520.928,1,false,'Leaf_VM_Pine','k',''},
  ['VM_Ter_TCanal__Stone_VM_Grey']={0.011,4.963,-12.0,59.992,5.786,14.118,1,true,'Stone_VM_Grey','',''},
  ['VM_Ter_TCanal__Stone_VM_Mortar']={0.0,4.265,-12.0,60.0,7.33,14.0,1,true,'Stone_VM_Mortar','',''},
  ['VM_Ter_TCanal__Stone_VM_Trim']={0.0,7.52,-12.0,60.12,1.4,14.28,1,true,'Stone_VM_Trim','',''},
  ['VM_Ter_TCanal__Stone_VM_Warm']={0.569,4.482,-12.0,58.723,4.82,13.24,1,true,'Stone_VM_Warm','',''},
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
  ['VM_House_QEE__Plaster_VM_Cream']={58.901,18.788,108.589,22.592,19.575,44.072,2,true,'Plaster_VM_Cream','','VM_House_QEE'},
  ['VM_House_QEE__Plaster_VM_Peach']={54.805,19.66,102.616,30.87,28.32,56.859,2,true,'Plaster_VM_Peach','','VM_House_QEE'},
  ['VM_House_QEE__Roof_VM_Terracotta']={54.075,26.321,102.253,33.625,16.399,58.011,2,true,'Roof_VM_Terracotta','','VM_House_QEE'},
  ['VM_House_QEE__Roof_VM_Terracotta_B']={55.508,26.223,101.786,32.606,17.931,59.043,2,true,'Roof_VM_Terracotta_B','','VM_House_QEE'},
  ['VM_House_QEE__Stone_VM_Grey']={63.026,17.723,118.892,13.543,24.445,23.423,2,true,'Stone_VM_Grey','','VM_House_QEE'},
  ['VM_House_QEE__Stone_VM_Mortar']={55.618,21.047,102.644,29.038,30.694,55.745,2,true,'Stone_VM_Mortar','','VM_House_QEE'},
  ['VM_House_QEE__Stone_VM_Warm']={51.737,20.787,88.05,22.245,30.174,27.481,2,true,'Stone_VM_Warm','','VM_House_QEE'},
  ['VM_House_QEE__Wood_VM_Timber']={54.161,20.238,101.667,34.194,28.676,59.25,2,true,'Wood_VM_Timber','','VM_House_QEE'},
  ['VM_House_QEW__Plaster_VM_Cream']={34.257,17.546,111.746,13.107,17.092,11.803,2,false,'Plaster_VM_Cream','','VM_House_QEW'},
  ['VM_House_QEW__Plaster_VM_Ochre']={33.428,19.815,111.014,21.589,28.631,32.06,2,true,'Plaster_VM_Ochre','','VM_House_QEW'},
  ['VM_House_QEW__Roof_VM_Terracotta']={32.773,26.929,112.049,22.905,17.164,31.463,2,true,'Roof_VM_Terracotta','','VM_House_QEW'},
  ['VM_House_QEW__Roof_VM_Terracotta_C']={33.373,26.557,110.814,25.826,16.542,35.148,2,true,'Roof_VM_Terracotta_C','','VM_House_QEW'},
  ['VM_House_QEW__Stone_VM_Grey']={33.203,20.848,111.257,20.745,30.696,31.527,2,true,'Stone_VM_Grey','','VM_House_QEW'},
  ['VM_House_QEW__Stone_VM_Mortar']={33.209,21.208,111.246,20.008,31.016,30.606,2,true,'Stone_VM_Mortar','','VM_House_QEW'},
  ['VM_House_QEW__Wood_VM_Timber']={33.358,20.388,110.805,26.023,28.977,35.707,2,true,'Wood_VM_Timber','','VM_House_QEW'},
  ['VM_House_QN__Plaster_VM_Cream']={-15.0,22.767,-28.1,10.8,15.534,13.8,2,true,'Plaster_VM_Cream','','VM_House_QN'},
  ['VM_House_QN__Plaster_VM_Peach']={14.95,22.955,-28.1,10.9,15.91,13.8,2,true,'Plaster_VM_Peach','','VM_House_QN'},
  ['VM_House_QN__Roof_VM_Terracotta_B']={0.075,25.732,-28.526,41.25,13.116,16.764,2,true,'Roof_VM_Terracotta_B','','VM_House_QN'},
  ['VM_House_QN__Roof_VM_Terracotta_C']={-0.075,25.49,-28.095,41.25,12.825,17.62,2,true,'Roof_VM_Terracotta_C','','VM_House_QN'},
  ['VM_House_QN__Stone_VM_Grey']={14.893,19.837,-28.1,11.186,26.275,14.52,2,true,'Stone_VM_Grey','','VM_House_QN'},
  ['VM_House_QN__Stone_VM_Mortar']={0.0,20.097,-28.1,39.96,26.795,13.26,2,true,'Stone_VM_Mortar','','VM_House_QN'},
  ['VM_House_QN__Stone_VM_Warm']={-14.886,19.644,-28.1,11.173,25.888,14.52,2,true,'Stone_VM_Warm','','VM_House_QN'},
  ['VM_House_QN__Wood_VM_Timber']={0.0,19.303,-28.1,41.62,24.706,17.675,2,true,'Wood_VM_Timber','','VM_House_QN'},
  ['VM_House_QNE__Plaster_VM_Ochre']={48.3,21.565,16.0,26.6,25.131,40.0,2,true,'Plaster_VM_Ochre','','VM_House_QNE'},
  ['VM_House_QNE__Plaster_VM_Peach']={36.972,18.296,15.986,27.944,18.592,39.973,2,true,'Plaster_VM_Peach','','VM_House_QNE'},
  ['VM_House_QNE__Roof_VM_Terracotta']={42.225,26.045,16.234,39.95,17.56,43.652,2,true,'Roof_VM_Terracotta','','VM_House_QNE'},
  ['VM_House_QNE__Roof_VM_Terracotta_C']={42.375,26.388,16.044,39.95,18.245,43.083,2,true,'Roof_VM_Terracotta_C','','VM_House_QNE'},
  ['VM_House_QNE__Stone_VM_Base']={56.5,15.583,30.6,10.2,20.165,10.0,2,false,'Stone_VM_Base','','VM_House_QNE'},
  ['VM_House_QNE__Stone_VM_Mortar']={42.3,21.208,16.0,38.88,31.016,40.28,2,true,'Stone_VM_Mortar','','VM_House_QNE'},
  ['VM_House_QNE__Stone_VM_Trim']={42.3,7.25,16.0,39.44,3.5,40.04,2,true,'Stone_VM_Trim','','VM_House_QNE'},
  ['VM_House_QNE__Stone_VM_Warm']={36.969,20.848,16.107,27.938,30.696,39.415,2,true,'Stone_VM_Warm','','VM_House_QNE'},
  ['VM_House_QNE__Wood_VM_Timber']={42.3,20.388,16.554,39.84,28.977,43.169,2,true,'Wood_VM_Timber','','VM_House_QNE'},
  ['VM_House_QNW__Plaster_VM_Cream']={-41.211,18.125,12.697,13.578,18.249,33.395,2,true,'Plaster_VM_Cream','','VM_House_QNW'},
  ['VM_House_QNW__Plaster_VM_Ochre']={-46.897,18.639,18.349,20.205,19.279,44.699,2,true,'Plaster_VM_Ochre','','VM_House_QNW'},
  ['VM_House_QNW__Roof_VM_Terracotta']={-45.377,23.866,19.032,24.746,11.585,47.43,2,true,'Roof_VM_Terracotta','','VM_House_QNW'},
  ['VM_House_QNW__Roof_VM_Terracotta_B']={-45.403,23.395,18.163,24.393,11.147,47.569,2,true,'Roof_VM_Terracotta_B','','VM_House_QNW'},
  ['VM_House_QNW__Stone_VM_Grey']={-46.5,15.833,1.4,21.0,20.665,10.0,2,true,'Stone_VM_Grey','','VM_House_QNW'},
  ['VM_House_QNW__Stone_VM_Mortar']={-46.002,18.282,17.921,22.277,25.164,44.122,2,true,'Stone_VM_Mortar','','VM_House_QNW'},
  ['VM_House_QNW__Stone_VM_Trim']={-46.5,7.25,1.4,21.84,3.5,10.84,2,false,'Stone_VM_Trim','','VM_House_QNW'},
  ['VM_House_QNW__Stone_VM_Warm']={-42.36,18.022,28.561,15.387,24.644,23.829,2,true,'Stone_VM_Warm','','VM_House_QNW'},
  ['VM_House_QNW__Wood_VM_Timber']={-45.183,17.463,18.923,24.874,23.125,47.907,2,true,'Wood_VM_Timber','','VM_House_QNW'},
  ['VM_House_QSB__Plaster_VM_Ochre']={-8.65,17.796,122.5,36.7,17.592,10.8,2,true,'Plaster_VM_Ochre','','VM_House_QSB'},
  ['VM_House_QSB__Plaster_VM_Peach']={2.05,18.546,122.5,35.7,19.092,10.8,2,true,'Plaster_VM_Peach','','VM_House_QSB'},
  ['VM_House_QSB__Roof_VM_Terracotta_B']={-3.46,23.364,122.511,48.28,12.131,14.014,2,true,'Roof_VM_Terracotta_B','','VM_House_QSB'},
  ['VM_House_QSB__Roof_VM_Terracotta_C']={-3.625,23.045,122.499,48.25,11.489,13.965,2,true,'Roof_VM_Terracotta_C','','VM_House_QSB'},
  ['VM_House_QSB__Stone_VM_Grey']={3.7,15.583,122.5,12.0,20.165,10.0,2,false,'Stone_VM_Grey','','VM_House_QSB'},
  ['VM_House_QSB__Stone_VM_Mortar']={-3.55,19.772,122.5,47.18,15.827,11.08,2,true,'Stone_VM_Mortar','','VM_House_QSB'},
  ['VM_House_QSB__Stone_VM_Trim']={-3.55,7.25,122.5,47.74,3.5,10.84,2,true,'Stone_VM_Trim','','VM_House_QSB'},
  ['VM_House_QSB__Stone_VM_Warm']={-3.55,16.333,122.5,46.9,21.665,10.0,2,true,'Stone_VM_Warm','','VM_House_QSB'},
  ['VM_House_QSB__Wood_VM_Plank']={-4.336,7.225,117.46,40.928,2.65,0.28,2,true,'Wood_VM_Plank','','VM_House_QSB'},
  ['VM_House_QSB__Wood_VM_Timber']={-3.55,18.52,122.5,48.14,19.94,12.862,2,true,'Wood_VM_Timber','','VM_House_QSB'},
  ['VM_House_QSE__Plaster_VM_Cream']={49.302,16.16,57.343,24.237,21.321,14.726,2,true,'Plaster_VM_Cream','','VM_House_QSE'},
  ['VM_House_QSE__Plaster_VM_Peach']={41.073,20.281,67.221,12.858,12.561,11.405,2,true,'Plaster_VM_Peach','','VM_House_QSE'},
  ['VM_House_QSE__Roof_VM_Terracotta']={47.566,22.98,61.613,28.428,10.418,26.452,2,true,'Roof_VM_Terracotta','','VM_House_QSE'},
  ['VM_House_QSE__Roof_VM_Terracotta_B']={47.376,22.854,60.384,28.449,10.227,23.918,2,true,'Roof_VM_Terracotta_B','','VM_House_QSE'},
  ['VM_House_QSE__Stone_VM_Grey']={47.871,15.083,61.616,26.258,19.165,22.432,2,true,'Stone_VM_Grey','','VM_House_QSE'},
  ['VM_House_QSE__Stone_VM_Mortar']={48.106,17.547,61.129,26.068,23.694,22.538,2,true,'Stone_VM_Mortar','','VM_House_QSE'},
  ['VM_House_QSE__Stone_VM_Warm']={43.901,17.287,58.384,12.827,23.174,12.338,2,true,'Stone_VM_Warm','','VM_House_QSE'},
  ['VM_House_QSE__Wood_VM_Timber']={47.243,16.738,61.937,28.754,21.676,25.935,2,true,'Wood_VM_Timber','','VM_House_QSE'},
  ['VM_House_QSW__Plaster_VM_Cream']={-49.306,17.796,79.948,52.385,17.592,23.615,2,true,'Plaster_VM_Cream','','VM_House_QSW'},
  ['VM_House_QSW__Plaster_VM_Peach']={-53.468,17.408,72.804,44.887,23.817,17.481,2,true,'Plaster_VM_Peach','','VM_House_QSW'},
  ['VM_House_QSW__Roof_VM_Terracotta']={-48.74,24.384,77.79,55.414,12.624,31.67,2,true,'Roof_VM_Terracotta','','VM_House_QSW'},
  ['VM_House_QSW__Roof_VM_Terracotta_C']={-48.915,24.046,77.319,54.246,11.928,29.558,2,true,'Roof_VM_Terracotta_C','','VM_House_QSW'},
  ['VM_House_QSW__Stone_VM_Grey']={-47.748,18.541,72.781,31.949,25.682,16.123,2,true,'Stone_VM_Grey','','VM_House_QSW'},
  ['VM_House_QSW__Stone_VM_Mortar']={-49.442,18.801,78.178,50.198,26.202,25.98,2,true,'Stone_VM_Mortar','','VM_House_QSW'},
  ['VM_House_QSW__Stone_VM_Warm']={-49.589,17.057,80.082,51.633,23.114,23.106,2,true,'Stone_VM_Warm','','VM_House_QSW'},
  ['VM_House_QSW__Wood_VM_Timber']={-48.572,17.981,77.833,55.497,24.163,32.153,2,true,'Wood_VM_Timber','','VM_House_QSW'},
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
  ['VM_Prop_CN__Cloth_VM_Cream']={-40.041,7.899,-39.894,3.563,2.356,1.109,2,false,'Cloth_VM_Cream','',''},
  ['VM_Prop_CN__Stone_VM_Grey']={-23.026,7.349,-47.696,136.122,1.581,87.153,2,true,'Stone_VM_Grey','',''},
  ['VM_Prop_CN__Wood_VM_Plank']={-58.299,8.011,-22.294,32.222,4.463,60.763,2,true,'Wood_VM_Plank','',''},
  ['VM_Prop_CN__Wood_VM_Timber']={-58.19,8.165,-22.203,32.7,4.77,60.945,2,true,'Wood_VM_Timber','',''},
  ['VM_Prop_CS__Cloth_VM_Cream']={-25.5,8.17,120.525,77.0,4.893,33.323,2,true,'Cloth_VM_Cream','',''},
  ['VM_Prop_CS__Cloth_VM_Red']={-27.977,9.342,120.494,66.954,2.527,33.253,2,true,'Cloth_VM_Red','',''},
  ['VM_Prop_CS__Roof_VM_Terracotta']={-6.855,8.381,89.933,93.332,5.201,53.47,2,true,'Roof_VM_Terracotta','',''},
  ['VM_Prop_CS__Stone_VM_Grey']={-27.141,6.36,74.705,121.617,1.552,118.846,2,true,'Stone_VM_Grey','',''},
  ['VM_Prop_CS__Wood_VM_Plank']={-22.848,9.655,78.819,120.819,7.75,132.774,2,true,'Wood_VM_Plank','',''},
  ['VM_Prop_CS__Wood_VM_Timber']={-22.819,9.93,79.496,120.912,8.9,131.949,2,true,'Wood_VM_Timber','',''},
  ['VM_Prop_EN__Cloth_VM_Blue']={70.605,10.343,-39.952,1.436,2.1,0.171,2,false,'Cloth_VM_Blue','',''},
  ['VM_Prop_EN__Cloth_VM_Cream']={70.687,10.379,-39.951,5.625,2.449,0.23,2,false,'Cloth_VM_Cream','',''},
  ['VM_Prop_EN__Stone_VM_Grey']={89.999,7.36,-70.001,24.126,1.558,3.851,2,true,'Stone_VM_Grey','',''},
  ['VM_Prop_EN__Wood_VM_Timber']={84.722,9.43,-32.525,45.444,5.9,16.55,2,true,'Wood_VM_Timber','',''},
  ['VM_Prop_ES__Cloth_VM_Cream']={93.073,6.9,29.982,1.446,2.354,4.414,2,false,'Cloth_VM_Cream','',''},
  ['VM_Prop_ES__Stone_VM_Grey']={98.863,6.359,51.653,103.822,1.559,84.102,2,true,'Stone_VM_Grey','',''},
  ['VM_Prop_ES__Wood_VM_Plank']={78.965,7.875,92.782,68.776,4.19,95.363,2,true,'Wood_VM_Plank','',''},
  ['VM_Prop_ES__Wood_VM_Timber']={78.855,7.92,92.847,68.804,4.34,95.493,2,true,'Wood_VM_Timber','',''},
  ['VM_Prop_WS__Stone_VM_Grey']={-100.882,6.361,102.411,22.135,1.555,47.922,2,true,'Stone_VM_Grey','',''},
  ['VM_Prop_WS__Wood_VM_Timber']={-103.197,9.92,49.474,17.171,8.881,59.83,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_DressE__Cloth_VM_Cream']={48.767,14.403,37.043,26.511,3.205,34.953,2,true,'Cloth_VM_Cream','',''},
  ['VM_Town_DressE__Cloth_VM_Red']={48.673,14.403,37.04,26.7,3.205,36.73,2,true,'Cloth_VM_Red','',''},
  ['VM_Town_DressE__Flower_VM_Pink']={49.12,22.99,37.143,23.683,10.762,30.331,2,false,'Flower_VM_Pink','',''},
  ['VM_Town_DressE__Leaf_VM_Tuft']={49.193,22.729,37.164,23.785,10.939,30.094,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_DressE__Wood_VM_Timber']={48.144,13.285,41.896,27.791,9.21,46.234,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_DressS__Cloth_VM_Cream']={43.01,13.703,120.158,3.501,1.805,6.709,2,false,'Cloth_VM_Cream','',''},
  ['VM_Town_DressS__Cloth_VM_Red']={43.01,13.703,120.158,3.858,1.805,8.496,2,false,'Cloth_VM_Red','',''},
  ['VM_Town_DressS__Flower_VM_Yellow']={42.714,23.035,103.008,16.484,10.838,35.93,2,false,'Flower_VM_Yellow','',''},
  ['VM_Town_DressS__Leaf_VM_Tuft']={42.65,22.714,102.937,16.685,10.95,35.908,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_DressS__Wood_VM_Timber']={46.434,12.235,104.084,22.958,7.11,40.438,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_DressW__Flower_VM_Red']={-24.39,17.472,24.296,123.693,21.822,112.945,2,false,'Flower_VM_Red','',''},
  ['VM_Town_DressW__Leaf_VM_Tuft']={-38.978,22.673,24.499,94.336,10.87,112.818,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_DressW__Wood_VM_Timber']={-38.41,9.5,26.054,97.979,1.64,111.478,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_Edges2__Leaf_VM_Tuft']={-19.529,6.419,96.828,158.623,1.637,100.043,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_Foot100__Stone_Paving_VM_Cob']={100.0,6.754,-11.913,3.796,1.912,19.339,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_Foot100__Stone_Paving_VM_Joint']={100.0,6.341,-11.9,3.9,2.483,19.4,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_Foot100__Stone_VM_Dark']={100.0,4.9,-12.0,3.7,3.4,12.92,2,false,'Stone_VM_Dark','',''},
  ['VM_Town_Foot100__Stone_VM_Grey']={100.0,4.741,-11.9,5.3,8.281,19.44,2,true,'Stone_VM_Grey','',''},
  ['VM_Town_Foot100__Stone_VM_Trim']={100.0,6.195,-11.9,5.6,5.872,19.44,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_Foot116__Stone_Paving_VM_Cob']={-115.999,6.754,-11.883,3.796,1.96,19.34,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_Foot116__Stone_Paving_VM_Joint']={-116.0,6.341,-11.9,3.9,2.483,19.4,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_Foot116__Stone_VM_Dark']={-116.0,4.9,-12.0,3.7,3.4,12.92,2,false,'Stone_VM_Dark','',''},
  ['VM_Town_Foot116__Stone_VM_Grey']={-116.0,4.741,-11.9,5.3,8.281,19.44,2,true,'Stone_VM_Grey','',''},
  ['VM_Town_Foot116__Stone_VM_Trim']={-116.0,6.195,-11.9,5.6,5.872,19.44,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_Medallion__Metal_VM_Bronze']={0.0,5.695,50.0,17.6,0.71,17.6,2,true,'Metal_VM_Bronze','',''},
  ['VM_Town_Medallion__Metal_VM_Iron']={-0.65,5.735,50.175,8.34,0.39,4.59,2,false,'Metal_VM_Iron','',''},
  ['VM_Town_Medallion__Stone_Paving_VM_Edge']={0.0,5.625,50.0,18.0,0.57,18.0,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_Medallion__Stone_Paving_VM_Joint']={0.0,5.115,50.0,17.964,0.85,17.964,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_Medallion__Stone_VM_Base']={0.0,5.61,50.0,18.0,0.54,18.0,2,false,'Stone_VM_Base','',''},
  ['VM_Town_Medallion__Stone_VM_Trim']={0.0,5.455,50.0,14.159,0.43,14.159,2,false,'Stone_VM_Trim','',''},
  ['VM_Town_Plaza__Stone_Paving_VM_Cob']={-0.049,6.015,48.25,69.27,0.29,65.975,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_Plaza__Stone_Paving_VM_CobB']={0.018,6.015,48.419,69.485,0.29,66.211,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_Plaza__Stone_Paving_VM_Edge']={0.007,6.015,49.006,71.922,0.289,67.65,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_Plaza__Stone_Paving_VM_Joint']={0.0,5.8,50.0,72.0,0.3,72.0,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_PlazaBorder__Metal_VM_Iron']={0.928,11.972,51.91,69.404,10.825,34.226,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_PlazaBorder__Stone_Paving_VM_Joint']={1.375,7.031,50.123,72.161,2.563,52.504,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_PlazaBorder__Stone_VM_Warm']={1.326,6.436,50.121,73.681,1.749,54.315,2,true,'Stone_VM_Warm','',''},
  ['VM_Town_PlazaBorder__Window_VM_Lamp']={0.956,15.56,51.903,68.785,1.6,33.516,2,true,'Window_VM_Lamp','',''},
  ['VM_Town_PlazaBorder__Wood_VM_Plank']={1.014,8.31,50.936,66.627,2.1,45.67,2,true,'Wood_VM_Plank','',''},
  ['VM_Town_RoadE__Stone_Paving_VM_Cob']={26.465,6.475,5.977,70.859,1.288,84.644,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_RoadE__Stone_Paving_VM_CobB']={26.456,6.472,5.99,70.859,1.281,84.619,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_RoadE__Stone_Paving_VM_Edge']={21.693,6.42,6.317,62.771,1.636,85.404,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_RoadE__Stone_Paving_VM_Joint']={26.1,6.27,6.31,71.6,1.3,85.42,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_RoadS__Stone_Paving_VM_Cob']={39.08,5.975,108.971,37.128,0.289,75.238,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_RoadS__Stone_Paving_VM_CobB']={41.361,5.975,109.625,32.501,0.289,74.12,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_RoadS__Stone_Paving_VM_Edge']={39.406,5.921,108.125,37.869,0.637,77.258,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_RoadS__Stone_Paving_VM_Joint']={38.55,5.77,108.076,39.666,0.3,77.398,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_RoadW__Stone_Paving_VM_Cob']={-62.311,5.975,58.991,52.932,0.289,24.076,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_RoadW__Stone_Paving_VM_CobB']={-61.54,5.976,60.255,52.637,0.287,22.68,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_RoadW__Stone_Paving_VM_Edge']={-69.549,5.92,50.692,70.536,0.637,43.363,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_RoadW__Stone_Paving_VM_Joint']={-68.043,5.77,48.527,71.387,0.3,48.633,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_RoadW__Stone_VM_Trim']={-77.743,5.976,42.994,56.117,0.269,36.49,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_Spawn__Metal_VM_Bronze']={-0.015,9.522,94.01,13.731,0.283,13.757,2,true,'Metal_VM_Bronze','',''},
  ['VM_Town_Spawn__Metal_VM_Iron']={0.0,12.612,79.1,29.127,7.825,1.527,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_Spawn__Stone_Paving_VM_Cob']={0.423,9.495,100.45,40.706,0.266,24.36,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_Spawn__Stone_Paving_VM_CobB']={-0.657,9.496,100.45,38.546,0.268,24.36,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_Spawn__Stone_Paving_VM_Edge']={-0.001,9.495,93.986,16.243,0.285,16.096,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_Spawn__Stone_Paving_VM_Joint']={0.0,9.275,100.0,39.6,0.25,23.64,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Town_Spawn__Stone_VM_Grey']={-0.144,7.391,100.069,39.789,3.619,24.028,2,true,'Stone_VM_Grey','',''},
  ['VM_Town_Spawn__Stone_VM_Mortar']={0.0,8.45,95.425,40.98,5.9,34.13,2,true,'Stone_VM_Mortar','',''},
  ['VM_Town_Spawn__Stone_VM_Trim']={0.0,8.74,95.425,42.1,6.32,35.25,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_Spawn__Stone_VM_Warm']={0.02,8.149,96.031,40.139,5.148,32.102,2,true,'Stone_VM_Warm','',''},
  ['VM_Town_Spawn__Window_VM_Lamp']={0.0,14.7,79.1,28.6,1.6,1.0,2,false,'Window_VM_Lamp','',''},
  ['VM_Town_StreetProps__Metal_VM_Iron']={-11.348,11.302,46.242,144.224,10.445,164.411,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_StreetProps__Stone_VM_Warm']={-11.348,6.635,46.242,144.137,1.77,164.324,2,true,'Stone_VM_Warm','',''},
  ['VM_Town_StreetProps__Window_VM_Lamp']={-11.348,14.2,46.242,143.697,2.6,163.884,2,true,'Window_VM_Lamp','',''},
  ['VM_Town_StreetProps__Wood_VM_Plank']={47.009,8.06,116.215,25.061,4.22,30.952,2,true,'Wood_VM_Plank','',''},
  ['VM_Town_StreetProps__Wood_VM_Timber']={47.239,8.12,116.411,25.069,4.34,30.867,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_TBridge__Metal_VM_Iron']={0.0,10.17,1.2,21.572,2.76,1.372,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_TBridge__Stone_VM_Dark']={0.0,4.625,-12.0,20.3,3.25,13.008,2,true,'Stone_VM_Dark','',''},
  ['VM_Town_TBridge__Stone_VM_Grey']={0.0,7.133,-10.0,23.3,4.494,25.5,2,true,'Stone_VM_Grey','',''},
  ['VM_Town_TBridge__Stone_VM_Mortar']={0.0,5.0,-10.405,22.18,8.8,25.19,2,true,'Stone_VM_Mortar','',''},
  ['VM_Town_TBridge__Stone_VM_Trim']={0.0,6.474,-10.0,22.48,6.852,24.4,2,true,'Stone_VM_Trim','',''},
  ['VM_Town_TBridge__Window_VM_Lamp']={0.0,9.6,1.2,21.04,1.2,0.84,2,false,'Window_VM_Lamp','',''},
  ['VM_Town_TDress__Cloth_VM_Cream']={11.177,13.703,-0.75,2.294,1.805,6.31,2,false,'Cloth_VM_Cream','',''},
  ['VM_Town_TDress__Cloth_VM_Red']={11.177,13.703,-0.75,2.294,1.805,8.11,2,false,'Cloth_VM_Red','',''},
  ['VM_Town_TDress__Flower_VM_Red']={1.009,17.324,6.865,73.538,22.256,26.424,2,false,'Flower_VM_Red','',''},
  ['VM_Town_TDress__Leaf_VM_Tuft']={1.028,21.617,6.873,73.348,13.119,26.337,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_TDress__Wood_VM_Timber']={-0.615,12.235,6.8,59.84,7.11,23.28,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_TEdges__Leaf_VM_Tuft']={0.661,6.462,7.549,68.166,1.724,25.043,2,false,'Leaf_VM_Tuft','',''},
  ['VM_Town_TEdges__Stone_VM_Warm']={0.397,5.977,7.541,69.127,0.753,24.862,2,true,'Stone_VM_Warm','',''},
  ['VM_Town_TProps__Metal_VM_Iron']={0.0,11.795,17.831,55.485,11.83,27.822,2,true,'Metal_VM_Iron','',''},
  ['VM_Town_TProps__Stone_VM_Warm']={0.0,6.21,24.4,55.5,0.8,14.7,2,true,'Stone_VM_Warm','',''},
  ['VM_Town_TProps__Window_VM_Lamp']={0.0,15.56,24.4,55.0,1.6,14.2,2,true,'Window_VM_Lamp','',''},
  ['VM_Town_TProps__Wood_VM_Plank']={-11.278,7.86,13.586,47.173,4.22,22.549,2,true,'Wood_VM_Plank','',''},
  ['VM_Town_TProps__Wood_VM_Timber']={-11.511,7.92,13.595,47.187,4.34,22.917,2,true,'Wood_VM_Timber','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_Cob']={0.646,6.608,4.536,62.589,1.676,51.037,2,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_CobB']={0.654,6.599,5.193,62.561,1.656,52.36,2,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_Edge']={0.1,5.835,5.943,22.78,0.57,18.215,2,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Town_TStreet__Stone_Paving_VM_Joint']={0.65,6.39,5.2,62.6,1.68,52.4,2,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Frg_Hall__Forge_Glow_VM']={-0.383,49.761,-81.193,9.033,81.722,17.786,3,false,'Forge_Glow_VM','','VM_Forja'},
  ['VM_Frg_Hall__Metal_VM_Iron']={11.26,21.235,-60.91,57.68,26.77,25.62,3,true,'Metal_VM_Iron','o','VM_Forja'},
  ['VM_Frg_Hall__Plaster_VM_Cream']={-1.694,33.525,-64.2,66.611,37.05,28.4,3,true,'Plaster_VM_Cream','o','VM_Forja'},
  ['VM_Frg_Hall__Roof_VM_Terracotta']={-1.698,33.685,-63.2,70.444,38.16,31.6,3,true,'Roof_VM_Terracotta','o','VM_Forja'},
  ['VM_Frg_Hall__Roof_VM_Terracotta_B']={-1.658,33.971,-63.185,70.36,38.764,31.93,3,true,'Roof_VM_Terracotta_B','o','VM_Forja'},
  ['VM_Frg_Hall__Stone_VM_Grey']={-1.0,23.335,-63.845,30.44,33.13,27.55,3,true,'Stone_VM_Grey','o','VM_Forja'},
  ['VM_Frg_Hall__Stone_VM_Mortar']={-1.465,50.1,-71.79,66.53,86.8,43.58,3,true,'Stone_VM_Mortar','o','VM_Forja'},
  ['VM_Frg_Hall__Stone_VM_Warm']={2.395,50.95,-71.775,75.51,88.5,45.05,3,true,'Stone_VM_Warm','o','VM_Forja'},
  ['VM_Frg_Hall__Wood_VM_Plank']={-1.0,32.817,-64.1,30.04,35.355,28.2,3,true,'Wood_VM_Plank','o','VM_Forja'},
  ['VM_Frg_Hall__Wood_VM_Timber']={-1.705,29.885,-63.806,70.445,45.964,33.331,3,true,'Wood_VM_Timber','o','VM_Forja'},
  ['VM_Frg_Props__Cloth_VM_Cream']={-1.63,11.303,-55.907,65.452,8.605,18.396,3,true,'Cloth_VM_Cream','','VM_Forja'},
  ['VM_Frg_Props__Cloth_VM_Red']={-9.116,22.2,-50.667,48.533,16.8,2.714,3,true,'Cloth_VM_Red','','VM_Forja'},
  ['VM_Frg_Props__Metal_VM_Bronze']={-4.04,26.48,-60.95,60.46,35.259,27.3,3,true,'Metal_VM_Bronze','','VM_Forja'},
  ['VM_Frg_Props__Metal_VM_Iron']={-0.79,25.09,-60.315,66.841,36.02,29.39,3,true,'Metal_VM_Iron','','VM_Forja'},
  ['VM_Frg_Props__Metal_VM_Steel']={-3.325,10.768,-52.51,46.25,4.304,10.42,3,true,'Metal_VM_Steel','','VM_Forja'},
  ['VM_Frg_Props__Stone_Paving_VM_Cob']={-1.603,6.884,-44.399,66.785,0.289,15.976,3,false,'Stone_Paving_VM_Cob','','VM_Forja'},
  ['VM_Frg_Props__Stone_Paving_VM_CobB']={-1.566,6.886,-44.407,66.716,0.288,15.96,3,false,'Stone_Paving_VM_CobB','','VM_Forja'},
  ['VM_Frg_Props__Stone_Paving_VM_Edge']={-1.805,6.825,-43.995,67.11,0.57,15.91,3,false,'Stone_Paving_VM_Edge','','VM_Forja'},
  ['VM_Frg_Props__Stone_Paving_VM_Joint']={-1.6,6.66,-44.4,66.8,0.28,16.0,3,false,'Stone_Paving_VM_Joint','','VM_Forja'},
  ['VM_Frg_Props__Stone_VM_Grey']={8.073,6.844,-63.774,47.249,0.288,27.125,3,true,'Stone_VM_Grey','','VM_Forja'},
  ['VM_Frg_Props__Stone_VM_Mortar']={-0.962,7.967,-62.37,65.424,2.973,30.06,3,true,'Stone_VM_Mortar','','VM_Forja'},
  ['VM_Frg_Props__Water_VM']={10.1,8.4,-57.6,4.8,1.3,3.4,3,false,'Water_VM','','VM_Forja'},
  ['VM_Frg_Props__Window_VM_Lamp']={-1.0,13.85,-48.3,30.96,1.5,0.96,3,true,'Window_VM_Lamp','','VM_Forja'},
  ['VM_Frg_Props__Wood_VM_Plank']={-0.845,24.5,-60.272,66.69,35.0,29.056,3,true,'Wood_VM_Plank','','VM_Forja'},
  ['VM_Frg_Props__Wood_VM_Timber']={-1.046,24.6,-60.292,66.588,35.4,28.616,3,true,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Frg_TripHammer__Metal_VM_Iron']={24.5,10.772,-64.978,2.0,4.145,17.455,3,false,'Metal_VM_Iron','','VM_Forja'},
  ['VM_Frg_TripHammer__Wood_VM_Timber']={24.5,11.625,-66.4,0.95,2.297,16.879,3,false,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Frg_Wheel__Metal_VM_Iron']={31.45,9.24,-66.0,18.25,3.079,3.294,3,true,'Metal_VM_Iron','','VM_Forja'},
  ['VM_Frg_Wheel__Wood_VM_Plank']={36.0,9.4,-66.0,4.3,15.8,15.8,3,false,'Wood_VM_Plank','','VM_Forja'},
  ['VM_Frg_Wheel__Wood_VM_Timber']={31.05,9.4,-66.0,19.7,14.3,14.3,3,true,'Wood_VM_Timber','','VM_Forja'},
  ['VM_Mail_Kiosk__Metal_VM_Bronze']={-11.39,16.0,100.0,0.12,1.2,2.0,4,false,'Metal_VM_Bronze','',''},
  ['VM_Mail_Kiosk__Plaster_VM_Cream']={-14.0,14.98,100.0,5.1,10.959,5.9,4,false,'Plaster_VM_Cream','',''},
  ['VM_Mail_Kiosk__Roof_VM_Terracotta']={-14.0,19.041,99.986,5.4,4.264,7.666,4,false,'Roof_VM_Terracotta','',''},
  ['VM_Mail_Kiosk__Roof_VM_Terracotta_B']={-13.985,19.817,100.019,5.73,3.924,6.149,4,false,'Roof_VM_Terracotta_B','',''},
  ['VM_Mail_Kiosk__Wood_VM_Timber']={-14.0,15.68,100.0,5.92,11.16,7.808,4,true,'Wood_VM_Timber','',''},
  ['VM_Rank_Hall__Plaster_VM_Ochre']={-87.589,23.91,11.746,32.058,19.82,22.416,4,true,'Plaster_VM_Ochre','','VM_Rank'},
  ['VM_Rank_Hall__Roof_VM_Terracotta']={-87.753,29.674,13.216,35.092,11.029,23.771,4,true,'Roof_VM_Terracotta','','VM_Rank'},
  ['VM_Rank_Hall__Roof_VM_Terracotta_B']={-87.417,29.334,11.356,35.034,10.37,25.904,4,true,'Roof_VM_Terracotta_B','','VM_Rank'},
  ['VM_Rank_Hall__Stone_VM_Mortar']={-87.868,21.047,11.067,30.394,30.694,20.103,4,true,'Stone_VM_Mortar','','VM_Rank'},
  ['VM_Rank_Hall__Stone_VM_Warm']={-87.881,20.787,11.072,31.428,30.174,20.973,4,true,'Stone_VM_Warm','','VM_Rank'},
  ['VM_Rank_Hall__Wood_VM_Timber']={-87.589,20.263,11.746,35.91,28.626,26.965,4,true,'Wood_VM_Timber','','VM_Rank'},
  ['VM_Rank_Stage__Cloth_VM_Blue']={-78.25,20.4,33.224,60.79,10.8,26.579,4,true,'Cloth_VM_Blue','','VM_Rank'},
  ['VM_Rank_Stage__Metal_VM_Bronze']={-78.195,24.575,33.109,58.19,8.55,25.877,4,true,'Metal_VM_Bronze','','VM_Rank'},
  ['VM_Rank_Stage__Metal_VM_Iron']={-76.344,11.913,37.608,51.531,10.825,23.541,4,true,'Metal_VM_Iron','','VM_Rank'},
  ['VM_Rank_Stage__Stone_Paving_VM_Edge']={-77.89,6.28,34.054,52.917,0.22,24.071,4,false,'Stone_Paving_VM_Edge','','VM_Rank'},
  ['VM_Rank_Stage__Stone_Paving_VM_Joint']={-78.199,6.09,33.343,53.772,0.22,25.833,4,false,'Stone_Paving_VM_Joint','','VM_Rank'},
  ['VM_Rank_Stage__Stone_VM_Mortar']={-81.209,5.815,26.419,61.165,0.33,41.468,4,true,'Stone_VM_Mortar','','VM_Rank'},
  ['VM_Rank_Stage__Stone_VM_Trim']={-81.657,6.19,26.029,59.216,0.42,39.634,4,true,'Stone_VM_Trim','','VM_Rank'},
  ['VM_Rank_Stage__Stone_VM_Warm']={-80.792,6.45,27.304,63.13,1.7,43.913,4,true,'Stone_VM_Warm','','VM_Rank'},
  ['VM_Rank_Stage__Window_VM_Lamp']={-76.344,15.5,37.608,50.838,1.6,22.847,4,true,'Window_VM_Lamp','','VM_Rank'},
  ['VM_Rank_Stage__Wood_VM_Timber']={-78.418,17.6,32.839,61.683,20.6,27.265,4,true,'Wood_VM_Timber','','VM_Rank'},
  ['VM_Shop_Building__Cloth_VM_Blue']={74.181,16.419,43.0,28.698,18.038,22.93,4,true,'Cloth_VM_Blue','','VM_Shop'},
  ['VM_Shop_Building__Cloth_VM_Red']={73.743,17.069,43.0,29.678,19.338,22.93,4,true,'Cloth_VM_Red','','VM_Shop'},
  ['VM_Shop_Building__Plaster_VM_Cream']={75.6,21.21,43.0,28.8,29.621,26.0,4,true,'Plaster_VM_Cream','o','VM_Shop'},
  ['VM_Shop_Building__Roof_VM_Terracotta']={75.5,28.908,42.98,31.0,15.659,29.759,4,true,'Roof_VM_Terracotta','o','VM_Shop'},
  ['VM_Shop_Building__Roof_VM_Terracotta_B']={75.485,29.232,42.979,31.33,16.17,29.623,4,true,'Roof_VM_Terracotta_B','o','VM_Shop'},
  ['VM_Shop_Building__Stone_VM_Mortar']={75.725,20.428,43.0,28.51,29.456,25.96,4,true,'Stone_VM_Mortar','o','VM_Shop'},
  ['VM_Shop_Building__Stone_VM_Warm']={75.3,20.204,43.0,29.599,28.863,26.72,4,true,'Stone_VM_Warm','o','VM_Shop'},
  ['VM_Shop_Building__Window_VM_Lamp']={72.0,13.7,43.0,3.661,0.8,3.661,4,false,'Window_VM_Lamp','','VM_Shop'},
  ['VM_Shop_Building__Wood_VM_Plank']={74.007,16.801,43.0,29.747,21.403,23.76,4,true,'Wood_VM_Plank','o','VM_Shop'},
  ['VM_Shop_Building__Wood_VM_Timber']={75.5,21.473,43.0,31.52,30.747,29.77,4,true,'Wood_VM_Timber','o','VM_Shop'},
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
  ['VM_Court_Arch__Metal_VM_Iron']={-89.079,18.045,65.487,1.547,3.31,1.547,5,false,'Metal_VM_Iron','',''},
  ['VM_Court_Arch__Stone_VM_Mortar']={-89.079,11.05,65.487,5.034,10.7,19.997,5,false,'Stone_VM_Mortar','',''},
  ['VM_Court_Arch__Stone_VM_Trim']={-89.079,18.675,65.487,6.652,5.85,21.616,5,true,'Stone_VM_Trim','',''},
  ['VM_Court_Arch__Stone_VM_Warm']={-89.075,13.439,65.511,5.988,15.321,20.997,5,true,'Stone_VM_Warm','',''},
  ['VM_Court_Arch__Window_VM_Lamp']={-89.079,17.15,65.487,0.921,1.1,0.921,5,false,'Window_VM_Lamp','',''},
  ['VM_Court_Floor__Grass_VM']={-161.364,6.3,72.0,79.471,1.8,146.18,5,false,'Grass_VM','',''},
  ['VM_Court_Floor__Metal_VM_Bronze']={-128.0,6.175,72.0,8.4,0.15,8.4,5,false,'Metal_VM_Bronze','',''},
  ['VM_Court_Floor__Metal_VM_Iron']={-155.932,11.972,72.0,22.063,10.825,69.523,5,true,'Metal_VM_Iron','',''},
  ['VM_Court_Floor__Stone_Paving_VM_Edge']={-142.593,6.3,72.0,108.813,1.8,137.982,5,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Court_Floor__Stone_Paving_VM_Joint']={-128.0,5.8,72.0,79.9,0.3,79.9,5,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Court_Floor__Stone_VM_Trim']={-144.644,7.03,72.0,115.212,2.939,148.499,5,true,'Stone_VM_Trim','',''},
  ['VM_Court_Floor__Stone_VM_Warm']={-144.606,6.713,72.0,114.888,2.89,148.1,5,true,'Stone_VM_Warm','',''},
  ['VM_Court_Floor__Window_VM_Lamp']={-155.979,15.56,72.0,21.442,1.6,68.81,5,true,'Window_VM_Lamp','',''},
  ['VM_Court_Floor__Wood_VM_Plank']={-149.27,8.31,72.0,19.0,2.1,56.402,5,true,'Wood_VM_Plank','',''},
  ['VM_Exit_Bridge__Metal_VM_Iron']={27.644,11.933,188.628,61.939,8.025,58.783,6,true,'Metal_VM_Iron','',''},
  ['VM_Exit_Bridge__Stone_Paving_VM_Cob']={26.38,5.955,180.117,61.529,0.289,68.194,6,false,'Stone_Paving_VM_Cob','',''},
  ['VM_Exit_Bridge__Stone_Paving_VM_CobB']={27.081,5.955,179.769,60.114,0.287,67.498,6,false,'Stone_Paving_VM_CobB','',''},
  ['VM_Exit_Bridge__Stone_Paving_VM_Edge']={0.0,5.95,216.7,23.86,0.22,7.26,6,false,'Stone_Paving_VM_Edge','',''},
  ['VM_Exit_Bridge__Stone_Paving_VM_Joint']={22.6,5.65,183.2,69.2,0.5,74.4,6,false,'Stone_Paving_VM_Joint','',''},
  ['VM_Exit_Bridge__Stone_VM_Base']={23.0,-15.95,184.0,72.4,42.9,76.0,6,true,'Stone_VM_Base','',''},
  ['VM_Exit_Bridge__Stone_VM_Dark']={25.0,-45.4,187.5,55.0,16.0,56.0,6,true,'Stone_VM_Dark','',''},
  ['VM_Exit_Bridge__Stone_VM_Grey']={22.6,6.274,183.993,71.5,1.826,76.015,6,true,'Stone_VM_Grey','',''},
  ['VM_Exit_Bridge__Stone_VM_Trim']={22.635,4.77,184.0,71.87,6.34,76.003,6,true,'Stone_VM_Trim','',''},
  ['VM_Exit_Bridge__Window_VM_Lamp']={27.644,14.12,188.628,61.411,1.6,58.256,6,true,'Window_VM_Lamp','',''},
  ['VM_Exit_Gate__Metal_VM_Bronze']={50.0,23.375,148.0,25.473,14.25,2.82,6,false,'Metal_VM_Bronze','','VM_Exit'},
  ['VM_Exit_Gate__Roof_VM_Terracotta']={50.0,24.335,148.0,32.4,10.531,8.0,6,true,'Roof_VM_Terracotta','','VM_Exit'},
  ['VM_Exit_Gate__Roof_VM_Terracotta_B']={49.985,20.531,148.411,19.33,2.863,4.311,6,true,'Roof_VM_Terracotta_B','','VM_Exit'},
  ['VM_Exit_Gate__Stone_VM_Grey']={50.024,13.071,147.997,30.907,14.666,6.584,6,true,'Stone_VM_Grey','','VM_Exit'},
  ['VM_Exit_Gate__Stone_VM_Mortar']={50.0,13.3,148.0,29.96,15.4,5.76,6,true,'Stone_VM_Mortar','','VM_Exit'},
  ['VM_Exit_Gate__Stone_VM_Trim']={50.0,20.47,148.0,31.7,1.26,7.3,6,true,'Stone_VM_Trim','','VM_Exit'},
  ['VM_Exit_Gate__Stone_VM_Warm']={50.0,13.054,147.999,30.919,14.744,6.594,6,true,'Stone_VM_Warm','','VM_Exit'},
  ['VM_Exit_Gate__Wood_VM_Plank']={50.0,12.2,147.6,18.5,12.2,13.48,6,false,'Wood_VM_Plank','','VM_Exit'},
  ['VM_Exit_Gate__Wood_VM_Timber']={50.0,14.11,147.6,19.04,13.921,13.6,6,false,'Wood_VM_Timber','','VM_Exit'},
  ['VM_Water_Canal__Water_VM']={18.5,-13.7,-45.0,300.0,32.6,78.0,7,false,'Water_VM','',''},
  ['VM_Veg_CN__Bark_VM']={-21.337,15.45,-56.054,133.804,20.5,119.839,8,true,'Bark_VM','',''},
  ['VM_Veg_CN__Flower_VM_Yellow']={5.196,7.946,-53.569,79.559,1.44,97.617,8,false,'Flower_VM_Yellow','',''},
  ['VM_Veg_CN__Leaf_VM_Light']={-21.485,27.208,-56.346,136.452,43.217,121.834,8,false,'Leaf_VM_Light','',''},
  ['VM_Veg_CN__Leaf_VM_Pine']={-20.319,23.869,-55.785,143.768,36.791,127.945,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_CN__Leaf_VM_Round']={-20.319,25.545,-55.785,143.768,39.89,127.945,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_CS__Bark_VM']={-28.292,12.218,116.265,120.302,14.166,68.951,8,true,'Bark_VM','',''},
  ['VM_Veg_CS__Flower_VM_Red']={-35.946,8.906,105.176,102.359,5.603,83.39,8,false,'Flower_VM_Red','',''},
  ['VM_Veg_CS__Leaf_VM_Light']={-24.053,20.678,93.118,135.938,30.157,116.424,8,false,'Leaf_VM_Light','',''},
  ['VM_Veg_CS__Leaf_VM_Pine']={-24.527,18.266,96.634,141.616,25.621,115.132,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_CS__Leaf_VM_Round']={-24.658,19.02,96.751,141.355,26.841,114.899,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_EN__Bark_VM']={104.862,15.418,-46.742,117.538,20.563,111.191,8,true,'Bark_VM','',''},
  ['VM_Veg_EN__Flower_VM_Pink']={119.998,7.512,-39.221,5.275,0.83,26.731,8,false,'Flower_VM_Pink','',''},
  ['VM_Veg_EN__Leaf_VM_Light']={104.982,27.208,-46.1,120.118,43.217,115.292,8,false,'Leaf_VM_Light','',''},
  ['VM_Veg_EN__Leaf_VM_Pine']={104.826,24.359,-47.134,125.839,35.811,119.8,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_EN__Leaf_VM_Round']={104.826,24.991,-47.134,125.839,38.782,119.8,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_ES__Bark_VM']={106.444,14.019,80.337,107.871,17.763,141.377,8,true,'Bark_VM','',''},
  ['VM_Veg_ES__Flower_VM_Yellow']={106.0,6.906,60.963,117.755,1.627,88.573,8,false,'Flower_VM_Yellow','',''},
  ['VM_Veg_ES__Leaf_VM_Light']={105.336,24.51,78.695,119.202,37.82,144.556,8,false,'Leaf_VM_Light','',''},
  ['VM_Veg_ES__Leaf_VM_Pine']={106.005,21.474,78.953,115.283,32.036,149.049,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_ES__Leaf_VM_Round']={105.074,22.002,78.953,117.418,32.804,149.049,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_WN__Bark_VM']={-128.755,13.077,-46.39,78.565,15.863,113.595,8,true,'Bark_VM','',''},
  ['VM_Veg_WN__Flower_VM_Yellow']={-98.668,7.513,-55.007,8.839,0.722,27.555,8,false,'Flower_VM_Yellow','',''},
  ['VM_Veg_WN__Leaf_VM_Light']={-128.266,21.672,-49.71,83.21,32.144,123.644,8,false,'Leaf_VM_Light','',''},
  ['VM_Veg_WN__Leaf_VM_Pine']={-126.862,19.137,-47.91,87.813,27.363,124.767,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_WN__Leaf_VM_Round']={-126.862,19.369,-47.91,87.813,26.645,124.767,8,false,'Leaf_VM_Round','',''},
  ['VM_Veg_WS__Bark_VM']={-153.622,12.437,85.354,129.233,14.594,136.516,8,true,'Bark_VM','',''},
  ['VM_Veg_WS__Flower_VM_Pink']={-190.141,6.483,22.977,1.524,0.667,1.192,8,false,'Flower_VM_Pink','',''},
  ['VM_Veg_WS__Leaf_VM_Light']={-153.904,20.872,85.818,129.669,30.544,138.946,8,false,'Leaf_VM_Light','',''},
  ['VM_Veg_WS__Leaf_VM_Pine']={-155.365,18.384,84.856,135.874,25.861,144.557,8,false,'Leaf_VM_Pine','',''},
  ['VM_Veg_WS__Leaf_VM_Round']={-155.365,18.395,84.856,135.874,25.59,144.557,8,false,'Leaf_VM_Round','',''},
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
  {'COL_Canal_005','Block',{-124.0,9.0,-5.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,1.0,6.0},false},
  {'COL_Canal_006','Block',{-62.0,9.0,-5.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{102.0,1.0,6.0},false},
  {'COL_Canal_007','Block',{54.0,9.0,-5.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{86.0,1.0,6.0},false},
  {'COL_Canal_008','Block',{134.5,9.0,-5.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{63.0,1.0,6.0},false},
  {'COL_Canal_009','Block',{-124.0,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.0,1.0,6.0},false},
  {'COL_Canal_010','Block',{-62.0,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{102.0,1.0,6.0},false},
  {'COL_Canal_011','Block',{21.5,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{21.0,1.0,6.0},false},
  {'COL_Canal_012','Block',{68.5,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{57.0,1.0,6.0},false},
  {'COL_Canal_013','Block',{134.5,10.0,-18.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{63.0,1.0,6.0},false},
  {'COL_CourtArch_001','Block',{-90.583,13.2,56.501},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,14.4},false},
  {'COL_CourtArch_002','Block',{-87.576,13.2,74.472},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.6,2.6,14.4},false},
  {'COL_CourtBench_001','Block',{-142.084,6.8,98.488},{-0.883,0.0,-0.469},{-0.469,0.0,0.883},{4.4,1.8,1.6},false},
  {'COL_CourtBench_002','Block',{-153.715,6.8,87.451},{-0.515,0.0,-0.857},{-0.857,0.0,0.515},{4.4,1.8,1.6},false},
  {'COL_CourtBench_003','Block',{-158.0,6.8,72.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{4.4,1.8,1.6},false},
  {'COL_CourtBench_004','Block',{-153.715,6.8,56.549},{0.515,0.0,-0.857},{-0.857,0.0,-0.515},{4.4,1.8,1.6},false},
  {'COL_CourtBench_005','Block',{-142.084,6.8,45.512},{0.883,0.0,-0.469},{-0.469,0.0,-0.883},{4.4,1.8,1.6},false},
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
  {'COL_CourtWall_001','Block',{-122.714,6.6,31.846},{0.991,0.0,0.131},{0.131,0.0,-0.991},{3.533,1.2,1.2},false},
  {'COL_CourtWall_002','Block',{-119.234,6.6,32.46},{0.976,0.0,0.216},{0.216,0.0,-0.976},{3.533,1.2,1.2},false},
  {'COL_CourtWall_003','Block',{-94.593,6.6,49.104},{0.565,0.0,0.825},{0.825,0.0,-0.565},{5.051,1.2,1.2},false},
  {'COL_CourtWall_004','Block',{-92.003,6.6,53.44},{0.458,0.0,0.889},{0.889,0.0,-0.458},{5.051,1.2,1.2},false},
  {'COL_CourtWall_005','Block',{-87.968,6.6,78.137},{-0.152,0.0,0.988},{0.988,0.0,0.152},{5.671,1.2,1.2},false},
  {'COL_CourtWall_006','Block',{-89.217,6.6,83.669},{-0.288,0.0,0.958},{0.958,0.0,0.288},{5.671,1.2,1.2},false},
  {'COL_CourtWall_007','Block',{-91.228,6.6,88.972},{-0.419,0.0,0.908},{0.908,0.0,0.419},{5.671,1.2,1.2},false},
  {'COL_CourtWall_008','Block',{-93.959,6.6,93.942},{-0.542,0.0,0.841},{0.841,0.0,0.542},{5.671,1.2,1.2},false},
  {'COL_CourtWall_009','Block',{-97.358,6.6,98.482},{-0.654,0.0,0.757},{0.757,0.0,0.654},{5.671,1.2,1.2},false},
  {'COL_CourtWall_010','Block',{-101.358,6.6,102.503},{-0.753,0.0,0.658},{0.658,0.0,0.753},{5.671,1.2,1.2},false},
  {'COL_CourtWall_011','Block',{-105.88,6.6,105.926},{-0.838,0.0,0.546},{0.546,0.0,0.838},{5.671,1.2,1.2},false},
  {'COL_CourtWall_012','Block',{-110.836,6.6,108.683},{-0.906,0.0,0.424},{0.424,0.0,0.906},{5.671,1.2,1.2},false},
  {'COL_CourtWall_013','Block',{-116.129,6.6,110.721},{-0.956,0.0,0.293},{0.293,0.0,0.956},{5.671,1.2,1.2},false},
  {'COL_CourtWall_014','Block',{-121.654,6.6,112.0},{-0.988,0.0,0.157},{0.157,0.0,0.988},{5.671,1.2,1.2},false},
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
  {'COL_FootBar_001','Block',{-117.9,9.75,-11.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.8,19.4,7.5},false},
  {'COL_FootBar_002','Block',{-114.1,9.75,-11.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.8,19.4,7.5},false},
  {'COL_FootBar_003','Block',{98.1,9.75,-11.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.8,19.4,7.5},false},
  {'COL_FootBar_004','Block',{101.9,9.75,-11.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.8,19.4,7.5},false},
  {'COL_Foot_001','Ramp',{-116.0,6.357,-6.881},{-0.0,0.161,-0.987},{-1.0,0.0,0.0},{10.538,4.0,1.0},false},
  {'COL_Foot_002','Ramp',{-116.0,6.851,-17.066},{-0.0,-0.068,-0.998},{-1.0,0.0,0.0},{10.224,4.0,1.0},false},
  {'COL_Foot_003','Ramp',{100.0,6.357,-6.881},{-0.0,0.161,-0.987},{-1.0,0.0,0.0},{10.538,4.0,1.0},false},
  {'COL_Foot_004','Ramp',{100.0,6.851,-17.066},{-0.0,-0.068,-0.998},{-1.0,0.0,0.0},{10.224,4.0,1.0},false},
  {'COL_Forge_008','Block',{23.4,11.45,-77.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.8,1.0,8.9},true},
  {'COL_Forge_009','Block',{0.0,23.5,-86.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.0,15.6,33.0},true},
  {'COL_Forge_010','Block',{0.0,67.6,-86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{13.0,13.0,55.2},true},
  {'COL_Forge_011','Block',{-26.0,14.6,-62.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{18.2,23.0,15.8},true},
  {'COL_Forge_012','Block',{-16.3,21.3,-64.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,28.4,28.6},true},
  {'COL_Forge_013','Block',{14.3,21.3,-64.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.4,28.4,28.6},true},
  {'COL_Forge_014','Block',{-1.0,21.3,-77.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{29.2,1.4,28.6},true},
  {'COL_Forge_015','Block',{-16.0,19.5,-51.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,25.0},true},
  {'COL_Forge_016','Block',{14.0,19.5,-51.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.8,2.8,25.0},true},
  {'COL_Forge_017','Block',{-1.0,33.3,-51.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{36.0,2.8,2.6},true},
  {'COL_Forge_018','Block',{-0.9,13.9,-73.85},{1.0,0.0,0.0},{0.0,0.0,-1.0},{19.0,6.3,13.8},true},
  {'COL_Forge_019','Block',{-0.9,30.35,-74.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{17.0,6.0,19.1},true},
  {'COL_FrgMill_001','Block',{25.5,10.5,-65.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.2,21.6,7.0},false},
  {'COL_FrgMill_002','Block',{36.0,12.25,-66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.4,16.2,10.5},false},
  {'COL_FrgPost_001','Block',{19.4,10.6,-52.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,7.2},false},
  {'COL_FrgPost_002','Block',{28.2,10.6,-52.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,7.2},false},
  {'COL_FrgPost_003','Block',{31.25,10.6,-52.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,7.2},false},
  {'COL_FrgPost_004','Block',{31.25,10.6,-61.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,7.2},false},
  {'COL_FrgPost_005','Block',{31.25,10.6,-71.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,7.2},false},
  {'COL_FrgPost_006','Block',{31.4,10.6,-77.65},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,7.2},false},
  {'COL_FrgProps_001','Block',{-12.25,10.004,-69.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.7,4.8,6.008},false},
  {'COL_FrgProps_002','Block',{-13.4,13.3,-62.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.2,1.2,12.6},false},
  {'COL_FrgProps_003','Block',{-13.3,8.2,-58.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,5.8,2.4},false},
  {'COL_FrgProps_004','Block',{-13.6,8.1,-53.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.6,2.0,2.2},false},
  {'COL_FrgProps_005','Block',{10.1,8.2,-57.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.4,4.0,2.4},false},
  {'COL_FrgProps_006','Block',{10.8,8.5,-73.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.4,2.8,3.0},false},
  {'COL_FrgProps_007','Block',{-20.8,10.4,-47.6},{-1.0,0.0,0.0},{0.0,0.0,1.0},{13.2,2.4,6.8},false},
  {'COL_FrgProps_008','Block',{20.0,10.4,-48.6},{-1.0,0.0,0.0},{0.0,0.0,1.0},{9.3,2.4,6.8},false},
  {'COL_FrgProps_009','Block',{-32.6,8.15,-48.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.6,4.0,2.3},false},
  {'COL_FrgProps_010','Block',{29.4,8.15,-50.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.6,2.4,2.3},false},
  {'COL_FrgProps_011','Block',{25.4,8.45,-48.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,2.4,2.9},false},
  {'COL_FrgProps_012','Block',{30.8,8.2,-47.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.6,3.0,2.4},false},
  {'COL_Gate_003','Block',{62.2,13.5,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.4,6.4,15.0},false},
  {'COL_Gate_004','Block',{37.8,13.5,148.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{6.4,6.4,15.0},false},
  {'COL_Gate_005','Block',{59.1,10.8,143.9},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.7,6.4,9.6},false},
  {'COL_Gate_006','Block',{40.9,10.8,151.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.7,6.4,9.6},false},
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
  {'COL_House_019','Block',{-17.0,13.6,-1.2},{-0.0,0.0,1.0},{1.0,0.0,0.0},{8.8,11.0,15.8},true},
  {'COL_House_020','Block',{-16.8,16.6,9.5},{-0.0,0.0,1.0},{1.0,0.0,0.0},{13.2,12.6,21.8},true},
  {'COL_House_021','Block',{-28.95,13.6,13.4},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{12.2,12.0,15.8},true},
  {'COL_House_022','Block',{16.6,16.6,-0.75},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{9.7,11.6,21.8},true},
  {'COL_House_023','Block',{17.65,13.6,9.9},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{12.2,12.1,15.8},true},
  {'COL_House_024','Block',{30.25,13.6,12.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{13.7,12.0,15.8},true},
  {'COL_House_025','Block',{47.775,16.6,82.784},{-0.577,0.0,-0.817},{-0.817,0.0,0.577},{13.2,11.6,21.8},true},
  {'COL_House_026','Block',{55.283,13.6,94.445},{-0.486,0.0,-0.874},{-0.874,0.0,0.486},{12.2,11.1,15.8},true},
  {'COL_House_027','Block',{62.432,13.6,113.874},{-0.196,0.0,-0.981},{-0.981,0.0,0.196},{11.7,11.0,15.8},true},
  {'COL_House_028','Block',{64.568,12.85,125.847},{-0.053,0.0,-0.999},{-0.999,0.0,0.053},{9.2,10.2,14.0},true},
  {'COL_House_029','Block',{30.632,13.6,103.507},{0.486,0.0,0.874},{0.874,0.0,-0.486},{13.7,11.0,15.8},true},
  {'COL_House_030','Block',{34.257,13.35,111.746},{0.346,0.0,0.938},{0.938,0.0,-0.346},{8.8,10.2,15.0},true},
  {'COL_House_031','Block',{37.692,16.6,121.219},{0.196,0.0,0.981},{0.981,0.0,-0.196},{9.8,11.6,21.8},true},
  {'COL_House_032','Block',{-15.0,14.6,-28.1},{-0.0,0.0,1.0},{1.0,0.0,0.0},{14.0,11.0,15.8},true},
  {'COL_House_033','Block',{14.95,14.6,-28.1},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{14.0,11.1,15.8},true},
  {'COL_House_034','Block',{42.599,16.6,21.808},{-0.207,0.0,-0.978},{-0.978,0.0,0.207},{9.8,11.6,21.8},true},
  {'COL_House_035','Block',{44.772,13.6,30.65},{-0.207,0.0,-0.978},{-0.978,0.0,0.207},{8.8,11.0,15.8},true},
  {'COL_House_036','Block',{56.5,13.6,30.6},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{10.4,10.2,15.5},true},
  {'COL_House_037','Block',{29.0,14.1,1.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{12.2,10.2,16.5},true},
  {'COL_House_038','Block',{40.5,12.85,1.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{11.2,10.2,14.0},true},
  {'COL_House_039','Block',{-40.908,13.6,22.982},{-0.233,0.0,0.972},{0.972,0.0,0.233},{10.8,11.0,15.8},true},
  {'COL_House_040','Block',{-43.446,13.6,33.788},{-0.233,0.0,0.972},{0.972,0.0,0.233},{11.8,11.1,15.8},true},
  {'COL_House_041','Block',{-42.0,13.85,1.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{12.2,10.2,16.0},true},
  {'COL_House_042','Block',{-52.5,13.1,1.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.2,10.2,14.5},true},
  {'COL_House_043','Block',{-22.0,13.1,122.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{10.2,10.2,14.5},true},
  {'COL_House_044','Block',{-11.3,14.35,122.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.2,10.2,17.0},true},
  {'COL_House_045','Block',{3.7,13.6,122.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{12.2,10.2,15.5},true},
  {'COL_House_046','Block',{15.4,12.85,122.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.2,10.2,14.0},true},
  {'COL_House_047','Block',{42.549,13.6,62.444},{0.295,0.0,-0.955},{-0.955,0.0,-0.295},{18.8,11.0,15.8},true},
  {'COL_House_049','Block',{56.5,13.1,55.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{9.2,10.2,14.5},true},
  {'COL_House_050','Block',{-39.276,13.6,72.531},{0.596,0.0,0.803},{0.803,0.0,-0.596},{13.2,11.1,15.8},true},
  {'COL_House_051','Block',{-31.443,13.6,83.156},{0.596,0.0,0.803},{0.803,0.0,-0.596},{13.6,11.0,15.8},true},
  {'COL_House_052','Block',{-56.1,13.6,71.439},{0.973,0.0,-0.232},{-0.232,0.0,-0.973},{13.7,11.0,15.8},true},
  {'COL_House_053','Block',{-68.41,13.35,74.784},{0.973,0.0,-0.232},{-0.232,0.0,-0.973},{12.2,10.2,15.0},true},
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
  {'COL_IsleNotch_001','Block',{-10.2,9.0,212.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.6,1.1,6.0},false},
  {'COL_IsleNotch_002','Block',{10.2,9.0,212.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.6,1.1,6.0},false},
  {'COL_Kiosk_001','Block',{-16.1,13.7,97.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,8.2},false},
  {'COL_Kiosk_002','Block',{-11.9,13.7,97.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,8.2},false},
  {'COL_Kiosk_003','Block',{-16.1,13.7,102.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,8.2},false},
  {'COL_Kiosk_004','Block',{-11.9,13.7,102.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,8.2},false},
  {'COL_PlazaBench_001','Block',{28.015,6.8,30.384},{0.574,0.0,0.819},{0.819,0.0,-0.574},{4.4,1.8,1.6},false},
  {'COL_PlazaBench_002','Block',{-30.472,6.8,34.474},{0.454,0.0,-0.891},{-0.891,0.0,-0.454},{4.4,1.8,1.6},false},
  {'COL_PlazaBench_003','Block',{32.792,6.8,59.713},{-0.284,0.0,0.959},{0.959,0.0,0.284},{4.4,1.8,1.6},false},
  {'COL_PlazaBench_004','Block',{-26.578,6.8,71.523},{-0.629,0.0,-0.777},{-0.777,0.0,0.629},{4.4,1.8,1.6},false},
  {'COL_PlazaBorder_001','Block',{29.415,6.5,26.18},{0.629,0.0,0.777},{0.777,0.0,-0.629},{5.281,2.9,1.0},false},
  {'COL_PlazaBorder_002','Block',{32.444,6.5,30.506},{0.515,0.0,0.857},{0.857,0.0,-0.515},{5.281,2.9,1.0},false},
  {'COL_PlazaBorder_003','Block',{-33.207,6.5,31.837},{0.48,0.0,-0.877},{-0.877,0.0,-0.48},{3.787,2.9,1.0},false},
  {'COL_PlazaBorder_004','Block',{36.254,6.5,60.877},{-0.287,0.0,0.958},{0.958,0.0,0.287},{3.231,2.9,1.0},false},
  {'COL_PlazaBorder_005','Block',{-28.59,6.5,74.804},{-0.655,0.0,-0.755},{-0.755,0.0,0.655},{3.366,2.9,1.0},false},
  {'COL_PlazaBorder_006','Block',{-30.681,6.5,72.166},{-0.586,0.0,-0.811},{-0.811,0.0,0.586},{3.366,2.9,1.0},false},
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
  {'COL_PropBench_001','Block',{25.0,6.5,92.0},{0.406,0.0,0.914},{0.914,0.0,-0.406},{4.0,1.6,1.4},false},
  {'COL_PropBench_002','Block',{-45.0,6.5,108.0},{0.958,0.0,0.287},{0.287,0.0,-0.958},{4.0,1.6,1.4},false},
  {'COL_PropBench_003','Block',{112.0,6.5,66.0},{0.196,0.0,-0.981},{-0.981,0.0,-0.196},{4.0,1.6,1.4},false},
  {'COL_PropBench_004','Block',{64.0,7.5,-25.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.0,1.6,1.4},false},
  {'COL_PropBench_005','Block',{-64.0,7.5,-25.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.0,1.6,1.4},false},
  {'COL_PropCart_001','Block',{-14.0,7.5,143.0},{0.981,0.0,0.196},{0.196,0.0,-0.981},{7.0,4.6,3.4},false},
  {'COL_PropCart_002','Block',{-80.0,7.5,108.0},{0.958,0.0,0.287},{0.287,0.0,-0.958},{7.0,4.6,3.4},false},
  {'COL_PropCart_003','Block',{100.0,7.5,48.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{7.0,4.6,3.4},false},
  {'COL_PropCart_004','Block',{-53.153,8.5,-36.961},{0.958,0.0,-0.287},{-0.287,0.0,-0.958},{7.0,4.6,3.4},false},
  {'COL_PropGroup_001','Block',{55.994,7.397,120.795},{-0.1,0.0,-0.995},{-0.995,0.0,0.1},{4.2,2.4,2.6},false},
  {'COL_PropGroup_002','Block',{46.0,7.212,138.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{4.4,3.4,2.4},false},
  {'COL_PropGroup_003','Block',{54.925,7.403,138.242},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{4.2,2.4,2.6},false},
  {'COL_PropGroup_004','Block',{-62.0,7.293,64.0},{0.981,0.0,0.196},{0.196,0.0,-0.981},{4.4,3.4,2.4},false},
  {'COL_PropGroup_005','Block',{-75.0,7.22,67.0},{0.981,0.0,0.196},{0.196,0.0,-0.981},{4.2,2.4,2.6},false},
  {'COL_PropGroup_006','Block',{-72.0,7.0,-2.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.4,3.4,2.4},false},
  {'COL_PropGroup_007','Block',{-66.0,7.1,6.0},{-0.196,0.0,0.981},{0.981,0.0,0.196},{4.2,2.4,2.6},false},
  {'COL_PropGroup_008','Block',{-110.0,7.075,22.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{5.0,4.2,2.55},false},
  {'COL_PropGroup_009','Block',{-70.0,7.075,86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.0,4.2,2.55},false},
  {'COL_PropGroup_010','Block',{-24.0,7.075,134.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.4,4.2,2.55},false},
  {'COL_PropGroup_011','Block',{70.0,7.1,61.5},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.2,2.4,2.6},false},
  {'COL_PropGroup_012','Block',{85.0,7.0,61.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.4,3.4,2.4},false},
  {'COL_PropGroup_013','Block',{-44.0,8.075,-50.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{5.4,4.2,2.55},false},
  {'COL_PropGroup_014','Block',{106.0,8.0,-27.0},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{4.4,3.4,2.4},false},
  {'COL_PropGroup_015','Block',{37.0,7.0,136.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{4.4,3.4,2.4},false},
  {'COL_PropPost_001','Block',{-65.0,8.6,104.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.6,0.6,5.6},false},
  {'COL_PropPost_002','Block',{-55.0,8.6,104.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.6,0.6,5.6},false},
  {'COL_PropPost_003','Block',{6.5,8.6,137.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.6,0.6,5.6},false},
  {'COL_PropPost_004','Block',{-2.5,8.6,137.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.6,0.6,5.6},false},
  {'COL_PropPost_005','Block',{74.5,9.6,-40.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.6,0.6,5.6},false},
  {'COL_PropPost_006','Block',{65.5,9.6,-40.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.6,0.6,5.6},false},
  {'COL_PropSign_001','Block',{-17.5,10.024,78.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,7.8},false},
  {'COL_PropSign_002','Block',{9.78,10.042,15.832},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,7.8},false},
  {'COL_PropSign_003','Block',{-30.922,10.05,60.343},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,7.8},false},
  {'COL_PropSign_004','Block',{33.117,10.032,51.546},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,7.8},false},
  {'COL_PropSign_005','Block',{-95.0,10.03,79.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,7.8},false},
  {'COL_PropSign_006','Block',{20.0,9.7,84.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,7.8},false},
  {'COL_PropWall_001','Block',{-100.883,6.5,124.546},{0.995,0.0,0.1},{0.1,0.0,-0.995},{22.0,1.3,1.4},false},
  {'COL_PropWall_002','Block',{-79.922,6.5,131.843},{0.981,0.0,-0.196},{-0.196,0.0,-0.981},{16.0,1.3,1.4},false},
  {'COL_PropWall_003','Block',{127.284,6.5,20.669},{0.1,0.0,0.995},{0.995,0.0,-0.1},{22.0,1.3,1.4},false},
  {'COL_PropWall_004','Block',{140.862,6.5,75.547},{0.97,0.0,0.243},{0.243,0.0,-0.97},{20.0,1.3,1.4},false},
  {'COL_PropWall_005','Block',{90.0,7.5,-70.0},{0.995,0.0,0.1},{0.1,0.0,-0.995},{24.0,1.3,1.4},false},
  {'COL_PropWall_006','Block',{-81.046,7.5,-89.065},{0.989,0.0,-0.148},{-0.148,0.0,-0.989},{20.0,1.3,1.4},false},
  {'COL_Race_001','Block',{32.5,10.0,-51.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,67.0,6.0},false},
  {'COL_Race_002','Block',{39.5,10.0,-51.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,67.0,6.0},false},
  {'COL_Race_003','Block',{36.0,10.0,-84.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{8.0,1.0,6.0},false},
  {'COL_RankHall_002','Block',{-87.589,16.6,11.746},{-0.917,0.0,0.399},{0.399,0.0,0.917},{30.2,11.6,21.8},true},
  {'COL_RankMast_001','Block',{-50.355,16.95,20.638},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,21.9},false},
  {'COL_RankMast_002','Block',{-106.48,16.95,45.04},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,21.9},false},
  {'COL_Rank_001','Block',{-81.209,4.9,26.419},{-0.917,0.0,0.399},{0.399,0.0,0.917},{58.0,20.0,3.0},false},
  {'COL_ShopFloor_001','Block',{76.0,4.9,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,26.0,3.0},false},
  {'COL_Shop_012','Block',{62.5,11.4,35.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,10.0,10.0},true},
  {'COL_Shop_013','Block',{62.5,11.4,51.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,10.0,10.0},true},
  {'COL_Shop_014','Block',{62.5,15.9,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,6.0,1.0},true},
  {'COL_Shop_015','Block',{76.0,11.4,30.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.0,10.0},true},
  {'COL_Shop_016','Block',{76.0,11.4,55.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,1.0,10.0},true},
  {'COL_Shop_017','Block',{89.5,11.4,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,26.0,10.0},true},
  {'COL_Shop_018','Block',{76.0,19.15,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{28.0,26.0,6.5},true},
  {'COL_Shop_019','Block',{75.125,8.175,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.25,12.4,3.55},false},
  {'COL_Shop_020','Block',{88.19,10.7,43.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.62,20.4,8.6},true},
  {'COL_Shop_021','Block',{76.0,9.7,31.82},{1.0,0.0,0.0},{0.0,0.0,-1.0},{11.0,1.4,6.6},true},
  {'COL_Shop_022','Block',{76.0,9.7,54.18},{1.0,0.0,0.0},{0.0,0.0,-1.0},{11.0,1.4,6.6},true},
  {'COL_Shop_023','Block',{61.25,9.45,35.3},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.5,5.7,6.9},true},
  {'COL_Shop_024','Block',{61.25,9.45,50.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.5,5.7,6.9},true},
  {'COL_SpawnCheek_001','Block',{-13.8,8.6,83.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.6,9.9,5.2},false},
  {'COL_SpawnCheek_002','Block',{13.8,8.6,83.05},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.6,9.9,5.2},false},
  {'COL_SpawnRail_001','Block',{-15.525,11.2,88.55},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.25,1.0,3.2},false},
  {'COL_SpawnRail_002','Block',{-17.95,11.2,90.05},{-0.707,0.0,0.707},{0.707,0.0,0.707},{4.643,1.0,3.2},false},
  {'COL_SpawnRail_003','Block',{-19.45,11.2,100.0},{-0.0,0.0,1.0},{1.0,0.0,0.0},{17.3,1.0,3.2},false},
  {'COL_SpawnRail_004','Block',{-17.95,11.2,109.95},{0.707,0.0,0.707},{0.707,0.0,-0.707},{4.643,1.0,3.2},false},
  {'COL_SpawnRail_005','Block',{0.0,11.2,111.45},{1.0,0.0,0.0},{0.0,0.0,-1.0},{33.3,1.0,3.2},false},
  {'COL_SpawnRail_006','Block',{17.95,11.2,109.95},{0.707,0.0,-0.707},{-0.707,0.0,-0.707},{4.643,1.0,3.2},false},
  {'COL_SpawnRail_007','Block',{19.45,11.2,100.0},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{17.3,1.0,3.2},false},
  {'COL_SpawnRail_008','Block',{17.95,11.2,90.05},{-0.707,0.0,-0.707},{-0.707,0.0,0.707},{4.643,1.0,3.2},false},
  {'COL_SpawnRail_009','Block',{15.525,11.2,88.55},{-1.0,0.0,-0.0},{-0.0,0.0,1.0},{2.25,1.0,3.2},false},
  {'COL_Spawn_001','Block',{-18.0,7.7,100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,22.0,3.8},false},
  {'COL_Spawn_002','Block',{0.0,7.7,100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{32.0,24.0,3.8},false},
  {'COL_Spawn_010','Block',{18.0,7.7,100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,22.0,3.8},false},
  {'COL_Spawn_015','Ramp',{0.0,7.344,83.405},{-0.0,0.41,0.912},{1.0,0.0,0.0},{8.773,26.0,1.0},false},
  {'COL_Spawn_016','Block',{0.0,9.1,87.75},{-0.0,0.0,1.0},{1.0,0.0,0.0},{1.1,26.0,1.0},false},
  {'COL_StreetProps_001','Block',{56.486,7.7,111.167},{0.271,0.0,0.962},{0.962,0.0,-0.271},{7.0,4.6,3.4},false},
  {'COL_StreetProps_002','Block',{57.879,7.15,116.604},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,1.8,2.3},false},
  {'COL_StreetProps_003','Block',{58.526,7.15,117.801},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,1.8,2.3},false},
  {'COL_StreetProps_004','Block',{35.287,7.15,101.589},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,1.8,2.3},false},
  {'COL_StreetProps_005','Block',{35.704,7.15,102.959},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.8,1.8,2.3},false},
  {'COL_StreetProps_006','Block',{58.589,6.95,119.894},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,1.9},false},
  {'COL_StreetProps_007','Block',{43.152,6.95,130.859},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,1.9},false},
  {'COL_TProps_001','Block',{-10.6,10.5,17.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_002','Block',{10.6,10.5,17.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_003','Block',{-27.0,10.5,31.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_004','Block',{27.0,10.5,31.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{0.9,0.9,9.0},false},
  {'COL_TProps_005','Block',{11.2,7.15,4.95},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.4,5.3,2.3},false},
  {'COL_TProps_006','Block',{-20.6,7.7,22.0},{-0.482,0.0,-0.876},{-0.876,0.0,0.482},{7.0,4.6,3.4},false},
  {'COL_TProps_007','Block',{-25.05,7.15,21.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{3.1,2.8,2.3},false},
  {'COL_TownProps_001','Block',{31.883,10.86,35.805},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_002','Block',{34.815,10.86,52.435},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_003','Block',{29.915,10.86,67.975},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_004','Block',{-32.795,10.86,61.937},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_005','Block',{-13.8,11.5,79.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,6.6},false},
  {'COL_TownProps_006','Block',{13.8,11.5,79.1},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,6.6},false},
  {'COL_TownProps_007','Block',{-44.052,9.9,62.784},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_008','Block',{-82.697,9.9,71.71},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_009','Block',{32.703,9.9,96.639},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_010','Block',{58.857,9.9,127.684},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_011','Block',{60.0,9.9,36.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_012','Block',{60.0,9.9,49.8},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_013','Block',{-9.9,10.9,-35.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_014','Block',{9.9,10.9,-35.2},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,7.8},false},
  {'COL_TownProps_015','Block',{-51.584,10.8,26.842},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_016','Block',{-101.105,10.8,48.373},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_017','Block',{-145.934,10.86,105.729},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_018','Block',{-160.744,10.86,91.674},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_019','Block',{-166.2,10.86,72.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_020','Block',{-160.744,10.86,52.326},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_TownProps_021','Block',{-145.934,10.86,38.271},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.0,1.0,9.6},false},
  {'COL_VegTrunk_001','Block',{69.126,9.6,101.566},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.669,2.669,8.0},false},
  {'COL_VegTrunk_002','Block',{72.0,9.6,84.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.458,2.458,8.0},false},
  {'COL_VegTrunk_003','Block',{77.0,9.6,95.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.64,2.64,8.0},false},
  {'COL_VegTrunk_004','Block',{80.0,9.6,117.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.405,2.405,8.0},false},
  {'COL_VegTrunk_005','Block',{77.0,9.6,134.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.14,2.14,8.0},false},
  {'COL_VegTrunk_006','Block',{62.0,9.6,72.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_007','Block',{27.0,9.6,129.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.352,2.352,8.0},false},
  {'COL_VegTrunk_008','Block',{54.01,9.6,67.317},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.669,2.669,8.0},false},
  {'COL_VegTrunk_009','Block',{26.0,9.6,142.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.232,2.232,8.0},false},
  {'COL_VegTrunk_010','Block',{29.149,9.6,149.672},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.194,2.194,8.0},false},
  {'COL_VegTrunk_011','Block',{71.01,9.6,149.317},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.299,2.299,8.0},false},
  {'COL_VegTrunk_012','Block',{-34.0,9.6,126.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.352,2.352,8.0},false},
  {'COL_VegTrunk_013','Block',{-4.0,9.6,136.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.216,2.216,8.0},false},
  {'COL_VegTrunk_014','Block',{14.0,9.6,138.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.246,2.246,8.0},false},
  {'COL_VegTrunk_015','Block',{-20.0,9.6,140.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.436,2.436,8.0},false},
  {'COL_VegTrunk_016','Block',{-50.0,9.6,88.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.64,2.64,8.0},false},
  {'COL_VegTrunk_017','Block',{-63.9,9.6,86.824},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.352,2.352,8.0},false},
  {'COL_VegTrunk_018','Block',{-42.0,9.6,98.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.141,2.141,8.0},false},
  {'COL_VegTrunk_019','Block',{-78.9,9.6,84.824},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.236,2.236,8.0},false},
  {'COL_VegTrunk_020','Block',{-26.0,9.6,98.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.232,2.232,8.0},false},
  {'COL_VegTrunk_021','Block',{-65.874,9.6,2.566},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.669,2.669,8.0},false},
  {'COL_VegTrunk_022','Block',{97.0,9.6,40.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.352,2.352,8.0},false},
  {'COL_VegTrunk_023','Block',{98.0,9.6,56.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.412,2.412,8.0},false},
  {'COL_VegTrunk_024','Block',{70.0,9.6,22.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.236,2.236,8.0},false},
  {'COL_VegTrunk_025','Block',{64.0,9.6,11.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.774,2.774,8.0},false},
  {'COL_VegTrunk_026','Block',{67.01,9.6,65.317},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.141,2.141,8.0},false},
  {'COL_VegTrunk_027','Block',{58.0,9.6,6.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_028','Block',{-48.0,10.6,-62.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.88,2.88,8.0},false},
  {'COL_VegTrunk_029','Block',{-46.0,10.6,-84.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.64,2.64,8.0},false},
  {'COL_VegTrunk_030','Block',{-12.0,10.6,-104.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.742,2.742,8.0},false},
  {'COL_VegTrunk_031','Block',{14.0,10.6,-106.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.458,2.458,8.0},false},
  {'COL_VegTrunk_032','Block',{50.0,10.6,-78.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.324,2.324,8.0},false},
  {'COL_VegTrunk_033','Block',{52.0,10.6,-56.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.88,2.88,8.0},false},
  {'COL_VegTrunk_034','Block',{-38.0,10.6,-100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.458,2.458,8.0},false},
  {'COL_VegTrunk_035','Block',{34.0,10.6,-100.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.436,2.436,8.0},false},
  {'COL_VegTrunk_036','Block',{-37.851,10.6,-42.328},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.986,2.986,8.0},false},
  {'COL_VegTrunk_037','Block',{47.772,10.6,-41.127},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.986,2.986,8.0},false},
  {'COL_VegTrunk_038','Block',{-31.0,10.6,-27.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.232,2.232,8.0},false},
  {'COL_VegTrunk_039','Block',{-58.0,10.6,-38.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.64,2.64,8.0},false},
  {'COL_VegTrunk_040','Block',{62.0,10.6,-42.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.352,2.352,8.0},false},
  {'COL_VegTrunk_041','Block',{-116.978,9.6,9.264},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.14,2.14,8.0},false},
  {'COL_VegTrunk_042','Block',{-123.918,9.6,149.893},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_043','Block',{-164.619,9.6,140.87},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_044','Block',{-194.859,9.6,112.173},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_045','Block',{-206.0,9.6,72.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_046','Block',{-194.859,9.6,31.827},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_047','Block',{-164.619,9.6,3.13},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_048','Block',{-121.0,9.6,20.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.141,2.141,8.0},false},
  {'COL_VegTrunk_049','Block',{-98.0,9.6,122.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.194,2.194,8.0},false},
  {'COL_VegTrunk_050','Block',{-210.9,9.6,72.824},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.246,2.246,8.0},false},
  {'COL_VegTrunk_051','Block',{-204.99,9.6,41.317},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.141,2.141,8.0},false},
  {'COL_VegTrunk_052','Block',{-206.0,9.6,104.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.088,2.088,8.0},false},
  {'COL_VegTrunk_053','Block',{-92.0,9.6,113.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.334,2.334,8.0},false},
  {'COL_VegTrunk_054','Block',{-216.157,9.6,91.684},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.019,2.019,8.0},false},
  {'COL_VegTrunk_055','Block',{-81.002,9.6,143.804},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.337,2.337,8.0},false},
  {'COL_VegTrunk_056','Block',{-216.107,9.6,101.355},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.432,2.432,8.0},false},
  {'COL_VegTrunk_057','Block',{-1.706,9.6,143.622},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.89,1.89,8.0},false},
  {'COL_VegTrunk_058','Block',{-101.883,9.6,146.575},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.192,2.192,8.0},false},
  {'COL_VegTrunk_059','Block',{-93.355,10.6,-86.48},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.661,2.661,8.0},false},
  {'COL_VegTrunk_060','Block',{-80.063,9.6,123.481},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.312,2.312,8.0},false},
  {'COL_VegTrunk_061','Block',{44.251,10.6,-99.025},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.335,2.335,8.0},false},
  {'COL_VegTrunk_062','Block',{162.589,10.6,-82.81},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.851,1.851,8.0},false},
  {'COL_VegTrunk_063','Block',{-97.822,10.6,-78.223},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.433,2.433,8.0},false},
  {'COL_VegTrunk_064','Block',{126.344,10.6,-69.112},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.671,2.671,8.0},false},
  {'COL_VegTrunk_065','Block',{26.822,10.6,-105.514},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.089,2.089,8.0},false},
  {'COL_VegTrunk_066','Block',{118.305,10.6,-73.377},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.05,2.05,8.0},false},
  {'COL_VegTrunk_067','Block',{81.212,10.6,-91.144},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.78,2.78,8.0},false},
  {'COL_VegTrunk_068','Block',{114.815,9.6,-0.812},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.657,2.657,8.0},false},
  {'COL_VegTrunk_069','Block',{105.674,10.6,-71.699},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.157,2.157,8.0},false},
  {'COL_VegTrunk_070','Block',{-204.34,9.6,117.293},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.22,2.22,8.0},false},
  {'COL_VegTrunk_071','Block',{-7.442,10.6,-114.705},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.372,2.372,8.0},false},
  {'COL_VegTrunk_072','Block',{-73.441,9.6,141.798},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.045,2.045,8.0},false},
  {'COL_VegTrunk_073','Block',{100.857,10.6,-99.265},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.188,2.188,8.0},false},
  {'COL_VegTrunk_074','Block',{104.902,10.6,-92.432},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.431,2.431,8.0},false},
  {'COL_VegTrunk_075','Block',{72.861,10.6,-78.254},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.164,2.164,8.0},false},
  {'COL_VegTrunk_076','Block',{123.007,9.6,25.021},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.002,2.002,8.0},false},
  {'COL_VegTrunk_077','Block',{-78.484,10.6,-73.345},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.045,2.045,8.0},false},
  {'COL_VegTrunk_078','Block',{116.08,9.6,71.561},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.486,2.486,8.0},false},
  {'COL_VegTrunk_079','Block',{150.715,9.6,12.004},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.018,2.018,8.0},false},
  {'COL_VegTrunk_080','Block',{-204.84,9.6,81.334},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.275,2.275,8.0},false},
  {'COL_VegTrunk_081','Block',{117.567,10.6,-90.444},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.78,2.78,8.0},false},
  {'COL_VegTrunk_082','Block',{-217.047,9.6,80.477},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.119,2.119,8.0},false},
  {'COL_VegTrunk_083','Block',{-108.421,10.6,-87.281},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.968,1.968,8.0},false},
  {'COL_VegTrunk_084','Block',{-8.484,9.6,142.286},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.916,1.916,8.0},false},
  {'COL_VegTrunk_085','Block',{126.469,9.6,83.902},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.311,2.311,8.0},false},
  {'COL_VegTrunk_086','Block',{107.564,10.6,-80.943},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.581,2.581,8.0},false},
  {'COL_VegTrunk_087','Block',{129.343,9.6,63.992},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.294,2.294,8.0},false},
  {'COL_VegTrunk_088','Block',{158.941,10.6,-65.058},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.67,2.67,8.0},false},
  {'COL_VegTrunk_089','Block',{-71.128,10.6,-81.055},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.381,2.381,8.0},false},
  {'COL_VegTrunk_090','Block',{127.726,9.6,7.649},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.252,2.252,8.0},false},
  {'COL_VegTrunk_091','Block',{-74.939,10.6,-66.064},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.721,2.721,8.0},false},
  {'COL_VegTrunk_092','Block',{119.875,9.6,56.711},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.478,2.478,8.0},false},
  {'COL_VegTrunk_093','Block',{78.594,10.6,-82.017},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.193,2.193,8.0},false},
  {'COL_VegTrunk_094','Block',{136.584,9.6,77.567},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.498,2.498,8.0},false},
  {'COL_VegTrunk_095','Block',{62.054,10.6,-78.14},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.452,2.452,8.0},false},
  {'COL_VegTrunk_096','Block',{-78.499,10.6,-78.767},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.363,2.363,8.0},false},
  {'COL_VegTrunk_097','Block',{146.736,9.6,19.947},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.661,2.661,8.0},false},
  {'COL_VegTrunk_098','Block',{133.83,9.6,-2.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.45,2.45,8.0},false},
  {'COL_VegTrunk_099','Block',{99.639,10.6,-77.923},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.89,1.89,8.0},false},
  {'COL_VegTrunk_100','Block',{131.541,10.6,-87.539},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.358,2.358,8.0},false},
  {'COL_VegTrunk_101','Block',{153.393,10.6,-84.058},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.286,2.286,8.0},false},
  {'COL_VegTrunk_102','Block',{7.877,10.6,-109.77},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.218,2.218,8.0},false},
  {'COL_VegTrunk_103','Block',{-2.119,10.6,-105.062},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.311,2.311,8.0},false},
  {'COL_VegTrunk_104','Block',{-90.901,10.6,-56.652},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.54,2.54,8.0},false},
  {'COL_VegTrunk_105','Block',{-72.54,9.6,123.035},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.352,2.352,8.0},false},
  {'COL_VegTrunk_106','Block',{159.347,9.6,16.914},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.836,1.836,8.0},false},
  {'COL_VegTrunk_107','Block',{-72.227,9.6,132.616},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.835,1.835,8.0},false},
  {'COL_VegTrunk_108','Block',{-75.093,10.6,-52.765},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.858,1.858,8.0},false},
  {'COL_VegTrunk_109','Block',{105.848,9.6,11.526},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.538,2.538,8.0},false},
  {'COL_VegTrunk_110','Block',{-87.199,10.6,-70.441},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.849,1.849,8.0},false},
  {'COL_VegTrunk_111','Block',{90.326,10.6,-74.064},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.526,2.526,8.0},false},
  {'COL_VegTrunk_112','Block',{-95.445,10.6,-64.088},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.435,2.435,8.0},false},
  {'COL_VegTrunk_113','Block',{64.294,10.6,-98.359},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.409,2.409,8.0},false},
  {'COL_VegTrunk_114','Block',{-64.564,10.6,-53.286},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.932,1.932,8.0},false},
  {'COL_VegTrunk_115','Block',{153.759,10.6,-50.83},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.311,2.311,8.0},false},
  {'COL_VegTrunk_116','Block',{115.265,9.6,17.73},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.428,2.428,8.0},false},
  {'COL_VegTrunk_117','Block',{90.122,10.6,-83.215},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.316,2.316,8.0},false},
  {'COL_VegTrunk_118','Block',{131.486,9.6,14.76},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.863,1.863,8.0},false},
  {'COL_VegTrunk_119','Block',{-83.693,10.6,-91.229},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.193,2.193,8.0},false},
  {'COL_VegTrunk_120','Block',{145.398,10.6,-70.222},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.079,2.079,8.0},false},
  {'COL_VegTrunk_121','Block',{114.363,9.6,82.903},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.429,2.429,8.0},false},
  {'COL_VegTrunk_122','Block',{-87.205,9.6,136.208},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.723,2.723,8.0},false},
  {'COL_VegTrunk_123','Block',{126.463,9.6,74.635},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.039,2.039,8.0},false},
  {'COL_VegTrunk_124','Block',{-84.458,10.6,-63.344},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.08,2.08,8.0},false},
  {'COL_VegTrunk_125','Block',{151.451,10.6,-71.453},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.959,1.959,8.0},false},
  {'COL_VegTrunk_126','Block',{53.386,10.6,-101.035},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.435,2.435,8.0},false},
  {'COL_VegTrunk_127','Block',{140.511,10.6,-84.175},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.995,1.995,8.0},false},
  {'COL_VegTrunk_128','Block',{118.978,9.6,88.651},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.196,2.196,8.0},false},
  {'COL_VegTrunk_129','Block',{117.487,9.6,28.369},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.363,2.363,8.0},false},
  {'COL_VegTrunk_130','Block',{132.119,9.6,35.71},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.591,2.591,8.0},false},
  {'COL_VegTrunk_131','Block',{124.495,9.6,47.813},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.365,2.365,8.0},false},
  {'COL_VegTrunk_132','Block',{154.214,9.6,18.977},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.83,1.83,8.0},false},
  {'COL_VegTrunk_133','Block',{-97.549,9.6,133.343},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.647,2.647,8.0},false},
  {'COL_VegTrunk_134','Block',{-108.554,10.6,-74.447},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.62,2.62,8.0},false},
  {'COL_VegTrunk_135','Block',{118.737,9.6,36.745},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.013,2.013,8.0},false},
  {'COL_VegTrunk_136','Block',{-200.752,9.6,128.562},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.78,2.78,8.0},false},
  {'COL_VegTrunk_137','Block',{125.178,9.6,37.241},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.95,1.95,8.0},false},
  {'COL_VegTrunk_138','Block',{89.884,9.6,2.759},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.296,2.296,8.0},false},
  {'COL_VegTrunk_139','Block',{-52.632,10.6,-24.502},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.098,2.098,8.0},false},
  {'COL_VegTrunk_140','Block',{-52.21,10.6,-52.898},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.617,2.617,8.0},false},
  {'COL_VegTrunk_141','Block',{142.453,10.6,-62.237},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.132,2.132,8.0},false},
  {'COL_VegTrunk_142','Block',{-82.976,10.6,-54.934},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.047,2.047,8.0},false},
  {'COL_VegTrunk_143','Block',{-115.266,10.6,-84.178},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.285,2.285,8.0},false},
  {'COL_VegTrunk_144','Block',{84.572,9.6,3.583},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.011,2.011,8.0},false},
  {'COL_VegTrunk_145','Block',{-116.376,10.6,-97.893},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.296,2.296,8.0},false},
  {'COL_VegTrunk_146','Block',{-110.436,9.6,147.015},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.403,2.403,8.0},false},
  {'COL_VegTrunk_147','Block',{110.816,10.6,-62.509},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.704,2.704,8.0},false},
  {'COL_VegTrunk_148','Block',{-102.527,10.6,-101.974},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.345,2.345,8.0},false},
  {'COL_VegTrunk_149','Block',{63.64,10.6,-69.943},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.159,2.159,8.0},false},
  {'COL_VegTrunk_150','Block',{-75.423,10.6,-36.183},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.989,1.989,8.0},false},
  {'COL_VegTrunk_151','Block',{-91.569,10.6,-102.103},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.226,2.226,8.0},false},
  {'COL_VegTrunk_152','Block',{-74.41,9.6,109.365},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.795,2.795,8.0},false},
  {'COL_VegTrunk_153','Block',{152.357,9.6,25.438},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.971,1.971,8.0},false},
  {'COL_VegTrunk_154','Block',{106.582,9.6,74.17},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.739,2.739,8.0},false},
  {'COL_VegTrunk_155','Block',{123.976,10.6,-21.404},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.744,2.744,8.0},false},
  {'COL_VegTrunk_156','Block',{144.789,9.6,87.293},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.129,2.129,8.0},false},
  {'COL_VegTrunk_157','Block',{-92.698,10.6,-34.658},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.049,2.049,8.0},false},
  {'COL_VegTrunk_158','Block',{-195.421,9.6,119.27},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.058,2.058,8.0},false},
  {'COL_VegTrunk_159','Block',{-126.536,10.6,-79.416},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.029,2.029,8.0},false},
  {'COL_VegTrunk_160','Block',{101.666,10.6,-62.335},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.308,2.308,8.0},false},
  {'COL_VegTrunk_161','Block',{-64.062,9.6,135.19},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.731,2.731,8.0},false},
  {'COL_VegTrunk_162','Block',{-44.654,10.6,-25.883},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.958,1.958,8.0},false},
  {'COL_VegTrunk_163','Block',{-107.67,10.6,-61.895},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.124,2.124,8.0},false},
  {'COL_VegTrunk_164','Block',{-44.892,10.6,-43.385},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.904,1.904,8.0},false},
  {'COL_VegTrunk_165','Block',{81.419,9.6,14.545},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.312,2.312,8.0},false},
  {'COL_VegTrunk_166','Block',{-98.728,10.6,-29.14},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.31,2.31,8.0},false},
  {'COL_VegTrunk_167','Block',{-74.455,10.6,-26.392},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.001,2.001,8.0},false},
  {'COL_VegTrunk_168','Block',{109.714,9.6,45.768},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.499,2.499,8.0},false},
  {'COL_VegTrunk_169','Block',{-62.147,9.6,120.003},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.285,2.285,8.0},false},
  {'COL_VegTrunk_170','Block',{111.372,9.6,101.735},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.116,2.116,8.0},false},
  {'COL_VegTrunk_171','Block',{-57.351,10.6,-71.431},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.853,1.853,8.0},false},
  {'COL_VegTrunk_172','Block',{-68.737,9.6,101.174},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.267,2.267,8.0},false},
  {'COL_VegTrunk_173','Block',{-21.478,10.6,-105.159},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.382,2.382,8.0},false},
  {'COL_VegTrunk_174','Block',{-141.792,9.6,151.597},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.929,1.929,8.0},false},
  {'COL_VegTrunk_175','Block',{-57.286,9.6,129.26},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.264,2.264,8.0},false},
  {'COL_VegTrunk_176','Block',{89.894,9.6,142.15},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.116,2.116,8.0},false},
  {'COL_VegTrunk_177','Block',{79.422,10.6,-21.242},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.539,2.539,8.0},false},
  {'COL_VegTrunk_178','Block',{-190.248,9.6,18.079},{1.0,0.0,0.0},{0.0,0.0,-1.0},{1.876,1.876,8.0},false},
  {'COL_VegTrunk_179','Block',{87.012,9.6,91.65},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.488,2.488,8.0},false},
  {'COL_VegTrunk_180','Block',{-111.214,10.6,-55.019},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.289,2.289,8.0},false},
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
  {'ForgeChimney',{0.0,94.7,-86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['nota']='AudioWorld: ambiente da chamine (camara de fogo da forja nova)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
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
  {'VFX_Anvil_Sparks',{-0.4,10.9,-55.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparks',['nota']='faiscas a cada martelada do Ignis (topo da bigorna do golem, sessao Ignis)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'VFX_Chimney_Smoke_Emitter',{0.0,96.2,-86.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='smoke',['rate']=6,['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0,['radius']=3.6,['nota']='fresta sob a capa elevada (boca do fumeiro); brasas na camara de fogo logo abaixo'}},
  {'VFX_Forge_Sparks',{24.5,8.75,-57.4},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='sparks',['nota']='faiscas do martelo-pilao a cada golpe (evento \'martinete\' do VFX_TripHammer)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'VFX_Hearth_Fire',{-0.9,9.2,-73.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='fire',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0,['nota']='leito de brasas da boca da fornalha (largura x profundidade x altura das chamas)'}},
  {'VFX_Quench_Steam',{10.1,9.2,-57.6},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='steam',['nota']='vapor do cocho de tempera (barra mergulhada)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
  {'VFX_TripHammer',{24.5,10.0,-57.4},{-0.0,0.0,-1.0},{-1.0,0.0,0.0},{['anim']='martinete sobe/desce 1x por came (3 cames por volta da roda)',['face_x']=1.0,['face_z']=0.0,['yaw_deg']=-90.0,['source']='VM_Frg_TripHammer',['cams']=3,['cam_len']=1.6,['cam_x']=24.5,['rest']=0.0,['lift']=0.16,['anvil_top']=8.65}},
  {'VFX_Waterwheel_Rotate',{36.0,9.4,-66.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['axis']='X',['rpm']=6,['raio']=7.5,['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0,['R']=7.5,['half_w']=1.6,['source']='VM_Frg_Wheel',['note']='girar VM_Frg_Wheel (roda + eixo + cames) em torno de +X Blender no pivot: o fundo da roda anda com a agua da levada (para o norte, -Z Roblox)'}},
  {'VFX_Wheel_Splash',{36.0,2.7,-62.836},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['particle']='splash',['nota']='pas entrando na agua da levada (lado sul, a montante)',['face_x']=0.0,['face_z']=1.0,['yaw_deg']=180.0}},
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
  {'L_Hearth_Fire_VM','POINT',{-0.9,11.8,-69.8},{255,122,41},24.0,2.2,true,false},
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
  {'L_VM_Lamp_Arch','POINT',{-89.079,17.2,65.487},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_C1','POINT',{-145.934,15.56,105.729},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_C2','POINT',{-160.744,15.56,91.674},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_C3','POINT',{-166.2,15.56,72.0},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_C4','POINT',{-160.744,15.56,52.326},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_C5','POINT',{-145.934,15.56,38.271},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_Frg1','POINT',{-16.0,13.9,-48.3},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_Frg2','POINT',{14.0,13.9,-48.3},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_I1','POINT',{57.85,14.12,160.0},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_I2','POINT',{42.15,14.12,160.0},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_I3','POINT',{7.246,14.12,217.256},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_I4','POINT',{-2.561,14.12,204.996},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_L1','POINT',{60.0,13.7,36.2},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_L2','POINT',{60.0,13.7,49.8},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_N1','POINT',{-9.9,14.7,-35.2},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_N2','POINT',{9.9,14.7,-35.2},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_P1','POINT',{-10.1,9.65,1.2},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_P1_1','POINT',{31.883,15.56,35.805},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_P2','POINT',{10.1,9.65,1.2},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_P2_1','POINT',{34.815,15.56,52.435},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_P3','POINT',{29.915,15.56,67.975},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_P4','POINT',{-32.795,15.56,61.937},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_R1','POINT',{-51.584,15.5,26.842},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_R2','POINT',{-101.105,15.5,48.373},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_S1','POINT',{32.703,13.7,96.639},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_S3','POINT',{58.857,13.7,127.684},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_SpawnE','POINT',{13.8,14.7,79.1},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_SpawnW','POINT',{-13.8,14.7,79.1},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_T1','POINT',{-10.6,15.61,17.8},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_T2','POINT',{10.6,15.61,17.8},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_T3','POINT',{-27.0,15.61,31.0},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_T4','POINT',{27.0,15.61,31.0},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_W1','POINT',{-44.052,13.7,62.784},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Lamp_W3','POINT',{-82.697,13.7,71.71},{255,223,173},14.0,0.8,false,true},
  {'L_VM_Night_Chimney','POINT',{0.0,90.1,-86.0},{255,128,48},18.0,1.2,false,true},
  {'L_VM_Night_Win_01','POINT',{8.895,23.734,-28.1},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_02','POINT',{-8.995,17.9,-29.825},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_03','POINT',{56.5,13.253,36.97},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_04','POINT',{-10.995,29.203,13.05},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_05','POINT',{10.295,22.9,-3.917},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_06','POINT',{11.095,22.494,9.9},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_07','POINT',{-10.995,22.131,-1.2},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_08','POINT',{56.5,13.253,26.23},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_09','POINT',{56.5,12.973,59.77},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_10','POINT',{-17.32,10.0,14.555},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_11','POINT',{16.163,16.9,16.505},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_12','POINT',{22.03,13.533,1.4},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_13','POINT',{8.2,13.253,116.13},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_14','POINT',{-28.95,22.435,19.905},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_15','POINT',{13.587,17.9,-20.595},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_16','POINT',{-33.555,16.9,11.925},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_17','POINT',{-11.3,13.673,126.87},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_18','POINT',{5.2,13.253,126.87},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_19','POINT',{15.4,12.833,126.87},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_20','POINT',{-15.411,11.0,-20.645},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_21','POINT',{-17.972,10.0,-6.055},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_22','POINT',{37.605,22.252,12.5},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_23','POINT',{16.312,17.9,-33.605},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_24','POINT',{31.938,16.9,19.005},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_25','POINT',{-24.45,16.9,6.895},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_26','POINT',{33.5,13.533,-4.97},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_27','POINT',{-35.03,13.393,1.4},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_28','POINT',{-22.0,12.973,126.87},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_29','POINT',{30.087,10.0,8.045},{255,178,98},7.0,0.9,false,true},
  {'L_VM_Night_Win_30','POINT',{-46.5,13.393,7.77},{255,178,98},7.0,0.9,false,true},
  {'L_VM_ShopIn_A','POINT',{70.0,13.6,43.0},{255,234,203},6.5,0.36,false,false},
  {'L_VM_ShopIn_B','POINT',{82.0,13.6,43.0},{255,234,203},6.5,0.36,false,false},
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
  Lg.Brightness = 2.3
  Lg.ExposureCompensation = -0.05
  Lg.EnvironmentDiffuseScale = 0.5
  Lg.EnvironmentSpecularScale = 0.3
  Lg.ShadowSoftness = 0.35
  Lg.Ambient = Color3.fromRGB(104,100,98)
  Lg.OutdoorAmbient = Color3.fromRGB(150,158,178)
  Lg.ColorShift_Top = Color3.fromRGB(255,238,214)
  Lg.ColorShift_Bottom = Color3.fromRGB(0,0,0)
  Lg.ClockTime = 13.929
  Lg.GeographicLatitude = 53.448
  do local e = Lg:FindFirstChildOfClass('Atmosphere') or Instance.new('Atmosphere', Lg)
    e.Density = 0.26
    e.Offset = 0.12
    e.Color = Color3.fromRGB(196,218,244)
    e.Decay = Color3.fromRGB(116,150,198)
    e.Glare = 0.1
    e.Haze = 0.9
  end
  do local e = Lg:FindFirstChildOfClass('Sky') or Instance.new('Sky', Lg)
    e.SunAngularSize = 14
    e.MoonAngularSize = 11
    e.StarCount = 0
  end
  do local e = Lg:FindFirstChildOfClass('BloomEffect') or Instance.new('BloomEffect', Lg)
    e.Intensity = 0.22
    e.Size = 24
    e.Threshold = 1.6
  end
  do local e = Lg:FindFirstChildOfClass('SunRaysEffect') or Instance.new('SunRaysEffect', Lg)
    e.Intensity = 0.03
    e.Spread = 0.12
  end
  do local e = Lg:FindFirstChildOfClass('ColorCorrectionEffect') or Instance.new('ColorCorrectionEffect', Lg)
    e.Brightness = 0.0
    e.Contrast = 0.06
    e.Saturation = 0.08
    e.TintColor = Color3.fromRGB(255,250,242)
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
