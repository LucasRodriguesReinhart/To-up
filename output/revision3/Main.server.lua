local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local Config       = require(RS.Config)
local PlayerData   = require(script.Parent.PlayerData)
local AreaBuilder  = require(script.Parent.AreaBuilder)
local Mineracao    = require(script.Parent.Mineracao)
local IgnisService = require(script.Parent.IgnisService)
local GachaService  = require(script.Parent.GachaService)
local PetService    = require(script.Parent.PetService)
local HatVisual     = require(script.Parent.HatVisual)

local R = RS.Remotes

-- ---------- MUNDO ----------
AreaBuilder.construir()
Mineracao.iniciar()

-- ponto de entrada da area 1, pra teleportar do lobby
local a1 = Config.Areas[1]
local ENTRADA = a1.centro + Vector3.new(0, 5, -a1.tamanho.Z / 2 + 14)
local LOBBY = Vector3.new(0, 7, 66)

-- ---------- JOGADORES ----------
local function aoEntrar(player)
	PlayerData.carregar(player)

	player.CharacterAdded:Connect(function(char)
		local hum = char:WaitForChild("Humanoid")
		task.wait(0.2)
		local perfil = PlayerData.get(player)
		if perfil then
			PlayerData.sincronizar(player)
			HatVisual.aplicar(player)
		end
	end)

	task.wait(0.5)
	PlayerData.sincronizar(player)
end

Players.PlayerAdded:Connect(aoEntrar)
for _, p in ipairs(Players:GetPlayers()) do task.spawn(aoEntrar, p) end

Players.PlayerRemoving:Connect(function(player)
	PlayerData.descarregar(player)
	GachaService.limpar(player)
end)

game:BindToClose(function()
	for _, p in ipairs(Players:GetPlayers()) do
		PlayerData.salvar(p)
	end
	task.wait(1)
end)

-- autosave
task.spawn(function()
	while true do
		task.wait(120)
		for _, p in ipairs(Players:GetPlayers()) do
			PlayerData.salvar(p)
		end
	end
end)

-- ---------- REMOTES ----------
R.PedirDados.OnServerInvoke = function(player)
	local perfil = PlayerData.get(player)
	if not perfil then return nil end
	return PlayerData.snapshot(perfil)
end

R.EquiparPet.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return PetService.equipar(player, id)
end

R.FundirPet.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return PetService.fundir(player, id)
end

R.EquiparMelhoresPets.OnServerInvoke = function(player)
	return PetService.equiparMelhores(player)
end

R.DesequiparPets.OnServerInvoke = function(player)
	return PetService.desequiparTodos(player)
end

-- o golpe vem do cliente agora, porque a Tool equipada engole o ClickDetector.
-- toda validacao continua no servidor: tipo, distancia, area e cooldown.
R.Golpear.OnServerEvent:Connect(function(player, rocha)
	if typeof(rocha) ~= "Instance" or not rocha:IsA("BasePart") then return end
	if rocha.Name ~= "Hitbox" then return end
	if not rocha:GetAttribute("HPMax") then return end
	if not rocha:IsDescendantOf(workspace) then return end
	Mineracao.golpear(player, rocha)
end)

R.RolarGacha.OnServerInvoke = function(player, areaId)
	return GachaService.rolar(player, areaId)
end

R.Vender.OnServerInvoke = function(player)
	return IgnisService.vender(player)
end

R.ComprarPicareta.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return IgnisService.comprarPicareta(player, id)
end

R.ComprarMochila.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return IgnisService.comprarMochila(player, id)
end

R.EquiparHat.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	local res = IgnisService.equipar(player, id)
	HatVisual.aplicar(player)
	return res
end

R.FundirHat.OnServerInvoke = function(player, id)
	if type(id) ~= "string" then return { ok = false } end
	return IgnisService.fundir(player, id)
end

R.EquiparMelhores.OnServerInvoke = function(player)
	local res = IgnisService.equiparMelhores(player)
	HatVisual.aplicar(player)
	return res
end

R.DesequiparTodos.OnServerInvoke = function(player)
	local res = IgnisService.desequiparTodos(player)
	HatVisual.aplicar(player)
	return res
end

-- ---------- TELEPORTE LOBBY <-> AREA ----------
local emCooldown = {}
local function teleportar(player, destino)
	if emCooldown[player] then return end
	emCooldown[player] = true
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	if hrp then
  local look = destino + Vector3.new(0,0,destino.Z > 130 and 30 or -30)
  hrp.CFrame = CFrame.lookAt(destino,look)
 end
	task.delay(1.5, function() emCooldown[player] = nil end)
end

local function entradaDaArea(area)
 local model=workspace.Areas:FindFirstChild("Area"..area.id)
 return model and model:GetAttribute("EntryPosition") or area.centro+Vector3.new(0,6,-area.tamanho.Z/2+16)
end

-- Progression portals use the same server-owned unlocks as the lobby.
for _,pad in ipairs(workspace.Areas:GetDescendants()) do
 local id=pad:IsA("BasePart") and pad:GetAttribute("NextAreaId")
 local area=id and Config.areaPorId(id)
 if area then
  local pr=Instance.new("ProximityPrompt")
  pr.Name="ViajarArea" pr.ActionText="Viajar" pr.ObjectText=area.nome
  pr.MaxActivationDistance=12 pr.RequiresLineOfSight=false pr.Parent=pad
  pr.Triggered:Connect(function(player)
   local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
   if not root or (root.Position-pad.Position).Magnitude>16 then return end
   local perfil=PlayerData.get(player)
   if not perfil or not perfil.areas[id] then
    R.FeedbackMina:FireClient(player,{tipo="bloqueada",texto="Quebre o chefe da area anterior primeiro"})
    return
   end
   teleportar(player,entradaDaArea(area))
  end)
 end
