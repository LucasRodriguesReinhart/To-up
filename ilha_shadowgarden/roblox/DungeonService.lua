-- DungeonService (ServerScriptService.Core) - MASMORRA DAS SOMBRAS da Ilha 3 (Shadow Garden).
-- Corrida de mineracao periodica: abre as XX:00 e XX:30 do relogio do servidor (workspace:GetServerTimeNow, UTC).
-- Reaproveita o que o jogo ja tem: minerios oficiais do tema (AreaBuilder.novoMinerio com posicao fixa), o golpe e a
-- quebra do Mineracao (minerio Temporario + evento Mineracao.Quebrou), PlayerData.darItem para os ingredientes,
-- FeedbackMina para os avisos. Nenhum DataStore novo; o estado global vai em atributos de RS.MasmorraEstado.
--
-- MASMORRA INFINITA (ov09b, 2026-09-29): a corrida e uma SEQUENCIA SEM FIM DE SALAS. A R1 e a chegada; a sala 1 e a
-- R2 e depois alternam R3, R2, R3... (AlquimiaConfig.Masmorra.SALAS). Quando todos os minerios da sala atual caem, o
-- selo do vao R2-R3 abre, todo mundo ganha o bonus da sala e, depois de TRANSICAO s, o grupo e teleportado para o
-- spawn da proxima sala, que nasce com minerios novos. Dificuldade: nivel = 1 + floor((sala - 1) / SALAS_POR_NIVEL);
-- cada nivel sobe o HP, a chance de promover o minerio (epico/lendario) e a recompensa (tabela NIVEL da config).
-- A cada SALAS_POR_NIVEL salas limpas: bonus de MARCO (1 vez por jogador por marco). O tempo e POR SALA (TEMPO_SALA):
-- se acabar sem limpar, a corrida termina. O portal de saida (R3) e o portal de chegada da R1 (prompt "Sair") ficam
-- disponiveis a qualquer momento: sai com o que ja ganhou.
--
-- MAQUINA DE ESTADOS (explicita, uma por servidor; a corrida atual e a do slot S = inicio da abertura):
--   WAITING    -> COUNTDOWN   em S - CONTAGEM
--   COUNTDOWN  -> ENTRY_OPEN  em S            (abre a corrida; a sala 1 nasce na 1a entrada)
--   ENTRY_OPEN -> RUNNING     em S + JANELA_ENTRADA (ninguem mais entra)
--   ENTRY_OPEN/RUNNING -> FINISHING quando a corrida marca fimEm:
--       o TEMPO DA SALA atual acabou sem limpar | ninguem mais dentro (so depois da janela de entrada) |
--       teto de seguranca S + DURACAO_MAX (a corrida acaba antes da contagem da proxima abertura)
--   FINISHING  -> RESETTING   depois de FINALIZANDO s (portal de saida aceso; minerios travados)
--   RESETTING  -> WAITING     depois de RESET s (quem ficou dentro volta; minerios somem; corrida apagada)
-- Garantias (testes da missao):
--   ultimo segundo: o golpe so vale com a rocha viva e DungeonRun == corrida dona; no fim da corrida as rochas perdem
--     o dono (ninguem golpeia) e RESETTING as apaga
--   entrada atrasada: fora de ENTRY_OPEN a entrada e recusada (servidor), e o prompt some
--   morte/reset/sair: CharacterAdded/PlayerRemoving tiram o jogador da corrida; pode voltar SO durante ENTRY_OPEN e SO
--     neste servidor (perfil.masmorra = {slot, job}); recompensas ja dadas nao se repetem (chave sala+minerio+jogador)
--   servidor vazio: a maquina roda so com o relogio; nada nasce sem alguem entrar
--   ultimo minerio simultaneo: a quebra e unica (Mineracao ignora golpe com HP <= 0; a rocha sai da tabela antes de
--     contar); a sala limpa, o bonus e o marco sao marcados ANTES de entregar (idempotentes); a troca de sala confere
--     corrida e sala no task.delay (uma troca so)
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Config = require(RS.Config)
local Alq = require(RS:WaitForChild("AlquimiaConfig"))
local PlayerData = require(script.Parent.PlayerData)
local AreaBuilder = require(script.Parent.AreaBuilder)
local Mineracao = require(script.Parent.Mineracao)

