-- hex_f19_areas.lua : F19 = forja, loja e lagos - as 3 diferencas de maior impacto por area,
-- comparadas com as referencias do briefing (nao com o ciclo anterior). Sem ornamentacao nova
-- alem do especificado; monumento INTOCADO (F18 preservado).
-- FORJA: (1) zona de trabalho unificada - laje de lareira escura sob Ignis+bigorna+barril
--        (hoje flutuam como pecas isoladas no piso de azulejo);
--        (2) estante de ferramentas de parede (1 painel, 2 martelos + 1 tenaz, poucos e legiveis);
--        (3) nada mais - fornalha/equilibrio de brilho ficam para a revisao do conjunto.
-- LOJA:  (1) tapete interno definindo o espaco de venda (entrada -> balcao);
--        (2) lanterna pendurada no interior com luz quente (interior hoje e escuro);
--        (3) friso de madeira nas prateleiras (arremate, nao decoracao nova).
-- LAGOS: (1) patamares de pedra nas bocas das pontes (encontro ponte-caminho resolvido);
--        (2) rochas encostadas nos cantos da borda (hoje soltas no piso);
--        (3) nada mais - passagens continuam abertas.
-- Idempotente: limpa HEX_F19; rochas reposicionadas guardam CF0 via H.remember.
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

assert(L:GetAttribute("HEX_F18_OK")==true, "F19: rode a F18 antes")
local rec = H.begin("HEX F19 areas")
local F19 = H.folder(L,"HEX_F19") H.clear(F19)
H.clearColliders("hx_f19_")

-- ============ FORJA ============
local PISO = 10.0
local FERRO = rgb(60,62,68)
local MADEIRA = rgb(96,64,44)
-- (1) laje de lareira FINA cobrindo Ignis (frente ate -105) e morrendo DENTRO da base da
-- fornalha (tras -123.5 < -124, sem face coplanar); borda bronze declarada como arremate.
-- Pisavel: CanCollide na propria laje (degrau 0.19 e sub-step, nao trava avatar).
H.part({Name="Lareira", Size=V3(26,0.18,18.5), CFrame=CF(0,PISO+0.10,-114.25),
  Color=rgb(66,60,56), Material=Enum.Material.Slate, CanCollide=true}, F19)
H.part({Name="LareiraBorda", Size=V3(27,0.10,19), CFrame=CF(0,PISO+0.05,-114),
  Color=rgb(150,104,48), Material=Enum.Material.Metal}, F19)
say("forja: laje de lareira unificando a zona de trabalho")
-- (2) estante de ferramentas DE PE PROPRIO na beira da zona (a "parede" do salao e colunata
-- com janelas - nao recebe movel). Pes ate o piso matam o flutuo; frente para a zona (+X).
local est = CF(-14.4,0,-118)*CFrame.Angles(0,math.rad(-90),0)
H.part({Name="EstanteFundo", Size=V3(6.4,4.6,0.4), CFrame=est*CF(0,PISO+3.4,0), Color=rgb(74,52,38), Material=Enum.Material.Wood}, F19)
H.part({Name="EstanteMoldura", Size=V3(6.8,0.4,0.5), CFrame=est*CF(0,PISO+5.6,0), Color=C.teal}, F19)
H.part({Name="EstanteMoldura", Size=V3(6.8,0.4,0.5), CFrame=est*CF(0,PISO+1.2,0), Color=C.teal}, F19)
for _,sg in ipairs({1,-1}) do
  H.part({Name="EstantePe", Size=V3(0.45,1.2,0.45), CFrame=est*CF(sg*2.9,PISO+0.6,0), Color=rgb(74,52,38), Material=Enum.Material.Wood}, F19)
end
local function martelo(ocf)
  H.part({Name="MarteloCabo", Size=V3(0.35,2.6,0.35), CFrame=est*ocf, Color=MADEIRA, Material=Enum.Material.Wood}, F19)
  H.part({Name="MarteloCabeca", Size=V3(1.5,0.8,0.8), CFrame=est*ocf*CF(0,1.35,0), Color=FERRO, Material=Enum.Material.Metal}, F19)
end
martelo(CF(-1.9,PISO+3.1,-0.35))
martelo(CF(0,PISO+3.3,-0.35)*CFrame.Angles(0,0,math.rad(8)))
-- tenaz: 2 hastes em V
for _,sg in ipairs({1,-1}) do
  H.part({Name="Tenaz", Size=V3(0.25,2.8,0.25), CFrame=est*CF(1.9+sg*0.18,PISO+3.2,-0.35)*CFrame.Angles(0,0,math.rad(sg*7)), Color=FERRO, Material=Enum.Material.Metal}, F19)
end
H.collider("hx_f19_estante", V3(0.9,6,6.9), CF(-14.4,PISO+3,-118))
say("forja: estante na parede com 2 martelos e 1 tenaz")

-- ============ LOJA ============
local loja
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="LOJA_interior" then loja=d break end
end
assert(loja, "F19: LOJA_interior nao achada")
local S = loja.CFrame
local chao = loja.Position.Y - loja.Size.Y/2
-- (1) tapete no LADO DO CLIENTE, da entrada (X~10) ate a face do balcao (X 5.5+~0.4)
H.part({Name="LojaTapete", Size=V3(4.2,0.06,6.5), CFrame=S*CF(7.9,(chao+0.05)-S.Position.Y,0),
  Color=rgb(178,44,40), Material=Enum.Material.Fabric}, F19)
