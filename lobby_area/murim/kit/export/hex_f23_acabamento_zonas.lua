-- hex_f23_acabamento_zonas.lua : F23 = acabamento do blockout F22 (pos Ctrl+S do usuario).
-- 1) GATEHOUSE: massas de telhado -> cluster REAL TEL_F2 (replica do telhado superior da
--    Forja via T*C:Inverse()); torres ganham coifa de 4 aguas + remate dourado.
-- 2) LEADERBOARDS: massa de telhado -> cluster REAL TEL_G reaproveitado do storage
--    (LojaPortico) em escala 0.8, cumeeira ao longo da face.
-- 3) TENDA: aguas de blockout -> tecido com barrado recortado (abas alternadas teal/laca),
--    amarracoes de corda nos postes e remates dourados na cumeeira.
-- 4) LAGO: vitorias-regias + lotus de volta sobre os discos (poucas).
-- 5) SAIDA: patamar de pedra portao->ponte com guias.
-- Idempotente: limpa HEX_F23; remove as massas B_* substituidas (folha HEX_F22 preservada
-- para o resto).
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

assert(L:GetAttribute("HEX_F22_OK")==true, "F23: rode a F22 antes")
math.randomseed(23)
local rec = H.begin("HEX F23 acabamento zonas")
local F22 = L:FindFirstChild("HEX_F22") assert(F22, "F23: HEX_F22 ausente")
local F23 = H.folder(L,"HEX_F23") H.clear(F23)
local REM = SS:FindFirstChild("F22_REMOVIDOS")

local function cloneCluster(pecas, Cref, T, escala, parent)
  local n = 0
  for _,p in ipairs(pecas) do
    local c = p:Clone()
    for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
    c:SetAttribute("HexGen", true)
    c.Anchored=true c.CanCollide=false c.CanQuery=false c.CanTouch=false
    if escala and escala~=1 then c.Size = c.Size*escala end
    local rel = Cref:Inverse()*p.CFrame
    local relPos = rel.Position*(escala or 1)
    c.CFrame = T * (CF(relPos) * (rel - rel.Position))
    c.Parent = parent
    n += 1
  end
  return n
end

-- ============ 1) gatehouse: telhado real TEL_F2 ============
for _,nome in ipairs({"B_GateTelhado","B_GateTelhado2","B_GateCumeeira"}) do
  for _,p in ipairs(F22:GetChildren()) do
    if p.Name==nome then p:Destroy() end
  end
end
local f2, cum2 = {}, nil
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:sub(1,6)=="TEL_F2" and not d:IsDescendantOf(F23) then
    table.insert(f2, d)
    if d.Name=="TEL_F2_cumeeira" then cum2=d end
  end
end
assert(cum2 and #f2>=11, "F23: cluster TEL_F2 nao achado ("..#f2..")")
local minY2 = math.huge
for _,p in ipairs(f2) do minY2 = math.min(minY2, p.Position.Y - p.Size.Y/2) end
local yCumGate = cum2.Position.Y - minY2 + 26.9 -- beiral assenta na sobreloja (topo 27.2)
local Tgate = CF(0, yCumGate, 150) -- cumeeira do TEL_F2 ja corre em X (igual ao portao)
local nG = cloneCluster(f2, cum2.CFrame, Tgate, 1, F23)
say("gatehouse: telhado TEL_F2 replicado:", nG, "pecas (cumeeira Y", ("%.1f"):format(yCumGate), ")")
-- coifas das torres: 4 aguas + remate
for _,sx in ipairs({-1,1}) do
  local topoT = V3(sx*48, 28.4, 150)
  for k=0,3 do
    local a = math.rad(90*k)
    local dir = V3(math.cos(a),0,math.sin(a))
    local w = Instance.new("WedgePart")
    w.Anchored=true w.CanCollide=false w.CanQuery=false w.CanTouch=false
    w.Size = V3(15,4.2,7.5)
    w.Color = C.teal w.Material = Enum.Material.SmoothPlastic
    -- LookVector aponta para o lado BAIXO da cunha (convencao do H.ramp): baixo = fora
    local look = (H.SIGN==1) and dir or -dir
    w.CFrame = CFrame.lookAt(topoT + dir*3.75 + V3(0,2.1,0), topoT + dir*3.75 + V3(0,2.1,0) + look)
    w:SetAttribute("HexGen",true) w.Parent = F23
  end
  H.part({Name="TorreRemate", Class="Part", Shape=Enum.PartType.Ball, Size=V3(1.6,1.6,1.6),
    CFrame=CF(topoT+V3(0,4.9,0)), Color=rgb(240,196,90), Material=Enum.Material.Metal}, F23)
end
say("torres com coifa de 4 aguas + remate dourado")

-- ============ 2) leaderboards: telhado real TEL_G (do storage, escala 0.8) ============
for _,nome in ipairs({"B_LB_Telhado","B_LB_Cumeeira"}) do
  for _,p in ipairs(F22:GetChildren()) do
    if p.Name==nome then p:Destroy() end
  end
end
local fonteG = REM and REM:FindFirstChild("LojaPortico")
local g, cumG = {}, nil
if fonteG then
  for _,d in ipairs(fonteG:GetChildren()) do
    if d:IsA("BasePart") and d.Name:sub(1,5)=="TEL_G" then
      table.insert(g, d)
      if d.Name=="TEL_G_cumeeira" then cumG=d end
    end
  end
