assert(not game:GetService('RunService'):IsRunning(),'Install only in Edit')
local H=game:GetService('HttpService')
local function resolve(path) local v=game for k in path:gmatch('[^.]+') do v=v:FindFirstChild(k) if not v then return nil end end return v end
local function norm(s) return (s:gsub('\r\n','\n'):gsub('%s+$','')) end
local function replaceOnce(s,old,new)
 local a,b=s:find(old,1,true) if not a then error('Expected audio patch missing') end
 assert(not s:find(old,b+1,true),'Audio patch ambiguous')
 return s:sub(1,a-1)..new..s:sub(b+1)
end
local specs={}
table.insert(specs,{name=[========[ReplicatedStorage.AudioCatalog]========],source=[========[-- AMS Audio V3. Licensed Roblox library sources; see ASSET_CANDIDATES.json.
-- Short playback windows are envelopes, not new uploaded derivative assets.
local C = {}
C.Version = 3
C.Budget = {voices=24, Mining=10, Rewards=8, UI=3, World=4, remote=4, loops=4}
C.Defaults = {Master=.8, Music=.6, SFX=.85, UI=.65, Ambience=.55}
C.Assets = {
 stone={9118598279,9118598469,9118598729,9118598470,9118598240},
 metal={9116651255,9116652339}, heavy={9118617342},
 crack={9118612665,9125869797}, debris={9118690959},
 swing={9120972321,9120972444,9120972323},
 click={9119717523,9119717529}, tone={9125531715}, glass={9114619221}, coin={9125509503,9125444889},
 fire={9112780438}, wind={9116258071}, water={9112855484}, energy={9125515917},
}
-- Measured from Roblox AudioPlayer waveform data, 2026-09-17 (1500 points/asset).
-- Start just before the audible attack; compensate source loudness, not event importance.
C.Trim={
 [9118598279]={offset=0,gain=1.0}, [9118598469]={offset=0,gain=1.0},
 [9118598729]={offset=0,gain=.90}, [9118598470]={offset=0,gain=1.12}, [9118598240]={offset=.002,gain=.90},
 [9120972321]={offset=.065,gain=.90}, [9120972444]={offset=.016,gain=1.55}, [9120972323]={offset=.056,gain=1.15},
 [9125509503]={offset=.344,gain=1.25}, [9125444889]={offset=0,gain=.95},
 [9114619221]={offset=.108,gain=2.4}, [9125531715]={offset=.200,gain=2.0},
}
-- A coherent dry-metal/crystal voice; reward figures use C-D-E-G across octaves.
local A=C.Assets
local function L(family,vol,duration,pitch,delay)
 return {family=family,volume=vol,duration=duration,pitch=pitch or 1,delay=delay or 0,variation=(family=='tone' or family=='coin') and 0 or .035}
end
local E={}
local function event(name,bus,priority,gap,layers,max)
 E[name]={bus=bus,priority=priority,gap=gap,max=max or 3,layers=layers}
end
event('hit','Mining',75,.045,{L('stone',.44,.32),L('metal',.12,.17,1.04)},5)
event('hit_pesado','Mining',70,.13,{L('heavy',.17,.32,.94)},2)
event('hit_crystal','Mining',74,.045,{L('stone',.32,.27),L('glass',.12,.26,1.12)},4)
event('hit_metal','Mining',74,.045,{L('stone',.30,.24),L('metal',.17,.24,.97)},4)
event('hit_magic','Mining',74,.045,{L('stone',.34,.28),L('tone',.11,.30,1.26)},4)
event('hit_lava','Mining',74,.045,{L('stone',.35,.28),L('heavy',.13,.32,.90)},4)
event('rock_crack','Mining',68,.30,{L('crack',.14,.24,1.08)},2)
event('critical_hit','Mining',80,.20,{L('metal',.14,.2,1.12),L('tone',.10,.22,1.5)},2)
event('whoosh','Mining',50,.13,{L('swing',.17,.21,1.02)},3)
for i,name in ipairs({'comum','incomum','raro','epico','lendario','chefe'}) do
 local layers={L('crack',.43,.48+(i-1)*.035,1.03-(i-1)*.017),L('debris',.09,.35,1,.055)}
 if i>=3 then table.insert(layers,L('tone',.11,.33,({1,1,1.25,1.5,2,1})[i],.09)) end
 event('break_'..name,'Mining',85,.1,layers,2)
end
event('ore_drop','Rewards',40,.15,{L('tone',.07,.14,1.12)},2)
event('coleta','Rewards',58,.075,{L('tone',.14,.14,1)},3)
event('coin_tick','Rewards',35,.12,{L('coin',.09,.12,1.12)},2)
local saleNames={'venda_pequena','venda_media','venda_grande','venda_enorme','venda_jackpot'}
for i,name in ipairs(saleNames) do
 local layers={L('click',.16,.12,1),L('coin',.20,.20,1,.06)}
 if i>=2 then table.insert(layers,L('coin',.16,.20,1.25,.15)) end
 if i>=3 then table.insert(layers,L('tone',.18,.38,1.5,.24)) end
 if i>=4 then table.insert(layers,L('tone',.17,.50,2,.36)) end
 if i==5 then table.insert(layers,L('heavy',.12,.32,.9,.02)) end
 event(name,'Rewards',80,.65,layers,1)
end
local function motif(name,notes,priority,duration)
 local layers={}
 for i,n in ipairs(notes) do table.insert(layers,L('tone',.22-((i-1)*.014),duration or .34,2^(n/12),(i-1)*.105)) end
 event(name,'Rewards',priority or 80,.65,layers,1)
end
motif('upgrade',{0,4,7},80)
motif('upgrade_max',{0,4,7,12},86,.45)
motif('level_up',{0,2,7,12},88,.48)
motif('area_nova',{0,7,4,12},91,.55)
motif('quest_complete',{4,7,12},82)
motif('achievement',{0,4,12},83)
motif('boost',{0,7},72)
motif('reward_banner',{0,4,7},74)
motif('forge_success',{0,7,12},82)
event('forge_interact','World',54,.4,{L('metal',.15,.25,.95)},1)
event('forge_hammer','World',28,.50,{L('metal',.19,.27,.94),L('heavy',.06,.2,1)},1)
event('invocar_inicio','Rewards',65,.4,{L('swing',.16,.38,.95),L('tone',.10,.35,.75,.13)},1)
event('summon_reveal','Rewards',65,.18,{L('tone',.14,.23,1.12)},1)
motif('drop_comum',{0},65,.2)
motif('drop_incomum',{0,4},69,.26)
motif('drop_raro',{0,7},75,.36)
motif('drop_epico',{0,4,7},82,.42)
motif('drop_lendario',{0,4,7,12},90,.60)
motif('drop_mitico',{0,7,12,16},94,.64)
event('drop_secreto','Rewards',100,1.3,{
 L('swing',.14,.27,.78),L('heavy',.13,.27,.91,.21),
 L('tone',.24,.65,1,.28),L('tone',.19,.65,1.5,.40),L('tone',.18,.72,2,.54),L('tone',.14,.75,2.5,.67),
},1)
E.drop_lendario.duck=.75 E.drop_mitico.duck=.62 E.drop_secreto.duck=.48 E.area_nova.duck=.70
event('portal_saida','World',70,.6,{L('swing',.22,.40,.85),L('tone',.12,.45,.75,.09)},1)
event('portal_chegada','World',65,.6,{L('swing',.14,.30,1.04),L('tone',.10,.28,1.25)},1)
event('ui_click','UI',60,.055,{L('click',.17,.075,1)},2)
event('ui_hover','UI',15,.18,{L('click',.035,.04,1.04)},1)
event('ui_tab','UI',48,.075,{L('click',.11,.065,1.05)},1)
event('ui_toggle','UI',50,.075,{L('click',.12,.08,.94)},1)
event('ui_abrir','UI',53,.12,{L('swing',.12,.14,1.06),L('click',.07,.07,1)},1)
event('ui_fechar','UI',53,.12,{L('swing',.09,.12,.94)},1)
event('ui_popup','UI',49,.15,{L('swing',.09,.14,1.1)},1)
event('ui_notify','UI',40,.4,{L('tone',.085,.13,1.12)},1)
event('ui_equipar','UI',68,.16,{L('swing',.11,.13,1.02),L('metal',.16,.18,1,.04)},1)
event('ui_desequipar','UI',60,.16,{L('metal',.10,.13,.92)},1)
event('ui_compra','UI',68,.2,{L('click',.15,.09),L('tone',.14,.2,1.25,.07)},1)
event('ui_confirm','UI',62,.15,{L('tone',.11,.17,1),L('tone',.10,.19,1.25,.065)},1)
event('ui_cancel','UI',50,.15,{L('click',.1,.1,.9)},1)
event('ui_erro','UI',70,.32,{L('click',.14,.1,.84),L('click',.10,.11,.75,.10)},1)
C.Events=E
C.Music={
 [0]={id=112898538778548,name='Lobby',volume=.23},
 [1]={id=82061470648013,name='Hidden Lotus Pond',volume=.22},
 [2]={id=1845421369,name='Space Atmosphere',volume=.23},
 [3]={id=9048681794,name='Mysterious Forest',volume=.20},
 [4]={id=131334832939011,name='The Forgotten Crypt',volume=.20},
 [5]={id=1835322563,name='Pirate King',volume=.20},
 [6]={id=1845676363,name='Home Bound',volume=.21},
}
C.SaleNames=saleNames
return C
]========],base=nil,edits={{old=[========[-- A coherent dry-metal/crystal voice, with a pentatonic signature C-D-E-G-A.]========],new=[========[-- A coherent dry-metal/crystal voice; reward figures use C-D-E-G across octaves.]========]}}})
table.insert(specs,{name=[========[StarterPlayer.StarterPlayerScripts.AudioWorld]========],source=[========[-- Physical sound sources follow the actual scene, including dynamically built areas.
local RS=game:GetService('ReplicatedStorage')
local Som=require(RS:WaitForChild('SomJogo'))
local registered={}
local connections={}
local destroyed=false
local function point(v)
 if v:IsA('BasePart') then return v.Position elseif v:IsA('Model') then return v:GetPivot().Position end
end
local function register(v)
 if registered[v] then return end
 local family,range,volume
 -- Exact scene semantics: portal decorations are not additional emitters.
 if v:IsA('Model') and v.Name:match('^Portal%d$') and v.Parent.Name=='Santuario' then family,range,volume='energy',36,.15
 elseif v:IsA('Model') and v.Name=='PortalDeProgressao' then family,range,volume='energy',34,.13
 elseif v:IsA('BasePart') and v.Name=='hot_billet' then family,range,volume='fire',38,.18
 elseif v:IsA('BasePart') and v.Name=='ForgeChimney' then family,range,volume='fire',42,.13
 elseif v:IsA('Texture') and v.Name=='FluxoCachoeira' and v.Parent:IsA('BasePart') then
  local carrier=v.Parent
  if not registered[carrier] then registered[carrier]=true Som.RegisterEmitter(carrier,'water',carrier.Position,52,.16) end
  return
 end
 if family then registered[v]=true Som.RegisterEmitter(v,family,point(v),range,volume) end
 if v:IsA('Model') and v.Name=='Ignis' and v.Parent.Name=='NPCs' then
  registered[v]=true
  table.insert(connections,v:GetAttributeChangedSignal('ForgeImpactTime'):Connect(function()
   local stamp=v:GetAttribute('ForgeImpactTime')
   if stamp and workspace:GetServerTimeNow()-stamp<.3 then
    local billet=v:FindFirstChild('hot_billet',true)
    Som.tocar('forge_hammer',{pos=billet and billet.Position or v:GetPivot().Position,maxDistance=40})
   end
  end))
 end
end
for _,v in ipairs(workspace:GetDescendants()) do register(v) end
table.insert(connections,workspace.DescendantAdded:Connect(register))
table.insert(connections,workspace.DescendantRemoving:Connect(function(v) if registered[v] then Som.RemoveEmitter(v) registered[v]=nil end end))
-- Locomotion remains recognizable but no longer bypasses the player's master/SFX mix.
local SS=game:GetService('SoundService')
local function characterSound(v)
 if v:IsA('Sound') and v.Parent and v.Parent.Name=='HumanoidRootPart' then
  local master=SS:FindFirstChild('MASTER')
  local sfx=master and master:FindFirstChild('SFX')
  local group=sfx and sfx:FindFirstChild('SFX_GAMEPLAY')
  if group then v.SoundGroup=group v.RollOffMinDistance=5 v.RollOffMaxDistance=38
   if v.Name=='Running' or v.Name=='Climbing' then v.Volume=.26 else v.Volume=math.min(v.Volume,.4) end
  end
 end
end
for _,v in ipairs(workspace:GetDescendants()) do characterSound(v) end
table.insert(connections,workspace.DescendantAdded:Connect(characterSound))
-- Equipment confirmation belongs to ExpeditionClient's authoritative response.
-- PicaretaTool replaces instances on its polling cycle; ChildAdded/Removed here
-- would repeat that confirmation (and play unequip) up to a second later.
-- Rarely update moved sources, never scan the full scene per frame.
task.spawn(function()
 while not destroyed do
  task.wait(2)
  for v in pairs(registered) do
   if not v.Parent then Som.RemoveEmitter(v) registered[v]=nil else local p=point(v) if p then Som.MoveEmitter(v,p) end end
  end
 end
end)
script.Destroying:Connect(function()
 destroyed=true
 for _,c in ipairs(connections) do c:Disconnect() end
 for v in pairs(registered) do Som.RemoveEmitter(v) end
end)
]========],base=nil,edits={{old=[========[local Players=game:GetService('Players')
]========],new=[========[]========]},{old=[========[local player=Players.LocalPlayer
]========],new=[========[]========]},{old=[========[local root=player.Character
local function watchCharacter(c)
 c.ChildAdded:Connect(function(v)
  if v:IsA('Tool') and v.Name=='Picareta' then Som.tocar('ui_equipar') end
 end)
 c.ChildRemoved:Connect(function(v)
  if v:IsA('Tool') and v.Name=='Picareta' and c.Parent then Som.tocar('ui_desequipar') end
 end)
end
if root then watchCharacter(root) end
table.insert(connections,player.CharacterAdded:Connect(watchCharacter))]========],new=[========[-- Equipment confirmation belongs to ExpeditionClient's authoritative response.
-- PicaretaTool replaces instances on its polling cycle; ChildAdded/Removed here
-- would repeat that confirmation (and play unequip) up to a second later.]========]}}})
table.insert(specs,{name=[========[ServerScriptService.Core.PlayerData]========],source=[========[local RS = game:GetService("ReplicatedStorage")
local DSS = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Config = require(RS.Config)
local AudioPreferences = require(RS:WaitForChild("AudioPreferences"))
local Passes = require(script.Parent.Passes)

-- ---------- ARMAZENAMENTO ----------
-- O GetDataStore nao bate na API, entao ele passa mesmo com o acesso desligado.
-- Quem falha e a primeira chamada real. Por isso a sondagem abaixo.
local memoria = {}
local storeMemoria = {
	GetAsync = function(_, k) return memoria[k] end,
	SetAsync = function(_, k, v) memoria[k] = v end,
	UpdateAsync = function(_, k, fn)
		local novo = fn(memoria[k])
		if novo ~= nil then memoria[k] = novo end
		return memoria[k]
	end,
}

local store = storeMemoria
local USANDO_MEMORIA = true
local MOTIVO = "nao testado"

do
	local okObter, real = pcall(function()
		return DSS:GetDataStore("MineracaoSim_v2")
	end)
	if okObter and real then
		local okLer, err = pcall(function()
			real:GetAsync("__sonda__")
		end)
		if okLer then
			store = real
			USANDO_MEMORIA = false
			MOTIVO = "ok"
		else
			MOTIVO = tostring(err)
		end
	else
		MOTIVO = tostring(real)
	end
end

if USANDO_MEMORIA then
	local motivoLower = string.lower(MOTIVO)
	if string.find(motivoLower, "studio access", 1, true)
		or string.find(motivoLower, "api services", 1, true)
		or string.find(motivoLower, "studioaccesstoapis", 1, true) then
		warn("[PlayerData] DataStore desligado no Studio. Progresso so nesta sessao.")
		warn("[PlayerData] Pra salvar de verdade: Home > Game Settings > Security > Enable Studio Access to API Services")
	else
		warn("[PlayerData] DataStore indisponivel (" .. MOTIVO .. "). Progresso so nesta sessao.")
	end
else
	print("[PlayerData] DataStore ativo, progresso sera salvo")
end

function PlayerDataUsandoMemoria() return USANDO_MEMORIA end

local PlayerData = {}
local cache = {}
local sessaoId = HttpService:GenerateGUID(false)
local TRAVA_VALIDA = 180 -- segundos: trava de outra sessao mais velha que isso e considerada abandonada

local function perfilNovo()
	return {
		audio = AudioPreferences.sanitize(), -- preferences share the existing profile/autosave
		moeda = 0,
		picareta = "enferrujada",
		mochilaTier = "saco_pano",
		mochila = {},            -- [idMinerio] = quantidade
		hats = {},               -- formato antigo (empilhado), so pra migracao
		hatsInv = {},            -- [uid] = { id, nivel, xp, xpTotal }  cada hat e um item separado
		hatSeq = 0,
		equipados = {},          -- lista de uid (pode ter 2 hats iguais)
		pets = {},               -- formato antigo (empilhado), so pra migracao
		petsInv = {},            -- [uid] = { id, nivel, xp, xpTotal, apelido }
		petSeq = 0,
		petsEquipados = {},      -- lista de uid
		apelidos = {},           -- formato antigo, so pra migracao
		picaretasCompradas = { enferrujada = true },
		missoes = {},            -- [idMissao] = { p = progresso, r = resgatada }
		codigos = {},            -- [CODIGO] = true quando ja resgatado
		minerados = 0,           -- minerios quebrados (placar)
		areas = { [1] = true },
		-- economia v3.1
		econVersao = Config.ECON_VERSAO,
		pity = { l = 0, m = 0 }, -- giros desde o ultimo Lendario+ / Mitico+
		giros = 0,               -- giros totais (o primeiro e garantido Raro+ e gratis)
		index = { pets = {}, hats = {} },
		daily = { dia = 1, ultimo = 0 },  -- ultimo = numero do dia UTC do ultimo resgate
		boosts = { sorte = 0, moedas = 0 }, -- os.time() em que cada boost termina
		recibos = {},            -- [PurchaseId] = os.time() (compras ja entregues)
		compras = {},            -- [chaveProduto] = quantidade
		cosmeticos = {},
		tel = {},                -- marcos de telemetria ja registrados (FirstOreMined etc.)
		exp = {},                -- atribuicoes do ExperimentService
		tempoJogado = 0,         -- segundos
		criadoEm = os.time(),
	}
end

-- cria um hat novo no inventario e devolve o uid
function PlayerData.novoHat(perfil, id, nivel)
	perfil.hatSeq = (perfil.hatSeq or 0) + 1
	local uid = "h" .. perfil.hatSeq
	perfil.hatsInv[uid] = { id = id, nivel = nivel or 1, xp = 0, xpTotal = 0 }
	perfil.index.hats[id] = true
	return uid
end

-- cria um pet novo no inventario e devolve o uid
function PlayerData.novoPet(perfil, id, nivel)
	perfil.petSeq = (perfil.petSeq or 0) + 1
	local uid = "p" .. perfil.petSeq
	perfil.petsInv[uid] = { id = id, nivel = nivel or 1, xp = 0, xpTotal = 0 }
	perfil.index.pets[id] = true
	return uid
end

-- XP guardado acima do necessario (save de uma curva antiga: v3.1.1 barateou os niveis de pet)
-- vira nivel pela curva atual. Nunca tira nivel; so resolve a sobra. Devolve true se mudou algo.
local function resolverSobraXp(inst, def, paraSubir, nivelMax)
	inst.xp = math.max(0, tonumber(inst.xp) or 0)
	local antes = inst.nivel
	while inst.nivel < nivelMax do
		local need = paraSubir(def, inst.nivel)
		if need <= 0 or inst.xp < need then break end
		inst.xp -= need
		inst.nivel += 1
	end
	if inst.nivel >= nivelMax then inst.xp = 0 end
	return inst.nivel ~= antes
end

local function normalizar(p)
	local novo = perfilNovo()
	for k, v in pairs(novo) do
		if p[k] == nil then p[k] = v end
	end
	p.audio = AudioPreferences.sanitize(p.audio)
	p.index.pets = p.index.pets or {}
	p.index.hats = p.index.hats or {}
	for id in pairs(p.index.hats) do if not Config.hatPorId(id) then p.index.hats[id] = nil end end
	p.pity.l, p.pity.m = p.pity.l or 0, p.pity.m or 0
	p.boosts.sorte, p.boosts.moedas = p.boosts.sorte or 0, p.boosts.moedas or 0
	p.melhorias = nil
	-- saves antigos: toda picareta ate a atual conta como comprada
	local _, iAtual = Config.picaretaPorId(p.picareta)
	if not iAtual then p.picareta = "enferrujada"; iAtual = 1 end
	for i = 1, iAtual do p.picaretasCompradas[Config.Picaretas[i].id] = true end
	if not Config.mochilaPorId(p.mochilaTier) then p.mochilaTier = "saco_pano" end
	-- pets empilhados viram itens separados
	if next(p.pets) then
		local porId = {}
		for id, posse in pairs(p.pets) do
			if Config.petPorId(id) then
				porId[id] = {}
				for k = 1, math.clamp(posse.qtd or 1, 1, 30) do
					local uid = PlayerData.novoPet(p, id, k == 1 and (posse.nivel or 1) or 1)
					local nick = p.apelidos[id]
					if k == 1 and type(nick) == "string" then p.petsInv[uid].apelido = nick end
					table.insert(porId[id], uid)
				end
			end
		end
		local novos = {}
		for _, id in ipairs(p.petsEquipados) do
			local lista = porId[id]
			if lista and #lista > 0 then table.insert(novos, table.remove(lista, 1)) end
		end
		p.petsEquipados = novos
		p.pets, p.apelidos = {}, {}
	end
	if next(p.hats) then
		local porId = {}
		for id, posse in pairs(p.hats) do
			if Config.hatPorId(id) then
				porId[id] = {}
				for _ = 1, math.clamp(posse.qtd or 1, 1, 20) do
					table.insert(porId[id], PlayerData.novoHat(p, id, posse.nivel or 1))
				end
			end
		end
		local novos = {}
		for _, id in ipairs(p.equipados) do
			local lista = porId[id]
			if lista and #lista > 0 then table.insert(novos, table.remove(lista, 1)) end
		end
		p.equipados = novos
		p.hats = {}
	end
	-- itens que sairam do jogo somem; niveis acima do novo maximo sao limitados
	for uid, inst in pairs(p.hatsInv) do
		-- hats provisorios antigos ("chakra_raro") viram o primeiro hat do catalogo com o mesmo tema e raridade
		if not Config.hatPorId(inst.id) and type(inst.id) == "string" then
			local tema, rar = inst.id:match("^(%a+)_(%a+)$")
			local lista = tema and Config.hatsDoTema(tema, rar) or {}
			if #lista > 0 then inst.id = lista[1].id end
		end
		if not Config.hatPorId(inst.id) then p.hatsInv[uid] = nil
		else
			inst.nivel = math.clamp(inst.nivel or 1, 1, Config.HAT_NIVEL_MAX)
			resolverSobraXp(inst, Config.hatPorId(inst.id), Config.hatXpParaSubir, Config.HAT_NIVEL_MAX)
			p.index.hats[inst.id] = true
		end
	end
	for uid, inst in pairs(p.petsInv) do
		if not Config.petPorId(inst.id) then p.petsInv[uid] = nil
		else
			inst.nivel = math.clamp(inst.nivel or 1, 1, Config.PET_NIVEL_MAX)
			resolverSobraXp(inst, Config.petPorId(inst.id), Config.petXpParaSubir, Config.PET_NIVEL_MAX)
			p.index.pets[inst.id] = true
		end
	end
	for i = #p.equipados, 1, -1 do
		if not p.hatsInv[p.equipados[i]] then table.remove(p.equipados, i) end
	end
	for i = #p.petsEquipados, 1, -1 do
		if not p.petsInv[p.petsEquipados[i]] then table.remove(p.petsEquipados, i) end
	end
	-- saves de quando havia mais slots de pet: fica so o limite atual, mantendo os mais fortes
	if #p.petsEquipados > Config.PET_SLOTS_BASE then
		local forca = {}
		for _, uid in ipairs(p.petsEquipados) do
			local inst = p.petsInv[uid]
			forca[uid] = Config.petBonusDano(Config.petPorId(inst.id), inst.nivel)
		end
		table.sort(p.petsEquipados, function(a, b) return forca[a] > forca[b] end)
		for i = #p.petsEquipados, Config.PET_SLOTS_BASE + 1, -1 do table.remove(p.petsEquipados, i) end
	end
	-- recibos antigos (mais de 60 dias) nao precisam mais ficar no save
	local agora = os.time()
	for id, t in pairs(p.recibos) do
		if type(t) ~= "number" or agora - t > 60 * 86400 then p.recibos[id] = nil end
	end
	p.econVersao = Config.ECON_VERSAO
	return p
end

local function chave(player) return "u_" .. player.UserId end

-- carrega travando a sessao: impede que dois servidores escrevam o mesmo save (duplicacao)
function PlayerData.carregar(player)
	local dados, okFinal
	for tentativa = 1, 5 do
		local ok, res = pcall(function()
			return store:UpdateAsync(chave(player), function(atual)
				if type(atual) == "table" and atual.sessao and atual.sessao.id ~= sessaoId
					and os.time() - (atual.sessao.t or 0) < TRAVA_VALIDA and tentativa < 5 then
					return nil -- outra sessao ativa: nao escreve, tenta de novo
				end
				atual = type(atual) == "table" and atual or perfilNovo()
				atual.sessao = { id = sessaoId, t = os.time() }
				return atual
			end)
		end)
		if ok and type(res) == "table" and res.sessao and res.sessao.id == sessaoId then
			dados, okFinal = res, true
			break
		end
		if not ok and not USANDO_MEMORIA then warn("[PlayerData] carregar " .. player.Name .. ": " .. tostring(res)) end
		task.wait(2)
	end
	if not player.Parent then return nil end
	local perfil
	if okFinal then
		perfil = normalizar(dados)
	else
		-- sem conseguir carregar: perfil temporario que NUNCA salva (nao sobrescreve o save real)
		perfil = perfilNovo()
		perfil.__semSalvar = true
		warn("[PlayerData] nao foi possivel carregar " .. player.Name .. "; perfil temporario sem salvar")
	end
	perfil.__entrouEm = os.clock()
	perfil.__player = player
	cache[player] = perfil
	AudioPreferences.apply(player, perfil.audio)
	return perfil
end

function PlayerData.get(player) return cache[player] end

function PlayerData.audioPersistente(perfil)
	return not USANDO_MEMORIA and not perfil.__semSalvar and not (perfil.__dev and not perfil.__devSalvar)
end

function PlayerData.atualizarAudio(player, patch)
	local perfil = cache[player]
	if not perfil then return { ok = false, carregando = true } end
	if type(patch) ~= "table" then return { ok = false } end
	-- Bounded whitelist traversal; nested values and unknown fields never enter the save.
	perfil.audio = AudioPreferences.sanitize(patch, perfil.audio)
	-- Client owns immediate mix attributes; server replication would roll back newer local edits.
	return { ok = true, audio = table.clone(perfil.audio), persistent = PlayerData.audioPersistente(perfil) }
end

-- perfil zerado (testes no Studio)
function PlayerData.carregarVazio() return normalizar(perfilNovo()) end

local function copiaParaSalvar(perfil, liberar)
	local t = {}
	for k, v in pairs(perfil) do
		if type(k) ~= "string" or k:sub(1, 2) ~= "__" then t[k] = v end
	end
	t.sessao = not liberar and { id = sessaoId, t = os.time() } or nil
	return t
end

-- salvar com UpdateAsync: so grava se a trava ainda for desta sessao
function PlayerData.salvar(player, liberar)
	local perfil = cache[player]
	if not perfil then return false end
	if perfil.__semSalvar then return false end
	if perfil.__dev and not perfil.__devSalvar then return false end
	if perfil.__entrouEm then
		perfil.tempoJogado = (perfil.tempoJogado or 0) + (os.clock() - perfil.__entrouEm)
		perfil.__entrouEm = os.clock()
	end
	local dados = copiaParaSalvar(perfil, liberar)
	local ok, err = pcall(function()
		store:UpdateAsync(chave(player), function(atual)
			if type(atual) == "table" and atual.sessao and atual.sessao.id ~= sessaoId then
				return nil -- outra sessao assumiu o save: nao sobrescreve
			end
			return dados
		end)
	end)
	if not ok and not USANDO_MEMORIA then
		warn("[PlayerData] falha ao salvar " .. player.Name .. ": " .. tostring(err))
	end
	return ok
end

function PlayerData.descarregar(player)
	PlayerData.salvar(player, true)
	cache[player] = nil
end

-- ---------- STATS ----------
local function maiorArea(perfil)
	local m = 1
	for id in pairs(perfil.areas) do if type(id) == "number" and id > m then m = id end end
	return m
end
PlayerData.maiorArea = maiorArea

function PlayerData.bonusHats(perfil)
	local dano = 0
	for _, uid in ipairs(perfil.equipados) do
		local posse = perfil.hatsInv[uid]
		local def = posse and Config.hatPorId(posse.id)
		if def then dano += Config.hatDanoNoNivel(def.dano, posse.nivel or 1) end
	end
	return dano, { capacidade = 0, sorte = 0, valor = 0 }
end

-- dano = (base + soma dos hats) x multiplicador da picareta x (1 + bonus % dos pets)
function PlayerData.dano(perfil)
	local pic = Config.picaretaPorId(perfil.picareta)
	local danoHats = PlayerData.bonusHats(perfil)
	local bonusDano = PlayerData.bonusPets(perfil)
	return (Config.DANO_BASE + danoHats) * (pic and pic.mult or 1) * (1 + bonusDano)
end

function PlayerData.intervalo(perfil)
	local pic = Config.picaretaPorId(perfil.picareta)
	return pic and pic.intervalo or Config.COOLDOWN_GOLPE
end

function PlayerData.capacidade(perfil)
	local moc = Config.mochilaPorId(perfil.mochilaTier)
	return moc and moc.capacidade or Config.Mochilas[1].capacidade
end

-- ---------- PETS ----------
function PlayerData.bonusPets(perfil)
	local dano = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local posse = perfil.petsInv[uid]
		local def = posse and Config.petPorId(posse.id)
		if def then dano += Config.petBonusDano(def, posse.nivel) end
	end
	return dano, 0
end

function PlayerData.levelBonus(perfil)
	local lb = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local posse = perfil.petsInv[uid]
		local def = posse and Config.petPorId(posse.id)
		if def then lb += Config.petLevelBonus(def) end
	end
	return lb
end

function PlayerData.velPets(perfil)
	local v = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local inst = perfil.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		if def then v += Config.petVelocidade(def, inst.nivel) end
	end
	return math.min(v, Config.VELOCIDADE_PETS_MAX)
end

function PlayerData.velocidade(perfil)
	return Config.VELOCIDADE_BASE + PlayerData.velPets(perfil)
end

function PlayerData.slotsPets() return Config.PET_SLOTS_BASE end

function PlayerData.totalPets(perfil)
	local n = 0
	for _ in pairs(perfil.petsInv) do n += 1 end
	return n
end

-- passes que dependem do jogador: PlayerData recebe o player guardado no perfil
local function temPasse(perfil, nome)
	return perfil.__player and Passes.possui(perfil.__player, nome) or false
end

function PlayerData.capacidadePets(perfil)
	return Config.capacidadePets() + (temPasse(perfil, "Inventario") and 50 or 0)
end

function PlayerData.petsResumo(perfil)
	local t = {}
	for _, inst in pairs(perfil.petsInv) do
		local r = t[inst.id] or { qtd = 0, nivel = 1, xp = 0 }
		r.qtd += 1
		r.nivel = math.max(r.nivel, inst.nivel)
		t[inst.id] = r
	end
	return t
end

function PlayerData.slots(perfil)
	return Config.slotsHat(maiorArea(perfil)) + (temPasse(perfil, "HatSlot") and 1 or 0)
end

function PlayerData.capacidadeHats(perfil)
	return Config.capacidadeHats() + (temPasse(perfil, "Inventario") and 50 or 0)
end

function PlayerData.hatsResumo(perfil)
	local t = {}
	for _, h in pairs(perfil.hatsInv) do
		local r = t[h.id] or { qtd = 0, nivel = 1 }
		r.qtd += 1
		r.nivel = math.max(r.nivel, h.nivel)
		t[h.id] = r
	end
	return t
end

function PlayerData.totalHats(perfil)
	local n = 0
	for _ in pairs(perfil.hatsInv) do n += 1 end
	return n
end

function PlayerData.itensNaMochila(perfil)
	local t = 0
	for id, q in pairs(perfil.mochila) do t += q * Config.espacoMinerio(id) end
	return t
end

function PlayerData.qtdMinerios(perfil)
	local t = 0
	for _, q in pairs(perfil.mochila) do t += q end
	return t
end

function PlayerData.mochilaCheia(perfil, idMinerio)
	local extra = idMinerio and Config.espacoMinerio(idMinerio) or 1
	return PlayerData.itensNaMochila(perfil) + extra > PlayerData.capacidade(perfil)
end

function PlayerData.progredirMissao(perfil, areaId, tipo, qtd)
	local lista = Config.Missoes[areaId]
	if not lista or not perfil.areas[areaId] then return end
	for _, m in ipairs(lista) do
		if m.tipo == tipo then
			local e = perfil.missoes[m.id] or { p = 0, r = false }
			e.p = math.min(m.meta, e.p + (qtd or 1))
			perfil.missoes[m.id] = e
		end
	end
end

-- ---------- BOOSTS ----------
function PlayerData.boostAtivo(perfil, tipo)
	return (perfil.boosts[tipo] or 0) > os.time()
end
-- boosts do mesmo tipo somam TEMPO, nunca multiplicador
function PlayerData.adicionarBoost(perfil, tipo, minutos)
	local agora = os.time()
	perfil.boosts[tipo] = math.max(perfil.boosts[tipo] or 0, agora) + math.floor(minutos * 60)
end

function PlayerData.diaUTC(t) return math.floor((t or os.time()) / 86400) end

function PlayerData.snapshot(perfil)
	local danoHats = PlayerData.bonusHats(perfil)
	local bonusDanoPets = PlayerData.bonusPets(perfil)
	local agora = os.time()
	return {
		audio = AudioPreferences.sanitize(perfil.audio),
		audioPersistent = PlayerData.audioPersistente(perfil),
		econVersao = Config.ECON_VERSAO,
		petsInv = perfil.petsInv,
		pets = PlayerData.petsResumo(perfil),
		petsEquipados = perfil.petsEquipados,
		capacidadePets = PlayerData.capacidadePets(perfil),
		picaretasCompradas = perfil.picaretasCompradas,
		missoes = perfil.missoes,
		bonusDanoPets = bonusDanoPets,
		bonusMoedaPets = 0,
		levelBonus = PlayerData.levelBonus(perfil),
		slotsPets = PlayerData.slotsPets(perfil),
		totalPets = PlayerData.totalPets(perfil),
		velocidade = PlayerData.velocidade(perfil),
		velPets = PlayerData.velPets(perfil),
		velPetsMax = Config.VELOCIDADE_PETS_MAX,
		moeda = perfil.moeda,
		picareta = perfil.picareta,
		intervalo = PlayerData.intervalo(perfil),
		mochilaTier = perfil.mochilaTier,
		mochila = perfil.mochila,
		hatsInv = perfil.hatsInv,
		hats = PlayerData.hatsResumo(perfil),
		equipados = perfil.equipados,
		areas = perfil.areas,
		dano = PlayerData.dano(perfil),
		danoHats = danoHats,
		capacidade = PlayerData.capacidade(perfil),
		carregado = PlayerData.itensNaMochila(perfil),
		slots = PlayerData.slots(perfil),
		totalHats = PlayerData.totalHats(perfil),
		capacidadeHats = PlayerData.capacidadeHats(perfil),
		qtdMinerios = PlayerData.qtdMinerios(perfil),
		bonusValor = 0,
		bonusSorte = 0,
		pity = perfil.pity,
		giros = perfil.giros,
		giroGratis = (perfil.giros or 0) == 0,
		index = perfil.index,
		daily = { dia = perfil.daily.dia, disponivel = PlayerData.diaUTC() > (perfil.daily.ultimo or 0) },
		boosts = { sorte = math.max(0, perfil.boosts.sorte - agora), moedas = math.max(0, perfil.boosts.moedas - agora) },
		compras = perfil.compras,
		cosmeticos = perfil.cosmeticos,
		multMoedas = perfil.__multMoedas or 1,
		friendBoost = perfil.__friendBoost or 0,
		luckyMult = perfil.__luckyMult or 1,
	}
end

-- ganchos opcionais (Economia preenche multiplicadores antes do snapshot)
PlayerData.antesDeSincronizar = nil

function PlayerData.sincronizar(player, audioContext)
	local perfil = cache[player]
	if not perfil then return end
	perfil.__player = player
	if PlayerData.antesDeSincronizar then pcall(PlayerData.antesDeSincronizar, player, perfil) end
	local snap = PlayerData.snapshot(perfil)
	-- Transient delivery metadata: never stored in the profile or the DataStore.
	if audioContext == "daily" or audioContext == "code" then snap.audioContext = audioContext end
	snap.passes = Passes.todos(player)
	RS.Remotes.AtualizarDados:FireClient(player, snap)
	local ids, nomes = {}, {}
	for _, uid in ipairs(perfil.petsEquipados) do
		local inst = perfil.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		if def then
			table.insert(ids, inst.id)
			table.insert(nomes, inst.apelido or def.nome)
		end
	end
	player:SetAttribute("PetsApelidos", HttpService:JSONEncode(nomes))
	local ls = player:FindFirstChild("leaderstats")
	if not ls then
		ls = Instance.new("Folder")
		ls.Name = "leaderstats"
		local m = Instance.new("IntValue"); m.Name = "Minérios"; m.Parent = ls
		local c = Instance.new("StringValue"); c.Name = "Moedas"; c.Parent = ls
		ls.Parent = player
	end
	ls["Minérios"].Value = perfil.minerados or 0
	ls.Moedas.Value = Config.formatar(perfil.moeda)
	player:SetAttribute("PetsEquipados", table.concat(ids, ","))
	player:SetAttribute("IntervaloGolpe", PlayerData.intervalo(perfil))
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then hum.WalkSpeed = PlayerData.velocidade(perfil) end
end

return PlayerData

]========],base=[========[local RS = game:GetService("ReplicatedStorage")
local DSS = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Config = require(RS.Config)
local AudioPreferences = require(RS:WaitForChild("AudioPreferences"))
local Passes = require(script.Parent.Passes)

-- ---------- ARMAZENAMENTO ----------
-- O GetDataStore nao bate na API, entao ele passa mesmo com o acesso desligado.
-- Quem falha e a primeira chamada real. Por isso a sondagem abaixo.
local memoria = {}
local storeMemoria = {
	GetAsync = function(_, k) return memoria[k] end,
	SetAsync = function(_, k, v) memoria[k] = v end,
	UpdateAsync = function(_, k, fn)
		local novo = fn(memoria[k])
		if novo ~= nil then memoria[k] = novo end
		return memoria[k]
	end,
}

local store = storeMemoria
local USANDO_MEMORIA = true
local MOTIVO = "nao testado"

do
	local okObter, real = pcall(function()
		return DSS:GetDataStore("MineracaoSim_v2")
	end)
	if okObter and real then
		local okLer, err = pcall(function()
			real:GetAsync("__sonda__")
		end)
		if okLer then
			store = real
			USANDO_MEMORIA = false
			MOTIVO = "ok"
		else
			MOTIVO = tostring(err)
		end
	else
		MOTIVO = tostring(real)
	end
end

if USANDO_MEMORIA then
	local motivoLower = string.lower(MOTIVO)
	if string.find(motivoLower, "studio access", 1, true)
		or string.find(motivoLower, "api services", 1, true)
		or string.find(motivoLower, "studioaccesstoapis", 1, true) then
		warn("[PlayerData] DataStore desligado no Studio. Progresso so nesta sessao.")
		warn("[PlayerData] Pra salvar de verdade: Home > Game Settings > Security > Enable Studio Access to API Services")
	else
		warn("[PlayerData] DataStore indisponivel (" .. MOTIVO .. "). Progresso so nesta sessao.")
	end
else
	print("[PlayerData] DataStore ativo, progresso sera salvo")
end

function PlayerDataUsandoMemoria() return USANDO_MEMORIA end

local PlayerData = {}
local cache = {}
local sessaoId = HttpService:GenerateGUID(false)
local TRAVA_VALIDA = 180 -- segundos: trava de outra sessao mais velha que isso e considerada abandonada

local function perfilNovo()
	return {
		audio = AudioPreferences.sanitize(), -- preferences share the existing profile/autosave
		moeda = 0,
		picareta = "enferrujada",
		mochilaTier = "saco_pano",
		mochila = {},            -- [idMinerio] = quantidade
		hats = {},               -- formato antigo (empilhado), so pra migracao
		hatsInv = {},            -- [uid] = { id, nivel, xp, xpTotal }  cada hat e um item separado
		hatSeq = 0,
		equipados = {},          -- lista de uid (pode ter 2 hats iguais)
		pets = {},               -- formato antigo (empilhado), so pra migracao
		petsInv = {},            -- [uid] = { id, nivel, xp, xpTotal, apelido }
		petSeq = 0,
		petsEquipados = {},      -- lista de uid
		apelidos = {},           -- formato antigo, so pra migracao
		picaretasCompradas = { enferrujada = true },
		missoes = {},            -- [idMissao] = { p = progresso, r = resgatada }
		codigos = {},            -- [CODIGO] = true quando ja resgatado
		minerados = 0,           -- minerios quebrados (placar)
		areas = { [1] = true },
		-- economia v3.1
		econVersao = Config.ECON_VERSAO,
		pity = { l = 0, m = 0 }, -- giros desde o ultimo Lendario+ / Mitico+
		giros = 0,               -- giros totais (o primeiro e garantido Raro+ e gratis)
		index = { pets = {}, hats = {} },
		daily = { dia = 1, ultimo = 0 },  -- ultimo = numero do dia UTC do ultimo resgate
		boosts = { sorte = 0, moedas = 0 }, -- os.time() em que cada boost termina
		recibos = {},            -- [PurchaseId] = os.time() (compras ja entregues)
		compras = {},            -- [chaveProduto] = quantidade
		cosmeticos = {},
		tel = {},                -- marcos de telemetria ja registrados (FirstOreMined etc.)
		exp = {},                -- atribuicoes do ExperimentService
		tempoJogado = 0,         -- segundos
		criadoEm = os.time(),
	}
end

-- cria um hat novo no inventario e devolve o uid
function PlayerData.novoHat(perfil, id, nivel)
	perfil.hatSeq = (perfil.hatSeq or 0) + 1
	local uid = "h" .. perfil.hatSeq
	perfil.hatsInv[uid] = { id = id, nivel = nivel or 1, xp = 0, xpTotal = 0 }
	perfil.index.hats[id] = true
	return uid
end

-- cria um pet novo no inventario e devolve o uid
function PlayerData.novoPet(perfil, id, nivel)
	perfil.petSeq = (perfil.petSeq or 0) + 1
	local uid = "p" .. perfil.petSeq
	perfil.petsInv[uid] = { id = id, nivel = nivel or 1, xp = 0, xpTotal = 0 }
	perfil.index.pets[id] = true
	return uid
end

-- XP guardado acima do necessario (save de uma curva antiga: v3.1.1 barateou os niveis de pet)
-- vira nivel pela curva atual. Nunca tira nivel; so resolve a sobra. Devolve true se mudou algo.
local function resolverSobraXp(inst, def, paraSubir, nivelMax)
	inst.xp = math.max(0, tonumber(inst.xp) or 0)
	local antes = inst.nivel
	while inst.nivel < nivelMax do
		local need = paraSubir(def, inst.nivel)
		if need <= 0 or inst.xp < need then break end
		inst.xp -= need
		inst.nivel += 1
	end
	if inst.nivel >= nivelMax then inst.xp = 0 end
	return inst.nivel ~= antes
end

local function normalizar(p)
	local novo = perfilNovo()
	for k, v in pairs(novo) do
		if p[k] == nil then p[k] = v end
	end
	p.audio = AudioPreferences.sanitize(p.audio)
	p.index.pets = p.index.pets or {}
	p.index.hats = p.index.hats or {}
	for id in pairs(p.index.hats) do if not Config.hatPorId(id) then p.index.hats[id] = nil end end
	p.pity.l, p.pity.m = p.pity.l or 0, p.pity.m or 0
	p.boosts.sorte, p.boosts.moedas = p.boosts.sorte or 0, p.boosts.moedas or 0
	p.melhorias = nil
	-- saves antigos: toda picareta ate a atual conta como comprada
	local _, iAtual = Config.picaretaPorId(p.picareta)
	if not iAtual then p.picareta = "enferrujada"; iAtual = 1 end
	for i = 1, iAtual do p.picaretasCompradas[Config.Picaretas[i].id] = true end
	if not Config.mochilaPorId(p.mochilaTier) then p.mochilaTier = "saco_pano" end
	-- pets empilhados viram itens separados
	if next(p.pets) then
		local porId = {}
		for id, posse in pairs(p.pets) do
			if Config.petPorId(id) then
				porId[id] = {}
				for k = 1, math.clamp(posse.qtd or 1, 1, 30) do
					local uid = PlayerData.novoPet(p, id, k == 1 and (posse.nivel or 1) or 1)
					local nick = p.apelidos[id]
					if k == 1 and type(nick) == "string" then p.petsInv[uid].apelido = nick end
					table.insert(porId[id], uid)
				end
			end
		end
		local novos = {}
		for _, id in ipairs(p.petsEquipados) do
			local lista = porId[id]
			if lista and #lista > 0 then table.insert(novos, table.remove(lista, 1)) end
		end
		p.petsEquipados = novos
		p.pets, p.apelidos = {}, {}
	end
	if next(p.hats) then
		local porId = {}
		for id, posse in pairs(p.hats) do
			if Config.hatPorId(id) then
				porId[id] = {}
				for _ = 1, math.clamp(posse.qtd or 1, 1, 20) do
					table.insert(porId[id], PlayerData.novoHat(p, id, posse.nivel or 1))
				end
			end
		end
		local novos = {}
		for _, id in ipairs(p.equipados) do
			local lista = porId[id]
			if lista and #lista > 0 then table.insert(novos, table.remove(lista, 1)) end
		end
		p.equipados = novos
		p.hats = {}
	end
	-- itens que sairam do jogo somem; niveis acima do novo maximo sao limitados
	for uid, inst in pairs(p.hatsInv) do
		-- hats provisorios antigos ("chakra_raro") viram o primeiro hat do catalogo com o mesmo tema e raridade
		if not Config.hatPorId(inst.id) and type(inst.id) == "string" then
			local tema, rar = inst.id:match("^(%a+)_(%a+)$")
			local lista = tema and Config.hatsDoTema(tema, rar) or {}
			if #lista > 0 then inst.id = lista[1].id end
		end
		if not Config.hatPorId(inst.id) then p.hatsInv[uid] = nil
		else
			inst.nivel = math.clamp(inst.nivel or 1, 1, Config.HAT_NIVEL_MAX)
			resolverSobraXp(inst, Config.hatPorId(inst.id), Config.hatXpParaSubir, Config.HAT_NIVEL_MAX)
			p.index.hats[inst.id] = true
		end
	end
	for uid, inst in pairs(p.petsInv) do
		if not Config.petPorId(inst.id) then p.petsInv[uid] = nil
		else
			inst.nivel = math.clamp(inst.nivel or 1, 1, Config.PET_NIVEL_MAX)
			resolverSobraXp(inst, Config.petPorId(inst.id), Config.petXpParaSubir, Config.PET_NIVEL_MAX)
			p.index.pets[inst.id] = true
		end
	end
	for i = #p.equipados, 1, -1 do
		if not p.hatsInv[p.equipados[i]] then table.remove(p.equipados, i) end
	end
	for i = #p.petsEquipados, 1, -1 do
		if not p.petsInv[p.petsEquipados[i]] then table.remove(p.petsEquipados, i) end
	end
	-- saves de quando havia mais slots de pet: fica so o limite atual, mantendo os mais fortes
	if #p.petsEquipados > Config.PET_SLOTS_BASE then
		local forca = {}
		for _, uid in ipairs(p.petsEquipados) do
			local inst = p.petsInv[uid]
			forca[uid] = Config.petBonusDano(Config.petPorId(inst.id), inst.nivel)
		end
		table.sort(p.petsEquipados, function(a, b) return forca[a] > forca[b] end)
		for i = #p.petsEquipados, Config.PET_SLOTS_BASE + 1, -1 do table.remove(p.petsEquipados, i) end
	end
	-- recibos antigos (mais de 60 dias) nao precisam mais ficar no save
	local agora = os.time()
	for id, t in pairs(p.recibos) do
		if type(t) ~= "number" or agora - t > 60 * 86400 then p.recibos[id] = nil end
	end
	p.econVersao = Config.ECON_VERSAO
	return p
end

local function chave(player) return "u_" .. player.UserId end

-- carrega travando a sessao: impede que dois servidores escrevam o mesmo save (duplicacao)
function PlayerData.carregar(player)
	local dados, okFinal
	for tentativa = 1, 5 do
		local ok, res = pcall(function()
			return store:UpdateAsync(chave(player), function(atual)
				if type(atual) == "table" and atual.sessao and atual.sessao.id ~= sessaoId
					and os.time() - (atual.sessao.t or 0) < TRAVA_VALIDA and tentativa < 5 then
					return nil -- outra sessao ativa: nao escreve, tenta de novo
				end
				atual = type(atual) == "table" and atual or perfilNovo()
				atual.sessao = { id = sessaoId, t = os.time() }
				return atual
			end)
		end)
		if ok and type(res) == "table" and res.sessao and res.sessao.id == sessaoId then
			dados, okFinal = res, true
			break
		end
		if not ok and not USANDO_MEMORIA then warn("[PlayerData] carregar " .. player.Name .. ": " .. tostring(res)) end
		task.wait(2)
	end
	if not player.Parent then return nil end
	local perfil
	if okFinal then
		perfil = normalizar(dados)
	else
		-- sem conseguir carregar: perfil temporario que NUNCA salva (nao sobrescreve o save real)
		perfil = perfilNovo()
		perfil.__semSalvar = true
		warn("[PlayerData] nao foi possivel carregar " .. player.Name .. "; perfil temporario sem salvar")
	end
	perfil.__entrouEm = os.clock()
	perfil.__player = player
	cache[player] = perfil
	AudioPreferences.apply(player, perfil.audio)
	return perfil
end

function PlayerData.get(player) return cache[player] end

function PlayerData.audioPersistente(perfil)
	return not USANDO_MEMORIA and not perfil.__semSalvar and not (perfil.__dev and not perfil.__devSalvar)
end

function PlayerData.atualizarAudio(player, patch)
	local perfil = cache[player]
	if not perfil then return { ok = false, carregando = true } end
	if type(patch) ~= "table" then return { ok = false } end
	-- Bounded whitelist traversal; nested values and unknown fields never enter the save.
	perfil.audio = AudioPreferences.sanitize(patch, perfil.audio)
	AudioPreferences.apply(player, perfil.audio)
	return { ok = true, audio = table.clone(perfil.audio), persistent = PlayerData.audioPersistente(perfil) }
end

-- perfil zerado (testes no Studio)
function PlayerData.carregarVazio() return normalizar(perfilNovo()) end

local function copiaParaSalvar(perfil, liberar)
	local t = {}
	for k, v in pairs(perfil) do
		if type(k) ~= "string" or k:sub(1, 2) ~= "__" then t[k] = v end
	end
	t.sessao = not liberar and { id = sessaoId, t = os.time() } or nil
	return t
end

-- salvar com UpdateAsync: so grava se a trava ainda for desta sessao
function PlayerData.salvar(player, liberar)
	local perfil = cache[player]
	if not perfil then return false end
	if perfil.__semSalvar then return false end
	if perfil.__dev and not perfil.__devSalvar then return false end
	if perfil.__entrouEm then
		perfil.tempoJogado = (perfil.tempoJogado or 0) + (os.clock() - perfil.__entrouEm)
		perfil.__entrouEm = os.clock()
	end
	local dados = copiaParaSalvar(perfil, liberar)
	local ok, err = pcall(function()
		store:UpdateAsync(chave(player), function(atual)
			if type(atual) == "table" and atual.sessao and atual.sessao.id ~= sessaoId then
				return nil -- outra sessao assumiu o save: nao sobrescreve
			end
			return dados
		end)
	end)
	if not ok and not USANDO_MEMORIA then
		warn("[PlayerData] falha ao salvar " .. player.Name .. ": " .. tostring(err))
	end
	return ok
end

function PlayerData.descarregar(player)
	PlayerData.salvar(player, true)
	cache[player] = nil
end

-- ---------- STATS ----------
local function maiorArea(perfil)
	local m = 1
	for id in pairs(perfil.areas) do if type(id) == "number" and id > m then m = id end end
	return m
end
PlayerData.maiorArea = maiorArea

function PlayerData.bonusHats(perfil)
	local dano = 0
	for _, uid in ipairs(perfil.equipados) do
		local posse = perfil.hatsInv[uid]
		local def = posse and Config.hatPorId(posse.id)
		if def then dano += Config.hatDanoNoNivel(def.dano, posse.nivel or 1) end
	end
	return dano, { capacidade = 0, sorte = 0, valor = 0 }
end

-- dano = (base + soma dos hats) x multiplicador da picareta x (1 + bonus % dos pets)
function PlayerData.dano(perfil)
	local pic = Config.picaretaPorId(perfil.picareta)
	local danoHats = PlayerData.bonusHats(perfil)
	local bonusDano = PlayerData.bonusPets(perfil)
	return (Config.DANO_BASE + danoHats) * (pic and pic.mult or 1) * (1 + bonusDano)
end

function PlayerData.intervalo(perfil)
	local pic = Config.picaretaPorId(perfil.picareta)
	return pic and pic.intervalo or Config.COOLDOWN_GOLPE
end

function PlayerData.capacidade(perfil)
	local moc = Config.mochilaPorId(perfil.mochilaTier)
	return moc and moc.capacidade or Config.Mochilas[1].capacidade
end

-- ---------- PETS ----------
function PlayerData.bonusPets(perfil)
	local dano = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local posse = perfil.petsInv[uid]
		local def = posse and Config.petPorId(posse.id)
		if def then dano += Config.petBonusDano(def, posse.nivel) end
	end
	return dano, 0
end

function PlayerData.levelBonus(perfil)
	local lb = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local posse = perfil.petsInv[uid]
		local def = posse and Config.petPorId(posse.id)
		if def then lb += Config.petLevelBonus(def) end
	end
	return lb
end

function PlayerData.velPets(perfil)
	local v = 0
	for _, uid in ipairs(perfil.petsEquipados) do
		local inst = perfil.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		if def then v += Config.petVelocidade(def, inst.nivel) end
	end
	return math.min(v, Config.VELOCIDADE_PETS_MAX)
end

function PlayerData.velocidade(perfil)
	return Config.VELOCIDADE_BASE + PlayerData.velPets(perfil)
end

function PlayerData.slotsPets() return Config.PET_SLOTS_BASE end

function PlayerData.totalPets(perfil)
	local n = 0
	for _ in pairs(perfil.petsInv) do n += 1 end
	return n
end

-- passes que dependem do jogador: PlayerData recebe o player guardado no perfil
local function temPasse(perfil, nome)
	return perfil.__player and Passes.possui(perfil.__player, nome) or false
end

function PlayerData.capacidadePets(perfil)
	return Config.capacidadePets() + (temPasse(perfil, "Inventario") and 50 or 0)
end

function PlayerData.petsResumo(perfil)
	local t = {}
	for _, inst in pairs(perfil.petsInv) do
		local r = t[inst.id] or { qtd = 0, nivel = 1, xp = 0 }
		r.qtd += 1
		r.nivel = math.max(r.nivel, inst.nivel)
		t[inst.id] = r
	end
	return t
end

function PlayerData.slots(perfil)
	return Config.slotsHat(maiorArea(perfil)) + (temPasse(perfil, "HatSlot") and 1 or 0)
end

function PlayerData.capacidadeHats(perfil)
	return Config.capacidadeHats() + (temPasse(perfil, "Inventario") and 50 or 0)
end

function PlayerData.hatsResumo(perfil)
	local t = {}
	for _, h in pairs(perfil.hatsInv) do
		local r = t[h.id] or { qtd = 0, nivel = 1 }
		r.qtd += 1
		r.nivel = math.max(r.nivel, h.nivel)
		t[h.id] = r
	end
	return t
end

function PlayerData.totalHats(perfil)
	local n = 0
	for _ in pairs(perfil.hatsInv) do n += 1 end
	return n
end

function PlayerData.itensNaMochila(perfil)
	local t = 0
	for id, q in pairs(perfil.mochila) do t += q * Config.espacoMinerio(id) end
	return t
end

function PlayerData.qtdMinerios(perfil)
	local t = 0
	for _, q in pairs(perfil.mochila) do t += q end
	return t
end

function PlayerData.mochilaCheia(perfil, idMinerio)
	local extra = idMinerio and Config.espacoMinerio(idMinerio) or 1
	return PlayerData.itensNaMochila(perfil) + extra > PlayerData.capacidade(perfil)
end

function PlayerData.progredirMissao(perfil, areaId, tipo, qtd)
	local lista = Config.Missoes[areaId]
	if not lista or not perfil.areas[areaId] then return end
	for _, m in ipairs(lista) do
		if m.tipo == tipo then
			local e = perfil.missoes[m.id] or { p = 0, r = false }
			e.p = math.min(m.meta, e.p + (qtd or 1))
			perfil.missoes[m.id] = e
		end
	end
end

-- ---------- BOOSTS ----------
function PlayerData.boostAtivo(perfil, tipo)
	return (perfil.boosts[tipo] or 0) > os.time()
end
-- boosts do mesmo tipo somam TEMPO, nunca multiplicador
function PlayerData.adicionarBoost(perfil, tipo, minutos)
	local agora = os.time()
	perfil.boosts[tipo] = math.max(perfil.boosts[tipo] or 0, agora) + math.floor(minutos * 60)
end

function PlayerData.diaUTC(t) return math.floor((t or os.time()) / 86400) end

function PlayerData.snapshot(perfil)
	local danoHats = PlayerData.bonusHats(perfil)
	local bonusDanoPets = PlayerData.bonusPets(perfil)
	local agora = os.time()
	return {
		audio = AudioPreferences.sanitize(perfil.audio),
		audioPersistent = PlayerData.audioPersistente(perfil),
		econVersao = Config.ECON_VERSAO,
		petsInv = perfil.petsInv,
		pets = PlayerData.petsResumo(perfil),
		petsEquipados = perfil.petsEquipados,
		capacidadePets = PlayerData.capacidadePets(perfil),
		picaretasCompradas = perfil.picaretasCompradas,
		missoes = perfil.missoes,
		bonusDanoPets = bonusDanoPets,
		bonusMoedaPets = 0,
		levelBonus = PlayerData.levelBonus(perfil),
		slotsPets = PlayerData.slotsPets(perfil),
		totalPets = PlayerData.totalPets(perfil),
		velocidade = PlayerData.velocidade(perfil),
		velPets = PlayerData.velPets(perfil),
		velPetsMax = Config.VELOCIDADE_PETS_MAX,
		moeda = perfil.moeda,
		picareta = perfil.picareta,
		intervalo = PlayerData.intervalo(perfil),
		mochilaTier = perfil.mochilaTier,
		mochila = perfil.mochila,
		hatsInv = perfil.hatsInv,
		hats = PlayerData.hatsResumo(perfil),
		equipados = perfil.equipados,
		areas = perfil.areas,
		dano = PlayerData.dano(perfil),
		danoHats = danoHats,
		capacidade = PlayerData.capacidade(perfil),
		carregado = PlayerData.itensNaMochila(perfil),
		slots = PlayerData.slots(perfil),
		totalHats = PlayerData.totalHats(perfil),
		capacidadeHats = PlayerData.capacidadeHats(perfil),
		qtdMinerios = PlayerData.qtdMinerios(perfil),
		bonusValor = 0,
		bonusSorte = 0,
		pity = perfil.pity,
		giros = perfil.giros,
		giroGratis = (perfil.giros or 0) == 0,
		index = perfil.index,
		daily = { dia = perfil.daily.dia, disponivel = PlayerData.diaUTC() > (perfil.daily.ultimo or 0) },
		boosts = { sorte = math.max(0, perfil.boosts.sorte - agora), moedas = math.max(0, perfil.boosts.moedas - agora) },
		compras = perfil.compras,
		cosmeticos = perfil.cosmeticos,
		multMoedas = perfil.__multMoedas or 1,
		friendBoost = perfil.__friendBoost or 0,
		luckyMult = perfil.__luckyMult or 1,
	}
end

-- ganchos opcionais (Economia preenche multiplicadores antes do snapshot)
PlayerData.antesDeSincronizar = nil

function PlayerData.sincronizar(player)
	local perfil = cache[player]
	if not perfil then return end
	perfil.__player = player
	if PlayerData.antesDeSincronizar then pcall(PlayerData.antesDeSincronizar, player, perfil) end
	local snap = PlayerData.snapshot(perfil)
	snap.passes = Passes.todos(player)
	RS.Remotes.AtualizarDados:FireClient(player, snap)
	local ids, nomes = {}, {}
	for _, uid in ipairs(perfil.petsEquipados) do
		local inst = perfil.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		if def then
			table.insert(ids, inst.id)
			table.insert(nomes, inst.apelido or def.nome)
		end
	end
	player:SetAttribute("PetsApelidos", HttpService:JSONEncode(nomes))
	local ls = player:FindFirstChild("leaderstats")
	if not ls then
		ls = Instance.new("Folder")
		ls.Name = "leaderstats"
		local m = Instance.new("IntValue"); m.Name = "Minérios"; m.Parent = ls
		local c = Instance.new("StringValue"); c.Name = "Moedas"; c.Parent = ls
		ls.Parent = player
	end
	ls["Minérios"].Value = perfil.minerados or 0
	ls.Moedas.Value = Config.formatar(perfil.moeda)
	player:SetAttribute("PetsEquipados", table.concat(ids, ","))
	player:SetAttribute("IntervaloGolpe", PlayerData.intervalo(perfil))
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then hum.WalkSpeed = PlayerData.velocidade(perfil) end
end

return PlayerData

]========],edits={}})
table.insert(specs,{name=[========[ServerScriptService.Core.Recompensas]========],source=[========[-- Recompensas: unico lugar que entrega hats, pets e moedas (minerio, chefe, Daily, compras, codigos).
-- Garante as mesmas regras em todo lugar: inventario, Index, Level Bonus, anuncio de item novo e telemetria.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Economia = require(script.Parent.Economia)
local Telemetria = require(script.Parent.Telemetria)
local Ofertas = require(script.Parent.Ofertas)
local HatVisual = require(script.Parent.HatVisual)

local R = {}
local rnd = Random.new()

local function feedback(player, info)
	RS.Remotes.FeedbackMina:FireClient(player, info)
end

-- hats caem com nivel 1 + soma do Level Bonus dos pets equipados (limitado)
function R.nivelDrop(perfil)
	return math.min(Config.HAT_NIVEL_DROP_MAX, 1 + PlayerData.levelBonus(perfil))
end

function R.inventarioHatsCheio(player, perfil)
	if PlayerData.totalHats(perfil) < PlayerData.capacidadeHats(perfil) then return false end
	feedback(player, { tipo = "cheia", texto = "Inventário de hats cheio! Funda hats para liberar espaço." })
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.hat then -- 1 evento por sessao (senao cada drop perdido vira um evento)
		perfil.__invCheio.hat = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "hat", passe = PlayerData.capacidadeHats(perfil) > Config.INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "hat")
	return true
end

function R.inventarioPetsCheio(player, perfil)
	if PlayerData.totalPets(perfil) < PlayerData.capacidadePets(perfil) then return false end
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.pet then
		perfil.__invCheio.pet = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "pet", passe = PlayerData.capacidadePets(perfil) > Config.PET_INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "pet")
	return true
end

function R.darHat(player, perfil, def, origem)
	if not def or R.inventarioHatsCheio(player, perfil) then return nil end
	local novo = not perfil.index.hats[def.id]
	local uid = PlayerData.novoHat(perfil, def.id, R.nivelDrop(perfil))
	-- slot livre: equipa sozinho (o jogador sente o dano subir na hora)
	if #perfil.equipados < PlayerData.slots(perfil) then
		table.insert(perfil.equipados, uid)
		Telemetria.marco(player, perfil, "FirstHatEquipped", { manual = 0 })
		task.defer(HatVisual.aplicar, player)
	end
	feedback(player, { tipo = "hat", id = def.id, texto = def.nome, raridade = def.raridade, novo = novo, nivel = perfil.hatsInv[uid].nivel, audioContext = origem })
	if Config.RAR_INDICE[def.raridade] >= 5 then
		Telemetria.evento(player, perfil, "HatDropped", Config.RAR_INDICE[def.raridade], { raridade = def.raridade, mundo = def.mundo, origem = origem or "" })
	end
	return uid, def -- additive metadata: the exact definition delivered, including fallbacks
end

-- raridade sorteada com a regra do simulador: Lucky/boost exatos em Epico+, depois sorte do tipo de minerio
function R.sortearRaridadeHat(player, perfil, sorteTipo)
	local dist = Config.aplicarLucky(Config.Eco.RAR_DIST, Economia.luckyMult(player, perfil))
	dist = Config.normalizarSorte(dist, sorteTipo)
	return Config.RAR_IDS[Config.sortearIndice(rnd, dist)]
end

function R.darHatAleatorio(player, perfil, tema, sorteTipo, origem)
	local raridade = R.sortearRaridadeHat(player, perfil, sorteTipo)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

function R.darHatDaRaridade(player, perfil, tema, raridade, origem)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

-- pet de uma raridade na area (area sem gacha usa a anterior; raridade sem pet cai para a de baixo)
function R.darPetDaRaridade(player, perfil, areaId, raridade, origem)
	while areaId > 1 and not Config.Gachas[areaId] do areaId -= 1 end
	if R.inventarioPetsCheio(player, perfil) then
		feedback(player, { tipo = "cheia", texto = "Inventário de pets cheio! Alimente pets para liberar espaço." })
		return nil
	end
	local r = Config.RAR_INDICE[raridade] or 1
	local lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	while #lista == 0 and r > 1 do
		r -= 1
		lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	end
	local def = lista[rnd:NextInteger(1, math.max(1, #lista))]
	if not def then return nil end
	local novo = not perfil.index.pets[def.id]
	local uid = PlayerData.novoPet(perfil, def.id, 1)
	if novo and #perfil.petsEquipados < PlayerData.slotsPets(perfil) then
		table.insert(perfil.petsEquipados, uid)
	end
	Telemetria.marco(player, perfil, "FirstPet", { origem = origem or "" })
	return uid, def, novo
end

function R.darMoedas(player, perfil, qtd, tipoTransacao, item)
	qtd = math.floor(qtd)
	if qtd <= 0 then return 0 end
	perfil.moeda += qtd
	Telemetria.economia(player, perfil, true, qtd, tipoTransacao, item)
	return qtd
end

return R

]========],base=[========[-- Recompensas: unico lugar que entrega hats, pets e moedas (minerio, chefe, Daily, compras, codigos).
-- Garante as mesmas regras em todo lugar: inventario, Index, Level Bonus, anuncio de item novo e telemetria.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Economia = require(script.Parent.Economia)
local Telemetria = require(script.Parent.Telemetria)
local Ofertas = require(script.Parent.Ofertas)
local HatVisual = require(script.Parent.HatVisual)

local R = {}
local rnd = Random.new()

local function feedback(player, info)
	RS.Remotes.FeedbackMina:FireClient(player, info)
end

-- hats caem com nivel 1 + soma do Level Bonus dos pets equipados (limitado)
function R.nivelDrop(perfil)
	return math.min(Config.HAT_NIVEL_DROP_MAX, 1 + PlayerData.levelBonus(perfil))
end

function R.inventarioHatsCheio(player, perfil)
	if PlayerData.totalHats(perfil) < PlayerData.capacidadeHats(perfil) then return false end
	feedback(player, { tipo = "cheia", texto = "Inventário de hats cheio! Funda hats para liberar espaço." })
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.hat then -- 1 evento por sessao (senao cada drop perdido vira um evento)
		perfil.__invCheio.hat = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "hat", passe = PlayerData.capacidadeHats(perfil) > Config.INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "hat")
	return true
end

function R.inventarioPetsCheio(player, perfil)
	if PlayerData.totalPets(perfil) < PlayerData.capacidadePets(perfil) then return false end
	perfil.__invCheio = perfil.__invCheio or {}
	if not perfil.__invCheio.pet then
		perfil.__invCheio.pet = true
		Telemetria.evento(player, perfil, "InventoryFull", 1, { tipo = "pet", passe = PlayerData.capacidadePets(perfil) > Config.PET_INVENTARIO_MAX and 1 or 0 })
	end
	Ofertas.inventarioCheio(player, perfil, "pet")
	return true
end

function R.darHat(player, perfil, def, origem)
	if not def or R.inventarioHatsCheio(player, perfil) then return nil end
	local novo = not perfil.index.hats[def.id]
	local uid = PlayerData.novoHat(perfil, def.id, R.nivelDrop(perfil))
	-- slot livre: equipa sozinho (o jogador sente o dano subir na hora)
	if #perfil.equipados < PlayerData.slots(perfil) then
		table.insert(perfil.equipados, uid)
		Telemetria.marco(player, perfil, "FirstHatEquipped", { manual = 0 })
		task.defer(HatVisual.aplicar, player)
	end
	feedback(player, { tipo = "hat", id = def.id, texto = def.nome, raridade = def.raridade, novo = novo, nivel = perfil.hatsInv[uid].nivel })
	if Config.RAR_INDICE[def.raridade] >= 5 then
		Telemetria.evento(player, perfil, "HatDropped", Config.RAR_INDICE[def.raridade], { raridade = def.raridade, mundo = def.mundo, origem = origem or "" })
	end
	return uid
end

-- raridade sorteada com a regra do simulador: Lucky/boost exatos em Epico+, depois sorte do tipo de minerio
function R.sortearRaridadeHat(player, perfil, sorteTipo)
	local dist = Config.aplicarLucky(Config.Eco.RAR_DIST, Economia.luckyMult(player, perfil))
	dist = Config.normalizarSorte(dist, sorteTipo)
	return Config.RAR_IDS[Config.sortearIndice(rnd, dist)]
end

function R.darHatAleatorio(player, perfil, tema, sorteTipo, origem)
	local raridade = R.sortearRaridadeHat(player, perfil, sorteTipo)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

function R.darHatDaRaridade(player, perfil, tema, raridade, origem)
	local lista = Config.hatsDoTema(tema, raridade)
	return R.darHat(player, perfil, lista[rnd:NextInteger(1, math.max(1, #lista))], origem)
end

-- pet de uma raridade na area (area sem gacha usa a anterior; raridade sem pet cai para a de baixo)
function R.darPetDaRaridade(player, perfil, areaId, raridade, origem)
	while areaId > 1 and not Config.Gachas[areaId] do areaId -= 1 end
	if R.inventarioPetsCheio(player, perfil) then
		feedback(player, { tipo = "cheia", texto = "Inventário de pets cheio! Alimente pets para liberar espaço." })
		return nil
	end
	local r = Config.RAR_INDICE[raridade] or 1
	local lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	while #lista == 0 and r > 1 do
		r -= 1
		lista = Config.petsDaRaridade(Config.RAR_IDS[r], areaId)
	end
	local def = lista[rnd:NextInteger(1, math.max(1, #lista))]
	if not def then return nil end
	local novo = not perfil.index.pets[def.id]
	local uid = PlayerData.novoPet(perfil, def.id, 1)
	if novo and #perfil.petsEquipados < PlayerData.slotsPets(perfil) then
		table.insert(perfil.petsEquipados, uid)
	end
	Telemetria.marco(player, perfil, "FirstPet", { origem = origem or "" })
	return uid, def, novo
end

function R.darMoedas(player, perfil, qtd, tipoTransacao, item)
	qtd = math.floor(qtd)
	if qtd <= 0 then return 0 end
	perfil.moeda += qtd
	Telemetria.economia(player, perfil, true, qtd, tipoTransacao, item)
	return qtd
end

return R

]========],edits={}})
table.insert(specs,{name=[========[ServerScriptService.Core.Retencao]========],source=[========[-- Retencao P0: Daily basico (ciclo de 7 dias sem perda) e Index (colecao de pets e hats).
-- Index nao da poder (economia congelada): so marca a colecao e aparece na UI.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)

local Ret = {}
local ocupado = {}

function Ret.resgatarDaily(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if ocupado[player] then return { ok = false, msg = "Aguarde..." } end
	local hoje = PlayerData.diaUTC()
	if (perfil.daily.ultimo or 0) >= hoje then
		return { ok = false, msg = "Volte amanha para a proxima recompensa" }
	end
	ocupado[player] = true
	local dia = math.clamp(perfil.daily.dia or 1, 1, #Config.DAILY)
	local def = Config.DAILY[dia]
	-- marca ANTES de entregar: nenhuma falha no meio permite resgatar duas vezes
	perfil.daily.ultimo = hoje
	perfil.daily.dia = dia % #Config.DAILY + 1
	local area = PlayerData.maiorArea(perfil)
	local tema = Config.Areas[area].tema
	local partes = {}
	local audioReward = { moedas = 0, boost = false }
	local function deliveredRarity(rarity)
		if (Config.RAR_INDICE[rarity] or 0) > (Config.RAR_INDICE[audioReward.raridade] or 0) then audioReward.raridade = rarity end
	end
	for _, item in ipairs(def.itens) do
		if item.tipo == "moedas" then
			-- limite do GDD: Daily + missoes cabem em RENDA_EXTRA (metade para cada) da renda do mundo.
			-- sem isso, 10 min de renda no M1 (mundo de ~15 min) pagaria o portal inteiro.
			local eco = Config.Eco
			local teto = (eco.RENDA_EXTRA - 1) / 2 * eco.MINUTOS_NO_MUNDO_MEDIO[area] * eco.MOEDAS_POR_MINUTO_MEDIO[area]
			local q = Recompensas.darMoedas(player, perfil, math.min(Config.moedasDeMinutos(area, item.minutos), teto), "TimedReward", "daily" .. dia)
			audioReward.moedas += q
			table.insert(partes, Config.formatar(q) .. " moedas")
		elseif item.tipo == "boost" then
			PlayerData.adicionarBoost(perfil, item.boost, item.minutos)
			audioReward.boost = true
			table.insert(partes, (item.boost == "sorte" and "Sorte " or "Moedas x2 ") .. item.minutos .. " min")
		elseif item.tipo == "hats" then
			local dados = 0
			for _ = 1, item.qtd do
				local uid, delivered = Recompensas.darHatDaRaridade(player, perfil, tema, item.raridade, "daily")
				if uid then
					dados += 1
					if delivered then deliveredRarity(delivered.raridade) end
				end
			end
			table.insert(partes, dados .. " hat(s) " .. (Config.Raridades[item.raridade] and Config.Raridades[item.raridade].nome or item.raridade))
		elseif item.tipo == "pet" then
			local _, pdef = Recompensas.darPetDaRaridade(player, perfil, area, item.raridade, "daily")
			if pdef then deliveredRarity(pdef.raridade); table.insert(partes, pdef.nome) end
		end
	end
	Telemetria.evento(player, perfil, "DailyClaimed", dia)
	PlayerData.sincronizar(player, "daily")
	task.spawn(PlayerData.salvar, player)
	ocupado[player] = nil
	return { ok = true, msg = "Dia " .. dia .. ": " .. table.concat(partes, " + "), dia = dia, audioReward = audioReward }
end

-- resumo da colecao por area (para a UI)
function Ret.progressoIndex(perfil)
	local pets, hats = 0, 0
	for _ in pairs(perfil.index.pets) do pets += 1 end
	for _ in pairs(perfil.index.hats) do hats += 1 end
	return { pets = pets, petsTotal = #Config.Pets, hats = hats, hatsTotal = #Config.Hats }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ocupado[p] = nil end)

return Ret

]========],base=[========[-- Retencao P0: Daily basico (ciclo de 7 dias sem perda) e Index (colecao de pets e hats).
-- Index nao da poder (economia congelada): so marca a colecao e aparece na UI.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)

local Ret = {}
local ocupado = {}

function Ret.resgatarDaily(player)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if ocupado[player] then return { ok = false, msg = "Aguarde..." } end
	local hoje = PlayerData.diaUTC()
	if (perfil.daily.ultimo or 0) >= hoje then
		return { ok = false, msg = "Volte amanha para a proxima recompensa" }
	end
	ocupado[player] = true
	local dia = math.clamp(perfil.daily.dia or 1, 1, #Config.DAILY)
	local def = Config.DAILY[dia]
	-- marca ANTES de entregar: nenhuma falha no meio permite resgatar duas vezes
	perfil.daily.ultimo = hoje
	perfil.daily.dia = dia % #Config.DAILY + 1
	local area = PlayerData.maiorArea(perfil)
	local tema = Config.Areas[area].tema
	local partes = {}
	for _, item in ipairs(def.itens) do
		if item.tipo == "moedas" then
			-- limite do GDD: Daily + missoes cabem em RENDA_EXTRA (metade para cada) da renda do mundo.
			-- sem isso, 10 min de renda no M1 (mundo de ~15 min) pagaria o portal inteiro.
			local eco = Config.Eco
			local teto = (eco.RENDA_EXTRA - 1) / 2 * eco.MINUTOS_NO_MUNDO_MEDIO[area] * eco.MOEDAS_POR_MINUTO_MEDIO[area]
			local q = Recompensas.darMoedas(player, perfil, math.min(Config.moedasDeMinutos(area, item.minutos), teto), "TimedReward", "daily" .. dia)
			table.insert(partes, Config.formatar(q) .. " moedas")
		elseif item.tipo == "boost" then
			PlayerData.adicionarBoost(perfil, item.boost, item.minutos)
			table.insert(partes, (item.boost == "sorte" and "Sorte " or "Moedas x2 ") .. item.minutos .. " min")
		elseif item.tipo == "hats" then
			local dados = 0
			for _ = 1, item.qtd do
				if Recompensas.darHatDaRaridade(player, perfil, tema, item.raridade, "daily") then dados += 1 end
			end
			table.insert(partes, dados .. " hat(s) " .. (Config.Raridades[item.raridade] and Config.Raridades[item.raridade].nome or item.raridade))
		elseif item.tipo == "pet" then
			local _, pdef = Recompensas.darPetDaRaridade(player, perfil, area, item.raridade, "daily")
			if pdef then table.insert(partes, pdef.nome) end
		end
	end
	Telemetria.evento(player, perfil, "DailyClaimed", dia)
	PlayerData.sincronizar(player)
	task.spawn(PlayerData.salvar, player)
	ocupado[player] = nil
	return { ok = true, msg = "Dia " .. dia .. ": " .. table.concat(partes, " + "), dia = dia }
end

-- resumo da colecao por area (para a UI)
function Ret.progressoIndex(perfil)
	local pets, hats = 0, 0
	for _ in pairs(perfil.index.pets) do pets += 1 end
	for _ in pairs(perfil.index.hats) do hats += 1 end
	return { pets = pets, petsTotal = #Config.Pets, hats = hats, hatsTotal = #Config.Hats }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ocupado[p] = nil end)

return Ret

]========],edits={}})
table.insert(specs,{name=[========[ServerScriptService.Core.Codigos]========],source=[========[-- CODIGOS: fica no servidor pra ninguem ver a lista pelo cliente.
-- Pra criar um codigo novo, adicione uma linha em CODIGOS (em MAIUSCULO).
--   moeda  = moedas que o jogador ganha
--   pet    = id de um pet de Config.Pets (opcional)
--   hat    = id de um hat de Config.Hats (opcional)
--   ativo  = false pra desligar sem apagar
-- Cada jogador so resgata cada codigo uma vez.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local CODIGOS = {
	LANCAMENTO = { moeda = 100, ativo = true },  -- ~5 min de jogo no inicio
	BEMVINDO   = { moeda = 50, hat = "chakra_106490972825856", ativo = true }, -- Kakashi (raro)
	NARUTO     = { pet = "naruto", ativo = true },
}

local Codigos = {}
local ultimo = {}

function Codigos.resgatar(player, texto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(texto) ~= "string" then return { ok = false } end
	local agora = os.clock()
	if ultimo[player] and agora - ultimo[player] < 1.5 then return { ok = false, msg = "Aguarde um pouco" } end
	ultimo[player] = agora

	local codigo = texto:upper():gsub("%s+", "")
	local c = CODIGOS[codigo]
	if not c or c.ativo == false then return { ok = false, msg = "Codigo invalido ou expirado" } end
	perfil.codigos = perfil.codigos or {}
	if perfil.codigos[codigo] then return { ok = false, msg = "Voce ja usou esse codigo" } end

	local partes = {}
	local audioReward = { moedas = 0, boost = false }
	local function deliveredRarity(rarity)
		if (Config.RAR_INDICE[rarity] or 0) > (Config.RAR_INDICE[audioReward.raridade] or 0) then audioReward.raridade = rarity end
	end
	if c.hat and Config.hatPorId(c.hat) then
		if PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil) then
			return { ok = false, msg = "Inventário de hats cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoHat(perfil, c.hat, 1)
		deliveredRarity(Config.hatPorId(c.hat).raridade)
		table.insert(partes, Config.hatPorId(c.hat).nome)
	end
	if c.pet and Config.petPorId(c.pet) then
		if PlayerData.totalPets(perfil) >= PlayerData.capacidadePets(perfil) then
			return { ok = false, msg = "Inventário de pets cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoPet(perfil, c.pet, 1)
		deliveredRarity(Config.petPorId(c.pet).raridade)
		table.insert(partes, Config.petPorId(c.pet).nome)
	end
	if c.moeda and c.moeda > 0 then
		perfil.moeda += c.moeda
		audioReward.moedas += c.moeda
		table.insert(partes, Config.formatar(c.moeda) .. " moedas")
	end
	perfil.codigos[codigo] = true
	PlayerData.sincronizar(player, "code")
	return { ok = true, msg = "Codigo resgatado: " .. table.concat(partes, " + "), audioReward = audioReward }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ultimo[p] = nil end)

return Codigos

]========],base=[========[-- CODIGOS: fica no servidor pra ninguem ver a lista pelo cliente.
-- Pra criar um codigo novo, adicione uma linha em CODIGOS (em MAIUSCULO).
--   moeda  = moedas que o jogador ganha
--   pet    = id de um pet de Config.Pets (opcional)
--   hat    = id de um hat de Config.Hats (opcional)
--   ativo  = false pra desligar sem apagar
-- Cada jogador so resgata cada codigo uma vez.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local CODIGOS = {
	LANCAMENTO = { moeda = 100, ativo = true },  -- ~5 min de jogo no inicio
	BEMVINDO   = { moeda = 50, hat = "chakra_106490972825856", ativo = true }, -- Kakashi (raro)
	NARUTO     = { pet = "naruto", ativo = true },
}

local Codigos = {}
local ultimo = {}

function Codigos.resgatar(player, texto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(texto) ~= "string" then return { ok = false } end
	local agora = os.clock()
	if ultimo[player] and agora - ultimo[player] < 1.5 then return { ok = false, msg = "Aguarde um pouco" } end
	ultimo[player] = agora

	local codigo = texto:upper():gsub("%s+", "")
	local c = CODIGOS[codigo]
	if not c or c.ativo == false then return { ok = false, msg = "Codigo invalido ou expirado" } end
	perfil.codigos = perfil.codigos or {}
	if perfil.codigos[codigo] then return { ok = false, msg = "Voce ja usou esse codigo" } end

	local partes = {}
	if c.hat and Config.hatPorId(c.hat) then
		if PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil) then
			return { ok = false, msg = "Inventário de hats cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoHat(perfil, c.hat, 1)
		table.insert(partes, Config.hatPorId(c.hat).nome)
	end
	if c.pet and Config.petPorId(c.pet) then
		if PlayerData.totalPets(perfil) >= PlayerData.capacidadePets(perfil) then
			return { ok = false, msg = "Inventário de pets cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoPet(perfil, c.pet, 1)
		table.insert(partes, Config.petPorId(c.pet).nome)
	end
	if c.moeda and c.moeda > 0 then
		perfil.moeda += c.moeda
		table.insert(partes, Config.formatar(c.moeda) .. " moedas")
	end
	perfil.codigos[codigo] = true
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Codigo resgatado: " .. table.concat(partes, " + ") }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ultimo[p] = nil end)

return Codigos

]========],edits={}})
table.insert(specs,{name=[========[StarterPlayer.StarterPlayerScripts.ExpeditionClient]========],source=[========[-- ============================================================================
-- EXPEDITION CLIENT · UI V2
-- HUD, janelas, popups, confirmações e o fluxo de recompensas do jogo.
-- Visual e componentes: ReplicatedStorage.ExpeditionUI (Theme, Notify, Menus, Inventory).
-- A lógica de jogo continua no servidor; este script só chama os mesmos Remotes.
-- ============================================================================
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Input = game:GetService("UserInputService")
local Lighting = game:GetService("Lighting")
local player = Players.LocalPlayer
local pg = player:WaitForChild("PlayerGui")
local R = RS:WaitForChild("Remotes")
local Config = require(RS:WaitForChild("Config"))
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local Som = require(RS:WaitForChild("SomJogo"))
local AudioPreferences = require(RS:WaitForChild("AudioPreferences"))
local modules = RS:WaitForChild("ExpeditionUI")
local T = require(modules.Theme)
local Notify = require(modules.Notify)
local Inventory = require(modules.Inventory)
local Menus = require(modules.Menus)
local P, C = T.P, T.C
local WHITE = Color3.new(1, 1, 1)

local BASE_W, BASE_H = 1440, 850
local GuiService=game:GetService("GuiService")
local function usingGamepad() return Input:GetLastInputType().Name:find("Gamepad")~=nil end
local oldScreen=pg:FindFirstChild("ExpeditionUI")
if oldScreen then oldScreen:Destroy() end
local screen = T.new("ScreenGui", { Name = "ExpeditionUI", ResetOnSpawn = false, DisplayOrder = 25, IgnoreGuiInset = false, ClipToDeviceSafeArea = true,
	ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, pg)
local canvas = T.frame(screen, "Canvas", 0, 0, BASE_W, BASE_H, nil, 1)
local scale = T.new("UIScale", { Scale = 1 }, canvas)
local hud = T.frame(canvas, "HUD", 0, 0, BASE_W, BASE_H, nil, 1)
local dim = T.new("TextButton", { Name = "ModalBackdrop", Text = "", Size = UDim2.fromScale(1, 1), BackgroundColor3 = P.bg0,
	BackgroundTransparency = .45, BorderSizePixel = 0, AutoButtonColor = false, Visible = false, ZIndex = 20, Active = true }, canvas)
local modalLayer = T.frame(canvas, "ModalLayer", 0, 0, BASE_W, BASE_H, nil, 1)
modalLayer.ZIndex = 21
local toastLayer = T.frame(canvas, "Notifications", 0, 0, BASE_W, BASE_H, nil, 1)
toastLayer.ZIndex = 70
local popupLayer = T.frame(canvas, "PopupLayer", 0, 0, BASE_W, BASE_H, nil, 1)
popupLayer.ZIndex = 90
local dialogHost = T.frame(popupLayer, "Dialogs", 0, 0, BASE_W, BASE_H, nil, 1)
local tipLayer = T.frame(canvas, "TooltipLayer", 0, 0, BASE_W, BASE_H, nil, 1)
tipLayer.ZIndex = 120
local blur = T.new("BlurEffect", { Name = "ExpeditionMenuBlur", Size = 0 }, Lighting)

local ctx = { data = nil, page = nil, collection = "pet", selected = nil, search = "", rarity = nil, ownedOnly = true, favorites = {},
	areaFavorites = {}, storeTab = "Picaretas", eventsTab = "Diario", bannerArea = 1, inventoryScroll = {}, scrollMemory = {},
	portrait = false, compact = false, summonBusy = false }
local virtualW, virtualH = BASE_W, BASE_H
local window, body, searchBox
local bodyW, bodyH = 0, 0
local actionBusy = {}
local pushVersion, hydrated, modalVersion = 0, false, 0
local pendingRefresh, lastInventorySignature = false, ""
local drawWindow, drawHeader, drawBody, drawHUD, updateHUD
local closePopup
local hudRefs = {}
local popupOpen = false
local popupOnClose=nil
local popupFocus=nil
local popupState=nil
local pendingOffer=nil
local alive=true
local connections={}
local function connect(signal,fn) local c=signal:Connect(fn);table.insert(connections,c);return c end
screen:SetAttribute("OpenPage","")
screen:SetAttribute("PopupOpen",false)
ctx.T, ctx.Notify = T, Notify

-- Apply locally at once; coalesce rapid +/- presses into a small profile patch.
-- Only the audio whitelist is persisted. Other visual preferences remain session-local.
local pendingAudio, failedAudio, audioWorker = {}, {}, false
local audioHydrated = false
ctx.audioSaveStatus = "loading"
for key, default in pairs(AudioPreferences.defaults) do
	if AudioPreferences.value(key, player:GetAttribute(key)) == nil then player:SetAttribute(key, default) end
end
local function audioStatus(status)
	ctx.audioSaveStatus = status
	if ctx.audioSettingsStatus then ctx.audioSettingsStatus() end
end
function ctx.setAudioPreference(key, value)
	value = AudioPreferences.value(key, value)
	if value == nil then return end
	player:SetAttribute(key, value)
	for failedKey, failedValue in pairs(failedAudio) do
		if pendingAudio[failedKey] == nil then pendingAudio[failedKey] = failedValue end
	end
	failedAudio = {}
	pendingAudio[key] = value
	audioStatus("pending")
	if audioWorker then return end
	audioWorker = true
	task.spawn(function()
		task.wait(.35)
		while alive and next(pendingAudio) do
			local patch = pendingAudio
			pendingAudio = {}
			local remote = R:FindFirstChild("AtualizarAudioProfile") or R:WaitForChild("AtualizarAudioProfile", 5)
			local ok, result = false, nil
			for attempt = 1, 3 do
				if remote and remote:IsA("RemoteFunction") then
					ok, result = pcall(function() return remote:InvokeServer(patch) end)
				end
				if ok and type(result) == "table" and result.ok then break end
				if attempt < 3 then task.wait(.6) end
			end
			if not alive then break end
			if ok and type(result) == "table" and result.ok then
				local confirmed = AudioPreferences.sanitize(result.audio)
				for key, value in pairs(confirmed) do
					-- A response for an older press must not roll back newer local input.
					if pendingAudio[key] == nil then player:SetAttribute(key, value) end
				end
				ctx.audioPersistent = result.persistent == true
				audioStatus(next(pendingAudio) and "pending" or (ctx.audioPersistent and "profile" or "session"))
			else
				-- Retain failed fields for the next deliberate edit, without a retry loop.
				for key, value in pairs(patch) do
					if pendingAudio[key] == nil then failedAudio[key] = value end
				end
				if next(pendingAudio) then
					for key, value in pairs(failedAudio) do
						if pendingAudio[key] == nil then pendingAudio[key] = value end
					end
					failedAudio = {}
				end
				audioStatus("error")
			end
			task.wait(.35)
		end
		audioWorker = false
	end)
end

T.setTooltipLayer(tipLayer, function() return scale.Scale end)
-- com uma janela aberta o HUD fica atrás do fundo escuro: nada de dica dele aparecendo por cima
T.setTooltipGuard(function(o) return not (ctx.page and o:IsDescendantOf(hud)) end)
Notify.init(toastLayer, popupLayer, function() return virtualW, virtualH end)
Notify.feedAnchor = function() return virtualW - 24, virtualH - (ctx.portrait and 272 or 128) end

-- ---------------------------------------------------------------- PÁGINAS
local PAGE = {
	Store = { title = "Loja", icon = "store", color = P.gold, sub = "Picaretas, mochilas, passes e boosts" },
	Inventory = { title = "Unidades", icon = "units", color = P.accent },
	Areas = { title = "Viajar", icon = "areas", color = P.teal, sub = "Ilhas de mineração e atalhos do lobby" },
	Summon = { title = "Invocar", icon = "summon", color = P.violet },
	Forge = { title = "Forja de Ignis", icon = "forge", color = P.ember, sub = "Venda seus minérios por moedas" },
	Settings = { title = "Configurações", icon = "settings", color = T.Page.Settings, sub = "Som, efeitos e códigos" },
	Quests = { title = "Missões", icon = "quests", color = P.warning },
	Events = { title = "Diário & Index", icon = "events", color = P.pink, sub = "Recompensas diárias e coleção" },
}
ctx.PAGE = PAGE

-- ---------------------------------------------------------------- TOASTS / BLUR
local function kindFor(color)
	if color == C.green then return "success" elseif color == C.red then return "error"
	elseif color == C.orange then return "warning" elseif color == C.gold then return "reward" end
	return "info"
end
function ctx.toast(value, color, kind)
	Notify.push(value, kind or kindFor(color))
end

local function updateBlur()
	local amount = ctx.page and player:GetAttribute("ExpeditionBlurEnabled") ~= false and 6 or 0
	T.tween(blur, .2, { Size = amount }, Enum.EasingStyle.Quad)
end

-- ---------------------------------------------------------------- POPUPS
closePopup = function()
	if not popupOpen then return end
	popupOpen = false
	popupState = nil
	screen:SetAttribute("PopupOpen",false)
	if popupOnClose then local fn=popupOnClose;popupOnClose=nil;pcall(fn) end
	if popupFocus and popupFocus.Parent then GuiService.SelectedObject=popupFocus end
	popupFocus=nil
	local old = dialogHost:GetChildren()
	for _, o in ipairs(old) do
		o.Name = o.Name .. "_Closing"
		if o:IsA("TextButton") then T.tween(o, .1, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad) end
		local sc = o:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .1, { Scale = .94 }, Enum.EasingStyle.Quad) end
	end
	task.delay(.11, function() for _, o in ipairs(old) do o:Destroy() end end)
end
ctx.closePopup = function() closePopup() end

-- A resize renders the same builder/closure again. Stateful selection stays in that
-- closure; text, scroll and focus survive by their stable component names.
local function renderPopup(state, reflow)
	local saved, selectedName = {}, nil
	if state.box and state.box.Parent then
		local selected = GuiService.SelectedObject
		if selected and selected:IsDescendantOf(state.box) then selectedName = selected.Name end
		for _, object in ipairs(state.box:GetDescendants()) do
			if object:IsA("TextBox") then
				table.insert(saved, { name = object.Name, class = "TextBox", text = object.Text,
					focused = object:IsFocused(), cursor = object.CursorPosition, selection = object.SelectionStart })
			elseif object:IsA("ScrollingFrame") then
				table.insert(saved, { name = object.Name, class = "ScrollingFrame", position = object.CanvasPosition })
			end
		end
		state.box:Destroy()
	end
	if state.shield then state.shield:Destroy() end
 if state.shadow then state.shadow:Destroy() end
	T.hideTooltip()
	local opts = state.opts
	local w = math.min(state.width, virtualW - 32)
	local h = math.min(state.height, virtualH - 40)
	local shield = T.new("TextButton", { Name = "PopupBackdrop", Text = "", AutoButtonColor = false, BorderSizePixel = 0,
		BackgroundColor3 = P.bg0, BackgroundTransparency = reflow and .35 or 1, Size = UDim2.fromScale(1, 1) }, dialogHost)
	state.shield = shield
	if not reflow then T.tween(shield, .16, { BackgroundTransparency = .35 }, Enum.EasingStyle.Quad) end
	shield.Activated:Connect(function() if not opts.modal then closePopup() end end)
	local box = T.panel(dialogHost, "Popup", (virtualW - w) / 2, (virtualH - h) / 2, w, h, { bg = P.bg1, radius = 16, strokeColor = P.line, shade = false })
	state.box = box
	box.Active = true
	local shadow = T.shadow(box, 16, 10, .4)
 state.shadow=shadow
	local accent = opts.color or P.accent
	local line = T.frame(box, "Accent", 18, 0, w - 36, 3, accent, 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, line)
	local closeSize = math.max(44, math.ceil(44 / scale.Scale))
	T.text(box, "Title", state.title, 22, 14, w - closeSize - 44, 36, 24, P.text, T.LEFT, "display")
	T.closeButton(box, w - closeSize - 12, 8, closeSize, closePopup)
	local area = T.frame(box, "Content", 20, 64, w - 40, h - 84, nil, 1)
	state.builder(area, w - 40, h - 84, reflow == true)
	for _, value in ipairs(saved) do
		local object = area:FindFirstChild(value.name, true)
		if object and object:IsA(value.class) and value.class == "TextBox" then object.Text = value.text end
	end
	task.defer(function()
		if popupState ~= state or state.box ~= box or not box.Parent then return end
		for _, value in ipairs(saved) do
			local object = area:FindFirstChild(value.name, true)
			if object and object:IsA(value.class) then
				if value.class == "ScrollingFrame" then object.CanvasPosition = value.position
				elseif value.focused then
					object:CaptureFocus(); object.CursorPosition = value.cursor; object.SelectionStart = value.selection
				end
			end
		end
		if usingGamepad() then
			local selected = selectedName and box:FindFirstChild(selectedName, true)
			GuiService.SelectedObject = selected and selected:IsA("GuiButton") and selected or box:FindFirstChildWhichIsA("GuiButton", true)
		end
	end)
	if not reflow then
		T.enter(box, .97, .18)
		T.enter(shadow, .97, .18)
		T.som("ui_popup")
	end
	return box
end

function ctx.popup(title, builder, w, h, opts)
	opts = opts or {}
	closePopup()
	popupOpen = true
	screen:SetAttribute("PopupOpen", true)
	popupOnClose = opts.onClose
	popupFocus = GuiService.SelectedObject
	popupState = { title = title, builder = builder, width = w or 560, height = h or 420, opts = opts }
	return renderPopup(popupState, false)
end

function ctx.refreshPopup()
	if popupOpen and popupState then renderPopup(popupState, true) end
end

-- confirmação. opts: confirmText, cancelText, tone, cost (moedas), preview(p,w) + previewH, w, h
function ctx.confirm(title, message, callback, opts)
	opts = opts or {}
	local hasCost = opts.cost ~= nil
	local used = false
	ctx.popup(title, function(p, w, h)
		local detailHeight = (opts.preview and (opts.previewH or 0) + 10 or 0) + 80 + (hasCost and 94 or 0)
		local details = T.scroll(p, "ConfirmationDetails", 0, 0, w, h - 66, opts.tone or P.accent)
		local cw = w - 14
		local y = 0
		if opts.preview then opts.preview(details, cw); y = (opts.previewH or 0) + 10 end
		T.para(details, "Prompt", message, 0, y, cw, 64, 18, P.text2, T.CENTER, "body")
		y += 80
		if hasCost then
			local have = ctx.data and ctx.data.moeda or 0
			local row = T.panel(details, "CostRow", 0, y, cw, 58, { bg = P.bg0, radius = 12 })
			T.text(row, "CostLabel", "PREÇO", 16, 0, 120, 58, 14, P.text2, T.LEFT, "title")
			T.icon(row, "coins", cw - 196, 9, 40, 40)
			T.text(row, "Cost", T.format(opts.cost), cw - 152, 0, 136, 58, 26, P.gold, T.RIGHT, "display", 1.4)
			T.text(details, "After", have >= opts.cost and ("Saldo depois da compra: " .. T.format(have - opts.cost)) or ("Faltam " .. T.format(opts.cost - have) .. " moedas"),
				0, y + 64, cw, 24, 14, have >= opts.cost and P.text3 or P.danger, T.CENTER, "body")
		end
		details.CanvasSize = UDim2.fromOffset(0, detailHeight)
		local bw = (w - 12) / 2
		T.button(p, "Cancel", opts.cancelText or "Cancelar", 0, h - 52, bw, 52, P.neutral, closePopup, { sound = "ui_cancel" })
		local ok = T.button(p, "Confirm", opts.confirmText or "Confirmar", bw + 12, h - 52, bw, 52, opts.tone or P.success, function()
			if used then return end
			used = true
			closePopup()
			callback()
		end)
		if hasCost and (ctx.data and ctx.data.moeda or 0) < opts.cost then T.setEnabled(ok, false) end
	end, opts.w or 520, opts.h or ((hasCost and 330 or 250) + (opts.previewH and opts.previewH + 10 or 0)), { color = opts.tone })
end

-- ---------------------------------------------------------------- RECOMPENSA VISUAL
-- moedas saem do centro, param um instante e voam para a carteira (o contador sobe quando chegam)
function ctx.coinBurst(amount, sx, sy)
	local wallet = hudRefs.wallet
	if not wallet or not wallet.Parent or not T.motionEnabled() then return end
	sx, sy = sx or virtualW / 2, sy or virtualH * .55
	local tx = wallet.Position.X.Offset + 26
	local ty = wallet.Position.Y.Offset + 27
	local n = math.clamp(math.floor(math.log10(math.max(10, amount or 10)) * 1.6), 5, 14)
	for i = 1, n do
		local c = T.icon(toastLayer, "coins", sx - 20, sy - 20, 40, 40)
		c.ZIndex = 40
		local ang = math.random() * math.pi * 2
		local rad = 50 + math.random() * 90
		T.tween(c, .26, { Position = UDim2.fromOffset(sx - 20 + math.cos(ang) * rad, sy - 20 + math.sin(ang) * rad * .7) }, Enum.EasingStyle.Quad)
		task.delay(.34 + i * .04, function()
			T.tween(c, .44, { Position = UDim2.fromOffset(tx - 15, ty - 15), Size = UDim2.fromOffset(30, 30) }, Enum.EasingStyle.Quint, Enum.EasingDirection.In)
			task.delay(.44, function()
				c:Destroy()
				-- Visual particles do not emit extra coins: the confirmed reward owns its audio.
				if wallet.Parent then T.pop(wallet, 1.05, .16) end
			end)
		end)
	end
end

local function floatDelta(text, col)
	local wallet = hudRefs.wallet
	if not wallet or not wallet.Parent then return end
	local x = wallet.Position.X.Offset
	local y = wallet.Position.Y.Offset + 58
	local w = wallet.Size.X.Offset
	local t = T.text(hud, "CoinDelta", text, x, y, w - 20, 24, 20, col, T.RIGHT, "display", 1.6)
	T.tween(t, .8, { Position = UDim2.fromOffset(x, y + 14), TextTransparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In, .25)
	local st = t:FindFirstChildOfClass("UIStroke")
	if st then T.tween(st, .8, { Transparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In, .25) end
	task.delay(1.1, function() t:Destroy() end)
end

-- ---------------------------------------------------------------- REMOTES
function ctx.invoke(name, ...)
	if name ~= "PedirDados" and not ctx.data then ctx.toast("Carregando seus dados...", nil, "info"); return { ok = false } end
	if actionBusy[name] then return { ok = false, msg = "Aguarde..." } end
	local remote = R:FindFirstChild(name) or R:WaitForChild(name, 3)
	if not remote or not remote:IsA("RemoteFunction") then ctx.toast("Ação indisponível no momento", nil, "error"); return { ok = false } end
	actionBusy[name] = true
	if name == "Vender" then ctx.coinHold = os.clock() + 1.05 end
	local args = table.pack(...)
	local ok, res = pcall(function() return remote:InvokeServer(table.unpack(args, 1, args.n)) end)
	actionBusy[name] = nil
	if not ok then ctx.coinHold = nil; ctx.toast("Falha na conexão. Tente novamente.", nil, "error"); return { ok = false } end
	if name == "PedirDados" then return res end
	if type(res) ~= "table" then ctx.toast("Não foi possível concluir a ação", nil, "error"); return { ok = false } end
	if res.semAcesso then task.defer(function() ctx.accessPopup(res.semAcesso) end) end
	if not res.ok then
		ctx.coinHold = nil
		if name ~= "RolarGacha" then -- a invocacao trata os proprios avisos (cooldown entre giros)
			Som.tocar("ui_erro")
			ctx.toast(res.msg or "Não foi possível concluir a ação", nil, "error")
		end
		return res
	end
	if name == "Vender" then
		Som.venda(res.ganho, res.itens)
		if res.ganho then
			ctx.coinBurst(res.ganho)
			ctx.toast("+" .. T.format(res.ganho) .. " moedas  ·  " .. tostring(res.itens or 0) .. " minérios vendidos", nil, "reward")
		elseif res.msg then ctx.toast(res.msg, nil, "success") end
		return res
	end
	if name == "ComprarArea" then
		Som.tocar("area_nova")
		local a = Config.areaPorId(args[1])
		Notify.banner({ title = "ILHA DESBLOQUEADA!", subtitle = a and a.nome or "", color = P.teal, sound = false, big = true, duration = 2.4 })
	elseif name == "ComprarPicareta" or name == "ComprarMochila" then
		Som.tocar(res.upgradeMax and "upgrade_max" or "upgrade")
		local def = name == "ComprarPicareta" and Config.picaretaPorId(args[1]) or Config.mochilaPorId(args[1])
		Notify.banner({ title = "UPGRADE!", subtitle = def and def.nome or "", color = P.gold, sound = false, duration = 2 })
	elseif name == "AlimentarPet" or name == "FundirHat" then
		local maximum = res.upgradeMax or (name == "AlimentarPet" and res.nivel and res.nivel >= Config.PET_NIVEL_MAX)
		Som.tocar(maximum and "upgrade_max" or (res.levelUp and "level_up" or "forge_success"))
		if res.levelUp and res.nivelAntes and res.nivel then ctx.levelUp(res) end
	elseif name == "EquiparHat" or name == "EquiparPet" or name == "EquiparPicareta" or name == "EquiparMelhores" or name == "EquiparMelhoresPets" then
		Som.tocar(res.equipped == false and "ui_desequipar" or "ui_equipar")
	elseif name == "DesequiparTodos" or name == "DesequiparPets" then
		Som.tocar("ui_desequipar")
	elseif name == "ResgatarMissao" then
		if not ctx.batchQuestAudio then Som.tocar("quest_complete") end
	elseif name == "ResgatarDaily" or name == "ResgatarCodigo" then
		-- One cue for what the server actually delivered; never infer rarity from the offer.
		local reward = res.audioReward
		if type(reward) ~= "table" then Som.tocar("reward_banner") -- compatible with an older server
		elseif type(reward.raridade) == "string" and Config.Raridades[reward.raridade] then Som.drop(reward.raridade)
		elseif reward.boost == true then Som.tocar("boost")
		elseif type(reward.moedas) == "number" and reward.moedas > 0 then Som.tocar("reward_banner") end
	elseif name ~= "RolarGacha" and name ~= "UITravel" and name ~= "ComprarRobux" then
		Som.tocar("ui_confirm")
	end
	if res.msg and name ~= "RolarGacha" then ctx.toast(res.msg, nil, (name:find("Resgatar") or name:find("Comprar")) and "reward" or "success") end
	return res
end

-- fora do lobby: a opção GRÁTIS (teleporte até o Ignis) vem sempre primeiro
function ctx.accessPopup(nome)
	local passe = nome == "AutoSell" and Mon.passe("AutoSell")
	ctx.popup("Ignis está no lobby", function(p, w, h)
		local details = T.scroll(p, "AccessDetails", 0, 0, w, h - 66, P.ember)
		local cw = w - 14
		local art = T.panel(details, "Art", (cw - 120) / 2, 0, 120, 120, { bg = P.bg2, radius = 20, strokeColor = P.ember })
		T.icon(art, "forge", 10, 10, 100, 100)
		T.para(details, "Message", passe and "Venda com o Ignis usando o teleporte grátis, ou deixe o Auto Sell vender sozinho em qualquer ilha."
			or "Compras de equipamento são feitas com o Ignis. O teleporte até ele é grátis.", 0, 132, cw, 100, 18, P.text2, T.CENTER, "body")
		details.CanvasSize = UDim2.fromOffset(0, 240)
		local bw = passe and (w - 12) / 2 or w
		T.button(p, "GoIgnis", "Teleporte grátis", 0, h - 52, bw, 52, P.teal, function() closePopup(); ctx.travel("ignis") end)
		if passe then
			local b = T.button(p, "BuyPass", passe.id > 0 and ("Auto Sell  ·  R$ " .. passe.robux) or "Auto Sell (em breve)", bw + 12, h - 52, bw, 52, P.gold, function()
				if passe.id > 0 then ctx.invoke("ComprarRobux", "AutoSell") end
			end)
			T.setEnabled(b, passe.id > 0)
		end
	end, 560, 400, { color = P.ember })
end

-- ofertas enviadas pelo servidor (Starter no minuto 5, inventário cheio, mochila cheia)
local OFERTA_TEXTO = {
	Starter = { "Starter Pack", "Pack de Moedas M + Moedas x2 (30 min) + Sorte (15 min) + skin Kunai de Ignis.", "Starter", "Agora não", "store" },
	Inventario = { "Inventário cheio", "Funda hats repetidos para liberar espaço (grátis) ou aumente o inventário para 100.", "Inventario", "Fundir hats", "items" },
	AutoSell = { "Mochila cheia", "Teleporte grátis até o Ignis para vender, ou deixe o Auto Sell vender sozinho.", "AutoSell", "Teleporte grátis", "forge" },
}
local function ofertaPopup(oferta)
	local info = OFERTA_TEXTO[oferta]
	if not info then return end
	if ctx.summonBusy or popupOpen or ctx.page or player:GetAttribute("RevealOpen") or player:GetAttribute("TravelTransition") then pendingOffer=oferta;return end
	local item = Mon.passe(info[3]) or Mon.produto(info[3])
	if not item or item.id<=0 then return end
	local fechou = false
	local function fechar(acao)
		if fechou then return end
		fechou = true
		local ev = R:FindFirstChild("OfertaAcao")
		if ev then ev:FireServer("fechada", oferta) end
		closePopup()
		if acao == "Fundir hats" then ctx.collection = "hat"; ctx.open("Inventory")
		elseif acao == "Teleporte grátis" then ctx.travel("ignis") end
	end
	ctx.popup(info[1], function(p, w, h)
		local details = T.scroll(p, "OfferDetails", 0, 0, w, h - 66, P.gold)
		local cw = w - 14
		local narrow = cw < 420
		local heroH = narrow and 238 or 150
		local hero = T.panel(details, "Hero", 0, 0, cw, heroH, { bg = P.bg2, radius = 14, strokeColor = P.gold:Lerp(P.bg2, .4) })
		T.stripes(hero, "Energy", math.max(0, cw - 240), 0, math.min(cw, 240), heroH, P.gold, .93)
		T.icon(hero, info[5], 16, 15, narrow and 72 or 120, narrow and 72 or 120)
		T.text(hero, "Name", item and item.nome or info[1], narrow and 100 or 150, 22, cw - (narrow and 116 or 170), narrow and 58 or 34, 26, P.text, T.LEFT, "display")
		T.para(hero, "Desc", info[2], narrow and 16 or 150, narrow and 100 or 60, narrow and cw - 32 or cw - 170, narrow and 124 or 76, 16, P.text2, T.LEFT, "body")
		local detailsH = heroH + 8
		if item and item.starter and item.valorSeparado then
			T.para(details, "Deal", "Vendido separado: R$ " .. item.valorSeparado .. "   ·   aqui: R$ " .. item.robux, 0, heroH + 12, cw, 40, 14, P.success, T.CENTER)
			detailsH = heroH + 60
		end
		details.CanvasSize = UDim2.fromOffset(0, detailsH)
		local bw = (w - 12) / 2
		T.button(p, "Free", info[4], 0, h - 52, bw, 52, P.neutral, function() fechar(info[4]) end)
		local label = item and (item.id > 0 and (item.nome .. "  ·  R$ " .. item.robux) or (item.nome .. " (em breve)")) or "Loja"
		local buy = T.button(p, "Buy", label, bw + 12, h - 52, bw, 52, P.gold, function()
			if item and item.id > 0 then ctx.invoke("ComprarRobux", item.chave) end
			fechar(nil)
		end)
		if item and item.id <= 0 then T.setEnabled(buy, false) end
	end, 620, 330, { color = P.gold, modal = true })
end
task.spawn(function()
	local ev = R:WaitForChild("OfertaMostrar", 30)
	if ev then connect(ev.OnClientEvent,function(oferta) ofertaPopup(oferta) end) end
end)

-- comprar a próxima área com moedas
function ctx.buyArea(areaId)
	local a = Config.areaPorId(areaId)
	if not a or not ctx.data then return end
	if ctx.data.areas[areaId] then ctx.travel("area", areaId); return end
	local prev = Config.areaPorId(areaId - 1)
	if prev and not ctx.data.areas[prev.id] then ctx.toast("Desbloqueie " .. prev.nome .. " antes", nil, "warning"); return end
	ctx.confirm("Desbloquear ilha", "Nova ilha com minérios, hats e missões próprias.", function()
		local res = ctx.invoke("ComprarArea", areaId)
		if res and res.ok then ctx.refresh() end
	end, {
		cost = a.custo, confirmText = "Desbloquear", tone = P.success, previewH = 120,
		preview = function(p, w)
			local f = T.frame(p, "Scene", 0, 0, w, 120, P.bg0, 0)
			T.corner(f, 12)
			local img = T.image(f, "Image", T.areaImage(a.id), 0, 0, w, 120)
			img.ScaleType = Enum.ScaleType.Crop
			T.corner(img, 12)
			local shade = T.frame(f, "Shade", 0, 0, w, 120, P.bg0, 0)
			T.corner(shade, 12)
			T.fade(shade, 90, .85, .15)
			local tema = Config.Temas[a.tema]
			T.text(f, "Name", a.nome, 16, 70, w - 32, 38, 28, WHITE, T.LEFT, "display", 1.8)
			T.text(f, "Tag", "ILHA " .. a.id .. "  ·  " .. T.upper(tema and tema.nome or ""), 16, 50, w - 32, 20, 13, tema and tema.cor or P.accent, T.LEFT, "title", 1.4)
		end,
	})
end

-- ---------------------------------------------------------------- JANELAS
function ctx.close()
	if not ctx.page then return end
	Som.tocar("ui_fechar")
	ctx.page = nil
	ctx.cancelSummon = true
	modalVersion += 1
	local old = modalLayer:GetChildren()
	for _, o in ipairs(old) do
		local sc = o:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .11, { Scale = .94 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In) end
	end
	task.delay(.11, function() for _, o in ipairs(old) do o:Destroy() end end)
	window, body, searchBox = nil, nil, nil
	T.tween(dim, .14, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad)
	task.delay(.15, function() if not ctx.page then dim.Visible = false end end)
	closePopup()
	T.hideTooltip()
	updateBlur()
	hud.Visible = true
	screen:SetAttribute("OpenPage", "")
	GuiService.SelectedObject=nil
end

function ctx.open(page)
	if player:GetAttribute("RevealOpen") or player:GetAttribute("TravelTransition") or player:GetAttribute("AreaTransition")~=nil then return end
	if page == "Items" then ctx.collection = "hat"; page = "Inventory"
	elseif page == "Play" then page = "Areas" end
	if ctx.page == page then
		if page ~= "Inventory" then ctx.close(); return end
		ctx.search, ctx.rarity, ctx.selected = "", nil, nil
		drawWindow(false)
		return
	end
	if not PAGE[page] then return end
	local wasOpen = ctx.page ~= nil
	ctx.page = page
	ctx.search, ctx.rarity, ctx.selected = "", nil, nil
	if ctx.summonBusy then ctx.cancelSummon = true end
	closePopup()
	T.hideTooltip()
	dim.Visible = true
	if not wasOpen then
		dim.BackgroundTransparency = 1
		T.tween(dim, .18, { BackgroundTransparency = .58 }, Enum.EasingStyle.Quad)
	end
	hud.Visible = not (ctx.portrait or ctx.compact)
	-- o fundo escuro cobre o HUD antes do MouseLeave: devolve os botões ao tamanho normal
	local function resetHudScale()
		if not ctx.page then return end
		for _, o in ipairs(hud:GetDescendants()) do
			if o:IsA("UIScale") and o.Parent:IsA("GuiButton") then o.Scale = 1 end
		end
	end
	resetHudScale()
	task.delay(.3, resetHudScale) -- o "soltar" do clique ainda anima o botão por .24s
	screen:SetAttribute("OpenPage", page)
	Som.tocar(page == "Forge" and "forge_interact" or (wasOpen and "ui_tab" or "ui_abrir"))
	drawWindow(not wasOpen)
	updateBlur()
end

function ctx.refresh()
	if pendingRefresh then return end
	pendingRefresh = true
	task.defer(function()
		pendingRefresh = false
		if ctx.page then drawHeader(); drawBody() end
		updateHUD()
	end)
end
function ctx.redrawBody() drawBody() end
dim.Activated:Connect(function() if popupOpen then closePopup() else ctx.close() end end)

function ctx.travel(action, id, keepMenu)
	if actionBusy.UITravel then return end
	local result = ctx.invoke("UITravel", action, id)
	if result and result.ok then
		if keepMenu then
			ctx.bannerArea = id
			if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end
		else
			ctx.close()
		end
	end
end

-- ---------------------------------------------------------------- INVOCAÇÃO
local function showResults(results, count, playAudio)
	if #results == 0 then return end
	playAudio = playAudio ~= false
	local desiredCols = math.min(#results, ctx.portrait and 2 or 5)
	local width = math.max(460, desiredCols * 170 + (desiredCols - 1) * 12 + 54)
	local height = math.ceil(#results / desiredCols) * 244 + 150
	local best
	for _, r in ipairs(results) do
		local rr = T.rar(r.raridade)
		if not best or rr.ordem > T.rar(best.raridade).ordem then best = r end
	end
	local revealPlayed, rarityPlayed = false, false
	ctx.popup("Invocação concluída", function(p, w, h, reflow)
		local gap = 12
		local available = w - 14
		local cols = math.max(1, math.min(#results, ctx.portrait and 2 or 5, math.floor((available + gap) / 168)))
		local rows = math.ceil(#results / cols)
		local cw = math.min(170, math.floor((available - (cols - 1) * gap) / cols))
		local ch = cw + 62
		local s = T.scroll(p, "Results", 0, 0, w, h - 66, P.violet)
		s.CanvasSize = UDim2.fromOffset(0, rows * (ch + gap))
		local margin = (available - (cols * cw + (cols - 1) * gap)) / 2
		local delay = .1
		for i, result in ipairs(results) do
			local def = Config.petPorId(result.petId)
			local r, key = T.rar(result.raridade)
			local cx = margin + ((i - 1) % cols) * (cw + gap) + cw / 2
			local cy = math.floor((i - 1) / cols) * (ch + gap) + ch / 2 + 2
			local card = T.panel(s, "Result_" .. i, 0, 0, cw, ch, { bg = P.bg2, radius = 14, strokeColor = r.cor, strokeWidth = 2 })
			card.AnchorPoint = Vector2.new(.5, .5)
			card.Position = UDim2.fromOffset(cx, cy)
			card.ClipsDescendants = true
			-- verso: só a cor da raridade (antecipação)
			local back = T.frame(card, "Back", 0, 0, cw, ch, r.cor, 0)
			T.corner(back, 14)
			T.gradient(back, r.cor:Lerp(P.bg0, .45), r.cor:Lerp(P.bg0, .8))
			T.stripes(back, "Energy", 0, 0, cw, ch, WHITE, .9)
			T.text(back, "Mark", "?", 0, 0, cw, ch, 64, r.cor:Lerp(WHITE, .5), T.CENTER, "display", 2)
			local sc = T.new("UIScale", { Scale = .001 }, card)
			local high = r.ordem >= 5
			if high then delay += .35 end
			local thisDelay = delay
			delay += .12
			task.delay(reflow and 0 or thisDelay, function()
				if not card.Parent then return end
				if reflow then sc.Scale = 1 else T.tween(sc, .22, { Scale = 1 }, Enum.EasingStyle.Back) end
				task.delay(reflow and 0 or (high and .45 or .16), function()
					if not card.Parent then return end
					back:Destroy()
					T.rarityFrame(card, key, { animated = r.ordem >= 5 })
					T.preview(card, "pet", result.petId, 8, 10, cw - 16, ch - 82, false)
					local plate = T.frame(card, "Plate", 0, ch - 76, cw, 76, P.bg1, .1)
					T.text(plate, "Name", def and def.nome or result.nome or "", 8, 6, cw - 16, 28, 20, P.text, T.CENTER, "display", 1.4)
					local chip, chw = T.chip(plate, "Rarity", T.upper(r.nome), 0, 40, 26, r.cor, { size = 13 })
					chip.Position = UDim2.fromOffset((cw - chw) / 2, 40)
					if result.novo then
						local nc, nw = T.chip(card, "New", "NOVO!", 0, 8, 24, P.success, { solid = true, size = 13 })
						nc.Position = UDim2.fromOffset(cw - nw - 8, 8)
					end
					if not reflow then T.pop(card, high and 1.18 or 1.08, .3) end
					if playAudio then
						-- One rarity signature for the best item, even for x10 summons.
						if result == best and not rarityPlayed then
							rarityPlayed = true
							Som.drop(result.raridade)
						elseif not revealPlayed and not rarityPlayed then
							revealPlayed = true
							Som.tocar("summon_reveal")
						end
					end
				end)
			end)
		end
		T.button(p, "Continue", "Continuar", 0, h - 54, (w - 12) / 2, 54, P.neutral, closePopup)
		T.button(p, "Again", "Invocar de novo " .. (count > 1 and ("x" .. count) or ""), (w - 12) / 2 + 12, h - 54, (w - 12) / 2, 54, P.violet, function()
			closePopup()
			task.defer(ctx.startSummon, count)
		end)
		if not reflow and best and T.rar(best.raridade).ordem >= 5 then
			local bd = Config.petPorId(best.petId)
			local br = T.rar(best.raridade)
			task.delay(delay + .5, function()
				if not s.Parent or not popupOpen then return end
				Notify.banner({ title = T.upper(br.nome) .. "!", subtitle = bd and bd.nome or "", color = br.cor, sound = false, big = br.ordem >= 6, duration = 2.2 })
			end)
		end
	end, width, height, { color = P.violet })
end

function ctx.showLastSummon()
	if ctx.lastSummonResults then showResults(ctx.lastSummonResults,ctx.lastSummonCount or #ctx.lastSummonResults,false) end
end

function ctx.nearBanner(areaId)
	local a = Config.areaPorId(areaId)
	local machines = workspace:FindFirstChild("Gachas")
	local machine = machines and a and machines:FindFirstChild("Gacha_" .. a.tema)
	if not machine then return false end
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local pad = machine:FindFirstChild("PadGacha")
	local pos = pad and pad.Position or machine:GetPivot().Position
	return (root.Position - pos).Magnitude <= 58
end

function ctx.startSummon(count)
	if ctx.summonBusy or not ctx.data then return end
	local areaId = ctx.bannerArea
	if not ctx.data.areas[areaId] then ctx.toast("Desbloqueie esta ilha primeiro", nil, "warning"); return end
	local cost = Config.Gachas[areaId].custo * (ctx.data.giroGratis and math.max(0, count - 1) or count)
	if ctx.data.moeda < cost then ctx.toast("Moedas insuficientes", nil, "error"); Som.tocar("ui_erro"); return end
	if not ctx.nearBanner(areaId) then
		ctx.toast("Viaje até o banner para invocar", nil, "info")
		return
	end
	ctx.summonBusy = true
	ctx.cancelSummon = false
	local results = {}
	ctx.refresh()
	task.spawn(function()
		for i = 1, count do
			if ctx.cancelSummon then break end
			if ctx.onSummonProgress then pcall(ctx.onSummonProgress, i, count) end
			local result
			for tentativa = 1, 3 do
				result = ctx.invoke("RolarGacha", areaId)
				-- "Calma ai": cooldown do servidor entre giros. Espera e tenta de novo em vez de cortar a sequencia.
				if result and not result.ok and result.msg and result.msg:find("Calma") then task.wait(.35) else break end
			end
			if not result or not result.ok then
				Som.tocar("ui_erro")
				if result and result.msg and not result.msg:find("Calma") then ctx.toast(result.msg, nil, "error") end
				break
			end
			if #results == 0 then Som.tocar("invocar_inicio") end
			table.insert(results, result)
			if i < count then task.wait(.66) end
		end
		ctx.summonBusy = false
		ctx.onSummonProgress = nil
		ctx.refresh()
		ctx.lastSummonResults,ctx.lastSummonCount=results,count
		if ctx.page=="Summon" and not ctx.cancelSummon then showResults(results,count)
		elseif #results>0 then
			local best = results[1]
			for _, result in ipairs(results) do
				if T.rar(result.raridade).ordem > T.rar(best.raridade).ordem then best = result end
			end
			Som.drop(best.raridade)
			ctx.toast(tostring(#results).." unidade(s) recebida(s). Veja o último resultado em Invocar.",nil,"reward")
		end
	end)
end

function ctx.levelUp(res)
	Notify.levelUp(res.nivelAntes, res.nivel)
end

-- ---------------------------------------------------------------- CABEÇALHO / CORPO
local FULLSCREEN = {Inventory=true}
local function fullPage() return FULLSCREEN[ctx.page] and not ctx.portrait and not ctx.compact end
local function scrollKey(name)
	return table.concat({ ctx.page or "", ctx.collection or "", ctx.storeTab or "", tostring(ctx.questArea or ""),
		tostring(ctx.bannerArea or ""), ctx.eventsTab or "", name }, ":")
end

local function pageTitle()
	local info = PAGE[ctx.page] or PAGE.Quests
	local title, icon, col, sub = info.title, info.icon, info.color, info.sub
	local d = ctx.data
	if ctx.page == "Inventory" then
		if ctx.collection == "hat" then title, icon, col = "Itens", "items", P.info end
		if d then
			local total = ctx.collection == "hat" and (d.totalHats or 0) or (d.totalPets or 0)
			local cap = ctx.collection == "hat" and (d.capacidadeHats or 0) or (d.capacidadePets or 0)
			local eq = ctx.collection == "hat" and #(d.equipados or {}) or #(d.petsEquipados or {})
			local slots = ctx.collection == "hat" and d.slots or d.slotsPets
			sub = total .. " / " .. cap .. " no inventário   ·   " .. eq .. " / " .. tostring(slots or "?") .. " equipados"
		end
	elseif ctx.page == "Quests" and d then
		local ready = 0
		for _, lista in pairs(Config.Missoes) do
			for _, m in ipairs(lista) do
				local e = d.missoes and d.missoes[m.id]
				if e and e.p >= m.meta and not e.r and d.areas[m.area] then ready += 1 end
			end
		end
		sub = ready > 0 and (ready .. " missão(ões) pronta(s) para resgatar") or "Complete objetivos em cada ilha"
	elseif ctx.page == "Summon" then
		local a = Config.areaPorId(ctx.bannerArea or 1)
		sub = "Banner  ·  " .. (a and a.nome or "")
	end
	return title, icon, col, sub
end

local function tabsFor()
	if ctx.page == "Inventory" then
		return { { id = "pet", label = "Unidades", icon = "units" }, { id = "hat", label = "Itens", icon = "items" } },
			ctx.collection, ctx.collection == "hat" and P.info or P.accent,
			function(id) ctx.collection = id; ctx.selected = nil; ctx.rarity = nil; ctx.refresh() end
	elseif ctx.page == "Store" then
		return { { id = "Picaretas", label = "Picaretas", icon = "pickaxe" }, { id = "Mochilas", label = "Mochilas", icon = "items" }, { id = "Passes", label = "Passes", icon = "vip" } },
			ctx.storeTab, P.gold, function(id) ctx.storeTab = id; ctx.refresh() end
	elseif ctx.page == "Events" then
		local daily = ctx.data and ctx.data.daily
		return { { id = "Diario", label = "Diário", icon = "gift", badge = daily and daily.disponivel and "!" or nil }, { id = "Index", label = "Index", icon = "units" } },
			ctx.eventsTab, P.pink, function(id) ctx.eventsTab = id; ctx.refresh() end
	end
end

drawHeader = function()
 if not window then return 0 end
 local title,icon,col,sub=pageTitle()
 local full=fullPage()
 local banner=window:FindFirstChild("Banner")
 if banner then
  banner.Title.Text=title
  local mark=banner:FindFirstChild("PageMark"); if mark then mark.BackgroundColor3=col end
  local slab=banner:FindFirstChild("Signature");if slab then slab.BackgroundColor3=col end
 end
 local sl=window:FindFirstChild("Subtitle")
 if sl then sl.Text=sub or (ctx.page=="Inventory" and "Selecione um item para ver detalhes e equipar" or "");sl.Visible=true end
 local tabsRoot=window:FindFirstChild("Tabs");if tabsRoot then tabsRoot:Destroy() end
 local items,current,tcol,onPick=tabsFor()
 if items then
  local ww=window.Size.X.Offset
  local th=(ctx.portrait or ctx.compact) and 60 or 52
  local tx=full and math.max(310,ww*.34) or 24
  local ty=full and 18 or 100
  local tw=full and math.min(660,ww-tx-130) or math.min(ww-48,660)
  tabsRoot=T.frame(window,"Tabs",tx,ty,tw,th,nil,1)
  T.tabs(tabsRoot,"Segment",0,0,tw,th,items,current,tcol or P.accent,onPick)
  return full and 0 or th+12
 end
 return 0
end

drawBody = function()
	if not body or not ctx.page then return end
	for _, d in ipairs(body:GetDescendants()) do
		if d:IsA("ScrollingFrame") then ctx.scrollMemory[scrollKey(d.Name)] = d.CanvasPosition end
	end
	T.clear(body)
	if not ctx.data then
		local ring = T.frame(body, "Spinner", bodyW / 2 - 24, bodyH / 2 - 52, 48, 48, nil, 1)
		T.corner(ring, 24)
		local st = T.stroke(ring, P.accent, 5)
		T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 0), T.kp(.7, 1), T.kp(1, 1) }) }, st)
		local tw = game:GetService("TweenService"):Create(ring, TweenInfo.new(.9, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = 360 })
		tw:Play()
		ring.Destroying:Once(function() tw:Cancel() end)
		T.text(body, "Loading", "Carregando seus dados...", 20, bodyH / 2 + 8, bodyW - 40, 32, 20, P.text2, T.CENTER, "title")
		return
	end
	if ctx.page == "Inventory" then Inventory.render(ctx, body, bodyW, bodyH)
	else Menus.render(ctx, body, bodyW, bodyH) end
	local restore = {}
	for _, d in ipairs(body:GetDescendants()) do
		if d:IsA("ScrollingFrame") then
			local pos = ctx.scrollMemory[scrollKey(d.Name)]
			if pos then restore[d] = pos; d.CanvasPosition = pos end
		end
	end
	if next(restore) then
		task.defer(function() for s, pos in pairs(restore) do if s.Parent then s.CanvasPosition = pos end end end)
	end
end

local function windowRect()
 if fullPage() then return virtualW,virtualH,0,0 end
 if ctx.portrait then
  return virtualW-20,virtualH-32,10,16
 elseif ctx.compact then
  return virtualW-28,virtualH-20,14,10
 end
 local ww=math.min(ctx.page=="Summon" and 1460 or 1280,virtualW-104)
 local wh=math.min(ctx.page=="Summon" and 800 or 780,virtualH-90)
 return ww,wh,(virtualW-ww)/2,(virtualH-wh)/2
end

drawWindow = function(animate)
 if not ctx.page then return end
 modalVersion+=1
 T.clear(modalLayer)
 local ww,wh,wx,wy=windowRect()
 local full=fullPage()
 local _,_,pageColor=pageTitle()
 if ctx.page=="Events" then pageColor=P.warning end
 window=T.panel(modalLayer,"Window",wx,wy,ww,wh,{bg=P.bg0,radius=full and 0 or 12,strokeColor=pageColor,strokeWidth=full and 0 or 3})
 window.Active=true
 local shadow
 if full then
  local inset=GuiService:GetGuiInset().Y/scale.Scale
  T.frame(window,"FullBleedTop",0,-inset,ww,inset+1,P.ink,0)
  window.BackgroundColor3=WHITE
  T.gradient(window,Color3.fromRGB(146,86,214),Color3.fromRGB(56,25,104),90)
  T.texture(window,"halftone",.94,WHITE,44)
  local haze=T.image(window,"StageLight",T.Assets.rays,ww*.30,100,ww*.44,wh-100,P.violet,.88)
  local top=T.frame(window,"TopBand",0,0,ww,92,P.ink,0)
  T.fade(top,90,0,.4)
 else
  shadow=T.shadow(window,12,8,.25)
 end
 local bw=full and math.min(330,ww*.3) or math.min(ww-100,640)
 local banner=T.frame(window,"Banner",24,full and 16 or 14,bw,52,nil,1)
 if not full then
  T.slant(banner,"TitlePlate",-8,0,bw,52,pageColor,{top=pageColor,bottom=pageColor:Lerp(P.ink,.16),tilt=20})
  T.texture(banner,"halftone",.88,P.ink,20)
 else
  local mark=T.frame(banner,"PageMark",3,10,25,25,P.accent,0);mark.Rotation=45
  T.frame(mark,"Facet",3,3,9,18,P.text,.5)
 end
 T.text(banner,"Title","",full and 42 or 24,0,bw-(full and 44 or 48),52,full and 32 or 34,P.text,T.LEFT,"display",3)
 T.text(window,"Subtitle","",24,full and 65 or 72,ww-128,22,15,P.text2,T.LEFT,"body",false)
 local close=T.closeButton(window,ww-78,12,60,ctx.close)
 local extra=drawHeader()
 local headH=full and 108 or 100+extra
 bodyW,bodyH=ww-48,wh-headH-(full and 16 or 22)
 body=T.frame(window,"Body",24,headH,bodyW,bodyH,nil,1)
 hud.Visible=not(full or ctx.portrait or ctx.compact)
 drawBody()
 if animate and not full then T.enter(window,.97,.18);if shadow then T.enter(shadow,.97,.18)end end
 if usingGamepad() then task.defer(function() if window and window.Parent then GuiService.SelectedObject=close end end) end
end

-- ---------------------------------------------------------------- HUD
local NAV = {
 {id="Store",label="Loja",icon="store",tip="Picaretas, mochilas e passes"},
 {id="Inventory",label="Unidades",icon="units",key="H",tip="Unidades e equipe"},
 {id="Items",label="Itens",icon="items",key="J",tip="Hats e atributos"},
 {id="Summon",label="Invocar",icon="summon",key="G",tip="Banners de unidades"},
 {id="Areas",label="Viajar",icon="areas",tip="Ilhas de mineração"},
 {id="Quests",label="Missões",icon="quests",tip="Objetivos e recompensas"},
 {id="Events",label="Diário",icon="events",tip="Recompensa diária e coleção"},
 {id="Settings",label="Ajustes",icon="settings",tip="Som, efeitos e códigos"},
}

drawHUD = function()
 T.clear(hud);hudRefs={}
 local portrait,compact=ctx.portrait,ctx.compact
 screen:SetAttribute("BottomReserved",portrait and 184 or 0)
 local margin=portrait and 16 or 24
 -- Recursos ficam juntos e fora da zona central de mineração.
 local row=T.panel(hud,"Currency",(portrait or compact) and margin or (virtualW-400)/2,14,(portrait or compact) and 340 or 400,60,{bg=P.bg0,alpha=.12,strokeColor=P.line,strokeWidth=2})
 hudRefs.wallet=row
 T.icon(row,"coins",12,12,36,36)
 hudRefs.coins=T.text(row,"Coins",ctx.shownCoins and T.format(ctx.shownCoins) or "0",56,22,150,28,26,P.gold,T.LEFT,"number",2)
 T.text(row,"CoinsLabel","MOEDAS",56,6,130,17,12,P.text3,T.LEFT,"label",false)
 local px=(portrait or compact) and 205 or 236
 T.frame(row,"Rule",px-10,14,1,32,P.lineSoft,0)
 T.statIcon(row,"dano",px,18,28,28)
 hudRefs.power=T.text(row,"Power","0",px+36,24,100,24,22,P.text,T.LEFT,"number",2)
 T.text(row,"PowerLabel","PODER",px+36,7,100,17,12,P.text3,T.LEFT,"label",false)
 T.hint(row,"Poder por golpe · moedas obtidas na venda","below")
 hudRefs.buffs=T.scroll(hud,"Buffs",margin,82,(portrait or compact) and math.min(virtualW-32,620) or 620,36,P.violet)
 hudRefs.buffs.ScrollingDirection=Enum.ScrollingDirection.X
 hudRefs.buffs.ScrollBarThickness=3
 hudRefs.buffKeys=""
 local tw=portrait and math.min(virtualW-32,420) or (compact and math.min(290,virtualW-400) or 360)
 local tx=portrait and margin or virtualW-margin-tw
 local ty=portrait and 126 or 14
 local tracker=T.new("TextButton",{Name="Tracker",Text="",BackgroundColor3=P.bg0,BorderSizePixel=0,Position=UDim2.fromOffset(tx,ty),Size=UDim2.fromOffset(tw,100)},hud)
 T.corner(tracker,8);hudRefs.trackerStroke=T.stroke(tracker,P.lineSoft,1)
 hudRefs.areaName=T.text(tracker,"Area","Praça central",14,10,tw-28,22,15,P.accent,T.LEFT,"label",false)
 hudRefs.questText=T.text(tracker,"Quest","Seu próximo objetivo",14,35,tw-28,23,16,P.text,T.LEFT,"body",false)
 hudRefs.questBar=T.progress(tracker,"QuestBar",14,72,tw-100,5,0,P.accent)
 hudRefs.questCount=T.text(tracker,"Count","",tw-84,63,70,23,13,P.text2,T.RIGHT,"number",false)
 T.bindInteraction(tracker,function() ctx.questArea=nil;ctx.open("Quests") end)
 T.hint(tracker,"Objetivo atual · abrir missões","below")
 -- Navegação única: cada atalho ocupa uma posição estável.
 local cols=portrait and 4 or #NAV
 local nw=portrait and math.floor((virtualW-44)/4) or (compact and 72 or 88)
 local nh=portrait and 60 or 74
 local ng=6
 local rows=math.ceil(#NAV/cols)
 local dw=cols*nw+(cols-1)*ng
 local dh=rows*nh+(rows-1)*ng
 local dock=T.panel(hud,"Navigation",(virtualW-dw)/2,virtualH-dh-14,dw,dh,{bg=P.bg0,stroke=false})
 hudRefs.rail={}
 for i,it in ipairs(NAV) do
  local x=((i-1)%cols)*(nw+ng);local y=math.floor((i-1)/cols)*(nh+ng)
  local b=T.new("TextButton",{Name=it.id,Text="",AutoButtonColor=false,BackgroundColor3=P.bg1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(nw,nh)},dock)
  T.corner(b,8)
  local navColor=T.Page[it.id] or P.violet
  b.BackgroundColor3=WHITE;T.gradient(b,P.bg0,navColor:Lerp(P.ink,.70),90)
  T.texture(b,"pattern",.90,navColor,90)
  local rim=T.stroke(b,navColor,2,0)
  local isz=portrait and 28 or 38
  T.icon(b,it.icon,(nw-isz)/2,5,isz,isz)
  T.text(b,"Label",it.label,4,nh-25,nw-8,22,15,P.text,T.CENTER,"label",1.7)
  T.bindInteraction(b,function()
   if it.id=="Inventory" then ctx.collection="pet" end
   ctx.open(it.id)
  end,{onFocus=function(on) rim.Color=on and P.text or navColor end})
  T.hint(b,it.tip..(it.key and " · ["..it.key.."]" or ""),"above")
  hudRefs.rail[it.id]=b
 end
 local bagW=portrait and virtualW-32 or math.min(600,virtualW*.42)
 local bagY=virtualH-dh-58
 local bagH=(portrait or compact) and 52 or 32
 if bagH>32 then bagY-=20 end
 local bag=T.frame(hud,"Bag",(virtualW-bagW)/2,bagY,bagW,bagH,nil,1)
 hudRefs.bagPanel=bag
 hudRefs.bagTrack=T.progress(bag,"Track",0,0,bagW-102,bagH,0,P.accent)
 hudRefs.bag=T.text(hudRefs.bagTrack,"Count","MOCHILA 0 / 0",10,0,bagW-122,bagH,14,P.text,T.LEFT,"label",false)
 hudRefs.sell=T.button(bag,"SellShortcut","Vender",bagW-94,0,94,bagH,P.neutral,function() ctx.open("Forge") end,{size=14})
 T.hint(hudRefs.sell,"Vender minérios com Ignis","above")
 local slot=(portrait or compact) and 52 or 44
 local hotY=(portrait or compact) and bagY-58 or virtualH-70
 hudRefs.hotbar=T.frame(hud,"Hotbar",margin,hotY,6*slot+5*8,slot,nil,1)
 T.text(hud,"TeamLabel","EQUIPE",margin,hotY-21,130,17,11,P.text3,T.LEFT,"label",false)
 hudRefs.signature=nil
 updateHUD()
end

local function nextPickaxe(d)
	local idx = 1
	for i, p in ipairs(Config.Picaretas) do if p.id == d.picareta then idx = i end end
	for i = idx + 1, #Config.Picaretas do
		local p = Config.Picaretas[i]
		if not (d.picaretasCompradas and d.picaretasCompradas[p.id]) then return p, i end
	end
end
local function nextBackpack(d)
	local idx = 1
	for i, m in ipairs(Config.Mochilas) do if m.id == d.mochilaTier then idx = i end end
	return Config.Mochilas[idx + 1]
end
local function nextArea(d)
	for _, a in ipairs(Config.Areas) do if not d.areas[a.id] then return a end end
end
ctx.nextPickaxe, ctx.nextBackpack, ctx.nextArea = nextPickaxe, nextBackpack, nextArea

local function readyQuests(d, areaId)
	local n = 0
	for _, m in ipairs(Config.Missoes[areaId] or {}) do
		local e = d.missoes and d.missoes[m.id]
		if e and e.p >= m.meta and not e.r then n += 1 end
	end
	return n
end

local function setBadge(target, value, col)
	if not target then return end
	if target:GetAttribute("BadgeValue")==tostring(value or "") then return end
	target:SetAttribute("BadgeValue",tostring(value or ""))
	local old = target:FindFirstChild("Badge")
	if old then old:Destroy() end
	if value and value ~= 0 and value ~= "" then
		local b = T.badge(target, target.Size.X.Offset - 20, -10, value, col)
		T.pop(b, 1.35, .32)
	end
end

local function inventorySignature(d)
	local list = { d.picareta or "", d.mochilaTier or "", table.concat(d.equipados or {}, ","), table.concat(d.petsEquipados or {}, ",") }
	for uid, o in pairs(d.petsInv or {}) do table.insert(list, uid .. ":" .. o.id .. ":" .. o.nivel .. ":" .. tostring(o.xp) .. ":" .. tostring(o.apelido)) end
	for uid, o in pairs(d.hatsInv or {}) do table.insert(list, uid .. ":" .. o.id .. ":" .. o.nivel .. ":" .. tostring(o.xp)) end
	table.sort(list)
	return table.concat(list, "|")
end

local function renderBuffs()
	local root = hudRefs.buffs
	local d = ctx.data
	if not root or not d then return false end
	local elapsed = os.clock() - (ctx.dataClock or os.clock())
	local b = d.boosts or {}
	local list = {}
	local coinsLeft = (b.moedas or 0) - elapsed
	local luckLeft = (b.sorte or 0) - elapsed
	if coinsLeft > 0 then table.insert(list, { "BoostCoins", "x2 MOEDAS  " .. T.clock(coinsLeft), P.gold, "coins", "Moedas x2 nas vendas" }) end
	if luckLeft > 0 then table.insert(list, { "BoostLuck", "SORTE  " .. T.clock(luckLeft), P.success, "potion", "Chance de Épico ou melhor x1,5" }) end
	if (d.friendBoost or 0) > 0 then table.insert(list, { "Friends", "AMIGOS +" .. math.floor(d.friendBoost * 100 + .5) .. "%", P.accent, "gift", "Bônus por amigos ativos no servidor" }) end
	if d.passes and d.passes.VIP then table.insert(list, { "VIP", "VIP", P.gold, "vip", "+10% de moedas nas vendas" }) end
	local keys = {}
	for _, it in ipairs(list) do table.insert(keys, it[1]) end
	local sig = table.concat(keys, ",")
	if sig == hudRefs.buffKeys then
		for _, it in ipairs(list) do
			local chip = root:FindFirstChild(it[1])
			local label = chip and chip:FindFirstChild("Label")
			if label then label.Text = it[2] end
		end
	else
		hudRefs.buffKeys = sig
		T.clear(root)
		local x = 0
		for _, it in ipairs(list) do
			local chip, w = T.chip(root, it[1], it[2], x, 0, 32, it[3], { icon = it[4], size = 15, w = it[1]:find("Boost") and 190 or nil })
			T.hint(chip, it[5], "below")
			x += w + 8
		end
  root.CanvasSize=UDim2.fromOffset(math.max(0,x-8),0)
	end
	return coinsLeft > 0 or luckLeft > 0
end

task.spawn(function()
	while alive and screen.Parent do
		task.wait(1)
		if pendingOffer and not ctx.page and not popupOpen and not ctx.summonBusy then local offer=pendingOffer;pendingOffer=nil;ofertaPopup(offer) end
		if ctx.data and hudRefs.buffs and hudRefs.buffs.Parent then renderBuffs() end
	end
end)

updateHUD = function()
	local d = ctx.data
	if not d or not hudRefs.coins then return end
	local coins = d.moeda or 0
	if ctx.shownCoins == nil then
		hudRefs.coins.Text = T.format(coins)
	elseif coins ~= ctx.shownCoins then
		local from, to = ctx.shownCoins, coins
		local hold = ctx.coinHold and math.max(0, ctx.coinHold - os.clock()) or 0
		task.delay(to > from and hold or 0, function()
			if not hudRefs.coins or not hudRefs.coins.Parent then return end
			T.countTo(hudRefs.coins, from, to, T.format, .55)
			floatDelta((to > from and "+" or "-") .. T.format(math.abs(to - from)), to > from and P.success or P.danger)
			T.pop(hudRefs.coins, to > from and 1.12 or 1.05, .3)
		end)
	end
	ctx.shownCoins = coins
	if hudRefs.power then hudRefs.power.Text = T.format(d.dano or 0) end

	-- mochila
	local frac = math.clamp((d.carregado or 0) / math.max(1, d.capacidade or 1), 0, 1)
	local col = frac >= 1 and P.danger or (frac >= .85 and P.warning or P.accent)
	T.setProgress(hudRefs.bagTrack, frac, col, .35)
	hudRefs.bag.Text = "MOCHILA  " .. T.format(d.carregado or 0) .. " / " .. T.format(d.capacidade or 0)
	local full = frac >= .85
	if hudRefs.sellFull ~= full then
		hudRefs.sellFull = full
		T.setTone(hudRefs.sell, full and P.success or P.neutral)
		if full then T.pop(hudRefs.sell, 1.18, .4) end
	end
	if frac >= 1 and not ctx.bagWasFull then T.shake(hudRefs.bagPanel, 8) end
	ctx.bagWasFull = frac >= 1

	-- ilha + missão em destaque
	local areaId = player:GetAttribute("CurrentAreaId") or 0
	local area = Config.areaPorId(areaId)
	local tema = area and Config.Temas[area.tema]
	hudRefs.areaName.Text = T.upper(area and area.nome or "Praça central")
	hudRefs.areaName.TextColor3 = tema and tema.cor or P.accent
	local questArea = (area and d.areas[area.id]) and area.id or nil
	if not questArea then
		for _, a in ipairs(Config.Areas) do if d.areas[a.id] then questArea = a.id end end
	end
	local shown, ready = nil, false
	for _, m in ipairs(Config.Missoes[questArea or 1] or {}) do
		local e = d.missoes and d.missoes[m.id] or { p = 0, r = false }
		if not e.r then
			if e.p >= m.meta then shown, ready = { m, e }, true; break end
			shown = shown or { m, e }
		end
	end
	hudRefs.trackerReady = ready
	if shown then
		local m, e = shown[1], shown[2]
		hudRefs.questText.Text = ready and "✓ MISSÃO PRONTA — RESGATAR" or m.texto
		hudRefs.questText.TextColor3 = ready and P.success or P.text2
		T.setProgress(hudRefs.questBar, e.p / m.meta, ready and P.success or P.warning, .35)
		hudRefs.questCount.Text = T.format(math.min(e.p, m.meta)) .. " / " .. T.format(m.meta)
		hudRefs.questBar.Visible = true
	else
		hudRefs.questText.Text = "Missões desta ilha concluídas"
		hudRefs.questText.TextColor3 = P.text3
		hudRefs.questBar.Visible = false
	end
	hudRefs.trackerStroke.Color = ready and P.success or P.lineSoft

	-- badges
	local totalReady = 0
	for _, a in ipairs(Config.Areas) do if d.areas[a.id] then totalReady += readyQuests(d, a.id) end end
	setBadge(hudRefs.rail.Quests, totalReady, P.danger)
	setBadge(hudRefs.rail.Events, d.daily and d.daily.disponivel and "!" or nil, P.danger)
	local na = nextArea(d)
	setBadge(hudRefs.rail.Areas, na and d.moeda >= na.custo and "!" or nil, P.success)
	local np = nextPickaxe(d)
	local nb = nextBackpack(d)
	setBadge(hudRefs.rail.Pickaxe, np and d.moeda >= np.custo and "▲" or nil, P.success)
	setBadge(hudRefs.rail.Store, ((np and d.moeda >= np.custo) or (nb and d.moeda >= nb.custo)) and "▲" or nil, P.success)

	-- hotbar + picareta (só quando algo muda)
	local signature = inventorySignature(d) .. "|" .. tostring(np and d.moeda >= np.custo)
	if hudRefs.signature == signature then renderBuffs(); return end
	hudRefs.signature = signature
	renderBuffs()
	if hudRefs.pickArt then
		T.clear(hudRefs.pickArt)
		local size = hudRefs.pickArt.Size.X.Offset
		T.preview(hudRefs.pickArt, "pickaxe", d.picareta, 0, 0, size, size, false)
	end
	local hotbar = hudRefs.hotbar
	T.clear(hotbar)
	local slot = hotbar.Size.Y.Offset
	for i = 1, math.clamp(tonumber(d.slotsPets) or 3,1,6) do
		local uid = d.petsEquipados and d.petsEquipados[i]
		local inst = uid and d.petsInv and d.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		local holder = T.new("TextButton", { Name = "Slot" .. i, Text = "", AutoButtonColor = false, BackgroundTransparency = 1, BorderSizePixel = 0,
			Position = UDim2.fromOffset((i - 1) * (slot + 8), 0), Size = UDim2.fromOffset(slot, slot) }, hotbar)
		if def then
			local tile, r = T.tile(holder, "Tile", 0, 0, slot, slot, def.raridade, { radius = 12 })
			local arte = Config.PetArte and Config.PetArte[def.id]
			if arte then
				local img = T.image(tile, "Portrait", arte.busto or arte.corpo, 3, 3, slot - 6, slot - 6)
				img.ScaleType = Enum.ScaleType.Crop
				T.corner(img, 9)
			else
				T.preview(tile, "pet", def.id, 3, 3, slot - 6, slot - 6, false)
			end
			T.text(tile, "Level", "Lv." .. tostring(inst.nivel or 1), 4, 2, slot - 8, 18, 13, WHITE, T.LEFT, "title")
			T.hint(holder, "<b>" .. ((inst.apelido and inst.apelido ~= "") and inst.apelido or def.nome) .. "</b>  <font color=\"#" .. r.cor:ToHex() .. "\">" .. r.nome .. "</font>\nDano +" .. T.format(math.floor(Config.petBonusDano(def, inst.nivel or 1) * 1000 + .5) / 10) .. "%", "above")
		else
			local empty = T.frame(holder, "Empty", 0, 0, slot, slot, P.bg0, .35)
			T.corner(empty, 12)
			T.stroke(empty, P.lineSoft, 2.5)
			T.text(empty, "Plus", "+", 0, 0, slot, slot, 28, P.text3, T.CENTER, "title")
			T.hint(holder, "Slot livre  ·  equipe uma unidade", "above")
		end
		local sc = T.new("UIScale", {}, holder)
		holder.MouseEnter:Connect(function() T.tween(sc, .14, { Scale = 1.09 }, Enum.EasingStyle.Back) end)
		holder.MouseLeave:Connect(function() T.tween(sc, .12, { Scale = 1 }, Enum.EasingStyle.Quad) end)
		holder.Activated:Connect(function()
			T.som("ui_click")
			ctx.collection = "pet"
			ctx.open("Inventory")
			if uid then ctx.selected = uid; drawBody() end
		end)
	end
end

-- ---------------------------------------------------------------- DADOS
local function barrier(part)
	if not ctx.data or not part:IsA("BasePart") or part.Name ~= "Barreira" then return end
	local id = part:GetAttribute("LiberaComArea")
	local unlocked = id and ctx.data.areas[id] == true
	part.CanCollide = not unlocked
	part.Transparency = unlocked and .9 or .65
end

local function completeCollection(data, kind, definitions)
	local known = data.index and data.index[kind]
	if type(known) ~= "table" or #definitions == 0 then return false end
	for _, definition in ipairs(definitions) do if not known[definition.id] then return false end end
	return true
end

local function acceptData(data)
	if type(data) ~= "table" or type(data.hatsInv) ~= "table" or type(data.petsInv) ~= "table" then return end
	local previous, previousClock = ctx.data, ctx.dataClock
	ctx.data = data
	ctx.dataClock = os.clock()
	if not audioHydrated then
		audioHydrated = true
		local preferences = AudioPreferences.sanitize(data.audio)
		for key, value in pairs(preferences) do
			if pendingAudio[key] == nil and not audioWorker then player:SetAttribute(key, value) end
		end
		ctx.audioPersistent = data.audioPersistent == true
		if not audioWorker then audioStatus(ctx.audioPersistent and "profile" or "session") end
	end
	local transactionAudio = data.audioContext == "daily" or data.audioContext == "code"
	if not transactionAudio and previous and previous.boosts and data.boosts then
		local elapsed = ctx.dataClock - (previousClock or ctx.dataClock)
		for _, key in ipairs({ "sorte", "moedas" }) do
			local before = math.max(0, (previous.boosts[key] or 0) - elapsed)
			if (data.boosts[key] or 0) > before + 5 then Som.tocar("boost"); break end
		end
	end
	hydrated = true
	updateHUD()
	local areas = workspace:FindFirstChild("Areas")
	local areaSig=table.concat((function() local out={} for k,v in pairs(data.areas or {}) do if v then table.insert(out,tostring(k)) end end table.sort(out);return out end)(),",")
	if areas and ctx.areaSignature~=areaSig then ctx.areaSignature=areaSig;for _,d in ipairs(areas:GetDescendants()) do if d.Name=="Barreira" then barrier(d) end end end
	local signature = inventorySignature(data)
	if signature ~= lastInventorySignature then
		if previous then
			local completed = {}
			for _, collection in ipairs({ { "pets", Config.Pets, "Unidades" }, { "hats", Config.Hats, "Hats" } }) do
				if completeCollection(data, collection[1], collection[2]) and not completeCollection(previous, collection[1], collection[2]) then
					table.insert(completed, collection[3])
				end
			end
			if #completed > 0 then
				-- The existing banner queue waits for reveal/menu closure before the milestone cue.
				Notify.banner({ title = "COLEÇÃO COMPLETA!", subtitle = table.concat(completed, " · ") .. " descobertos no Index",
					color = P.gold, sound = not transactionAudio and "achievement" or false, big = true, duration = 2.8 })
			end
		end
		lastInventorySignature = signature
		if ctx.page and not ctx.summonBusy then ctx.refresh() end
	elseif ctx.page == "Forge" or ctx.page == "Quests" or ctx.page == "Events" or ctx.page == "Store" or ctx.page == "Areas" then
		if not ctx.summonBusy then ctx.refresh() end
	end
end
connect(R.AtualizarDados.OnClientEvent,function(data) pushVersion += 1; acceptData(data) end)
connect(workspace.DescendantAdded,function(d) if d.Name == "Barreira" then task.defer(barrier, d) end end)

-- nome do minério da ilha atual (feed de coleta)
local function oreName(variante)
	local a = Config.areaPorId(player:GetAttribute("CurrentAreaId") or 0)
	local info = a and Config.infoMinerio(a.tema .. "_" .. (variante or "comum"))
	return info and info.nome or "Minério"
end

connect(R.FeedbackMina.OnClientEvent,function(info)
	if type(info) ~= "table" then return end
	if info.tipo == "hat" then
		local r = T.rar(info.raridade)
		if info.novo then
			Notify.reveal({ kind = "hat", id = info.id, name = info.texto, rarity = info.raridade, tag = "NOVO HAT!",
				subtitle = "Nível " .. tostring(info.nivel or 1) .. "  ·  entra no Index da coleção" })
		else
			Notify.feed("hat:" .. tostring(info.id), info.texto or "Hat", r.cor, 1, { icon = "items" })
			if r.ordem >= 4 then
				Notify.banner({ title = T.upper(r.nome) .. "!", subtitle = info.texto, color = r.cor, sound = false, big = r.ordem >= 6, duration = 1.8 })
			end
		end
	elseif info.tipo == "quebrou" then
		if info.chefe then
			Notify.banner({ title = "CHEFE DERROTADO!", subtitle = "Recompensa para todos que ajudaram", color = P.danger, big = true, duration = 2.4 })
		else
			local r = T.rar(info.variante)
			Notify.feed("ore:" .. tostring(info.variante), oreName(info.variante), r.cor, 1, { ore = info.variante })
			if r.ordem >= 5 then Notify.banner({ title = "MINÉRIO " .. T.upper(r.nome) .. "!", subtitle = oreName(info.variante), color = r.cor, sound = false, duration = 1.6 }) end
			if hudRefs.bagPanel then T.pop(hudRefs.bagPanel, 1.03, .2) end
		end
	elseif info.tipo == "cheia" then
		ctx.toast(info.texto, nil, "warning")
		if hudRefs.bagPanel then T.shake(hudRefs.bagPanel, 7) end
	elseif info.tipo == "bloqueada" then
		ctx.toast(info.texto, nil, "warning")
	elseif info.tipo == "venda" then
		if type(info.ganho) == "number" and info.ganho > 0 and info.ganho < math.huge then
			Som.venda(info.ganho, info.itens)
			ctx.coinBurst(info.ganho)
			ctx.toast(info.texto or ("+" .. T.format(info.ganho) .. " moedas"), nil, "reward")
		end
	elseif info.tipo == "area" then
		local texto = tostring(info.texto or "")
		ctx.toast(texto, nil, (texto:find("moedas") or texto:find("Compra")) and "reward" or "info")
	elseif info.tipo == "comprarArea" then
		ctx.buyArea(info.areaId)
	end
end)
connect(R.AbrirIgnis.OnClientEvent,function() if ctx.page ~= "Forge" then ctx.open("Forge") end end)
connect(R.AbrirLoja.OnClientEvent,function() ctx.storeTab = "Mochilas"; if ctx.page ~= "Store" then ctx.open("Store") else ctx.refresh() end end)
connect(R.AbrirGacha.OnClientEvent,function(id)
	if Config.Gachas[id] then ctx.bannerArea = id; if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end end
end)
connect(player:GetAttributeChangedSignal("CurrentAreaId"),function()
	-- IslandTransition owns arrival audio at the actual transition, not at replication time.
	local id = player:GetAttribute("CurrentAreaId")
	local a = id and Config.areaPorId(id)
	local tema = a and Config.Temas[a.tema]
	Notify.banner({ title = a and a.nome or "Praça Central", subtitle = a and ("ILHA " .. a.id .. "  ·  " .. T.upper(tema.nome)) or "LOBBY  ·  IGNIS, BANNERS E PORTAIS",
		color = tema and tema.cor or P.accent, sound = false, duration = 1.8 })
	updateHUD()
end)
connect(player:GetAttributeChangedSignal("ExpeditionBlurEnabled"),updateBlur)

-- ---------------------------------------------------------------- RESOLUÇÃO
local function resize()
	local v = screen.AbsoluteSize
	if v.X < 1 or v.Y < 1 then return end
	ctx.portrait = v.X < v.Y * .85
	ctx.compact = not ctx.portrait and v.Y < 560
	local s
	if ctx.portrait then s = math.clamp(v.X / 500, .85, 1.25)
	elseif ctx.compact then s = math.max(.85,math.min(v.X / 1180, v.Y / 500))
	else s = math.clamp(math.min(v.X / BASE_W, v.Y / BASE_H), .5, 1.45) end
	if Input.TouchEnabled then s = math.max(.85, s) end
	scale.Scale = s
	T.uiScale = s
	virtualW, virtualH = v.X / s, v.Y / s
	canvas.Size = UDim2.fromOffset(virtualW, virtualH)
	for _, layer in ipairs({ hud, modalLayer, toastLayer, popupLayer, dialogHost, tipLayer }) do
		layer.Size = UDim2.fromOffset(virtualW, virtualH)
	end
	Notify.toastTop = ctx.portrait and 240 or 126
	drawHUD()
	hud.Visible = not (ctx.page and (fullPage() or ctx.portrait or ctx.compact))
	if ctx.page then drawWindow(false) end
	-- Reflow preserves builder state and input, without closing or shrinking controls.
	if popupOpen and popupState then renderPopup(popupState, true) end
	Notify.relayout()
end
screen:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)

connect(Input.InputBegan,function(input, processed)
	if processed or Input:GetFocusedTextBox() then return end
	local key = input.KeyCode
	if key == Enum.KeyCode.Escape or key==Enum.KeyCode.ButtonB then
		if popupOpen then closePopup() elseif ctx.page then ctx.close() end
	elseif key == Enum.KeyCode.H or key == Enum.KeyCode.B or key==Enum.KeyCode.ButtonY then ctx.collection = "pet"; ctx.open("Inventory")
	elseif key == Enum.KeyCode.J then ctx.open("Items")
	elseif key == Enum.KeyCode.G then ctx.open("Summon") end
end)
screen.Destroying:Connect(function() alive=false;for _,c in ipairs(connections) do c:Disconnect() end;blur:Destroy() end)
resize()

task.spawn(function()
	for attempt = 1, 8 do
		if hydrated then break end
		local version = pushVersion
		local ok, data = pcall(function() return R.PedirDados:InvokeServer() end)
		if ok and version == pushVersion and data then acceptData(data) end
		if not hydrated then task.wait(.5 + attempt * .15) end
	end
	if not hydrated then ctx.toast("Não foi possível carregar seus dados. Reconecte ao jogo.", nil, "error") end
end)
task.spawn(function()
	local images = { T.Assets.icons, T.Assets.header, T.Assets.lobby }
	for _, id in ipairs(T.Assets.areas) do table.insert(images, id) end
	pcall(function() game:GetService("ContentProvider"):PreloadAsync(images) end)
end)

]========],base=[========[-- ============================================================================
-- EXPEDITION CLIENT · UI V2
-- HUD, janelas, popups, confirmações e o fluxo de recompensas do jogo.
-- Visual e componentes: ReplicatedStorage.ExpeditionUI (Theme, Notify, Menus, Inventory).
-- A lógica de jogo continua no servidor; este script só chama os mesmos Remotes.
-- ============================================================================
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Input = game:GetService("UserInputService")
local Lighting = game:GetService("Lighting")
local player = Players.LocalPlayer
local pg = player:WaitForChild("PlayerGui")
local R = RS:WaitForChild("Remotes")
local Config = require(RS:WaitForChild("Config"))
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local Som = require(RS:WaitForChild("SomJogo"))
local AudioPreferences = require(RS:WaitForChild("AudioPreferences"))
local modules = RS:WaitForChild("ExpeditionUI")
local T = require(modules.Theme)
local Notify = require(modules.Notify)
local Inventory = require(modules.Inventory)
local Menus = require(modules.Menus)
local P, C = T.P, T.C
local WHITE = Color3.new(1, 1, 1)

local BASE_W, BASE_H = 1440, 850
local GuiService=game:GetService("GuiService")
local function usingGamepad() return Input:GetLastInputType().Name:find("Gamepad")~=nil end
local oldScreen=pg:FindFirstChild("ExpeditionUI")
if oldScreen then oldScreen:Destroy() end
local screen = T.new("ScreenGui", { Name = "ExpeditionUI", ResetOnSpawn = false, DisplayOrder = 25, IgnoreGuiInset = false, ClipToDeviceSafeArea = true,
	ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, pg)
local canvas = T.frame(screen, "Canvas", 0, 0, BASE_W, BASE_H, nil, 1)
local scale = T.new("UIScale", { Scale = 1 }, canvas)
local hud = T.frame(canvas, "HUD", 0, 0, BASE_W, BASE_H, nil, 1)
local dim = T.new("TextButton", { Name = "ModalBackdrop", Text = "", Size = UDim2.fromScale(1, 1), BackgroundColor3 = P.bg0,
	BackgroundTransparency = .45, BorderSizePixel = 0, AutoButtonColor = false, Visible = false, ZIndex = 20, Active = true }, canvas)
local modalLayer = T.frame(canvas, "ModalLayer", 0, 0, BASE_W, BASE_H, nil, 1)
modalLayer.ZIndex = 21
local toastLayer = T.frame(canvas, "Notifications", 0, 0, BASE_W, BASE_H, nil, 1)
toastLayer.ZIndex = 70
local popupLayer = T.frame(canvas, "PopupLayer", 0, 0, BASE_W, BASE_H, nil, 1)
popupLayer.ZIndex = 90
local dialogHost = T.frame(popupLayer, "Dialogs", 0, 0, BASE_W, BASE_H, nil, 1)
local tipLayer = T.frame(canvas, "TooltipLayer", 0, 0, BASE_W, BASE_H, nil, 1)
tipLayer.ZIndex = 120
local blur = T.new("BlurEffect", { Name = "ExpeditionMenuBlur", Size = 0 }, Lighting)

local ctx = { data = nil, page = nil, collection = "pet", selected = nil, search = "", rarity = nil, ownedOnly = true, favorites = {},
	areaFavorites = {}, storeTab = "Picaretas", eventsTab = "Diario", bannerArea = 1, inventoryScroll = {}, scrollMemory = {},
	portrait = false, compact = false, summonBusy = false }
local virtualW, virtualH = BASE_W, BASE_H
local window, body, searchBox
local bodyW, bodyH = 0, 0
local actionBusy = {}
local pushVersion, hydrated, modalVersion = 0, false, 0
local pendingRefresh, lastInventorySignature = false, ""
local drawWindow, drawHeader, drawBody, drawHUD, updateHUD
local closePopup
local hudRefs = {}
local popupOpen = false
local popupOnClose=nil
local popupFocus=nil
local popupState=nil
local pendingOffer=nil
local alive=true
local connections={}
local function connect(signal,fn) local c=signal:Connect(fn);table.insert(connections,c);return c end
screen:SetAttribute("OpenPage","")
screen:SetAttribute("PopupOpen",false)
ctx.T, ctx.Notify = T, Notify

-- Apply locally at once; coalesce rapid +/- presses into a small profile patch.
-- Only the audio whitelist is persisted. Other visual preferences remain session-local.
local pendingAudio, failedAudio, audioWorker = {}, {}, false
local audioHydrated = false
ctx.audioSaveStatus = "loading"
for key, default in pairs(AudioPreferences.defaults) do
	if AudioPreferences.value(key, player:GetAttribute(key)) == nil then player:SetAttribute(key, default) end
end
local function audioStatus(status)
	ctx.audioSaveStatus = status
	if ctx.audioSettingsStatus then ctx.audioSettingsStatus() end
end
function ctx.setAudioPreference(key, value)
	value = AudioPreferences.value(key, value)
	if value == nil then return end
	player:SetAttribute(key, value)
	for failedKey, failedValue in pairs(failedAudio) do
		if pendingAudio[failedKey] == nil then pendingAudio[failedKey] = failedValue end
	end
	failedAudio = {}
	pendingAudio[key] = value
	audioStatus("pending")
	if audioWorker then return end
	audioWorker = true
	task.spawn(function()
		task.wait(.35)
		while alive and next(pendingAudio) do
			local patch = pendingAudio
			pendingAudio = {}
			local remote = R:FindFirstChild("AtualizarAudioProfile") or R:WaitForChild("AtualizarAudioProfile", 5)
			local ok, result = false, nil
			for attempt = 1, 3 do
				if remote and remote:IsA("RemoteFunction") then
					ok, result = pcall(function() return remote:InvokeServer(patch) end)
				end
				if ok and type(result) == "table" and result.ok then break end
				if attempt < 3 then task.wait(.6) end
			end
			if not alive then break end
			if ok and type(result) == "table" and result.ok then
				local confirmed = AudioPreferences.sanitize(result.audio)
				for key, value in pairs(confirmed) do
					-- A response for an older press must not roll back newer local input.
					if pendingAudio[key] == nil then player:SetAttribute(key, value) end
				end
				ctx.audioPersistent = result.persistent == true
				audioStatus(next(pendingAudio) and "pending" or (ctx.audioPersistent and "profile" or "session"))
			else
				-- Retain failed fields for the next deliberate edit, without a retry loop.
				for key, value in pairs(patch) do
					if pendingAudio[key] == nil then failedAudio[key] = value end
				end
				if next(pendingAudio) then
					for key, value in pairs(failedAudio) do
						if pendingAudio[key] == nil then pendingAudio[key] = value end
					end
					failedAudio = {}
				end
				audioStatus("error")
			end
			task.wait(.35)
		end
		audioWorker = false
	end)
end

T.setTooltipLayer(tipLayer, function() return scale.Scale end)
-- com uma janela aberta o HUD fica atrás do fundo escuro: nada de dica dele aparecendo por cima
T.setTooltipGuard(function(o) return not (ctx.page and o:IsDescendantOf(hud)) end)
Notify.init(toastLayer, popupLayer, function() return virtualW, virtualH end)
Notify.feedAnchor = function() return virtualW - 24, virtualH - (ctx.portrait and 272 or 128) end

-- ---------------------------------------------------------------- PÁGINAS
local PAGE = {
	Store = { title = "Loja", icon = "store", color = P.gold, sub = "Picaretas, mochilas, passes e boosts" },
	Inventory = { title = "Unidades", icon = "units", color = P.accent },
	Areas = { title = "Viajar", icon = "areas", color = P.teal, sub = "Ilhas de mineração e atalhos do lobby" },
	Summon = { title = "Invocar", icon = "summon", color = P.violet },
	Forge = { title = "Forja de Ignis", icon = "forge", color = P.ember, sub = "Venda seus minérios por moedas" },
	Settings = { title = "Configurações", icon = "settings", color = T.Page.Settings, sub = "Som, efeitos e códigos" },
	Quests = { title = "Missões", icon = "quests", color = P.warning },
	Events = { title = "Diário & Index", icon = "events", color = P.pink, sub = "Recompensas diárias e coleção" },
}
ctx.PAGE = PAGE

-- ---------------------------------------------------------------- TOASTS / BLUR
local function kindFor(color)
	if color == C.green then return "success" elseif color == C.red then return "error"
	elseif color == C.orange then return "warning" elseif color == C.gold then return "reward" end
	return "info"
end
function ctx.toast(value, color, kind)
	Notify.push(value, kind or kindFor(color))
end

local function updateBlur()
	local amount = ctx.page and player:GetAttribute("ExpeditionBlurEnabled") ~= false and 6 or 0
	T.tween(blur, .2, { Size = amount }, Enum.EasingStyle.Quad)
end

-- ---------------------------------------------------------------- POPUPS
closePopup = function()
	if not popupOpen then return end
	popupOpen = false
	popupState = nil
	screen:SetAttribute("PopupOpen",false)
	if popupOnClose then local fn=popupOnClose;popupOnClose=nil;pcall(fn) end
	if popupFocus and popupFocus.Parent then GuiService.SelectedObject=popupFocus end
	popupFocus=nil
	local old = dialogHost:GetChildren()
	for _, o in ipairs(old) do
		o.Name = o.Name .. "_Closing"
		if o:IsA("TextButton") then T.tween(o, .1, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad) end
		local sc = o:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .1, { Scale = .94 }, Enum.EasingStyle.Quad) end
	end
	task.delay(.11, function() for _, o in ipairs(old) do o:Destroy() end end)
end
ctx.closePopup = function() closePopup() end

-- A resize renders the same builder/closure again. Stateful selection stays in that
-- closure; text, scroll and focus survive by their stable component names.
local function renderPopup(state, reflow)
	local saved, selectedName = {}, nil
	if state.box and state.box.Parent then
		local selected = GuiService.SelectedObject
		if selected and selected:IsDescendantOf(state.box) then selectedName = selected.Name end
		for _, object in ipairs(state.box:GetDescendants()) do
			if object:IsA("TextBox") then
				table.insert(saved, { name = object.Name, class = "TextBox", text = object.Text,
					focused = object:IsFocused(), cursor = object.CursorPosition, selection = object.SelectionStart })
			elseif object:IsA("ScrollingFrame") then
				table.insert(saved, { name = object.Name, class = "ScrollingFrame", position = object.CanvasPosition })
			end
		end
		state.box:Destroy()
	end
	if state.shield then state.shield:Destroy() end
 if state.shadow then state.shadow:Destroy() end
	T.hideTooltip()
	local opts = state.opts
	local w = math.min(state.width, virtualW - 32)
	local h = math.min(state.height, virtualH - 40)
	local shield = T.new("TextButton", { Name = "PopupBackdrop", Text = "", AutoButtonColor = false, BorderSizePixel = 0,
		BackgroundColor3 = P.bg0, BackgroundTransparency = reflow and .35 or 1, Size = UDim2.fromScale(1, 1) }, dialogHost)
	state.shield = shield
	if not reflow then T.tween(shield, .16, { BackgroundTransparency = .35 }, Enum.EasingStyle.Quad) end
	shield.Activated:Connect(function() if not opts.modal then closePopup() end end)
	local box = T.panel(dialogHost, "Popup", (virtualW - w) / 2, (virtualH - h) / 2, w, h, { bg = P.bg1, radius = 16, strokeColor = P.line, shade = false })
	state.box = box
	box.Active = true
	local shadow = T.shadow(box, 16, 10, .4)
 state.shadow=shadow
	local accent = opts.color or P.accent
	local line = T.frame(box, "Accent", 18, 0, w - 36, 3, accent, 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, line)
	local closeSize = math.max(44, math.ceil(44 / scale.Scale))
	T.text(box, "Title", state.title, 22, 14, w - closeSize - 44, 36, 24, P.text, T.LEFT, "display")
	T.closeButton(box, w - closeSize - 12, 8, closeSize, closePopup)
	local area = T.frame(box, "Content", 20, 64, w - 40, h - 84, nil, 1)
	state.builder(area, w - 40, h - 84, reflow == true)
	for _, value in ipairs(saved) do
		local object = area:FindFirstChild(value.name, true)
		if object and object:IsA(value.class) and value.class == "TextBox" then object.Text = value.text end
	end
	task.defer(function()
		if popupState ~= state or state.box ~= box or not box.Parent then return end
		for _, value in ipairs(saved) do
			local object = area:FindFirstChild(value.name, true)
			if object and object:IsA(value.class) then
				if value.class == "ScrollingFrame" then object.CanvasPosition = value.position
				elseif value.focused then
					object:CaptureFocus(); object.CursorPosition = value.cursor; object.SelectionStart = value.selection
				end
			end
		end
		if usingGamepad() then
			local selected = selectedName and box:FindFirstChild(selectedName, true)
			GuiService.SelectedObject = selected and selected:IsA("GuiButton") and selected or box:FindFirstChildWhichIsA("GuiButton", true)
		end
	end)
	if not reflow then
		T.enter(box, .97, .18)
		T.enter(shadow, .97, .18)
		T.som("ui_popup")
	end
	return box
end

function ctx.popup(title, builder, w, h, opts)
	opts = opts or {}
	closePopup()
	popupOpen = true
	screen:SetAttribute("PopupOpen", true)
	popupOnClose = opts.onClose
	popupFocus = GuiService.SelectedObject
	popupState = { title = title, builder = builder, width = w or 560, height = h or 420, opts = opts }
	return renderPopup(popupState, false)
end

function ctx.refreshPopup()
	if popupOpen and popupState then renderPopup(popupState, true) end
end

-- confirmação. opts: confirmText, cancelText, tone, cost (moedas), preview(p,w) + previewH, w, h
function ctx.confirm(title, message, callback, opts)
	opts = opts or {}
	local hasCost = opts.cost ~= nil
	local used = false
	ctx.popup(title, function(p, w, h)
		local detailHeight = (opts.preview and (opts.previewH or 0) + 10 or 0) + 80 + (hasCost and 94 or 0)
		local details = T.scroll(p, "ConfirmationDetails", 0, 0, w, h - 66, opts.tone or P.accent)
		local cw = w - 14
		local y = 0
		if opts.preview then opts.preview(details, cw); y = (opts.previewH or 0) + 10 end
		T.para(details, "Prompt", message, 0, y, cw, 64, 18, P.text2, T.CENTER, "body")
		y += 80
		if hasCost then
			local have = ctx.data and ctx.data.moeda or 0
			local row = T.panel(details, "CostRow", 0, y, cw, 58, { bg = P.bg0, radius = 12 })
			T.text(row, "CostLabel", "PREÇO", 16, 0, 120, 58, 14, P.text2, T.LEFT, "title")
			T.icon(row, "coins", cw - 196, 9, 40, 40)
			T.text(row, "Cost", T.format(opts.cost), cw - 152, 0, 136, 58, 26, P.gold, T.RIGHT, "display", 1.4)
			T.text(details, "After", have >= opts.cost and ("Saldo depois da compra: " .. T.format(have - opts.cost)) or ("Faltam " .. T.format(opts.cost - have) .. " moedas"),
				0, y + 64, cw, 24, 14, have >= opts.cost and P.text3 or P.danger, T.CENTER, "body")
		end
		details.CanvasSize = UDim2.fromOffset(0, detailHeight)
		local bw = (w - 12) / 2
		T.button(p, "Cancel", opts.cancelText or "Cancelar", 0, h - 52, bw, 52, P.neutral, closePopup, { sound = "ui_cancel" })
		local ok = T.button(p, "Confirm", opts.confirmText or "Confirmar", bw + 12, h - 52, bw, 52, opts.tone or P.success, function()
			if used then return end
			used = true
			closePopup()
			callback()
		end)
		if hasCost and (ctx.data and ctx.data.moeda or 0) < opts.cost then T.setEnabled(ok, false) end
	end, opts.w or 520, opts.h or ((hasCost and 330 or 250) + (opts.previewH and opts.previewH + 10 or 0)), { color = opts.tone })
end

-- ---------------------------------------------------------------- RECOMPENSA VISUAL
-- moedas saem do centro, param um instante e voam para a carteira (o contador sobe quando chegam)
function ctx.coinBurst(amount, sx, sy)
	local wallet = hudRefs.wallet
	if not wallet or not wallet.Parent or not T.motionEnabled() then return end
	sx, sy = sx or virtualW / 2, sy or virtualH * .55
	local tx = wallet.Position.X.Offset + 26
	local ty = wallet.Position.Y.Offset + 27
	local n = math.clamp(math.floor(math.log10(math.max(10, amount or 10)) * 1.6), 5, 14)
	for i = 1, n do
		local c = T.icon(toastLayer, "coins", sx - 20, sy - 20, 40, 40)
		c.ZIndex = 40
		local ang = math.random() * math.pi * 2
		local rad = 50 + math.random() * 90
		T.tween(c, .26, { Position = UDim2.fromOffset(sx - 20 + math.cos(ang) * rad, sy - 20 + math.sin(ang) * rad * .7) }, Enum.EasingStyle.Quad)
		task.delay(.34 + i * .04, function()
			T.tween(c, .44, { Position = UDim2.fromOffset(tx - 15, ty - 15), Size = UDim2.fromOffset(30, 30) }, Enum.EasingStyle.Quint, Enum.EasingDirection.In)
			task.delay(.44, function()
				c:Destroy()
				-- Visual particles do not emit extra coins: the confirmed reward owns its audio.
				if wallet.Parent then T.pop(wallet, 1.05, .16) end
			end)
		end)
	end
end

local function floatDelta(text, col)
	local wallet = hudRefs.wallet
	if not wallet or not wallet.Parent then return end
	local x = wallet.Position.X.Offset
	local y = wallet.Position.Y.Offset + 58
	local w = wallet.Size.X.Offset
	local t = T.text(hud, "CoinDelta", text, x, y, w - 20, 24, 20, col, T.RIGHT, "display", 1.6)
	T.tween(t, .8, { Position = UDim2.fromOffset(x, y + 14), TextTransparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In, .25)
	local st = t:FindFirstChildOfClass("UIStroke")
	if st then T.tween(st, .8, { Transparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In, .25) end
	task.delay(1.1, function() t:Destroy() end)
end

-- ---------------------------------------------------------------- REMOTES
function ctx.invoke(name, ...)
	if name ~= "PedirDados" and not ctx.data then ctx.toast("Carregando seus dados...", nil, "info"); return { ok = false } end
	if actionBusy[name] then return { ok = false, msg = "Aguarde..." } end
	local remote = R:FindFirstChild(name) or R:WaitForChild(name, 3)
	if not remote or not remote:IsA("RemoteFunction") then ctx.toast("Ação indisponível no momento", nil, "error"); return { ok = false } end
	actionBusy[name] = true
	if name == "Vender" then ctx.coinHold = os.clock() + 1.05 end
	local args = table.pack(...)
	local ok, res = pcall(function() return remote:InvokeServer(table.unpack(args, 1, args.n)) end)
	actionBusy[name] = nil
	if not ok then ctx.coinHold = nil; ctx.toast("Falha na conexão. Tente novamente.", nil, "error"); return { ok = false } end
	if name == "PedirDados" then return res end
	if type(res) ~= "table" then ctx.toast("Não foi possível concluir a ação", nil, "error"); return { ok = false } end
	if res.semAcesso then task.defer(function() ctx.accessPopup(res.semAcesso) end) end
	if not res.ok then
		ctx.coinHold = nil
		if name ~= "RolarGacha" then -- a invocacao trata os proprios avisos (cooldown entre giros)
			Som.tocar("ui_erro")
			ctx.toast(res.msg or "Não foi possível concluir a ação", nil, "error")
		end
		return res
	end
	if name == "Vender" then
		Som.venda(res.ganho, res.itens)
		if res.ganho then
			ctx.coinBurst(res.ganho)
			ctx.toast("+" .. T.format(res.ganho) .. " moedas  ·  " .. tostring(res.itens or 0) .. " minérios vendidos", nil, "reward")
		elseif res.msg then ctx.toast(res.msg, nil, "success") end
		return res
	end
	if name == "ComprarArea" then
		Som.tocar("area_nova")
		local a = Config.areaPorId(args[1])
		Notify.banner({ title = "ILHA DESBLOQUEADA!", subtitle = a and a.nome or "", color = P.teal, sound = false, big = true, duration = 2.4 })
	elseif name == "ComprarPicareta" or name == "ComprarMochila" then
		Som.tocar(res.upgradeMax and "upgrade_max" or "upgrade")
		local def = name == "ComprarPicareta" and Config.picaretaPorId(args[1]) or Config.mochilaPorId(args[1])
		Notify.banner({ title = "UPGRADE!", subtitle = def and def.nome or "", color = P.gold, sound = false, duration = 2 })
	elseif name == "AlimentarPet" or name == "FundirHat" then
		local maximum = res.upgradeMax or (name == "AlimentarPet" and res.nivel and res.nivel >= Config.PET_NIVEL_MAX)
		Som.tocar(maximum and "upgrade_max" or (res.levelUp and "level_up" or "forge_success"))
		if res.levelUp and res.nivelAntes and res.nivel then ctx.levelUp(res) end
	elseif name == "EquiparHat" or name == "EquiparPet" or name == "EquiparPicareta" or name == "EquiparMelhores" or name == "EquiparMelhoresPets" then
		Som.tocar(res.equipped == false and "ui_desequipar" or "ui_equipar")
	elseif name == "DesequiparTodos" or name == "DesequiparPets" then
		Som.tocar("ui_desequipar")
	elseif name == "ResgatarMissao" then
		if not ctx.batchQuestAudio then Som.tocar("quest_complete") end
	elseif name == "ResgatarDaily" or name == "ResgatarCodigo" then
		Som.tocar("reward_banner")
	elseif name ~= "RolarGacha" and name ~= "UITravel" and name ~= "ComprarRobux" then
		Som.tocar("ui_confirm")
	end
	if res.msg and name ~= "RolarGacha" then ctx.toast(res.msg, nil, (name:find("Resgatar") or name:find("Comprar")) and "reward" or "success") end
	return res
end

-- fora do lobby: a opção GRÁTIS (teleporte até o Ignis) vem sempre primeiro
function ctx.accessPopup(nome)
	local passe = nome == "AutoSell" and Mon.passe("AutoSell")
	ctx.popup("Ignis está no lobby", function(p, w, h)
		local details = T.scroll(p, "AccessDetails", 0, 0, w, h - 66, P.ember)
		local cw = w - 14
		local art = T.panel(details, "Art", (cw - 120) / 2, 0, 120, 120, { bg = P.bg2, radius = 20, strokeColor = P.ember })
		T.icon(art, "forge", 10, 10, 100, 100)
		T.para(details, "Message", passe and "Venda com o Ignis usando o teleporte grátis, ou deixe o Auto Sell vender sozinho em qualquer ilha."
			or "Compras de equipamento são feitas com o Ignis. O teleporte até ele é grátis.", 0, 132, cw, 100, 18, P.text2, T.CENTER, "body")
		details.CanvasSize = UDim2.fromOffset(0, 240)
		local bw = passe and (w - 12) / 2 or w
		T.button(p, "GoIgnis", "Teleporte grátis", 0, h - 52, bw, 52, P.teal, function() closePopup(); ctx.travel("ignis") end)
		if passe then
			local b = T.button(p, "BuyPass", passe.id > 0 and ("Auto Sell  ·  R$ " .. passe.robux) or "Auto Sell (em breve)", bw + 12, h - 52, bw, 52, P.gold, function()
				if passe.id > 0 then ctx.invoke("ComprarRobux", "AutoSell") end
			end)
			T.setEnabled(b, passe.id > 0)
		end
	end, 560, 400, { color = P.ember })
end

-- ofertas enviadas pelo servidor (Starter no minuto 5, inventário cheio, mochila cheia)
local OFERTA_TEXTO = {
	Starter = { "Starter Pack", "Pack de Moedas M + Moedas x2 (30 min) + Sorte (15 min) + skin Kunai de Ignis.", "Starter", "Agora não", "store" },
	Inventario = { "Inventário cheio", "Funda hats repetidos para liberar espaço (grátis) ou aumente o inventário para 100.", "Inventario", "Fundir hats", "items" },
	AutoSell = { "Mochila cheia", "Teleporte grátis até o Ignis para vender, ou deixe o Auto Sell vender sozinho.", "AutoSell", "Teleporte grátis", "forge" },
}
local function ofertaPopup(oferta)
	local info = OFERTA_TEXTO[oferta]
	if not info then return end
	if ctx.summonBusy or popupOpen or ctx.page or player:GetAttribute("RevealOpen") or player:GetAttribute("TravelTransition") then pendingOffer=oferta;return end
	local item = Mon.passe(info[3]) or Mon.produto(info[3])
	if not item or item.id<=0 then return end
	local fechou = false
	local function fechar(acao)
		if fechou then return end
		fechou = true
		local ev = R:FindFirstChild("OfertaAcao")
		if ev then ev:FireServer("fechada", oferta) end
		closePopup()
		if acao == "Fundir hats" then ctx.collection = "hat"; ctx.open("Inventory")
		elseif acao == "Teleporte grátis" then ctx.travel("ignis") end
	end
	ctx.popup(info[1], function(p, w, h)
		local details = T.scroll(p, "OfferDetails", 0, 0, w, h - 66, P.gold)
		local cw = w - 14
		local narrow = cw < 420
		local heroH = narrow and 238 or 150
		local hero = T.panel(details, "Hero", 0, 0, cw, heroH, { bg = P.bg2, radius = 14, strokeColor = P.gold:Lerp(P.bg2, .4) })
		T.stripes(hero, "Energy", math.max(0, cw - 240), 0, math.min(cw, 240), heroH, P.gold, .93)
		T.icon(hero, info[5], 16, 15, narrow and 72 or 120, narrow and 72 or 120)
		T.text(hero, "Name", item and item.nome or info[1], narrow and 100 or 150, 22, cw - (narrow and 116 or 170), narrow and 58 or 34, 26, P.text, T.LEFT, "display")
		T.para(hero, "Desc", info[2], narrow and 16 or 150, narrow and 100 or 60, narrow and cw - 32 or cw - 170, narrow and 124 or 76, 16, P.text2, T.LEFT, "body")
		local detailsH = heroH + 8
		if item and item.starter and item.valorSeparado then
			T.para(details, "Deal", "Vendido separado: R$ " .. item.valorSeparado .. "   ·   aqui: R$ " .. item.robux, 0, heroH + 12, cw, 40, 14, P.success, T.CENTER)
			detailsH = heroH + 60
		end
		details.CanvasSize = UDim2.fromOffset(0, detailsH)
		local bw = (w - 12) / 2
		T.button(p, "Free", info[4], 0, h - 52, bw, 52, P.neutral, function() fechar(info[4]) end)
		local label = item and (item.id > 0 and (item.nome .. "  ·  R$ " .. item.robux) or (item.nome .. " (em breve)")) or "Loja"
		local buy = T.button(p, "Buy", label, bw + 12, h - 52, bw, 52, P.gold, function()
			if item and item.id > 0 then ctx.invoke("ComprarRobux", item.chave) end
			fechar(nil)
		end)
		if item and item.id <= 0 then T.setEnabled(buy, false) end
	end, 620, 330, { color = P.gold, modal = true })
end
task.spawn(function()
	local ev = R:WaitForChild("OfertaMostrar", 30)
	if ev then connect(ev.OnClientEvent,function(oferta) ofertaPopup(oferta) end) end
end)

-- comprar a próxima área com moedas
function ctx.buyArea(areaId)
	local a = Config.areaPorId(areaId)
	if not a or not ctx.data then return end
	if ctx.data.areas[areaId] then ctx.travel("area", areaId); return end
	local prev = Config.areaPorId(areaId - 1)
	if prev and not ctx.data.areas[prev.id] then ctx.toast("Desbloqueie " .. prev.nome .. " antes", nil, "warning"); return end
	ctx.confirm("Desbloquear ilha", "Nova ilha com minérios, hats e missões próprias.", function()
		local res = ctx.invoke("ComprarArea", areaId)
		if res and res.ok then ctx.refresh() end
	end, {
		cost = a.custo, confirmText = "Desbloquear", tone = P.success, previewH = 120,
		preview = function(p, w)
			local f = T.frame(p, "Scene", 0, 0, w, 120, P.bg0, 0)
			T.corner(f, 12)
			local img = T.image(f, "Image", T.areaImage(a.id), 0, 0, w, 120)
			img.ScaleType = Enum.ScaleType.Crop
			T.corner(img, 12)
			local shade = T.frame(f, "Shade", 0, 0, w, 120, P.bg0, 0)
			T.corner(shade, 12)
			T.fade(shade, 90, .85, .15)
			local tema = Config.Temas[a.tema]
			T.text(f, "Name", a.nome, 16, 70, w - 32, 38, 28, WHITE, T.LEFT, "display", 1.8)
			T.text(f, "Tag", "ILHA " .. a.id .. "  ·  " .. T.upper(tema and tema.nome or ""), 16, 50, w - 32, 20, 13, tema and tema.cor or P.accent, T.LEFT, "title", 1.4)
		end,
	})
end

-- ---------------------------------------------------------------- JANELAS
function ctx.close()
	if not ctx.page then return end
	Som.tocar("ui_fechar")
	ctx.page = nil
	ctx.cancelSummon = true
	modalVersion += 1
	local old = modalLayer:GetChildren()
	for _, o in ipairs(old) do
		local sc = o:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .11, { Scale = .94 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In) end
	end
	task.delay(.11, function() for _, o in ipairs(old) do o:Destroy() end end)
	window, body, searchBox = nil, nil, nil
	T.tween(dim, .14, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad)
	task.delay(.15, function() if not ctx.page then dim.Visible = false end end)
	closePopup()
	T.hideTooltip()
	updateBlur()
	hud.Visible = true
	screen:SetAttribute("OpenPage", "")
	GuiService.SelectedObject=nil
end

function ctx.open(page)
	if player:GetAttribute("RevealOpen") or player:GetAttribute("TravelTransition") or player:GetAttribute("AreaTransition")~=nil then return end
	if page == "Items" then ctx.collection = "hat"; page = "Inventory"
	elseif page == "Play" then page = "Areas" end
	if ctx.page == page then
		if page ~= "Inventory" then ctx.close(); return end
		ctx.search, ctx.rarity, ctx.selected = "", nil, nil
		drawWindow(false)
		return
	end
	if not PAGE[page] then return end
	local wasOpen = ctx.page ~= nil
	ctx.page = page
	ctx.search, ctx.rarity, ctx.selected = "", nil, nil
	if ctx.summonBusy then ctx.cancelSummon = true end
	closePopup()
	T.hideTooltip()
	dim.Visible = true
	if not wasOpen then
		dim.BackgroundTransparency = 1
		T.tween(dim, .18, { BackgroundTransparency = .58 }, Enum.EasingStyle.Quad)
	end
	hud.Visible = not (ctx.portrait or ctx.compact)
	-- o fundo escuro cobre o HUD antes do MouseLeave: devolve os botões ao tamanho normal
	local function resetHudScale()
		if not ctx.page then return end
		for _, o in ipairs(hud:GetDescendants()) do
			if o:IsA("UIScale") and o.Parent:IsA("GuiButton") then o.Scale = 1 end
		end
	end
	resetHudScale()
	task.delay(.3, resetHudScale) -- o "soltar" do clique ainda anima o botão por .24s
	screen:SetAttribute("OpenPage", page)
	Som.tocar(page == "Forge" and "forge_interact" or (wasOpen and "ui_tab" or "ui_abrir"))
	drawWindow(not wasOpen)
	updateBlur()
end

function ctx.refresh()
	if pendingRefresh then return end
	pendingRefresh = true
	task.defer(function()
		pendingRefresh = false
		if ctx.page then drawHeader(); drawBody() end
		updateHUD()
	end)
end
function ctx.redrawBody() drawBody() end
dim.Activated:Connect(function() if popupOpen then closePopup() else ctx.close() end end)

function ctx.travel(action, id, keepMenu)
	if actionBusy.UITravel then return end
	local result = ctx.invoke("UITravel", action, id)
	if result and result.ok then
		if keepMenu then
			ctx.bannerArea = id
			if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end
		else
			ctx.close()
		end
	end
end

-- ---------------------------------------------------------------- INVOCAÇÃO
local function showResults(results, count, playAudio)
	if #results == 0 then return end
	playAudio = playAudio ~= false
	local desiredCols = math.min(#results, ctx.portrait and 2 or 5)
	local width = math.max(460, desiredCols * 170 + (desiredCols - 1) * 12 + 54)
	local height = math.ceil(#results / desiredCols) * 244 + 150
	local best
	for _, r in ipairs(results) do
		local rr = T.rar(r.raridade)
		if not best or rr.ordem > T.rar(best.raridade).ordem then best = r end
	end
	local revealPlayed, rarityPlayed = false, false
	ctx.popup("Invocação concluída", function(p, w, h, reflow)
		local gap = 12
		local available = w - 14
		local cols = math.max(1, math.min(#results, ctx.portrait and 2 or 5, math.floor((available + gap) / 168)))
		local rows = math.ceil(#results / cols)
		local cw = math.min(170, math.floor((available - (cols - 1) * gap) / cols))
		local ch = cw + 62
		local s = T.scroll(p, "Results", 0, 0, w, h - 66, P.violet)
		s.CanvasSize = UDim2.fromOffset(0, rows * (ch + gap))
		local margin = (available - (cols * cw + (cols - 1) * gap)) / 2
		local delay = .1
		for i, result in ipairs(results) do
			local def = Config.petPorId(result.petId)
			local r, key = T.rar(result.raridade)
			local cx = margin + ((i - 1) % cols) * (cw + gap) + cw / 2
			local cy = math.floor((i - 1) / cols) * (ch + gap) + ch / 2 + 2
			local card = T.panel(s, "Result_" .. i, 0, 0, cw, ch, { bg = P.bg2, radius = 14, strokeColor = r.cor, strokeWidth = 2 })
			card.AnchorPoint = Vector2.new(.5, .5)
			card.Position = UDim2.fromOffset(cx, cy)
			card.ClipsDescendants = true
			-- verso: só a cor da raridade (antecipação)
			local back = T.frame(card, "Back", 0, 0, cw, ch, r.cor, 0)
			T.corner(back, 14)
			T.gradient(back, r.cor:Lerp(P.bg0, .45), r.cor:Lerp(P.bg0, .8))
			T.stripes(back, "Energy", 0, 0, cw, ch, WHITE, .9)
			T.text(back, "Mark", "?", 0, 0, cw, ch, 64, r.cor:Lerp(WHITE, .5), T.CENTER, "display", 2)
			local sc = T.new("UIScale", { Scale = .001 }, card)
			local high = r.ordem >= 5
			if high then delay += .35 end
			local thisDelay = delay
			delay += .12
			task.delay(reflow and 0 or thisDelay, function()
				if not card.Parent then return end
				if reflow then sc.Scale = 1 else T.tween(sc, .22, { Scale = 1 }, Enum.EasingStyle.Back) end
				task.delay(reflow and 0 or (high and .45 or .16), function()
					if not card.Parent then return end
					back:Destroy()
					T.rarityFrame(card, key, { animated = r.ordem >= 5 })
					T.preview(card, "pet", result.petId, 8, 10, cw - 16, ch - 82, false)
					local plate = T.frame(card, "Plate", 0, ch - 76, cw, 76, P.bg1, .1)
					T.text(plate, "Name", def and def.nome or result.nome or "", 8, 6, cw - 16, 28, 20, P.text, T.CENTER, "display", 1.4)
					local chip, chw = T.chip(plate, "Rarity", T.upper(r.nome), 0, 40, 26, r.cor, { size = 13 })
					chip.Position = UDim2.fromOffset((cw - chw) / 2, 40)
					if result.novo then
						local nc, nw = T.chip(card, "New", "NOVO!", 0, 8, 24, P.success, { solid = true, size = 13 })
						nc.Position = UDim2.fromOffset(cw - nw - 8, 8)
					end
					if not reflow then T.pop(card, high and 1.18 or 1.08, .3) end
					if playAudio then
						-- One rarity signature for the best item, even for x10 summons.
						if result == best and not rarityPlayed then
							rarityPlayed = true
							Som.drop(result.raridade)
						elseif not revealPlayed and not rarityPlayed then
							revealPlayed = true
							Som.tocar("summon_reveal")
						end
					end
				end)
			end)
		end
		T.button(p, "Continue", "Continuar", 0, h - 54, (w - 12) / 2, 54, P.neutral, closePopup)
		T.button(p, "Again", "Invocar de novo " .. (count > 1 and ("x" .. count) or ""), (w - 12) / 2 + 12, h - 54, (w - 12) / 2, 54, P.violet, function()
			closePopup()
			task.defer(ctx.startSummon, count)
		end)
		if not reflow and best and T.rar(best.raridade).ordem >= 5 then
			local bd = Config.petPorId(best.petId)
			local br = T.rar(best.raridade)
			task.delay(delay + .5, function()
				if not s.Parent or not popupOpen then return end
				Notify.banner({ title = T.upper(br.nome) .. "!", subtitle = bd and bd.nome or "", color = br.cor, sound = false, big = br.ordem >= 6, duration = 2.2 })
			end)
		end
	end, width, height, { color = P.violet })
end

function ctx.showLastSummon()
	if ctx.lastSummonResults then showResults(ctx.lastSummonResults,ctx.lastSummonCount or #ctx.lastSummonResults,false) end
end

function ctx.nearBanner(areaId)
	local a = Config.areaPorId(areaId)
	local machines = workspace:FindFirstChild("Gachas")
	local machine = machines and a and machines:FindFirstChild("Gacha_" .. a.tema)
	if not machine then return false end
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local pad = machine:FindFirstChild("PadGacha")
	local pos = pad and pad.Position or machine:GetPivot().Position
	return (root.Position - pos).Magnitude <= 58
end

function ctx.startSummon(count)
	if ctx.summonBusy or not ctx.data then return end
	local areaId = ctx.bannerArea
	if not ctx.data.areas[areaId] then ctx.toast("Desbloqueie esta ilha primeiro", nil, "warning"); return end
	local cost = Config.Gachas[areaId].custo * (ctx.data.giroGratis and math.max(0, count - 1) or count)
	if ctx.data.moeda < cost then ctx.toast("Moedas insuficientes", nil, "error"); Som.tocar("ui_erro"); return end
	if not ctx.nearBanner(areaId) then
		ctx.toast("Viaje até o banner para invocar", nil, "info")
		return
	end
	ctx.summonBusy = true
	ctx.cancelSummon = false
	local results = {}
	ctx.refresh()
	task.spawn(function()
		for i = 1, count do
			if ctx.cancelSummon then break end
			if ctx.onSummonProgress then pcall(ctx.onSummonProgress, i, count) end
			local result
			for tentativa = 1, 3 do
				result = ctx.invoke("RolarGacha", areaId)
				-- "Calma ai": cooldown do servidor entre giros. Espera e tenta de novo em vez de cortar a sequencia.
				if result and not result.ok and result.msg and result.msg:find("Calma") then task.wait(.35) else break end
			end
			if not result or not result.ok then
				Som.tocar("ui_erro")
				if result and result.msg and not result.msg:find("Calma") then ctx.toast(result.msg, nil, "error") end
				break
			end
			if #results == 0 then Som.tocar("invocar_inicio") end
			table.insert(results, result)
			if i < count then task.wait(.66) end
		end
		ctx.summonBusy = false
		ctx.onSummonProgress = nil
		ctx.refresh()
		ctx.lastSummonResults,ctx.lastSummonCount=results,count
		if ctx.page=="Summon" and not ctx.cancelSummon then showResults(results,count)
		elseif #results>0 then
			local best = results[1]
			for _, result in ipairs(results) do
				if T.rar(result.raridade).ordem > T.rar(best.raridade).ordem then best = result end
			end
			Som.drop(best.raridade)
			ctx.toast(tostring(#results).." unidade(s) recebida(s). Veja o último resultado em Invocar.",nil,"reward")
		end
	end)
end

function ctx.levelUp(res)
	Notify.levelUp(res.nivelAntes, res.nivel)
end

-- ---------------------------------------------------------------- CABEÇALHO / CORPO
local FULLSCREEN = {Inventory=true}
local function fullPage() return FULLSCREEN[ctx.page] and not ctx.portrait and not ctx.compact end
local function scrollKey(name)
	return table.concat({ ctx.page or "", ctx.collection or "", ctx.storeTab or "", tostring(ctx.questArea or ""),
		tostring(ctx.bannerArea or ""), ctx.eventsTab or "", name }, ":")
end

local function pageTitle()
	local info = PAGE[ctx.page] or PAGE.Quests
	local title, icon, col, sub = info.title, info.icon, info.color, info.sub
	local d = ctx.data
	if ctx.page == "Inventory" then
		if ctx.collection == "hat" then title, icon, col = "Itens", "items", P.info end
		if d then
			local total = ctx.collection == "hat" and (d.totalHats or 0) or (d.totalPets or 0)
			local cap = ctx.collection == "hat" and (d.capacidadeHats or 0) or (d.capacidadePets or 0)
			local eq = ctx.collection == "hat" and #(d.equipados or {}) or #(d.petsEquipados or {})
			local slots = ctx.collection == "hat" and d.slots or d.slotsPets
			sub = total .. " / " .. cap .. " no inventário   ·   " .. eq .. " / " .. tostring(slots or "?") .. " equipados"
		end
	elseif ctx.page == "Quests" and d then
		local ready = 0
		for _, lista in pairs(Config.Missoes) do
			for _, m in ipairs(lista) do
				local e = d.missoes and d.missoes[m.id]
				if e and e.p >= m.meta and not e.r and d.areas[m.area] then ready += 1 end
			end
		end
		sub = ready > 0 and (ready .. " missão(ões) pronta(s) para resgatar") or "Complete objetivos em cada ilha"
	elseif ctx.page == "Summon" then
		local a = Config.areaPorId(ctx.bannerArea or 1)
		sub = "Banner  ·  " .. (a and a.nome or "")
	end
	return title, icon, col, sub
end

local function tabsFor()
	if ctx.page == "Inventory" then
		return { { id = "pet", label = "Unidades", icon = "units" }, { id = "hat", label = "Itens", icon = "items" } },
			ctx.collection, ctx.collection == "hat" and P.info or P.accent,
			function(id) ctx.collection = id; ctx.selected = nil; ctx.rarity = nil; ctx.refresh() end
	elseif ctx.page == "Store" then
		return { { id = "Picaretas", label = "Picaretas", icon = "pickaxe" }, { id = "Mochilas", label = "Mochilas", icon = "items" }, { id = "Passes", label = "Passes", icon = "vip" } },
			ctx.storeTab, P.gold, function(id) ctx.storeTab = id; ctx.refresh() end
	elseif ctx.page == "Events" then
		local daily = ctx.data and ctx.data.daily
		return { { id = "Diario", label = "Diário", icon = "gift", badge = daily and daily.disponivel and "!" or nil }, { id = "Index", label = "Index", icon = "units" } },
			ctx.eventsTab, P.pink, function(id) ctx.eventsTab = id; ctx.refresh() end
	end
end

drawHeader = function()
 if not window then return 0 end
 local title,icon,col,sub=pageTitle()
 local full=fullPage()
 local banner=window:FindFirstChild("Banner")
 if banner then
  banner.Title.Text=title
  local mark=banner:FindFirstChild("PageMark"); if mark then mark.BackgroundColor3=col end
  local slab=banner:FindFirstChild("Signature");if slab then slab.BackgroundColor3=col end
 end
 local sl=window:FindFirstChild("Subtitle")
 if sl then sl.Text=sub or (ctx.page=="Inventory" and "Selecione um item para ver detalhes e equipar" or "");sl.Visible=true end
 local tabsRoot=window:FindFirstChild("Tabs");if tabsRoot then tabsRoot:Destroy() end
 local items,current,tcol,onPick=tabsFor()
 if items then
  local ww=window.Size.X.Offset
  local th=(ctx.portrait or ctx.compact) and 60 or 52
  local tx=full and math.max(310,ww*.34) or 24
  local ty=full and 18 or 100
  local tw=full and math.min(660,ww-tx-130) or math.min(ww-48,660)
  tabsRoot=T.frame(window,"Tabs",tx,ty,tw,th,nil,1)
  T.tabs(tabsRoot,"Segment",0,0,tw,th,items,current,tcol or P.accent,onPick)
  return full and 0 or th+12
 end
 return 0
end

drawBody = function()
	if not body or not ctx.page then return end
	for _, d in ipairs(body:GetDescendants()) do
		if d:IsA("ScrollingFrame") then ctx.scrollMemory[scrollKey(d.Name)] = d.CanvasPosition end
	end
	T.clear(body)
	if not ctx.data then
		local ring = T.frame(body, "Spinner", bodyW / 2 - 24, bodyH / 2 - 52, 48, 48, nil, 1)
		T.corner(ring, 24)
		local st = T.stroke(ring, P.accent, 5)
		T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 0), T.kp(.7, 1), T.kp(1, 1) }) }, st)
		local tw = game:GetService("TweenService"):Create(ring, TweenInfo.new(.9, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = 360 })
		tw:Play()
		ring.Destroying:Once(function() tw:Cancel() end)
		T.text(body, "Loading", "Carregando seus dados...", 20, bodyH / 2 + 8, bodyW - 40, 32, 20, P.text2, T.CENTER, "title")
		return
	end
	if ctx.page == "Inventory" then Inventory.render(ctx, body, bodyW, bodyH)
	else Menus.render(ctx, body, bodyW, bodyH) end
	local restore = {}
	for _, d in ipairs(body:GetDescendants()) do
		if d:IsA("ScrollingFrame") then
			local pos = ctx.scrollMemory[scrollKey(d.Name)]
			if pos then restore[d] = pos; d.CanvasPosition = pos end
		end
	end
	if next(restore) then
		task.defer(function() for s, pos in pairs(restore) do if s.Parent then s.CanvasPosition = pos end end end)
	end
end

local function windowRect()
 if fullPage() then return virtualW,virtualH,0,0 end
 if ctx.portrait then
  return virtualW-20,virtualH-32,10,16
 elseif ctx.compact then
  return virtualW-28,virtualH-20,14,10
 end
 local ww=math.min(ctx.page=="Summon" and 1460 or 1280,virtualW-104)
 local wh=math.min(ctx.page=="Summon" and 800 or 780,virtualH-90)
 return ww,wh,(virtualW-ww)/2,(virtualH-wh)/2
end

drawWindow = function(animate)
 if not ctx.page then return end
 modalVersion+=1
 T.clear(modalLayer)
 local ww,wh,wx,wy=windowRect()
 local full=fullPage()
 local _,_,pageColor=pageTitle()
 if ctx.page=="Events" then pageColor=P.warning end
 window=T.panel(modalLayer,"Window",wx,wy,ww,wh,{bg=P.bg0,radius=full and 0 or 12,strokeColor=pageColor,strokeWidth=full and 0 or 3})
 window.Active=true
 local shadow
 if full then
  local inset=GuiService:GetGuiInset().Y/scale.Scale
  T.frame(window,"FullBleedTop",0,-inset,ww,inset+1,P.ink,0)
  window.BackgroundColor3=WHITE
  T.gradient(window,Color3.fromRGB(146,86,214),Color3.fromRGB(56,25,104),90)
  T.texture(window,"halftone",.94,WHITE,44)
  local haze=T.image(window,"StageLight",T.Assets.rays,ww*.30,100,ww*.44,wh-100,P.violet,.88)
  local top=T.frame(window,"TopBand",0,0,ww,92,P.ink,0)
  T.fade(top,90,0,.4)
 else
  shadow=T.shadow(window,12,8,.25)
 end
 local bw=full and math.min(330,ww*.3) or math.min(ww-100,640)
 local banner=T.frame(window,"Banner",24,full and 16 or 14,bw,52,nil,1)
 if not full then
  T.slant(banner,"TitlePlate",-8,0,bw,52,pageColor,{top=pageColor,bottom=pageColor:Lerp(P.ink,.16),tilt=20})
  T.texture(banner,"halftone",.88,P.ink,20)
 else
  local mark=T.frame(banner,"PageMark",3,10,25,25,P.accent,0);mark.Rotation=45
  T.frame(mark,"Facet",3,3,9,18,P.text,.5)
 end
 T.text(banner,"Title","",full and 42 or 24,0,bw-(full and 44 or 48),52,full and 32 or 34,P.text,T.LEFT,"display",3)
 T.text(window,"Subtitle","",24,full and 65 or 72,ww-128,22,15,P.text2,T.LEFT,"body",false)
 local close=T.closeButton(window,ww-78,12,60,ctx.close)
 local extra=drawHeader()
 local headH=full and 108 or 100+extra
 bodyW,bodyH=ww-48,wh-headH-(full and 16 or 22)
 body=T.frame(window,"Body",24,headH,bodyW,bodyH,nil,1)
 hud.Visible=not(full or ctx.portrait or ctx.compact)
 drawBody()
 if animate and not full then T.enter(window,.97,.18);if shadow then T.enter(shadow,.97,.18)end end
 if usingGamepad() then task.defer(function() if window and window.Parent then GuiService.SelectedObject=close end end) end
end

-- ---------------------------------------------------------------- HUD
local NAV = {
 {id="Store",label="Loja",icon="store",tip="Picaretas, mochilas e passes"},
 {id="Inventory",label="Unidades",icon="units",key="H",tip="Unidades e equipe"},
 {id="Items",label="Itens",icon="items",key="J",tip="Hats e atributos"},
 {id="Summon",label="Invocar",icon="summon",key="G",tip="Banners de unidades"},
 {id="Areas",label="Viajar",icon="areas",tip="Ilhas de mineração"},
 {id="Quests",label="Missões",icon="quests",tip="Objetivos e recompensas"},
 {id="Events",label="Diário",icon="events",tip="Recompensa diária e coleção"},
 {id="Settings",label="Ajustes",icon="settings",tip="Som, efeitos e códigos"},
}

drawHUD = function()
 T.clear(hud);hudRefs={}
 local portrait,compact=ctx.portrait,ctx.compact
 screen:SetAttribute("BottomReserved",portrait and 184 or 0)
 local margin=portrait and 16 or 24
 -- Recursos ficam juntos e fora da zona central de mineração.
 local row=T.panel(hud,"Currency",(portrait or compact) and margin or (virtualW-400)/2,14,(portrait or compact) and 340 or 400,60,{bg=P.bg0,alpha=.12,strokeColor=P.line,strokeWidth=2})
 hudRefs.wallet=row
 T.icon(row,"coins",12,12,36,36)
 hudRefs.coins=T.text(row,"Coins",ctx.shownCoins and T.format(ctx.shownCoins) or "0",56,22,150,28,26,P.gold,T.LEFT,"number",2)
 T.text(row,"CoinsLabel","MOEDAS",56,6,130,17,12,P.text3,T.LEFT,"label",false)
 local px=(portrait or compact) and 205 or 236
 T.frame(row,"Rule",px-10,14,1,32,P.lineSoft,0)
 T.statIcon(row,"dano",px,18,28,28)
 hudRefs.power=T.text(row,"Power","0",px+36,24,100,24,22,P.text,T.LEFT,"number",2)
 T.text(row,"PowerLabel","PODER",px+36,7,100,17,12,P.text3,T.LEFT,"label",false)
 T.hint(row,"Poder por golpe · moedas obtidas na venda","below")
 hudRefs.buffs=T.scroll(hud,"Buffs",margin,82,(portrait or compact) and math.min(virtualW-32,620) or 620,36,P.violet)
 hudRefs.buffs.ScrollingDirection=Enum.ScrollingDirection.X
 hudRefs.buffs.ScrollBarThickness=3
 hudRefs.buffKeys=""
 local tw=portrait and math.min(virtualW-32,420) or (compact and math.min(290,virtualW-400) or 360)
 local tx=portrait and margin or virtualW-margin-tw
 local ty=portrait and 126 or 14
 local tracker=T.new("TextButton",{Name="Tracker",Text="",BackgroundColor3=P.bg0,BorderSizePixel=0,Position=UDim2.fromOffset(tx,ty),Size=UDim2.fromOffset(tw,100)},hud)
 T.corner(tracker,8);hudRefs.trackerStroke=T.stroke(tracker,P.lineSoft,1)
 hudRefs.areaName=T.text(tracker,"Area","Praça central",14,10,tw-28,22,15,P.accent,T.LEFT,"label",false)
 hudRefs.questText=T.text(tracker,"Quest","Seu próximo objetivo",14,35,tw-28,23,16,P.text,T.LEFT,"body",false)
 hudRefs.questBar=T.progress(tracker,"QuestBar",14,72,tw-100,5,0,P.accent)
 hudRefs.questCount=T.text(tracker,"Count","",tw-84,63,70,23,13,P.text2,T.RIGHT,"number",false)
 T.bindInteraction(tracker,function() ctx.questArea=nil;ctx.open("Quests") end)
 T.hint(tracker,"Objetivo atual · abrir missões","below")
 -- Navegação única: cada atalho ocupa uma posição estável.
 local cols=portrait and 4 or #NAV
 local nw=portrait and math.floor((virtualW-44)/4) or (compact and 72 or 88)
 local nh=portrait and 60 or 74
 local ng=6
 local rows=math.ceil(#NAV/cols)
 local dw=cols*nw+(cols-1)*ng
 local dh=rows*nh+(rows-1)*ng
 local dock=T.panel(hud,"Navigation",(virtualW-dw)/2,virtualH-dh-14,dw,dh,{bg=P.bg0,stroke=false})
 hudRefs.rail={}
 for i,it in ipairs(NAV) do
  local x=((i-1)%cols)*(nw+ng);local y=math.floor((i-1)/cols)*(nh+ng)
  local b=T.new("TextButton",{Name=it.id,Text="",AutoButtonColor=false,BackgroundColor3=P.bg1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(nw,nh)},dock)
  T.corner(b,8)
  local navColor=T.Page[it.id] or P.violet
  b.BackgroundColor3=WHITE;T.gradient(b,P.bg0,navColor:Lerp(P.ink,.70),90)
  T.texture(b,"pattern",.90,navColor,90)
  local rim=T.stroke(b,navColor,2,0)
  local isz=portrait and 28 or 38
  T.icon(b,it.icon,(nw-isz)/2,5,isz,isz)
  T.text(b,"Label",it.label,4,nh-25,nw-8,22,15,P.text,T.CENTER,"label",1.7)
  T.bindInteraction(b,function()
   if it.id=="Inventory" then ctx.collection="pet" end
   ctx.open(it.id)
  end,{onFocus=function(on) rim.Color=on and P.text or navColor end})
  T.hint(b,it.tip..(it.key and " · ["..it.key.."]" or ""),"above")
  hudRefs.rail[it.id]=b
 end
 local bagW=portrait and virtualW-32 or math.min(600,virtualW*.42)
 local bagY=virtualH-dh-58
 local bagH=(portrait or compact) and 52 or 32
 if bagH>32 then bagY-=20 end
 local bag=T.frame(hud,"Bag",(virtualW-bagW)/2,bagY,bagW,bagH,nil,1)
 hudRefs.bagPanel=bag
 hudRefs.bagTrack=T.progress(bag,"Track",0,0,bagW-102,bagH,0,P.accent)
 hudRefs.bag=T.text(hudRefs.bagTrack,"Count","MOCHILA 0 / 0",10,0,bagW-122,bagH,14,P.text,T.LEFT,"label",false)
 hudRefs.sell=T.button(bag,"SellShortcut","Vender",bagW-94,0,94,bagH,P.neutral,function() ctx.open("Forge") end,{size=14})
 T.hint(hudRefs.sell,"Vender minérios com Ignis","above")
 local slot=(portrait or compact) and 52 or 44
 local hotY=(portrait or compact) and bagY-58 or virtualH-70
 hudRefs.hotbar=T.frame(hud,"Hotbar",margin,hotY,6*slot+5*8,slot,nil,1)
 T.text(hud,"TeamLabel","EQUIPE",margin,hotY-21,130,17,11,P.text3,T.LEFT,"label",false)
 hudRefs.signature=nil
 updateHUD()
end

local function nextPickaxe(d)
	local idx = 1
	for i, p in ipairs(Config.Picaretas) do if p.id == d.picareta then idx = i end end
	for i = idx + 1, #Config.Picaretas do
		local p = Config.Picaretas[i]
		if not (d.picaretasCompradas and d.picaretasCompradas[p.id]) then return p, i end
	end
end
local function nextBackpack(d)
	local idx = 1
	for i, m in ipairs(Config.Mochilas) do if m.id == d.mochilaTier then idx = i end end
	return Config.Mochilas[idx + 1]
end
local function nextArea(d)
	for _, a in ipairs(Config.Areas) do if not d.areas[a.id] then return a end end
end
ctx.nextPickaxe, ctx.nextBackpack, ctx.nextArea = nextPickaxe, nextBackpack, nextArea

local function readyQuests(d, areaId)
	local n = 0
	for _, m in ipairs(Config.Missoes[areaId] or {}) do
		local e = d.missoes and d.missoes[m.id]
		if e and e.p >= m.meta and not e.r then n += 1 end
	end
	return n
end

local function setBadge(target, value, col)
	if not target then return end
	if target:GetAttribute("BadgeValue")==tostring(value or "") then return end
	target:SetAttribute("BadgeValue",tostring(value or ""))
	local old = target:FindFirstChild("Badge")
	if old then old:Destroy() end
	if value and value ~= 0 and value ~= "" then
		local b = T.badge(target, target.Size.X.Offset - 20, -10, value, col)
		T.pop(b, 1.35, .32)
	end
end

local function inventorySignature(d)
	local list = { d.picareta or "", d.mochilaTier or "", table.concat(d.equipados or {}, ","), table.concat(d.petsEquipados or {}, ",") }
	for uid, o in pairs(d.petsInv or {}) do table.insert(list, uid .. ":" .. o.id .. ":" .. o.nivel .. ":" .. tostring(o.xp) .. ":" .. tostring(o.apelido)) end
	for uid, o in pairs(d.hatsInv or {}) do table.insert(list, uid .. ":" .. o.id .. ":" .. o.nivel .. ":" .. tostring(o.xp)) end
	table.sort(list)
	return table.concat(list, "|")
end

local function renderBuffs()
	local root = hudRefs.buffs
	local d = ctx.data
	if not root or not d then return false end
	local elapsed = os.clock() - (ctx.dataClock or os.clock())
	local b = d.boosts or {}
	local list = {}
	local coinsLeft = (b.moedas or 0) - elapsed
	local luckLeft = (b.sorte or 0) - elapsed
	if coinsLeft > 0 then table.insert(list, { "BoostCoins", "x2 MOEDAS  " .. T.clock(coinsLeft), P.gold, "coins", "Moedas x2 nas vendas" }) end
	if luckLeft > 0 then table.insert(list, { "BoostLuck", "SORTE  " .. T.clock(luckLeft), P.success, "potion", "Chance de Épico ou melhor x1,5" }) end
	if (d.friendBoost or 0) > 0 then table.insert(list, { "Friends", "AMIGOS +" .. math.floor(d.friendBoost * 100 + .5) .. "%", P.accent, "gift", "Bônus por amigos ativos no servidor" }) end
	if d.passes and d.passes.VIP then table.insert(list, { "VIP", "VIP", P.gold, "vip", "+10% de moedas nas vendas" }) end
	local keys = {}
	for _, it in ipairs(list) do table.insert(keys, it[1]) end
	local sig = table.concat(keys, ",")
	if sig == hudRefs.buffKeys then
		for _, it in ipairs(list) do
			local chip = root:FindFirstChild(it[1])
			local label = chip and chip:FindFirstChild("Label")
			if label then label.Text = it[2] end
		end
	else
		hudRefs.buffKeys = sig
		T.clear(root)
		local x = 0
		for _, it in ipairs(list) do
			local chip, w = T.chip(root, it[1], it[2], x, 0, 32, it[3], { icon = it[4], size = 15, w = it[1]:find("Boost") and 190 or nil })
			T.hint(chip, it[5], "below")
			x += w + 8
		end
  root.CanvasSize=UDim2.fromOffset(math.max(0,x-8),0)
	end
	return coinsLeft > 0 or luckLeft > 0
end

task.spawn(function()
	while alive and screen.Parent do
		task.wait(1)
		if pendingOffer and not ctx.page and not popupOpen and not ctx.summonBusy then local offer=pendingOffer;pendingOffer=nil;ofertaPopup(offer) end
		if ctx.data and hudRefs.buffs and hudRefs.buffs.Parent then renderBuffs() end
	end
end)

updateHUD = function()
	local d = ctx.data
	if not d or not hudRefs.coins then return end
	local coins = d.moeda or 0
	if ctx.shownCoins == nil then
		hudRefs.coins.Text = T.format(coins)
	elseif coins ~= ctx.shownCoins then
		local from, to = ctx.shownCoins, coins
		local hold = ctx.coinHold and math.max(0, ctx.coinHold - os.clock()) or 0
		task.delay(to > from and hold or 0, function()
			if not hudRefs.coins or not hudRefs.coins.Parent then return end
			T.countTo(hudRefs.coins, from, to, T.format, .55)
			floatDelta((to > from and "+" or "-") .. T.format(math.abs(to - from)), to > from and P.success or P.danger)
			T.pop(hudRefs.coins, to > from and 1.12 or 1.05, .3)
		end)
	end
	ctx.shownCoins = coins
	if hudRefs.power then hudRefs.power.Text = T.format(d.dano or 0) end

	-- mochila
	local frac = math.clamp((d.carregado or 0) / math.max(1, d.capacidade or 1), 0, 1)
	local col = frac >= 1 and P.danger or (frac >= .85 and P.warning or P.accent)
	T.setProgress(hudRefs.bagTrack, frac, col, .35)
	hudRefs.bag.Text = "MOCHILA  " .. T.format(d.carregado or 0) .. " / " .. T.format(d.capacidade or 0)
	local full = frac >= .85
	if hudRefs.sellFull ~= full then
		hudRefs.sellFull = full
		T.setTone(hudRefs.sell, full and P.success or P.neutral)
		if full then T.pop(hudRefs.sell, 1.18, .4) end
	end
	if frac >= 1 and not ctx.bagWasFull then T.shake(hudRefs.bagPanel, 8) end
	ctx.bagWasFull = frac >= 1

	-- ilha + missão em destaque
	local areaId = player:GetAttribute("CurrentAreaId") or 0
	local area = Config.areaPorId(areaId)
	local tema = area and Config.Temas[area.tema]
	hudRefs.areaName.Text = T.upper(area and area.nome or "Praça central")
	hudRefs.areaName.TextColor3 = tema and tema.cor or P.accent
	local questArea = (area and d.areas[area.id]) and area.id or nil
	if not questArea then
		for _, a in ipairs(Config.Areas) do if d.areas[a.id] then questArea = a.id end end
	end
	local shown, ready = nil, false
	for _, m in ipairs(Config.Missoes[questArea or 1] or {}) do
		local e = d.missoes and d.missoes[m.id] or { p = 0, r = false }
		if not e.r then
			if e.p >= m.meta then shown, ready = { m, e }, true; break end
			shown = shown or { m, e }
		end
	end
	hudRefs.trackerReady = ready
	if shown then
		local m, e = shown[1], shown[2]
		hudRefs.questText.Text = ready and "✓ MISSÃO PRONTA — RESGATAR" or m.texto
		hudRefs.questText.TextColor3 = ready and P.success or P.text2
		T.setProgress(hudRefs.questBar, e.p / m.meta, ready and P.success or P.warning, .35)
		hudRefs.questCount.Text = T.format(math.min(e.p, m.meta)) .. " / " .. T.format(m.meta)
		hudRefs.questBar.Visible = true
	else
		hudRefs.questText.Text = "Missões desta ilha concluídas"
		hudRefs.questText.TextColor3 = P.text3
		hudRefs.questBar.Visible = false
	end
	hudRefs.trackerStroke.Color = ready and P.success or P.lineSoft

	-- badges
	local totalReady = 0
	for _, a in ipairs(Config.Areas) do if d.areas[a.id] then totalReady += readyQuests(d, a.id) end end
	setBadge(hudRefs.rail.Quests, totalReady, P.danger)
	setBadge(hudRefs.rail.Events, d.daily and d.daily.disponivel and "!" or nil, P.danger)
	local na = nextArea(d)
	setBadge(hudRefs.rail.Areas, na and d.moeda >= na.custo and "!" or nil, P.success)
	local np = nextPickaxe(d)
	local nb = nextBackpack(d)
	setBadge(hudRefs.rail.Pickaxe, np and d.moeda >= np.custo and "▲" or nil, P.success)
	setBadge(hudRefs.rail.Store, ((np and d.moeda >= np.custo) or (nb and d.moeda >= nb.custo)) and "▲" or nil, P.success)

	-- hotbar + picareta (só quando algo muda)
	local signature = inventorySignature(d) .. "|" .. tostring(np and d.moeda >= np.custo)
	if hudRefs.signature == signature then renderBuffs(); return end
	hudRefs.signature = signature
	renderBuffs()
	if hudRefs.pickArt then
		T.clear(hudRefs.pickArt)
		local size = hudRefs.pickArt.Size.X.Offset
		T.preview(hudRefs.pickArt, "pickaxe", d.picareta, 0, 0, size, size, false)
	end
	local hotbar = hudRefs.hotbar
	T.clear(hotbar)
	local slot = hotbar.Size.Y.Offset
	for i = 1, math.clamp(tonumber(d.slotsPets) or 3,1,6) do
		local uid = d.petsEquipados and d.petsEquipados[i]
		local inst = uid and d.petsInv and d.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		local holder = T.new("TextButton", { Name = "Slot" .. i, Text = "", AutoButtonColor = false, BackgroundTransparency = 1, BorderSizePixel = 0,
			Position = UDim2.fromOffset((i - 1) * (slot + 8), 0), Size = UDim2.fromOffset(slot, slot) }, hotbar)
		if def then
			local tile, r = T.tile(holder, "Tile", 0, 0, slot, slot, def.raridade, { radius = 12 })
			local arte = Config.PetArte and Config.PetArte[def.id]
			if arte then
				local img = T.image(tile, "Portrait", arte.busto or arte.corpo, 3, 3, slot - 6, slot - 6)
				img.ScaleType = Enum.ScaleType.Crop
				T.corner(img, 9)
			else
				T.preview(tile, "pet", def.id, 3, 3, slot - 6, slot - 6, false)
			end
			T.text(tile, "Level", "Lv." .. tostring(inst.nivel or 1), 4, 2, slot - 8, 18, 13, WHITE, T.LEFT, "title")
			T.hint(holder, "<b>" .. ((inst.apelido and inst.apelido ~= "") and inst.apelido or def.nome) .. "</b>  <font color=\"#" .. r.cor:ToHex() .. "\">" .. r.nome .. "</font>\nDano +" .. T.format(math.floor(Config.petBonusDano(def, inst.nivel or 1) * 1000 + .5) / 10) .. "%", "above")
		else
			local empty = T.frame(holder, "Empty", 0, 0, slot, slot, P.bg0, .35)
			T.corner(empty, 12)
			T.stroke(empty, P.lineSoft, 2.5)
			T.text(empty, "Plus", "+", 0, 0, slot, slot, 28, P.text3, T.CENTER, "title")
			T.hint(holder, "Slot livre  ·  equipe uma unidade", "above")
		end
		local sc = T.new("UIScale", {}, holder)
		holder.MouseEnter:Connect(function() T.tween(sc, .14, { Scale = 1.09 }, Enum.EasingStyle.Back) end)
		holder.MouseLeave:Connect(function() T.tween(sc, .12, { Scale = 1 }, Enum.EasingStyle.Quad) end)
		holder.Activated:Connect(function()
			T.som("ui_click")
			ctx.collection = "pet"
			ctx.open("Inventory")
			if uid then ctx.selected = uid; drawBody() end
		end)
	end
end

-- ---------------------------------------------------------------- DADOS
local function barrier(part)
	if not ctx.data or not part:IsA("BasePart") or part.Name ~= "Barreira" then return end
	local id = part:GetAttribute("LiberaComArea")
	local unlocked = id and ctx.data.areas[id] == true
	part.CanCollide = not unlocked
	part.Transparency = unlocked and .9 or .65
end

local function completeCollection(data, kind, definitions)
	local known = data.index and data.index[kind]
	if type(known) ~= "table" or #definitions == 0 then return false end
	for _, definition in ipairs(definitions) do if not known[definition.id] then return false end end
	return true
end

local function acceptData(data)
	if type(data) ~= "table" or type(data.hatsInv) ~= "table" or type(data.petsInv) ~= "table" then return end
	local previous, previousClock = ctx.data, ctx.dataClock
	ctx.data = data
	ctx.dataClock = os.clock()
	if not audioHydrated then
		audioHydrated = true
		local preferences = AudioPreferences.sanitize(data.audio)
		for key, value in pairs(preferences) do
			if pendingAudio[key] == nil and not audioWorker then player:SetAttribute(key, value) end
		end
		ctx.audioPersistent = data.audioPersistent == true
		if not audioWorker then audioStatus(ctx.audioPersistent and "profile" or "session") end
	end
	if previous and previous.boosts and data.boosts then
		local elapsed = ctx.dataClock - (previousClock or ctx.dataClock)
		for _, key in ipairs({ "sorte", "moedas" }) do
			local before = math.max(0, (previous.boosts[key] or 0) - elapsed)
			if (data.boosts[key] or 0) > before + 5 then Som.tocar("boost"); break end
		end
	end
	hydrated = true
	updateHUD()
	local areas = workspace:FindFirstChild("Areas")
	local areaSig=table.concat((function() local out={} for k,v in pairs(data.areas or {}) do if v then table.insert(out,tostring(k)) end end table.sort(out);return out end)(),",")
	if areas and ctx.areaSignature~=areaSig then ctx.areaSignature=areaSig;for _,d in ipairs(areas:GetDescendants()) do if d.Name=="Barreira" then barrier(d) end end end
	local signature = inventorySignature(data)
	if signature ~= lastInventorySignature then
		if previous then
			local completed = {}
			for _, collection in ipairs({ { "pets", Config.Pets, "Unidades" }, { "hats", Config.Hats, "Hats" } }) do
				if completeCollection(data, collection[1], collection[2]) and not completeCollection(previous, collection[1], collection[2]) then
					table.insert(completed, collection[3])
				end
			end
			if #completed > 0 then
				-- The existing banner queue waits for reveal/menu closure before the milestone cue.
				Notify.banner({ title = "COLEÇÃO COMPLETA!", subtitle = table.concat(completed, " · ") .. " descobertos no Index",
					color = P.gold, sound = "achievement", big = true, duration = 2.8 })
			end
		end
		lastInventorySignature = signature
		if ctx.page and not ctx.summonBusy then ctx.refresh() end
	elseif ctx.page == "Forge" or ctx.page == "Quests" or ctx.page == "Events" or ctx.page == "Store" or ctx.page == "Areas" then
		if not ctx.summonBusy then ctx.refresh() end
	end
end
connect(R.AtualizarDados.OnClientEvent,function(data) pushVersion += 1; acceptData(data) end)
connect(workspace.DescendantAdded,function(d) if d.Name == "Barreira" then task.defer(barrier, d) end end)

-- nome do minério da ilha atual (feed de coleta)
local function oreName(variante)
	local a = Config.areaPorId(player:GetAttribute("CurrentAreaId") or 0)
	local info = a and Config.infoMinerio(a.tema .. "_" .. (variante or "comum"))
	return info and info.nome or "Minério"
end

connect(R.FeedbackMina.OnClientEvent,function(info)
	if type(info) ~= "table" then return end
	if info.tipo == "hat" then
		local r = T.rar(info.raridade)
		if info.novo then
			Notify.reveal({ kind = "hat", id = info.id, name = info.texto, rarity = info.raridade, tag = "NOVO HAT!",
				subtitle = "Nível " .. tostring(info.nivel or 1) .. "  ·  entra no Index da coleção" })
		else
			Notify.feed("hat:" .. tostring(info.id), info.texto or "Hat", r.cor, 1, { icon = "items" })
			if r.ordem >= 4 then
				Notify.banner({ title = T.upper(r.nome) .. "!", subtitle = info.texto, color = r.cor, sound = false, big = r.ordem >= 6, duration = 1.8 })
			end
		end
	elseif info.tipo == "quebrou" then
		if info.chefe then
			Notify.banner({ title = "CHEFE DERROTADO!", subtitle = "Recompensa para todos que ajudaram", color = P.danger, big = true, duration = 2.4 })
		else
			local r = T.rar(info.variante)
			Notify.feed("ore:" .. tostring(info.variante), oreName(info.variante), r.cor, 1, { ore = info.variante })
			if r.ordem >= 5 then Notify.banner({ title = "MINÉRIO " .. T.upper(r.nome) .. "!", subtitle = oreName(info.variante), color = r.cor, sound = false, duration = 1.6 }) end
			if hudRefs.bagPanel then T.pop(hudRefs.bagPanel, 1.03, .2) end
		end
	elseif info.tipo == "cheia" then
		ctx.toast(info.texto, nil, "warning")
		if hudRefs.bagPanel then T.shake(hudRefs.bagPanel, 7) end
	elseif info.tipo == "bloqueada" then
		ctx.toast(info.texto, nil, "warning")
	elseif info.tipo == "venda" then
		if type(info.ganho) == "number" and info.ganho > 0 and info.ganho < math.huge then
			Som.venda(info.ganho, info.itens)
			ctx.coinBurst(info.ganho)
			ctx.toast(info.texto or ("+" .. T.format(info.ganho) .. " moedas"), nil, "reward")
		end
	elseif info.tipo == "area" then
		local texto = tostring(info.texto or "")
		ctx.toast(texto, nil, (texto:find("moedas") or texto:find("Compra")) and "reward" or "info")
	elseif info.tipo == "comprarArea" then
		ctx.buyArea(info.areaId)
	end
end)
connect(R.AbrirIgnis.OnClientEvent,function() if ctx.page ~= "Forge" then ctx.open("Forge") end end)
connect(R.AbrirLoja.OnClientEvent,function() ctx.storeTab = "Mochilas"; if ctx.page ~= "Store" then ctx.open("Store") else ctx.refresh() end end)
connect(R.AbrirGacha.OnClientEvent,function(id)
	if Config.Gachas[id] then ctx.bannerArea = id; if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end end
end)
connect(player:GetAttributeChangedSignal("CurrentAreaId"),function()
	-- IslandTransition owns arrival audio at the actual transition, not at replication time.
	local id = player:GetAttribute("CurrentAreaId")
	local a = id and Config.areaPorId(id)
	local tema = a and Config.Temas[a.tema]
	Notify.banner({ title = a and a.nome or "Praça Central", subtitle = a and ("ILHA " .. a.id .. "  ·  " .. T.upper(tema.nome)) or "LOBBY  ·  IGNIS, BANNERS E PORTAIS",
		color = tema and tema.cor or P.accent, sound = false, duration = 1.8 })
	updateHUD()
end)
connect(player:GetAttributeChangedSignal("ExpeditionBlurEnabled"),updateBlur)

-- ---------------------------------------------------------------- RESOLUÇÃO
local function resize()
	local v = screen.AbsoluteSize
	if v.X < 1 or v.Y < 1 then return end
	ctx.portrait = v.X < v.Y * .85
	ctx.compact = not ctx.portrait and v.Y < 560
	local s
	if ctx.portrait then s = math.clamp(v.X / 500, .85, 1.25)
	elseif ctx.compact then s = math.max(.85,math.min(v.X / 1180, v.Y / 500))
	else s = math.clamp(math.min(v.X / BASE_W, v.Y / BASE_H), .5, 1.45) end
	scale.Scale = s
	T.uiScale = s
	virtualW, virtualH = v.X / s, v.Y / s
	canvas.Size = UDim2.fromOffset(virtualW, virtualH)
	for _, layer in ipairs({ hud, modalLayer, toastLayer, popupLayer, dialogHost, tipLayer }) do
		layer.Size = UDim2.fromOffset(virtualW, virtualH)
	end
	Notify.toastTop = ctx.portrait and 240 or 126
	drawHUD()
	hud.Visible = not (ctx.page and (fullPage() or ctx.portrait or ctx.compact))
	if ctx.page then drawWindow(false) end
	-- Reflow preserves builder state and input, without closing or shrinking controls.
	if popupOpen and popupState then renderPopup(popupState, true) end
	Notify.relayout()
end
screen:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)

connect(Input.InputBegan,function(input, processed)
	if processed or Input:GetFocusedTextBox() then return end
	local key = input.KeyCode
	if key == Enum.KeyCode.Escape or key==Enum.KeyCode.ButtonB then
		if popupOpen then closePopup() elseif ctx.page then ctx.close() end
	elseif key == Enum.KeyCode.H or key == Enum.KeyCode.B or key==Enum.KeyCode.ButtonY then ctx.collection = "pet"; ctx.open("Inventory")
	elseif key == Enum.KeyCode.J then ctx.open("Items")
	elseif key == Enum.KeyCode.G then ctx.open("Summon") end
end)
screen.Destroying:Connect(function() alive=false;for _,c in ipairs(connections) do c:Disconnect() end;blur:Destroy() end)
resize()

task.spawn(function()
	for attempt = 1, 8 do
		if hydrated then break end
		local version = pushVersion
		local ok, data = pcall(function() return R.PedirDados:InvokeServer() end)
		if ok and version == pushVersion and data then acceptData(data) end
		if not hydrated then task.wait(.5 + attempt * .15) end
	end
	if not hydrated then ctx.toast("Não foi possível carregar seus dados. Reconecte ao jogo.", nil, "error") end
end)
task.spawn(function()
	local images = { T.Assets.icons, T.Assets.header, T.Assets.lobby }
	for _, id in ipairs(T.Assets.areas) do table.insert(images, id) end
	pcall(function() game:GetService("ContentProvider"):PreloadAsync(images) end)
end)
]========],edits={{old=[========[	elseif name == "ResgatarMissao" then
		if not ctx.batchQuestAudio then Som.tocar("quest_complete") end
	elseif name == "ResgatarDaily" or name == "ResgatarCodigo" then
		Som.tocar("reward_banner")
	elseif name ~= "RolarGacha" and name ~= "UITravel" and name ~= "ComprarRobux" then
		Som.tocar("ui_confirm")
	end]========],new=[========[	elseif name == "ResgatarMissao" then
		if not ctx.batchQuestAudio then Som.tocar("quest_complete") end
	elseif name == "ResgatarDaily" or name == "ResgatarCodigo" then
		-- One cue for what the server actually delivered; never infer rarity from the offer.
		local reward = res.audioReward
		if type(reward) ~= "table" then Som.tocar("reward_banner") -- compatible with an older server
		elseif type(reward.raridade) == "string" and Config.Raridades[reward.raridade] then Som.drop(reward.raridade)
		elseif reward.boost == true then Som.tocar("boost")
		elseif type(reward.moedas) == "number" and reward.moedas > 0 then Som.tocar("reward_banner") end
	elseif name ~= "RolarGacha" and name ~= "UITravel" and name ~= "ComprarRobux" then
		Som.tocar("ui_confirm")
	end]========]},{old=[========[		ctx.audioPersistent = data.audioPersistent == true
		if not audioWorker then audioStatus(ctx.audioPersistent and "profile" or "session") end
	end
	if previous and previous.boosts and data.boosts then
		local elapsed = ctx.dataClock - (previousClock or ctx.dataClock)
		for _, key in ipairs({ "sorte", "moedas" }) do
			local before = math.max(0, (previous.boosts[key] or 0) - elapsed)]========],new=[========[		ctx.audioPersistent = data.audioPersistent == true
		if not audioWorker then audioStatus(ctx.audioPersistent and "profile" or "session") end
	end
	local transactionAudio = data.audioContext == "daily" or data.audioContext == "code"
	if not transactionAudio and previous and previous.boosts and data.boosts then
		local elapsed = ctx.dataClock - (previousClock or ctx.dataClock)
		for _, key in ipairs({ "sorte", "moedas" }) do
			local before = math.max(0, (previous.boosts[key] or 0) - elapsed)]========]},{old=[========[			if #completed > 0 then
				-- The existing banner queue waits for reveal/menu closure before the milestone cue.
				Notify.banner({ title = "COLEÇÃO COMPLETA!", subtitle = table.concat(completed, " · ") .. " descobertos no Index",
					color = P.gold, sound = "achievement", big = true, duration = 2.8 })
			end
		end
		lastInventorySignature = signature]========],new=[========[			if #completed > 0 then
				-- The existing banner queue waits for reveal/menu closure before the milestone cue.
				Notify.banner({ title = "COLEÇÃO COMPLETA!", subtitle = table.concat(completed, " · ") .. " descobertos no Index",
					color = P.gold, sound = not transactionAudio and "achievement" or false, big = true, duration = 2.8 })
			end
		end
		lastInventorySignature = signature]========]},{old=[========[	scale.Scale = s
	T.uiScale = s]========],new=[========[	if Input.TouchEnabled then s = math.max(.85, s) end
	scale.Scale = s
	T.uiScale = s]========]}}})
table.insert(specs,{name=[========[StarterPlayer.StarterPlayerScripts.MineracaoVisual]========],source=[========[-- MineracaoVisual: feedback audiovisual do golpe para TODOS os mineradores visiveis.
-- Tudo aqui e so visual e local (nada replica): VFX de impacto por raridade, reacao da rocha, trail da picareta,
-- tremida de camera (so do proprio jogador), numeros de dano e explosao de quebra.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local RunService=game:GetService("RunService")
local Tween=game:GetService("TweenService")
local Debris=game:GetService("Debris")
local player=Players.LocalPlayer
local R=RS:WaitForChild("Remotes")
local Config=require(RS:WaitForChild("Config"))
local swing=require(RS:WaitForChild("MiningSwing"))
local Anim=require(RS:WaitForChild("MiningAnimations"))
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local Som=require(RS:WaitForChild("SomJogo"))

local Theme=require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local function motionEnabled()
 return Theme.motionEnabled and Theme.motionEnabled() or (not Theme.motionEnabled and player:GetAttribute("ReducedMotion")~=true and player:GetAttribute("ExpeditionEffectsEnabled")~=false)
end
local function effectsEnabled() return player:GetAttribute("ExpeditionEffectsEnabled")~=false end
local efeitosAtivos=0
local DIST_VISUAL=90 -- mineradores alem disso nao geram VFX/som local (desempenho)

-- ---------- ESTILO POR RARIDADE DO MINERIO ----------
local TIER={
 comum={cor=Color3.fromRGB(196,176,138),faisca=Color3.fromRGB(255,228,150),poeira=6,faiscas=4,escala=1,shake=.06},
 incomum={cor=Color3.fromRGB(120,210,130),faisca=Color3.fromRGB(170,255,170),poeira=7,faiscas=6,escala=1.05,shake=.07},
 raro={cor=Color3.fromRGB(110,160,255),faisca=Color3.fromRGB(170,210,255),poeira=7,faiscas=8,escala=1.12,shake=.08},
 epica={cor=Color3.fromRGB(190,120,255),faisca=Color3.fromRGB(230,180,255),poeira=8,faiscas=11,escala=1.2,shake=.1,luz=true},
 lendaria={cor=Color3.fromRGB(255,196,70),faisca=Color3.fromRGB(255,240,160),poeira=9,faiscas=15,escala=1.3,shake=.13,luz=true},
 chefe={cor=Color3.fromRGB(255,110,80),faisca=Color3.fromRGB(255,200,140),poeira=10,faiscas=14,escala=1.35,shake=.16,luz=true},
}
local function tierDe(rock)
 if not rock then return TIER.comum end
 if rock:GetAttribute("Chefe") then return TIER.chefe end
 return TIER[rock:GetAttribute("Variante") or "comum"] or TIER.comum
end

local function perto(pos)
 local cam=workspace.CurrentCamera
 return cam and pos and (cam.CFrame.Position-pos).Magnitude<DIST_VISUAL
end

-- ---------- VFX DE IMPACTO ----------
local function impacto(pos,tier,forca)
 if not effectsEnabled() or efeitosAtivos>=16 then return end
 efeitosAtivos+=1
 task.delay(1.05,function() efeitosAtivos=math.max(0,efeitosAtivos-1) end)
 local p=Instance.new("Part") p.Name="ImpactoPicareta" p.Anchored=true p.Transparency=1
 p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local dust=Instance.new("ParticleEmitter")
 dust.Texture="rbxasset://textures/particles/smoke_main.dds" dust.Rate=0
 dust.Color=ColorSequence.new(tier.cor:Lerp(Color3.fromRGB(180,161,128),.5))
 dust.Lifetime=NumberRange.new(.18,.38) dust.Speed=NumberRange.new(2,5.5)
 dust.SpreadAngle=Vector2.new(70,70) dust.Drag=4
 dust.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.35*tier.escala),NumberSequenceKeypoint.new(1,1.5*tier.escala)})
 dust.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.5),NumberSequenceKeypoint.new(1,1)})
 dust.Parent=a dust:Emit(math.floor(tier.poeira*forca))
 local spark=Instance.new("ParticleEmitter")
 spark.Texture="rbxasset://textures/particles/sparkles_main.dds" spark.Rate=0
 spark.Lifetime=NumberRange.new(.1,.24) spark.Speed=NumberRange.new(5,10*tier.escala)
 spark.SpreadAngle=Vector2.new(95,95) spark.LightEmission=.9 spark.Acceleration=Vector3.new(0,-25,0)
 spark.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.26*tier.escala),NumberSequenceKeypoint.new(1,0)})
 spark.Color=ColorSequence.new(tier.faisca)
 spark.Parent=a spark:Emit(math.floor(tier.faiscas*forca))
 local chip=Instance.new("ParticleEmitter")
 chip.Texture="rbxasset://textures/particles/explosion01_core_main.dds" chip.Rate=0
 chip.Lifetime=NumberRange.new(.25,.45) chip.Speed=NumberRange.new(6,11)
 chip.SpreadAngle=Vector2.new(60,60) chip.Acceleration=Vector3.new(0,-40,0) chip.RotSpeed=NumberRange.new(-300,300)
 chip.Size=NumberSequence.new(.14*tier.escala) chip.Color=ColorSequence.new(tier.cor:Lerp(Color3.new(.3,.3,.32),.55))
 chip.Parent=a chip:Emit(math.floor(3*forca))
 if tier.luz then
  local l=Instance.new("PointLight") l.Color=tier.faisca l.Brightness=3 l.Range=9*tier.escala l.Parent=p
  Tween:Create(l,TweenInfo.new(.14),{Brightness=0}):Play()
 end
 Debris:AddItem(p,1)
end

-- ---------- REACAO DA ROCHA ----------
local tremendo={} -- [visual] = {base, inicio, dir, forca}
local function tremerRocha(rock,origem,forca)
 if not motionEnabled() then return end
 local visual=rock and rock.Parent and rock.Parent:FindFirstChild("Visual")
 if not visual or not visual:IsA("Model") then return end
 local st=tremendo[visual]
 local base=st and st.base or visual:GetPivot()
 local dir=origem and Vector3.new(rock.Position.X-origem.X,0,rock.Position.Z-origem.Z) or Vector3.zero
 dir=dir.Magnitude>.01 and dir.Unit or Vector3.new(1,0,0)
 tremendo[visual]={base=base,inicio=os.clock(),dir=dir,forca=forca}
end

-- ---------- CAMERA (so o proprio jogador) ----------
local shake=0
local function tremerCamera(valor) if motionEnabled() then shake=math.min(.22,math.max(shake,valor)) end end

RunService:BindToRenderStep("MineracaoFeedback",Enum.RenderPriority.Camera.Value+1,function(dt)
 local agora=os.clock()
 for visual,st in pairs(tremendo) do
  local a=(agora-st.inicio)/.16
  if not visual.Parent or a>=1 then
   if visual.Parent then visual:PivotTo(st.base) end
   tremendo[visual]=nil
  else
   local k=(1-a)^2*math.sin(a*math.pi*3)
   visual:PivotTo(st.base*CFrame.new(st.dir*.16*st.forca*k)*CFrame.Angles(0,0,math.rad(2.2*st.forca*k)))
  end
 end
 if not motionEnabled() then shake=0 end
 if shake>.002 then
  local cam=workspace.CurrentCamera
  local n=math.noise(agora*38,0,0)
  local n2=math.noise(0,agora*38,0)
  if cam then cam.CFrame=cam.CFrame*CFrame.new(n*shake,n2*shake,0) end
  shake=shake*math.exp(-dt*22)
 end
end)

-- ---------- TRAIL DA PICARETA ----------
local COR_MUNDO={Color3.fromRGB(235,235,240),Color3.fromRGB(120,200,255),Color3.fromRGB(95,230,190),Color3.fromRGB(175,115,255),Color3.fromRGB(80,215,255),Color3.fromRGB(255,165,70)}
local trails=setmetatable({},{__mode="k"})
local function trailDa(tool)
 if trails[tool] and trails[tool].Parent then return trails[tool] end
 local handle=tool:FindFirstChild("Handle")
 if not handle then return nil end
 local cabeca,dist=handle,0
 for _,d in ipairs(tool:GetDescendants()) do
  if d:IsA("BasePart") and d~=handle then
   local x=(d.Position-handle.Position).Magnitude
   if x>dist then cabeca,dist=d,x end
  end
 end
 local eixo=cabeca~=handle and (cabeca.Position-handle.Position) or handle.CFrame.UpVector
 eixo=eixo.Magnitude>.01 and eixo.Unit or Vector3.yAxis
 local a0=Instance.new("Attachment") a0.Name="TrailA" a0.WorldPosition=cabeca.Position-eixo*.4 a0.Parent=cabeca
 local a1=Instance.new("Attachment") a1.Name="TrailB" a1.WorldPosition=cabeca.Position+eixo*.9 a1.Parent=cabeca
 local def=Config.picaretaPorId(tool:GetAttribute("PicaretaId") or "")
 local mundo=def and def.mundo or 1
 local cor=COR_MUNDO[mundo] or COR_MUNDO[1]
 local t=Instance.new("Trail")
 t.Attachment0=a0 t.Attachment1=a1 t.Lifetime=.13+.01*mundo t.MinLength=.04 t.FaceCamera=true
 t.LightEmission=.35+.11*mundo
 t.Color=ColorSequence.new(cor,cor:Lerp(Color3.new(1,1,1),.4))
 t.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.75-.07*mundo),NumberSequenceKeypoint.new(1,1)})
 t.WidthScale=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(1,0)})
 t.Enabled=false t.Parent=cabeca
 trails[tool]=t
 return t
end

-- ---------- NUMEROS DE DANO (UI V2) ----------
-- fonte pesada com contorno, cor pela raridade do minerio e "pop" maior no golpe que quebra
local FONTE_DANO = Theme.F.number or Theme.F.heavy
local TINTA = Theme.P.ink
local numeros=0
local function numero(pos,dano,tier,final)
 if numeros>=9 then return end
 numeros+=1
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos+Vector3.new(math.random()-.5,1.2,math.random()-.5) p.Parent=workspace
 local bb=Instance.new("BillboardGui") bb.Size=UDim2.fromOffset(final and 150 or 122,final and 46 or 36)
 bb.AlwaysOnTop=true bb.MaxDistance=70 bb.Parent=p
 local t=Instance.new("TextLabel") t.Size=UDim2.fromScale(1,1) t.BackgroundTransparency=1
 t.FontFace=FONTE_DANO t.TextScaled=true t.Text=Config.formatar(math.floor(dano+.5))
 t.TextColor3=final and tier.faisca or Color3.new(1,1,1)
 t.Rotation=motionEnabled() and (math.random()-.5)*5 or 0
 t.Parent=bb
 local st=Instance.new("UIStroke") st.Color=TINTA st.Thickness=final and 1.8 or 1.4 st.LineJoinMode=Enum.LineJoinMode.Round st.Parent=t
 local sc=Instance.new("UIScale") sc.Scale=motionEnabled() and (final and 1.35 or 1.15) or 1 sc.Parent=t
 Tween:Create(sc,TweenInfo.new(.14,Enum.EasingStyle.Back),{Scale=1}):Play()
 if motionEnabled() then Tween:Create(p,TweenInfo.new(.62,Enum.EasingStyle.Quad),{Position=p.Position+Vector3.new(0,final and 1.8 or 1.2,0)}):Play() end
 task.delay(.3,function() Tween:Create(t,TweenInfo.new(.32),{TextTransparency=1}):Play() Tween:Create(st,TweenInfo.new(.32),{Transparency=1}):Play() end)
 task.delay(.66,function() p:Destroy() numeros-=1 end)
end

-- ---------- BARRA DE VIDA DA ROCHA ----------
-- rastro branco que persegue a barra (mostra o quanto o golpe tirou) + flash no impacto
local function barraFeedback(rock)
 if not effectsEnabled() then return end
 local bb=rock and rock:FindFirstChild("Vida")
 if not bb then return end
 local barra=bb:FindFirstChild("Barra",true)
 local interno=barra and barra.Parent
 if not barra or not interno then return end
 local rastro=interno:FindFirstChild("Rastro")
 if not rastro then
  rastro=Instance.new("Frame")
  rastro.Name="Rastro" rastro.BorderSizePixel=0 rastro.ZIndex=(barra.ZIndex or 2)-1
  rastro.BackgroundColor3=Color3.fromRGB(255,236,236) rastro.Size=barra.Size rastro.Position=barra.Position
  local c=Instance.new("UICorner") c.CornerRadius=UDim.new(0,8) c.Parent=rastro
  rastro.Parent=interno
 end
 task.delay(.1,function()
  if rastro.Parent and barra.Parent then Tween:Create(rastro,TweenInfo.new(.28,Enum.EasingStyle.Quad),{Size=barra.Size}):Play() end
 end)
 local flash=interno:FindFirstChild("Flash")
 if not flash then
  flash=Instance.new("Frame") flash.Name="Flash" flash.BorderSizePixel=0 flash.ZIndex=(barra.ZIndex or 2)+1
  flash.BackgroundColor3=Color3.new(1,1,1) flash.Size=UDim2.fromScale(1,1) flash.BackgroundTransparency=1
  local c=Instance.new("UICorner") c.CornerRadius=UDim.new(0,8) c.Parent=flash
  flash.Parent=interno
 end
 flash.BackgroundTransparency=.55
 Tween:Create(flash,TweenInfo.new(.18),{BackgroundTransparency=1}):Play()
end

-- ---------- QUEBRA ----------
local function explosao(pos,tier)
 if not effectsEnabled() or not perto(pos) or efeitosAtivos>=16 then return end
 efeitosAtivos+=1
 task.delay(1.25,function() efeitosAtivos=math.max(0,efeitosAtivos-1) end)
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local e=Instance.new("ParticleEmitter")
 e.Texture="rbxasset://textures/particles/sparkles_main.dds" e.Rate=0
 e.Lifetime=NumberRange.new(.3,.6) e.Speed=NumberRange.new(10,20*tier.escala) e.SpreadAngle=Vector2.new(180,180)
 e.Drag=3 e.LightEmission=1 e.Color=ColorSequence.new(tier.faisca,tier.cor)
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.5*tier.escala),NumberSequenceKeypoint.new(1,0)})
 e.Parent=a e:Emit(math.floor(10*tier.escala^2))
 -- Fragmentos locais pequenos, sem física nem colisão: a quebra termina antes da coleta.
 if motionEnabled() then
  local count=tier.escala>=1.2 and 7 or 4
  for i=1,count do
   local fragment=Instance.new("Part")
   fragment.Name="FragmentoMinerio" fragment.Anchored=true fragment.CanCollide=false fragment.CanQuery=false fragment.CanTouch=false
   fragment.Material=Enum.Material.SmoothPlastic fragment.Color=tier.cor
   fragment.Size=Vector3.one*(.13+math.random()*.16)*tier.escala
   fragment.CFrame=CFrame.new(pos)*CFrame.Angles(math.random()*3,math.random()*3,math.random()*3) fragment.Parent=p
   local angle=(i/count)*math.pi*2
   local apex=pos+Vector3.new(math.cos(angle)*1.1,1.1+math.random()*.6,math.sin(angle)*1.1)*tier.escala
   Tween:Create(fragment,TweenInfo.new(.14,Enum.EasingStyle.Quad,Enum.EasingDirection.Out),{Position=apex}):Play()
   task.delay(.14,function()
    if fragment.Parent then Tween:Create(fragment,TweenInfo.new(.23,Enum.EasingStyle.Quad,Enum.EasingDirection.In),{Position=apex+Vector3.new(math.cos(angle),-1.3,math.sin(angle)),Transparency=1,Size=Vector3.one*.04}):Play() end
   end)
  end
 end
 local l=Instance.new("PointLight") l.Color=tier.faisca l.Brightness=4*tier.escala l.Range=14*tier.escala l.Parent=p
 Tween:Create(l,TweenInfo.new(.25),{Brightness=0}):Play()
 Debris:AddItem(p,1.2)
end

-- ---------- EVENTOS ----------
local function tocarImpacto(miner,c,rock,position)
 local root=c and c:FindFirstChild("HumanoidRootPart")
 local tier=tierDe(rock)
 local golpe=c and c:GetAttribute("MiningComboGolpe")
 local forca=golpe=="vertical" and 1.35 or (golpe=="lateral" and .9 or 1)
 impacto(position,tier,forca)
 tremerRocha(rock,root and root.Position,forca*(rock and rock:GetAttribute("Chefe") and .5 or 1))
 local ehLocal=miner==player
 local def=c and c:FindFirstChild("Picareta") and Config.picaretaPorId(c.Picareta:GetAttribute("PicaretaId") or "")
 Som.hit(rock,{pos=position,remote=not ehLocal,heavy=def and def.mundo>=3,auto=ehLocal and player:GetAttribute("HoldMode")==true})
 if ehLocal then tremerCamera(tier.shake*forca) barraFeedback(rock) end
end
-- A strike is identified by the server start timestamp. Never deduplicate by a broad time window.
local strikes={} -- bounded per-player history
local function strike(miner,id)
 local history=strikes[miner]
 if not history then history={} strikes[miner]=history end
 local now=os.clock()
 for key,value in pairs(history) do if now-value.at>3 then history[key]=nil end end
 if not history[id] then history[id]={at=now} end
 return history[id]
end
Players.PlayerRemoving:Connect(function(miner) strikes[miner]=nil end)
swing.MarkerReached:Connect(function(c,name,rock,startedAt,oldTool)
 if name=='Cancelled' then
  local trail=oldTool and oldTool:FindFirstChild('MiningTrail',true)
  if trail and trail:IsA('Trail') then trail.Enabled=false end
  if oldTool then for _,v in ipairs(oldTool:GetDescendants()) do if v:IsA('Trail') then v.Enabled=false end end end
  local miner=Players:GetPlayerFromCharacter(c)
  local state=miner and strike(miner,startedAt)
  if state and state.confirmedPosition and not state.played and perto(state.confirmedPosition) then
   state.played=true tocarImpacto(miner,c,rock,state.confirmedPosition)
  end
  return
 end
 local miner=Players:GetPlayerFromCharacter(c)
 local root=c:FindFirstChild("HumanoidRootPart")
 if not miner or not root then return end
 local tool=c:FindFirstChild("Picareta")
 local trail=tool and trailDa(tool)
 if name=="SwingEnd" then if trail then trail.Enabled=false end return end
 if not tool or not perto(root.Position) then return end
 local state=strike(miner,startedAt)
 if name=="SwingStart" then
  if trail then trail.Enabled=effectsEnabled() end
  Som.tocar("whoosh",{pos=root.Position,remote=miner~=player,auto=miner==player and player:GetAttribute("HoldMode")==true})
 elseif name=="Hit" and not state.played then
  local position=state.confirmedPosition
  if not position and Geometry.valid(rock) and Geometry.canReach(c,rock,Geometry.Reach+.5) then
   local handle=tool:FindFirstChild("Handle")
   local head=handle and (handle.CFrame*Vector3.new(0,Anim.CABECA_Y,0)) or Geometry.contact(rock,root.Position)
   position=Geometry.surface(rock,head)
  end
  if position then state.played=true tocarImpacto(miner,c,rock,position) end
 end
end)
R:WaitForChild("AnimarPicareta").OnClientEvent:Connect(function(miner,rock,startedAt,isImpact,position,strikeId)
 local c=miner and miner.Character
 if not c then return end
 if isImpact then
  if not position or not perto(position) then return end
  local id=strikeId or startedAt
  local state=strike(miner,id)
  if state.played then return end
  state.confirmedPosition=position
  local active=swing.Ativo(c)
  if active and active.time==id and not active.markers.Hit and workspace:GetServerTimeNow()-id<Anim.CONTATO+.12 then return end
  state.played=true tocarImpacto(miner,c,rock,position)
 else
  swing.Play(c,rock,startedAt)
 end
end)

R.FeedbackMina.OnClientEvent:Connect(function(info)
 if type(info)~="table" then return end
 if info.tipo=="golpe" then
  if info.pos then numero(info.pos,info.dano or 0,TIER[info.chefe and "chefe" or info.variante or "comum"] or TIER.comum,info.quebrou) end
 elseif info.tipo=="quebrou" then
  local tier=TIER[info.variante or "comum"] or TIER.comum
  if info.pos then explosao(info.pos,tier) end
  Som.quebra(info.variante,info.pos)
  if not info.chefe then Som.coleta(info.pos) end
  tremerCamera(tier.shake*1.6)
 elseif info.tipo=="hat" then
  if info.audioContext~="daily" and info.audioContext~="code" then Som.drop(info.raridade) end
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then
  Som.tocar("ui_erro")
 end
end)
]========],base=[========[-- MineracaoVisual: feedback audiovisual do golpe para TODOS os mineradores visiveis.
-- Tudo aqui e so visual e local (nada replica): VFX de impacto por raridade, reacao da rocha, trail da picareta,
-- tremida de camera (so do proprio jogador), numeros de dano e explosao de quebra.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local RunService=game:GetService("RunService")
local Tween=game:GetService("TweenService")
local Debris=game:GetService("Debris")
local player=Players.LocalPlayer
local R=RS:WaitForChild("Remotes")
local Config=require(RS:WaitForChild("Config"))
local swing=require(RS:WaitForChild("MiningSwing"))
local Anim=require(RS:WaitForChild("MiningAnimations"))
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local Som=require(RS:WaitForChild("SomJogo"))

local Theme=require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local function motionEnabled()
 return Theme.motionEnabled and Theme.motionEnabled() or (not Theme.motionEnabled and player:GetAttribute("ReducedMotion")~=true and player:GetAttribute("ExpeditionEffectsEnabled")~=false)
end
local function effectsEnabled() return player:GetAttribute("ExpeditionEffectsEnabled")~=false end
local efeitosAtivos=0
local DIST_VISUAL=90 -- mineradores alem disso nao geram VFX/som local (desempenho)

-- ---------- ESTILO POR RARIDADE DO MINERIO ----------
local TIER={
 comum={cor=Color3.fromRGB(196,176,138),faisca=Color3.fromRGB(255,228,150),poeira=6,faiscas=4,escala=1,shake=.06},
 incomum={cor=Color3.fromRGB(120,210,130),faisca=Color3.fromRGB(170,255,170),poeira=7,faiscas=6,escala=1.05,shake=.07},
 raro={cor=Color3.fromRGB(110,160,255),faisca=Color3.fromRGB(170,210,255),poeira=7,faiscas=8,escala=1.12,shake=.08},
 epica={cor=Color3.fromRGB(190,120,255),faisca=Color3.fromRGB(230,180,255),poeira=8,faiscas=11,escala=1.2,shake=.1,luz=true},
 lendaria={cor=Color3.fromRGB(255,196,70),faisca=Color3.fromRGB(255,240,160),poeira=9,faiscas=15,escala=1.3,shake=.13,luz=true},
 chefe={cor=Color3.fromRGB(255,110,80),faisca=Color3.fromRGB(255,200,140),poeira=10,faiscas=14,escala=1.35,shake=.16,luz=true},
}
local function tierDe(rock)
 if not rock then return TIER.comum end
 if rock:GetAttribute("Chefe") then return TIER.chefe end
 return TIER[rock:GetAttribute("Variante") or "comum"] or TIER.comum
end

local function perto(pos)
 local cam=workspace.CurrentCamera
 return cam and pos and (cam.CFrame.Position-pos).Magnitude<DIST_VISUAL
end

-- ---------- VFX DE IMPACTO ----------
local function impacto(pos,tier,forca)
 if not effectsEnabled() or efeitosAtivos>=16 then return end
 efeitosAtivos+=1
 task.delay(1.05,function() efeitosAtivos=math.max(0,efeitosAtivos-1) end)
 local p=Instance.new("Part") p.Name="ImpactoPicareta" p.Anchored=true p.Transparency=1
 p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local dust=Instance.new("ParticleEmitter")
 dust.Texture="rbxasset://textures/particles/smoke_main.dds" dust.Rate=0
 dust.Color=ColorSequence.new(tier.cor:Lerp(Color3.fromRGB(180,161,128),.5))
 dust.Lifetime=NumberRange.new(.18,.38) dust.Speed=NumberRange.new(2,5.5)
 dust.SpreadAngle=Vector2.new(70,70) dust.Drag=4
 dust.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.35*tier.escala),NumberSequenceKeypoint.new(1,1.5*tier.escala)})
 dust.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.5),NumberSequenceKeypoint.new(1,1)})
 dust.Parent=a dust:Emit(math.floor(tier.poeira*forca))
 local spark=Instance.new("ParticleEmitter")
 spark.Texture="rbxasset://textures/particles/sparkles_main.dds" spark.Rate=0
 spark.Lifetime=NumberRange.new(.1,.24) spark.Speed=NumberRange.new(5,10*tier.escala)
 spark.SpreadAngle=Vector2.new(95,95) spark.LightEmission=.9 spark.Acceleration=Vector3.new(0,-25,0)
 spark.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.26*tier.escala),NumberSequenceKeypoint.new(1,0)})
 spark.Color=ColorSequence.new(tier.faisca)
 spark.Parent=a spark:Emit(math.floor(tier.faiscas*forca))
 local chip=Instance.new("ParticleEmitter")
 chip.Texture="rbxasset://textures/particles/explosion01_core_main.dds" chip.Rate=0
 chip.Lifetime=NumberRange.new(.25,.45) chip.Speed=NumberRange.new(6,11)
 chip.SpreadAngle=Vector2.new(60,60) chip.Acceleration=Vector3.new(0,-40,0) chip.RotSpeed=NumberRange.new(-300,300)
 chip.Size=NumberSequence.new(.14*tier.escala) chip.Color=ColorSequence.new(tier.cor:Lerp(Color3.new(.3,.3,.32),.55))
 chip.Parent=a chip:Emit(math.floor(3*forca))
 if tier.luz then
  local l=Instance.new("PointLight") l.Color=tier.faisca l.Brightness=3 l.Range=9*tier.escala l.Parent=p
  Tween:Create(l,TweenInfo.new(.14),{Brightness=0}):Play()
 end
 Debris:AddItem(p,1)
end

-- ---------- REACAO DA ROCHA ----------
local tremendo={} -- [visual] = {base, inicio, dir, forca}
local function tremerRocha(rock,origem,forca)
 if not motionEnabled() then return end
 local visual=rock and rock.Parent and rock.Parent:FindFirstChild("Visual")
 if not visual or not visual:IsA("Model") then return end
 local st=tremendo[visual]
 local base=st and st.base or visual:GetPivot()
 local dir=origem and Vector3.new(rock.Position.X-origem.X,0,rock.Position.Z-origem.Z) or Vector3.zero
 dir=dir.Magnitude>.01 and dir.Unit or Vector3.new(1,0,0)
 tremendo[visual]={base=base,inicio=os.clock(),dir=dir,forca=forca}
end

-- ---------- CAMERA (so o proprio jogador) ----------
local shake=0
local function tremerCamera(valor) if motionEnabled() then shake=math.min(.22,math.max(shake,valor)) end end

RunService:BindToRenderStep("MineracaoFeedback",Enum.RenderPriority.Camera.Value+1,function(dt)
 local agora=os.clock()
 for visual,st in pairs(tremendo) do
  local a=(agora-st.inicio)/.16
  if not visual.Parent or a>=1 then
   if visual.Parent then visual:PivotTo(st.base) end
   tremendo[visual]=nil
  else
   local k=(1-a)^2*math.sin(a*math.pi*3)
   visual:PivotTo(st.base*CFrame.new(st.dir*.16*st.forca*k)*CFrame.Angles(0,0,math.rad(2.2*st.forca*k)))
  end
 end
 if not motionEnabled() then shake=0 end
 if shake>.002 then
  local cam=workspace.CurrentCamera
  local n=math.noise(agora*38,0,0)
  local n2=math.noise(0,agora*38,0)
  if cam then cam.CFrame=cam.CFrame*CFrame.new(n*shake,n2*shake,0) end
  shake=shake*math.exp(-dt*22)
 end
end)

-- ---------- TRAIL DA PICARETA ----------
local COR_MUNDO={Color3.fromRGB(235,235,240),Color3.fromRGB(120,200,255),Color3.fromRGB(95,230,190),Color3.fromRGB(175,115,255),Color3.fromRGB(80,215,255),Color3.fromRGB(255,165,70)}
local trails=setmetatable({},{__mode="k"})
local function trailDa(tool)
 if trails[tool] and trails[tool].Parent then return trails[tool] end
 local handle=tool:FindFirstChild("Handle")
 if not handle then return nil end
 local cabeca,dist=handle,0
 for _,d in ipairs(tool:GetDescendants()) do
  if d:IsA("BasePart") and d~=handle then
   local x=(d.Position-handle.Position).Magnitude
   if x>dist then cabeca,dist=d,x end
  end
 end
 local eixo=cabeca~=handle and (cabeca.Position-handle.Position) or handle.CFrame.UpVector
 eixo=eixo.Magnitude>.01 and eixo.Unit or Vector3.yAxis
 local a0=Instance.new("Attachment") a0.Name="TrailA" a0.WorldPosition=cabeca.Position-eixo*.4 a0.Parent=cabeca
 local a1=Instance.new("Attachment") a1.Name="TrailB" a1.WorldPosition=cabeca.Position+eixo*.9 a1.Parent=cabeca
 local def=Config.picaretaPorId(tool:GetAttribute("PicaretaId") or "")
 local mundo=def and def.mundo or 1
 local cor=COR_MUNDO[mundo] or COR_MUNDO[1]
 local t=Instance.new("Trail")
 t.Attachment0=a0 t.Attachment1=a1 t.Lifetime=.13+.01*mundo t.MinLength=.04 t.FaceCamera=true
 t.LightEmission=.35+.11*mundo
 t.Color=ColorSequence.new(cor,cor:Lerp(Color3.new(1,1,1),.4))
 t.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.75-.07*mundo),NumberSequenceKeypoint.new(1,1)})
 t.WidthScale=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(1,0)})
 t.Enabled=false t.Parent=cabeca
 trails[tool]=t
 return t
