-- EfeitosShadowGarden (LocalScript, StarterPlayerScripts) - efeitos visuais da Ilha 3 (Shadow Garden), so neste cliente.
-- Le os marcadores do export (GAMEPLAY_MARKERS) e monta cada efeito em POUCAS camadas, cada uma com papel claro
-- (nucleo, borda, brilho, particulas, onda), em vez de um emissor com Rate alto. Direcao de arte: o roxo e acento de
-- funcao; brilho aditivo (LightEmission 1, LightInfluence 0) so no que e magia.
--  * INVOCACAO (torre): circulo runico girando no piso onde o jogador fica, motas subindo do circulo, duas fitas de
--    luz em espiral subindo pela torre ate a esfera armilar, halo no nucleo da esfera, nevoa violeta escorrendo da porta
--    pela escada. Ato de invocar (Remotes.InvocacaoFX, de QUALQUER jogador na torre): carga (motas sugadas para o
--    circulo) -> flash + onda de choque no piso + coluna de luz na cor da raridade. Quem invocou ve o fecho quando a
--    tela da estrela fecha (RevealOpen).
--  * PORTAL DO SALAO SOMBRIO (DUNGEON_Portal): nucleo escuro, vortice em 2 velocidades, borda clara, particulas
--    sugadas para dentro, nevoa rasteira saindo pelo chao e a luz L_SGCave_Portal pulsando (sem luz nova: teto de 6
--    luzes da caverna). Mais forte com a masmorra ABERTA (ReplicatedStorage.MasmorraEstado.Estado = ENTRY_OPEN).
--  * PORTAIS DAS SALAS (MasmorraProxima_*, do DungeonService): selado = veu escuro com runas lentas; aberto = vortice
--    + succao. O estado vem da propria peca (CanTouch = aberto).
-- Tudo criado neste cliente (pasta workspace.EfeitosShadowGarden_Local), ligado so na area 3 (ShadowGardenMood ou
-- DungeonRun) e com culling por distancia. Nada aqui colide, consulta ou decide gameplay.
local Players = game:GetService('Players')
local RS = game:GetService('ReplicatedStorage')
local RunService = game:GetService('RunService')
local TweenService = game:GetService('TweenService')
local Debris = game:GetService('Debris')
local player = Players.LocalPlayer

local V, C = Vector3.new, Color3.fromRGB
local NS, NSK = NumberSequence.new, NumberSequenceKeypoint.new
local CSq = ColorSequence.new

-- texturas ja publicadas no jogo (ReplicatedStorage.OreVFX.Textures)
local TX = {
	glow = 'rbxassetid://119690923296259',
	spark = 'rbxassetid://106034798506002',
	diamond = 'rbxassetid://113126543125281',
	ring = 'rbxassetid://123618418899772',
	swirl = 'rbxassetid://124410208940490',
	beam = 'rbxassetid://134235069437330',
	smoke = 'rbxassetid://111755528879126',      -- flipbook 4x4
	runes = 'rbxassetid://84448215429631',       -- 2x2 glifos (512 px: cada glifo 256)
}

-- paleta: luar branco-lavanda + violeta de funcao
local LUAR = C(222, 218, 255)
local VIOLETA = C(150, 112, 255)
local VIOLETA_FUNDO = C(84, 52, 170)

local pasta = Instance.new('Folder')
pasta.Name = 'EfeitosShadowGarden_Local'
pasta.Parent = workspace

-- ------------------------------------------------------------------ utilitarios
local function peca(nome, tam, cf)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1
	p.Parent = pasta
	return p
end

local function superficie(p, face, brilho, px)
	local sg = Instance.new('SurfaceGui')
	sg.Face = face
	sg.LightInfluence = 0
	sg.Brightness = brilho
	sg.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
	sg.CanvasSize = Vector2.new(px or 1024, px or 1024)
	sg.ClipsDescendants = false
	sg.ResetOnSpawn = false
	sg.Parent = p
	return sg
end

local function imagem(pai, tex, escala, cor, transp, z)
	local im = Instance.new('ImageLabel')
	im.BackgroundTransparency = 1
	im.Image = tex
	im.AnchorPoint = Vector2.new(0.5, 0.5)
	im.Position = UDim2.fromScale(0.5, 0.5)
	im.Size = UDim2.fromScale(escala, escala)
	im.ImageColor3 = cor
	im.ImageTransparency = transp
	im.ZIndex = z or 1
	im.Parent = pai
	return im
end

local function transpSeq(t0, meio)
	return NS({ NSK(0, 1), NSK(0.15, t0), NSK(meio or 0.7, math.min(1, t0 + 0.2)), NSK(1, 1) })
end

