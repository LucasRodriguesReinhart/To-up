-- CinematicaInvocacao (LocalScript, StarterPlayerScripts) - cinematica da invocacao na torre da Ilha 3 para as raridades
-- ALTAS (so mitico e secreto). O ExpeditionClient chama ReplicatedStorage.CinematicaInvocacao:Invoke(areaId, results)
-- logo antes da tela da estrela; o Invoke so volta quando a cinematica acaba (ou o jogador clica para pular). Fora da
-- area 3, longe da torre ou raridade menor: volta na hora (a invocacao segue igual a antes).
-- Sequencia (~2,6 s, cor da raridade): plano baixo da plataforma olhando a torre -> carga (riscos subindo do circulo ate a
-- esfera armilar, aneis se fechando no piso, nucleo crescendo, tinta e vinheta) -> FEIXE da esfera no circulo com
-- IMPACT FRAME preto e branco e corte -> liberacao (ondas no piso, faiscas, tremida forte, FOV) -> flash na cor da
-- raridade que entrega para a tela da estrela. Tudo so neste cliente.
local Players = game:GetService('Players')
local RS = game:GetService('ReplicatedStorage')
local RunService = game:GetService('RunService')
local TweenService = game:GetService('TweenService')
local Lighting = game:GetService('Lighting')
local GuiService = game:GetService('GuiService')
local UIS = game:GetService('UserInputService')
local player = Players.LocalPlayer

local V, C = Vector3.new, Color3.fromRGB
local NS, NSK = NumberSequence.new, NumberSequenceKeypoint.new
local TX = {
	ring = 'rbxassetid://123618418899772',
	glow = 'rbxassetid://119690923296259',
	spark = 'rbxassetid://106034798506002',
	beam = 'rbxassetid://134235069437330',
	risco = 'rbxassetid://77069445230804',
	linhas = 'rbxassetid://121853663711721',
	vinheta = 'rbxassetid://104763198580372',
	disco = 'rbxassetid://89137224521485',
}
task.spawn(function()
	local l = {}
	for _, id in pairs(TX) do local d = Instance.new('Decal'); d.Texture = id; table.insert(l, d) end
	pcall(function() game:GetService('ContentProvider'):PreloadAsync(l) end)
end)
local ORDEM = { comum = 1, incomum = 2, raro = 3, epico = 4, lendario = 5, mitico = 6, secreto = 7 }
local MINIMO = 6                     -- so mitico e secreto (pedido do usuario)
local DIST_TORRE = 70

local function clamp01(t) return math.clamp(t, 0, 1) end
local function easeOut(t) return 1 - (1 - t) ^ 3 end
local function easeIn(t) return t * t * t end

local function marcador(nome)
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	local ilha = a3 and a3:FindFirstChild('ILHA_SHADOWGARDEN')
	local mk = ilha and ilha:FindFirstChild('GAMEPLAY_MARKERS')
	return mk and mk:FindFirstChild(nome)
end

local function corRaridade(key)
	-- cores oficiais em Config.Raridades (a UI antiga ExpeditionUI saiu; WaitForChild nela travava 5 s)
	local ok, Config = pcall(require, RS:FindFirstChild('Config'))
	local r = ok and Config and Config.Raridades and Config.Raridades[key]
	if r and typeof(r.cor) == 'Color3' then return r.cor end
	return C(190, 110, 255)
end

local function peca(pai, nome, tam, cf, forma)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf; p.Shape = forma or Enum.PartType.Block
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1; p.Parent = pai
	return p
end
local function sgui(p, face, brilho)
	local s = Instance.new('SurfaceGui'); s.Face = face; s.LightInfluence = 0; s.Brightness = brilho
	s.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize; s.CanvasSize = Vector2.new(1024, 1024); s.Parent = p
	return s
end
local function img(pai, tex, escala, cor, transp, z)
	local i = Instance.new('ImageLabel'); i.BackgroundTransparency = 1; i.Image = tex; i.ImageColor3 = cor
	i.ImageTransparency = transp; i.AnchorPoint = Vector2.new(0.5, 0.5); i.Position = UDim2.fromScale(0.5, 0.5)
	i.Size = UDim2.fromScale(escala, escala); i.ZIndex = z or 1; i.Parent = pai
	return i
