from pathlib import Path
import re
root=Path(__file__).parent
base=root/'before'; out=root/'src'
def read(path): return (base/path).read_text(encoding='utf-8')
def save(path,s):
 p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def rep(s,a,b):
 assert a in s, a[:120]
 return s.replace(a,b)
theme='ReplicatedStorage/ExpeditionUI/Theme.lua'
s=read(theme)
s=rep(s,'display=Font.new("rbxasset://fonts/families/FredokaOne.json")','display=Font.fromEnum(Enum.Font.LuckiestGuy)')
s=s.replace('Font.new(BUILDER,Enum.FontWeight.Bold)','Font.new(GOTHAM,Enum.FontWeight.Bold)').replace('Font.new(BUILDER,Enum.FontWeight.Medium)','Font.new(GOTHAM,Enum.FontWeight.Bold)')
s=rep(s,'function T.icon(p, key, x, y, w, h)\n', '''function T.icon(p, key, x, y, w, h)
 local cells={coins=Vector2.new(0,0),dano=Vector2.new(627,0),power=Vector2.new(627,0),items=Vector2.new(0,627),capacidade=Vector2.new(0,627),summon=Vector2.new(627,627)}
 if cells[key] then
  local im=T.image(p,"Icon_"..key,"rbxassetid://108999126113973",x,y,w,h or w)
  im.ImageRectOffset=cells[key];im.ImageRectSize=Vector2.new(627,627)
  return im
 end
''')
s=rep(s,'function T.statIcon(p, key, x, y, w, h)\n','function T.statIcon(p, key, x, y, w, h)\n if key=="dano" or key=="capacidade" then return T.icon(p,key,x,y,w,h) end\n')
s=rep(s,'local ts = tile or (kind == "halftone" and 26 or 110)','local ts = kind=="halftone" and math.max(140,tile or 180) or (tile or 110)')
s=rep(s,'WHITE,.93,-55,2','WHITE,.86,-55,2')
s=rep(s,'grad.Color=ColorSequence.new(top,used:Lerp(P.ink,.10))','grad.Color=ColorSequence.new({ColorSequenceKeypoint.new(0,top:Lerp(WHITE,.16)),ColorSequenceKeypoint.new(.48,used),ColorSequenceKeypoint.new(1,used:Lerp(P.ink,.30))})')
s=rep(s,'local ix=12','local gloss=T.frame(face,"TopLight",4,3,w-8,math.max(2,h*.09),WHITE,.58);T.corner(gloss,3)\n local bevel=T.frame(face,"BottomBevel",3,h-5,w-6,3,P.ink,.55);T.corner(bevel,2)\n local ix=12')
s=rep(s,'if opts.stroke ~= false then T.stroke(track, P.lineSoft, 1) end','if opts.stroke ~= false then T.stroke(track, P.ink, 2); local edge=T.frame(track,"InnerEdge",1,1,w-2,h-2,nil,1);T.corner(edge,4);T.stroke(edge,col:Lerp(WHITE,.22),1,.32) end')
s=rep(s,'local g = T.gradient(fill, col, col)','local g = T.gradient(fill, col:Lerp(WHITE,.23), col:Lerp(P.ink,.24),90)')
s=s.replace('math.floor(ih * .35)), WHITE, 1)','math.floor(ih * .35)), WHITE, .65)')
s=s.replace('g.Color = ColorSequence.new(col, col)','g.Color = ColorSequence.new(col:Lerp(WHITE,.23), col:Lerp(P.ink,.24))')
s=rep(s,'local count=#ids;local minV','local animatedModels={}\n local count=#ids;local minV')
s=rep(s,'local range=Vector3.new(2.45,3.25,1.6)','local joints={}\n   for _,joint in ipairs(model:GetDescendants()) do if (joint:IsA("Motor6D") or joint:IsA("AnimationConstraint")) and poses[joint.Name] then table.insert(joints,{joint,joint.Transform}) end end\n   table.insert(animatedModels,{model=model,pivot=model:GetPivot(),joints=joints,phase=index*.85})\n   local range=Vector3.new(2.45,3.25,1.6)')
s=rep(s,'v:SetAttribute("ModelIds",table.concat(ids,","))','''local elapsed=0
 local idle=Run.RenderStepped:Connect(function(dt)
  if not v.Visible or v.AbsoluteSize.Y<5 then return end
  local ancestor=v.Parent
  while ancestor and ancestor:IsA("GuiObject") do if not ancestor.Visible then return end;ancestor=ancestor.Parent end
  elapsed+=dt
  for _,entry in ipairs(animatedModels) do
   local t=elapsed*1.65+entry.phase
   local breath=T.motionEnabled() and math.sin(t) or 0
   entry.model:PivotTo(entry.pivot*CFrame.new(0,breath*.045,0)*CFrame.Angles(0,breath*.018,0))
   for _,pair in ipairs(entry.joints) do
    local joint,pose=pair[1],pair[2]
    if joint.Parent then joint.Transform=pose*CFrame.Angles(breath*.025,0,math.cos(t)*.008) end
   end
  end
 end)
 v.Destroying:Once(function() idle:Disconnect() end)
 v:SetAttribute("IdleAnimation","BreathingPose")
 v:SetAttribute("ModelIds",table.concat(ids,","))''')
