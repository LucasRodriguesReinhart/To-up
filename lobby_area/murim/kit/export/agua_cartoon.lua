-- agua_cartoon.lua - AGUA DO LOBBY usando O MESMO SISTEMA das areas Dragon Ball (Area2) e Mare (Area5).
--
-- Inspecionado no projeto antes de escrever, nao presumido: aquelas areas NAO usam agua de Terrain.
-- Usam Part com filho Texture apontando para rbxasset://textures/particles/water_main.dds:
--   Lago        Part Plastic, Transparency 0.23, Reflectance 0.10
--               Texture Face=Top,   StudsPerTile 18x22, Transparency 0.90
--   LaminaDagua Part Plastic, Transparency 0.20, Reflectance 0.00   (folha VERTICAL, e queda d'agua)
--               Texture Face=Front, StudsPerTile 6x12,  Transparency 0.60
--   MargemExterior  Part opaca na cor do terreno
--
-- A TECNICA e a APARENCIA vem dessas areas. O FORMATO vem do contorno do lago do lobby, que e o
-- mesmo poligono que k_montagem.py usa para a malha, o leito e as margens - fonte unica, para acabar
-- com o caso de um componente usar o contorno novo e outro o retangulo antigo.
-- Nao mexe em Area2 nem em Area5: aqui so se LE a especificacao delas.

local lm = workspace:FindFirstChild("LOBBY_MURIM")
if not lm then return "LOBBY_MURIM nao encontrado" end

local DDS = "rbxasset://textures/particles/water_main.dds"
local COR = Color3.fromRGB(46, 150, 168)     -- turquesa do lobby, na familia das areas

-- contorno do lago, em Blender (y, x). Identico ao de k_montagem.py. Roblox: X = -x, Z = y.
local OESTE = {{-72,-99},{-56,-101.5},{-40,-100},{-28,-95},{-19,-88},{-9,-84.5},{9,-84.5},
               {19,-88},{28,-95},{40,-100.5},{58,-99},{78,-101},{100,-99.5},{118,-97},{132,-98}}
local LESTE = {{-72,-71},{-54,-68.5},{-36,-72},{-18,-69},{0,-71.5},{18,-68.5},{34,-71.5},
               {56,-69},{78,-72},{102,-69.5},{120,-71},{132,-70}}
local function interp(lista, y)
	if y <= lista[1][1] then return lista[1][2] end
	for i = 1, #lista - 1 do
		local a, b = lista[i], lista[i + 1]
		if y >= a[1] and y <= b[1] then
			return a[2] + (b[2] - a[2]) * ((y - a[1]) / (b[1] - a[1]))
		end
	end
	return lista[#lista][2]
end

-- limpa a agua anterior (terreno esculpido e partes antigas)
workspace.Terrain:FillRegion(
	Region3.new(Vector3.new(56, -14, -84), Vector3.new(116, 8, 144)):ExpandToGrid(4), 4, Enum.Material.Air)
local pasta = lm:FindFirstChild("AGUA")
if pasta then pasta:Destroy() end
pasta = Instance.new("Folder"); pasta.Name = "AGUA"; pasta.Parent = lm
-- a malha chapada do lago sai de cena: quem faz a agua agora sao estas Parts
for _, d in ipairs(lm:GetDescendants()) do
	if d:IsA("BasePart") and d.Name:find("LAGO_agua") then d.Transparency = 1; d.CanCollide = false end
end

local function faixa(z0, z1)
	local yo0, yl0 = interp(OESTE, z0), interp(LESTE, z0)
	local yo1, yl1 = interp(OESTE, z1), interp(LESTE, z1)
	local X0 = -((yo0 + yo1) / 2)                     -- Roblox X = -x do Blender
	local X1 = -((yl0 + yl1) / 2)
	if X1 < X0 then X0, X1 = X1, X0 end
	local larg = X1 - X0
	if larg < 1.5 then return nil end
	local p = Instance.new("Part")
	p.Name = "Lago"
	p.Anchored = true; p.CanCollide = false; p.CanTouch = false; p.CanQuery = false
	p.Material = Enum.Material.Plastic
	p.Transparency = 0.23; p.Reflectance = 0.10; p.Color = COR
	p.Size = Vector3.new(larg, 0.3, math.abs(z1 - z0) + 0.15)
	p.CFrame = CFrame.new((X0 + X1) / 2, 0.30, (z0 + z1) / 2)
	local t = Instance.new("Texture")
	t.Texture = DDS; t.Face = Enum.NormalId.Top
	t.StudsPerTileU = 18; t.StudsPerTileV = 22
	t.Transparency = 0.90; t.Color3 = Color3.new(1, 1, 1)
	t.Parent = p
	p.Parent = pasta
	return larg
end

local n, larguras = 0, {}
for z = -72, 130, 4 do
	local l = faixa(z, z + 4)
	if l then n += 1; table.insert(larguras, l) end
end

-- QUEDAS: folha vertical com a mesma especificacao da LaminaDagua das areas.
-- Ficam no labio do penhasco, onde a referencia mostra cascata caindo para fora do complexo.
local quedas = 0
for _, q in ipairs({
	{X = -182, Z = -60, rot = 90}, {X = -182, Z = 92, rot = 90},
	{X = 182, Z = -28, rot = 270}, {X = 182, Z = 112, rot = 270},
	{X = -44, Z = -206, rot = 180}, {X = 64, Z = 192, rot = 0},
}) do
	local p = Instance.new("Part")
	p.Name = "LaminaDagua"
	p.Anchored = true; p.CanCollide = false; p.CanTouch = false; p.CanQuery = false
	p.Material = Enum.Material.Plastic
	p.Transparency = 0.20; p.Reflectance = 0.00; p.Color = COR
	p.Size = Vector3.new(9, 38, 2)
	p.CFrame = CFrame.new(q.X, -17, q.Z) * CFrame.Angles(0, math.rad(q.rot), 0)
	local t = Instance.new("Texture")
	t.Texture = DDS; t.Face = Enum.NormalId.Front
	t.StudsPerTileU = 6; t.StudsPerTileV = 12
	t.Transparency = 0.60; t.Color3 = Color3.new(1, 1, 1)
	t.Parent = p
	p.Parent = pasta
	quedas += 1
end

local min, max = math.huge, 0
for _, l in ipairs(larguras) do min = math.min(min, l); max = math.max(max, l) end
return string.format(
	"agua no sistema das areas Dragon Ball/Mare: %d faixas de Lago seguindo o contorno (largura %.1f a %.1f studs) + %d LaminaDagua\n" ..
	"  Part Plastic transp 0.23 refl 0.10 | Texture %s Face=Top 18x22 transp 0.90\n" ..
	"  terreno de agua do lobby removido; LAGO_agua (malha chapada) invisivel",
	n, min, max, quedas, DDS)