end

-- ---------- NUMEROS DE DANO (UI V2) ----------
-- fonte pesada com contorno, cor pela raridade do minerio e "pop" maior no golpe que quebra
local FONTE_DANO = Theme.F.number or Theme.F.heavy
local TINTA = Theme.P.ink
local numeros=0
local function numero(pos,dano,tier,final)
 if numeros>=9 then return end
 numeros+=1
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos+Vector3.new(math.random()-.5,1.2,math.random()-.5) p.Parent=workspace
 local bb=Instance.new("BillboardGui") bb.Size=UDim2.fromOffset(final and 150 or 122,final and 46 or 36)
 bb.AlwaysOnTop=true bb.MaxDistance=70 bb.Parent=p
 local t=Instance.new("TextLabel") t.Size=UDim2.fromScale(1,1) t.BackgroundTransparency=1
 t.FontFace=FONTE_DANO t.TextScaled=true t.Text=Config.formatar(math.floor(dano+.5))
 t.TextColor3=final and tier.faisca or Color3.new(1,1,1)
 t.Rotation=motionEnabled() and (math.random()-.5)*5 or 0
 t.Parent=bb
 local st=Instance.new("UIStroke") st.Color=TINTA st.Thickness=final and 1.8 or 1.4 st.LineJoinMode=Enum.LineJoinMode.Round st.Parent=t
 local sc=Instance.new("UIScale") sc.Scale=motionEnabled() and (final and 1.35 or 1.15) or 1 sc.Parent=t
 Tween:Create(sc,TweenInfo.new(.14,Enum.EasingStyle.Back),{Scale=1}):Play()
 if motionEnabled() then Tween:Create(p,TweenInfo.new(.62,Enum.EasingStyle.Quad),{Position=p.Position+Vector3.new(0,final and 1.8 or 1.2,0)}):Play() end
 task.delay(.3,function() Tween:Create(t,TweenInfo.new(.32),{TextTransparency=1}):Play() Tween:Create(st,TweenInfo.new(.32),{Transparency=1}):Play() end)
 task.delay(.66,function() p:Destroy() numeros-=1 end)
