-- hex_fase3_galeria.lua : F3 = portal gallery relocation (TG) and portal order easiest -> hardest. No accents.
-- The six portal sets (Santuario.PortalN + their POR_*_<tema> meshes) move rigidly by dZ = -2*Zp in the
-- original frame and then by H.TG, so read from the plaza, left to right, the AreaIds are 1..6.
-- Every other GALERIA-tagged member moves by H.TG. No roof: sign on the colonnade beam, 2 tall end banners,
-- 22.8-wide stair, 2 stair-foot box lanterns, colliders hx_f3_*.
-- Idempotent: clears HEX_Galeria / hx_f3_*, every placement is computed from CF0/S0, removals are counted
-- live + already-removed. On any error after writes began, the ChangeHistory recording is CANCELLED.
-- Deviations from the spec text (all measured on the SANT_galeria / lantern / base meshes, see report):
-- * the sign sits at local X 105.8 (flush against the front beam face at X 107.20), not X 103.3, which
--   would float 3.9 studs in front of the beam;
-- * the 4 gallery KIT_lanterna_palacio hang 5.5 higher (hook into the beam instead of 4.9 below it) and the
--   two at Z +-40, which sat inside the end columns, hang at their bay centres Z +-32.5;
-- * the 6 portal-base colliders are Cylinders (the POR_base meshes are round discs), not boxes;
-- * the GAL_A/GAL_B banners stay in Props (reparenting them into HEX_Galeria would let H.clear destroy them).
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, REM = H.L, H.REM
local CHS = game:GetService("ChangeHistoryService")
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end
local function v3s(v) return ("(%.2f,%.2f,%.2f)"):format(v.X, v.Y, v.Z) end
assert(L:GetAttribute("HEX_F0_OK") == true, "F3: F0 marker HEX_F0_OK missing")
assert(L:GetAttribute("HEX_F1_OK") == true, "F3: F1 marker HEX_F1_OK missing")
assert(L:GetAttribute("HEX_F2_OK") == true, "F3: F2 marker HEX_F2_OK missing (run hex_fase2_perimetro_chao.lua first)")

local P, Le, Pr, COL = L.Patio, L.Leste, L.Props, H.COL
local SANT = workspace:FindFirstChild("Santuario")
local HG = L:FindFirstChild("HEX_Galeria")
local TG = H.TG
local FASE = "F3_R09b_R14"
local TEMA = {"chakra", "ki", "nichirin", "sombra", "mare", "serio"}
local TARGET = {Vector3.new(97.75, 9.55, -80.11), Vector3.new(104.25, 9.55, -68.85), Vector3.new(110.75, 9.55, -57.59),
	Vector3.new(117.25, 9.55, -46.33), Vector3.new(123.75, 9.55, -35.07), Vector3.new(130.25, 9.55, -23.81)}
local SIGN_X = 105.8 -- beam front face X 107.20 (measured on the SANT_galeria mesh) minus half the placa depth 1.37
local LANT_DY = 5.5  -- palace lantern hook top 20.38 -> 25.88, 0.6 into the beam bottom 25.28 (measured)

------------------------------------------------------------------ read-only gather + asserts
local bad = {}
if not SANT then table.insert(bad, "workspace.Santuario missing") end
if not HG then table.insert(bad, "LOBBY_MURIM.HEX_Galeria missing (F0 creates it)") end
if #bad > 0 then error("F3 aborted before writing anything:\n" .. table.concat(bad, "\n")) end
-- HEX_Galeria may only hold what this phase generates (H.clear destroys its children)
for _, c in ipairs(HG:GetChildren()) do
	if not c:GetAttribute("HexGen") then table.insert(bad, "HEX_Galeria holds a non-generated instance: " .. c:GetFullName()) end end

-- 1) removals: each item is either live in its original parent or already in REM/F3_R09b_R14
local remF = REM:FindFirstChild(FASE)
local function removedMatch(parent, name, pos)
	local r = {}
	if remF then for _, c in ipairs(remF:GetChildren()) do
		if c.Name == name and c:GetAttribute("OrigemPath") == parent:GetFullName() then
			local cf = c:GetAttribute("CF0")
			if pos == nil or (cf and (cf.Position - pos).Magnitude <= 0.3) then table.insert(r, c) end end end end
	return r end
