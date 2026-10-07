-- DungeonService (ServerScriptService.Core) - MASMORRA DAS SOMBRAS da Ilha 3 (Shadow Garden).
-- Corrida de mineracao periodica: abre as XX:00 e XX:30 do relogio do servidor (workspace:GetServerTimeNow, UTC).
-- Reaproveita o que o jogo ja tem: minerios oficiais do tema (AreaBuilder.novoMinerio com posicao fixa), o golpe e a
-- quebra do Mineracao (minerio Temporario + evento Mineracao.Quebrou), PlayerData.darItem para os ingredientes,
-- FeedbackMina para os avisos. Nenhum DataStore novo; o estado global vai em atributos de RS.MasmorraEstado.
--
-- MAQUINA DE ESTADOS (explicita, uma por servidor; a corrida atual e a do slot S = inicio da abertura):
--   WAITING    -> COUNTDOWN   em S - CONTAGEM
--   COUNTDOWN  -> ENTRY_OPEN  em S            (abre a corrida; minerios nascem na 1a entrada)
--   ENTRY_OPEN -> RUNNING     em S + JANELA_ENTRADA (ninguem mais entra)
--   ENTRY_OPEN/RUNNING -> FINISHING em S + DURACAO, ou antes se TODOS os minerios da corrida cairem
--   FINISHING  -> RESETTING   depois de FINALIZANDO s (portal de saida aceso; bonus de limpeza ja entregue)
--   RESETTING  -> WAITING     depois de RESET s (quem ficou dentro volta; minerios somem; corrida apagada)
-- Regras de teste da missao:
--   ultimo segundo: o golpe so vale com a rocha viva e DungeonRun == corrida dona; RESETTING apaga as rochas
--   entrada atrasada: fora de ENTRY_OPEN a entrada e recusada (servidor), e o prompt some
--   morte/reset/sair: CharacterAdded/PlayerRemoving tiram o jogador da corrida; pode voltar SO durante ENTRY_OPEN e SO
--     neste servidor (perfil.masmorra = {slot, job}); recompensas ja dadas nao se repetem (chave por minerio+jogador)
--   servidor vazio: a maquina roda so com o relogio; nada nasce sem alguem entrar
--   ultimo minerio simultaneo: a quebra e unica (Mineracao ignora golpe com HP <= 0); o fim antecipado e o bonus sao
--     marcados ANTES de entregar (idempotentes)
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Config = require(RS.Config)
local Alq = require(RS:WaitForChild("AlquimiaConfig"))
local PlayerData = require(script.Parent.PlayerData)
local AreaBuilder = require(script.Parent.AreaBuilder)
local Mineracao = require(script.Parent.Mineracao)

local D = Alq.Masmorra
local S = {}
S.estado = "WAITING"
S.deslocamento = 0              -- so testes no Studio: desloca o relogio da masmorra (segundos)

local pasta                    -- RS.MasmorraEstado (atributos replicados)
local area, areaModel, marcas  -- area da Shadow Garden (tema sombra) e marcadores do export
local corrida                  -- { id, slot, participantes = {[player] = true}, dados = {[chave] = true}, rochas = {}, restantes, limpa }
local prompt, saida
local espirais = {}             -- pecas SG_Dun_R3_ExitSpiral* do export (so aparecem com a saida aberta)
local HRP = 3.5

local function agora() return workspace:GetServerTimeNow() + S.deslocamento end
local function slotAtual(t) return math.floor((t + D.CONTAGEM) / D.PERIODO) * D.PERIODO end

local function avisar(player, texto)
	RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area", texto = texto })
end
local function avisarIlha(texto)
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == area.id then avisar(p, texto) end
	end
end

local function marcador(nome) return marcas and marcas:FindFirstChild(nome) end
local function posMarcador(nome, dy)
	local m = marcador(nome)
	return m and (m.Position + Vector3.new(0, dy or 0, 0)) or nil
end

