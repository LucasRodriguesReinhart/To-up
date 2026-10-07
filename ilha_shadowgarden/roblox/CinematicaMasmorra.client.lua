-- CinematicaMasmorra (LocalScript, StarterPlayerScripts) - entrada da Masmorra das Sombras como cinematica: o jogador e
-- SUGADO pelo vortice do Salao Sombrio. O servidor (DungeonService.entrar) valida, dispara Remotes.MasmorraCinematica
-- (duracao) e so teleporta no fim; a chegada na sala 1 abre com onda de choque e o titulo da masmorra.
-- Linguagem dos efeitos (referencia do usuario, buraco negro estilo anime): camadas no mundo (nucleo preto, disco de
-- acrecao girando, anel de luz, riscos e destrocos puxados para dentro, rachaduras no chao) + camera (dolly com tremida,
-- corte para close, mergulho com FOV abrindo) + tela (tinta roxa, linhas de velocidade, vinheta, IMPACT FRAME em preto
-- e branco, flash). Tudo so neste cliente e desfeito no fim; ReducedMotion tira tremida e flashes.
local Players = game:GetService('Players')
local RS = game:GetService('ReplicatedStorage')
local RunService = game:GetService('RunService')
local TweenService = game:GetService('TweenService')
local Lighting = game:GetService('Lighting')
local GuiService = game:GetService('GuiService')
local player = Players.LocalPlayer

local V, C = Vector3.new, Color3.fromRGB
local NS, NSK = NumberSequence.new, NumberSequenceKeypoint.new
local TX = {
	ring = 'rbxassetid://123618418899772',
	glow = 'rbxassetid://119690923296259',
	spark = 'rbxassetid://106034798506002',
	debris = 'rbxassetid://134946881676486',      -- 2x2
	smoke = 'rbxassetid://111755528879126',       -- 4x4
	risco = 'rbxassetid://77069445230804',        -- proprias (textures_rbx/gen_vfx.py)
	disco = 'rbxassetid://89137224521485',
	linhas = 'rbxassetid://121853663711721',
	vinheta = 'rbxassetid://104763198580372',
	rachas = 'rbxassetid://112586625195801',
}
-- pre-carrega as texturas (as proprias sao novas: sem isso a primeira cinematica saia sem disco/riscos/redemoinho)
task.spawn(function()
	local lista = {}
	for _, id in pairs(TX) do
		local d = Instance.new('Decal'); d.Texture = id; table.insert(lista, d)
	end
	pcall(function() game:GetService('ContentProvider'):PreloadAsync(lista) end)
end)
local LILAS = C(214, 190, 255)
local VIOLETA = C(150, 104, 255)

local function easeIn(t) return t * t * t end
local function easeOut(t) return 1 - (1 - t) ^ 3 end
local function clamp01(t) return math.clamp(t, 0, 1) end

local function marcador(nome)
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	local ilha = a3 and a3:FindFirstChild('ILHA_SHADOWGARDEN')
	local mk = ilha and ilha:FindFirstChild('GAMEPLAY_MARKERS')
	return mk and mk:FindFirstChild(nome), ilha
end

-- centro/normal/raio do disco do portal (mesma conta do EfeitosShadowGarden: a malha SG_Cave_PortalVortex manda)
local function portalGeo()
	local m, ilha = marcador('DUNGEON_Portal')
	if not m then return nil end
	local f = V(m:GetAttribute('fwd_x') or 0, 0, m:GetAttribute('fwd_z') or 1).Unit
	local r = m:GetAttribute('radius') or 13
	local centro = m.Position + V(0, r - 0.4, 0) - f * 4.4
	local sub = ilha and ilha:FindFirstChild('SUBSOLO')
	local vort = sub and sub:FindFirstChild('SG_Cave_PortalVortex', true)
	if vort and vort:IsA('BasePart') then centro = vort.Position; r = math.max(vort.Size.Y, vort.Size.Z) / 2 end
	return centro, f, r, m.Position.Y
end

local function peca(pai, nome, tam, cf, forma)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf; p.Shape = forma or Enum.PartType.Block
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1
	p.Parent = pai
	return p
