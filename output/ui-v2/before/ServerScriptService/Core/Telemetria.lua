-- Telemetria (GDD v3.1 secao 10): AnalyticsService (Creator Analytics).
-- Todo evento leva econ_versao e as variantes de experimento do jogador.
-- Em Studio os eventos tambem ficam num historico em memoria (Telemetria.historico) para testes.
local AnalyticsService = game:GetService("AnalyticsService")
local RunService = game:GetService("RunService")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)

local T = {}
T.historico = {}
local MAX_HIST = 300

-- funil de onboarding (ordem = passo). Joined e o passo 1.
T.FUNIL = { "Joined", "FirstOreMined", "FirstHatEquipped", "FirstSell", "FirstUpgrade", "FirstPet", "FirstFusion", "FirstPortal" }

local Experimentos -- injetado (evita require circular)
function T.usarExperimentos(mod) Experimentos = mod end

local Campo = Enum.AnalyticsCustomFieldKeys

local function campos(perfil, extra)
	local exp = Experimentos and perfil and Experimentos.resumo(perfil) or ""
	return {
		[Campo.CustomField01.Name] = "econ:" .. Config.ECON_VERSAO,
		[Campo.CustomField02.Name] = exp ~= "" and exp or "exp:nenhum",
		[Campo.CustomField03.Name] = extra or "",
	}
end

local function guardar(player, nome, valor, extra)
	if not RunService:IsStudio() then return end
	table.insert(T.historico, { t = os.clock(), user = player and player.UserId or 0, nome = nome, valor = valor, extra = extra })
	if #T.historico > MAX_HIST then table.remove(T.historico, 1) end
end

-- detalhes = tabela simples; vira texto "chave=valor;..." no CustomField03 (limite de campos da Roblox)
local function texto(detalhes)
	if type(detalhes) ~= "table" then return detalhes and tostring(detalhes) or "" end
	local partes = {}
	for k, v in pairs(detalhes) do table.insert(partes, tostring(k) .. "=" .. tostring(v)) end
	table.sort(partes)
	return table.concat(partes, ";")
end

function T.evento(player, perfil, nome, valor, detalhes)
	local extra = texto(detalhes)
	guardar(player, nome, valor, extra)
	if not player or not player.Parent then return end
	pcall(function()
		AnalyticsService:LogCustomEvent(player, nome, valor or 1, campos(perfil, extra))
	end)
end

-- marco unico por conta (FirstOreMined etc.): registra no funil e no evento
function T.marco(player, perfil, nome, detalhes)
	if not perfil or not perfil.tel or perfil.tel[nome] then return false end
	perfil.tel[nome] = os.time()
	local passo = table.find(T.FUNIL, nome)
	local minutos = math.floor(((perfil.tempoJogado or 0) + (perfil.__entrouEm and (os.clock() - perfil.__entrouEm) or 0)) / 6) / 10
	if passo then
		pcall(function()
			AnalyticsService:LogOnboardingFunnelStepEvent(player, passo, nome, campos(perfil, "min=" .. minutos))
		end)
	end
	T.evento(player, perfil, nome, minutos, detalhes)
	return true
end

-- moedas: fonte (Source) e gasto (Sink)
function T.economia(player, perfil, fonte, quantidade, tipo, item)
	if not quantidade or quantidade <= 0 then return end
	guardar(player, fonte and "Economy+" or "Economy-", quantidade, tostring(tipo) .. ":" .. tostring(item))
	pcall(function()
		AnalyticsService:LogEconomyEvent(player,
			fonte and Enum.AnalyticsEconomyFlowType.Source or Enum.AnalyticsEconomyFlowType.Sink,
			"Moedas", quantidade, perfil and perfil.moeda or 0,
			tipo or Enum.AnalyticsEconomyTransactionType.Gameplay.Name, item, campos(perfil))
	end)
end

function T.minutosJogados(perfil)
	return ((perfil.tempoJogado or 0) + (perfil.__entrouEm and (os.clock() - perfil.__entrouEm) or 0)) / 60
end

return T

