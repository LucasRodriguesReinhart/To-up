-- hex_fase9_vegetacao.lua : F9 = transformacao visual rumo a referencia (imagem 1.webp da sessao 2026-09-21).
-- A) colhe templates SAKURA_C e VERDE_A de workspace.TEMP_ARVORES -> ServerStorage.LIB_ARVORES (sem scripts);
--    apaga TEMP_ARVORES (inclui candidatos reprovados SAKURA_A/B).
-- B) planta arvores por clone: 4 canteiros (verde pequena), canteiros da forja (sakura), entorno dos lagos,
--    faces BL/BR, e sakuras grandes FORA da muralha nas quinas visiveis (so onde o chao da ilha existe).
--    1 collider cilindrico por tronco (hx_f9_), copas sem colisao.
-- C) lagos: vitorias-regias + flores de lotus sobre a agua (acha as partes de agua por cor/posicao em HEX_Lagos).
-- D) cachoeiras na borda frontal/lateral da ilha (2 segmentos + espuma + particulas), fora do vao da ponte.
-- E) petalas caindo: 4 emissores discretos no patio.
-- Idempotente: limpa HEX_Veg, HEX_Cachoeiras, HEX_Petalas e colliders hx_f9_ antes de recriar.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, C = H.L, H.C
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F8_OK")==true, "F9: rode a F8 antes")
math.randomseed(9)

local rec = H.begin("HEX F9 vegetacao")

-- ============ A) templates ============
local LIB = SS:FindFirstChild("LIB_ARVORES")
local TEMP = workspace:FindFirstChild("TEMP_ARVORES")
if TEMP then
  LIB = LIB or (function() local f=Instance.new("Folder") f.Name="LIB_ARVORES" f.Parent=SS return f end)()
  for _,nm in ipairs({"SAKURA_C","VERDE_A"}) do
    local m = TEMP:FindFirstChild(nm)
    if m and not LIB:FindFirstChild(nm) then m.Parent = LIB end
  end
  TEMP:Destroy()
end
assert(LIB and LIB:FindFirstChild("SAKURA_C") and LIB:FindFirstChild("VERDE_A"), "F9: templates ausentes")
for _,m in ipairs(LIB:GetChildren()) do
  for _,d in ipairs(m:GetDescendants()) do
    if d:IsA("BaseScript") or d:IsA("ModuleScript") then d:Destroy()
    elseif d:IsA("BasePart") then d.Anchored=true d.CanCollide=false d.CanQuery=false d.CanTouch=false d.CastShadow=false end
  end
end

-- ============ limpeza (idempotencia) ============
local VEG = H.folder(L,"HEX_Veg") H.clear(VEG)
local CAS = H.folder(L,"HEX_Cachoeiras") H.clear(CAS)
local PET = H.folder(L,"HEX_Petalas") H.clear(PET)
H.clearColliders("hx_f9_")

-- chao da ilha (para cachoeiras e arvores externas): uniao de HEX_Chao.Fora + ChaoSimples
local sTop, sMinX, sMaxX, sMinZ, sMaxZ = -math.huge, math.huge, -math.huge, math.huge, -math.huge
local nSolo = 0
local function accSolo(c)
  if c:IsA("BasePart") and c.Size.Y <= 6 then -- so placas horizontais (Fora_canto e vertical)
    sTop = math.max(sTop, c.Position.Y + c.Size.Y/2)
    sMinX = math.min(sMinX, c.Position.X - c.Size.X/2) sMaxX = math.max(sMaxX, c.Position.X + c.Size.X/2)
    sMinZ = math.min(sMinZ, c.Position.Z - c.Size.Z/2) sMaxZ = math.max(sMaxZ, c.Position.Z + c.Size.Z/2)
    nSolo += 1
  end
end
for _,c in ipairs(L.HEX_Chao.Fora:GetDescendants()) do accSolo(c) end
for _,c in ipairs(L.ChaoSimples:GetDescendants()) do accSolo(c) end
assert(nSolo > 0, "F9: chao externo nao achado")
say("ilha: top", ("%.2f"):format(sTop), "x", ("%.0f..%.0f"):format(sMinX,sMaxX), "z", ("%.0f..%.0f"):format(sMinZ,sMaxZ))

