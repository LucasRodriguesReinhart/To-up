local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Config = require(RS.Config)
local Geometry = require(RS.MiningGeometry)
local PlayerData = require(script.Parent.PlayerData)
local OreVFX = require(RS:WaitForChild("OreVFX"))
local AreaBuilder = require(script.Parent.AreaBuilder)
local SpawnMinerio = require(script.Parent.SpawnMinerio)
local Economia = require(script.Parent.Economia)
local Recompensas = require(script.Parent.Recompensas)
local BossService = require(script.Parent.BossService)
local Telemetria = require(script.Parent.Telemetria)
local Ofertas = require(script.Parent.Ofertas)
local Passes = require(script.Parent.Passes)

local function vfx(fn, ...)
	local ok, err = pcall(fn, ...)
	if not ok then warn("[Mineracao] OreVFX: " .. tostring(err)) end
end

local Mineracao = {}
local rnd = Random.new()
local pending = {}
local ultimoGolpe = {}   -- [player] = os.clock()
local golpesNaRocha = setmetatable({}, { __mode = "k" }) -- [rocha] = { [player] = golpes }
local TOLERANCIA = 0.06  -- latencia: o cliente pede um pouco depois do intervalo
local RESPAWN_ROCHA = Config.RESPAWN_ROCHA
local IgnisService -- injetado (IgnisService requer PlayerData/Economia; evita ciclo)

local FAIXAS = { { 1, 1, "1" }, { 2, 3, "2-3" }, { 4, 7, "4-7" }, { 8, 15, "8-15" }, { 16, 40, "16-40" }, { 41, math.huge, "41+" } }

-- ---------- HISTOGRAMA DE GOLPES (agregado; enviado ao sair da ilha ou do jogo) ----------
local function registrarGolpes(perfil, areaId, varianteId, golpes)
	perfil.__hist = perfil.__hist or {}
	local h = perfil.__hist[areaId] or { n = 0 }
	perfil.__hist[areaId] = h
	h.n += 1
	for _, f in ipairs(FAIXAS) do
		if golpes >= f[1] and golpes <= f[2] then
			local k = varianteId .. ":" .. f[3]
			h[k] = (h[k] or 0) + 1
			break
		end
	end
end

function Mineracao.enviarHistograma(player, perfil)
	if not perfil or not perfil.__hist then return end
	for areaId, h in pairs(perfil.__hist) do
		if h.n > 0 then
			local detalhes = { mundo = areaId }
			for k, v in pairs(h) do if k ~= "n" then detalhes[k] = v end end
			Telemetria.evento(player, perfil, "OreHitsHistogram", h.n, detalhes)
		end
	end
	perfil.__hist = {}
end

-- ---------- BARRA DE VIDA ----------
local function fmt(n)
	return Config.formatar(math.max(math.floor(n), 0))
end

local function atualizarBarra(rocha)
	local bb = rocha:FindFirstChild("Vida")
	if not bb then return end
	local barra = bb:FindFirstChild("Barra", true)
	local texto = bb:FindFirstChild("HPTexto", true)
	local hp, hpMax = rocha:GetAttribute("HP"), rocha:GetAttribute("HPMax")
	if barra then
		barra.Size = UDim2.fromScale(math.clamp(hp / hpMax, 0, 1), 1)
		local f = math.clamp(hp / hpMax, 0, 1)
		if not rocha:GetAttribute("Chefe") then
			barra.BackgroundColor3 = Color3.fromRGB(120, 220, 130):Lerp(Color3.fromRGB(255, 100, 70), 1 - f)
		end
	end
	if texto then
		texto.Text = fmt(hp) .. " / " .. fmt(hpMax)
	end
end

local function avisarIlha(areaId, texto)
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == areaId then
			RS.Remotes.FeedbackMina:FireClient(p, { tipo = "area", texto = texto })
		end
	end
end

local function esconder(rocha)
	local visual = rocha.Parent and rocha.Parent:FindFirstChild("Visual")
	if visual then
		for _, d in ipairs(visual:GetDescendants()) do
			if d:IsA("BasePart") then
				d:SetAttribute("MiningVisibleTransparency", d.Transparency)
				d.Transparency = 1
				d.CanQuery = false
			end
		end
	end
	rocha.CanCollide = false
	rocha.CanQuery = false
	local cd = rocha:FindFirstChildOfClass("ClickDetector")
	if cd then cd.MaxActivationDistance = 0 end
	local bb = rocha:FindFirstChild("Vida")
	if bb then bb.Enabled = false end
	rocha:SetAttribute("UltimoGolpe", nil)
