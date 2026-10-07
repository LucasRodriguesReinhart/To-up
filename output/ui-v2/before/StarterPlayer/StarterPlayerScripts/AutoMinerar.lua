-- Select a rock, approach its actual surface, then request a server-validated strike.
-- Arrastar (estilo Unboxing Simulator): segure o botao esquerdo (ou ligue o Hold Mode com T / botao,
-- ou segure RT no controle) e passe o cursor sobre outros minerios. Sem alvo, o minerio sob o cursor
-- vira alvo na hora; com alvo, o ultimo minerio apontado fica na fila e o personagem vai ate ele
-- sozinho quando o atual quebrar. O cliente so escolhe o alvo: o servidor continua validando cada golpe.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local UIS=game:GetService("UserInputService")
local Run=game:GetService("RunService")
local Paths=game:GetService("PathfindingService")
local player=Players.LocalPlayer
local mouse=player:GetMouse()
local Geometry=require(RS:WaitForChild("MiningGeometry"))
local Config=require(RS:WaitForChild("Config"))
local remote=RS:WaitForChild("Remotes").Golpear
local target,highlight
local proximo,highlightProximo
local version=0
local waypoints,index,pathBusy,lastPlan=nil,1,false,0
local lastRequest=0
local lastServerRequest=0
local confirmado=-1
-- estado do arrasto
local segurandoMouse=false
local segurandoGatilho=false
local holdMode=false
local toques={} -- InputObject -> true (toques que comecaram fora da interface)
local ultimoToque=nil
local function limparProximo()
 proximo=nil
 if highlightProximo then highlightProximo:Destroy() highlightProximo=nil end
end
local function selectRock(rock)
 version+=1
 target=rock waypoints=nil index=1
 player:SetAttribute("MiningTargetSelected",rock~=nil)
 if highlight then highlight:Destroy() highlight=nil end
 if rock==nil or rock==proximo then limparProximo() end
 if rock then
  highlight=Instance.new("Highlight")
  highlight.FillColor=Color3.fromRGB(255,240,140) highlight.FillTransparency=.8
  highlight.OutlineColor=Color3.fromRGB(255,230,90)
  highlight.DepthMode=Enum.HighlightDepthMode.Occluded
  highlight.Adornee=rock.Parent:FindFirstChild("Visual") or rock
  highlight.Parent=rock
 end
end
local function enfileirar(rock)
 if rock==proximo then return end
 limparProximo()
 proximo=rock
 highlightProximo=Instance.new("Highlight")
 highlightProximo.FillTransparency=1
 highlightProximo.OutlineColor=Color3.fromRGB(255,255,255)
 highlightProximo.OutlineTransparency=.15
 highlightProximo.DepthMode=Enum.HighlightDepthMode.Occluded
 highlightProximo.Adornee=rock.Parent:FindFirstChild("Visual") or rock
 highlightProximo.Parent=rock
end
local function rockFromPart(hit)
 local group=hit
 while group and group~=workspace do
  local candidate=group:FindFirstChild("Hitbox")
  if Geometry.valid(candidate) then return candidate end
  group=group.Parent
 end
end
local function clickedRock()
 local hit=mouse.Target
 if not hit then return end
 return rockFromPart(hit)
end
-- minerio sob um ponto da tela. Raycast novo a cada chamada (mouse.Target so atualiza quando o mouse
-- se mexe, e a camera anda junto com o personagem). Atravessa partes sem colisao (pets, efeitos) e,
-- se o raio fino nao pegar nada, tenta um raio grosso para minerios pequenos / dedo no celular.
local RAIO_TOLERANCIA=1.6
local function rockAtScreen(pos)
 local cam=workspace.CurrentCamera
 if not cam then return end
 local ray=cam:ScreenPointToRay(pos.X,pos.Y)
 local ignore={player.Character}
 local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude
 for tentativa=1,2 do
  table.clear(ignore) ignore[1]=player.Character
  for _=1,6 do
   params.FilterDescendantsInstances=ignore
   local r
   if tentativa==1 then r=workspace:Raycast(ray.Origin,ray.Direction*500,params)
   else r=workspace:Spherecast(ray.Origin,RAIO_TOLERANCIA,ray.Direction*500,params) end
   if not r then break end
   local rock=rockFromPart(r.Instance)
   if rock then return rock end
   if r.Instance.Transparency<1 and r.Instance.CanCollide then break end
   table.insert(ignore,r.Instance)
  end
 end
end
local function pointerRock()
 if segurandoGatilho then
  local cam=workspace.CurrentCamera
  if cam then
   local inset=game:GetService("GuiService"):GetGuiInset()
   return rockAtScreen(cam.ViewportSize/2-inset) -- centro da tela (ScreenPointToRay soma o inset)
  end
  return
 end
 if UIS.TouchEnabled and not UIS.MouseEnabled then
  return ultimoToque and rockAtScreen(ultimoToque.Position)
 end
 return rockAtScreen(Vector2.new(mouse.X,mouse.Y))
