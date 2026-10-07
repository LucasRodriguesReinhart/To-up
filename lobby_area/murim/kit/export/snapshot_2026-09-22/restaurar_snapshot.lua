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

-- 1) containers: resolucao por ORDEM DE DFS (mesma ordem da exportacao).
-- Resolver por caminho falha com nomes duplicados (FindFirstChild pega sempre o 1o)
-- e com nomes contendo ponto (split do GetFullName quebra) - defeitos achados no teste.
local RAIZES = {workspace:FindFirstChild("LOBBY_MURIM"), workspace:FindFirstChild("Santuario"),
  workspace:FindFirstChild("LojaMochilas"), workspace:FindFirstChild("NPCs")}
local vivos = {}
local function coleta(inst)
  if inst:IsA("Folder") or inst:IsA("Model") then
    table.insert(vivos, inst)
    for _, c in ipairs(inst:GetChildren()) do coleta(c) end
  end
end
for _, r in ipairs(RAIZES) do if r then coleta(r) end end
local conts = {}
local faltamC, desalinhados = 0, 0
for i, c in ipairs(idx.containers) do
  local nomeSnap = c[1]:match("([^%.]+)$") or c[1]
  local vivo = vivos[i]
  if vivo and vivo.Name == nomeSnap then
    conts[i] = vivo
  else
    -- estrutura mudou desde o snapshot: tenta achar por nome na vizinhanca da ordem
    conts[i] = nil
    local achou = false
    for k = math.max(1, i-3), math.min(#vivos, i+3) do
      if vivos[k] and vivos[k].Name == nomeSnap then conts[i] = vivos[k] achou = true break end
    end
    if not achou then faltamC += 1 else desalinhados += 1 end
  end
end
print(("containers: %d ausentes, %d desalinhados (estrutura mudou desde o snapshot)"):format(faltamC, desalinhados))
if faltamC + desalinhados > 10 then
  print("AVISO: muitos containers fora de ordem - o snapshot e de uma estrutura diferente; confira antes de reconstruir")
end

-- 2) pecas: verificar/reconstruir
local function cor(k) return Color3.fromRGB(k[1],k[2],k[3]) end
-- casamento por NOME + DISTANCIA (tolerancia 0.12): o snapshot arredonda a 2 casas
-- (erro ate 0.005) e chaves por balde de 0.1 flipavam ~14% das pecas (defeito achado
-- e provado no teste de restauracao; o metodo por distancia bateu 1:1 com o delta real).
local porNome = {}
for _, r in ipairs(RAIZES) do
  if r then
    for _, d in ipairs(r:GetDescendants()) do
      if d:IsA("BasePart") then
        local t = porNome[d.Name] if not t then t = {} porNome[d.Name] = t end
        table.insert(t, {d.Position, false})
      end
    end
  end
end
local faltam, criadas = 0, 0
for _, e in ipairs(parts) do
  local cf = CFrame.new(unpack(e.f))
  local pos = Vector3.new(cf.X, cf.Y, cf.Z)
  local achou = false
  local lista = porNome[e.n]
  if lista then
    for _, v in ipairs(lista) do
      if not v[2] and (v[1]-pos).Magnitude <= 0.12 then v[2] = true achou = true break end
    end
  end
  if not achou then
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