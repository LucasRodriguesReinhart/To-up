-- hex_f16_monumento.lua : F16 = trecho de qualidade final - monumento e entorno imediato.
-- NAO EXECUTAR antes do usuario confirmar o salvamento do place (briefing etapa 1).
-- Remodelagem por construcao, nao por cor:
-- A) 6 faces do tambor: painel recuado escuro + moldura dourada (4 reguas) + medalhao central;
-- B) cornija teal projetada com filete dourado + rodape de pedra escura (os frisos simples
--    do F14e proximos ao centro sao removidos - superados);
-- C) orbe alojado: colar dourado + 5 garras + orbe em 2 camadas (casca translucida + nucleo);
-- D) passadeiras vermelhas nos 3 eixos dos tapetes ligando piso -> degraus -> tambor;
-- E) feixe: curto, quente e quase apagado (a qualidade tem que funcionar sem o brilho).
-- Idempotente: limpa HEX_F16; efeitos no Mon_orbe com backup CorOriginal/atributos.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local OURO = rgb(240,196,90)
local VERM_ESC = rgb(124,37,44)
local TEAL = rgb(30,75,83)
local PEDRA_ESC = rgb(110,102,94)
local TAPETE = rgb(178,44,40)
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F15_OK")==true, "F16: rode a F15 antes")
H.selfTest()
local rec = H.begin("HEX F16 monumento")
local F16 = H.folder(L,"HEX_F16") H.clear(F16)

-- geometria real do tambor e degraus
local tambor, orbe, passo1, passo2, anelBase
for _,d in ipairs(L.HEX_Monumento:GetChildren()) do
  if d:IsA("Part") then
    if d.Name=="Mon_tambor" then tambor=d
    elseif d.Name=="Mon_orbe" then orbe=d
    elseif d.Name=="Mon_passo1" then passo1=d
    elseif d.Name=="Mon_passo2" then passo2=d
    elseif d.Name=="Mon_anel_base" then anelBase=d end
  end
end
assert(tambor and orbe and passo1 and passo2 and anelBase, "F16: pecas do monumento nao achadas")
local apT = tambor.Size.Z/2            -- apotema do tambor (~10.5)
local y0T, y1T = tambor.Position.Y-tambor.Size.Y/2, tambor.Position.Y+tambor.Size.Y/2
local ap1 = passo1.Size.Z/2            -- apotema do degrau externo
local ap2 = passo2.Size.Z/2
local apA = anelBase.Size.Z/2
local top1 = passo1.Position.Y+passo1.Size.Y/2
local top2 = passo2.Position.Y+passo2.Size.Y/2
local topA = anelBase.Position.Y+anelBase.Size.Y/2
say(("tambor ap=%.1f y=%.1f..%.1f; degraus ap %.1f/%.1f/%.1f tops %.1f/%.1f/%.1f"):format(apT,y0T,y1T,ap1,ap2,apA,top1,top2,topA))

-- remove os frisos simples do F14e no tambor (superados pela cornija/rodape)
local nFri = 0
local FE = L:FindFirstChild("HEX_F14E")
if FE then
  for _,p in ipairs(FE:GetChildren()) do
    if p:IsA("BasePart") and p.Position.Y>1.5 and p.Position.Y<9.5 and math.abs(p.Position.X)<14 and math.abs(p.Position.Z)<14 then
      local c=p.Color
      if c.R>0.85 and c.G>0.6 and c.B<0.5 then p:Destroy() nFri += 1 end
    end
  end
end
say("frisos F14e removidos:", nFri)

-- ============ A) faces do tambor ============
local lado = 2*apT*math.tan(math.rad(30)) -- largura da face
local wIn = lado - 2.2
local hFace = (y1T-y0T) - 1.0
local yFace = (y0T+y1T)/2
for _,th in ipairs({30,90,150,210,270,330}) do
  local c,s = math.cos(math.rad(th)), math.sin(math.rad(th))
  local n, t = V3(c,0,s), V3(-s,0,c)
  local function facePart(nome, w, h, dy, saliencia, esp, cor)
    local pos = n*(apT+saliencia) + V3(0, yFace+dy, 0)
    H.part({Name=nome, Size=V3(w, h, esp), CFrame=CFrame.fromMatrix(pos, t, V3(0,1,0)),
      Color=cor, Material=Enum.Material.SmoothPlastic}, F16)
  end
  -- painel recuado (menos saliente que a moldura)
  facePart("PainelFundo", wIn-0.7, hFace-0.7, 0, 0.10, 0.16, VERM_ESC)
  -- moldura dourada: 4 reguas
  facePart("Moldura", wIn, 0.42, (hFace/2-0.21), 0.26, 0.3, OURO)
  facePart("Moldura", wIn, 0.42, -(hFace/2-0.21), 0.26, 0.3, OURO)
  local wReg = 0.42
  for _,sg in ipairs({1,-1}) do
    local pos = n*(apT+0.26) + t*(sg*(wIn/2-wReg/2)) + V3(0, yFace, 0)
    H.part({Name="Moldura", Size=V3(wReg, hFace, 0.3), CFrame=CFrame.fromMatrix(pos, t, V3(0,1,0)),
      Color=OURO, Material=Enum.Material.SmoothPlastic}, F16)
  end
  -- medalhao central da face
  local posM = n*(apT+0.30) + V3(0, yFace, 0)
  H.part({Name="FaceMedalhao", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.22, 2.4, 2.4),
    CFrame=CFrame.fromMatrix(posM, V3(0,1,0), t)*CFrame.Angles(0,0,math.rad(90)),
    Color=OURO, Material=Enum.Material.SmoothPlastic}, F16)
  H.part({Name="FaceMedalhaoMiolo", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.26, 1.5, 1.5),
    CFrame=CFrame.fromMatrix(posM, V3(0,1,0), t)*CFrame.Angles(0,0,math.rad(90)),
    Color=VERM_ESC, Material=Enum.Material.SmoothPlastic}, F16)
