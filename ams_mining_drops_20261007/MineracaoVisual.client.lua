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

local Theme=require(RS:WaitForChild("UI"):WaitForChild("Theme")).Compat
local function motionEnabled()
 return Theme.motionEnabled and Theme.motionEnabled() or (not Theme.motionEnabled and player:GetAttribute("ReducedMotion")~=true and player:GetAttribute("ExpeditionEffectsEnabled")~=false)
end
local function effectsEnabled() return player:GetAttribute("ExpeditionEffectsEnabled")~=false end
local ReferenceVFX=require(RS:WaitForChild("EquipmentV3"):WaitForChild("EquipmentVFX"))
task.spawn(function()
 local ok,result=pcall(ReferenceVFX.Warmup)
 if not ok or #result>0 then warn('[EquipmentV3] Texture preload incomplete',result) end
end)
local efeitosAtivos=0
local DIST_VISUAL=90 -- mineradores alem disso nao geram VFX/som local (desempenho)
-- Every confirmed strike still gets its damage feedback. Dense multiplayer only
-- samples decorative particles, rock motion and audio to protect weaker devices.
local lastRemoteDetail=setmetatable({},{__mode="k"})
local lastRockMotion=setmetatable({},{__mode="k"})
local lastHitAudio=setmetatable({},{__mode="k"})
local lastWhooshAudio=setmetatable({},{__mode="k"})

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
 if not effectsEnabled() or efeitosAtivos>=16 then return end
 efeitosAtivos+=1
 task.delay(1.05,function() efeitosAtivos=math.max(0,efeitosAtivos-1) end)
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
 if not motionEnabled() then return end
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
local function tremerCamera(valor) if motionEnabled() then shake=math.min(.22,math.max(shake,valor)) end end

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
 if not motionEnabled() then shake=0 end
 if shake>.002 then
  local cam=workspace.CurrentCamera
  local n=math.noise(agora*38,0,0)
  local n2=math.noise(0,agora*38,0)
  if cam then cam.CFrame=cam.CFrame*CFrame.new(n*shake,n2*shake,0) end
  shake=shake*math.exp(-dt*22)
 end
end)

-- ---------- TRAIL DA PICARETA ----------
local COR_MUNDO={Color3.fromRGB(235,235,240),Color3.fromRGB(120,200,255),Color3.fromRGB(95,230,190),Color3.fromRGB(175,115,255),Color3.fromRGB(80,215,255),Color3.fromRGB(255,165,70)}
local trails=setmetatable({},{__mode="k"})
local function trailDa(tool)
 if ReferenceVFX.Has(tool) then return ReferenceVFX.Trail(tool) end
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
local FONTE_DANO = Theme.F.number or Theme.F.heavy
local TINTA = Theme.P.ink
local numeros=0
local function numero(pos,dano,tier,final)
 if numeros>=9 then return end
 numeros+=1
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos+Vector3.new(math.random()-.5,1.2,math.random()-.5) p.Parent=workspace
 local bb=Instance.new("BillboardGui") bb.Size=UDim2.fromOffset(final and 150 or 122,final and 46 or 36)
 bb.AlwaysOnTop=true bb.MaxDistance=70 bb.Parent=p
 local t=Instance.new("TextLabel") t.Size=UDim2.fromScale(1,1) t.BackgroundTransparency=1
 t.FontFace=FONTE_DANO t.TextScaled=true t.Text=Config.formatar(math.floor(dano+.5))
 t.TextColor3=final and tier.faisca or Color3.new(1,1,1)
 t.Rotation=motionEnabled() and (math.random()-.5)*5 or 0
 t.Parent=bb
 local st=Instance.new("UIStroke") st.Color=TINTA st.Thickness=final and 1.8 or 1.4 st.LineJoinMode=Enum.LineJoinMode.Round st.Parent=t
 local sc=Instance.new("UIScale") sc.Scale=motionEnabled() and (final and 1.35 or 1.15) or 1 sc.Parent=t
 Tween:Create(sc,TweenInfo.new(.14,Enum.EasingStyle.Back),{Scale=1}):Play()
 if motionEnabled() then Tween:Create(p,TweenInfo.new(.62,Enum.EasingStyle.Quad),{Position=p.Position+Vector3.new(0,final and 1.8 or 1.2,0)}):Play() end
 task.delay(.3,function() Tween:Create(t,TweenInfo.new(.32),{TextTransparency=1}):Play() Tween:Create(st,TweenInfo.new(.32),{Transparency=1}):Play() end)
 task.delay(.66,function() p:Destroy() numeros-=1 end)
