-- hex_f22_blockout.lua : F22 = BLOCKOUT do redesign estrutural (briefing 2026-09-22 noite).
-- SO MASSAS E POSICOES - sem acabamento (regra 12 do briefing). Tudo em HEX_F22 com
-- atributo Blockout=true; remocoes vao para ServerStorage.F22_REMOVIDOS com OrigemPath.
-- A) REMOVE lago FR inteiro (leste) + preenche o buraco do piso -> area dos LEADERBOARDS
--    (plataforma + 4 pilares + massa de telhado + painel de 4 secoes com cabecalhos).
-- B) lago FL vira LAGO ORGANICO: bordas retas/pilaretes/terraco/chegada FL removidos;
--    blob assimetrico de discos d'agua + aro de pedra + placas de recorte; ponte/lampioes/
--    banco/rochas/sakura FICAM.
-- C) predio da loja (Oeste + HEX_Loja + LOJA_interior) -> storage; TENDA grande no lugar
--    (postes, cumeeira, 2 aguas de tecido teal com barrado vermelho, balcao F21 mantido,
--    posto do VENDEDOR demarcado - NPC nao existe no projeto, decisao do usuario).
--    PadLoja INTOCADO.
-- D) MURALHA + ALTA: sobreloja (banda vermelha 4 + friso teal) sobre as 6 faces, com vaos
--    nos cantos (torres) e no portao.
-- E) GATEHOUSE: massas de 2 torres flanqueando o portao + sobreloja + grande telhado
--    elevado em 2 aguas + banners (so blockout).
-- Idempotente: limpa HEX_F22; remocoes com guard (ja movido nao move de novo).
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

assert(L:GetAttribute("HEX_F21_OK")==true, "F22: rode a F21 antes")
local rec = H.begin("HEX F22 blockout")
local F22 = H.folder(L,"HEX_F22") H.clear(F22)
H.clearColliders("hx_f22_")
local REM = SS:FindFirstChild("F22_REMOVIDOS") or (function() local f=Instance.new("Folder") f.Name="F22_REMOVIDOS" f.Parent=SS return f end)()
local function tira(i, sub)
  if not i or i:IsDescendantOf(REM) then return 0 end
  if i:GetAttribute("OrigemPath")==nil then i:SetAttribute("OrigemPath", i.Parent:GetFullName()) end
  i.Parent = H.folder(REM, sub)
  return 1
end
local function blq(o, parent)
  local p = H.part(o, parent or F22)
  p:SetAttribute("Blockout", true)
  return p
end

-- zona de face: testa se uma posicao cai no retangulo (s,d) da face
local function naZona(face, pos, sA, sB, dA, dB)
  local lp = H.faceCF(face,0,0,0):PointToObjectSpace(pos)
  return lp.X>=sA and lp.X<=sB and lp.Z>=dA and lp.Z<=dB
end
local function posDe(i)
  if i:IsA("Model") then return i:GetPivot().Position end
  if i:IsA("BasePart") then return i.Position end
  return nil
end

-- ============ A) remover lago FR + leaderboards ============
local FR = H.LAY.PONDS.FR
local nFR = 0
local PASTAS_LAGO = {"HEX_Lagos","HEX_F14D","HEX_F19","HEX_F20","HEX_F21","AGUA","HEX_F13","HEX_P2"}
for _,nome in ipairs(PASTAS_LAGO) do
  local pasta = L:FindFirstChild(nome)
  if pasta then
    for _,c in ipairs(pasta:GetChildren()) do
      local p = posDe(c)
      -- sakuras do usuario FICAM (viram enquadramento dos leaderboards)
      if p and not c.Name:upper():find("SAKURA") and naZona("FR", p, FR.s1-10, FR.s2+10, FR.d1-9, FR.d2+13) then
        nFR += tira(c, "LagoFR")
      end
    end
  end
end
-- colliders: SO os da ponte FR (os hx_p1_estandarte/hx_f8 da muralha ficam com seus visuais)
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name:find("ponte_FR") then nFR += tira(c, "LagoFR") end
end
say("lago FR removido (recuperavel):", nFR, "itens")
-- preencher o buraco do piso do lago FR (tamanho EXATO, topo -0.05: sem face coplanar)
blq({Name="B_PisoFR", Size=V3(FR.s2-FR.s1, 1, FR.d2-FR.d1),
  CFrame=H.faceCF("FR",(FR.s1+FR.s2)/2,(FR.d1+FR.d2)/2,-0.55),
  Color=rgb(190,166,132), Material=Enum.Material.Pavement, CanCollide=true})
