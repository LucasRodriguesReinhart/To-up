-- HatVisual: poe no personagem os hats que o jogador tem equipados,
-- do mesmo jeito que o Unboxing Simulator faz - Accessory de verdade na cabeca.
--
-- De onde vem o modelo, nessa ordem:
--   1) ServerStorage.Acessorios.<idDoHat>  (modelo colado na mao, sem depender de internet)
--   2) Config.HatAssets[idDoHat]           (ID de acessorio do catalogo do Roblox)
-- Se nao achar nenhum dos dois, o hat continua valendo bonus, so nao aparece.
local RS = game:GetService("ReplicatedStorage")
local SS = game:GetService("ServerStorage")
local InsertService = game:GetService("InsertService")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local HatVisual = {}
local cache = {}          -- [assetId] = Accessory modelo
local MARCA = "HatDoJogo"  -- atributo pra saber o que e nosso e pode remover

local function pastaAcessorios()
	return SS:FindFirstChild("Acessorios")
end

-- transforma um modelo antigo (so Handle + script) num Accessory de verdade
local function virarAcessorio(instancia)
	if instancia:IsA("Accessory") then return instancia end

	local handle = instancia:FindFirstChild("Handle", true)
	if not handle or not handle:IsA("BasePart") then return nil end

	local acc = Instance.new("Accessory")
	acc.Name = instancia.Name
	handle = handle:Clone()
	handle.Name = "Handle"
	handle.CanCollide = false
	handle.Massless = true
	handle.Parent = acc

	-- sem ponto de encaixe o Roblox nao sabe onde grudar: cria um em cima da cabeca
	if not handle:FindFirstChild("HatAttachment") then
		local at = Instance.new("Attachment")
		at.Name = "HatAttachment"
		at.Position = Vector3.new(0, -0.5, 0)
		at.Parent = handle
	end
	return acc
end

local function modeloDoHat(def)
	local pasta = pastaAcessorios()
	local local_ = pasta and pasta:FindFirstChild(def.id)
	if local_ then
		return virarAcessorio(local_)
	end

	local assetId = Config.HatAssets[def.id] or def.assetId
	if not assetId or assetId == 0 then return nil end
	if cache[assetId] then return cache[assetId] end

	local ok, resultado = pcall(function()
		return InsertService:LoadAsset(assetId)
	end)
	if not ok or not resultado then
		warn(("[HatVisual] nao consegui carregar o acessorio %s (id %s)"):format(def.id, tostring(assetId)))
		return nil
	end

	local acc = resultado:FindFirstChildWhichIsA("Accessory", true) or virarAcessorio(resultado)
	if acc then
		acc = acc:Clone()
		cache[assetId] = acc
	end
	resultado:Destroy()
	return acc
end

local function limpar(char)
	for _, c in ipairs(char:GetChildren()) do
		if c:IsA("Accessory") and c:GetAttribute(MARCA) then c:Destroy() end
	end
end

-- poe no personagem exatamente os hats equipados no perfil
local versao = setmetatable({}, { __mode = "k" }) -- [player] = numero da ultima chamada

function HatVisual.aplicar(player)
	local char = player.Character
	local humanoid = char and char:FindFirstChildOfClass("Humanoid")
	if not humanoid then return end

	local perfil = PlayerData.get(player)
	if not perfil then return end

	-- carregar o acessorio espera a rede: se outra chamada comecou nesse meio tempo, esta desiste
	-- (antes as chamadas se sobrepunham e o personagem ficava com acessorios duplicados)
	versao[player] = (versao[player] or 0) + 1
	local minha = versao[player]
	local modelos = {}
	for _, uid in ipairs(perfil.equipados) do
		local inst = perfil.hatsInv[uid]
		local def = inst and Config.hatPorId(inst.id)
		local modelo = def and modeloDoHat(def)
		if modelo then table.insert(modelos, { modelo, def }) end
	end
	if versao[player] ~= minha or player.Character ~= char then return end

	limpar(char)
	for _, par in ipairs(modelos) do
		local acc = par[1]:Clone()
		acc:SetAttribute(MARCA, true)
		acc.Name = par[2].nome
		local ok = pcall(function() humanoid:AddAccessory(acc) end)
		if not ok then acc:Destroy() end
	end
end

-- reaplica quando o jogador renasce
function HatVisual.acompanhar(player)
	player.CharacterAppearanceLoaded:Connect(function()
		task.wait(0.2)
		HatVisual.aplicar(player)
	end)
	if player.Character then
		task.defer(HatVisual.aplicar, player)
	end
end

return HatVisual

