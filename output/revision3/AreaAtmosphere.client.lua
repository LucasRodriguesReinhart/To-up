-- Local per-area mood; the lobby and daytime islands retain their original lighting.
local Players=game:GetService("Players")
local Lighting=game:GetService("Lighting")
local TweenService=game:GetService("TweenService")
local player=Players.LocalPlayer
local original={ClockTime=Lighting.ClockTime,Brightness=Lighting.Brightness,Ambient=Lighting.Ambient,OutdoorAmbient=Lighting.OutdoorAmbient,FogColor=Lighting.FogColor,FogStart=Lighting.FogStart,FogEnd=Lighting.FogEnd}
local grade=Instance.new("ColorCorrectionEffect") grade.Name="ShadowGardenMood" grade.Parent=Lighting
local atmosphere=Lighting:FindFirstChildOfClass("Atmosphere")
local savedAtmosphere=atmosphere and {Color=atmosphere.Color,Decay=atmosphere.Decay,Density=atmosphere.Density,Haze=atmosphere.Haze,Glare=atmosphere.Glare}
local atmosphereTween
local active=false
local tween,gradeTween
local function setMood(shadow)
 if shadow==active then return end active=shadow
 if tween then tween:Cancel() end if gradeTween then gradeTween:Cancel() end
 local props=shadow and {ClockTime=0.4,Brightness=2.5,Ambient=Color3.fromRGB(130,107,162),OutdoorAmbient=Color3.fromRGB(143,120,173),FogColor=Color3.fromRGB(54,32,94),FogStart=75,FogEnd=330} or original
 tween=TweenService:Create(Lighting,TweenInfo.new(1.6),props) tween:Play()
 gradeTween=TweenService:Create(grade,TweenInfo.new(1.6),{TintColor=shadow and Color3.fromRGB(245,230,255) or Color3.new(1,1,1),Contrast=shadow and -.06 or 0,Saturation=shadow and -.15 or 0}) gradeTween:Play()
 if atmosphere and savedAtmosphere then
  if atmosphereTween then atmosphereTween:Cancel() end
  atmosphereTween=TweenService:Create(atmosphere,TweenInfo.new(1.6),shadow and {Color=Color3.fromRGB(158,128,199),Decay=Color3.fromRGB(90,63,137),Density=.22,Haze=.7,Glare=0} or savedAtmosphere)
  atmosphereTween:Play()
 end
 player:SetAttribute("ShadowGardenMood",shadow)
end
while task.wait(.3) do
 local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
 local p=root and root.Position
 setMood(p~=nil and math.abs(p.X)<135 and math.abs(p.Z-1075)<112)
end