end

-- ---------- BARRA DE VIDA DA ROCHA ----------
-- rastro branco que persegue a barra (mostra o quanto o golpe tirou) + flash no impacto
local function barraFeedback(rock)
 if not effectsEnabled() then return end
 local bb=rock and rock:FindFirstChild("Vida")
 if not bb then return end
 local barra=bb:FindFirstChild("Barra",true)
 local interno=barra and barra.Parent
 if not barra or not interno then return end
 local rastro=interno:FindFirstChild("Rastro")
 if not rastro then
  rastro=Instance.new("Frame")
  rastro.Name="Rastro" rastro.BorderSizePixel=0 rastro.ZIndex=(barra.ZIndex or 2)-1
  rastro.BackgroundColor3=Color3.fromRGB(255,236,236) rastro.Size=barra.Size rastro.Position=barra.Position
  local c=Instance.new("UICorner") c.CornerRadius=UDim.new(0,8) c.Parent=rastro
  rastro.Parent=interno
 end
 task.delay(.1,function()
  if rastro.Parent and barra.Parent then Tween:Create(rastro,TweenInfo.new(.28,Enum.EasingStyle.Quad),{Size=barra.Size}):Play() end
 end)
 local flash=interno:FindFirstChild("Flash")
 if not flash then
  flash=Instance.new("Frame") flash.Name="Flash" flash.BorderSizePixel=0 flash.ZIndex=(barra.ZIndex or 2)+1
  flash.BackgroundColor3=Color3.new(1,1,1) flash.Size=UDim2.fromScale(1,1) flash.BackgroundTransparency=1
  local c=Instance.new("UICorner") c.CornerRadius=UDim.new(0,8) c.Parent=flash
  flash.Parent=interno
 end
 flash.BackgroundTransparency=.55
 Tween:Create(flash,TweenInfo.new(.18),{BackgroundTransparency=1}):Play()
