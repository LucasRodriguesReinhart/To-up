-- Local atmosphere per island. Leaving the area restores the original lobby lighting.
local Players=game:GetService("Players")
local Lighting=game:GetService("Lighting")
local TweenService=game:GetService("TweenService")
local Config=require(game.ReplicatedStorage.Config)
local player=Players.LocalPlayer
local C=Color3.fromRGB
local original={ClockTime=Lighting.ClockTime,Brightness=Lighting.Brightness,Ambient=Lighting.Ambient,OutdoorAmbient=Lighting.OutdoorAmbient,FogColor=Lighting.FogColor,FogStart=Lighting.FogStart,FogEnd=Lighting.FogEnd}
local atmosphere=Lighting:FindFirstChildOfClass("Atmosphere")
local savedAtmosphere=atmosphere and {Color=atmosphere.Color,Decay=atmosphere.Decay,Density=atmosphere.Density,Haze=atmosphere.Haze,Glare=atmosphere.Glare}
local grade=Instance.new("ColorCorrectionEffect") grade.Name="IslandAtmosphere" grade.Parent=Lighting
local profiles={
 [3]={name="Natagumo",lighting={ClockTime=18.1,Brightness=2.4,Ambient=C(132,141,162),OutdoorAmbient=C(142,152,171),FogColor=C(105,132,157),FogStart=90,FogEnd=420},
  air={Color=C(175,199,214),Decay=C(102,123,158),Density=.24,Haze=.7,Glare=0},tint=C(232,245,255),contrast=-.04,saturation=-.05},
 [4]={name="ShadowGarden",lighting={ClockTime=.4,Brightness=2.5,Ambient=C(130,107,162),OutdoorAmbient=C(143,120,173),FogColor=C(54,32,94),FogStart=75,FogEnd=330},
  air={Color=C(158,128,199),Decay=C(90,63,137),Density=.22,Haze=.7,Glare=0},tint=C(245,230,255),contrast=-.06,saturation=-.15},
 [5]={name="GrandLine",lighting={ClockTime=14.2,Brightness=2.5,Ambient=C(128,136,134),OutdoorAmbient=C(159,165,157),FogColor=C(151,204,230),FogStart=150,FogEnd=650},
  air={Color=C(210,229,231),Decay=C(126,168,190),Density=.23,Haze=.65,Glare=.1},tint=C(255,250,238),contrast=-.03,saturation=-.03},
 [6]={name="CidadeZ",lighting={ClockTime=15.8,Brightness=2.4,Ambient=C(130,139,149),OutdoorAmbient=C(153,162,169),FogColor=C(160,181,190),FogStart=120,FogEnd=500},
  air={Color=C(212,218,219),Decay=C(135,154,169),Density=.24,Haze=.6,Glare=.08},tint=C(249,248,244),contrast=-.03,saturation=-.08},
}
local current=0
local running={}
local function apply(id)
 if id==current then return end current=id
 for _,tween in ipairs(running) do tween:Cancel() end table.clear(running)
 local profile=profiles[id]
 local function tween(instance,props)
  local t=TweenService:Create(instance,TweenInfo.new(1.5),props) table.insert(running,t) t:Play()
 end
 tween(Lighting,profile and profile.lighting or original)
 tween(grade,{TintColor=profile and profile.tint or Color3.new(1,1,1),Contrast=profile and profile.contrast or 0,Saturation=profile and profile.saturation or 0})
 if atmosphere and savedAtmosphere then tween(atmosphere,profile and profile.air or savedAtmosphere) end
 player:SetAttribute("ShadowGardenMood",id==4)
 player:SetAttribute("CurrentIslandMood",profile and profile.name or "Default")
end
while task.wait(.3) do
 local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
 local id=0
 if root then for _,area in ipairs(Config.Areas) do
  local offset=root.Position-area.centro
  if profiles[area.id] and math.abs(offset.X)<135 and math.abs(offset.Z)<112 then id=area.id break end
 end end
 apply(id)
end