local RITEMS = {}
for i = 1, 8 do table.insert(RITEMS, {parent = COL, name = "degrau_sant" .. i}) end
for _, q in ipairs({{"KIT_bal_seg", 104.80, 8.80, -10.95}, {"KIT_bal_seg", 104.80, 8.80, 9.85},
	{"KIT_sumeru_seg", 103.52, 4.39, -10.80}, {"KIT_sumeru_seg", 103.52, 4.39, 10.38}}) do
	table.insert(RITEMS, {parent = P, name = q[1], pos = Vector3.new(q[2], q[3], q[4])}) end
local toRemove, nAlready, isTarget = {}, 0, {}
for _, it in ipairs(RITEMS) do
	local live
	if it.pos then live = H.findAll({it.parent}, it.name, it.pos, 0.3)
	else live = {} for _, c in ipairs(it.parent:GetChildren()) do if c.Name == it.name then table.insert(live, c) end end end
	local done = removedMatch(it.parent, it.name, it.pos)
	local lbl = it.parent.Name .. "." .. it.name .. (it.pos and (" @" .. v3s(it.pos)) or "")
	if #live + #done ~= 1 then table.insert(bad, ("%s: live %d + removed %d ~= 1"):format(lbl, #live, #done))
	else
		for _, c in ipairs(live) do
			if not c:IsA("BasePart") then table.insert(bad, lbl .. ": not a BasePart") end
			if it.pos and c:GetAttribute("HEX_GRUPO") ~= "GALERIA" then table.insert(bad, lbl .. ": not tagged GALERIA") end
			if not it.pos then local cf = c:GetAttribute("CF0") or c.CFrame
				if math.abs(cf.Z) > 0.05 or cf.X < 90 or cf.X > 104.5 then table.insert(bad, lbl .. ": unexpected position " .. v3s(cf.Position)) end end
			table.insert(toRemove, c) isTarget[c] = true end
		nAlready += #done
	end
end

-- 2) portal sets
local SETS = {}
for n = 1, 6 do
	local m = SANT:FindFirstChild("Portal" .. n)
	local d = m and m:FindFirstChild("Disco")
	if not (m and m:IsA("Model")) then table.insert(bad, "Santuario.Portal" .. n .. " missing or not a Model")
	elseif not (d and d:IsA("BasePart") and d:GetAttribute("AreaId") == n) then table.insert(bad, ("Portal%d Disco/AreaId mismatch"):format(n))
	elseif m:GetAttribute("CF0") == nil or m:GetAttribute("HEX_GRUPO") ~= "GALERIA" then table.insert(bad, "Portal" .. n .. " lacks CF0 or GALERIA tag")
	else SETS[n] = {model = m, disco = d, por = {}, dz = -2 * (32.5 - 13 * (n - 1))} end