local function emissor(pai, s)
	local e = Instance.new('ParticleEmitter')
	e.Name = s.nome or 'FX'
	e.Texture = s.tex
	e.Color = s.cor
	e.Rate = s.rate or 0
	e.Lifetime = s.vida
	e.Speed = s.vel or NumberRange.new(0)
	e.SpreadAngle = s.spread or Vector2.new(0, 0)
	e.Acceleration = s.acc or V(0, 0, 0)
	e.Drag = s.drag or 0
	e.LightEmission = s.luz or 1
	e.LightInfluence = s.infl or 0
	e.Brightness = s.brilho or 1.5
	e.Rotation = NumberRange.new(0, 360)
	e.RotSpeed = s.rot or NumberRange.new(-20, 20)
	e.Size = s.tam
	e.Transparency = s.transp
	e.ZOffset = s.z or 0
	e.LockedToPart = s.preso or false
	e.EmissionDirection = s.dir or Enum.NormalId.Top
	if s.forma then e.Shape = s.forma end
	if s.estilo then e.ShapeStyle = s.estilo end
	if s.inout then e.ShapeInOut = s.inout end
	if s.flip then
		e.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4
		e.FlipbookMode = Enum.ParticleFlipbookMode.OneShot
	end
	e.Parent = pai
	return e
end

-- ------------------------------------------------------------------ marcadores (o modelo entra por streaming)
local function ilha()
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	return a3, a3 and a3:FindFirstChild('ILHA_SHADOWGARDEN')
end

local function marcador(nome)
	local _, m = ilha()
	local mk = m and m:FindFirstChild('GAMEPLAY_MARKERS')
	local p = mk and mk:FindFirstChild(nome)
	return p and p:IsA('BasePart') and p or nil
end

local function frente(m)
	local fx, fz = m:GetAttribute('fwd_x'), m:GetAttribute('fwd_z')
	if fx and fz then return V(fx, 0, fz).Unit end
	return V(0, 0, -1)
end

local function luzDaIlha(nome)
	local _, m = ilha()
	local lf = m and m:FindFirstChild('LIGHTS')
	local p = lf and lf:FindFirstChild(nome)
	return p and p:FindFirstChildWhichIsA('Light')
end

local function corRaridade(key)
	-- cores oficiais em Config.Raridades (a UI antiga ExpeditionUI saiu; WaitForChild nela travava 5 s)
	local ok, Config = pcall(require, RS:FindFirstChild('Config'))
	local r = ok and Config and Config.Raridades and Config.Raridades[key]
	if r and typeof(r.cor) == 'Color3' then return r.cor end
	return C(190, 110, 255)
end

-- ------------------------------------------------------------------ efeitos registrados
-- cada efeito: { pos, dist, ligar(bool), passo(dt, t) }
local efeitos = {}
local ativo = false

