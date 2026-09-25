-- Ilha 1 "Vila da Folha" (Naruto). Modelada no Blender (pasta ilha_naruto/), montada no Studio por
-- montar_ilha_naruto.lua e guardada em ServerStorage.IlhaNaruto. Aqui a ilha e clonada para a Area 1 e ligada aos
-- sistemas que JA existem (nada de sistema novo):
--  * minerios: pontos ORE_* (so a POSICAO; variante/raridade continuam vindo do SpawnMinerio) + zona
--    MiningZone_Naruto (piso do fosso) com bloqueios em marco central, escadas e rampas. AreaBuilder/SpawnMinerio intactos.
--  * invocacao: a maquina Gacha_<tema> vira o "motor" invisivel da torre (prompt no portal, pad na praca);
--    GachaService/ExpeditionClient/UITravel continuam lendo a mesma maquina.
--  * portao DB: peca NextAreaId=2 no patio (o Core.Main liga o prompt: bloqueado -> compra pela UI de sempre,
--    Progresso.comprarArea; liberado -> viajar). Estado da barreira por jogador no cliente (perfil.areas[2]).
--  * VFX baratos: emissores marcados 'IlhaVFX' (o LocalScript ILHA_NARUTO_Cliente liga/desliga por distancia).
local SS = game:GetService('ServerStorage')
local CS = game:GetService('CollectionService')
local RS = game:GetService('ReplicatedStorage')
local M = {}
local V = Vector3.new
local C = Color3.fromRGB

-- MiningZone_Naruto: piso do fosso (Blender GP_Zone_Pit: centro (0,3.2,420), raio 56)
M.ZONA = { nome = 'MiningZone_Naruto', centro = V(0, 3.2, 420), tamanho = V(104, 0, 104) }
M.BLOQUEIOS = {
	{ pos = V(0, 3.2, 420), raio = 15 },    -- marco de pedra central (cairn)
	{ pos = V(0, 3.2, 366), raio = 12 },    -- escada sul (chegada da entrada)
	{ pos = V(0, 3.2, 474), raio = 12 },    -- escada norte
	{ pos = V(-52, 3.2, 413), raio = 16 },  -- rampa de carga oeste
	{ pos = V(52, 3.2, 413), raio = 16 },   -- rampa de carga leste
}
-- borda do fosso: o SpawnMinerio so aceita bloqueios circulares, entao um anel de circulos (centro r=60, raio 9,
-- a cada 8 studs) fecha tudo de r>=52 para fora: minerio nenhum encosta na parede/cerca do fosso
do
	local n = math.ceil(2 * math.pi * 60 / 8)
	for i = 0, n - 1 do
		local a = i / n * 2 * math.pi
		table.insert(M.BLOQUEIOS, { pos = M.ZONA.centro + V(math.cos(a) * 60, 0, math.sin(a) * 60), raio = 9 })
	end
end
M.RAIO_UTIL = 50  -- raio dos pontos candidatos em grade hexagonal (folga para o tamanho do minerio)
M.PASSO_HEX = 7.5 -- o SpawnMinerio exige 7 entre pontos; a folga de verdade (distanciaMin 9) e escolhida por ele
local HRP = 3.5 -- altura do HumanoidRootPart acima do piso (IslandTravel poe o root exatamente na posicao)

local function bloqueado(p)
	for _, b in ipairs(M.BLOQUEIOS) do
		if (V(b.pos.X, 0, b.pos.Z) - V(p.X, 0, p.Z)).Magnitude < b.raio then return true end
	end
	return false
end

local function peca(nome, tam, cf, pai)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1
	p.Parent = pai
	return p
end

