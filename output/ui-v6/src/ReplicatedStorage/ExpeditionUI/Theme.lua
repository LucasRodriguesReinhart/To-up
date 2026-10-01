-- ============================================================================
-- THEME V5 · EXPEDITIONS · Anime Mining Simulator
-- Contorno preto, faces simples, arte dominante e tipografia sem redução implícita.
-- Cor, fonte, estados e componentes são centralizados neste módulo.
-- ============================================================================
local T = {}
local Tween = game:GetService("TweenService")
local Run = game:GetService("RunService")
local RS = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")

local rgb = Color3.fromRGB
local WHITE = Color3.new(1, 1, 1)
local function kp(t, v) return NumberSequenceKeypoint.new(t, v) end
T.kp = kp

-- ---------------------------------------------------------------- CORES
T.P = {
 ink=rgb(2,4,6), bg0=rgb(7,10,12), bg1=rgb(13,17,20), bg2=rgb(20,25,28), bg3=rgb(31,37,40), bg4=rgb(46,53,57),
 line=rgb(116,132,139), lineSoft=rgb(61,73,79), text=rgb(255,255,255), text2=rgb(225,225,235), text3=rgb(169,169,188),
 accent=rgb(0,180,224), gold=rgb(255,211,43), violet=rgb(167,74,255), magenta=rgb(245,40,186),
 success=rgb(49,204,108), danger=rgb(225,38,64), warning=rgb(255,144,23), info=rgb(66,166,255),
 teal=rgb(30,224,180), ember=rgb(255,105,34), pink=rgb(255,79,170), robux=rgb(44,224,89), neutral=rgb(56,59,63),
}
T.Space = { xs=4, sm=8, md=12, lg=16, xl=24, xxl=32, section=48 }
T.Radius = { button=6, card=8, modal=10, icon=6 }
T.Motion = { fast=.10, medium=.18, slow=.32 }
T.Type = { display=32, title=26, subtitle=20, body=16, caption=12, number=26, currency=26, label=16, button=22, tooltip=15 }
function T.motionEnabled()
 local p=game:GetService("Players").LocalPlayer
 return not p or (p:GetAttribute("ReducedMotion")~=true and p:GetAttribute("ExpeditionEffectsEnabled")~=false)
end

-- Um registro para todos os tweens contínuos: duas conexões de preferência no total,
-- sem polling. Cada componente remove seu registro ao ser destruído.
local continuousTweens = {}
local motionPreferenceConnections = {}
local function disconnectMotionPreferences()
	for _, connection in ipairs(motionPreferenceConnections) do connection:Disconnect() end
	table.clear(motionPreferenceConnections)
end
local function applyContinuousMotion(tw, state, enabled)
	if state.enabled == enabled then return end
	state.enabled = enabled
	if enabled then
		if state.onState then state.onState(true) end
		tw:Play()
	else
		tw:Cancel()
		for property, value in pairs(state.rest or {}) do state.target[property] = value end
		if state.onState then state.onState(false) end
	end
end
local function refreshContinuousMotion()
	local enabled = T.motionEnabled()
	for tw, state in pairs(continuousTweens) do applyContinuousMotion(tw, state, enabled) end
end
local function continuousTween(owner, target, info, goals, rest, onState)
	local tw = Tween:Create(target, info, goals)
	local state = { target = target, rest = rest, onState = onState }
	continuousTweens[tw] = state
	owner.Destroying:Once(function()
		continuousTweens[tw] = nil
		tw:Cancel()
		if next(continuousTweens) == nil then disconnectMotionPreferences() end
	end)
	if #motionPreferenceConnections == 0 and Run:IsClient() then
		local player = game:GetService("Players").LocalPlayer
		if player then
			for _, attribute in ipairs({ "ReducedMotion", "ExpeditionEffectsEnabled" }) do
				table.insert(motionPreferenceConnections, player:GetAttributeChangedSignal(attribute):Connect(refreshContinuousMotion))
			end
		end
	end
	applyContinuousMotion(tw, state, T.motionEnabled())
	return tw
end

local P = T.P
local INK = P.ink

T.C = {
	black = P.bg0, panel = P.bg1, gray = P.neutral, white = WHITE, muted = P.text2,
	gold = P.gold, purple = P.violet, cyan = P.accent, green = P.success, red = P.danger,
	teal = P.teal, orange = P.warning, blue = P.info,
}

-- ---------------------------------------------------------------- RARIDADES
T.Rarity = {
	comum    = { nome = "Comum",    cor = rgb(176, 184, 204), ordem = 1 },
	incomum  = { nome = "Incomum",  cor = rgb(86, 226, 96),   ordem = 2 },
	raro     = { nome = "Raro",     cor = rgb(56, 150, 255),  ordem = 3 },
	epico    = { nome = "Épico",    cor = rgb(184, 88, 255),  ordem = 4, glow = true },
	lendario = { nome = "Lendário", cor = rgb(255, 196, 28),  ordem = 5, glow = true, shine = true },
	mitico   = { nome = "Mítico",   cor = rgb(255, 48, 92),   ordem = 6, glow = true, shine = true },
	secreto  = { nome = "Secreto",  cor = rgb(240, 240, 255), ordem = 7, glow = true, shine = true, rainbow = true },
}
local ORE_TO_RARITY = { comum = "comum", incomum = "incomum", raro = "raro", epica = "epico", lendaria = "lendario", chefe = "mitico" }
T.RAINBOW = ColorSequence.new({
	ColorSequenceKeypoint.new(0, rgb(255, 70, 110)), ColorSequenceKeypoint.new(.2, rgb(255, 200, 40)),
	ColorSequenceKeypoint.new(.4, rgb(100, 240, 110)), ColorSequenceKeypoint.new(.6, rgb(60, 200, 255)),
	ColorSequenceKeypoint.new(.8, rgb(180, 100, 255)), ColorSequenceKeypoint.new(1, rgb(255, 70, 110)),
})
function T.rar(key)
	key = ORE_TO_RARITY[key] or key
	return T.Rarity[key] or T.Rarity.comum, (T.Rarity[key] and key or "comum")
end

T.Page = {
	Store = P.gold, Inventory = P.accent, Items = P.info, Summon = P.violet, Quests = P.warning,
	Events = P.pink, Areas = P.teal, Forge = P.ember, Settings = rgb(130, 120, 220),
}

-- ---------------------------------------------------------------- TIPOGRAFIA
local GOTHAM = "rbxasset://fonts/families/GothamSSm.json"
local BUILDER = "rbxasset://fonts/families/BuilderSans.json"
T.F = {
 display=Font.new(GOTHAM,Enum.FontWeight.Heavy),
 title=Font.new(GOTHAM,Enum.FontWeight.Heavy), label=Font.new(GOTHAM,Enum.FontWeight.Heavy),
 heavy=Font.new(GOTHAM,Enum.FontWeight.Heavy), body=Font.new(GOTHAM,Enum.FontWeight.Bold),
 regular=Font.new(GOTHAM,Enum.FontWeight.Medium), number=Font.new(GOTHAM,Enum.FontWeight.Heavy),
 caption=Font.new(GOTHAM,Enum.FontWeight.Bold), footer=Font.new(GOTHAM,Enum.FontWeight.Bold),
}
local STROKED = {display=true,title=true,label=true,heavy=true,number=true}

-- string.upper nao conhece acentos ("Diário" virava "DIáRIO")
local UPPER_ACCENTS = { { "á", "Á" }, { "à", "À" }, { "â", "Â" }, { "ã", "Ã" }, { "é", "É" }, { "ê", "Ê" }, { "í", "Í" },
	{ "ó", "Ó" }, { "ô", "Ô" }, { "õ", "Õ" }, { "ú", "Ú" }, { "ü", "Ü" }, { "ç", "Ç" } }
function T.upper(value)
	local s = string.upper(tostring(value or ""))
	for _, pair in ipairs(UPPER_ACCENTS) do s = s:gsub(pair[1], pair[2]) end
	return s
end
T.CENTER, T.LEFT, T.RIGHT = Enum.TextXAlignment.Center, Enum.TextXAlignment.Left, Enum.TextXAlignment.Right

-- ---------------------------------------------------------------- ASSETS
T.Assets = {
	icons = "rbxassetid://104814264232835", header = "rbxassetid://116375197441315",
	-- Espirais vetoriais e emblema de mineração para a linguagem Expeditions.
	pattern = "rbxassetid://105263140080714", crest = "rbxassetid://88607305530210", patternAntigo = "rbxassetid://86819702987826",
	halftone = "rbxassetid://122225275814931",
	lobby = "rbxassetid://130085080318250",
	logo = "rbxassetid://118440179735497",
	rays = "rbxassetid://82278754836880",
	spark = "rbxassetid://93745913424342",
	-- arte de cada ilha (Viajar, Invocar e transicao de viagem)
	areas = {
		"rbxassetid://101066089903346", "rbxassetid://85779368803874", "rbxassetid://90527758233479",
		"rbxassetid://104635612587442", "rbxassetid://109337840912579", "rbxassetid://133967024190781",
	},
	-- minerio por raridade (feed de coleta, forja, recompensas)
	ore = {
		comum = "rbxassetid://93857051385311", incomum = "rbxassetid://103598735159509", raro = "rbxassetid://96221855249208",
		epico = "rbxassetid://73307783035701", lendario = "rbxassetid://75762467171008", mitico = "rbxassetid://94223784618123",
		secreto = "rbxassetid://94223784618123",
	},
	-- atributos (ficha de unidade, HUD, comparacoes da loja)
	stat = {
		dano = "rbxassetid://94552502266497", velocidade = "rbxassetid://100712963702922",
		capacidade = "rbxassetid://97132919516046", sorte = "rbxassetid://73227768675822",
		nivel = "rbxassetid://82017114135306",
	},
}
T.IconIndex = { store = 0, units = 1, items = 2, quests = 3, areas = 4, play = 5, events = 6, summon = 7, pickaxe = 8, coins = 9, vip = 10, shiny = 11, potion = 12, gift = 13, forge = 14, settings = 15 }

