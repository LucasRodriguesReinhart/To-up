-- Ilha Naruto (cliente): estado do portao DB POR JOGADOR, culling dos VFX por distancia e pulsos lentos.
-- Nada aqui decide progresso: o estado vem do snapshot do servidor (PlayerData -> AtualizarDados / PedirDados,
-- campo areas). A compra continua sendo Progresso.comprarArea (prompt do Core.Main na peca NextAreaId).
local Players = game:GetService('Players')
local RS = game:GetService('ReplicatedStorage')
local CS = game:GetService('CollectionService')
local RunService = game:GetService('RunService')

local Portoes = require(RS:WaitForChild('PortoesCompra'))
local Remotes = RS:WaitForChild('Remotes')
local AREA_DB = 2

local liberado = false
local placas, prompts = {}, {}
local function aplicarUI(d)
	if placas[d] then d.Enabled = not liberado end
	if prompts[d] then d.ActionText = liberado and 'Viajar' or 'Desbloquear' end
end
local function registrarUI(d)
	if d.Name == 'CompraPortao' and d:IsA('BillboardGui') then
		placas[d] = true; aplicarUI(d)
	elseif d.Name == 'ViajarArea' and d:IsA('ProximityPrompt') and d.Parent and d.Parent.Name == 'PortaoDB_Interacao' then
		prompts[d] = true; aplicarUI(d)
	end
end
local function aplicarPortao()
	Portoes.Estado('DB', liberado)
	for d in pairs(placas) do if d.Parent then aplicarUI(d) else placas[d] = nil end end
	for d in pairs(prompts) do if d.Parent then aplicarUI(d) else prompts[d] = nil end end
end
local primeiro = true
local function lerSnapshot(snap)
	if type(snap) ~= 'table' or type(snap.areas) ~= 'table' then return end
	local v = snap.areas[AREA_DB]
	if v == nil then v = snap.areas[tostring(AREA_DB)] end
	local novo = v == true
	if novo ~= liberado or primeiro then
		primeiro = false
		liberado = novo
		aplicarPortao()
	end
end
-- com StreamingEnabled a placa/prompt chegam depois
workspace.DescendantAdded:Connect(registrarUI)
local areas = workspace:FindFirstChild('Areas')
if areas then for _, d in ipairs(areas:GetDescendants()) do registrarUI(d) end end
Remotes:WaitForChild('AtualizarDados').OnClientEvent:Connect(lerSnapshot)
task.spawn(function()
	local ok, snap = pcall(function() return Remotes:WaitForChild('PedirDados'):InvokeServer() end)
	if ok then lerSnapshot(snap) end
end)

-- ---------- VFX: culling por distancia + pulsos ----------
local emissores, pulsos, barreiras, abertos = {}, {}, {}, {}
local function acompanhar(tag, lista, filtro)
	local function add(d) if not filtro or filtro(d) then lista[d] = true end end
	for _, d in ipairs(CS:GetTagged(tag)) do add(d) end
	CS:GetInstanceAddedSignal(tag):Connect(add)
	CS:GetInstanceRemovedSignal(tag):Connect(function(d) lista[d] = nil end)
end
acompanhar('IlhaVFX', emissores)
acompanhar('IlhaPulso', pulsos)
acompanhar('PortaoCompra', barreiras, function(d) return d:GetAttribute('gate_part') == 'barrier' end)
acompanhar('PortaoCompra', abertos, function(d) return d:GetAttribute('gate_part') == 'openglow' end)

-- culling (2x por segundo): emissor longe da camera nao emite
task.spawn(function()
	while true do
		local cam = workspace.CurrentCamera
		local c = cam and cam.CFrame.Position
		if c then
			for e in pairs(emissores) do
				local p = e.Parent
				if p and p:IsA('BasePart') then
					if e.Name == 'Portao_DB' then
						-- portao: faiscas quando bloqueado, bem mais calmo depois de liberado
						e.Rate = liberado and 0.8 or (e:GetAttribute('Rate0') or 3)
					end
					e.Enabled = (p.Position - c).Magnitude <= (e:GetAttribute('Dist') or 260)
				end
			end
		end
		task.wait(0.5)
	end
end)

-- pulsos lentos (30 Hz, so perto): cristais da torre respiram, barreira do portao ondula
local acc = 0
RunService.Heartbeat:Connect(function(dt)
	acc += dt
	if acc < 1 / 30 then return end
	acc = 0
	local cam = workspace.CurrentCamera
	if not cam then return end
	local c = cam.CFrame.Position
	local t = os.clock()
	for d in pairs(pulsos) do
		if d.Parent and (d.Position - c).Magnitude < 360 then
			local c0 = d:GetAttribute('Cor0')
			if typeof(c0) == 'Color3' then
				local k = 0.5 + 0.5 * math.sin(t * 1.3 + d.Position.Y * 0.05) -- ~4.8 s por ciclo
				d.Color = Color3.new(c0.R * 0.8, c0.G * 0.8, c0.B * 0.8):Lerp(c0, k)
			end
		end
	end
	for d in pairs(barreiras) do
		if d.Parent and not liberado and (d.Position - c).Magnitude < 260 then
			local t0 = d:GetAttribute('t0') or 0.2
			d.Transparency = math.clamp(t0 + 0.14 * (0.5 + 0.5 * math.sin(t * 1.6)), 0, 0.95)
		end
	end
	for d in pairs(abertos) do
		if d.Parent and liberado and (d.Position - c).Magnitude < 260 then
			d.Transparency = 0.45 + 0.15 * (0.5 + 0.5 * math.sin(t * 0.7)) -- calmo
		end
	end
end)
