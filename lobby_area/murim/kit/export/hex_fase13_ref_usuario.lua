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

-- ============ A) tapetes com borda dourada (recortados nos medalhoes) ============
local MEDS = {{x=0, z=92, r=12}, {x=0, z=-55, r=10}}
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
      -- intervalos livres ao longo do eixo (o medalhao interrompe o caminho)
      local segs = {{-comp/2, comp/2}}
      for _,md in ipairs(MEDS) do
        local lp = fx.CFrame:PointToObjectSpace(V3(md.x, fx.Position.Y, md.z))
        local ax = aoLongoX and lp.X or lp.Z
        local lat = aoLongoX and lp.Z or lp.X
        if math.abs(lat) < curto/2 then
          local g1, g2 = ax-(md.r+0.8), ax+(md.r+0.8)
          local novo = {}
          for _,sv in ipairs(segs) do
            if g2<=sv[1] or g1>=sv[2] then table.insert(novo,sv) else
              if g1>sv[1] then table.insert(novo,{sv[1],g1}) end
              if g2<sv[2] then table.insert(novo,{g2,sv[2]}) end end
          end
          segs = novo
        end
      end
      for _,sv in ipairs(segs) do
        local len, mid = sv[2]-sv[1], (sv[1]+sv[2])/2
        if len >= 4 then
          local function faixa(nome, w, off, cor, mat, dy)
            local size = aoLongoX and V3(len, 0.06, w) or V3(w, 0.06, len)
            local ocf = aoLongoX and CF(mid, 0, off) or CF(off, 0, mid)
            H.part({Name=nome, Size=size, CFrame=fx.CFrame*ocf+V3(0, topo-fx.Position.Y+0.04+(dy or 0), 0),
              Color=cor, Material=mat or Enum.Material.Fabric}, F13)
          end
          -- niveis de detalhe: campo vermelho > campo interno escuro > borda ouro > losangos
          faixa("Tapete", wV, 0, VERMELHO_TAPETE)
          faixa("TapeteInterno", wV*0.62, 0, rgb(150,32,30), Enum.Material.Fabric, 0.035)
          faixa("TapeteBorda", 0.8, (wV/2+0.4), OURO, Enum.Material.SmoothPlastic)
          faixa("TapeteBorda", 0.8, -(wV/2+0.4), OURO, Enum.Material.SmoothPlastic)
          local nLos = math.floor((len-6)/9)
          for k=0,nLos do
            local off = mid - ((len-6)/2) + k*9
            local ocf = aoLongoX and CF(off,0,0) or CF(0,0,off)
            H.part({Name="TapeteLosango", Size=V3(1.5,0.04,1.5),
              CFrame=fx.CFrame*ocf*CFrame.Angles(0,math.rad(45),0)+V3(0, topo-fx.Position.Y+0.11, 0),
              Color=OURO, Material=Enum.Material.Metal}, F13)
          end
        end
      end
      nTap += 1
    end
  end
end
say("tapetes com borda dourada:", nTap, "faixas (recorte nos medalhoes)")

-- ============ B) medalhoes de piso ============
-- topo real das faixas cinzas (os medalhoes assentam SOBRE elas, nunca por baixo)
local topoFaixas = 0
for _,fx in ipairs(L:GetDescendants()) do
  if fx:IsA("BasePart") and fx.Parent.Name=="Faixas" then
    topoFaixas = math.max(topoFaixas, fx.Position.Y + fx.Size.Y/2)
  end