-- ================================================================== INVOCACAO
local Inv = nil
local function montarInvocacao()
	local main, pp = marcador('SUMMON_Main'), marcador('SUMMON_PlayerPosition')
	if not (main and pp) then return false end
	local fw = frente(main)                     -- a torre olha para o jogador
	local piso = pp.Position.Y
	local centro = V(pp.Position.X, piso, pp.Position.Z)
	-- eixo da torre: corpo de pedra ~1,4 atras do marcador; esfera armilar ~46 acima do piso
	local eixo = V(main.Position.X, piso, main.Position.Z) - fw * 1.4
	local esfera = eixo + V(0, 46.2, 0) - fw * 1.8
	local giro = CFrame.lookAt(centro, centro + fw)

	local I = { pos = centro, dist = 300, emissores = {}, fitas = {} }

	-- 1) circulo runico no piso (14 studs, cobre o anel gravado na plataforma)
	local disco = peca('Inv_Circulo', V(18, 0.05, 18), giro + V(0, 0.08, 0))
	local sg = superficie(disco, Enum.NormalId.Top, 1.4)
	local rotor = Instance.new('Frame')
	rotor.BackgroundTransparency = 1; rotor.AnchorPoint = Vector2.new(0.5, 0.5)
	rotor.Position = UDim2.fromScale(0.5, 0.5); rotor.Size = UDim2.fromScale(1, 1); rotor.Parent = sg
	local anelFora = imagem(sg, TX.ring, 1.0, VIOLETA, 0.5, 1)
	imagem(rotor, TX.ring, 0.64, LUAR, 0.7, 2)
	-- 8 glifos na coroa entre os aneis (quadrantes do 2x2 alternados)
	local glifos = {}
	for i = 0, 7 do
		local a = i / 8 * math.pi * 2
		local g = Instance.new('ImageLabel')
		g.BackgroundTransparency = 1; g.Image = TX.runes
		g.ImageRectSize = Vector2.new(256, 256); g.ImageRectOffset = Vector2.new((i % 2) * 256, (math.floor(i / 2) % 2) * 256)
		g.AnchorPoint = Vector2.new(0.5, 0.5); g.Size = UDim2.fromScale(0.12, 0.12)
		g.Position = UDim2.fromScale(0.5 + math.cos(a) * 0.4, 0.5 + math.sin(a) * 0.4)
		g.Rotation = math.deg(a) + 90; g.ImageColor3 = LUAR; g.ImageTransparency = 0.2; g.ZIndex = 3
		g.Parent = rotor
		table.insert(glifos, g)
	end
	local nucleo = imagem(sg, TX.glow, 0.55, VIOLETA, 0.55, 0)
	I.sg, I.rotor, I.anelFora, I.nucleo, I.glifos = sg, rotor, anelFora, nucleo, glifos

	-- 2) motas subindo do circulo
	local motas = peca('Inv_Motas', V(12, 0.2, 12), CFrame.new(centro + V(0, 0.3, 0)))
	table.insert(I.emissores, emissor(motas, { nome = 'Motas', tex = TX.spark, cor = CSq(LUAR, VIOLETA), rate = 7,
		vida = NumberRange.new(2.6, 3.8), vel = NumberRange.new(1.2, 2.6), acc = V(0, 0.5, 0),
		tam = NS({ NSK(0, 0.15), NSK(0.3, 0.38), NSK(1, 0.05) }), transp = transpSeq(0.15), brilho = 2,
		forma = Enum.ParticleEmitterShape.Box, estilo = Enum.ParticleEmitterShapeStyle.Volume }))

	-- 3) fitas em espiral subindo pela torre ate a esfera (2 fitas em fase oposta)
	local ancora = peca('Inv_Eixo', V(1, 1, 1), CFrame.new(eixo))
	for k = 0, 1 do
		local a0 = Instance.new('Attachment'); a0.Parent = ancora
		local a1 = Instance.new('Attachment'); a1.Parent = ancora
		local tr = Instance.new('Trail')
		tr.Attachment0 = a0; tr.Attachment1 = a1
		tr.Lifetime = 1.0; tr.MinLength = 0.05; tr.FaceCamera = true
		tr.LightEmission = 1; tr.LightInfluence = 0; tr.Brightness = 3
		tr.Color = CSq(LUAR, VIOLETA)
		tr.MaxLength = 0
		tr.Transparency = NS({ NSK(0, 0.1), NSK(0.6, 0.6), NSK(1, 1) })
		tr.WidthScale = NS({ NSK(0, 1), NSK(1, 0.2) })
		tr.Texture = TX.beam; tr.TextureMode = Enum.TextureMode.Stretch
		tr.Parent = ancora
		local brilho = emissor(a0, { nome = 'Rastro', tex = TX.spark, cor = CSq(LUAR), rate = 10,
			vida = NumberRange.new(0.6, 1.1), tam = NS({ NSK(0, 0.35), NSK(1, 0) }), transp = transpSeq(0.1), brilho = 2.5 })
		table.insert(I.emissores, brilho)
		table.insert(I.fitas, { a0 = a0, a1 = a1, tr = tr, fase = k * 0.5 })
	end
	I.eixo, I.esfera = eixo, esfera

	-- 4) halo no nucleo da esfera armilar
	local halo = peca('Inv_Halo', V(1, 1, 1), CFrame.new(esfera))
	table.insert(I.emissores, emissor(halo, { nome = 'Halo', tex = TX.glow, cor = CSq(VIOLETA), rate = 1.2,
		vida = NumberRange.new(2.4, 3), tam = NS({ NSK(0, 12), NSK(1, 18) }), transp = NS({ NSK(0, 1), NSK(0.4, 0.78), NSK(1, 1) }),
		brilho = 1.4, rot = NumberRange.new(-6, 6), z = -2, preso = true }))
	local brilhos = peca('Inv_Cintilas', V(14, 14, 14), CFrame.new(esfera))
	table.insert(I.emissores, emissor(brilhos, { nome = 'Cintilas', tex = TX.diamond, cor = CSq(LUAR), rate = 3,
		vida = NumberRange.new(0.6, 1), tam = NS({ NSK(0, 0), NSK(0.5, 0.7), NSK(1, 0) }), transp = transpSeq(0.1), brilho = 3,
		forma = Enum.ParticleEmitterShape.Sphere, estilo = Enum.ParticleEmitterShapeStyle.Volume }))

	-- 5) nevoa violeta escorrendo da porta pela escada
	local porta = eixo - fw * 6.5 + V(0, 4.6, 0)
	local np = peca('Inv_NevoaPorta', V(5, 0.4, 1.5), CFrame.lookAt(porta, porta - fw))
	table.insert(I.emissores, emissor(np, { nome = 'NevoaPorta', tex = TX.smoke, flip = true, cor = CSq(C(120, 100, 230)),
		rate = 1.6, vida = NumberRange.new(3.5, 5), vel = NumberRange.new(1.4, 2.4), acc = V(0, -0.9, 0), drag = 0.4,
		tam = NS({ NSK(0, 2.5), NSK(1, 6) }), transp = NS({ NSK(0, 1), NSK(0.25, 0.8), NSK(1, 1) }), luz = 0.35, infl = 0.4,
		brilho = 1, rot = NumberRange.new(-10, 10), dir = Enum.NormalId.Back, spread = Vector2.new(20, 10),
		forma = Enum.ParticleEmitterShape.Box, estilo = Enum.ParticleEmitterShapeStyle.Volume }))

	-- 6) partes do ato de invocar (prontas, desligadas)
	local carga = peca('Inv_Carga', V(22, 0.1, 22), CFrame.new(centro + V(0, 0.6, 0)))
	I.carga = emissor(carga, { nome = 'Carga', tex = TX.spark, cor = CSq(LUAR), rate = 0, vida = NumberRange.new(0.75, 0.85),
		vel = NumberRange.new(13, 14), tam = NS({ NSK(0, 0.6), NSK(1, 0.2) }), transp = NS({ NSK(0, 0.6), NSK(0.3, 0), NSK(1, 0.4) }),
		brilho = 3, forma = Enum.ParticleEmitterShape.Disc, estilo = Enum.ParticleEmitterShapeStyle.Surface,
		inout = Enum.ParticleEmitterShapeInOut.Inward })
	local estouro = peca('Inv_Estouro', V(2, 0.2, 2), CFrame.new(centro + V(0, 0.5, 0)))
	I.estouro = emissor(estouro, { nome = 'Estouro', tex = TX.spark, cor = CSq(LUAR), rate = 0, vida = NumberRange.new(0.8, 1.4),
		vel = NumberRange.new(18, 34), drag = 3.5, spread = Vector2.new(70, 70), acc = V(0, -4, 0),
		tam = NS({ NSK(0, 0.9), NSK(1, 0.1) }), transp = transpSeq(0, 0.6), brilho = 3.5 })
	I.onda = peca('Inv_Onda', V(2, 0.05, 2), CFrame.new(centro + V(0, 0.15, 0)))
	I.ondaImg = imagem(superficie(I.onda, Enum.NormalId.Top, 3, 512), TX.ring, 1, LUAR, 1)
	I.flash = Instance.new('PointLight'); I.flash.Range = 40; I.flash.Brightness = 0; I.flash.Shadows = false
	I.flash.Parent = estouro

	local gachas = workspace:FindFirstChild('Gachas')
	local maquina = gachas and gachas:FindFirstChild('Gacha_sombra')
	I.pad = maquina and maquina:FindFirstChild('PadGacha')
	I.disco, I.centro = disco, centro
	I.ligado = true
	Inv = I
	return true