local function publicar(extra)
	if not pasta then return end
	local t = agora()
	local s = corrida and corrida.slot or slotAtual(t)
	if not corrida and t >= s then s = s + D.PERIODO end       -- esperando: a PROXIMA abertura
	pasta:SetAttribute("Estado", S.estado)
	pasta:SetAttribute("Slot", s)
	pasta:SetAttribute("AbreEm", s)
	pasta:SetAttribute("EntradaFechaEm", s + D.JANELA_ENTRADA)
	pasta:SetAttribute("FechaEm", corrida and corrida.fimEm or (s + D.DURACAO))
	pasta:SetAttribute("Deslocamento", S.deslocamento)
	local n = 0
	if corrida then for _ in pairs(corrida.participantes) do n += 1 end end
	pasta:SetAttribute("Participantes", n)
	pasta:SetAttribute("Restantes", corrida and corrida.restantes or 0)
	if prompt then
		prompt.Enabled = S.estado == "ENTRY_OPEN"
		prompt.ObjectText = "Masmorra das Sombras"
	end
end

-- ---------- recompensas (idempotentes por corrida) ----------
local function entregar(player, lista, chave)
	if not corrida or corrida.dados[chave] then return end
	corrida.dados[chave] = true                     -- marca ANTES de entregar
	local perfil = PlayerData.get(player)
	if not perfil then return end
	local partes = {}
	for _, par in ipairs(lista) do
		local dado = PlayerData.darItem(perfil, par[1], par[2])
		local def = Alq.item(par[1])
		if dado > 0 and def then table.insert(partes, "+" .. dado .. " " .. def.nome) end
	end
	if #partes > 0 then avisar(player, table.concat(partes, "  ")) end
	PlayerData.sincronizar(player)
end

-- ---------- participantes ----------
local function tirar(player, teleportar)
	if not corrida or not corrida.participantes[player] then return end
	corrida.participantes[player] = nil
	player:SetAttribute("DungeonRun", nil)
	if teleportar then
		local char = player.Character
		local ret = posMarcador("DUNGEON_Return", HRP)
		if char and ret and char:FindFirstChild("HumanoidRootPart") then
			char:PivotTo(CFrame.new(ret) * CFrame.Angles(0, math.pi, 0))
		end
	end
	publicar()
end

local function nascerMinerios()
	corrida.rochas = {}
	local folder = areaModel:FindFirstChild("Masmorra") or Instance.new("Folder")
	folder.Name = "Masmorra"        -- NAO e "Rochas": o SpawnMinerio/energia nao mexem aqui
	folder.Parent = areaModel
	local n = 0
	for _, m in ipairs(marcas:GetChildren()) do
		local rar = string.match(m.Name, "^DUN_ORE_%w+_(%u+)_%d+$")
		local variante = rar and Alq.VARIANTE_DO_MARCADOR[rar]
		if variante then
			local ok, grupo = pcall(AreaBuilder.novoMinerio, area, folder, nil, variante, m.Position)
			local hit = ok and grupo and grupo:FindFirstChild("Hitbox")
			if hit then
				local hp = math.max(1, math.floor((hit:GetAttribute("HPMax") or 1) * (D.HP_MULT[variante] or 0.5)))
				hit:SetAttribute("HPMax", hp)
				hit:SetAttribute("HP", hp)
				hit:SetAttribute("Temporario", true)
				hit:SetAttribute("DonoRun", corrida.id)
				hit:SetAttribute("ChaveMasmorra", m.Name)
				Mineracao.registrar(hit)
				corrida.rochas[hit] = variante
				n += 1
			elseif not ok then
				warn("[DungeonService] minerio " .. m.Name .. ": " .. tostring(grupo))
			end
		end
	end
	corrida.restantes = n
	corrida.nasceu = true
end

local function limparMinerios()
	local folder = areaModel and areaModel:FindFirstChild("Masmorra")
	if folder then folder:ClearAllChildren() end
end

