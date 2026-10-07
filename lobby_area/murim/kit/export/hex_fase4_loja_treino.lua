-- hex_fase4_loja_treino.lua : F4 = shop relocation (TS) with a rebuilt hall and a reachable pad; training yard
-- relocation (TT). No accents.
-- Shop: the broken frame goes to LOBBY_REMOVIDOS_HEX/F4_R10; every LOJA member moves rigidly by H.TS (stair +10.4,
-- pad +17.65/-4, MailBox +15.5/+3.5, VIL_placa_loja +30/-2.5); the LOJA TEL_G roof is refitted along the facade;
-- a new 10-column hall with an OPEN 3-bay front is built in HEX_Loja; a forecourt block carries the pad at the
-- stair head; 2 end banners, 2 stair-foot box lanterns, colliders hx_f4_loja_*.
-- Training: every TREINO member moves by H.TT onto a raised wood deck with a red railing (entrance facing the
-- plaza), 4 red lanterns on the corner posts, 2 banners, colliders hx_f4_treino_*.
-- Idempotent: clears HEX_Loja / HEX_Treino / hx_f4_*, every placement is computed from CF0/S0, removals are counted
-- live + already-removed. On any error after writes began, the ChangeHistory recording is CANCELLED.
-- Deviations from the spec text (all measured, see the report):
-- * new kit pieces are clones of the LIVE lobby pieces (the removed shop frame, the shop piso/sumeru/balustrades,
--   a VIA red lantern), not H.libClone: the BIBLIOTECA_MURIM atlases are the old grey bake (non-black mean colour
--   (125..159) blue-grey, saturation 0.22..0.26, against the live (70..104) warm, saturation 0.40..0.47);
-- * roof scale (0.734, 0.9, 1.191) with the eave bottom at 22.8 instead of (0.674, 0.9, 0.975) at 23.9: measured on
--   the TEL_G triangles, the spec scale leaves only 0.64 of eave past the front/back column faces (1.94 at the sides);
--   this one gives 3.54 on all four sides and rests the roof on the front/back brackets (gate reference: 2.6 gaps);
-- * forecourt tiles start at u 13.96 (the face of the terrace sumeru moulding) instead of 13.45, because the front
--   sumeru tops (7.98) would otherwise lie coplanar under the first tile row; the old stair gap in that moulding
--   (v -4.6..5.0) is closed with 2 sumeru clones, so the threshold is one continuous moulding band;
-- * forecourt block in podium stone (160,138,112) Limestone with the same sumeru band on its 3 outer faces: the
--   cremeS SmoothPlastic block of the spec read as a bare white box in the V7 capture;
-- * forecourt balustrades inset like the kit (outer face 0.14 inside the edge: sides v +-12.2, front u 23.05) and
--   butted instead of crossed at the corners (no coplanar rail caps); the spec put them half off the block edge;
-- * shop KIT_placa 6.9 x 3.32 (uniform scale 1.327) instead of 8.3 x 4.0, which would cut 0.7 into both front columns;
-- * hall wall panels at Y 12.93 (bottom on the floor 7.98) instead of 13.0 (a 0.07 slit under every wall);
-- * training front posts at z +-15.4 / +-10.2 / +-5.4 so the visible railing ends where its colliders end and the
--   entrance is exactly z -5..5 (the spec's posts at +-9.0 left 3.6 of invisible collider past the last post);
--   training banners at x -117.5 instead of -117 (at -117 their bounding box cut 0.2 into the front rail).
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, REM, COL = H.L, H.REM, H.COL
local CHS = game:GetService("ChangeHistoryService")
local CS = game:GetService("CollectionService")
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end
local function v3s(v) return ("(%.2f,%.2f,%.2f)"):format(v.X, v.Y, v.Z) end
for _, k in ipairs({"HEX_F0_OK", "HEX_F1_OK", "HEX_F2_OK", "HEX_F3_OK"}) do
	assert(L:GetAttribute(k) == true, "F4: marker " .. k .. " missing (run the earlier phases first)") end

local P, Pr, Fo, OE = L.Patio, L.Props, L.Forja, L.Oeste
local HL, HT = L:FindFirstChild("HEX_Loja"), L:FindFirstChild("HEX_Treino")
local TS, TT, C = H.TS, H.TT, H.C
local FASE = "F4_R10"
local B3 = 29 / 3 -- front/back bay (9.667)
local HALF_PI = math.pi / 2
local function SF(u, y, v, yaw) return TS * H.shopOrig(u, y, v) * CFrame.Angles(0, yaw or 0, 0) end
local SHOPF = TS * H.shopOrig(0, 0, 0) -- shop frame (u = local X toward the plaza, v = local Z along the facade)
local UW = SHOPF.RightVector
local ROOF_SX, ROOF_SY, ROOF_SZ, ROOF_Y = 0.734, 0.9, 1.191, 22.8
local WALL_Y = 12.93
local PAD_TARGET = Vector3.new(-105.20, 8.25, -46.88)
local COLS = {{10.5, 14.5}, {10.5, B3 / 2}, {10.5, -B3 / 2}, {10.5, -14.5}, {-11.5, 14.5}, {-11.5, B3 / 2}, {-11.5, -B3 / 2}, {-11.5, -14.5}, {-0.5, 14.5}, {-0.5, -14.5}}

------------------------------------------------------------------ read-only gather + asserts
local bad = {}
if not (HL and HT) then error("F4 aborted before writing anything: HEX_Loja / HEX_Treino missing (F0 creates them)") end
for _, f in ipairs({HL, HT}) do for _, c in ipairs(f:GetChildren()) do
	if not c:GetAttribute("HexGen") then table.insert(bad, f.Name .. " holds a non-generated instance: " .. c:GetFullName()) end end end
local remF = REM:FindFirstChild(FASE)
local function posOf(i) local cf = i:GetAttribute("CF0") if cf then return cf.Position end return i:IsA("Model") and i:GetPivot().Position or i.Position end
local function inShopBox(p) return p.X >= -146 and p.X <= -88 and p.Z >= -30 and p.Z <= 20 and p.Y > 8 end
local toRemove, isTarget, nAlready, TPL = {}, {}, 0, {}
local function remMatches(parent, name, pred)
	local r = {}
	if remF then for _, c in ipairs(remF:GetChildren()) do
		if c.Name == name and c:GetAttribute("OrigemPath") == parent:GetFullName() and (pred == nil or pred(c)) then table.insert(r, c) end end end
	return r end
-- 1a) shop frame pieces, by CF0 inside X[-146,-88], Z[-30,20], Y>8
local FRAME = {KIT_coluna = 6, KIT_col_base = 6, KIT_arquitrave = 4, KIT_prancha = 4, KIT_dougong_intermediario = 10,
	KIT_vao_parede = 3, KIT_vao_janela = 2, KIT_vao_porta = 1}
