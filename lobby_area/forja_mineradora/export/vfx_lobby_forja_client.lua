--[[
vfx_lobby_forja_client.lua   (gerado por export_vfx.py - vfx-forja-2 - nao editar a mao)
VFX e MOVIMENTO do Lobby Vila-Forja - ANIMACAO NO CLIENTE

ONDE COLOCAR: LocalScript em StarterPlayer > StarterPlayerScripts.
Precisa da montagem (vfx_lobby_forja.lua) feita antes: ela deixa ReplicatedStorage.LOBBY_FORJA_VFX e as tags.

O que faz (tudo local, nada replica para o servidor; relogio = workspace:GetServerTimeNow, todos veem a mesma fase):
  - gira a roda d'agua + eixo baixo, o eixo alto (pinhao + engrenagem da parede) e a engrenagem menor, bate o
    martinete (faiscas no golpe), bombeia o fole (rajada de chamas, faiscas na torre e clarao na lareira no pico);
  - respingos da roda sincronizados com as pas que entram e saem da agua;
  - espirais dos portais: gira as 2 ImageLabels do SurfaceGui (interna 2,3x) + o disco; pulso de brilho, aro e anel;
  - carrinho de mina ocasional: sai do patio da mina, para na balanca, descarrega no portao da forja e volta;
  - golpes do Ignis (ritmo interno ou KeyframeMarker "Golpe" no rig com a tag FORJA_Ignis) e chiado da tempera;
  - pulsos: cristais, metal quente, brasas, chamas, aros dos portais; flicker das lanternas e do fogo.
Desempenho: 1 conexao PreRender com BulkMoveTo so para o que esta perto da camera; pulsos a 20 Hz, luzes a 15 Hz,
liga/desliga de emissores a 2 Hz. Streaming: registra/desregistra por tag (CollectionService), sem WaitForChild
no workspace. Respeita GuiService.ReducedMotionEnabled. CFG:SetAttribute("VFX_Pause", true) congela tudo.
]]

local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local GuiService = game:GetService("GuiService")

if not RunService:IsClient() then return end

