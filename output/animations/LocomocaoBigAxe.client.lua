-- Big Axe Stance Bundle by Lotucupi, bundle 272148363726799.
-- Uses the imported KeyframeSequences locally for every player character.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local sequences = ReplicatedStorage:WaitForChild("BigAxeKeyframes")
local clips = {}
for _, sequence in ipairs(sequences:GetChildren()) do
 if sequence:IsA("KeyframeSequence") then
  local clip = {channels = {}, length = 0}
  for _, frame in ipairs(sequence:GetKeyframes()) do
   clip.length = math.max(clip.length, frame.Time)
   for _, pose in ipairs(frame:GetDescendants()) do
    if pose:IsA("Pose") then
     local keys = clip.channels[pose.Name] or {}
     clip.channels[pose.Name] = keys
     table.insert(keys, {time = frame.Time, cf = pose.CFrame, weight = pose.Weight})
    end
   end
  end
  for _, keys in pairs(clip.channels) do
   table.sort(keys, function(a, b) return a.time < b.time end)
  end
  clips[sequence.Name] = clip
 end
end
for _, name in ipairs({"idle", "walk", "run", "jump", "fall", "climb", "swim", "swimidle"}) do
 if not clips[name] or clips[name].length <= 0 then
  warn("[BigAxe] Keyframes ausentes: " .. name)
  return
 end
end

local function sample(keys, time)
 if time <= keys[1].time then return keys[1].cf, keys[1].weight end
 local lo, hi = 1, #keys
 while lo < hi do
  local mid = math.floor((lo + hi) / 2)
  if keys[mid].time < time then lo = mid + 1 else hi = mid end
 end
 local b = keys[lo]
 local a = keys[math.max(1, lo - 1)]
 local alpha = math.clamp((time - a.time) / math.max(.0001, b.time - a.time), 0, 1)
 return a.cf:Lerp(b.cf, alpha), a.weight + (b.weight - a.weight) * alpha
end

local characters = {}
local playerConnections = {}
local function detach(character)
 local state = characters[character]
 if not state then return end
 for _, connection in ipairs(state.connections) do connection:Disconnect() end
 characters[character] = nil
end

local function attach(character)
 if characters[character] then return end
 local state = {joints = {}, connections = {}, time = 0, blend = 0, scanTime = 0}
 characters[character] = state
 task.spawn(function()
  local humanoid = character:WaitForChild("Humanoid", 15)
  local root = character:WaitForChild("HumanoidRootPart", 15)
  if characters[character] ~= state or not humanoid or not root then return end
  if humanoid.RigType ~= Enum.HumanoidRigType.R15 then
   character:SetAttribute("LocomotionAnimationStatus", "DefaultR6")
   return
  end
  state.humanoid, state.root = humanoid, root
  local function register(joint)
   if not joint:IsA("Motor6D") and not joint:IsA("AnimationConstraint") then return end
   local child
   if joint:IsA("Motor6D") then child = joint.Part1
   elseif joint.Attachment1 then child = joint.Attachment1.Parent end
   if child and clips.idle.channels[child.Name] then
    state.joints[joint] = {name = child.Name, from = joint.Transform}
   end
  end
  for _, joint in ipairs(character:GetDescendants()) do register(joint) end
  table.insert(state.connections, character.DescendantAdded:Connect(function(joint)
   task.defer(function()
    if characters[character] == state then register(joint) end
   end)
  end))
  table.insert(state.connections, character.DescendantRemoving:Connect(function(joint)
   state.joints[joint] = nil
  end))
  character:SetAttribute("LocomotionAnimationStatus", "ReadyKeyframes")
  character:SetAttribute("LocomotionBundleId", 272148363726799)
 end)
end

local locomotionGroups = {
 idle = true, walk = true, run = true, jump = true, fall = true,
 climb = true, swim = true, swimidle = true, toolnone = true, mood = true, pose = true,
}
local function hasAction(character, humanoid)
 local animator = humanoid:FindFirstChildOfClass("Animator")
 if not animator then return false end
 local emotes = {}
 local animate = character:FindFirstChild("Animate")
 if animate then
  for _, group in ipairs(animate:GetChildren()) do
   if not locomotionGroups[group.Name] then
    for _, animation in ipairs(group:GetDescendants()) do
     if animation:IsA("Animation") then emotes[animation.AnimationId] = true end
    end
   end
  end
 end
 for _, track in ipairs(animator:GetPlayingAnimationTracks()) do
  if track.WeightCurrent > .05 and
   ((track.Priority == Enum.AnimationPriority.Action or track.Priority == Enum.AnimationPriority.Action2 or
    track.Priority == Enum.AnimationPriority.Action3 or track.Priority == Enum.AnimationPriority.Action4) or
   (track.Animation and emotes[track.Animation.AnimationId])) then
   return true
  end
 end
 return false
