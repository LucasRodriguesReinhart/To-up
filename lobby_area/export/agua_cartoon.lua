-- agua_cartoon.lua - troca o lago chapado do lobby por AGUA DE TERRENO no tom cartoon que o usuario pediu
-- (referencia: Blox Fruits). O terreno do jogo esta vazio (CountCells=0 quando medi), entao a cor global
-- da agua e so nossa e nao mexe em nenhuma area.
-- Por que terreno e nao MeshPart: a agua de terreno tem onda, refracao e reflexo de verdade. Um MeshPart
-- pintado nunca ia passar de um plano azul parado.
local T = workspace.Terrain
local lob = workspace:FindFirstChild("LOBBY_MURIM")
if not lob then return "LOBBY_MURIM nao encontrado" end

-- ---------- cor global da agua: ciano saturado, onda grande e devagar
T.WaterColor = Color3.fromRGB(33, 154, 220)
T.WaterTransparency = 0.62      -- 1 = vidro, 0 = opaca. 0.62 deixa ver o leito sem perder a cor
T.WaterWaveSize = 0.55          -- o maximo aceito e 1
T.WaterWaveSpeed = 9
T.WaterReflectance = 0.45

-- ---------- acha o lago pelas malhas que ja existem
local function pecas(nome)
  local t = {}
  for _, d in ipairs(lob:GetDescendants()) do
    if d:IsA("BasePart") and d.Name == nome then table.insert(t, d) end
  end
  return t
end
local function caixa(lista)
  if #lista == 0 then return nil end
  local mn, mx
  for _, p in ipairs(lista) do
    local a = p.Position - p.Size / 2
    local b = p.Position + p.Size / 2
    mn = mn and Vector3.new(math.min(mn.X, a.X), math.min(mn.Y, a.Y), math.min(mn.Z, a.Z)) or a
    mx = mx and Vector3.new(math.max(mx.X, b.X), math.max(mx.Y, b.Y), math.max(mx.Z, b.Z)) or b
  end
  return mn, mx
end

local out = {}
local espelho = pecas("LAGO_agua")
local leito = pecas("LAGO_leito")
local mn, mx = caixa(espelho)
if not mn then return "LAGO_agua nao encontrado" end

local _, leitoMx = caixa(leito)
local fundo = leitoMx and (leitoMx.Y - 3) or (mn.Y - 6)
local linha = mx.Y                                   -- a lamina d'agua fica onde estava o plano chapado

-- limpa agua anterior desta mesma regiao (o script pode rodar de novo sem empilhar)
local reg = Region3.new(Vector3.new(mn.X - 8, fundo - 8, mn.Z - 8), Vector3.new(mx.X + 8, linha + 8, mx.Z + 8)):ExpandToGrid(4)
T:ReplaceMaterial(reg, 4, Enum.Material.Water, Enum.Material.Air)

local centro = Vector3.new((mn.X + mx.X) / 2, (fundo + linha) / 2, (mn.Z + mx.Z) / 2)
local tam = Vector3.new(mx.X - mn.X, linha - fundo, mx.Z - mn.Z)
T:FillBlock(CFrame.new(centro), tam, Enum.Material.Water)
table.insert(out, string.format("lago: %.0f x %.0f studs, lamina em Y=%.1f, fundo em Y=%.1f", tam.X, tam.Z, linha, fundo))

-- o plano chapado sai de cena, mas continua no modelo caso o usuario queira voltar atras
for _, p in ipairs(espelho) do
  p.Transparency = 1
  p.CanCollide = false
  p.CanQuery = false
end
table.insert(out, "LAGO_agua (plano chapado) ficou invisivel: a agua agora e o terreno")

-- ---------- espelho do patio: pequeno demais para terreno (voxel de 4 studs faria serra na borda),
-- entao ele so ganha transparencia e reflexo para acompanhar o tom do lago
for _, p in ipairs(pecas("PATIO_agua")) do
  p.Transparency = 0.35
  p.Reflectance = 0.25
  table.insert(out, "PATIO_agua: transparencia 0.35, reflexo 0.25")
end

return table.concat(out, "\n")