local DATA = {}
DATA.version = "vfx-forja-2"
DATA.exportId = "e4dec731"
-- trilho percorrido pelo carrinho (canonico; o cliente aplica VFX_RootCF)
DATA.path = {
  Vector3.new(-58.537, 4.3, 32.59), Vector3.new(-58.027, 4.3, 31.729), Vector3.new(-57.613, 4.3, 30.821),
  Vector3.new(-57.22, 4.3, 29.901), Vector3.new(-56.826, 4.3, 28.982), Vector3.new(-56.491, 4.3, 28.042),
  Vector3.new(-56.225, 4.3, 27.078), Vector3.new(-55.959, 4.3, 26.114), Vector3.new(-55.727, 4.3, 25.143),
  Vector3.new(-55.583, 4.3, 24.154), Vector3.new(-55.438, 4.3, 23.164), Vector3.new(-55.311, 4.3, 22.173),
  Vector3.new(-55.267, 4.3, 21.174), Vector3.new(-55.223, 4.3, 20.175), Vector3.new(-55.179, 4.3, 19.176),
  Vector3.new(-55.206, 4.3, 18.176), Vector3.new(-55.234, 4.3, 17.177), Vector3.new(-55.261, 4.3, 16.177),
  Vector3.new(-55.316, 4.3, 15.179), Vector3.new(-55.384, 4.3, 14.181), Vector3.new(-55.451, 4.3, 13.183),
  Vector3.new(-55.521, 4.3, 12.186), Vector3.new(-55.601, 4.3, 11.189), Vector3.new(-55.681, 4.3, 10.192),
  Vector3.new(-55.761, 4.3, 9.195), Vector3.new(-55.836, 4.3, 8.198), Vector3.new(-55.906, 4.3, 7.201),
  Vector3.new(-55.975, 4.3, 6.203), Vector3.new(-56.045, 4.3, 5.205), Vector3.new(-56.104, 4.3, 4.207),
  Vector3.new(-56.145, 4.3, 3.208), Vector3.new(-56.186, 4.3, 2.209), Vector3.new(-56.227, 4.3, 1.21),
  Vector3.new(-56.268, 4.3, 0.211), Vector3.new(-56.27, 4.3, -0.789), Vector3.new(-56.269, 4.3, -1.789),
  Vector3.new(-56.269, 4.3, -2.789), Vector3.new(-56.268, 4.3, -3.789), Vector3.new(-56.263, 4.3, -4.789),
  Vector3.new(-56.212, 4.3, -5.788), Vector3.new(-56.162, 4.3, -6.787), Vector3.new(-56.112, 4.3, -7.785),
  Vector3.new(-56.061, 4.3, -8.784), Vector3.new(-56.011, 4.3, -9.783), Vector3.new(-55.795, 4.3, -10.755),
  Vector3.new(-55.534, 4.3, -11.721), Vector3.new(-55.272, 4.3, -12.686), Vector3.new(-54.827, 4.3, -13.569),
  Vector3.new(-54.282, 4.3, -14.408), Vector3.new(-53.719, 4.3, -15.229), Vector3.new(-52.922, 4.3, -15.833),
  Vector3.new(-52.125, 4.3, -16.436), Vector3.new(-51.231, 4.3, -16.863), Vector3.new(-50.292, 4.3, -17.209),
  Vector3.new(-49.344, 4.3, -17.514), Vector3.new(-48.355, 4.3, -17.668), Vector3.new(-47.367, 4.3, -17.821),
  Vector3.new(-46.373, 4.3, -17.913), Vector3.new(-45.374, 4.3, -17.95), Vector3.new(-44.375, 4.3, -17.986),
  Vector3.new(-43.375, 4.3, -18), Vector3.new(-42.375, 4.3, -18), Vector3.new(-41.375, 4.3, -18),
  Vector3.new(-40.375, 4.3, -18), Vector3.new(-39.375, 4.3, -18), Vector3.new(-38.375, 4.3, -18),
  Vector3.new(-37.375, 4.3, -18), Vector3.new(-36.375, 4.3, -18), Vector3.new(-35.375, 4.3, -18),
  Vector3.new(-34.375, 4.3, -18), Vector3.new(-33.375, 4.3, -18), Vector3.new(-32.375, 4.3, -18),
  Vector3.new(-31.375, 4.3, -18), Vector3.new(-30.375, 4.3, -18),
}
DATA.cart = {rest = 4.735, weigh = 24.994, far = 68.36, cycle = 48, vOut = 6, vBack = 7.5, acc = 3,
  stopWeigh = 3, stopFar = 4.5, unloadAt = 1.6, reloadAt = 2.2}
DATA.hammer = {rise0 = 0.125, rise1 = 0.533, fall0 = 0.55, hit = 0.6, bounce = 0.667}
DATA.ignis = {cycle = 4.4, hits = {{0, 0.7}, {0.75, 0.7}, {1.5, 1.35}}, quenchEvery = 3, pos = Vector3.new(0.5, 8.9, 10)}
-- pas da roda: a pa k esta no angulo k*step - w*t (plano da roda); entra na agua em aIn e sai em aOut
DATA.wheel = {speed = 0.628, step = 0.393, aIn = -0.006, aOut = -3.136, pos = Vector3.new(62, 11, -20)}
DATA.portals = {
  {key = "Naruto", idx = 0, center = Vector3.new(-108, 41.2, -113.9)},
  {key = "DragonBall", idx = 1, center = Vector3.new(-76, 41.2, -113.9)},
  {key = "DemonSlayer", idx = 2, center = Vector3.new(-44, 41.2, -113.9)},
  {key = "ShadowGarden", idx = 3, center = Vector3.new(44, 41.2, -113.9)},
  {key = "OnePiece", idx = 4, center = Vector3.new(76, 41.2, -113.9)},
  {key = "OnePunchMan", idx = 5, center = Vector3.new(108, 41.2, -113.9)},
}

local CFG = ReplicatedStorage:WaitForChild("LOBBY_FORJA_VFX", 60)
if not CFG then
  warn("[VFX Forja] ReplicatedStorage.LOBBY_FORJA_VFX nao existe: rode vfx_lobby_forja.lua (montagem) antes")
  return
end
if CFG:GetAttribute("VFX_Version") and CFG:GetAttribute("VFX_Version") ~= DATA.version then
  warn(string.format("[VFX Forja] montagem %s e cliente %s: rode os dois do mesmo export", tostring(CFG:GetAttribute("VFX_Version")), DATA.version))
