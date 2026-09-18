-- Viagem guiada exclusivamente pelo atributo autoritativo AreaTransition.
-- TravelTransition representa o período em que a interface ainda bloqueia gameplay.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local TextService = game:GetService("TextService")
local player = Players.LocalPlayer
local T = require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local Config = require(RS:WaitForChild("Config"))
local P = T.P
local Som=require(RS:WaitForChild("SomJogo"))
local audioTransition=nil

local gui = T.new("ScreenGui", { Name = "IslandTransition", IgnoreGuiInset = true, ResetOnSpawn = false,
	DisplayOrder = 1000, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, player:WaitForChild("PlayerGui"))
local panel = T.new("TextButton", { Name = "Panel", Size = UDim2.fromScale(1, 1), Text = "", AutoButtonColor = false,
	Selectable = false, Active = true, BackgroundColor3 = P.bg0, BackgroundTransparency = 1, BorderSizePixel = 0, Visible = false }, gui)
local scene = T.new("ImageLabel", { Name = "Scene", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1,
	ImageTransparency = 1, ScaleType = Enum.ScaleType.Crop, ImageColor3 = Color3.fromRGB(74, 87, 103) }, panel)
local content = T.new("CanvasGroup", { Name = "Destination", AnchorPoint = Vector2.new(.5, .5), Position = UDim2.fromScale(.5, .5),
	Size = UDim2.fromOffset(720, 304), GroupTransparency = 1, BackgroundColor3 = P.bg1, BorderSizePixel = 0 }, panel)
T.corner(content, 10)
T.stroke(content, P.neutral, 1)
local accent = T.frame(content, "Accent", 0, 0, 4, 304, P.accent, 0)
local textBody = T.scroll(content, "TextBody", 32, 32, 656, 164, P.line)
textBody.ClipsDescendants = true
local caption = T.text(textBody, "Caption", "EXPEDIÇÃO", 0, 0, 648, 26, 14, P.accent, T.LEFT, "label")
caption:SetAttribute("Paragraph", true)
local title = T.text(textBody, "Title", "", 0, 36, 648, 56, 38, P.text, T.LEFT, "display")
title:SetAttribute("Paragraph", true)
local sub = T.para(textBody, "Subtitle", "", 0, 102, 648, 34, 17, P.text2, T.LEFT, "body")
local status = T.text(content, "Status", "Atravessando o portal…", 40, 211, 640, 24, 14, P.text3, T.LEFT, "body")
local track = T.frame(content, "Track", 40, 253, 640, 5, P.bg0, 0)
track.ClipsDescendants = true
T.corner(track, 2)
local fill = T.new("Frame", { Name = "Fill", Size = UDim2.fromScale(.3, 1), BackgroundColor3 = P.accent,
	BorderSizePixel = 0 }, track)
T.corner(fill, 2)

local tweens, revision = {}, 0
local function motionEnabled()
	return T.motionEnabled and T.motionEnabled() or (not T.motionEnabled and player:GetAttribute("ReducedMotion") ~= true)
end
local function stopTweens()
	for _, tw in ipairs(tweens) do tw:Cancel() end
	table.clear(tweens)
end
local function tween(object, duration, properties)
	local tw = T.tween(object, duration, properties, Enum.EasingStyle.Quad)
	table.insert(tweens, tw)
	return tw
end
local function resize()
	local v = gui.AbsoluteSize
	if v.X < 1 or v.Y < 1 then return end
	local width = math.max(1, math.min(720, v.X - 32))
	local padding = width < 520 and 24 or 32
	local textW = math.max(1, width - padding * 2 - 8)
	local function heightFor(label, font, minimum)
		local bounds = TextService:GetTextSize(label.Text, label.TextSize, font, Vector2.new(textW, 10000))
		return math.max(minimum, bounds.Y + 6)
	end
	local captionH = heightFor(caption, Enum.Font.GothamBlack, 26)
	local titleH = heightFor(title, Enum.Font.FredokaOne, 48)
	local subH = heightFor(sub, Enum.Font.BuilderSansBold, 26)
	local titleY = captionH + 10
	local subY = titleY + titleH + 10
	local bodyH = subY + subH
	local height = math.min(padding + bodyH + 76, v.Y - 32)
	local viewportH = math.max(1, height - padding - 76)
	content.Size = UDim2.fromOffset(width, height)
	accent.Size = UDim2.fromOffset(4, height)
	textBody.Position = UDim2.fromOffset(padding, padding)
	textBody.Size = UDim2.fromOffset(width - padding * 2, viewportH)
	textBody.CanvasSize = UDim2.fromOffset(0, bodyH)
	textBody.CanvasPosition = Vector2.new(0, math.clamp(textBody.CanvasPosition.Y, 0, math.max(0, bodyH - viewportH)))
	caption.Size = UDim2.fromOffset(textW, captionH)
	title.Position = UDim2.fromOffset(0, titleY)
	title.Size = UDim2.fromOffset(textW, titleH)
	sub.Position = UDim2.fromOffset(0, subY)
	sub.Size = UDim2.fromOffset(textW, subH)
	status.Position = UDim2.fromOffset(padding, height - 64)
	status.Size = UDim2.fromOffset(width - padding * 2, 24)
	track.Position = UDim2.fromOffset(padding, height - 28)
	track.Size = UDim2.fromOffset(width - padding * 2, 5)
end
gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)
resize()

