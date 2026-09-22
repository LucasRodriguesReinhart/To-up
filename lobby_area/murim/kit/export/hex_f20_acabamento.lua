-- hex_f20_acabamento.lua : F20 = acabamento artistico dos elementos provisorios do F19.
-- A) MOCHILA V2 (prioridade 1): o jogo NAO tem modelo de mochila reutilizavel (verificado:
--    backups sao uma cabana de ferreiro e uma porta). Familia propria com silhueta real:
--    corpo de topo arredondado, aba com 2 fivelas, bolso frontal com mini-aba, alca superior
--    em arco, alcas de ombro. Substitui TODOS os "Mochila" do F14C, sempre de frente
--    para o cliente. Sem aumentar a quantidade de produtos.
-- B) FORJA: brilho local dos braseiros do terraco reduzido (particula/luz - sem tocar
--    Lighting global); bigorna e barril ASSENTADOS no topo da laje (+0.2, estavam afundados).
-- C) LAGOS: chegada desenhada - lingua de pavimentacao da praca ate o patamar da ponte
--    e contorno fino delimitando a area do lago (linguagem de piso, sem objetos novos).
-- Idempotente: limpa HEX_F20; mochilas velhas destruidas e recriadas pelo F20 (o F14C
--  as recria se re-executado - ordem de fases documentada).
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
H.selfTest()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F19_OK")==true, "F20: rode a F19 antes")
local rec = H.begin("HEX F20 acabamento")
local F20 = H.folder(L,"HEX_F20") H.clear(F20)

-- ============ A) mochila v2 ============
-- frente da mochila = -Z local do cf dado (aba/bolso para -Z)
local OUROF = rgb(212,164,74)
local function mochilaV2(parent, cf, esc, corCorpo, corAba, corCorreia)
  corCorreia = corCorreia or corAba
  local m = Instance.new("Model") m.Name="MochilaV2" m.Parent=parent
  local function P(nome, o)
    o.Name=nome
    o.CFrame = cf * CF(o.at.X*esc, o.at.Y*esc, o.at.Z*esc) * (o.rot or CFrame.identity)
    o.Size = o.Size*esc
    o.at = nil o.rot = nil
    return H.part(o, m)
  end
  -- corpo: caixa + topo cilindrico eliptico (silhueta arredondada)
  P("Corpo",   {Size=V3(2.4,2.6,1.35), at=V3(0,-0.2,0), Color=corCorpo, Material=Enum.Material.Fabric})
  -- cilindros deitados: eixo do cilindro Roblox JA e o X local (esquerda-direita), sem rotacao
  P("Topo",    {Size=V3(2.4,1.5,1.35), at=V3(0,1.1,0), Class="Part", Shape=Enum.PartType.Cylinder,
    Color=corCorpo, Material=Enum.Material.Fabric})
  -- aba de couro MAIS ESTREITA que o corpo (o topo do corpo aparece nas laterais)
  P("AbaTopo", {Size=V3(2.1,1.62,1.42), at=V3(0,1.1,-0.03), Class="Part", Shape=Enum.PartType.Cylinder,
    Color=corAba, Material=Enum.Material.SmoothPlastic})
  P("AbaFrente",{Size=V3(2.1,1.15,0.22), at=V3(0,0.62,-0.78), Color=corAba, Material=Enum.Material.SmoothPlastic})
  P("AbaBorda",{Size=V3(2.1,0.24,0.26), at=V3(0,0.06,-0.78), Class="Part", Shape=Enum.PartType.Cylinder,
    Color=corAba, Material=Enum.Material.SmoothPlastic})
  -- 2 correias verticais com fivelas, PARA FORA da aba (antes ficavam embutidas nela)
  for _,sx in ipairs({-0.62, 0.62}) do
    P("Correia", {Size=V3(0.42,1.35,0.08), at=V3(sx,0.575,-0.93), Color=corCorreia, Material=Enum.Material.SmoothPlastic})
    P("Fivela",  {Size=V3(0.5,0.34,0.12), at=V3(sx,0.02,-0.99), Color=OUROF, Material=Enum.Material.Metal})
  end
  -- bolso frontal com mini-aba
  P("Bolso",   {Size=V3(1.5,1.0,0.5), at=V3(0,-0.95,-0.85), Color=corCorpo, Material=Enum.Material.Fabric})
  P("BolsoAba",{Size=V3(1.56,0.42,0.56), at=V3(0,-0.55,-0.85), Color=corAba, Material=Enum.Material.SmoothPlastic})
  P("BolsoFiv",{Size=V3(0.34,0.22,0.1), at=V3(0,-0.72,-1.13), Color=OUROF, Material=Enum.Material.Metal})
  -- alca superior em arco (3 segmentos)
  P("AlcaTopoA",{Size=V3(0.22,0.5,0.22), at=V3(-0.45,1.95,0.1), rot=CFrame.Angles(0,0,math.rad(-25)), Color=corAba})
  P("AlcaTopoB",{Size=V3(0.7,0.22,0.22), at=V3(0,2.12,0.1), Color=corAba})
  P("AlcaTopoC",{Size=V3(0.22,0.5,0.22), at=V3(0.45,1.95,0.1), rot=CFrame.Angles(0,0,math.rad(25)), Color=corAba})
  -- alcas de ombro (2 segmentos cada, nas costas)
  for _,sx in ipairs({-0.62, 0.62}) do
    P("Ombro1", {Size=V3(0.44,1.5,0.16), at=V3(sx,0.65,0.78), rot=CFrame.Angles(math.rad(-14),0,0), Color=corCorreia, Material=Enum.Material.SmoothPlastic})
    P("Ombro2", {Size=V3(0.44,1.3,0.16), at=V3(sx,-0.65,0.92), rot=CFrame.Angles(math.rad(10),0,0), Color=corCorreia, Material=Enum.Material.SmoothPlastic})
  end
  return m
