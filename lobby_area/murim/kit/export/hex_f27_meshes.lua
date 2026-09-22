-- hex_f27_meshes.lua : ART RESET - hero assets viram MALHA DE VERDADE (EditableMesh),
-- nao mais pilhas de Parts. Gera geometria custom dentro do Studio (sem FBX manual).
-- A) LAGO: contorno DESENHADO a mao (13 pontos de controle) -> Catmull-Rom -> poligono
--    concavo -> ear clipping -> prisma solido. Borda como anel de malha no MESMO contorno.
-- B) LONA da tenda: superficie parametrica continua (catenaria transversal + barriga entre
--    postes), uma malha curva por listra longitudinal (cor no MeshPart, nada de xadrez).
-- C) PadLoja deixa de ser piscina ciano (Part preservada, so a aparencia recua).
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
local L, C = H.L, H.C
local AS = game:GetService("AssetService")
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

local rec = H.begin("HEX F27 malhas")
local F27 = H.folder(L,"HEX_F27") H.clear(F27)

-- ================= helpers de malha =================
-- constroi MeshPart a partir de lista de vertices (V3, coords LOCAIS) e triangulos {i,j,k}
local function construir(verts, tris, nome, cor, material, parent, pivoWorld)
  -- CreateMeshPartAsync RECENTRA a geometria no bbox: compensar com o centro local
  local mn = V3(math.huge, math.huge, math.huge)
  local mx = V3(-math.huge, -math.huge, -math.huge)
  for _,v in ipairs(verts) do
    mn = V3(math.min(mn.X,v.X), math.min(mn.Y,v.Y), math.min(mn.Z,v.Z))
    mx = V3(math.max(mx.X,v.X), math.max(mx.Y,v.Y), math.max(mx.Z,v.Z))
  end
  local centro = (mn+mx)/2
  local em = AS:CreateEditableMesh()
  local ids = {}
  -- vertices RELATIVOS ao centro: a geometria carrega o offset absoluto e o CFrame
  -- somaria de novo (a lona ficava ao dobro da altura)
  for i,v in ipairs(verts) do ids[i] = em:AddVertex(v - centro) end
  local uv = em:AddUV(Vector2.new(0,0))
  -- EditableMesh exige NORMAIS explicitas; e o winding precisa apontar para FORA
  -- (sem isso as faces somem por culling - diagnosticado em teste isolado)
  for _,t in ipairs(tris) do
    local pa, pb, pc = verts[t[1]], verts[t[2]], verts[t[3]]
    if pa and pb and pc then
      local nor = (pb-pa):Cross(pc-pa)
      if nor.Magnitude > 1e-9 then
        -- direcao de referencia EXPLICITA (t[4]) quando dada; o palpite pelo centroide
        -- falha em faces planas e largas (componente horizontal domina)
        local fora = t[4]
        if not fora then
          local meio = (pa+pb+pc)/3
          fora = meio - centro
        end
        local a, b, c = t[1], t[2], t[3]
        if nor.Unit:Dot(fora.Unit) < 0 then b, c = t[3], t[2] nor = -nor end
        local nid = em:AddNormal(nor.Unit)
        local fid = em:AddTriangle(ids[a], ids[b], ids[c])
        em:SetFaceNormals(fid, {nid, nid, nid})
        em:SetFaceUVs(fid, {uv, uv, uv})
      end
    end
  end
  local mp = AS:CreateMeshPartAsync(Content.fromObject(em))
  mp.Name = nome
  mp.Anchored = true
  mp.CanCollide = false
  mp.CanQuery = false
  mp.CanTouch = false
  mp.Color = cor
  mp.Material = material or Enum.Material.SmoothPlastic
  mp:SetAttribute("HexGen", true)
  mp.CFrame = pivoWorld * CF(centro)
  mp.Parent = parent
  return mp
end

