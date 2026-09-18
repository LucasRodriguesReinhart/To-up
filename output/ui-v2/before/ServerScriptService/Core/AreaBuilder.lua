local RS = game:GetService("ReplicatedStorage")
local SS = game:GetService("ServerStorage")
local Config = require(RS.Config)
local IslandWorld = require(script.Parent.IslandWorld)
local SpawnMinerio = require(script.Parent.SpawnMinerio)

local AreaBuilder = {}
local rnd = Random.new(1337)
local MODELOS = SS:WaitForChild("Modelos")
local OreVFX = require(RS:WaitForChild("OreVFX"))

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

-- etiqueta da rocha (UI V2): nome com contorno, barra grossa com trilho escuro e recompensa em moedas.
-- Nomes preservados (Vida / Nome / Fundo / Barra / HPTexto / Recompensa): Mineracao.atualizarBarra usa esses nomes.
local FONTE_UI = Font.new("rbxasset://fonts/families/FredokaOne.json")
local TINTA = Color3.fromRGB(10, 6, 22)
local ATLAS_ICONES = "rbxassetid://104814264232835"

local function etiqueta(hit, texto, corTexto, hp, alturaOffset, ehChefe, recompensa)
	local largura = ehChefe and 240 or 158
	local alturaNome = ehChefe and 28 or 20
	local alturaBarra = ehChefe and 26 or 20
	local alturaPremio = ehChefe and 24 or 18

	local bb = Instance.new("BillboardGui")
	bb.Name = "Vida"
	bb.Size = UDim2.fromOffset(largura, alturaNome + alturaBarra + alturaPremio + 8)
	bb.StudsOffset = Vector3.new(0, alturaOffset, 0)
	bb.AlwaysOnTop = false
	bb.MaxDistance = ehChefe and 85 or 70
	bb.Enabled = ehChefe
	bb.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	bb.Parent = hit

	local raiz = Instance.new("Frame")
	raiz.Size = UDim2.fromScale(1, 1); raiz.BackgroundTransparency = 1; raiz.Parent = bb

	local nome = Instance.new("TextLabel")
	nome.Name = "Nome"
	nome.Size = UDim2.new(1, 0, 0, alturaNome)
	nome.BackgroundTransparency = 1
	nome.FontFace = FONTE_UI
	nome.TextScaled = true
	nome.TextColor3 = corTexto
	nome.Text = texto
	nome.Parent = raiz
	local nomeStroke = Instance.new("UIStroke")
	nomeStroke.Color = TINTA; nomeStroke.Thickness = ehChefe and 3 or 2.2
	nomeStroke.LineJoinMode = Enum.LineJoinMode.Round; nomeStroke.Parent = nome

	local fundo = Instance.new("Frame")
	fundo.Name = "Fundo"
	fundo.Size = UDim2.new(1, 0, 0, alturaBarra)
	fundo.Position = UDim2.new(0, 0, 0, alturaNome + 2)
	fundo.BackgroundColor3 = Color3.fromRGB(9, 7, 20)
	fundo.BorderSizePixel = 0
	fundo.Parent = raiz
	local u1 = Instance.new("UICorner"); u1.CornerRadius = UDim.new(0, math.floor(alturaBarra / 2)); u1.Parent = fundo
	local st = Instance.new("UIStroke"); st.Thickness = 2.5; st.Color = TINTA; st.Parent = fundo

	-- trilho interno: a barra vive aqui dentro (sobra 3 px de moldura em volta)
	local interno = Instance.new("Frame")
	interno.Name = "Interno"
	interno.Position = UDim2.fromOffset(3, 3)
	interno.Size = UDim2.new(1, -6, 1, -6)
	interno.BackgroundTransparency = 1
	interno.ClipsDescendants = true
	interno.Parent = fundo
	local u3 = Instance.new("UICorner"); u3.CornerRadius = UDim.new(0, math.floor(alturaBarra / 2) - 2); u3.Parent = interno

	local barra = Instance.new("Frame")
	barra.Name = "Barra"; barra.Size = UDim2.fromScale(1, 1)
	barra.BackgroundColor3 = ehChefe and Color3.fromRGB(255, 70, 60) or Color3.fromRGB(120, 230, 120)
	barra.BorderSizePixel = 0; barra.ZIndex = 2; barra.Parent = interno
	local u2 = Instance.new("UICorner"); u2.CornerRadius = UDim.new(0, math.floor(alturaBarra / 2) - 2); u2.Parent = barra
	local brilho = Instance.new("UIGradient")
	brilho.Color = ColorSequence.new(Color3.fromRGB(255, 255, 255), Color3.fromRGB(190, 190, 200))
	brilho.Rotation = 90; brilho.Parent = barra

	local txt = Instance.new("TextLabel")
	txt.Name = "HPTexto"; txt.Size = UDim2.fromScale(1, 1)
	txt.BackgroundTransparency = 1
	txt.FontFace = FONTE_UI; txt.TextScaled = true
	txt.TextColor3 = Color3.new(1, 1, 1)
	txt.ZIndex = 4; txt.Text = tostring(hp) .. " / " .. tostring(hp)
	txt.Parent = fundo
	local txtStroke = Instance.new("UIStroke")
	txtStroke.Color = TINTA; txtStroke.Thickness = 2; txtStroke.Parent = txt

	local premio = Instance.new("Frame")
	premio.Name = "PremioLinha"
	premio.Size = UDim2.new(1, 0, 0, alturaPremio)
	premio.Position = UDim2.new(0, 0, 0, alturaNome + alturaBarra + 4)
	premio.BackgroundTransparency = 1
	premio.Parent = raiz

	local moeda = Instance.new("ImageLabel")
	moeda.Name = "Moeda"
	moeda.BackgroundTransparency = 1
	moeda.Image = ATLAS_ICONES
	moeda.ImageRectOffset = Vector2.new(256, 512)   -- indice 9 do atlas (moedas)
	moeda.ImageRectSize = Vector2.new(256, 256)
	moeda.Size = UDim2.fromOffset(alturaPremio, alturaPremio)
	moeda.Position = UDim2.fromOffset(largura / 2 - 52, 0)
	moeda.Parent = premio

	local rec = Instance.new("TextLabel")
	rec.Name = "Recompensa"
	rec.Size = UDim2.new(1, -(largura / 2 - 30), 1, 0)
	rec.Position = UDim2.fromOffset(largura / 2 - 30, 0)
	rec.BackgroundTransparency = 1
	rec.FontFace = FONTE_UI; rec.TextScaled = true
	rec.TextXAlignment = Enum.TextXAlignment.Left
	rec.TextColor3 = ehChefe and Color3.fromRGB(140, 230, 255) or Color3.fromRGB(255, 204, 36)
	rec.Text = recompensa
	rec.Parent = premio
	local recStroke = Instance.new("UIStroke")
	recStroke.Color = TINTA; recStroke.Thickness = 2; recStroke.Parent = rec
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
		l.Brightness = ehChefe and .8 or .5
		l.Range = ehChefe and 17 or 9
		l.Parent = nucleo
	end
