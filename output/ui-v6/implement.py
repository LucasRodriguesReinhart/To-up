from pathlib import Path
import re
root=Path(__file__).parent/'src'
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).parent.mkdir(parents=True,exist_ok=True);(root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 assert a in s,a[:100]
 return s.replace(a,b)

write('ReplicatedStorage/UIPreferences.lua','''-- Whitelisted device preferences; desktop and landscape phone retain independent sizes.
local U={defaults={desktopScale=.85,mobileScale=.80},min=.65,max=1.15}
function U.value(value)
 if type(value)~="number" or value~=value or math.abs(value)==math.huge then return nil end
 return math.clamp(math.round(value*100)/100,U.min,U.max)
end
function U.sanitize(patch,base)
 local out={}
 for key,default in pairs(U.defaults) do out[key]=U.value(type(patch)=="table" and patch[key]) or U.value(type(base)=="table" and base[key]) or default end
 return out
end
return U
''')
p='ReplicatedStorage/MonetizacaoConfig.lua';s=read(p)
catalog=[('PetSlots','+3 unidades equipadas',1982222478,399,99441632008831,'Equipe três unidades adicionais.'),('PortableForge','Forja portátil de Ignis',1983332510,249,132981230702521,'Venda seus minérios de qualquer lugar. Venda manual pelo atalho da mochila.'),('Inventory1000','+1000 espaços',1981412489,299,119556624950231,'Mais 1000 espaços para unidades e acessórios. Acumula com os outros passes de espaço.'),('Inventory300','+300 espaços',1985126289,150,77731366713850,'Mais 300 espaços para unidades e acessórios. Acumula com os outros passes de espaço.'),('Inventario','+50 espaços',1981526513,9,113891132096263,'Mais 50 espaços para unidades e acessórios. Acumula com os outros passes de espaço.'),('HatSlot','+3 acessórios equipados',1985288267,350,128462085658045,'Equipe três acessórios adicionais.'),('LuckyPlus','Lucky+',1984808508,149,130567131583953,'Sorte extra para unidades e acessórios.'),('Lucky','Lucky',1984046505,599,129542791610654,'Chance de Épico ou melhor ×1,25. Não altera a garantia.'),('VIP','VIP',1985138262,499,125812291452782,'Receba 10% mais moedas nas vendas.')]
rows=['M.PASSES = {']
for key,name,id,price,icon,desc in catalog:
 rows.append(f' {{chave="{key}",nome="{name}",id={id},robux={price},icon={icon},desc="{desc}"}},')
rows.append('}')
s=re.sub(r'M.PASSES = \{.*?\n\}', '\n'.join(rows),s,count=1,flags=re.S)
write(p,s)
p='ServerScriptService/Core/PlayerData.lua';s=read(p)
s=rep(s,'local AudioPreferences =','local UIPreferences = require(RS:WaitForChild("UIPreferences"))\nlocal AudioPreferences =')
s=rep(s,'audio = AudioPreferences.sanitize(),','ui = UIPreferences.sanitize(),\n\t\taudio = AudioPreferences.sanitize(),')
s=rep(s,'p.audio = AudioPreferences.sanitize(p.audio)','p.ui = UIPreferences.sanitize(p.ui)\n\tp.audio = AudioPreferences.sanitize(p.audio)')
s=rep(s,'-- perfil zerado (testes no Studio)','''function PlayerData.atualizarUI(player, patch)
 local perfil=cache[player]
 if not perfil or type(patch)~="table" then return {ok=false} end
 perfil.ui=UIPreferences.sanitize(patch,perfil.ui)
 return {ok=true,ui=table.clone(perfil.ui),persistent=PlayerData.audioPersistente(perfil)}
end

-- perfil zerado (testes no Studio)''')
s=rep(s,'function PlayerData.slotsPets() return Config.PET_SLOTS_BASE end','function PlayerData.slotsPets(perfil) return Config.PET_SLOTS_BASE + (perfil and perfil.__player and Passes.possui(perfil.__player,"PetSlots") and 3 or 0) end')
s=rep(s,'function PlayerData.capacidadePets(perfil)','''local function inventoryBonus(perfil)
 return (temPasse(perfil,"Inventario") and 50 or 0)+(temPasse(perfil,"Inventory300") and 300 or 0)+(temPasse(perfil,"Inventory1000") and 1000 or 0)
end
function PlayerData.capacidadePets(perfil)''')
s=s.replace('(temPasse(perfil, "Inventario") and 50 or 0)','inventoryBonus(perfil)').replace('(temPasse(perfil, "HatSlot") and 1 or 0)','(temPasse(perfil, "HatSlot") and 3 or 0)')
s=rep(s,'audio = AudioPreferences.sanitize(perfil.audio),','ui = UIPreferences.sanitize(perfil.ui),\n\t\tuiPersistent = PlayerData.audioPersistente(perfil),\n\t\taudio = AudioPreferences.sanitize(perfil.audio),')
write(p,s)
p='ServerScriptService/Core/Main.lua';s=read(p)
s=rep(s,'-- Audio settings are a small patch','''local uiRate={}
remoteNovo("AtualizarUIProfile","RemoteFunction").OnServerInvoke=function(player,patch)
 if type(patch)~="table" then return {ok=false} end
 local now=os.clock()
 if now-(uiRate[player] or -math.huge)<.20 then return {ok=false,retryAfter=.3} end
 uiRate[player]=now
 return PlayerData.atualizarUI(player,patch)
end
Players.PlayerRemoving:Connect(function(player) uiRate[player]=nil end)

-- Audio settings are a small patch''')
s=rep(s,'R.Vender.OnServerInvoke = function(player)\n\treturn IgnisService.vender(player)','R.Vender.OnServerInvoke = function(player, mode)\n\treturn IgnisService.vender(player, false, mode)')
s=rep(s,'R.AbrirIgnis:FireClient(player)','if IgnisService.pertoDoIgnis(player) then R.AbrirIgnis:FireClient(player) end')
write(p,s)
p='ServerScriptService/Core/IgnisService.lua';s=read(p)
s=rep(s,'local MSG_VENDA = "Venda no Ignis do lobby (teleporte gratis) ou use o passe Auto Sell"','local MSG_VENDA = "A forja portátil exige o passe Portable Ignis Forge. Você também pode vender gratuitamente junto ao Ignis."')
s=rep(s,'function IgnisService.vender(player, auto)','''-- Never trust a client-provided NPC flag. Check the actual character position.
function IgnisService.pertoDoIgnis(player)
 local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
 local npcs=workspace:FindFirstChild("NPCs")
 local npc=npcs and npcs:FindFirstChild("Ignis")
 local belly=npc and npc:FindFirstChild("belly",true)
 return root~=nil and belly~=nil and belly:IsA("BasePart") and (root.Position-belly.Position).Magnitude<=22
end
function IgnisService.podeVender(player,auto,mode)
 if auto then return Passes.possui(player,"AutoSell") end
 if mode=="npc" and IgnisService.pertoDoIgnis(player) then return true end
 return Passes.possui(player,"PortableForge")
end
function IgnisService.vender(player, auto, mode)''')
s=rep(s,'if not auto and not Passes.noLobby(player) and not Passes.possui(player, "AutoSell") then\n\t\treturn { ok = false, msg = MSG_VENDA, semAcesso = "AutoSell" }','if not IgnisService.podeVender(player,auto,mode) then\n\t\treturn { ok = false, msg = MSG_VENDA, semAcesso = "PortableForge" }')
write(p,s)
p='ServerScriptService/Core/Ofertas.lua';s=read(p).replace('"AutoSell"','"PortableForge"');write(p,s)

p='StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua';s=read(p)
s=rep(s,'local AudioPreferences =','local UIPreferences = require(RS:WaitForChild("UIPreferences"))\nlocal AudioPreferences =')
s=rep(s,'local closePopup','local resize\nlocal closePopup')
s=rep(s,'T.setTooltipLayer(tipLayer, function() return scale.Scale end)','''-- Apply scale immediately and save a bounded, per-device preference patch.
ctx.ui=UIPreferences.sanitize()
local uiHydrated,uiWorker=false,false
local pendingUI={}
ctx.uiSaveStatus="loading"
function ctx.setUIScale(value)
 value=UIPreferences.value(value);if not value then return end
 local key=ctx.compact and "mobileScale" or "desktopScale"
 ctx.ui[key]=value;pendingUI[key]=value;ctx.uiSaveStatus="pending"
 task.defer(function() if alive and resize then resize() end end)
 if uiWorker then return end
 uiWorker=true
 task.spawn(function()
  task.wait(.45)
  while alive and next(pendingUI) do
   local patch=pendingUI;pendingUI={}
   local remote=R:WaitForChild("AtualizarUIProfile",5)
   local ok,result=false,nil
   for attempt=1,3 do
    if remote then ok,result=pcall(function() return remote:InvokeServer(patch) end) end
    if ok and type(result)=="table" and result.ok then break end
    task.wait(.4)
   end
   if not alive then break end
   if ok and type(result)=="table" and result.ok then
    ctx.uiSaveStatus=result.persistent and "profile" or "session"
   else
    ctx.uiSaveStatus="error"
   end
   if ctx.uiSettingsStatus then ctx.uiSettingsStatus() end
   task.wait(.3)
  end
  uiWorker=false
 end)
end
ctx.marketInfo={}
T.setTooltipLayer(tipLayer, function() return scale.Scale end)''')
s=rep(s,'function ctx.open(page)','''function ctx.open(page)''')
s=rep(s,'\tif not PAGE[page] then return end','''\tif not PAGE[page] then return end
 if page=="Forge" and ctx.forgeMode~="npc" then ctx.forgeMode="portable" end
 if page~="Forge" then ctx.forgeMode=nil end''')
s=rep(s,'\tctx.page = nil','\tctx.page = nil\n\tctx.forgeMode=nil')
s=rep(s,'function() ctx.open("Forge") end)','function() ctx.forgeMode="portable"; ctx.open("Forge") end)')
s=rep(s,'connect(R.AbrirIgnis.OnClientEvent,function() if ctx.page ~= "Forge" then ctx.open("Forge") end end)','connect(R.AbrirIgnis.OnClientEvent,function() ctx.forgeMode="npc"; if ctx.page ~= "Forge" then ctx.open("Forge") else ctx.refresh() end end)')
s=rep(s,'local function resize()','resize = function()')
s=rep(s,' screen:SetAttribute("HudScale",s)',''' local preference=ctx.ui[ctx.compact and "mobileScale" or "desktopScale"]
 s*=preference
 screen:SetAttribute("UIScalePreference",preference)
 screen:SetAttribute("HudScale",s)''')
s=rep(s,'\thydrated = true',''' if not uiHydrated then
  ctx.ui=UIPreferences.sanitize(pendingUI,data.ui)
  ctx.uiSaveStatus=data.uiPersistent and "profile" or "session"
  uiHydrated=true
  task.defer(function() if alive and resize then resize() end end)
 end
\thydrated = true''')
# Keep the inventory columns and anchor positions, but give the shell desktop breathing room.
s=rep(s,'if fullPage() then return virtualW,virtualH,0,0 end','''if fullPage() then
  if ctx.compact then return virtualW-28,virtualH-20,14,10 end
  local ww,wh=math.min(1360,virtualW-104),math.min(760,virtualH-90)
  return ww,wh,(virtualW-ww)/2,(virtualH-wh)/2
 end''')
s=s.replace('strokeWidth=full and 0 or 2','strokeWidth=2')
s=rep(s,'T.frame(window,"FullBleedTop",0,-inset,ww,inset+1,P.ink,0)','-- Preserve the safe area; menus no longer paint over the Roblox top bar.')
s=rep(s,'if animate and not full then','if animate then')
s=rep(s,'local bw=full and 280 or math.min(ww-112,ctx.page=="Events" and 380 or 330)','local bw=full and 280 or math.min(ww-112,ctx.page=="Events" and 380 or 330)')
s=s.replace('ctx.page=="Events" and 27 or 32','ctx.page=="Events" and 27 or 29')
# Official client-local prices, including regional/Plus prices, never copied from the creator screenshot.
s+='''
task.spawn(function()
 local market=game:GetService("MarketplaceService")
 for _,def in ipairs(Mon.PASSES) do
  local ok,info=pcall(market.GetProductInfoAsync,market,def.id,Enum.InfoType.GamePass)
  if ok and type(info)=="table" then ctx.marketInfo[def.chave]=info end
 end
 if alive and ctx.page=="Store" then ctx.refresh() end
end)
'''
# Replace obsolete Auto Sell offer copy without enabling automatic sales.
s=s.replace('nome == "AutoSell" and Mon.passe("AutoSell")','nome == "PortableForge" and Mon.passe("PortableForge")').replace('ctx.invoke("ComprarRobux", "AutoSell")','ctx.invoke("ComprarRobux", "PortableForge")')
s=s.replace('Venda com o Ignis usando o teleporte grátis, ou deixe o Auto Sell vender sozinho em qualquer ilha.','Venda gratuitamente junto ao Ignis ou use a forja portátil em qualquer ilha.').replace('"Auto Sell  ·  R$ " .. passe.robux','"Ver forja portátil"').replace('"Auto Sell (em breve)"','"Forja portátil"')
write(p,s)

p='ReplicatedStorage/ExpeditionUI/Menus.lua';s=read(p)
s=rep(s,'T.icon(card, PASS_ICON[def.chave] or "store", 12, 12, 52, 52)','if def.icon then T.image(card,"OfficialPassIcon","rbxassetid://"..def.icon,6,6,66,66) else T.icon(card, PASS_ICON[def.chave] or "store", 12, 12, 52, 52) end')
s=rep(s,'local caption = owned and "Adquirido" or (configured and (tostring(def.robux) .. " Robux") or "Em breve")','''local market=ctx.marketInfo and ctx.marketInfo[def.chave]
            local caption = owned and "Adquirido" or (configured and (market and market.PriceInRobux and (tostring(market.PriceInRobux).." Robux") or "Ver preço") or "Em breve")''')
s=rep(s,'local res = ctx.invoke("Vender")','local res = ctx.invoke("Vender",ctx.forgeMode=="npc" and "npc" or "portable")')
s=rep(s,'\tlocal hint = d.passes and d.passes.AutoSell and "✓ Auto Sell ativo: a venda acontece quando sua mochila enche."\n\t\tor "Vendas são feitas com Ignis. Fora do lobby, viaje gratuitamente até a praça central."','\tlocal hint = ctx.forgeMode=="npc" and "Venda gratuita junto ao Ignis." or "✓ Forja portátil adquirida. Venda manual disponível em qualquer ilha."')
marker='function M.forge(ctx, p, w, h)'
assert marker in s
s=rep(s,marker,marker+'''
 if ctx.forgeMode~="npc" and not (ctx.data.passes and ctx.data.passes.PortableForge) then
  local card=T.panel(p,"PortableForgeLocked",0,0,w,h,{bg=P.bg0,strokeColor=P.ember})
  local iw=math.min(170,h*.34)
  T.image(card,"OfficialPassIcon","rbxassetid://132981230702521",(w-iw)/2,18,iw,iw)
  label(card,"Title","Forja portátil",16,iw+24,w-32,36,28,P.ember,T.CENTER)
  T.para(card,"Requirement","Venda de qualquer ilha com o passe Portable Ignis Forge.",24,iw+68,w-48,48,18,P.text2,T.CENTER)
  local bw=math.min(360,(w-60)/2)
  T.button(card,"GetForge","Ver gamepass",w/2-bw-7,h-72,bw,52,P.ember,function() ctx.invoke("ComprarRobux","PortableForge") end,{icon="lock",size=19})
  T.button(card,"VisitIgnis","Ir ao Ignis · grátis",w/2+7,h-72,bw,52,P.neutral,function() ctx.travel("ignis") end,{size=18})
  return
 end''')
s=rep(s,'{ "G", "Invocar" }, ','')
s=rep(s,'local y = T.section(scroll, "Mixagem de áudio", 0, 0, colW, P.accent)','''local y = T.section(scroll, "Tamanho da interface", 0, 0, colW, P.accent)
 local scaleRow=panel(scroll,"UIScaleSetting",0,y,colW,138)
 local key=ctx.compact and "mobileScale" or "desktopScale"
 local value=ctx.ui[key]
 label(scaleRow,"Name",ctx.compact and "Escala · celular" or "Escala · PC",16,10,colW-100,24,18)
 text(scaleRow,"Percentage",math.round(value*100).."%",colW-85,10,69,24,20,P.accent,T.RIGHT,"number")
 T.para(scaleRow,"Description","HUD e menus. Tamanhos separados para PC e celular.",16,40,colW-32,30,14,P.text2,T.LEFT)
 local U=require(RS.UIPreferences)
 T.progress(scaleRow,"ScaleTrack",82,91,colW-164,10,(value-U.min)/(U.max-U.min),P.accent)
 local minus=T.button(scaleRow,"Decrease","−",16,72,52,48,P.neutral,function() ctx.setUIScale(value-.05) end,{size=24})
 local plus=T.button(scaleRow,"Increase","+",colW-68,72,52,48,P.neutral,function() ctx.setUIScale(value+.05) end,{size=24})
 T.setEnabled(minus,value>U.min);T.setEnabled(plus,value<U.max)
 y+=148
 local reset=T.button(scroll,"ResetUIScale","Restaurar tamanho recomendado",0,y,colW,44,P.neutral,function() ctx.setUIScale(U.defaults[key]) end,{size=16})
 y+=50
 local state=T.para(scroll,"UISaveState","",0,y,colW,40,13,P.text3,T.LEFT)
 ctx.uiSettingsStatus=function()
  if not state.Parent then return end
  state.Text=ctx.uiSaveStatus=="pending" and "Aplicado. Salvando preferência..." or ctx.uiSaveStatus=="profile" and "Tamanho salvo no seu perfil." or ctx.uiSaveStatus=="error" and "Aplicado. Ajuste novamente para tentar salvar." or "Aplicado nesta sessão de teste."
 end
 ctx.uiSettingsStatus()
 y+=46
 y+=T.section(scroll,"Mixagem de áudio",0,y,colW,P.accent)''')
write(p,s)

p='StarterPlayer/StarterPlayerScripts/IslandTransition.lua';s=read(p)
s=rep(s,'local revision,lastDestination=0,nil','''local revision,lastDestination=0,nil
local shell
local function menuOpen() return shell and ((shell:GetAttribute("OpenPage") or "")~="" or shell:GetAttribute("PopupOpen")==true) end''')
s=rep(s,'else root.Size=UDim2.fromOffset(math.min(690,v.X*.66),math.min(152,v.Y*.28));root.Position=UDim2.fromScale(.5,.30);title.TextSize=v.Y<500 and 30 or 46 end','''else
  local factor=shell and shell:GetAttribute("UIScalePreference") or .85
  root.Size=UDim2.fromOffset(math.min(560*factor,v.X*.60),math.min(112*factor,v.Y*.24))
  root.Position=UDim2.fromScale(.5,.30);title.TextSize=(v.Y<500 and 29 or 40)*factor
 end
 local constraint=title:FindFirstChildOfClass("UITextSizeConstraint")
 if constraint then constraint.MinTextSize=title.TextSize;constraint.MaxTextSize=title.TextSize end''')
s=rep(s,'player:SetAttribute("TravelTransition",false);shield.Visible=false;resize()','player:SetAttribute("TravelTransition",false);shield.Visible=false;resize();root.Visible=not menuOpen()')
s=rep(s,'update()\n','''update()
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
''') if False else s
# Append only at EOF (avoid replacing the function declaration).
s+='''
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
'''
write(p,s)
print('Core, preferences, pass catalog, forge gating and UI patched.')
