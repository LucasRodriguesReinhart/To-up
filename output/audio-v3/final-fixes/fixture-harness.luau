-- No Roblox services, remotes, datastore, or live transactions. Original and revised
-- source run against identical fresh profiles and a deterministic Random.new stub.
local function deep(value)
	if type(value) ~= "table" then return value end
	local result = {}
	for key, item in pairs(value) do result[key] = deep(item) end
	return result
end
local function canonical(value)
	if type(value) ~= "table" then return tostring(value) end
	local keys = {}
	for key in pairs(value) do table.insert(keys, key) end
	table.sort(keys, function(a,b) return tostring(a)<tostring(b) end)
	local out = {}
	for _, key in ipairs(keys) do table.insert(out,tostring(key).."="..canonical(value[key])) end
	return "{"..table.concat(out,",").."}"
end
local function compile(source, name, env)
	local chunk, err = loadstring(source, name)
	assert(chunk, err)
	setfenv(chunk, setmetatable(env or {}, { __index = getfenv() }))
	return chunk()
end

local scenarios = {
	{ name="daily2",day=2,event="drop_raro" },
	{ name="daily5",day=5,event="drop_raro" },
	{ name="daily7",day=7,event="drop_epico" },
	{ name="daily3_multi_hat",day=3,event="drop_raro" },
	{ name="daily7_fallback",day=7,fallback=true,event="drop_raro" },
	{ name="daily7_inventory_full",day=7,full=true,event="none" },
	{ name="daily2_inventory_full",day=2,full=true,event="boost" },
	{ name="code_coins",code="LANCAMENTO",event="reward_banner" },
	{ name="code_hat",code="BEMVINDO",event="drop_raro" },
	{ name="code_pet",code="NARUTO",event="drop_raro" },
	{ name="code_full",code="NARUTO",full=true,event="none" },
	{ name="code_invalid",code="INVALID",event="none" },
	{ name="code_duplicate",code="LANCAMENTO",duplicate=true,event="none" },
}
local function world(scenario, revised)
	local profile = { moeda=1000,hatsInv={},petsInv={},hatSeq=0,petSeq=0,equipados={},petsEquipados={},index={hats={},pets={}},
		daily={dia=scenario.day or 1,ultimo=0},boosts={sorte=0,moedas=0},codigos={},tel={},__invCheio={} }
	if scenario.duplicate then profile.codigos[scenario.code]=true end
	local captures={feedback={},sync={},telemetry={},random={},saveRequests=0}
	local player={Name="OfflineFixture",UserId=0}
	local hats={
		chakra_106490972825856={id="chakra_106490972825856",nome="Rare hat",raridade="raro",mundo=1},
		epic_hat={id="epic_hat",nome="Epic hat",raridade="epico",mundo=1},
	}
	local pets={naruto={id="naruto",nome="Rare pet",raridade="raro"},epic_pet={id="epic_pet",nome="Epic pet",raridade="epico"}}
	local Config={
		RAR_INDICE={comum=1,incomum=2,raro=3,epico=4,lendario=5,mitico=6,secreto=7},
		RAR_IDS={"comum","incomum","raro","epico","lendario","mitico","secreto"},
		HAT_NIVEL_DROP_MAX=20,INVENTARIO_MAX=50,PET_INVENTARIO_MAX=50,
		Gachas={[1]={}},Areas={{tema="chakra"}},Eco={RENDA_EXTRA=1.1,MINUTOS_NO_MUNDO_MEDIO={10},MOEDAS_POR_MINUTO_MEDIO={100}},
		DAILY={
			{itens={{tipo="moedas",minutos=10}}},
			{itens={{tipo="boost",boost="sorte",minutos=15},{tipo="moedas",minutos=10},{tipo="pet",raridade="raro"}}},
			{itens={{tipo="hats",raridade="raro",qtd=3}}},
			{itens={{tipo="moedas",minutos=20}}},
			{itens={{tipo="boost",boost="moedas",minutos=15},{tipo="hats",raridade="raro",qtd=1}}},
			{itens={{tipo="hats",raridade="epico",qtd=1}}},
			{itens={{tipo="pet",raridade="epico"}}},
		},
	}
	Config.Raridades={}
	for key in pairs(Config.RAR_INDICE) do Config.Raridades[key]={nome=key} end
	Config.hatPorId=function(id) return hats[id] end
	Config.petPorId=function(id) return pets[id] end
	Config.formatar=tostring
	Config.moedasDeMinutos=function(_,minutes) return minutes*100 end
	Config.hatsDoTema=function(_,rarity) return {rarity=="epico" and hats.epic_hat or hats.chakra_106490972825856} end
	Config.petsDaRaridade=function(rarity)
		if rarity=="epico" then return scenario.fallback and {} or {pets.epic_pet} end
		return {pets.naruto}
	end
	local PD={get=function()return profile end,diaUTC=function()return 100 end,maiorArea=function()return 1 end,
		levelBonus=function()return 0 end,slots=function()return 3 end,slotsPets=function()return 3 end,
		capacidadeHats=function()return scenario.full and 0 or 50 end,capacidadePets=function()return scenario.full and 0 or 50 end,
		adicionarBoost=function(p,kind,minutes) p.boosts[kind]=math.max(p.boosts[kind],5000)+minutes*60 end,
	}
	local function count(items) local n=0 for _ in pairs(items) do n+=1 end return n end
	PD.totalHats=function(p)return count(p.hatsInv)end
	PD.totalPets=function(p)return count(p.petsInv)end
	PD.novoHat=function(p,id,level) p.hatSeq+=1;local uid="h"..p.hatSeq;p.hatsInv[uid]={id=id,nivel=level};p.index.hats[id]=true;return uid end
	PD.novoPet=function(p,id,level) p.petSeq+=1;local uid="p"..p.petSeq;p.petsInv[uid]={id=id,nivel=level};p.index.pets[id]=true;return uid end
	PD.sincronizar=function(_,context) table.insert(captures.sync,{profile=deep(profile),audioContext=context}) end
	PD.salvar=function()captures.saveRequests+=1;return true end
	local function log(kind,...)table.insert(captures.telemetry,{kind=kind,args=table.pack(...)})end
	local Telemetria={evento=function(_,_,...)log("evento",...)end,marco=function(_,_,...)log("marco",...)end,economia=function(_,_,...)log("economia",...)end}
	local services={Config=Config,PlayerData=PD,Economia={},Telemetria=Telemetria,Ofertas={inventarioCheio=function()end},HatVisual={aplicar=function()end}}
	local parent={}
	for _,name in ipairs({"PlayerData","Economia","Telemetria","Ofertas","HatVisual","Recompensas"})do parent[name]=name end
	local RS={Config="Config",Remotes={FeedbackMina={FireClient=function(_,_,info)table.insert(captures.feedback,deep(info))end}}}
	local env={game={GetService=function(_,service)
		assert(service=="ReplicatedStorage" or service=="Players","REAL SERVICE FORBIDDEN: "..service)
		if service=="ReplicatedStorage"then return RS end
		return {PlayerRemoving={Connect=function()end}}
	end},script={Parent=parent},require=function(name)assert(services[name],name);return services[name]end,
		Random={new=function()return {NextInteger=function(_,a,b)table.insert(captures.random,{a,b});return a end}end},
		task={spawn=function(fn,...)fn(...)end,defer=function(fn,...)fn(...)end},os={time=function()return 5000 end,clock=function()return 100 end}}
	local suffix=revised and "After" or "Before"
	services.Recompensas=compile(SOURCES["Recompensas"..suffix],"Recompensas"..suffix,env)
	local moduleName=scenario.day and "Retencao" or "Codigos"
	local module=compile(SOURCES[moduleName..suffix],moduleName..suffix,env)
	local result=scenario.day and module.resgatarDaily(player) or module.resgatar(player,scenario.code)
	return {profile=profile,captures=captures,result=result,config=Config}
