-- LobbyVida : movimento ambiental do lobby (somente cliente).
-- Roda no cliente porque e puramente visual: nao gasta CPU de servidor
-- nem replica CFrame pela rede.
-- Item 8 do brief: movimento CONTROLADO. Tudo aqui e lento e discreto.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local root = workspace:WaitForChild("LobbyRenovado", 30)
if not root then return end

-- ---------------------------------------------------------------
-- coleta de alvos (uma vez; depois so o loop roda)
-- ---------------------------------------------------------------
local spinRings   = {}   -- aneis de energia dos portais
local pulseCores  = {}   -- neon que respira
local beacons     = {}   -- balizas piscando
local oreOnBelt   = {}   -- minerio viajando na esteira
local steamVents  = {}
local sparkJets   = {}
local beltData    = {}

for _, d in ipairs(root:GetDescendants()) do
	if d:IsA("BasePart") then
		local n = d.Name
		if n == "Baliza" then
			table.insert(beacons, {part = d, phase = math.random() * 6.28})
		elseif n == "NucleoQuente" or n == "Brilho" or n == "MetalFundido" then
			table.insert(pulseCores, {part = d, base = d.Transparency, phase = math.random() * 6.28})
		elseif n == "MinerioNaEsteira" then
			table.insert(oreOnBelt, d)
		end
	elseif d:IsA("Model") then
		if d.Name == "AnelDeEnergia" then
			table.insert(spinRings, {model = d, speed = 0.18 + math.random() * 0.22,
				pivot = d:GetPivot()})
		elseif d.Name == "EsteiraMagnetica" then
			local de, para = d:GetAttribute("De"), d:GetAttribute("Para")
			if de and para then table.insert(beltData, {model = d, a = de, b = para}) end
		end
	elseif d:IsA("ParticleEmitter") then
		if d.Name == "Vapor" then table.insert(steamVents, d)
		elseif d.Name == "Faiscas" then table.insert(sparkJets, d) end
	end
end

-- pre-calcula a rota de cada minerio na esteira a que pertence
for _, ore in ipairs(oreOnBelt) do
	local belt = ore.Parent
	local a, b = belt:GetAttribute("De"), belt:GetAttribute("Para")
	if a and b then
		ore:SetAttribute("A", a)
		ore:SetAttribute("B", b)
	end
end

-- ---------------------------------------------------------------
-- eventos esporadicos: vapor e faisca nao podem ser continuos,
-- senao viram ruido visual
-- ---------------------------------------------------------------
task.spawn(function()
	while task.wait(math.random(4, 9)) do
		if #steamVents > 0 then
			local v = steamVents[math.random(#steamVents)]
			v:Emit(26)
		end
	end
end)

task.spawn(function()
	while task.wait(math.random(2, 6) + math.random()) do
		if #sparkJets > 0 then
			local s = sparkJets[math.random(#sparkJets)]
			for i = 1, math.random(2, 4) do
				s:Emit(math.random(8, 16))
				task.wait(0.09)
			end
		end
	end
end)

-- ---------------------------------------------------------------
-- loop principal (throttled em 20 Hz: o movimento e lento, nao precisa 60)
-- ---------------------------------------------------------------
local acc = 0
local STEP = 1 / 20
local t = 0

RunService.RenderStepped:Connect(function(dt)
	acc = acc + dt
	if acc < STEP then return end
	local step = acc
	acc = 0
	t = t + step

	-- aneis dos portais girando devagar
	for _, r in ipairs(spinRings) do
		r.model:PivotTo(r.pivot * CFrame.Angles(0, 0, t * r.speed))
	end

	-- nucleos respirando
	for _, c in ipairs(pulseCores) do
		local k = 0.5 + 0.5 * math.sin(t * 1.3 + c.phase)
		c.part.Transparency = math.clamp(c.base + k * 0.16 - 0.08, 0, 1)
	end

	-- balizas de obstaculo piscando
	for _, b in ipairs(beacons) do
		local on = (math.sin(t * 2.1 + b.phase) > 0.55)
		b.part.Transparency = on and 0 or 0.85
	end

	-- minerio correndo na esteira (loop continuo)
	for _, ore in ipairs(oreOnBelt) do
		local a, b = ore:GetAttribute("A"), ore:GetAttribute("B")
		if a and b then
			local p = ore:GetAttribute("EsteiraT") or 0
			p = (p + step * 0.055) % 1
			ore:SetAttribute("EsteiraT", p)
			ore.CFrame = CFrame.new(a:Lerp(b, p) + Vector3.new(0, 1.4, 0))
				* CFrame.Angles(t * 0.8, t * 0.5, 0)
		end
	end
end)
