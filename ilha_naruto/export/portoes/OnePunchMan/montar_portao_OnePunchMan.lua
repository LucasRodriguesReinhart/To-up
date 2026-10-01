-- montar_portao_OnePunchMan.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID 051caef9
-- 1) Importe os FBX PORTAO_OnePunchMan_*_051cae.fbx (3D Importer) para dentro de workspace.PORTAO_OnePunchMan. Deixe o importador
--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns
--    minutos) antes de 'corrigir' cor: o branco some sozinho.
-- 2) Rode este script na Command Bar. Ele:
--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;
--      normaliza nomes trocados pelo importador ('.001', ' (1)');
--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);
--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade
--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);
--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os
--      personagens: o Script PORTAO_OnePunchMan_Servidor poe os personagens no grupo 'Personagens');
--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),
--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.
-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.
-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.
local EXPORT_ID = '051caef9'
local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o portao INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)
local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)
local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra
local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido
local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)
local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)
local root = workspace:FindFirstChild('PORTAO_OnePunchMan') or Instance.new('Model', workspace)
root.Name = 'PORTAO_OnePunchMan'
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
  ['Energy_Core_OnePunchMan_Glow'] = {c = Color3.fromRGB(255,226,140), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Metal_Brass'] = {c = Color3.fromRGB(186,148,90), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Dark'] = {c = Color3.fromRGB(78,76,76), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_GateOPM_Red'] = {c = Color3.fromRGB(208,36,30), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['Metal_Gold'] = {c = Color3.fromRGB(222,170,70), m = Enum.Material.Metal, t = 0.0, s = true, x = nil, w = nil},
  ['P_Gold_Glow'] = {c = Color3.fromRGB(255,195,30), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['P_OPM_DarkGlass'] = {c = Color3.fromRGB(22,34,62), m = Enum.Material.Glass, t = 0.0, s = true, x = nil, w = nil},
  ['P_Red_Glow'] = {c = Color3.fromRGB(185,12,22), m = Enum.Material.Neon, t = 0.0, s = false, x = nil, w = nil},
  ['Stone_Dark'] = {c = Color3.fromRGB(102,95,88), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Dark'] = {c = Color3.fromRGB(128,120,110), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
  ['Stone_Wall_Light'] = {c = Color3.fromRGB(178,170,156), m = Enum.Material.SmoothPlastic, t = 0.0, s = true, x = 'stone', w = nil},
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
local FBX = {[1]='PORTAO_OnePunchMan_08_PURCHASE_GATES_051cae.fbx', [2]='PORTAO_OnePunchMan_12_VFX_HELPERS_051cae.fbx'}
-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}
--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)
--   modelo: Model Atomic (streaming sem pecas pela metade)
local MESH = {
  ['GATE_OnePunchMan_Barrier__Energy_Core_OnePunchMan_Glow']={0.0,9.042,0.0,12.962,13.312,1.4,1,false,'Energy_Core_OnePunchMan_Glow','','PORTAO'},
  ['GATE_OnePunchMan_Barrier__P_Gold_Glow']={0.0,9.0,0.0,16.0,18.0,0.5,1,false,'P_Gold_Glow','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Metal_Brass']={0.0,5.3,4.51,32.8,9.7,3.62,1,true,'Metal_Brass','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Metal_Dark']={0.28,15.0,1.38,34.04,30.0,17.44,1,true,'Metal_Dark','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Metal_GateOPM_Red']={0.125,11.95,3.475,34.15,23.9,13.05,1,true,'Metal_GateOPM_Red','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Metal_Gold']={0.0,14.042,0.845,33.0,23.584,15.889,1,true,'Metal_Gold','','PORTAO'},
  ['GATE_OnePunchMan_Frame__P_Gold_Glow']={0.0,11.75,0.925,33.4,19.5,16.45,1,false,'P_Gold_Glow','','PORTAO'},
  ['GATE_OnePunchMan_Frame__P_OPM_DarkGlass']={0.0,13.75,-2.32,33.2,23.5,9.76,1,true,'P_OPM_DarkGlass','','PORTAO'},
  ['GATE_OnePunchMan_Frame__P_Red_Glow']={1.421,21.935,-0.849,23.458,17.33,2.378,1,false,'P_Red_Glow','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Stone_Dark']={0.0,2.825,3.4,34.2,5.65,12.2,1,true,'Stone_Dark','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Stone_Wall_Dark']={0.0,0.0,2.6,36.0,1.2,15.2,1,true,'Stone_Wall_Dark','','PORTAO'},
  ['GATE_OnePunchMan_Frame__Stone_Wall_Light']={-0.0,12.85,1.45,35.4,26.9,16.9,1,true,'Stone_Wall_Light','','PORTAO'},
  ['GATE_OnePunchMan_Lock__Energy_Core_OnePunchMan_Glow']={0.0,8.28,0.0,3.9,3.4,1.2,1,false,'Energy_Core_OnePunchMan_Glow','','PORTAO'},
  ['GATE_OnePunchMan_Lock__Metal_Dark']={0.0,8.08,0.0,0.5,1.0,2.6,1,false,'Metal_Dark','','PORTAO'},
  ['GATE_OnePunchMan_Lock__Metal_Gold']={0.0,9.243,0.0,3.2,4.625,2.3,1,false,'Metal_Gold','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_1__Metal_Gold']={-13.0,15.6,4.3,3.1,3.1,0.36,2,false,'Metal_Gold','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_1__P_Red_Glow']={-13.0,15.6,4.3,1.8,1.8,0.58,2,false,'P_Red_Glow','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_2__Metal_Gold']={-12.4,10.8,8.5,3.1,3.1,0.36,2,false,'Metal_Gold','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_2__P_Red_Glow']={-12.4,10.8,8.5,1.8,1.8,0.58,2,false,'P_Red_Glow','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_3__Metal_Gold']={12.4,11.1,8.5,3.1,3.1,0.36,2,false,'Metal_Gold','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_3__P_Red_Glow']={12.4,11.1,8.5,1.8,1.8,0.58,2,false,'P_Red_Glow','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_4__Metal_Gold']={13.0,15.9,4.3,3.1,3.1,0.36,2,false,'Metal_Gold','','PORTAO'},
  ['VFX_GATE_OnePunchMan_Star_4__P_Red_Glow']={13.0,15.9,4.3,1.8,1.8,0.58,2,false,'P_Red_Glow','','PORTAO'},
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
  {'COL_GateOnePunchManLock_001','GateLock',{0.0,9.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{16.6,1.4,18.0},false},
  {'COL_GateOnePunchMan_001','Block',{-10.15,13.35,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.3,6.1,26.7},false},
  {'COL_GateOnePunchMan_002','Block',{-14.4,7.4,-0.375},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.2,4.35,14.8},false},
  {'COL_GateOnePunchMan_003','Block',{-10.75,7.0,-4.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.3,4.6,15.2},false},
  {'COL_GateOnePunchMan_004','Block',{10.15,13.35,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.3,6.1,26.7},false},
  {'COL_GateOnePunchMan_005','Block',{14.4,5.6,-0.375},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.2,4.35,11.2},false},
  {'COL_GateOnePunchMan_006','Block',{10.75,7.0,-4.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.3,4.6,15.2},false},
  {'COL_GateOnePunchMan_007','Block',{0.0,-0.225,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{22.0,10.0,0.75},false},
  {'COL_GateOnePunchMan_008','Block',{-14.5,0.0,3.65},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.0,13.1,1.2},false},
  {'COL_GateOnePunchMan_009','Block',{-15.1,0.85,4.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.2,5.2,0.5},false},
  {'COL_GateOnePunchMan_010','Block',{-15.1,5.4,4.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,4.0,9.6},false},
  {'COL_GateOnePunchMan_011','Block',{-12.4,3.85,8.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,6.5},false},
  {'COL_GateOnePunchMan_012','Block',{14.5,0.0,3.65},{1.0,0.0,0.0},{0.0,0.0,-1.0},{7.0,13.1,1.2},false},
  {'COL_GateOnePunchMan_013','Block',{15.1,0.85,4.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{5.2,5.2,0.5},false},
  {'COL_GateOnePunchMan_014','Block',{15.1,5.4,4.7},{1.0,0.0,0.0},{0.0,0.0,-1.0},{4.0,4.0,9.6},false},
  {'COL_GateOnePunchMan_015','Block',{12.4,3.85,8.5},{1.0,0.0,0.0},{0.0,0.0,-1.0},{2.0,2.0,6.5},false},
}
COLF:ClearAllChildren()
for _, c in ipairs(COL) do
  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true
  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic
  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])
  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF
