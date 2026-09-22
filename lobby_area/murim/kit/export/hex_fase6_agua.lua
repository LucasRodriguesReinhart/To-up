-- hex_fase6_agua.lua : F6 = water. Two sunken lotus ponds (FL and FR bays) with real visible water,
-- red parabolic arched bridges (8 segments, invisible rail walls), FL cascade box + sheet, lily pads,
-- lotus + rock keepers relocated into the ponds (this also settles the F3 reviewer pendencia: the
-- lotus keepers leave the gallery apron/stair), player-scale benches, 4 box lanterns per bridge.
-- Idempotent: HEX_Lagos is cleared EXCEPT children with HEX_ROLE; hx_f6_ colliders cleared; keepers
-- and benches are set from constants and S0. On any error after writes begin, the recording is CANCELLED.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, COL, C = H.L, H.COL, H.C
local CHS = game:GetService("ChangeHistoryService")
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end
local function v3s(v) return ("(%.2f,%.2f,%.2f)"):format(v.X, v.Y, v.Z) end
for _, k in ipairs({"HEX_F0_OK", "HEX_F1_OK", "HEX_F2_OK", "HEX_F3_OK", "HEX_F4_OK", "HEX_F5_OK"}) do
	assert(L:GetAttribute(k) == true, "F6: marker " .. k .. " missing (run the earlier phases first)") end

local LAG = L:FindFirstChild("HEX_Lagos")
assert(LAG, "F6: HEX_Lagos missing (F0 creates it)")

-- ============================== constants ==============================
local PONDS = {
	{key = "FL", face = "FL", s1 = -52, s2 = 12, d1 = 10, d2 = 34, sb = 0,  dA = 38, benchS = -30, benchD = 39},
	{key = "FR", face = "FR", s1 = 4,   s2 = 52, d1 = 10, d2 = 32, sb = 16, dA = 36, benchS = 34,  benchD = 37},
}
local DB, NSEG, RISE = 6, 8, 2.7
local LOTUS = {
	{role = "LOTUS_FL1", f = "FL", s = -30, d = 27,   yaw = 0},
	{role = "LOTUS_FL2", f = "FL", s = -14, d = 15,   yaw = math.rad(40)},
	{role = "LOTUS_FL3", f = "FL", s = 8,   d = 24,   yaw = math.rad(90)},
	{role = "LOTUS_FR1", f = "FR", s = 34,  d = 25,   yaw = 0},
	{role = "LOTUS_FR2", f = "FR", s = 45,  d = 15.5, yaw = math.rad(60)},
}
local ROCKS = {
	{role = "ROCK_FL1", f = "FL", s = -50.8, d = 33.2, yaw = math.rad(25)},
	{role = "ROCK_FL2", f = "FL", s = 10.8,  d = 33.2, yaw = math.rad(140)},
	{role = "ROCK_FR1", f = "FR", s = 50.8,  d = 31.2, yaw = math.rad(70)},
}
local LILIES = {
	FL = {{-48.5,22,3.0},{-46,26.5,2.6},{-43,30,3.2},{-35,13.4,3.4},{-31.5,15,2.6},{-24,29.2,2.4},
		{-20,30.4,3.6},{-15,13.5,2.8},{-11.5,15.2,2.5},{8.5,13.6,3.2},{8.8,30,2.7},{-27,31,3.0}},
	FR = {{7.5,14,2.8},{7.8,27.5,3.2},{26,13.4,3.4},{29.5,15,2.6},{27.5,28.6,3.0},{31,29,2.4},
		{38,13.2,2.5},{41,28.6,3.4},{48.8,14,3.0},{48.5,20,2.6},{47,27.5,3.2},{35,20.5,2.2}},
}
local CASC = {s1 = -48, s2 = -38, d1 = 11.6, d2 = 18} -- FL only
local WATER_TEX = "rbxasset://textures/particles/water_main.dds"
local GRAY = Color3.fromRGB(128, 128, 128)

