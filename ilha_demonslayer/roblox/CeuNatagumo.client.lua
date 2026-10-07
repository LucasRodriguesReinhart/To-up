-- CeuNatagumo (LocalScript, StarterPlayerScripts) - noite da Ilha 4 (Demon Slayer, Monte Natagumo), so neste cliente.
-- O AreaAtmosphere e o dono do Lighting (ClockTime/Brightness/Ambient/Atmosphere/ColorCorrection, perfil [4] 'Natagumo')
-- e NAO toca em Sky nem Bloom. Este script cuida dos efeitos locais, ligado so com o jogador na area 4 (a mesma deteccao
-- do CeuSombras: o atributo que o AreaAtmosphere publica - CurrentIslandMood = 'Natagumo'; NatagumoMood do patch so
-- como reserva):
--   * Sky: skybox padrao do Roblox (preto a noite) no lugar do ceu anime de dia (as nuvens diurnas viram manchas no ceu
--     noturno), lua fria um pouco maior e estrelas; Bloom proprio fraco (PLANO secao 10: 0,3 / limiar 1,4).
--   * MAR DE NUVENS em -60 (PLANO 3.3): placa escura + veu claro + bancos de nuvem (particulas grandes e lentas) em volta
--     da ilha. A quilha da SG (ate -108) "sai das nuvens" vista daqui. Fica acima do mar da SG (-111,5), que so existe
--     com o jogador na area 3.
--   * fundos das outras ilhas: esconde o chao distante do lobby e escurece o mar da Ilha 1 (como o CeuSombras).
--   * luzes NightOnly da ilha (lanternas de caminho e toro, L_DSProp_*): a area 4 e noite fixa e nada as ligava (o
--     export grava desligadas para um ciclo dia/noite que a area nao tem).
--   * AguaCorrente: rola as Textures da agua feita no Roblox (DemonSlayerIsland.agua) pelo atributo Velocidade.
--   * interiores: SoundService.AmbientReverb muda de leve dentro das casas entraveis (V1, V6) e do salao da fornalha
--     (a musica nao reinicia: mesma area).
--   * som do lugar: os marcadores AUDIO_* (familia + alcance) viram fontes do SomJogo.RegisterEmitter (API existente,
--     a mesma do AudioWorld); saem ao deixar a area.
--   * PadGacha da maquina invisivel: escondido neste cliente (na Ilha 3 o neon do pad vazava por fresta do piso).
--   * A roda d'agua, o eixo e os piloes NAO sao animados aqui: ja tem a tag IlhaMovel do montar e o LocalScript
--     ILHA_NARUTO_Movel gira/bate (nao duplicar).
-- Tudo restaurado ao sair. Local: nao afeta outros jogadores.
local Players = game:GetService('Players')
local Lighting = game:GetService('Lighting')
local TweenService = game:GetService('TweenService')
local RunService = game:GetService('RunService')
local CS = game:GetService('CollectionService')
local SoundService = game:GetService('SoundService')
local RS = game:GetService('ReplicatedStorage')
local player = Players.LocalPlayer

local V, C = Vector3.new, Color3.fromRGB
local MOOD = 'Natagumo'                 -- profiles[4].name no AreaAtmosphere
local ILHA = 'ILHA_DEMONSLAYER'         -- Model clonado pelo Core.DemonSlayerIsland
local MOON_SIZE = 18                    -- MoonAngularSize na area (padrao 11; a SG usa 32): lua fria, sem roubar a forja
local STARS = 2600
local BLOOM = { Intensity = 0.3, Size = 24, Threshold = 1.4 }
local SKYBOX_NOITE = 'rbxasset://textures/sky/sky512_'   -- + bk/dn/ft/lf/rt/up .tex (ceu padrao, preto a noite)
local FACES = { 'Bk', 'Dn', 'Ft', 'Lf', 'Rt', 'Up' }
local MAR_Y = -60                       -- topo do mar de nuvens
local MAR_COR = C(46, 54, 78)           -- placa de baixo (sombra das nuvens)
local VEU_COR = C(120, 132, 164)        -- veu de cima (topo das nuvens ao luar)
local NUVEM_COR = C(150, 162, 192)
local MAR_NOITE = C(24, 28, 66)         -- mar da Ilha 1 visto daqui (o mesmo tom do CeuSombras)
local LIGAR_NOTURNAS = true
local ESCONDER_PAD = true

local ligado = false

-- ------------------------------------------------------------------ onde esta a ilha
local function ilhaDS()
	local areas = workspace:FindFirstChild('Areas')
	if not areas then return nil, nil end
	for _, a in ipairs(areas:GetChildren()) do
		local ilha = a:FindFirstChild(ILHA)
		if ilha then return a, ilha end
	end
	return nil, nil
