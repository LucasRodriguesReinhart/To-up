-- CeuSombras (LocalScript, StarterPlayerScripts) - ceu noturno da Ilha 3 (Shadow Garden).
-- O AreaAtmosphere e o dono do Lighting (ClockTime/Ambient/Atmosphere/ColorCorrection) e NAO toca em Sky nem Bloom
-- (auditoria C). Este script cuida dos efeitos locais, reagindo ao atributo ShadowGardenMood que o AreaAtmosphere publica:
--   * Sky: lua GRANDE + muitas estrelas enquanto o jogador esta na area sombra (a referencia tem uma lua enorme);
--   * Bloom proprio (fraco) para os neons violeta/lanternas brilharem de noite.
--   * fundos das outras ilhas: esconde o chao distante do lobby e escurece o mar da Ilha 1 (so neste cliente).
--   * mar proprio, reverb da caverna e corte visual do subsolo e dos interiores das casas.
-- Tudo restaurado ao sair. Local: nao afeta outros jogadores.
local Players = game:GetService('Players')
local Lighting = game:GetService('Lighting')
local TweenService = game:GetService('TweenService')
local player = Players.LocalPlayer

local MOON_SIZE = 24          -- MoonAngularSize na area (padrao do Roblox: 11)
local STARS = 3000
local BLOOM = { Intensity = 0.35, Size = 42, Threshold = 1.55 }

local bloom = Instance.new('BloomEffect')
bloom.Name = 'CeuSombrasBloom'
bloom.Enabled = false
bloom.Intensity = 0
bloom.Size = BLOOM.Size
bloom.Threshold = BLOOM.Threshold
bloom.Parent = Lighting

local salvo = nil             -- { sky, moon, stars } do estado fora da area

-- fundos das OUTRAS ilhas vistos da Shadow Garden (so neste cliente, restaurados ao sair):
--  * o chao distante cinza do lobby (y -70, ate z 130) aparecia como um piso claro ao sul da ilha -> escondido;
--  * o mar da Ilha 1 (azul vivo de dia) vira azul-noite.
local MAR_NOITE = Color3.fromRGB(24, 28, 66)
local fundos = {}              -- [part] = { cor, ltm }
local ligadoFundos = false
local marArea3 = nil

-- o mar da Ilha 1 termina antes da ilha nova; esta placa so existe neste cliente
local function atualizarMarArea3()
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	local centro = a3 and a3:GetAttribute('BoundsCenter')
	local metade = a3 and a3:GetAttribute('BoundsHalfSize')
	if typeof(centro) ~= 'Vector3' or typeof(metade) ~= 'Vector3' then return end
	if not marArea3 then
		marArea3 = Instance.new('Part')
		marArea3.Name = 'MarShadowGardenLocal'
		marArea3.Anchored = true
		marArea3.CanCollide = false; marArea3.CanQuery = false; marArea3.CanTouch = false; marArea3.CastShadow = false
		marArea3.Material = Enum.Material.SmoothPlastic
		marArea3.Color = Color3.fromRGB(20, 24, 58)
		marArea3.Size = Vector3.new((metade.X + 1500) * 2, 1, (metade.Z + 1500) * 2)
		marArea3.Position = Vector3.new(centro.X, -111.5, centro.Z)
		marArea3.Parent = workspace
	end
	marArea3.Size = Vector3.new((metade.X + 1500) * 2, 1, (metade.Z + 1500) * 2)
	marArea3.Position = Vector3.new(centro.X, -111.5, centro.Z)
end

local function restaurarPartes(salvos)
	for p, ltm in pairs(salvos) do
		if p.Parent then p.LocalTransparencyModifier = ltm end
		salvos[p] = nil
	end
end

local function esconderParte(p, salvos)
	if salvos[p] == nil then salvos[p] = p.LocalTransparencyModifier end
	p.LocalTransparencyModifier = 1
end

local subsoloAtual, subsoloConexao, subsoloEscondido = nil, nil, false
local subsoloSalvo = {}
local function restaurarSubsolo()
	restaurarPartes(subsoloSalvo)
	if subsoloConexao then subsoloConexao:Disconnect(); subsoloConexao = nil end
	subsoloAtual = nil
	subsoloEscondido = false
end

