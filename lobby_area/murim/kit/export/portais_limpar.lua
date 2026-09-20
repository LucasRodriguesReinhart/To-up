-- portais_limpar.lua - tira de cena os portais procedurais antigos do Santuario, que ficam exatamente
-- em cima dos novos. NAO apaga nada: move as pecas para ServerStorage.PORTAIS_PROCEDURAIS_ANTIGOS,
-- entao da para voltar atras. O que FICA em cada Portal<n> e o `Disco`, porque e dele que o
-- Core.Main le o atributo AreaId e nele que esta o Touched que teleporta - e o AudioWorld do cliente
-- procura justamente por um Model chamado Portal<n> dentro do Santuario.
local SS = game:GetService("ServerStorage")
local sant = workspace:FindFirstChild("Santuario")
if not sant then return "Santuario nao encontrado" end

local dest = SS:FindFirstChild("PORTAIS_PROCEDURAIS_ANTIGOS")
if not dest then
	dest = Instance.new("Folder")
	dest.Name = "PORTAIS_PROCEDURAIS_ANTIGOS"
	dest.Parent = SS
end

local movidos, mantidos = 0, 0
for _, mod in ipairs(sant:GetChildren()) do
	if mod:IsA("Model") and mod.Name:match("^Portal%d$") then
		local caixa = dest:FindFirstChild(mod.Name)
		if not caixa then
			caixa = Instance.new("Folder")
			caixa.Name = mod.Name
			caixa.Parent = dest
		end
		for _, c in ipairs(mod:GetChildren()) do
			if c.Name == "Disco" or c.Name == "VFX_PORTAL" then
				mantidos += 1
			else
				c.Parent = caixa
				movidos += 1
			end
		end
	end
end
return string.format("guardados %d objetos em ServerStorage.%s | mantidos %d (Disco/VFX)",
	movidos, dest.Name, mantidos)
