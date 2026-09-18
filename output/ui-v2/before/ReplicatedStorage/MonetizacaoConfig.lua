-- MONETIZACAO P0 (GDD v3.1, secao 5). Catalogo de gamepasses, developer products e Starter Pack.
-- COMO ATIVAR: crie cada item no Creator Dashboard (Monetization) e cole o ID em `id`.
-- id = 0 -> o item aparece na loja como "Em breve" e nao pode ser comprado.
-- `robux` e so o preco exibido/planejado: o preco cobrado e sempre o do Creator Dashboard.
local M = {}

M.PASSES = {
	{ chave = "VIP",        nome = "VIP",            id = 0, robux = 399, desc = "+10% de moedas nas vendas, tag no chat e sala VIP" },
	{ chave = "Lucky",      nome = "Lucky",          id = 0, robux = 149, desc = "Chance de Épico ou melhor x1,25 em hats e invocações (não mexe no pity)" },
	{ chave = "HatSlot",    nome = "+1 Hat Slot",    id = 0, robux = 249, desc = "+1 slot para equipar hats" },
	{ chave = "Inventario", nome = "+50 Inventário", id = 0, robux = 99,  desc = "Inventário de hats e de pets: 50 → 100" },
	{ chave = "AutoSell",   nome = "Auto Sell",      id = 0, robux = 199, desc = "Vende sozinho quando a mochila enche, em qualquer ilha" },
}

M.PRODUTOS = {
	{ chave = "BoostSorte",   nome = "Boost de Sorte",    id = 0, robux = 49,  desc = "Chance de Épico ou melhor x1,5 por 15 min", boost = "sorte", minutos = 15 },
	{ chave = "BoostMoedas",  nome = "Moedas x2",         id = 0, robux = 79,  desc = "Moedas x2 nas vendas por 30 min", boost = "moedas", minutos = 30 },
	{ chave = "PackP",        nome = "Pack de Moedas P",  id = 0, robux = 49,  desc = "10 min de renda do seu mundo atual", minutosRenda = 10 },
	{ chave = "PackM",        nome = "Pack de Moedas M",  id = 0, robux = 129, desc = "30 min de renda do seu mundo atual", minutosRenda = 30 },
	{ chave = "PackG",        nome = "Pack de Moedas G",  id = 0, robux = 349, desc = "90 min de renda do seu mundo atual", minutosRenda = 90 },
	{ chave = "InvocarChefe", nome = "Invocar Chefe",     id = 0, robux = 99,  desc = "O chefe aparece agora na sua ilha, para o servidor inteiro" },
	-- Starter: conteudo = Pack M (129) + Moedas x2 30 min (79) + Sorte 15 min (49) = 257 Robux vendidos separado.
	-- A skin Kunai de Ignis e so visual e NAO entra na soma.
	{ chave = "Starter", nome = "Starter Pack", id = 0, robux = 129, starter = true, valorSeparado = 257,
		desc = "Pack de Moedas M + Moedas x2 (30 min) + Sorte (15 min) + skin Kunai de Ignis",
		conteudo = { minutosRenda = 30, boosts = { { boost = "moedas", minutos = 30 }, { boost = "sorte", minutos = 15 } }, cosmetico = "kunai_ignis" } },
}

M.VIP_MOEDAS = 1.10
M.LUCKY_MULT = 1.25
M.BOOST_SORTE_MULT = 1.5
M.BOOST_MOEDAS_MULT = 2
-- Friend Boost (P0): amigos do Roblox no mesmo servidor e ativos
M.FRIEND_BOOST_POR_AMIGO = 0.10
M.FRIEND_BOOST_MAX = 0.30

-- ofertas (regras de etica do GDD: no maximo 1 oferta paga a cada 10 min, nunca antes do min 5)
M.STARTER_APOS_MIN = 5
M.STARTER_JANELA_H = 72
M.OFERTA_INTERVALO_MIN = 10

function M.passe(chave)
	for _, p in ipairs(M.PASSES) do if p.chave == chave then return p end end
end
function M.produto(chave)
	for _, p in ipairs(M.PRODUTOS) do if p.chave == chave then return p end end
end
function M.produtoPorId(id)
	if not id or id <= 0 then return nil end
	for _, p in ipairs(M.PRODUTOS) do if p.id == id then return p end end
end

return M

