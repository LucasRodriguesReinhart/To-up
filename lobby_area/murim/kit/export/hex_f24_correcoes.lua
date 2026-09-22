-- hex_f24_correcoes.lua : F24 = correcoes do redesign (briefing com imagens de referencia).
-- B) LAGO: ponte FL removida (recuperavel); silhueta refeita com 5 ELIPSES grandes em curva-S
--    + 3 MORDIDAS concavas (o que mata a leitura de "circulos grudados" e concavidade),
--    pequena queda d'agua na extremidade da muralha, 3 rochas grandes, 8 vitorias.
-- 8) BANCOS: auditoria - removidos os 4 das vinhetas (isolados no pavimento) e o do lago
--    ganha um patamar proprio virado para a agua.
-- C) TENDA v2 pela referencia (4 postes + tecido + balcao FRONTAL + comerciante DENTRO):
--    cobertura LISTRADA teal/laca (le tecido, nao telha), barrado recortado, balcao volta
--    para a FRENTE, NPC VENDEDOR REAL ("npc vendedor ") atras do balcao (HRP ancorado),
--    mochilas: expositor atras dele + ilhas nas LATERAIS. Eixo: MOCHILAS->NPC->BALCAO->PLAYER.
-- D) LEADERBOARD pela referencia da placa: moldura de madeira, saia de pedra ate a base,
--    SurfaceGui com 4 colunas (cabecalho colorido + linhas 1-5).
-- Idempotente: limpa HEX_F24; remocoes p/ ServerStorage.F24_REMOVIDOS; movimentos com guard.
local fnH, errH = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))
assert(fnH, errH)
local H = fnH()
H.selfTest()
local L, C = H.L, H.C
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F23_OK")==true, "F24: rode a F23 antes")
math.randomseed(24)
local rec = H.begin("HEX F24 correcoes")
local F22 = L:FindFirstChild("HEX_F22")
local F23 = L:FindFirstChild("HEX_F23")
local F24 = H.folder(L,"HEX_F24") H.clear(F24)
H.clearColliders("hx_f24_")
local REM = SS:FindFirstChild("F24_REMOVIDOS") or (function() local f=Instance.new("Folder") f.Name="F24_REMOVIDOS" f.Parent=SS return f end)()
local function tira(i, sub)
  if not i or i:IsDescendantOf(REM) then return 0 end
  if i:GetAttribute("OrigemPath")==nil then i:SetAttribute("OrigemPath", i.Parent:GetFullName()) end
  i.Parent = H.folder(REM, sub)
  return 1
end

-- ============ B) lago: ponte fora, silhueta continua ============
local nPonte = 0
local Lagos = L:FindFirstChild("HEX_Lagos")
if Lagos then
  for _,c in ipairs(Lagos:GetChildren()) do
    if c.Name=="Ponte_FL" or c.Name:sub(1,11)=="Lanterna_FL" then nPonte += tira(c,"PonteFL") end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name:find("ponte_FL") then nPonte += tira(c,"PonteFL") end
end
say("ponte do lago removida (recuperavel):", nPonte, "conjuntos")
-- discos antigos e vitorias da F23 saem
if F22 then
  for _,p in ipairs(F22:GetChildren()) do
    if p.Name:sub(1,7)=="B_Agua_" or p.Name:sub(1,6)=="B_Aro_" then p:Destroy() end
  end
end
if F23 then
  for _,p in ipairs(F23:GetChildren()) do
    if p.Name=="Vitoria" or p.Name=="Lotus" or p.Name=="LotusMiolo" then p:Destroy() end
  end
end
-- 5 elipses grandes em curva-S (eixo do cilindro vertical; footprint = Size.Y x Size.Z)
local AGUA_COR = rgb(64,168,186)
local ELIPSES = {
  {s=-46, d=19, A=32, B=21, yaw=18},
  {s=-22, d=25, A=38, B=26, yaw=-8},
  {s=2,  d=17, A=28, B=18, yaw=28},
  {s=22, d=27, A=20, B=13, yaw=-22},
  {s=-60, d=13, A=14, B=10, yaw=8},
}
for i,e in ipairs(ELIPSES) do
  local base = H.faceCF("FL", e.s, e.d, 0) * CFrame.Angles(0, math.rad(e.yaw), 0)
  H.part({Name="LagoAro_"..i, Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.2, e.A+2.4, e.B+2.4),
    CFrame=base*CF(0,0.04,0)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(176,166,152), Material=Enum.Material.Slate}, F24)
  H.part({Name="LagoAgua_"..i, Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.3, e.A, e.B),
    CFrame=base*CF(0,0.12,0)*CFrame.Angles(0,0,math.rad(90)), Color=AGUA_COR, Material=Enum.Material.Glass, Transparency=0.15}, F24)
