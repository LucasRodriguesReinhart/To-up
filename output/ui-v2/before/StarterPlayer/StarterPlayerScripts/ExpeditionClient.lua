-- ============================================================================
-- EXPEDITION CLIENT · UI V2
-- HUD, janelas, popups, confirmações e o fluxo de recompensas do jogo.
-- Visual e componentes: ReplicatedStorage.ExpeditionUI (Theme, Notify, Menus, Inventory).
-- A lógica de jogo continua no servidor; este script só chama os mesmos Remotes.
-- ============================================================================
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Input = game:GetService("UserInputService")
local Lighting = game:GetService("Lighting")
local player = Players.LocalPlayer
local pg = player:WaitForChild("PlayerGui")
local R = RS:WaitForChild("Remotes")
local Config = require(RS:WaitForChild("Config"))
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local Som = require(RS:WaitForChild("SomJogo"))
local modules = RS:WaitForChild("ExpeditionUI")
local T = require(modules.Theme)
local Notify = require(modules.Notify)
local Inventory = require(modules.Inventory)
local Menus = require(modules.Menus)
local P, C = T.P, T.C
local WHITE = Color3.new(1, 1, 1)

local BASE_W, BASE_H = 1440, 850
local screen = T.new("ScreenGui", { Name = "ExpeditionUI", ResetOnSpawn = false, DisplayOrder = 25, IgnoreGuiInset = false, ClipToDeviceSafeArea = false,
	ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, pg)
local canvas = T.frame(screen, "Canvas", 0, 0, BASE_W, BASE_H, nil, 1)
local scale = T.new("UIScale", { Scale = 1 }, canvas)
local hud = T.frame(canvas, "HUD", 0, 0, BASE_W, BASE_H, nil, 1)
local dim = T.new("TextButton", { Name = "ModalBackdrop", Text = "", Size = UDim2.fromScale(1, 1), BackgroundColor3 = P.bg0,
	BackgroundTransparency = .45, BorderSizePixel = 0, AutoButtonColor = false, Visible = false, ZIndex = 20, Active = true }, canvas)
local modalLayer = T.frame(canvas, "ModalLayer", 0, 0, BASE_W, BASE_H, nil, 1)
modalLayer.ZIndex = 21
local toastLayer = T.frame(canvas, "Notifications", 0, 0, BASE_W, BASE_H, nil, 1)
toastLayer.ZIndex = 70
local popupLayer = T.frame(canvas, "PopupLayer", 0, 0, BASE_W, BASE_H, nil, 1)
popupLayer.ZIndex = 90
local dialogHost = T.frame(popupLayer, "Dialogs", 0, 0, BASE_W, BASE_H, nil, 1)
local tipLayer = T.frame(canvas, "TooltipLayer", 0, 0, BASE_W, BASE_H, nil, 1)
tipLayer.ZIndex = 120
local blur = T.new("BlurEffect", { Name = "ExpeditionMenuBlur", Size = 0 }, Lighting)

local ctx = { data = nil, page = nil, collection = "pet", selected = nil, search = "", rarity = nil, ownedOnly = true, favorites = {},
	areaFavorites = {}, storeTab = "Picaretas", eventsTab = "Diario", bannerArea = 1, inventoryScroll = {}, scrollMemory = {},
	portrait = false, compact = false, summonBusy = false }
local virtualW, virtualH = BASE_W, BASE_H
local window, body, searchBox
local bodyW, bodyH = 0, 0
local actionBusy = {}
local pushVersion, hydrated, modalVersion = 0, false, 0
local pendingRefresh, lastInventorySignature = false, ""
local drawWindow, drawHeader, drawBody, drawHUD, updateHUD
local closePopup
local hudRefs = {}
local popupOpen = false
ctx.T, ctx.Notify = T, Notify

T.setTooltipLayer(tipLayer, function() return scale.Scale end)
-- com uma janela aberta o HUD fica atrás do fundo escuro: nada de dica dele aparecendo por cima
T.setTooltipGuard(function(o) return not (ctx.page and o:IsDescendantOf(hud)) end)
Notify.init(toastLayer, popupLayer, function() return virtualW, virtualH end)
Notify.feedAnchor = function() return virtualW - 16, virtualH - 16 - 58 end

-- ---------------------------------------------------------------- PÁGINAS
local PAGE = {
	Store = { title = "Loja", icon = "store", color = P.gold, sub = "Picaretas, mochilas, passes e boosts" },
	Inventory = { title = "Unidades", icon = "units", color = P.accent },
	Areas = { title = "Viajar", icon = "areas", color = P.teal, sub = "Ilhas de mineração e atalhos do lobby" },
	Summon = { title = "Invocar", icon = "summon", color = P.violet },
	Forge = { title = "Forja de Ignis", icon = "forge", color = P.ember, sub = "Venda seus minérios por moedas" },
	Settings = { title = "Configurações", icon = "settings", color = T.Page.Settings, sub = "Som, efeitos e códigos" },
	Quests = { title = "Missões", icon = "quests", color = P.warning },
	Events = { title = "Diário & Index", icon = "events", color = P.pink, sub = "Recompensas diárias e coleção" },
}
ctx.PAGE = PAGE

-- ---------------------------------------------------------------- TOASTS / BLUR
local function kindFor(color)
	if color == C.green then return "success" elseif color == C.red then return "error"
	elseif color == C.orange then return "warning" elseif color == C.gold then return "reward" end
	return "info"
end
function ctx.toast(value, color, kind)
	Notify.push(value, kind or kindFor(color))
end

local function updateBlur()
	local amount = ctx.page and player:GetAttribute("ExpeditionBlurEnabled") ~= false and 14 or 0
	T.tween(blur, .2, { Size = amount }, Enum.EasingStyle.Quad)
end

-- ---------------------------------------------------------------- POPUPS
closePopup = function()
	if not popupOpen then return end
	popupOpen = false
	local old = dialogHost:GetChildren()
	for _, o in ipairs(old) do
		o.Name = o.Name .. "_Closing"
		if o:IsA("TextButton") then T.tween(o, .1, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad) end
		local sc = o:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .1, { Scale = .94 }, Enum.EasingStyle.Quad) end
	end
	task.delay(.11, function() for _, o in ipairs(old) do o:Destroy() end end)
end
ctx.closePopup = function() closePopup() end

function ctx.popup(title, builder, w, h, opts)
	opts = opts or {}
	closePopup()
	popupOpen = true
	T.hideTooltip()
	w = math.min(w or 560, virtualW - 32)
	h = math.min(h or 420, virtualH - 40)
	local shield = T.new("TextButton", { Name = "PopupBackdrop", Text = "", AutoButtonColor = false, BorderSizePixel = 0,
		BackgroundColor3 = P.bg0, BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1) }, dialogHost)
	T.tween(shield, .16, { BackgroundTransparency = .35 }, Enum.EasingStyle.Quad)
	shield.Activated:Connect(function() if not opts.modal then closePopup() end end)
	local box = T.panel(dialogHost, "Popup", (virtualW - w) / 2, (virtualH - h) / 2, w, h, { bg = P.bg1, radius = 16, strokeColor = P.line, shade = false })
	box.Active = true
	local shadow = T.shadow(box, 16, 10, .4)
	local accent = opts.color or P.accent
	local line = T.frame(box, "Accent", 18, 0, w - 36, 3, accent, 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, line)
	T.text(box, "Title", title, 22, 14, w - 90, 36, 24, P.text, T.LEFT, "display")
	T.closeButton(box, w - 54, 14, 38, closePopup)
	local area = T.frame(box, "Content", 20, 64, w - 40, h - 84, nil, 1)
	builder(area, w - 40, h - 84)
	T.enter(box, .9, .24)
	T.enter(shadow, .9, .24)
	T.som("ui_popup")
	return box
end

-- confirmação. opts: confirmText, cancelText, tone, cost (moedas), preview(p,w) + previewH, w, h
function ctx.confirm(title, message, callback, opts)
	opts = opts or {}
	local hasCost = opts.cost ~= nil
	ctx.popup(title, function(p, w, h)
		local y = 0
		if opts.preview then opts.preview(p, w); y = (opts.previewH or 0) + 10 end
		local bottom = hasCost and 146 or 66
		T.para(p, "Prompt", message, 0, y, w, math.max(30, h - y - bottom), 18, P.text2, T.CENTER, "body")
		if hasCost then
			local have = ctx.data and ctx.data.moeda or 0
			local row = T.panel(p, "CostRow", 0, h - 140, w, 58, { bg = P.bg0, radius = 12 })
			T.text(row, "CostLabel", "PREÇO", 16, 0, 120, 58, 14, P.text2, T.LEFT, "title")
			T.icon(row, "coins", w - 196, 9, 40, 40)
			T.text(row, "Cost", T.format(opts.cost), w - 152, 0, 136, 58, 26, P.gold, T.RIGHT, "display", 1.4)
			T.text(p, "After", have >= opts.cost and ("Saldo depois da compra: " .. T.format(have - opts.cost)) or ("Faltam " .. T.format(opts.cost - have) .. " moedas"),
				0, h - 78, w, 20, 14, have >= opts.cost and P.text3 or P.danger, T.CENTER, "body")
		end
		local bw = (w - 12) / 2
		T.button(p, "Cancel", opts.cancelText or "Cancelar", 0, h - 52, bw, 52, P.neutral, closePopup)
		local used = false
		local ok = T.button(p, "Confirm", opts.confirmText or "Confirmar", bw + 12, h - 52, bw, 52, opts.tone or P.success, function()
			if used then return end
			used = true
			closePopup()
			callback()
		end)
		if hasCost and (ctx.data and ctx.data.moeda or 0) < opts.cost then T.setEnabled(ok, false) end
	end, opts.w or 520, opts.h or ((hasCost and 330 or 250) + (opts.previewH and opts.previewH + 10 or 0)), { color = opts.tone })
