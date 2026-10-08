-- Ilha 5 "One Piece" (Wano, area 5 "Grand Line", tema mare). Modelada no Blender (pasta ilha_onepiece/), montada no
-- Studio por montar_ilha_onepiece.lua + pos_montagem_onepiece.lua e guardada em ServerStorage.IlhaOnePiece. Aqui a ilha
-- e clonada para a area de tema mare e ligada aos sistemas que JA existem, no MESMO contrato da Ilha 4
-- (ilha_demonslayer/roblox/DemonSlayerIsland.lua, testado no Play em 2026-10-07):
--  * encaixe: a ilha ja sai do export no lugar certo (WORLD_FROM_PREV = ISLAND_NEXT_ANCHOR_OnePiece da Ilha 4); a guarda
--    provisoria da ponta da DS sai no proprio DemonSlayerIsland quando esta fonte existe (M.FONTE_PROXIMA de la).
--  * mineracao A CEU ABERTO na praca: pontos ORE_* + grade hexagonal no piso 92,2 + zona MiningZone_OnePiece (152 x 120,
--    girada com a ilha: vira LISTA de celulas 8x8, como na DS) com bloqueios GP_Block_* (48 borda + 28 canto).
--  * invocacao: a maquina Gacha_<tema> (mare) vira o motor invisivel da torre (prompt na torre, pad no terraco).
--  * portao ONE PUNCH MAN: peca NextAreaId=6 no promontorio (o Core.Main liga o prompt: bloqueado -> compra pela UI de
--    sempre) + placa de preco; estado da barreira por jogador no cliente (ILHAS_Cliente, GATES.OnePunchMan = 6).
--  * guarda da ancora OPM (OP_Exit_AnchorGuard + COL_OPAnchorGuard_*) sai quando existir ServerStorage.IlhaOnePunchMan
--    (NOME SUPOSTO da fonte da area 6, que ainda nao existe: a integracao da area 6 usa este nome ou muda a constante).
--  * agua feita no Roblox a partir dos marcadores da pedra (op_water.water_markers): cachoeira do castelo (bica do
--    labio -> cortina -> 2 degraus de espuma -> bacia), bacia do adro em POLIGONO (sem camada ForceField: ela desenhava
--    emendas brancas no Play da DS), canal leste com degrau 3 x 2 ate a queda leste (enseada), bica da nascente oeste ->
--    canal oeste com degrau 2 x 2 -> espuma da roda d'agua -> queda oeste (mar). O MAR LOCAL (WATER_Sea, nivel 36) NAO
--    e feito aqui: e do cliente (CeuWano), so com o jogador na area 5; aqui so os atributos MarLocal* da area.
--  * emissores: cada FX_* com atributo vfx='emissor' vira um ParticleEmitter pela receita gravada no marcador (as chaves
--    do emissor() da DS); sem receita, as reservas PADRAO abaixo (petalas da copa, nevoa do pe da cachoeira). Pecas
--    moveis (roda d'agua VFX_OP_Wheel, aneis/estrela VFX_OPSUM_*) ja vem com a tag IlhaMovel do montar (o LocalScript
--    ILHA_NARUTO_Movel gira): nada a fazer aqui.
--  * regiao: BoundsCenter/BoundsHalfSize (o Config.centro desta area fica longe da ilha), SafeMaxY 150 (patio do
--    castelo 136,2), BoundsMinY 28 (abaixo do mar local 36: quem cai na agua e resgatado).
-- Sem masmorra, sem alquimia, sem trono (nada de CRAFT_/DUNGEON_ aqui). DIURNA: nada de NightOnly/lua aqui.
local SS = game:GetService('ServerStorage')
local CS = game:GetService('CollectionService')
local RS = game:GetService('ReplicatedStorage')
local M = {}
local V = Vector3.new
local C = Color3.fromRGB
local HRP = 3.5
M.PASSO_HEX = 7.5
M.GATE_KEY = 'OnePunchMan'
M.GATE_AREA = 6            -- Cidade Z (One Punch Man)
M.FONTE = 'IlhaOnePiece'
M.NOME = 'ILHA_ONEPIECE'   -- IlhaMovel (atributo movel_de), PortoesCompra e o CeuWano procuram por este nome
M.FONTE_PROXIMA = 'IlhaOnePunchMan' -- NOME SUPOSTO: quando a fonte da ilha 6 existir, a guarda provisoria da ancora sai
M.ZONA = 'MiningZone_OnePiece'
M.PISO = 92.2              -- P (praca)
M.SAFE_MAX_Y = 150         -- PLANO_OP secao 12: salva ponto seguro em todos os patamares (ate o patio do castelo 136,2)
M.BOUNDS_MIN_Y = 28        -- PLANO_OP secao 12: abaixo do mar local (36) -> queda na agua e resgatada
M.ORE_MAX = 80
M.ENTRADA = V(-2136.99, 84.4, 1669.72)   -- WORLD_ENTRY_OnePiece (export M2), so se o marcador faltar

