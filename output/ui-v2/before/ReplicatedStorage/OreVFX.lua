--[[
	OreVFX (ModuleScript)  -  Anime Mining Simulator
	Place in ReplicatedStorage. All effects use only native Roblox instances
	(ParticleEmitter, Beam, PointLight, Attachment, Part + TweenService).

	API
	  OreVFX.Attach(ore, oreType, rarity)   -> idle / ambient effects (loops)
	  OreVFX.Hit(ore, worldPosition?)       -> small burst when the pickaxe hits
	  OreVFX.Break(ore)                     -> big burst when the ore is destroyed
	  OreVFX.Clear(ore)                     -> removes idle effects

	  ore      : BasePart or Model (uses PrimaryPart / first BasePart)
	  oreType  : "NinjaChakra" | "DragonBall" | "DemonSlayer" | "ShadowMana" | "OceanTreasure" | "HeroImpact"
	  rarity   : "Common" | "Uncommon" | "Epic" | "SuperLegendary"

	If oreType / rarity are omitted, the ore's Attributes "OreType" and "Rarity" are used.
]]

local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local OreVFX = {}

-- Uploaded from RobloxVFX/Textures (same file names).
OreVFX.Textures = {
	glow_soft              = "rbxassetid://119690923296259",
	spark_star             = "rbxassetid://106034798506002",
	sparkle_diamond        = "rbxassetid://113126543125281",
	shockwave_ring         = "rbxassetid://123618418899772",
	swirl_vortex           = "rbxassetid://124410208940490",
	slash_crescent         = "rbxassetid://110819782030693",
	bubble                 = "rbxassetid://94376140973180",
	speed_lines            = "rbxassetid://88060793234854",
	leaf_particle          = "rbxassetid://120563379296122",
	magic_circle           = "rbxassetid://118214441618788",
	energy_beam            = "rbxassetid://134235069437330",
	flame_flipbook_4x4     = "rbxassetid://108696159734060",
	smoke_flipbook_4x4     = "rbxassetid://111755528879126",
	lightning_flipbook_4x4 = "rbxassetid://108351666436535",
	coin_flipbook_4x4      = "rbxassetid://81147718598264",
	rock_debris_2x2        = "rbxassetid://134946881676486",
	rune_glyphs_2x2        = "rbxassetid://84448215429631",
	icon_konoha_leaf       = "rbxassetid://129506891038957",
	icon_shuriken          = "rbxassetid://93752512929437",
	icon_dragonball        = "rbxassetid://98146604921725",
	icon_flame             = "rbxassetid://127316648152210",
	icon_water_wave        = "rbxassetid://107707114254311",
	icon_hanafuda          = "rbxassetid://100049624002097",
	icon_star4             = "rbxassetid://122362060823933",
	icon_demon_eye         = "rbxassetid://100494237576497",
	icon_anchor            = "rbxassetid://132169961085226",
	icon_ship_wheel        = "rbxassetid://94487268683616",
	icon_pow               = "rbxassetid://114926374953247",
	icon_fist              = "rbxassetid://78114678437464",
	icon_straw_hat         = "rbxassetid://115151836878119",
	aura_spike             = "rbxassetid://125231045049619",
	aura_flipbook_4x4      = "rbxassetid://118729825325307",
	ki_column              = "rbxassetid://73794900832947",
}
local TX = OreVFX.Textures

local TIER = { Common = 1, Uncommon = 2, Epic = 3, SuperLegendary = 4 }

-- ------------------------------------------------------------------ helpers
local function rgb(r, g, b) return Color3.fromRGB(r, g, b) end

