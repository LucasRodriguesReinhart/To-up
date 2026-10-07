local Players=game:GetService('Players')
local Lighting=game:GetService('Lighting')
local TweenService=game:GetService('TweenService')
local SoundService=game:GetService('SoundService')
local RS=game:GetService('ReplicatedStorage')
local player=Players.LocalPlayer
local C=Color3.fromRGB
local atmosphere=Lighting:FindFirstChildOfClass('Atmosphere')
local base={} for _,key in {'ClockTime','Brightness','Ambient','OutdoorAmbient','ExposureCompensation','ColorShift_Top','ColorShift_Bottom'} do base[key]=Lighting[key] end
local baseAir={} if atmosphere then for _,key in {'Color','Decay','Density','Haze','Glare','Offset'} do baseAir[key]=atmosphere[key] end end
local correction=Instance.new('ColorCorrectionEffect') correction.Name='IslandAtmosphere' correction.Parent=Lighting
local profiles={
 [1]={name='VilaDaFolha',time=15.1,ambient=C(139,143,129),out=C(161,166,142),air=C(218,224,205),decay=C(125,154,142),density=.25,haze=.7,tint=C(255,249,234),contrast=-.025,saturation=-.09,exposure=-.12},
 [2]={name='Namekusei',time=13.5,ambient=C(125,154,137),out=C(151,181,157),air=C(157,214,176),decay=C(92,143,130),density=.28,haze=1,tint=C(235,255,240),contrast=-.035,saturation=-.12,exposure=-.12},
 [4]={name='Natagumo',time=18.35,ambient=C(159,172,190),out=C(175,192,200),air=C(151,179,188),decay=C(83,116,134),density=.29,haze=.9,tint=C(237,245,255),contrast=-.055,saturation=-.14,exposure=.17},
 [3]={name='ShadowGarden',time=3.5,ambient=C(112,118,162),out=C(122,132,186),air=C(28,82,240),decay=C(8,10,32),density=.22,haze=1.05,glare=.15,offset=.4,cst=C(178,198,255),csb=C(40,60,140),tint=C(228,236,255),contrast=.1,saturation=.1,exposure=.25}, -- efeitos 2026-10-06 (referencia do usuario): noite azul profunda; zenite preto descendo para a faixa azul eletrico do horizonte (Atmosphere Color saturado + Haze ~1 + Offset), Decay navy, luar branco-azulado (ColorShift_Top) e lua grande a 37 graus em -X (ClockTime 3,5: sobre o castelo para quem cruza a ponte); contraste/saturacao positivos. Lua/estrelas/skybox/bloom: CeuSombras
 [5]={name='GrandLine',time=15.3,ambient=C(140,151,151),out=C(166,177,172),air=C(197,226,231),decay=C(112,160,172),density=.24,haze=.75,tint=C(255,250,236),contrast=-.025,saturation=-.09,exposure=-.1},
 [6]={name='CidadeZ',time=16.6,ambient=C(140,145,154),out=C(160,168,177),air=C(199,208,218),decay=C(109,131,154),density=.29,haze=1,tint=C(251,244,233),contrast=-.03,saturation=-.16,exposure=-.08},
}
local Som=require(RS:WaitForChild('SomJogo'))
local current=-1
local transitions={}
local function apply()
 local id=player:GetAttribute('CurrentAreaId') or 0 if id==current then return end current=id
 local profile=profiles[id]
 for _,t in transitions do t:Cancel() end table.clear(transitions)
 local function tween(obj,props)
  local t=TweenService:Create(obj,TweenInfo.new(1.6,Enum.EasingStyle.Sine),props) table.insert(transitions,t) t:Play()
 end
 if profile then
  tween(Lighting,{ClockTime=profile.time,Brightness=2,Ambient=profile.ambient,OutdoorAmbient=profile.out,ExposureCompensation=profile.exposure,
   ColorShift_Top=profile.cst or base.ColorShift_Top,ColorShift_Bottom=profile.csb or base.ColorShift_Bottom})
  if atmosphere then tween(atmosphere,{Color=profile.air,Decay=profile.decay,Density=profile.density,Haze=profile.haze,Glare=profile.glare or .08,Offset=profile.offset or baseAir.Offset}) end
  tween(correction,{TintColor=profile.tint,Contrast=profile.contrast,Saturation=profile.saturation})
 else
  tween(Lighting,base) if atmosphere then tween(atmosphere,baseAir) end
  tween(correction,{TintColor=C(255,255,255),Contrast=0,Saturation=0})
 end
 player:SetAttribute('CurrentIslandMood',profile and profile.name or 'Default') player:SetAttribute('ShadowGardenMood',id==3)
 Som.setArea(id)
end
player:GetAttributeChangedSignal('CurrentAreaId'):Connect(apply) apply()
