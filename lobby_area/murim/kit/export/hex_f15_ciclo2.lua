-- hex_f15_ciclo2.lua : F15 = ciclo 2 do briefing - acabamento sobre o que existe, sem objetos novos
-- (exceto 1 luz de preenchimento e a troca 1:1 da arvore fora de estilo).
-- a) telhado da galeria (HEX_F14B) desce 0.6 (fresta beiral/viga);
-- b) degraus do pedestal: branco -> pedra clara quente (CorOriginal);
-- c) losangos/insignias Metal cáqui -> OURO_VIVO SmoothPlastic;
-- d) fill quente frontal no Ignis (nao altera Lighting global);
-- e) BordaTopo dos lagos: -1 passo de valor;
-- f) arvore torcida antiga no lago FL -> SAKURA do usuario no MESMO ponto;
-- g) piso: campo -1 passo de valor (CorOriginal ja existe do P0).
-- Idempotente: marca HEX_F15_OK; reexecucao segura (usa alvos absolutos).
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local SS = H.SS
local V3, CF = Vector3.new, CFrame.new
local rgb = Color3.fromRGB
local OURO_VIVO = rgb(240,196,90)
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F14E_OK")==true, "F15: rode a F14e antes")
local rec = H.begin("HEX F15 ciclo 2")

-- a) telhado da galeria desce 0.6 (uma vez)
if L:GetAttribute("HEX_F15_TELHADO")~=true then
  for _,p in ipairs(L.HEX_F14B:GetChildren()) do
    if p:IsA("BasePart") then p.CFrame = p.CFrame - V3(0,0.6,0) end
  end
  L:SetAttribute("HEX_F15_TELHADO", true)
  say("telhado da galeria: -0.6")
else say("telhado da galeria: ja ajustado") end

-- b) degraus do pedestal
local nDeg = 0
for _,d in ipairs(L.HEX_Monumento:GetChildren()) do
  if d:IsA("BasePart") and (d.Name:sub(1,8)=="Mon_pass" or d.Name=="Mon_anel_base") then
    local c=d.Color
    if c.R>0.85 and c.G>0.85 and c.B>0.85 then
      if d:GetAttribute("CorOriginal")==nil then d:SetAttribute("CorOriginal", d.Color) end
      d.Color = rgb(213,201,184) nDeg += 1
    end
  end
end
say("degraus do pedestal recoloridos:", nDeg)

-- c) insignias douradas: Metal caqui -> OURO_VIVO SmoothPlastic
local nOuro = 0
for _,d in ipairs(L.HEX_F13:GetChildren()) do
  if d:IsA("BasePart") and (d.Name=="TapeteLosango" or d.Name=="Med_losango") then
    d.Color = OURO_VIVO d.Material = Enum.Material.SmoothPlastic nOuro += 1
  end
end
say("insignias em OURO_VIVO:", nOuro)

-- d) fill frontal do Ignis
local FE = L:FindFirstChild("HEX_F14E")
local fill = FE and FE:FindFirstChild("IgnisFill")
if not fill then
  fill = H.part({Name="IgnisFill", Size=V3(0.4,0.4,0.4), CFrame=CF(0,22,-99),
    Transparency=1, CastShadow=false}, FE or L)
  local pl = Instance.new("PointLight")
  pl.Range=20 pl.Brightness=0.55 pl.Color=rgb(255,214,160) pl.Shadows=false pl.Parent=fill
  say("fill quente frontal do Ignis criado")
else say("fill do Ignis ja existe") end

-- e) topo das bordas dos lagos
local nTopo = 0
for _,d in ipairs(L.HEX_F14D:GetChildren()) do
  if d:IsA("BasePart") and (d.Name=="BordaTopo" or d.Name=="PilareteTopo") then
    d.Color = rgb(176,166,152) nTopo += 1
  end
end
say("topos de borda aquecidos:", nTopo)

-- f) arvore torcida no lago FL -> SAKURA do usuario
local REM = SS:FindFirstChild("F14_REMOVIDOS")
local LIBU = SS:FindFirstChild("LIB_USUARIO")
local trocou = false
if LIBU and LIBU:FindFirstChild("SAKURA") then
  for _,d in ipairs(L:GetDescendants()) do
    if (d:IsA("Model") or d:IsA("MeshPart")) and not d:IsDescendantOf(L.HEX_F13) and d.Parent~=REM then
      local ok, p = pcall(function() return d:IsA("Model") and d:GetPivot().Position or d.Position end)
      if ok and p.X>-100 and p.X<-72 and p.Z>100 and p.Z<126 and p.Y>1 and p.Y<26 then
        local nm = d.Name:lower()
        local cf, sz
        if d:IsA("Model") then cf,sz = d:GetBoundingBox() else cf,sz = d.CFrame,d.Size end
        if sz.Y > 6 and (nm:find("arvore") or nm:find("sakura") or nm:find("cerej") or nm:find("vil") or nm:find("jar") or nm:find("tree")) then
          if REM then d.Parent = REM else d:Destroy() end
          local s = LIBU.SAKURA:Clone()
          for k in pairs(s:GetAttributes()) do s:SetAttribute(k,nil) end
          s:SetAttribute("HexGen",true) s.Parent = L.HEX_F13
          s:PivotTo(CF(p.X, 0, p.Z)*CFrame.Angles(0,math.rad(140),0))
          local cf2,sz2 = s:GetBoundingBox()
          s:PivotTo(s:GetPivot()+V3(0, (0-0.25+sz2.Y/2)-cf2.Position.Y, 0))
          H.collider("hx_f15_tronco", V3(2.2,8,2.2), CF(p.X,4,p.Z))
          trocou = true
          say("arvore fora de estilo ("..d.Name..") -> SAKURA em", ("%.0f,%.0f"):format(p.X,p.Z))
          break
        end
      end
    end
  end
end
if not trocou then say("arvore torcida: nenhum alvo casou (verificar manualmente)") end

-- g) campo do piso: -1 passo de valor
local nPiso = 0
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") and d.Parent.Name=="Piso" then
    d.Color = rgb(190,166,132) nPiso += 1
  end
end
say("campo do piso aquecido:", nPiso)

L:SetAttribute("HEX_F15_OK", true)
H.commit(rec)
return "F15 OK\n"..table.concat(rep,"\n")