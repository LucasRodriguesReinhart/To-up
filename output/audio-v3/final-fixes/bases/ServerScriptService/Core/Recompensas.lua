-- Recompensas: unico lugar que entrega hats, pets e moedas (minerio, chefe, Daily, compras, codigos).
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

