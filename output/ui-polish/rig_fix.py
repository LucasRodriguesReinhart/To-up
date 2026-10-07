from pathlib import Path
p=Path(__file__).parent/'src/ReplicatedStorage/ExpeditionUI/Theme.lua'
s=p.read_text(encoding='utf-8')
s=s.replace('d.Anchored=true;d.CanCollide=false;d.CanTouch=false;d.CanQuery=false','d.Anchored=(d==root);d.CanCollide=false;d.CanTouch=false;d.CanQuery=false;d.Massless=true')
a=s.index('   -- Anchor the display rig')
b=s.index('   local range=',a)
s=s[:a]+'''   -- Use native joints inside the WorldModel so layered clothing follows the rig.
   -- Manual BasePart FK detached reversed accessory welds and did not deform WrapLayers.
   local joints={}
   for _,joint in ipairs(model:GetDescendants()) do
    if joint:IsA("AnimationConstraint") and joint.Attachment0 and joint.Attachment1 then
     local motor=Instance.new("Motor6D")
     motor.Name=joint.Name;motor.Part0=joint.Attachment0.Parent;motor.Part1=joint.Attachment1.Parent
     motor.C0=joint.Attachment0.CFrame;motor.C1=joint.Attachment1.CFrame
     motor.Parent=joint.Parent;joint:Destroy()
    end
   end
   local hum=model:FindFirstChildOfClass("Humanoid")
   if hum then hum.AutoRotate=false;hum.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.None end
   for _,accessory in ipairs(model:GetChildren()) do
    if accessory:IsA("Accessory") then
     local handle=accessory:FindFirstChild("Handle")
     local attachment=handle and handle:FindFirstChildOfClass("Attachment")
     if handle and attachment and not handle:FindFirstChild("AccessoryWeld") then
      for _,part in ipairs(model:GetChildren()) do
       local target=part:IsA("BasePart") and part:FindFirstChild(attachment.Name)
       if target and target:IsA("Attachment") then
        local weld=Instance.new("Weld");weld.Name="AccessoryWeld";weld.Part0=handle;weld.Part1=part
        weld.C0=attachment.CFrame;weld.C1=target.CFrame;handle.CFrame=part.CFrame*weld.C1*weld.C0:Inverse();weld.Parent=handle;break
       end
      end
     end
    end
   end
   for _,motor in ipairs(model:GetDescendants()) do
    if motor:IsA("Motor6D") then
     local a=poses[motor.Name] or Vector3.zero
     local pose=CFrame.Angles(math.rad(a.X),math.rad(a.Y),math.rad(a.Z))
     motor.Transform=pose
     table.insert(joints,{name=motor.Name,motor=motor,pose=pose})
    end
   end
   table.insert(animatedModels,{model=model,root=root,joints=joints,phase=index*.85})
''' +s[b:]
s=s.replace('local idle=Run.RenderStepped:Connect','local idle=Run.PreSimulation:Connect')
s=s.replace('j.p1.CFrame=j.p0.CFrame*j.c0*j.pose*extra*j.c1','j.motor.Transform=j.pose*extra')
s=s.replace('ArticulatedDisplayPose','NativeDisplayRig')
p.write_text(s,encoding='utf-8')
print('Preview rig patched')