-- ---------- entrada ----------
function S.entrar(player)
	if S.estado ~= "ENTRY_OPEN" or not corrida then
		return { ok = false, msg = S.estado == "COUNTDOWN" and "A Masmorra ainda nao abriu." or "A entrada da Masmorra esta fechada." }
	end
	local perfil = PlayerData.get(player)
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not perfil or not hrp or not hum or hum.Health <= 0 then return { ok = false } end
	if not perfil.areas[area.id] then return { ok = false, msg = "Desbloqueie o " .. area.nome .. " primeiro." } end
	local porta = posMarcador("DUNGEON_Entrance")
	if not porta or (hrp.Position - porta).Magnitude > 14 then return { ok = false, msg = "Chegue mais perto do portal." } end
	if corrida.participantes[player] then return { ok = false } end
	local n = 0
	for _ in pairs(corrida.participantes) do n += 1 end
	if n >= D.MAX_JOGADORES then return { ok = false, msg = "A Masmorra esta lotada." } end
	-- 1 corrida por abertura: pode voltar (morreu/saiu) so nesta abertura E neste servidor
	local mm = perfil.masmorra
	if mm.slot == corrida.slot and mm.job ~= game.JobId then return { ok = false, msg = "Voce ja entrou nesta abertura." } end
	mm.slot, mm.job = corrida.slot, game.JobId
	if not corrida.nasceu then nascerMinerios() end
	corrida.participantes[player] = true
	player:SetAttribute("DungeonRun", corrida.id)
	local sp = posMarcador("DUNGEON_Spawn", HRP)
	if sp then char:PivotTo(CFrame.new(sp) * CFrame.Angles(0, -math.pi / 2, 0)) end
	avisar(player, "Masmorra das Sombras: quebre os minerios antes do tempo acabar!")
	publicar()
	return { ok = true }
end

-- ---------- quebra de minerio da masmorra ----------
local function quebrou(rocha, quem, contribuintes)
	if not corrida or rocha:GetAttribute("DonoRun") ~= corrida.id then return end
	local variante = corrida.rochas[rocha]
	if not variante then return end
	corrida.rochas[rocha] = nil
	corrida.restantes = math.max(0, corrida.restantes - 1)
	local chave = rocha:GetAttribute("ChaveMasmorra") or tostring(rocha)
	local lista = D.RECOMPENSA[variante] or {}
	-- contribuintes chega como LISTA {player, ...} (o BindableEvent descarta chaves Instance de um mapa); quem quebrou
	-- sempre entra, entao uma lista vazia/antiga nunca deixa a corrida sem recompensa
	local alvos = { [quem] = true }
	for k, v in pairs(contribuintes or {}) do
		if typeof(v) == "Instance" then alvos[v] = true elseif typeof(k) == "Instance" then alvos[k] = true end
	end
	for p in pairs(alvos) do
		if typeof(p) == "Instance" and p.Parent and corrida.participantes[p] then
			entregar(p, lista, chave .. ":" .. p.UserId)
		end
	end
	if corrida.restantes == 0 and not corrida.limpa then
		corrida.limpa = true                            -- marca ANTES (ultimo minerio simultaneo)
		for p in pairs(corrida.participantes) do entregar(p, D.BONUS_LIMPEZA, "limpeza:" .. p.UserId) end
		corrida.fimEm = agora()
		for p in pairs(corrida.participantes) do avisar(p, "Masmorra limpa! O portal de saida se abriu.") end
		for sp, t0 in pairs(espirais) do sp.Transparency = t0 end
	end
	publicar()
end

