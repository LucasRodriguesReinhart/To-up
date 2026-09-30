-- CeuSombras (LocalScript, StarterPlayerScripts) - ceu noturno da Ilha 3 (Shadow Garden).
-- O AreaAtmosphere e o dono do Lighting (ClockTime/Ambient/Atmosphere/ColorCorrection) e NAO toca em Sky nem Bloom
-- (auditoria C). Este script cuida SO desses dois, reagindo ao atributo ShadowGardenMood que o AreaAtmosphere publica:
--   * Sky: lua GRANDE + muitas estrelas enquanto o jogador esta na area sombra (a referencia tem uma lua enorme);
--   * Bloom proprio (fraco) para os neons violeta/lanternas brilharem de noite.
--   * fundos das outras ilhas: esconde o chao distante do lobby e escurece o mar da Ilha 1 (so neste cliente).
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
		if ligadoFundos then aplicarFundos() end
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
		local r = interiorAtual() or reverbOriginal
		if SoundService.AmbientReverb ~= r then SoundService.AmbientReverb = r end
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
	if ligado then aplicarFundos() else restaurarFundos() end
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