end

-- ---------------------------------------------------------------- RECOMPENSA VISUAL
-- moedas saem do centro, param um instante e voam para a carteira (o contador sobe quando chegam)
function ctx.coinBurst(amount, sx, sy)
	local wallet = hudRefs.wallet
	if not wallet or not wallet.Parent then return end
	sx, sy = sx or virtualW / 2, sy or virtualH * .55
	local tx = wallet.Position.X.Offset + 26
	local ty = wallet.Position.Y.Offset + 27
	local n = math.clamp(math.floor(math.log10(math.max(10, amount or 10)) * 1.6), 5, 14)
	for i = 1, n do
		local c = T.icon(toastLayer, "coins", sx - 20, sy - 20, 40, 40)
		c.ZIndex = 40
		local ang = math.random() * math.pi * 2
		local rad = 50 + math.random() * 90
		T.tween(c, .26, { Position = UDim2.fromOffset(sx - 20 + math.cos(ang) * rad, sy - 20 + math.sin(ang) * rad * .7) }, Enum.EasingStyle.Quad)
		task.delay(.34 + i * .04, function()
			T.tween(c, .44, { Position = UDim2.fromOffset(tx - 15, ty - 15), Size = UDim2.fromOffset(30, 30) }, Enum.EasingStyle.Quint, Enum.EasingDirection.In)
			task.delay(.44, function()
				c:Destroy()
				if i % 2 == 1 then Som.tocar("coin_tick") end
				if wallet.Parent then T.pop(wallet, 1.05, .16) end
			end)
		end)
	end
end

