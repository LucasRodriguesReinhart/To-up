-- BossService: chefe GLOBAL cooperativo por ilha (economia v3.1 + analise de sensibilidade).
--  * nasce a cada CHEFE_QUEBRAS_SERVIDOR quebras somadas do servidor na ilha,
--    nunca antes de intervaloMin (servidor cheio) e sempre ate intervaloMax (servidor vazio), se houver alguem na ilha
--  * HP da luta = HP base x (jogadores ativos / 4): sozinho a luta dura o mesmo que em grupo
--  * recompensa pelo HP BASE: quem causou >= 2% do HP da luta recebe tudo (moedas + 4 hats de sorte alta);
--    abaixo disso recebe moedas proporcionais e nenhum hat
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local AreaBuilder = require(script.Parent.AreaBuilder)
local Economia = require(script.Parent.Economia)
local Telemetria = require(script.Parent.Telemetria)
local Recompensas = require(script.Parent.Recompensas)

local B = {}
local CH = Config.CHEFE
local estado = {}      -- [areaId] = { quebras, ultimoSpawn, vivos = { [hit] = luta } }
local Mineracao         -- injetado em B.iniciar (evita require circular)

local function est(areaId)
	estado[areaId] = estado[areaId] or { quebras = 0, ultimoSpawn = os.clock(), vivos = {} }
	return estado[areaId]
end

local function avisarIlha(areaId, texto)
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == areaId then
			RS.Remotes.FeedbackMina:FireClient(p, { tipo = "area", texto = texto })
		end
	end
end

local function qualquerJogadorNaIlha(areaId)
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == areaId and PlayerData.get(p) then return p end
	end
end

function B.vivos(areaId)
	local n = 0
	for hit in pairs(est(areaId).vivos) do
		if hit.Parent then n += 1 else est(areaId).vivos[hit] = nil end
	end
	return n
end

-- nasce um chefe; motivo = "quebras" | "tempo_max" | "invocado"
function B.nascer(areaId, motivo, invocador)
	local area = Config.areaPorId(areaId)
	if not area then return false end
	local e = est(areaId)
	local ativos = math.max(1, Economia.ativosNaArea(areaId))
	local hpLuta = area.hp.super * ativos / CH.hpEscalaJogadores
	local ok, grupo = pcall(AreaBuilder.novoChefe, area, hpLuta)
	local hit = ok and grupo and grupo:FindFirstChild("Hitbox")
	if not hit then
		warn("[BossService] nao foi possivel criar o chefe na area " .. areaId .. ": " .. tostring(grupo))
		return false
	end
	local agora = os.clock()
	hit:SetAttribute("HPBase", area.hp.super)
	hit:SetAttribute("AtivosNoSpawn", ativos)
	e.vivos[hit] = { hpLuta = hpLuta, dano = {}, nasceu = agora, ativos = ativos,
		desdeAnterior = agora - e.ultimoSpawn, motivo = motivo, invocador = invocador }
	e.quebras = 0
	e.ultimoSpawn = agora
	if Mineracao then Mineracao.registrar(hit) end
	local txt = invocador and (invocador.DisplayName .. " invocou o CHEFE para todos!") or "O CHEFE apareceu na ilha! Todos que ajudarem ganham recompensa."
	avisarIlha(areaId, txt)
	return true
end

function B.quebra(areaId)
	local e = est(areaId)
	e.quebras += 1
end

-- dano causado no chefe (limitado ao HP que ainda restava)
function B.aplicarDano(player, hit, dano)
	local areaId = hit:GetAttribute("AreaId")
	local luta = areaId and est(areaId).vivos[hit]
	if not luta then return end
	local restante = math.max(0, (hit:GetAttribute("HP") or 0) + dano) -- HP antes do golpe
	luta.dano[player] = (luta.dano[player] or 0) + math.min(dano, restante)
end

