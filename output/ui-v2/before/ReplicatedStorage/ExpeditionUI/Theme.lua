-- ============================================================================
-- THEME V2.1 · Design System do Anime Mining Simulator ("Crystal Rush")
-- Linguagem: fundo tinta-violeta quase preto, cores saturadas, bordas grossas
-- coloridas, texto pesado com contorno escuro, cards texturizados tingidos pela
-- raridade, faixas inclinadas (energia anime) e cristais (losangos) como assinatura.
-- Toda a UI usa SOMENTE este módulo para cor/fonte/componentes.
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
	ink = rgb(10, 6, 22),      -- contorno de texto e bordas escuras
	bg0 = rgb(9, 7, 20),       -- trilhas, campos, fundo profundo
	bg1 = rgb(17, 13, 34),     -- janelas
	bg2 = rgb(26, 20, 50),     -- painéis internos
	bg3 = rgb(38, 30, 72),     -- cards
	bg4 = rgb(54, 44, 100),    -- hover / elevado
	line = rgb(104, 88, 178),  -- borda forte (violeta)
	lineSoft = rgb(62, 52, 112),
	text = rgb(255, 255, 255),
	text2 = rgb(200, 192, 240),
	text3 = rgb(132, 122, 184),
	accent = rgb(56, 222, 255),   -- cristal / navegação
	gold = rgb(255, 204, 36),     -- moedas / premium
	violet = rgb(168, 84, 255),   -- invocação
	magenta = rgb(236, 64, 196),
	success = rgb(92, 230, 70),   -- comprar / confirmar / resgatar
	danger = rgb(255, 50, 78),
	warning = rgb(255, 146, 24),
	info = rgb(64, 146, 255),
	teal = rgb(24, 222, 168),
	ember = rgb(255, 104, 36),
	pink = rgb(255, 74, 168),
	robux = rgb(92, 230, 70),
	neutral = rgb(78, 68, 132),
}
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
	display = Font.new(GOTHAM, Enum.FontWeight.Heavy, Enum.FontStyle.Italic), -- banners, números grandes
	title = Font.new("rbxasset://fonts/families/FredokaOne.json"),            -- botões, nomes, abas (arredondada)
	label = Font.new("rbxasset://fonts/families/FredokaOne.json"),
	heavy = Font.new(GOTHAM, Enum.FontWeight.Heavy),                           -- títulos retos
	body = Font.new(BUILDER, Enum.FontWeight.Bold),                            -- descrições
	regular = Font.new(BUILDER, Enum.FontWeight.Medium),
}
local STROKED = { display = true, title = true, label = true, heavy = true }
-- equivalentes Enum.Font para medir texto (TextService) e fator de largura (itálico ocupa um pouco mais)
local MEASURE_FONT = { display = Enum.Font.GothamBlack, heavy = Enum.Font.GothamBlack, title = Enum.Font.FredokaOne, label = Enum.Font.FredokaOne,
	body = Enum.Font.BuilderSansBold, regular = Enum.Font.BuilderSansMedium }
local MEASURE_FACTOR = { display = 1.06, heavy = 1.02 }

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
	-- textura dos cards: cristais em mosaico (tileavel)
	pattern = "rbxassetid://70662576263159", patternAntigo = "rbxassetid://86819702987826",
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
	local tw = Tween:Create(o, TweenInfo.new(t, style or Enum.EasingStyle.Quint, dir or Enum.EasingDirection.Out, 0, false, delay or 0), props)
	tw:Play()
	return tw
end

function T.corner(p, r)
	local c = p:FindFirstChildOfClass("UICorner") or T.new("UICorner", {}, p)
	c.CornerRadius = UDim.new(0, r or 10)
	return c
end