end
local ultimoAnalogico=0
local TECLAS_MOV={Enum.KeyCode.W,Enum.KeyCode.A,Enum.KeyCode.S,Enum.KeyCode.D,Enum.KeyCode.Space}
local function movendoManual()
 -- andando com teclado/analogico: o arrasto nao puxa o personagem de volta para um minerio
 if os.clock()-ultimoAnalogico<.35 then return true end
 for _,k in ipairs(TECLAS_MOV) do if UIS:IsKeyDown(k) then return true end end
 return false
end
local function arrastando()
 if movendoManual() then return false end
 if segurandoGatilho or segurandoMouse then return true end
 if holdMode then
  if UIS.TouchEnabled and not UIS.MouseEnabled then return ultimoToque~=nil end
  return true
 end
 return false
end
local function pararMovimento()
 selectRock(nil)
 local c=player.Character local h=c and c:FindFirstChildOfClass("Humanoid")
 if h then h:Move(Vector3.zero) end
end

-- Hold Mode (UI V2): botao de alternancia no canto inferior direito + tecla T.
-- O botao usa o Design System (ExpeditionUI.Theme) e acompanha a escala da interface.
local Theme=require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local gui=Instance.new("ScreenGui")
gui.Name="HoldModeGui" gui.ResetOnSpawn=false gui.DisplayOrder=2 gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling
gui.Parent=player:WaitForChild("PlayerGui")
local botao
local function textoBotao()
 local tecla=(UIS.TouchEnabled and not UIS.MouseEnabled) and "" or "  (T)"
 return (holdMode and "HOLD: ON" or "HOLD: OFF")..tecla
end
local function atualizarBotao()
 if not botao then return end
 Theme.setTone(botao, holdMode and Theme.P.success or Theme.P.neutral)
 local caption=botao.Face:FindFirstChild("Caption")
 if caption then caption.Text=textoBotao() end
end
local function setHoldMode(on)
 holdMode=on
 player:SetAttribute("HoldMode",on)
 if not on then ultimoToque=nil end
 atualizarBotao()
end
local function construirBotao()
 if botao then botao:Destroy() end
 local v=gui.AbsoluteSize
 local s=math.clamp(math.min(v.X/1440, v.Y/850), .5, 1.45)
 local w,h=math.floor(176*s),math.floor(48*s)
 local movel=UIS.TouchEnabled and not UIS.MouseEnabled
 botao=Theme.button(gui,"HoldMode",textoBotao(),0,0,w,h,holdMode and Theme.P.success or Theme.P.neutral,function()
  setHoldMode(not holdMode)
 end,{icon="pickaxe",size=math.floor(17*s)})
 botao.AnchorPoint=Vector2.new(1,1)
 botao.Position=UDim2.new(1,-math.floor(24*s),1,-math.floor(movel and 200*s or 24*s))
 Theme.hint(botao,"Segure para minerar em sequência: com o Hold ligado, basta passar o cursor pelos minérios.","above")
end
construirBotao()
UIS.LastInputTypeChanged:Connect(construirBotao)
gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(construirBotao)