-- ============ B) arvores ============
local nArv = 0
local function planta(nome, escala, pos, giro)
  local t = LIB[nome]:Clone()
  t.Name = nome.."_"..tostring(nArv+1)
  t:ScaleTo(t:GetScale()*escala)
  t.Parent = VEG
  local cf, sz = t:GetBoundingBox()
  -- base da copa no Y pedido, leve enterro de 0.25
  t:PivotTo(CF(pos.X, pos.Y, pos.Z) * CFrame.Angles(0, math.rad(giro or math.random(0,359)), 0)
    * (t:GetPivot() - t:GetPivot().Position) + Vector3.zero)
  -- reposiciona: pivo pode nao ser a base; alinhar bbox
  local cf2, sz2 = t:GetBoundingBox()
  local dy = (pos.Y - 0.25 + sz2.Y/2) - cf2.Position.Y
  local dxz = V3(pos.X - cf2.Position.X, 0, pos.Z - cf2.Position.Z)
  t:PivotTo(t:GetPivot() + V3(dxz.X, dy, dxz.Z))
  H.collider("hx_f9_tronco", V3(1.6*escala+0.6, 8, 1.6*escala+0.6), CF(pos.X, pos.Y+4, pos.Z), "Part")
  nArv += 1
  return t
end

-- 4 canteiros centrais: verde pequena (topo do canteiro medido nas pecas proximas)
for _,p in ipairs(H.LAY.PLANTERS) do
  local topo = 0
  for _,q in ipairs(L.HEX_Canteiros:GetChildren()) do
    if q:IsA("BasePart") and math.abs(q.Position.X-p.X)<4.5 and math.abs(q.Position.Z-p.Z)<4.5 then
      topo = math.max(topo, q.Position.Y + q.Size.Y/2) end
  end
  planta("VERDE_A", 0.38, V3(p.X, math.max(topo-0.3,0), p.Z))
end
say("canteiros centrais: 4 verdes")

-- canteiros da forja: sakura media
for i,p in ipairs(H.LAY.FORGE_BEDS) do
  planta("SAKURA_C", 0.62, V3(p.X, 0.6, p.Z), i==1 and 20 or 200)
end
say("canteiros forja: 2 sakuras")

-- entorno dos lagos (face FL e FR): sakura nas pontas, verdes entre lago e muralha
local ARV_LAGO = {
  {f="FL", s=-62, d=21, nome="SAKURA_C", e=0.85},
  {f="FL", s= 22, d=23, nome="SAKURA_C", e=0.75},
  {f="FL", s=-32, d=6.5, nome="VERDE_A", e=0.62},
  {f="FL", s=  2, d=6.5, nome="VERDE_A", e=0.55},
  {f="FR", s= -8, d=21, nome="SAKURA_C", e=0.8},
  {f="FR", s= 60, d=21, nome="SAKURA_C", e=0.85},
  {f="FR", s= 16, d=6.5, nome="VERDE_A", e=0.6},
  {f="FR", s= 42, d=6.5, nome="VERDE_A", e=0.55},
}
for _,a in ipairs(ARV_LAGO) do planta(a.nome, a.e, H.fp(a.f, a.s, a.d, 0), nil) end
say("lagos: 4 sakuras + 4 verdes")

-- faces BL/BR (fundo, perto da forja): sakura + verde
local ARV_TRAS = {
  {f="BL", s=-34, d=8, nome="SAKURA_C", e=0.8},
  {f="BL", s= 16, d=7, nome="VERDE_A", e=0.6},
  {f="BR", s= 34, d=8, nome="SAKURA_C", e=0.8},
  {f="BR", s=-16, d=7, nome="VERDE_A", e=0.6},
}
for _,a in ipairs(ARV_TRAS) do planta(a.nome, a.e, H.fp(a.f, a.s, a.d, 0), nil) end
say("fundo BL/BR: 2 sakuras + 2 verdes")

