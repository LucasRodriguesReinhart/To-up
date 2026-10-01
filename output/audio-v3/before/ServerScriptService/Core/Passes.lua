-- Gamepasses: IDs em ReplicatedStorage.MonetizacaoConfig (id = 0 -> ainda nao criado: ninguem tem).
local Players = game:GetService("Players")
local Market = game:GetService("MarketplaceService")
local RS = game:GetService("ReplicatedStorage")
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))

local Passes = {}
local cache = {} -- [player] = { [chave] = bool }

function Passes.id(nome)
	local p = Mon.passe(nome)
	return p and p.id or 0
end

function Passes.possui(player, nome)
	local id = Passes.id(nome)
	if id <= 0 then return false end
	cache[player] = cache[player] or {}
	if cache[player][nome] == nil then
		local ok, tem = pcall(Market.UserOwnsGamePassAsync, Market, player.UserId, id)
		if not ok then return false end -- tenta de novo na proxima chamada
		cache[player][nome] = tem
	end
	return cache[player][nome]
end

function Passes.todos(player)
	local t = {}
	for _, p in ipairs(Mon.PASSES) do t[p.chave] = Passes.possui(player, p.chave) end
	return t
end

-- compra na hora: marca e avisa quem quiser sincronizar
Passes.aoComprar = Instance.new("BindableEvent")
Market.PromptGamePassPurchaseFinished:Connect(function(player, passId, comprou)
	if not comprou then return end
	for _, p in ipairs(Mon.PASSES) do
		if p.id > 0 and p.id == passId then
			cache[player] = cache[player] or {}
			cache[player][p.chave] = true
			Passes.aoComprar:Fire(player, p.chave)
		end
	end
end)

Players.PlayerRemoving:Connect(function(p) cache[p] = nil end)

-- esta no lobby? (IslandTravel marca CurrentAreaId = 0 no lobby)
function Passes.noLobby(player)
	return (player:GetAttribute("CurrentAreaId") or 0) == 0
end

-- compra de equipamento: no lobby (Ignis) -- o teleporte ate o Ignis e gratis
function Passes.acesso(player, nome)
	return Passes.noLobby(player) or (nome ~= nil and Passes.possui(player, nome))
end

return Passes

