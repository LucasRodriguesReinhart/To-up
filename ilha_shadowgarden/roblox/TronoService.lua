-- TronoService (ModuleScript, ServerScriptService.Core) - PASSAGEM SECRETA DO TRONO da Ilha 3 (Shadow Garden).
-- Pedido do usuario: "o player toca no trono, o trono se esconde e abre uma passagem subterranea em escada caracol que
-- leva para baixo do castelo, ao salao sombrio onde fica a entrada da masmorra". Ligado pelo SistemasShadowGarden.
--
-- Contrato com o export (marcadores em GAMEPLAY_MARKERS, ver renders/plano_mestre/PLANO.md 3.2/3.4):
--   THRONE_Rest / THRONE_Park   pivo do trono em repouso / recolhido no bolso da parede (a translacao e Park - Rest)
--   THRONE_Interact             prompt "Tocar o trono" (na frente do soco)
--   THRONE_Stair_Top            patamar de cima da escada, DENTRO do arco: prompt "Abrir passagem" para quem sobe
--   THRONE_OpenZone             caixa (atributos sx, sy, sz) onde o trono NAO fecha se houver jogador
--   THRONE_Return, CAVE_Stair_Up  atalho opcional "Subir ao salao" (do salao sombrio de volta para o trono)
-- Pecas moveis: toda BasePart cujo nome comeca com SG_Hall_ThroneMov ou COL_SGHallThroneMov (visual + colisao).
-- Estado no SERVIDOR (igual para todos): atributo TronoAberto no modelo da area. Tween de 3 s (Quad InOut) por CFrame,
-- colisao desligada durante o movimento. Fecha 20 s depois da ultima abertura, so com a OpenZone vazia (checa a cada
-- 1 s); se alguem entra durante o fechamento, o tween inverte. Aberto sempre em COUNTDOWN/ENTRY_OPEN da masmorra.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Config = require(RS.Config)

local T = {}
local TEMPO_MOV = 3
local FECHA_APOS = 20
local area, areaModel, marcas
local pecas = {}          -- { {part, cfRepouso} }
local desloc               -- Vector3 de Rest -> Park
local aberto, movendo, ultimaAbertura = false, false, 0
local tweens = {}
local som

local function marcador(nome) return marcas and marcas:FindFirstChild(nome) end
local function frente(m)
	local fx, fz = m:GetAttribute("fwd_x"), m:GetAttribute("fwd_z")
	if fx and fz and (fx ~= 0 or fz ~= 0) then return Vector3.new(fx, 0, fz).Unit end
	return Vector3.new(0, 0, -1)
end

local function zonaOcupada()
	local z = marcador("THRONE_OpenZone")
	if not z then return false end
	local sx, sy, sz = z:GetAttribute("sx") or 18, z:GetAttribute("sy") or 32, z:GetAttribute("sz") or 14
	local cf = CFrame.lookAt(z.Position, z.Position + frente(z))
	for _, p in ipairs(Players:GetPlayers()) do
		local hrp = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
		if hrp then
			local l = cf:PointToObjectSpace(hrp.Position)
			if math.abs(l.X) <= sx / 2 and math.abs(l.Z) <= sy / 2 and l.Y > -4 and l.Y < sz then return true end
		end
	end
	return false
end

local function mover(abrir)
	for _, tw in ipairs(tweens) do tw:Cancel() end
	tweens = {}
	movendo = true
	aberto = abrir
	areaModel:SetAttribute("TronoAberto", abrir)
	if som then som.TimePosition = 6; som:Play(); task.delay(TEMPO_MOV + 0.3, function() som:Stop() end) end
	local info = TweenInfo.new(TEMPO_MOV, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut)
	local ultimo
	for _, pc in ipairs(pecas) do
		local alvo = abrir and (pc.cf + desloc) or pc.cf
		pc.part.CanCollide = false
		local tw = TweenService:Create(pc.part, info, { CFrame = alvo })
		table.insert(tweens, tw)
		tw:Play()
		ultimo = tw
	end
	if ultimo then
		ultimo.Completed:Connect(function(estado)
			if estado ~= Enum.PlaybackState.Completed then return end
			movendo = false
			for _, pc in ipairs(pecas) do pc.part.CanCollide = pc.colide end
		end)
	else
		movendo = false
	end
end

function T.abrir()
	ultimaAbertura = os.clock()
	if not aberto then mover(true) end
end

local function masmorraChamando()
	local st = RS:FindFirstChild("MasmorraEstado")
	local e = st and st:GetAttribute("Estado")
	return e == "COUNTDOWN" or e == "ENTRY_OPEN"
end

