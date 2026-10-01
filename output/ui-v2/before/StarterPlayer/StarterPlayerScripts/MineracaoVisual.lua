-- MineracaoVisual: feedback audiovisual do golpe para TODOS os mineradores visiveis.
-- Tudo aqui e so visual e local (nada replica): VFX de impacto por raridade, reacao da rocha, trail da picareta,
-- tremida de camera (so do proprio jogador), numeros de dano e explosao de quebra.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local RunService=game:GetService("RunService")
local Tween=game:GetService("TweenService")
local Debris=game:GetService("Debris")
local player=Players.LocalPlayer
local R=RS:WaitForChild("Remotes")
local Config=require(RS:WaitForChild("Config"))
local swing=require(RS:WaitForChild("MiningSwing"))
local Anim=require(RS:WaitForChild("MiningAnimations"))
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local Som=require(RS:WaitForChild("SomJogo"))

local DIST_VISUAL=90 -- mineradores alem disso nao geram VFX/som local (desempenho)

-- ---------- ESTILO POR RARIDADE DO MINERIO ----------
local TIER={
 comum={cor=Color3.fromRGB(196,176,138),faisca=Color3.fromRGB(255,228,150),poeira=6,faiscas=4,escala=1,shake=.06},
 incomum={cor=Color3.fromRGB(120,210,130),faisca=Color3.fromRGB(170,255,170),poeira=7,faiscas=6,escala=1.05,shake=.07},
 raro={cor=Color3.fromRGB(110,160,255),faisca=Color3.fromRGB(170,210,255),poeira=7,faiscas=8,escala=1.12,shake=.08},
 epica={cor=Color3.fromRGB(190,120,255),faisca=Color3.fromRGB(230,180,255),poeira=8,faiscas=11,escala=1.2,shake=.1,luz=true},
 lendaria={cor=Color3.fromRGB(255,196,70),faisca=Color3.fromRGB(255,240,160),poeira=9,faiscas=15,escala=1.3,shake=.13,luz=true},
 chefe={cor=Color3.fromRGB(255,110,80),faisca=Color3.fromRGB(255,200,140),poeira=10,faiscas=14,escala=1.35,shake=.16,luz=true},
}
local function tierDe(rock)
 if not rock then return TIER.comum end
 if rock:GetAttribute("Chefe") then return TIER.chefe end
 return TIER[rock:GetAttribute("Variante") or "comum"] or TIER.comum
end

local function perto(pos)
 local cam=workspace.CurrentCamera
 return cam and pos and (cam.CFrame.Position-pos).Magnitude<DIST_VISUAL
end

-- ---------- VFX DE IMPACTO ----------
local function impacto(pos,tier,forca)
 local p=Instance.new("Part") p.Name="ImpactoPicareta" p.Anchored=true p.Transparency=1
 p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local dust=Instance.new("ParticleEmitter")
 dust.Texture="rbxasset://textures/particles/smoke_main.dds" dust.Rate=0
 dust.Color=ColorSequence.new(tier.cor:Lerp(Color3.fromRGB(180,161,128),.5))
 dust.Lifetime=NumberRange.new(.18,.38) dust.Speed=NumberRange.new(2,5.5)
 dust.SpreadAngle=Vector2.new(70,70) dust.Drag=4
 dust.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.35*tier.escala),NumberSequenceKeypoint.new(1,1.5*tier.escala)})
 dust.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.5),NumberSequenceKeypoint.new(1,1)})
 dust.Parent=a dust:Emit(math.floor(tier.poeira*forca))
 local spark=Instance.new("ParticleEmitter")
 spark.Texture="rbxasset://textures/particles/sparkles_main.dds" spark.Rate=0
 spark.Lifetime=NumberRange.new(.1,.24) spark.Speed=NumberRange.new(5,10*tier.escala)
 spark.SpreadAngle=Vector2.new(95,95) spark.LightEmission=.9 spark.Acceleration=Vector3.new(0,-25,0)
 spark.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.26*tier.escala),NumberSequenceKeypoint.new(1,0)})
 spark.Color=ColorSequence.new(tier.faisca)
 spark.Parent=a spark:Emit(math.floor(tier.faiscas*forca))
 local chip=Instance.new("ParticleEmitter")
 chip.Texture="rbxasset://textures/particles/explosion01_core_main.dds" chip.Rate=0
 chip.Lifetime=NumberRange.new(.25,.45) chip.Speed=NumberRange.new(6,11)
 chip.SpreadAngle=Vector2.new(60,60) chip.Acceleration=Vector3.new(0,-40,0) chip.RotSpeed=NumberRange.new(-300,300)
 chip.Size=NumberSequence.new(.14*tier.escala) chip.Color=ColorSequence.new(tier.cor:Lerp(Color3.new(.3,.3,.32),.55))
 chip.Parent=a chip:Emit(math.floor(3*forca))
 if tier.luz then
  local l=Instance.new("PointLight") l.Color=tier.faisca l.Brightness=3 l.Range=9*tier.escala l.Parent=p
  Tween:Create(l,TweenInfo.new(.14),{Brightness=0}):Play()
 end
 Debris:AddItem(p,1)
