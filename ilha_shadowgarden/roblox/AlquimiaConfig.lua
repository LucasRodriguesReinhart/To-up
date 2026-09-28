-- AlquimiaConfig (ReplicatedStorage) - DADOS do Craft (Alquimia) e da Masmorra das Sombras da Ilha 3 (Shadow Garden).
-- Tudo aqui e DADO: o CraftService e o DungeonService so leem esta tabela. Nenhum numero de economia vai no Config
-- (regra do projeto) nem no EconomiaV31 (gerado).
-- !!! TODOS OS NUMEROS SAO PROVISORIOS (2026-09-28): nao existe simulacao para ingredientes/pocoes/masmorra.
-- Ajuste aqui (quantidades, duracoes, HP, janelas) sem tocar em codigo. Marcados com PROVISORIO.
local M = {}

M.PROVISORIO = true

-- ---------- ITENS (pilhas em perfil.itens = {[id] = qtd}) ----------
-- categoria: "ingrediente" (vem da masmorra) | "pocao" (sai do craft; beber = boost que o jogo ja tem)
-- boosts: tipos que JA existem no jogo (PlayerData.adicionarBoost / Economia.luckyMult e multMoedas): sorte, moedas
M.Itens = {
	{ id = "sg_po_sombra",      nome = "Po de Sombra",        categoria = "ingrediente", raridade = "comum",    icone = "items", stackMax = 999,
	  desc = "Resto negro que sobra dos minerios da Masmorra." },
	{ id = "sg_essencia_lunar", nome = "Essencia Lunar",      categoria = "ingrediente", raridade = "epico",    icone = "shiny", stackMax = 999,
	  desc = "Brilho frio dos minerios epicos da Masmorra." },
	{ id = "sg_fragmento_abismo", nome = "Fragmento do Abismo", categoria = "ingrediente", raridade = "lendario", icone = "gift",  stackMax = 999,
	  desc = "Cai do grande minerio da camara final." },
	{ id = "sg_pocao_sorte",    nome = "Pocao de Sorte",      categoria = "pocao", raridade = "raro",     icone = "potion", stackMax = 99,
	  efeitos = { { boost = "sorte", minutos = 10 } },                                   -- PROVISORIO
	  desc = "Sorte ativa por 10 min (soma com o boost de Sorte que ja estiver ativo)." },
	{ id = "sg_pocao_moedas",   nome = "Pocao de Moedas",     categoria = "pocao", raridade = "raro",     icone = "potion", stackMax = 99,
	  efeitos = { { boost = "moedas", minutos = 10 } },                                  -- PROVISORIO
	  desc = "Moedas x2 por 10 min (soma com o boost de Moedas que ja estiver ativo)." },
	{ id = "sg_elixir_sombras", nome = "Elixir das Sombras",  categoria = "pocao", raridade = "lendario", icone = "potion", stackMax = 99,
	  efeitos = { { boost = "sorte", minutos = 20 }, { boost = "moedas", minutos = 20 } }, -- PROVISORIO
	  desc = "Sorte e Moedas x2 por 20 min." },
}
M.porId = {}
for i, it in ipairs(M.Itens) do it.ordem = i; M.porId[it.id] = it end
function M.item(id) return M.porId[id] end

-- ---------- RECEITAS (data-driven; o servidor valida tudo) ----------
M.Receitas = {
	{ id = "r_pocao_sorte",  resultado = "sg_pocao_sorte",    qtd = 1,
	  ingredientes = { { "sg_po_sombra", 6 }, { "sg_essencia_lunar", 1 } } },           -- PROVISORIO
	{ id = "r_pocao_moedas", resultado = "sg_pocao_moedas",   qtd = 1,
	  ingredientes = { { "sg_po_sombra", 8 }, { "sg_essencia_lunar", 1 } } },           -- PROVISORIO
	{ id = "r_elixir",       resultado = "sg_elixir_sombras", qtd = 1,
	  ingredientes = { { "sg_po_sombra", 10 }, { "sg_essencia_lunar", 2 }, { "sg_fragmento_abismo", 1 } } }, -- PROVISORIO
}
M.receitaPorId = {}
for _, r in ipairs(M.Receitas) do M.receitaPorId[r.id] = r end
function M.receita(id) return M.receitaPorId[id] end

M.CRAFT_ALCANCE = 16          -- studs do caldeirao (validado no servidor pela posicao real)
M.CRAFT_INTERVALO = 0.6       -- s entre pedidos do mesmo jogador

-- ---------- MASMORRA DAS SOMBRAS (periodica: XX:00 e XX:30 no relogio do servidor) ----------
M.Masmorra = {
	PERIODO = 1800,            -- abre a cada 30 min, alinhado a hora cheia/meia hora (GetServerTimeNow, UTC)
	CONTAGEM = 60,             -- s de contagem regressiva antes de abrir (estado COUNTDOWN)
	JANELA_ENTRADA = 90,       -- s depois de abrir em que ainda da para entrar (ENTRY_OPEN)          PROVISORIO
	DURACAO = 300,             -- s de corrida contados da abertura (RUNNING termina em abre + DURACAO) PROVISORIO
	FINALIZANDO = 12,          -- s com o portal de saida aceso e as recompensas finais (FINISHING)
	RESET = 6,                 -- s de limpeza antes de voltar a WAITING (RESETTING)
	MAX_JOGADORES = 12,
	HP_MULT = { comum = 0.5, incomum = 0.5, epica = 0.45, lendaria = 0.35 },   -- x HP do minerio da area PROVISORIO
	-- recompensa por minerio quebrado, para CADA jogador que golpeou aquele minerio (idempotente por corrida)
	RECOMPENSA = {                                                                  -- PROVISORIO
		comum = { { "sg_po_sombra", 1 } },
		incomum = { { "sg_po_sombra", 2 } },
		epica = { { "sg_essencia_lunar", 1 } },
		lendaria = { { "sg_fragmento_abismo", 1 }, { "sg_essencia_lunar", 1 } },
	},
	-- bonus para quem ainda esta dentro quando TODOS os minerios da corrida caem (1 vez por jogador por corrida)
	BONUS_LIMPEZA = { { "sg_po_sombra", 3 } },                                     -- PROVISORIO
}

-- tipos de minerio da masmorra: o marcador DUN_ORE_<sala>_<RARIDADE>_<nn> -> variante do jogo
M.VARIANTE_DO_MARCADOR = { COMMON = "comum", UNCOMMON = "incomum", EPIC = "epica", SUPERLEGENDARY = "lendaria" }

M.ESTADOS = { "WAITING", "COUNTDOWN", "ENTRY_OPEN", "RUNNING", "FINISHING", "RESETTING" }
M.NOME_ESTADO = { WAITING = "Fechada", COUNTDOWN = "Abrindo", ENTRY_OPEN = "Aberta", RUNNING = "Em andamento",
	FINISHING = "Terminando", RESETTING = "Reiniciando" }

return M