-- LEADERBOARDS: plataforma + pilares + telhado + painel de 4 secoes
local lbC = function(s,d,y) return H.faceCF("FR", s, d, y) end
local sC, dC = (FR.s1+FR.s2)/2, 19
blq({Name="B_LB_Base", Size=V3(36,1.2,17), CFrame=lbC(sC,dC,0.6), Color=rgb(168,158,146), Material=Enum.Material.Slate, CanCollide=true})
for _,off in ipairs({{-16,-7},{16,-7},{-16,7},{16,7}}) do
  blq({Name="B_LB_Pilar", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(9.5,2.2,2.2),
    CFrame=lbC(sC+off[1], dC+off[2], 5.95)*CFrame.Angles(0,0,math.rad(90)), Color=C.laca})
end
blq({Name="B_LB_Telhado", Size=V3(41,1.8,21), CFrame=lbC(sC,dC,11.6), Color=C.teal})
blq({Name="B_LB_Cumeeira", Size=V3(30,1.6,10), CFrame=lbC(sC,dC,13.2), Color=C.teal})
-- painel: fundo escuro + 4 secoes com moldura e cabecalho
local painel = blq({Name="B_LB_Painel", Size=V3(30,7.2,0.9), CFrame=lbC(sC, dC-6.2, 4.8), Color=rgb(52,44,40), CanCollide=true})
local CATS = {{"FORCA",rgb(214,84,72)},{"MOEDAS",rgb(240,196,90)},{"MINERIOS",rgb(96,180,200)},{"TEMPO",rgb(120,200,140)}}
for i,cat in ipairs(CATS) do
  local sx = (i-2.5)*7.4
  blq({Name="B_LB_Divisa", Size=V3(0.5,7.2,1.0), CFrame=lbC(sC+sx+3.7, dC-6.2, 4.8), Color=rgb(240,196,90)})
  -- icone: eixo do cilindro (X) apontando para a praca (inw da face)
  local posIc = lbC(sC+sx, dC-6.75, 9.6).Position
  blq({Name="B_LB_Icone", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.4,2.2,2.2),
    CFrame=CFrame.fromMatrix(posIc, H.FACES.FR.inw, V3(0,1,0)), Color=cat[2]})
end
-- cabecalhos via um unico SurfaceGui no painel (lado da praca = +Z local = face Back)
local gui = Instance.new("SurfaceGui")
gui.Face = Enum.NormalId.Back
gui.CanvasSize = Vector2.new(1200,300)
gui.Parent = painel
for i,cat in ipairs(CATS) do
  local tl = Instance.new("TextLabel")
  tl.Size = UDim2.new(0.25,-8,0.22,0)
  tl.Position = UDim2.new(0.25*(i-1),4,0.02,0)
  tl.BackgroundTransparency = 1
  tl.Text = cat[1]
  tl.TextColor3 = cat[2]
  tl.TextScaled = true
  tl.Font = Enum.Font.GothamBold
  tl.Parent = gui
  local corpo = Instance.new("TextLabel")
  corpo.Size = UDim2.new(0.25,-8,0.7,0)
  corpo.Position = UDim2.new(0.25*(i-1),4,0.26,0)
  corpo.BackgroundTransparency = 1
  corpo.Text = "1. ---\n2. ---\n3. ---\n4. ---\n5. ---"
  corpo.TextColor3 = rgb(220,210,200)
  corpo.TextScaled = true
  corpo.Font = Enum.Font.Gotham
  corpo.Parent = gui
end
say("leaderboards: plataforma + painel 4 secoes (dados = pendencia de sistema)")

-- ============ B) lago FL organico ============
local FL = H.LAY.PONDS.FL
local nFL = 0
-- remover so a linguagem RETA: bordas/pilaretes/patamares/terraco/chegada/contorno FL
for _,nomePasta in ipairs({"HEX_F14D","HEX_F19","HEX_F20","HEX_F21"}) do
  local pasta = L:FindFirstChild(nomePasta)
  if pasta then
    for _,c in ipairs(pasta:GetChildren()) do
      local p = posDe(c)
      if p and naZona("FL", p, FL.s1-10, FL.s2+16, FL.d1-9, FL.d2+13) then
        local nm = c.Name
        if nm=="Borda" or nm=="BordaTopo" or nm=="Pilarete" or nm=="PilareteTopo"
          or nm=="PatamarPonte" or nm=="PatamarFilete" or nm=="Terraco" or nm=="TerracoBorda"
          or nm=="Chegada" or nm=="Contorno" then
          nFL += tira(c, "LagoFL_retas")
        end
      end
    end
  end
