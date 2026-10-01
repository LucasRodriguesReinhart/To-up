local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local Config       = require(RS.Config)
local PlayerData   = require(script.Parent.PlayerData)
local AreaBuilder  = require(script.Parent.AreaBuilder)
local Mineracao    = require(script.Parent.Mineracao)
local IgnisService = require(script.Parent.IgnisService)
local GachaService  = require(script.Parent.GachaService)
local PetService    = require(script.Parent.PetService)
local HatVisual     = require(script.Parent.HatVisual)
local Progresso     = require(script.Parent.Progresso)
local Passes        = require(script.Parent.Passes)
local Codigos       = require(script.Parent.Codigos)
local Economia      = require(script.Parent.Economia)
local Telemetria    = require(script.Parent.Telemetria)
local ExperimentService = require(script.Parent.ExperimentService)
local Ofertas       = require(script.Parent.Ofertas)
local BossService   = require(script.Parent.BossService)
local Retencao      = require(script.Parent.Retencao)
local Produtos      = require(script.Parent.Produtos)
local RunService    = game:GetService("RunService")

local IslandTravel = require(script.Parent.IslandTravel)
local R = RS.Remotes

-- ---------- MUNDO ----------
AreaBuilder.construir()
IslandTravel.start()
Mineracao.iniciar(IgnisService)
Telemetria.usarExperimentos(ExperimentService)
BossService.iniciar(Mineracao)
Ofertas.iniciar()
Produtos.iniciar()

-- remotes novos da economia v3.1 (criados em runtime, o cliente usa WaitForChild)
local function remoteNovo(nome, classe)
	local r = R:FindFirstChild(nome) or Instance.new(classe)
	r.Name = nome
	r.Parent = R
	return r
end
local uiRate={}
remoteNovo("AtualizarUIProfile","RemoteFunction").OnServerInvoke=function(player,patch)
 if type(patch)~="table" then return {ok=false} end
 local now=os.clock()
 if now-(uiRate[player] or -math.huge)<.20 then return {ok=false,retryAfter=.3} end
 uiRate[player]=now
 return PlayerData.atualizarUI(player,patch)
end
Players.PlayerRemoving:Connect(function(player) uiRate[player]=nil end)

-- Audio settings are a small patch on the existing profile, never a new DataStore.
local audioRate = {}
remoteNovo("AtualizarAudioProfile", "RemoteFunction").OnServerInvoke = function(player, patch)
	if type(patch) ~= "table" then return { ok = false } end
	local now = os.clock()
	local state = audioRate[player] or { tokens = 8, clock = now }
	state.tokens = math.min(8, state.tokens + (now - state.clock) * 4)
	state.clock = now
	audioRate[player] = state
	if state.tokens < 1 then return { ok = false, retryAfter = .5 } end
	state.tokens -= 1
	return PlayerData.atualizarAudio(player, patch)
end
Players.PlayerRemoving:Connect(function(player) audioRate[player] = nil end)

remoteNovo("ResgatarDaily", "RemoteFunction").OnServerInvoke = function(player)
	return Retencao.resgatarDaily(player)
end

-- ponto de entrada da area 1, pra teleportar do lobby
local a1 = Config.Areas[1]
local ENTRADA = a1.centro + Vector3.new(0, 5, -a1.tamanho.Z / 2 + 14)
local LOBBY = Vector3.new(0, 7, 66)

