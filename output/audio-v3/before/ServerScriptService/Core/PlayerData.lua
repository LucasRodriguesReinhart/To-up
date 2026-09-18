local RS = game:GetService("ReplicatedStorage")
local DSS = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Config = require(RS.Config)
local Passes = require(script.Parent.Passes)

-- ---------- ARMAZENAMENTO ----------
-- O GetDataStore nao bate na API, entao ele passa mesmo com o acesso desligado.
-- Quem falha e a primeira chamada real. Por isso a sondagem abaixo.
local memoria = {}
local storeMemoria = {
	GetAsync = function(_, k) return memoria[k] end,
	SetAsync = function(_, k, v) memoria[k] = v end,
	UpdateAsync = function(_, k, fn)
		local novo = fn(memoria[k])
		if novo ~= nil then memoria[k] = novo end
		return memoria[k]
	end,
}

local store = storeMemoria
local USANDO_MEMORIA = true
local MOTIVO = "nao testado"

do
	local okObter, real = pcall(function()
		return DSS:GetDataStore("MineracaoSim_v2")
	end)
	if okObter and real then
		local okLer, err = pcall(function()
			real:GetAsync("__sonda__")
		end)
		if okLer then
			store = real
			USANDO_MEMORIA = false
			MOTIVO = "ok"
		else
			MOTIVO = tostring(err)
		end
	else
		MOTIVO = tostring(real)
	end
end

if USANDO_MEMORIA then
	local motivoLower = string.lower(MOTIVO)
	if string.find(motivoLower, "studio access", 1, true)
		or string.find(motivoLower, "api services", 1, true)
		or string.find(motivoLower, "studioaccesstoapis", 1, true) then
		warn("[PlayerData] DataStore desligado no Studio. Progresso so nesta sessao.")
		warn("[PlayerData] Pra salvar de verdade: Home > Game Settings > Security > Enable Studio Access to API Services")
	else
		warn("[PlayerData] DataStore indisponivel (" .. MOTIVO .. "). Progresso so nesta sessao.")
	end
else
	print("[PlayerData] DataStore ativo, progresso sera salvo")
end

function PlayerDataUsandoMemoria() return USANDO_MEMORIA end

local PlayerData = {}
local cache = {}
local sessaoId = HttpService:GenerateGUID(false)
local TRAVA_VALIDA = 180 -- segundos: trava de outra sessao mais velha que isso e considerada abandonada

local function perfilNovo()
	return {
		moeda = 0,
		picareta = "enferrujada",
		mochilaTier = "saco_pano",
		mochila = {},            -- [idMinerio] = quantidade
		hats = {},               -- formato antigo (empilhado), so pra migracao
		hatsInv = {},            -- [uid] = { id, nivel, xp, xpTotal }  cada hat e um item separado
		hatSeq = 0,
		equipados = {},          -- lista de uid (pode ter 2 hats iguais)
		pets = {},               -- formato antigo (empilhado), so pra migracao
		petsInv = {},            -- [uid] = { id, nivel, xp, xpTotal, apelido }
		petSeq = 0,
		petsEquipados = {},      -- lista de uid
		apelidos = {},           -- formato antigo, so pra migracao
		picaretasCompradas = { enferrujada = true },
		missoes = {},            -- [idMissao] = { p = progresso, r = resgatada }
		codigos = {},            -- [CODIGO] = true quando ja resgatado
		minerados = 0,           -- minerios quebrados (placar)
		areas = { [1] = true },
		-- economia v3.1
		econVersao = Config.ECON_VERSAO,
		pity = { l = 0, m = 0 }, -- giros desde o ultimo Lendario+ / Mitico+
		giros = 0,               -- giros totais (o primeiro e garantido Raro+ e gratis)
		index = { pets = {}, hats = {} },
		daily = { dia = 1, ultimo = 0 },  -- ultimo = numero do dia UTC do ultimo resgate
		boosts = { sorte = 0, moedas = 0 }, -- os.time() em que cada boost termina
		recibos = {},            -- [PurchaseId] = os.time() (compras ja entregues)
		compras = {},            -- [chaveProduto] = quantidade
		cosmeticos = {},
		tel = {},                -- marcos de telemetria ja registrados (FirstOreMined etc.)
		exp = {},                -- atribuicoes do ExperimentService
		tempoJogado = 0,         -- segundos
		criadoEm = os.time(),
	}