for name, n in pairs(FRAME) do
	local live = {}
	for _, c in ipairs(P:GetChildren()) do if c.Name == name and inShopBox(posOf(c)) then table.insert(live, c) end end
	local done = remMatches(P, name, function(c) local cf = c:GetAttribute("CF0") return cf ~= nil and inShopBox(cf.Position) end)
	if #live + #done ~= n then table.insert(bad, ("Patio.%s in the shop box: live %d + removed %d ~= %d"):format(name, #live, #done, n)) end
	local mesh = nil
	for _, c in ipairs(live) do
		if c:GetAttribute("HEX_GRUPO") ~= nil or not c:IsA("MeshPart") then table.insert(bad, "unexpected shop frame piece " .. c:GetFullName()) end
		table.insert(toRemove, c) isTarget[c] = true end
	for _, c in ipairs(live) do mesh = mesh or c.MeshId if c.MeshId ~= mesh then table.insert(bad, name .. ": mixed MeshIds in the shop frame") end end
	for _, c in ipairs(done) do mesh = mesh or c.MeshId if c.MeshId ~= mesh then table.insert(bad, name .. ": mixed MeshIds in the shop frame") end end
	nAlready += #done
	TPL[name] = live[1] or done[1]
end
-- 1b) old shop colliders
local CN = {"loja_N", "loja_fundo"} for i = 1, 10 do table.insert(CN, "degrau_loja" .. i) end
for _, name in ipairs(CN) do
	local live = {} for _, c in ipairs(COL:GetChildren()) do if c.Name == name then table.insert(live, c) end end
	local done = remMatches(COL, name)
	if #live + #done ~= 1 then table.insert(bad, ("Colisao.%s: live %d + removed %d ~= 1"):format(name, #live, #done)) end
	for _, c in ipairs(live) do local p = posOf(c)
		if p.X < -131 or p.X > -86 or math.abs(p.Z + 4) > 19 then table.insert(bad, "Colisao." .. name .. " at unexpected " .. v3s(p)) end
		table.insert(toRemove, c) isTarget[c] = true end
	nAlready += #done
end
-- 1c) the two terrace-front balustrades the forecourt replaces
for _, pos in ipairs({Vector3.new(-104.80, 10.40, 7.56), Vector3.new(-104.80, 10.40, -14.39)}) do
	local live = H.findAll({P}, "KIT_bal_seg", pos, 0.3)
	local done = remMatches(P, "KIT_bal_seg", function(c) local cf = c:GetAttribute("CF0") return cf ~= nil and (cf.Position - pos).Magnitude <= 0.3 end)
	if #live + #done ~= 1 then table.insert(bad, ("Patio.KIT_bal_seg @%s: live %d + removed %d ~= 1"):format(v3s(pos), #live, #done)) end
	for _, c in ipairs(live) do if c:GetAttribute("HEX_GRUPO") ~= "LOJA" then table.insert(bad, "KIT_bal_seg @" .. v3s(pos) .. " not tagged LOJA") end
		table.insert(toRemove, c) isTarget[c] = true end
	nAlready += #done
	TPL.KIT_bal_seg = TPL.KIT_bal_seg or live[1] or done[1]
end

-- 2) LOJA members (live), minus the two balustrade targets
local LOJA, cnt = {}, {}
local function takeLoja(d)
	if d:GetAttribute("HEX_GRUPO") == "LOJA" and not isTarget[d] then
		local key = (d.Name:sub(1, 6) == "TEL_G_") and "TEL_G" or d.Name
		table.insert(LOJA, d) cnt[key] = (cnt[key] or 0) + 1
		if d:GetAttribute("CF0") == nil or (d:IsA("BasePart") and d:GetAttribute("S0") == nil) then table.insert(bad, "LOJA member without CF0/S0: " .. d:GetFullName()) end
	end end
for _, d in ipairs(L:GetDescendants()) do takeLoja(d) end
local LM, MB = workspace:FindFirstChild("LojaMochilas"), workspace:FindFirstChild("MailBox")
if not (LM and MB) then error("F4 aborted before writing anything: workspace.LojaMochilas / workspace.MailBox missing") end
for _, d in ipairs(LM:GetDescendants()) do takeLoja(d) end
takeLoja(MB)
local EXPECT = {["NUC_104_-24"] = 1, ["PODIO_104_-24"] = 1, ESCADA_X_104 = 1, LOJA_interior = 1, KIT_piso_mod = 40, KIT_bal_seg = 19,
	KIT_sumeru_seg = 24, KIT_sumeru_canto = 4, TEL_G = 17, terraco_loja = 1, PadLoja = 1, MailBox = 1, VIL_placa_loja = 1, KIT_placa = 1}
local nExp = 0
for k, v in pairs(EXPECT) do nExp += v if cnt[k] ~= v then table.insert(bad, ("LOJA %s: %d (expected %d)"):format(k, cnt[k] or 0, v)) end end
for k in pairs(cnt) do if not EXPECT[k] then table.insert(bad, "unexpected LOJA member name: " .. k) end end
if #LOJA ~= nExp then table.insert(bad, ("LOJA members: %d (expected %d)"):format(#LOJA, nExp)) end
local PAD, MAILP = nil, nil
for _, i in ipairs(LOJA) do
	if i.Name == "PadLoja" then PAD = i end
	if i.Name:sub(1, 6) == "TEL_G_" then local cf = i:GetAttribute("CF0")
		if cf and (math.abs(cf.RightVector.Y) > 0.02 or cf.UpVector.Y < 0.999) then table.insert(bad, "LOJA TEL_G piece is not yaw-only: " .. i.Name) end end
	if i.Name == "KIT_piso_mod" and not TPL.KIT_piso_mod then TPL.KIT_piso_mod = i end
	if i.Name == "KIT_sumeru_seg" then local p = i:GetAttribute("CF0").Position
		if (p - Vector3.new(-103.52, 5.99, -11.30)).Magnitude < 0.05 then TPL.KIT_sumeru_seg = i end end
end
if not (PAD and PAD.Parent == LM) then table.insert(bad, "LojaMochilas.PadLoja missing") end
MAILP = MB:FindFirstChildWhichIsA("ProximityPrompt", true)
if not MAILP then table.insert(bad, "MailBox ProximityPrompt missing") end
-- the terrace-front sumeru gap the fillers close must be empty, and the two neighbours must end at v -4.6 and 5.0
if not TPL.KIT_sumeru_seg then table.insert(bad, "front KIT_sumeru_seg @(-103.52,5.99,-11.30) (u 13.48, v -7.3) missing") end
local frontS = 0
for _, i in ipairs(LOJA) do if i.Name == "KIT_sumeru_seg" then local cf, s0 = i:GetAttribute("CF0"), i:GetAttribute("S0")
	if math.abs(cf.X + 103.52) < 0.05 then local v, hl = cf.Z + 4, s0.X / 2
		if v + hl > -4.6 + 0.02 and v - hl < 5.0 - 0.02 then table.insert(bad, ("front sumeru overlaps the gap v -4.6..5.0: v %.2f"):format(v)) end
		if math.abs(v + 7.3) < 0.05 or math.abs(v - 7.7) < 0.05 then frontS += 1 end end end end
