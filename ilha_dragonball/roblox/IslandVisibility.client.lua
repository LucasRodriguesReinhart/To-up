-- IslandVisibility (cliente) - 2026-09-25: VIZINHANCA em vez de "so a area atual".
-- Antes: toda ilha que nao fosse a area atual ficava invisivel (LocalTransparencyModifier=1). No mundo continuo isso
-- escondia a ilha ao lado: voltando da Ilha 2 para a Ilha 1 o jogador ainda e area 2 (histerese do IslandTravel) e
-- andava no vazio; na ponte nao dava para ver a ilha seguinte.
-- Agora: fica visivel a area atual E toda area cuja regiao (BoundsCenter/BoundsHalfSize, como o IslandTravel) encosta
-- na regiao dela (folga GAP). O lobby conta como uma regiao. So as ilhas longe/desconectadas somem (as silhuetas
-- soltas que o script original evitava). O IslandTravel mantem as vizinhas carregadas (AddPersistentPlayer).
local Players = game:GetService('Players')
local RS = game:GetService('ReplicatedStorage')
local player = Players.LocalPlayer
local Config = require(RS:WaitForChild('Config'))
local GAP = 60
local LOBBY_C, LOBBY_H = Vector3.new(0, 0, -55), Vector3.new(190, 0, 245)   -- |x|<190, -300<z<190 (IslandTravel)

local known = {}
local visible = {}
local current = player:GetAttribute('CurrentAreaId') or 0

local function box(id)
	if id == 0 then return LOBBY_C, LOBBY_H end
	local areas = workspace:FindFirstChild('Areas')
	local m = areas and areas:FindFirstChild('Area' .. id)
	local h = m and m:GetAttribute('BoundsHalfSize')
	if typeof(h) ~= 'Vector3' then return nil end
	local c = m:GetAttribute('BoundsCenter')
	if typeof(c) ~= 'Vector3' then local a = Config.areaPorId(id); c = a and a.centro end
	return c, h
end

local function touches(a, b)
	local ca, ha = box(a)
	local cb, hb = box(b)
	if not ca or not cb then return false end
	return math.abs(ca.X - cb.X) <= ha.X + hb.X + GAP and math.abs(ca.Z - cb.Z) <= ha.Z + hb.Z + GAP
end

local function areaId(instance)
	local areas = workspace:FindFirstChild('Areas') if not areas then return end
	local node = instance
	while node and node.Parent ~= areas do node = node.Parent end
	return node and (node:GetAttribute('AreaId') or tonumber(node.Name:match('^Area(%d+)$')))
end

local function apply(part, id)
	part.LocalTransparencyModifier = visible[id] and 0 or 1
end

local function recompute()
	local old = visible
	visible = {}
	for _, a in ipairs(Config.Areas) do visible[a.id] = (a.id == current) or touches(a.id, current) end
	for part, id in known do
		if part.Parent and old[id] ~= visible[id] then apply(part, id) end
	end
end

local function register(instance)
	if not instance:IsA('BasePart') then return end
	local id = areaId(instance) if not id then return end
	known[instance] = id
	apply(instance, id)
end

recompute()
workspace.DescendantAdded:Connect(register)
workspace.DescendantRemoving:Connect(function(instance) known[instance] = nil end)
for _, instance in workspace:GetDescendants() do register(instance) end
player:GetAttributeChangedSignal('CurrentAreaId'):Connect(function()
	current = player:GetAttribute('CurrentAreaId') or 0
	recompute()
end)
-- as regioes chegam quando o servidor monta as ilhas (atributos na Area): recalcula quando mudam
local function watch(m)
	m:GetAttributeChangedSignal('BoundsCenter'):Connect(recompute)
	m:GetAttributeChangedSignal('BoundsHalfSize'):Connect(recompute)
end
local areas = workspace:WaitForChild('Areas', 30)
if areas then
	for _, m in ipairs(areas:GetChildren()) do watch(m) end
	areas.ChildAdded:Connect(function(m) watch(m); task.defer(recompute) end)
end
