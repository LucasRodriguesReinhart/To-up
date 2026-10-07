-- hex_fase2_perimetro_chao.lua : F2 = hexagon perimeter and ground. No accents.
-- Builds HEX_Chao (29 paving parts + gate apron, bands / spokes / border band / medallion ring / studs, joints,
-- outside ground) and HEX_Muralha (84 wall segments, 6 towers with hip roofs cloned from the gate TEL_G tiles),
-- colliders hx_f2_*, the forge stair ramp; moves the 4 Portao.KIT_muro_pilar, mirrors AGUA.LaminaDagua and
-- reshapes ChaoSimples.Base.Base so that NO plate lies inside the hexagon under the paving or the pond holes
-- (Base top -0.5 would otherwise cover the F6 pond water at -0.9).
-- Idempotent: clears HEX_Chao / HEX_Muralha / hx_f2_* and sets every existing instance from CF0/S0 or constants.
-- On any error after writes began, the ChangeHistory recording is CANCELLED (all F2 writes are reverted).
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, Y = H.L, H.Y
local CHS = game:GetService("ChangeHistoryService")
local rep = {}
local function say(...) local t = {} for i, v in ipairs({...}) do t[i] = tostring(v) end table.insert(rep, table.concat(t, " ")) end
local function v3s(v) return ("(%.2f,%.2f,%.2f)"):format(v.X, v.Y, v.Z) end
assert(L:GetAttribute("HEX_F0_OK") == true, "F2: F0 marker HEX_F0_OK missing")
assert(L:GetAttribute("HEX_F1_OK") == true, "F2: F1 marker HEX_F1_OK missing (run hex_fase1_remocoes.lua first)")

local C = H.C
local T30 = math.tan(math.rad(30))
local VR = 150 / math.cos(math.rad(30)) -- 173.205 (circumradius)
local A100 = 100 * T30                  -- 57.735 (half side at apothem 100)
local PAV_MAT = H.PAVING_MATERIAL
local SECONDARY = (PAV_MAT ~= Enum.Material.Pavement) -- SmoothPlastic fallback -> secondary joint rings
local FACE_ORDER = {"FR", "F", "FL", "BL", "B", "BR"}

------------------------------------------------------------------ read-only pre-checks
local HC, HM = L:FindFirstChild("HEX_Chao"), L:FindFirstChild("HEX_Muralha")
local Po, Fo, AG, Pa, COL = L.Portao, L.Forja, L.AGUA, L.Patio, H.COL
local bad = {}
if not (HC and HM) then table.insert(bad, "HEX_Chao / HEX_Muralha folder missing (F0 creates them)") end
-- gate roof template: 17 Forja TEL_G_* with Z in [130,170], yaw 0 or 180 only
local Fold = CFrame.new(0, 30.91, 150)
local TPL = {}
for _, c in ipairs(Fo:GetChildren()) do
	if c:IsA("BasePart") and c.Name:sub(1, 6) == "TEL_G_" then
		local cf = c:GetAttribute("CF0") or c.CFrame
		if cf.Position.Z >= 130 and cf.Position.Z <= 170 then table.insert(TPL, c) end
	end
end
table.sort(TPL, function(a, b) local pa, pb = (a:GetAttribute("CF0") or a.CFrame).Position, (b:GetAttribute("CF0") or b.CFrame).Position
	if a.Name ~= b.Name then return a.Name < b.Name end if pa.X ~= pb.X then return pa.X < pb.X end return pa.Z < pb.Z end)
if #TPL ~= 17 then table.insert(bad, ("gate TEL_G template: %d pieces (expected 17)"):format(#TPL)) end
local tplMin, tplMax = math.huge, -math.huge
for _, c in ipairs(TPL) do
	local rel = Fold:ToObjectSpace(c:GetAttribute("CF0") or c.CFrame)
	if math.abs(rel.RightVector.Z) >= 0.02 or math.abs(rel.RightVector.Y) >= 0.02 then table.insert(bad, "TEL_G piece not yaw 0/180: " .. c.Name) end
	for _, d in ipairs(c:GetDescendants()) do if not d:IsA("SurfaceAppearance") then table.insert(bad, "TEL_G piece has unexpected child " .. d.ClassName) end end
	local cf, sz = c:GetAttribute("CF0") or c.CFrame, c:GetAttribute("S0") or c.Size
	for _, sy in ipairs({-1, 1}) do local w = cf:PointToWorldSpace(Vector3.new(0, sy * sz.Y / 2, 0)) tplMin = math.min(tplMin, w.Y) tplMax = math.max(tplMax, w.Y) end
end
-- pillars
local PIL = {}
for _, q in ipairs({{48, "F"}, {-48, "F"}, {148, "B"}, {-148, "B"}}) do
	local r = H.findAll({Po}, "KIT_muro_pilar", Vector3.new(q[1], 6.7, 150), 0.3)
	if #r ~= 1 then table.insert(bad, ("Portao.KIT_muro_pilar @(%g,6.7,150): %d found"):format(q[1], #r)) else table.insert(PIL, {r[1], q[1], q[2]}) end
