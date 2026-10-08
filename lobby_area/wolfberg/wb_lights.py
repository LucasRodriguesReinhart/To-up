# wb_lights.py - LUZ e VFX do lobby Wolfberg no Roblox (era medieval: sol quente de fim de manha, neblina leve e
# quente, fogo/fumaca/brasas/lanternas; nada de neon, laser ou holograma).
# - LOBBY_PROFILE: Lighting do Edit (= base do AreaAtmosphere, area 0) que o montar grava em APLICAR_LIGHTING;
# - RBX: alcance/brilho/sombra por prefixo de luz (o export_roblox calcula pela energia e corta em 20 / 1,5: as
#   fornalhas precisam de mais); "L_WB_Lamp_*" = NightOnly;
# - vfx_lua(): bloco Lua (EXTRA_LUA do montar) que cria as particulas a partir dos marcadores VFX_* (atributo
#   'particle') em LOBBY_FORJA.VFX + o LocalScript de tremor das luzes de fogo.
import json

LOBBY_PROFILE = {
    "Lighting": {"Brightness": 2.6, "ExposureCompensation": -0.1, "EnvironmentDiffuseScale": 0.55,
                 "EnvironmentSpecularScale": 0.35, "ShadowSoftness": 0.3, "Ambient": [110, 102, 94],
                 "OutdoorAmbient": [156, 150, 140], "ColorShift_Top": [255, 232, 200],
                 "ColorShift_Bottom": [40, 30, 20]},
    "Atmosphere": {"Density": 0.3, "Offset": 0.15, "Color": [214, 206, 190], "Decay": [128, 148, 190],
                   "Glare": 0.25, "Haze": 1.3},
    "Sky": {"SunAngularSize": 16, "MoonAngularSize": 11, "StarCount": 0},
    "BloomEffect": {"Intensity": 0.3, "Size": 28, "Threshold": 1.4},
    "SunRaysEffect": {"Intensity": 0.08, "Spread": 0.2},
    "ColorCorrectionEffect": {"Brightness": 0.02, "Contrast": 0.08, "Saturation": 0.12, "TintColor": [255, 246, 232]},
}
CLOUDS = {"Cover": 0.5, "Density": 0.6, "Color": [255, 252, 246]}

# overrides do Roblox por prefixo (range, brightness, shadows, color)
RBX = {
    "L_WB_Hearth_": dict(range=26.0, brightness=2.4, shadows=True, color=(255, 128, 46)),
    "L_WB_Furnace": dict(range=30.0, brightness=2.0, shadows=True, color=(255, 112, 36)),
    "L_WB_Brazier_": dict(range=18.0, brightness=1.4, shadows=False, color=(255, 130, 50)),
    "L_WB_Shop_": dict(range=16.0, brightness=0.9, shadows=False, color=(255, 200, 130)),
    "L_WB_Lamp_": dict(range=14.0, brightness=0.8, shadows=False, color=(255, 190, 110)),
}
NIGHT = "L_WB_Lamp_"
FLICKER = ("L_WB_Hearth_", "L_WB_Furnace", "L_WB_Brazier_")


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
      host.Size = (kind == 'leaves') and Vector3.new(10, 6, 10) or ((kind == 'dust') and Vector3.new(20, 14, 24) or Vector3.new(2, 1, 2))
      host.CFrame = mk.CFrame
      local pe = Instance.new('ParticleEmitter'); KIND[kind](pe, mk:GetAttribute('size'))
      local rate = mk:GetAttribute('rate'); if rate then pe.Rate = rate end
      if kind == 'leaves' then local r = mk:GetAttribute('radius'); if r then host.Size = Vector3.new(r * 2, r, r * 2) end end
      pe.Parent = host; host.Parent = VF; n += 1
    end
  end
  print(string.format('VFX Wolfberg: %d emissores', n))
  -- tremor das luzes de fogo (fornalhas, forno, braseiros): LocalScript em StarterPlayerScripts
  local SP = game:GetService('StarterPlayer'):WaitForChild('StarterPlayerScripts')
  local old = SP:FindFirstChild('VFX_Wolfberg_Client'); if old then old:Destroy() end
  local ls = Instance.new('LocalScript'); ls.Name = 'VFX_Wolfberg_Client'
  ls.Source = [==[
local RS = game:GetService('RunService')
local root = workspace:WaitForChild('LOBBY_FORJA', 30); if not root then return end
local LT = root:WaitForChild('LIGHTS', 30); if not LT then return end
local fires = {}
for _, p in ipairs(LT:GetChildren()) do
  local n = p.Name
  if string.find(n, '^L_WB_Hearth_') or string.find(n, '^L_WB_Furnace') or string.find(n, '^L_WB_Brazier_') then
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