end

-- ---------- BARRA DE VIDA DA ROCHA ----------
-- rastro branco que persegue a barra (mostra o quanto o golpe tirou) + flash no impacto
local function barraFeedback(rock)
 if not effectsEnabled() then return end
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
 if not effectsEnabled() or not perto(pos) or efeitosAtivos>=16 then return end
 efeitosAtivos+=1
 task.delay(1.25,function() efeitosAtivos=math.max(0,efeitosAtivos-1) end)
 local p=Instance.new("Part") p.Anchored=true p.Transparency=1 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.Size=Vector3.one p.Position=pos p.Parent=workspace
 local a=Instance.new("Attachment") a.Parent=p
 local e=Instance.new("ParticleEmitter")
 e.Texture="rbxasset://textures/particles/sparkles_main.dds" e.Rate=0
 e.Lifetime=NumberRange.new(.3,.6) e.Speed=NumberRange.new(10,20*tier.escala) e.SpreadAngle=Vector2.new(180,180)
 e.Drag=3 e.LightEmission=1 e.Color=ColorSequence.new(tier.faisca,tier.cor)
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,.5*tier.escala),NumberSequenceKeypoint.new(1,0)})
 e.Parent=a e:Emit(math.floor(10*tier.escala^2))
 -- Fragmentos locais pequenos, sem física nem colisão: a quebra termina antes da coleta.
 if motionEnabled() then
  local count=tier.escala>=1.2 and 7 or 4
  for i=1,count do
   local fragment=Instance.new("Part")
   fragment.Name="FragmentoMinerio" fragment.Anchored=true fragment.CanCollide=false fragment.CanQuery=false fragment.CanTouch=false
   fragment.Material=Enum.Material.SmoothPlastic fragment.Color=tier.cor
   fragment.Size=Vector3.one*(.13+math.random()*.16)*tier.escala
   fragment.CFrame=CFrame.new(pos)*CFrame.Angles(math.random()*3,math.random()*3,math.random()*3) fragment.Parent=p
   local angle=(i/count)*math.pi*2
   local apex=pos+Vector3.new(math.cos(angle)*1.1,1.1+math.random()*.6,math.sin(angle)*1.1)*tier.escala
   Tween:Create(fragment,TweenInfo.new(.14,Enum.EasingStyle.Quad,Enum.EasingDirection.Out),{Position=apex}):Play()
   task.delay(.14,function()
    if fragment.Parent then Tween:Create(fragment,TweenInfo.new(.23,Enum.EasingStyle.Quad,Enum.EasingDirection.In),{Position=apex+Vector3.new(math.cos(angle),-1.3,math.sin(angle)),Transparency=1,Size=Vector3.one*.04}):Play() end
   end)
  end
 end
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
 local ehLocal=miner==player
 local now=os.clock()
 local detail=ehLocal or now-(lastRemoteDetail[miner] or -math.huge)>=.22
 if detail and not ehLocal then lastRemoteDetail[miner]=now end
 if detail and not ReferenceVFX.Has(c and c:FindFirstChild("Picareta")) then impacto(position,tier,forca) end
 if detail and rock and now-(lastRockMotion[rock] or -math.huge)>=(ehLocal and .10 or .22) then
  lastRockMotion[rock]=now
  tremerRocha(rock,root and root.Position,forca*(rock:GetAttribute("Chefe") and .5 or 1))
 end
 local def=c and c:FindFirstChild("Picareta") and Config.picaretaPorId(c.Picareta:GetAttribute("PicaretaId") or "")
 if now-(lastHitAudio[miner] or -math.huge)>=(ehLocal and .10 or .22) then
  lastHitAudio[miner]=now
  Som.hit(rock,{pos=position,remote=not ehLocal,heavy=def and def.mundo>=3,auto=ehLocal and player:GetAttribute("MiningContinuous")==true})
 end
 if ehLocal then tremerCamera(tier.shake*forca) barraFeedback(rock) end
