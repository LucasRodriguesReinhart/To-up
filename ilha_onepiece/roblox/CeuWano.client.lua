-- CeuWano (LocalScript, StarterPlayerScripts) - DIA da Ilha 5 (One Piece / Wano, area 5 "Grand Line"), so neste cliente.
-- O AreaAtmosphere e o dono do Lighting (ClockTime/Brightness/Ambient/Atmosphere/ColorCorrection, perfil [5]
-- 'GrandLine', trechos [OP]) e NAO toca em Sky nem Bloom. Este script cuida dos efeitos locais, ligado so com o jogador
-- na area 5 (a mesma deteccao do CeuNatagumo: CurrentIslandMood = 'GrandLine'; WanoMood do patch so como reserva):
--   * CEU DE DIA: o Sky do jogo (ceu anime de dia) fica como esta: Wano NAO troca skybox, lua nem estrelas. O que este
--     script garante e o contrario: que o ceu NAO fique "preso" de noite. Na troca DS -> Wano o CeuNatagumo devolve o Sky
--     (sincrono, no CurrentIslandMood); na SG -> ... o CeuSombras devolve no ShadowGardenMood. Ao ligar, este script
--     espera os 2 soltarem e, se o Sky AINDA estiver com o skybox noturno / lua grande, volta ao ceu de dia guardado no
--     inicio (rede de seguranca; nao briga com eles: so age com os 2 desligados).
--   * NUVENS brancas: Clouds do Terrain neste cliente (cria se nao houver; se houver, ajusta e devolve ao sair).
--   * Bloom e SunRays proprios, fracos (PLANO_OP secao 10: Bloom 0,35 / 24 / limiar 1,6 - o reboco branco nao estoura;
--     SunRays 0,04 / 0,12).
--   * MAR LOCAL turquesa no nivel 36 (WATER_Sea: quadrado de 2200 em volta de Wano; dados nos atributos MarLocal* que o
--     Core.OnePieceIsland publica na area, com o marcador como reserva): esconde a quilha; vista de Wano, a DS aparece
--     saindo do mar. Placa funda opaca 6 abaixo (esconde a quilha) + superficie turquesa translucida com a textura de
--     agua rolando devagar. Pecas <= 2048 por eixo (limite do Roblox): o quadrado vira ladrilhos. Entra e sai com fade.
--   * fundos das outras ilhas: esconde o chao distante do lobby (como o CeuNatagumo; o mar azul da Ilha 1 fica, e dia).
--   * AguaCorrente: rola as Textures da agua feita no Roblox (OnePieceIsland.agua) e do mar pelo atributo Velocidade.
--   * interiores: SoundService.AmbientReverb muda de leve no salao real do castelo e na casa de cha (musica continua).
--   * som do lugar: os marcadores AUDIO_* (familia + alcance) viram fontes do SomJogo.RegisterEmitter (API existente);
--     saem ao deixar a area.
--   * PadGacha da maquina invisivel (Gacha_mare): escondido neste cliente (vazamento de neon pela fresta, Ilha 3).
--   * A roda d'agua (VFX_OP_Wheel) e os aneis/estrela do summon NAO sao animados aqui: tag IlhaMovel do montar, o
--     LocalScript ILHA_NARUTO_Movel gira (nao duplicar). Luzes NightOnly ficam APAGADAS (area de dia fixo).
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
local MOOD = 'GrandLine'                -- profiles[5].name no AreaAtmosphere
local ILHA = 'ILHA_ONEPIECE'            -- Model clonado pelo Core.OnePieceIsland
local BLOOM = { Intensity = 0.35, Size = 24, Threshold = 1.6 }
local RAIOS = { Intensity = 0.04, Spread = 0.12 }
local NUVENS = { Cover = 0.5, Density = 0.65, Color = C(255, 255, 255) }   -- nil = nao mexe nas nuvens
local SKYBOX_NOITE = 'rbxasset://textures/sky/sky512_'   -- o skybox noturno que CeuNatagumo/CeuSombras aplicam
local FACES = { 'Bk', 'Dn', 'Ft', 'Lf', 'Rt', 'Up' }
local MAR = { nivel = 36, tamanho = 2200, cor = C(48, 176, 196) }   -- reserva (WATER_Sea do op_water)
local MAR_FUNDO_COR = C(22, 92, 112)    -- placa funda (sombra da agua, opaca: esconde a quilha)
local MAR_TRANSP = 0.3                  -- superficie: deixa ver a pedra logo abaixo da linha d'agua
local MAR_ESCALA = 1                    -- ajuste no Play se a borda do quadrado aparecer (1 = os 2200 do plano)
local LADO_MAX = 2000                   -- ladrilho (o Roblox corta Part > 2048 por eixo)
local ESCONDER_FUNDO_LOBBY = true
local ESCONDER_PAD = true

