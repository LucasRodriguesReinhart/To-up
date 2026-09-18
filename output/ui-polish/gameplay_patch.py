from pathlib import Path
root=Path(__file__).parent/'src'
def read(k): return (root/(k.replace('.','/')+'.lua')).read_text(encoding='utf-8')
def write(k,s):
 p=root/(k.replace('.','/')+'.lua');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
k='ReplicatedStorage.MonetizacaoConfig';s=read(k).replace('M.PASSES = {','''M.MULTI_OPEN_COUNT = 4
M.PASSES = {
 {chave="MultiOpen",nome="Multi Open",id=0,robux=0,desc="Abra 4 estrelas simultaneamente. Cada estrela usa o custo normal de moedas."},
 {chave="Speed2x",nome="2X Speed",id=0,robux=0,desc="Escolha de 1x a 2x sua velocidade normal nas configurações."},''');write(k,s)
k='ServerScriptService.Core.PlayerData';s=read(k)
s=s.replace('ui = UIPreferences.sanitize(),','ui = UIPreferences.sanitize(),\n        movementSpeed = 1,')
s=s.replace('p.ui = UIPreferences.sanitize(p.ui)','p.ui = UIPreferences.sanitize(p.ui)\n p.movementSpeed=PlayerData.sanitizarVelocidade(p.movementSpeed) or 1')
s=s.replace('function PlayerData.velocidade(perfil)\n\treturn Config.VELOCIDADE_BASE + PlayerData.velPets(perfil)\nend','''function PlayerData.sanitizarVelocidade(value)
 if type(value)~="number" or value~=value or math.abs(value)==math.huge then return nil end
 return math.clamp(math.round(value*4)/4,1,2)
end
function PlayerData.velocidade(perfil)
 local allowed=perfil.__player and Passes.possui(perfil.__player,"Speed2x")
 return (Config.VELOCIDADE_BASE + PlayerData.velPets(perfil))*(allowed and (PlayerData.sanitizarVelocidade(perfil.movementSpeed) or 1) or 1)
end
function PlayerData.atualizarVelocidade(player,value)
 local p=cache[player];local parsed=PlayerData.sanitizarVelocidade(value)
 if not p or not parsed then return {ok=false,msg="Velocidade inválida."} end
 local maximum=Passes.possui(player,"Speed2x") and 2 or 1
 if value<1 or value>maximum then return {ok=false,msg="2X Speed é necessário para aumentar o limite."} end
 p.movementSpeed=parsed;p.__player=player
 PlayerData.sincronizar(player)
 return {ok=true,value=parsed,maximum=maximum}
end''')
s=s.replace('uiPersistent = PlayerData.audioPersistente(perfil),','uiPersistent = PlayerData.audioPersistente(perfil),\n        movementSpeed = PlayerData.sanitizarVelocidade(perfil.movementSpeed) or 1,')
s=s.replace('snap.passes = Passes.todos(player)','snap.passes = Passes.todos(player)\n player:SetAttribute("VIPOwned",snap.passes.VIP==true)')
write(k,s)
k='ServerScriptService.Core.Main';s=read(k)
s=s.replace('R.RolarGacha.OnServerInvoke = function(player, areaId)\n\treturn GachaService.rolar(player, areaId)\nend','''R.RolarGacha.OnServerInvoke = function(player, areaId, mode, requestId)
 return GachaService.abrir(player,areaId,mode,requestId)
end
remoteNovo("ConcluirReveal","RemoteEvent").OnServerEvent:Connect(function(player,id) GachaService.apresentado(player,id) end)
local speedRate={}
remoteNovo("AtualizarVelocidade","RemoteFunction").OnServerInvoke=function(player,value)
 if os.clock()-(speedRate[player] or -math.huge)<.2 then return {ok=false,msg="Aguarde um instante."} end
 speedRate[player]=os.clock();return PlayerData.atualizarVelocidade(player,value)
end
Players.PlayerRemoving:Connect(function(p) speedRate[p]=nil end)''')
write(k,s)
k='ServerScriptService.Core.GachaService';s=read(k);a=s.index('function GachaService.rolar');s=s[:a]+'''local Passes=require(script.Parent.Passes)
local Mon=require(RS.MonetizacaoConfig)
local sessions={}
local locks={}
function GachaService.quantidade(mode,owned)
 if mode=="single" then return 1 end
 if mode=="multi" and owned then return Mon.MULTI_OPEN_COUNT end
 return nil
end
function GachaService.apresentado(player,id)
 local state=sessions[player]
 if not state or state.id~=id or state.presented then return end
 state.presented=true
 local perfil=PlayerData.get(player);if not perfil then return end
 for _,result in ipairs(state.result.results) do
  if result.novo and perfil.petsInv[result.uid] and #perfil.petsEquipados<PlayerData.slotsPets(perfil) then
   table.insert(perfil.petsEquipados,result.uid)
  end
 end
 PlayerData.sincronizar(player)
end
local function transaction(player,areaId,mode,requestId)
 local perfil=PlayerData.get(player)
 if not perfil then return {ok=false,msg="Perfil não carregado."} end
 perfil.__player=player
 local count=GachaService.quantidade(mode,mode=="multi" and Passes.possui(player,"MultiOpen"))
 if not count then return {ok=false,msg="Multi Open exige o passe para abrir 4 estrelas.",premium="MultiOpen"} end
 local g=Config.Gachas[areaId];local area=Config.areaPorId(areaId)
 if not g or not area or not perfil.areas[areaId] then return {ok=false,msg="Desbloqueie esta ilha primeiro."} end
 local char=player.Character;local hrp=char and char:FindFirstChild("HumanoidRootPart")
 local machines=workspace:FindFirstChild("Gachas");local machine=machines and machines:FindFirstChild("Gacha_"..area.tema)
 local pad=machine and machine:FindFirstChild("PadGacha")
 if not hrp or not pad or (hrp.Position-pad.Position).Magnitude>60 then return {ok=false,msg="Chegue perto do banner."} end
 -- Resolve all yielding ownership calls before the currency/inventory transaction.
 local capacity=PlayerData.capacidadePets(perfil)
 local dist=Config.distGacha(areaId,Economia.luckyMult(player,perfil))
 local pools={}
 for r=1,#Config.RAR_IDS do
  local index=r;local candidates=Config.petsDaRaridade(Config.RAR_IDS[index],areaId)
  while #candidates==0 and index>1 do index-=1;candidates=Config.petsDaRaridade(Config.RAR_IDS[index],areaId) end
  if #candidates==0 then return {ok=false,msg="Banner indisponível."} end
  pools[r]={items=candidates,rarity=Config.RAR_IDS[index]}
 end
 local free=(perfil.giros or 0)==0;local cost=g.custo*(count-(free and 1 or 0))
 if perfil.moeda<cost then return {ok=false,msg="Moedas insuficientes."} end
 if PlayerData.totalPets(perfil)+count>capacity then return {ok=false,msg="Libere "..count.." espaços no inventário para abrir."} end
 local result={ok=true,requestId=requestId,results={},count=count,cost=cost}
 perfil.moeda-=cost
 for i=1,count do
  local rarityIndex=GachaService.sortear(perfil,dist)
  local pool=pools[rarityIndex];local pet=pool.items[rnd:NextInteger(1,#pool.items)]
  local isNew=not perfil.index.pets[pet.id];local uid=PlayerData.novoPet(perfil,pet.id,1)
  table.insert(result.results,{petId=pet.id,uid=uid,nome=pet.nome,raridade=pool.rarity,novo=isNew,gratis=free and i==1})
 end
 PlayerData.progredirMissao(perfil,areaId,"invocar",count)
 sessions[player]={id=requestId,result=result,presented=false}
 ultimo[player]=os.clock()
 -- Result is already granted. Only its presentation/auto-equip waits for the impact.
 task.delay(8,function() GachaService.apresentado(player,requestId) end)
 pcall(function()
  if cost>0 then Telemetria.economia(player,perfil,false,cost,"Shop","gacha_"..areaId) end
  Telemetria.marco(player,perfil,"FirstPet",{origem=free and "giro_gratis" or "gacha"})
  Telemetria.evento(player,perfil,"GachaBatch",count,{area=areaId,mode=mode})
 end)
 return result
end
function GachaService.abrir(player,areaId,mode,requestId)
 if type(areaId)~="number" or areaId~=areaId or type(requestId)~="string" or #requestId<8 or #requestId>64 then return {ok=false,msg="Pedido inválido."} end
 local previous=sessions[player]
 if previous and previous.id==requestId then return previous.result end
 if locks[player] or (previous and not previous.presented) or os.clock()-(ultimo[player] or -math.huge)<1.1 then return {ok=false,msg="Aguarde a abertura terminar."} end
 locks[player]=true
 local ok,res=pcall(transaction,player,areaId,mode,requestId)
 locks[player]=nil
 if not ok then warn("[Gacha] "..tostring(res));return {ok=false,msg="Não foi possível abrir agora."} end
 return res
end
function GachaService.rolar(player,areaId)
 return GachaService.abrir(player,areaId,"single",game:GetService("HttpService"):GenerateGUID(false))
end
function GachaService.limpar(player) ultimo[player]=nil;sessions[player]=nil;locks[player]=nil end
return GachaService
''';write(k,s)
print('Server batch and movement patched')