-- arte da ilha (cai para a imagem do lobby se faltar)
function T.areaImage(id)
	return T.Assets.areas[id] or T.Assets.lobby
end

-- ================================================================ PRIMITIVAS
function T.new(class, props, parent)
	local o = Instance.new(class)
	for k, v in pairs(props or {}) do o[k] = v end
	o.Parent = parent
	return o
end

function T.tween(o, t, props, style, dir, delay)
	local tw = Tween:Create(o, TweenInfo.new(T.motionEnabled() and t or .001, style or Enum.EasingStyle.Quint, dir or Enum.EasingDirection.Out, 0, false, delay or 0), props)
	tw:Play()
	return tw
end

function T.corner(p, r)
	local c = p:FindFirstChildOfClass("UICorner") or T.new("UICorner", {}, p)
	c.CornerRadius = UDim.new(0, math.min(r or 8, 12))
	return c
end

function T.stroke(p, col, width, alpha)
	return T.new("UIStroke", { Color = col or P.lineSoft, Thickness = math.min(width or 1, 3), Transparency = alpha or 0,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border, LineJoinMode = Enum.LineJoinMode.Round }, p)
end

function T.gradient(p, top, bottom, rotation)
	return T.new("UIGradient", { Color = ColorSequence.new(top, bottom), Rotation = rotation or 90 }, p)
end

function T.fade(p, rotation, a0, a1)
	return T.new("UIGradient", { Rotation = rotation or 90, Transparency = NumberSequence.new({ kp(0, a0 or 0), kp(1, a1 or 1) }) }, p)
end

function T.frame(p, name, x, y, w, h, col, alpha)
	return T.new("Frame", { Name = name, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(math.max(0, w), math.max(0, h)),
		BackgroundColor3 = col or P.bg1, BackgroundTransparency = alpha or 0, BorderSizePixel = 0 }, p)
end

function T.clear(p)
	for _, o in ipairs(p:GetChildren()) do
		if not o:IsA("UIComponent") then o:Destroy() end
	end
end

-- Size is intentional: layout grows, wraps or truncates; text never shrinks to fit.
-- Caption/footer are explicit compact roles. Canvas scaling belongs to the client.
T.uiScale = 1

function T.text(p, name, value, x, y, w, h, size, col, align, font, stroke)
	font = font or "title"
	local minimum = (font == "caption" or font == "footer") and 11 or 14
	local physicalMinimum=(font=="caption" or font=="footer") and 9 or (font=="display" and 16 or 11)
	size = math.max(minimum, size or 16, physicalMinimum / math.max(.4,T.uiScale))
	local t = T.new("TextLabel", {
		Name = name, Text = value or "", Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(math.max(1, w), math.max(1, h)),
		BackgroundTransparency = 1, BorderSizePixel = 0, FontFace = T.F[font] or T.F.title, TextSize = size,
		TextColor3 = col or P.text, TextXAlignment = align or T.LEFT, TextYAlignment = Enum.TextYAlignment.Center,
		TextScaled = false, TextWrapped = false, TextTruncate = Enum.TextTruncate.AtEnd,
	}, p)
	-- TextScaled=false already fixes the authored font size. A fixed UITextSizeConstraint
	-- incorrectly clamps the final rendered glyphs after UIScale and causes overflow.
	t:SetAttribute("TextRole", font)
	t:SetAttribute("RequestedTextSize", size)
	local function applyTextPolicy()
		t.TextScaled = false
		t.TextSize = size
		t.TextWrapped = t:GetAttribute("Paragraph") == true or t.Text:find("\n") ~= nil
	end
	local function markOverflow()
		t:SetAttribute("TextOverflow", not t.TextFits)
	end
	applyTextPolicy()
	t:GetPropertyChangedSignal("Text"):Connect(applyTextPolicy)
	t:GetAttributeChangedSignal("Paragraph"):Connect(applyTextPolicy)
	t:GetPropertyChangedSignal("TextBounds"):Connect(markOverflow)
	t:GetPropertyChangedSignal("AbsoluteSize"):Connect(markOverflow)
	markOverflow()
	if stroke == nil and STROKED[font] then stroke = math.clamp(size * .06, 1, 1.8) end
	if stroke and stroke ~= false then
		T.new("UIStroke", { Color = INK, Thickness = stroke == true and 1.8 or stroke, LineJoinMode = Enum.LineJoinMode.Round }, t)
	end
	return t
end

function T.para(p, name, value, x, y, w, h, size, col, align, font)
	local t = T.text(p, name, value, x, y, w, h, size, col or P.text2, align, font or "body", false)
	t:SetAttribute("Paragraph", true)
	t.TextTruncate = Enum.TextTruncate.None
	t.TextYAlignment = Enum.TextYAlignment.Top
	return t
end

function T.image(p, name, id, x, y, w, h, color, alpha)
	return T.new("ImageLabel", { Name = name, Image = id, BackgroundTransparency = 1, Position = UDim2.fromOffset(x, y),
		Size = UDim2.fromOffset(w, h), ImageColor3 = color or WHITE, ImageTransparency = alpha or 0, ScaleType = Enum.ScaleType.Fit }, p)
end

function T.icon(p, key, x, y, w, h)
 local cells={coins=Vector2.new(0,0),dano=Vector2.new(512,0),power=Vector2.new(512,0),items=Vector2.new(0,512),capacidade=Vector2.new(0,512),summon=Vector2.new(512,512)}
 if cells[key] then
  local im=T.image(p,"Icon_"..key,"rbxassetid://119470718103729",x,y,w,h or w)
  im.ImageRectOffset=cells[key];im.ImageRectSize=Vector2.new(512,512)
  local index=(key=="summon" and T.IconIndex.units) or T.IconIndex[key] or T.IconIndex[key=="dano" and "pickaxe" or "items"] or 0
  local fallback=T.image(im,"AssetFallback",T.Assets.icons,0,0,0,0)
  fallback.Size=UDim2.fromScale(1,1)
  fallback.ImageRectOffset=Vector2.new((index%4)*256,math.floor(index/4)*256)
  fallback.ImageRectSize=Vector2.new(256,256)
  local function sync() fallback.Visible=not im.IsLoaded end
  sync();im:GetPropertyChangedSignal("IsLoaded"):Connect(sync)
  task.spawn(function()
   while im.Parent and not im.IsLoaded do task.wait(.25) end
   if im.Parent then sync() end
  end)
  return im
 end
	local i = T.IconIndex[key] or T.IconIndex.items
	local im = T.image(p, "Icon_" .. key, T.Assets.icons, x, y, w, h or w)
	im.ImageRectOffset = Vector2.new((i % 4) * 256, math.floor(i / 4) * 256)
	im.ImageRectSize = Vector2.new(256, 256)
	return im
end

-- arte dedicada com rede de seguranca: se o asset nao carregar (moderacao pendente,
-- permissao faltando), o icone do atlas entra no lugar sem deixar buraco na tela.
local ATLAS_EQUIVALENTE = { dano = "pickaxe", velocidade = "play", capacidade = "items", sorte = "shiny", nivel = "units" }
local function comFallback(img, p, atlasKey, x, y, w, h)
	task.delay(4, function()
		if img.Parent and not img.IsLoaded then
			local pai = img.Parent
			img:Destroy()
			if pai.Parent then T.icon(pai, atlasKey, x, y, w, h) end
		end
	end)
	return img
end

-- icone do minerio pela raridade/variante
function T.oreIcon(p, key, x, y, w, h)
	local _, chave = T.rar(key)
	local id = T.Assets.ore[chave]
	if not id then return T.icon(p, "items", x, y, w, h) end
	return comFallback(T.image(p, "Ore_" .. chave, id, x, y, w, h or w), p, "items", x, y, w, h or w)
end

-- icone de atributo: usa a arte dedicada quando existir, senao o atlas
function T.statIcon(p, key, x, y, w, h)
 if key=="dano" or key=="capacidade" then return T.icon(p,key,x,y,w,h) end
	local id = T.Assets.stat[key]
	if id then return comFallback(T.image(p, "Stat_" .. key, id, x, y, w, h or w), p, ATLAS_EQUIVALENTE[key] or "items", x, y, w, h or w) end
	return T.icon(p, key, x, y, w, h)
end

function T.texture(p, kind, alpha, col, tile)
	local im = T.image(p, "Texture_" .. kind, T.Assets[kind=="halftone" and "pattern" or kind], 0, 0, 0, 0, col, kind=="halftone" and math.max(.86,alpha or .86) or (alpha or .8))
	im.Size = UDim2.fromScale(1, 1)
	im.ScaleType = Enum.ScaleType.Tile
	local ts = kind=="halftone" and math.max(140,tile or 180) or (tile or 110)
	im.TileSize = UDim2.fromOffset(ts, ts)
	local cr = p:FindFirstChildOfClass("UICorner")
	T.corner(im, cr and cr.CornerRadius.Offset or 10)
	return im
end