end
-- A strike is identified by the server start timestamp. Never deduplicate by a broad time window.
local strikes={} -- bounded per-player history
local function strike(miner,id)
 local history=strikes[miner]
 if not history then history={} strikes[miner]=history end
 local now=os.clock()
 for key,value in pairs(history) do if now-value.at>3 then history[key]=nil end end
 if not history[id] then history[id]={at=now} end
 return history[id]
end
Players.PlayerRemoving:Connect(function(miner) strikes[miner]=nil end)
swing.MarkerReached:Connect(function(c,name,rock,startedAt,oldTool)
 if name=='Cancelled' then
  if oldTool then ReferenceVFX.Cancel(oldTool,false,startedAt) end
  local trail=oldTool and oldTool:FindFirstChild('MiningTrail',true)
  if trail and trail:IsA('Trail') then trail.Enabled=false end
  if oldTool then for _,v in ipairs(oldTool:GetDescendants()) do if v:IsA('Trail') then v.Enabled=false end end end
  local miner=Players:GetPlayerFromCharacter(c)
  local state=miner and strike(miner,startedAt)
  if state and state.confirmedPosition and not state.played and perto(state.confirmedPosition) then
   state.played=true tocarImpacto(miner,c,rock,state.confirmedPosition)
  end
  return
 end
 local miner=Players:GetPlayerFromCharacter(c)
 local root=c:FindFirstChild("HumanoidRootPart")
 if not miner or not root then return end
 local tool=c:FindFirstChild("Picareta")
 local trail=tool and trailDa(tool)
 if name=="SwingEnd" then
  local function endTrail()
   ReferenceVFX.End(tool)
   if trail then trail.Enabled=false end
  end
  local active=swing.Ativo(c)
  if active and active.intervalo<=.25 then
   -- At 8 Hz the authored trail lasts only two frames. A tiny visual tail
   -- keeps it readable without carrying it into the next strike.
   task.delay(.025,function()
    local newer=swing.Ativo(c)
    if not newer or newer.time==startedAt then endTrail() end
   end)
  else endTrail() end
  return
 end
 if not tool or not perto(root.Position) then return end
 local state=strike(miner,startedAt)
 if name=="SwingStart" then
  ReferenceVFX.Swing(tool,Geometry.valid(rock) and Geometry.contact(rock,root.Position))
  if trail and not ReferenceVFX.Has(tool) then trail.Enabled=effectsEnabled() end
  local now=os.clock()
  if now-(lastWhooshAudio[miner] or -math.huge)>=(miner==player and .10 or .22) then
   lastWhooshAudio[miner]=now
   Som.tocar("whoosh",{pos=root.Position,remote=miner~=player,auto=miner==player and player:GetAttribute("MiningContinuous")==true})
  end
 elseif name=="Hit" and not state.played then
  local position=state.confirmedPosition
  if not position and Geometry.valid(rock) and Geometry.canReach(c,rock,Geometry.Reach+.5) then
   local handle=tool:FindFirstChild("Handle")
   local head=handle and (handle.CFrame*Vector3.new(0,Anim.CABECA_Y,0)) or Geometry.contact(rock,root.Position)
   position=Geometry.surface(rock,head)
  end
  if position then state.played=true tocarImpacto(miner,c,rock,position) end
 end
end)
R:WaitForChild("AnimarPicareta").OnClientEvent:Connect(function(miner,rock,startedAt,isImpact,position,strikeId,oreBroken,intervalo)
 local c=miner and miner.Character
 if not c then return end
 if isImpact then
  if not position or not perto(position) then return end
  local id=strikeId or startedAt
  ReferenceVFX.ConfirmImpact(miner,id,position)
  if oreBroken then ReferenceVFX.Break(c:FindFirstChild("Picareta"),position) end
  local state=strike(miner,id)
  state.intervalo=intervalo or state.intervalo
  if state.played then return end
  state.confirmedPosition=position
  local active=swing.Ativo(c)
  local cadence=state.intervalo or (active and active.intervalo) or miner:GetAttribute("IntervaloGolpe") or Config.COOLDOWN_GOLPE
  if active and active.time==id and not active.markers.Hit
   and workspace:GetServerTimeNow()-active.visualStart<Geometry.impactTime(cadence)+math.min(.12,cadence*.5) then return end
  state.played=true tocarImpacto(miner,c,rock,position)
 else
  strike(miner,startedAt).intervalo=intervalo
  ReferenceVFX.ObserveStart(miner,startedAt,c:FindFirstChild("Picareta"))
  swing.Play(c,rock,startedAt,intervalo)
 end
end)