star='''
-- Abertura visual; o resultado já foi decidido pelo servidor antes desta chamada.
function T.starOpening(parent,w,h,complete)
 local overlay=T.new("CanvasGroup",{Name="StarOpening",Size=UDim2.fromOffset(w,h),BackgroundColor3=P.ink,BackgroundTransparency=.25,ZIndex=80,Active=true},parent)
 local shield=T.new("TextButton",{Name="Skip",Text="",Size=UDim2.fromScale(1,1),BackgroundTransparency=1,ZIndex=80},overlay)
 local size=math.min(290,h*.64)
 local star=T.icon(overlay,"summon",(w-size)/2,(h-size)/2,size,size);star.ZIndex=81
 star.AnchorPoint=Vector2.new(.5,.5);star.Position=UDim2.fromScale(.5,.5)
 local sc=T.new("UIScale",{Scale=.12},star)
 local burst=T.frame(overlay,"Flash",0,0,w,h,WHITE,1);burst.ZIndex=82
 local finished=false
 local function finish()
  if finished then return end;finished=true
  overlay:Destroy();if complete then complete() end
 end
 T.bindInteraction(shield,finish,{sound=false})
 overlay.Destroying:Once(function() finished=true end)
 if not T.motionEnabled() then task.delay(.15,finish);return overlay end
 T.tween(sc,.30,{Scale=1},Enum.EasingStyle.Back)
 T.tween(star,.62,{Rotation=22},Enum.EasingStyle.Quad)
 task.delay(.64,function()
  if finished then return end
  T.tween(star,.18,{Rotation=-18});T.tween(sc,.18,{Scale=.76})
  task.delay(.19,function()
   if finished then return end
   T.tween(sc,.24,{Scale=2.1});T.tween(star,.22,{ImageTransparency=1,Rotation=42})
   T.tween(burst,.10,{BackgroundTransparency=.25})
   task.delay(.13,function() if not finished then T.tween(overlay,.18,{GroupTransparency=1});task.delay(.19,finish) end end)
  end)
 end)
 return overlay
end
'''
s=rep(s,'return T\n',star+'\nreturn T\n')
save(theme,s)