end

local function invocacaoPasso(I, dt, t)
	I.giro = (I.giro or 0) + dt * (I.velGiro or 7)
	I.rotor.Rotation = I.giro
	local pulso = 0.5 + 0.5 * math.sin(t * 1.6)
	I.nucleo.ImageTransparency = 0.62 - 0.12 * pulso
	-- fitas: helice que sobe 38 studs em 5,2 s fechando o raio de 16 para 9 junto a esfera
	for _, f in ipairs(I.fitas) do
		local u = (t / 5.2 + f.fase) % 1
		if u < (f.uAnt or 0) then f.tr.Enabled = false; f.tr:Clear(); f.pausa = 2 end
		f.uAnt = u
		local ang = f.fase * math.pi * 2 + u * math.pi * 2.4
		local raio = 15 - 5 * u
		local h = 18 + 26 * u
		local p = V(math.cos(ang) * raio, h, math.sin(ang) * raio)
		f.a0.Position = p
		f.a1.Position = p + V(0, 1.1 * (1 - u) + 0.3, 0)
		if (f.pausa or 0) > 0 then
			f.pausa -= 1
			if f.pausa == 0 then f.tr.Enabled = true end
		end
		local larg = math.sin(u * math.pi)
		f.tr.Transparency = NS({ NSK(0, 1 - 0.9 * larg), NSK(0.6, 1 - 0.45 * larg), NSK(1, 1) })
	end
end

local function invocacaoLigar(I, on)
	I.sg.Enabled = on
	for _, e in ipairs(I.emissores) do e.Enabled = on end
	for _, f in ipairs(I.fitas) do f.tr.Enabled = on; f.tr:Clear() end
	if I.pad and I.pad.Parent then I.pad.LocalTransparencyModifier = on and 1 or 0 end
end