end

-- ---------- QUEBRA ----------
local function quebrar(rocha, player)
	local areaId = rocha:GetAttribute("AreaId")
	local ehChefe = rocha:GetAttribute("Chefe")
	local grupo = rocha.Parent

	if ehChefe then
		-- chefe global: recompensa de todos os participantes fica no BossService
		BossService.morreu(rocha)
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "quebrou", pos = rocha.Position, chefe = true, variante = "chefe" })
		if rocha:GetAttribute("OreType") then vfx(OreVFX.Break, rocha) end
		esconder(rocha)
		task.delay(2, function() if grupo then grupo:Destroy() end end)
		return
	end

	local perfil = PlayerData.get(player)
	if not perfil then return end
	local varianteId = rocha:GetAttribute("Variante")
	local variante = Config.variantePorId(varianteId) or Config.Variantes[1]
	local minerioId = Config.idMinerio(rocha:GetAttribute("Tema"), varianteId)

	if PlayerData.mochilaCheia(perfil, minerioId) then
		-- nao deveria chegar aqui (o golpe e recusado antes), mas a rocha nunca fica travada em HP 0
		rocha:SetAttribute("HP", rocha:GetAttribute("HPMax"))
		atualizarBarra(rocha)
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "cheia", texto = "Mochila cheia!" })
		return
	end

	local contagem = golpesNaRocha[rocha] and golpesNaRocha[rocha][player] or 1
	registrarGolpes(perfil, areaId, varianteId, contagem)
	golpesNaRocha[rocha] = nil

	perfil.mochila[minerioId] = (perfil.mochila[minerioId] or 0) + 1
	perfil.minerados = (perfil.minerados or 0) + 1
	Telemetria.marco(player, perfil, "FirstOreMined", { mundo = areaId })
	SpawnMinerio.quebrou(areaId, varianteId)
	BossService.quebra(areaId)

	local efeito = Config.SPAWN.efeitos[rocha:GetAttribute("Efeito") or ""]
	if efeito then
		local info = Config.infoMinerio(minerioId)
		local extra = Recompensas.darMoedas(player, perfil, (info and info.valor or 1) * efeito.mult * Economia.multMoedas(player, perfil), "Gameplay", "efeito_" .. rocha:GetAttribute("Efeito"))
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area", texto = efeito.nome .. "! +" .. Config.formatar(extra) .. " moedas" })
	end
	PlayerData.progredirMissao(perfil, areaId, "minerar", 1)
	if variante.ordem >= 4 then
		PlayerData.progredirMissao(perfil, areaId, "epico", 1)
	end

	-- hat: chance pelo tipo de minerio; onboarding garante um hat no 3o minerio da conta
	local garantido = perfil.minerados >= 3 and not perfil.tel.HatGarantido
	if garantido or rnd:NextNumber() < variante.hatChance then
		if garantido then perfil.tel.HatGarantido = os.time() end
		Recompensas.darHatAleatorio(player, perfil, rocha:GetAttribute("Tema"), variante.hatSorte, "minerio")
	end

	RS.Remotes.FeedbackMina:FireClient(player, { tipo = "quebrou", pos = rocha.Position, chefe = false, variante = varianteId, valor = Config.infoMinerio(minerioId) and Config.infoMinerio(minerioId).valor or 0 })
	PlayerData.sincronizar(player)

	if rocha:GetAttribute("OreType") then vfx(OreVFX.Break, rocha) end
	esconder(rocha)

	-- escada de spawn: comum renasce sempre; o que a quebra liberou entra na fila
	local modArea = grupo and grupo.Parent
	if modArea and modArea.Name == "Rochas" then modArea = modArea.Parent end
	local pasta = modArea and modArea:FindFirstChild("Rochas")
	local perto = rocha.Position
	task.delay(RESPAWN_ROCHA, function()
		local area = Config.areaPorId(areaId)
		if not area or not pasta or not pasta.Parent then return end
		if varianteId == "comum" then
			local ok, novo = pcall(AreaBuilder.novoMinerio, area, pasta, grupo, "comum", nil, SpawnMinerio.pegarEfeito(areaId))
			local hit = ok and novo and novo:FindFirstChild("Hitbox")
			if hit then Mineracao.registrar(hit) elseif not ok then warn("[Mineracao] respawn: " .. tostring(novo)) end
		end
		if grupo then grupo:Destroy() end
		Mineracao.processarEnergia(area, pasta, perto)
	end)
end