end

local function chooseClip(state)
 local humanoid, root = state.humanoid, state.root
 if humanoid.Health <= 0 or humanoid.Sit or humanoid.PlatformStand then return nil end
 local kind = humanoid:GetState()
 local velocity = root.AssemblyLinearVelocity
 local speed = Vector3.new(velocity.X, 0, velocity.Z).Magnitude
 if kind == Enum.HumanoidStateType.Jumping then return "jump", 1 end
 if kind == Enum.HumanoidStateType.Freefall then
  if state.name == "jump" and state.time < .3 then return "jump", 1 end
  return "fall", 1
 end
 if kind == Enum.HumanoidStateType.Climbing then
  return "climb", math.clamp(velocity.Y / 5, -3, 3)
 end
 if kind == Enum.HumanoidStateType.Swimming then
  if velocity.Magnitude > .6 then return "swim", math.clamp(velocity.Magnitude / 10, .2, 3) end
  return "swimidle", 1
 end
 if kind ~= Enum.HumanoidStateType.Running and
  kind ~= Enum.HumanoidStateType.RunningNoPhysics and
  kind ~= Enum.HumanoidStateType.Landed then return nil end
 if speed < .65 then return "idle", 1 end
 -- Hysteresis avoids alternating clips around the walking/running boundary.
 local threshold = state.name == "run" and 9 or 11
 if speed > threshold then return "run", math.clamp(speed / 16, .25, 3) end
 return "walk", math.clamp(speed / 8, .15, 3)
end

RunService.PreSimulation:Connect(function(dt)
 for character, state in pairs(characters) do
  if not state.humanoid or not state.root.Parent then continue end
  state.scanTime -= dt
  if state.scanTime <= 0 then
   state.action = hasAction(character, state.humanoid)
   state.scanTime = .1
  end
  local mining = character:GetAttribute("MiningSwingActive") == true
  local name, rate
  if not mining and not state.action then name, rate = chooseClip(state) end
  if name ~= state.name then
   local oldName = state.name
   local oldClip = oldName and clips[oldName]
   local phase = oldClip and state.time / oldClip.length or 0
   state.name, state.time, state.blend = name, 0, 0
   if (name == "walk" or name == "run") and (oldName == "walk" or oldName == "run") then
    state.time = phase * clips[name].length
   end
   for joint, entry in pairs(state.joints) do
    if joint.Parent then entry.from = joint.Transform end
   end
  end
  local label = name or (mining and "mining" or "default")
  if state.label ~= label then
   state.label = label
   character:SetAttribute("BigAxeAnimationState", label)
  end
  if not name then continue end
  local clip = clips[name]
  state.time += dt * rate
  -- Jump/fall settle into their last pose instead of restarting in mid-air.
  if name == "jump" or name == "fall" then
   state.time = math.min(state.time, clip.length)
  else
   state.time %= clip.length
  end
  state.blend = math.min(1, state.blend + dt / .16)
  local blend = state.blend * state.blend * (3 - 2 * state.blend)
  for joint, entry in pairs(state.joints) do
   local keys = clip.channels[entry.name]
   if joint.Parent and keys then
    local cf, weight = sample(keys, state.time)
    if weight > 0 then
     joint.Transform = entry.from:Lerp(cf, blend * math.clamp(weight, 0, 1))
    end
   end
  end
 end
end)

local function watch(player)
 local connections = {}
 playerConnections[player] = connections
 table.insert(connections, player.CharacterAdded:Connect(attach))
 table.insert(connections, player.CharacterRemoving:Connect(detach))
 if player.Character then attach(player.Character) end
end
Players.PlayerAdded:Connect(watch)
Players.PlayerRemoving:Connect(function(player)
 if player.Character then detach(player.Character) end
 for _, connection in ipairs(playerConnections[player] or {}) do connection:Disconnect() end
 playerConnections[player] = nil
end)
for _, player in ipairs(Players:GetPlayers()) do watch(player) end
