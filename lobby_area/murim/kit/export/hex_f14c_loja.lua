-- hex_f14c_loja.lua : F14c = a loja de mochilas precisa parecer uma loja de mochilas (briefing secao 5).
-- Placa de madeira com MOCHILA estilizada na fachada, balcao com tampo laqueado e
-- expositor de 2 prateleiras com 3 mochilas de cores diferentes. Pad de interacao intocado.
-- Idempotente: limpa HEX_F14C e colliders hx_f14c_.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F14B_OK")==true, "F14c: rode a F14b antes")
local rec = H.begin("HEX F14c loja")
local FC = H.folder(L,"HEX_F14C") H.clear(FC)
H.clearColliders("hx_f14c_")

local loja
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="LOJA_interior" then loja=d break end
end
assert(loja, "F14c: LOJA_interior nao achada")
local S = loja.CFrame -- local +X = fachada (em direcao ao pad)
local chao = loja.Position.Y - loja.Size.Y/2 -- ~7.98
local COURO = rgb(146,95,58)
local COURO_ESCURO = rgb(112,70,42)

-- mochila estilizada: corpo, aba, bolso, alcas; frente = -X local do cframe dado
local function mochila(cf, esc, corCorpo, corAba)
  local m = Instance.new("Model") m.Name="Mochila" m.Parent=FC
  local function P(nome, sz, ocf, cor, mat)
    return H.part({Name=nome, Size=sz*esc, CFrame=cf*CFrame.new(ocf.Position*esc)*(ocf-ocf.Position),
      Color=cor, Material=mat or Enum.Material.SmoothPlastic}, m)
  end
  P("Corpo", V3(2.6,3.2,1.4), CF(0,0,0), corCorpo)
  P("Aba", V3(2.7,1.3,1.5), CF(0,1.15,0.03)*CFrame.Angles(math.rad(-8),0,0), corAba)
  P("Fecho", V3(0.5,0.5,0.2), CF(0,0.65,-0.78), rgb(240,196,90), Enum.Material.Metal)
  P("Bolso", V3(1.6,1.1,0.5), CF(0,-0.85,-0.85), corAba)
  P("AlcaE", V3(0.45,2.6,0.25), CF(-0.7,-0.1,0.78), COURO_ESCURO)
  P("AlcaD", V3(0.45,2.6,0.25), CF(0.7,-0.1,0.78), COURO_ESCURO)
  return m
end

-- ============ 1) placa da fachada com mochila ============
-- pendurada no portico real, sobre a porta (pad em local X ~ +18); frente olha a praca
local placaCF = S * CF(15.6, 1.6, 0) * CFrame.Angles(0, math.rad(-90), 0)
H.part({Name="PlacaFundo", Size=V3(7.5,4.6,0.5), CFrame=placaCF, Color=rgb(216,204,191)}, FC)
H.part({Name="PlacaMoldura", Size=V3(7.9,0.5,0.7), CFrame=placaCF*CF(0,2.3,0), Color=C.teal}, FC)
H.part({Name="PlacaMoldura", Size=V3(7.9,0.5,0.7), CFrame=placaCF*CF(0,-2.3,0), Color=C.teal}, FC)
H.part({Name="PlacaMoldura", Size=V3(0.5,4.6,0.7), CFrame=placaCF*CF(-3.7,0,0), Color=C.teal}, FC)
H.part({Name="PlacaMoldura", Size=V3(0.5,4.6,0.7), CFrame=placaCF*CF(3.7,0,0), Color=C.teal}, FC)
-- correntes curtas ate a viga acima
for _,sx in ipairs({-3,3}) do
  H.part({Name="PlacaCorrente", Size=V3(0.25,1.6,0.25), CFrame=placaCF*CF(sx,3.1,0), Color=rgb(70,60,50), Material=Enum.Material.Metal}, FC)
end
-- a mochila-simbolo, GRANDE, aba e bolso para a praca
mochila(placaCF*CF(0,-0.15,-1.1), 1.4, COURO, COURO_ESCURO)
say("placa pendurada no portico com mochila-simbolo")

-- ============ 2) balcao ============
local balcaoCF = S * CF(5.5, 0, 0) -- dentro, perto da entrada
local by = chao
H.part({Name="BalcaoCorpo", Size=V3(2.2,2.6,10), CFrame=balcaoCF+V3(0,0,0)*V3(1,1,1), Color=C.laca}, FC)
-- reposiciona: corpo do balcao com base no chao
for _,p in ipairs(FC:GetChildren()) do
  if p.Name=="BalcaoCorpo" then p.CFrame=balcaoCF*CF(0, (by+1.3)-balcaoCF.Position.Y, 0) end
end
H.part({Name="BalcaoTampo", Size=V3(2.8,0.35,10.6), CFrame=balcaoCF*CF(0,(by+2.77)-balcaoCF.Position.Y,0), Color=rgb(90,58,42), Material=Enum.Material.Wood}, FC)
H.part({Name="BalcaoFriso", Size=V3(2.9,0.18,10.7), CFrame=balcaoCF*CF(0,(by+2.55)-balcaoCF.Position.Y,0), Color=rgb(240,196,90), Material=Enum.Material.Metal}, FC)
H.collider("hx_f14c_balcao", V3(2.9,3,10.7), balcaoCF*CF(0,(by+1.5)-balcaoCF.Position.Y,0))
-- uma mochila de amostra sobre o balcao
mochila(balcaoCF*CF(0,(by+3.6)-balcaoCF.Position.Y,3)*CFrame.Angles(0,math.rad(-90),0), 0.75, rgb(60,120,130), COURO_ESCURO)
say("balcao com tampo e mochila de amostra")

-- ============ 3) expositor no fundo ============
local expCF = S * CF(-8.2, 0, 0) -- parede do fundo (local -X)
for i,alt in ipairs({2.2, 5.0}) do
  H.part({Name="Prateleira", Size=V3(1.6,0.3,11), CFrame=expCF*CF(0,(chao+alt)-expCF.Position.Y,0), Color=rgb(90,58,42), Material=Enum.Material.Wood}, FC)
end
H.part({Name="ExpositorFundo", Size=V3(0.3,6.4,11.4), CFrame=expCF*CF(-0.9,(chao+3.4)-expCF.Position.Y,0), Color=rgb(124,37,44)}, FC)
local CORES = {{rgb(160,100,58),rgb(112,70,42)},{rgb(58,132,144),rgb(36,92,102)},{rgb(196,52,44),rgb(130,36,40)}}
for i=1,3 do
  local z = (i-2)*3.8
  mochila(expCF*CF(0.3,(chao+2.35+1.6)-expCF.Position.Y,z)*CFrame.Angles(0,math.rad(90),0), 0.95, CORES[i][1], CORES[i][2])
end
mochila(expCF*CF(0.3,(chao+5.15+1.3)-expCF.Position.Y,-1.9)*CFrame.Angles(0,math.rad(90),0), 0.8, rgb(240,196,90), COURO)
H.collider("hx_f14c_expositor", V3(2.2,6.5,11.4), expCF*CF(-0.3,(chao+3.25)-expCF.Position.Y,0))
say("expositor com 4 mochilas em 2 prateleiras")

L:SetAttribute("HEX_F14C_OK", true)
H.commit(rec)
return "F14c OK\n"..table.concat(rep,"\n")