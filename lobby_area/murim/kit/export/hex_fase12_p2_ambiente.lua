-- hex_fase12_p2_ambiente.lua : P2 = ambientacao (plano de beleza aprovado).
-- A) petalas caindo no patio (4 emissores discretos).
-- B) koi nos lagos (3 por lago, logo abaixo da superficie).
-- C) cachoeiras na borda da ilha (design ajustado da F9: atravessam as rochas, SAI 8-16).
-- D) nuvens volumetricas (Clouds no Terrain, tag P2_Clouds).
-- Idempotente: limpa HEX_P2; Clouds so cria se nao existir.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_P1_OK")==true, "P2: rode o P1 antes")
math.randomseed(12)
local rec = H.begin("HEX P2 ambiente")
local P2 = H.folder(L,"HEX_P2") H.clear(P2)

-- ============ A) petalas ============
for i,p in ipairs({V3(46,16,46), V3(-46,16,46), V3(-46,16,-40), V3(46,16,-40)}) do
  local e = H.part({Name="P2_petalas_"..i, Size=V3(30,0.4,30), CFrame=CF(p),
    Transparency=1, CastShadow=false}, P2)
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

-- ============ B) koi ============
local aguas = {}
for _,q in ipairs(L.HEX_Lagos:GetDescendants()) do
  if q:IsA("BasePart") and q.Size.X>8 and q.Size.Z>8 and q.Size.Y<=2.5 then
    local c = q.Color
    if math.abs(c.R-C.agua.R)<0.12 and math.abs(c.G-C.agua.G)<0.12 and math.abs(c.B-C.agua.B)<0.12 then
      table.insert(aguas, q) end
  end
end
local nKoi = 0
local CORES_KOI = {rgb(240,120,50), rgb(245,245,240), rgb(238,90,40)}
for _,w in ipairs(aguas) do
  local top = w.Position.Y + w.Size.Y/2
  for i=1,3 do
    local lx = (math.random()-0.5)*(w.Size.X-6)
    local lz = (math.random()-0.5)*(w.Size.Z-6)
    local p = w.CFrame:PointToWorldSpace(V3(lx,0,lz))
    local giro = CFrame.Angles(0, math.rad(math.random(0,359)), 0)
    local cor = CORES_KOI[(i%3)+1]
    local corpo = H.part({Name="P2_koi", Class="Part", Shape=Enum.PartType.Ball,
      Size=V3(2.4,0.65,0.9), CFrame=CF(p.X, top-0.28, p.Z)*giro,
      Color=cor, Material=Enum.Material.SmoothPlastic, CastShadow=false}, P2)
    H.part({Name="P2_koi_cauda", Class="WedgePart", Size=V3(0.5,0.5,0.9),
      CFrame=corpo.CFrame*CF(-1.45,0,0)*CFrame.Angles(0,math.rad(-90),0),
      Color=rgb(245,245,240), Material=Enum.Material.SmoothPlastic, CastShadow=false}, P2)
    -- mancha nas costas do koi branco
    if i%3==1 then
      H.part({Name="P2_koi_mancha", Class="Part", Shape=Enum.PartType.Ball, Size=V3(0.9,0.3,0.6),
        CFrame=corpo.CFrame*CF(0.3,0.25,0), Color=rgb(238,90,40), CastShadow=false}, P2)
    end
    nKoi += 1
  end
end
say("koi:", nKoi, "em", #aguas, "lagos")

-- ============ C) cachoeiras (design final da F9) ============
local sTop, sMinX, sMaxX, sMinZ, sMaxZ = -math.huge, math.huge, -math.huge, math.huge, -math.huge
local function accSolo(c)
  if c:IsA("BasePart") and c.Size.Y <= 6 then
    sTop = math.max(sTop, c.Position.Y + c.Size.Y/2)
    sMinX = math.min(sMinX, c.Position.X - c.Size.X/2) sMaxX = math.max(sMaxX, c.Position.X + c.Size.X/2)
    sMinZ = math.min(sMinZ, c.Position.Z - c.Size.Z/2) sMaxZ = math.max(sMaxZ, c.Position.Z + c.Size.Z/2)
  end
