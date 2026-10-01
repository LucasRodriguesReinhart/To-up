-- A single controlled arm swing. No root/torso motion and no changing Tool.Grip.
local RunService=game:GetService("RunService")
local RS=game:GetService("ReplicatedStorage")
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local M={Duration=Geometry.Duration,ImpactTime=Geometry.ImpactTime}
local active={}
local function cf(x,y,z) return CFrame.Angles(math.rad(x),math.rad(y or 0),math.rad(z or 0)) end
local keys={
 {t=0,shoulder=cf(122,-7,8),elbow=cf(-38),weight=0},
 {t=.1,shoulder=cf(133,-7,8),elbow=cf(-45),weight=1},
 {t=.28,shoulder=cf(66,-7,6),elbow=cf(-22),weight=1},
 {t=.34,shoulder=cf(62,-7,6),elbow=cf(-21),weight=1},
 {t=.6,shoulder=cf(112,-7,8),elbow=cf(-36),weight=0},
}
for _,key in ipairs(keys) do key.wrist=CFrame.identity end
local function stop(char,s)
 for _,entry in ipairs(s.joints) do if entry.joint.Parent then entry.joint.Transform=entry.base end end
 if char.Parent then char:SetAttribute("MiningSwingActive",false) end
 active[char]=nil
end
function M.Play(char,hit,startedAt)
 local humanoid=char and char:FindFirstChildOfClass("Humanoid")
 local tool=char and char:FindFirstChild("Picareta")
 if not humanoid or humanoid.Health<=0 or not tool then return false end
 if active[char] then return false end
 local joints={}
 for _,joint in ipairs(char:GetDescendants()) do
  if joint:IsA("Motor6D") or joint:IsA("AnimationConstraint") then
   local child=joint:IsA("Motor6D") and joint.Part1 or joint.Attachment1 and joint.Attachment1.Parent
   local name=child and child.Name
   if name=="RightUpperArm" or name=="RightLowerArm" or name=="Right Arm" or name=="RightHand" then
    table.insert(joints,{joint=joint,key=name=="RightLowerArm" and "elbow" or name=="RightHand" and "wrist" or "shoulder",base=joint.Transform})
   end
  end
 end
 if #joints==0 then return false end
 active[char]={joints=joints,tool=tool,time=startedAt or workspace:GetServerTimeNow(),humanoid=humanoid}
 char:SetAttribute("MiningSwingActive",true)
 char:SetAttribute("MiningSwingSource","GameArmStrike")
 return true
end
RunService.PreSimulation:Connect(function()
 for char,s in pairs(active) do
  local t=workspace:GetServerTimeNow()-s.time
  if not char.Parent or s.humanoid.Health<=0 or s.tool.Parent~=char or t>=M.Duration then
   stop(char,s)
  elseif t>=0 then
   for i=2,#keys do
    local a,b=keys[i-1],keys[i]
    if t<=b.t then
     local alpha=math.clamp((t-a.t)/(b.t-a.t),0,1)
     alpha=alpha*alpha*(3-2*alpha)
     local weight=a.weight+(b.weight-a.weight)*alpha
     for _,entry in ipairs(s.joints) do
      if entry.joint.Parent then entry.joint.Transform=entry.base:Lerp(a[entry.key]:Lerp(b[entry.key],alpha),weight) end
     end
     break
    end
   end
  end
 end
end)
return M

