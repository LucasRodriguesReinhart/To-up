-- pos_montagem_onepiece.lua - roda DEPOIS do export/montar_ilha_onepiece.lua (Command Bar ou MCP). Idempotente.
-- Transforma o workspace.ILHA_ONEPIECE recem-montado na FONTE que o jogo usa (ServerStorage.IlhaOnePiece, clonada para
-- a area 5 pelo Core.OnePieceIsland; e o nome que a DS ja espera em FONTE_PROXIMA) e confere o que a integracao espera
-- (so LE e avisa; nao edita script):
--  1) ILHA_ONEPIECE_Servidor desligado (como os das Ilhas 1-4: o grupo 'Personagens' colidiria com 'PetsVisuais'; as
--     quedas ficam com o IslandTravel)
--  2) nada de prova de desenvolvimento no modelo (OP_Plz_OreProxy / COL_QA_ / PREVIEW_), e o trecho do M2
--     (workspace.ILHA_ONEPIECE_M2) nao pode ficar no place junto da ilha inteira
--  3) marcadores que o Core.OnePieceIsland e o CeuWano usam, contagens (ORE_ 72, GP_Block_ 76, SAFE_ 17, AUDIO_ 9,
--     PATH_ENTRY_CENTER_ 11), atributos da agua (contorno da bacia, boca, roda, bica do labio, mar 36 / 2200) e o
--     ENCAIXE: WORLD_FROM_PREV x ISLAND_NEXT_ANCHOR_OnePiece da fonte da Ilha 4 (tem de dar 0,000)
--  4) pecas moveis (IlhaMovel: roda d'agua VFX_OP_Wheel, aneis/estrela do summon), portao One Punch Man (PortaoCompra)
--     e guarda da ancora (GuardaProximaIlha), luzes de dia (teto 36) / NightOnly, MeshParts
--  5) scripts e patches do M5 instalados? (Core.OnePieceIsland, linha do IslandWorld - aceita a forma SEM require no
--     topo -, perfil [5]/WanoMood no AreaAtmosphere, CeuWano, FONTE_PROXIMA da DS) - le o Source quando a Command Bar
--     permite
--  6) a versao anterior de ServerStorage.IlhaOnePiece vai para ServerStorage.IlhaOnePiece_anterior (rollback)
local SS = game:GetService('ServerStorage')
local SSS = game:GetService('ServerScriptService')
local CS = game:GetService('CollectionService')
local root = workspace:FindFirstChild('ILHA_ONEPIECE')
assert(root, 'rode o montar_ilha_onepiece.lua antes (workspace.ILHA_ONEPIECE nao existe)')
local avisos = {}
local function aviso(s) table.insert(avisos, s); warn('[pos_montagem_onepiece] ' .. s) end

-- 1) servidor do export desligado
local srv = SSS:FindFirstChild('ILHA_ONEPIECE_Servidor')
if srv then srv.Disabled = true end
local srvM2 = SSS:FindFirstChild('ILHA_ONEPIECE_M2_Servidor')
if srvM2 then srvM2.Disabled = true end

-- 2) provas de desenvolvimento
local ruins = {}
for _, d in ipairs(root:GetDescendants()) do
	if string.match(d.Name, '^OP_Plz_OreProxy') or string.match(d.Name, '^COL_QA_') or string.match(d.Name, '^PREVIEW_') then
		table.insert(ruins, d:GetFullName())
	end
end
assert(#ruins == 0, 'prova de desenvolvimento no modelo: ' .. table.concat(ruins, ', '))
if workspace:FindFirstChild('ILHA_ONEPIECE_M2') then
	aviso('workspace.ILHA_ONEPIECE_M2 (trecho de validacao do M2) ainda esta no place: mova para ServerStorage ou apague')
end

-- 3) marcadores
local mk = root:FindFirstChild('GAMEPLAY_MARKERS')
assert(mk, 'GAMEPLAY_MARKERS faltando')
local precisa = { 'WORLD_FROM_PREV', 'WORLD_ENTRY_OnePiece', 'ISLAND_EXIT_OnePiece', 'ISLAND_NEXT_ANCHOR_OnePunchMan',
	'MiningZone_OnePiece', 'SUMMON_Main', 'SUMMON_Interact', 'SUMMON_PlayerPosition', 'GATE_OnePunchMan',
	'GATE_OnePunchMan_INTERACT', 'PURCHASE_UI_ANCHOR_OnePunchMan', 'PATH_ENTRY_CENTER', 'FX_Fall_Castle_Lip',
	'FX_Fall_Castle_Step', 'FX_Fall_Castle_Base', 'FX_Fall_E_Lip', 'FX_Fall_E_Base', 'FX_Fall_W_Lip', 'FX_Fall_W_Base',
	'FX_Weir_E', 'FX_Weir_W', 'FX_Spring_W', 'FX_Petals_Tree', 'FX_Mist_CastleFall', 'WATER_Sea', 'WATER_Basin',
	'WATER_CanalE', 'WATER_CanalW' }