local function floatDelta(text, col)
	local wallet = hudRefs.wallet
	if not wallet or not wallet.Parent then return end
	local x = wallet.Position.X.Offset
	local y = wallet.Position.Y.Offset + 58
	local w = wallet.Size.X.Offset
	local t = T.text(hud, "CoinDelta", text, x, y, w - 20, 24, 20, col, T.RIGHT, "display", 1.6)
	T.tween(t, .8, { Position = UDim2.fromOffset(x, y + 14), TextTransparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In, .25)
	local st = t:FindFirstChildOfClass("UIStroke")
	if st then T.tween(st, .8, { Transparency = 1 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In, .25) end
	task.delay(1.1, function() t:Destroy() end)
end

-- ---------------------------------------------------------------- REMOTES
function ctx.invoke(name, ...)
	if name ~= "PedirDados" and not ctx.data then ctx.toast("Carregando seus dados...", nil, "info"); return { ok = false } end
	if actionBusy[name] then return { ok = false, msg = "Aguarde..." } end
	local remote = R:FindFirstChild(name) or R:WaitForChild(name, 3)
	if not remote or not remote:IsA("RemoteFunction") then ctx.toast("Ação indisponível no momento", nil, "error"); return { ok = false } end
	actionBusy[name] = true
	if name == "Vender" then ctx.coinHold = os.clock() + 1.05 end
	local args = table.pack(...)
	local ok, res = pcall(function() return remote:InvokeServer(table.unpack(args, 1, args.n)) end)
	actionBusy[name] = nil
	if not ok then ctx.coinHold = nil; ctx.toast("Falha na conexão. Tente novamente.", nil, "error"); return { ok = false } end
	if name == "PedirDados" then return res end
	if type(res) ~= "table" then ctx.toast("Não foi possível concluir a ação", nil, "error"); return { ok = false } end
	if res.semAcesso then task.defer(function() ctx.accessPopup(res.semAcesso) end) end
	if not res.ok then
		ctx.coinHold = nil
		if name ~= "RolarGacha" then -- a invocacao trata os proprios avisos (cooldown entre giros)
			Som.tocar("ui_erro")
			ctx.toast(res.msg or "Não foi possível concluir a ação", nil, "error")
		end
		return res
	end
	if name == "Vender" then
		Som.venda(res.ganho, res.itens)
		if res.ganho then
			ctx.coinBurst(res.ganho)
			ctx.toast("+" .. T.format(res.ganho) .. " moedas  ·  " .. tostring(res.itens or 0) .. " minérios vendidos", nil, "reward")
		elseif res.msg then ctx.toast(res.msg, nil, "success") end
		return res
	end
	if name == "ComprarArea" then
		Som.tocar("area_nova")
		local a = Config.areaPorId(args[1])
		Notify.banner({ title = "ILHA DESBLOQUEADA!", subtitle = a and a.nome or "", color = P.teal, sound = false, big = true, duration = 2.4 })
	elseif name == "ComprarPicareta" or name == "ComprarMochila" then
		Som.tocar("upgrade")
		local def = name == "ComprarPicareta" and Config.picaretaPorId(args[1]) or Config.mochilaPorId(args[1])
		Notify.banner({ title = "UPGRADE!", subtitle = def and def.nome or "", color = P.gold, sound = false, duration = 2 })
	elseif name == "AlimentarPet" or name == "FundirHat" then
		if res.levelUp or (res.msg and res.msg:find("nivel")) then Som.tocar("level_up"); ctx.levelUp(res) else Som.tocar("ui_compra") end
	elseif name == "EquiparHat" or name == "EquiparPet" or name == "EquiparPicareta" or name == "EquiparMelhores" or name == "EquiparMelhoresPets" then
		Som.tocar("ui_equipar")
	elseif name == "ResgatarMissao" or name == "ResgatarDaily" or name == "ResgatarCodigo" then
		Som.tocar("reward_banner")
	elseif name ~= "RolarGacha" and name ~= "UITravel" and name ~= "ComprarRobux" then
		Som.tocar("ui_compra")
	end
	if res.msg and name ~= "RolarGacha" then ctx.toast(res.msg, nil, (name:find("Resgatar") or name:find("Comprar")) and "reward" or "success") end
	return res
end

-- fora do lobby: a opção GRÁTIS (teleporte até o Ignis) vem sempre primeiro
function ctx.accessPopup(nome)
	local passe = nome == "AutoSell" and Mon.passe("AutoSell")
	ctx.popup("Ignis está no lobby", function(p, w, h)
		local art = T.panel(p, "Art", (w - 120) / 2, 0, 120, 120, { bg = P.bg2, radius = 20, strokeColor = P.ember })
		T.icon(art, "forge", 10, 10, 100, 100)
		T.para(p, "Message", passe and "Venda com o Ignis usando o teleporte grátis, ou deixe o Auto Sell vender sozinho em qualquer ilha."
			or "Compras de equipamento são feitas com o Ignis. O teleporte até ele é grátis.", 0, 132, w, h - 200, 18, P.text2, T.CENTER, "body")
		local bw = passe and (w - 12) / 2 or w
		T.button(p, "GoIgnis", "Teleporte grátis", 0, h - 52, bw, 52, P.teal, function() closePopup(); ctx.travel("ignis") end)
		if passe then
			local b = T.button(p, "BuyPass", passe.id > 0 and ("Auto Sell  ·  R$ " .. passe.robux) or "Auto Sell (em breve)", bw + 12, h - 52, bw, 52, P.gold, function()
				if passe.id > 0 then ctx.invoke("ComprarRobux", "AutoSell") end
			end)
			T.setEnabled(b, passe.id > 0)
		end
	end, 560, 400, { color = P.ember })
end

-- ofertas enviadas pelo servidor (Starter no minuto 5, inventário cheio, mochila cheia)
local OFERTA_TEXTO = {
	Starter = { "Starter Pack", "Pack de Moedas M + Moedas x2 (30 min) + Sorte (15 min) + skin Kunai de Ignis.", "Starter", "Agora não", "store" },
	Inventario = { "Inventário cheio", "Funda hats repetidos para liberar espaço (grátis) ou aumente o inventário para 100.", "Inventario", "Fundir hats", "items" },
	AutoSell = { "Mochila cheia", "Teleporte grátis até o Ignis para vender, ou deixe o Auto Sell vender sozinho.", "AutoSell", "Teleporte grátis", "forge" },
}
local function ofertaPopup(oferta)
	local info = OFERTA_TEXTO[oferta]
	if not info or ctx.summonBusy then return end
	local item = Mon.passe(info[3]) or Mon.produto(info[3])
	local fechou = false
	local function fechar(acao)
		if fechou then return end
		fechou = true
		local ev = R:FindFirstChild("OfertaAcao")
		if ev then ev:FireServer("fechada", oferta) end
		closePopup()
		if acao == "Fundir hats" then ctx.collection = "hat"; ctx.open("Inventory")
		elseif acao == "Teleporte grátis" then ctx.travel("ignis") end
	end
	ctx.popup(info[1], function(p, w, h)
		local hero = T.panel(p, "Hero", 0, 0, w, 150, { bg = P.bg2, radius = 14, strokeColor = P.gold:Lerp(P.bg2, .4) })
		T.stripes(hero, "Energy", w - 260, 0, 240, 150, P.gold, .93)
		T.icon(hero, info[5], 16, 15, 120, 120)
		T.text(hero, "Name", item and item.nome or info[1], 150, 22, w - 170, 34, 26, P.text, T.LEFT, "display")
		T.para(hero, "Desc", info[2], 150, 60, w - 170, 76, 16, P.text2, T.LEFT, "body")
		if item and item.starter and item.valorSeparado then
			T.chip(p, "Deal", "Vendido separado: R$ " .. item.valorSeparado .. "   ·   aqui: R$ " .. item.robux, 0, 164, 30, P.success, { size = 14 })
		end
		local bw = (w - 12) / 2
		T.button(p, "Free", info[4], 0, h - 52, bw, 52, P.neutral, function() fechar(info[4]) end)
		local label = item and (item.id > 0 and (item.nome .. "  ·  R$ " .. item.robux) or (item.nome .. " (em breve)")) or "Loja"
		local buy = T.button(p, "Buy", label, bw + 12, h - 52, bw, 52, P.gold, function()
			if item and item.id > 0 then ctx.invoke("ComprarRobux", item.chave) end
			fechar(nil)
		end)
		if item and item.id <= 0 then T.setEnabled(buy, false) end
	end, 620, 330, { color = P.gold, modal = true })
end
task.spawn(function()
	local ev = R:WaitForChild("OfertaMostrar", 30)
	if ev then ev.OnClientEvent:Connect(function(oferta) ofertaPopup(oferta) end) end
end)

-- comprar a próxima área com moedas
function ctx.buyArea(areaId)
	local a = Config.areaPorId(areaId)
	if not a or not ctx.data then return end
	if ctx.data.areas[areaId] then ctx.travel("area", areaId); return end
	local prev = Config.areaPorId(areaId - 1)
	if prev and not ctx.data.areas[prev.id] then ctx.toast("Desbloqueie " .. prev.nome .. " antes", nil, "warning"); return end
	ctx.confirm("Desbloquear ilha", "Nova ilha com minérios, hats e missões próprias.", function()
		local res = ctx.invoke("ComprarArea", areaId)
		if res and res.ok then ctx.refresh() end
	end, {
		cost = a.custo, confirmText = "Desbloquear", tone = P.success, previewH = 120,
		preview = function(p, w)
			local f = T.frame(p, "Scene", 0, 0, w, 120, P.bg0, 0)
			T.corner(f, 12)
			local img = T.image(f, "Image", T.areaImage(a.id), 0, 0, w, 120)
			img.ScaleType = Enum.ScaleType.Crop
			T.corner(img, 12)
			local shade = T.frame(f, "Shade", 0, 0, w, 120, P.bg0, 0)
			T.corner(shade, 12)
			T.fade(shade, 90, .85, .15)
			local tema = Config.Temas[a.tema]
			T.text(f, "Name", a.nome, 16, 70, w - 32, 38, 28, WHITE, T.LEFT, "display", 1.8)
			T.text(f, "Tag", "ILHA " .. a.id .. "  ·  " .. T.upper(tema and tema.nome or ""), 16, 50, w - 32, 20, 13, tema and tema.cor or P.accent, T.LEFT, "title", 1.4)
		end,
	})
end

-- ---------------------------------------------------------------- JANELAS
function ctx.close()
	if not ctx.page then return end
	Som.tocar("ui_fechar")
	ctx.page = nil
	ctx.cancelSummon = true
	modalVersion += 1
	local old = modalLayer:GetChildren()
	for _, o in ipairs(old) do
		local sc = o:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .11, { Scale = .94 }, Enum.EasingStyle.Quad, Enum.EasingDirection.In) end
	end
	task.delay(.11, function() for _, o in ipairs(old) do o:Destroy() end end)
	window, body, searchBox = nil, nil, nil
	T.tween(dim, .14, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad)
	task.delay(.15, function() if not ctx.page then dim.Visible = false end end)
	closePopup()
	T.hideTooltip()
	updateBlur()
	hud.Visible = true
	screen:SetAttribute("OpenPage", "")
end

function ctx.open(page)
	if page == "Items" then ctx.collection = "hat"; page = "Inventory"
	elseif page == "Play" then page = "Areas" end
	if ctx.page == page then
		if page ~= "Inventory" then ctx.close(); return end
		ctx.search, ctx.rarity, ctx.selected = "", nil, nil
		drawWindow(false)
		return
	end
	local wasOpen = ctx.page ~= nil
	ctx.page = page
	ctx.search, ctx.rarity, ctx.selected = "", nil, nil
	ctx.cancelSummon = false
	closePopup()
	T.hideTooltip()
	dim.Visible = true
	if not wasOpen then
		dim.BackgroundTransparency = 1
		T.tween(dim, .18, { BackgroundTransparency = .45 }, Enum.EasingStyle.Quad)
	end
	hud.Visible = not (ctx.portrait or ctx.compact)
	-- o fundo escuro cobre o HUD antes do MouseLeave: devolve os botões ao tamanho normal
	local function resetHudScale()
		if not ctx.page then return end
		for _, o in ipairs(hud:GetDescendants()) do
			if o:IsA("UIScale") and o.Parent:IsA("GuiButton") then o.Scale = 1 end
		end
	end
	resetHudScale()
	task.delay(.3, resetHudScale) -- o "soltar" do clique ainda anima o botão por .24s
	screen:SetAttribute("OpenPage", page)
	Som.tocar("ui_abrir")
	drawWindow(not wasOpen)
	updateBlur()
end

function ctx.refresh()
	if pendingRefresh then return end
	pendingRefresh = true
	task.defer(function()
		pendingRefresh = false
		if ctx.page then drawHeader(); drawBody() end
		updateHUD()
	end)
end
function ctx.redrawBody() drawBody() end

function ctx.travel(action, id, keepMenu)
	if actionBusy.UITravel then return end
	Som.tocar("portal_saida")
	local result = ctx.invoke("UITravel", action, id)
	if result and result.ok then
		if keepMenu then
			ctx.bannerArea = id
			if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end
		else
			ctx.close()
		end
	end
end

-- ---------------------------------------------------------------- INVOCAÇÃO
local function showResults(results, count)
	if #results == 0 then return end
	local cols = math.min(#results, ctx.portrait and 2 or 5)
	local rows = math.ceil(#results / cols)
	local cw, ch, gap = 170, 232, 12
	local width = math.max(460, cols * cw + (cols - 1) * gap + 40)
	local height = math.min(virtualH - 40, rows * (ch + gap) + 150)
	local best
	for _, r in ipairs(results) do
		local rr = T.rar(r.raridade)
		if not best or rr.ordem > T.rar(best.raridade).ordem then best = r end
	end
	ctx.popup("Invocação concluída", function(p, w, h)
		local s = T.scroll(p, "Results", 0, 0, w, h - 66, P.violet)
		s.CanvasSize = UDim2.fromOffset(0, rows * (ch + gap))
		local margin = (w - (cols * cw + (cols - 1) * gap)) / 2
		local delay = .1
		for i, result in ipairs(results) do
			local def = Config.petPorId(result.petId)
			local r, key = T.rar(result.raridade)
			local cx = margin + ((i - 1) % cols) * (cw + gap) + cw / 2
			local cy = math.floor((i - 1) / cols) * (ch + gap) + ch / 2 + 2
			local card = T.panel(s, "Result_" .. i, 0, 0, cw, ch, { bg = P.bg2, radius = 14, strokeColor = r.cor, strokeWidth = 2 })
			card.AnchorPoint = Vector2.new(.5, .5)
			card.Position = UDim2.fromOffset(cx, cy)
			card.ClipsDescendants = true
			-- verso: só a cor da raridade (antecipação)
			local back = T.frame(card, "Back", 0, 0, cw, ch, r.cor, 0)
			T.corner(back, 14)
			T.gradient(back, r.cor:Lerp(P.bg0, .45), r.cor:Lerp(P.bg0, .8))
			T.stripes(back, "Energy", 0, 0, cw, ch, WHITE, .9)
			T.text(back, "Mark", "?", 0, 0, cw, ch, 64, r.cor:Lerp(WHITE, .5), T.CENTER, "display", 2)
			local sc = T.new("UIScale", { Scale = .001 }, card)
			local high = r.ordem >= 5
			if high then delay += .35 end
			local thisDelay = delay
			delay += .12
			task.delay(thisDelay, function()
				if not card.Parent then return end
				T.tween(sc, .22, { Scale = 1 }, Enum.EasingStyle.Back)
				task.delay(high and .45 or .16, function()
					if not card.Parent then return end
					back:Destroy()
					T.rarityFrame(card, key, { animated = r.ordem >= 5 })
					T.preview(card, "pet", result.petId, 8, 10, cw - 16, 150, false)
					local plate = T.frame(card, "Plate", 0, ch - 76, cw, 76, P.bg1, .1)
					T.text(plate, "Name", def and def.nome or result.nome or "", 8, 6, cw - 16, 28, 20, P.text, T.CENTER, "display", 1.4)
					local chip, chw = T.chip(plate, "Rarity", T.upper(r.nome), 0, 40, 26, r.cor, { size = 13 })
					chip.Position = UDim2.fromOffset((cw - chw) / 2, 40)
					if result.novo then
						local nc, nw = T.chip(card, "New", "NOVO!", 0, 8, 24, P.success, { solid = true, size = 13 })
						nc.Position = UDim2.fromOffset(cw - nw - 8, 8)
					end
					T.pop(card, high and 1.18 or 1.08, .3)
					Som.drop(result.raridade)
				end)
			end)
		end
		T.button(p, "Continue", "Continuar", 0, h - 54, (w - 12) / 2, 54, P.neutral, closePopup)
		T.button(p, "Again", "Invocar de novo " .. (count > 1 and ("x" .. count) or ""), (w - 12) / 2 + 12, h - 54, (w - 12) / 2, 54, P.violet, function()
			closePopup()
			task.defer(ctx.startSummon, count)
		end)
		if best and T.rar(best.raridade).ordem >= 5 then
			local bd = Config.petPorId(best.petId)
			local br = T.rar(best.raridade)
			task.delay(delay + .5, function()
				Notify.banner({ title = T.upper(br.nome) .. "!", subtitle = bd and bd.nome or "", color = br.cor, sound = false, big = br.ordem >= 6, duration = 2.2 })
			end)
		end
	end, width, height, { color = P.violet })
end

function ctx.nearBanner(areaId)
	local a = Config.areaPorId(areaId)
	local machines = workspace:FindFirstChild("Gachas")
	local machine = machines and a and machines:FindFirstChild("Gacha_" .. a.tema)
	if not machine then return false end
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local pad = machine:FindFirstChild("PadGacha")
	local pos = pad and pad.Position or machine:GetPivot().Position
	return (root.Position - pos).Magnitude <= 58
end

function ctx.startSummon(count)
	if ctx.summonBusy or not ctx.data then return end
	local areaId = ctx.bannerArea
	if not ctx.data.areas[areaId] then ctx.toast("Desbloqueie esta ilha primeiro", nil, "warning"); return end
	local cost = Config.Gachas[areaId].custo * (ctx.data.giroGratis and math.max(0, count - 1) or count)
	if ctx.data.moeda < cost then ctx.toast("Moedas insuficientes", nil, "error"); Som.tocar("ui_erro"); return end
	if not ctx.nearBanner(areaId) then
		ctx.toast("Viaje até o banner para invocar", nil, "info")
		return
	end
	ctx.summonBusy = true
	ctx.cancelSummon = false
	Som.tocar("invocar_inicio")
	local results = {}
	ctx.refresh()
	task.spawn(function()
		for i = 1, count do
			if ctx.cancelSummon then break end
			if ctx.onSummonProgress then pcall(ctx.onSummonProgress, i, count) end
			local result
			for tentativa = 1, 3 do
				result = ctx.invoke("RolarGacha", areaId)
				-- "Calma ai": cooldown do servidor entre giros. Espera e tenta de novo em vez de cortar a sequencia.
				if result and not result.ok and result.msg and result.msg:find("Calma") then task.wait(.35) else break end
			end
			if not result or not result.ok then
				if result and result.msg and not result.msg:find("Calma") then ctx.toast(result.msg, nil, "error") end
				break
			end
			table.insert(results, result)
			if i < count then task.wait(.66) end
		end
		ctx.summonBusy = false
		ctx.onSummonProgress = nil
		ctx.refresh()
		showResults(results, count)
	end)
end

function ctx.levelUp(res)
	Notify.levelUp(res.nivelAntes, res.nivel)
end

-- ---------------------------------------------------------------- CABEÇALHO / CORPO
local FULLSCREEN = { Inventory = true }
local function scrollKey(name)
	return table.concat({ ctx.page or "", ctx.collection or "", ctx.storeTab or "", tostring(ctx.questArea or ""),
		tostring(ctx.bannerArea or ""), ctx.eventsTab or "", name }, ":")
end

local function pageTitle()
	local info = PAGE[ctx.page] or PAGE.Quests
	local title, icon, col, sub = info.title, info.icon, info.color, info.sub
	local d = ctx.data
	if ctx.page == "Inventory" then
		if ctx.collection == "hat" then title, icon, col = "Itens", "items", P.info end
		if d then
			local total = ctx.collection == "hat" and (d.totalHats or 0) or (d.totalPets or 0)
			local cap = ctx.collection == "hat" and (d.capacidadeHats or 0) or (d.capacidadePets or 0)
			local eq = ctx.collection == "hat" and #(d.equipados or {}) or #(d.petsEquipados or {})
			local slots = ctx.collection == "hat" and d.slots or d.slotsPets
			sub = total .. " / " .. cap .. " no inventário   ·   " .. eq .. " / " .. tostring(slots or "?") .. " equipados"
		end
	elseif ctx.page == "Quests" and d then
		local ready = 0
		for _, lista in pairs(Config.Missoes) do
			for _, m in ipairs(lista) do
				local e = d.missoes and d.missoes[m.id]
				if e and e.p >= m.meta and not e.r and d.areas[m.area] then ready += 1 end
			end
		end
		sub = ready > 0 and (ready .. " missão(ões) pronta(s) para resgatar") or "Complete objetivos em cada ilha"
	elseif ctx.page == "Summon" then
		local a = Config.areaPorId(ctx.bannerArea or 1)
		sub = "Banner  ·  " .. (a and a.nome or "")
	end
	return title, icon, col, sub
end

local function tabsFor()
	if ctx.page == "Inventory" then
		return { { id = "pet", label = "Unidades", icon = "units" }, { id = "hat", label = "Itens", icon = "items" } },
			ctx.collection, ctx.collection == "hat" and P.info or P.accent,
			function(id) ctx.collection = id; ctx.selected = nil; ctx.rarity = nil; ctx.refresh() end
	elseif ctx.page == "Store" then
		return { { id = "Picaretas", label = "Picaretas", icon = "pickaxe" }, { id = "Mochilas", label = "Mochilas", icon = "items" }, { id = "Passes", label = "Passes", icon = "vip" } },
			ctx.storeTab, P.gold, function(id) ctx.storeTab = id; ctx.refresh() end
	elseif ctx.page == "Events" then
		local daily = ctx.data and ctx.data.daily
		return { { id = "Diario", label = "Diário", icon = "gift", badge = daily and daily.disponivel and "!" or nil }, { id = "Index", label = "Index", icon = "units" } },
			ctx.eventsTab, P.pink, function(id) ctx.eventsTab = id; ctx.refresh() end
	end
end

drawHeader = function()
	if not window then return 0 end
	local title, icon, col, sub = pageTitle()
	local banner = window:FindFirstChild("Banner")
	if banner then
		local tl = banner:FindFirstChild("Title")
		if tl then tl.Text = T.upper(title) end
		for _, o in ipairs(banner:GetChildren()) do if o:IsA("ImageLabel") and o.Name:sub(1, 5) == "Icon_" then o:Destroy() end end
		local bh = banner.Size.Y.Offset
		T.icon(banner, icon, 18, (bh - 46) / 2, 46, 46)
		local g = banner:FindFirstChildOfClass("UIGradient")
		if g then g.Color = ColorSequence.new(col:Lerp(WHITE, .25), col:Lerp(P.ink, .2)) end
	end
	local sl = window:FindFirstChild("Subtitle")
	if sl then sl.Text = sub or ""; sl.Visible = sub ~= nil end
	local st = window:FindFirstChildOfClass("UIStroke")
	if st then st.Color = col end
	local tabsRoot = window:FindFirstChild("Tabs")
	if tabsRoot then tabsRoot:Destroy() end
	local items, current, tcol, onPick = tabsFor()
	if not items then return 0 end
	local ww = window.Size.X.Offset
	local full = FULLSCREEN[ctx.page]
	local tw = math.min(#items * 190, ctx.portrait and ww - 40 or 560)
	local x = full and (ww - tw) / 2 or (ww - tw - 40)
	local y = full and 10 or 56
	tabsRoot = T.frame(window, "Tabs", x, y, tw, 52, nil, 1)
	T.tabs(tabsRoot, "Segment", 0, 0, tw, 52, items, current, tcol, onPick)
	return full and 0 or 22
end

drawBody = function()
	if not body or not ctx.page then return end
	for _, d in ipairs(body:GetDescendants()) do
		if d:IsA("ScrollingFrame") then ctx.scrollMemory[scrollKey(d.Name)] = d.CanvasPosition end
	end
	T.clear(body)
	if not ctx.data then
		local ring = T.frame(body, "Spinner", bodyW / 2 - 24, bodyH / 2 - 52, 48, 48, nil, 1)
		T.corner(ring, 24)
		local st = T.stroke(ring, P.accent, 5)
		T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 0), T.kp(.7, 1), T.kp(1, 1) }) }, st)
		local tw = game:GetService("TweenService"):Create(ring, TweenInfo.new(.9, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = 360 })
		tw:Play()
		ring.Destroying:Once(function() tw:Cancel() end)
		T.text(body, "Loading", "Carregando seus dados...", 20, bodyH / 2 + 8, bodyW - 40, 32, 20, P.text2, T.CENTER, "title")
		return
	end
	if ctx.page == "Inventory" then Inventory.render(ctx, body, bodyW, bodyH)
	else Menus.render(ctx, body, bodyW, bodyH) end
	local restore = {}
	for _, d in ipairs(body:GetDescendants()) do
		if d:IsA("ScrollingFrame") then
			local pos = ctx.scrollMemory[scrollKey(d.Name)]
			if pos then restore[d] = pos; d.CanvasPosition = pos end
		end
	end
	if next(restore) then
		task.defer(function() for s, pos in pairs(restore) do if s.Parent then s.CanvasPosition = pos end end end)
	end
