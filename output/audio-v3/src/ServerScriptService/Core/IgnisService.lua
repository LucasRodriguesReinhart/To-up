local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Passes = require(script.Parent.Passes)
local Economia = require(script.Parent.Economia)
local Telemetria = require(script.Parent.Telemetria)
local HatVisual = require(script.Parent.HatVisual)

local IgnisService = {}

local MSG_VENDA = "Venda no Ignis do lobby (teleporte gratis) ou use o passe Auto Sell"
local MSG_LOJA = "Compre no Ignis do lobby (teleporte gratis)"

-- ---------- VENDER ----------
-- auto = true quando o passe Auto Sell vende sozinho ao encher a mochila (qualquer ilha)
function IgnisService.vender(player, auto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if not auto and not Passes.noLobby(player) and not Passes.possui(player, "AutoSell") then
		return { ok = false, msg = MSG_VENDA, semAcesso = "AutoSell" }
	end

	local mult = Economia.multMoedas(player, perfil)
	local total, itens = 0, 0
	local porArea = {}
	for id, qtd in pairs(perfil.mochila) do
		local def = Config.infoMinerio(id)
		if def then
			local ganho = def.valor * qtd * mult
			total += ganho
			itens += qtd
			for _, a in ipairs(Config.Areas) do
				if a.tema == def.tema then porArea[a.id] = (porArea[a.id] or 0) + ganho end
			end
		end
	end
	if itens == 0 then return { ok = false, msg = auto and nil or "Mochila vazia" } end

	total = math.floor(total)
	for areaId, ganho in pairs(porArea) do
		PlayerData.progredirMissao(perfil, areaId, "vender", math.floor(ganho))
	end
	perfil.moeda += total
	perfil.mochila = {}
	Telemetria.economia(player, perfil, true, total, "Gameplay", auto and "venda_auto" or "venda")
	Telemetria.marco(player, perfil, "FirstSell", { auto = auto and 1 or 0 })
	PlayerData.sincronizar(player)
	if auto then
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "venda", ganho = total, itens = itens, auto = true, texto = "Auto Sell: +" .. Config.formatar(total) .. " moedas" })
	end
	return { ok = true, ganho = total, itens = itens }
end

local function gastar(player, perfil, custo, item)
	perfil.moeda -= custo
	Telemetria.economia(player, perfil, false, custo, "Shop", item)
end