local function CS(...)
	local args = { ... }
	if #args == 1 then return ColorSequence.new(args[1]) end
	local kps = {}
	for i, c in ipairs(args) do
		table.insert(kps, ColorSequenceKeypoint.new((i - 1) / (#args - 1), c))
	end
	return ColorSequence.new(kps)
end

-- NS({0, v0}, {0.5, v1}, {1, v2})  or NS(v)
local function NS(...)
	local args = { ... }
	if type(args[1]) == "number" then return NumberSequence.new(args[1]) end
	local kps = {}
	for _, p in ipairs(args) do table.insert(kps, NumberSequenceKeypoint.new(p[1], p[2], p[3] or 0)) end
	return NumberSequence.new(kps)
end

local FADE = NS({ 0, 1 }, { 0.15, 0 }, { 0.75, 0.2 }, { 1, 1 })
local FADE_SOFT = NS({ 0, 1 }, { 0.3, 0.35 }, { 1, 1 })

local function rootPart(ore)
	if ore:IsA("BasePart") then return ore end
	if ore:IsA("Model") then
		return ore.PrimaryPart or ore:FindFirstChildWhichIsA("BasePart", true)
	end
	return nil
end

local function oreSize(ore)
	if ore:IsA("Model") then
		local _, size = ore:GetBoundingBox()
		return size
	end
	return ore.Size
end

local function emitter(parent, name, props)
	local e = Instance.new("ParticleEmitter")
	e.Name = name
	e.LightInfluence = 0
	e.LightEmission = 1
	e.Rate = 0
	for k, v in pairs(props) do e[k] = v end
	e.Parent = parent
	return e
end

local function attachment(part, name, offset)
	local a = Instance.new("Attachment")
	a.Name = name
	a.Position = offset or Vector3.zero
	a.Parent = part
	return a
end

local function light(parent, color, brightness, range)
	local l = Instance.new("PointLight")
	l.Color = color
	l.Brightness = math.min(brightness * 0.35, 2)
	l.Range = math.min(range * 0.45, 18)
	l.Shadows = false
	l.Parent = parent
	return l
end

local function burst(parent, name, props, count, lifetimeMax)
	local e = emitter(parent, name, props)
	e.Enabled = false
	e:Emit(count)
	Debris:AddItem(e, lifetimeMax + 0.5)
	return e
end

-- Rock debris colour per ore type (matches the 3D models)
local ROCK = {
	NinjaChakra   = { rgb(170, 120, 80), rgb(120, 140, 175), rgb(190, 110, 60), rgb(210, 90, 35) },
	DragonBall    = { rgb(215, 170, 110), rgb(190, 135, 90), rgb(90, 120, 200), rgb(250, 205, 60) },
	DemonSlayer   = { rgb(95, 92, 100), rgb(60, 110, 160), rgb(130, 50, 45), rgb(70, 70, 85) },
	ShadowMana    = { rgb(130, 115, 150), rgb(110, 80, 150), rgb(95, 55, 135), rgb(70, 30, 110) },
	OceanTreasure = { rgb(225, 205, 160), rgb(80, 175, 180), rgb(45, 110, 200), rgb(30, 180, 215) },
	HeroImpact    = { rgb(150, 150, 158), rgb(140, 128, 105), rgb(150, 60, 50), rgb(255, 215, 50) },
}

-- ------------------------------------------------------------------ shared building blocks
local Common = {}

function Common.dust(part, color, tier, size)
	emitter(part, "Dust", {
		Texture = TX.sparkle_diamond, Color = CS(color), LightEmission = 0.6,
		Size = NS({ 0, 0 }, { 0.3, 0.18 * size }, { 1, 0 }), Transparency = FADE_SOFT,
		Lifetime = NumberRange.new(1.2, 2), Rate = 1.5 * tier, Speed = NumberRange.new(0.3, 0.8),
		SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, 0.6, 0),
		Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
		RotSpeed = NumberRange.new(-90, 90), Rotation = NumberRange.new(0, 360),
	})
end

function Common.glowCore(att, color, size, tier)
	emitter(att, "GlowCore", {
		Texture = TX.glow_soft, Color = CS(color), LightEmission = 1, LockedToPart = true,
		Size = NS({ 0, size * 1.4 }, { 0.5, size * 1.7 }, { 1, size * 1.4 }),
		Transparency = NS({ 0, 1 }, { 0.5, 0.55 + 0.08 * (4 - tier) }, { 1, 1 }),
		Lifetime = NumberRange.new(1.5), Rate = 2, Speed = NumberRange.new(0),
		ZOffset = -1,
	})
end

function Common.risingWisps(part, texture, color, tier, size, flip)
	local e = emitter(part, "Wisps", {
		Texture = texture, Color = color, LightEmission = 1,
		Size = NS({ 0, 0.25 * size }, { 0.4, 0.5 * size }, { 1, 0 }), Transparency = FADE,
		Lifetime = NumberRange.new(0.8, 1.4), Rate = 4 * tier, Speed = NumberRange.new(1.5, 3),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(20, 20),
		Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
		Drag = 1, Acceleration = Vector3.new(0, 2, 0),
	})
	if flip then
		e.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4
		e.FlipbookMode = Enum.ParticleFlipbookMode.OneShot
		e.FlipbookStartRandom = false
	end
	return e
end

function Common.iconPop(att, texture, color, size, rate, lifetime)
	return emitter(att, "IconPop", {
		Texture = texture, Color = CS(color), LightEmission = 0.2,
		Size = NS({ 0, 0 }, { 0.12, size * 1.15 }, { 0.25, size }, { 1, size * 0.8 }),
		Transparency = NS({ 0, 0 }, { 0.7, 0 }, { 1, 1 }),
		Lifetime = NumberRange.new(lifetime or 1.6), Rate = rate, Speed = NumberRange.new(1.5, 2.5),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(35, 35), Drag = 2,
		Rotation = NumberRange.new(-15, 15), RotSpeed = NumberRange.new(-20, 20),
	})
end

function Common.groundCircle(att, texture, color, size, rotSpeed)
	return emitter(att, "GroundCircle", {
		Texture = texture, Color = CS(color), LightEmission = 1, LockedToPart = true,
		Orientation = Enum.ParticleOrientation.VelocityPerpendicular,
		EmissionDirection = Enum.NormalId.Top, Speed = NumberRange.new(0.01),
		Size = NS({ 0, size * 0.9 }, { 0.2, size }, { 1, size }),
		Transparency = NS({ 0, 1 }, { 0.2, 0.15 }, { 0.8, 0.15 }, { 1, 1 }),
		Lifetime = NumberRange.new(3), Rate = 0.5, Rotation = NumberRange.new(0, 360),
		RotSpeed = NumberRange.new(rotSpeed or 25),
	})
end

function Common.beamPillar(part, bottom, top, color, width, texture)
	local b = Instance.new("Beam")
	b.Name = "AuraPillar"
	b.Attachment0 = bottom
	b.Attachment1 = top
	b.Texture = texture or TX.energy_beam
	b.TextureMode = Enum.TextureMode.Stretch
	b.TextureSpeed = 1.5
	b.Color = CS(color)
	b.LightEmission = 1
	b.LightInfluence = 0
	b.FaceCamera = true
	b.Width0 = width
	b.Width1 = width * 0.35
	b.Transparency = NS({ 0, 0.9 }, { 0.4, 0.45 }, { 1, 1 })
	b.Segments = 10
	b.Parent = part
	return b
end

function Common.shockwave(part, position, color, maxSize, duration)
	local ring = Instance.new("Part")
	ring.Name = "Shockwave"
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.CanTouch = false
	ring.CastShadow = false
	ring.Material = Enum.Material.Neon
	ring.Color = color
	ring.Shape = Enum.PartType.Cylinder
	ring.Size = Vector3.new(0.15, 1, 1)
	ring.CFrame = CFrame.new(position) * CFrame.Angles(0, 0, math.rad(90))
	ring.Transparency = 0.2
	ring.Parent = workspace
	local info = TweenInfo.new(duration, Enum.EasingStyle.Quint, Enum.EasingDirection.Out)
	TweenService:Create(ring, info, { Size = Vector3.new(0.05, maxSize, maxSize), Transparency = 1 }):Play()
	Debris:AddItem(ring, duration + 0.1)
end

function Common.flash(part, color, brightness, range, duration)
	local l = light(part, color, brightness, range)
	TweenService:Create(l, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Brightness = 0 }):Play()
	Debris:AddItem(l, duration + 0.1)
end

-- Particle shapes (Disc/Cylinder/Box) only work when the emitter is inside a BasePart,
-- so ring-shaped emitters get an invisible helper part welded to the ore.
local function shapePart(part, name, size, offset)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Transparency = 1
	p.Anchored = part.Anchored
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Massless = true
	p.CFrame = part.CFrame * (offset or CFrame.identity)
	if not part.Anchored then
		local w = Instance.new("WeldConstraint")
		w.Part0 = part
		w.Part1 = p
		w.Parent = p
	end
	p.Parent = part
	return p
end

-- ------------------------------------------------------------------ anime aura (generic)
-- Layered anime aura: tall flame-tongue spikes rising around the ore, pale inner
-- spikes, short spikes hugging the surface, body glow, optional electricity,
-- rising sparks, floating pebbles, a pulsing ground ring and a breathing light.
-- opts = { outer, inner, pale, glow, spark, lightning (Color3|nil), pebbles (bool),
--          height (1 = SSJ), rate (1), ring (bool), light (bool), emission }
function OreVFX.Aura(part, W, H, opts)
	local hm = (opts.height or 1) * math.min(1, (8 / W) ^ 0.75) -- big ores (bosses) get proportionally shorter flames
	local rm = opts.rate or 1
	local ring = shapePart(part, "Aura_Ring", Vector3.new(W * 0.8, 0.2, W * 0.5), CFrame.new(0, -H * 0.4 + 0.3, 0))
	local floor = shapePart(part, "Aura_Floor", Vector3.new(W * 1.6, 0.2, W * 1.6), CFrame.new(0, -H * 0.4 + 0.1, 0))

	emitter(ring, "Aura_Spikes", {
		Texture = TX.aura_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
		FlipbookMode = Enum.ParticleFlipbookMode.OneShot,
		Color = CS(opts.outer, opts.inner), LightEmission = opts.emission or 0.25,
		Size = NS({ 0, W * 0.45 * hm }, { 0.5, W * 0.7 * hm }, { 1, W * 0.4 * hm }), Squash = NS(1.1),
		Transparency = NS({ 0, 0.15 }, { 0.7, 0.25 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.5, 0.75), Rate = 55 * rm,
		Speed = NumberRange.new(W * 1.4 * hm, W * 2.0 * hm), Drag = 3, Acceleration = Vector3.new(0, W * 0.6, 0),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(4, 4),
		Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
		Orientation = Enum.ParticleOrientation.FacingCameraWorldUp, ZOffset = -2,
	})
	emitter(ring, "Aura_SpikesInner", {
		Texture = TX.aura_spike, Color = CS(opts.pale, opts.inner), LightEmission = 0.6,
		Size = NS({ 0, W * 0.25 * hm }, { 0.35, W * 0.5 * hm }, { 1, W * 0.2 * hm }), Squash = NS(1.3),
		Transparency = NS({ 0, 0.1 }, { 0.6, 0.2 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.35, 0.55), Rate = 45 * rm, Speed = NumberRange.new(W * 1.8 * hm, W * 2.6 * hm), Drag = 4,
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(3, 3),
		Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
		Orientation = Enum.ParticleOrientation.FacingCameraWorldUp, ZOffset = -0.5,
	})
	emitter(part, "Aura_Skin", {
		Texture = TX.aura_spike, Color = CS(opts.pale, opts.outer), LightEmission = 0.45,
		Size = NS({ 0, W * 0.18 }, { 0.4, W * 0.32 }, { 1, W * 0.12 }), Squash = NS(0.9),
		Transparency = NS({ 0, 0.2 }, { 0.7, 0.3 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.3, 0.45), Rate = 70 * rm, Speed = NumberRange.new(W * 0.6, W * 1.0),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(5, 5), Acceleration = Vector3.new(0, W * 1.5, 0),
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
		Orientation = Enum.ParticleOrientation.FacingCameraWorldUp, ZOffset = 0.8,
	})
	emitter(part, "Aura_Body", {
		Texture = TX.glow_soft, Color = CS(opts.glow or opts.inner), LightEmission = 0.5, LockedToPart = true,
		Size = NS(W * 1.35), Transparency = NS({ 0, 1 }, { 0.5, 0.55 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.3), Rate = 12, Speed = NumberRange.new(0), ZOffset = -3,
	})
	if opts.lightning then
		emitter(part, "Aura_Lightning", {
			Texture = TX.lightning_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
			FlipbookMode = Enum.ParticleFlipbookMode.Random,
			Color = CS(opts.lightning), LightEmission = 1, Size = NS({ 0, W * 0.35 }, { 1, W * 0.45 }),
			Transparency = NS({ 0, 0 }, { 0.7, 0 }, { 1, 1 }), Lifetime = NumberRange.new(0.06, 0.12), Rate = 7,
			Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 360), LockedToPart = true, ZOffset = 1,
			Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
		})
	end
	emitter(floor, "Aura_Sparks", {
		Texture = TX.sparkle_diamond, Color = CS(opts.spark or opts.pale), LightEmission = 1, Size = NS({ 0, W * 0.06 }, { 1, 0 }),
		Lifetime = NumberRange.new(0.5, 0.9), Rate = 30 * rm, Speed = NumberRange.new(W * 1.5, W * 3), Drag = 1.5,
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(10, 10),
		Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
	})
	if opts.pebbles then
		emitter(floor, "Aura_Pebbles", {
			Texture = TX.rock_debris_2x2, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid2x2,
			FlipbookMode = Enum.ParticleFlipbookMode.Random,
			Color = CS(rgb(170, 145, 110)), LightEmission = 0, LightInfluence = 1, Size = NS({ 0, W * 0.05 }, { 1, W * 0.035 }),
			Transparency = NS({ 0, 1 }, { 0.1, 0 }, { 0.85, 0 }, { 1, 1 }), Lifetime = NumberRange.new(1.6, 2.4), Rate = 6,
			Speed = NumberRange.new(2, 4), EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(6, 6), Drag = 0.6,
			Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-90, 90),
			Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
		})
	end
	if opts.ring ~= false then
		local ground = attachment(part, "Aura_Ground", Vector3.new(0, -H * 0.4 + 0.08, 0))
		emitter(ground, "Aura_GroundPulse", {
			Texture = TX.shockwave_ring, Color = CS(opts.inner), LightEmission = 0.7, LockedToPart = true,
			Orientation = Enum.ParticleOrientation.VelocityPerpendicular, EmissionDirection = Enum.NormalId.Top,
			Speed = NumberRange.new(0.01), Size = NS({ 0, W * 0.6 }, { 1, W * 1.6 }),
			Transparency = NS({ 0, 0.2 }, { 1, 1 }), Lifetime = NumberRange.new(0.8), Rate = 1.5,
		})
	end
	if opts.light ~= false then
		local l = light(part, opts.inner, 3.4, W * 4)
		TweenService:Create(l, TweenInfo.new(0.3, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), { Brightness = 2.2 }):Play()
	end
end

-- Super Saiyan: golden aura + SSJ2 electricity + floating pebbles.
function OreVFX.SuperSaiyanAura(part, W, H)
	OreVFX.Aura(part, W, H, {
		outer = rgb(255, 170, 10), inner = rgb(255, 205, 40), pale = rgb(255, 248, 170), glow = rgb(255, 196, 30),
		lightning = rgb(150, 225, 255), pebbles = true,
	})
end

-- ------------------------------------------------------------------ effect pieces
local FX = {}

-- sparkles drifting off the ore (every rarity)
function FX.sparkles(c, color, rate)
	emitter(c.part, "Sparkles", {
		Texture = TX.sparkle_diamond, Color = CS(color), LightEmission = 0.8,
		Size = NS({ 0, 0 }, { 0.3, c.W * 0.07 }, { 1, 0 }), Transparency = FADE_SOFT,
		Lifetime = NumberRange.new(1, 1.8), Rate = rate, Speed = NumberRange.new(0.5, 1.2),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(60, 60), Acceleration = Vector3.new(0, 1, 0),
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-120, 120),
	})
end

-- soft pulsing glow behind the ore
function FX.glow(c, color, strength)
	emitter(c.part, "Glow", {
		Texture = TX.glow_soft, Color = CS(color), LightEmission = 0.6, LockedToPart = true,
		Size = NS({ 0, c.W * 1.3 }, { 0.5, c.W * 1.55 }, { 1, c.W * 1.3 }),
		Transparency = NS({ 0, 1 }, { 0.5, 1 - (strength or 0.4) }, { 1, 1 }),
		Lifetime = NumberRange.new(1.4), Rate = 2.2, Speed = NumberRange.new(0), ZOffset = -2,
	})
end

-- short flame tongues licking up from the ore surface
function FX.flames(c, outer, pale, rate, size, name)
	emitter(c.part, name or "Flames", {
		Texture = TX.aura_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
		FlipbookMode = Enum.ParticleFlipbookMode.OneShot,
		Color = CS(pale, outer), LightEmission = 0.5,
		Size = NS({ 0, c.W * 0.15 * size }, { 0.4, c.W * 0.3 * size }, { 1, c.W * 0.1 * size }), Squash = NS(0.7),
		Transparency = NS({ 0, 0.2 }, { 0.7, 0.3 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.45, 0.7), Rate = rate, Speed = NumberRange.new(c.W * 0.5, c.W * 0.9),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(10, 10), Acceleration = Vector3.new(0, c.W * 0.8, 0),
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
		Orientation = Enum.ParticleOrientation.FacingCameraWorldUp, ZOffset = 0.5,
	})
end

function FX.embers(c, color, rate)
	emitter(c.part, "Embers", {
		Texture = TX.sparkle_diamond, Color = CS(rgb(255, 230, 150), color), LightEmission = 1,
		Size = NS({ 0, c.W * 0.05 }, { 1, 0 }), Lifetime = NumberRange.new(0.8, 1.6), Rate = rate,
		Speed = NumberRange.new(c.W * 0.6, c.W * 1.3), EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(40, 40),
		Acceleration = Vector3.new(0, 1.5, 0), Drag = 0.5, RotSpeed = NumberRange.new(-200, 200),
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
	})
end

function FX.bubbles(c, color, rate)
	emitter(c.part, "Bubbles", {
		Texture = TX.bubble, Color = CS(color), LightEmission = 0.4,
		Size = NS({ 0, c.W * 0.03 }, { 1, c.W * 0.1 }), Transparency = NS({ 0, 1 }, { 0.15, 0.1 }, { 0.85, 0.2 }, { 1, 1 }),
		Lifetime = NumberRange.new(1.6, 2.6), Rate = rate, Speed = NumberRange.new(c.W * 0.25, c.W * 0.5),
		EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(25, 25), Acceleration = Vector3.new(0, 0.6, 0),
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
	})
end

-- crescent slashes spinning around the ore (breathing-style sword arcs)
function FX.slashes(c, color, rate, name, offset)
	local a = attachment(c.part, (name or "Slash") .. "_Att", offset or Vector3.zero)
	emitter(a, name or "Slashes", {
		Texture = TX.slash_crescent, Color = CS(rgb(255, 255, 255), color), LightEmission = 0.8,
		Size = NS({ 0, c.W * 0.7 }, { 1, c.W * 1.25 }), Transparency = NS({ 0, 0 }, { 0.6, 0.1 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.3, 0.4), Rate = rate, Speed = NumberRange.new(0),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(500, 700), LockedToPart = true, ZOffset = 1,
	})
	return a
end

-- circle lying on the ground, slowly rotating
function FX.groundDecal(c, texture, color, size, rotSpeed, transparency)
	local a = attachment(c.part, "GroundDecal_Att", Vector3.new(0, -c.H * 0.4 + 0.06, 0))
	emitter(a, "GroundDecal", {
		Texture = texture, Color = CS(color), LightEmission = 0.8, LockedToPart = true,
		Orientation = Enum.ParticleOrientation.VelocityPerpendicular, EmissionDirection = Enum.NormalId.Top,
		Speed = NumberRange.new(0.001), Size = NS(c.W * size),
		Transparency = NS({ 0, 1 }, { 0.15, transparency or 0.1 }, { 0.85, transparency or 0.1 }, { 1, 1 }),
		Lifetime = NumberRange.new(2.4), Rate = 0.9, Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(rotSpeed),
	})
	return a
end

function FX.groundPulse(c, color, rate, maxSize)
	local a = attachment(c.part, "GroundPulse_Att", Vector3.new(0, -c.H * 0.4 + 0.1, 0))
	emitter(a, "GroundPulse", {
		Texture = TX.shockwave_ring, Color = CS(color), LightEmission = 0.8, LockedToPart = true,
		Orientation = Enum.ParticleOrientation.VelocityPerpendicular, EmissionDirection = Enum.NormalId.Top,
		Speed = NumberRange.new(0.001), Size = NS({ 0, c.W * 0.5 }, { 1, c.W * (maxSize or 2) }),
		Transparency = NS({ 0, 0.1 }, { 1, 1 }), Lifetime = NumberRange.new(0.9), Rate = rate,
	})
	return a
end

function FX.lightning(c, color, rate, scale)
	emitter(c.part, "Crackle", {
		Texture = TX.lightning_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
		FlipbookMode = Enum.ParticleFlipbookMode.Random,
		Color = CS(color), LightEmission = 1, Size = NS(c.W * 0.4 * (scale or 1)),
		Transparency = NS({ 0, 0 }, { 0.7, 0 }, { 1, 1 }), Lifetime = NumberRange.new(0.06, 0.12), Rate = rate,
		Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 360), LockedToPart = true, ZOffset = 1,
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
	})
end

-- floating icon above the ore that gently bobs
function FX.floatingIcon(c, texture, size, height)
	local a = attachment(c.part, "Icon_Att", Vector3.new(0, c.H * 0.5 + c.W * (height or 0.45), 0))
	emitter(a, "FloatingIcon", {
		Texture = texture, LightEmission = 0.15, LockedToPart = true,
		Size = NS({ 0, c.W * size * 0.9 }, { 0.5, c.W * size }, { 1, c.W * size * 0.9 }),
		Transparency = NS({ 0, 1 }, { 0.2, 0 }, { 0.8, 0 }, { 1, 1 }),
		Lifetime = NumberRange.new(2), Rate = 0.5, Speed = NumberRange.new(0.001),
		EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 0.25, 0),
	})
	return a
end

-- Rasengan: bright core + fast spinning swirl + wind arcs
function FX.rasengan(c, position)
	local a = attachment(c.part, "Rasengan_Att", position)
	local R = c.W * 0.35
	emitter(a, "Rasengan_Core", {
		Texture = TX.glow_soft, Color = CS(rgb(40, 120, 255)), LightEmission = 0.35, LockedToPart = true,
		Size = NS(R * 1.9), Transparency = NS(0.15), Lifetime = NumberRange.new(0.25), Rate = 20, Speed = NumberRange.new(0),
	})
	emitter(a, "Rasengan_Swirl", {
		Texture = TX.swirl_vortex, Color = CS(rgb(200, 240, 255), rgb(60, 150, 255)), LightEmission = 0.5, LockedToPart = true,
		Size = NS({ 0, R * 1.5 }, { 1, R * 2.0 }), Transparency = NS({ 0, 0 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.3), Rate = 25, Speed = NumberRange.new(0),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-900, -700), ZOffset = 0.5,
	})
	emitter(a, "Rasengan_Wind", {
		Texture = TX.slash_crescent, Color = CS(rgb(220, 245, 255)), LightEmission = 0.4, LockedToPart = true,
		Size = NS({ 0, R * 2.0 }, { 1, R * 2.6 }), Transparency = NS({ 0, 0.35 }, { 1, 1 }),
		Lifetime = NumberRange.new(0.2), Rate = 12, Speed = NumberRange.new(0),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-1200), ZOffset = 1,
	})
	local l = Instance.new("PointLight"); l.Color = rgb(120, 200, 255); l.Brightness = 1.5; l.Range = c.W * 1.5; l.Parent = a
	return a
end

-- ------------------------------------------------------------------ themes
-- Each theme: idle(ctx) builds looping effects, hit(ctx, att) and brk(ctx, att) build bursts.
-- ctx = { part, tier, W (width studs), H (height studs), size (scale) }
local Themes = {}

-- NINJA CHAKRA ----------------------------------------------------------------
Themes.NinjaChakra = {
	colors = { rgb(255, 150, 60), rgb(80, 200, 255), rgb(255, 140, 20), rgb(255, 90, 10) },
	idle = function(c)
		if c.tier == 1 then
			FX.sparkles(c, rgb(255, 190, 120), 2)
		elseif c.tier == 2 then
			FX.sparkles(c, rgb(150, 220, 255), 3)
			FX.flames(c, rgb(40, 150, 255), rgb(200, 240, 255), 10, 0.9, "ChakraFlames")
			FX.glow(c, rgb(80, 180, 255), 0.3)
		elseif c.tier == 3 then
			FX.sparkles(c, rgb(255, 200, 120), 4)
			FX.flames(c, rgb(255, 120, 10), rgb(255, 230, 150), 22, 1.1, "ChakraFlames")
			FX.glow(c, rgb(255, 140, 30), 0.35)
			emitter(c.part, "Leaves", {
				Texture = TX.leaf_particle, Color = CS(rgb(120, 200, 90)), LightEmission = 0, LightInfluence = 1,
				Size = NS(c.W * 0.08), Transparency = FADE_SOFT, Lifetime = NumberRange.new(2.5, 3.5), Rate = 3,
				Speed = NumberRange.new(1, 2), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0.6, -0.8, 0), Drag = 0.8,
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-180, 180),
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
			})
			light(c.part, rgb(255, 140, 30), 3, c.W * 3)
		else
			-- Nine-Tails chakra cloak + Rasengan
			OreVFX.Aura(c.part, c.W, c.H, {
				outer = rgb(230, 60, 0), inner = rgb(255, 130, 10), pale = rgb(255, 210, 120), glow = rgb(255, 110, 20),
				spark = rgb(255, 200, 120), height = 0.85,
			})
			FX.rasengan(c, Vector3.new(0, c.H * 0.5 + c.W * 0.45, 0))
			emitter(c.part, "Leaves", {
				Texture = TX.leaf_particle, Color = CS(rgb(130, 210, 90)), LightEmission = 0, LightInfluence = 1,
				Size = NS(c.W * 0.07), Transparency = FADE_SOFT, Lifetime = NumberRange.new(2, 3), Rate = 5,
				Speed = NumberRange.new(c.W * 0.5, c.W), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(1, -1, 0), Drag = 1,
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-240, 240),
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
			})
		end
	end,
	hit = function(c, att)
		local col = Themes.NinjaChakra.colors[c.tier]
		burst(att, "ChakraHit", {
			Texture = TX.spark_star, Color = CS(col), Size = NS({ 0, c.W * 0.3 }, { 1, 0 }), LightEmission = 1,
			Lifetime = NumberRange.new(0.25, 0.4), Speed = NumberRange.new(8, 14), SpreadAngle = Vector2.new(180, 180), Drag = 4,
		}, 6 + 3 * c.tier, 0.4)
		if c.tier >= 3 then
			burst(att, "ShurikenHit", {
				Texture = TX.icon_shuriken, LightEmission = 0, Size = NS(c.W * 0.12), Transparency = FADE,
				Lifetime = NumberRange.new(0.5, 0.7), Speed = NumberRange.new(10, 16), SpreadAngle = Vector2.new(180, 180),
				Drag = 3, RotSpeed = NumberRange.new(900, 1200),
			}, 3, 0.7)
		end
	end,
	brk = function(c, att)
		local col = Themes.NinjaChakra.colors[c.tier]
		burst(att, "SmokeBomb", {
			Texture = TX.smoke_flipbook_4x4, Color = CS(rgb(245, 245, 245)), LightEmission = 0, LightInfluence = 1,
			FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4, FlipbookMode = Enum.ParticleFlipbookMode.OneShot,
			Size = NS({ 0, c.W * 0.6 }, { 1, c.W * 1.6 }), Lifetime = NumberRange.new(0.9, 1.2),
			Speed = NumberRange.new(c.W, c.W * 2), SpreadAngle = Vector2.new(180, 180), Drag = 3,
		}, 10 + 4 * c.tier, 1.2)
		burst(att, "LeafBurst", {
			Texture = TX.leaf_particle, Color = CS(rgb(130, 210, 90)), LightEmission = 0, LightInfluence = 1,
			Size = NS(c.W * 0.09), Lifetime = NumberRange.new(1, 1.6), Speed = NumberRange.new(c.W * 1.5, c.W * 3),
			SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, -8, 0), Drag = 2, RotSpeed = NumberRange.new(-360, 360),
			Transparency = FADE,
		}, 8 + 4 * c.tier, 1.6)
		burst(att, "ChakraFlash", {
			Texture = TX.glow_soft, Color = CS(col), LightEmission = 1, Size = NS({ 0, c.W }, { 1, c.W * 3 }),
			Transparency = NS({ 0, 0 }, { 1, 1 }), Lifetime = NumberRange.new(0.35), Speed = NumberRange.new(0),
		}, 1, 0.4)
	end,
}