end

local function windowRect()
	if ctx.portrait then
		local ww, wh = virtualW - 24, math.min(virtualH - 140, 1180)
		return ww, wh, 12, (virtualH - wh) / 2 + 10
	elseif ctx.compact then
		return virtualW - 24, virtualH - 16, 12, 8
	end
	local ww, wh = math.min(1220, virtualW - 120), math.min(740, virtualH - 90)
	return ww, wh, (virtualW - ww) / 2, (virtualH - wh) / 2 + 14
end

drawWindow = function(animate)
	if not ctx.page then return end
	modalVersion += 1
	T.clear(modalLayer)
	local _, _, col = pageTitle()
	local full = FULLSCREEN[ctx.page] and not ctx.portrait
	if full then
		-- tela cheia imersiva (Unidades / Itens)
		local ww, wh = virtualW, virtualH
		window = T.frame(modalLayer, "Window", 0, 0, ww, wh, P.bg1, .06)
		window.Active = true
		-- cobre a barra do Roblox e as laterais do notch fora do canvas (sem isso o mundo aparece nas bordas)
		local pad = 400
		local cover = T.frame(window, "EdgeCover", -pad, -pad, ww + pad * 2, wh + pad * 2, P.bg1, .06)
		cover.ZIndex = 0
		local wash = T.frame(window, "Wash", 0, 0, ww, math.floor(wh * .7), col, 0)
		T.fade(wash, 90, .78, 1)
		T.sparkles(window, ww, wh, 16, WHITE)
		T.stripes(window, "TopEnergy", 0, 0, ww, 6, col, .85, -62, 26)
		local bar = T.frame(window, "TopBar", 0, 0, ww, 74, P.bg0, .25)
		T.frame(window, "TopRule", 0, 74, ww, 2, col, .35)
		local banner = T.frame(window, "Banner", 20, 8, 340, 58, nil, 1)
		T.text(banner, "Title", "", 72, 0, 260, 58, 30, P.text, T.LEFT, "display")
		T.icon(banner, "units", 6, 6, 46, 46)
		T.text(window, "Subtitle", "", 26, 74, 520, 26, 15, P.text2, T.LEFT, "title")
		T.closeButton(window, ww - 92, 10, 62, ctx.close)
		local sw = 300
		local box = T.input(window, "Search", ww - 92 - sw - 20, 16, sw, 44, "Buscar...", ctx.search, { search = true })
		searchBox = box
		local serial = 0
		box:GetPropertyChangedSignal("Text"):Connect(function()
			ctx.search = box.Text
			serial += 1
			local version = serial
			task.delay(.14, function() if version == serial and box.Parent and body then drawBody() end end)
		end)
		hud.Visible = false
		drawHeader()
		bodyW, bodyH = ww - 48, wh - 112
		body = T.frame(window, "Body", 24, 104, bodyW, bodyH, nil, 1)
		drawBody()
		if animate then T.enter(window, .97, .24) end
		return
	end
	local ww, wh, wx, wy = windowRect()
	window = T.frame(modalLayer, "Window", wx, wy, ww, wh, P.bg1, 0)
	window.Active = true
	T.corner(window, 20)
	T.new("UIStroke", { Color = col, Thickness = 3.5, ApplyStrokeMode = Enum.ApplyStrokeMode.Border, LineJoinMode = Enum.LineJoinMode.Round }, window)
	local shadow = T.shadow(window, 20, 16, .45)
	local inner = T.frame(window, "InnerEdge", 5, 5, ww - 10, wh - 10, nil, 1)
	T.corner(inner, 16)
	T.stroke(inner, P.ink, 2)
	local top = T.frame(window, "TopWash", 4, 4, ww - 8, 120, col, 0)
	T.corner(top, 16)
	T.fade(top, 90, .82, 1)
	-- faixa inclinada do título, saindo da borda
	local bw = math.min(ctx.compact and 300 or 420, ww * .55)
	local bh = ctx.compact and 52 or 62
	local banner = T.slant(window, "Banner", -14, -24, bw, bh, col, { tilt = 18 })
	banner.ZIndex = 6
	T.stripes(banner, "Energy", bw * .45, 0, bw * .4, bh, WHITE, .94, -62, 5)
	T.text(banner, "Title", "", 72, 0, bw - 96, bh, ctx.compact and 24 or 30, P.text, T.LEFT, "display")
	T.icon(banner, "store", 18, (bh - 46) / 2, 46, 46)
	T.text(window, "Subtitle", "", 26, bh - 18, math.min(560, ww - 240), 24, 15, P.text2, T.LEFT, "title")
	T.closeButton(window, ww - 38, -32, 70, ctx.close)
	hud.Visible = not (ctx.portrait or ctx.compact)
	local extra = drawHeader()
	local headH = (ctx.compact and 62 or 96) + extra
	bodyW, bodyH = ww - 40, wh - headH - 26
	body = T.frame(window, "Body", 20, headH, bodyW, bodyH, nil, 1)
	drawBody()
	if animate then
		T.enter(window, .94, .28)
		T.enter(shadow, .94, .28)
	end
