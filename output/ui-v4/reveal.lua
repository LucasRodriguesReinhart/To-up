nextReveal = function()
 if revealBusy or bannerBusy or #reveals==0 or not overlayLayer or not overlayLayer.Parent then return end
 if rewardBlocked() then pump();return end
 revealBusy=true;player:SetAttribute("RevealOpen",true)
 local o=table.remove(reveals,1)
 local r=T.rar(o.rarity);local col=r.cor
 local holder=T.new("CanvasGroup",{Name="Reveal",Size=UDim2.fromScale(1,1),BackgroundColor3=P.ink,BackgroundTransparency=.2,ZIndex=60},overlayLayer)
 local shield=T.new("TextButton",{Name="Shield",Text="",Selectable=false,AutoButtonColor=false,BackgroundTransparency=1,Size=UDim2.fromScale(1,1)},holder)
 local stage=T.frame(holder,"Stage",0,0,0,0,nil,1)
 local art=T.frame(stage,"Art",0,0,0,0,nil,1)
 local tag=T.text(stage,"New",o.tag or "NOVA DESCOBERTA",0,0,0,0,24,P.gold,T.CENTER,"display",2)
 local name=T.text(stage,"Name",o.name or "",0,0,0,0,42,P.text,T.CENTER,"title",2.5)
 name.TextWrapped=true
 local rarity=T.text(stage,"Rarity",r.nome,0,0,0,0,30,col,T.CENTER,"title",2)
 local subtitle=T.text(stage,"Subtitle",o.subtitle or "",0,0,0,0,17,P.text2,T.CENTER,"body",1)
 subtitle.TextWrapped=true
 local closed,connection=false,nil
 local previous=GuiService.SelectedObject
 local function close()
  if closed then return end;closed=true
  if connection then connection:Disconnect() end
  activeRevealLayout=nil
  animate(holder,.15,{GroupTransparency=1})
  task.delay(.17,function()
   holder:Destroy();revealBusy=false;player:SetAttribute("RevealOpen",false)
   if previous and previous.Parent and previous.Visible then GuiService.SelectedObject=previous end
   callOnce(o);nextReveal();nextBanner()
  end)
 end
 local claim=T.button(stage,"Claim",o.button or "Continuar",0,0,280,52,col,close,{size=23})
 local lastSize
 activeRevealLayout=function()
  if closed then return end
  local vw,vh=getSize()
  local w,h=math.min(1000,vw-40),vh-24
  stage.Size=UDim2.fromOffset(w,h);stage.Position=UDim2.fromOffset((vw-w)/2,12)
  local compact=h<520
  local aw=compact and w*.5 or w*.70
  local ah=compact and h-20 or h-185
  local ax=compact and 0 or (w-aw)/2
  local ay=compact and 5 or 35
  local ix=compact and w*.49 or 0
  local iw=compact and w*.51 or w
  art.Position=UDim2.fromOffset(ax,ay);art.Size=UDim2.fromOffset(aw,ah)
  tag.Position=UDim2.fromOffset(ix,compact and h*.14 or 0);tag.Size=UDim2.fromOffset(iw,32)
  name.Position=UDim2.fromOffset(ix,compact and h*.30 or h-154);name.Size=UDim2.fromOffset(iw,compact and 78 or 58);name.TextSize=compact and 34 or 42
  rarity.Position=UDim2.fromOffset(ix,compact and h*.55 or h-102);rarity.Size=UDim2.fromOffset(iw,34)
  subtitle.Position=UDim2.fromOffset(ix,compact and h*.65 or h-70);subtitle.Size=UDim2.fromOffset(iw,30)
  claim.Position=UDim2.fromOffset(ix+(iw-280)/2,h-54)
  local signature=aw..":"..ah
  if lastSize~=signature then
   lastSize=signature;T.clear(art)
   N.rays(art,aw/2,ah*.53,math.min(aw,ah)*.65,col,10,.72)
   if o.kind=="pet" then T.characterViewport(art,o.id,0,0,aw,ah,{fullBody=true,padding=.98})
   else T.preview(art,o.kind or "hat",o.id,0,0,aw,ah,true) end
  end
 end
 activeRevealLayout()
 shield.Activated:Connect(close)
 connection=UIS.InputBegan:Connect(function(input) if input.KeyCode==Enum.KeyCode.Escape or input.KeyCode==Enum.KeyCode.ButtonB then close() end end)
 if UIS:GetLastInputType().Name:find("Gamepad") then GuiService.SelectedObject=claim end
 T.som("ui_popup")
 task.delay(math.clamp(o.duration or 7,3,12),close)
end
