-- SomJogo: identidade sonora do Anime Mining Simulator (cliente).
--  * SoundGroups: Mining, Rewards, UI, SFX, Ambience + o grupo de musica que ja existia (MusicaGrupo)
--  * cada evento e uma lista de CAMADAS; cada camada sorteia entre variacoes de SoundId e de pitch
--  * limite de vozes por evento e intervalo minimo (nada de 30 moedas tocando juntas)
--  * combo de coleta: o pitch sobe a cada minerio seguido e volta ao normal depois de 1,5 s
-- Fontes: Pro Sound Effects e APM Music (bibliotecas licenciadas para uso no Roblox) + sons que o jogo ja usava.
-- TROCAR UM SOM: mude so o id na tabela ID abaixo. Volumes finais por grupo em GRUPOS.
local SoundService = game:GetService("SoundService")
local Debris = game:GetService("Debris")

local S = {}

local ID = {
	-- pedra (Pro Sound Effects)
	rock_hit_1 = 9118598279,   -- Rock Hit Dirt Impact 14 (0,4 s)
	rock_hit_2 = 9118598469,   -- Rock Hit Dirt Impact 15 (0,5 s)
	rock_hit_big = 9118617342, -- Rock Impact Large Hit Scrape (0,9 s)
	rock_break_1 = 9125869797, -- Rock Drops Smashes Impacts 7 (1,5 s)
	rock_break_2 = 9118612665, -- Rock Impact 7 (2,1 s)
	rock_debris = 9118690959,  -- (ja usado no jogo)
	-- metal da picareta (ja usados no jogo, Pro Sound Effects)
	metal_1 = 9116651255,
	metal_2 = 9116652339,
	-- ar (Pro Sound Effects)
	whoosh_1 = 9120972321,
	whoosh_2 = 9120972444,
	whoosh_3 = 9120972323,
	-- recompensa
	coin = 4608067546,         -- (ja usado no jogo)
	pickup = 93529351909119,   -- retro coin pickup (ja usado no jogo)
	sand = 9118770617,         -- (ja usado no jogo: abertura do ovo)
	erro = 9116652038,         -- (ja usado no jogo)
	sting_hit = 9040476898,    -- APM "Early Bird - Hit1" (2 s)
	sting_up = 1840076509,     -- APM "Through the Roof (sting)" (2 s)
	sting_big = 9047103106,    -- APM "All It Takes Sting 2"
}
S.ID = ID

local GRUPOS = { Mining = 0.9, Rewards = 1, UI = 0.55, SFX = 0.85, Ambience = 0.5 }
local MUSICA_VOLUME = 0.32 -- a musica nunca compete com o feedback

local function grupo(nome)
	local g = SoundService:FindFirstChild("Grupo" .. nome)
	if not g then
		g = Instance.new("SoundGroup")
		g.Name = "Grupo" .. nome
		g.Volume = GRUPOS[nome] or 1
		g.Parent = SoundService
	end
	return g
end
for nome in pairs(GRUPOS) do grupo(nome) end
do
	local musica = SoundService:FindFirstChild("MusicaGrupo")
	if musica and musica:IsA("SoundGroup") then musica.Volume = math.min(musica.Volume, MUSICA_VOLUME) end
end

-- camada = { ids = {...}, vol, pitch = {min, max}, grupo, atraso }
local function L(ids, vol, pmin, pmax, grupoNome, atraso)
	return { ids = ids, vol = vol, pitch = { pmin, pmax or pmin }, grupo = grupoNome, atraso = atraso }
end

