-- tour_video_cliente.lua (CLIENTE, em Play; colar no execute do cliente): voo de camera pela Ilha 2 para o video
-- dentro do jogo. Camera Scriptable, HUD escondido durante o voo e devolvido no fim. Posicoes = CAM_DB_* do Blender
-- levadas ao mundo (db_layout.world_matrix).
local RunService = game:GetService('RunService')
local cam = workspace.CurrentCamera
local pg = game.Players.LocalPlayer:WaitForChild('PlayerGui')
local V = Vector3.new
local function fov(lens) return math.deg(2 * math.atan(math.tan(math.atan(18 / lens)) * 9 / 16)) end
local K = {
	main = { V(-111.56, 235.0, 531.56), V(-344.9, 0.0, 764.9), 26 },
	front = { V(-54.99, 175.0, 474.99), V(-344.9, 20.0, 764.9), 24 },
	entry = { V(-197.82, 26.2, 617.82), V(-274.19, 34.2, 694.19), 20 },
	entry2 = { V(-245.91, 29.4, 665.91), V(-302.48, 26.2, 722.48), 24 },
	mining = { V(-236.01, 38.2, 729.55), V(-337.83, 24.2, 743.69), 18 },
	summon = { V(-248.74, 34.2, 770.56), V(-225.4, 48.2, 844.81), 18 },
	summon2 = { V(-237.42, 38.2, 793.19), V(-225.4, 52.2, 844.81), 20 },
	village = { V(-326.52, 35.2, 887.94), V(-401.47, 40.2, 878.04), 20 },
	capsule = { V(-385.91, 37.2, 805.91), V(-446.73, 56.2, 866.73), 18 },
	capsule2 = { V(-402.88, 33.2, 822.88), V(-446.73, 50.2, 866.73), 20 },
	inside = { V(-421.27, 39.4, 841.27), V(-448.14, 40.2, 868.14), 18 },
	env = { V(-318.03, 38.2, 848.34), V(-308.13, 50.0, 914.81), 20 },
	sg = { V(-524.5, 37.2, 680.48), V(-553.45, 38.2, 661.67), 22 },
	bird = { V(-309.55, 640.0, 729.55), V(-337.83, 0.0, 757.83), 24 },
}
-- (de, para, segundos)
local SHOTS = {
	{ 'main', 'front', 5 }, { 'entry', 'entry2', 4.5 }, { 'mining', 'mining', 0.1 }, { 'mining', 'summon', 4.5 },
	{ 'summon', 'summon2', 3.5 }, { 'village', 'village', 0.1 }, { 'village', 'capsule', 4 }, { 'capsule', 'capsule2', 3 },
	{ 'capsule2', 'inside', 3.5 }, { 'env', 'env', 3 }, { 'sg', 'sg', 3 }, { 'main', 'bird', 5 },
}
local guis = {}
for _, g in ipairs(pg:GetChildren()) do if g:IsA('ScreenGui') and g.Enabled then g.Enabled = false; table.insert(guis, g) end end
cam.CameraType = Enum.CameraType.Scriptable
local function ease(t) return t * t * (3 - 2 * t) end
for _, s in ipairs(SHOTS) do
	local a, b, dur = K[s[1]], K[s[2]], s[3]
	local t0 = os.clock()
	while true do
		local t = math.min(1, (os.clock() - t0) / dur)
		local e = ease(t)
		local p = a[1]:Lerp(b[1], e)
		local q = a[2]:Lerp(b[2], e)
		cam.CFrame = CFrame.lookAt(p, q)
		cam.FieldOfView = fov(a[3] + (b[3] - a[3]) * e)
		if t >= 1 then break end
		RunService.RenderStepped:Wait()
	end
end
task.wait(0.5)
cam.CameraType = Enum.CameraType.Custom
cam.FieldOfView = 70
for _, g in ipairs(guis) do g.Enabled = true end
