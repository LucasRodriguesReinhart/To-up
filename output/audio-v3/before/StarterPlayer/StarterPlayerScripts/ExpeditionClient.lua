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
local GuiService=game:GetService("GuiService")
local oldScreen=pg:FindFirstChild("ExpeditionUI")
if oldScreen then oldScreen:Destroy() end
local screen = T.new("ScreenGui", { Name = "ExpeditionUI", ResetOnSpawn = false, DisplayOrder = 25, IgnoreGuiInset = false, ClipToDeviceSafeArea = true,
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
local popupOnClose=nil
local popupFocus=nil
local pendingOffer=nil
local alive=true
local connections={}
local function connect(signal,fn) local c=signal:Connect(fn);table.insert(connections,c);return c end
screen:SetAttribute("OpenPage","")
screen:SetAttribute("PopupOpen",false)
ctx.T, ctx.Notify = T, Notify

T.setTooltipLayer(tipLayer, function() return scale.Scale end)
-- com uma janela aberta o HUD fica atrás do fundo escuro: nada de dica dele aparecendo por cima
T.setTooltipGuard(function(o) return not (ctx.page and o:IsDescendantOf(hud)) end)
Notify.init(toastLayer, popupLayer, function() return virtualW, virtualH end)
Notify.feedAnchor = function() return virtualW - 24, virtualH - (ctx.portrait and 272 or 128) end

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
	local amount = ctx.page and player:GetAttribute("ExpeditionBlurEnabled") ~= false and 6 or 0
	T.tween(blur, .2, { Size = amount }, Enum.EasingStyle.Quad)
end

-- ---------------------------------------------------------------- POPUPS
closePopup = function()
	if not popupOpen then return end
	popupOpen = false
	screen:SetAttribute("PopupOpen",false)
	if popupOnClose then local fn=popupOnClose;popupOnClose=nil;pcall(fn) end
	if popupFocus and popupFocus.Parent then GuiService.SelectedObject=popupFocus end
	popupFocus=nil
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
	screen:SetAttribute("PopupOpen",true)
	popupOnClose=opts.onClose
	popupFocus=GuiService.SelectedObject
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
	T.enter(box, .97, .18)
	if Input.GamepadEnabled and not Input.MouseEnabled then task.defer(function() if box.Parent then GuiService.SelectedObject=box:FindFirstChildWhichIsA("GuiButton",true) end end) end
	T.enter(shadow, .97, .18)
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
	if not wallet or not wallet.Parent or not T.motionEnabled() then return end
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
		if res.levelUp and res.nivelAntes and res.nivel then Som.tocar("level_up"); ctx.levelUp(res) else Som.tocar("ui_compra") end
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
	if not info then return end
	if ctx.summonBusy or popupOpen or ctx.page or player:GetAttribute("RevealOpen") or player:GetAttribute("TravelTransition") then pendingOffer=oferta;return end
	local item = Mon.passe(info[3]) or Mon.produto(info[3])
	if not item or item.id<=0 then return end
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
	if ev then connect(ev.OnClientEvent,function(oferta) ofertaPopup(oferta) end) end
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
	GuiService.SelectedObject=nil
end

function ctx.open(page)
	if player:GetAttribute("RevealOpen") or player:GetAttribute("TravelTransition") or player:GetAttribute("AreaTransition")~=nil then return end
	if page == "Items" then ctx.collection = "hat"; page = "Inventory"
	elseif page == "Play" then page = "Areas" end
	if ctx.page == page then
		if page ~= "Inventory" then ctx.close(); return end
		ctx.search, ctx.rarity, ctx.selected = "", nil, nil
		drawWindow(false)
		return
	end
	if not PAGE[page] then return end
	local wasOpen = ctx.page ~= nil
	ctx.page = page
	ctx.search, ctx.rarity, ctx.selected = "", nil, nil
	if ctx.summonBusy then ctx.cancelSummon = true end
	closePopup()
	T.hideTooltip()
	dim.Visible = true
	if not wasOpen then
		dim.BackgroundTransparency = 1
		T.tween(dim, .18, { BackgroundTransparency = .58 }, Enum.EasingStyle.Quad)
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
dim.Activated:Connect(function() if popupOpen then closePopup() else ctx.close() end end)

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

function ctx.showLastSummon()
	if ctx.lastSummonResults then showResults(ctx.lastSummonResults,ctx.lastSummonCount or #ctx.lastSummonResults) end
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
		ctx.lastSummonResults,ctx.lastSummonCount=results,count
		if ctx.page=="Summon" and not ctx.cancelSummon then showResults(results,count)
		elseif #results>0 then ctx.toast(tostring(#results).." unidade(s) recebida(s). Veja o último resultado em Invocar.",nil,"reward") end
	end)
end

function ctx.levelUp(res)
	Notify.levelUp(res.nivelAntes, res.nivel)
end

-- ---------------------------------------------------------------- CABEÇALHO / CORPO
local FULLSCREEN = {}
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
 local title,icon,col,sub=pageTitle()
 local banner=window:FindFirstChild("Banner")
 if banner then
  banner.Title.Text=title
  local mark=banner:FindFirstChild("PageMark"); if mark then mark.BackgroundColor3=P.accent end
 end
 local sl=window:FindFirstChild("Subtitle")
 if sl then sl.Text=sub or (ctx.page=="Inventory" and "Selecione um item para ver detalhes e equipar" or "");sl.Visible=true end
 local tabsRoot=window:FindFirstChild("Tabs");if tabsRoot then tabsRoot:Destroy() end
 local items,current,tcol,onPick=tabsFor()
 if items then
  local ww=window.Size.X.Offset
  local th=(ctx.portrait or ctx.compact) and 60 or 44
  tabsRoot=T.frame(window,"Tabs",24,90,math.min(ww-48,600),th,nil,1)
  T.tabs(tabsRoot,"Segment",0,0,tabsRoot.Size.X.Offset,th,items,current,P.accent,onPick)
  return th+10
 end
 return 0
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
  local ww,wh=virtualW-24,virtualH-48
  return ww,wh,12,24
 elseif ctx.compact then
  return virtualW-40,virtualH-28,20,14
 end
 local ww,wh=math.min(1180,virtualW-160),math.min(740,virtualH-100)
 return ww,wh,(virtualW-ww)/2,(virtualH-wh)/2
end

drawWindow = function(animate)
 if not ctx.page then return end
 modalVersion+=1
 T.clear(modalLayer)
 local ww,wh,wx,wy=windowRect()
 window=T.panel(modalLayer,"Window",wx,wy,ww,wh,{bg=P.bg1,radius=10,strokeColor=P.lineSoft})
 window.Active=true
 local shadow=T.shadow(window,10,8,.55)
 local banner=T.frame(window,"Banner",24,18,ww-100,34,nil,1)
 T.frame(banner,"PageMark",0,5,3,24,P.accent,0)
 T.text(banner,"Title","",16,0,ww-160,34,28,P.text,T.LEFT,"display",false)
 T.text(window,"Subtitle","",40,54,ww-120,24,15,P.text2,T.LEFT,"body",false)
 local close=T.closeButton(window,ww-66,18,42,ctx.close)
 local extra=drawHeader()
 local headH=90+extra
 T.frame(window,"HeaderRule",24,headH-4,ww-48,1,P.lineSoft,.35)
 bodyW,bodyH=ww-48,wh-headH-24
 body=T.frame(window,"Body",24,headH,bodyW,bodyH,nil,1)
 hud.Visible=not (ctx.portrait or ctx.compact)
 drawBody()
 if animate then T.enter(window,.97,.18);T.enter(shadow,.97,.18) end
 if Input.GamepadEnabled and not Input.MouseEnabled then task.defer(function() if window and window.Parent then GuiService.SelectedObject=close end end) end
end

-- ---------------------------------------------------------------- HUD
local NAV = {
 {id="Store",label="Loja",icon="store",tip="Picaretas, mochilas e passes"},
 {id="Inventory",label="Unidades",icon="units",key="H",tip="Unidades e equipe"},
 {id="Items",label="Itens",icon="items",key="J",tip="Hats e atributos"},
 {id="Summon",label="Invocar",icon="summon",key="G",tip="Banners de unidades"},
 {id="Areas",label="Viajar",icon="areas",tip="Ilhas de mineração"},
 {id="Quests",label="Missões",icon="quests",tip="Objetivos e recompensas"},
 {id="Events",label="Diário",icon="events",tip="Recompensa diária e coleção"},
 {id="Settings",label="Ajustes",icon="settings",tip="Som, efeitos e códigos"},
}

drawHUD = function()
 T.clear(hud);hudRefs={}
 local portrait,compact=ctx.portrait,ctx.compact
 screen:SetAttribute("BottomReserved",portrait and 184 or 0)
 local margin=portrait and 16 or 24
 -- Recursos ficam juntos e fora da zona central de mineração.
 local row=T.panel(hud,"Currency",margin,14,portrait and 340 or 400,60,{bg=P.bg0})
 hudRefs.wallet=row
 T.icon(row,"coins",12,12,36,36)
 hudRefs.coins=T.text(row,"Coins",ctx.shownCoins and T.format(ctx.shownCoins) or "0",56,22,150,28,26,P.gold,T.LEFT,"number",false)
 T.text(row,"CoinsLabel","MOEDAS",56,6,130,17,12,P.text3,T.LEFT,"label",false)
 local px=portrait and 205 or 236
 T.frame(row,"Rule",px-10,14,1,32,P.lineSoft,0)
 T.statIcon(row,"dano",px,18,28,28)
 hudRefs.power=T.text(row,"Power","0",px+36,24,100,24,22,P.text,T.LEFT,"number",false)
 T.text(row,"PowerLabel","PODER",px+36,7,100,17,12,P.text3,T.LEFT,"label",false)
 T.hint(row,"Poder por golpe · moedas obtidas na venda","below")
 hudRefs.buffs=T.frame(hud,"Buffs",margin,82,portrait and virtualW-32 or 620,32,nil,1)
 hudRefs.buffKeys=""
 local tw=portrait and math.min(virtualW-32,420) or 360
 local tx=portrait and margin or virtualW-margin-tw
 local ty=portrait and 126 or 14
 local tracker=T.new("TextButton",{Name="Tracker",Text="",BackgroundColor3=P.bg0,BorderSizePixel=0,Position=UDim2.fromOffset(tx,ty),Size=UDim2.fromOffset(tw,100)},hud)
 T.corner(tracker,8);hudRefs.trackerStroke=T.stroke(tracker,P.lineSoft,1)
 hudRefs.areaName=T.text(tracker,"Area","Praça central",14,10,tw-28,22,15,P.accent,T.LEFT,"label",false)
 hudRefs.questText=T.text(tracker,"Quest","Seu próximo objetivo",14,35,tw-28,23,16,P.text,T.LEFT,"body",false)
 hudRefs.questBar=T.progress(tracker,"QuestBar",14,72,tw-100,5,0,P.accent)
 hudRefs.questCount=T.text(tracker,"Count","",tw-84,63,70,23,13,P.text2,T.RIGHT,"number",false)
 T.bindInteraction(tracker,function() ctx.questArea=nil;ctx.open("Quests") end)
 T.hint(tracker,"Objetivo atual · abrir missões","below")
 -- Navegação única: cada atalho ocupa uma posição estável.
 local cols=portrait and 4 or #NAV
 local nw=portrait and math.floor((virtualW-44)/4) or (compact and 72 or 88)
 local nh=portrait and 54 or 56
 local ng=6
 local rows=math.ceil(#NAV/cols)
 local dw=cols*nw+(cols-1)*ng
 local dh=rows*nh+(rows-1)*ng
 local dock=T.panel(hud,"Navigation",(virtualW-dw)/2,virtualH-dh-14,dw,dh,{bg=P.bg0,stroke=false})
 hudRefs.rail={}
 for i,it in ipairs(NAV) do
  local x=((i-1)%cols)*(nw+ng);local y=math.floor((i-1)/cols)*(nh+ng)
  local b=T.new("TextButton",{Name=it.id,Text="",AutoButtonColor=false,BackgroundColor3=P.bg1,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(nw,nh)},dock)
  T.corner(b,6)
  local rim=T.stroke(b,P.lineSoft,1,.4)
  local isz=portrait and 23 or 26
  T.icon(b,it.icon,(nw-isz)/2,5,isz,isz)
  T.text(b,"Label",it.label,4,nh-23,nw-8,20,14,P.text2,T.CENTER,"label",false)
  T.bindInteraction(b,function()
   if it.id=="Inventory" then ctx.collection="pet" end
   ctx.open(it.id)
  end,{onFocus=function(on) rim.Color=on and P.accent or P.lineSoft end})
  T.hint(b,it.tip..(it.key and " · ["..it.key.."]" or ""),"above")
  hudRefs.rail[it.id]=b
 end
 local bagW=portrait and virtualW-32 or math.min(600,virtualW*.42)
 local bagY=virtualH-dh-58
 local bagH=(portrait or compact) and 52 or 32
 if bagH>32 then bagY-=20 end
 local bag=T.frame(hud,"Bag",(virtualW-bagW)/2,bagY,bagW,bagH,nil,1)
 hudRefs.bagPanel=bag
 hudRefs.bagTrack=T.progress(bag,"Track",0,0,bagW-102,bagH,0,P.accent)
 hudRefs.bag=T.text(hudRefs.bagTrack,"Count","MOCHILA 0 / 0",10,0,bagW-122,bagH,14,P.text,T.LEFT,"label",false)
 hudRefs.sell=T.button(bag,"SellShortcut","Vender",bagW-94,0,94,bagH,P.neutral,function() ctx.open("Forge") end,{size=14})
 T.hint(hudRefs.sell,"Vender minérios com Ignis","above")
 local slot=portrait and 42 or 44
 local hotY=portrait and bagY-58 or virtualH-70
 hudRefs.hotbar=T.frame(hud,"Hotbar",margin,hotY,6*slot+5*8,slot,nil,1)
 T.text(hud,"TeamLabel","EQUIPE",margin,hotY-21,130,17,11,P.text3,T.LEFT,"label",false)
 hudRefs.signature=nil
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
	if target:GetAttribute("BadgeValue")==tostring(value or "") then return end
	target:SetAttribute("BadgeValue",tostring(value or ""))
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
	while alive and screen.Parent do
		task.wait(1)
		if pendingOffer and not ctx.page and not popupOpen and not ctx.summonBusy then local offer=pendingOffer;pendingOffer=nil;ofertaPopup(offer) end
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
	hudRefs.areaName.Text = T.upper(area and area.nome or "Praça central")
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
	for i = 1, math.clamp(tonumber(d.slotsPets) or 3,1,6) do
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
	local areaSig=table.concat((function() local out={} for k,v in pairs(data.areas or {}) do if v then table.insert(out,tostring(k)) end end table.sort(out);return out end)(),",")
	if areas and ctx.areaSignature~=areaSig then ctx.areaSignature=areaSig;for _,d in ipairs(areas:GetDescendants()) do if d.Name=="Barreira" then barrier(d) end end end
	local signature = inventorySignature(data)
	if signature ~= lastInventorySignature then
		lastInventorySignature = signature
		if ctx.page and not ctx.summonBusy then ctx.refresh() end
	elseif ctx.page == "Forge" or ctx.page == "Quests" or ctx.page == "Events" or ctx.page == "Store" or ctx.page == "Areas" then
		if not ctx.summonBusy then ctx.refresh() end
	end
end
connect(R.AtualizarDados.OnClientEvent,function(data) pushVersion += 1; acceptData(data) end)
connect(workspace.DescendantAdded,function(d) if d.Name == "Barreira" then task.defer(barrier, d) end end)

-- nome do minério da ilha atual (feed de coleta)
local function oreName(variante)
	local a = Config.areaPorId(player:GetAttribute("CurrentAreaId") or 0)
	local info = a and Config.infoMinerio(a.tema .. "_" .. (variante or "comum"))
	return info and info.nome or "Minério"
end

connect(R.FeedbackMina.OnClientEvent,function(info)
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
connect(R.AbrirIgnis.OnClientEvent,function() if ctx.page ~= "Forge" then ctx.open("Forge") end end)
connect(R.AbrirLoja.OnClientEvent,function() ctx.storeTab = "Mochilas"; if ctx.page ~= "Store" then ctx.open("Store") else ctx.refresh() end end)
connect(R.AbrirGacha.OnClientEvent,function(id)
	if Config.Gachas[id] then ctx.bannerArea = id; if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end end
end)
connect(player:GetAttributeChangedSignal("CurrentAreaId"),function()
	Som.tocar("portal_chegada")
	local id = player:GetAttribute("CurrentAreaId")
	local a = id and Config.areaPorId(id)
	local tema = a and Config.Temas[a.tema]
	Notify.banner({ title = a and a.nome or "Praça Central", subtitle = a and ("ILHA " .. a.id .. "  ·  " .. T.upper(tema.nome)) or "LOBBY  ·  IGNIS, BANNERS E PORTAIS",
		color = tema and tema.cor or P.accent, sound = false, duration = 1.8 })
	updateHUD()
end)
connect(player:GetAttributeChangedSignal("ExpeditionBlurEnabled"),updateBlur)

-- ---------------------------------------------------------------- RESOLUÇÃO
local function resize()
	local v = screen.AbsoluteSize
	if v.X < 1 or v.Y < 1 then return end
	ctx.portrait = v.X < v.Y * .85
	ctx.compact = not ctx.portrait and v.Y < 560
	local s
	if ctx.portrait then s = math.clamp(v.X / 500, .85, 1.25)
	elseif ctx.compact then s = math.max(.85,math.min(v.X / 1180, v.Y / 500))
	else s = math.clamp(math.min(v.X / BASE_W, v.Y / BASE_H), .5, 1.45) end
	scale.Scale = s
	T.uiScale = s
	virtualW, virtualH = v.X / s, v.Y / s
	canvas.Size = UDim2.fromOffset(virtualW, virtualH)
	for _, layer in ipairs({ hud, modalLayer, toastLayer, popupLayer, dialogHost, tipLayer }) do
		layer.Size = UDim2.fromOffset(virtualW, virtualH)
	end
	Notify.toastTop = ctx.portrait and 240 or 126
	drawHUD()
	hud.Visible = not ((ctx.portrait or ctx.compact) and ctx.page ~= nil)
	if ctx.page then drawWindow(false) end
	-- Resize conserva os objetos e a seleção do popup; somente reenquadra.
	for _,box in ipairs(dialogHost:GetChildren()) do if box.Name=="Popup" then
	 local bs=box.Size;local fit=math.min(1,(virtualW-24)/bs.X.Offset,(virtualH-24)/bs.Y.Offset)
	 T.scaleOf(box).Scale=fit;box.Position=UDim2.fromOffset((virtualW-bs.X.Offset*fit)/2,(virtualH-bs.Y.Offset*fit)/2)
	 local close=box:FindFirstChild("Close");if close then local cs=math.max(42,44/(s*fit));close.Size=UDim2.fromOffset(cs,cs);close.Position=UDim2.fromOffset(bs.X.Offset-cs-12,12);if close:FindFirstChild("Face") then close.Face.Size=UDim2.fromScale(1,1) end end
	 local shadow=dialogHost:FindFirstChild("PopupShadow");if shadow then T.scaleOf(shadow).Scale=fit;shadow.Position=box.Position+UDim2.fromOffset(0,8) end
	end end
	Notify.relayout()
end
screen:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)

connect(Input.InputBegan,function(input, processed)
	if processed or Input:GetFocusedTextBox() then return end
	local key = input.KeyCode
	if key == Enum.KeyCode.Escape or key==Enum.KeyCode.ButtonB then
		if popupOpen then closePopup() elseif ctx.page then ctx.close() end
	elseif key == Enum.KeyCode.H or key == Enum.KeyCode.B then ctx.collection = "pet"; ctx.open("Inventory")
	elseif key == Enum.KeyCode.J then ctx.open("Items")
	elseif key == Enum.KeyCode.G then ctx.open("Summon") end
end)
screen.Destroying:Connect(function() alive=false;for _,c in ipairs(connections) do c:Disconnect() end;blur:Destroy() end)
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

