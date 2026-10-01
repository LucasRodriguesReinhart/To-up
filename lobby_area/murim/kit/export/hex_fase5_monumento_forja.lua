-- hex_fase5_monumento_forja.lua : F5 = central monument (stepped hex, red drum, gold rims, pickaxe, glowing orb),
-- 4 banner planters + 2 forge flank beds (all EMPTY), forge fixes (furnace out of the Ignis bay, placa turned to the
-- plaza, 61 forge balustrades to 3.4, stair-top lanterns, hx_f5_ignis), stone lions in pairs on plinths. No accents.
-- Idempotent: H.clear(HEX_Monumento), H.clear(HEX_Canteiros), H.clearColliders("hx_f5_"), own HEX_Detalhes items
-- removed by name; every existing-instance placement is computed from CF0/S0 or absolute constants.
-- On any error after writes began, the ChangeHistory recording is CANCELLED.
-- Deviations from the spec text (all measured, see the report):
-- * LOB_fornalha CF0 has yaw 180 (live: ry -180), so the spec's CF0*CFrame.new(0,0,-3.2) would move it +3.2 in WORLD
--   Z, INTO Ignis. Applied CF0 + Vector3.new(0,0,-3.2) (world translation), which gives the spec's stated intent:
--   Z -116 -> -119.2, front -114.0, clear of back_hump -113.65.
-- * Patio KIT_placa (0,29.13,-104.57): lettered side is local -Z and its LookVector is (0,0,-1), so the letters face
--   the forge back wall and the plaza sees the blank back. Rotated CF0*CFrame.Angles(0,pi,0) as the spec instructs
--   for that case (confirmed with the V9 capture afterwards).
-- * Reviewer pendencia from F2/F3: the BR planter at (23.5,-40.7) sat in the spawn-to-gallery sightline (and grazed
--   the direct spawn-to-gallery-stair walk line), and the banners tagged PLANTER_BR/PLANTER_FR still stood in the
--   plaza rows at (46,11.1,-52)/(46,11.1,-31), also in that sightline. The banners now stand in their planters, and
--   the BR planter moved out along its own 300-degree vertex ray, radius 47 -> 75: (37.5,0,-64.95). The BL planter
--   mirrors it at (-37.5,0,-64.95): its old spot grazed the spawn-to-shop walk line the same way, and the pair keeps
--   the layout symmetric. Min distance from every sight segment (spawn to stairs, pad and all 6 discos) is asserted.
-- * Moving the two planters exposes the F2 joint-clip gaps on the 240/300 vertex-ray radials (r 43..51). Each gap is
--   measured live from the two neighbouring HEX_Chao Junta strips and filled with a matching strip in HEX_Canteiros.
-- * The pickaxe is set CanCollide/CanTouch/CanQuery false (decorative MeshPart per the collider plan; the handle
--   collider hx_f5_mon_cabo is the walk hitbox and the head is unreachable on purpose).
-- PICARETA_FLAT: set true only if the V8 capture shows the pickaxe blurry/blotchy (flat gold switch, reversible
-- from Color0/Alpha0). Default false = keep the baked texture.
local PICARETA_FLAT = false

local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, COL, C = H.L, H.COL, H.C
local CHS = game:GetService("ChangeHistoryService")
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end
local function v3s(v) return ("(%.2f,%.2f,%.2f)"):format(v.X, v.Y, v.Z) end
for _, k in ipairs({"HEX_F0_OK", "HEX_F1_OK", "HEX_F2_OK", "HEX_F3_OK", "HEX_F4_OK"}) do
	assert(L:GetAttribute(k) == true, "F5: marker " .. k .. " missing (run the earlier phases first)") end

local P, Fo, Pr = L.Patio, L.Forja, L.Props
local MON = L:FindFirstChild("HEX_Monumento")
local CAN = L:FindFirstChild("HEX_Canteiros")
local DET = L:FindFirstChild("HEX_Detalhes")
assert(MON and CAN and DET, "F5: HEX_Monumento / HEX_Canteiros / HEX_Detalhes missing (F0 creates them)")
local NPCS = workspace:FindFirstChild("NPCs")
local IGNIS = NPCS and NPCS:FindFirstChild("Ignis")
assert(IGNIS, "F5: workspace.NPCs.Ignis missing")

