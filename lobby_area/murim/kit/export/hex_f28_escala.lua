-- hex_f28_escala.lua : escala e distribuicao (NAO e escala global - e reorganizacao).
-- Diagnostico: monumento no centro (0) e TODOS os servicos no anel 125..140; o miolo
-- 25..100, que e onde o jogador anda, estava vazio. Solucao: puxar os servicos para
-- o anel ~100 e aumentar a loja.
-- 1) LOJA: conjunto inteiro puxado 34 studs para o centro + tenda ~32% maior em footprint.
-- 2) LEADERBOARDS: area nova a 100 do centro, 4 paineis grandes (top 5 cada) no formato
--    da referencia (Rank / Player / Amount), com moldura de madeira e base de pedra.
-- 3) LAGO: puxado 18 studs para o centro (continua no lado direito).
-- Nada de monumento/Forja/portais/galeria/Ignis.
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
H.selfTest()
local L, C = H.L, H.C
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end
local rec = H.begin("HEX F28 escala e distribuicao")

-- ============ 1) LOJA: puxar o conjunto para o centro ============
local S0 = L:GetAttribute("F22_LojaCF")
assert(S0, "F28: F22_LojaCF ausente")
local dirCentro = V3(-S0.Position.X, 0, -S0.Position.Z).Unit
local PUXA = 34
local delta = dirCentro * PUXA
local novoS = S0 + delta

if L:GetAttribute("F28_LojaMovida") ~= true then
  -- tudo na regiao da loja anda junto (inclui patamar, pad, mochilas, mesas, colliders)
  local alvos = {}
  local function coletar(root, filtro)
    for _,d in ipairs(root:GetDescendants()) do
      if d:IsA("BasePart") and (not filtro or filtro(d)) then
        local p = d.Position
        if p.X<-92 and p.X>-150 and p.Z<-26 and p.Z>-80 then table.insert(alvos, d) end
      end
    end
  end
  coletar(L)
  local lm = workspace:FindFirstChild("LojaMochilas")
  if lm then for _,d in ipairs(lm:GetDescendants()) do if d:IsA("BasePart") then table.insert(alvos,d) end end end
  -- deduplica por peca que pertence a Model (mover a Model uma vez so)
  local models = {}
  for _,d in ipairs(alvos) do
    local m = d:FindFirstAncestorOfClass("Model")
    if m and m ~= L and m.Parent ~= workspace then models[m] = true end
  end
  local movidas = 0
  for _,d in ipairs(alvos) do
    local m = d:FindFirstAncestorOfClass("Model")
    if not (m and models[m]) then d.CFrame = d.CFrame + delta movidas += 1 end
  end
  for m,_ in pairs(models) do m:PivotTo(m:GetPivot() + delta) movidas += 1 end
  -- NPC vendedor
  local npc
  for _,c in ipairs(workspace:GetChildren()) do if c.Name:match("^npc vendedor") then npc=c break end end
  if npc then npc:PivotTo(npc:GetPivot() + delta) movidas += 1 end
  L:SetAttribute("F22_LojaCF", novoS)
  L:SetAttribute("F28_LojaMovida", true)
  say(("loja puxada %d studs para o centro: %d objetos (raio %.0f -> %.0f)"):format(
    PUXA, movidas, S0.Position.Magnitude, novoS.Position.Magnitude))
else
  say("loja ja estava na posicao nova")
end

-- ============ 2) LEADERBOARDS: area nova, 4 paineis grandes ============
-- remove a estrutura antiga (pavilhao do F22/F23/F24)
local REM = H.SS:FindFirstChild("F24_REMOVIDOS") or H.SS
local destLB = H.folder(REM, "LeaderboardAntigo")
local nOld = 0
for _,nome in ipairs({"HEX_F22","HEX_F23","HEX_F24"}) do
  local f = L:FindFirstChild(nome)
  if f then
    for _,p in ipairs(f:GetChildren()) do
      if p.Name:sub(1,5)=="B_LB_" or p.Name:sub(1,3)=="LB_" or p.Name:sub(1,5)=="TEL_G" then
        p.Parent = destLB nOld += 1
      end
    end
  end
end
say("estrutura antiga do leaderboard arquivada:", nOld, "pecas")

local F28 = H.folder(L,"HEX_F28") H.clear(F28)
H.clearColliders("hx_f28_")
-- posicao: face FR (lado esquerdo visto do portao), a ~100 do centro
local LBs, LBd = 20, 52      -- coords de face FR (d cresce para o centro: 150-52 = 98)
local MAD = rgb(88,60,42)
local MAD_CLARA = rgb(126,88,58)
local OURO = rgb(226,178,84)
local base = H.faceCF("FR", LBs, LBd, 0)
-- plataforma de pedra
H.part({Name="LB_Base", Size=V3(58,1.0,16), CFrame=base*CF(0,0.5,0),
  Color=rgb(178,169,156), Material=Enum.Material.Slate, CanCollide=true}, F28)
H.part({Name="LB_BaseFriso", Size=V3(59,0.4,17), CFrame=base*CF(0,0.2,0),
  Color=rgb(150,140,126), Material=Enum.Material.Slate}, F28)
