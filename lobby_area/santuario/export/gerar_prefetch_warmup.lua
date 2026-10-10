-- Gera ReplicatedStorage.LobbyAssetPrefetch para o LobbyAssetWarmup (StarterPlayerScripts).
-- Rodar na command bar do Studio (Edit) DEPOIS de cada reimportacao do lobby ou troca do Ignis.
-- Por que existe: com StreamingEnabled o cliente nao enxerga o lobby inteiro quando entra, e
-- PreloadAsync com string so baixa imagem comum (malha e mapa de SurfaceAppearance falham).
-- ReplicatedStorage chega inteiro no join, entao uma copia leve de cada malha unica fica la
-- (sem filhos alem da SurfaceAppearance, sem colisao) so para o PreloadAsync por instancia.
local RS = game:GetService("ReplicatedStorage")
local root = workspace:FindFirstChild("LOBBY_FORJA")
local npcs = workspace:FindFirstChild("NPCs")
local ignis = npcs and npcs:FindFirstChild("Ignis")
assert(root, "LOBBY_FORJA nao esta no Workspace")

local antigo = RS:FindFirstChild("LobbyAssetPrefetch")
if antigo then antigo:Destroy() end
local velhoManifesto = RS:FindFirstChild("LobbyAssetManifest")
if velhoManifesto then velhoManifesto:Destroy() end

local pasta = Instance.new("Folder")
pasta.Name = "LobbyAssetPrefetch"
pasta:SetAttribute("EXPORT_ID", tostring(root:GetAttribute("EXPORT_ID") or ""))

local vistos, n, semBox = {}, 0, 0
for _, model in { root, ignis } do
	if model then
		for _, d in model:GetDescendants() do
			if d:IsA("MeshPart") and d.MeshId ~= "" and d.Transparency < 1 then
				local sa = d:FindFirstChildWhichIsA("SurfaceAppearance")
				local chave = d.MeshId .. "|" .. d.TextureID
				if sa then
					chave ..= "|" .. sa.ColorMap .. "|" .. sa.NormalMap .. "|" .. sa.RoughnessMap .. "|" .. sa.MetalnessMap
				end
				if not vistos[chave] then
					vistos[chave] = true
					n += 1
					local c = d:Clone()
					for _, filho in c:GetChildren() do
						if not filho:IsA("SurfaceAppearance") then filho:Destroy() end
					end
					c.Name = string.format("%03d", n)
					c.Anchored = true
					c.CanCollide = false
					c.CanTouch = false
					c.CanQuery = false
					c.CFrame = CFrame.identity
					-- tira a geometria de colisao serializada (deixa a copia leve na replicacao)
					if not pcall(function() c.CollisionFidelity = Enum.CollisionFidelity.Box end) then semBox += 1 end
					c.Parent = pasta
				end
			end
		end
	end
end
pasta.Parent = RS
print(string.format("[LobbyAssetPrefetch] %d malhas unicas, export %s, sem Box %d", n, pasta:GetAttribute("EXPORT_ID"), semBox))
