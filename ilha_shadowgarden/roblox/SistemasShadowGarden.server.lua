-- SistemasShadowGarden (Script, ServerScriptService.Core) - liga a Alquimia (CraftService), a Masmorra das Sombras
-- (DungeonService) e a passagem secreta do trono (TronoService) da Ilha 3 depois que o AreaBuilder monta as areas.
-- A ilha v4 e grande: o AreaBuilder demora e RECRIA a pasta Areas/Area3. Por isso este script espera a ilha montada
-- (GAMEPLAY_MARKERS com os marcadores da Ilha 3 dentro da Area da tema sombra) antes de ligar os servicos.
-- Sem a Ilha 3 (3 min sem marcadores), os servicos tentam mesmo assim e avisam (nada quebra). Rollback: desabilitar.
local Core = script.Parent
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Config"))

local function ilhaMontada()
	local area
	for _, a in ipairs(Config.Areas) do if a.tema == "sombra" then area = a end end
	local areas = workspace:FindFirstChild("Areas")
	local m = area and areas and areas:FindFirstChild("Area" .. area.id)
	local mk = m and m:FindFirstChild("GAMEPLAY_MARKERS", true)
	return mk ~= nil and mk:FindFirstChild("CRAFT_Station") ~= nil and mk:FindFirstChild("DUNGEON_Entrance") ~= nil
end

local t0 = os.clock()
while not ilhaMontada() and os.clock() - t0 < 180 do task.wait(1) end
task.wait(1)   -- uma batida a mais: o JardimSombrasIsland termina de publicar os atributos da area

for _, nome in ipairs({ "CraftService", "DungeonService", "TronoService" }) do
	task.spawn(function()
		local ok, res = pcall(function() return require(Core:WaitForChild(nome)).iniciar() end)
		if not ok then warn("[SistemasShadowGarden] " .. nome .. ": " .. tostring(res))
		else print("[SistemasShadowGarden] " .. nome .. (res and " ligado" or " desligado (sem Ilha 3)")) end
	end)
end
