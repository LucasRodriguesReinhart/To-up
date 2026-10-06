-- CeuSombras (LocalScript, StarterPlayerScripts) - ceu noturno da Ilha 3 (Shadow Garden).
-- O AreaAtmosphere e o dono do Lighting (ClockTime/Ambient/Atmosphere/ColorCorrection) e NAO toca em Sky nem Bloom
-- (auditoria C). Este script cuida dos efeitos locais, reagindo ao atributo ShadowGardenMood que o AreaAtmosphere publica:
--   * Sky: lua GRANDE + muitas estrelas enquanto o jogador esta na area sombra (a referencia tem uma lua enorme) e o
--     skybox padrao do Roblox no lugar do ceu anime de dia (as nuvens diurnas viravam manchas verdes no ceu noturno):
--     zenite preto, e o Atmosphere do AreaAtmosphere pinta a faixa azul eletrico do horizonte (efeitos 2026-10-06);
--   * Bloom proprio para o que e claro (neon, lanternas, efeitos) brilhar de noite.
--   * fundos das outras ilhas: esconde o chao distante do lobby e escurece o mar da Ilha 1 (so neste cliente).
--   * mar proprio, reverb da caverna e corte visual do subsolo e dos interiores das casas.
--   * luz do subsolo: ambiente (offset sobre o do AreaAtmosphere) + contraste no Salao Sombrio e na masmorra, camadas
--     de luz (L_SGCave_* / L_SGDun_* so ligadas onde o jogador esta) e postes NightOnly ligados (secao SUBSOLO).
-- Tudo restaurado ao sair. Local: nao afeta outros jogadores.
local Players = game:GetService('Players')
local Lighting = game:GetService('Lighting')
local TweenService = game:GetService('TweenService')
local player = Players.LocalPlayer

local MOON_SIZE = 32          -- MoonAngularSize na area (padrao do Roblox: 11); ClockTime 3,5 a poe a 37 graus em -X,
                              -- sobre o castelo para quem atravessa a ponte de entrada
local STARS = 3500
local BLOOM = { Intensity = 0.55, Size = 36, Threshold = 1.15 }
local SKYBOX_NOITE = 'rbxasset://textures/sky/sky512_'   -- + bk/dn/ft/lf/rt/up .tex (ceu padrao, preto a noite)
local FACES = { 'Bk', 'Dn', 'Ft', 'Lf', 'Rt', 'Up' }

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

-- SUBSOLO: luz no jogo (AUDITORIA3 09.01, 15.01, 10.11). So neste cliente, restaurado ao sair.
--  * Ambiente de subsolo: dentro do CAVE_Zone (Salao Sombrio) e das salas DUN_ROOM_* (ou em DungeonRun), o Ambient e
--    o OutdoorAmbient sobem um OFFSET violeta-frio SOMADO ao valor que o AreaAtmosphere (dono do Lighting) deixou,
--    com tween; ao sair voltam a esse valor. Sem briga com o AreaAtmosphere: so age 2 s depois do ShadowGardenMood
--    ligar (o tween de 1,6 s dele ja acabou; um tween novo na mesma propriedade cancelaria o dele), so restaura se o
--    Lighting ainda estiver no caminho base -> alvo deste script e, na troca de area, apenas solta (nao toca).
--  * ColorCorrection PROPRIO (CeuSombrasSubsolo) com contraste leve, para a rocha ler como forma e nao como preto.
--  * Camadas de luz: o export_sg da Range ate 60 aos interiores; sem Shadows a luz do Roblox atravessa rocha, entao
--    L_SGCave_* so ficam ligadas com o jogador no Salao Sombrio ou no poco da escada caracol e L_SGDun_* so na
--    masmorra (sem vazar no patio, no salao nem de uma camada na outra; na superficie sao 11 luzes a menos).
--  * Luzes NightOnly da ilha (postes, lanternas da praca, do patio e da saida): a area 3 e noite eterna e nada as
--    ligava (o export as grava desligadas para um ciclo dia/noite que a area nao tem).
local C = Color3.fromRGB
local SUB_AMBIENT = C(36, 32, 50)      -- offset somado ao Ambient (interior, sem ceu); metade desde a noite azul de
                                      -- 2026-10-06 (base mais clara + luzes de Range 60: o salao lavava de lilas)
local SUB_OUTDOOR = C(18, 16, 24)      -- metade no OutdoorAmbient (o poco e as frestas veem o ceu)
local SUB_CC = { Contrast = 0.08, Brightness = 0.02 }
local SUB_TWEEN = 1.4
local SUB_ESPERA = 2.0                 -- s depois do ShadowGardenMood ligar (tween do AreaAtmosphere: 1,6 s)
local SUB_FOLGA = 4                    -- histerese na borda das zonas (studs)
local LIGAR_NOTURNAS = true