end

-- ---------------------------------------------------------------- HUD
local RAIL_LEFT = {
	{ id = "Store", label = "Loja", icon = "store", col = P.gold, tip = "Loja  ·  picaretas, mochilas e passes" },
	{ id = "Inventory", label = "Unidades", icon = "units", col = P.accent, key = "H", tip = "Suas unidades" },
	{ id = "Items", label = "Itens", icon = "items", col = P.info, key = "J", tip = "Seus hats" },
	{ id = "Summon", label = "Invocar", icon = "summon", col = P.violet, key = "G", tip = "Invocar personagens" },
}
local RAIL_RIGHT = {
	{ id = "Pickaxe", label = "Picareta", icon = "pickaxe", col = P.gold, tip = "Equipamento e upgrades" },
	{ id = "Quests", label = "Missões", icon = "quests", col = P.warning, tip = "Missões por ilha" },
	{ id = "Events", label = "Diário", icon = "events", col = P.pink, tip = "Recompensa diária e Index" },
	{ id = "Areas", label = "Viajar", icon = "areas", col = P.teal, tip = "Viajar entre ilhas" },
}

local function railTile(parent, it, x, y, size, showLabel)
	local b = T.new("TextButton", { Name = it.id, Text = "", AutoButtonColor = false, BackgroundColor3 = it.col:Lerp(P.ink, .78), BorderSizePixel = 0,
		Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size) }, parent)
	T.corner(b, 14)
	T.texture(b, "pattern", .88, it.col:Lerp(WHITE, .2), 80)
	local glow = T.frame(b, "Glow", 0, 0, size, size, it.col, 0)
	T.corner(glow, 14)
	T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.55, .92), T.kp(1, .55) }) }, glow)
	local st = T.new("UIStroke", { Color = it.col, Thickness = 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border, LineJoinMode = Enum.LineJoinMode.Round }, b)
	T.new("UIGradient", { Rotation = 90, Color = ColorSequence.new(it.col:Lerp(WHITE, .4), it.col:Lerp(P.ink, .25)) }, st)
	local isz = math.floor(size * (showLabel and .58 or .72))
	local holder = T.frame(b, "Art", (size - isz) / 2, showLabel and 6 or (size - isz) / 2, isz, isz, nil, 1)
	local icon = T.icon(holder, it.icon, 0, 0, isz, isz)
	if showLabel then T.text(b, "Label", it.label, 2, size - 24, size - 4, 20, 14, P.text, T.CENTER, "title") end
	local sc = T.new("UIScale", {}, b)
	b.MouseEnter:Connect(function()
		T.tween(sc, .16, { Scale = 1.09 }, Enum.EasingStyle.Back)
		T.tween(holder, .16, { Rotation = -6 }, Enum.EasingStyle.Back)
		T.som("ui_hover")
	end)
	b.MouseLeave:Connect(function()
		T.tween(sc, .14, { Scale = 1 }, Enum.EasingStyle.Quad)
		T.tween(holder, .14, { Rotation = 0 }, Enum.EasingStyle.Quad)
	end)
	b.MouseButton1Down:Connect(function() T.tween(sc, .06, { Scale = .93 }, Enum.EasingStyle.Quad) end)
	b.MouseButton1Up:Connect(function() T.tween(sc, .24, { Scale = 1.09 }, Enum.EasingStyle.Back) end)
	b.Activated:Connect(function()
		T.som("ui_click")
		if it.id == "Inventory" then ctx.collection = "pet"; ctx.open("Inventory")
		elseif it.id == "Pickaxe" then ctx.storeTab = "Picaretas"; ctx.open("Store")
		else ctx.open(it.id) end
	end)
	T.hint(b, it.tip .. (it.key and ("   <font color=\"#847ab8\">[" .. it.key .. "]</font>") or ""), it.side or "right")
	return b, holder
