-- Core.Paredes : PAREDES DE CUSTO entre os mundos.
--
-- Substitui o portal de teleporte. O mundo virou continuo: o jogador anda
-- do lobby ate a Area 1, e de cada area para a proxima. Entre elas existe
-- uma parede que so abre quando o jogador DEPOSITA moeda ate o total.
--
-- Diferenca para a referencia que inspirou: la o requisito e DANO causado;
-- aqui e MOEDA GASTA, que e a moeda do jogo e ja tem toda a economia
-- calibrada (Eco.PORTAIS).
--
-- O progresso e POR JOGADOR (perfil.paredes[areaId]), nao do servidor:
-- cada um abre o seu caminho e ve a sua barra.
local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local M = {}
local V = Vector3.new
local C = Color3.fromRGB

local DEPOSITO_POR_TICK = 0.06   -- fracao do custo depositada por segundo dentro da zona
local TICK = 0.25

-- ---------------------------------------------------------------
-- formata numero grande igual a HUD do jogo (51.2M)
-- ---------------------------------------------------------------
local function fmt(n)
	n = math.floor(n)
	if n >= 1e9 then return string.format("%.1fB", n/1e9) end
	if n >= 1e6 then return string.format("%.1fM", n/1e6) end
	if n >= 1e3 then return string.format("%.1fK", n/1e3) end
	return tostring(n)
end
M.fmt = fmt

-- ---------------------------------------------------------------
-- constroi a parede de uma area
-- ---------------------------------------------------------------
-- PORTAO DE COMPRA: em vez de um paredao de energia de 200 studs, cada bloqueio
-- agora e um portao monumental sobre a passarela: torres de pedra, verga dourada,
-- emblema no tema da area e a cortina de energia so no vao. Nao da para contornar:
-- fora da passarela e vazio, e cair devolve o jogador pelo IslandTravel.
local LARGURA, ALTURA, ESPESSURA = 64, 38, 6

