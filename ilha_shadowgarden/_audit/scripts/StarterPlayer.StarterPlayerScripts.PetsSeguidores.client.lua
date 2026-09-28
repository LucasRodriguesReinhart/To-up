-- Pets que seguem o jogador pelo mundo.
-- O servidor so publica o atributo "PetsEquipados" (ids separados por virgula) em cada Player.
-- Cada cliente desenha localmente os pets de todo mundo: movimento liso e sem custo de rede.
-- Modelos vem de ReplicatedStorage.PreviewModelos.Pets (os mesmos da interface).
--  * pet com Humanoid (rig, ex: goku) anda no chao com animacao de andar/parado
--  * pet sem Humanoid (mesh) flutua atras do jogador

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local HttpService = game:GetService("HttpService")
local Config = require(RS:WaitForChild("Config"))

local PastaModelos = RS:WaitForChild("PreviewModelos"):WaitForChild("Pets")

local ESCALA_RIG = 1          -- tamanho normal de avatar
local TAMANHO_MESH = 2.5      -- maior lado dos pets de mesh, em studs
local DIST_ATRAS = 6          -- quanto atras do jogador fica a fileira
local ESPACO = 4.5            -- espaco entre pets lado a lado
local POR_FILEIRA = 3
local SUAVIDADE = 8           -- maior = alcanca o alvo mais rapido
local DIST_TELEPORTE = 60
local ALTURA_VOO = 1.5

local ANIM_ANDAR = "rbxassetid://507777826"  -- R15 walk padrao do Roblox
local ANIM_PARADO = "rbxassetid://507766388" -- R15 idle padrao do Roblox

local pastaMundo = Instance.new("Folder")
pastaMundo.Name = "PetsVisuais"
pastaMundo.Parent = workspace

local raioParams = RaycastParams.new()
raioParams.FilterType = Enum.RaycastFilterType.Exclude
raioParams.IgnoreWater = false
-- so chao de verdade: hitbox de minerio, zona invisivel e barreira sem colisao nao contam
raioParams.RespectCanCollide = true

local porJogador = {} -- [Player] = { pets = { {modelo, ...} }, ids = "..." }

local function atualizarFiltroRaio()
	local ignorar = { pastaMundo }
	for _, p in ipairs(Players:GetPlayers()) do
		if p.Character then table.insert(ignorar, p.Character) end
	end
	raioParams.FilterDescendantsInstances = ignorar
end

local function prepararPartes(modelo, ancorarTudo)
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("LuaSourceContainer") then
			d:Destroy()
		elseif d:IsA("BasePart") then
			d.CanCollide = false
			-- o Humanoid religa CanCollide do tronco; o grupo garante que o pet nunca bloqueie ninguem
			d.CollisionGroup = "PetsVisuais"
			d.CanTouch = false
			d.CanQuery = false
			d.Massless = true
			d.Anchored = ancorarTudo or d.Name == "HumanoidRootPart"
		end
	end
end

-- PetsApelidos = lista de nomes na mesma ordem de PetsEquipados (cada pet tem o proprio nome)
local function apelidoDe(player, id, indice)
	local ok, t = pcall(HttpService.JSONDecode, HttpService, player:GetAttribute("PetsApelidos") or "[]")
	local nick = ok and type(t) == "table" and t[indice]
	if type(nick) == "string" and nick ~= "" then return nick end
	local def = Config.petPorId(id)
	return def and def.nome or id
end

-- placa do pet (UI V2): nome com contorno + raridade na cor do Design System
local UITokens=require(RS.ExpeditionUI.Theme)
local FONTE_PET=UITokens.F.label
local TINTA_PET=UITokens.P.ink
local CORES_RARIDADE,NOMES_RARIDADE={},{}
for key,r in pairs(UITokens.Rarity) do CORES_RARIDADE[key]=r.cor;NOMES_RARIDADE[key]=r.nome end

