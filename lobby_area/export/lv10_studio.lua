-- lv10_studio.lua - pos-import do trecho LV10_SECAO (REVISAO 3) no Studio. Rodar via execute_luau (Edit).
-- Etapas: 1) alinhar por _ORIGEM  2) materiais/tints por prefixo  3) luzes  4) agua de Terrain em faixas
-- seguindo a margem curva  5) spawn  6) colisao (RODAR EM LOTES SEPARADOS: uma chamada longa derruba a bridge)
local M = workspace:FindFirstChild("LV10_SECAO")
assert(M, "LV10_SECAO nao encontrado no workspace")
local log = {}
local function L(s) table.insert(log, s) end

-- 1) alinhamento
local org = M:FindFirstChild("_ORIGEM", true)
if org then
	local off = Vector3.new(0, 120, 0) - org.Position
	M:PivotTo(M:GetPivot() + off); org.Transparency = 1; org.CanCollide = false; org.Anchored = true
	L("alinhado " .. tostring(off))
end

-- 2) materiais. tint = multiplicador da textura (separacao de valor: molduras SLT 1.0 > corpo SMD .86 > piso .8)
local SP, NEON, GLASS, METAL = Enum.Material.SmoothPlastic, Enum.Material.Neon, Enum.Material.Glass, Enum.Material.Metal
local W = Color3.new(1, 1, 1)
local MAP = {
	SMD = {mat = SP, tex = true, col = Color3.fromRGB(190, 182, 168), tint = .86, coll = "precise"},   -- corpo (pedra clara-media)
	SLT = {mat = SP, tex = true, col = Color3.fromRGB(228, 223, 212), tint = 1.0, coll = "voxel"},     -- marfim (molduras, pilastras, balaustres)
	ASH = {mat = SP, tex = true, col = Color3.fromRGB(212, 206, 194), tint = .84, coll = "precise"},   -- muretas, saias, pilares de ponte
	FLR = {mat = SP, tex = true, col = Color3.fromRGB(214, 207, 192), tint = .80, coll = "precise"},   -- piso praca/passeios
	FLL = {mat = SP, tex = true, col = Color3.fromRGB(222, 216, 202), tint = .82, coll = "precise"},   -- piso patamar/terraco/escada
	FLF = {mat = SP, tex = true, col = Color3.fromRGB(222, 216, 202), tint = .82, coll = "none"},      -- lamina com folhas
	GLD = {mat = METAL, tex = true, col = Color3.fromRGB(226, 180, 82), tint = .9, refl = 0.06, coll = "none"},
	LPS = {mat = SP, tex = true, col = Color3.fromRGB(34, 78, 190), coll = "none"},
	GRS = {mat = SP, tex = true, col = Color3.fromRGB(110, 186, 88), tint = .82, coll = "voxel"},
	RCK = {mat = SP, tex = true, col = Color3.fromRGB(140, 142, 148), tint = .9, coll = "precise"},
	SLA = {mat = SP, tex = true, col = Color3.fromRGB(120, 138, 160), coll = "voxel"},
	MLK = {mat = NEON, col = Color3.fromRGB(255, 236, 200), coll = "none"},
	EMB = {mat = NEON, col = Color3.fromRGB(255, 128, 40), coll = "none"},
	FRG = {mat = NEON, col = Color3.fromRGB(246, 196, 110), coll = "none"},
	CYN = {mat = NEON, col = Color3.fromRGB(120, 225, 255), coll = "none"},
	GLS = {mat = GLASS, col = Color3.fromRGB(130, 196, 220), transp = 0.3, refl = 0.12, coll = "none"},
	WTR = {mat = GLASS, col = Color3.fromRGB(190, 230, 245), transp = 0.45, refl = 0.1, coll = "none"},
	FOAM = {mat = SP, col = Color3.fromRGB(236, 248, 250), coll = "none"},
	DRK = {mat = SP, col = Color3.fromRGB(38, 34, 36), coll = "none"},
	LFG = {mat = SP, tex = true, col = Color3.fromRGB(236, 192, 86), tint = .92, coll = "none"},
	LFG2 = {mat = SP, tex = true, col = Color3.fromRGB(222, 168, 60), tint = .9, coll = "none"},
	LFV = {mat = SP, tex = true, col = Color3.fromRGB(104, 178, 90), tint = .7, coll = "none"},
	LFP = {mat = SP, col = Color3.fromRGB(238, 210, 146), coll = "none"},
	TRK = {mat = SP, col = Color3.fromRGB(92, 70, 52), coll = "none"},
	FLW = {mat = SP, col = Color3.fromRGB(246, 176, 206), coll = "none"},
	WHT = {mat = SP, col = Color3.fromRGB(236, 232, 224), coll = "voxel"},
}
local n, nsa = 0, 0
for _, p in ipairs(M:GetDescendants()) do
	if p:IsA("MeshPart") then
		n += 1; p.Anchored = true
		local pre = p.Name:match("^(%u+%d*)__"); local cfg = pre and MAP[pre]
		if cfg then
			p.Material = cfg.mat; p.Reflectance = cfg.refl or 0; p.Transparency = cfg.transp or 0
			local sa = p:FindFirstChildOfClass("SurfaceAppearance"); local hasTex = (p.TextureID ~= "")
			if sa then nsa += 1 end
			if cfg.tex and (sa or hasTex) then
				local t = cfg.tint or 1
				if sa then p.Color = W; sa.Color = Color3.new(t, t, t) else p.Color = Color3.new(t, t, t) end
			else
				p.Color = cfg.col
				if sa and not cfg.tex then sa:Destroy() end
				if not cfg.tex then p.TextureID = "" end
			end
			p.CastShadow = (cfg.mat ~= NEON)
			p.CanCollide = false
			p:SetAttribute("LV10_coll", cfg.coll)
		end
	end
