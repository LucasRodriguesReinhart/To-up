-- pos_montagem_integracao.lua - roda DEPOIS do export/montar_ilha_naruto.lua (Command Bar ou MCP). Idempotente.
-- Transforma o workspace.ILHA_NARUTO recem-montado na FONTE que o jogo usa (ServerStorage.IlhaNaruto, clonada
-- para a Area 1 pelo Core.NarutoIsland) e reaplica os ajustes da integracao:
--  1) luzes na hierarquia pedida: invocacao > predio principal > portao > agua > props
--  2) ILHA_NARUTO_Servidor desligado (este export nao tem cascas SoVisual; o grupo 'Personagens' colidiria com
--     'PetsVisuais'; quedas ficam com o IslandTravel)
--  3) confere que nao entrou o MINE_Props__Crystal_Blue antigo (o do 203d27 espalhava cristais pelo fosso)
--  4) a versao anterior de ServerStorage.IlhaNaruto vai para ServerStorage.IlhaNaruto_anterior (rollback)
local SS = game:GetService('ServerStorage')
local root = workspace:FindFirstChild('ILHA_NARUTO')
assert(root, 'rode o montar_ilha_naruto.lua antes (workspace.ILHA_NARUTO nao existe)')

local LUZ = {
	L_Summon_Star = { 1.7, 22 }, L_Summon_Portal = { 1.55, 20 },
	L_Village_HallInterior = { 1.2, 18 }, L_Village_HallDesk = { 0.95, 15 },
	L_GateDB_Barrier = { 0.8, 12 },
	L_Village_ShopInterior = { 0.55, 13 }, L_Village_Ramen = { 0.55, 13 },
	L_Houses_MillInterior = { 0.45, 11 }, L_Houses_MillCounter = { 0.35, 9 }, L_Houses_MillDoor = { 0.3, 7 },
	L_Mining_Core_Glow = { 0.45, 11 },
}
for _, l in ipairs(root.LIGHTS:GetDescendants()) do
	local a = l:IsA('Light') and LUZ[l.Parent.Name]
	if a then l.Brightness, l.Range = a[1], a[2] end
end
local agua = root.LIGHTS:FindFirstChild('L_Water_BackFalls') or Instance.new('Part')
agua.Name = 'L_Water_BackFalls'; agua.Anchored = true; agua.CanCollide = false; agua.CanQuery = false
agua.CanTouch = false; agua.CastShadow = false; agua.Transparency = 1; agua.Size = Vector3.new(1, 1, 1)
agua.Position = Vector3.new(0, 27, 596); agua.Parent = root.LIGHTS
local pl = agua:FindFirstChildOfClass('PointLight') or Instance.new('PointLight', agua)
pl.Brightness = 0.6; pl.Range = 16; pl.Color = Color3.fromRGB(190, 225, 255); pl.Shadows = false

local srv = game:GetService('ServerScriptService'):FindFirstChild('ILHA_NARUTO_Servidor')
if srv then srv.Disabled = true end

local cristal = root:FindFirstChild('MINE_Props__Crystal_Blue', true)
if cristal and math.max(cristal.Size.X, cristal.Size.Y, cristal.Size.Z) > 60 then
	warn('MINE_Props__Crystal_Blue com ' .. tostring(cristal.Size) .. ': e a malha ANTIGA (cristais no fosso). Reimporte ILHA1_03_MINING.')
end

local velho = SS:FindFirstChild('IlhaNaruto')
if velho then
	local ant = SS:FindFirstChild('IlhaNaruto_anterior'); if ant then ant:Destroy() end
	velho.Name = 'IlhaNaruto_anterior'
end
root:SetAttribute('PendenteReimport', nil)
root.Name = 'IlhaNaruto'
root.Parent = SS
print('Ilha Naruto pronta em ServerStorage.IlhaNaruto (a anterior ficou em ServerStorage.IlhaNaruto_anterior)')
