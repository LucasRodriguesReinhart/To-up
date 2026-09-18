-- SpawnMinerio: onde e qual minerio nasce.
--  * pontos: cada ilha tem os pontos originais + pontos extras gerados em volta (chao livre),
--    e cada minerio nasce num ponto sorteado longe dos outros.
--  * energia (Config.SPAWN): cada quebra enche a barra do tipo acima; barra cheia faz nascer 1.
--    o custo sobe com quantos daquele tipo ja estao vivos. compartilhado pelo servidor.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)

local S = {}
local pontos = {}       -- [areaId] = { Vector3 }
local energia = {}      -- [areaId] = { incomum = n, epica = n, chefe = n }
local rnd = Random.new()

local function barra(areaId)
	if not energia[areaId] then
		local b = {}
		for id in pairs(Config.SPAWN.barras) do b[id] = 0 end
		for id in pairs(Config.SPAWN.efeitos) do b[id] = 0 end
		energia[areaId] = b
	end
	return energia[areaId]
end
local efeitosProntos = {}  -- [areaId] = { dourado = n, arcoiris = n } esperando o proximo minerio

-- gera os pontos possiveis da ilha: os originais + uma varredura em grade da ilha inteira,
-- so em chao plano na altura do chao principal, sem nada solido em cima e longe de
-- entrada, portais, gacha e pad do lobby.
-- zonas (opcional): { lista = { {centro=Vector3 (altura do piso), tamanho=Vector3(x,0,z)} }, bloqueios = { {pos, raio} } }
-- quando existe, so aceita pontos dentro das zonas (em qualquer altura) e fora dos bloqueios decorativos.
function S.registrarPontos(area, originais, ignorar, evitar, zonas)
	local lista = {}
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignorar or {}
	params.RespectCanCollide = true
	local overlap = OverlapParams.new()
	overlap.FilterType = Enum.RaycastFilterType.Exclude
	overlap.FilterDescendantsInstances = ignorar or {}
	overlap.RespectCanCollide = true

	-- altura do chao principal = mediana dos pontos originais
	local alturas = {}
	for _, p in ipairs(originais) do table.insert(alturas, p.Y) end
	table.sort(alturas)
	local chaoY = alturas[math.max(1, math.ceil(#alturas / 2))] or area.centro.Y

	local function longe(pos, dist)
		for _, q in ipairs(lista) do
			if (Vector3.new(q.X, 0, q.Z) - Vector3.new(pos.X, 0, pos.Z)).Magnitude < dist then return false end
		end
		for _, e in ipairs(evitar or {}) do
			if (Vector3.new(e.X, 0, e.Z) - Vector3.new(pos.X, 0, pos.Z)).Magnitude < 16 then return false end
		end
		return true
	end
	local function aceitar(pos, alturaRef)
		if math.abs(pos.Y - alturaRef) > 3 then return end
		local bloqueio = workspace:GetPartBoundsInBox(CFrame.new(pos + Vector3.new(0, 5, 0)), Vector3.new(7, 8, 7), overlap)
		if #bloqueio == 0 and longe(pos, 7) then table.insert(lista, pos) end
	end

	for _, p in ipairs(originais) do
		if longe(p, 7) then table.insert(lista, p) end
	end
	if zonas and zonas.lista and #zonas.lista > 0 then
		local function bloqueado(pos)
			for _, b in ipairs(zonas.bloqueios or {}) do
				if (Vector3.new(b.pos.X, 0, b.pos.Z) - Vector3.new(pos.X, 0, pos.Z)).Magnitude < b.raio then return true end
			end
		end
		for _, z in ipairs(zonas.lista) do
			local meio = z.tamanho * 0.5
			for x = -meio.X + 4, meio.X - 4, 8 do
				for zz = -meio.Z + 4, meio.Z - 4, 8 do
					local teste = z.centro + Vector3.new(x + rnd:NextNumber(-2, 2), 0, zz + rnd:NextNumber(-2, 2))
					local hit = workspace:Raycast(teste + Vector3.new(0, 12, 0), Vector3.new(0, -30, 0), params)
					if hit and hit.Normal.Y > 0.85 and hit.Position.Y > z.centro.Y - 1 and hit.Position.Y < z.centro.Y + 5 and not bloqueado(hit.Position) then
						aceitar(hit.Position, hit.Position.Y)
					end
				end
			end
		end
		pontos[area.id] = lista
		return lista
	end
	local passo = 8
	for x = -124, 124, passo do
		for z = -124, 124, passo do
			local teste = area.centro + Vector3.new(x + rnd:NextNumber(-2, 2), 0, z + rnd:NextNumber(-2, 2))
			local hit = workspace:Raycast(Vector3.new(teste.X, chaoY + 40, teste.Z), Vector3.new(0, -70, 0), params)
			if hit and hit.Normal.Y > 0.85 then aceitar(hit.Position, chaoY) end
		end
	end
	pontos[area.id] = lista
	return lista
end

-- ponto sorteado longe dos minerios que ja existem na pasta (ignora o que esta sendo substituido).
-- pro chefe: distancia maior e checa se cabe (caixa grande sem nada solido).
function S.posicaoLivre(areaId, pastaRochas, ignorarGrupo, ehChefe)
	local lista = pontos[areaId]
	if not lista or #lista == 0 then return nil end
	local ocupados = {}
	if pastaRochas then
		for _, g in ipairs(pastaRochas:GetChildren()) do
			local hit = g ~= ignorarGrupo and g:FindFirstChild("Hitbox")
			if hit then table.insert(ocupados, { pos = hit.Position, chefe = g.Name == "PedraChefe" }) end
		end
	end
	local cfg = Config.SPAWN
	local overlap
	if ehChefe then
		overlap = OverlapParams.new()
		overlap.FilterType = Enum.RaycastFilterType.Exclude
		overlap.FilterDescendantsInstances = { pastaRochas }
		overlap.RespectCanCollide = true
	end
	local ordem = {}
	for i = 1, #lista do ordem[i] = i end
	for i = #ordem, 2, -1 do local j = rnd:NextInteger(1, i); ordem[i], ordem[j] = ordem[j], ordem[i] end
	local melhor, melhorFolga = nil, -math.huge
	for _, i in ipairs(ordem) do
		local p = lista[i]
		local folga = math.huge
		for _, o in ipairs(ocupados) do
			local minimo = (ehChefe or o.chefe) and cfg.distanciaChefe or cfg.distanciaMin
			local d = (Vector3.new(p.X, 0, p.Z) - Vector3.new(o.pos.X, 0, o.pos.Z)).Magnitude
			folga = math.min(folga, d - minimo)
		end
		local cabe = true
		if ehChefe then
			cabe = #workspace:GetPartBoundsInBox(CFrame.new(p + Vector3.new(0, 8, 0)), Vector3.new(16, 14, 16), overlap) == 0
		end
		if cabe then
			if folga >= 0 then return p end
			if folga > melhorFolga then melhor, melhorFolga = p, folga end
		end
	end
	return melhor
end

-- ---------- ENERGIA ----------
local pastaPublica
local function publicar(areaId, vivos)
	if not pastaPublica then
		pastaPublica = RS:FindFirstChild("EnergiaIlhas") or Instance.new("Folder")
		pastaPublica.Name = "EnergiaIlhas"
		pastaPublica.Parent = RS
	end
	local b = barra(areaId)
	for id, _ in pairs(Config.SPAWN.barras) do
		pastaPublica:SetAttribute(("a%d_%s"):format(areaId, id), math.floor(b[id] * 10) / 10)
		pastaPublica:SetAttribute(("a%d_%s_custo"):format(areaId, id), S.custo(areaId, id, vivos and vivos[id] or 0))
	end
	for id, e in pairs(Config.SPAWN.efeitos) do
		pastaPublica:SetAttribute(("a%d_%s"):format(areaId, id), b[id])
		pastaPublica:SetAttribute(("a%d_%s_custo"):format(areaId, id), e.custo)
	end
end
S.publicar = publicar

function S.custo(areaId, id, vivos)
	local r = Config.SPAWN.barras[id]
	return r.custo * (1 + r.porVivo * (vivos or 0))
end

-- a quebra enche a barra do tipo de cima
function S.quebrou(areaId, varianteId)
	local ganho = Config.SPAWN.energiaPorQuebra[varianteId]
	if not ganho then return end
	local b = barra(areaId)
	for id, r in pairs(Config.SPAWN.barras) do
		if r.vem == varianteId then b[id] += ganho end
	end
	-- efeitos: cada quebra conta 1 (dourado) ou so epicos (arco-iris)
	for id, e in pairs(Config.SPAWN.efeitos) do
		if e.vem == "qualquer" or e.vem == varianteId then
			b[id] += 1
			if b[id] >= e.custo then
				b[id] -= e.custo
				efeitosProntos[areaId] = efeitosProntos[areaId] or {}
				efeitosProntos[areaId][id] = (efeitosProntos[areaId][id] or 0) + 1
			end
		end
	end
end

-- efeito pro proximo minerio que nascer/amplificar (arco-iris tem prioridade)
function S.pegarEfeito(areaId)
	local p = efeitosProntos[areaId]
	if not p then return nil end
	for _, id in ipairs({ "arcoiris", "dourado" }) do
		if (p[id] or 0) > 0 then p[id] -= 1; return id end
	end
	return nil
end

-- barra cheia? consome o custo e devolve true (quem chama cria o minerio; se nao conseguir, chama devolver)
function S.tentarGerar(areaId, id, vivos)
	local r = Config.SPAWN.barras[id]
	if r.maxVivos and vivos >= r.maxVivos then return false end
	local b, custo = barra(areaId), S.custo(areaId, id, vivos)
	if b[id] < custo then return false end
	b[id] -= custo
	return true, custo
end

function S.devolver(areaId, id, qtd)
	local b = barra(areaId)
	b[id] += qtd
end

return S