end
local porAll = 0
for _, c in ipairs(Le:GetChildren()) do
	if c.Name:sub(1, 4) == "POR_" then porAll += 1
		local hit = 0
		for n, t in ipairs(TEMA) do if c.Name:sub(-(#t + 1)) == "_" .. t then hit += 1 if SETS[n] then table.insert(SETS[n].por, c) end end end
		if hit ~= 1 then table.insert(bad, "POR piece with no/ambiguous theme: " .. c.Name) end
		if c:GetAttribute("HEX_GRUPO") ~= "GALERIA" or c:GetAttribute("CF0") == nil then table.insert(bad, c.Name .. " lacks CF0 or GALERIA tag") end
	end
end
if porAll ~= 30 then table.insert(bad, ("Leste POR_*: %d (expected 30)"):format(porAll)) end
local isPortalSet = {}
for n = 1, 6 do local S = SETS[n] if S then
	local k = {base = 0, moldura = 0, vortice = 0, fragmento_1 = 0}
	for _, c in ipairs(S.por) do isPortalSet[c] = true
		for key in pairs(k) do if c.Name == "POR_" .. key .. "_" .. TEMA[n] then k[key] += 1 end end end
	if not (#S.por == 5 and k.base == 1 and k.moldura == 1 and k.vortice == 1 and k.fragmento_1 == 2) then
		table.insert(bad, ("theme %s: %d pieces (base %d moldura %d vortice %d fragmento_1 %d)"):format(TEMA[n], #S.por, k.base, k.moldura, k.vortice, k.fragmento_1)) end
	isPortalSet[S.model] = true
	-- planned Disco centre must hit the layout table before anything is written
	local planned = (TG * CFrame.new(0, 0, S.dz) * S.model:GetAttribute("CF0")).Position
	if (planned - TARGET[n]).Magnitude > 0.05 then table.insert(bad, ("Portal%d planned %s, target %s"):format(n, v3s(planned), v3s(TARGET[n]))) end
end end

-- 3) every other GALERIA member (live, in workspace)
local OTHERS, cnt = {}, {}
for _, root in ipairs({L, SANT}) do for _, d in ipairs(root:GetDescendants()) do
	if d:GetAttribute("HEX_GRUPO") == "GALERIA" and not isPortalSet[d] and not isTarget[d] then
		if d:GetAttribute("CF0") == nil then table.insert(bad, "GALERIA member without CF0: " .. d:GetFullName()) end
		table.insert(OTHERS, d) cnt[d.Name] = (cnt[d.Name] or 0) + 1 end end end
local EXPECT = {["NUC_-146_-45"] = 1, ["PODIO_-146_-45"] = 1, ["ESCADA_X_-104"] = 1, KIT_piso_mod = 136, KIT_bal_seg = 45, KIT_sumeru_seg = 45,
	KIT_sumeru_canto = 4, SANT_galeria = 1, SANT_fundo = 1, KIT_lanterna_palacio = 4, terraco_santuario = 1, sant_N = 1, sant_S = 1, sant_fundo = 1, portal_pilar = 12}
local nExp = 0 for k, v in pairs(EXPECT) do nExp += v if cnt[k] ~= v then table.insert(bad, ("GALERIA %s: %d (expected %d)"):format(k, cnt[k] or 0, v)) end end
for k in pairs(cnt) do if not EXPECT[k] then table.insert(bad, "unexpected GALERIA member name: " .. k) end end
if #OTHERS ~= nExp then table.insert(bad, ("GALERIA others: %d (expected %d)"):format(#OTHERS, nExp)) end

-- 6) banners and library
local BAN = {}
for _, role in ipairs({"GAL_A", "GAL_B"}) do local r = {}
	for _, c in ipairs(Pr:GetChildren()) do if c.Name == "KIT_estandarte" and c:GetAttribute("HEX_ROLE") == role then table.insert(r, c) end end
	if #r ~= 1 or not r[1]:IsA("BasePart") or r[1]:GetAttribute("S0") == nil then table.insert(bad, ("Props.KIT_estandarte %s: %d found (need 1 MeshPart with S0)"):format(role, #r))
	else BAN[role] = r[1] end
end
if not (H.LIB:FindFirstChild("KIT") and H.LIB.KIT:FindFirstChild("KIT_placa")) then table.insert(bad, "BIBLIOTECA_MURIM.KIT.KIT_placa missing") end
local ESC = P:FindFirstChild("ESCADA_X_-104")
if #bad > 0 then error("F3 aborted before writing anything:\n" .. table.concat(bad, "\n")) end

local SIGN = H.selfTest()
local ignis = workspace.NPCs.Ignis
local ib0, is0 = ignis:GetBoundingBox()

------------------------------------------------------------------ writes
local N = {removedNow = 0}
local function build()
	H.clear(HG) H.clearColliders("hx_f3_")
	-- 1) removals
	for _, c in ipairs(toRemove) do if H.remove(c, FASE) then N.removedNow += 1 end end
	-- 2) portal sets: rigid dZ in the original frame, then TG
	N.portalPieces = 0
	for n = 1, 6 do local S = SETS[n] local pre = CFrame.new(0, 0, S.dz)
		H.placeRigid(S.model, TG, pre) N.portalPieces += 1
		for _, c in ipairs(S.por) do H.placeRigid(c, TG, pre) N.portalPieces += 1 end
	end
	-- 3) every other GALERIA member. Palace lanterns: measured fix (see header): +5.5 up so the hook enters the
	-- beam bottom (Y 25.28) by 0.6 instead of floating 4.9 below it; the two at Z +-40 (inside the end columns,
	-- Z 37.19..40.81) move to their bay centres Z +-32.5
	for _, i in ipairs(OTHERS) do
		if i.Name == "KIT_lanterna_palacio" then local z0 = H.cf0(i).Z
			H.placeRigid(i, TG, CFrame.new(0, LANT_DY, (math.abs(z0) > 30) and (-math.sign(z0) * 7.5) or 0))
		else H.placeRigid(i, TG) end
	end
	N.others = #OTHERS
	-- 4) stair 1.5x wider (22.8): size first, then the rigid placement again
	local s0 = H.s0(ESC) ESC.Size = Vector3.new(s0.X, s0.Y, s0.Z * 1.5) H.placeRigid(ESC, TG)
	-- 5) balustrades 3.4 tall, same bottom
	N.bal = 0
	for _, i in ipairs(OTHERS) do if i.Name == "KIT_bal_seg" then H.fixBal(i) N.bal += 1 end end
	-- 6) new parts
	local placa = H.libClone("KIT", "KIT_placa", HG)
	placa.Name = "KIT_placa_galeria" placa.Size = Vector3.new(15.6, 7.5, 2.74)
	placa.CFrame = TG * CFrame.new(SIGN_X, 27, 0) * CFrame.Angles(0, math.pi / 2, 0)
	N.bannerCF = {}
	for _, q in ipairs({{"GAL_A", 48}, {"GAL_B", -48}}) do local b = BAN[q[1]]
		b.Size = H.s0(b) * 1.3
		b.CFrame = TG * CFrame.new(100.0, 14.43, q[2]) * CFrame.Angles(0, math.pi / 2, 0)
		N.bannerCF[q[1]] = b.CFrame end
	for _, q in ipairs({{"LanternaEscadaA", 13.6}, {"LanternaEscadaB", -13.6}}) do
		local m = H.boxLantern(HG, q[1], TG * Vector3.new(86.9, 0, q[2])) m:SetAttribute("HexGen", true) end
	-- 7) colliders
	H.ramp("hx_f3_gal_rampa", Vector3.new(96.3, 3.19, 0), 22.8, 6.38, 15.6, Vector3.new(-1, 0, 0), TG)
	-- the POR_base meshes are round discs (7.2 across, 0.66 thick): a Cylinder collider with the same size
	-- instead of a box, whose corners would stick out 1.5 studs past the disc as an invisible 0.68 step
	for n = 1, 6 do for _, c in ipairs(SETS[n].por) do if c.Name == "POR_base_" .. TEMA[n] then
		local col = H.collider("hx_f3_gal_base_" .. TEMA[n], Vector3.new(c.Size.Y, c.Size.X, c.Size.Z), c.CFrame * CFrame.Angles(0, 0, math.pi / 2))
		col.Shape = Enum.PartType.Cylinder end end end
	H.collider("hx_f3_gal_banner_A", Vector3.new(3.6, 28.85, 3.6), N.bannerCF.GAL_A)
	H.collider("hx_f3_gal_banner_B", Vector3.new(3.6, 28.85, 3.6), N.bannerCF.GAL_B)
	L:SetAttribute("HEX_F3_OK", true)