function M.construir(areaId, pai)
	local area = Config.Areas[areaId]
	local z = Config.PAREDE_Z[areaId]
	if not area or not z then return nil end
	local custo = area.custo or 0
	if custo <= 0 then return nil end

	local tema = Config.Temas and Config.Temas[area.tema]
	local cor = (tema and tema.cor) or C(120, 190, 255)

	local m = Instance.new("Model")
	m.Name = "Parede" .. areaId
	m:SetAttribute("AreaId", areaId)
	m:SetAttribute("Custo", custo)
	m.Parent = pai

	local function part(name, size, pos, color, mat, props)
		local p = Instance.new("Part")
		p.Name = name; p.Size = size; p.Position = pos
		p.Anchored = true; p.Color = color; p.Material = mat
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		for k, v in pairs(props or {}) do p[k] = v end
		p.Parent = m
		return p
	end

	local PEDRA, PEDRA_E, OURO = C(112, 116, 130), C(84, 88, 102), C(236, 190, 88)

	-- ---- barreira de energia (o que bloqueia de fato: cobre o vao inteiro) ----
	local barreira = part("Barreira", V(LARGURA, ALTURA, ESPESSURA), V(0, ALTURA/2 + 4, z),
		cor, Enum.Material.ForceField, {Transparency = 0.4, CanCollide = true})
	m.PrimaryPart = barreira

	-- cortina de energia visivel so no vao central do portao
	local glow = part("Brilho", V(24, 25, 1.1), V(0, 16.5, z),
		cor, Enum.Material.Neon, {Transparency = 0.55, CanCollide = false, CanQuery = false})
	TweenService:Create(glow, TweenInfo.new(1.6, Enum.EasingStyle.Sine,
		Enum.EasingDirection.InOut, -1, true), {Transparency = 0.85}):Play()

	-- ---- portao: torres, batentes e verga em arco ----
	for _, sx in ipairs({-1, 1}) do
		-- torre externa
		part("TorreBase", V(10, 6, 12), V(sx * 20, 7, z), PEDRA_E, Enum.Material.Slate)
		part("Torre", V(8, 26, 10), V(sx * 20, 20, z), PEDRA, Enum.Material.Slate)
		part("TorreCinta", V(8.6, 1.4, 10.6), V(sx * 20, 24, z), OURO, Enum.Material.Foil, {Reflectance = .22})
		part("TorreCoroa", V(9.6, 2.2, 11.6), V(sx * 20, 34, z), PEDRA_E, Enum.Material.Slate)
		-- braseiro no topo da torre
		local taca = part("Braseiro", V(4, 1.6, 4), V(sx * 20, 36, z), OURO, Enum.Material.Foil, {Reflectance = .2})
		local chama = part("Chama", V(2.2, 2.2, 2.2), V(sx * 20, 37.6, z), cor, Enum.Material.Neon,
			{Shape = Enum.PartType.Ball, CanQuery = false})
		local fogo = Instance.new("ParticleEmitter")
		fogo.Texture = "rbxasset://textures/particles/fire_main.dds"
		fogo.Color = ColorSequence.new(cor)
		fogo.Rate = 8; fogo.Lifetime = NumberRange.new(.5, .9); fogo.Speed = NumberRange.new(2, 4)
		fogo.SpreadAngle = Vector2.new(15, 15); fogo.Acceleration = V(0, 4, 0); fogo.LightEmission = .8
		fogo.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.6), NumberSequenceKeypoint.new(1, .4)})
		fogo.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, .3), NumberSequenceKeypoint.new(1, 1)})
		fogo:SetAttribute("FolhaAmbient", true); fogo.Parent = chama
		local pl = Instance.new("PointLight"); pl.Color = cor; pl.Range = 18; pl.Brightness = .9; pl.Shadows = false; pl.Parent = chama
		-- batente interno do vao
		part("Batente", V(3, 25, 5), V(sx * 13.5, 16.5, z), PEDRA, Enum.Material.Slate)
		part("BatenteFriso", V(1, 23, .8), V(sx * 12.2, 15.5, z - 2.2), cor, Enum.Material.Neon, {CanQuery = false})
		-- muro baixo ligando a torre a borda da barreira
		part("Muro", V(14, 9, 6), V(sx * 27, 10.5, z), PEDRA, Enum.Material.Slate)
		part("MuroTampa", V(15, 1.4, 7), V(sx * 27, 15.4, z), PEDRA_E, Enum.Material.Slate)
	end
	-- verga sobre o vao + coroamento
	part("Verga", V(30, 4.5, 6.5), V(0, 30.5, z), PEDRA, Enum.Material.Slate)
	part("VergaOuro", V(31, 1.6, 7), V(0, 33.4, z), OURO, Enum.Material.Foil, {Reflectance = .25})
	for _, sx in ipairs({-1, 1}) do
		local ombro = Instance.new("WedgePart")
		ombro.Anchored = true; ombro.CanCollide = false; ombro.CanQuery = false; ombro.CanTouch = false
		ombro.Size = V(6.5, 3.5, 5); ombro.Color = PEDRA; ombro.Material = Enum.Material.Slate
		ombro.CFrame = CFrame.new(sx * 12.7, 36, z) * CFrame.Angles(0, sx > 0 and math.rad(-90) or math.rad(90), 0)
		ombro.Name = "VergaOmbro"; ombro.Parent = m
	end
	-- emblema circular no tema da area, no alto do portao
	part("EmblemaAro", V(1.6, 7.5, 7.5), V(0, 38.5, z), OURO, Enum.Material.Foil,
		{Shape = Enum.PartType.Cylinder, Reflectance = .25, CFrame = CFrame.new(0, 38.5, z) * CFrame.Angles(0, math.rad(90), 0)})
	part("Emblema", V(1.8, 5.8, 5.8), V(0, 38.5, z), cor, Enum.Material.Neon,
		{Shape = Enum.PartType.Cylinder, CFrame = CFrame.new(0, 38.5, z) * CFrame.Angles(0, math.rad(90), 0), CanQuery = false})

	-- ---- praca de deposito (lado SUL, por onde o jogador chega) ----
	part("Praca", V(30, 1, 40), V(0, 5.85, z - 24), C(200, 202, 210), Enum.Material.Slate)
	part("PracaBorda", V(32, .6, 42), V(0, 5.55, z - 24), PEDRA_E, Enum.Material.Slate)
	local zona = part("Zona", V(30, 20, 38), V(0, 15, z - 24),
		cor, Enum.Material.Neon,
		{Transparency = 1, CanCollide = false, CanTouch = false, CanQuery = false})
	part("ZonaPiso", V(20, .3, 28), V(0, 6.5, z - 24),
		cor, Enum.Material.Neon, {Transparency = 0.55, CanCollide = false, CanQuery = false})
	for _, sx in ipairs({-1, 1}) do
		part("PostePraca", V(1.1, 6.5, 1.1), V(sx * 13, 9.2, z - 42), PEDRA, Enum.Material.Slate)
		local orbe = part("OrbePraca", V(1.8, 1.8, 1.8), V(sx * 13, 13.2, z - 42), cor, Enum.Material.Neon,
			{Shape = Enum.PartType.Ball, CanQuery = false})
		local ol = Instance.new("PointLight"); ol.Color = cor; ol.Range = 13; ol.Brightness = .8; ol.Shadows = false; ol.Parent = orbe
	end

	-- ---- painel de requisito (o "Requirement to Break") ----
	local anchor = part("Painel", V(1,1,1), V(0, 24, z - 2),
		cor, Enum.Material.Neon, {Transparency = 1, CanCollide = false, CanQuery = false})
	local bb = Instance.new("BillboardGui")
	bb.Name = "Requisito"
	bb.Size = UDim2.fromScale(20, 7)
	bb.AlwaysOnTop = false
	bb.MaxDistance = 420
	bb.Parent = anchor

	local titulo = Instance.new("TextLabel")
	titulo.Size = UDim2.new(1, 0, 0.30, 0)
	titulo.BackgroundTransparency = 1
	titulo.Font = Enum.Font.GothamBold
	titulo.Text = "Custo para Abrir:"
	titulo.TextScaled = true
	titulo.TextColor3 = C(255, 255, 255)
	titulo.Parent = bb
	local st = Instance.new("UIStroke"); st.Thickness = 3; st.Color = C(0,0,0); st.Parent = titulo

	local valor = Instance.new("TextLabel")
	valor.Name = "Valor"
	valor.Position = UDim2.new(0, 0, 0.30, 0)
	valor.Size = UDim2.new(1, 0, 0.40, 0)
	valor.BackgroundTransparency = 1
	valor.Font = Enum.Font.GothamBlack
	valor.Text = "0 / " .. fmt(custo)
	valor.TextScaled = true
	valor.TextColor3 = C(255, 214, 92)
	valor.Parent = bb
	local st2 = Instance.new("UIStroke"); st2.Thickness = 3.5; st2.Color = C(0,0,0); st2.Parent = valor

	-- barra de progresso
	local barraBg = Instance.new("Frame")
	barraBg.Position = UDim2.new(0.08, 0, 0.74, 0)
	barraBg.Size = UDim2.new(0.84, 0, 0.16, 0)
	barraBg.BackgroundColor3 = C(20, 22, 30)
	barraBg.BorderSizePixel = 0
	barraBg.Parent = bb
	Instance.new("UICorner").Parent = barraBg
	local barra = Instance.new("Frame")
	barra.Name = "Preenchimento"
	barra.Size = UDim2.new(0, 0, 1, 0)
	barra.BackgroundColor3 = C(255, 196, 64)
	barra.BorderSizePixel = 0
	barra.Parent = barraBg
	Instance.new("UICorner").Parent = barra

	local nome = Instance.new("TextLabel")
	nome.Position = UDim2.new(0, 0, 0.92, 0)
	nome.Size = UDim2.new(1, 0, 0.22, 0)
	nome.BackgroundTransparency = 1
	nome.Font = Enum.Font.GothamMedium
	nome.Text = area.nome
	nome.TextScaled = true
	nome.TextColor3 = cor
	nome.Parent = bb
	local st3 = Instance.new("UIStroke"); st3.Thickness = 2.5; st3.Color = C(0,0,0); st3.Parent = nome

	return m
