local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local root = workspace:WaitForChild("LobbyRenovado")
local entries = {}
local function register(v)
    if v:IsA("Texture") and v.Name=="PondRipples" then
        entries[v]={kind="water",carrier=v.Parent}
    elseif v:IsA("Attachment") and v:GetAttribute("V2Arc") then
        entries[v] = {kind="arc",carrier=v.Parent,style=v:GetAttribute("V2Arc"),u=v:GetAttribute("ArcU"),arm=v:GetAttribute("ArcArm"),seed=v:GetAttribute("ArcSeed")}
    elseif v:IsA("ImageLabel") and v:GetAttribute("V2Spin") then
        local gui = v:FindFirstAncestorWhichIsA("SurfaceGui")
        entries[v] = {kind="spin",speed=v:GetAttribute("V2Spin"),carrier=gui and gui.Parent,phase=v.Rotation}
    elseif v:IsA("ParticleEmitter") and v:GetAttribute("V2Ambient") then
        entries[v] = {kind="emitter",carrier=v.Parent}
    elseif v:IsA("Beam") and v:GetAttribute("V2Beam") then
        entries[v] = {kind="beam",carrier=v.Parent}
    end
end
for _, v in root:GetDescendants() do register(v) end
root.DescendantAdded:Connect(register)
root.DescendantRemoving:Connect(function(v) entries[v] = nil end)
local elapsed,acc = 0,0
local connection
connection = RunService.Heartbeat:Connect(function(dt)
    if not root.Parent then connection:Disconnect();return end
    elapsed += dt;acc += dt
    if acc < 1/30 then return end
    acc = 0
    local camera = workspace.CurrentCamera
    if not camera then return end
    local enabled = Players.LocalPlayer:GetAttribute("LobbyVFXEnabled") ~= false
    for v, data in entries do
        local carrier = data.carrier
        if not v.Parent or not carrier or not carrier.Parent then entries[v] = nil;continue end
        local near = (camera.CFrame.Position-carrier.Position).Magnitude < 160
        if data.kind == "emitter" then v.Enabled = enabled and near
        elseif data.kind == "beam" then v.Enabled = enabled and near
        elseif data.kind == "water" and enabled and near then
            v.OffsetStudsU=elapsed*.18;v.OffsetStudsV=elapsed*.09
        elseif data.kind == "arc" and enabled and near then
            local w,h = carrier.Size.X,carrier.Size.Y
            if data.style == "spiral" then
                local a = data.arm*math.pi+data.u*math.pi*3-elapsed*.85
                local radius = .05+data.u*.4
                v.Position = Vector3.new(math.cos(a)*w*radius,math.sin(a)*h*radius,.35)
            else
                local a = data.arm*math.pi/4
                local radius = data.style=="lightning" and data.u*.47 or .42
                local jitter = (data.u==0 or data.u==1) and 0 or math.noise(data.seed,math.floor(elapsed*12))*.65
                v.Position = Vector3.new(math.cos(a)*w*radius+jitter,math.sin(a)*h*radius+jitter,.4)
            end
        elseif data.kind == "spin" and enabled and near then
            v.Rotation = (data.phase+elapsed*data.speed)%360
            v.ImageTransparency = .14+.08*math.sin(elapsed*1.7+data.phase)
        end
    end
end)


