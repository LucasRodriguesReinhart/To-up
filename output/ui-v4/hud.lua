drawHUD = function()
 T.clear(hud);hudRefs={}
 local compact=ctx.compact
 local margin=18
 local slot=compact and 58 or math.clamp(math.floor(virtualW*.053),64,86)
 local slots=math.clamp(ctx.data and tonumber(ctx.data.slotsPets) or 3,1,6)
 local hotW=slots*slot+(slots-1)*8
 local hotY=virtualH-slot-18
 local walletW=compact and 250 or 300
 local row=T.frame(hud,"Currency",margin,compact and 8 or 16,walletW,48,nil,1)
 hudRefs.wallet=row
 T.icon(row,"coins",-3,-3,60,60)
 hudRefs.coins=T.text(row,"Coins",ctx.shownCoins and T.format(ctx.shownCoins) or "0",61,1,walletW-65,46,compact and 30 or 34,P.gold,T.LEFT,"number",2.5)
 T.hint(row,"Moedas · obtidas na venda de minérios","below")
 local bagW=walletW
 local bag=T.frame(hud,"Bag",margin,compact and 62 or 78,bagW,36,nil,1);hudRefs.bagPanel=bag
 T.icon(bag,"items",-3,-9,46,46)
 hudRefs.bagTrack=T.progress(bag,"Track",44,0,bagW-93,28,0,P.accent,{segments=5})
 hudRefs.bag=T.text(hudRefs.bagTrack,"Count","0 / 0",3,0,bagW-99,28,15,P.text,T.CENTER,"number",1.6)
 hudRefs.sell=T.iconButton(bag,"SellShortcut","forge",bagW-42,-6,40,function() ctx.open("Forge") end)
 T.hint(hudRefs.sell,"Vender minérios com Ignis","below")
 local pw=compact and 180 or 216
 local py=virtualH-(compact and 118 or 74)
 local power=T.frame(hud,"Power",virtualW-pw-margin,py,pw,56,nil,1)
 T.statIcon(power,"dano",-5,-7,66,66)
 hudRefs.power=T.text(power,"Value","0",60,0,pw-60,54,compact and 28 or 34,P.text,T.LEFT,"number",2.5)
 T.hint(power,"Força por golpe","above")
 hudRefs.buffs=T.scroll(hud,"Buffs",walletW+50,18,math.max(100,virtualW-walletW-280),32,P.violet)
 hudRefs.buffs.ScrollingDirection=Enum.ScrollingDirection.X;hudRefs.buffs.ScrollBarThickness=2;hudRefs.buffKeys=""
 local nw=compact and 66 or 80
 local nh=compact and 65 or 82
 local ng=8
 local navY=compact and 116 or 150
 local dock=T.frame(hud,"Navigation",0,0,virtualW,virtualH,nil,1);hudRefs.rail={}
 for i,it in ipairs(NAV) do
  if it.id=="Settings" then continue end
  local x=margin+((i-1)%2)*(nw+ng)
  local y=navY+math.floor((i-1)/2)*(nh+ng)
  local navColor=T.Page[it.id] or P.violet
  local b=T.new("TextButton",{Name=it.id,Text="",AutoButtonColor=false,BackgroundColor3=WHITE,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(nw,nh)},dock)
  T.corner(b,7);T.gradient(b,navColor:Lerp(P.ink,.66),P.bg0,90)
  T.texture(b,"halftone",.45,navColor,160);T.stroke(b,P.ink,4)
  local edge=T.frame(b,"Rim",2,2,nw-4,nh-4,nil,1);T.corner(edge,5);local rim=T.stroke(edge,navColor,2)
  local isz=compact and 43 or 57
  T.icon(b,it.icon,(nw-isz)/2,1,isz,isz)
  T.text(b,"Label",it.id=="Inventory" and "Inventário" or it.label,1,nh-24,nw-2,23,compact and 14 or 16,P.text,T.CENTER,"title",1.8)
  if it.key and not compact then T.text(b,"Key",it.key,5,1,18,17,12,P.text2,T.LEFT,"caption",1) end
  T.bindInteraction(b,function() if it.id=="Inventory" then ctx.collection="pet" end;ctx.open(it.id) end,{onFocus=function(on) rim.Color=on and P.text or navColor end})
  T.hint(b,it.tip..(it.key and " · ["..it.key.."]" or ""),"right")
  hudRefs.rail[it.id]=b
 end
 local settings=T.iconButton(dock,"Settings","settings",margin,virtualH-60,48,function() ctx.open("Settings") end)
 T.hint(settings,"Configurações","above");hudRefs.rail.Settings=settings
 hudRefs.hotbar=T.frame(hud,"Hotbar",(virtualW-hotW)/2-27,hotY,hotW,slot,nil,1)
 screen:SetAttribute("BottomReserved",0)
 screen:SetAttribute("HoldX",(virtualW+hotW)/2-17)
 screen:SetAttribute("HoldY",hotY+(slot-48)/2)
 hudRefs.signature=nil;updateHUD()
end
