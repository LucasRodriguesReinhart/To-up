local P=game:GetService("PathfindingService")
local H=game:GetService("HttpService")
local G=require(game.ReplicatedStorage.MiningGeometry)
local cfg=require(game.ReplicatedStorage.Config)
local results={}
local function path(a,b)
 local p=P:CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,WaypointSpacing=5})
 local ok=pcall(function() p:ComputeAsync(a,b) end)
 return ok and p.Status.Name or "Error"
end
for _,def in cfg.Areas do
 local m=workspace.Areas["Area"..def.id] local c=def.centro local entry=m:GetAttribute("EntryPosition")
 local result={id=def.id,orePass=0,failures={},routes={}}
 for name,q in {Center=Vector3.new(0,9,1),Portal=Vector3.new(45,9,74),Gacha=Vector3.new(-43,9,-87),Boss=Vector3.new(-37,9,66),WestBank=Vector3.new(-109,9,26),EastBank=Vector3.new(109,9,26),Mine=Vector3.new(def.id==2 and 66 or -65,9,94)} do result.routes[name]=path(entry,c+q) end
 for _,side in {-1,1} do result.routes["BankLoop"..side]=path(c+Vector3.new(side*106,9,-61),c+Vector3.new(side*106,9,87)) end
 for i,ore in m.Rochas:GetChildren() do
  local hit=ore.Hitbox local ok=true
  for _,from in {entry,c+Vector3.new(0,9,1),c+Vector3.new(0,9,65)} do
   local status=path(from,G.destination(hit,from))
   if status~="Success" then ok=false table.insert(result.failures,{i=i,from=tostring(from),goal=tostring(G.destination(hit,from)),status=status}) end
  end
  if ok then result.orePass+=1 end
 end
 table.insert(results,result) script:SetAttribute("Results",H:JSONEncode(results))
end
script:SetAttribute("Finished",true)

