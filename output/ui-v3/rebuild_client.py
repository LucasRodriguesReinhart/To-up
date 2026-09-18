from pathlib import Path
p=Path('output/ui-v3/src/StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua')
s=p.read_text(encoding='utf-8')
s=s.replace('local FULLSCREEN = {Inventory=true}', 'local FULLSCREEN = {Inventory=true}')
a=s.index('drawHeader = function()')
b=s.index('\ndrawBody = function()',a)
s=s[:a]+'''drawHeader = function()
 if not window then return 0 end
 local title,icon,col,sub=pageTitle()
 local full=fullPage()
 if ctx.page=="Events" then title=ctx.eventsTab=="Index" and "Coleção" or "Recompensas diárias" end
 local banner=window:FindFirstChild("Banner")
 if banner then banner.Title.Text=title end
 local tabsRoot=window:FindFirstChild("Tabs");if tabsRoot then tabsRoot:Destroy() end
 local items,current,tcol,onPick=tabsFor()
 if items then
  local ww=window.Size.X.Offset
  local inline=not(ctx.portrait or ctx.compact)
  local th=inline and 48 or 44
  local tw=math.min(#items*140,ww-40)
  local tx=inline and (full and (ww-tw)/2 or ww-tw-96) or 20
  if inline and tx<400 and not full then inline=false;tx=20 end
  local ty=inline and 12 or 64
  tabsRoot=T.frame(window,"Tabs",tx,ty,tw,th,nil,1)
  T.tabs(tabsRoot,"Segment",0,0,tw,th,items,current,tcol or P.accent,onPick)
  return inline and 0 or 44
 end
 return 0
end
''' + s[b:]
a=s.index('drawWindow = function(animate)')
b=s.index('\n-- ---------------------------------------------------------------- HUD',a)
s=s[:a]+'''drawWindow = function(animate)
 if not ctx.page then return end
 modalVersion+=1
 T.clear(modalLayer)
 local ww,wh,wx,wy=windowRect()
 local full=fullPage()
 local _,_,pageColor=pageTitle()
 if ctx.page=="Events" then pageColor=P.warning end
 window=T.panel(modalLayer,"Window",wx,wy,ww,wh,{bg=P.bg0,radius=full and 0 or 10,strokeColor=pageColor,strokeWidth=full and 0 or 2})
 window.Active=true
 local shadow
 if full then
  local inset=GuiService:GetGuiInset().Y/scale.Scale
  T.frame(window,"FullBleedTop",0,-inset,ww,inset+1,P.ink,0)
  window.BackgroundColor3=WHITE
  T.gradient(window,Color3.fromRGB(166,108,224),Color3.fromRGB(100,61,166),90)
  T.texture(window,"halftone",.65,WHITE,40)
  local lower=T.frame(window,"LowerShade",0,wh*.63,ww,wh*.37,P.ink,0)
  T.fade(lower,90,1,.06)
  local top=T.frame(window,"TopBand",0,0,ww,78,P.ink,0)
  T.gradient(top,Color3.fromRGB(23,12,36),Color3.fromRGB(89,45,127),90)
  T.texture(top,"halftone",.35,P.ink,32)
 else shadow=T.shadow(window,10,5,.3) end
 local bw=full and 280 or math.min(ww-112,ctx.page=="Events" and 380 or 330)
 local banner=T.frame(window,"Banner",20,10,bw,50,nil,1)
 if not full then
  T.slant(banner,"TitlePlate",-6,0,bw,50,pageColor,{top=pageColor,bottom=pageColor:Lerp(P.ink,.10),tilt=14})
  T.texture(banner,"halftone",.30,P.ink,20)
 end
 T.text(banner,"Title","",12,0,bw-24,50,ctx.page=="Events" and 27 or 32,P.text,T.LEFT,"display",2.3)
 local close=T.closeButton(window,ww-72,8,56,ctx.close)
 local extra=drawHeader()
 local headH=(full and 94 or 76)+extra
 bodyW,bodyH=ww-40,wh-headH-16
 body=T.frame(window,"Body",20,headH,bodyW,bodyH,nil,1)
 hud.Visible=not(full or ctx.portrait or ctx.compact)
 drawBody()
 if animate and not full then T.enter(window,.98,.15);if shadow then T.enter(shadow,.98,.15)end end
 if usingGamepad() then task.defer(function() if window and window.Parent then GuiService.SelectedObject=close end end) end
end
''' + s[b:]
a=s.index('drawHUD = function()')
b=s.index('\nlocal function nextPickaxe',a)
s=s[:a]+'''drawHUD = function()
 T.clear(hud);hudRefs={}
 local portrait,compact=ctx.portrait,ctx.compact
 local largeTargets=portrait or compact or Input.TouchEnabled
 screen:SetAttribute("BottomReserved",portrait and 152 or 0)
 local margin=portrait and 10 or 18
 local slot=portrait and 50 or compact and 52 or math.clamp(math.floor(virtualW*.053),64,86)
 local slots=math.clamp(ctx.data and tonumber(ctx.data.slotsPets) or 3,1,6)
 local hotW=slots*slot+(slots-1)*8
 local hotY=virtualH-slot-(portrait and 58 or 46)
 local currencyW=portrait and 314 or 378
 local row=T.frame(hud,"Currency",(virtualW-currencyW)/2,portrait and 12 or hotY-48,currencyW,40,nil,1)
 hudRefs.wallet=row
 T.icon(row,"coins",0,3,34,34)
 hudRefs.coins=T.text(row,"Coins",ctx.shownCoins and T.format(ctx.shownCoins) or "0",42,0,160,40,26,P.gold,T.LEFT,"number",2)
 local px=portrait and 193 or 230
 T.statIcon(row,"dano",px,7,28,28)
 hudRefs.power=T.text(row,"Power","0",px+34,0,currencyW-px-34,40,24,P.text,T.LEFT,"number",2)
 T.hint(row,"Poder por golpe · moedas obtidas na venda","above")
 local tw=portrait and math.min(virtualW-24,340) or compact and 270 or 320
 local tx=portrait and (virtualW-tw)/2 or virtualW-margin-tw
 local ty=portrait and 58 or 16
 local tracker=T.new("TextButton",{Name="Tracker",Text="",BackgroundColor3=P.bg0,BackgroundTransparency=.15,BorderSizePixel=0,Position=UDim2.fromOffset(tx,ty),Size=UDim2.fromOffset(tw,90)},hud)
 T.corner(tracker,6);hudRefs.trackerStroke=T.stroke(tracker,P.lineSoft,1)
 hudRefs.areaName=T.text(tracker,"Area","Praça central",12,8,tw-24,22,16,P.accent,T.LEFT,"title",1.5)
 hudRefs.questText=T.text(tracker,"Quest","Seu próximo objetivo",12,32,tw-24,25,16,P.text,T.LEFT,"body",false)
 hudRefs.questBar=T.progress(tracker,"QuestBar",12,70,tw-104,6,0,P.accent)
 hudRefs.questCount=T.text(tracker,"Count","",tw-84,60,72,24,14,P.text2,T.RIGHT,"number",1)
 T.bindInteraction(tracker,function() ctx.questArea=nil;ctx.open("Quests") end)
 T.hint(tracker,"Objetivo atual · abrir missões","below")
 hudRefs.buffs=T.scroll(hud,"Buffs",margin,portrait and 154 or 18,portrait and virtualW-20 or math.max(120,math.min(620,tx-margin-16)),32,P.violet)
 hudRefs.buffs.ScrollingDirection=Enum.ScrollingDirection.X;hudRefs.buffs.ScrollBarThickness=2;hudRefs.buffKeys=""
 local nw=portrait and 56 or compact and 62 or 78
 local nh=portrait and 62 or compact and 66 or 82
 local ng=6
 local navY=portrait and 202 or math.max(128,(virtualH-3*(nh+ng))/2-15)
 local dock=T.frame(hud,"Navigation",0,0,virtualW,virtualH,nil,1)
 hudRefs.rail={}
 for i,it in ipairs(NAV) do
  local right=i>=7
  local x=right and virtualW-margin-nw or margin+((i-1)%2)*(nw+ng)
  local y=navY+(right and i-7 or math.floor((i-1)/2))*(nh+ng)
  local b=T.new("TextButton",{Name=it.id,Text="",AutoButtonColor=false,BackgroundColor3=WHITE,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(nw,nh)},dock)
  T.corner(b,7)
  local navColor=T.Page[it.id] or P.violet
  T.gradient(b,navColor:Lerp(P.ink,.77),P.bg0,90)
  T.texture(b,"halftone",.3,navColor,24)
  T.stroke(b,P.ink,4,0)
  local edge=T.frame(b,"Rim",2,2,nw-4,nh-4,nil,1);T.corner(edge,5)
  local rim=T.stroke(edge,navColor,2,0)
  local isz=portrait and 34 or compact and 38 or 52
  T.icon(b,it.icon,(nw-isz)/2,4,isz,isz)
  T.text(b,"Label",it.label,2,nh-25,nw-4,23,portrait and 14 or 17,P.text,T.CENTER,"title",1.8)
  if it.key and not largeTargets then T.text(b,"Key",it.key,5,1,20,18,12,P.text2,T.LEFT,"caption",1) end
  T.bindInteraction(b,function() if it.id=="Inventory" then ctx.collection="pet" end;ctx.open(it.id) end,{onFocus=function(on) rim.Color=on and P.text or navColor end})
  T.hint(b,it.tip..(it.key and " · ["..it.key.."]" or ""),right and "left" or "right")
  hudRefs.rail[it.id]=b
 end
 hudRefs.hotbar=T.frame(hud,"Hotbar",(virtualW-hotW)/2,hotY,hotW,slot,nil,1)
 local bagW=portrait and virtualW-24 or math.max(hotW,400)
 local bagH=portrait and 44 or 28
 local bagY=hotY+slot+6
 local bag=T.frame(hud,"Bag",(virtualW-bagW)/2,bagY,bagW,bagH,nil,1);hudRefs.bagPanel=bag
 local sellW=portrait and 80 or 84
 hudRefs.bagTrack=T.progress(bag,"Track",0,0,bagW-sellW-6,bagH,0,P.violet)
 hudRefs.bag=T.text(hudRefs.bagTrack,"Count","MOCHILA 0 / 0",8,0,bagW-sellW-22,bagH,14,P.text,T.CENTER,"title",1)
 hudRefs.sell=T.button(bag,"SellShortcut","Vender",bagW-sellW,0,sellW,bagH,P.warning,function() ctx.open("Forge") end,{size=16})
 T.hint(hudRefs.sell,"Vender minérios com Ignis","above")
 hudRefs.signature=nil;updateHUD()
end
''' + s[b:]
a=s.index('\tlocal s\n',s.index('local function resize()'))
b=s.index('\tscale.Scale = s',a)
s=s[:a]+'''\tlocal s=math.clamp(math.min(v.X/1600,v.Y/900),1,1.35)
\tif ctx.portrait or ctx.compact then s=1 end
''' + s[b:]
p.write_text(s,encoding='utf-8',newline='\n')
t=Path('output/ui-v3/src/ReplicatedStorage/ExpeditionUI/Theme.lua')
theme=t.read_text(encoding='utf-8')
fragment=Path('output/ui-v3/characterViewport.lua').read_text(encoding='utf-8')
theme=theme.replace('function T.preview(p,',fragment+'\n\nfunction T.preview(p,',1)
t.write_text(theme,encoding='utf-8',newline='\n')
print('Client rebuilt; characterViewport inserted')
