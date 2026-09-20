-- medir_lobby.lua - despeja MEDIDAS do lobby montado, em JSON, para revisao.
-- Nao altera nada. E a fonte de dados da auditoria: numeros, nao impressao.
local H = game:GetService("HttpService")
local Config = require(game:GetService("ReplicatedStorage").Config)
local lob = workspace:FindFirstChild("LOBBY_MURIM")
if not lob then return "LOBBY_MURIM nao existe" end
local sant = workspace:FindFirstChild("Santuario")

local R = {}

-- ---------- contagem e custo
do
	local mesh, part, sombras, malhas, texturas = 0, 0, 0, {}, {}
	for _, d in ipairs(lob:GetDescendants()) do
		if d:IsA("MeshPart") then
			mesh += 1
			malhas[d.MeshId] = (malhas[d.MeshId] or 0) + 1
			if d.CastShadow then sombras += 1 end
			local sa = d:FindFirstChildOfClass("SurfaceAppearance")
			if sa then texturas[sa.ColorMap] = true end
		elseif d:IsA("BasePart") then part += 1 end
	end
	local nm, nt = 0, 0
	for _ in pairs(malhas) do nm += 1 end
	for _ in pairs(texturas) do nt += 1 end
	R.custo = { meshParts = mesh, malhasDistintas = nm, partsColisao = part,
		castShadow = sombras, texturasDistintas = nt,
		streamingEnabled = workspace.StreamingEnabled }
end