local ccSub = Instance.new('ColorCorrectionEffect')
ccSub.Name = 'CeuSombrasSubsolo'
ccSub.Enabled = false
ccSub.Contrast = 0; ccSub.Brightness = 0
ccSub.Parent = Lighting

local moodDesde = math.huge
local sub = { ativo = false, base = nil, alvo = nil, tweens = {} }
local luzesSalvas = setmetatable({}, { __mode = 'k' })     -- [Light] = Enabled de antes

local function ilhaEMarcadores()
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	local ilha = a3 and a3:FindFirstChild('ILHA_SHADOWGARDEN')
	return ilha, ilha and ilha:FindFirstChild('GAMEPLAY_MARKERS')
end

-- p dentro da caixa do marcador: frente (fwd_x, fwd_z), sx de lado, sy na frente, de 0 a h acima dele; folga em volta
local function dentroCaixa(m, p, h, folga)
	local fx, fz = m:GetAttribute('fwd_x'), m:GetAttribute('fwd_z')
	local sx, sy = m:GetAttribute('sx'), m:GetAttribute('sy')
	if not (fx and fz and sx and sy and h) then return false end
	local frente = Vector3.new(fx, 0, fz).Unit
	local lado = Vector3.new(-frente.Z, 0, frente.X)
	local d = p - m.Position
	return math.abs(d:Dot(lado)) <= sx / 2 + folga and math.abs(d:Dot(frente)) <= sy / 2 + folga
		and d.Y >= -folga and d.Y <= h + folga
end

local function naCavernaZona(mk, p, folga)
	local cave = mk and mk:FindFirstChild('CAVE_Zone')
	return cave ~= nil and cave:IsA('BasePart') and dentroCaixa(cave, p, cave:GetAttribute('h'), folga)
end

-- 'masmorra' | 'caverna' (Salao Sombrio) | 'poco' (escada caracol entre o salao e o Salao Sombrio) | nil (superficie)
local function camadaSubsolo(folgaCave, folgaDun)
	if player:GetAttribute('DungeonRun') then return 'masmorra' end
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	local _, mk = ilhaEMarcadores()
	if not (hrp and mk) then return nil end
	local p = hrp.Position
	for _, m in ipairs(mk:GetChildren()) do
		if m:IsA('BasePart') and string.match(m.Name, '^DUN_ROOM_') then
			local piso, teto = m:GetAttribute('floor'), m:GetAttribute('ceil')
			if piso and teto and dentroCaixa(m, p, teto - piso, folgaDun) then return 'masmorra' end
		end
	end
	if naCavernaZona(mk, p, folgaCave) then return 'caverna' end
	local topo, pe = mk:FindFirstChild('THRONE_Stair_Top'), mk:FindFirstChild('THRONE_Stair_Bottom')
	if topo and pe and topo:IsA('BasePart') and pe:IsA('BasePart') then
		local h = Vector3.new(p.X - topo.Position.X, 0, p.Z - topo.Position.Z).Magnitude
		if h <= 22 and p.Y < topo.Position.Y - 3 and p.Y > pe.Position.Y - 4 then return 'poco' end
	end
	return nil
end

local function somar(c, d)
	return Color3.new(math.min(1, c.R + d.R), math.min(1, c.G + d.G), math.min(1, c.B + d.B))
end

-- o Lighting ainda esta entre a base e o alvo deste script (ninguem trocou no meio)?
local function aindaMeu(cor, base, alvo)
	local tol = 3 / 255
	for _, k in ipairs({ 'R', 'G', 'B' }) do
		local a, b = base[k], alvo[k]
		if cor[k] < math.min(a, b) - tol or cor[k] > math.max(a, b) + tol then return false end
	end
	return true
end

local function pararTweensSub()
	for _, t in ipairs(sub.tweens) do t:Cancel() end
	table.clear(sub.tweens)
end

local function tweenSub(obj, props)
	local t = TweenService:Create(obj, TweenInfo.new(SUB_TWEEN, Enum.EasingStyle.Sine), props)
	table.insert(sub.tweens, t)
	t:Play()
	return t
end

local function entrarAmbienteSubsolo()
	if sub.ativo then return end
	sub.ativo = true
	pararTweensSub()
	if not sub.base then           -- reentrada durante a volta: a base de antes continua valendo
		sub.base = { Ambient = Lighting.Ambient, OutdoorAmbient = Lighting.OutdoorAmbient }
	end
	sub.alvo = { Ambient = somar(sub.base.Ambient, SUB_AMBIENT), OutdoorAmbient = somar(sub.base.OutdoorAmbient, SUB_OUTDOOR) }
	tweenSub(Lighting, sub.alvo)
	ccSub.Enabled = true
	tweenSub(ccSub, SUB_CC)
end

