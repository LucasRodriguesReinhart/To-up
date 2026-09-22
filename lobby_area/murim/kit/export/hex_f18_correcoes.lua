-- hex_f18_correcoes.lua : F18 = correcoes do trecho-padrao (avaliacao ciclo 4).
-- NAO EXECUTAR antes de persistencia confirmada pelo usuario.
-- A) VASOs do anel do monumento -> ServerStorage.F14_REMOVIDOS (folhagem do template tem
--    Transparency 0.36 assada nas Unions Grass = retangulos translucidos; causa verificada).
--    Sem substituto no lugar (diretriz de nao preencher).
-- B) LIB_USUARIO.VASO_CORRIGIDO criado a parte (unions de folhagem opacas) para avaliacao futura.
-- C) Faces do pedestal v2: moldura com hierarquia de espessura (regua de baixo mais grossa),
--    anel do medalhao maior e concentrico ao emblema dourado original (vira moldura dele,
--    nao "O sobre quadrado"), painel recuado mantido.
-- D) Cornija: labio superior fino (perfil em 2 degraus, nao faixa nova).
-- E) Orbe legivel: garras mais grossas em bronze escuro, colar maior e mais alto (visivel),
--    casca mais translucida, nucleo menor e mais claro.
-- F) Atico: remove o par de blocos teal das extremidades (apareciam acima do beiral na lateral).
-- Idempotente: reconstrucoes guardadas por marcador HEX_F18_OK e por nomes.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local OURO = rgb(240,196,90)
local BRONZE = rgb(158,110,52)
local VERM_ESC = rgb(124,37,44)
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F17_OK")==true, "F18: rode a F17 antes")
local rec = H.begin("HEX F18 correcoes")
local F16 = L:FindFirstChild("HEX_F16") assert(F16, "F18: HEX_F16 ausente")
local F17 = L:FindFirstChild("HEX_F17") assert(F17, "F18: HEX_F17 ausente")
local F13 = L:FindFirstChild("HEX_F13")
local REM = SS:FindFirstChild("F14_REMOVIDOS") or (function() local f=Instance.new("Folder") f.Name="F14_REMOVIDOS" f.Parent=SS return f end)()

-- ============ A) retirar os VASOs do anel (com buque e colliders) ============
local nVaso = 0
if F13 then
  for _,m in ipairs(F13:GetChildren()) do
    if m.Name=="VASO" or m.Name=="VasoVerde" or m.Name=="VasoFlor" then
      local p = m:IsA("Model") and m:GetPivot().Position or m.Position
      if (V3(p.X,0,p.Z)).Magnitude < 40 then m.Parent=REM nVaso += 1 end
    end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name=="hx_f13_vaso" then c:Destroy() end
end
say("vasos do anel retirados (recuperaveis):", nVaso)

-- ============ B) VASO_CORRIGIDO na biblioteca ============
local LIBU = SS:FindFirstChild("LIB_USUARIO")
if LIBU and LIBU:FindFirstChild("VASO") and not LIBU:FindFirstChild("VASO_CORRIGIDO") then
  local c = LIBU.VASO:Clone()
  c.Name = "VASO_CORRIGIDO"
  local nOp = 0
  for _,d in ipairs(c:GetDescendants()) do
    if d:IsA("BasePart") and d.Material==Enum.Material.Grass and d.Transparency>0.05 then
      d.Transparency = 0 nOp += 1
    end
  end
  c.Parent = LIBU
  say("VASO_CORRIGIDO criado na LIB_USUARIO (unions opacas:", nOp, ")")
end

-- ============ C) faces do pedestal v2 ============
local tambor
for _,d in ipairs(L.HEX_Monumento:GetChildren()) do
  if d:IsA("Part") and d.Name=="Mon_tambor" then tambor=d break end
end
local apT = tambor.Size.Z/2
local y0T, y1T = tambor.Position.Y-tambor.Size.Y/2, tambor.Position.Y+tambor.Size.Y/2
local yFace = (y0T+y1T)/2
for _,p in ipairs(F16:GetChildren()) do
  if p.Name=="PainelFundo" or p.Name=="Moldura" or p.Name=="FaceMedalhao" or p.Name=="FaceMedalhaoMiolo" then p:Destroy() end