-- ---------- JOGADORES ----------
local function aoEntrar(player)
	local perfilCarregado = PlayerData.carregar(player)
	if not perfilCarregado then return end
	ExperimentService.atribuir(player, perfilCarregado)
	Telemetria.marco(player, perfilCarregado, "Joined")
	-- onboarding: conta nova nasce DENTRO da ilha 1 (minerar nos primeiros segundos, sem andar pelo lobby)
	local novato = (perfilCarregado.minerados or 0) == 0 and not perfilCarregado.tel.SpawnIlha1
	player:GetAttributeChangedSignal("CurrentAreaId"):Connect(function()
		Mineracao.enviarHistograma(player, PlayerData.get(player))
	end)

	player.CharacterAdded:Connect(function(char)
		local hum = char:WaitForChild("Humanoid")
		task.wait(0.2)
		local perfil = PlayerData.get(player)
		if perfil then
			PlayerData.sincronizar(player)
			HatVisual.aplicar(player)
			if novato and not perfil.tel.SpawnIlha1 then
				perfil.tel.SpawnIlha1 = os.time()
				task.delay(1.2, function()
					local model = workspace.Areas:FindFirstChild("Area1")
					local entrada = model and model:GetAttribute("EntryPosition")
					if typeof(entrada) == "Vector3" and player.Character == char then IslandTravel.teleport(player, entrada) end
				end)
			end
		end
	end)

	task.wait(0.5)
	PlayerData.sincronizar(player)
end

Players.PlayerAdded:Connect(aoEntrar)
for _, p in ipairs(Players:GetPlayers()) do task.spawn(aoEntrar, p) end

Players.PlayerRemoving:Connect(function(player)
	local perfil = PlayerData.get(player)
	if perfil then
		Mineracao.enviarHistograma(player, perfil)
		Telemetria.evento(player, perfil, "SessionEnded", math.floor((os.clock() - (perfil.__entrouEm or os.clock())) / 6) / 10,
			{ mundo = PlayerData.maiorArea(perfil) })
	end
	PlayerData.descarregar(player)
	GachaService.limpar(player)
end)

game:BindToClose(function()
	for _, p in ipairs(Players:GetPlayers()) do
		PlayerData.salvar(p, true)
	end
	task.wait(2)
end)

-- autosave
task.spawn(function()
	while true do
		task.wait(120)
		for _, p in ipairs(Players:GetPlayers()) do
			PlayerData.salvar(p)
		end
	end
end)

-- ---------- REMOTES ----------
R.PedirDados.OnServerInvoke = function(player)
	local perfil = PlayerData.get(player)
	if not perfil then return nil end
	local snap = PlayerData.snapshot(perfil)
	snap.passes = Passes.todos(player)
	return snap
end

-- comprou passe dentro do jogo: libera na hora
Passes.aoComprar.Event:Connect(function(player)
	PlayerData.sincronizar(player)
end)

R.EquiparPicareta.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return IgnisService.equiparPicareta(player, id)
end

-- alvo = uid do pet; lista = uids dos pets que viram comida
R.AlimentarPet.OnServerInvoke = function(player, alvoUid, lista)
	if type(lista) ~= "table" or #lista > 300 then return { ok = false } end
	return PetService.alimentar(player, alvoUid, lista)
end

R.RenomearPet.OnServerInvoke = function(player, id, texto)
	return PetService.renomear(player, id, texto)
end

R.ComprarArea.OnServerInvoke = function(player, areaId)
	return Progresso.comprarArea(player, areaId)
end

R.ResgatarMissao.OnServerInvoke = function(player, id)
	return Progresso.resgatarMissao(player, id)
end

-- aviso de area bloqueada: o cliente abre a confirmacao de compra
local function avisarBloqueada(player, area)
	R.FeedbackMina:FireClient(player, { tipo = "comprarArea", areaId = area.id,
		texto = area.nome .. " custa " .. Config.formatar(area.custo) .. " moedas" })
end

R.EquiparPet.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	local res = PetService.equipar(player, id)
	local perfil = PlayerData.get(player)
	if res.ok and perfil then res.equipped = table.find(perfil.petsEquipados, id) ~= nil end
	return res
end

-- fusao de pet foi trocada pelo sistema de alimentar
R.FundirPet.OnServerInvoke = function()
	return { ok = false, msg = "Use Alimentar no inventario" }
end