end

-- cria um hat novo no inventario e devolve o uid
function PlayerData.novoHat(perfil, id, nivel)
	perfil.hatSeq = (perfil.hatSeq or 0) + 1
	local uid = "h" .. perfil.hatSeq
	perfil.hatsInv[uid] = { id = id, nivel = nivel or 1, xp = 0, xpTotal = 0 }
	perfil.index.hats[id] = true
	return uid
end

-- cria um pet novo no inventario e devolve o uid
function PlayerData.novoPet(perfil, id, nivel)
	perfil.petSeq = (perfil.petSeq or 0) + 1
	local uid = "p" .. perfil.petSeq
	perfil.petsInv[uid] = { id = id, nivel = nivel or 1, xp = 0, xpTotal = 0 }
	perfil.index.pets[id] = true
	return uid
end

-- XP guardado acima do necessario (save de uma curva antiga: v3.1.1 barateou os niveis de pet)
-- vira nivel pela curva atual. Nunca tira nivel; so resolve a sobra. Devolve true se mudou algo.
local function resolverSobraXp(inst, def, paraSubir, nivelMax)
	inst.xp = math.max(0, tonumber(inst.xp) or 0)
	local antes = inst.nivel
	while inst.nivel < nivelMax do
		local need = paraSubir(def, inst.nivel)
		if need <= 0 or inst.xp < need then break end
		inst.xp -= need
		inst.nivel += 1
	end
	if inst.nivel >= nivelMax then inst.xp = 0 end
	return inst.nivel ~= antes
end