function T.stroke(p, col, width, alpha)
	return T.new("UIStroke", { Color = col or P.lineSoft, Thickness = width or 2, Transparency = alpha or 0,
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

-- texto de 1 linha que reduz para caber. Contorno escuro automático nas fontes de destaque.
-- stroke: nil = automático, false = sem contorno, número = espessura
-- TextScaled do Roblox quebra linha sozinho ("LONGE DO / BANNER" minúsculo); aqui o tamanho é medido
-- e aplicado em uma linha só. Texto com quebra (T.para) continua escalado.
-- escala do canvas (UIScale do cliente). Em telas pequenas o texto ganha até +30% para continuar legível.
T.uiScale = 1
local function fitText(t, size, font)
	size = size * math.clamp(1 / math.max(.1, T.uiScale), 1, 1.3)
	-- (TextScaled = true liga TextWrapped sozinho no Roblox; por isso parágrafo é marcado por atributo)
	if t:GetAttribute("Paragraph") then t.TextScaled = true; t.TextWrapped = true; return end
	local raw = t.Text
	if t.RichText then raw = raw:gsub("<[^>]+>", ""):gsub("&lt;", "<"):gsub("&gt;", ">"):gsub("&amp;", "&") end
	local bw, bh = t.Size.X.Offset, t.Size.Y.Offset
	if raw == "" or raw:find("\n") or bw <= 2 or bh <= 2 then t.TextScaled = true; return end
	local ok, bounds = pcall(TextService.GetTextSize, TextService, raw, size, MEASURE_FONT[font] or Enum.Font.FredokaOne, Vector2.new(1e5, 1e5))
	if not ok or bounds.X <= 0 then t.TextScaled = true; return end
	local k = math.min(1, (bw - 2) / (bounds.X * (MEASURE_FACTOR[font] or 1)), bh / math.max(1, bounds.Y))
	t.TextScaled = false
	t.TextWrapped = false
	t.TextSize = math.max(7, math.floor(size * k))
end

function T.text(p, name, value, x, y, w, h, size, col, align, font, stroke)
	font = font or "title"
	size = size or 16
	local t = T.new("TextLabel", {
		Name = name, Text = value or "", Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(math.max(1, w), math.max(1, h)),
		BackgroundTransparency = 1, BorderSizePixel = 0, FontFace = T.F[font] or T.F.title, TextSize = size,
		TextColor3 = col or P.text, TextXAlignment = align or T.LEFT, TextYAlignment = Enum.TextYAlignment.Center,
		TextScaled = false, TextWrapped = false,
	}, p)
	T.new("UITextSizeConstraint", { MinTextSize = 7, MaxTextSize = size }, t)
	local function refit() fitText(t, size, font) end
	refit()
	for _, prop in ipairs({ "Text", "Size", "RichText" }) do t:GetPropertyChangedSignal(prop):Connect(refit) end
	t:GetAttributeChangedSignal("Paragraph"):Connect(refit)
	if stroke == nil and STROKED[font] then stroke = math.clamp(size * .09, 1.3, 3.4) end
	if stroke and stroke ~= false then
		T.new("UIStroke", { Color = INK, Thickness = stroke == true and 1.8 or stroke, LineJoinMode = Enum.LineJoinMode.Round }, t)
	end
	return t
end

function T.para(p, name, value, x, y, w, h, size, col, align, font)
	local t = T.text(p, name, value, x, y, w, h, size, col or P.text2, align, font or "body", false)
	t:SetAttribute("Paragraph", true)
	t.TextYAlignment = Enum.TextYAlignment.Top
	return t
end

function T.image(p, name, id, x, y, w, h, color, alpha)
	return T.new("ImageLabel", { Name = name, Image = id, BackgroundTransparency = 1, Position = UDim2.fromOffset(x, y),
		Size = UDim2.fromOffset(w, h), ImageColor3 = color or WHITE, ImageTransparency = alpha or 0, ScaleType = Enum.ScaleType.Fit }, p)
end

function T.icon(p, key, x, y, w, h)
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
	local id = T.Assets.stat[key]
	if id then return comFallback(T.image(p, "Stat_" .. key, id, x, y, w, h or w), p, ATLAS_EQUIVALENTE[key] or "items", x, y, w, h or w) end
	return T.icon(p, key, x, y, w, h)
end

function T.texture(p, kind, alpha, col, tile)
	local im = T.image(p, "Texture_" .. kind, T.Assets[kind], 0, 0, 0, 0, col, alpha or .8)
	im.Size = UDim2.fromScale(1, 1)
	im.ScaleType = Enum.ScaleType.Tile
	local ts = tile or (kind == "halftone" and 26 or 110)
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
function T.panel(p, name, x, y, w, h, opts)
	opts = opts or {}
	local f = T.frame(p, name, x, y, w, h, opts.bg or P.bg2, opts.alpha or 0)
	T.corner(f, opts.radius or 12)
	if opts.stroke ~= false then T.stroke(f, opts.strokeColor or P.lineSoft, opts.strokeWidth or 2, opts.strokeAlpha or 0) end
	if opts.shade ~= false then T.gradient(f, WHITE, rgb(196, 190, 220)) end
	return f
end

function T.shadow(f, r, off, alpha)
	local s = T.new("Frame", { Name = f.Name .. "Shadow", BackgroundColor3 = INK, BackgroundTransparency = alpha or .4,
		BorderSizePixel = 0, AnchorPoint = f.AnchorPoint, Position = f.Position + UDim2.fromOffset(0, off or 6), Size = f.Size,
		ZIndex = f.ZIndex - 1 }, f.Parent)
	T.corner(s, r or 12)
	return s
end

function T.surface(p, col)
	p.BackgroundColor3 = P.bg3
	T.corner(p, 10)
	T.stroke(p, col or P.line, 2)
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
function T.tile(p, name, x, y, w, h, key, opts)
	opts = opts or {}
	local r = T.rar(key)
	local col = opts.color or r.cor
	local dim = opts.dim
	local f = T.frame(p, name, x, y, w, h, (dim and rgb(40, 38, 56) or col):Lerp(INK, dim and .55 or .7), 0)
	T.corner(f, opts.radius or 10)
	local tex = T.texture(f, "pattern", dim and .9 or .8, dim and rgb(120, 118, 140) or col:Lerp(WHITE, .1), opts.tile or 90)
	tex.Name = "Texture"
	local glow = T.frame(f, "RarityGlow", 0, 0, 0, 0, dim and rgb(90, 88, 110) or col, 0)
	glow.Size = UDim2.fromScale(1, 1)
	T.corner(glow, opts.radius or 10)
	T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ kp(0, 1), kp(.5, .92), kp(1, dim and .8 or .5) }) }, glow)
	local st = T.new("UIStroke", { Name = "Rim", Color = opts.selected and WHITE or (dim and rgb(90, 86, 118) or col), Thickness = opts.selected and 3.5 or (opts.thick or 3),
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border, LineJoinMode = Enum.LineJoinMode.Round }, f)
	if not opts.selected then
		if r.rainbow and not dim and not opts.color then
			local g = T.new("UIGradient", { Color = T.RAINBOW }, st)
			if opts.animated then
				local tw = Tween:Create(g, TweenInfo.new(3, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = 360 })
				tw:Play(); g.Destroying:Once(function() tw:Cancel() end)
			end
		else
			T.new("UIGradient", { Rotation = 90, Color = ColorSequence.new((dim and rgb(90, 86, 118) or col):Lerp(WHITE, .35), dim and rgb(70, 66, 96) or col) }, st)
		end
	end
	if opts.animated and r.shine and not dim then T.shine(f, r.ordem >= 6 and 1.6 or 2.4, .7) end
	return f, r