-- layout constants
local COS30 = 0.8660254
local PLANTERS = { -- BR/BL moved 47 -> 75 on their vertex rays (reviewer pendencia; see header)
	{role = "PLANTER_FR", pos = Vector3.new(23.5, 0, 40.7)},
	{role = "PLANTER_FL", pos = Vector3.new(-23.5, 0, 40.7)},
	{role = "PLANTER_BL", pos = Vector3.new(-37.5, 0, -75 * COS30)},
	{role = "PLANTER_BR", pos = Vector3.new(37.5, 0, -75 * COS30)},
}
local BEDS = {Vector3.new(47, 0, -86.9), Vector3.new(-47, 0, -86.9)}
local LIONS = {
	{role = "FORGE_M", name = "LOB_leao_esfera", x = 31, z = -69},
	{role = "FORGE_F", name = "LOB_leao_filhote", x = -31, z = -69},
	{role = "GATE_M", name = "LOB_leao_esfera", x = 38, z = 172},
	{role = "GATE_F", name = "LOB_leao_filhote", x = -38, z = 172},
}
local IG_MIN = Vector3.new(-5.99, 9.99, -113.66) -- Ignis AABB, checked in stage 1
local IG_MAX = Vector3.new(5.99, 24.56, -102.05)
local DET_MINE = function(n) return n == "LanternaForjaE" or n == "LanternaForjaW"
	or n:sub(1, 11) == "PlintoLeao_" or n:sub(1, 10) == "DiscoLeao_" end

------------------------------------------------------------------ stage 1: read-only gather + asserts
local bad = {}
for _, f in ipairs({MON, CAN}) do for _, c in ipairs(f:GetChildren()) do
	if not c:GetAttribute("HexGen") then table.insert(bad, f.Name .. " holds a non-generated instance: " .. c:GetFullName()) end end end
for _, c in ipairs(DET:GetChildren()) do
	if not DET_MINE(c.Name) then table.insert(bad, "HEX_Detalhes holds a foreign instance: " .. c:GetFullName()) end end

local function near(a, b, tol) return (a - b).Magnitude <= (tol or 0.3) end

-- pickaxe
local pic = P:FindFirstChild("LOB_picareta_aurora")
if not (pic and pic:IsA("MeshPart")) then table.insert(bad, "Patio.LOB_picareta_aurora missing") end
local picS0 = pic and (pic:GetAttribute("S0") or pic.Size)
if picS0 and not near(picS0, Vector3.new(31.9502, 40, 8.088), 0.2) then table.insert(bad, "picareta S0 unexpected: " .. v3s(picS0)) end

-- furnace
local forn = Fo:FindFirstChild("LOB_fornalha")
local fornCF0 = forn and (forn:GetAttribute("CF0") or forn.CFrame)
if not forn then table.insert(bad, "Forja.LOB_fornalha missing")
elseif not near(fornCF0.Position, Vector3.new(0, 17.08, -116), 0.2) then table.insert(bad, "fornalha CF0 pos unexpected: " .. v3s(fornCF0.Position)) end

-- forge placa
local placa
for _, c in ipairs(P:GetChildren()) do
	if c.Name == "KIT_placa" and near((c:GetAttribute("CF0") and c:GetAttribute("CF0").Position or c.Position), Vector3.new(0, 29.13, -104.57), 0.3) then
		if placa then table.insert(bad, "two forge KIT_placa found") end placa = c end end
if not placa then table.insert(bad, "forge KIT_placa @ (0,29.13,-104.57) not found") end

-- lions and banners by HEX_ROLE
local byRole = {}
for _, c in ipairs(Pr:GetChildren()) do
	local r = c:GetAttribute("HEX_ROLE")
	if r then
		if byRole[r] then table.insert(bad, "duplicate HEX_ROLE " .. r) end
		byRole[r] = c
	end
end
for _, li in ipairs(LIONS) do
	local c = byRole[li.role]
	if not c then table.insert(bad, "lion role missing: " .. li.role)
	elseif c.Name ~= li.name then table.insert(bad, li.role .. " is " .. c.Name .. ", expected " .. li.name) end
end
local banners = {}
for _, pl in ipairs(PLANTERS) do
	local b = byRole[pl.role]
	if not b or b.Name ~= "KIT_estandarte" then table.insert(bad, "banner role missing: " .. pl.role)
	else
		banners[pl.role] = b
		local s0 = b:GetAttribute("S0") or b.Size
		if math.abs(s0.Y - 22.1903) > 0.1 then table.insert(bad, pl.role .. " S0.Y unexpected: " .. tostring(s0.Y)) end
	end
