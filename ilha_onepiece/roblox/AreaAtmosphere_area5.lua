-- AreaAtmosphere (LocalScript, StarterPlayerScripts) COM o tema da Ilha 4 (Demon Slayer, trechos -- [DS], JA aplicados
-- no Studio em 2026-10-07) E o da Ilha 5 (One Piece / Wano, trechos -- [OP]). Base: ilha_demonslayer/roblox/
-- AreaAtmosphere_area4.lua (a versao aplicada hoje); as linhas [DS] estao IGUAIS. So 5 pontos [OP], todos aditivos:
--   1) profiles[5] ('GrandLine', o nome continua o mesmo: CurrentIslandMood = 'GrandLine'): DIA, PLANO_OP secao 10
--      (valores iniciais, ajustar no Play): ClockTime 13,5 + GeographicLatitude 30 (sol alto vindo de tras-esquerda de
--      quem chega pela ponte: fachada sul do castelo clara), Brightness 2,6, Exposure 0, Ambient (138,146,164),
--      OutdoorAmbient (150,162,182), EnvironmentDiffuse/Specular 0,6 / 0,3, Atmosphere Density 0,26 / Offset 0,15 /
--      Color (196,220,246) / Decay (112,156,206) / Glare 0,15 / Haze 1,0, ColorCorrection Brightness 0,02 /
--      Contrast 0,06 / Saturation 0,10 / Tint (255,250,244). (Se o agente de luz entregar AreaAtmosphere_area5.md nesta
--      pasta, os valores de la mandam: troque so a linha [5].)
--   2) base guarda tambem GeographicLatitude / EnvironmentDiffuseScale / EnvironmentSpecularScale (linha nova).
--   3) o tween do Lighting leva lat/eds/ess por perfil (linha nova; os outros perfis voltam ao valor base = sem mudanca).
--   4) ColorCorrection.Brightness por perfil (profile.cbright, padrao 0; volta a 0 fora das ilhas) (linhas novas).
--   5) atributo WanoMood (como NatagumoMood/ShadowGardenMood), linha nova depois deles. O CeuWano funciona mesmo sem
--      este item (le o CurrentIslandMood = 'GrandLine', que ja existe); e so a chave explicita.
-- Bloom (0,35 / 24 / limiar 1,6), SunRays (0,04 / 0,12), nuvens, mar local turquesa (36) e a garantia de ceu de dia
-- ficam no CeuWano (este script nao toca em Sky/Bloom).
-- V2 (2026-10-10): so a linha [5] mudou (perfil rosa-lilas da ref_03, PLANO_V2 secao 7.1).
-- SE o AreaAtmosphere do Studio tiver mudado depois de 2026-10-07, NAO cole o arquivo inteiro: aplique so as linhas [OP].
local Players=game:GetService('Players')
local Lighting=game:GetService('Lighting')
local TweenService=game:GetService('TweenService')
local SoundService=game:GetService('SoundService')
local RS=game:GetService('ReplicatedStorage')
local player=Players.LocalPlayer
local C=Color3.fromRGB
local atmosphere=Lighting:FindFirstChildOfClass('Atmosphere')
local base={} for _,key in {'ClockTime','Brightness','Ambient','OutdoorAmbient','ExposureCompensation','ColorShift_Top','ColorShift_Bottom'} do base[key]=Lighting[key] end
for _,key in {'GeographicLatitude','EnvironmentDiffuseScale','EnvironmentSpecularScale'} do base[key]=Lighting[key] end -- [OP] luz de dia de Wano (latitude e reflexos por perfil)
local baseAir={} if atmosphere then for _,key in {'Color','Decay','Density','Haze','Glare','Offset'} do baseAir[key]=atmosphere[key] end end
local correction=Instance.new('ColorCorrectionEffect') correction.Name='IslandAtmosphere' correction.Parent=Lighting
local profiles={
 [1]={name='VilaDaFolha',time=15.1,ambient=C(139,143,129),out=C(161,166,142),air=C(218,224,205),decay=C(125,154,142),density=.25,haze=.7,tint=C(255,249,234),contrast=-.025,saturation=-.09,exposure=-.12},
 [2]={name='Namekusei',time=13.5,ambient=C(125,154,137),out=C(151,181,157),air=C(157,214,176),decay=C(92,143,130),density=.28,haze=1,tint=C(235,255,240),contrast=-.035,saturation=-.12,exposure=-.12},
 [4]={name='Natagumo',time=20.5,brightness=1.6,ambient=C(118,128,156),out=C(138,152,184),air=C(150,170,205),decay=C(60,72,105),density=.30,haze=1.8,glare=0,cst=C(176,192,232),tint=C(232,236,255),contrast=0,saturation=-.05,exposure=.2}, -- [DS] Ilha 4 (PLANO_DS secao 10): noite legivel, lua fria a ~37 graus em +X (ClockTime 20,5, ajustar no Play); Sky/bloom/mar de nuvens: CeuNatagumo
 [3]={name='ShadowGarden',time=3.5,ambient=C(112,118,162),out=C(122,132,186),air=C(28,82,240),decay=C(8,10,32),density=.22,haze=1.05,glare=.15,offset=.4,cst=C(178,198,255),csb=C(40,60,140),tint=C(228,236,255),contrast=.1,saturation=.1,exposure=.25}, -- efeitos 2026-10-06 (referencia do usuario): noite azul profunda; zenite preto descendo para a faixa azul eletrico do horizonte (Atmosphere Color saturado + Haze ~1 + Offset), Decay navy, luar branco-azulado (ColorShift_Top) e lua grande a 37 graus em -X (ClockTime 3,5: sobre o castelo para quem cruza a ponte); contraste/saturacao positivos. Lua/estrelas/skybox/bloom: CeuSombras
 [5]={name='GrandLine',time=9.05,lat=10,brightness=2.2,ambient=C(150,136,168),out=C(178,156,196),eds=.5,ess=.25,air=C(238,198,228),decay=C(168,136,204),density=.30,offset=.20,haze=1.7,glare=.30,cst=C(255,222,234),tint=C(255,238,246),contrast=.05,saturation=.14,cbright=0,exposure=0}, -- [OP] Ilha 5 Wano V2 (PLANO_V2 sec. 7.1, U14 = ref_03): DIA rosa-lilas (Atmosphere rosa + Haze alto + ColorShift/tint rosados); ClockTime 9,05 / lat 10 FICAM (sol validado no Play); bloom/sunrays/nuvens rosadas/mar local: CeuWano
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
   GeographicLatitude=profile.lat or base.GeographicLatitude,EnvironmentDiffuseScale=profile.eds or base.EnvironmentDiffuseScale,EnvironmentSpecularScale=profile.ess or base.EnvironmentSpecularScale, -- [OP] lat/eds/ess por perfil (os outros perfis ficam no valor base)
   ColorShift_Top=profile.cst or base.ColorShift_Top,ColorShift_Bottom=profile.csb or base.ColorShift_Bottom})
  if atmosphere then tween(atmosphere,{Color=profile.air,Decay=profile.decay,Density=profile.density,Haze=profile.haze,Glare=profile.glare or .08,Offset=profile.offset or baseAir.Offset}) end
  tween(correction,{TintColor=profile.tint,Contrast=profile.contrast,Saturation=profile.saturation})
  tween(correction,{Brightness=profile.cbright or 0}) -- [OP] ColorCorrection.Brightness por perfil (Wano 0,02)
 else
  tween(Lighting,base) if atmosphere then tween(atmosphere,baseAir) end
  tween(correction,{TintColor=C(255,255,255),Contrast=0,Saturation=0})
  tween(correction,{Brightness=0}) -- [OP]
 end
 player:SetAttribute('CurrentIslandMood',profile and profile.name or 'Default') player:SetAttribute('NatagumoMood',profile~=nil and profile.name=='Natagumo') player:SetAttribute('ShadowGardenMood',id==3) -- [DS] NatagumoMood ANTES do ShadowGardenMood (o CeuNatagumo devolve o Sky antes do CeuSombras salvar)
 player:SetAttribute('WanoMood',profile~=nil and profile.name=='GrandLine') -- [OP] chave explicita da area 5 (o CeuWano le o CurrentIslandMood primeiro)
 Som.setArea(id)
end
player:GetAttributeChangedSignal('CurrentAreaId'):Connect(apply) apply()