end

-- substitui as mochilas provisorias do F14C
local F14C = L:FindFirstChild("HEX_F14C")
assert(F14C, "F20: HEX_F14C ausente")
local loja
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="LOJA_interior" then loja=d break end
end
assert(loja, "F20: LOJA_interior nao achada")
local S = loja.CFrame
local chao = loja.Position.Y - loja.Size.Y/2
local nRem = 0
for _,m in ipairs(F14C:GetChildren()) do
  if m.Name=="Mochila" then m:Destroy() nRem += 1 end
end
say("mochilas provisorias removidas:", nRem)
F14C:SetAttribute("F20_SUBSTITUIU_MOCHILAS", true) -- se re-rodar o F14C, re-rodar o F20 depois
-- frente do cliente: prateleiras estao em local X=-8.2 com frente +X; frente da mochila (-Z local
-- do builder) deve apontar para +X da loja -> rot Y de -90 no frame S
local rotCliente = CFrame.Angles(0, math.rad(-90), 0)
local CORES = {
  {rgb(158,104,60), rgb(104,66,40), rgb(84,54,34)},   -- couro
  {rgb(56,128,140), rgb(34,88,98),  rgb(70,48,32)},   -- teal
  {rgb(192,58,48),  rgb(126,38,36), rgb(70,48,32)},   -- vermelho
}
-- prateleiras ACIMA da linha do balcao (tampo em chao+2.95 escondia a fileira de baixo
-- da posicao do cliente - defeito visto em captura): baixa sobe p/ chao+3.4, alta p/ chao+6.0
local prats = {}
for _,p in ipairs(F14C:GetChildren()) do
  if p.Name=="Prateleira" and p:IsA("BasePart") then table.insert(prats, p) end
