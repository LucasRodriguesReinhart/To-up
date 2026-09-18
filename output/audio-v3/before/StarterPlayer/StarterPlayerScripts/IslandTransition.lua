-- Viagem guiada exclusivamente pelo atributo autoritativo AreaTransition.
-- TravelTransition representa o período em que a interface ainda bloqueia gameplay.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local player = Players.LocalPlayer
local T = require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local Config = require(RS:WaitForChild("Config"))
local P = T.P

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
local contentScale = T.new("UIScale", {}, content)
local accent = T.frame(content, "Accent", 0, 0, 4, 304, P.accent, 0)
local caption = T.text(content, "Caption", "EXPEDIÇÃO", 40, 30, 640, 26, 14, P.accent, T.LEFT, "label")
local title = T.text(content, "Title", "", 40, 74, 640, 56, 38, P.text, T.LEFT, "display")
title.TextScaled = true
local titleConstraint = title:FindFirstChildOfClass("UITextSizeConstraint")
if titleConstraint then titleConstraint.MinTextSize = 18; titleConstraint.MaxTextSize = 38 end
local sub = T.text(content, "Subtitle", "", 40, 142, 640, 34, 17, P.text2, T.LEFT, "body")
sub.TextTruncate = Enum.TextTruncate.AtEnd
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
	contentScale.Scale = math.min(1.2, math.max(.32, (v.X - 32) / 720), math.max(.32, (v.Y - 40) / 304))
end
gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)
resize()

local function update()
	revision += 1
	local mine = revision
	local id = player:GetAttribute("AreaTransition")
	stopTweens()
	if id ~= nil then
		player:SetAttribute("TravelTransition", true)
		local area = Config.areaPorId(id)
		local tema = area and Config.Temas[area.tema]
		local col = tema and tema.cor or P.accent
		title.Text = area and area.nome or "Praça Central"
		caption.Text = area and ("EXPEDIÇÃO  /  ILHA " .. tostring(area.id)) or "BASE DA EXPEDIÇÃO"
		sub.Text = tema and tema.nome or "Ignis, invocações e portais"
		status.Text = "Atravessando o portal…"
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

