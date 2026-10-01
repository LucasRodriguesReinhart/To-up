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

-- ---------- MASMORRA DAS SOMBRAS (periodica: XX:00 e XX:30 no relogio do servidor; corrida INFINITA de salas) ----------
M.Masmorra = {
	PERIODO = 1800,            -- abre a cada 30 min, alinhado a hora cheia/meia hora (GetServerTimeNow, UTC)
	CONTAGEM = 60,             -- s de contagem regressiva antes de abrir (estado COUNTDOWN)
	JANELA_ENTRADA = 90,       -- s depois de abrir em que ainda da para entrar (ENTRY_OPEN)          PROVISORIO
	-- masmorra infinita (ov09b): o tempo e POR SALA; esgotou sem limpar = fim da corrida
	TEMPO_SALA = 180,          -- s para limpar a sala atual (salas 3x: 150 -> 180; o relogio da sala 1 comeca na 1a entrada)
	TRANSICAO = 8,             -- s entre limpar a sala e o teleporte do grupo (tocar o portal aberto segue na hora)
	DURACAO_MAX = 1500,        -- s desde a abertura: TETO de seguranca da corrida. Tem de ser
	                           -- <= PERIODO - CONTAGEM - FINALIZANDO - RESET (1722), senao encosta na proxima abertura
	FINALIZANDO = 12,          -- s com o portal de saida aceso e as rochas travadas (FINISHING)
	RESET = 6,                 -- s de limpeza antes de voltar a WAITING (RESETTING)
	MAX_JOGADORES = 12,
	-- ciclo das salas fisicas: sala 1 = R2, sala 2 = R3, sala 3 = R2, ... (a R1 e so a chegada)
	SALAS = { "R2", "R3" },
	SALAS_POR_NIVEL = 5,       -- nivel = 1 + floor((sala - 1) / SALAS_POR_NIVEL)  -> salas 1-5 = nivel 1, 6-10 = nivel 2
	-- NIVEL 1 (a base de tudo):
	HP_MULT = { comum = 0.5, incomum = 0.5, epica = 0.45, lendaria = 0.35 },   -- x HP do minerio da area PROVISORIO
	-- recompensa por minerio quebrado, para CADA jogador que golpeou aquele minerio (idempotente: sala+minerio+jogador)
	RECOMPENSA = {                                                                  -- PROVISORIO
		comum = { { "sg_po_sombra", 1 } },
		incomum = { { "sg_po_sombra", 2 } },
		epica = { { "sg_essencia_lunar", 1 } },
		lendaria = { { "sg_fragmento_abismo", 1 }, { "sg_essencia_lunar", 1 } },
	},
	-- bonus por SALA LIMPA para quem esta dentro (1 vez por jogador por sala)
	BONUS_LIMPEZA = { { "sg_po_sombra", 3 } },                                     -- PROVISORIO
	-- bonus de MARCO a cada SALAS_POR_NIVEL salas limpas (sala 5, 10, 15...; 1 vez por jogador por marco)
	BONUS_MARCO = { { "sg_essencia_lunar", 2 }, { "sg_po_sombra", 6 } },          -- PROVISORIO
	-- DIFICULDADE por nivel (formulas; nivel 1 = os valores acima):
	--   HP do minerio   = HP_MULT[v] * (1 + HP_POR_NIVEL * (nivel - 1))
	--   recompensa/bonus/marco: qtd = max(base, floor(base * (1 + RECOMPENSA_POR_NIVEL * (nivel - 1)) + 0,5))
	--   raridade: o marcador DUN_ORE_<sala>_<RARIDADE>_<nn> e o PISO; cada ponto sobe 1 degrau com chance
	--     p = min(PROMOCAO_MAX, PROMOCAO_POR_NIVEL * (nivel - 1)) e mais 1 degrau com a mesma chance p (so se subiu o
	--     1o). Lendaria so nos pontos TETO_LENDARIA (espacados para o minerio grande); nos outros o teto e epica.
	--   nivel:      1     2     3     4     5     6+
	--   HP x      1,00  1,35  1,70  2,05  2,40  +0,35/nivel
	--   promocao   0%   12%   24%   36%   48%   60% (teto)
	--   recomp. x 1,0   1,5   2,0   2,5   3,0   +0,5/nivel
	NIVEL = {
		HP_POR_NIVEL = 0.35,                                                        -- PROVISORIO
		RECOMPENSA_POR_NIVEL = 0.5,                                                 -- PROVISORIO
		PROMOCAO_POR_NIVEL = 0.12,                                                  -- PROVISORIO
		PROMOCAO_MAX = 0.6,
		TETO_LENDARIA = { EPIC = true, SUPERLEGENDARY = true },
	},
	-- selo de energia no vao R2-R3 (medidas de reserva se o marcador DUN_LINK_R2R3 nao trouxer os atributos w/h/t)
	SELO = { largura = 27, altura = 21, espessura = 1 },
}

-- tipos de minerio da masmorra: o marcador DUN_ORE_<sala>_<RARIDADE>_<nn> -> variante do jogo (no nivel 1; acima,
-- e o PISO da promocao por nivel)
M.VARIANTE_DO_MARCADOR = { COMMON = "comum", UNCOMMON = "incomum", EPIC = "epica", SUPERLEGENDARY = "lendaria" }

M.ESTADOS = { "WAITING", "COUNTDOWN", "ENTRY_OPEN", "RUNNING", "FINISHING", "RESETTING" }
M.NOME_ESTADO = { WAITING = "Fechada", COUNTDOWN = "Abrindo", ENTRY_OPEN = "Aberta", RUNNING = "Em andamento",
	FINISHING = "Terminando", RESETTING = "Reiniciando" }

return M