-- sakuras grandes FORA da muralha, nas quinas do hexagono (aparecem acima do muro como na referencia)
local R = 150/math.cos(math.rad(30)) -- raio das quinas ~173.2
local fora = 0
for _,ang in ipairs({0, 60, 120, 180, 240, 300}) do
  local a = math.rad(ang)
  local p = V3((R+16)*math.cos(a), sTop, (R+16)*math.sin(a))
  if p.X > sMinX+8 and p.X < sMaxX-8 and p.Z > sMinZ+8 and p.Z < sMaxZ-8 then
    planta("SAKURA_C", 1.05, p, nil) fora += 1
  end
end
say("quinas externas:", fora, "sakuras grandes")

-- ============ C) lagos: vitorias-regias e lotus ============
local nPad, aguas = 0, {}
for _,q in ipairs(L.HEX_Lagos:GetDescendants()) do
  if q:IsA("BasePart") and q.Size.X>8 and q.Size.Z>8 and q.Size.Y<=2.5 then
    local c = q.Color
    if math.abs(c.R-C.agua.R)<0.12 and math.abs(c.G-C.agua.G)<0.12 and math.abs(c.B-C.agua.B)<0.12 then
      table.insert(aguas, q) end
  end
end
say("partes de agua achadas:", #aguas)
for _,w in ipairs(aguas) do
  local top = w.Position.Y + w.Size.Y/2
  local hx, hz = w.Size.X/2-2.5, w.Size.Z/2-2.5
  local n = math.max(4, math.floor((w.Size.X*w.Size.Z)/140))
  for i=1,n do
    local lx = (math.random()-0.5)*2*hx
    local lz = (math.random()-0.5)*2*hz
    local p = w.CFrame:PointToWorldSpace(V3(lx, 0, lz))
    local raio = 1.1 + math.random()*0.9
    local pad = H.part({Name="Vitoria", Class="Part", Shape=Enum.PartType.Cylinder,
      Size=V3(0.18, raio*2, raio*2), CFrame=CF(p.X, top+0.09, p.Z)*CFrame.Angles(0,math.rad(math.random(0,359)),math.rad(90)),
      Color=C.lirio, Material=Enum.Material.Grass}, VEG)
    if i % 3 == 1 then -- flor de lotus em 1/3 das folhas
      local fy = top+0.35
      H.part({Name="LotusBase", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.5,1.6,1.6),
        CFrame=CF(p.X, fy, p.Z)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(244,143,177)}, VEG)
      H.part({Name="LotusMiolo", Class="Part", Shape=Enum.PartType.Ball, Size=V3(0.7,0.7,0.7),
        CFrame=CF(p.X, fy+0.35, p.Z), Color=rgb(255,214,98), Material=Enum.Material.Neon}, VEG)
      for k=0,4 do
        local aa = math.rad(72*k)
        H.part({Name="LotusPetala", Class="Part", Shape=Enum.PartType.Ball, Size=V3(1.0,0.5,0.55),
          CFrame=CF(p.X+math.cos(aa)*0.55, fy+0.18, p.Z+math.sin(aa)*0.55)*CFrame.Angles(0,-aa,math.rad(18)),
          Color=rgb(248,166,190)}, VEG)
      end
    end
    nPad += 1
  end
end
say("vitorias-regias:", nPad)

