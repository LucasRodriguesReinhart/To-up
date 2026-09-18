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
local escala = conteudo:WaitForChild("UIScale")
local function escalaAlvo(): number
	local vp = workspace.CurrentCamera.ViewportSize
	return math.clamp(math.min((vp.X-24) / math.max(1,conteudo.Size.X.Offset), (vp.Y-28) / math.max(1,conteudo.Size.Y.Offset)), 0.2, 1.25)
end
escala.Scale = escalaAlvo()
workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
	escala.Scale = escalaAlvo()
end)

-- ---------- utilitarios ----------
local function limpar(pai: Instance)
	for _, f in ipairs(pai:GetChildren()) do
		if f:GetAttribute("GeradoPeloControlador") then f:Destroy() end
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
		local e = tpl.EstrelaTemplate:Clone()
 e.Name="Estrela"..i
 e.Visible=true
 e.LayoutOrder=i
 e:SetAttribute("GeradoPeloControlador",true)
 e.Parent=info.Estrelas
	end
end

-- ---------- chances reais da area ----------
local function montarChances(banner)
	for _, f in ipairs(blocoChances:GetChildren()) do
		if f:GetAttribute("GeradoPeloControlador") then f:Destroy() end
	end
	local chances=Banners.chances(banner.areaId)

 for i, c in ipairs(chances) do
		local barra = tpl.BarraTemplate:Clone()
		barra.Name = "Chance_" .. c.raridade
		barra.Visible = true
 barra:SetAttribute("GeradoPeloControlador",true)
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
 card:SetAttribute("GeradoPeloControlador",true)
		card.LayoutOrder = i
		card.Nome.Text = d.nome
		card.Raridade.Text = string.upper(d.raridade) .. "  •  PET"
		card.Raridade.TextColor3 = d.cor
		card.Stat.Text = d.stat
		card.Faixa.BackgroundColor3 = d.cor
		card.Thumb.UIStroke.Color = d.cor
		card.Thumb.Inicial.Text = string.upper(string.sub(d.nome, 1, 1))
		card.Thumb.Inicial.TextColor3 = d.cor
		local basePosition=card.Position
 card.Position = basePosition+UDim2.fromOffset(36, 0)
		card.Parent = dropsFrame
		task.delay(0.04 * i, function()
			if card.Parent then
				TweenService:Create(card, INFO, {Position = basePosition}):Play()
			end
		end)
	end
end

-- ---------- preview 3D da maquina ----------
local conexaoGiro: RBXScriptConnection? = nil
local function montarPreview(banner)
	if conexaoGiro then conexaoGiro:Disconnect(); conexaoGiro = nil end
	for _,obj in viewport:GetChildren() do
 if obj:GetAttribute("PreviewGerado") then obj:Destroy() end
 end

	local pasta = ReplicatedStorage:FindFirstChild("PreviewModelos")
	local origem = pasta and pasta:FindFirstChild(banner.gacha)
	if not origem then return end

	local modelo = origem:Clone()
	modelo:SetAttribute("PreviewGerado",true)
 modelo.Parent = viewport

	local cam = Instance.new("Camera")
	cam:SetAttribute("PreviewGerado",true)
 cam.Parent = viewport
	viewport.CurrentCamera = cam

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

conteudo.Topo.Fechar.Activated:Connect(function() definirVisivel(false) end)
conteudo.Topo.FecharDireita.Activated:Connect(function() definirVisivel(false) end)

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
local resultadoSize=painelRes.Size
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
	painelRes.Size = resultadoSize-UDim2.fromOffset(30,0)
	TweenService:Create(painelRes, INFO, {Size = resultadoSize}):Play()
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
 local corBase = botao.BackgroundColor3
	botao.MouseEnter:Connect(function()
		TweenService:Create(botao, INFO, {Size = tamanhoBase + UDim2.fromOffset(10, 4)}):Play()
	end)
	botao.MouseLeave:Connect(function()
		TweenService:Create(botao, INFO, {Size = tamanhoBase}):Play()
	end)
	botao.Activated:Connect(function()
		TweenService:Create(botao, TweenInfo.new(0.08), {BackgroundColor3 = corBase:Lerp(Color3.new(1,1,1),.25)}):Play()
		task.delay(0.1, function()
			TweenService:Create(botao, INFO, {BackgroundColor3 = corBase}):Play()
		end)
		invocar(qtd)
	end)
end
prepararBotao(btn1, 1)
prepararBotao(btn10, 10)



aplicarBanner(1)
definirVisivel(false)