end

-- the 61 forge balustrades (position box; unchanged by fixBal, so stable across runs)
local balSegs = {}
for _, d in ipairs(L:GetDescendants()) do
	if d.Name == "KIT_bal_seg" and d:IsA("BasePart") and d.Position.Z < -85 and math.abs(d.Position.X) < 62.5 then
		table.insert(balSegs, d)
	end
end
if #balSegs ~= 61 then table.insert(bad, ("forge KIT_bal_seg: found %d, expected 61"):format(#balSegs)) end

-- portal discos (sightline targets); Santuario is a top-level workspace model
local discos = {}
local SANT = workspace:FindFirstChild("Santuario")
if SANT then for _, d in ipairs(SANT:GetDescendants()) do
	if d.Name == "Disco" and d:IsA("BasePart") and d:GetAttribute("AreaId") then table.insert(discos, d) end
end end
if #discos ~= 6 then table.insert(bad, ("Santuario Disco count %d, expected 6"):format(#discos)) end

-- Ignis AABB sanity
do
	local cf, sz = IGNIS:GetBoundingBox()
	if not (near(cf.Position, Vector3.new(0, 17.27, -107.86), 0.5) and near(sz, Vector3.new(11.97, 14.55, 11.59), 0.6)) then
		table.insert(bad, "Ignis AABB moved: c" .. v3s(cf.Position) .. " s" .. v3s(sz))
	end
end

-- joint-clip gaps on the 240/300 vertex-ray radials (measured from HEX_Chao only, so stable across runs)
local juntasFolder = L.HEX_Chao:FindFirstChild("Juntas")
local gapFills = {} -- {a=Vector3, b=Vector3}
for _, dir in ipairs({Vector3.new(0.5, 0, -COS30), Vector3.new(-0.5, 0, -COS30)}) do
	local strips = {}
	if juntasFolder then for _, d in ipairs(juntasFolder:GetChildren()) do
		if d.Name == "Junta" and d:IsA("BasePart") then
			local p = d.Position
			local r = p.X * dir.X + p.Z * dir.Z
			local off = math.abs(-p.X * dir.Z + p.Z * dir.X)
			if off < 0.6 and r > 36 and r < 64 then table.insert(strips, {r = r, len = d.Size.Z, y = p.Y}) end
		end end end
	if #strips ~= 2 then table.insert(bad, ("radial %s: %d Junta strips in r 36..64, expected 2"):format(v3s(dir), #strips))
	else
		table.sort(strips, function(u, v) return u.r < v.r end)
		local a = strips[1].r + strips[1].len / 2
		local b = strips[2].r - strips[2].len / 2
		if b - a < 5 or b - a > 11 then table.insert(bad, ("radial %s: gap %.2f..%.2f unexpected"):format(v3s(dir), a, b))
		else table.insert(gapFills, {a = dir * a, b = dir * b, y = strips[1].y}) end
	end
end

-- build spots must be clear (visible parts only; own HexGen parts, tagged banners and lions excluded)
local function spotClear(center, halfX, halfZ, height, groundY, allowFn, label)
	local parts = workspace:GetPartBoundsInBox(CFrame.new(center.X, groundY + height / 2 + 0.3, center.Z), Vector3.new(halfX * 2, height, halfZ * 2))
	for _, q in ipairs(parts) do
		local top = q.Position.Y + q.Size.Y / 2
		if q.Transparency < 0.9 and top > groundY + 0.5 and not q:GetAttribute("HexGen")
			and not (allowFn and allowFn(q)) then
			table.insert(bad, label .. " blocked by " .. q:GetFullName() .. (" top %.2f"):format(top))
		end
	end
end
local isBannerOrLion = function(q)
	local r = q:GetAttribute("HEX_ROLE") return r ~= nil
end
for _, pl in ipairs(PLANTERS) do spotClear(pl.pos, 4.2, 4.2, 12, 0, isBannerOrLion, "planter " .. pl.role) end
for _, bp in ipairs(BEDS) do spotClear(bp, 13.2, 2.7, 5, 0, nil, "bed " .. v3s(bp)) end
for _, li in ipairs(LIONS) do spotClear(Vector3.new(li.x, 0, li.z), 3.5, 3.6, 11, 0, isBannerOrLion, "lion " .. li.role) end

