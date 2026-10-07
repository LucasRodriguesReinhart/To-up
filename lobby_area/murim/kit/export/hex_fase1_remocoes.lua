-- hex_fase1_remocoes.lua : F1 = removals to ServerStorage.LOBBY_REMOVIDOS_HEX/F1_Rxx (never Destroy).
-- Removes dragons, gallery roof, vegetation (keeps the 8 pond keepers -> HEX_Lagos), clutter, old river,
-- rectangle plaza + old monument, rectangle perimeter, forge column/beams over Ignis, forge step colliders,
-- LV10_TempContexto and the 8 surplus banners. No accents.
-- Idempotent: every item is looked up in its original parent AND in LOBBY_REMOVIDOS_HEX; the phase asserts
-- found + already_removed == expected for every item BEFORE moving anything, then moves only what is still live.
-- WARNING: after F1 there is no floor collider and no forge stair collider. Run F2 straight after; no Play between.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, SS, REM = H.L, H.SS, H.REM
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end
assert(L:GetAttribute("HEX_F0_OK") == true, "F1: F0 marker HEX_F0_OK missing; run hex_fase0_backup.lua first")

local P, F, Le, Pr, Col, Veg, AG, CS, Po, Ch = L.Patio, L.Forja, L.Leste, L.Props, L.Colisao, L.Veg, L.AGUA,
	L.ChaoSimples, L.Portao, L.Chao
local LAGOS = L:FindFirstChild("HEX_Lagos") assert(LAGOS, "F1: LOBBY_MURIM.HEX_Lagos missing (F0 creates it)")

local function posOf(i) local cf = i:GetAttribute("CF0") if cf then return cf.Position end
	if i:IsA("Model") then return i:GetPivot().Position end
	if i:IsA("BasePart") then return i.Position end
	return nil end
local function near(x, y, z, tol) local v = Vector3.new(x, y, z) tol = tol or 0.3
	return function(c) local p = posOf(c) return p ~= nil and (p - v).Magnitude <= tol end end
local function named(n, extra) return function(c) return c.Name == n and (not extra or extra(c)) end end

------------------------------------------------------------------ item list
-- each item: fase, label, parent (original parent instance), match(c), n (expected), kind ("folder" for Folders)
local ITEMS = {}
local function add(fase, label, parent, match, n, kind)
	table.insert(ITEMS, {fase = fase, label = label, parent = parent, match = match, n = n, kind = kind}) end
local function addName(fase, parent, name, n, extra, label) add(fase, label or (parent.Name .. "." .. name), parent, named(name, extra), n) end

-- R01 dragons / roof beasts (100)
for _, q in ipairs({{"KIT_chiwen", 10}, {"KIT_besta_0", 20}, {"KIT_besta_1", 20}, {"KIT_besta_2", 20}, {"KIT_imortal", 20}, {"KIT_chuishou", 20}}) do
	addName("F1_R01_dragoes", P, q[1], q[2]) end
-- R02 gallery roof: Forja TEL_G_* with X > 95 (17)
add("F1_R02_telhado_galeria", "Forja TEL_G_* X>95", F, function(c)
	local p = posOf(c) return c.Name:sub(1, 6) == "TEL_G_" and p ~= nil and p.X > 95 end, 17)
-- R03 vegetation: every Veg child without HEX_ROLE (149), Canteiros folder, Patio.LOB_canteiro
add("F1_R03_vegetacao", "Veg children without HEX_ROLE", Veg, function(c) return c:GetAttribute("HEX_ROLE") == nil end, 149)
add("F1_R03_vegetacao", "ChaoSimples.Canteiros (folder, 24 parts)", CS, named("Canteiros"), 1, "folder")
addName("F1_R03_vegetacao", P, "LOB_canteiro", 1)
-- R04 clutter
for _, q in ipairs({{"VIL_poco", 1}, {"VIL_barril", 2}, {"VIL_carroca", 1}, {"VIL_cesto", 2}, {"VIL_caixas", 1}, {"VIL_telhas", 1},
	{"VIL_varal", 1}, {"VIL_lanterna_pedra", 16}}) do addName("F1_R04_entulho", Pr, q[1], q[2]) end
