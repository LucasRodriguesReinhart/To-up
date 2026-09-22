-- hex_f14b_galeria.lua : F14b = cobertura da galeria dos portais (briefing secao 5).
-- Replica o cluster TEL_F1 do telhado da Forja (17 pecas, linguagem identica do kit)
-- sobre a colunata da galeria, com a cumeeira ao longo do comprimento (89 studs).
-- Sem chiwen/bestas (regra do usuario). Nada da galeria existente e alterado.
-- Idempotente: limpa HEX_F14B.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local V3, CF = Vector3.new, CFrame.new
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F14A_OK")==true, "F14b: rode a F14a antes")
local rec = H.begin("HEX F14b galeria")
local FB = H.folder(L,"HEX_F14B") H.clear(FB)

-- cluster de origem (telhado da Forja)
local pecas, cum = {}, nil
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:sub(1,6)=="TEL_F1" and not d:IsDescendantOf(FB) then
    table.insert(pecas, d)
    if d.Name=="TEL_F1_cumeeira" then cum=d end
  end
end
assert(cum and #pecas>=15, "F14b: cluster TEL_F1 nao achado ("..#pecas..")")
local C = cum.CFrame
local minY = math.huge
for _,p in ipairs(pecas) do minY = math.min(minY, p.Position.Y - p.Size.Y/2) end
say("cluster origem:", #pecas, "pecas, base em", ("%.2f"):format(minY))

-- alvo: topo da galeria (mesh SANT_galeria)
local gal
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="SANT_galeria" then gal=d break end
end
assert(gal, "F14b: SANT_galeria nao achada")
local topo = gal.Position.Y + gal.Size.Y/2 -- 32.38
local Grot = gal.CFrame - gal.CFrame.Position
-- cumeeira alvo: centro XZ da galeria, comprimento (local Z) recebe o eixo X do cluster
local yCum = C.Position.Y - minY + (topo - 0.5)
local T = CF(gal.Position.X, yCum, gal.Position.Z) * Grot * CFrame.Angles(0, math.rad(90), 0)
local rel = T * C:Inverse()
local n = 0
for _,p in ipairs(pecas) do
  local c = p:Clone()
  for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
  c:SetAttribute("HexGen", true)
  c.CanCollide=false c.CanQuery=false c.CanTouch=false c.Anchored=true
  c.CFrame = rel * p.CFrame
  c.Parent = FB
  n += 1
end
say("telhado montado sobre a galeria:", n, "pecas; cumeeira em Y", ("%.1f"):format(yCum))

L:SetAttribute("HEX_F14B_OK", true)
H.commit(rec)
return "F14b OK\n"..table.concat(rep,"\n")