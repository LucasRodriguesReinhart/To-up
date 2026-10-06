-- Ilha 4 "Demon Slayer" (Monte Natagumo). Modelada no Blender (pasta ilha_demonslayer/), montada no Studio por
-- montar_ilha_demonslayer.lua + pos_montagem_demonslayer.lua e guardada em ServerStorage.IlhaDemonSlayer. Aqui a ilha e
-- clonada para a area de tema nichirin (id 4 desde a troca 3<->4) e ligada aos sistemas que JA existem, no mesmo
-- contrato das Ilhas 1, 2 e 3 (Core.JardimSombrasIsland):
--  * encaixe: a ilha ja sai do export no lugar certo (WORLD_FROM_PREV = ISLAND_NEXT_ANCHOR_DemonSlayer da Ilha 3);
--    a guarda provisoria da ponta da Ilha 3 sai no JardimSombrasIsland quando esta fonte existe (patch de 1 bloco).
--  * mineracao A CEU ABERTO na clareira: pontos ORE_* + grade hexagonal no piso 60,2 + zona MiningZone_DemonSlayer
--    (girada com a ilha: vira LISTA de celulas 8x8, como na Ilha 3) com bloqueios GP_Block_* (borda, cantos, corredores).
--  * invocacao: a maquina Gacha_<tema> (nichirin) vira o motor invisivel da torre (prompt na torre, pad no plato).
--  * portao ONE PIECE: peca NextAreaId=5 na cabeceira de saida (o Core.Main liga o prompt: bloqueado -> compra pela UI
--    de sempre) + placa de preco; estado da barreira por jogador no cliente (ILHAS_Cliente, GATES.OnePiece = 5).
--  * agua feita no Roblox a partir dos marcadores da pedra (ds_water): cascata unica, lagoa com CONTORNO (poligono
--    triangulado, nao retangulo), calha do terraco da forja, canal (comeca na linha da boca da lagoa), sangradouro em
--    3 pocos + bica, aqueduto de madeira e poco da roda.
--  * emissores: cada FX_* com atributo vfx='emissor' vira um ParticleEmitter pela receita gravada no marcador (as
--    chaves do emissor() das Ilhas 1 e 3 + acc_up e drift). Pecas moveis (roda, eixo e piloes, aneis do summon) ja
--    vem com a tag IlhaMovel do montar (o LocalScript ILHA_NARUTO_Movel gira/bate): nada a fazer aqui.
--  * regiao: BoundsCenter/BoundsHalfSize (o Config.centro desta area fica longe da ilha).
-- Sem masmorra, sem alquimia, sem trono (nada de CRAFT_/DUNGEON_ aqui).
local SS = game:GetService('ServerStorage')
local CS = game:GetService('CollectionService')
local RS = game:GetService('ReplicatedStorage')
local M = {}
local V = Vector3.new
local C = Color3.fromRGB
local HRP = 3.5
M.PASSO_HEX = 7.5
M.GATE_KEY = 'OnePiece'
M.GATE_AREA = 5            -- Grand Line (One Piece)
M.FONTE = 'IlhaDemonSlayer'
M.NOME = 'ILHA_DEMONSLAYER' -- IlhaMovel (atributo movel_de) e PortoesCompra procuram por este nome
M.FONTE_PROXIMA = 'IlhaOnePiece' -- quando a fonte da ilha 5 existir, a guarda provisoria da ancora OP sai
M.ZONA = 'MiningZone_DemonSlayer'
M.PISO = 60.2              -- T1 (clareira)
M.ENTRADA = V(-1627.95, 54.4, 1040.86)   -- WORLD_ENTRY_DemonSlayer (plano), so se o marcador faltar

local function peca(nome, tam, cf, pai)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1
	p.Parent = pai
	return p
end

-- ------------------------------------------------------------------ leitura dos atributos dos marcadores
-- o export grava cores como "r,g,b" (0-255), pares como "a,b", listas de pontos como "x,y,z;x,y,z" (ja no mundo)
local function numeros(s)
	local t = {}
	for n in string.gmatch(tostring(s or ''), '[%-%d%.]+') do
		local v = tonumber(n)
		if v then table.insert(t, v) end
	end
	return t
end

local function cor3(s, padrao)
	if typeof(s) == 'Color3' then return s end
	local n = numeros(s)
	if #n < 3 then return padrao end
	return C(n[1], n[2], n[3])
end

local function lista(s)
	local t = {}
	for item in string.gmatch(s or '', '[^;]+') do table.insert(t, item) end
	return t
end

local function pontos(s)
	local t = {}
	for _, item in ipairs(lista(s)) do
		local x, y, z = string.match(item, '([%-%d%.]+),([%-%d%.]+),([%-%d%.]+)')
		if x then table.insert(t, V(tonumber(x), tonumber(y), tonumber(z))) end
	end
	return t
end

local function larguras(s)
	local t = {}
	for _, n in ipairs(numeros(s)) do table.insert(t, n) end
	return t
end

local function mpos(mk, n, dy)
	local m = mk[n]
	return m and (m.Position + V(0, dy or 0, 0)) or nil
end

local function fwdDe(m)
	if not m then return V(0, 0, 1) end
	local fx, fz = m:GetAttribute('fwd_x'), m:GetAttribute('fwd_z')
	if fx and fz and (fx ~= 0 or fz ~= 0) then return V(fx, 0, fz).Unit end
	return m.CFrame.UpVector