end

drawHUD = function()
	T.clear(hud)
	hudRefs = {}
	local compact, portrait = ctx.compact, ctx.portrait
	local tile = compact and 56 or 78
	local gap = compact and 8 or 10
	local topY = compact and 48 or 88

	-- buffs ativos (canto superior esquerdo)
	hudRefs.buffs = T.frame(hud, "Buffs", 16, 12, 560, 32, nil, 1)
	hudRefs.buffKeys = ""

	-- colunas de navegação
	hudRefs.rail = {}
	for i, it in ipairs(RAIL_LEFT) do
		local b = railTile(hud, it, 16, topY + (i - 1) * (tile + gap), tile, not compact)
		hudRefs.rail[it.id] = b
	end
	for i, it in ipairs(RAIL_RIGHT) do
		it = table.clone(it)
		it.side = "left"
		local b, holder = railTile(hud, it, virtualW - 16 - tile, topY + (i - 1) * (tile + gap), tile, not compact)
		hudRefs.rail[it.id] = b
		if it.id == "Pickaxe" then hudRefs.pickArt = holder end
	end

	-- barra da ilha atual + missão (topo centro)
	local tw = math.min(660, virtualW - 2 * (tile + 60))
	local tracker = T.new("TextButton", { Name = "Tracker", Text = "", AutoButtonColor = false, BackgroundColor3 = P.bg0, BackgroundTransparency = .2,
		BorderSizePixel = 0, Position = UDim2.fromOffset((virtualW - tw) / 2, 12), Size = UDim2.fromOffset(tw, 38) }, hud)
	T.corner(tracker, 19)
	local tst = T.stroke(tracker, P.lineSoft, 2.5)
	hudRefs.trackerStroke = tst
	hudRefs.areaName = T.text(tracker, "Area", "[PRAÇA CENTRAL]", 18, 0, 240, 38, 16, P.accent, T.LEFT, "title")
	hudRefs.questText = T.text(tracker, "Quest", "", 250, 0, tw - 250 - 190, 38, 15, P.text2, T.LEFT, "title")
	hudRefs.questBar = T.progress(tracker, "QuestBar", tw - 178, 9, 160, 20, 0, P.warning)
	hudRefs.questCount = T.text(hudRefs.questBar, "Count", "", 0, 0, 160, 20, 13, P.text, T.CENTER, "title")
	hudRefs.questCount.ZIndex = 3
	local tsc = T.new("UIScale", {}, tracker)
	tracker.MouseEnter:Connect(function() tst.Color = P.warning; T.tween(tsc, .12, { Scale = 1.02 }, Enum.EasingStyle.Quad) end)
	tracker.MouseLeave:Connect(function() tst.Color = hudRefs.trackerReady and P.success or P.lineSoft; T.tween(tsc, .12, { Scale = 1 }, Enum.EasingStyle.Quad) end)
	tracker.Activated:Connect(function() T.som("ui_click"); ctx.questArea = nil; ctx.open("Quests") end)
	T.hint(tracker, "Missão atual  ·  clique para abrir", "below")

	-- ===== base: moedas → unidades equipadas → mochila
	local slot = compact and 58 or 74
	local sgap = 8
	local hbW = 6 * slot + 5 * sgap
	local bagW = math.min(760, math.max(hbW + 120, virtualW * .46))
	local bagY = virtualH - 16 - 28
	local hotY = bagY - 12 - slot
	local curY = hotY - 8 - 44

	-- linha de moedas / poder / config
	local row = T.frame(hud, "Currency", (virtualW - bagW) / 2, curY, bagW, 44, nil, 1)
	hudRefs.wallet = row
	-- pílulas escuras: leitura garantida mesmo sobre chão claro
	local function pill(name, x, w, col)
		local f = T.frame(row, name, x, 3, w, 38, P.bg0, .3)
		T.corner(f, 19)
		T.stroke(f, col:Lerp(P.bg0, .45), 2)
		return f
	end
	pill("CoinsPill", 18, 220, P.gold)
	pill("PowerPill", 272, 190, P.danger)
	T.icon(row, "coins", 0, 0, 44, 44)
	hudRefs.coins = T.text(row, "Coins", ctx.shownCoins and T.format(ctx.shownCoins) or "0", 50, 0, 178, 44, 28, P.gold, T.LEFT, "display")
	T.statIcon(row, "dano", 254, 0, 44, 44)
	hudRefs.power = T.text(row, "Power", "0", 304, 0, 150, 44, 24, P.text, T.LEFT, "display")
	T.hint(row, "<b>Poder</b> = dano por golpe  ·  <b>Moedas</b> = venda de minérios", "above")
	local gear = T.iconButton(hud, "Settings", "settings", (virtualW + bagW) / 2 - 44, curY, 44, function() ctx.open("Settings") end, { iconScale = .7, bg = P.bg2 })
	T.hint(gear, "Configurações e códigos", "above")

	-- unidades equipadas
	local hotbar = T.frame(hud, "Hotbar", (virtualW - hbW) / 2, hotY, hbW, slot, nil, 1)
	hudRefs.hotbar = hotbar

	-- mochila (barra longa da base)
	local bag = T.frame(hud, "Bag", (virtualW - bagW) / 2, bagY, bagW, 28, nil, 1)
	hudRefs.bagPanel = bag
	hudRefs.bagTrack = T.progress(bag, "Track", 0, 0, bagW, 28, 0, P.accent, { segments = 6 })
	T.statIcon(bag, "capacidade", -34, -4, 36, 36)
	hudRefs.bag = T.text(hudRefs.bagTrack, "Count", "MOCHILA 0 / 0", 0, 0, bagW, 28, 16, P.text, T.CENTER, "title")
	local sellX = (compact or portrait) and ((virtualW - bagW) / 2 - 170) or ((virtualW + bagW) / 2 + 10)
	local sell = T.button(hud, "SellShortcut", "Vender", sellX, bagY - 9, 120, 46, P.neutral, function() ctx.open("Forge") end, { icon = "forge", size = 17 })
	T.hint(sell, "Vender minérios com o Ignis", "above")
	hudRefs.sell = sell
	hudRefs.signature = nil
	updateHUD()
end

local function nextPickaxe(d)
	local idx = 1
	for i, p in ipairs(Config.Picaretas) do if p.id == d.picareta then idx = i end end
	for i = idx + 1, #Config.Picaretas do
		local p = Config.Picaretas[i]
		if not (d.picaretasCompradas and d.picaretasCompradas[p.id]) then return p, i end
	end
end
local function nextBackpack(d)
	local idx = 1
	for i, m in ipairs(Config.Mochilas) do if m.id == d.mochilaTier then idx = i end end
	return Config.Mochilas[idx + 1]
end
local function nextArea(d)
	for _, a in ipairs(Config.Areas) do if not d.areas[a.id] then return a end end
end
ctx.nextPickaxe, ctx.nextBackpack, ctx.nextArea = nextPickaxe, nextBackpack, nextArea

local function readyQuests(d, areaId)
	local n = 0
	for _, m in ipairs(Config.Missoes[areaId] or {}) do
		local e = d.missoes and d.missoes[m.id]
		if e and e.p >= m.meta and not e.r then n += 1 end
	end
	return n
end

local function setBadge(target, value, col)
	if not target then return end
	local old = target:FindFirstChild("Badge")
	if old then old:Destroy() end
	if value and value ~= 0 and value ~= "" then
		local b = T.badge(target, target.Size.X.Offset - 20, -10, value, col)
		T.pop(b, 1.35, .32)
	end
end