local function normalizar(p)
	local novo = perfilNovo()
	for k, v in pairs(novo) do
		if p[k] == nil then p[k] = v end
	end
	p.index.pets = p.index.pets or {}
	p.index.hats = p.index.hats or {}
	for id in pairs(p.index.hats) do if not Config.hatPorId(id) then p.index.hats[id] = nil end end
	p.pity.l, p.pity.m = p.pity.l or 0, p.pity.m or 0
	p.boosts.sorte, p.boosts.moedas = p.boosts.sorte or 0, p.boosts.moedas or 0
	p.melhorias = nil
	-- saves antigos: toda picareta ate a atual conta como comprada
	local _, iAtual = Config.picaretaPorId(p.picareta)
	if not iAtual then p.picareta = "enferrujada"; iAtual = 1 end
	for i = 1, iAtual do p.picaretasCompradas[Config.Picaretas[i].id] = true end
	if not Config.mochilaPorId(p.mochilaTier) then p.mochilaTier = "saco_pano" end
	-- pets empilhados viram itens separados
	if next(p.pets) then
		local porId = {}
		for id, posse in pairs(p.pets) do
			if Config.petPorId(id) then
				porId[id] = {}
				for k = 1, math.clamp(posse.qtd or 1, 1, 30) do
					local uid = PlayerData.novoPet(p, id, k == 1 and (posse.nivel or 1) or 1)
					local nick = p.apelidos[id]
					if k == 1 and type(nick) == "string" then p.petsInv[uid].apelido = nick end
					table.insert(porId[id], uid)
				end
			end
		end
		local novos = {}
		for _, id in ipairs(p.petsEquipados) do
			local lista = porId[id]
			if lista and #lista > 0 then table.insert(novos, table.remove(lista, 1)) end
		end
		p.petsEquipados = novos
		p.pets, p.apelidos = {}, {}
	end
	if next(p.hats) then
		local porId = {}
		for id, posse in pairs(p.hats) do
			if Config.hatPorId(id) then
				porId[id] = {}
				for _ = 1, math.clamp(posse.qtd or 1, 1, 20) do
					table.insert(porId[id], PlayerData.novoHat(p, id, posse.nivel or 1))
				end
			end
		end
		local novos = {}
		for _, id in ipairs(p.equipados) do
			local lista = porId[id]
			if lista and #lista > 0 then table.insert(novos, table.remove(lista, 1)) end
		end
		p.equipados = novos
		p.hats = {}
	end
	-- itens que sairam do jogo somem; niveis acima do novo maximo sao limitados
	for uid, inst in pairs(p.hatsInv) do
		-- hats provisorios antigos ("chakra_raro") viram o primeiro hat do catalogo com o mesmo tema e raridade
		if not Config.hatPorId(inst.id) and type(inst.id) == "string" then
			local tema, rar = inst.id:match("^(%a+)_(%a+)$")
			local lista = tema and Config.hatsDoTema(tema, rar) or {}
			if #lista > 0 then inst.id = lista[1].id end
		end
		if not Config.hatPorId(inst.id) then p.hatsInv[uid] = nil
		else
			inst.nivel = math.clamp(inst.nivel or 1, 1, Config.HAT_NIVEL_MAX)
			resolverSobraXp(inst, Config.hatPorId(inst.id), Config.hatXpParaSubir, Config.HAT_NIVEL_MAX)
			p.index.hats[inst.id] = true
		end
	end
	for uid, inst in pairs(p.petsInv) do
		if not Config.petPorId(inst.id) then p.petsInv[uid] = nil
		else
			inst.nivel = math.clamp(inst.nivel or 1, 1, Config.PET_NIVEL_MAX)
			resolverSobraXp(inst, Config.petPorId(inst.id), Config.petXpParaSubir, Config.PET_NIVEL_MAX)
			p.index.pets[inst.id] = true
		end
	end
	for i = #p.equipados, 1, -1 do
		if not p.hatsInv[p.equipados[i]] then table.remove(p.equipados, i) end
	end
	for i = #p.petsEquipados, 1, -1 do
		if not p.petsInv[p.petsEquipados[i]] then table.remove(p.petsEquipados, i) end
	end
	-- saves de quando havia mais slots de pet: fica so o limite atual, mantendo os mais fortes
	if #p.petsEquipados > Config.PET_SLOTS_BASE then
		local forca = {}
		for _, uid in ipairs(p.petsEquipados) do
			local inst = p.petsInv[uid]
			forca[uid] = Config.petBonusDano(Config.petPorId(inst.id), inst.nivel)
		end
		table.sort(p.petsEquipados, function(a, b) return forca[a] > forca[b] end)
		for i = #p.petsEquipados, Config.PET_SLOTS_BASE + 1, -1 do table.remove(p.petsEquipados, i) end
	end
	-- recibos antigos (mais de 60 dias) nao precisam mais ficar no save
	local agora = os.time()
	for id, t in pairs(p.recibos) do
		if type(t) ~= "number" or agora - t > 60 * 86400 then p.recibos[id] = nil end
	end
	p.econVersao = Config.ECON_VERSAO
	return p
end

local function chave(player) return "u_" .. player.UserId end

-- carrega travando a sessao: impede que dois servidores escrevam o mesmo save (duplicacao)
function PlayerData.carregar(player)
	local dados, okFinal
	for tentativa = 1, 5 do
		local ok, res = pcall(function()
			return store:UpdateAsync(chave(player), function(atual)
				if type(atual) == "table" and atual.sessao and atual.sessao.id ~= sessaoId
					and os.time() - (atual.sessao.t or 0) < TRAVA_VALIDA and tentativa < 5 then
					return nil -- outra sessao ativa: nao escreve, tenta de novo
				end
				atual = type(atual) == "table" and atual or perfilNovo()
				atual.sessao = { id = sessaoId, t = os.time() }
				return atual
			end)
		end)
		if ok and type(res) == "table" and res.sessao and res.sessao.id == sessaoId then
			dados, okFinal = res, true
			break
		end
		if not ok and not USANDO_MEMORIA then warn("[PlayerData] carregar " .. player.Name .. ": " .. tostring(res)) end
		task.wait(2)
	end
	if not player.Parent then return nil end
	local perfil
	if okFinal then
		perfil = normalizar(dados)
	else
		-- sem conseguir carregar: perfil temporario que NUNCA salva (nao sobrescreve o save real)
		perfil = perfilNovo()
		perfil.__semSalvar = true
		warn("[PlayerData] nao foi possivel carregar " .. player.Name .. "; perfil temporario sem salvar")
	end
	perfil.__entrouEm = os.clock()
	perfil.__player = player
	cache[player] = perfil
	return perfil