R.EquiparMelhoresPets.OnServerInvoke = function(player)
	return PetService.equiparMelhores(player)
end

R.DesequiparPets.OnServerInvoke = function(player)
	return PetService.desequiparTodos(player)
end

-- o golpe vem do cliente agora, porque a Tool equipada engole o ClickDetector.
-- toda validacao continua no servidor: tipo, distancia, area e cooldown.
R.Golpear.OnServerEvent:Connect(function(player, rocha)
	if typeof(rocha) ~= "Instance" or not rocha:IsA("BasePart") then return end
	if rocha.Name ~= "Hitbox" then return end
	if not rocha:GetAttribute("HPMax") then return end
	if not rocha:IsDescendantOf(workspace) then return end
	Mineracao.golpear(player, rocha)
end)

R.RolarGacha.OnServerInvoke = function(player, areaId, mode, requestId)
 return GachaService.abrir(player,areaId,mode,requestId)
end
remoteNovo("ConcluirReveal","RemoteEvent").OnServerEvent:Connect(function(player,id) GachaService.apresentado(player,id) end)
local speedRate={}
remoteNovo("AtualizarVelocidade","RemoteFunction").OnServerInvoke=function(player,value)
 if os.clock()-(speedRate[player] or -math.huge)<.2 then return {ok=false,msg="Aguarde um instante."} end
 speedRate[player]=os.clock();return PlayerData.atualizarVelocidade(player,value)
end
Players.PlayerRemoving:Connect(function(p) speedRate[p]=nil end)

R.Vender.OnServerInvoke = function(player, mode)
	return IgnisService.vender(player, false, mode)
end

R.ComprarPicareta.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return IgnisService.comprarPicareta(player, id)
end

R.ComprarMochila.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return IgnisService.comprarMochila(player, id)
end

R.EquiparHat.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	local res = IgnisService.equipar(player, id)
	HatVisual.aplicar(player)
	return res
end

R.FundirHat.OnServerInvoke = function(player, id, lista)
	if type(id) ~= "string" or type(lista) ~= "table" or #lista > 300 then return { ok = false } end
	local res = IgnisService.fundir(player, id, lista)
	HatVisual.aplicar(player)
	return res
end

R.ResgatarCodigo.OnServerInvoke = function(player, texto)
	return Codigos.resgatar(player, texto)
end

R.EquiparMelhores.OnServerInvoke = function(player)
	local res = IgnisService.equiparMelhores(player)
	HatVisual.aplicar(player)
	return res
end

R.DesequiparTodos.OnServerInvoke = function(player)
	local res = IgnisService.desequiparTodos(player)
	HatVisual.aplicar(player)
	return res
end

-- ---------- TELEPORTE LOBBY <-> AREA ----------
local emCooldown = {}
Players.PlayerRemoving:Connect(function(player) emCooldown[player]=nil end)
local function teleportar(player, destino)
	if emCooldown[player] then return end
	emCooldown[player] = true
	IslandTravel.teleport(player, destino)
	task.delay(1.5, function() emCooldown[player] = nil end)
end

local function entradaDaArea(area)
 local model=workspace.Areas:FindFirstChild("Area"..area.id)
 return model and model:GetAttribute("EntryPosition") or area.centro+Vector3.new(0,6,-area.tamanho.Z/2+16)
end

-- Progression portals use the same server-owned unlocks as the lobby.
for _,pad in ipairs(workspace.Areas:GetDescendants()) do
 local id=pad:IsA("BasePart") and pad:GetAttribute("NextAreaId")
 local area=id and Config.areaPorId(id)
 if area then
  local pr=Instance.new("ProximityPrompt")
  pr.Name="ViajarArea" pr.ActionText="Viajar" pr.ObjectText=area.nome
  pr.MaxActivationDistance=12 pr.RequiresLineOfSight=false pr.Parent=pad
  pr.Triggered:Connect(function(player)
   local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
   if not root or (root.Position-pad.Position).Magnitude>16 then return end
   local perfil=PlayerData.get(player)
   if not perfil or not perfil.areas[id] then
    avisarBloqueada(player,area)
    return
   end
   teleportar(player,entradaDaArea(area))
  end)
 end
