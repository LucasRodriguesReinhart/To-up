-- O servidor determina o destino. Após chegar, imagem e nome ficam por cinco segundos.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local player=Players.LocalPlayer
local T=require(RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
local Config=require(RS:WaitForChild("Config"))
local Som=require(RS:WaitForChild("SomJogo"))
local gui=T.new("ScreenGui",{Name="IslandTransition",IgnoreGuiInset=true,ResetOnSpawn=false,DisplayOrder=1000},player:WaitForChild("PlayerGui"))
local root=T.new("CanvasGroup",{Name="Arrival",AnchorPoint=Vector2.new(.5,.5),Position=UDim2.fromScale(.5,.5),Size=UDim2.fromScale(1,1),BackgroundColor3=T.P.ink,BorderSizePixel=0,Visible=false},gui)
local art=T.image(root,"Scene","",0,0,0,0);art.Size=UDim2.fromScale(1,1);art.ScaleType=Enum.ScaleType.Crop
local shade=T.frame(root,"Shade",0,0,0,0,T.P.ink,.4);shade.Size=UDim2.fromScale(1,1)
local title=T.text(root,"Title","",0,0,0,0,56,T.P.text,T.CENTER,"display",3)
title.Size=UDim2.fromScale(.94,.8);title.Position=UDim2.fromScale(.03,.1);title.TextWrapped=true
local shield=T.new("TextButton",{Name="TravelShield",Text="",Size=UDim2.fromScale(1,1),BackgroundTransparency=1,Visible=false},root)
local revision,lastDestination=0,nil
local shell
local function menuOpen() return shell and ((shell:GetAttribute("OpenPage") or "")~="" or shell:GetAttribute("PopupOpen")==true) end
local fades={}
local function cancel() for _,tw in ipairs(fades) do tw:Cancel() end;table.clear(fades) end
local function resize()
 local v=gui.AbsoluteSize
 if player:GetAttribute("AreaTransition")~=nil then root.Size=UDim2.fromScale(1,1);root.Position=UDim2.fromScale(.5,.5);title.TextSize=v.Y<500 and 42 or 68
 else
  local factor=shell and shell:GetAttribute("UIScalePreference") or .85
  root.Size=UDim2.fromOffset(math.min(390*factor,v.X*.50),math.min(66*factor,v.Y*.15))
  root.Position=UDim2.fromScale(.5,.17);title.TextSize=(v.Y<500 and 23 or 29)*factor
 end
 local constraint=title:FindFirstChildOfClass("UITextSizeConstraint")
 if constraint then constraint.MinTextSize=title.TextSize;constraint.MaxTextSize=title.TextSize end
end
local function update()
 revision+=1;local token=revision;cancel()
 local id=player:GetAttribute("AreaTransition")
 if id~=nil then
  if lastDestination~=id then Som.tocar("portal_saida") end
  lastDestination=id
  local area=Config.areaPorId(id)
  title.Text=area and area.nome or "Praça Central"
  art.Image=area and T.areaImage(id) or T.Assets.lobby
  player:SetAttribute("TravelTransition",true)
  root.Visible=true;root.GroupTransparency=0;shield.Visible=true;resize()
 elseif lastDestination~=nil then
  lastDestination=nil;Som.tocar("portal_chegada")
  player:SetAttribute("TravelTransition",false);shield.Visible=false;resize();root.Visible=not menuOpen()
  task.delay(2.2,function()
   if token~=revision then return end
   local tw=T.tween(root,T.motionEnabled() and .25 or 0,{GroupTransparency=1});table.insert(fades,tw)
   tw.Completed:Once(function() if token==revision then root.Visible=false end end)
  end)
 else player:SetAttribute("TravelTransition",false) end
end
gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)
player:GetAttributeChangedSignal("AreaTransition"):Connect(update)
update()


local function hook(o)
 if o.Name~="ExpeditionUI" then return end
 shell=o
 local function suppress()
  if player:GetAttribute("AreaTransition")==nil and menuOpen() then root.Visible=false end
 end
 o:GetAttributeChangedSignal("OpenPage"):Connect(suppress)
 o:GetAttributeChangedSignal("PopupOpen"):Connect(suppress)
 o:GetAttributeChangedSignal("UIScalePreference"):Connect(resize)
 suppress()
end
local pg=player:WaitForChild("PlayerGui")
for _,o in ipairs(pg:GetChildren()) do hook(o) end
pg.ChildAdded:Connect(hook)
