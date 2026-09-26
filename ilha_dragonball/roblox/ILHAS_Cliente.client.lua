-- Ilhas (cliente): estado dos portoes de compra POR JOGADOR (DB -> area 2, ShadowGarden -> area 4, ...), culling dos
-- VFX por distancia e pulsos lentos. Substitui o ILHA_NARUTO_Cliente (mesma logica, generalizada para varias ilhas).
-- Nada aqui decide progresso: o estado vem do snapshot do servidor (PlayerData -> AtualizarDados / PedirDados,
-- campo areas). A compra continua sendo Progresso.comprarArea (prompt do Core.Main na peca NextAreaId).
-- Portao liberado NAO teleporta: o prompt fica desligado para quem ja comprou (atravessa a pe).
local RS = game:GetService('ReplicatedStorage')
local CS = game:GetService('CollectionService')
local RunService = game:GetService('RunService')

local Portoes = require(RS:WaitForChild('PortoesCompra'))
local Remotes = RS:WaitForChild('Remotes')
local GATES = { DB = 2, ShadowGarden = 4, DemonSlayer = 3, OnePiece = 5, OnePunchMan = 6 }

local liberado = {}          -- chave -> bool
local placas, prompts = {}, {}

local function chaveDe(inst)
	local k = inst:GetAttribute('Portao')
	if k then return k end
	local p = inst.Parent
	local nm = p and p.Name or ''
	return string.match(nm, '^Portao(%w+)_') or string.match(nm, '^Portao(%w+)$')
end

local function aplicarUI(d)
	local k = placas[d] or prompts[d]
	if not k then return end
	local ok = liberado[k] == true
	if placas[d] then d.Enabled = not ok end
	-- sem teleporte no portao: liberado, o prompt some e a travessia e a pe (a viagem continua no menu Viajar)
	if prompts[d] then d.ActionText = 'Desbloquear'; d.Enabled = not ok end
end

local function registrarUI(d)
	if d.Name == 'CompraPortao' and d:IsA('BillboardGui') then
		local k = chaveDe(d) or chaveDe(d.Parent or d)
		if k then placas[d] = k; aplicarUI(d) end
	elseif d.Name == 'ViajarArea' and d:IsA('ProximityPrompt') and d.Parent and string.match(d.Parent.Name, '^Portao%w+_Interacao$') then
		local k = chaveDe(d.Parent)
		if k then prompts[d] = k; aplicarUI(d) end
	end
end

local function aplicarTudo()
	for k in pairs(GATES) do Portoes.Estado(k, liberado[k] == true) end
	for d in pairs(placas) do if d.Parent then aplicarUI(d) else placas[d] = nil end end
	for d in pairs(prompts) do if d.Parent then aplicarUI(d) else prompts[d] = nil end end
end

local primeiro = true
local function lerSnapshot(snap)
	if type(snap) ~= 'table' or type(snap.areas) ~= 'table' then return end
	local mudou = primeiro
	for k, id in pairs(GATES) do
		local v = snap.areas[id]
		if v == nil then v = snap.areas[tostring(id)] end
		local novo = v == true
		if liberado[k] ~= novo then liberado[k] = novo; mudou = true end
	end
	primeiro = false
	if mudou then aplicarTudo() end
end

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

task.spawn(function()
	while true do
		local cam = workspace.CurrentCamera
		local c = cam and cam.CFrame.Position
		if c then
			for e in pairs(emissores) do
				local p = e.Parent
				if p and p:IsA('BasePart') then
					local k = string.match(e.Name, '^Portao_(%w+)$')
					if k then e.Rate = liberado[k] and 0.8 or (e:GetAttribute('Rate0') or 3) end
					e.Enabled = (p.Position - c).Magnitude <= (e:GetAttribute('Dist') or 260)
				end
			end
		end
		task.wait(0.5)
	end
end)

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
				local k = 0.5 + 0.5 * math.sin(t * 1.3 + d.Position.Y * 0.05)
				d.Color = Color3.new(c0.R * 0.8, c0.G * 0.8, c0.B * 0.8):Lerp(c0, k)
			end
		end
	end
	for d in pairs(barreiras) do
		local k = d:GetAttribute('gate')
		if d.Parent and not liberado[k] and (d.Position - c).Magnitude < 260 then
			local t0 = d:GetAttribute('t0') or 0.2
			d.Transparency = math.clamp(t0 + 0.14 * (0.5 + 0.5 * math.sin(t * 1.6)), 0, 0.95)
		end
	end
	for d in pairs(abertos) do
		local k = d:GetAttribute('gate')
		if d.Parent and liberado[k] and (d.Position - c).Magnitude < 260 then
			d.Transparency = 0.45 + 0.15 * (0.5 + 0.5 * math.sin(t * 0.7))
		end
	end
end)
