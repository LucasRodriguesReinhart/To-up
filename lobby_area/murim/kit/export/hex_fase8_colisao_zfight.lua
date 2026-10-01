-- hex_fase8_colisao_zfight.lua : F8 = hitboxes, z-fighting and proportion pass, with automated scans.
-- A) every MeshPart under LOBBY_MURIM non-collidable/non-queryable, CollisionFidelity Box (pcall-tested).
-- B) generic hx_f8_ colliders: 131 balustrades, 26 forge columns (spec said 27; live count after the
--    F1 removals is 8+8+5+5 = 26), 2 porch side panels, 8 banners (4 already have f3/f4 colliders),
--    forge props + braziers, training props, 8 VIA posts.
--    F3 reviewer pendencias folded in: 5 cylinder colliders (3.6 diameter) for the inner SANT_galeria
--    colonnade columns at gallery-local X 110 (part-local X -14.70, Z -26/-13/0/13/26, measured with
--    EditableMesh), box colliders for the 2 end columns (Z +-39), and visible newel fillers closing the
--    uneven terrace-front gaps beside the 22.8 stair (lz -13.45..-11.40 and 11.40..12.35, 6.38 drop).
-- C) z-fight: 16 KIT_dougong_principal (CF0*+0.1 local Z), 9 KIT_forro_alpendre Size.X 9.44 -> 9.0 (from S0).
-- D) LOD Disabled, RenderFidelity Precise on the 66 listed meshes, CastShadow false per spec.
-- E) scans: duplicates, near-coplanar, invisible floors, 4-stud walkability grid, pad/Disco/MailBox clearance.
-- Idempotent: H.clearColliders("hx_f8_") + clear of HEX_Detalhes.F8; all Size/CFrame edits from CF0/S0.
-- Stage 1 is read-only and aborts before any write. Stage 2 runs in one ChangeHistory recording that is
-- CANCELLED on any failed check.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, COL, C = H.L, H.COL, H.C
local CHS = game:GetService("ChangeHistoryService")
local V3 = Vector3.new
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end

for _, k in ipairs({"HEX_F0_OK", "HEX_F1_OK", "HEX_F2_OK", "HEX_F3_OK", "HEX_F4_OK", "HEX_F5_OK", "HEX_F6_OK", "HEX_F7_OK"}) do
	assert(L:GetAttribute(k) == true, "F8: marker " .. k .. " missing") end

local function near(a, b, tol) return (a - b).Magnitude <= (tol or 0.05) end
local function aabb(cf, sz)
	local r, u, k = cf.RightVector, cf.UpVector, cf.LookVector
	local hx = (math.abs(r.X) * sz.X + math.abs(u.X) * sz.Y + math.abs(k.X) * sz.Z) / 2
	local hy = (math.abs(r.Y) * sz.X + math.abs(u.Y) * sz.Y + math.abs(k.Y) * sz.Z) / 2
	local hz = (math.abs(r.Z) * sz.X + math.abs(u.Z) * sz.Y + math.abs(k.Z) * sz.Z) / 2
	local p = cf.Position
	return p - V3(hx, hy, hz), p + V3(hx, hy, hz)
end

-- ============================== stage 1: read-only ==============================
-- 1a. balustrades: all 3.4 tall, grouped by bottom height
local BALS = {}
local balBottoms = {}
for _, d in ipairs(L:GetDescendants()) do
	if d.Name == "KIT_bal_seg" and d:IsA("BasePart") then
		assert(math.abs(d.Size.Y - 3.4) < 0.02, "F8: KIT_bal_seg not 3.4 tall: " .. tostring(d.Size.Y))
		table.insert(BALS, d)
		local b = string.format("%.1f", d.Position.Y - d.Size.Y / 2)
		balBottoms[b] = (balBottoms[b] or 0) + 1
	end