-- ---------- transicoes ----------
local function entrarEstado(novo)
	if novo == S.estado then return end
	S.estado = novo
	if novo == "COUNTDOWN" then
		avisarIlha("A Masmorra das Sombras abre em " .. D.CONTAGEM .. " s!")
	elseif novo == "ENTRY_OPEN" then
		local s = slotAtual(agora())
		corrida = { id = "m" .. s, slot = s, participantes = {}, dados = {}, rochas = {}, restantes = 0, nasceu = false }
		avisarIlha("A Masmorra das Sombras abriu! Entre pelo portal da torre.")
	elseif novo == "RUNNING" then
		if corrida then for p in pairs(corrida.participantes) do avisar(p, "A entrada da Masmorra fechou.") end end
	elseif novo == "FINISHING" then
		if corrida then
			corrida.fimEm = corrida.fimEm or agora()
			for p in pairs(corrida.participantes) do avisar(p, "Fim da corrida! Saia pelo portal.") end
		end
	elseif novo == "RESETTING" then
		if corrida then
			for p in pairs(corrida.participantes) do tirar(p, true) end
		end
		limparMinerios()
	elseif novo == "WAITING" then
		if corrida then S.slotEncerrado = corrida.slot end
		corrida = nil
	end
	local aceso = novo == "FINISHING" or (corrida ~= nil and corrida.limpa == true)
	if saida then saida.Transparency = aceso and 0.35 or 0.8 end
	for p, t0 in pairs(espirais) do p.Transparency = aceso and t0 or 1 end
	publicar()
end

-- estado desejado pelo relogio (+ fim antecipado; slot ja encerrado nao reabre)
local function estadoPara(t)
	local s = slotAtual(t)
	local dt = t - s
	if dt < 0 then return "COUNTDOWN" end
	if S.slotEncerrado == s then return "WAITING" end
	local fim = s + D.DURACAO
	if corrida and corrida.slot == s and corrida.fimEm then fim = math.min(fim, corrida.fimEm) end
	if dt < D.JANELA_ENTRADA and t < fim then return "ENTRY_OPEN" end
	if t < fim then return "RUNNING" end
	if t < fim + D.FINALIZANDO then return "FINISHING" end
	if t < fim + D.FINALIZANDO + D.RESET then return "RESETTING" end
	return "WAITING"
end

-- ciclo explicito: cada transicao passa pelo estado seguinte (nenhum handler e pulado)
local CICLO = { WAITING = "COUNTDOWN", COUNTDOWN = "ENTRY_OPEN", ENTRY_OPEN = "RUNNING", RUNNING = "FINISHING",
	FINISHING = "RESETTING", RESETTING = "WAITING" }
local function passo()
	local alvo = estadoPara(agora())
	local n = 0
	while alvo ~= S.estado and n < 6 do
		n += 1
		-- fora de corrida (WAITING/COUNTDOWN) o relogio pode voltar ao comeco do ciclo sem abrir nada
		if (S.estado == "WAITING" or S.estado == "COUNTDOWN") and (alvo == "WAITING" or alvo == "COUNTDOWN") then
			entrarEstado(alvo)
		else
			entrarEstado(CICLO[S.estado])
		end
		alvo = estadoPara(agora())
	end
end

-- ---------- montagem ----------
local function acharArea()
	for _, a in ipairs(Config.Areas) do if a.tema == "sombra" then return a end end
end