end

-- ---------------------------------------------------------------
-- loop de deposito: quem estiver na zona paga aos poucos
-- ---------------------------------------------------------------
function M.iniciar(pasta)
	local paredes = {}
	for _, m in ipairs(pasta:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("AreaId") then
			paredes[#paredes+1] = m
		end
	end
	-- sincroniza o estado das paredes de quem entra (senao a barreira ja paga
	-- volta a bloquear visualmente a cada sessao)
	local function sincronizarJogador(pl)
		for tent = 1, 40 do
			if PlayerData.get(pl) then break end
			task.wait(.5)
		end
		local perfil = PlayerData.get(pl)
		if not perfil then return end
		for _, m in ipairs(paredes) do
			local id = m:GetAttribute("AreaId")
			local custo = m:GetAttribute("Custo") or 0
			local pago = (perfil.paredes and perfil.paredes[id]) or 0
			if perfil.areas and perfil.areas[id] then pago = custo end
			M.atualizarVisual(pl, m, pago, custo)
		end
	end
	Players.PlayerAdded:Connect(function(pl) task.spawn(sincronizarJogador, pl) end)
	for _, pl in ipairs(Players:GetPlayers()) do task.spawn(sincronizarJogador, pl) end

	task.spawn(function()
		while true do
			task.wait(TICK)
			for _, m in ipairs(paredes) do
				local areaId = m:GetAttribute("AreaId")
				local custo  = m:GetAttribute("Custo")
				local zona   = m:FindFirstChild("Zona")
				if not zona then continue end

				local reg = workspace:GetPartBoundsInBox(zona.CFrame, zona.Size)
				local vistos = {}
				for _, p in ipairs(reg) do
					local ch = p.Parent
					local pl = ch and Players:GetPlayerFromCharacter(ch)
					if pl and not vistos[pl] then
						vistos[pl] = true
						M.depositar(pl, m, areaId, custo)
					end
				end
			end
		end
	end)
end

-- deposita a fatia deste tick, respeitando o saldo do jogador
function M.depositar(pl, modelo, areaId, custo)
	local perfil = PlayerData.get(pl)
	if not perfil then return end
	perfil.paredes = perfil.paredes or {}
	local pago = perfil.paredes[areaId] or 0
	if pago >= custo then return end                 -- ja abriu
	if (perfil.moeda or 0) <= 0 then return end      -- sem saldo

	local fatia = math.max(1, math.floor(custo * DEPOSITO_POR_TICK * TICK))
	fatia = math.min(fatia, custo - pago, math.floor(perfil.moeda))
	if fatia <= 0 then return end

	perfil.moeda = perfil.moeda - fatia
	perfil.paredes[areaId] = pago + fatia

	if perfil.paredes[areaId] >= custo then
		perfil.areas = perfil.areas or {}
		perfil.areas[areaId] = true                  -- libera a area no perfil
	end
	PlayerData.sincronizar(pl)
	M.atualizarVisual(pl, modelo, perfil.paredes[areaId], custo)
end

-- ---------------------------------------------------------------
-- visual por jogador: a barreira some SO para quem pagou
-- ---------------------------------------------------------------
function M.atualizarVisual(pl, modelo, pago, custo)
	local ev = RS:FindFirstChild("ParedeAtualizar")
	if not ev then
		ev = Instance.new("RemoteEvent")
		ev.Name = "ParedeAtualizar"
		ev.Parent = RS
	end
	ev:FireClient(pl, modelo, pago, custo)
end

function M.build(pai)
	local pasta = workspace:FindFirstChild("ParedesDeCusto")
	if pasta then pasta:Destroy() end
	pasta = Instance.new("Folder")
	pasta.Name = "ParedesDeCusto"
	pasta.Parent = pai or workspace

	local feitas = {}
	for areaId = 2, 6 do
		local anterior = workspace:FindFirstChild("Areas") and workspace.Areas:FindFirstChild("Area" .. (areaId - 1))
		if anterior and anterior:GetAttribute("RotaPropria") then continue end -- a ilha anterior tem portao de compra proprio
		local m = M.construir(areaId, pasta)
		if m then feitas[#feitas+1] = areaId end
	end
	M.iniciar(pasta)
	return pasta, feitas
end

return M