end

local function fwd(mk, n)
	return fwdDe(mk[n])
end

-- direita (local +X da ilha) a partir da frente (local +Y): a mesma regra u = (-v.Z, 0, v.X) da Ilha 3
local function lado(f)
	return V(-f.Z, 0, f.X)
end

-- referencial LOCAL do projeto -> mundo. Alguns atributos sao 2D LOCAIS (o export so converte 'waypoints' e trios
-- *_pivot/_pos/center): WATER_Pond.mouth e WATER_Flume.pit_rect. A origem vem do WORLD_FROM_PREV, que no projeto
-- fica em (0, -bridge_len) e olha para +Y local.
local function conversorLocal(mk)
	local w = mk.WORLD_FROM_PREV
	if not w then return nil end
	local f = fwdDe(w)
	local r = lado(f)
	local y0 = -(w:GetAttribute('bridge_len') or 100)
	local o = w.Position
	return function(x, y, alt)
		local p = o + r * x + f * (y - y0)
		return V(p.X, alt or o.Y, p.Z)
	end, f, r
end

-- ------------------------------------------------------------------ emissores (mesmo emissor() das Ilhas 1 e 3)
local TEX = {
	fumaca = 'rbxasset://textures/particles/smoke_main.dds',
	brilho = 'rbxasset://textures/particles/sparkles_main.dds',
	nevoa = 'rbxassetid://534953301',
	gota = 'rbxassetid://1389215359',
}
local function emissor(pai, nome, onde, s)
	local cf = typeof(onde) == 'CFrame' and onde or CFrame.new(onde)
	local a = peca('VFX_' .. nome, s.area or V(1, 1, 1), cf, pai)
	local e = Instance.new('ParticleEmitter')
	e.Name = nome
	e.Texture = TEX[s.tex or 'fumaca'] or TEX.fumaca
	e.Color = typeof(s.cor) == 'ColorSequence' and s.cor or ColorSequence.new(s.cor)
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

-- receitas de reserva (os valores do ds_vfx) para marcador FX_* exportado sem a receita gravada
local PADRAO = {
	fumaca = { tex = 'fumaca', cor = '96,90,88', rate = 3, vida = 9, vel = 3.5, tam = 4.5, fim = 2.6, transp = 0.55, luz = 0.05,
		infl = 1, spread = '10,10', acc_up = 1.3, drift = 0.5, area = '3.4,1,3.4', forma = 'Box', Dist = 400 },
	brasas = { tex = 'brilho', cor = '255,140,60', cor_fim = '255,72,24', rate = 6, vida = 2.2, vel = 2.6, tam = 0.28, fim = 0.15,
		transp = 0.15, luz = 1, infl = 0, spread = '28,28', acc_up = 2.6, drift = 0.6, area = '6.5,3,1.2', forma = 'Box', Dist = 120 },
	nevoa_baixa = { tex = 'nevoa', cor = '176,188,214', rate = 1, vida = 10, vel = 0.5, tam = 14, fim = 1.3, transp = 0.86, luz = 0,
		infl = 1, spread = '90,10', acc_up = 0.05, drift = 0.3, area = '30,1.5,30', forma = 'Box', Dist = 260 },
}

local function formaDe(nome)
	if typeof(nome) ~= 'string' or nome == '' then return Enum.ParticleEmitterShape.Box end
	local ok, f = pcall(function() return Enum.ParticleEmitterShape[nome] end)
	return ok and f or Enum.ParticleEmitterShape.Box
end