end

-- ---------- REACAO DA ROCHA ----------
local tremendo={} -- [visual] = {base, inicio, dir, forca}
local function tremerRocha(rock,origem,forca)
 local visual=rock and rock.Parent and rock.Parent:FindFirstChild("Visual")
 if not visual or not visual:IsA("Model") then return end
 local st=tremendo[visual]
 local base=st and st.base or visual:GetPivot()
 local dir=origem and Vector3.new(rock.Position.X-origem.X,0,rock.Position.Z-origem.Z) or Vector3.zero
 dir=dir.Magnitude>.01 and dir.Unit or Vector3.new(1,0,0)
 tremendo[visual]={base=base,inicio=os.clock(),dir=dir,forca=forca}
end

-- ---------- CAMERA (so o proprio jogador) ----------
local shake=0
local function tremerCamera(valor) shake=math.min(.35,math.max(shake,valor)) end

RunService:BindToRenderStep("MineracaoFeedback",Enum.RenderPriority.Camera.Value+1,function(dt)
 local agora=os.clock()
 for visual,st in pairs(tremendo) do
  local a=(agora-st.inicio)/.16
  if not visual.Parent or a>=1 then
   if visual.Parent then visual:PivotTo(st.base) end
   tremendo[visual]=nil
  else
   local k=(1-a)^2*math.sin(a*math.pi*3)
   visual:PivotTo(st.base*CFrame.new(st.dir*.16*st.forca*k)*CFrame.Angles(0,0,math.rad(2.2*st.forca*k)))
  end
 end
 if shake>.002 then
  local cam=workspace.CurrentCamera
  local n=math.noise(agora*38,0,0)
  local n2=math.noise(0,agora*38,0)
  cam.CFrame=cam.CFrame*CFrame.new(n*shake,n2*shake,0)
  shake=shake*math.exp(-dt*22)
 end
end)

-- ---------- TRAIL DA PICARETA ----------
local COR_MUNDO={Color3.fromRGB(235,235,240),Color3.fromRGB(120,200,255),Color3.fromRGB(95,230,190),Color3.fromRGB(175,115,255),Color3.fromRGB(80,215,255),Color3.fromRGB(255,165,70)}
local trails=setmetatable({},{__mode="k"})
local function trailDa(tool)
 if trails[tool] and trails[tool].Parent then return trails[tool] end
 local handle=tool:FindFirstChild("Handle")
 if not handle then return nil end
 local cabeca,dist=handle,0
 for _,d in ipairs(tool:GetDescendants()) do
  if d:IsA("BasePart") and d~=handle then
   local x=(d.Position-handle.Position).Magnitude
   if x>dist then cabeca,dist=d,x end
  end
 end
 local eixo=cabeca~=handle and (cabeca.Position-handle.Position) or handle.CFrame.UpVector
 eixo=eixo.Magnitude>.01 and eixo.Unit or Vector3.yAxis
 local a0=Instance.new("Attachment") a0.Name="TrailA" a0.WorldPosition=cabeca.Position-eixo*.4 a0.Parent=cabeca
 local a1=Instance.new("Attachment") a1.Name="TrailB" a1.WorldPosition=cabeca.Position+eixo*.9 a1.Parent=cabeca
 local def=Config.picaretaPorId(tool:GetAttribute("PicaretaId") or "")
 local mundo=def and def.mundo or 1
 local cor=COR_MUNDO[mundo] or COR_MUNDO[1]
 local t=Instance.new("Trail")
 t.Attachment0=a0 t.Attachment1=a1 t.Lifetime=.13+.01*mundo t.MinLength=.04 t.FaceCamera=true
 t.LightEmission=.35+.11*mundo
 t.Color=ColorSequence.new(cor,cor:Lerp(Color3.new(1,1,1),.4))
 t.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.75-.07*mundo),NumberSequenceKeypoint.new(1,1)})
 t.WidthScale=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(1,0)})
 t.Enabled=false t.Parent=cabeca
 trails[tool]=t
 return t
