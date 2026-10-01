-- PortoesDeIlha: adapta as ilhas MODELADAS (Konoha e Vale Capsule) ao mundo continuo.
-- Cada ilha ganha entrada e saida fisicas no PROPRIO estilo, alinhadas a passarela
-- central (|x|<9), sem reformular o resto do modelo:
--  * Konoha: portico de madeira nas duas bocas do arco sob o Monte Hokage + lanternas no tunel.
--  * Vale Capsule: escadaria de acesso a pista de pouso (a colisao original da pista
--    e restaurada, o TravessiaCorredores a tinha apagado) e desfiladeiro aberto na
--    montanha norte com portal Capsule para a proxima ilha.
-- Pecas invisiveis de colisao levam o atributo TravessiaKeep (o TravessiaCorredores pula).
local SS=game:GetService('ServerStorage')
local M={}
local V=Vector3.new local C=Color3.fromRGB local rad=math.rad

local function part(props,parent,keep)
	local cls=props.Shape=='Wedge' and 'WedgePart' or 'Part'
	local p=Instance.new(cls)
	if props.Shape and cls=='Part' then p.Shape=props.Shape end
	props.Shape=nil
	p.Anchored=true p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth
	p.CanCollide=false p.CanQuery=false p.CanTouch=false p.CastShadow=false
	for k,v in props do p[k]=v end
	if p.CanCollide then p.CanQuery=true end
	if keep then p:SetAttribute('TravessiaKeep',true) end
	p.Parent=parent
	return p
end

local function texto(p,words,cor,tam)
	for _,face in {Enum.NormalId.Front,Enum.NormalId.Back} do
		local g=Instance.new('SurfaceGui') g.Face=face g.Adornee=p g.LightInfluence=.3 g.MaxDistance=360
		g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.PixelsPerStud=tam or 26 g.Parent=p
		local t=Instance.new('TextLabel') t.Size=UDim2.fromScale(.94,.8) t.Position=UDim2.fromScale(.03,.1)
		t.BackgroundTransparency=1 t.Text=words t.TextScaled=true t.Font=Enum.Font.GothamBlack
		t.TextColor3=cor or C(255,255,255) t.TextStrokeTransparency=.75 t.Parent=g
	end
end

local function luz(p,cor,range,brilho)
	local l=Instance.new('PointLight') l.Color=cor l.Range=range or 14 l.Brightness=brilho or .9 l.Shadows=false l.Parent=p
end

local function clonarKit(nome,cf,escala,parent)
	local kit=SS:FindFirstChild('DragonBallKit')
	local tpl=kit and kit:FindFirstChild(nome)
	if not tpl then return nil end
	local c=tpl:Clone()
	if escala and math.abs(escala-1)>.01 then c:ScaleTo(escala) end
	c:PivotTo(cf)
	c.Parent=parent
	return c
end

-- ------------------------------------------------------------------ KONOHA
local WOOD,WOOD_D,ROOF,GOLD=C(140,96,60),C(84,58,42),C(190,78,50),C(222,176,72)

