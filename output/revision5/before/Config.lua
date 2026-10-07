local Config = {}

-- ---------- TEMAS / MINERIOS ----------
-- um tema por area. cada tema tem 3 variantes mineraveis + chefe.
Config.Temas = {
	chakra   = { nome = "Chakra",   valor = 1,     cor = Color3.fromRGB(90, 175, 255) },
	ki       = { nome = "Ki",       valor = 7,     cor = Color3.fromRGB(255, 190, 60) },
	nichirin = { nome = "Nichirin", valor = 48,    cor = Color3.fromRGB(90, 220, 190) },
	sombra   = { nome = "Sombra",   valor = 330,   cor = Color3.fromRGB(150, 90, 230) },
	mare     = { nome = "Mare",     valor = 2300,  cor = Color3.fromRGB(70, 200, 235) },
	serio    = { nome = "Serio",    valor = 16000, cor = Color3.fromRGB(255, 110, 80) },
}

-- variantes dentro de uma area: multiplicam vida, valor e chance de aparecer
Config.Variantes = {
	{ id = "comum",   nome = "",         hp = 1,  valor = 1,  peso = 70, corMult = 1.00 },
	{ id = "incomum", nome = "Incomum",  hp = 4,  valor = 5,  peso = 25, corMult = 1.15 },
	{ id = "epica",   nome = "Epico",    hp = 16, valor = 22, peso = 5,  corMult = 1.35 },
}

-- ---------- PICARETAS ----------
Config.Picaretas = {
	{ id = "enferrujada", nome = "Picareta Enferrujada", dano = 2,        custo = 0 },
	{ id = "ferro",       nome = "Picareta de Ferro",    dano = 8,        custo = 150 },
	{ id = "aco",         nome = "Picareta de Aco",      dano = 34,       custo = 1100 },
	{ id = "rubi",        nome = "Picareta de Rubi",     dano = 150,      custo = 8000 },
	{ id = "obsidiana",   nome = "Picareta de Obsidiana",dano = 700,      custo = 60000 },
	{ id = "runica",      nome = "Picareta Runica",      dano = 3400,     custo = 450000 },
	{ id = "estelar",     nome = "Picareta Estelar",     dano = 17000,    custo = 3200000 },
	{ id = "ignis",       nome = "Picareta de Ignis",    dano = 90000,    custo = 24000000 },
}

-- ---------- MOCHILAS ----------
Config.Mochilas = {
	{ id = "saco_pano", nome = "Saco de Pano",      capacidade = 20,    custo = 0 },
	{ id = "couro",     nome = "Mochila de Couro",  capacidade = 50,    custo = 120 },
	{ id = "reforcada", nome = "Mochila Reforcada", capacidade = 130,   custo = 900 },
	{ id = "ferro",     nome = "Mochila de Ferro",  capacidade = 340,   custo = 7000 },
	{ id = "runica",    nome = "Mochila Runica",    capacidade = 900,   custo = 55000 },
	{ id = "abissal",   nome = "Mochila Abissal",   capacidade = 2400,  custo = 420000 },
	{ id = "estelar",   nome = "Mochila Estelar",   capacidade = 6500,  custo = 3000000 },
	{ id = "ignis",     nome = "Mochila de Ignis",  capacidade = 18000, custo = 22000000 },
}

-- ---------- HATS ----------
Config.Raridades = {
	comum    = { nome = "Comum",    cor = Color3.fromRGB(175, 175, 180), peso = 1000, ordem = 1 },
	incomum  = { nome = "Incomum",  cor = Color3.fromRGB(90, 205, 110),  peso = 340,  ordem = 2 },
	raro     = { nome = "Raro",     cor = Color3.fromRGB(80, 150, 255),  peso = 90,   ordem = 3 },
	epico    = { nome = "Epico",    cor = Color3.fromRGB(185, 100, 255), peso = 20,   ordem = 4 },
	lendario = { nome = "Lendario", cor = Color3.fromRGB(255, 175, 40),  peso = 4,    ordem = 5 },
	secreto  = { nome = "Secreto",  cor = Color3.fromRGB(255, 70, 130),  peso = 1,    ordem = 6 },
}

Config.Hats = {}