end

-- efeito (dourado / arco-iris): brilho no minerio + etiqueta sempre visivel
local function aplicarEfeito(grupo, hit, efeitoId)
	local e = Config.SPAWN.efeitos[efeitoId]
	if not e then return end
	hit:SetAttribute("Efeito", efeitoId)
	local visual = grupo:FindFirstChild("Visual")
	local hl = Instance.new("Highlight")
	hl.Name = "BrilhoEfeito"
	hl.FillColor = e.cor
	hl.FillTransparency = 0.55
	hl.OutlineColor = e.cor:Lerp(Color3.new(1, 1, 1), 0.4)
	hl.DepthMode = Enum.HighlightDepthMode.Occluded
	hl.Adornee = visual or grupo
	hl.Parent = grupo
	local brilho = Instance.new("Sparkles")
	brilho.SparkleColor = e.cor
	brilho.Parent = hit
	local bb = Instance.new("BillboardGui")
	bb.Name = "EtiquetaEfeito"
	bb.Size = UDim2.fromOffset(130, 26)
	bb.StudsOffsetWorldSpace = Vector3.new(0, hit.Size.Y * 0.5 + 3, 0)
	bb.MaxDistance = 90
	bb.Parent = hit
	local t = Instance.new("TextLabel")
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundTransparency = 1
	t.Font = Enum.Font.FredokaOne
	t.TextScaled = true
	t.TextColor3 = e.cor
	t.TextStrokeTransparency = 0.1
	t.Text = e.nome .. " x" .. e.mult
	t.Parent = bb
end