local function porticoKonoha(pai,z,comTelhado,letreiro)
	for _,s in {-1,1} do
		part({Name='PostePortico',Size=V(3,26,3),Position=V(s*11,19,z),Color=WOOD_D,Material=Enum.Material.Wood,CanCollide=true},pai)
		part({Name='BasePoste',Size=V(4,2,4),Position=V(s*11,7,z),Color=C(138,134,128),Material=Enum.Material.Slate,CanCollide=true},pai)
	end
	part({Name='Verga',Size=V(27,2.4,3.4),Position=V(0,31,z),Color=WOOD,Material=Enum.Material.Wood},pai)
	part({Name='VergaAlta',Size=V(30,2,3.8),Position=V(0,34.2,z),Color=WOOD_D,Material=Enum.Material.Wood},pai)
	if comTelhado then
		for _,s in {-1,1} do
			part({Name='Telhado',Size=V(32,1.2,5.4),CFrame=CFrame.new(0,36.8,z+s*2.4)*CFrame.Angles(s*rad(-18),0,0),Color=ROOF,Material=Enum.Material.SmoothPlastic},pai)
		end
		part({Name='Cumeeira',Size=V(32,1,1.6),Position=V(0,38.1,z),Color=WOOD_D,Material=Enum.Material.Wood},pai)
	end
	local placa=part({Name='PlacaPortico',Size=V(12,2.6,.6),Position=V(0,31.1,z),Color=C(58,52,50),Material=Enum.Material.Wood},pai)
	texto(placa,letreiro,C(250,238,206))
	for _,s in {-1,1} do
		local lant=part({Name='LanternaPortico',Shape=Enum.PartType.Ball,Size=V(2.2,2.2,2.2),Position=V(s*8,27.6,z),Color=C(226,70,50),Material=Enum.Material.Neon},pai)
		part({Name='FioLanterna',Size=V(.2,2.4,.2),Position=V(s*8,29.4,z),Color=WOOD_D,Material=Enum.Material.Wood},pai)
		luz(lant,C(255,170,110),13,.8)
	end
end

function M.konoha(model,base)
	local pai=Instance.new('Model') pai.Name='PortaoNorte' pai.Parent=model
	local zc=base.Z
	-- piso de pedra do tunel: a passarela tem 18 de largura, os porticos e lanternas
	-- ficam a x +-11..12, entao o corredor sob o monte ganha um piso proprio mais largo
	part({Name='PisoTunel',Size=V(28,1,96),Position=V(0,5.55,zc+158),Color=C(196,188,166),Material=Enum.Material.Slate,CanCollide=true},pai)
	part({Name='FiladaPiso',Size=V(28.4,.5,97),Position=V(0,5.2,zc+158),Color=C(160,150,130),Material=Enum.Material.Slate,CanCollide=true},pai)
	-- bocas do arco sob o Monte Hokage (frente ~ +118 local, fundo ~ +196 local)
	porticoKonoha(pai,zc+114,true,'VILA DA FOLHA')
	porticoKonoha(pai,zc+198,false,'PROXIMA ILHA')
	-- lanternas de pedra dentro do tunel
	for _,z in {zc+140,zc+168} do
		for _,s in {-1,1} do
			part({Name='PilarLanterna',Size=V(1.4,4.5,1.4),Position=V(s*12,8.4,z),Color=C(138,134,128),Material=Enum.Material.Slate,CanCollide=true},pai)
			local g=part({Name='LuzTunel',Size=V(1.6,1.2,1.6),Position=V(s*12,11.2,z),Color=C(255,196,110),Material=Enum.Material.Neon},pai)
			part({Name='ChapeuLanterna',Size=V(2.2,.6,2.2),Position=V(s*12,12.1,z),Color=C(96,94,96),Material=Enum.Material.Slate},pai)
			luz(g,C(255,196,110),16,.85)
		end
	end
	return pai
end

-- ------------------------------------------------------------------ VALE CAPSULE
local BRANCO,AZUL,CINZA,NAVY,KI=C(248,248,244),C(58,128,222),C(170,178,190),C(36,46,84),C(96,232,255)

