from pathlib import Path
root=Path(__file__).parent/'src'
def read(k):return (root/(k.replace('.','/')+'.lua')).read_text(encoding='utf-8')
def write(k,s):(root/(k.replace('.','/')+'.lua')).write_text(s,encoding='utf-8')
k='StarterPlayer.StarterPlayerScripts.ExpeditionClient';s=read(k)
s=s.replace('function ctx.close()\n','function ctx.close()\n if ctx.summonBusy then return end\n')
s=s.replace('function ctx.open(page)\n','function ctx.open(page)\n if ctx.summonBusy then return end\n local previousCollection=ctx.collection\n')
a=s.index('\tif ctx.page == page then',s.index('function ctx.open'));b=s.index('\n\tif not PAGE[page]',a)
s=s[:a]+''' if ctx.page == page then
  if page=="Inventory" and previousCollection~=ctx.collection then ctx.search="";ctx.selected=nil;drawWindow(false) end
  return
 end'''+s[b:]
# Store data updates until the animation's impact callback.
s=s.replace('local function acceptData(data)\n','local function acceptData(data)\n if ctx.summonBusy and not ctx.revealCommitted then ctx.pendingSummonData=data;return end\n')
s=s.replace('local function acceptData(data)','local function acceptData(data)',1)
# Forward callback assigned after acceptData is in scope.
s=s.replace('connect(R.AtualizarDados.OnClientEvent,','ctx.releaseSummonData=function() local d=ctx.pendingSummonData;ctx.pendingSummonData=nil;if d then acceptData(d) end end\nconnect(R.AtualizarDados.OnClientEvent,')
a=s.index('local function showResults(');b=s.index('\nfunction ctx.showLastSummon()',a)
s=s[:a]+'''local function showResults(results,count,playAudio)
 if #results==0 then return end
 local best=results[1]
 for _,r in ipairs(results) do if T.rar(r.raridade).ordem>T.rar(best.raridade).ordem then best=r end end
 if playAudio~=false then Som.drop(best.raridade) end
 local cols=math.min(#results,ctx.portrait and 2 or 4)
 local width=math.max(480,cols*204+40)
 ctx.popup(#results==1 and "Unidade recebida" or "Multi Open · 4 unidades",function(p,w,h)
  local gap=10;local cw=(w-(cols-1)*gap)/cols
  local cardH=math.min(h-64,cw*1.25+64)
  local list=T.scroll(p,"Results",0,0,w,h-66,P.violet)
  list.CanvasSize=UDim2.fromOffset(0,math.ceil(#results/cols)*(cardH+gap))
  for i,result in ipairs(results) do
   local r=T.rar(result.raridade);local def=Config.petPorId(result.petId)
   local card=T.tile(list,"Result_"..i,((i-1)%cols)*(cw+gap),math.floor((i-1)/cols)*(cardH+gap),cw,cardH,result.raridade,{selected=false})
   T.characterViewport(card,result.petId,4,6,cw-8,cardH-74,{fullBody=true,padding=1.05})
   T.text(card,"Name",def and def.nome or result.nome,6,cardH-65,cw-12,30,21,P.text,T.CENTER,"title")
   T.text(card,"Rarity",r.nome,6,cardH-33,cw-12,24,16,r.cor:Lerp(WHITE,.35),T.CENTER,"title")
   if result.novo then T.chip(card,"New","NOVO",7,7,22,P.success,{size=12,solid=true}) end
  end
  T.button(p,"Continue","Continuar",0,h-52,(w-12)/2,52,P.neutral,closePopup)
  T.button(p,"Again",count>1 and "Multi Open" or "Summon 1",(w+12)/2,h-52,(w-12)/2,52,P.violet,function() if ctx.summonBusy then return end;closePopup();ctx.startSummon(count>1 and "multi" or "single") end)
 end,width,480,{color=T.rar(best.raridade).cor})
end
'''+s[b:]
a=s.index('function ctx.startSummon(');b=s.index('\nfunction ctx.levelUp',a)
s=s[:a]+'''function ctx.startSummon(mode)
 if ctx.summonBusy or not ctx.data then return end
 mode=mode=="multi" and "multi" or "single"
 if mode=="multi" and not (ctx.data.passes and ctx.data.passes.MultiOpen) then ctx.invoke("ComprarRobux","MultiOpen");return end
 local areaId=ctx.bannerArea
 if not ctx.nearBanner(areaId) then ctx.toast("Viaje até o banner para invocar",nil,"info");return end
 ctx.summonBusy=true;ctx.revealCommitted=false;ctx.refresh()
 local id=game:GetService("HttpService"):GenerateGUID(false)
 task.spawn(function()
  local result=ctx.invoke("RolarGacha",areaId,mode,id)
  if not result or not result.ok then
   ctx.summonBusy=false;ctx.revealCommitted=true
   if ctx.releaseSummonData then ctx.releaseSummonData() end
   ctx.refresh();return
  end
  ctx.lastSummonResults=result.results;ctx.lastSummonCount=result.count
  player:SetAttribute("RevealOpen",true)
  Som.tocar("invocar_inicio")
  T.starOpening(popupLayer,virtualW,virtualH,function()
   ctx.revealCommitted=true
   screen:SetAttribute("SummonPhase","reveal")
   if ctx.releaseSummonData then ctx.releaseSummonData() end
   local ack=R:FindFirstChild("ConcluirReveal");if ack then ack:FireServer(result.requestId) end
   showResults(result.results,result.count,true)
  end,{count=result.count,onFinish=function()
   ctx.summonBusy=false;player:SetAttribute("RevealOpen",false);screen:SetAttribute("SummonPhase","complete");ctx.refresh()
  end})
  screen:SetAttribute("SummonPhase","anticipation")
 end)
end
'''+s[b:]
s=s.replace('\tif d.passes and d.passes.VIP then table.insert(list, { "VIP", "VIP", P.gold, "vip", "+10% de moedas nas vendas" }) end','')
s=s.replace('function ctx.setUIScale(value)','''function ctx.setMovementSpeed(value)
 local res=ctx.invoke("AtualizarVelocidade",value)
 if res and res.ok then ctx.data.movementSpeed=res.value;ctx.refresh() end
end
function ctx.setUIScale(value)''')
write(k,s)
k='ReplicatedStorage.ExpeditionUI.Menus';s=read(k)
s=s.replace('local viewportH = stageH - (narrow and 274 or 184)','local viewportH = stageH - (narrow and 274 or 240)')
s=s.replace('local namesY = stageH - (narrow and 234 or 196)','local namesY = stageH - (narrow and 234 or 186)')
a=s.index('\tif ctx.summonBusy then',s.index('function M.summon'));b=s.index('\n\tlocal pity =',a)
s=s[:a]+''' if ctx.summonBusy then
  text(stage,"Progress","Preparando estrelas…",12,actionY,centerW-24,52,20,WHITE,T.CENTER,"title")
 else
  ctx.onSummonProgress=nil
  if unlocked then
   local owns=d.passes and d.passes.MultiOpen
   local cost=free and 0 or g.custo
   action(ctx,stage,"Summon1","Summon 1 · "..(cost==0 and "Grátis" or T.format(cost)),12,actionY,bw,52,function() ctx.startSummon("single") end,near and d.moeda>=cost,not near and "Viaje até o banner." or "Moedas insuficientes.",P.success,"StartSummon",{size=20})
   local multiCost=g.custo*(Mon.MULTI_OPEN_COUNT-(free and 1 or 0))
   T.button(stage,"MultiOpen",owns and ("Multi Open · "..T.format(multiCost)) or "Multi Open · PREMIUM",24+bw,actionY,bw,52,owns and P.violet or P.gold,function()
    if owns then ctx.startSummon("multi") else ctx.invoke("ComprarRobux","MultiOpen") end
   end,{size=18})
   T.hint(stage.MultiOpen,"4 estrelas ao mesmo tempo. Cada estrela mantém seu custo em moedas.")
  else
   areaUnlock(ctx,stage,a,12,actionY,bw,52)
   T.button(stage,"ViewAreas","Ver ilhas",24+bw,actionY,bw,52,P.neutral,function() ctx.open("Areas") end)
  end
 end'''+s[b:]