end

-- ================================================================ MOTION
function T.scaleOf(o)
	return o:FindFirstChildOfClass("UIScale") or T.new("UIScale", {}, o)
end

function T.pop(o, amount, time)
	local sc = T.scaleOf(o)
	sc.Scale = amount or 1.14
	T.tween(sc, time or .32, { Scale = 1 }, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
end

function T.enter(o, fromScale, time, delay)
	local sc = T.scaleOf(o)
	sc.Scale = fromScale or .92
	T.tween(sc, time or .26, { Scale = 1 }, Enum.EasingStyle.Back, Enum.EasingDirection.Out, delay)
	return sc
end

function T.shake(o, force)
	if not o or not o.Parent or o:GetAttribute("Shaking") then return end
	o:SetAttribute("Shaking", true)
	local p0 = o.Position
	local f = force or 6
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
	local tw = Tween:Create(nv, TweenInfo.new(dur or .5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Value = to })
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
	local tw = Tween:Create(g, TweenInfo.new(.85, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, false, period or 2.4), { Offset = Vector2.new(1, 0) })
	tw:Play()
	s.Destroying:Once(function() tw:Cancel() end)
	return s
end

function T.breathe(o, prop, a, b, period)
	o[prop] = a
	local tw = Tween:Create(o, TweenInfo.new(period or .9, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), { [prop] = b })
	tw:Play()
	o.Destroying:Once(function() tw:Cancel() end)
	return tw
end

-- brilhos de 4 pontas espalhados (fundos de telas cheias / recompensas)
function T.sparkles(p, w, h, n, col)
	local rnd = Random.new(n * 7 + math.floor(w))
	for i = 1, n do
		local size = rnd:NextInteger(16, 46)
		local holder = T.frame(p, "Sparkle" .. i, rnd:NextNumber(0, w - size), rnd:NextNumber(0, h - size), size, size, nil, 1)
		T.image(holder, "Art", T.Assets.spark, 0, 0, size, size, col or WHITE, .3)
		local sc = T.new("UIScale", { Scale = .4 }, holder)
		local tw = Tween:Create(sc, TweenInfo.new(rnd:NextNumber(.9, 1.8), Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true, rnd:NextNumber(0, 1.5)), { Scale = 1.1 })
		tw:Play()
		holder.Destroying:Once(function() tw:Cancel() end)
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
function T.button(p, name, value, x, y, w, h, col, fn, opts)
	opts = opts or {}
	local lipH = opts.flat and 0 or math.clamp(math.floor(h * .1), 3, 6)
	local faceH = h - lipH
	local r = opts.radius or math.min(12, math.floor(h * .3))
	local b = T.new("TextButton", { Name = name, Text = "", AutoButtonColor = false, BackgroundTransparency = 1, BorderSizePixel = 0,
		Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(w, h), Selectable = true }, p)
	b:SetAttribute("ToneColor", col or P.neutral)
	local lip = T.frame(b, "Lip", 0, lipH, w, faceH, P.bg0, 0)
	T.corner(lip, r)
	T.new("UIStroke", { Color = INK, Thickness = 2, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, lip)
	local face = T.frame(b, "Face", 0, 0, w, faceH, WHITE, 0)
	T.corner(face, r)
	local grad = T.new("UIGradient", { Rotation = 90 }, face)
	T.new("UIStroke", { Name = "Outline", Color = INK, Thickness = 2, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, face)
	local gloss = T.frame(face, "Gloss", 3, 3, w - 6, math.floor(faceH * .45), WHITE, .7)
	T.corner(gloss, math.max(2, r - 3))
	T.fade(gloss, 90, .2, 1)
	if value and value ~= "" then
		local size = opts.size or math.clamp(math.floor(faceH * .5), 13, 26)
		local ix = 10
		if opts.icon then
			local isz = math.floor(faceH * .82)
			T.icon(face, opts.icon, 6, math.floor((faceH - isz) / 2), isz, isz)
			ix = isz + 8
		end
		T.text(face, "Caption", value, ix, 0, w - ix - 10, faceH, size, opts.textColor or P.text, opts.align or T.CENTER, opts.font or "title")
	end
	local sc = T.new("UIScale", {}, b)
	local hovered = false
	local function paint()
		local disabled = b:GetAttribute("Disabled") == true
		local tn = T.tone(disabled and rgb(70, 66, 92) or (b:GetAttribute("ToneColor") or P.neutral))
		local top = (hovered and not disabled) and tn.top:Lerp(WHITE, .15) or tn.top
		grad.Color = ColorSequence.new(top, tn.bottom)
		lip.BackgroundColor3 = tn.lip
		gloss.Visible = not disabled
		local cap = face:FindFirstChild("Caption")
		if cap then cap.TextColor3 = disabled and rgb(170, 166, 190) or (opts.textColor or P.text) end
	end
	paint()
	b:GetAttributeChangedSignal("ToneColor"):Connect(paint)
	b:GetAttributeChangedSignal("Disabled"):Connect(paint)
	b.MouseEnter:Connect(function()
		hovered = true; paint()
		if b:GetAttribute("Disabled") then return end
		T.tween(sc, .14, { Scale = opts.hoverScale or 1.04 }, Enum.EasingStyle.Back)
		if opts.hoverSound then T.som("ui_hover") end
	end)
	b.MouseLeave:Connect(function()
		hovered = false; paint()
		T.tween(sc, .14, { Scale = 1 }, Enum.EasingStyle.Quad)
		T.tween(face, .14, { Position = UDim2.fromOffset(0, 0) }, Enum.EasingStyle.Quad)
	end)
	b.MouseButton1Down:Connect(function()
		if b:GetAttribute("Disabled") then return end
		T.tween(face, .05, { Position = UDim2.fromOffset(0, lipH) }, Enum.EasingStyle.Quad)
		T.tween(sc, .06, { Scale = .96 }, Enum.EasingStyle.Quad)
	end)
	b.MouseButton1Up:Connect(function()
		T.tween(face, .24, { Position = UDim2.fromOffset(0, 0) }, Enum.EasingStyle.Back)
		T.tween(sc, .24, { Scale = hovered and (opts.hoverScale or 1.04) or 1 }, Enum.EasingStyle.Back)
	end)
	b.Activated:Connect(function()
		if b:GetAttribute("Disabled") then
			T.som("ui_erro")
			T.shake(face, 5)
			if opts.onDisabled then opts.onDisabled() end
			return
		end
		T.som(opts.sound or "ui_click")
		if fn then fn() end
	end)
	return b
end

function T.setTone(b, col) if b then b:SetAttribute("ToneColor", col) end end
function T.setEnabled(b, on) if b then b:SetAttribute("Disabled", not on) end end

-- botão redondo de ícone com rótulo embaixo (ações do inventário, atalhos)
function T.roundButton(p, name, key, label, x, y, size, fn, opts)
	opts = opts or {}
	local b = T.new("TextButton", { Name = name, Text = "", AutoButtonColor = false, BackgroundColor3 = opts.bg or P.bg2,
		BorderSizePixel = 0, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size) }, p)
	T.corner(b, size / 2)
	local st = T.stroke(b, opts.stroke or P.line, 3)
	T.gradient(b, WHITE, rgb(170, 164, 200))
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

function T.iconButton(p, name, key, x, y, size, fn, opts)
	opts = opts or {}
	local b = T.new("TextButton", { Name = name, Text = "", AutoButtonColor = false, BackgroundColor3 = opts.bg or P.bg1,
		BackgroundTransparency = opts.alpha or 0, BorderSizePixel = 0, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size) }, p)
	T.corner(b, opts.radius or 12)
	local st = T.stroke(b, opts.stroke or P.line, 3)
	T.gradient(b, WHITE, rgb(170, 164, 200))
	local isz = math.floor(size * (opts.iconScale or .72))
	T.icon(b, key, (size - isz) / 2, (size - isz) / 2, isz, isz)
	local sc = T.new("UIScale", {}, b)
	b.MouseEnter:Connect(function() T.tween(sc, .14, { Scale = 1.08 }, Enum.EasingStyle.Back); st.Color = opts.hover or P.accent end)
	b.MouseLeave:Connect(function() T.tween(sc, .14, { Scale = 1 }, Enum.EasingStyle.Quad); st.Color = opts.stroke or P.line end)
	b.MouseButton1Down:Connect(function() T.tween(sc, .06, { Scale = .92 }, Enum.EasingStyle.Quad) end)
	b.MouseButton1Up:Connect(function() T.tween(sc, .24, { Scale = 1 }, Enum.EasingStyle.Back) end)
	b.Activated:Connect(function() T.som("ui_click"); if fn then fn() end end)
	return b
end

-- fechar: cristal vermelho (losango) com X. Assinatura visual do jogo.
function T.closeButton(p, x, y, size, fn)
	local b = T.new("TextButton", { Name = "Close", Text = "", AutoButtonColor = false, BackgroundTransparency = 1, BorderSizePixel = 0,
		Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size), ZIndex = 10 }, p)
	local shadow = T.new("TextLabel", { Name = "GemShadow", BackgroundTransparency = 1, Text = "◆", TextScaled = true, FontFace = T.F.heavy,
		TextColor3 = INK, TextTransparency = .35, Position = UDim2.fromOffset(0, size * .07), Size = UDim2.fromScale(1, 1) }, b)
	local gem = T.new("TextLabel", { Name = "Gem", BackgroundTransparency = 1, Text = "◆", TextScaled = true, FontFace = T.F.heavy,
		TextColor3 = WHITE, Size = UDim2.fromScale(1, 1) }, b)
	T.new("UIGradient", { Rotation = 90, Color = ColorSequence.new(rgb(255, 120, 130), rgb(210, 20, 50)) }, gem)
	T.new("UIStroke", { Color = WHITE, Thickness = math.max(2, size * .045), LineJoinMode = Enum.LineJoinMode.Round }, gem)
	local cross = T.frame(b, "Cross", 0, 0, size, size, nil, 1)
	for i, rot in ipairs({ 45, -45 }) do
		local bar = T.new("Frame", { Name = "X" .. i, AnchorPoint = Vector2.new(.5, .5), Position = UDim2.fromScale(.5, .52),
			Size = UDim2.fromOffset(math.floor(size * .36), math.max(4, math.floor(size * .1))), Rotation = rot, BackgroundColor3 = WHITE, BorderSizePixel = 0 }, cross)
		T.corner(bar, 3)
		T.new("UIStroke", { Color = INK, Thickness = 2 }, bar)
	end
	local sc = T.new("UIScale", {}, b)
	b.MouseEnter:Connect(function()
		T.tween(sc, .16, { Scale = 1.12 }, Enum.EasingStyle.Back)
		T.tween(cross, .2, { Rotation = 90 }, Enum.EasingStyle.Back)
	end)
	b.MouseLeave:Connect(function()
		T.tween(sc, .14, { Scale = 1 }, Enum.EasingStyle.Quad)
		T.tween(cross, .16, { Rotation = 0 }, Enum.EasingStyle.Quad)
	end)
	b.MouseButton1Down:Connect(function() T.tween(sc, .06, { Scale = .9 }, Enum.EasingStyle.Quad) end)
	b.MouseButton1Up:Connect(function() T.tween(sc, .24, { Scale = 1 }, Enum.EasingStyle.Back) end)
	b.Activated:Connect(function() if fn then fn() end end)
	return b