-- ============================== stage 1: read-only ==============================
local bad = {}
local roleOf, roles = {}, {}
for _, c in ipairs(LAG:GetChildren()) do
	local r = c:GetAttribute("HEX_ROLE")
	if r then
		if roleOf[r] then table.insert(bad, "duplicated HEX_ROLE " .. r) end
		roleOf[r] = c table.insert(roles, r)
	elseif not c:GetAttribute("HexGen") then
		-- a boxLantern Model from a previous F6 run: the Model has no attribute, its parts all do
		local lantern = c:IsA("Model") and c.Name:sub(1, 9) == "Lanterna_"
		if lantern then
			for _, q in ipairs(c:GetChildren()) do
				if q:IsA("BasePart") and not q:GetAttribute("HexGen") then lantern = false break end end
		end
		if not lantern then
			table.insert(bad, "HEX_Lagos holds a foreign instance: " .. c:GetFullName())
		end
	end
end
for _, e in ipairs(LOTUS) do local i = roleOf[e.role]
	if not (i and i:IsA("MeshPart")) then table.insert(bad, "keeper missing: " .. e.role) end end
for _, e in ipairs(ROCKS) do local i = roleOf[e.role]
	if not (i and i:IsA("MeshPart")) then table.insert(bad, "keeper missing: " .. e.role) end end
if #roles ~= 8 then table.insert(bad, "HEX_Lagos keeper count " .. #roles .. " ~= 8") end

local BENCH = {}
for _, c in ipairs(L:GetDescendants()) do
	if c.Name == "VIL_banco" then
		local r = c:GetAttribute("HEX_ROLE")
		if r == "BENCH_FL" or r == "BENCH_FR" then
			if BENCH[r] then table.insert(bad, "duplicated bench role " .. r) end
			BENCH[r] = c
		end
	end
end
for _, r in ipairs({"BENCH_FL", "BENCH_FR"}) do
	if not (BENCH[r] and BENCH[r]:IsA("MeshPart")) then table.insert(bad, "bench keeper missing: " .. r) end end

-- pond holes and paving levels
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances = {}
local function rayY(p3) local h = workspace:Raycast(Vector3.new(p3.X, 200, p3.Z), Vector3.new(0, -260, 0), rp)
	return h and h.Position.Y or nil, h and h.Instance or nil end
for _, P in ipairs(PONDS) do
	local cs, cd = (P.s1 + P.s2) / 2, (P.d1 + P.d2) / 2
	local y = rayY(H.fp(P.face, cs, cd, 0))
	if y ~= nil and math.abs(y - (-1.6)) > 0.1 then
		table.insert(bad, ("pond %s centre: expected a hole or the F6 bed, got Y=%.2f"):format(P.key, y)) end
	local ya = rayY(H.fp(P.face, P.sb, P.dA, 0))
	if not ya or math.abs(ya) > 0.15 then
		table.insert(bad, ("pond %s bridge plaza end: paving Y=%s"):format(P.key, tostring(ya))) end
	local yb = rayY(H.fp(P.face, P.sb, DB, 0)) -- deck landing on the garden strip
	if not yb or math.abs(yb) > 0.15 then
		table.insert(bad, ("pond %s bridge wall end (d=%d): paving Y=%s"):format(P.key, DB, tostring(yb))) end
	for _, sl in ipairs({P.sb + 5.6, P.sb - 5.6}) do -- lantern spots: paving 0 or the 0.25 border band; old F6 lantern ok
		local yl, il = rayY(H.fp(P.face, sl, 4.5, 0))
		local prev = il and il:IsDescendantOf(LAG)
		if not prev and (not yl or yl < -0.15 or yl > 0.30) then
			table.insert(bad, ("pond %s wall lantern spot s=%.1f: ground Y=%s"):format(P.key, sl, tostring(yl))) end
	end
	local yc, ic = rayY(H.fp(P.face, P.benchS, P.benchD, 0))
	local prevBench = ic and ic:GetAttribute("HexCollider") and ic.Name:sub(1, 11) == "hx_f6_banco"
	if not prevBench and (not yc or math.abs(yc) > 0.15) then
		table.insert(bad, ("pond %s bench spot: paving Y=%s"):format(P.key, tostring(yc))) end
