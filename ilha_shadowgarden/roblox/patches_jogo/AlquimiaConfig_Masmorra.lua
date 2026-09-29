-- PATCH ov09b (2026-09-29) - MASMORRA INFINITA em ReplicatedStorage.AlquimiaConfig.
-- ONDE ENTRA: substitui a tabela INTEIRA "M.Masmorra = { ... }" (do comentario "---------- MASMORRA DAS SOMBRAS" ate o
-- "}" que fecha a tabela, logo ANTES de "-- tipos de minerio da masmorra: ... M.VARIANTE_DO_MARCADOR"). O resto do
-- AlquimiaConfig (itens, receitas, VARIANTE_DO_MARCADOR, ESTADOS, NOME_ESTADO) fica igual.
-- A copia completa ja atualizada esta em roblox/AlquimiaConfig.lua (colar no ModuleScript RS.AlquimiaConfig inteiro
-- tambem serve). O DungeonService.lua novo PRECISA destes campos (TEMPO_SALA, TRANSICAO, DURACAO_MAX, SALAS,
-- SALAS_POR_NIVEL, NIVEL, BONUS_MARCO); o campo antigo DURACAO deixou de ser usado.

-- ---------- MASMORRA DAS SOMBRAS (periodica: XX:00 e XX:30 no relogio do servidor; corrida INFINITA de salas) ----------
M.Masmorra = {
	PERIODO = 1800,            -- abre a cada 30 min, alinhado a hora cheia/meia hora (GetServerTimeNow, UTC)
	CONTAGEM = 60,             -- s de contagem regressiva antes de abrir (estado COUNTDOWN)
	JANELA_ENTRADA = 90,       -- s depois de abrir em que ainda da para entrar (ENTRY_OPEN)          PROVISORIO
	-- masmorra infinita (ov09b): o tempo e POR SALA; esgotou sem limpar = fim da corrida
	TEMPO_SALA = 150,          -- s para limpar a sala atual (o relogio da sala 1 comeca na 1a entrada) PROVISORIO
	TRANSICAO = 4,             -- s entre limpar a sala (passagem aberta, bonus) e o teleporte para a proxima
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
	SELO = { largura = 18, altura = 14, espessura = 2 },
}