end

local function sgui(p, face, brilho)
	local s = Instance.new('SurfaceGui')
	s.Face = face; s.LightInfluence = 0; s.Brightness = brilho
	s.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize; s.CanvasSize = Vector2.new(1024, 1024)
	s.ClipsDescendants = false; s.Parent = p
	return s
end

local function img(pai, tex, escala, cor, transp, z)
	local i = Instance.new('ImageLabel')
	i.BackgroundTransparency = 1; i.Image = tex; i.ImageColor3 = cor; i.ImageTransparency = transp
	i.AnchorPoint = Vector2.new(0.5, 0.5); i.Position = UDim2.fromScale(0.5, 0.5); i.Size = UDim2.fromScale(escala, escala)
	i.ZIndex = z or 1; i.Parent = pai
	return i
end

local function emissor(pai, s)
	local e = Instance.new('ParticleEmitter')
	e.Texture = s.tex; e.Color = s.cor; e.Rate = s.rate or 0
	e.Lifetime = s.vida; e.Speed = s.vel or NumberRange.new(0)
	e.LightEmission = s.luz or 1; e.LightInfluence = 0; e.Brightness = s.brilho or 2
	e.Size = s.tam; e.Transparency = s.transp
	e.Rotation = s.rotacao or NumberRange.new(0, 360); e.RotSpeed = s.rotvel or NumberRange.new(0)
	e.Acceleration = s.acc or V(); e.Drag = s.drag or 0
	e.Orientation = s.orient or Enum.ParticleOrientation.FacingCamera
	e.Squash = s.squash or NS(0)
	e.ZOffset = s.z or 0
	e.EmissionDirection = s.dir or Enum.NormalId.Top
	e.SpreadAngle = s.spread or Vector2.new(0, 0)
	if s.forma then e.Shape = s.forma; e.ShapeStyle = s.estilo or Enum.ParticleEmitterShapeStyle.Volume end
	if s.inout then e.ShapeInOut = s.inout end
	if s.flip then e.FlipbookLayout = s.flip; e.FlipbookMode = Enum.ParticleFlipbookMode.OneShot; e.FlipbookStartRandom = true end
	e.Enabled = s.ligado ~= false
	e.Parent = pai
	return e
end