end
local cfgId = CFG:GetAttribute("VFX_ExportId")
if cfgId and cfgId ~= "" and DATA.exportId and cfgId ~= DATA.exportId then
  warn(string.format("[VFX Forja] montagem do passe %s e cliente do passe %s: o trilho do carrinho e a fase das pas "
    .. "podem nao bater (use os dois .lua do mesmo export_all.py)", cfgId, DATA.exportId))
end
local rootCF = CFG:GetAttribute("VFX_RootCF")
if typeof(rootCF) ~= "CFrame" then rootCF = CFrame.new() end

local TAU = math.pi * 2
local SPIN_DIST, HAMMER_DIST, CART_DIST, SWIRL_DIST, WHEEL_DIST = 340, 220, 420, 520, 260
local PULSE_DIST = {crystal = 230, heat = 200, ember = 450, lantern = 200, portalrim = 480}
local LIGHT_DIST = {lantern = 170, fire = 260, crystal = 220, portal = 480, flash = 260}
local HOT = Color3.fromRGB(255, 196, 120)
local WHITE = Color3.new(1, 1, 1)

local reduced = false
local function readReduced()
  local ok, v = pcall(function() return GuiService.ReducedMotionEnabled end)
  reduced = ok and v == true
end
readReduced()
pcall(function() GuiService:GetPropertyChangedSignal("ReducedMotionEnabled"):Connect(readReduced) end)

local localFolder = Instance.new("Folder")
localFolder.Name = "FORJA_VFX_LOCAL"
localFolder.Parent = workspace

local function angleAt(speed, t)
  if speed == 0 then return 0 end
  local period = TAU / math.abs(speed)
  return speed * (t % period)
end
local function seedOf(v) return (v.X * 0.137 + v.Y * 0.071 + v.Z * 0.113) % 97 + 0.37 end
local function watch(tag, add, remove)
  CollectionService:GetInstanceAddedSignal(tag):Connect(add)
  CollectionService:GetInstanceRemovedSignal(tag):Connect(remove)
  for _, inst in ipairs(CollectionService:GetTagged(tag)) do task.spawn(add, inst) end
end
local function posOf(inst)
  if inst:IsA("BasePart") then return inst.Position end
  if inst:IsA("Attachment") then return inst.WorldPosition end
  local p = inst.Parent
  if p then return posOf(p) end
  return Vector3.zero
end

-- ---------------------------------------------------------------- eventos (faiscas, claroes, rajadas)
local bursts, flash = {}, {}
local function fire(ev, strength)
  strength = strength or 1
  local cam = workspace.CurrentCamera
  local cp = cam and cam.CFrame.Position or Vector3.zero
  for em, b in pairs(bursts) do
    if b.event == ev and em.Parent and (b.pos - cp).Magnitude < 300 then
      em:Emit(math.max(1, math.floor(b.count * strength + 0.5)))
    end
  end
  flash[ev] = math.max(flash[ev] or 0, math.min(1.5, strength))
end
watch("FORJA_Burst", function(e)
  if not e:IsA("ParticleEmitter") or not e:IsDescendantOf(workspace) then return end
  bursts[e] = {event = e:GetAttribute("VFX_Event") or "", count = e:GetAttribute("VFX_Count") or 8, pos = posOf(e)}
end, function(e) bursts[e] = nil end)
local EV = CFG:FindFirstChild("Evento")
if EV and EV:IsA("BindableEvent") then
  EV.Event:Connect(function(name, strength) if type(name) == "string" then fire(name, tonumber(strength) or 1) end end)
end

-- ---------------------------------------------------------------- rotores (roda, engrenagens, discos dos portais)
local spins = {}
watch("FORJA_Spin", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) or spins[p] then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  spins[p] = {pivot = pivot, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home,
    speed = p:GetAttribute("VFX_Speed") or 0, phase = p:GetAttribute("VFX_Phase") or 0, portal = p:GetAttribute("VFX_Portal")}
end, function(p) spins[p] = nil end)