end
say("lago FL: linguagem reta removida:", nFL, "itens")
-- agua/leito retangulares antigos saem (senao o retangulo continua legivel sob o blob)
for _,nomePasta in ipairs({"HEX_Lagos","AGUA"}) do
  local pasta = L:FindFirstChild(nomePasta)
  if pasta then
    for _,c in ipairs(pasta:GetChildren()) do
      local nm = c.Name
      if nm:find("_FL") and (nm:sub(1,4)=="Agua" or nm:sub(1,5)=="Leito" or nm:sub(1,5)=="Lirio") then
        nFL += tira(c, "LagoFL_retas")
      end
    end
  end
end
-- preenche o leito do FL (tamanho exato, topo -0.05)
blq({Name="B_PisoFL", Size=V3(FL.s2-FL.s1, 1, FL.d2-FL.d1),
  CFrame=H.faceCF("FL",(FL.s1+FL.s2)/2,(FL.d1+FL.d2)/2,-0.55),
  Color=rgb(190,166,132), Material=Enum.Material.Pavement, CanCollide=true})
-- blob organico: discos d'agua sobrepostos (assimetrico, sem retangulo)
local AGUA_COR = rgb(64,168,186)
local DISCOS = {
  {s=-38, d=21, r=12}, {s=-18, d=19, r=14}, {s=0, d=23, r=11}, {s=-6, d=13, r=8},
  {s=14, d=18, r=9}, {s=26, d=15, r=6.5}, {s=-48, d=14, r=6},
}
for i,dsc in ipairs(DISCOS) do
  blq({Name="B_Agua_"..i, Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.35, dsc.r*2, dsc.r*2),
    CFrame=H.faceCF("FL", dsc.s, dsc.d, 0.1)*CFrame.Angles(0,0,math.rad(90)),
    Color=AGUA_COR, Material=Enum.Material.Glass, Transparency=0.15})
  blq({Name="B_Aro_"..i, Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(0.22, dsc.r*2+1.6, dsc.r*2+1.6),
    CFrame=H.faceCF("FL", dsc.s, dsc.d, 0.05)*CFrame.Angles(0,0,math.rad(90)),
    Color=rgb(176,166,152), Material=Enum.Material.Slate})
end
say("lago organico: 7 discos de blockout (forma a validar em captura)")

-- ============ C) tenda da loja ============
local loja
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Name=="LOJA_interior" then loja=d break end
end
-- idempotencia: na 1a execucao o frame vai para atributo; nas seguintes (loja ja no storage) le de la
local S = loja and loja.CFrame or L:GetAttribute("F22_LojaCF")
if loja then L:SetAttribute("F22_LojaCF", loja.CFrame) end
-- ATENCAO (verdade-terreno): pasta "Oeste" e a AREA DE TREINO - NAO TOCAR.
-- De HEX_Loja sai SO o corpo do predio; ficam: piso do patamar (KIT_piso_mod),
-- bloco do patio, molde sumeru, balaustrada e lanternas da escada.
local nLoja = 0
local SAI_LOJA = {KIT_coluna=true, KIT_col_base=true, KIT_arquitrave=true,
  KIT_dougong_intermediario=true, KIT_prancha=true, KIT_vao_parede=true}
local HL = L:FindFirstChild("HEX_Loja")
if HL then
  for _,c in ipairs(HL:GetChildren()) do
    if SAI_LOJA[c.Name] then nLoja += tira(c, "LojaPredio") end
  end
end
if loja then nLoja += tira(loja, "LojaPredio") end
say("corpo do predio da loja removido (recuperavel):", nLoja, "pecas; patamar/escada/treino intactos")
assert(S, "F22: frame da loja perdido antes do uso")
local chao = 7.98
local function TB(lx,ly,lz) return S*CF(lx, ly-13.28, lz) end
-- postes
for _,off in ipairs({{-9,-11},{-9,0},{-9,11},{7,-11},{7,0},{7,11}}) do
  blq({Name="B_TendaPoste", Class="Part", Shape=Enum.PartType.Cylinder, Size=V3(11,1.8,1.8),
    CFrame=TB(off[1], chao+5.5, off[2])*CFrame.Angles(0,0,math.rad(90)), Color=C.laca, CanCollide=true})