local function peca(nome, tam, cf, pai)
	local p = Instance.new('Part')
	p.Name = nome; p.Size = tam; p.CFrame = cf
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1
	p.Parent = pai
	return p
end

-- ------------------------------------------------------------------ leitura dos atributos dos marcadores
-- o export grava cores como "r,g,b" (0-255), pares como "a,b", listas de pontos como "x,y,z;x,y,z" (ja no mundo);
-- trios *_pos/pivot/center viram 3 atributos <chave>_x/_y/_z JA no mundo (export_op.to_world). 'spout_waypoints' fica
-- no referencial LOCAL; desde a M6c o export grava TAMBEM 'spout_waypoints_world' (ja no mundo). Usa a '_world' quando
-- existe; so converte a local pelo WORLD_FROM_PREV num export antigo (sem conversao dupla nos dois casos).
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

-- trio gravado pelo export como <k>_x/<k>_y/<k>_z (ou Vector3 direto, se algum dia vier assim)
local function trio(m, k)
	if not m then return nil end
	local v = m:GetAttribute(k)
	if typeof(v) == 'Vector3' then return v end
	local x, y, z = m:GetAttribute(k .. '_x'), m:GetAttribute(k .. '_y'), m:GetAttribute(k .. '_z')
	if type(x) == 'number' and type(y) == 'number' and type(z) == 'number' then return V(x, y, z) end
	return nil
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

-- direita (local +X da ilha) a partir da frente (local +Y): a mesma regra u = (-v.Z, 0, v.X) das Ilhas 3 e 4
local function lado(f)
	return V(-f.Z, 0, f.X)
end

-- referencial LOCAL do projeto -> mundo (para 'spout_waypoints'). A origem vem do WORLD_FROM_PREV, que no projeto fica
-- em (0, -bridge_len) = (0, -120) e olha para +Y local; z local = Y do Roblox.
local function conversorLocal(mk)
	local w = mk.WORLD_FROM_PREV
	if not w then return nil end
	local f = fwdDe(w)
	local r = lado(f)
	local y0 = -(w:GetAttribute('bridge_len') or 120)
	local o = w.Position
	return function(x, y, alt)
		local p = o + r * x + f * (y - y0)
		return V(p.X, alt or o.Y, p.Z)
	end, f, r
end

-- ------------------------------------------------------------------ emissores (mesmo emissor() das Ilhas 1, 3 e 4)
local TEX = {
	fumaca = 'rbxasset://textures/particles/smoke_main.dds',
	brilho = 'rbxasset://textures/particles/sparkles_main.dds',
	nevoa = 'rbxassetid://534953301',
	gota = 'rbxassetid://1389215359',
	-- petala: a textura padrao do ParticleEmitter (a mesma das petalas aprovadas do lobby Murim, hex_fase9_vegetacao).
	-- Uma textura propria de petala entra pela receita do marcador (tex = 'rbxassetid://...').
	petala = 'rbxasset://textures/particles/sparkles_main.dds',
}
local function textura(t)
	if TEX[t or ''] then return TEX[t] end
	if typeof(t) == 'string' and string.sub(t, 1, 3) == 'rbx' then return t end
	return TEX.fumaca
end

local function emissor(pai, nome, onde, s)
	local cf = typeof(onde) == 'CFrame' and onde or CFrame.new(onde)
	local a = peca('VFX_' .. nome, s.area or V(1, 1, 1), cf, pai)
	local e = Instance.new('ParticleEmitter')
	e.Name = nome
	e.Texture = textura(s.tex)
	e.Color = typeof(s.cor) == 'ColorSequence' and s.cor or ColorSequence.new(s.cor)
	e.Rate = s.rate
	e.Lifetime = NumberRange.new(s.vida * 0.7, s.vida)
	e.Speed = NumberRange.new(s.vel * 0.4, s.vel)
	e.SpreadAngle = s.spread or Vector2.new(40, 40)
	e.Acceleration = s.acc or V(0, 0, 0)
	e.LightEmission = s.luz or 0.2
	e.LightInfluence = s.infl or 1
	e.Rotation = NumberRange.new(0, 360)
	local rs = s.rotv or 12
	e.RotSpeed = NumberRange.new(-rs, rs)
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

