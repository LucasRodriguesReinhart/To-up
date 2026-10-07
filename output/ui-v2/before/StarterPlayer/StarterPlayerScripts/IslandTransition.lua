-- Transição de viagem (UI V2): cartela com o nome da ilha, energia do tema e barra de carregamento.
-- Continua guiada pelo atributo AreaTransition, publicado pelo servidor.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local player = Players.LocalPlayer
local T = require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local Config = require(RS:WaitForChild("Config"))
local P = T.P

local gui = T.new("ScreenGui", { Name = "IslandTransition", IgnoreGuiInset = true, ResetOnSpawn = false, DisplayOrder = 1000,
	ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, player:WaitForChild("PlayerGui"))
local panel = T.new("Frame", { Name = "Panel", Size = UDim2.fromScale(1, 1), BackgroundColor3 = P.ink, BackgroundTransparency = 1,
	BorderSizePixel = 0, Visible = false }, gui)
-- arte da ilha de destino ao fundo
local scene = T.new("ImageLabel", { Name = "Scene", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, ImageTransparency = 1,
	ScaleType = Enum.ScaleType.Crop, ImageColor3 = Color3.fromRGB(150, 150, 170), BorderSizePixel = 0 }, panel)
local wash = T.new("Frame", { Name = "Wash", Size = UDim2.fromScale(1, 1), BackgroundColor3 = P.accent, BackgroundTransparency = 1, BorderSizePixel = 0 }, panel)
T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, .75), T.kp(.5, 1), T.kp(1, .75) }) }, wash)
local bandTop = T.new("Frame", { Name = "BandTop", Position = UDim2.fromScale(0, .3), Size = UDim2.new(1, 0, 0, 3), BackgroundColor3 = P.accent, BorderSizePixel = 0 }, panel)
local bandBottom = bandTop:Clone()
bandBottom.Name = "BandBottom"
bandBottom.Position = UDim2.fromScale(0, .68)
bandBottom.Parent = panel
for _, band in ipairs({ bandTop, bandBottom }) do
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, band)
end
local stripes = T.new("Frame", { Name = "Stripes", Position = UDim2.fromScale(0, .303), Size = UDim2.new(1, 0, 0, 0), BackgroundTransparency = 1, BorderSizePixel = 0 }, panel)

local logo = T.new("ImageLabel", { Name = "Logo", AnchorPoint = Vector2.new(.5, 0), Position = UDim2.fromScale(.5, .1), Size = UDim2.fromScale(.26, .14),
	BackgroundTransparency = 1, ImageTransparency = 1, Image = T.Assets.logo, ScaleType = Enum.ScaleType.Fit }, panel)
local caption = T.new("TextLabel", { Name = "Caption", BackgroundTransparency = 1, Position = UDim2.fromScale(.1, .345), Size = UDim2.fromScale(.8, .05),
	FontFace = T.F.title, TextScaled = true, TextColor3 = P.text2, TextTransparency = 1, Text = "VIAJANDO PARA" }, panel)
local title = T.new("TextLabel", { Name = "Title", BackgroundTransparency = 1, Position = UDim2.fromScale(.1, .4), Size = UDim2.fromScale(.8, .14),
	FontFace = T.F.display, TextScaled = true, TextColor3 = P.text, TextTransparency = 1, Text = "" }, panel)
T.new("UIStroke", { Color = P.ink, Thickness = 4, LineJoinMode = Enum.LineJoinMode.Round }, title)
local sub = T.new("TextLabel", { Name = "Sub", BackgroundTransparency = 1, Position = UDim2.fromScale(.1, .55), Size = UDim2.fromScale(.8, .04),
	FontFace = T.F.title, TextScaled = true, TextColor3 = P.text2, TextTransparency = 1, Text = "" }, panel)
local track = T.new("Frame", { Name = "Track", AnchorPoint = Vector2.new(.5, 0), Position = UDim2.fromScale(.5, .61), Size = UDim2.new(.26, 0, 0, 8),
	BackgroundColor3 = P.bg0, BackgroundTransparency = 1, BorderSizePixel = 0 }, panel)
T.corner(track, 4)
local fill = T.new("Frame", { Name = "Fill", Size = UDim2.fromScale(.35, 1), BackgroundColor3 = P.accent, BackgroundTransparency = 1, BorderSizePixel = 0 }, track)
T.corner(fill, 4)

local tweens, revision = {}, 0
local function stopTweens()
	for _, tw in ipairs(tweens) do tw:Cancel() end
	table.clear(tweens)
end

local function update()
	revision += 1
	local mine = revision
	local id = player:GetAttribute("AreaTransition")
	stopTweens()
	if id ~= nil then
		local area = Config.areaPorId(id)
		local tema = area and Config.Temas[area.tema]
		local col = tema and tema.cor or P.accent
		title.Text = area and T.upper(area.nome) or "PRAÇA CENTRAL"
		sub.Text = area and ("ILHA " .. area.id .. "   ·   " .. T.upper(tema.nome)) or "LOBBY   ·   IGNIS, BANNERS E PORTAIS"
		wash.BackgroundColor3 = col
		bandTop.BackgroundColor3 = col
		bandBottom.BackgroundColor3 = col
		fill.BackgroundColor3 = col
		T.clear(stripes)
		stripes.Size = UDim2.new(1, 0, 0, 0)
		scene.Image = area and T.areaImage(area.id) or T.Assets.lobby
		scene.ImageTransparency = .55
		logo.ImageTransparency = .15
		panel.Visible = true
		panel.BackgroundTransparency = .06
		caption.TextTransparency = 0
		title.TextTransparency = 0
		sub.TextTransparency = 0
		track.BackgroundTransparency = .2
		fill.BackgroundTransparency = 0
		local sc = T.scaleOf(title)
		sc.Scale = .92
		table.insert(tweens, T.tween(sc, .4, { Scale = 1 }, Enum.EasingStyle.Back))
		fill.Position = UDim2.fromScale(-.35, 0)
		table.insert(tweens, game:GetService("TweenService"):Create(fill, TweenInfo.new(1.1, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut, -1), { Position = UDim2.fromScale(1, 0) }))
		tweens[#tweens]:Play()
	else
		for _, o in ipairs({ caption, title, sub }) do table.insert(tweens, T.tween(o, .3, { TextTransparency = 1 }, Enum.EasingStyle.Quad)) end
		table.insert(tweens, T.tween(scene, .3, { ImageTransparency = 1 }, Enum.EasingStyle.Quad))
		table.insert(tweens, T.tween(logo, .25, { ImageTransparency = 1 }, Enum.EasingStyle.Quad))
		table.insert(tweens, T.tween(track, .25, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad))
		table.insert(tweens, T.tween(fill, .25, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad))
		local out = T.tween(panel, .35, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad)
		table.insert(tweens, out)
		out.Completed:Once(function() if revision == mine then panel.Visible = false end end)
	end
end

player:GetAttributeChangedSignal("AreaTransition"):Connect(update)
update()

