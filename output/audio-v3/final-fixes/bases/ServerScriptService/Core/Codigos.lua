-- CODIGOS: fica no servidor pra ninguem ver a lista pelo cliente.
-- Pra criar um codigo novo, adicione uma linha em CODIGOS (em MAIUSCULO).
--   moeda  = moedas que o jogador ganha
--   pet    = id de um pet de Config.Pets (opcional)
--   hat    = id de um hat de Config.Hats (opcional)
--   ativo  = false pra desligar sem apagar
-- Cada jogador so resgata cada codigo uma vez.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)

local CODIGOS = {
	LANCAMENTO = { moeda = 100, ativo = true },  -- ~5 min de jogo no inicio
	BEMVINDO   = { moeda = 50, hat = "chakra_106490972825856", ativo = true }, -- Kakashi (raro)
	NARUTO     = { pet = "naruto", ativo = true },
}

local Codigos = {}
local ultimo = {}

function Codigos.resgatar(player, texto)
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false } end
	if type(texto) ~= "string" then return { ok = false } end
	local agora = os.clock()
	if ultimo[player] and agora - ultimo[player] < 1.5 then return { ok = false, msg = "Aguarde um pouco" } end
	ultimo[player] = agora

	local codigo = texto:upper():gsub("%s+", "")
	local c = CODIGOS[codigo]
	if not c or c.ativo == false then return { ok = false, msg = "Codigo invalido ou expirado" } end
	perfil.codigos = perfil.codigos or {}
	if perfil.codigos[codigo] then return { ok = false, msg = "Voce ja usou esse codigo" } end

	local partes = {}
	if c.hat and Config.hatPorId(c.hat) then
		if PlayerData.totalHats(perfil) >= PlayerData.capacidadeHats(perfil) then
			return { ok = false, msg = "Inventário de hats cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoHat(perfil, c.hat, 1)
		table.insert(partes, Config.hatPorId(c.hat).nome)
	end
	if c.pet and Config.petPorId(c.pet) then
		if PlayerData.totalPets(perfil) >= PlayerData.capacidadePets(perfil) then
			return { ok = false, msg = "Inventário de pets cheio. Libere espaço e tente de novo." }
		end
		PlayerData.novoPet(perfil, c.pet, 1)
		table.insert(partes, Config.petPorId(c.pet).nome)
	end
	if c.moeda and c.moeda > 0 then
		perfil.moeda += c.moeda
		table.insert(partes, Config.formatar(c.moeda) .. " moedas")
	end
	perfil.codigos[codigo] = true
	PlayerData.sincronizar(player)
	return { ok = true, msg = "Codigo resgatado: " .. table.concat(partes, " + ") }
end

game:GetService("Players").PlayerRemoving:Connect(function(p) ultimo[p] = nil end)

return Codigos

