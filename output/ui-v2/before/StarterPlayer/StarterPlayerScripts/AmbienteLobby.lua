
local RunService=game:GetService("RunService")
local root=workspace:WaitForChild("LobbyRenovado")
local entries={}
local function register(v)
 if v:IsA("BasePart") and v.Name=="Corrente" then entries[v]={kind="flow"}
 elseif v:IsA("PointLight") then entries[v]={kind="light",brightness=v.Brightness,seed=math.random()*6}
 elseif v:IsA("ParticleEmitter") and v:GetAttribute("LobbyAmbient") then entries[v]={kind="emitter"}
 elseif v:IsA("Model") and v:GetAttribute("AmbientBird") then entries[v]={kind="bird",index=v:GetAttribute("AmbientBird")} end
end
root.DescendantAdded:Connect(register)
root.DescendantRemoving:Connect(function(v) entries[v]=nil end)
for _,v in ipairs(root:GetDescendants()) do register(v) end
local elapsed,acc=0,0
local connection
connection=RunService.Heartbeat:Connect(function(dt)
 if not root.Parent then connection:Disconnect() return end
 elapsed+=dt acc+=dt
 if acc<1/15 then return end
 acc=0
 local camera=workspace.CurrentCamera
 if not camera then return end
 local cam=camera.CFrame.Position
 local effectsEnabled=game.Players.LocalPlayer:GetAttribute("LobbyVFXEnabled")~=false
 local near=effectsEnabled and (cam-Vector3.new(0,10,0)).Magnitude<230
 for v,data in pairs(entries) do
 if not v.Parent then entries[v]=nil
 elseif data.kind=="emitter" then
 local a=v.Parent
 if a:IsA("Attachment") then v.Enabled=effectsEnabled and (cam-a.WorldPosition).Magnitude<150 end
 elseif near then
 if data.kind=="flow" then
 local a,b=v:GetAttribute("FlowA"),v:GetAttribute("FlowB")
 if a and b then
 local t=(elapsed*.095+(v:GetAttribute("FlowPhase") or 0))%1
 local point=a:Lerp(b,t)
 v.CFrame=CFrame.lookAt(point,point+(b-a))
 v.Transparency=.45+math.abs(t-.5)*.7
 end
 elseif data.kind=="light" then
 v.Brightness=data.brightness*(.94+.04*math.sin(elapsed*3+data.seed)+.02*math.sin(elapsed*7+data.seed))
 elseif data.kind=="bird" then
 local body,left,right=v:FindFirstChild("Corpo"),v:FindFirstChild("Asa2"),v:FindFirstChild("Asa3")
 if body and left and right then
 local phase=elapsed*.075+data.index*2.1
 local pos=Vector3.new(math.cos(phase)*(53+data.index*7),58+data.index*3+math.sin(phase*2)*2,-32+math.sin(phase)*36)
 local cf=CFrame.lookAt(pos,pos+Vector3.new(-math.sin(phase),0,math.cos(phase)))
 body.CFrame=cf
 local flap=math.sin(elapsed*4+data.index)*.3
 left.CFrame=cf*CFrame.new(-.6,0,0)*CFrame.Angles(0,0,-flap)
 right.CFrame=cf*CFrame.new(.6,0,0)*CFrame.Angles(0,0,flap)
 end
 end
 end
 end
end)