-- receitas de reserva para marcador FX_* exportado SEM a receita gravada (o op_vfx do M4 ainda nao existia quando este
-- modulo foi escrito: os FX_* do op_core/op_water so trazem 'fx'). Valores de DIA (nada de brasa/luz forte).
--  petalas: o FX_Petals_Tree (UM emissor discreto na copa, Dist 320 do marcador), petala rosa caindo devagar com deriva;
--           a mesma linguagem das petalas aprovadas do lobby Murim (cor 255,170,195 -> 248,140,170, giro +-60).
--  nevoa_baixa: o FX_Mist_CastleFall (raio 11 no marcador), spray claro no pe da cachoeira, sem esconder arquitetura.
-- (FX_Fall_* ficam com a nevoa da agua(); FX_Weir_*/FX_Spring_W com os respingos da agua(); ver vfx()).
local PADRAO = {
	petalas = { tex = 'petala', cor = '255,178,204', cor_fim = '246,142,178', rate = 3, vida = 12, vel = 1.2, tam = 0.34,
		fim = 0.7, transp = 0.2, luz = 0, infl = 1, spread = '180,180', acc_up = -1.1, drift = 0.5, area = '56,10,56',
		forma = 'Box', Dist = 320, rotv = 60 },
	nevoa_baixa = { tex = 'nevoa', cor = '226,236,244', rate = 1.5, vida = 7, vel = 0.6, tam = 9, fim = 1.3, transp = 0.84,
		luz = 0, infl = 1, spread = '90,10', acc_up = 0.15, drift = 0.3, area = '22,1.5,22', forma = 'Box', Dist = 220 },
	fumaca = { tex = 'fumaca', cor = '200,200,204', rate = 3, vida = 9, vel = 3.5, tam = 4.5, fim = 2.6, transp = 0.6, luz = 0.05,
		infl = 1, spread = '10,10', acc_up = 1.3, drift = 0.5, area = '3.4,1,3.4', forma = 'Box', Dist = 400 },
}

local function formaDe(nome)
	if typeof(nome) ~= 'string' or nome == '' then return Enum.ParticleEmitterShape.Box end
	local ok, f = pcall(function() return Enum.ParticleEmitterShape[nome] end)
	return ok and f or Enum.ParticleEmitterShape.Box
end

-- um emissor a partir do marcador: 'area' = "lado,altura,frente" nos eixos do marcador; aceleracao = acc_up para cima
-- (negativo = cai, petalas) + drift ao longo da frente do marcador (fwd_x, fwd_z). As quedas (FX_Fall_<k>_*) nascem no
-- mesmo lugar que a DS usa: crista um pouco a frente e abaixo do labio, degrau a frente, pe 4 acima do nivel da agua.
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
	local cor = cor3(at('cor'), C(226, 236, 248))
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
	if string.match(m.Name, '^FX_Fall_.+_Lip$') then
		pos = pos + f * 0.8 - V(0, 1, 0)
	elseif string.match(m.Name, '^FX_Fall_.+_Step$') then
		pos = pos + f * 1.5
	elseif string.match(m.Name, '^FX_Fall_.+_Base$') then
		pos = pos + V(0, 4, 0)
	end
	local nome = string.gsub(m.Name, '^FX_', '')
	return emissor(pai, nome, CFrame.fromMatrix(pos, l, V(0, 1, 0)), {
		tex = tex, cor = seq, rate = at('rate') or 2, vida = at('vida') or 3, vel = at('vel') or 1, tam = tam,
		fim = at('fim') or (nev and 1.2 or 0.6), transp = at('transp') or 0.55, luz = at('luz') or 0.1,
		infl = at('infl') or 1, spread = spread, acc = acc, area = area, forma = formaDe(at('forma')),
		dist = at('Dist') or 260, rotv = at('rotv') })
end

