-- pos_montagem_demonslayer.lua - roda DEPOIS do export/montar_ilha_demonslayer.lua (Command Bar ou MCP). Idempotente.
-- Transforma o workspace.ILHA_DEMONSLAYER recem-montado na FONTE que o jogo usa (ServerStorage.IlhaDemonSlayer, clonada
-- para a area 4 pelo Core.DemonSlayerIsland) e confere o que a integracao espera (so LE e avisa; nao edita script):
--  1) ILHA_DEMONSLAYER_Servidor desligado (como os das Ilhas 1-3: o grupo 'Personagens' colidiria com 'PetsVisuais';
--     as quedas ficam com o IslandTravel)
--  2) nada de prova de desenvolvimento no modelo (DS_Clr_OreProxy / COL_QA_ / PREVIEW_)
--  3) marcadores que o Core.DemonSlayerIsland usa, contagens (ORE_ 72, SAFE_ 13, AUDIO_ 8, FX_ com receita) e o
--     ENCAIXE: WORLD_FROM_PREV x ISLAND_NEXT_ANCHOR_DemonSlayer da fonte da Ilha 3 (tem de dar 0,000)
--  4) pecas moveis (IlhaMovel: roda, eixo, piloes, aneis do summon), portao One Piece (PortaoCompra) e guarda da ancora
--     (GuardaProximaIlha), luzes de dia / NightOnly, MeshParts
--  5) scripts e patches da Onda 5 instalados? (Core.DemonSlayerIsland, linha do IslandWorld, guarda no
--     JardimSombrasIsland, perfil [4] no AreaAtmosphere, CeuNatagumo) - le o Source quando a Command Bar permite
--  6) a versao anterior de ServerStorage.IlhaDemonSlayer vai para ServerStorage.IlhaDemonSlayer_anterior (rollback)
local SS = game:GetService('ServerStorage')
local SSS = game:GetService('ServerScriptService')
local CS = game:GetService('CollectionService')
local root = workspace:FindFirstChild('ILHA_DEMONSLAYER')
assert(root, 'rode o montar_ilha_demonslayer.lua antes (workspace.ILHA_DEMONSLAYER nao existe)')
local avisos = {}
local function aviso(s) table.insert(avisos, s); warn('[pos_montagem_demonslayer] ' .. s) end

-- 1) servidor do export desligado
local srv = SSS:FindFirstChild('ILHA_DEMONSLAYER_Servidor')
if srv then srv.Disabled = true end

-- 2) provas de desenvolvimento
local ruins = {}
for _, d in ipairs(root:GetDescendants()) do
	if string.match(d.Name, '^DS_Clr_OreProxy') or string.match(d.Name, '^COL_QA_') or string.match(d.Name, '^PREVIEW_') then
		table.insert(ruins, d:GetFullName())
	end
end
assert(#ruins == 0, 'prova de desenvolvimento no modelo: ' .. table.concat(ruins, ', '))

-- 3) marcadores
local mk = root:FindFirstChild('GAMEPLAY_MARKERS')
assert(mk, 'GAMEPLAY_MARKERS faltando')
local precisa = { 'WORLD_FROM_PREV', 'WORLD_ENTRY_DemonSlayer', 'ISLAND_EXIT_DemonSlayer', 'ISLAND_NEXT_ANCHOR_OnePiece',
	'MiningZone_DemonSlayer', 'SUMMON_Main', 'SUMMON_Interact', 'SUMMON_PlayerPosition', 'GATE_OnePiece',
	'GATE_OnePiece_INTERACT', 'PURCHASE_UI_ANCHOR_OnePiece', 'PATH_ENTRY_CENTER', 'FX_Fall_1_Lip', 'FX_Fall_1_Step',
	'FX_Fall_1_Base', 'FX_Fall_2_Lip', 'FX_Fall_2_Base', 'FX_Forge_Smoke', 'FX_Forge_Embers', 'FX_Mist_Bamboo',
	'FX_Mist_Ravine', 'WATER_Pond', 'WATER_Tailrace', 'WATER_Channel', 'WATER_Flume' }
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
if cont.SAFE_ ~= 13 then aviso(('SAFE_* = %d (plano: 13)'):format(cont.SAFE_)) end
if cont.AUDIO_ ~= 8 then aviso(('AUDIO_* = %d (plano: 8)'):format(cont.AUDIO_)) end
if #semReceita > 0 then aviso('FX_* sem receita de emissor (usa o padrao do DemonSlayerIsland): ' .. table.concat(semReceita, ', ')) end
local zona = mk:FindFirstChild('MiningZone_DemonSlayer')
if zona then
	local sx, sy, fl = zona:GetAttribute('sx'), zona:GetAttribute('sy'), zona:GetAttribute('floor')
	if sx ~= 112 or sy ~= 150 or math.abs((fl or 0) - 60.2) > 0.01 then
		aviso(('MiningZone sx %s sy %s floor %s (plano 112 x 150, 60,2)'):format(tostring(sx), tostring(sy), tostring(fl)))
	end
