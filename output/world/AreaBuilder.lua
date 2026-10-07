local RS = game:GetService("ReplicatedStorage")
local SS = game:GetService("ServerStorage")
local Config = require(RS.Config)
local FolhaEnvironment = require(script.Parent.FolhaEnvironment)

local AreaBuilder = {}
local rnd = Random.new(1337)
local MODELOS = SS:WaitForChild("Modelos")

local ESCALA_ROCHA = 3.2
local ESCALA_CHEFE = 8.5

local function novaPart(props, parent)
	local p = Instance.new("Part")
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	for k, v in pairs(props) do p[k] = v end
	p.Parent = parent
	return p
end

local function bbox(mo)
	local mn = Vector3.new(math.huge, math.huge, math.huge); local mx = -mn
	for _, d in ipairs(mo:GetDescendants()) do
		if d:IsA("BasePart") then
			mn = mn:Min(d.Position - d.Size/2); mx = mx:Max(d.Position + d.Size/2)
		end
	end
	return (mn + mx) / 2, mx - mn
end

local function etiqueta(hit, texto, corTexto, hp, alturaOffset, ehChefe, recompensa)
	local bb = Instance.new("BillboardGui")
	bb.Name = "Vida"
	bb.Size = UDim2.fromOffset(ehChefe and 190 or 120, ehChefe and 56 or 42)
	bb.StudsOffset = Vector3.new(0, alturaOffset, 0)
	bb.AlwaysOnTop = false
	bb.MaxDistance = ehChefe and 75 or 65
	bb.Enabled = ehChefe
	bb.Parent = hit

	local raiz = Instance.new("Frame")
	raiz.Size = UDim2.fromScale(1, 1); raiz.BackgroundTransparency = 1; raiz.Parent = bb

	local nome = Instance.new("TextLabel")
	nome.Name = "Nome"
	nome.Size = UDim2.new(1, 0, 0, ehChefe and 26 or 18)
	nome.BackgroundTransparency = 1
	nome.Font = Enum.Font.GothamBold; nome.TextScaled = true
	nome.TextColor3 = corTexto; nome.TextStrokeTransparency = 0.2
	nome.Text = texto
	nome.Parent = raiz

	local fundo = Instance.new("Frame")
	fundo.Name = "Fundo"
	fundo.Size = UDim2.new(1, 0, 0, ehChefe and 22 or 15)
	fundo.Position = UDim2.new(0, 0, 0, ehChefe and 28 or 19)
	fundo.BackgroundColor3 = Color3.fromRGB(18, 18, 22); fundo.BorderSizePixel = 0
	fundo.Parent = raiz
	local u1 = Instance.new("UICorner"); u1.CornerRadius = UDim.new(0, 4); u1.Parent = fundo
	local st = Instance.new("UIStroke"); st.Thickness = 1.5; st.Parent = fundo

	local barra = Instance.new("Frame")
	barra.Name = "Barra"; barra.Size = UDim2.fromScale(1, 1)
	barra.BackgroundColor3 = ehChefe and Color3.fromRGB(255, 90, 60) or Color3.fromRGB(120, 220, 130)
	barra.BorderSizePixel = 0; barra.Parent = fundo
	local u2 = Instance.new("UICorner"); u2.CornerRadius = UDim.new(0, 4); u2.Parent = barra

	local txt = Instance.new("TextLabel")
	txt.Name = "HPTexto"; txt.Size = UDim2.fromScale(1, 1)
	txt.BackgroundTransparency = 1
	txt.Font = Enum.Font.GothamBold; txt.TextScaled = true
	txt.TextColor3 = Color3.new(1,1,1); txt.TextStrokeTransparency = 0.3
	txt.ZIndex = 2; txt.Text = tostring(hp) .. " / " .. tostring(hp)
	txt.Parent = fundo

	local rec = Instance.new("TextLabel")
	rec.Name = "Recompensa"
	rec.Size = UDim2.new(1, 0, 0, ehChefe and 22 or 16)
	rec.Position = UDim2.new(0, 0, 0, ehChefe and 52 or 36)
	rec.BackgroundTransparency = 1
	rec.Font = Enum.Font.GothamBold; rec.TextScaled = true
	rec.TextColor3 = ehChefe and Color3.fromRGB(140, 230, 255) or Color3.fromRGB(255, 215, 90)
	rec.TextStrokeTransparency = 0.2
	rec.Text = recompensa
	rec.Parent = raiz
end

-- pinta o clone usando a cor do tema (os modelos importados vem sem cor)
local ROCHA_ESCURA = Color3.fromRGB(58, 56, 64)
local ROCHA_MEDIA  = Color3.fromRGB(84, 82, 92)

