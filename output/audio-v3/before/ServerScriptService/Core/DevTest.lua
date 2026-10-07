-- DevTest: perfil de teste com tudo liberado e dinheiro que nao acaba.
-- Serve pra testar o jogo sem grindar. NAO afeta jogador normal.
--
-- AJUSTES RAPIDOS:
local LIGADO            = true    -- false desliga tudo de uma vez
local SOMENTE_STUDIO    = true    -- true = so funciona no Studio, nunca no jogo publicado
local SALVAR_PROGRESSO  = false   -- false = o perfil de teste nao vai pro DataStore
local DEV_IDS = {                 -- quem pode usar (UserId)
	[638377833] = true,
}
local MOEDA_ALVO = 1e15           -- recarrega sempre que cair abaixo disso

local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local IgnisService = require(script.Parent.IgnisService)
local PetService = require(script.Parent.PetService)
local HatVisual = require(script.Parent.HatVisual)

if not LIGADO then return end
-- atributo "Desligado" = true no proprio script desliga sem editar codigo (usado nos testes da economia)
if script:GetAttribute("Desligado") then return end
if SOMENTE_STUDIO and not RunService:IsStudio() then return end

local function ehDev(player)
	return DEV_IDS[player.UserId] == true
end

local function darTudo(player)
	local perfil = PlayerData.get(player)
	if not perfil then return end

	perfil.__dev = true
	perfil.__devSalvar = SALVAR_PROGRESSO

	-- dinheiro
	perfil.moeda = MOEDA_ALVO

	-- melhor picareta e melhor mochila
	perfil.picareta = Config.Picaretas[#Config.Picaretas].id
	perfil.mochilaTier = Config.Mochilas[#Config.Mochilas].id
	for _, p in ipairs(Config.Picaretas) do perfil.picaretasCompradas[p.id] = true end

	-- todas as areas desbloqueadas
	for _, area in ipairs(Config.Areas) do
		perfil.areas[area.id] = true
	end

	-- todos os hats, no nivel maximo e com duplicata sobrando pra testar fusao
	-- hats sao itens separados: 1 de cada no maximo + 1 de nivel 1 pra testar fusao
	perfil.hatsInv, perfil.equipados = {}, {}
	for _, h in ipairs(Config.Hats) do
		PlayerData.novoHat(perfil, h.id, Config.HAT_NIVEL_MAX)
		PlayerData.novoHat(perfil, h.id, 1)
	end

	-- todos os pets, mesma coisa
	-- pets sao itens separados: 1 de cada no maximo + 1 de nivel 1 pra testar alimentar
	perfil.pets, perfil.petsInv, perfil.petsEquipados = {}, {}, {}
	for _, p in ipairs(Config.Pets) do
		PlayerData.novoPet(perfil, p.id, Config.PET_NIVEL_MAX)
		PlayerData.novoPet(perfil, p.id, 1)
	end

	-- equipa os melhores que couberem nos slots
	IgnisService.equiparMelhores(player)
	PetService.equiparMelhores(player)

	PlayerData.sincronizar(player)
	HatVisual.aplicar(player)

	print(("[DevTest] %s liberado: %d hats, %d pets, todas as areas")
		:format(player.Name, #Config.Hats, #Config.Pets))
end

local function limparTudo(player)
	local perfil = PlayerData.get(player)
	if not perfil then return end
	perfil.__dev = nil
	perfil.moeda = 0
	perfil.picareta = Config.Picaretas[1].id
	perfil.mochilaTier = Config.Mochilas[1].id
	perfil.hats, perfil.hatsInv, perfil.equipados = {}, {}, {}
	perfil.pets, perfil.petsInv, perfil.petsEquipados = {}, {}, {}
	perfil.picaretasCompradas = { [Config.Picaretas[1].id] = true }
	perfil.apelidos, perfil.missoes = {}, {}
	perfil.mochila = {}
	perfil.areas = { [1] = true }
	PlayerData.sincronizar(player)
	HatVisual.aplicar(player)
	print("[DevTest] " .. player.Name .. " zerado")
end

local ligados = {}
local pausado = {}   -- quem deu /devoff fica de fora ate mandar /dev de novo

local function ligarComandos(player)
	player.Chatted:Connect(function(msg)
		local cmd = string.lower(string.gsub(msg, "%s+", ""))
		if cmd == "/dev" then
			pausado[player] = nil
			darTudo(player)
		elseif cmd == "/devoff" then
			pausado[player] = true
			limparTudo(player)
		end
	end)
end



local function cuidar(player)
	if not ehDev(player) or ligados[player] then return end
	ligados[player] = true
	ligarComandos(player)
end

Players.PlayerAdded:Connect(cuidar)
Players.PlayerRemoving:Connect(function(player) ligados[player] = nil end)
for _, player in ipairs(Players:GetPlayers()) do cuidar(player) end

-- varredura: libera assim que o perfil carrega e mantem a moeda cheia
-- depois de gastar comprando ou rolando gacha
task.spawn(function()
	while true do
		for _, player in ipairs(Players:GetPlayers()) do
			if ehDev(player) and not pausado[player] then
				cuidar(player)
				local perfil = PlayerData.get(player)
				if perfil and not perfil.__dev then
					darTudo(player)
				elseif perfil and perfil.moeda < MOEDA_ALVO then
					perfil.moeda = MOEDA_ALVO
					PlayerData.sincronizar(player)
				end
			end
		end
		task.wait(1)
	end
end)