end
say("6 faces: painel recuado + moldura + medalhao")

-- ============ B) cornija e rodape ============
local oC = {Color=TEAL, Material=Enum.Material.SmoothPlastic}
H.hexRing(F16, oC, apT-0.1, apT+1.25, y1T-0.05, y1T+0.62)
local oB = {Color=OURO, Material=Enum.Material.SmoothPlastic}
H.hexRing(F16, oB, apT-0.1, apT+0.75, y1T-0.33, y1T-0.05)
local oR = {Color=PEDRA_ESC, Material=Enum.Material.Slate}
H.hexRing(F16, oR, apT-0.1, apT+0.8, topA-0.05, topA+0.6)
say("cornija teal + filete + rodape de pedra")

-- ============ C) orbe alojado ============
if orbe:GetAttribute("CorOriginal")==nil then orbe:SetAttribute("CorOriginal", orbe.Color) end
if orbe:GetAttribute("F16_Transp")==nil then orbe:SetAttribute("F16_Transp", orbe.Transparency) end
orbe.Color = rgb(255,178,70)
orbe.Transparency = 0.25
local rO = orbe.Size.Y/2
local cO = orbe.Position
-- nucleo interno claro
H.part({Name="OrbeNucleo", Class="Part", Shape=Enum.PartType.Ball, Size=orbe.Size*0.55,
  CFrame=CF(cO), Color=rgb(255,236,180), Material=Enum.Material.Neon, CastShadow=false}, F16)
-- colar dourado sob o orbe
H.part({Name="OrbeColar", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.8, rO*1.7, rO*1.7),
  CFrame=CF(cO.X, cO.Y-rO*0.78, cO.Z)*CFrame.Angles(0,0,math.rad(90)),
  Color=OURO, Material=Enum.Material.Metal}, F16)
-- 5 garras inclinadas segurando o orbe
for k=0,4 do
  local a = math.rad(72*k)
  local px, pz = math.cos(a)*rO*0.95, math.sin(a)*rO*0.95
  H.part({Name="OrbeGarra", Size=V3(0.55, rO*1.15, 0.55),
    CFrame=CF(cO.X+px, cO.Y-rO*0.35, cO.Z+pz)
      *CFrame.Angles(0, -a, 0)*CFrame.Angles(0, 0, math.rad(-22)),
    Color=OURO, Material=Enum.Material.Metal}, F16)
end
say("orbe: casca translucida + nucleo + colar + 5 garras")

-- ============ D) passadeiras nos 3 eixos ============
-- eixos dos tapetes: portao (90), galeria (30), loja (150)
local nPass = 0
for _,th in ipairs({30, 90, 150}) do
  local c,s = math.cos(math.rad(th)), math.sin(math.rad(th))
  local n, t = V3(c,0,s), V3(-s,0,c)
  local function trecho(rIn, rOut, topo)
    local mid = n*((rIn+rOut)/2) + V3(0, topo+0.05, 0)
    local len = rOut-rIn
    H.part({Name="Passadeira", Size=V3(4.6, 0.08, len), CFrame=CFrame.fromMatrix(mid, t, V3(0,1,0)),
      Color=TAPETE, Material=Enum.Material.Fabric}, F16)
    for _,sg in ipairs({1,-1}) do
      H.part({Name="PassadeiraBorda", Size=V3(0.5, 0.07, len), CFrame=CFrame.fromMatrix(mid+t*(sg*2.55), t, V3(0,1,0)),
        Color=OURO, Material=Enum.Material.SmoothPlastic}, F16)
    end
  end
  trecho(ap1+0.2, 24.2, 0)      -- piso: liga ao anel vermelho do chao
  trecho(ap2-0.4, ap1+0.4, top1) -- degrau 1
  trecho(apA-0.4, ap2+0.4, top2) -- degrau 2
  nPass += 3
end
say("passadeiras: 3 eixos x 3 trechos =", nPass)

-- ============ E) feixe discreto ============
local P1 = L:FindFirstChild("HEX_P1")
local feixe = P1 and P1:FindFirstChild("P1_feixe")
if feixe then
  feixe.Size = V3(26, 2.2, 2.2)
  feixe.CFrame = CF(cO.X, cO.Y+30, cO.Z)*CFrame.Angles(0,0,math.rad(90))
  feixe.Color = rgb(255,205,130)
  feixe.Transparency = 0.9
  say("feixe encurtado/aquecido/apagado (Transparency 0.9)")
end

L:SetAttribute("HEX_F16_OK", true)
H.commit(rec)
return "F16 OK\n"..table.concat(rep,"\n")