end
assert(#BALS == 131, "F8: KIT_bal_seg count " .. #BALS .. " ~= 131")
assert(balBottoms["10.0"] == 61, "F8: forge bal (bottom 9.98) " .. tostring(balBottoms["10.0"]) .. " ~= 61")
assert(balBottoms["6.4"] == 45, "F8: gallery bal (bottom 6.38) " .. tostring(balBottoms["6.4"]) .. " ~= 45")
assert(balBottoms["8.0"] == 25, "F8: shop bal (bottom 7.98) " .. tostring(balBottoms["8.0"]) .. " ~= 25")

-- 1b. forge columns
local FCOLS = {}
for _, d in ipairs(L.Patio:GetChildren()) do
	if d.Name == "KIT_coluna" and math.abs(d.Position.X) <= 37 and d.Position.Z < -100 then table.insert(FCOLS, d) end
end
assert(#FCOLS == 26, "F8: forge KIT_coluna " .. #FCOLS .. " ~= 26")

-- 1c. porch side panels
local PORCH = {}
for _, sx in ipairs({36, -36}) do
	local hits = H.findAll({L.Patio}, "KIT_vao_parede", V3(sx, 17, -116), 0.3)
	assert(#hits == 1, "F8: porch panel at X " .. sx .. " -> " .. #hits)
	table.insert(PORCH, hits[1])
end

-- 1d. banners: 12 total, 8 without an existing f3/f4 collider
local oldBanCol = {}
for _, c in ipairs(COL:GetChildren()) do
	if c.Name:find("banner") and c:GetAttribute("HexCollider") then table.insert(oldBanCol, c) end
end
assert(#oldBanCol == 4, "F8: existing banner colliders " .. #oldBanCol .. " ~= 4")
local BANNERS, nCovered = {}, 0
for _, d in ipairs(L:GetDescendants()) do
	if d.Name == "KIT_estandarte" and d:IsA("BasePart") then
		local covered = false
		for _, c in ipairs(oldBanCol) do
			if (V3(c.Position.X, 0, c.Position.Z) - V3(d.Position.X, 0, d.Position.Z)).Magnitude < 2.5 then covered = true end
		end
		if covered then nCovered = nCovered + 1 else table.insert(BANNERS, d) end
	end
end
assert(nCovered == 4 and #BANNERS == 8, ("F8: banners covered %d / new %d ~= 4/8"):format(nCovered, #BANNERS))

-- 1e. props (one each unless stated)
local PROPS = {}
local function findProps(parent, name, n)
	local t = {}
	for _, d in ipairs(parent:GetDescendants()) do if d.Name == name and d:IsA("BasePart") then table.insert(t, d) end end
	assert(#t == n, ("F8: %s -> %d ~= %d"):format(name, #t, n))
	for _, p in ipairs(t) do table.insert(PROPS, p) end
end
findProps(L.Forja, "LOB_fornalha", 1)
findProps(L.Forja, "LOB_bigorna", 1)
findProps(L.Forja, "LOB_fole", 1)
findProps(L.Forja, "LOB_calha_tempera", 1)
findProps(L.Forja, "LOB_altar_laminas", 1)
findProps(L, "LOB_braseiro", 2)
findProps(L, "LOB_poste_treino", 9)
findProps(L, "LOB_boneco_treino", 2)
findProps(L, "LOB_estante_armas", 1)
assert(#PROPS == 19, "F8: prop list " .. #PROPS)

-- 1f. VIA posts mesh present (colliders use the spec's fixed coordinates)
local viaMesh = L.Portao:FindFirstChild("VIA_postes")
assert(viaMesh and viaMesh:IsA("MeshPart") and near(viaMesh.Position, V3(0, 4.2, 102), 0.3), "F8: VIA_postes mesh missing/moved")

-- 1g. SANT_galeria: exact frame for the colonnade colliders (columns measured via EditableMesh:
--     part-local X -16.72..-12.68 centre -14.70, Z at -39,-26,-13,0,13,26,39, shaft ~3.6 wide)
local GAL
for _, d in ipairs(L.Leste:GetChildren()) do if d.Name == "SANT_galeria" then GAL = d end end
assert(GAL, "F8: SANT_galeria missing in Leste")
assert(GAL.MeshId == "rbxassetid://107026906664363", "F8: SANT_galeria MeshId changed: " .. GAL.MeshId)
assert(near(GAL.Size, V3(41.8, 26, 89.2), 0.05), "F8: SANT_galeria size " .. tostring(GAL.Size))
do
	local want = H.TG * CFrame.new(124.699997, 19.3799992, 0)
	local a = {want:GetComponents()} local b = {GAL.CFrame:GetComponents()}
	local dmax = 0 for i = 1, 12 do dmax = math.max(dmax, math.abs(a[i] - b[i])) end
	assert(dmax < 0.01, "F8: SANT_galeria not at TG*CF0 (delta " .. dmax .. ")")
end

-- 1h. dougong rows (17 each), 8 z-fight targets per row by CF0 X
local DOUG = {}
for _, z in ipairs({-109.06, -123.06}) do
	local row, targets = 0, 0
	for _, d in ipairs(L.Patio:GetChildren()) do
		if d.Name == "KIT_dougong_principal" and d:IsA("BasePart") then
			local cf = d:GetAttribute("CF0") or d.CFrame
			if math.abs(cf.Z - z) < 0.3 then
				row = row + 1
				local ax = math.abs(cf.X)
				if math.abs(ax - 4.5) < 0.05 or math.abs(ax - 13.5) < 0.05 or math.abs(ax - 22.5) < 0.05 or math.abs(ax - 31.5) < 0.05 then
					targets = targets + 1
					table.insert(DOUG, d)
				end
			end
		end
	end
	assert(row == 17, ("F8: dougong row Z %.2f -> %d ~= 17"):format(z, row))
	assert(targets == 8, ("F8: dougong targets Z %.2f -> %d ~= 8"):format(z, targets))
end

-- 1i. forro alpendre
local FORRO = {}
for _, d in ipairs(L.Patio:GetChildren()) do
	if d.Name == "KIT_forro_alpendre" and d:IsA("BasePart") then
		local s0 = d:GetAttribute("S0") or d.Size
		assert(math.abs(s0.X - 9.44) < 0.02, "F8: forro S0.X " .. tostring(s0.X))
		table.insert(FORRO, d)
	end
end
assert(#FORRO == 9, "F8: forro " .. #FORRO .. " ~= 9")

-- 1j. gallery terrace-front gaps beside the widened stair, from live pieces
local TG = H.TG
local rampa = COL:FindFirstChild("hx_f3_gal_rampa")
assert(rampa and math.abs(rampa.Size.X - 22.8) < 0.05, "F8: hx_f3_gal_rampa missing or not 22.8 wide")
local leftEnd, rightStart = -math.huge, math.huge
for _, d in ipairs(BALS) do
	local lp = TG:PointToObjectSpace(d.Position)
	if math.abs(lp.X - 104.80) < 0.5 and math.abs(lp.Y - 8.08) < 0.3 then -- gallery front row
		if lp.Z < -11.4 then leftEnd = math.max(leftEnd, lp.Z + 2.7) end
		if lp.Z > 11.4 then rightStart = math.min(rightStart, lp.Z - 2.7) end
	end
end
assert(math.abs(leftEnd - -13.45) < 0.2 and math.abs(rightStart - 12.35) < 0.2,
	("F8: front gaps unexpected: leftEnd %.2f rightStart %.2f"):format(leftEnd, rightStart))
local GAPL = {leftEnd, -11.40}
local GAPR = {11.40, rightStart}

-- 1k. render-fidelity targets: exact family counts
local RF = {}
local function rfAdd(d) table.insert(RF, d) end
local cTF1, cTF2, cTG, cESC, cMOL = 0, 0, 0, 0, 0
for _, d in ipairs(L:GetDescendants()) do
	if d:IsA("MeshPart") then
		local n = d.Name
		if n:sub(1, 6) == "TEL_F1" then cTF1 = cTF1 + 1 rfAdd(d)
		elseif n:sub(1, 6) == "TEL_F2" then cTF2 = cTF2 + 1 rfAdd(d)
		elseif n:sub(1, 5) == "TEL_G" and d.Parent == L.Forja and d.Position.Z > 120 and d.Position.Z < 180 then cTG = cTG + 1 rfAdd(d)
		elseif n:sub(1, 6) == "ESCADA" then cESC = cESC + 1 rfAdd(d)
		elseif n:sub(1, 11) == "POR_moldura" then cMOL = cMOL + 1 rfAdd(d)
		end
	end
end
assert(cTF1 == 17 and cTF2 == 17 and cTG == 17 and cESC == 3 and cMOL == 6,
	("F8: RF families %d/%d/%d/%d/%d ~= 17/17/17/3/6"):format(cTF1, cTF2, cTG, cESC, cMOL))
for _, spec in ipairs({{L.Leste, "SANT_galeria"}, {L.Portao, "PORTAO_muralha"}, {L.Portao, "PORTAO_parapeito"},
	{L.Patio, "FORJA_claraboia"}, {L.Patio, "LOB_picareta_aurora"}, {L.Patio, "LOJA_interior"}}) do
	local f = spec[1]:FindFirstChild(spec[2])
	assert(f and f:IsA("MeshPart"), "F8: RF single missing: " .. spec[2])
	rfAdd(f)
end
assert(#RF == 66, "F8: RF list " .. #RF .. " ~= 66")

local DET = L:FindFirstChild("HEX_Detalhes")
assert(DET, "F8: HEX_Detalhes missing")
local oldF8 = DET:FindFirstChild("F8")
if oldF8 then for _, c in ipairs(oldF8:GetChildren()) do
	assert(c:GetAttribute("HexGen"), "F8: foreign child in HEX_Detalhes.F8: " .. c.Name) end end

say(("stage1 OK: bal 131 (61/45/25), fcol 26, porch 2, banners 8 new (4 covered), props 19, dougong 16, forro 9, RF 66, gaps L[%.2f..%.2f] R[%.2f..%.2f]")
	:format(GAPL[1], GAPL[2], GAPR[1], GAPR[2]))

-- ============================== stage 2: one recording ==============================
local recId = H.begin("HEX F8 colisao zfight")
local okRun, errRun = pcall(function()
	local fail = {}
	H.clearColliders("hx_f8_")
	local F8F = H.folder(DET, "F8")
	F8F:SetAttribute("HexGen", true)
	H.clear(F8F)

	-- ---------- A) decorative meshparts ----------
	local nFlag, nFid, fidErr = 0, 0, nil
	local meshes = {}
	for _, d in ipairs(L:GetDescendants()) do if d:IsA("MeshPart") then table.insert(meshes, d) end end
	for _, d in ipairs(meshes) do
		if d.CanCollide or d.CanTouch or d.CanQuery then nFlag = nFlag + 1 end
		d.CanCollide = false d.CanTouch = false d.CanQuery = false
	end
	local okFid, e1 = pcall(function() meshes[1].CollisionFidelity = Enum.CollisionFidelity.Box end)
	if okFid then
		for _, d in ipairs(meshes) do
			local ok2 = pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Box end)
			if ok2 then nFid = nFid + 1 end
		end
	else fidErr = tostring(e1) end
	say(("A: %d meshparts swept (%d had a flag on), CollisionFidelity Box on %d%s")
		:format(#meshes, nFlag, nFid, fidErr and (" SKIPPED: " .. fidErr) or ""))

	-- ---------- C) z-fighting ----------
	for _, d in ipairs(DOUG) do
		local cf0 = H.cf0(d)
		d.CFrame = cf0 * CFrame.new(0, 0, 0.1)
	end
	for _, d in ipairs(FORRO) do
		local s0 = H.s0(d)
		d.Size = V3(9.0, s0.Y, s0.Z)
	end
	say(("C: %d dougong offset +0.1 local Z from CF0; %d forro Size.X 9.44 -> 9.0"):format(#DOUG, #FORRO))

	-- ---------- D) LOD and rendering ----------
	local okLod = pcall(function() L.LevelOfDetail = Enum.ModelLevelOfDetail.Disabled end)
	local nRF, nRFerr = 0, 0
	for _, d in ipairs(RF) do
		local ok2 = pcall(function() d.RenderFidelity = Enum.RenderFidelity.Precise end)
		if ok2 then nRF = nRF + 1 else nRFerr = nRFerr + 1 end
	end
	local nShadow = 0
	local function unshadow(p) if p:IsA("BasePart") and p.CastShadow then p.CastShadow = false nShadow = nShadow + 1 end end
	for _, d in ipairs(L.HEX_Chao:GetDescendants()) do unshadow(d) end
	for _, d in ipairs(L.HEX_Lagos:GetDescendants()) do
		if d:IsA("BasePart") then
			local n = d.Name
			if n:sub(1, 4) == "Agua" or n:sub(1, 5) == "Lirio" or n:sub(1, 9) == "Longarina" then unshadow(d) end
		end
	end
	for _, m in ipairs(L:GetDescendants()) do
		if m:IsA("Model") and m:FindFirstChild("Plinto") then
			for _, p in ipairs(m:GetDescendants()) do
				if p:IsA("BasePart") and p.Name ~= "Plinto" then unshadow(p) end
			end
		end
	end
	for _, d in ipairs(meshes) do
		local s = d.Size
		if s.X < 4 and s.Y < 4 and s.Z < 4 then unshadow(d) end
	end
	say(("D: LOD Disabled=%s, RenderFidelity Precise on %d (%d failed), CastShadow turned off on %d")
		:format(tostring(okLod), nRF, nRFerr, nShadow))

	-- ---------- B) colliders ----------
	local nCol = 0
	local function addCol(name, size, cf)
		nCol = nCol + 1
		return H.collider(name, size, cf)
	end
	for i, d in ipairs(BALS) do
		local bottom = d.Position.Y - d.Size.Y / 2
		addCol("hx_f8_bal_" .. i, V3(d.Size.X, 3.6, math.max(d.Size.Z, 1.0)),
			d.CFrame + V3(0, (bottom + 1.8) - d.CFrame.Y, 0))
	end
	for i, d in ipairs(FCOLS) do addCol("hx_f8_fcol_" .. i, d.Size, d.CFrame) end
	for i, d in ipairs(PORCH) do addCol("hx_f8_porch_" .. i, V3(9, 14.1, 1.9), d.CFrame) end
	for i, d in ipairs(BANNERS) do addCol("hx_f8_ban_" .. i, V3(0.55 * d.Size.X, d.Size.Y, d.Size.Z), d.CFrame) end
	for i, d in ipairs(PROPS) do
		local mn, mx = aabb(d.CFrame, d.Size)
		addCol("hx_f8_prop_" .. d.Name .. "_" .. i, mx - mn, CFrame.new((mn + mx) / 2))
	end
	local iv = 0
	for _, sx in ipairs({21, -21}) do for _, z in ipairs({72, 92, 112, 132}) do
		iv = iv + 1
		addCol("hx_f8_via_" .. iv, V3(1.2, 8.4, 1.2), CFrame.new(sx, 4.2, z))
	end end
	-- colonnade: columns measured at part-local X -14.70; collider spans world Y 6.38..23.50
	local gCF = GAL.CFrame
	local colY = (6.38 + 23.50) / 2 - 19.38 -- part-local Y of the collider centre
	local colH = 23.50 - 6.38
	for i, z in ipairs({-26, -13, 0, 13, 26}) do
		local p = addCol("hx_f8_galcol_" .. i, V3(colH, 3.6, 3.6),
			gCF * CFrame.new(-14.70, colY, z) * CFrame.Angles(0, 0, math.rad(90)))
		p.Shape = Enum.PartType.Cylinder
	end
	addCol("hx_f8_galcol_endS", V3(4.1, colH, 4.1), gCF * CFrame.new(-14.70, colY, -39))
	addCol("hx_f8_galcol_endN", V3(4.1, colH, 4.1), gCF * CFrame.new(-14.70, colY, 39))
	say(("B: %d hx_f8_ colliders (131 bal, 26 fcol, 2 porch, 8 banner, %d prop, 8 via, 7 colonnade)"):format(nCol, #PROPS))

	-- ---------- terrace-front newel fillers (visible, collidable) ----------
	local function newel(tag, g)
		local w = g[2] - g[1]
		local cz = (g[1] + g[2]) / 2
		H.part({Name = "GalNewel_" .. tag, Size = V3(2.4, 9.78, w + 0.4), CFrame = TG * CFrame.new(103.9, 4.89, cz),
			Color = C.creme, CanCollide = true}, F8F)
		H.part({Name = "GalNewelCap_" .. tag, Size = V3(3.0, 0.5, w + 1.1), CFrame = TG * CFrame.new(103.9, 10.03, cz),
			Color = C.cremeS, CanCollide = true}, F8F)
	end
	newel("L", GAPL)
	newel("R", GAPR)
	say(("fillers: 2 newel pylons at gallery front, lz [%.2f..%.2f] and [%.2f..%.2f], Y 0..10.28"):format(GAPL[1], GAPL[2], GAPR[1], GAPR[2]))

	-- ---------- E) automated scans ----------
	-- oriented plan boxes (rect + SAT): plain AABBs of the 30-degree-rotated parts overlap where the
	-- real rectangles only abut, which gave false positives in E2/E5 dry runs
	local function planOf(cf, sz)
		local ax = {{cf.RightVector, sz.X / 2}, {cf.UpVector, sz.Y / 2}, {cf.LookVector, sz.Z / 2}}
		local A, R = {}, {}
		for _, a in ipairs(ax) do
			if math.abs(a[1].Y) < 0.99 then
				local v = Vector2.new(a[1].X, a[1].Z)
				if v.Magnitude < 0.95 then return nil end
				table.insert(A, v.Unit) table.insert(R, a[2])
			end
		end
		if #A ~= 2 then return nil end
		local mn, mx = aabb(cf, sz)
		return {c = Vector2.new(cf.X, cf.Z), a = A, r = R, y1 = mn.Y, y2 = mx.Y}
	end
	local function rectOf(cf, sz)
		local mn, mx = aabb(cf, sz)
		return {c = Vector2.new((mn.X + mx.X) / 2, (mn.Z + mx.Z) / 2),
			a = {Vector2.new(1, 0), Vector2.new(0, 1)}, r = {(mx.X - mn.X) / 2, (mx.Z - mn.Z) / 2},
			y1 = mn.Y, y2 = mx.Y}
	end
	local function box2(cf, sz) return planOf(cf, sz) or rectOf(cf, sz) end
	local function hits(A, B, margin)
		if math.min(A.y2, B.y2) - math.max(A.y1, B.y1) <= margin then return false end
		local d = B.c - A.c
		for _, ax2 in ipairs({A.a[1], A.a[2], B.a[1], B.a[2]}) do
			local ra = A.r[1] * math.abs(A.a[1]:Dot(ax2)) + A.r[2] * math.abs(A.a[2]:Dot(ax2))
			local rb = B.r[1] * math.abs(B.a[1]:Dot(ax2)) + B.r[2] * math.abs(B.a[2]:Dot(ax2))
			if math.abs(d:Dot(ax2)) >= ra + rb - margin then return false end
		end
		return true
	end
	local function planArea(A, B) -- rough oriented overlap area along A's axes (0 when only abutting)
		local d = B.c - A.c
		local p = {}
		for i = 1, 2 do
			local rb = B.r[1] * math.abs(B.a[1]:Dot(A.a[i])) + B.r[2] * math.abs(B.a[2]:Dot(A.a[i]))
			p[i] = math.min(A.r[i] + rb - math.abs(d:Dot(A.a[i])), 2 * A.r[i], 2 * rb)
			if p[i] < 0.05 then return 0 end
		end
		return p[1] * p[2]
	end

	-- E1 duplicates
	local groups = {}
	for _, d in ipairs(L:GetDescendants()) do
		if d:IsA("BasePart") then
			local g = groups[d.Name]
			if not g then g = {} groups[d.Name] = g end
			table.insert(g, d)
		end
	end
	local nDup = 0
	for _, g in pairs(groups) do
		if #g > 1 then
			table.sort(g, function(a, b) return a.Position.X < b.Position.X end)
			for i = 1, #g - 1 do
				for j = i + 1, #g do
					local a, b = g[i], g[j]
					if b.Position.X - a.Position.X > 0.02 then break end
					if a.ClassName == b.ClassName and (not a:IsA("MeshPart") or a.MeshId == b.MeshId)
						and (a.Size - b.Size).Magnitude <= 0.01 then
						local ca = {a.CFrame:GetComponents()} local cb = {b.CFrame:GetComponents()}
						local dm = 0 for k = 1, 12 do dm = math.max(dm, math.abs(ca[k] - cb[k])) end
						if dm <= 0.01 then
							nDup = nDup + 1
							if nDup <= 5 then say("E1 dup: " .. a:GetFullName() .. " == " .. b:GetFullName()) end
						end
					end
				end
			end
		end
	end
	if nDup ~= 0 then table.insert(fail, "E1 duplicates: " .. nDup) end

	-- E2 near-coplanar horizontal tops (Parts under HEX_* + KIT_piso_mod meshes), oriented rects.
	-- "wide" uses the MINOR plan extent: a 30-stud rail 0.45 thick is not a plate. Full SAT first,
	-- so abutting or stopped-short strips (mitred rings, radials) do not count.
	local function scanCoplanar()
		local items = {}
		local function addItem(d)
			local bx = box2(d.CFrame, d.Size)
			table.insert(items, {p = d, top = bx.y2, bx = bx, w = 2 * math.min(bx.r[1], bx.r[2])})
		end
		for _, fn in ipairs({"HEX_Chao", "HEX_Muralha", "HEX_Monumento", "HEX_Lagos", "HEX_Canteiros",
			"HEX_Loja", "HEX_Treino", "HEX_Galeria", "HEX_PonteSaida", "HEX_Detalhes"}) do
			local f = L:FindFirstChild(fn)
			if f then for _, d in ipairs(f:GetDescendants()) do
				if d.ClassName == "Part" and d.Shape == Enum.PartType.Block and d.Transparency < 0.95
					and math.abs(d.CFrame.UpVector.Y) > 0.999 then addItem(d) end
			end end
		end
		for _, d in ipairs(L:GetDescendants()) do
			if d:IsA("MeshPart") and d.Name == "KIT_piso_mod" then addItem(d) end
		end
		table.sort(items, function(a, b) return a.top < b.top end)
		local pairsFound = {}
		for i = 1, #items - 1 do
			local a = items[i]
			for j = i + 1, #items do
				local b = items[j]
				if b.top - a.top > 0.101 then break end
				local thr = ((a.w > 20 or b.w > 20) and 0.10 or 0.05) - 0.001
				if b.top - a.top < thr and hits(a.bx, b.bx, 0.04) then
					local area = planArea(a.bx, b.bx)
					if area > 0.25 then table.insert(pairsFound, {a = a, b = b, area = area, thr = thr}) end
				end
			end
		end
		return pairsFound
	end
	-- auto-fix: lower the smaller generated Part of each flagged pair (from CF0, so re-runs do not
	-- stack), just past the pair's threshold; kit meshes are never moved by this pass
	local firstPass = scanCoplanar()
	local need = {}
	for _, pr in ipairs(firstPass) do
		local va, vb = pr.a, pr.b
		local victim = (4 * va.bx.r[1] * va.bx.r[2] <= 4 * vb.bx.r[1] * vb.bx.r[2]) and va or vb
		local other = (victim == va) and vb or va
		if not (victim.p.ClassName == "Part" and victim.p:GetAttribute("HexGen")) then victim = other end
		if victim.p.ClassName == "Part" and victim.p:GetAttribute("HexGen") then
			need[victim.p] = math.max(need[victim.p] or 0, pr.thr + 0.021)
		end
	end
	local nFix = 0
	for p, dy in pairs(need) do
		local cf0 = H.cf0(p)
		p.CFrame = cf0 - V3(0, dy, 0)
		nFix = nFix + 1
		if nFix <= 8 then say(("E2 fix: %s lowered %.3f (top was flush with a neighbour)"):format(p:GetFullName(), dy)) end
	end
	say(("E2: %d coplanar pairs on first pass, %d generated parts lowered"):format(#firstPass, nFix))
	local second = scanCoplanar()
	for k = 1, math.min(#second, 6) do
		local pr = second[k]
		say(("E2 coplanar: %s top %.3f ~ %s top %.3f area %.2f")
			:format(pr.a.p:GetFullName(), pr.a.top, pr.b.p:GetFullName(), pr.b.top, pr.area))
	end
	if #second ~= 0 then table.insert(fail, "E2 near-coplanar after fix: " .. #second) end

	-- E3 invisible floors
	local nInv = 0
	local A1 = workspace:FindFirstChild("Corredores") and workspace.Corredores:FindFirstChild("Lobby_Area1")
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("BasePart") and d.Transparency >= 0.95 and (d.CanCollide or d.CanQuery) then
			local skip = d:IsDescendantOf(COL) or d.Name == "HumanoidRootPart" or d.Name == "SpawnLobby"
				or d:IsA("SpawnLocation")
			if not skip and workspace:FindFirstChild("NPCs") and d:IsDescendantOf(workspace.NPCs) then skip = true end
			if not skip and workspace:FindFirstChild("Santuario") and d:IsDescendantOf(workspace.Santuario) then
				if d.Name == "Disco" then skip = true else
					local q = d
					while q and q ~= workspace do if q.Name == "VFX" then skip = true break end q = q.Parent end
				end
			end
			if not skip and A1 and d.Parent == A1 and (d.Name == "Estrada" or d.Name == "RampaArea1" or d.Name == "RampaPatamar") then skip = true end
			if not skip then
				local mn, mx = aabb(d.CFrame, d.Size)
				if mx.X > -185 and mn.X < 185 and mx.Z > -220 and mn.Z < 280 then
					nInv = nInv + 1
					if nInv <= 6 then say("E3 invisible: " .. d:GetFullName() .. " T=" .. d.Transparency) end
				end
			end
		end
	end
	if nInv ~= 0 then table.insert(fail, "E3 invisible floors: " .. nInv) end

	-- E4 walkability grid
	local rp = RaycastParams.new()
	rp.FilterType = Enum.RaycastFilterType.Exclude
	rp.RespectCanCollide = true
	local WL = {-1.6, 0, 0.25, 0.40, 1.0, 2.0, 6.1, 6.38, 7.98, 8.5, 9.98}
	local n30 = {math.rad(30), math.rad(90), math.rad(150)}
	local function inHex(x, z, a)
		for _, t in ipairs(n30) do if math.abs(x * math.cos(t) + z * math.sin(t)) > a then return false end end
		return true
	end
	local MB = workspace:FindFirstChild("MailBox")
	local nPts, nMissReal, nBad, nSeam = 0, 0, 0, 0
	local function allowedHit(r)
		local h = r.Position.Y
		for _, w in ipairs(WL) do if math.abs(h - w) <= 0.07 then return true end end
		local inst = r.Instance
		if inst:IsDescendantOf(COL) then return true end
		if inst:GetAttribute("HexGen") or inst:GetAttribute("HexCollider") then return true end
		if MB and inst:IsDescendantOf(MB) then return true end
		if inst.Name == "Estrada" or inst.Name == "RampaArea1" or inst.Name == "RampaPatamar" then return true end
		return false
	end
	local function probe(x, z)
		nPts = nPts + 1
		local r = workspace:Raycast(V3(x, 80, z), V3(0, -160, 0), rp)
		if not r then
			-- knife-edge seams on part boundaries: real miss only if an offset probe also misses
			local holes = 0
			for _, o in ipairs({{0.3, 0}, {-0.3, 0}, {0, 0.3}, {0, -0.3}}) do
				if not workspace:Raycast(V3(x + o[1], 80, z + o[2]), V3(0, -160, 0), rp) then holes = holes + 1 end
			end
			if holes > 0 then
				nMissReal = nMissReal + 1
				if nMissReal <= 8 then say(("E4 MISS at (%d,%d), %d offsets also miss"):format(x, z, holes)) end
			else nSeam = nSeam + 1 end
			return
		end
		if not allowedHit(r) then
			nBad = nBad + 1
			if nBad <= 10 then say(("E4 odd: (%d,%d) h=%.2f %s"):format(x, z, r.Position.Y, r.Instance:GetFullName())) end
		end
	end
	for x = -144, 144, 4 do for z = -148, 148, 4 do
		if inHex(x, z, 146) then probe(x, z) end
	end end
	for x = -44, 44, 4 do for z = 152, 176, 4 do probe(x, z) end end
	for x = -12, 12, 4 do for z = 180, 244, 4 do probe(x, z) end end
	say(("E4 grid: %d points, %d real misses, %d knife-edge seams, %d odd hits"):format(nPts, nMissReal, nSeam, nBad))
	if nMissReal ~= 0 then table.insert(fail, "E4 misses: " .. nMissReal) end
	if nBad ~= 0 then table.insert(fail, "E4 odd hits: " .. nBad) end

	-- E5 pad / Disco / MailBox clearance (same oriented plan-SAT as E2)
	local boxes = {}
	local pad = workspace.LojaMochilas.PadLoja
	table.insert(boxes, {"PadLoja", box2(pad.CFrame, pad.Size), false})
	for _, d in ipairs(workspace.Santuario:GetDescendants()) do
		if d.Name == "Disco" and d:IsA("BasePart") then
			table.insert(boxes, {"Disco", box2(d.CFrame, d.Size), false})
		end
	end
	local caixaTight
	if MB then for _, d in ipairs(MB:GetDescendants()) do
		if d.Name == "Caixa" and d:IsA("BasePart") then
			table.insert(boxes, {"Caixa+1", box2(d.CFrame, d.Size + V3(2, 2, 2)), true})
			caixaTight = box2(d.CFrame, d.Size + V3(0.4, 0.4, 0.4))
		end
	end end
	assert(#boxes == 8, "E5: expected 8 boxes, got " .. #boxes)
	local nClash, nExempt = 0, 0
	local function against(part)
		local A = box2(part.CFrame, part.Size)
		for _, b in ipairs(boxes) do
			if hits(A, b[2], 0.02) then
				-- railing colliders back a VISIBLE balustrade that stands beside the MailBox; they may
				-- enter the 1-stud grown margin but never the Caixa itself (prompt needs no line of sight)
				if b[3] and part.Name:sub(1, 9) == "hx_f8_bal" and caixaTight and not hits(A, caixaTight, 0.02) then
					nExempt = nExempt + 1
				else
					nClash = nClash + 1
					if nClash <= 6 then say(("E5 clash: %s overlaps %s box"):format(part.Name, b[1])) end
				end
			end
		end
	end
	for _, c in ipairs(COL:GetChildren()) do if c:IsA("BasePart") and c.CanCollide then against(c) end end
	for _, c in ipairs(F8F:GetChildren()) do if c:IsA("BasePart") and c.CanCollide then against(c) end end
	say(("E5: %d clashes, %d railing colliders inside the grown MailBox margin (visible railing, exempt)"):format(nClash, nExempt))
	if nClash ~= 0 then table.insert(fail, "E5 clearance: " .. nClash) end

	-- ---------- F) proportion report (measured) ----------
	do
		local lion
		for _, d in ipairs(L:GetDescendants()) do if d.Name == "LOB_leao_esfera" then lion = d break end end
		local bench
		for _, d in ipairs(L:GetDescendants()) do if d.Name == "VIL_banco" then bench = d break end end
		local wallTop, towTop = -99, -99
		for _, d in ipairs(L.HEX_Muralha:GetDescendants()) do
			if d:IsA("BasePart") then
				local t = d.Position.Y + d.Size.Y / 2
				if (d.Position.X ^ 2 + d.Position.Z ^ 2) > 158 ^ 2 then towTop = math.max(towTop, t)
				else wallTop = math.max(wallTop, t) end
			end
		end
		local lant
		for _, m in ipairs(L.HEX_Lagos:GetChildren()) do
			if m:IsA("Model") and m:FindFirstChild("Plinto") then
				local _, sz = m:GetBoundingBox() lant = sz.Y break
			end
		end
		local monW, stepH = 0, {}
		for _, d in ipairs(L.HEX_Monumento:GetChildren()) do
			if d:IsA("BasePart") and d.Name:find("passo") or d.Name:find("degrau") then
				table.insert(stepH, d.Size.Y)
			end
			if d:IsA("BasePart") then
				local mn, mx = aabb(d.CFrame, d.Size)
				if mx.Y < 1.2 then monW = math.max(monW, mx.X - mn.X) end
			end
		end
		say(("F proportions: bal 3.40 tall; bench %s; lion %.2f tall base %.2f; wall top %.2f; tower top %.2f; lantern %.2f; monument base width %.1f")
			:format(bench and tostring(bench.Size) or "?", lion and lion.Size.Y or -1,
				lion and (lion.Position.Y - lion.Size.Y / 2) or -1, wallTop, towTop, lant or -1, monW))
	end

	assert(#fail == 0, "F8 checks FAILED:\n" .. table.concat(fail, "\n"))
	L:SetAttribute("HEX_F8_OK", true)
	say("marker HEX_F8_OK set")
end)
if not okRun then
	if recId then CHS:FinishRecording(recId, Enum.FinishRecordingOperation.Cancel) end
	return "F8 CANCELLED (all writes reverted):\n" .. tostring(errRun) .. "\n---- partial report ----\n" .. table.concat(rep, "\n")
end
H.commit(recId)
return "F8 OK\n" .. table.concat(rep, "\n")