end
local lagoa = mk:FindFirstChild('WATER_Pond')
if lagoa then
	local n = 0
	for _ in string.gmatch(lagoa:GetAttribute('waypoints') or '', '[^;]+') do n += 1 end
	if n < 3 then aviso('WATER_Pond sem contorno (waypoints)') end
	if not lagoa:GetAttribute('mouth') then aviso('WATER_Pond sem mouth (o canal nao sera conferido contra a boca)') end
end

-- encaixe: a fonte da Ilha 3 (ou a Area3 montada, se o Play estiver rodando)
local encaixe = 'nao conferido (sem a Ilha 3)'
do
	local wf = mk:FindFirstChild('WORLD_FROM_PREV')
	local sg = SS:FindFirstChild('IlhaShadowGarden')
	local sgmk = sg and sg:FindFirstChild('GAMEPLAY_MARKERS')
	local anc = sgmk and sgmk:FindFirstChild('ISLAND_NEXT_ANCHOR_DemonSlayer')
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
for _, d in ipairs(root:GetDescendants()) do
	if d:IsA('MeshPart') then meshes += 1 end
	if CS:HasTag(d, 'IlhaMovel') and d:GetAttribute('movel_de') == 'ILHA_DEMONSLAYER' then moveis += 1 end
	if CS:HasTag(d, 'PortaoCompra') and d:GetAttribute('gate') == 'OnePiece' then portao += 1 end
	if d:GetAttribute('next_island_guard') then guarda += 1 end
end
if moveis == 0 then aviso('nenhuma peca IlhaMovel (roda d\'agua/piloes/aneis parados)') end
if portao == 0 then aviso('portao One Piece sem tag PortaoCompra') end
if guarda == 0 then aviso('guarda da ancora One Piece nao marcada (next_island_guard)') end
local roda = false
for _, d in ipairs(root:GetDescendants()) do
	if d:IsA('MeshPart') and string.match(d.Name, '^VFX_DS_Wheel') then roda = true; break end
end
if not roda then aviso('VFX_DS_Wheel nao encontrada (roda d\'agua)') end
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
local function confere(rotulo, inst, trecho)
	if not inst then aviso(rotulo .. ': script nao encontrado'); return end
	if not trecho then return end
	local s = fonte(inst)
	if s == nil then aviso(rotulo .. ': nao consegui ler o Source (confira a mao)')
	elseif not string.find(s, trecho, 1, true) then aviso(rotulo .. ': falta "' .. trecho .. '"') end
end
confere('Core.DemonSlayerIsland', core and core:FindFirstChild('DemonSlayerIsland'), "M.GATE_KEY = 'OnePiece'")
confere('Core.IslandWorld (linha da Ilha 4)', core and core:FindFirstChild('IslandWorld'), 'DemonSlayer.build(parent,area)')
confere('Core.JardimSombrasIsland (guarda da ancora)', core and core:FindFirstChild('JardimSombrasIsland'), "FindFirstChild('IlhaDemonSlayer')")
local SPS = game:GetService('StarterPlayer'):FindFirstChildOfClass('StarterPlayerScripts')
confere('AreaAtmosphere (perfil [4])', SPS and SPS:FindFirstChild('AreaAtmosphere'), "name='Natagumo',time=20.5")
confere('CeuNatagumo', SPS and SPS:FindFirstChild('CeuNatagumo'), 'MarNuvensNatagumoLocal')
confere('ILHA_NARUTO_Movel (gira a roda)', SPS and SPS:FindFirstChild('ILHA_NARUTO_Movel'), nil)
local rs = game:GetService('ReplicatedStorage')
confere('PortoesCompra', rs:FindFirstChild('PortoesCompra'), nil)
local gachas = workspace:FindFirstChild('Gachas')
if not (gachas and gachas:FindFirstChild('Gacha_nichirin')) then aviso('workspace.Gachas.Gacha_nichirin nao encontrado (motor da torre)') end

-- 6) vira a fonte
local velho = SS:FindFirstChild('IlhaDemonSlayer')
if velho then
	local ant = SS:FindFirstChild('IlhaDemonSlayer_anterior'); if ant then ant:Destroy() end
	velho.Name = 'IlhaDemonSlayer_anterior'
end
root.Name = 'IlhaDemonSlayer'
root.Parent = SS
print(('Ilha Demon Slayer pronta em ServerStorage.IlhaDemonSlayer: %d MeshParts, %d ORE_*, %d GP_Block_*, %d SAFE_*, %d AUDIO_*, %d PATH_ENTRY, %d FX_* com receita, %d moveis, %d pecas do portao OP, %d da guarda, luzes %d de dia + %d NightOnly; encaixe %s')
	:format(meshes, cont.ORE_, cont.GP_Block_, cont.SAFE_, cont.AUDIO_, cont.PATH_ENTRY_CENTER_, receitas, moveis, portao,
		guarda, dia, noite, encaixe))
print(#avisos == 0 and 'pos_montagem_demonslayer: sem avisos' or ('pos_montagem_demonslayer: %d aviso(s) acima'):format(#avisos))
