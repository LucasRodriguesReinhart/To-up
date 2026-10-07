-- hex_f14e_forja_praca.lua : F14e = profundidade da forja + refinamento do pedestal (briefing secao 5).
-- Forja: fornalha circular de pedra com nucleo incandescente ATRAS do Ignis (nao o esconde),
-- bigorna e barril de tempera ao lado, luz quente. Ignis intocado.
-- Praca: frisos dourados no tambor hexagonal do monumento (topo e base).
-- Idempotente: limpa HEX_F14E.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F14D_OK")==true, "F14e: rode a F14d antes")
H.selfTest()
local rec = H.begin("HEX F14e forja e praca")
local FE = H.folder(L,"HEX_F14E") H.clear(FE)
H.clearColliders("hx_f14e_")

local PISO_FORJA = 10.0
local ESCURO = rgb(74,68,64)
local PEDRA = rgb(120,112,104)

-- ============ fornalha circular atras do Ignis ============
-- parede-fornalha em (0, piso, -122), de frente para a porta (+Z)
local cxz = CF(0, 0, -122)
-- base/plataforma
H.part({Name="ForjaBase", Size=V3(17,1.2,6), CFrame=cxz*CF(0,PISO_FORJA+0.6,1), Color=ESCURO, Material=Enum.Material.Slate, CanCollide=true}, FE)
-- anel de pedra (12 blocos radiais) num plano vertical de frente para +Z
local cy = PISO_FORJA + 8.2
for k=0,11 do
  local a = math.rad(30*k)
  H.part({Name="ForjaAnel", Size=V3(3.4,3.0,2.2),
    CFrame=CF(0,cy,-122.6)*CFrame.Angles(0,0,a)*CF(0,6.2,0)*CFrame.Angles(0,0,math.rad(0)),
    Color=PEDRA, Material=Enum.Material.Slate}, FE)
end
-- nucleo incandescente (disco vertical)
H.part({Name="ForjaNucleo", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(1.2,9.6,9.6),
  CFrame=CF(0,cy,-122.2)*CFrame.Angles(0,math.rad(90),0),
  Color=rgb(255,150,60), Material=Enum.Material.Neon}, FE)
H.part({Name="ForjaNucleoFundo", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(1.0,12.4,12.4),
  CFrame=CF(0,cy,-122.9)*CFrame.Angles(0,math.rad(90),0),
  Color=rgb(150,60,24), Material=Enum.Material.Slate}, FE)
local nucleo = FE:FindFirstChild("ForjaNucleo")
local pl=Instance.new("PointLight") pl.Range=30 pl.Brightness=1.4 pl.Color=rgb(255,140,60) pl.Shadows=false pl.Parent=nucleo
local pe=Instance.new("ParticleEmitter")
pe.Color=ColorSequence.new(rgb(255,190,90), rgb(255,110,40))
pe.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,0.5),NumberSequenceKeypoint.new(1,0.1)})
pe.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,0.3),NumberSequenceKeypoint.new(1,1)})
pe.Rate=8 pe.Lifetime=NumberRange.new(0.8,1.6) pe.Speed=NumberRange.new(1,2.5)
pe.SpreadAngle=Vector2.new(25,25) pe.LightEmission=1 pe.Parent=nucleo
say("fornalha circular com nucleo incandescente em z=-122")

-- ============ bigorna e barril de tempera ============
local bx = CF(8.5, 0, -114)
H.part({Name="BigornaBase", Size=V3(2.6,1.6,2.2), CFrame=bx*CF(0,PISO_FORJA+0.8,0), Color=rgb(96,64,44), Material=Enum.Material.Wood, CanCollide=true}, FE)
H.part({Name="BigornaCorpo", Size=V3(1.6,1.1,3.6), CFrame=bx*CF(0,PISO_FORJA+2.15,0), Color=rgb(60,62,68), Material=Enum.Material.Metal}, FE)
H.part({Name="BigornaTopo", Size=V3(1.8,0.5,4.6), CFrame=bx*CF(0,PISO_FORJA+2.95,0), Color=rgb(74,76,84), Material=Enum.Material.Metal}, FE)
H.part({Name="BigornaChifre", Class="WedgePart", Size=V3(1.4,0.9,1.3), CFrame=bx*CF(0,PISO_FORJA+2.5,2.9)*CFrame.Angles(0,math.rad(180),0), Color=rgb(74,76,84), Material=Enum.Material.Metal}, FE)
H.collider("hx_f14e_bigorna", V3(2.8,3.4,4.8), bx*CF(0,PISO_FORJA+1.7,0))
local tq = CF(-8.5, 0, -114)
H.part({Name="Barril", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(2.6,3.2,3.2), CFrame=tq*CF(0,PISO_FORJA+1.3,0)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(96,64,44), Material=Enum.Material.Wood, CanCollide=true}, FE)
H.part({Name="BarrilAgua", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.3,2.7,2.7), CFrame=tq*CF(0,PISO_FORJA+2.5,0)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(70,140,160), Material=Enum.Material.Glass, Transparency=0.2}, FE)
H.part({Name="BarrilAro", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.4,3.4,3.4), CFrame=tq*CF(0,PISO_FORJA+2.2,0)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(70,64,58), Material=Enum.Material.Metal}, FE)
H.collider("hx_f14e_barril", V3(3.3,3.4,3.3), tq*CF(0,PISO_FORJA+1.7,0))
say("bigorna e barril de tempera flanqueando o Ignis")

-- ============ frisos dourados no tambor do monumento ============
local OURO_VIVO = rgb(240,196,90)
local o = {Color=OURO_VIVO, Material=Enum.Material.SmoothPlastic}
H.hexRing(FE, o, 10.55, 11.15, 7.85, 8.4)  -- friso do topo
H.hexRing(FE, o, 10.55, 11.15, 2.2, 2.75)  -- friso da base
say("frisos dourados no tambor (topo e base)")

L:SetAttribute("HEX_F14E_OK", true)
H.commit(rec)
return "F14e OK\n"..table.concat(rep,"\n")