-- 4 paineis grandes lado a lado
local CATS = {
  {"FORCA",    rgb(226,92,78)},
  {"MOEDAS",   rgb(240,196,90)},
  {"MINERIOS", rgb(104,190,208)},
  {"TEMPO",    rgb(126,206,146)},
}
local PW, PH = 13.0, 11.5     -- largura e altura de cada painel
local GAP = 1.2
local total = #CATS*PW + (#CATS-1)*GAP
for i,cat in ipairs(CATS) do
  local sx = -total/2 + (i-1)*(PW+GAP) + PW/2
  local pcf = base*CF(sx, 1.0 + PH/2 + 1.6, 0)
  -- moldura de madeira
  H.part({Name="LB_Moldura", Size=V3(PW+1.0, PH+1.0, 0.7), CFrame=pcf, Color=MAD, Material=Enum.Material.Wood}, F28)
  -- tabuleiro
  local painel = H.part({Name="LB_Painel", Size=V3(PW, PH, 0.35), CFrame=pcf*CF(0,0,-0.35),
    Color=rgb(40,34,32), Material=Enum.Material.SmoothPlastic}, F28)
  -- travessa superior e pes (linguagem da placa de referencia)
  H.part({Name="LB_TravessaTopo", Size=V3(PW+2.4, 0.8, 1.0), CFrame=pcf*CF(0, PH/2+1.0, 0), Color=MAD_CLARA, Material=Enum.Material.Wood}, F28)
  H.part({Name="LB_Filete", Size=V3(PW+0.6, 0.3, 0.9), CFrame=pcf*CF(0, PH/2-0.2, -0.1), Color=OURO, Material=Enum.Material.Metal}, F28)
  for _,sg in ipairs({-1,1}) do
    H.part({Name="LB_Poste", Size=V3(1.1, PH+4.4, 1.1), CFrame=base*CF(sx+sg*(PW/2+0.9), (PH+4.4)/2, 0), Color=MAD, Material=Enum.Material.Wood, CanCollide=true}, F28)
    H.part({Name="LB_PosteBase", Size=V3(1.9, 1.0, 1.9), CFrame=base*CF(sx+sg*(PW/2+0.9), 0.5, 0), Color=rgb(150,140,126), Material=Enum.Material.Slate}, F28)
  end
  -- GUI: cabecalho + 5 linhas com Rank / Player / Amount
  local gui = Instance.new("SurfaceGui")
  gui.Face = Enum.NormalId.Back
  gui.CanvasSize = Vector2.new(520, 460)
  gui.Parent = painel
  local cab = Instance.new("TextLabel")
  cab.Size = UDim2.new(1,-16,0.16,0) cab.Position = UDim2.new(0,8,0.02,0)
  cab.BackgroundColor3 = cat[2] cab.BackgroundTransparency = 0.12
  cab.Text = cat[1] cab.TextColor3 = rgb(28,24,22)
  cab.TextScaled = true cab.Font = Enum.Font.GothamBlack
  cab.Parent = gui
  for r=1,5 do
    local lin = Instance.new("Frame")
    lin.Size = UDim2.new(1,-16,0.145,0)
    lin.Position = UDim2.new(0,8,0.20+0.155*(r-1),0)
    lin.BackgroundColor3 = (r%2==0) and rgb(56,48,44) or rgb(46,39,36)
    lin.BackgroundTransparency = 0.15
    lin.BorderSizePixel = 0
    lin.Parent = gui
    local pos = Instance.new("TextLabel")
    pos.Size = UDim2.new(0.18,0,1,0) pos.BackgroundTransparency = 1
    pos.Text = "#"..r pos.TextColor3 = cat[2] pos.TextScaled = true
    pos.Font = Enum.Font.GothamBold pos.Parent = lin
    local nome = Instance.new("TextLabel")
    nome.Size = UDim2.new(0.5,0,1,0) nome.Position = UDim2.new(0.18,0,0,0)
    nome.BackgroundTransparency = 1 nome.Text = "---"
    nome.TextColor3 = rgb(226,220,212) nome.TextScaled = true
    nome.TextXAlignment = Enum.TextXAlignment.Left
    nome.Font = Enum.Font.Gotham nome.Parent = lin
    local val = Instance.new("TextLabel")
    val.Size = UDim2.new(0.3,-6,1,0) val.Position = UDim2.new(0.7,0,0,0)
    val.BackgroundTransparency = 1 val.Text = "--"
    val.TextColor3 = rgb(196,188,178) val.TextScaled = true
    val.TextXAlignment = Enum.TextXAlignment.Right
    val.Font = Enum.Font.GothamMedium val.Parent = lin
  end
  H.collider("hx_f28_lb", V3(PW+2, PH+3, 2.2), base*CF(sx, (PH+3)/2, 0))
end
say(("leaderboards: 4 paineis de %.0fx%.0f numa base de 58, a %.0f do centro"):format(PW,PH, base.Position.Magnitude))

-- ============ 3) LAGO: puxar para o centro ============
if L:GetAttribute("F28_LagoMovido") ~= true then
  local F27 = L:FindFirstChild("HEX_F27")
  local F26 = L:FindFirstChild("HEX_F26")
  local dLago = H.FACES.FL.inw * 18
  local n = 0
  for _,pasta in ipairs({F27, F26}) do
    if pasta then
      for _,p in ipairs(pasta:GetChildren()) do
        local nm = p.Name
        if nm:sub(1,4)=="Lago" or nm=="Vitoria" or nm:sub(1,9)=="LOB_rocha" or nm=="PisoRemendo"
           or nm:sub(1,5)=="Queda" then
          if p:IsA("Model") then p:PivotTo(p:GetPivot()+dLago) else p.CFrame = p.CFrame + dLago end
          n += 1
        end
      end
    end
  end
  L:SetAttribute("F28_LagoMovido", true)
  say("lago puxado 18 studs para o centro:", n, "pecas")
end

L:SetAttribute("HEX_F28_OK", true)
H.commit(rec)
return "F28 OK\n"..table.concat(rep,"\n")