-- ============ D) cachoeiras na borda da ilha ============
-- frente (+Z): 2 fora do vao central da ponte; laterais: 1 de cada lado, na altura dos lagos
local QUEDAS = {
  {x=-72, z=sMaxZ, rot=0},  {x=72, z=sMaxZ, rot=0},
  {x=sMinX, z=40, rot=90},  {x=sMaxX, z=40, rot=-90},
  {x=sMinX, z=-60, rot=90}, {x=sMaxX, z=-60, rot=-90},
}
local nCas = 0
for _,q in ipairs(QUEDAS) do
  local x = math.clamp(q.x, sMinX, sMaxX)
  local z = math.clamp(q.z, sMinZ, sMaxZ)
  local rotY = CFrame.Angles(0, math.rad(q.rot), 0)
  local base = CF(x, 0, z) * rotY -- +Z local aponta para fora da ilha
  -- avanco: na frente das rochas do penhasco proximas desta queda
  local n = base.LookVector
  local tg = V3(-n.Z, 0, n.X)
  local maxFora = 0
  for _,r in ipairs(L.Patio:GetChildren()) do
    if r:IsA("BasePart") and r.Name:sub(1,12)=="LOB_penhasco" then
      local d = r.Position - V3(x, r.Position.Y, z)
      local lat = d.X*tg.X + d.Z*tg.Z
      if math.abs(lat) < 16 then
        local fora = d.X*n.X + d.Z*n.Z + math.max(r.Size.X, r.Size.Z)/2
        maxFora = math.max(maxFora, fora)
      end
    end
  end
  local SAI = math.clamp(maxFora*0.45, 8, 16) -- entre as rochas: parte aparece, parte se esconde
  local function seg(name, dy, h, tr, w)
    H.part({Name=name, Size=V3(w, h, 1.1), CFrame=base*CF(0, dy, SAI),
      Color=rgb(214,242,250), Material=Enum.Material.Glass, Transparency=tr, CastShadow=false}, CAS)
  end
  seg("QuedaA", sTop-17, 34, 0.12, 16)
  seg("QuedaB", sTop-45, 24, 0.38, 14)
  for k=-1,1 do -- filetes verticais mais claros, como na referencia
    H.part({Name="Filete", Size=V3(1.4, 30, 0.4), CFrame=base*CF(k*4.2, sTop-15, SAI+0.5),
      Color=rgb(255,255,255), Material=Enum.Material.Neon, Transparency=0.35, CastShadow=false}, CAS)
  end
  local espuma = H.part({Name="Espuma", Size=V3(13.5, 1.6, 3.4), CFrame=base*CF(0, sTop+0.2, SAI-0.8),
    Color=rgb(255,255,255), Material=Enum.Material.Neon, Transparency=0.1, CastShadow=false}, CAS)
  H.part({Name="Lingua", Class="Part", Size=V3(13, 0.8, 8), CFrame=base*CF(0, sTop-0.1, SAI-3.5),
    Color=rgb(190,232,244), Material=Enum.Material.Glass, Transparency=0.2, CastShadow=false}, CAS)
  say(("queda x=%.0f z=%.0f SAI=%.1f"):format(x, z, SAI))
  local pe = Instance.new("ParticleEmitter")
  pe.Color = ColorSequence.new(rgb(230,248,252))
  pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,1.2), NumberSequenceKeypoint.new(1,3.2)})
  pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0,0.55), NumberSequenceKeypoint.new(1,1)})
  pe.Rate = 6 pe.Lifetime = NumberRange.new(1.6, 2.6)
  pe.Speed = NumberRange.new(2, 4) pe.SpreadAngle = Vector2.new(12, 12)
  pe.Acceleration = V3(0, -14, 0) pe.LockedToPart = false
  pe.Parent = espuma
  nCas += 1
end
say("cachoeiras:", nCas)

-- ============ E) petalas caindo no patio ============
for i,p in ipairs({V3(46,16,46), V3(-46,16,46), V3(-46,16,-40), V3(46,16,-40)}) do
  local e = H.part({Name="EmissorPetala_"..i, Size=V3(30,0.4,30), CFrame=CF(p),
    Transparency=1, CastShadow=false}, PET)
  local pe = Instance.new("ParticleEmitter")
  pe.Color = ColorSequence.new(rgb(255,170,195), rgb(248,140,170))
  pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,0.32), NumberSequenceKeypoint.new(1,0.22)})
  pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0,0.25), NumberSequenceKeypoint.new(0.85,0.35), NumberSequenceKeypoint.new(1,1)})
  pe.Rate = 1.6 pe.Lifetime = NumberRange.new(7, 11)
  pe.Speed = NumberRange.new(0.6, 1.4) pe.SpreadAngle = Vector2.new(180, 180)
  pe.Acceleration = V3(0.5, -1.1, 0.4)
  pe.Rotation = NumberRange.new(0, 360) pe.RotSpeed = NumberRange.new(-60, 60)
  pe.EmissionDirection = Enum.NormalId.Bottom
  pe.Parent = e
end
say("petalas: 4 emissores")

L:SetAttribute("HEX_F9_OK", true)
H.commit(rec)
say("marcador HEX_F9_OK gravado; arvores:", nArv)
return "F9 OK\n"..table.concat(rep,"\n")