local function inventorySignature(d)
	local list = { d.picareta or "", d.mochilaTier or "", table.concat(d.equipados or {}, ","), table.concat(d.petsEquipados or {}, ",") }
	for uid, o in pairs(d.petsInv or {}) do table.insert(list, uid .. ":" .. o.id .. ":" .. o.nivel .. ":" .. tostring(o.xp) .. ":" .. tostring(o.apelido)) end
	for uid, o in pairs(d.hatsInv or {}) do table.insert(list, uid .. ":" .. o.id .. ":" .. o.nivel .. ":" .. tostring(o.xp)) end
	table.sort(list)
	return table.concat(list, "|")
end

local function renderBuffs()
	local root = hudRefs.buffs
	local d = ctx.data
	if not root or not d then return false end
	local elapsed = os.clock() - (ctx.dataClock or os.clock())
	local b = d.boosts or {}
	local list = {}
	local coinsLeft = (b.moedas or 0) - elapsed
	local luckLeft = (b.sorte or 0) - elapsed
	if coinsLeft > 0 then table.insert(list, { "BoostCoins", "x2 MOEDAS  " .. T.clock(coinsLeft), P.gold, "coins", "Moedas x2 nas vendas" }) end
	if luckLeft > 0 then table.insert(list, { "BoostLuck", "SORTE  " .. T.clock(luckLeft), P.success, "potion", "Chance de Épico ou melhor x1,5" }) end
	if (d.friendBoost or 0) > 0 then table.insert(list, { "Friends", "AMIGOS +" .. math.floor(d.friendBoost * 100 + .5) .. "%", P.accent, "gift", "Bônus por amigos ativos no servidor" }) end
	if d.passes and d.passes.VIP then table.insert(list, { "VIP", "VIP", P.gold, "vip", "+10% de moedas nas vendas" }) end
	local keys = {}
	for _, it in ipairs(list) do table.insert(keys, it[1]) end
	local sig = table.concat(keys, ",")
	if sig == hudRefs.buffKeys then
		for _, it in ipairs(list) do
			local chip = root:FindFirstChild(it[1])
			local label = chip and chip:FindFirstChild("Label")
			if label then label.Text = it[2] end
		end
	else
		hudRefs.buffKeys = sig
		T.clear(root)
		local x = 0
		for _, it in ipairs(list) do
			local chip, w = T.chip(root, it[1], it[2], x, 0, 32, it[3], { icon = it[4], size = 15, w = it[1]:find("Boost") and 190 or nil })
			T.hint(chip, it[5], "below")
			x += w + 8
		end
	end
	return coinsLeft > 0 or luckLeft > 0
end

task.spawn(function()
	while true do
		task.wait(1)
		if ctx.data and hudRefs.buffs and hudRefs.buffs.Parent then renderBuffs() end
	end
end)

updateHUD = function()
	local d = ctx.data
	if not d or not hudRefs.coins then return end
	local coins = d.moeda or 0
	if ctx.shownCoins == nil then
		hudRefs.coins.Text = T.format(coins)
	elseif coins ~= ctx.shownCoins then
		local from, to = ctx.shownCoins, coins
		local hold = ctx.coinHold and math.max(0, ctx.coinHold - os.clock()) or 0
		task.delay(to > from and hold or 0, function()
			if not hudRefs.coins or not hudRefs.coins.Parent then return end
			T.countTo(hudRefs.coins, from, to, T.format, .55)
			floatDelta((to > from and "+" or "-") .. T.format(math.abs(to - from)), to > from and P.success or P.danger)
			T.pop(hudRefs.coins, to > from and 1.12 or 1.05, .3)
		end)
	end
	ctx.shownCoins = coins
	if hudRefs.power then hudRefs.power.Text = T.format(d.dano or 0) end

	-- mochila
	local frac = math.clamp((d.carregado or 0) / math.max(1, d.capacidade or 1), 0, 1)
	local col = frac >= 1 and P.danger or (frac >= .85 and P.warning or P.accent)
	T.setProgress(hudRefs.bagTrack, frac, col, .35)
	hudRefs.bag.Text = "MOCHILA  " .. T.format(d.carregado or 0) .. " / " .. T.format(d.capacidade or 0)
	local full = frac >= .85
	if hudRefs.sellFull ~= full then
		hudRefs.sellFull = full
		T.setTone(hudRefs.sell, full and P.success or P.neutral)
		if full then T.pop(hudRefs.sell, 1.18, .4) end
	end
	if frac >= 1 and not ctx.bagWasFull then T.shake(hudRefs.bagPanel, 8) end
	ctx.bagWasFull = frac >= 1

	-- ilha + missão em destaque
	local areaId = player:GetAttribute("CurrentAreaId") or 0
	local area = Config.areaPorId(areaId)
	local tema = area and Config.Temas[area.tema]
	hudRefs.areaName.Text = "[" .. T.upper(area and area.nome or "Praça central") .. "]"
	hudRefs.areaName.TextColor3 = tema and tema.cor or P.accent
	local questArea = (area and d.areas[area.id]) and area.id or nil
	if not questArea then
		for _, a in ipairs(Config.Areas) do if d.areas[a.id] then questArea = a.id end end
	end
	local shown, ready = nil, false
	for _, m in ipairs(Config.Missoes[questArea or 1] or {}) do
		local e = d.missoes and d.missoes[m.id] or { p = 0, r = false }
		if not e.r then
			if e.p >= m.meta then shown, ready = { m, e }, true; break end
			shown = shown or { m, e }
		end
	end
	hudRefs.trackerReady = ready
	if shown then
		local m, e = shown[1], shown[2]
		hudRefs.questText.Text = ready and "✓ MISSÃO PRONTA — RESGATAR" or m.texto
		hudRefs.questText.TextColor3 = ready and P.success or P.text2
		T.setProgress(hudRefs.questBar, e.p / m.meta, ready and P.success or P.warning, .35)
		hudRefs.questCount.Text = T.format(math.min(e.p, m.meta)) .. " / " .. T.format(m.meta)
		hudRefs.questBar.Visible = true
	else
		hudRefs.questText.Text = "Missões desta ilha concluídas"
		hudRefs.questText.TextColor3 = P.text3
		hudRefs.questBar.Visible = false
	end
	hudRefs.trackerStroke.Color = ready and P.success or P.lineSoft

	-- badges
	local totalReady = 0
	for _, a in ipairs(Config.Areas) do if d.areas[a.id] then totalReady += readyQuests(d, a.id) end end
	setBadge(hudRefs.rail.Quests, totalReady, P.danger)
	setBadge(hudRefs.rail.Events, d.daily and d.daily.disponivel and "!" or nil, P.danger)
	local na = nextArea(d)
	setBadge(hudRefs.rail.Areas, na and d.moeda >= na.custo and "!" or nil, P.success)
	local np = nextPickaxe(d)
	local nb = nextBackpack(d)
	setBadge(hudRefs.rail.Pickaxe, np and d.moeda >= np.custo and "▲" or nil, P.success)
	setBadge(hudRefs.rail.Store, ((np and d.moeda >= np.custo) or (nb and d.moeda >= nb.custo)) and "▲" or nil, P.success)

	-- hotbar + picareta (só quando algo muda)
	local signature = inventorySignature(d) .. "|" .. tostring(np and d.moeda >= np.custo)
	if hudRefs.signature == signature then renderBuffs(); return end
	hudRefs.signature = signature
	renderBuffs()
	if hudRefs.pickArt then
		T.clear(hudRefs.pickArt)
		local size = hudRefs.pickArt.Size.X.Offset
		T.preview(hudRefs.pickArt, "pickaxe", d.picareta, 0, 0, size, size, false)
	end
	local hotbar = hudRefs.hotbar
	T.clear(hotbar)
	local slot = hotbar.Size.Y.Offset
	for i = 1, 6 do
		local uid = d.petsEquipados and d.petsEquipados[i]
		local inst = uid and d.petsInv and d.petsInv[uid]
		local def = inst and Config.petPorId(inst.id)
		local holder = T.new("TextButton", { Name = "Slot" .. i, Text = "", AutoButtonColor = false, BackgroundTransparency = 1, BorderSizePixel = 0,
			Position = UDim2.fromOffset((i - 1) * (slot + 8), 0), Size = UDim2.fromOffset(slot, slot) }, hotbar)
		if def then
			local tile, r = T.tile(holder, "Tile", 0, 0, slot, slot, def.raridade, { radius = 12 })
			local arte = Config.PetArte and Config.PetArte[def.id]
			if arte then
				local img = T.image(tile, "Portrait", arte.busto or arte.corpo, 3, 3, slot - 6, slot - 6)
				img.ScaleType = Enum.ScaleType.Crop
				T.corner(img, 9)
			else
				T.preview(tile, "pet", def.id, 3, 3, slot - 6, slot - 6, false)
			end
			T.text(tile, "Level", "Lv." .. tostring(inst.nivel or 1), 4, 2, slot - 8, 18, 13, WHITE, T.LEFT, "title")
			T.hint(holder, "<b>" .. ((inst.apelido and inst.apelido ~= "") and inst.apelido or def.nome) .. "</b>  <font color=\"#" .. r.cor:ToHex() .. "\">" .. r.nome .. "</font>\nDano +" .. T.format(math.floor(Config.petBonusDano(def, inst.nivel or 1) * 1000 + .5) / 10) .. "%", "above")
		else
			local empty = T.frame(holder, "Empty", 0, 0, slot, slot, P.bg0, .35)
			T.corner(empty, 12)
			T.stroke(empty, P.lineSoft, 2.5)
			T.text(empty, "Plus", "+", 0, 0, slot, slot, 28, P.text3, T.CENTER, "title")
			T.hint(holder, "Slot livre  ·  equipe uma unidade", "above")
		end
		local sc = T.new("UIScale", {}, holder)
		holder.MouseEnter:Connect(function() T.tween(sc, .14, { Scale = 1.09 }, Enum.EasingStyle.Back) end)
		holder.MouseLeave:Connect(function() T.tween(sc, .12, { Scale = 1 }, Enum.EasingStyle.Quad) end)
		holder.Activated:Connect(function()
			T.som("ui_click")
			ctx.collection = "pet"
			ctx.open("Inventory")
			if uid then ctx.selected = uid; drawBody() end
		end)
	end