function T.scroll(p, name, x, y, w, h, col)
	return T.new("ScrollingFrame", {
		Name = name, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(math.max(1, w), math.max(1, h)),
		BackgroundTransparency = 1, BorderSizePixel = 0, ScrollBarThickness = 6, ScrollBarImageColor3 = col or P.line,
		ScrollBarImageTransparency = 0, CanvasSize = UDim2.new(), ScrollingDirection = Enum.ScrollingDirection.Y,
		ElasticBehavior = Enum.ElasticBehavior.WhenScrollable,
		TopImage = "rbxasset://textures/ui/Scroll/scroll-middle.png", BottomImage = "rbxasset://textures/ui/Scroll/scroll-middle.png",
	}, p)
end

-- ================================================================ SUPERFÍCIES
function T.panel(p,name,x,y,w,h,opts)
 opts=opts or {}
 local f=T.frame(p,name,x,y,w,h,opts.bg or P.bg2,opts.alpha or 0)
 T.corner(f, math.min(opts.radius or 4,5))
 if opts.stroke~=false then T.stroke(f,opts.strokeColor or P.lineSoft,opts.strokeWidth or 1,opts.strokeAlpha or .12) end
 return f
end

function T.shadow(f, r, off, alpha)
	-- Solid six-pixel backing edge, not a second translucent panel behind the UI.
	local s = T.new("Frame", { Name = f.Name .. "Shadow", BackgroundColor3 = INK, BackgroundTransparency = 0,
		BorderSizePixel = 0, AnchorPoint = f.AnchorPoint, Position = f.Position + UDim2.fromOffset(0, math.clamp(off or 4, 0, 6)), Size = f.Size,
		ZIndex = f.ZIndex - 1 }, f.Parent)
	T.corner(s, r or 12)
	return s
end

function T.surface(p, col)
	p.BackgroundColor3 = P.bg3
	T.corner(p, 4)
	T.stroke(p, col or P.line, 1)
	return p
end

-- listras diagonais (dentro de um retângulo)
function T.stripes(p, name, x, y, w, h, col, alpha, rotation, count)
	local f = T.frame(p, name, x, y, w, h, col or WHITE, 0)
	local a = alpha or .9
	local n = math.clamp(count or 4, 1, 4) -- NumberSequence aceita no maximo 20 pontos
	local seq = { kp(0, 1) }
	for i = 0, n - 1 do
		local s, e = (i + .15) / n, (i + .5) / n
		table.insert(seq, kp(s, 1)); table.insert(seq, kp(s + .003, a))
		table.insert(seq, kp(e, a)); table.insert(seq, kp(e + .003, 1))
	end
	table.insert(seq, kp(1, 1))
	T.new("UIGradient", { Rotation = rotation or -62, Transparency = NumberSequence.new(seq) }, f)
	return f
end

-- faixa inclinada (paralelogramo) com gradiente de cor. tilt = inclinação visual das pontas em graus
function T.slant(p, name, x, y, w, h, col, opts)
	opts = opts or {}
	local f = T.frame(p, name, x, y, w, h, WHITE, 0)
	local tilt = math.rad(opts.tilt or 18)
	local shift = h * math.tan(tilt) / w
	local angle = math.deg(math.atan(shift))
	local cut = math.clamp(shift / 2 + .004, .005, .45)
	local fillA = opts.alpha or 0
	local top = opts.top or col:Lerp(WHITE, .22)
	local bottom = opts.bottom or col:Lerp(INK, .18)
	T.new("UIGradient", {
		Rotation = angle,
		Color = ColorSequence.new(top, bottom),
		Transparency = NumberSequence.new({ kp(0, 1), kp(cut, 1), kp(cut + .002, fillA), kp(1 - cut - .002, fillA), kp(1 - cut, 1), kp(1, 1) }),
	}, f)
	return f, cut
end

-- card texturizado na cor da raridade (itens, unidades, recompensas, slots)
function T.tile(p,name,x,y,w,h,key,opts)
 opts=opts or {}
 local r=T.rar(key)
 local col=opts.color or r.cor
 local f=T.frame(p,name,x,y,w,h,opts.dim and P.bg0 or Color3.new(1,1,1),0)
 if not opts.dim then
  T.gradient(f,col:Lerp(WHITE,.10),col:Lerp(P.ink,.32),90)
  T.texture(f,"pattern",.48,col:Lerp(WHITE,.45),128)
 end
 T.corner(f,math.min(opts.radius or 5,5))
 local st=T.new("UIStroke",{Name="Rim",Color=opts.selected and P.text or (opts.dim and P.lineSoft or col),Thickness=opts.selected and 2 or 1.25,Transparency=0,ApplyStrokeMode=Enum.ApplyStrokeMode.Border},f)
 local inner=T.frame(f,"CardInset",2,2,w-4,h-4,nil,1);T.corner(inner,3);T.stroke(inner,opts.dim and P.lineSoft or col:Lerp(WHITE,.48),.7,.22)
 local mark=T.frame(f,"RarityMark",1,h-4,w-2,3,opts.dim and P.neutral or col,.6)
 T.corner(mark,2)
 if opts.animated and r.ordem>=6 and not opts.dim and T.motionEnabled() then T.shine(f,4,.9) end
 return f,r
end

-- ================================================================ MOTION
function T.headerOrnament(p,w,h,col)
 local dark=col:Lerp(P.ink,.70)
 local rim=T.image(p,"CrestOutline",T.Assets.crest,-17,-15,h+30,h+30,P.ink,0)
 local ring=T.image(p,"MiningCrest",T.Assets.crest,-14,-12,h+24,h+24,col:Lerp(P.ink,.38),0)
 local shadow=T.slant(p,"HeaderOutline",-8,-2,w+4,h+4,P.ink,{tilt=18})
 local plate=T.slant(p,"TitlePlate",-6,0,w,h,col,{top=col:Lerp(WHITE,.12),bottom=col:Lerp(P.ink,.38),tilt=18})
 T.slant(p,"TitleInset",-3,3,w-9,h-6,col,{top=col,bottom=col:Lerp(P.ink,.28),tilt=18,alpha=.35})
 T.frame(p,"TitleEdge",6,1,w-24,1,col:Lerp(WHITE,.48),.12)
 local tail=T.image(p,"WindTailOutline",T.Assets.pattern,w-82,h-36,88,60,P.ink,.05);tail.Rotation=-12
 local curl=T.image(p,"WindTail",T.Assets.pattern,w-79,h-33,82,54,dark,.02);curl.Rotation=-12

 return plate
end

function T.scaleOf(o)
	return o:FindFirstChildOfClass("UIScale") or T.new("UIScale", {}, o)
end

