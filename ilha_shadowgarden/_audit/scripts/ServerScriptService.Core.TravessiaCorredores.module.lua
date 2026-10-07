-- TravessiaCorredores: abre a passagem fisica lobby -> Area1 -> ... -> Area6.
-- A corrente corre para o NORTE (+Z) e cada ilha ja tem a ENTRADA no seu lado
-- sul (-Z local): torii, ponte e Portao Principal encaram o corredor de chegada.
-- Este script so faz o minimo depois do AreaBuilder:
--   * paredes invisiveis de limite: viram 2 segmentos laterais (vao central)
--   * pedras centrais na faixa da estrada: DESLIZAM para o lado (nada e apagado)
--   * portao de Konoha: folhas deslizam abertas (porta de correr)
--   * saida norte de Konoha: arco sob o Monte Hokage (rostos intactos)
-- Nenhuma ilha e reformulada alem do necessario para andar o percurso.
local GAP = 16          -- meia-largura do vao central
local ALT_TUNEL = 24    -- altura livre nos arcos/tuneis

local function esperarAreas()
	local areas = workspace:WaitForChild("Areas", 60)
	if not areas then return nil end
	for tent = 1, 120 do
		if areas:FindFirstChild("Area6") and areas:FindFirstChild("Area1") then break end
		task.wait(.5)
	end
	task.wait(2) -- deixa os builders customizados terminarem
	return areas
end

local function dentroDaFaixa(p, z0, z1)
	local pos = p.Position
	return math.abs(pos.X) < 30 and pos.Z > math.min(z0, z1) and pos.Z < math.max(z0, z1)
end

-- divide uma parede larga em 2 segmentos laterais, deixando vao |x| < GAP
local function fenderParede(p)
	local sz, pos = p.Size, p.Position
	local bordaEsq = pos.X - sz.X / 2
	local bordaDir = pos.X + sz.X / 2
	if bordaEsq > -GAP or bordaDir < GAP then
		p:Destroy()
		return
	end
	local esq = p:Clone()
	esq.Size = Vector3.new(-GAP - bordaEsq, sz.Y, sz.Z)
	esq.Position = Vector3.new((bordaEsq + -GAP) / 2, pos.Y, pos.Z)
	esq.Parent = p.Parent
	local dir = p:Clone()
	dir.Size = Vector3.new(bordaDir - GAP, sz.Y, sz.Z)
	dir.Position = Vector3.new((GAP + bordaDir) / 2, pos.Y, pos.Z)
	dir.Parent = p.Parent
	p:Destroy()
end

-- desliza uma pedra/falesia para fora da faixa central (preserva a peca)
local function deslizarPedra(p)
	local lado = p.Position.X >= 0 and 1 or -1
	local alvoX = lado * (GAP + p.Size.X / 2 + 2)
	p.CFrame = p.CFrame + Vector3.new(alvoX - p.Position.X, 0, 0)
end

-- transforma um bloco de falesia em arco: mantem so a parte de cima
local function virarArco(p, chao)
	local sz, pos = p.Size, p.Position
	local topo = pos.Y + sz.Y / 2
	local novoFundo = chao + ALT_TUNEL
	if topo - novoFundo < 6 then
		p:Destroy()
		return
	end
	p.Size = Vector3.new(sz.X, topo - novoFundo, sz.Z)
	p.Position = Vector3.new(pos.X, (novoFundo + topo) / 2, pos.Z)
end

local function abrirFaixa(areaModel, z0, z1)
	for _, p in ipairs(areaModel:GetDescendants()) do
		if p:IsA("BasePart") and p.CanCollide and dentroDaFaixa(p, z0, z1) and not p:GetAttribute("TravessiaKeep") then
			local pai = p.Parent and p.Parent.Name or ""
			if p.Transparency >= .99 then
				if p.Size.X > 60 then fenderParede(p) else p:Destroy() end
			elseif (pai:find("Fal") and (pai:find("sia") or pai:find("esia"))) or pai:find("Rochedo")
				or p.Name == "Maciço" or p.Name:find("Rochedo") then
				if math.abs(p.Position.X) < GAP + 4 then deslizarPedra(p) end
			end
		end
	end
