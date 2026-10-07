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

local function hasEquipmentVFX(player)
 local char=player and player.Character
 local tool=char and char:FindFirstChild('Picareta')
 return tool and tool:GetAttribute('VisualVersion')=='EquipmentV3'
end

local Mineracao = {}
-- minerio TEMPORARIO (Masmorra das Sombras, Ilha 3): nao vai para a mochila, nao gasta energia, nao chama chefe e nao
-- renasce. Quem da a recompensa e o DungeonService, ouvindo este evento: (rocha, quemQuebrou, {player1, player2, ...}).
Mineracao.Quebrou = Instance.new("BindableEvent")
local rnd = Random.new()
local pending = {}
local dropsPendentes = {} -- [player] = { drops = {}, espaco = 0, hats = 0 }
local proximoDropId = 0
local TEMPO_COLETA = 5
local proximoGolpe = {}  -- [player] = deadline monotono, sem acelerar por spam de remotes
local golpesNaRocha = setmetatable({}, { __mode = "k" }) -- [rocha] = { [player] = golpes }
local TOLERANCIA = 0.025 -- absorve jitter de 30 FPS; deadline com divida impede ganho sustentado
local INTERVALO_AVISO = 6 -- um aviso imediato por motivo; nao repete toast/som a cada tentativa automatica
local ultimoAviso = {} -- [player] = { cheia = tempo, ["bloqueada:<areaId>"] = tempo }
local RESPAWN_ROCHA = Config.RESPAWN_ROCHA
local IgnisService -- injetado (IgnisService requer PlayerData/Economia; evita ciclo)

local function feedbackLimitado(player, motivo, info)
	local avisos = ultimoAviso[player]
	if not avisos then
		avisos = {}
		ultimoAviso[player] = avisos
	end
	local agora = os.clock()
	if agora - (avisos[motivo] or -math.huge) < INTERVALO_AVISO then return false end
	avisos[motivo] = agora
	RS.Remotes.FeedbackMina:FireClient(player, info)
	return true
end

local function avisarMochilaCheia(player, perfil, texto, idMin)
 local carregado = PlayerData.itensNaMochila(perfil) + ((dropsPendentes[player] and dropsPendentes[player].espaco) or 0)
	local capacidade = PlayerData.capacidade(perfil)
	local cheio = carregado >= capacidade
	if feedbackLimitado(player, cheio and "cheia" or "sem_espaco", {
		tipo = "cheia", origem = "mochila_minerio",
		texto = cheio and texto or "Sem espaço para este minério. Venda ou escolha outro.",
		carregado = carregado, capacidade = capacidade,
		espaco = idMin and Config.espacoMinerio(idMin) or 1 }) and cheio then
		Ofertas.mochilaCheia(player, perfil)
	end
end

local function mochilaCheiaComPendentes(player, perfil, idMin)
 if PlayerData.mochilaInfinita(perfil) then return false end
 local reservado = dropsPendentes[player] and dropsPendentes[player].espaco or 0
 return PlayerData.itensNaMochila(perfil) + reservado + Config.espacoMinerio(idMin) > PlayerData.capacidade(perfil)
end

local function concluirDrop(player, drop, forcar)
 local fila = dropsPendentes[player]
 if not fila or fila.drops[drop.id] ~= drop then return false end
 local perfil = PlayerData.get(player)
 if not perfil then return false end
 if not forcar and (PlayerData.mochilaCheia(perfil, drop.minerioId)
  or (drop.hat and PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil))) then
  return false
 end
 fila.drops[drop.id] = nil
 fila.espaco -= Config.espacoMinerio(drop.minerioId)
 fila.count -= 1
 if drop.hat then fila.hats -= 1 end
 if drop.garantidoConta then fila.contaGarantida = false end
 if drop.garantidoArea then fila.areasGarantidas[drop.areaId] = nil end
 perfil.mochila[drop.minerioId] = (perfil.mochila[drop.minerioId] or 0) + 1
 perfil.minerados = (perfil.minerados or 0) + 1
 Telemetria.marco(player, perfil, "FirstOreMined", { mundo = drop.areaId })
 if drop.hat then
  local uid
  if forcar and PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil) then
   uid = PlayerData.novoHat(perfil, drop.hat.id, Recompensas.nivelDrop(perfil))
  else
   uid = Recompensas.darHat(player, perfil, drop.hat, "minerio")
  end
  if uid then
   if drop.garantidoConta then perfil.tel.HatGarantido = os.time() end
   if drop.garantidoArea then
    perfil.tel["PrimeiroMinerioHat_" .. drop.areaId] = os.time()
    Recompensas.equiparSeMelhor(player, perfil, uid)
   end
  end
 end
 if not forcar then
  local infoMinerio = Config.infoMinerio(drop.minerioId)
  RS.Remotes.FeedbackMina:FireClient(player, {
   tipo = "dropColetado", id = drop.id,
   variante = drop.varianteId, nome = infoMinerio and infoMinerio.nome,
  })
  PlayerData.sincronizar(player)
 end
 return true