end

-- ---------- NUMEROS DE DANO (UI V2) ----------
-- fonte pesada com contorno, cor pela raridade do minerio e "pop" maior no golpe que quebra
local FONTE_DANO = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Heavy, Enum.FontStyle.Italic)
local TINTA = Color3.fromRGB(10, 6, 22)
local numeros=0
local function numero(pos,dano,tier,final)
 if numeros>=9 then return end
 numeros+=1
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos+Vector3.new(math.random()-.5,1.2,math.random()-.5) p.Parent=workspace
 local bb=Instance.new("BillboardGui") bb.Size=UDim2.fromOffset(final and 210 or 170,final and 62 or 48)
 bb.AlwaysOnTop=true bb.MaxDistance=70 bb.Parent=p
 local t=Instance.new("TextLabel") t.Size=UDim2.fromScale(1,1) t.BackgroundTransparency=1
 t.FontFace=FONTE_DANO t.TextScaled=true t.Text=Config.formatar(math.floor(dano+.5))
 t.TextColor3=final and tier.faisca or Color3.new(1,1,1)
 t.Rotation=(math.random()-.5)*10
 t.Parent=bb
 local st=Instance.new("UIStroke") st.Color=TINTA st.Thickness=final and 3.2 or 2.4 st.LineJoinMode=Enum.LineJoinMode.Round st.Parent=t
 local sc=Instance.new("UIScale") sc.Scale=final and 1.9 or 1.45 sc.Parent=t
 Tween:Create(sc,TweenInfo.new(.14,Enum.EasingStyle.Back),{Scale=1}):Play()
 Tween:Create(p,TweenInfo.new(.62,Enum.EasingStyle.Quad),{Position=p.Position+Vector3.new(0,final and 2.2 or 1.6,0)}):Play()
 task.delay(.3,function() Tween:Create(t,TweenInfo.new(.32),{TextTransparency=1}):Play() Tween:Create(st,TweenInfo.new(.32),{Transparency=1}):Play() end)
 task.delay(.66,function() p:Destroy() numeros-=1 end)
end

-- ---------- BARRA DE VIDA DA ROCHA ----------
-- rastro branco que persegue a barra (mostra o quanto o golpe tirou) + flash no impacto
local function barraFeedback(rock)
 local bb=rock and rock:FindFirstChild("Vida")
 if not bb then return end
 local barra=bb:FindFirstChild("Barra",true)
 local interno=barra and barra.Parent
 if not barra or not interno then return end
 local rastro=interno:FindFirstChild("Rastro")
 if not rastro then
  rastro=Instance.new("Frame")
  rastro.Name="Rastro" rastro.BorderSizePixel=0 rastro.ZIndex=(barra.ZIndex or 2)-1
  rastro.BackgroundColor3=Color3.fromRGB(255,236,236) rastro.Size=barra.Size rastro.Position=barra.Position
  local c=Instance.new("UICorner") c.CornerRadius=UDim.new(0,8) c.Parent=rastro
  rastro.Parent=interno
 end
 task.delay(.1,function()
  if rastro.Parent and barra.Parent then Tween:Create(rastro,TweenInfo.new(.28,Enum.EasingStyle.Quad),{Size=barra.Size}):Play() end
 end)
 local flash=interno:FindFirstChild("Flash")
 if not flash then
  flash=Instance.new("Frame") flash.Name="Flash" flash.BorderSizePixel=0 flash.ZIndex=(barra.ZIndex or 2)+1
  flash.BackgroundColor3=Color3.new(1,1,1) flash.Size=UDim2.fromScale(1,1) flash.BackgroundTransparency=1
  local c=Instance.new("UICorner") c.CornerRadius=UDim.new(0,8) c.Parent=flash
  flash.Parent=interno
 end
 flash.BackgroundTransparency=.55
 Tween:Create(flash,TweenInfo.new(.18),{BackgroundTransparency=1}):Play()
end

-- ---------- QUEBRA ----------
local function explosao(pos,tier)
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local e=Instance.new("ParticleEmitter")
 e.Texture="rbxasset://textures/particles/sparkles_main.dds" e.Rate=0
 e.Lifetime=NumberRange.new(.3,.6) e.Speed=NumberRange.new(10,20*tier.escala) e.SpreadAngle=Vector2.new(180,180)
 e.Drag=3 e.LightEmission=1 e.Color=ColorSequence.new(tier.faisca,tier.cor)
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.5*tier.escala),NumberSequenceKeypoint.new(1,0)})
 e.Parent=a e:Emit(math.floor(14*tier.escala^3))
 local l=Instance.new("PointLight") l.Color=tier.faisca l.Brightness=4*tier.escala l.Range=14*tier.escala l.Parent=p
 Tween:Create(l,TweenInfo.new(.25),{Brightness=0}):Play()
 Debris:AddItem(p,1.2)
