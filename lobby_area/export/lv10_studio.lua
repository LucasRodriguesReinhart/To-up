-- lv10_studio.lua - pos-import do trecho LV10_SECAO no Studio (rodar via execute_luau, datamodel Edit)
-- 1) alinha pelo marcador _ORIGEM  2) aplica material/cor/colisao por prefixo  3) luzes das lanternas/forja
-- 4) agua de Terrain nos espelhos d'agua  5) spawn sob o medalhao
local M = workspace:FindFirstChild("LV10_SECAO")
assert(M, "LV10_SECAO nao encontrado no workspace")
local log = {}
local function L(s) table.insert(log, s) end

-- ---------- 1) alinhamento ----------
local org = M:FindFirstChild("_ORIGEM", true)
if org then
	local off = Vector3.new(0, 120, 0) - org.Position
	M:PivotTo(M:GetPivot() + off)
	L(("alinhado: offset %s"):format(tostring(off)))
	org.Transparency = 1; org.CanCollide = false; org.Anchored = true
end

-- ---------- 2) materiais ----------
local SP, NEON, GLASS, METAL = Enum.Material.SmoothPlastic, Enum.Material.Neon, Enum.Material.Glass, Enum.Material.Metal
local W = Color3.new(1, 1, 1)
-- COLISAO (licao do teste de caminhada): meshes fundidos por material com componentes separados
-- NAO podem usar Box (a caixa envolve tudo: os troncos dos dois canteiros viraram uma parede invisivel
-- atravessando a escada) nem sempre Precise (a decomposicao pode ligar componentes distantes).
-- Regra: pisos/estruturas = precise; decorativos separados (balaustres, troncos, canteiros) = voxel (Default) ou sem colisao.
local MAP = {
	SDK = {mat = SP, tex = true, col = Color3.fromRGB(128, 118, 106), coll = "precise"},
	SLT = {mat = SP, tex = true, col = Color3.fromRGB(188, 190, 196), coll = "voxel"},
	ASH = {mat = SP, tex = true, col = Color3.fromRGB(204, 200, 190), coll = "precise"},
	FLR = {mat = SP, tex = true, col = Color3.fromRGB(212, 205, 190), coll = "precise"},
	FLL = {mat = SP, tex = true, col = Color3.fromRGB(222, 216, 202), coll = "precise"},
	GLD = {mat = METAL, tex = true, col = Color3.fromRGB(222, 176, 78), refl = 0.12, coll = "none"},
	LPS = {mat = SP, tex = true, col = Color3.fromRGB(34, 78, 190), coll = "none"},
	GRS = {mat = SP, tex = true, col = Color3.fromRGB(110, 186, 88), coll = "voxel"},
	RCK = {mat = SP, tex = true, col = Color3.fromRGB(132, 136, 142), coll = "precise"},
	SLA = {mat = SP, tex = true, col = Color3.fromRGB(96, 112, 132), coll = "voxel"},
	MLK = {mat = NEON, col = Color3.fromRGB(255, 236, 200), coll = "none"},   -- vidro leitoso luminoso da lanterna
	EMB = {mat = NEON, col = Color3.fromRGB(255, 128, 40), coll = "none"},
	FRG = {mat = NEON, col = Color3.fromRGB(255, 208, 110), coll = "none"},
	CYN = {mat = NEON, col = Color3.fromRGB(120, 225, 255), coll = "none"},
	GLS = {mat = GLASS, col = Color3.fromRGB(120, 190, 215), transp = 0.3, refl = 0.12, coll = "none"},
	WTR = {mat = GLASS, col = Color3.fromRGB(52, 170, 210), transp = 0.35, refl = 0.08, coll = "none"},
	DRK = {mat = SP, col = Color3.fromRGB(28, 26, 30), coll = "none"},
	LFG = {mat = SP, col = Color3.fromRGB(236, 192, 86), coll = "none"},
	LFG2 = {mat = SP, col = Color3.fromRGB(222, 168, 60), coll = "none"},
	LFV = {mat = SP, col = Color3.fromRGB(104, 178, 90), coll = "none"},
	TRK = {mat = SP, col = Color3.fromRGB(92, 70, 52), coll = "box"},
	FLW = {mat = SP, col = Color3.fromRGB(246, 176, 206), coll = "none"},
	WHT = {mat = SP, col = Color3.fromRGB(236, 236, 232), coll = "precise"},
}
local nTex, nSA, nParts = 0, 0, 0
for _, p in ipairs(M:GetDescendants()) do
	if p:IsA("MeshPart") then
		nParts += 1
		p.Anchored = true
		local pre = p.Name:match("^(%u+%d*)__")
		local cfg = pre and MAP[pre]
		if cfg then
			p.Material = cfg.mat
			p.Reflectance = cfg.refl or 0
			p.Transparency = cfg.transp or 0
			local sa = p:FindFirstChildOfClass("SurfaceAppearance")
			local hasTex = (p.TextureID ~= nil and p.TextureID ~= "")
			if sa then nSA += 1 end
			if hasTex then nTex += 1 end
			if cfg.tex and (sa or hasTex) then
				p.Color = W                      -- textura ja carrega a cor
			else
				p.Color = cfg.col
				if not cfg.tex and sa then sa:Destroy() end
			end
			if cfg.coll == "precise" then
				p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
			elseif cfg.coll == "voxel" then
				p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.Default
			elseif cfg.coll == "box" then
				p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.Box
			else
				p.CanCollide = false
			end
			p.CastShadow = (cfg.mat ~= NEON)
		else
			L("sem mapeamento: " .. p.Name)
		end
	end
