-- Ilha 2 "Dragon Ball". Modelada no Blender (pasta ilha_dragonball/), montada no Studio por montar_ilha_dragonball.lua
-- e guardada em ServerStorage.IlhaDragonBall. Aqui a ilha e clonada para a Area 2 e ligada aos sistemas que JA
-- existem (nada de sistema novo), como a Ilha 1 (Core.NarutoIsland):
--  * encaixe: a ilha ja sai do export no lugar certo (WORLD_FROM_PREV = ISLAND_NEXT_ANCHOR da Ilha 1); a ponte de
--    chegada encosta na cabeceira da Ilha 1 (a guarda provisoria de la sai na integracao).
--  * minerios: pontos ORE_* (so POSICAO; variante/raridade do SpawnMinerio) + grade hexagonal na bacia + zona
--    MiningZone_DragonBall com bloqueios GP_Block_* (rochas, pod, acessos, anel junto ao muro). A bacia fica so 4
--    abaixo do chao: a zona usa piso-1,5 como referencia (janela -1..+5 do SpawnMinerio vai ate 23,7 < chao 24,2).
--  * invocacao: a maquina Gacha_<tema> vira o motor invisivel da torre (prompt no portal, pad na praca).
--  * portao SHADOW GARDEN: peca NextAreaId=4 no patio (o Core.Main liga o prompt: bloqueado -> compra pela UI de
--    sempre; liberado -> viajar) + placa de preco; estado da barreira por jogador no cliente (perfil.areas[4]).
--  * regiao: BoundsCenter/BoundsHalfSize (caixa da ilha no mundo) para o IslandTravel decidir a area por regiao.
local SS = game:GetService('ServerStorage')
local CS = game:GetService('CollectionService')
local RS = game:GetService('ReplicatedStorage')
local M = {}
local V = Vector3.new
local C = Color3.fromRGB
local HRP = 3.5
M.PASSO_HEX = 7.5
M.GATE_KEY = 'ShadowGarden'
M.GATE_AREA = 4

local function peca(nome, tam, cf, pai)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1
	p.Parent = pai
	return p
end

local TEX = {
	fumaca = 'rbxasset://textures/particles/smoke_main.dds',
	brilho = 'rbxasset://textures/particles/sparkles_main.dds',
}
local function emissor(pai, nome, pos, s)
	local a = peca('VFX_' .. nome, s.area or V(1, 1, 1), CFrame.new(pos), pai)
	local e = Instance.new('ParticleEmitter')
	e.Name = nome
	e.Texture = TEX[s.tex or 'fumaca']
	e.Color = ColorSequence.new(s.cor)
	e.Rate = s.rate
	e.Lifetime = NumberRange.new(s.vida * 0.7, s.vida)
	e.Speed = NumberRange.new(s.vel * 0.4, s.vel)
	e.SpreadAngle = s.spread or Vector2.new(40, 40)
	e.Acceleration = s.acc or V(0, 0, 0)
	e.LightEmission = s.luz or 0.2
	e.LightInfluence = s.infl or 1
	e.Rotation = NumberRange.new(0, 360)
	e.RotSpeed = NumberRange.new(-12, 12)
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, s.tam * 0.5), NumberSequenceKeypoint.new(0.5, s.tam),
		NumberSequenceKeypoint.new(1, s.tam * (s.fim or 0.6)) })
	local t0 = s.transp or 0.55
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, t0),
		NumberSequenceKeypoint.new(0.75, math.min(1, t0 + 0.25)), NumberSequenceKeypoint.new(1, 1) })
	if s.forma then e.Shape = s.forma; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume end
	e:SetAttribute('Dist', s.dist or 260)
	e:SetAttribute('Rate0', s.rate)
	CS:AddTag(e, 'IlhaVFX')
	e.Parent = a
	return e
end

local function mpos(mk, n, dy)
	local m = mk[n]
	return m and (m.Position + V(0, dy or 0, 0)) or nil
end

local function fwd(mk, n)
	local m = mk[n]
	if not m then return V(0, 0, 1) end
	local fx, fz = m:GetAttribute('fwd_x'), m:GetAttribute('fwd_z')
	if fx and fz then return V(fx, 0, fz).Unit end
	return m.CFrame.UpVector
end

