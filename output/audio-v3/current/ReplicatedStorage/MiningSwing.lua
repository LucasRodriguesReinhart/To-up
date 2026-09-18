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
local marker=Instance.new('BindableEvent')
M.MarkerReached=marker.Event
M.Markers={{name='SwingStart',time=Anim.TRAIL_INICIO},{name='Hit',time=Anim.CONTATO},{name='SwingEnd',time=Anim.TRAIL_FIM}}
-- Called after the pose/IK is written, on the same sampled animation frame.
function M.Advance(char,t)
 local state=active[char] if not state then return end
 for _,m in ipairs(M.Markers) do
  if t>=m.time and not state.markers[m.name] then
   state.markers[m.name]=true
   if m.name~='SwingStart' or t-m.time<.12 then marker:Fire(char,m.name,state.hit,state.time) end
  end
 end
end
-- Native AnimationTrack adapter: exact same named marker interface if tracks replace the procedural rig.
function M.BindTrack(track,char,rock,startedAt)
 local cs={}
 for _,m in ipairs(M.Markers) do table.insert(cs,track:GetMarkerReachedSignal(m.name):Connect(function() marker:Fire(char,m.name,rock,startedAt) end)) end
 local function disconnect() for _,c in ipairs(cs) do c:Disconnect() end table.clear(cs) end
 table.insert(cs,track.Stopped:Connect(disconnect))
 return disconnect
end
local function stop(char)
 local state=active[char]
 if state then marker:Fire(char,'Cancelled',state.hit,state.time,state.tool) end
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
 if current then stop(char) end
 active[char]={tool=tool,humanoid=humanoid,time=began,fim=fim,hit=hit,markers={}}
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