local ligado = false

-- ------------------------------------------------------------------ onde esta a ilha
local function ilhaOP()
	local areas = workspace:FindFirstChild('Areas')
	if not areas then return nil, nil end
	for _, a in ipairs(areas:GetChildren()) do
		local ilha = a:FindFirstChild(ILHA)
		if ilha then return a, ilha end
	end
	return nil, nil
end

local function marcadores()
	local _, ilha = ilhaOP()
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

-- ------------------------------------------------------------------ mar local (so neste cliente)
local mar = nil                         -- Folder com as placas
local marTweens = {}

local function dadosMar()
	local area = ilhaOP()
	local nivel, centro, tam, cor = MAR.nivel, nil, MAR.tamanho, MAR.cor
	if area then
		nivel = area:GetAttribute('MarLocalNivel') or nivel
		centro = area:GetAttribute('MarLocalCentro')
		tam = area:GetAttribute('MarLocalTamanho') or tam
		local c = area:GetAttribute('MarLocalCor')
		if typeof(c) == 'Color3' then cor = c end
		if typeof(centro) ~= 'Vector3' then
			-- reserva: o marcador (se ja chegou pelo streaming) ou o centro da caixa da ilha
			local mk = marcadores()
			local s = mk and mk:FindFirstChild('WATER_Sea')
			if s and s:IsA('BasePart') then
				centro = s.Position
				nivel = s:GetAttribute('level') or nivel
				tam = s:GetAttribute('size') or tam
			else
				centro = area:GetAttribute('BoundsCenter')
			end
		end
	end
	if typeof(centro) ~= 'Vector3' then return nil end
	return nivel, V(centro.X, nivel, centro.Z), tam * MAR_ESCALA, cor
end

local function cancelarMarTweens()
	for _, t in ipairs(marTweens) do t:Cancel() end
	table.clear(marTweens)
end

local function fadeMar(alvo)                -- alvo: 'entra' | 'sai'
	if not mar then return end
	cancelarMarTweens()
	for _, d in ipairs(mar:GetDescendants()) do
		local t0 = d:GetAttribute('T0')
		if t0 ~= nil and (d:IsA('BasePart') or d:IsA('Texture')) then
			local t = TweenService:Create(d, TweenInfo.new(1.6, Enum.EasingStyle.Sine),
				{ Transparency = (alvo == 'entra') and t0 or 1 })
			table.insert(marTweens, t)
			t:Play()
		end
	end
end