end

function Mineracao.concluirDropsPendentes(player)
 local fila = dropsPendentes[player]
 if not fila then return end
 for _, drop in pairs(fila.drops) do concluirDrop(player, drop, true) end
 dropsPendentes[player] = nil
end

local function criarDrop(player, perfil, rocha, areaId, varianteId, minerioId, hat, garantidoConta, garantidoArea)
 local fila = dropsPendentes[player]
 if not fila then
  fila = { drops = {}, espaco = 0, hats = 0, count = 0, areasGarantidas = {} }
  dropsPendentes[player] = fila
 end
 proximoDropId += 1
 local drop = {
  id = proximoDropId, minerioId = minerioId, areaId = areaId, varianteId = varianteId,
  hat = hat, garantidoConta = garantidoConta, garantidoArea = garantidoArea,
 }
 fila.drops[drop.id] = drop
 fila.espaco += Config.espacoMinerio(minerioId)
 fila.count += 1
 if hat then fila.hats += 1 end
 if drop.garantidoConta then fila.contaGarantida = true end
 if drop.garantidoArea then fila.areasGarantidas[areaId] = true end
 RS.Remotes.FeedbackMina:FireClient(player, {
  tipo = "dropMinerio", id = drop.id, pos = rocha.Position,
  tema = rocha:GetAttribute("Tema"), variante = varianteId,
  hatId = hat and hat.id, hatNome = hat and hat.nome,
  hatRaridade = hat and hat.raridade,
  hatAssetId = hat and (Config.HatAssets[hat.id] or hat.assetId),
  coletaEm = workspace:GetServerTimeNow() + TEMPO_COLETA,
 })
 task.delay(TEMPO_COLETA, function()
  if not dropsPendentes[player] or dropsPendentes[player].drops[drop.id] ~= drop then return end
  if concluirDrop(player, drop, false) then return end
  -- Outra recompensa pode ocupar a mochila enquanto o drop aguarda. Ele permanece
  -- no chao e e entregue assim que houver espaco, sem apagar o item sorteado.
  task.spawn(function()
   while dropsPendentes[player] and dropsPendentes[player].drops[drop.id] == drop do
    task.wait(2)
    if concluirDrop(player, drop, false) then break end
   end
  end)
 end)
end

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
	-- HP fracionário ainda precisa de um golpe; nunca exibir 0 antes da quebra.
	return Config.formatar(n > 0 and math.ceil(n) or 0)
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