-- ---------- HATS POR ILHA ----------
-- um hat por raridade em cada tema de ilha. o hat que cai numa area e sempre
-- do tema daquela area, igual o Unboxing: cada mundo tem a propria colecao.
--
-- COMO LIGAR O MODELO DO CATALOGO:
-- pegue o ID do acessorio no catalogo do Roblox (a Accessory, nao o modelo)
-- e coloque em Config.HatAssets com o id do hat. Com o ID preenchido o hat
-- aparece na cabeca do personagem; sem ID ele so da o bonus.
-- IDs de acessorio do catalogo do Roblox (UGC). Sao Accessory de verdade,
-- carregados por InsertService:LoadAsset e vestidos no personagem.
-- Pra trocar um hat de visual, basta trocar o ID aqui.
Config.HatAssets = {
	-- Vila da Folha (ninja)
	chakra_comum    = 118847047216527,  -- Black Headband
	chakra_incomum  = 131373390896001,  -- White Ninja Headband
	chakra_raro     = 11297708,         -- Black Ninja Headband of the Silent Sun
	chakra_epico    = 127241485823600,  -- Kakashi ANBU Mask
	chakra_lendario = 117940187308496,  -- Hokage Hat
	chakra_secreto  = 7730789399,       -- Golden Halo of the Divine

	-- Planeta Namekusei (ki)
	ki_comum        = 12377589455,      -- Green tracker glasses
	ki_incomum      = 134776884657832,  -- Green Scouter
	ki_raro         = 14256632396,      -- Captain Scouter
	ki_epico        = 112655023141849,  -- Saiyan Hair
	ki_lendario     = 74432870401130,   -- SSJ2 Hair
	ki_secreto      = 71547694600196,   -- Golden Halo

	-- Monte Natagumo (nichirin)
	nichirin_comum    = 17876147566,      -- Tanjiro Mask on side
	nichirin_incomum  = 108267228456151,  -- Sabito Mask
	nichirin_raro     = 9403367761,       -- Red Demonic Oni Mask
	nichirin_epico    = 129382709468977,  -- Samurai Helmet Black
	nichirin_lendario = 15099071051,      -- Kami Hannya Oni Mask Red
	nichirin_secreto  = 97410365695657,   -- Cyber Oni Samurai Hat

	-- Jardim das Sombras
	sombra_comum    = 14194512385,      -- Blindfold
	sombra_incomum  = 137503517262193,  -- Black Blindfold
	sombra_raro     = 15362311998,      -- Shadow Hood
	sombra_epico    = 11306211948,      -- Death's Shadow Hood
	sombra_lendario = 83606751701361,   -- Dark Crown
	sombra_secreto  = 135351522010275,  -- Corrupted Black Crown of the Void

	-- Grand Line (mare)
	mare_comum    = 5063815350,       -- Straw Hat
	mare_incomum  = 13476872,         -- Pirate Headband
	mare_raro     = 90042875778980,   -- Pirate Hat
	mare_epico    = 1028859,          -- Pirate Captain's Hat
	mare_lendario = 90856729434570,   -- Coral Crown
	mare_secreto  = 109107602312330,  -- Ocean's Shell Coral Crown

	-- Cidade Z (serio)
	serio_comum    = 14449295729,      -- White Hard Hat
	serio_incomum  = 14617421935,      -- Orange Hard Hat
	serio_raro     = 90840545636542,   -- Black Hood Cape
	serio_epico    = 16010152494,      -- Cyborg Helmet
	serio_lendario = 111844766857677,  -- Operator Helmet Mk2
	serio_secreto  = 88233017929294,   -- Angel Halo
}