-- VFX com funcao: petalas da copa da arvore, nevoa do pe da cachoeira do castelo e o brilho do portao One Punch Man.
-- Nada de particula decorativa solta. Os FX_* que o op_vfx (M4) gravar com vfx='emissor' entram sozinhos.
local function vfx(model, mk)
	local pasta = Instance.new('Folder'); pasta.Name = 'VFX_Integracao'; pasta.Parent = model
	local n = 0
	for nome, m in pairs(mk) do
		if string.match(nome, '^FX_') and m:IsA('BasePart') then
			local fx = m:GetAttribute('fx')
			local queda = string.match(nome, '^FX_Fall_') ~= nil
			-- quedas sem receita ficam com a nevoa da agua(); degraus e bica sem receita, com os respingos da agua()
			if m:GetAttribute('vfx') == 'emissor' or (not queda and PADRAO[fx or '']) then
				receita(pasta, m)
				n += 1
			end
		end
	end
	local g = mpos(mk, 'GATE_' .. M.GATE_KEY)
	if g then
		emissor(pasta, 'Portao_' .. M.GATE_KEY, g + V(0, 9, 0), { tex = 'brilho', cor = C(255, 204, 110), rate = 3, vida = 2,
			vel = 0.7, tam = 0.4, fim = 0.2, acc = V(0, 1, 0), luz = 0.7, infl = 0.3, transp = 0.35, area = V(10, 16, 10),
			forma = Enum.ParticleEmitterShape.Box, dist = 180 })
	end
	print(('[OnePieceIsland] %d emissores FX_*'):format(n))
end

-- ------------------------------------------------------------------ AGUA feita no Roblox
-- O Blender so deixa a pedra estanque e os marcadores (op_water mediu tudo na pedra):
--   FX_Fall_Castle_Lip (waypoints/widths = eixo da cortina labio -> degrau A -> degrau B -> bacia; spout_waypoints/
--     spout_width = lamina deitada da boca escura da nascente ate a frente do labio, em coordenada LOCAL);
--   FX_Fall_Castle_Step (+ step2_pos) = os 2 degraus de espuma; FX_Fall_Castle_Base = pe na bacia;
--   FX_Fall_E_Lip / FX_Fall_W_Lip (waypoints/widths ate o mar 36) + _Base; FX_Spring_W (bica, waypoints/widths);
--   WATER_Basin (waypoints = CONTORNO da agua no nivel 97,6; mouth_a_pos/mouth_b_pos = boca do canal leste, no mundo);
--   WATER_CanalE / WATER_CanalW (waypoints/widths = eixo da agua; degraus = pares de pontos com cota diferente;
--     wheel_pos = onde as pas da roda batem); FX_Weir_E / FX_Weir_W = borda da soleira dos degraus.
-- Cortina = paineis finos por trecho, face para fora da rocha; canais = os mesmos paineis deitados (face para cima).
-- Texture de agua corrente rolada pelo cliente (tag AguaCorrente, atributo Velocidade; CeuWano/CeuNatagumo/CeuSombras).
-- Espelho da bacia = Glass em triangulos (WedgeParts) pelo contorno, SEM camada ForceField (emendas brancas na DS).
-- Tudo decorativo: sem colisao nem consulta. Cores de DIA (turquesa, a familia do mar local 48,176,196).
local AGUA = {
	correnteza = 'rbxassetid://1190623231',   -- textura de agua corrente (a mesma das Ilhas 3 e 4)
	corpo = C(66, 150, 176), claro = C(214, 242, 250), espelho = C(54, 134, 160), brilho = C(170, 226, 240),
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

-- agua corrente deitada ao longo de uma lista de pontos (canal, bica do labio). sem0 = a primeira ponta nao estica
-- (o canal leste comeca EXATAMENTE na linha da boca da bacia: sem duas laminas sobrepostas)
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
	e.Color = ColorSequence.new(cor or C(232, 242, 250)); e.LightInfluence = 0.9; e.LightEmission = 0.1
	e.Rotation = NumberRange.new(0, 360); e.RotSpeed = NumberRange.new(-20, 20)
	e.Shape = Enum.ParticleEmitterShape.Box; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
	e:SetAttribute('Dist', 260); e:SetAttribute('Rate0', rate)
	CS:AddTag(e, 'IlhaVFX')
	e.Parent = a
	return e
end

-- respingo de gotas (o mesmo da fonte da Ilha 3 / roda da DS)
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

-- espelho d'agua com o CONTORNO dado: so a camada Glass (sem ForceField por triangulo: o brilho de borda de cada cunha
-- desenhava as emendas do leque - linhas brancas radiais no Play da DS, 2026-10-06)
local function espelhoPoligono(pai, nome, pts, nivel)
	local plano = {}
	for _, p in ipairs(pts) do table.insert(plano, V(p.X, nivel, p.Z)) end
	local tris = triangular(plano)
	local np = 0
	for i, t in ipairs(tris) do
		local d = V(0, -0.1, 0)
		np += triangulo(pai, nome .. '_Vidro_' .. i, t[1] + d, t[2] + d, t[3] + d, 0.2, Enum.Material.Glass, AGUA.espelho, 0.25)
	end
	return #tris, np
