-- Creates the physical pickaxe. MiningSwing controls the game-owned arm strike.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local PickaxeModels = require(script.Parent.PickaxeModels)

local CORES = {
	Color3.fromRGB(128, 118, 108), Color3.fromRGB(176, 180, 190),
	Color3.fromRGB(210, 214, 224), Color3.fromRGB(224, 70, 84),
	Color3.fromRGB(58, 54, 74),    Color3.fromRGB(150, 110, 255),
	Color3.fromRGB(120, 210, 255), Color3.fromRGB(255, 150, 55),
}

local function construir(idPicareta)
	local def, tier = Config.picaretaPorId(idPicareta)
	local imported = PickaxeModels.create(def and def.modelo or idPicareta, def)
	if imported then imported:SetAttribute("PicaretaId", idPicareta); return imported end
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

	-- Empunhadura de destro (mesmo valor de PickaxeModels): mao direita em cima (meio da haste), esquerda abaixo,
	-- haste atravessando o punho, lamina no plano do golpe. A pose dos bracos vem do CharacterRig (IK), nao do grip.
	local R = CFrame.fromMatrix(Vector3.zero, Vector3.new(0, 1, 0), Vector3.new(0, 0, -1), Vector3.new(-1, 0, 0))
	tool.Grip = CFrame.new(0, -0.05, 0) * R:Inverse() * CFrame.Angles(math.rad(-90), 0, 0)

	return tool
end

-- A picareta nunca pode faltar na mao: alem de entregar quando o personagem nasce e quando o jogador
-- compra uma melhor, um vigia confere a cada 0.4 s e reequipa se ela sair da mao (morte, queda da tool,
-- jogador desequipando pelo teclado, ou qualquer script que a remova).
local function garantir(player)
 local char = player.Character
 local hum = char and char:FindFirstChildOfClass("Humanoid")
 if not char or not hum or hum.Health <= 0 or not char:FindFirstChild("HumanoidRootPart") then return end
 if not player:FindFirstChildOfClass("Backpack") then return end

 local perfil = PlayerData.get(player)
 local id = perfil and perfil.picareta or "enferrujada"
 local naMao = char:FindFirstChild("Picareta")
 if naMao and naMao:GetAttribute("PicaretaId") == id then return end

 -- ja existe a certa na mochila (jogador desequipou): so reequipa, sem reconstruir
 local guardada = player.Backpack:FindFirstChild("Picareta")
 if not naMao and guardada and guardada:GetAttribute("PicaretaId") == id then
  hum:EquipTool(guardada)
  return
 end

 for _, onde in ipairs({ player.Backpack, char }) do
  local velha = onde:FindFirstChild("Picareta")
  if velha then velha:Destroy() end
 end

 local tool = construir(id)
 if not tool then return end
 tool.Parent = player.Backpack
 if player.Character == char and hum.Parent == char then hum:EquipTool(tool) end
end

local function acompanhar(player)
 player.CharacterAdded:Connect(function(char)
  task.wait(0.6)
  garantir(player)
  char.ChildRemoved:Connect(function(filho)
   -- saiu da mao: devolve no frame seguinte (evita brigar com o proprio EquipTool)
   if filho.Name == "Picareta" then task.defer(garantir, player) end
  end)
 end)
end

Players.PlayerAdded:Connect(acompanhar)
for _, p in ipairs(Players:GetPlayers()) do
 acompanhar(p)
 if p.Character then task.spawn(garantir, p) end
end

-- vigia: cobre morte, respawn, troca de picareta comprada e qualquer remocao que escape dos eventos
task.spawn(function()
 while true do
  task.wait(0.4)
  for _, p in ipairs(Players:GetPlayers()) do
   local ok, err = pcall(garantir, p)
   if not ok then warn("[PicaretaTool] " .. tostring(err)) end
  end
 end
end)