end
assert(cumG and #g>=9, "F23: cluster TEL_G nao achado no storage ("..#g..")")
local minYG = math.huge
for _,p in ipairs(g) do minYG = math.min(minYG, p.Position.Y - p.Size.Y/2) end
local FRp = H.LAY.PONDS.FR
local sC, dC = (FRp.s1+FRp.s2)/2, 19
local minYrel = (minYG - cumG.Position.Y)*0.8
local yCumLB = 10.7 - minYrel
local Tlb = H.faceCF("FR", sC, dC, yCumLB) -- X local = tangente: cumeeira corre ao longo da face
local nLB = cloneCluster(g, cumG.CFrame, Tlb, 0.8, F23)
say("leaderboards: telhado TEL_G 0.8x reaproveitado:", nLB, "pecas")

-- ============ 3) tenda: tecido com barrado e amarracoes ============
local S = L:GetAttribute("F22_LojaCF")
assert(S, "F23: F22_LojaCF ausente")
local chao = 7.98
local function TB(lx,ly,lz) return S*CF(lx, ly-13.28, lz) end
for _,p in ipairs(F22:GetChildren()) do
  if p.Name=="B_TendaBarrado" then p:Destroy() end
end
-- barrado recortado: abas alternadas penduradas nas beiradas longas
local nAba = 0
for _,lado in ipairs({{-11.9, C.teal, rgb(184,50,42)}, {9.9, C.teal, rgb(184,50,42)}}) do
  for k=0,12 do
    local lz = -12.4 + k*2.1
    local cor = (k%2==0) and lado[2] or lado[3]
    H.part({Name="TendaAba", Size=V3(0.35,1.5,1.9), CFrame=TB(lado[1], chao+9.85, lz),
      Color=cor, Material=Enum.Material.Fabric}, F23)
    nAba += 1
  end
end
-- amarracoes de corda dos 4 postes de canto ate a beirada
for _,off in ipairs({{-9,-11,-1},{-9,11,-1},{7,-11,1},{7,11,1}}) do
  H.part({Name="TendaCorda", Size=V3(0.18,3.4,0.18),
    CFrame=TB(off[1]-off[3]*1.4, chao+9.4, off[2])*CFrame.Angles(0,0,math.rad(off[3]*24)),
    Color=rgb(196,168,120), Material=Enum.Material.Fabric}, F23)
end
-- remates dourados na cumeeira
for _,lz in ipairs({-13.2, 13.2}) do
  H.part({Name="TendaRemate", Class="Part", Shape=Enum.PartType.Ball, Size=V3(1.1,1.1,1.1),
    CFrame=TB(-1, chao+14.5, lz), Color=rgb(240,196,90), Material=Enum.Material.Metal}, F23)
end
say("tenda: barrado recortado (", nAba, "abas), cordas e remates")

-- ============ 4) lago: vitorias-regias de volta ============
local DISCOS = {
  {s=-38, d=21, r=12}, {s=-18, d=19, r=14}, {s=0, d=23, r=11},
  {s=14, d=18, r=9}, {s=-48, d=14, r=6},
}
local nPad = 0
for i,dsc in ipairs(DISCOS) do
  for k=1,2 do
    local a = math.random()*math.pi*2
    local rr = math.random()*(dsc.r-2.5)
    local pos = H.fp("FL", dsc.s+math.cos(a)*rr, dsc.d+math.sin(a)*rr*0.7, 0.32)
    local raio = 1.0+math.random()*0.7
    H.part({Name="Vitoria", Class="Part", Shape=Enum.PartType.Cylinder,
      Size=V3(0.16, raio*2, raio*2), CFrame=CF(pos)*CFrame.Angles(0,math.rad(math.random(0,359)),math.rad(90)),
      Color=C.lirio, Material=Enum.Material.Grass}, F23)
    if (i+k)%3==0 then
      H.part({Name="Lotus", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.45,1.4,1.4),
        CFrame=CF(pos+V3(0,0.28,0))*CFrame.Angles(0,0,math.rad(90)), Color=rgb(244,143,177)}, F23)
      H.part({Name="LotusMiolo", Class="Part", Shape=Enum.PartType.Ball, Size=V3(0.6,0.6,0.6),
        CFrame=CF(pos+V3(0,0.55,0)), Color=rgb(255,214,98), Material=Enum.Material.Neon}, F23)
    end
    nPad += 1
  end
end
say("lago: vitorias-regias:", nPad)

-- ============ 5) patamar de saida portao->ponte ============
-- fora do muro o chao esta em -0.5: patamar meio-embutido (topo 0.10), sem flutuo
H.part({Name="SaidaPatamar", Size=V3(22,0.6,12), CFrame=CF(0,-0.2,166),
  Color=rgb(176,166,152), Material=Enum.Material.Slate, CanCollide=true}, F23)
for _,sx in ipairs({-1,1}) do
  H.part({Name="SaidaGuia", Size=V3(0.8,0.55,12.4), CFrame=CF(sx*11.2,0.12,166),
    Color=rgb(150,140,126), Material=Enum.Material.Slate, CanCollide=true}, F23)
end
say("saida: patamar de pedra com guias ate a ponte")

L:SetAttribute("HEX_F23_OK", true)
H.commit(rec)
return "F23 OK\n"..table.concat(rep,"\n")