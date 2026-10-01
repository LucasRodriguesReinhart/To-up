--!strict
-- Tela de invocacao do gacha de OVOS (pets).
-- Abre pelo ProximityPrompt da maquina, igual o painel do Ignis.
-- Todo o sorteio continua no servidor: Remotes.RolarGacha -> GachaService.
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

local Banners = require(ReplicatedStorage:WaitForChild("BannersConfig"))
local Remotes = ReplicatedStorage:WaitForChild("Remotes")

local gui = script.Parent
local root = gui:WaitForChild("Root")
local conteudo = root:WaitForChild("Conteudo")
local tpl = gui:WaitForChild("Templates")

local selo = conteudo.Topo.SeloBanner
local info = conteudo.InfoBanner
local blocoChances = conteudo.Chances
local dropsFrame = conteudo.Drops
local viewport = conteudo.PreviewModelo
local painelRes = conteudo.Resultado
local btn1 = conteudo.BotoesInvocar.Invocarx1
local btn10 = conteudo.BotoesInvocar.Invocarx10
local lblMoeda = conteudo.Topo.Moedas.Ouro.Valor

local INFO = TweenInfo.new(0.22, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local indiceAtual = 1
local dados = nil
local rolando = false

-- ---------- escala responsiva ----------
local escala = conteudo:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
escala.Parent = conteudo
local function escalaAlvo(): number
	local vp = workspace.CurrentCamera.ViewportSize
	return math.clamp(math.min((vp.X-24) / 1600, (vp.Y-28) / 760), 0.2, 1.25)
end
escala.Scale = escalaAlvo()
workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
	escala.Scale = escalaAlvo()
end)

-- ---------- utilitarios ----------
local function limpar(pai: Instance)
	for _, f in ipairs(pai:GetChildren()) do
		if f:IsA("GuiObject") then f:Destroy() end
	end
end

local function formatar(n: number): string
	local s = tostring(math.floor(n)):reverse():gsub("(%d%d%d)", "%1.")
	return (s:reverse():gsub("^%.", ""))
end

-- numero grande vira 1.2M, 3.4B... senao estoura a pilula do topo
local SUFIXOS = { "", "K", "M", "B", "T", "Qa", "Qi" }
local function curto(n: number): string
	local i = 1
	while n >= 1000 and i < #SUFIXOS do
		n /= 1000
		i += 1
	end
	if i == 1 then return formatar(n) end
	return string.format("%.1f%s", n, SUFIXOS[i])
end

local function atualizarMoeda()
	lblMoeda.Text = dados and ("$ " .. curto(dados.moeda)) or "$ 0"
end

-- ---------- estrelas ----------
local function montarEstrelas(qtd: number)
	limpar(info.Estrelas)
	for i = 1, qtd do
		local e = Instance.new("TextLabel")
		e.Name = "Estrela" .. i
		e.Size = UDim2.fromOffset(30, 30)
		e.BackgroundTransparency = 1
		e.Text = "★"
		e.TextColor3 = Color3.fromRGB(255, 206, 60)
		e.TextSize = 30
		e.FontFace = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Heavy)
		e.ZIndex = 7
		local st = Instance.new("UIStroke")
		st.Color = Color3.fromRGB(120, 70, 0)
		st.Thickness = 2
		st.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
		st.Parent = e
		e.Parent = info.Estrelas
	end
end

