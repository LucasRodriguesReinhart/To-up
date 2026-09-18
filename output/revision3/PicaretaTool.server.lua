-- Creates the physical pickaxe. MiningSwing controls the game-owned arm strike.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local CORES = {
	Color3.fromRGB(128, 118, 108), Color3.fromRGB(176, 180, 190),
	Color3.fromRGB(210, 214, 224), Color3.fromRGB(224, 70, 84),
	Color3.fromRGB(58, 54, 74),    Color3.fromRGB(150, 110, 255),
	Color3.fromRGB(120, 210, 255), Color3.fromRGB(255, 150, 55),
}

local function construir(idPicareta)
	local def, tier = Config.picaretaPorId(idPicareta)
	tier = tier or 1
	local cor = CORES[math.min(tier, #CORES)]

	local tool = Instance.new("Tool")
	tool.Name = "Picareta"
 tool:SetAttribute("PicaretaId", idPicareta)
	tool.RequiresHandle = true
	tool.CanBeDropped = false
	tool.ToolTip = def and def.nome or "Picareta"

	local cabo = Instance.new("Part")
	cabo.Name = "Handle"
	cabo.Size = Vector3.new(0.4, 3.4, 0.4)
	cabo.Color = Color3.fromRGB(126, 84, 48)
	cabo.Material = Enum.Material.Wood
	cabo.CanCollide = false
	cabo.Massless = true
	cabo.TopSurface = Enum.SurfaceType.Smooth
	cabo.BottomSurface = Enum.SurfaceType.Smooth
	cabo.Parent = tool

	local cabeca = Instance.new("Part")
	cabeca.Name = "Cabeca"
	cabeca.Size = Vector3.new(2.4, 0.5, 0.6)
	cabeca.Color = cor
	cabeca.Material = tier >= 6 and Enum.Material.Neon or Enum.Material.Metal
	cabeca.Reflectance = tier >= 3 and 0.15 or 0.05
	cabeca.CanCollide = false
	cabeca.Massless = true
	cabeca.Parent = tool

	local ponta = Instance.new("Part")
	ponta.Name = "Ponta"
	ponta.Size = Vector3.new(0.7, 0.45, 0.5)
	ponta.Color = cor:Lerp(Color3.new(1,1,1), 0.3)
	ponta.Material = cabeca.Material
	ponta.CanCollide = false
	ponta.Massless = true
	ponta.Parent = tool

	local w1 = Instance.new("Weld")
	w1.Part0 = cabo; w1.Part1 = cabeca
	w1.C0 = CFrame.new(0, 1.5, 0)
	w1.Parent = cabeca

	local w2 = Instance.new("Weld")
	w2.Part0 = cabeca; w2.Part1 = ponta
	w2.C0 = CFrame.new(-1.4, 0, 0) * CFrame.Angles(0, 0, math.rad(-18))
	w2.Parent = ponta

	if tier >= 6 then
		local l = Instance.new("PointLight")
		l.Color = cor; l.Brightness = 1.2; l.Range = 10
		l.Parent = cabeca
	end

	-- Fixed grip calibrated to the game strike; never animated independently.
	tool.Grip = CFrame.new(0, 0.1, 0, 0.4328632354736328, 0.3389130234718323, -0.8353247046470642, -0.8923119902610779, 0.02941453456878662, -0.45046013593673706, -0.1280960887670517, 0.9403578639030457, 0.31514862179756165)

	return tool
end

local function entregar(player)
	local perfil = PlayerData.get(player)
	local id = perfil and perfil.picareta or "enferrujada"
 local existing=(player.Character and player.Character:FindFirstChild("Picareta")) or player.Backpack:FindFirstChild("Picareta")
 if existing and existing:GetAttribute("PicaretaId")==id then return end

	for _, onde in ipairs({ player.Backpack, player.Character }) do
		if onde then
			local velha = onde:FindFirstChild("Picareta")
			if velha then velha:Destroy() end
		end
	end

	local tool = construir(id)
	tool.Parent = player.Backpack

	-- equipa sozinha, o jogador nao deveria precisar procurar
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then
  task.defer(function()
   if player.Character==char and hum.Parent==char and tool.Parent==player.Backpack then
    hum:EquipTool(tool)
   end
  end)
 end
end

Players.PlayerAdded:Connect(function(player)
	player.CharacterAdded:Connect(function()
		task.wait(0.6)
		entregar(player)
	end)
end)
for _, p in ipairs(Players:GetPlayers()) do
	if p.Character then task.spawn(entregar, p) end
	p.CharacterAdded:Connect(function() task.wait(0.6); entregar(p) end)
end

-- troca a tool quando o jogador compra picareta melhor
local ultimaPic = {}
task.spawn(function()
	while true do
		task.wait(1)
		for _, p in ipairs(Players:GetPlayers()) do
			local perfil = PlayerData.get(p)
			if perfil and ultimaPic[p] ~= perfil.picareta then
				ultimaPic[p] = perfil.picareta
				if p.Character then entregar(p) end
			end
		end
	end
end)

Players.PlayerRemoving:Connect(function(p) ultimaPic[p] = nil end)

