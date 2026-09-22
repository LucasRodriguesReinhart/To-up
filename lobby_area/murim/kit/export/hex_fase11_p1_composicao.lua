-- hex_fase11_p1_composicao.lua : P1 = foco, vinhetas e ritmo (plano de beleza aprovado).
-- A) monumento heroi: feixe de luz, particulas douradas subindo e PointLight ambar no orbe (tags P1_*).
-- B) vinhetas: nas 6 direcoes de quina (r=95), banco + lanterna + 2 rochas voltados ao centro;
--    cada posicao passa por checagem de espaco livre e e PULADA se houver qualquer coisa construida.
-- C) ritmo na muralha: clones do KIT_estandarte ao longo das faces FL/FR/BL/BR, espacados,
--    longe de pontes/torres; collider fino hx_p1_ por estandarte.
-- Idempotente: limpa HEX_P1 e colliders hx_p1_; nao mexe em nada existente alem de
-- adicionar filhos tagged P1_* no orbe do monumento (removidos na limpeza).
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_P0_OK")==true, "P1: rode o P0 antes")
math.randomseed(11)
local rec = H.begin("HEX P1 composicao")

local P1 = H.folder(L,"HEX_P1") H.clear(P1)
H.clearColliders("hx_p1_")
-- limpa efeitos P1_* de execucoes anteriores no monumento
for _,d in ipairs(L.HEX_Monumento:GetDescendants()) do
  if d:GetAttribute("P1") then d:Destroy() end
end

-- ============ A) monumento heroi ============
local orbe
for _,c in ipairs(L.HEX_Monumento:GetChildren()) do
  if c.Name=="Mon_orbe" and c:IsA("BasePart") then orbe=c break end
end
assert(orbe, "P1: Mon_orbe nao achado")
local topoOrbe = orbe.Position.Y + orbe.Size.Y/2
-- feixe vertical discreto saindo do orbe
local feixe = H.part({Name="P1_feixe", Class="Part", Shape=Enum.PartType.Cylinder,
  Size=V3(55, 3.2, 3.2), CFrame=CF(orbe.Position.X, topoOrbe+27, orbe.Position.Z)*CFrame.Angles(0,0,math.rad(90)),
  Color=rgb(255,214,120), Material=Enum.Material.Neon, Transparency=0.82, CastShadow=false}, P1)
feixe:SetAttribute("P1",true)
local pe = Instance.new("ParticleEmitter")
pe.Color = ColorSequence.new(rgb(255,220,140), rgb(255,180,80))
pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,0.35), NumberSequenceKeypoint.new(1,0.1)})
pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0,0.2), NumberSequenceKeypoint.new(1,1)})
pe.Rate = 5 pe.Lifetime = NumberRange.new(1.8, 3)
pe.Speed = NumberRange.new(2.5, 4.5) pe.SpreadAngle = Vector2.new(14, 14)
pe.Acceleration = V3(0, 1.5, 0) pe.LightEmission = 0.8
pe:SetAttribute("P1",true) pe.Parent = orbe
local pl = Instance.new("PointLight")
pl.Range = 34 pl.Brightness = 1.1 pl.Color = rgb(255,196,110) pl.Shadows = false
pl:SetAttribute("P1",true) pl.Parent = orbe
say("monumento: feixe + particulas + luz ambar no orbe (topo", ("%.1f"):format(topoOrbe), ")")

-- ============ helpers de template ============
local function acha(pasta, nome)
  for _,c in ipairs(pasta:GetDescendants()) do
    if c.Name==nome and (c:IsA("BasePart") or c:IsA("Model")) then return c end
  end
end
local banco = acha(L.Props, "VIL_banco")
local estand = acha(L.Props, "KIT_estandarte")
local rocha
for _,c in ipairs(L.HEX_Lagos:GetDescendants()) do
  if c:IsA("MeshPart") and c.Name:sub(1,9)=="LOB_rocha" then rocha=c break end
