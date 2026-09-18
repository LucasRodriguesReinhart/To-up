-- Temporary Studio-only regression check. Removed after the verification run.
if not game:GetService("RunService"):IsStudio() then return end
local RS=game.ReplicatedStorage
local U=require(RS.UIPreferences)
local PD=require(script.Parent.PlayerData)
local Passes=require(script.Parent.Passes)
local Ignis=require(script.Parent.IgnisService)
local Config=require(RS.Config)
local Mon=require(RS.MonetizacaoConfig)
local Economy=require(script.Parent.Economia)
local results={}
local function check(name,condition) assert(condition,name);table.insert(results,name) end
check("nine real gamepasses",#Mon.PASSES==9)
check("NaN rejected",U.value(0/0)==nil)
check("infinite rejected",U.value(math.huge)==nil)
check("nested rejected",U.value({})==nil)
local clean=U.sanitize({desktopScale=100,mobileScale=-10,coins=100000})
check("bounded scale whitelist",clean.desktopScale==1.15 and clean.mobileScale==.65 and clean.coins==nil)
local char=Instance.new("Model")
local root=Instance.new("Part");root.Name="HumanoidRootPart";root.Anchored=true;root.Parent=char
local fake={Character=char,UserId=-6006}
local owned={}
local original=Passes.possui
-- This block does not yield. It restores the dependency even when an assertion fails.
Passes.possui=function(player,name) if player==fake then return owned[name]==true end return original(player,name) end
local ok,err=pcall(function()
 root.Position=Vector3.new(100000,100000,100000)
 check("remote forge denied without pass",not Ignis.podeVender(fake,false,"portable"))
 check("forged npc flag denied at distance",not Ignis.podeVender(fake,false,"npc"))
 check("nil mode denied without pass",not Ignis.podeVender(fake,false,nil))
 local belly=workspace.NPCs.Ignis:FindFirstChild("belly",true)
 assert(belly,"Ignis belly missing")
 root.Position=belly.Position
 check("free physical Ignis sale allowed",Ignis.podeVender(fake,false,"npc"))
 check("HUD still needs portable pass beside NPC",not Ignis.podeVender(fake,false,"portable"))
 owned.PortableForge=true;root.Position=Vector3.new(100000,100000,100000)
 check("owner allowed remotely",Ignis.podeVender(fake,false,"portable"))
 check("portable does not grant automatic selling",not Ignis.podeVender(fake,true,"portable"))
 local profile={__player=fake,areas={[1]=true},boosts={sorte=0,moedas=0}}
 check("base pet slots",PD.slotsPets(profile)==Config.PET_SLOTS_BASE)
 owned.PetSlots=true
 check("three extra pet slots",PD.slotsPets(profile)==Config.PET_SLOTS_BASE+3)
 local hats=PD.slots(profile);owned.HatSlot=true
 check("three extra hat slots",PD.slots(profile)==hats+3)
 owned.Inventario=true;owned.Inventory300=true;owned.Inventory1000=true
 check("inventory passes stack pets",PD.capacidadePets(profile)==Config.capacidadePets()+1350)
 check("inventory passes stack hats",PD.capacidadeHats(profile)==Config.capacidadeHats()+1350)
 owned.Lucky=true;owned.LuckyPlus=true
 check("both lucky benefits applied",math.abs(Economy.luckyMult(fake,profile)-1.875)<.00001)
end)
Passes.possui=original;char:Destroy()
assert(ok,err)
script:SetAttribute("Results",game:GetService("HttpService"):JSONEncode(results))
script:SetAttribute("Passed",#results)
print("[UIV6 QA] "..#results.." checks passed")