end
-- waterfalls
local LAM, CAS = {}, {}
for _, c in ipairs(AG:GetChildren()) do if c.Name == "LaminaDagua" and c:IsA("BasePart") then table.insert(LAM, c) end end
for _, c in ipairs(Pa:GetChildren()) do if c.Name == "LOB_cascata" then table.insert(CAS, c) end end
if #LAM ~= 6 then table.insert(bad, ("AGUA.LaminaDagua: %d (expected 6)"):format(#LAM)) end
if #CAS ~= 6 then table.insert(bad, ("Patio.LOB_cascata: %d (expected 6)"):format(#CAS)) end
local function casPos(c) return c:IsA("Model") and c:GetPivot().Position or c.Position end
local function mirrorCF(cf0) local p = cf0.Position local rx, ry, rz = cf0:ToEulerAnglesYXZ()
	return CFrame.new(-p.X, p.Y, p.Z) * CFrame.fromEulerAnglesYXZ(rx, -ry, -rz) end
local EXPECT_LAM = {Vector3.new(182, -17, -60), Vector3.new(182, -17, 92), Vector3.new(-182, -17, -28), Vector3.new(-182, -17, 112),
	Vector3.new(44, -17, -206), Vector3.new(-64, -17, 192)}
for _, w in ipairs(LAM) do
	local t = mirrorCF(w:GetAttribute("CF0") or w.CFrame).Position
	local okE = false for _, e in ipairs(EXPECT_LAM) do if (e - t).Magnitude < 0.05 then okE = true end end
	local best = math.huge for _, c in ipairs(CAS) do local p = casPos(c) best = math.min(best, (Vector2.new(p.X, p.Z) - Vector2.new(t.X, t.Z)).Magnitude) end
	if not okE then table.insert(bad, "LaminaDagua mirror target unexpected: " .. v3s(t)) end
	if best > 12 then table.insert(bad, ("LaminaDagua at %s is %.1f from the nearest cascade"):format(v3s(t), best)) end
end
-- base plate, library, kept colliders
local CS = L:FindFirstChild("ChaoSimples") local BASE = CS and CS:FindFirstChild("Base") and CS.Base:FindFirstChild("Base")
if not (BASE and BASE:IsA("BasePart")) then table.insert(bad, "ChaoSimples.Base.Base missing") end
if not (H.LIB:FindFirstChild("KIT") and H.LIB.KIT:FindFirstChild("KIT_muro_seg")) then table.insert(bad, "BIBLIOTECA_MURIM.KIT.KIT_muro_seg missing") end
for _, n in ipairs({"muro_portao_C1", "muro_portao_C2", "muro_portao_E", "muro_portao_W", "soleira_portao", "terraco_forja"}) do
	if not COL:FindFirstChild(n) then table.insert(bad, "Colisao." .. n .. " missing") end end
if #bad > 0 then error("F2 aborted before writing anything:\n" .. table.concat(bad, "\n")) end

local SIGN = H.selfTest() -- temporary wedge, created and destroyed inside

------------------------------------------------------------------ builders
local WEDGES = {}
local rawTri = H.rightTri
H.rightTri = function(parent, o, Cc, a, la, b, lb, topY, thick) -- record every wedge for H.checkTri
	local w = rawTri(parent, o, Cc, a, la, b, lb, topY, thick)
	table.insert(WEDGES, {w = w, C = Cc, a = a, la = la, b = b, lb = lb, top = topY})
	return w end