end
assert(banco and estand and rocha, "P1: template ausente (banco/estandarte/rocha)")
local function cloneAt(tpl, cfAlvo, escala, parent)
  local c = tpl:Clone()
  for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
  c:SetAttribute("HexGen",true)
  if c:IsA("BasePart") then c.Anchored=true c.CanCollide=false c.CanQuery=false c.CanTouch=false end
  if escala and escala~=1 and c:IsA("BasePart") then c.Size=c.Size*escala end
  c.Parent=parent
  -- base do bbox no Y do alvo, mantendo a rotacao pedida
  local cfr = c:IsA("Model") and select(1,c:GetBoundingBox()) or c.CFrame
  local sz = c:IsA("Model") and select(2,c:GetBoundingBox()) or c.Size
  if c:IsA("Model") then c:PivotTo(cfAlvo) else c.CFrame = cfAlvo end
  local cf2 = c:IsA("Model") and select(1,c:GetBoundingBox()) or c.CFrame
  local sz2 = c:IsA("Model") and select(2,c:GetBoundingBox()) or c.Size
  local dy = (cfAlvo.Position.Y + sz2.Y/2 - 0.1) - cf2.Position.Y
  if c:IsA("Model") then c:PivotTo(c:GetPivot()+V3(0,dy,0)) else c.CFrame = c.CFrame+V3(0,dy,0) end
  return c
end

-- checagem de espaco livre: nada construido (top>0.8) num raio horizontal
local function livre(pos, raio)
  for _,d in ipairs(L:GetDescendants()) do
    if d:IsA("BasePart") and not d:IsDescendantOf(L.HEX_Chao) and not d:IsDescendantOf(L.ChaoSimples) and not d:IsDescendantOf(P1) then
      local top = d.Position.Y + d.Size.Y/2
      if top > 0.8 and d.Position.Y < 20 then
        if math.abs(d.Position.X-pos.X) < raio and math.abs(d.Position.Z-pos.Z) < raio then return false end
      end
    end
  end
  return true
end

-- ============ B) vinhetas nas quinas ============
local nVin = 0
for _,ang in ipairs({0, 60, 120, 180, 240, 300}) do
  local a = math.rad(ang)
  local pos = V3(95*math.cos(a), 0, 95*math.sin(a))
  if livre(pos, 8) then
    local paraCentro = CFrame.lookAt(pos, V3(0,0,0))
    -- banco olhando o monumento, lanterna a direita, rochas a esquerda
    cloneAt(banco, paraCentro, 1, P1)
    H.boxLantern(P1, "P1_lanterna", pos + paraCentro.RightVector*6)
    cloneAt(rocha, CF(pos + paraCentro.RightVector*-5.5 + paraCentro.LookVector*-1)*CFrame.Angles(0,math.rad(math.random(0,359)),0), 0.8, P1)
    cloneAt(rocha, CF(pos + paraCentro.RightVector*-4 + paraCentro.LookVector*2)*CFrame.Angles(0,math.rad(math.random(0,359)),0), 0.5, P1)
    H.collider("hx_p1_banco", V3(8.4,3,2.6), paraCentro+V3(0,1.5,0))
    nVin += 1
  else
    say("vinheta", ang, "PULADA (espaco ocupado)")
  end
end
say("vinhetas construidas:", nVin)

-- ============ C) estandartes ritmando a muralha ============
local BANDS = {
  FL={-65,-39,-13,26,52}, FR={-68,-42,34,60},
  BL={-60,-30,30,60},     BR={-60,-30,30,60},
}
local nEst = 0
for f,ss in pairs(BANDS) do
  for _,s in ipairs(ss) do
    local pos = H.fp(f, s, 4.5, 0)
    if livre(pos, 2.2) then
      local F = H.FACES[f]
      local cfr = CFrame.lookAt(pos, pos + F.inw) -- de frente para o patio
      cloneAt(estand, cfr, 1, P1)
      H.collider("hx_p1_estandarte", V3(1.2,10,1.2), CF(pos+V3(0,5,0)))
      nEst += 1
    else
      say("estandarte", f, s, "PULADO")
    end
  end
end
say("estandartes na muralha:", nEst)

L:SetAttribute("HEX_P1_OK", true)
H.commit(rec)
say("marcador HEX_P1_OK gravado")
return "P1 OK\n"..table.concat(rep,"\n")