-- TEMPORÁRIO: avaliar somente no Server de uma sessão Play do Studio.
-- Não instalar no Edit, publicar ou copiar para src. Nenhuma rotina chama o DataStore.
local Run = game:GetService("RunService")
assert(Run:IsStudio() and Run:IsServer(), "Fixture exige Server Play no Studio")
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Core = game:GetService("ServerScriptService"):WaitForChild("Core")
local PD = require(Core.PlayerData)
local Config = require(RS.Config)
local F = { events = {}, blockedSaves = 0, phase = "idle" }
local subject, original, cached, originalPivot, originalArea

local function copy(value, seen)
	if type(value) ~= "table" then return value end
	seen = seen or {}
	if seen[value] then return seen[value] end
	local result = {}
	seen[value] = result
	for key, item in pairs(value) do result[copy(key, seen)] = copy(item, seen) end
	return result
end
local function same(a, b)
	if type(a) ~= type(b) then return false end
	if type(a) ~= "table" then return a == b end
	for k, v in pairs(a) do
		if not (type(k) == "string" and k:sub(1, 2) == "__") and not same(v, b[k]) then return false end
	end
	for k in pairs(b) do
		if not (type(k) == "string" and k:sub(1, 2) == "__") and a[k] == nil then return false end
	end
	return true
end
local function assertSafe()
	assert(subject and subject.Parent == Players, "Jogador QA saiu")
	assert(PD.get(subject) == cached, "A tabela do cache foi substituída; interrompa o QA")
	assert(cached.__semSalvar == true and cached.__dev == true and cached.__devSalvar == false, "Guardas de persistência alteradas")
end
local function record(kind, name, value)
	table.insert(F.events, { kind = kind, name = name, value = value, at = os.clock() })
end
local function sync()
	assertSafe()
	PD.sincronizar(subject)
	require(Core.HatVisual).aplicar(subject)
end