end

function PlayerData.get(player) return cache[player] end

-- perfil zerado (testes no Studio)
function PlayerData.carregarVazio() return normalizar(perfilNovo()) end

local function copiaParaSalvar(perfil, liberar)
	local t = {}
	for k, v in pairs(perfil) do
		if type(k) ~= "string" or k:sub(1, 2) ~= "__" then t[k] = v end
	end
	t.sessao = not liberar and { id = sessaoId, t = os.time() } or nil
	return t
end

-- salvar com UpdateAsync: so grava se a trava ainda for desta sessao
function PlayerData.salvar(player, liberar)
	local perfil = cache[player]
	if not perfil then return false end
	if perfil.__semSalvar then return false end
	if perfil.__dev and not perfil.__devSalvar then return false end
	if perfil.__entrouEm then
		perfil.tempoJogado = (perfil.tempoJogado or 0) + (os.clock() - perfil.__entrouEm)
		perfil.__entrouEm = os.clock()
	end
	local dados = copiaParaSalvar(perfil, liberar)
	local ok, err = pcall(function()
		store:UpdateAsync(chave(player), function(atual)
			if type(atual) == "table" and atual.sessao and atual.sessao.id ~= sessaoId then
				return nil -- outra sessao assumiu o save: nao sobrescreve
			end
			return dados
		end)
	end)
	if not ok and not USANDO_MEMORIA then
		warn("[PlayerData] falha ao salvar " .. player.Name .. ": " .. tostring(err))
	end
	return ok
end

function PlayerData.descarregar(player)
	PlayerData.salvar(player, true)
	cache[player] = nil
end

-- ---------- STATS ----------
local function maiorArea(perfil)
	local m = 1
	for id in pairs(perfil.areas) do if type(id) == "number" and id > m then m = id end end
	return m
end
PlayerData.maiorArea = maiorArea

function PlayerData.bonusHats(perfil)
	local dano = 0
	for _, uid in ipairs(perfil.equipados) do
		local posse = perfil.hatsInv[uid]
		local def = posse and Config.hatPorId(posse.id)
		if def then dano += Config.hatDanoNoNivel(def.dano, posse.nivel or 1) end
	end
	return dano, { capacidade = 0, sorte = 0, valor = 0 }
end

-- dano = (base + soma dos hats) x multiplicador da picareta x (1 + bonus % dos pets)
function PlayerData.dano(perfil)
	local pic = Config.picaretaPorId(perfil.picareta)
	local danoHats = PlayerData.bonusHats(perfil)
	local bonusDano = PlayerData.bonusPets(perfil)
	return (Config.DANO_BASE + danoHats) * (pic and pic.mult or 1) * (1 + bonusDano)
end

function PlayerData.intervalo(perfil)
	local pic = Config.picaretaPorId(perfil.picareta)
	return pic and pic.intervalo or Config.COOLDOWN_GOLPE
end

function PlayerData.capacidade(perfil)
	local moc = Config.mochilaPorId(perfil.mochilaTier)
	return moc and moc.capacidade or Config.Mochilas[1].capacidade
end

-- ---------- PETS ----------
function PlayerData.bonusPets(perfil)
	local dano = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local posse = perfil.petsInv[uid]
		local def = posse and Config.petPorId(posse.id)
		if def then dano += Config.petBonusDano(def, posse.nivel) end
	end
	return dano, 0
end

