--[[
	OreVFX_Setup (Server Script)  -  put in ServerScriptService.

	1) Every ore tagged "Ore" (CollectionService) that has the Attributes
	   OreType + Rarity gets its idle VFX automatically.
	2) Your mining code calls:
	       OreVFX.Hit(ore, hitPosition)
	       OreVFX.Break(ore)          -- right before destroying the ore
	3) SHOWCASE = true builds a test grid of all 24 ores in front of the spawn,
	   hitting and breaking them in a loop so you can preview every effect.
]]

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local OreVFX = require(ReplicatedStorage:WaitForChild("OreVFX"))

local SHOWCASE = false -- true = grade de teste com os 24 minerios em (0, 0, -600)

local function setup(ore)
	if ore:GetAttribute("OreType") and ore:GetAttribute("Rarity") then
		local ok, err = pcall(OreVFX.Attach, ore)
		if not ok then warn("OreVFX:", err) end
	end
end

CollectionService:GetInstanceAddedSignal("Ore"):Connect(setup)
for _, ore in ipairs(CollectionService:GetTagged("Ore")) do task.spawn(setup, ore) end

if not SHOWCASE then return end

local TYPES = { "NinjaChakra", "DragonBall", "DemonSlayer", "ShadowMana", "OceanTreasure", "HeroImpact" }
local RARITIES = { "Common", "Uncommon", "Epic", "SuperLegendary" }
local SIZES = { 2.9, 3.8, 4.8, 6 }            -- same ratio as the Blender models
local COLORS = {
	NinjaChakra = Color3.fromRGB(190, 110, 60), DragonBall = Color3.fromRGB(230, 180, 60),
	DemonSlayer = Color3.fromRGB(60, 110, 90), ShadowMana = Color3.fromRGB(110, 60, 160),
	OceanTreasure = Color3.fromRGB(40, 170, 210), HeroImpact = Color3.fromRGB(240, 200, 40),
}

local folder = Instance.new("Folder")
folder.Name = "OreVFX_Showcase"
folder.Parent = workspace

local origin = Vector3.new(0, 0, -600)
local ores = {}
for t, oreType in ipairs(TYPES) do
	for r, rarity in ipairs(RARITIES) do
		local s = SIZES[r]
		local p = Instance.new("Part")
		p.Name = oreType .. "_" .. rarity
		p.Shape = Enum.PartType.Ball
		p.Size = Vector3.new(s, s * 0.8, s)
		p.Anchored = true
		p.Material = Enum.Material.Slate
		p.Color = COLORS[oreType]
		p.Position = origin + Vector3.new((r - 2.5) * 14, s * 0.4, (t - 3.5) * 16)
		p:SetAttribute("OreType", oreType)
		p:SetAttribute("Rarity", rarity)
		p.Parent = folder
		CollectionService:AddTag(p, "Ore")
		table.insert(ores, p)
	end
end

-- preview loop: 3 hits then a break, then respawn idle VFX
task.spawn(function()
	while folder.Parent do
		for _, ore in ipairs(ores) do
			for _ = 1, 3 do
				local offset = Vector3.new(math.random(-10, 10) / 10, math.random(0, 10) / 10, -ore.Size.Z / 2)
				OreVFX.Hit(ore, ore.Position + offset)
				task.wait(0.15)
			end
		end
		task.wait(1)
		for _, ore in ipairs(ores) do
			OreVFX.Break(ore)
			task.wait(0.25)
		end
		task.wait(2)
		for _, ore in ipairs(ores) do OreVFX.Attach(ore) end
		task.wait(6)
	end
end)