local function update()
	revision += 1
	local mine = revision
	local id = player:GetAttribute("AreaTransition")
	stopTweens()
	if id ~= nil then
		if audioTransition~=id then Som.tocar("portal_saida"); audioTransition=id end
		player:SetAttribute("TravelTransition", true)
		local area = Config.areaPorId(id)
		local tema = area and Config.Temas[area.tema]
		local col = tema and tema.cor or P.accent
		title.Text = area and area.nome or "Praça Central"
		caption.Text = area and ("EXPEDIÇÃO  /  ILHA " .. tostring(area.id)) or "BASE DA EXPEDIÇÃO"
		sub.Text = tema and tema.nome or "Ignis, invocações e portais"
		status.Text = "Atravessando o portal…"
		textBody.CanvasPosition = Vector2.zero
		resize()
		accent.BackgroundColor3 = col
		caption.TextColor3 = col
		fill.BackgroundColor3 = col
		scene.Image = area and T.areaImage(area.id) or T.Assets.lobby
		panel.Visible = true
		panel.BackgroundTransparency = 0
		scene.ImageTransparency = .68
		content.GroupTransparency = 0
		fill.Position = UDim2.fromScale(-.3, 0)
		if motionEnabled() then
			local loading = TweenService:Create(fill, TweenInfo.new(.85, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut, -1),
				{ Position = UDim2.fromScale(1, 0) })
			table.insert(tweens, loading)
			loading:Play()
		else
			fill.Position = UDim2.fromScale(.35, 0)
		end
	else
		if not panel.Visible then player:SetAttribute("TravelTransition", false); return end
		status.Text = "Destino alcançado"
		if audioTransition~=nil then Som.tocar("portal_chegada"); audioTransition=nil end
		local duration = motionEnabled() and .18 or .08
		tween(content, duration, { GroupTransparency = 1 })
		tween(scene, duration, { ImageTransparency = 1 })
		local out = tween(panel, duration, { BackgroundTransparency = 1 })
		out.Completed:Once(function()
			if revision == mine then
				panel.Visible = false
				player:SetAttribute("TravelTransition", false)
			end
		end)
	end
end

player:GetAttributeChangedSignal("AreaTransition"):Connect(update)
player:GetAttributeChangedSignal("ReducedMotion"):Connect(function() if player:GetAttribute("AreaTransition") ~= nil then update() end end)
player:GetAttributeChangedSignal("ExpeditionEffectsEnabled"):Connect(function() if player:GetAttribute("AreaTransition") ~= nil then update() end end)
update()