end

-- placas de volta pro lobby dentro das areas
for _, d in ipairs(workspace.Areas:GetDescendants()) do
	if d:IsA("BasePart") and d:GetAttribute("Destino") == "lobby" then
		d.Touched:Connect(function(hit)
			local p = Players:GetPlayerFromCharacter(hit.Parent)
			if p then teleportar(p, LOBBY) end
		end)
	end
end

-- prompt do Ignis abre a UI
local ignis = workspace.NPCs:WaitForChild("Ignis")
local corpo
for _, d in ipairs(ignis:GetDescendants()) do
	if d:IsA("BasePart") and d.Name == "belly" then corpo = d end
end
if corpo then
	local antigo = corpo:FindFirstChildOfClass("ProximityPrompt")
	if antigo then antigo:Destroy() end
	local pr = Instance.new("ProximityPrompt")
	pr.Name = "IgnisPrompt"
	pr.ActionText = "Falar"
	pr.ObjectText = "Ignis"
	pr.HoldDuration = 0
	pr.MaxActivationDistance = 18
	pr.RequiresLineOfSight = false
	pr.Parent = corpo
	pr.Triggered:Connect(function(player)
		R.AbrirIgnis:FireClient(player)
	end)
end

-- pad da loja de mochilas
local loja = workspace:FindFirstChild("LojaMochilas")
	or workspace:FindFirstChild("backpack shop")
if loja then
	local pad = loja:FindFirstChild("PadLoja")
	if pad then
		local ultimo = {}
		pad.Touched:Connect(function(hit)
			local pl = Players:GetPlayerFromCharacter(hit.Parent)
			if not pl then return end
			if ultimo[pl] and os.clock() - ultimo[pl] < 1.5 then return end
			ultimo[pl] = os.clock()
			R.AbrirLoja:FireClient(pl)
		end)
		-- pulsa devagar pra chamar atencao
		task.spawn(function()
			local t = 0
			while pad.Parent do
				t += task.wait()
				pad.Transparency = 0.25 + 0.2 * math.sin(t * 2)
			end
		end)
	end
end

-- arcada do lobby: uma baia por area
-- liga os portais do lobby (montados no Edit, com atributo AreaId)
-- o Santuario pode estar solto no Workspace ou dentro de um modelo de lobby.
-- procura pelo nome em vez de assumir o caminho, assim desagrupar nao quebra nada.
local function acharSantuario()
	local direto = workspace:FindFirstChild("Santuario")
	if direto then return direto end
	for _, c in ipairs(workspace:GetChildren()) do
		local dentro = c:FindFirstChild("Santuario")
		if dentro then return dentro end
	end
	return nil
end
local sant = acharSantuario()
LOBBY = Vector3.new(0, 7, 66)

local ligados = 0
if not sant then warn("[Main] Santuario nao encontrado, viagem rapida desligada") end
for _, g in ipairs(sant and sant:GetDescendants() or {}) do
	local disco = g:IsA("Model") and g:FindFirstChild("Disco")
	if disco and disco:GetAttribute("AreaId") then
		local id = disco:GetAttribute("AreaId")
		local area = Config.areaPorId(id)
		if area then
			local destino = entradaDaArea(area)
			disco.CanTouch = true
			disco.Touched:Connect(function(hit)
				local pl = Players:GetPlayerFromCharacter(hit.Parent)
				if not pl then return end
				local perfil = PlayerData.get(pl)
				if not perfil or not perfil.areas[id] then
					R.FeedbackMina:FireClient(pl, { tipo = "bloqueada",
						texto = "Quebre o chefe da area anterior primeiro" })
					return
				end
				teleportar(pl, destino)
			end)
			ligados += 1
		end
	end
end

-- maquinas de gacha: abrem por ProximityPrompt, igual o Ignis
local gachas = workspace:FindFirstChild("Gachas")
if gachas then
	for _, maq in ipairs(gachas:GetChildren()) do
		local pad = maq:FindFirstChild("PadGacha")
		local areaId = pad and pad:GetAttribute("AreaId")
		if pad and areaId then
			pad.CanTouch = false

			-- prompt fica no corpo da maquina, nao no pad do chao
			local corpoMaq
			for _, d in ipairs(maq:GetDescendants()) do
				if d:IsA("BasePart") and string.find(d.Name:lower(), "cabinet_body") then
					corpoMaq = d
					break
				end
			end
			corpoMaq = corpoMaq or pad

			local antigoPr = corpoMaq:FindFirstChildOfClass("ProximityPrompt")
			if antigoPr then antigoPr:Destroy() end

			local pr = Instance.new("ProximityPrompt")
			pr.Name = "GachaPrompt"
			pr.ActionText = "Invocar"
			pr.ObjectText = "Gacha"
			pr.HoldDuration = 0
			pr.MaxActivationDistance = 14
			pr.RequiresLineOfSight = false
			pr.Parent = corpoMaq
			pr.Triggered:Connect(function(pl)
				R.AbrirGacha:FireClient(pl, areaId)
			end)
			task.spawn(function()
				local t = 0
				while pad.Parent do
					t += task.wait()
					pad.Transparency = 0.3 + 0.2 * math.sin(t * 2.2)
				end
			end)
		end
	end
end

print("[Mineracao] servidor pronto - " .. #Config.Areas .. " areas construidas")

