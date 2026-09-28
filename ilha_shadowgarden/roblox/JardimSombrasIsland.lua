-- Ilha 3 "Shadow Garden" (Jardim das Sombras). Modelada no Blender (pasta ilha_shadowgarden/), montada no Studio por
-- montar_ilha_shadowgarden.lua e guardada em ServerStorage.IlhaShadowGarden. Aqui a ilha e clonada para a area de tema
-- sombra (id 3 desde a troca 3<->4) e ligada aos sistemas que JA existem, no mesmo contrato das Ilhas 1 e 2:
--  * encaixe: a ilha ja sai do export no lugar certo (WORLD_FROM_PREV = ISLAND_NEXT_ANCHOR_ShadowGarden da Ilha 2);
--    a guarda provisoria da ponta da Ilha 2 sai no DragonBallIsland quando esta fonte existe.
--  * mineracao DENTRO do castelo (Mining Hall): pontos ORE_* + grade hexagonal no piso do salao + zona
--    MiningZone_ShadowGarden com bloqueios GP_Block_* (corredor da porta, anel junto as paredes).
--  * invocacao: a maquina Gacha_sombra vira o motor invisivel da torre (prompt na torre, pad na praca da plataforma).
--  * portao DEMON SLAYER: peca NextAreaId=4 na ilhota (o Core.Main liga o prompt: bloqueado -> compra pela UI de sempre)
--    + placa de preco; estado da barreira por jogador no cliente (ILHAS_Cliente).
--  * Alquimia e Masmorra: os servicos (CraftService/DungeonService) leem os marcadores CRAFT_* / DUNGEON_* / DUN_*.
--  * regiao: BoundsCenter/BoundsHalfSize (o Config.centro desta area fica longe da ilha).
local SS = game:GetService('ServerStorage')
local CS = game:GetService('CollectionService')
local RS = game:GetService('ReplicatedStorage')
local M = {}
local V = Vector3.new
local C = Color3.fromRGB
local HRP = 3.5
M.PASSO_HEX = 7.5
M.GATE_KEY = 'DemonSlayer'
M.GATE_AREA = 4        -- Monte Natagumo (troca 3<->4)

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

