-- hex_fase13_ref_usuario.lua : F13 = upgrades das imagens melhoradas pelo usuario (2026-09-22).
-- Templates DELE (deixados no canto FL do lobby): arvore verde "Arvores", cerejeira (Model c/ Leaves),
-- lanterna-pagode (Model 6x8.5), "Vaso". Movidos para ServerStorage.LIB_USUARIO na 1a execucao.
-- A) tapetes vermelhos com borda dourada sobre as faixas de caminho (Faixas/*).
-- B) medalhoes de piso: frente do portao, adro da forja e anel vermelho ao redor do monumento.
-- C) anel do monumento em r=30: lanternas-pagode e vasos floridos alternados.
-- D) arvores dele: cerejeiras + verdes nos canteiros da forja, entorno dos lagos, BL/BR,
--    canteiros centrais e quinas externas (posicoes provadas na F9).
-- E) forja: fogo + luz nos braseiros existentes.
-- F) lotus + vitorias-regias nos lagos.
-- Idempotente: limpa HEX_F13 e colliders hx_f13_. Nada existente e alterado.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L, C = H.L, H.C
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local OURO = rgb(226,180,80)
local VERMELHO_TAPETE = rgb(178,44,40)
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_P2_OK")==true, "F13: rode o P2 antes")
math.randomseed(13)
local rec = H.begin("HEX F13 ref usuario")
local F13 = H.folder(L,"HEX_F13") H.clear(F13)
H.clearColliders("hx_f13_")

-- ============ templates do usuario -> LIB_USUARIO ============
local LIB = SS:FindFirstChild("LIB_USUARIO")
if not LIB then LIB=Instance.new("Folder") LIB.Name="LIB_USUARIO" LIB.Parent=SS end
local function adota(m, novoNome)
  if m then m.Name=novoNome m.Parent=LIB return true end
  return LIB:FindFirstChild(novoNome)~=nil
end
local sak, lant
for _,c in ipairs(workspace:GetChildren()) do
  if c.Name=="Model" and c:IsA("Model") then
    if c:FindFirstChild("Leaves") then sak=c else lant=c end
  end
end
assert(adota(workspace:FindFirstChild("Arvores"),"ARVORE_VERDE"), "F13: ARVORE_VERDE ausente")
assert(adota(sak,"SAKURA"), "F13: SAKURA ausente")
assert(adota(lant,"LANTERNA_PAGODE"), "F13: LANTERNA_PAGODE ausente")
assert(adota(workspace:FindFirstChild("Vaso"),"VASO"), "F13: VASO ausente")
for _,m in ipairs(LIB:GetChildren()) do
  for _,d in ipairs(m:GetDescendants()) do
    if d:IsA("BaseScript") or d:IsA("ModuleScript") then d:Destroy()
    elseif d:IsA("BasePart") then d.Anchored=true d.CanCollide=false d.CanQuery=false d.CanTouch=false d.CastShadow=false end
  end
end
say("LIB_USUARIO pronta:", #LIB:GetChildren(), "templates")

local function cloneAt(nome, cfAlvo, escala, parent, semAfundar)
  local c = LIB[nome]:Clone()
  for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
  c:SetAttribute("HexGen",true)
  if escala and escala~=1 then c:ScaleTo(c:GetScale()*escala) end
  c.Parent=parent
  c:PivotTo(cfAlvo)
  local cf2, sz2 = c:GetBoundingBox()
  local mergulho = semAfundar and 0.02 or 0.25
  local dy = (cfAlvo.Position.Y - mergulho + sz2.Y/2) - cf2.Position.Y
  c:PivotTo(c:GetPivot()+V3(0,dy,0))
  return c
end
local function livre(pos, raio)
  for _,d in ipairs(L:GetDescendants()) do
    if d:IsA("BasePart") and not d:IsDescendantOf(L.HEX_Chao) and not d:IsDescendantOf(L.ChaoSimples) and not d:IsDescendantOf(F13) then
      local top = d.Position.Y + d.Size.Y/2
      if top > 0.8 and d.Position.Y < 20 then
        if math.abs(d.Position.X-pos.X) < raio and math.abs(d.Position.Z-pos.Z) < raio then return false end
      end
    end
  end
  return true
end

-- ============ A) tapetes com borda dourada ============
local nTap = 0
for _,fx in ipairs(L:GetDescendants()) do
  if fx:IsA("BasePart") and fx.Parent.Name=="Faixas" then
    local sx, sz = fx.Size.X, fx.Size.Z
    local curto = math.min(sx, sz)
    if curto >= 6 then
      local aoLongoX = sx >= sz
      local topo = fx.Position.Y + fx.Size.Y/2
      local wV = math.clamp(curto*0.5, 5, 9)
      local comp = math.max(sx, sz) - 2
      local function faixa(nome, w, off, cor, mat)
        local size = aoLongoX and V3(comp, 0.06, w) or V3(w, 0.06, comp)
        local ocf = aoLongoX and CF(0, 0, off) or CF(off, 0, 0)
        H.part({Name=nome, Size=size, CFrame=fx.CFrame*ocf+V3(0, topo-fx.Position.Y+0.04, 0),
          Color=cor, Material=mat or Enum.Material.Fabric}, F13)
      end
      faixa("Tapete", wV, 0, VERMELHO_TAPETE)
      faixa("TapeteBorda", 0.8, (wV/2+0.4), OURO, Enum.Material.SmoothPlastic)
      faixa("TapeteBorda", 0.8, -(wV/2+0.4), OURO, Enum.Material.SmoothPlastic)
      nTap += 1
    end
  end
end
say("tapetes com borda dourada:", nTap, "faixas")

-- ============ B) medalhoes de piso ============
local function medalhao(cx, cz, r)
  local function disco(nome, raio, dy, cor, mat)
    H.part({Name=nome, Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.05+dy, raio*2, raio*2),
      CFrame=CF(cx, 0.05+dy/2, cz)*CFrame.Angles(0,0,math.rad(90)),
      Color=cor, Material=mat or Enum.Material.SmoothPlastic}, F13)
  end
  disco("Med_anel", r, 0.00, VERMELHO_TAPETE)
  disco("Med_campo", r*0.78, 0.02, rgb(214,196,168))
  disco("Med_ouro", r*0.32, 0.04, OURO, Enum.Material.Metal)
  for k=0,3 do
    local a=math.rad(90*k+45)
    H.part({Name="Med_raio", Size=V3(r*0.5,0.05,1.1),
      CFrame=CF(cx,0.10,cz)*CFrame.Angles(0,a,0)*CF(r*0.5,0,0),
      Color=OURO, Material=Enum.Material.Metal}, F13)
  end
end
medalhao(0, 92, 12)    -- entre o portao e o monumento
medalhao(0, -55, 10)   -- adro da forja
-- anel vermelho ao redor do monumento (faixa circular por segmentos)
for k=0,23 do
  local a = math.rad(15*k)
  H.part({Name="Anel_monumento", Size=V3(6.6,0.06,2.6),
    CFrame=CF(math.cos(a)*26, 0.06, math.sin(a)*26)*CFrame.Angles(0,-a+math.rad(90),0),
    Color=VERMELHO_TAPETE, Material=Enum.Material.Fabric}, F13)
end
say("medalhoes: 2 + anel do monumento")

-- ============ C) anel do monumento: lanternas-pagode e vasos ============
local nAnel = 0
for i,ang in ipairs({0,60,120,180,240,300}) do
  local a = math.rad(ang)
  local pos = V3(31*math.cos(a), 0, 31*math.sin(a))
  if livre(pos, 3.5) then
    local cfr = CFrame.lookAt(pos, V3(0,pos.Y,0))
    if i%2==1 then
      local m = cloneAt("LANTERNA_PAGODE", cfr, 1, F13)
      local cf2,sz2 = m:GetBoundingBox()
      local corpo = m:FindFirstChildWhichIsA("BasePart",true)
      if corpo then
        local pl=Instance.new("PointLight") pl.Range=12 pl.Brightness=0.8 pl.Color=rgb(255,190,120) pl.Shadows=false pl.Parent=corpo
      end
      H.collider("hx_f13_lanterna", V3(sz2.X+0.3, sz2.Y, sz2.Z+0.3), CF(pos.X, sz2.Y/2, pos.Z))
    else
      local m = cloneAt("VASO", cfr, 1, F13)
      local cf2,sz2 = m:GetBoundingBox()
      -- flor rosa no vaso (como nos conceitos)
      H.part({Name="VasoFlor", Class="Part", Shape=Enum.PartType.Ball, Size=V3(3.4,2.6,3.4),
        CFrame=CF(pos.X, cf2.Y+sz2.Y/2+0.9, pos.Z), Color=rgb(240,150,180), Material=Enum.Material.Grass}, F13)
      H.collider("hx_f13_vaso", V3(sz2.X+0.3, sz2.Y+2, sz2.Z+0.3), CF(pos.X, (sz2.Y+2)/2, pos.Z))
    end
    nAnel += 1
  end
end
say("anel do monumento:", nAnel, "pecas (lanterna/vaso alternados)")

-- ============ D) arvores do usuario ============
local nArv = 0
local function planta(nome, escala, pos)
  local giro = CFrame.Angles(0, math.rad(math.random(0,359)), 0)
  local m = cloneAt(nome, CF(pos)*giro, escala, F13)
  local cf2,sz2 = m:GetBoundingBox()
  H.collider("hx_f13_tronco", V3(2.2,8,2.2), CF(pos.X,pos.Y+4,pos.Z))
  nArv += 1
end
-- canteiros centrais: verde pequena em cima do canteiro
for _,p in ipairs(H.LAY.PLANTERS) do
  local topo = 0
  for _,q in ipairs(L.HEX_Canteiros:GetChildren()) do
    if q:IsA("BasePart") and math.abs(q.Position.X-p.X)<4.5 and math.abs(q.Position.Z-p.Z)<4.5 then
      topo = math.max(topo, q.Position.Y + q.Size.Y/2) end
  end
  planta("ARVORE_VERDE", 0.22, V3(p.X, math.max(topo-0.3,0), p.Z))
end
-- canteiros da forja: sakura
for _,p in ipairs(H.LAY.FORGE_BEDS) do planta("SAKURA", 1.15, V3(p.X, 0.6, p.Z)) end
-- entorno dos lagos e faces BL/BR (posicoes da F9)
local ARV = {
  {f="FL", s=-62, d=21, n="SAKURA", e=1.3}, {f="FL", s=22, d=23, n="SAKURA", e=1.1},
  {f="FL", s=-32, d=6.5, n="ARVORE_VERDE", e=0.35}, {f="FL", s=2, d=6.5, n="ARVORE_VERDE", e=0.3},
  {f="FR", s=-8, d=21, n="SAKURA", e=1.2}, {f="FR", s=60, d=21, n="SAKURA", e=1.3},
  {f="FR", s=16, d=6.5, n="ARVORE_VERDE", e=0.33}, {f="FR", s=42, d=6.5, n="ARVORE_VERDE", e=0.3},
  {f="BL", s=-34, d=8, n="SAKURA", e=1.2}, {f="BL", s=16, d=7, n="ARVORE_VERDE", e=0.33},
  {f="BR", s=34, d=8, n="SAKURA", e=1.2}, {f="BR", s=-16, d=7, n="ARVORE_VERDE", e=0.33},
}
for _,a in ipairs(ARV) do
  local pos = H.fp(a.f, a.s, a.d, 0)
  if livre(pos, 3) then planta(a.n, a.e, pos) end
end
-- quinas externas: sakuras grandes acima da muralha
local sMinX,sMaxX,sMinZ,sMaxZ = -182,182,-218,202
local R = 150/math.cos(math.rad(30))
for _,ang in ipairs({60,120,240,300}) do
  local a=math.rad(ang)
  local p=V3((R+16)*math.cos(a), -0.5, (R+16)*math.sin(a))
  if p.X>sMinX+8 and p.X<sMaxX-8 and p.Z>sMinZ+8 and p.Z<sMaxZ-8 then planta("SAKURA", 1.7, p) end
end
say("arvores plantadas:", nArv)

-- ============ E) fogo nos braseiros da forja ============
local nFogo = 0
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:lower():find("brase") and not d:FindFirstChildOfClass("ParticleEmitter") then
    local pe = Instance.new("ParticleEmitter")
    pe.Color = ColorSequence.new(rgb(255,180,70), rgb(255,90,30))
    pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,1.1), NumberSequenceKeypoint.new(1,0.2)})
    pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0,0.25), NumberSequenceKeypoint.new(1,1)})
    pe.Rate = 10 pe.Lifetime = NumberRange.new(0.7,1.2)
    pe.Speed = NumberRange.new(2.5,4) pe.SpreadAngle = Vector2.new(10,10)
    pe.LightEmission = 1 pe.Parent = d
    local pl = Instance.new("PointLight") pl.Range=11 pl.Brightness=1 pl.Color=rgb(255,140,60) pl.Shadows=false pl.Parent=d
    nFogo += 1
  end
end
say("braseiros acesos:", nFogo)

-- ============ F) lotus nos lagos ============
local nPad = 0
for _,w in ipairs(L.HEX_Lagos:GetDescendants()) do
  if w:IsA("BasePart") and w.Size.X>8 and w.Size.Z>8 and w.Size.Y<=2.5 then
    local c=w.Color
    if math.abs(c.R-C.agua.R)<0.12 and math.abs(c.G-C.agua.G)<0.12 and math.abs(c.B-C.agua.B)<0.12 then
      local top = w.Position.Y + w.Size.Y/2
      for i=1,6 do
        local p = w.CFrame:PointToWorldSpace(V3((math.random()-0.5)*(w.Size.X-5), 0, (math.random()-0.5)*(w.Size.Z-5)))
        local raio = 1.0 + math.random()*0.8
        H.part({Name="Vitoria", Class="Part", Shape=Enum.PartType.Cylinder,
          Size=V3(0.18, raio*2, raio*2), CFrame=CF(p.X, top+0.09, p.Z)*CFrame.Angles(0,math.rad(math.random(0,359)),math.rad(90)),
          Color=C.lirio, Material=Enum.Material.Grass}, F13)
        if i%2==1 then
          local fy = top+0.35
          H.part({Name="LotusBase", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.5,1.6,1.6),
            CFrame=CF(p.X, fy, p.Z)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(244,143,177)}, F13)
          H.part({Name="LotusMiolo", Class="Part", Shape=Enum.PartType.Ball, Size=V3(0.7,0.7,0.7),
            CFrame=CF(p.X, fy+0.35, p.Z), Color=rgb(255,214,98), Material=Enum.Material.Neon}, F13)
        end
        nPad += 1
      end
    end
  end
end
say("vitorias-regias/lotus:", nPad)

L:SetAttribute("HEX_F13_OK", true)
H.commit(rec)
say("marcador HEX_F13_OK gravado")
return "F13 OK\n"..table.concat(rep,"\n")