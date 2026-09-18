local Config = {}

-- ECONOMIA v3.1 (congelada): todos os numeros de balanceamento vem de EconomiaV31,
-- gerado por gerar.py a partir do simulador (usim3.py). Aqui so existe a ESTRUTURA do jogo
-- (ids, nomes, modelos). Nao coloque numero de economia neste arquivo.
local Eco = require(script.Parent:WaitForChild("EconomiaV31"))
Config.Eco = Eco
Config.ECON_VERSAO = Eco.VERSAO
Config.RAR_IDS = Eco.RAR_IDS
Config.RAR_INDICE = {}
for i, id in ipairs(Eco.RAR_IDS) do Config.RAR_INDICE[id] = i end

-- ---------- TEMAS / MINERIOS ----------
-- um tema por area. cada tema tem 3 variantes mineraveis + chefe.
-- BALANCEAMENTO (planilha Balanceamento_AnimeMining.xlsx / balance.py):
--   HP = golpes-alvo (4/7/14/120) x poder da 1a picareta do mundo x mult. medio de pets+hats
--   valor = valor do comum do mundo (x4.4 por mundo) x (1 / 3 / 8 / 60)
--   precos = coins/min do jogador medio no momento da compra x minutos-alvo
-- valor aqui = valor do minerio comum do mundo (usado em textos e referencias)
Config.Temas = {
	chakra   = { nome = "Chakra",   cor = Color3.fromRGB(90, 175, 255) },
	ki       = { nome = "Ki",       cor = Color3.fromRGB(255, 190, 60) },
	nichirin = { nome = "Nichirin", cor = Color3.fromRGB(90, 220, 190) },
	sombra   = { nome = "Sombra",   cor = Color3.fromRGB(150, 90, 230) },
	mare     = { nome = "Maré",     cor = Color3.fromRGB(70, 200, 235) },
	serio    = { nome = "Sério",    cor = Color3.fromRGB(255, 110, 80) },
}

-- 5 tipos de minerio (+ chefe global). hp/espaco/chance de hat/sorte vem da economia.
-- ids "epica" mantido por compatibilidade com saves e modelos. raro e lendaria reaproveitam
-- os modelos de incomum e epica com cor e brilho proprios (ver AreaBuilder).
local TIPOS = {
	{ id = "comum",    nome = "",         eco = "comum",    modelo = "comum",   ore = "Common",   cor = nil },
	{ id = "incomum",  nome = "Incomum",  eco = "incomum",  modelo = "incomum", ore = "Uncommon", cor = Color3.fromRGB(90, 205, 110) },
	{ id = "raro",     nome = "Raro",     eco = "raro",     modelo = "incomum", ore = "Uncommon", cor = Color3.fromRGB(80, 150, 255) },
	{ id = "epica",    nome = "Épico",    eco = "epico",    modelo = "epica",   ore = "Epic",     cor = Color3.fromRGB(189, 114, 255) },
	{ id = "lendaria", nome = "Lendário", eco = "lendario", modelo = "epica",   ore = "Epic",     cor = Color3.fromRGB(255, 190, 40) },
}
Config.Variantes = {}
for i, t in ipairs(TIPOS) do
	table.insert(Config.Variantes, {
		id = t.id, nome = t.nome, ordem = i, modelo = t.modelo, oreRarity = t.ore, cor = t.cor,
		hp = Eco.HP_REL[t.eco], peso = Eco.SPAWN_PARTE[t.eco], espaco = Eco.ESPACO[i],
		hatChance = Eco.HAT_CHANCE[i], hatSorte = Eco.HAT_SORTE[i],
	})
end

-- ---------- PICARETAS ----------
-- a picareta MULTIPLICA o dano dos hats e define o intervalo entre golpes
Config.Picaretas = {
	{ id = "enferrujada", nome = "Picareta Enferrujada",   mundo = 1, modelo = "enferrujada" },
	{ id = "ferro",       nome = "Picareta de Ferro",      mundo = 1, modelo = "ferro" },
	{ id = "kunai",       nome = "Picareta Kunai",         mundo = 1, modelo = "ferro" },
	{ id = "aco",         nome = "Picareta de Aço",        mundo = 1, modelo = "aco" },
	{ id = "capsula",     nome = "Picareta Cápsula",       mundo = 2, modelo = "aco" },
	{ id = "rubi",        nome = "Picareta de Rubi",       mundo = 2, modelo = "rubi" },
	{ id = "saiyajin",    nome = "Picareta Saiyajin",      mundo = 2, modelo = "rubi" },
	{ id = "ki_supremo",  nome = "Picareta Ki Supremo",    mundo = 2, modelo = "rubi" },
	{ id = "nichirin",    nome = "Picareta Nichirin",      mundo = 3, modelo = "obsidiana" },
	{ id = "obsidiana",   nome = "Picareta de Obsidiana",  mundo = 3, modelo = "obsidiana" },
	{ id = "respiracao",  nome = "Picareta da Respiração", mundo = 3, modelo = "obsidiana" },
	{ id = "hashira",     nome = "Picareta Hashira",       mundo = 3, modelo = "runica" },
	{ id = "sombria",     nome = "Picareta Sombria",       mundo = 4, modelo = "runica" },
	{ id = "runica",      nome = "Picareta Rúnica",        mundo = 4, modelo = "runica" },
	{ id = "vazio",       nome = "Picareta do Vazio",      mundo = 4, modelo = "runica" },
	{ id = "eminence",    nome = "Picareta Eminence",      mundo = 4, modelo = "estelar" },
	{ id = "maritima",    nome = "Picareta Marítima",      mundo = 5, modelo = "estelar" },
	{ id = "estelar",     nome = "Picareta Estelar",       mundo = 5, modelo = "estelar" },
	{ id = "haki",        nome = "Picareta Haki",          mundo = 5, modelo = "estelar" },
	{ id = "yonkou",      nome = "Picareta Yonkou",        mundo = 5, modelo = "ignis" },
	{ id = "heroica",     nome = "Picareta Heroica",       mundo = 6, modelo = "ignis" },
	{ id = "ignis",       nome = "Picareta de Ignis",      mundo = 6, modelo = "ignis" },
	{ id = "ciborgue",    nome = "Picareta Ciborgue",      mundo = 6, modelo = "ignis" },
	{ id = "soco_serio",  nome = "Picareta do Soco Sério", mundo = 6, modelo = "ignis" },
}
for i, p in ipairs(Config.Picaretas) do
	local e = Eco.PICARETAS[i]
	p.mult, p.intervalo, p.custo = e.mult, e.intervalo, e.custo
	p.dano = e.mult -- compatibilidade: telas antigas que ordenam por "dano"