function PlayerData.levelBonus(perfil)
	local lb = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local posse = perfil.petsInv[uid]
		local def = posse and Config.petPorId(posse.id)
		if def then lb += Config.petLevelBonus(def) end
	end
	return lb
end

function PlayerData.velPets(perfil)
	local v = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local inst = perfil.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		if def then v += Config.petVelocidade(def, inst.nivel) end
	end
	return math.min(v, Config.VELOCIDADE_PETS_MAX)
end

function PlayerData.velocidade(perfil)
	return Config.VELOCIDADE_BASE + PlayerData.velPets(perfil)
end

function PlayerData.slotsPets() return Config.PET_SLOTS_BASE end

function PlayerData.totalPets(perfil)
	local n = 0
	for _ in pairs(perfil.petsInv) do n += 1 end
	return n
end

-- passes que dependem do jogador: PlayerData recebe o player guardado no perfil
local function temPasse(perfil, nome)
	return perfil.__player and Passes.possui(perfil.__player, nome) or false
end

function PlayerData.capacidadePets(perfil)
	return Config.capacidadePets() + (temPasse(perfil, "Inventario") and 50 or 0)
end

function PlayerData.petsResumo(perfil)
	local t = {}
	for _, inst in pairs(perfil.petsInv) do
		local r = t[inst.id] or { qtd = 0, nivel = 1, xp = 0 }
		r.qtd += 1
		r.nivel = math.max(r.nivel, inst.nivel)
		t[inst.id] = r
	end
	return t
end

function PlayerData.slots(perfil)
	return Config.slotsHat(maiorArea(perfil)) + (temPasse(perfil, "HatSlot") and 1 or 0)
end

function PlayerData.capacidadeHats(perfil)
	return Config.capacidadeHats() + (temPasse(perfil, "Inventario") and 50 or 0)
end

function PlayerData.hatsResumo(perfil)
	local t = {}
	for _, h in pairs(perfil.hatsInv) do
		local r = t[h.id] or { qtd = 0, nivel = 1 }
		r.qtd += 1
		r.nivel = math.max(r.nivel, h.nivel)
		t[h.id] = r
	end
	return t
end

function PlayerData.totalHats(perfil)
	local n = 0
	for _ in pairs(perfil.hatsInv) do n += 1 end
	return n
end

function PlayerData.itensNaMochila(perfil)
	local t = 0
	for id, q in pairs(perfil.mochila) do t += q * Config.espacoMinerio(id) end
	return t
end

function PlayerData.qtdMinerios(perfil)
	local t = 0
	for _, q in pairs(perfil.mochila) do t += q end
	return t
end

function PlayerData.mochilaCheia(perfil, idMinerio)
	local extra = idMinerio and Config.espacoMinerio(idMinerio) or 1
	return PlayerData.itensNaMochila(perfil) + extra > PlayerData.capacidade(perfil)
end

function PlayerData.progredirMissao(perfil, areaId, tipo, qtd)
	local lista = Config.Missoes[areaId]
	if not lista or not perfil.areas[areaId] then return end
	for _, m in ipairs(lista) do
		if m.tipo == tipo then
			local e = perfil.missoes[m.id] or { p = 0, r = false }
			e.p = math.min(m.meta, e.p + (qtd or 1))
			perfil.missoes[m.id] = e
		end
	end
end

-- ---------- BOOSTS ----------
function PlayerData.boostAtivo(perfil, tipo)
	return (perfil.boosts[tipo] or 0) > os.time()
end
-- boosts do mesmo tipo somam TEMPO, nunca multiplicador
function PlayerData.adicionarBoost(perfil, tipo, minutos)
	local agora = os.time()
	perfil.boosts[tipo] = math.max(perfil.boosts[tipo] or 0, agora) + math.floor(minutos * 60)
end

function PlayerData.diaUTC(t) return math.floor((t or os.time()) / 86400) end