-- ---------------------------------------------------------------- martinete
local H = DATA.hammer
local function smooth(x) x = math.clamp(x, 0, 1) return x * x * (3 - 2 * x) end
local function hammerLift(u)
  if u < H.rise0 then return 0 end
  if u < H.rise1 then return smooth((u - H.rise0) / (H.rise1 - H.rise0)) end
  if u < H.fall0 then return 1 end
  if u < H.hit then local f = (u - H.fall0) / (H.hit - H.fall0) return 1 - f * f end
  if u < H.bounce then return 0.08 * math.sin(math.pi * (u - H.hit) / (H.bounce - H.hit)) end
  return 0
end
local hammers, hammerGroups = {}, {}
watch("FORJA_Hammer", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  local ev = p:GetAttribute("VFX_Event") or "martinete"
  local g = hammerGroups[ev]
  if not g then
    g = {speed = p:GetAttribute("VFX_Speed") or 0.6, camPhase = p:GetAttribute("VFX_CamPhase") or 0,
      cams = math.max(1, p:GetAttribute("VFX_Cams") or 3), rest = p:GetAttribute("VFX_Rest") or 0,
      lift = p:GetAttribute("VFX_Lift") or 0.15, lastU = nil, angle = 0, pivot = pivot}
    hammerGroups[ev] = g
  end
  hammers[p] = {group = g, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home}
end, function(p) hammers[p] = nil end)

-- ---------------------------------------------------------------- fole: angulo = rest + lift * (0.5 - 0.5 cos(k w t))
local pumps, pumpGroups = {}, {}
watch("FORJA_Pump", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  local ev = p:GetAttribute("VFX_Event") or "foles"
  local g = pumpGroups[ev]
  if not g then
    g = {w = (p:GetAttribute("VFX_K") or 2) * (p:GetAttribute("VFX_Speed") or 0.63), rest = p:GetAttribute("VFX_Rest") or 0,
      lift = p:GetAttribute("VFX_Lift") or 0.14, lastPh = nil, angle = 0, pivot = pivot}
    pumpGroups[ev] = g
  end
  pumps[p] = {group = g, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home}
end, function(p) pumps[p] = nil end)

-- ---------------------------------------------------------------- espirais dos portais (SurfaceGui)
local swirls = {}
watch("FORJA_Swirl", function(h)
  if not h:IsA("BasePart") or not h:IsDescendantOf(workspace) then return end
  local sg = h:FindFirstChildOfClass("SurfaceGui")
  if not sg then return end
  swirls[h] = {pos = h.Position, sg = sg, ext = sg:FindFirstChild("Externa"), int = sg:FindFirstChild("Interna"),
    speed = h:GetAttribute("VFX_Speed") or 0.9, mul = h:GetAttribute("VFX_InnerMul") or 2.3,
    bright = h:GetAttribute("VFX_Bright") or sg.Brightness, portal = h:GetAttribute("VFX_Portal") or ""}
end, function(h) swirls[h] = nil end)

-- ---------------------------------------------------------------- pulsos de cor e luzes
local pulses, lights, emitters = {}, {}, {}
watch("FORJA_Pulse", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local base = p:GetAttribute("VFX_BaseColor")
  if typeof(base) ~= "Color3" then base = p.Color end
  local kind = p:GetAttribute("VFX_Kind") or "crystal"
  pulses[p] = {kind = kind, event = p:GetAttribute("VFX_Event") or "", base = base, hi = base:Lerp(WHITE, 0.45),
    amp = p:GetAttribute("VFX_Amp") or 1, pos = p.Position, seed = seedOf(p.Position), maxd = PULSE_DIST[kind] or 220}
end, function(p) pulses[p] = nil end)
watch("FORJA_Flicker", function(l)
  if not l:IsA("Light") or not l:IsDescendantOf(workspace) then return end
  local kind = l:GetAttribute("VFX_Kind") or "lantern"
  local pos = posOf(l)
  lights[l] = {kind = kind, event = l:GetAttribute("VFX_Event") or "", base = l:GetAttribute("VFX_Base") or l.Brightness,
    pos = pos, seed = seedOf(pos), maxd = LIGHT_DIST[kind] or 200}
end, function(l) lights[l] = nil end)
watch("FORJA_Emitter", function(e)
  if not e:IsA("ParticleEmitter") or not e:IsDescendantOf(workspace) then return end
  emitters[e] = {pos = posOf(e), maxd = e:GetAttribute("VFX_MaxDist") or 400}
end, function(e) emitters[e] = nil end)

