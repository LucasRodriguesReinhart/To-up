-- hex_fase10_p0_valor_luz.lua : P0 = hierarquia de valor no piso + luz fim de tarde.
-- Nao cria nenhum objeto novo (so PointLight em lampiao apagado, marcado P0_Light).
-- Tudo reversivel: pecas recoloridas guardam CorOriginal; propriedades do Lighting
-- guardam P0_<prop> (string/number/color) antes da primeira mudanca.
-- Idempotente: rodar de novo re-aplica os mesmos valores finais.
local H = loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/hex_comum.lua", true))()
local L = H.L
local Li = game:GetService("Lighting")
local rgb = Color3.fromRGB
local rep = {}
local function say(...) local t={} for i,v in ipairs({...}) do t[i]=tostring(v) end table.insert(rep,table.concat(t," ")) end

assert(L:GetAttribute("HEX_F8_OK")==true, "P0: F8 ausente")
local rec = H.begin("HEX P0 valor e luz")

-- ============ 1) piso: 3 niveis de valor, tom quente ============
-- campo (claro-quente) > caminhos (medio) > medalhao (escuro). Nada de branco.
local ALVO = {
  {pasta="Piso",     cor=rgb(199,174,140)}, -- campo: bege pedra quente (era 220,198,166 lavado)
  {pasta="Faixas",   cor=rgb(140,126,110)}, -- caminhos: meio tom mais escuro
  {pasta="Medalhao", cor=rgb(97,90,85)},    -- medalhao: ancora escura do focal
}
local nPiso = 0
for _,a in ipairs(ALVO) do
  for _,d in ipairs(L:GetDescendants()) do
    if d:IsA("BasePart") and d.Parent.Name==a.pasta then
      if d:GetAttribute("CorOriginal")==nil then d:SetAttribute("CorOriginal", d.Color) end
      d.Color = a.cor nPiso += 1
    end
  end
end
say("piso recolorido:", nPiso, "pecas em 3 niveis de valor")

-- ============ 2) Lighting: fim de tarde dourado ============
local function setP(obj, prop, val)
  local k = "P0_"..prop
  if obj:GetAttribute(k)==nil then obj:SetAttribute(k, obj[prop]) end
  obj[prop] = val
end
setP(Li, "ClockTime", 15.4) -- 16.6 escurecia demais; referencia e dourada POREM clara
setP(Li, "Brightness", 2.9)
setP(Li, "ExposureCompensation", 0.12)
setP(Li, "Ambient", rgb(112,103,95))
setP(Li, "OutdoorAmbient", rgb(152,139,122))
setP(Li, "ColorShift_Top", rgb(255,226,180))
setP(Li, "ShadowSoftness", 0.12)
setP(Li, "EnvironmentDiffuseScale", 1)
setP(Li, "EnvironmentSpecularScale", 1)
say("sol: ClockTime 16.6, ambiente quente")

local CC = Li:FindFirstChild("ColorCorrection")
if CC then
  setP(CC, "Contrast", 0.06)
  setP(CC, "Saturation", 0.13)
  setP(CC, "TintColor", rgb(255,246,232))
  setP(CC, "Brightness", 0)
  say("ColorCorrection: contraste 0.06, saturacao 0.13, tint quente")
end
local AT = Li:FindFirstChild("Atmosphere")
if AT then
  -- density 0.3/haze 1.4 deixou tudo cinza na vista aerea; nevoa LEVE
  setP(AT, "Density", 0.12)
  setP(AT, "Offset", 0.2)
  setP(AT, "Color", rgb(222,208,188))
  setP(AT, "Decay", rgb(170,150,128))
  setP(AT, "Haze", 0.7)
  setP(AT, "Glare", 0.18)
  say("Atmosphere: haze quente leve")
end
local BL = Li:FindFirstChild("Bloom")
if BL then
  setP(BL, "Intensity", 0.6)
  setP(BL, "Size", 30)
  setP(BL, "Threshold", 1.35)
  say("Bloom: brilho suave para ouro/neon")
end
local SR = Li:FindFirstChild("SunRays")
if SR then
  setP(SR, "Intensity", 0.06)
  setP(SR, "Spread", 0.6)
  say("SunRays: discreto (guia manda nao exagerar)")
end

-- ============ 3) lampioes acesos ============
-- todo corpo de lampiao/lanterna sem PointLight ganha um (marcado P0_Light=true)
local nLuz = 0
for _,d in ipairs(L:GetDescendants()) do
  if d:IsA("BasePart") then
    local nm = d.Name:lower()
    local pai = d.Parent and d.Parent.Name:lower() or ""
    local eLampiao = nm:find("lampiao") or nm:find("lanterna") or ((nm=="corpo" or nm=="balao") and (pai:find("lampiao") or pai:find("lanterna")))
    if eLampiao and d.Size.Magnitude<8 and not d:FindFirstChildOfClass("PointLight") then
      local pl = Instance.new("PointLight")
      pl.Range = 13 pl.Brightness = 0.85 pl.Color = rgb(255,182,112) pl.Shadows = false
      pl:SetAttribute("P0_Light", true) pl.Parent = d
      nLuz += 1
    end
  end
end
say("lampioes acesos (PointLight novo):", nLuz)

L:SetAttribute("HEX_P0_OK", true)
H.commit(rec)
say("marcador HEX_P0_OK gravado")
return "P0 OK\n"..table.concat(rep,"\n")