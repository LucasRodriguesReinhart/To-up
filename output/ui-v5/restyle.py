from pathlib import Path
root=Path(__file__).parent/'src'
def read(p): return (root/p).read_text(encoding='utf-8')
def save(p,s): (root/p).write_text(s,encoding='utf-8')
def replace(s,a,b):
    assert a in s, a[:100]
    return s.replace(a,b)
def function(s,name,nextname,body):
    start=s.index('function T.'+name+'(');end=s.index('function T.'+nextname+'(',start)
    return s[:start]+body+'\n\n'+s[end:]
p='ReplicatedStorage/ExpeditionUI/Theme.lua';s=read(p)
s=replace(s,'THEME V3','THEME V5 · EXPEDITIONS')
s=replace(s,'ink=rgb(0,0,0), bg0=rgb(10,10,15), bg1=rgb(16,17,24), bg2=rgb(24,25,34), bg3=rgb(37,38,51), bg4=rgb(52,53,70)', 'ink=rgb(2,4,6), bg0=rgb(7,10,12), bg1=rgb(13,17,20), bg2=rgb(20,25,28), bg3=rgb(31,37,40), bg4=rgb(46,53,57)')
s=replace(s,'line=rgb(104,101,118), lineSoft=rgb(60,59,74)', 'line=rgb(116,132,139), lineSoft=rgb(61,73,79)')
s=replace(s,'accent=rgb(46,218,255)', 'accent=rgb(0,180,224)')
s=replace(s,'success=rgb(40,235,79), danger=rgb(255,47,95)', 'success=rgb(49,204,108), danger=rgb(225,38,64)')
s=replace(s,'neutral=rgb(63,60,78)', 'neutral=rgb(56,59,63)')
s=replace(s,'display=Font.fromEnum(Enum.Font.LuckiestGuy)', 'display=Font.new(GOTHAM,Enum.FontWeight.Heavy)')
s=replace(s,'Font.new("rbxasset://fonts/families/FredokaOne.json")', 'Font.new(GOTHAM,Enum.FontWeight.Heavy)')
s=replace(s,'regular=Font.new(GOTHAM,Enum.FontWeight.Bold)', 'regular=Font.new(GOTHAM,Enum.FontWeight.Medium)')
s=replace(s,'pattern = "rbxassetid://70662576263159"','pattern = "rbxassetid://105263140080714", crest = "rbxassetid://88607305530210"')
# New ornamental pattern replaces the unrelated crystal raster, including old dot surfaces.
s=replace(s,'local im = T.image(p, "Texture_" .. kind, T.Assets[kind], 0, 0, 0, 0, col, alpha or .8)', 'local im = T.image(p, "Texture_" .. kind, T.Assets[kind=="halftone" and "pattern" or kind], 0, 0, 0, 0, col, kind=="halftone" and math.max(.86,alpha or .86) or (alpha or .8))')
s=replace(s,'T.corner(f, math.min(opts.radius or 8,10))','T.corner(f, math.min(opts.radius or 4,5))')
s=replace(s,'opts.strokeAlpha or .25','opts.strokeAlpha or .12')
s=replace(s,'T.corner(p, 10)\n\tT.stroke(p, col or P.line, 2)','T.corner(p, 4)\n\tT.stroke(p, col or P.line, 1)')
s=replace(s,'T.gradient(f,P.bg0:Lerp(col,.04),P.bg0:Lerp(col,.35),90)','T.gradient(f,col:Lerp(P.ink,.20),col:Lerp(P.ink,.46),90)')
s=replace(s,'T.texture(f,"pattern",.82,col:Lerp(WHITE,.2),108)','T.texture(f,"pattern",.61,col:Lerp(WHITE,.38),128)')
s=replace(s,'T.corner(f,opts.radius or 8)','T.corner(f,math.min(opts.radius or 5,5))')
s=replace(s,'Thickness=opts.selected and 3 or 2.5','Thickness=opts.selected and 2 or 1.25')
s=replace(s,'local mark=T.frame(f,"RarityMark",1,h-4,w-2,3,opts.dim and P.neutral or col,0)','local inner=T.frame(f,"CardInset",2,2,w-4,h-4,nil,1);T.corner(inner,3);T.stroke(inner,opts.dim and P.lineSoft or col:Lerp(WHITE,.48),.7,.22)\n local mark=T.frame(f,"RarityMark",1,h-4,w-2,3,opts.dim and P.neutral or col,.6)')
s=function(s,'button','setTone',r'''function T.button(p,name,value,x,y,w,h,col,fn,opts)
 opts=opts or {}
 local b=T.new("TextButton",{Name=name,Text="",BackgroundTransparency=1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(w,h),Selectable=true},p)
 b:SetAttribute("ToneColor",col or P.neutral)
 local face=T.frame(b,"Face",0,0,w,h,WHITE,0);T.corner(face,4)
 face.ClipsDescendants=true
 local grad=T.gradient(face,P.neutral,P.bg1,90)
 T.stroke(face,P.ink,2,0)
 local inner=T.frame(face,"InnerRim",1.5,1.5,w-3,h-3,nil,1);T.corner(inner,3)
 local rim=T.stroke(inner,P.line,1,0)
 local light=T.frame(face,"TopLight",3,2,w-6,1,WHITE,.65)
 local ix=12
 if opts.icon then local isz=math.min(30,h-16);T.icon(face,opts.icon,10,(h-isz)/2,isz,isz);ix=isz+18 end
 local caption
 if value and value~="" then caption=T.text(face,"Caption",value,ix,0,w-ix-12,h,math.max(14,opts.size or 22),P.text,opts.align or T.CENTER,opts.font or "title",1.25) end
 local focused=false
 local function paint()
  local disabled=b:GetAttribute("Disabled")
  local tone=b:GetAttribute("ToneColor") or P.neutral
  local neutral=tone==P.neutral or opts.variant=="secondary"
  local used=disabled and rgb(31,34,36) or (neutral and P.neutral or tone)
  local top=focused and used:Lerp(WHITE,.12) or used
  grad.Color=ColorSequence.new({ColorSequenceKeypoint.new(0,top:Lerp(WHITE,.08)),ColorSequenceKeypoint.new(.47,used:Lerp(P.ink,.18)),ColorSequenceKeypoint.new(1,used:Lerp(P.ink,.54))})
  rim.Color=focused and P.text or (neutral and rgb(137,144,149) or used:Lerp(WHITE,.28))
  rim.Transparency=disabled and .65 or .10
  light.Visible=not disabled
  if caption then caption.TextColor3=disabled and P.text3 or (opts.textColor or P.text) end
 end
 b:GetAttributeChangedSignal("Disabled"):Connect(paint)
 b:GetAttributeChangedSignal("ToneColor"):Connect(paint)
 T.bindInteraction(b,fn,{sound=opts.sound,hoverScale=opts.hoverScale or 1,onDisabled=opts.onDisabled,onFocus=function(on) focused=on;paint() end})
 paint()
 return b
end''')
s=function(s,'closeButton','section',r'''function T.closeButton(p,x,y,size,fn)
 size=math.max(size,math.ceil(44/math.max(T.uiScale,.5)))
 if p.Size.X.Offset>0 then x=math.min(x,p.Size.X.Offset-size-12) end
 local b=T.new("TextButton",{Name="Close",Text="",BackgroundTransparency=1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(size,size),ZIndex=10},p)
 local face=T.frame(b,"Face",size*.14,size*.14,size*.72,size*.72,WHITE,0)
 T.corner(face,size);T.stroke(face,P.ink,2)
 T.gradient(face,rgb(244,61,72),rgb(119,11,20),90)
 local inset=T.frame(face,"InnerRim",2,2,size*.72-4,size*.72-4,nil,1);T.corner(inset,size);T.stroke(inset,rgb(255,105,104),1,.3)
 T.text(b,"X","×",0,-1,size,size,math.floor(size*.57),P.text,T.CENTER,"heavy",1.5).ZIndex=11
 T.bindInteraction(b,fn,{sound="ui_fechar",hoverScale=1.04})
 T.hint(b,"Fechar · Esc / B","below")
 return b
end''')
s=replace(s,'T.upper(value), x + 24','value, x + 24')
s=replace(s,'TextService:GetTextSize(value, 22, Enum.Font.FredokaOne','TextService:GetTextSize(value, 22, Enum.Font.GothamBold')
s=replace(s,'T.corner(field, 7)','T.corner(field, 3)')
s=replace(s,'T.stroke(field, P.lineSoft, 2.5)','T.stroke(field, P.lineSoft, 1)')
s=replace(s,'T.corner(ring, 8); T.stroke(ring, P.text2, 3)','T.corner(ring, 8); T.stroke(ring, P.text2, 2)')
s=replace(s,'local face=T.frame(b,"Face",0,0,tw,h,col,selected and .85 or 1)\n  if selected then T.frame(b,"SelectedRule",0,h-3,tw,3,col,0)end\n  T.text(face,"Caption",T.upper(it.label)', 'local face=T.frame(b,"Face",0,0,tw,h,WHITE,0);T.corner(face,4)\n  T.gradient(face,selected and col or P.bg3,selected and col:Lerp(P.ink,.48) or P.bg0,90)\n  T.stroke(face,selected and col:Lerp(WHITE,.35) or P.lineSoft,1)\n  if selected then T.frame(b,"SelectedRule",2,h-2,tw-4,1,col:Lerp(WHITE,.3),0)end\n  T.text(face,"Caption",it.label')
# Ornament is entirely decorative; it never changes the shell or hit rectangles.
at=s.index('function T.scaleOf(')
s=s[:at]+r'''function T.headerOrnament(p,w,h,col)
 local ring=T.image(p,"MiningCrest",T.Assets.crest,-26,-12,h+24,h+24,col:Lerp(WHITE,.06),.08)
 ring.ZIndex=0
 local plate=T.slant(p,"TitlePlate",-6,0,w,h,col,{top=col,bottom=col:Lerp(P.ink,.3),tilt=14})
 local top=T.frame(p,"TitleEdge",5,1,w-18,1,col:Lerp(WHITE,.4),.1)
 local curl=T.image(p,"WindTail",T.Assets.pattern,w-76,h-30,82,50,col:Lerp(P.ink,.28),.16)
 curl.Rotation=-12
 return plate
end

'''+s[at:]
save(p,s)
p='StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua';s=read(p)
s=replace(s,'T.gradient(window,Color3.fromRGB(166,108,224),Color3.fromRGB(100,61,166),90)','T.gradient(window,Color3.fromRGB(6,23,31),Color3.fromRGB(5,10,15),90)')
s=replace(s,'T.texture(window,"halftone",.82,WHITE,40)','T.texture(window,"pattern",.95,pageColor,440)')
s=replace(s,'T.sparkles(stars,ww,wh-78,6,WHITE)','T.sparkles(stars,ww,wh-78,3,pageColor:Lerp(WHITE,.35))')
s=replace(s,'T.gradient(top,Color3.fromRGB(23,12,36),Color3.fromRGB(89,45,127),90)','T.gradient(top,Color3.fromRGB(4,13,19),Color3.fromRGB(9,26,33),90)')
s=replace(s,'T.texture(top,"halftone",.35,P.ink,32)','T.texture(top,"pattern",.92,pageColor,240)')
s=replace(s,'if not full then\n  T.slant(banner,"TitlePlate",-6,0,bw,50,pageColor,{top=pageColor,bottom=pageColor:Lerp(P.ink,.10),tilt=14})\n  T.texture(banner,"halftone",.30,P.ink,20)\n end','T.headerOrnament(banner,bw,50,pageColor)')
s=replace(s,'T.corner(b,7);T.gradient(b,navColor:Lerp(P.ink,.66),P.bg0,90)','T.corner(b,5);T.gradient(b,navColor:Lerp(P.ink,.68),P.bg0,90)')
s=replace(s,'T.texture(b,"halftone",.45,navColor,160);T.stroke(b,P.ink,4)','T.texture(b,"pattern",.73,navColor,96);T.stroke(b,P.ink,2)')
s=replace(s,'T.corner(edge,5);local rim=T.stroke(edge,navColor,2)','T.corner(edge,4);local rim=T.stroke(edge,navColor:Lerp(WHITE,.25),1.25)')
save(p,s)
p='ReplicatedStorage/ExpeditionUI/Inventory.lua';s=read(p)
# A dark rarity-coloured stage and ornamental wash, all behind existing artwork.
s=replace(s,'stage.ClipsDescendants = true','stage.ClipsDescendants = true\n local wash=T.frame(stage,"RarityWash",0,0,w,h,WHITE,0)\n T.gradient(wash,P.bg0:Lerp(r.cor,.015),P.bg0:Lerp(r.cor,.18),90)\n T.corner(wash,5);T.stroke(wash,r.cor:Lerp(P.bg0,.70),1,.2)\n T.texture(wash,"pattern",.96,r.cor:Lerp(WHITE,.3),260)')
s=replace(s,'bg = Color3.fromRGB(15, 12, 20)','bg = Color3.fromRGB(9, 13, 16)')
s=replace(s,'Color3.fromRGB(8, 7, 12):Lerp(stat[3], .09)','Color3.fromRGB(7, 10, 12):Lerp(stat[3], .05)')
# Action emphasis matches the reference: neutral utility actions, cyan primary.
s=replace(s,'"title", 2.2','"title", 1.5')
save(p,s)
p='ReplicatedStorage/ExpeditionUI/Menus.lua';s=read(p)
s=replace(s,'claimed and WHITE or Color3.fromRGB(57, 57, 62)','claimed and Color3.fromRGB(16,29,25) or Color3.fromRGB(23,27,30)')
s=replace(s,'claimed and "RESGATADO" or (today and "AGUARDE" or "BLOQUEADO")','claimed and "Resgatado" or (today and "Aguarde" or "Bloqueado")')
s=replace(s,'claimed and Color3.fromRGB(20, 235, 35)','claimed and Color3.fromRGB(90,221,137)')
save(p,s)
print('V5 visual components written. All layout/interaction formulas preserved.')
