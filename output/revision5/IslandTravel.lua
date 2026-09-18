-- Server-owned area membership and recovery. No position or area supplied by a client is trusted.
local Players=game:GetService('Players')
local RunService=game:GetService('RunService')
local Config=require(game.ReplicatedStorage.Config)
local PlayerData=require(script.Parent.PlayerData)
local Travel={}
local states={} local loading={} local started=false
local lobby=Vector3.new(0,7,66)
local function destination(id)
 if id==0 then return lobby end
 local model=workspace.Areas:FindFirstChild('Area'..id)
 return model and model:GetAttribute('EntryPosition')
end
local function put(player,pos,id)
 local char=player.Character local root=char and char:FindFirstChild('HumanoidRootPart')
 if not root then return false end
 root.AssemblyLinearVelocity=Vector3.zero root.AssemblyAngularVelocity=Vector3.zero
 root.CFrame=CFrame.lookAt(pos,pos+Vector3.new(0,0,id==0 and -30 or 30))
 return true
end
function Travel.teleport(player,pos)
 if typeof(pos)~='Vector3' then return false end
 if loading[player] then return false end
 local id=0
 for _,a in Config.Areas do if (pos-a.centro).Magnitude<240 then id=a.id break end end
 if id>0 then local data=PlayerData.get(player) if not data or not data.areas[id] then return false end end
 local char=player.Character local root=char and char:FindFirstChild('HumanoidRootPart')
 if not root then return false end
 loading[player]=true
 local previous=states[player] and states[player].id or 0
 local model=id>0 and workspace.Areas:FindFirstChild('Area'..id)
 if model then model:AddPersistentPlayer(player) end
 player:SetAttribute('AreaTransition',id)
 local wasAnchored=root.Anchored root.Anchored=true
 if workspace.StreamingEnabled then pcall(function() player:RequestStreamAroundAsync(pos,3) end) end
 if player.Character~=char or not root.Parent then
  if model then model:RemovePersistentPlayer(player) end
  if root.Parent then root.Anchored=wasAnchored end
  loading[player]=nil player:SetAttribute('AreaTransition',nil) return false
 end
 put(player,pos,id)
 states[player]={id=id,safe=pos,grace=os.clock()+.8}
 player:SetAttribute('CurrentAreaId',id)
 root.Anchored=wasAnchored
 if previous>0 and previous~=id then
  local old=workspace.Areas:FindFirstChild('Area'..previous) if old then old:RemovePersistentPlayer(player) end
 end
 loading[player]=nil player:SetAttribute('AreaTransition',nil)
 return true
end
function Travel.start()
 if started then return end started=true
 local function playerAdded(player)
  local function spawned(char)
   local prior=states[player] and states[player].id
   if prior and prior>0 then local model=workspace.Areas:FindFirstChild('Area'..prior) if model then model:RemovePersistentPlayer(player) end end
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
  local state=states[player] if state and state.id>0 then local m=workspace.Areas:FindFirstChild('Area'..state.id) if m then m:RemovePersistentPlayer(player) end end
  states[player]=nil loading[player]=nil
 end)
 local elapsed=0
 RunService.Heartbeat:Connect(function(dt)
  elapsed+=dt if elapsed<.2 then return end elapsed=0
  for player,state in states do
   local char=player.Character local root=char and char:FindFirstChild('HumanoidRootPart') local hum=char and char:FindFirstChildOfClass('Humanoid')
   if not root or not hum or hum.Health<=0 or os.clock()<state.grace then continue end
   local pos=root.Position local valid
   if state.id==0 then
    valid=math.abs(pos.X)<190 and pos.Z>-180 and pos.Z<175 and pos.Y>-20 and pos.Y<170
   else
    local a=Config.areaPorId(state.id) local offset=a and pos-a.centro
    valid=offset and math.abs(offset.X)<146 and math.abs(offset.Z)<146 and offset.Y>-8 and offset.Y<125
   end
   if not valid then
    put(player,state.safe or destination(state.id),state.id)
    player:SetAttribute('AreaRecoveries',(player:GetAttribute('AreaRecoveries') or 0)+1)
    state.grace=os.clock()+.5
   else
    local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude params.FilterDescendantsInstances={char}
    params.RespectCanCollide=true
    local ground=workspace:Raycast(pos,Vector3.new(0,-8,0),params)
    local center=state.id>0 and Config.areaPorId(state.id).centro or Vector3.zero
    -- Don't save cliff tops, water channels or decorative roofs as recovery positions.
    if ground and ground.Normal.Y>.8 and pos.Y-center.Y<18 and math.abs(pos.X-center.X)<125 and hum.FloorMaterial~=Enum.Material.Air then
     state.safe=pos+Vector3.new(0,.25,0)
    end
   end
  end
 end)
end
return Travel
