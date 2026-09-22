-- hex_f25_gatehouse_blockout.lua : F25 = GATEHOUSE NOVO - SO BLOCKOUT (briefing itens 9-13).
-- PARADA OBRIGATORIA apos este script: o usuario avalia a silhueta em 5 vistas antes de
-- qualquer acabamento (item 17). NAO reutiliza a estrutura anterior: o portao antigo
-- (PORTAO_muralha/parapeito/pilares + massas F22 + telhado F23) vai INTEIRO para o storage.
-- Nova massa: base de pedra larga -> TUNEL profundo (26 de vao x 24 de profundidade,
-- fachada->tunel->saida) -> salao superior com janelas e varanda -> 2 torres fortificadas
-- de 47 (integradas a muralha) -> telhado dominante em 2 niveis. Blockout = caixas.
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
local L, C = H.L, H.C
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F24_OK")==true, "F25: rode a F24 antes")
local rec = H.begin("HEX F25 gatehouse blockout")
local F22 = L:FindFirstChild("HEX_F22")
local F23 = L:FindFirstChild("HEX_F23")
local F25 = H.folder(L,"HEX_F25") H.clear(F25)
local REM = SS:FindFirstChild("F24_REMOVIDOS") or (function() local f=Instance.new("Folder") f.Name="F24_REMOVIDOS" f.Parent=SS return f end)()
local function tira(i, sub)
  if not i or i:IsDescendantOf(REM) then return 0 end
  if i:GetAttribute("OrigemPath")==nil then i:SetAttribute("OrigemPath", i.Parent:GetFullName()) end
  i.Parent = H.folder(REM, sub)
  return 1
end

-- ============ portao antigo INTEIRO para o storage ============
local nOld = 0
local Portao = L:FindFirstChild("Portao")
if Portao then
  for _,c in ipairs(Portao:GetChildren()) do
    if c.Name=="PORTAO_muralha" or c.Name=="PORTAO_parapeito" or (c.Name=="KIT_muro_pilar" and math.abs(c.Position.Z-150)<3) then
      nOld += tira(c, "GateAntigo")
    end
  end
end
if F22 then
  for _,p in ipairs(F22:GetChildren()) do
    if p.Name:sub(1,6)=="B_Gate" then nOld += tira(p, "GateAntigo") end
  end
end
if F23 then
  for _,p in ipairs(F23:GetChildren()) do
    if p.Name:sub(1,6)=="TEL_F2" or p.Name=="TorreRemate" or p:IsA("WedgePart") then
      nOld += tira(p, "GateAntigo")
    end
  end
end
say("portao antigo movido para storage:", nOld, "pecas")

local PEDRA = rgb(168,158,146)
local function blq(o) local p=H.part(o,F25) p:SetAttribute("Blockout",true) return p end
local Z = 150

-- ============ base de pedra + tunel profundo ============
for _,sx in ipairs({-1,1}) do
  -- pier de base (pedra) e corpo vermelho do tunel
  blq({Name="G_BasePier", Size=V3(34,7,26), CFrame=CF(sx*30,3.5,Z), Color=PEDRA, Material=Enum.Material.Slate, CanCollide=true})
  blq({Name="G_CorpoTunel", Size=V3(34,18,24), CFrame=CF(sx*30,16,Z), Color=C.muro, CanCollide=true})
end
-- teto do tunel (lintel) e faixa dourada da fachada
blq({Name="G_Lintel", Size=V3(30,4,24), CFrame=CF(0,20,Z), Color=C.muro, CanCollide=true})
blq({Name="G_FaixaOuro", Size=V3(28,1.2,0.6), CFrame=CF(0,18.6,Z-12.4), Color=rgb(240,196,90), Material=Enum.Material.Metal})
blq({Name="G_FaixaOuro", Size=V3(28,1.2,0.6), CFrame=CF(0,18.6,Z+12.4), Color=rgb(240,196,90), Material=Enum.Material.Metal})
say("base de pedra + tunel 26x18x24 (fachada->tunel->saida)")

-- ============ salao superior com janelas e varanda ============
blq({Name="G_Salao", Size=V3(64,11,20), CFrame=CF(0,27.5,Z), Color=C.muro, CanCollide=true})
for _,sz in ipairs({-1,1}) do
  for k=-2,2 do
    blq({Name="G_Janela", Size=V3(4.2,5,0.5), CFrame=CF(k*12,27.5,Z+sz*10.2), Color=rgb(58,30,30)})
  end
  blq({Name="G_Varanda", Size=V3(66,1.8,1.0), CFrame=CF(0,23,Z+sz*10.8), Color=C.teal})
end
say("salao superior com 10 janelas e varandas")

-- ============ torres fortificadas integradas a muralha ============
for _,sx in ipairs({-1,1}) do
  blq({Name="G_TorreBase", Size=V3(24,8,24), CFrame=CF(sx*55,4,Z), Color=PEDRA, Material=Enum.Material.Slate, CanCollide=true})
  blq({Name="G_TorreCorpo", Size=V3(22,26,22), CFrame=CF(sx*55,21,Z), Color=C.muro, CanCollide=true})
  blq({Name="G_TorreSalao", Size=V3(18,8,18), CFrame=CF(sx*55,38,Z), Color=C.muro})
  blq({Name="G_TorreJanela", Size=V3(3.4,4,0.5), CFrame=CF(sx*55,38,Z-9.2), Color=rgb(58,30,30)})
  blq({Name="G_TorreCapa", Size=V3(26,3.5,26), CFrame=CF(sx*55,43.8,Z), Color=C.teal})
  blq({Name="G_TorreCapa2", Size=V3(14,2.5,14), CFrame=CF(sx*55,46.8,Z), Color=C.teal})
  blq({Name="G_TorreBanner", Size=V3(5,16,0.4), CFrame=CF(sx*55,25,Z-11.6), Color=C.laca})
end
say("torres 47 de altura em x=+-55 (dentro da linha da muralha)")

-- ============ telhados dominantes (massas) ============
blq({Name="G_Telhado1", Size=V3(78,4.5,28), CFrame=CF(0,35.5,Z), Color=C.teal})
blq({Name="G_Telhado2", Size=V3(54,4,22), CFrame=CF(0,41.5,Z), Color=C.teal})
blq({Name="G_Cumeeira", Size=V3(30,2.5,8), CFrame=CF(0,44.5,Z), Color=C.teal})
say("telhado em 2 niveis (cumeeira Y 44.5-45.7)")

L:SetAttribute("HEX_F25_OK", true)
H.commit(rec)
say("PARADA: avaliar silhueta nas 5 vistas antes de acabamento (item 17)")
return "F25 OK (BLOCKOUT DO GATEHOUSE)\n"..table.concat(rep,"\n")