-- ---------- os seis portais
R.portais = {}
for _, mod in ipairs(sant and sant:GetChildren() or {}) do
	local disco = mod:FindFirstChild("Disco")
	local id = disco and disco:GetAttribute("AreaId")
	local area = id and Config.areaPorId(id)
	if area then
		local e = { modelo = mod.Name, areaId = id, tema = area.tema, nome = area.nome,
			discoZ = math.floor(disco.Position.Z * 100) / 100, pecas = {}, sobrasAntigas = 0 }
		for _, c in ipairs(mod:GetChildren()) do
			if c.Name ~= "Disco" and c.Name ~= "VFX_PORTAL" then e.sobrasAntigas += 1 end
		end
		-- malhas do portal que caem perto deste pad
		for _, d in ipairs(lob:GetDescendants()) do
			if d:IsA("MeshPart") and d.Name:find("^POR_") and math.abs(d.Position.Z - disco.Position.Z) < 6.6 then
				local mn = d.Position - d.Size / 2
				local mx = d.Position + d.Size / 2
				table.insert(e.pecas, { nome = d.Name,
					pos = { math.floor(d.Position.X * 10) / 10, math.floor(d.Position.Y * 10) / 10, math.floor(d.Position.Z * 10) / 10 },
					tam = { math.floor(d.Size.X * 10) / 10, math.floor(d.Size.Y * 10) / 10, math.floor(d.Size.Z * 10) / 10 },
					topoY = math.floor(mx.Y * 10) / 10, baseY = math.floor(mn.Y * 10) / 10,
					rotY = math.floor(math.deg(select(2, d.CFrame:ToEulerAnglesYXZ())) * 10) / 10 })
			end
		end
		-- VFX
		local f = mod:FindFirstChild("VFX_PORTAL")
		if f then
			local emis, luz = 0, nil
			for _, d in ipairs(f:GetDescendants()) do
				if d:IsA("ParticleEmitter") then emis += 1 end
				if d:IsA("PointLight") then luz = d end
			end
			local esperada = Config.Temas[area.tema] and Config.Temas[area.tema].cor
			e.vfx = { emissores = emis, temLuz = luz ~= nil,
				luzBate = luz and esperada and (luz.Color == esperada) or false,
				partes = #f:GetChildren() }
		end
		table.insert(R.portais, e)
	end
end

-- ---------- agua
do
	local T = workspace.Terrain
	local mn, mx
	for _, d in ipairs(lob:GetDescendants()) do
		if d:IsA("BasePart") and (d.Name == "LAGO_agua" or d.Name == "LAGO_margem") then
			local a, b = d.Position - d.Size / 2, d.Position + d.Size / 2
			mn = mn and Vector3.new(math.min(mn.X, a.X), math.min(mn.Y, a.Y), math.min(mn.Z, a.Z)) or a
			mx = mx and Vector3.new(math.max(mx.X, b.X), math.max(mx.Y, b.Y), math.max(mx.Z, b.Z)) or b
		end
	end
	R.agua = { cor = tostring(T.WaterColor), transparencia = T.WaterTransparency,
		onda = T.WaterWaveSize, velocidade = T.WaterWaveSpeed, reflexo = T.WaterReflectance,
		celulas = T:CountCells(),
		lagoCaixa = mn and { math.floor(mn.X), math.floor(mn.Y), math.floor(mn.Z), math.floor(mx.X), math.floor(mx.Y), math.floor(mx.Z) } or nil }
end

-- ---------- circulacao: chao e degraus por raio
do
	local rp = RaycastParams.new()
	rp.FilterType = Enum.RaycastFilterType.Include
	rp.FilterDescendantsInstances = { lob }
	local pontos = {
		spawn = Vector3.new(0, 30, -38), patio = Vector3.new(0, 30, 0),
		peEscadaria = Vector3.new(0, 30, -88), terracoForja = Vector3.new(0, 45, -120),
		viaImperial = Vector3.new(0, 30, 100), portao = Vector3.new(0, 30, 150),
		santuario = Vector3.new(124, 45, 0), loja = Vector3.new(-115, 45, -4),
		jardimW = Vector3.new(90, 45, 40), jardimE = Vector3.new(-90, 45, 40),
	}
	R.chao = {}
	for nome, p in pairs(pontos) do
		local r = workspace:Raycast(p, Vector3.new(0, -90, 0), rp)
		R.chao[nome] = r and math.floor(r.Position.Y * 10) / 10 or false
	end
	-- perfil da escadaria da Forja: maior degrau
	local maior, ant = 0, nil
	for z = -60, -95, -1 do
		local r = workspace:Raycast(Vector3.new(0, 40, z), Vector3.new(0, -60, 0), rp)
		local y = r and r.Position.Y or nil
		if y and ant then maior = math.max(maior, math.abs(y - ant)) end
		ant = y
	end
	R.maiorDegrauEscadaria = math.floor(maior * 100) / 100
	-- perfil do terraco do Santuario, onde ficam os portais
	local maior2, ant2 = 0, nil
	for x = 100, 140, 1 do
		local r = workspace:Raycast(Vector3.new(x, 45, 0), Vector3.new(0, -60, 0), rp)
		local y = r and r.Position.Y or nil
		if y and ant2 then maior2 = math.max(maior2, math.abs(y - ant2)) end
		ant2 = y
	end
	R.maiorDegrauSantuario = math.floor(maior2 * 100) / 100
end

-- ---------- sistemas do jogo
do
	local ignis = workspace.NPCs:FindFirstChild("Ignis")
	local pr
	for _, d in ipairs(ignis and ignis:GetDescendants() or {}) do
		if d:IsA("ProximityPrompt") then pr = d end
	end
	local padsOk = 0
	for _, m in ipairs(sant and sant:GetChildren() or {}) do
		local d = m:FindFirstChild("Disco")
		if d and d:GetAttribute("AreaId") and d.CanTouch then padsOk += 1 end
	end
	R.sistemas = { ignis = ignis ~= nil, ignisPrompt = pr ~= nil,
		promptAlcance = pr and pr.MaxActivationDistance or 0,
		padsComAreaId = padsOk,
		loja = workspace:FindFirstChild("LojaMochilas") ~= nil,
		mailbox = workspace:FindFirstChild("MailBox") ~= nil,
		ambienteScript = game:GetService("ServerScriptService"):FindFirstChild("PortaisAmbiente") ~= nil }
end

return H:JSONEncode(R)
