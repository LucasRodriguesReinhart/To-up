-- hex_f14a_limpeza.lua : F14a = reducao de poluicao visual (briefing 2026-09-22).
-- Arvores: 17 -> 7 (mantem: 2 sakuras da forja, 1 sakura por lago, 4 sakuras externas de quina).
-- Remove: 4 verdes dos canteiros centrais, 4 verdes lago-muralha, 4 arvores BL/BR, 2 sakuras de lago.
-- Estandartes P1: mantem no maximo 3 por face (remove alternados).
-- Petalas: 4 -> 2 emissores. Cachoeiras: remove as 4 laterais (agua concentrada na frente).
-- Arvores torcidas antigas (JAR/bonsai) perto das muralhas: REMOVIDAS para ServerStorage (recuperavel).
-- Tudo movido para ServerStorage.F14_REMOVIDOS (nao destruido).
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local SS = H.SS
local V3 = Vector3.new
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F13_OK")==true, "F14a: F13 ausente")
local rec = H.begin("HEX F14a limpeza")
local REM = SS:FindFirstChild("F14_REMOVIDOS") or (function() local f=Instance.new("Folder") f.Name="F14_REMOVIDOS" f.Parent=SS return f end)()
local function tira(obj, motivo)
  if obj and obj.Parent~=REM then obj.Parent=REM return 1 end
  return 0
end
local function posDe(m) return m:IsA("Model") and m:GetPivot().Position or m.Position end

-- ============ arvores da F13 ============
local REMOVER = {}
for _,p in ipairs(H.LAY.PLANTERS) do table.insert(REMOVER, V3(p.X,0,p.Z)) end       -- 4 verdes canteiros
for _,a in ipairs({{"FL",-32,6.5},{"FL",2,6.5},{"FR",16,6.5},{"FR",42,6.5},          -- verdes lago-muralha
                   {"BL",-34,8},{"BL",16,7},{"BR",34,8},{"BR",-16,7},                -- BL/BR
                   {"FL",22,23},{"FR",-8,21}}) do                                    -- 2 sakuras de lago
  table.insert(REMOVER, H.fp(a[1],a[2],a[3],0))
end
local nArv, nCol = 0, 0
for _,m in ipairs(L.HEX_F13:GetChildren()) do
  if m:IsA("Model") and (m.Name=="SAKURA" or m.Name=="ARVORE_VERDE") then
    local p = posDe(m)
    for _,r in ipairs(REMOVER) do
      if math.abs(p.X-r.X)<5 and math.abs(p.Z-r.Z)<5 then nArv+=tira(m,"arvore") break end
    end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name=="hx_f13_tronco" then
    local p=c.Position
    for _,r in ipairs(REMOVER) do
      if math.abs(p.X-r.X)<5 and math.abs(p.Z-r.Z)<5 then c:Destroy() nCol+=1 break end
    end
  end
end
say("arvores removidas:", nArv, "(+", nCol, "colliders)")

-- ============ arvores torcidas antigas (fora de estilo) ============
local nJar = 0
for _,d in ipairs(L:GetDescendants()) do
  if (d:IsA("Model") or d:IsA("MeshPart")) and d.Parent and d.Parent.Parent then
    local nm = d.Name:upper()
    if nm:sub(1,3)=="JAR" and not d:IsDescendantOf(REM) then
      -- so as que estao no patio (perto das muralhas FL/FR), nao as da biblioteca
      local ok, p = pcall(posDe, d)
      if ok and p.Y > -5 and p.Y < 30 and d:IsDescendantOf(L) then nJar += tira(d,"jar") end
    end
  end
end
say("arvores/bonsai antigos JAR removidos:", nJar)

-- ============ estandartes P1: max 3 por face ============
local porFace = {}
for _,m in ipairs(L.HEX_P1:GetChildren()) do
  if m.Name=="KIT_estandarte" or (m:IsA("Model") and m.Name:find("estandarte")) then
    local p = posDe(m)
    local ang = math.deg(math.atan2(p.Z, p.X))%360
    local face = math.floor(((ang+30)%360)/60) -- 0..5
    porFace[face] = porFace[face] or {}
    table.insert(porFace[face], {m=m, s=p.X*math.cos(math.rad(face*60+90))+p.Z*math.sin(math.rad(face*60+90))})
  end
end
local nEst = 0
for _,lista in pairs(porFace) do
  table.sort(lista, function(a,b) return a.s<b.s end)
  if #lista > 3 then
    -- remove alternados ate sobrar 3
    local alvo = #lista - 3
    local rem = 0
    for i=2,#lista,2 do
      if rem < alvo then nEst += tira(lista[i].m,"estandarte") rem += 1 end
    end
  end
end
say("estandartes removidos:", nEst)

-- ============ petalas e cachoeiras ============
local nPet, nCas = 0, 0
for _,e in ipairs(L.HEX_P2:GetChildren()) do
  if e.Name=="P2_petalas_3" or e.Name=="P2_petalas_4" then nPet += tira(e,"petala") end
end
-- cachoeiras laterais: pecas com |X| > 150 (as da frente ficam, z=202)
for _,e in ipairs(L.HEX_P2:GetChildren()) do
  if e.Name:sub(1,7)=="P2_qued" or e.Name=="P2_filete" or e.Name=="P2_espuma" or e.Name=="P2_lingua" then
    if math.abs(e.Position.X) > 150 then nCas += tira(e,"cascata") end
  end
end
say("petalas removidas:", nPet, "; pecas de cachoeira lateral:", nCas)

L:SetAttribute("HEX_F14A_OK", true)
H.commit(rec)
say("marcador HEX_F14A_OK gravado; itens recuperaveis em ServerStorage.F14_REMOVIDOS")
return "F14a OK\n"..table.concat(rep,"\n")