local function criarNome(pet, texto)
	local cabeca = pet.modelo:FindFirstChild("Head") or pet.modelo.PrimaryPart
	if not cabeca then return end
	local def = Config.petPorId(pet.id)
	local cor = def and CORES_RARIDADE[def.raridade] or Color3.new(1, 1, 1)
	local bb = Instance.new("BillboardGui")
	bb.Name = "NomePet"
	-- tamanho em pixels proporcional à altura da tela: no celular o nome não cobre metade da visão
	local k = math.clamp(workspace.CurrentCamera.ViewportSize.Y / 820, .55, 1.15)
	bb.Size = UDim2.fromOffset(math.floor(210 * k), math.floor(48 * k))
	bb.StudsOffsetWorldSpace = Vector3.new(0, 2.7, 0)
	bb.MaxDistance = 70
	bb.LightInfluence = 0
	bb.AlwaysOnTop = false
	local t = Instance.new("TextLabel")
	t.Name = "Nome"
	t.Size = UDim2.fromScale(1, .625)
	t.BackgroundTransparency = 1
	t.FontFace = FONTE_PET
	t.TextScaled = true
	t.TextColor3 = Color3.new(1, 1, 1)
	t.Text = texto
	t.Parent = bb
	local st = Instance.new("UIStroke")
	st.Color = TINTA_PET; st.Thickness = 1.4 * k; st.LineJoinMode = Enum.LineJoinMode.Round; st.Parent = t
	local r = Instance.new("TextLabel")
	r.Name = "Raridade"
	r.Position = UDim2.fromScale(0, .625)
	r.Size = UDim2.fromScale(1, .335)
	r.BackgroundTransparency = 1
	r.FontFace = FONTE_PET
	r.TextScaled = true
	r.TextColor3 = cor
	r.Text = def and (NOMES_RARIDADE[def.raridade] or "") or ""
	r.Parent = bb
	local st2 = Instance.new("UIStroke")
	st2.Color = TINTA_PET; st2.Thickness = 1.25 * k; st2.LineJoinMode = Enum.LineJoinMode.Round; st2.Parent = r
	bb.Adornee = cabeca
	bb.Parent = pet.modelo
	pet.nome = t
end

local function criarPet(id)
	local base = PastaModelos:FindFirstChild(id)
	if not base then return nil end
	local modelo = base:Clone()
	local hum = modelo:FindFirstChildOfClass("Humanoid")
	local pet = { modelo = modelo, hum = hum, id = id }

	if hum then
		prepararPartes(modelo, false)
		hum.EvaluateStateMachine = false
		hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
		modelo:ScaleTo(ESCALA_RIG)
		modelo.Parent = pastaMundo
		local animator = hum:FindFirstChildOfClass("Animator") or Instance.new("Animator", hum)
		local a1 = Instance.new("Animation"); a1.AnimationId = ANIM_ANDAR
		local a2 = Instance.new("Animation"); a2.AnimationId = ANIM_PARADO
		pet.andar = animator:LoadAnimation(a1)
		pet.parado = animator:LoadAnimation(a2)
		pet.andar.Looped = true
		pet.parado.Looped = true
		pet.parado:Play()
	else
		prepararPartes(modelo, true)
		local _, sz = modelo:GetBoundingBox()
		local maior = math.max(sz.X, sz.Y, sz.Z)
		if maior > 0 then modelo:ScaleTo(modelo:GetScale() * TAMANHO_MESH / maior) end
		modelo.Parent = pastaMundo
	end

	-- distancia do pivot ate a sola do pe. usar a caixa do modelo inteiro fazia pet com capa,
	-- espada ou roupa em camadas (ainda sem deformar) boiar no ar.
	local pivo = modelo:GetPivot()
	local pes = {}
	for _, n in ipairs({ "LeftFoot", "RightFoot", "Left Leg", "Right Leg" }) do
		local p = modelo:FindFirstChild(n)
		if p then table.insert(pes, p.Position.Y - p.Size.Y / 2) end
	end
	if #pes > 0 then
		pet.alturaBase = pivo.Position.Y - math.min(table.unpack(pes))
	else
		local cf, sz = modelo:GetBoundingBox()
		pet.alturaBase = pivo.Position.Y - (cf.Position.Y - sz.Y / 2)
	end
	pet.fase = math.random() * math.pi * 2
	return pet
end

local function destruirPets(estado)
	for _, pet in ipairs(estado.pets) do
		pet.modelo:Destroy()
	end
	estado.pets = {}
end

local function reconstruir(player)
	local estado = porJogador[player]
	if not estado then return end
	local ids = player:GetAttribute("PetsEquipados") or ""
	if ids == estado.ids and #estado.pets > 0 then return end
	estado.ids = ids
	destruirPets(estado)
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	local indice = 0
	for id in string.gmatch(ids, "[^,]+") do
		indice += 1
		local pet = criarPet(id)
		if pet then
			pet.indice = indice
			criarNome(pet, apelidoDe(player, id, indice))
			table.insert(estado.pets, pet)
			if hrp then
				pet.modelo:PivotTo(hrp.CFrame * CFrame.new(0, 0, DIST_ATRAS))
			end
		end
	end
end