-- VFX com funcao (hierarquia: portal da dungeon > invocacao > portao > quedas). Nada de particula decorativa solta.
local function vfx(model, mk)
	local pasta = Instance.new('Folder'); pasta.Name = 'VFX_Integracao'; pasta.Parent = model
	local sm = mpos(mk, 'SUMMON_Main')
	if sm then
		emissor(pasta, 'Sum_Energia', sm + V(0, 6, 0), { tex = 'brilho', cor = C(170, 120, 255), rate = 4, vida = 2.8, vel = 0.9,
			tam = 0.45, fim = 0.2, acc = V(0, 1.4, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(8, 1, 8),
			forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	end
	local dp = mpos(mk, 'DUNGEON_Portal')
	if dp then
		emissor(pasta, 'Dun_Portal', dp + V(0, 7, 0), { tex = 'brilho', cor = C(160, 100, 250), rate = 6, vida = 2.2, vel = 1.2,
			tam = 0.5, fim = 0.2, luz = 0.8, infl = 0.2, transp = 0.3, area = V(8, 10, 1), spread = Vector2.new(10, 10),
			forma = Enum.ParticleEmitterShape.Box, dist = 160 })
	end
	local FX = {
		nevoa_base = { cor = C(200, 214, 240), rate = 1.6, vida = 4, vel = 1.2, tam = 9, fim = 1.2, acc = V(0, 0.6, 0),
			transp = 0.8, area = V(12, 2, 12), forma = Enum.ParticleEmitterShape.Box, dist = 320 },
		nevoa_borda = { cor = C(214, 228, 248), rate = 1.2, vida = 2.6, vel = 0.8, tam = 4, fim = 1.4, acc = V(0, -1.2, 0),
			transp = 0.82, area = V(6, 1, 3), forma = Enum.ParticleEmitterShape.Box, dist = 220 },
	}
	for _, m in pairs(mk) do
		if string.match(m.Name, '^FX_Fall') then
			local s = FX[m:GetAttribute('fx') or ''] or FX.nevoa_base
			emissor(pasta, 'Agua_' .. m.Name, m.Position, s)
		end
	end
	local g = mpos(mk, 'GATE_' .. M.GATE_KEY)
	if g then
		emissor(pasta, 'Portao_' .. M.GATE_KEY, g + V(0, 9, 0), { tex = 'brilho', cor = C(255, 120, 110), rate = 3, vida = 2,
			vel = 0.7, tam = 0.4, fim = 0.2, acc = V(0, 1, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(10, 16, 10),
			forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	end
end

-- a maquina de gacha vira o motor invisivel da torre (o mesmo esquema das Ilhas 1 e 2)
local function invocacao(area, mk)
	local machine = workspace:FindFirstChild('Gachas') and workspace.Gachas:FindFirstChild('Gacha_' .. area.tema)
	local pad = machine and machine:FindFirstChild('PadGacha')
	local cab
	for _, d in ipairs(machine and machine:GetDescendants() or {}) do
		if d:IsA('BasePart') and string.find(d.Name:lower(), 'cabinet_body') then cab = d break end
	end
	local inter, jog = mk.SUMMON_Interact, mk.SUMMON_PlayerPosition
	if not (pad and cab and inter and jog) then warn('[JardimSombrasIsland] maquina de gacha/marcadores de invocacao faltando') return nil end
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
	machine:SetAttribute('MotorDaTorre', 'Ilha Shadow Garden: maquina invisivel, visual = torre de invocacao')
	return V(pad.Position.X, piso + HRP, pad.Position.Z)
end

-- portao Demon Slayer: interacao (NextAreaId, so para COMPRAR: liberado, o cliente desliga o prompt) + placa de preco
local function portao(model, mk, Config)
	local key = M.GATE_KEY
	local prox = Config.areaPorId(M.GATE_AREA)
	local gi, ui = mk['GATE_' .. key .. '_INTERACT'], mk['PURCHASE_UI_ANCHOR_' .. key]
	if not (prox and gi and ui) then warn('[JardimSombrasIsland] marcadores do portao ' .. key .. ' faltando') return end
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
	txt('Nome', 0, 30, string.upper(prox.nome), C(255, 140, 120))
	txt('Custo', 32, 28, 'Custo: ' .. Config.formatar(prox.custo) .. ' moedas', C(255, 255, 255), Enum.Font.GothamBold)
	txt('Dica', 62, 20, 'Interaja no portao para desbloquear', C(225, 225, 235), Enum.Font.GothamMedium)
end

-- caixa da ilha no mundo (regiao do IslandTravel): todas as pecas menos o fundo (ilhotas de skyline)
local function caixa(model)
	local mn, mx = V(math.huge, math.huge, math.huge), V(-math.huge, -math.huge, -math.huge)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and not string.match(d.Name, '^SG_Sky_') and d.Name ~= 'VOID_CATCH' and d.Size.Magnitude < 900 then
			local h = d.Size / 2
			mn = mn:Min(d.Position - h); mx = mx:Max(d.Position + h)
		end
	end
	return (mn + mx) / 2, (mx - mn) / 2
end

function M.build(parent, area)
	local Config = require(RS.Config)
	local source = SS:FindFirstChild('IlhaShadowGarden')
	assert(source, '[JardimSombrasIsland] ServerStorage.IlhaShadowGarden nao encontrado')
	parent.ModelStreamingMode = Enum.ModelStreamingMode.PersistentPerPlayer
	local model = source:Clone()
	model.Name = 'ILHA_SHADOWGARDEN'
	model.Parent = parent
	local mk = {}
	for _, m in ipairs(model.GAMEPLAY_MARKERS:GetChildren()) do mk[m.Name] = m end

	local ent = mpos(mk, 'WORLD_ENTRY_ShadowGarden') or V(-667.6, 36.4, 613.2)
	local fe = fwd(mk, 'WORLD_ENTRY_ShadowGarden')
	parent:SetAttribute('WorldRevision', 1)
	parent:SetAttribute('EntryPosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z))
	parent:SetAttribute('EntryForward', fe)
	parent:SetAttribute('SafePosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z) + fe * 8)
	parent:SetAttribute('RotaPropria', true)
	parent:SetAttribute('SafeMaxY', 60)           -- IslandTravel: salva posicao segura em todos os patamares (ate o P3 52,2)
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
	local st = mpos(mk, 'CRAFT_Station')
	if st then parent:SetAttribute('CraftPosition', st) end
	local dp = mpos(mk, 'DUNGEON_Entrance')
	if dp then parent:SetAttribute('DungeonEntrance', dp) end
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and string.match(d.Name, '^COL_') then d:SetAttribute('TravessiaKeep', true) end
	end

	local gacha = invocacao(area, mk)
	if gacha then parent:SetAttribute('GachaPosition', gacha) end
	portao(model, mk, Config)
	vfx(model, mk)

	-- minerio: zona e bloqueios a partir dos marcadores do export (piso do Mining Hall; teto em piso+28)
	local zm = mk.MiningZone_ShadowGarden
	local piso = zm and zm.Position.Y or 52.2
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
	-- a ilha e GIRADA no mundo (67 graus): o SpawnMinerio so conhece zonas alinhadas aos eixos, entao a zona do salao vira
	-- uma LISTA de celulas 8x8 dentro do retangulo do salao (eixos da ilha: v = frente do marcador, u = direita), e a
	-- grade hexagonal anda nos mesmos eixos. Nada fora do salao (patio no mesmo piso) entra.
	local v = fwd(mk, 'MiningZone_ShadowGarden')
	local u = V(-v.Z, 0, v.X)
	local lx = zm and (zm:GetAttribute('sx') or 76) or 76
	local ly = zm and (zm:GetAttribute('sy') or 78) or 78
	local c0 = zm and zm.Position or zc
	local function mundo(x, y) return V(c0.X, piso, c0.Z) + u * x + v * y end
	local celulas = {}
	for x = -lx / 2 + 4, lx / 2 - 4, 8 do
		for y = -ly / 2 + 4, ly / 2 - 4, 8 do
			local p = mundo(x, y)
			table.insert(celulas, { nome = 'MiningZone_ShadowGarden', centro = V(p.X, piso - 0.5, p.Z), tamanho = V(8, 0, 8) })
		end
	end
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.RespectCanCollide = true
	local hx = 0
	local lin = math.ceil(ly / 2 / (M.PASSO_HEX * 0.866))
	local col = math.ceil(lx / 2 / M.PASSO_HEX) + 1
	for row = -lin, lin do
		for c = -col, col do
			local x = c * M.PASSO_HEX + ((row % 2 == 0) and 0 or M.PASSO_HEX / 2)
			local y = row * M.PASSO_HEX * 0.866
			if math.abs(x) <= lx / 2 - 3 and math.abs(y) <= ly / 2 - 3 then
				local p = mundo(x, y)
				if not bloqueado(p) then
					local hit = workspace:Raycast(p + V(0, 12, 0), V(0, -30, 0), rp)
					if hit and hit.Normal.Y > 0.85 and math.abs(hit.Position.Y - piso) < 0.5
						and #workspace:GetPartBoundsInBox(CFrame.new(hit.Position + V(0, 5, 0)), V(7, 8, 7), ov) == 0 then
						table.insert(spawns, { pos = hit.Position }); hx += 1
					end
				end
			end
		end
	end
	parent:SetAttribute('OrePontosGrade', hx)
	local z = peca('MiningZone_ShadowGarden', V(lx, 1, ly), CFrame.lookAt(V(c0.X, piso - 0.5, c0.Z), V(c0.X, piso - 0.5, c0.Z) + v), model)
	z:SetAttribute('PisoY', piso)

	local sl = mk.ORE_SUPERLEGENDARY_01 or mk.ORE_EPIC_01
	local boss = sl and sl.Position or (zc + V(0, 1.5, 0))
	local volta = V(ent.X, ent.Y - 0.05, ent.Z) + V(-fe.Z, 0, fe.X) * 12
	return { spawns = spawns, boss = boss, returnPad = volta,
		zonas = { lista = celulas, bloqueios = blocos } }
end

return M