local faltam = {}
for _, n in ipairs(precisa) do if not mk:FindFirstChild(n) then table.insert(faltam, n) end end
if #faltam > 0 then aviso('marcadores faltando: ' .. table.concat(faltam, ', ')) end
local cont = { ORE_ = 0, GP_Block_ = 0, SAFE_ = 0, AUDIO_ = 0, PATH_ENTRY_CENTER_ = 0 }
local receitas, semReceita = 0, {}
for _, m in ipairs(mk:GetChildren()) do
	for pre in pairs(cont) do
		if string.sub(m.Name, 1, #pre) == pre then cont[pre] += 1 end
	end
	if string.match(m.Name, '^FX_') then
		if m:GetAttribute('vfx') == 'emissor' then receitas += 1 else table.insert(semReceita, m.Name) end
	end
end
if cont.ORE_ ~= 72 then aviso(('ORE_* = %d (plano: 72)'):format(cont.ORE_)) end
if cont.GP_Block_ ~= 76 then aviso(('GP_Block_* = %d (plano: 76 = 48 borda + 28 canto)'):format(cont.GP_Block_)) end
if cont.SAFE_ ~= 17 then aviso(('SAFE_* = %d (plano: 17)'):format(cont.SAFE_)) end
if cont.AUDIO_ ~= 9 then aviso(('AUDIO_* = %d (plano: 9)'):format(cont.AUDIO_)) end
if cont.PATH_ENTRY_CENTER_ ~= 11 then aviso(('PATH_ENTRY_CENTER_* = %d (plano: 11)'):format(cont.PATH_ENTRY_CENTER_)) end
-- sem receita e o esperado ate existir o op_vfx: o OnePieceIsland usa as reservas (petalas, nevoa) e a agua(); so informa
if #semReceita > 0 then
	print('[pos_montagem_onepiece] FX_* sem receita de emissor (reservas do OnePieceIsland): ' .. table.concat(semReceita, ', '))
end
local zona = mk:FindFirstChild('MiningZone_OnePiece')
if zona then
	local sx, sy, fl = zona:GetAttribute('sx'), zona:GetAttribute('sy'), zona:GetAttribute('floor')
	if sx ~= 152 or sy ~= 120 or math.abs((fl or 0) - 92.2) > 0.01 then
		aviso(('MiningZone sx %s sy %s floor %s (plano 152 x 120, 92,2)'):format(tostring(sx), tostring(sy), tostring(fl)))
	end
end
local function npts(s)
	local n = 0
	for _ in string.gmatch(s or '', '[^;]+') do n += 1 end
	return n
end
local function temTrio(m, k)
	return m and type(m:GetAttribute(k .. '_x')) == 'number' and type(m:GetAttribute(k .. '_z')) == 'number'
end
local bacia = mk:FindFirstChild('WATER_Basin')
if bacia then
	if npts(bacia:GetAttribute('waypoints')) < 3 then aviso('WATER_Basin sem contorno (waypoints)') end
	if not (temTrio(bacia, 'mouth_a_pos') and temTrio(bacia, 'mouth_b_pos')) then
		aviso('WATER_Basin sem mouth_a_pos/mouth_b_pos (o canal leste nao sera conferido contra a boca)')
	end
end
for _, n in ipairs({ 'WATER_CanalE', 'WATER_CanalW', 'FX_Fall_Castle_Lip', 'FX_Fall_E_Lip', 'FX_Fall_W_Lip', 'FX_Spring_W' }) do
	local m = mk:FindFirstChild(n)
	if m and npts(m:GetAttribute('waypoints')) < 2 then aviso(n .. ' sem waypoints medidos (export antigo do M1?)') end
end
local cw = mk:FindFirstChild('WATER_CanalW')
if cw and not temTrio(cw, 'wheel_pos') then aviso('WATER_CanalW sem wheel_pos (espuma da roda)') end
local lip = mk:FindFirstChild('FX_Fall_Castle_Lip')
if lip and npts(lip:GetAttribute('spout_waypoints')) < 2 then aviso('FX_Fall_Castle_Lip sem spout_waypoints (bica do labio)') end
local st = mk:FindFirstChild('FX_Fall_Castle_Step')
if st and not temTrio(st, 'step2_pos') then aviso('FX_Fall_Castle_Step sem step2_pos (degrau de espuma de baixo)') end
local mar = mk:FindFirstChild('WATER_Sea')
if mar then
	local lv, sz = mar:GetAttribute('level'), mar:GetAttribute('size')
	if math.abs((lv or 0) - 36) > 0.01 or math.abs((sz or 0) - 2200) > 0.01 then
		aviso(('WATER_Sea level %s size %s (plano 36, 2200)'):format(tostring(lv), tostring(sz)))
	end
end

-- encaixe: a fonte da Ilha 4 (ou a Area4 montada, se o Play estiver rodando)
local encaixe = 'nao conferido (sem a Ilha 4)'
do
	local wf = mk:FindFirstChild('WORLD_FROM_PREV')
	local ds = SS:FindFirstChild('IlhaDemonSlayer')
	local dsmk = ds and ds:FindFirstChild('GAMEPLAY_MARKERS')
	local anc = dsmk and dsmk:FindFirstChild('ISLAND_NEXT_ANCHOR_OnePiece')
	if not anc then
		local a4 = workspace:FindFirstChild('Areas') and workspace.Areas:FindFirstChild('Area4')
		local m4 = a4 and a4:FindFirstChild('ILHA_DEMONSLAYER')
		anc = m4 and m4:FindFirstChild('GAMEPLAY_MARKERS') and m4.GAMEPLAY_MARKERS:FindFirstChild('ISLAND_NEXT_ANCHOR_OnePiece')
	end
	if wf and anc then
		local d = (wf.Position - anc.Position).Magnitude
		local fa = Vector3.new(anc:GetAttribute('fwd_x') or 0, 0, anc:GetAttribute('fwd_z') or 0)
		local fw = Vector3.new(wf:GetAttribute('fwd_x') or 0, 0, wf:GetAttribute('fwd_z') or 0)
		local dot = (fa.Magnitude > 0 and fw.Magnitude > 0) and fa.Unit:Dot(fw.Unit) or 0
		encaixe = ('distancia %.3f, frentes %.4f (cos)'):format(d, dot)
		if d > 0.01 or dot < 0.9999 then aviso('ENCAIXE fora: ' .. encaixe) end
	end
end

-- 4) pecas moveis, portao, guarda, luzes, malhas
local moveis, portao, guarda, meshes = 0, 0, 0, 0
local roda = false
for _, d in ipairs(root:GetDescendants()) do
	if d:IsA('MeshPart') then
		meshes += 1
		if string.match(d.Name, '^VFX_OP_Wheel') then roda = true end
	end
	if CS:HasTag(d, 'IlhaMovel') and d:GetAttribute('movel_de') == 'ILHA_ONEPIECE' then moveis += 1 end
	if CS:HasTag(d, 'PortaoCompra') and d:GetAttribute('gate') == 'OnePunchMan' then portao += 1 end
	if d:GetAttribute('next_island_guard') then guarda += 1 end
