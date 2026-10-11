-- auditoria_colisao.lua - Command Bar do Studio (de preferencia no MODO DE EDICAO). So LE e mede; nao muda nada no fim.
-- Rodada 3 (colisao V3, "o que se ve e o que colide"): mede na ilha INSTALADA o que o Roblox colide de verdade.
-- Acha a ilha em: workspace.ILHA_ONEPIECE (logo depois do montar) -> workspace.Areas.Area5.<modelo> (Play) ->
-- ServerStorage.IlhaOnePiece (clona TEMPORARIAMENTE para o workspace e apaga no fim).
-- Relatorio:
--  (1) pecas COLIDIVEIS INVISIVEIS (CanCollide e Transparency >= 0,95): total, por categoria, as maiores (posicao/tamanho)
--      e tags CamOccluder (tem de ser 0);
--  (2) EM PE NO AR: grade de raios para baixo (RespectCanCollide) - o primeiro colisor atingido; se for INVISIVEL e nao
--      houver malha VISIVEL a <= 0,5 do topo dele, o ponto e 'no ar'. Para enxergar a malha visivel (que fica com
--      CanQuery=false e fidelidade Box), no MODO DE EDICAO o script liga CanQuery e PreciseConvexDecomposition nas
--      MeshParts so-visuais da ilha durante a medida e DEVOLVE tudo no fim (demora ~1 min). No Play isso nao e possivel:
--      ali so o colisor visivel conta como 'visivel';
--  (3) FECHO GRANDE DEMAIS: em cada MeshPart colidivel, a cobertura da planta da caixa (grade 6 x 6 de raios so nela) x
--      a cobertura que o fecho tinha no Blender (atributo colv3_cov do montar). Muito maior = o Roblox nao fez o fecho
--      esperado (fidelidade Box/Default no lugar de Hull?). Lista tambem as maiores caixas colidiveis.
local PASSO = 2.0          -- grade da medida (2) em studs
local TOL = 0.5            -- tolerancia 'tem visual' acima/abaixo do topo do colisor
local MAX_LISTA = 25
local SS = game:GetService('ServerStorage')
local CS = game:GetService('CollectionService')
local RS = game:GetService('RunService')

local root, temp = workspace:FindFirstChild('ILHA_ONEPIECE'), nil
if not root then
	local a5 = workspace:FindFirstChild('Areas') and workspace.Areas:FindFirstChild('Area5')
	if a5 then
		for _, m in ipairs(a5:GetChildren()) do
			if m:IsA('Model') and m:FindFirstChild('GAMEPLAY_MARKERS') then root = m break end
		end
	end
end
if not root then
	local src = SS:FindFirstChild('IlhaOnePiece')
	assert(src, '[auditoria] ilha nao encontrada (workspace.ILHA_ONEPIECE, Areas.Area5 ou ServerStorage.IlhaOnePiece)')
	temp = src:Clone(); temp.Name = 'AUDITORIA_COLISAO_TEMP'; temp.Parent = workspace
	root = temp
end
local edicao = not RS:IsRunning()
print(('[auditoria] ilha: %s (%s)'):format(root:GetFullName(), edicao and 'modo de edicao' or 'Play'))

local function invisivel(p) return p.Transparency >= 0.95 end
local function categoria(n)
	for _, p in ipairs({ '^COL_OP_Terrain_', '^COL_OP_Rock', '^COL_OP_Bed', '^COL_OP_Stair', '^COL_OP_Arrival_',
		'^COL_OP_ExitBridge_', '^COL_OP_CanalS_', '^COL_OP_CanalN_', '^COL_OP_Gangway_', '^COL_OPSumStair_' }) do
		if string.match(n, p) then return 'PISO_PLANTA' end
	end
	if string.match(n, '^COL_OP_V3Slab') then return 'PISO_MODULO' end
	if string.match(n, '^COL_OPAnchorGuard_') or string.match(n, '^COL_GateOnePunchMan') or string.match(n, '^COL_OP_WheelEnvelope_') then return 'JOGO' end
	if string.match(n, '^COL_OP_Fall') then return 'QUEDA' end
	if string.match(n, '^COL_OP_VegTrunk_') then return 'TRONCO' end
	if string.match(n, '^VOID_CATCH') or string.match(n, '^MiningZone') then return 'SISTEMA' end
	return 'OUTRA'