end

-- cortina de queda por uma lista de pontos (cachoeira, quedas para o mar, bica): os paineis da Ilha 3, face para fora
local function cortinaPts(pai, pts, ws, fora, velA, velB)
	for k = 1, #pts - 1 do
		local w0, w1 = ws[k] or ws[#ws] or 3, ws[k + 1] or ws[#ws] or 3
		lamina(pai, 'Agua_' .. k, pts[k], pts[k + 1], w0, w1, fora, 0, 0.075, 0.075, velA, 0.12)
		lamina(pai, 'Brilho_' .. k, pts[k], pts[k + 1], w0 * 0.7, w1 * 0.7, fora, 1, 0.075, 0.075, velB, 0.12)
	end
end

-- uma queda FX_Fall_<k>_*: cortina medida + (sem receita no marcador) a nevoa da crista, do(s) degrau(s) e do pe
local function cortina(pai, lip, mk, k)
	local fora = fwdDe(lip)
	local pts, ws = pontos(lip:GetAttribute('waypoints')), larguras(lip:GetAttribute('widths'))
	local base = mk['FX_Fall_' .. k .. '_Base']
	if #pts < 2 then
		pts = { lip.Position, base and base.Position or (lip.Position - V(0, 20, 0)) }
		ws = { lip:GetAttribute('width') or 3, (base and base:GetAttribute('width')) or 4 }
	end
	local q = Instance.new('Folder'); q.Name = 'Queda_' .. k; q.Parent = pai
	cortinaPts(q, pts, ws, fora, 14, 22)
	if lip:GetAttribute('vfx') ~= 'emissor' then
		local w = lip:GetAttribute('width') or 3
		nevoa(q, 'Crista_' .. k, lip.Position + fora * 0.8 - V(0, 1, 0), w * 0.5, 3)
		local st = mk['FX_Fall_' .. k .. '_Step']
		if st and st:GetAttribute('vfx') ~= 'emissor' then
			local sw = st:GetAttribute('width') or w
			nevoa(q, 'Degrau_' .. k, st.Position + fora * 1.5, sw * 0.8, 8)
			local s2 = trio(st, 'step2_pos')          -- degrau de espuma de baixo (so a cachoeira do castelo)
			if s2 then nevoa(q, 'Degrau2_' .. k, s2 + fora * 1.2, sw * 0.9, 8) end
		end
		if base and base:GetAttribute('vfx') ~= 'emissor' then
			nevoa(q, 'Pe_' .. k, base.Position + V(0, 4, 0), (base:GetAttribute('width') or w) * 1.6, 14)
		end
	end
	return q, #pts
end

local function agua(model, mk, L2W)
	local pasta = Instance.new('Folder'); pasta.Name = 'AGUA_Roblox'; pasta.Parent = model
	local rel = {}
	-- quedas: cachoeira do castelo (Castle), queda leste (E, enseada), queda oeste (W, mar)
	local chaves = {}
	for nome in pairs(mk) do
		local k = string.match(nome, '^FX_Fall_(.+)_Lip$')
		if k then table.insert(chaves, k) end
	end
	table.sort(chaves)
	for _, k in ipairs(chaves) do
		local lip = mk['FX_Fall_' .. k .. '_Lip']
		local q, n = cortina(pasta, lip, mk, k)
		-- bica do labio (so a cachoeira do castelo): lamina DEITADA da boca escura da nascente ate a frente do labio.
		-- M6c: 'spout_waypoints_world' (export novo) ja vem no mundo; 'spout_waypoints' (local) so num export antigo
		local spw = pontos(lip:GetAttribute('spout_waypoints_world'))
		local sp = pontos(lip:GetAttribute('spout_waypoints'))
		if #spw >= 2 or #sp >= 2 then
			if #spw >= 2 or L2W then
				local w = spw
				if #spw < 2 then
					w = {}
					for i, p in ipairs(sp) do w[i] = L2W(p.X, p.Y, p.Z) end
				end
				local sw = lip:GetAttribute('spout_width') or 5
				fita(q, 'Bica', w, { sw, sw }, 5, false)
				table.insert(rel, ('queda %s: %d pontos + bica do labio'):format(k, n))
			else
				warn('[OnePieceIsland] WORLD_FROM_PREV faltando: bica do labio da queda ' .. k .. ' nao criada')
			end
		else
			table.insert(rel, ('queda %s: %d pontos'):format(k, n))
		end
	end
	-- bica da nascente do canal oeste (FX_Spring_W): cortina pequena + respingo na cabeceira do canal
	local bica = mk.FX_Spring_W
	if bica then
		local pts, ws = pontos(bica:GetAttribute('waypoints')), larguras(bica:GetAttribute('widths'))
		if #pts >= 2 then
			local f = Instance.new('Folder'); f.Name = 'Nascente_W'; f.Parent = pasta
			cortinaPts(f, pts, ws, fwdDe(bica), 10, 16)
			if bica:GetAttribute('vfx') ~= 'emissor' then gotas(f, 'Respingo_Nascente', pts[#pts] + V(0, 0.3, 0), V(1.6, 0.2, 1.6), 8, 120) end
			table.insert(rel, ('nascente W: %d pontos'):format(#pts))
		end
	end
	-- bacia do adro: contorno desenhado (nao retangulo); a boca do canal leste e a borda leste do poligono
	local bacia = mk.WATER_Basin
	local boca
	if bacia then
		local nivel = bacia:GetAttribute('level') or bacia.Position.Y
		local cont = pontos(bacia:GetAttribute('waypoints'))
		local f = Instance.new('Folder'); f.Name = 'Bacia'; f.Parent = pasta
		if #cont >= 3 then
			local nt, np = espelhoPoligono(f, 'Espelho', cont, nivel - 0.06)
			table.insert(rel, ('bacia: contorno %d pontos -> %d triangulos (%d cunhas)'):format(#cont, nt, np))
			if nt < #cont - 2 - 2 then warn('[OnePieceIsland] bacia: triangulacao incompleta (' .. nt .. ' triangulos)') end
		else
			warn('[OnePieceIsland] WATER_Basin sem contorno (waypoints): bacia nao criada')
		end
		local ma, mb = trio(bacia, 'mouth_a_pos'), trio(bacia, 'mouth_b_pos')
		if ma and mb then boca = (ma + mb) / 2 end
	end
	-- canal leste: boca da bacia -> degrau 3 x 2 -> pe do rochedo NE -> curva -> bica da queda leste
	local ce = mk.WATER_CanalE
	if ce then
		local pts = pontos(ce:GetAttribute('waypoints'))
		if boca and #pts >= 2 then
			local d = (V(pts[1].X, 0, pts[1].Z) - V(boca.X, 0, boca.Z)).Magnitude
			if d < 1.5 then
				pts[1] = V(boca.X, pts[1].Y, boca.Z)
			else
				warn(('[OnePieceIsland] o canal leste comeca a %.2f da boca da bacia (esperado 0)'):format(d))
			end
		end
		local f = Instance.new('Folder'); f.Name = 'CanalLeste'; f.Parent = pasta
		table.insert(rel, ('canal leste: %d trechos'):format(fita(f, 'CanalE', pts, larguras(ce:GetAttribute('widths')), 4, true)))
	end
	-- canal oeste: cabeceira no arrimo -> sob as 2 pontes -> degrau 2 x 2 -> roda d'agua -> bica da queda oeste
	local cw = mk.WATER_CanalW
	if cw then
		local pts = pontos(cw:GetAttribute('waypoints'))
		local f = Instance.new('Folder'); f.Name = 'CanalOeste'; f.Parent = pasta
		table.insert(rel, ('canal oeste: %d trechos'):format(fita(f, 'CanalW', pts, larguras(cw:GetAttribute('widths')), 4, false)))
		local wp = trio(cw, 'wheel_pos')
		if wp then
			gotas(f, 'Espuma_Roda', wp + V(0, 0.2, 0), V(5, 0.2, 3), 10, 120)
			table.insert(rel, 'espuma da roda: ok')
		else
			warn('[OnePieceIsland] WATER_CanalW sem wheel_pos (espuma da roda nao criada)')
		end
	end
	-- degraus dos canais (sem receita): respingo na borda da soleira, correnteza = frente do marcador
	for _, nome in ipairs({ 'FX_Weir_E', 'FX_Weir_W' }) do
		local m = mk[nome]
		if m and m:GetAttribute('vfx') ~= 'emissor' then
			local w = m:GetAttribute('width') or 5
			gotas(pasta, 'Respingo_' .. string.gsub(nome, '^FX_', ''), m.Position + fwdDe(m) * 1.2 - V(0, 0.8, 0),
				V(w * 0.8, 0.2, 2), 10, 120)
		end
	end
	print('[OnePieceIsland] agua: ' .. table.concat(rel, '; '))
end

-- ------------------------------------------------------------------ invocacao (o mesmo esquema das Ilhas 1 a 4)
local function invocacao(area, mk)
	local machine = workspace:FindFirstChild('Gachas') and workspace.Gachas:FindFirstChild('Gacha_' .. area.tema)
	local pad = machine and machine:FindFirstChild('PadGacha')
	local cab
	for _, d in ipairs(machine and machine:GetDescendants() or {}) do
		if d:IsA('BasePart') and string.find(d.Name:lower(), 'cabinet_body') then cab = d break end
	end
	local inter, jog = mk.SUMMON_Interact, mk.SUMMON_PlayerPosition
	if not (pad and cab and inter and jog) then warn('[OnePieceIsland] maquina de gacha/marcadores de invocacao faltando') return nil end
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
	machine:SetAttribute('MotorDaTorre', 'Ilha One Piece: maquina invisivel, visual = torre de invocacao')
	return V(pad.Position.X, piso + HRP, pad.Position.Z)
end

-- portao One Punch Man: interacao (NextAreaId, so para COMPRAR: liberado, o cliente desliga o prompt) + placa de preco
local function portao(model, mk, Config)
	local key = M.GATE_KEY
	local prox = Config.areaPorId(M.GATE_AREA)
	local gi, ui = mk['GATE_' .. key .. '_INTERACT'], mk['PURCHASE_UI_ANCHOR_' .. key]
	if not (prox and gi and ui) then warn('[OnePieceIsland] marcadores do portao ' .. key .. ' faltando') return end
	local aid = mk['GATE_' .. key] and mk['GATE_' .. key]:GetAttribute('area_id')
	if aid and aid ~= prox.id then
		warn(('[OnePieceIsland] GATE_%s.area_id = %s, mas o portao vende a area %d'):format(key, tostring(aid), prox.id))
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
	txt('Nome', 0, 30, string.upper(prox.nome), C(255, 204, 96))
	txt('Custo', 32, 28, 'Custo: ' .. Config.formatar(prox.custo) .. ' moedas', C(255, 255, 255), Enum.Font.GothamBold)
	txt('Dica', 62, 20, 'Interaja no portao para desbloquear', C(225, 225, 235), Enum.Font.GothamMedium)
	-- sem disco de viagem na ancora: a travessia sera a pe (a ilha da area 6 vai encostar no ISLAND_NEXT_ANCHOR_OnePunchMan)
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

-- mar LOCAL (WATER_Sea): so publica os dados na area; quem desenha e o CeuWano, no cliente e so na area 5 (os
-- atributos da area replicam sem depender do streaming do marcador)
local function marLocal(parent, mk)
	local s = mk.WATER_Sea
	if not s then warn('[OnePieceIsland] WATER_Sea faltando: o CeuWano usa o padrao (nivel 36, 2200)') return end
	local nivel = s:GetAttribute('level') or s.Position.Y
	parent:SetAttribute('MarLocalNivel', nivel)
	parent:SetAttribute('MarLocalCentro', V(s.Position.X, nivel, s.Position.Z))
	parent:SetAttribute('MarLocalTamanho', s:GetAttribute('size') or 2200)
	parent:SetAttribute('MarLocalCor', cor3(s:GetAttribute('color'), C(48, 176, 196)))
end

function M.build(parent, area)
	local Config = require(RS.Config)
	local source = SS:FindFirstChild(M.FONTE)
	assert(source, '[OnePieceIsland] ServerStorage.' .. M.FONTE .. ' nao encontrado')
	parent.ModelStreamingMode = Enum.ModelStreamingMode.PersistentPerPlayer
	local model = source:Clone()
	model.Name = M.NOME
	model.Parent = parent
	-- ilha One Punch Man instalada: a ponte dela encosta no ISLAND_NEXT_ANCHOR_OnePunchMan, entao sai a guarda provisoria
	-- da ponta (OP_Exit_AnchorGuard + COL_OPAnchorGuard_*, atributo next_island_guard do montar)
	if SS:FindFirstChild(M.FONTE_PROXIMA) then
		for _, d in ipairs(model:GetDescendants()) do
			if d.Parent and d:GetAttribute('next_island_guard') then d:Destroy() end
		end
	end
	local gm = model:FindFirstChild('GAMEPLAY_MARKERS')
	assert(gm, '[OnePieceIsland] GAMEPLAY_MARKERS faltando em ServerStorage.' .. M.FONTE)
	local mk = {}
	for _, m in ipairs(gm:GetChildren()) do mk[m.Name] = m end
	local L2W = conversorLocal(mk)

	local ent = mpos(mk, 'WORLD_ENTRY_OnePiece') or M.ENTRADA
	local fe = fwd(mk, 'WORLD_ENTRY_OnePiece')
	parent:SetAttribute('WorldRevision', 1)
	parent:SetAttribute('EntryPosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z))
	parent:SetAttribute('EntryForward', fe)
	parent:SetAttribute('SafePosition', V(ent.X, ent.Y - 0.2 + HRP, ent.Z) + fe * 8)
	parent:SetAttribute('RotaPropria', true)
	parent:SetAttribute('SafeMaxY', M.SAFE_MAX_Y)
	parent:SetAttribute('OreMax', M.ORE_MAX)
	local bc, bh = caixa(model)
	-- convencao do IslandTravel: centro em Y 0 e teto em BoundsHalfSize.Y (a copa da arvore passa de 300). O fundo fica
	-- em 28: abaixo do mar local (36) e acima da quilha (-10) e da rede (-30) -> queda no mar e resgatada
	parent:SetAttribute('BoundsCenter', V(bc.X, 0, bc.Z))
	parent:SetAttribute('BoundsHalfSize', V(bh.X + 10, math.max(130, bc.Y + bh.Y + 10), bh.Z + 10))
	parent:SetAttribute('BoundsMinY', M.BOUNDS_MIN_Y)
	local anc = mk['ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY]
	if anc then
		parent:SetAttribute('NextAnchorPosition', anc.Position)
		parent:SetAttribute('NextAnchorForward', fwd(mk, 'ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY))
		parent:SetAttribute('NextAnchorWidth', anc:GetAttribute('width') or 18)
		parent:SetAttribute('NextAnchorClearHeight', anc:GetAttribute('clear_h') or 22)
		parent:SetAttribute('NextAnchorKey', M.GATE_KEY)
	else
		warn('[OnePieceIsland] ISLAND_NEXT_ANCHOR_' .. M.GATE_KEY .. ' faltando')
	end
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA('BasePart') and string.match(d.Name, '^COL_') then d:SetAttribute('TravessiaKeep', true) end
	end
	marLocal(parent, mk)

	local gacha = invocacao(area, mk)
	if gacha then parent:SetAttribute('GachaPosition', gacha) end
	portao(model, mk, Config)
	vfx(model, mk)
	agua(model, mk, L2W)

	-- minerio: zona e bloqueios a partir dos marcadores do export (praca a ceu aberto, piso plano 92,2)
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
	-- a ilha e GIRADA no mundo (145 graus): o SpawnMinerio so conhece zonas alinhadas aos eixos, entao a zona vira uma
	-- LISTA de celulas 8x8 dentro do retangulo (eixos da ilha: v = frente do marcador, u = direita), e a grade hexagonal
	-- anda nos mesmos eixos. Os cantos sao recortados pelos GP_Block_* 'canto' (area util em elipse).
	local v = fwd(mk, M.ZONA)
	local u = lado(v)
	local lx = zm and (zm:GetAttribute('sx') or 152) or 152
	local ly = zm and (zm:GetAttribute('sy') or 120) or 120
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
	print(('[OnePieceIsland] mineracao: %d marcadores ORE_ (%d fora), %d pontos da grade, %d celulas, %d bloqueios')
		:format(#spawns - hx, fora, hx, #celulas, #blocos))

	-- chefe: o primeiro superlendario (perto do castelo); senao um epico; senao o centro da zona
	for _, pre in ipairs({ 'ORE_SUPERLEGENDARY_', 'ORE_EPIC_' }) do
		local melhor
		for n, m in pairs(mk) do
			if string.sub(n, 1, #pre) == pre and (not melhor or n < melhor.Name) then melhor = m end
		end
		if melhor then boss = melhor.Position break end
	end
	boss = boss or (zc + V(0, 1.5, 0))
	local volta = V(ent.X, ent.Y - 0.05, ent.Z) + lado(fe) * 12     -- patio do torii (ENTRY_COURT tem +-26)
	return { spawns = spawns, boss = boss, returnPad = volta,
		zonas = { lista = celulas, bloqueios = blocos } }
end

return M
