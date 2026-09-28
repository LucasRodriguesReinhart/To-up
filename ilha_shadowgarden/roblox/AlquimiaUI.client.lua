-- AlquimiaUI (LocalScript, StarterPlayerScripts) - interface da Ilha 3 (Shadow Garden):
--  * painel de ALQUIMIA (abre pelo prompt do caldeirao: Remotes.AbrirCraft): receitas com ingredientes que voce tem /
--    precisa, botao Fabricar (Remotes.FabricarItem, com requestId) e a lista dos seus itens com Beber nas pocoes
--    (Remotes.UsarItem). O estado vem do snapshot de sempre (AtualizarDados/PedirDados, campo itens).
--  * faixa da MASMORRA no topo, so na Shadow Garden: estado e contagem lidos dos atributos de RS.MasmorraEstado
--    (AbreEm/EntradaFechaEm/FechaEm em GetServerTimeNow; o servidor publica, o cliente so conta).
-- Usa os tokens do ExpeditionUI.Theme (cores, fontes, icones, raridade) para casar com o resto da UI.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")
local player = Players.LocalPlayer
local Config = require(RS:WaitForChild("Config"))
local Alq = require(RS:WaitForChild("AlquimiaConfig"))
local Remotes = RS:WaitForChild("Remotes")
local okT, T = pcall(require, RS:WaitForChild("ExpeditionUI"):WaitForChild("Theme"))
if not okT then T = nil end
local rgb = Color3.fromRGB
local P = T and T.P or { bg0 = rgb(7, 10, 12), bg1 = rgb(13, 17, 20), bg2 = rgb(20, 25, 28), bg3 = rgb(31, 37, 40),
	line = rgb(116, 132, 139), lineSoft = rgb(61, 73, 79), text = rgb(255, 255, 255), text2 = rgb(225, 225, 235),
	text3 = rgb(169, 169, 188), violet = rgb(167, 74, 255), success = rgb(49, 204, 108), danger = rgb(225, 38, 64) }
local FT = T and T.F or {}
local function font(k) return FT[k] or Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Bold) end
local function rarCor(k) if T and T.rar then return (T.rar(k)).cor end return P.text2 end

local itens, areas = {}, {}
local function areaSombra()
	for _, a in ipairs(Config.Areas) do if a.tema == "sombra" then return a end end
end
local AREA = areaSombra()

-- ---------------------------------------------------------------- base visual
local gui = Instance.new("ScreenGui")
gui.Name = "AlquimiaUI"; gui.ResetOnSpawn = false; gui.IgnoreGuiInset = false; gui.DisplayOrder = 6
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling; gui.Parent = player:WaitForChild("PlayerGui")

local function frame(pai, nome, props)
	local f = Instance.new("Frame"); f.Name = nome; f.BorderSizePixel = 0
	for k, v in pairs(props or {}) do f[k] = v end
	f.Parent = pai
	return f
end
local function corner(o, r) local c = Instance.new("UICorner"); c.CornerRadius = UDim.new(0, r or 8); c.Parent = o return c end
local function stroke(o, cor, t) local s = Instance.new("UIStroke"); s.Color = cor; s.Thickness = t or 1.5; s.Parent = o return s end
local function label(pai, nome, texto, props)
	local l = Instance.new("TextLabel"); l.Name = nome; l.BackgroundTransparency = 1; l.Text = texto
	l.FontFace = font("body"); l.TextColor3 = P.text; l.TextScaled = false; l.TextSize = 16
	l.TextXAlignment = Enum.TextXAlignment.Left
	for k, v in pairs(props or {}) do l[k] = v end
	l.Parent = pai
	return l
end
local function botao(pai, nome, texto, cor, fn)
	local b = Instance.new("TextButton"); b.Name = nome; b.AutoButtonColor = true; b.BorderSizePixel = 0
	b.BackgroundColor3 = cor; b.Text = texto; b.FontFace = font("label"); b.TextSize = 16; b.TextColor3 = P.text
	corner(b, 6); b.Parent = pai
	b.MouseButton1Click:Connect(fn)
	return b
end
local function icone(pai, key, x, y, s)
	if T and T.icon then
		local ok, im = pcall(T.icon, pai, key, x, y, s)
		if ok and im then return im end
	end
end

-- ---------------------------------------------------------------- painel da Alquimia
local painel = frame(gui, "Painel", { AnchorPoint = Vector2.new(.5, .5), Position = UDim2.fromScale(.5, .5),
	Size = UDim2.fromOffset(760, 470), BackgroundColor3 = P.bg1, Visible = false })
corner(painel, 10); stroke(painel, P.violet, 2)
local escala = Instance.new("UIScale"); escala.Parent = painel
local function ajustar()
	local cam = workspace.CurrentCamera
	local v = cam and cam.ViewportSize or Vector2.new(1280, 720)
	escala.Scale = math.clamp(math.min(v.X / 820, v.Y / 520), 0.55, 1.25)
end
ajustar()
workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(ajustar)

