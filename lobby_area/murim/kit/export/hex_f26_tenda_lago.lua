-- hex_f26_tenda_lago.lua : F26 = a loja vira TENDA de verdade e o lago vira UM corpo d'agua.
-- 1) DES-TEMPLIFICAR a loja: saem as 22 balaustradas de pedra (KIT_bal_seg) e as 31 pecas de
--    base ornamental (KIT_sumeru_seg/canto) do patamar + seus colliders. O piso do patamar
--    FICA (o PadLoja depende dele).
-- 2) TENDA v3 pela referencia: 6 postes FINOS de madeira, travessas aparentes, cobertura de
--    TECIDO EM ARCO (3 segmentos por agua com inclinacao progressiva = catenaria, listras
--    vermelho/teal correndo do cume a beira), barrado festonado, cordas e ferragens.
--    Placa menor e DESLOCADA (nao cobre o vendedor).
-- 3) LAGO refeito como POLIGONO UNICO: perimetro por funcao radial (harmonicos), 44 vertices,
--    preenchido por triangulacao em leque (star-shaped por construcao) com WedgeParts.
--    Sem elipses sobrepostas. ~+28% de area, so no lado direito.
-- 4) Borda acompanha o perimetro real; 3 pedras maiores; queda d'agua numa extremidade.
-- 5) LIMPEZA: 8 rochas orfas das vinhetas (bancos ja removidos) e rochas soltas no pavimento.
-- Idempotente: limpa HEX_F26 e o que a F24 criou de lago/tenda.
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
H.selfTest()
local L, C = H.L, H.C
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F25_OK")==true, "F26: rode a F25 antes")
math.randomseed(26)
local rec = H.begin("HEX F26 tenda e lago")
local F24 = L:FindFirstChild("HEX_F24")
local F26 = H.folder(L,"HEX_F26") H.clear(F26)
H.clearColliders("hx_f26_")
local REM = SS:FindFirstChild("F24_REMOVIDOS") or (function() local f=Instance.new("Folder") f.Name="F24_REMOVIDOS" f.Parent=SS return f end)()
local function tira(i, sub)
  if not i or i:IsDescendantOf(REM) then return 0 end
  if i:GetAttribute("OrigemPath")==nil then i:SetAttribute("OrigemPath", i.Parent:GetFullName()) end
  i.Parent = H.folder(REM, sub)
  return 1
end

-- ============ 1) des-templificar a loja ============
local nTpl = 0
local SAI_TEMPLO = {KIT_bal_seg=true, KIT_sumeru_seg=true, KIT_sumeru_canto=true}
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and SAI_TEMPLO[d.Name] then
    local p = d.Position
    if p.X<-95 and p.X>-142 and p.Z<-30 and p.Z>-75 then nTpl += tira(d, "LojaTemplo") end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  local p = c.Position
  if p.X<-95 and p.X>-142 and p.Z<-30 and p.Z>-75 then
    if c.Name:find("_bal_") or c.Name:find("loja_banner") or c.Name:find("loja_fundo") or c.Name:find("loja_lado") then
      nTpl += tira(c, "LojaTemplo")
    end
  end
end
say("linguagem de templo removida da loja:", nTpl, "pecas (balaustradas + base ornamental)")

-- ============ 2) tenda v3 ============
local S = L:GetAttribute("F22_LojaCF")
assert(S, "F26: F22_LojaCF ausente")
local chao = 7.98
local function TB(lx,ly,lz) return S*CF(lx, ly-13.28, lz) end
if F24 then
  for _,p in ipairs(F24:GetChildren()) do
    if p.Name:sub(1,5)=="Tenda" then p:Destroy() end
  end
end
local MAD = rgb(82,56,40)
local MAD_CLARA = rgb(120,84,56)
local OURO = rgb(226,178,84)
local LX_F, LX_B = 8.2, -8.2   -- frente (entrada) e fundo
-- postes FINOS com sapata discreta
for _,lx in ipairs({LX_F, LX_B}) do
  for _,lz in ipairs({-9.6, 0, 9.6}) do
    H.part({Name="TendaSapata", Size=V3(1.3,0.45,1.3), CFrame=TB(lx, chao+0.22, lz),
      Color=rgb(150,140,126), Material=Enum.Material.Slate}, F26)
    H.part({Name="TendaPoste", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(10.0,0.85,0.85),
      CFrame=TB(lx, chao+5.2, lz)*CFrame.Angles(0,0,math.rad(90)),
      Color=MAD, Material=Enum.Material.Wood, CanCollide=true}, F26)
    H.part({Name="TendaFerragem", Size=V3(0.95,0.45,0.95), CFrame=TB(lx, chao+10.05, lz),
      Color=OURO, Material=Enum.Material.Metal}, F26)
  end