local D = Alq.Masmorra
local N = D.NIVEL or {}
local S = {}
S.estado = "WAITING"
S.deslocamento = 0              -- so testes no Studio: desloca o relogio da masmorra (segundos)

local pasta                    -- RS.MasmorraEstado (atributos replicados)
local area, areaModel, marcas  -- area da Shadow Garden (tema sombra) e marcadores do export
-- corrida = { id, slot, participantes = {[player] = true}, dados = {[chave] = true}, rochas = {[hit] = variante},
--             restantes, nasceu, sala, nivel, fimSala, transicao, limpas = {[sala] = true}, fimEm }
local corrida
local prompt
local promptsSair = {}          -- prompts "Sair" (DUN_EXIT_R1, DUN_EXIT_R3)
local espirais = {}             -- pecas SG_Dun_R3_ExitSpiral* do export (acesas enquanto ha corrida)
local pontos = {}               -- [sala fisica] = { {nome, pos, rar}, ... } (marcadores DUN_ORE_<sala>_<RAR>_<nn>)
local HRP = 3.5
local GIRO = CFrame.Angles(0, -math.pi / 2, 0)   -- a mesma orientacao do spawn da R1 (as salas estao em fila)

local RANK = { comum = 1, incomum = 2, epica = 3, lendaria = 4 }
local ORDEM = { "comum", "incomum", "epica", "lendaria" }

local function agora() return workspace:GetServerTimeNow() + S.deslocamento end
local function slotAtual(t) return math.floor((t + D.CONTAGEM) / D.PERIODO) * D.PERIODO end