if frontS ~= 2 then table.insert(bad, ("front sumeru neighbours of the gap: %d (expected 2)"):format(frontS)) end
if TPL.KIT_piso_mod then local _, ry = TPL.KIT_piso_mod:GetAttribute("CF0"):ToEulerAnglesYXZ()
	if math.abs(math.sin(ry)) > 0.02 then table.insert(bad, "live KIT_piso_mod template is not yaw 0/180") end end
-- planned pad centre must hit the layout table before anything is written
if PAD then local planned = (TS * CFrame.new(17.65, 0, -4) * PAD:GetAttribute("CF0")).Position
	if (planned - PAD_TARGET).Magnitude > 0.05 then table.insert(bad, "PadLoja planned " .. v3s(planned) .. ", target " .. v3s(PAD_TARGET)) end end

-- 3) TREINO members
local TREINO, tc = {}, {}
for _, c in ipairs(OE:GetChildren()) do if c:GetAttribute("HEX_GRUPO") == "TREINO" then
	table.insert(TREINO, c) tc[c.Name] = (tc[c.Name] or 0) + 1
	if c:GetAttribute("CF0") == nil then table.insert(bad, "TREINO member without CF0: " .. c.Name) end end end
for k, v in pairs({LOB_poste_treino = 9, LOB_boneco_treino = 2, LOB_estante_armas = 1, TREINO_areia = 1}) do
	if tc[k] ~= v then table.insert(bad, ("TREINO %s: %d (expected %d)"):format(k, tc[k] or 0, v)) end end
if #TREINO ~= 13 then table.insert(bad, ("TREINO members: %d (expected 13)"):format(#TREINO)) end

-- 4) banners (stay in Props), red lantern template
local BAN = {}
for _, role in ipairs({"LOJA_A", "LOJA_B", "TREINO_A", "TREINO_B"}) do local r = {}
	for _, c in ipairs(Pr:GetChildren()) do if c.Name == "KIT_estandarte" and c:GetAttribute("HEX_ROLE") == role then table.insert(r, c) end end
	if #r ~= 1 or not r[1]:IsA("BasePart") or r[1]:GetAttribute("S0") == nil then table.insert(bad, ("Props.KIT_estandarte %s: %d found (need 1 with S0)"):format(role, #r))
	else BAN[role] = r[1] end
end
local lv = H.findAll({Pr}, "KIT_lanterna_vermelha", Vector3.new(21, 5.04, 72), 0.3)
if #lv ~= 1 or lv[1]:GetAttribute("S0") == nil then table.insert(bad, "Props.KIT_lanterna_vermelha @(21,5.04,72) template missing") else TPL.KIT_lanterna_vermelha = lv[1] end
-- templates: present, archivable, only a SurfaceAppearance inside
for _, n in ipairs({"KIT_coluna", "KIT_col_base", "KIT_arquitrave", "KIT_prancha", "KIT_dougong_intermediario", "KIT_vao_parede",
	"KIT_piso_mod", "KIT_sumeru_seg", "KIT_bal_seg", "KIT_lanterna_vermelha"}) do local t = TPL[n]
	if not t then table.insert(bad, "no live template for " .. n)
	else
		if not t.Archivable then table.insert(bad, "template not Archivable: " .. t:GetFullName()) end
		for _, d in ipairs(t:GetDescendants()) do if not d:IsA("SurfaceAppearance") then table.insert(bad, "template " .. n .. " has a " .. d.ClassName .. " inside") end end
	end end
if #bad > 0 then error("F4 aborted before writing anything:\n" .. table.concat(bad, "\n")) end

local SIGN = H.selfTest()
local ignis = workspace.NPCs.Ignis
local ib0 = ignis:GetBoundingBox()

------------------------------------------------------------------ writes
local function liveClone(src, parent)
	local c = src:Clone()
	for k in pairs(c:GetAttributes()) do c:SetAttribute(k, nil) end
	for _, t in ipairs(CS:GetTags(c)) do CS:RemoveTag(c, t) end
	c.Anchored = true c.CanCollide = false c.CanTouch = false c.CanQuery = false
	c:SetAttribute("HexGen", true) c.Parent = parent return c end