inv='ReplicatedStorage/ExpeditionUI/Inventory.lua';s=read(inv)
s=rep(s,'local function feedPopup(ctx, targetUid)', '''local function rarityPicks()
 local result={}
 for _,id in ipairs({"comum","incomum","raro","epico","lendario","mitico"}) do
  local rarity=T.rar(id);local rank=rarity.ordem
  table.insert(result,{"Até "..rarity.nome,function(c) return T.rar(c.def.raridade).ordem<=rank end,rarity.cor})
 end
 return result
end
local function feedPopup(ctx, targetUid)''')
s,n=re.subn(r'quickPicks = \{\n.*?\n\t\t\},', 'quickPicks = rarityPicks(),',s,flags=re.S);assert n==2
s=rep(s,'local gridTop = 108 + buttonH + 12','local pickCols=w<780 and 3 or 6\n\t\tlocal pickRows=math.ceil(#opts.quickPicks/pickCols)\n\t\tlocal gridTop = 108 + pickRows*(buttonH+8) + 12')
s=rep(s,'local bw = (w - gap * #opts.quickPicks) / (#opts.quickPicks + 1)','local bw = (w - gap * (pickCols-1)) / pickCols')
s=rep(s,'(i - 1) * (bw + gap), 108, bw, buttonH, P.neutral','((i-1)%pickCols) * (bw + gap), 108+math.floor((i-1)/pickCols)*(buttonH+8), bw, buttonH, pick[3] or P.neutral')
s=rep(s,'for _, c in ipairs(list) do if pick[2](c) then selection[c.key] = true end end','table.clear(selection)\n\t\t\t\t\tfor _, c in ipairs(list) do if pick[2](c) then selection[c.key] = true end end')
s=rep(s,'#opts.quickPicks * (bw + gap), 108, bw, buttonH','w-90, 72, 90, 28')
s=s.replace('0, 72, w, 34, 14','0, 72, w-104, 34, 14')
start=s.index('local function textAction(');end=s.index('local function renderDesktopDetail',start)
s=s[:start]+'''local function textAction(parent,name,value,glyph,x,y,w,h,color,fn,opts)
 opts=opts or {}
 local tone=color and color~=P.text and color or P.neutral
 local b=T.button(parent,name,value,x,y,w,h,tone,fn,{size=21,onDisabled=opts.onDisabled})
 local caption=b:FindFirstChild("Caption",true)
 if caption then caption.Position=UDim2.fromOffset(42,0);caption.Size=UDim2.fromOffset(w-54,h) end
 if glyph=="lock" then T.lock(b.Face,12,(h-22)/2,22,P.text)
 else T.text(b.Face,"Glyph",glyph,6,0,32,h,24,P.text,T.CENTER,"title",2) end
 return b
end

'''+s[end:]
s=rep(s,'if h < minimum then parent','if h < minimum and not ctx.compact then parent')
s=rep(s,'renderDesktopDetail(ctx, detail, kind, selected, detailW, h, data)','if ctx.compact then renderMobileDetail(ctx,detail,kind,selected,detailW,h,data,false) else renderDesktopDetail(ctx, detail, kind, selected, detailW, h, data) end')
s=s.replace('ctx.open("Summon")','ctx.open("Areas")')
save(inv,s)

client='StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua';s=read(client)
s=rep(s,'Store = { title = "Loja", icon = "store", color = P.gold, sub = "Picaretas, mochilas, passes e boosts" },','Store = { title = "Loja", icon = "store", color = P.gold, sub = "Passes, boosts e pacotes" },\n Equipment = {title="Equipamentos",icon="pickaxe",color=P.ember,sub="Picaretas e mochilas · Ignis"},')
s=rep(s,'Inventory = { title = "Unidades"','Inventory = { title = "Inventário"')
s=rep(s,'elseif ctx.page == "Store" then\n\t\treturn { { id = "Picaretas", label = "Picaretas", icon = "pickaxe" }, { id = "Mochilas", label = "Mochilas", icon = "items" }, { id = "Passes", label = "Passes", icon = "vip" } },','elseif ctx.page == "Equipment" then\n\t\treturn { { id = "Picaretas", label = "Picaretas", icon = "pickaxe" }, { id = "Mochilas", label = "Mochilas", icon = "items" } },')
s=rep(s,'tip="Picaretas, mochilas e passes"','tip="Passes, boosts e pacotes"')
s=re.sub(r' \{id="Summon",label="Invocar"[^\n]+\n','',s)
s=s.replace('elseif key == Enum.KeyCode.G then ctx.open("Summon") end','end')
s=rep(s,'ctx.storeTab = "Mochilas"; if ctx.page ~= "Store" then ctx.open("Store")','ctx.storeTab = "Mochilas"; if ctx.page ~= "Equipment" then ctx.open("Equipment")')
s=rep(s,'or ctx.page == "Store" or ctx.page == "Areas"','or ctx.page == "Store" or ctx.page == "Equipment" or ctx.page == "Areas"')
a=s.index('\t-- ilha + missão em destaque');b=s.index('\t-- badges',a);s=s[:a]+s[b:]
s=re.sub(r'\tsetBadge\(hudRefs.rail.Store,[^\n]+\n','',s)
a=s.index('connect(player:GetAttributeChangedSignal("CurrentAreaId"),function()');b=s.index('connect(player:GetAttributeChangedSignal("ExpeditionBlurEnabled")',a)
s=s[:a]+'connect(player:GetAttributeChangedSignal("CurrentAreaId"),function() updateHUD() end)\n'+s[b:]
s=rep(s,'if ctx.portrait or ctx.compact then s=1 end','if ctx.portrait then s=1 elseif ctx.compact then s=math.clamp(v.Y/480,.75,.95) end\n screen:SetAttribute("HudScale",s)')
s=rep(s,'local inline=not(ctx.portrait or ctx.compact)','local inline=not ctx.portrait')
s=rep(s,'local function fullPage() return FULLSCREEN[ctx.page] and not ctx.portrait and not ctx.compact end','local function fullPage() return FULLSCREEN[ctx.page] and not ctx.portrait end')
s=rep(s,'local headH=(full and 94 or 76)+extra','local headH=(ctx.compact and 70 or full and 94 or 76)+extra')
s=rep(s,'local function showResults(results, count, playAudio)','''local function showResults(results, count, playAudio, opened)
 if playAudio~=false and not opened and #results>0 then
  player:SetAttribute("RevealOpen",true)
  T.starOpening(popupLayer,virtualW,virtualH,function()
   player:SetAttribute("RevealOpen",false)
   if alive and screen.Parent then showResults(results,count,playAudio,true) end
  end)
  return
 end''')
