-- portais_vfx.lua - liga os efeitos do pack VFX_Guardado_Lobby nos seis portais do Santuario.
-- Cada area ganha o vortice base (Portal-Enter-01) tingido com a cor do Config.Temas mais um efeito
-- com a cara do anime dela. Roda no Edit, e idempotente: apaga o que ele mesmo criou antes de refazer.
--
-- CALIBRAGEM (a primeira versao tapou a pedra inteira e foi corrigida pela captura):
--   o pack e de efeito de COMBATE, feito para uma Part de 1 stud e para durar meio segundo na tela.
--   No cenario ele fica ligado o tempo todo, entao tudo desce: tamanho, taxa e alcance da luz.
--   PortalLines sai fora de proposito (taxa 50 e velocidade 15: vira risco atravessando o Santuario).
local SS = game:GetService("ServerStorage")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)

local pack = SS:FindFirstChild("VFX_Guardado_Lobby")
if not pack then return "VFX_Guardado_Lobby nao encontrado" end
local anime = pack:FindFirstChild("Anime")
local sant = workspace:FindFirstChild("Santuario")
if not (anime and sant) then return "Anime/Santuario nao encontrado" end

local ESCALA_VORTICE = 1.5      -- o vao tem 6.8 de largura; 3.2 tapava a pedra inteira
local ESCALA_SOTAQUE = 0.7
local TAXA_VORTICE   = 0.5
local TAXA_SOTAQUE   = 0.12
-- PortalLines: taxa 50 e velocidade 15, vira risco atravessando o Santuario.
-- Portal: cor preta com blend NORMAL (LightEmission 0). No pack ele e o nucleo escuro do portal;
-- aqui a malha do vortice ja tem nucleo aceso, entao ele so aparecia como um oval preto no meio.
local DESCARTAR      = { PortalLines = true, Portal = true }

-- o sotaque de cada area: UM efeito do pack que combina com o anime dela
local SOTAQUE = {
	chakra   = "Wind-01",      -- Naruto: vento
	ki       = "Charge-01",    -- Dragon Ball: carga de ki
	nichirin = "Slashes-01",   -- Demon Slayer: cortes da respiracao
	sombra   = "Smoke-01",     -- sombra: fumaca
	mare     = "Water-02",     -- One Piece: agua
	serio    = "Wind-02",      -- serio: deslocamento de ar
}

local function escalar(v, n)
	if typeof(v) == "NumberSequence" then
		local kp = {}
		for _, k in ipairs(v.Keypoints) do
			table.insert(kp, NumberSequenceKeypoint.new(k.Time, k.Value * n, k.Envelope * n))
		end
		return NumberSequence.new(kp)
	end
	return NumberSequence.new(v * n)
end

-- Tingir achatando para uma cor so mataria o gradiente do efeito. Aqui a cor do tema entra como
-- MULTIPLICADOR sobre a sequencia original, o que preserva as passagens claro/escuro do pack.
local function tingir(pe, cor)
	local orig = pe.Color
	local kp = {}
	for _, k in ipairs(orig.Keypoints) do
		table.insert(kp, ColorSequenceKeypoint.new(k.Time, Color3.new(
			k.Value.R * cor.R, k.Value.G * cor.G, k.Value.B * cor.B)))
	end
	pe.Color = ColorSequence.new(kp)
end

local function ajustar(c, cor, escala, taxa)
	c.Size = escalar(c.Size, escala)
	c.Rate = math.max(1, c.Rate * taxa)
	tingir(c, cor)
	-- NAO mexer em LightEmission/LightInfluence: as particulas de brilho do pack sao feitas para blend
	-- ADITIVO, onde o preto da textura some. Baixar LightEmission fez o fundo preto aparecer e o portal
	-- do ki ganhou um borrao escuro no meio. Quem controla o excesso aqui e tamanho e taxa, nao blend.
	c.ZOffset = -0.5
end

