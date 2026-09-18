local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Economia = require(script.Parent.Economia)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)

-- Gacha de personagens (economia v3.1):
--  * 1o giro da conta: gratis e garantido Raro ou melhor
--  * pity Lendario+ e Mitico+ com contadores independentes; o de Lendario zera ao sair Lendario+ (sorte ou pity)
--  * Lucky/boost multiplicam exatamente a chance de Epico+ (Config.aplicarLucky)
--  * raridade sem personagem na area cai para a de baixo (Config.distGacha)
local GachaService = {}
local rnd = Random.new()
local ultimo = {}
local COOLDOWN = 0.6

local I_LENDARIO = Config.RAR_INDICE.lendario
local I_MITICO = Config.RAR_INDICE.mitico
local I_MIN_PRIMEIRO = Config.PRIMEIRO_GIRO_MIN_RAR + 1 -- valor da economia vem indexado em 0 (simulador)

-- sorteio puro (testavel): devolve o indice de raridade e atualiza o estado de pity
function GachaService.sortear(estado, dist, r0)
	local primeiro = (estado.giros or 0) == 0
	estado.giros = (estado.giros or 0) + 1
	estado.pity.l += 1
	estado.pity.m += 1
	local r = r0 or Config.sortearIndice(rnd, dist)
	if primeiro then r = math.max(r, I_MIN_PRIMEIRO) end
	if estado.pity.m >= Config.PITY_MITICO and r < I_MITICO then r = I_MITICO end
	if estado.pity.l >= Config.PITY_LENDARIO and r < I_LENDARIO then r = I_LENDARIO end
	if r >= I_LENDARIO then estado.pity.l = 0 end
	if r >= I_MITICO then estado.pity.m = 0 end
	return r
end

local Passes=require(script.Parent.Passes)
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