end

-- ---------- MOCHILAS ----------
Config.Mochilas = {
	{ id = "saco_pano",     nome = "Saco de Pano",        mundo = 1 },
	{ id = "couro",         nome = "Mochila de Couro",    mundo = 1 },
	{ id = "reforcada",     nome = "Mochila Reforçada",   mundo = 2 },
	{ id = "capsula",       nome = "Cápsula Hoi-Poi",     mundo = 2 },
	{ id = "ferro",         nome = "Mochila de Ferro",    mundo = 3 },
	{ id = "bau_demoniaco", nome = "Baú Demoníaco",       mundo = 3 },
	{ id = "runica",        nome = "Mochila Rúnica",      mundo = 4 },
	{ id = "sombria",       nome = "Mochila das Sombras", mundo = 4 },
	{ id = "abissal",       nome = "Mochila Abissal",     mundo = 5 },
	{ id = "bau_pirata",    nome = "Baú Pirata",          mundo = 5 },
	{ id = "estelar",       nome = "Mochila Estelar",     mundo = 6 },
	{ id = "ignis",         nome = "Mochila de Ignis",    mundo = 6 },
}
for i, m in ipairs(Config.Mochilas) do
	m.capacidade, m.custo = Eco.MOCHILAS[i].capacidade, Eco.MOCHILAS[i].custo
end