end
if moveis == 0 then aviso('nenhuma peca IlhaMovel (roda d\'agua / aneis do summon parados)') end
if not roda then aviso('VFX_OP_Wheel nao encontrada (roda d\'agua)') end
if portao == 0 then aviso('portao One Punch Man sem tag PortaoCompra') end
if guarda == 0 then aviso('guarda da ancora One Punch Man nao marcada (next_island_guard)') end
local dia, noite = 0, 0
local lt = root:FindFirstChild('LIGHTS')
for _, l in ipairs(lt and lt:GetDescendants() or {}) do
	if l:IsA('Light') then if l:GetAttribute('NightOnly') then noite += 1 else dia += 1 end end
end
if dia > 36 then aviso(('%d luzes de dia (teto 36)'):format(dia)) end

-- 5) scripts e patches (so leitura; a Command Bar pode ler Source)
local function fonte(inst)
	local ok, s = pcall(function() return inst.Source end)
	return ok and s or nil
end
local core = SSS:FindFirstChild('Core')
local function confere(rotulo, inst, ...)
	if not inst then aviso(rotulo .. ': script nao encontrado'); return end
	local trechos = { ... }
	if #trechos == 0 then return end
	local s = fonte(inst)
	if s == nil then aviso(rotulo .. ': nao consegui ler o Source (confira a mao)'); return end
	for _, t in ipairs(trechos) do
		if not string.find(s, t, 1, true) then aviso(rotulo .. ': falta "' .. t .. '"') end
	end