label(painel, "Titulo", "ALQUIMIA", { Position = UDim2.fromOffset(22, 14), Size = UDim2.fromOffset(400, 34),
	FontFace = font("title"), TextSize = 28, TextColor3 = P.text })
label(painel, "Sub", "Pocoes com ingredientes da Masmorra das Sombras", { Position = UDim2.fromOffset(22, 46),
	Size = UDim2.fromOffset(500, 20), TextColor3 = P.text3, TextSize = 14, FontFace = font("regular") })
local fechar = botao(painel, "Fechar", "X", P.bg3, function() painel.Visible = false end)
fechar.Size = UDim2.fromOffset(36, 36)
fechar.Position = UDim2.fromOffset(760 - 50, 14)

local colR = frame(painel, "Receitas", { Position = UDim2.fromOffset(18, 80), Size = UDim2.fromOffset(452, 372),
	BackgroundColor3 = P.bg2 })
corner(colR, 8)
local colI = frame(painel, "Itens", { Position = UDim2.fromOffset(484, 80), Size = UDim2.fromOffset(258, 372),
	BackgroundColor3 = P.bg2 })
corner(colI, 8)
local aviso = label(painel, "Aviso", "", { Position = UDim2.fromOffset(22, 452), Size = UDim2.fromOffset(700, 16),
	TextSize = 13, TextColor3 = P.text3, FontFace = font("regular") })

local function limpar(f) for _, c in ipairs(f:GetChildren()) do if not c:IsA("UICorner") then c:Destroy() end end end
local ocupado = false
local function toast(texto, bom)
	aviso.Text = texto or ""
	aviso.TextColor3 = bom and P.success or (bom == false and P.danger or P.text3)
end

local desenhar
local function fabricar(r)
	if ocupado then return end
	ocupado = true
	local ok, res = pcall(function() return Remotes:WaitForChild("FabricarItem"):InvokeServer(r.id, HttpService:GenerateGUID(false)) end)
	ocupado = false
	if ok and type(res) == "table" then toast(res.msg or (res.ok and "Pronto!" or "Nao deu."), res.ok) else toast("Erro de conexao.", false) end
end
local function beber(id)
	if ocupado then return end
	ocupado = true
	local ok, res = pcall(function() return Remotes:WaitForChild("UsarItem"):InvokeServer(id) end)
	ocupado = false
	if ok and type(res) == "table" then toast(res.msg or "", res.ok) else toast("Erro de conexao.", false) end
end

desenhar = function()
	limpar(colR); limpar(colI)
	label(colR, "Cab", "RECEITAS", { Position = UDim2.fromOffset(14, 8), Size = UDim2.fromOffset(300, 22),
		FontFace = font("label"), TextSize = 16, TextColor3 = P.text2 })
	for i, r in ipairs(Alq.Receitas) do
		local def = Alq.item(r.resultado)
		local y = 36 + (i - 1) * 110
		local card = frame(colR, "R_" .. r.id, { Position = UDim2.fromOffset(10, y), Size = UDim2.fromOffset(432, 102),
			BackgroundColor3 = P.bg3 })
		corner(card, 8); stroke(card, rarCor(def.raridade), 1.2)
		icone(card, def.icone or "potion", 10, 10, 44)
		label(card, "Nome", def.nome, { Position = UDim2.fromOffset(62, 8), Size = UDim2.fromOffset(250, 22),
			FontFace = font("label"), TextSize = 17, TextColor3 = rarCor(def.raridade) })
		label(card, "Desc", def.desc or "", { Position = UDim2.fromOffset(62, 30), Size = UDim2.fromOffset(250, 30),
			TextSize = 12, TextWrapped = true, TextYAlignment = Enum.TextYAlignment.Top, TextColor3 = P.text3,
			FontFace = font("regular") })
		local podes = true
		local partes = {}
		for _, par in ipairs(r.ingredientes) do
			local ing = Alq.item(par[1])
			local tem = itens[par[1]] or 0
			if tem < par[2] then podes = false end
			table.insert(partes, string.format("%s %d/%d", ing and ing.nome or par[1], tem, par[2]))
		end
		label(card, "Ingr", table.concat(partes, "   "), { Position = UDim2.fromOffset(12, 70), Size = UDim2.fromOffset(300, 24),
			TextSize = 13, TextWrapped = true, TextColor3 = podes and P.success or P.text2, FontFace = font("body") })
		local b = botao(card, "Fabricar", "FABRICAR", podes and P.violet or P.bg2, function() fabricar(r) end)
		b.Position = UDim2.fromOffset(318, 30); b.Size = UDim2.fromOffset(104, 40)
		b.AutoButtonColor = podes
		b.TextColor3 = podes and P.text or P.text3
	end
	label(colI, "Cab", "SEUS ITENS", { Position = UDim2.fromOffset(14, 8), Size = UDim2.fromOffset(200, 22),
		FontFace = font("label"), TextSize = 16, TextColor3 = P.text2 })
	local y = 36
	local n = 0
	for _, def in ipairs(Alq.Itens) do
		local q = itens[def.id] or 0
		if q > 0 then
			n += 1
			local row = frame(colI, "I_" .. def.id, { Position = UDim2.fromOffset(8, y), Size = UDim2.fromOffset(242, 44),
				BackgroundColor3 = P.bg3 })
			corner(row, 6)
			icone(row, def.icone or "items", 6, 6, 32)
			label(row, "Nome", def.nome, { Position = UDim2.fromOffset(44, 4), Size = UDim2.fromOffset(130, 18), TextSize = 13,
				FontFace = font("body"), TextColor3 = rarCor(def.raridade), TextTruncate = Enum.TextTruncate.AtEnd })
			label(row, "Qtd", "x" .. q, { Position = UDim2.fromOffset(44, 22), Size = UDim2.fromOffset(80, 18), TextSize = 13,
				TextColor3 = P.text2 })
			if def.categoria == "pocao" then
				local b = botao(row, "Beber", "BEBER", P.success, function() beber(def.id) end)
				b.Position = UDim2.fromOffset(176, 7); b.Size = UDim2.fromOffset(60, 30); b.TextSize = 13
			end
			y += 50
		end
	end
	if n == 0 then
		label(colI, "Vazio", "Nada ainda. Entre na Masmorra das Sombras (torre ao lado do castelo) nas aberturas das XX:00 e XX:30.",
			{ Position = UDim2.fromOffset(14, 40), Size = UDim2.fromOffset(230, 120), TextWrapped = true, TextSize = 13,
				TextYAlignment = Enum.TextYAlignment.Top, TextColor3 = P.text3, FontFace = font("regular") })
	end
