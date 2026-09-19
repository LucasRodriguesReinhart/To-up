-- blockout.lua - BLOCKOUT (etapa 4) do lobby "Seita da Forja Celeste" em Parts, para validar composicao,
-- niveis, circulacao e leitura. Nao e arte final: volumes com cor-codigo da paleta. Rodar via execute_luau (Edit).
-- Coordenadas Roblox: -Z = Forja (norte do complexo), +Z = Grande Portao / saida para o corredor (z 178).
local ROOT = workspace:FindFirstChild("MURIM_BLOCKOUT"); if ROOT then ROOT:Destroy() end
ROOT = Instance.new("Folder"); ROOT.Name = "MURIM_BLOCKOUT"; ROOT.Parent = workspace
local function C(h) return Color3.fromHex(h) end
local COL = {
	verm = C("B8321E"), vermS = C("7E2014"), ouro = C("E0A83A"), bronze = C("8C6A2E"), mad = C("4A2E1E"), madM = C("7A4B2A"),
	pedra = C("DCCDB0"), piso = C("B9AD95"), junta = C("8F846E"), muralha = C("A89B84"), telha = C("2E5A4C"), telhaImp = C("D4A034"),
	ferro = C("2B2624"), brasa = C("FF7A1A"), chama = C("FFC84A"), pinho = C("3E6B3A"), folha = C("6E9A45"), bordo = C("C4432B"),
	bambu = C("7FA85A"), agua = C("3FA0A0"), leito = C("2A6C6A"), grama = C("4F7A3C"), rocha = C("8A8272"), rochaE = C("6E6658"),
	areia = C("C9B27A"), aco = C("D8DEE6"), palha = C("C9A86A"), cascata = C("DDF3F3"),
}
local FOLD = {}
local function F(n) if not FOLD[n] then local f = Instance.new("Folder"); f.Name = n; f.Parent = ROOT; FOLD[n] = f end return FOLD[n] end
local function mk(cls, name, size, cf, color, folder, props)
	local p = Instance.new(cls); p.Name = name; p.Size = size; p.CFrame = cf; p.Anchored = true; p.Color = color
	p.Material = Enum.Material.SmoothPlastic; p.TopSurface = Enum.SurfaceType.Smooth; p.BottomSurface = Enum.SurfaceType.Smooth
	if props then for k, v in pairs(props) do p[k] = v end end
	p.Parent = folder or ROOT; return p
