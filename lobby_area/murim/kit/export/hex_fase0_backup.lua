-- hex_fase0_backup.lua : F0 = backup, original-state tagging (CF0/S0), cluster and role tags,
-- empty HEX_* folders, wedge self-test and triangle check. Nothing visible moves. No accents.
-- Idempotent: backup is skipped if it exists; CF0/S0/Color0/Alpha0 are written only where missing;
-- tags are plain attribute sets; folders are created only if missing.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, SS = H.L, H.SS
local SSS = game:GetService("ServerScriptService")
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end

local function posOf(i) local cf = i:GetAttribute("CF0") if cf then return cf.Position end
	return i:IsA("Model") and i:GetPivot().Position or i.Position end
local function kids(parent, name, filter) local r = {}
	for _, c in ipairs(parent:GetChildren()) do
		if c.Name == name and (c:IsA("BasePart") or c:IsA("Model")) and (not filter or filter(posOf(c))) then table.insert(r, c) end end
	return r end
local function one(parent, name) local r = kids(parent, name)
	assert(#r == 1, ("F0: %s.%s -> %d (expected 1)"):format(parent.Name, name, #r)) return r[1] end
local function need(list, n, label) assert(#list == n, ("F0: %s -> %d (expected %d)"):format(label, #list, n)) return list end
local function addAll(dst, src) for _, v in ipairs(src) do table.insert(dst, v) end end

local P, F, Le, Pr, Col, Veg, Oe = L.Patio, L.Forja, L.Leste, L.Props, L.Colisao, L.Veg, L.Oeste
if L:GetAttribute("HEX_F0_OK") and #H.REM:GetChildren() > 0 then
	return "F0 already applied and later phases have run (LOBBY_REMOVIDOS_HEX not empty): nothing written." end

------------------------------------------------------------------ 0. gather + assert (read-only)
local galF = function(q) return q.X >= 100 and q.X <= 150 and math.abs(q.Z) <= 48 and q.Y > 1 end
local lojF = function(q) return q.X >= -132 and q.X <= -100 and q.Z >= -27 and q.Z <= 19 and q.Y > 1 end

local GAL = {}
for _, n in ipairs({"NUC_-146_-45", "PODIO_-146_-45", "ESCADA_X_-104"}) do table.insert(GAL, one(P, n)) end
addAll(GAL, need(kids(P, "KIT_piso_mod", galF), 136, "GAL KIT_piso_mod"))
addAll(GAL, need(kids(P, "KIT_bal_seg", galF), 47, "GAL KIT_bal_seg"))
addAll(GAL, need(kids(P, "KIT_sumeru_seg", galF), 47, "GAL KIT_sumeru_seg"))
addAll(GAL, need(kids(P, "KIT_sumeru_canto", galF), 4, "GAL KIT_sumeru_canto"))
table.insert(GAL, one(Le, "SANT_galeria")) table.insert(GAL, one(Le, "SANT_fundo"))
do local por, sub = {}, {base = 0, moldura = 0, vortice = 0, fragmento_1 = 0}
	for _, c in ipairs(Le:GetChildren()) do if c.Name:sub(1, 4) == "POR_" then table.insert(por, c)
		for k in pairs(sub) do if c.Name:sub(1, 5 + #k) == "POR_" .. k .. "_" then sub[k] += 1 end end end end
	need(por, 30, "GAL POR_*")
	assert(sub.base == 6 and sub.moldura == 6 and sub.vortice == 6 and sub.fragmento_1 == 12,
		("F0: POR split base %d moldura %d vortice %d fragmento_1 %d"):format(sub.base, sub.moldura, sub.vortice, sub.fragmento_1))
	addAll(GAL, por) end
addAll(GAL, need(kids(Pr, "KIT_lanterna_palacio", function(q) return q.X >= 105 and q.X <= 115 end), 4, "GAL KIT_lanterna_palacio"))
for _, n in ipairs({"terraco_santuario", "sant_N", "sant_S", "sant_fundo"}) do table.insert(GAL, one(Col, n)) end
addAll(GAL, need(kids(Col, "portal_pilar"), 12, "GAL portal_pilar"))
local PORTALS = {}
for i = 1, 6 do local m = workspace.Santuario:FindFirstChild("Portal" .. i)
	assert(m and m:IsA("Model"), "F0: Santuario.Portal" .. i .. " missing") table.insert(PORTALS, m) table.insert(GAL, m) end
need(GAL, 3 + 136 + 47 + 47 + 4 + 2 + 30 + 4 + 4 + 12 + 6, "GALERIA total")

local LOJA = {}
for _, n in ipairs({"NUC_104_-24", "PODIO_104_-24", "ESCADA_X_104", "LOJA_interior"}) do table.insert(LOJA, one(P, n)) end
addAll(LOJA, need(kids(P, "KIT_piso_mod", lojF), 40, "LOJA KIT_piso_mod"))
addAll(LOJA, need(kids(P, "KIT_bal_seg", lojF), 21, "LOJA KIT_bal_seg"))
addAll(LOJA, need(kids(P, "KIT_sumeru_seg", lojF), 24, "LOJA KIT_sumeru_seg"))
addAll(LOJA, need(kids(P, "KIT_sumeru_canto", lojF), 4, "LOJA KIT_sumeru_canto"))
do local t = {} for _, c in ipairs(F:GetChildren()) do
		if c.Name:sub(1, 6) == "TEL_G_" and (c:IsA("BasePart") or c:IsA("Model")) and posOf(c).X < -85 then table.insert(t, c) end end
	addAll(LOJA, need(t, 17, "LOJA Forja TEL_G_* X<-85")) end
table.insert(LOJA, one(Col, "terraco_loja"))
local lojaM = workspace:FindFirstChild("LojaMochilas") assert(lojaM, "F0: workspace.LojaMochilas missing")
local pad = lojaM:FindFirstChild("PadLoja") assert(pad and pad:IsA("BasePart"), "F0: LojaMochilas.PadLoja missing")
local mail = workspace:FindFirstChild("MailBox") assert(mail and mail:IsA("Model"), "F0: workspace.MailBox (Model) missing")
table.insert(LOJA, pad) table.insert(LOJA, mail) table.insert(LOJA, one(Pr, "VIL_placa_loja"))
table.insert(LOJA, H.find({P}, "KIT_placa", Vector3.new(-118, 17.48, -20.07)))
need(LOJA, 4 + 40 + 21 + 24 + 4 + 17 + 1 + 3 + 1, "LOJA total")

local TREINO = {}
do local want = {LOB_poste_treino = 9, LOB_boneco_treino = 2, LOB_estante_armas = 1, TREINO_areia = 1} local got = {}
	for _, c in ipairs(Oe:GetChildren()) do table.insert(TREINO, c) got[c.Name] = (got[c.Name] or 0) + 1 end
	need(TREINO, 13, "TREINO Oeste children")
	for k, v in pairs(want) do assert(got[k] == v, ("F0: Oeste %s -> %d (expected %d)"):format(k, got[k] or 0, v)) end end

-- roles
local ROLES = {}
local function role(parents, name, pos, r) table.insert(ROLES, {H.find(parents, name, pos), r}) end
local B = {{50, 21.08, -96, "FORJA_E"}, {-50, 21.08, -96, "FORJA_W"},
	{-46, 11.1, -52, "PLANTER_BL"}, {46, 11.1, -52, "PLANTER_BR"}, {-46, 11.1, -31, "PLANTER_FL"}, {46, 11.1, -31, "PLANTER_FR"},
	{46, 11.1, -10, "GAL_A"}, {46, 11.1, 11, "GAL_B"}, {-46, 11.1, -10, "LOJA_A"}, {-46, 11.1, 11, "LOJA_B"},
	{-100, 11.1, 22, "TREINO_A"}, {-100, 11.1, 54, "TREINO_B"},
	{46, 11.1, 32, "REMOVE"}, {-46, 11.1, 32, "REMOVE"}, {46, 11.1, 53, "REMOVE"}, {-46, 11.1, 53, "REMOVE"},
	{27, 11.1, 85, "REMOVE"}, {-27, 11.1, 85, "REMOVE"}, {27, 11.1, 120, "REMOVE"}, {-27, 11.1, 120, "REMOVE"}}
for _, b in ipairs(B) do role({Pr}, "KIT_estandarte", Vector3.new(b[1], b[2], b[3]), b[4]) end
need(kids(Pr, "KIT_estandarte"), 20, "KIT_estandarte total")
local LIONS = {}
for _, l in ipairs({{"LOB_leao_esfera", -14, 3.99, -88.03, "FORGE_M"}, {"LOB_leao_filhote", 14, 3.98, -88.12, "FORGE_F"},
	{"LOB_leao_esfera", -17, 3.99, 134.03, "GATE_M"}, {"LOB_leao_filhote", 17, 3.98, 134.12, "GATE_F"}}) do
	role({Pr}, l[1], Vector3.new(l[2], l[3], l[4]), l[5]) table.insert(LIONS, ROLES[#ROLES][1]) end
for _, k in ipairs({{"JAR_lotus", 88.1, 1.05, -40.6, "LOTUS_FL1"}, {"JAR_lotus", 93.7, 1.10, 57.5, "LOTUS_FL2"},
	{"JAR_lotus", 86.5, 1.00, 95.7, "LOTUS_FR1"}, {"JAR_lotus_b", 82.2, 0.95, 9.5, "LOTUS_FL3"}, {"JAR_lotus_b", 80.2, 0.90, -20.5, "LOTUS_FR2"},
	{"LOB_rocha_1", 29.9, 2.34, -159.8, "ROCK_FL1"}, {"LOB_rocha_1", -33.9, 2.13, -158.2, "ROCK_FL2"}, {"LOB_rocha_2", -87.9, 1.30, -20.1, "ROCK_FR1"}}) do
	role({Veg}, k[1], Vector3.new(k[2], k[3], k[4]), k[5]) end
for _, b in ipairs({{-64, 0.85, -22, "BENCH_FL"}, {64, 0.85, 30, "BENCH_FR"}, {-94, 0.85, -8, "REMOVE"}}) do
	role({Pr}, "VIL_banco", Vector3.new(b[1], b[2], b[3]), b[4]) end
need(ROLES, 20 + 4 + 8 + 3, "HEX_ROLE total")
local PIC = one(P, "LOB_picareta_aurora")

-- portals: Disco with AreaId N (read-only check, must hold before we write anything)
local portalRep = {}
for i, m in ipairs(PORTALS) do local d = m:FindFirstChild("Disco", true)
	assert(d and d:IsA("BasePart") and d:GetAttribute("AreaId") == i, ("F0: Portal%d Disco/AreaId mismatch"):format(i))
	table.insert(portalRep, ("P%d=A%d"):format(i, d:GetAttribute("AreaId"))) end

-- backup sources (read-only presence check)
local SRC = {workspace.LOBBY_MURIM, workspace:FindFirstChild("Santuario"), lojaM, mail,
	workspace:FindFirstChild("Corredores") and workspace.Corredores:FindFirstChild("Lobby_Area1"),
	workspace:FindFirstChild("LV10_TempContexto"), workspace:FindFirstChild("NPCs") and workspace.NPCs:FindFirstChild("Ignis"),
	SSS:FindFirstChild("Core") and SSS.Core:FindFirstChild("ExpeditionTravel"),
	SSS:FindFirstChild("Core") and SSS.Core:FindFirstChild("IslandTravel"),
	game:GetService("StarterPlayer").StarterPlayerScripts:FindFirstChild("PortaisAmbiente")}
local SRCN = {"LOBBY_MURIM", "Santuario", "LojaMochilas", "MailBox", "Corredores.Lobby_Area1", "LV10_TempContexto",
	"NPCs.Ignis", "Core.ExpeditionTravel", "Core.IslandTravel", "StarterPlayerScripts.PortaisAmbiente"}

------------------------------------------------------------------ writes start here
local rec = H.begin("HEX F0 backup + tags")
local ok, err = pcall(function()
	-- 1. backup
	local bk = SS:FindFirstChild("BACKUP_LOBBY_PRE_HEX")
	if bk then say("1 backup: BACKUP_LOBBY_PRE_HEX already exists (" .. #bk:GetChildren() .. " children) -> skipped")
	else
		for i = 1, #SRCN do assert(SRC[i], "F0: backup source missing: " .. SRCN[i]) end
		bk = Instance.new("Folder") bk.Name = "BACKUP_LOBBY_PRE_HEX"
		for i, s in ipairs(SRC) do local c = s:Clone() assert(c, "F0: Clone() returned nil for " .. SRCN[i])
			c:SetAttribute("BackupOrigem", s:GetFullName()) c.Parent = bk end
		bk.Parent = SS
		say("1 backup: created BACKUP_LOBBY_PRE_HEX with " .. #bk:GetChildren() .. " clones")
	end

	-- 2. originals
	local nNew, nAll = 0, 0
	local function rem(i) if i:IsA("BasePart") or i:IsA("Model") then nAll += 1
			if i:GetAttribute("CF0") == nil then nNew += 1 end H.remember(i) end end
	for _, d in ipairs(L:GetDescendants()) do rem(d) end
	for _, d in ipairs(workspace.Santuario:GetDescendants()) do rem(d) end
	rem(pad) rem(mail) for _, d in ipairs(mail:GetDescendants()) do rem(d) end
	for _, d in ipairs(workspace.Corredores.Lobby_Area1:GetDescendants()) do rem(d) end
	local nC, nA = 0, 0
	for _, o in ipairs({LIONS[1], LIONS[2], LIONS[3], LIONS[4], PIC}) do
		local list = {o} for _, d in ipairs(o:GetDescendants()) do table.insert(list, d) end
		for _, mp in ipairs(list) do if mp:IsA("MeshPart") then
				if mp:GetAttribute("Color0") == nil then mp:SetAttribute("Color0", mp.Color) end nC += 1
				local sa = mp:FindFirstChildOfClass("SurfaceAppearance")
				if sa then if sa:GetAttribute("Alpha0") == nil then sa:SetAttribute("Alpha0", sa.AlphaMode.Name) end nA += 1 end end end end
	say(("2 originals: %d BasePart/Model remembered (%d new CF0); Color0 on %d MeshParts, Alpha0 on %d SurfaceAppearances"):format(nAll, nNew, nC, nA))

	-- 3. cluster tags
	for _, i in ipairs(GAL) do i:SetAttribute("HEX_GRUPO", "GALERIA") end
	for _, i in ipairs(LOJA) do i:SetAttribute("HEX_GRUPO", "LOJA") end
	for _, i in ipairs(TREINO) do i:SetAttribute("HEX_GRUPO", "TREINO") end
	say(("3 HEX_GRUPO: GALERIA %d, LOJA %d, TREINO %d"):format(#GAL, #LOJA, #TREINO))

	-- 4. role tags
	local rc = {} for _, r in ipairs(ROLES) do r[1]:SetAttribute("HEX_ROLE", r[2]) rc[r[2]] = (rc[r[2]] or 0) + 1 end
	say(("4 HEX_ROLE: %d tags (REMOVE %d: 8 banners + 1 bench)"):format(#ROLES, rc.REMOVE or 0))

	-- 5. folders
	local made = 0
	for _, n in ipairs({"HEX_Chao", "HEX_Muralha", "HEX_Monumento", "HEX_Lagos", "HEX_Canteiros", "HEX_Loja", "HEX_Galeria",
		"HEX_Treino", "HEX_PonteSaida", "HEX_Detalhes"}) do if not L:FindFirstChild(n) then made += 1 end H.folder(L, n) end
	say("5 HEX_* folders: 10 present (" .. made .. " created now)")

	-- 6. self-tests
	local sign = H.selfTest()
	local C, a, b = Vector3.new(0, 0, 0), Vector3.new(1, 0, 0), Vector3.new(0, 0, 1)
	local w = H.rightTri(workspace, {Name = "hx_tritest", Color = H.C.ouro}, C, a, 8, b, 6, 600, 1)
	local pass = H.checkTri(w, C, a, 8, b, 6, 600) w:Destroy()
	local C2, a2, b2 = Vector3.new(10, 0, -4), Vector3.new(0.8660254, 0, 0.5), Vector3.new(-0.5, 0, 0.8660254)
	local w2 = H.rightTri(workspace, {Name = "hx_tritest2", Color = H.C.ouro}, C2, a2, 5, b2, 3, 600, 0.5)
	local pass2 = H.checkTri(w2, C2, a2, 5, b2, 3, 600) w2:Destroy()
	say(("6 selfTest SIGN=%d (%s); rightTri check %s, rotated check %s"):format(sign, sign == 1 and "tall at local +Z, as expected" or "INVERTED",
		pass and "PASS" or "FAIL", pass2 and "PASS" or "FAIL"))
	assert(pass and pass2, "F0: triangle check failed")
end)
if ok then L:SetAttribute("HEX_F0_OK", true) end
H.commit(rec)
if not ok then error("F0 failed after writes began: " .. tostring(err)) end

-- 7. report
local mainOK = workspace:FindFirstChild("LojaMochilas") and workspace.LojaMochilas:FindFirstChild("PadLoja") ~= nil
say("7 Main path workspace.LojaMochilas.PadLoja: " .. (mainOK and "found" or "MISSING"))
say("7 portals: " .. table.concat(portalRep, " "))
local bk = SS:FindFirstChild("BACKUP_LOBBY_PRE_HEX")
local names = {} for _, c in ipairs(bk:GetChildren()) do table.insert(names, c.Name) end
say("7 backup children (" .. #names .. "): " .. table.concat(names, ", "))
return "F0 OK\n" .. table.concat(rep, "\n")