end
-- cumeeira e aguas de tecido (massas)
blq({Name="B_TendaCumeeira", Size=V3(2.2,2.2,26), CFrame=TB(-1, chao+13.2, 0), Color=rgb(96,64,44), Material=Enum.Material.Wood})
-- sinais corretos: cumeeira ALTA no centro, beiradas baixas (o painel pegou o V invertido)
blq({Name="B_TendaAguaE", Size=V3(11.5,0.7,27), CFrame=TB(-6.4, chao+11.8, 0)*CFrame.Angles(0,0,math.rad(14)), Color=C.teal})
blq({Name="B_TendaAguaD", Size=V3(11.5,0.7,27), CFrame=TB(4.4, chao+11.8, 0)*CFrame.Angles(0,0,math.rad(-14)), Color=C.teal})
blq({Name="B_TendaBarrado", Size=V3(0.5,2.2,27.4), CFrame=TB(-11.9, chao+10.2, 0), Color=C.laca})
blq({Name="B_TendaBarrado", Size=V3(0.5,2.2,27.4), CFrame=TB(9.9, chao+10.2, 0), Color=C.laca})
-- posto do vendedor (NPC INEXISTENTE no projeto - marcado para decisao do usuario)
blq({Name="B_PostoVendedor", Size=V3(2.2,0.4,2.2), CFrame=TB(-2.5, chao+0.2, 6.8), Color=rgb(240,196,90)})
-- placa da fachada (F14C) e simbolo (F20) reancorados na frente da tenda (o predio saiu)
local F14C = L:FindFirstChild("HEX_F14C")
local F20f = L:FindFirstChild("HEX_F20")
local placaCF = TB(8.9, chao+8.6, 0) * CFrame.Angles(0, math.rad(-90), 0)
if F14C then
  for _,p in ipairs(F14C:GetChildren()) do
    if p.Name:sub(1,5)=="Placa" and p:IsA("BasePart") and p:GetAttribute("F22_Movido")~=true then
      H.remember(p)
      if p.Name=="PlacaFundo" then p.CFrame = placaCF
      elseif p.Name=="PlacaCorrente" then p.CFrame = placaCF*CF((p.Position.X>-108) and 3 or -3, 3.1, 0)
      else -- molduras: recomputa pelos offsets originais aproximados
        local off = p.Size.X>2 and CF(0, (p.Position.Y>15 and 2.3 or -2.3), 0) or CF((p.Position.X>-108 and 3.7 or -3.7), 0, 0)
        p.CFrame = placaCF*off
      end
      p:SetAttribute("F22_Movido", true)
    end
  end
end
if F20f then
  for _,m in ipairs(F20f:GetChildren()) do
    if m.Name=="MochilaV2" and m:GetAttribute("F22_Movido")~=true then
      local lp = S:PointToObjectSpace(m:GetPivot().Position)
      if lp.X > 12 then -- o simbolo da placa
        H.remember(m)
        m:PivotTo(placaCF*CF(0,-0.27,-0.9))
        m:SetAttribute("F22_Movido", true)
      end
    end
  end
end
say("tenda: 6 postes + cobertura em 2 aguas (blockout); placa reancorada; posto do vendedor demarcado")

-- C2) o PORTICO-TEMPLO da loja sobreviveu (telhado TEL_G arquivado na pasta Forja, na
-- posicao da loja + colunas + KIT_placa) e compete com a tenda ("loja, nao outro templo").
local nPort = 0
local Forja = L:FindFirstChild("Forja")
if Forja then
  for _,d in ipairs(Forja:GetChildren()) do
    if d:IsA("BasePart") and d.Name:sub(1,5)=="TEL_G" and d.Position.X < -90 then
      nPort += tira(d, "LojaPortico")
    end
  end
end
local Patio = L:FindFirstChild("Patio")
if Patio then
  for _,d in ipairs(Patio:GetChildren()) do
    if d:IsA("BasePart") and d.Position.X<-93 and d.Position.X>-125 and d.Position.Z<-35 and d.Position.Z>-62 then
      local nm = d.Name
      if nm=="KIT_placa" or ((nm:sub(1,4)=="KIT_" or nm:sub(1,4)=="LOB_") and d.Size.Y>6) then
        nPort += tira(d, "LojaPortico")
      end
    end
  end
