-- restaurar_snapshot.lua : reconstroi o layout do lobby a partir do snapshot serializado.
-- USO: python -m http.server 8766 na pasta snapshot_2026-09-22, depois rodar este script
-- no command bar (loadstring via GetAsync) em um place com os MESMOS assets de malha
-- (os MeshParts referenciam MeshId/TextureID na nuvem do Roblox e sao recriados por asset id).
-- MODO: "verificar" (padrao) so compara e relata divergencias; "reconstruir" cria o que falta.
local MODO = "verificar" -- mude para "reconstruir" para recriar pecas ausentes
local HttpService = game:GetService("HttpService")
local base = "http://127.0.0.1:8766/"
local idx = HttpService:JSONDecode(HttpService:GetAsync(base.."index_cena.json", true))
local parts = HttpService:JSONDecode(HttpService:GetAsync(base.."parts_tudo.json", true))
print("snapshot: "..#idx.containers.." containers, "..#parts.." pecas")

-- 1) containers: garante a arvore de Folders/Models
local porCaminho = {}
local function resolve(caminho, classe)
  if porCaminho[caminho] then return porCaminho[caminho] end
  local segs = {}
  for s in caminho:gmatch("[^%.]+") do table.insert(segs, s) end
  local atual = game
  for i, s in ipairs(segs) do
    local filho = (s=="Workspace") and workspace or atual:FindFirstChild(s)
    if not filho then
      if MODO=="reconstruir" then
        filho = Instance.new(i==#segs and classe or "Folder")
        filho.Name = s
        filho.Parent = atual
      else
        return nil
      end
    end
    atual = filho
  end
  porCaminho[caminho] = atual
  return atual
end
local conts = {}
local faltamC = 0
for i, c in ipairs(idx.containers) do
  conts[i] = resolve(c[1], c[2])
  if not conts[i] then faltamC += 1 end
end
print("containers ausentes: "..faltamC)

-- 2) pecas: verificar/reconstruir
local function cor(k) return Color3.fromRGB(k[1],k[2],k[3]) end
local existentes = {}
for i = 1, #idx.containers do -- NAO usar ipairs: conts pode ter buracos (nil) e ipairs pararia no primeiro
  local c = conts[i]
  if c then
    for _, f in ipairs(c:GetChildren()) do
      if f:IsA("BasePart") then
        local chave = i.."|"..f.Name.."|"..math.floor(f.Position.X*10).."|"..math.floor(f.Position.Y*10).."|"..math.floor(f.Position.Z*10)
        existentes[chave] = f
      end
    end
  end
end
local faltam, criadas = 0, 0
for _, e in ipairs(parts) do
  local cf = CFrame.new(unpack(e.f))
  local chave = e.p.."|"..e.n.."|"..math.floor(cf.X*10).."|"..math.floor(cf.Y*10).."|"..math.floor(cf.Z*10)
  if not existentes[chave] then
    faltam += 1
    if MODO=="reconstruir" and conts[e.p] then
      local p
      if e.c=="MeshPart" and e.mid and e.mid~="" then
        local ok, mp = pcall(function()
          return game:GetService("InsertService"):CreateMeshPartAsync(e.mid, Enum.CollisionFidelity.Box, Enum.RenderFidelity.Automatic)
        end)
        if ok then p = mp if e.tex then p.TextureID = e.tex end end
      end
      if not p then
        p = Instance.new(e.c=="MeshPart" and "Part" or e.c)
        if e.sh and p:IsA("Part") then p.Shape = Enum.PartType[e.sh] end
      end
      p.Name = e.n
      p.Anchored = true
      p.Size = Vector3.new(unpack(e.s))
      p.CFrame = cf
      p.Color = cor(e.k)
      p.Material = Enum.Material[e.m]
      p.Transparency = e.t or 0
      p.CanCollide = e.cc==1
      p.CanQuery = e.cc==1
      p.CanTouch = false
      p.Parent = conts[e.p]
      criadas += 1
    end
  end
end
print(("pecas do snapshot ausentes na cena: %d%s"):format(faltam, MODO=="reconstruir" and (" (recriadas: "..criadas..")") or ""))
print("OBS: luzes/particulas/scripts nao fazem parte do snapshot; rode os hex_*.lua para efeitos.")
return "restauracao ("..MODO..") concluida"