local N = {removedNow = 0}
local colCF, bannerCF = {}, {}
local function build()
	H.clear(HL) H.clear(HT) H.clearColliders("hx_f4_")
	-- 1) removals
	for _, c in ipairs(toRemove) do if H.remove(c, FASE) then N.removedNow += 1 end end
	-- 2) rigid placements + 3) roof
	N.rigid, N.roof = 0, 0
	for _, i in ipairs(LOJA) do local nm = i.Name
		if nm:sub(1, 6) == "TEL_G_" then
			local cf0, s0 = H.cf0(i), H.s0(i)
			local o = cf0.Position - Vector3.new(-117, 0, -4)
			local _, yaw = cf0:ToEulerAnglesYXZ()
			i.Size = s0 * Vector3.new(ROOF_SX, ROOF_SY, ROOF_SZ)
			i.CFrame = TS * CFrame.new(-117.5, 0, -4) * CFrame.Angles(0, HALF_PI, 0)
				* CFrame.new(o.X * ROOF_SX, (cf0.Y - 21.8) * ROOF_SY + ROOF_Y, o.Z * ROOF_SZ) * CFrame.Angles(0, yaw, 0)
			N.roof += 1
		elseif nm == "KIT_placa" then
			H.remember(i) i.Size = Vector3.new(6.9, 3.32, 2.74) i.CFrame = SF(12.0, 17.6, 0, -HALF_PI) N.rigid += 1
		elseif nm == "ESCADA_X_104" then H.placeRigid(i, TS, CFrame.new(10.4, 0, 0)) N.rigid += 1
		elseif nm == "PadLoja" then H.placeRigid(i, TS, CFrame.new(17.65, 0, -4)) N.rigid += 1
		elseif nm == "MailBox" then H.placeRigid(i, TS, CFrame.new(15.5, 0, 3.5)) N.rigid += 1
		elseif nm == "VIL_placa_loja" then H.placeRigid(i, TS, CFrame.new(30, 0, -2.5)) N.rigid += 1
		else H.placeRigid(i, TS) N.rigid += 1 end
	end
	-- 8) balustrades 3.4 tall, same bottom (after the rigid move)
	N.bal = 0
	for _, i in ipairs(LOJA) do if i.Name == "KIT_bal_seg" then H.fixBal(i) N.bal += 1 end end
	-- 4) new hall: 10 columns, open 3-bay front
	local function kit(name, size, u, y, v, yaw) local c = liveClone(TPL[name], HL) c.Size = size c.CFrame = SF(u, y, v, yaw) return c end
	for k, q in ipairs(COLS) do
		colCF[k] = kit("KIT_coluna", Vector3.new(2.72, 10.1, 2.72), q[1], 14.4, q[2], 0).CFrame
		kit("KIT_col_base", Vector3.new(3.9, 1.5, 3.9), q[1], 8.7, q[2], 0)
		kit("KIT_dougong_intermediario", Vector3.new(4.9, 3.9, 3.8), q[1], 21.9, q[2], (q[1] == -0.5) and 0 or HALF_PI)
	end
	for _, u in ipairs({10.5, -11.5}) do for _, v in ipairs({-B3, 0, B3}) do
		kit("KIT_arquitrave", Vector3.new(B3, 3.6, 1.7), u, 17.6, v, HALF_PI)
		kit("KIT_prancha", Vector3.new(B3, 0.5, 2.5), u, 19.7, v, HALF_PI)
	end end
	-- side beams and walls stop at the inner face of the front/back beams and back wall (butted, not crossed:
	-- crossing pieces would leave coplanar tops at the corners)
	for _, v in ipairs({14.5, -14.5}) do
		kit("KIT_arquitrave", Vector3.new(10.15, 3.6, 1.7), -5.575, 17.6, v, 0)
		kit("KIT_arquitrave", Vector3.new(10.15, 3.6, 1.7), 4.575, 17.6, v, 0)
		kit("KIT_prancha", Vector3.new(9.75, 0.5, 2.5), -5.375, 19.7, v, 0)
		kit("KIT_prancha", Vector3.new(9.75, 0.5, 2.5), 4.375, 19.7, v, 0)
		kit("KIT_vao_parede", Vector3.new(10.05, 9.9, 1.9), -5.525, WALL_Y, v, 0)
		kit("KIT_vao_parede", Vector3.new(11, 9.9, 1.9), 5, WALL_Y, v, 0)
	end
	for _, v in ipairs({-B3, 0, B3}) do kit("KIT_vao_parede", Vector3.new(B3, 9.9, 1.9), -11.5, WALL_Y, v, HALF_PI) end
	-- 5) forecourt: stone block, 2x5 tiles from the moulding face (u 13.96) to the edge (23.85), moulding filler, balustrades
	-- block colour sampled from the PODIO atlas (dominant non-black (132,108,84)/(156,132,108)); a cremeS SmoothPlastic
	-- block rendered as a bare white box beside the textured podium (V7 capture)
	H.part({Name = "PatioLoja_bloco", Size = Vector3.new(10.4, 7.45, 26), CFrame = SF(18.65, 3.725, 0), Color = Color3.fromRGB(160, 138, 112),
		Material = Enum.Material.Limestone, CastShadow = true}, HL)
	-- the terrace edge treatment continued round the forecourt: sumeru moulding band (Y 4.0..7.98) on both sides and
	-- beside the stair, butted at the corners (side runs to u 24.81, front runs v 7.6..13.0 at the seg's native 5.4)
	for _, sg in ipairs({-1, 1}) do
		for _, u in ipairs({16.6725, 22.0975}) do
			local m = liveClone(TPL.KIT_sumeru_seg, HL) m.Size = Vector3.new(5.425, 3.98, 0.96) m.CFrame = SF(u, 5.99, sg * 13.48, sg < 0 and 0 or math.pi) end
		local m = liveClone(TPL.KIT_sumeru_seg, HL) m.Size = Vector3.new(5.4, 3.98, 0.96) m.CFrame = SF(24.33, 5.99, sg * 10.3, -HALF_PI)
	end
	for _, u in ipairs({16.4325, 21.3775}) do for _, v in ipairs({-10.4, -5.2, 0, 5.2, 10.4}) do
		local t = liveClone(TPL.KIT_piso_mod, HL) t.Size = Vector3.new(4.945, 0.5, 5.2) t.CFrame = SF(u, 7.73, v, 0) end end
	local sRot = TPL.KIT_sumeru_seg:GetAttribute("CF0").Rotation
	for _, v in ipairs({-2.2, 2.6}) do
		local s = liveClone(TPL.KIT_sumeru_seg, HL) s.Size = Vector3.new(4.8, 3.98, 0.96)
		s.CFrame = TS * CFrame.new(-117 + 13.48, 5.99, -4 + v) * sRot end
	for _, sg in ipairs({-1, 1}) do
		for _, u in ipairs({15.685, 20.155}) do
			local b = liveClone(TPL.KIT_bal_seg, HL) b.Size = Vector3.new(4.47, 3.4, 1.32) b.CFrame = SF(u, 9.68, sg * 12.2, sg < 0 and 0 or math.pi) end
		local b = liveClone(TPL.KIT_bal_seg, HL) b.Size = Vector3.new(5.16, 3.4, 1.32) b.CFrame = SF(23.05, 9.68, sg * 10.28, -HALF_PI)
	end
	-- 6) end banners (stay in Props)
	for _, q in ipairs({{"LOJA_A", -22}, {"LOJA_B", 22}}) do local b = BAN[q[1]]
		b.Size = H.s0(b) b.CFrame = SF(16, 11.1, q[2], -HALF_PI) bannerCF[q[1]] = b.CFrame end
	-- 7) stair-foot lanterns
	for _, q in ipairs({{"LanternaEscadaA", -13.4}, {"LanternaEscadaB", 5.4}}) do
		H.boxLantern(HL, q[1], TS * Vector3.new(-73.8, 0, q[2])):SetAttribute("HexGen", true) end
	-- 9) shop colliders
	H.ramp("hx_f4_loja_rampa", Vector3.new(-84.2, 3.99, -4), 15.2, 7.98, 19.0, Vector3.new(1, 0, 0), TS)
	H.collider("hx_f4_loja_patamar", Vector3.new(10.95, 7.98, 26), SF(18.375, 3.99, 0))
	H.collider("hx_f4_loja_fundo", Vector3.new(1.9, 12, 30), SF(-11.5, 13.98, 0))
	H.collider("hx_f4_loja_lado_N", Vector3.new(22, 12, 1.9), SF(-0.5, 13.98, 14.5))
	H.collider("hx_f4_loja_lado_S", Vector3.new(22, 12, 1.9), SF(-0.5, 13.98, -14.5))
	for k, cf in ipairs(colCF) do H.collider("hx_f4_loja_col_" .. k, Vector3.new(2.72, 10.1, 2.72), cf) end
	H.collider("hx_f4_loja_banner_A", Vector3.new(2.8, 22.2, 2.8), bannerCF.LOJA_A)
	H.collider("hx_f4_loja_banner_B", Vector3.new(2.8, 22.2, 2.8), bannerCF.LOJA_B)

	-- TRAINING
	for _, i in ipairs(TREINO) do H.placeRigid(i, TT) end
	H.part({Name = "Deck", Size = Vector3.new(40, 1.2, 32), CFrame = CFrame.new(-135, 0.4, 0), Color = C.treino,
		Material = Enum.Material.WoodPlanks, CanCollide = true, CastShadow = true}, HT)
	local POSTS = {}
	for k = 0, 6 do local x = -154.4 + k * 38.8 / 6 table.insert(POSTS, {x, 15.4}) table.insert(POSTS, {x, -15.4}) end
	for _, z in ipairs({-7.7, 0, 7.7}) do table.insert(POSTS, {-154.4, z}) end
	for _, z in ipairs({-10.2, -5.4, 5.4, 10.2}) do table.insert(POSTS, {-115.6, z}) end
	for _, q in ipairs(POSTS) do
		H.part({Name = "Poste", Size = Vector3.new(0.8, 3.2, 0.8), CFrame = CFrame.new(q[1], 2.6, q[2]), Color = C.grade, CastShadow = true}, HT)
		H.part({Name = "Tampa", Size = Vector3.new(1.0, 0.35, 1.0), CFrame = CFrame.new(q[1], 4.375, q[2]), Color = C.ouro, Material = Enum.Material.Metal}, HT)
	end
	N.posts = #POSTS
	local RUNS = {{-154.4, 15.4, -115.6, 15.4}, {-154.4, -15.4, -115.6, -15.4}, {-154.4, -15.4, -154.4, 15.4}, {-115.6, 5.4, -115.6, 15.4}, {-115.6, -15.4, -115.6, -5.4}}
	for _, r in ipairs(RUNS) do for _, y in ipairs({2.4, 3.9}) do
		local a, b = Vector3.new(r[1], y, r[2]), Vector3.new(r[3], y, r[4])
		H.part({Name = "Corrimao", Size = Vector3.new(0.45, 0.45, (b - a).Magnitude), CFrame = CFrame.lookAt((a + b) / 2, b), Color = C.grade}, HT)
	end end
	local ls = TPL.KIT_lanterna_vermelha:GetAttribute("S0") * 0.6
	for _, q in ipairs({{-154.4, 15.4}, {-154.4, -15.4}, {-115.6, 15.4}, {-115.6, -15.4}}) do
		local l = liveClone(TPL.KIT_lanterna_vermelha, HT) l.Size = ls
		l.CFrame = CFrame.new(q[1], 4.55 + ls.Y / 2, q[2]) * CFrame.Angles(0, -HALF_PI, 0) end
	for _, q in ipairs({{"TREINO_A", -12.5}, {"TREINO_B", 12.5}}) do local b = BAN[q[1]]
		b.Size = H.s0(b) b.CFrame = CFrame.new(-117.5, 12.1, q[2]) * CFrame.Angles(0, -HALF_PI, 0) end
	H.collider("hx_f4_treino_rail_N", Vector3.new(40, 4, 0.6), CFrame.new(-135, 3, 15.4))
	H.collider("hx_f4_treino_rail_S", Vector3.new(40, 4, 0.6), CFrame.new(-135, 3, -15.4))
	H.collider("hx_f4_treino_rail_back", Vector3.new(0.6, 4, 31), CFrame.new(-154.4, 3, 0))
	H.collider("hx_f4_treino_rail_front1", Vector3.new(0.6, 4, 10.4), CFrame.new(-115.6, 3, 10.2))
	H.collider("hx_f4_treino_rail_front2", Vector3.new(0.6, 4, 10.4), CFrame.new(-115.6, 3, -10.2))
	L:SetAttribute("HEX_F4_OK", true)