end

-- placas de volta pro lobby dentro das areas
for _, d in ipairs(workspace.Areas:GetDescendants()) do
	if d:IsA("BasePart") and d:GetAttribute("Destino") == "lobby" then
		d.Touched:Connect(function(hit)
			local p = Players:GetPlayerFromCharacter(hit.Parent)
			if p then teleportar(p, LOBBY) end
		end)
	end
end

-- prompt do Ignis abre a UI
local ignis = workspace.NPCs:WaitForChild("Ignis")
local corpo
for _, d in ipairs(ignis:GetDescendants()) do
	if d:IsA("BasePart") and d.Name == "belly" then corpo = d end
end
if corpo then
	local antigo = corpo:FindFirstChildOfClass("ProximityPrompt")
	if antigo then antigo:Destroy() end
	local pr = Instance.new("ProximityPrompt")
	pr.Name = "IgnisPrompt"
	pr.ActionText = "Falar"
	pr.ObjectText = "Ignis"
	pr.HoldDuration = 0
	pr.MaxActivationDistance = 18
	pr.RequiresLineOfSight = false
	pr.Parent = corpo
	pr.Triggered:Connect(function(player)
		if IgnisService.pertoDoIgnis(player) then R.AbrirIgnis:FireClient(player) end
	end)
end

-- pad da loja de mochilas
local loja = workspace:FindFirstChild("LojaMochilas")
	or workspace:FindFirstChild("backpack shop")
if loja then
	local pad = loja:FindFirstChild("PadLoja")
	if pad then
		local ultimo = {}
		pad.Touched:Connect(function(hit)
			local pl = Players:GetPlayerFromCharacter(hit.Parent)
			if not pl then return end
			if ultimo[pl] and os.clock() - ultimo[pl] < 1.5 then return end
			ultimo[pl] = os.clock()
			R.AbrirLoja:FireClient(pl)
		end)
		-- pulsa devagar pra chamar atencao
		task.spawn(function()
			local t = 0
			while pad.Parent do
				t += task.wait()
				pad.Transparency = 0.25 + 0.2 * math.sin(t * 2)
			end
		end)
	end
end

-- arcada do lobby: uma baia por area
-- liga os portais do lobby (montados no Edit, com atributo AreaId)
-- o Santuario pode estar solto no Workspace ou dentro de um modelo de lobby.
-- procura pelo nome em vez de assumir o caminho, assim desagrupar nao quebra nada.
local function acharSantuario()
	local direto = workspace:FindFirstChild("Santuario")
	if direto then return direto end
	for _, c in ipairs(workspace:GetChildren()) do
		local dentro = c:FindFirstChild("Santuario")
		if dentro then return dentro end
	end
	return nil
end
local sant = acharSantuario()
LOBBY = Vector3.new(0, 7, 66)

local ligados = 0
if not sant then warn("[Main] Santuario nao encontrado, viagem rapida desligada") end
for _, g in ipairs(sant and sant:GetDescendants() or {}) do
	local disco = g:IsA("Model") and g:FindFirstChild("Disco")
	if disco and disco:GetAttribute("AreaId") then
		local id = disco:GetAttribute("AreaId")
		local area = Config.areaPorId(id)
		if area then
			local destino = entradaDaArea(area)
			disco.CanTouch = true
			disco.Touched:Connect(function(hit)
				local pl = Players:GetPlayerFromCharacter(hit.Parent)
				if not pl then return end
				local perfil = PlayerData.get(pl)
				if not perfil or not perfil.areas[id] then
					avisarBloqueada(pl, area)
					return
				end
				teleportar(pl, destino)
			end)
			ligados += 1
		end
	end
