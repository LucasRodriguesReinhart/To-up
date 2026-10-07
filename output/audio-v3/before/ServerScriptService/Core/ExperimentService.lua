-- ExperimentService (GDD v3.1 secao 11)
-- * atribuicao persistente no perfil (perfil.exp[chave] = { v = variante, salt, versao, inicio })
-- * bucket = hash(UserId .. chave .. salt) % 10000 -> rollout (0-100%) e pesos das variantes
-- * camadas: um jogador so participa de UM experimento por camada (exclusao mutua)
-- * kill switch: ativo = false -> todo mundo recebe o padrao na hora (a atribuicao fica guardada)
-- * trocar o salt reinicia o experimento com nova amostra
-- Nenhum experimento vem ligado: ligue so quando o produto/variacao existir de verdade.
local E = {}

E.EXPERIMENTOS = {
	-- exemplo pronto para o primeiro teste A/B do GDD (preco do Starter). Precisa de 2 produtos criados.
	starter_preco = {
		ativo = false, camada = "loja", rollout = 100, salt = "s1", versao = 1, inicio = "2026-09-14",
		variantes = { { id = "A", peso = 50 }, { id = "B", peso = 50 } },
	},
}

-- FNV-1a 32 bits (deterministico, igual em qualquer servidor)
local function hash(texto)
	local h = 2166136261
	for i = 1, #texto do
		h = bit32.bxor(h, string.byte(texto, i))
		h = (h * 16777619) % 4294967296
	end
	return h
end
E.hash = hash

function E.atribuir(player, perfil)
	perfil.exp = perfil.exp or {}
	local camadasOcupadas = {}
	for chave, a in pairs(perfil.exp) do
		local def = E.EXPERIMENTOS[chave]
		if def and def.ativo and a.salt == def.salt and a.v ~= "controle" and a.v ~= "excluido" then
			camadasOcupadas[def.camada] = chave
		end
	end
	local nomes = {}
	for chave in pairs(E.EXPERIMENTOS) do table.insert(nomes, chave) end
	table.sort(nomes)
	for _, chave in ipairs(nomes) do
		local def = E.EXPERIMENTOS[chave]
		local atual = perfil.exp[chave]
		if def.ativo and not (atual and atual.salt == def.salt) then
			local b = hash(tostring(player.UserId) .. ":" .. chave .. ":" .. def.salt) % 10000
			local v
			if b >= def.rollout * 100 then
				v = "controle"
			elseif camadasOcupadas[def.camada] and camadasOcupadas[def.camada] ~= chave then
				v = "excluido"
			else
				local total = 0
				for _, var in ipairs(def.variantes) do total += var.peso end
				local x = (hash(tostring(player.UserId) .. ":" .. chave .. ":var:" .. def.salt) % 10000) / 10000 * total
				for _, var in ipairs(def.variantes) do
					x -= var.peso
					if x < 0 then v = var.id; break end
				end
				v = v or def.variantes[#def.variantes].id
				camadasOcupadas[def.camada] = chave
			end
			perfil.exp[chave] = { v = v, salt = def.salt, versao = def.versao, inicio = def.inicio }
		end
	end
end

-- variante ativa do jogador (nil = experimento desligado, controle ou excluido -> use o padrao)
function E.variante(perfil, chave)
	local def = E.EXPERIMENTOS[chave]
	local a = perfil and perfil.exp and perfil.exp[chave]
	if not def or not def.ativo or not a or a.salt ~= def.salt then return nil end
	if a.v == "controle" or a.v == "excluido" then return nil end
	return a.v
end

-- texto curto para a telemetria: "starter_preco:A@v1"
function E.resumo(perfil)
	local partes = {}
	for chave, a in pairs(perfil and perfil.exp or {}) do
		local def = E.EXPERIMENTOS[chave]
		if def and def.ativo and a.salt == def.salt then
			table.insert(partes, chave .. ":" .. tostring(a.v) .. "@v" .. tostring(a.versao))
		end
	end
	table.sort(partes)
	return table.concat(partes, ",")
end

return E

