-- Produtos: developer products (ProcessReceipt) idempotentes.
-- 1. jogador fora do servidor ou perfil sem salvar -> NotProcessedYet (a Roblox tenta de novo depois)
-- 2. recibo ja entregue (perfil.recibos[PurchaseId]) -> nao entrega de novo, so confirma quando o save funcionar
-- 3. entrega, grava o recibo no perfil e SALVA; so responde PurchaseGranted se o save deu certo
--    (se o servidor cair antes do save, nem o item nem o recibo ficam gravados -> a Roblox reentrega uma vez)
local Players = game:GetService("Players")
local Market = game:GetService("MarketplaceService")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local PlayerData = require(script.Parent.PlayerData)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)
local Ofertas = require(script.Parent.Ofertas)
local BossService = require(script.Parent.BossService)

local P = {}
local emProcesso = {} -- [PurchaseId] = true (duas chamadas simultaneas do mesmo recibo)

local function entregar(player, perfil, prod)
	local area = PlayerData.maiorArea(perfil)
	local partes = {}
	local conteudo = prod.conteudo or prod
	if conteudo.minutosRenda then
		local q = Recompensas.darMoedas(player, perfil, Config.moedasDeMinutos(area, conteudo.minutosRenda), "IAP", prod.chave)
		table.insert(partes, Config.formatar(q) .. " moedas")
	end
	if prod.boost then
		PlayerData.adicionarBoost(perfil, prod.boost, prod.minutos)
		table.insert(partes, prod.nome .. " (" .. prod.minutos .. " min)")
	end
	for _, b in ipairs(conteudo.boosts or {}) do
		PlayerData.adicionarBoost(perfil, b.boost, b.minutos)
		table.insert(partes, (b.boost == "sorte" and "Sorte " or "Moedas x2 ") .. b.minutos .. " min")
	end
	if conteudo.cosmetico then
		perfil.cosmeticos[conteudo.cosmetico] = true
		table.insert(partes, "skin exclusiva")
	end
	if prod.chave == "InvocarChefe" then
		BossService.invocar(player)
		table.insert(partes, "chefe invocado")
	end
	return table.concat(partes, " + ")
end

local function processar(info)
	local player = Players:GetPlayerByUserId(info.PlayerId)
	if not player then return Enum.ProductPurchaseDecision.NotProcessedYet end
	local perfil = PlayerData.get(player)
	if not perfil or perfil.__semSalvar then return Enum.ProductPurchaseDecision.NotProcessedYet end
	local id = tostring(info.PurchaseId)
	if emProcesso[id] then return Enum.ProductPurchaseDecision.NotProcessedYet end

	local function confirmar()
		if perfil.__dev and not perfil.__devSalvar then return true end -- perfil de teste do Studio nao vai pro DataStore
		return PlayerData.salvar(player)
	end

	if perfil.recibos[id] then
		return confirmar() and Enum.ProductPurchaseDecision.PurchaseGranted or Enum.ProductPurchaseDecision.NotProcessedYet
	end

	local prod = Mon.produtoPorId(info.ProductId)
	if not prod then
		warn("[Produtos] ProductId sem cadastro em MonetizacaoConfig: " .. tostring(info.ProductId))
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	emProcesso[id] = true
	local ok, texto = pcall(entregar, player, perfil, prod)
	if not ok then
		emProcesso[id] = nil
		warn("[Produtos] falha ao entregar " .. prod.chave .. ": " .. tostring(texto))
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	perfil.recibos[id] = os.time()
	perfil.compras[prod.chave] = (perfil.compras[prod.chave] or 0) + 1
	Ofertas.comprouAlgo(player, perfil, prod.chave)
	Telemetria.marco(player, perfil, "FirstPurchase", { item = prod.chave })
	Telemetria.evento(player, perfil, "ProductPurchased", info.CurrencySpent or prod.robux, { item = prod.chave })
	PlayerData.sincronizar(player)
	RS.Remotes.FeedbackMina:FireClient(player, { tipo = "area", texto = "Compra entregue: " .. texto })
	local salvo = confirmar()
	emProcesso[id] = nil
	return salvo and Enum.ProductPurchaseDecision.PurchaseGranted or Enum.ProductPurchaseDecision.NotProcessedYet
end

function P.iniciar()
	Market.ProcessReceipt = processar
	-- gamepass comprado dentro do jogo: telemetria + sincronizar (o Passes ja atualiza o cache)
	Market.PromptGamePassPurchaseFinished:Connect(function(player, passId, comprou)
		if not comprou then return end
		local perfil = PlayerData.get(player)
		if not perfil then return end
		for _, p in ipairs(Mon.PASSES) do
			if p.id > 0 and p.id == passId then
				Ofertas.comprouAlgo(player, perfil, p.chave)
				Telemetria.marco(player, perfil, "FirstPurchase", { item = p.chave })
			end
		end
		task.defer(PlayerData.sincronizar, player)
	end)
end

P._processar = processar -- exposto para testes automatizados no Studio

return P