local function atualizarSubsolo()
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	local ilha = a3 and a3:FindFirstChild('ILHA_SHADOWGARDEN')
	local subsolo = ilha and ilha:FindFirstChild('SUBSOLO')
	if subsolo ~= subsoloAtual then
		restaurarSubsolo()
		subsoloAtual = subsolo
		if subsolo then
			subsoloConexao = subsolo.DescendantAdded:Connect(function(d)
				if subsoloEscondido and d:IsA('BasePart') then esconderParte(d, subsoloSalvo) end
			end)
		end
	end
	if not subsolo then return end -- export antigo
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	local esconder = false
	if hrp and not player:GetAttribute('DungeonRun') then
		local ok, longe = pcall(function()
			local markers = ilha:FindFirstChild('GAMEPLAY_MARKERS')
			local topo = markers and markers:FindFirstChild('THRONE_Stair_Top')
			if not (topo and topo:IsA('BasePart')) then return false end
			local p, t = hrp.Position, topo.Position
			return (Vector3.new(p.X - t.X, 0, p.Z - t.Z)).Magnitude > 40
		end)
		esconder = ok and longe and hrp.Position.Y > 46
	end
	if esconder == subsoloEscondido then
		if esconder then
			for p in pairs(subsoloSalvo) do
				if p.Parent and p.LocalTransparencyModifier ~= 1 then p.LocalTransparencyModifier = 1 end
			end
		end
		return
	end
	subsoloEscondido = esconder
	if esconder then
		for _, d in ipairs(subsolo:GetDescendants()) do
			if d:IsA('BasePart') then esconderParte(d, subsoloSalvo) end
		end
	else
		restaurarPartes(subsoloSalvo)
	end
end

local interiores, interioresArea, interioresConexao = {}, nil, nil
local function registrarInterior(d)
	if not d:IsA('Model') or not string.match(d.Name, '^SG_Vil_Int_') or interiores[d] then return end
	local ok, cf = pcall(function() return d:GetBoundingBox() end)
	if ok then interiores[d] = { centro = cf.Position, salvos = {}, escondido = false } end
end

local function restaurarInteriores()
	if interioresConexao then interioresConexao:Disconnect(); interioresConexao = nil end
	for _, dados in pairs(interiores) do restaurarPartes(dados.salvos) end
	interiores = {}
	interioresArea = nil
end

local function atualizarInteriores()
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	if a3 ~= interioresArea then
		restaurarInteriores()
		interioresArea = a3
		if a3 then
			for _, d in ipairs(a3:GetDescendants()) do registrarInterior(d) end
			interioresConexao = a3.DescendantAdded:Connect(function(d)
				registrarInterior(d)
				if d:IsA('BasePart') then
					local pai = d.Parent
					while pai and pai ~= a3 do
						local dados = interiores[pai]
						if dados and dados.escondido then esconderParte(d, dados.salvos); break end
						pai = pai.Parent
					end
				end
			end)
		end
	end
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	for model, dados in pairs(interiores) do
		if not model.Parent then
			restaurarPartes(dados.salvos)
			interiores[model] = nil
		else
			local esconder = hrp and (hrp.Position - dados.centro).Magnitude > 90 or false
			if esconder ~= dados.escondido then
				dados.escondido = esconder
				if esconder then
					for _, d in ipairs(model:GetDescendants()) do
						if d:IsA('BasePart') then esconderParte(d, dados.salvos) end
					end
				else
					restaurarPartes(dados.salvos)
				end
			elseif esconder then
				for p in pairs(dados.salvos) do
					if p.Parent and p.LocalTransparencyModifier ~= 1 then p.LocalTransparencyModifier = 1 end
				end
			end
		end
	end
end
local function fundosAlvo()
	local t = {}
	local lobby = workspace:FindFirstChild('LOBBY_FORJA')
	local fg = lobby and lobby:FindFirstChild('SKYLINE') and lobby.SKYLINE:FindFirstChild('FAR_GROUND')
	if fg then t[fg] = 'esconder' end
	local areas = workspace:FindFirstChild('Areas')
	local a1 = areas and areas:FindFirstChild('Area1')
	local nar = a1 and a1:FindFirstChild('ILHA_NARUTO')
	local mar = nar and nar:FindFirstChild('SKYLINE') and nar.SKYLINE:FindFirstChild('FAR_GROUND')
	if mar then t[mar] = 'noite' end
	return t
end
local function aplicarFundos()
	for p, modo in pairs(fundosAlvo()) do
		if not fundos[p] then fundos[p] = { cor = p.Color, ltm = p.LocalTransparencyModifier } end
		if modo == 'esconder' then p.LocalTransparencyModifier = 1 else p.Color = MAR_NOITE end
	end
end
local function restaurarFundos()
	for p, s in pairs(fundos) do
		if p.Parent then p.Color = s.cor; p.LocalTransparencyModifier = s.ltm end
	end
	fundos = {}
end
task.spawn(function()          -- as pecas entram/saem com o streaming: reaplica enquanto estiver na area
	while true do
		task.wait(2)
		if ligadoFundos then aplicarFundos(); atualizarMarArea3() end
	end
end)
task.spawn(function()
	while true do
		task.wait(0.5)
		if ligadoFundos then atualizarSubsolo() end
	end
end)
task.spawn(function()
	while true do
		task.wait(1)
		if ligadoFundos then atualizarInteriores() end
	end
end)

