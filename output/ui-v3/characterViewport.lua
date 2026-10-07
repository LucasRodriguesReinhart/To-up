-- Models are rendered at their native proportions. Body bounds avoid remote
-- accessory handles in imported rigs changing the camera framing.
function T.characterViewport(p, ids, x, y, w, h, opts)
 opts=opts or {}
 if type(ids)=="string" then ids={ids} end
 local v=T.new("ViewportFrame",{Name="CharacterViewport",Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(w,h),BackgroundTransparency=1,BorderSizePixel=0,Ambient=rgb(202,199,221),LightColor=rgb(255,244,228),LightDirection=Vector3.new(-.35,-.6,1),ImageColor3=opts.dim and rgb(74,70,85) or WHITE},p)
 local world=T.new("WorldModel",{},v)
 local cam=T.new("Camera",{FieldOfView=28},v);v.CurrentCamera=cam
 local folder=RS:FindFirstChild("PreviewModelos");folder=folder and folder:FindFirstChild("Pets")
 local count=#ids;local minV=Vector3.new(math.huge,math.huge,math.huge);local maxV=-minV
 local poses={RightShoulder=Vector3.new(8,0,-5),LeftShoulder=Vector3.new(13,0,6),RightElbow=Vector3.new(18,0,0),LeftElbow=Vector3.new(28,0,0),Waist=Vector3.new(0,5,0),Neck=Vector3.new(-3,-5,0)}
 for index,id in ipairs(ids) do
  local original=folder and folder:FindFirstChild(id)
  if original then
   local model=original:Clone();model.Name=id
   local root=model:FindFirstChild("HumanoidRootPart")
   for _,d in ipairs(model:GetDescendants()) do
    if d:IsA("LuaSourceContainer") or d:IsA("ParticleEmitter") or d:IsA("Trail") or d:IsA("Sound") then d:Destroy()
    elseif d:IsA("BasePart") then
     d.Anchored=d==root;d.CanCollide=false;d.CanTouch=false;d.CanQuery=false
     if root and (d.Position-root.Position).Magnitude>15 then d.Transparency=1 end
    end
   end
   model:PivotTo(CFrame.new())
   local head=model:FindFirstChild("Head")
   local lf=model:FindFirstChild("LeftFoot") or model:FindFirstChild("Left Leg")
   local rf=model:FindFirstChild("RightFoot") or model:FindFirstChild("Right Leg")
   local top=head and head.Position.Y+head.Size.Y*.5 or 2.5
   local bottom=math.min(lf and lf.Position.Y-lf.Size.Y*.5 or -3,rf and rf.Position.Y-rf.Size.Y*.5 or -3)
   local height=math.max(3,top-bottom)
   local factor=5.6/height
   model:ScaleTo(model:GetScale()*factor)
   local offset=(index-(count+1)/2)*(count>1 and 2.75 or 0)
   local yaw=opts.yaw or (count>1 and (index-(count+1)/2)*-.18 or .12)
   local z=count>1 and (index==math.ceil(count/2) and -.65 or .25) or 0
   model:PivotTo(CFrame.new(offset,-bottom*factor,z)*CFrame.Angles(0,yaw,0))
   model.Parent=world
   for _,d in ipairs(model:GetDescendants()) do
    if d:IsA("AnimationConstraint") or d:IsA("Motor6D") then
     local a=poses[d.Name];if a then d.Transform=CFrame.Angles(math.rad(a.X),math.rad(a.Y),math.rad(a.Z)) end
    end
   end
   local range=Vector3.new(2.45,3.25,1.6)
   local center=Vector3.new(offset,2.95,z)
   local lo,hi=center-range,center+range
   minV=Vector3.new(math.min(minV.X,lo.X),math.min(minV.Y,lo.Y),math.min(minV.Z,lo.Z))
   maxV=Vector3.new(math.max(maxV.X,hi.X),math.max(maxV.Y,hi.Y),math.max(maxV.Z,hi.Z))
  end
 end
 if minV.X==math.huge then
  T.text(v,"Unavailable","Modelo indisponível",8,h/2-15,w-16,30,16,T.P.text2,T.CENTER,"body",false)
  return v
 end
 local center=(minV+maxV)/2
 local size=maxV-minV
 if opts.fullBody==false then center+=Vector3.new(0,.8,0);size=Vector3.new(size.X,size.Y*.75,size.Z) end
 local angle=0
 local function frameCamera()
  local aspect=math.max(.2,v.AbsoluteSize.X/math.max(1,v.AbsoluteSize.Y))
  if v.AbsoluteSize.Y<2 then aspect=math.max(.2,w/math.max(1,h)) end
  local dist=math.max(size.Y*.5/math.tan(math.rad(14)),size.X*.5/(math.tan(math.rad(14))*aspect))*(opts.padding or 1.04)
  cam.CFrame=CFrame.lookAt(center+Vector3.new(math.sin(angle)*dist,dist*.015,-math.cos(angle)*dist),center)
 end
 frameCamera();v:GetPropertyChangedSignal("AbsoluteSize"):Connect(frameCamera)
 if opts.interactive then
  v.Active=true
  local inputService=game:GetService("UserInputService")
  local dragging,lastX=false,0
  v.InputBegan:Connect(function(input)
   if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then dragging=true;lastX=input.Position.X end
  end)
  local changed=inputService.InputChanged:Connect(function(input)
   if dragging and (input.UserInputType==Enum.UserInputType.MouseMovement or input.UserInputType==Enum.UserInputType.Touch) then
    angle+=(input.Position.X-lastX)*.009;lastX=input.Position.X;frameCamera()
   end
  end)
  local ended=inputService.InputEnded:Connect(function(input)
   if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then dragging=false end
  end)
  v.Destroying:Once(function() changed:Disconnect();ended:Disconnect() end)
 end
 v:SetAttribute("ModelIds",table.concat(ids,","))
 return v
end