Config.HatNomes = {
	chakra   = { comum = "Bandana Preta",       incomum = "Bandana da Folha",   raro = "Bandana do Sol Silencioso", epico = "Mascara ANBU",       lendario = "Chapeu de Hokage",    secreto = "Halo Divino" },
	ki       = { comum = "Oculos Rastreadores", incomum = "Scouter Verde",      raro = "Scouter de Capitao",        epico = "Cabelo Saiyajin",    lendario = "Cabelo SSJ2",         secreto = "Halo Dourado" },
	nichirin = { comum = "Mascara de Tanjiro",  incomum = "Mascara de Sabito",  raro = "Mascara Oni Vermelha",      epico = "Elmo Samurai",       lendario = "Hannya Escarlate",    secreto = "Elmo Ciber-Oni" },
	sombra   = { comum = "Venda",               incomum = "Venda Negra",        raro = "Capuz Sombrio",             epico = "Capuz da Morte",     lendario = "Coroa Negra",         secreto = "Coroa do Vazio" },
	mare     = { comum = "Chapeu de Palha",     incomum = "Bandana Pirata",     raro = "Chapeu Pirata",             epico = "Chapeu do Capitao",  lendario = "Coroa de Corais",     secreto = "Coroa Abissal" },
	serio    = { comum = "Capacete Branco",     incomum = "Capacete Laranja",   raro = "Capuz do Vigilante",        epico = "Elmo Ciborgue",      lendario = "Elmo Operador Mk2",   secreto = "Halo do Heroi" },
}

-- extra secundario por raridade, pra hat nao ser so numero de dano
local EXTRA_POR_RARIDADE = {
	incomum  = { extra = "capacidade", extraValor = 0.06 },
	raro     = { extra = "sorte",      extraValor = 0.10 },
	epico    = { extra = "capacidade", extraValor = 0.22 },
	lendario = { extra = "valor",      extraValor = 0.40 },
	secreto  = { extra = "sorte",      extraValor = 0.75 },
}

local ORDEM_TEMAS = { "chakra", "ki", "nichirin", "sombra", "mare", "serio" }
local ORDEM_RARIDADES = { "comum", "incomum", "raro", "epico", "lendario", "secreto" }

for iTema, tema in ipairs(ORDEM_TEMAS) do
	for iRar, raridade in ipairs(ORDEM_RARIDADES) do
		local id = tema .. "_" .. raridade
		local extra = EXTRA_POR_RARIDADE[raridade]
		table.insert(Config.Hats, {
			id = id,
			nome = Config.HatNomes[tema][raridade],
			tema = tema,
			raridade = raridade,
			-- ilha mais avancada e raridade mais alta batem mais forte
			dano = math.floor(1 * (3.1 ^ (iTema - 1)) * (2.4 ^ (iRar - 1))),
			extra = extra and extra.extra or nil,
			extraValor = extra and extra.extraValor or nil,
			assetId = Config.HatAssets[id] or 0,
		})
	end
end

-- hats de um tema (opcionalmente de uma raridade so)
function Config.hatsDoTema(tema, raridade)
	local t = {}
	for _, h in ipairs(Config.Hats) do
		if h.tema == tema and (raridade == nil or h.raridade == raridade) then
			table.insert(t, h)
		end
	end
	return t
end

Config.HAT_NIVEL_MAX = 15
Config.INVENTARIO_MAX = 300

function Config.hatDanoNoNivel(base, nivel) return base * (1 + 0.30 * (nivel - 1)) end
function Config.hatExtraNoNivel(base, nivel) return base * (1 + 0.20 * (nivel - 1)) end

function Config.custoFusao(raridade, nivel)
	local peso = { comum = 1, incomum = 3, raro = 10, epico = 40, lendario = 160, secreto = 700 }
	local p = peso[raridade] or 1
	return {
		moeda = math.floor(100 * p * (1.55 ^ (nivel - 1))),
		duplicatas = math.min(1 + math.floor((nivel - 1) / 2), 5),
	}
end

Config.SLOTS_BASE = 2   -- +1 por area desbloqueada alem da primeira