local function arcoCapsule(pai,z,vao,alto,letreiro)
	for _,s in {-1,1} do
		part({Name='PilarArco',Size=V(2.8,alto,2.8),Position=V(s*vao/2,6+alto/2,z),Color=BRANCO,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
		part({Name='FaixaPilar',Size=V(3,1.6,3),Position=V(s*vao/2,6+alto*.35,z),Color=AZUL,Material=Enum.Material.SmoothPlastic},pai)
		part({Name='PilarBase',Size=V(4,1.4,4),Position=V(s*vao/2,6.7,z),Color=CINZA,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
	end
	local y=6+alto+1.2
	part({Name='Lintel',Shape=Enum.PartType.Cylinder,Size=V(vao+4,2.6,2.6),CFrame=CFrame.new(0,y,z),Color=BRANCO,Material=Enum.Material.SmoothPlastic},pai)
	for _,s in {-1,1} do
		part({Name='LintelPonta',Shape=Enum.PartType.Ball,Size=V(2.6,2.6,2.6),Position=V(s*(vao+4)/2,y,z),Color=BRANCO,Material=Enum.Material.SmoothPlastic},pai)
	end
	part({Name='LintelLuz',Size=V(vao-2,.35,.35),Position=V(0,y-1.5,z),Color=KI,Material=Enum.Material.Neon},pai)
	local placa=part({Name='PlacaArco',Size=V(15,3,.7),Position=V(0,y+2.6,z),Color=NAVY,Material=Enum.Material.SmoothPlastic},pai)
	texto(placa,letreiro,C(150,236,255))
end

function M.capsule(model,base)
	local pai=Instance.new('Model') pai.Name='AcessosIlha' pai.Parent=model
	local zc=base.Z
	-- ===== ENTRADA SUL: escadaria da passarela ate o topo da pista de pouso =====
	-- colisao original da pista/rampa (o TravessiaCorredores apagou as invisiveis da faixa)
	part({Name='ColisaoPista',Shape=Enum.PartType.Cylinder,Size=V(8,40,40),CFrame=CFrame.new(0,10,zc-180)*CFrame.Angles(0,0,rad(90)),Transparency=1,CanCollide=true},pai,true)
	local rampaN=Instance.new('WedgePart')
	rampaN.Name='ColisaoRampaNorte' rampaN.Anchored=true rampaN.Transparency=1 rampaN.CanCollide=true rampaN.CanTouch=false
	rampaN.Size=V(18,8,20) rampaN.CFrame=CFrame.new(0,10,zc-150)*CFrame.Angles(0,rad(180),0)
	rampaN:SetAttribute('TravessiaKeep',true) rampaN.Parent=pai
	-- escadaria sul (visivel): sobe da passarela (y~6) ao topo da pista (y 14)
	local esc=Instance.new('WedgePart')
	esc.Name='EscadariaSul' esc.Anchored=true esc.CanCollide=true esc.CanQuery=true esc.CanTouch=false
	esc.Size=V(18,7.8,19) esc.CFrame=CFrame.new(0,9.9,zc-196.5)
	esc.Color=CINZA esc.Material=Enum.Material.SmoothPlastic esc.TopSurface=Enum.SurfaceType.Smooth esc.Parent=pai
	for i=1,9 do
		local t=i/9
		part({Name='Degrau',Size=V(18.2,.22,.9),Position=V(0,6.1+7.8*t-.11,zc-206+19*t),Color=BRANCO,Material=Enum.Material.SmoothPlastic},pai)
	end
	part({Name='FaixaEscada',Size=V(3,.1,19),CFrame=CFrame.new(0,10.1,zc-196.5)*CFrame.Angles(math.atan(7.8/19),0,0),Color=KI,Material=Enum.Material.Neon,Transparency=.25},pai)
	for _,s in {-1,1} do
		local guarda=part({Name='GuardaEscada',Size=V(.6,1,21.5),CFrame=CFrame.new(s*9.3,13.4,zc-196.5)*CFrame.Angles(math.atan(7.8/19),0,0),Color=AZUL,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
		guarda:SetAttribute('TravessiaKeep',true)
		part({Name='PosteGuarda',Size=V(.8,3.2,.8),Position=V(s*9.3,7.6,zc-205),Color=BRANCO,Material=Enum.Material.SmoothPlastic},pai)
		part({Name='PosteGuarda',Size=V(.8,3.2,.8),Position=V(s*9.3,15.4,zc-188),Color=BRANCO,Material=Enum.Material.SmoothPlastic},pai)
	end
	-- apoio do arco de boas-vindas (os pilares ficam fora da passarela)
	part({Name='ApoioArco',Size=V(28,1,9),Position=V(0,5.55,zc-206),Color=CINZA,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
	arcoCapsule(pai,zc-206,23,17,'VALE CAPSULE')
	-- ===== SAIDA NORTE: desfiladeiro na montanha + portal para a proxima ilha =====
	local rochas=model:FindFirstChild('DRAGONBALL_ROCKS')
	local mont=rochas and rochas:FindFirstChild('Montanha')
	if mont then
		for _,m in mont:GetChildren() do
			if m:IsA('Model') then
				local p=m:GetPivot().Position
				if math.abs(p.X)<30 and p.Z>zc+150 and p.Z<zc+280 then
					local lado=p.X>=0 and 1 or -1
					m:PivotTo(m:GetPivot()+V(lado*46-p.X,0,0))
				end
			end
		end
	end
	-- limpa colisoes invisiveis que sobraram no desfiladeiro
	local ov=OverlapParams.new() ov.FilterType=Enum.RaycastFilterType.Include ov.FilterDescendantsInstances={model}
	for _,p in workspace:GetPartBoundsInBox(CFrame.new(0,36,zc+215),V(46,70,130),ov) do
		if p:IsA('BasePart') and p.CanCollide and p.Transparency>=.99 and not p:GetAttribute('TravessiaKeep') then p:Destroy() end
	end
	-- estrada do desfiladeiro: a saida passa na PISTA OESTE, colada a fachada da
	-- Mina Capsule (o tunel da mina ocupa o lado leste do vao)
	part({Name='EstradaSaida',Size=V(16,.5,64),Position=V(-3,6.15,zc+186),Color=C(238,230,206),Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
	part({Name='FaixaEstrada',Size=V(2.4,.1,64),Position=V(-6,6.45,zc+186),Color=AZUL,Material=Enum.Material.SmoothPlastic},pai)
	-- guarda-corpo do lado oeste (alem dele e vazio)
	part({Name='CorrimaoOeste',Size=V(.5,.5,58),Position=V(-11.3,9.2,zc+184),Color=AZUL,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
	for _,z in {zc+158,zc+172,zc+186,zc+200,zc+212} do
		part({Name='PosteCorrimao',Size=V(.7,3.4,.7),Position=V(-11.3,7.7,z),Color=BRANCO,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
	end
	for _,z in {zc+164,zc+196} do
		local poste=part({Name='BalizaKi',Size=V(.7,4.6,.7),Position=V(-13.5,8.3,z),Color=BRANCO,Material=Enum.Material.SmoothPlastic},pai)
		local orbe=part({Name='OrbeKi',Shape=Enum.PartType.Ball,Size=V(1.5,1.5,1.5),Position=V(-13.5,11.2,z),Color=KI,Material=Enum.Material.Neon},pai)
		luz(orbe,KI,13,.8)
	end
	-- portico da pista: pilar oeste + placa apoiada na fachada da mina
	part({Name='PilarSaida',Size=V(2.4,14,2.4),Position=V(-14,13,zc+170),Color=BRANCO,Material=Enum.Material.SmoothPlastic,CanCollide=true},pai)
	part({Name='FaixaPilarSaida',Size=V(2.6,1.4,2.6),Position=V(-14,12,zc+170),Color=AZUL,Material=Enum.Material.SmoothPlastic},pai)
	local placaSaida=part({Name='PlacaSaida',Size=V(13,2.8,.7),Position=V(-8,18.6,zc+170),Color=NAVY,Material=Enum.Material.SmoothPlastic},pai)
	texto(placaSaida,'PROXIMA ILHA',C(150,236,255))
	part({Name='LuzPlacaSaida',Size=V(12,.3,.3),Position=V(-8,16.9,zc+170),Color=KI,Material=Enum.Material.Neon},pai)
	clonarKit('Torre_Energia',CFrame.new(-16,6,zc+152),.9,pai)
	return pai
end

return M