function B.morreu(hit)
	local areaId = hit:GetAttribute("AreaId")
	local area = Config.areaPorId(areaId)
	local e = areaId and est(areaId)
	local luta = e and e.vivos[hit]
	if not luta or not area then return end
	e.vivos[hit] = nil
	local duracao = os.clock() - luta.nasceu
	local participantes = 0
	for player, dano in pairs(luta.dano) do
		local perfil = player.Parent and PlayerData.get(player)
		if perfil and dano > 0 then
			participantes += 1
			local contrib = dano / luta.hpLuta
			local parte = math.min(1, contrib / CH.contribMin)
			local moedas = area.valores.super * parte * Economia.multMoedas(player, perfil)
			local ganho = Recompensas.darMoedas(player, perfil, moedas, "Gameplay", "chefe")
			local hats = 0
			if parte >= 1 then
				for _ = 1, CH.hats do
					if Recompensas.darHatAleatorio(player, perfil, area.tema, CH.hatSorte, "chefe") then hats += 1 end
				end
			end
			PlayerData.progredirMissao(perfil, areaId, "chefe", 1)
			Telemetria.evento(player, perfil, "BossContribution", math.floor(contrib * 1000) / 10,
				{ mundo = areaId, cheia = parte >= 1 and 1 or 0, ativos = luta.ativos })
			RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area",
				texto = ("Chefe derrotado! +%s moedas%s (%.1f%% do dano)"):format(Config.formatar(ganho), hats > 0 and (" + " .. hats .. " hats") or "", contrib * 100) })
			PlayerData.sincronizar(player)
		end
	end
	-- BossSpawnInterval: valida no beta a hipotese de jogadores ativos da simulacao
	local quem = next(luta.dano) or qualquerJogadorNaIlha(areaId)
	if quem and quem.Parent then
		Telemetria.evento(quem, PlayerData.get(quem), "BossSpawnInterval", math.floor(luta.desdeAnterior),
			{ mundo = areaId, ativos = luta.ativos, participantes = participantes, duracao = math.floor(duracao), motivo = luta.motivo })
	end
end

-- Invocar Chefe (developer product): nasce agora na ilha do jogador, mesmo com outro vivo (max 2)
function B.invocar(player)
	local perfil = PlayerData.get(player)
	local areaId = player:GetAttribute("CurrentAreaId") or 0
	if areaId == 0 and perfil then areaId = PlayerData.maiorArea(perfil) end
	if B.vivos(areaId) >= 2 then
		-- ja tem 2: guarda o chefe pro proximo espaco livre (a compra nunca se perde)
		local e = est(areaId)
		e.fila = (e.fila or 0) + 1
		RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area", texto = "Chefe na fila: ele aparece assim que um dos chefes atuais cair." })
		return true
	end
	return B.nascer(areaId, "invocado", player)
end

function B.iniciar(mineracao)
	Mineracao = mineracao
	for _, a in ipairs(Config.Areas) do est(a.id) end
	task.spawn(function()
		while true do
			task.wait(2)
			for _, a in ipairs(Config.Areas) do
				local e = est(a.id)
				local vivos = B.vivos(a.id)
				if vivos < 2 and (e.fila or 0) > 0 then
					e.fila -= 1
					B.nascer(a.id, "invocado")
				elseif vivos == 0 and qualquerJogadorNaIlha(a.id) then
					local dt = os.clock() - e.ultimoSpawn
					if (e.quebras >= CH.quebrasServidor and dt >= CH.intervaloMin) then
						B.nascer(a.id, "quebras")
					elseif dt >= CH.intervaloMax then
						B.nascer(a.id, "tempo_max")
					end
				end
			end
		end
	end)
	-- ActiveMinersWorld: a cada 5 min, quantos jogadores estao ativos em cada ilha
	task.spawn(function()
		while true do
			task.wait(300)
			for _, a in ipairs(Config.Areas) do
				local p = qualquerJogadorNaIlha(a.id)
				if p then
					Telemetria.evento(p, PlayerData.get(p), "ActiveMinersWorld", Economia.ativosNaArea(a.id),
						{ mundo = a.id, naIlha = Economia.jogadoresNaArea(a.id) })
				end
			end
		end
	end)
end

return B