-- DRAGON BALL -----------------------------------------------------------------
Themes.DragonBall = {
	colors = { rgb(255, 190, 80), rgb(255, 160, 40), rgb(90, 200, 255), rgb(255, 225, 60) },
	idle = function(c)
		if c.tier == 1 then
			FX.sparkles(c, rgb(255, 200, 120), 2)
		elseif c.tier == 2 then
			FX.sparkles(c, rgb(255, 180, 60), 4)
			FX.glow(c, rgb(255, 150, 40), 0.3)
			emitter(c.part, "KiMotes", {
				Texture = TX.glow_soft, Color = CS(rgb(255, 220, 150)), LightEmission = 1,
				Size = NS({ 0, c.W * 0.1 }, { 1, 0 }), Lifetime = NumberRange.new(0.8, 1.2), Rate = 8,
				Speed = NumberRange.new(c.W * 0.4, c.W * 0.8), EmissionDirection = Enum.NormalId.Top,
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
			})
		elseif c.tier == 3 then
			-- base-form ki aura (blue-white)
			OreVFX.Aura(c.part, c.W, c.H, {
				outer = rgb(40, 140, 255), inner = rgb(120, 210, 255), pale = rgb(230, 250, 255), glow = rgb(90, 190, 255),
				height = 0.6, rate = 0.6, ring = false, emission = 0.5,
			})
		else
			OreVFX.SuperSaiyanAura(c.part, c.W, c.H)
		end
	end,
	hit = function(c, att)
		local col = Themes.DragonBall.colors[c.tier]
		burst(att, "KiSpark", {
			Texture = TX.spark_star, Color = CS(col), Size = NS({ 0, c.W * 0.35 }, { 1, 0 }), LightEmission = 1,
			Lifetime = NumberRange.new(0.2, 0.35), Speed = NumberRange.new(10, 16), SpreadAngle = Vector2.new(180, 180), Drag = 5,
		}, 8 + 3 * c.tier, 0.4)
	end,
	brk = function(c, att)
		local col = Themes.DragonBall.colors[c.tier]
		burst(att, "KiBlast", {
			Texture = TX.glow_soft, Color = CS(rgb(255, 255, 255), col), LightEmission = 1,
			Size = NS({ 0, c.W * 0.5 }, { 1, c.W * 3.5 }), Transparency = NS({ 0, 0 }, { 1, 1 }),
			Lifetime = NumberRange.new(0.45), Speed = NumberRange.new(0),
		}, 2, 0.5)
		burst(att, "KiSpikes", {
			Texture = TX.aura_spike, Color = CS(rgb(255, 250, 200), col), LightEmission = 0.6,
			Size = NS({ 0, c.W * 0.4 }, { 1, c.W * 0.8 }), Squash = NS(1.2), Transparency = NS({ 0, 0 }, { 1, 1 }),
			Lifetime = NumberRange.new(0.35, 0.5), Speed = NumberRange.new(c.W * 3, c.W * 5), SpreadAngle = Vector2.new(180, 180),
			Orientation = Enum.ParticleOrientation.VelocityParallel, Drag = 4,
		}, 14 + 4 * c.tier, 0.5)
		burst(att, "DragonBalls", {
			Texture = TX.icon_dragonball, LightEmission = 0, Size = NS(c.W * 0.22), Transparency = FADE,
			Lifetime = NumberRange.new(1.2, 1.6), Speed = NumberRange.new(10, 16), SpreadAngle = Vector2.new(60, 60),
			EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -25, 0), RotSpeed = NumberRange.new(-180, 180),
		}, math.min(7, 1 + 2 * c.tier), 1.6)
	end,
}