-- Uma espera por rocha ativa, mesmo quando varios jogadores a atingem a 8 Hz.
local barraPendente = setmetatable({}, { __mode = "k" })
local function ativarBarra(rocha)
	local bb = rocha:FindFirstChild("Vida")
	if not bb then return end
	bb.Enabled = true
	rocha:SetAttribute("UltimoGolpe", os.clock())
	if barraPendente[rocha] then return end
	barraPendente[rocha] = true
	task.spawn(function()
		while rocha.Parent and bb.Parent do
			local ultimo = rocha:GetAttribute("UltimoGolpe")
			if not ultimo then break end
			local falta = 3 - (os.clock() - ultimo)
			if falta <= 0 then break end
			task.wait(falta)
		end
		if bb.Parent then bb.Enabled = false end
		barraPendente[rocha] = nil
	end)
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
-- Como nas caixas normais do Unboxing, todo jogador que acertou ao menos um golpe
-- valido recebe seu proprio drop. Mochila/hat/garantias continuam no perfil do AMS.
local function premiarNormal(rocha, player, golpes, areaId, varianteId, variante, minerioId, efeito)
	if player.Parent ~= Players then return false end
	local perfil = PlayerData.get(player)
	if not perfil or not perfil.areas[areaId] then return false end
 if mochilaCheiaComPendentes(player, perfil, minerioId) then
		avisarMochilaCheia(player, perfil, "Mochila cheia! Venda com o Ignis para receber novos minerios.", minerioId)
		return false
	end
	registrarGolpes(perfil, areaId, varianteId, golpes)

	if efeito then
		local info = Config.infoMinerio(minerioId)
		local extra = Recompensas.darMoedas(player, perfil, (info and info.valor or 1) * efeito.mult * Economia.multMoedas(player, perfil), "Gameplay", "efeito_" .. rocha:GetAttribute("Efeito"))
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area", texto = efeito.nome .. "! +" .. Config.formatar(extra) .. " moedas" })
	end
	PlayerData.progredirMissao(perfil, areaId, "minerar", 1)
	if variante.ordem >= 4 then PlayerData.progredirMissao(perfil, areaId, "epico", 1) end

 local fila = dropsPendentes[player]
 local totalMinerados = (perfil.minerados or 0) + (fila and fila.count or 0) + 1
 local garantidoConta = totalMinerados >= 3 and not perfil.tel.HatGarantido and not (fila and fila.contaGarantida)
	local marcaArea = "PrimeiroMinerioHat_" .. areaId
 local garantidoArea = areaId > 1 and not perfil.tel[marcaArea] and not (fila and fila.areasGarantidas[areaId])
 local hat
 local hatsReservados = fila and fila.hats or 0
 if (garantidoConta or garantidoArea or rnd:NextNumber() < variante.hatChance)
  and PlayerData.totalHats(perfil) + hatsReservados < PlayerData.capacidadeHats(perfil) then
  local raridade = Recompensas.sortearRaridadeHat(player, perfil, variante.hatSorte)
  local lista = Config.hatsDoTema(rocha:GetAttribute("Tema"), raridade)
  hat = lista[rnd:NextInteger(1, math.max(1, #lista))]
 end

 criarDrop(player, perfil, rocha, areaId, varianteId, minerioId, hat,
  hat and garantidoConta, hat and garantidoArea)

	local info = Config.infoMinerio(minerioId)
	RS.Remotes.FeedbackMina:FireClient(player, { tipo = "quebrou", pos = rocha.Position, chefe = false, variante = varianteId, valor = info and info.valor or 0 })
	return true
end

local function quebrar(rocha, player)
	local areaId = rocha:GetAttribute("AreaId")
	local ehChefe = rocha:GetAttribute("Chefe")
	local grupo = rocha.Parent

	if ehChefe then
		-- chefe global: recompensa de todos os participantes fica no BossService
		BossService.morreu(rocha)
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "quebrou", pos = rocha.Position, chefe = true, variante = "chefe" })
		if rocha:GetAttribute("OreType") and not hasEquipmentVFX(player) then vfx(OreVFX.Break, rocha) end
		esconder(rocha)
		task.delay(2, function() if grupo then grupo:Destroy() end end)
		return
	end

	if rocha:GetAttribute("Temporario") then
		local contribuintes = golpesNaRocha[rocha] or { [player] = 1 }
		golpesNaRocha[rocha] = nil
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "quebrou", pos = rocha.Position, chefe = false, variante = rocha:GetAttribute("Variante"), valor = 0 })
		if rocha:GetAttribute("OreType") and not hasEquipmentVFX(player) then vfx(OreVFX.Break, rocha) end
		esconder(rocha)
		-- BindableEvent copia a tabela e DESCARTA chaves que sao Instance: manda a LISTA de quem golpeou
		local quem = {}
		for p in pairs(contribuintes) do if typeof(p) == "Instance" then table.insert(quem, p) end end
		Mineracao.Quebrou:Fire(rocha, player, quem)
		task.delay(1.5, function() if grupo then grupo:Destroy() end end)
		return
	end

	local varianteId = rocha:GetAttribute("Variante")
	local variante = Config.variantePorId(varianteId) or Config.Variantes[1]
	local minerioId = Config.idMinerio(rocha:GetAttribute("Tema"), varianteId)
	local contribuintes = golpesNaRocha[rocha] or { [player] = 1 }
	golpesNaRocha[rocha] = nil
	local efeito = Config.SPAWN.efeitos[rocha:GetAttribute("Efeito") or ""]
	local premiados = 0
	for participante, golpes in pairs(contribuintes) do
		if typeof(participante) == "Instance" and participante:IsA("Player")
			and premiarNormal(rocha, participante, golpes, areaId, varianteId, variante, minerioId, efeito) then
			premiados += 1
		end
	end
	if premiados == 0 then
		-- O unico atacante pode ter enchido a mochila enquanto o impacto estava em voo.
		-- Nesse caso a rocha volta inteira, sem perder o drop nem disparar respawn.
		rocha:SetAttribute("HP", rocha:GetAttribute("HPMax"))
		rocha:SetAttribute("Quebrando", nil)
		atualizarBarra(rocha)
		return
	end
	SpawnMinerio.quebrou(areaId, varianteId)
	BossService.quebra(areaId)

	if rocha:GetAttribute("OreType") and not hasEquipmentVFX(player) then vfx(OreVFX.Break, rocha) end
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
  if res and res.ok and not mochilaCheiaComPendentes(player, perfil, idMin) then return true end
	end
	avisarMochilaCheia(player, perfil, "Mochila cheia! Venda com o Ignis (teleporte gratis).", idMin)
	return false