-- INTERIORES: a musica (SomJogo) NAO reinicia ao entrar no castelo/alquimia/masmorra (mesma area); so o ambiente
-- acustico muda de leve via SoundService.AmbientReverb. Restaurado ao sair dos interiores e da area.
local SoundService = game:GetService('SoundService')
local reverbOriginal = SoundService.AmbientReverb
local function interiorAtual()
	if not ligadoFundos then return nil end
	if player:GetAttribute('DungeonRun') then return Enum.ReverbType.StoneCorridor end
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	if not (hrp and a3) then return nil end
	local p = hrp.Position
	local ok, naCaverna = pcall(function()
		local ilha = a3:FindFirstChild('ILHA_SHADOWGARDEN')
		local markers = ilha and ilha:FindFirstChild('GAMEPLAY_MARKERS')
		local cave = markers and markers:FindFirstChild('CAVE_Zone')
		if not (cave and cave:IsA('BasePart')) then return false end
		local fx, fz = cave:GetAttribute('fwd_x'), cave:GetAttribute('fwd_z')
		local sx, sy, h = cave:GetAttribute('sx'), cave:GetAttribute('sy'), cave:GetAttribute('h')
		if not (fx and fz and sx and sy and h) then return false end
		local frente = Vector3.new(fx, 0, fz).Unit
		local lado = Vector3.new(-frente.Z, 0, frente.X)
		local delta = p - cave.Position
		return math.abs(delta:Dot(lado)) <= sx / 2 and math.abs(delta:Dot(frente)) <= sy / 2
			and delta.Y >= 0 and delta.Y <= h
	end)
	if ok and naCaverna then return Enum.ReverbType.Cave end
	local zona = a3:FindFirstChild('MiningZone_ShadowGarden', true)
	if zona and zona:IsA('BasePart') then
		local l = zona.CFrame:PointToObjectSpace(p)
		if math.abs(l.X) <= zona.Size.X / 2 + 3 and math.abs(l.Z) <= zona.Size.Z / 2 + 3 and l.Y > -2 and l.Y < 26 then
			return Enum.ReverbType.StoneRoom
		end
	end
	local alq = a3:FindFirstChild('AlquimiaEstacao', true)
	if alq and alq:IsA('BasePart') and (Vector3.new(p.X, 0, p.Z) - Vector3.new(alq.Position.X, 0, alq.Position.Z)).Magnitude < 14
		and math.abs(p.Y - alq.Position.Y) < 10 then
		return Enum.ReverbType.StoneRoom
	end
	return nil
end
task.spawn(function()
	while true do
		task.wait(0.5)
		if ligadoFundos then
			local r = interiorAtual() or reverbOriginal
			if SoundService.AmbientReverb ~= r then SoundService.AmbientReverb = r end
		end
	end
end)

-- AGUA do Roblox (JardimSombrasIsland): as Textures com tag AguaCorrente rolam para baixo pelo atributo Velocidade
-- (studs/s). So anima enquanto o jogador esta na area (ligadoFundos); fora dela nada roda.
local CS = game:GetService('CollectionService')
game:GetService('RunService').Heartbeat:Connect(function(dt)
	if not ligadoFundos then return end
	for _, t in ipairs(CS:GetTagged('AguaCorrente')) do
		local v = t:GetAttribute('Velocidade') or 12
		t.OffsetStudsV = (t.OffsetStudsV + v * dt) % math.max(t.StudsPerTileV, 1)
	end
end)

local function aplicar(ligado)
	ligadoFundos = ligado
	if ligado then
		aplicarFundos()
		atualizarMarArea3()
		atualizarSubsolo()
		atualizarInteriores()
	else
		restaurarFundos()
		restaurarSubsolo()
		restaurarInteriores()
		if marArea3 then marArea3:Destroy(); marArea3 = nil end
		SoundService.AmbientReverb = reverbOriginal
	end
	local sky = Lighting:FindFirstChildOfClass('Sky')
	if ligado then
		if sky and not salvo then
			salvo = { sky = sky, moon = sky.MoonAngularSize, stars = sky.StarCount }
			sky.MoonAngularSize = MOON_SIZE
			sky.StarCount = STARS
		end
		bloom.Enabled = true
		TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = BLOOM.Intensity }):Play()
	else
		if salvo then
			if salvo.sky.Parent then
				salvo.sky.MoonAngularSize = salvo.moon
				salvo.sky.StarCount = salvo.stars
			end
			salvo = nil
		end
		local t = TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = 0 })
		t.Completed:Once(function() if not (player:GetAttribute('ShadowGardenMood') == true) then bloom.Enabled = false end end)
		t:Play()
	end
end

player:GetAttributeChangedSignal('ShadowGardenMood'):Connect(function()
	aplicar(player:GetAttribute('ShadowGardenMood') == true)
end)
aplicar(player:GetAttribute('ShadowGardenMood') == true)