-- ---------- dificuldade (formulas em AlquimiaConfig.Masmorra) ----------
local function nivelDe(sala) return 1 + math.floor((sala - 1) / (D.SALAS_POR_NIVEL or 5)) end
local function salaFisica(sala)
	local ciclo = D.SALAS or { "R2", "R3" }
	return ciclo[((sala - 1) % #ciclo) + 1]
end
local function fator(nivel, porNivel) return 1 + (porNivel or 0) * (nivel - 1) end
-- lista de recompensa {{item, qtd}} escalada pelo nivel (nunca menos que a base)
local function escalar(lista, nivel)
	local f = fator(nivel, N.RECOMPENSA_POR_NIVEL)
	local out = {}
	for _, par in ipairs(lista or {}) do
		table.insert(out, { par[1], math.max(par[2], math.floor(par[2] * f + 0.5)) })
	end
	return out
end
-- raridade do ponto no nivel: o marcador e o PISO; cada nivel acima do 1 da chance de subir 1 degrau (e de novo, a mesma
-- chance, para o 2o); lendaria so nos pontos espacados para o minerio grande (N.TETO_LENDARIA)
local function promover(varianteBase, rarMarcador, nivel, rng)
	local p = math.min(N.PROMOCAO_MAX or 0.6, (N.PROMOCAO_POR_NIVEL or 0) * (nivel - 1))
	local r = RANK[varianteBase] or 1
	local base = r
	if p > 0 and rng:NextNumber() < p then
		r += 1
		if rng:NextNumber() < p then r += 1 end
	end
	local teto = (N.TETO_LENDARIA and N.TETO_LENDARIA[rarMarcador]) and 4 or 3
	r = math.max(base, math.min(r, teto))
	return ORDEM[r]
end

local function avisar(player, texto)
	RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area", texto = texto })
end
local function avisarIlha(texto)
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == area.id then avisar(p, texto) end
	end
end
local function avisarCorrida(texto)
	if not corrida then return end
	for p in pairs(corrida.participantes) do avisar(p, texto) end
end

local function marcador(nome) return marcas and marcas:FindFirstChild(nome) end
local function posMarcador(nome, dy)
	local m = marcador(nome)
	return m and (m.Position + Vector3.new(0, dy or 0, 0)) or nil
end
-- spawn de cada sala: DUN_SPAWN_<sala> (R1 = DUNGEON_Spawn); sem o marcador, cai na chegada (R1) e avisa
local function spawnDaSala(sala)
	local p = (sala ~= "R1" and posMarcador("DUN_SPAWN_" .. sala)) or posMarcador("DUNGEON_Spawn")
	if sala ~= "R1" and not marcador("DUN_SPAWN_" .. sala) then
		warn("[DungeonService] marcador DUN_SPAWN_" .. sala .. " nao encontrado: usando DUNGEON_Spawn")
	end
	return p
end
-- o grupo chega espalhado (centro + anel de 4 + anel de 7,5): ninguem nasce dentro do outro
local function posGrupo(base, i)
	if not base or i <= 1 then return base end
	local k, n, r = i - 2, 6, 4
	if i > 7 then k, n, r = i - 8, 8, 7.5 end
	local a = 2 * math.pi * k / n
	return base + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
end
-- frente de um marcador (fwd_x/fwd_z do export; a ilha e GIRADA no mundo, nada pode nascer alinhado aos eixos)
local function frenteMarcador(nome)
	local m = marcador(nome)
	if not m then return nil end
	local fx, fz = m:GetAttribute("fwd_x"), m:GetAttribute("fwd_z")
	if fx and fz and (fx ~= 0 or fz ~= 0) then return Vector3.new(fx, 0, fz).Unit end
	local lv = m.CFrame.LookVector
	return Vector3.new(lv.X, 0, lv.Z).Magnitude > 1e-3 and Vector3.new(lv.X, 0, lv.Z).Unit or nil
end
local function cfMarcador(nome, dy)
	local m = marcador(nome)
	if not m then return nil end
	local pos = m.Position + Vector3.new(0, dy or 0, 0)
	local f = frenteMarcador(nome) or Vector3.new(0, 0, -1)
	return CFrame.lookAt(pos, pos + f)
end
local function frenteDaSala(sala)
	return (sala ~= "R1" and frenteMarcador("DUN_SPAWN_" .. sala)) or frenteMarcador("DUNGEON_Spawn")
end
local function teleportar(player, pos, frente)
	local char = player.Character
	if char and pos and char:FindFirstChild("HumanoidRootPart") then
		pcall(function() player:RequestStreamAroundAsync(pos, 4) end)   -- o subsolo pode estar recolhido no cliente
		local alvo = pos + Vector3.new(0, HRP, 0)
		if frente then char:PivotTo(CFrame.lookAt(alvo, alvo + frente)) else char:PivotTo(CFrame.new(alvo) * GIRO) end
	end
end

local function contar(t) local n = 0 for _ in pairs(t) do n += 1 end return n end

local function publicar()
	if not pasta then return end
	local t = agora()
	local s = corrida and corrida.slot or slotAtual(t)
	if not corrida and t >= s then s = s + D.PERIODO end       -- esperando: a PROXIMA abertura
	pasta:SetAttribute("Estado", S.estado)
	pasta:SetAttribute("Slot", s)
	pasta:SetAttribute("AbreEm", s)
	pasta:SetAttribute("EntradaFechaEm", s + D.JANELA_ENTRADA)
	-- FechaEm (a UI ja usa): o prazo que vale agora = o fim da SALA atual (ou o fim da corrida em FINISHING)
	local fimSala = corrida and corrida.fimSala or 0
	pasta:SetAttribute("FechaEm", corrida and (corrida.fimEm or (corrida.nasceu and fimSala) or (s + D.DURACAO_MAX))
		or (s + D.DURACAO_MAX))
	pasta:SetAttribute("Deslocamento", S.deslocamento)
	pasta:SetAttribute("Participantes", corrida and contar(corrida.participantes) or 0)
	pasta:SetAttribute("Restantes", corrida and corrida.restantes or 0)
	-- masmorra infinita: sala atual, nivel, prazo da sala (timestamp GetServerTimeNow) e troca de sala em curso
	pasta:SetAttribute("Sala", corrida and corrida.sala or 0)
	pasta:SetAttribute("Nivel", corrida and corrida.nivel or 1)
	pasta:SetAttribute("FimSala", fimSala)
	pasta:SetAttribute("Transicao", corrida ~= nil and corrida.transicao == true)
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

-- ---------- portal da proxima sala (um por arena: DUN_NEXT_<sala fisica>, DENTRO do vao/nicho) ----------
-- fechado durante a sala (parede escura colidivel); aberto quando a sala limpa (brilho, atravessavel, tocar = seguir)
local selos = {}                 -- [salaFisica] = Part
local function abrirSelo(aberto)
	local atual = corrida and corrida.sala and corrida.sala > 0 and salaFisica(corrida.sala)
	for salaF, sp in pairs(selos) do
		local este = aberto and (salaF == atual or not atual)
		sp.CanCollide = not este
		sp.CanTouch = este
		sp.Transparency = este and 0.25 or 0.55
		sp.Color = este and Color3.fromRGB(170, 120, 255) or Color3.fromRGB(70, 44, 128)
	end
	-- a espiral do nicho da R3 (SG_Dun_R3_ExitSpiral) acende junto com o portal da R3 aberto
	local r3aberto = aberto and atual == "R3"
	for p, t0 in pairs(espirais) do p.Transparency = r3aberto and t0 or 1 end
end

-- ---------- participantes ----------
local function tirar(player, teleportarAoPatio)
	if not corrida or not corrida.participantes[player] then return end
	corrida.participantes[player] = nil
	player:SetAttribute("DungeonRun", nil)
	if teleportarAoPatio then
		local char = player.Character
		local ret = posMarcador("DUNGEON_Return")
		if char and ret and char:FindFirstChild("HumanoidRootPart") then
			teleportar(player, ret, frenteMarcador("DUNGEON_Return"))
		end
	end
	publicar()
end

local function limparMinerios()
	local folder = areaModel and areaModel:FindFirstChild("Masmorra")
	if folder then folder:ClearAllChildren() end
	if corrida then corrida.rochas = {} end
end

-- minerios NOVOS nos pontos da sala fisica, com a raridade e o HP do nivel
local function nascerMinerios(salaF)
	corrida.rochas = {}
	local folder = areaModel:FindFirstChild("Masmorra") or Instance.new("Folder")
	folder.Name = "Masmorra"        -- NAO e "Rochas": o SpawnMinerio/energia nao mexem aqui
	folder.Parent = areaModel
	local nivel = corrida.nivel
	local rng = Random.new(corrida.slot + corrida.sala * 7919)
	local hpF = fator(nivel, N.HP_POR_NIVEL)
	local n = 0
	for _, pt in ipairs(pontos[salaF] or {}) do
		local base = Alq.VARIANTE_DO_MARCADOR[pt.rar]
		local variante = base and promover(base, pt.rar, nivel, rng)
		if variante then
			local ok, grupo = pcall(AreaBuilder.novoMinerio, area, folder, nil, variante, pt.pos)
			local hit = ok and grupo and grupo:FindFirstChild("Hitbox")
			if hit then
				local hp = math.max(1, math.floor((hit:GetAttribute("HPMax") or 1) * (D.HP_MULT[variante] or 0.5) * hpF))
				hit:SetAttribute("HPMax", hp)
				hit:SetAttribute("HP", hp)
				hit:SetAttribute("Temporario", true)
				hit:SetAttribute("DonoRun", corrida.id)
				hit:SetAttribute("DonoSala", corrida.sala)
				hit:SetAttribute("NivelMasmorra", nivel)
				hit:SetAttribute("ChaveMasmorra", corrida.sala .. ":" .. pt.nome)
				Mineracao.registrar(hit)
				corrida.rochas[hit] = variante
				n += 1
			elseif not ok then
				warn("[DungeonService] minerio " .. pt.nome .. ": " .. tostring(grupo))
			end
		end
	end
	corrida.restantes = n
	if n == 0 then warn("[DungeonService] sala " .. salaF .. " sem minerio (marcadores DUN_ORE_" .. salaF .. "_* ?)") end
end

-- comeca a sala 'n' (1 = primeira entrada; > 1 = troca): minerios novos, prazo novo, grupo teleportado, selo fechado
local function iniciarSala(n)
	if not corrida or corrida.fimEm then return end
	local nivelAntes = corrida.nivel or 1
	corrida.sala = n
	corrida.nivel = nivelDe(n)
	corrida.transicao = false
	corrida.nasceu = true
	limparMinerios()
	local salaF = salaFisica(n)
	nascerMinerios(salaF)
	corrida.fimSala = agora() + D.TEMPO_SALA
	if n > 1 then
		local base, frente = spawnDaSala(salaF), frenteDaSala(salaF)
		local i = 0
		for p in pairs(corrida.participantes) do
			i += 1
			teleportar(p, posGrupo(base, i), frente)
		end
	end
	abrirSelo(false)                               -- depois do teleporte: ninguem fica preso no vao
	avisarCorrida("Sala " .. n .. "  (Nivel " .. corrida.nivel .. ")")
	if corrida.nivel > nivelAntes then
		avisarCorrida("Nivel " .. corrida.nivel .. "! Minerios mais fortes e mais raros.")
	end
	publicar()
end

local function finalizar(msg)
	if not corrida or corrida.fimEm then return end
	corrida.fimEm = agora()
	-- rochas travadas: sem dono, ninguem golpeia mais (RESETTING apaga)
	for rocha in pairs(corrida.rochas) do rocha:SetAttribute("DonoRun", "fim") end
	if msg then avisarCorrida(msg) end
	publicar()
end

-- sala atual limpa: bonus (e marco), selo aberto, troca agendada
local function salaLimpa()
	local sala = corrida.sala
	if corrida.limpas[sala] then return end
	corrida.limpas[sala] = true                     -- marca ANTES (ultimo minerio simultaneo)
	local nivel = corrida.nivel
	local bonus = escalar(D.BONUS_LIMPEZA, nivel)
	for p in pairs(corrida.participantes) do entregar(p, bonus, "limpeza:" .. sala .. ":" .. p.UserId) end
	if sala % (D.SALAS_POR_NIVEL or 5) == 0 then
		local marco = escalar(D.BONUS_MARCO, nivel)
		for p in pairs(corrida.participantes) do
			avisar(p, "MARCO! " .. sala .. " salas vencidas.")
			entregar(p, marco, "marco:" .. sala .. ":" .. p.UserId)
		end
	end
	corrida.transicao = true
	corrida.fimSala = agora() + D.TRANSICAO + D.TEMPO_SALA   -- ja publica o prazo da proxima sala
	abrirSelo(true)
	avisarCorrida("Sala " .. sala .. " limpa! A passagem se abriu.")
	local id = corrida.id
	task.delay(D.TRANSICAO, function()
		if corrida and corrida.id == id and corrida.sala == sala and corrida.transicao and not corrida.fimEm then
			iniciarSala(sala + 1)
		end
	end)
	publicar()
end

-- ---------- entrada ----------
function S.entrar(player)
	if S.estado ~= "ENTRY_OPEN" or not corrida or corrida.fimEm then
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
	if contar(corrida.participantes) >= D.MAX_JOGADORES then return { ok = false, msg = "A Masmorra esta lotada." } end
	-- 1 corrida por abertura: pode voltar (morreu/saiu) so nesta abertura E neste servidor
	local mm = perfil.masmorra
	if mm.slot == corrida.slot and mm.job ~= game.JobId then return { ok = false, msg = "Voce ja entrou nesta abertura." } end
	mm.slot, mm.job = corrida.slot, game.JobId
	corrida.participantes[player] = true
	player:SetAttribute("DungeonRun", corrida.id)
	if not corrida.nasceu then iniciarSala(1) end
	-- sala 1: chega pela R1 (a chegada) e anda ate a R2; depois dela: direto no spawn da sala atual
	local destino = corrida.sala <= 1 and posMarcador("DUNGEON_Spawn") or spawnDaSala(salaFisica(corrida.sala))
	teleportar(player, posGrupo(destino, contar(corrida.participantes)))
	avisar(player, "Masmorra das Sombras: limpe cada sala antes do tempo acabar! Sala " .. corrida.sala
		.. " (Nivel " .. corrida.nivel .. ")")
	publicar()
	return { ok = true }
end

-- ---------- quebra de minerio da masmorra ----------
local function quebrou(rocha, quem, contribuintes)
	if not corrida or corrida.fimEm or rocha:GetAttribute("DonoRun") ~= corrida.id then return end
	local variante = corrida.rochas[rocha]
	if not variante or rocha:GetAttribute("DonoSala") ~= corrida.sala then return end
	corrida.rochas[rocha] = nil                     -- sai da tabela ANTES de contar (quebra unica)
	corrida.restantes = math.max(0, corrida.restantes - 1)
	local chave = rocha:GetAttribute("ChaveMasmorra") or tostring(rocha)
	local lista = escalar(D.RECOMPENSA[variante], rocha:GetAttribute("NivelMasmorra") or corrida.nivel)
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
	if corrida.restantes == 0 then salaLimpa() end
	publicar()
end

-- ---------- fim da corrida pelo relogio da sala / corrida vazia / teto ----------
local function verificar(t)
	if not corrida or corrida.fimEm then return end
	if S.estado ~= "ENTRY_OPEN" and S.estado ~= "RUNNING" then return end
	if t >= corrida.slot + D.DURACAO_MAX then
		finalizar("A Masmorra vai fechar: tempo maximo da abertura.")
	elseif corrida.nasceu and not corrida.transicao and corrida.fimSala and t >= corrida.fimSala then
		finalizar("O tempo da Sala " .. corrida.sala .. " acabou! Fim da corrida.")
	elseif S.estado == "RUNNING" and next(corrida.participantes) == nil then
		finalizar(nil)                               -- todos sairam, morreram ou deslogaram
	end
end

-- ---------- transicoes ----------
local function entrarEstado(novo)
	if novo == S.estado then return end
	S.estado = novo
	if novo == "COUNTDOWN" then
		avisarIlha("A Masmorra das Sombras abre em " .. D.CONTAGEM .. " s!")
	elseif novo == "ENTRY_OPEN" then
		local s = slotAtual(agora())
		corrida = { id = "m" .. s, slot = s, participantes = {}, dados = {}, rochas = {}, restantes = 0, nasceu = false,
			sala = 0, nivel = 1, limpas = {}, transicao = false }
		abrirSelo(false)
		avisarIlha("A Masmorra das Sombras abriu! Entre pelo portal da caverna.")
	elseif novo == "RUNNING" then
		avisarCorrida("A entrada da Masmorra fechou.")
	elseif novo == "FINISHING" then
		if corrida then
			finalizar(nil)
			avisarCorrida("Fim da corrida! Voce chegou a Sala " .. corrida.sala .. ". Saia pelo portal.")
		end
	elseif novo == "RESETTING" then
		if corrida then
			for p in pairs(corrida.participantes) do tirar(p, true) end
		end
		limparMinerios()
		abrirSelo(false)
	elseif novo == "WAITING" then
		if corrida then S.slotEncerrado = corrida.slot end
		corrida = nil
	end
	-- portal de saida: aceso durante toda a corrida (sair a qualquer momento), apagado sem corrida
	local aceso = corrida ~= nil and (novo == "ENTRY_OPEN" or novo == "RUNNING" or novo == "FINISHING")
	if not aceso then for p in pairs(espirais) do p.Transparency = 1 end end   -- espiral = visual do DUN_NEXT_R3 (abrirSelo)
	for _, ps in ipairs(promptsSair) do ps.Enabled = aceso end
	publicar()
end

-- estado desejado pelo relogio (+ fim marcado pela corrida; slot ja encerrado nao reabre)
local function estadoPara(t)
	local s = slotAtual(t)
	local dt = t - s
	if dt < 0 then return "COUNTDOWN" end
	if S.slotEncerrado == s then return "WAITING" end
	local fim = s + D.DURACAO_MAX
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
	verificar(agora())
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
		verificar(agora())
		alvo = estadoPara(agora())
	end
end

-- ---------- montagem ----------
local function acharArea()
	for _, a in ipairs(Config.Areas) do if a.tema == "sombra" then return a end end
end

local function lerPontos()
	pontos = {}
	local n = 0
	for _, m in ipairs(marcas:GetChildren()) do
		local sala, rar = string.match(m.Name, "^DUN_ORE_(%w+)_(%u+)_%d+$")
		if sala and Alq.VARIANTE_DO_MARCADOR[rar] then
			pontos[sala] = pontos[sala] or {}
			table.insert(pontos[sala], { nome = m.Name, pos = m.Position, rar = rar })
			n += 1
		end
	end
	for _, lista in pairs(pontos) do table.sort(lista, function(a, b) return a.nome < b.nome end) end
	return n
end

-- portais da proxima sala: DUN_NEXT_R2 (plano medio do vao R2-R3) e DUN_NEXT_R3 (nicho do muro norte da R3), com o
-- CFrame do marcador (frente = eixo das salas). Sem esses marcadores (export antigo), cai no selo unico do DUN_LINK_R2R3,
-- agora com a parede NO vao (largura perpendicular ao eixo das salas).
local function portal(salaF, cf, w, h, t)
	local sp = Instance.new("Part")
	sp.Name = "MasmorraProxima_" .. salaF; sp.Anchored = true; sp.CanQuery = false; sp.CanTouch = false
	sp.Material = Enum.Material.Neon; sp.Color = Color3.fromRGB(70, 44, 128); sp.CastShadow = false
	sp.Size = Vector3.new(w, h, t)
	sp.CFrame = cf * CFrame.new(0, h / 2, 0)
	sp.Parent = areaModel
	selos[salaF] = sp
end
-- quem chega PERTO do portal aberto segue na hora (caixa do portal + 4 de folga na espessura e 2 nas bordas).
-- Por proximidade e nao por Touched: o portal do nicho da R3 fica atras de soleira/colunelos e o toque falhava.
task.spawn(function()
	while true do
		task.wait(0.2)
		if corrida and corrida.transicao and not corrida.fimEm and corrida.sala and corrida.sala > 0 then
			local sp = selos[salaFisica(corrida.sala)]
			if sp then
				for p in pairs(corrida.participantes) do
					local hrp = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
					if hrp then
						local l = sp.CFrame:PointToObjectSpace(hrp.Position)
						if math.abs(l.X) <= sp.Size.X / 2 + 2 and math.abs(l.Y) <= sp.Size.Y / 2 + 2 and math.abs(l.Z) <= 5 then
							iniciarSala(corrida.sala + 1)      -- uma vez so: iniciarSala desliga a transicao
							break
						end
					end
				end
			end
		end
	end
end)
local function criarSelo()
	local cfg = D.SELO or {}
	local n = 0
	for _, salaF in ipairs(D.SALAS or { "R2", "R3" }) do
		local m = marcador("DUN_NEXT_" .. salaF)
		if m then
			portal(salaF, cfMarcador("DUN_NEXT_" .. salaF), m:GetAttribute("w") or cfg.largura or 27,
				m:GetAttribute("h") or cfg.altura or 21, m:GetAttribute("t") or cfg.espessura or 1)
			n += 1
		end
	end
	if n > 0 then abrirSelo(false) return end
	local link = marcador("DUN_LINK_R2R3")
	local r2, r3 = marcador("DUN_ROOM_R2"), marcador("DUN_ROOM_R3")
	if not (link and r2 and r3) then
		warn("[DungeonService] sem DUN_NEXT_* nem DUN_LINK_R2R3: sem portal entre as salas")
		return
	end
	local dir = Vector3.new(r3.Position.X - r2.Position.X, 0, r3.Position.Z - r2.Position.Z).Unit
	local lado = Vector3.new(-dir.Z, 0, dir.X)
	portal("R2", CFrame.fromMatrix(link.Position, lado, Vector3.new(0, 1, 0)), link:GetAttribute("w") or cfg.largura or 18,
		link:GetAttribute("h") or cfg.altura or 14, (link:GetAttribute("t") or cfg.espessura or 2) * 0.5)
	abrirSelo(false)
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
	local np = lerPontos()
	if np == 0 then warn("[DungeonService] nenhum marcador DUN_ORE_* encontrado") end
	-- prompt de entrada no portal da caverna (so habilitado em ENTRY_OPEN)
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
	-- saidas SO por prompt (a barreira de toque antiga ficava para fora da sala): DUN_EXIT_R1 e DUN_EXIT_R3
	-- (DUNGEON_ExitPortal = alias da R3 em export antigo). "Sair" a qualquer momento, com o que ja ganhou.
	for _, nome in ipairs({ "DUN_EXIT_R1", marcador("DUN_EXIT_R3") and "DUN_EXIT_R3" or "DUNGEON_ExitPortal" }) do
		local ex = marcador(nome)
		if ex then
			local a1 = Instance.new("Part")
			a1.Name = "MasmorraSaida_" .. nome; a1.Size = Vector3.new(4, 8, 4); a1.Anchored = true; a1.CanCollide = false
			a1.CanQuery = false; a1.CanTouch = false; a1.Transparency = 1
			a1.CFrame = cfMarcador(nome, 4); a1.Parent = areaModel
			local ps = Instance.new("ProximityPrompt")
			ps.Name = "MasmorraSairPrompt"; ps.ActionText = "Sair"; ps.ObjectText = "Masmorra das Sombras"
			ps.MaxActivationDistance = 12; ps.RequiresLineOfSight = false; ps.HoldDuration = 0.6
			ps.Enabled = false; ps.Parent = a1
			ps.Triggered:Connect(function(p)
				if corrida and corrida.participantes[p] then
					avisar(p, "Voce saiu da Masmorra (Sala " .. corrida.sala .. ").")
					tirar(p, true)
				end
			end)
			table.insert(promptsSair, ps)
		end
	end
	if #promptsSair == 0 then warn("[DungeonService] sem DUN_EXIT_R1/DUN_EXIT_R3: nenhuma saida por prompt") end
	criarSelo()
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
	-- so no Studio: gancho de teste (a barra de comando nao enxerga este modulo ja carregado)
	--   Invoke("abrirEm", seg) | Invoke("estado") | Invoke("pularSala", n) | Invoke("fimSala") | Invoke("limparSala")
	if RunService:IsStudio() then
		local bf = game:GetService("ServerStorage"):FindFirstChild("DebugMasmorra") or Instance.new("BindableFunction")
		bf.Name = "DebugMasmorra"
		bf.OnInvoke = function(acao, a)
			if acao == "abrirEm" then return S.debugAbrirEm(a) end
			if acao == "pularSala" then return S.debugPularSala(a) end
			if acao == "fimSala" then return S.debugFimSala() end
			if acao == "limparSala" then return S.debugLimparSala() end
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
	-- a abertura que ja foi usada neste servidor nao reabre (slotEncerrado): o teste vai para a seguinte
	while S.slotEncerrado and prox <= S.slotEncerrado do prox += D.PERIODO end
	S.deslocamento = prox - (t + seg)
	publicar()
	return S.deslocamento
end
-- pula direto para a sala n (minerios da sala atual somem SEM recompensa; o grupo e teleportado)
function S.debugPularSala(n)
	if not RunService:IsStudio() or not corrida or corrida.fimEm or not corrida.nasceu then return "sem corrida ativa" end
	n = math.max(1, math.floor(tonumber(n) or 1))
	corrida.nivel = nivelDe(math.max(1, n - 1))     -- o aviso de "Nivel X" sai se a sala n abre um nivel novo
	iniciarSala(n)
	return S.debugEstado()
end
-- forca o fim do tempo da sala atual (a corrida termina no proximo passo)
function S.debugFimSala()
	if not RunService:IsStudio() or not corrida or corrida.fimEm then return "sem corrida ativa" end
	corrida.transicao = false
	corrida.fimSala = agora() - 1
	return S.debugEstado()
end
-- limpa a sala atual como se o ultimo minerio tivesse caido (bonus/marco/troca normais; sem recompensa por minerio)
function S.debugLimparSala()
	if not RunService:IsStudio() or not corrida or corrida.fimEm or not corrida.nasceu or corrida.transicao then
		return "sem sala ativa"
	end
	limparMinerios()
	corrida.restantes = 0
	salaLimpa()
	return S.debugEstado()
end
function S.debugEstado()
	return { estado = S.estado, corrida = corrida and corrida.id, participantes = corrida and contar(corrida.participantes) or 0,
		sala = corrida and corrida.sala, salaFisica = corrida and corrida.sala > 0 and salaFisica(corrida.sala) or nil,
		nivel = corrida and corrida.nivel, restantes = corrida and corrida.restantes,
		tempoSala = corrida and corrida.fimSala and math.floor(corrida.fimSala - agora()) or nil,
		transicao = corrida and corrida.transicao, dados = corrida and contar(corrida.dados) }
end
S.passo = passo
S.estadoPara = estadoPara
S.nivelDe = nivelDe
S.salaFisica = salaFisica

return S