-- DEMON SLAYER ----------------------------------------------------------------
Themes.DemonSlayer = {
	colors = { rgb(255, 60, 40), rgb(40, 150, 255), rgb(255, 110, 20), rgb(255, 255, 255) },
	idle = function(c)
		local W, H = c.W, c.H
		if c.tier == 1 then
			FX.sparkles(c, rgb(255, 120, 100), 2)
			FX.slashes(c, rgb(255, 60, 40), 0.35, "RedSlash")
		elseif c.tier == 2 then
			-- Water Breathing: spinning water crescents + bubbles + spray
			FX.slashes(c, rgb(40, 150, 255), 2.2, "WaterSlash")
			FX.bubbles(c, rgb(170, 230, 255), 6)
			FX.glow(c, rgb(60, 160, 255), 0.35)
			emitter(c.part, "WaterSpray", {
				Texture = TX.smoke_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
				FlipbookMode = Enum.ParticleFlipbookMode.OneShot, Color = CS(rgb(180, 230, 255)), LightEmission = 0.5,
				Size = NS({ 0, W * 0.2 }, { 1, W * 0.5 }), Transparency = NS({ 0, 0.5 }, { 1, 1 }),
				Lifetime = NumberRange.new(0.6, 0.9), Rate = 8, Speed = NumberRange.new(W * 0.4, W * 0.8),
				EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -W * 0.8, 0),
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
			})
			light(c.part, rgb(60, 160, 255), 3, W * 3)
		elseif c.tier == 3 then
			-- Sun Breathing (Hinokami Kagura): fire crescents + flames + embers
			FX.slashes(c, rgb(255, 110, 20), 2.2, "FireSlash")
			FX.flames(c, rgb(255, 70, 10), rgb(255, 220, 120), 26, 1.2, "SunFlames")
			FX.embers(c, rgb(255, 80, 10), 14)
			FX.glow(c, rgb(255, 110, 30), 0.4)
			light(c.part, rgb(255, 120, 40), 3, W * 3)
		else
			-- Water on the left, Sun on the right, hanafuda earring floating above
			local left = shapePart(c.part, "WaterSide", Vector3.new(W * 0.5, H * 0.8, W * 0.8), CFrame.new(-W * 0.25, 0, 0))
			local right = shapePart(c.part, "FireSide", Vector3.new(W * 0.5, H * 0.8, W * 0.8), CFrame.new(W * 0.25, 0, 0))
			FX.slashes(c, rgb(40, 150, 255), 2.5, "WaterSlash", Vector3.new(-W * 0.3, 0, 0))
			FX.slashes(c, rgb(255, 110, 20), 2.5, "FireSlash", Vector3.new(W * 0.3, 0, 0))
			emitter(right, "SunFlames", {
				Texture = TX.aura_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
				FlipbookMode = Enum.ParticleFlipbookMode.OneShot, Color = CS(rgb(255, 230, 140), rgb(255, 60, 10)),
				LightEmission = 0.5, Size = NS({ 0, W * 0.25 }, { 0.4, W * 0.5 }, { 1, W * 0.15 }), Squash = NS(0.8),
				Transparency = NS({ 0, 0.2 }, { 0.7, 0.3 }, { 1, 1 }), Lifetime = NumberRange.new(0.5, 0.75), Rate = 30,
				Speed = NumberRange.new(W * 0.8, W * 1.4), EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(8, 8),
				Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
				Orientation = Enum.ParticleOrientation.FacingCameraWorldUp,
			})
			emitter(left, "WaterRise", {
				Texture = TX.aura_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
				FlipbookMode = Enum.ParticleFlipbookMode.OneShot, Color = CS(rgb(210, 240, 255), rgb(30, 120, 255)),
				LightEmission = 0.5, Size = NS({ 0, W * 0.25 }, { 0.4, W * 0.45 }, { 1, W * 0.15 }), Squash = NS(0.6),
				Transparency = NS({ 0, 0.25 }, { 0.7, 0.35 }, { 1, 1 }), Lifetime = NumberRange.new(0.6, 0.9), Rate = 24,
				Speed = NumberRange.new(W * 0.6, W * 1.1), EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(8, 8),
				RotSpeed = NumberRange.new(-60, 60),
				Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
				Orientation = Enum.ParticleOrientation.FacingCameraWorldUp,
			})
			FX.bubbles({ part = left, W = W }, rgb(170, 230, 255), 8)
			FX.embers({ part = right, W = W }, rgb(255, 80, 10), 16)
			FX.groundPulse(c, rgb(255, 150, 80), 0.8, 2.2)
			FX.floatingIcon(c, TX.icon_hanafuda, 0.28, 0.35)
			light(c.part, rgb(255, 170, 120), 3, W * 3)
		end
	end,
	hit = function(c, att)
		local col = Themes.DemonSlayer.colors[c.tier]
		burst(att, "SlashHit", {
			Texture = TX.slash_crescent, Color = CS(rgb(255, 255, 255), col), LightEmission = 0.9,
			Size = NS({ 0, c.W * 0.4 }, { 1, c.W * 0.8 }), Transparency = NS({ 0, 0 }, { 1, 1 }),
			Lifetime = NumberRange.new(0.22), Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 360),
		}, 1 + math.floor(c.tier / 2), 0.3)
	end,
	brk = function(c, att)
		burst(att, "CrossSlash", {
			Texture = TX.slash_crescent, Color = CS(rgb(255, 255, 255), rgb(80, 180, 255)), LightEmission = 1,
			Size = NS({ 0, c.W * 1.2 }, { 1, c.W * 2.8 }), Transparency = NS({ 0, 0 }, { 1, 1 }),
			Lifetime = NumberRange.new(0.35), Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 360),
		}, 3, 0.4)
		burst(att, "FireBurst", {
			Texture = TX.aura_flipbook_4x4, Color = CS(rgb(255, 220, 110), rgb(255, 60, 10)), LightEmission = 0.6,
			FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4, FlipbookMode = Enum.ParticleFlipbookMode.OneShot,
			Size = NS({ 0, c.W * 0.5 }, { 1, c.W }), Lifetime = NumberRange.new(0.6, 0.9),
			Speed = NumberRange.new(c.W * 2, c.W * 4), SpreadAngle = Vector2.new(180, 180), Drag = 4,
			Orientation = Enum.ParticleOrientation.VelocityParallel,
		}, 8 + 4 * c.tier, 0.9)
	end,
}