-- Drops locais: a recompensa e mantida no servidor ate a coleta automatica.
-- Os modelos sao apenas visuais para o dono, sem colisao nem simulacao fisica.
local dropsVisuais = {}
local coresHat = {
 comum = Color3.fromRGB(190, 205, 220), incomum = Color3.fromRGB(95, 222, 130),
 raro = Color3.fromRGB(90, 165, 255), epico = Color3.fromRGB(185, 105, 255),
 lendario = Color3.fromRGB(255, 194, 70), mitico = Color3.fromRGB(255, 85, 155),
}

local function prepararPeca(peca)
 peca.Anchored = true
 peca.CanCollide = false
 peca.CanTouch = false
 peca.CanQuery = false
 peca.CastShadow = false
end

local function posicaoNoChao(origem, deslocamento, altura)
 local pos = origem + deslocamento
 local params = RaycastParams.new()
 params.FilterType = Enum.RaycastFilterType.Exclude
 local ignorar = { player.Character }
 if workspace:FindFirstChild("MiningDropsLocal") then table.insert(ignorar, workspace.MiningDropsLocal) end
 local areas = workspace:FindFirstChild("Areas")
 if areas then
  for _, area in ipairs(areas:GetChildren()) do
   local rochas = area:FindFirstChild("Rochas")
   if rochas then table.insert(ignorar, rochas) end
  end
 end
 params.FilterDescendantsInstances = ignorar
 local hit = workspace:Raycast(pos + Vector3.new(0, 4, 0), Vector3.new(0, -24, 0), params)
 return Vector3.new(pos.X, hit and hit.Position.Y + altura or pos.Y - 1, pos.Z)
end