end

-- ================================================================ COMPONENTES
function T.section(p, value, x, y, w, col, _icon, right)
	col = col or P.accent
	T.text(p, "SectionPip", "◆", x, y, 18, 26, 17, col, T.CENTER, "heavy", 1.5)
	T.text(p, "Section", T.upper(value), x + 24, y, w - 24 - (right and 180 or 0), 26, 19, P.text, T.LEFT, "title")
	if right then T.text(p, "SectionRight", right, x + w - 180, y, 180, 26, 15, P.text2, T.RIGHT, "title") end
	local line = T.frame(p, "SectionRule", x, y + 31, w, 2, col, 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ kp(0, 0), kp(.6, .75), kp(1, 1) }) }, line)
	return 42
end

-- título centralizado com linhas dos dois lados ("—— Bundles ——")
function T.sectionCenter(p, value, x, y, w, col)
	local tw = math.min(w * .6, TextService:GetTextSize(value, 22, Enum.Font.FredokaOne, Vector2.new(1000, 40)).X + 20)
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
	T.corner(track, math.floor(h / 2))
	if opts.stroke ~= false then T.stroke(track, INK, h >= 14 and 2.5 or 2) end
	local inset = h >= 12 and 2 or 1
	local ih = h - inset * 2
	local fill = T.frame(track, "Fill", inset, inset, math.max(ih, (w - inset * 2) * frac), ih, WHITE, 0)
	T.corner(fill, math.floor(ih / 2))
	local g = T.gradient(fill, col:Lerp(WHITE, .35), col:Lerp(INK, .1))
	g.Name = "Tint"
	local shine = T.frame(fill, "Shine", 2, 1, 0, math.max(1, math.floor(ih * .35)), WHITE, .6)
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
	local target = UDim2.fromOffset(math.max(ih, (track.Size.X.Offset - inset * 2) * frac), ih)
	fill.Visible = frac > 0
	if col then local g = fill:FindFirstChild("Tint"); if g then g.Color = ColorSequence.new(col:Lerp(WHITE, .35), col:Lerp(INK, .1)) end end
	if time and time > 0 then T.tween(fill, time, { Size = target }, Enum.EasingStyle.Quint) else fill.Size = target end
