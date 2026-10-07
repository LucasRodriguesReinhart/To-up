-- hex_f14d_agua.lua : F14d = area da agua com bordas resolvidas (briefing secao 5).
-- Guarda-corpo baixo de pedra ao redor dos 2 lagos (com vao na ponte), rochas nos cantos.
-- Cachoeiras laterais ja sairam na F14a; as 2 da frente ficam.
-- Idempotente: limpa HEX_F14D e colliders hx_f14d_.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F14C_OK")==true, "F14d: rode a F14c antes")
math.randomseed(14)
local rec = H.begin("HEX F14d agua")
local FD = H.folder(L,"HEX_F14D") H.clear(FD)
H.clearColliders("hx_f14d_")

local PEDRA = rgb(168,158,146)
local PEDRA_CLARA = rgb(190,181,168)

local rocha
for _,c in ipairs(L.HEX_Lagos:GetDescendants()) do
  if c:IsA("MeshPart") and c.Name:sub(1,9)=="LOB_rocha" then rocha=c break end
end

local nSeg, nRocha = 0, 0
for _,P in pairs(H.LAY.PONDS) do
  local f = P.face
  local s1,s2,d1,d2 = P.s1-0.7, P.s2+0.7, P.d1-0.7, P.d2+0.7
  -- trecho de borda: do ponto (sA) ao (sB) na profundidade d fixa
  local function trecho(sA, sB, d)
    if sB-sA < 1.5 then return end
    local cfm = H.faceCF(f,(sA+sB)/2, d, 0.42)
    H.part({Name="Borda", Size=V3(sB-sA, 0.85, 1.4), CFrame=cfm, Color=PEDRA,
      Material=Enum.Material.Slate, CanCollide=true}, FD)
    H.part({Name="BordaTopo", Size=V3(sB-sA+0.15, 0.22, 1.6), CFrame=cfm+V3(0,0.53,0),
      Color=PEDRA_CLARA, Material=Enum.Material.SmoothPlastic}, FD)
    nSeg += 1
  end
  -- lados longos (d1 e d2) com vao da ponte
  local g1, g2 = P.bridgeS-5.6, P.bridgeS+5.6
  for _,d in ipairs({d1, d2}) do
    trecho(s1, g1, d)
    trecho(g2, s2, d)
  end
  -- lados curtos (s1 e s2): construidos como trechos rotacionados 90 (usar faixa ao longo de d)
  for _,s in ipairs({s1, s2}) do
    local cfm = H.faceCF(f, s, (d1+d2)/2, 0.42) * CFrame.Angles(0, math.rad(90), 0)
    H.part({Name="Borda", Size=V3(d2-d1+1.4, 0.85, 1.4), CFrame=cfm, Color=PEDRA,
      Material=Enum.Material.Slate, CanCollide=true}, FD)
    H.part({Name="BordaTopo", Size=V3(d2-d1+1.55, 0.22, 1.6), CFrame=cfm+V3(0,0.53,0),
      Color=PEDRA_CLARA, Material=Enum.Material.SmoothPlastic}, FD)
    nSeg += 1
  end
  -- pilaretes nos 4 cantos e nas bocas da ponte
  local cantos = {{s1,d1},{s1,d2},{s2,d1},{s2,d2},{g1,d1},{g2,d1},{g1,d2},{g2,d2}}
  for _,cc in ipairs(cantos) do
    local cfm = H.faceCF(f, cc[1], cc[2], 0.7)
    H.part({Name="Pilarete", Size=V3(1.9,1.4,1.9), CFrame=cfm, Color=PEDRA, Material=Enum.Material.Slate, CanCollide=true}, FD)
    H.part({Name="PilareteTopo", Size=V3(1.4,0.5,1.4), CFrame=cfm+V3(0,0.95,0), Color=PEDRA_CLARA}, FD)
  end
  -- rochas nos cantos externos (fora da borda)
  if rocha then
    for i,cc in ipairs({{s1-2.5,d1-2}, {s2+2.5,d2+1.5}, {s2+2.8,d1-1.8}}) do
      local esc = ({0.95,0.62,0.42})[i]
      local c = rocha:Clone()
      for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
      c:SetAttribute("HexGen",true)
      c.Size = rocha.Size*esc
      c.CanCollide=false c.CanQuery=false c.CanTouch=false c.Anchored=true
      c.CFrame = H.faceCF(f, cc[1], cc[2], c.Size.Y/2-0.3) * CFrame.Angles(0, math.rad(math.random(0,359)), 0)
      c.Parent = FD
      nRocha += 1
    end
  end
end
say("bordas de pedra:", nSeg, "trechos; rochas:", nRocha)

L:SetAttribute("HEX_F14D_OK", true)
H.commit(rec)
return "F14d OK\n"..table.concat(rep,"\n")