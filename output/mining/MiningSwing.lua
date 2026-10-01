-- Authored pickaxe swing: anticipation, descending strike, impact, follow-through.
-- Original locomotion remains in LocomocaoBigAxe. This owns the pose only during a strike.
local RunService=game:GetService("RunService")
local RS=game:GetService("ReplicatedStorage")
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local M={Duration=Geometry.Duration,ImpactTime=Geometry.ImpactTime}
local active={}
local function rotation(x,y,z) return CFrame.Angles(math.rad(x),math.rad(y or 0),math.rad(z or 0)) end
local poses={
 {t=0,weight=0,body=rotation(0,0,0),waist=rotation(0,0,0),right=rotation(100,0,12),elbow=rotation(-35),left=rotation(55,0,-24),leftElbow=rotation(-45),neck=rotation(0),knee=rotation(0)},
 {t=.18,weight=1,body=CFrame.new(0,-.08,.05)*rotation(-6,-6,-2),waist=rotation(-14,24,-8),right=rotation(155,-15,18),elbow=rotation(-64),left=rotation(108,22,-20),leftElbow=rotation(-75),neck=rotation(10,-18,3),knee=rotation(10)},
 {t=.26,weight=1,body=CFrame.new(0,-.12,0)*rotation(1,-3,-1),waist=rotation(-6,14,-5),right=rotation(125,-10,14),elbow=rotation(-42),left=rotation(91,18,-18),leftElbow=rotation(-60),neck=rotation(2,-12,2),knee=rotation(12)},
 {t=.34,weight=1,body=CFrame.new(0,-.24,-.15)*rotation(9,5,2),waist=rotation(19,-15,6),right=rotation(65,-8,6),elbow=rotation(-12),left=rotation(61,10,-18),leftElbow=rotation(-48),neck=rotation(-12,10,-3),knee=rotation(19)},
 {t=.4,weight=1,body=CFrame.new(0,-.26,-.18)*rotation(11,7,3),waist=rotation(23,-19,8),right=rotation(56,-10,8),elbow=rotation(-18),left=rotation(48,12,-22),leftElbow=rotation(-48),neck=rotation(-14,12,-4),knee=rotation(21)},
 {t=.53,weight=.92,body=CFrame.new(0,-.1,-.02)*rotation(3,2,1),waist=rotation(8,-7,2),right=rotation(81,-8,10),elbow=rotation(-28),left=rotation(44,5,-19),leftElbow=rotation(-34),neck=rotation(-4,4,0),knee=rotation(8)},
 {t=.72,weight=0,body=CFrame.identity,waist=CFrame.identity,right=rotation(100),elbow=rotation(-30),left=rotation(35,0,-15),leftElbow=rotation(-25),neck=CFrame.identity,knee=CFrame.identity},
}
local map={LowerTorso="body",UpperTorso="waist",RightUpperArm="right",RightLowerArm="elbow",
 LeftUpperArm="left",LeftLowerArm="leftElbow",Head="neck",RightLowerLeg="knee",LeftLowerLeg="knee",
 ["Right Arm"]="right",["Left Arm"]="left",Torso="waist"}