addName("F1_R04_entulho", Pr, "VIL_banco", 1, function(c) return c:GetAttribute("HEX_ROLE") == "REMOVE" end, "Props.VIL_banco HEX_ROLE=REMOVE")
-- R05 old river
for _, n in ipairs({"LAGO_agua", "LAGO_leito", "LAGO_margem", "LOB_ponte_lua"}) do addName("F1_R05_rio", Le, n, 1) end
addName("F1_R05_rio", AG, "Lago", 51)
add("F1_R05_rio", "ChaoSimples.Margem (folder, 102 parts)", CS, named("Margem"), 1, "folder")
addName("F1_R05_rio", Col, "lago_fundo", 1)
for i = 0, 15 do addName("F1_R05_rio", Col, "ponte" .. i, 1) end
-- R06 rectangle plaza and old monument (PATIO_passadeira is NOT matched: exact names only)
for _, n in ipairs({"PATIO_base", "PATIO_piso_0", "PATIO_piso_1", "PATIO_piso_2", "PATIO_piso_3", "PATIO_piso_4", "PATIO_piso_5",
	"PATIO_borda", "PATIO_marcos", "PATIO_ornamento", "PATIO_agua", "PATIO_leito", "LOB_meiofio", "LOB_pedestal_espada", "OESTE_caminho"}) do
	addName("F1_R06_patio_retangulo", P, n, 1) end
add("F1_R06_patio_retangulo", "Props LOB_braseiro |X|<12 |Z|<12", Pr, function(c)
	local p = posOf(c) return c.Name == "LOB_braseiro" and p ~= nil and math.abs(p.X) < 12 and math.abs(p.Z) < 12 end, 4)
add("F1_R06_patio_retangulo", "ChaoSimples.AroHex (folder, 12 parts)", CS, named("AroHex"), 1, "folder")
add("F1_R06_patio_retangulo", "ChaoSimples.Juntas (folder, 32 parts)", CS, named("Juntas"), 1, "folder")
addName("F1_R06_patio_retangulo", Ch, "LOB_chao", 1)
addName("F1_R06_patio_retangulo", Po, "VIA_piso", 1)
for _, n in ipairs({"pedestal_espada", "via", "patio", "patio_spawn", "chao_leste", "chao_oeste", "chao_sul", "chao_norte"}) do
	addName("F1_R06_patio_retangulo", Col, n, 1) end
-- R07 rectangle perimeter (Portao.KIT_muro_pilar stays; F2 moves it)
addName("F1_R07_muralha_ret", Po, "KIT_muro_seg", 112)
addName("F1_R07_muralha_ret", F, "KIT_muro_torre", 14)
for _, n in ipairs({"limite_N", "limite_E", "limite_W", "limite_S_E", "limite_S_W", "muralha1", "muralha-1"}) do
	addName("F1_R07_muralha_ret", Col, n, 1) end
-- R08 forge: central column + base + architraves over Ignis (the duplicates are handled below)
for _, q in ipairs({{"KIT_coluna", 0, 19.04, -108}, {"KIT_coluna", 0, 19.04, -122}, {"KIT_col_base", 0, 10.73, -108}, {"KIT_col_base", 0, 10.73, -122},
	{"KIT_arquitrave", 4.5, 24.42, -108}, {"KIT_arquitrave", -4.5, 24.42, -108}, {"KIT_arquitrave", 4.5, 24.42, -122}, {"KIT_arquitrave", -4.5, 24.42, -122}}) do
	add("F1_R08_forja", ("Patio.%s @(%g,%g,%g)"):format(q[1], q[2], q[3], q[4]), P, named(q[1], near(q[2], q[3], q[4])), 1) end
-- R09a forge step colliders (replaced in F2 by hx_f2_forja_rampa)
for i = 1, 12 do addName("F1_R09a_degraus_forja", Col, "degrau_forja" .. i, 1) end
-- R12 temporary context folder
add("F1_R12_temp", "Workspace.LV10_TempContexto (folder)", workspace, named("LV10_TempContexto"), 1, "folder")
-- R13 surplus banners
addName("F1_R13_estandartes", Pr, "KIT_estandarte", 8, function(c) return c:GetAttribute("HEX_ROLE") == "REMOVE" end,
	"Props.KIT_estandarte HEX_ROLE=REMOVE")

------------------------------------------------------------------ gather + assert (read-only, nothing is written here)
local function removedIn(fase, parentPath, match)
	local f = REM:FindFirstChild(fase) local r = {}
	if f then for _, c in ipairs(f:GetChildren()) do
			if c:GetAttribute("OrigemPath") == parentPath and match(c) then table.insert(r, c) end end end
	return r end

local FOLDER_PARTS = {Canteiros = 24, Margem = 102, AroHex = 12, Juntas = 32, LV10_TempContexto = 5}
local function countParts(f) local k = 0 for _, d in ipairs(f:GetDescendants()) do if d:IsA("BasePart") then k += 1 end end return k end