-- ato de invocar: carga -> flash + onda + coluna na cor da raridade (cor clareada para ler no escuro)
local function invocacaoAto(I, cor, comCarga)
	cor = cor:Lerp(Color3.new(1, 1, 1), 0.25)
	task.spawn(function()
		if comCarga then
			I.carga.Color = CSq(LUAR, cor)
			I.carga:Emit(26)
			I.velGiro = 60
			TweenService:Create(I.sg, TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Brightness = 4.5 }):Play()
			task.wait(0.75)
		end
		-- flash
		I.flash.Color = cor
		I.flash.Brightness = 7
		TweenService:Create(I.flash, TweenInfo.new(0.9, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Brightness = 0 }):Play()
		I.estouro.Color = CSq(Color3.new(1, 1, 1), cor)
		I.estouro:Emit(36)
		-- onda de choque no piso (2 -> 46 studs)
		I.onda.Size = V(2, 0.05, 2)
		I.ondaImg.ImageColor3 = cor; I.ondaImg.ImageTransparency = 0
		TweenService:Create(I.onda, TweenInfo.new(0.85, Enum.EasingStyle.Quart, Enum.EasingDirection.Out), { Size = V(46, 0.05, 46) }):Play()
		TweenService:Create(I.ondaImg, TweenInfo.new(0.85, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { ImageTransparency = 1 }):Play()
		-- coluna de luz: feixe vertical do circulo ate acima da esfera, abre e some
		local base = peca('Inv_Coluna', V(1, 1, 1), CFrame.new(I.centro))
		local a0 = Instance.new('Attachment'); a0.Parent = base
		local a1 = Instance.new('Attachment'); a1.Position = V(0, 70, 0); a1.Parent = base
		local b = Instance.new('Beam')
		b.Attachment0 = a0; b.Attachment1 = a1; b.FaceCamera = true
		b.Texture = TX.beam; b.TextureMode = Enum.TextureMode.Stretch; b.TextureSpeed = 2.5
		b.LightEmission = 1; b.LightInfluence = 0; b.Brightness = 4; b.Segments = 1
		b.Color = CSq(Color3.new(1, 1, 1), cor)
		b.Width0, b.Width1 = 1, 1
		b.Transparency = NS({ NSK(0, 0), NSK(0.75, 0.3), NSK(1, 1) })
		b.Parent = base
		Debris:AddItem(base, 1.6)
		local t0 = os.clock()
		while base.Parent and os.clock() - t0 < 1.4 do
			local k = (os.clock() - t0) / 1.4
			local w = 9 * math.sin(math.min(1, k * 3) * math.pi / 2) * (1 - k)
			b.Width0, b.Width1 = w, w * 0.6
			b.Transparency = NS({ NSK(0, k), NSK(0.75, 0.3 + 0.7 * k), NSK(1, 1) })
			RunService.RenderStepped:Wait()
		end
		I.velGiro = 7
		TweenService:Create(I.sg, TweenInfo.new(1.2), { Brightness = 1.4 }):Play()
	end)
end

-- ================================================================== PORTAL DO SALAO SOMBRIO
local function camadasVortice(sg, escala)
	local n = imagem(sg, TX.glow, 0.95 * escala, Color3.new(0, 0, 0), 0.05, 1)            -- fundo escuro do disco
	local s1 = imagem(sg, TX.swirl, 1.0 * escala, VIOLETA, 0.3, 2)                         -- vortice lento
	local s2 = imagem(sg, TX.swirl, 0.72 * escala, LUAR, 0.62, 3)                          -- vortice rapido
	local cen = imagem(sg, TX.glow, 0.62 * escala, Color3.new(0, 0, 0), 0.1, 4)            -- olho escuro (por cima)
	local borda = imagem(sg, TX.ring, 1.04 * escala, LUAR, 0.25, 5)                        -- borda clara e nitida
	return { nucleo = n, s1 = s1, s2 = s2, centro = cen, borda = borda }
end