end

-- abas: selecionada vira faixa inclinada colorida; as outras ficam em texto
function T.tabs(p, name, x, y, w, h, items, current, col, onPick)
	col = col or P.accent
	local bar = T.frame(p, name, x, y, w, h, P.bg0, .25)
	T.corner(bar, 12)
	T.stroke(bar, P.lineSoft, 2)
	local n, pad, gap = #items, 5, 2
	local tw = (w - pad * 2 - gap * (n - 1)) / n
	for i, it in ipairs(items) do
		local sel = it.id == current
		local b = T.new("TextButton", { Name = "Tab_" .. tostring(it.id), Text = "", AutoButtonColor = false, BorderSizePixel = 0,
			BackgroundTransparency = 1, Position = UDim2.fromOffset(pad + (i - 1) * (tw + gap), pad), Size = UDim2.fromOffset(tw, h - pad * 2) }, bar)
		local bh = h - pad * 2
		local hl, cut = T.slant(b, "Highlight", 0, 0, tw, bh, sel and col or P.bg4, { tilt = 16, alpha = sel and 0 or 1 })
		local textCol = sel and P.text or (it.locked and P.text3 or P.text2)
		if it.icon then
			local isz = math.floor(bh * .86)
			local lw = TextService:GetTextSize(it.label, 18, Enum.Font.FredokaOne, Vector2.new(400, 40)).X
			local total = isz + 6 + math.min(lw, tw - isz - 24)
			local ix = math.max(tw * cut + 2, (tw - total) / 2)
			T.icon(b, it.icon, ix, (bh - isz) / 2, isz, isz)
			T.text(b, "Label", it.label, ix + isz + 6, 0, tw - (ix + isz + 6) - tw * cut, bh, 18, textCol, T.LEFT, "title")
		else
			T.text(b, "Label", it.label, tw * cut + 4, 0, tw - tw * cut * 2 - 8, bh, 18, textCol, T.CENTER, "title")
		end
		if it.badge and it.badge ~= 0 and it.badge ~= "" then T.badge(b, tw - 26, -10, it.badge, P.success) end
		if not sel then
			local g = hl:FindFirstChildOfClass("UIGradient")
			b.MouseEnter:Connect(function()
				local seq = g.Transparency.Keypoints
				local nk = {}
				for _, k in ipairs(seq) do table.insert(nk, kp(k.Time, k.Value < 1 and .35 or (k.Time > cut and k.Time < 1 - cut and .35 or 1))) end
				g.Transparency = NumberSequence.new(nk)
			end)
			b.MouseLeave:Connect(function()
				local seq = g.Transparency.Keypoints
				local nk = {}
				for _, k in ipairs(seq) do table.insert(nk, kp(k.Time, 1)) end
				g.Transparency = NumberSequence.new(nk)
			end)
			b.Activated:Connect(function() T.som("ui_tab"); onPick(it.id) end)
		end
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
	local size = opts.size or math.floor(h * .6)
	-- largura medida com o mesmo aumento de leitura aplicado ao texto (senão o rótulo encolhe dentro do chip)
	local shown = math.min(size * math.clamp(1 / math.max(.1, T.uiScale), 1, 1.3), h * .78)
	local w = opts.w or (TextService:GetTextSize(value, shown, Enum.Font.FredokaOne, Vector2.new(900, 90)).X + (opts.icon and h + 18 or 26))
	local f = T.frame(p, name, x, y, w, h, opts.solid and col or P.bg0, opts.solid and 0 or .2)
	T.corner(f, math.floor(h / 2))
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
	T.text(f, "Label", value, tx, 0, w - tx - 10, h, size, opts.solid and WHITE or col, opts.icon and T.LEFT or T.CENTER, "title")
	return f, w