end

local function marcadores()
	local _, ilha = ilhaDS()
	return ilha and ilha:FindFirstChild('GAMEPLAY_MARKERS')
end

-- ------------------------------------------------------------------ partes salvas (LocalTransparencyModifier)
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

-- ------------------------------------------------------------------ mar de nuvens (so neste cliente)
local mar = nil                         -- Folder com as pecas
local function bancoNuvem(pai, nome, pos, tam)
	local a = Instance.new('Part')
	a.Name = nome; a.Anchored = true; a.CanCollide = false; a.CanQuery = false; a.CanTouch = false; a.CastShadow = false
	a.Transparency = 1; a.Size = tam; a.CFrame = CFrame.new(pos); a.Parent = pai
	local e = Instance.new('ParticleEmitter')
	e.Name = 'Nuvem'; e.Texture = 'rbxasset://textures/particles/smoke_main.dds'
	e.Rate = 1.1; e.Lifetime = NumberRange.new(18, 26); e.Speed = NumberRange.new(0.3, 0.9)
	e.SpreadAngle = Vector2.new(80, 10); e.Acceleration = V(0.4, 0.05, 0.2)
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 38), NumberSequenceKeypoint.new(0.5, 62),
		NumberSequenceKeypoint.new(1, 80) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0.55),
		NumberSequenceKeypoint.new(0.75, 0.62), NumberSequenceKeypoint.new(1, 1) })
	e.Color = ColorSequence.new(NUVEM_COR); e.LightInfluence = 1; e.LightEmission = 0
	e.Rotation = NumberRange.new(0, 360); e.RotSpeed = NumberRange.new(-3, 3)
	e.Shape = Enum.ParticleEmitterShape.Box; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
	e.Parent = a
	return a
end

local function atualizarMar()
	local area = ilhaDS()
	local centro = area and area:GetAttribute('BoundsCenter')
	local metade = area and area:GetAttribute('BoundsHalfSize')
	if typeof(centro) ~= 'Vector3' or typeof(metade) ~= 'Vector3' then return end
	local largo = V((metade.X + 1500) * 2, 1, (metade.Z + 1500) * 2)
	if not mar then
		mar = Instance.new('Folder')
		mar.Name = 'MarNuvensNatagumoLocal'
		local function placa(nome, y, cor, transp, mat)
			local p = Instance.new('Part')
			p.Name = nome; p.Anchored = true
			p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
			p.Material = mat; p.Color = cor; p.Transparency = transp
			p.Size = largo; p.Position = V(centro.X, y, centro.Z)
			p.Parent = mar
			return p
		end
		placa('Fundo', MAR_Y - 6, MAR_COR, 0, Enum.Material.SmoothPlastic)
		placa('Veu', MAR_Y - 0.5, VEU_COR, 0.45, Enum.Material.SmoothPlastic)
		-- bancos de nuvem em anel em volta da ilha (fora da caixa: debaixo da ilha so a placa)
		local rx, rz = metade.X + 140, metade.Z + 140
		for i = 0, 7 do
			local a = i / 8 * math.pi * 2
			local pos = V(centro.X + math.cos(a) * rx, MAR_Y + 4, centro.Z + math.sin(a) * rz)
			bancoNuvem(mar, 'Banco_' .. i, pos, V(260, 6, 260))
		end
		bancoNuvem(mar, 'Banco_Centro', V(centro.X, MAR_Y + 3, centro.Z), V(metade.X * 1.6, 6, metade.Z * 1.6))
		mar.Parent = workspace
	end
	for _, p in ipairs(mar:GetChildren()) do
		if p.Name == 'Fundo' or p.Name == 'Veu' then
			p.Size = largo
			p.Position = V(centro.X, p.Position.Y, centro.Z)
		end
	end
end

-- ------------------------------------------------------------------ fundos das OUTRAS ilhas (como o CeuSombras)
local fundos = {}                       -- [part] = { cor, ltm }
local function fundosAlvo()
	local t = {}
	local lobby = workspace:FindFirstChild('LOBBY_FORJA')
	local fg = lobby and lobby:FindFirstChild('SKYLINE') and lobby.SKYLINE:FindFirstChild('FAR_GROUND')
	if fg then t[fg] = 'esconder' end
	local areas = workspace:FindFirstChild('Areas')
	local a1 = areas and areas:FindFirstChild('Area1')
	local nar = a1 and a1:FindFirstChild('ILHA_NARUTO')
	local m1 = nar and nar:FindFirstChild('SKYLINE') and nar.SKYLINE:FindFirstChild('FAR_GROUND')
	if m1 then t[m1] = 'noite' end
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

