-- Server-owned area membership and recovery. No position or area supplied by a client is trusted.
-- 2026-09-25 (Ilha 2 Dragon Ball): a area passa a ser decidida por REGIAO. Cada Areas.AreaN pode declarar
-- BoundsCenter (Vector3, so X/Z contam) + BoundsHalfSize; sem BoundsCenter vale Config.centro (como antes). A area
-- atual tem preferencia enquanto o jogador continuar dentro da caixa dela (histerese nas regioes que se tocam, p.ex. a
-- cabeceira da Ilha 1 e a ponte da Ilha 2). Fora de toda caixa: faixas de z como antes (mundo em linha reta).
-- SafeMaxY (atributo opcional): altura maxima para salvar posicao segura (ilhas altas, como a Ilha 2).
-- Persistentes: a area atual + as vizinhas (regioes encostadas) ficam carregadas para o jogador (ver persist).
local Players=game:GetService('Players')
local RunService=game:GetService('RunService')
local Config=require(game.ReplicatedStorage.Config)
local PlayerData=require(script.Parent.PlayerData)
local Travel={}
local states={} local loading={} local started=false
local lobby=Vector3.new(0,3.5,104) -- Vila-Forja (lobby ativo desde 2026-09-24): plataforma do spawn, de frente para a Forja (-Z); a ponte sul leva a Vila da Folha
local function destination(id)
 if id==0 then return lobby end
 local model=workspace.Areas:FindFirstChild('Area'..id)
 return model and model:GetAttribute('EntryPosition')
end
-- caixa (centro, meia-medida) de uma area, ou nil se o modelo nao declara BoundsHalfSize
local function box(id)
 local areas=workspace:FindFirstChild('Areas')
 local m=areas and areas:FindFirstChild('Area'..id)
 if not m then return nil end
 local half=m:GetAttribute('BoundsHalfSize')
 if typeof(half)~='Vector3' then return nil end
 local c=m:GetAttribute('BoundsCenter')
 if typeof(c)~='Vector3' then local a=Config.areaPorId(id) c=a and a.centro end
 if not c then return nil end
 return c,half,m
end
local function inside(id,pos)
 local c,half=box(id)
 if not c then return false end
 local o=pos-c
 return math.abs(o.X)<half.X and math.abs(o.Z)<half.Z and pos.Y>-12 and pos.Y<half.Y+5
end
-- lobby: mesma regra de antes (a checagem de altura antiga ficou comentada por engano no original; mantida assim)
local function lobbyAt(pos)
 return math.abs(pos.X)<190 and pos.Z>-300 and pos.Z<190
end
-- area de uma posicao: a preferida (atual) se ainda contem o ponto; depois qualquer caixa; depois o lobby; depois z
local function areaAt(pos,prefer)
 if prefer and prefer>0 and inside(prefer,pos) then return prefer end
 for _,a in Config.Areas do if inside(a.id,pos) then return a.id end end
 if lobbyAt(pos) then return 0 end
 if pos.Z>190 then return math.clamp(math.floor((pos.Z+210)/420),1,6) end
 return 0
end
Travel.areaAt=areaAt
-- VIZINHAS: a area atual e as que encostam nela (mesma regra do IslandVisibility do cliente) ficam PERSISTENTES para o
-- jogador (carregadas inteiras): a ilha ao lado nunca some nem vira vazio na travessia a pe.
local GAP=60
local LOBBY_C,LOBBY_H=Vector3.new(0,0,-55),Vector3.new(190,0,245)
local function region(id)
 if id==0 then return LOBBY_C,LOBBY_H end
 local c,h=box(id) return c,h
end
local function touches(a,b)
 local ca,ha=region(a) local cb,hb=region(b)
 if not ca or not cb then return false end
 return math.abs(ca.X-cb.X)<=ha.X+hb.X+GAP and math.abs(ca.Z-cb.Z)<=ha.Z+hb.Z+GAP
end
local persisted={}
local function persist(player,id)
 local want={}
 for _,a in Config.Areas do if a.id==id or touches(a.id,id) then want[a.id]=true end end
 local have=persisted[player] or {}
 for aid in have do if not want[aid] then local m=workspace.Areas:FindFirstChild('Area'..aid) if m then pcall(function() m:RemovePersistentPlayer(player) end) end end end
 for aid in want do if not have[aid] then local m=workspace.Areas:FindFirstChild('Area'..aid) if m then pcall(function() m:AddPersistentPlayer(player) end) end end end
 persisted[player]=want
end
local function unpersist(player)
 for aid in persisted[player] or {} do local m=workspace.Areas:FindFirstChild('Area'..aid) if m then pcall(function() m:RemovePersistentPlayer(player) end) end end
 persisted[player]=nil
end
Travel.vizinhas=function(id) local t={} for _,a in Config.Areas do if a.id~=id and touches(a.id,id) then table.insert(t,a.id) end end return t end
local function put(player,pos,id)
 local char=player.Character local root=char and char:FindFirstChild('HumanoidRootPart')
 if not root then return false end
 root.AssemblyLinearVelocity=Vector3.zero root.AssemblyAngularVelocity=Vector3.zero
 local look=Vector3.new(0,0,id==0 and -30 or 30) -- lobby (id 0): nasce olhando a Forja (-Z); areas: +Z como antes
 local model=id>0 and workspace.Areas:FindFirstChild('Area'..id)
 local ef=model and model:GetAttribute('EntryForward')          -- ilha girada (Ilha 2): olha para dentro dela
 if typeof(ef)=='Vector3' and ef.Magnitude>0.1 then look=Vector3.new(ef.X,0,ef.Z).Unit*30 end
 root.CFrame=CFrame.lookAt(pos,pos+look)
 return true