-- emissor barato; 'dist' = alcance de culling no cliente
local TEX = {
	fumaca = 'rbxasset://textures/particles/smoke_main.dds',
	brilho = 'rbxasset://textures/particles/sparkles_main.dds',
}
local function emissor(pai, nome, pos, s)
	local a = peca('VFX_' .. nome, V(1, 1, 1), CFrame.new(pos), pai)
	local e = Instance.new('ParticleEmitter')
	e.Name = nome
	e.Texture = TEX[s.tex or 'fumaca']
	e.Color = ColorSequence.new(s.cor)
	e.Rate = s.rate
	e.Lifetime = NumberRange.new(s.vida * 0.7, s.vida)
	e.Speed = NumberRange.new(s.vel * 0.4, s.vel)
	e.SpreadAngle = s.spread or Vector2.new(40, 40)
	e.Acceleration = s.acc or V(0, 0, 0)
	e.LightEmission = s.luz or 0.2
	e.LightInfluence = s.infl or 1
	e.Rotation = NumberRange.new(0, 360)
	e.RotSpeed = NumberRange.new(-12, 12)
	e.EmissionDirection = s.dir or Enum.NormalId.Top
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, s.tam * 0.5), NumberSequenceKeypoint.new(0.5, s.tam),
		NumberSequenceKeypoint.new(1, s.tam * (s.fim or 0.6)) })
	local t0 = s.transp or 0.55
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, t0),
		NumberSequenceKeypoint.new(0.75, math.min(1, t0 + 0.25)), NumberSequenceKeypoint.new(1, 1) })
	if s.forma then e.Shape = s.forma; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume end
	a.Size = s.area or V(1, 1, 1)
	e:SetAttribute('Dist', s.dist or 260)
	e:SetAttribute('Rate0', s.rate)
	CS:AddTag(e, 'IlhaVFX')
	e.Parent = a
	return e
end