-- um emissor a partir do marcador: 'area' = "lado,altura,frente" nos eixos do marcador; aceleracao = acc_up para cima
-- + drift ao longo da frente do marcador (fwd_x, fwd_z). As quedas (FX_Fall_*) nascem no mesmo lugar que a Ilha 3 usa:
-- crista um pouco a frente e abaixo do labio, degrau a frente, pe 4 acima do nivel da agua.
local function receita(pai, m)
	local fx = m:GetAttribute('fx')
	local base = (m:GetAttribute('vfx') ~= 'emissor') and PADRAO[fx or ''] or nil
	local function at(k)
		local v = m:GetAttribute(k)
		if v == nil and base then v = base[k] end
		return v
	end
	local tex = at('tex') or 'fumaca'
	local nev = tex == 'nevoa'
	local tam = at('tam') or 2
	local f = fwdDe(m)
	local l = lado(f)
	local ar = numeros(at('area'))
	local area = (#ar >= 3) and V(ar[1], ar[2], ar[3]) or V(tam, 1, tam)
	local sp = numeros(at('spread'))
	local spread = (#sp >= 2) and Vector2.new(sp[1], sp[2]) or (nev and Vector2.new(70, 70) or Vector2.new(40, 40))
	local acc = V(0, at('acc_up') or (nev and 1.2 or 0), 0) + f * (at('drift') or 0)
	local cor = cor3(at('cor'), C(214, 228, 248))
	local ini, fim = cor3(at('cor_ini')), cor3(at('cor_fim'))
	local seq
	if ini then
		seq = ColorSequence.new({ ColorSequenceKeypoint.new(0, ini), ColorSequenceKeypoint.new(0.3, cor),
			ColorSequenceKeypoint.new(1, cor) })
	elseif fim then
		seq = ColorSequence.new(cor, fim)
	else
		seq = ColorSequence.new(cor)
	end
	local pos = m.Position
	if string.match(m.Name, '^FX_Fall_%d+_Lip$') then
		pos = pos + f * 0.8 - V(0, 1, 0)
	elseif string.match(m.Name, '^FX_Fall_%d+_Step$') then
		pos = pos + f * 1.5
	elseif string.match(m.Name, '^FX_Fall_%d+_Base$') then
		pos = pos + V(0, 4, 0)
	end
	local nome = string.gsub(m.Name, '^FX_', '')
	return emissor(pai, nome, CFrame.fromMatrix(pos, l, V(0, 1, 0)), {
		tex = tex, cor = seq, rate = at('rate') or 2, vida = at('vida') or 3, vel = at('vel') or 1, tam = tam,
		fim = at('fim') or (nev and 1.2 or 0.6), transp = at('transp') or 0.55, luz = at('luz') or 0.1,
		infl = at('infl') or 1, spread = spread, acc = acc, area = area, forma = formaDe(at('forma')),
		dist = at('Dist') or 260 })
end

-- VFX com funcao: fumaca da chamine e do lanternim, brasas da boca, nevoa baixa (bambuzal, ravina), espuma das quedas
-- e o brilho do portao One Piece. Nada de particula decorativa solta.
local function vfx(model, mk)
	local pasta = Instance.new('Folder'); pasta.Name = 'VFX_Integracao'; pasta.Parent = model
	local n = 0
	for nome, m in pairs(mk) do
		if string.match(nome, '^FX_') and m:IsA('BasePart') then
			local fx = m:GetAttribute('fx')
			local queda = string.match(nome, '^FX_Fall_') ~= nil
			-- quedas sem receita ficam com a nevoa da agua() (fallback da Ilha 3)
			if m:GetAttribute('vfx') == 'emissor' or (not queda and PADRAO[fx or '']) then
				receita(pasta, m)
				n += 1
			end
		end
	end
	local g = mpos(mk, 'GATE_' .. M.GATE_KEY)
	if g then
		emissor(pasta, 'Portao_' .. M.GATE_KEY, g + V(0, 9, 0), { tex = 'brilho', cor = C(110, 214, 255), rate = 3, vida = 2,
			vel = 0.7, tam = 0.4, fim = 0.2, acc = V(0, 1, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(10, 16, 10),
			forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	end
	-- brasa da boca da fornalha "respira" devagar (ILHAS_Cliente anima a tag IlhaPulso com a cor base Cor0; culling por
	-- distancia ja e dele)
	local np = 0
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and d.Material == Enum.Material.Neon
			and (string.find(d.Name, 'Ember_DS_Glow', 1, true) or string.find(d.Name, 'Fire_DS_Glow', 1, true)) then
			d:SetAttribute('Cor0', d.Color)
			CS:AddTag(d, 'IlhaPulso')
			np += 1
		end
	end
	print(('[DemonSlayerIsland] %d emissores FX_*, %d pecas de brasa pulsando (IlhaPulso)'):format(n, np))
end

-- ------------------------------------------------------------------ AGUA feita no Roblox
-- O Blender so deixa a pedra estanque e os marcadores (ds_water mediu tudo na pedra):
--   FX_Fall_1_Lip / FX_Fall_2_Lip (waypoints/widths = eixo da cortina, fwd = para fora da rocha);
--   WATER_Pond (waypoints = CONTORNO da agua no nivel, mouth = boca do canal em coordenada LOCAL);
--   WATER_Tailrace / WATER_Channel / WATER_Flume (waypoints/widths = eixo da agua; soleiras = pares de pontos com cota
--   diferente); WATER_Flume.pit_rect/pit_level = poco da roda (LOCAL).
-- Cortina = paineis finos por trecho, face para fora da rocha; canais = os mesmos paineis deitados (face para cima).
-- Texture de agua corrente rolada pelo cliente (tag AguaCorrente, atributo Velocidade; CeuNatagumo/CeuSombras).
-- Espelhos d'agua = Glass + ForceField (brilho animado nativo), a lagoa em triangulos (WedgeParts) pelo contorno.
-- Tudo decorativo: sem colisao nem consulta.
local AGUA = {
	correnteza = 'rbxassetid://1190623231',   -- textura de agua corrente (a mesma da Ilha 3)
	corpo = C(58, 96, 150), claro = C(196, 222, 250), espelho = C(52, 100, 158), brilho = C(150, 196, 240),
}

-- lamina de agua de p0 a p1 (largura media de w0/w1), face para 'fora'; e0/e1 = quanto estica alem de cada ponta;
-- afasta = deslocamento ao longo da normal (camada 1 = brilho, so a textura, 0,06 acima)
local function lamina(pai, nome, p0, p1, w0, w1, fora, camada, e0, e1, vel, afasta, tileV)
	local eixo = p1 - p0
	local len = eixo.Magnitude
	if len < 0.05 then return nil end
	local u = eixo / len
	p0 = p0 - u * e0
	p1 = p1 + u * e1
	len = len + e0 + e1
	local cima = -u
	local f = fora - cima * fora:Dot(cima)
	if f.Magnitude < 1e-3 then return nil end
	f = f.Unit
	local dir = cima:Cross(f)
	local w = (w0 + w1) / 2
	local p = Instance.new('Part')
	p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Size = V(w, len, 0.05)
	p.CFrame = CFrame.fromMatrix((p0 + p1) / 2 + f * (afasta + camada * 0.06), dir, cima)
	p.Material = Enum.Material.SmoothPlastic
	p.Color = AGUA.corpo
	p.Transparency = camada == 0 and 0.28 or 1
	local t = Instance.new('Texture')
	t.Texture = AGUA.correnteza; t.Face = Enum.NormalId.Back
	t.StudsPerTileU = w; t.StudsPerTileV = tileV or (camada == 0 and 10 or 6)
	t.Color3 = AGUA.claro; t.Transparency = camada == 0 and 0.35 or 0.55
	t:SetAttribute('Velocidade', vel)
	CS:AddTag(t, 'AguaCorrente')
	t.Parent = p
	p.Parent = pai
	return p
end

-- quanto um trecho estica na quina (p -> q -> r) para fechar a curva por fora (meia largura x tan(meio angulo))
local function junta(p, q, r, w)
	local d1, d2 = (q - p) * V(1, 0, 1), (r - q) * V(1, 0, 1)
	if d1.Magnitude < 1e-3 or d2.Magnitude < 1e-3 then return 0.05 end
	local t = math.acos(math.clamp(d1.Unit:Dot(d2.Unit), -1, 1))
	return math.min(w, (w / 2) * math.tan(t / 2)) + 0.05
end

-- agua corrente deitada ao longo de uma lista de pontos (canal, calha, aqueduto). sem0 = a primeira ponta nao estica
-- (o canal comeca EXATAMENTE na linha da boca da lagoa: sem duas laminas sobrepostas)
local function fita(pai, nome, pts, ws, vel, sem0)
	local n = #pts
	local cima = V(0, 1, 0)
	local feitos = 0
	for k = 1, n - 1 do
		local a, b = pts[k], pts[k + 1]
		local w0, w1 = ws[k] or ws[#ws] or 3, ws[k + 1] or ws[#ws] or 3
		local e0 = (k == 1) and (sem0 and 0 or 0.05) or junta(pts[k - 1], a, b, w0)
		local e1 = (k == n - 1) and 0.05 or junta(a, b, pts[k + 2], w1)
		if lamina(pai, nome .. '_' .. k, a, b, w0, w1, cima, 0, e0, e1, vel, -0.04, 8) then feitos += 1 end
		lamina(pai, nome .. '_Brilho_' .. k, a, b, w0 * 0.7, w1 * 0.7, cima, 1, e0, e1, vel * 1.5, -0.04, 5)
	end
	return feitos
end

local function nevoa(pai, nome, pos, tam, rate, cor)
	local a = peca('VFX_' .. nome, V(tam, 1, tam), CFrame.new(pos), pai)
	local e = Instance.new('ParticleEmitter')
	e.Name = nome; e.Texture = TEX.nevoa; e.Rate = rate
	e.Lifetime = NumberRange.new(1.6, 2.6); e.Speed = NumberRange.new(1.5, 4)
	e.SpreadAngle = Vector2.new(70, 70); e.Acceleration = V(0, 1.2, 0)
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, tam * 0.35), NumberSequenceKeypoint.new(1, tam * 0.9) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0.55),
		NumberSequenceKeypoint.new(1, 1) })
	e.Color = ColorSequence.new(cor or C(214, 228, 248)); e.LightInfluence = 0.9; e.LightEmission = 0.1
	e.Rotation = NumberRange.new(0, 360); e.RotSpeed = NumberRange.new(-20, 20)
	e.Shape = Enum.ParticleEmitterShape.Box; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
	e:SetAttribute('Dist', 260); e:SetAttribute('Rate0', rate)
	CS:AddTag(e, 'IlhaVFX')
	e.Parent = a
	return e
end

-- respingo de gotas (o mesmo da fonte da Ilha 3)
local function gotas(pai, nome, pos, area, rate, dist)
	local sp = peca(nome, area, CFrame.new(pos), pai)
	local e = Instance.new('ParticleEmitter')
	e.Texture = TEX.gota; e.Rate = rate; e.Lifetime = NumberRange.new(0.35, 0.6)
	e.Speed = NumberRange.new(1.5, 3); e.SpreadAngle = Vector2.new(35, 35); e.Acceleration = V(0, -18, 0)
	e.EmissionDirection = Enum.NormalId.Top
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.18), NumberSequenceKeypoint.new(1, 0.05) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1) })
	e.Color = ColorSequence.new(AGUA.claro); e.LightInfluence = 0.8
	e:SetAttribute('Dist', dist or 120); e:SetAttribute('Rate0', rate)
	CS:AddTag(e, 'IlhaVFX')
	e.Parent = sp
	return e
