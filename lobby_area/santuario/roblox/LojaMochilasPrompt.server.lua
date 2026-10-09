-- ServerScriptService.LojaMochilasPrompt (instalado no Studio do AMS em 2026-10-09)
-- LojaMochilasPrompt: o vendedor de mochilas (lobby Santuario, dentro da loja-mochila) abre a loja por ProximityPrompt.
-- Dispara o mesmo Remotes.AbrirLoja que o PadLoja usava (o AMS_UI abre a janela do Ignis na aba de mochilas).
-- O PadLoja ficou com CanTouch = false no Edit: so o prompt abre a loja.
local Players = game:GetService('Players')
local RS = game:GetService('ReplicatedStorage')
local R = RS:WaitForChild('Remotes')
local abrir = R:WaitForChild('AbrirLoja')

local NOMES = {'Vebdedor suspeito', 'npc vendedor ', 'npc vendedor'}
local function acharVendedor()
	for _, c in ipairs(workspace:GetChildren()) do
		if c:IsA('Model') and c:GetAttribute('VendedorMochilas') then return c end
	end
	for _, n in ipairs(NOMES) do
		local c = workspace:FindFirstChild(n)
		if c then return c end
	end
	local npcs = workspace:FindFirstChild('NPCs')
	for _, n in ipairs(NOMES) do
		local c = npcs and npcs:FindFirstChild(n)
		if c then return c end
	end
	return nil
end

local vendedor = acharVendedor()
local t0 = os.clock()
while not vendedor and os.clock() - t0 < 30 do task.wait(1); vendedor = acharVendedor() end
if not vendedor then warn('LojaMochilasPrompt: vendedor de mochilas nao encontrado'); return end
local alvo = vendedor:FindFirstChild('HumanoidRootPart') or vendedor.PrimaryPart or vendedor:FindFirstChild('Head')
if not alvo then warn('LojaMochilasPrompt: vendedor sem HumanoidRootPart'); return end

for _, d in ipairs(vendedor:GetDescendants()) do
	if d:IsA('ProximityPrompt') and d.Name == 'LojaPrompt' then d:Destroy() end
end
local pr = Instance.new('ProximityPrompt')
pr.Name = 'LojaPrompt'
pr.ActionText = 'Comprar mochilas'
pr.ObjectText = 'Vendedor de Mochilas'
pr.KeyboardKeyCode = Enum.KeyCode.E
pr.HoldDuration = 0
pr.MaxActivationDistance = 11
pr.RequiresLineOfSight = false
pr.UIOffset = Vector2.new(0, 0)
pr.Parent = alvo

local ultimo = {}
pr.Triggered:Connect(function(pl)
	local root = pl.Character and pl.Character:FindFirstChild('HumanoidRootPart')
	if not root or (root.Position - alvo.Position).Magnitude > 16 then return end
	if ultimo[pl] and os.clock() - ultimo[pl] < 0.8 then return end
	ultimo[pl] = os.clock()
	abrir:FireClient(pl)
end)
Players.PlayerRemoving:Connect(function(pl) ultimo[pl] = nil end)