function T.pop(o, amount, time)
	if not T.motionEnabled() then return end
	local sc = T.scaleOf(o)
	sc.Scale = math.min(amount or 1.04,1.08)
	T.tween(sc, time or .32, { Scale = 1 }, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
end

function T.enter(o, fromScale, time, delay)
	local sc = T.scaleOf(o)
	sc.Scale = T.motionEnabled() and math.max(fromScale or .97,.94) or 1
	T.tween(sc, time or .26, { Scale = 1 }, Enum.EasingStyle.Back, Enum.EasingDirection.Out, delay)
	return sc
end

function T.shake(o, force)
	if not T.motionEnabled() or not o or not o.Parent or o:GetAttribute("Shaking") then return end
	o:SetAttribute("Shaking", true)
	local p0 = o.Position
	local f = math.min(force or 3,4)
	task.spawn(function()
		for _, k in ipairs({ 1, -.85, .6, -.4, .2, 0 }) do
			if not o.Parent then return end
			o.Position = p0 + UDim2.fromOffset(f * k, 0)
			task.wait(.028)
		end
		o.Position = p0
		o:SetAttribute("Shaking", nil)
	end)
end

function T.countTo(label, from, to, fmt, dur)
	fmt = fmt or T.format
	if not label or from == to then if label then label.Text = fmt(to) end return end
	local nv = Instance.new("NumberValue")
	nv.Value = from
	nv.Changed:Connect(function(v) if label.Parent then label.Text = fmt(math.floor(v + .5)) end end)
	local tw = Tween:Create(nv, TweenInfo.new(T.motionEnabled() and (dur or .5) or .001, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Value = to })
	tw.Completed:Once(function() if label.Parent then label.Text = fmt(to) end nv:Destroy() end)
	tw:Play()
	return tw
end

function T.shine(f, period, alpha, rotation)
	local s = T.frame(f, "Shine", 0, 0, 0, 0, WHITE, 0)
	s.Size = UDim2.fromScale(1, 1)
	s.ZIndex = 8
	local cr = f:FindFirstChildOfClass("UICorner")
	if cr then T.corner(s, cr.CornerRadius.Offset) end
	local a = alpha or .7
	local g = T.new("UIGradient", { Rotation = rotation or 22, Offset = Vector2.new(-1, 0),
		Transparency = NumberSequence.new({ kp(0, 1), kp(.4, 1), kp(.5, a), kp(.6, 1), kp(1, 1) }) }, s)
	continuousTween(s, g, TweenInfo.new(.85, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, false, period or 2.4),
		{ Offset = Vector2.new(1, 0) }, { Offset = Vector2.new(-1, 0) }, function(enabled) s.Visible = enabled end)
	return s
end

function T.breathe(o, prop, a, b, period)
	o[prop] = a
	return continuousTween(o, o, TweenInfo.new(period or .9, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
		{ [prop] = b }, { [prop] = a })
end

-- brilhos de 4 pontas espalhados (fundos de telas cheias / recompensas)
function T.sparkles(p, w, h, n, col)
	n=math.min(n,6)
	local rnd = Random.new(n * 7 + math.floor(w))
	for i = 1, n do
		local size = rnd:NextInteger(16, 46)
		local holder = T.frame(p, "Sparkle" .. i, rnd:NextNumber(0, w - size), rnd:NextNumber(0, h - size), size, size, nil, 1)
		T.image(holder, "Art", T.Assets.spark, 0, 0, size, size, col or WHITE, .3)
		local sc = T.new("UIScale", { Scale = .4 }, holder)
		continuousTween(holder, sc, TweenInfo.new(rnd:NextNumber(.9, 1.8), Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true, rnd:NextNumber(0, 1.5)),
			{ Scale = 1.1 }, { Scale = .4 }, function(enabled) holder.Visible = enabled end)
	end
end

-- ================================================================ SOM
local somOk, Som = pcall(function() return require(RS:WaitForChild("SomJogo", 5)) end)
function T.som(nome, opts)
	if somOk and Som and Run:IsClient() then Som.tocar(nome, opts) end
end

-- ================================================================ BOTÕES
function T.tone(col)
	local h, s, v = col:ToHSV()
	return {
		top = Color3.fromHSV(h, s * .8, math.min(1, v * 1.12 + .08)),
		bottom = Color3.fromHSV(h, math.min(1, s * 1.05), v * .82),
		lip = Color3.fromHSV(h, math.min(1, s * 1.05), v * .42),
		edge = Color3.fromHSV(h, s * .45, math.min(1, v * 1.2 + .2)),
	}
end

-- botão 3D: face com gradiente, contorno escuro, brilho superior e lábio. Hover cresce, press afunda, disabled treme.
function T.bindInteraction(b,fn,opts)
 opts=opts or {}
 b.Selectable=true
 b.AutoButtonColor=false
 local sc=T.scaleOf(b)
 local hovered=false
 local function pose(v)
  if T.motionEnabled() then T.tween(sc,T.Motion.fast,{Scale=v},Enum.EasingStyle.Quad) else sc.Scale=1 end
 end
 local function focus(on)
  hovered=on
  if opts.onFocus then opts.onFocus(on) end
  if not b:GetAttribute("Disabled") then pose(on and (opts.hoverScale or 1.015) or 1) end
 end
 b.MouseEnter:Connect(function() focus(true) end)
 b.MouseLeave:Connect(function() focus(false) end)
 b.SelectionGained:Connect(function() focus(true) end)
 b.SelectionLost:Connect(function() focus(false) end)
 b.InputBegan:Connect(function(input)
  if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch or input.KeyCode==Enum.KeyCode.ButtonA then
   if not b:GetAttribute("Disabled") then pose(.975) end
  end
 end)
 b.InputEnded:Connect(function(input)
  if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch or input.KeyCode==Enum.KeyCode.ButtonA then pose(hovered and 1.015 or 1) end
 end)
 b.Activated:Connect(function()
  if b:GetAttribute("Disabled") then
   if opts.onDisabled then opts.onDisabled() end
   T.som("ui_erro"); T.shake(b,2); return
  end
  pose(.98); task.delay(.08,function() if b.Parent then pose(hovered and 1.015 or 1) end end)
  if opts.sound~=false then T.som(opts.sound or "ui_click") end
  if fn then fn() end
 end)
 return b
end

function T.button(p,name,value,x,y,w,h,col,fn,opts)
 opts=opts or {}
 local b=T.new("TextButton",{Name=name,Text="",BackgroundTransparency=1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(w,h),Selectable=true},p)
 b:SetAttribute("ToneColor",col or P.neutral)
 local face=T.frame(b,"Face",0,0,w,h,WHITE,0);T.corner(face,4)
 face.ClipsDescendants=true
 local grad=T.gradient(face,P.neutral,P.bg1,90)
 T.stroke(face,P.ink,2,0)
 local inner=T.frame(face,"InnerRim",1.5,1.5,w-3,h-3,nil,1);T.corner(inner,3)
 local rim=T.stroke(inner,P.line,1,0)
 local light=T.frame(face,"TopLight",3,2,w-6,1,WHITE,.50)
 local lower=T.frame(face,"LowerEdge",3,h-4,w-6,2,P.ink,.15)
 local ix=12
 if opts.icon then local isz=math.min(30,h-16);T.icon(face,opts.icon,10,(h-isz)/2,isz,isz);ix=isz+18 end
 local caption
 if value and value~="" then caption=T.text(face,"Caption",value,ix,0,w-ix-12,h,math.max(14,opts.size or 22),P.text,opts.align or T.CENTER,opts.font or "title",1.25) end
 local focused=false
 local function paint()
  local disabled=b:GetAttribute("Disabled")
  local tone=b:GetAttribute("ToneColor") or P.neutral
  local neutral=tone==P.neutral or opts.variant=="secondary"
  local used=disabled and rgb(31,34,36) or (neutral and P.neutral or tone)
  local top=focused and used:Lerp(WHITE,.12) or used
  grad.Color=ColorSequence.new({ColorSequenceKeypoint.new(0,top:Lerp(WHITE,.08)),ColorSequenceKeypoint.new(.48,used:Lerp(P.ink,.12)),ColorSequenceKeypoint.new(.51,used:Lerp(P.ink,.25)),ColorSequenceKeypoint.new(1,used:Lerp(P.ink,.54))})
  rim.Color=focused and P.text or (neutral and rgb(137,144,149) or used:Lerp(WHITE,.28))
  rim.Transparency=disabled and .65 or .10
  light.Visible=not disabled
  if caption then caption.TextColor3=disabled and P.text3 or (opts.textColor or P.text) end
 end
 b:GetAttributeChangedSignal("Disabled"):Connect(paint)
 b:GetAttributeChangedSignal("ToneColor"):Connect(paint)
 T.bindInteraction(b,fn,{sound=opts.sound,hoverScale=opts.hoverScale or 1,onDisabled=opts.onDisabled,onFocus=function(on) focused=on;paint() end})
 paint()
 return b
end

function T.setTone(b, col) if b then b:SetAttribute("ToneColor", col) end end
function T.setEnabled(b, on) if b then b:SetAttribute("Disabled", not on) end end

-- botão redondo de ícone com rótulo embaixo (ações do inventário, atalhos)
function T.roundButton(p, name, key, label, x, y, size, fn, opts)
	opts = opts or {}
	local b = T.new("TextButton", { Name = name, Text = "", AutoButtonColor = false, BackgroundColor3 = opts.bg or P.bg2,
		BorderSizePixel = 0, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size) }, p)
	T.corner(b, 8)
	local st = T.stroke(b, opts.stroke or P.line, 3)
	
	local isz = math.floor(size * .64)
	T.icon(b, key, (size - isz) / 2, (size - isz) / 2, isz, isz)
	if label then T.text(b, "Label", label, -30, size + 2, size + 60, 20, 15, P.text, T.CENTER, "title") end
	local sc = T.new("UIScale", {}, b)
	b.MouseEnter:Connect(function() st.Color = opts.hover or P.accent; T.tween(sc, .14, { Scale = 1.1 }, Enum.EasingStyle.Back) end)
	b.MouseLeave:Connect(function() st.Color = opts.stroke or P.line; T.tween(sc, .14, { Scale = 1 }, Enum.EasingStyle.Quad) end)
	b.MouseButton1Down:Connect(function() T.tween(sc, .06, { Scale = .9 }, Enum.EasingStyle.Quad) end)
	b.MouseButton1Up:Connect(function() T.tween(sc, .24, { Scale = 1 }, Enum.EasingStyle.Back) end)
	b.Activated:Connect(function()
		if b:GetAttribute("Disabled") then T.som("ui_erro"); T.shake(b, 5); return end
		T.som(opts.sound or "ui_click")
		if fn then fn() end
	end)
	return b
end

function T.iconButton(p,name,key,x,y,size,fn,opts)
 opts=opts or {}
 local b=T.button(p,name,"",x,y,size,size,P.neutral,fn,opts)
 local isz=math.floor(size*(opts.iconScale or .68))
 T.icon(b.Face,key,(size-isz)/2,(size-isz)/2,isz,isz)
 return b
end

-- fechar: cristal vermelho (losango) com X. Assinatura visual do jogo.
function T.closeButton(p,x,y,size,fn)
 size=math.max(size,math.ceil(44/math.max(T.uiScale,.5)))
 if p.Size.X.Offset>0 then x=math.min(x,p.Size.X.Offset-size-12) end
 local b=T.new("TextButton",{Name="Close",Text="",BackgroundTransparency=1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(size,size),ZIndex=10},p)
 local face=T.frame(b,"Face",size*.14,size*.14,size*.72,size*.72,WHITE,0)
 T.corner(face,size).CornerRadius=UDim.new(.5,0);T.stroke(face,P.ink,2)
 T.gradient(face,rgb(244,61,72),rgb(119,11,20),90)
 local inset=T.frame(face,"InnerRim",2,2,size*.72-4,size*.72-4,nil,1);T.corner(inset,size).CornerRadius=UDim.new(.5,0);T.stroke(inset,rgb(255,105,104),1,.3)
 T.text(b,"X","×",0,-1,size,size,math.floor(size*.57),P.text,T.CENTER,"heavy",1.5).ZIndex=11
 T.bindInteraction(b,fn,{sound="ui_fechar",hoverScale=1.04})
 T.hint(b,"Fechar · Esc / B","below")
 return b
end

function T.section(p, value, x, y, w, col, _icon, right)
	col = col or P.accent
	local stacked = right and w < 440
	T.text(p, "SectionPip", "◆", x, y, 18, 26, 17, col, T.CENTER, "heavy", 1.5)
	T.text(p, "Section", value, x + 24, y, w - 24 - (right and not stacked and 180 or 0), 26, 19, P.text, T.LEFT, "title")
	if right then T.text(p, "SectionRight", right, stacked and x + 24 or x + w - 180, stacked and y + 27 or y, stacked and w - 24 or 180, 26, 15, P.text2, stacked and T.LEFT or T.RIGHT, "title") end
	local line = T.frame(p, "SectionRule", x, y + (stacked and 56 or 31), w, 2, col, 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ kp(0, 0), kp(.6, .75), kp(1, 1) }) }, line)
	return stacked and 66 or 42
