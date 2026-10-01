-- pos_montagem_dragonball.lua - roda DEPOIS do export/montar_ilha_dragonball.lua (Command Bar ou MCP). Idempotente.
-- Transforma o workspace.ILHA_DRAGONBALL recem-montado na FONTE que o jogo usa (ServerStorage.IlhaDragonBall, clonada
-- para a Area 2 pelo Core.DragonBallIsland) e confere o que a integracao espera:
--  1) ILHA_DRAGONBALL_Servidor desligado (como o da Ilha 1: o grupo 'Personagens' colidiria com 'PetsVisuais'; as
--     quedas ficam com o IslandTravel)
--  2) nada de prova de desenvolvimento no modelo (DB_Mine_OreProxy / COL_QA_) e os marcadores que o builder usa
--  3) a versao anterior de ServerStorage.IlhaDragonBall vai para ServerStorage.IlhaDragonBall_anterior (rollback)
local SS = game:GetService('ServerStorage')
local root = workspace:FindFirstChild('ILHA_DRAGONBALL')
assert(root, 'rode o montar_ilha_dragonball.lua antes (workspace.ILHA_DRAGONBALL nao existe)')

local srv = game:GetService('ServerScriptService'):FindFirstChild('ILHA_DRAGONBALL_Servidor')
if srv then srv.Disabled = true end

local ruins = {}
for _, d in ipairs(root:GetDescendants()) do
	if string.match(d.Name, '^DB_Mine_OreProxy') or string.match(d.Name, '^COL_QA_') then table.insert(ruins, d:GetFullName()) end
end
assert(#ruins == 0, 'prova de desenvolvimento no modelo: ' .. table.concat(ruins, ', '))

local mk = root:FindFirstChild('GAMEPLAY_MARKERS')
assert(mk, 'GAMEPLAY_MARKERS faltando')
local precisa = { 'WORLD_FROM_PREV', 'WORLD_ENTRY_DragonBall', 'ISLAND_EXIT_DragonBall', 'ISLAND_NEXT_ANCHOR_ShadowGarden',
	'MiningZone_DragonBall', 'SUMMON_Main', 'SUMMON_Interact', 'SUMMON_PlayerPosition', 'GATE_ShadowGarden',
	'GATE_ShadowGarden_INTERACT', 'PURCHASE_UI_ANCHOR_ShadowGarden', 'NPC_Capsule', 'PLAYER_INTERACT_Capsule' }
local faltam = {}
for _, n in ipairs(precisa) do if not mk:FindFirstChild(n) then table.insert(faltam, n) end end
if #faltam > 0 then warn('[pos_montagem_dragonball] marcadores faltando: ' .. table.concat(faltam, ', ')) end
local ores, blocks = 0, 0
for _, m in ipairs(mk:GetChildren()) do
	if string.match(m.Name, '^ORE_') then ores += 1 elseif string.match(m.Name, '^GP_Block_') then blocks += 1 end
end

local meshes = 0
for _, d in ipairs(root:GetDescendants()) do if d:IsA('MeshPart') then meshes += 1 end end

local velho = SS:FindFirstChild('IlhaDragonBall')
if velho then
	local ant = SS:FindFirstChild('IlhaDragonBall_anterior'); if ant then ant:Destroy() end
	velho.Name = 'IlhaDragonBall_anterior'
end
root.Name = 'IlhaDragonBall'
root.Parent = SS
print(('Ilha Dragon Ball pronta em ServerStorage.IlhaDragonBall: %d MeshParts, %d ORE_*, %d GP_Block_*'):format(meshes, ores, blocks))
