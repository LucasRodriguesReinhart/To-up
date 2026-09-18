local RS = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TS = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui")
local Config = require(RS:WaitForChild("Config"))
local R = RS:WaitForChild("Remotes")

local dados = nil

-- ================= HUD =================
local tela = Instance.new("ScreenGui")
tela.Name = "MinaHUD"
tela.ResetOnSpawn = false
tela.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
tela.Parent = gui

local function novoFrame(props, parent)
	local f = Instance.new("Frame")
	f.BorderSizePixel = 0
	for k, v in pairs(props) do f[k] = v end
	f.Parent = parent
	return f
end

local function novoTexto(props, parent)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Font = Enum.Font.GothamBold
	t.TextColor3 = Color3.new(1, 1, 1)
	for k, v in pairs(props) do t[k] = v end
	t.Parent = parent
	return t
end

local function canto(inst, raio)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, raio or 8)
	c.Parent = inst
	return c
end

-- painel superior esquerdo
local hud = novoFrame({
	Size = UDim2.fromOffset(250, 96),
	Position = UDim2.fromOffset(16, 16),
	BackgroundColor3 = Color3.fromRGB(24, 24, 30),
	BackgroundTransparency = 0.15,
}, tela)
canto(hud, 12)

do
	local urlMoeda = Config.icone and Config.icone("moeda")
	if urlMoeda then
		local img = Instance.new("ImageLabel")
		img.Name = "IconeMoeda"
		img.Size = UDim2.fromOffset(24, 24)
		img.Position = UDim2.fromOffset(12, 11)
		img.BackgroundTransparency = 1
		img.Image = urlMoeda
		img.ScaleType = Enum.ScaleType.Fit
		img.Parent = hud
	end
end

local lblMoeda = novoTexto({
	Size = UDim2.new(1, -20, 0, 30),
	Position = UDim2.fromOffset((Config.icone and Config.icone("moeda")) and 42 or 12, 8),
	TextXAlignment = Enum.TextXAlignment.Left, TextSize = 22,
	TextColor3 = Color3.fromRGB(255, 205, 70), Text = "0",
}, hud)

local lblMochila = novoTexto({
	Size = UDim2.new(1, -20, 0, 20), Position = UDim2.fromOffset(12, 42),
	TextXAlignment = Enum.TextXAlignment.Left, TextSize = 15,
	Font = Enum.Font.Gotham, Text = "Mochila 0/25",
}, hud)

local barraFundo = novoFrame({
	Size = UDim2.new(1, -24, 0, 8), Position = UDim2.fromOffset(12, 66),
	BackgroundColor3 = Color3.fromRGB(45, 45, 55),
}, hud)
canto(barraFundo, 4)
local barraMochila = novoFrame({
	Size = UDim2.fromScale(0, 1), BackgroundColor3 = Color3.fromRGB(110, 200, 255),
}, barraFundo)
canto(barraMochila, 4)

local lblDano = novoTexto({
	Size = UDim2.new(1, -20, 0, 18), Position = UDim2.fromOffset(12, 78),
	TextXAlignment = Enum.TextXAlignment.Left, TextSize = 13,
	Font = Enum.Font.Gotham, TextColor3 = Color3.fromRGB(180, 180, 195), Text = "Dano 1",
}, hud)

-- ================= AVISOS =================
local avisos = novoFrame({
	Size = UDim2.fromOffset(320, 200),
	Position = UDim2.new(0.5, -160, 0, 90),
	BackgroundTransparency = 1,
}, tela)
local layout = Instance.new("UIListLayout")
layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
layout.VerticalAlignment = Enum.VerticalAlignment.Top
layout.Padding = UDim.new(0, 6)
layout.Parent = avisos

local function avisar(texto, cor)
	local f = novoFrame({
		Size = UDim2.fromOffset(300, 34),
		BackgroundColor3 = Color3.fromRGB(20, 20, 26),
		BackgroundTransparency = 0.1,
	}, avisos)
	canto(f, 8)
	novoTexto({
		Size = UDim2.fromScale(1, 1), TextSize = 16,
		TextColor3 = cor or Color3.new(1, 1, 1), Text = texto,
	}, f)
	task.delay(2.2, function()
		TS:Create(f, TweenInfo.new(0.4), { BackgroundTransparency = 1 }):Play()
		for _, c in ipairs(f:GetChildren()) do
			if c:IsA("TextLabel") then
				TS:Create(c, TweenInfo.new(0.4), { TextTransparency = 1 }):Play()
			end
		end
		task.wait(0.45)
		f:Destroy()
	end)
end

-- ================= ATUALIZAR HUD =================
local function formatar(n)
	if n >= 1e9 then return string.format("%.1fB", n / 1e9) end
	if n >= 1e6 then return string.format("%.1fM", n / 1e6) end
	if n >= 1e3 then return string.format("%.1fK", n / 1e3) end
	return tostring(math.floor(n))
end

local atualizarUI  -- definida mais abaixo (UI do Ignis tambem depende)

local function atualizarHUD()
	if not dados then return end
	lblMoeda.Text = "$ " .. formatar(dados.moeda)
	lblMochila.Text = string.format("Mochila %d/%d", dados.carregado, dados.capacidade)
	local frac = dados.capacidade > 0 and dados.carregado / dados.capacidade or 0
	TS:Create(barraMochila, TweenInfo.new(0.2), { Size = UDim2.fromScale(math.min(frac, 1), 1) }):Play()
	barraMochila.BackgroundColor3 = frac >= 1 and Color3.fromRGB(255, 95, 80) or Color3.fromRGB(110, 200, 255)
	lblDano.Text = string.format("Dano %.1f", dados.dano)
end

-- ================= BARREIRAS =================
-- libera localmente a barreira das areas que o jogador ja desbloqueou
local function atualizarBarreiras()
	if not dados then return end
	local areas = workspace:FindFirstChild("Areas")
	if not areas then return end
	for _, d in ipairs(areas:GetDescendants()) do
		if d:IsA("BasePart") and d.Name == "Barreira" then
			local precisa = d:GetAttribute("LiberaComArea")
			local liberada = precisa and dados.areas[precisa] == true
			d.CanCollide = not liberada
            d.Transparency = liberada and 0.9 or 0.65
		end
	end
end

R.AtualizarDados.OnClientEvent:Connect(function(novo)
	dados = novo
	atualizarHUD()
	atualizarBarreiras()
	if atualizarUI then atualizarUI() end
end)

R.FeedbackMina.OnClientEvent:Connect(function(info)
	if info.tipo == "hat" then
		local r = Config.Raridades[info.raridade]
		avisar((info.novo and "NOVO! " or "") .. info.texto .. " (" .. r.nome .. ")", r.cor)
	elseif info.tipo == "cheia" then
		avisar(info.texto, Color3.fromRGB(255, 110, 90))
	elseif info.tipo == "area" then
		avisar(info.texto, Color3.fromRGB(120, 230, 140))
	elseif info.tipo == "bloqueada" then
		avisar(info.texto, Color3.fromRGB(255, 160, 60))
	end
end)

task.spawn(function()
	local ost = game:GetService("SoundService"):FindFirstChild("OST")
	if ost and not ost.IsPlaying then ost:Play() end
	dados = R.PedirDados:InvokeServer()
	atualizarHUD()
	atualizarBarreiras()
	if atualizarUI then atualizarUI() end
end)

-- ================= BASE DE PAINEIS =================
local VERDE   = Color3.fromRGB(55, 160, 85)
local AZUL    = Color3.fromRGB(55, 120, 200)
local LARANJA = Color3.fromRGB(200, 120, 45)
local ROXO    = Color3.fromRGB(140, 70, 210)

local Sons = RS:WaitForChild("Sons")
local Debris = game:GetService("Debris")
local function tocar(nome)
	local base = Sons:FindFirstChild(nome)
	if not base then return end
	local c = base:Clone()
	c.Parent = game:GetService("SoundService")
	c:Play()
	Debris:AddItem(c, 5)
end

local function chamar(remote, arg)
	local res = remote:InvokeServer(arg)
	if res and res.msg then
		avisar(res.msg, res.ok and Color3.fromRGB(120, 230, 140) or Color3.fromRGB(255, 120, 90))
	end
	tocar(res and res.ok and "Compra" or "Erro")
	return res
end