local function vfx(model)
	local pasta = Instance.new('Folder'); pasta.Name = 'VFX_Integracao'; pasta.Parent = model
	local agua = C(214, 238, 250)
	-- INVOCACAO: estrela/aneis ja giram (IlhaMovel); aqui so o brilho discreto
	emissor(pasta, 'Sum_Estrela', V(135.457, 62.2, 457.721), { tex = 'brilho', cor = C(255, 226, 150), rate = 3, vida = 2.6,
		vel = 0.6, tam = 0.55, fim = 0.2, spread = Vector2.new(180, 180), luz = 0.7, infl = 0.2, transp = 0.35,
		area = V(8, 8, 8), forma = Enum.ParticleEmitterShape.Sphere, dist = 320 })
	emissor(pasta, 'Sum_Portal', V(133.2, 21.2, 456.2), { tex = 'brilho', cor = C(150, 205, 255), rate = 3, vida = 3,
		vel = 0.8, tam = 0.35, fim = 0.2, acc = V(0, 1.4, 0), luz = 0.6, infl = 0.3, transp = 0.4,
		area = V(6, 1, 6), forma = Enum.ParticleEmitterShape.Box, dist = 160 })
	-- AGUA: nevoa na base da cachoeira dos fundos, borrifo na roda d'agua, nevoa nas bordas das quedas no mar
	for _, x in ipairs({ -62, 0, 55 }) do
		emissor(pasta, 'Agua_NevoaFundos', V(x, 24, 598), { cor = agua, rate = 1.6, vida = 4, vel = 1.2, tam = 9, fim = 1.2,
			acc = V(0, 0.6, 0), transp = 0.78, area = V(40, 2, 6), forma = Enum.ParticleEmitterShape.Box, dist = 300 })
	end
	emissor(pasta, 'Agua_EspumaFundos', V(0, 22.6, 596), { cor = C(245, 252, 255), rate = 4, vida = 1.4, vel = 3, tam = 1.4,
		acc = V(0, -6, 0), transp = 0.5, spread = Vector2.new(60, 60), area = V(150, 1, 4),
		forma = Enum.ParticleEmitterShape.Box, dist = 200 })
	emissor(pasta, 'Agua_RodaBorrifo', V(-118, 6.5, 432), { cor = agua, rate = 6, vida = 0.9, vel = 7, tam = 0.45,
		fim = 0.3, acc = V(0, -22, 0), transp = 0.35, spread = Vector2.new(55, 55), area = V(4, 1, 8),
		forma = Enum.ParticleEmitterShape.Box, dist = 140 })
	emissor(pasta, 'Agua_CanalOeste', V(140, 19.5, 544), { cor = agua, rate = 3, vida = 1, vel = 4, tam = 0.5,
		acc = V(0, -14, 0), transp = 0.4, area = V(3, 1, 3), forma = Enum.ParticleEmitterShape.Box, dist = 140 })
	local quedas = { V(-127, 20, 577), V(-112, 3, 337), V(98, -5, 339), V(170, 15, 497) }
	for i, q in ipairs(quedas) do
		emissor(pasta, 'Agua_BordaQueda' .. i, q, { cor = agua, rate = 1.2, vida = 3, vel = 1.5, tam = 6, fim = 1.3,
			acc = V(0, -1.5, 0), transp = 0.8, area = V(18, 2, 18), forma = Enum.ParticleEmitterShape.Box, dist = 320 })
		emissor(pasta, 'Agua_BaseQueda' .. i, V(q.X, -108, q.Z), { cor = agua, rate = 1, vida = 6, vel = 2, tam = 22,
			fim = 1.3, acc = V(0, 1, 0), transp = 0.82, area = V(26, 2, 26), forma = Enum.ParticleEmitterShape.Box, dist = 700 })
	end
	-- PORTAO DB: faiscas discretas (o cliente acalma quando o jogador ja liberou)
	emissor(pasta, 'Portao_DB', V(-172.4, 25, 592.4), { tex = 'brilho', cor = C(255, 170, 70), rate = 3, vida = 2,
		vel = 0.7, tam = 0.4, fim = 0.2, acc = V(0, 1, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(10, 16, 10),
		forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	-- pulso dos cristais da torre (o cliente anima a cor)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('MeshPart') and (d.Name == 'SUM_Tower_Glow__Crystal_SumPortal_Glow' or d.Name == 'SUM_Tower_Glow__Summon_Blue_Glow'
			or d.Name == 'SUM_Constellation__Summon_Blue_Glow' or d.Name == 'SUM_Constellation__Crystal_SumStar_Glow') then
			d:SetAttribute('Cor0', d.Color)
			CS:AddTag(d, 'IlhaPulso')
		end
	end
end

-- a maquina de gacha vira o motor invisivel da torre de invocacao
local function invocacao(area, mk)
	local machine = workspace:FindFirstChild('Gachas') and workspace.Gachas:FindFirstChild('Gacha_' .. area.tema)
	local pad = machine and machine:FindFirstChild('PadGacha')
	local cab
	for _, d in ipairs(machine and machine:GetDescendants() or {}) do
		if d:IsA('BasePart') and string.find(d.Name:lower(), 'cabinet_body') then cab = d break end
	end
	local inter, jog = mk.SUMMON_Interact, mk.SUMMON_PlayerPosition
	if not (pad and cab and inter and jog) then warn('[NarutoIsland] maquina de gacha/marcadores de invocacao faltando') return nil end
	-- frente da torre (de onde o jogador chega): do portal para o jogador
	local frente = (jog.Position - inter.Position) * V(1, 0, 1)
	frente = frente.Magnitude > 0.1 and frente.Unit or V(-0.8192, 0, -0.5736)
	local atual = (pad.Position - cab.Position) * V(1, 0, 1)
	local ang = math.atan2(frente.X, frente.Z) - math.atan2(atual.Unit.X, atual.Unit.Z)
	local rot = CFrame.Angles(0, ang, 0)
	if (rot:VectorToWorldSpace(atual.Unit) - frente).Magnitude > 0.05 then rot = CFrame.Angles(0, -ang, 0) end
	-- corpo (onde fica o prompt) no portal, na altura do peito
	local alvo = V(inter.Position.X, inter.Position.Y + 2.5, inter.Position.Z)
	local T = CFrame.new(alvo) * rot * CFrame.new(-cab.Position)
	machine:PivotTo(T * machine:GetPivot())
	-- pad (proximidade do GachaService/cliente e destino do UITravel 'gacha') afundado sob o piso da praca
	local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { machine }; params.RespectCanCollide = true
	local chao = workspace:Raycast(pad.Position + V(0, 20, 0), V(0, -40, 0), params)
	local piso = chao and chao.Position.Y or 16.5
	pad.Size = V(10, 0.25, 10)
	pad.CFrame = CFrame.new(pad.Position.X, piso - 0.9, pad.Position.Z) * (pad.CFrame - pad.CFrame.Position)
	pad.CanCollide = false; pad.CanTouch = false; pad.CanQuery = false; pad.CastShadow = false
	-- o modelo (maquina de chiclete) some: a torre aprovada e o visual da invocacao
	for _, d in ipairs(machine:GetDescendants()) do
		if d:IsA('BasePart') and d ~= pad then
			d.Transparency = 1; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.CastShadow = false
		elseif d:IsA('Light') or d:IsA('ParticleEmitter') or d:IsA('Beam') or d:IsA('Trail') then
			d.Enabled = false
		elseif d:IsA('BillboardGui') then
			d.MaxDistance = 45
		end
	end
	local placa = machine:FindFirstChild('PlacaGacha')
	if placa then placa.CFrame = CFrame.new(inter.Position + V(0, 13, 0)) end
	machine:SetAttribute('MotorDaTorre', 'Ilha Naruto: maquina invisivel, visual = torre de invocacao')
	return V(pad.Position.X, piso + HRP, pad.Position.Z)
end

-- portao DB: interacao (NextAreaId) + ancora de UI de compra + ponto de viagem na ponta da ilhota
local function portaoDB(model, area, mk, Config)
	local prox = Config.areaPorId(area.id + 1)
	local gi, ui, anc = mk.GATE_DB_INTERACT, mk.PURCHASE_UI_ANCHOR_DB, mk.ISLAND_NEXT_ANCHOR
	if not (prox and gi and ui and anc) then return end
	local pasta = Instance.new('Folder'); pasta.Name = 'PORTAO_DB_Integracao'; pasta.Parent = model
	local inter = peca('PortaoDB_Interacao', V(6, 6, 6), CFrame.new(gi.Position + V(0, 3, 0)), pasta)
	inter:SetAttribute('NextAreaId', prox.id)
	inter:SetAttribute('Portao', 'DB')
	-- placa de compra (o cliente esconde para quem ja liberou)
	local a = peca('PortaoDB_UI', V(1, 1, 1), CFrame.new(ui.Position), pasta)
	local bb = Instance.new('BillboardGui'); bb.Name = 'CompraPortao'; bb.Size = UDim2.fromOffset(230, 84)
	bb.MaxDistance = 90; bb.LightInfluence = 0; bb.Parent = a
	local function txt(n, y, h, s, cor, font)
		local t = Instance.new('TextLabel'); t.Name = n; t.BackgroundTransparency = 1; t.Size = UDim2.new(1, 0, 0, h)
		t.Position = UDim2.fromOffset(0, y); t.Text = s; t.TextScaled = true; t.Font = font or Enum.Font.GothamBlack
		t.TextColor3 = cor; t.TextStrokeTransparency = 0.35; t.Parent = bb
	end
	txt('Nome', 0, 30, string.upper(prox.nome), C(255, 196, 92))
	txt('Custo', 32, 28, 'Custo: ' .. Config.formatar(prox.custo) .. ' moedas', C(255, 255, 255), Enum.Font.GothamBold)
	txt('Dica', 62, 20, 'Interaja no portao para desbloquear', C(225, 225, 235), Enum.Font.GothamMedium)
	-- ponto de viagem na ponta (ISLAND_NEXT_ANCHOR): a ponte da Ilha 2 encosta aqui no futuro
	local fwd = anc:GetAttribute('fwd') or V(-0.7071, 0, 0.7071)
	local pv = anc.Position - fwd * 5
	local disco = Instance.new('Part'); disco.Name = 'ViagemProximaArea'; disco.Shape = Enum.PartType.Cylinder
	disco.Size = V(0.2, 9, 9); disco.CFrame = CFrame.new(pv.X, 16.3, pv.Z) * CFrame.Angles(0, 0, math.rad(90))
	disco.Anchored = true; disco.CanCollide = false; disco.CanQuery = false; disco.CanTouch = false; disco.CastShadow = false
	disco.Material = Enum.Material.Neon; disco.Color = C(255, 170, 70); disco.Transparency = 0.72
	disco:SetAttribute('NextAreaId', prox.id)
	disco.Parent = pasta
	return pasta
end

function M.build(parent, area)
	local Config = require(RS.Config)
	local source = SS:FindFirstChild('IlhaNaruto')
	assert(source, '[NarutoIsland] ServerStorage.IlhaNaruto nao encontrado')
	parent.ModelStreamingMode = Enum.ModelStreamingMode.PersistentPerPlayer
	local model = source:Clone()
	model.Name = 'ILHA_NARUTO' -- IlhaMovel/PortoesCompra procuram por este nome
	model.Parent = parent

	local mk = {}
	for _, m in ipairs(model.GAMEPLAY_MARKERS:GetChildren()) do mk[m.Name] = m end
	local function pos(n, dy) local m = mk[n] return m and (m.Position + V(0, dy or 0, 0)) end

	-- atributos que o resto do jogo le (IslandTravel, UITravel, AreaBuilder)
	local entrada = pos('WORLD_ENTRY_Naruto') or V(0, 6.4, 320)
	parent:SetAttribute('WorldRevision', 7)
	parent:SetAttribute('BoundsHalfSize', V(212, 120, 232)) -- cobre a ilhota do portao DB (x -201) e a torre (x 160)
	parent:SetAttribute('EntryPosition', V(entrada.X, 6.2 + HRP, entrada.Z))
	parent:SetAttribute('SafePosition', V(entrada.X, 6.2 + HRP, entrada.Z + 8))
	parent:SetAttribute('RotaPropria', true) -- TravessiaCorredores/Paredes: a ilha tem entrada, saida e portao proprios
	-- ISLAND_NEXT_ANCHOR (documentado para a Ilha 2)
	local anc = mk.ISLAND_NEXT_ANCHOR
	if anc then
		parent:SetAttribute('NextAnchorPosition', anc.Position)
		parent:SetAttribute('NextAnchorForward', V(-0.7071, 0, 0.7071))
		parent:SetAttribute('NextAnchorWidth', 18)
		parent:SetAttribute('NextAnchorClearHeight', 22)
	end

	-- colisoes invisiveis da ilha nao podem ser 'abertas' pelo TravessiaCorredores
	for _, p in ipairs(model.COLLISION:GetDescendants()) do
		if p:IsA('BasePart') then p:SetAttribute('TravessiaKeep', true) end
	end
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and string.match(d.Name, '^COL_') then d:SetAttribute('TravessiaKeep', true) end
	end

	local gacha = invocacao(area, mk)
	if gacha then parent:SetAttribute('GachaPosition', gacha) end
	portaoDB(model, area, mk, Config)
	vfx(model)

	-- minerios: so posicoes. Marcador que nao passa na mesma folga que o SpawnMinerio exige dos pontos da grade
	-- (caixa 7x8x7 livre acima do piso) ou que cai num bloqueio fica de fora: nada em escada, rampa, cerca ou no marco.
	local ov = OverlapParams.new(); ov.FilterType = Enum.RaycastFilterType.Exclude; ov.RespectCanCollide = true
	local spawns, fora = {}, 0
	for n, m in pairs(mk) do
		if string.match(n, '^ORE_') then
			local p = m.Position
			if not bloqueado(p) and #workspace:GetPartBoundsInBox(CFrame.new(p + V(0, 5, 0)), V(7, 8, 7), ov) == 0 then
				table.insert(spawns, { pos = p })
			else
				fora += 1
			end
		end
	end
	table.sort(spawns, function(a, b) return a.pos.Z < b.pos.Z or (a.pos.Z == b.pos.Z and a.pos.X < b.pos.X) end)
	parent:SetAttribute('OrePontosMarcadores', #spawns)
	parent:SetAttribute('OreMarcadoresFora', fora)
	-- pool de pontos: o AreaBuilder enche min(SPAWN.minerios, pontos-2) e a amplificacao de comum cria mais 1;
	-- com o pool justo o SpawnMinerio acabaria empilhando dois minerios no mesmo ponto. Grade hexagonal no piso
	-- do fosso (mesmas regras: piso plano na altura do fosso, caixa 7x8x7 livre, fora dos bloqueios). Os marcadores
	-- vem primeiro, entao o desenho original do Blender tem prioridade.
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.RespectCanCollide = true
	local c0, hx = M.ZONA.centro, 0
	local lin = math.ceil(M.RAIO_UTIL / (M.PASSO_HEX * 0.866))
	for row = -lin, lin do
		for col = -lin - 1, lin + 1 do
			local x = col * M.PASSO_HEX + ((row % 2 == 0) and 0 or M.PASSO_HEX / 2)
			local z = row * M.PASSO_HEX * 0.866
			local p = c0 + V(x, 0, z)
			if math.sqrt(x * x + z * z) <= M.RAIO_UTIL and not bloqueado(p) then
				local hit = workspace:Raycast(p + V(0, 12, 0), V(0, -30, 0), rp)
				if hit and hit.Normal.Y > 0.85 and math.abs(hit.Position.Y - c0.Y) < 0.5
					and #workspace:GetPartBoundsInBox(CFrame.new(hit.Position + V(0, 5, 0)), V(7, 8, 7), ov) == 0 then
					table.insert(spawns, { pos = hit.Position }); hx += 1
				end
			end
		end
	end
	parent:SetAttribute('OrePontosGrade', hx)
	-- zona logica visivel no Explorer (para QA/designer); CanQuery=false para o raycast de spawn nao bater nela
	local z = peca(M.ZONA.nome, V(M.ZONA.tamanho.X, 1, M.ZONA.tamanho.Z), CFrame.new(M.ZONA.centro), model)
	z:SetAttribute('Raio', 56); z:SetAttribute('PisoY', M.ZONA.centro.Y)

	local boss = V(-30, 3.2, 428)
	local volta = V(-13, 6.35, 324)
	return { spawns = spawns, boss = boss, returnPad = volta,
		zonas = { lista = { { nome = M.ZONA.nome, centro = M.ZONA.centro, tamanho = M.ZONA.tamanho } }, bloqueios = M.BLOQUEIOS } }
end

return M
