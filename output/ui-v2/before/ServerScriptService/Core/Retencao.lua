-- Retencao P0: Daily basico (ciclo de 7 dias sem perda) e Index (colecao de pets e hats).
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

