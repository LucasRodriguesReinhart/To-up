-- CraftService (ServerScriptService.Core) - ALQUIMIA da Ilha 3 (Shadow Garden): ingredientes da Masmorra -> pocoes.
-- Receitas sao DADOS (RS.AlquimiaConfig). Servidor autoritativo: o cliente so manda (receitaId, requestId).
--   Fabricar: trava por jogador + intervalo + requestId idempotente (mesmo padrao do GachaService), proximidade REAL
--   do caldeirao, area desbloqueada, cabe o resultado (stackMax) -> gasta TODOS os ingredientes de forma atomica ->
--   entrega o resultado. Nada no inventario paralelo: perfil.itens (PlayerData.darItem/gastarItens).
--   Usar: pocao = PlayerData.adicionarBoost (os boosts que o jogo ja tem: sorte, moedas).
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local Alq = require(RS:WaitForChild("AlquimiaConfig"))
local PlayerData = require(script.Parent.PlayerData)

local C = {}
local ocupado, ultimo, feitos = {}, {}, {}   -- [player] = bool / os.clock() / {[requestId] = resposta}
local area, estacao

local function remoto(nome, classe)
	local R = RS:WaitForChild("Remotes")
	local r = R:FindFirstChild(nome)
	if not r then r = Instance.new(classe); r.Name = nome; r.Parent = R end
	return r
end

local function perto(player)
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	return hrp and estacao and (hrp.Position - estacao).Magnitude <= Alq.CRAFT_ALCANCE
end

local function lembrar(player, requestId, res)
	local t = feitos[player] or {}
	feitos[player] = t
	t[requestId] = res
	t.__n = (t.__n or 0) + 1
	if t.__n > 40 then feitos[player] = { [requestId] = res, __n = 1 } end
	return res
end

function C.fabricar(player, receitaId, requestId)
	if type(receitaId) ~= "string" or #receitaId > 40 then return { ok = false, msg = "Receita invalida." } end
	if type(requestId) ~= "string" or #requestId < 8 or #requestId > 64 then return { ok = false, msg = "Pedido invalido." } end
	local ja = feitos[player] and feitos[player][requestId]
	if ja then return ja end                                      -- repeticao do MESMO pedido: mesma resposta
	if ocupado[player] then return { ok = false, msg = "Aguarde..." } end
	if ultimo[player] and os.clock() - ultimo[player] < Alq.CRAFT_INTERVALO then return { ok = false, msg = "Aguarde..." } end
	ocupado[player] = true
	local ok, res = pcall(function()
		local perfil = PlayerData.get(player)
		if not perfil then return { ok = false } end
		if not (area and perfil.areas[area.id]) then return { ok = false, msg = "Desbloqueie o " .. (area and area.nome or "Jardim das Sombras") .. " primeiro." } end
		if not perto(player) then return { ok = false, msg = "Va ate o caldeirao do alquimista." } end
		local r = Alq.receita(receitaId)
		local def = r and Alq.item(r.resultado)
		if not def then return { ok = false, msg = "Receita invalida." } end
		if not PlayerData.cabeItem(perfil, r.resultado, r.qtd) then return { ok = false, msg = "Voce ja tem o maximo de " .. def.nome .. "." } end
		if not PlayerData.gastarItens(perfil, r.ingredientes) then return { ok = false, msg = "Faltam ingredientes." } end
		PlayerData.darItem(perfil, r.resultado, r.qtd)
		PlayerData.sincronizar(player)
		task.spawn(PlayerData.salvar, player)
		return { ok = true, msg = "Voce criou: " .. def.nome .. "!", item = r.resultado, qtd = r.qtd }
	end)
	ocupado[player] = nil
	ultimo[player] = os.clock()
	if not ok then warn("[CraftService] " .. tostring(res)); res = { ok = false, msg = "Erro ao fabricar." } end
	if res.ok then lembrar(player, requestId, res) end
	return res
end

function C.usar(player, itemId)
	if type(itemId) ~= "string" or #itemId > 40 then return { ok = false } end
	if ocupado[player] then return { ok = false, msg = "Aguarde..." } end
	ocupado[player] = true
	local ok, res = pcall(function()
		local perfil = PlayerData.get(player)
		local def = Alq.item(itemId)
		if not perfil or not def or def.categoria ~= "pocao" or not def.efeitos then return { ok = false, msg = "Item invalido." } end
		if not PlayerData.gastarItens(perfil, { { itemId, 1 } }) then return { ok = false, msg = "Voce nao tem " .. def.nome .. "." } end
		for _, e in ipairs(def.efeitos) do PlayerData.adicionarBoost(perfil, e.boost, e.minutos) end
		PlayerData.sincronizar(player)
		return { ok = true, msg = def.nome .. " ativa!" }
	end)
	ocupado[player] = nil
	if not ok then warn("[CraftService] " .. tostring(res)); res = { ok = false, msg = "Erro ao usar." } end
	return res
end

function C.iniciar()
	for _, a in ipairs(Config.Areas) do if a.tema == "sombra" then area = a end end
	local areas = workspace:WaitForChild("Areas", 60)
	local mod = area and areas and areas:WaitForChild("Area" .. area.id, 60)
	local marcas = mod and mod:FindFirstChild("GAMEPLAY_MARKERS", true)
	local st = marcas and marcas:FindFirstChild("CRAFT_Station")
	local abrir = remoto("AbrirCraft", "RemoteEvent")
	remoto("FabricarItem", "RemoteFunction").OnServerInvoke = function(player, receitaId, requestId)
		return C.fabricar(player, receitaId, requestId)
	end
	remoto("UsarItem", "RemoteFunction").OnServerInvoke = function(player, itemId)
		return C.usar(player, itemId)
	end
	Players.PlayerRemoving:Connect(function(p) ocupado[p], ultimo[p], feitos[p] = nil, nil, nil end)
	if not st then warn("[CraftService] CRAFT_Station nao encontrado (Ilha 3 ainda nao montada?)") return false end
	estacao = st.Position
	-- prompt no caldeirao: abre a pagina de receitas no cliente
	local ancora = Instance.new("Part")
	ancora.Name = "AlquimiaEstacao"; ancora.Size = Vector3.new(5, 4, 5); ancora.Anchored = true; ancora.CanCollide = false
	ancora.CanQuery = false; ancora.CanTouch = false; ancora.Transparency = 1
	ancora.CFrame = CFrame.new(estacao + Vector3.new(0, 2.5, 0)); ancora.Parent = mod
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "AlquimiaPrompt"; pp.ActionText = "Alquimia"; pp.ObjectText = "Caldeirao"; pp.MaxActivationDistance = 10
	pp.RequiresLineOfSight = false; pp.Parent = ancora
	pp.Triggered:Connect(function(player) abrir:FireClient(player) end)
	return true
end

return C