function S.iniciar()
	area = acharArea()
	local areas = workspace:WaitForChild("Areas", 60)
	areaModel = area and areas and areas:WaitForChild("Area" .. area.id, 60)
	marcas = areaModel and areaModel:FindFirstChild("GAMEPLAY_MARKERS", true)
	pasta = RS:FindFirstChild("MasmorraEstado") or Instance.new("Folder")
	pasta.Name = "MasmorraEstado"
	pasta.Parent = RS
	if not (marcas and marcador("DUNGEON_Entrance") and marcador("DUNGEON_Spawn")) then
		pasta:SetAttribute("Estado", "INDISPONIVEL")
		warn("[DungeonService] marcadores da Masmorra nao encontrados (Ilha 3 ainda nao montada?)")
		return false
	end
	-- prompt de entrada no portal da torre (so habilitado em ENTRY_OPEN)
	local ent = marcador("DUNGEON_Entrance")
	local ancora = Instance.new("Part")
	ancora.Name = "MasmorraEntrada"; ancora.Size = Vector3.new(4, 6, 4); ancora.Anchored = true
	ancora.CanCollide = false; ancora.CanQuery = false; ancora.CanTouch = false; ancora.Transparency = 1
	ancora.CFrame = CFrame.new(ent.Position + Vector3.new(0, 3, 0)); ancora.Parent = areaModel
	prompt = Instance.new("ProximityPrompt")
	prompt.Name = "MasmorraPrompt"; prompt.ActionText = "Entrar"; prompt.ObjectText = "Masmorra das Sombras"
	prompt.MaxActivationDistance = 12; prompt.RequiresLineOfSight = false; prompt.HoldDuration = 0.4
	prompt.Enabled = false; prompt.Parent = ancora
	prompt.Triggered:Connect(function(player)
		local res = S.entrar(player)
		if res and res.msg then avisar(player, res.msg) end
	end)
	-- portal de saida (sala final): tocar = voltar para o patio (a qualquer momento)
	local ex = marcador("DUNGEON_ExitPortal")
	if ex then
		saida = Instance.new("Part")
		saida.Name = "MasmorraSaida"; saida.Size = Vector3.new(2, 10, 9); saida.Anchored = true; saida.CanCollide = false
		saida.CanQuery = false; saida.Material = Enum.Material.Neon; saida.Color = Color3.fromRGB(150, 100, 235)
		saida.Transparency = 0.8; saida.CFrame = CFrame.new(ex.Position + Vector3.new(0, 5.5, 0)); saida.Parent = areaModel
		saida.Touched:Connect(function(hit)
			local p = Players:GetPlayerFromCharacter(hit.Parent)
			if p and corrida and corrida.participantes[p] then tirar(p, true) end
		end)
	end
	for _, d in ipairs(areaModel:GetDescendants()) do
		if d:IsA("BasePart") and string.match(d.Name, "^SG_Dun_R3_ExitSpiral") then
			espirais[d] = d.Transparency
			d.Transparency = 1
		end
	end
	Mineracao.Quebrou.Event:Connect(quebrou)
	Players.PlayerRemoving:Connect(function(p) tirar(p, false) end)
	Players.PlayerAdded:Connect(function(p)
		p.CharacterAdded:Connect(function() if corrida and corrida.participantes[p] then tirar(p, false) end end)
	end)
	for _, p in ipairs(Players:GetPlayers()) do
		p.CharacterAdded:Connect(function() if corrida and corrida.participantes[p] then tirar(p, false) end end)
	end
	S.estado = "WAITING"
	S.slotEncerrado = slotAtual(agora())   -- servidor que sobe no meio de uma abertura espera a proxima
	if agora() < S.slotEncerrado then S.slotEncerrado = nil end
	passo()
	task.spawn(function()
		while true do
			local ok, err = pcall(passo)
			if not ok then warn("[DungeonService] " .. tostring(err)) end
			task.wait(0.25)
		end
	end)
	-- so no Studio: gancho de teste para os ganchos abaixo (a barra de comando nao enxerga este modulo ja carregado)
	if RunService:IsStudio() then
		local bf = game:GetService("ServerStorage"):FindFirstChild("DebugMasmorra") or Instance.new("BindableFunction")
		bf.Name = "DebugMasmorra"
		bf.OnInvoke = function(acao, a)
			if acao == "abrirEm" then return S.debugAbrirEm(a) end
			return S.debugEstado()
		end
		bf.Parent = game:GetService("ServerStorage")
	end
	return true
end

-- ---------- testes (Studio) ----------
-- faz a proxima abertura acontecer daqui a 'seg' segundos (desloca o relogio SO da masmorra)
function S.debugAbrirEm(seg)
	if not RunService:IsStudio() then return end
	local t = workspace:GetServerTimeNow()
	local prox = math.ceil((t + seg) / D.PERIODO) * D.PERIODO
	S.deslocamento = prox - (t + seg)
	publicar()
	return S.deslocamento
end
function S.debugEstado()
	local n = 0
	if corrida then for _ in pairs(corrida.participantes) do n += 1 end end
	return { estado = S.estado, corrida = corrida and corrida.id, participantes = n, restantes = corrida and corrida.restantes,
		dados = corrida and (function() local c = 0 for _ in pairs(corrida.dados) do c += 1 end return c end)() }
end
S.passo = passo
S.estadoPara = estadoPara

return S
