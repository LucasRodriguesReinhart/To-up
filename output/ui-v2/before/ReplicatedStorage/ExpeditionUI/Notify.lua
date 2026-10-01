-- ============================================================================
-- NOTIFY V2 · notificações, feed de loot, banners e revelações de recompensa
--  * toasts: fila (máx. 3 visíveis), mensagens repetidas viram "x2" em vez de empilhar
--  * feed: coleta de minério agrupada por tipo, no canto inferior direito
--  * banner: momentos importantes (drop épico+, level up, ilha nova), um por vez
--  * reveal: card grande para item NOVO, com raios na cor da raridade
-- Contraste proposital: comum = linha discreta no feed; raro = banner; novo = card.
-- ============================================================================
local T = require(script.Parent.Theme)
local TextService = game:GetService("TextService")
local P = T.P
local WHITE = Color3.new(1, 1, 1)

local N = {}
local toastLayer, overlayLayer, getSize
N.toastTop = 84
N.feedAnchor = function() local w, h = getSize(); return w - 16, h - 78 end

function N.init(toastLayerFrame, overlayLayerFrame, sizeFn)
	toastLayer, overlayLayer, getSize = toastLayerFrame, overlayLayerFrame, sizeFn
end

local function textWidth(text, size)
	return TextService:GetTextSize(text, size, Enum.Font.GothamBold, Vector2.new(2000, 100)).X
end

-- ---------------------------------------------------------------- TOASTS
local KIND = {
	success = { col = P.success, glyph = "✓" },
	info = { col = P.accent, glyph = "i" },
	warning = { col = P.warning, glyph = "!" },
	error = { col = P.danger, glyph = "!" },
	reward = { col = P.gold, glyph = "★" },
}
local visible, pending = {}, {}
local MAX_VISIBLE, TOAST_H, TOAST_GAP = 3, 46, 8

local function layoutToasts()
	if not getSize then return end
	local vw = getSize()
	for i, t in ipairs(visible) do
		local y = N.toastTop + (i - 1) * (TOAST_H + TOAST_GAP)
		T.tween(t.frame, .22, { Position = UDim2.fromOffset(vw / 2, y) }, Enum.EasingStyle.Quint)
	end
end

local showToast
local function removeToast(t)
	local idx = table.find(visible, t)
	if not idx then return end
	table.remove(visible, idx)
	T.tween(t.frame, .18, { GroupTransparency = 1, Position = t.frame.Position - UDim2.fromOffset(0, 10) }, Enum.EasingStyle.Quad)
	task.delay(.2, function() t.frame:Destroy() end)
	layoutToasts()
	if #pending > 0 then
		local nxt = table.remove(pending, 1)
		showToast(nxt.text, nxt.kind)
	end
end

local function arm(t)
	t.serial += 1
	local serial = t.serial
	task.delay(t.kind == "error" and 3.8 or 3.2, function()
		if t.serial == serial then removeToast(t) end
	end)
end