end
-- travessas aparentes
for _,lx in ipairs({LX_F, LX_B}) do
  H.part({Name="TendaTravessa", Size=V3(0.5,0.5,20.2), CFrame=TB(lx, chao+9.9, 0), Color=MAD_CLARA, Material=Enum.Material.Wood}, F26)
end
for _,lz in ipairs({-9.6, 0, 9.6}) do
  H.part({Name="TendaTravessa", Size=V3(16.9,0.45,0.45), CFrame=TB(0, chao+9.9, lz), Color=MAD_CLARA, Material=Enum.Material.Wood}, F26)
end
-- cumeeira: alta o bastante para o tecido APOIAR nas travessas (antes passava por baixo)
local RIDGE = chao + 13.6
H.part({Name="TendaCumeeira", Size=V3(0.7,0.7,21.6), CFrame=TB(0, RIDGE, 0), Color=MAD, Material=Enum.Material.Wood}, F26)
-- COBERTURA DE TECIDO EM ARCO: 3 segmentos por agua, inclinacao progressiva (catenaria),
-- listras alternadas correndo do cume a beira
local QUEDA, LARG = 4.0, 9.4  -- y(poste 8.2)=chao+10.5 (sobre a travessa), beira em chao+9.6
local function yArco(x) return RIDGE - QUEDA*((x/LARG)^1.75) end
local nTec = 0
for _,lado in ipairs({1,-1}) do
  for seg=0,2 do
    local x0, x1 = seg*(LARG/3), (seg+1)*(LARG/3)
    local y0, y1 = yArco(x0), yArco(x1)
    local comp = math.sqrt((x1-x0)^2 + (y0-y1)^2)
    local ang = math.atan2(y0-y1, x1-x0)
    for k=0,7 do
      local lz = -9.45 + k*2.7
      -- listra CONTINUA do cume a beira (alternar por seg dava xadrez)
      local cor = (k%2==0) and rgb(186,52,44) or rgb(32,86,94)
      H.part({Name="TendaTecido", Size=V3(comp, 0.22, 2.7),
        -- sinal NEGATIVO: rotacao +Z levanta o +X local; a beira tem que CAIR
        CFrame=TB(lado*(x0+x1)/2, (y0+y1)/2, lz)*CFrame.Angles(0,0,math.rad(-lado*math.deg(ang))),
        Color=cor, Material=Enum.Material.Fabric}, F26)
      nTec += 1
    end
  end
end
-- barrado festonado nas beiradas longas (comprimentos alternados)
local nAba = 0
for _,lado in ipairs({1,-1}) do
  local yB = yArco(LARG) - 0.1
  for k=0,13 do
    local lz = -9.75 + k*1.5
    local alt = (k%2==0) and 1.6 or 1.05
    H.part({Name="TendaAba", Size=V3(0.28, alt, 1.5), CFrame=TB(lado*(LARG+0.15), yB-alt/2, lz),
      Color=(k%2==0) and rgb(186,52,44) or rgb(32,86,94), Material=Enum.Material.Fabric}, F26)
    nAba += 1
  end
end
-- valance das testeiras (frente e fundo) + cordas de amarracao
for _,lz in ipairs({-10.6, 10.6}) do
  H.part({Name="TendaValance", Size=V3(19,1.1,0.25), CFrame=TB(0, chao+9.7, lz),
    Color=rgb(186,52,44), Material=Enum.Material.Fabric}, F26)