end
assert(#bad == 0, "F6 stage 1 FAILED:\n" .. table.concat(bad, "\n"))
say("stage 1 OK: 8 keepers + 2 benches found, pond holes and paving levels as expected")

-- ============================== helpers for checks ==============================
local function nodesOf(P)
	local ds, ys = {}, {}
	for k = 0, NSEG do
		ds[k] = P.dA - (P.dA - DB) * k / NSEG
		local u = 2 * k / NSEG - 1
		ys[k] = RISE * (1 - u * u)
	end
	return ds, ys
end
local function chordY(P, d) -- deck centre-line height at inward distance d (clamped to span)
	local ds, ys = nodesOf(P)
	if d >= ds[0] then return ys[0] end
	if d <= ds[NSEG] then return ys[NSEG] end
	for k = 1, NSEG do
		if d <= ds[k - 1] and d >= ds[k] then
			local t = (ds[k - 1] - d) / (ds[k - 1] - ds[k])
			return ys[k - 1] + t * (ys[k] - ys[k - 1])
		end
	end
	return nil
end
local function rectDist(p3, cf, hx, hz) -- planar distance point -> oriented rect
	local q = cf:PointToObjectSpace(Vector3.new(p3.X, cf.Position.Y, p3.Z))
	local dx = math.max(math.abs(q.X) - hx, 0) local dz = math.max(math.abs(q.Z) - hz, 0)
	return math.sqrt(dx * dx + dz * dz)
end

-- ============================== stage 2: writes (one recording) ==============================
local recId = H.begin("HEX_F6_agua")
local okRun, errRun = pcall(function()
	-- idempotency: clear generated children (keep HEX_ROLE keepers), clear own colliders
	local cleared = 0
	for _, c in ipairs(LAG:GetChildren()) do
		if c:GetAttribute("HEX_ROLE") == nil then c:Destroy() cleared = cleared + 1 end end
	H.clearColliders("hx_f6_")
	say("cleared " .. cleared .. " generated children of HEX_Lagos + hx_f6_ colliders")

	H.selfTest()
	local nParts, nColl = 0, 0
	local function mk(o, parent) nParts = nParts + 1 return H.part(o, parent) end

	local lotusBox = {} -- per face list of {s1,s2,d1,d2} AABBs of planned lotus poses (for lily shifts)
	for _, e in ipairs(LOTUS) do
		local i = roleOf[e.role] local s0 = H.s0(i)
		local ca, sa = math.abs(math.cos(e.yaw)), math.abs(math.sin(e.yaw))
		local hs = (ca * s0.X + sa * s0.Z) / 2 local hd = (sa * s0.X + ca * s0.Z) / 2
		lotusBox[e.f] = lotusBox[e.f] or {}
		table.insert(lotusBox[e.f], {e.s - hs, e.s + hs, e.d - hd, e.d + hd})
	end

	for _, P in ipairs(PONDS) do
		local f, key = P.face, P.key
		-- 1. bed
		H.faceRect(LAG, {Name = "Leito_" .. key, Color = C.leito, CanCollide = true},
			f, P.s1, P.s2, P.d1, P.d2, -2.6, -1.6) nParts = nParts + 1
		-- 2. coping (Slate, top 0.4, reaches 0.1 into the paving)
		local function coping(n, a, b, c2, d)
			H.faceRect(LAG, {Name = "Borda_" .. key .. "_" .. n, Material = Enum.Material.Slate,
				Color = C.pedra, CanCollide = true}, f, a, b, c2, d, -2.6, 0.4) nParts = nParts + 1 end
		coping("praca", P.s1 - 0.1, P.s2 + 0.1, P.d2 - 1.6, P.d2 + 0.1)
		coping("muro",  P.s1 - 0.1, P.s2 + 0.1, P.d1 - 0.1, P.d1 + 1.6)
		coping("ext1",  P.s1 - 0.1, P.s1 + 1.6, P.d1 + 1.6, P.d2 - 1.6)
		coping("ext2",  P.s2 - 1.6, P.s2 + 0.1, P.d1 + 1.6, P.d2 - 1.6)
		-- 3. water: ONE part per pond
		local w = H.faceRect(LAG, {Name = "Agua_" .. key, Material = Enum.Material.Plastic, Color = C.agua,
			Transparency = 0.23, Reflectance = 0.10, CanCollide = false},
			f, P.s1 + 1.6, P.s2 - 1.6, P.d1 + 1.6, P.d2 - 1.6, -1.2, -0.9) nParts = nParts + 1
		local tx = Instance.new("Texture") tx.Texture = WATER_TEX tx.Face = Enum.NormalId.Top
		tx.StudsPerTileU = 18 tx.StudsPerTileV = 22 tx.Transparency = 0.9 tx.Parent = w
		P.water = w
		-- 4. bridge
		local BR = Instance.new("Model") BR.Name = "Ponte_" .. key BR:SetAttribute("HexGen", true) BR.Parent = LAG
		local ds, ys = nodesOf(P)
		local maxSlope = 0
		for k = 1, NSEG do
			local A = H.fp(f, P.sb, ds[k - 1], ys[k - 1])
			local B = H.fp(f, P.sb, ds[k], ys[k])
			local mid, len = (A + B) / 2, (B - A).Magnitude
			local base = CFrame.lookAt(mid, B)
			maxSlope = math.max(maxSlope, math.deg(math.atan(math.abs(ys[k] - ys[k - 1]) / math.abs(ds[k] - ds[k - 1]))))
			mk({Name = "Prancha_" .. k, Size = Vector3.new(8, 0.6, len + 0.3), Material = Enum.Material.WoodPlanks,
				Color = C.madeira, CanCollide = true, CFrame = base * CFrame.new(0, -0.3, 0)}, BR)
			for _, sd in ipairs({{1, "E"}, {-1, "W"}}) do
				local sg = sd[1]
				mk({Name = "Longarina_" .. k .. "_" .. sd[2], Size = Vector3.new(0.5, 1.0, len), Color = C.grade,
					CFrame = base * CFrame.new(sg * 3.75, -1.1, 0)}, BR)
				mk({Name = "CorrimaoAlto_" .. k .. "_" .. sd[2], Size = Vector3.new(0.4, 0.4, len), Color = C.grade,
					CanCollide = true, CFrame = base * CFrame.new(sg * 3.6, 3.0, 0)}, BR)
				mk({Name = "CorrimaoMeio_" .. k .. "_" .. sd[2], Size = Vector3.new(0.3, 0.3, len), Color = C.grade,
					CFrame = base * CFrame.new(sg * 3.6, 1.6, 0)}, BR)
				H.collider("hx_f6_ponte_" .. key .. "_" .. k .. "_" .. sd[2], Vector3.new(0.4, 3.2, len),
					base * CFrame.new(sg * 3.8, 1.6, 0)) nColl = nColl + 1
			end
		end
		for k = 0, NSEG do
			for _, sd in ipairs({{1, "E"}, {-1, "W"}}) do
				mk({Name = "Poste_" .. k .. "_" .. sd[2], Size = Vector3.new(0.7, 3.2, 0.7), Color = C.grade,
					CanCollide = true, CFrame = H.faceCF(f, P.sb + sd[1] * 3.6, ds[k], ys[k] + 1.6)}, BR)
				if k == 0 or k == NSEG then
					mk({Name = "TopoOuro_" .. k .. "_" .. sd[2], Size = Vector3.new(0.9, 0.4, 0.9), Color = C.ouro,
						Material = Enum.Material.Metal, CFrame = H.faceCF(f, P.sb + sd[1] * 3.6, ds[k], ys[k] + 3.4)}, BR)
				end
			end
		end
		P.maxSlope = maxSlope
		-- 5. bridge-end lanterns (4)
		local li = 0
		for _, spot in ipairs({{P.sb + 5.6, P.dA + 1.5}, {P.sb - 5.6, P.dA + 1.5}, {P.sb + 5.6, 4.5}, {P.sb - 5.6, 4.5}}) do
			li = li + 1
			local lm = H.boxLantern(LAG, "Lanterna_" .. key .. "_" .. li, H.fp(f, spot[1], spot[2], 0))
			lm:SetAttribute("HexGen", true)
			nParts = nParts + 10
		end
	end

	-- 6. cascade (FL only)
	H.faceRect(LAG, {Name = "Cascata_caixa", Material = Enum.Material.Slate, Color = GRAY, CanCollide = true},
		"FL", CASC.s1, CASC.s2, CASC.d1, CASC.d2, -1.6, 3.6) nParts = nParts + 1
	H.faceRect(LAG, {Name = "Cascata_musgo", Material = Enum.Material.Grass, Color = C.musgo, CanCollide = true},
		"FL", CASC.s1 + 0.2, CASC.s2 - 0.2, CASC.d1 + 0.2, CASC.d2 - 0.2, 3.6, 4.0) nParts = nParts + 1
	local sheet = H.part({Name = "Cascata_lamina", Size = Vector3.new(5, 4.5, 0.3), CFrame = H.faceCF("FL", -43, 18.15, 1.35),
		Color = C.cascata, Transparency = 0.3, CanCollide = false}, LAG) nParts = nParts + 1
	local stx = Instance.new("Texture") stx.Texture = WATER_TEX stx.Face = Enum.NormalId.Back
	stx.StudsPerTileU = 5 stx.StudsPerTileV = 5 stx.Transparency = 0.6 stx.Parent = sheet

	-- 7. lily pads (shift up to 2 along s when they hit a lotus AABB, the cascade or the bridge zone)
	local lilyShifts = {}
	for _, P in ipairs(PONDS) do
		local f, key = P.face, P.key
		for i, e in ipairs(LILIES[key]) do
			local s0, d, D = e[1], e[2], e[3] local r = D / 2
			local function conflict(s)
				if math.abs(s - P.sb) < 7 + r then return true end -- bridge zone sb +/- 7
				if key == "FL" and s + r > CASC.s1 and s - r < CASC.s2 and d + r > CASC.d1 and d - r < CASC.d2 then return true end
				for _, b in ipairs(lotusBox[f] or {}) do
					if s + r > b[1] and s - r < b[2] and d + r > b[3] and d - r < b[4] then return true end end
				return false
			end
			local s = s0
			if conflict(s) then
				for _, off in ipairs({0.5, -0.5, 1, -1, 1.5, -1.5, 2, -2}) do
					if not conflict(s0 + off) then s = s0 + off break end end
				if s ~= s0 then table.insert(lilyShifts, ("%s#%d s %.1f->%.1f"):format(key, i, s0, s)) end
			end
			mk({Name = "Lirio_" .. key .. "_" .. i, Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.06, D, D),
				CFrame = CFrame.new(H.fp(f, s, d, -0.83)) * CFrame.Angles(0, 0, math.pi / 2),
				Color = C.lirio, CanCollide = false}, LAG)
		end
	end
	say("lily shifts: " .. (#lilyShifts > 0 and table.concat(lilyShifts, ", ") or "none"))

	-- 8. lotus keepers into the ponds (settles the F3 pendencia: off the gallery apron/stair)
	for _, e in ipairs(LOTUS) do
		local i = roleOf[e.role] local s0 = H.s0(i)
		i.CFrame = CFrame.new(H.fp(e.f, e.s, e.d, -0.9 + 0.05 + s0.Y / 2)) * CFrame.Angles(0, e.yaw, 0)
		i.CanCollide = false i.CanQuery = false i.CanTouch = false
		say(("%s -> %s"):format(e.role, v3s(i.Position)))
	end
	-- 9. rock keepers on the plaza-side coping corners
	for _, e in ipairs(ROCKS) do
		local i = roleOf[e.role] local s0 = H.s0(i)
		i.CFrame = CFrame.new(H.fp(e.f, e.s, e.d, -0.8 + s0.Y / 2)) * CFrame.Angles(0, e.yaw, 0)
		i.CanCollide = false i.CanQuery = false i.CanTouch = false
		say(("%s -> %s"):format(e.role, v3s(i.Position)))
	end
	-- 10. benches at player scale + colliders
	for _, P in ipairs(PONDS) do
		local b = BENCH["BENCH_" .. P.key]
		H.remember(b)
		local cf = H.faceCF(P.face, P.benchS, P.benchD, 0.95)
		b.Size = Vector3.new(8.3, 2.1, 2.4) b.CFrame = cf
		b.CanCollide = false b.CanQuery = false b.CanTouch = false
		H.collider("hx_f6_banco_" .. P.key, Vector3.new(8.3, 2.2, 2.4), cf) nColl = nColl + 1
		say(("BENCH_%s -> %s size (8.3,2.1,2.4)"):format(P.key, v3s(b.Position)))
	end

	-- ============================== checks (cancel the recording on failure) ==============================
	local fail = {}
	-- A. chord slopes
	if PONDS[1].maxSlope > 16.55 then table.insert(fail, ("FL slope %.2f > 16.5"):format(PONDS[1].maxSlope)) end
	if PONDS[2].maxSlope > 17.55 then table.insert(fail, ("FR slope %.2f > 17.5"):format(PONDS[2].maxSlope)) end
	say(("chord slopes: FL %.2f deg, FR %.2f deg"):format(PONDS[1].maxSlope, PONDS[2].maxSlope))
	-- B. deck bottom over the exposed coping >= 0.58
	for _, P in ipairs(PONDS) do
		local minBot = math.huge
		for _, rng in ipairs({{P.d2 - 1.6, P.d2}, {P.d1, P.d1 + 1.6}}) do
			local d = rng[1]
			while d <= rng[2] + 1e-6 do
				minBot = math.min(minBot, chordY(P, d) - 0.6) d = d + 0.05 end
		end
		say(("%s deck bottom over coping: min %.3f (coping top 0.4)"):format(P.key, minBot))
		if minBot < 0.575 then table.insert(fail, ("%s deck bottom %.3f < 0.58 over coping"):format(P.key, minBot)) end
	end
	-- C. water directly under planks 2..7
	for _, P in ipairs(PONDS) do
		local ds = nodesOf(P)
		for k = 2, 7 do
			local mid = (ds[k - 1] + ds[k]) / 2
			if mid < P.d1 + 1.6 - 0.05 or mid > P.d2 - 1.6 + 0.05 then
				table.insert(fail, ("%s plank %d mid d=%.2f outside water %.1f..%.1f"):format(P.key, k, mid, P.d1 + 1.6, P.d2 - 1.6)) end
		end
	end
	-- D. nothing opaque and foreign intrudes into the water column (plan x Y -0.9..0.4)
	for _, P in ipairs(PONDS) do
		local probe = Instance.new("Part") probe.Anchored = true
		probe.Size = Vector3.new(P.s2 - P.s1 - 3.2, 1.3, P.d2 - P.d1 - 3.2)
		probe.CFrame = H.faceCF(P.face, (P.s1 + P.s2) / 2, (P.d1 + P.d2) / 2, -0.25)
		probe.Transparency = 1 probe.CanCollide = false probe.CanTouch = false probe.CanQuery = false
		probe.Parent = workspace
		local op = OverlapParams.new() op.FilterType = Enum.RaycastFilterType.Exclude op.FilterDescendantsInstances = {probe}
		op.MaxParts = 500
		local hits = workspace:GetPartsInPart(probe, op)
		local intr = 0
		for _, q in ipairs(hits) do
			if not (q:IsDescendantOf(LAG) or q:IsDescendantOf(COL)) and q.Transparency < 0.5 then
				intr = intr + 1 table.insert(fail, P.key .. " water intrusion: " .. q:GetFullName())
			end
		end
		probe:Destroy()
		say(("%s water column: %d contacts, %d foreign intrusions"):format(P.key, #hits, intr))
	end
	-- E. walkability: full hexagon grid (step 4, apothem<=144) zero misses + pond fine grid heights
	local ns6 = {}
	for _, th in ipairs({30, 90, 150, 210, 270, 330}) do
		table.insert(ns6, Vector3.new(math.cos(math.rad(th)), 0, math.sin(math.rad(th)))) end
	local function insideHex(x, z, ap)
		for _, n in ipairs(ns6) do if x * n.X + z * n.Z > ap then return false end end return true end
	local miss = 0
	for x = -146, 146, 4 do for z = -146, 146, 4 do
		if insideHex(x, z, 144) and rayY(Vector3.new(x, 0, z)) == nil then miss = miss + 1 end end end
	say("full walk grid misses: " .. miss)
	if miss > 0 then table.insert(fail, miss .. " walk grid misses remain in the hexagon") end
	for _, P in ipairs(PONDS) do
		local nBed, nCop, badH = 0, 0, 0
		for s = P.s1 + 1, P.s2 - 1, 2 do
			for d = P.d1 + 1, P.d2 - 1, 2 do
				local overBridge = math.abs(s - P.sb) <= 4.5
				local inCasc = (P.key == "FL") and s > CASC.s1 - 0.3 and s < CASC.s2 + 0.3 and d > CASC.d1 - 0.3 and d < CASC.d2 + 0.3
				local isCop = (s < P.s1 + 1.6 - 0.3 or s > P.s2 - 1.6 + 0.3 or d < P.d1 + 1.6 - 0.3 or d > P.d2 - 1.6 + 0.3)
				local isBed = (s > P.s1 + 1.6 + 0.3 and s < P.s2 - 1.6 - 0.3 and d > P.d1 + 1.6 + 0.3 and d < P.d2 - 1.6 - 0.3)
				if not overBridge and not inCasc then
					local y = rayY(H.fp(P.face, s, d, 0))
					if y == nil then badH = badH + 1
					elseif isBed and math.abs(y - (-1.6)) <= 0.05 then nBed = nBed + 1
					elseif isCop and math.abs(y - 0.4) <= 0.05 then nCop = nCop + 1
					elseif isBed or isCop then badH = badH + 1 end
				end
			end
		end
		say(("%s fine grid: bed ok %d, coping ok %d, bad %d"):format(P.key, nBed, nCop, badH))
		if badH > 0 then table.insert(fail, P.key .. " fine grid bad heights: " .. badH) end
		-- deck heights along the centreline
		local badD = 0
		for d = DB + 0.5, P.dA - 0.5, 0.5 do
			local y = rayY(H.fp(P.face, P.sb, d, 0))
			local want = chordY(P, d)
			if not y or math.abs(y - want) > 0.25 then badD = badD + 1 end
		end
		say(("%s deck centreline samples off: %d"):format(P.key, badD))
		if badD > 0 then table.insert(fail, P.key .. " deck centreline mismatches: " .. badD) end
	end
	-- F. distances (pond boundary sampling vs processional band and gallery zone)
	local bandCF, bandHX, bandHZ = CFrame.new(0, 0, 92), 14, 58
	local galCF, galHX, galHZ = H.TG * CFrame.new(125, 0, 0), 21.5, 45.5
	for _, P in ipairs(PONDS) do
		local minBand, minGal = math.huge, math.huge
		local function eat(p3)
			minBand = math.min(minBand, rectDist(p3, bandCF, bandHX, bandHZ))
			minGal = math.min(minGal, rectDist(p3, galCF, galHX, galHZ))
		end
		for s = P.s1, P.s2, 1 do eat(H.fp(P.face, s, P.d1, 0)) eat(H.fp(P.face, s, P.d2, 0)) end
		for d = P.d1, P.d2, 1 do eat(H.fp(P.face, P.s1, d, 0)) eat(H.fp(P.face, P.s2, d, 0)) end
		P.minBand, P.minGal = minBand, minGal
		say(("%s min distance: band %.2f, gallery %.2f"):format(P.key, minBand, minGal))
	end
	if PONDS[2].minGal < 60 then table.insert(fail, ("FR-gallery %.2f < 60"):format(PONDS[2].minGal)) end
	if PONDS[2].minBand < 60 then table.insert(fail, ("FR-band %.2f < 60"):format(PONDS[2].minBand)) end
	if PONDS[1].minBand < 59 then table.insert(fail, ("FL-band %.2f < 59"):format(PONDS[1].minBand)) end

	assert(#fail == 0, "F6 checks FAILED:\n" .. table.concat(fail, "\n"))
	say(("built: %d parts in HEX_Lagos (+2 bridge models, 8 lantern models), %d hx_f6_ colliders"):format(nParts, nColl))
	L:SetAttribute("HEX_F6_OK", true)
	say("marker HEX_F6_OK set")
end)
if not okRun then
	if recId then CHS:FinishRecording(recId, Enum.FinishRecordingOperation.Cancel) end
	return "F6 CANCELLED (all writes reverted):\n" .. tostring(errRun) .. "\n---- partial report ----\n" .. table.concat(rep, "\n")
end
H.commit(recId)
return "F6 OK\n" .. table.concat(rep, "\n")