function PlayerData.snapshot(perfil)
	local danoHats = PlayerData.bonusHats(perfil)
	local bonusDanoPets = PlayerData.bonusPets(perfil)
	local agora = os.time()
	return {
		econVersao = Config.ECON_VERSAO,
		petsInv = perfil.petsInv,
		pets = PlayerData.petsResumo(perfil),
		petsEquipados = perfil.petsEquipados,
		capacidadePets = PlayerData.capacidadePets(perfil),
		picaretasCompradas = perfil.picaretasCompradas,
		missoes = perfil.missoes,
		bonusDanoPets = bonusDanoPets,
		bonusMoedaPets = 0,
		levelBonus = PlayerData.levelBonus(perfil),
		slotsPets = PlayerData.slotsPets(perfil),
		totalPets = PlayerData.totalPets(perfil),
		velocidade = PlayerData.velocidade(perfil),
		velPets = PlayerData.velPets(perfil),
		velPetsMax = Config.VELOCIDADE_PETS_MAX,
		moeda = perfil.moeda,
		picareta = perfil.picareta,
		intervalo = PlayerData.intervalo(perfil),
		mochilaTier = perfil.mochilaTier,
		mochila = perfil.mochila,
		hatsInv = perfil.hatsInv,
		hats = PlayerData.hatsResumo(perfil),
		equipados = perfil.equipados,
		areas = perfil.areas,
		dano = PlayerData.dano(perfil),
		danoHats = danoHats,
		capacidade = PlayerData.capacidade(perfil),
		carregado = PlayerData.itensNaMochila(perfil),
		slots = PlayerData.slots(perfil),
		totalHats = PlayerData.totalHats(perfil),
		capacidadeHats = PlayerData.capacidadeHats(perfil),
		qtdMinerios = PlayerData.qtdMinerios(perfil),
		bonusValor = 0,
		bonusSorte = 0,
		pity = perfil.pity,
		giros = perfil.giros,
		giroGratis = (perfil.giros or 0) == 0,
		index = perfil.index,
		daily = { dia = perfil.daily.dia, disponivel = PlayerData.diaUTC() > (perfil.daily.ultimo or 0) },
		boosts = { sorte = math.max(0, perfil.boosts.sorte - agora), moedas = math.max(0, perfil.boosts.moedas - agora) },
		compras = perfil.compras,
		cosmeticos = perfil.cosmeticos,
		multMoedas = perfil.__multMoedas or 1,
		friendBoost = perfil.__friendBoost or 0,
		luckyMult = perfil.__luckyMult or 1,
	}
end

-- ganchos opcionais (Economia preenche multiplicadores antes do snapshot)
PlayerData.antesDeSincronizar = nil

function PlayerData.sincronizar(player)
	local perfil = cache[player]
	if not perfil then return end
	perfil.__player = player
	if PlayerData.antesDeSincronizar then pcall(PlayerData.antesDeSincronizar, player, perfil) end
	local snap = PlayerData.snapshot(perfil)
	snap.passes = Passes.todos(player)
	RS.Remotes.AtualizarDados:FireClient(player, snap)
	local ids, nomes = {}, {}
	for _, uid in ipairs(perfil.petsEquipados) do
		local inst = perfil.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		if def then
			table.insert(ids, inst.id)
			table.insert(nomes, inst.apelido or def.nome)
		end
	end
	player:SetAttribute("PetsApelidos", HttpService:JSONEncode(nomes))
	local ls = player:FindFirstChild("leaderstats")
	if not ls then
		ls = Instance.new("Folder")
		ls.Name = "leaderstats"
		local m = Instance.new("IntValue"); m.Name = "Minérios"; m.Parent = ls
		local c = Instance.new("StringValue"); c.Name = "Moedas"; c.Parent = ls
		ls.Parent = player
	end
	ls["Minérios"].Value = perfil.minerados or 0
	ls.Moedas.Value = Config.formatar(perfil.moeda)
	player:SetAttribute("PetsEquipados", table.concat(ids, ","))
	player:SetAttribute("IntervaloGolpe", PlayerData.intervalo(perfil))
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then hum.WalkSpeed = PlayerData.velocidade(perfil) end
end

return PlayerData

