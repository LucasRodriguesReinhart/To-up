local Players=game:GetService('Players')
local Lighting=game:GetService('Lighting')
local TweenService=game:GetService('TweenService')
local SoundService=game:GetService('SoundService')
local RS=game:GetService('ReplicatedStorage')
local player=Players.LocalPlayer
local C=Color3.fromRGB
local atmosphere=Lighting:FindFirstChildOfClass('Atmosphere')
local base={} for _,key in {'ClockTime','Brightness','Ambient','OutdoorAmbient','ExposureCompensation'} do base[key]=Lighting[key] end
local baseAir={} if atmosphere then for _,key in {'Color','Decay','Density','Haze','Glare'} do baseAir[key]=atmosphere[key] end end
local correction=Instance.new('ColorCorrectionEffect') correction.Name='IslandAtmosphere' correction.Parent=Lighting
local profiles={
 [1]={name='VilaDaFolha',time=15.1,ambient=C(139,143,129),out=C(161,166,142),air=C(218,224,205),decay=C(125,154,142),density=.25,haze=.7,tint=C(255,249,234),contrast=-.025,saturation=-.09,exposure=-.12},
 [2]={name='Namekusei',time=13.5,ambient=C(125,154,137),out=C(151,181,157),air=C(157,214,176),decay=C(92,143,130),density=.28,haze=1,tint=C(235,255,240),contrast=-.035,saturation=-.12,exposure=-.12},
 [3]={name='Natagumo',time=18.35,ambient=C(159,172,190),out=C(175,192,200),air=C(151,179,188),decay=C(83,116,134),density=.29,haze=.9,tint=C(237,245,255),contrast=-.055,saturation=-.14,exposure=.17},
 [4]={name='ShadowGarden',time=.6,ambient=C(167,145,192),out=C(183,161,205),air=C(158,140,193),decay=C(98,78,130),density=.27,haze=.8,tint=C(248,237,255),contrast=-.07,saturation=-.16,exposure=.2},
 [5]={name='GrandLine',time=15.3,ambient=C(140,151,151),out=C(166,177,172),air=C(197,226,231),decay=C(112,160,172),density=.24,haze=.75,tint=C(255,250,236),contrast=-.025,saturation=-.09,exposure=-.1},
 [6]={name='CidadeZ',time=16.6,ambient=C(140,145,154),out=C(160,168,177),air=C(199,208,218),decay=C(109,131,154),density=.29,haze=1,tint=C(251,244,233),contrast=-.03,saturation=-.16,exposure=-.08},
}
local tracks={
 [0]={id='112898538778548',name='Lobby',volume=.23},
 [1]={id='82061470648013',name='Hidden Lotus Pond',volume=.22},
 [2]={id='1845421369',name='Space Atmosphere',volume=.23},
 [3]={id='9048681794',name='Mysterious Forest',volume=.2},
 [4]={id='131334832939011',name='The Forgotten Crypt',volume=.2},
 [5]={id='1835322563',name='Pirate King',volume=.2},
 [6]={id='1845676363',name='Home Bound',volume=.21},
}
local old=SoundService:FindFirstChild('OST') if old then old:Stop() end
local group=Instance.new('SoundGroup') group.Name='AreaMusic' group.Parent=SoundService
local sounds={} local fades={} local current=-1
for id,track in tracks do
 local s=Instance.new('Sound') s.Name='Theme_'..id s.SoundId='rbxassetid://'..track.id s.Volume=0 s.Looped=true s.SoundGroup=group s.Parent=SoundService
 s:SetAttribute('ThemeTitle',track.name) sounds[id]=s
end
local function updateMute()
 group.Volume=player:GetAttribute('MusicEnabled')==false and 0 or 1
end
updateMute() player:GetAttributeChangedSignal('MusicEnabled'):Connect(updateMute)
local transitions={}
local function apply()
 local id=player:GetAttribute('CurrentAreaId') or 0 if id==current then return end current=id
 local profile=profiles[id]
 for _,t in transitions do t:Cancel() end table.clear(transitions)
 local function tween(obj,props)
  local t=TweenService:Create(obj,TweenInfo.new(1.6,Enum.EasingStyle.Sine),props) table.insert(transitions,t) t:Play()
 end
 if profile then
  tween(Lighting,{ClockTime=profile.time,Brightness=2,Ambient=profile.ambient,OutdoorAmbient=profile.out,ExposureCompensation=profile.exposure})
  if atmosphere then tween(atmosphere,{Color=profile.air,Decay=profile.decay,Density=profile.density,Haze=profile.haze,Glare=.08}) end
  tween(correction,{TintColor=profile.tint,Contrast=profile.contrast,Saturation=profile.saturation})
 else
  tween(Lighting,base) if atmosphere then tween(atmosphere,baseAir) end
  tween(correction,{TintColor=C(255,255,255),Contrast=0,Saturation=0})
 end
 player:SetAttribute('CurrentIslandMood',profile and profile.name or 'Default') player:SetAttribute('ShadowGardenMood',id==4)
 for key,s in sounds do
  if fades[key] then fades[key]:Cancel() end
  if key==id and not s.IsPlaying then s:Play() end
  local t=TweenService:Create(s,TweenInfo.new(1.8,Enum.EasingStyle.Sine),{Volume=key==id and tracks[key].volume or 0}) fades[key]=t t:Play()
  if key~=id then t.Completed:Once(function(status) if status==Enum.PlaybackState.Completed and current~=key then s:Pause() end end) end
 end
 player:SetAttribute('AreaMusicTitle',tracks[id] and tracks[id].name or '')
end
player:GetAttributeChangedSignal('CurrentAreaId'):Connect(apply) apply()