-- soltar = true: a area mudou e o AreaAtmosphere ja esta no tween dele -> nao toca no Lighting
local function sairAmbienteSubsolo(soltar)
	if not sub.ativo and not sub.base then return end
	sub.ativo = false
	pararTweensSub()
	local base, alvo = sub.base, sub.alvo
	local volta = not soltar and base and alvo
		and aindaMeu(Lighting.Ambient, base.Ambient, alvo.Ambient)
		and aindaMeu(Lighting.OutdoorAmbient, base.OutdoorAmbient, alvo.OutdoorAmbient)
	if volta then
		tweenSub(Lighting, base).Completed:Once(function(estado)
			if estado == Enum.PlaybackState.Completed and not sub.ativo then sub.base = nil; sub.alvo = nil end
		end)
	else
		sub.base = nil; sub.alvo = nil
	end
	tweenSub(ccSub, { Contrast = 0, Brightness = 0 }).Completed:Once(function(estado)
		if estado == Enum.PlaybackState.Completed and not sub.ativo then ccSub.Enabled = false end
	end)
end

local function aplicarLuzesCamada(camada)
	local ilha = ilhaEMarcadores()
	local pasta = ilha and ilha:FindFirstChild('LIGHTS')
	if not pasta then return end
	for _, a in ipairs(pasta:GetChildren()) do
		local quer = nil
		if string.match(a.Name, '^L_SGCave') then
			quer = camada == 'caverna' or camada == 'poco'
		elseif string.match(a.Name, '^L_SGDun') then
			quer = camada == 'masmorra'
		elseif LIGAR_NOTURNAS and a:GetAttribute('NightOnly') then
			quer = true
		end
		if quer ~= nil then
			for _, l in ipairs(a:GetChildren()) do
				if l:IsA('Light') then
					if luzesSalvas[l] == nil then luzesSalvas[l] = l.Enabled end
					if l.Enabled ~= quer then l.Enabled = quer end
				end
			end
		end
	end
end

local function restaurarLuzesCamada()
	for l, ligada in pairs(luzesSalvas) do
		if l.Parent then l.Enabled = ligada end
		luzesSalvas[l] = nil
	end
end

local camadaAtual = nil
local function atualizarSubsoloLuz()
	-- histerese: quem ja esta numa zona so sai SUB_FOLGA alem da borda
	local camada = camadaSubsolo(camadaAtual == 'caverna' and SUB_FOLGA or 0, camadaAtual == 'masmorra' and SUB_FOLGA or 0)
	camadaAtual = camada
	aplicarLuzesCamada(camada)          -- todo tick: as luzes entram e saem com o streaming
	local quer = (camada == 'caverna' or camada == 'masmorra') and os.clock() - moodDesde >= SUB_ESPERA
	if quer then entrarAmbienteSubsolo() elseif sub.ativo then sairAmbienteSubsolo(false) end
end

task.spawn(function()
	while true do
		task.wait(0.3)
		if ligadoFundos then
			local ok, erro = pcall(atualizarSubsoloLuz)
			if not ok then warn('[CeuSombras] subsolo:', erro) end
		end
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
		local _, mk = ilhaEMarcadores()
		return naCavernaZona(mk, p, 0)
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
		moodDesde = os.clock()          -- o ambiente de subsolo espera o tween do AreaAtmosphere acabar
		aplicarFundos()
		atualizarMarArea3()
		atualizarSubsolo()
		atualizarInteriores()
		pcall(atualizarSubsoloLuz)
	else
		moodDesde = math.huge
		camadaAtual = nil
		restaurarLuzesCamada()
		sairAmbienteSubsolo(true)       -- troca de area: o AreaAtmosphere ja esta no tween dele, so solta
		restaurarFundos()
		restaurarSubsolo()
		restaurarInteriores()
		if marArea3 then marArea3:Destroy(); marArea3 = nil end
		SoundService.AmbientReverb = reverbOriginal
	end
	local sky = Lighting:FindFirstChildOfClass('Sky')
	if ligado then
		if sky and not salvo then
			salvo = { sky = sky, moon = sky.MoonAngularSize, stars = sky.StarCount, faces = {} }
			sky.MoonAngularSize = MOON_SIZE
			sky.StarCount = STARS
			for _, f in ipairs(FACES) do
				salvo.faces[f] = sky['Skybox' .. f]
				sky['Skybox' .. f] = SKYBOX_NOITE .. string.lower(f) .. '.tex'
			end
		end
		bloom.Enabled = true
		TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = BLOOM.Intensity }):Play()
	else
		if salvo then
			if salvo.sky.Parent then
				salvo.sky.MoonAngularSize = salvo.moon
				salvo.sky.StarCount = salvo.stars
				for f, id in pairs(salvo.faces) do salvo.sky['Skybox' .. f] = id end
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