end

-- ---------- QUEBRA ----------
local function explosao(pos,tier)
 if not effectsEnabled() or not perto(pos) or efeitosAtivos>=16 then return end
 efeitosAtivos+=1
 task.delay(1.25,function() efeitosAtivos=math.max(0,efeitosAtivos-1) end)
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local e=Instance.new("ParticleEmitter")
 e.Texture="rbxasset://textures/particles/sparkles_main.dds" e.Rate=0
 e.Lifetime=NumberRange.new(.3,.6) e.Speed=NumberRange.new(10,20*tier.escala) e.SpreadAngle=Vector2.new(180,180)
 e.Drag=3 e.LightEmission=1 e.Color=ColorSequence.new(tier.faisca,tier.cor)
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.5*tier.escala),NumberSequenceKeypoint.new(1,0)})
 e.Parent=a e:Emit(math.floor(10*tier.escala^2))
 -- Fragmentos locais pequenos, sem física nem colisão: a quebra termina antes da coleta.
 if motionEnabled() then
  local count=tier.escala>=1.2 and 7 or 4
  for i=1,count do
   local fragment=Instance.new("Part")
   fragment.Name="FragmentoMinerio" fragment.Anchored=true fragment.CanCollide=false fragment.CanQuery=false fragment.CanTouch=false
   fragment.Material=Enum.Material.SmoothPlastic fragment.Color=tier.cor
   fragment.Size=Vector3.one*(.13+math.random()*.16)*tier.escala
   fragment.CFrame=CFrame.new(pos)*CFrame.Angles(math.random()*3,math.random()*3,math.random()*3) fragment.Parent=p
   local angle=(i/count)*math.pi*2
   local apex=pos+Vector3.new(math.cos(angle)*1.1,1.1+math.random()*.6,math.sin(angle)*1.1)*tier.escala
   Tween:Create(fragment,TweenInfo.new(.14,Enum.EasingStyle.Quad,Enum.EasingDirection.Out),{Position=apex}):Play()
   task.delay(.14,function()
    if fragment.Parent then Tween:Create(fragment,TweenInfo.new(.23,Enum.EasingStyle.Quad,Enum.EasingDirection.In),{Position=apex+Vector3.new(math.cos(angle),-1.3,math.sin(angle)),Transparency=1,Size=Vector3.one*.04}):Play() end
   end)
  end
 end
 local l=Instance.new("PointLight") l.Color=tier.faisca l.Brightness=4*tier.escala l.Range=14*tier.escala l.Parent=p
 Tween:Create(l,TweenInfo.new(.25),{Brightness=0}):Play()
 Debris:AddItem(p,1.2)