local function criarMar()
	if mar then return true end
	local nivel, centro, tam, cor = dadosMar()
	if not nivel then return false end
	mar = Instance.new('Folder')
	mar.Name = 'MarWanoLocal'
	local n = math.max(1, math.ceil(tam / LADO_MAX))
	local lado = tam / n
	local function placa(nome, cr, transp, mat, refl)
		local p = Instance.new('Part')
		p.Name = nome; p.Anchored = true
		p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Material = mat; p.Color = cr; p.Reflectance = refl or 0
		p.Size = V(lado, 1, lado)
		p:SetAttribute('T0', transp)
		p.Transparency = 1                  -- entra com fade
		p.Parent = mar
		return p
	end
	for i = 0, n - 1 do
		for j = 0, n - 1 do
			local cx = centro.X - tam / 2 + lado * (i + 0.5)
			local cz = centro.Z - tam / 2 + lado * (j + 0.5)
			local f = placa(('Fundo_%d_%d'):format(i, j), MAR_FUNDO_COR, 0, Enum.Material.SmoothPlastic)
			f.Position = V(cx, nivel - 6.5, cz)
			local s = placa(('Superficie_%d_%d'):format(i, j), cor, MAR_TRANSP, Enum.Material.SmoothPlastic, 0.04)
			s.Position = V(cx, nivel - 0.55, cz)       -- topo da placa = nivel - 0,05 (o pe das quedas fica em 36)
			local t = Instance.new('Texture')
			t.Name = 'Ondas'; t.Texture = 'rbxassetid://1190623231'; t.Face = Enum.NormalId.Top
			t.StudsPerTileU = 48; t.StudsPerTileV = 48
			t.Color3 = C(214, 244, 250)
			t:SetAttribute('T0', 0.72)
			t.Transparency = 1
			t:SetAttribute('Velocidade', 1.2)
			CS:AddTag(t, 'AguaCorrente')
			t.Parent = s
		end
	end
	mar.Parent = workspace
	return true
end

-- ------------------------------------------------------------------ fundos das OUTRAS ilhas
local fundos = {}                       -- [part] = ltm
local function aplicarFundos()
	if not ESCONDER_FUNDO_LOBBY then return end
	local lobby = workspace:FindFirstChild('LOBBY_FORJA')
	local fg = lobby and lobby:FindFirstChild('SKYLINE') and lobby.SKYLINE:FindFirstChild('FAR_GROUND')
	if fg and fg:IsA('BasePart') then
		if fundos[fg] == nil then fundos[fg] = fg.LocalTransparencyModifier end
		fg.LocalTransparencyModifier = 1
	end
end
local function restaurarFundos()
	for p, ltm in pairs(fundos) do
		if p.Parent then p.LocalTransparencyModifier = ltm end
	end
	fundos = {}
end

-- ------------------------------------------------------------------ pad da maquina de gacha (vazamento de neon)
local padSalvo = {}
local function aplicarPad()
	if not ESCONDER_PAD then return end
	local area = ilhaOP()
	local Config = RS:FindFirstChild('Config')
	local tema = 'mare'
	if area and Config then
		local ok, cfg = pcall(require, Config)
		local a = ok and cfg.areaPorId and cfg.areaPorId(area:GetAttribute('AreaId') or 5)
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
			local chave = 'OP:' .. m.Name
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
		if type(Som.RemoveEmitter) == 'function' then pcall(Som.RemoveEmitter, chave) end
		sons[chave] = nil
	end
end

-- ------------------------------------------------------------------ interiores: reverb leve (musica continua)
local reverbOriginal = SoundService.AmbientReverb
local SALAS = {                          -- prefixo da luz de interior -> raio horizontal, reverb
	{ '^L_OPCas_Hall_', 22, Enum.ReverbType.Auditorium },     -- salao real no terreo da torre (50 x 42, pe-direito 12)
	{ '^L_OPCap_Int_Cha', 8, Enum.ReverbType.LivingRoom },    -- casa de cha (interior)
}
local function interiorAtual()
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	local _, ilha = ilhaOP()
	local pasta = ilha and ilha:FindFirstChild('LIGHTS')
	if not (hrp and pasta) then return nil end
	local p = hrp.Position
	for _, s in ipairs(SALAS) do
		for _, a in ipairs(pasta:GetChildren()) do
			if a:IsA('BasePart') and string.match(a.Name, s[1]) then
				local d = V(p.X - a.Position.X, 0, p.Z - a.Position.Z).Magnitude
				if d <= s[2] and math.abs(p.Y - a.Position.Y) < 12 then return s[3] end
			end
		end
	end
	return nil