function F.begin(player)
	assert(F.phase == "idle", "Fixture já iniciada")
	assert(#Players:GetPlayers() == 1, "Use sessão Play com um único jogador")
	assert(player and player.Parent == Players, "Jogador inválido")
	local profile = assert(PD.get(player), "Espere o perfil terminar de carregar")
	-- Até aqui: leitura e cópia, sem yields. A cópia não usa snapshot, que compartilha tabelas.
	original = copy(profile)
	subject, cached = player, profile
	originalArea = player:GetAttribute("CurrentAreaId")
	originalPivot = player.Character and player.Character:GetPivot()
	local save = PD.salvar
	PD.salvar = function(target, ...)
		if target == subject then F.blockedSaves += 1; return false end
		return save(target, ...)
	end
	-- A guarda da tabela também protege chamadas antigas que tenham capturado PD.salvar.
	cached.__semSalvar, cached.__dev, cached.__devSalvar = true, true, false
	local dev = Core:FindFirstChild("DevTest")
	if dev and dev:IsA("Script") then dev.Disabled = true end
	-- Telemetria existente chama AnalyticsService até no Studio. Para o alvo QA, manter só memória.
	local Tel = require(Core.Telemetria)
	local event, milestone, economy = Tel.evento, Tel.marco, Tel.economia
	Tel.evento = function(target, profileArg, name, value, details)
		if target == subject then record("event", name, value); return end
		return event(target, profileArg, name, value, details)
	end
	Tel.marco = function(target, profileArg, name, details)
		if target ~= subject then return milestone(target, profileArg, name, details) end
		if not profileArg or not profileArg.tel or profileArg.tel[name] then return false end
		profileArg.tel[name] = os.time()
		record("milestone", name, details)
		return true
	end
	Tel.economia = function(target, profileArg, source, amount, kind, item)
		if target == subject then record(source and "income" or "expense", item, amount); return end
		return economy(target, profileArg, source, amount, kind, item)
	end
	F.phase = "ready"
	assertSafe()
	return F.status()
end

function F.reset(phase)
	assert(F.phase ~= "restored", "Fim do QA: encerre Play")
	assertSafe()
	local fresh = PD.carregarVazio() -- função pura: não carrega nem grava uma conta
	fresh.__semSalvar, fresh.__dev, fresh.__devSalvar = true, true, false
	fresh.__player, fresh.__entrouEm, fresh.__UIV2QA = subject, os.clock(), true
	local ids = { pets = {}, hats = {} }
	if phase == "economy" then
		fresh.moeda = (Config.Picaretas[2].custo or 0) + (Config.Mochilas[2].custo or 0) + 1000
		local ore = Config.Areas[1].tema .. "_comum"
		assert(Config.infoMinerio(ore), "Minério da área 1 não encontrado")
		fresh.mochila[ore] = 3
	elseif phase == "inventory" then
		for i = 1, math.min(3, #Config.Pets) do table.insert(ids.pets, PD.novoPet(fresh, Config.Pets[i].id, 1)) end
		for i = 1, math.min(3, #Config.Hats) do table.insert(ids.hats, PD.novoHat(fresh, Config.Hats[i].id, 1)) end
	elseif phase == "gacha" then
		fresh.moeda = Config.Gachas[1].custo * 12
	elseif phase == "quests" then
		local quest = assert(Config.Missoes[1][1], "Missão da área 1 ausente")
		fresh.missoes[quest.id] = { p = quest.meta, r = false }
		ids.quest = quest.id
		ids.questReward = quest.premio
	elseif phase == "areas" then
		fresh.moeda = assert(Config.Areas[2], "Área 2 ausente").custo
	elseif phase ~= "mining" and phase ~= "empty" then
		error("Fase desconhecida: " .. tostring(phase))
	end
	-- Substitui os conteúdos, preservando a identidade da tabela conhecida por todos os serviços.
	-- Não há yields entre table.clear e recolocação dos dois bloqueios de persistência.
	table.clear(cached)
	for k, value in pairs(fresh) do cached[k] = value end
	F.phase = phase
	require(Core.GachaService).limpar(subject)
	sync()
	return { phase = phase, ids = ids, state = F.status() }
end

function F.profile()
	assertSafe()
	assert(F.phase ~= "restored", "Perfil original restaurado: não mutar")
	return cached
end
function F.status()
	assertSafe()
	return {
		phase = F.phase, userId = subject.UserId, semSalvar = cached.__semSalvar,
		dev = cached.__dev, devSalvar = cached.__devSalvar, blockedSaves = F.blockedSaves,
		moeda = cached.moeda, picareta = cached.picareta, mochilaTier = cached.mochilaTier,
		bagCount = PD.itensNaMochila(cached), pets = PD.totalPets(cached), hats = PD.totalHats(cached),
		giros = cached.giros, equippedPets = #cached.petsEquipados, equippedHats = #cached.equipados,
	}
end
function F.sync() sync(); return F.status() end
function F.assertSaveBlocked()
	assertSafe()
	assert(PD.salvar(subject) == false, "Salvar deveria estar bloqueado")
	return F.status()
end
function F.restore()
	assertSafe()
	-- Antes: fechar/cancelar invocação pelo Client. Esta barreira cancela mineração contínua.
	subject:SetAttribute("TravelTransition", true)
	local geometry = require(RS.MiningGeometry)
	task.wait(math.max(1, (geometry.ImpactTime or 0) + .25))
	assertSafe()
	table.clear(cached)
	for k, value in pairs(copy(original)) do cached[k] = value end
	-- Guardas permanecem até Stop Play. Nunca restaurar autorização para salvar nesta sessão.
	cached.__semSalvar, cached.__dev, cached.__devSalvar = true, true, false
	cached.__entrouEm = os.clock()
	F.phase = "restored"
	if originalArea ~= nil then subject:SetAttribute("CurrentAreaId", originalArea) end
	if originalPivot and subject.Character then subject.Character:PivotTo(originalPivot) end
	sync()
	local restored = same(cached, original)
	assert(restored, "Conteúdo persistível divergiu do backup")
	return { restored = restored, persistenceStillBlocked = PD.salvar(subject) == false, nextStep = "Stop Play" }
end

return F