end
confere('Core.OnePieceIsland', core and core:FindFirstChild('OnePieceIsland'), "M.GATE_KEY = 'OnePunchMan'",
	"M.FONTE = 'IlhaOnePiece'")
-- IslandWorld: aceita a forma do Play da Ilha 4 (sem require no topo: require(script.Parent.OnePieceIsland).build) ou
-- a antiga (local OnePiece=require(...) no topo + OnePiece.build(parent,area)); o que importa e o tema e a fonte
do
	local iw = core and core:FindFirstChild('IslandWorld')
	local s = iw and fonte(iw)
	if not iw then aviso('Core.IslandWorld: script nao encontrado')
	elseif s == nil then aviso('Core.IslandWorld: nao consegui ler o Source (confira a mao a linha da Ilha 5)')
	else
		local temTema = string.find(s, "area.tema=='mare'", 1, true) or string.find(s, 'area.tema=="mare"', 1, true)
		local temFonte = string.find(s, "'IlhaOnePiece'", 1, true) or string.find(s, '"IlhaOnePiece"', 1, true)
		local temBuild = string.find(s, 'OnePieceIsland).build(parent,area)', 1, true) or string.find(s, 'OnePiece.build(parent,area)', 1, true)
		if not (temTema and temFonte and temBuild) then aviso('Core.IslandWorld: falta a linha da Ilha 5 (ver IslandWorld_linha.md)') end
	end
end
confere('Core.DemonSlayerIsland (remove a guarda da DS)', core and core:FindFirstChild('DemonSlayerIsland'),
	"M.FONTE_PROXIMA = 'IlhaOnePiece'")
local SPS = game:GetService('StarterPlayer'):FindFirstChildOfClass('StarterPlayerScripts')
confere('AreaAtmosphere (perfil [5] + WanoMood)', SPS and SPS:FindFirstChild('AreaAtmosphere'), "name='GrandLine'", "'WanoMood'",
	'profile.cbright')
confere('CeuWano', SPS and SPS:FindFirstChild('CeuWano'), 'MarWanoLocal')
confere('CeuNatagumo (devolve o Sky ao sair da DS)', SPS and SPS:FindFirstChild('CeuNatagumo'), 'restaurarCeu')
confere('ILHA_NARUTO_Movel (gira a roda)', SPS and SPS:FindFirstChild('ILHA_NARUTO_Movel'))
local rs = game:GetService('ReplicatedStorage')
confere('PortoesCompra', rs:FindFirstChild('PortoesCompra'))
local gachas = workspace:FindFirstChild('Gachas')
if not (gachas and gachas:FindFirstChild('Gacha_mare')) then aviso('workspace.Gachas.Gacha_mare nao encontrado (motor da torre)') end

-- 6) vira a fonte
local velho = SS:FindFirstChild('IlhaOnePiece')
if velho then
	local ant = SS:FindFirstChild('IlhaOnePiece_anterior'); if ant then ant:Destroy() end
	velho.Name = 'IlhaOnePiece_anterior'
end
root.Name = 'IlhaOnePiece'
root.Parent = SS
print(('Ilha One Piece pronta em ServerStorage.IlhaOnePiece: %d MeshParts, %d ORE_*, %d GP_Block_*, %d SAFE_*, %d AUDIO_*, %d PATH_ENTRY, %d FX_* com receita (%d sem), %d moveis, %d pecas do portao OPM, %d da guarda, luzes %d de dia + %d NightOnly; encaixe %s')
	:format(meshes, cont.ORE_, cont.GP_Block_, cont.SAFE_, cont.AUDIO_, cont.PATH_ENTRY_CENTER_, receitas, #semReceita,
		moveis, portao, guarda, dia, noite, encaixe))
print(#avisos == 0 and 'pos_montagem_onepiece: sem avisos' or ('pos_montagem_onepiece: %d aviso(s) acima'):format(#avisos))