end

local choose=compile(SOURCES.ChooseCue,"actual-client-cue")
local boostGate=compile(SOURCES.BoostGate,"actual-client-boost-gate")
local hatGate=compile(SOURCES.HatGate,"actual-mining-hat-gate")
local function gameplay(world)
	local copy={profile=deep(world.profile),captures=deep(world.captures),result=deep(world.result)}
	copy.result.audioReward=nil
	for _,f in ipairs(copy.captures.feedback)do f.audioContext=nil end
	for _,sync in ipairs(copy.captures.sync)do sync.audioContext=nil end
	return canonical(copy)
end
for _,scenario in ipairs(scenarios) do
	local original,revised=world(scenario,false),world(scenario,true)
	assert(gameplay(original)==gameplay(revised),"Gameplay changed: "..scenario.name)
	assert(revised.profile.audioContext==nil and revised.profile.audioReward==nil,"Metadata persisted in profile")
	local played={}
	local sound={tocar=function(event)table.insert(played,event)end,drop=function(rarity)table.insert(played,"drop_"..rarity)end}
	for _,feedback in ipairs(revised.captures.feedback)do if feedback.tipo=="hat"then hatGate(feedback,sound)end end
	for _,snap in ipairs(revised.captures.sync)do
		boostGate({audioContext=snap.audioContext,boosts=snap.profile.boosts},{boosts={sorte=0,moedas=0}},98,{dataClock=100},sound)
	end
	if revised.result.ok then choose(revised.result,sound,revised.config) end
	local actual=#played==0 and "none" or table.concat(played,",")
	assert(actual==scenario.event,"Cue mismatch "..scenario.name..": "..actual)
	assert(#played<=1,"Duplicate transaction celebration: "..scenario.name)
	print("CASE|"..scenario.name.."|"..actual.."|"..canonical(revised.profile))
end

-- Ordinary purchases/boosts and mined hats keep their original independent route.
do
	local sounds={}
	local sound={tocar=function(event)table.insert(sounds,event)end,drop=function(r)table.insert(sounds,"drop_"..r)end}
	boostGate({boosts={sorte=900,moedas=0}},{boosts={sorte=0,moedas=0}},98,{dataClock=100},sound)
	hatGate({audioContext="mineracao",raridade="mitico"},sound)
	assert(table.concat(sounds,",")=="boost,drop_mitico")
	print("PASS|purchase_boost_and_mined_hat_preserved")
end

-- Exercise the actual preference updater with a newer local value and stale server patch.
do
	local Preferences=compile(SOURCES.Preferences,"actual-preferences")
	local player={attribute=.90,SetAttribute=function()error("Server update replicated a stale mix attribute")end}
	local profile={audio=Preferences.sanitize(),moeda=777}
	local env={AudioPreferences=Preferences,cache={[player]=profile},PlayerData={audioPersistente=function()return true end}}
	local updater=compile(SOURCES.UpdateAudio.."\nreturn PlayerData.atualizarAudio","actual-preference-update",env)
	local first=updater(player,{AudioMasterVolume=.85,MusicEnabled=false,moeda=99999})
	assert(first.ok and first.audio.AudioMasterVolume==.85 and first.audio.MusicEnabled==false)
	assert(player.attribute==.90 and profile.moeda==777 and profile.audio.moeda==nil)
	local second=updater(player,{AudioMasterVolume=.90,AudioMusicVolume=0/0,AudioSFXVolume=math.huge,AudioUIVolume=-5})
	assert(second.audio.AudioMasterVolume==.90 and second.audio.AudioMusicVolume==.60 and second.audio.AudioSFXVolume==.85 and second.audio.AudioUIVolume==0)
	print("PASS|late_patch_no_attribute_rollback_and_whitelist")
end
print("ALL_FIXTURES_PASSED|13")