local EVENTOS = {
	-- mineracao: impacto de pedra + metal da picareta (+ grave nas picaretas avancadas)
	hit = { max = 4, gap = 0.04, camadas = {
		L({ ID.rock_hit_1, ID.rock_hit_2 }, 0.55, 0.95, 1.12, "Mining"),
		L({ ID.metal_1, ID.metal_2 }, 0.16, 1.35, 1.6, "Mining"),
	} },
	hit_pesado = { max = 3, gap = 0.05, camadas = {
		L({ ID.rock_hit_big }, 0.32, 0.85, 0.95, "Mining"),
	} },
	whoosh = { max = 2, gap = 0.12, camadas = { L({ ID.whoosh_1, ID.whoosh_2, ID.whoosh_3 }, 0.14, 1.15, 1.35, "Mining") } },
	-- quebra por raridade (contraste: comum simples, raras com camada extra)
	break_comum = { max = 3, gap = 0.05, camadas = { L({ ID.rock_break_1, ID.rock_break_2 }, 0.5, 1.05, 1.18, "Mining") } },
	break_incomum = { max = 2, gap = 0.05, camadas = {
		L({ ID.rock_break_1, ID.rock_break_2 }, 0.55, 1.0, 1.1, "Mining"),
		L({ ID.pickup }, 0.22, 1.35, 1.35, "Rewards", 0.05),
	} },
	break_raro = { max = 2, gap = 0.05, camadas = {
		L({ ID.rock_break_1, ID.rock_break_2 }, 0.6, 0.98, 1.05, "Mining"),
		L({ ID.pickup }, 0.28, 1.7, 1.7, "Rewards", 0.04),
		L({ ID.coin }, 0.2, 1.5, 1.5, "Rewards", 0.1),
	} },
	break_epico = { max = 2, gap = 0.08, camadas = {
		L({ ID.rock_break_2 }, 0.65, 0.92, 0.98, "Mining"),
		L({ ID.sting_hit }, 0.34, 1.0, 1.0, "Rewards", 0.03),
	} },
	break_lendario = { max = 1, gap = 0.2, camadas = {
		L({ ID.rock_hit_big }, 0.5, 0.8, 0.8, "Mining"),
		L({ ID.rock_break_2 }, 0.6, 0.85, 0.85, "Mining", 0.02),
		L({ ID.sting_up }, 0.42, 1.0, 1.0, "Rewards", 0.05),
	} },
	break_chefe = { max = 1, gap = 0.5, camadas = {
		L({ ID.rock_hit_big }, 0.7, 0.7, 0.7, "Mining"),
		L({ ID.rock_break_2 }, 0.7, 0.75, 0.75, "Mining", 0.04),
		L({ ID.sting_big }, 0.5, 1.0, 1.0, "Rewards", 0.1),
	} },
	-- coleta (o combo sobe o pitch; ver S.coleta)
	coleta = { max = 3, gap = 0.035, camadas = { L({ ID.coin }, 0.22, 1.0, 1.0, "Rewards") } },
	-- venda por tamanho
	venda_pequena = { max = 1, gap = 0.2, camadas = { L({ ID.coin }, 0.45, 1.0, 1.05, "Rewards") } },
	venda_media = { max = 1, gap = 0.2, camadas = {
		L({ ID.pickup }, 0.45, 1.0, 1.0, "Rewards"),
		L({ ID.coin }, 0.35, 1.1, 1.1, "Rewards", 0.07),
	} },
	venda_grande = { max = 1, gap = 0.2, camadas = {
		L({ ID.pickup }, 0.5, 0.95, 0.95, "Rewards"),
		L({ ID.coin }, 0.4, 1.0, 1.0, "Rewards", 0.06),
		L({ ID.coin }, 0.35, 1.15, 1.15, "Rewards", 0.13),
		L({ ID.coin }, 0.3, 1.3, 1.3, "Rewards", 0.2),
	} },
	venda_jackpot = { max = 1, gap = 0.5, camadas = {
		L({ ID.sting_hit }, 0.45, 1.0, 1.0, "Rewards"),
		L({ ID.coin }, 0.4, 1.0, 1.0, "Rewards", 0.05),
		L({ ID.coin }, 0.35, 1.2, 1.2, "Rewards", 0.12),
		L({ ID.coin }, 0.3, 1.4, 1.4, "Rewards", 0.19),
	} },
	-- progresso
	upgrade = { max = 1, gap = 0.2, camadas = {
		L({ ID.whoosh_2 }, 0.25, 1.2, 1.2, "Rewards"),
		L({ ID.metal_1 }, 0.3, 0.95, 0.95, "Rewards", 0.08),
		L({ ID.pickup }, 0.35, 1.25, 1.25, "Rewards", 0.12),
	} },
	level_up = { max = 1, gap = 0.3, camadas = { L({ ID.sting_up }, 0.55, 1.0, 1.0, "Rewards") } },
	area_nova = { max = 1, gap = 1, camadas = {
		L({ ID.whoosh_1 }, 0.3, 0.8, 0.8, "Rewards"),
		L({ ID.rock_hit_big }, 0.45, 0.7, 0.7, "Rewards", 0.25),
		L({ ID.sting_big }, 0.55, 1.0, 1.0, "Rewards", 0.3),
	} },
	-- drops e invocacao por raridade
	drop_comum = { max = 2, gap = 0.1, camadas = { L({ ID.pickup }, 0.3, 1.15, 1.25, "Rewards") } },
	drop_raro = { max = 1, gap = 0.2, camadas = { L({ ID.pickup }, 0.4, 1.5, 1.5, "Rewards"), L({ ID.coin }, 0.25, 1.6, 1.6, "Rewards", 0.08) } },
	drop_epico = { max = 1, gap = 0.3, camadas = { L({ ID.sting_hit }, 0.45, 1.05, 1.05, "Rewards") } },
	drop_lendario = { max = 1, gap = 0.5, camadas = { L({ ID.sting_up }, 0.55, 1.0, 1.0, "Rewards") } },
	drop_secreto = { max = 1, gap = 0.8, camadas = {
		L({ ID.rock_hit_big }, 0.4, 0.6, 0.6, "Rewards"),
		L({ ID.sting_big }, 0.6, 0.9, 0.9, "Rewards", 0.1),
	} },
	invocar_inicio = { max = 1, gap = 0.3, camadas = { L({ ID.sand }, 0.35, 1.2, 1.2, "Rewards"), L({ ID.whoosh_3 }, 0.2, 0.9, 0.9, "Rewards", 0.1) } },
	-- viagem
	portal_saida = { max = 1, gap = 0.5, camadas = {
		L({ ID.whoosh_1 }, 0.35, 0.75, 0.75, "SFX"),
		L({ ID.whoosh_2 }, 0.3, 0.95, 0.95, "SFX", 0.12),
	} },
	portal_chegada = { max = 1, gap = 0.5, camadas = { L({ ID.rock_hit_big }, 0.28, 0.75, 0.75, "SFX") } },
	-- interface (baixo e curto)
	ui_click = { max = 2, gap = 0.04, camadas = { L({ ID.pickup }, 0.12, 1.9, 2.0, "UI") } },
	ui_hover = { max = 1, gap = 0.06, camadas = { L({ ID.coin }, 0.035, 2.4, 2.6, "UI") } },
	ui_abrir = { max = 1, gap = 0.1, camadas = { L({ ID.whoosh_2 }, 0.13, 1.45, 1.5, "UI") } },
	ui_fechar = { max = 1, gap = 0.1, camadas = { L({ ID.whoosh_3 }, 0.1, 1.05, 1.1, "UI") } },
	ui_compra = { max = 1, gap = 0.15, camadas = { L({ ID.pickup }, 0.4, 1.0, 1.0, "UI"), L({ ID.coin }, 0.25, 1.2, 1.2, "UI", 0.06) } },
	ui_erro = { max = 1, gap = 0.2, camadas = { L({ ID.erro }, 0.22, 0.7, 0.75, "UI") } },
	ui_equipar = { max = 1, gap = 0.08, camadas = { L({ ID.metal_2 }, 0.14, 1.6, 1.7, "UI") } },
	-- UI V2: abas, interruptores, notificacoes e banners de recompensa (curtos e discretos)
	ui_tab = { max = 1, gap = 0.06, camadas = { L({ ID.pickup }, 0.08, 2.2, 2.3, "UI") } },
	ui_toggle = { max = 1, gap = 0.06, camadas = { L({ ID.metal_2 }, 0.1, 2.0, 2.1, "UI") } },
	ui_notify = { max = 1, gap = 0.25, camadas = { L({ ID.coin }, 0.08, 1.8, 1.8, "UI") } },
	ui_popup = { max = 1, gap = 0.12, camadas = { L({ ID.whoosh_2 }, 0.1, 1.7, 1.75, "UI") } },
	reward_banner = { max = 1, gap = 0.4, camadas = {
		L({ ID.pickup }, 0.35, 1.2, 1.2, "Rewards"),
		L({ ID.coin }, 0.28, 1.45, 1.45, "Rewards", 0.07),
	} },
	coin_tick = { max = 2, gap = 0.08, camadas = { L({ ID.coin }, 0.12, 1.3, 1.5, "Rewards") } },
}
S.EVENTOS = EVENTOS