end
for _,c in ipairs(L.HEX_Chao.Fora:GetDescendants()) do accSolo(c) end
for _,c in ipairs(L.ChaoSimples:GetDescendants()) do accSolo(c) end
local QUEDAS = {
  {x=-72, z=sMaxZ, rot=0},  {x=72, z=sMaxZ, rot=0},
  {x=sMinX, z=40, rot=90},  {x=sMaxX, z=40, rot=-90},
  {x=sMinX, z=-60, rot=90}, {x=sMaxX, z=-60, rot=-90},
}
local nCas = 0
for _,q in ipairs(QUEDAS) do
  local x, z = q.x, q.z
  local rotY = CFrame.Angles(0, math.rad(q.rot), 0)
  local base = CF(x, 0, z) * rotY
  local n = base.LookVector
  local tg = V3(-n.Z, 0, n.X)
  local maxFora = 0
  for _,r in ipairs(L.Patio:GetChildren()) do
    if r:IsA("BasePart") and r.Name:sub(1,12)=="LOB_penhasco" then
      local d = r.Position - V3(x, r.Position.Y, z)
      local lat = d.X*tg.X + d.Z*tg.Z
      if math.abs(lat) < 16 then
        maxFora = math.max(maxFora, d.X*n.X + d.Z*n.Z + math.max(r.Size.X, r.Size.Z)/2)
      end
    end
  end
  local SAI = math.clamp(maxFora*0.45, 8, 16)
  local function seg(name, dy, h, tr, w)
    H.part({Name=name, Size=V3(w, h, 1.1), CFrame=base*CF(0, dy, SAI),
      Color=rgb(214,242,250), Material=Enum.Material.Glass, Transparency=tr, CastShadow=false}, P2)
  end
  seg("P2_quedaA", sTop-17, 34, 0.12, 16)
  seg("P2_quedaB", sTop-45, 24, 0.38, 14)
  for k=-1,1 do
    H.part({Name="P2_filete", Size=V3(1.4, 30, 0.4), CFrame=base*CF(k*4.2, sTop-15, SAI+0.5),
      Color=rgb(255,255,255), Material=Enum.Material.Neon, Transparency=0.35, CastShadow=false}, P2)
  end
  local espuma = H.part({Name="P2_espuma", Size=V3(13.5, 1.6, 3.4), CFrame=base*CF(0, sTop+0.2, SAI-0.8),
    Color=rgb(255,255,255), Material=Enum.Material.Neon, Transparency=0.1, CastShadow=false}, P2)
  H.part({Name="P2_lingua", Size=V3(13, 0.8, 8), CFrame=base*CF(0, sTop-0.1, SAI-3.5),
    Color=rgb(190,232,244), Material=Enum.Material.Glass, Transparency=0.2, CastShadow=false}, P2)
  local pe = Instance.new("ParticleEmitter")
  pe.Color = ColorSequence.new(rgb(230,248,252))
  pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,1.2), NumberSequenceKeypoint.new(1,3.2)})
  pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0,0.55), NumberSequenceKeypoint.new(1,1)})
  pe.Rate = 6 pe.Lifetime = NumberRange.new(1.6, 2.6)
  pe.Speed = NumberRange.new(2, 4) pe.SpreadAngle = Vector2.new(12, 12)
  pe.Acceleration = V3(0, -14, 0)
  pe.Parent = espuma
  nCas += 1
end
say("cachoeiras:", nCas, "(topo ilha", ("%.1f"):format(sTop), ")")

-- ============ D) nuvens ============
local terr = workspace:FindFirstChildOfClass("Terrain")
local cl = terr and terr:FindFirstChildOfClass("Clouds")
if terr and not cl then
  cl = Instance.new("Clouds")
  cl.Cover = 0.48 cl.Density = 0.22 cl.Color = rgb(255,252,248)
  cl:SetAttribute("P2_Clouds", true)
  cl.Parent = terr
  say("Clouds criado (Cover 0.48)")
else
  say("Clouds ja existia ou sem Terrain - intocado")
end

L:SetAttribute("HEX_P2_OK", true)
H.commit(rec)
say("marcador HEX_P2_OK gravado")
return "P2 OK\n"..table.concat(rep,"\n")