end

local function cunha(pai, nome, tam, cf, mat, cor, transp)
	local w = Instance.new('WedgePart')
	w.Name = nome; w.Anchored = true; w.CanCollide = false; w.CanQuery = false; w.CanTouch = false; w.CastShadow = false
	w.Size = tam; w.CFrame = cf
	w.Material = mat; w.Color = cor; w.Transparency = transp
	w.TopSurface = Enum.SurfaceType.Smooth; w.BottomSurface = Enum.SurfaceType.Smooth
	w.Parent = pai
	return w
end

-- triangulo a,b,c com 2 WedgeParts (espessura esp, centrada no plano do triangulo)
local function triangulo(pai, nome, a, b, c, esp, mat, cor, transp)
	local ab, ac, bc = b - a, c - a, c - b
	local abd, acd, bcd = ab:Dot(ab), ac:Dot(ac), bc:Dot(bc)
	if abd > acd and abd > bcd then
		c, a = a, c
	elseif acd > bcd and acd > abd then
		a, b = b, a
	end
	ab, ac, bc = b - a, c - a, c - b
	local n = ac:Cross(ab)
	if n.Magnitude < 1e-4 or bc.Magnitude < 1e-3 then return 0 end
	local right = n.Unit
	local up = bc:Cross(right).Unit
	local back = bc.Unit
	local h = math.abs(ab:Dot(up))
	if h < 0.01 then return 0 end
	cunha(pai, nome .. 'a', V(esp, h, math.abs(ab:Dot(back))), CFrame.fromMatrix((a + b) / 2, right, up, back), mat, cor, transp)
	cunha(pai, nome .. 'b', V(esp, h, math.abs(ac:Dot(back))), CFrame.fromMatrix((a + c) / 2, -right, up, -back), mat, cor, transp)
	return 2