local function pintarMinerio(visual, corTema, ehChefe)
	for _, d in ipairs(visual:GetDescendants()) do
		if d:IsA("BasePart") then
			local n = d.Name
			if string.find(n, "cristal_saliente", 1, true)
				or string.find(n, "fragmento_flutuante", 1, true)
				or string.find(n, "aureola_lasca", 1, true) then
				d.Color = corTema
				d.Material = Enum.Material.Neon
			elseif string.find(n, "lasca", 1, true) then
				d.Color = corTema:Lerp(Color3.new(1,1,1), 0.25)
				d.Material = Enum.Material.Glass
				d.Transparency = 0.15
			elseif string.find(n, "rachadura", 1, true) then
				d.Color = corTema
				d.Material = Enum.Material.Neon
			elseif string.find(n, "emblema", 1, true)
				or string.find(n, "anel_ritual", 1, true)
				or string.find(n, "faixa_metal", 1, true) then
				d.Color = corTema:Lerp(Color3.fromRGB(210, 210, 220), 0.5)
				d.Material = Enum.Material.Metal
				d.Reflectance = 0.15
			elseif string.find(n, "massa_minerio", 1, true) then
				d.Color = corTema:Lerp(ROCHA_ESCURA, 0.62)
				d.Material = Enum.Material.Rock
			elseif string.find(n, "obelisco", 1, true) or string.find(n, "plinto", 1, true) then
				d.Color = ROCHA_ESCURA
				d.Material = Enum.Material.Slate
			else -- escombros e o resto
				d.Color = ROCHA_MEDIA:Lerp(corTema, 0.12)
				d.Material = Enum.Material.Rock
			end
		end
	end

	-- brilho no nucleo
	local nucleo
	for _, d in ipairs(visual:GetDescendants()) do
		if d:IsA("BasePart") and string.find(d.Name, "cristal_saliente_1", 1, true) then nucleo = d; break end
	end
	if nucleo then
		local l = Instance.new("PointLight")
		l.Color = corTema
		l.Brightness = ehChefe and 3 or 1.1
		l.Range = ehChefe and 45 or 14
		l.Parent = nucleo
	end
end

