local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local Debris=game:GetService("Debris")
local player=Players.LocalPlayer
local R=RS:WaitForChild("Remotes")
local Sons=RS:WaitForChild("Sons")
local swing=require(RS:WaitForChild("MiningSwing"))
local function sound(name,position)
 local base=Sons:FindFirstChild(name) if not base then return end
 local s=base:Clone()
 if position then
  local p=Instance.new("Part") p.Size=Vector3.one p.Transparency=1 p.Anchored=true
  p.CanCollide=false p.CanTouch=false p.CanQuery=false p.Position=position p.Parent=workspace
  s.Parent=p Debris:AddItem(p,4)
 else s.Parent=game:GetService("SoundService") Debris:AddItem(s,4) end
 s:Play()
end
local function impact(position,rock)
 if not position then return end
 local p=Instance.new("Part") p.Name="ImpactoPicareta" p.Anchored=true p.Transparency=1
 p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Size=Vector3.one p.Position=position p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local dust=Instance.new("ParticleEmitter")
 dust.Texture="rbxasset://textures/particles/smoke_main.dds" dust.Rate=0
 dust.Color=ColorSequence.new(Color3.fromRGB(180,161,128))
 dust.Lifetime=NumberRange.new(.16,.35) dust.Speed=NumberRange.new(2,5)
 dust.SpreadAngle=Vector2.new(65,65)
 dust.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.3),NumberSequenceKeypoint.new(1,1.4)})
 dust.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.55),NumberSequenceKeypoint.new(1,1)})
 dust.Parent=a dust:Emit(7)
 local spark=Instance.new("ParticleEmitter")
 spark.Texture="rbxasset://textures/particles/sparkles_main.dds" spark.Rate=0
 spark.Lifetime=NumberRange.new(.1,.22) spark.Speed=NumberRange.new(4,8)
 spark.SpreadAngle=Vector2.new(90,90) spark.LightEmission=.8
 spark.Size=NumberSequence.new(.23)
 spark.Color=ColorSequence.new(Color3.fromRGB(255,228,132))
 spark.Parent=a spark:Emit(5)
 Debris:AddItem(p,1)
end
R:WaitForChild("AnimarPicareta").OnClientEvent:Connect(function(miner,rock,startedAt,isImpact,position)
 if isImpact then impact(position,rock) return end
 local c=miner and miner.Character
 if c then swing.Play(c,rock,startedAt) end
end)
R.FeedbackMina.OnClientEvent:Connect(function(info)
 if info.tipo=="golpe" then sound(math.random()<.5 and "Golpe" or "GolpeAlt",info.pos)
 elseif info.tipo=="quebrou" then sound("Quebra",info.pos) sound("Detrito",info.pos)
 elseif info.tipo=="hat" or info.tipo=="area" then sound("Premio")
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then sound("Erro") end
end)