local tocando = false
local chegou = false     -- o servidor avisa ('chegou') logo depois do teleporte
local function tocar(duracao)
	if tocando then return end
	local centro, f, r, piso = portalGeo()
	local char = player.Character
	local hrp = char and char:FindFirstChild('HumanoidRootPart')
	local hum = char and char:FindFirstChildOfClass('Humanoid')
	if not (centro and hrp and hum) then return end
	tocando = true
	chegou = false
	local reduzido = false
	pcall(function() reduzido = GuiService.ReducedMotionEnabled end)
	local cam = workspace.CurrentCamera
	local fov0 = cam.FieldOfView
	local pos0 = hrp.Position
	local cfJogador0 = hrp.CFrame
	local lado = f:Cross(V(0, 1, 0)).Unit
	local pasta = Instance.new('Folder'); pasta.Name = 'CinematicaMasmorra_Local'; pasta.Parent = workspace
	hrp.Anchored = true

	-- ---------------- MUNDO
	-- nucleo: esfera preta saindo do disco (cresce)
	local nucleo = peca(pasta, 'Nucleo', V(1, 1, 1), CFrame.new(centro + f * 0.5), Enum.PartType.Ball)
	nucleo.Color = C(4, 2, 10); nucleo.Material = Enum.Material.SmoothPlastic; nucleo.Transparency = 0
	-- disco de acrecao + anel de luz (camada propria por cima do portal, os dois lados)
	local cfDisco = CFrame.fromMatrix(centro + f * 0.8, lado, V(0, 1, 0), -f)
	local disco = peca(pasta, 'Disco', V(r * 2, r * 2, 0.05), cfDisco)
	local camDisco = {}
	for _, face in ipairs({ Enum.NormalId.Front, Enum.NormalId.Back }) do
		local s = sgui(disco, face, 1.4)
		local d1 = img(s, TX.disco, 1.0, C(176, 140, 255), 0.25, 1)
		local d2 = img(s, TX.disco, 0.78, LILAS, 0.55, 2)
		local an = img(s, TX.ring, 0.6, C(255, 255, 255), 0.1, 3)
		local hl = img(s, TX.glow, 1.3, C(90, 50, 200), 0.6, 0)
		table.insert(camDisco, { s = s, d1 = d1, d2 = d2, an = an, hl = hl })
	end
	-- riscos sugados: casca esferica em volta do portal, particula alongada na direcao da velocidade
	local casca = peca(pasta, 'Casca', V(48, 48, 48), CFrame.new(centro + f * 6), Enum.PartType.Ball)
	local riscos = emissor(casca, { tex = TX.risco, cor = ColorSequence.new(C(255, 255, 255), LILAS), rate = 0,
		vida = NumberRange.new(0.5, 0.6), vel = NumberRange.new(40, 48), tam = NS({ NSK(0, 1.8), NSK(1, 0.5) }),
		transp = NS({ NSK(0, 1), NSK(0.15, 0), NSK(0.85, 0.1), NSK(1, 1) }), brilho = 3,
		orient = Enum.ParticleOrientation.VelocityParallel, squash = NS(2.4), rotacao = NumberRange.new(90),
		forma = Enum.ParticleEmitterShape.Sphere, estilo = Enum.ParticleEmitterShapeStyle.Surface,
		inout = Enum.ParticleEmitterShapeInOut.Inward })
	-- destrocos do chao puxados (anel no piso em volta do jogador)
	local chao = peca(pasta, 'Chao', V(46, 0.2, 46), CFrame.new(V(pos0.X, piso + 0.4, pos0.Z)))
	local destrocos = emissor(chao, { tex = TX.debris, cor = ColorSequence.new(C(120, 110, 150)), rate = 0,
		vida = NumberRange.new(1.0, 1.4), vel = NumberRange.new(4, 9), tam = NS({ NSK(0, 0.9), NSK(1, 0.4) }),
		transp = NS({ NSK(0, 0), NSK(0.85, 0), NSK(1, 1) }), luz = 0, brilho = 1, rotvel = NumberRange.new(-260, 260),
		acc = (centro - pos0).Unit * 34 + V(0, 10, 0), drag = 0.5, flip = Enum.ParticleFlipbookLayout.Grid2x2,
		forma = Enum.ParticleEmitterShape.Box })
	-- poeira violeta rasteira
	local poeira = emissor(chao, { tex = TX.smoke, cor = ColorSequence.new(C(120, 96, 210)), rate = 0,
		vida = NumberRange.new(0.9, 1.3), vel = NumberRange.new(2, 5), tam = NS({ NSK(0, 3), NSK(1, 8) }),
		transp = NS({ NSK(0, 1), NSK(0.2, 0.55), NSK(1, 1) }), luz = 0.4, brilho = 1,
		acc = (centro - pos0).Unit * 22, flip = Enum.ParticleFlipbookLayout.Grid4x4, forma = Enum.ParticleEmitterShape.Box })
	-- rachaduras se abrindo no chao, do portal para o jogador
	local meio = (V(centro.X, piso, centro.Z) + V(pos0.X, piso, pos0.Z)) / 2
	local rachaPeca = peca(pasta, 'Rachas', V(2, 0.05, 2), CFrame.lookAt(meio + V(0, 0.12, 0), meio + V(0, 0.12, 0) + f))
	local rachaImg = img(sgui(rachaPeca, Enum.NormalId.Top, 1), TX.rachas, 1, C(10, 4, 20), 0.05)
	-- anel de alerta no piso em volta do jogador (como o circulo do ataque na referencia)
	local alerta = peca(pasta, 'Alerta', V(2, 0.05, 2), CFrame.new(V(pos0.X, piso + 0.15, pos0.Z)))
	local alertaImg = img(sgui(alerta, Enum.NormalId.Top, 2), TX.ring, 1, VIOLETA, 0.2)
	-- luz do vortice (so durante a cinematica)
	local luz = Instance.new('PointLight'); luz.Color = VIOLETA; luz.Range = 34; luz.Brightness = 0; luz.Parent = nucleo

	-- ---------------- TELA
	local gui = Instance.new('ScreenGui')
	gui.Name = 'CinematicaMasmorra'; gui.IgnoreGuiInset = true; gui.DisplayOrder = 200; gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild('PlayerGui')
	local function cheia(nome, cor, transp, z)
		local fr = Instance.new('Frame'); fr.Name = nome; fr.BorderSizePixel = 0; fr.BackgroundColor3 = cor
		fr.BackgroundTransparency = transp; fr.Size = UDim2.fromScale(1, 1); fr.ZIndex = z; fr.Parent = gui
		return fr
	end
	local vinheta = Instance.new('ImageLabel'); vinheta.BackgroundTransparency = 1; vinheta.Image = TX.vinheta
	vinheta.Size = UDim2.fromScale(1, 1); vinheta.ImageTransparency = 1; vinheta.ZIndex = 1; vinheta.Parent = gui
	local linhas = Instance.new('ImageLabel'); linhas.BackgroundTransparency = 1; linhas.Image = TX.linhas
	linhas.AnchorPoint = Vector2.new(0.5, 0.5); linhas.Position = UDim2.fromScale(0.5, 0.5)
	linhas.Size = UDim2.fromScale(1.5, 1.5); linhas.SizeConstraint = Enum.SizeConstraint.RelativeXX
	linhas.ImageColor3 = LILAS; linhas.ImageTransparency = 1; linhas.ZIndex = 2; linhas.Parent = gui
	local redemoinho = Instance.new('ImageLabel'); redemoinho.BackgroundTransparency = 1; redemoinho.Image = TX.disco
	redemoinho.AnchorPoint = Vector2.new(0.5, 0.5); redemoinho.Position = UDim2.fromScale(0.5, 0.5)
	redemoinho.SizeConstraint = Enum.SizeConstraint.RelativeYY; redemoinho.Size = UDim2.fromScale(0.3, 0.3)
	redemoinho.ImageColor3 = LILAS; redemoinho.ImageTransparency = 1; redemoinho.ZIndex = 3; redemoinho.Parent = gui
	local flash = cheia('Flash', C(255, 255, 255), 1, 5)
	local preto = cheia('Preto', C(6, 3, 14), 1, 6)
	local cc = Instance.new('ColorCorrectionEffect'); cc.Name = 'CinematicaMasmorraCC'; cc.Parent = Lighting
	local bloom = Instance.new('BloomEffect'); bloom.Name = 'CinematicaMasmorraBloom'; bloom.Intensity = 0
	bloom.Size = 40; bloom.Threshold = 0.9; bloom.Parent = Lighting
	local destaque = Instance.new('Highlight'); destaque.FillColor = C(0, 0, 0); destaque.OutlineColor = C(255, 255, 255)
	destaque.FillTransparency = 1; destaque.OutlineTransparency = 1; destaque.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
	destaque.Adornee = char; destaque.Parent = gui

	-- ---------------- TEMPO
	local T = math.max(1.8, duracao or 2.6)
	local tImpacto = T * 0.48          -- impact frame
	local tMergulho = T * 0.58         -- camera mergulha no vortice
	local tBranco = T * 0.90           -- flash final -> preto
	cam.CameraType = Enum.CameraType.Scriptable
	local camIni = cam.CFrame
	-- plano 1: 3/4 por tras do jogador olhando o portal, empurrando devagar
	local atrasJog = (pos0 - centro) * V(1, 0, 1)
	atrasJog = atrasJog.Magnitude > 0.1 and atrasJog.Unit or -f
	local foco = pos0:Lerp(centro, 0.35)
	local cam1A = CFrame.lookAt(pos0 + atrasJog * 18 + lado * 12 + V(0, 6, 0), foco + V(0, 2, 0))
	local cam1B = CFrame.lookAt(pos0 + atrasJog * 12 + lado * 8 + V(0, 4, 0), foco + V(0, 3, 0))
	-- plano 2 (impacto): close de frente para o jogador com o vortice atras
	local giro = 0
	local t0 = os.clock()
	local teleportado = false
	local con
	-- escala de tempo SO para revisar gravando (atributo CinematicaEscala no jogador; 1 = normal)
	local escala = math.max(1, player:GetAttribute('CinematicaEscala') or 1)
	con = RunService.RenderStepped:Connect(function(dt)
		dt /= escala
		local t = (os.clock() - t0) / escala
		giro += dt
		-- jogador puxado para o centro (comeca devagar, acelera)
		local u = clamp01((t - 0.35) / (tMergulho + 0.5 - 0.35))
		if not teleportado and not chegou and t < tMergulho + 0.25 and hrp.Parent then
			local alvo = pos0:Lerp(centro - f * 2, easeIn(u) * 0.85) + V(0, math.sin(u * math.pi) * 2.5, 0)
			hrp.CFrame = CFrame.lookAt(alvo, alvo + (centro - alvo) * V(1, 0, 1) + f * 0.001) * CFrame.Angles(0, 0, u * u * 0.9)
		end
		-- mundo
		local k = clamp01(t / tImpacto)
		local tamN = 1 + 9 * easeOut(clamp01(t / (T * 0.7)))
		nucleo.Size = V(tamN, tamN, tamN)
		for _, cd in ipairs(camDisco) do
			cd.d1.Rotation = -giro * (120 + 260 * k)
			cd.d2.Rotation = -giro * (210 + 420 * k)
			cd.d1.Size = UDim2.fromScale(1 + 0.6 * k, 1 + 0.6 * k)
			cd.an.ImageTransparency = 0.05 + 0.25 * (0.5 + 0.5 * math.sin(t * 22))
			cd.s.Brightness = 1.4 + 1.3 * k
		end
		disco.Size = V(r * 2 * (1 + 0.45 * k), r * 2 * (1 + 0.45 * k), 0.05)
		luz.Brightness = 3 * k
		riscos.Rate = 40 + 220 * k
		destrocos.Rate = t < tMergulho and 30 + 50 * k or 0
		poeira.Rate = t < tMergulho and 6 + 10 * k or 0
		local rk = easeOut(clamp01(t / (tImpacto * 0.9)))
		local dist = (V(centro.X, 0, centro.Z) - V(pos0.X, 0, pos0.Z)).Magnitude
		rachaPeca.Size = V(dist * 1.4 * rk + 1, 0.05, dist * 1.4 * rk + 1)
		alerta.Size = V(4 + 24 * easeOut(clamp01(t / 0.9)), 0.05, 4 + 24 * easeOut(clamp01(t / 0.9)))
		alertaImg.ImageTransparency = 0.2 + 0.5 * clamp01((t - 0.9) / 0.6)
		-- tela
		vinheta.ImageTransparency = 1 - 0.85 * k
		linhas.ImageTransparency = 1 - 0.75 * clamp01((t - 0.3) / 0.8)
		linhas.Rotation = giro * 12
		linhas.Size = UDim2.fromScale(1.5 - 0.15 * math.sin(t * 30) * k, 1.5 - 0.15 * math.sin(t * 30) * k)
		bloom.Intensity = 0.35 * k
		-- camera
		local shake = reduzido and 0 or (0.08 + 0.5 * k)
		local sx = (math.noise(t * 18, 1) * shake)
		local sy = (math.noise(t * 18, 2) * shake)
		if t < tImpacto then
			cam.CFrame = camIni:Lerp(cam1A, easeOut(clamp01(t / 0.45))):Lerp(cam1B, clamp01((t - 0.45) / (tImpacto - 0.45)))
				* CFrame.new(sx, sy, 0)
			cam.FieldOfView = fov0 + (62 - fov0) * easeOut(k)
			cc.TintColor = C(255, 255, 255):Lerp(C(212, 188, 255), k)
			cc.Contrast = 0.25 * k; cc.Saturation = 0.15 * k; cc.Brightness = 0
		elseif t < tMergulho then
			-- IMPACT FRAME: preto e branco, silhueta preta com contorno branco, corte para o close
			local closeCF = CFrame.lookAt(hrp.Position + f * 9 + lado * 3 + V(0, 2, 0), hrp.Position + V(0, 1, 0))
			cam.CFrame = closeCF * CFrame.new(sx * 2, sy * 2, 0)
			cam.FieldOfView = 50
			if not reduzido then
				cc.Saturation = -1; cc.Contrast = 2.4; cc.Brightness = 0.15; cc.TintColor = C(255, 255, 255)
				destaque.FillTransparency = 0; destaque.OutlineTransparency = 0
				flash.BackgroundTransparency = t - tImpacto < 0.05 and 0 or 1
			end
		else
			-- MERGULHO: a camera voa para o nucleo, o FOV abre, o redemoinho toma a tela
			local m = clamp01((t - tMergulho) / (tBranco - tMergulho))
			destaque.FillTransparency = 1; destaque.OutlineTransparency = 1
			cc.Saturation = 0.25; cc.Contrast = 0.35; cc.Brightness = 0.05 * m; cc.TintColor = C(205, 178, 255)
			local de = hrp.Position + f * 7 + V(0, 3, 0)
			local para = centro + f * 1.5
			cam.CFrame = CFrame.lookAt(de:Lerp(para, easeIn(m)), centro) * CFrame.new(sx * 0.5, sy * 0.5, 0)
			cam.FieldOfView = 55 + 55 * easeIn(m)
			redemoinho.ImageTransparency = 1 - 0.9 * m
			redemoinho.Rotation = -giro * 400
			redemoinho.Size = UDim2.fromScale(0.3 + 2.4 * easeIn(m), 0.3 + 2.4 * easeIn(m))
			linhas.ImageTransparency = 0.1
			if m > 0.55 then
				for _, d in ipairs(char:GetDescendants()) do if d:IsA('BasePart') then d.LocalTransparencyModifier = 1 end end
			end
			if t >= tBranco then
				local w = clamp01((t - tBranco) / (T - tBranco))
				flash.BackgroundTransparency = reduzido and 1 or (1 - w)
				preto.BackgroundTransparency = 1 - clamp01((t - tBranco - 0.08) / 0.12)
			end
		end
		-- chegou o teleporte (o servidor move o personagem para a masmorra)
		if chegou then teleportado = true end
	end)

	-- ---------------- FIM + CHEGADA
	local function limpar()
		if con then con:Disconnect() end
		riscos.Rate = 0; destrocos.Rate = 0
		for _, d in ipairs(char:GetDescendants()) do if d:IsA('BasePart') then d.LocalTransparencyModifier = 0 end end
		pasta:Destroy()
	end
	task.spawn(function()
		local fim = os.clock() + T + 3.5
		fim = os.clock() + (T + 3.5) * escala
		repeat RunService.RenderStepped:Wait() until os.clock() >= t0 + T * escala and (teleportado or os.clock() > fim)
		task.wait(0.15)
		limpar()
		hrp.Anchored = false
		cam.CameraType = Enum.CameraType.Custom
		cam.CameraSubject = hum
		cam.FieldOfView = fov0
		flash.BackgroundTransparency = 1
		linhas.ImageTransparency = 1; redemoinho.ImageTransparency = 1
		-- chegada: sai do preto, onda de choque e faiscas no chao, titulo
		local base = hrp.Position - V(0, 3, 0)
		local pasta2 = Instance.new('Folder'); pasta2.Name = 'CinematicaChegada_Local'; pasta2.Parent = workspace
		local onda = peca(pasta2, 'Onda', V(2, 0.05, 2), CFrame.new(base + V(0, 0.2, 0)))
		local ondaImg = img(sgui(onda, Enum.NormalId.Top, 3), TX.ring, 1, LILAS, 0)
		TweenService:Create(onda, TweenInfo.new(0.9, Enum.EasingStyle.Quart), { Size = V(44, 0.05, 44) }):Play()
		TweenService:Create(ondaImg, TweenInfo.new(0.9, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { ImageTransparency = 1 }):Play()
		local burst = peca(pasta2, 'Burst', V(2, 0.2, 2), CFrame.new(base + V(0, 0.5, 0)))
		local bp = emissor(burst, { tex = TX.spark, cor = ColorSequence.new(C(255, 255, 255), LILAS), vida = NumberRange.new(0.6, 1.1),
			vel = NumberRange.new(16, 30), tam = NS({ NSK(0, 0.7), NSK(1, 0.1) }), transp = NS({ NSK(0, 0), NSK(1, 1) }),
			brilho = 3, drag = 3, spread = Vector2.new(80, 80), ligado = false })
		bp:Emit(40)
		game:GetService('Debris'):AddItem(pasta2, 2.5)
		TweenService:Create(preto, TweenInfo.new(0.7, Enum.EasingStyle.Quad), { BackgroundTransparency = 1 }):Play()
		TweenService:Create(vinheta, TweenInfo.new(1.4), { ImageTransparency = 1 }):Play()
		TweenService:Create(cc, TweenInfo.new(1.2), { Saturation = 0, Contrast = 0, Brightness = 0, TintColor = C(255, 255, 255) }):Play()
		TweenService:Create(bloom, TweenInfo.new(1.2), { Intensity = 0 }):Play()
		local titulo = Instance.new('TextLabel')
		titulo.BackgroundTransparency = 1; titulo.AnchorPoint = Vector2.new(0.5, 0.5); titulo.Position = UDim2.fromScale(0.5, 0.36)
		titulo.Size = UDim2.fromScale(0.8, 0.09); titulo.Text = 'MASMORRA DAS SOMBRAS'; titulo.TextScaled = true
		titulo.Font = Enum.Font.GothamBlack; titulo.TextColor3 = C(236, 226, 255); titulo.TextStrokeColor3 = C(40, 16, 90)
		titulo.TextStrokeTransparency = 0.2; titulo.TextTransparency = 1; titulo.ZIndex = 7; titulo.Parent = gui
		local sub = Instance.new('TextLabel')
		sub.BackgroundTransparency = 1; sub.AnchorPoint = Vector2.new(0.5, 0.5); sub.Position = UDim2.fromScale(0.5, 0.43)
		sub.Size = UDim2.fromScale(0.6, 0.04); sub.TextScaled = true; sub.Font = Enum.Font.GothamBold
		sub.Text = 'Limpe cada sala antes do tempo acabar'; sub.TextColor3 = C(200, 186, 240); sub.TextTransparency = 1
		sub.ZIndex = 7; sub.Parent = gui
		local escala = Instance.new('UIScale'); escala.Scale = 1.25; escala.Parent = titulo
		TweenService:Create(titulo, TweenInfo.new(0.35), { TextTransparency = 0 }):Play()
		TweenService:Create(escala, TweenInfo.new(0.5, Enum.EasingStyle.Back), { Scale = 1 }):Play()
		task.delay(0.25, function() TweenService:Create(sub, TweenInfo.new(0.35), { TextTransparency = 0 }):Play() end)
		task.wait(2.2)
		TweenService:Create(titulo, TweenInfo.new(0.6), { TextTransparency = 1, TextStrokeTransparency = 1 }):Play()
		TweenService:Create(sub, TweenInfo.new(0.6), { TextTransparency = 1 }):Play()
		task.wait(0.7)
		gui:Destroy(); cc:Destroy(); bloom:Destroy()
		tocando = false
	end)
end

task.spawn(function()
	local remotes = RS:WaitForChild('Remotes')
	local ev = remotes:WaitForChild('MasmorraCinematica', 120)
	if ev then
		ev.OnClientEvent:Connect(function(arg)
			if arg == 'chegou' then chegou = true return end
			task.spawn(tocar, arg)
		end)
	end
end)

-- teste no Studio: player:SetAttribute('TestarCinematica', true) dispara sem entrar (nao teleporta)
player:GetAttributeChangedSignal('TestarCinematica'):Connect(function()
	if player:GetAttribute('TestarCinematica') then player:SetAttribute('TestarCinematica', nil); task.spawn(tocar, 2.6) end
end)