end
local MK = {
  {'GATE_OnePunchMan',{0.0,0.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['open_w']=16.0,['open_h']=18.0,['deck_w']=18.0,['area_id']=6,['key']='OnePunchMan'}},
  {'GATE_OnePunchMan_EXIT',{0.0,0.2,-12.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['gate']='OnePunchMan'}},
  {'GATE_OnePunchMan_INTERACT',{0.0,0.2,7.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['gate']='OnePunchMan',['radius']=10.0}},
  {'GATE_OnePunchMan_LOCKED',{0.0,9.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['gate']='OnePunchMan',['state_default']='locked'}},
  {'GATE_OnePunchMan_OpenFX',{0.0,9.0,0.0},{1.0,0.0,0.0},{0.0,0.0,-1.0},{['gate']='OnePunchMan',['state']='unlocked',['fx']='abertura'}},
  {'PURCHASE_UI_ANCHOR_OnePunchMan',{0.0,14.0,2.5},{-1.0,0.0,0.0},{0.0,0.0,1.0},{['gate']='OnePunchMan',['faces']='approach',['ui']='BillboardGui preco/requisito'}},
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
  Lg.GeographicLatitude = 61.894
  Lg.ClockTime = 14.166
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
  print(string.format('Lighting do lobby aplicado: sol (%.2f, %.2f, %.2f), esperado (-0.42, 0.66, 0.62) = sol do Blender', d.X, d.Y, d.Z))
  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')
end
root.WorldPivot = CFrame.new(ROOT_OFFSET)
-- ===== pecas moveis (VFX_*) =====
local VFX = {
  ['VFX_GATE_OnePunchMan_Star_1'] = {p = Vector3.new(-13.000,15.600,4.300), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -4.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePunchMan_Star_2'] = {p = Vector3.new(-12.400,10.800,8.500), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 5.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePunchMan_Star_3'] = {p = Vector3.new(12.400,11.100,8.500), a = Vector3.new(0.0000,1.0000,0.0000), rpm = -6.000, bob = 0.600, rate = 0.000},
  ['VFX_GATE_OnePunchMan_Star_4'] = {p = Vector3.new(13.000,15.900,4.300), a = Vector3.new(0.0000,1.0000,0.0000), rpm = 7.000, bob = 0.600, rate = 0.000},
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
print(string.format('PORTAO_OnePunchMan montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))