UIS.InputBegan:Connect(function(input,processed)
 if processed then return end
 local tipo=input.UserInputType
 if tipo==Enum.UserInputType.MouseButton1 or tipo==Enum.UserInputType.Touch then
  if tipo==Enum.UserInputType.MouseButton1 then segurandoMouse=true
  else toques[input]=true ultimoToque=input end
  local hit=clickedRock()
  if tipo==Enum.UserInputType.Touch then hit=rockAtScreen(input.Position) or hit
  elseif not hit then hit=rockAtScreen(Vector2.new(mouse.X,mouse.Y)) end
  if hit then selectRock(hit) end
 elseif input.KeyCode==Enum.KeyCode.ButtonR2 then
  segurandoGatilho=true
  local hit=pointerRock() if hit then selectRock(hit) end
 elseif input.KeyCode==Enum.KeyCode.T then
  setHoldMode(not holdMode)
 elseif input.KeyCode==Enum.KeyCode.W or input.KeyCode==Enum.KeyCode.A or input.KeyCode==Enum.KeyCode.S
  or input.KeyCode==Enum.KeyCode.D or input.KeyCode==Enum.KeyCode.Space then
  pararMovimento()
 end
end)
UIS.InputChanged:Connect(function(input)
 if input.KeyCode==Enum.KeyCode.Thumbstick1 and input.Position.Magnitude>.2 then ultimoAnalogico=os.clock() selectRock(nil) end
 if input.UserInputType==Enum.UserInputType.Touch and toques[input] then ultimoToque=input end
end)
UIS.InputEnded:Connect(function(input)
 if input.UserInputType==Enum.UserInputType.MouseButton1 then segurandoMouse=false
 elseif input.UserInputType==Enum.UserInputType.Touch then
  toques[input]=nil
  if ultimoToque==input then ultimoToque=nil end
 elseif input.KeyCode==Enum.KeyCode.ButtonR2 then segurandoGatilho=false end
end)
UIS.WindowFocusReleased:Connect(function() segurandoMouse=false segurandoGatilho=false end)
player.CharacterAdded:Connect(function() selectRock(nil) end)
player:GetAttributeChangedSignal("CurrentAreaId"):Connect(function()
 selectRock(nil)
 local char=player.Character local h=char and char:FindFirstChildOfClass("Humanoid")
 local root=char and char:FindFirstChild("HumanoidRootPart")
 if h and root then h:Move(Vector3.zero) h:MoveTo(root.Position) end
end)
-- arrasto: le o minerio sob o cursor a cada frame
Run.Heartbeat:Connect(function()
 if proximo and not Geometry.valid(proximo) then limparProximo() end
 if not arrastando() then return end
 local rock=pointerRock()
 if not rock then return end
 if not target or not Geometry.valid(target) then selectRock(rock)
 elseif rock==target then limparProximo() -- voltou para o atual: cancela a fila
 else enfileirar(rock) end
end)
task.spawn(function()
 for _=1,12 do
  if pcall(function() game:GetService("StarterGui"):SetCoreGuiEnabled(Enum.CoreGuiType.Backpack,false) end) then break end
  task.wait(.4)
 end
end)
task.spawn(function()
 while true do
  task.wait(.08)
  if target and not Geometry.valid(target) then
   -- o atual quebrou: segue para o proximo da fila
   if proximo and Geometry.valid(proximo) then selectRock(proximo) else selectRock(nil) end
  end
  if not target then continue end
  local c=player.Character local h=c and c:FindFirstChildOfClass("Humanoid")
  local root=c and c:FindFirstChild("HumanoidRootPart")
  if not h or not root or h.Health<=0 then continue end
  local goal=Geometry.destination(target,root.Position)
  local distance=(Vector3.new(goal.X,root.Position.Y,goal.Z)-root.Position).Magnitude
  if Geometry.canReach(c,target,Geometry.ClientReach) then
   h:Move(Vector3.zero,false)
   h:MoveTo(root.Position)
   local look=Vector3.new(target.Position.X,root.Position.Y,target.Position.Z)
   if (look-root.Position).Magnitude>.01 then root.CFrame=CFrame.lookAt(root.Position,look) end
   -- intervalo real vem da picareta (o servidor publica em IntervaloGolpe e valida de novo)
   local swingStart=c:GetAttribute("MiningSwingStart")
   if swingStart and swingStart>=lastServerRequest-.05 then confirmado=lastRequest end
   local espera=confirmado==lastRequest and ((player:GetAttribute("IntervaloGolpe") or Config.COOLDOWN_GOLPE)+.03) or .14
   if os.clock()-lastRequest>=espera then
    -- sem swing confirmado: o servidor recusou (ex.: posicao ainda chegando) -> reenvia em .14 s, nao em 1 intervalo
    lastRequest=os.clock()
    lastServerRequest=workspace:GetServerTimeNow()
    remote:FireServer(target)
   end
  elseif not c:GetAttribute("MiningSwingActive") then
   local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude
   params.FilterDescendantsInstances={c,target.Parent} params.RespectCanCollide=true
   local obstacle=workspace:Raycast(root.Position,goal-root.Position,params)
   if not obstacle and math.abs(target.Position.Y-root.Position.Y)<8 then
    waypoints=nil h:MoveTo(goal)
   else
    if not pathBusy and os.clock()-lastPlan>1 then
     pathBusy=true lastPlan=os.clock()
     local revision=version
     task.spawn(function()
      local path=Paths:CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=true,WaypointSpacing=4})
      local ok=pcall(function() path:ComputeAsync(root.Position,goal) end)
      if revision==version and ok and path.Status==Enum.PathStatus.Success then
       waypoints=path:GetWaypoints() index=2
      end
      pathBusy=false
     end)
    end
    local point=waypoints and waypoints[index]
    if point then
     if (point.Position-root.Position).Magnitude<3 then index+=1 point=waypoints[index] end
     if point then
      if point.Action==Enum.PathWaypointAction.Jump then h.Jump=true end
      h:MoveTo(point.Position)
     end
    else h:MoveTo(goal) end
   end
  end
 end
end)