local Portal = nil
local function montarPortal()
	local m = marcador('DUNGEON_Portal') or marcador('DUNGEON_Hall')
	if not m then return false end
	local f = frente(m)
	local r = m:GetAttribute('radius') or 13
	-- disco do vortice: medido na malha (SG_Cave_PortalVortex) = 4,4 atras do marcador, centro a r - 0,4 do piso
	local centro = m.Position + V(0, r - 0.4, 0) - f * 4.4
	local _, ilhaM = ilha()
	local vort = ilhaM and ilhaM:FindFirstChild('SUBSOLO') and ilhaM.SUBSOLO:FindFirstChild('SG_Cave_PortalVortex', true)
	if vort and vort:IsA('BasePart') then centro = vort.Position; r = math.max(vort.Size.Y, vort.Size.Z) / 2 end
	local P = { pos = centro, dist = 170, emissores = {}, caverna = true }
	-- o disco olha para quem chega (frente do marcador); UpVector = frente para o Disc das particulas
	local cfDisco = CFrame.fromMatrix(centro + f * 0.5, f:Cross(V(0, 1, 0)).Unit, f)
	local disco = peca('Portal_Disco', V(r * 2, 0.05, r * 2), cfDisco)
	P.sg = superficie(disco, Enum.NormalId.Top, 2.2)
	P.cam = camadasVortice(P.sg, 1)
	-- particulas sugadas: nascem na borda e correm para o centro
	P.succao = emissor(disco, { nome = 'Succao', tex = TX.spark, cor = CSq(LUAR, VIOLETA), rate = 14,
		vida = NumberRange.new(0.95, 1.05), vel = NumberRange.new(r * 0.9, r * 0.95), tam = NS({ NSK(0, 0.55), NSK(1, 0.08) }),
		transp = NS({ NSK(0, 1), NSK(0.15, 0.1), NSK(0.85, 0.2), NSK(1, 1) }), brilho = 2.5,
		forma = Enum.ParticleEmitterShape.Disc, estilo = Enum.ParticleEmitterShapeStyle.Surface,
		inout = Enum.ParticleEmitterShapeInOut.Inward, z = 1 })
	table.insert(P.emissores, P.succao)
	-- nevoa rasteira saindo do portal pelo chao do salao
	local chao = V(centro.X, m.Position.Y + 0.6, centro.Z) + f * 3
	local nv = peca('Portal_Nevoa', V(r * 1.6, 0.5, 3), CFrame.lookAt(chao, chao + f))
	table.insert(P.emissores, emissor(nv, { nome = 'Nevoa', tex = TX.smoke, flip = true, cor = CSq(C(140, 122, 238)),
		rate = 3.5, vida = NumberRange.new(4.5, 6.5), vel = NumberRange.new(1.2, 2.6), drag = 0.25, acc = V(0, -0.05, 0),
		tam = NS({ NSK(0, 4), NSK(1, 10) }), transp = NS({ NSK(0, 1), NSK(0.25, 0.68), NSK(1, 1) }), luz = 0.5, infl = 0.2,
		brilho = 1, rot = NumberRange.new(-8, 8), dir = Enum.NormalId.Front, spread = Vector2.new(25, 4), z = -1,
		forma = Enum.ParticleEmitterShape.Box, estilo = Enum.ParticleEmitterShapeStyle.Volume }))
	P.malha = {}
	if ilhaM then
		for _, d in ipairs(ilhaM:GetDescendants()) do
			if d:IsA('BasePart') and d.Material == Enum.Material.Neon and string.find(d.Name, 'SG_Cave_PortalVortex', 1, true) then
				P.malha[d] = d.Color
			end
		end
	end
	P.luz = luzDaIlha('L_SGCave_Portal')
	P.luz0 = P.luz and P.luz.Brightness or 1.5
	P.alcance0 = P.luz and P.luz.Range or 20
	Portal = P
	return true
end

local function aberta()
	local e = RS:FindFirstChild('MasmorraEstado')
	local s = e and e:GetAttribute('Estado')
	return s == 'ENTRY_OPEN'
end

local function vorticePasso(cam, sg, dt, t, forca, base)
	cam.s1.Rotation = (cam.s1.Rotation - dt * (18 + 14 * forca)) % 360
	cam.s2.Rotation = (cam.s2.Rotation - dt * (48 + 40 * forca)) % 360
	local p = 0.5 + 0.5 * math.sin(t * (1.4 + forca))
	cam.borda.ImageTransparency = 0.32 - 0.22 * p * (0.5 + forca * 0.5)
	cam.centro.ImageTransparency = 0.1 + 0.15 * p * (1 - forca * 0.5)
	sg.Brightness = base + 1.2 * forca + 0.3 * p
end

local function portalPasso(P, dt, t)
	local alvo = aberta() and 1 or 0
	P.forca = (P.forca or 0) + (alvo - (P.forca or 0)) * math.min(1, dt * 1.5)
	vorticePasso(P.cam, P.sg, dt, t, P.forca, 1.8)
	P.succao.Rate = 9 + 16 * P.forca
	if P.luz and P.luz.Parent then
		P.luz.Brightness = P.luz0 * (0.85 + 0.25 * math.sin(t * 1.4) + 0.5 * P.forca)
	end
end

local function portalLigar(P, on)
	P.sg.Enabled = on
	for _, e in ipairs(P.emissores) do e.Enabled = on end
	for d, cor in pairs(P.malha) do if d.Parent then d.Color = on and VIOLETA_FUNDO:Lerp(Color3.new(0, 0, 0), 0.35) or cor end end
	-- o export da Range 60 a esta luz (camada do salao): com ela o portal lavava a caverna inteira de lilas; perto do
	-- portal ela fica curta (banha a moldura e o piso da frente) e o resto do salao volta ao escuro
	if P.luz and P.luz.Parent then
		P.luz.Range = on and math.min(P.alcance0, 26) or P.alcance0
		if not on then P.luz.Brightness = P.luz0 end
	end
end

