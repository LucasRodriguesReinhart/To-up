-- preparar_wb.lua: ANTES de importar os FBX do Wolfberg no Studio (Edit). Guarda a geometria do lobby atual
-- (Vila Medieval V4 ou outro) em ServerStorage e mantem no LOBBY_FORJA so o que e do JOGO (CircularUI, GlobalTop100,
-- Santuario, LobbyRevision). Idempotente. Uso: loadstring(HttpService:GetAsync("http://127.0.0.1:8773/roblox/preparar_wb.lua"))()
local SS = game:GetService("ServerStorage")
local root = workspace:FindFirstChild("LOBBY_FORJA")
if not root then return "sem LOBBY_FORJA no workspace" end
local tag = os.date("%Y%m%d%H%M")
local bk = Instance.new("Folder"); bk.Name = "LOBBY_FORJA_antes_Wolfberg_" .. tag
bk:SetAttribute("EXPORT_ID_antes", tostring(root:GetAttribute("EXPORT_ID")))
local KEEP = {CircularUI = true, GlobalTop100 = true, Santuario = true, LobbyRevision = true}
local moved, kept = {}, {}
for _, c in ipairs(root:GetChildren()) do
	if KEEP[c.Name] then
		table.insert(kept, c.Name)
	else
		c.Parent = bk
		table.insert(moved, c.Name)
	end
end
bk.Parent = SS
-- objetos soltos do jogo (so copia de seguranca das posicoes; os originais ficam e o montar os move)
local sol = Instance.new("Folder"); sol.Name = "LobbySoltos_antes_Wolfberg_" .. tag
local function note(name, inst)
	if inst then
		local v = Instance.new("CFrameValue"); v.Name = name; v.Value = inst:IsA("Model") and inst:GetPivot() or inst.CFrame; v.Parent = sol
	end
end
local msp = workspace:FindFirstChild("Mystical Spawn Point"); note("SpawnLobby", msp and msp:FindFirstChild("SpawnLobby"))
note("MailBox", workspace:FindFirstChild("MailBox"))
local lm = workspace:FindFirstChild("LojaMochilas"); note("PadLoja", lm and lm:FindFirstChild("PadLoja"))
local npcs = workspace:FindFirstChild("NPCs"); note("npc vendedor ", npcs and npcs:FindFirstChild("npc vendedor "))
sol.Parent = SS
-- Lighting atual (copia das propriedades principais)
local Lg = game:GetService("Lighting")
local lb = Instance.new("Folder"); lb.Name = "Lighting_antes_Wolfberg_" .. tag
for _, k in ipairs({"ClockTime", "Brightness", "GeographicLatitude", "ExposureCompensation", "EnvironmentDiffuseScale", "EnvironmentSpecularScale", "ShadowSoftness"}) do
	local v = Instance.new("NumberValue"); v.Name = k; v.Value = Lg[k]; v.Parent = lb
end
for _, k in ipairs({"Ambient", "OutdoorAmbient", "ColorShift_Top", "ColorShift_Bottom"}) do
	local v = Instance.new("Color3Value"); v.Name = k; v.Value = Lg[k]; v.Parent = lb
end
for _, c in ipairs(Lg:GetChildren()) do c:Clone().Parent = lb end
lb.Parent = SS
return string.format("guardado em ServerStorage.%s: movidos %d (%s); mantidos %s", bk.Name, #moved, table.concat(moved, ", "), table.concat(kept, ", "))