end

local function aceitar(snap)
	if type(snap) ~= "table" then return end
	if type(snap.itens) == "table" then itens = snap.itens end
	if type(snap.areas) == "table" then areas = snap.areas end
	if painel.Visible then desenhar() end
end
Remotes:WaitForChild("AtualizarDados").OnClientEvent:Connect(aceitar)
task.spawn(function()
	local pd = Remotes:WaitForChild("PedirDados", 10)
	if pd then local ok, snap = pcall(function() return pd:InvokeServer() end) if ok then aceitar(snap) end end
end)
task.spawn(function()
	local ab = Remotes:WaitForChild("AbrirCraft", 120)
	if ab then ab.OnClientEvent:Connect(function() toast(""); desenhar(); painel.Visible = true end) end
end)

-- ---------------------------------------------------------------- faixa da Masmorra
local faixa = frame(gui, "Masmorra", { AnchorPoint = Vector2.new(.5, 0), Position = UDim2.new(.5, 0, 0, 58),
	Size = UDim2.fromOffset(330, 34), BackgroundColor3 = P.bg1, BackgroundTransparency = 0.12, Visible = false })
corner(faixa, 17); local fs = stroke(faixa, P.violet, 1.5)
local ft = label(faixa, "Texto", "", { Size = UDim2.fromScale(1, 1), TextXAlignment = Enum.TextXAlignment.Center,
	FontFace = font("label"), TextSize = 15, TextColor3 = P.text })
local function relogio(s)
	s = math.max(0, math.floor(s))
	return string.format("%02d:%02d", math.floor(s / 60), s % 60)
end
task.spawn(function()
	local est = RS:WaitForChild("MasmorraEstado", 120)
	while gui.Parent do
		local naIlha = AREA and player:GetAttribute("CurrentAreaId") == AREA.id
		local e = est and est:GetAttribute("Estado")
		faixa.Visible = naIlha and e ~= nil and e ~= "INDISPONIVEL"
		if faixa.Visible then
			local t = workspace:GetServerTimeNow() + (est:GetAttribute("Deslocamento") or 0)
			local dentro = player:GetAttribute("DungeonRun") ~= nil
			local txt, cor
			if e == "WAITING" then txt, cor = "MASMORRA DAS SOMBRAS  abre em " .. relogio((est:GetAttribute("AbreEm") or t) - t), P.text2
			elseif e == "COUNTDOWN" then txt, cor = "MASMORRA ABRE EM " .. relogio((est:GetAttribute("AbreEm") or t) - t), P.violet
			elseif e == "ENTRY_OPEN" then
				if dentro then txt = "MASMORRA  tempo " .. relogio((est:GetAttribute("FechaEm") or t) - t) .. "  restam " .. (est:GetAttribute("Restantes") or 0)
				else txt = "MASMORRA ABERTA!  entre em " .. relogio((est:GetAttribute("EntradaFechaEm") or t) - t) end
				cor = P.success
			elseif e == "RUNNING" then
				txt = dentro and ("MASMORRA  tempo " .. relogio((est:GetAttribute("FechaEm") or t) - t) .. "  restam " .. (est:GetAttribute("Restantes") or 0))
					or ("MASMORRA EM ANDAMENTO  " .. relogio((est:GetAttribute("FechaEm") or t) - t))
				cor = P.violet
			elseif e == "FINISHING" then txt, cor = dentro and "FIM DA CORRIDA  saia pelo portal" or "MASMORRA TERMINANDO", P.text2
			else txt, cor = "MASMORRA REINICIANDO", P.text3 end
			ft.Text = txt
			fs.Color = cor
		end
		task.wait(0.25)
	end
end)