-- VFX baratos: energia do summon, nevoa das quedas, brilho do portao roxo (o cliente faz culling por distancia)
local function vfx(model, mk)
	local pasta = Instance.new('Folder'); pasta.Name = 'VFX_Integracao'; pasta.Parent = model
	local sm = mpos(mk, 'SUMMON_Main')
	if sm then
		emissor(pasta, 'Sum_Energia', sm + V(0, 2, 0), { tex = 'brilho', cor = C(255, 170, 70), rate = 4, vida = 2.8, vel = 0.9,
			tam = 0.45, fim = 0.2, acc = V(0, 1.4, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(10, 1, 10),
			forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	end
	for _, m in pairs(mk) do
		if string.match(m.Name, '^FX_Fall') then
			emissor(pasta, 'Agua_Nevoa_' .. m.Name, m.Position, { cor = C(214, 238, 250), rate = 1.6, vida = 4, vel = 1.2,
				tam = 9, fim = 1.2, acc = V(0, 0.6, 0), transp = 0.78, area = V(12, 2, 12),
				forma = Enum.ParticleEmitterShape.Box, dist = 320 })
		end
	end
	local g = mpos(mk, 'GATE_' .. M.GATE_KEY)
	if g then
		emissor(pasta, 'Portao_' .. M.GATE_KEY, g + V(0, 9, 0), { tex = 'brilho', cor = C(190, 120, 255), rate = 3, vida = 2,
			vel = 0.7, tam = 0.4, fim = 0.2, acc = V(0, 1, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(10, 16, 10),
			forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	end
end

-- a maquina de gacha vira o motor invisivel da torre (o mesmo esquema da Ilha 1)
local function invocacao(area, mk)
	local machine = workspace:FindFirstChild('Gachas') and workspace.Gachas:FindFirstChild('Gacha_' .. area.tema)
	local pad = machine and machine:FindFirstChild('PadGacha')
	local cab
	for _, d in ipairs(machine and machine:GetDescendants() or {}) do
		if d:IsA('BasePart') and string.find(d.Name:lower(), 'cabinet_body') then cab = d break end
	end
	local inter, jog = mk.SUMMON_Interact, mk.SUMMON_PlayerPosition
	if not (pad and cab and inter and jog) then warn('[DragonBallIsland] maquina de gacha/marcadores de invocacao faltando') return nil end
	local frente = (jog.Position - inter.Position) * V(1, 0, 1)
	frente = frente.Magnitude > 0.1 and frente.Unit or V(0, 0, 1)
	local atual = (pad.Position - cab.Position) * V(1, 0, 1)
	local ang = math.atan2(frente.X, frente.Z) - math.atan2(atual.Unit.X, atual.Unit.Z)
	local rot = CFrame.Angles(0, ang, 0)
	if (rot:VectorToWorldSpace(atual.Unit) - frente).Magnitude > 0.05 then rot = CFrame.Angles(0, -ang, 0) end
	local alvo = V(inter.Position.X, inter.Position.Y + 2.5, inter.Position.Z)
	machine:PivotTo(CFrame.new(alvo) * rot * CFrame.new(-cab.Position) * machine:GetPivot())
	local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { machine }; params.RespectCanCollide = true
	local chao = workspace:Raycast(pad.Position + V(0, 20, 0), V(0, -40, 0), params)
	local piso = chao and chao.Position.Y or inter.Position.Y
	pad.Size = V(10, 0.25, 10)
	pad.CFrame = CFrame.new(pad.Position.X, piso - 0.9, pad.Position.Z) * (pad.CFrame - pad.CFrame.Position)
	pad.CanCollide = false; pad.CanTouch = false; pad.CanQuery = false; pad.CastShadow = false
	for _, d in ipairs(machine:GetDescendants()) do
		if d:IsA('BasePart') and d ~= pad then
			d.Transparency = 1; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.CastShadow = false
		elseif d:IsA('Light') or d:IsA('ParticleEmitter') or d:IsA('Beam') or d:IsA('Trail') then
			d.Enabled = false
		elseif d:IsA('BillboardGui') then
			d.MaxDistance = 45
		end
	end
	local placa = machine:FindFirstChild('PlacaGacha')
	if placa then placa.CFrame = CFrame.new(inter.Position + V(0, 13, 0)) end
	machine:SetAttribute('MotorDaTorre', 'Ilha Dragon Ball: maquina invisivel, visual = torre de invocacao')
	return V(pad.Position.X, piso + HRP, pad.Position.Z)
end

-- portao Shadow Garden: interacao (NextAreaId) + placa de preco + ponto de viagem na ancora
local function portao(model, mk, Config)
	local key = M.GATE_KEY
	local prox = Config.areaPorId(M.GATE_AREA)
	local gi, ui, anc = mk['GATE_' .. key .. '_INTERACT'], mk['PURCHASE_UI_ANCHOR_' .. key], mk['ISLAND_NEXT_ANCHOR_' .. key]
	if not (prox and gi and ui and anc) then warn('[DragonBallIsland] marcadores do portao ' .. key .. ' faltando') return end
	local pasta = Instance.new('Folder'); pasta.Name = 'PORTAO_' .. key .. '_Integracao'; pasta.Parent = model
	local inter = peca('Portao' .. key .. '_Interacao', V(6, 6, 6), CFrame.new(gi.Position + V(0, 3, 0)), pasta)
	inter:SetAttribute('NextAreaId', prox.id)
	inter:SetAttribute('Portao', key)
	local a = peca('Portao' .. key .. '_UI', V(1, 1, 1), CFrame.new(ui.Position), pasta)
	local bb = Instance.new('BillboardGui'); bb.Name = 'CompraPortao'; bb.Size = UDim2.fromOffset(230, 84)
	bb.MaxDistance = 90; bb.LightInfluence = 0; bb.Parent = a
	bb:SetAttribute('Portao', key)
	local function txt(n, y, h, s, cor, font)
		local t = Instance.new('TextLabel'); t.Name = n; t.BackgroundTransparency = 1; t.Size = UDim2.new(1, 0, 0, h)
		t.Position = UDim2.fromOffset(0, y); t.Text = s; t.TextScaled = true; t.Font = font or Enum.Font.GothamBlack
		t.TextColor3 = cor; t.TextStrokeTransparency = 0.35; t.Parent = bb
	end
	txt('Nome', 0, 30, string.upper(prox.nome), C(206, 160, 255))
	txt('Custo', 32, 28, 'Custo: ' .. Config.formatar(prox.custo) .. ' moedas', C(255, 255, 255), Enum.Font.GothamBold)
	txt('Dica', 62, 20, 'Interaja no portao para desbloquear', C(225, 225, 235), Enum.Font.GothamMedium)
	local f = fwd(mk, 'ISLAND_NEXT_ANCHOR_' .. key)
	local pv = anc.Position - f * 5
	local disco = Instance.new('Part'); disco.Name = 'ViagemProximaArea'; disco.Shape = Enum.PartType.Cylinder
	disco.Size = V(0.2, 9, 9); disco.CFrame = CFrame.new(pv.X, anc.Position.Y + 0.1, pv.Z) * CFrame.Angles(0, 0, math.rad(90))
	disco.Anchored = true; disco.CanCollide = false; disco.CanQuery = false; disco.CanTouch = false; disco.CastShadow = false
	disco.Material = Enum.Material.Neon; disco.Color = C(170, 110, 255); disco.Transparency = 0.72
	disco:SetAttribute('NextAreaId', prox.id)
	disco.Parent = pasta
end

-- caixa da ilha no mundo (regiao do IslandTravel): todas as pecas menos o fundo (ilhotas de skyline)
local function caixa(model)
	local mn, mx = V(math.huge, math.huge, math.huge), V(-math.huge, -math.huge, -math.huge)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and not string.match(d.Name, '^DB_Sky_') and d.Name ~= 'VOID_CATCH' and d.Size.Magnitude < 900 then
			local h = d.Size / 2
			mn = mn:Min(d.Position - h); mx = mx:Max(d.Position + h)
		end
	end
	return (mn + mx) / 2, (mx - mn) / 2
end

function M.build(parent, area)
	local Config = require(RS.Config)
	local source = SS:FindFirstChild('IlhaDragonBall')
	assert(source, '[DragonBallIsland] ServerStorage.IlhaDragonBall nao encontrado')
	parent.ModelStreamingMode = Enum.ModelStreamingMode.PersistentPerPlayer
	local model = source:Clone()
	model.Name = 'ILHA_DRAGONBALL'
	model.Parent = parent
	local mk = {}
	for _, m in ipairs(model.GAMEPLAY_MARKERS:GetChildren()) do mk[m.Name] = m end

	local ent = mpos(mk, 'WORLD_ENTRY_DragonBall') or V(-258.6, 24.4, 678.6)
	local fe = fwd(mk, 'WORLD_ENTRY_DragonBall')
	parent:SetAttribute('WorldRevision', 1)
	parent:SetAttribute('EntryPosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z))
	parent:SetAttribute('EntryForward', fe)
	parent:SetAttribute('SafePosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z) + fe * 8)
	parent:SetAttribute('RotaPropria', true)
	parent:SetAttribute('SafeMaxY', 40)           -- IslandTravel: salva posicao segura em todos os pisos (ate o Capsule)
	local bc, bh = caixa(model)
	parent:SetAttribute('BoundsCenter', V(bc.X, 0, bc.Z))
	parent:SetAttribute('BoundsHalfSize', V(bh.X + 10, 130, bh.Z + 10))
	local anc = mk['ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY]
	if anc then
		parent:SetAttribute('NextAnchorPosition', anc.Position)
		parent:SetAttribute('NextAnchorForward', fwd(mk, 'ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY))
		parent:SetAttribute('NextAnchorWidth', 18)
		parent:SetAttribute('NextAnchorClearHeight', 22)
		parent:SetAttribute('NextAnchorKey', M.GATE_KEY)
	end
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and string.match(d.Name, '^COL_') then d:SetAttribute('TravessiaKeep', true) end
	end

	local gacha = invocacao(area, mk)
	if gacha then parent:SetAttribute('GachaPosition', gacha) end
	portao(model, mk, Config)
	vfx(model, mk)

	-- minerio: zona e bloqueios a partir dos marcadores do export
	local zm = mk.MiningZone_DragonBall
	local piso = zm and zm.Position.Y or 20.2
	local blocos = {}
	local bmn, bmx = V(math.huge, 0, math.huge), V(-math.huge, 0, -math.huge)
	for n, m in pairs(mk) do
		if string.match(n, '^GP_Block_') then
			local r = m:GetAttribute('radius') or 6
			table.insert(blocos, { pos = m.Position, raio = r })
			if m:GetAttribute('kind') == 'borda' then
				bmn = bmn:Min(m.Position); bmx = bmx:Max(m.Position)
			end
		end
	end
	local zc = zm and V(zm.Position.X, piso - 1.5, zm.Position.Z) or V((bmn.X + bmx.X) / 2, piso - 1.5, (bmn.Z + bmx.Z) / 2)
	local zt = V(bmx.X - bmn.X, 0, bmx.Z - bmn.Z)
	local function bloqueado(p)
		for _, b in ipairs(blocos) do
			if (V(b.pos.X, 0, b.pos.Z) - V(p.X, 0, p.Z)).Magnitude < b.raio then return true end
		end
		return false
	end
	local ov = OverlapParams.new(); ov.FilterType = Enum.RaycastFilterType.Exclude; ov.RespectCanCollide = true
	local spawns, fora = {}, 0
	for n, m in pairs(mk) do
		if string.match(n, '^ORE_') then
			local p = m.Position
			if not bloqueado(p) and #workspace:GetPartBoundsInBox(CFrame.new(p + V(0, 5, 0)), V(7, 8, 7), ov) == 0 then
				table.insert(spawns, { pos = p })
			else
				fora += 1
			end
		end
	end
	table.sort(spawns, function(a, b) return a.pos.Z < b.pos.Z or (a.pos.Z == b.pos.Z and a.pos.X < b.pos.X) end)
	parent:SetAttribute('OrePontosMarcadores', #spawns)
	parent:SetAttribute('OreMarcadoresFora', fora)
	-- grade hexagonal no piso da bacia (so onde o raio bate no piso da arena, fora dos bloqueios, caixa 7x8x7 livre)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.RespectCanCollide = true
	local hx = 0
	local lin = math.ceil(zt.Z / 2 / (M.PASSO_HEX * 0.866))
	local col = math.ceil(zt.X / 2 / M.PASSO_HEX) + 1
	for row = -lin, lin do
		for c = -col, col do
			local x = c * M.PASSO_HEX + ((row % 2 == 0) and 0 or M.PASSO_HEX / 2)
			local z = row * M.PASSO_HEX * 0.866
			local p = V(zc.X + x, piso, zc.Z + z)
			if not bloqueado(p) then
				local hit = workspace:Raycast(p + V(0, 12, 0), V(0, -30, 0), rp)
				if hit and hit.Normal.Y > 0.85 and math.abs(hit.Position.Y - piso) < 0.5
					and #workspace:GetPartBoundsInBox(CFrame.new(hit.Position + V(0, 5, 0)), V(7, 8, 7), ov) == 0 then
					table.insert(spawns, { pos = hit.Position }); hx += 1
				end
			end
		end
	end
	parent:SetAttribute('OrePontosGrade', hx)
	local z = peca('MiningZone_DragonBall', V(zt.X, 1, zt.Z), CFrame.new(zc), model)
	z:SetAttribute('PisoY', piso)

	local sl = mk.ORE_SUPERLEGENDARY_01 or mk.ORE_EPIC_01
	local boss = sl and sl.Position or (zc + V(0, 1.5, 0))
	local volta = V(ent.X, ent.Y - 0.05, ent.Z) + V(-fe.Z, 0, fe.X) * 12
	return { spawns = spawns, boss = boss, returnPad = volta,
		zonas = { lista = { { nome = 'MiningZone_DragonBall', centro = zc, tamanho = zt } }, bloqueios = blocos } }
end

return M
