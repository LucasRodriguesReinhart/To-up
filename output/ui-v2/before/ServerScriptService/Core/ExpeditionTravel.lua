--!strict
-- Deploy as a Script under ServerScriptService.Core.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("Config"))
local PlayerData = require(script.Parent:WaitForChild("PlayerData"))
local IslandTravel = require(script.Parent:WaitForChild("IslandTravel"))
local remotes = ReplicatedStorage:WaitForChild("Remotes")

local COOLDOWN = 1.5
local MAX_AREA_ID = 6
local LOBBY = Vector3.new(0, 7, 66)
-- Edit-world raycasts and character-clearance queries verified these lobby points.
local SHOP = Vector3.new(39, 7, 36)
local IGNIS = Vector3.new(-30, 7, 36)

type Result = { ok: boolean, msg: string }
type RequestState = { busy: boolean, lastAttempt: number }
local states: { [Player]: RequestState } = {}

local function result(ok: boolean, msg: string): Result
    return { ok = ok, msg = msg }
end

local function finite(value: any): boolean
    return type(value) == "number"
        and value == value
        and value > -math.huge
        and value < math.huge
end

local function validId(id: any, minimum: number): boolean
    return finite(id) and id % 1 == 0 and id >= minimum and id <= MAX_AREA_ID
end

local function validPosition(position: any): boolean
    return typeof(position) == "Vector3"
        and finite(position.X) and finite(position.Y) and finite(position.Z)
end

local function destination(player: Player, action: string, id: any): (Vector3?, string?)
    local profile = PlayerData.get(player)
    if not profile then
        return nil, "Perfil nao carregado"
    end

    if action == "shop" then return SHOP, nil end
    if action == "ignis" then return IGNIS, nil end
    if action == "area" and id == 0 then return LOBBY, nil end

    local area = Config.areaPorId(id)
    if not area then return nil, "Area inexistente" end
    if not profile.areas or profile.areas[id] ~= true then
        return nil, "Desbloqueie " .. area.nome .. " primeiro"
    end

    if action == "gacha" then
        local gachas = workspace:FindFirstChild("Gachas")
        local machine = gachas and gachas:FindFirstChild("Gacha_" .. area.tema)
        local pad = machine and machine:FindFirstChild("PadGacha")
        if not pad or not pad:IsA("BasePart") then
            return nil, "Maquina de gacha indisponivel"
        end
        local position = pad.Position + Vector3.new(0, 4, 0)
        if not validPosition(position) then return nil, "Destino indisponivel" end
        return position, nil
    end

    local areas = workspace:FindFirstChild("Areas")
    local model = areas and areas:FindFirstChild("Area" .. id)
    local entry = model and model:GetAttribute("EntryPosition")
    if not validPosition(entry) then return nil, "Entrada da area indisponivel" end
    return entry, nil
end

local function travel(player: Player, action: any, id: any): Result
    if player.Parent ~= Players then return result(false, "Jogador indisponivel") end
    if type(action) ~= "string" then return result(false, "Acao invalida") end
    if action == "area" or action == "gacha" then
        if not validId(id, action == "area" and 0 or 1) then
            return result(false, "ID de area invalido")
        end
    elseif action == "shop" or action == "ignis" then
        if id ~= nil then return result(false, "Este destino nao recebe ID") end
    else
        return result(false, "Acao invalida")
    end

    local character = player.Character
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    local root = character and character:FindFirstChild("HumanoidRootPart")
    if not character or not character.Parent or not humanoid or humanoid.Health <= 0
        or not root or not root:IsA("BasePart") then
        return result(false, "Personagem indisponivel")
    end

    local now = os.clock()
    local state = states[player]
    if state then
        if state.busy then return result(false, "Viagem em andamento") end
        if now - state.lastAttempt < COOLDOWN then
            return result(false, "Aguarde para viajar novamente")
        end
    else
        state = { busy = false, lastAttempt = -math.huge }
        states[player] = state
    end

    -- Lock before the server travel call, which can yield while preparing streaming.
    state.busy = true
    state.lastAttempt = now
    local succeeded, response = pcall(function(): Result
        local position, message = destination(player, action, id)
        if not position then return result(false, message or "Destino indisponivel") end
        if not IslandTravel.teleport(player, position) then
            return result(false, "Nao foi possivel viajar agora")
        end
        return result(true, "Viagem concluida")
    end)
    -- Do not recreate a player's state if PlayerRemoving fired during the yield.
    state.busy = false
    if not succeeded then
        warn("[UITravel] Travel failed for " .. player.UserId .. ": " .. tostring(response))
        return result(false, "Falha ao viajar. Tente novamente")
    end
    return response
end

Players.PlayerRemoving:Connect(function(player)
    states[player] = nil
end)

local existing = remotes:FindFirstChild("UITravel")
local remote: RemoteFunction
if existing then
    assert(existing:IsA("RemoteFunction"), "ReplicatedStorage.Remotes.UITravel must be a RemoteFunction")
    remote = existing
else
    remote = Instance.new("RemoteFunction")
    remote.Name = "UITravel"
    remote.Parent = remotes
end
remote.OnServerInvoke = travel