end

-- maquinas de gacha: abrem por ProximityPrompt, igual o Ignis
local gachas = workspace:FindFirstChild("Gachas")
if gachas then
	for _, maq in ipairs(gachas:GetChildren()) do
		local pad = maq:FindFirstChild("PadGacha")
		local areaId = pad and pad:GetAttribute("AreaId")
		if pad and areaId then
			pad.CanTouch = false

			-- prompt fica no corpo da maquina, nao no pad do chao
			local corpoMaq
			for _, d in ipairs(maq:GetDescendants()) do
				if d:IsA("BasePart") and string.find(d.Name:lower(), "cabinet_body") then
					corpoMaq = d
					break
				end
			end
			corpoMaq = corpoMaq or pad

			local antigoPr = corpoMaq:FindFirstChildOfClass("ProximityPrompt")
			if antigoPr then antigoPr:Destroy() end

			local pr = Instance.new("ProximityPrompt")
			pr.Name = "GachaPrompt"
			pr.ActionText = "Invocar"
			pr.ObjectText = "Gacha"
			pr.HoldDuration = 0
			pr.MaxActivationDistance = 14
			pr.RequiresLineOfSight = false
			pr.Parent = corpoMaq
			pr.Triggered:Connect(function(pl)
				R.AbrirGacha:FireClient(pl, areaId)
			end)
			task.spawn(function()
				local t = 0
				while pad.Parent do
					t += task.wait()
					pad.Transparency = 0.3 + 0.2 * math.sin(t * 2.2)
				end
			end)
		end
	end
end