-- SHADOW MANA -----------------------------------------------------------------
Themes.ShadowMana = {
	colors = { rgb(190, 120, 255), rgb(170, 60, 255), rgb(220, 70, 255), rgb(255, 70, 220) },
	idle = function(c)
		local W = c.W
		local col = Themes.ShadowMana.colors[c.tier]
		FX.sparkles(c, col, 1 + c.tier)
		if c.tier >= 2 then
			FX.groundDecal(c, TX.magic_circle, col, 1.2 + 0.35 * c.tier, 20 + 8 * c.tier, 0.2)
			emitter(c.part, "DarkMist", {
				Texture = TX.smoke_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
				FlipbookMode = Enum.ParticleFlipbookMode.OneShot, Color = CS(rgb(40, 10, 70)), LightEmission = 0, LightInfluence = 0,
				Size = NS({ 0, W * 0.3 }, { 1, W * 0.7 }), Transparency = NS({ 0, 0.5 }, { 1, 1 }),
				Lifetime = NumberRange.new(1.4, 2), Rate = 3 * c.tier, Speed = NumberRange.new(W * 0.15, W * 0.35),
				EmissionDirection = Enum.NormalId.Top, Shape = Enum.ParticleEmitterShape.Sphere,
				ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ZOffset = -1,
			})
		end
		if c.tier >= 3 then
			FX.glow(c, col, 0.4)
			emitter(c.part, "Runes", {
				Texture = TX.rune_glyphs_2x2, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid2x2,
				FlipbookMode = Enum.ParticleFlipbookMode.Random, Color = CS(col), LightEmission = 1,
				Size = NS(W * 0.16), Transparency = FADE, Lifetime = NumberRange.new(2, 3), Rate = c.tier,
				Speed = NumberRange.new(W * 0.3, W * 0.5), SpreadAngle = Vector2.new(80, 80), Drag = 1.5,
				EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 0.8, 0), RotSpeed = NumberRange.new(-40, 40),
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
			})
			light(c.part, col, 3, W * 3)
		end
		if c.tier >= 4 then
			-- void aura + black hole in front
			OreVFX.Aura(c.part, W, c.H, {
				outer = rgb(90, 0, 160), inner = rgb(210, 60, 255), pale = rgb(255, 180, 255), glow = rgb(170, 40, 255),
				spark = rgb(255, 150, 255), height = 0.7, rate = 0.7, ring = false, light = false, emission = 0.4,
			})
			local hole = attachment(c.part, "BlackHole", Vector3.new(0, 0, -c.part.Size.Z * 0.5 - 0.3))
			emitter(hole, "VoidSwirl", {
				Texture = TX.swirl_vortex, Color = CS(rgb(255, 120, 240), rgb(160, 40, 255)), LightEmission = 1, LockedToPart = true,
				Size = NS(W * 0.7), Transparency = NS({ 0, 0.1 }, { 1, 1 }), Lifetime = NumberRange.new(0.5),
				Rate = 12, Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(400, 500), ZOffset = 2,
			})
			local inhale = shapePart(c.part, "VoidInhale", Vector3.new(W * 1.4, W * 1.4, W * 1.4), CFrame.new(0, 0, 0))
			emitter(inhale, "Inhale", {
				Texture = TX.sparkle_diamond, Color = CS(rgb(255, 170, 255)), LightEmission = 1, Size = NS({ 0, W * 0.07 }, { 1, 0 }),
				Lifetime = NumberRange.new(0.6), Rate = 30, Speed = NumberRange.new(W, W * 1.4),
				Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward,
				ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface,
			})
		end
	end,
	hit = function(c, att)
		local col = Themes.ShadowMana.colors[c.tier]
		burst(att, "ManaShards", {
			Texture = TX.icon_star4, Color = CS(col), Size = NS({ 0, c.W * 0.2 }, { 1, 0 }), LightEmission = 1,
			Lifetime = NumberRange.new(0.3, 0.5), Speed = NumberRange.new(6, 12), SpreadAngle = Vector2.new(180, 180),
			Drag = 4, RotSpeed = NumberRange.new(-360, 360),
		}, 6 + 2 * c.tier, 0.5)
	end,
	brk = function(c, att)
		local col = Themes.ShadowMana.colors[c.tier]
		burst(att, "Implosion", {
			Texture = TX.swirl_vortex, Color = CS(col), LightEmission = 1, Size = NS({ 0, c.W * 2.5 }, { 1, 0 }),
			Transparency = NS({ 0, 0.5 }, { 1, 0 }), Lifetime = NumberRange.new(0.5), Speed = NumberRange.new(0),
			RotSpeed = NumberRange.new(-720),
		}, 2, 0.6)
		burst(att, "RuneScatter", {
			Texture = TX.rune_glyphs_2x2, Color = CS(col), LightEmission = 1,
			FlipbookLayout = Enum.ParticleFlipbookLayout.Grid2x2, FlipbookMode = Enum.ParticleFlipbookMode.Random,
			Size = NS(c.W * 0.25), Transparency = FADE, Lifetime = NumberRange.new(1, 1.4),
			Speed = NumberRange.new(c.W * 2, c.W * 3), SpreadAngle = Vector2.new(180, 180), Drag = 3,
		}, 6 + 2 * c.tier, 1.4)
	end,
}

