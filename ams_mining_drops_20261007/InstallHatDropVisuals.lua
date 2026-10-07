-- Execute em Edit pelo Command Bar ou MCP. Por padrao instala os 80 hats.
-- Para dividir em lotes, defina _G.AMS_HAT_DROP_FROM e _G.AMS_HAT_DROP_TO antes.
local fromIndex = tonumber(_G.AMS_HAT_DROP_FROM) or 1
local toIndex = tonumber(_G.AMS_HAT_DROP_TO) or math.huge

local RS = game:GetService("ReplicatedStorage")
local InsertService = game:GetService("InsertService")
local Config = require(RS.Config)
local folder = RS:FindFirstChild("MiningDropHats")
if not folder then
 folder = Instance.new("Folder")
 folder.Name = "MiningDropHats"
 folder.Parent = RS
end

local ids = {}
for id in pairs(Config.HatAssets) do table.insert(ids, id) end
table.sort(ids)
local added, failed = 0, {}
for i = fromIndex, math.min(toIndex, #ids) do
 local id = ids[i]
 if not folder:FindFirstChild(id) then
  local assetId = Config.HatAssets[id]
  local ok, asset = pcall(function() return InsertService:LoadAsset(assetId) end)
  local acc = ok and asset and asset:FindFirstChildWhichIsA("Accessory", true)
  local handle = acc and acc:FindFirstChild("Handle")
  if handle and handle:IsA("BasePart") then
   local mini = handle:Clone()
   mini.Name = id
   mini.Anchored = true
   mini.CanCollide = false
   mini.CanTouch = false
   mini.CanQuery = false
   mini.CastShadow = false
   for _, child in ipairs(mini:GetDescendants()) do
    if child:IsA("LuaSourceContainer") or child:IsA("Weld") or child:IsA("WeldConstraint")
     or child:IsA("Motor6D") or child:IsA("Sound") then child:Destroy() end
   end
   mini.Parent = folder
   added += 1
  else
   table.insert(failed, id .. ":" .. tostring(ok and "sem Handle" or asset))
  end
  if ok and asset then asset:Destroy() end
 end
end
-- O asset Goku SSJ4 nao e aprovado para este lugar. Use a silhueta 3D
-- proxima do SSJ5, escurecida, ate o asset correto ser autorizado.
if fromIndex <= #ids and toIndex >= #ids and not folder:FindFirstChild("ki_86070099711035") then
 local base = folder:FindFirstChild("ki_122442369782268")
 if base then
  local fallback = base:Clone()
  fallback.Name = "ki_86070099711035"
  fallback.Color = Color3.fromRGB(45, 30, 48)
  if fallback:IsA("MeshPart") then fallback.TextureID = "" end
  for _, child in ipairs(fallback:GetDescendants()) do
   if child:IsA("SurfaceAppearance") then child:Destroy() end
  end
  fallback.Parent = folder
 end
end
return "total=" .. #ids .. " added=" .. added .. " cached=" .. #folder:GetChildren()
 .. " failed=" .. table.concat(failed, ",")