local ORDEM_ESCADA = { "lendaria", "epica", "raro", "incomum" }
local ABAIXO = { incomum = "comum", raro = "incomum", epica = "raro", lendaria = "epica" }
local NOME_TIPO = { incomum = "INCOMUM", raro = "RARO", epica = "EPICO", lendaria = "LENDARIO" }

-- minerio do nivel de baixo mais perto de quem quebrou, inteiro (ninguem minerando) e vivo
local function candidatoAmplificar(pasta, variante, perto)
	if not perto then return nil end
	local melhor, dist = nil, Config.SPAWN.raioAmplificar
	for _, g in ipairs(pasta:GetChildren()) do
		local h = g.Name ~= "PedraChefe" and g:FindFirstChild("Hitbox")
		if h and h.CanQuery and h:GetAttribute("Variante") == variante and not h:GetAttribute("Efeito")
			and (h:GetAttribute("HP") or 0) >= (h:GetAttribute("HPMax") or 0) and h:GetAttribute("SpawnPos") then
			local d = (h.Position - perto).Magnitude
			if d < dist then melhor, dist = g, d end
		end
	end
	return melhor
end

-- barras de energia cheias: amplifica o minerio de baixo mais perto (estilo Unboxing Simulator);
-- sem candidato, nasce um novo num ponto sorteado.
function Mineracao.processarEnergia(area, pasta, perto)
	local vivos = {}
	for id in pairs(Config.SPAWN.barras) do vivos[id] = 0 end
	vivos.comum = 0
	for _, g in ipairs(pasta:GetChildren()) do
		local h = g:FindFirstChild("Hitbox")
		if h and h.CanQuery and not h:GetAttribute("Chefe") then
			local v = h:GetAttribute("Variante")
			if vivos[v] then vivos[v] += 1 end
		end
	end
	local nasceram, amplificados = {}, {}
	for _, id in ipairs(ORDEM_ESCADA) do
		for _ = 1, 10 do -- trava de seguranca por chamada
			local ok, custo = SpawnMinerio.tentarGerar(area.id, id, vivos[id])
			if not ok then break end
			local criou, novo
			local alvo = candidatoAmplificar(pasta, ABAIXO[id], perto)
			if alvo then
				local hitVelho = alvo.Hitbox
				local pos = hitVelho:GetAttribute("SpawnPos")
				local eraComum = hitVelho:GetAttribute("Variante") == "comum"
				if hitVelho:GetAttribute("OreType") then vfx(OreVFX.Break, hitVelho) end
				alvo:Destroy()
				criou, novo = pcall(AreaBuilder.novoMinerio, area, pasta, nil, id, pos, SpawnMinerio.pegarEfeito(area.id))
				if eraComum then
					local ok2, rep = pcall(AreaBuilder.novoMinerio, area, pasta, nil, "comum", nil, SpawnMinerio.pegarEfeito(area.id))
					local h2 = ok2 and rep and rep:FindFirstChild("Hitbox")
					if h2 then Mineracao.registrar(h2) end
				elseif vivos[ABAIXO[id]] then
					vivos[ABAIXO[id]] -= 1
				end
			else
				criou, novo = pcall(AreaBuilder.novoMinerio, area, pasta, nil, id, nil, SpawnMinerio.pegarEfeito(area.id))
			end
			local hit = criou and novo and novo:FindFirstChild("Hitbox")
			if hit then
				Mineracao.registrar(hit)
				vivos[id] += 1
				if alvo then amplificados[id] = (amplificados[id] or 0) + 1 else nasceram[id] = (nasceram[id] or 0) + 1 end
			else
				SpawnMinerio.devolver(area.id, id, custo)
				if not criou then warn("[Mineracao] spawn " .. id .. ": " .. tostring(novo)) end
				break
			end
		end
	end
	SpawnMinerio.publicar(area.id, vivos)
	local partes = {}
	for _, id in ipairs({ "lendaria", "epica" }) do
		if amplificados[id] then table.insert(partes, amplificados[id] .. " minerio(s) AMPLIFICADO(S) para " .. NOME_TIPO[id] .. "!") end
		if nasceram[id] then table.insert(partes, nasceram[id] .. " minerio(s) " .. NOME_TIPO[id] .. " surgiu na ilha") end
	end
	if #partes > 0 then avisarIlha(area.id, table.concat(partes, " + ")) end
end