-- OCEAN TREASURE --------------------------------------------------------------
Themes.OceanTreasure = {
	colors = { rgb(255, 235, 200), rgb(80, 255, 210), rgb(90, 210, 255), rgb(120, 255, 255) },
	idle = function(c)
		local W = c.W
		local col = Themes.OceanTreasure.colors[c.tier]
		FX.sparkles(c, col, 1 + c.tier)
		if c.tier >= 2 then FX.bubbles(c, rgb(190, 250, 255), 3 * c.tier) end
		if c.tier >= 3 then
			FX.glow(c, rgb(80, 220, 255), 0.35)
			local floor = shapePart(c.part, "CoinFloor", Vector3.new(W, 0.2, W * 0.6), CFrame.new(0, -c.H * 0.3, 0))
			emitter(floor, "CoinHop", {
				Texture = TX.coin_flipbook_4x4, FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4,
				FlipbookMode = Enum.ParticleFlipbookMode.Loop, FlipbookFramerate = NumberRange.new(20, 30), FlipbookStartRandom = true,
				LightEmission = 0.2, Size = NS(W * 0.1), Transparency = NS({ 0, 1 }, { 0.1, 0 }, { 0.8, 0 }, { 1, 1 }),
				Lifetime = NumberRange.new(1, 1.3), Rate = c.tier, Speed = NumberRange.new(W * 1.2, W * 1.6),
				EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(25, 25), Acceleration = Vector3.new(0, -W * 3, 0),
				Shape = Enum.ParticleEmitterShape.Box, ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume,
			})
			light(c.part, rgb(80, 220, 255), 3, W * 3)
		end
		if c.tier >= 4 then
			OreVFX.Aura(c.part, W, c.H, {
				outer = rgb(0, 140, 220), inner = rgb(80, 230, 255), pale = rgb(230, 255, 255), glow = rgb(60, 210, 255),
				spark = rgb(255, 230, 120), height = 0.65, rate = 0.6, light = false, emission = 0.45,
			})
			FX.floatingIcon(c, TX.icon_straw_hat, 0.35, 0.3)
		end
	end,
	hit = function(c, att)
		burst(att, "Splash", {
			Texture = TX.bubble, Color = CS(rgb(190, 250, 255)), Size = NS({ 0, c.W * 0.15 }, { 1, c.W * 0.04 }), LightEmission = 0.5,
			Lifetime = NumberRange.new(0.4, 0.7), Speed = NumberRange.new(6, 10), SpreadAngle = Vector2.new(180, 180),
			Acceleration = Vector3.new(0, -20, 0),
		}, 6 + 2 * c.tier, 0.7)
		if c.tier >= 3 then
			burst(att, "CoinHit", {
				Texture = TX.coin_flipbook_4x4, LightEmission = 0.2,
				FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4, FlipbookMode = Enum.ParticleFlipbookMode.Loop,
				FlipbookFramerate = NumberRange.new(25), Size = NS(c.W * 0.12), Lifetime = NumberRange.new(0.8),
				Speed = NumberRange.new(8, 12), SpreadAngle = Vector2.new(50, 50), EmissionDirection = Enum.NormalId.Top,
				Acceleration = Vector3.new(0, -35, 0),
			}, 2 + c.tier, 0.8)
		end
	end,
	brk = function(c, att)
		burst(att, "CoinFountain", {
			Texture = TX.coin_flipbook_4x4, LightEmission = 0.2,
			FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4, FlipbookMode = Enum.ParticleFlipbookMode.Loop,
			FlipbookFramerate = NumberRange.new(20, 30), FlipbookStartRandom = true,
			Size = NS(c.W * 0.16), Transparency = FADE, Lifetime = NumberRange.new(1.2, 1.8),
			Speed = NumberRange.new(14, 22), SpreadAngle = Vector2.new(35, 35), EmissionDirection = Enum.NormalId.Top,
			Acceleration = Vector3.new(0, -40, 0), RotSpeed = NumberRange.new(-90, 90),
		}, 10 * c.tier, 1.8)
		burst(att, "WaterBurst", {
			Texture = TX.smoke_flipbook_4x4, Color = CS(rgb(190, 240, 255)), LightEmission = 0.4,
			FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4, FlipbookMode = Enum.ParticleFlipbookMode.OneShot,
			Size = NS({ 0, c.W * 0.4 }, { 1, c.W * 1.2 }), Lifetime = NumberRange.new(0.6, 0.9),
			Speed = NumberRange.new(c.W * 1.5, c.W * 3), SpreadAngle = Vector2.new(70, 70), EmissionDirection = Enum.NormalId.Top,
			Acceleration = Vector3.new(0, -30, 0), Drag = 1,
		}, 12, 0.9)
	end,
}