local function criarRocha(area, pos, variante, ehChefe, parent)
	local tema = Config.Temas[area.tema]
	local nomeModelo = Config.modeloMinerio(area.tema, ehChefe and "chefe" or variante.id)
	local template = MODELOS:FindFirstChild(nomeModelo)
	if not template then
		warn("[AreaBuilder] modelo faltando: " .. nomeModelo)
		return
	end

	local hp = ehChefe and area.bossHP or (area.rochaHP * variante.hp)

	local grupo = Instance.new("Model")
	grupo.Name = ehChefe and "PedraChefe" or "Rocha"
	grupo.Parent = parent

	local visual = template:Clone()
	visual.Name = "Visual"
	visual.Parent = grupo
	visual:ScaleTo(ehChefe and (area.id==1 and 6.5 or ESCALA_CHEFE) or (area.id==1 and 5.2 or ESCALA_ROCHA))

	for _, d in ipairs(visual:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.CastShadow = ehChefe
		end
	end

	local oreColor=tema.cor
 if area.id==1 and not ehChefe then
  oreColor=variante.id=="epica" and Color3.fromRGB(189,114,255) or variante.id=="incomum" and Color3.fromRGB(255,183,50) or tema.cor
 end
 pintarMinerio(visual, oreColor, ehChefe)

	local c, t = bbox(visual)
	visual:PivotTo(visual:GetPivot() + (pos + Vector3.new(0, t.Y/2, 0) - c))
	local cf = visual:GetPivot()
	visual:PivotTo(CFrame.new(cf.Position) * CFrame.Angles(0, rnd:NextNumber(0, 6.28), 0))

	-- The collision/contact volume follows the solid ore, excluding scattered rubble.
 local mn,mx=Vector3.new(math.huge,math.huge,math.huge),Vector3.new(-math.huge,-math.huge,-math.huge)
 local count=0
 for _,p in ipairs(visual:GetDescendants()) do
  if p:IsA("BasePart") and (p.Name:find("massa_minerio",1,true) or p.Name=="plinto") then
   for _,x in ipairs({-1,1}) do for _,y in ipairs({-1,1}) do for _,z in ipairs({-1,1}) do
    local point=p.CFrame:PointToWorldSpace(p.Size*Vector3.new(x,y,z)*.5)
    mn=mn:Min(point) mx=mx:Max(point)
   end end end
   count+=1
  end
 end
 local c2,t2
 if count>0 then c2=(mn+mx)*.5 t2=mx-mn else c2,t2=bbox(visual) end

	local hit = novaPart({
		Name = "Hitbox", Size = t2, Position = c2,
		Transparency = 1, CanCollide = true, CanQuery = true,
	}, grupo)

	hit:SetAttribute("AreaId", area.id)
	hit:SetAttribute("Tema", area.tema)
	hit:SetAttribute("Variante", ehChefe and "chefe" or variante.id)
	hit:SetAttribute("HPMax", hp)
	hit:SetAttribute("HP", hp)
	hit:SetAttribute("Chefe", ehChefe)

	local cd = Instance.new("ClickDetector")
	cd.MaxActivationDistance = ehChefe and 55 or 30
	cd.Parent = hit

	if ehChefe then
		etiqueta(hit, area.nome:upper() .. " - CHEFE", Color3.fromRGB(255, 120, 80),
			hp, t2.Y * 0.65, true, "DESBLOQUEIA A PROXIMA AREA")
	else
		local info = Config.infoMinerio(Config.idMinerio(area.tema, variante.id))
		etiqueta(hit, info.nome, tema.cor, hp, t2.Y * 0.7, false, "+1   $" .. info.valor)
	end
	return grupo
end

function AreaBuilder.construir()
	local ws = workspace
	local antigo = ws:FindFirstChild("Areas")
	if antigo then antigo:Destroy() end

	local raiz = Instance.new("Folder"); raiz.Name = "Areas"; raiz.Parent = ws
	local total = 0

	for _, area in ipairs(Config.Areas) do
		local mod = Instance.new("Model"); mod.Name = "Area" .. area.id; mod.Parent = raiz
		mod:SetAttribute("AreaId", area.id)

		local c, t = area.centro, area.tamanho
		local tema = Config.Temas[area.tema]
		local corChao = tema.cor:Lerp(Color3.fromRGB(34, 32, 38), 0.78)

		local custom
		if area.id==1 then custom=FolhaEnvironment.build(mod,area) else
		novaPart({ Name = "Piso", Size = Vector3.new(t.X, 4, t.Z),
			Position = c - Vector3.new(0, 2, 0), Color = corChao,
			Material = Enum.Material.Slate }, mod)

		for _, dx in ipairs({-1, 1}) do
			novaPart({ Name = "Parede", Size = Vector3.new(6, 40, t.Z),
				Position = c + Vector3.new(dx * (t.X/2), 18, 0),
				Color = corChao:Lerp(Color3.new(0,0,0), 0.25),
				Material = Enum.Material.Rock }, mod)
		end

		local placa = novaPart({ Name = "Placa", Size = Vector3.new(1,1,1), Transparency = 1,
			CanCollide = false, Position = c + Vector3.new(0, 20, -t.Z/2 + 8) }, mod)
		local bbP = Instance.new("BillboardGui")
		bbP.Size = UDim2.fromOffset(150, 24); bbP.MaxDistance = 220; bbP.Parent = placa
		local lbl = Instance.new("TextLabel")
		lbl.Size = UDim2.fromScale(1,1); lbl.BackgroundTransparency = 1
		lbl.Font = Enum.Font.GothamBold; lbl.TextScaled = true
		lbl.TextColor3 = tema.cor; lbl.TextStrokeTransparency = 0.25
		lbl.Text = area.id .. ". " .. area.nome
		lbl.Parent = bbP

		end

		local rochas = Instance.new("Folder"); rochas.Name = "Rochas"; rochas.Parent = mod
		local feitas=0
  if custom then
   for _,entry in ipairs(custom.spawns) do
    criarRocha(area,entry.pos,Config.Variantes[entry.variant],false,rochas)
    feitas+=1
   end
  else
		local usados, tent = {}, 0
		while feitas < area.rochas and tent < area.rochas * 60 do
			tent += 1
			local x = rnd:NextNumber(-t.X/2 + 16, t.X/2 - 16)
			local z = rnd:NextNumber(-t.Z/2 + 26, t.Z/2 - 42)
			local ok = true
			for _, u in ipairs(usados) do
				if (Vector2.new(x, z) - u).Magnitude < 11 then ok = false; break end
			end
			if ok then
				table.insert(usados, Vector2.new(x, z))
				criarRocha(area, c + Vector3.new(x, 0, z), Config.varianteSorteada(rnd), false, rochas)
				feitas += 1
			end
		end
  end
		total += feitas

		criarRocha(area, custom and custom.boss or c + Vector3.new(0, 0, t.Z/2 - 20), Config.Variantes[1], true, mod)

		local b = novaPart({ Name = "Barreira", Size = Vector3.new(t.X, 40, 4),
			Position = c + Vector3.new(0, 18, t.Z/2 + 2), Color = tema.cor,
			Transparency = 0.65, Material = Enum.Material.ForceField, CanCollide = true }, mod)
		b:SetAttribute("LiberaComArea", area.id + 1)

		local prox = Config.areaPorId(area.id + 1)
		if prox then
			local zI = c.Z + t.Z/2
			local zF = prox.centro.Z - prox.tamanho.Z/2
			novaPart({ Name = "Corredor", Size = Vector3.new(40, 4, zF - zI),
				Position = Vector3.new(c.X, c.Y - 2, (zI + zF)/2),
				Color = Color3.fromRGB(46, 44, 50), Material = Enum.Material.Slate }, mod)
		end

		local volta = novaPart({ Name = "VoltarLobby", Size = Vector3.new(14, 1, 14),
			CanCollide = false, Position = custom and custom.returnPad or c + Vector3.new(-t.X/2 + 16, 0.5, -t.Z/2 + 14),
			Color = Color3.fromRGB(90, 190, 255), Material = Enum.Material.Neon }, mod)
		volta:SetAttribute("Destino", "lobby")
	end

	print("[AreaBuilder] " .. #Config.Areas .. " areas, " .. total .. " rochas")
	return raiz
end

return AreaBuilder