needle=' y+=T.section(scroll,"Mixagem de áudio",0,y,colW,P.accent)'
assert needle in s
s=s.replace(needle,''' y+=T.section(scroll,"Velocidade de movimento",0,y,colW,P.info)
 local speedRow=panel(scroll,"MovementSpeed",0,y,colW,152)
 local owns=ctx.data.passes and ctx.data.passes.Speed2x
 local current=owns and (ctx.data.movementSpeed or 1) or 1
 text(speedRow,"Description",owns and "Escolha quanto do seu bônus quer usar." or "Normal: 1x · 2X Speed libera o limite maior.",14,10,colW-28,30,14,P.text2)
 local bw=(colW-36)/5
 for i,value in ipairs({1,1.25,1.5,1.75,2}) do
  T.button(speedRow,"Speed_"..i,string.format("%.2gx",value),10+(i-1)*(bw+4),48,bw,44,current==value and P.info or P.neutral,function()
   if value>1 and not owns then ctx.invoke("ComprarRobux","Speed2x") else ctx.setMovementSpeed(value) end
  end,{size=16})
 end
 text(speedRow,"Limit",owns and "Preferência salva · limite 2x" or "Toque em uma opção premium para desbloquear.",14,108,colW-28,30,13,owns and P.success or P.gold)
 y+=166
 y+=T.section(scroll,"Mixagem de áudio",0,y,colW,P.accent)''')