-- HERO IMPACT -----------------------------------------------------------------
Themes.HeroImpact = {
	colors = { rgb(220, 220, 220), rgb(255, 210, 40), rgb(255, 60, 30), rgb(255, 220, 40) },
	idle = function(c)
		local W = c.W
		local col = Themes.HeroImpact.colors[c.tier]
		FX.sparkles(c, col, 1 + c.tier)
		if c.tier >= 2 then FX.lightning(c, col, 1.5 * c.tier, 0.8) end
		if c.tier >= 3 then
			FX.glow(c, col, 0.35)
			FX.groundPulse(c, col, 0.9, 2.4)
			FX.floatingIcon(c, TX.icon_pow, 0.4, 0.3)
			light(c.part, col, 3, W * 3)
		end
		if c.tier >= 4 then
			OreVFX.Aura(c.part, W, c.H, {
				outer = rgb(255, 150, 0), inner = rgb(255, 225, 60), pale = rgb(255, 255, 220), glow = rgb(255, 220, 60),
				height = 0.55, rate = 0.5, ring = false, light = false, emission = 0.4,
			})
			local a = attachment(c.part, "SpeedLines_Att", Vector3.zero)
			emitter(a, "SpeedLines", {
				Texture = TX.speed_lines, Color = CS(rgb(255, 255, 255)), LightEmission = 0.6, LockedToPart = true,
				Size = NS({ 0, W * 1.6 }, { 1, W * 2.4 }), Transparency = NS({ 0, 0.2 }, { 1, 1 }),
				Lifetime = NumberRange.new(0.2), Rate = 2.5, Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 360), ZOffset = -1,
			})
		end
	end,
	hit = function(c, att)
		burst(att, "ImpactStar", {
			Texture = TX.spark_star, Color = CS(rgb(255, 240, 150)), Size = NS({ 0, c.W * 0.6 }, { 1, 0 }), LightEmission = 1,
			Lifetime = NumberRange.new(0.15), Speed = NumberRange.new(0), Rotation = NumberRange.new(0, 90),
		}, 1, 0.2)
		if c.tier >= 3 then
			burst(att, "PowHit", {
				Texture = TX.icon_pow, LightEmission = 0, Size = NS({ 0, c.W * 0.1 }, { 0.2, c.W * 0.45 }, { 1, c.W * 0.38 }),
				Transparency = NS({ 0, 0 }, { 0.6, 0 }, { 1, 1 }), Lifetime = NumberRange.new(0.5),
				Speed = NumberRange.new(3), EmissionDirection = Enum.NormalId.Top, Rotation = NumberRange.new(-20, 20),
			}, 1, 0.5)
		end
	end,
	brk = function(c, att)
		burst(att, "OnePunch", {
			Texture = TX.speed_lines, Color = CS(rgb(255, 255, 255)), LightEmission = 1,
			Size = NS({ 0, c.W * 1.5 }, { 1, c.W * 3.5 }), Transparency = NS({ 0, 0 }, { 1, 1 }),
			Lifetime = NumberRange.new(0.35), Speed = NumberRange.new(0),
		}, 2, 0.4)
		burst(att, "FistPop", {
			Texture = TX.icon_fist, LightEmission = 0, Size = NS({ 0, 0 }, { 0.12, c.W * 1.1 }, { 1, c.W * 0.9 }),
			Transparency = NS({ 0, 0 }, { 0.6, 0 }, { 1, 1 }), Lifetime = NumberRange.new(0.8), Speed = NumberRange.new(0),
		}, 1, 0.8)
	end,
}