-- ================================================================== PORTAIS DAS SALAS (MasmorraProxima_*)
local salas = {}          -- [part] = efeito
local COR_ABERTO = C(66, 40, 140)
local function montarSala(sp)
	if salas[sp] then return end
	local w, h = sp.Size.X, sp.Size.Y
	local lado = math.min(w, h)
	local S = { pos = sp.Position, dist = 150, emissores = {}, caverna = true, peca = sp, sgs = {}, cams = {} }
	for _, face in ipairs({ Enum.NormalId.Front, Enum.NormalId.Back }) do
		local sg = superficie(sp, face, 2, 1024)
		sg.CanvasSize = Vector2.new(1024 * w / lado, 1024 * h / lado)
		local quadro = Instance.new('Frame')
		quadro.BackgroundTransparency = 1; quadro.AnchorPoint = Vector2.new(0.5, 0.5)
		quadro.Position = UDim2.fromScale(0.5, 0.5); quadro.SizeConstraint = Enum.SizeConstraint.RelativeYY
		quadro.Size = UDim2.fromScale(1, 1); quadro.Parent = sg
		local cam = camadasVortice(quadro, 0.98)
		-- veu do selo: anel de runas lento por cima (so visivel fechado)
		local veu = Instance.new('Frame')
		veu.BackgroundTransparency = 1; veu.AnchorPoint = Vector2.new(0.5, 0.5); veu.Position = UDim2.fromScale(0.5, 0.5)
		veu.Size = UDim2.fromScale(0.8, 0.8); veu.ZIndex = 6; veu.Parent = quadro
		for i = 0, 5 do
			local a = i / 6 * math.pi * 2
			local g = Instance.new('ImageLabel')
			g.BackgroundTransparency = 1; g.Image = TX.runes
			g.ImageRectSize = Vector2.new(256, 256); g.ImageRectOffset = Vector2.new((i % 2) * 256, (math.floor(i / 2) % 2) * 256)
			g.AnchorPoint = Vector2.new(0.5, 0.5); g.Size = UDim2.fromScale(0.2, 0.2)
			g.Position = UDim2.fromScale(0.5 + math.cos(a) * 0.4, 0.5 + math.sin(a) * 0.4)
			g.ImageColor3 = VIOLETA; g.ImageTransparency = 0.35; g.ZIndex = 6; g.Parent = veu
		end
		cam.veu = veu
		table.insert(S.sgs, sg); table.insert(S.cams, cam)
	end
	-- succao (so aberto): disco proprio no plano do portal
	local f = sp.CFrame.LookVector
	local cf = CFrame.fromMatrix(sp.Position, sp.CFrame.RightVector, f)
	local d = peca('Sala_Succao_' .. sp.Name, V(lado * 0.95, 0.05, lado * 0.95), cf)
	S.succao = emissor(d, { nome = 'Succao', tex = TX.spark, cor = CSq(LUAR, VIOLETA), rate = 18,
		vida = NumberRange.new(0.95, 1.05), vel = NumberRange.new(lado * 0.45, lado * 0.47), tam = NS({ NSK(0, 0.5), NSK(1, 0.08) }),
		transp = NS({ NSK(0, 1), NSK(0.15, 0.1), NSK(0.85, 0.2), NSK(1, 1) }), brilho = 2.5,
		forma = Enum.ParticleEmitterShape.Disc, estilo = Enum.ParticleEmitterShapeStyle.Surface,
		inout = Enum.ParticleEmitterShapeInOut.Inward })
	S.discoSuccao = d
	sp.Destroying:Once(function() salas[sp] = nil; d:Destroy() end)
	salas[sp] = S
end

local function salaPasso(S, dt, t)
	local sp = S.peca
	local abre = sp.CanTouch
	S.forca = (S.forca or 0) + ((abre and 1 or 0) - (S.forca or 0)) * math.min(1, dt * 2.5)
	-- aberto: o servidor acende a placa em lilas claro (neon que o bloom estoura em branco e engole o vortice); neste
	-- cliente ela vira violeta fundo e o vortice/borda fazem a leitura. Fechado: a cor do servidor (veu escuro) fica.
	if abre and sp.Color ~= COR_ABERTO then sp.Color = COR_ABERTO end
	for i, cam in ipairs(S.cams) do
		vorticePasso(cam, S.sgs[i], dt, t, S.forca, 1.2)
		cam.borda.ImageTransparency = 0.7 + (cam.borda.ImageTransparency - 0.7) * S.forca
		cam.s1.ImageTransparency = 0.3 + 0.6 * (1 - S.forca)
		cam.s2.ImageTransparency = 0.55 + 0.45 * (1 - S.forca)
		cam.veu.Rotation = (cam.veu.Rotation + dt * 8) % 360
		for _, g in ipairs(cam.veu:GetChildren()) do g.ImageTransparency = 0.35 + 0.65 * S.forca end
	end
	S.succao.Enabled = S.forca > 0.5
