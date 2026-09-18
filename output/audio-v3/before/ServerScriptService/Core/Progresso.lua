-- Progresso: compra de areas com moedas e resgate de missoes.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Telemetria = require(script.Parent.Telemetria)
local Passes = require(script.Parent.Passes)
local RSMon = require(RS:WaitForChild("MonetizacaoConfig"))

local Progresso = {}

function Progresso.comprarArea(player, areaId)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local area = type(areaId) == "number" and Config.areaPorId(areaId)
	if not area then return { ok = false, msg = "Area inexistente" } end
	if perfil.areas[area.id] then return { ok = false, msg = "Voce ja tem essa area" } end
	local anterior = Config.areaPorId(area.id - 1)
	if anterior and not perfil.areas[anterior.id] then
		return { ok = false, msg = "Compre " .. anterior.nome .. " antes" }
	end
	if perfil.moeda < area.custo then
		return { ok = false, msg = "Faltam " .. Config.formatar(area.custo - perfil.moeda) .. " moedas" }
	end
	perfil.moeda -= area.custo
	perfil.areas[area.id] = true
	Telemetria.economia(player, perfil, false, area.custo, "Shop", "portal_" .. area.id)
	Telemetria.marco(player, perfil, "FirstPortal", { mundo = area.id })
	-- PortalReached: P25/P50/P75 por mundo, separando quem ja pagou (passe ou produto)
	local pagante = next(perfil.compras) ~= nil
	for _, p in ipairs(RSMon.PASSES) do if Passes.possui(player, p.chave) then pagante = true end end
	Telemetria.evento(player, perfil, "PortalReached", math.floor(Telemetria.minutosJogados(perfil) * 10) / 10,
		{ mundo = area.id, pagante = pagante and 1 or 0 })
	PlayerData.sincronizar(player)
	return { ok = true, msg = area.nome .. " desbloqueada!", areaId = area.id }
end

function Progresso.resgatarMissao(player, id)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	local m = type(id) == "string" and Config.missaoPorId(id)
	if not m then return { ok = false, msg = "Missao inexistente" } end
	local e = perfil.missoes[m.id]
	if not e or e.p < m.meta then return { ok = false, msg = "Missao ainda nao concluida" } end
	if e.r then return { ok = false, msg = "Recompensa ja resgatada" } end
	e.r = true
	perfil.moeda += m.premio
	Telemetria.economia(player, perfil, true, m.premio, "Gameplay", "missao_" .. m.id)
	PlayerData.sincronizar(player)
	return { ok = true, msg = "+" .. Config.formatar(m.premio) .. " moedas" }
end

return Progresso