-- ------------------------------------------------------------------ luzes NightOnly da ilha
local luzesSalvas = setmetatable({}, { __mode = 'k' })     -- [Light] = Enabled de antes
local function aplicarNoturnas()
	if not LIGAR_NOTURNAS then return end
	local _, ilha = ilhaDS()
	local pasta = ilha and ilha:FindFirstChild('LIGHTS')
	if not pasta then return end
	for _, a in ipairs(pasta:GetChildren()) do
		if a:GetAttribute('NightOnly') then
			for _, l in ipairs(a:GetChildren()) do
				if l:IsA('Light') then
					if luzesSalvas[l] == nil then luzesSalvas[l] = l.Enabled end
					if not l.Enabled then l.Enabled = true end
				end
			end
		end
	end
end
local function restaurarNoturnas()
	for l, antes in pairs(luzesSalvas) do
		if l.Parent then l.Enabled = antes end
		luzesSalvas[l] = nil
	end
end

-- ------------------------------------------------------------------ pad da maquina de gacha (vazamento de neon)
local padSalvo = {}
local function aplicarPad()
	if not ESCONDER_PAD then return end
	local area = ilhaDS()
	local Config = RS:FindFirstChild('Config')
	local tema = 'nichirin'
	if area and Config then
		local ok, cfg = pcall(require, Config)
		local a = ok and cfg.areaPorId and cfg.areaPorId(area:GetAttribute('AreaId') or 4)
		if a and a.tema then tema = a.tema end
	end
	local g = workspace:FindFirstChild('Gachas')
	local m = g and g:FindFirstChild('Gacha_' .. tema)
	local pad = m and m:FindFirstChild('PadGacha')
	if pad and pad:IsA('BasePart') then esconderParte(pad, padSalvo) end
end

-- ------------------------------------------------------------------ som do lugar (AUDIO_*)
local Som = nil
do
	local mod = RS:FindFirstChild('SomJogo')
	if mod then
		local ok, s = pcall(require, mod)
		if ok and type(s) == 'table' and type(s.RegisterEmitter) == 'function' then Som = s end
	end
end
local sons = {}                          -- [chave] = true
local function aplicarSons()
	if not Som then return end
	local mk = marcadores()
	if not mk then return end
	for _, m in ipairs(mk:GetChildren()) do
		if m:IsA('BasePart') and string.match(m.Name, '^AUDIO_') then
			local chave = 'DS:' .. m.Name
			if not sons[chave] then
				local fam = m:GetAttribute('family')
				local vol = (m:GetAttribute('volume') == 'baixo') and 0.08 or 0.15
				Som.RegisterEmitter(chave, fam, m.Position, m:GetAttribute('range') or 42, vol)
				sons[chave] = true
			end
		end
	end
end
local function restaurarSons()
	if not Som then return end
	for chave in pairs(sons) do
		pcall(Som.RemoveEmitter, chave)
		sons[chave] = nil
	end
end

-- ------------------------------------------------------------------ interiores: reverb leve (musica continua)
local reverbOriginal = SoundService.AmbientReverb
local SALAS = {                          -- prefixo da luz de interior -> raio horizontal, reverb
	{ '^L_DSFrg_Furnace$', 16, Enum.ReverbType.StoneRoom },   -- salao da fornalha (44 x 32)
	{ '^L_DSVil_V6_', 11, Enum.ReverbType.LivingRoom },       -- casa principal (terreo visitavel)
	{ '^L_DSVil_V1_', 7, Enum.ReverbType.Room },              -- chaya (pavilhao aberto)
}
local function interiorAtual()
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	local _, ilha = ilhaDS()
	local pasta = ilha and ilha:FindFirstChild('LIGHTS')
	if not (hrp and pasta) then return nil end
	local p = hrp.Position
	for _, s in ipairs(SALAS) do
		for _, a in ipairs(pasta:GetChildren()) do
			if a:IsA('BasePart') and string.match(a.Name, s[1]) then
				local d = V(p.X - a.Position.X, 0, p.Z - a.Position.Z).Magnitude
				if d <= s[2] and math.abs(p.Y - a.Position.Y) < 10 then return s[3] end
			end
		end
	end
	return nil
end

-- ------------------------------------------------------------------ ceu (Sky) + bloom
local bloom = Instance.new('BloomEffect')
bloom.Name = 'CeuNatagumoBloom'
bloom.Enabled = false
bloom.Intensity = 0
bloom.Size = BLOOM.Size
bloom.Threshold = BLOOM.Threshold
bloom.Parent = Lighting

