-- AreaAtmosphere (LocalScript, StarterPlayerScripts) COM o tema da Ilha 4 (Demon Slayer, Monte Natagumo), PLANO_DS
-- secao 10 "noite legivel". Base: a copia de ilha_shadowgarden/roblox/patches_jogo/AreaAtmosphere.client.lua
-- (efeitos da Ilha 3, 2026-10-06). So 3 pontos mudam, marcados com  -- [DS] :
--   1) profiles[4] ('Natagumo'): valores da secao 10 (Ambient, OutdoorAmbient, Brightness 1,6, Exposure +0,2,
--      Atmosphere 0,30 / (150,170,205) / (60,72,105) / Haze 1,8 / Glare 0, ColorCorrection sat -0,05 tint (232,236,255)).
--      ClockTime 20,5 = noite com a lua a ~37 graus no lado +X (a SG mediu 37 graus em -X com 3,5; 20,5 e o simetrico):
--      +X e o "tras-esquerda" de quem chega pela ponte (sudoeste LOCAL da ilha), o rumo que a secao 10 pede. AJUSTAR NO
--      PLAY (Lighting:GetMoonDirection()). ColorShift_Top frio = luar.
--   2) Brightness por perfil (profile.brightness; os outros continuam com 2).
--   3) atributo NatagumoMood (como o ShadowGardenMood da Ilha 3), publicado ANTES do ShadowGardenMood. O CeuNatagumo
--      funciona mesmo sem este item (le o CurrentIslandMood = 'Natagumo', que ja existe); e so a chave explicita.
-- Bloom (0,3 / limiar 1,4), Sky, mar de nuvens e luzes NightOnly ficam no CeuNatagumo (este script nao toca em Sky/Bloom).
-- SE o AreaAtmosphere do Studio tiver mudado depois de 2026-10-06 (a outra sessao mexe na Ilha 3), NAO cole o arquivo
-- inteiro: aplique so as 3 linhas [DS] no script de la.
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
 [4]={name='Natagumo',time=20.5,brightness=1.6,ambient=C(118,128,156),out=C(138,152,184),air=C(150,170,205),decay=C(60,72,105),density=.30,haze=1.8,glare=0,cst=C(176,192,232),tint=C(232,236,255),contrast=0,saturation=-.05,exposure=.2}, -- [DS] Ilha 4 (PLANO_DS secao 10): noite legivel, lua fria a ~37 graus em +X (ClockTime 20,5, ajustar no Play); Sky/bloom/mar de nuvens: CeuNatagumo
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
  tween(Lighting,{ClockTime=profile.time,Brightness=profile.brightness or 2,Ambient=profile.ambient,OutdoorAmbient=profile.out,ExposureCompensation=profile.exposure, -- [DS] Brightness por perfil (era 2 fixo)
   ColorShift_Top=profile.cst or base.ColorShift_Top,ColorShift_Bottom=profile.csb or base.ColorShift_Bottom})
  if atmosphere then tween(atmosphere,{Color=profile.air,Decay=profile.decay,Density=profile.density,Haze=profile.haze,Glare=profile.glare or .08,Offset=profile.offset or baseAir.Offset}) end
  tween(correction,{TintColor=profile.tint,Contrast=profile.contrast,Saturation=profile.saturation})
 else
  tween(Lighting,base) if atmosphere then tween(atmosphere,baseAir) end
  tween(correction,{TintColor=C(255,255,255),Contrast=0,Saturation=0})
 end
 player:SetAttribute('CurrentIslandMood',profile and profile.name or 'Default') player:SetAttribute('NatagumoMood',profile~=nil and profile.name=='Natagumo') player:SetAttribute('ShadowGardenMood',id==3) -- [DS] NatagumoMood ANTES do ShadowGardenMood (o CeuNatagumo devolve o Sky antes do CeuSombras salvar)
 Som.setArea(id)
end
player:GetAttributeChangedSignal('CurrentAreaId'):Connect(apply) apply()