end

-- ---------- EVENTOS ----------
local function tocarImpacto(miner,c,rock,position)
 local root=c and c:FindFirstChild("HumanoidRootPart")
 local tier=tierDe(rock)
 local golpe=c and c:GetAttribute("MiningComboGolpe")
 local forca=golpe=="vertical" and 1.35 or (golpe=="lateral" and .9 or 1)
 impacto(position,tier,forca)
 tremerRocha(rock,root and root.Position,forca*(rock and rock:GetAttribute("Chefe") and .5 or 1))
 local ehLocal=miner==player
 local def=c and c:FindFirstChild("Picareta") and Config.picaretaPorId(c.Picareta:GetAttribute("PicaretaId") or "")
 Som.hit(rock,{pos=position,remote=not ehLocal,heavy=def and def.mundo>=3,auto=ehLocal and player:GetAttribute("HoldMode")==true})
 if ehLocal then tremerCamera(tier.shake*forca) barraFeedback(rock) end
end
-- A strike is identified by the server start timestamp. Never deduplicate by a broad time window.
local strikes={} -- bounded per-player history
local function strike(miner,id)
 local history=strikes[miner]
 if not history then history={} strikes[miner]=history end
 local now=os.clock()
 for key,value in pairs(history) do if now-value.at>3 then history[key]=nil end end
 if not history[id] then history[id]={at=now} end
 return history[id]
