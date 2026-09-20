-- ignis_frente.lua - traz o Ignis para o alpendre da Forja, junto da fornalha.
-- Ele estava em Roblox (0, 17.3, -134), ou seja ATRAS da fachada (Blender y=-122), num interior escuro:
-- o jogador tinha de entrar no salao para achar quem vende. A forja foi para y=-116..-98 no Blender,
-- que em Roblox e Z=-116..-98; o Ignis vai para a frente dela, de cara para quem sobe a escadaria.
local ig = workspace.NPCs:FindFirstChild("Ignis")
if not ig then return "Ignis nao encontrado" end

local alvo = Vector3.new(0, 17.3, -108)          -- Roblox: na frente da fornalha, no alpendre
local atual = ig:GetPivot().Position
local d = alvo - atual

ig:PivotTo(ig:GetPivot() + d)

-- o prompt e criado em runtime pelo Core.Main sobre a peca "belly"; so conferimos que ela veio junto
local belly
for _, x in ipairs(ig:GetDescendants()) do
	if x:IsA("BasePart") and x.Name == "belly" then belly = x end
end
return string.format("Ignis movido de Z=%.1f para Z=%.1f (deslocamento %.1f) | belly em %s",
	atual.Z, ig:GetPivot().Position.Z, d.Magnitude, belly and tostring(belly.Position) or "nao achada")