-- ---------- PICARETA ----------
function IgnisService.comprarPicareta(player, id)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local nova, iNova = Config.picaretaPorId(id)
	if not nova then return { ok = false, msg = "Picareta inexistente" } end
	if perfil.picaretasCompradas[id] then return { ok = false, msg = "Voce ja tem essa picareta" } end
	if iNova > 1 and not perfil.picaretasCompradas[Config.Picaretas[iNova - 1].id] then
		return { ok = false, msg = "Compre a " .. Config.Picaretas[iNova - 1].nome .. " antes" }
	end
	if not Passes.noLobby(player) then
		return { ok = false, msg = MSG_LOJA, semAcesso = "Loja" }
	end
	if perfil.moeda < nova.custo then return { ok = false, msg = "Faltam " .. Config.formatar(nova.custo - perfil.moeda) .. " moedas" } end

	gastar(player, perfil, nova.custo, "picareta_" .. id)
	perfil.picaretasCompradas[id] = true
	perfil.picareta = id
	Telemetria.marco(player, perfil, "FirstUpgrade", { item = id })
	PlayerData.sincronizar(player)
	return { ok = true, upgradeMax = iNova == #Config.Picaretas, msg = nova.nome .. " equipada (x" .. string.format("%.2f", nova.mult) .. " dano)" }
end

-- trocar entre picaretas ja compradas: livre, em qualquer lugar
function IgnisService.equiparPicareta(player, id)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local def = Config.picaretaPorId(id)
	if not def or not perfil.picaretasCompradas[id] then return { ok = false, msg = "Voce nao tem essa picareta" } end
	if perfil.picareta == id then return { ok = true, msg = def.nome .. " ja esta em uso" } end
	perfil.picareta = id
	PlayerData.sincronizar(player)
	return { ok = true, msg = def.nome .. " equipada" }
end

-- ---------- MOCHILA ----------
function IgnisService.comprarMochila(player, id)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local nova, iNova = Config.mochilaPorId(id)
	if not nova then return { ok = false, msg = "Mochila inexistente" } end
	local _, iAtual = Config.mochilaPorId(perfil.mochilaTier)
	if iNova <= (iAtual or 1) then return { ok = false, msg = "Voce ja tem essa ou melhor" } end
	if iNova > (iAtual or 1) + 1 then
		return { ok = false, msg = "Compre a " .. Config.Mochilas[(iAtual or 1) + 1].nome .. " antes" }
	end
	if not Passes.noLobby(player) then
		return { ok = false, msg = MSG_LOJA, semAcesso = "Loja" }
	end
	if perfil.moeda < nova.custo then return { ok = false, msg = "Faltam " .. Config.formatar(nova.custo - perfil.moeda) .. " moedas" } end

	gastar(player, perfil, nova.custo, "mochila_" .. id)
	perfil.mochilaTier = id
	Telemetria.marco(player, perfil, "FirstUpgrade", { item = id })
	PlayerData.sincronizar(player)
	return { ok = true, upgradeMax = iNova == #Config.Mochilas, msg = nova.nome .. " equipada" }
end

-- ---------- HATS ----------
function IgnisService.equipar(player, uid)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local inst = perfil.hatsInv[uid]
	if not inst then return { ok = false, msg = "Voce nao tem esse hat" } end

	for i, e in ipairs(perfil.equipados) do
		if e == uid then
			table.remove(perfil.equipados, i)
			PlayerData.sincronizar(player)
			return { ok = true, equipped = false, msg = "Desequipado" }
		end
	end
	if #perfil.equipados >= PlayerData.slots(perfil) then
		return { ok = false, msg = "Sem slot livre. Novos slots nos mundos 3 e 5." }
	end
	table.insert(perfil.equipados, uid)
	Telemetria.marco(player, perfil, "FirstHatEquipped", { manual = 1 })
	PlayerData.sincronizar(player)
	return { ok = true, equipped = true, msg = "Equipado" }
end

function IgnisService.desequiparTodos(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	perfil.equipados = {}
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Todos desequipados" }
end

-- equipa os hats de maior dano que couberem nos slots (repetidos valem)
function IgnisService.equiparMelhores(player, silencioso)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local lista = {}
	for uid, inst in pairs(perfil.hatsInv) do
		local def = Config.hatPorId(inst.id)
		if def then
			table.insert(lista, { uid = uid, dano = Config.hatDanoNoNivel(def.dano, inst.nivel or 1) })
		end
	end
	table.sort(lista, function(a, b) return a.dano > b.dano end)
	local slots = PlayerData.slots(perfil)
	perfil.equipados = {}
	for i = 1, math.min(slots, #lista) do
		table.insert(perfil.equipados, lista[i].uid)
	end
	if #perfil.equipados > 0 then Telemetria.marco(player, perfil, "FirstHatEquipped", { manual = silencioso and 0 or 1 }) end
	PlayerData.sincronizar(player)
	return { ok = true, msg = #perfil.equipados .. " hat(s) equipado(s)" }
end

-- ---------- FUSAO (estilo Anime Fighters) ----------
function IgnisService.fundir(player, uid, lista)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(uid) ~= "string" or type(lista) ~= "table" then return { ok = false, msg = "Selecione hats pra fundir" } end

	local alvo = perfil.hatsInv[uid]
	local def = alvo and Config.hatPorId(alvo.id)
	if not def then return { ok = false, msg = "Voce nao tem esse hat" } end
	if alvo.nivel >= Config.HAT_NIVEL_MAX then return { ok = false, msg = "Nivel maximo" } end

	local vistos, usados, xpTotal, ganhos = {}, 0, 0, 0
	local nivelAntes = alvo.nivel
	for _, outro in ipairs(lista) do
		if alvo.nivel >= Config.HAT_NIVEL_MAX then break end
		if type(outro) == "string" and outro ~= uid and not vistos[outro] then
			vistos[outro] = true
			local inst = perfil.hatsInv[outro]
			local odef = inst and Config.hatPorId(inst.id)
			if odef and not table.find(perfil.equipados, outro) then
				local xp = Config.hatXpComoComida(odef, inst)
				ganhos += Config.hatAplicarXp(def, alvo, xp)
				xpTotal += xp
				perfil.hatsInv[outro] = nil
				usados += 1
			end
		end
	end
	if usados == 0 then return { ok = false, msg = "Nenhum hat valido selecionado" } end
	Telemetria.marco(player, perfil, "FirstFusion", { usados = usados })
	PlayerData.sincronizar(player)
	return { ok = true, usados = usados, levelUp = alvo.nivel > nivelAntes, nivelAntes = nivelAntes, nivel = alvo.nivel, upgradeMax = alvo.nivel >= Config.HAT_NIVEL_MAX, raridade = def.raridade,
		msg = ganhos > 0 and (def.nome .. ": nivel " .. nivelAntes .. " -> " .. alvo.nivel .. " (" .. usados .. " hats)")
			or ("+" .. Config.formatar(xpTotal) .. " XP em " .. def.nome) }
end

return IgnisService

