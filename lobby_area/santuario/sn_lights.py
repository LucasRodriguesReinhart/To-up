# sn_lights.py - LUZ e VFX do lobby Santuario do Deus-Ferreiro no Roblox (copia adaptada do wb_lights): manha clara
# e quente, neblina azulada leve (casa com a serra pintada), bloom para lava/runas Neon, fogo dos braseiros, brasas da
# bigorna, poeira dourada na praca, folhas, faiscas de runa nos estrados e brilho dos cristais.
# - LOBBY_PROFILE: Lighting do Edit (= base do AreaAtmosphere, area 0) que o montar grava em APLICAR_LIGHTING;
# - RBX: alcance/brilho/sombra por prefixo de luz (o export_roblox calcula pela energia e corta em 20 / 1,5: as
#   fornalhas precisam de mais); "L_WB_Lamp_*" = NightOnly;
# - vfx_lua(): bloco Lua (EXTRA_LUA do montar) que cria as particulas a partir dos marcadores VFX_* (atributo
#   'particle') em LOBBY_FORJA.VFX + o LocalScript de tremor das luzes de fogo.
import json

LOBBY_PROFILE = {
    "Lighting": {"Brightness": 2.8, "ExposureCompensation": 0.0, "EnvironmentDiffuseScale": 0.6,
                 "EnvironmentSpecularScale": 0.3, "ShadowSoftness": 0.35, "Ambient": [118, 112, 106],
                 "OutdoorAmbient": [160, 158, 152], "ColorShift_Top": [255, 236, 206],
                 "ColorShift_Bottom": [36, 32, 30]},
    "Atmosphere": {"Density": 0.28, "Offset": 0.2, "Color": [206, 214, 228], "Decay": [150, 166, 200],
                   "Glare": 0.2, "Haze": 1.2},
    "Sky": {"SunAngularSize": 15, "MoonAngularSize": 11, "StarCount": 0},
    "BloomEffect": {"Intensity": 0.38, "Size": 26, "Threshold": 1.25},
    "SunRaysEffect": {"Intensity": 0.06, "Spread": 0.25},
    "ColorCorrectionEffect": {"Brightness": 0.02, "Contrast": 0.09, "Saturation": 0.14, "TintColor": [255, 248, 236]},
}
CLOUDS = {"Cover": 0.45, "Density": 0.55, "Color": [255, 252, 248]}

# overrides do Roblox por prefixo (range, brightness, shadows, color)
RBX = {
    "L_SN_Hearth": dict(range=28.0, brightness=2.4, shadows=True, color=(255, 128, 46)),
    "L_SN_AnvilCrack": dict(range=40.0, brightness=2.2, shadows=False, color=(255, 120, 40)),
    "L_SN_Brazier_": dict(range=16.0, brightness=1.2, shadows=False, color=(255, 140, 60)),
    "L_SN_Shop": dict(range=16.0, brightness=0.9, shadows=False, color=(255, 200, 130)),
    "L_SN_ShopLegend": dict(range=12.0, brightness=1.2, shadows=False, color=(140, 190, 255)),
    "L_SN_Crystal_": dict(range=14.0, brightness=1.0, shadows=False, color=(255, 170, 80)),
}
NIGHT = "L_SN_Brazier_"           # braseiros: fogo (particula) de dia, luz so a noite (teto de luzes diurnas)
FLICKER = ("L_SN_Hearth", "L_SN_AnvilCrack", "L_SN_Brazier_")


def rbx_for(name):
    best = None
    for k, v in RBX.items():
        if name.startswith(k) and (best is None or len(k) > len(best[0])):
            best = (k, v)
    return best[1] if best else None


def apply_rbx(lights_out):
    n = 0
    for l in lights_out:
        o = rbx_for(l["name"])
        if not o:
            continue
        l["range"] = o["range"]
        l["brightness"] = o["brightness"]
        l["shadows"] = o["shadows"]
        l["color"] = list(o["color"])
        if l["name"].startswith(NIGHT):
            l["night"] = True
        else:
            l["night"] = False
        n += 1
    return n


def lighting_cfg(clock, lat):
    cfg = json.loads(json.dumps(LOBBY_PROFILE))
    cfg["Lighting"]["ClockTime"] = clock
    cfg["Lighting"]["GeographicLatitude"] = lat
    return cfg


