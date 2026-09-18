local function maiusculo(s)
	s = string.upper(s)
	for _, par in ipairs({ { "á", "Á" }, { "ã", "Ã" }, { "â", "Â" }, { "é", "É" }, { "ê", "Ê" }, { "í", "Í" }, { "ó", "Ó" }, { "õ", "Õ" }, { "ú", "Ú" }, { "ç", "Ç" } }) do s = s:gsub(par[1], par[2]) end
	return s
end
--!strict
-- Banners da tela de invocacao. E o MESMO gacha de ovos/pets do jogo:
-- tudo vem de ReplicatedStorage.Config (custo, pesos, pets), aqui so entra
-- o que e visual - titulo, descricao e cor de cada banner.
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS:WaitForChild("Config"))

local M = {}

M.Raridades = Config.Raridades

-- texto de vitrine por area
local TEXTOS = {
	[1] = "Ninjas da Vila da Folha. Do Naruto ao lendario Sasuke secreto.",
	[2] = "Guerreiros de Ki. Goten, Piccolo, Vegeta e o Goku SSJ God secreto.",
	[3] = "Cacadores de Nichirin. Tanjiro, Hashiras e o Yoriichi secreto.",
	[5] = "Piratas da Grand Line. Usopp, Zoro, Luffy e o Mihawk secreto.",
	[6] = "Herois da Cidade Z. Tatsumaki, Boros e o Saitama secreto.",
}

-- monta um banner por area, na ordem das areas
M.Banners = {}
for _, area in ipairs(Config.Areas) do
	local tema = Config.Temas[area.tema]
	local g = Config.Gachas[area.id]
	if tema and g then
		table.insert(M.Banners, {
			id = area.tema,
			areaId = area.id,
			gacha = "Gacha_" .. area.tema,          -- Model em Workspace.Gachas
			titulo = maiusculo(area.nome),
			subtitulo = "OVO " .. maiusculo(tema.nome),
			descricao = TEXTOS[area.id] or "",
			estrelas = math.min(5, area.id),
			custo = g.custo,
			corA = tema.cor,
			corB = tema.cor:Lerp(Color3.fromRGB(20, 12, 40), 0.72),
		})
	end
end

function M.porArea(areaId: number)
	for i, b in ipairs(M.Banners) do
		if b.areaId == areaId then return b, i end
	end
	return M.Banners[1], 1
end

-- chances reais da area, ja em porcentagem e ordenadas
function M.chances(areaId: number)
	return Config.chancesGacha(areaId) or {}
end

-- ate 4 pets de destaque: os das melhores raridades que a area pode dar
function M.destaques(areaId: number, limite: number?)
	local pesos = Config.pesosGacha(areaId)
	if not pesos then return {} end

	local ordens = {}
	for chave, peso in pairs(pesos) do
		if peso > 0 then table.insert(ordens, chave) end
	end
	table.sort(ordens, function(a, b)
		return Config.Raridades[a].ordem > Config.Raridades[b].ordem
	end)

	local lista = {}
	local max = limite or 4
	for _, raridade in ipairs(ordens) do
		for _, pet in ipairs(Config.petsDaRaridade(raridade, areaId)) do
			if #lista >= max then return lista end
			table.insert(lista, {
				nome = pet.nome,
				raridade = raridade,
				cor = Config.Raridades[raridade].cor,
				corTexto = Config.Raridades[raridade].corTexto,
				stat = string.format("+%d%% dano | +%d Level Bonus", math.floor(pet.bonusDano * 100), pet.levelBonus or 0),
			})
		end
	end
	return lista
end

return M

