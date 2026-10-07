-- materiais_alpha.lua - roda DEPOIS de montar_lobby.lua.
--
-- Os atlas assados sao RGB de 24 bits, sem canal alfa (que e a especificacao de albedo do Roblox).
-- O importador deixa toda SurfaceAppearance em AlphaMode.Overlay, modo em que o alfa do ColorMap
-- controla quanto da textura e MESCLADA sobre a cor da Part. Sem canal alfa a mescla nao acontece e
-- a peca fica na cor da Part - o cinza 0.639,0.635,0.647 que deixou metade do lobby sem cor.
-- Em AlphaMode.Transparency o ColorMap SUBSTITUI a cor, que e o comportamento que este pipeline quer.
--
-- Medido antes/depois no mesmo enquadramento: com Overlay, lanterna/balaustrada/telhado/portais
-- saiam cinza; com Transparency, todos voltam a ter cor.
local lm = workspace:FindFirstChild("LOBBY_MURIM")
if not lm then return "LOBBY_MURIM nao encontrado" end
local n, brancos = 0, 0
for _, d in ipairs(lm:GetDescendants()) do
	if d:IsA("MeshPart") then
		local sa = d:FindFirstChildOfClass("SurfaceAppearance")
		if sa and sa.AlphaMode ~= Enum.AlphaMode.Transparency then
			sa.AlphaMode = Enum.AlphaMode.Transparency
			n = n + 1
		end
		if d.Color ~= Color3.new(1, 1, 1) then
			d.Color = Color3.new(1, 1, 1)   -- cor neutra: quem manda e o ColorMap
			brancos = brancos + 1
		end
	end
end
return string.format("AlphaMode -> Transparency em %d SurfaceAppearance | cor neutralizada em %d MeshParts", n, brancos)
