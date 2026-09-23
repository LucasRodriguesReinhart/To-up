-- hex_f29_compactar.lua : compacta o hexagono (apotema 150 -> 125).
-- Move RADIALMENTE para dentro tudo que forma o anel externo: muralha, torres, portao/
-- gatehouse e o conjunto da Forja (que fica encostado na muralha norte).
-- NAO move: piso, penhascos, chao externo, ponte de saida (ancora os corredores),
-- nem os elementos internos (monumento, tenda, lago, leaderboards, treino) que ja estao
-- no raio ~100 depois da F28.
-- Segmentos de muralha que sobram nas quinas (o perimetro encolhe) vao para o storage.
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
local L = H.L
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

if L:GetAttribute("HEX_F29_OK") == true then return "F29 ja aplicado (compactacao e movimento unico)" end
local rec = H.begin("HEX F29 compactar")
local REC = 25                       -- quanto o anel externo vem para dentro
local NOVO_AP = 150 - REC            -- 125
local dest = SS:FindFirstChild("F29_EXCEDENTE") or (function() local f=Instance.new("Folder") f.Name="F29_EXCEDENTE" f.Parent=SS return f end)()

-- fatia de face para um ponto (qual das 6 faces ele pertence) e coords (s,d)
local FACES = {"FR","F","FL","BL","B","BR"}
local function faceDe(pos)
  local ang = math.deg(math.atan2(pos.Z, pos.X)) % 360
  local melhor, md = nil, 999
  for _,f in ipairs(FACES) do
    local fa = H.FACES[f].th % 360
    local d = math.abs(((ang - fa + 180) % 360) - 180)
    if d < md then md, melhor = d, f end
  end
  return melhor, md
end

-- 1) MURALHA + TORRES
local mur = L:FindFirstChild("HEX_Muralha")
local nMov, nEx = 0, 0
if mur then
  for _,grupo in ipairs(mur:GetChildren()) do
    local ehTorre = grupo.Name:sub(1,5)=="Torre"
    local pecas = {}
    if grupo:IsA("Model") then
      table.insert(pecas, grupo)
    else
      for _,p in ipairs(grupo:GetChildren()) do table.insert(pecas, p) end
    end
    for _,p in ipairs(pecas) do
      local pos = p:IsA("Model") and p:GetPivot().Position or p.Position
      local f = faceDe(pos)
      if ehTorre then
        -- torres ficam nas QUINAS: puxar radialmente pelo proprio vetor
        local dir = V3(pos.X, 0, pos.Z)
        if dir.Magnitude > 1 then
          local d = dir.Unit * REC
          if p:IsA("Model") then p:PivotTo(p:GetPivot() - d) else p.CFrame = p.CFrame - d end
          nMov += 1
        end
      else
        local F = H.FACES[f]
        local lp = H.faceCF(f,0,0,0):PointToObjectSpace(pos)
        local sNovo = lp.X * (NOVO_AP/150)     -- encolhe o comprimento da face junto
        local meiaFace = NOVO_AP * math.tan(math.rad(30))
        if math.abs(sNovo) > meiaFace - 2 then
          if p:GetAttribute("OrigemPath")==nil then p:SetAttribute("OrigemPath", p.Parent:GetFullName()) end
          p.Parent = dest
          nEx += 1
        else
          local alvo = H.faceCF(f, sNovo, lp.Z, 0)
          local delta = alvo.Position - V3(pos.X, 0, pos.Z)
          if p:IsA("Model") then p:PivotTo(p:GetPivot() + delta) else p.CFrame = p.CFrame + delta end
          nMov += 1
        end
      end
    end
  end
end
say(("muralha: %d pecas puxadas %d studs (apotema %d), %d excedentes arquivadas"):format(nMov, REC, NOVO_AP, nEx))

-- colliders da muralha acompanham
local nCol = 0
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name:find("muro") or c.Name:find("costura") then
    local pos = c.Position
    local f = faceDe(pos)
    local lp = H.faceCF(f,0,0,0):PointToObjectSpace(pos)
    local sNovo = lp.X * (NOVO_AP/150)
    local alvo = H.faceCF(f, sNovo, lp.Z, 0)
    c.CFrame = c.CFrame + (alvo.Position - V3(pos.X,0,pos.Z))
    nCol += 1
  end
end
say("colliders de muralha movidos:", nCol)

-- 2) PORTAO / GATEHOUSE (face F, +Z) - desce REC em Z; a ponte NAO se move
local nPort = 0
local function moverZ(lista, dz, filtro)
  for _,p in ipairs(lista) do
    if not filtro or filtro(p) then
      if p:IsA("Model") then p:PivotTo(p:GetPivot() + V3(0,0,dz))
      elseif p:IsA("BasePart") then p.CFrame = p.CFrame + V3(0,0,dz) end
      nPort += 1
    end
  end
end
local Portao = L:FindFirstChild("Portao")
if Portao then moverZ(Portao:GetChildren(), -REC) end
local F25 = L:FindFirstChild("HEX_F25")
if F25 then moverZ(F25:GetChildren(), -REC) end
local F23 = L:FindFirstChild("HEX_F23")
if F23 then
  moverZ(F23:GetChildren(), -REC, function(p)
    return p:IsA("BasePart") and p.Position.Z > 120
  end)
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Position.Z > 120 and c.Position.Z < 175 then c.CFrame = c.CFrame + V3(0,0,-REC) nPort += 1 end
end
say("portao/gatehouse movido:", nPort, "pecas")

-- 3) FORJA (face B, -Z) - sobe REC em Z junto com terraco, escadaria e props
local nForja = 0
local function moverForja(root, filtro)
  for _,p in ipairs(root:GetChildren()) do
    local pos = p:IsA("Model") and p:GetPivot().Position or (p:IsA("BasePart") and p.Position)
    if pos and pos.Z < -70 and (not filtro or filtro(p, pos)) then
      if p:IsA("Model") then p:PivotTo(p:GetPivot() + V3(0,0,REC))
      else p.CFrame = p.CFrame + V3(0,0,REC) end
      nForja += 1
    end
  end
end
local semPenhasco = function(p, pos)
  return p.Name:sub(1,12) ~= "LOB_penhasco" and pos.Y > -25
end
moverForja(L:FindFirstChild("Forja") or L, semPenhasco)
for _,nome in ipairs({"Patio","Props","HEX_Detalhes","HEX_F14E","HEX_F19"}) do
  local f = L:FindFirstChild(nome)
  if f then moverForja(f, semPenhasco) end
end
local NPCs = workspace:FindFirstChild("NPCs")
if NPCs then
  for _,p in ipairs(NPCs:GetChildren()) do
    local pos = p:IsA("Model") and p:GetPivot().Position or nil
    if pos and pos.Z < -70 then p:PivotTo(p:GetPivot() + V3(0,0,REC)) nForja += 1 end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Position.Z < -70 and c.Position.Y > -25 then c.CFrame = c.CFrame + V3(0,0,REC) nForja += 1 end
end
say("forja/terraco/Ignis movidos:", nForja, "pecas")

L:SetAttribute("HEX_F29_OK", true)
H.commit(rec)
return "F29 OK\n"..table.concat(rep,"\n")