showToast = function(text, kind)
	local vw = getSize()
	local k = KIND[kind] or KIND.info
	local w = math.clamp(textWidth(text, 16) + 78, 240, math.min(620, vw - 40))
	local f = T.new("CanvasGroup", { Name = "Toast", AnchorPoint = Vector2.new(.5, 0), BackgroundColor3 = P.bg1, BackgroundTransparency = .04,
		BorderSizePixel = 0, Size = UDim2.fromOffset(w, TOAST_H), GroupTransparency = 1,
		Position = UDim2.fromOffset(vw / 2, N.toastTop + #visible * (TOAST_H + TOAST_GAP) - 10) }, toastLayer)
	T.corner(f, 12)
	T.stroke(f, k.col:Lerp(P.bg1, .45), 1.5)
	local bar = T.frame(f, "Accent", 0, 0, 4, TOAST_H, k.col, 0)
	local dot = T.frame(f, "Glyph", 14, (TOAST_H - 26) / 2, 26, 26, k.col, 0)
	T.corner(dot, 13)
	T.text(dot, "G", k.glyph, 0, 0, 26, 26, 15, WHITE, T.CENTER, "title")
	local label = T.text(f, "Message", text, 50, 0, w - 64, TOAST_H, 16, P.text, T.LEFT, "body")
	local t = { frame = f, text = text, kind = kind, count = 1, label = label, serial = 0 }
	table.insert(visible, t)
	T.tween(f, .22, { GroupTransparency = 0 }, Enum.EasingStyle.Quad)
	T.enter(f, .92, .24)
	layoutToasts()
	arm(t)
	if kind == "error" then T.shake(bar, 0) end
end

function N.push(text, kind)
	if not text or text == "" or not toastLayer then return end
	for _, t in ipairs(visible) do
		if t.text == text then
			t.count += 1
			t.label.Text = text .. "  x" .. t.count
			T.pop(t.frame, 1.05, .2)
			arm(t)
			return
		end
	end
	for _, q in ipairs(pending) do if q.text == text then return end end
	if #visible >= MAX_VISIBLE then
		table.insert(pending, { text = text, kind = kind })
		if #pending > 4 then table.remove(pending, 1) end
		return
	end
	if kind == "reward" or kind == "success" then T.som("ui_notify") end
	showToast(text, kind)
end

-- ---------------------------------------------------------------- FEED DE LOOT
local feed = {}
local FEED_H, FEED_GAP, FEED_MAX = 34, 6, 5

local function layoutFeed()
	if not getSize then return end
	local right, bottom = N.feedAnchor()
	for i = #feed, 1, -1 do
		local e = feed[i]
		local fromBottom = #feed - i
		T.tween(e.frame, .2, { Position = UDim2.fromOffset(right, bottom - fromBottom * (FEED_H + FEED_GAP)) }, Enum.EasingStyle.Quint)
	end
end

local function dropFeed(e)
	local i = table.find(feed, e)
	if not i then return end
	table.remove(feed, i)
	T.tween(e.frame, .2, { GroupTransparency = 1, Position = e.frame.Position + UDim2.fromOffset(24, 0) }, Enum.EasingStyle.Quad)
	task.delay(.22, function() e.frame:Destroy() end)
	layoutFeed()
end

-- key agrupa entradas iguais; qty soma
function N.feed(key, name, col, qty, opts)
	if not toastLayer then return end
	opts = opts or {}
	qty = qty or 1
	local right, bottom = N.feedAnchor()
	for _, e in ipairs(feed) do
		if e.key == key then
			e.qty += qty
			e.label.Text = "+" .. T.format(e.qty) .. "  " .. name
			T.pop(e.label, 1.12, .22)
			e.serial += 1
			local s = e.serial
			task.delay(2.6, function() if e.serial == s then dropFeed(e) end end)
			return
		end
	end
	if #feed >= FEED_MAX then dropFeed(feed[1]) end
	local text = "+" .. T.format(qty) .. "  " .. name
	local w = math.clamp(textWidth(text, 15) + 58, 150, 320)
	local f = T.new("CanvasGroup", { Name = "Loot", AnchorPoint = Vector2.new(1, 1), BackgroundColor3 = P.bg0, BackgroundTransparency = .22,
		BorderSizePixel = 0, Size = UDim2.fromOffset(w, FEED_H), GroupTransparency = 1, Position = UDim2.fromOffset(right + 30, bottom) }, toastLayer)
	T.corner(f, 10)
	T.stroke(f, col:Lerp(P.bg0, .35), 1.5)
	local glow = T.frame(f, "Glow", 0, 0, w, FEED_H, col, 0)
	T.fade(glow, 0, .7, 1)
	if opts.ore then T.oreIcon(f, opts.ore, 4, 2, 30, 30)
	elseif opts.icon then T.icon(f, opts.icon, 6, 3, 28, 28)
	else T.text(f, "Gem", "◆", 8, 0, 24, FEED_H, 18, col, T.CENTER, "title", 1.4) end
	local label = T.text(f, "Text", text, 38, 0, w - 46, FEED_H, 15, opts.textColor or P.text, T.LEFT, "title", 1.4)
	local e = { key = key, qty = qty, frame = f, label = label, serial = 0 }
	table.insert(feed, e)
	T.tween(f, .18, { GroupTransparency = 0 }, Enum.EasingStyle.Quad)
	layoutFeed()
	e.serial += 1
	local s = e.serial
	task.delay(2.6, function() if e.serial == s then dropFeed(e) end end)
end

-- ---------------------------------------------------------------- BANNER
local banners, bannerBusy = {}, false
local function rays(parent, cx, cy, radius, col, _count, alpha)
	local holder = T.new("Frame", { Name = "Rays", AnchorPoint = Vector2.new(.5, .5), Position = UDim2.fromOffset(cx, cy),
		Size = UDim2.fromOffset(radius * 2, radius * 2), BackgroundTransparency = 1 }, parent)
	local img = T.image(holder, "Art", T.Assets.rays, 0, 0, radius * 2, radius * 2, col, alpha or .45)
	img.ScaleType = Enum.ScaleType.Fit
	local tw = game:GetService("TweenService"):Create(holder, TweenInfo.new(22, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = 360 })
	tw:Play()
	holder.Destroying:Once(function() tw:Cancel() end)
	return holder
end
N.rays = rays

local function nextBanner()
	if bannerBusy or #banners == 0 or not toastLayer then return end
	bannerBusy = true
	local b = table.remove(banners, 1)
	local vw, vh = getSize()
	local col = b.color or P.gold
	local w = math.min(b.big and 660 or 560, vw - 40)
	local h = b.big and 104 or 84
	local root = T.new("CanvasGroup", { Name = "Banner", AnchorPoint = Vector2.new(.5, .5), BackgroundTransparency = 1, GroupTransparency = 1,
		Position = UDim2.fromOffset(vw / 2, math.floor(vh * .24)), Size = UDim2.fromOffset(w, h + 40), ZIndex = 50 }, toastLayer)
	local band = T.frame(root, "Band", 0, 20, w, h, col, 0)
	T.new("UIGradient", { Color = ColorSequence.new(col:Lerp(P.bg0, .55), col:Lerp(P.bg0, .2)),
		Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.18, .15), T.kp(.82, .15), T.kp(1, 1) }) }, band)
	T.stripes(band, "Energy", 0, 0, w, h, WHITE, .93)
	local top = T.frame(root, "EdgeTop", w * .1, 20, w * .8, 2, col:Lerp(WHITE, .35), 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, top)
	local bottom = T.frame(root, "EdgeBottom", w * .1, 20 + h - 2, w * .8, 2, col:Lerp(WHITE, .35), 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, bottom)
	local tx = 0
	if b.icon then
		T.icon(root, b.icon, w * .5 - 190, 20 + (h - 72) / 2, 72, 72)
	end
	T.text(root, "Title", b.title or "", 40, 20 + 6, w - 80, h * .55, b.big and 46 or 36, col:Lerp(WHITE, .55), T.CENTER, "display", 2.2)
	if b.subtitle then
		T.text(root, "Subtitle", b.subtitle, 40, 20 + h * .56, w - 80, h * .36, b.big and 22 or 18, P.text, T.CENTER, "title", 1.6)
	end
	if b.sound ~= false then T.som(b.sound or "reward_banner") end
	T.tween(root, .16, { GroupTransparency = 0 }, Enum.EasingStyle.Quad)
	T.enter(root, .7, .34)
	task.delay(b.duration or 2.2, function()
		T.tween(root, .22, { GroupTransparency = 1 }, Enum.EasingStyle.Quad)
		local sc = root:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .22, { Scale = 1.06 }, Enum.EasingStyle.Quad) end
		task.delay(.24, function()
			root:Destroy()
			bannerBusy = false
			nextBanner()
		end)
	end)