end

function T.toggle(p, name, x, y, on, fn)
	local b = T.new("TextButton", { Name = name, Text = "", AutoButtonColor = false, BorderSizePixel = 0,
		BackgroundColor3 = on and P.success or P.bg0, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(70, 36) }, p)
	T.corner(b, 18)
	T.stroke(b, INK, 2.5)
	local knob = T.frame(b, "Knob", on and 38 or 4, 4, 28, 28, WHITE, 0)
	T.corner(knob, 14)
	T.stroke(knob, INK, 2)
	local state = on
	b.Activated:Connect(function()
		state = not state
		T.som("ui_toggle")
		T.tween(knob, .22, { Position = UDim2.fromOffset(state and 38 or 4, 4) }, Enum.EasingStyle.Back)
		T.tween(b, .15, { BackgroundColor3 = state and P.success or P.bg0 }, Enum.EasingStyle.Quad)
		if fn then fn(state) end
	end)
	return b
end

function T.input(p, name, x, y, w, h, placeholder, value, opts)
	opts = opts or {}
	local field = T.frame(p, name .. "Field", x, y, w, h, P.bg0, .1)
	T.corner(field, 12)
	local st = T.stroke(field, P.lineSoft, 2.5)
	local left = 14
	if opts.search then
		local ring = T.frame(field, "Lens", 16, h / 2 - 11, 16, 16, WHITE, 1)
		T.corner(ring, 8); T.stroke(ring, P.text2, 3)
		local handle = T.new("Frame", { Name = "Handle", BackgroundColor3 = P.text2, BorderSizePixel = 0, Rotation = 45,
			Position = UDim2.fromOffset(31, h / 2 + 7), Size = UDim2.fromOffset(9, 3.5), AnchorPoint = Vector2.new(.5, .5) }, field)
		T.corner(handle, 2)
		left = 44
	end
	local box = T.new("TextBox", { Name = name, Text = value or "", PlaceholderText = placeholder or "", ClearTextOnFocus = false,
		BackgroundTransparency = 1, Position = UDim2.fromOffset(left, 0), Size = UDim2.fromOffset(w - left - 10, h),
		TextColor3 = P.text, PlaceholderColor3 = P.text3, FontFace = T.F.title, TextSize = opts.size or 20,
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
function T.rarityFrame(f, key, opts)
	opts = opts or {}
	local r = T.rar(key)
	local st = f:FindFirstChildOfClass("UIStroke") or T.stroke(f, r.cor, 3)
	st.Color = opts.selected and WHITE or r.cor
	st.Thickness = opts.selected and 3.5 or (opts.thin and 2.5 or 3)
	st.Transparency = opts.dim and .5 or 0
	if r.rainbow and not opts.dim then
		local g = T.new("UIGradient", { Color = T.RAINBOW, Rotation = 0 }, st)
		if opts.animated then
			local tw = Tween:Create(g, TweenInfo.new(3, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = 360 })
			tw:Play(); g.Destroying:Once(function() tw:Cancel() end)
		end
	end
	if not opts.noGlow then
		local glow = T.frame(f, "RarityGlow", 0, 0, 0, 0, r.cor, 0)
		glow.Size = UDim2.fromScale(1, 1)
		local cr = f:FindFirstChildOfClass("UICorner")
		if cr then T.corner(glow, cr.CornerRadius.Offset) end
		T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ kp(0, 1), kp(.45, 1), kp(1, opts.dim and .9 or .55) }) }, glow)
	end
	if opts.animated and r.shine and not opts.dim then T.shine(f, r.ordem >= 6 and 1.6 or 2.4, .7) end
	return r