end
-- 3 mordidas concavas (placas cor do piso cortando as bordas circulares)
for _,m in ipairs({{s=-34,d=9,A=18,B=9,yaw=12},{s=-8,d=30,A=16,B=10,yaw=-18},{s=12,d=10,A=14,B=8,yaw=30}}) do
  local base = H.faceCF("FL", m.s, m.d, 0) * CFrame.Angles(0, math.rad(m.yaw), 0)
  H.part({Name="LagoMordida", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.36, m.A, m.B),
    CFrame=base*CF(0,0.14,0)*CFrame.Angles(0,0,math.rad(90)), Color=rgb(190,166,132), Material=Enum.Material.Pavement}, F24)
end
-- pequena queda d'agua na extremidade da muralha (s=-60)
local qBase = H.faceCF("FL", -63, 9, 0)
H.part({Name="QuedaPedra", Size=V3(9,3.2,4), CFrame=qBase*CF(0,1.6,0), Color=rgb(150,140,126), Material=Enum.Material.Slate, CanCollide=true}, F24)
H.part({Name="QuedaLamina", Size=V3(5.5,2.4,0.5), CFrame=qBase*CF(0,1.5,1.9), Color=rgb(214,242,250), Material=Enum.Material.Glass, Transparency=0.2}, F24)
local espuma = H.part({Name="QuedaEspuma", Size=V3(6,0.5,1.6), CFrame=qBase*CF(0,0.35,2.4), Color=rgb(255,255,255), Material=Enum.Material.Neon, Transparency=0.2}, F24)
local pe = Instance.new("ParticleEmitter")
pe.Color=ColorSequence.new(rgb(230,248,252)) pe.Rate=4 pe.Lifetime=NumberRange.new(1,1.8)
pe.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,0.7),NumberSequenceKeypoint.new(1,1.8)})
pe.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,0.5),NumberSequenceKeypoint.new(1,1)})
pe.Speed=NumberRange.new(1,2) pe.Parent=espuma
-- 3 rochas grandes estrategicas
local rocha
local F14D = L:FindFirstChild("HEX_F14D")
if F14D then
  for _,c in ipairs(F14D:GetChildren()) do
    if c:IsA("MeshPart") and c.Name:sub(1,9)=="LOB_rocha" then rocha=c break end
  end
end
if rocha then
  for i,rr in ipairs({{s=-56,d=22,e=1.25},{s=-2,d=28,e=0.85},{s=26,d=20,e=0.55}}) do
    local c = rocha:Clone()
    for k in pairs(c:GetAttributes()) do c:SetAttribute(k,nil) end
    c:SetAttribute("HexGen",true)
    c.Size = rocha.Size*(rr.e/0.95)
    c.CanCollide=false c.CanQuery=false c.Anchored=true
    c.CFrame = H.faceCF("FL", rr.s, rr.d, c.Size.Y/2-0.4)*CFrame.Angles(0,math.rad(math.random(0,359)),0)
    c.Parent = F24
  end
end
-- vitorias-regias novas (8) sobre as elipses
for i=1,8 do
  local e = ELIPSES[(i%4)+1]
  local a = math.random()*math.pi*2
  local pos = H.fp("FL", e.s+math.cos(a)*(e.A/2-3), e.d+math.sin(a)*(e.B/2-2.5)*0.8, 0.34)
  H.part({Name="Vitoria", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.14,2.2,2.2),
    CFrame=CF(pos)*CFrame.Angles(0,math.rad(math.random(0,359)),math.rad(90)), Color=C.lirio, Material=Enum.Material.Grass}, F24)