end

-- triangulacao por orelhas (ear clipping) de um poligono simples no plano XZ; aceita horario ou anti-horario
local function triangular(pts)
	local q = {}
	local n0 = #pts
	-- tira pontos repetidos e colineares (nao mudam a forma e travariam o corte de orelhas)
	for i = 1, n0 do
		local a, b, c = pts[(i - 2) % n0 + 1], pts[i], pts[i % n0 + 1]
		local cr = (b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X)
		if (b - a).Magnitude > 1e-3 and math.abs(cr) > 1e-4 then table.insert(q, b) end
	end
	local n = #q
	if n < 3 then return {} end
	local s = 0
	for i = 1, n do
		local a, b = q[i], q[i % n + 1]
		s += a.X * b.Z - b.X * a.Z
	end
	local sinal = s > 0 and 1 or -1
	local function cruz(o, a, b)
		return ((a.X - o.X) * (b.Z - o.Z) - (a.Z - o.Z) * (b.X - o.X)) * sinal
	end
	local function dentro(p, a, b, c)
		return cruz(a, b, p) >= 0 and cruz(b, c, p) >= 0 and cruz(c, a, p) >= 0
	end
	local idx = {}
	for i = 1, n do idx[i] = i end
	local tris = {}
	local voltas = 0
	while #idx > 3 and voltas < 4 * n * n do
		voltas += 1
		local achou = false
		local m = #idx
		for k = 1, m do
			local i0, i1, i2 = idx[(k - 2) % m + 1], idx[k], idx[k % m + 1]
			local a, b, c = q[i0], q[i1], q[i2]
			if cruz(a, b, c) > 1e-6 then
				local livre = true
				for _, j in ipairs(idx) do
					if j ~= i0 and j ~= i1 and j ~= i2 and dentro(q[j], a, b, c) then livre = false; break end
				end
				if livre then
					table.insert(tris, { a, b, c })
					table.remove(idx, k)
					achou = true
					break
				end
			end
		end
		if not achou then break end
	end
	if #idx == 3 then table.insert(tris, { q[idx[1]], q[idx[2]], q[idx[3]] }) end
	return tris
end

-- espelho d'agua com o CONTORNO dado (2 camadas: Glass por baixo, ForceField com brilho animado por cima)
local function espelhoPoligono(pai, nome, pts, nivel)
	local plano = {}
	for _, p in ipairs(pts) do table.insert(plano, V(p.X, nivel, p.Z)) end
	local tris = triangular(plano)
	local np = 0
	for i, t in ipairs(tris) do
		local d = V(0, -0.1, 0)
		np += triangulo(pai, nome .. '_Vidro_' .. i, t[1] + d, t[2] + d, t[3] + d, 0.2, Enum.Material.Glass, AGUA.espelho, 0.25)
		local u = V(0, 0.02, 0)
		np += triangulo(pai, nome .. '_Brilho_' .. i, t[1] + u, t[2] + u, t[3] + u, 0.04, Enum.Material.ForceField, AGUA.brilho, 0)
	end
	return #tris, np
end

-- espelho retangular orientado (poco da roda): centro, eixos r (largura) e f (comprimento)
local function espelhoRet(pai, nome, centro, r, f, sx, sy)
	local function placa(n, dy, esp, mat, cor, transp)
		local p = Instance.new('Part')
		p.Name = n; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Size = V(sx, esp, sy)
		p.CFrame = CFrame.fromMatrix(centro + V(0, dy, 0), r, V(0, 1, 0), -f)
		p.Material = mat; p.Color = cor; p.Transparency = transp
		p.Parent = pai
		return p
	end
	placa(nome .. '_Vidro', -0.1, 0.2, Enum.Material.Glass, AGUA.espelho, 0.25)
	placa(nome .. '_Brilho', 0.02, 0.04, Enum.Material.ForceField, AGUA.brilho, 0)
end