end

-- linha de atributo com gradiente na cor do atributo (estilo ficha de personagem)
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
function T.hint(o, text, side)
	o.MouseEnter:Connect(function()
		local token = {}
		tip.token = token
		task.delay(.28, function()
			if tip.token ~= token or not o.Parent or not tip.layer then return end
			local mouse = game:GetService("UserInputService"):GetMouseLocation()
			local ap, asz = o.AbsolutePosition, o.AbsoluteSize
			local inset = game:GetService("GuiService"):GetGuiInset()
			local mx, my = mouse.X, mouse.Y - inset.Y
			if mx < ap.X or mx > ap.X + asz.X or my < ap.Y or my > ap.Y + asz.Y then return end
			if tip.guard and not tip.guard(o) then return end
			if tip.frame then tip.frame:Destroy() end
			local s = tip.scale and tip.scale() or 1
			local value = type(text) == "function" and text() or text
			local f = T.new("Frame", { Name = "Tooltip", BackgroundColor3 = P.bg0, BackgroundTransparency = .02, BorderSizePixel = 0,
				AutomaticSize = Enum.AutomaticSize.XY, Size = UDim2.fromOffset(0, 0), ZIndex = 100 }, tip.layer)
			T.corner(f, 10); T.stroke(f, P.line, 2.5)
			T.new("UIPadding", { PaddingLeft = UDim.new(0, 12), PaddingRight = UDim.new(0, 12), PaddingTop = UDim.new(0, 7), PaddingBottom = UDim.new(0, 7) }, f)
			T.new("TextLabel", { Name = "Text", BackgroundTransparency = 1, AutomaticSize = Enum.AutomaticSize.XY, Size = UDim2.fromOffset(0, 0),
				FontFace = T.F.title, TextSize = 17, TextColor3 = P.text, Text = value, RichText = true, ZIndex = 101 }, f)
			local rel = (o.AbsolutePosition - tip.layer.AbsolutePosition) / s
			local size = o.AbsoluteSize / s
			if side == "above" then
				f.AnchorPoint = Vector2.new(.5, 1)
				f.Position = UDim2.fromOffset(rel.X + size.X / 2, rel.Y - 8)
			elseif side == "below" then
				f.AnchorPoint = Vector2.new(.5, 0)
				f.Position = UDim2.fromOffset(rel.X + size.X / 2, rel.Y + size.Y + 8)
			elseif side == "left" then
				f.AnchorPoint = Vector2.new(1, .5)
				f.Position = UDim2.fromOffset(rel.X - 10, rel.Y + size.Y / 2)
			else
				f.AnchorPoint = Vector2.new(0, .5)
				f.Position = UDim2.fromOffset(rel.X + size.X + 10, rel.Y + size.Y / 2)
			end
			tip.frame = f
			T.enter(f, .9, .16)
		end)
	end)
	o.MouseLeave:Connect(hideTip)
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
function T.preview(p, kind, id, x, y, w, h, animated, dim)
	local model
	if kind == "pet" then
		local arte = require(RS.Config).PetArte
		arte = arte and arte[id]
		if arte then
			local img = T.image(p, "Retrato_" .. id, animated and (arte.corpo or arte.busto) or (arte.busto or arte.corpo), x, y, w, h, dim and rgb(60, 58, 80) or nil)
			if animated then
				img.Position = UDim2.fromOffset(x, y + 3)
				local tw = Tween:Create(img, TweenInfo.new(2.2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), { Position = UDim2.fromOffset(x, y - 3) })
				tw:Play()
				img.Destroying:Once(function() tw:Cancel() end)
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
	orient(.3)
	if animated then
		local age = 0
		local conn
		conn = Run.RenderStepped:Connect(function(dt)
			if not v.Parent then conn:Disconnect(); return end
			age += dt
			orient(.3 + math.sin(age * .32) * .45)
		end)
		v.Destroying:Once(function() conn:Disconnect() end)
	end
	return v
end

return T