end
L(("meshparts %d, com SurfaceAppearance %d"):format(n, nsa))

-- 3) luzes
local lights = M:FindFirstChild("Luzes") or Instance.new("Folder"); lights.Name = "Luzes"; lights.Parent = M; lights:ClearAllChildren()
local function light(name, pos, color, range, bright)
	local a = Instance.new("Part"); a.Name = name; a.Anchored = true; a.CanCollide = false; a.CanQuery = false
	a.Transparency = 1; a.Size = Vector3.new(.5, .5, .5); a.Position = pos; a.Parent = lights
	local pl = Instance.new("PointLight"); pl.Color = color; pl.Range = range; pl.Brightness = bright; pl.Shadows = false; pl.Parent = a
end
local warm = Color3.fromRGB(255, 236, 200)
for _, s in ipairs({-1, 1}) do
	light("Lanterna_escada", Vector3.new(s * 10.7, 14.8, -87.6), warm, 16, .8)
	light("Lanterna_patamar", Vector3.new(s * 21.0, 14.5, -71.0), warm, 16, .8)
	light("Sconce", Vector3.new(s * 9.4, 17.6, -110.5), Color3.fromRGB(255, 150, 60), 10, 1.0)
	light("NichoDourado", Vector3.new(s * 11.0, 13.5, -113.5), Color3.fromRGB(255, 215, 130), 9, .5)
	light("NichoAla", Vector3.new(s * 27.5, 15, -127.5), Color3.fromRGB(255, 215, 130), 10, .5)
	light("AlcovaTeto", Vector3.new(s * 3, 24, -115), Color3.fromRGB(255, 228, 190), 14, 1.0)
end
light("BocaForja", Vector3.new(0, 12.5, -119.0), Color3.fromRGB(255, 130, 50), 18, 1.5)
light("VitralForja", Vector3.new(0, 48.0, -111.0), Color3.fromRGB(255, 215, 130), 24, .6)

-- 4) agua de Terrain em faixas seguindo a margem curva (raio 43.2 em torno de (s*20,-80)); nada fora do muro nem dentro do tambor
local T = workspace.Terrain
T:FillBlock(CFrame.new(0, -0.9, -80), Vector3.new(170, 4, 64), Enum.Material.Air)
for _, s in ipairs({-1, 1}) do
	local z = -103.6
	while z < -56.4 do
		local zc = math.min(z + 1.2, -56.4 - 1.2)
		local xmax = 20 + math.sqrt(math.max(0, 43.2 ^ 2 - (zc + 80) ^ 2))
		if xmax > 34.6 then T:FillBlock(CFrame.new(s * (34.2 + xmax) / 2, -0.9, zc), Vector3.new(xmax - 34.2, 3.0, 2.4), Enum.Material.Water) end
		z += 2.4
	end
end
T.WaterTransparency = 0.84; T.WaterReflectance = 0.14; T.WaterColor = Color3.fromRGB(64, 186, 202); T.WaterWaveSize = 0.12; T.WaterWaveSpeed = 9
-- lajes sob os espelhos: a grade de voxels (4 studs) deixa agua ate y=-4, abaixo do fundo RCK (-2.8); as lajes escondem isso
local lj = M:FindFirstChild("LajesSubAgua") or Instance.new("Folder"); lj.Name = "LajesSubAgua"; lj.Parent = M; lj:ClearAllChildren()
for _, s in ipairs({-1, 1}) do
	local p = Instance.new("Part"); p.Name = "LajeSubAgua"; p.Anchored = true; p.CanCollide = false; p.CastShadow = false
	p.Material = Enum.Material.Slate; p.Color = Color3.fromRGB(96, 98, 104)
	p.Size = Vector3.new(34, 2.6, 52); p.Position = Vector3.new(s * 49, -4.1, -80); p.Parent = lj
end

-- 5) spawn sob o medalhao (plataforma baixa em y=5.16)
local msp = workspace:FindFirstChild("Mystical Spawn Point")
if msp then local sl = msp:FindFirstChildWhichIsA("SpawnLocation", true); if sl then sl.Position = Vector3.new(0, 4.6, -66); sl.Transparency = 1 end end

-- 6) colisao: aplicar em lotes (ex.: precise A = FLL/FLR/ASH; voxel = SLT/GRS/SLA/WHT; precise B = SMD/RCK)
--   for _, p in ipairs(M:GetDescendants()) do if p:IsA("MeshPart") and p:GetAttribute("LV10_coll") == "voxel" then p.CollisionFidelity = Enum.CollisionFidelity.Default; p.CanCollide = true end end
return table.concat(log, "\n")