end

local rec = H.begin("HEX F3 portal gallery")
local ok, err = pcall(build)
if ok then H.commit(rec)
else
	if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Cancel) end
	error("F3 failed after writes began; the recording was CANCELLED (writes reverted): " .. tostring(err))
end

------------------------------------------------------------------ verify (read-only)
local v, allOK = {}, true
local function chk(cond, msg) table.insert(v, (cond and "PASS " or "FAIL ") .. msg) if not cond then allOK = false end return cond end
local function xz(p) return Vector2.new(p.X, p.Z) end

-- Disco centres
local dl, dmax = {}, 0
for n = 1, 6 do local d = SETS[n].disco local e = (d.Position - TARGET[n]).Magnitude dmax = math.max(dmax, e)
	table.insert(dl, ("P%d%s"):format(n, v3s(d.Position))) end
chk(dmax <= 0.05, ("Disco centres within 0.05 of the layout table (max %.3f): %s"):format(dmax, table.concat(dl, " ")))
-- order along (0.5,0,0.866)
local ord = {} for n = 1, 6 do table.insert(ord, {a = SETS[n].disco:GetAttribute("AreaId"), k = SETS[n].disco.Position:Dot(Vector3.new(0.5, 0, 0.866))}) end
table.sort(ord, function(a, b) return a.k < b.k end)
local ordS = {} for _, o in ipairs(ord) do table.insert(ordS, tostring(o.a)) end
chk(table.concat(ordS, ",") == "1,2,3,4,5,6", "order along (0.5,0,0.866), left to right from the plaza: AreaId " .. table.concat(ordS, ","))
-- themes stay with their portal, rigidly
local rig, mol = 0, {}
for n = 1, 6 do local S = SETS[n] local d0 = S.model:GetAttribute("CF0").Position
	for _, c in ipairs(S.por) do local e = math.abs((xz(c.Position) - xz(S.disco.Position)).Magnitude - (xz(c:GetAttribute("CF0").Position) - xz(d0)).Magnitude)
		rig = math.max(rig, e)
		if c.Name:sub(1, 12) == "POR_moldura_" then table.insert(mol, ("%s->P%d %.2f"):format(TEMA[n], n, (xz(c.Position) - xz(S.disco.Position)).Magnitude)) end end end
