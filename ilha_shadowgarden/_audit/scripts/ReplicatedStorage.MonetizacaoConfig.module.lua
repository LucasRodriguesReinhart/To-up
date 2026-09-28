-- MONETIZACAO P0 (GDD v3.1, secao 5). Catalogo de gamepasses, developer products e Starter Pack.
-- COMO ATIVAR: crie cada item no Creator Dashboard (Monetization) e cole o ID em `id`.
-- id = 0 -> o item aparece na loja como "Em breve" e nao pode ser comprado.
-- `robux` e so o preco exibido/planejado: o preco cobrado e sempre o do Creator Dashboard.
local M = {}

M.MULTI_OPEN_COUNT = 4
M.PASSES = {
 {chave="MultiOpen",nome="Multi Open",id=0,robux=0,desc="Abra 4 estrelas simultaneamente. Cada estrela usa o custo normal de moedas."},
 {chave="Speed2x",nome="2X Speed",id=0,robux=0,desc="Escolha de 1x a 2x sua velocidade normal nas configurações."},
 {chave="PetSlots",nome="+3 unidades equipadas",id=1982222478,robux=399,icon=99441632008831,desc="Equipe três unidades adicionais."},
 {chave="PortableForge",nome="Forja portátil de Ignis",id=1983332510,robux=249,icon=132981230702521,desc="Venda seus minérios de qualquer lugar. Venda manual pelo atalho da mochila."},
 {chave="Inventory1000",nome="+1000 espaços",id=1981412489,robux=299,icon=119556624950231,desc="Mais 1000 espaços para unidades e acessórios. Acumula com os outros passes de espaço."},
 {chave="Inventory300",nome="+300 espaços",id=1985126289,robux=150,icon=77731366713850,desc="Mais 300 espaços para unidades e acessórios. Acumula com os outros passes de espaço."},
 {chave="Inventario",nome="+50 espaços",id=1981526513,robux=9,icon=113891132096263,desc="Mais 50 espaços para unidades e acessórios. Acumula com os outros passes de espaço."},
 {chave="HatSlot",nome="+3 acessórios equipados",id=1985288267,robux=350,icon=128462085658045,desc="Equipe três acessórios adicionais."},
 {chave="LuckyPlus",nome="Lucky+",id=1984808508,robux=149,icon=130567131583953,desc="Chance de Épico ou melhor ×1,50. Acumula com Lucky e não altera a garantia."},
 {chave="Lucky",nome="Lucky",id=1984046505,robux=599,icon=129542791610654,desc="Chance de Épico ou melhor ×1,25. Não altera a garantia."},
 {chave="VIP",nome="VIP",id=1985138262,robux=499,icon=125812291452782,desc="Receba 10% mais moedas nas vendas."},
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
M.LUCKY_PLUS_MULT = 1.50
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

