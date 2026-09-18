if not game:GetService('RunService'):IsStudio() then return end
local RS=game.ReplicatedStorage
local PD=require(script.Parent.PlayerData)
local G=require(script.Parent.GachaService)
local Passes=require(script.Parent.Passes)
local Config=require(RS.Config)
local results={}
local function check(name,ok) assert(ok,name);table.insert(results,name) end
local attempts=0
repeat task.wait(.1);attempts+=1 until workspace:FindFirstChild('Gachas') or attempts>150
local machine=workspace.Gachas:FindFirstChild('Gacha_'..Config.Areas[1].tema)
local pad=machine and machine:FindFirstChild('PadGacha');assert(pad,'Banner missing')
local model=Instance.new('Model');local root=Instance.new('Part');root.Name='HumanoidRootPart';root.Position=pad.Position;root.Parent=model
local fake={UserId=-70707,Name='IsolatedUITest',Character=model,GetAttribute=function() return nil end}
local profile=PD.carregarVazio();profile.__player=fake;profile.moeda=1e9;profile.areas[1]=true;profile.giros=1
local owned={};local originalOwn,originalGet,originalSync=Passes.possui,PD.get,PD.sincronizar
Passes.possui=function(p,key) if p==fake then return owned[key]==true end;return originalOwn(p,key) end
PD.get=function(p) if p==fake then return profile end;return originalGet(p) end
PD.sincronizar=function(p,...) if p~=fake then return originalSync(p,...) end end
local ok,err=pcall(function()
 check('single count',G.quantidade('single',false)==1)
 check('multi requires pass',G.quantidade('multi',false)==nil)
 check('multi grants four',G.quantidade('multi',true)==4)
 check('legacy count rejected',G.quantidade(10,true)==nil)
 check('NaN speed rejected',PD.sanitizarVelocidade(0/0)==nil)
 check('infinite speed rejected',PD.sanitizarVelocidade(math.huge)==nil)
 check('table speed rejected',PD.sanitizarVelocidade({})==nil)
 check('speed step',PD.sanitizarVelocidade(1.26)==1.25)
 profile.movementSpeed=2;local normal=PD.velocidade(profile)
 check('normal player retains normal speed',normal==Config.VELOCIDADE_BASE)
 owned.Speed2x=true;check('owner double limit',PD.velocidade(profile)==normal*2)
 profile.movementSpeed=1.25;check('owner selected multiplier',PD.velocidade(profile)==normal*1.25)
 local before=PD.totalPets(profile);local coins=profile.moeda
 check('multi server denial',not G.abrir(fake,1,'multi','no-pass-001').ok)
 check('denial changes nothing',PD.totalPets(profile)==before and profile.moeda==coins)
 owned.MultiOpen=true;profile.moeda=0
 check('insufficient funds',not G.abrir(fake,1,'multi','no-coins-001').ok)
 profile.moeda=coins;root.Position=pad.Position+Vector3.new(500,0,0)
 check('real distance enforced',not G.abrir(fake,1,'multi','far-away-001').ok)
 root.Position=pad.Position
 local result=G.abrir(fake,1,'multi','multi-open-001')
 check('four results one request',result.ok and #result.results==4)
 check('four granted exactly',PD.totalPets(profile)==before+4)
 check('batch exact cost',profile.moeda==coins-Config.Gachas[1].custo*4)
 check('not autoequipped before reveal',#profile.petsEquipados==0)
 local repeatResult=G.abrir(fake,1,'multi','multi-open-001')
 check('duplicate id is idempotent',repeatResult==result and PD.totalPets(profile)==before+4)
 check('spam rejected',not G.abrir(fake,1,'single','spam-open-001').ok)
 G.apresentado(fake,'wrong-id');check('wrong ack ignored',#profile.petsEquipados==0)
 G.apresentado(fake,result.requestId);local equipped=#profile.petsEquipados
 G.apresentado(fake,result.requestId);check('ack idempotent',#profile.petsEquipados==equipped)
 G.limpar(fake);profile.moeda=coins
 local oldCapacity=PD.capacidadePets;PD.capacidadePets=function(p) if p==profile then return PD.totalPets(p)+3 end;return oldCapacity(p) end
 local full=G.abrir(fake,1,'multi','capacity-001');PD.capacidadePets=oldCapacity
 check('batch capacity checked before charging',not full.ok and profile.moeda==coins)
end)
G.limpar(fake);Passes.possui=originalOwn;PD.get=originalGet;PD.sincronizar=originalSync;model:Destroy()
script:SetAttribute('Passed',#results);script:SetAttribute('Results',game:GetService('HttpService'):JSONEncode(results))
if not ok then error(err) end
print('[UI Polish QA] '..#results..' checks passed')