end

-- (1) colidiveis invisiveis
local colid, invis, porCat, cam = {}, {}, {}, 0
for _, d in ipairs(root:GetDescendants()) do
	if d:IsA('BasePart') then
		if CS:HasTag(d, 'CamOccluder') then cam += 1 end
		if d.CanCollide then
			table.insert(colid, d)
			if invisivel(d) then
				table.insert(invis, d)
				local c = categoria(d.Name)
				porCat[c] = (porCat[c] or 0) + 1
			end
		end
	end
end
table.sort(invis, function(a, b) return a.Size.Magnitude > b.Size.Magnitude end)
local cats = {}
for k, v in pairs(porCat) do table.insert(cats, k .. ' ' .. v) end
table.sort(cats)
local barreiras = (porCat.JOGO or 0) + (porCat.QUEDA or 0) + (porCat.TRONCO or 0) + (porCat.OUTRA or 0)
print(('(1) COLIDIVEIS INVISIVEIS: %d de %d colidiveis | %s | barreiras (JOGO+QUEDA+TRONCO+OUTRA) %d (meta < 150) | CamOccluder %d (meta 0)')
	:format(#invis, #colid, table.concat(cats, ', '), barreiras, cam))
local n = 0
for _, p in ipairs(invis) do
	local c = categoria(p.Name)
	if c ~= 'PISO_PLANTA' and c ~= 'PISO_MODULO' then
		n += 1
		if n <= MAX_LISTA then
			print(('    %-34s %-11s pos (%.1f, %.1f, %.1f) tam (%.1f, %.1f, %.1f)'):format(p.Name, c, p.Position.X, p.Position.Y,
				p.Position.Z, p.Size.X, p.Size.Y, p.Size.Z))
		end
	end
end

-- (2) em pe no ar
local visuais, guard = {}, {}
local function ligarVisual()
	if not edicao then return end
	for _, d in ipairs(root:GetDescendants()) do
		if d:IsA('MeshPart') and not d.CanCollide and d.Transparency < 0.95 then
			table.insert(guard, { d, d.CanQuery, d.CollisionFidelity })
			d.CanQuery = true
			pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end)
			table.insert(visuais, d)
		end
	end
end
local function devolver()
	for _, g in ipairs(guard) do
		local d = g[1]
		pcall(function() d.CollisionFidelity = g[3] end)
		d.CanQuery = g[2]
	end
end
local ok, erro = pcall(function()
	ligarVisual()
	local pc = RaycastParams.new(); pc.FilterType = Enum.RaycastFilterType.Include
	pc.FilterDescendantsInstances = colid; pc.RespectCanCollide = true
	local pv = RaycastParams.new(); pv.FilterType = Enum.RaycastFilterType.Include
	local vis = {}
	for _, p in ipairs(colid) do if not invisivel(p) then table.insert(vis, p) end end
	for _, p in ipairs(visuais) do table.insert(vis, p) end
	pv.FilterDescendantsInstances = vis
	local cf, size = root:GetBoundingBox()
	local lo = cf.Position - size / 2
	local hi = cf.Position + size / 2
	local total, noAr, pts, porPeca = 0, 0, {}, {}
	for x = lo.X, hi.X, PASSO do
		for z = lo.Z, hi.Z, PASSO do
			local o = Vector3.new(x, hi.Y + 5, z)
			local h = workspace:Raycast(o, Vector3.new(0, -(size.Y + 10), 0), pc)
			if h and h.Normal.Y > 0.6 then
				total += 1
				if invisivel(h.Instance) then
					local v = workspace:Raycast(h.Position + Vector3.new(0, TOL, 0), Vector3.new(0, -2 * TOL, 0), pv)
					local up = workspace:Raycast(h.Position + Vector3.new(0, 0.05, 0), Vector3.new(0, TOL, 0), pv)
					if not v and not up then
						noAr += 1
						porPeca[h.Instance.Name] = (porPeca[h.Instance.Name] or 0) + 1
						if #pts < MAX_LISTA then table.insert(pts, h) end
					end
				end
			end
		end
	end
	print(('(2) EM PE NO AR: %d de %d pontos de topo (grade %.1f) com colisor invisivel sem visual a <= %.1f%s')
		:format(noAr, total, PASSO, TOL, edicao and '' or ' (Play: so o colisor visivel conta como visual)'))
	local lst = {}
	for k, v in pairs(porPeca) do table.insert(lst, { k, v }) end
	table.sort(lst, function(a, b) return a[2] > b[2] end)
	for i = 1, math.min(MAX_LISTA, #lst) do
		print(('    %-34s %4d pontos (%s)'):format(lst[i][1], lst[i][2], categoria(lst[i][1])))
	end
	for _, h in ipairs(pts) do
		print(('    no ar em (%.1f, %.1f, %.1f) sobre %s'):format(h.Position.X, h.Position.Y, h.Position.Z, h.Instance.Name))
	end
end)
devolver()
if not ok then warn('[auditoria] medida (2) falhou: ' .. tostring(erro)) end

-- (3) fecho grande demais
local porFid, ruins, maiores = {}, {}, {}
for _, p in ipairs(colid) do
	if p:IsA('MeshPart') then
		local f = p.CollisionFidelity.Name
		porFid[f] = (porFid[f] or 0) + 1
		table.insert(maiores, p)
		local ref = p:GetAttribute('colv3_cov')
		local pr = RaycastParams.new(); pr.FilterType = Enum.RaycastFilterType.Include
		pr.FilterDescendantsInstances = { p }
		local hit, nn = 0, 0
		local c, s = p.Position, p.Size
		for a = 0, 5 do
			for b = 0, 5 do
				local x = c.X - s.X / 2 + (a + 0.5) / 6 * s.X
				local z = c.Z - s.Z / 2 + (b + 0.5) / 6 * s.Z
				nn += 1
				if workspace:Raycast(Vector3.new(x, c.Y + s.Y / 2 + 1, z), Vector3.new(0, -(s.Y + 2), 0), pr) then hit += 1 end
			end
		end
		local cov = hit / nn
		if (ref and cov - ref > 0.2) or (not ref and cov > 0.95 and s.Magnitude > 20 and f ~= 'Box') then
			table.insert(ruins, { p, cov, ref or -1 })
		end
		if p:GetAttribute('colv3') == 'H' and f ~= 'Hull' then table.insert(ruins, { p, cov, ref or -1, 'fidelidade ' .. f }) end
	end
end
table.sort(maiores, function(a, b) return a.Size.X * a.Size.Y * a.Size.Z > b.Size.X * b.Size.Y * b.Size.Z end)
local fid = {}
for k, v in pairs(porFid) do table.insert(fid, k .. ' ' .. v) end
table.sort(fid)
print(('(3) MESHPARTS COLIDIVEIS: %d (%s); fecho maior que o do Blender (cobertura +0,2) ou fidelidade errada: %d')
	:format(#maiores, table.concat(fid, ', '), #ruins))
for i = 1, math.min(MAX_LISTA, #ruins) do
	local r = ruins[i]
	print(('    %-40s cobertura %.2f (Blender %.2f) %s pos (%.1f, %.1f, %.1f) tam (%.1f, %.1f, %.1f)'):format(r[1].Name, r[2],
		r[3], r[4] or '', r[1].Position.X, r[1].Position.Y, r[1].Position.Z, r[1].Size.X, r[1].Size.Y, r[1].Size.Z))
end
print('    maiores caixas colidiveis:')
for i = 1, math.min(10, #maiores) do
	local p = maiores[i]
	print(('    %-40s %s tam (%.1f, %.1f, %.1f) cobertura Blender %s'):format(p.Name, p.CollisionFidelity.Name, p.Size.X,
		p.Size.Y, p.Size.Z, tostring(p:GetAttribute('colv3_cov'))))
end
if temp then temp:Destroy() end
print('[auditoria] fim (nada foi alterado)')