# ------------------------------------------------------------------ VFX (particulas) a partir dos marcadores
VFX_LUA = r'''
-- ================= VFX (era medieval): particulas nos marcadores VFX_* (atributo 'particle') =================
do
  local VF = root:FindFirstChild('VFX') or Instance.new('Folder'); VF.Name = 'VFX'; VF.Parent = root
  VF:ClearAllChildren()
  local SMOKE = 'rbxasset://textures/particles/smoke_main.dds'
  local FIRE = 'rbxasset://textures/particles/fire_main.dds'
  local SPARK = 'rbxasset://textures/particles/sparkles_main.dds'
  local function ns(a, b) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(1, b)}) end
  local function ns3(a, m, b, tm) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(tm or 0.5, m), NumberSequenceKeypoint.new(1, b)}) end
  local function cs(a, b) return ColorSequence.new(a, b) end
  local KIND = {
    smoke_heavy = function(pe, size)
      pe.Texture = SMOKE; pe.Rate = 7; pe.Lifetime = NumberRange.new(4.5, 7); pe.Speed = NumberRange.new(6, 9)
      pe.Size = ns(3.0, 11.0); pe.Transparency = ns3(0.35, 0.6, 1.0, 0.6); pe.Color = cs(Color3.fromRGB(96, 92, 90), Color3.fromRGB(200, 196, 192))
      pe.Acceleration = Vector3.new(2.5, 1.5, -1.0); pe.SpreadAngle = Vector2.new(12, 12); pe.Rotation = NumberRange.new(0, 360)
      pe.RotSpeed = NumberRange.new(-20, 20); pe.Drag = 0.6; pe.LightInfluence = 1
    end,
    smoke_thin = function(pe, size)
      pe.Texture = SMOKE; pe.Rate = 2; pe.Lifetime = NumberRange.new(4, 6); pe.Speed = NumberRange.new(3, 5)
      pe.Size = ns(1.2, 5.0); pe.Transparency = ns3(0.5, 0.7, 1.0, 0.6); pe.Color = cs(Color3.fromRGB(150, 146, 144), Color3.fromRGB(220, 218, 216))
      pe.Acceleration = Vector3.new(2.0, 1.0, -0.8); pe.SpreadAngle = Vector2.new(10, 10); pe.Rotation = NumberRange.new(0, 360)
      pe.RotSpeed = NumberRange.new(-15, 15); pe.Drag = 0.6; pe.LightInfluence = 1
    end,
    fire = function(pe, size)
      size = size or 3.0
      pe.Texture = FIRE; pe.Rate = 16; pe.Lifetime = NumberRange.new(0.55, 0.95); pe.Speed = NumberRange.new(3, 5.5)
      pe.Size = ns3(size * 0.55, size, size * 0.2, 0.4); pe.Transparency = ns3(0.1, 0.25, 1.0, 0.6)
      pe.Color = cs(Color3.fromRGB(255, 228, 120), Color3.fromRGB(255, 96, 20)); pe.LightEmission = 1; pe.LightInfluence = 0
      pe.SpreadAngle = Vector2.new(18, 18); pe.Acceleration = Vector3.new(0, 6, 0); pe.Rotation = NumberRange.new(-30, 30)
      pe.RotSpeed = NumberRange.new(-40, 40); pe.Drag = 1.0; pe.ZOffset = 0.5
    end,
    ember = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 5; pe.Lifetime = NumberRange.new(1.2, 2.4); pe.Speed = NumberRange.new(5, 9)
      pe.Size = ns(0.35, 0.05); pe.Transparency = ns(0.0, 1.0); pe.Color = cs(Color3.fromRGB(255, 190, 90), Color3.fromRGB(255, 80, 20))
      pe.LightEmission = 1; pe.LightInfluence = 0; pe.SpreadAngle = Vector2.new(35, 35); pe.Acceleration = Vector3.new(0.5, -3, 0)
      pe.Drag = 1.5; pe.VelocityInheritance = 0
    end,
    water = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 24; pe.Lifetime = NumberRange.new(0.8, 1.2); pe.Speed = NumberRange.new(7, 10)
      pe.Size = ns(0.7, 0.2); pe.Transparency = ns(0.2, 1.0); pe.Color = cs(Color3.fromRGB(220, 240, 255), Color3.fromRGB(150, 200, 240))
      pe.LightEmission = 0.3; pe.SpreadAngle = Vector2.new(14, 14); pe.Acceleration = Vector3.new(0, -24, 0); pe.Drag = 0
    end,
    leaves = function(pe, size)
      pe.Texture = SMOKE; pe.Rate = 0.6; pe.Lifetime = NumberRange.new(4, 7); pe.Speed = NumberRange.new(0.5, 1.5)
      pe.Size = ns(0.55, 0.45); pe.Transparency = ns3(0.3, 0.3, 1.0, 0.85); pe.Color = cs(Color3.fromRGB(120, 170, 60), Color3.fromRGB(190, 150, 60))
      pe.SpreadAngle = Vector2.new(60, 60); pe.Acceleration = Vector3.new(1.2, -1.6, 0.6); pe.Drag = 0.8
      pe.Rotation = NumberRange.new(0, 360); pe.RotSpeed = NumberRange.new(-90, 90); pe.Shape = Enum.ParticleEmitterShape.Sphere
    end,
    rune = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 2; pe.Lifetime = NumberRange.new(2.5, 4); pe.Speed = NumberRange.new(0.6, 1.4)
      pe.Size = ns(0.25, 0.05); pe.Transparency = ns3(0.2, 0.3, 1.0, 0.6); pe.Color = cs(Color3.fromRGB(255, 226, 140), Color3.fromRGB(255, 180, 70))
      pe.LightEmission = 1; pe.LightInfluence = 0; pe.SpreadAngle = Vector2.new(25, 25); pe.Acceleration = Vector3.new(0, 1.2, 0)
      pe.Shape = Enum.ParticleEmitterShape.Box; pe.Drag = 0.4
    end,
    sparkle = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 3; pe.Lifetime = NumberRange.new(1.0, 1.8); pe.Speed = NumberRange.new(0.2, 0.5)
      pe.Size = ns3(0.05, 0.4, 0.05, 0.5); pe.Transparency = ns(0.1, 1.0); pe.Color = cs(Color3.fromRGB(200, 230, 255), Color3.fromRGB(140, 190, 255))
      pe.LightEmission = 1; pe.LightInfluence = 0; pe.SpreadAngle = Vector2.new(180, 180); pe.Shape = Enum.ParticleEmitterShape.Box
    end,
    dust = function(pe, size)
      pe.Texture = SPARK; pe.Rate = 3; pe.Lifetime = NumberRange.new(4, 7); pe.Speed = NumberRange.new(0.2, 0.6)
      pe.Size = ns(0.12, 0.08); pe.Transparency = ns3(1.0, 0.55, 1.0, 0.5); pe.Color = cs(Color3.fromRGB(255, 220, 170), Color3.fromRGB(255, 200, 140))
      pe.LightEmission = 0.6; pe.SpreadAngle = Vector2.new(180, 180); pe.Shape = Enum.ParticleEmitterShape.Box; pe.Drag = 0.2
    end,
  }
  local n = 0
  for _, mk in ipairs(MKF:GetChildren()) do
    local kind = mk:GetAttribute('particle')
    if kind and KIND[kind] then
      local host = Instance.new('Part'); host.Name = mk.Name; host.Anchored = true; host.CanCollide = false; host.CanQuery = false
      host.CanTouch = false; host.CastShadow = false; host.Transparency = 1
      host.Size = (kind == 'leaves') and Vector3.new(10, 6, 10) or ((kind == 'dust') and Vector3.new(60, 16, 60) or (((kind == 'rune') or (kind == 'sparkle')) and Vector3.new(6, 2, 6) or Vector3.new(2, 1, 2)))
      host.CFrame = mk.CFrame
      local pe = Instance.new('ParticleEmitter'); KIND[kind](pe, mk:GetAttribute('size'))
      local rate = mk:GetAttribute('rate'); if rate then pe.Rate = rate end
      if kind == 'leaves' then local r = mk:GetAttribute('radius'); if r then host.Size = Vector3.new(r * 2, r, r * 2) end end
      pe.Parent = host; host.Parent = VF; n += 1
    end
  end
  print(string.format('VFX Santuario: %d emissores', n))
  -- tremor das luzes de fogo (fornalhas, forno, braseiros): LocalScript em StarterPlayerScripts
  local SP = game:GetService('StarterPlayer'):WaitForChild('StarterPlayerScripts')
  local old = SP:FindFirstChild('VFX_Santuario_Client'); if old then old:Destroy() end
  local ls = Instance.new('LocalScript'); ls.Name = 'VFX_Santuario_Client'
  ls.Source = [==[
local RS = game:GetService('RunService')
local root = workspace:WaitForChild('LOBBY_FORJA', 30); if not root then return end
local LT = root:WaitForChild('LIGHTS', 30); if not LT then return end
local fires = {}
for _, p in ipairs(LT:GetChildren()) do
  local n = p.Name
  if string.find(n, '^L_SN_Hearth') or string.find(n, '^L_SN_AnvilCrack') or string.find(n, '^L_SN_Brazier_') then
    local l = p:FindFirstChildOfClass('PointLight')
    if l then table.insert(fires, {l = l, b = l.Brightness, r = l.Range, ph = math.random() * 6.28}) end
  end
end
if #fires == 0 then return end
local t = 0
RS.RenderStepped:Connect(function(dt)
  t += dt
  for _, f in ipairs(fires) do
    local k = 1 + 0.10 * math.sin(t * 9.1 + f.ph) + 0.06 * math.sin(t * 23.7 + f.ph * 1.7) + 0.04 * math.noise(t * 4, f.ph)
    f.l.Brightness = f.b * k
    f.l.Range = f.r * (1 + 0.04 * math.sin(t * 7.3 + f.ph))
  end
end)
]==]
  ls.Parent = SP
end
'''


def vfx_lua():
    return VFX_LUA