end

local function tocar(raridade)
	local main, pp = marcador('SUMMON_Main'), marcador('SUMMON_PlayerPosition')
	local char = player.Character
	local hrp = char and char:FindFirstChild('HumanoidRootPart')
	local hum = char and char:FindFirstChildOfClass('Humanoid')
	if not (main and pp and hrp and hum) then return end
	if (hrp.Position - pp.Position).Magnitude > DIST_TORRE then return end
	local reduzido = false
	pcall(function() reduzido = GuiService.ReducedMotionEnabled end)
	local cor = corRaridade(raridade):Lerp(Color3.new(1, 1, 1), 0.2)
	local fw = V(pp:GetAttribute('fwd_x') or 0, 0, pp:GetAttribute('fwd_z') or 1).Unit      -- do circulo para a torre
	local lado = fw:Cross(V(0, 1, 0)).Unit
	local piso = pp.Position.Y
	local circ = V(pp.Position.X, piso, pp.Position.Z)
	local fwT = V(main:GetAttribute('fwd_x') or 0, 0, main:GetAttribute('fwd_z') or -1).Unit
	local eixo = V(main.Position.X, piso, main.Position.Z) - fwT * 1.4
	local esfera = eixo + V(0, 46.2, 0) - fwT * 1.8
	player:SetAttribute('CinematicaInvocacaoEm', os.clock())

	-- o jogador invoca com o menu aberto: as outras telas somem durante a cinematica e voltam antes da revelacao
	local telas = {}
	for _, g in ipairs(player:WaitForChild('PlayerGui'):GetChildren()) do
		if g:IsA('ScreenGui') and g.Enabled then telas[g] = true; g.Enabled = false end
	end
	local pasta = Instance.new('Folder'); pasta.Name = 'CinematicaInvocacao_Local'; pasta.Parent = workspace
	-- riscos subindo do circulo ate a esfera
	local base = peca(pasta, 'Base', V(14, 0.2, 14), CFrame.new(circ + V(0, 0.3, 0)))
	local riscos = Instance.new('ParticleEmitter')
	riscos.Texture = TX.risco; riscos.Color = ColorSequence.new(Color3.new(1, 1, 1), cor); riscos.Rate = 0
	riscos.Lifetime = NumberRange.new(0.8, 1.0); riscos.Speed = NumberRange.new(45, 60)
	riscos.Acceleration = (esfera - circ).Unit * 25 * V(1, 0, 1)
	riscos.EmissionDirection = Enum.NormalId.Top; riscos.SpreadAngle = Vector2.new(8, 8)
	riscos.Orientation = Enum.ParticleOrientation.VelocityParallel; riscos.Rotation = NumberRange.new(90)
	riscos.Squash = NS(2.4); riscos.Size = NS({ NSK(0, 1.4), NSK(1, 0.3) })
	riscos.Transparency = NS({ NSK(0, 1), NSK(0.1, 0), NSK(0.8, 0.1), NSK(1, 1) })
	riscos.LightEmission = 1; riscos.LightInfluence = 0; riscos.Brightness = 3
	riscos.Shape = Enum.ParticleEmitterShape.Box; riscos.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
	riscos.Parent = base
	-- aneis se fechando no piso (3 defasados) e onda de liberacao
	local anelP = peca(pasta, 'Aneis', V(40, 0.05, 40), CFrame.new(circ + V(0, 0.18, 0)))
	local anelS = sgui(anelP, Enum.NormalId.Top, 3)
	local aneis = {}
	for i = 1, 3 do table.insert(aneis, img(anelS, TX.ring, 1, cor, 1, i)) end
	local onda = peca(pasta, 'Onda', V(2, 0.05, 2), CFrame.new(circ + V(0, 0.22, 0)))
	local ondaImg = img(sgui(onda, Enum.NormalId.Top, 4), TX.ring, 1, cor, 1)
	-- nucleo da esfera armilar crescendo
	local nucleo = peca(pasta, 'Nucleo', V(1, 1, 1), CFrame.new(esfera), Enum.PartType.Ball)
	nucleo.Material = Enum.Material.Neon; nucleo.Color = cor; nucleo.Transparency = 0.15
	local luz = Instance.new('PointLight'); luz.Color = cor; luz.Range = 50; luz.Brightness = 0; luz.Parent = nucleo
	local halo = peca(pasta, 'Halo', V(1, 1, 1), CFrame.new(esfera))
	local haloG = Instance.new('BillboardGui'); haloG.Size = UDim2.fromScale(40, 40); haloG.LightInfluence = 0
	haloG.Brightness = 3; haloG.AlwaysOnTop = false; haloG.Parent = halo
	local haloImg = img(haloG, TX.disco, 1, cor, 1)
	-- feixe da esfera ao circulo (nucleo branco + corpo na cor)
	local a0 = Instance.new('Attachment'); a0.Parent = nucleo
	local a1 = Instance.new('Attachment'); a1.Parent = base
	local function feixe(w, c, transp)
		local b = Instance.new('Beam'); b.Attachment0 = a0; b.Attachment1 = a1; b.FaceCamera = true
		b.Texture = TX.beam; b.TextureMode = Enum.TextureMode.Stretch; b.TextureSpeed = 4; b.Segments = 1
		b.LightEmission = 1; b.LightInfluence = 0; b.Brightness = 4; b.Color = ColorSequence.new(c)
		b.Width0 = 0; b.Width1 = 0; b.Transparency = NS(transp); b.Parent = nucleo
		return b, w
	end
	local feixeCor, wCor = feixe(6, cor, 0.25)
	local feixeBranco, wBranco = feixe(1.8, Color3.new(1, 1, 1), 0)
	local faiscas = Instance.new('ParticleEmitter')
	faiscas.Texture = TX.spark; faiscas.Color = ColorSequence.new(Color3.new(1, 1, 1), cor); faiscas.Rate = 0
	faiscas.Lifetime = NumberRange.new(0.7, 1.2); faiscas.Speed = NumberRange.new(25, 50); faiscas.Drag = 3
	faiscas.SpreadAngle = Vector2.new(75, 75); faiscas.Size = NS({ NSK(0, 1), NSK(1, 0.1) })
	faiscas.Transparency = NS({ NSK(0, 0), NSK(1, 1) }); faiscas.LightEmission = 1; faiscas.Brightness = 3
	faiscas.Acceleration = V(0, -12, 0); faiscas.Parent = base

	-- tela
	local gui = Instance.new('ScreenGui'); gui.Name = 'CinematicaInvocacao'; gui.IgnoreGuiInset = true
	gui.DisplayOrder = 300; gui.ResetOnSpawn = false; gui.Parent = player:WaitForChild('PlayerGui')
	local vinheta = Instance.new('ImageLabel'); vinheta.BackgroundTransparency = 1; vinheta.Image = TX.vinheta
	vinheta.Size = UDim2.fromScale(1, 1); vinheta.ImageTransparency = 1; vinheta.Parent = gui
	local linhas = Instance.new('ImageLabel'); linhas.BackgroundTransparency = 1; linhas.Image = TX.linhas
	linhas.AnchorPoint = Vector2.new(0.5, 0.5); linhas.Position = UDim2.fromScale(0.5, 0.5)
	linhas.SizeConstraint = Enum.SizeConstraint.RelativeXX; linhas.Size = UDim2.fromScale(1.5, 1.5)
	linhas.ImageColor3 = cor:Lerp(Color3.new(1, 1, 1), 0.5); linhas.ImageTransparency = 1; linhas.ZIndex = 2; linhas.Parent = gui
	local flash = Instance.new('Frame'); flash.BorderSizePixel = 0; flash.Size = UDim2.fromScale(1, 1)
	flash.BackgroundColor3 = Color3.new(1, 1, 1); flash.BackgroundTransparency = 1; flash.ZIndex = 5; flash.Parent = gui
	local dica = Instance.new('TextLabel'); dica.BackgroundTransparency = 1; dica.AnchorPoint = Vector2.new(1, 1)
	dica.Position = UDim2.new(1, -24, 1, -20); dica.Size = UDim2.fromOffset(260, 26); dica.TextXAlignment = Enum.TextXAlignment.Right
	dica.Font = Enum.Font.GothamBold; dica.TextSize = 16; dica.Text = 'Toque para pular'; dica.TextColor3 = C(230, 225, 245)
	dica.TextTransparency = 0.35; dica.ZIndex = 6; dica.Parent = gui
	local cc = Instance.new('ColorCorrectionEffect'); cc.Name = 'CinematicaInvocacaoCC'; cc.Parent = Lighting
	local destaque = Instance.new('Highlight'); destaque.FillColor = C(0, 0, 0); destaque.OutlineColor = C(255, 255, 255)
	destaque.FillTransparency = 1; destaque.OutlineTransparency = 1; destaque.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
	destaque.Adornee = char; destaque.Parent = gui

	local cam = workspace.CurrentCamera
	local fov0 = cam.FieldOfView
	local camIni = cam.CFrame
	cam.CameraType = Enum.CameraType.Scriptable
	hrp.Anchored = true
	-- posicoes de camera presas antes de paredes (a plataforma e estreita: a camera entrava na rocha)
	local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { char }
	local function livre(pos)
		local de = circ + V(0, 3, 0)
		local r = workspace:Raycast(de, pos - de, params)
		if r then return de + (r.Position - de) * 0.85 end
		return pos
	end
	local foco = circ:Lerp(esfera, 0.62)
	local camA = CFrame.lookAt(livre(circ - fw * 13 + lado * 7 + V(0, 1.2, 0)), foco)
	local camB = CFrame.lookAt(livre(circ - fw * 9 + lado * 5 + V(0, 0.8, 0)), foco + V(0, 4, 0))
	local camC = CFrame.lookAt(livre(circ - fw * 20 - lado * 8 + V(0, 3, 0)), circ:Lerp(esfera, 0.45))   -- corte do impacto
	local T = 2.6
	local tFeixe, tLibera = T * 0.46, T * 0.54
	local pular = false
	local conIn = UIS.InputBegan:Connect(function(inp)
		if inp.UserInputType == Enum.UserInputType.MouseButton1 or inp.UserInputType == Enum.UserInputType.Touch then pular = true end
	end)
	local escala = math.max(1, player:GetAttribute('CinematicaEscala') or 1)
	local t0 = os.clock()
	local soltou = false
	while true do
		local dt = RunService.RenderStepped:Wait() / escala
		local t = (os.clock() - t0) / escala
		if pular and t < T - 0.25 then t0 = os.clock() - (T - 0.25) * escala; t = T - 0.25 end
		if t >= T then break end
		local k = clamp01(t / tFeixe)
		-- carga
		riscos.Rate = t < tLibera and (20 + 160 * k) or 0
		for i, a in ipairs(aneis) do
			local u = ((t * 1.3) + i / 3) % 1
			a.Size = UDim2.fromScale(1 - 0.75 * u, 1 - 0.75 * u)
			a.ImageTransparency = t < tLibera and (1 - 0.8 * math.sin(u * math.pi) * (0.3 + 0.7 * k)) or 1
		end
		local tn = 1 + 7 * easeOut(k)
		nucleo.Size = V(tn, tn, tn)
		luz.Brightness = 2 + 5 * k
		haloImg.ImageTransparency = 1 - 0.6 * k
		haloImg.Rotation = t * 300
		vinheta.ImageTransparency = 1 - 0.8 * k
		linhas.ImageTransparency = 1 - 0.55 * clamp01((t - 0.4) / 0.6)
		linhas.Rotation = t * 15
		local shake = reduzido and 0 or (0.05 + 0.25 * k)
		if t < tFeixe then
			cam.CFrame = camIni:Lerp(camA, easeOut(clamp01(t / 0.35))):Lerp(camB, clamp01((t - 0.35) / (tFeixe - 0.35)))
			cam.FieldOfView = fov0 + (60 - fov0) * easeOut(k)
			cc.TintColor = Color3.new(1, 1, 1):Lerp(cor:Lerp(Color3.new(1, 1, 1), 0.6), k); cc.Contrast = 0.2 * k; cc.Saturation = 0.15 * k
		elseif t < tLibera then
			-- FEIXE + IMPACT FRAME
			feixeCor.Width0, feixeCor.Width1 = wCor, wCor * 0.8
			feixeBranco.Width0, feixeBranco.Width1 = wBranco, wBranco
			cam.CFrame = camC
			cam.FieldOfView = 52
			if not reduzido then
				cc.Saturation = -1; cc.Contrast = 2.2; cc.Brightness = 0.12; cc.TintColor = Color3.new(1, 1, 1)
				destaque.FillTransparency = 0; destaque.OutlineTransparency = 0
				flash.BackgroundTransparency = t - tFeixe < 0.04 and 0 or 1
			end
			shake = reduzido and 0 or 0.9
		else
			-- LIBERACAO
			if not soltou then
				soltou = true
				faiscas:Emit(60)
				onda.Size = V(2, 0.05, 2); ondaImg.ImageTransparency = 0
				TweenService:Create(onda, TweenInfo.new(0.8, Enum.EasingStyle.Quart), { Size = V(70, 0.05, 70) }):Play()
				TweenService:Create(ondaImg, TweenInfo.new(0.8, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { ImageTransparency = 1 }):Play()
			end
			local m = clamp01((t - tLibera) / (T - tLibera))
			destaque.FillTransparency = 1; destaque.OutlineTransparency = 1
			cc.Saturation = 0.2; cc.Contrast = 0.25; cc.Brightness = 0; cc.TintColor = cor:Lerp(Color3.new(1, 1, 1), 0.55)
			local pulso = 1 + 0.25 * math.sin(t * 40)
			feixeCor.Width0, feixeCor.Width1 = wCor * pulso * (1 + 0.4 * m), wCor * (1 + 0.4 * m)
			feixeBranco.Width0, feixeBranco.Width1 = wBranco * pulso, wBranco
			cam.CFrame = camC * CFrame.new(0, 0, -6 * easeOut(m))
			cam.FieldOfView = 52 + 26 * easeOut(m)
			shake = reduzido and 0 or 0.9 * (1 - m) + 0.1
			flash.BackgroundColor3 = cor:Lerp(Color3.new(1, 1, 1), 0.6)
			flash.BackgroundTransparency = reduzido and 1 or (1 - easeIn(clamp01((m - 0.55) / 0.45)))
		end
		cam.CFrame = cam.CFrame * CFrame.new(math.noise(t * 20, 1) * shake, math.noise(t * 20, 2) * shake, 0)
		local _ = dt
	end
	conIn:Disconnect()
	-- entrega para a tela da estrela (ela abre por cima); o mundo volta ao normal por baixo
	pasta:Destroy()
	hrp.Anchored = false
	cam.CameraType = Enum.CameraType.Custom; cam.CameraSubject = hum; cam.FieldOfView = fov0
	destaque:Destroy(); dica:Destroy(); linhas.ImageTransparency = 1; vinheta.ImageTransparency = 1
	for g in pairs(telas) do if g.Parent then g.Enabled = true end end
	TweenService:Create(cc, TweenInfo.new(0.6), { Saturation = 0, Contrast = 0, Brightness = 0, TintColor = Color3.new(1, 1, 1) }):Play()
	TweenService:Create(flash, TweenInfo.new(0.5), { BackgroundTransparency = 1 }):Play()
	task.delay(0.7, function() gui:Destroy(); cc:Destroy() end)
end

-- ponto de entrada para o ExpeditionClient (o Invoke espera a cinematica terminar)
local bf = RS:FindFirstChild('CinematicaInvocacao') or Instance.new('BindableFunction')
bf.Name = 'CinematicaInvocacao'
bf.OnInvoke = function(areaId, results)
	if areaId ~= 3 then return false end
	local melhor, im = nil, 0
	for _, r in ipairs(type(results) == 'table' and results or {}) do
		local i = ORDEM[r.raridade] or 0
		if i > im then melhor, im = r.raridade, i end
	end
	if im < MINIMO then return false end
	local ok, err = pcall(tocar, melhor)
	if not ok then warn('[CinematicaInvocacao]', err) end
	return true
end
bf.Parent = RS

-- teste no Studio: player:SetAttribute('TestarInvocacao', 'mitico') toca a cinematica sem invocar
player:GetAttributeChangedSignal('TestarInvocacao'):Connect(function()
	local r = player:GetAttribute('TestarInvocacao')
	if r then player:SetAttribute('TestarInvocacao', nil); task.spawn(tocar, r) end
end)
