-- hex_f21_composicao.lua : F21 = revisao de COMPOSICAO (loja como exposicao; ponte integrada).
-- LOJA (funcoes preservadas; pad intocado):
--  1) balcao sai da frente da entrada -> deslocado para o lado (local Z+6.8, correndo ao longo
--     de X; o vao de ~5.5 atras dele e o corredor do lojista), collider junto; vista livre;
--  2) lanterna: 5.84 de altura num interior de 10.6 dominava o quadro -> escala 0.58 e
--     reposicionada sobre o balcao (fora do eixo entrada->produtos); corrente refeita;
--  3) 2 ILHAS DE EXPOSICAO no meio da loja (mesa de madeira com saia teal) recebem a mochila
--     vermelha e a teal, de frente para a entrada - produtos viram protagonistas;
--  4) prateleira do fundo fica com a de couro (centralizada) + dourada no alto;
--     a amostra do balcao acompanha o balcao novo.
-- PONTE (FL e FR):
--  5) TERRACO DE MARGEM: banda Slate quente ao longo do lado da praca do lago
--     (s1-6..s2+6, d2+0.7..d2+6.2) - a margem vira um lugar; banco assenta NELE (+0.21, CF0);
--  6) lingua de chegada recuada para comecar na borda do terraco (sem sobreposicao).
-- Idempotente: limpa HEX_F21; movimentos com atributo F21_Movido; H.remember antes de mover.
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
H.selfTest()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F20_OK")==true, "F21: rode a F20 antes")
local rec = H.begin("HEX F21 composicao")
local F21 = H.folder(L,"HEX_F21") H.clear(F21)
H.clearColliders("hx_f21_")

local loja
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="LOJA_interior" then loja=d break end
end
assert(loja, "F21: LOJA_interior nao achada")
local S = loja.CFrame
local chao = loja.Position.Y - loja.Size.Y/2
local F14C = L.HEX_F14C
local F19f = L:FindFirstChild("HEX_F19")
local F20f = L:FindFirstChild("HEX_F20")
local rot90 = CFrame.Angles(0, math.rad(90), 0)

-- ============ 1) balcao para a lateral ============
local nBal = 0
for _,p in ipairs(F14C:GetChildren()) do
  if p.Name:sub(1,6)=="Balcao" and p:IsA("BasePart") and p:GetAttribute("F21_Movido")~=true then
    H.remember(p)
    local dy = p.Position.Y - loja.Position.Y
    p.CFrame = S * CF(0.5, dy, 6.8) * rot90
    p:SetAttribute("F21_Movido", true)
    nBal += 1
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name=="hx_f14c_balcao" and c:GetAttribute("F21_Movido")~=true then
    H.remember(c)
    local dy = c.Position.Y - loja.Position.Y
    c.CFrame = S * CF(0.5, dy, 6.8) * rot90
    c:SetAttribute("F21_Movido", true)
  end
end
say("balcao movido para a lateral:", nBal, "pecas")

-- ============ 2) lanterna em escala e fora do eixo ============
if F19f then
  local lant = F19f:FindFirstChild("KIT_lanterna_palacio")
  local corr = F19f:FindFirstChild("LanternaCorrente")
  if lant and lant:GetAttribute("F21_Movido")~=true then
    H.remember(lant)
    lant.Size = lant.Size * 0.58
    local teto = loja.Position.Y + loja.Size.Y/2
    local cy = teto - 1.2 - lant.Size.Y/2
    lant.CFrame = S * CF(0.5, cy - loja.Position.Y, 6.8)
    lant:SetAttribute("F21_Movido", true)
    if corr then
      local topoLant = cy + lant.Size.Y/2
      if teto - topoLant > 0.15 then
        corr.Size = V3(0.2, teto-topoLant, 0.2)
        corr.CFrame = S * CF(0.5, ((topoLant+teto)/2) - loja.Position.Y, 6.8)
      else
        corr.Transparency = 1
      end
    end
    say("lanterna: escala 0.58, sobre o balcao")
  end
end

-- ============ 3) ilhas de exposicao ============
local MAD = rgb(96,64,44)
local function mesa(lx, lz)
  local base = chao
  H.part({Name="MesaPe", Size=V3(1.2,1.15,1.2), CFrame=S*CF(lx,(base+0.58)-loja.Position.Y,lz),
    Color=MAD, Material=Enum.Material.Wood, CanCollide=true}, F21)
  H.part({Name="MesaSaia", Size=V3(2.0,0.3,2.0), CFrame=S*CF(lx,(base+1.3)-loja.Position.Y,lz),
    Color=C.teal, Material=Enum.Material.SmoothPlastic}, F21)
  H.part({Name="MesaTampo", Size=V3(2.3,0.22,2.3), CFrame=S*CF(lx,(base+1.56)-loja.Position.Y,lz),
    Color=rgb(118,80,54), Material=Enum.Material.Wood}, F21)
  H.collider("hx_f21_mesa", V3(2.4,1.67,2.4), S*CF(lx,(base+0.835)-loja.Position.Y,lz))
  return base + 1.67
end
local topoMesaA = mesa(2.2, -2.8)
local topoMesaB = mesa(-1.8, 2.8)
say("2 ilhas de exposicao no eixo entrada->fundo")