-- ---------- PETS ----------
-- velocidade e o bonus principal. extra e secundario.
-- o campo modelo aponta pra ServerStorage.Modelos quando voce montar os 3D.
Config.Pets = {
	{ id = "pedrinha",   nome = "Pedrinha",       raridade = "comum",    velocidade = 1.0,  modelo = "pet_pedrinha" },
	{ id = "morcego",    nome = "Morceguinho",    raridade = "comum",    velocidade = 1.4,  modelo = "pet_morcego" },
	{ id = "vagalume",   nome = "Vagalume",       raridade = "comum",    velocidade = 1.2,  extra = "sorte",  extraValor = 0.04, modelo = "pet_vagalume" },
	{ id = "lobo",       nome = "Lobo de Pedra",  raridade = "incomum",  velocidade = 2.6,  modelo = "pet_lobo" },
	{ id = "coruja",     nome = "Coruja Runica",  raridade = "incomum",  velocidade = 2.2,  extra = "valor",  extraValor = 0.06, modelo = "pet_coruja" },
	{ id = "golem_mini", nome = "Mini Golem",     raridade = "raro",     velocidade = 4.2,  extra = "dano",   extraValor = 12,   modelo = "pet_golem_mini" },
	{ id = "raposa",     nome = "Raposa Espirito",raridade = "raro",     velocidade = 5.0,  modelo = "pet_raposa" },
	{ id = "dragao",     nome = "Dragaozinho",    raridade = "epico",    velocidade = 7.5,  extra = "dano",   extraValor = 60,   modelo = "pet_dragao" },
	{ id = "fenix",      nome = "Fenix",          raridade = "epico",    velocidade = 8.2,  extra = "sorte",  extraValor = 0.18, modelo = "pet_fenix" },
	{ id = "kitsune",    nome = "Kitsune",        raridade = "lendario", velocidade = 13.0, extra = "valor",  extraValor = 0.35, modelo = "pet_kitsune" },
	{ id = "leviata",    nome = "Leviata",        raridade = "lendario", velocidade = 14.5, extra = "dano",   extraValor = 320,  modelo = "pet_leviata" },
	{ id = "ignis_pet",  nome = "Ignis Miniatura",raridade = "secreto",  velocidade = 22.0, extra = "dano",   extraValor = 1500, modelo = "pet_ignis" },
}

Config.PET_NIVEL_MAX = 15
Config.PET_SLOTS_BASE = 1     -- +1 por area desbloqueada alem da primeira
Config.PET_INVENTARIO_MAX = 200
Config.VELOCIDADE_BASE = 16

function Config.petVelocidadeNoNivel(base, nivel) return base * (1 + 0.28 * (nivel - 1)) end
function Config.petExtraNoNivel(base, nivel) return base * (1 + 0.20 * (nivel - 1)) end

function Config.custoFusaoPet(raridade, nivel)
	local peso = { comum = 1, incomum = 3, raro = 10, epico = 40, lendario = 160, secreto = 700 }
	local p = peso[raridade] or 1
	return {
		moeda = math.floor(120 * p * (1.55 ^ (nivel - 1))),
		duplicatas = math.min(1 + math.floor((nivel - 1) / 2), 5),
	}
end

function Config.petPorId(id)
	for _, p in ipairs(Config.Pets) do if p.id == id then return p end end
end

function Config.petsDaRaridade(raridade)
	local t = {}
	for _, p in ipairs(Config.Pets) do
		if p.raridade == raridade then table.insert(t, p) end
	end
	return t
end

-- ---------- GACHA DE OVOS ----------
-- um por area. quanto mais avancada, mais caro e melhor a tabela.
Config.OVO_MODELOS = { "ovo_shuriken", "ovo_hat", "ovo_sigil", "ovo_burst", "ovo_checker_tile_1" }

Config.Gachas = {
	[1] = { custo = 250,       pesos = { comum = 700, incomum = 260, raro = 38,  epico = 2,   lendario = 0,   secreto = 0 } },
	[2] = { custo = 2200,      pesos = { comum = 480, incomum = 380, raro = 120, epico = 19,  lendario = 1,   secreto = 0 } },
	[3] = { custo = 18000,     pesos = { comum = 240, incomum = 400, raro = 290, epico = 65,  lendario = 5,   secreto = 0 } },
	[4] = { custo = 150000,    pesos = { comum = 80,  incomum = 300, raro = 400, epico = 190, lendario = 29,  secreto = 1 } },
	[5] = { custo = 1300000,   pesos = { comum = 0,   incomum = 150, raro = 380, epico = 380, lendario = 85,  secreto = 5 } },
	[6] = { custo = 11000000,  pesos = { comum = 0,   incomum = 0,   raro = 260, epico = 460, lendario = 260, secreto = 20 } },
}