-- ---------------------------------------------------------------- Ignis: rig real (marker "Golpe") ou ritmo interno
local lastRigStrike = -1e9
local function hookAnimator(animator)
  local function hookTrack(track)
    track:GetMarkerReachedSignal("Golpe"):Connect(function(param)
      lastRigStrike = os.clock()
      fire("ignis", tonumber(param) or 1)
    end)
  end
  animator.AnimationPlayed:Connect(hookTrack)
  for _, tr in ipairs(animator:GetPlayingAnimationTracks()) do hookTrack(tr) end
end
watch("FORJA_Ignis", function(model)
  task.spawn(function()
    for _ = 1, 20 do
      local an = model:FindFirstChildWhichIsA("Animator", true)
      if an then hookAnimator(an) return end
      task.wait(0.5)
    end
  end)
end, function() end)

-- ---------------------------------------------------------------- carrinho de mina
local cart
local function setupCart()
  local tpl = CFG:FindFirstChild("MineCart")
  if not tpl or #DATA.path < 2 then return end
  local restCF = tpl:GetAttribute("VFX_RestCF")
  if typeof(restCF) ~= "CFrame" then restCF = tpl:GetPivot() end
  local m = tpl:Clone()
  m.Name = "Carrinho_Local"
  m.Parent = localFolder
  local c = {model = m, parts = {}, offs = {}, load = {}, loaded = nil, pts = {}, cum = {}, idx = 1}
  for _, d in ipairs(m:GetDescendants()) do
    if d:IsA("BasePart") then
      table.insert(c.parts, d)
      table.insert(c.offs, restCF:ToObjectSpace(d.CFrame))
      if d:GetAttribute("VFX_Load") then table.insert(c.load, d) end
      d.CanCollide = false
      d.CanQuery = false
      d.CanTouch = false
    end
  end
  for i, p in ipairs(DATA.path) do
    c.pts[i] = rootCF * p
    c.cum[i] = (i == 1) and 0 or (c.cum[i - 1] + (c.pts[i] - c.pts[i - 1]).Magnitude)
  end
  c.up = rootCF.UpVector
  if c.parts[1] then
    local dust = Instance.new("ParticleEmitter")
    dust.Name = "Po"
    dust.Texture = "rbxasset://textures/particles/smoke_main.dds"
    dust.Color = ColorSequence.new(Color3.fromRGB(150, 138, 124))
    dust.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 3.5)})
    dust.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 1)})
    dust.Lifetime = NumberRange.new(0.8, 1.4)
    dust.Speed = NumberRange.new(2, 4)
    dust.SpreadAngle = Vector2.new(70, 70)
    dust.Drag = 2
    dust.Rate = 0
    dust.LightInfluence = 1
    dust.Parent = c.parts[1]
    c.dust = dust
  end
  local C = DATA.cart
  local function moveDur(d, v, a)
    if d <= v * v / a then return 2 * math.sqrt(d / a) end
    return d / v + v / a
  end
  local segs = {}
  local function mv(s0, s1, v) table.insert(segs, {kind = "move", s0 = s0, s1 = s1, v = v, dur = moveDur(math.abs(s1 - s0), v, C.acc)}) end
  local function st(s, dur, tag) table.insert(segs, {kind = "stop", s0 = s, s1 = s, dur = dur, tag = tag}) end
  if C.weigh then
    mv(C.rest, C.weigh, C.vOut)
    st(C.weigh, C.stopWeigh, "balanca")
    mv(C.weigh, C.far, C.vOut)
  else
    mv(C.rest, C.far, C.vOut)
  end
  st(C.far, C.stopFar, "descarga")
  mv(C.far, C.rest, C.vBack)
  local used = 0
  for _, s in ipairs(segs) do used += s.dur end
  table.insert(segs, {kind = "stop", s0 = C.rest, s1 = C.rest, dur = math.max(4, C.cycle - used), tag = "carga"})
  local t0 = 0
  for _, s in ipairs(segs) do s.t0 = t0 t0 += s.dur end
  c.segs = segs
  c.cycle = t0
  c.idx = 1
  cart = c
