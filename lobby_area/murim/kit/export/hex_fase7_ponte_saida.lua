-- hex_fase7_ponte_saida.lua : F7 = first exit bridge restyled in lobby style.
-- The 92-wide white/yellow/blue slab (image 58) becomes a 32-wide stone bridge that continues the
-- gate axis: red carpet band, creme curbs, vinho fascia, red lacquer railing with gold caps,
-- 6 lamp posts with hanging KIT_lanterna_vermelha + PointLights, stone piers and arch ribs
-- underneath, apron railing + hx_f7_ colliders sealing the sides. The walk profile to Area 1 is
-- UNCHANGED: Estrada/RampaArea1/RampaPatamar keep CFrame/Size/CanCollide and are only made
-- invisible. Decor moves to ServerStorage.LOBBY_REMOVIDOS_HEX/F7_R11 (nothing destroyed).
-- Cliff tops near the exit are lowered by rule (computed from CF0/S0) so no rock pokes through.
-- Idempotent: H.clear(HEX_PonteSaida) + H.clearColliders("hx_f7_"); cliff targets come from CF0.
-- Stage 1 is read-only and aborts before any write. Stage 2 runs in one ChangeHistory recording
-- that is CANCELLED on any failed check.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, COL, C = H.L, H.COL, H.C
local CHS = game:GetService("ChangeHistoryService")
local V3 = Vector3.new
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end

for _, k in ipairs({"HEX_F0_OK", "HEX_F1_OK", "HEX_F2_OK", "HEX_F3_OK", "HEX_F4_OK", "HEX_F5_OK", "HEX_F6_OK"}) do
	assert(L:GetAttribute(k) == true, "F7: marker " .. k .. " missing (run the earlier phases first)") end

local PS = L:FindFirstChild("HEX_PonteSaida")
assert(PS, "F7: HEX_PonteSaida missing (F0 creates it)")
local CORR = workspace:FindFirstChild("Corredores")
local A1 = CORR and CORR:FindFirstChild("Lobby_Area1")
assert(A1, "F7: workspace.Corredores.Lobby_Area1 missing")

-- ============================== constants ==============================
local DECKCOL = Color3.fromRGB(189, 174, 154)
local KEEP = { -- name -> expected position / size (spec, section "Corredores.Lobby_Area1")
	Estrada      = {pos = V3(0, -1.5, 228), size = V3(92, 3, 100)},
	RampaArea1   = {pos = V3(0, 1.8, 223),  size = V3(92, 3, 28.68)},
	RampaPatamar = {pos = V3(0, 4.6, 239),  size = V3(92, 3, 10)},
}
local REMOVE = { -- exact-name decor -> expected count (31 with the Poste* prefix)
	FaixaCentral = 1, FaixaAzul = 1, Guia = 2, GuiaOuro = 2,
	RampaFaixa = 1, RampaGuia = 2, RampaGuiaOuro = 2,
}
local POSTE_N = 20
-- cliff pieces the rule is expected to move (spec lists 7; the 8th at (-74.02,..) is caught by the
-- rule as written: AABB centre |X|<75 and 180<Z<230, top -0.3 > -0.3). Anything else aborts.
local EXPECTED_MOVES = {
	V3(35.87, -14.63, 198.27), V3(14.43, -21.98, 196.66), V3(4.30, -14.26, 203.63),
	V3(-7.04, -20.22, 206.26), V3(-19.35, -19.86, 195.37), V3(-32.16, -17.76, 197.54),
	V3(-57.83, -12.67, 200.38), V3(-74.02, -15.56, 201.59),
}

local function aabb(cf, sz)
	local mn, mx
	for _, sx in ipairs({-1, 1}) do for _, sy in ipairs({-1, 1}) do for _, s2 in ipairs({-1, 1}) do
		local p = cf * V3(sx * sz.X / 2, sy * sz.Y / 2, s2 * sz.Z / 2)
		if not mn then mn, mx = p, p else
			mn = V3(math.min(mn.X, p.X), math.min(mn.Y, p.Y), math.min(mn.Z, p.Z))
			mx = V3(math.max(mx.X, p.X), math.max(mx.Y, p.Y), math.max(mx.Z, p.Z)) end
	end end end
	return mn, mx
