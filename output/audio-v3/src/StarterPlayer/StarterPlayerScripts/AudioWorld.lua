-- Physical sound sources follow the actual scene, including dynamically built areas.
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