local function criarRocha(area, pos, variante, ehChefe, parent, efeitoId, hpForcado)
	local tema = Config.Temas[area.tema]
	-- raro e lendario reaproveitam os modelos de incomum/epica (variante.modelo)
	local nomeModelo = Config.modeloMinerio(area.tema, ehChefe and "chefe" or (variante.modelo or variante.id))
	local template = MODELOS:FindFirstChild(nomeModelo)
	if not template then
		warn("[AreaBuilder] modelo faltando: " .. nomeModelo)
		return
	end

	local hp = hpForcado or (ehChefe and area.hp.super or area.hp[variante.id])

	local grupo = Instance.new("Model")
	grupo.Name = ehChefe and "PedraChefe" or "Rocha"
	grupo.Parent = parent

	local visual = template:Clone()
	visual.Name = "Visual"
	visual.Parent = grupo
	local escalaTipo = (not ehChefe and variante.id == "lendaria") and 1.25 or ((not ehChefe and variante.id == "raro") and 1.08 or 1)
	visual:ScaleTo((ehChefe and ((area.id>=1 and area.id<=6) and 6.5 or ESCALA_CHEFE) or ((area.id>=1 and area.id<=6) and 5.2 or ESCALA_ROCHA)) * escalaTipo)

	for _, d in ipairs(visual:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = true
			d.CanTouch = false
			d.CastShadow = ehChefe
		end
	end

	local oreColor=tema.cor
 if (area.id>=1 and area.id<=6) and not ehChefe then
  oreColor=variante.id=="epica" and Color3.fromRGB(189,114,255) or variante.id=="incomum" and (area.id==4 and Color3.fromRGB(255,73,81) or Color3.fromRGB(255,183,50)) or (area.id==2 and Color3.fromRGB(59,152,255) or tema.cor)
 end
 if not ehChefe and (variante.id == "raro" or variante.id == "lendaria") and variante.cor then
  oreColor = variante.cor
 end
 if not template:GetAttribute("CoresProprias") or (not ehChefe and (variante.id == "raro" or variante.id == "lendaria")) then
  pintarMinerio(visual, oreColor, ehChefe)
 end
 if not ehChefe and variante.id == "lendaria" then
  local hl = Instance.new("Highlight")
  hl.Name = "BrilhoLendario"
  hl.FillColor = variante.cor
  hl.FillTransparency = 0.7
  hl.OutlineColor = Color3.fromRGB(255, 240, 170)
  hl.DepthMode = Enum.HighlightDepthMode.Occluded
  hl.Adornee = visual
  hl.Parent = grupo
 end

	local volume = visual:FindFirstChild("massa_minerio_volume", true)
	if volume then
		-- modelos novos: pivot na base da rocha, gira em volta dela e apoia no chao
		visual:PivotTo(CFrame.new(pos) * CFrame.Angles(0, rnd:NextNumber(0, 6.28), 0))
	else
		local c, t = bbox(visual)
		visual:PivotTo(visual:GetPivot() + (pos + Vector3.new(0, t.Y/2, 0) - c))
		local cf = visual:GetPivot()
		visual:PivotTo(CFrame.new(cf.Position) * CFrame.Angles(0, rnd:NextNumber(0, 6.28), 0))
	end

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
		-- minerios sao atravessaveis: continuam clicaveis (CanQuery) mas nao bloqueiam ninguem
		Transparency = 1, CanCollide = false, CanQuery = true,
	}, grupo)

	hit:SetAttribute("AreaId", area.id)
	hit:SetAttribute("SpawnPos", pos)
	hit:SetAttribute("Tema", area.tema)
	hit:SetAttribute("Variante", ehChefe and "chefe" or variante.id)
	hit:SetAttribute("HPMax", hp)
	hit:SetAttribute("HP", hp)
	hit:SetAttribute("Chefe", ehChefe)

	-- VFX anime (OreVFX) conforme o tema e a raridade do modelo
	if template:GetAttribute("OreType") then
		hit:SetAttribute("OreType", template:GetAttribute("OreType"))
		hit:SetAttribute("Rarity", ehChefe and template:GetAttribute("Rarity") or (variante.oreRarity or template:GetAttribute("Rarity")))
		task.defer(function()
			local ok, err = pcall(OreVFX.Attach, hit)
			if not ok then warn("[AreaBuilder] OreVFX: " .. tostring(err)) end
		end)
	end

	local cd = Instance.new("ClickDetector")
	cd.MaxActivationDistance = ehChefe and 55 or 30
	cd.Parent = hit

	if ehChefe then
		etiqueta(hit, "CHEFE", Color3.fromRGB(255, 120, 80),
			hp, t2.Y * 0.65, true, "+" .. Config.formatar(area.valores.super) .. " por ajudante")
	else
		local info = Config.infoMinerio(Config.idMinerio(area.tema, variante.id))
		etiqueta(hit, info.nome, variante.cor or tema.cor, hp, t2.Y * 0.7, false, Config.formatar(info.valor))
	end
	if efeitoId then aplicarEfeito(grupo, hit, efeitoId) end
	return grupo
end

-- usado pelo respawn: cria um minerio da variante pedida numa posicao sorteada da ilha
-- posFixa: usado pela amplificacao (o minerio vira outro no mesmo lugar)
function AreaBuilder.novoMinerio(area, pastaRochas, ignorarGrupo, varianteId, posFixa, efeitoId)
	local pos = posFixa or SpawnMinerio.posicaoLivre(area.id, pastaRochas, ignorarGrupo)
	if not pos then return nil end
	return criarRocha(area, pos, Config.variantePorId(varianteId or "comum"), false, pastaRochas, efeitoId)
