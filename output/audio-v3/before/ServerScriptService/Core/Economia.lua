-- Economia: multiplicadores que dependem do jogador (passes, boosts, amigos) e quem esta ativo.
-- Numeros de balanceamento vem de Config/EconomiaV31; precos/multiplicadores de monetizacao de MonetizacaoConfig.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local PlayerData = require(script.Parent.PlayerData)
local Passes = require(script.Parent.Passes)

local E = {}
local ultimoGolpe = {}   -- [player] = os.clock()
local amizade = {}       -- [userIdA .. ":" .. userIdB] = bool

-- ---------- ATIVIDADE ----------
function E.registrarGolpe(player)
	ultimoGolpe[player] = os.clock()
end

function E.ativo(player)
	return ultimoGolpe[player] ~= nil and os.clock() - ultimoGolpe[player] < Config.CHEFE.ativoJanela
end

function E.ativosNaArea(areaId)
	local n = 0
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == areaId and E.ativo(p) then n += 1 end
	end
	return n
end

function E.jogadoresNaArea(areaId)
	local n = 0
	for _, p in ipairs(Players:GetPlayers()) do
		if p:GetAttribute("CurrentAreaId") == areaId then n += 1 end
	end
	return n
end

-- ---------- FRIEND BOOST ----------
local function chaveAmizade(a, b)
	return a < b and (a .. ":" .. b) or (b .. ":" .. a)
end

local function verificarAmizades(novo)
	for _, outro in ipairs(Players:GetPlayers()) do
		if outro ~= novo then
			local k = chaveAmizade(novo.UserId, outro.UserId)
			if amizade[k] == nil then
				local ok, sao = pcall(novo.IsFriendsWith, novo, outro.UserId)
				if ok then amizade[k] = sao end
			end
		end
	end
end

-- +10% por amigo do Roblox no servidor que tambem esteja ativo (max +30%). so conta se EU estiver ativo.
function E.friendBoost(player)
	if not E.ativo(player) then return 0 end
	local n = 0
	for _, outro in ipairs(Players:GetPlayers()) do
		if outro ~= player and amizade[chaveAmizade(player.UserId, outro.UserId)] and E.ativo(outro) then n += 1 end
	end
	return math.min(Mon.FRIEND_BOOST_MAX, n * Mon.FRIEND_BOOST_POR_AMIGO)
end

-- ---------- MULTIPLICADORES ----------
-- moedas de venda e de chefe: VIP x boost de moedas x Friend Boost
function E.multMoedas(player, perfil)
	local m = 1
	if Passes.possui(player, "VIP") then m *= Mon.VIP_MOEDAS end
	if PlayerData.boostAtivo(perfil, "moedas") then m *= Mon.BOOST_MOEDAS_MULT end
	return m * (1 + E.friendBoost(player))
end

-- sorte (hats e gacha): Lucky x boost de sorte, aplicado com Config.aplicarLucky (Epico+ exato)
function E.luckyMult(player, perfil)
	local m = 1
	if Passes.possui(player, "Lucky") then m *= Mon.LUCKY_MULT end
	if PlayerData.boostAtivo(perfil, "sorte") then m *= Mon.BOOST_SORTE_MULT end
	return m
end

PlayerData.antesDeSincronizar = function(player, perfil)
	perfil.__multMoedas = E.multMoedas(player, perfil)
	perfil.__friendBoost = E.friendBoost(player)
	perfil.__luckyMult = E.luckyMult(player, perfil)
	player:SetAttribute("FriendBoost", perfil.__friendBoost)
end

Players.PlayerAdded:Connect(function(p) task.spawn(verificarAmizades, p) end)
for _, p in ipairs(Players:GetPlayers()) do task.spawn(verificarAmizades, p) end
Players.PlayerRemoving:Connect(function(p) ultimoGolpe[p] = nil end)

return E

