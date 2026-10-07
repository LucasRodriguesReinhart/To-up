-- trecho_studio.lua - pos-import do TRECHO_AMOSTRA (execute_luau, Edit). Alinha por _ORIGEM, ajusta materiais
-- (o importador ja cria SurfaceAppearance com albedo/normal/rugosidade), foliage com alpha e dupla face,
-- luminosos, colisao por grupo, agua de Terrain na margem, luzes de apoio.
local M = workspace:FindFirstChild("TRECHO_AMOSTRA")
assert(M, "TRECHO_AMOSTRA nao encontrado")
local log = {}
local function L(s) table.insert(log, s) end
-- 1) alinhar: origem do Blender (0,0,0) = ponto do avatar; no jogo, spawn em z=-66 -> desloca o trecho para la
local ORIGEM_ROBLOX = Vector3.new(0, 0, -66)
local org = M:FindFirstChild("_ORIGEM", true)
if org then
	local off = (ORIGEM_ROBLOX + Vector3.new(0, 120, 0)) - org.Position
	M:PivotTo(M:GetPivot() + off); org.Transparency = 1; org.CanCollide = false; L("alinhado " .. tostring(off))
end
-- 2) materiais / colisao por nome de objeto
local n, sa = 0, 0
for _, p in ipairs(M:GetDescendants()) do
	if p:IsA("MeshPart") then
		n += 1; p.Anchored = true
		local nm = p.Name
		local s = p:FindFirstChildOfClass("SurfaceAppearance"); if s then sa += 1 end
		p.Material = Enum.Material.SmoothPlastic; p.Color = Color3.new(1, 1, 1)
		if nm:find("GOLD") or nm:find("ouro") or nm:find("TRAC_") or nm:find("FRISO") or nm:find("FILETE") or nm:find("anel") or nm:find("lant_") or nm:find("cupula") or nm:find("SIGN_") or nm:find("tampa_anel") or nm:find("tampa_aro") then
			p.Material = Enum.Material.Metal; p.Reflectance = 0.05
		end
		if nm:find("fundo_luz") then p.Material = Enum.Material.Neon; p.Color = Color3.fromRGB(255, 214, 120); if s then s:Destroy() end end
		if nm:find("lant_vidro") then p.Material = Enum.Material.Neon; p.Color = Color3.fromRGB(255, 240, 210); if s then s:Destroy() end end
		if nm:find("_folhas") or nm:find("_cards") then
			p.DoubleSided = true; p.CanCollide = false; p.CastShadow = true
			if s then s.AlphaMode = Enum.AlphaMode.Transparency end
		end
		-- colisao
		if nm:find("TORRE_corpo") or nm:find("ESCADA_degraus") or nm:find("TERRACO") or nm:find("PISO_lajotas") or nm:find("PISO_base") or nm:find("AGUA_leito") or nm:find("AGUA_caixa") or nm:find("ESCADA_bochecha") or nm:find("PEDESTAL") or nm:find("AGUA_meiofio") or nm:find("PORTAL_piso") then
			p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
		elseif nm:find("PISO_curb") or nm:find("AGUA_pedra") or nm:find("TUFO") or nm:find("haste") or nm:find("base") then
			p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.Default
		else
			p.CanCollide = false
		end
	end
end
L(("meshparts %d, SurfaceAppearance %d"):format(n, sa))
-- 3) agua de Terrain na margem: x 15.6..27 (Blender) -> Roblox x -27..-15.6 ; y -21..-2 (Blender) -> Roblox z -87..-68 ; topo -0.35
local T = workspace.Terrain
T:FillBlock(CFrame.new(-21.3, -1.6, -77.5), Vector3.new(11.4, 2.5, 19.0), Enum.Material.Water)
T.WaterTransparency = 0.9; T.WaterReflectance = 0.25; T.WaterColor = Color3.fromRGB(60, 150, 165); T.WaterWaveSize = 0.08; T.WaterWaveSpeed = 8
-- 4) luzes quentes no portal e nos nichos (sem bloom extra)
local lf = M:FindFirstChild("Luzes") or Instance.new("Folder"); lf.Name = "Luzes"; lf.Parent = M; lf:ClearAllChildren()
local function light(pos, col, range, br)
	local a = Instance.new("Part"); a.Anchored = true; a.CanCollide = false; a.CanQuery = false; a.Transparency = 1; a.Size = Vector3.new(.5, .5, .5); a.Position = pos; a.Parent = lf
	local pl = Instance.new("PointLight"); pl.Color = col; pl.Range = range; pl.Brightness = br; pl.Shadows = false; pl.Parent = a
end
light(Vector3.new(0, 4.5 + 5, -66 - 36), Color3.fromRGB(255, 220, 140), 16, 1.2)
for _, s in ipairs({-1, 1}) do
	light(Vector3.new(s * 10.5, 4.5 + 4, -66 - 34.5), Color3.fromRGB(255, 220, 140), 8, .6)
	light(Vector3.new(s * 10.6, 4.5 + 1.3 + 7.2, -66 - 28.5), Color3.fromRGB(255, 236, 200), 12, .7)
end
-- 5) spawn no ponto do avatar (origem do trecho), sobre o piso (topo 0 -> Roblox y 0)
local msp = workspace:FindFirstChild("Mystical Spawn Point")
if msp then local sl = msp:FindFirstChildWhichIsA("SpawnLocation", true); if sl then sl.Position = Vector3.new(0, -0.6, -60); sl.Transparency = 1 end end
return table.concat(log, "\n")