write(k,s)
k='ReplicatedStorage.ExpeditionUI.Theme';s=read(k);a=s.index('function T.starOpening(');s=s[:a]+'''function T.starOpening(parent,w,h,onImpact,opts)
 opts=opts or {};local count=opts.count or 1
 local overlay=T.new("CanvasGroup",{Name="StarOpening",Size=UDim2.fromScale(1,1),BackgroundColor3=P.ink,BackgroundTransparency=.10,ZIndex=80,Active=true},parent)
 local shield=T.new("TextButton",{Name="OpeningShield",Text="",Size=UDim2.fromScale(1,1),BackgroundTransparency=1,ZIndex=80},overlay)
 local stars={};local size=math.min(count>1 and 160 or 230,h*.48,w/(count+1))
 for i=1,count do
  local star=T.icon(overlay,"summon",0,0,size,size);star.ZIndex=81;star.AnchorPoint=Vector2.new(.5,.5);star.Position=UDim2.fromScale(i/(count+1),.47)
  local sc=T.new("UIScale",{Scale=.2},star);table.insert(stars,{star=star,scale=sc})
  T.tween(sc,.26,{Scale=1},Enum.EasingStyle.Back)
 end
 local flash=T.frame(overlay,"Impact",0,0,0,0,WHITE,1);flash.Size=UDim2.fromScale(1,1);flash.ZIndex=84
 local phase="anticipation";local impact=false;local finished=false
 local function finish()
  if finished then return end;finished=true;overlay:Destroy()
  if opts.onFinish then opts.onFinish() end
 end
 local function reveal()
  if impact or finished then return end;impact=true;phase="reveal"
  overlay:SetAttribute("Phase",phase)
  for _,entry in ipairs(stars) do entry.star.Visible=false end
  flash.BackgroundTransparency=T.motionEnabled() and .35 or 1
  -- One impact event is the only point that reveals cards, updates UI and plays rarity audio.
  if onImpact then onImpact() end
  T.tween(overlay,.18,{GroupTransparency=1});task.delay(.19,finish)
 end
 local skip=T.button(overlay,"Skip","Pular",w/2-60,h-66,120,40,P.neutral,reveal,{size=15,sound=false});skip.ZIndex=85
 overlay:SetAttribute("Phase",phase)
 overlay.Destroying:Once(function() if not finished then finished=true;if opts.onFinish then opts.onFinish() end end end)
 if not T.motionEnabled() then task.delay(.15,reveal);return overlay end
 task.delay(.28,function()
  if finished or impact then return end
  for _,e in ipairs(stars) do T.tween(e.star,.22,{Rotation=-14});T.tween(e.scale,.22,{Scale=.84}) end
 end)
 task.delay(.52,function()
  if finished or impact then return end
  for _,e in ipairs(stars) do T.tween(e.star,.16,{Rotation=16});T.tween(e.scale,.16,{Scale=1.28}) end
 end)
 task.delay(.69,reveal)
 return overlay
end
return T
''';write(k,s)
print('Navigation, summon presentation and settings patched')