end
Players.PlayerRemoving:Connect(function(miner) strikes[miner]=nil end)
swing.MarkerReached:Connect(function(c,name,rock,startedAt,oldTool)
 if name=='Cancelled' then
  local trail=oldTool and oldTool:FindFirstChild('MiningTrail',true)
  if trail and trail:IsA('Trail') then trail.Enabled=false end
  if oldTool then for _,v in ipairs(oldTool:GetDescendants()) do if v:IsA('Trail') then v.Enabled=false end end end
  local miner=Players:GetPlayerFromCharacter(c)
  local state=miner and strike(miner,startedAt)
  if state and state.confirmedPosition and not state.played and perto(state.confirmedPosition) then
   state.played=true tocarImpacto(miner,c,rock,state.confirmedPosition)
  end
  return
 end
 local miner=Players:GetPlayerFromCharacter(c)
 local root=c:FindFirstChild("HumanoidRootPart")
 if not miner or not root then return end
 local tool=c:FindFirstChild("Picareta")
 local trail=tool and trailDa(tool)
 if name=="SwingEnd" then if trail then trail.Enabled=false end return end
 if not tool or not perto(root.Position) then return end
 local state=strike(miner,startedAt)
 if name=="SwingStart" then
  if trail then trail.Enabled=effectsEnabled() end
  Som.tocar("whoosh",{pos=root.Position,remote=miner~=player,auto=miner==player and player:GetAttribute("HoldMode")==true})
 elseif name=="Hit" and not state.played then
  local position=state.confirmedPosition
  if not position and Geometry.valid(rock) and Geometry.canReach(c,rock,Geometry.Reach+.5) then
   local handle=tool:FindFirstChild("Handle")
   local head=handle and (handle.CFrame*Vector3.new(0,Anim.CABECA_Y,0)) or Geometry.contact(rock,root.Position)
   position=Geometry.surface(rock,head)
  end
  if position then state.played=true tocarImpacto(miner,c,rock,position) end
 end
end)
R:WaitForChild("AnimarPicareta").OnClientEvent:Connect(function(miner,rock,startedAt,isImpact,position,strikeId)
 local c=miner and miner.Character
 if not c then return end
 if isImpact then
  if not position or not perto(position) then return end
  local id=strikeId or startedAt
  local state=strike(miner,id)
  if state.played then return end
  state.confirmedPosition=position
  local active=swing.Ativo(c)
  if active and active.time==id and not active.markers.Hit and workspace:GetServerTimeNow()-id<Anim.CONTATO+.12 then return end
  state.played=true tocarImpacto(miner,c,rock,position)
 else
  swing.Play(c,rock,startedAt)
 end
end)