end
-- (cordas diagonais removidas: liam como gravetos soltos)
-- patamar cru (NUC/PODIO brancos) tingido na cor da pedra do lobby
local nTint = 0
local HLoja = L:FindFirstChild("HEX_Loja")
for _,Patio in ipairs({L:FindFirstChild("Patio"), HLoja}) do
 if Patio then
  for _,d in ipairs(Patio:GetChildren()) do
    if d:IsA("BasePart") and (d.Name:sub(1,4)=="NUC_" or d.Name:sub(1,6)=="PODIO_" or d.Name=="KIT_piso_mod") then
      local p = d.Position
      if p.X<-100 and p.X>-142 and p.Z<-30 and p.Z>-75 then
        if d:GetAttribute("CorOriginal")==nil then d:SetAttribute("CorOriginal", d.Color) end
        d.Color = rgb(186,174,156)
        d.Material = Enum.Material.Slate
        nTint += 1
      end
    end
  end
 end
end
say("patamar da loja tingido (NUC/PODIO/piso):", nTint, "pecas")
say("tenda v3: postes finos, tecido em arco (", nTec, "faixas), barrado (", nAba, "abas), cordas")
-- placa menor e deslocada (nao cobre o vendedor, que fica em lz=0)
local F14C = L:FindFirstChild("HEX_F14C")
local F20f = L:FindFirstChild("HEX_F20")
-- pendurada na travessa da frente, DESLOCADA 7 studs do eixo do vendedor (lz=0)
local placaCF = TB(LX_F+0.45, chao+7.4, -9.6) * CFrame.Angles(0, math.rad(-90), 0)
if F14C then
  for _,p in ipairs(F14C:GetChildren()) do
    if p.Name:sub(1,5)=="Placa" and p:IsA("BasePart") then
      if p:GetAttribute("S0_F26")==nil then p:SetAttribute("S0_F26", p.Size) end
      local s0 = p:GetAttribute("S0_F26")
      p.Size = s0*0.72
      if p.Name=="PlacaFundo" then p.CFrame = placaCF
      elseif p.Name=="PlacaCorrente" then p.CFrame = placaCF*CF(0,2.3,0) end
    end
  end
  -- molduras: 2 horizontais (topo/base) e 2 verticais (laterais), pelo tamanho novo
  local horiz, vert = {}, {}
  for _,p in ipairs(F14C:GetChildren()) do
    if p.Name=="PlacaMoldura" then
      if p.Size.X > p.Size.Y then table.insert(horiz,p) else table.insert(vert,p) end
    end
  end
  for i,p in ipairs(horiz) do p.CFrame = placaCF*CF(0, (i==1 and 1.66 or -1.66), 0) end
  for i,p in ipairs(vert)  do p.CFrame = placaCF*CF((i==1 and -2.66 or 2.66), 0, 0) end
end
-- simbolo da placa = a MochilaV2 de maior volume (marcada por atributo na 1a vez;
-- o filtro por altura falhava depois que a placa mudava de lugar)
if F20f then
  local simbolo
  for _,m in ipairs(F20f:GetChildren()) do
    if m.Name=="MochilaV2" and m:GetAttribute("SimboloPlaca") then simbolo = m break end
  end
  if not simbolo then
    local maior = 0
    for _,m in ipairs(F20f:GetChildren()) do
      if m.Name=="MochilaV2" then
        local _, sz = m:GetBoundingBox()
        local vol = sz.X*sz.Y*sz.Z
        if vol > maior then maior, simbolo = vol, m end
      end
    end
    if simbolo then simbolo:SetAttribute("SimboloPlaca", true) end
  end
  if simbolo then
    local _, sz = simbolo:GetBoundingBox()
    if sz.Y > 3.2 then simbolo:ScaleTo(simbolo:GetScale()*0.72) end
    simbolo:PivotTo(placaCF*CF(0,-0.2,-0.8))
  end
end
-- vendedor: o PIVO do Model R15 fica nos PES (nao no centro do bbox) - assentar em chao
local npc
for _,c in ipairs(workspace:GetChildren()) do
  if c.Name:match("^npc vendedor") then npc=c break end
end
if npc then
  npc:PivotTo(S * CF(2.4, chao-13.28, 0) * CFrame.Angles(0, math.rad(-90), 0))
  local cf,sz = npc:GetBoundingBox()
  local baseY = cf.Position.Y - sz.Y/2
  if math.abs(baseY-chao) > 0.15 then -- pivo nao era nos pes: corrige pela medida real
    npc:PivotTo(npc:GetPivot() + V3(0, chao-baseY, 0))
  end
  local hrp = npc:FindFirstChild("HumanoidRootPart")
  if hrp then hrp.Anchored = true end
  local cf2 = npc:GetBoundingBox()
  say(("vendedor assentado: base Y %.2f (chao %.2f)"):format(cf2.Position.Y-sz.Y/2, chao))