local function registrar(player)
	local estado = { pets = {}, ids = nil, conexoes = {} }
	porJogador[player] = estado
	table.insert(estado.conexoes, player:GetAttributeChangedSignal("PetsEquipados"):Connect(function()
		reconstruir(player)
	end))
	table.insert(estado.conexoes, player:GetAttributeChangedSignal("PetsApelidos"):Connect(function()
		for _, pet in ipairs(estado.pets) do
			if pet.nome then pet.nome.Text = apelidoDe(player, pet.id, pet.indice) end
		end
	end))
	table.insert(estado.conexoes, player.CharacterAdded:Connect(function()
		atualizarFiltroRaio()
		estado.ids = nil
		task.defer(reconstruir, player)
	end))
	atualizarFiltroRaio()
	reconstruir(player)
end

local function remover(player)
	local estado = porJogador[player]
	if not estado then return end
	for _, c in ipairs(estado.conexoes) do c:Disconnect() end
	destruirPets(estado)
	porJogador[player] = nil
	atualizarFiltroRaio()
end

local function chaoEm(pos)
	local r = workspace:Raycast(pos + Vector3.new(0, 6, 0), Vector3.new(0, -30, 0), raioParams)
	return r and r.Position.Y
end

local function atualizarPet(pet, hrp, hum, i, total, dt, agora)
	local fileira = math.floor((i - 1) / POR_FILEIRA)
	local naFileira = math.min(POR_FILEIRA, total - fileira * POR_FILEIRA)
	local coluna = (i - 1) % POR_FILEIRA
	local x = (coluna - (naFileira - 1) / 2) * ESPACO
	local z = DIST_ATRAS + fileira * ESPACO

	local olhar = hrp.CFrame.LookVector * Vector3.new(1, 0, 1)
	if olhar.Magnitude < 0.01 then olhar = Vector3.new(0, 0, -1) end
	local base = CFrame.lookAt(hrp.Position, hrp.Position + olhar.Unit)
	local alvo = (base * CFrame.new(x, 0, z)).Position

	local atual = pet.modelo:GetPivot()
	local posAtual = atual.Position
	if (posAtual - alvo).Magnitude > DIST_TELEPORTE then
		posAtual = alvo
	end

	local k = 1 - math.exp(-SUAVIDADE * dt)
	local novoXZ = Vector3.new(posAtual.X, 0, posAtual.Z):Lerp(Vector3.new(alvo.X, 0, alvo.Z), k)

	-- altura: chao embaixo do pet; se nao achar chao, acompanha a altura do pe do jogador
	local peJogador = hrp.Position.Y - hrp.Size.Y / 2 - (hum and hum.HipHeight or 2)
	local chao = chaoEm(Vector3.new(novoXZ.X, hrp.Position.Y, novoXZ.Z)) or peJogador
	local y = chao + pet.alturaBase
	if not pet.hum then
		y += ALTURA_VOO + math.sin(agora * 3 + pet.fase) * 0.35
	end
	local novaPos = Vector3.new(novoXZ.X, y, novoXZ.Z)

	local deslocXZ = Vector3.new(novaPos.X - posAtual.X, 0, novaPos.Z - posAtual.Z)
	local velocidade = dt > 0 and deslocXZ.Magnitude / dt or 0

	local direcao = velocidade > 1 and deslocXZ.Unit or olhar.Unit
	local atualDir = atual.LookVector * Vector3.new(1, 0, 1)
	if atualDir.Magnitude < 0.01 then atualDir = direcao end
	local dirSuave = atualDir.Unit:Lerp(direcao, math.min(1, dt * 10))
	if dirSuave.Magnitude < 0.01 then dirSuave = direcao end

	pet.modelo:PivotTo(CFrame.lookAt(novaPos, novaPos + dirSuave.Unit))

	if pet.hum then
		local andando = velocidade > 1.5
		if andando and not pet.andar.IsPlaying then
			pet.parado:Stop(0.2)
			pet.andar:Play(0.2)
		elseif not andando and pet.andar.IsPlaying then
			pet.andar:Stop(0.2)
			pet.parado:Play(0.2)
		end
		if andando then
			-- a animacao padrao foi feita pra ~16 studs/s num avatar tamanho 1
			pet.andar:AdjustSpeed(math.clamp(velocidade / (16 * ESCALA_RIG), 0.5, 3))
		end
	end
end

Run.RenderStepped:Connect(function(dt)
	local agora = os.clock()
	for player, estado in pairs(porJogador) do
		local char = player.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart")
		if hrp then
			local hum = char:FindFirstChildOfClass("Humanoid")
			local total = #estado.pets
			for i, pet in ipairs(estado.pets) do
				if pet.modelo.Parent then
					atualizarPet(pet, hrp, hum, i, total, dt, agora)
				end
			end
		end
	end
end)

for _, p in ipairs(Players:GetPlayers()) do registrar(p) end
Players.PlayerAdded:Connect(registrar)
Players.PlayerRemoving:Connect(remover)
