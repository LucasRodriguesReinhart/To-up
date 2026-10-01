-- PortaisAmbiente - balanca as lascas dos portais e faz a luz do vortice respirar.
-- Instalado por lobby_area/murim/kit/export/portais_vfx.lua. Apagar aqui nao quebra mais nada.
-- E LocalScript de proposito: e decoracao, e no servidor cada frame viraria pacote de replicacao.
local RunService = game:GetService("RunService")
local sant = workspace:WaitForChild("Santuario", 30)
local lob = workspace:WaitForChild("LOBBY_MURIM", 30)
if not (sant and lob) then return end

local lascas, luzes = {}, {}
for _, d in ipairs(lob:GetDescendants()) do
	if d:IsA("MeshPart") and d.Name:match("^POR_fragmento") then
		table.insert(lascas, { p = d, cf = d.CFrame, f = 0.5 + (#lascas % 5) * 0.17, a = (#lascas % 7) * 0.9 })
	end
end
for _, mod in ipairs(sant:GetChildren()) do
	local f = mod:FindFirstChild("VFX_PORTAL")
	local b = f and f:FindFirstChild("VortexEmitter")
	local l = b and b:FindFirstChildOfClass("PointLight")
	if l then table.insert(luzes, { l = l, base = l.Brightness, a = #luzes * 1.1 }) end
end
if #lascas == 0 and #luzes == 0 then return end

-- os seis portais cabem num trecho de ~65 studs: longe dali nao ha o que animar
local FOCO = Vector3.new(124.5, 13, 0)
local ALCANCE = 140

local t = 0
RunService.RenderStepped:Connect(function(dt)
	local cam = workspace.CurrentCamera
	if not cam or (cam.CFrame.Position - FOCO).Magnitude > ALCANCE then return end
	t += dt
	for _, s in ipairs(lascas) do
		local sobe = math.sin(t * s.f + s.a) * 0.55
		s.p.CFrame = s.cf * CFrame.new(0, sobe, 0) * CFrame.Angles(0, t * 0.35 + s.a, 0)
	end
	for _, u in ipairs(luzes) do
		u.l.Brightness = u.base * (0.78 + 0.22 * math.sin(t * 1.6 + u.a))
	end
end)