end

-- título centralizado com linhas dos dois lados ("—— Bundles ——")
function T.sectionCenter(p, value, x, y, w, col)
	local tw = math.min(w * .6, TextService:GetTextSize(value, 22, Enum.Font.GothamBold, Vector2.new(1000, 40)).X + 20)
	T.text(p, "SectionTitle", value, x + (w - tw) / 2, y, tw, 30, 22, P.text, T.CENTER, "title")
	for i, side in ipairs({ -1, 1 }) do
		local lw = (w - tw) / 2 - 30
		local lx = side < 0 and x + 10 or x + (w + tw) / 2 + 20
		local line = T.frame(p, "SectionLine" .. i, lx, y + 14, lw, 2, col or P.text2, 0)
		T.new("UIGradient", { Transparency = NumberSequence.new(side < 0 and { kp(0, 1), kp(1, .1) } or { kp(0, .1), kp(1, 1) }) }, line)
	end
	return 42
end

function T.progress(p, name, x, y, w, h, frac, col, opts)
	opts = opts or {}
	frac = math.clamp(tonumber(frac) or 0, 0, 1)
	col = col or P.accent
	local track = T.frame(p, name, x, y, w, h, opts.track or P.bg0, opts.trackAlpha or 0)
	T.corner(track, math.min(4, math.floor(h / 2)))
	if opts.stroke ~= false then T.stroke(track, P.ink, 2); local edge=T.frame(track,"InnerEdge",1,1,w-2,h-2,nil,1);T.corner(edge,4);T.stroke(edge,col:Lerp(WHITE,.22),1,.32) end
	local inset = h >= 12 and 2 or 1
	local ih = h - inset * 2
	local fill = T.frame(track, "Fill", inset, inset, math.max(1, (w - inset * 2) * frac), ih, WHITE, 0)
	T.corner(fill, math.min(3, math.floor(ih / 2)))
	local g = T.gradient(fill, col:Lerp(WHITE,.23), col:Lerp(P.ink,.24),90)
	g.Name = "Tint"
	local shine = T.frame(fill, "Shine", 2, 1, 0, math.max(1, math.floor(ih * .35)), WHITE, .65)
	shine.Size = UDim2.new(1, -4, 0, math.max(1, math.floor(ih * .35)))
	T.corner(shine, 3)
	fill.Visible = frac > 0
	track:SetAttribute("Inset", inset)
	if opts.segments then
		for i = 1, opts.segments - 1 do
			T.frame(track, "Seg" .. i, math.floor(w * i / opts.segments), 0, 2, h, INK, .35)
		end
	end
	if opts.text then
		T.text(track, "Value", opts.text, 8, 0, w - 16, h, opts.textSize or math.min(16, h - 2), P.text, opts.align or T.CENTER, "title")
	end
	return track, fill
end

function T.setProgress(track, frac, col, time)
	local fill = track and track:FindFirstChild("Fill")
	if not fill then return end
	frac = math.clamp(tonumber(frac) or 0, 0, 1)
	local inset = track:GetAttribute("Inset") or 2
	local ih = fill.Size.Y.Offset
	local target = UDim2.fromOffset(math.max(1, (track.Size.X.Offset - inset * 2) * frac), ih)
	fill.Visible = frac > 0
	if col then local g = fill:FindFirstChild("Tint"); if g then g.Color = ColorSequence.new(col:Lerp(WHITE,.23), col:Lerp(P.ink,.24)) end end
	if time and time > 0 then T.tween(fill, time, { Size = target }, Enum.EasingStyle.Quint) else fill.Size = target end
end

