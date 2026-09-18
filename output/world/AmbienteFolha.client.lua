local RunService=game:GetService("RunService")
local Players=game:GetService("Players")
local entries={}
local function register(v)
 if v:IsA("BasePart") and v.Name=="CorrenteFolha" then entries[v]={kind="flow",phase=v:GetAttribute("FlowPhase") or 0}
 elseif v:IsA("Texture") and v.Name=="FluxoCachoeira" then entries[v]={kind="waterfall"}
 elseif v:IsA("ParticleEmitter") and v:GetAttribute("FolhaAmbient") then entries[v]={kind="emitter"}
 elseif v:IsA("PointLight") and v:IsDescendantOf(workspace:FindFirstChild("Areas") or v) then entries[v]={kind="light",brightness=v.Brightness,phase=math.random()*6} end
end
workspace.DescendantAdded:Connect(register)
workspace.DescendantRemoving:Connect(function(v) entries[v]=nil end)
for _,v in ipairs(workspace:GetDescendants()) do register(v) end
local elapsed,acc=0,0
RunService.Heartbeat:Connect(function(dt)
 elapsed+=dt acc+=dt if acc<1/20 then return end acc=0
 local camera=workspace.CurrentCamera if not camera then return end
 local enabled=Players.LocalPlayer:GetAttribute("LobbyVFXEnabled")~=false
 for v,data in pairs(entries) do
  if not v.Parent then entries[v]=nil continue end
  local carrier=v:IsA("BasePart") and v or v.Parent
  local point=carrier:IsA("Attachment") and carrier.WorldPosition or carrier:IsA("BasePart") and carrier.Position
  local near=point and (camera.CFrame.Position-point).Magnitude<180
  if data.kind=="emitter" then v.Enabled=enabled and near
  elseif enabled and near then
   if data.kind=="flow" then
    local a,b=v:GetAttribute("FlowA"),v:GetAttribute("FlowB")
    if a and b then
     local t=(elapsed*.22+data.phase)%1
     local p=a:Lerp(b,t)
     v.CFrame=CFrame.lookAt(p,p+(b-a))
     v.Transparency=.45+math.abs(t-.5)*.8
    end
   elseif data.kind=="waterfall" then v.OffsetStudsV=-elapsed*10
   elseif data.kind=="light" then v.Brightness=data.brightness*(.96+.04*math.sin(elapsed*3+data.phase)) end
  end
 end
end)