end

function N.banner(opts)
	table.insert(banners, opts)
	if #banners > 4 then table.remove(banners, 1) end
	nextBanner()
end

function N.levelUp(from, to, name)
	N.banner({ title = "LEVEL UP!", subtitle = (name and (name .. "  ·  ") or "") .. (from and to and ("Nv. " .. from .. "  →  Nv. " .. to) or ""),
		color = P.gold, sound = false, duration = 1.8 })
end

-- ---------------------------------------------------------------- REVEAL
local reveals, revealBusy = {}, false
local function nextReveal()
	if revealBusy or #reveals == 0 or not overlayLayer then return end
	revealBusy = true
	local o = table.remove(reveals, 1)
	local vw, vh = getSize()
	local r = T.rar(o.rarity)
	local col = r.cor
	local holder = T.frame(overlayLayer, "Reveal", 0, 0, vw, vh, P.bg0, 1)
	holder.ZIndex = 60
	local shield = T.new("TextButton", { Name = "Shield", Text = "", AutoButtonColor = false, BackgroundColor3 = P.bg0,
		BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), BorderSizePixel = 0 }, holder)
	T.tween(shield, .2, { BackgroundTransparency = .45 }, Enum.EasingStyle.Quad)
	local cx, cy = vw / 2, vh / 2
	local ray = rays(holder, cx, cy - 40, 360, col, 12, r.ordem >= 5 and .45 or .7)
	local w, h = 360, 486
	local card = T.panel(holder, "Card", cx - w / 2, cy - h / 2, w, h, { bg = P.bg1, radius = 18, strokeColor = col, strokeWidth = 2.5 })
	T.shadow(card, 18, 10, .45)
	T.rarityFrame(card, o.rarity, { animated = true, noGlow = false })
	local chip, cw = T.chip(card, "NewChip", o.tag or "NOVO!", 0, 16, 28, P.success, { solid = true, size = 15 })
	chip.Position = UDim2.fromOffset((w - cw) / 2, 16)
	local art = T.frame(card, "Art", 30, 54, w - 60, 230, P.bg0, .4)
	T.corner(art, 14)
	T.preview(art, o.kind or "hat", o.id, 10, 6, w - 80, 218, true)
	T.text(card, "Name", o.name or "", 18, 296, w - 36, 42, 30, P.text, T.CENTER, "display", 1.8)
	local rchip, rw = T.chip(card, "Rarity", T.upper(r.nome), 0, 342, 30, col, { size = 15 })
	rchip.Position = UDim2.fromOffset((w - rw) / 2, 342)
	if o.subtitle then T.para(card, "Subtitle", o.subtitle, 22, 378, w - 44, 38, 14, P.text2, T.CENTER) end
	local closed = false
	local function close()
		if closed then return end
		closed = true
		T.tween(shield, .16, { BackgroundTransparency = 1 }, Enum.EasingStyle.Quad)
		local sc = card:FindFirstChildOfClass("UIScale")
		if sc then T.tween(sc, .16, { Scale = .85 }, Enum.EasingStyle.Quad) end
		ray.Visible = false
		task.delay(.17, function()
			holder:Destroy()
			revealBusy = false
			if o.onClose then o.onClose() end
			nextReveal()
		end)
	end
	T.button(card, "Claim", o.button or "Resgatar", 40, h - 66, w - 80, 50, P.success, close, { sound = "ui_compra" })
	shield.Activated:Connect(close)
	T.enter(card, .55, .42)
	T.som("ui_popup")
	task.delay(o.duration or 7, close)
end

function N.reveal(opts)
	table.insert(reveals, opts)
	nextReveal()
end

function N.relayout()
	layoutToasts()
	layoutFeed()
end

return N