end

-- A animacao pertence aos jogadores proximos; a 8 golpes/s nao ha motivo para
-- transmitir dois eventos por golpe a todos os clientes de todas as ilhas.
local function animarVisiveis(minerador, rocha, ...)
	local pos = rocha.Position
	for _, observador in ipairs(Players:GetPlayers()) do
		local char = observador.Character
		local raiz = char and char:FindFirstChild("HumanoidRootPart")
		if observador == minerador or (raiz and (raiz.Position - pos).Magnitude <= 100) then
			RS.Remotes.AnimarPicareta:FireClient(observador, minerador, rocha, ...)
		end
	end
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
	local deadline = proximoGolpe[player] or 0
	if pending[player] or agora + TOLERANCIA < deadline then return end
	if not perfil.areas[rocha:GetAttribute("AreaId")] then
		feedbackLimitado(player, "bloqueada:" .. tostring(rocha:GetAttribute("AreaId")),
			{ tipo = "bloqueada", texto = "Area bloqueada" })
		return
	end
	local ehChefe = rocha:GetAttribute("Chefe")
	local temporario = rocha:GetAttribute("Temporario")
	-- minerio da masmorra: so quem esta na corrida dona dele golpeia; mochila cheia nao bloqueia (nao usa mochila)
	if temporario and player:GetAttribute("DungeonRun") ~= rocha:GetAttribute("DonoRun") then return end
	local idMin = Config.idMinerio(rocha:GetAttribute("Tema"), rocha:GetAttribute("Variante"))
 if not ehChefe and not temporario and mochilaCheiaComPendentes(player, perfil, idMin) then
		proximoGolpe[player] = agora + math.min(intervalo, .3)
		if not tratarMochilaCheia(player, perfil, idMin) then return end
	end
	local avisos = ultimoAviso[player]
	if avisos and not ehChefe and not temporario then
		avisos.cheia = nil -- novo ciclo depois que a mochila foi esvaziada
	end
	local prazoReservado = math.max(agora, deadline) + intervalo
	proximoGolpe[player] = prazoReservado
	Economia.registrarGolpe(player)
	local token = {}
	pending[player] = token
	local function devolverGolpeAbortado()
		-- Um golpe sem impacto nao consome a cadencia. O piso curto limita
		-- animacoes repetidas se o jogador oscilar na borda do alcance.
		if player.Parent == Players and proximoGolpe[player] == prazoReservado then
			proximoGolpe[player] = math.max(deadline, os.clock() + .12)
		end
	end
	local starts = workspace:GetServerTimeNow() + .02
	animarVisiveis(player, rocha, starts, false, nil, nil, nil, intervalo)
	task.delay(.02 + Geometry.impactTime(intervalo), function()
		if pending[player] ~= token then return end
		pending[player] = nil
		if player.Character ~= char or not char:FindFirstChild("Picareta") or not Geometry.canReach(char, rocha) then
			devolverGolpeAbortado()
			return
		end
		local perfilAgora = PlayerData.get(player)
  if not perfilAgora or (not ehChefe and not temporario and mochilaCheiaComPendentes(player, perfilAgora, idMin)) then
			devolverGolpeAbortado()
			return
		end
		if temporario and player:GetAttribute("DungeonRun") ~= rocha:GetAttribute("DonoRun") then
			devolverGolpeAbortado()
			return
		end
		if rocha:GetAttribute("Quebrando") or (rocha:GetAttribute("HP") or 0) <= 0 then
			devolverGolpeAbortado()
			return
		end
		if not ehChefe and not temporario then
			if Recompensas.entregaEntradaArea(player, perfilAgora, rocha:GetAttribute("AreaId")) then
				PlayerData.sincronizar(player)
			end
		end
		local hrp = char.HumanoidRootPart
		local dano = PlayerData.dano(perfilAgora)
		local hpAtual = rocha:GetAttribute("HP")
		local hpMax = rocha:GetAttribute("HPMax")
		-- Quantizacao de hits: mais golpes/s com menor dano por golpe pode piorar
		-- o tempo de quebra exatamente nos limiares de HP. Um piso de dano por
		-- minerio preserva o TTK da v3.2, inclusive os one-shots ja conquistados.
		if not ehChefe and not temporario and hpMax and hpMax > 0 then
			local pic = Config.picaretaPorId(perfilAgora.picareta)
			if pic and pic.mult and pic.mult > 0 and pic.multReferencia and pic.intervaloReferencia then
				local danoAntigo = dano * pic.multReferencia / pic.mult
				if danoAntigo > 0 then
					local golpesAntigos = math.max(1, math.ceil(hpMax / danoAntigo))
					local prazoAntigo = .05 + Geometry.ImpactTime + (golpesAntigos - 1) * pic.intervaloReferencia
					local prazoNovo = .02 + Geometry.impactTime(intervalo)
					local golpesMaximos = golpesAntigos == 1 and 1
						or math.max(1, math.floor((prazoAntigo - prazoNovo + 1e-6) / intervalo) + 1)
					dano = math.max(dano, hpMax / golpesMaximos * (1 + 1e-10))
				end
			end
		end
		local hp = math.max(0, hpAtual - dano)
		rocha:SetAttribute("HP", hp)
		if hp <= 0 then rocha:SetAttribute("Quebrando", true) end
		if ehChefe then
			BossService.aplicarDano(player, rocha, dano)
		else
			golpesNaRocha[rocha] = golpesNaRocha[rocha] or {}
			golpesNaRocha[rocha][player] = (golpesNaRocha[rocha][player] or 0) + 1
		end

		if not ehChefe then ativarBarra(rocha) end

		atualizarBarra(rocha)
		if rocha:GetAttribute("OreType") and hp > 0 and not hasEquipmentVFX(player) then vfx(OreVFX.Hit, rocha, Geometry.contact(rocha, hrp.Position)) end
		animarVisiveis(player, rocha, workspace:GetServerTimeNow(), true, Geometry.contact(rocha, hrp.Position), starts, hp <= 0, intervalo)
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
		proximoGolpe[p] = nil
		pending[p] = nil
		ultimoAviso[p] = nil
		for rocha, contribuintes in pairs(golpesNaRocha) do
			contribuintes[p] = nil
			if not next(contribuintes) then golpesNaRocha[rocha] = nil end
		end
	end)
end

return Mineracao