end

-- ---------------------------------------------------------------- DADOS
local function barrier(part)
	if not ctx.data or not part:IsA("BasePart") or part.Name ~= "Barreira" then return end
	local id = part:GetAttribute("LiberaComArea")
	local unlocked = id and ctx.data.areas[id] == true
	part.CanCollide = not unlocked
	part.Transparency = unlocked and .9 or .65
end

local function acceptData(data)
	if type(data) ~= "table" or type(data.hatsInv) ~= "table" or type(data.petsInv) ~= "table" then return end
	ctx.data = data
	ctx.dataClock = os.clock()
	hydrated = true
	updateHUD()
	local areas = workspace:FindFirstChild("Areas")
	if areas then for _, d in ipairs(areas:GetDescendants()) do if d.Name == "Barreira" then barrier(d) end end end
	local signature = inventorySignature(data)
	if signature ~= lastInventorySignature then
		lastInventorySignature = signature
		if ctx.page and not ctx.summonBusy then ctx.refresh() end
	elseif ctx.page == "Forge" or ctx.page == "Quests" or ctx.page == "Events" or ctx.page == "Store" or ctx.page == "Areas" then
		if not ctx.summonBusy then ctx.refresh() end
	end
end
R.AtualizarDados.OnClientEvent:Connect(function(data) pushVersion += 1; acceptData(data) end)
workspace.DescendantAdded:Connect(function(d) if d.Name == "Barreira" then task.defer(barrier, d) end end)

-- nome do minério da ilha atual (feed de coleta)
local function oreName(variante)
	local a = Config.areaPorId(player:GetAttribute("CurrentAreaId") or 0)
	local info = a and Config.infoMinerio(a.tema .. "_" .. (variante or "comum"))
	return info and info.nome or "Minério"
end

R.FeedbackMina.OnClientEvent:Connect(function(info)
	if type(info) ~= "table" then return end
	if info.tipo == "hat" then
		local r = T.rar(info.raridade)
		if info.novo then
			Notify.reveal({ kind = "hat", id = info.id, name = info.texto, rarity = info.raridade, tag = "NOVO HAT!",
				subtitle = "Nível " .. tostring(info.nivel or 1) .. "  ·  entra no Index da coleção" })
		else
			Notify.feed("hat:" .. tostring(info.id), info.texto or "Hat", r.cor, 1, { icon = "items" })
			if r.ordem >= 4 then
				Notify.banner({ title = T.upper(r.nome) .. "!", subtitle = info.texto, color = r.cor, sound = false, big = r.ordem >= 6, duration = 1.8 })
			end
		end
	elseif info.tipo == "quebrou" then
		if info.chefe then
			Notify.banner({ title = "CHEFE DERROTADO!", subtitle = "Recompensa para todos que ajudaram", color = P.danger, big = true, duration = 2.4 })
		else
			local r = T.rar(info.variante)
			Notify.feed("ore:" .. tostring(info.variante), oreName(info.variante), r.cor, 1, { ore = info.variante })
			if r.ordem >= 5 then Notify.banner({ title = "MINÉRIO " .. T.upper(r.nome) .. "!", subtitle = oreName(info.variante), color = r.cor, sound = false, duration = 1.6 }) end
			if hudRefs.bagPanel then T.pop(hudRefs.bagPanel, 1.03, .2) end
		end
	elseif info.tipo == "cheia" then
		ctx.toast(info.texto, nil, "warning")
		if hudRefs.bagPanel then T.shake(hudRefs.bagPanel, 7) end
	elseif info.tipo == "bloqueada" then
		ctx.toast(info.texto, nil, "warning")
	elseif info.tipo == "area" then
		local texto = tostring(info.texto or "")
		ctx.toast(texto, nil, (texto:find("moedas") or texto:find("Compra")) and "reward" or "info")
	elseif info.tipo == "comprarArea" then
		ctx.buyArea(info.areaId)
	end
end)
R.AbrirIgnis.OnClientEvent:Connect(function() if ctx.page ~= "Forge" then ctx.open("Forge") end end)
R.AbrirLoja.OnClientEvent:Connect(function() ctx.storeTab = "Mochilas"; if ctx.page ~= "Store" then ctx.open("Store") else ctx.refresh() end end)
R.AbrirGacha.OnClientEvent:Connect(function(id)
	if Config.Gachas[id] then ctx.bannerArea = id; if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end end
end)
player:GetAttributeChangedSignal("CurrentAreaId"):Connect(function()
	Som.tocar("portal_chegada")
	local id = player:GetAttribute("CurrentAreaId")
	local a = id and Config.areaPorId(id)
	local tema = a and Config.Temas[a.tema]
	Notify.banner({ title = a and a.nome or "Praça Central", subtitle = a and ("ILHA " .. a.id .. "  ·  " .. T.upper(tema.nome)) or "LOBBY  ·  IGNIS, BANNERS E PORTAIS",
		color = tema and tema.cor or P.accent, sound = false, duration = 1.8 })
	updateHUD()
end)
player:GetAttributeChangedSignal("ExpeditionBlurEnabled"):Connect(updateBlur)

-- ---------------------------------------------------------------- RESOLUÇÃO
local function resize()
	local v = screen.AbsoluteSize
	if v.X < 1 or v.Y < 1 then return end
	ctx.portrait = v.X < v.Y * .85
	ctx.compact = not ctx.portrait and v.Y < 560
	local s
	if ctx.portrait then s = math.clamp(v.X / 760, .4, 1.25)
	elseif ctx.compact then s = math.min(v.X / 1180, v.Y / 500)
	else s = math.clamp(math.min(v.X / BASE_W, v.Y / BASE_H), .5, 1.45) end
	scale.Scale = s
	T.uiScale = s
	virtualW, virtualH = v.X / s, v.Y / s
	canvas.Size = UDim2.fromOffset(virtualW, virtualH)
	for _, layer in ipairs({ hud, modalLayer, toastLayer, popupLayer, dialogHost, tipLayer }) do
		layer.Size = UDim2.fromOffset(virtualW, virtualH)
	end
	Notify.toastTop = ctx.portrait and 176 or 84
	drawHUD()
	hud.Visible = not ((ctx.portrait or ctx.compact) and ctx.page ~= nil)
	if ctx.page then drawWindow(false) end
	closePopup()
	Notify.relayout()
end
screen:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)

Input.InputBegan:Connect(function(input, processed)
	if processed or Input:GetFocusedTextBox() then return end
	local key = input.KeyCode
	if key == Enum.KeyCode.Escape then
		if popupOpen then closePopup() elseif ctx.page then ctx.close() end
	elseif key == Enum.KeyCode.H or key == Enum.KeyCode.B then ctx.collection = "pet"; ctx.open("Inventory")
	elseif key == Enum.KeyCode.J then ctx.open("Items")
	elseif key == Enum.KeyCode.G then ctx.open("Summon") end
end)
screen.Destroying:Connect(function() blur:Destroy() end)
resize()

task.spawn(function()
	for attempt = 1, 8 do
		if hydrated then break end
		local version = pushVersion
		local ok, data = pcall(function() return R.PedirDados:InvokeServer() end)
		if ok and version == pushVersion and data then acceptData(data) end
		if not hydrated then task.wait(.5 + attempt * .15) end
	end
	if not hydrated then ctx.toast("Não foi possível carregar seus dados. Reconecte ao jogo.", nil, "error") end
end)
task.spawn(function()
	local images = { T.Assets.icons, T.Assets.header, T.Assets.lobby }
	for _, id in ipairs(T.Assets.areas) do table.insert(images, id) end
	pcall(function() game:GetService("ContentProvider"):PreloadAsync(images) end)
end)