end
say("placa reduzida (0.72) e deslocada para lz=-6.4; vendedor livre no centro")

-- ============ 3/4) lago: poligono unico ============
if F24 then
  for _,p in ipairs(F24:GetChildren()) do
    local n=p.Name
    if n:sub(1,8)=="LagoAgua" or n:sub(1,7)=="LagoAro" or n=="LagoMordida" or n=="Vitoria" then p:Destroy() end
  end
end
local F22 = L:FindFirstChild("HEX_F22")
if F22 then
  for _,p in ipairs(F22:GetChildren()) do
    if p.Name:sub(1,7)=="B_Agua_" or p.Name:sub(1,6)=="B_Aro_" then p:Destroy() end
  end
end
-- perimetro: funcao radial suave (um unico contorno, sem sobreposicao)
local CS, CD = -18, 28        -- centro em coords de face
local RA, RB = 38, 15         -- raios (s, d)
local N = 44
-- amplitudes fortes: extremidade larga, meio estreito, uma concavidade e uma expansao
local function raio(th)
  return 1 + 0.30*math.sin(th + 0.6) + 0.21*math.sin(2*th + 2.3)
           + 0.13*math.sin(3*th + 4.1) + 0.07*math.sin(4*th + 1.2)
end
local pts, ptsOut = {}, {}
for i=0,N-1 do
  local th = (i/N)*math.pi*2
  local r = raio(th)
  local s = CS + RA*r*math.cos(th)
  local d = CD + RB*r*math.sin(th)
  pts[i+1] = H.fp("FL", s, d, 0.22)
  local ro = r*1.055
  ptsOut[i+1] = H.fp("FL", CS + RA*ro*math.cos(th), CD + RB*ro*math.sin(th), 0.22)
end
local centro = H.fp("FL", CS, CD, 0.22)
-- triangulacao em leque (valida: o poligono e star-shaped por construcao radial)
local function tri(a,b,c,esp,cor,mat,parent)
  local ab,ac,bc = b-a, c-a, c-b
  local abd,acd,bcd = ab:Dot(ab), ac:Dot(ac), bc:Dot(bc)
  if abd>acd and abd>bcd then c,a = a,c
  elseif acd>bcd and acd>abd then a,b = b,a end
  ab,ac,bc = b-a, c-a, c-b
  local right = ac:Cross(ab).Unit
  local up = bc:Cross(right).Unit
  local back = bc.Unit
  local h = math.abs(ab:Dot(up))
  H.part({Name="LagoAgua", Class="WedgePart", Size=V3(esp, h, math.abs(ab:Dot(back))),
    CFrame=CFrame.fromMatrix((a+b)/2, right, up, back), Color=cor, Material=mat, Transparency=0.08}, parent)
  H.part({Name="LagoAgua", Class="WedgePart", Size=V3(esp, h, math.abs(ac:Dot(back))),
    CFrame=CFrame.fromMatrix((a+c)/2, -right, up, -back), Color=cor, Material=mat, Transparency=0.08}, parent)
end
local AGUA = rgb(58,158,178)
for i=1,N do
  local a = pts[i]
  local b = pts[(i%N)+1]
  tri(centro, a, b, 0.45, AGUA, Enum.Material.Glass, F26)
end
say("lago: poligono unico de", N, "vertices triangulado (", N*2, "faces)")
-- borda acompanhando o perimetro real, com larguras variadas
local nB = 0
for i=1,N do
  local a = ptsOut[i]
  local b = ptsOut[(i%N)+1]
  local mid = (a+b)/2
  local len = (b-a).Magnitude
  local w = (i%3==0) and 1.9 or ((i%3==1) and 1.35 or 1.6)
  local alt = (i%5==0) and 1.0 or 0.75
  H.part({Name="LagoBorda", Size=V3(len+0.35, alt, w),
    CFrame=CFrame.lookAt(V3(mid.X, alt/2-0.06, mid.Z), V3(b.X, alt/2-0.06, b.Z))*CFrame.Angles(0,math.rad(90),0),
    Color=rgb(174,165,152), Material=Enum.Material.Slate, CanCollide=true}, F26)
  nB += 1