-- ---------- chances reais da area ----------
local function montarChances(banner)
	for _, f in ipairs(blocoChances:GetChildren()) do
		if f:IsA("GuiObject") and f.Name ~= "TituloChances" then f:Destroy() end
	end
	local chances=Banners.chances(banner.areaId)
 blocoChances.Size=UDim2.fromOffset(530,42+#chances*29)
 for i, c in ipairs(chances) do
		local barra = tpl.BarraTemplate:Clone()
		barra.Name = "Chance_" .. c.raridade
		barra.Visible = true
		barra.LayoutOrder = i
		barra.Nome.Text = string.upper(c.nome)
		barra.Valor.Text = string.format("%.2f%%", c.pct)
		barra.Fill.Cor.Color = ColorSequence.new(c.cor, c.cor:Lerp(Color3.fromRGB(20, 12, 40), 0.45))
		barra.Fill.Size = UDim2.fromScale(0, 1)
		barra.Parent = blocoChances
		-- barra em escala de raiz, senao raridade rara vira um risco invisivel
		local frac = math.clamp(math.sqrt(c.pct / 100), 0.04, 1)
		TweenService:Create(barra.Fill, TweenInfo.new(0.45, Enum.EasingStyle.Quad), {
			Size = UDim2.fromScale(frac, 1),
		}):Play()
	end
end

-- ---------- pets de destaque ----------
local function montarDestaques(banner)
	limpar(dropsFrame)
	for i, d in ipairs(Banners.destaques(banner.areaId, 4)) do
		local card = tpl.CardTemplate:Clone()
		card.Name = "Pet" .. i
		card.Visible = true
		card.LayoutOrder = i
		card.Nome.Text = d.nome
		card.Raridade.Text = string.upper(d.raridade) .. "  •  PET"
		card.Raridade.TextColor3 = d.cor
		card.Stat.Text = d.stat
		card.Faixa.BackgroundColor3 = d.cor
		card.Thumb.UIStroke.Color = d.cor
		card.Thumb.Inicial.Text = string.upper(string.sub(d.nome, 1, 1))
		card.Thumb.Inicial.TextColor3 = d.cor
		card.Position = UDim2.fromOffset(36, 0)
		card.Parent = dropsFrame
		task.delay(0.04 * i, function()
			if card.Parent then
				TweenService:Create(card, INFO, {Position = UDim2.fromOffset(0, 0)}):Play()
			end
		end)
	end
end

-- ---------- preview 3D da maquina ----------
local conexaoGiro: RBXScriptConnection? = nil
local function montarPreview(banner)
	if conexaoGiro then conexaoGiro:Disconnect(); conexaoGiro = nil end
	viewport:ClearAllChildren()

	local pasta = ReplicatedStorage:FindFirstChild("PreviewModelos")
	local origem = pasta and pasta:FindFirstChild(banner.gacha)
	if not origem then return end

	local modelo = origem:Clone()
	modelo.Parent = viewport

	local cam = Instance.new("Camera")
	cam.Parent = viewport
	viewport.CurrentCamera = cam
	viewport.Ambient = Color3.fromRGB(196, 186, 226)
	viewport.LightColor = Color3.fromRGB(255, 250, 240)
	viewport.LightDirection = Vector3.new(-0.4, -1, -0.6)

	local cf, tam = modelo:GetBoundingBox()
	local base = CFrame.new(modelo:GetPivot().Position - cf.Position)
	modelo:PivotTo(base)

	local raio = math.max(tam.X, tam.Y, tam.Z)
	cam.CFrame = CFrame.new(Vector3.new(0, tam.Y * 0.18, raio * 1.28), Vector3.zero)

	local ang = 0
	conexaoGiro = RunService.RenderStepped:Connect(function(dt)
		if not modelo.Parent or not root.Visible then return end
		ang += dt * 0.5
		modelo:PivotTo(CFrame.Angles(0, ang, 0) * base)
	end)
end

-- ---------- troca de banner ----------
local function aplicarBanner(idx: number)
	indiceAtual = ((idx - 1) % #Banners.Banners) + 1
	local b = Banners.Banners[indiceAtual]

	info.Titulo.Text = b.titulo
	info.TituloSombra.Text = b.titulo
	info.TituloGlow.Text = b.titulo
	selo.Nome.Text = b.subtitulo
	selo.Icone.BackgroundColor3 = b.corA
	info.Descricao.Text = b.descricao
	root.Fundo.UIGradient.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, Color3.fromRGB(28,22,73)),
		ColorSequenceKeypoint.new(0.45, Color3.fromRGB(48,40,142):Lerp(b.corA,.10)),
		ColorSequenceKeypoint.new(1, Color3.fromRGB(10,8,27)),
	})

	btn1.Custo.Text = "$ " .. curto(b.custo)
	btn10.Custo.Text = "$ " .. curto(b.custo * 10)
	painelRes.Visible = false

	montarEstrelas(b.estrelas)
	montarChances(b)
	montarDestaques(b)
	montarPreview(b)

end


