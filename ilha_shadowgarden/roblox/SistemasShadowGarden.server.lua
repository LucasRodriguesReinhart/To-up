-- SistemasShadowGarden (Script, ServerScriptService.Core) - liga a Alquimia (CraftService), a Masmorra das Sombras
-- (DungeonService) e a passagem secreta do trono (TronoService) da Ilha 3 depois que o AreaBuilder monta as areas.
-- Sem a Ilha 3 montada, os servicos avisam e ficam desligados (nada quebra). Rollback: desabilitar este Script.
local Core = script.Parent
for _, nome in ipairs({ "CraftService", "DungeonService", "TronoService" }) do
	task.spawn(function()
		local ok, res = pcall(function() return require(Core:WaitForChild(nome)).iniciar() end)
		if not ok then warn("[SistemasShadowGarden] " .. nome .. ": " .. tostring(res))
		else print("[SistemasShadowGarden] " .. nome .. (res and " ligado" or " desligado (sem Ilha 3)")) end
	end)
end
