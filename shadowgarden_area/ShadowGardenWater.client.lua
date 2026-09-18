local RunService=game:GetService('RunService')
local Players=game:GetService('Players')
local p=Players.LocalPlayer
local waves={}
local function add(v)
 if v:IsA('BasePart')and v:GetAttribute('ShadowWaterRipple')then waves[v]={base=v.CFrame,phase=v.Position.X%.7}end
end
for _,v in workspace:GetDescendants()do add(v)end
workspace.DescendantAdded:Connect(add)
workspace.DescendantRemoving:Connect(function(v)waves[v]=nil end)
local time,acc=0,0
RunService.Heartbeat:Connect(function(dt)
 time+=dt;acc+=dt;if acc<1/20 then return end;acc=0
 local camera=workspace.CurrentCamera;if not camera then return end
 for v,d in waves do
  if not v.Parent then waves[v]=nil
  elseif (camera.CFrame.Position-v.Position).Magnitude<190 then
   v.CFrame=d.base+Vector3.new(math.sin(time*.3)*.23,math.sin(time*.65)*.017,math.cos(time*.21)*.27)
  end
 end
end)