print("[Mineracao] servidor pronto - " .. #Config.Areas .. " areas construidas")

if RunService:IsStudio() then
	local dbg = remoteNovo("DebugV31", "RemoteFunction")
	dbg.OnServerInvoke = function(player, acao, a, b)
		local perfil = PlayerData.get(player)
		if not perfil then return { ok = false, msg = "sem perfil" } end
		if acao == "semSalvar" then
			-- sessao de teste: nada desta sessao vai para o DataStore
			perfil.__semSalvar = true
			return { ok = true }
		elseif acao == "modoTeste" then
			-- como semSalvar, mas o fluxo de compra roda inteiro (perfil de teste nunca vai para o DataStore)
			perfil.__semSalvar = nil
			perfil.__dev = true
			perfil.__devSalvar = false
			return { ok = true }
		elseif acao == "chefeVida" then
			for _, d in ipairs(workspace.Areas:GetDescendants()) do
				if d.Name == "Hitbox" and d:GetAttribute("Chefe") and (d:GetAttribute("HP") or 0) > 0 then
					d:SetAttribute("HP", math.max(1, d:GetAttribute("HPMax") * (tonumber(a) or 0.01)))
				end
			end
			return { ok = true }
		elseif acao == "perfilNovo" then
			-- zera o perfil EM MEMORIA (sem salvar) para testar o fluxo de conta nova
			local velho = perfil
			for k in pairs(velho) do if type(k) ~= "string" or k:sub(1, 2) ~= "__" then velho[k] = nil end end
			local novo = PlayerData.carregarVazio()
			for k, v in pairs(novo) do velho[k] = v end
			velho.__semSalvar = not velho.__dev
		elseif acao == "estado" then
			return { moeda = perfil.moeda, pity = perfil.pity, giros = perfil.giros, dano = PlayerData.dano(perfil),
				intervalo = PlayerData.intervalo(perfil), slots = PlayerData.slots(perfil), capHats = PlayerData.capacidadeHats(perfil),
				hats = PlayerData.totalHats(perfil), pets = PlayerData.totalPets(perfil), lb = PlayerData.levelBonus(perfil),
				daily = perfil.daily, tel = perfil.tel, recibos = perfil.recibos, compras = perfil.compras,
				boosts = perfil.boosts, minerados = perfil.minerados, index = perfil.index, exp = perfil.exp,
				equipados = #perfil.equipados, area = player:GetAttribute("CurrentAreaId"), mochila = PlayerData.itensNaMochila(perfil),
				capMochila = PlayerData.capacidade(perfil), dev = perfil.__dev }
		elseif acao == "tel" then
			local t = {}
			for _, e in ipairs(Telemetria.historico) do if e.user == player.UserId then table.insert(t, e.nome .. "|" .. tostring(e.valor) .. "|" .. tostring(e.extra)) end end
			return t
		elseif acao == "moedas" then
			perfil.moeda = tonumber(a) or 0
		elseif acao == "areas" then
			for i = 1, tonumber(a) or 1 do perfil.areas[i] = true end
		elseif acao == "chefe" then
			return { ok = BossService.nascer(player:GetAttribute("CurrentAreaId") or 1, "debug") }
		elseif acao == "recibo" then
			local Mon = require(RS.MonetizacaoConfig)
			local prod = Mon.produto(a)
			if not prod then return { ok = false, msg = "produto?" } end
			local idReal = prod.id
			if idReal <= 0 then prod.id = 999000 + #a end -- id temporario so para o teste
			local r1 = Produtos._processar({ PlayerId = player.UserId, ProductId = prod.id, PurchaseId = b, CurrencySpent = prod.robux })
			prod.id = idReal
			return { ok = true, decisao = r1.Name, moeda = perfil.moeda, compras = perfil.compras }
		elseif acao == "hats" then
			local Recompensas = require(script.Parent.Recompensas)
			for _ = 1, tonumber(a) or 1 do Recompensas.darHatAleatorio(player, perfil, "chakra", 1, "debug") end
		elseif acao == "gacha_sim" then
			local est = { giros = 0, pity = { l = 0, m = 0 } }
			local dist = Config.distGacha(tonumber(b) or 1, 1)
			local cont, maiorSemL, semL, primeiro = {}, 0, 0, nil
			for i = 1, tonumber(a) or 1000 do
				local r = GachaService.sortear(est, dist)
				if i == 1 then primeiro = r end
				cont[r] = (cont[r] or 0) + 1
				if r >= 5 then semL = 0 else semL += 1; maiorSemL = math.max(maiorSemL, semL) end
			end
			return { contagem = cont, maiorSemLendario = maiorSemL, primeiro = primeiro }
		elseif acao == "golpear" then
			if typeof(a) == "Instance" then Mineracao.golpear(player, a) end
			return { ok = true }
		elseif acao == "vender" then return IgnisService.vender(player)
		elseif acao == "comprarPicareta" then return IgnisService.comprarPicareta(player, a)
		elseif acao == "comprarMochila" then return IgnisService.comprarMochila(player, a)
		elseif acao == "comprarArea" then return Progresso.comprarArea(player, a)
		elseif acao == "gacha" then return GachaService.rolar(player, a)
		elseif acao == "daily" then return Retencao.resgatarDaily(player)
		elseif acao == "equiparMelhores" then return IgnisService.equiparMelhores(player)
		elseif acao == "fundirTudo" then
			local alvo = perfil.equipados[1]
			local lista = {}
			for uid in pairs(perfil.hatsInv) do if not table.find(perfil.equipados, uid) then table.insert(lista, uid) end end
			return alvo and IgnisService.fundir(player, alvo, lista) or { ok = false, msg = "sem alvo" }
		elseif acao == "missao" then return Progresso.resgatarMissao(player, a)
		elseif acao == "oferta" then Ofertas.mostrar(player, perfil, a, { contexto = "debug" })
		elseif acao == "tempo" then
			perfil.tempoJogado = (tonumber(a) or 0) * 60
		elseif acao == "salvar" then
			return { ok = PlayerData.salvar(player) }
		end
		PlayerData.sincronizar(player)
		return { ok = true }
	end
end