end
table.sort(prats, function(a,b) return a.Position.Y < b.Position.Y end)
assert(#prats==2, "F20: esperava 2 prateleiras, achei "..#prats)
local ALVOS_Y = {chao+3.4, chao+6.0}
local velhosY = {prats[1].Position.Y, prats[2].Position.Y}
for i,p in ipairs(prats) do
  if p:GetAttribute("F20_Reposicionada")~=true then
    p.CFrame = p.CFrame + V3(0, ALVOS_Y[i]-p.Position.Y, 0)
    p:SetAttribute("F20_Reposicionada", true)
  end
end
-- frisos do F19 acompanham a prateleira mais proxima (senao flutuam na altura antiga)
local F19f = L:FindFirstChild("HEX_F19")
if F19f then
  for _,fr in ipairs(F19f:GetChildren()) do
    if fr.Name=="PrateleiraFriso" and fr:IsA("BasePart") and fr:GetAttribute("F20_Reposicionada")~=true then
      local i = (math.abs(fr.Position.Y - velhosY[1]) < math.abs(fr.Position.Y - velhosY[2])) and 1 or 2
      fr.CFrame = fr.CFrame + V3(0, ALVOS_Y[i]-velhosY[i], 0)
      fr:SetAttribute("F20_Reposicionada", true)
    end
  end
end
for _,p in ipairs(F14C:GetChildren()) do
  if p.Name=="ExpositorFundo" and p:IsA("BasePart") and p:GetAttribute("F20_Reposicionada")~=true then
    p.Size = V3(p.Size.X, 7.6, p.Size.Z)
    p.CFrame = CF(p.Position.X, chao+4.0, p.Position.Z) * (p.CFrame - p.CFrame.Position)
    p:SetAttribute("F20_Reposicionada", true)
  end
end
say("prateleiras subidas acima da linha do balcao")
-- esc 0.62: altura total ~2.33 cabe no vao (painel refutou 0.78);
-- base = topo REAL de cada prateleira + 1.5*esc (offset fixo flutuava as 5)
local expX = -8.2
local ESC = 0.62
local ALT = 1.5*ESC + 0.02
local topoB = prats[1].Position.Y + prats[1].Size.Y/2
local topoA = prats[2].Position.Y + prats[2].Size.Y/2
for i=1,3 do
  local z = (i-2)*3.8
  mochilaV2(F20, S*CF(expX+0.2, (topoB+ALT)-S.Position.Y, z)*rotCliente, ESC, CORES[i][1], CORES[i][2], CORES[i][3])
end
-- dourada na prateleira alta (produto premium)
mochilaV2(F20, S*CF(expX+0.2, (topoA+ALT)-S.Position.Y, -1.9)*rotCliente, ESC, rgb(214,170,84), rgb(150,108,50), rgb(104,74,38))
-- amostra sobre o balcao, de frente para quem entra
mochilaV2(F20, S*CF(5.5, (chao+2.945+ALT)-S.Position.Y, 3)*rotCliente, ESC, rgb(56,128,140), rgb(34,88,98), rgb(70,48,32))
say("5 mochilas v2 expostas de frente para o cliente")
-- placa da fachada: troca o simbolo tambem
local nPl = 0
for _,m in ipairs(F14C:GetChildren()) do
  if m.Name=="PlacaFundo" and m:IsA("BasePart") then
    -- acha e remove a mochila-simbolo antiga (modelo "Mochila" ja destruido acima); cria v2 dourada
    -- frente da placa = -Z do proprio CFrame dela; recuada (o simbolo avancado invadia o pad)
    mochilaV2(F20, m.CFrame*CF(0,-0.27,-0.9), 1.1, rgb(214,170,84), rgb(150,108,50), rgb(104,74,38))
    nPl += 1
  end
end
say("placa: simbolo v2 dourado:", nPl)

-- ============ B) forja ============
-- braseiros do terraco: brilho local reduzido (eram o "recipiente luminoso" dominando o quadro)
local nBra = 0
for _,d in ipairs(L:GetDescendants()) do
  -- escopo: so os braseiros da REGIAO da forja (z<-60), nunca o lobby inteiro
  if d:IsA("BasePart") and d.Name:lower():find("brase") and d.Position.Z < -60 then
    local mudou = false
    local pe = d:FindFirstChildOfClass("ParticleEmitter")
    if pe then
      pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,1.0), NumberSequenceKeypoint.new(1,0.2)})
      pe.Rate = 9 mudou = true
    end
    local pl = d:FindFirstChildOfClass("PointLight")
    if pl then pl.Brightness = 0.6 pl.Range = 9 mudou = true end
    if mudou then nBra += 1 end
  end
