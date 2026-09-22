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
-- (1) laje de lareira: unifica Ignis (0,-108), bigorna (8.5,-114), barril (-8.5,-114), fornalha (0,-122)
H.part({Name="Lareira", Size=V3(26,0.35,17), CFrame=CF(0,PISO+0.18,-115.5),
  Color=rgb(66,60,56), Material=Enum.Material.Slate}, F19)
H.part({Name="LareiraBorda", Size=V3(27,0.22,18), CFrame=CF(0,PISO+0.08,-115.5),
  Color=rgb(150,104,48), Material=Enum.Material.Metal}, F19)
say("forja: laje de lareira unificando a zona de trabalho")
-- (2) estante de ferramentas na lateral esquerda da zona
local est = CF(-14.5,0,-118)*CFrame.Angles(0,math.rad(90),0) -- de frente para a zona
H.part({Name="EstanteFundo", Size=V3(6.4,4.6,0.4), CFrame=est*CF(0,PISO+3.4,0), Color=rgb(74,52,38), Material=Enum.Material.Wood}, F19)
H.part({Name="EstanteMoldura", Size=V3(6.8,0.4,0.5), CFrame=est*CF(0,PISO+5.6,0), Color=C.teal}, F19)
H.part({Name="EstanteMoldura", Size=V3(6.8,0.4,0.5), CFrame=est*CF(0,PISO+1.2,0), Color=C.teal}, F19)
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
H.collider("hx_f19_estante", V3(0.9,6,6.9), CF(-14.5,PISO+3,-118))
say("forja: estante com 2 martelos e 1 tenaz")

-- ============ LOJA ============
local loja
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="LOJA_interior" then loja=d break end
end
assert(loja, "F19: LOJA_interior nao achada")
local S = loja.CFrame
local chao = loja.Position.Y - loja.Size.Y/2
-- (1) tapete interno da entrada ao balcao
H.part({Name="LojaTapete", Size=V3(11,0.06,6.5), CFrame=S*CF(1.5,(chao+0.08)-S.Position.Y,0),
  Color=rgb(178,44,40), Material=Enum.Material.Fabric}, F19)
H.part({Name="LojaTapeteBorda", Size=V3(11.4,0.05,0.5), CFrame=S*CF(1.5,(chao+0.1)-S.Position.Y,3.4), Color=rgb(240,196,90)}, F19)
H.part({Name="LojaTapeteBorda", Size=V3(11.4,0.05,0.5), CFrame=S*CF(1.5,(chao+0.1)-S.Position.Y,-3.4), Color=rgb(240,196,90)}, F19)
-- (2) lanterna pendurada com luz quente
local lib = SS:FindFirstChild("BIBLIOTECA_MURIM")
local lant = lib and lib:FindFirstChild("KIT") and lib.KIT:FindFirstChild("KIT_lanterna_palacio")
if lant then
  local c = lant:Clone()
  for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
  c:SetAttribute("HexGen",true)
  c.Anchored=true c.CanCollide=false c.CanQuery=false c.CanTouch=false
  c.CFrame = S*CF(0,(chao+8.2)-S.Position.Y,0)
  c.Parent = F19
  local pl = Instance.new("PointLight")
  pl.Range=16 pl.Brightness=0.9 pl.Color=rgb(255,196,130) pl.Shadows=false pl.Parent=c
  H.part({Name="LanternaCorrente", Size=V3(0.2,1.6,0.2), CFrame=S*CF(0,(chao+10)-S.Position.Y,0), Color=rgb(70,60,50), Material=Enum.Material.Metal}, F19)
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
      H.part({Name="PrateleiraFriso", Size=V3(p.Size.X+0.15,0.18,0.3),
        CFrame=p.CFrame*CF(0,p.Size.Y/2+0.09,p.Size.Z/2-0.15),
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
    H.part({Name="PatamarPonte", Size=V3(10.5,0.28,3.6), CFrame=H.faceCF(P.face, P.bridgeS, dd, 0.14),
      Color=rgb(176,166,152), Material=Enum.Material.Slate}, F19)
    H.part({Name="PatamarFilete", Size=V3(10.9,0.14,0.5), CFrame=H.faceCF(P.face, P.bridgeS, dd + (dd<P.d1 and -1.8 or 1.8), 0.2),
      Color=rgb(150,140,126), Material=Enum.Material.Slate}, F19)
    nPat += 1
  end
end
say("lagos: patamares nas bocas das pontes:", nPat)
-- (2) rochas encostadas nos cantos da borda (hoje soltas): puxa cada rocha do F14D
-- para o pilarete de canto mais proximo, com leve afundamento
local F14D = L:FindFirstChild("HEX_F14D")
local nRocha = 0
if F14D then
  local pilaretes = {}
  for _,p in ipairs(F14D:GetChildren()) do
    if p.Name=="Pilarete" and p:IsA("BasePart") then table.insert(pilaretes, p.Position) end
  end
  for _,r in ipairs(F14D:GetChildren()) do
    if r:IsA("MeshPart") and r.Name:sub(1,9)=="LOB_rocha" then
      H.remember(r)
      local melhor, md = nil, math.huge
      for _,pp in ipairs(pilaretes) do
        local d = (V3(pp.X,0,pp.Z)-V3(r.Position.X,0,r.Position.Z)).Magnitude
        if d < md then md, melhor = d, pp end
      end
      if melhor and md > 2.2 then
        local dir = (V3(melhor.X,0,melhor.Z)-V3(r.Position.X,0,r.Position.Z)).Unit
        local novo = r.Position + dir*(md-2.0) - V3(0,0.35,0)
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