end

-- ---------- EVENTOS ----------
local function tocarImpacto(miner,c,rock,position)
 local root=c and c:FindFirstChild("HumanoidRootPart")
 local tier=tierDe(rock)
 local golpe=c and c:GetAttribute("MiningComboGolpe")
 local forca=golpe=="vertical" and 1.35 or (golpe=="lateral" and .9 or 1)
 impacto(position,tier,forca)
 tremerRocha(rock,root and root.Position,forca*(rock and rock:GetAttribute("Chefe") and .5 or 1))
 local ehLocal=miner==player
 Som.tocar("hit",{pos=position,volume=ehLocal and 1 or .55})
 local def=c and c:FindFirstChild("Picareta") and Config.picaretaPorId(c.Picareta:GetAttribute("PicaretaId") or "")
 if def and def.mundo>=3 then Som.tocar("hit_pesado",{pos=position,volume=(ehLocal and 1 or .5)*math.min(1,(def.mundo-2)/3)}) end
 if ehLocal then tremerCamera(tier.shake*forca) barraFeedback(rock) end
end
-- impacto PREVISTO no cliente, no frame de contato da animacao (startedAt + CONTATO no relogio do servidor).
-- O aviso de impacto do servidor chega com o ping de atraso; ele so toca o VFX se a previsao nao tocou.
local previsto={} -- [miner] = os.clock() do ultimo impacto previsto
R:WaitForChild("AnimarPicareta").OnClientEvent:Connect(function(miner,rock,startedAt,isImpact,position)
 local c=miner and miner.Character
 local root=c and c:FindFirstChild("HumanoidRootPart")
 if isImpact then
  if previsto[miner] and os.clock()-previsto[miner]<.45 then previsto[miner]=nil return end
  if not position or not perto(position) then return end
  tocarImpacto(miner,c,rock,position)
  return
 end
 if not c then return end
 if not swing.Play(c,rock,startedAt) then return end
 if not root or not perto(root.Position) then return end
 local ate=math.max(0,(startedAt or workspace:GetServerTimeNow())+Anim.CONTATO-workspace:GetServerTimeNow())
 task.delay(ate,function()
  if c:GetAttribute("MiningSwingStart")~=startedAt or not Geometry.valid(rock) or not c:FindFirstChild("Picareta") then return end
  -- ponto do impacto = onde a cabeca da picareta esta AGORA, projetado na superficie da rocha
  local handle=c.Picareta:FindFirstChild("Handle")
  local cabeca=handle and (handle.CFrame*Vector3.new(0,Anim.CABECA_Y,0)) or Geometry.contact(rock,root.Position)
  previsto[miner]=os.clock()
  tocarImpacto(miner,c,rock,Geometry.surface(rock,cabeca))
 end)
 local tool=c:FindFirstChild("Picareta")
 local trail=tool and trailDa(tool)
 local espera=math.max(0,(startedAt or workspace:GetServerTimeNow())+Anim.TRAIL_INICIO-workspace:GetServerTimeNow())
 task.delay(espera,function()
  if trail and trail.Parent then trail.Enabled=true end
  Som.tocar("whoosh",{pos=root.Position,volume=miner==player and 1 or .5})
  task.delay(Anim.TRAIL_FIM-Anim.TRAIL_INICIO,function() if trail and trail.Parent then trail.Enabled=false end end)
 end)
end)

R.FeedbackMina.OnClientEvent:Connect(function(info)
 if type(info)~="table" then return end
 if info.tipo=="golpe" then
  if info.pos then numero(info.pos,info.dano or 0,TIER[info.chefe and "chefe" or info.variante or "comum"] or TIER.comum,info.quebrou) end
 elseif info.tipo=="quebrou" then
  local tier=TIER[info.variante or "comum"] or TIER.comum
  if info.pos then explosao(info.pos,tier) end
  Som.quebra(info.variante,info.pos)
  if not info.chefe then task.delay(.08,function() Som.coleta(info.pos) end) end
  tremerCamera(tier.shake*1.6)
 elseif info.tipo=="hat" then
  Som.drop(info.raridade)
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then
  Som.tocar("ui_erro")
 end
end)