end
say("braseiros da forja com brilho local reduzido:", nBra)
-- bigorna e barril assentados NO TOPO da laje (estavam 0.19 afundados)
local FE = L:FindFirstChild("HEX_F14E")
local nAss = 0
if FE then
  for _,p in ipairs(FE:GetChildren()) do
    if (p.Name:sub(1,7)=="Bigorna" or p.Name:sub(1,6)=="Barril") and p:IsA("BasePart") then
      if p:GetAttribute("F20_Assentado")~=true then
        p.CFrame = p.CFrame + V3(0,0.19,0)
        p:SetAttribute("F20_Assentado", true)
        nAss += 1
      end
    end
  end
  local nCol = 0
  for _,c in ipairs(H.COL:GetChildren()) do
    if (c.Name:sub(1,15)=="hx_f14e_bigorna" or c.Name:sub(1,14)=="hx_f14e_barril") and c:GetAttribute("F20_Assentado")~=true then
      c.CFrame = c.CFrame + V3(0,0.19,0)
      c:SetAttribute("F20_Assentado", true)
      nCol += 1
    end
  end
  say("colliders assentados:", nCol)
end
say("equipamentos assentados na laje:", nAss)

-- ============ C) lagos: chegada e contorno ============
local PAV_CHEGADA = rgb(150,136,120)
local nCheg = 0
for _,P in pairs(H.LAY.PONDS) do
  -- lingua de chegada: do patamar interno (d2+2.2) em direcao a praca, afinando
  local d0 = P.d2 + 4.0
  for k,w in ipairs({8.4, 6.6, 4.8}) do
    H.part({Name="Chegada", Size=V3(w, 0.12, 4.6), CFrame=H.faceCF(P.face, P.bridgeS, d0 + (k-1)*4.6 + 2.3, 0.06),
      Color=PAV_CHEGADA, Material=Enum.Material.Pavement}, F20)
  end
  -- contorno fino delimitando a area do lago (junta escura, so 3 lados - o lado da muralha nao precisa)
  local s1, s2, dIn, dOut = P.s1-2.6, P.s2+2.6, P.d1-2.6, P.d2+2.6
  local function tira(sA, sB, dd)
    if sB-sA < 2 then return end
    H.part({Name="Contorno", Size=V3(sB-sA, 0.1, 0.55), CFrame=H.faceCF(P.face,(sA+sB)/2, dd, 0.06),
      Color=C.junta, Material=Enum.Material.SmoothPlastic}, F20)
  end
  local g1, g2 = P.bridgeS-5.4, P.bridgeS+5.4
  tira(s1, g1, dOut) tira(g2, s2, dOut)
  for _,ss in ipairs({s1, s2}) do
    H.part({Name="Contorno", Size=V3(dOut-dIn, 0.1, 0.55), CFrame=H.faceCF(P.face, ss, (dIn+dOut)/2, 0.06)*CFrame.Angles(0,math.rad(90),0),
      Color=C.junta, Material=Enum.Material.SmoothPlastic}, F20)
  end
  nCheg += 1
end
say("lagos com chegada e contorno:", nCheg)

L:SetAttribute("HEX_F20_OK", true)
H.commit(rec)
return "F20 OK\n"..table.concat(rep,"\n")