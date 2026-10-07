local RunService=game:GetService('RunService')
local Players=game:GetService('Players')
local player=Players.LocalPlayer
local entries={}
local function register(v)
 local d
 if v:IsA('BasePart') and v.Name=='CorrenteFolha' then d={kind='flow',phase=v:GetAttribute('FlowPhase') or 0}
 elseif v:IsA('Texture') and v.Name=='FluxoCachoeira' then d={kind='waterfall'}
 elseif v:IsA('Texture') and v.Name=='OndasDaIlha' then d={kind='waves'}
 elseif v:IsA('Texture') and (v.Name=='AguaLinhas' or v.Name=='AguaSombra' or v.Name=='EspumaPoco') then d={kind=v.Name,seed=v:GetAttribute('WaterSeed') or 0}
 elseif v:IsA('BasePart') and v.Name=='OndaAnel' then d={kind='ring',phase=v:GetAttribute('RingPhase') or 0,max=v:GetAttribute('RingMax') or 20,min=v:GetAttribute('RingMin') or 4}
 elseif v:IsA('ParticleEmitter') and v:GetAttribute('FolhaAmbient') then d={kind='emitter'}
 elseif v:IsA('BasePart') and v:GetAttribute('IslandSway') then d={kind='sway',base=v.CFrame,phase=v:GetAttribute('SwayPhase') or 0}
 elseif v:IsA('Model') and v:GetAttribute('IslandBird') then d={kind='bird',origin=v:GetAttribute('OrbitCenter'),radius=v:GetAttribute('OrbitRadius'),phase=v:GetAttribute('OrbitPhase')}
 elseif v:IsA('PointLight') and workspace:FindFirstChild('Areas') and v:IsDescendantOf(workspace.Areas) then d={kind='light',brightness=v.Brightness,phase=math.random()*6} end
 if d then entries[v]=d end
end
workspace.DescendantAdded:Connect(register)
workspace.DescendantRemoving:Connect(function(v) entries[v]=nil end)
for _,v in workspace:GetDescendants() do register(v) end
local elapsed,acc=0,0
RunService.Heartbeat:Connect(function(dt)
 elapsed+=dt acc+=dt if acc<1/15 then return end acc=0
 local camera=workspace.CurrentCamera if not camera then return end
 local enabled=player:GetAttribute('LobbyVFXEnabled')~=false
 for v,data in entries do
  if not v.Parent then entries[v]=nil continue end
  local carrier=v:IsA('BasePart') and v or v.Parent
  local point=data.origin or (carrier:IsA('Attachment') and carrier.WorldPosition) or (carrier:IsA('BasePart') and carrier.Position)
  local near=point and (camera.CFrame.Position-point).Magnitude<200
  if data.kind=='emitter' then v.Enabled=enabled and near
  elseif data.kind=='light' then
   v.Enabled=near==true
   if near then v.Brightness=data.brightness*(.98+.02*math.sin(elapsed*3+data.phase)) end
  elseif enabled and near then
   if data.kind=='flow' then
    local a,b=v:GetAttribute('FlowA'),v:GetAttribute('FlowB') if not a or not b then continue end
    local t=(elapsed*.17+data.phase)%1 local p=a:Lerp(b,t)
    v.CFrame=CFrame.lookAt(p,p+(b-a)) v.Transparency=.6+math.abs(t-.5)*.7
   elseif data.kind=='waterfall' then v.OffsetStudsV=-elapsed*9
   elseif data.kind=='waves' then v.OffsetStudsU=elapsed*.4 v.OffsetStudsV=elapsed*.65
   elseif data.kind=='AguaLinhas' then
    -- rede de linhas: deriva lenta com leve oscilacao (brilho da agua)
    v.OffsetStudsU=elapsed*.9+math.sin(elapsed*.7+data.seed)*1.6 v.OffsetStudsV=elapsed*.55+math.cos(elapsed*.5+data.seed)*1.2
   elseif data.kind=='AguaSombra' then
    v.OffsetStudsU=-elapsed*.6+math.cos(elapsed*.6+data.seed)*1.4 v.OffsetStudsV=elapsed*.35+3.3
   elseif data.kind=='EspumaPoco' then v.OffsetStudsU=elapsed*1.2 v.OffsetStudsV=math.sin(elapsed)*1
   elseif data.kind=='ring' then
    local t=(elapsed*.35+data.phase)%1
    local s=data.min+(data.max-data.min)*t
    v.Size=Vector3.new(v.Size.X,s,s) v.Transparency=.35+t*.65
   elseif data.kind=='sway' then v.CFrame=data.base*CFrame.Angles(math.sin(elapsed*1.3+data.phase)*.025,0,math.sin(elapsed+data.phase)*.018)
   elseif data.kind=='bird' then
    local a=elapsed*.13+data.phase local q=data.origin+Vector3.new(math.sin(a)*data.radius,math.sin(a*2)*2,math.cos(a)*data.radius*.45)
    v:PivotTo(CFrame.lookAt(q,q+Vector3.new(math.cos(a),0,-math.sin(a)*.45))*CFrame.Angles(0,0,math.sin(elapsed*4+data.phase)*.06))
   end
  end
 end
end)