-- chance em porcentagem, pra mostrar na UI
function Config.chancesGacha(areaId)
	local g = Config.Gachas[areaId]
	if not g then return nil end
	local total = 0
	for _, p in pairs(g.pesos) do total = total + p end
	local lista = {}
	for chave, def in pairs(Config.Raridades) do
		local p = g.pesos[chave] or 0
		if p > 0 then
			table.insert(lista, { raridade = chave, nome = def.nome, cor = def.cor,
				pct = p / total * 100, ordem = def.ordem })
		end
	end
	table.sort(lista, function(a, b) return a.ordem < b.ordem end)
	return lista, total
end

-- hats disponiveis numa raridade
function Config.hatsDaRaridade(raridade)
	local t = {}
	for _, h in ipairs(Config.Hats) do
		if h.raridade == raridade then table.insert(t, h) end
	end
	return t
end

-- ---------- AREAS ----------
-- nomes de lugar, nao de franquia: reconhecivel sem virar alvo de DMCA
Config.Areas = {
	{ id = 1, tema = "chakra",   nome = "Vila da Folha",      rochaHP = 18,      bossHP = 900 },
	{ id = 2, tema = "ki",       nome = "Planeta Namekusei",  rochaHP = 160,     bossHP = 7500 },
	{ id = 3, tema = "nichirin", nome = "Monte Natagumo",     rochaHP = 1400,    bossHP = 60000 },
	{ id = 4, tema = "sombra",   nome = "Jardim das Sombras", rochaHP = 12000,   bossHP = 500000 },
	{ id = 5, tema = "mare",     nome = "Grand Line",         rochaHP = 100000,  bossHP = 4200000 },
	{ id = 6, tema = "serio",    nome = "Cidade Z",           rochaHP = 850000,  bossHP = 36000000 },
}

-- posicao e tamanho iguais pra todas, calculados a partir do id
Config.AREA_TAMANHO = Vector3.new(200, 1, 180)
Config.AREA_PASSO = 280
Config.AREA_Z_INICIAL = 235
Config.AREA_ROCHAS = 70

for _, a in ipairs(Config.Areas) do
	a.tamanho = Config.AREA_TAMANHO
	a.rochas = Config.AREA_ROCHAS
	a.centro = Vector3.new(0, 0, Config.AREA_Z_INICIAL + (a.id - 1) * Config.AREA_PASSO)
end

Config.RESPAWN_ROCHA = 1.2
Config.RESPAWN_CHEFE = 12
Config.COOLDOWN_GOLPE = 0.8

-- ---------- HELPERS ----------
function Config.varianteSorteada(rnd)
	local total = 0
	for _, v in ipairs(Config.Variantes) do total = total + v.peso end
	local roll = rnd:NextNumber() * total
	for _, v in ipairs(Config.Variantes) do
		roll = roll - v.peso
		if roll <= 0 then return v end
	end
	return Config.Variantes[1]
end

function Config.variantePorId(id)
	for _, v in ipairs(Config.Variantes) do
		if v.id == id then return v end
	end
end

-- id do item guardado na mochila: "chakra_incomum"
function Config.idMinerio(tema, variante) return tema .. "_" .. variante end

function Config.infoMinerio(id)
	local tema, variante = string.match(id, "^(%a+)_(%a+)$")
	local t = tema and Config.Temas[tema]
	local v = variante and Config.variantePorId(variante)
	if not t or not v then return nil end
	local nome = v.nome ~= "" and (t.nome .. " " .. v.nome) or t.nome
	return {
		nome = nome,
		valor = t.valor * v.valor,
		cor = t.cor,
		tema = tema,
		variante = variante,
	}
end

-- nome do modelo em ServerStorage.Modelos
function Config.modeloMinerio(tema, variante) return "minerio_" .. tema .. "_" .. variante end

function Config.picaretaPorId(id)
	for i, p in ipairs(Config.Picaretas) do if p.id == id then return p, i end end
end
function Config.mochilaPorId(id)
	for i, m in ipairs(Config.Mochilas) do if m.id == id then return m, i end end
end
function Config.hatPorId(id)
	for _, h in ipairs(Config.Hats) do if h.id == id then return h end end
end
function Config.areaPorId(id)
	for _, a in ipairs(Config.Areas) do if a.id == id then return a end end
end

return Config