-- mochila cheia: Auto Sell vende sozinho; sem o passe, aviso + oferta contextual (teleporte gratis primeiro)
local function tratarMochilaCheia(player, perfil, idMin)
	if IgnisService and Passes.possui(player, "AutoSell") then
		local res = IgnisService.vender(player, true)
		if res and res.ok and not PlayerData.mochilaCheia(perfil, idMin) then return true end
	end
	RS.Remotes.FeedbackMina:FireClient(player, { tipo = "cheia", texto = "Mochila cheia! Venda com o Ignis (teleporte gratis)." })
	Ofertas.mochilaCheia(player, perfil)
	return false
end

-- ---------- GOLPE ----------
function Mineracao.golpear(player, rocha)
	local char = player.Character
	if not Geometry.valid(rocha) or not rocha:IsDescendantOf(workspace.Areas) then return end
	if not char or not char:FindFirstChild("Picareta") or not Geometry.canReach(char, rocha) then return end
	local perfil = PlayerData.get(player)
	if not perfil then return end
	local agora = os.clock()
	local intervalo = PlayerData.intervalo(perfil)
	if pending[player] or (ultimoGolpe[player] and agora - ultimoGolpe[player] < intervalo - TOLERANCIA) then return end
	if not perfil.areas[rocha:GetAttribute("AreaId")] then
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "bloqueada", texto = "Area bloqueada" })
		return
	end
	local ehChefe = rocha:GetAttribute("Chefe")
	local idMin = Config.idMinerio(rocha:GetAttribute("Tema"), rocha:GetAttribute("Variante"))
	if not ehChefe and PlayerData.mochilaCheia(perfil, idMin) then
		ultimoGolpe[player] = agora
		if not tratarMochilaCheia(player, perfil, idMin) then return end
	end
	ultimoGolpe[player] = agora
	Economia.registrarGolpe(player)
	local token = {}
	pending[player] = token
	local starts = workspace:GetServerTimeNow() + .05
	RS.Remotes.AnimarPicareta:FireAllClients(player, rocha, starts)
	task.delay(Geometry.ImpactTime + .05, function()
		if pending[player] ~= token then return end
		pending[player] = nil
		if player.Character ~= char or not char:FindFirstChild("Picareta") or not Geometry.canReach(char, rocha) then return end
		local perfilAgora = PlayerData.get(player)
		if not perfilAgora or (not ehChefe and PlayerData.mochilaCheia(perfilAgora, idMin)) then return end
		if (rocha:GetAttribute("HP") or 0) <= 0 then return end
		local hrp = char.HumanoidRootPart
		local dano = PlayerData.dano(perfilAgora)
		local hp = rocha:GetAttribute("HP") - dano
		rocha:SetAttribute("HP", hp)
		if ehChefe then
			BossService.aplicarDano(player, rocha, dano)
		else
			golpesNaRocha[rocha] = golpesNaRocha[rocha] or {}
			golpesNaRocha[rocha][player] = (golpesNaRocha[rocha][player] or 0) + 1
		end

		local bb = rocha:FindFirstChild("Vida")
		if bb and not ehChefe then
			bb.Enabled = true
			local marca = os.clock()
			rocha:SetAttribute("UltimoGolpe", marca)
			task.delay(3, function()
				if rocha:GetAttribute("UltimoGolpe") == marca and bb then
					bb.Enabled = false
				end
			end)
		end

		atualizarBarra(rocha)
		if rocha:GetAttribute("OreType") and hp > 0 then vfx(OreVFX.Hit, rocha, Geometry.contact(rocha, hrp.Position)) end
		RS.Remotes.AnimarPicareta:FireAllClients(player, rocha, workspace:GetServerTimeNow(), true, Geometry.contact(rocha, hrp.Position))
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "golpe", dano = dano, pos = Geometry.contact(rocha, hrp.Position),
			variante = rocha:GetAttribute("Variante"), chefe = ehChefe, quebrou = hp <= 0 })

		if hp <= 0 then
			quebrar(rocha, player)
		end
	end)
end

function Mineracao.registrar(rocha)
	if rocha:GetAttribute("Registrada") then return end
	local cd = rocha:FindFirstChildOfClass("ClickDetector")
	if not cd then return end
	rocha:SetAttribute("Registrada", true)
	cd.MouseClick:Connect(function(player)
		Mineracao.golpear(player, rocha)
	end)
end

function Mineracao.iniciar(ignis)
	IgnisService = ignis
	local areas = workspace:WaitForChild("Areas")
	for _, d in ipairs(areas:GetDescendants()) do
		if d:IsA("BasePart") and d:GetAttribute("HPMax") then
			Mineracao.registrar(d)
		end
	end
	Players.PlayerRemoving:Connect(function(p)
		ultimoGolpe[p] = nil
		pending[p] = nil
	end)
end

return Mineracao

