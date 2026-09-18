-- Timing authority for the mining strike. The poses live in MiningAnimations (combo authored in code);
-- LocomocaoBigAxe samples them off this timestamp so the contact frame lands on the instant the server
-- used for damage. A new strike may replace the previous one once it is past the contact frame.
local Players=game:GetService("Players")
local RunService=game:GetService("RunService")
local RS=game:GetService("ReplicatedStorage")
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local Anim=require(RS:WaitForChild("MiningAnimations"))
local M={Duration=Geometry.Duration,ImpactTime=Geometry.ImpactTime}
local active={}
local function stop(char)
 if char.Parent then
  char:SetAttribute("MiningSwingActive",false)
  char:SetAttribute("MiningSwingStart",nil)
 end
 active[char]=nil
end
function M.Play(char,hit,startedAt)
 local humanoid=char and char:FindFirstChildOfClass("Humanoid")
 local tool=char and char:FindFirstChild("Picareta")
 if not humanoid or humanoid.Health<=0 or not tool then return false end
 local began=startedAt or workspace:GetServerTimeNow()
 local current=active[char]
 if current and began-current.time<Anim.CONTATO+.02 then return false end
 local owner=Players:GetPlayerFromCharacter(char)
 local fim=Anim.fimRecuperacao(owner and owner:GetAttribute("IntervaloGolpe") or .8)
 active[char]={tool=tool,humanoid=humanoid,time=began,fim=fim,hit=hit}
 char:SetAttribute("MiningSwingStart",began)
 char:SetAttribute("MiningSwingActive",true)
 char:SetAttribute("MiningSwingSource","MiningAnimations")
 return true
end
function M.Ativo(char) return active[char] end
RunService.PreSimulation:Connect(function()
 for char,s in pairs(active) do
  local t=workspace:GetServerTimeNow()-s.time
  if not char.Parent or s.humanoid.Health<=0 or s.tool.Parent~=char or t>=s.fim then
   stop(char)
  end
 end
end)
return M