end

local rec = H.begin("HEX F4 shop + training")
local ok, err = pcall(build)
if ok then H.commit(rec)
else
	if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Cancel) end
	error("F4 failed after writes began; the recording was CANCELLED (writes reverted): " .. tostring(err))
end

------------------------------------------------------------------ verify (read-only)
local v, allOK = {}, true
local function chk(cond, msg) table.insert(v, (cond and "PASS " or "FAIL ") .. msg) if not cond then allOK = false end return cond end
local function toShop(p) return SHOPF:PointToObjectSpace(p) end
-- extents of a part's box along the shop axes (or world axes when frame is nil)
local function boxIn(frame, p)
	local cf, sz = p.CFrame, p.Size
	local rc = frame and frame:ToObjectSpace(cf) or cf
	local ex = (math.abs(rc.RightVector.X) * sz.X + math.abs(rc.UpVector.X) * sz.Y + math.abs(rc.LookVector.X) * sz.Z) / 2
	local ey = (math.abs(rc.RightVector.Y) * sz.X + math.abs(rc.UpVector.Y) * sz.Y + math.abs(rc.LookVector.Y) * sz.Z) / 2
	local ez = (math.abs(rc.RightVector.Z) * sz.X + math.abs(rc.UpVector.Z) * sz.Y + math.abs(rc.LookVector.Z) * sz.Z) / 2
	local c = rc.Position
	return c - Vector3.new(ex, ey, ez), c + Vector3.new(ex, ey, ez) end
local function overlap(a0, a1, b0, b1) return a0.X < b1.X and a1.X > b0.X and a0.Y < b1.Y and a1.Y > b0.Y and a0.Z < b1.Z and a1.Z > b0.Z end

-- pad
local padE = (PAD.Position - PAD_TARGET).Magnitude
chk(padE <= 0.05 and PAD.Parent == LM and PAD.Name == "PadLoja" and PAD.CanTouch and not PAD.CanCollide and (PAD.Size - Vector3.new(9, 0.4, 9)).Magnitude < 0.01,
	("PadLoja at %s (error %.3f), parent LojaMochilas, Size 9x0.4x9, CanTouch true, CanCollide false"):format(v3s(PAD.Position), padE))
local op = OverlapParams.new() op.RespectCanCollide = true
local inPad = {}
for _, p in ipairs(workspace:GetPartBoundsInBox(PAD.CFrame, PAD.Size - Vector3.new(0.05, 0.05, 0.05), op)) do if p ~= PAD then table.insert(inPad, p:GetFullName()) end end
local pad0, pad1 = boxIn(PAD.CFrame, PAD) pad0 += Vector3.new(0.025, 0.025, 0.025) pad1 -= Vector3.new(0.025, 0.025, 0.025)
local meshIn = {}
for _, p in ipairs(workspace:GetDescendants()) do if p:IsA("BasePart") and p ~= PAD and (p.Position - PAD.Position).Magnitude < 40 then
	local a0, a1 = boxIn(PAD.CFrame, p) if overlap(a0, a1, pad0, pad1) then table.insert(meshIn, p:GetFullName()) end end end