end

-- chefe nasce em qualquer lugar livre da ilha (com espaco pro tamanho dele).
-- a arena original so e usada se nenhum ponto couber.
AreaBuilder.arenas = {}  -- [areaId] = { pos = Vector3, pasta = Folder }
function AreaBuilder.novoChefe(area, hpLuta)
	local arena = AreaBuilder.arenas[area.id]
	if not arena or not arena.pasta.Parent then return nil end
	local pos = SpawnMinerio.posicaoLivre(area.id, arena.pasta, nil, true) or arena.pos
	return criarRocha(area, pos, Config.Variantes[1], true, arena.pasta, nil, hpLuta)
end

function AreaBuilder.chefesVivos(area)
	local arena = AreaBuilder.arenas[area.id]
	local n = 0
	if arena then
		for _, g in ipairs(arena.pasta:GetChildren()) do if g.Name == "PedraChefe" then n += 1 end end
	end
	return n
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
		if area.id>=1 and area.id<=6 then custom=IslandWorld.build(mod,area) else
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
   -- pontos originais + extras gerados; cada minerio nasce num ponto sorteado e a variante
   -- vem do sistema de progressao (SpawnMinerio)
   local originais={}
   for _,entry in ipairs(custom.spawns) do table.insert(originais,entry.pos) end
   if custom.boss then table.insert(originais,custom.boss) end
   -- lugares onde nao pode nascer minerio: entrada, gacha, volta pro lobby e portais
   local evitar={}
   for _,nome in ipairs({"EntryPosition","GachaPosition"}) do
    local v=mod:GetAttribute(nome) if typeof(v)=="Vector3" then table.insert(evitar,v) end
   end
   if custom.returnPad then table.insert(evitar,custom.returnPad) end
   for _,d in ipairs(mod:GetDescendants()) do
    if d:IsA("BasePart") and (d:GetAttribute("NextAreaId") or d:GetAttribute("Destino")) then table.insert(evitar,d.Position) end
   end
   local lista=SpawnMinerio.registrarPontos(area,originais,{rochas},evitar,custom.zonas)
   area.pontosMinerio=#lista
   -- servidor novo: um pouco de cada (Config.SPAWN.inicial), o resto dos pontos vira comum
   local ini=Config.SPAWN.inicial
   local plano={}
   for _,vid in ipairs({"lendaria","epica","raro","incomum"}) do
    for _=1,ini[vid] or 0 do table.insert(plano,vid) end
   end
   for _=#plano+1,math.min(Config.SPAWN.minerios or #custom.spawns,#lista-2) do table.insert(plano,"comum") end
   for _,vid in ipairs(plano) do
    local pos=SpawnMinerio.posicaoLivre(area.id,rochas)
    if pos then
     criarRocha(area,pos,Config.variantePorId(vid),false,rochas)
     feitas+=1
    end
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

		AreaBuilder.arenas[area.id] = { pos = custom and custom.boss or c + Vector3.new(0, 0, t.Z/2 - 20), pasta = rochas }
		-- chefe e global (BossService): nao nasce na construcao da ilha
		local ini = Config.SPAWN.inicial
		SpawnMinerio.publicar(area.id, { incomum = ini.incomum or 0, raro = ini.raro or 0, epica = ini.epica or 0, lendaria = ini.lendaria or 0 })

		local volta = novaPart({ Name = "VoltarLobby", Size = custom and Vector3.new(6,.3,6) or Vector3.new(14,1,14),
			CanCollide = false, Position = custom and custom.returnPad or c + Vector3.new(-t.X/2 + 16, 0.5, -t.Z/2 + 14),
			Color = Color3.fromRGB(90, 190, 255), Material = Enum.Material.Neon }, mod)
		volta:SetAttribute("Destino", "lobby")
  if custom then
   volta.Transparency=.45
   local gui=Instance.new("BillboardGui") gui.Size=UDim2.fromOffset(90,22) gui.StudsOffset=Vector3.new(0,2,0) gui.MaxDistance=28 gui.Parent=volta
   local label=Instance.new("TextLabel") label.Size=UDim2.fromScale(1,1) label.BackgroundTransparency=1 label.Text="LOBBY" label.Font=Enum.Font.GothamBold label.TextSize=16 label.TextColor3=Color3.new(1,1,1) label.TextStrokeTransparency=.4 label.Parent=gui
  end
	end

	print("[AreaBuilder] " .. #Config.Areas .. " areas, " .. total .. " rochas")
	return raiz
end

return AreaBuilder