local N = {}
local function build()
	H.clear(HC) H.clear(HM) H.clearColliders("hx_f2_")

	-- A) PAVING: 29 parts, tops at 0, thickness 1; pond holes left open
	local PISO = H.folder(HC, "Piso")
	local function oPav(n) return {Name = n, Color = C.pav, Material = PAV_MAT, CanCollide = true} end
	H.part({Name = "Piso_nucleo", Size = Vector3.new(2 * A100, 1, 200), CFrame = CFrame.new(0, -0.5, 0), Color = C.pav, Material = PAV_MAT, CanCollide = true}, PISO)
	for _, sx in ipairs({1, -1}) do for _, sz in ipairs({1, -1}) do
		H.rightTri(PISO, oPav("Piso_cunha_centro"), Vector3.new(sx * A100, 0, 0), Vector3.new(sx, 0, 0), A100, Vector3.new(0, 0, sz), 100, 0, 1) end end
	local P = H.LAY.PONDS
	local RECTS = {
		F = {{-A100, A100, 0, 50}}, B = {{-A100, A100, 0, 50}}, BL = {{-A100, A100, 0, 50}}, BR = {{-A100, A100, 0, 50}},
		FL = {{-A100, P.FL.s1, 0, 50}, {P.FL.s2, A100, 0, 50}, {P.FL.s1, P.FL.s2, 0, P.FL.d1}, {P.FL.s1, P.FL.s2, P.FL.d2, 50}},
		FR = {{-A100, P.FR.s1, 0, 50}, {P.FR.s2, A100, 0, 50}, {P.FR.s1, P.FR.s2, 0, P.FR.d1}, {P.FR.s1, P.FR.s2, P.FR.d2, 50}},
	}
	for _, f in ipairs(FACE_ORDER) do
		for _, r in ipairs(RECTS[f]) do H.faceRect(PISO, oPav("Piso_faixa_" .. f), f, r[1], r[2], r[3], r[4], -1, 0) end
		local Fc = H.FACES[f]
		for _, sg in ipairs({1, -1}) do H.rightTri(PISO, oPav("Piso_cunha_" .. f), H.fp(f, sg * A100, 0, 0), Fc.t * sg, 50 * T30, Fc.inw, 50, 0, 1) end
	end
	N.piso = #PISO:GetChildren()
	H.part({Name = "Piso_adro", Size = Vector3.new(92, 1, 28), CFrame = CFrame.new(0, -0.5, 164), Color = C.pav, Material = PAV_MAT, CanCollide = false}, PISO)

	-- B) OVERLAYS: tops 0.25 (bands, spokes, border), medallion 0.40, studs 0.55
	local FX = H.folder(HC, "Faixas")
	local function strip(name, size, cf, col, mat) return H.part({Name = name, Size = size, CFrame = cf, Color = col,
		Material = mat or Enum.Material.SmoothPlastic, CanCollide = true}, FX) end
	local function bandEdges(name, cf, w, len)
		strip(name, Vector3.new(w, 0.35, len), cf, C.faixa, Enum.Material.Pavement)
		for _, sx in ipairs({1, -1}) do strip(name .. "_linha", Vector3.new(1, 0.35, len), cf * CFrame.new(sx * (w / 2 + 0.5), 0, 0), C.linha) end
	end
	bandEdges("Faixa_frente", CFrame.new(0, 0.075, 92), 28, 116)
	bandEdges("Faixa_fundo", CFrame.new(0, 0.075, -47.5), 28, 27)
	bandEdges("Raio_galeria", CFrame.fromMatrix(Vector3.new(59.13, 0.075, -20.28), Vector3.new(0.5, 0, 0.866025), Y), 14, 54.7)
	bandEdges("Raio_loja", CFrame.fromMatrix(Vector3.new(-60.08, 0.075, -20.83), Vector3.new(0.5, 0, -0.866025), Y), 14, 56.9)
	bandEdges("Faixa_adro", CFrame.new(0, 0.075, 164), 28, 28)
	H.hexRing(FX, {Name = "Borda", Color = C.borda, Material = Enum.Material.Pavement, CanCollide = true}, 144.6, 147.6, -0.1, 0.25, {[90] = {{-15, 15}}})
	N.faixas = #FX:GetChildren()
	local MED = H.folder(HC, "Medalhao")
	H.hexRing(MED, {Name = "Medalhao_linha_int", Color = C.linha, CanCollide = true}, 27, 28, -0.1, 0.40)
	H.hexRing(MED, {Name = "Medalhao_anel", Color = C.anel, Material = Enum.Material.Slate, CanCollide = true}, 28, 33, -0.1, 0.40)
	H.hexRing(MED, {Name = "Medalhao_linha_ext", Color = C.linha, CanCollide = true}, 33, 34, -0.1, 0.40)
	for k = 0, 5 do local a = math.rad(60 * k) local u = Vector3.new(math.cos(a), 0, math.sin(a))
		H.part({Name = "Medalhao_tacha", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.15, 2.4, 2.4),
			CFrame = CFrame.new(u * 35.22 + Vector3.new(0, 0.475, 0)) * CFrame.Angles(0, 0, math.pi / 2), Color = C.ouro, Material = Enum.Material.Metal}, MED) end
	N.medalhao = #MED:GetChildren()

	-- C) JOINTS: top 0.10, no collision, clipped against H.zones()
	local JUN = H.folder(HC, "Juntas")
	local ZONES = H.zones()
	local RINGS = {52, 76, 100, 124}
	if SECONDARY then for _, a in ipairs({40, 64, 88, 112, 136}) do table.insert(RINGS, a) end table.sort(RINGS) end
	for _, a in ipairs(RINGS) do for _, f in ipairs(FACE_ORDER) do
		local len = 2 * T30 * (a - 0.25) - 0.1
		H.jointStrip(JUN, H.fp(f, -len / 2, 150 - a, 0), H.fp(f, len / 2, 150 - a, 0), ZONES) end end
	local cuts = {} for _, a in ipairs(RINGS) do table.insert(cuts, a / math.cos(math.rad(30))) end table.sort(cuts)
	local pieces, r0 = {}, 40
	for _, rc in ipairs(cuts) do if rc - 0.695 > r0 and rc < 159.4 then table.insert(pieces, {r0, rc - 0.695}) r0 = rc + 0.695 end end
	table.insert(pieces, {r0, 159.4})
	for k = 0, 5 do local a = math.rad(60 * k) local u = Vector3.new(math.cos(a), 0, math.sin(a))
		for _, pc in ipairs(pieces) do H.jointStrip(JUN, u * pc[1], u * pc[2], ZONES) end end
	N.juntas, N.radialPieces = #JUN:GetChildren(), pieces

	-- I) OUTSIDE GROUND: the old rectangle (X +-182, Z -218..202, top -0.5) minus the hexagon, so nothing lies
	-- under the paving or the pond holes. Base.Base becomes the strip behind the forge; 7 new parts do the rest.
	local FORA = H.folder(HC, "Fora")
	local function oFora(n) return {Name = n, Color = C.fora, Material = Enum.Material.SmoothPlastic, CanCollide = false} end
	H.part({Name = "Fora_frente", Size = Vector3.new(364, 3, 52), CFrame = CFrame.new(0, -2, 176), Color = C.fora, CanCollide = false}, FORA)
	for _, sx in ipairs({1, -1}) do
		H.part({Name = "Fora_lado", Size = Vector3.new(182 - VR, 3, 300), CFrame = CFrame.new(sx * (VR + 182) / 2, -2, 0), Color = C.fora, CanCollide = false}, FORA)
		for _, sz in ipairs({1, -1}) do
			H.rightTri(FORA, oFora("Fora_canto"), Vector3.new(sx * VR, 0, sz * 150), Vector3.new(-sx, 0, 0), 150 * T30, Vector3.new(0, 0, -sz), 150, -0.5, 3) end
	end
	H.remember(BASE)
	BASE.Size = Vector3.new(364, 3, 68) BASE.CFrame = CFrame.new(0, -2, -184)
	BASE.Color = C.fora BASE.Material = Enum.Material.SmoothPlastic BASE.CanCollide = false
	BASE:SetAttribute("HEX_F2_forma", "faixa de fora atras da forja (Z -218..-150)")
	N.fora = #FORA:GetChildren()

	-- E) WALLS: 84 KIT_muro_seg clones (named Muro_seg), Y -0.5..14.0, butted end to end
	local RUNS = {F = {{46, 80, 4}, {-80, -46, 4}}, B = {{63.5, 80, 2}, {-80, -63.5, 2}},
		FL = {{-80, 80, 18}}, BL = {{-80, 80, 18}}, BR = {{-80, 80, 18}}, FR = {{-80, 80, 18}}}
	N.muros = 0
	for _, f in ipairs(FACE_ORDER) do
		local fold = H.folder(HM, "Muro_" .. f)
		for _, run in ipairs(RUNS[f]) do local s1, s2, n = run[1], run[2], run[3] local Li = (s2 - s1) / n
			for i = 1, n do local s = s1 + Li * (i - 0.5)
				local seg = H.libClone("KIT", "KIT_muro_seg", fold)
				seg.Name = "Muro_seg" seg.Size = Vector3.new(Li, 14.5, 4.8)
				seg.CFrame = H.faceCF(f, s, 0, 6.75) * CFrame.Angles(0, math.pi, 0)
				seg:SetAttribute("Face", f) N.muros += 1 end end
	end
	-- pillars (from CF0/S0)
	for _, q in ipairs(PIL) do local p, x, face = q[1], q[2], q[3]
		local cf0, s0 = H.cf0(p), H.s0(p)
		p.Size = Vector3.new(s0.X, 16, s0.Z)
		if face == "F" then p.CFrame = cf0.Rotation + Vector3.new(cf0.X, 7.5, cf0.Z)
		else p.CFrame = H.faceCF("B", (x > 0) and 63.5 or -63.5, 0, 7.5) end
	end

	-- F) TOWERS on the 6 vertex rays, local -Z facing the plaza; roofs = gate TEL_G tiles rescaled
	local TOW = {{"R", 0}, {"FR", 60}, {"FL", 120}, {"L", 180}, {"BL", 240}, {"BR", 300}}
	local sc = Vector3.new(0.451, 0.55, 0.6175)
	N.torres, N.telhas = 0, 0
	for _, tw in ipairs(TOW) do local id, ang = tw[1], math.rad(tw[2])
		local pos = Vector3.new(169 * math.cos(ang), 0, 169 * math.sin(ang))
		local Ft = CFrame.lookAt(pos, Vector3.zero)
		local m = Instance.new("Model") m.Name = "Torre_" .. id m.Parent = HM
		local function TP(name, size, lp, col, mat, coll) return H.part({Name = name, Size = size, CFrame = Ft * CFrame.new(lp), Color = col,
			Material = mat, CanCollide = coll, CastShadow = true}, m) end
		TP("Plinto", Vector3.new(18.6, 2.5, 18.6), Vector3.new(0, 0.75, 0), C.pedra, Enum.Material.Slate, true)
		TP("Corpo", Vector3.new(18, 12.6, 18), Vector3.new(0, 8.3, 0), C.muro)
		TP("Capa", Vector3.new(19.4, 1.0, 19.4), Vector3.new(0, 15.1, 0), C.teal)
		TP("Corpo_alto", Vector3.new(18, 8.4, 13), Vector3.new(0, 19.8, 0), C.laca)
		for _, sz in ipairs({1, -1}) do TP("Janela", Vector3.new(4, 4.4, 0.25), Vector3.new(0, 19.6, sz * 6.675), C.janela) end
		for _, sx in ipairs({1, -1}) do TP("Janela", Vector3.new(0.25, 4.4, 4), Vector3.new(sx * 9.175, 19.6, 0), C.janela) end
		TP("Faixa_ouro", Vector3.new(18.4, 0.6, 13.4), Vector3.new(0, 23.5, 0), C.ouro, Enum.Material.Metal)
		TP("Moldura", Vector3.new(5.4, 9.6, 0.2), Vector3.new(0, 8.6, -9.15), C.ouro, Enum.Material.Metal)
		TP("Estandarte", Vector3.new(4.6, 8.8, 0.2), Vector3.new(0, 8.6, -9.3), C.carpete, Enum.Material.Fabric)
		local roof = Instance.new("Model") roof.Name = "Telhado" roof.Parent = m
		local Fnew = Ft * CFrame.new(0, 23.9, 0)
		for _, src in ipairs(TPL) do
			local cf0, s0 = src:GetAttribute("CF0") or src.CFrame, src:GetAttribute("S0") or src.Size
			local rel = Fold:ToObjectSpace(cf0)
			local cl = src:Clone()
			for k in pairs(cl:GetAttributes()) do cl:SetAttribute(k, nil) end
			cl.Anchored = true cl.CanCollide = false cl.CanTouch = false cl.CanQuery = false
			cl.Size = s0 * sc
			cl.CFrame = Fnew * CFrame.new(rel.Position * sc) * rel.Rotation
			cl:SetAttribute("HexGen", true) cl.Parent = roof N.telhas += 1
		end
		H.collider("hx_f2_torre_" .. id, Vector3.new(18.6, 34, 18.6), Ft * CFrame.new(0, 16.5, 0))
		m:SetAttribute("HexGen", true) N.torres += 1
	end

	-- G) WALL AND SEAL COLLIDERS, H) FORGE STAIR RAMP
	H.collider("hx_f2_muro_F_a", Vector3.new(34, 20, 5), H.faceCF("F", 63, 0, 9.5))
	H.collider("hx_f2_muro_F_b", Vector3.new(34, 20, 5), H.faceCF("F", -63, 0, 9.5))
	H.collider("hx_f2_muro_B_a", Vector3.new(16.5, 20, 5), H.faceCF("B", 71.75, 0, 9.5))
	H.collider("hx_f2_muro_B_b", Vector3.new(16.5, 20, 5), H.faceCF("B", -71.75, 0, 9.5))
	for _, f in ipairs({"FL", "BL", "BR", "FR"}) do H.collider("hx_f2_muro_" .. f, Vector3.new(160, 20, 5), H.faceCF(f, 0, 0, 9.5)) end
	H.collider("hx_f2_forja_costas", Vector3.new(128, 30, 2), CFrame.new(0, 15, -153.1))
	H.ramp("hx_f2_forja_rampa", Vector3.new(0, 4.99, -77.8), 49.2, 9.98, 25.0, Vector3.new(0, 0, 1))
	-- seam seals: the two inner paving wedges on each side meet exactly on Z=0 (X 57.7..115.5); a ray or a
	-- floor probe that lands exactly on that zero-width edge misses both, so an invisible 0.4-wide strip (top 0) closes it
	for _, sx in ipairs({1, -1}) do H.collider(sx > 0 and "hx_f2_costura_E" or "hx_f2_costura_W", Vector3.new(A100 + 0.2, 1, 0.4), CFrame.new(sx * 1.5 * A100, -0.5, 0)) end

	-- I) LaminaDagua mirrored from CF0
	for _, w in ipairs(LAM) do w.CFrame = mirrorCF(H.cf0(w)) end

	-- wedge check on EVERY wedge built above (paving, rings, outside corners)
	local failed = {}
	for _, W in ipairs(WEDGES) do if not H.checkTri(W.w, W.C, W.a, W.la, W.b, W.lb, W.top) then table.insert(failed, W.w.Name .. v3s(W.w.Position)) end end
	N.wedges, N.wedgeFail = #WEDGES, #failed
	if #failed > 0 then error(("wedge check failed on %d of %d wedges, e.g. %s"):format(#failed, #WEDGES, failed[1])) end
	if N.piso ~= 29 then error(("paving has %d parts (expected 29)"):format(N.piso)) end
	if N.muros ~= 84 then error(("walls: %d segments (expected 84)"):format(N.muros)) end
	if N.telhas ~= 6 * 17 then error(("tower roofs: %d tiles (expected 102)"):format(N.telhas)) end

	HC:SetAttribute("PavingMaterial", PAV_MAT.Name) HC:SetAttribute("SecondaryRings", SECONDARY)
	L:SetAttribute("HEX_F2_OK", true)
