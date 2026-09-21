-- chao_simples.lua - o CHAO do lobby em Part chapada, no lugar das malhas assadas.
--
-- Por que nao e mais malha: o calcamento eram 985 lajes e o gramado 97 ladrilhos de relva
-- geometrica. No jogo o primeiro lia como tabuleiro de xadrez e o segundo como tapete de espinhos
-- escuros, e juntos custavam quase um milhao de triangulos. Chao e FUNDO: num simulator ele tem de
-- ser claro, uniforme e de graca, e a leitura de calcamento vem da JUNTA, nao de mil lajes.
--
-- Roda depois de montar_lobby.lua. E idempotente: refaz a pasta do zero a cada execucao.

local L = workspace:FindFirstChild("LOBBY_MURIM")
if not L then return "PARE: LOBBY_MURIM ausente. Rode montar_lobby.lua antes." end

local velho = L:FindFirstChild("ChaoSimples")
if velho then velho:Destroy() end
local CH = Instance.new("Folder"); CH.Name = "ChaoSimples"; CH.Parent = L

-- Tons ajustados contra a praca JA TEXTURADA no jogo. A base estava clara demais e o olho lia dois
-- pisos diferentes colados; na referencia e UM calcamento continuo, e a praca so se distingue pelo
-- desenho (aneis e raios), nunca por ser de outra pedra.
local PEDRA  = Color3.fromRGB(188, 174, 150)   -- base, no tom que o atlas da a praca
local JUNTA  = Color3.fromRGB(162, 148, 126)
local ARO    = Color3.fromRGB(212, 200, 178)
local FIO    = Color3.fromRGB(146, 132, 110)
local GRAMA  = Color3.fromRGB(116, 176, 92)
local TERRA  = Color3.fromRGB(128, 104, 78)
local MARGEM = Color3.fromRGB(152, 142, 124)

local function pasta(n) local f = Instance.new("Folder"); f.Name = n; f.Parent = CH; return f end
local function parte(pai, nome, tam, cf, cor, mat)
	local p = Instance.new("Part")
	p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanTouch = false; p.CanQuery = false
	p.CastShadow = false; p.Material = mat or Enum.Material.SmoothPlastic; p.Color = cor
	p.Size = tam; p.CFrame = cf; p.Parent = pai
	return p
end

-- 1) BASE: uma placa so cobrindo o terreno inteiro.
local B = pasta("Base")
parte(B, "Base", Vector3.new(364, 3, 420), CFrame.new(0, -2.0, -8), PEDRA)

-- 2) JUNTAS: fios escuros a cada 26 studs. Sao eles que dizem "laje grande de pedra"; desenhar as
--    lajes uma a uma foi o erro anterior, porque o modulo pequeno vira xadrez visto de cima.
local J = pasta("Juntas")
for x = -182, 182, 26 do parte(J, "Jx", Vector3.new(0.7, 0.25, 420), CFrame.new(x, -0.42, -8), JUNTA) end
for z = -218, 202, 26 do parte(J, "Jz", Vector3.new(364, 0.25, 0.7), CFrame.new(0, -0.42, z), JUNTA) end

-- 3) ARO DO HEXAGONO: o espaco central so le como hexagono se a forma estiver DESENHADA no chao.
--    Piso hexagonal sem contorno le apenas como "praca de contorno irregular".
local A = pasta("AroHex")
local V = {
	Vector3.new(0, 0, 74), Vector3.new(70, 0, 42), Vector3.new(70, 0, -42),
	Vector3.new(0, 0, -74), Vector3.new(-70, 0, -42), Vector3.new(-70, 0, 42),
}
for k = 1, 6 do
	local a, b = V[k], V[(k % 6) + 1]
	local meio = (a + b) / 2
	local comp = (b - a).Magnitude
	local ang = math.atan2(b.X - a.X, b.Z - a.Z)
	parte(A, "Faixa", Vector3.new(5.0, 0.30, comp), CFrame.new(meio.X, -0.40, meio.Z) * CFrame.Angles(0, ang, 0), ARO)
	parte(A, "Fio", Vector3.new(1.1, 0.34, comp),
		CFrame.new(meio.X, -0.39, meio.Z) * CFrame.Angles(0, ang, 0) * CFrame.new(3.2, 0, 0), FIO)
end

-- 4) CANTEIROS: mancha verde com fio de terra na divisa. O jardim em si (arvores, flores) fica por
--    conta do usuario; aqui so se marca ONDE ele pode existir.
local G = pasta("Canteiros")
local CANT = {
	{112,166,-186,-104}, {-166,-112,-186,-104}, {112,166,60,140}, {-166,-112,58,140},
	{24,60,-196,-160}, {-60,-24,-196,-160}, {114,166,-60,30}, {-166,-116,-96,-58},
	{22,58,74,138}, {-58,-22,74,138}, {68,100,140,186}, {-100,-68,140,186},
}
for i, c in ipairs(CANT) do
	parte(G, "Terra" .. i, Vector3.new(c[2] - c[1], 1.2, c[4] - c[3]),
		CFrame.new((c[1] + c[2]) / 2, -1.0, (c[3] + c[4]) / 2), TERRA)
	parte(G, "Grama" .. i, Vector3.new(c[2] - c[1] - 2.8, 1.4, c[4] - c[3] - 2.8),
		CFrame.new((c[1] + c[2]) / 2, -1.0, (c[3] + c[4]) / 2), GRAMA, Enum.Material.Grass)
end

-- 5) MARGEM DO RIO: sem ela a agua encosta no calcamento em corte seco e le como retangulo azul
--    pintado no chao. A faixa de pedra meio submersa e o que faz a agua parecer estar DENTRO de algo.
local M = pasta("Margem")
local corpos = 0
for _, d in ipairs(L:GetDescendants()) do
	if d:IsA("BasePart") and d.Name:match("^Lago") then
		local s, cf = d.Size, d.CFrame
		if s.X > 4 and s.Z > 4 then
			corpos += 1
			for _, lado in ipairs({1, -1}) do
				if s.X >= s.Z then
					parte(M, "Marg", Vector3.new(s.X + 5, 1.6, 3.2),
						cf * CFrame.new(0, -0.3, lado * (s.Z / 2 + 1.4)), MARGEM)
				else
					parte(M, "Marg", Vector3.new(3.2, 1.6, s.Z + 5),
						cf * CFrame.new(lado * (s.X / 2 + 1.4), -0.3, 0), MARGEM)
				end
			end
		end
	end
end

-- 6) PECA INVISIVEL NAO LANCA SOMBRA. Uma laje invisivel de 306 x 200 studs de outro sistema estava
--    deitada sobre a praca e projetava uma mancha cinza enorme nela. Escopo preso ao retangulo do
--    lobby, para nao mexer no resto do jogo.
local semSombra = 0
for _, d in ipairs(workspace:GetDescendants()) do
	if d:IsA("BasePart") and d.Transparency >= 0.99 and d.CastShadow then
		local p = d.Position
		if math.abs(p.X) < 340 and p.Z > -260 and p.Z < 250 and p.Y > -60 and p.Y < 140 then
			d.CastShadow = false; semSombra += 1
		end
	end
end

return string.format("chao simples: base + %d juntas + aro do hexagono + %d canteiros + %d faixas de margem em %d corpos d'agua | %d pecas invisiveis deixaram de lancar sombra",
	#J:GetChildren(), #CANT, #M:GetChildren(), corpos, semSombra)
