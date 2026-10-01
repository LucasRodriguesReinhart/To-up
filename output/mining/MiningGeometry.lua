-- Shared contact geometry: one reach rule for automatic movement and the server.
local M = {StandOff = 2.05, Reach = 3.05, ImpactTime = .34, Duration = .72}
function M.surface(hit, position)
 local p = hit.CFrame:PointToObjectSpace(position)
 local half = hit.Size * .5
 return hit.CFrame:PointToWorldSpace(Vector3.new(
  math.clamp(p.X, -half.X, half.X), math.clamp(p.Y, -half.Y, half.Y),
  math.clamp(p.Z, -half.Z, half.Z)))
end
function M.destination(hit, position)
 local flat = Vector3.new(position.X, hit.Position.Y, position.Z)
 local edge = M.surface(hit, flat)
 local away = Vector3.new(flat.X-edge.X, 0, flat.Z-edge.Z)
 if away.Magnitude < .01 then
  away = Vector3.new(position.X-hit.Position.X, 0, position.Z-hit.Position.Z)
  if away.Magnitude < .01 then away = Vector3.new(0,0,-1) end
  local half = hit.Size * .5
  local direction = hit.CFrame:VectorToObjectSpace(away.Unit)
  local radius = math.min(half.X / math.max(.001,math.abs(direction.X)),half.Z / math.max(.001,math.abs(direction.Z)))
  edge = hit.Position + away.Unit * radius
 end
 local point = edge + away.Unit * M.StandOff
 return Vector3.new(point.X, position.Y, point.Z)
end
function M.contact(hit, position)
 local y = math.clamp(position.Y-.7, hit.Position.Y-hit.Size.Y*.5+.35,hit.Position.Y+hit.Size.Y*.5-.1)
 return M.surface(hit, Vector3.new(position.X,y,position.Z))
end
function M.valid(hit)
 return typeof(hit)=="Instance" and hit:IsA("BasePart") and hit.Name=="Hitbox"
  and hit.Parent and hit.CanQuery and (hit:GetAttribute("HP") or 0)>0
end
function M.canReach(character, hit)
 if not M.valid(hit) then return false end
 local root = character and character:FindFirstChild("HumanoidRootPart")
 local hum = character and character:FindFirstChildOfClass("Humanoid")
 if not root or not hum or hum.Health<=0 then return false end
 local target = M.contact(hit,root.Position)
 if (target-root.Position).Magnitude > M.Reach then return false end
 local params=RaycastParams.new()
 params.FilterType=Enum.RaycastFilterType.Exclude
 params.FilterDescendantsInstances={character}
 params.RespectCanCollide=true
 local ray=workspace:Raycast(root.Position,target-root.Position,params)
 return not ray or ray.Instance==hit or ray.Instance:IsDescendantOf(hit.Parent)
end
return M