-- ------------------------------------------------------------------ public API
local function context(ore, oreType, rarity)
	local part = rootPart(ore)
	assert(part, "OreVFX: ore has no BasePart")
	oreType = oreType or ore:GetAttribute("OreType")
	rarity = rarity or ore:GetAttribute("Rarity")
	local theme = Themes[oreType]
	assert(theme, "OreVFX: unknown OreType " .. tostring(oreType))
	local tier = TIER[rarity] or 1
	local size = oreSize(ore)
	local s = math.max(size.X, size.Z) / 2.5 -- 2.5 studs wide ore = scale 1
	return part, theme, tier, size, s, oreType
end

function OreVFX.Clear(ore)
	local part = rootPart(ore)
	if not part then return end
	local f = part:FindFirstChild("OreVFX_Idle")
	if f then f:Destroy() end
	for _, child in ipairs(part:GetChildren()) do
		if child:GetAttribute("OreVFX") then child:Destroy() end
	end
end

function OreVFX.Attach(ore, oreType, rarity)
	OreVFX.Clear(ore)
	local part, theme, tier, size, s, typeName = context(ore, oreType, rarity)
	local halfY = size.Y / 2
	-- Offsets are relative to the root part's pivot.
	local c = {
		part = part, tier = tier, size = s, W = math.max(size.X, size.Z), H = size.Y,
		center = attachment(part, "VFX_Center", Vector3.new(0, 0, 0)),
		top = attachment(part, "VFX_Top", Vector3.new(0, halfY, 0)),
		base = attachment(part, "VFX_Base", Vector3.new(0, -halfY + 0.05, 0)),
		skyTop = attachment(part, "VFX_SkyTop", Vector3.new(0, halfY + 10 * s, 0)),
	}
	local before = {}
	for _, ch in ipairs(part:GetChildren()) do before[ch] = true end
	theme.idle(c)
	-- Tag everything we created so Clear() can remove it.
	for _, ch in ipairs(part:GetDescendants()) do
		if not before[ch] and ch.Parent == part then ch:SetAttribute("OreVFX", true) end
	end
	for _, a in ipairs({ c.center, c.top, c.base, c.skyTop }) do a:SetAttribute("OreVFX", true) end
	part:SetAttribute("OreVFX_Type", typeName)
end

function OreVFX.Hit(ore, worldPosition, oreType, rarity)
	local part, theme, tier, size, s, typeName = context(ore, oreType, rarity)
	local att = Instance.new("Attachment")
	att.WorldPosition = worldPosition or part.Position
	att.Parent = workspace.Terrain
	Debris:AddItem(att, 3)
	local rockCol = ROCK[typeName][tier]
	burst(att, "Debris", {
		Texture = TX.rock_debris_2x2, Color = CS(rockCol), LightEmission = 0, LightInfluence = 1,
		FlipbookLayout = Enum.ParticleFlipbookLayout.Grid2x2, FlipbookMode = Enum.ParticleFlipbookMode.Random,
		Size = NS({ 0, 0.35 }, { 1, 0.2 }), Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(6, 12),
		SpreadAngle = Vector2.new(60, 60), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -40, 0),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-400, 400),
	}, 5 + tier, 0.8)
	theme.hit({ part = part, tier = tier, size = s, W = math.max(size.X, size.Z), H = size.Y }, att)
end

function OreVFX.Break(ore, oreType, rarity)
	local part, theme, tier, size, s, typeName = context(ore, oreType, rarity)
	local pos = part.Position
	local att = Instance.new("Attachment")
	att.WorldPosition = pos
	att.Parent = workspace.Terrain
	Debris:AddItem(att, 4)
	local rockCol = ROCK[typeName][tier]
	burst(att, "DebrisBig", {
		Texture = TX.rock_debris_2x2, Color = CS(rockCol), LightEmission = 0, LightInfluence = 1,
		FlipbookLayout = Enum.ParticleFlipbookLayout.Grid2x2, FlipbookMode = Enum.ParticleFlipbookMode.Random,
		Size = NS({ 0, 0.8 * s }, { 1, 0.4 * s }), Lifetime = NumberRange.new(0.9, 1.3), Speed = NumberRange.new(12, 22),
		SpreadAngle = Vector2.new(70, 70), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -50, 0),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-300, 300),
	}, 10 + 5 * tier, 1.3)
	burst(att, "Dust", {
		Texture = TX.smoke_flipbook_4x4, Color = CS(rockCol), LightEmission = 0, LightInfluence = 1,
		FlipbookLayout = Enum.ParticleFlipbookLayout.Grid4x4, FlipbookMode = Enum.ParticleFlipbookMode.OneShot,
		Size = NS({ 0, 1.5 * s }, { 1, 4 * s }), Lifetime = NumberRange.new(0.8, 1.1), Speed = NumberRange.new(4, 8),
		SpreadAngle = Vector2.new(180, 30), Drag = 3,
	}, 8 + 2 * tier, 1.1)
	local col = theme.colors[tier]
	Common.shockwave(part, pos - Vector3.new(0, size.Y / 2 - 0.1, 0), col, 6 * s + 3 * tier, 0.45 + 0.1 * tier)
	Common.flash(part, col, 4 + tier * 2, 10 * s + 4 * tier, 0.5)
	theme.brk({ part = part, tier = tier, size = s, W = math.max(size.X, size.Z), H = size.Y }, att)
	OreVFX.Clear(ore)
end

OreVFX.Themes = Themes
return OreVFX