chk(#inPad == 0 and #meshIn == 0, ("nothing overlaps the pad box: collidable %d %s; any part (boxes, incl. meshes) %d %s"):format(
	#inPad, table.concat(inPad, ", "), #meshIn, table.concat(meshIn, ", ", 1, math.min(#meshIn, 5))))
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances = {} rp.RespectCanCollide = true
local function hitW(x, z) local r = workspace:Raycast(Vector3.new(x, 80, z), Vector3.new(0, -120, 0), rp) return r and r.Position.Y or nil, r and r.Instance.Name or "MISS" end
local function hitS(u, vv) local w = SHOPF * Vector3.new(u, 0, vv) return hitW(w.X, w.Z) end
local pb, pOK = {}, true
for u = 14.15, 23.16, 1 do for vv = -4.5, 4.51, 1 do local h, n = hitS(u, vv)
	if not h or math.abs(h - 7.98) > 0.02 or n ~= "hx_f4_loja_patamar" then pOK = false table.insert(pb, ("(%.1f,%.1f)%s %.2f"):format(u, vv, n, h or -99)) end end end
chk(pOK, "rays over the whole pad footprint land on hx_f4_loja_patamar at 7.98" .. (#pb > 0 and (": " .. table.concat(pb, " ", 1, math.min(#pb, 6))) or ""))
-- walk profile plaza -> stair -> forecourt
local prof, sOK, maxStep = {}, true, 0
for _, vv in ipairs({0, -6, 6}) do local prev = nil
	for u = 52, 12, -0.5 do local h = hitS(u, vv) if not h then sOK = false h = -99 end
		if prev then maxStep = math.max(maxStep, math.abs(h - prev)) end prev = h
		if vv == 0 and (u % 4 == 0) then table.insert(prof, ("u%d:%.2f"):format(u, h)) end end
	local h0, h1 = hitS(52, vv), hitS(15, vv)
	if not (h0 and h1 and h0 <= 0.3 and math.abs(h1 - 7.98) < 0.02) then sOK = false end
end
chk(sOK and maxStep <= 0.5, ("smooth rise plaza 0 -> forecourt 7.98 on v 0/-6/+6, max change per 0.5 stud %.2f; axis: %s"):format(maxStep, table.concat(prof, " ")))
-- MailBox
local caixa = MB:FindFirstChild("Caixa")
local dMail = caixa and (caixa.Position - (PAD.Position + Vector3.new(0, 3, 0))).Magnitude or 99
chk(caixa ~= nil and MAILP.Parent == caixa and MAILP.Enabled and dMail <= MAILP.MaxActivationDistance - 0.5,
	("MailBox Caixa at %s (shop u %.2f v %.2f), prompt Enabled, %.1f from the pad centre at chest height (range %g)"):format(
		caixa and v3s(caixa.Position) or "?", caixa and toShop(caixa.Position).X or 0, caixa and toShop(caixa.Position).Z or 0, dMail, MAILP.MaxActivationDistance))
-- hall: open front bays, walk-in rays
local HALL = {} for _, c in ipairs(HL:GetChildren()) do if c:IsA("BasePart") then HALL[c.Name] = (HALL[c.Name] or 0) + 1 end end
chk(HALL.KIT_coluna == 10 and HALL.KIT_col_base == 10 and HALL.KIT_dougong_intermediario == 10 and HALL.KIT_arquitrave == 10 and HALL.KIT_prancha == 10 and HALL.KIT_vao_parede == 7,
	("hall pieces: coluna %s, col_base %s, dougong %s, arquitrave %s, prancha %s, vao_parede %s (10/10/10/10/10/7)"):format(
		tostring(HALL.KIT_coluna), tostring(HALL.KIT_col_base), tostring(HALL.KIT_dougong_intermediario), tostring(HALL.KIT_arquitrave), tostring(HALL.KIT_prancha), tostring(HALL.KIT_vao_parede)))
local inBay = {}
for _, p in ipairs(workspace:GetDescendants()) do if p:IsA("BasePart") and (p.Transparency < 1 or p.CanCollide) and (p.Position - SHOPF.Position).Magnitude < 60 then
	local a0, a1 = boxIn(SHOPF, p)
	for _, bay in ipairs({{-B3 / 2, B3 / 2}, {B3 / 2, 14.5}, {-14.5, -B3 / 2}}) do
		-- clear passage: column faces +-1.36 plus 0.25 tolerance, above the 1.5 column bases, below the beam (15.8)
		local b0 = Vector3.new(9.3, 9.5, bay[1] + 1.61) local b1 = Vector3.new(12.9, 15.7, bay[2] - 1.61)
		if overlap(a0, a1, b0, b1) then table.insert(inBay, p:GetFullName()) end end end end
local rpH = RaycastParams.new() rpH.FilterType = Enum.RaycastFilterType.Exclude rpH.FilterDescendantsInstances = {} rpH.RespectCanCollide = true
local walkIn = {}
for _, vv in ipairs({0, B3, -B3}) do for _, y in ipairs({9.5, 12, 15}) do
	local a = SHOPF * Vector3.new(13.5, y, vv) local b = SHOPF * Vector3.new(-9, y, vv)
	local r = workspace:Raycast(a, b - a, rpH) if r then table.insert(walkIn, ("v%.1f y%g %s"):format(vv, y, r.Instance.Name)) end end end
chk(#inBay == 0 and #walkIn == 0, ("the 3 front bays are open (no part in any opening: %d %s) and walkable from the forecourt to u -9 (collider hits: %s)"):format(
	#inBay, table.concat(inBay, ", ", 1, math.min(#inBay, 4)), #walkIn == 0 and "none" or table.concat(walkIn, "; ")))
-- sign and banners face the plaza (front = LookVector for these meshes)
local placa = nil for _, i in ipairs(LOJA) do if i.Name == "KIT_placa" then placa = i end end
chk(placa.CFrame.LookVector:Dot(UW) > 0.99, ("shop KIT_placa at %s faces the plaza (dot %.3f), size %s"):format(v3s(placa.Position), placa.CFrame.LookVector:Dot(UW), v3s(placa.Size)))
local bs, bOK = {}, true
for _, r in ipairs({"LOJA_A", "LOJA_B"}) do local b = BAN[r] local bot = b.Position.Y - b.Size.Y / 2
	table.insert(bs, ("%s %s bottom %.3f facing %.3f"):format(r, v3s(b.Position), bot, b.CFrame.LookVector:Dot(UW))) if math.abs(bot) > 0.02 or b.CFrame.LookVector:Dot(UW) < 0.99 then bOK = false end end
chk(bOK, "shop end banners stand on the paving and face the plaza: " .. table.concat(bs, "; "))
-- roof: ridge along the facade, eave line / brackets measured on the placed triangles
local TEL = {} for _, i in ipairs(LOJA) do if i.Name:sub(1, 6) == "TEL_G_" then table.insert(TEL, i) end end
local ridge = nil for _, i in ipairs(TEL) do if i.Name == "TEL_G_cumeeira" then ridge = i end end
local rdot = math.abs(ridge.CFrame.RightVector:Dot(SHOPF.LookVector))
local rb0, rb1 = Vector3.new(1e9, 1e9, 1e9), Vector3.new(-1e9, -1e9, -1e9)
for _, i in ipairs(TEL) do local a0, a1 = boxIn(SHOPF, i) rb0 = rb0:Min(a0) rb1 = rb1:Max(a1) end
chk(rdot > 0.99, ("roof ridge runs along the facade (|dot v| %.3f); roof box u %.2f..%.2f v %.2f..%.2f y %.2f..%.2f"):format(rdot, rb0.X, rb1.X, rb0.Z, rb1.Z, rb0.Y, rb1.Y))
local okP, probe = pcall(function()
	local AS = game:GetService("AssetService")
	local cache, tris = {}, {}
	for _, i in ipairs(TEL) do
		local d = cache[i.MeshId]
		if not d then
			local em = AS:CreateEditableMeshAsync(Content.fromUri(i.MeshId))
			local pos, mn, mx = {}, Vector3.new(1e9, 1e9, 1e9), Vector3.new(-1e9, -1e9, -1e9)
			for _, vid in ipairs(em:GetVertices()) do local p = em:GetPosition(vid) pos[vid] = p mn = mn:Min(p) mx = mx:Max(p) end
			local tl = {} for _, fid in ipairs(em:GetFaces()) do local fv = em:GetFaceVertices(fid) table.insert(tl, {pos[fv[1]], pos[fv[2]], pos[fv[3]]}) end
			em:Destroy() d = {t = tl, c = (mn + mx) / 2, s = mx - mn} cache[i.MeshId] = d
		end
		local k = Vector3.new(i.Size.X / d.s.X, i.Size.Y / d.s.Y, i.Size.Z / d.s.Z)
		local cf = SHOPF:ToObjectSpace(i.CFrame)
		for _, t in ipairs(d.t) do local a, b, c = cf * ((t[1] - d.c) * k), cf * ((t[2] - d.c) * k), cf * ((t[3] - d.c) * k)
			table.insert(tris, {a, b, c, math.min(a.X, b.X, c.X), math.max(a.X, b.X, c.X), math.min(a.Z, b.Z, c.Z), math.max(a.Z, b.Z, c.Z)}) end
	end
	local function low(x, z, y0) local best
		for _, t in ipairs(tris) do if x >= t[4] and x <= t[5] and z >= t[6] and z <= t[7] then
			local a, b, c = t[1], t[2], t[3] local d1x, d1z, d2x, d2z = b.X - a.X, b.Z - a.Z, c.X - a.X, c.Z - a.Z
			local den = d1x * d2z - d2x * d1z
			if math.abs(den) > 1e-9 then local px, pz = x - a.X, z - a.Z
				local l1, l2 = (px * d2z - d2x * pz) / den, (d1x * pz - px * d1z) / den
				if l1 >= 0 and l2 >= 0 and l1 + l2 <= 1 then local y = a.Y + l1 * (b.Y - a.Y) + l2 * (c.Y - a.Y)
					if y >= y0 and (best == nil or y < best) then best = y end end end end end
		return best end
	local function ext(dx, dz) local last = 0 for s = 0, 30, 0.1 do if low(-0.5 + dx * s, dz * s, 0) then last = s end end return last end
	local gaps = {} for _, q in ipairs(COLS) do local y = low(q[1], q[2], 15) table.insert(gaps, y and (y - 23.85) or 99) end
	local banner = 99 for _, sg in ipairs({-1, 1}) do for _, du in ipairs({-1.4, 1.4}) do for _, dv in ipairs({-2.5, 2.5}) do
		local y = low(16 + du, sg * 22 + dv, 0) if y then banner = math.min(banner, y - 22.2) end end end end
	return {n = #tris, front = ext(1, 0) - 12.36, back = ext(-1, 0) - 12.36, left = ext(0, 1) - 15.86, right = ext(0, -1) - 15.86, gaps = gaps, banner = banner}
end)
if okP then
	local g0, g1 = math.huge, -math.huge local gs = {}
	for _, g in ipairs(probe.gaps) do g0 = math.min(g0, g) g1 = math.max(g1, g) table.insert(gs, ("%.2f"):format(g)) end
	local oh = {probe.front, probe.back, probe.left, probe.right} local ohOK = true
	for _, o in ipairs(oh) do if o < 3 or o > 5 then ohOK = false end end
	chk(ohOK, ("roof eave overhang past the outer column faces (measured on %d placed triangles): front %.2f back %.2f sides %.2f / %.2f (3..5)"):format(probe.n, probe.front, probe.back, probe.left, probe.right))
	chk(g0 > -0.6 and g1 < 4.5, ("roof underside above the 10 bracket tops (23.85): %s (min %.2f max %.2f; gate reference -0.41..2.71)"):format(table.concat(gs, " "), g0, g1))
	chk(probe.banner > 0.5, ("roof clears the end banners' tops by %.2f"):format(probe.banner))
else table.insert(v, "NOTE roof triangle probe skipped: " .. tostring(probe)) end
local wallOut = -math.huge for _, c in ipairs(HL:GetChildren()) do if c.Name == "KIT_vao_parede" then local a0, a1 = boxIn(SHOPF, c)
	wallOut = math.max(wallOut, a1.X - rb1.X, rb0.X - a0.X, a1.Z - rb1.Z, rb0.Z - a0.Z) end end
chk(wallOut < -3, ("no hall wall reaches past the roof box (closest %.2f inside)"):format(-wallOut))
-- training
local tIn, tOut = 0, {}
for _, i in ipairs(TREINO) do local a0, a1 = boxIn(nil, i) tIn += 1
	if a0.X < -154.0 or a1.X > -116.0 or a0.Z < -15.0 or a1.Z > 15.0 then table.insert(tOut, i.Name .. v3s(i.Position)) end end
local sand = OE:FindFirstChild("TREINO_areia")
chk(#tOut == 0, ("training props inside the railing (%d members, sand top %.2f): %s"):format(tIn, sand.Position.Y + sand.Size.Y / 2, #tOut == 0 and "all inside" or table.concat(tOut, ", ")))
local rpT = RaycastParams.new() rpT.FilterType = Enum.RaycastFilterType.Exclude rpT.FilterDescendantsInstances = {} rpT.RespectCanCollide = true
local ent = {}
for _, z in ipairs({-4, 0, 4}) do local r = workspace:Raycast(Vector3.new(-105, 3, z), Vector3.new(-60, 0, 0), rpT)
	table.insert(ent, ("z%d first hit %s x %.1f"):format(z, r and r.Instance.Name or "none", r and r.Position.X or 0))
	if not r or r.Position.X > -150 then ent.bad = true end end
local rows = {} for _, x in ipairs({-110, -116, -120, -135, -150}) do local h, n = hitW(x, 0) table.insert(rows, ("x%d %s %.2f"):format(x, n, h or -99)) end
chk(not ent.bad and math.abs((hitW(-120, 0) or -99) - 1.0) < 0.02 and math.abs(hitW(-110, 0) or -99) < 0.3,
	("training entrance open toward the plaza (%s); floor: %s"):format(table.concat(ent, "; "), table.concat(rows, " ")))
local tb, tOK = {}, true
for _, r in ipairs({"TREINO_A", "TREINO_B"}) do local b = BAN[r] local bot = b.Position.Y - b.Size.Y / 2
	table.insert(tb, ("%s %s bottom %.3f facing %.3f"):format(r, v3s(b.Position), bot, b.CFrame.LookVector.X)) if math.abs(bot - 1.0) > 0.02 or b.CFrame.LookVector.X < 0.99 then tOK = false end end
chk(tOK, "training banners stand on the deck and face the plaza: " .. table.concat(tb, "; "))
-- colliders
local cols, badCol = {}, {}
local cx = caixa and caixa.CFrame local cs = caixa and (caixa.Size + Vector3.new(2, 2, 2))
for _, c in ipairs(COL:GetChildren()) do if c.Name:sub(1, 6) == "hx_f4_" then table.insert(cols, c.Name)
	local a0, a1 = boxIn(PAD.CFrame, c) if overlap(a0, a1, pad0, pad1) then table.insert(badCol, c.Name .. "/pad") end
	if cx then local m0, m1 = boxIn(cx, c) if overlap(m0, m1, -cs / 2, cs / 2) then table.insert(badCol, c.Name .. "/MailBox") end end end end
table.sort(cols)
chk(#cols == 22 and #badCol == 0, ("hx_f4_ colliders: %d (expected 22: ramp, landing, back wall, 2 side walls, 10 columns, 2 banners, 5 training rails); over the pad or the MailBox Caixa (+1): %d %s"):format(
	#cols, #badCol, table.concat(badCol, " ")))
-- walkability grid over the shop and the training yard (RespectCanCollide), no misses
local hist, miss = {}, {}
local function rec(h, lbl) if not h then table.insert(miss, lbl) return end local k = ("%.2f"):format(h) hist[k] = (hist[k] or 0) + 1 end
for u = -12, 52, 2 do for vv = -24, 24, 2 do local h = hitS(u, vv) rec(h, ("shop(%d,%d)"):format(u, vv)) end end
for x = -158, -100, 2 do for z = -18, 18, 2 do local h = hitW(x, z) rec(h, ("tr(%d,%d)"):format(x, z)) end end
local hk = {} for k, n in pairs(hist) do table.insert(hk, {k = k, n = n}) end table.sort(hk, function(a, b) return a.n > b.n end)
local hs = {} for i = 1, math.min(#hk, 14) do table.insert(hs, hk[i].k .. "x" .. hk[i].n) end
chk(#miss == 0, ("walkability grid (2 studs) over the shop and the training yard: %d misses %s; heights %s"):format(#miss, table.concat(miss, " ", 1, math.min(#miss, 6)), table.concat(hs, " ")))
-- near-coplanar tops among the shop pieces (shop frame) and the training pieces (world frame)
local function coplanar(list, frame)
	local bx = {} for _, p in ipairs(list) do local a0, a1 = boxIn(frame, p) table.insert(bx, {p = p, a0 = a0, a1 = a1}) end
	local pairsNew, pairsOld = {}, 0
	for i = 1, #bx do for j = i + 1, #bx do local A, B = bx[i], bx[j]
		if math.abs(A.a1.Y - B.a1.Y) < 0.045 then
			local ox = math.min(A.a1.X, B.a1.X) - math.max(A.a0.X, B.a0.X) local oz = math.min(A.a1.Z, B.a1.Z) - math.max(A.a0.Z, B.a0.Z)
			if ox > 0.05 and oz > 0.05 and ox * oz > 0.25 then
				if A.p:GetAttribute("HexGen") or B.p:GetAttribute("HexGen") then table.insert(pairsNew, A.p.Name .. "/" .. B.p.Name .. ("@%.2f"):format(A.a1.Y)) else pairsOld += 1 end
			end end end end
	return pairsNew, pairsOld end
local shopList = {} for _, c in ipairs(HL:GetDescendants()) do if c:IsA("BasePart") then table.insert(shopList, c) end end
for _, i in ipairs(LOJA) do if i:IsA("BasePart") and i.Transparency < 1 and i.Name ~= "PadLoja" then table.insert(shopList, i) end end
local pn, po = coplanar(shopList, SHOPF)
local trList = {} for _, c in ipairs(HT:GetDescendants()) do if c:IsA("BasePart") then table.insert(trList, c) end end
for _, i in ipairs(TREINO) do table.insert(trList, i) end
local tn, to = coplanar(trList, nil)
chk(#pn == 0 and #tn == 0, ("near-coplanar overlapping tops involving new parts: shop %d %s, training %d %s (pre-existing kit pairs, box test: %d)"):format(
	#pn, table.concat(pn, ", ", 1, math.min(#pn, 6)), #tn, table.concat(tn, ", ", 1, math.min(#tn, 6)), po + to))
-- old shop area left empty (apart from the training yard)
local left = {}
for _, p in ipairs(workspace:GetDescendants()) do if p:IsA("BasePart") and (p.Transparency < 1 or p.CanCollide) then local q = p.Position
	if q.X > -146 and q.X < -88 and q.Z > -30 and q.Z < 20 and q.Y > 0.3 and q.Y < 45 and not (p:IsDescendantOf(HT) or p:IsDescendantOf(HL) or p:IsDescendantOf(L.HEX_Chao) or p:IsDescendantOf(L.HEX_Muralha)
		or p:GetAttribute("HEX_GRUPO") == "TREINO" or p:GetAttribute("HEX_GRUPO") == "LOJA" or p.Name:sub(1, 6) == "hx_f4_" or p.Name:sub(1, 6) == "hx_f2_"
		or (p.Name == "KIT_estandarte" and (BAN.TREINO_A == p or BAN.TREINO_B == p or BAN.LOJA_A == p or BAN.LOJA_B == p))) then table.insert(left, p:GetFullName() .. v3s(q)) end end end
chk(#left == 0, "old shop area (X -146..-88, Z -30..20) holds nothing but the training yard" .. (#left > 0 and (": " .. table.concat(left, ", ", 1, math.min(#left, 6))) or ""))
-- removals in storage, folders
local rf = REM:FindFirstChild(FASE) local nR = rf and #rf:GetChildren() or 0
chk(nR == 50, ("%s holds %d items (expected 50: 36 frame pieces, 12 colliders, 2 balustrades)"):format(FASE, nR))
local nHL, nHT = #HL:GetChildren(), #HT:GetChildren()
chk(nHL == 84 and nHT == 57, ("HEX_Loja %d children (84 = 57 hall + block + 10 tiles + 8 moulding + 6 balustrades + 2 lanterns), HEX_Treino %d (57 = deck + 21 posts + 21 caps + 10 rails + 4 lanterns)"):format(nHL, nHT))
-- things that must keep working
local SANT = workspace:FindFirstChild("Santuario") local tp = true
for n = 1, 6 do local m = SANT and SANT:FindFirstChild("Portal" .. n) local d = m and m:FindFirstChild("Disco")
	if not (d and d:GetAttribute("AreaId") == n and d.CanTouch) then tp = false end end
chk(tp, "Santuario Portal1..6 Disco/AreaId/CanTouch unchanged")
local ib1 = ignis:GetBoundingBox()
chk((ib1.Position - ib0.Position).Magnitude < 1e-3, "NPCs.Ignis unchanged")
local LA = workspace.Corredores.Lobby_Area1 local drift = 0
for _, n in ipairs({"Estrada", "RampaArea1", "RampaPatamar"}) do local c = LA:FindFirstChild(n)
	if not c or (c.Position - c:GetAttribute("CF0").Position).Magnitude > 1e-3 or not c.CanCollide then drift += 1 end end
chk(drift == 0, "exit walk colliders Estrada/RampaArea1/RampaPatamar unchanged")

say(("F4 %s: SIGN %d, removed now %d (already removed %d), LOJA members placed %d + roof pieces refitted %d, balustrades fixed %d, training members %d, railing posts %d")
	:format(allOK and "OK" or "VERIFY FAILED", SIGN, N.removedNow, nAlready, N.rigid, N.roof, N.bal, #TREINO, N.posts or 0))
for _, s in ipairs(v) do say("  " .. s) end
say("  colliders: " .. table.concat(cols, ","))
return table.concat(rep, "\n")