H.part({Name="LojaTapeteBorda", Size=V3(4.6,0.05,0.5), CFrame=S*CF(7.9,(chao+0.07)-S.Position.Y,3.4), Color=rgb(240,196,90)}, F19)
H.part({Name="LojaTapeteBorda", Size=V3(4.6,0.05,0.5), CFrame=S*CF(7.9,(chao+0.07)-S.Position.Y,-3.4), Color=rgb(240,196,90)}, F19)
-- (2) lanterna pendurada com luz quente
local lib = SS:FindFirstChild("BIBLIOTECA_MURIM")
local lant = lib and lib:FindFirstChild("KIT") and lib.KIT:FindFirstChild("KIT_lanterna_palacio")
if lant and lant:IsA("BasePart") then
  local c = lant:Clone()
  for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
  c:SetAttribute("HexGen",true)
  c.Anchored=true c.CanCollide=false c.CanQuery=false c.CanTouch=false
  c.CFrame = S*CF(0,(chao+8.2)-S.Position.Y,0)
  c.Parent = F19
  local pl = Instance.new("PointLight")
  pl.Range=16 pl.Brightness=0.9 pl.Color=rgb(255,196,130) pl.Shadows=false pl.Parent=c
  -- corrente derivada do tamanho REAL da lanterna ate o teto do interior
  local topoLant = (chao+8.2) + c.Size.Y/2
  local teto = loja.Position.Y + loja.Size.Y/2
  if teto - topoLant > 0.2 then
    H.part({Name="LanternaCorrente", Size=V3(0.2, teto-topoLant, 0.2),
      CFrame=S*CF(0, ((topoLant+teto)/2)-S.Position.Y, 0), Color=rgb(70,60,50), Material=Enum.Material.Metal}, F19)
  end
  say("loja: tapete interno + lanterna pendurada acesa")
else
  say("loja: tapete interno (lanterna do kit nao achada)")
end
-- (3) friso de arremate nas prateleiras existentes (HEX_F14C)
local F14C = L:FindFirstChild("HEX_F14C")
local nFriso = 0
if F14C then
  for _,p in ipairs(F14C:GetChildren()) do
    if p.Name=="Prateleira" and p:IsA("BasePart") then
      -- friso ao longo do EIXO LONGO (Z local, 11 studs), na borda frontal (+X local = frente da loja)
      H.part({Name="PrateleiraFriso", Size=V3(0.3,0.18,p.Size.Z+0.15),
        CFrame=p.CFrame*CF(p.Size.X/2-0.15, p.Size.Y/2+0.09, 0),
        Color=rgb(240,196,90), Material=Enum.Material.SmoothPlastic}, F19)
      nFriso += 1
    end
  end
end
say("loja: frisos de prateleira:", nFriso)

-- ============ LAGOS ============
-- (1) patamares de pedra nas bocas das pontes
local nPat = 0
for _,P in pairs(H.LAY.PONDS) do
  for _,dd in ipairs({P.d1-2.2, P.d2+2.2}) do
    -- 9.2 de largura: folga de 0.05 para as faces dos pilaretes das bocas (em s = bridgeS±5.6,
    -- face interna ±4.65). Pisavel: CanCollide (0.28 e sub-step).
    H.part({Name="PatamarPonte", Size=V3(9.2,0.28,3.6), CFrame=H.faceCF(P.face, P.bridgeS, dd, 0.14),
      Color=rgb(176,166,152), Material=Enum.Material.Slate, CanCollide=true}, F19)
    -- filete morre DENTRO do patamar (deslocamento 1.55 < meia-profundidade 1.8), baixo (y 0.13)
    H.part({Name="PatamarFilete", Size=V3(9.6,0.14,0.5), CFrame=H.faceCF(P.face, P.bridgeS, dd + (dd<P.d1 and -1.55 or 1.55), 0.13),
      Color=rgb(150,140,126), Material=Enum.Material.Slate}, F19)
    nPat += 1
  end
end
say("lagos: patamares nas bocas das pontes:", nPat)
-- (2) rochas encostadas nos CANTOS da borda: alvos calculados da planta (só os 4 cantos
-- de cada lago, nunca as bocas da ponte), distancia proporcional ao raio da rocha
local F14D = L:FindFirstChild("HEX_F14D")
local nRocha = 0
if F14D then
  local cantos = {}
  for _,P in pairs(H.LAY.PONDS) do
    for _,ss in ipairs({P.s1-0.7, P.s2+0.7}) do
      for _,dd in ipairs({P.d1-0.7, P.d2+0.7}) do
        table.insert(cantos, H.fp(P.face, ss, dd, 0))
      end
    end
  end
  for _,r in ipairs(F14D:GetChildren()) do
    if r:IsA("MeshPart") and r.Name:sub(1,9)=="LOB_rocha" then
      H.remember(r)
      local melhor, md = nil, math.huge
      for _,pp in ipairs(cantos) do
        local d = (V3(pp.X,0,pp.Z)-V3(r.Position.X,0,r.Position.Z)).Magnitude
        if d < md then md, melhor = d, pp end
      end
      local raio = math.max(r.Size.X, r.Size.Z)/2
      local alvo = raio + 1.4 -- encosta no pilarete (meia-largura 0.95) sem engoli-lo
      if melhor and md > alvo + 0.2 then
        local dir = (V3(melhor.X,0,melhor.Z)-V3(r.Position.X,0,r.Position.Z)).Unit
        local novo = r.Position + dir*(md-alvo) - V3(0,0.35,0)
        r.CFrame = (r.CFrame - r.CFrame.Position) + novo
        nRocha += 1
      end
    end
  end
end
say("lagos: rochas encostadas nos cantos:", nRocha)

L:SetAttribute("HEX_F19_OK", true)
H.commit(rec)
return "F19 OK\n"..table.concat(rep,"\n")