local function criarMiniMinerio(info, parent)
 local modelos = RS:FindFirstChild("MiningDropVisuals")
 local variante = info.variante
 if variante == "raro" or variante == "lendaria" then variante = "epica" end
 local nome = "minerio_" .. tostring(info.tema) .. "_" .. tostring(variante)
 local modelo = modelos and (modelos:FindFirstChild(nome)
  or modelos:FindFirstChild("minerio_" .. tostring(info.tema) .. "_comum"))
 local grupo = Instance.new("Model")
 grupo.Name = "MineriosDrop"
 grupo.WorldPivot = CFrame.new(0, 0, 0)
 local quantidade = math.clamp(tonumber(info.quantidade) or 2, 1, 5)
 for i = 1, quantidade do
  local mini
  if modelo then
   mini = modelo:Clone()
   for _, d in ipairs(mini:GetDescendants()) do
    if d:IsA("BasePart") then
     if d.Size.Magnitude > 7 then d:Destroy() else prepararPeca(d) end
    elseif d:IsA("LuaSourceContainer") then d:Destroy() end
   end
   mini:ScaleTo(.95 + (i % 3) * .15)
  else
   mini = Instance.new("Part")
   mini.Shape = Enum.PartType.Ball
   mini.Size = Vector3.new(.7, .6, .7)
   mini.Material = Enum.Material.SmoothPlastic
   mini.Color = (TIER[info.variante] or TIER.comum).cor
   prepararPeca(mini)
  end
  mini.Name = "Minerio_" .. i
  mini.Parent = grupo
  local angulo = i * 2.39996 + info.id * .7
  local raio = i == 1 and .1 or .8 + (i % 2) * .45
  local localPos = Vector3.new(math.cos(angulo) * raio, .1 + (i % 2) * .04, math.sin(angulo) * raio)
  local cf = CFrame.new(localPos) * CFrame.Angles(0, angulo, 0)
  if mini:IsA("Model") then mini:PivotTo(cf) else mini.CFrame = cf end
 end
 local contornos = parent:FindFirstChild("ContornoMinerios")
 if not contornos then
  contornos = Instance.new("Model")
  contornos.Name = "ContornoMinerios"
  contornos.Parent = parent
  local borda = Instance.new("Highlight")
  borda.Name = "Borda"
  borda.Adornee = contornos
  borda.FillTransparency = .97
  borda.OutlineColor = Color3.fromRGB(16, 27, 48)
  borda.OutlineTransparency = .05
  borda.DepthMode = Enum.HighlightDepthMode.Occluded
  borda.Parent = contornos
 end
 grupo.Parent = contornos
 return grupo
end

local function criarMiniHat(info, parent)
 local cor = coresHat[info.hatRaridade] or Color3.fromRGB(255, 198, 85)
 local folder = RS:FindFirstChild("MiningDropHats")
 local template = folder and folder:FindFirstChild(tostring(info.hatId))
 local objeto
 if template and template:IsA("BasePart") then
  objeto = template:Clone()
  local maior = math.max(objeto.Size.X, objeto.Size.Y, objeto.Size.Z)
  local escala = 1.3 / math.max(maior, .01)
  objeto.Size *= escala
  for _, d in ipairs(objeto:GetDescendants()) do
   if d:IsA("SpecialMesh") then d.Scale *= escala end
  end
  prepararPeca(objeto)
 else
  -- Fallback somente se um asset nao estiver disponivel no cliente.
  objeto = Instance.new("Model")
  local topo = Instance.new("Part")
  topo.Name = "Copa"
  topo.Shape = Enum.PartType.Ball
  topo.Size = Vector3.new(.9, .65, .9)
  topo.Color = cor
  topo.Material = Enum.Material.SmoothPlastic
  prepararPeca(topo)
  topo.CFrame = CFrame.new(0, .3, 0)
  topo.Parent = objeto
  local aba = Instance.new("Part")
  aba.Name = "Aba"
  aba.Shape = Enum.PartType.Cylinder
  aba.Size = Vector3.new(.14, 1.2, 1.2)
  aba.Color = cor
  aba.Material = Enum.Material.SmoothPlastic
  prepararPeca(aba)
  aba.CFrame = CFrame.new(0, .05, -.15) * CFrame.Angles(0, 0, math.pi / 2)
  aba.Parent = objeto
 end
 objeto.Name = "HatDrop"
 local contorno = Instance.new("Highlight")
 contorno.Adornee = objeto
 contorno.FillTransparency = .94
 contorno.FillColor = cor
 contorno.OutlineColor = Color3.fromRGB(20, 22, 34)
 contorno.OutlineTransparency = 0
 contorno.DepthMode = Enum.HighlightDepthMode.Occluded
 contorno.Parent = objeto
 objeto.Parent = parent
 return objeto
end

local function moverDrop(objeto, pos, angulo)
 if not objeto or not objeto.Parent then return end
 local cf = CFrame.new(pos) * CFrame.Angles(0, angulo or 0, 0)
 if objeto:IsA("Model") then objeto:PivotTo(cf) else objeto.CFrame = cf end