end
local function trapezoid(d, v, a, tau)
  local ta = v / a
  if d <= v * ta then
    local tt = math.sqrt(d / a)
    if tau < tt then return 0.5 * a * tau * tau end
    local r = math.max(0, 2 * tt - tau)
    return d - 0.5 * a * r * r
  end
  local T = d / v + ta
  if tau < ta then return 0.5 * a * tau * tau end
  if tau < T - ta then return 0.5 * a * ta * ta + v * (tau - ta) end
  local r = math.max(0, T - tau)
  return d - 0.5 * a * r * r
end
local function cartPos(c, s)
  local pts, cum = c.pts, c.cum
  local n = #pts
  s = math.clamp(s, 0, cum[n])
  local i = math.clamp(c.idx, 1, n - 1)
  while i > 1 and cum[i] > s do i -= 1 end
  while i < n - 1 and cum[i + 1] < s do i += 1 end
  c.idx = i
  local span = cum[i + 1] - cum[i]
  local f = span > 0 and (s - cum[i]) / span or 0
  return pts[i]:Lerp(pts[i + 1], f)
end
local function cartCF(c, s)
  local p = cartPos(c, s)
  local fwd = cartPos(c, s + 1.2) - cartPos(c, s - 1.2)
  fwd = fwd - c.up * fwd:Dot(c.up)
  if fwd.Magnitude < 1e-3 then fwd = rootCF.RightVector end
  return CFrame.fromMatrix(p, fwd.Unit, c.up)
