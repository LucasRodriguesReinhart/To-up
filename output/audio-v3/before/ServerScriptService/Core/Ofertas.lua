-- Ofertas (GDD v3.1 secoes 4, 5 e monetizacao contextual)
-- Regras eticas: nunca antes do minuto 5, no maximo 1 oferta paga a cada 10 min por sessao,
-- a opcao gratis sempre aparece junto, fechar e tao facil quanto comprar, nada de contador falso.
-- A compra e sempre iniciada pelo SERVIDOR com o ID do catalogo (o cliente so manda a chave).
local Players = game:GetService("Players")
local Market = game:GetService("MarketplaceService")
local RS = game:GetService("ReplicatedStorage")
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local PlayerData = require(script.Parent.PlayerData)
local Passes = require(script.Parent.Passes)
local Telemetria = require(script.Parent.Telemetria)

local O = {}
local sessao = {}   -- [player] = { ultimaPaga, mostradaEm, oferta, inventario, autosell }
local remotes = {}

local function estado(player)
	sessao[player] = sessao[player] or { ultimaPaga = -math.huge, autosell = -math.huge }
	return sessao[player]
end

local function podePaga(player)
	return os.clock() - estado(player).ultimaPaga >= Mon.OFERTA_INTERVALO_MIN * 60
end

function O.mostrar(player, perfil, oferta, dados)
	local e = estado(player)
	e.ultimaPaga, e.mostradaEm, e.oferta = os.clock(), os.clock(), oferta
	remotes.mostrar:FireClient(player, oferta, dados or {})
	Telemetria.evento(player, perfil, "OfferShown", 1, { oferta = oferta, contexto = dados and dados.contexto or "" })
end

-- inventario de hats/pets cheio: fundir (gratis) + passe +50 Inventario, 1x por sessao
function O.inventarioCheio(player, perfil, tipo)
	local e = estado(player)
	if e.inventario or Passes.possui(player, "Inventario") or not podePaga(player) then return end
	e.inventario = true
	O.mostrar(player, perfil, "Inventario", { contexto = "inventario_cheio_" .. tostring(tipo) })
end

-- mochila cheia fora do lobby: teleporte gratis pro Ignis + Auto Sell, no maximo a cada 30 min
function O.mochilaCheia(player, perfil)
	local e = estado(player)
	if Passes.noLobby(player) or Passes.possui(player, "AutoSell") then return end
	if os.clock() - e.autosell < 30 * 60 or not podePaga(player) then return end
	e.autosell = os.clock()
	O.mostrar(player, perfil, "AutoSell", { contexto = "mochila_cheia" })
end

local function acaoCliente(player, acao, oferta)
	local perfil = PlayerData.get(player)
	if type(acao) ~= "string" or type(oferta) ~= "string" or not perfil then return end
	if acao == "fechada" then
		Telemetria.evento(player, perfil, "OfferClosed", 1, { oferta = oferta })
		local e = estado(player)
		if e.oferta == oferta then e.oferta = nil end
	end
end

-- compra iniciada pelo cliente com a CHAVE do catalogo
local function comprar(player, chave)
	if type(chave) ~= "string" then return { ok = false } end
	local perfil = PlayerData.get(player)
	local passe, produto = Mon.passe(chave), Mon.produto(chave)
	if passe then
		if passe.id <= 0 then return { ok = false, msg = passe.nome .. " ainda nao esta a venda" } end
		if Passes.possui(player, chave) then return { ok = false, msg = "Voce ja tem " .. passe.nome } end
		Market:PromptGamePassPurchase(player, passe.id)
	elseif produto then
		if produto.id <= 0 then return { ok = false, msg = produto.nome .. " ainda nao esta a venda" } end
		if produto.starter and perfil and (perfil.compras.Starter or 0) > 0 then
			return { ok = false, msg = "Voce ja comprou o Starter Pack" }
		end
		Market:PromptProductPurchase(player, produto.id)
	else
		return { ok = false, msg = "Produto inexistente" }
	end
	if perfil then Telemetria.evento(player, perfil, "ShopPrompt", 1, { item = chave }) end
	return { ok = true }
end

function O.comprouAlgo(player, perfil, chave)
	local e = estado(player)
	Telemetria.evento(player, perfil, "OfferBought", 1, { item = chave, deOferta = e.oferta == chave and 1 or 0 })
	if e.oferta == chave then e.oferta = nil end
end

function O.iniciar()
	local pasta = RS:WaitForChild("Remotes")
	local function criar(nome, classe)
		local r = pasta:FindFirstChild(nome) or Instance.new(classe)
		r.Name = nome
		r.Parent = pasta
		return r
	end
	remotes.mostrar = criar("OfertaMostrar", "RemoteEvent")
	remotes.acao = criar("OfertaAcao", "RemoteEvent")
	remotes.comprar = criar("ComprarRobux", "RemoteFunction")
	remotes.acao.OnServerEvent:Connect(acaoCliente)
	remotes.comprar.OnServerInvoke = comprar

	Players.PlayerRemoving:Connect(function(player)
		local e = sessao[player]
		local perfil = PlayerData.get(player)
		if e and e.mostradaEm and os.clock() - e.mostradaEm < 60 and perfil then
			Telemetria.evento(player, perfil, "OfferLeave60s", 1, { oferta = e.oferta or "?" })
		end
		sessao[player] = nil
	end)

	-- Starter Pack: uma vez por conta, a partir do minuto 5 da primeira sessao, ate 72 h depois de criar a conta
	task.spawn(function()
		while true do
			task.wait(20)
			for _, player in ipairs(Players:GetPlayers()) do
				local perfil = PlayerData.get(player)
				local starter = Mon.produto("Starter")
				if perfil and starter and not perfil.tel.StarterMostrado and (perfil.compras.Starter or 0) == 0
					and os.time() - (perfil.criadoEm or 0) < Mon.STARTER_JANELA_H * 3600
					and Telemetria.minutosJogados(perfil) >= Mon.STARTER_APOS_MIN and podePaga(player) then
					perfil.tel.StarterMostrado = os.time()
					O.mostrar(player, perfil, "Starter", { contexto = "onboarding_min5" })
				end
			end
		end
	end)
end

return O

