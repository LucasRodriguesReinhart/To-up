-- Temporary Studio-only traversal/spawn test. Remove after QA.
local RunService=game:GetService('RunService')
if not RunService:IsStudio()then return end
task.wait(8)
local C=game.ServerScriptService.Core
local Config=require(game.ReplicatedStorage.Config)
local Layout=require(C.ShadowGardenLayout)
local Spawn=require(C.SpawnMinerio)
local Builder=require(C.AreaBuilder)
local area=table.clone(Config.Areas[4]);area.id=904;area.centro=Vector3.new(0,100,5000)
local root=workspace:FindFirstChild('ShadowGarden_Review');if not root then return end
local result=Instance.new('Folder');result.Name='__ShadowQAResults';result.Parent=workspace
local ores=Instance.new('Folder');ores.Name='QA_Minerios';ores.Parent=root
local function cv(p)return Vector3.new(-p[1],106+p[3],5000+p[2])end
local points={}for _,m in Layout.markers do if m.kind=='ore'then table.insert(points,cv(m.p))end end
local zones={lista={{nome='Pedreira',centro=cv({0,-5,-6}),tamanho=Vector3.new(110,0,108)},{nome='Mina',centro=cv({0,128,0}),tamanho=Vector3.new(13,0,42)},{nome='Cripta',centro=cv({-91,124,0}),tamanho=Vector3.new(16,0,26)}},bloqueios={}}
local available=Spawn.registrarPontos(area,points,{ores},{cv({0,-167,0})},zones)
result:SetAttribute('AvailableSpawns',#available)
for i=1,70 do Builder.novoMinerio(area,ores,nil,i%12==0 and 'epica'or i%4==0 and 'incomum'or 'comum')end
result:SetAttribute('Ores',#ores:GetChildren())
local Players=game:GetService('Players')
local dummy=Players:CreateHumanoidModelFromDescriptionAsync(Instance.new('HumanoidDescription'),Enum.HumanoidRigType.R15)
dummy.Name='QA_Walker';dummy.Parent=root
local hum=dummy:FindFirstChildOfClass('Humanoid');hum.WalkSpeed=16
local routes={
 {'Entrada',{0,-163,4},{0,-94,4}},
 {'RampaSul',{0,-81,4},{0,-43,-2}},
 {'RampaNorte',{0,30,-2},{0,73,4}},
 {'RampaOeste',{-80,-5,4},{-39,-5,-2}},
 {'RampaLeste',{80,-5,4},{39,-5,-2}},
 {'Castelo',{57,63,4},{57,107,20}},
 {'Patamar',{57,107,20},{24,107,20}},
 {'Ponte',{85,-52,4},{146,-52,4}},
 {'Mina',{0,95,4},{0,147,4}},
}
for _,r in routes do
 dummy:PivotTo(CFrame.new(cv(r[2])));dummy.PrimaryPart.AssemblyLinearVelocity=Vector3.zero
 task.wait(.65);hum:MoveTo(cv(r[3]));local reached=hum.MoveToFinished:Wait()
 local distance=(dummy:GetPivot().Position-cv(r[3])).Magnitude
 result:SetAttribute(r[1],reached and distance<6);result:SetAttribute(r[1]..'_Dist',math.floor(distance*100)/100)
 print('[ShadowQA]',r[1],reached,distance)
end
result:SetAttribute('Done',true)
