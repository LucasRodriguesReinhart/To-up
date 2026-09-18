local p=game.Players:GetPlayers()[1] if not p then return end
local travel=require(game.ServerScriptService.Core.IslandTravel)
local cfg=require(game.ReplicatedStorage.Config)
local H=game.HttpService
local results={}
for _,a in cfg.Areas do
 local entry=workspace.Areas["Area"..a.id]:GetAttribute("EntryPosition")
 travel.teleport(p,entry) task.wait(.95)
 local root=p.Character.HumanoidRootPart
 local before=p:GetAttribute("AreaRecoveries") or 0
 for name,offset in {Side=Vector3.new(165,10,0),Back=Vector3.new(0,12,165),Above=Vector3.new(0,140,0),Below=Vector3.new(0,-15,0)} do
  root.CFrame=CFrame.new(a.centro+offset) root.AssemblyLinearVelocity=Vector3.zero
  task.wait(.75)
  local d=root.Position-a.centro
  results[#results+1]={id=a.id,test=name,inside=math.abs(d.X)<146 and math.abs(d.Z)<146 and d.Y>-8 and d.Y<125,area=p:GetAttribute("CurrentAreaId")}
 end
 script:SetAttribute("Results",H:JSONEncode(results))
end
travel.teleport(p,workspace.Areas.Area1:GetAttribute("EntryPosition"))
script:SetAttribute("Finished",true)

