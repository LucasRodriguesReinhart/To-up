-- hex_f17_galeria_atico.lua : F17 = causa real da "faixa clara" da galeria (briefing ciclo 3).
-- O TEL_F1 pressupoe um corpo de fachada ate a linha do beiral (como na Forja); na galeria
-- ficava ceu aberto entre a viga e a barriga do telhado. Este script constroi o ATICO:
-- caixa de fechamento vermelha com fileira de blocos teal e filete dourado, nas 4 faces,
-- recuada da borda da viga, morrendo dentro do telhado.
-- Idempotente: limpa HEX_F17.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F16_OK")==true, "F17: rode a F16 antes")
local rec = H.begin("HEX F17 atico galeria")
local F17 = H.folder(L,"HEX_F17") H.clear(F17)

local gal
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="SANT_galeria" then gal=d break end
end
assert(gal, "F17: SANT_galeria nao achada")
local G = gal.CFrame
local topo = gal.Position.Y + gal.Size.Y/2 -- 32.38
-- corpo do atico: comprimento local Z (89.2), profundidade local X (41.8)
local LEN, DEP = gal.Size.Z - 4, gal.Size.X - 7
local hAt = 4.6
local yc = topo + hAt/2 - 0.3
-- nucleo (fecha o vao por completo)
H.part({Name="AticoNucleo", Size=V3(DEP, hAt, LEN),
  CFrame=CF(gal.Position.X, yc, gal.Position.Z)*(G-G.Position),
  Color=C.laca, Material=Enum.Material.SmoothPlastic, CastShadow=false}, F17)
-- filete dourado no topo das 4 faces
local function faixa(offX, offZ, w, l, cor, dy, esp, mat)
  H.part({Name="AticoFaixa", Size=V3(w, esp, l),
    CFrame=(CF(gal.Position.X, yc+dy, gal.Position.Z)*(G-G.Position))*CF(offX, 0, offZ),
    Color=cor, Material=mat or Enum.Material.SmoothPlastic, CastShadow=false}, F17)
end
faixa( DEP/2+0.1, 0, 0.5, LEN+0.2, rgb(240,196,90), hAt/2-0.5, 0.6)
faixa(-DEP/2-0.1, 0, 0.5, LEN+0.2, rgb(240,196,90), hAt/2-0.5, 0.6)
faixa(0,  LEN/2+0.1, DEP+0.2, 0.5, rgb(240,196,90), hAt/2-0.5, 0.6)
faixa(0, -LEN/2-0.1, DEP+0.2, 0.5, rgb(240,196,90), hAt/2-0.5, 0.6)
-- fileira de blocos teal nas 2 faces longas (continuidade com a viga existente)
local nBloco = 0
local passo = 7.4
local meia = math.floor((LEN/2-4)/passo)
for k=-meia,meia do
  for _,sx in ipairs({1,-1}) do
    H.part({Name="AticoBloco", Size=V3(0.5, 1.9, 3.4),
      CFrame=(CF(gal.Position.X, yc-0.5, gal.Position.Z)*(G-G.Position))*CF(sx*(DEP/2+0.15), 0, k*passo),
      Color=C.teal, Material=Enum.Material.SmoothPlastic, CastShadow=false}, F17)
    nBloco += 1
  end
end
say(("atico: nucleo %.0fx%.1fx%.0f + 4 filetes + %d blocos teal"):format(DEP,hAt,LEN,nBloco))

L:SetAttribute("HEX_F17_OK", true)
H.commit(rec)
return "F17 OK\n"..table.concat(rep,"\n")