end
local function near(a, b, tol) return (a - b).Magnitude <= (tol or 0.05) end

-- ============================== stage 1: read-only ==============================
-- 1a. HEX_PonteSaida holds only generated items
for _, c in ipairs(PS:GetChildren()) do
	assert(c:GetAttribute("HexGen"), "F7: foreign child in HEX_PonteSaida: " .. c.Name) end

-- 1b. keepers: exactly one each, at the spec CFrame/Size, CanCollide, anchored, never moved
local KP = {}
for name, exp in pairs(KEEP) do
	local found = {}
	for _, c in ipairs(A1:GetChildren()) do if c.Name == name then table.insert(found, c) end end
	assert(#found == 1, "F7: expected exactly 1 " .. name .. ", found " .. #found)
	local p = found[1]
	assert(near(p.Position, exp.pos), "F7: " .. name .. " moved: " .. tostring(p.Position))
	assert(near(p.Size, exp.size), "F7: " .. name .. " resized: " .. tostring(p.Size))
	assert(p.CanCollide == true and p.Anchored == true, "F7: " .. name .. " not collidable+anchored")
	local cf0 = p:GetAttribute("CF0")
	if cf0 then
		local d = 0
		local a = {cf0:GetComponents()} local b = {p.CFrame:GetComponents()}
		for i = 1, 12 do d = math.max(d, math.abs(a[i] - b[i])) end
		assert(d < 0.01, "F7: " .. name .. " no longer equals its CF0")
	end
	KP[name] = p
end

-- 1c. removals: live + already-removed == expected, per name (Poste* by prefix)
local REMF = H.REM:FindFirstChild("F7_R11")
local function countRem(match)
	local n = 0
	if REMF then for _, c in ipairs(REMF:GetChildren()) do
		local op = c:GetAttribute("OrigemPath") or ""
		if match(c.Name) and op:find("Lobby_Area1", 1, true) then n = n + 1 end
	end end
	return n
end
local liveDecor = {}
local function countLive(match)
	local n = 0
	for _, c in ipairs(A1:GetChildren()) do
		if c:IsA("BasePart") and not KEEP[c.Name] and match(c.Name) then n = n + 1 end
	end
	return n
end
local totalExp = POSTE_N
for name, exp in pairs(REMOVE) do
	totalExp = totalExp + exp
	local live = countLive(function(n) return n == name end)
	local rem = countRem(function(n) return n == name end)
	assert(live + rem == exp, ("F7: %s live %d + removed %d ~= %d"):format(name, live, rem, exp))
end
do
	local live = countLive(function(n) return n:sub(1, 5) == "Poste" end)
	local rem = countRem(function(n) return n:sub(1, 5) == "Poste" end)
	assert(live + rem == POSTE_N, ("F7: Poste* live %d + removed %d ~= %d"):format(live, rem, POSTE_N))
end
assert(totalExp == 31, "F7: internal removal count " .. totalExp)
for _, c in ipairs(A1:GetChildren()) do
	assert(c:IsA("BasePart"), "F7: non-BasePart in Lobby_Area1: " .. c.Name)
	local known = KEEP[c.Name] or REMOVE[c.Name] or c.Name:sub(1, 5) == "Poste"
	assert(known, "F7: unexpected part in Lobby_Area1: " .. c.Name)
	if not KEEP[c.Name] then table.insert(liveDecor, c) end
end

-- 1d. library lantern
local LK = H.LIB:FindFirstChild("KIT") and H.LIB.KIT:FindFirstChild("KIT_lanterna_vermelha")
assert(LK and LK:IsA("BasePart"), "F7: BIBLIOTECA_MURIM.KIT.KIT_lanterna_vermelha missing")
local LS = LK.Size * 0.7
assert(LS.Y > 3 and LS.Y < 6, "F7: lantern scaled height odd: " .. LS.Y)

-- 1e. cliff scan by rule (from CF0/S0)
local moves, kept = {}, 0
for _, d in ipairs(L.Patio:GetChildren()) do
	if d:IsA("BasePart") and d.Name:sub(1, 12) == "LOB_penhasco" then
		local cf = d:GetAttribute("CF0") or d.CFrame
		local sz = d:GetAttribute("S0") or d.Size
		local mn, mx = aabb(cf, sz)
		local cc = (mn + mx) / 2
		if math.abs(cc.X) < 75 and cc.Z > 180 and cc.Z < 230 then
			local target
			if mx.X > -18 and mn.X < 18 then target = -3.3
			elseif mx.Y > -0.3 then target = -0.3 end
			local dy = target and math.min(0, target - mx.Y) or 0
			if dy < -0.005 then
				table.insert(moves, {part = d, c = cc, top = mx.Y, dy = dy, cf0 = cf})
			else kept = kept + 1 end
		end
	end
end
for _, m in ipairs(moves) do
	local ok = false
	for _, e in ipairs(EXPECTED_MOVES) do if near(m.c, e, 0.3) then ok = true break end end
	assert(ok, ("F7: unexpected cliff move at (%.2f,%.2f,%.2f)"):format(m.c.X, m.c.Y, m.c.Z))
end
assert(#moves == #EXPECTED_MOVES, ("F7: cliff moves %d ~= expected %d"):format(#moves, #EXPECTED_MOVES))

-- 1f. pre-profiles along X=0 (walk surface must be identical after the phase)
local function profile(filterType, list, z1, z2)
	local rp = RaycastParams.new()
	rp.FilterType = filterType
	rp.FilterDescendantsInstances = list
	rp.RespectCanCollide = true
	local t = {}
	for z = z1, z2 do
		local r = workspace:Raycast(V3(0, 50, z), V3(0, -100, 0), rp)
		t[#t + 1] = r and math.floor(r.Position.Y * 100 + 0.5) / 100 or -999
	end
	return t
end
local exList = {PS}
for _, c in ipairs(liveDecor) do table.insert(exList, c) end
local preWalk = profile(Enum.RaycastFilterType.Include, {KP.Estrada, KP.RampaArea1, KP.RampaPatamar}, 179, 244)
local preEnv = profile(Enum.RaycastFilterType.Exclude, exList, 150, 244)
say(("stage1 OK: 3 keepers, %d live decor, %d cliff moves planned (%d in-region kept), lantern S0*0.7=%s")
	:format(#liveDecor, #moves, kept, tostring(LS)))

-- ============================== stage 2: one recording ==============================
local recId = H.begin("HEX F7 ponte saida")
local okRun, errRun = pcall(function()
	local fail = {}
	H.clear(PS)
	H.clearColliders("hx_f7_")

	-- keepers invisible, untouched otherwise
	for name, p in pairs(KP) do
		H.remember(p)
		p.Transparency = 1
		p.CastShadow = false
	end
	say("keepers made invisible (Transparency 1, CastShadow false); collision untouched")

	-- removals
	local nMoved = 0
	for _, c in ipairs(liveDecor) do if H.remove(c, "F7_R11") then nMoved = nMoved + 1 end end
	say(("removals: %d moved now, %d total in F7_R11"):format(nMoved, #H.REM.F7_R11:GetChildren()))

	-- ---------- visual bridge ----------
	local function pp(o) return H.part(o, PS) end
	local rCF, pCF = KP.RampaArea1.CFrame, KP.RampaPatamar.CFrame

	-- deck + clones
	pp{Name = "Tabuleiro", Size = V3(32, 3, 30.7), CFrame = CFrame.new(0, -1.5, 193.35),
		Color = DECKCOL, Material = Enum.Material.Pavement}
	local function deckClone(src, name)
		local c = src:Clone()
		for _, ch in ipairs(c:GetChildren()) do ch:Destroy() end
		for k in pairs(c:GetAttributes()) do c:SetAttribute(k, nil) end
		c.Name = name
		c.Size = V3(32, src.Size.Y, src.Size.Z)
		c.CFrame = src.CFrame
		c.Transparency = 0 c.CastShadow = false
		c.CanCollide = false c.CanQuery = false c.CanTouch = false
		c.Color = DECKCOL c.Material = Enum.Material.Pavement
		c.TopSurface = Enum.SurfaceType.Smooth c.BottomSurface = Enum.SurfaceType.Smooth
		c:SetAttribute("HexGen", true)
		c.Parent = PS
		return c
	end
	deckClone(KP.RampaArea1, "PonteRampa")
	deckClone(KP.RampaPatamar, "PontePatamar")

	-- red carpet band on the gate axis (top 0.15 above each deck surface)
	for _, cp in ipairs({
		{V3(8, 0.3, 30.7), CFrame.new(0, 0, 193.35)},
		{V3(8, 0.3, 28.68), rCF * CFrame.new(0, 1.5, 0)},
		{V3(8, 0.3, 10), pCF * CFrame.new(0, 1.5, 0)},
	}) do pp{Name = "Carpete", Size = cp[1], CFrame = cp[2], Color = C.carpete, Material = Enum.Material.Fabric} end

	-- curbs (creme) and fascia (vinho)
	for _, s in ipairs({1, -1}) do
		pp{Name = "Meiofio", Size = V3(1.2, 0.9, 30.7), CFrame = CFrame.new(15.4 * s, 0.45, 193.35), Color = C.creme}
		pp{Name = "Meiofio", Size = V3(1.2, 0.9, 28.68), CFrame = rCF * CFrame.new(15.4 * s, 1.95, 0), Color = C.creme}
		pp{Name = "Meiofio", Size = V3(1.2, 0.9, 10), CFrame = pCF * CFrame.new(15.4 * s, 1.95, 0), Color = C.creme}
		pp{Name = "Fascia", Size = V3(1.0, 2.6, 30.7), CFrame = CFrame.new(16.5 * s, -1.3, 193.35), Color = C.vinho}
		pp{Name = "Fascia", Size = V3(1.0, 2.6, 28.68), CFrame = rCF * CFrame.new(16.5 * s, 0.2, 0), Color = C.vinho}
		pp{Name = "Fascia", Size = V3(1.0, 2.6, 10), CFrame = pCF * CFrame.new(16.5 * s, 0.2, 0), Color = C.vinho}
	end

	-- railing: vertical posts + gold caps + two rails per side per segment
	local function postCap(x, baseY, z)
		pp{Name = "Balaustre", Size = V3(0.9, 3.4, 0.9), CFrame = CFrame.new(x, baseY + 1.7, z), Color = C.grade}
		pp{Name = "BalaustreTopo", Size = V3(1.2, 0.4, 1.2), CFrame = CFrame.new(x, baseY + 3.6, z),
			Color = C.ouro, Material = Enum.Material.Metal}
	end
	for _, s in ipairs({1, -1}) do
		for _, z in ipairs({184.5, 190.5, 196.5, 202.5}) do postCap(15.4 * s, 0.9, z) end
		for _, lz in ipairs({-12, -6, 0, 6, 12}) do
			local b = (rCF * CFrame.new(15.4 * s, 2.4, lz)).Position
			postCap(b.X, b.Y, b.Z)
		end
		postCap(15.4 * s, 7.0, 239)
		for _, y in ipairs({2.4, 4.0}) do
			pp{Name = "Corrimao", Size = V3(0.45, 0.45, 30.7), CFrame = CFrame.new(15.4 * s, y, 193.35), Color = C.grade} end
		for _, ly in ipairs({3.9, 5.5}) do
			pp{Name = "Corrimao", Size = V3(0.45, 0.45, 28.68), CFrame = rCF * CFrame.new(15.4 * s, ly, 0), Color = C.grade}
			pp{Name = "Corrimao", Size = V3(0.45, 0.45, 10), CFrame = pCF * CFrame.new(15.4 * s, ly, 0), Color = C.grade}
		end
	end

	-- 6 lamp posts with hanging red lanterns
	local function lamp(s, z, curbTop)
		local top = curbTop + 9
		pp{Name = "LampiaoPoste", Size = V3(1.2, 9, 1.2), CFrame = CFrame.new(15.4 * s, curbTop + 4.5, z), Color = C.laca}
		pp{Name = "LampiaoTopo", Size = V3(1.6, 0.5, 1.6), CFrame = CFrame.new(15.4 * s, top + 0.25, z),
			Color = C.ouro, Material = Enum.Material.Metal}
		pp{Name = "LampiaoBraco", Size = V3(2.8, 0.5, 0.5), CFrame = CFrame.new((15.4 + 1.4) * s, top - 0.25, z), Color = C.laca}
		local lant = H.libClone("KIT", "KIT_lanterna_vermelha", PS)
		lant.Size = LS
		lant.CFrame = CFrame.new(17.9 * s, (top - 0.5) - LS.Y / 2, z)
		local pl = Instance.new("PointLight")
		pl.Range = 14 pl.Brightness = 1.5 pl.Color = C.luz pl.Shadows = false pl.Parent = lant
	end
	for _, s in ipairs({1, -1}) do lamp(s, 178.5, 0.9) lamp(s, 208.5, 0.9) lamp(s, 243.5, 7.0) end

	-- stone piers + arch ribs (visual: side view reads as an arched bridge)
	pp{Name = "Pilar", Size = V3(30, 26, 6), CFrame = CFrame.new(0, -16, 200), Color = C.pilar, Material = Enum.Material.Slate}
	pp{Name = "Pilar", Size = V3(30, 28.8, 6), CFrame = CFrame.new(0, -14.6, 222), Color = C.pilar, Material = Enum.Material.Slate}
	for _, s in ipairs({1, -1}) do
		local pts = {}
		for i = 0, 8 do
			local phi = math.pi - i * math.pi / 8
			pts[i + 1] = V3(15.5 * s, -14 + 9.5 * math.sin(phi), 211 + 9.5 * math.cos(phi))
		end
		for i = 1, 8 do
			local a, b = pts[i], pts[i + 1]
			pp{Name = "ArcoCostela", Size = V3(1.0, 1.4, 4.0), CFrame = CFrame.lookAt((a + b) / 2, b), Color = C.vinho}
		end
	end

	-- apron railing (same recipe), posts stand at Y -0.1..3.3
	for _, s in ipairs({1, -1}) do
		for _, x in ipairs({16.3, 22.3, 28.3, 34.3, 40.3, 46.3}) do postCap(x * s, -0.1, 178.3) end
		for _, z in ipairs({156, 162, 168, 174}) do postCap(46.3 * s, -0.1, z) end
		for _, y in ipairs({1.4, 3.0}) do
			pp{Name = "Corrimao", Size = V3(30, 0.45, 0.45), CFrame = CFrame.new(31.3 * s, y, 178.3), Color = C.grade}
			pp{Name = "Corrimao", Size = V3(0.45, 0.45, 28), CFrame = CFrame.new(46.3 * s, y, 164), Color = C.grade}
		end
	end

	-- colliders
	H.collider("hx_f7_lado_E", V3(0.6, 20, 66), CFrame.new(16.3, 9, 211))
	H.collider("hx_f7_lado_W", V3(0.6, 20, 66), CFrame.new(-16.3, 9, 211))
	H.collider("hx_f7_aprF_E", V3(29.7, 12, 0.6), CFrame.new(31.15, 6, 178.3))
	H.collider("hx_f7_aprF_W", V3(29.7, 12, 0.6), CFrame.new(-31.15, 6, 178.3))
	H.collider("hx_f7_aprL_E", V3(0.6, 12, 28), CFrame.new(46.3, 6, 164))
	H.collider("hx_f7_aprL_W", V3(0.6, 12, 28), CFrame.new(-46.3, 6, 164))

	-- cliff lowering (rule; offsets from CF0)
	for _, m in ipairs(moves) do
		H.remember(m.part)
		m.part.CFrame = m.part:GetAttribute("CF0") + V3(0, m.dy, 0)
		say(("cliff %s centre(%.2f,%.2f,%.2f) top %.2f dY %.2f"):format(m.part.Name, m.c.X, m.c.Y, m.c.Z, m.top, m.dy))
	end

	-- ---------- checks ----------
	-- keepers exactly equal CF0/S0
	for name, p in pairs(KP) do
		local a = {p:GetAttribute("CF0"):GetComponents()} local b = {p.CFrame:GetComponents()}
		local d = 0 for i = 1, 12 do d = math.max(d, math.abs(a[i] - b[i])) end
		if d > 0.005 then table.insert(fail, name .. " CFrame drifted " .. d) end
		if not near(p.Size, p:GetAttribute("S0"), 0.001) then table.insert(fail, name .. " Size drifted") end
		if p.CanCollide ~= true then table.insert(fail, name .. " lost CanCollide") end
		if p.Transparency ~= 1 then table.insert(fail, name .. " still visible") end
	end
	-- Lobby_Area1 holds only the 3 invisible keepers
	if #A1:GetChildren() ~= 3 then table.insert(fail, "Lobby_Area1 children " .. #A1:GetChildren() .. " ~= 3") end
	for _, c in ipairs(A1:GetChildren()) do
		if c:IsA("BasePart") and c.Transparency < 1 then table.insert(fail, "visible part left: " .. c.Name) end
	end
	-- generated parts: never collidable/queryable
	local nParts, nLights, nLant = 0, 0, 0
	for _, c in ipairs(PS:GetChildren()) do
		if c:IsA("BasePart") then
			nParts = nParts + 1
			if c.CanCollide or c.CanQuery then table.insert(fail, "PS part collidable: " .. c.Name) end
		end
		if c.Name == "KIT_lanterna_vermelha" then nLant = nLant + 1 end
	end
	for _, d in ipairs(PS:GetDescendants()) do if d:IsA("PointLight") then nLights = nLights + 1 end end
	if nParts ~= 160 then table.insert(fail, "PS parts " .. nParts .. " ~= 160") end
	if nLights ~= 6 or nLant ~= 6 then table.insert(fail, ("lanterns %d / lights %d ~= 6/6"):format(nLant, nLights)) end
	local nColl = 0
	for _, c in ipairs(COL:GetChildren()) do
		if c.Name:sub(1, 6) == "hx_f7_" and c:GetAttribute("HexCollider") then nColl = nColl + 1 end end
	if nColl ~= 6 then table.insert(fail, "hx_f7_ colliders " .. nColl .. " ~= 6") end
	-- cliffs after the move: nothing above -0.3 near the exit; nothing above -3.3 under the deck
	for _, d in ipairs(L.Patio:GetChildren()) do
		if d:IsA("BasePart") and d.Name:sub(1, 12) == "LOB_penhasco" then
			local mn, mx = aabb(d.CFrame, d.Size)
			if mx.X > -75 and mn.X < 75 and mx.Z > 178 and mn.Z < 244 then
				if mx.X > -18 and mn.X < 18 and mx.Y > -3.25 then
					table.insert(fail, ("cliff under deck top %.2f > -3.3 at (%.1f,%.1f)"):format(mx.Y, (mn.X+mx.X)/2, (mn.Z+mx.Z)/2))
				elseif mx.Y > -0.25 then
					table.insert(fail, ("cliff top %.2f > -0.3 at (%.1f,%.1f)"):format(mx.Y, (mn.X+mx.X)/2, (mn.Z+mx.Z)/2))
				end
			end
		end
	end
	-- walk profile identical
	local postWalk = profile(Enum.RaycastFilterType.Include, {KP.Estrada, KP.RampaArea1, KP.RampaPatamar}, 179, 244)
	local postEnv = profile(Enum.RaycastFilterType.Exclude, {PS}, 150, 244)
	local dw, de = 0, 0
	for i = 1, #preWalk do dw = math.max(dw, math.abs(postWalk[i] - preWalk[i])) end
	for i = 1, #preEnv do de = math.max(de, math.abs(postEnv[i] - preEnv[i])) end
	if dw > 0.011 then table.insert(fail, "walk profile changed by " .. dw) end
	if de > 0.011 then table.insert(fail, "environment profile changed by " .. de) end
	-- walk profile shape: 0 up to Z 208, rising, then 6.1 flat to 244
	for i, z in ipairs({179, 190, 200, 208}) do
		local v = postWalk[z - 178]
		if math.abs(v) > 0.06 then table.insert(fail, ("walk h(%d)=%.2f ~= 0"):format(z, v)) end
	end
	for z = 238, 244 do
		local v = postWalk[z - 178]
		if math.abs(v - 6.1) > 0.06 then table.insert(fail, ("walk h(%d)=%.2f ~= 6.1"):format(z, v)) end
	end
	for z = 210, 236 do
		local a, b = postWalk[z - 179], postWalk[z - 178]
		if b + 0.02 < a or b - a > 0.5 then table.insert(fail, ("walk rise not smooth at Z %d (%.2f->%.2f)"):format(z, a, b)) end
	end
	say(("profiles: walk max delta %.3f, env max delta %.3f; h(179)=%.2f h(208)=%.2f h(240)=%.2f")
		:format(dw, de, postWalk[1], postWalk[30], postWalk[62]))

	-- stray LaminaDagua next to the exit: measured and reported (owned by F2; not touched here)
	local lamMsg = "stray LaminaDagua: not found"
	for _, d in ipairs(L.AGUA:GetChildren()) do
		if d.Name == "LaminaDagua" and near(d.Position, V3(-64, -17, 192), 1) then
			local mn, mx = aabb(d.CFrame, d.Size)
			local casc
			for _, q in ipairs(L.Patio:GetChildren()) do
				if q.Name == "LOB_cascata" and q.Position.Z > 150 then casc = q end end
			lamMsg = ("stray LaminaDagua at (%.1f,%.1f,%.1f), AABB x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]; cascade at %s, gap %.1f; sheet top %.1f pokes above ground -0.5")
				:format(d.Position.X, d.Position.Y, d.Position.Z, mn.X, mx.X, mn.Y, mx.Y, mn.Z, mx.Z,
					casc and ("(%.1f,%.1f,%.1f)"):format(casc.Position.X, casc.Position.Y, casc.Position.Z) or "?",
					casc and (V3(d.Position.X, 0, d.Position.Z) - V3(casc.Position.X, 0, casc.Position.Z)).Magnitude or -1, mx.Y)
		end
	end
	say(lamMsg)

	assert(#fail == 0, "F7 checks FAILED:\n" .. table.concat(fail, "\n"))
	say(("built: %d parts in HEX_PonteSaida, %d hx_f7_ colliders, %d cliffs lowered"):format(nParts, nColl, #moves))
	L:SetAttribute("HEX_F7_OK", true)
	say("marker HEX_F7_OK set")
end)
if not okRun then
	if recId then CHS:FinishRecording(recId, Enum.FinishRecordingOperation.Cancel) end
	return "F7 CANCELLED (all writes reverted):\n" .. tostring(errRun) .. "\n---- partial report ----\n" .. table.concat(rep, "\n")
end
H.commit(recId)
return "F7 OK\n" .. table.concat(rep, "\n")