end

local function salaLigar(S, on)
	for _, sg in ipairs(S.sgs) do sg.Enabled = on end
	if not on then S.succao.Enabled = false end
end

-- ================================================================== PORTAO DEMON SLAYER (harmonizar com o bloom)
-- o painel neon da barreira (asset aprovado) estourava em branco com o bloom da noite e escondia o desenho e o preco:
-- neste cliente as pecas Neon do portao ficam a metade da cor (o vermelho le como vermelho). Pecas que chegam depois
-- pela tag PortaoCompra tambem.
local CS = game:GetService('CollectionService')
local tomPortao = {}
local function tonarPortao(d)
	if tomPortao[d] or not d:IsA('BasePart') or d.Material ~= Enum.Material.Neon then return end
	local areas = workspace:FindFirstChild('Areas')
	local a3 = areas and areas:FindFirstChild('Area3')
	if not (a3 and d:IsDescendantOf(a3)) then return end
	local c = d.Color
	tomPortao[d] = true
	d.Color = Color3.new(c.R * 0.5, c.G * 0.5, c.B * 0.5)
end
for _, d in ipairs(CS:GetTagged('PortaoCompra')) do tonarPortao(d) end
CS:GetInstanceAddedSignal('PortaoCompra'):Connect(tonarPortao)

-- ------------------------------------------------------------------ registro e laco
local function registrarSala(d)
	if d:IsA('BasePart') and string.match(d.Name, '^MasmorraProxima_') then montarSala(d) end
end

local tentouSalas = false
local function garantir()
	if not Inv then montarInvocacao() end
	if not Portal then montarPortal() end
	local a3 = ilha()
	if a3 and not tentouSalas then
		tentouSalas = true
		for _, d in ipairs(a3:GetDescendants()) do registrarSala(d) end
		a3.DescendantAdded:Connect(registrarSala)
	end
end

local function noSubsolo()
	if player:GetAttribute('DungeonRun') then return true end
	local ch = player.Character
	local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
	return hrp ~= nil and hrp.Position.Y < 25
end

local function estado()
	return player:GetAttribute('ShadowGardenMood') == true or player:GetAttribute('DungeonRun') ~= nil
end

local ligados = {}         -- [efeito] = bool
local function ajustar(fx, on, ligar)
	if ligados[fx] ~= on then ligados[fx] = on; ligar(fx, on) end
end

task.spawn(function()
	while true do
		ativo = estado()
		if ativo then garantir() end
		task.wait(1)
	end
end)

RunService.RenderStepped:Connect(function(dt)
	local cam = workspace.CurrentCamera
	if not cam then return end
	local c = cam.CFrame.Position
	local t = os.clock()
	local sub = ativo and noSubsolo()
	if Inv then
		local on = ativo and not sub and (Inv.pos - c).Magnitude < Inv.dist
		ajustar(Inv, on, invocacaoLigar)
		if on then invocacaoPasso(Inv, dt, t) end
	end
	if Portal then
		local on = ativo and (Portal.pos - c).Magnitude < Portal.dist and (sub or (Portal.pos - c).Magnitude < 60)
		ajustar(Portal, on, portalLigar)
		if on then portalPasso(Portal, dt, t) end
	end
	for _, S in pairs(salas) do
		local on = ativo and sub and (S.pos - c).Magnitude < S.dist
		ajustar(S, on, salaLigar)
		if on then salaPasso(S, dt, t) end
	end
end)

-- ato de invocar: o servidor avisa todos (Remotes.InvocacaoFX: areaId, userId, raridade da melhor unidade)
task.spawn(function()
	local remotes = RS:WaitForChild('Remotes')
	local ev = remotes:WaitForChild('InvocacaoFX', 60)
	if not ev then return end
	ev.OnClientEvent:Connect(function(areaId, userId, raridade)
		if areaId ~= 3 or not ativo then return end
		garantir()
		local I = Inv
		if not I then return end
		local cor = corRaridade(raridade)
		if userId == player.UserId then
			-- quem invocou esta com a tela da estrela aberta: o fecho aparece quando ela fecha
			task.spawn(function()
				local t0 = os.clock()
				repeat task.wait(0.1) until player:GetAttribute('RevealOpen') ~= true or os.clock() - t0 > 20
				-- mitico/secreto ja tiveram a cinematica completa (CinematicaInvocacao): sem repetir a coluna
				local cin = player:GetAttribute('CinematicaInvocacaoEm')
				if cin and os.clock() - cin < 30 then return end
				invocacaoAto(I, cor, false)
			end)
		elseif (I.pos - workspace.CurrentCamera.CFrame.Position).Magnitude < I.dist then
			invocacaoAto(I, cor, true)
		end
	end)
end)