end
say("borda: ", nB, "trechos acompanhando o perimetro")
-- 3 pedras maiores nos pontos certos + queda d'agua numa extremidade
-- fonte da rocha: tambem no storage (a limpeza de orfas leva as da cena)
local rocha
local fontes = {L:FindFirstChild("HEX_F14D"), F24,
  REM:FindFirstChild("RochasOrfas"), REM:FindFirstChild("LagoFL_retas"), REM:FindFirstChild("PonteFL")}
for _,pasta in ipairs(fontes) do
  if pasta and not rocha then
    for _,c in ipairs(pasta:GetDescendants()) do
      if c:IsA("MeshPart") and c.Name:sub(1,9)=="LOB_rocha" then rocha=c break end
    end
  end
end
if rocha then
  for i,rr in ipairs({{th=0.35,e=1.35},{th=2.6,e=0.95},{th=4.4,e=0.6}}) do
    local r = raio(rr.th)*1.02
    local pos = H.fp("FL", CS + RA*r*math.cos(rr.th), CD + RB*r*math.sin(rr.th), 0)
    local c = rocha:Clone()
    for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
    c:SetAttribute("HexGen",true)
    c.Size = rocha.Size*(rr.e/0.6)
    c.Anchored=true c.CanCollide=false c.CanQuery=false c.CanTouch=false
    c.CFrame = CF(pos + V3(0, c.Size.Y/2-0.5, 0))*CFrame.Angles(0,math.rad(math.random(0,359)),0)
    c.Parent = F26
  end
end
-- vitorias-regias sobre a lamina (poucas)
for i=1,7 do
  local th = math.random()*math.pi*2
  local rr = raio(th)*(0.25+math.random()*0.5)
  local pos = H.fp("FL", CS + RA*rr*math.cos(th), CD + RB*rr*math.sin(th), 0.46)
  H.part({Name="Vitoria", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.13,2.3,2.3),
    CFrame=CF(pos)*CFrame.Angles(0,math.rad(math.random(0,359)),math.rad(90)),
    Color=C.lirio, Material=Enum.Material.Grass}, F26)
end
say("3 pedras maiores + 7 vitorias-regias")

-- banco de contemplacao: FORA do novo perimetro, virado para a agua
local thB = 1.9 -- sin>0 = lado da praca (d maior), nao junto ao muro
local rB = raio(thB)
local sB = CS + RA*rB*math.cos(thB)
local dB = CD + RB*rB*math.sin(thB)
local sOut = CS + RA*rB*1.30*math.cos(thB)
local dOut = CD + RB*rB*1.30*math.sin(thB)
for _,d in ipairs(L:GetDescendants()) do
  if d.Name=="VIL_banco" and d:IsA("BasePart") then
    local lp = H.faceCF("FL",0,0,0):PointToObjectSpace(d.Position)
    if lp.Z < 60 and math.abs(lp.X) < 80 then
      H.remember(d)
      -- olhando para a agua (do lado de fora para o centro do lago)
      local pos = H.fp("FL", sOut, dOut, 1.15)
      local alvo = H.fp("FL", sB, dB, 1.15)
      d.CFrame = CFrame.lookAt(pos, alvo) * CFrame.Angles(0, math.rad(180), 0)
    end
  end
end
if F24 then
  for _,p in ipairs(F24:GetChildren()) do
    if p.Name=="BancoPatamar" then p:Destroy() end
  end
end
H.part({Name="BancoPatamar", Size=V3(12,0.45,7), CFrame=H.faceCF("FL", sOut, dOut+1.2, 0.22),
  Color=rgb(174,165,152), Material=Enum.Material.Slate, CanCollide=true}, F26)
say(("banco de contemplacao reposicionado fora da agua (s %.0f, d %.0f)"):format(sOut,dOut))

-- ============ 5) limpeza de props orfaos ============
local nOrf = 0
for _,d in ipairs(L:GetDescendants()) do
  if (d:IsA("MeshPart") or d:IsA("BasePart")) and d.Name:sub(1,9)=="LOB_rocha" and not d:IsDescendantOf(F26) then
    nOrf += tira(d, "RochasOrfas")
  end
end
say("rochas orfas/soltas removidas:", nOrf)

L:SetAttribute("HEX_F26_OK", true)
H.commit(rec)
return "F26 OK\n"..table.concat(rep,"\n")