-- cortina de queda (cascata, sangradouro): os paineis da Ilha 3, face para fora da rocha
local function cortina(pai, lip, mk, i)
	local fora = fwdDe(lip)
	local pts, ws = pontos(lip:GetAttribute('waypoints')), larguras(lip:GetAttribute('widths'))
	if #pts < 2 then
		local base = mk['FX_Fall_' .. i .. '_Base']
		pts = { lip.Position, base and base.Position or (lip.Position - V(0, 20, 0)) }
		ws = { lip:GetAttribute('width') or 3, (base and base:GetAttribute('width')) or 4 }
	end
	local q = Instance.new('Folder'); q.Name = 'Queda_' .. i; q.Parent = pai
	for k = 1, #pts - 1 do
		local w0, w1 = ws[k] or ws[#ws] or 3, ws[k + 1] or ws[#ws] or 3
		lamina(q, 'Agua_' .. k, pts[k], pts[k + 1], w0, w1, fora, 0, 0.075, 0.075, 14, 0.12)
		lamina(q, 'Brilho_' .. k, pts[k], pts[k + 1], w0 * 0.7, w1 * 0.7, fora, 1, 0.075, 0.075, 22, 0.12)
	end
	-- sem receita no marcador (export antigo): a nevoa da Ilha 3
	if lip:GetAttribute('vfx') ~= 'emissor' then
		local w = lip:GetAttribute('width') or 3
		nevoa(q, 'Crista_' .. i, lip.Position + fora * 0.8 - V(0, 1, 0), w * 0.5, 3)
		local st = mk['FX_Fall_' .. i .. '_Step']
		if st and st:GetAttribute('vfx') ~= 'emissor' then
			nevoa(q, 'Degrau_' .. i, st.Position + fora * 1.5, (st:GetAttribute('width') or w) * 0.8, 8)
		end
		local bs = mk['FX_Fall_' .. i .. '_Base']
		if bs and bs:GetAttribute('vfx') ~= 'emissor' then
			nevoa(q, 'Pe_' .. i, bs.Position + V(0, 4, 0), (bs:GetAttribute('width') or w) * 1.6, 14)
		end
	end
	return #pts
end

local function agua(model, mk, L2W)
	local pasta = Instance.new('Folder'); pasta.Name = 'AGUA_Roblox'; pasta.Parent = model
	local rel = {}
	-- quedas: a cascata unica (forja -> lagoa) e o sangradouro (ravina leste)
	for i = 1, 9 do
		local lip = mk['FX_Fall_' .. i .. '_Lip']
		if lip then table.insert(rel, ('queda %d: %d pontos'):format(i, cortina(pasta, lip, mk, i))) end
	end
	-- lagoa: contorno desenhado (nao retangulo); a boca do canal fica FORA do poligono
	local lagoa = mk.WATER_Pond
	local boca
	if lagoa then
		local nivel = lagoa:GetAttribute('level') or lagoa.Position.Y
		local cont = pontos(lagoa:GetAttribute('waypoints'))
		local f = Instance.new('Folder'); f.Name = 'Lagoa'; f.Parent = pasta
		if #cont >= 3 then
			local nt, np = espelhoPoligono(f, 'Espelho', cont, nivel - 0.06)
			table.insert(rel, ('lagoa: contorno %d pontos -> %d triangulos (%d cunhas)'):format(#cont, nt, np))
			if nt < #cont - 2 - 2 then warn('[DemonSlayerIsland] lagoa: triangulacao incompleta (' .. nt .. ' triangulos)') end
		else
			warn('[DemonSlayerIsland] WATER_Pond sem contorno (waypoints): lagoa nao criada')
		end
		local nb = numeros(lagoa:GetAttribute('mouth'))
		if L2W and #nb >= 4 then boca = (L2W(nb[1], nb[2], nivel) + L2W(nb[3], nb[4], nivel)) / 2 end
	end
	-- calha de cantaria do terraco da forja (roda -> bica da cascata)
	local cal = mk.WATER_Tailrace
	if cal then
		local pts = pontos(cal:GetAttribute('waypoints'))
		local f = Instance.new('Folder'); f.Name = 'Calha'; f.Parent = pasta
		table.insert(rel, ('calha: %d trechos'):format(fita(f, 'Calha', pts, larguras(cal:GetAttribute('widths')), 5, false)))
	end
	-- canal da clareira (lagoa -> pontezinha -> ravina, 3 pocos com soleiras) ate a bica do sangradouro
	local can = mk.WATER_Channel
	if can then
		local pts = pontos(can:GetAttribute('waypoints'))
		if boca and #pts >= 2 then
			local d = (V(pts[1].X, 0, pts[1].Z) - V(boca.X, 0, boca.Z)).Magnitude
			if d < 1.5 then
				pts[1] = V(boca.X, pts[1].Y, boca.Z)
			else
				warn(('[DemonSlayerIsland] o canal comeca a %.2f da boca da lagoa (esperado 0)'):format(d))
			end
		end
		local f = Instance.new('Folder'); f.Name = 'Canal'; f.Parent = pasta
		table.insert(rel, ('canal: %d trechos'):format(fita(f, 'Canal', pts, larguras(can:GetAttribute('widths')), 4, true)))
	end
	-- aqueduto de madeira (nascente -> bico sobre o topo da roda) + poco da roda
	local aq = mk.WATER_Flume
	if aq then
		local pts = pontos(aq:GetAttribute('waypoints'))
		local f = Instance.new('Folder'); f.Name = 'Aqueduto'; f.Parent = pasta
		table.insert(rel, ('aqueduto: %d trechos'):format(fita(f, 'Aqueduto', pts, larguras(aq:GetAttribute('widths')), 7, false)))
		if #pts >= 1 then gotas(f, 'Respingo_Bico', pts[#pts] - V(0, 0.6, 0), V(1.2, 0.2, 1.2), 8, 120) end
		local rr = numeros(aq:GetAttribute('pit_rect'))
		local lv = aq:GetAttribute('pit_level')
		if L2W and #rr >= 4 and lv then
			local _, fl, rl = conversorLocal(mk)
			local c = L2W((rr[1] + rr[3]) / 2, (rr[2] + rr[4]) / 2, lv - 0.06)
			espelhoRet(f, 'PocoRoda', c, rl, fl, math.abs(rr[3] - rr[1]), math.abs(rr[4] - rr[2]))
			gotas(f, 'Espuma_Roda', c + V(0, 0.2, 0), V(math.abs(rr[3] - rr[1]) * 0.6, 0.2, 3), 10, 120)
			table.insert(rel, 'poco da roda: ok')
		end
	end
	print('[DemonSlayerIsland] agua: ' .. table.concat(rel, '; '))
end

-- ------------------------------------------------------------------ invocacao (o mesmo esquema das Ilhas 1, 2 e 3)
local function invocacao(area, mk)
	local machine = workspace:FindFirstChild('Gachas') and workspace.Gachas:FindFirstChild('Gacha_' .. area.tema)
	local pad = machine and machine:FindFirstChild('PadGacha')
	local cab
	for _, d in ipairs(machine and machine:GetDescendants() or {}) do
		if d:IsA('BasePart') and string.find(d.Name:lower(), 'cabinet_body') then cab = d break end
	end
	local inter, jog = mk.SUMMON_Interact, mk.SUMMON_PlayerPosition
	if not (pad and cab and inter and jog) then warn('[DemonSlayerIsland] maquina de gacha/marcadores de invocacao faltando') return nil end
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
	machine:SetAttribute('MotorDaTorre', 'Ilha Demon Slayer: maquina invisivel, visual = torre de invocacao')
	return V(pad.Position.X, piso + HRP, pad.Position.Z)
end

-- portao One Piece: interacao (NextAreaId, so para COMPRAR: liberado, o cliente desliga o prompt) + placa de preco
local function portao(model, mk, Config)
	local key = M.GATE_KEY
	local prox = Config.areaPorId(M.GATE_AREA)
	local gi, ui = mk['GATE_' .. key .. '_INTERACT'], mk['PURCHASE_UI_ANCHOR_' .. key]
	if not (prox and gi and ui) then warn('[DemonSlayerIsland] marcadores do portao ' .. key .. ' faltando') return end
	local aid = mk['GATE_' .. key] and mk['GATE_' .. key]:GetAttribute('area_id')
	if aid and aid ~= prox.id then
		warn(('[DemonSlayerIsland] GATE_%s.area_id = %s, mas o portao vende a area %d'):format(key, tostring(aid), prox.id))
	end
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
	txt('Nome', 0, 30, string.upper(prox.nome), C(120, 214, 255))
	txt('Custo', 32, 28, 'Custo: ' .. Config.formatar(prox.custo) .. ' moedas', C(255, 255, 255), Enum.Font.GothamBold)
	txt('Dica', 62, 20, 'Interaja no portao para desbloquear', C(225, 225, 235), Enum.Font.GothamMedium)
	-- sem disco de viagem na ancora: a travessia e a pe (a ilha One Piece vai encostar no ISLAND_NEXT_ANCHOR_OnePiece)
end

-- caixa da ilha no mundo (regiao do IslandTravel): tudo menos a rede de quedas; extensao girada de cada peca
local function caixa(model)
	local mn, mx = V(math.huge, math.huge, math.huge), V(-math.huge, -math.huge, -math.huge)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and d.Name ~= 'VOID_CATCH' and d.Size.Magnitude < 900 then
			local s = d.Size / 2
			local cf = d.CFrame
			local h = V(math.abs(cf.RightVector.X) * s.X + math.abs(cf.UpVector.X) * s.Y + math.abs(cf.LookVector.X) * s.Z,
				math.abs(cf.RightVector.Y) * s.X + math.abs(cf.UpVector.Y) * s.Y + math.abs(cf.LookVector.Y) * s.Z,
				math.abs(cf.RightVector.Z) * s.X + math.abs(cf.UpVector.Z) * s.Y + math.abs(cf.LookVector.Z) * s.Z)
			mn = mn:Min(d.Position - h); mx = mx:Max(d.Position + h)
		end
	end
	return (mn + mx) / 2, (mx - mn) / 2
end

function M.build(parent, area)
	local Config = require(RS.Config)
	local source = SS:FindFirstChild(M.FONTE)
	assert(source, '[DemonSlayerIsland] ServerStorage.' .. M.FONTE .. ' nao encontrado')
	parent.ModelStreamingMode = Enum.ModelStreamingMode.PersistentPerPlayer
	local model = source:Clone()
	model.Name = M.NOME
	model.Parent = parent
	-- ilha One Piece instalada: a ponte dela encosta no ISLAND_NEXT_ANCHOR_OnePiece, entao sai a guarda provisoria da
	-- ponta (DS_Exit_AnchorGuard + COL_DSAnchorGuard_*, atributo next_island_guard do montar)
	if SS:FindFirstChild(M.FONTE_PROXIMA) then
		for _, d in ipairs(model:GetDescendants()) do
			if d.Parent and d:GetAttribute('next_island_guard') then d:Destroy() end
		end
	end
	local gm = model:FindFirstChild('GAMEPLAY_MARKERS')
	assert(gm, '[DemonSlayerIsland] GAMEPLAY_MARKERS faltando em ServerStorage.' .. M.FONTE)
	local mk = {}
	for _, m in ipairs(gm:GetChildren()) do mk[m.Name] = m end
	local L2W = conversorLocal(mk)

	local ent = mpos(mk, 'WORLD_ENTRY_DemonSlayer') or M.ENTRADA
	local fe = fwd(mk, 'WORLD_ENTRY_DemonSlayer')
	parent:SetAttribute('WorldRevision', 1)
	parent:SetAttribute('EntryPosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z))
	parent:SetAttribute('EntryForward', fe)
	parent:SetAttribute('SafePosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z) + fe * 8)
	parent:SetAttribute('RotaPropria', true)
	parent:SetAttribute('SafeMaxY', 100)          -- IslandTravel: salva posicao segura em todos os patamares (ate T4 80,2)
	parent:SetAttribute('OreMax', 80)
	local bc, bh = caixa(model)
	-- convencao do IslandTravel: centro em Y 0 e teto em BoundsHalfSize.Y (a chamine passa de 150). Sem subsolo: o fundo
	-- fica no padrao (-12), entao queda pela borda e resgatada antes de chegar na quilha (-34) e na rede (-45)
	parent:SetAttribute('BoundsCenter', V(bc.X, 0, bc.Z))
	parent:SetAttribute('BoundsHalfSize', V(bh.X + 10, math.max(130, bc.Y + bh.Y + 10), bh.Z + 10))
	parent:SetAttribute('BoundsMinY', -12)
	local anc = mk['ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY]
	if anc then
		parent:SetAttribute('NextAnchorPosition', anc.Position)
		parent:SetAttribute('NextAnchorForward', fwd(mk, 'ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY))
		parent:SetAttribute('NextAnchorWidth', anc:GetAttribute('width') or 18)
		parent:SetAttribute('NextAnchorClearHeight', anc:GetAttribute('clear_h') or 22)
		parent:SetAttribute('NextAnchorKey', M.GATE_KEY)
	else
		warn('[DemonSlayerIsland] ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY .. ' faltando')
	end
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and string.match(d.Name, '^COL_') then d:SetAttribute('TravessiaKeep', true) end
	end

	local gacha = invocacao(area, mk)
	if gacha then parent:SetAttribute('GachaPosition', gacha) end
	portao(model, mk, Config)
	vfx(model, mk)
	agua(model, mk, L2W)

	-- minerio: zona e bloqueios a partir dos marcadores do export (clareira a ceu aberto, piso plano 60,2)
	local zm = mk[M.ZONA]
	local piso = zm and (zm:GetAttribute('floor') or zm.Position.Y) or M.PISO
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
	local function bloqueado(p)
		for _, b in ipairs(blocos) do
			if (V(b.pos.X, 0, b.pos.Z) - V(p.X, 0, p.Z)).Magnitude < b.raio then return true end
		end
		return false
	end
	local ov = OverlapParams.new(); ov.FilterType = Enum.RaycastFilterType.Exclude; ov.RespectCanCollide = true
	local spawns, fora = {}, 0
	local boss
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
	-- a ilha e GIRADA no mundo (130 graus): o SpawnMinerio so conhece zonas alinhadas aos eixos, entao a zona vira uma
	-- LISTA de celulas 8x8 dentro do retangulo (eixos da ilha: v = frente do marcador, u = direita), e a grade hexagonal
	-- anda nos mesmos eixos. Os cantos sao recortados pelos GP_Block_* 'canto' (mancha eliptica).
	local v = fwd(mk, M.ZONA)
	local u = lado(v)
	local lx = zm and (zm:GetAttribute('sx') or 112) or 112
	local ly = zm and (zm:GetAttribute('sy') or 150) or 150
	local c0 = zm and zm.Position or zc
	local function mundo(x, y) return V(c0.X, piso, c0.Z) + u * x + v * y end
	local celulas = {}
	for x = -lx / 2 + 4, lx / 2 - 4, 8 do
		for y = -ly / 2 + 4, ly / 2 - 4, 8 do
			local p = mundo(x, y)
			table.insert(celulas, { nome = M.ZONA, centro = V(p.X, piso - 0.5, p.Z), tamanho = V(8, 0, 8) })
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
	local z = peca(M.ZONA, V(lx, 1, ly), CFrame.lookAt(V(c0.X, piso - 0.5, c0.Z), V(c0.X, piso - 0.5, c0.Z) + v), model)
	z:SetAttribute('PisoY', piso)
	print(('[DemonSlayerIsland] mineracao: %d marcadores ORE_ (%d fora), %d pontos da grade, %d celulas, %d bloqueios')
		:format(#spawns - hx, fora, hx, #celulas, #blocos))

	-- chefe: o primeiro superlendario (pe da subida, diante da forja); senao um epico; senao o centro da zona
	for _, pre in ipairs({ 'ORE_SUPERLEGENDARY_', 'ORE_EPIC_' }) do
		local melhor
		for n, m in pairs(mk) do
			if string.sub(n, 1, #pre) == pre and (not melhor or n < melhor.Name) then melhor = m end
		end
		if melhor then boss = melhor.Position break end
	end
	boss = boss or (zc + V(0, 1.5, 0))
	local volta = V(ent.X, ent.Y - 0.05, ent.Z) + lado(fe) * 12
	return { spawns = spawns, boss = boss, returnPad = volta,
		zonas = { lista = celulas, bloqueios = blocos } }
end

return M