-- Abas planas: rótulo fixo, wash discreto e linha de seleção.
-- O chamador controla a largura total e a quantidade de abas visíveis.
function T.tabs(p,name,x,y,w,h,items,current,col,onPick,opts)
 col=col or P.violet
 local bar=T.frame(p,name,x,y,w,h,P.ink,1)
 if #items==0 then return bar end
 local gap=8
 local tw=(w-gap*(#items-1))/#items
 for i,it in ipairs(items)do
  local selected=it.id==current
  local b=T.new("TextButton",{Name="Tab_"..tostring(it.id),Text="",BackgroundTransparency=1,BorderSizePixel=0,Position=UDim2.fromOffset((i-1)*(tw+gap),0),Size=UDim2.fromOffset(tw,h)},bar)
  b:SetAttribute("Selected",selected)
  local face=T.frame(b,"Face",0,0,tw,h,WHITE,0);T.corner(face,4)
  T.gradient(face,selected and col or P.bg3,selected and col:Lerp(P.ink,.48) or P.bg0,90)
  T.stroke(face,selected and col:Lerp(WHITE,.35) or P.lineSoft,1)
  if selected then T.frame(b,"SelectedRule",2,h-2,tw-4,1,col:Lerp(WHITE,.3),0)end
  T.text(face,"Caption",it.label,8,0,tw-16,h-3,opts and opts.textSize or 22,P.text,T.CENTER,"title",1.5)
  T.bindInteraction(b,function()if not it.locked then onPick(it.id)end end,{sound="ui_tab",hoverScale=1})
  if it.badge and it.badge~=0 and it.badge~="" then T.badge(b,tw-25,-5,it.badge,P.success)end
  if it.locked then T.setEnabled(b,false)end
 end
 return bar
end

-- badge de cristal (losango) com número ou "!"
function T.badge(p, x, y, value, col)
	local f = T.frame(p, "Badge", x, y, 30, 30, nil, 1)
	f.ZIndex = 9
	local gem = T.new("TextLabel", { Name = "Gem", BackgroundTransparency = 1, Text = "◆", TextScaled = true, FontFace = T.F.heavy,
		TextColor3 = col or P.danger, Size = UDim2.fromScale(1, 1), ZIndex = 9 }, f)
	T.new("UIStroke", { Color = WHITE, Thickness = 2, LineJoinMode = Enum.LineJoinMode.Round }, gem)
	T.text(f, "N", tostring(value), 0, 1, 30, 28, 14, WHITE, T.CENTER, "heavy", 1.6).ZIndex = 10
	return f
end

function T.chip(p, name, value, x, y, h, col, opts)
	opts = opts or {}
	local size = math.max(14, opts.size or math.floor(h * .6))
	-- Medir a mesma família e o mesmo tamanho que serão desenhados.
	local w = opts.w or (TextService:GetTextSize(tostring(value), size, Enum.Font.GothamBlack, Vector2.new(900, 90)).X + (opts.icon and h + 18 or 26))
	local f = T.frame(p, name, x, y, w, h, opts.solid and col or P.bg0, opts.solid and 0 or .2)
	T.corner(f, 5)
	if opts.solid then
		local tn = T.tone(col)
		f.BackgroundColor3 = WHITE
		T.gradient(f, tn.top, tn.bottom)
		T.stroke(f, INK, 2)
	else
		T.stroke(f, col, 2)
	end
	local tx = 11
	if opts.icon then T.icon(f, opts.icon, 2, 0, h, h); tx = h + 4 end
	local labelStroke
	if opts.solid then labelStroke = false end
	T.text(f, "Label", value, tx, 0, w - tx - 10, h, size, opts.solid and P.ink or col, opts.icon and T.LEFT or T.CENTER, "label", labelStroke)
	return f, w
end

function T.toggle(p,name,x,y,on,fn)
 local b=T.new("TextButton",{Name=name,Text="",BackgroundTransparency=1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(70,52)},p)
 local track=T.frame(b,"Track",0,8,70,36,on and P.accent:Lerp(P.bg0,.35) or P.bg0,0)
 T.corner(track,12);T.stroke(track,P.lineSoft,1)
 local knob=T.frame(track,"Knob",on and 38 or 4,4,28,28,P.text,0);T.corner(knob,9)
 local state=on
 b:SetAttribute("Checked",on)
 T.bindInteraction(b,function()
  state=not state;b:SetAttribute("Checked",state)
  T.tween(knob,.15,{Position=UDim2.fromOffset(state and 38 or 4,4)})
  T.tween(track,.15,{BackgroundColor3=state and P.accent:Lerp(P.bg0,.35) or P.bg0})
  if fn then fn(state) end
 end,{sound="ui_toggle"})
 return b
end

function T.input(p, name, x, y, w, h, placeholder, value, opts)
	opts = opts or {}
	local field = T.frame(p, name .. "Field", x, y, w, h, P.bg0, .1)
	T.corner(field, 3)
	local st = T.stroke(field, P.lineSoft, 1)
	local left = 14
	if opts.search then
		local ring = T.frame(field, "Lens", 16, h / 2 - 11, 16, 16, WHITE, 1)
		T.corner(ring, 8); T.stroke(ring, P.text2, 2)
		local handle = T.new("Frame", { Name = "Handle", BackgroundColor3 = P.text2, BorderSizePixel = 0, Rotation = 45,
			Position = UDim2.fromOffset(31, h / 2 + 7), Size = UDim2.fromOffset(9, 3.5), AnchorPoint = Vector2.new(.5, .5) }, field)
		T.corner(handle, 2)
		left = 44
	end
	local box = T.new("TextBox", { Name = name, Text = value or "", PlaceholderText = placeholder or "", ClearTextOnFocus = false,
		BackgroundTransparency = 1, Position = UDim2.fromOffset(left, 0), Size = UDim2.fromOffset(w - left - 10, h),
		TextColor3 = P.text, PlaceholderColor3 = P.text3, FontFace = T.F.body, TextSize = math.max(14, opts.size or 20), TextScaled = false,
		TextXAlignment = opts.align or T.LEFT, TextTruncate = Enum.TextTruncate.AtEnd, BorderSizePixel = 0 }, field)
	box.Focused:Connect(function() st.Color = P.accent end)
	box.FocusLost:Connect(function() st.Color = P.lineSoft end)
	return box, field
end

function T.lock(p, x, y, size, col)
	col = col or P.text2
	local g = T.frame(p, "Lock", x, y, size, size, nil, 1)
	local sh = T.frame(g, "Shackle", size * .27, size * .04, size * .46, size * .58, nil, 1)
	T.corner(sh, size); T.stroke(sh, col, math.max(2, size * .12))
	local body = T.frame(g, "Body", size * .12, size * .42, size * .76, size * .54, col, 0)
	T.corner(body, math.max(2, math.floor(size * .12)))
	T.stroke(body, INK, math.max(1.5, size * .06))
	local hole = T.frame(body, "Hole", size * .33, size * .15, size * .1, size * .2, INK, 0)
	T.corner(hole, 2)
	return g
end

-- compat: identidade de raridade num frame existente (borda + brilho inferior)
function T.rarityFrame(f,key,opts)
 opts=opts or {}
 local r=T.rar(key)
 local st=f:FindFirstChildOfClass("UIStroke") or T.stroke(f,P.lineSoft,1)
 st.Color=opts.selected and P.accent or P.lineSoft
 st.Thickness=opts.selected and 2 or 1
 local mark=f:FindFirstChild("RarityMark")
 if not mark then mark=T.frame(f,"RarityMark",0,0,0,3,r.cor,0);mark.Position=UDim2.new(0,1,1,-4);mark.Size=UDim2.new(1,-2,0,3) end
 mark.BackgroundColor3=r.cor
 return st,r
end

function T.statRow(p, name, x, y, w, h, icon, labelText, valueText, col, grade)
	local row = T.frame(p, name, x, y, w, h, WHITE, 0)
	T.corner(row, 10)
	T.new("UIGradient", { Color = ColorSequence.new(col:Lerp(INK, .35), P.bg1), Transparency = NumberSequence.new({ kp(0, .05), kp(1, .1) }) }, row)
	T.stroke(row, col:Lerp(INK, .45), 2)
	local tx = 14
	if icon then T.statIcon(row, icon, 8, 5, h - 10, h - 10); tx = h + 2 end
	T.text(row, "Label", labelText, tx, 0, w * .64 - tx, h, math.min(22, h * .48), P.text, T.LEFT, "title")
	local vw = grade and w * .36 - h - 6 or w * .36 - 14
	T.text(row, "Value", valueText, w * .64, 0, vw, h, math.min(26, h * .56), col:Lerp(WHITE, .25), T.RIGHT, "title")
	if grade then
		local g = T.frame(row, "Grade", w - h + 2, 5, h - 10, h - 10, P.info, 0)
		T.corner(g, 6)
		T.stroke(g, INK, 2)
		T.text(g, "G", grade, 0, 0, h - 10, h - 10, 18, WHITE, T.CENTER, "heavy")
	end
	return row
end

function T.stat(p, name, x, y, w, labelText, valueText, col, h)
	h = h or 32
	local row = T.frame(p, name, x, y, w, h, P.bg0, .3)
	T.corner(row, 8)
	T.text(row, "Label", labelText, 12, 0, w * .5 - 18, h, 16, P.text2, T.LEFT, "title")
	T.text(row, "Value", valueText, w * .5, 0, w * .5 - 12, h, 17, col or P.text, T.RIGHT, "title")
	return row
end

-- ================================================================ TOOLTIP
local tip = { layer = nil, scale = nil, token = nil, frame = nil, guard = nil }
function T.setTooltipLayer(layer, getScale) tip.layer, tip.scale = layer, getScale end
-- guard(o) -> false bloqueia a dica (ex.: elemento do HUD coberto por uma janela aberta)
function T.setTooltipGuard(fn) tip.guard = fn end
local function hideTip()
	tip.token = nil
	if tip.frame then tip.frame:Destroy(); tip.frame = nil end
end
T.hideTooltip = hideTip
function T.hint(o,value,side)
 local function show()
  local token={};tip.token=token
  task.delay(.28,function()
   if tip.token~=token or not o.Parent or not tip.layer or (tip.guard and not tip.guard(o)) then return end
   if tip.frame then tip.frame:Destroy() end
   local s=tip.scale and tip.scale() or 1
   local vw,vh=tip.layer.AbsoluteSize.X/s,tip.layer.AbsoluteSize.Y/s
   local text=type(value)=="function" and value() or value
   local width=math.min(360,vw-24)
   local raw=tostring(text):gsub("<[^>]+>","")
   local bounds=TextService:GetTextSize(raw,15,Enum.Font.BuilderSansBold,Vector2.new(width-24,1000))
   local height=math.min(vh-24,math.max(40,bounds.Y+20))
   local f=T.panel(tip.layer,"Tooltip",0,0,width,height,{bg=P.bg0})
   f.ZIndex=100
   local t=T.new("TextLabel",{Name="Text",BackgroundTransparency=1,Position=UDim2.fromOffset(12,8),Size=UDim2.fromOffset(width-24,height-16),FontFace=T.F.body,TextSize=15,TextWrapped=true,RichText=true,TextColor3=P.text,Text=tostring(text),TextXAlignment=Enum.TextXAlignment.Left,ZIndex=101},f)
   local rel=(o.AbsolutePosition-tip.layer.AbsolutePosition)/s
   local size=o.AbsoluteSize/s
   local x=rel.X+size.X+8;local y=rel.Y
   if side=="above" then x=rel.X+(size.X-width)/2;y=rel.Y-height-8
   elseif side=="below" then x=rel.X+(size.X-width)/2;y=rel.Y+size.Y+8
   elseif side=="left" then x=rel.X-width-8;y=rel.Y end
   f.Position=UDim2.fromOffset(math.clamp(x,12,math.max(12,vw-width-12)),math.clamp(y,12,math.max(12,vh-height-12)))
   tip.frame=f
  end)
 end
 o.MouseEnter:Connect(show);o.SelectionGained:Connect(show)
 o.MouseLeave:Connect(hideTip);o.SelectionLost:Connect(hideTip)
 o.Destroying:Connect(function() if tip.frame then hideTip() end end)
end

-- ================================================================ DADOS
function T.format(n)
	return require(RS.Config).formatar(n)
end

function T.clock(seconds)
	seconds = math.max(0, math.floor(seconds))
	local h = math.floor(seconds / 3600)
	local m = math.floor(seconds % 3600 / 60)
	local s = seconds % 60
	if h > 0 then return string.format("%dh %02dm %02ds", h, m, s) end
	return string.format("%d:%02d", m, s)
end

-- prévia de item: retrato 2D (pets), ViewportFrame (picaretas/rigs) ou miniatura (hats)
-- Models are rendered at their native proportions. Body bounds avoid remote
-- accessory handles in imported rigs changing the camera framing.
function T.characterViewport(p, ids, x, y, w, h, opts)
 opts=opts or {}
 if type(ids)=="string" then ids={ids} end
 local v=T.new("ViewportFrame",{Name="CharacterViewport",Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(w,h),BackgroundTransparency=1,BorderSizePixel=0,Ambient=rgb(202,199,221),LightColor=rgb(255,244,228),LightDirection=Vector3.new(-.35,-.6,1),ImageColor3=opts.dim and rgb(74,70,85) or WHITE},p)
 local world=T.new("WorldModel",{},v)
 local cam=T.new("Camera",{FieldOfView=28},v);v.CurrentCamera=cam
 local folder=RS:FindFirstChild("PreviewModelos");folder=folder and folder:FindFirstChild("Pets")
 local animatedModels={}
 local count=#ids;local minV=Vector3.new(math.huge,math.huge,math.huge);local maxV=-minV
 -- Articulated display poses, evaluated in the joint hierarchy. No floating whole-body loop.
 local profiles={
  muzan={right=3,left=-22,re=9,le=88,turn=-7,head=9},
  goku={right=-27,left=-19,re=58,le=48,turn=7,head=-7},
  vegeta={right=-23,left=-28,re=63,le=57,turn=-8,head=8},
  saitama={right=4,left=-8,re=12,le=32,turn=-4,head=5},
  tanjiro={right=-19,left=-12,re=41,le=33,turn=6,head=-6},
 }
 local function poseFor(id)
  local p=profiles[id] or {right=4,left=-12,re=16,le=36,turn=-5,head=6}
  return {RightShoulder=Vector3.new(p.right,0,-7),LeftShoulder=Vector3.new(p.left,0,9),RightElbow=Vector3.new(p.re,0,0),LeftElbow=Vector3.new(p.le,0,0),Waist=Vector3.new(-1,p.turn,0),Neck=Vector3.new(-2,p.head,0)}
 end
 for index,id in ipairs(ids) do
  local original=folder and folder:FindFirstChild(id)
  if original then
   local model=original:Clone();model.Name=id
   local poses=poseFor(id)
   local root=model:FindFirstChild("HumanoidRootPart")
   for _,d in ipairs(model:GetDescendants()) do
    if d:IsA("LuaSourceContainer") or d:IsA("ParticleEmitter") or d:IsA("Trail") or d:IsA("Sound") then d:Destroy()
    elseif d:IsA("BasePart") then
     d.Anchored=true;d.CanCollide=false;d.CanTouch=false;d.CanQuery=false

    end
   end
   model:PivotTo(CFrame.new())
   local head=model:FindFirstChild("Head")
   local lf=model:FindFirstChild("LeftFoot") or model:FindFirstChild("Left Leg")
   local rf=model:FindFirstChild("RightFoot") or model:FindFirstChild("Right Leg")
   local top=head and head.Position.Y+head.Size.Y*.5 or 2.5
   local bottom=math.min(lf and lf.Position.Y-lf.Size.Y*.5 or -3,rf and rf.Position.Y-rf.Size.Y*.5 or -3)
   local height=math.max(3,top-bottom)
   local factor=5.6/height
   model:ScaleTo(model:GetScale()*factor)
   local offset=((count+1)/2-index)*(count>1 and 2.75 or 0)
   local yaw=opts.yaw or (count>1 and (index-(count+1)/2)*-.18 or .12)
   local z=count>1 and (index==math.ceil(count/2) and -.65 or .25) or 0
   model:PivotTo(CFrame.new(offset,-bottom*factor,z)*CFrame.Angles(0,yaw,0))
   model.Parent=world
   -- Anchor the display rig and solve FK explicitly. AnimationConstraint simulation is not
   -- reliable in every ViewportFrame; evaluating both rig formats produces the same pose.
   local unordered={}
   for _,joint in ipairs(model:GetDescendants()) do
    local p0,p1,c0,c1
    if joint:IsA("Motor6D") or joint:IsA("Weld") then
     p0,p1,c0,c1=joint.Part0,joint.Part1,joint.C0,joint.C1
    elseif joint:IsA("AnimationConstraint") and joint.Attachment0 and joint.Attachment1 then
     p0,p1,c0,c1=joint.Attachment0.Parent,joint.Attachment1.Parent,joint.Attachment0.CFrame,joint.Attachment1.CFrame
     joint.Enabled=false
    end
    if p0 and p1 and p0:IsA("BasePart") and p1:IsA("BasePart") then
     local a=poses[joint.Name] or Vector3.zero
     table.insert(unordered,{name=joint.Name,p0=p0,p1=p1,c0=c0,c1=c1:Inverse(),pose=CFrame.Angles(math.rad(a.X),math.rad(a.Y),math.rad(a.Z))})
    end
   end
   local known={[root]=true};local ordered={}
   for _=1,20 do
    local progress=false
    for i=#unordered,1,-1 do
     local j=unordered[i]
     if known[j.p0] then known[j.p1]=true;table.insert(ordered,j);table.remove(unordered,i);progress=true end
    end
    if not progress then break end
   end
   -- Accessory meshes follow their attachment welds after their parent bone.
   for _,j in ipairs(ordered) do j.p1.CFrame=j.p0.CFrame*j.c0*j.pose*j.c1 end
   table.insert(animatedModels,{model=model,root=root,joints=ordered,phase=index*.85})
   local range=Vector3.new(2.45,3.25,1.6)
   local center=Vector3.new(offset,2.95,z)
   local lo,hi=center-range,center+range
   minV=Vector3.new(math.min(minV.X,lo.X),math.min(minV.Y,lo.Y),math.min(minV.Z,lo.Z))
   maxV=Vector3.new(math.max(maxV.X,hi.X),math.max(maxV.Y,hi.Y),math.max(maxV.Z,hi.Z))
  end
 end
 if minV.X==math.huge then
  T.text(v,"Unavailable","Modelo indisponível",8,h/2-15,w-16,30,16,T.P.text2,T.CENTER,"body",false)
  return v
 end
 local center=(minV+maxV)/2
 local size=maxV-minV
 if opts.fullBody==false then center+=Vector3.new(0,.8,0);size=Vector3.new(size.X,size.Y*.75,size.Z) end
 local angle=0
 local function frameCamera()
  local aspect=math.max(.2,v.AbsoluteSize.X/math.max(1,v.AbsoluteSize.Y))
  if v.AbsoluteSize.Y<2 then aspect=math.max(.2,w/math.max(1,h)) end
  local dist=math.max(size.Y*.5/math.tan(math.rad(14)),size.X*.5/(math.tan(math.rad(14))*aspect))*(opts.padding or 1.04)
  cam.CFrame=CFrame.lookAt(center+Vector3.new(math.sin(angle)*dist,dist*.015,-math.cos(angle)*dist),center)
 end
 frameCamera();v:GetPropertyChangedSignal("AbsoluteSize"):Connect(frameCamera)
 v.ImageTransparency=1;task.delay(.18,function() if v.Parent then T.tween(v,.16,{ImageTransparency=0}) end end)
 if opts.interactive then
  v.Active=true
  local inputService=game:GetService("UserInputService")
  local dragging,lastX=false,0
  v.InputBegan:Connect(function(input)
   if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then dragging=true;lastX=input.Position.X end
  end)
  local changed=inputService.InputChanged:Connect(function(input)
   if dragging and (input.UserInputType==Enum.UserInputType.MouseMovement or input.UserInputType==Enum.UserInputType.Touch) then
    angle+=(input.Position.X-lastX)*.009;lastX=input.Position.X;frameCamera()
   end
  end)
  local ended=inputService.InputEnded:Connect(function(input)
   if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then dragging=false end
  end)
  v.Destroying:Once(function() changed:Disconnect();ended:Disconnect() end)
 end
 local elapsed=0
 local idle=Run.RenderStepped:Connect(function(dt)
  if not v.Visible or v.AbsoluteSize.Y<5 then return end
  local ancestor=v.Parent
  while ancestor and ancestor:IsA("GuiObject") do if not ancestor.Visible then return end;ancestor=ancestor.Parent end
  elapsed+=dt
  for _,entry in ipairs(animatedModels) do
   local t=elapsed+entry.phase
   local motion=T.motionEnabled()
   local breath=motion and math.sin(t*1.45) or 0
   local glance=motion and math.sin(t*.34)*math.sin(t*.34) or 0
   for _,j in ipairs(entry.joints) do
    local delta=CFrame.identity
    if j.name=="Waist" then delta=CFrame.Angles(math.rad(breath*.65),0,0)
    elseif j.name=="Neck" then delta=CFrame.Angles(math.rad(-breath*.35),math.rad(glance*3.5),0)
    elseif j.name=="LeftShoulder" then delta=CFrame.Angles(math.rad(breath*.8),0,math.rad(breath*.3))
    elseif j.name=="RightShoulder" then delta=CFrame.Angles(math.rad(breath*.55),0,math.rad(-breath*.3))
    elseif j.name=="LeftElbow" then delta=CFrame.Angles(math.rad(breath*.9),0,0) end
    if j.p0.Parent and j.p1.Parent then j.p1.CFrame=j.p0.CFrame*j.c0*j.pose*delta*j.c1 end
   end
  end
 end)
 v.Destroying:Once(function() idle:Disconnect() end)
 v:SetAttribute("IdleAnimation","ArticulatedDisplayPose")
 v:SetAttribute("ModelIds",table.concat(ids,","))
 return v
end


function T.preview(p, kind, id, x, y, w, h, animated, dim)
	local model
	if kind == "pet" then
		local arte = require(RS.Config).PetArte
		arte = arte and arte[id]
		if arte then
			local img = T.image(p, "Retrato_" .. id, animated and (arte.corpo or arte.busto) or (arte.busto or arte.corpo), x, y, w, h, dim and rgb(60, 58, 80) or nil)
			if animated then
				img.Position = UDim2.fromOffset(x, y + 3)
				continuousTween(img, img, TweenInfo.new(2.2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
					{ Position = UDim2.fromOffset(x, y - 3) }, { Position = UDim2.fromOffset(x, y) },
					function(enabled) if enabled then img.Position = UDim2.fromOffset(x, y + 3) end end)
			end
			return img
		end
		local folder = RS:FindFirstChild("PreviewModelos")
		folder = folder and folder:FindFirstChild("Pets")
		model = folder and folder:FindFirstChild(id)
	elseif kind == "pickaxe" then
		local folder = RS:FindFirstChild("ExpeditionPreviews")
		folder = folder and folder:FindFirstChild("Pickaxes")
		local def = require(RS.Config).picaretaPorId(id)
		model = folder and folder:FindFirstChild(def and def.modelo or id)
	end
	if not model then
		if kind == "hat" then
			local aid = require(RS.Config).HatAssets[id]
			if aid then return T.image(p, "ItemArt", "rbxthumb://type=Asset&id=" .. aid .. "&w=420&h=420", x, y, w, h, dim and rgb(60, 58, 80) or nil) end
		end
		local s = math.min(w, h)
		return T.icon(p, kind == "pickaxe" and "pickaxe" or "items", x + (w - s) / 2, y + (h - s) / 2, s, s)
	end
	local v = T.new("ViewportFrame", { Name = "Preview_" .. id, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(w, h), BackgroundTransparency = 1,
		Ambient = dim and rgb(80, 80, 90) or rgb(225, 225, 235), LightColor = rgb(255, 246, 235), LightDirection = Vector3.new(-.6, -.8, -1),
		ImageColor3 = dim and rgb(95, 95, 110) or WHITE }, p)
	local world = T.new("WorldModel", {}, v)
	local clone = model:Clone()
	for _, d in ipairs(clone:GetDescendants()) do
		if d:IsA("LuaSourceContainer") or d:IsA("ParticleEmitter") or d:IsA("Trail") then d:Destroy()
		elseif d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false end
	end
	clone.Parent = world
	local cam = T.new("Camera", { FieldOfView = 32 }, v)
	v.CurrentCamera = cam
	local orient
	if clone:FindFirstChildOfClass("Humanoid") then
		clone:PivotTo(CFrame.new())
		v.LightDirection = Vector3.new(-.45, -.75, .9)
		if not dim then v.Ambient = rgb(200, 200, 210) end
		local head = clone:FindFirstChild("Head")
		local torso = clone:FindFirstChild("UpperTorso") or clone:FindFirstChild("Torso")
		local lower = clone:FindFirstChild("LowerTorso") or torso
		local top = head and head.Position.Y + head.Size.Y / 2 or 0
		if head then
			for _, acc in ipairs(clone:GetChildren()) do
				local handle = acc:IsA("Accessory") and acc:FindFirstChild("Handle")
				if handle and not handle:FindFirstChildOfClass("WrapLayer") and handle.Position.Y > head.Position.Y - head.Size.Y / 2 then
					top = math.max(top, handle.Position.Y + handle.Size.Y * .4)
				end
			end
		end
		local bottom
		if animated then bottom = lower and lower.Position.Y - lower.Size.Y / 2 or top - 4
		else bottom = torso and torso.Position.Y - torso.Size.Y * .05 or top - 2.5 end
		local height = math.max(top - bottom, .5)
		local width = torso and torso.Size.X * (animated and 2.1 or 1.7) or height
		local center = Vector3.new(0, (top + bottom) / 2, 0)
		local tanHalf = math.tan(math.rad(16))
		local dist = math.max(height * .5 / tanHalf, width * .5 / (tanHalf * math.max(w / h, .3))) * 1.05
		orient = function(angle)
			cam.CFrame = CFrame.lookAt(center + Vector3.new(math.sin(angle) * dist, height * .04, -math.cos(angle) * dist), center)
		end
	else
		local cf, sz = clone:GetBoundingBox()
		clone:PivotTo(cf:Inverse() * clone:GetPivot())
		cf, sz = clone:GetBoundingBox()
		local dist = math.max(sz.Y, sz.X / math.max(w / h, .4)) * .5 / math.tan(math.rad(16)) + sz.Z * .55
		dist = math.max(dist, 2)
		orient = function(angle)
			cam.CFrame = CFrame.lookAt(cf.Position + Vector3.new(math.sin(angle), .12, math.cos(angle)) * dist, cf.Position)
		end
	end
	orient(kind=="pet" and 0 or .3)
	if animated and T.motionEnabled() then
		local age = 0
		local conn
		conn = Run.RenderStepped:Connect(function(dt)
			if not v.Parent then conn:Disconnect(); return end
			if not T.motionEnabled() then return end
			local ancestor=v
			while ancestor and ancestor~=game do
			 if ancestor:IsA("GuiObject") and not ancestor.Visible then return end
			 if ancestor:IsA("ScreenGui") and not ancestor.Enabled then return end
			 ancestor=ancestor.Parent
			end
			age += dt
			orient((kind=="pet" and 0 or .3) + math.sin(age * .32) * .25)
		end)
		v.Destroying:Once(function() conn:Disconnect() end)
	end
	return v
end


-- Componentes compostos compartilhados. Não criam conexões globais por instância.
function T.emptyState(p,name,title,description,x,y,w,h,actionLabel,onAction)
 local f=T.frame(p,name,x,y,w,h,nil,1)
 T.text(f,"Symbol","◇",0,math.max(8,h*.18-20),w,40,32,P.accent,T.CENTER,"heavy",false)
 T.text(f,"Title",title,12,h*.38,w-24,30,20,P.text,T.CENTER,"title",false)
 T.para(f,"Description",description or "",20,h*.38+36,w-40,50,15,P.text2,T.CENTER,"body")
 if actionLabel and onAction then T.button(f,"Action",actionLabel,math.max(0,(w-240)/2),math.min(h-48,h*.38+96),math.min(240,w),44,P.accent,onAction) end
 return f
end
function T.loading(p,name,x,y,w,h)
 local f=T.frame(p,name,x,y,w,h,nil,1)
 T.text(f,"Title","Carregando...",0,h*.4,w,32,20,P.text,T.CENTER,"title",false)
 T.progress(f,"Track",w*.25,h*.4+46,w*.5,4,.45,P.accent)
 return f
end
function T.dropdown(p,name,x,y,w,h,items,current,onPick,opts)
 opts=opts or {}
 local label=opts.label or ""
 for _,it in ipairs(items) do if it.id==current then label=it.label end end
 local b=T.button(p,name,label,x,y,w,h,P.neutral,nil,{size=opts.size or 14,align=T.LEFT})
 local caption=b.Face:FindFirstChild("Caption");if caption then caption.Size=UDim2.fromOffset(w-42,h) end
 for i,rot in ipairs({45,-45}) do T.new("Frame",{Name="Chevron"..i,BackgroundColor3=P.text2,BorderSizePixel=0,Size=UDim2.fromOffset(7,2),Position=UDim2.fromOffset(w-24+(i-1)*4,h/2-1),Rotation=rot},b.Face) end
 local panel,shield
 local function close()
  if panel then panel:Destroy();panel=nil end
  if shield then shield:Destroy();shield=nil end
 end
 b.Activated:Connect(function()
  if b:GetAttribute("Disabled") then return end
  if panel then close();return end
  T.hideTooltip()
  local host=tip.layer or p
  local s=tip.scale and tip.scale() or 1
  local vw,vh=host.AbsoluteSize.X/s,host.AbsoluteSize.Y/s
  local rel=(b.AbsolutePosition-host.AbsolutePosition)/s
  local rowH=math.max(40,math.ceil(44/math.max(s,.5)))
  local ph=math.min(#items*rowH+8,vh-32)
  local pw=math.max(w,190)
  local px=math.clamp(rel.X,8,math.max(8,vw-pw-8))
  local py=rel.Y+h+4
  if py+ph>vh-8 then py=math.max(8,rel.Y-ph-4) end
  shield=T.new("TextButton",{Name="DropdownBackdrop",Text="",BackgroundTransparency=1,Size=UDim2.fromScale(1,1),ZIndex=130},host)
  shield.Activated:Connect(close)
  panel=T.panel(host,"Options",px,py,pw,ph,{bg=P.bg1})
  panel.ZIndex=131
  local list=T.scroll(panel,"OptionsList",4,4,pw-8,ph-8)
  list.CanvasSize=UDim2.fromOffset(0,#items*rowH)
  for i,it in ipairs(items) do
   T.button(list,"Option_"..tostring(it.id),(it.id==current and "✓ " or "")..it.label,0,(i-1)*rowH,pw-16,rowH-2,it.id==current and P.accent or P.neutral,function()
    close();onPick(it.id)
   end,{size=15,align=T.LEFT})
  end
 end)
 b.Destroying:Connect(close)
 return b
end




-- Abertura visual; o resultado já foi decidido pelo servidor antes desta chamada.
function T.starOpening(parent,w,h,complete)
 local overlay=T.new("CanvasGroup",{Name="StarOpening",Size=UDim2.fromOffset(w,h),BackgroundColor3=P.ink,BackgroundTransparency=.25,ZIndex=80,Active=true},parent)
 local shield=T.new("TextButton",{Name="Skip",Text="",Size=UDim2.fromScale(1,1),BackgroundTransparency=1,ZIndex=80},overlay)
 local size=math.min(290,h*.64)
 local star=T.icon(overlay,"summon",(w-size)/2,(h-size)/2,size,size);star.ZIndex=81
 star.AnchorPoint=Vector2.new(.5,.5);star.Position=UDim2.fromScale(.5,.5)
 local sc=T.new("UIScale",{Scale=.12},star)
 local burst=T.frame(overlay,"Flash",0,0,w,h,WHITE,1);burst.ZIndex=82
 local finished=false
 local function finish()
  if finished then return end;finished=true
  overlay:Destroy();if complete then complete() end
 end
 T.bindInteraction(shield,finish,{sound=false})
 overlay.Destroying:Once(function() finished=true end)
 if not T.motionEnabled() then task.delay(.15,finish);return overlay end
 T.tween(sc,.30,{Scale=1},Enum.EasingStyle.Back)
 T.tween(star,.62,{Rotation=22},Enum.EasingStyle.Quad)
 task.delay(.64,function()
  if finished then return end
  T.tween(star,.18,{Rotation=-18});T.tween(sc,.18,{Scale=.76})
  task.delay(.19,function()
   if finished then return end
   T.tween(sc,.24,{Scale=2.1});T.tween(star,.22,{ImageTransparency=1,Rotation=42})
   T.tween(burst,.10,{BackgroundTransparency=.25})
   task.delay(.13,function() if not finished then T.tween(overlay,.18,{GroupTransparency=1});task.delay(.19,finish) end end)
  end)
 end)
 return overlay
end

return T