end
L(("meshparts %d | com TextureID %d | com SurfaceAppearance %d"):format(nParts, nTex, nSA))

-- ---------- 3) luzes ----------
local lights = M:FindFirstChild("Luzes") or Instance.new("Folder"); lights.Name = "Luzes"; lights.Parent = M
lights:ClearAllChildren()
local function light(name, pos, color, range, bright)
	local a = Instance.new("Part"); a.Name = name; a.Anchored = true; a.CanCollide = false; a.CanQuery = false
	a.Transparency = 1; a.Size = Vector3.new(0.5, 0.5, 0.5); a.Position = pos; a.Parent = lights
	local pl = Instance.new("PointLight"); pl.Color = color; pl.Range = range; pl.Brightness = bright; pl.Shadows = false; pl.Parent = a
end
local warm = Color3.fromRGB(255, 236, 200)
for _, s in ipairs({-1, 1}) do
	light("Lanterna_escada", Vector3.new(s * 14.2, 19.1, -87.6), warm, 22, 1.1)
	light("Lanterna_patamar", Vector3.new(s * 23.0, 16.5, -72.0), warm, 22, 1.1)
	light("Braseiro", Vector3.new(s * 10.6, 15.6, -109.0), Color3.fromRGB(255, 150, 60), 14, 1.4)
	light("NichoDourado", Vector3.new(s * 15.0, 15.0, -113.0), Color3.fromRGB(255, 215, 130), 12, 0.8)
end
light("BocaForja", Vector3.new(0, 13.0, -122.0), Color3.fromRGB(255, 130, 50), 26, 2.0)
light("VitralForja", Vector3.new(0, 48.0, -111.0), Color3.fromRGB(255, 215, 130), 30, 1.0)

-- ---------- 4) agua de Terrain nos espelhos ----------
local T = workspace.Terrain
for _, s in ipairs({-1, 1}) do
	T:FillBlock(CFrame.new(s * 48.5, -0.7, -80), Vector3.new(30.4, 2.6, 47.6), Enum.Material.Water)
end
T.WaterColor = Color3.fromRGB(40, 160, 205)
T.WaterTransparency = 0.5
T.WaterReflectance = 0.35
T.WaterWaveSize = 0.08
T.WaterWaveSpeed = 8
L("agua de terrain preenchida")

-- ---------- 5) spawn sob o medalhao ----------
local msp = workspace:FindFirstChild("Mystical Spawn Point")
if msp then
	local sl = msp:FindFirstChildWhichIsA("SpawnLocation", true)
	if sl then sl.Position = Vector3.new(0, 4.4, -66); sl.Transparency = 1; L("spawn em " .. tostring(sl.Position)) end
	for _, p in ipairs(msp:GetDescendants()) do
		if p:IsA("BasePart") and not p:IsA("SpawnLocation") then p.Transparency = 1; p.CanCollide = false end
	end
end
return table.concat(log, "\n")