local salvoCeu = nil                     -- { sky, moon, stars, faces } do estado fora da area
local function aplicarCeu()
	local sky = Lighting:FindFirstChildOfClass('Sky')
	if sky and not salvoCeu then
		salvoCeu = { sky = sky, moon = sky.MoonAngularSize, stars = sky.StarCount, faces = {} }
		sky.MoonAngularSize = MOON_SIZE
		sky.StarCount = STARS
		for _, f in ipairs(FACES) do
			salvoCeu.faces[f] = sky['Skybox' .. f]
			sky['Skybox' .. f] = SKYBOX_NOITE .. string.lower(f) .. '.tex'
		end
	end
end
local function restaurarCeu()
	if salvoCeu then
		if salvoCeu.sky.Parent then
			salvoCeu.sky.MoonAngularSize = salvoCeu.moon
			salvoCeu.sky.StarCount = salvoCeu.stars
			for f, id in pairs(salvoCeu.faces) do salvoCeu.sky['Skybox' .. f] = id end
		end
		salvoCeu = nil
	end
end

-- ------------------------------------------------------------------ lacos (so trabalham com o jogador na area)
task.spawn(function()          -- as pecas entram/saem com o streaming: reaplica enquanto estiver na area
	while true do
		task.wait(2)
		if ligado then
			pcall(aplicarFundos)
			pcall(atualizarMar)
			pcall(aplicarNoturnas)
			pcall(aplicarPad)
			pcall(aplicarSons)
		end
	end
end)

task.spawn(function()
	while true do
		task.wait(0.5)
		if ligado then
			local ok, r = pcall(interiorAtual)
			local alvo = (ok and r) or reverbOriginal
			if SoundService.AmbientReverb ~= alvo then SoundService.AmbientReverb = alvo end
		end
	end
end)

-- AGUA do Roblox: as Textures com tag AguaCorrente rolam para baixo pelo atributo Velocidade (studs/s). So anima
-- enquanto o jogador esta na area; fora dela nada roda (na area 3 quem rola e o CeuSombras).
RunService.Heartbeat:Connect(function(dt)
	if not ligado then return end
	for _, t in ipairs(CS:GetTagged('AguaCorrente')) do
		local v = t:GetAttribute('Velocidade') or 12
		t.OffsetStudsV = (t.OffsetStudsV + v * dt) % math.max(t.StudsPerTileV, 1)
	end
end)

-- ------------------------------------------------------------------ liga / desliga
-- CurrentIslandMood e o PRIMEIRO atributo que o AreaAtmosphere publica na troca de area (antes do ShadowGardenMood):
-- e ele que manda, para o Sky voltar ao normal antes do CeuSombras salvar o dele (DS -> SG). NatagumoMood (patch) so
-- vale se o CurrentIslandMood nao existir.
local function noNatagumo()
	local mood = player:GetAttribute('CurrentIslandMood')
	if mood ~= nil then return mood == MOOD end
	return player:GetAttribute('NatagumoMood') == true
end

local function aplicar(on)
	if on == ligado then return end
	ligado = on
	if on then
		-- o Sky e compartilhado com o CeuSombras: na troca SG -> DS espera ele devolver o ceu dele antes de salvar o
		-- estado (o AreaAtmosphere publica CurrentIslandMood ANTES de ShadowGardenMood = false)
		task.defer(function()
			local t0 = os.clock()
			while ligado and player:GetAttribute('ShadowGardenMood') == true and os.clock() - t0 < 5 do task.wait(0.1) end
			if not ligado then return end
			aplicarCeu()
			bloom.Enabled = true
			TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = BLOOM.Intensity }):Play()
			pcall(aplicarFundos)
			pcall(atualizarMar)
			pcall(aplicarNoturnas)
			pcall(aplicarPad)
			pcall(aplicarSons)
		end)
	else
		-- sincrono: na troca DS -> SG o CeuSombras salva o ceu logo depois (ShadowGardenMood vem depois)
		restaurarCeu()
		restaurarFundos()
		restaurarNoturnas()
		restaurarPartes(padSalvo)
		restaurarSons()
		if mar then mar:Destroy(); mar = nil end
		SoundService.AmbientReverb = reverbOriginal
		local t = TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = 0 })
		t.Completed:Once(function() if not ligado then bloom.Enabled = false end end)
		t:Play()
	end
end

local function reavaliar()
	aplicar(noNatagumo())
end
player:GetAttributeChangedSignal('NatagumoMood'):Connect(reavaliar)
player:GetAttributeChangedSignal('CurrentIslandMood'):Connect(reavaliar)
reavaliar()