end

-- ------------------------------------------------------------------ ceu de dia: guarda + rede de seguranca
local function noturno(sky)
	for _, f in ipairs(FACES) do
		if string.sub(tostring(sky['Skybox' .. f]), 1, #SKYBOX_NOITE) == SKYBOX_NOITE then return true end
	end
	return false
end

local ceuDia = nil                       -- { faces, moon, stars } do ceu de dia, guardado com o ceu ainda de dia
local function guardarCeuDia()
	local sky = Lighting:FindFirstChildOfClass('Sky')
	if not sky or noturno(sky) then return end
	if player:GetAttribute('ShadowGardenMood') == true or player:GetAttribute('NatagumoMood') == true then return end
	local mood = player:GetAttribute('CurrentIslandMood')
	if mood == 'Natagumo' or mood == 'ShadowGarden' then return end
	ceuDia = { moon = sky.MoonAngularSize, stars = sky.StarCount, faces = {} }
	for _, f in ipairs(FACES) do ceuDia.faces[f] = sky['Skybox' .. f] end
end

local function garantirCeuDia()
	local sky = Lighting:FindFirstChildOfClass('Sky')
	if not (sky and ceuDia) then return end
	if noturno(sky) then
		warn('[CeuWano] o Sky chegou em Wano com o skybox noturno: devolvido o ceu de dia')
		for f, id in pairs(ceuDia.faces) do sky['Skybox' .. f] = id end
	end
	if sky.MoonAngularSize ~= ceuDia.moon then sky.MoonAngularSize = ceuDia.moon end
	if sky.StarCount ~= ceuDia.stars then sky.StarCount = ceuDia.stars end
end

-- nuvens (Terrain.Clouds) neste cliente
local nuvemCriada, nuvemSalva = nil, nil
local function aplicarNuvens()
	if not NUVENS then return end
	local terr = workspace:FindFirstChildOfClass('Terrain')
	if not terr then return end
	local cl = terr:FindFirstChildOfClass('Clouds')
	if not cl then
		cl = Instance.new('Clouds')
		cl.Name = 'NuvensWanoLocal'
		cl.Cover = 0; cl.Density = NUVENS.Density; cl.Color = NUVENS.Color
		cl.Parent = terr
		nuvemCriada = cl
	elseif not nuvemSalva and cl ~= nuvemCriada then
		nuvemSalva = { obj = cl, Cover = cl.Cover, Density = cl.Density, Color = cl.Color, Enabled = cl.Enabled }
		cl.Enabled = true
	end
	TweenService:Create(cl, TweenInfo.new(1.6, Enum.EasingStyle.Sine),
		{ Cover = NUVENS.Cover, Density = NUVENS.Density, Color = NUVENS.Color }):Play()
end
local function restaurarNuvens()
	if nuvemCriada then nuvemCriada:Destroy(); nuvemCriada = nil end
	if nuvemSalva then
		local s = nuvemSalva
		if s.obj.Parent then
			s.obj.Cover = s.Cover; s.obj.Density = s.Density; s.obj.Color = s.Color; s.obj.Enabled = s.Enabled
		end
		nuvemSalva = nil
	end
end

-- ------------------------------------------------------------------ bloom + raios de sol (proprios, fracos)
local bloom = Instance.new('BloomEffect')
bloom.Name = 'CeuWanoBloom'
bloom.Enabled = false
bloom.Intensity = 0
bloom.Size = BLOOM.Size
bloom.Threshold = BLOOM.Threshold
bloom.Parent = Lighting

local raios = Instance.new('SunRaysEffect')
raios.Name = 'CeuWanoSunRays'
raios.Enabled = false
raios.Intensity = 0
raios.Spread = RAIOS.Spread
raios.Parent = Lighting

-- ------------------------------------------------------------------ lacos (so trabalham com o jogador na area)
guardarCeuDia()
Lighting.ChildAdded:Connect(function(c) if c:IsA('Sky') and not ceuDia then task.defer(guardarCeuDia) end end)

task.spawn(function()          -- as pecas entram/saem com o streaming: reaplica enquanto estiver na area
	while true do
		task.wait(2)
		if ligado then
			pcall(aplicarFundos)
			if not mar then
				local ok, feito = pcall(criarMar)
				if ok and feito then fadeMar('entra') end
			end
			pcall(aplicarPad)
			pcall(aplicarSons)
		elseif not ceuDia then
			pcall(guardarCeuDia)
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

-- AGUA do Roblox + mar: as Textures com tag AguaCorrente rolam pelo atributo Velocidade (studs/s). So anima enquanto
-- o jogador esta na area; nas areas 3 e 4 quem rola e o CeuSombras / CeuNatagumo.
RunService.Heartbeat:Connect(function(dt)
	if not ligado then return end
	for _, t in ipairs(CS:GetTagged('AguaCorrente')) do
		local v = t:GetAttribute('Velocidade') or 12
		t.OffsetStudsV = (t.OffsetStudsV + v * dt) % math.max(t.StudsPerTileV, 1)
	end
end)

-- ------------------------------------------------------------------ liga / desliga
-- CurrentIslandMood e o PRIMEIRO atributo que o AreaAtmosphere publica na troca de area: e ele que manda. WanoMood
-- (patch [OP]) so vale se o CurrentIslandMood nao existir.
local function emWano()
	local mood = player:GetAttribute('CurrentIslandMood')
	if mood ~= nil then return mood == MOOD end
	return player:GetAttribute('WanoMood') == true
end

local function aplicar(on)
	if on == ligado then return end
	ligado = on
	if on then
		-- o Sky e compartilhado com CeuNatagumo/CeuSombras: espera os 2 devolverem o ceu deles antes de conferir
		-- (o AreaAtmosphere publica CurrentIslandMood ANTES de NatagumoMood/ShadowGardenMood)
		task.defer(function()
			local t0 = os.clock()
			while ligado and (player:GetAttribute('ShadowGardenMood') == true or player:GetAttribute('NatagumoMood') == true)
				and os.clock() - t0 < 5 do task.wait(0.1) end
			if not ligado then return end
			task.wait(0.1)
			if not ligado then return end
			pcall(garantirCeuDia)
			pcall(aplicarNuvens)
			bloom.Enabled = true; raios.Enabled = true
			TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = BLOOM.Intensity }):Play()
			TweenService:Create(raios, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = RAIOS.Intensity }):Play()
			pcall(aplicarFundos)
			local ok, feito = pcall(criarMar)
			if ok and feito then fadeMar('entra') end
			pcall(aplicarPad)
			pcall(aplicarSons)
		end)
	else
		-- sincrono: Wano nao segura o Sky (nada a devolver); o resto sai ja
		restaurarFundos()
		restaurarPartes(padSalvo)
		restaurarSons()
		restaurarNuvens()
		SoundService.AmbientReverb = reverbOriginal
		if mar then
			local velho = mar
			mar = nil
			cancelarMarTweens()
			for _, d in ipairs(velho:GetDescendants()) do
				if d:IsA('BasePart') or d:IsA('Texture') then
					TweenService:Create(d, TweenInfo.new(1.2, Enum.EasingStyle.Sine), { Transparency = 1 }):Play()
				end
			end
			task.delay(1.3, function() velho:Destroy() end)
		end
		for _, ef in ipairs({ bloom, raios }) do
			local t = TweenService:Create(ef, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = 0 })
			t.Completed:Once(function() if not ligado then ef.Enabled = false end end)
			t:Play()
		end
	end
end

local function reavaliar()
	aplicar(emWano())
end
player:GetAttributeChangedSignal('WanoMood'):Connect(reavaliar)
player:GetAttributeChangedSignal('CurrentIslandMood'):Connect(reavaliar)
reavaliar()
