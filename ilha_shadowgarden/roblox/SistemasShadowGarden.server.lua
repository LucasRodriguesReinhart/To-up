-- SistemasShadowGarden (Script, ServerScriptService.Core) - liga a Alquimia (CraftService) e a Masmorra das Sombras
-- (DungeonService) da Ilha 3 depois que o AreaBuilder monta as areas. Sem a Ilha 3 montada, os dois avisam e ficam
-- desligados (nada quebra). Rollback: desabilitar este Script.
local Core = script.Parent
for _, nome in ipairs({ "CraftService", "DungeonService" }) do
	task.spawn(function()
		local ok, res = pcall(function() return require(Core:WaitForChild(nome)).iniciar() end)
		if not ok then warn("[SistemasShadowGarden] " .. nome .. ": " .. tostring(res))
		else print("[SistemasShadowGarden] " .. nome .. (res and " ligado" or " desligado (sem Ilha 3)")) end
	end)
end