if #bad > 0 then error("F5 aborted before writing anything:\n- " .. table.concat(bad, "\n- ")) end
say("stage 1 OK: picareta, fornalha, placa, 4 lions, 4 banners, 61 bal_seg, 6 discos, 2 radial gaps, spots clear")

------------------------------------------------------------------ stage 2: one ChangeHistory recording
H.selfTest()
say("wedge self-test SIGN = " .. tostring(H.SIGN))
local rec = H.begin("HEX_F5 monumento forja")
local WEDGES = {}

local ok, err = pcall(function()
	-- clear own output
	H.clear(MON) H.clear(CAN) H.clearColliders("hx_f5_")
	for _, c in ipairs(DET:GetChildren()) do if DET_MINE(c.Name) then c:Destroy() end end

	-- hex prism with wedge bookkeeping (same geometry as H.hexPrism, centred on the origin)
	local function hexPrism2(o, ap, y0, y1)
		local R = ap / COS30
		local h = y1 - y0
		local q = {} for k, v in pairs(o) do q[k] = v end
		q.Size = Vector3.new(R, h, 2 * ap) q.CFrame = CFrame.new(0, (y0 + y1) / 2, 0)
		H.part(q, MON)
		for _, sx in ipairs({1, -1}) do for _, sz in ipairs({1, -1}) do
			local Cc = Vector3.new(sx * R / 2, 0, 0)
			local a, b = Vector3.new(sx, 0, 0), Vector3.new(0, 0, sz)
			local w = H.rightTri(MON, o, Cc, a, R / 2, b, ap, y1, h)
			table.insert(WEDGES, {w = w, C = Cc, a = a, la = R / 2, b = b, lb = ap, topY = y1})
		end end
	end

	-- MONUMENT
	hexPrism2({Name = "Mon_passo1", Color = C.creme, CanCollide = true, CastShadow = true}, 20, -0.2, 1.0)
	hexPrism2({Name = "Mon_passo2", Color = C.cremeS, CanCollide = true, CastShadow = true}, 16, 0.9, 2.0)
	hexPrism2({Name = "Mon_anel_base", Color = C.ouro, Material = Enum.Material.Metal, CanCollide = true, CastShadow = true}, 11.1, 1.9, 2.5)
	hexPrism2({Name = "Mon_tambor", Color = C.laca, CanCollide = true, CastShadow = true}, 10.5, 2.4, 8.0)
	hexPrism2({Name = "Mon_aro_topo", Color = C.ouro, Material = Enum.Material.Metal, CanCollide = true, CastShadow = true}, 11.1, 7.9, 8.5)
	for _, th in ipairs({30, 90, 150, 210, 270, 330}) do
		local n = Vector3.new(math.cos(math.rad(th)), 0, math.sin(math.rad(th)))
		H.part({Name = "Mon_emblema", Size = Vector3.new(3.2, 3.2, 0.2),
			CFrame = CFrame.lookAt(n * 10.6 + Vector3.new(0, 5.2, 0), n * 20 + Vector3.new(0, 5.2, 0)),
			Color = C.ouro, Material = Enum.Material.Metal, CanCollide = true, CastShadow = true}, MON)
	end
	local orb = H.part({Name = "Mon_orbe", Shape = Enum.PartType.Ball, Size = Vector3.new(5.5, 5.5, 5.5),
		CFrame = CFrame.new(0, 10.3, 0), Color = C.orbe, Material = Enum.Material.Neon,
		CanCollide = true, CastShadow = true}, MON)
	local ol = Instance.new("PointLight") ol.Range = 16 ol.Brightness = 1.2 ol.Color = C.luz ol.Shadows = false ol.Parent = orb
	-- pickaxe
	H.remember(pic)
	pic.Size = picS0 * 0.85
	pic.CFrame = CFrame.new(0, 25.5, 0)
	pic.Anchored = true pic.CanCollide = false pic.CanTouch = false pic.CanQuery = false
	local psa = pic:FindFirstChildOfClass("SurfaceAppearance")
	if PICARETA_FLAT then
		if pic:GetAttribute("Color0") == nil then pic:SetAttribute("Color0", pic.Color) end
		if psa and pic:GetAttribute("Alpha0") == nil then pic:SetAttribute("Alpha0", psa.AlphaMode.Name) end
		pic.Color = C.ouro pic.Material = Enum.Material.Metal
		if psa then psa.AlphaMode = Enum.AlphaMode.Overlay end
		say("picareta: FLAT GOLD applied (reversible from Color0/Alpha0)")
	else
		say("picareta: baked texture kept (PICARETA_FLAT=false)")
	end
	H.collider("hx_f5_mon_cabo", Vector3.new(4.2, 18.7, 4.2), CFrame.new(0, 17.85, 0))
	say(("monument: %d parts (%d wedges), orb %s, picareta %s size %s"):format(#MON:GetChildren(), #WEDGES, v3s(orb.Position), v3s(pic.Position), v3s(pic.Size)))

	-- PLANTERS (empty) + banners
	for _, pl in ipairs(PLANTERS) do
		local p = pl.pos
		local F = CFrame.lookAt(Vector3.new(p.X, 0, p.Z), Vector3.new(0, 0, 0))
		for _, sz in ipairs({1, -1}) do
			H.part({Name = "Canteiro_borda", Size = Vector3.new(7.4, 1.5, 0.8), CFrame = F * CFrame.new(0, 0.65, 3.3 * sz),
				Color = C.creme, CanCollide = true, CastShadow = true}, CAN)
			H.part({Name = "Canteiro_borda", Size = Vector3.new(0.8, 1.5, 5.8), CFrame = F * CFrame.new(3.3 * sz, 0.65, 0),
				Color = C.creme, CanCollide = true, CastShadow = true}, CAN)
		end
		H.part({Name = "Canteiro_terra", Size = Vector3.new(5.8, 0.5, 5.8), CFrame = F * CFrame.new(0, 1.0, 0),
			Color = C.terra, CanCollide = true}, CAN)
		local b = banners[pl.role]
		local s0 = b:GetAttribute("S0") or b.Size
		H.remember(b)
		b.Size = s0
		local at = Vector3.new(p.X, 12.35, p.Z)
		b.CFrame = CFrame.lookAt(at, at + Vector3.new(p.X, 0, p.Z).Unit)
		say(("planter %s at %s, banner bottom %.2f"):format(pl.role, v3s(p), b.Position.Y - s0.Y / 2))
	end
	-- fill the two exposed radial joint gaps
	for _, g in ipairs(gapFills) do
		local mid = (g.a + g.b) / 2
		H.part({Name = "Junta", Size = Vector3.new(0.5, 0.15, (g.b - g.a).Magnitude),
			CFrame = CFrame.lookAt(Vector3.new(mid.X, g.y, mid.Z), Vector3.new(g.b.X, g.y, g.b.Z)),
			Color = C.junta}, CAN)
		say(("radial junta fill %s -> %s"):format(v3s(g.a), v3s(g.b)))
	end

	-- FORGE FLANK BEDS (empty)
	for _, bp in ipairs(BEDS) do
		for _, sz in ipairs({1, -1}) do
			H.part({Name = "Canteiro_borda", Size = Vector3.new(26, 1.0, 0.8), CFrame = CFrame.new(bp.X, 0.4, bp.Z + 2.1 * sz),
				Color = C.creme, CanCollide = true, CastShadow = true}, CAN)
			H.part({Name = "Canteiro_borda", Size = Vector3.new(0.8, 1.0, 3.4), CFrame = CFrame.new(bp.X + 12.6 * sz, 0.4, bp.Z),
				Color = C.creme, CanCollide = true, CastShadow = true}, CAN)
		end
		H.part({Name = "Canteiro_terra", Size = Vector3.new(24.4, 0.5, 3.4), CFrame = CFrame.new(bp.X, 0.4, bp.Z),
			Color = C.terra, CanCollide = true}, CAN)
	end
	say("beds: 2 forge flank beds at (+-47,-86.9), empty")

	-- FORGE
	local fcf0 = H.cf0(forn)
	forn.CFrame = fcf0 + Vector3.new(0, 0, -3.2) -- world -Z (CF0 has yaw 180; see header)
	say(("fornalha: Z %.2f -> %.2f (front %.2f, back_hump -113.65)"):format(fcf0.Z, forn.Position.Z, forn.Position.Z + forn.Size.Z / 2))
	placa.CFrame = H.cf0(placa) * CFrame.Angles(0, math.pi, 0)
	say(("placa: turned pi, LookVector.Z now %.2f (letters to the plaza)"):format(placa.CFrame.LookVector.Z))
	for _, seg in ipairs(balSegs) do H.fixBal(seg) end
	say(("fixBal on %d forge KIT_bal_seg (height 3.4, bottom kept)"):format(#balSegs))
	H.boxLantern(DET, "LanternaForjaE", Vector3.new(25.8, 9.98, -92.5))
	H.boxLantern(DET, "LanternaForjaW", Vector3.new(-25.8, 9.98, -92.5))
	H.collider("hx_f5_ignis", Vector3.new(6, 14, 5), CFrame.new(0, 17, -108.3))
	say("2 stair-top lanterns + hx_f5_ignis")

	-- LIONS
	for _, li in ipairs(LIONS) do
		local lion = byRole[li.role]
		H.remember(lion)
		local s0 = lion:GetAttribute("S0")
		lion.Size = s0 * 1.25
		lion.CFrame = CFrame.new(li.x, 8.98, li.z) * CFrame.Angles(0, math.pi, 0)
		if lion:GetAttribute("Color0") == nil then lion:SetAttribute("Color0", lion.Color) end
		local sa = lion:FindFirstChildOfClass("SurfaceAppearance")
		if sa then
			if lion:GetAttribute("Alpha0") == nil then lion:SetAttribute("Alpha0", sa.AlphaMode.Name) end
			sa.AlphaMode = Enum.AlphaMode.Overlay
		end
		lion.Color = C.leao
		H.part({Name = "PlintoLeao_" .. li.role, Size = Vector3.new(6, 4.1, 6.6), CFrame = CFrame.new(li.x, 1.95, li.z),
			Color = C.pedra, Material = Enum.Material.Slate, CanCollide = true, CastShadow = true}, DET)
		H.part({Name = "DiscoLeao_" .. li.role, Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.3, 2.2, 2.2),
			CFrame = CFrame.new(li.x, 2.2, li.z + 3.45) * CFrame.Angles(0, math.pi / 2, 0),
			Color = C.ouro, Material = Enum.Material.Metal, CastShadow = true}, DET)
		H.collider("hx_f5_leao_" .. li.role, Vector3.new(5.2, 10, 5.8), CFrame.new(li.x, 8.98, li.z))
		say(("lion %s (%s) at (%d,8.98,%d), bottom %.2f on plinth top 4.00, stone overlay"):format(
			li.role, lion.Name, li.x, li.z, lion.Position.Y - lion.Size.Y / 2))
	end

	------------------------------------------------------------------ checks (fail -> recording cancelled)
	local fails = {}
	-- wedge raycast check
	local wf = 0
	for _, t in ipairs(WEDGES) do if not H.checkTri(t.w, t.C, t.a, t.la, t.b, t.lb, t.topY) then wf = wf + 1 end end
	if wf > 0 then table.insert(fails, wf .. " monument wedges failed checkTri") end
	say(("checkTri: %d wedges, %d failed"):format(#WEDGES, wf))
	-- monument tops
	local rpM = RaycastParams.new() rpM.FilterType = Enum.RaycastFilterType.Include rpM.FilterDescendantsInstances = {MON}
	for _, t in ipairs({{0, -18, 1.0}, {0, -13, 2.0}, {16.5, 1.5, 2.0}, {0, -9, 8.5}, {0, 0, 13.05}}) do -- (16.5,1.5) is inside a step2 corner wedge
		local r = workspace:Raycast(Vector3.new(t[1], 50, t[2]), Vector3.new(0, -60, 0), rpM)
		if not (r and math.abs(r.Position.Y - t[3]) < 0.05) then
			table.insert(fails, ("monument top @(%d,%d): got %s, want %.2f"):format(t[1], t[2], r and ("%.2f"):format(r.Position.Y) or "nil", t[3]))
		end
	end
	-- Ignis AABB vs forge frame pieces and the furnace
	local function aabb(part)
		local cf, s = part.CFrame, part.Size / 2
		local ax = Vector3.new(math.abs(cf.RightVector.X), math.abs(cf.UpVector.X), math.abs(cf.LookVector.X))
		local hx = ax.X * s.X + ax.Y * s.Y + ax.Z * s.Z
		local ay = Vector3.new(math.abs(cf.RightVector.Y), math.abs(cf.UpVector.Y), math.abs(cf.LookVector.Y))
		local hy = ay.X * s.X + ay.Y * s.Y + ay.Z * s.Z
		local az = Vector3.new(math.abs(cf.RightVector.Z), math.abs(cf.UpVector.Z), math.abs(cf.LookVector.Z))
		local hz = az.X * s.X + az.Y * s.Y + az.Z * s.Z
		return cf.Position - Vector3.new(hx, hy, hz), cf.Position + Vector3.new(hx, hy, hz)
	end
	local nChecked = 0
	for _, parent in ipairs({P, Fo}) do for _, c in ipairs(parent:GetChildren()) do
		if (c.Name == "KIT_coluna" or c.Name == "KIT_arquitrave" or c.Name == "KIT_col_base" or c == forn) and c:IsA("BasePart") then
			nChecked = nChecked + 1
			local mn, mx = aabb(c)
			if mn.X < IG_MAX.X and mx.X > IG_MIN.X and mn.Y < IG_MAX.Y and mx.Y > IG_MIN.Y and mn.Z < IG_MAX.Z and mx.Z > IG_MIN.Z then
				table.insert(fails, "intersects Ignis AABB: " .. c:GetFullName())
			end
		end
	end end
	say(("Ignis AABB check: %d columns/beams/bases + fornalha, 0 required"):format(nChecked))
	if forn.Position.Z + forn.Size.Z / 2 > -113.95 then table.insert(fails, "fornalha front not clear of back_hump") end
	-- Letreiro line to +Z
	local rpI = RaycastParams.new() rpI.FilterType = Enum.RaycastFilterType.Exclude rpI.FilterDescendantsInstances = {IGNIS}
	local rl = workspace:Raycast(Vector3.new(0, 24.33, -70), Vector3.new(0, 0, -45), rpI)
	if rl and rl.Position.Z > -113.5 then table.insert(fails, "LetreiroIgnis line blocked by " .. rl.Instance:GetFullName()) end
	-- sightline: planters and their banners clear of every spawn sight segment
	local S = Vector2.new(0, -38)
	local targets = {Vector2.new(82.82, -33.96), Vector2.new(-84.72, -35.06), Vector2.new(-105.2, -46.88)}
	for _, d in ipairs(discos) do table.insert(targets, Vector2.new(d.Position.X, d.Position.Z)) end
	local function dSeg(p, a, b)
		local ab, ap2 = b - a, p - a
		local t = math.clamp(ap2:Dot(ab) / ab:Dot(ab), 0, 1)
		return (ap2 - ab * t).Magnitude
	end
	for _, pl in ipairs(PLANTERS) do
		local p2 = Vector2.new(pl.pos.X, pl.pos.Z)
		local dmin = math.huge
		for _, tg in ipairs(targets) do dmin = math.min(dmin, dSeg(p2, S, tg)) end
		say(("sightline: planter %s min distance %.1f"):format(pl.role, dmin))
		if dmin < 6.2 then table.insert(fails, pl.role .. " too close to a spawn sight segment: " .. ("%.1f"):format(dmin)) end
	end
	-- spawn point ground unchanged
	local rpL = RaycastParams.new() rpL.FilterType = Enum.RaycastFilterType.Include rpL.FilterDescendantsInstances = {L}
	local rs = workspace:Raycast(Vector3.new(0, 20, -38), Vector3.new(0, -30, 0), rpL)
	if not (rs and math.abs(rs.Position.Y - 0.25) < 0.05) then table.insert(fails, "spawn ground changed: " .. tostring(rs and rs.Position.Y)) end

	if #fails > 0 then error("F5 checks failed:\n- " .. table.concat(fails, "\n- ")) end
	L:SetAttribute("HEX_F5_OK", true)
end)

if not ok then
	if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Cancel) end
	error("F5 CANCELLED (all writes reverted): " .. tostring(err))
end
H.commit(rec)
say(("F5 OK. HEX_Monumento %d, HEX_Canteiros %d, HEX_Detalhes %d, hx_f5_ colliders %d"):format(
	#MON:GetChildren(), #CAN:GetChildren(), #DET:GetChildren(), (function()
		local n = 0 for _, c in ipairs(COL:GetChildren()) do if c.Name:sub(1, 6) == "hx_f5_" and c:GetAttribute("HexCollider") then n = n + 1 end end return n end)()))
return table.concat(rep, "\n")