end

task.spawn(function()
	local areas = esperarAreas()
	if not areas then return end
	local Config = require(game.ReplicatedStorage.Config)
	for id = 1, 6 do
		local m = areas:FindFirstChild("Area" .. id)
		if m and not m:GetAttribute("RotaPropria") then -- ilha com entrada/saida proprias (Ilha Naruto): nada a abrir
			local zc = Config.Areas[id].centro.Z
			-- frente da ilha (lado sul, onde chega o corredor); as cercas de borda
			-- invisiveis chegam a rel 112, por isso a faixa comeca ali
			abrirFaixa(m, zc - 220, zc - 112)
			-- saida norte para a proxima ilha (nao existe na ultima)
			if id < 6 then
				abrirFaixa(m, zc + 112, zc + 220)
			end
		end
	end
	-- ---- casos especiais de Konoha ----
	local a1 = areas:FindFirstChild("Area1")
	if a1 then
		local zc = Config.Areas[1].centro.Z
		-- portao principal (frente): folhas deslizam abertas
		for _, p in ipairs(a1:GetDescendants()) do
			if p:IsA("BasePart") and p.Name == "FolhaPortao" then
				local lado = p.Position.X >= 0 and 1 or -1
				p.CFrame = p.CFrame + Vector3.new(lado * p.Size.X, 0, 0)
			end
		end
		-- saida norte: arco sob o Monte Hokage (mantem o monumento e os rostos)
		for _, p in ipairs(a1:GetDescendants()) do
			if p:IsA("BasePart") and p.Name == "Macico" and math.abs(p.Position.X) < GAP and p.Position.Z > zc + 118 and p.Position.Z < zc + 200 then
				virarArco(p, 6)
			end
		end
	end
	print("[TravessiaCorredores] passagens abertas entre lobby e areas")
	-- PASSARELAS DE TRAVESSIA: as ilhas terminam em falesia e a estrada fica
	-- 6 studs abaixo; uma passarela continua no nivel do piso das ilhas liga
	-- cada saida norte a entrada da ilha seguinte (largura 18: passa no arco
	-- do Monte Hokage).
	local velhaPasta = workspace:FindFirstChild("TravessiaPontes")
	if velhaPasta then velhaPasta:Destroy() end
	local pontes = Instance.new("Folder")
	pontes.Name = "TravessiaPontes"
	pontes.Parent = workspace
	local function parteP(nome, tam, pos, cor, mat)
		local p = Instance.new("Part")
		p.Name = nome
		p.Size = tam
		p.Position = pos
		p.Color = cor
		p.Material = mat
		p.Anchored = true
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		p.Parent = pontes
		return p
	end
	local C3 = Color3.fromRGB
	for k = 1, 5 do
		local ak = areas:FindFirstChild("Area" .. k)
		if ak and ak:GetAttribute("RotaPropria") then continue end -- saida pelo portao de compra da propria ilha
		local zc = Config.Areas[k].centro.Z
		local z0, z1 = zc + 112, zc + 308
		local cz = (z0 + z1) / 2
		local L = z1 - z0
		parteP("Passarela" .. k, Vector3.new(18, 3, L), Vector3.new(0, 4.5, cz), C3(214, 208, 196), Enum.Material.SmoothPlastic)
		parteP("PassarelaOuro" .. k, Vector3.new(4, .3, L), Vector3.new(0, 6.1, cz), C3(236, 190, 88), Enum.Material.Foil)
		for _, s in ipairs({-1, 1}) do
			parteP("PassarelaGuia" .. k, Vector3.new(1.6, 1.4, L), Vector3.new(s * 9.8, 5.9, cz), C3(226, 222, 212), Enum.Material.SmoothPlastic)
		end
	end
	-- PAREDES DE CUSTO: o modulo existia mas nada o chamava; e aqui que o
	-- mundo continuo ganha os bloqueios de progressao de verdade.
	local Paredes = require(script.Parent.Paredes)
	local pasta, feitas = Paredes.build(workspace)
	print("[TravessiaCorredores] paredes de custo ativas: " .. #feitas)
end)
return true