local todo, bad, nLive, nDone = {}, {}, 0, 0
local perFase = {}
for _, it in ipairs(ITEMS) do
	local live = {}
	for _, c in ipairs(it.parent:GetChildren()) do if it.match(c) then table.insert(live, c) end end
	local done = removedIn(it.fase, it.parent:GetFullName(), it.match)
	if #live + #done ~= it.n then
		table.insert(bad, ("%s: live %d + removed %d ~= %d"):format(it.label, #live, #done, it.n))
	else
		for _, c in ipairs(live) do
			if it.kind == "folder" then
				if not c:IsA("Folder") then table.insert(bad, it.label .. ": expected a Folder, got " .. c.ClassName) end
			elseif not (c:IsA("BasePart") or c:IsA("Model")) then
				table.insert(bad, it.label .. ": unexpected class " .. c.ClassName) end
			table.insert(todo, {c, it.fase, it.kind}) end
		for _, c in ipairs(done) do if c:IsA("Folder") then local e = FOLDER_PARTS[c.Name]
				if e and countParts(c) ~= e then table.insert(bad, it.label .. ": removed folder has " .. countParts(c) .. " parts, expected " .. e) end end end
		for _, c in ipairs(live) do if c:IsA("Folder") then local e = FOLDER_PARTS[c.Name]
				if e and countParts(c) ~= e then table.insert(bad, it.label .. ": folder has " .. countParts(c) .. " parts, expected " .. e) end end end
	end
	nLive += #live nDone += #done
	perFase[it.fase] = (perFase[it.fase] or 0) + it.n
end

-- R08 exact duplicates: each spot must hold 2 KIT_coluna live (first run) or 1 live + 1 removed (re-run)
local DUP = {{36, 19.04, -134}, {36, 19.04, -146}, {-36, 19.04, -134}, {-36, 19.04, -146}}
for _, q in ipairs(DUP) do
	local v = Vector3.new(q[1], q[2], q[3])
	local live = H.findAll({P}, "KIT_coluna", v)
	local done = removedIn("F1_R08_forja", P:GetFullName(), named("KIT_coluna", near(q[1], q[2], q[3])))
	local lbl = ("Patio.KIT_coluna duplicate @(%g,%g,%g)"):format(q[1], q[2], q[3])
	if #live == 2 and #done == 0 then
		local a, b = live[1], live[2]
		if not (a.CFrame == b.CFrame and a.Size == b.Size) then table.insert(bad, lbl .. ": the two copies are not identical") end
		table.insert(todo, {b, "F1_R08_forja"}) nLive += 1
	elseif #live == 1 and #done == 1 then nDone += 1
	else table.insert(bad, ("%s: live %d + removed %d (expected 2+0 or 1+1)"):format(lbl, #live, #done)) end
	perFase["F1_R08_forja"] = (perFase["F1_R08_forja"] or 0) + 1
end

-- keepers: 8 pond keepers (LOTUS_*, ROCK_*) either still in Veg or already in HEX_Lagos
local KEEP_ROLES = {LOTUS_FL1 = true, LOTUS_FL2 = true, LOTUS_FL3 = true, LOTUS_FR1 = true, LOTUS_FR2 = true, ROCK_FL1 = true, ROCK_FL2 = true, ROCK_FR1 = true}
local keepLive, keepDone = {}, {}
for _, c in ipairs(Veg:GetChildren()) do local r = c:GetAttribute("HEX_ROLE") if r then
		if KEEP_ROLES[r] then table.insert(keepLive, c) else table.insert(bad, "Veg child with unexpected HEX_ROLE " .. r) end end end
for _, c in ipairs(LAGOS:GetChildren()) do if KEEP_ROLES[c:GetAttribute("HEX_ROLE") or ""] then table.insert(keepDone, c) end end
if #keepLive + #keepDone ~= 8 then table.insert(bad, ("keepers: Veg %d + HEX_Lagos %d ~= 8"):format(#keepLive, #keepDone)) end

-- no instance may be selected twice
do local seen = {} for _, t in ipairs(todo) do if seen[t[1]] then table.insert(bad, "selected twice: " .. t[1]:GetFullName()) end seen[t[1]] = true end end

if #bad > 0 then error("F1 aborted before writing anything:\n" .. table.concat(bad, "\n")) end

-- pre-state for verification
local ignis = workspace.NPCs.Ignis
local ib0, is0 = ignis:GetBoundingBox()

------------------------------------------------------------------ writes start here
local function removeFolder(f, fase) -- H.remember cannot take a Folder (no CFrame): remember its parts, tag, move
	if f:IsDescendantOf(REM) then return false end
	for _, d in ipairs(f:GetDescendants()) do if d:IsA("BasePart") or d:IsA("Model") then H.remember(d) end end
	if f:GetAttribute("OrigemPath") == nil then f:SetAttribute("OrigemPath", f.Parent:GetFullName()) end
	f.Parent = H.folder(REM, fase) return true end

local moved, keptMoved = 0, 0
local movedPer = {}
local rec = H.begin("HEX F1 removals")
local ok, err = pcall(function()
	for _, t in ipairs(todo) do
		local i, fase, kind = t[1], t[2], t[3]
		local did = (kind == "folder") and removeFolder(i, fase) or H.remove(i, fase)
		if did then moved += 1 movedPer[fase] = (movedPer[fase] or 0) + 1 end
	end
	for _, k in ipairs(keepLive) do
		local cf = k:IsA("Model") and k:GetPivot() or k.CFrame
		k.Parent = LAGOS
		local cf2 = k:IsA("Model") and k:GetPivot() or k.CFrame
		assert((cf2.Position - cf.Position).Magnitude < 1e-4, "F1: keeper moved while reparenting: " .. k.Name)
		keptMoved += 1
	end
end)
if ok then L:SetAttribute("HEX_F1_OK", true) end
H.commit(rec)
if not ok then error("F1 failed after writes began (Ctrl+Z undoes the partial recording): " .. tostring(err)) end

------------------------------------------------------------------ verify
local v = {}
local function chk(cond, msg) table.insert(v, (cond and "PASS " or "FAIL ") .. msg) return cond end
local allOK = true
-- per-folder counts in REM
local fases = {"F1_R01_dragoes", "F1_R02_telhado_galeria", "F1_R03_vegetacao", "F1_R04_entulho", "F1_R05_rio", "F1_R06_patio_retangulo",
	"F1_R07_muralha_ret", "F1_R08_forja", "F1_R09a_degraus_forja", "F1_R12_temp", "F1_R13_estandartes"}
local total, noOrig = 0, 0
local parts = {}
for _, fs in ipairs(fases) do
	local f = REM:FindFirstChild(fs) local n = f and #f:GetChildren() or 0 total += n
	if f then for _, c in ipairs(f:GetChildren()) do if c:GetAttribute("OrigemPath") == nil then noOrig += 1 end end end
	allOK = chk(n == perFase[fs], ("%s: %d in storage (expected %d)"):format(fs, n, perFase[fs])) and allOK
end
allOK = chk(noOrig == 0, ("OrigemPath set on every moved item (%d missing)"):format(noOrig)) and allOK
-- name scan across Workspace
local pats = {"KIT_chiwen", "KIT_besta", "KIT_imortal", "KIT_chuishou", "pinheiro", "bordo", "bambu", "ameixeira", "arbusto", "tufo", "JAR_grama",
	"peonia", "crisantemo", "JAR_canteiro", "VIL_poco", "VIL_barril", "VIL_carroca", "VIL_cesto", "VIL_caixas", "VIL_telhas", "VIL_varal",
	"VIL_lanterna_pedra", "KIT_muro_torre", "KIT_muro_seg", "LAGO_", "LOB_ponte_lua"}
local hits = {}
for _, d in ipairs(workspace:GetDescendants()) do for _, p in ipairs(pats) do
		if d.Name:find(p, 1, true) then table.insert(hits, d:GetFullName()) break end end end
allOK = chk(#hits == 0, ("name scan across Workspace: %d hits %s"):format(#hits, table.concat(hits, "; ", 1, math.min(#hits, 5)))) and allOK
-- Ignis untouched (vs pre-F1 and vs the F0 backup clone)
local ib1, is1 = ignis:GetBoundingBox()
local bI = SS:FindFirstChild("BACKUP_LOBBY_PRE_HEX") and SS.BACKUP_LOBBY_PRE_HEX:FindFirstChild("Ignis")
local bb, bs = bI:GetBoundingBox()
allOK = chk((ib1.Position - ib0.Position).Magnitude < 1e-4 and (is1 - is0).Magnitude < 1e-4 and (ib1.Position - bb.Position).Magnitude < 1e-4
	and (is1 - bs).Magnitude < 1e-4, ("NPCs.Ignis bounding box unchanged (%s / %s)"):format(tostring(ib1.Position), tostring(is1))) and allOK
allOK = chk(ignis:FindFirstChild("LetreiroIgnis") ~= nil, "NPCs.Ignis.LetreiroIgnis still present") and allOK
-- Veg empty, HEX_Lagos = 8 keepers at their original CFrames
allOK = chk(#Veg:GetChildren() == 0, ("Veg has %d children (expected 0)"):format(#Veg:GetChildren())) and allOK
local kOK, kN = true, 0
for _, c in ipairs(LAGOS:GetChildren()) do if KEEP_ROLES[c:GetAttribute("HEX_ROLE") or ""] then kN += 1
		local cf = c:IsA("Model") and c:GetPivot() or c.CFrame
		if (cf.Position - c:GetAttribute("CF0").Position).Magnitude > 1e-3 then kOK = false end end end
allOK = chk(kN == 8 and #LAGOS:GetChildren() == 8 and kOK, ("HEX_Lagos has %d children, %d keepers, all at CF0: %s"):format(#LAGOS:GetChildren(), kN, tostring(kOK))) and allOK
-- nothing that stays in LOBBY_MURIM moved
local drift = 0
for _, d in ipairs(L:GetDescendants()) do if d:IsA("BasePart") then local cf = d:GetAttribute("CF0")
		if cf and (d.Position - cf.Position).Magnitude > 1e-3 then drift += 1 end end end
allOK = chk(drift == 0, ("BaseParts still in LOBBY_MURIM away from CF0: %d"):format(drift)) and allOK
-- things that must survive
local function nKids(parent, pred) local k = 0 for _, c in ipairs(parent:GetChildren()) do if pred(c) then k += 1 end end return k end
local keepList = {
	{"PATIO_passadeira", P:FindFirstChild("PATIO_passadeira") ~= nil}, {"ChaoSimples.Base", CS:FindFirstChild("Base") ~= nil},
	{"AGUA LaminaDagua x6", nKids(AG, named("LaminaDagua")) == 6},
	{"Portao.KIT_muro_pilar x4", nKids(Po, named("KIT_muro_pilar")) == 4},
	{"Colisao.soleira_portao", Col:FindFirstChild("soleira_portao") ~= nil}, {"Colisao.terraco_forja", Col:FindFirstChild("terraco_forja") ~= nil},
	{"Props.VIL_placa_loja", Pr:FindFirstChild("VIL_placa_loja") ~= nil},
	{"Props VIL_banco BENCH_FL+FR", nKids(Pr, named("VIL_banco", function(c) return c:GetAttribute("HEX_ROLE") ~= "REMOVE" end)) == 2},
	{"Props KIT_estandarte x12", nKids(Pr, named("KIT_estandarte")) == 12},
	{"Props LOB_braseiro x2 (forge)", nKids(Pr, named("LOB_braseiro")) == 2},
	{"Forja TEL_G_* x34 (shop 17 + gate 17)", nKids(F, function(c) return c.Name:sub(1, 6) == "TEL_G_" end) == 34},
	{"Patio KIT_coluna x42", nKids(P, named("KIT_coluna")) == 42},
	{"LojaMochilas.PadLoja", workspace:FindFirstChild("LojaMochilas") ~= nil and workspace.LojaMochilas:FindFirstChild("PadLoja") ~= nil},
	{"MailBox", workspace:FindFirstChild("MailBox") ~= nil},
	{"SpawnLobby", workspace:FindFirstChild("Mystical Spawn Point") ~= nil and workspace["Mystical Spawn Point"]:FindFirstChild("SpawnLobby") ~= nil},
	{"Corredores.Lobby_Area1", workspace.Corredores:FindFirstChild("Lobby_Area1") ~= nil},
}
local miss = {} for _, k in ipairs(keepList) do if not k[2] then table.insert(miss, k[1]) end end
allOK = chk(#miss == 0, "kept items present" .. (#miss > 0 and (": MISSING " .. table.concat(miss, ", ")) or "")) and allOK
local portals = {} for i = 1, 6 do local m = workspace.Santuario:FindFirstChild("Portal" .. i) local d = m and m:FindFirstChild("Disco", true)
	table.insert(portals, (d and d:GetAttribute("AreaId") == i) and ("P" .. i .. "ok") or ("P" .. i .. "BAD")) end
allOK = chk(not table.concat(portals, ""):find("BAD"), "portals Disco/AreaId: " .. table.concat(portals, " ")) and allOK

say(("F1 %s: moved now %d (live before %d, already removed before %d); keepers reparented now %d; storage total %d"):format(
	allOK and "OK" or "VERIFY FAILED", moved, nLive, nDone, keptMoved, total))
for _, fs in ipairs(fases) do say(("  %s: moved now %d, expected total %d"):format(fs, movedPer[fs] or 0, perFase[fs])) end
for _, s in ipairs(v) do say("  " .. s) end
say("NEXT: run hex_fase2_perimetro_chao.lua now (no floor or forge-stair collider until F2). Do not enter Play before F2.")
return table.concat(rep, "\n")