-- ear clipping para poligono 2D (lista de {x,z}), devolve triangulos de indices
local function areaSinal(p)
  local a = 0
  for i=1,#p do
    local j = (i % #p) + 1
    a = a + (p[i][1]*p[j][2] - p[j][1]*p[i][2])
  end
  return a/2
end
local function dentroTri(px,pz, ax,az, bx,bz, cx,cz)
  local d1 = (px-bx)*(az-bz) - (ax-bx)*(pz-bz)
  local d2 = (px-cx)*(bz-cz) - (bx-cx)*(pz-cz)
  local d3 = (px-ax)*(cz-az) - (cx-ax)*(pz-az)
  local neg = (d1<0) or (d2<0) or (d3<0)
  local pos = (d1>0) or (d2>0) or (d3>0)
  return not (neg and pos)
end
local function earClip(poly)
  local idx = {}
  local n = #poly
  local ccw = areaSinal(poly) > 0
  for i=1,n do idx[i] = ccw and i or (n-i+1) end
  local tris = {}
  local guard = 0
  while #idx > 3 and guard < 4000 do
    guard = guard + 1
    local achou = false
    for k=1,#idx do
      local i0 = idx[((k-2) % #idx) + 1]
      local i1 = idx[k]
      local i2 = idx[(k % #idx) + 1]
      local ax,az = poly[i0][1], poly[i0][2]
      local bx,bz = poly[i1][1], poly[i1][2]
      local cx,cz = poly[i2][1], poly[i2][2]
      local cross = (bx-ax)*(cz-az) - (bz-az)*(cx-ax)
      if cross > 0 then -- convexo
        local ok = true
        for _,m in ipairs(idx) do
          if m~=i0 and m~=i1 and m~=i2 then
            if dentroTri(poly[m][1], poly[m][2], ax,az, bx,bz, cx,cz) then ok=false break end
          end
        end
        if ok then
          table.insert(tris, {i0,i1,i2})
          table.remove(idx, k)
          achou = true
          break
        end
      end
    end
    if not achou then break end
  end
  if #idx == 3 then table.insert(tris, {idx[1], idx[2], idx[3]}) end
  return tris
end
-- Catmull-Rom fechada
local function suavizar(ctrl, porTrecho)
  local out = {}
  local n = #ctrl
  for i=1,n do
    local p0 = ctrl[((i-2) % n) + 1]
    local p1 = ctrl[i]
    local p2 = ctrl[(i % n) + 1]
    local p3 = ctrl[((i+1) % n) + 1]
    for s=0,porTrecho-1 do
      local t = s/porTrecho
      local t2, t3 = t*t, t*t*t
      local x = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
      local z = 0.5*((2*p1[2]) + (-p0[2]+p2[2])*t + (2*p0[2]-5*p1[2]+4*p2[2]-p3[2])*t2 + (-p0[2]+3*p1[2]-3*p2[2]+p3[2])*t3)
      table.insert(out, {x,z})
    end
  end
  return out
end
-- prisma solido a partir de poligono (topo em yTop, fundo em yBot)
local function prisma(poly, tris, yTop, yBot)
  local verts, faces = {}, {}
  local n = #poly
  for i=1,n do verts[i] = V3(poly[i][1], yTop, poly[i][2]) end
  for i=1,n do verts[n+i] = V3(poly[i][1], yBot, poly[i][2]) end
  local UP, DN = V3(0,1,0), V3(0,-1,0)
  for _,t in ipairs(tris) do table.insert(faces, {t[1], t[2], t[3], UP}) end        -- topo
  for _,t in ipairs(tris) do table.insert(faces, {n+t[3], n+t[2], n+t[1], DN}) end  -- fundo
  for i=1,n do
    local j = (i % n) + 1
    local ax, az = poly[i][1], poly[i][2]
    local bx, bz = poly[j][1], poly[j][2]
    local tx, tz = bx-ax, bz-az
    local m = math.sqrt(tx*tx+tz*tz) if m<1e-9 then m=1 end
    local fora = V3(tz/m, 0, -tx/m)   -- perpendicular horizontal a aresta
    table.insert(faces, {i, n+i, n+j, fora})
    table.insert(faces, {i, n+j, j, fora})
  end
  return verts, faces
end

-- ================= A) LAGO =================
-- contorno DESENHADO (coords de face FL: s ao longo do muro, d para dentro)
local CTRL = {
  {-72, 15}, {-64, 27}, {-52, 35}, {-38, 37},
  {-29, 28},                      -- concavidade (entra)
  {-17, 34}, {-3, 34}, {9, 28},
  {16, 19},                       -- estreitamento/ponta leste
  {7, 11}, {-12, 8}, {-38, 6}, {-58, 9},
}
local poly = suavizar(CTRL, 5)   -- 65 pontos
local tris = earClip(poly)
say("lago: contorno de", #CTRL, "pontos ->", #poly, "vertices, ear clipping ->", #tris, "triangulos")
-- limpa lago anterior
for _,nome in ipairs({"HEX_F26","HEX_F24","HEX_F22"}) do
  local f = L:FindFirstChild(nome)
  if f then
    for _,p in ipairs(f:GetChildren()) do
      local n = p.Name
      if n:sub(1,4)=="Lago" or n:sub(1,7)=="B_Agua_" or n:sub(1,6)=="B_Aro_" or n=="Vitoria" or n=="BancoPatamar" then p:Destroy() end
    end
  end
end
-- referencial: converte (s,d) local -> mundo pela face FL
local REF = H.faceCF("FL", 0, 0, 0)
-- superficie da agua com FACES DUPLAS (visivel dos dois lados: imune a culling)
local vA, fA = {}, {}
for i=1,#poly do vA[i] = V3(poly[i][1], 0.30, poly[i][2]) end
for _,t in ipairs(tris) do
  table.insert(fA, {t[1], t[2], t[3], V3(0,1,0)})
  table.insert(fA, {t[1], t[3], t[2], V3(0,-1,0)})
end
local _unused1, _unused2 = prisma(poly, tris, 0.30, -1.30)
-- Glass com transparencia 0 fica quase invisivel no Roblox: usar SmoothPlastic translucido
local agua = construir(vA, fA, "LagoAgua", rgb(64,170,196), Enum.Material.SmoothPlastic, F27, REF)
agua.Transparency = 0.12
agua.Reflectance = 0.06
-- borda: anel entre o contorno e um offset externo
local polyOut = {}
for i=1,#poly do
  local a = poly[((i-2) % #poly) + 1]
  local b = poly[i]
  local c = poly[(i % #poly) + 1]
  local tx, tz = c[1]-a[1], c[2]-a[2]
  local m = math.sqrt(tx*tx + tz*tz)
  if m < 1e-6 then m = 1 end
  polyOut[i] = {b[1] + (tz/m)*2.4, b[2] - (tx/m)*2.4}
end
local vB, fB = {}, {}
local n = #poly
for i=1,n do
  vB[i]       = V3(poly[i][1],    0.44, poly[i][2])
  vB[n+i]     = V3(polyOut[i][1], 0.44, polyOut[i][2])
  vB[2*n+i]   = V3(poly[i][1],   -0.5,  poly[i][2])
  vB[3*n+i]   = V3(polyOut[i][1], -0.5, polyOut[i][2])
end
local UPv, DNv = V3(0,1,0), V3(0,-1,0)
local function quadDuplo(a,b,c,d, dir)   -- faces duplas: imune a culling
  table.insert(fB, {a,b,c, dir});  table.insert(fB, {a,c,d, dir})
  table.insert(fB, {a,c,b, -dir}); table.insert(fB, {a,d,c, -dir})
end
for i=1,n do
  local j = (i % n) + 1
  local tx, tz = poly[j][1]-poly[i][1], poly[j][2]-poly[i][2]
  local m = math.sqrt(tx*tx+tz*tz) if m<1e-9 then m=1 end
  local fora = V3(tz/m, 0, -tx/m)
  quadDuplo(i, n+i, n+j, j, UPv)             -- topo do anel de pedra
  quadDuplo(n+i, 3*n+i, 3*n+j, n+j, fora)    -- parede externa
  quadDuplo(j, 2*n+j, 2*n+i, i, -fora)       -- parede interna (para a agua)
end
construir(vB, fB, "LagoBorda", rgb(178,169,156), Enum.Material.Slate, F27, REF)
say("lago: agua + borda como malhas unicas seguindo o mesmo contorno")

-- rochas e vitorias reposicionadas PELO NOVO CONTORNO (as antigas seguiam a elipse)
local F26b = L:FindFirstChild("HEX_F26")
local rochaFonte
for _,pasta in ipairs({F26b, H.SS:FindFirstChild("F24_REMOVIDOS")}) do
  if pasta and not rochaFonte then
    for _,c in ipairs(pasta:GetDescendants()) do
      if c:IsA("MeshPart") and c.Name:sub(1,9)=="LOB_rocha" then rochaFonte=c break end
    end
  end
end
if F26b then
  for _,c in ipairs(F26b:GetChildren()) do
    if c:IsA("MeshPart") and c.Name:sub(1,9)=="LOB_rocha" then c:Destroy() end
    if c.Name=="Vitoria" or c.Name=="QuedaPedra" or c.Name=="QuedaLamina" or c.Name=="QuedaEspuma" then c:Destroy() end
  end
end
if rochaFonte then
  for _,r in ipairs({{i=8, e=1.5}, {i=30, e=1.0}, {i=52, e=0.62}}) do
    local p = poly[r.i]
    local c = rochaFonte:Clone()
    for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
    c:SetAttribute("HexGen",true)
    c.Size = rochaFonte.Size*r.e
    c.Color = rgb(174,166,150)
    c.Material = Enum.Material.Slate
    c.Anchored=true c.CanCollide=false c.CanQuery=false c.CanTouch=false
    c.CFrame = (REF*CF(p[1], c.Size.Y/2-0.7, p[2]))*CFrame.Angles(0,math.rad(40*r.i),0)
    c.Parent = F27
  end
end
-- vitorias-regias dentro do poligono (amostra em torno de pontos internos conhecidos)
for _,v in ipairs({{-52,24},{-44,29},{-20,25},{-8,26},{4,22},{-33,17},{-60,18}}) do
  H.part({Name="Vitoria", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.14,2.4,2.4),
    CFrame=(REF*CF(v[1], 0.36, v[2]))*CFrame.Angles(0,math.rad(math.random(0,359)),math.rad(90)),
    Color=C.lirio, Material=Enum.Material.Grass}, F27)
end
-- piso de preenchimento antigo do leito retangular: some sob a agua nova
local F22b = L:FindFirstChild("HEX_F22")
if F22b then
  local pf = F22b:FindFirstChild("B_PisoFL")
  -- fica no nivel do piso (rebaixar abria um buraco visivel ao lado da agua)
  if pf then pf.Color = rgb(190,166,132) pf.Material = Enum.Material.Pavement pf.CFrame = CF(pf.Position.X, -0.55, pf.Position.Z) end
end

-- ================= B) LONA DA TENDA =================
local S = L:GetAttribute("F22_LojaCF")
local chao = 7.98
local F26 = L:FindFirstChild("HEX_F26")
if F26 then
  for _,p in ipairs(F26:GetChildren()) do
    local n = p.Name
    if n=="TendaTecido" or n=="TendaAba" or n=="TendaValance" or n=="TendaCumeeira" then p:Destroy() end
  end
end
-- superficie: catenaria transversal + leve barriga entre os postes (lz = -9.6, 0, 9.6)
-- beira pousa EXATAMENTE na travessa (chao+7.2); cume 2.2 acima dela
-- LARG/COMP acompanham a tenda ~32% maior
local RIDGE, QUEDA, LARG = chao+9.7, 2.5, 11.6
local COMP = 28.0
local function alturaLona(lx, lz)
  local y = RIDGE - QUEDA*((math.abs(lx)/LARG)^1.7)
  local fase = (lz + COMP/2) / (COMP/2)      -- 0..2 entre os 3 postes (lz = -12.6, 0, 12.6)
  local frac = fase % 1
  local sag = 0.42 * math.sin(math.pi*frac) * (1 - (math.abs(lx)/LARG)*0.45)
  return y - sag
end
local ESP = 0.22
local NU, NV = 8, 7            -- por listra: 8 divisoes no comprimento, 7 na queda
local NLISTRA = 8
local corA, corB = rgb(190,54,46), rgb(30,88,96)
for li=0,NLISTRA-1 do
  local z0 = -COMP/2 + li*(COMP/NLISTRA)
  local z1 = z0 + (COMP/NLISTRA)
  local verts, faces = {}, {}
  local function idx(iu, iv, camada) return camada*(NU+1)*(2*NV+1) + iu*(2*NV+1) + iv + 1 end
  for camada=0,1 do
    local dy = (camada==0) and 0 or -ESP
    for iu=0,NU do
      local lz = z0 + (z1-z0)*(iu/NU)
      for iv=0,2*NV do
        local lx = -LARG + (2*LARG)*(iv/(2*NV))
        verts[idx(iu,iv,camada)] = V3(lx, alturaLona(lx,lz)+dy, lz)
      end
    end
  end
  local UPl, DNl = V3(0,1,0), V3(0,-1,0)
  for iu=0,NU-1 do
    for iv=0,2*NV-1 do
      local a,b,c,d = idx(iu,iv,0), idx(iu+1,iv,0), idx(iu+1,iv+1,0), idx(iu,iv+1,0)
      table.insert(faces,{a,b,c,UPl}) table.insert(faces,{a,c,d,UPl})
      local e,f,g,h = idx(iu,iv,1), idx(iu+1,iv,1), idx(iu+1,iv+1,1), idx(iu,iv+1,1)
      table.insert(faces,{e,g,f,DNl}) table.insert(faces,{e,h,g,DNl})
    end
  end
  -- bordas (costura das duas camadas)
  for iu=0,NU-1 do
    for _,iv in ipairs({0, 2*NV}) do
      local a,b = idx(iu,iv,0), idx(iu+1,iv,0)
      local c,d = idx(iu,iv,1), idx(iu+1,iv,1)
      if iv==0 then table.insert(faces,{a,c,d}) table.insert(faces,{a,d,b})
      else table.insert(faces,{a,d,c}) table.insert(faces,{a,b,d}) end
    end
  end
  for iv=0,2*NV-1 do
    for _,iu in ipairs({0, NU}) do
      local a,b = idx(iu,iv,0), idx(iu,iv+1,0)
      local c,d = idx(iu,iv,1), idx(iu,iv+1,1)
      if iu==0 then table.insert(faces,{a,b,d}) table.insert(faces,{a,d,c})
      else table.insert(faces,{a,d,b}) table.insert(faces,{a,c,d}) end
    end
  end
  construir(verts, faces, "LonaListra", (li%2==0) and corA or corB, Enum.Material.Fabric, F27, S*CF(0,-13.28,0))
  -- barrado pendente na beira de cada listra (frente e fundo da lona)
  for _,lado in ipairs({1,-1}) do
    local yB = alturaLona(lado*LARG, (z0+z1)/2)
    H.part({Name="LonaBarrado", Size=V3(0.25, 1.25, (z1-z0)*0.92),
      CFrame=S*CF(lado*(LARG-0.1), (yB-0.62)-13.28, (z0+z1)/2),
      Color=(li%2==0) and corA or corB, Material=Enum.Material.Fabric}, F27)
  end
end
say("lona: ", NLISTRA, "listras curvas continuas (malha, nao blocos)")

-- ================= C) PadLoja discreto =================
local pad = workspace:FindFirstChild("LojaMochilas")
pad = pad and pad:FindFirstChild("PadLoja")
if pad then
  if pad:GetAttribute("F27_Cor")==nil then
    pad:SetAttribute("F27_Cor", pad.Color)
    pad:SetAttribute("F27_Mat", pad.Material.Name)
    pad:SetAttribute("F27_Tr", pad.Transparency)
  end
  pad.Color = rgb(196,178,150)
  pad.Material = Enum.Material.Slate
  pad.Transparency = 0.25
  say("PadLoja integrado ao piso (funcao preservada, aparencia recuada)")
end

-- banco do lago retirado (o usuario pediu para avaliar o jardim sem ele)
local REM = H.SS:FindFirstChild("F24_REMOVIDOS") or H.SS
local nBanco = 0
for _,d in ipairs(L:GetDescendants()) do
  if d.Name=="VIL_banco" and d:IsA("BasePart") then
    d.Parent = H.folder(REM, "Bancos") nBanco += 1
  end
end
say("bancos retirados:", nBanco)

L:SetAttribute("HEX_F27_OK", true)
H.commit(rec)
return "F27 OK\n"..table.concat(rep,"\n")