end
local OURO_VIVO = rgb(240,196,90)
local function medalhao(cx, cz, r)
  local y0 = topoFaixas + 0.02
  local function disco(nome, raio, camada, cor, mat)
    H.part({Name=nome, Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.06, raio*2, raio*2),
      CFrame=CF(cx, y0+camada*0.025, cz)*CFrame.Angles(0,0,math.rad(90)),
      Color=cor, Material=mat or Enum.Material.SmoothPlastic}, F13)
  end
  -- niveis: aro ouro > banda vermelha > filete ouro > anel escuro > campo claro > emblema
  disco("Med_aro",    r*1.05, 0, OURO_VIVO)
  disco("Med_banda",  r*0.97, 1, VERMELHO_TAPETE)
  disco("Med_filete", r*0.80, 2, OURO_VIVO)
  disco("Med_escuro", r*0.76, 3, rgb(66,78,96))
  disco("Med_campo",  r*0.62, 4, rgb(224,208,182))
  -- emblema: picareta em T, pecas CONECTADAS, dourado vivo
  local e = r*0.5
  local yE = y0 + 5*0.025
  local function barra(nome, sz, ocf)
    H.part({Name=nome, Size=sz, CFrame=CF(cx,yE,cz)*ocf, Color=OURO_VIVO, Material=Enum.Material.SmoothPlastic}, F13)
  end
  barra("Emb_cabo",   V3(1.35,0.05,e*1.55), CF(0,0,e*0.22))
  barra("Emb_cabeca", V3(e*1.30,0.05,1.35), CF(0,0,-e*0.48))
  for _,sg in ipairs({1,-1}) do
    barra("Emb_ponta", V3(e*0.5,0.05,1.15), CF(sg*e*0.78,0,-e*0.33)*CFrame.Angles(0,math.rad(-sg*38),0))
  end
  barra("Emb_no", V3(1.9,0.05,1.9), CF(0,0,-e*0.48)*CFrame.Angles(0,math.rad(45),0))
  -- 4 losangos sobre o anel escuro
  for k=0,3 do
    local a=math.rad(90*k+45)
    H.part({Name="Med_losango", Size=V3(1.3,0.05,1.3),
      CFrame=CF(cx,yE,cz)*CFrame.Angles(0,a,0)*CF(r*0.69,0,0)*CFrame.Angles(0,math.rad(45),0),
      Color=OURO_VIVO, Material=Enum.Material.SmoothPlastic}, F13)
  end
end
medalhao(0, 92, 12)    -- entre o portao e o monumento
medalhao(0, -55, 10)   -- adro da forja
-- anel vermelho ao redor do monumento, com filetes dourados por dentro e por fora
for k=0,23 do
  local a = math.rad(15*k)
  local function seg(nome, raio, w, cor, mat, dy)
    H.part({Name=nome, Size=V3(raio*math.rad(15)+0.35, 0.05, w),
      CFrame=CF(math.cos(a)*raio, 0.06+(dy or 0), math.sin(a)*raio)*CFrame.Angles(0,-a+math.rad(90),0),
      Color=cor, Material=mat or Enum.Material.Fabric}, F13)
  end
  seg("Anel_monumento", 26, 2.6, VERMELHO_TAPETE)
  seg("Anel_ouro", 27.7, 0.4, OURO, Enum.Material.Metal, 0.01)
  seg("Anel_ouro", 24.3, 0.4, OURO, Enum.Material.Metal, 0.01)
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
      -- buque em camadas: 3 tons de rosa + base verde (nada de bola unica)
      local fy = cf2.Y+sz2.Y/2
      H.part({Name="VasoVerde", Class="Part", Shape=Enum.PartType.Ball, Size=V3(3.2,1.4,3.2),
        CFrame=CF(pos.X, fy+0.3, pos.Z), Color=rgb(110,157,72), Material=Enum.Material.Grass}, F13)
      for _,fl in ipairs({{0.6,0.9,0,2.4,rgb(240,150,180)},{-0.8,1.1,0.5,2.0,rgb(248,178,200)},
                          {0.1,1.4,-0.7,1.7,rgb(230,120,160)},{-0.2,1.7,0.2,1.3,rgb(252,196,214)}}) do
        H.part({Name="VasoFlor", Class="Part", Shape=Enum.PartType.Ball, Size=V3(fl[4],fl[4]*0.8,fl[4]),
          CFrame=CF(pos.X+fl[1], fy+fl[2], pos.Z+fl[3]), Color=fl[5], Material=Enum.Material.Grass}, F13)
      end
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
for _,p in ipairs(H.LAY.FORGE_BEDS) do planta("SAKURA", 1.55, V3(p.X, 0.6, p.Z)) end -- 1.15 lia como moita
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
    pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0,1.7), NumberSequenceKeypoint.new(1,0.3)})
    pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0,0.15), NumberSequenceKeypoint.new(1,1)})
    pe.Rate = 16 pe.Lifetime = NumberRange.new(0.8,1.4)
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