end

local function mostrarDrop(info)
 if typeof(info.pos) ~= "Vector3" or dropsVisuais[info.id] then return end
 local pasta = workspace:FindFirstChild("MiningDropsLocal")
 if not pasta then
  pasta = Instance.new("Folder")
  pasta.Name = "MiningDropsLocal"
  pasta.Parent = workspace
 end
 local angulo = (info.id * 2.39996) % (math.pi * 2)
 local raio = 1.2 + (info.id % 3) * .38
 local base = posicaoNoChao(info.pos, Vector3.new(math.cos(angulo) * raio, 0, math.sin(angulo) * raio), .44)
 local lista = { { objeto = criarMiniMinerio(info, pasta), pos = base } }
 if info.hatId then
  local angHat = angulo + 2.2
  local posHat = posicaoNoChao(info.pos, Vector3.new(math.cos(angHat) * (raio + 1), 0, math.sin(angHat) * (raio + 1)), .7)
  table.insert(lista, { objeto = criarMiniHat(info, pasta), pos = posHat, angulo = angHat })
 end
 for _, item in ipairs(lista) do moverDrop(item.objeto, item.pos, item.angulo) end
 dropsVisuais[info.id] = { itens = lista, criado = os.clock(), coletando = false }
end

local function coletarDrop(id)
 local drop = dropsVisuais[id]
 if not drop then return end
 drop.coletando = true
 drop.inicioColeta = os.clock()
 for _, item in ipairs(drop.itens) do item.inicio = item.pos end
end

RunService.RenderStepped:Connect(function()
 local agora = os.clock()
 local raiz = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
 for id, drop in pairs(dropsVisuais) do
  if agora - drop.criado > 120 then
   for _, item in ipairs(drop.itens) do item.objeto:Destroy() end
   dropsVisuais[id] = nil
  else
   local t = drop.coletando and math.clamp((agora - drop.inicioColeta) / .42, 0, 1) or 0
   for j, item in ipairs(drop.itens) do
    local pos
    if drop.coletando and raiz then
     local alvo = raiz.Position + Vector3.new(0, 1.2, 0)
     pos = item.inicio:Lerp(alvo, t * t * (3 - 2 * t)) + Vector3.new(0, math.sin(t * math.pi) * 1.15, 0)
    else
     pos = item.pos + Vector3.new(0, math.sin((agora - drop.criado) * 3 + j) * .12, 0)
    end
    moverDrop(item.objeto, pos, item.angulo)
   end
   if drop.coletando and t >= 1 then
    for _, item in ipairs(drop.itens) do item.objeto:Destroy() end
    dropsVisuais[id] = nil
   end
  end
 end
end)

R.FeedbackMina.OnClientEvent:Connect(function(info)
 if type(info)~="table" then return end
 if info.tipo=="dropMinerio" then
  mostrarDrop(info)
 elseif info.tipo=="dropColetado" then
  coletarDrop(info.id)
 elseif info.tipo=="golpe" then
  if info.pos then numero(info.pos,info.dano or 0,TIER[info.chefe and "chefe" or info.variante or "comum"] or TIER.comum,info.quebrou) end
 elseif info.tipo=="quebrou" then
  local tier=TIER[info.variante or "comum"] or TIER.comum
  if info.pos and not ReferenceVFX.Break(player.Character and player.Character:FindFirstChild("Picareta"),info.pos) then explosao(info.pos,tier) end
  -- coleta e quebra do chefe tocam pelo UIAudio (AMS_UI); aqui fica so a quebra da rocha no mundo
  if not info.chefe then Som.quebra(info.variante,info.pos) end
  tremerCamera(tier.shake*1.6)
 elseif info.tipo=="hat" then
  -- som do drop: UIAudio (AMS_UI)
 elseif info.tipo=="cheia" or info.tipo=="bloqueada" then
  -- som de erro: UIAudio (AMS_UI)
 end
end)