chk(rig < 0.01, ("each POR piece keeps its XZ distance to its Disco (max error %.4f); moldura: %s"):format(rig, table.concat(mol, ", ")))
-- teleports untouched
local tp = {} for n = 1, 6 do local S = SETS[n]
	table.insert(tp, (S.model.Parent == SANT and S.disco.Parent == S.model and S.disco.Name == "Disco" and S.disco:GetAttribute("AreaId") == n and S.disco.CanTouch) and ("P" .. n .. "ok") or ("P" .. n .. "BAD")) end
chk(not table.concat(tp):find("BAD"), "Portal Models direct children of Santuario, Disco name/AreaId/CanTouch unchanged: " .. table.concat(tp, " "))
-- no roof: no TEL_* part within 25 studs (XZ, AABB) of any Disco; nothing above the gallery beam line except the sign
local near, tmin = {}, math.huge
for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d.Name:sub(1, 4) == "TEL_" then
	local cf, sz = d.CFrame, d.Size
	local hx = (math.abs(cf.RightVector.X) * sz.X + math.abs(cf.UpVector.X) * sz.Y + math.abs(cf.LookVector.X) * sz.Z) / 2
	local hz = (math.abs(cf.RightVector.Z) * sz.X + math.abs(cf.UpVector.Z) * sz.Y + math.abs(cf.LookVector.Z) * sz.Z) / 2
	for n = 1, 6 do local p = SETS[n].disco.Position
		local dx, dz = math.max(0, math.abs(p.X - cf.X) - hx), math.max(0, math.abs(p.Z - cf.Z) - hz)
		local dd = math.sqrt(dx * dx + dz * dz) tmin = math.min(tmin, dd)
		if dd < 25 then table.insert(near, d:GetFullName()) end end end end