R.FeedbackMina.OnClientEvent:Connect(function(info)
 if type(info)~="table" then return end
 if info.tipo=="golpe" then
  if info.pos then numero(info.pos,info.dano or 0,TIER[info.chefe and "chefe" or info.variante or "comum"] or TIER.comum,info.quebrou) end
 elseif info.tipo=="quebrou" then
  local tier=TIER[info.variante or "comum"] or TIER.comum
  if info.pos then explosao(info.pos,tier) end
  Som.quebra(info.variante,info.pos)
  if not info.chefe then Som.coleta(info.pos) end
  tremerCamera(tier.shake*1.6)
 elseif info.tipo=="hat" then
  Som.drop(info.raridade)
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then
  Som.tocar("ui_erro")
 end
end)

]========],edits={{old=[========[  if not info.chefe then Som.coleta(info.pos) end
  tremerCamera(tier.shake*1.6)
 elseif info.tipo=="hat" then
  Som.drop(info.raridade)
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then
  Som.tocar("ui_erro")
 end]========],new=[========[  if not info.chefe then Som.coleta(info.pos) end
  tremerCamera(tier.shake*1.6)
 elseif info.tipo=="hat" then
  if info.audioContext~="daily" and info.audioContext~="code" then Som.drop(info.raridade) end
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then
  Som.tocar("ui_erro")
 end]========]}}})
local failures={} local prepared={}
for _,s in ipairs(specs) do
 local ok,err=pcall(function()
  local p=assert(resolve(s.name),'Missing script '..s.name)
  local current=norm(p.Source)
  if s.base then assert(current==norm(s.base),'Source changed since reviewed base: '..s.name) end
  local target=s.source
  if #s.edits>0 then
   target=current
   for _,e in ipairs(s.edits) do target=replaceOnce(target,e.old,e.new) end
   assert(norm(target)==norm(s.source),'Patched source differs from reviewed output: '..s.name)
  end
  assert(loadstring(target), 'Compile failed: '..s.name)
  table.insert(prepared,{p=p,target=target,name=s.name})
 end)
 if not ok then table.insert(failures,tostring(err)) end
end
if #failures>0 then return H:JSONEncode({installed=false,failures=failures}) end
local done={}
for _,s in ipairs(prepared) do s.p.Source=s.target table.insert(done,{path=s.name,bytes=#s.target}) end
return H:JSONEncode({installed=true,files=done,mode='Edit'})