end
say("portico-templo removido (recuperavel):", nPort, "pecas")
-- placa da F14C re-pendurada na testeira da tenda (o portico que a segurava saiu)
local placaCF2 = TB(10.4, chao+7.4, 0) * CFrame.Angles(0, math.rad(-90), 0)
if F14C then
  for _,p in ipairs(F14C:GetChildren()) do
    if p.Name:sub(1,5)=="Placa" and p:IsA("BasePart") and p:GetAttribute("F22b")~=true then
      if p.Name=="PlacaFundo" then p.CFrame = placaCF2
      elseif p.Name=="PlacaCorrente" then p.CFrame = placaCF2*CF((p.Position.Z<-52) and 3 or -3, 2.7, 0)
      else
        local off = p.Size.X>2 and CF(0, (p.Position.Y>16.6 and 2.3 or -2.3), 0) or CF((p.Position.Z<-52 and 3.7 or -3.7), 0, 0)
        p.CFrame = placaCF2*off
      end
      p:SetAttribute("F22b", true)
    end
  end
end
if F20f then
  for _,m in ipairs(F20f:GetChildren()) do
    if m.Name=="MochilaV2" and m:GetAttribute("F22b")~=true then
      local lp = S:PointToObjectSpace(m:GetPivot().Position)
      if lp.X > 8 and lp.Y > 1 then -- o simbolo (alto, na frente)
        m:PivotTo(placaCF2*CF(0,-0.27,-0.9))
        m:SetAttribute("F22b", true)
      end
    end
  end
end
say("placa re-pendurada na testeira da tenda")
-- colliders das colunas do predio antigo saem junto
for _,c in ipairs(H.COL:GetChildren()) do
  if c.Name:sub(1,15)=="hx_f4_loja_col_" then tira(c, "LojaPredio") end
end

-- ============ D) muralha mais alta (sobreloja) ============
local nMur = 0
for _,f in ipairs({"FR","F","FL","BL","B","BR"}) do
  local segs = (f=="F") and {{-72,-48},{48,72}} or {{-72,72}}
  for _,sg in ipairs(segs) do
    H.faceRect(F22, {Name="B_Sobreloja", Color=C.muro, CanCollide=false}, f, sg[1], sg[2], -1.6, 1.6, 14, 18)
    H.faceRect(F22, {Name="B_Friso", Color=C.teal}, f, sg[1]-0.2, sg[2]+0.2, -2.0, 2.0, 18, 18.9)
    nMur += 1
  end
end
for _,p in ipairs(F22:GetChildren()) do
  if p.Name=="B_Sobreloja" or p.Name=="B_Friso" then p:SetAttribute("Blockout", true) end
end
say("muralha: sobreloja de blockout em", nMur, "trechos")

-- ============ E) gatehouse ============
local function GT(x,y,z) return CF(x,y,150+ (z or 0)) end
for _,sx in ipairs({-1,1}) do
  -- torres meio para fora do portao (em x=44 ficavam 100% dentro da espessura e liam finas)
  blq({Name="B_GateTorre", Size=V3(13,26,13), CFrame=GT(sx*48,13,0), Color=C.muro, CanCollide=true})
  blq({Name="B_GateTorreTopo", Size=V3(15,2.4,15), CFrame=GT(sx*48,27.2,0), Color=C.teal})
  -- banner saliente da face da praca (em -7.2 ficava enterrado na muralha de 20.5)
  blq({Name="B_GateBanner", Size=V3(4.5,14,0.4), CFrame=GT(sx*48,16,-10.9), Color=C.laca})
end
blq({Name="B_GateSobreloja", Size=V3(64,7,12), CFrame=GT(0,23.7,0), Color=C.muro})
blq({Name="B_GateTelhado", Size=V3(71,2.6,24), CFrame=GT(0,28.6,0), Color=C.teal})
blq({Name="B_GateTelhado2", Size=V3(50,2.2,15), CFrame=GT(0,33,0), Color=C.teal})
blq({Name="B_GateCumeeira", Size=V3(34,1.8,6), CFrame=GT(0,35,0), Color=C.teal})
say("gatehouse: torres + sobreloja + telhado em 2 niveis (massas)")

L:SetAttribute("HEX_F22_OK", true)
H.commit(rec)
return "F22 OK (BLOCKOUT)\n"..table.concat(rep,"\n")