end
say("lago: 5 elipses + 3 mordidas concavas + queda + 3 rochas + 8 vitorias")

-- ============ 8) auditoria de bancos ============
local nBanco = 0
for _,d in ipairs(L:GetDescendants()) do
  if d.Name=="VIL_banco" and d:IsA("BasePart") and not d:IsDescendantOf(REM) then
    local p = d.Position
    local pertoLagoFL = (H.faceCF("FL",0,0,0):PointToObjectSpace(p)).Z < 46 and math.abs((H.faceCF("FL",0,0,0):PointToObjectSpace(p)).X) < 70
    if not pertoLagoFL then
      nBanco += tira(d, "Bancos")
    else
      -- banco do lago ganha patamar proprio virado para a agua
      if d:GetAttribute("F24_Movido")~=true then
        H.remember(d)
        local alvo = H.faceCF("FL", -34, 40, 1.15) * CFrame.Angles(0, math.rad(180), 0)
        d.CFrame = alvo
        d:SetAttribute("F24_Movido", true)
        H.part({Name="BancoPatamar", Size=V3(11,0.5,5.5), CFrame=H.faceCF("FL",-34,40,0.25),
          Color=rgb(176,166,152), Material=Enum.Material.Slate, CanCollide=true}, F24)
      end
    end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name:find("banco") and not c.Name:find("f14c") then tira(c, "Bancos") end
end
say("bancos sem funcao removidos:", nBanco, "(o do lago ganhou patamar proprio)")

-- ============ C) tenda v2 pela referencia ============
local S = L:GetAttribute("F22_LojaCF")
assert(S, "F24: F22_LojaCF ausente")
local chao = 7.98
local function TB(lx,ly,lz) return S*CF(lx, ly-13.28, lz) end
-- limpa tenda antiga (F22 massas + F23 tecido)
if F22 then
  for _,p in ipairs(F22:GetChildren()) do
    if p.Name:sub(1,7)=="B_Tenda" or p.Name=="B_PostoVendedor" then p:Destroy() end
  end
end
if F23 then
  for _,p in ipairs(F23:GetChildren()) do
    if p.Name:sub(1,5)=="Tenda" then p:Destroy() end
  end
end
local MAD_ESC = rgb(74,52,38)
-- 4 postes de madeira robustos com sapata de pedra
for _,off in ipairs({{-8,-9.5},{-8,9.5},{8,-9.5},{8,9.5}}) do
  H.part({Name="TendaSapata", Size=V3(1.8,1.0,1.8), CFrame=TB(off[1], chao+0.5, off[2]), Color=rgb(168,158,146), Material=Enum.Material.Slate, CanCollide=true}, F24)
  H.part({Name="TendaPoste", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(9.6,1.5,1.5),
    CFrame=TB(off[1], chao+5.8, off[2])*CFrame.Angles(0,0,math.rad(90)), Color=MAD_ESC, Material=Enum.Material.Wood, CanCollide=true}, F24)