end

local rec = H.begin("HEX F2 perimeter and ground")
local ok, err = pcall(build)
H.rightTri = rawTri
if ok then H.commit(rec)
else
	if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Cancel) end
	error("F2 failed after writes began; the recording was CANCELLED (writes reverted): " .. tostring(err))
end

------------------------------------------------------------------ verify (read-only)
local v, allOK = {}, true
local function chk(cond, msg) table.insert(v, (cond and "PASS " or "FAIL ") .. msg) if not cond then allOK = false end return cond end

-- walls: 84, each on its face centre line
local nSeg, off = 0, 0
for _, fo in ipairs(HM:GetChildren()) do if fo.Name:sub(1, 5) == "Muro_" then
	for _, s in ipairs(fo:GetChildren()) do nSeg += 1 local n = H.FACES[s:GetAttribute("Face")].n
		off = math.max(off, math.abs(s.Position:Dot(n) - 150)) end end end
chk(nSeg == 84 and off < 0.5, ("84 wall segments on the face centre lines: %d, max |p.n-150| = %.3f"):format(nSeg, off))
-- towers + roof fit
local tw = {}
for _, m in ipairs(HM:GetChildren()) do if m.Name:sub(1, 6) == "Torre_" then
	local body = m:FindFirstChild("Corpo_alto") local Ft = body.CFrame - body.CFrame.Position + Vector3.new(body.Position.X, 0, body.Position.Z)
	local mn, mx = Vector3.new(1e9, 1e9, 1e9), Vector3.new(-1e9, -1e9, -1e9)
	for _, t in ipairs(m.Telhado:GetChildren()) do for _, x in ipairs({-1, 1}) do for _, y in ipairs({-1, 1}) do for _, z in ipairs({-1, 1}) do
		local w = Ft:PointToObjectSpace(t.CFrame:PointToWorldSpace(Vector3.new(x * t.Size.X / 2, y * t.Size.Y / 2, z * t.Size.Z / 2)))
		mn = mn:Min(w) mx = mx:Max(w) end end end end
	local d = mx - mn
	table.insert(tw, ("%s roof %.1fx%.1f (body 18x13, overhang %.1f/%.1f), Y %.2f..%.2f, %d tiles"):format(m.Name, d.X, d.Z, (d.X - 18) / 2, (d.Z - 13) / 2,
		mn.Y, mx.Y, #m.Telhado:GetChildren()))
end end
chk(#tw == 6, ("6 towers with fitted hip roofs: %d"):format(#tw))
-- colliders
local cols = {} for _, c in ipairs(H.COL:GetChildren()) do if c.Name:sub(1, 6) == "hx_f2_" then table.insert(cols, c.Name) end end table.sort(cols)
chk(#cols == 18, ("hx_f2_ colliders: %d (expected 18: 8 walls, 6 towers, forge back seal, forge ramp, 2 seam seals)"):format(#cols))
-- rectangle remnants
local rem = {}
for _, c in ipairs(H.COL:GetChildren()) do for _, n in ipairs({"limite_", "muralha", "chao_", "patio", "via", "lago_fundo", "ponte"}) do
	if c.Name:sub(1, #n) == n then table.insert(rem, "Colisao." .. c.Name) end end end
for _, d in ipairs(workspace:GetDescendants()) do if d.Name == "KIT_muro_seg" or d.Name == "KIT_muro_torre" or d.Name == "LOB_chao" or d.Name:sub(1, 10) == "PATIO_piso" then
	table.insert(rem, d:GetFullName()) end end
if BASE.Size.Z > 100 then table.insert(rem, "ChaoSimples.Base.Base is still the full rectangle") end
chk(#rem == 0, "no rectangle remnant in walls, colliders or floor" .. (#rem > 0 and (": " .. table.concat(rem, ", ", 1, math.min(#rem, 6))) or ""))
-- nothing inside the hexagon below the paving (the pond water must never be covered)
local NF = {} for _, f in ipairs(FACE_ORDER) do table.insert(NF, H.FACES[f].n) end
local function apo(x, z) local m = -1e9 for _, n in ipairs(NF) do m = math.max(m, n.X * x + n.Z * z) end return m end
local under = {}
for _, d in ipairs(workspace:GetDescendants()) do
	if d:IsA("BasePart") and d ~= workspace.Terrain and d.Transparency < 1 and not d:IsDescendantOf(HC) then
		local cf, sz = d.CFrame, d.Size
		local top = d.Position.Y + (math.abs(cf.RightVector.Y) * sz.X + math.abs(cf.UpVector.Y) * sz.Y + math.abs(cf.LookVector.Y) * sz.Z) / 2
		if d.Position.Y < -0.3 and top > -3 and top < -0.05 and apo(d.Position.X, d.Position.Z) < 140 and math.abs(cf.UpVector.Y) > 0.99 and sz.X > 20 and sz.Z > 20 then
			table.insert(under, d:GetFullName()) end end end
chk(#under == 0, "no wide plate with its top between -3 and 0 inside the hexagon" .. (#under > 0 and (": " .. table.concat(under, ", ")) or ""))
-- LaminaDagua next to the cascades
local lam = {}
for _, w in ipairs(LAM) do local best = math.huge for _, c in ipairs(CAS) do local p = casPos(c) best = math.min(best, (Vector2.new(p.X, p.Z) - Vector2.new(w.Position.X, w.Position.Z)).Magnitude) end
	table.insert(lam, ("(%g,%g) %.1f"):format(w.Position.X, w.Position.Z, best)) if best > 12 then allOK = false end end
chk(true, "LaminaDagua mirrored, distance to nearest cascade: " .. table.concat(lam, "; "))
-- pillars
local pil = {} for _, q in ipairs(PIL) do table.insert(pil, v3s(q[1].Position) .. " h" .. q[1].Size.Y) end
chk(true, "KIT_muro_pilar: " .. table.concat(pil, " "))

-- walkability grid (4 studs, apothem < 146, RespectCanCollide), pond holes reported separately
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances = {} rp.RespectCanCollide = true
local holes = {}
for k, Pd in pairs(H.LAY.PONDS) do holes[k] = {cf = H.faceCF(Pd.face, (Pd.s1 + Pd.s2) / 2, (Pd.d1 + Pd.d2) / 2, 0), hx = (Pd.s2 - Pd.s1) / 2 + 0.05, hz = (Pd.d2 - Pd.d1) / 2 + 0.05} end
local function inHole(x, z) for k, h in pairs(holes) do local o = h.cf:PointToObjectSpace(Vector3.new(x, 0, z))
	if math.abs(o.X) < h.hx and math.abs(o.Z) < h.hz then return k end end end
local hist, miss, holeHit, holeMiss, total = {}, {}, {}, {FL = 0, FR = 0}, 0
for x = -168, 168, 4 do for z = -148, 148, 4 do if apo(x, z) < 146 then total += 1
	local hk = inHole(x, z)
	local r = workspace:Raycast(Vector3.new(x, 60, z), Vector3.new(0, -100, 0), rp)
	if hk then if r then table.insert(holeHit, ("%s(%d,%d)->%s %.2f"):format(hk, x, z, r.Instance.Name, r.Position.Y)) else holeMiss[hk] += 1 end
	elseif not r then table.insert(miss, ("(%d,%d)"):format(x, z))
	else local key = ("%.2f"):format(r.Position.Y) local e = hist[key] if not e then e = {n = 0, ex = r.Instance.Name} hist[key] = e end e.n += 1 end
end end end
local hl = {} for k, e in pairs(hist) do table.insert(hl, {k = k, n = e.n, ex = e.ex}) end table.sort(hl, function(a, b) return a.n > b.n end)
local hs = {} for i = 1, math.min(#hl, 22) do table.insert(hs, ("%s:%d[%s]"):format(hl[i].k, hl[i].n, hl[i].ex)) end
chk(#miss == 0, ("walkability grid: %d points, %d misses outside the pond holes %s"):format(total, #miss, table.concat(miss, " ", 1, math.min(#miss, 10))))
table.insert(v, "     hit heights: " .. table.concat(hs, "  "))
table.insert(v, ("     pond holes (pending F6): FL %d misses, FR %d misses, %d hits %s"):format(holeMiss.FL, holeMiss.FR, #holeHit,
	table.concat(holeHit, " ", 1, math.min(#holeHit, 8))))

-- near-coplanar scan over HEX_Chao (true polygon overlap, tops closer than 0.10)
local function footprint(p)
	local cf, sz = p.CFrame, p.Size local ax = {cf.RightVector, cf.UpVector, -cf.LookVector} local s = {sz.X, sz.Y, sz.Z}
	local vi for i = 1, 3 do if math.abs(ax[i].Y) > 0.999 then vi = i end end
	if not vi then return nil end
	local top = cf.Position.Y + s[vi] / 2 local pts = {}
	if p:IsA("WedgePart") then
		if vi ~= 1 then return nil end
		for _, q in ipairs({{-1, -1}, {-1, 1}, {1, 1}}) do local w = cf:PointToWorldSpace(Vector3.new(0, q[1] * sz.Y / 2, q[2] * sz.Z / 2)) table.insert(pts, Vector2.new(w.X, w.Z)) end
	elseif p:IsA("Part") and p.Shape == Enum.PartType.Cylinder then
		local r = sz.Y / 2 for k = 0, 7 do local a = k * math.pi / 4 table.insert(pts, Vector2.new(cf.X + r * math.cos(a), cf.Z + r * math.sin(a))) end
	else
		local o = {} for i = 1, 3 do if i ~= vi then table.insert(o, i) end end
		local e1, e2 = ax[o[1]] * s[o[1]] / 2, ax[o[2]] * s[o[2]] / 2
		for _, q in ipairs({{1, 1}, {1, -1}, {-1, -1}, {-1, 1}}) do local w = cf.Position + e1 * q[1] + e2 * q[2] table.insert(pts, Vector2.new(w.X, w.Z)) end
	end
	local a = 0 for i = 1, #pts do local p1, q1 = pts[i], pts[i % #pts + 1] a += p1.X * q1.Y - q1.X * p1.Y end
	if a < 0 then local rv = {} for i = #pts, 1, -1 do table.insert(rv, pts[i]) end pts = rv end
	local mn, mx = Vector2.new(1e9, 1e9), Vector2.new(-1e9, -1e9) for _, q in ipairs(pts) do mn = mn:Min(q) mx = mx:Max(q) end
	return {pts = pts, top = top, mn = mn, mx = mx, p = p}
end
local function clipArea(S, Cp)
	local out = S
	for i = 1, #Cp do if #out == 0 then break end
		local A, B = Cp[i], Cp[i % #Cp + 1] local inp = out out = {}
		local function sd(p) return (B.X - A.X) * (p.Y - A.Y) - (B.Y - A.Y) * (p.X - A.X) end
		for j = 1, #inp do local P1, Q1 = inp[j], inp[j % #inp + 1] local dp, dq = sd(P1), sd(Q1)
			if dp >= 0 and dq >= 0 then table.insert(out, Q1)
			elseif dp >= 0 and dq < 0 then table.insert(out, P1 + (Q1 - P1) * (dp / (dp - dq)))
			elseif dp < 0 and dq >= 0 then table.insert(out, P1 + (Q1 - P1) * (dp / (dp - dq))) table.insert(out, Q1) end end
	end
	local a = 0 for i = 1, #out do local p1, q1 = out[i], out[i % #out + 1] a += p1.X * q1.Y - q1.X * p1.Y end return math.abs(a) / 2
end
local FP, skipped = {}, 0
for _, d in ipairs(HC:GetDescendants()) do if d:IsA("BasePart") then local f = footprint(d) if f then table.insert(FP, f) else skipped += 1 end end end
local pairsBad = {}
for i = 1, #FP do local a = FP[i] for j = i + 1, #FP do local b = FP[j]
	if math.abs(a.top - b.top) < 0.099 and a.mx.X > b.mn.X and b.mx.X > a.mn.X and a.mx.Y > b.mn.Y and b.mx.Y > a.mn.Y then
		local ar = clipArea(a.pts, b.pts)
		if ar > 0.25 then table.insert(pairsBad, ("%s/%s %.2f@%.2f"):format(a.p.Name, b.p.Name, ar, a.top)) end end end end
chk(#pairsBad == 0, ("near-coplanar scan over HEX_Chao: %d parts, %d overlapping pairs with tops < 0.10 apart %s"):format(#FP, #pairsBad,
	table.concat(pairsBad, " ", 1, math.min(#pairsBad, 8))) .. (skipped > 0 and (" (skipped " .. skipped .. ")") or ""))
-- duplicates inside the new folders
local dups, seen = 0, {}
for _, root in ipairs({HC, HM}) do for _, d in ipairs(root:GetDescendants()) do if d:IsA("BasePart") then
	local lk, up = d.CFrame.LookVector, d.CFrame.UpVector
	local key = d.Name .. ("|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f"):format(d.Position.X, d.Position.Y, d.Position.Z, d.Size.X, d.Size.Y, d.Size.Z)
		.. ("|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f"):format(lk.X, lk.Y, lk.Z, up.X, up.Y, up.Z)
	if seen[key] then dups += 1 end seen[key] = true end end end
chk(dups == 0, ("duplicate scan over HEX_Chao/HEX_Muralha: %d"):format(dups))
-- things that must keep working
local portals = {} for i = 1, 6 do local m = workspace.Santuario:FindFirstChild("Portal" .. i) local d = m and m:FindFirstChild("Disco", true)
	table.insert(portals, (d and d:GetAttribute("AreaId") == i) and ("P" .. i .. "ok") or ("P" .. i .. "BAD")) end
chk(not table.concat(portals, ""):find("BAD"), "portals Disco/AreaId: " .. table.concat(portals, " "))
local pad = workspace:FindFirstChild("LojaMochilas") and workspace.LojaMochilas:FindFirstChild("PadLoja")
local pr = workspace:FindFirstChild("MailBox") and workspace.MailBox:FindFirstChildWhichIsA("ProximityPrompt", true)
chk(pad ~= nil and pad.CanTouch and pr ~= nil and pr.Enabled, "PadLoja present (CanTouch) and MailBox ProximityPrompt enabled")
local ib, is = workspace.NPCs.Ignis:GetBoundingBox() local bb, bs = H.SS.BACKUP_LOBBY_PRE_HEX.Ignis:GetBoundingBox()
chk((ib.Position - bb.Position).Magnitude < 1e-3 and (is - bs).Magnitude < 1e-3, "NPCs.Ignis unchanged vs backup")
local LA = workspace.Corredores.Lobby_Area1 local drift = 0
for _, n in ipairs({"Estrada", "RampaArea1", "RampaPatamar"}) do local c = LA:FindFirstChild(n) if not c or (c.Position - c:GetAttribute("CF0").Position).Magnitude > 1e-3 or not c.CanCollide then drift += 1 end end
chk(drift == 0, "exit walk colliders Estrada/RampaArea1/RampaPatamar unchanged")

say(("F2 %s: SIGN %d, paving %d parts (+ gate apron) material %s%s, overlays %d, medallion %d, joints %d, outside ground %d + Base.Base, walls %d, towers %d (%d roof tiles), wedges %d checked / %d failed")
	:format(allOK and "OK" or "VERIFY FAILED", SIGN, N.piso, PAV_MAT.Name, SECONDARY and " + secondary rings" or "", N.faixas, N.medalhao, N.juntas, N.fora,
		N.muros, N.torres, N.telhas, N.wedges, N.wedgeFail))
say(("  gate TEL_G template Y %.2f..%.2f (expected 30.91..43.93)"):format(tplMin, tplMax))
for _, s in ipairs(v) do say("  " .. s) end
for _, s in ipairs(tw) do say("  " .. s) end
say("  colliders: " .. table.concat(cols, ","))
return table.concat(rep, "\n")