local feitos, avisos = 0, {}
for _, mod in ipairs(sant:GetChildren()) do
	local disco = mod:FindFirstChild("Disco")
	local id = disco and disco:GetAttribute("AreaId")
	local area = id and Config.areaPorId(id)
	if area then
		local tema = Config.Temas[area.tema]
		local cor = (typeof(tema) == "table" and (tema.cor or tema.Cor)) or Color3.fromRGB(200, 200, 200)

		-- o disco Neon do jogo fica DENTRO do vao do portal novo e briga com o vortice de pedra.
		-- Some com ele, mas mantem CanTouch: e nele que o Core.Main liga o teleporte.
		disco.Transparency = 1
		disco.CanTouch = true

		local antigo = mod:FindFirstChild("VFX_PORTAL")
		if antigo then antigo:Destroy() end
		local folder = Instance.new("Folder"); folder.Name = "VFX_PORTAL"; folder.Parent = mod

		local base = Instance.new("Part")
		base.Name = "VortexEmitter"
		base.Size = Vector3.new(0.2, 0.2, 0.2)
		base.Transparency = 1
		base.Anchored = true
		base.CanCollide = false
		base.CanQuery = false
		base.CanTouch = false
		base.CastShadow = false
		-- o portal encara -X; girar 90 em Z manda o +Y local (direcao de emissao padrao) para -X,
		-- que e o lado do jogador. Sem isso as linhas do vortice saem para dentro da parede.
		base.CFrame = CFrame.new(disco.Position + Vector3.new(-0.8, 2.6, 0)) * CFrame.Angles(0, 0, math.rad(90))
		base.Parent = folder

		local fonte = anime:FindFirstChild("Portal-Enter-01")
		if fonte then
			for _, pe in ipairs(fonte:GetDescendants()) do
				if pe:IsA("ParticleEmitter") and not DESCARTAR[pe.Name] then
					local c = pe:Clone()
					ajustar(c, cor, ESCALA_VORTICE, TAXA_VORTICE)
					c.Parent = base
				end
			end
		else
			table.insert(avisos, "Portal-Enter-01 ausente")
		end

		-- sotaque do anime: um so, no mesmo plano do vao, pequeno. Com 1.6 de escala e 6 studs de
		-- altura ele invadia o portal vizinho, que fica a 13 studs.
		local nome = SOTAQUE[area.tema]
		local src = nome and anime:FindFirstChild(nome)
		if src then
			local p = base:Clone()
			p:ClearAllChildren()
			p.Name = "Accent_" .. nome
			p.CFrame = CFrame.new(disco.Position + Vector3.new(-1.2, -1.2, 0)) * CFrame.Angles(0, 0, math.rad(90))
			p.Parent = folder
			for _, pe in ipairs(src:GetDescendants()) do
				if pe:IsA("ParticleEmitter") then
					local c = pe:Clone()
					ajustar(c, cor, ESCALA_SOTAQUE, TAXA_SOTAQUE)
					c.Parent = p
				end
			end
		elseif nome then
			table.insert(avisos, nome .. " ausente")
		end

		-- luz do portal: pinta a pedra em volta com a cor da area sem lavar o vizinho a 13 studs
		local luz = Instance.new("PointLight")
		luz.Color = cor
		luz.Brightness = 1.4
		luz.Range = 15
		luz.Shadows = false
		luz.Parent = base

		feitos += 1
	end
end

-- ---------- animacao ambiente: sem movimento nenhum a "lasca flutuando" e so uma pedra parada no ar.
-- Roda no CLIENTE, de proposito. A primeira versao era um Script em ServerScriptService escrevendo
-- CFrame de 12 pecas ancoradas e Brightness de 6 luzes a cada Heartbeat: sao 18 propriedades por frame
-- REPLICADAS para todo mundo, para sempre, so para balancar pedra. No cliente custa zero de banda.
local SP = game:GetService("StarterPlayer")
local SPS = SP:WaitForChild("StarterPlayerScripts")
for _, onde in ipairs({ SPS, game:GetService("ServerScriptService") }) do
	local velho = onde:FindFirstChild("PortaisAmbiente")
	if velho then velho:Destroy() end          -- inclusive a versao de servidor, se ainda estiver la
end
local amb = Instance.new("LocalScript")
amb.Name = "PortaisAmbiente"
amb.Source = [==[
-- PortaisAmbiente - balanca as lascas dos portais e faz a luz do vortice respirar.
-- Instalado por lobby_area/murim/kit/export/portais_vfx.lua. Apagar aqui nao quebra mais nada.
-- E LocalScript de proposito: e decoracao, e no servidor cada frame viraria pacote de replicacao.
local RunService = game:GetService("RunService")
local sant = workspace:WaitForChild("Santuario", 30)
local lob = workspace:WaitForChild("LOBBY_MURIM", 30)
if not (sant and lob) then return end

local lascas, luzes = {}, {}
for _, d in ipairs(lob:GetDescendants()) do
	if d:IsA("MeshPart") and d.Name:match("^POR_fragmento") then
		table.insert(lascas, { p = d, cf = d.CFrame, f = 0.5 + (#lascas % 5) * 0.17, a = (#lascas % 7) * 0.9 })
	end
end
for _, mod in ipairs(sant:GetChildren()) do
	local f = mod:FindFirstChild("VFX_PORTAL")
	local b = f and f:FindFirstChild("VortexEmitter")
	local l = b and b:FindFirstChildOfClass("PointLight")
	if l then table.insert(luzes, { l = l, base = l.Brightness, a = #luzes * 1.1 }) end
end
if #lascas == 0 and #luzes == 0 then return end

-- os seis portais cabem num trecho de ~65 studs: longe dali nao ha o que animar
local FOCO = Vector3.new(124.5, 13, 0)
local ALCANCE = 140

local t = 0
RunService.RenderStepped:Connect(function(dt)
	local cam = workspace.CurrentCamera
	if not cam or (cam.CFrame.Position - FOCO).Magnitude > ALCANCE then return end
	t += dt
	for _, s in ipairs(lascas) do
		local sobe = math.sin(t * s.f + s.a) * 0.55
		s.p.CFrame = s.cf * CFrame.new(0, sobe, 0) * CFrame.Angles(0, t * 0.35 + s.a, 0)
	end
	for _, u in ipairs(luzes) do
		u.l.Brightness = u.base * (0.78 + 0.22 * math.sin(t * 1.6 + u.a))
	end
end)
]==]
amb.Parent = SPS
table.insert(avisos, "PortaisAmbiente instalado em StarterPlayerScripts (cliente)")

return string.format("VFX ligado em %d portais | avisos: %s", feitos,
	#avisos > 0 and table.concat(avisos, ", ") or "nenhum")
