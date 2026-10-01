-- leoes_escadaria.lua - reposiciona e amplia o par de leoes guardiaes.
-- Na referencia eles guardam o PE da escadaria do palacio, em pedestal alto, grandes o bastante para
-- estreitar a passagem: o jogador passa ENTRE os dois. No lobby estavam em Z=-88, ou seja no TOPO
-- (a escada vai de Z=-90.5 a -65.5), e com 8 studs de altura se perdiam na escala.
-- Roda no lobby JA MONTADO, sem custar ciclo de bake - so mexe em posicao e tamanho de MeshPart.
local lm = workspace:FindFirstChild("LOBBY_MURIM")
if not lm then return "LOBBY_MURIM nao encontrado" end
local ESCALA = 1.65
local n = 0
for _, d in ipairs(lm:GetDescendants()) do
	if d:IsA("MeshPart") and d.Name:find("leao") then
		local antes = d.Position
		d.Size = d.Size * ESCALA
		local novoY = d.Size.Y / 2                      -- base assentada em Y=0
		if math.abs(antes.Z + 88) < 2 then              -- par do palacio: vai para o PE da escada
			local sx = antes.X > 0 and 1 or -1
			d.CFrame = CFrame.new(sx * 21, novoY, -60) * (d.CFrame - d.Position)
		else                                            -- par do Grande Portao: so cresce e assenta
			d.CFrame = CFrame.new(antes.X, novoY, antes.Z) * (d.CFrame - d.Position)
		end
		n += 1
	end
end
return "leoes ajustados: " .. n
