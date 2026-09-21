-- tudo.lua - roda, na ordem certa, tudo que vem DEPOIS de importar o LOBBY_FORJA_CELESTE.fbx.
-- Cole no Command Bar do Studio:
--   loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8766/tudo.lua"))()
local H = game:GetService("HttpService")
local BASE = "http://127.0.0.1:8766/"

if not workspace:FindFirstChild("LOBBY_FORJA_CELESTE") then
	return "PARE: importe primeiro o LOBBY_FORJA_CELESTE.fbx (Home > Import). "
		.. "O modelo importado precisa estar no Workspace com esse nome."
end

local ETAPAS = {
	{ "montar_lobby.lua",   "monta o lobby inteiro a partir das malhas importadas" },
	{ "portais_limpar.lua", "guarda os portais procedurais antigos em ServerStorage" },
	{ "portais_vfx.lua",    "liga o VFX e a animacao dos seis portais" },
	{ "materiais_alpha.lua", "AlphaMode -> Transparency: sem isso os atlas RGB saem cinza" },
	{ "agua_cartoon.lua",   "agua no sistema das areas Dragon Ball/Mare" },
	{ "chao_simples.lua",   "chao em Part chapada: base, juntas, aro do hexagono, canteiros e margem" },
	{ "verificar_lobby.lua", "confere tudo por medida" },
}

local log = {}
for i, e in ipairs(ETAPAS) do
	local nome, oque = e[1], e[2]
	local ok, corpo = pcall(function() return H:GetAsync(BASE .. nome) end)
	if not ok then
		table.insert(log, string.format("[%d/%d] %s: NAO BAIXOU (%s)", i, #ETAPAS, nome, tostring(corpo)))
		break
	end
	local fn, erroCompila = loadstring(corpo)
	if not fn then
		table.insert(log, string.format("[%d/%d] %s: NAO COMPILOU (%s)", i, #ETAPAS, nome, tostring(erroCompila)))
		break
	end
	local ok2, res = pcall(fn)
	table.insert(log, string.format("[%d/%d] %s - %s", i, #ETAPAS, nome, oque))
	table.insert(log, "      " .. (ok2 and tostring(res) or ("ERRO: " .. tostring(res))):gsub("\n", "\n      "))
	if not ok2 then break end
end
return table.concat(log, "\n")