end
-- vigas do quadro superior
for _,lz in ipairs({-9.5,9.5}) do
  H.part({Name="TendaViga", Size=V3(18.4,0.7,0.7), CFrame=TB(0, chao+10.4, lz), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
end
for _,lx in ipairs({-8,8}) do
  H.part({Name="TendaViga", Size=V3(0.7,0.7,19.8), CFrame=TB(lx, chao+10.4, 0), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
end
-- cobertura LISTRADA em 2 aguas suaves (listras correm ladeira abaixo; le tecido)
local RIDGE = chao+12.6
H.part({Name="TendaCumeeira", Size=V3(1.1,1.1,22.5), CFrame=TB(0, RIDGE, 0), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
for lado,ang in pairs({[-1]=10, [1]=-10}) do
  for k=0,10 do
    local lz = -11 + k*2.2
    local cor = (k%2==0) and C.teal or rgb(184,50,42)
    H.part({Name="TendaListra", Size=V3(10.6,0.35,2.2),
      CFrame=TB(lado*5.0, RIDGE-0.95, lz)*CFrame.Angles(0,0,math.rad(ang)),
      Color=cor, Material=Enum.Material.Fabric}, F24)
  end
end
-- barrado recortado nas 4 beiradas
local nAba=0
for _,ed in ipairs({{-10.2,nil},{10.2,nil},{nil,-11},{nil,11}}) do
  for k=0,9 do
    local cor = (k%2==0) and rgb(184,50,42) or C.teal
    local lx = ed[1] or (-9+k*2)
    local lz = ed[2] or (-9.9+k*2.2)
    H.part({Name="TendaAba", Size=ed[1] and V3(0.3,1.3,1.9) or V3(1.7,1.3,0.3),
      CFrame=TB(lx, chao+9.35, lz), Color=cor, Material=Enum.Material.Fabric}, F24)
    nAba+=1
  end
end
-- balcao volta para a FRENTE (eixo mochilas->NPC->balcao->player)
local F14C = L:FindFirstChild("HEX_F14C")
if F14C then
  for _,p in ipairs(F14C:GetChildren()) do
    if p:IsA("BasePart") and p:GetAttribute("F24_Movido")~=true then
      if p.Name=="BalcaoCorpo" then H.remember(p) p.CFrame = TB(5.2, chao+1.3, 0) p:SetAttribute("F24_Movido",true)
      elseif p.Name=="BalcaoTampo" then H.remember(p) p.CFrame = TB(5.2, chao+2.77, 0) p:SetAttribute("F24_Movido",true)
      elseif p.Name=="BalcaoFriso" then H.remember(p) p.CFrame = TB(5.2, chao+2.55, 0) p:SetAttribute("F24_Movido",true) end
    end
  end
end
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name=="hx_f14c_balcao" then
    c.CFrame = TB(5.2, chao+1.5, 0)
  end
end
-- NPC VENDEDOR REAL atras do balcao, de frente para o player (+X local)
local npc
for _,c in ipairs(workspace:GetChildren()) do
  if c.Name:match("^npc vendedor") then npc=c break end
end
if npc then
  local hrp = npc:FindFirstChild("HumanoidRootPart")
  npc:PivotTo(S * CF(2.4, (chao+3.05)-13.28, 0) * CFrame.Angles(0, math.rad(-90), 0))
  if hrp then hrp.Anchored = true end
  say("NPC vendedor posicionado atras do balcao (HRP ancorado)")
else
  say("AVISO: npc vendedor nao achado na raiz do workspace")
end
-- ilhas de exposicao para as LATERAIS (guard por atributo)
local F21f = L:FindFirstChild("HEX_F21")
if F21f then
  local mesas = {}
  for _,p in ipairs(F21f:GetChildren()) do
    if p.Name:sub(1,4)=="Mesa" and p:IsA("BasePart") then table.insert(mesas,p) end
  end
  -- agrupa por proximidade das 2 ilhas originais e desloca em bloco
  local ALVO = {TB(-2.5,0,-7.6), TB(-2.5,0,7.6)}
  local ORIG = {S*CF(2.2,0,-2.8), S*CF(-1.8,0,2.8)}
  for _,p in ipairs(mesas) do
    if p:GetAttribute("F24_Movido")~=true then
      local qual = ((p.Position-ORIG[1].Position).Magnitude < (p.Position-ORIG[2].Position).Magnitude) and 1 or 2
      p.CFrame = p.CFrame + (ALVO[qual].Position - ORIG[qual].Position)
      p:SetAttribute("F24_Movido", true)
    end
  end
  for _,c in ipairs(H.COL:GetChildren()) do
    if c.Name=="hx_f21_mesa" and c:GetAttribute("F24_Movido")~=true then
      local qual = ((c.Position-ORIG[1].Position).Magnitude < (c.Position-ORIG[2].Position).Magnitude) and 1 or 2
      c.CFrame = c.CFrame + (ALVO[qual].Position - ORIG[qual].Position)
      c:SetAttribute("F24_Movido", true)
    end
  end
end
local F20f = L:FindFirstChild("HEX_F20")
if F20f then
  local ORIG = {S*CF(2.2,0,-2.8), S*CF(-1.8,0,2.8)}
  local ALVO = {TB(-2.5,0,-7.6), TB(-2.5,0,7.6)}
  for _,m in ipairs(F20f:GetChildren()) do
    if m.Name=="MochilaV2" and m:GetAttribute("F24_Movido")~=true then
      local p = m:GetPivot().Position
      local d1 = (V3(p.X,0,p.Z)-V3(ORIG[1].Position.X,0,ORIG[1].Position.Z)).Magnitude
      local d2 = (V3(p.X,0,p.Z)-V3(ORIG[2].Position.X,0,ORIG[2].Position.Z)).Magnitude
      if math.min(d1,d2) < 3 then
        local qual = (d1<d2) and 1 or 2
        m:PivotTo(m:GetPivot() + (ALVO[qual].Position - ORIG[qual].Position))
        m:SetAttribute("F24_Movido", true)
      elseif math.abs(S:PointToObjectSpace(p).X - 5.5) < 2 and S:PointToObjectSpace(p).Z > 4 then
        -- amostra do balcao antigo lateral -> balcao frontal novo
        m:PivotTo(S * CF(5.2, (chao+2.945+0.95)-13.28, 3) * CFrame.Angles(0, math.rad(-90), 0))
        m:SetAttribute("F24_Movido", true)
      end
    end
  end
end
say("tenda v2: postes/vigas/listras/abas =", nAba, "abas; balcao frontal; ilhas nas laterais")

-- ============ D) leaderboard: moldura + saia + GUI da referencia ============
if F22 then
  local painel
  for _,p in ipairs(F22:GetChildren()) do if p.Name=="B_LB_Painel" then painel=p break end end
  if painel then
    -- moldura de madeira e saia de pedra
    local pc = painel.CFrame
    H.part({Name="LB_Moldura", Size=V3(31,0.6,1.1), CFrame=pc*CF(0,3.9,0), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
    H.part({Name="LB_Moldura", Size=V3(31,0.6,1.1), CFrame=pc*CF(0,-3.9,0), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
    H.part({Name="LB_Moldura", Size=V3(0.6,8.4,1.1), CFrame=pc*CF(-15.3,0,0), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
    H.part({Name="LB_Moldura", Size=V3(0.6,8.4,1.1), CFrame=pc*CF(15.3,0,0), Color=MAD_ESC, Material=Enum.Material.Wood}, F24)
    H.part({Name="LB_Saia", Size=V3(31.6,1.6,1.6), CFrame=pc*CF(0,-4.9,0), Color=rgb(168,158,146), Material=Enum.Material.Slate}, F24)
    -- GUI refeita no padrao da referencia (4 colunas, cabecalho colorido, linhas 1-5)
    local velho = painel:FindFirstChildOfClass("SurfaceGui")
    if velho then velho:Destroy() end
    local gui = Instance.new("SurfaceGui")
    gui.Face = Enum.NormalId.Back
    gui.CanvasSize = Vector2.new(1600,420)
    gui.Parent = painel
    local CATS = {{"FORCA",rgb(214,84,72)},{"MOEDAS",rgb(240,196,90)},{"MINERIOS",rgb(96,180,200)},{"TEMPO",rgb(120,200,140)}}
    for i,cat in ipairs(CATS) do
      local cab = Instance.new("TextLabel")
      cab.Size=UDim2.new(0.25,-12,0.2,0)
      cab.Position=UDim2.new(0.25*(i-1),6,0.03,0)
      cab.BackgroundColor3=rgb(28,24,22) cab.BackgroundTransparency=0.15
      cab.Text=cat[1] cab.TextColor3=cat[2] cab.TextScaled=true cab.Font=Enum.Font.GothamBlack
      cab.Parent=gui
      for r=1,5 do
        local lin=Instance.new("TextLabel")
        lin.Size=UDim2.new(0.25,-12,0.13,0)
        lin.Position=UDim2.new(0.25*(i-1),6,0.24+0.14*(r-1),0)
        lin.BackgroundTransparency=1
        lin.Text=r..".  ---"
        lin.TextColor3=rgb(216,208,198) lin.TextScaled=true lin.Font=Enum.Font.Gotham
        lin.TextXAlignment=Enum.TextXAlignment.Left
        lin.Parent=gui
      end
    end
  end
end
say("leaderboard: moldura de madeira + saia de pedra + GUI 4 colunas 1-5")

L:SetAttribute("HEX_F24_OK", true)
H.commit(rec)
return "F24 OK\n"..table.concat(rep,"\n")