-- cria um painel com abas. devolve { painel, render, setConteudo }
local function criarPainel(titulo, corTema, largura, altura, abas)
	local p = novoFrame({
		Size = UDim2.fromOffset(largura, altura),
		Position = UDim2.new(0.5, -largura/2, 0.5, -altura/2),
		BackgroundColor3 = Color3.fromRGB(22, 21, 26),
		Visible = false,
	}, tela)
	canto(p, 14)
	local st = Instance.new("UIStroke")
	st.Color = corTema; st.Thickness = 2; st.Transparency = 0.35; st.Parent = p

	novoTexto({ Size = UDim2.new(1, -110, 0, 40), Position = UDim2.fromOffset(20, 10),
		TextXAlignment = Enum.TextXAlignment.Left, TextSize = 23,
		TextColor3 = corTema, Text = titulo }, p)

	local x = Instance.new("TextButton")
	x.Size = UDim2.fromOffset(36, 36); x.Position = UDim2.new(1, -46, 0, 12)
	x.BackgroundColor3 = Color3.fromRGB(150, 45, 45)
	x.Font = Enum.Font.GothamBold; x.TextSize = 20
	x.TextColor3 = Color3.new(1,1,1); x.Text = "X"; x.BorderSizePixel = 0
	x.Parent = p
	canto(x, 8)
	x.MouseButton1Click:Connect(function() p.Visible = false end)

	local temAbas = #abas > 1
	local topoY = temAbas and 98 or 58

	local barra
	local botoes = {}
	if temAbas then
		barra = novoFrame({ Size = UDim2.new(1, -40, 0, 36), Position = UDim2.fromOffset(20, 54),
			BackgroundTransparency = 1 }, p)
		local l = Instance.new("UIListLayout")
		l.FillDirection = Enum.FillDirection.Horizontal; l.Padding = UDim.new(0, 8)
		l.Parent = barra
	end

	local conteudo = Instance.new("ScrollingFrame")
	conteudo.Size = UDim2.new(1, -40, 1, -(topoY + 12))
	conteudo.Position = UDim2.fromOffset(20, topoY)
	conteudo.BackgroundTransparency = 1; conteudo.BorderSizePixel = 0
	conteudo.ScrollBarThickness = 5
	conteudo.CanvasSize = UDim2.new()
	conteudo.AutomaticCanvasSize = Enum.AutomaticSize.Y
	conteudo.Parent = p
	local ll = Instance.new("UIListLayout"); ll.Padding = UDim.new(0, 6); ll.Parent = conteudo

	local ativa = abas[1].nome
	local render

	local function limpar()
		for _, c in ipairs(conteudo:GetChildren()) do
			if not c:IsA("UIListLayout") then c:Destroy() end
		end
	end

	render = function()
		if not dados or not p.Visible then return end
		limpar()
		for _, a in ipairs(abas) do
			if a.nome == ativa then a.fn(conteudo) end
		end
		for nome, b in pairs(botoes) do
			b.BackgroundColor3 = (nome == ativa) and corTema or Color3.fromRGB(42, 40, 48)
		end
	end

	if temAbas then
		local larguraAba = math.floor((largura - 40 - (#abas - 1) * 8) / #abas)
		for _, a in ipairs(abas) do
			local b = Instance.new("TextButton")
			b.Size = UDim2.fromOffset(larguraAba, 34)
			b.BackgroundColor3 = Color3.fromRGB(42, 40, 48)
			b.Font = Enum.Font.GothamBold; b.TextSize = 14
			b.TextColor3 = Color3.new(1,1,1); b.Text = a.nome; b.BorderSizePixel = 0
			b.Parent = barra
			canto(b, 8)
			botoes[a.nome] = b
			b.MouseButton1Click:Connect(function() ativa = a.nome; render() end)
		end
	end

	return { frame = p, render = render, conteudo = conteudo,
		abrir = function() p.Visible = true; ativa = abas[1].nome; render() end }
end

-- linha de lista reutilizavel
local function linha(pai, titulo, sub, textoBotao, corBotao, aoClicar, desativado)
	local f = novoFrame({ Size = UDim2.new(1, -8, 0, 56), BackgroundColor3 = Color3.fromRGB(36, 34, 42) }, pai)
	canto(f, 10)
	novoTexto({ Size = UDim2.new(1, -180, 0, 22), Position = UDim2.fromOffset(14, 8),
		TextXAlignment = Enum.TextXAlignment.Left, TextSize = 16, Text = titulo }, f)
	novoTexto({ Size = UDim2.new(1, -180, 0, 18), Position = UDim2.fromOffset(14, 30),
		TextXAlignment = Enum.TextXAlignment.Left, TextSize = 13, Font = Enum.Font.Gotham,
		TextColor3 = Color3.fromRGB(175, 175, 190), Text = sub }, f)
	if textoBotao then
		local b = Instance.new("TextButton")
		b.Size = UDim2.fromOffset(150, 38); b.Position = UDim2.new(1, -162, 0, 9)
		b.BackgroundColor3 = desativado and Color3.fromRGB(58, 56, 64) or corBotao
		b.Font = Enum.Font.GothamBold; b.TextSize = 14
		b.TextColor3 = desativado and Color3.fromRGB(130,130,140) or Color3.new(1,1,1)
		b.Text = textoBotao; b.AutoButtonColor = not desativado; b.BorderSizePixel = 0
		b.Parent = f
		canto(b, 8)
		if not desativado then b.MouseButton1Click:Connect(aoClicar) end
	end
	return f
end

-- ================= PAINEL DO IGNIS: VENDER + PICARETAS =================
local function abaVender(pai)
	local total, itens = 0, 0
	local ordenado = {}
	for id, qtd in pairs(dados.mochila) do
		local def = Config.infoMinerio(id)
		if def then table.insert(ordenado, { def = def, qtd = qtd }) end
	end
	table.sort(ordenado, function(a, b) return a.def.valor > b.def.valor end)
	for _, it in ipairs(ordenado) do
		total = total + it.def.valor * it.qtd
		itens = itens + it.qtd
		local f = linha(pai, it.def.nome .. "  x" .. it.qtd,
			"$ " .. formatar(it.def.valor) .. " cada", nil)
		f:FindFirstChildOfClass("TextLabel").TextColor3 = it.def.cor
	end
	if itens == 0 then
		linha(pai, "Mochila vazia", "Va minerar antes de voltar aqui", nil)
		return
	end
	local final = math.floor(total * (1 + dados.bonusValor))
	linha(pai, "VENDER TUDO", itens .. " itens" ..
		(dados.bonusValor > 0 and string.format("   +%d%% de hats", dados.bonusValor * 100) or ""),
		"$ " .. formatar(final), VERDE, function()
			local r = chamar(R.Vender)
			if r and r.ok then
				avisar("+$ " .. formatar(r.ganho), Color3.fromRGB(255, 215, 90))
				tocar("Moeda")
			end
		end)
end

local function abaPicaretas(pai)
	local _, iAtual = Config.picaretaPorId(dados.picareta)
	for i, p in ipairs(Config.Picaretas) do
		local possui = i <= (iAtual or 1)
		linha(pai, p.nome, "Dano base " .. formatar(p.dano),
			possui and "EM USO" or ("$ " .. formatar(p.custo)),
			possui and VERDE or AZUL,
			function() chamar(R.ComprarPicareta, p.id) end,
			possui or dados.moeda < p.custo)
	end
end

local painelIgnis = criarPainel("IGNIS, o Ferreiro", Color3.fromRGB(255, 150, 55), 620, 440, {
	{ nome = "Vender", fn = abaVender },
	{ nome = "Picaretas", fn = abaPicaretas },
})

-- ================= PAINEL DA LOJA: MOCHILAS =================
local function abaMochilas(pai)
	local _, iAtual = Config.mochilaPorId(dados.mochilaTier)
	for i, m in ipairs(Config.Mochilas) do
		local possui = i <= (iAtual or 1)
		linha(pai, m.nome, "Capacidade " .. formatar(m.capacidade),
			possui and "EM USO" or ("$ " .. formatar(m.custo)),
			possui and VERDE or LARANJA,
			function() chamar(R.ComprarMochila, m.id) end,
			possui or dados.moeda < m.custo)
	end
end

local painelLoja = criarPainel("LOJA DE MOCHILAS", Color3.fromRGB(255, 190, 70), 620, 440, {
	{ nome = "Mochilas", fn = abaMochilas },
})

-- ================= INVENTARIO: GRADE DE ICONES + DETALHE =================
local painelInv
local selecionado = nil          -- { tipo = "hat"|"pet", id = ... }
local abaInv = "Hats"

-- icone do item. hat com acessorio do catalogo mostra a foto do proprio UGC;
-- o resto continua desenhado com Frames.
local function desenharIcone(pai, tipo, id, cor)
	if tipo == "hat" then
		local assetId = Config.HatAssets and Config.HatAssets[id]
		if assetId and assetId ~= 0 then
			local img = Instance.new("ImageLabel")
			img.Name = "Icone"
			img.Size = UDim2.fromScale(1, 1)
			img.BackgroundTransparency = 1
			img.ScaleType = Enum.ScaleType.Fit
			img.Image = ("rbxthumb://type=Asset&id=%d&w=150&h=150"):format(assetId)
			img.Parent = pai
			return img
		end
	end

	local i = novoFrame({ Name = "Icone", Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1 }, pai)
	local function bloco(w, h, x, y, c, raio)
		local f = novoFrame({ Size = UDim2.fromScale(w, h), Position = UDim2.fromScale(x, y),
			BackgroundColor3 = c }, i)
		canto(f, raio or 4)
		return f
	end
	local escuro = cor:Lerp(Color3.new(0,0,0), 0.35)

	if tipo == "hat" then
		if string.find(id, "bandana") or string.find(id, "faixa") then
			bloco(0.72, 0.16, 0.14, 0.42, cor)
			bloco(0.16, 0.30, 0.66, 0.56, escuro)
		elseif string.find(id, "elmo") or string.find(id, "capacete") then
			bloco(0.56, 0.42, 0.22, 0.24, cor, 10)
			bloco(0.62, 0.12, 0.19, 0.60, escuro)
			bloco(0.10, 0.26, 0.45, 0.16, escuro)
		elseif string.find(id, "capuz") or string.find(id, "gorro") then
			bloco(0.52, 0.46, 0.24, 0.22, cor, 12)
			bloco(0.30, 0.20, 0.35, 0.56, escuro, 6)
		elseif string.find(id, "chapeu") then
			bloco(0.80, 0.12, 0.10, 0.56, cor)
			bloco(0.44, 0.34, 0.28, 0.26, cor, 8)
			bloco(0.44, 0.08, 0.28, 0.52, escuro)
		elseif string.find(id, "coroa") or string.find(id, "halo") or string.find(id, "aura") then
			bloco(0.62, 0.14, 0.19, 0.52, cor)
			for k = 0, 2 do bloco(0.14, 0.26, 0.20 + k * 0.24, 0.30, cor) end
		elseif string.find(id, "mascara") then
			bloco(0.54, 0.50, 0.23, 0.24, cor, 12)
			bloco(0.12, 0.08, 0.31, 0.38, escuro, 3)
			bloco(0.12, 0.08, 0.57, 0.38, escuro, 3)
		else
			bloco(0.52, 0.44, 0.24, 0.28, cor, 10)
		end
	else -- pet
		bloco(0.44, 0.34, 0.28, 0.42, cor, 10)          -- corpo
		bloco(0.30, 0.28, 0.35, 0.20, cor, 10)          -- cabeca
		bloco(0.09, 0.14, 0.33, 0.10, escuro, 3)        -- orelha
		bloco(0.09, 0.14, 0.58, 0.10, escuro, 3)
		bloco(0.08, 0.08, 0.38, 0.28, escuro, 3)        -- olhos
		bloco(0.08, 0.08, 0.54, 0.28, escuro, 3)
		bloco(0.14, 0.10, 0.66, 0.50, escuro, 4)        -- cauda
	end
	return i
end

painelInv = (function()
	local p = novoFrame({ Name = "PainelInventario",
		Size = UDim2.fromOffset(720, 470),
		Position = UDim2.new(0.5, -360, 0.5, -235),
		BackgroundColor3 = Color3.fromRGB(22, 21, 30),
		Visible = false }, tela)
	canto(p, 16)
	local st = Instance.new("UIStroke")
	st.Color = Color3.fromRGB(120, 190, 255); st.Thickness = 3; st.Parent = p

	novoTexto({ Size = UDim2.fromOffset(240, 36), Position = UDim2.fromOffset(20, 12),
		TextXAlignment = Enum.TextXAlignment.Left, TextSize = 22,
		TextColor3 = Color3.fromRGB(140, 200, 255), Text = "INVENTARIO" }, p)

	local x = Instance.new("TextButton")
	x.Size = UDim2.fromOffset(34, 34); x.Position = UDim2.new(1, -46, 0, 14)
	x.BackgroundColor3 = Color3.fromRGB(150, 45, 45)
	x.Font = Enum.Font.GothamBold; x.TextSize = 19
	x.TextColor3 = Color3.new(1,1,1); x.Text = "X"; x.BorderSizePixel = 0
	x.Parent = p
	canto(x, 8)
	x.MouseButton1Click:Connect(function() p.Visible = false end)

	-- abas Hats / Pets
	local abas = {}
	for k, nome in ipairs({"Hats", "Pets"}) do
		local b = Instance.new("TextButton")
		b.Name = "Aba" .. nome
		b.Size = UDim2.fromOffset(96, 32)
		b.Position = UDim2.fromOffset(250 + (k-1) * 104, 14)
		b.BackgroundColor3 = Color3.fromRGB(44, 42, 54)
		b.Font = Enum.Font.GothamBold; b.TextSize = 14
		b.TextColor3 = Color3.new(1,1,1); b.Text = nome; b.BorderSizePixel = 0
		b.Parent = p
		canto(b, 8)
		abas[nome] = b
	end

	-- ---------- PAINEL DE DETALHE (esquerda) ----------
	local det = novoFrame({ Name = "Detalhe",
		Size = UDim2.fromOffset(238, 386), Position = UDim2.fromOffset(20, 60),
		BackgroundColor3 = Color3.fromRGB(16, 15, 23) }, p)
	canto(det, 12)
	local detStroke = Instance.new("UIStroke")
	detStroke.Color = Color3.fromRGB(60, 58, 74); detStroke.Thickness = 2
	detStroke.Parent = det

	local vazio = novoTexto({ Name = "Vazio", Size = UDim2.fromScale(1, 1),
		TextSize = 15, Font = Enum.Font.Gotham, TextWrapped = true,
		TextColor3 = Color3.fromRGB(120, 120, 138),
		Text = "Selecione um item\nna grade ao lado" }, det)

	local caixaIcone = novoFrame({ Name = "CaixaIcone", Visible = false,
		Size = UDim2.fromOffset(120, 120), Position = UDim2.fromOffset(59, 20),
		BackgroundColor3 = Color3.fromRGB(28, 27, 38) }, det)
	canto(caixaIcone, 14)

	local detNome = novoTexto({ Name = "Nome", Visible = false,
		Size = UDim2.new(1, -20, 0, 26), Position = UDim2.fromOffset(10, 150),
		TextSize = 18, TextWrapped = true, Text = "" }, det)
	local detRar = novoTexto({ Name = "Raridade", Visible = false,
		Size = UDim2.new(1, -20, 0, 20), Position = UDim2.fromOffset(10, 176),
		TextSize = 14, Font = Enum.Font.Gotham, Text = "" }, det)

	local stats = novoFrame({ Name = "Stats", Visible = false,
		Size = UDim2.new(1, -24, 0, 92), Position = UDim2.fromOffset(12, 202),
		BackgroundTransparency = 1 }, det)
	local sl = Instance.new("UIListLayout"); sl.Padding = UDim.new(0, 4); sl.Parent = stats

	local function linhaStat(rotulo, valor, cor)
		local f = novoFrame({ Size = UDim2.new(1, 0, 0, 22),
			BackgroundColor3 = Color3.fromRGB(30, 29, 40) }, stats)
		canto(f, 6)
		novoTexto({ Size = UDim2.new(0.5, 0, 1, 0), Position = UDim2.fromOffset(10, 0),
			TextXAlignment = Enum.TextXAlignment.Left, TextSize = 13, Font = Enum.Font.Gotham,
			TextColor3 = Color3.fromRGB(160, 160, 178), Text = rotulo }, f)
		novoTexto({ Size = UDim2.new(0.5, -12, 1, 0), Position = UDim2.new(0.5, 0, 0, 0),
			TextXAlignment = Enum.TextXAlignment.Right, TextSize = 14,
			TextColor3 = cor or Color3.new(1,1,1), Text = valor }, f)
	end

	local btnEquipar = Instance.new("TextButton")
	btnEquipar.Name = "BotaoEquipar"; btnEquipar.Visible = false
	btnEquipar.Size = UDim2.new(1, -24, 0, 36); btnEquipar.Position = UDim2.fromOffset(12, 300)
	btnEquipar.Font = Enum.Font.GothamBold; btnEquipar.TextSize = 14
	btnEquipar.TextColor3 = Color3.new(1,1,1); btnEquipar.BorderSizePixel = 0
	btnEquipar.Parent = det
	canto(btnEquipar, 8)

	local btnFundir = Instance.new("TextButton")
	btnFundir.Name = "BotaoFundir"; btnFundir.Visible = false
	btnFundir.Size = UDim2.new(1, -24, 0, 36); btnFundir.Position = UDim2.fromOffset(12, 342)
	btnFundir.Font = Enum.Font.GothamBold; btnFundir.TextSize = 13
	btnFundir.TextColor3 = Color3.new(1,1,1); btnFundir.BorderSizePixel = 0
	btnFundir.Parent = det
	canto(btnFundir, 8)

	-- ---------- GRADE (direita) ----------
	local topo = novoFrame({ Name = "Resumo",
		Size = UDim2.fromOffset(422, 44), Position = UDim2.fromOffset(276, 60),
		BackgroundColor3 = Color3.fromRGB(30, 29, 40) }, p)
	canto(topo, 10)
	local resumoTxt = novoTexto({ Name = "Texto", Size = UDim2.new(1, -190, 1, 0),
		Position = UDim2.fromOffset(12, 0), TextXAlignment = Enum.TextXAlignment.Left,
		TextSize = 14, Font = Enum.Font.Gotham, Text = "" }, topo)

	local btnMelhores = Instance.new("TextButton")
	btnMelhores.Size = UDim2.fromOffset(84, 28); btnMelhores.Position = UDim2.new(1, -180, 0, 8)
	btnMelhores.BackgroundColor3 = Color3.fromRGB(55, 160, 85)
	btnMelhores.Font = Enum.Font.GothamBold; btnMelhores.TextSize = 12
	btnMelhores.TextColor3 = Color3.new(1,1,1); btnMelhores.Text = "MELHORES"
	btnMelhores.BorderSizePixel = 0; btnMelhores.Parent = topo
	canto(btnMelhores, 7)

	local btnLimpar = Instance.new("TextButton")
	btnLimpar.Size = UDim2.fromOffset(84, 28); btnLimpar.Position = UDim2.new(1, -92, 0, 8)
	btnLimpar.BackgroundColor3 = Color3.fromRGB(120, 60, 60)
	btnLimpar.Font = Enum.Font.GothamBold; btnLimpar.TextSize = 12
	btnLimpar.TextColor3 = Color3.new(1,1,1); btnLimpar.Text = "LIMPAR"
	btnLimpar.BorderSizePixel = 0; btnLimpar.Parent = topo
	canto(btnLimpar, 7)

	local grade = Instance.new("ScrollingFrame")
	grade.Name = "Grade"
	grade.Size = UDim2.fromOffset(422, 336); grade.Position = UDim2.fromOffset(276, 110)
	grade.BackgroundTransparency = 1; grade.BorderSizePixel = 0
	grade.ScrollBarThickness = 5
	grade.CanvasSize = UDim2.new(); grade.AutomaticCanvasSize = Enum.AutomaticSize.Y
	grade.Parent = p
	local gl = Instance.new("UIGridLayout")
	gl.CellSize = UDim2.fromOffset(74, 74); gl.CellPadding = UDim2.fromOffset(8, 8)
	gl.Parent = grade

	local render

	local function mostrarDetalhe()
		local temSel = selecionado ~= nil
		vazio.Visible = not temSel
		caixaIcone.Visible = temSel
		detNome.Visible = temSel
		detRar.Visible = temSel
		stats.Visible = temSel
		btnEquipar.Visible = temSel
		btnFundir.Visible = temSel
		for _, c in ipairs(stats:GetChildren()) do
			if not c:IsA("UIListLayout") then c:Destroy() end
		end
		for _, c in ipairs(caixaIcone:GetChildren()) do
			if c.Name == "Icone" then c:Destroy() end
		end
		if not temSel then return end

		local ehHat = selecionado.tipo == "hat"
		local def = ehHat and Config.hatPorId(selecionado.id) or Config.petPorId(selecionado.id)
		local posse = ehHat and dados.hats[selecionado.id] or dados.pets[selecionado.id]
		if not def or not posse then selecionado = nil; return mostrarDetalhe() end

		local r = Config.Raridades[def.raridade]
		detStroke.Color = r.cor
		desenharIcone(caixaIcone, selecionado.tipo, selecionado.id, r.cor)
		detNome.Text = def.nome
		detNome.TextColor3 = r.cor
		detRar.Text = r.nome .. "   x" .. posse.qtd
		detRar.TextColor3 = r.cor

		linhaStat("Nivel", posse.nivel .. " / " .. (ehHat and Config.HAT_NIVEL_MAX or Config.PET_NIVEL_MAX))
		if ehHat then
			linhaStat("Dano", "+" .. formatar(Config.hatDanoNoNivel(def.dano, posse.nivel)),
				Color3.fromRGB(255, 200, 90))
			if def.extra then
				linhaStat(def.extra, string.format("+%d%%",
					Config.hatExtraNoNivel(def.extraValor, posse.nivel) * 100), Color3.fromRGB(140, 210, 255))
			end
		else
			linhaStat("Velocidade", "+" .. string.format("%.1f",
				Config.petVelocidadeNoNivel(def.velocidade, posse.nivel)), Color3.fromRGB(140, 230, 160))
			if def.extra then
				local v = Config.petExtraNoNivel(def.extraValor, posse.nivel)
				linhaStat(def.extra, def.extra == "dano" and ("+" .. formatar(v))
					or string.format("+%d%%", v * 100), Color3.fromRGB(140, 210, 255))
			end
		end

		local equipados = ehHat and dados.equipados or dados.petsEquipados
		local eq = false
		for _, e in ipairs(equipados) do if e == selecionado.id then eq = true end end

		btnEquipar.Text = eq and "DESEQUIPAR" or "EQUIPAR"
		btnEquipar.BackgroundColor3 = eq and Color3.fromRGB(150, 60, 60) or Color3.fromRGB(55, 120, 200)

		local nivelMax = ehHat and Config.HAT_NIVEL_MAX or Config.PET_NIVEL_MAX
		if posse.nivel >= nivelMax then
			btnFundir.Text = "NIVEL MAXIMO"
			btnFundir.BackgroundColor3 = Color3.fromRGB(52, 50, 62)
			btnFundir.AutoButtonColor = false
		else
			local c = ehHat and Config.custoFusao(def.raridade, posse.nivel)
				or Config.custoFusaoPet(def.raridade, posse.nivel)
			local pode = (posse.qtd - 1) >= c.duplicatas and dados.moeda >= c.moeda
			btnFundir.Text = "FUNDIR   $" .. formatar(c.moeda) .. "  +  " .. c.duplicatas .. "x"
			btnFundir.BackgroundColor3 = pode and Color3.fromRGB(140, 70, 210) or Color3.fromRGB(52, 50, 62)
			btnFundir.AutoButtonColor = pode
		end
	end

	btnEquipar.MouseButton1Click:Connect(function()
		if not selecionado then return end
		chamar(selecionado.tipo == "hat" and R.EquiparHat or R.EquiparPet, selecionado.id)
	end)
	btnFundir.MouseButton1Click:Connect(function()
		if not selecionado then return end
		chamar(selecionado.tipo == "hat" and R.FundirHat or R.FundirPet, selecionado.id)
	end)
	btnMelhores.MouseButton1Click:Connect(function()
		chamar(abaInv == "Hats" and R.EquiparMelhores or R.EquiparMelhoresPets)
	end)
	btnLimpar.MouseButton1Click:Connect(function()
		chamar(abaInv == "Hats" and R.DesequiparTodos or R.DesequiparPets)
	end)

	-- celula: so o icone, borda pela raridade, marcador de equipado e quantidade
	local function celula(tipo, id, def, posse, eq)
		local r = Config.Raridades[def.raridade]
		local b = Instance.new("TextButton")
		b.Name = id
		b.Size = UDim2.fromOffset(74, 74)
		b.BackgroundColor3 = Color3.fromRGB(30, 29, 40)
		b.Text = ""; b.BorderSizePixel = 0
		b.Parent = grade
		canto(b, 10)

		local st2 = Instance.new("UIStroke")
		st2.Color = r.cor
		local sel = selecionado and selecionado.id == id and selecionado.tipo == tipo
		st2.Thickness = sel and 4 or (eq and 2.5 or 1.5)
		st2.Transparency = sel and 0 or (eq and 0.1 or 0.5)
		st2.Parent = b

		local caixa = novoFrame({ Size = UDim2.fromOffset(52, 52), Position = UDim2.fromOffset(11, 8),
			BackgroundTransparency = 1 }, b)
		desenharIcone(caixa, tipo, id, r.cor)

		if posse.qtd > 1 then
			novoTexto({ Size = UDim2.fromOffset(30, 14), Position = UDim2.new(1, -34, 1, -16),
				TextXAlignment = Enum.TextXAlignment.Right, TextSize = 12,
				TextColor3 = Color3.fromRGB(170, 170, 188), Text = "x" .. posse.qtd }, b)
		end
		if posse.nivel > 1 then
			novoTexto({ Size = UDim2.fromOffset(28, 14), Position = UDim2.fromOffset(5, 1),
				TextXAlignment = Enum.TextXAlignment.Left, TextSize = 11,
				TextColor3 = Color3.fromRGB(255, 210, 110), Text = "Nv" .. posse.nivel }, b)
		end
		if eq then
			local tag = novoFrame({ Size = UDim2.fromOffset(20, 14),
				Position = UDim2.fromOffset(5, 56), BackgroundColor3 = Color3.fromRGB(55, 175, 85) }, b)
			canto(tag, 4)
			novoTexto({ Size = UDim2.fromScale(1,1), TextSize = 10, Text = "EQ" }, tag)
		end

		b.MouseButton1Click:Connect(function()
			selecionado = { tipo = tipo, id = id }
			render()
		end)
	end

	render = function()
		if not dados or not p.Visible then return end
		for _, c in ipairs(grade:GetChildren()) do
			if not c:IsA("UIGridLayout") then c:Destroy() end
		end
		for nome, b in pairs(abas) do
			b.BackgroundColor3 = (nome == abaInv) and Color3.fromRGB(80, 150, 230) or Color3.fromRGB(44, 42, 54)
		end

		local ehHat = abaInv == "Hats"
		local colecao = ehHat and dados.hats or dados.pets
		local equipadosLista = ehHat and dados.equipados or dados.petsEquipados
		local equipados = {}
		for _, id in ipairs(equipadosLista) do equipados[id] = true end

		resumoTxt.Text = ehHat
			and string.format("Hats %d/%d    Equipados %d/%d    Dano +%s",
				dados.totalHats, Config.INVENTARIO_MAX, #dados.equipados, dados.slots, formatar(dados.danoHats))
			or string.format("Pets %d/%d    Equipados %d/%d    Velocidade %.1f",
				dados.totalPets, Config.PET_INVENTARIO_MAX, #dados.petsEquipados, dados.slotsPets, dados.velocidade)

		local lista = {}
		for id, posse in pairs(colecao) do
			local def = ehHat and Config.hatPorId(id) or Config.petPorId(id)
			if def then table.insert(lista, { id = id, def = def, posse = posse, eq = equipados[id] == true }) end
		end
		table.sort(lista, function(a, b)
			if a.eq ~= b.eq then return a.eq end
			local ra, rb = Config.Raridades[a.def.raridade].ordem, Config.Raridades[b.def.raridade].ordem
			if ra ~= rb then return ra > rb end
			return (a.posse.nivel or 1) > (b.posse.nivel or 1)
		end)

		if #lista == 0 then
			local aviso = novoFrame({ Size = UDim2.fromOffset(74, 74), BackgroundTransparency = 1 }, grade)
			novoTexto({ Size = UDim2.fromScale(1,1), TextSize = 12, TextWrapped = true,
				TextColor3 = Color3.fromRGB(120,120,138),
				Text = ehHat and "sem hats" or "sem pets" }, aviso)
		end
		for _, it in ipairs(lista) do
			celula(ehHat and "hat" or "pet", it.id, it.def, it.posse, it.eq)
		end

		mostrarDetalhe()
	end

	for nome, b in pairs(abas) do
		b.MouseButton1Click:Connect(function()
			abaInv = nome
			selecionado = nil
			render()
		end)
	end

	return { frame = p, render = render,
		abrir = function() p.Visible = true; render() end }
end)()

-- ---------- COLUNA DE BOTOES DO HUD ----------
-- tudo feito com Frame + UICorner + UIStroke, editavel no Explorer.
-- caminho: PlayerGui > MinaHUD > MenuLateral > Botao_<id>
local menu = novoFrame({
	Name = "MenuLateral",
	Size = UDim2.fromOffset(84, 300),
	Position = UDim2.fromOffset(16, 130),
	BackgroundTransparency = 1,
}, tela)
local menuLayout = Instance.new("UIListLayout")
menuLayout.Padding = UDim.new(0, 10)
menuLayout.SortOrder = Enum.SortOrder.LayoutOrder
menuLayout.Parent = menu

-- desenha um icone simples com Frames, sem depender de imagem
-- mapa botao -> chave de icone na Config
local CHAVE_ICONE = {
	loja    = "loja",      -- barraca SHOP
	chapeu  = "mochila",   -- a imagem de mochila e o icone do Inventario
	pet     = "pets",
	config  = "config",    -- engrenagem, botao Som
	mochila = "mochila",
	mapa    = "areas",
	martelo = "loja",
}

local function icone(pai, tipo, cor)
	local i = novoFrame({ Name = "Icone", Size = UDim2.fromOffset(38, 38),
		Position = UDim2.new(0.5, -19, 0.5, -23), BackgroundTransparency = 1 }, pai)

	-- se voce subiu a imagem e colou o ID na Config, usa ela
	local chave = CHAVE_ICONE[tipo]
	local url = chave and Config.icone and Config.icone(chave)
	if url then
		i.Size = UDim2.fromOffset(46, 46)
		i.Position = UDim2.new(0.5, -23, 0.5, -27)
		local img = Instance.new("ImageLabel")
		img.Name = "Imagem"
		img.Size = UDim2.fromScale(1, 1)
		img.BackgroundTransparency = 1
		img.Image = url
		img.ScaleType = Enum.ScaleType.Fit
		img.Parent = i
		return i
	end
	if tipo == "mochila" then
		local corpo = novoFrame({ Size = UDim2.fromOffset(30, 24), Position = UDim2.fromOffset(4, 12),
			BackgroundColor3 = cor }, i)
		canto(corpo, 6)
		local alca = novoFrame({ Size = UDim2.fromOffset(16, 12), Position = UDim2.fromOffset(11, 4),
			BackgroundColor3 = cor }, i)
		canto(alca, 6)
		local bolso = novoFrame({ Size = UDim2.fromOffset(16, 9), Position = UDim2.fromOffset(11, 22),
			BackgroundColor3 = Color3.new(1,1,1), BackgroundTransparency = 0.55 }, i)
		canto(bolso, 3)
	elseif tipo == "martelo" then
		local cabeca = novoFrame({ Size = UDim2.fromOffset(30, 12), Position = UDim2.fromOffset(4, 6),
			BackgroundColor3 = cor }, i)
		canto(cabeca, 4)
		local cabo = novoFrame({ Size = UDim2.fromOffset(7, 22), Position = UDim2.fromOffset(15, 16),
			BackgroundColor3 = Color3.fromRGB(150, 100, 58) }, i)
		canto(cabo, 3)
	elseif tipo == "chapeu" then
		local aba = novoFrame({ Size = UDim2.fromOffset(36, 8), Position = UDim2.fromOffset(1, 24),
			BackgroundColor3 = cor }, i)
		canto(aba, 4)
		local copa = novoFrame({ Size = UDim2.fromOffset(22, 20), Position = UDim2.fromOffset(8, 6),
			BackgroundColor3 = cor }, i)
		canto(copa, 6)
		local faixa = novoFrame({ Size = UDim2.fromOffset(22, 5), Position = UDim2.fromOffset(8, 20),
			BackgroundColor3 = Color3.new(0,0,0), BackgroundTransparency = 0.55 }, i)
	elseif tipo == "pet" then
		local corpo = novoFrame({ Size = UDim2.fromOffset(24, 16), Position = UDim2.fromOffset(7, 18),
			BackgroundColor3 = cor }, i)
		canto(corpo, 7)
		local cab = novoFrame({ Size = UDim2.fromOffset(18, 16), Position = UDim2.fromOffset(10, 4),
			BackgroundColor3 = cor }, i)
		canto(cab, 7)
		for _, dx in ipairs({9, 22}) do
			local or_ = novoFrame({ Size = UDim2.fromOffset(6, 8), Position = UDim2.fromOffset(dx, 1),
				BackgroundColor3 = cor }, i)
			canto(or_, 2)
		end
	elseif tipo == "mapa" then
		local base = novoFrame({ Size = UDim2.fromOffset(34, 30), Position = UDim2.fromOffset(2, 5),
			BackgroundColor3 = cor }, i)
		canto(base, 6)
		for k = 0, 2 do
			local linha = novoFrame({ Size = UDim2.fromOffset(24, 4),
				Position = UDim2.fromOffset(7, 11 + k * 7),
				BackgroundColor3 = Color3.new(1,1,1), BackgroundTransparency = 0.5 }, i)
			canto(linha, 2)
		end
	end
	return i
end

local function botaoHUD(id, rotulo, corBase, corBorda, tipoIcone, ordem, aoClicar)
	local b = Instance.new("TextButton")
	b.Name = "Botao_" .. id
	b.Size = UDim2.fromOffset(74, 74)
	b.LayoutOrder = ordem
	b.BackgroundColor3 = corBase
	b.Text = ""
	b.BorderSizePixel = 0
	b.AutoButtonColor = false
	b.Parent = menu
	canto(b, 14)

	local borda = Instance.new("UIStroke")
	borda.Name = "Borda"
	borda.Color = corBorda
	borda.Thickness = 3
	borda.Parent = b

	-- brilho no topo, da o volume do estilo simulator
	local brilho = novoFrame({ Name = "Brilho", Size = UDim2.new(1, -10, 0, 22),
		Position = UDim2.fromOffset(5, 5),
		BackgroundColor3 = Color3.new(1,1,1), BackgroundTransparency = 0.78 }, b)
	canto(brilho, 10)

	icone(b, tipoIcone, Color3.new(1, 1, 1))

	local txt = novoTexto({ Name = "Rotulo",
		Size = UDim2.new(1, 0, 0, 18), Position = UDim2.new(0, 0, 1, -21),
		TextSize = 13, Text = rotulo }, b)
	txt.TextStrokeTransparency = 0
	txt.TextStrokeColor3 = Color3.fromRGB(26, 26, 34)

	b.MouseEnter:Connect(function() borda.Thickness = 4 end)
	b.MouseLeave:Connect(function() borda.Thickness = 3 end)
	b.MouseButton1Click:Connect(aoClicar)
	return b
end

local function alternar(painel)
	if painel.frame.Visible then
		painel.frame.Visible = false
	else
		painelIgnis.frame.Visible = false
		painelLoja.frame.Visible = false
		painelInv.frame.Visible = false
		painel.abrir()
	end
end

local btnInv = botaoHUD("Inventario", "HATS", Color3.fromRGB(58, 128, 214),
	Color3.fromRGB(150, 205, 255), "chapeu", 1, function()
		abaInv = "Hats"
		selecionado = nil
		alternar(painelInv)
	end)

botaoHUD("Pets", "PETS", Color3.fromRGB(150, 90, 210),
	Color3.fromRGB(215, 170, 255), "pet", 4, function()
		abaInv = "Pets"
		selecionado = nil
		alternar(painelInv)
	end)

botaoHUD("Areas", "AREAS", Color3.fromRGB(72, 168, 92),
	Color3.fromRGB(150, 240, 175), "mapa", 5, function()
		local n, total = 0, #Config.Areas
		for _ in pairs(dados.areas) do n += 1 end
		avisar("Areas liberadas: " .. n .. "/" .. total, Color3.fromRGB(150, 240, 175))
	end)

-- tecla B tambem abre
game:GetService("UserInputService").InputBegan:Connect(function(input, digitando)
	if digitando then return end
	if input.KeyCode == Enum.KeyCode.B then
		if painelInv.frame.Visible then
			painelInv.frame.Visible = false
		else
			painelIgnis.frame.Visible = false
			painelLoja.frame.Visible = false
			painelInv.abrir()
		end
	end
end)


-- ================= GACHA =================
local gachaArea = 1

local painelGacha = novoFrame({
	Name = "PainelGacha",
	Size = UDim2.fromOffset(460, 480),
	Position = UDim2.new(0.5, -230, 0.5, -240),
	BackgroundColor3 = Color3.fromRGB(24, 22, 34),
	Visible = false,
}, tela)
canto(painelGacha, 16)
local bordaG = Instance.new("UIStroke")
bordaG.Color = Color3.fromRGB(170, 130, 255); bordaG.Thickness = 3
bordaG.Parent = painelGacha

local tituloG = novoTexto({ Name = "Titulo",
	Size = UDim2.new(1, -80, 0, 38), Position = UDim2.fromOffset(20, 12),
	TextXAlignment = Enum.TextXAlignment.Left, TextSize = 22,
	TextColor3 = Color3.fromRGB(190, 155, 255), Text = "OVOS" }, painelGacha)

local fecharG = Instance.new("TextButton")
fecharG.Size = UDim2.fromOffset(34, 34); fecharG.Position = UDim2.new(1, -46, 0, 14)
fecharG.BackgroundColor3 = Color3.fromRGB(150, 45, 45)
fecharG.Font = Enum.Font.GothamBold; fecharG.TextSize = 19
fecharG.TextColor3 = Color3.new(1,1,1); fecharG.Text = "X"; fecharG.BorderSizePixel = 0
fecharG.Parent = painelGacha
canto(fecharG, 8)
fecharG.MouseButton1Click:Connect(function() painelGacha.Visible = false end)

-- palco do ovo
local palco = novoFrame({ Name = "Palco",
	Size = UDim2.new(1, -40, 0, 150), Position = UDim2.fromOffset(20, 56),
	BackgroundColor3 = Color3.fromRGB(16, 15, 24) }, painelGacha)
canto(palco, 12)

local ovo = novoFrame({ Name = "Ovo",
	Size = UDim2.fromOffset(74, 92), Position = UDim2.new(0.5, -37, 0.5, -46),
	BackgroundColor3 = Color3.fromRGB(210, 210, 225) }, palco)
local cantoOvo = Instance.new("UICorner")
cantoOvo.CornerRadius = UDim.new(0.5, 0)
cantoOvo.Parent = ovo
local faixaOvo = novoFrame({ Name = "Faixa",
	Size = UDim2.new(1, 0, 0, 12), Position = UDim2.new(0, 0, 0.52, 0),
	BackgroundColor3 = Color3.fromRGB(150, 150, 170) }, ovo)

local resultado = novoTexto({ Name = "Resultado",
	Size = UDim2.new(1, -20, 0, 44), Position = UDim2.new(0, 10, 1, -50),
	TextSize = 19, Text = "" }, palco)

-- lista de chances
local chances = Instance.new("ScrollingFrame")
chances.Name = "Chances"
chances.Size = UDim2.new(1, -40, 1, -292)
chances.Position = UDim2.fromOffset(20, 216)
chances.BackgroundTransparency = 1; chances.BorderSizePixel = 0
chances.ScrollBarThickness = 4
chances.CanvasSize = UDim2.new()
chances.AutomaticCanvasSize = Enum.AutomaticSize.Y
chances.Parent = painelGacha
local lc = Instance.new("UIListLayout"); lc.Padding = UDim.new(0, 4); lc.Parent = chances

local btnRolar = Instance.new("TextButton")
btnRolar.Name = "BotaoRolar"
btnRolar.Size = UDim2.new(1, -40, 0, 52)
btnRolar.Position = UDim2.new(0, 20, 1, -66)
btnRolar.BackgroundColor3 = Color3.fromRGB(130, 70, 210)
btnRolar.Font = Enum.Font.FredokaOne; btnRolar.TextSize = 20
btnRolar.TextColor3 = Color3.new(1,1,1); btnRolar.Text = "ABRIR"
btnRolar.BorderSizePixel = 0
btnRolar.Parent = painelGacha
canto(btnRolar, 12)

local rolando = false

local function desenharChances()
	for _, c in ipairs(chances:GetChildren()) do
		if not c:IsA("UIListLayout") then c:Destroy() end
	end
	local lista = Config.chancesGacha(gachaArea)
	if not lista then return end
	for _, it in ipairs(lista) do
		local f = novoFrame({ Size = UDim2.new(1, -6, 0, 26),
			BackgroundColor3 = Color3.fromRGB(34, 32, 46) }, chances)
		canto(f, 6)
		novoTexto({ Size = UDim2.new(0.6, 0, 1, 0), Position = UDim2.fromOffset(12, 0),
			TextXAlignment = Enum.TextXAlignment.Left, TextSize = 14,
			TextColor3 = it.cor, Text = it.nome }, f)
		novoTexto({ Size = UDim2.new(0.35, -12, 1, 0), Position = UDim2.new(0.62, 0, 0, 0),
			TextXAlignment = Enum.TextXAlignment.Right, TextSize = 14, Font = Enum.Font.Gotham,
			TextColor3 = Color3.fromRGB(200, 200, 215),
			Text = string.format("%.2f%%", it.pct) }, f)
	end
end

local function atualizarGacha()
	if not dados or not painelGacha.Visible then return end
	local g = Config.Gachas[gachaArea]
	local area = Config.areaPorId(gachaArea)
	if not g or not area then return end
	tituloG.Text = "OVOS - " .. string.upper(area.nome)
	local tema = Config.Temas[area.tema]
	bordaG.Color = tema.cor
	tituloG.TextColor3 = tema.cor
	local podePagar = dados.moeda >= g.custo
	btnRolar.Text = "ABRIR   $" .. formatar(g.custo)
	btnRolar.BackgroundColor3 = podePagar and Color3.fromRGB(130, 70, 210) or Color3.fromRGB(62, 58, 74)
	btnRolar.AutoButtonColor = podePagar
	desenharChances()
end

local function animarAbertura(res)
	rolando = true
	tocar("Ovo")
	btnRolar.Text = "..."
	btnRolar.AutoButtonColor = false
	resultado.Text = ""

	-- chacoalha
	local base = UDim2.new(0.5, -37, 0.5, -46)
	for i = 1, 16 do
		local dx = (i % 2 == 0) and 7 or -7
		ovo.Position = base + UDim2.fromOffset(dx, 0)
		ovo.Rotation = dx * 0.7
		task.wait(0.05)
	end
	ovo.Position = base
	ovo.Rotation = 0

	local r = Config.Raridades[res.raridade]
	ovo.BackgroundColor3 = r.cor
	faixaOvo.BackgroundColor3 = r.cor:Lerp(Color3.new(0,0,0), 0.3)

	-- estoura
	TS:Create(ovo, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Size = UDim2.fromOffset(112, 138), BackgroundTransparency = 0.35 }):Play()
	task.wait(0.3)
	TS:Create(ovo, TweenInfo.new(0.3), { Size = UDim2.fromOffset(74, 92), BackgroundTransparency = 0 }):Play()

	tocar("Premio")
	resultado.TextColor3 = r.cor
	resultado.Text = (res.novo and "NOVO! " or "") .. res.nome
		.. "  (" .. r.nome .. ")  +" .. string.format("%.1f", res.velocidade or 0) .. " vel"
	avisar((res.novo and "NOVO! " or "") .. res.nome, r.cor)

	rolando = false
	atualizarGacha()
end

btnRolar.MouseButton1Click:Connect(function()
	if rolando then return end
	local g = Config.Gachas[gachaArea]
	if not g or not dados or dados.moeda < g.custo then
		avisar("Moeda insuficiente", Color3.fromRGB(255, 120, 90))
		return
	end
	rolando = true
	local res = R.RolarGacha:InvokeServer(gachaArea)
	rolando = false
	if res and res.ok then
		animarAbertura(res)
	else
		if res and res.msg then avisar(res.msg, Color3.fromRGB(255, 120, 90)) end
		atualizarGacha()
	end
end)

-- o painel antigo de OVOS foi aposentado: quem abre agora e a SummonGui
-- (StarterGui.SummonGui.SummonController escuta o mesmo AbrirGacha).
-- aqui so fechamos os outros paineis pra nao ficar tela sobre tela.
R.AbrirGacha.OnClientEvent:Connect(function(areaId)
	gachaArea = areaId or 1
	painelIgnis.frame.Visible = false
	painelLoja.frame.Visible = false
	painelInv.frame.Visible = false
	painelGacha.Visible = false
end)


-- ================= HOTBAR DO JOGADOR =================
-- 8 slots no rodape. slot 1 e a picareta, o resto mostra o que esta equipado.
-- caminho pra editar: PlayerGui > MinaHUD > Hotbar > Slot_1
-- so a picareta fica aqui. hats e pets se veem pelo Inventario.
local SLOTS = 1
local slotSel = 1

local hotbar = novoFrame({
	Name = "Hotbar",
	Size = UDim2.fromOffset(SLOTS * 58 + 10, 66),
	Position = UDim2.new(0.5, -(SLOTS * 58 + 10)/2, 1, -84),
	BackgroundColor3 = Color3.fromRGB(18, 24, 32),
	BackgroundTransparency = 0.25,
}, tela)
canto(hotbar, 12)

local hbLayout = Instance.new("UIListLayout")
hbLayout.FillDirection = Enum.FillDirection.Horizontal
hbLayout.Padding = UDim.new(0, 5)
hbLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
hbLayout.VerticalAlignment = Enum.VerticalAlignment.Center
hbLayout.Parent = hotbar

local celulasHB = {}
for k = 1, SLOTS do
	local b = Instance.new("TextButton")
	b.Name = "Slot_" .. k
	b.LayoutOrder = k
	b.Size = UDim2.fromOffset(53, 53)
	b.BackgroundColor3 = Color3.fromRGB(58, 72, 86)
	b.Text = ""
	b.BorderSizePixel = 0
	b.AutoButtonColor = false
	b.Parent = hotbar
	canto(b, 10)

	local st = Instance.new("UIStroke")
	st.Name = "Borda"
	st.Color = Color3.fromRGB(150, 190, 220)
	st.Thickness = 1.5
	st.Transparency = 0.5
	st.Parent = b

	local num = novoTexto({ Name = "Numero",
		Size = UDim2.fromOffset(14, 14), Position = UDim2.fromOffset(4, 2),
		TextXAlignment = Enum.TextXAlignment.Left, TextSize = 11, Font = Enum.Font.Gotham,
		TextColor3 = Color3.fromRGB(190, 210, 230), Text = tostring(k) }, b)

	local caixa = novoFrame({ Name = "Caixa",
		Size = UDim2.fromOffset(36, 36), Position = UDim2.fromOffset(8, 13),
		BackgroundTransparency = 1 }, b)

	celulasHB[k] = { botao = b, borda = st, caixa = caixa }
end

local function conteudoHotbar()
	-- slot unico: a picareta em uso
	local pic = dados and Config.picaretaPorId(dados.picareta)
	local cor = Color3.fromRGB(190, 195, 210)
	if pic and pic.raridade and Config.Raridades[pic.raridade] then
		cor = Config.Raridades[pic.raridade].cor
	end
	return { {
		tipo = "picareta",
		id = dados and dados.picareta or "",
		nome = pic and pic.nome or "Picareta",
		cor = cor,
	} }
end

local function renderHotbar()
	local itens = conteudoHotbar()
	for k = 1, SLOTS do
		local c = celulasHB[k]
		for _, f in ipairs(c.caixa:GetChildren()) do f:Destroy() end
		local it = itens[k]
		if it then
			c.botao.BackgroundColor3 = Color3.fromRGB(52, 66, 82)
			c.borda.Color = it.cor
			c.borda.Transparency = 0.15
			if it.tipo == "picareta" then
				local cabeca = novoFrame({ Size = UDim2.fromOffset(28, 9),
					Position = UDim2.fromOffset(4, 6), BackgroundColor3 = it.cor }, c.caixa)
				canto(cabeca, 3)
				local cabo = novoFrame({ Size = UDim2.fromOffset(6, 20),
					Position = UDim2.fromOffset(15, 14), BackgroundColor3 = Color3.fromRGB(150, 100, 58) }, c.caixa)
				canto(cabo, 2)
				-- nome da picareta embaixo do icone
				novoTexto({ Name = "NomePicareta",
					Size = UDim2.fromOffset(56, 12), Position = UDim2.fromOffset(-10, 37),
					TextSize = 10, Font = Enum.Font.GothamBold, TextColor3 = it.cor,
					TextTruncate = Enum.TextTruncate.AtEnd,
					Text = it.nome }, c.caixa)
			else
				desenharIcone(c.caixa, it.tipo, it.id, it.cor)
			end
		else
			c.botao.BackgroundColor3 = Color3.fromRGB(46, 58, 70)
			c.borda.Color = Color3.fromRGB(150, 190, 220)
			c.borda.Transparency = 0.6
		end
		-- selecionado
		if k == slotSel then
			c.botao.BackgroundColor3 = c.botao.BackgroundColor3:Lerp(Color3.new(1,1,1), 0.22)
			c.borda.Thickness = 3
			c.borda.Transparency = 0
		else
			c.borda.Thickness = 1.5
		end
	end
end

local function selecionarSlot(k)
	slotSel = math.clamp(k, 1, SLOTS)
	renderHotbar()
	local itens = conteudoHotbar()
	local it = itens[slotSel]
	if it and it.tipo ~= "picareta" then
		abaInv = (it.tipo == "hat") and "Hats" or "Pets"
		selecionado = { tipo = it.tipo, id = it.id }
		painelIgnis.frame.Visible = false
		painelLoja.frame.Visible = false
		painelInv.abrir()
	elseif it then
		avisar(it.nome, it.cor)
	end
end

for k = 1, SLOTS do
	celulasHB[k].botao.MouseButton1Click:Connect(function() selecionarSlot(k) end)
end

local TECLAS = { Enum.KeyCode.One, Enum.KeyCode.Two, Enum.KeyCode.Three, Enum.KeyCode.Four,
	Enum.KeyCode.Five, Enum.KeyCode.Six, Enum.KeyCode.Seven, Enum.KeyCode.Eight }
game:GetService("UserInputService").InputBegan:Connect(function(input, digitando)
	if digitando then return end
	for k, tecla in ipairs(TECLAS) do
		if input.KeyCode == tecla then selecionarSlot(k) end
	end
end)

-- ---------- LIGACOES ----------
atualizarUI = function()
	renderHotbar()
	painelIgnis.render()
	painelLoja.render()
	painelInv.render()
	atualizarGacha()
end

R.AbrirIgnis.OnClientEvent:Connect(function()
	painelLoja.frame.Visible = false
	painelInv.frame.Visible = false
	painelIgnis.abrir()
end)

R.AbrirLoja.OnClientEvent:Connect(function()
	painelIgnis.frame.Visible = false
	painelInv.frame.Visible = false
	painelLoja.abrir()
end)

-- Reference-inspired HUD / existing gameplay bindings retained.
do
local cyan=Color3.fromRGB(90,210,255)
local purple=Color3.fromRGB(180,110,255)
local gold=Color3.fromRGB(255,204,85)
local green=Color3.fromRGB(85,240,166)
local function skin(f,col)
 f.BackgroundColor3=Color3.fromRGB(10,16,30)
 f.BackgroundTransparency=.08
 local s=f:FindFirstChildOfClass("UIStroke") or Instance.new("UIStroke",f)
 s.Color=col or cyan s.Thickness=1 s.Transparency=.25
 if not f:FindFirstChildOfClass("UICorner") then canto(f,12) end
 local g=Instance.new("UIGradient",f)
 g.Color=ColorSequence.new(Color3.fromRGB(31,40,65),Color3.fromRGB(7,11,22))
 g.Rotation=100
end
local function text(p,value,x,y,w,h,size,col)
 return novoTexto({Text=value,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(w,h),
 TextSize=size or 13,TextColor3=col or Color3.new(1,1,1),TextXAlignment=Enum.TextXAlignment.Left},p)
end
local function panel(name,w,h,pos,col)
 local p=novoFrame({Name=name,Size=UDim2.fromOffset(w,h),Position=pos},tela)
 skin(p,col) return p
end
-- Scale a safe-area canvas to preserve spacing on smaller screens.
local canvas=novoFrame({Name="ResponsiveHUD",Size=UDim2.fromScale(1,1),BackgroundTransparency=1},tela)
for _,v in ipairs(tela:GetChildren()) do if v:IsA("GuiObject") and v~=canvas then v.Parent=canvas end end
local scale=Instance.new("UIScale",canvas)
local function resize()
 local v=tela.AbsoluteSize
 local s=math.min(1,v.X/1100,v.Y/700)
 scale.Scale=s canvas.Size=UDim2.fromOffset(v.X/s,v.Y/s)
end
tela:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize) resize()
local function attach(p) p.Parent=canvas return p end
-- pilula amarela: fundo solido, borda escura, icone a esquerda
hud.Name="Moedas"
hud.Size=UDim2.fromOffset(212,54)
hud.Position=UDim2.new(1,-228,0,14)
hud.BackgroundColor3=Color3.fromRGB(255,214,48)
hud.BackgroundTransparency=0
for _,v in ipairs(hud:GetChildren()) do
 if v:IsA("UIStroke") or v:IsA("UIGradient") or v:IsA("UICorner") then v:Destroy() end
end
local hc=Instance.new("UICorner",hud) hc.CornerRadius=UDim.new(0,16)
local hs=Instance.new("UIStroke",hud)
hs.Color=Color3.fromRGB(58,42,10) hs.Thickness=3 hs.Transparency=0
hs.ApplyStrokeMode=Enum.ApplyStrokeMode.Border
local hg=Instance.new("UIGradient",hud)
hg.Color=ColorSequence.new(Color3.fromRGB(255,228,96),Color3.fromRGB(246,190,26))
hg.Rotation=90

-- icone: usa a imagem se voce colou o ID na Config, senao desenha o simbolo
local urlMoeda = Config.icone and Config.icone("moeda")
if urlMoeda then
 local img=Instance.new("ImageLabel",hud)
 img.Name="IconeMoeda"
 img.Size=UDim2.fromOffset(40,40) img.Position=UDim2.fromOffset(9,7)
 img.BackgroundTransparency=1 img.Image=urlMoeda
 img.ScaleType=Enum.ScaleType.Fit
else
 local sym=novoTexto({Text="¥",Position=UDim2.fromOffset(12,9),Size=UDim2.fromOffset(36,36),
  TextSize=30,TextColor3=Color3.fromRGB(38,28,6)},hud)
 sym.Name="IconeMoeda"
end

lblMoeda.Position=UDim2.fromOffset(58,10)
lblMoeda.Size=UDim2.fromOffset(142,34)
lblMoeda.TextSize=26
lblMoeda.TextColor3=Color3.fromRGB(38,28,6)
lblMoeda.TextXAlignment=Enum.TextXAlignment.Left
lblMoeda.TextStrokeTransparency=1
local bag=attach(panel("Mochila",240,76,UDim2.new(0,16,1,-94),cyan))
lblMochila.Parent=bag lblMochila.Position=UDim2.fromOffset(72,29) lblMochila.Size=UDim2.fromOffset(158,20) lblMochila.TextSize=12
barraFundo.Parent=bag barraFundo.Position=UDim2.fromOffset(72,55) barraFundo.Size=UDim2.fromOffset(151,7)
text(bag,player.DisplayName,72,9,154,20,15)
local portrait=Instance.new("ImageLabel",bag)
portrait.Size=UDim2.fromOffset(54,54) portrait.Position=UDim2.fromOffset(9,10)
portrait.BackgroundColor3=Color3.fromRGB(29,45,63) canto(portrait,27)
task.spawn(function()
 local ok,url=pcall(function() return Players:GetUserThumbnailAsync(player.UserId,Enum.ThumbnailType.HeadShot,Enum.ThumbnailSize.Size150x150) end)
 if ok then portrait.Image=url end
end)
-- painel de equipamento removido: a hotbar ja mostra o que esta em uso
lblDano.Visible=false
hotbar.Position=UDim2.new(.5,-(hotbar.Size.X.Offset/2),1,-84) skin(hotbar,cyan)
-- aviso de area: aparece so ao entrar numa area nova e some sozinho
local area=attach(panel("AreaAtual",300,72,UDim2.new(.5,-150,0,-90),cyan))
area.BackgroundTransparency=.08
local areaTopo=text(area,"VOCÊ ENTROU EM",18,10,260,14,10,cyan)
areaTopo.TextXAlignment=Enum.TextXAlignment.Center
areaTopo.Size=UDim2.fromOffset(264,14)
local areaName=text(area,"",18,30,264,30,22)
areaName.TextXAlignment=Enum.TextXAlignment.Center
local areaVisivel=false
local function mostrarArea(nome)
 areaName.Text=nome
 if areaVisivel then return end
 areaVisivel=true
 TS:Create(area,TweenInfo.new(.4,Enum.EasingStyle.Back,Enum.EasingDirection.Out),
  {Position=UDim2.new(.5,-150,0,16)}):Play()
 task.delay(3.2,function()
  TS:Create(area,TweenInfo.new(.45,Enum.EasingStyle.Quad,Enum.EasingDirection.In),
   {Position=UDim2.new(.5,-150,0,-90)}):Play()
  task.wait(.5)
  areaVisivel=false
 end)
end
avisos.Position=UDim2.new(.5,-160,0,90) avisos.ZIndex=20
-- painel SUA JORNADA removido; vira sistema de quest no futuro
menu.Position=UDim2.fromOffset(16,92) menu.Size=UDim2.fromOffset(156,240)
menuLayout:Destroy()
local grid=Instance.new("UIGridLayout",menu)
grid.CellSize=UDim2.fromOffset(72,70) grid.CellPadding=UDim2.fromOffset(8,8) grid.SortOrder=Enum.SortOrder.LayoutOrder

local painelPasses = criarPainel("LOJA DE GAMEPASSES", gold, 620, 440, {
 {nome="Gamepasses",fn=function(pai)
  local passes=RS:FindFirstChild("Gamepasses")
  local count=0
  if passes then
   for _,pass in ipairs(passes:GetChildren()) do
    if pass:IsA("IntValue") and pass.Value>0 then
     count+=1
     local row=linha(pai,pass.Name,"Carregando informações...",nil)
     task.spawn(function()
      local market=game:GetService("MarketplaceService")
      local ok,info=pcall(function() return market:GetProductInfo(pass.Value,Enum.InfoType.GamePass) end)
      if not row.Parent then return end
      row:Destroy()
      if not ok then linha(pai,pass.Name,"Informações indisponíveis. Reabra a loja.",nil) return end
      local ownsOk,owned=pcall(function() return market:UserOwnsGamePassAsync(player.UserId,pass.Value) end)
      local available=info.IsForSale and info.PriceInRobux~=nil
      linha(pai,info.Name or pass.Name,info.Description or "",
       owned and ownsOk and "ADQUIRIDO" or (available and ("R$ "..tostring(info.PriceInRobux)) or "INDISPONÍVEL"),
       ROXO,function() market:PromptGamePassPurchase(player,pass.Value) end,
       (ownsOk and owned) or not available)
     end)
    end
   end
  end
  if count==0 then
   linha(pai,"Gamepasses em breve","Nenhum passe disponível no momento.",nil)
  end
 end},
})
botaoHUD("Loja","Loja",gold,gold,"loja",0,function()
 painelIgnis.frame.Visible=false
 painelLoja.frame.Visible=false
 painelInv.frame.Visible=false
 painelGacha.Visible=false
 if painelPasses.frame.Visible then painelPasses.frame.Visible=false else painelPasses.abrir() end
end)
skin(painelPasses.frame,purple)
painelPasses.frame.ZIndex=30
painelPasses.frame.Parent=canvas


botaoHUD("Som","Som",cyan,cyan,"config",6,function()
 local ost=game:GetService("SoundService"):FindFirstChild("OST")
 if ost then if ost.IsPlaying then ost:Pause() else ost:Resume() end end
end)
for _,b in ipairs(menu:GetChildren()) do
 if b:IsA("TextButton") then
 local col=b.Borda.Color skin(b,col)
 b.Borda.Thickness=1
 if b:FindFirstChild("Brilho") then b.Brilho.BackgroundTransparency=.94 end
 b.Rotulo.Text=({Inventario="Inventário",Pets="Pets",Areas="Áreas"})[b.Name:sub(7)] or b.Rotulo.Text
 b.Rotulo.TextSize=11
 local ico=b:FindFirstChild("Icone")
 -- so recolore icone desenhado; imagem propria fica intacta
 if ico and not ico:FindFirstChild("Imagem") then
  for _,v in ipairs(ico:GetDescendants()) do if v:IsA("Frame") then v.BackgroundColor3=col end end
 end
 
 
 end
end
-- SUA COLECAO removido (vira aba de index) e DICA removida.
-- Bonus vira so uma pilula de icone no canto, e some quando e zero.
local bonus=attach(novoFrame({Name="Boost",Size=UDim2.fromOffset(96,38),
 Position=UDim2.new(1,-116,0,86),BackgroundColor3=Color3.fromRGB(10,16,30),Visible=false},tela))
canto(bonus,19)
local bs=Instance.new("UIStroke",bonus) bs.Color=green bs.Thickness=2 bs.Transparency=.15
local bonusIco=novoTexto({Text="▲",Position=UDim2.fromOffset(10,7),Size=UDim2.fromOffset(24,24),
 TextSize=18,TextColor3=green},bonus)
local bonusText=novoTexto({Text="+0%",Position=UDim2.fromOffset(36,7),Size=UDim2.fromOffset(52,24),
 TextSize=17,TextColor3=green,TextXAlignment=Enum.TextXAlignment.Left},bonus)
for _,p in ipairs({painelIgnis.frame,painelLoja.frame,painelInv.frame,painelGacha}) do
 skin(p,purple) p.ZIndex=30
end
local oldUpdate=atualizarUI
atualizarUI=function()
 oldUpdate()
 if not dados then return end
 local pct=math.floor((dados.bonusValor or 0)*100+0.5)
 bonus.Visible = pct > 0
 bonusText.Text="+"..pct.."%"
end
-- so avisa quando o jogador REALMENTE muda de area
task.spawn(function()
 local ultima=nil
 while tela.Parent do
  task.wait(0.6)
  local char=player.Character
  local root=char and char:FindFirstChild("HumanoidRootPart")
  if root then
   local atual=nil
   local areas=workspace:FindFirstChild("Areas")
   if areas then
    for _,m in ipairs(areas:GetChildren()) do
     local id=m:GetAttribute("AreaId")
     local def=id and Config.areaPorId(id)
     if def then
      local c,t=def.centro,def.tamanho
      -- dentro do retangulo da area, nao "a mais perto"
      if math.abs(root.Position.X-c.X)<=t.X/2 and math.abs(root.Position.Z-c.Z)<=t.Z/2 then
       atual=def.nome
       break
      end
     end
    end
   end
   if atual ~= ultima then
    ultima=atual
    if atual then mostrarArea(atual) end
   end
  end
 end
end)
if dados then atualizarUI() end
end

-- Illustrated circular menu, using a shared sprite atlas.
do
local canvas=tela:FindFirstChild("ResponsiveHUD") or tela
local ATLAS="rbxassetid://117093221263804"
local gold=Color3.fromRGB(255,207,74)
local settings
settings=criarPainel("CONFIGURAÇÕES",gold,520,300,{{nome="Preferências",fn=function(pai)
 local ost=game:GetService("SoundService"):FindFirstChild("OST")
 linha(pai,"Música","Trilha sonora do jogo",ost and ost.IsPlaying and "DESLIGAR" or "LIGAR",AZUL,function()
  if ost then if ost.IsPlaying then ost:Pause() else ost:Resume() end end
  settings.render()
 end)
 linha(pai,"Efeitos do lobby","Partículas, pássaros e correnteza",player:GetAttribute("LobbyVFXEnabled")==false and "LIGAR" or "DESLIGAR",ROXO,function()
  player:SetAttribute("LobbyVFXEnabled",player:GetAttribute("LobbyVFXEnabled")==false)
  avisar(player:GetAttribute("LobbyVFXEnabled") and "Efeitos ativados" or "Efeitos reduzidos")
  settings.render()
 end)
end}})
settings.frame.Name="PainelConfiguracoes"
settings.frame.Parent=canvas settings.frame.ZIndex=40
botaoHUD("Config","Config.",Color3.fromRGB(35,38,48),Color3.fromRGB(145,161,195),"config",5,function()
 if settings.frame.Visible then settings.frame.Visible=false else
 painelIgnis.frame.Visible=false painelLoja.frame.Visible=false painelInv.frame.Visible=false painelGacha.Visible=false
 settings.abrir()
 end
end)
local layout=menu:FindFirstChildOfClass("UIGridLayout")
layout.CellSize=UDim2.fromOffset(92,104)
layout.CellPadding=UDim2.fromOffset(10,12)
menu.Size=UDim2.fromOffset(194,336)
menu.Position=UDim2.fromOffset(18,96)
local mapping={
 Loja={0,0,"Loja",0},Pets={1,0,"Pets",1},Inventario={2,0,"Inventário",2},
 Areas={3,0,"Áreas",3},Config={1,1,"Config.",4},Som={2,1,"Som",5}
}
local sprites={}
for _,b in ipairs(menu:GetChildren()) do
 if b:IsA("TextButton") then
 local spec=mapping[b.Name:sub(7)]
 if spec then
 b.LayoutOrder=spec[4] b.BackgroundTransparency=1 b.AutoButtonColor=false
 for _,v in ipairs(b:GetChildren()) do
 if v:IsA("UIGradient") or v.Name=="Icone" or v.Name=="Brilho" then v:Destroy() end
 end
 local oldStroke=b:FindFirstChild("Borda") if oldStroke then oldStroke.Transparency=1 end
 local face=Instance.new("ImageLabel",b)
 face.Name="Arte" face.BackgroundColor3=Color3.fromRGB(16,19,24)
 face.Size=UDim2.fromOffset(88,88) face.Position=UDim2.fromOffset(2,0)
 face.Image=ATLAS face.ScaleType=Enum.ScaleType.Stretch
 -- The upload preserves the source atlas's pixel dimensions.
 face.ImageRectOffset=Vector2.new(spec[1]*256,spec[2]*256)
 face.ImageRectSize=Vector2.new(256,256)
 face.ZIndex=2
 local corner=Instance.new("UICorner",face) corner.CornerRadius=UDim.new(.5,0)
 local rim=Instance.new("UIStroke",face) rim.Color=Color3.fromRGB(43,46,53) rim.Thickness=3 rim.ApplyStrokeMode=Enum.ApplyStrokeMode.Border
 local hover=Instance.new("UIScale",face)
 face.AnchorPoint=Vector2.new(.5,.5) face.Position=UDim2.fromOffset(46,44)
 local label=b:FindFirstChild("Rotulo")
 label.Text=spec[3] label.TextSize=21 label.Font=Enum.Font.FredokaOne
 label.Size=UDim2.new(1,12,0,30) label.Position=UDim2.fromOffset(-6,76)
 label.TextColor3=spec[3]=="Loja" and gold or Color3.new(1,1,1)
 label.TextStrokeTransparency=1 label.ZIndex=4
 local outline=Instance.new("UIStroke",label) outline.Color=Color3.fromRGB(3,4,6) outline.Thickness=3 outline.LineJoinMode=Enum.LineJoinMode.Round
 b.MouseEnter:Connect(function()
  TS:Create(hover,TweenInfo.new(.15,Enum.EasingStyle.Back),{Scale=1.07}):Play()
  rim.Color=gold
 end)
 b.MouseLeave:Connect(function()
  TS:Create(hover,TweenInfo.new(.15),{Scale=1}):Play()
  rim.Color=Color3.fromRGB(43,46,53)
 end)
 b.MouseButton1Down:Connect(function() hover.Scale=.94 end)
 b.MouseButton1Up:Connect(function() hover.Scale=1 end)
 table.insert(sprites,face)
 end
 end
end
task.spawn(function() pcall(function() game:GetService("ContentProvider"):PreloadAsync(sprites) end) end)
end