end
local function cartState(c, t)
  local tc = t % c.cycle
  for _, s in ipairs(c.segs) do
    if tc < s.t0 + s.dur then
      local tau = tc - s.t0
      if s.kind == "stop" then return s.s0, s, tau end
      local d = math.abs(s.s1 - s.s0)
      local x = trapezoid(d, s.v, DATA.cart.acc, tau)
      return s.s0 + (s.s1 > s.s0 and x or -x), s, tau
    end
  end
  local last = c.segs[#c.segs]
  return last.s0, last, last.dur
end
local function cartLoaded(c, seg, tau)
  -- carregado na ida; descarrega no portao da forja; recarrega parado no patio da mina
  local after = false
  for _, s in ipairs(c.segs) do
    if s == seg then break end
    if s.tag == "descarga" then after = true end
  end
  if seg.tag == "descarga" then return tau < DATA.cart.unloadAt end
  if seg.tag == "carga" then return tau >= DATA.cart.reloadAt end
  return not after
end
task.spawn(function()
  for _ = 1, 30 do
    if CFG:FindFirstChild("MineCart") then setupCart() return end
    task.wait(1)
  end
end)

-- ---------------------------------------------------------------- relogios (portais, Ignis, pas da roda)
local portalW = {}
for _, p in ipairs(DATA.portals) do portalW[p.key] = {pos = rootCF * p.center, idx = p.idx, last = nil} end
local PORTAL_PERIOD = 3.6
local ignisPos = rootCF * DATA.ignis.pos
local lastIgnis, ignisCycles = nil, 0
local WH = DATA.wheel
local wheelPos = rootCF * WH.pos
local lastIn, lastOut

-- ---------------------------------------------------------------- laco
local moveParts, moveCFs = {}, {}
local accPulse, accLight, accEm = 0, 0, 0
local okStep, step = pcall(function() return RunService.PreRender end)
if not okStep or not step then step = RunService.RenderStepped end
step:Connect(function(dt)
  if CFG:GetAttribute("VFX_Pause") then return end
  local cam = workspace.CurrentCamera
  if not cam then return end
  local cp = cam.CFrame.Position
  local t = workspace:GetServerTimeNow()
  local tn = t % 3600 -- ruido/seno com numeros pequenos (math.noise perde precisao com ~1e9)
  local motion = reduced and 0.35 or 1
  table.clear(moveParts)
  table.clear(moveCFs)
  local n = 0

  -- rotores
  for p, e in pairs(spins) do
    if (e.pivot - cp).Magnitude < SPIN_DIST then
      local sp = e.speed * (e.portal and motion or 1)
      n += 1
      moveParts[n] = p
      moveCFs[n] = e.pivotCF * CFrame.fromAxisAngle(e.axis, e.phase + angleAt(sp, t)) * e.rel
    end
  end

  -- martinete (fase vem do eixo da roda: 1 golpe por came)
  for ev, g in pairs(hammerGroups) do
    local span = TAU / g.cams
    local u = ((angleAt(g.speed, t) - g.camPhase) % span) / span
    local near = (g.pivot - cp).Magnitude < HAMMER_DIST
    if g.lastU and near then
      local crossed = (g.lastU < H.hit and u >= H.hit) or (u < g.lastU and g.lastU < H.hit)
      if crossed and dt < 0.5 then fire(ev, 1) end
    end
    g.lastU = u
    g.near = near
    g.angle = g.rest + g.lift * hammerLift(u)
  end
  for p, h in pairs(hammers) do
    if h.group.near then
      n += 1
      moveParts[n] = p
      moveCFs[n] = h.pivotCF * CFrame.fromAxisAngle(h.axis, h.group.angle) * h.rel
    end
  end

  -- fole (no pico do curso: rajada nas chamas/brasas, faiscas na torre, clarao na lareira)
  for ev, g in pairs(pumpGroups) do
    local ph = angleAt(g.w, t)
    local near = (g.pivot - cp).Magnitude < HAMMER_DIST
    if g.lastPh and near and dt < 0.5 then
      if (g.lastPh < math.pi and ph >= math.pi) then fire(ev, 1) end
    end
    g.lastPh = ph
    g.near = near
    g.angle = g.rest + g.lift * (0.5 - 0.5 * math.cos(ph))
  end
  for p, h in pairs(pumps) do
    if h.group.near then
      n += 1
      moveParts[n] = p
      moveCFs[n] = h.pivotCF * CFrame.fromAxisAngle(h.axis, h.group.angle) * h.rel
    end
  end

  -- carrinho
  if cart then
    local s, seg, tau = cartState(cart, t)
    local cf = cartCF(cart, s)
    if (cf.Position - cp).Magnitude < CART_DIST then
      for i, part in ipairs(cart.parts) do
        n += 1
        moveParts[n] = part
        moveCFs[n] = cf * cart.offs[i]
      end
      local loaded = cartLoaded(cart, seg, tau)
      if loaded ~= cart.loaded then
        if cart.loaded ~= nil and cart.dust then cart.dust:Emit(8) end
        cart.loaded = loaded
        for _, part in ipairs(cart.load) do part.Transparency = loaded and 0 or 1 end
      end
    end
  end

  if n > 0 then workspace:BulkMoveTo(moveParts, moveCFs, Enum.BulkMoveMode.FireCFrameChanged) end

  -- espirais: mesmo relogio do disco (Rotation positiva = horario visto de frente = giro negativo em volta da normal)
  for _, s in pairs(swirls) do
    if (s.pos - cp).Magnitude < SWIRL_DIST then
      local sp = s.speed * motion
      if s.ext then s.ext.Rotation = (-math.deg(angleAt(sp, t))) % 360 end
      if s.int then s.int.Rotation = (-math.deg(angleAt(sp * s.mul, t))) % 360 end
      s.sg.Brightness = s.bright * (1 + 0.45 * (flash["portal:" .. s.portal] or 0))
    end
  end

  -- pas da roda: a pa k esta em k*step - w*t; entra na agua em aIn e sai em aOut
  if (wheelPos - cp).Magnitude < WHEEL_DIST then
    local th = angleAt(WH.speed, t)
    local nIn = math.floor((th + WH.aIn) / WH.step)
    local nOut = math.floor((th + WH.aOut) / WH.step)
    if lastIn and nIn ~= lastIn and dt < 0.5 then fire("roda:entra", 1) end
    if lastOut and nOut ~= lastOut and dt < 0.5 then fire("roda:sai", 1) end
    lastIn, lastOut = nIn, nOut
  else
    lastIn, lastOut = nil, nil
  end

  -- portais: pulso de luz + anel + aro + brilho da espiral
  for key, pw in pairs(portalW) do
    local ph = (t + pw.idx * 0.55) % PORTAL_PERIOD
    if pw.last and ph < pw.last and (pw.pos - cp).Magnitude < 480 then fire("portal:" .. key, 1) end
    pw.last = ph
  end
  -- Ignis: ritmo interno enquanto o rig nao manda "Golpe"; a tempera chia a cada quenchEvery ciclos
  if os.clock() - lastRigStrike > 12 and (ignisPos - cp).Magnitude < 260 then
    local tc = t % DATA.ignis.cycle
    if lastIgnis then
      for _, hit in ipairs(DATA.ignis.hits) do
        local ht = hit[1]
        if (lastIgnis < ht and tc >= ht) or (tc < lastIgnis and (lastIgnis < ht or tc >= ht)) then fire("ignis", hit[2]) end
      end
      if tc < lastIgnis then
        ignisCycles += 1
        if ignisCycles % DATA.ignis.quenchEvery == 0 then fire("tempera", 1) end
      end
    end
    lastIgnis = tc
  else
    lastIgnis = nil
  end

  -- decaimento dos claroes
  local k = math.exp(-dt * 7)
  for ev, v in pairs(flash) do
    v *= k
    flash[ev] = (v > 0.01) and v or nil
  end

  -- claroes (todo frame, sao poucos)
  for l, e in pairs(lights) do
    if e.kind == "flash" then l.Brightness = e.base * (flash[e.event] or 0) end
  end

  -- pulsos de cor (20 Hz)
  accPulse += dt
  if accPulse >= 0.05 then
    accPulse = 0
    local flick = reduced and 0.3 or 1
    for p, e in pairs(pulses) do
      if (e.pos - cp).Magnitude < e.maxd then
        local c
        if e.kind == "crystal" then
          local s = 0.5 + 0.5 * math.sin(tn * 1.9 + e.seed)
          c = e.base:Lerp(e.hi, (0.08 + 0.34 * s * s) * (reduced and 0.5 or 1))
        elseif e.kind == "heat" then
          local br = 0.5 + math.noise(tn * 0.9, e.seed, 0.5)
          c = e.base:Lerp(HOT, math.clamp(0.06 + 0.14 * br + 0.8 * (flash[e.event] or 0), 0, 1))
        elseif e.kind == "ember" then
          local f0 = math.clamp(0.9 + 0.22 * math.noise(tn * 1.6, e.seed, 0.3) * flick, 0.7, 1)
          local f = 1 - e.amp * (1 - f0)
          c = Color3.new(e.base.R * f, e.base.G * f, e.base.B * f)
        elseif e.kind == "lantern" then
          local f = math.clamp(0.96 + 0.1 * math.noise(tn * 5.5, e.seed, 0.7) * flick, 0.85, 1)
          c = Color3.new(e.base.R * f, e.base.G * f, e.base.B * f)
        elseif e.kind == "portalrim" then
          c = e.base:Lerp(WHITE, math.clamp(0.08 + 0.1 * math.sin(tn * 2.6 + e.seed) + 0.55 * (flash[e.event] or 0), 0, 1))
        end
        if c then p.Color = c end
      end
    end
  end

  -- flicker das luzes (15 Hz)
  accLight += dt
  if accLight >= 0.066 then
    accLight = 0
    local flick = reduced and 0.3 or 1
    for l, e in pairs(lights) do
      if e.kind ~= "flash" and (e.pos - cp).Magnitude < e.maxd then
        local f = 1
        if e.kind == "lantern" then
          f = 1 + (0.12 * math.noise(tn * 2.1, e.seed, 0.2) + 0.06 * math.noise(tn * 9.3, e.seed, 0.8)) * flick
        elseif e.kind == "fire" then
          f = 1 + (0.3 * math.noise(tn * 3.3, e.seed, 0.4) + 0.16 * math.noise(tn * 11, e.seed, 0.9)) * flick
          f *= 1 + 0.3 * (flash[e.event] or 0)
        elseif e.kind == "crystal" then
          f = 1 + 0.15 * math.sin(tn * 1.9 + e.seed)
        elseif e.kind == "portal" then
          f = 1 + 0.1 * math.sin(tn * 2.2 + e.seed) + 0.9 * (flash[e.event] or 0)
        end
        l.Brightness = e.base * f
      end
    end
  end

  -- emissores continuos longe da camera ficam desligados (2 Hz)
  accEm += dt
  if accEm >= 0.5 then
    accEm = 0
    for em, e in pairs(emitters) do
      local on = (e.pos - cp).Magnitude < e.maxd
      if em.Enabled ~= on then em.Enabled = on end
    end
  end
end)