-- ============ 4) reposicionar mochilas ============
-- identifica as MochilaV2 por altura/posicao (medidas do F20)
local rotCliente = CFrame.Angles(0, math.rad(-90), 0)
-- offset pivo->base MEDIDO por modelo (GetPivot = centro do bbox, nao a origem do builder;
-- constante fixa afundava 0.22 - achado do painel)
local function altDe(m)
  local cf, sz = m:GetBoundingBox()
  return (m:GetPivot().Position.Y - (cf.Position.Y - sz.Y/2)) + 0.02
end
local baixas, dourada, amostra = {}, nil, nil
if F20f then
  for _,m in ipairs(F20f:GetChildren()) do
    if m.Name=="MochilaV2" and m:GetAttribute("F21_Movido")~=true then
      local p = m:GetPivot().Position
      local lp = S:PointToObjectSpace(p)
      if lp.X > 12 then -- simbolo da placa: nao mexe
      elseif lp.X > 0 then amostra = m
      elseif p.Y > 14 then dourada = m
      else table.insert(baixas, m) end
    end
  end
end
table.sort(baixas, function(a,b) return a:GetPivot().Position.Z < b:GetPivot().Position.Z end)
local nMov = 0
local function poe(m, lx, topoApoio, lz, comRot)
  if not m then return end
  H.remember(m)
  local cfAlvo = S*CF(lx, (topoApoio+altDe(m))-loja.Position.Y, lz)
  if comRot then cfAlvo = cfAlvo*rotCliente end
  m:PivotTo(cfAlvo)
  m:SetAttribute("F21_Movido", true)
  nMov += 1
end
-- sort por world Z da [couro, teal, vermelho]; ilhas recebem VERMELHA e TEAL (painel pegou a troca)
if #baixas >= 3 then
  poe(baixas[3], 2.2, topoMesaA, -2.8, true)   -- vermelha na mesa A
  poe(baixas[2], -1.8, topoMesaB, 2.8, true)   -- teal na mesa B
  poe(baixas[1], -8.0, chao+3.55, 0, true)     -- couro centralizada na prateleira baixa
end
-- amostra acompanha o balcao novo (frente para o interior = -Z local)
poe(amostra, 3.2, chao+2.945, 6.3, false)
say("mochilas reposicionadas:", nMov, "(ilhas/prateleira/balcao)")

-- ============ 5/6) terraco de margem + lingua recuada ============
local nTer = 0
for _,P in pairs(H.LAY.PONDS) do
  local s1, s2 = P.s1-6, P.s2+6
  local dA, dB = P.d2+0.75, P.d2+6.2
  H.part({Name="Terraco", Size=V3(s2-s1, 0.16, dB-dA), CFrame=H.faceCF(P.face,(s1+s2)/2,(dA+dB)/2, 0.1),
    Color=rgb(176,166,152), Material=Enum.Material.Slate, CanCollide=true}, F21)
  -- borda do terraco no lado da praca, com VAO na largura da lingua (painel: cruzava a Chegada)
  local gA, gB = P.bridgeS-4.4, P.bridgeS+4.4
  for _,seg in ipairs({{s1, gA}, {gB, s2}}) do
    if seg[2]-seg[1] > 1 then
      H.part({Name="TerracoBorda", Size=V3(seg[2]-seg[1], 0.1, 0.5), CFrame=H.faceCF(P.face,(seg[1]+seg[2])/2, dB+0.2, 0.08),
        Color=C.junta, Material=Enum.Material.SmoothPlastic}, F21)
    end
  end
  -- banco do lago assenta no terraco
  for _,d in ipairs(L:GetDescendants()) do
    if d.Name=="VIL_banco" and d:IsA("BasePart") and d:GetAttribute("F21_Movido")~=true then
      local lp = H.faceCF(P.face, 0, 0, 0):PointToObjectSpace(d.Position)
      -- coords de face: X=s, Z=d (aprox; usar distancia ao centro do lago)
      local sB, dBanco = lp.X, lp.Z
      if math.abs(sB) < 90 and dBanco > P.d2-2 and dBanco < P.d2+10 then
        H.remember(d)
        d.CFrame = d.CFrame + V3(0, 0.21, 0)
        d:SetAttribute("F21_Movido", true)
      end
    end
  end
  nTer += 1
end
-- lingua recuada: empurrao PURO em d pelo inward da face de cada lago (o vetor ao origin
-- desviava 8 graus no FR e deslizava a lingua do eixo da ponte - achado do painel)
if F20f then
  for _,P in pairs(H.LAY.PONDS) do
    local F = H.FACES[P.face]
    local ref = H.faceCF(P.face, 0, 0, 0)
    for _,p in ipairs(F20f:GetChildren()) do
      if p.Name=="Chegada" and p:GetAttribute("F21_Movido")~=true then
        local lp = ref:PointToObjectSpace(p.Position)
        if math.abs(lp.X - P.bridgeS) < 6 and lp.Z > P.d2 then
          H.remember(p)
          p.CFrame = p.CFrame + F.inw*2.6
          p:SetAttribute("F21_Movido", true)
        end
      end
    end
  end
end
say("terracos de margem:", nTer, "(bancos assentados, lingua recuada)")

L:SetAttribute("HEX_F21_OK", true)
H.commit(rec)
return "F21 OK\n"..table.concat(rep,"\n")