end
local lado = 2*apT*math.tan(math.rad(30))
local wIn = lado - 2.2
local hFace = (y1T-y0T) - 1.0
for _,th in ipairs({30,90,150,210,270,330}) do
  local c,s = math.cos(math.rad(th)), math.sin(math.rad(th))
  local n, t = V3(c,0,s), V3(-s,0,c)
  local function faceP(nome, w, h, dy, sal, esp, cor)
    H.part({Name=nome, Size=V3(w, h, esp), CFrame=CFrame.fromMatrix(n*(apT+sal)+V3(0,yFace+dy,0), t, V3(0,1,0)),
      Color=cor, Material=Enum.Material.SmoothPlastic}, F16)
  end
  faceP("PainelFundo", wIn-0.7, hFace-0.7, 0, 0.10, 0.16, VERM_ESC)
  -- hierarquia: regua de baixo 0.62, de cima 0.34, laterais 0.42
  faceP("Moldura", wIn, 0.34, (hFace/2-0.17), 0.26, 0.3, OURO)
  faceP("Moldura", wIn, 0.62, -(hFace/2-0.31), 0.30, 0.34, OURO)
  for _,sg in ipairs({1,-1}) do
    H.part({Name="Moldura", Size=V3(0.42, hFace, 0.3),
      CFrame=CFrame.fromMatrix(n*(apT+0.26)+t*(sg*(wIn/2-0.21))+V3(0,yFace,0), t, V3(0,1,0)),
      Color=OURO, Material=Enum.Material.SmoothPlastic}, F16)
  end
  -- anel maior emoldurando o emblema dourado ORIGINAL (concentrico, nao sobreposto)
  local posM = n*(apT+0.24) + V3(0, yFace, 0)
  H.part({Name="FaceMedalhao", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.2, 3.8, 3.8),
    CFrame=CFrame.fromMatrix(posM, n, V3(0,1,0)), Color=OURO, Material=Enum.Material.SmoothPlastic}, F16)
  H.part({Name="FaceMedalhaoFundo", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.16, 3.3, 3.3),
    CFrame=CFrame.fromMatrix(posM, n, V3(0,1,0)), Color=VERM_ESC, Material=Enum.Material.SmoothPlastic}, F16)
end
say("faces v2: moldura com hierarquia + anel emoldurando o emblema original")

-- ============ D) labio da cornija ============
if L:GetAttribute("HEX_F18_LABIO")~=true then
  H.hexRing(F16, {Color=rgb(26,64,71), Material=Enum.Material.SmoothPlastic}, apT+1.1, apT+1.6, y1T+0.5, y1T+0.72)
  L:SetAttribute("HEX_F18_LABIO", true)
  say("labio superior da cornija (perfil 2 degraus)")
end

-- ============ E) orbe legivel ============
local orbe
for _,d in ipairs(L.HEX_Monumento:GetChildren()) do
  if d:IsA("Part") and d.Name=="Mon_orbe" then orbe=d break end
end
local rO = orbe.Size.Y/2
local cO = orbe.Position
orbe.Transparency = 0.38
orbe.Color = rgb(255,166,52)
for _,p in ipairs(F16:GetChildren()) do
  if p.Name=="OrbeGarra" then
    p.Size = V3(0.95, rO*1.2, 0.95)
    p.Color = BRONZE p.Material = Enum.Material.SmoothPlastic
  elseif p.Name=="OrbeColar" then
    p.Size = V3(1.1, rO*2.15, rO*2.15)
    p.CFrame = CF(cO.X, cO.Y-rO*0.62, cO.Z)*CFrame.Angles(0,0,math.rad(90))
    p.Color = BRONZE p.Material = Enum.Material.SmoothPlastic
  elseif p.Name=="OrbeNucleo" then
    p.Size = orbe.Size*0.5
    p.Color = rgb(255,246,220)
  end
end
say("orbe: garras/colar em bronze visivel, casca 0.38, nucleo claro")

-- ============ F) blocos do atico nas pontas ============
local gal
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="SANT_galeria" then gal=d break end
end
local nB = 0
if gal then
  local LEN = gal.Size.Z - 4
  for _,p in ipairs(F17:GetChildren()) do
    if p.Name=="AticoBloco" then
      local lz = gal.CFrame:PointToObjectSpace(p.Position).Z
      if math.abs(lz) > LEN/2 - 9 then p:Destroy() nB += 1 end
    end
  end
end
say("blocos do atico removidos nas pontas:", nB)

L:SetAttribute("HEX_F18_OK", true)
H.commit(rec)
return "F18 OK\n"..table.concat(rep,"\n")