chk(#near == 0, ("no TEL_* part within 25 studs (XZ) of any Disco: nearest %.1f"):format(tmin))
local high = {}
for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d.Transparency < 1 and not d:IsDescendantOf(HG) then
	local lp = TG:PointToObjectSpace(d.Position)
	if lp.X > 100 and lp.X < 150 and math.abs(lp.Z) < 47 and d.Position.Y > 33 then table.insert(high, d:GetFullName()) end end end
chk(#high == 0, "nothing visible above Y 33 over the gallery podium (no roof, no ridge ornament)" .. (#high > 0 and (": " .. table.concat(high, ", ", 1, math.min(#high, 5))) or ""))
-- podium corners
local POD = P["PODIO_-146_-45"] local want = {Vector3.new(73.12, 0, -80.84), Vector3.new(118.58, 0, -2.12), Vector3.new(110.28, 0, -102.30), Vector3.new(155.74, 0, -23.58)}
local cmax, cl = 0, {}
for _, sx in ipairs({-1, 1}) do for _, sz in ipairs({-1, 1}) do local w = POD.CFrame:PointToWorldSpace(Vector3.new(sx * POD.Size.X / 2, 0, sz * POD.Size.Z / 2))
	local best = math.huge for _, t in ipairs(want) do best = math.min(best, (xz(w) - xz(t)).Magnitude) end
	cmax = math.max(cmax, best) table.insert(cl, ("(%.2f,%.2f)"):format(w.X, w.Z)) end end
chk(cmax <= 0.3, ("gallery podium corners within 0.3 of the layout (max %.3f): %s"):format(cmax, table.concat(cl, " ")))
-- palace lanterns: hook 0.6 into the beam bottom (25.28), clear of the 7 colonnade columns (measured AABBs)
local COLZ = {{37.19, 40.81}, {24.19, 27.81}, {11.19, 14.81}, {-1.81, 1.81}, {-14.81, -11.19}, {-27.81, -24.19}, {-40.81, -37.19}}
local ll, lOK = {}, true
for _, i in ipairs(OTHERS) do if i.Name == "KIT_lanterna_palacio" then
	local lp = TG:ToObjectSpace(i.CFrame) local top = i.Position.Y + i.Size.Y / 2 local hit = false
	for _, cz in ipairs(COLZ) do if lp.Z + i.Size.Z / 2 > cz[1] and lp.Z - i.Size.Z / 2 < cz[2] and lp.X + i.Size.X / 2 > 108.14 and lp.X - i.Size.X / 2 < 111.86 then hit = true end end
	if hit or math.abs(top - 25.88) > 0.02 then lOK = false end
	table.insert(ll, ("Z%.1f top %.2f%s"):format(lp.Z, top, hit and " IN COLUMN" or "")) end end
chk(lOK and #ll == 4, "gallery palace lanterns hang from the beam, clear of the columns: " .. table.concat(ll, ", "))
-- stair width, balustrades
chk(math.abs(ESC.Size.Z - 22.8) < 0.01, ("ESCADA_X_-104 width %.2f (expected 22.8)"):format(ESC.Size.Z))
local bmax = 0 for _, i in ipairs(OTHERS) do if i.Name == "KIT_bal_seg" then
	local bot0 = i:GetAttribute("CF0").Y - i:GetAttribute("S0").Y / 2 bmax = math.max(bmax, math.abs(i.Size.Y - 3.4), math.abs((i.Position.Y - 1.7) - bot0)) end end
chk(N.bal == 45 and bmax < 0.01, ("%d gallery KIT_bal_seg at 3.4 tall, bottom kept (max error %.4f)"):format(N.bal, bmax))
-- sign and banners face the plaza (front = LookVector for these meshes)
local placa = HG:FindFirstChild("KIT_placa_galeria")
local FRONT = -TG.RightVector -- gallery front normal, toward the plaza
local function facing(p) return p.CFrame.LookVector:Dot(FRONT) end
chk(placa ~= nil and facing(placa) > 0.9, ("sign %s faces the plaza (dot %.3f), size %s"):format(placa and v3s(placa.Position) or "?", placa and facing(placa) or 0, placa and v3s(placa.Size) or "?"))
local bs = {} local bOK = true
for _, r in ipairs({"GAL_A", "GAL_B"}) do local b = BAN[r] local bot = b.Position.Y - b.Size.Y / 2
	table.insert(bs, ("%s %s bottom %.3f facing %.3f"):format(r, v3s(b.Position), bot, facing(b))) if math.abs(bot) > 0.02 or facing(b) < 0.9 then bOK = false end end
chk(bOK, "end banners stand on the paving and face the plaza: " .. table.concat(bs, "; "))

-- walkability (RespectCanCollide) in the gallery frame
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances = {} rp.RespectCanCollide = true
local function hAt(x, z) local w = TG * Vector3.new(x, 0, z) local r = workspace:Raycast(Vector3.new(w.X, 60, w.Z), Vector3.new(0, -100, 0), rp)
	return r and r.Position.Y or nil, r and r.Instance.Name or "MISS" end
local tp2, tOK = {}, true
for _, q in ipairs({{110, 0}, {135, 20}, {135, -20}, {110, 30}, {110, -30}, {140, 0}}) do local h, n = hAt(q[1], q[2])
	table.insert(tp2, ("(%g,%g)%s %.2f"):format(q[1], q[2], n, h or -99)) if not h or math.abs(h - 6.38) > 0.02 then tOK = false end end
chk(tOK, "terrace probes hit 6.38: " .. table.concat(tp2, " "))
local bp, bOK2 = {}, true
for n = 1, 6 do local z = 32.5 - 13 * (n - 1) + SETS[n].dz local h, nm = hAt(118, z)
	table.insert(bp, ("%s %.2f"):format(nm, h or -99)) if not h or math.abs(h - 7.06) > 0.02 then bOK2 = false end
	local hc = hAt(118 - 3.1, z + 3.1) -- 4.4 from the disc centre, i.e. outside the round base: terrace
	if not hc or math.abs(hc - 6.38) > 0.02 then bOK2 = false table.insert(bp, ("corner %.2f"):format(hc or -99)) end end
chk(bOK2, "portal base probes hit 7.06 on the disc and 6.38 just outside it (round collider): " .. table.concat(bp, " "))
local prof, sOK, maxStep = {}, true, 0
for _, z in ipairs({0, -10, 10}) do local prev, row = nil, {}
	for x = 87, 106 do local h = hAt(x, z) if not h then sOK = false h = -99 end
		if prev then maxStep = math.max(maxStep, math.abs(h - prev)) end prev = h
		if z == 0 then table.insert(row, ("%.2f"):format(h)) end end
	local h0, h1 = hAt(87, z), hAt(106, z)
	if not (h0 and h1 and h0 <= 0.3 and math.abs(h1 - 6.38) < 0.02) then sOK = false end
	if z == 0 then table.insert(prof, table.concat(row, " ")) end
end
chk(sOK and maxStep <= 0.5, ("stair ramp 0 -> 6.38, max rise per stud %.2f; axis profile x=87..106: %s"):format(maxStep, prof[1]))
-- dry apron: 25 studs of paving before the stair, full stair width, nothing standing on it
local ap, aOK = {}, true
for x = 63.5, 88, 2.5 do for z = -10, 10, 5 do local h, n = hAt(x, z)
	if not h or h > 0.3 or h < -0.05 then aOK = false table.insert(ap, ("(%g,%g)%s %.2f"):format(x, z, n, h or -99)) end end end
-- manual oriented-extent scan (GetPartBoundsInBox would skip CanQuery=false decorative meshes)
local inBox, keepers = {}, {}
local AX, AZ = TG.RightVector, TG.LookVector
for _, p in ipairs(workspace:GetDescendants()) do if p:IsA("BasePart") and p ~= workspace.Terrain and (p.Transparency < 1 or p.CanCollide) then
	local cf, sz = p.CFrame, p.Size
	local function ext(a) return (math.abs(a:Dot(cf.RightVector)) * sz.X + math.abs(a:Dot(cf.UpVector)) * sz.Y + math.abs(a:Dot(cf.LookVector)) * sz.Z) / 2 end
	local lp = TG:PointToObjectSpace(p.Position) local ex, ey, ez = ext(AX), ext(Vector3.yAxis), ext(AZ)
	if lp.X + ex > 63.2 and lp.X - ex < 88.2 and math.abs(lp.Z) - ez < 11.4 and p.Position.Y + ey > 0.5 and p.Position.Y - ey < 8.5 then
		-- the 8 pond keepers (HEX_Lagos, HEX_ROLE LOTUS_*/ROCK_*) still lie where F1 left them; F6 moves them into the ponds
		if p.Parent == L.HEX_Lagos and p:GetAttribute("HEX_ROLE") then table.insert(keepers, p:GetAttribute("HEX_ROLE") .. v3s(p.Position))
		else table.insert(inBox, p:GetFullName()) end end end end
chk(aOK and #inBox == 0, ("dry apron 25 x 22.8 before the stair: floor hits 0..0.25 %s; parts standing in it: %d %s"):format(
	#ap == 0 and "OK" or table.concat(ap, " "), #inBox, table.concat(inBox, ", ", 1, math.min(#inBox, 4))))
local kst = {}
for _, k in ipairs(L.HEX_Lagos:GetChildren()) do if k:GetAttribute("HEX_ROLE") and k:IsA("BasePart") then
	local lp = TG:PointToObjectSpace(k.Position)
	if lp.X > 60 and lp.X < 150 and math.abs(lp.Z) < 50 then table.insert(kst, ("%s at gallery-local (%.1f,%.1f)"):format(k:GetAttribute("HEX_ROLE"), lp.X, lp.Z)) end end end
table.insert(v, "NOTE pond keepers on the apron/stair until F6 moves them into the ponds: " .. (#kst > 0 and table.concat(kst, "; ") or "none"))
local wet = {}
for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and (d.Name:lower():find("agua") or d.Name:lower():find("lamina")) then
	local lp = TG:PointToObjectSpace(d.Position) if lp.X > 55 and lp.X < 150 and math.abs(lp.Z) < 60 then table.insert(wet, d:GetFullName()) end end end
chk(#wet == 0, "no water part in front of or on the gallery" .. (#wet > 0 and (": " .. table.concat(wet, ", ")) or ""))
-- colliders never over a Disco / prompt
local cols, overD = {}, {}
for _, c in ipairs(COL:GetChildren()) do if c.Name:sub(1, 6) == "hx_f3_" then table.insert(cols, c.Name)
	for n = 1, 6 do local d = SETS[n].disco local o = c.CFrame:PointToObjectSpace(d.Position)
		if math.abs(o.X) < c.Size.X / 2 + 0.3 and math.abs(o.Y) < c.Size.Y / 2 + 3.2 and math.abs(o.Z) < c.Size.Z / 2 + 0.3 then table.insert(overD, c.Name .. "/P" .. n) end end end end
table.sort(cols)
chk(#cols == 9 and #overD == 0, ("hx_f3_ colliders: %d (expected 9: ramp, 6 bases, 2 banners); overlapping a Disco: %d %s"):format(#cols, #overD, table.concat(overD, " ")))
-- removals in storage
local rf = REM:FindFirstChild(FASE) local nR = rf and #rf:GetChildren() or 0
chk(nR == 12, ("%s holds %d items (expected 12: degrau_sant1..8, 2 KIT_bal_seg, 2 KIT_sumeru_seg)"):format(FASE, nR))
-- HEX_Galeria
local hg = {} for _, c in ipairs(HG:GetChildren()) do table.insert(hg, c.Name) end table.sort(hg)
chk(#hg == 3, "HEX_Galeria: " .. table.concat(hg, ", "))
-- things that must keep working
local pad = workspace:FindFirstChild("LojaMochilas") and workspace.LojaMochilas:FindFirstChild("PadLoja")
local pr = workspace:FindFirstChild("MailBox") and workspace.MailBox:FindFirstChildWhichIsA("ProximityPrompt", true)
chk(pad ~= nil and pad.CanTouch and pr ~= nil and pr.Enabled, "PadLoja present (CanTouch) and MailBox ProximityPrompt enabled")
local ib1, is1 = ignis:GetBoundingBox() local bb, bsz = H.SS.BACKUP_LOBBY_PRE_HEX.Ignis:GetBoundingBox()
chk((ib1.Position - ib0.Position).Magnitude < 1e-3 and (ib1.Position - bb.Position).Magnitude < 1e-3 and (is1 - bsz).Magnitude < 1e-3, "NPCs.Ignis unchanged")
local LA = workspace.Corredores.Lobby_Area1 local drift = 0
for _, n in ipairs({"Estrada", "RampaArea1", "RampaPatamar"}) do local c = LA:FindFirstChild(n)
	if not c or (c.Position - c:GetAttribute("CF0").Position).Magnitude > 1e-3 or not c.CanCollide then drift += 1 end end
chk(drift == 0, "exit walk colliders Estrada/RampaArea1/RampaPatamar unchanged")

say(("F3 %s: SIGN %d, removed now %d (already removed %d), portal pieces placed %d (6 Models + 30 POR), other GALERIA members placed %d, balustrades %d")
	:format(allOK and "OK" or "VERIFY FAILED", SIGN, N.removedNow, nAlready, N.portalPieces, N.others, N.bal))
for _, s in ipairs(v) do say("  " .. s) end
say("  colliders: " .. table.concat(cols, ","))
return table.concat(rep, "\n")
