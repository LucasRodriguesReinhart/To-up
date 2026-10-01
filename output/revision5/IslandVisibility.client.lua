-- Hide distant destinations so their silhouettes do not appear outside the current scenery.
local player=game.Players.LocalPlayer
local known={}
local current=player:GetAttribute('CurrentAreaId') or 0
local function areaId(instance)
 local areas=workspace:FindFirstChild('Areas') if not areas then return end
 local node=instance
 while node and node.Parent~=areas do node=node.Parent end
 return node and (node:GetAttribute('AreaId') or tonumber(node.Name:match('^Area(%d+)$')))
end
local function register(instance)
 if not instance:IsA('BasePart') then return end
 local id=areaId(instance) if not id then return end
 known[instance]=id instance.LocalTransparencyModifier=id==current and 0 or 1
end
workspace.DescendantAdded:Connect(register)
workspace.DescendantRemoving:Connect(function(instance) known[instance]=nil end)
for _,instance in workspace:GetDescendants() do register(instance) end
player:GetAttributeChangedSignal('CurrentAreaId'):Connect(function()
 local old=current current=player:GetAttribute('CurrentAreaId') or 0
 for part,id in known do
  if part.Parent and (id==old or id==current) then part.LocalTransparencyModifier=id==current and 0 or 1 end
 end
end)