local function prompt(nome, acao, objeto, dist, fn)
	local m = marcador(nome)
	if not m then return end
	local a = Instance.new("Part")
	a.Name = "Trono_" .. nome; a.Size = Vector3.new(2, 2, 2); a.Anchored = true; a.CanCollide = false
	a.CanQuery = false; a.CanTouch = false; a.Transparency = 1
	a.CFrame = CFrame.new(m.Position + Vector3.new(0, 3, 0)); a.Parent = areaModel
	local pp = Instance.new("ProximityPrompt")
	pp.ActionText = acao; pp.ObjectText = objeto; pp.HoldDuration = 0.5; pp.MaxActivationDistance = dist
	pp.RequiresLineOfSight = false; pp.Parent = a
	pp.Triggered:Connect(fn)
	return pp
end

local function montar()
	for _, a in ipairs(Config.Areas) do if a.tema == "sombra" then area = a end end
	if not area then warn("[TronoService] area de tema sombra nao encontrada no Config") return false end
	-- a Area3 nasce antes do clone da ilha (e o AreaBuilder pode demorar): espera os marcadores sem prazo
	-- o AreaBuilder RECRIA a Area3: busca o modelo de novo a cada volta (a referencia antiga fica orfa)
	repeat
		local areas = workspace:FindFirstChild("Areas")     -- a pasta Areas tambem pode ser recriada
		areaModel = areas and areas:FindFirstChild("Area" .. area.id)
		marcas = areaModel and areaModel:FindFirstChild("GAMEPLAY_MARKERS", true)
		if marcas and marcas:FindFirstChild("THRONE_Rest") then break end
		task.wait(1)
	until false
	local rest, park = marcador("THRONE_Rest"), marcador("THRONE_Park")
	if not (rest and park) then
		warn("[TronoService] THRONE_Rest/THRONE_Park ausentes (export sem a passagem do trono)")
		return false
	end
	desloc = park.Position - rest.Position
	for _, d in ipairs(areaModel:GetDescendants()) do
		if d:IsA("BasePart") and (string.match(d.Name, "^SG_Hall_ThroneMov") or string.match(d.Name, "^COL_SGHallThroneMov")) then
			d.Anchored = true
			table.insert(pecas, { part = d, cf = d.CFrame, colide = d.CanCollide })
		end
	end
	if #pecas == 0 then warn("[TronoService] nenhuma peca SG_Hall_ThroneMov* / COL_SGHallThroneMov* encontrada") end
	som = Instance.new("Sound")
	som.Name = "TronoPedra"; som.SoundId = "rbxassetid://9118657384"   -- "Rock Movement 3" (ProSoundEffects, biblioteca licenciada Roblox)
	som.Volume = 0.6; som.RollOffMaxDistance = 80; som.RollOffMinDistance = 10
	som.Parent = pecas[1] and pecas[1].part or areaModel
	areaModel:SetAttribute("TronoAberto", false)

	prompt("THRONE_Interact", "Tocar o trono", "Trono das Sombras", 10, function() T.abrir() end)
	prompt("THRONE_Stair_Top", "Abrir passagem", "Trono das Sombras", 10, function() T.abrir() end)
	prompt("CAVE_Stair_Up", "Subir ao salao", "Escada do Trono", 10, function(p)
		local ret = marcador("THRONE_Return")
		local char = p.Character
		if ret and char and char:FindFirstChild("HumanoidRootPart") then
			T.abrir()
			local alvo = ret.Position + Vector3.new(0, 3.5, 0)
			char:PivotTo(CFrame.lookAt(alvo, alvo + frente(ret)))
		end
	end)

	task.spawn(function()
		while true do
			task.wait(1)
			local ok, err = pcall(function()
				if masmorraChamando() then
					ultimaAbertura = os.clock()
					if not aberto then mover(true) end
				elseif aberto and not movendo and os.clock() - ultimaAbertura > FECHA_APOS and not zonaOcupada() then
					mover(false)
				elseif not aberto and movendo and zonaOcupada() then
					mover(true)                      -- alguem entrou no caminho durante o fechamento: inverte
				end
			end)
			if not ok then warn("[TronoService] " .. tostring(err)) end
		end
	end)
	return true
end

-- iniciar devolve na hora (o SistemasShadowGarden nao espera); a montagem roda em segundo plano ate achar o trono
function T.iniciar()
	task.spawn(function()
		local ok, res = pcall(montar)
		if not ok then warn("[TronoService] " .. tostring(res))
		elseif res then print("[TronoService] passagem do trono pronta (" .. #pecas .. " pecas moveis)") end
	end)
	return true
end

return T
