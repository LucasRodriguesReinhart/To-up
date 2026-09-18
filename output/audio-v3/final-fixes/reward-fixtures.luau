local SOURCES = {
SyncHeader = [====[function PlayerData.sincronizar(player, audioContext)
	local perfil = cache[player]
	if not perfil then return end
	perfil.__player = player
	if PlayerData.antesDeSincronizar then pcall(PlayerData.antesDeSincronizar, player, perfil) end
	local snap = PlayerData.snapshot(perfil)
	-- Transient delivery metadata: never stored in the profile or the DataStore.
	if audioContext == "daily" or audioContext == "code" then snap.audioContext = audioContext end
	snap.passes = Passes.todos(player)
	RS.Remotes.AtualizarDados:FireClient(player, snap)
end]====],
AchievementGate = [====[return function(transactionAudio) return not transactionAudio and "achievement" or false end]====],
RecompensasBefore = [====[-- Recompensas: unico lugar que entrega hats, pets e moedas (minerio, chefe, Daily, compras, codigos).
-- Garante as mesmas regras em todo lugar: inventario, Index, Level Bonus, anuncio de item novo e telemetria.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Economia = require(script.Parent.Economia)
local Telemetria = require(script.Parent.Telemetria)
local Ofertas = require(script.Parent.Ofertas)
local HatVisual = require(script.Parent.HatVisual)

local R = {}
local rnd = Random.new()

local function feedback(player, info)
	RS.Remotes.FeedbackMina:FireClient(player, info)
end

-- hats caem com nivel 1 + soma do Level Bonus dos pets equipados (limitado)
function R.nivelDrop(perfil)
	return math.min(Config.HAT_NIVEL_DROP_MAX, 1 + PlayerData.levelBonus(perfil))
end

function R.inventarioHatsCheio(player, perfil)
	if PlayerData.totalHats(perfil) < PlayerData.capacidadeHats(perfil) then return false end
	feedback(player, { tipo = "cheia", texto = "Inventário de hats cheio! Funda hats para liberar espaço." })
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.hat then -- 1 evento por sessao (senao cada drop perdido vira um evento)
		perfil.__invCheio.hat = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "hat", passe = PlayerData.capacidadeHats(perfil) > Config.INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "hat")
	return true
end

function R.inventarioPetsCheio(player, perfil)
	if PlayerData.totalPets(perfil) < PlayerData.capacidadePets(perfil) then return false end
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.pet then
		perfil.__invCheio.pet = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "pet", passe = PlayerData.capacidadePets(perfil) > Config.PET_INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "pet")
	return true
end

function R.darHat(player, perfil, def, origem)
	if not def or R.inventarioHatsCheio(player, perfil) then return nil end
	local novo = not perfil.index.hats[def.id]
	local uid = PlayerData.novoHat(perfil, def.id, R.nivelDrop(perfil))
	-- slot livre: equipa sozinho (o jogador sente o dano subir na hora)
	if #perfil.equipados < PlayerData.slots(perfil) then
		table.insert(perfil.equipados, uid)
		Telemetria.marco(player, perfil, "FirstHatEquipped", { manual = 0 })
		task.defer(HatVisual.aplicar, player)
	end
	feedback(player, { tipo = "hat", id = def.id, texto = def.nome, raridade = def.raridade, novo = novo, nivel = perfil.hatsInv[uid].nivel })
	if Config.RAR_INDICE[def.raridade] >= 5 then
		Telemetria.evento(player, perfil, "HatDropped", Config.RAR_INDICE[def.raridade], { raridade = def.raridade, mundo = def.mundo, origem = origem or "" })
	end
	return uid
end

-- raridade sorteada com a regra do simulador: Lucky/boost exatos em Epico+, depois sorte do tipo de minerio
function R.sortearRaridadeHat(player, perfil, sorteTipo)
	local dist = Config.aplicarLucky(Config.Eco.RAR_DIST, Economia.luckyMult(player, perfil))
	dist = Config.normalizarSorte(dist, sorteTipo)
	return Config.RAR_IDS[Config.sortearIndice(rnd, dist)]
end

function R.darHatAleatorio(player, perfil, tema, sorteTipo, origem)
	local raridade = R.sortearRaridadeHat(player, perfil, sorteTipo)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

function R.darHatDaRaridade(player, perfil, tema, raridade, origem)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

-- pet de uma raridade na area (area sem gacha usa a anterior; raridade sem pet cai para a de baixo)
function R.darPetDaRaridade(player, perfil, areaId, raridade, origem)
	while areaId > 1 and not Config.Gachas[areaId] do areaId -= 1 end
	if R.inventarioPetsCheio(player, perfil) then
		feedback(player, { tipo = "cheia", texto = "Inventário de pets cheio! Alimente pets para liberar espaço." })
		return nil
	end
	local r = Config.RAR_INDICE[raridade] or 1
	local lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	while #lista == 0 and r > 1 do
		r -= 1
		lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	end
	local def = lista[rnd:NextInteger(1, math.max(1, #lista))]
	if not def then return nil end
	local novo = not perfil.index.pets[def.id]
	local uid = PlayerData.novoPet(perfil, def.id, 1)
	if novo and #perfil.petsEquipados < PlayerData.slotsPets(perfil) then
		table.insert(perfil.petsEquipados, uid)
	end
	Telemetria.marco(player, perfil, "FirstPet", { origem = origem or "" })
	return uid, def, novo
end

function R.darMoedas(player, perfil, qtd, tipoTransacao, item)
	qtd = math.floor(qtd)
	if qtd <= 0 then return 0 end
	perfil.moeda += qtd
	Telemetria.economia(player, perfil, true, qtd, tipoTransacao, item)
	return qtd
end

return R

]====],
RecompensasAfter = [====[-- Recompensas: unico lugar que entrega hats, pets e moedas (minerio, chefe, Daily, compras, codigos).
-- Garante as mesmas regras em todo lugar: inventario, Index, Level Bonus, anuncio de item novo e telemetria.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Economia = require(script.Parent.Economia)
local Telemetria = require(script.Parent.Telemetria)
local Ofertas = require(script.Parent.Ofertas)
local HatVisual = require(script.Parent.HatVisual)

local R = {}
local rnd = Random.new()

local function feedback(player, info)
	RS.Remotes.FeedbackMina:FireClient(player, info)
end

-- hats caem com nivel 1 + soma do Level Bonus dos pets equipados (limitado)
function R.nivelDrop(perfil)
	return math.min(Config.HAT_NIVEL_DROP_MAX, 1 + PlayerData.levelBonus(perfil))
end

function R.inventarioHatsCheio(player, perfil)
	if PlayerData.totalHats(perfil) < PlayerData.capacidadeHats(perfil) then return false end
	feedback(player, { tipo = "cheia", texto = "Inventário de hats cheio! Funda hats para liberar espaço." })
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.hat then -- 1 evento por sessao (senao cada drop perdido vira um evento)
		perfil.__invCheio.hat = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "hat", passe = PlayerData.capacidadeHats(perfil) > Config.INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "hat")
	return true
end

function R.inventarioPetsCheio(player, perfil)
	if PlayerData.totalPets(perfil) < PlayerData.capacidadePets(perfil) then return false end
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.pet then
		perfil.__invCheio.pet = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "pet", passe = PlayerData.capacidadePets(perfil) > Config.PET_INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "pet")
	return true
end

function R.darHat(player, perfil, def, origem)
	if not def or R.inventarioHatsCheio(player, perfil) then return nil end
	local novo = not perfil.index.hats[def.id]
	local uid = PlayerData.novoHat(perfil, def.id, R.nivelDrop(perfil))
	-- slot livre: equipa sozinho (o jogador sente o dano subir na hora)
	if #perfil.equipados < PlayerData.slots(perfil) then
		table.insert(perfil.equipados, uid)
		Telemetria.marco(player, perfil, "FirstHatEquipped", { manual = 0 })
		task.defer(HatVisual.aplicar, player)
	end
	feedback(player, { tipo = "hat", id = def.id, texto = def.nome, raridade = def.raridade, novo = novo, nivel = perfil.hatsInv[uid].nivel, audioContext = origem })
	if Config.RAR_INDICE[def.raridade] >= 5 then
		Telemetria.evento(player, perfil, "HatDropped", Config.RAR_INDICE[def.raridade], { raridade = def.raridade, mundo = def.mundo, origem = origem or "" })
	end
	return uid, def -- additive metadata: the exact definition delivered, including fallbacks
end

-- raridade sorteada com a regra do simulador: Lucky/boost exatos em Epico+, depois sorte do tipo de minerio
function R.sortearRaridadeHat(player, perfil, sorteTipo)
	local dist = Config.aplicarLucky(Config.Eco.RAR_DIST, Economia.luckyMult(player, perfil))
	dist = Config.normalizarSorte(dist, sorteTipo)
	return Config.RAR_IDS[Config.sortearIndice(rnd, dist)]
end

function R.darHatAleatorio(player, perfil, tema, sorteTipo, origem)
	local raridade = R.sortearRaridadeHat(player, perfil, sorteTipo)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

function R.darHatDaRaridade(player, perfil, tema, raridade, origem)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

-- pet de uma raridade na area (area sem gacha usa a anterior; raridade sem pet cai para a de baixo)
function R.darPetDaRaridade(player, perfil, areaId, raridade, origem)
	while areaId > 1 and not Config.Gachas[areaId] do areaId -= 1 end
	if R.inventarioPetsCheio(player, perfil) then
		feedback(player, { tipo = "cheia", texto = "Inventário de pets cheio! Alimente pets para liberar espaço." })
		return nil
	end
	local r = Config.RAR_INDICE[raridade] or 1
	local lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	while #lista == 0 and r > 1 do
		r -= 1
		lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	end
	local def = lista[rnd:NextInteger(1, math.max(1, #lista))]
	if not def then return nil end
	local novo = not perfil.index.pets[def.id]
	local uid = PlayerData.novoPet(perfil, def.id, 1)
	if novo and #perfil.petsEquipados < PlayerData.slotsPets(perfil) then
		table.insert(perfil.petsEquipados, uid)
	end
	Telemetria.marco(player, perfil, "FirstPet", { origem = origem or "" })
	return uid, def, novo
end

function R.darMoedas(player, perfil, qtd, tipoTransacao, item)
	qtd = math.floor(qtd)
	if qtd <= 0 then return 0 end
	perfil.moeda += qtd
	Telemetria.economia(player, perfil, true, qtd, tipoTransacao, item)
	return qtd
end

return R

]====],
RetencaoBefore = [====[-- Retencao P0: Daily basico (ciclo de 7 dias sem perda) e Index (colecao de pets e hats).
-- Index nao da poder (economia congelada): so marca a colecao e aparece na UI.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)

local Ret = {}
local ocupado = {}

function Ret.resgatarDaily(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if ocupado[player] then return { ok = false, msg = "Aguarde..." } end
	local hoje = PlayerData.diaUTC()
	if (perfil.daily.ultimo or 0) >= hoje then
		return { ok = false, msg = "Volte amanha para a proxima recompensa" }
	end
	ocupado[player] = true
	local dia = math.clamp(perfil.daily.dia or 1, 1, #Config.DAILY)
	local def = Config.DAILY[dia]
	-- marca ANTES de entregar: nenhuma falha no meio permite resgatar duas vezes
	perfil.daily.ultimo = hoje
	perfil.daily.dia = dia % #Config.DAILY + 1
	local area = PlayerData.maiorArea(perfil)
	local tema = Config.Areas[area].tema
	local partes = {}
	for _, item in ipairs(def.itens) do
		if item.tipo == "moedas" then
			-- limite do GDD: Daily + missoes cabem em RENDA_EXTRA (metade para cada) da renda do mundo.
			-- sem isso, 10 min de renda no M1 (mundo de ~15 min) pagaria o portal inteiro.
			local eco = Config.Eco
			local teto = (eco.RENDA_EXTRA - 1) / 2 * eco.MINUTOS_NO_MUNDO_MEDIO[area] * eco.MOEDAS_POR_MINUTO_MEDIO[area]
			local q = Recompensas.darMoedas(player, perfil, math.min(Config.moedasDeMinutos(area, item.minutos), teto), "TimedReward", "daily" .. dia)
			table.insert(partes, Config.formatar(q) .. " moedas")
		elseif item.tipo == "boost" then
			PlayerData.adicionarBoost(perfil, item.boost, item.minutos)
			table.insert(partes, (item.boost == "sorte" and "Sorte " or "Moedas x2 ") .. item.minutos .. " min")
		elseif item.tipo == "hats" then
			local dados = 0
			for _ = 1, item.qtd do
				if Recompensas.darHatDaRaridade(player, perfil, tema, item.raridade, "daily") then dados += 1 end
			end
			table.insert(partes, dados .. " hat(s) " .. (Config.Raridades[item.raridade] and Config.Raridades[item.raridade].nome or item.raridade))
		elseif item.tipo == "pet" then
			local _, pdef = Recompensas.darPetDaRaridade(player, perfil, area, item.raridade, "daily")
			if pdef then table.insert(partes, pdef.nome) end
		end
	end
	Telemetria.evento(player, perfil, "DailyClaimed", dia)
	PlayerData.sincronizar(player)
	task.spawn(PlayerData.salvar, player)
	ocupado[player] = nil
	return { ok = true, msg = "Dia " .. dia .. ": " .. table.concat(partes, " + "), dia = dia }
end

-- resumo da colecao por area (para a UI)
function Ret.progressoIndex(perfil)
	local pets, hats = 0, 0
	for _ in pairs(perfil.index.pets) do pets += 1 end
	for _ in pairs(perfil.index.hats) do hats += 1 end
	return { pets = pets, petsTotal = #Config.Pets, hats = hats, hatsTotal = #Config.Hats }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ocupado[p] = nil end)

return Ret

]====],
RetencaoAfter = [====[-- Retencao P0: Daily basico (ciclo de 7 dias sem perda) e Index (colecao de pets e hats).
-- Index nao da poder (economia congelada): so marca a colecao e aparece na UI.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)

local Ret = {}
local ocupado = {}

function Ret.resgatarDaily(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if ocupado[player] then return { ok = false, msg = "Aguarde..." } end
	local hoje = PlayerData.diaUTC()
	if (perfil.daily.ultimo or 0) >= hoje then
		return { ok = false, msg = "Volte amanha para a proxima recompensa" }
	end
	ocupado[player] = true
	local dia = math.clamp(perfil.daily.dia or 1, 1, #Config.DAILY)
	local def = Config.DAILY[dia]
	-- marca ANTES de entregar: nenhuma falha no meio permite resgatar duas vezes
	perfil.daily.ultimo = hoje
	perfil.daily.dia = dia % #Config.DAILY + 1
	local area = PlayerData.maiorArea(perfil)
	local tema = Config.Areas[area].tema
	local partes = {}
	local audioReward = { moedas = 0, boost = false }
	local function deliveredRarity(rarity)
		if (Config.RAR_INDICE[rarity] or 0) > (Config.RAR_INDICE[audioReward.raridade] or 0) then audioReward.raridade = rarity end
	end
	for _, item in ipairs(def.itens) do
		if item.tipo == "moedas" then
			-- limite do GDD: Daily + missoes cabem em RENDA_EXTRA (metade para cada) da renda do mundo.
			-- sem isso, 10 min de renda no M1 (mundo de ~15 min) pagaria o portal inteiro.
			local eco = Config.Eco
			local teto = (eco.RENDA_EXTRA - 1) / 2 * eco.MINUTOS_NO_MUNDO_MEDIO[area] * eco.MOEDAS_POR_MINUTO_MEDIO[area]
			local q = Recompensas.darMoedas(player, perfil, math.min(Config.moedasDeMinutos(area, item.minutos), teto), "TimedReward", "daily" .. dia)
			audioReward.moedas += q
			table.insert(partes, Config.formatar(q) .. " moedas")
		elseif item.tipo == "boost" then
			PlayerData.adicionarBoost(perfil, item.boost, item.minutos)
			audioReward.boost = true
			table.insert(partes, (item.boost == "sorte" and "Sorte " or "Moedas x2 ") .. item.minutos .. " min")
		elseif item.tipo == "hats" then
			local dados = 0
			for _ = 1, item.qtd do
				local uid, delivered = Recompensas.darHatDaRaridade(player, perfil, tema, item.raridade, "daily")
				if uid then
					dados += 1
					if delivered then deliveredRarity(delivered.raridade) end
				end
			end
			table.insert(partes, dados .. " hat(s) " .. (Config.Raridades[item.raridade] and Config.Raridades[item.raridade].nome or item.raridade))
		elseif item.tipo == "pet" then
			local _, pdef = Recompensas.darPetDaRaridade(player, perfil, area, item.raridade, "daily")
			if pdef then deliveredRarity(pdef.raridade); table.insert(partes, pdef.nome) end
		end
	end
	Telemetria.evento(player, perfil, "DailyClaimed", dia)
	PlayerData.sincronizar(player, "daily")
	task.spawn(PlayerData.salvar, player)
	ocupado[player] = nil
	return { ok = true, msg = "Dia " .. dia .. ": " .. table.concat(partes, " + "), dia = dia, audioReward = audioReward }
end

-- resumo da colecao por area (para a UI)
function Ret.progressoIndex(perfil)
	local pets, hats = 0, 0
	for _ in pairs(perfil.index.pets) do pets += 1 end
	for _ in pairs(perfil.index.hats) do hats += 1 end
	return { pets = pets, petsTotal = #Config.Pets, hats = hats, hatsTotal = #Config.Hats }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ocupado[p] = nil end)

return Ret

]====],
CodigosBefore = [====[-- CODIGOS: fica no servidor pra ninguem ver a lista pelo cliente.
-- Pra criar um codigo novo, adicione uma linha em CODIGOS (em MAIUSCULO).
--   moeda  = moedas que o jogador ganha
--   pet    = id de um pet de Config.Pets (opcional)
--   hat    = id de um hat de Config.Hats (opcional)
--   ativo  = false pra desligar sem apagar
-- Cada jogador so resgata cada codigo uma vez.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local CODIGOS = {
	LANCAMENTO = { moeda = 100, ativo = true },  -- ~5 min de jogo no inicio
	BEMVINDO   = { moeda = 50, hat = "chakra_106490972825856", ativo = true }, -- Kakashi (raro)
	NARUTO     = { pet = "naruto", ativo = true },
}

local Codigos = {}
local ultimo = {}

function Codigos.resgatar(player, texto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(texto) ~= "string" then return { ok = false } end
	local agora = os.clock()
	if ultimo[player] and agora - ultimo[player] < 1.5 then return { ok = false, msg = "Aguarde um pouco" } end
	ultimo[player] = agora

	local codigo = texto:upper():gsub("%s+", "")
	local c = CODIGOS[codigo]
	if not c or c.ativo == false then return { ok = false, msg = "Codigo invalido ou expirado" } end
	perfil.codigos = perfil.codigos or {}
	if perfil.codigos[codigo] then return { ok = false, msg = "Voce ja usou esse codigo" } end

	local partes = {}
	if c.hat and Config.hatPorId(c.hat) then
		if PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil) then
			return { ok = false, msg = "Inventário de hats cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoHat(perfil, c.hat, 1)
		table.insert(partes, Config.hatPorId(c.hat).nome)
	end
	if c.pet and Config.petPorId(c.pet) then
		if PlayerData.totalPets(perfil) >= PlayerData.capacidadePets(perfil) then
			return { ok = false, msg = "Inventário de pets cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoPet(perfil, c.pet, 1)
		table.insert(partes, Config.petPorId(c.pet).nome)
	end
	if c.moeda and c.moeda > 0 then
		perfil.moeda += c.moeda
		table.insert(partes, Config.formatar(c.moeda) .. " moedas")
	end
	perfil.codigos[codigo] = true
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Codigo resgatado: " .. table.concat(partes, " + ") }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ultimo[p] = nil end)

return Codigos

]====],
CodigosAfter = [====[-- CODIGOS: fica no servidor pra ninguem ver a lista pelo cliente.
-- Pra criar um codigo novo, adicione uma linha em CODIGOS (em MAIUSCULO).
--   moeda  = moedas que o jogador ganha
--   pet    = id de um pet de Config.Pets (opcional)
--   hat    = id de um hat de Config.Hats (opcional)
--   ativo  = false pra desligar sem apagar
-- Cada jogador so resgata cada codigo uma vez.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local CODIGOS = {
	LANCAMENTO = { moeda = 100, ativo = true },  -- ~5 min de jogo no inicio
	BEMVINDO   = { moeda = 50, hat = "chakra_106490972825856", ativo = true }, -- Kakashi (raro)
	NARUTO     = { pet = "naruto", ativo = true },
}

local Codigos = {}
local ultimo = {}

function Codigos.resgatar(player, texto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(texto) ~= "string" then return { ok = false } end
	local agora = os.clock()
	if ultimo[player] and agora - ultimo[player] < 1.5 then return { ok = false, msg = "Aguarde um pouco" } end
	ultimo[player] = agora

	local codigo = texto:upper():gsub("%s+", "")
	local c = CODIGOS[codigo]
	if not c or c.ativo == false then return { ok = false, msg = "Codigo invalido ou expirado" } end
	perfil.codigos = perfil.codigos or {}
	if perfil.codigos[codigo] then return { ok = false, msg = "Voce ja usou esse codigo" } end

	local partes = {}
	local audioReward = { moedas = 0, boost = false }
	local function deliveredRarity(rarity)
		if (Config.RAR_INDICE[rarity] or 0) > (Config.RAR_INDICE[audioReward.raridade] or 0) then audioReward.raridade = rarity end
	end
	if c.hat and Config.hatPorId(c.hat) then
		if PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil) then
			return { ok = false, msg = "Inventário de hats cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoHat(perfil, c.hat, 1)
		deliveredRarity(Config.hatPorId(c.hat).raridade)
		table.insert(partes, Config.hatPorId(c.hat).nome)
	end
	if c.pet and Config.petPorId(c.pet) then
		if PlayerData.totalPets(perfil) >= PlayerData.capacidadePets(perfil) then
			return { ok = false, msg = "Inventário de pets cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoPet(perfil, c.pet, 1)
		deliveredRarity(Config.petPorId(c.pet).raridade)
		table.insert(partes, Config.petPorId(c.pet).nome)
	end
	if c.moeda and c.moeda > 0 then
		perfil.moeda += c.moeda
		audioReward.moedas += c.moeda
		table.insert(partes, Config.formatar(c.moeda) .. " moedas")
	end
	perfil.codigos[codigo] = true
	PlayerData.sincronizar(player, "code")
	return { ok = true, msg = "Codigo resgatado: " .. table.concat(partes, " + "), audioReward = audioReward }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ultimo[p] = nil end)

return Codigos

]====],
Preferences = [====[-- Shared, pure audio preference schema. No settings outside this whitelist are persisted.
local AudioPreferences = {}

AudioPreferences.defaults = table.freeze({
	AudioMasterVolume = .8,
	AudioMusicVolume = .6,
	AudioSFXVolume = .85,
	AudioUIVolume = .65,
	AudioAmbienceVolume = .55,
	MusicEnabled = true,
	SomMineracaoEnabled = true,
	SomInterfaceEnabled = true,
})

function AudioPreferences.value(key, value)
	local default = AudioPreferences.defaults[key]
	if default == nil then return nil end
	if type(default) == "boolean" then
		if type(value) == "boolean" then return value end
		return nil
	end
	if type(value) ~= "number" or value ~= value or value == math.huge or value == -math.huge then return nil end
	return math.round(math.clamp(value, 0, 1) * 100) / 100
end

function AudioPreferences.sanitize(input, base)
	local result = {}
	input = type(input) == "table" and input or {}
	base = type(base) == "table" and base or {}
	for key, default in pairs(AudioPreferences.defaults) do
		local value = AudioPreferences.value(key, input[key])
		if value == nil then value = AudioPreferences.value(key, base[key]) end
		if value == nil then value = default end
		result[key] = value
	end
	return result
end

function AudioPreferences.apply(player, preferences)
	for key, value in pairs(AudioPreferences.sanitize(preferences)) do
		player:SetAttribute(key, value)
	end
end

return table.freeze(AudioPreferences)
]====],
UpdateAudio = [====[function PlayerData.atualizarAudio(player, patch)
	local perfil = cache[player]
	if not perfil then return { ok = false, carregando = true } end
	if type(patch) ~= "table" then return { ok = false } end
	-- Bounded whitelist traversal; nested values and unknown fields never enter the save.
	perfil.audio = AudioPreferences.sanitize(patch, perfil.audio)
	-- Client owns immediate mix attributes; server replication would roll back newer local edits.
	return { ok = true, audio = table.clone(perfil.audio), persistent = PlayerData.audioPersistente(perfil) }
end

]====],
ChooseCue = [====[return function(res, Som, Config)
		-- One cue for what the server actually delivered; never infer rarity from the offer.
		local reward = res.audioReward
		if type(reward) ~= "table" then Som.tocar("reward_banner") -- compatible with an older server
		elseif type(reward.raridade) == "string" and Config.Raridades[reward.raridade] then Som.drop(reward.raridade)
		elseif reward.boost == true then Som.tocar("boost")
		elseif type(reward.moedas) == "number" and reward.moedas > 0 then Som.tocar("reward_banner") end
end]====],
BoostGate = [====[return function(data, previous, previousClock, ctx, Som)
	local transactionAudio = data.audioContext == "daily" or data.audioContext == "code"
	if not transactionAudio and previous and previous.boosts and data.boosts then
		local elapsed = ctx.dataClock - (previousClock or ctx.dataClock)
		for _, key in ipairs({ "sorte", "moedas" }) do
			local before = math.max(0, (previous.boosts[key] or 0) - elapsed)
			if (data.boosts[key] or 0) > before + 5 then Som.tocar("boost"); break end
		end
	end
end]====],
HatGate = [====[return function(info, Som)
  if info.audioContext~="daily" and info.audioContext~="code" then Som.drop(info.raridade) end
end]====],
}

-- No Roblox services, remotes, datastore, or live transactions. Original and revised
-- source run against identical fresh profiles and a deterministic Random.new stub.
local function deep(value)
	if type(value) ~= "table" then return value end
	local result = {}
	for key, item in pairs(value) do result[key] = deep(item) end
	return result
end
local function canonical(value)
	if type(value) ~= "table" then return tostring(value) end
	local keys = {}
	for key in pairs(value) do table.insert(keys, key) end
	table.sort(keys, function(a,b) return tostring(a)<tostring(b) end)
	local out = {}
	for _, key in ipairs(keys) do table.insert(out,tostring(key).."="..canonical(value[key])) end
	return "{"..table.concat(out,",").."}"
end
local function compile(source, name, env)
	local chunk, err = loadstring(source, name)
	assert(chunk, err)
	setfenv(chunk, setmetatable(env or {}, { __index = getfenv() }))
	return chunk()
end

local scenarios = {
	{ name="daily2",day=2,event="drop_raro" },
	{ name="daily5",day=5,event="drop_raro" },
	{ name="daily7",day=7,event="drop_epico" },
	{ name="daily3_multi_hat",day=3,event="drop_raro" },
	{ name="daily7_fallback",day=7,fallback=true,event="drop_raro" },
	{ name="daily7_inventory_full",day=7,full=true,event="none" },
	{ name="daily2_inventory_full",day=2,full=true,event="boost" },
	{ name="code_coins",code="LANCAMENTO",event="reward_banner" },
	{ name="code_hat",code="BEMVINDO",event="drop_raro" },
	{ name="code_pet",code="NARUTO",event="drop_raro" },
	{ name="code_full",code="NARUTO",full=true,event="none" },
	{ name="code_invalid",code="INVALID",event="none" },
	{ name="code_duplicate",code="LANCAMENTO",duplicate=true,event="none" },
}
local function world(scenario, revised)
	local profile = { moeda=1000,hatsInv={},petsInv={},hatSeq=0,petSeq=0,equipados={},petsEquipados={},index={hats={},pets={}},
		daily={dia=scenario.day or 1,ultimo=0},boosts={sorte=0,moedas=0},codigos={},tel={},__invCheio={} }
	if scenario.duplicate then profile.codigos[scenario.code]=true end
	local captures={feedback={},sync={},telemetry={},random={},saveRequests=0}
	local player={Name="OfflineFixture",UserId=0}
	local hats={
		chakra_106490972825856={id="chakra_106490972825856",nome="Rare hat",raridade="raro",mundo=1},
		epic_hat={id="epic_hat",nome="Epic hat",raridade="epico",mundo=1},
	}
	local pets={naruto={id="naruto",nome="Rare pet",raridade="raro"},epic_pet={id="epic_pet",nome="Epic pet",raridade="epico"}}
	local Config={
		RAR_INDICE={comum=1,incomum=2,raro=3,epico=4,lendario=5,mitico=6,secreto=7},
		RAR_IDS={"comum","incomum","raro","epico","lendario","mitico","secreto"},
		HAT_NIVEL_DROP_MAX=20,INVENTARIO_MAX=50,PET_INVENTARIO_MAX=50,
		Gachas={[1]={}},Areas={{tema="chakra"}},Eco={RENDA_EXTRA=1.1,MINUTOS_NO_MUNDO_MEDIO={10},MOEDAS_POR_MINUTO_MEDIO={100}},
		DAILY={
			{itens={{tipo="moedas",minutos=10}}},
			{itens={{tipo="boost",boost="sorte",minutos=15},{tipo="moedas",minutos=10},{tipo="pet",raridade="raro"}}},
			{itens={{tipo="hats",raridade="raro",qtd=3}}},
			{itens={{tipo="moedas",minutos=20}}},
			{itens={{tipo="boost",boost="moedas",minutos=15},{tipo="hats",raridade="raro",qtd=1}}},
			{itens={{tipo="hats",raridade="epico",qtd=1}}},
			{itens={{tipo="pet",raridade="epico"}}},
		},
	}
	Config.Raridades={}
	for key in pairs(Config.RAR_INDICE) do Config.Raridades[key]={nome=key} end
	Config.hatPorId=function(id) return hats[id] end
	Config.petPorId=function(id) return pets[id] end
	Config.formatar=tostring
	Config.moedasDeMinutos=function(_,minutes) return minutes*100 end
	Config.hatsDoTema=function(_,rarity) return {rarity=="epico" and hats.epic_hat or hats.chakra_106490972825856} end
	Config.petsDaRaridade=function(rarity)
		if rarity=="epico" then return scenario.fallback and {} or {pets.epic_pet} end
		return {pets.naruto}
	end
	local PD={get=function()return profile end,diaUTC=function()return 100 end,maiorArea=function()return 1 end,
		levelBonus=function()return 0 end,slots=function()return 3 end,slotsPets=function()return 3 end,
		capacidadeHats=function()return scenario.full and 0 or 50 end,capacidadePets=function()return scenario.full and 0 or 50 end,
		adicionarBoost=function(p,kind,minutes) p.boosts[kind]=math.max(p.boosts[kind],5000)+minutes*60 end,
	}
	local function count(items) local n=0 for _ in pairs(items) do n+=1 end return n end
	PD.totalHats=function(p)return count(p.hatsInv)end
	PD.totalPets=function(p)return count(p.petsInv)end
	PD.novoHat=function(p,id,level) p.hatSeq+=1;local uid="h"..p.hatSeq;p.hatsInv[uid]={id=id,nivel=level};p.index.hats[id]=true;return uid end
	PD.novoPet=function(p,id,level) p.petSeq+=1;local uid="p"..p.petSeq;p.petsInv[uid]={id=id,nivel=level};p.index.pets[id]=true;return uid end
	PD.sincronizar=function(_,context) table.insert(captures.sync,{profile=deep(profile),audioContext=context}) end
	PD.salvar=function()captures.saveRequests+=1;return true end
	local function log(kind,...)table.insert(captures.telemetry,{kind=kind,args=table.pack(...)})end
	local Telemetria={evento=function(_,_,...)log("evento",...)end,marco=function(_,_,...)log("marco",...)end,economia=function(_,_,...)log("economia",...)end}
	local services={Config=Config,PlayerData=PD,Economia={},Telemetria=Telemetria,Ofertas={inventarioCheio=function()end},HatVisual={aplicar=function()end}}
	local parent={}
	for _,name in ipairs({"PlayerData","Economia","Telemetria","Ofertas","HatVisual","Recompensas"})do parent[name]=name end
	local RS={Config="Config",Remotes={FeedbackMina={FireClient=function(_,_,info)table.insert(captures.feedback,deep(info))end}}}
	local env={game={GetService=function(_,service)
		assert(service=="ReplicatedStorage" or service=="Players","REAL SERVICE FORBIDDEN: "..service)
		if service=="ReplicatedStorage"then return RS end
		return {PlayerRemoving={Connect=function()end}}
	end},script={Parent=parent},require=function(name)assert(services[name],name);return services[name]end,
		Random={new=function()return {NextInteger=function(_,a,b)table.insert(captures.random,{a,b});return a end}end},
		task={spawn=function(fn,...)fn(...)end,defer=function(fn,...)fn(...)end},os={time=function()return 5000 end,clock=function()return 100 end}}
	local suffix=revised and "After" or "Before"
	services.Recompensas=compile(SOURCES["Recompensas"..suffix],"Recompensas"..suffix,env)
	local moduleName=scenario.day and "Retencao" or "Codigos"
	local module=compile(SOURCES[moduleName..suffix],moduleName..suffix,env)
	local result=scenario.day and module.resgatarDaily(player) or module.resgatar(player,scenario.code)
	return {profile=profile,captures=captures,result=result,config=Config}
end

local choose=compile(SOURCES.ChooseCue,"actual-client-cue")
local boostGate=compile(SOURCES.BoostGate,"actual-client-boost-gate")
local hatGate=compile(SOURCES.HatGate,"actual-mining-hat-gate")
local function gameplay(world)
	local copy={profile=deep(world.profile),captures=deep(world.captures),result=deep(world.result)}
	copy.result.audioReward=nil
	for _,f in ipairs(copy.captures.feedback)do f.audioContext=nil end
	for _,sync in ipairs(copy.captures.sync)do sync.audioContext=nil end
	return canonical(copy)
end
for _,scenario in ipairs(scenarios) do
	local original,revised=world(scenario,false),world(scenario,true)
	assert(gameplay(original)==gameplay(revised),"Gameplay changed: "..scenario.name)
	assert(revised.profile.audioContext==nil and revised.profile.audioReward==nil,"Metadata persisted in profile")
	local played={}
	local sound={tocar=function(event)table.insert(played,event)end,drop=function(rarity)table.insert(played,"drop_"..rarity)end}
	for _,feedback in ipairs(revised.captures.feedback)do if feedback.tipo=="hat"then hatGate(feedback,sound)end end
	for _,snap in ipairs(revised.captures.sync)do
		boostGate({audioContext=snap.audioContext,boosts=snap.profile.boosts},{boosts={sorte=0,moedas=0}},98,{dataClock=100},sound)
	end
	if revised.result.ok then choose(revised.result,sound,revised.config) end
	local actual=#played==0 and "none" or table.concat(played,",")
	assert(actual==scenario.event,"Cue mismatch "..scenario.name..": "..actual)
	assert(#played<=1,"Duplicate transaction celebration: "..scenario.name)
	print("CASE|"..scenario.name.."|"..actual.."|"..canonical(revised.profile))
end

-- Ordinary purchases/boosts and mined hats keep their original independent route.
do
	local sounds={}
	local sound={tocar=function(event)table.insert(sounds,event)end,drop=function(r)table.insert(sounds,"drop_"..r)end}
	boostGate({boosts={sorte=900,moedas=0}},{boosts={sorte=0,moedas=0}},98,{dataClock=100},sound)
	hatGate({audioContext="mineracao",raridade="mitico"},sound)
	assert(table.concat(sounds,",")=="boost,drop_mitico")
	print("PASS|purchase_boost_and_mined_hat_preserved")
end

-- Exercise the actual preference updater with a newer local value and stale server patch.
do
	local Preferences=compile(SOURCES.Preferences,"actual-preferences")
	local player={attribute=.90,SetAttribute=function()error("Server update replicated a stale mix attribute")end}
	local profile={audio=Preferences.sanitize(),moeda=777}
	local env={AudioPreferences=Preferences,cache={[player]=profile},PlayerData={audioPersistente=function()return true end}}
	local updater=compile(SOURCES.UpdateAudio.."\nreturn PlayerData.atualizarAudio","actual-preference-update",env)
	local first=updater(player,{AudioMasterVolume=.85,MusicEnabled=false,moeda=99999})
	assert(first.ok and first.audio.AudioMasterVolume==.85 and first.audio.MusicEnabled==false)
	assert(player.attribute==.90 and profile.moeda==777 and profile.audio.moeda==nil)
	local second=updater(player,{AudioMasterVolume=.90,AudioMusicVolume=0/0,AudioSFXVolume=math.huge,AudioUIVolume=-5})
	assert(second.audio.AudioMasterVolume==.90 and second.audio.AudioMusicVolume==.60 and second.audio.AudioSFXVolume==.85 and second.audio.AudioUIVolume==0)
	print("PASS|late_patch_no_attribute_rollback_and_whitelist")
end

-- Read the actual snapshot prefix independently of presentation/leaderstats side effects.
do
	local profile = { moeda = 321, audio = { AudioMasterVolume = .7 } }
	local player = { Name = "SnapshotFixture" }
	local published
	local env = { cache = { [player] = profile }, Passes = { todos = function()return {}end },
		PlayerData = { snapshot = function(p)return { moeda=p.moeda,audio=table.clone(p.audio) }end },
		RS = { Remotes = { AtualizarDados = { FireClient = function(_,_,snap)published=snap end } } } }
	local sync = compile(SOURCES.SyncHeader.."\nreturn PlayerData.sincronizar", "actual-snapshot-context", env)
	sync(player, "daily")
	assert(published.audioContext=="daily" and profile.audioContext==nil)
	sync(player, "code")
	assert(published.audioContext=="code" and profile.audioContext==nil)
	sync(player)
	assert(published.audioContext==nil and profile.audioContext==nil)
	print("PASS|snapshot_context_transient_and_purchase_context_clear")
end
do
	local gate=compile(SOURCES.AchievementGate,"actual-achievement-gate")
	assert(gate(true)==false and gate(false)=="achievement")
	print("PASS|transaction_achievement_sound_false_visual_preserved")
end

print("ALL_FIXTURES_PASSED|13")