end
function Travel.teleport(player,pos)
 if typeof(pos)~='Vector3' then return false end
 if loading[player] then return false end
 local id=0
 for _,a in Config.Areas do if inside(a.id,pos) then id=a.id break end end
 if id==0 then for _,a in Config.Areas do if (pos-a.centro).Magnitude<240 then id=a.id break end end end
 if id>0 then local data=PlayerData.get(player) if not data or not data.areas[id] then return false end end
 local char=player.Character local root=char and char:FindFirstChild('HumanoidRootPart')
 if not root then return false end
 loading[player]=true
 local previous=states[player] and states[player].id or 0
 persist(player,id)
 player:SetAttribute('AreaTransition',id)
 local wasAnchored=root.Anchored root.Anchored=true
 if workspace.StreamingEnabled then pcall(function() player:RequestStreamAroundAsync(pos,3) end) end
 if player.Character~=char or not root.Parent then
  persist(player,previous)
  if root.Parent then root.Anchored=wasAnchored end
  loading[player]=nil player:SetAttribute('AreaTransition',nil) return false
 end
 put(player,pos,id)
 states[player]={id=id,safe=pos,grace=os.clock()+.8}
 player:SetAttribute('CurrentAreaId',id)
 root.Anchored=wasAnchored
 loading[player]=nil player:SetAttribute('AreaTransition',nil)
 return true
end
function Travel.start()
 if started then return end started=true
 local function playerAdded(player)
  local function spawned(char)
   persist(player,0)
   states[player]={id=0,safe=lobby,grace=os.clock()+3}
   player:SetAttribute('CurrentAreaId',0)
   local root=char:WaitForChild('HumanoidRootPart',10)
   if root and player.Character==char then put(player,lobby,0) end
  end
  player.CharacterAdded:Connect(spawned)
  if player.Character then task.spawn(spawned,player.Character) end
 end
 Players.PlayerAdded:Connect(playerAdded) for _,player in Players:GetPlayers() do playerAdded(player) end
 Players.PlayerRemoving:Connect(function(player)
  unpersist(player)
  states[player]=nil loading[player]=nil
 end)
 local elapsed=0
 RunService.Heartbeat:Connect(function(dt)
  elapsed+=dt if elapsed<.2 then return end elapsed=0
  for player,state in states do
   local char=player.Character local root=char and char:FindFirstChild('HumanoidRootPart') local hum=char and char:FindFirstChildOfClass('Humanoid')
   if not root or not hum or hum.Health<=0 or os.clock()<state.grace then continue end
   local pos=root.Position local valid
   -- MUNDO CONTINUO: andar tambem muda de area (regioes das ilhas; lobby; fora disso faixas de z)
   local zona=areaAt(pos,state.id)
   if zona~=state.id and not loading[player] then
    state.id=zona
    player:SetAttribute('CurrentAreaId',zona)
    persist(player,zona)
   end
   if state.id==0 then
    valid=lobbyAt(pos)
   else
    valid=inside(state.id,pos)
    if not valid and not box(state.id) then
     -- area sem caixa declarada: a regra antiga (centro do Config + caixa padrao)
     local a=Config.areaPorId(state.id) local offset=a and pos-a.centro
     valid=offset and math.abs(offset.X)<146 and math.abs(offset.Z)<146 and offset.Y>-12 and offset.Y<125
    end
    -- corredor entre mundos: faixa estreita ligando as areas
    if not valid then
     valid=math.abs(pos.X)<60 and pos.Z>170 and pos.Z<2740 and pos.Y>-12 and pos.Y<80
    end
   end
   if not valid then
    put(player,state.safe or destination(state.id),state.id)
    player:SetAttribute('AreaRecoveries',(player:GetAttribute('AreaRecoveries') or 0)+1)
    state.grace=os.clock()+.5
   else
    local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude params.FilterDescendantsInstances={char}
    params.RespectCanCollide=true
    local ground=workspace:Raycast(pos,Vector3.new(0,-8,0),params)
    local c,half,m=nil,nil,nil
    if state.id>0 then c,half,m=box(state.id) end
    local center=c or (state.id>0 and Config.areaPorId(state.id).centro) or Vector3.zero
    local ymax=m and m:GetAttribute('SafeMaxY')
    local lowOk=(typeof(ymax)=='number' and pos.Y<ymax) or (typeof(ymax)~='number' and pos.Y-center.Y<18)
    local halfX=(half and half.X) or 180
    -- Don't save cliff tops, water channels or decorative roofs as recovery positions.
    if ground and ground.Normal.Y>.8 and lowOk and math.abs(pos.X-center.X)<halfX and hum.FloorMaterial~=Enum.Material.Air then
     state.safe=pos+Vector3.new(0,.25,0)
    end
   end
  end
 end)
end
return Travel