-- ---------- HATS ----------
Config.Raridades = {
	comum    = { nome = "Comum",    cor = Color3.fromRGB(175, 175, 180), peso = 1000, ordem = 1 },
	incomum  = { nome = "Incomum",  cor = Color3.fromRGB(90, 205, 110),  peso = 340,  ordem = 2 },
	raro     = { nome = "Raro",     cor = Color3.fromRGB(80, 150, 255),  peso = 90,   ordem = 3 },
	epico    = { nome = "Épico",    cor = Color3.fromRGB(185, 100, 255), peso = 20,   ordem = 4 },
	lendario = { nome = "Lendário", cor = Color3.fromRGB(255, 175, 40),  peso = 4,    ordem = 5 },
	mitico   = { nome = "Mítico",   cor = Color3.fromRGB(255, 55, 55),   peso = 2,    ordem = 6 },
	-- secreto e preto; corTexto e usada onde a cor vira texto ou barra (preto some no fundo escuro)
	secreto  = { nome = "Secreto",  cor = Color3.fromRGB(16, 16, 20),   corTexto = Color3.fromRGB(235, 235, 240), peso = 1, ordem = 7 },
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
-- ---------- CATALOGO DE HATS POR ILHA ----------
-- Acessorios do catalogo da Roblox (UGC) enviados pelo dono do jogo. O HatVisual veste com InsertService.
-- A RARIDADE define o dano (economia v3.1: base do mundo x multiplicador da raridade); o nome/visual e livre.
-- Pra mudar a raridade de um hat, troque o terceiro campo. Varios hats na mesma raridade dividem a chance.
-- Ordem das raridades: comum, incomum, raro, epico, lendario, mitico, secreto.
Config.HatCatalogo = {
	chakra = { -- Vila da Folha
		{ "Ninja Headband Naruto", 125125413956986, "comum" },
		{ "Sakura", 119800366008474, "comum" },
		{ "Rock Lee", 127978986091636, "comum" },
		{ "Naruto", 74918048277154, "incomum" },
		{ "Tsunade", 74456774114586, "incomum" },
		{ "Kakashi", 106490972825856, "raro" },
		{ "Obito", 17538575020, "raro" },
		{ "Obito Tobi", 132375430855836, "epico" },
		{ "Sasuke", 70959483026517, "epico" },
		{ "Helmet Susanoo Itachi", 18159187047, "lendario" },
		{ "Pain Hair with Headband", 122061309107006, "mitico" },
		{ "Madara", 96742478967390, "secreto" },
	},
	ki = { -- Planeta Namekusei
		{ "Dragon Ball", 89866005328437, "comum" },
		{ "Kuririn", 103188899582798, "comum" },
		{ "Master Kame", 124981574739172, "comum" },
		{ "Goku", 94461657872694, "incomum" },
		{ "Goku Classico", 85673926407962, "incomum" },
		{ "SSJ Goku", 75708618101006, "incomum" },
		{ "Goku SSJ3", 140100771028615, "raro" },
		{ "Beerus Dragon Ball Super Head", 140224407015195, "raro" },
		{ "Broly", 87208871210868, "epico" },
		{ "Goku SSJ4", 86070099711035, "epico" },
		{ "Goku SSJ5", 122442369782268, "lendario" },
		{ "Goku MUI Hair", 121964353549674, "mitico" },
		{ "Zeno Omni King", 17863861873, "secreto" },
	},
	nichirin = { -- Monte Natagumo
		{ "Tanjiro", 116486347108244, "comum" },
		{ "Tanjiro Kamado Earrings", 120687579945328, "comum" },
		{ "Female Demon Slayer Hero", 71306705366888, "comum" },
		{ "Tanjiro Classico", 75461258228509, "incomum" },
		{ "Nezuko Box", 138490892546928, "incomum" },
		{ "Zenitsu Agatsuma", 108730849468814, "incomum" },
		{ "Inosuke", 132914418471356, "raro" },
		{ "Shinobu Kocho Hair", 82251339516297, "raro" },
		{ "Mitsuri Hair Braids", 84425473562217, "epico" },
		{ "Nezuko Transformation Head", 136805686559515, "epico" },
		{ "Gyomei Hair", 134843809698787, "lendario" },
		{ "Rengoku", 89791894813363, "mitico" },
		{ "Yoriichi", 134917791668741, "secreto" },
	},
	sombra = { -- Jardim das Sombras
		{ "John Smith", 18292000158, "comum" },
		{ "Cid", 132214824986127, "comum" },
		{ "Cid Classico", 114589064741078, "comum" },
		{ "Delta Hair", 101683316441256, "incomum" },
		{ "Cid Shadow", 108645413552891, "incomum" },
		{ "Zeta Eminence in Shadow", 112217132240254, "raro" },
		{ "Beta Eminence in Shadow", 126473787951515, "raro" },
		{ "Delta", 119442576937551, "epico" },
		{ "Delta Eminence Hair", 136544800238717, "epico" },
		{ "Alpha", 104576139547604, "lendario" },
		{ "Lelouch Glowing", 87369527046079, "mitico" },
		{ "Shadow Cid", 134031289633258, "secreto" },
	},
	mare = { -- Grand Line
		{ "Nami Timeskip", 110596452512324, "comum" },
		{ "Arlong", 18960149540, "comum" },
		{ "Loki", 121848907314744, "comum" },
		{ "Law Head", 18638499839, "comum" },
		{ "Luffy Straw Hat", 103025593029630, "incomum" },
		{ "Zoro Hair Skypiea", 71946982701165, "incomum" },
		{ "Sabo", 137290460120285, "incomum" },
		{ "Ace", 92678685465484, "raro" },
		{ "Zoro Head", 108241581680266, "raro" },
		{ "Katakuri Head", 109197339854421, "raro" },
		{ "Akainu Hat", 18988881246, "epico" },
		{ "Bartholomew Kuma Full Head", 86710698888354, "epico" },
		{ "Whitebeard", 87578732736983, "lendario" },
		{ "Dracule Mihawk", 94492598054768, "lendario" },
		{ "Luffy", 132460037987346, "mitico" },
		{ "Roger", 117009461004387, "secreto" },
	},
	serio = { -- Cidade Z
		{ "King", 125846359832552, "comum" },
		{ "King Classico", 138690804153276, "comum" },
		{ "Saitama Face", 18809885128, "comum" },
		{ "Genos Hair", 73478651514526, "incomum" },
		{ "Sonic", 80131551719555, "incomum" },
		{ "Blast Cape", 90976012124542, "incomum" },
		{ "Tatsumaki Hair", 133385810578741, "raro" },
		{ "Garou", 70921037483733, "raro" },
		{ "Boros", 17784909337, "epico" },
		{ "Boros Classico", 126437668232450, "epico" },
		{ "Boros Supremo", 109108961316185, "lendario" },
		{ "Blast", 17811301642, "lendario" },
		{ "Strongest One Punch Hero", 16320044698, "mitico" },
		{ "Saitama", 114645219107971, "secreto" },
	},
}

-- dano do hat = base do mundo do hat x multiplicador da raridade x (1 + coef x (nivel - 1))
-- (hats nao tem extras de capacidade/sorte/valor: a economia v3.1 nao os simula)
local ORDEM_TEMAS = { "chakra", "ki", "nichirin", "sombra", "mare", "serio" }
local ORDEM_TEMA = { chakra = 1, ki = 2, nichirin = 3, sombra = 4, mare = 5, serio = 6 }
Config.ORDEM_TEMA = ORDEM_TEMA
Config.HatAssets = {}

for iTema, tema in ipairs(ORDEM_TEMAS) do
	for _, entrada in ipairs(Config.HatCatalogo[tema]) do
		local nome, assetId, raridade = entrada[1], entrada[2], entrada[3]
		local iRar = Config.RAR_INDICE[raridade]
		assert(iRar, "raridade invalida no catalogo de hats: " .. tostring(raridade))
		local id = tema .. "_" .. tostring(assetId)   -- id estavel: nao muda se a ordem da lista mudar
		Config.HatAssets[id] = assetId
		table.insert(Config.Hats, {
			id = id,
			nome = nome,
			tema = tema,
			mundo = iTema,
			raridade = raridade,
			dano = Eco.BASE_HAT[iTema] * Eco.RAR_MULT[iRar],
			assetId = assetId,
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

Config.HAT_NIVEL_MAX = Eco.NIVEL_MAX
Config.HAT_NIVEL_DROP_MAX = Eco.NIVEL_DROP_MAX
Config.INVENTARIO_MAX = Eco.INVENTARIO   -- hats; o passe +50 Inventario soma em PlayerData
Config.INVENTARIO_POR_AREA = 0

function Config.capacidadeHats() return Config.INVENTARIO_MAX end

function Config.hatDanoNoNivel(base, nivel) return base * (1 + Eco.NIVEL_COEF * ((nivel or 1) - 1)) end
function Config.hatExtraNoNivel() return 0 end

-- slots de hat pelo mundo mais avancado desbloqueado
function Config.slotsHat(maiorArea) return Eco.SLOTS_HAT[math.clamp(maiorArea or 1, 1, #Eco.SLOTS_HAT)] end

-- ---------- SORTE (mesma regra do simulador) ----------
-- aplicarLucky: multiplica EXATAMENTE a chance de cada raridade >= Epico e tira a diferenca do Comum.
function Config.aplicarLucky(dist, mult)
	if not mult or mult == 1 then return dist end
	local nova, extra = table.clone(dist), 0
	for i = Eco.LUCKY_A_PARTIR_RAR, #dist do
		nova[i] = dist[i] * mult
		extra += nova[i] - dist[i]
	end
	nova[1] = math.max(0, dist[1] - extra)
	return nova
end
-- sorte do tipo de minerio: multiplica o peso de toda raridade acima de Comum e renormaliza
function Config.normalizarSorte(dist, sorte)
	local pesos, total = {}, 0
	for i, p in ipairs(dist) do
		pesos[i] = i == 1 and p or p * (sorte or 1)
		total += pesos[i]
	end
	for i = 1, #pesos do pesos[i] /= total end
	return pesos
end
function Config.sortearIndice(rnd, dist)
	local x = rnd:NextNumber()
	for i, p in ipairs(dist) do
		x -= p
		if x <= 0 then return i end
	end
	return #dist
end

-- ---------- FUSAO DE HATS (estilo Anime Fighters) ----------
-- cada hat sacrificado vira XP: base da raridade x (1 + 0.4 x mundo) x 1.05^(nivel - 1)
function Config.hatXpComoComida(def, inst)
	local r = Config.RAR_INDICE[def.raridade] or 1
	local w = (ORDEM_TEMA[def.tema] or 1) - 1
	local n = (inst and inst.nivel) or 1
	return math.floor(Eco.HAT_XP_BASE[r] * (1 + 0.4 * w) * 1.05 ^ (n - 1))
end
function Config.hatXpParaSubir(def, nivel)
	local r = Config.RAR_INDICE[def.raridade] or 1
	local w = (ORDEM_TEMA[def.tema] or 1) - 1
	return math.floor(20 * Eco.HAT_XP_RAR[r] * (1 + 0.3 * w) * 1.12 ^ ((nivel or 1) - 1))
end
-- aplica XP num hat (tabela {nivel, xp, xpTotal}); devolve niveis ganhos
function Config.hatAplicarXp(def, inst, xp)
	local ganhos = 0
	inst.xp = (inst.xp or 0) + xp
	inst.xpTotal = (inst.xpTotal or 0) + xp
	while inst.nivel < Config.HAT_NIVEL_MAX and inst.xp >= Config.hatXpParaSubir(def, inst.nivel) do
		inst.xp -= Config.hatXpParaSubir(def, inst.nivel)
		inst.nivel += 1
		ganhos += 1
	end
	if inst.nivel >= Config.HAT_NIVEL_MAX then inst.xp = 0 end
	return ganhos
end

function Config.custoFusao(raridade, nivel)
	return { moeda = 0, duplicatas = 0 }
end

Config.SLOTS_BASE = 2   -- +1 por area desbloqueada alem da primeira

-- ---------- PETS ----------
-- cada area tem a propria colecao de personagens (modelo em ReplicatedStorage.PreviewModelos.Pets[id]).
-- o gacha de uma area so sorteia pets daquela area. Reino das Sombras (4) nao tem gacha.
-- pet = bonus % de DANO (raridade x mundo x nivel) + LEVEL BONUS (nivel com que os hats caem).
-- pets nao multiplicam moedas na economia v3.1. velocidade continua pequena e com teto.
local PET_VEL = { comum = 0.4, incomum = 0.6, raro = 0.9, epico = 1.2, lendario = 1.6, mitico = 2.0, secreto = 2.5 }

local PETS_POR_AREA = {
	[1] = { -- Vila da Folha
		{ "naruto",   "Naruto",   "comum" },
		{ "sakura",   "Sakura",   "incomum" },
		{ "rock_lee", "Rock Lee", "raro" },
		{ "itachi",   "Itachi",   "epico" },
		{ "kakashi",  "Kakashi",  "lendario" },
		{ "madara",   "Madara",   "mitico" },
		{ "sasuke",   "Sasuke",   "secreto" },
	},
	[2] = { -- Planeta Namekusei
		{ "goten",        "Goten",          "comum" },
		{ "piccolo",      "Piccolo",        "incomum" },
		{ "kuririn",      "Kuririn",        "raro" },
		{ "majin_boo",    "Majin Boo",      "epico" },
		{ "vegeta",       "Vegeta",         "lendario" },
		{ "goku",         "Goku",           "mitico" },
		{ "goku_ssj_god", "Goku SSJ God",   "secreto" },
	},
	[3] = { -- Monte Natagumo
		{ "tanjiro",  "Tanjiro",  "comum" },
		{ "zenitsu",  "Zenitsu",  "raro" },
		{ "inosuke",  "Inosuke",  "epico" },
		{ "tomioka",  "Tomioka",  "lendario" },
		{ "muzan",    "Muzan",    "mitico" },
		{ "yoriichi", "Yoriichi", "secreto" },
	},
	[5] = { -- Grand Line
		{ "usopp",  "Usopp",  "comum" },
		{ "sanji",  "Sanji",  "raro" },
		{ "nami",   "Nami",   "epico" },
		{ "zoro",   "Zoro",   "lendario" },
		{ "luffy",  "Luffy",  "mitico" },
		{ "mihawk", "Mihawk", "secreto" },
	},
	[6] = { -- Cidade Z
		{ "suiryu",         "Suiryu",         "comum" },
		{ "atomic_samurai", "Atomic Samurai", "raro" },
		{ "tatsumaki",      "Tatsumaki",      "epico" },
		{ "metal_bat",      "Metal Bat",      "lendario" },
		{ "boros",          "Boros",          "mitico" },
		{ "saitama",        "Saitama",        "secreto" },
	},
}

Config.Pets = {}
for areaId = 1, 6 do
	for _, p in ipairs(PETS_POR_AREA[areaId] or {}) do
		local r = Config.RAR_INDICE[p[3]]
		table.insert(Config.Pets, {
			id = p[1], nome = p[2], raridade = p[3], area = areaId,
			bonusDano = Eco.PET_BONUS[r] * (1 + Eco.PET_BONUS_MUNDO * (areaId - 1)),
			bonusMoeda = 0,
			levelBonus = Eco.PET_LB[r],
			velocidade = PET_VEL[p[3]] * (1 + 0.1 * (areaId - 1)),
		})
	end
end

-- retrato 2D dos personagens nos cards (busto = grade, corpo = painel de detalhe).
-- pets com roupa em camadas precisam disso: ViewportFrame nao deforma layered clothing.
Config.PetArte = {
	naruto          = { busto = "rbxassetid://110178261080797", corpo = "rbxassetid://124272353297978" },
	sakura          = { busto = "rbxassetid://128544426883928", corpo = "rbxassetid://115636259129083" },
	rock_lee        = { busto = "rbxassetid://112009144569110", corpo = "rbxassetid://94163413715651" },
	itachi          = { busto = "rbxassetid://136726988718866", corpo = "rbxassetid://87331029272074" },
	kakashi         = { busto = "rbxassetid://101241966476297", corpo = "rbxassetid://72282019042075" },
	madara          = { busto = "rbxassetid://99855140449535", corpo = "rbxassetid://106406917127696" },
	sasuke          = { busto = "rbxassetid://114158373067410", corpo = "rbxassetid://103890128525964" },
	goten           = { busto = "rbxassetid://126567414640629", corpo = "rbxassetid://118740737364465" },
	piccolo         = { busto = "rbxassetid://98676801687808", corpo = "rbxassetid://133181389676650" },
	kuririn         = { busto = "rbxassetid://138033298203189", corpo = "rbxassetid://80125825278710" },
	majin_boo       = { busto = "rbxassetid://98962411012321", corpo = "rbxassetid://134744195682209" },
	vegeta          = { busto = "rbxassetid://128048313485992", corpo = "rbxassetid://109431357574847" },
	goku            = { busto = "rbxassetid://85612578933460", corpo = "rbxassetid://99198496876131" },
	goku_ssj_god    = { busto = "rbxassetid://140109378719063", corpo = "rbxassetid://139641078659693" },
	tanjiro         = { busto = "rbxassetid://130850262305841", corpo = "rbxassetid://82405172705302" },
	zenitsu         = { busto = "rbxassetid://90612353386699", corpo = "rbxassetid://124328798422987" },
	inosuke         = { busto = "rbxassetid://126925387599669", corpo = "rbxassetid://75531157764030" },
	tomioka         = { busto = "rbxassetid://124130841911780", corpo = "rbxassetid://89438896826307" },
	muzan           = { busto = "rbxassetid://126402076522827", corpo = "rbxassetid://136358139677268" },
	yoriichi        = { busto = "rbxassetid://107663513720922", corpo = "rbxassetid://82972008734911" },
	usopp           = { busto = "rbxassetid://109302129113835", corpo = "rbxassetid://85726010479366" },
	sanji           = { busto = "rbxassetid://94407869896683", corpo = "rbxassetid://73954038781535" },
	nami            = { busto = "rbxassetid://101693114905599", corpo = "rbxassetid://105621082022680" },
	zoro            = { busto = "rbxassetid://124459545651133", corpo = "rbxassetid://122030337460037" },
	luffy           = { busto = "rbxassetid://85878027295805", corpo = "rbxassetid://74127517501669" },
	mihawk          = { busto = "rbxassetid://131718207503704", corpo = "rbxassetid://129419630896492" },
	suiryu          = { busto = "rbxassetid://133224832682893", corpo = "rbxassetid://137389476739274" },
	atomic_samurai  = { busto = "rbxassetid://124808866382055", corpo = "rbxassetid://100980276947735" },
	tatsumaki       = { busto = "rbxassetid://121288372154863", corpo = "rbxassetid://99545549717591" },
	metal_bat       = { busto = "rbxassetid://98897987843362", corpo = "rbxassetid://86375864076987" },
	boros           = { busto = "rbxassetid://88742950513735", corpo = "rbxassetid://138980515003596" },
	saitama         = { busto = "rbxassetid://88869979562574", corpo = "rbxassetid://93765430775367" },
}

Config.PET_NIVEL_MAX = Eco.PET_NIVEL_MAX
Config.PET_SLOTS_BASE = Eco.PET_SLOTS
Config.PET_INVENTARIO_MAX = Eco.INVENTARIO  -- o passe +50 Inventario soma em PlayerData
Config.PET_INVENTARIO_POR_AREA = 0
function Config.capacidadePets() return Config.PET_INVENTARIO_MAX end

-- bonus de um pet no nivel (0.18 = +18%)
function Config.petBonusDano(def, nivel) return def.bonusDano * (1 + Eco.PET_BONUS_NIVEL * ((nivel or 1) - 1)) end
function Config.petBonusMoeda() return 0 end
function Config.petLevelBonus(def) return def.levelBonus or 0 end

-- ---------- ALIMENTAR (FEED) - v3.1.1 ----------
-- cada personagem usado de comida vira XP: raridade x mundo x nivel dele.
-- cada nivel do pet alvo exige XP crescente (raridade e mundo do alvo). Numeros: EconomiaV31 (PET_XP_*).
function Config.petXpComoComida(def, inst)
	local nivel = type(inst) == "table" and inst.nivel or inst or 1
	local r = Config.RAR_INDICE[def.raridade] or 1
	return math.floor(Eco.PET_XP_COMIDA[r] * (1 + Eco.PET_XP_MUNDO * ((def.area or 1) - 1)) * (1 + Eco.PET_XP_NIVEL_COMIDA * (nivel - 1)))
end
function Config.petXpParaSubir(def, nivel)
	local r = Config.RAR_INDICE[def.raridade] or 1
	return math.floor(Eco.PET_XP_BASE * Eco.PET_XP_RAR[r] * (1 + Eco.PET_XP_MUNDO * ((def.area or 1) - 1)) * Eco.PET_XP_CRESC ^ ((nivel or 1) - 1))
end
function Config.petAplicarXp(def, inst, xp)
	local ganhos = 0
	inst.xp = (inst.xp or 0) + xp
	inst.xpTotal = (inst.xpTotal or 0) + xp
	while inst.nivel < Config.PET_NIVEL_MAX and inst.xp >= Config.petXpParaSubir(def, inst.nivel) do
		inst.xp -= Config.petXpParaSubir(def, inst.nivel)
		inst.nivel += 1
		ganhos += 1
	end
	if inst.nivel >= Config.PET_NIVEL_MAX then inst.xp = 0 end
	return ganhos
end
Config.VELOCIDADE_BASE = 16
Config.VELOCIDADE_PETS_MAX = 10   -- soma maxima que os pets podem dar (andar no maximo a 26)
function Config.petVelocidade(def, nivel) return (def.velocidade or 0) * (1 + 0.03 * ((nivel or 1) - 1)) end

-- ---------- SPAWN DE MINERIOS (energia da ilha) ----------
-- sem sorte. cada ilha tem 3 barras de energia, compartilhadas por todos os jogadores do servidor:
--   quebrar COMUM   enche a barra de INCOMUM com 1   (a vida relativa do comum)
--   quebrar INCOMUM enche a barra de EPICO   com 4   (incomum tem 4x a vida)
--   quebrar EPICO   enche a barra de CHEFE   com 16  (epico tem 16x a vida)
-- barra cheia -> nasce 1 daquele tipo e a barra desconta o custo (sobra continua).
-- custo = custo base x (1 + porVivo x quantos daquele tipo ja estao vivos na ilha):
-- com muitos raros parados a ilha nao lota; quem quebra os raros acelera os proximos.
-- comum sempre renasce. servidor novo ja comeca com um pouco de cada.
-- ritmo base: ~8 comuns = 1 incomum, ~6 incomuns = 1 epico, ~4 epicos = 1 chefe.
-- inspirado no Unboxing Simulator:
--  * AMPLIFICAR: barra cheia transforma o minerio do nivel de baixo mais perto de quem quebrou
--    (como a Box Amplifier). sem nenhum por perto, nasce um novo num ponto sorteado.
--  * EFEITOS: tambem por barra, sem sorte. o proximo minerio que nascer/amplificar vem com efeito
--    e da moedas extras na hora (valor do minerio x mult).
Config.SPAWN = {
	raioAmplificar = 70,
	efeitos = {
		dourado  = { vem = "qualquer", custo = 40, mult = 5,  nome = "DOURADO",   cor = Color3.fromRGB(255, 200, 40) },
		arcoiris = { vem = "epica",    custo = 6,  mult = 20, nome = "ARCO-ÍRIS", cor = Color3.fromRGB(255, 90, 230) },
	},
	-- escada: cada quebra enche a barra do tipo de cima com o HP relativo do minerio quebrado.
	-- custos calibrados para as quebras seguirem a SPAWN_PARTE da economia (com amplificacao):
	-- custo[k] = quebras[k-1] x HP_REL[k-1] / nascimentos[k]
	barras = {},
	energiaPorQuebra = {},
	inicial = { incomum = 8, raro = 3, epica = 1, lendaria = 0 },  -- o resto vira comum
	minerios = 70,           -- minerios vivos por ilha (da pra ~5 jogadores minerarem juntos)
	distanciaMin = 9,        -- studs entre minerios
	distanciaChefe = 20,     -- studs livres em volta do chefe
}
do
	local vs = Config.Variantes
	local quebras = {}
	for i, v in ipairs(vs) do quebras[i] = v.peso end
	local nascem = {}
	nascem[#vs] = quebras[#vs]
	for i = #vs - 1, 2, -1 do nascem[i] = quebras[i] + nascem[i + 1] end
	for i = 2, #vs do
		Config.SPAWN.barras[vs[i].id] = { vem = vs[i - 1].id, custo = quebras[i - 1] * vs[i - 1].hp / nascem[i], porVivo = 0.05, ordem = i }
	end
	for _, v in ipairs(vs) do Config.SPAWN.energiaPorQuebra[v.id] = v.hp end
end

function Config.petVelocidadeNoNivel(base, nivel) return base * (1 + 0.28 * (nivel - 1)) end
function Config.petExtraNoNivel(base, nivel) return base * (1 + 0.20 * (nivel - 1)) end

function Config.custoFusaoPet(raridade, nivel)
	local peso = { comum = 1, incomum = 3, raro = 10, epico = 40, lendario = 160, mitico = 350, secreto = 700 }
	local p = peso[raridade] or 1
	return {
		moeda = math.floor(120 * p * (1.55 ^ (nivel - 1))),
		duplicatas = math.min(1 + math.floor((nivel - 1) / 2), 5),
	}
end

function Config.petPorId(id)
	for _, p in ipairs(Config.Pets) do if p.id == id then return p end end
end

-- pets de uma raridade; com areaId, so os daquela area
function Config.petsDaRaridade(raridade, areaId)
	local t = {}
	for _, p in ipairs(Config.Pets) do
		if p.raridade == raridade and (areaId == nil or p.area == areaId) then table.insert(t, p) end
	end
	return t
end

-- ---------- GACHA DE OVOS ----------
-- um por area. quanto mais avancada, mais caro e melhor a tabela.
Config.OVO_MODELOS = { "ovo_shuriken", "ovo_hat", "ovo_sigil", "ovo_burst", "ovo_checker_tile_1" }

-- toda area usa a mesma tabela de pesos; raridade sem personagem na area fica fora do sorteio.
-- area 4 (Jardim das Sombras) nao tem gacha.
Config.Gachas = {}
for areaId = 1, 6 do
	if Eco.GACHA_MUNDO[areaId] then Config.Gachas[areaId] = { custo = Eco.GACHA_GIRO[areaId] } end
end
Config.PITY_LENDARIO = Eco.PITY_LENDARIO
Config.PITY_MITICO = Eco.PITY_MITICO
Config.PRIMEIRO_GIRO_MIN_RAR = Eco.PRIMEIRO_GIRO_MIN_RAR

-- distribuicao por INDICE de raridade numa area (com Lucky). raridade sem personagem na area
-- cai para a raridade de baixo mais proxima que tenha personagem (Lendario+ nunca muda).
function Config.distGacha(areaId, luckyMult)
	if not Config.Gachas[areaId] then return nil end
	local base = Config.aplicarLucky(Eco.PET_DIST, luckyMult)
	local dist = table.create(#base, 0)
	for i, p in ipairs(base) do
		local alvo = i
		while alvo > 1 and #Config.petsDaRaridade(Eco.RAR_IDS[alvo], areaId) == 0 do alvo -= 1 end
		dist[alvo] += p
	end
	return dist
end

-- compatibilidade: pesos por chave de raridade (so as que tem personagem)
function Config.pesosGacha(areaId, luckyMult)
	local dist = Config.distGacha(areaId, luckyMult)
	if not dist then return nil end
	local t = {}
	for i, p in ipairs(dist) do if p > 0 then t[Eco.RAR_IDS[i]] = p end end
	return t
end

-- chance em porcentagem, pra mostrar na UI (ja com Lucky/boost aplicados)
function Config.chancesGacha(areaId, luckyMult)
	local dist = Config.distGacha(areaId, luckyMult)
	if not dist then return nil end
	local lista = {}
	for i, p in ipairs(dist) do
		if p > 0 then
			local chave = Eco.RAR_IDS[i]
			local def = Config.Raridades[chave]
			table.insert(lista, { raridade = chave, nome = def.nome, cor = def.cor, pct = p * 100, ordem = def.ordem })
		end
	end
	table.sort(lista, function(a, b) return a.ordem < b.ordem end)
	return lista, 1
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
	{ id = 1, tema = "chakra",   nome = "Vila da Folha" },
	{ id = 2, tema = "ki",       nome = "Planeta Namekusei" },
	{ id = 3, tema = "nichirin", nome = "Monte Natagumo" },
	{ id = 4, tema = "sombra",   nome = "Jardim das Sombras" },
	{ id = 5, tema = "mare",     nome = "Grand Line" },
	{ id = 6, tema = "serio",    nome = "Cidade Z" },
}
for i, a in ipairs(Config.Areas) do
	local hc = Eco.HP_COMUM[i]
	a.custo = Eco.PORTAIS[i]
	a.espaco = Eco.ESPACO_MUNDO[i]
	a.hp, a.valores = {}, {}
	for _, v in ipairs(Config.Variantes) do
		a.hp[v.id] = hc * v.hp
		a.valores[v.id] = hc * v.hp * Eco.MOEDA_POR_HP
	end
	a.hp.super = hc * Eco.HP_REL.chefe
	a.valores.super = a.hp.super * Eco.MOEDA_POR_HP * Eco.CHEFE_MOEDA  -- por participante
	a.rochaHP = a.hp.comum      -- compatibilidade
	a.bossHP = a.hp.super
end

-- moedas/min do jogador medio em cada mundo (simulador): base de packs, Daily e missoes
Config.CPM_REFERENCIA = Eco.MOEDAS_POR_MINUTO_MEDIO
local function arredondar(x)
	if x < 10 then return math.max(1, math.floor(x + 0.5)) end
	local e = 10 ^ (math.floor(math.log10(x)) - 1)
	return math.floor(x / e + 0.5) * e
end
Config.arredondar = arredondar
function Config.moedasDeMinutos(areaId, minutos)
	return arredondar(Eco.MOEDAS_POR_MINUTO_MEDIO[math.clamp(areaId or 1, 1, 6)] * minutos)
end

-- ---------- CHEFE GLOBAL ----------
Config.CHEFE = {
	quebrasServidor = Eco.CHEFE_QUEBRAS_SERVIDOR,
	intervaloMin = Eco.CHEFE_INTERVALO_MIN_MIN * 60,
	intervaloMax = Eco.CHEFE_INTERVALO_MAX_MIN * 60,
	hpEscalaJogadores = Eco.CHEFE_HP_ESCALA_JOGADORES,
	contribMin = Eco.CHEFE_CONTRIB_MIN,
	hats = Eco.CHEFE_HATS,
	hatSorte = Eco.HAT_SORTE[#Eco.HAT_SORTE],
	ativoJanela = 90,   -- segundos sem golpear = nao conta como jogador ativo
}

-- ---------- DAILY (P0) ----------
-- ciclo de 7 dias: so avanca quando o jogador resgata (faltar nao tira nada).
-- moedas em minutos de renda do mundo mais avancado. soma com as missoes dentro de RENDA_EXTRA.
Config.DAILY = {
	{ texto = "Moedas", itens = { { tipo = "moedas", minutos = 10 } } },
	{ texto = "Sorte 15 min + moedas + pet Raro", itens = { { tipo = "boost", boost = "sorte", minutos = 15 }, { tipo = "moedas", minutos = 10 }, { tipo = "pet", raridade = "raro" } } },
	{ texto = "3 hats Raros", itens = { { tipo = "hats", raridade = "raro", qtd = 3 } } },
	{ texto = "Moedas (maior)", itens = { { tipo = "moedas", minutos = 20 } } },
	{ texto = "Moedas x2 15 min + hat Raro", itens = { { tipo = "boost", boost = "moedas", minutos = 15 }, { tipo = "hats", raridade = "raro", qtd = 1 } } },
	{ texto = "1 hat Épico", itens = { { tipo = "hats", raridade = "epico", qtd = 1 } } },
	{ texto = "Pet Épico", itens = { { tipo = "pet", raridade = "epico" } } },
}

-- super lendario (pedra chefe) paga Config.Areas[i].valores.super direto, sem ocupar mochila

-- ---------- MISSOES ----------
-- cada area tem a mesma trilha de missoes, com metas e premios escalados pelo valor do tema.
-- tipos: minerar (minerios quebrados na area), epico (variante epica), chefe, invocar (banner da area),
-- vender (moedas ganhas vendendo minerios dessa area)
Config.Missoes = {}
-- premios: a trilha inteira de um mundo paga ~5% do tempo medio no mundo em moedas
-- (a outra metade do limite RENDA_EXTRA fica com o Daily)
local PESO_MISSAO = { minerar30 = 2, epico = 4, chefe = 5, invocar = 3, vender = 6, minerar250 = 12 }
for _, a in ipairs(Config.Areas) do
	local cpm = Config.CPM_REFERENCIA[a.id]
	local orcamento = (Eco.RENDA_EXTRA - 1) / 2 * Eco.MINUTOS_NO_MUNDO_MEDIO[a.id] * cpm
	local lista = {
		{ tipo = "minerar", meta = 30,  texto = "Quebre 30 minérios",              peso = PESO_MISSAO.minerar30 },
		{ tipo = "epico",   meta = 5,   texto = "Quebre 5 minérios Épicos ou melhores", peso = PESO_MISSAO.epico },
		{ tipo = "chefe",   meta = 1,   texto = "Ajude a derrotar o chefe",        peso = PESO_MISSAO.chefe },
		{ tipo = "vender",  meta = arredondar(cpm * 10), texto = "Venda minérios desta ilha", peso = PESO_MISSAO.vender },
		{ tipo = "minerar", meta = 250, texto = "Quebre 250 minérios",             peso = PESO_MISSAO.minerar250 },
	}
	if Config.Gachas[a.id] then
		table.insert(lista, 4, { tipo = "invocar", meta = 5, texto = "Invoque 5 personagens", peso = PESO_MISSAO.invocar })
	end
	local soma = 0
	for _, m in ipairs(lista) do soma += m.peso end
	for i, m in ipairs(lista) do
		m.id = "a" .. a.id .. "_" .. i
		m.area = a.id
		m.premio = arredondar(orcamento * m.peso / soma)
	end
	Config.Missoes[a.id] = lista
end

function Config.missaoPorId(id)
	for _, lista in pairs(Config.Missoes) do
		for _, m in ipairs(lista) do if m.id == id then return m end end
	end
end

-- ---------- GAMEPASSES / PRODUTOS ----------
-- catalogo (IDs, precos em Robux, textos) em ReplicatedStorage.MonetizacaoConfig
Config.PASSES = {}
do
	local ok, Mon = pcall(require, script.Parent:WaitForChild("MonetizacaoConfig", 5))
	if ok and Mon then
		for _, p in ipairs(Mon.PASSES) do table.insert(Config.PASSES, p.chave) end
	end
end

-- ---------- NUMEROS ----------
-- formato unico de moedas/numeros no jogo inteiro: 3 digitos significativos + sufixo
local SUFIXOS = { "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc" }
function Config.formatar(n)
	n = tonumber(n) or 0
	local sinal = n < 0 and "-" or ""
	n = math.abs(n)
	if n < 1000 then
		if n ~= math.floor(n) and n < 100 then
			return sinal .. (string.format("%.1f", n):gsub("%.0$", ""))
		end
		return sinal .. tostring(math.floor(n))
	end
	local i = math.min(math.floor(math.log10(n) / 3), #SUFIXOS)
	local v = n / (1000 ^ i)
	local txt
	if v < 10 then txt = string.format("%.2f", math.floor(v * 100) / 100)
	elseif v < 100 then txt = string.format("%.1f", math.floor(v * 10) / 10)
	else txt = string.format("%d", math.floor(v)) end
	if txt:find("%.") then txt = txt:gsub("0+$", ""):gsub("%.$", "") end
	return sinal .. txt .. SUFIXOS[i]
end

-- espaco que um minerio ocupa na mochila
function Config.espacoMinerio(id)
	local tema, variante = string.match(id, "^(%a+)_(%a+)$")
	local v
	for _, x in ipairs(Config.Variantes) do if x.id == variante then v = x end end
	local area
	for _, a in ipairs(Config.Areas) do if a.tema == tema then area = a end end
	return (v and v.espaco or 1) * (area and area.espaco or 1)
end

-- Separate destinations: no physical connection exists between islands.
Config.AREA_TAMANHO = Vector3.new(292, 1, 292)
Config.AREA_PASSO = 1600
Config.AREA_Z_INICIAL = 1600
Config.AREA_ROCHAS = 24
local centros = {
 Vector3.new(-1600,100,0), Vector3.new(1600,100,0),
 Vector3.new(-1600,100,1600), Vector3.new(0,100,1600),
 Vector3.new(1600,100,1600), Vector3.new(0,100,3200),
}
for _, a in ipairs(Config.Areas) do
 a.tamanho=Config.AREA_TAMANHO a.rochas=Config.AREA_ROCHAS a.centro=centros[a.id]
end

Config.RESPAWN_ROCHA = 1.2
Config.RESPAWN_CHEFE = 12
Config.COOLDOWN_GOLPE = Eco.PICARETAS[1].intervalo  -- fallback; o intervalo real vem da picareta
Config.DANO_BASE = Eco.DANO_BASE
Config.MOEDA_POR_HP = Eco.MOEDA_POR_HP

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

function Config.valorMinerio(tema, variante)
	for _, a in ipairs(Config.Areas) do
		if a.tema == tema then return a.valores[variante] or 0 end
	end
	return 0
end

function Config.infoMinerio(id)
	local tema, variante = string.match(id, "^(%a+)_(%a+)$")
	local t = tema and Config.Temas[tema]
	local v = variante and Config.variantePorId(variante)
	if not t or not v then return nil end
	local nome = v.nome ~= "" and (t.nome .. " " .. v.nome) or t.nome
	return {
		nome = nome,
		valor = Config.valorMinerio(tema, variante),
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