-- ---------- abrir / fechar ----------
local aberto = false
local function definirVisivel(v: boolean)
	aberto = v
	if v then
		local alvo = escalaAlvo()
		escala.Scale = alvo * 0.94
		gui.Enabled = true
		root.Visible = true
		TweenService:Create(escala, INFO, {Scale = alvo}):Play()
	else
		root.Visible = false
		gui.Enabled = false
	end
end

conteudo.Topo.Fechar.MouseButton1Click:Connect(function() definirVisivel(false) end)
conteudo.Topo.FecharDireita.MouseButton1Click:Connect(function() definirVisivel(false) end)

UserInputService.InputBegan:Connect(function(input, processado)
	if processado then return end
	if input.KeyCode == Enum.KeyCode.Escape and aberto then
		definirVisivel(false)
	end
end)

-- prompt da maquina manda abrir, igual o Ignis faz
Remotes:WaitForChild("AbrirGacha").OnClientEvent:Connect(function(areaId)
	local _, indice = Banners.porArea(areaId or 1)
	aplicarBanner(indice)
	definirVisivel(true)
end)

-- ---------- dados do jogador (moeda no topo) ----------
Remotes:WaitForChild("AtualizarDados").OnClientEvent:Connect(function(novo)
	dados = novo
	atualizarMoeda()
end)
task.spawn(function()
	dados = Remotes:WaitForChild("PedirDados"):InvokeServer()
	atualizarMoeda()
end)

-- ---------- invocar ----------
local function mostrarResultado(res, indice: number?, total: number?)
	local cor = Banners.Raridades[res.raridade] and Banners.Raridades[res.raridade].cor
		or Color3.fromRGB(255, 255, 255)
	painelRes.Visible = true
	painelRes.UIStroke.Color = cor
	painelRes.Nome.Text = res.nome
	painelRes.Nome.TextColor3 = cor
	local etiqueta = (Banners.Raridades[res.raridade] and Banners.Raridades[res.raridade].nome or res.raridade)
	local sufixo = res.novo and "  •  NOVO!" or "  •  duplicado"
	if total and total > 1 then
		sufixo = sufixo .. string.format("  •  %d/%d", indice or 1, total)
	end
	painelRes.Sub.Text = string.upper(etiqueta) .. sufixo
	painelRes.Size = UDim2.fromOffset(400, 74)
	TweenService:Create(painelRes, INFO, {Size = UDim2.fromOffset(430, 74)}):Play()
end

local function avisar(msg: string)
	painelRes.Visible = true
	painelRes.UIStroke.Color = Color3.fromRGB(255, 110, 90)
	painelRes.Nome.Text = msg
	painelRes.Nome.TextColor3 = Color3.fromRGB(255, 150, 130)
	painelRes.Sub.Text = ""
end

local function invocar(qtd: number)
	if rolando then return end
	rolando = true
	local b = Banners.Banners[indiceAtual]
	for i = 1, qtd do
		local ok, res = pcall(function()
			return Remotes.RolarGacha:InvokeServer(b.areaId)
		end)
		if not ok or not res then
			avisar("Falhou, tenta de novo")
			break
		end
		if res.ok then
			mostrarResultado(res, i, qtd)
		else
			avisar(res.msg or "Nao deu")
			break
		end
		if i < qtd then task.wait(0.7) end   -- o servidor tem cooldown de 0.6s por roll
	end
	rolando = false
end

local function prepararBotao(botao: TextButton, qtd: number)
	local tamanhoBase = botao.Size
	botao.MouseEnter:Connect(function()
		TweenService:Create(botao, INFO, {Size = tamanhoBase + UDim2.fromOffset(10, 4)}):Play()
	end)
	botao.MouseLeave:Connect(function()
		TweenService:Create(botao, INFO, {Size = tamanhoBase}):Play()
	end)
	botao.MouseButton1Click:Connect(function()
		TweenService:Create(botao, TweenInfo.new(0.08), {BackgroundColor3 = Color3.fromRGB(255, 236, 170)}):Play()
		task.delay(0.1, function()
			TweenService:Create(botao, INFO, {BackgroundColor3 = Color3.fromRGB(240, 236, 226)}):Play()
		end)
		invocar(qtd)
	end)
end
prepararBotao(btn1, 1)
prepararBotao(btn10, 10)

btn1.Titulo.Text = "ABRIR x1"
btn10.Titulo.Text = "ABRIR x10"

aplicarBanner(1)
definirVisivel(false)