end
local function box(name, x0, x1, y0, y1, z0, z1, color, folder, props)
	return mk("Part", name, Vector3.new(x1 - x0, y1 - y0, z1 - z0), CFrame.new((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), color, folder, props)
end
local function cyl(name, x, z, y0, y1, r, color, folder, props)
	local p = mk("Part", name, Vector3.new(y1 - y0, 2 * r, 2 * r), CFrame.new(x, (y0 + y1) / 2, z) * CFrame.Angles(0, 0, math.pi / 2), color, folder, props)
	p.Shape = Enum.PartType.Cylinder; return p
end
local function ball(name, x, y, z, r, color, folder, props)
	local p = mk("Part", name, Vector3.new(2 * r, 2 * r, 2 * r), CFrame.new(x, y, z), color, folder, props); p.Shape = Enum.PartType.Ball; return p
end
-- telhado de 4 aguas (wudian): w em x, d em z; a = avanco horizontal; topo = (w-2a) x (d-2a) (ridge se d-2a = 0)
local function hip_roof(name, cx, cz, w, d, ybot, h, a, color, folder, ridgeColor)
	local tw, td = w - 2 * a, d - 2 * a
	if tw > 0.05 then
		mk("WedgePart", name .. "_S", Vector3.new(tw, h, a), CFrame.new(cx, ybot + h / 2, cz + d / 2 - a / 2) * CFrame.Angles(0, math.pi, 0), color, folder)
		mk("WedgePart", name .. "_N", Vector3.new(tw, h, a), CFrame.new(cx, ybot + h / 2, cz - d / 2 + a / 2), color, folder)
	end
	if td > 0.05 then
		mk("WedgePart", name .. "_E", Vector3.new(td, h, a), CFrame.new(cx + w / 2 - a / 2, ybot + h / 2, cz) * CFrame.Angles(0, -math.pi / 2, 0), color, folder)
		mk("WedgePart", name .. "_W", Vector3.new(td, h, a), CFrame.new(cx - w / 2 + a / 2, ybot + h / 2, cz) * CFrame.Angles(0, math.pi / 2, 0), color, folder)
	end
	for _, c in ipairs({ { 1, 1, math.pi / 2 }, { -1, 1, 0 }, { -1, -1, 3 * math.pi / 2 }, { 1, -1, math.pi } }) do
		mk("CornerWedgePart", name .. "_C", Vector3.new(a, h, a), CFrame.new(cx + c[1] * (w / 2 - a / 2), ybot + h / 2, cz + c[2] * (d / 2 - a / 2)) * CFrame.Angles(0, c[3], 0), color, folder)
	end
	if tw > 0.05 and td > 0.05 then box(name .. "_topo", cx - tw / 2, cx + tw / 2, ybot + h - 0.6, ybot + h, cz - td / 2, cz + td / 2, color, folder) end
	-- beiral com espessura (fascia)
	local t = 1.1
	box(name .. "_fS", cx - w / 2, cx + w / 2, ybot - t, ybot + 0.05, cz + d / 2 - 1.2, cz + d / 2, color, folder)
	box(name .. "_fN", cx - w / 2, cx + w / 2, ybot - t, ybot + 0.05, cz - d / 2, cz - d / 2 + 1.2, color, folder)
	box(name .. "_fE", cx + w / 2 - 1.2, cx + w / 2, ybot - t, ybot + 0.05, cz - d / 2, cz + d / 2, color, folder)
	box(name .. "_fW", cx - w / 2, cx - w / 2 + 1.2, ybot - t, ybot + 0.05, cz - d / 2, cz + d / 2, color, folder)
	-- cumeeira
	local rc = ridgeColor or COL.ouro
	if td <= 0.05 and tw > 0.05 then
		box(name .. "_cume", cx - tw / 2 - 1.5, cx + tw / 2 + 1.5, ybot + h - 0.5, ybot + h + 1.2, cz - 1, cz + 1, rc, folder)
		box(name .. "_chiwen", cx - tw / 2 - 2.2, cx - tw / 2 - 0.2, ybot + h, ybot + h + 4, cz - 1.1, cz + 1.1, rc, folder)
		box(name .. "_chiwen", cx + tw / 2 + 0.2, cx + tw / 2 + 2.2, ybot + h, ybot + h + 4, cz - 1.1, cz + 1.1, rc, folder)
	elseif tw <= 0.05 and td > 0.05 then
		box(name .. "_cume", cx - 1, cx + 1, ybot + h - 0.5, ybot + h + 1.2, cz - td / 2 - 1.5, cz + td / 2 + 1.5, rc, folder)
	elseif tw <= 0.05 and td <= 0.05 then
		box(name .. "_pinaculo", cx - 0.8, cx + 0.8, ybot + h - 0.3, ybot + h + 2.5, cz - 0.8, cz + 0.8, rc, folder)
	end
end
local function stairs_z(name, x0, x1, zStart, dir, y0, n, rise, tread, color, folder)
	for i = 0, n - 1 do
		local za, zb = zStart + dir * i * tread, zStart + dir * (i + 1) * tread
		box(name .. i, x0, x1, y0 - 1, y0 + (i + 1) * rise, math.min(za, zb), math.max(za, zb), color, folder)
	end
end
local function stairs_x(name, z0, z1, xStart, dir, y0, n, rise, tread, color, folder)
	for i = 0, n - 1 do
		local xa, xb = xStart + dir * i * tread, xStart + dir * (i + 1) * tread
		box(name .. i, math.min(xa, xb), math.max(xa, xb), y0 - 1, y0 + (i + 1) * rise, z0, z1, color, folder)
	end
end
local function bal(name, x0, x1, z0, z1, y, folder)  -- balaustrada (murete + corrimao + postes)
	local ax = (x1 - x0) >= (z1 - z0)
	box(name .. "_mur", x0, x1, y, y + 1.0, z0, z1, COL.pedra, folder)
	if ax then box(name .. "_rail", x0, x1, y + 2.6, y + 3.2, (z0 + z1) / 2 - 0.5, (z0 + z1) / 2 + 0.5, COL.pedra, folder)
	else box(name .. "_rail", (x0 + x1) / 2 - 0.5, (x0 + x1) / 2 + 0.5, y + 2.6, y + 3.2, z0, z1, COL.pedra, folder) end
	local L = ax and (x1 - x0) or (z1 - z0); local n = math.max(1, math.floor(L / 6))
	for i = 0, n do
		local t = n > 0 and i / n or 0
		local px = ax and (x0 + 0.5 + t * (L - 1)) or (x0 + x1) / 2
		local pz = ax and (z0 + z1) / 2 or (z0 + 0.5 + t * (L - 1))
		box(name .. "_post", px - 0.55, px + 0.55, y + 1, y + 3.6, pz - 0.55, pz + 0.55, COL.pedra, folder)
	end
end
local function pine(x, z, y, h, s, folder)
	s = s or 1
	cyl("pinho_tronco", x, z, y, y + h * 0.45, 0.7 * s, COL.madM, folder)
	for i, r in ipairs({ 5.5, 4.2, 3.0, 1.8 }) do
		local yy = y + h * (0.28 + 0.2 * (i - 1))
		cyl("pinho_copa", x, z, yy, yy + h * 0.13, r * s, COL.pinho, folder)
	end
end
local function maple(x, z, y, folder)
	cyl("bordo_tronco", x, z, y, y + 6, 0.7, COL.madM, folder)
	ball("bordo_copa", x, y + 9, z, 5.5, COL.bordo, folder); ball("bordo_copa", x + 2.5, y + 7.5, z + 1.5, 3.5, COL.bordo, folder)
end
local function rock(x, y, z, sx, sy, sz, ry, rx, folder)
	mk("Part", "rocha", Vector3.new(sx, sy, sz), CFrame.new(x, y, z) * CFrame.Angles(rx or 0, ry or 0, 0), COL.rocha, folder)
end
local function lantern_post(x, z, y, folder)
	cyl("lant_poste", x, z, y, y + 7, 0.45, COL.mad, folder)
	box("lant_caixa", x - 1, x + 1, y + 7, y + 9.6, z - 1, z + 1, COL.chama, folder, { Material = Enum.Material.Neon })
	box("lant_tampa", x - 1.4, x + 1.4, y + 9.6, y + 10.2, z - 1.4, z + 1.4, COL.telha, folder)
end
local function lion(x, z, y, dir, folder)
	box("leao_corpo", x - 2, x + 2, y, y + 4.5, z - 3.5, z + 3.5, COL.junta, folder)
	box("leao_cabeca", x - 2, x + 2, y + 4.5, y + 7.5, z + dir * 1.2 - 2, z + dir * 1.2 + 2, COL.junta, folder)
	box("leao_base", x - 2.6, x + 2.6, y - 0.2, y + 0.6, z - 4.1, z + 4.1, COL.pedra, folder)
end
local function sword(x, z, y, h, folder)  -- espada fincada: lamina de y ate y+h*0.7, guarda, punho, pomo
	local hb = h * 0.7
	box("esp_lamina", x - h * 0.06, x + h * 0.06, y, y + hb, z - 0.3, z + 0.3, COL.aco, folder)
	box("esp_guarda", x - h * 0.22, x + h * 0.22, y + hb, y + hb + h * 0.06, z - 0.6, z + 0.6, COL.ouro, folder)
	box("esp_punho", x - h * 0.035, x + h * 0.035, y + hb + h * 0.06, y + hb + h * 0.24, z - h * 0.035, z + h * 0.035, COL.mad, folder)
	ball("esp_pomo", x, y + hb + h * 0.27, z, h * 0.05, COL.ouro, folder)
end

---------------------------------------------------------------- TERRENO
local T = F("Terreno")
box("grama_W", -170, 70, -6, -0.2, -210, 180, COL.grama, T)
box("grama_E", 100, 170, -6, -0.2, -210, 180, COL.grama, T)
box("grama_E2", 70, 100, -6, -0.2, -210, -150, COL.grama, T)
box("grama_E3", 70, 84, -6, -0.2, -150, -70, COL.grama, T); box("grama_E4", 94, 100, -6, -0.2, -150, -70, COL.grama, T)
box("grama_E5", 70, 100, -6, -0.2, 130, 180, COL.grama, T)
-- lago de jade + riacho
box("lago_leito", 70, 100, -5, -4, -70, 130, COL.leito, T)
box("lago_agua", 70, 100, -4, -1.5, -70, 130, COL.agua, T, { Material = Enum.Material.Glass, Transparency = 0.35, CanCollide = false })
box("riacho_leito", 84, 94, -5, -4, -150, -70, COL.leito, T)
box("riacho_agua", 84, 94, -4, -1.2, -150, -70, COL.agua, T, { Material = Enum.Material.Glass, Transparency = 0.35, CanCollide = false })
box("lago_borda_W", 68.8, 70.4, -0.3, 0.6, -70.8, 130.8, COL.pedra, T); box("lago_borda_E", 99.6, 101.2, -0.3, 0.6, -70.8, 130.8, COL.pedra, T)
box("lago_borda_N", 68.8, 101.2, -0.3, 0.6, -70.8, -69.2, COL.pedra, T); box("lago_borda_S", 68.8, 101.2, -0.3, 0.6, 129.2, 130.8, COL.pedra, T)
box("riacho_ponte", 82, 96, -0.4, 0.6, -116, -108, COL.pedra, T)

---------------------------------------------------------------- PATIO CENTRAL + ALTAR DA ESPADA
local P = F("Patio")
box("patio_N", -70, 70, -0.5, 0, -60, -23, COL.piso, P); box("patio_S", -70, 70, -0.5, 0, 23, 60, COL.piso, P)
box("patio_W", -70, -23, -0.5, 0, -23, 23, COL.piso, P); box("patio_E", 23, 70, -0.5, 0, -23, 23, COL.piso, P)
local L = 23 - 23 * math.tan(math.rad(22.5))
for _, c in ipairs({ { 1, 1, 0 }, { -1, 1, -math.pi / 2 }, { -1, -1, math.pi }, { 1, -1, math.pi / 2 } }) do
	mk("WedgePart", "patio_canto", Vector3.new(0.5, L, L), CFrame.new(c[1] * (23 - L / 2), -0.25, c[2] * (23 - L / 2)) * CFrame.Angles(0, c[3], 0) * CFrame.Angles(0, 0, math.pi / 2), COL.piso, P)
end
cyl("altar_fundo", 0, 0, -4, -3.5, 25, COL.leito, P)
cyl("altar_agua", 0, 0, -3.5, -1, 25, COL.agua, P, { Material = Enum.Material.Glass, Transparency = 0.35, CanCollide = false })
cyl("altar_estrado", 0, 0, -3.5, 2.5, 13, COL.pedra, P)
cyl("altar_degrau", 0, 0, 2.5, 3.2, 10, COL.piso, P)
for k = 0, 7 do
	local phi = k * math.pi / 4
	mk("Part", "altar_meiofio", Vector3.new(19.6, 1.2, 1.2), CFrame.new(23.6 * math.cos(phi), 0.3, 23.6 * math.sin(phi)) * CFrame.Angles(0, phi + math.pi / 2, 0), COL.pedra, P)
end
box("altar_ponte_E", 12.5, 24.5, -1.1, 0.4, -4, 4, COL.pedra, P); box("altar_ponte_W", -24.5, -12.5, -1.1, 0.4, -4, 4, COL.pedra, P)
box("altar_ponte_S", -4, 4, -1.1, 0.4, 12.5, 24.5, COL.pedra, P); box("altar_ponte_N", -4, 4, -1.1, 0.4, -24.5, -12.5, COL.pedra, P)
box("altar_pedestal", -4, 4, 3.2, 7.2, -4, 4, COL.pedra, P); box("altar_pedestal_topo", -3.2, 3.2, 7.2, 8, -3.2, 3.2, COL.ouro, P)
sword(0, 0, 7.8, 25, P)
for _, s in ipairs({ { 1, 1 }, { -1, 1 }, { -1, -1 }, { 1, -1 } }) do
	local bx, bz = s[1] * 7.4, s[2] * 7.4
	cyl("braseiro", bx, bz, 3.2, 5.6, 1.7, COL.bronze, P)
	cyl("braseiro_fogo", bx, bz, 5.6, 7.2, 1.2, COL.brasa, P, { Material = Enum.Material.Neon })
end

---------------------------------------------------------------- ESCADARIA MONUMENTAL + SPAWN
local E = F("Escadaria")
stairs_z("esc_W", -23, -5, -60, -1, 0, 12, 10 / 12, 2.5, COL.pedra, E)
stairs_z("esc_E", 5, 23, -60, -1, 0, 12, 10 / 12, 2.5, COL.pedra, E)
mk("WedgePart", "danbi", Vector3.new(10, 10, 30), CFrame.new(0, 5, -75) * CFrame.Angles(0, math.pi, 0), COL.piso, E)
box("danbi_relevo", -3.5, 3.5, 9.9, 10.3, -89.5, -80, COL.ouro, E)  -- marca do relevo (dragao) no topo da rampa
mk("WedgePart", "bochecha_W", Vector3.new(1.5, 11.5, 30), CFrame.new(-23.75, 5.25, -75) * CFrame.Angles(0, math.pi, 0), COL.pedra, E)
mk("WedgePart", "bochecha_E", Vector3.new(1.5, 11.5, 30), CFrame.new(23.75, 5.25, -75) * CFrame.Angles(0, math.pi, 0), COL.pedra, E)
lion(-13, -55, 0, 1, E); lion(13, -55, 0, 1, E)
for _, sx in ipairs({ -1, 1 }) do
	box("pedestal_esp", sx * 30 - 2, sx * 30 + 2, 0, 4, -68, -64, COL.pedra, E); sword(sx * 30, -66, 4, 11, E)
	lantern_post(sx * 36, -62, 0, E)
end
local sp = workspace:FindFirstChild("Mystical Spawn Point"); sp = sp and sp:FindFirstChild("SpawnLobby")
if sp then sp.CFrame = CFrame.lookAt(Vector3.new(0, 0.6, -62), Vector3.new(0, 0.6, -120)) end

---------------------------------------------------------------- TERRACO + SALAO DA FORJA
local Fj = F("Forja")
box("terraco", -62, 62, 0, 10, -152, -90, COL.pedra, Fj)
box("terraco_faixa", -62.2, 62.2, 8.4, 9.2, -152.2, -89.8, COL.junta, Fj)
bal("bal_frente_W", -62, -23.5, -91, -90.2, 10, Fj); bal("bal_frente_E", 23.5, 62, -91, -90.2, 10, Fj)
bal("bal_lado_W", -62, -61.2, -152, -91, 10, Fj); bal("bal_lado_E", 61.2, 62, -152, -91, 10, Fj)
-- salao: x -36..36, z -147..-108 (alpendre aberto z -108..-122)
local CZ = -127.5
for _, x in ipairs({ -35, -27, -17, -7, 7, 17, 27, 35 }) do
	cyl("col_frente", x, -108, 10, 24, 1.25, COL.verm, Fj); cyl("col_base", x, -108, 10, 10.8, 1.7, COL.pedra, Fj)
end
for _, x in ipairs({ -26, -12, 12, 26 }) do
	cyl("col_int", x, -131, 10, 24, 1.1, COL.verm, Fj); cyl("col_int", x, -141, 10, 24, 1.1, COL.verm, Fj)
end
box("parede_fundo", -36, 36, 10, 24, -147, -145, COL.verm, Fj)
box("parede_lado_W", -36, -34, 10, 24, -147, -122, COL.verm, Fj); box("parede_lado_E", 34, 36, 10, 24, -147, -122, COL.verm, Fj)
box("parede_frente_W", -36, -10, 10, 24, -123, -121, COL.verm, Fj); box("parede_frente_E", 10, 36, 10, 24, -123, -121, COL.verm, Fj)
box("verga_porta", -10.5, 10.5, 22, 24, -123.2, -120.8, COL.mad, Fj)
box("viga_frente", -37, 37, 22.6, 24, -109.2, -106.8, COL.mad, Fj)
-- faixa de dougong (blocos sob o beiral)
for _, x in ipairs({ -35, -27, -17, -7, 7, 17, 27, 35 }) do box("dougong", x - 1.6, x + 1.6, 22.4, 24, -105, -101.5, COL.mad, Fj) end
-- telhado duplo dourado
hip_roof("Forja_tel_inf", 0, CZ, 84, 51, 24, 7, 10, COL.telhaImp, Fj)
box("clerestorio", -30, 30, 31, 36, CZ - 13.5, CZ + 13.5, COL.verm, Fj)
hip_roof("Forja_tel_sup", 0, CZ, 74, 41, 36, 10, 20.5, COL.telhaImp, Fj)
-- lareira monumental, Torre do Fogo, fole, bigorna, calha, altar de laminas
box("lareira", -10, 10, 10, 22, -146, -134, COL.ferro, Fj)
box("lareira_boca", -5, 5, 10, 18, -134.3, -133.7, COL.brasa, Fj, { Material = Enum.Material.Neon })
box("lareira_moldura", -11, 11, 21.5, 23, -146.5, -133.5, COL.bronze, Fj)
box("chamine1", -5, 5, 22, 50, -146, -136, COL.ferro, Fj); box("chamine2", -4, 4, 50, 64, -145, -137, COL.ferro, Fj)
box("chamine_anel", -5.4, 5.4, 34, 35.4, -146.4, -135.6, COL.bronze, Fj); box("chamine_anel", -5.4, 5.4, 48, 49.4, -146.4, -135.6, COL.bronze, Fj)
box("chamine_capa", -5.2, 5.2, 64, 66, -146.2, -135.8, COL.bronze, Fj)
box("chamine_brasa", -2.6, 2.6, 66, 67.6, -143.6, -138.4, COL.brasa, Fj, { Material = Enum.Material.Neon })
local pl = Instance.new("PointLight"); pl.Color = COL.brasa; pl.Range = 45; pl.Brightness = 2; pl.Parent = Fj.lareira_boca
box("fole", 14, 21, 10, 15, -140, -128, COL.madM, Fj); box("fole_bico", 10, 14, 12, 13.5, -135, -133, COL.ferro, Fj)
cyl("bigorna_cepo", -8, -128, 10, 12, 1.6, COL.mad, Fj); box("bigorna", -10, -6, 12, 14.2, -130, -126, COL.ferro, Fj)
box("calha", 6, 10, 10, 12.5, -128, -120, COL.mad, Fj); box("calha_agua", 6.3, 9.7, 12.3, 12.5, -127.7, -120.3, COL.agua, Fj, { Material = Enum.Material.Glass, Transparency = 0.3 })
box("altar_laminas", -34, -30, 10, 13, -142, -126, COL.pedra, Fj)
for z = -140, -128, 3 do box("lamina", -32.6, -31.4, 13, 21, z - 0.2, z + 0.2, COL.aco, Fj) end
-- estandartes do salao, incensarios, lanternas do terraco
for _, sx in ipairs({ -1, 1 }) do
	box("estandarte_salao", sx * 22 - 1.6, sx * 22 + 1.6, 14, 23.5, -106.6, -106.2, COL.verm, Fj)
	cyl("ding", sx * 16, -96, 10, 14, 2.6, COL.bronze, Fj); cyl("ding_boca", sx * 16, -96, 14, 14.6, 2.2, COL.ferro, Fj)
	lantern_post(sx * 44, -95, 10, Fj); lantern_post(sx * 58, -120, 10, Fj)
end
-- escadas laterais do terraco (loops leste/oeste)
stairs_x("esc_lat_E", -118, -106, 80, -1, 0, 12, 10 / 12, 1.5, COL.pedra, Fj)
stairs_x("esc_lat_W", -118, -106, -80, 1, 0, 12, 10 / 12, 1.5, COL.pedra, Fj)
-- Ignis de volta ao lugar (pes em y 10, alpendre)
local ig = workspace:FindFirstChild("NPCs") and workspace.NPCs:FindFirstChild("Ignis")
if ig then
	local cf = ig:GetBoundingBox()
	if math.abs(cf.X) > 50 then ig:PivotTo(ig:GetPivot() + Vector3.new(-cf.X, 0, -116 - cf.Z)) end
end

---------------------------------------------------------------- VIA IMPERIAL + GRANDE PORTAO + MURALHA
local G = F("Portao")
box("via", -16, 16, -0.4, 0.15, 60, 140, COL.piso, G)
box("via_faixa", -1.5, 1.5, 0.15, 0.3, 60, 140, COL.pedra, G)
box("soleira", -46, 46, -0.5, 0, 140, 178, COL.piso, G)
for _, z in ipairs({ 72, 92, 112, 132 }) do lantern_post(-20, z, 0, G); lantern_post(20, z, 0, G) end
for _, z in ipairs({ 85, 120 }) do
	for _, sx in ipairs({ -1, 1 }) do
		cyl("estandarte_poste", sx * 26, z, 0, 22, 0.5, COL.mad, G)
		box("estandarte", sx * 26 - 0.15, sx * 26 + 0.15, 8, 20, z + 0.5, z + 4.5, COL.verm, G)
		box("estandarte_emblema", sx * 26 - 0.2, sx * 26 + 0.2, 12, 15, z + 1.5, z + 3.5, COL.ouro, G)
		ball("estandarte_pomo", sx * 26, 22.6, z, 0.7, COL.ouro, G)
	end
end
lion(-17, 134, 0, 1, G); lion(17, 134, 0, 1, G)
-- base do portao (3 passagens: central 22 x 15, laterais 12 x 11)
for _, s in ipairs({ { -46, -29 }, { -17, -11 }, { 11, 17 }, { 29, 46 } }) do box("portao_pilar", s[1], s[2], 0, 16, 140, 160, COL.muralha, G) end
box("portao_verga_C", -11, 11, 15, 16, 140, 160, COL.muralha, G)
box("portao_verga_W", -29, -17, 11, 16, 140, 160, COL.muralha, G); box("portao_verga_E", 17, 29, 11, 16, 140, 160, COL.muralha, G)
for _, s in ipairs({ { -46.2, -28.8 }, { -17.2, -10.8 }, { 10.8, 17.2 }, { 28.8, 46.2 } }) do box("portao_faixa", s[1], s[2], 0, 1.6, 139.8, 160.2, COL.junta, G) end
box("portao_parapeito_S", -46, 46, 16, 18, 140, 141.5, COL.muralha, G); box("portao_parapeito_N", -46, 46, 16, 18, 158.5, 160, COL.muralha, G)
box("portao_parapeito_W", -46, -44.5, 16, 18, 140, 160, COL.muralha, G); box("portao_parapeito_E", 44.5, 46, 16, 18, 140, 160, COL.muralha, G)
for x = -42, 42, 6 do box("ameia", x - 1.5, x + 1.5, 18, 19.6, 140, 141.5, COL.muralha, G) end
-- pavilhao do portao (2 beirais)
box("pav_piso", -32, 32, 16, 17, 143, 157, COL.pedra, G)
box("pav_corpo", -28, 28, 17, 27, 146, 156, COL.verm, G)
for _, x in ipairs({ -28, -17, -6, 6, 17, 28 }) do cyl("pav_col", x, 144, 17, 27, 1.0, COL.verm, G); cyl("pav_col", x, 158, 17, 27, 1.0, COL.verm, G) end
hip_roof("Portao_tel_inf", 0, 151, 70, 26, 27, 5, 8, COL.telha, G)
box("pav_clerestorio", -26, 26, 32, 35, 146, 156, COL.verm, G)
hip_roof("Portao_tel_sup", 0, 151, 60, 22, 35, 7, 11, COL.telha, G)
box("portao_placa", -6, 6, 20, 24, 143.6, 144.2, COL.ouro, G)
-- muralha vermelha com capa de telha + torres de canto
for _, s in ipairs({ { -150, -46 }, { 46, 150 } }) do
	box("muralha", s[1], s[2], 0, 11, 146, 154, COL.verm, G); box("muralha_base", s[1], s[2], 0, 1.6, 145.8, 154.2, COL.junta, G)
	box("muralha_capa", s[1] - 0.5, s[2] + 0.5, 11, 12.6, 145, 155, COL.telha, G)
end
for _, sx in ipairs({ -1, 1 }) do
	box("torre_base", sx * 150 - 7, sx * 150 + 7, 0, 4, 143, 157, COL.muralha, G)
	box("torre_corpo", sx * 150 - 6, sx * 150 + 6, 4, 15, 144, 156, COL.verm, G)
	hip_roof("Torre_canto", sx * 150, 150, 18, 18, 15, 5.5, 9, COL.telha, G)
end
box("muro_E", 150, 154, 0, 12, -70, 146, COL.verm, G); box("muro_E_capa", 149.5, 154.5, 12, 13.5, -70.5, 146.5, COL.telha, G)
box("muro_W", -154, -150, 0, 12, -70, 146, COL.verm, G); box("muro_W_capa", -154.5, -149.5, 12, 13.5, -70.5, 146.5, COL.telha, G)

---------------------------------------------------------------- LESTE: PONTE-LUA + SANTUARIO DOS PORTAIS
local Le = F("Leste")
local N = 8
for i = 0, N - 1 do
	local t0, t1 = i / N, (i + 1) / N
	local x0, x1 = 68 + 34 * t0, 68 + 34 * t1
	local y0, y1 = 4.2 * math.sin(math.pi * t0), 4.2 * math.sin(math.pi * t1)
	local Lg = math.sqrt((x1 - x0) ^ 2 + (y1 - y0) ^ 2); local ang = math.atan2(y1 - y0, x1 - x0)
	local cf = CFrame.new((x0 + x1) / 2, (y0 + y1) / 2 + 0.6, 0) * CFrame.Angles(0, 0, ang)
	mk("Part", "ponte_seg", Vector3.new(Lg + 0.25, 1.2, 8), cf, COL.madM, Le)
	mk("Part", "ponte_guarda", Vector3.new(Lg + 0.25, 2.2, 0.4), cf * CFrame.new(0, 1.7, 3.8), COL.verm, Le, { CanCollide = false })
	mk("Part", "ponte_guarda", Vector3.new(Lg + 0.25, 2.2, 0.4), cf * CFrame.new(0, 1.7, -3.8), COL.verm, Le, { CanCollide = false })
end
box("gal_plat_N", 104, 146, 0, 6.4, -45, -6, COL.pedra, Le); box("gal_plat_S", 104, 146, 0, 6.4, 6, 45, COL.pedra, Le); box("gal_plat_C", 120, 146, 0, 6.4, -6, 6, COL.pedra, Le)
stairs_x("gal_esc", -6, 6, 104, 1, 0, 8, 0.8, 2, COL.pedra, Le)
bal("gal_bal_N", 104, 104.8, -45, -6.5, 6.4, Le); bal("gal_bal_S", 104, 104.8, 6.5, 45, 6.4, Le)
bal("gal_bal_n2", 104, 146, -45, -44.2, 6.4, Le); bal("gal_bal_s2", 104, 146, 44.2, 45, 6.4, Le)
for _, z in ipairs({ -39, -26, -13, 0, 13, 26, 39 }) do
	cyl("gal_col", 109, z, 6.4, 17.4, 1.0, COL.verm, Le); cyl("gal_col", 139, z, 6.4, 17.4, 1.0, COL.verm, Le)
end
box("gal_parede", 143, 146, 6.4, 17.4, -45, 45, COL.verm, Le)
box("gal_viga", 107.5, 110.5, 16, 17.4, -45, 45, COL.mad, Le)
for _, z in ipairs({ -32, -20, -6, 7, 19, 32 }) do box("gal_emblema", 142.6, 143, 9, 15, z - 1.6, z + 1.6, COL.ouro, Le) end
hip_roof("Galeria_tel", 125, 0, 52, 100, 17.4, 10, 26, COL.telha, Le)
for _, p in ipairs({ { 108, 62 }, { 108, 92 }, { 110, 122 }, { 112, -60 }, { 130, -75 }, { 62, -76 } }) do pine(p[1], p[2], -0.2, 22, 1, Le) end
maple(104, 40, -0.2, Le); maple(112, -52, -0.2, Le)
rock(106, 1.5, 78, 7, 4, 5, 0.4, 0.1, Le); rock(118, 2, 110, 9, 5, 6, -0.6, 0, Le)

---------------------------------------------------------------- OESTE: JARDIM, CASA DO INTENDENTE (LOJA), PATIO DE TREINO
local O = F("Oeste")
box("cam_W", -84, -70, -0.1, 0.1, -4, 4, COL.piso, O)
stairs_x("loja_esc", -4, 4, -84, -1, 0, 10, 0.8, 2, COL.pedra, O)
box("loja_plat", -130, -104, 0, 8, -24, 16, COL.pedra, O)
bal("loja_bal_N", -130, -104, -24, -23.2, 8, O); bal("loja_bal_S", -130, -104, 15.2, 16, 8, O)
bal("loja_bal_E1", -104.8, -104, -24, -4.5, 8, O); bal("loja_bal_E2", -104.8, -104, 4.5, 16, 8, O)
box("loja_corpo", -130, -120, 8, 18, -16, 16, COL.verm, O)
box("loja_balcao", -120, -118, 8, 11.5, -8, 8, COL.madM, O)
cyl("loja_col", -119, -14, 8, 18, 0.9, COL.verm, O); cyl("loja_col", -119, 14, 8, 18, 0.9, COL.verm, O)
box("loja_placa", -119.6, -119.2, 14, 17, -4, 4, COL.ouro, O)
hip_roof("Loja_tel", -124, 0, 22, 42, 18, 6, 11, COL.telha, O)
box("cam_W2", -98, -80, -0.1, 0.1, -115, -109, COL.piso, O); box("cam_W3", -98, -94, -0.1, 0.1, -115, -2, COL.piso, O)
-- patio de treino
box("treino_areia", -100, -72, -0.15, 0.1, 20, 56, COL.areia, O)
for x = -92, -80, 6 do for z = 30, 42, 6 do cyl("treino_poste", x, z, 0, 4, 0.5, COL.madM, O) end end
for _, x in ipairs({ -76, -96 }) do cyl("boneco", x, 50, 0, 5.5, 0.9, COL.palha, O); ball("boneco_cabeca", x, 6.4, 50, 1.1, COL.palha, O) end
box("estante", -90, -82, 0, 5, 55, 56, COL.mad, O)
for x = -89, -83, 2 do cyl("lanca", x, 55.5, 1, 9, 0.16, COL.madM, O) end
box("treino_estandarte", -100.15, -99.85, 6, 16, 22, 26, COL.verm, O); cyl("treino_estandarte_poste", -100, 22, 0, 18, 0.4, COL.mad, O)
-- jardim
for _, p in ipairs({ { -80, -40 }, { -96, -54 }, { -84, 12 }, { -100, 70 }, { -80, 90 }, { -96, 120 }, { -120, 30 }, { -135, -40 }, { -62, -76 } }) do pine(p[1], p[2], -0.2, 22, 1, O) end
maple(-76, 66, -0.2, O); maple(-110, 100, -0.2, O); maple(-125, 42, -0.2, O)
rock(-88, 1.5, -30, 8, 4, 6, 0.3, 0, O); rock(-108, 2.5, 76, 10, 6, 7, -0.5, 0.1, O); rock(-74, 1.2, 108, 6, 3, 5, 0.8, 0, O)
for _, z in ipairs({ -50, -20, 30, 70, 110 }) do
	for k = 0, 4 do cyl("bambu", -146 + (k % 3) * 1.1, z + math.floor(k / 3) * 1.2 + k * 0.4, -0.2, 14 + k, 0.3, COL.bambu, O) end
end

---------------------------------------------------------------- NORTE: PENHASCOS + CASCATA
local Nn = F("Norte")
box("penhasco_C", -40, 40, -1, 48, -200, -152, COL.rochaE, Nn)
box("penhasco_E1", 40, 110, -1, 66, -200, -152, COL.rocha, Nn); box("penhasco_W1", -110, -40, -1, 66, -200, -152, COL.rocha, Nn)
box("penhasco_E2", 110, 175, -1, 58, -200, -150, COL.rochaE, Nn); box("penhasco_W2", -175, -110, -1, 58, -200, -150, COL.rochaE, Nn)
box("penhasco_fundo", -175, 175, -1, 84, -240, -200, COL.rocha, Nn)
mk("Part", "penhasco_pico", Vector3.new(40, 60, 30), CFrame.new(-70, 90, -215) * CFrame.Angles(0.2, 0.4, 0.15), COL.rochaE, Nn)
mk("Part", "penhasco_pico", Vector3.new(36, 52, 28), CFrame.new(75, 86, -212) * CFrame.Angles(-0.15, -0.5, 0.1), COL.rochaE, Nn)
box("cascata", 83, 95, -1.2, 40, -152.6, -151, COL.cascata, Nn, { Transparency = 0.15, CanCollide = false })
for _, p in ipairs({ { -60, 66, -165 }, { 60, 66, -168 }, { -100, 66, -175 }, { 100, 66, -180 }, { 0, 48, -178 }, { -140, 58, -170 }, { 140, 58, -175 }, { -25, 48, -190 }, { 30, 48, -192 } }) do
	pine(p[1], p[3], p[2] - 0.2, 24, 1.2, Nn)
end
return "MURIM_BLOCKOUT: " .. #ROOT:GetDescendants() .. " instancias"