local function sample(t)
 for i=2,#poses do
  local a,b=poses[i-1],poses[i]
  if t<=b.t then
   local alpha=math.clamp((t-a.t)/(b.t-a.t),0,1)
   alpha=alpha*alpha*(3-2*alpha)
   local result={weight=a.weight+(b.weight-a.weight)*alpha}
   for _,name in pairs(map) do if a[name] then result[name]=a[name]:Lerp(b[name],alpha) end end
   return result
  end
 end
 return poses[#poses]
end
local function stop(char,state)
 for _,j in ipairs(state.joints) do if j.joint.Parent then j.joint.Transform=j.base end end
 if state.tool.Parent then state.tool.Grip=state.grip end
 if state.trail then state.trail.Enabled=false end
 if char.Parent then char:SetAttribute("MiningSwingActive",false) end
 active[char]=nil
end
local function gripWorld(state)
 local hand=state.char:FindFirstChild("RightHand") or state.char:FindFirstChild("Right Arm")
 if not hand then return end
 local attachment=hand:FindFirstChild("RightGripAttachment")
 return attachment and attachment.WorldCFrame or hand.CFrame*CFrame.new(0,-1,0)
end
function M.Play(char, hit, startedAt)
 local hum=char and char:FindFirstChildOfClass("Humanoid")
 local tool=char and char:FindFirstChild("Picareta")
 if not hum or hum.Health<=0 or not tool then return false end
 if active[char] then stop(char,active[char]) end
 local joints={}
 for _,j in ipairs(char:GetDescendants()) do
  if j:IsA("Motor6D") or j:IsA("AnimationConstraint") then
   local child=j:IsA("Motor6D") and j.Part1 or j.Attachment1 and j.Attachment1.Parent
   if child and map[child.Name] then table.insert(joints,{joint=j,name=map[child.Name],base=j.Transform}) end
  end
 end
 if #joints==0 then return false end
 local head=tool:FindFirstChild("Cabeca")
 local trail=head and head:FindFirstChild("StrikeTrail")
 if head and not trail then
  local a=Instance.new("Attachment") a.Name="TrailLeft" a.Position=Vector3.new(-1.1,0,0) a.Parent=head
  local b=Instance.new("Attachment") b.Name="TrailRight" b.Position=Vector3.new(1.1,0,0) b.Parent=head
  trail=Instance.new("Trail") trail.Name="StrikeTrail" trail.Attachment0=a trail.Attachment1=b
  trail.Lifetime=.09 trail.MinLength=.08 trail.FaceCamera=true trail.LightEmission=.35
  trail.Color=ColorSequence.new(Color3.fromRGB(244,227,172))
  trail.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.55),NumberSequenceKeypoint.new(1,1)})
  trail.Enabled=false trail.Parent=head
 end
 local root=char:FindFirstChild("HumanoidRootPart")
 active[char]={char=char,tool=tool,grip=tool.Grip,joints=joints,hit=hit,
  startedAt=startedAt or workspace:GetServerTimeNow(),trail=trail,
  target=Geometry.valid(hit) and Geometry.contact(hit,root.Position) or nil}
 char:SetAttribute("MiningSwingSource","AuthoredPickaxe2026")
 char:SetAttribute("MiningSwingActive",true)
 return true
end
RunService.PreSimulation:Connect(function()
 for char,state in pairs(active) do
  local t=workspace:GetServerTimeNow()-state.startedAt
  local h=char:FindFirstChildOfClass("Humanoid")
  if not char.Parent or not h or h.Health<=0 or state.tool.Parent~=char or t>=M.Duration then
   stop(char,state)
  elseif t>=0 then
   local pose=sample(t)
   for _,j in ipairs(state.joints) do
    if j.joint.Parent then j.joint.Transform=j.base:Lerp(pose[j.name],pose.weight) end
   end
   -- Rotate the pick around the hand, keeping the handle seated in the palm.
   local hand=gripWorld(state)
   if hand then
    local root=char:FindFirstChild("HumanoidRootPart")
    local target=state.target or (root.Position+root.CFrame.LookVector*3-Vector3.new(0,.5,0))
    local down=(target-hand.Position)
    if down.Magnitude>.1 then
     local aim=down.Unit
     local right=root.CFrame.RightVector
     right=(right-aim*right:Dot(aim)).Unit
     local desired=CFrame.fromMatrix(hand.Position-aim*state.grip.Position.Y,right,aim)
     local impactGrip=desired:Inverse()*hand
     local aimWeight=t<.18 and 0 or t<.34 and (t-.18)/.16 or t<.43 and 1 or math.max(0,1-(t-.43)/.29)
     state.tool.Grip=state.grip:Lerp(impactGrip,aimWeight)
    end
   end
   if state.trail then state.trail.Enabled=t>.2 and t<.39 end
  end
 end
end)
return M

