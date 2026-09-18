-- Select a rock, approach its actual surface, then request a server-validated strike.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local UIS=game:GetService("UserInputService")
local Paths=game:GetService("PathfindingService")
local player=Players.LocalPlayer
local mouse=player:GetMouse()
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local Config=require(RS:WaitForChild("Config"))
local remote=RS:WaitForChild("Remotes").Golpear
local target,highlight
local version=0
local waypoints,index,pathBusy,lastPlan=nil,1,false,0
local lastRequest=0
local function selectRock(rock)
 version+=1
 target=rock waypoints=nil index=1
 player:SetAttribute("MiningTargetSelected",rock~=nil)
 if highlight then highlight:Destroy() highlight=nil end
 if rock then
  highlight=Instance.new("Highlight")
  highlight.FillColor=Color3.fromRGB(255,240,140) highlight.FillTransparency=.8
  highlight.OutlineColor=Color3.fromRGB(255,230,90)
  highlight.DepthMode=Enum.HighlightDepthMode.Occluded
  highlight.Adornee=rock.Parent:FindFirstChild("Visual") or rock
  highlight.Parent=rock
 end
end
local function clickedRock()
 local hit=mouse.Target
 if not hit then return end
 local group=hit
 while group and group~=workspace do
  local candidate=group:FindFirstChild("Hitbox")
  if Geometry.valid(candidate) then return candidate end
  group=group.Parent
 end
end
UIS.InputBegan:Connect(function(input,processed)
 if processed then return end
 if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then
  local hit=clickedRock() if hit then selectRock(hit) end
 elseif input.KeyCode==Enum.KeyCode.W or input.KeyCode==Enum.KeyCode.A or input.KeyCode==Enum.KeyCode.S
  or input.KeyCode==Enum.KeyCode.D or input.KeyCode==Enum.KeyCode.Space then
  selectRock(nil)
  local c=player.Character local h=c and c:FindFirstChildOfClass("Humanoid")
  if h then h:Move(Vector3.zero) end
 end
end)
UIS.InputChanged:Connect(function(input)
 if input.KeyCode==Enum.KeyCode.Thumbstick1 and input.Position.Magnitude>.2 then selectRock(nil) end
end)
player.CharacterAdded:Connect(function() selectRock(nil) end)
player:GetAttributeChangedSignal("CurrentAreaId"):Connect(function()
 selectRock(nil)
 local char=player.Character local h=char and char:FindFirstChildOfClass("Humanoid")
 local root=char and char:FindFirstChild("HumanoidRootPart")
 if h and root then h:Move(Vector3.zero) h:MoveTo(root.Position) end
end)
task.spawn(function()
 for _=1,12 do
  if pcall(function() game:GetService("StarterGui"):SetCoreGuiEnabled(Enum.CoreGuiType.Backpack,false) end) then break end
  task.wait(.4)
 end
end)
task.spawn(function()
 while true do
  task.wait(.08)
  if target and not Geometry.valid(target) then selectRock(nil) end
  if not target then continue end
  local c=player.Character local h=c and c:FindFirstChildOfClass("Humanoid")
  local root=c and c:FindFirstChild("HumanoidRootPart")
  if not h or not root or h.Health<=0 then continue end
  local goal=Geometry.destination(target,root.Position)
  local distance=(Vector3.new(goal.X,root.Position.Y,goal.Z)-root.Position).Magnitude
  if Geometry.canReach(c,target,Geometry.ClientReach) then
   h:Move(Vector3.zero,false)
   h:MoveTo(root.Position)
   local look=Vector3.new(target.Position.X,root.Position.Y,target.Position.Z)
   if (look-root.Position).Magnitude>.01 then root.CFrame=CFrame.lookAt(root.Position,look) end
   if os.clock()-lastRequest>=Config.COOLDOWN_GOLPE+.03 then
    lastRequest=os.clock()
    remote:FireServer(target)
   end
  elseif not c:GetAttribute("MiningSwingActive") then
   local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude
   params.FilterDescendantsInstances={c,target.Parent} params.RespectCanCollide=true
   local obstacle=workspace:Raycast(root.Position,goal-root.Position,params)
   if not obstacle and math.abs(target.Position.Y-root.Position.Y)<8 then
    waypoints=nil h:MoveTo(goal)
   else
    if not pathBusy and os.clock()-lastPlan>1 then
     pathBusy=true lastPlan=os.clock()
     local revision=version
     task.spawn(function()
      local path=Paths:CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=true,WaypointSpacing=4})
      local ok=pcall(function() path:ComputeAsync(root.Position,goal) end)
      if revision==version and ok and path.Status==Enum.PathStatus.Success then
       waypoints=path:GetWaypoints() index=2
      end
      pathBusy=false
     end)
    end
    local point=waypoints and waypoints[index]
    if point then
     if (point.Position-root.Position).Magnitude<3 then index+=1 point=waypoints[index] end
     if point then
      if point.Action==Enum.PathWaypointAction.Jump then h.Jump=true end
      h:MoveTo(point.Position)
     end
    else h:MoveTo(goal) end
   end
  end
 end
end)

