-- Pets: cada pet e um item separado (uid), ocupando 1 espaco no inventario.
local RS = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local PetService = {}

local function equipado(perfil, uid)
	return table.find(perfil.petsEquipados, uid) ~= nil
end

function PetService.equipar(player, uid)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if not perfil.petsInv[uid] then return { ok = false, msg = "Voce nao tem esse pet" } end

	for i, e in ipairs(perfil.petsEquipados) do
		if e == uid then
			table.remove(perfil.petsEquipados, i)
			PlayerData.sincronizar(player)
			return { ok = true, msg = "Desequipado" }
		end
	end
	if #perfil.petsEquipados >= PlayerData.slotsPets(perfil) then
		return { ok = false, msg = "Sem slot de pet livre (" .. PlayerData.slotsPets(perfil) .. " slots)" }
	end
	table.insert(perfil.petsEquipados, uid)
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Equipado" }
end

function PetService.desequiparTodos(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	perfil.petsEquipados = {}
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Pets desequipados" }
end

-- os que mais multiplicam dano (repetidos valem)
function PetService.equiparMelhores(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local lista = {}
	for uid, inst in pairs(perfil.petsInv) do
		local def = Config.petPorId(inst.id)
		if def then table.insert(lista, { uid = uid, v = Config.petBonusDano(def, inst.nivel or 1) }) end
	end
	table.sort(lista, function(a, b) return a.v > b.v end)
	local slots = PlayerData.slotsPets(perfil)
	perfil.petsEquipados = {}
	for i = 1, math.min(slots, #lista) do
		table.insert(perfil.petsEquipados, lista[i].uid)
	end
	PlayerData.sincronizar(player)
	return { ok = true, msg = #perfil.petsEquipados .. " pet(s) equipado(s)" }
end

-- ---------- ALIMENTAR (estilo Anime Fighters) ----------
-- escolhe o pet alvo e uma lista de pets pra sacrificar (qualquer personagem).
-- XP de cada um: base da raridade/area/nivel + 70% do que ja foi investido nele.
-- pets equipados e o proprio alvo nunca entram; parou no nivel maximo, o resto nao e consumido.
function PetService.alimentar(player, alvoUid, lista)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(alvoUid) ~= "string" or type(lista) ~= "table" then return { ok = false, msg = "Selecione personagens" } end
	local alvo = perfil.petsInv[alvoUid]
	local def = alvo and Config.petPorId(alvo.id)
	if not def then return { ok = false, msg = "Voce nao tem esse pet" } end
	if alvo.nivel >= Config.PET_NIVEL_MAX then return { ok = false, msg = "Nivel maximo" } end

	local vistos, usados, xpTotal = {}, 0, 0
	local nivelAntes = alvo.nivel
	for _, uid in ipairs(lista) do
		if alvo.nivel >= Config.PET_NIVEL_MAX then break end
		if type(uid) == "string" and uid ~= alvoUid and not vistos[uid] then
			vistos[uid] = true
			local inst = perfil.petsInv[uid]
			local odef = inst and Config.petPorId(inst.id)
			if odef and not equipado(perfil, uid) then
				local xp = Config.petXpComoComida(odef, inst)
				Config.petAplicarXp(def, alvo, xp)
				xpTotal += xp
				perfil.petsInv[uid] = nil
				usados += 1
			end
		end
	end
	if usados == 0 then return { ok = false, msg = "Nenhum personagem valido selecionado" } end
	PlayerData.sincronizar(player)
	local nome = alvo.apelido or def.nome
	return { ok = true, levelUp = alvo.nivel > nivelAntes, nivelAntes = nivelAntes, nivel = alvo.nivel, xp = xpTotal, msg = alvo.nivel > nivelAntes and (nome .. ": nivel " .. nivelAntes .. " -> " .. alvo.nivel .. " (" .. usados .. " usados)")
		or ("+" .. Config.formatar(xpTotal) .. " XP para " .. nome) }
end

-- ---------- APELIDO ----------
-- aparece em cima do pet pra todo mundo: tem que passar pelo filtro do Roblox.
function PetService.renomear(player, uid, texto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(uid) ~= "string" or type(texto) ~= "string" then return { ok = false } end
	local inst = perfil.petsInv[uid]
	local def = inst and Config.petPorId(inst.id)
	if not def then return { ok = false, msg = "Voce nao tem esse pet" } end

	texto = texto:gsub("[%c]", ""):match("^%s*(.-)%s*$")
	if texto == "" or texto == def.nome then
		inst.apelido = nil
		PlayerData.sincronizar(player)
		return { ok = true, msg = "Nome original restaurado" }
	end
	if utf8.len(texto) == nil or utf8.len(texto) > 20 then return { ok = false, msg = "Use ate 20 caracteres" } end

	local ok, filtrado = pcall(function()
		local res = TextService:FilterStringAsync(texto, player.UserId, Enum.TextFilterContext.PublicChat)
		return res:GetNonChatStringForBroadcastAsync()
	end)
	if not ok then return { ok = false, msg = "Nao foi possivel verificar o nome. Tente de novo." } end
	if filtrado:find("#") and not texto:find("#") then
		return { ok = false, msg = "Esse nome nao e permitido" }
	end
	inst.apelido = filtrado
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Nome alterado para " .. filtrado }
end

return PetService