local tocando = {}   -- [evento] = { ultimo = clock, vozes = n }
local rnd = Random.new()

local function criarSom(camada, pos, pitchExtra)
	local s = Instance.new("Sound")
	s.SoundId = "rbxassetid://" .. camada.ids[rnd:NextInteger(1, #camada.ids)]
	s.Volume = camada.vol
	s.PlaybackSpeed = rnd:NextNumber(camada.pitch[1], camada.pitch[2]) * (pitchExtra or 1)
	s.SoundGroup = grupo(camada.grupo or "SFX")
	if pos then
		-- audio 3D: presente perto, some a ~70 studs (nao atravessa o mapa)
		local a = Instance.new("Attachment")
		a.WorldPosition = pos
		a.Parent = workspace.Terrain
		s.RollOffMode = Enum.RollOffMode.InverseTapered
		s.RollOffMinDistance = 10
		s.RollOffMaxDistance = 70
		s.Parent = a
		Debris:AddItem(a, 4)
	else
		s.Parent = SoundService
		Debris:AddItem(s, 4)
	end
	return s
end

-- toca um evento. opcoes: pos (Vector3, audio 3D), pitch (multiplicador), volume (multiplicador)
function S.tocar(nome, opcoes)
	local ev = EVENTOS[nome]
	if not ev then return end
	opcoes = opcoes or {}
	local agora = os.clock()
	local st = tocando[nome] or { ultimo = -1, vozes = 0 }
	tocando[nome] = st
	if agora - st.ultimo < ev.gap or st.vozes >= ev.max then return end
	st.ultimo = agora
	st.vozes += 1
	task.delay(0.6, function() st.vozes = math.max(0, st.vozes - 1) end)
	for _, camada in ipairs(ev.camadas) do
		local function play()
			local s = criarSom(camada, opcoes.pos, opcoes.pitch)
			if opcoes.volume then s.Volume *= opcoes.volume end
			s:Play()
		end
		if camada.atraso then task.delay(camada.atraso, play) else play() end
	end
end

-- coleta em sequencia: pitch sobe 4% por item (ate +40%), volta ao normal depois de 1,5 s parado
local combo, ultimaColeta = 0, 0
function S.coleta(pos)
	local agora = os.clock()
	if agora - ultimaColeta > 1.5 then combo = 0 end
	ultimaColeta = agora
	combo = math.min(combo + 1, 11)
	S.tocar("coleta", { pos = pos, pitch = 1 + 0.04 * (combo - 1) })
end

-- preferencias do jogador (Configuracoes): desligar uma categoria zera o volume do grupo, sem mexer nas outras
if game:GetService("RunService"):IsClient() then
	local jogador = game:GetService("Players").LocalPlayer
	local PREFERENCIAS = { SomMineracaoEnabled = "Mining", SomInterfaceEnabled = "UI" }
	for atributo, nome in pairs(PREFERENCIAS) do
		local function aplicar() grupo(nome).Volume = jogador:GetAttribute(atributo) == false and 0 or (GRUPOS[nome] or 1) end
		jogador:GetAttributeChangedSignal(atributo):Connect(aplicar)
		aplicar()
	end
end

local RAR_EVENTO = { comum = "drop_comum", incomum = "drop_comum", raro = "drop_raro", epico = "drop_epico", lendario = "drop_lendario", mitico = "drop_lendario", secreto = "drop_secreto" }
function S.drop(raridade) S.tocar(RAR_EVENTO[raridade] or "drop_comum") end

local VAR_QUEBRA = { comum = "break_comum", incomum = "break_incomum", raro = "break_raro", epica = "break_epico", lendaria = "break_lendario", chefe = "break_chefe" }
function S.quebra(variante, pos) S.tocar(VAR_QUEBRA[variante] or "break_comum", { pos = pos }) end

-- venda: o tamanho e medido pelo ganho em relacao ao que um minerio comum da ilha vale
function S.venda(ganho, itens)
	local n = itens or 1
	if n >= 120 then S.tocar("venda_jackpot")
	elseif n >= 50 then S.tocar("venda_grande")
	elseif n >= 12 then S.tocar("venda_media")
	else S.tocar("venda_pequena") end
end

return S