a=s.index('drawHUD = function()');b=s.index('\nlocal function nextPickaxe',a)
s=s[:a]+(root/'hud.lua').read_text(encoding='utf-8')+s[b:]
# Force both device orientations to remain horizontal; native controls keep their safe insets.
s=rep(s,'local Inventory = require(modules.Inventory)','local Inventory = require(modules.Inventory)\nplayer:WaitForChild("PlayerGui").ScreenOrientation=Enum.ScreenOrientation.LandscapeSensor')
save(client,s)

menus='ReplicatedStorage/ExpeditionUI/Menus.lua';s=read(menus)
s=rep(s,'if ctx.storeTab == "Passes" then passesStore','if ctx.page == "Store" then passesStore')
s=s.replace('ctx.storeTab = "Picaretas"; ctx.open("Store")','ctx.storeTab = "Picaretas"; ctx.open("Equipment")')
s=s.replace('if page == "Store" then','if page == "Store" or page == "Equipment" then')
s=s.replace('ctx.page == "Store" then M.store','(ctx.page == "Store" or ctx.page == "Equipment") then M.store')
s=rep(s,'local narrow = w < 860','local narrow = w < 620')
s=rep(s,'local stageH = narrow and 520 or math.max(450, h)','local stageH = narrow and 520 or math.max(300, h)')
a=s.index('function M.progress(ctx, p, w, h)');b=s.index('function M.settings',a)
s=s[:a]+(root/'quests.lua').read_text(encoding='utf-8')+'\n'+s[b:]
save(menus,s)

auto='StarterPlayer/StarterPlayerScripts/AutoMinerar.lua';s=read(auto)
s=s.replace('Size=UDim2.fromOffset(206,46)','Size=UDim2.fromOffset(48,48)')
s=rep(s,'botao=Theme.button(container,"HoldMode",textoBotao(),0,0,206,46','botao=Theme.button(container,"HoldMode","",0,0,48,48')
s=rep(s,'end,{icon="pickaxe",size=18,sound="ui_toggle"})','end,{sound="ui_toggle"})\nTheme.icon(botao.Face,"pickaxe",7,7,34,34)')
a=s.index(' local reserved=shell and shell:GetAttribute("BottomReserved")');b=s.index(' atualizarBotao()\nend',a)
s=s[:a]+''' local scale=shell and shell:GetAttribute("HudScale") or 1
 escala.Scale=scale
 local hx=shell and shell:GetAttribute("HoldX") or v.X/2+150
 local hy=shell and shell:GetAttribute("HoldY") or v.Y-70
 container.Position=UDim2.fromOffset((hx+48)*scale,(hy+48)*scale)
'''+s[b:]
s=rep(s,'shell:GetAttributeChangedSignal("BottomReserved"):Connect(posicionarBotao)','for _,key in ipairs({"HoldX","HoldY","HudScale"}) do shell:GetAttributeChangedSignal(key):Connect(posicionarBotao) end')
save(auto,s)
save('StarterPlayer/StarterPlayerScripts/IslandTransition.lua',(root/'transition.lua').read_text(encoding='utf-8'))
print('V4 modules authored')
