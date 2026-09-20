-- verificar_lobby.lua - confere o lobby por MEDIDA, nao a olho. Roda depois de montar_lobby.lua,
-- portais_limpar.lua, portais_vfx.lua e agua_cartoon.lua.
local Config = require(game:GetService("ReplicatedStorage").Config)
local out = {}
local function L(...) table.insert(out, string.format(...)) end

local lob = workspace:FindFirstChild("LOBBY_MURIM")
if not lob then return "LOBBY_MURIM nao existe" end

-- 1) contagem
local mesh, col, tris, malhas = 0, 0, 0, {}
for _, d in ipairs(lob:GetDescendants()) do
	if d:IsA("MeshPart") then mesh += 1; malhas[d.MeshId] = true
	elseif d:IsA("Part") then col += 1 end
end
local nm = 0; for _ in pairs(malhas) do nm += 1 end
L("1) %d MeshParts a partir de %d malhas distintas, %d Parts de colisao", mesh, nm, col)

-- 2) os seis portais: existe a moldura do tema certo em cima do pad certo?
local sant = workspace:FindFirstChild("Santuario")
local okPortal, faltas = 0, {}
for _, mod in ipairs(sant and sant:GetChildren() or {}) do
	local disco = mod:FindFirstChild("Disco")
	local id = disco and disco:GetAttribute("AreaId")
	local area = id and Config.areaPorId(id)
	if area then
		local alvo, perto = "POR_moldura_" .. area.tema, nil
		for _, d in ipairs(lob:GetDescendants()) do
			if d:IsA("MeshPart") and d.Name == alvo then
				local dz = math.abs(d.Position.Z - disco.Position.Z)
				if dz < 3 then perto = d end
			end
		end
		if perto then
			okPortal += 1
		else
			table.insert(faltas, string.format("%s(area %d/%s)", mod.Name, id, area.tema))
		end
	end
end
L("2) portais com a moldura do tema certo sobre o pad: %d/6%s", okPortal,
	#faltas > 0 and (" | faltando: " .. table.concat(faltas, ", ")) or "")

-- 3) VFX ligado?
local comVfx, emissores = 0, 0
for _, mod in ipairs(sant and sant:GetChildren() or {}) do
	local f = mod:FindFirstChild("VFX_PORTAL")
	if f then
		comVfx += 1
		for _, d in ipairs(f:GetDescendants()) do if d:IsA("ParticleEmitter") then emissores += 1 end end
	end
end
L("3) portais com VFX: %d/6 (%d emissores no total)", comVfx, emissores)

-- 4) portais procedurais antigos ainda em cena?
local sobrando = 0
for _, mod in ipairs(sant and sant:GetChildren() or {}) do
	for _, c in ipairs(mod:GetChildren()) do
		if c.Name ~= "Disco" and c.Name ~= "VFX_PORTAL" then sobrando += 1 end
	end
end
L("4) pecas do portal procedural antigo ainda no Santuario: %d (o esperado e 0)", sobrando)

-- 5) agua
local T = workspace.Terrain
L("5) agua: cor %s, transparencia %.2f, onda %.2f, %d celulas de terreno",
	tostring(T.WaterColor), T.WaterTransparency, T.WaterWaveSize, T:CountCells())

-- 6) circulacao: o chao responde em pontos-chave? (raio para baixo, so na colisao do lobby)
local rp = RaycastParams.new()
rp.FilterType = Enum.RaycastFilterType.Include
rp.FilterDescendantsInstances = { lob }
local pontos = {
	{ "spawn", Vector3.new(0, 30, -38) }, { "patio", Vector3.new(0, 30, 0) },
	{ "pe da escadaria", Vector3.new(0, 30, -88) }, { "terraco da Forja", Vector3.new(0, 40, -120) },
	{ "via imperial", Vector3.new(0, 30, 100) }, { "portao", Vector3.new(0, 30, 150) },
	{ "santuario", Vector3.new(124, 40, 0) }, { "loja", Vector3.new(-115, 40, -4) },
	{ "jardim W", Vector3.new(90, 40, 40) }, { "jardim E", Vector3.new(-90, 40, 40) },
}
local semChao = {}
for _, p in ipairs(pontos) do
	local r = workspace:Raycast(p[2], Vector3.new(0, -80, 0), rp)
	if not r then table.insert(semChao, p[1]) end
end
L("6) pontos sem chao: %s", #semChao == 0 and "nenhum" or table.concat(semChao, ", "))

-- 7) sistemas do jogo intactos
local ignis = workspace.NPCs:FindFirstChild("Ignis")
local prompt
for _, d in ipairs(ignis and ignis:GetDescendants() or {}) do
	if d:IsA("ProximityPrompt") then prompt = d end
end
L("7) Ignis=%s prompt=%s | LojaMochilas=%s | MailBox=%s | pads=%d",
	tostring(ignis ~= nil), tostring(prompt ~= nil),
	tostring(workspace:FindFirstChild("LojaMochilas") ~= nil),
	tostring(workspace:FindFirstChild("MailBox") ~= nil),
	sant and #sant:GetChildren() or 0)

return table.concat(out, "\n")
