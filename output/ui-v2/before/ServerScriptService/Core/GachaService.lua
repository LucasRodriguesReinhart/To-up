local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)
local PlayerData = require(script.Parent.PlayerData)
local Economia = require(script.Parent.Economia)
local Recompensas = require(script.Parent.Recompensas)
local Telemetria = require(script.Parent.Telemetria)

-- Gacha de personagens (economia v3.1):
--  * 1o giro da conta: gratis e garantido Raro ou melhor
--  * pity Lendario+ e Mitico+ com contadores independentes; o de Lendario zera ao sair Lendario+ (sorte ou pity)
--  * Lucky/boost multiplicam exatamente a chance de Epico+ (Config.aplicarLucky)
--  * raridade sem personagem na area cai para a de baixo (Config.distGacha)
local GachaService = {}
local rnd = Random.new()
local ultimo = {}
local COOLDOWN = 0.6

local I_LENDARIO = Config.RAR_INDICE.lendario
local I_MITICO = Config.RAR_INDICE.mitico
local I_MIN_PRIMEIRO = Config.PRIMEIRO_GIRO_MIN_RAR + 1 -- valor da economia vem indexado em 0 (simulador)

-- sorteio puro (testavel): devolve o indice de raridade e atualiza o estado de pity
function GachaService.sortear(estado, dist, r0)
	local primeiro = (estado.giros or 0) == 0
	estado.giros = (estado.giros or 0) + 1
	estado.pity.l += 1
	estado.pity.m += 1
	local r = r0 or Config.sortearIndice(rnd, dist)
	if primeiro then r = math.max(r, I_MIN_PRIMEIRO) end
	if estado.pity.m >= Config.PITY_MITICO and r < I_MITICO then r = I_MITICO end
	if estado.pity.l >= Config.PITY_LENDARIO and r < I_LENDARIO then r = I_LENDARIO end
	if r >= I_LENDARIO then estado.pity.l = 0 end
	if r >= I_MITICO then estado.pity.m = 0 end
	return r
end

function GachaService.rolar(player, areaId)
	if type(areaId) ~= "number" then return { ok = false } end
	local perfil = PlayerData.get(player)
	if not perfil then return { ok = false, msg = "Perfil nao carregado" } end

	local agora = os.clock()
	if ultimo[player] and agora - ultimo[player] < COOLDOWN then
		return { ok = false, msg = "Calma ai" }
	end

	local g = Config.Gachas[areaId]
	local area = Config.areaPorId(areaId)
	if not g or not area then return { ok = false, msg = "Gacha inexistente" } end
	if not perfil.areas[areaId] then
		return { ok = false, msg = "Desbloqueie " .. area.nome .. " primeiro" }
	end
	local gratis = (perfil.giros or 0) == 0
	local custo = gratis and 0 or g.custo
	if perfil.moeda < custo then
		return { ok = false, msg = "Faltam " .. Config.formatar(custo - perfil.moeda) .. " moedas" }
	end
	if Recompensas.inventarioPetsCheio(player, perfil) then
		return { ok = false, msg = "Inventário de pets cheio! Alimente ou libere espaço." }
	end

	-- distancia real: o cliente nao decide isso
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	if not hrp then return { ok = false } end
	local maq = workspace:FindFirstChild("Gachas")
	maq = maq and maq:FindFirstChild("Gacha_" .. area.tema)
	if maq then
		local pad = maq:FindFirstChild("PadGacha")
		if pad and (hrp.Position - pad.Position).Magnitude > 60 then
			return { ok = false, msg = "Chegue perto da maquina" }
		end
	end

	ultimo[player] = agora
	if custo > 0 then
		perfil.moeda -= custo
		Telemetria.economia(player, perfil, false, custo, "Shop", "gacha_" .. areaId)
	end

	local dist = Config.distGacha(areaId, Economia.luckyMult(player, perfil))
	local r = GachaService.sortear(perfil, dist)
	local raridade = Config.RAR_IDS[r]
	local candidatos = Config.petsDaRaridade(raridade, areaId)
	while #candidatos == 0 and r > 1 do -- seguranca: nunca some com a moeda
		r -= 1
		raridade = Config.RAR_IDS[r]
		candidatos = Config.petsDaRaridade(raridade, areaId)
	end
	local pet = candidatos[rnd:NextInteger(1, #candidatos)]
	local novo = not perfil.index.pets[pet.id]
	local uid = PlayerData.novoPet(perfil, pet.id, 1)

	PlayerData.progredirMissao(perfil, areaId, "invocar", 1)
	if novo and #perfil.petsEquipados < PlayerData.slotsPets(perfil) then
		table.insert(perfil.petsEquipados, uid)
	end
	Telemetria.marco(player, perfil, "FirstPet", { origem = gratis and "giro_gratis" or "gacha" })
	Telemetria.evento(player, perfil, "GachaRoll", r, { area = areaId, pity_l = perfil.pity.l, pity_m = perfil.pity.m, gratis = gratis and 1 or 0 })

	PlayerData.sincronizar(player)
	return {
		ok = true,
		petId = pet.id,
		nome = pet.nome,
		raridade = raridade,
		novo = novo,
		gratis = gratis,
		pity = { l = perfil.pity.l, m = perfil.pity.m },
		ovo = Config.OVO_MODELOS[rnd:NextInteger(1, #Config.OVO_MODELOS)],
	}
end

function GachaService.limpar(player)
	ultimo[player] = nil
end

return GachaService

