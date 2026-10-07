-- Feedback compartilhado: confirmação breve, loot agrupado e revelações reservadas à raridade.
local T = require(script.Parent.Theme)
local Players = game:GetService("Players")
local TextService = game:GetService("TextService")
local TweenService = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local GuiService = game:GetService("GuiService")
local player = Players.LocalPlayer
local P = T.P
local N = {}
local toastLayer, overlayLayer, getSize
local visible, pending, feed, banners, reveals = {}, {}, {}, {}, {}
local bannerBusy, revealBusy, pumpQueued = false, false, false
local activeRevealLayout
local activeBanner
local bannerState
local nextBanner, nextReveal
local syncActiveBanner
local rewardConnections, shellConnections = {}, {}
N.toastTop = 84
N.feedAnchor = function() local w, h = getSize(); return w - 20, h - 82 end

local function motionEnabled()
	return T.motionEnabled and T.motionEnabled() or (not T.motionEnabled and player:GetAttribute("ReducedMotion") ~= true)
end
local function animate(object, duration, properties)
	return T.tween(object, motionEnabled() and duration or .08, properties, Enum.EasingStyle.Quad)
end
local function callOnce(opts)
	if opts._closed then return end
	opts._closed = true
	if opts.onClose then
		local ok, err = pcall(opts.onClose)
		if not ok then warn("[UI] Recompensa: " .. tostring(err)) end
	end
end
local function rewardBlocked()
	local shell = player:FindFirstChild("PlayerGui") and player.PlayerGui:FindFirstChild("ExpeditionUI")
	local page = shell and shell:GetAttribute("OpenPage")
	return (page ~= nil and page ~= "") or (shell and shell:GetAttribute("PopupOpen") == true)
		or player:GetAttribute("AreaTransition") ~= nil or player:GetAttribute("TravelTransition") == true
end
local function pump()
	if pumpQueued or (#banners == 0 and #reveals == 0) then return end
	pumpQueued = true
	task.delay(.25, function()
		pumpQueued = false
		nextReveal()
		nextBanner()
	end)
end

local function disconnectAll(connections)
	for _, connection in ipairs(connections) do connection:Disconnect() end
	table.clear(connections)
end
local function syncRewards()
	if syncActiveBanner then syncActiveBanner() end
	nextReveal()
	nextBanner()
end

function N.init(toastLayerFrame, overlayLayerFrame, sizeFn)
	disconnectAll(rewardConnections)
	disconnectAll(shellConnections)
	toastLayer, overlayLayer, getSize = toastLayerFrame, overlayLayerFrame, sizeFn
	player:SetAttribute("RevealOpen", false)
	-- One observer per shared blocking attribute, not a polling loop per banner.
	local pg = player:FindFirstChild("PlayerGui")
	local watchedShell
	local function watchShell(shell)
		disconnectAll(shellConnections)
		watchedShell = shell
		if shell then
			for _, name in ipairs({ "OpenPage", "PopupOpen" }) do
				table.insert(shellConnections, shell:GetAttributeChangedSignal(name):Connect(syncRewards))
			end
		end
		syncRewards()
	end
	for _, name in ipairs({ "AreaTransition", "TravelTransition" }) do
		table.insert(rewardConnections, player:GetAttributeChangedSignal(name):Connect(syncRewards))
	end
	if pg then
		table.insert(rewardConnections, pg.ChildAdded:Connect(function(child)
			if child.Name == "ExpeditionUI" then watchShell(child) end
		end))
		table.insert(rewardConnections, pg.ChildRemoved:Connect(function(child)
			if child == watchedShell then watchShell(nil) end
		end))
		watchShell(pg:FindFirstChild("ExpeditionUI"))
	end
	table.insert(rewardConnections, toastLayer.Destroying:Once(function()
		disconnectAll(rewardConnections)
		disconnectAll(shellConnections)
	end))
end
local function textBounds(text, size, width, font)
	return TextService:GetTextSize(tostring(text or ""), size, font or Enum.Font.BuilderSansBold, Vector2.new(math.max(1, width), 10000))
end
local function textWidth(text, size)
	return textBounds(text, size, 10000).X
end
local function toastBottom()
	local bottom = N.toastTop
	for _, t in ipairs(visible) do bottom += t.frame.Size.Y.Offset + 8 end
	return bottom
end
local function layoutBanner()
	if not activeBanner or not activeBanner.Parent then return end
	local vw, vh = getSize()
	local width = math.max(1, math.min(540, vw - 40))
	local title = activeBanner:FindFirstChild("Title")
	local subtitle = activeBanner:FindFirstChild("Subtitle")
	local icon = activeBanner:FindFirstChildWhichIsA("ImageLabel")
	local left = icon and 76 or 22
	local textW = math.max(1, width - left - 22)
	local titleH = title and math.max(30, textBounds(title.Text, title.TextSize, textW, Enum.Font.FredokaOne).Y + 4) or 30
	local subtitleH = subtitle and math.max(20, textBounds(subtitle.Text, subtitle.TextSize, textW).Y + 4) or 0
	local height = math.max(84, 28 + titleH + (subtitle and subtitleH + 4 or 0))
	activeBanner.Size = UDim2.fromOffset(width, height)
	if title then title.Size = UDim2.fromOffset(textW, titleH) end
	if subtitle then subtitle.Position = UDim2.fromOffset(left, 18 + titleH); subtitle.Size = UDim2.fromOffset(textW, subtitleH) end
	if icon then icon.Position = UDim2.fromOffset(20, (height - 42) / 2) end
	local rarity = activeBanner:FindFirstChild("Rarity")
	if rarity then rarity.Size = UDim2.fromOffset(4, height - 24) end
	local y = math.max(toastBottom() + 12, vh * .18)
	-- On a short screen, wait for toast space instead of covering or clipping text.
	activeBanner:SetAttribute("LayoutBlocked", #visible > 0 and y + height > vh - 16)
	y = math.max(16, math.min(y, vh - height - 16))
	animate(activeBanner, .18, { Position = UDim2.fromOffset(vw / 2, y) })
	if syncActiveBanner then syncActiveBanner() end
end

-- TOASTS: 3 visíveis e 4 aguardando. Categoria + mensagem definem duplicação.
local KIND = {
	success = { col = P.success, glyph = "✓" }, info = { col = P.accent, glyph = "i" },
	warning = { col = P.warning, glyph = "!" }, error = { col = P.danger, glyph = "!" },
	reward = { col = P.gold, glyph = "+" },
}
local TOAST_H, TOAST_GAP = 54, 8
local function toastSize(t)
	local vw, vh = getSize()
	local w = math.min(math.max(260, textWidth(t.label.Text, 15) + 72), 560, vw - 32)
	local maximumH = math.max(TOAST_H, math.min(96, math.floor((vh - N.toastTop - 24) / 3) - TOAST_GAP))
	local h = math.clamp(textBounds(t.label.Text, 15, w - 64).Y + 16, TOAST_H, maximumH)
	t.frame.Size = UDim2.fromOffset(w, h)
	t.label.Size = UDim2.fromOffset(w - 64, h - 12)
	t.frame.Category.Size = UDim2.fromOffset(24, h)
	t.frame.Accent.Size = UDim2.fromOffset(3, h - 16)
end
local function layoutToasts()
	if not getSize then return end
	local vw = getSize()
	local y = N.toastTop
	for _, t in ipairs(visible) do
		toastSize(t)
		animate(t.frame, .18, { Position = UDim2.fromOffset(vw / 2, y) })
		y += t.frame.Size.Y.Offset + TOAST_GAP
	end
	layoutBanner()
end
local showToast
local function removeToast(t)
	local idx = table.find(visible, t)
	if not idx then return end
	table.remove(visible, idx)
	animate(t.frame, .10, { GroupTransparency = 1 })
	task.delay(.12, function() t.frame:Destroy() end)
	layoutToasts()
	if #pending > 0 then local q = table.remove(pending, 1); showToast(q.text, q.kind) end
end
local function arm(t)
	t.serial += 1
	local serial = t.serial
	task.delay(t.kind == "error" and 4.5 or 3.4, function() if t.serial == serial then removeToast(t) end end)
end
showToast = function(text, kind)
	local k = KIND[kind] or KIND.info
	local vw = getSize()
	local f = T.new("CanvasGroup", { Name = "Toast", AnchorPoint = Vector2.new(.5, 0), BackgroundColor3 = P.bg1,
		BorderSizePixel = 0, GroupTransparency = 1, Position = UDim2.fromOffset(vw / 2, N.toastTop) }, toastLayer)
	T.corner(f, 8)
	T.stroke(f, P.neutral, 1)
	T.frame(f, "Accent", 0, 8, 3, TOAST_H - 16, k.col, 0)
	T.text(f, "Category", k.glyph, 13, 0, 24, TOAST_H, 19, k.col, T.CENTER, "title")
	local label = T.text(f, "Message", text, 48, 6, 220, TOAST_H - 12, 15, P.text, T.LEFT, "body")
	label:SetAttribute("Paragraph", true)
	label.TextTruncate = Enum.TextTruncate.AtEnd
	local t = { frame = f, text = text, kind = kind, label = label, count = 1, serial = 0 }
	table.insert(visible, t)
	layoutToasts()
	animate(f, .18, { GroupTransparency = 0 })
	arm(t)
end
function N.push(text, kind)
	if not toastLayer or type(text) ~= "string" or text == "" then return end
	kind = KIND[kind] and kind or "info"
	for _, t in ipairs(visible) do
		if t.text == text and t.kind == kind then
			t.count += 1
			t.label.Text = text .. "  ×" .. t.count
			layoutToasts()
			arm(t)
			return
		end
	end
	for _, q in ipairs(pending) do if q.text == text and q.kind == kind then return end end
	if #visible >= 3 then
		table.insert(pending, { text = text, kind = kind })
		if #pending > 4 then table.remove(pending, 1) end
		return
	end
	if kind == "success" or kind == "reward" then T.som("ui_notify") end
	showToast(text, kind)
end

-- LOOT: cinco linhas no máximo, sem criar novo widget para cada unidade recebida.
local FEED_H, FEED_GAP = 34, 6
local function layoutFeed()
	if not getSize then return end
	local right, bottom = N.feedAnchor()
	local vw = getSize()
	for i, e in ipairs(feed) do
		local w = math.min(math.max(158, textWidth(e.label.Text, 14) + 56), 330, vw - 32)
		e.frame.Size = UDim2.fromOffset(w, FEED_H)
		e.label.Size = UDim2.fromOffset(w - 48, FEED_H)
		animate(e.frame, .18, { Position = UDim2.fromOffset(right, bottom - (#feed - i) * (FEED_H + FEED_GAP)) })
	end
end
local function dropFeed(e)
	local i = table.find(feed, e)
	if not i then return end
	table.remove(feed, i)
	animate(e.frame, .10, { GroupTransparency = 1 })
	task.delay(.12, function() e.frame:Destroy() end)
	layoutFeed()
end
local function feedExpiry(e)
	e.serial += 1
	local serial = e.serial
	task.delay(2.8, function() if e.serial == serial then dropFeed(e) end end)
end
function N.feed(key, name, col, qty, opts)
	if not toastLayer then return end
	opts, qty, col = opts or {}, qty or 1, col or P.accent
	for _, e in ipairs(feed) do
		if e.key == key then
			e.qty += qty
			e.label.Text = "+" .. T.format(e.qty) .. "  " .. name
			layoutFeed()
			feedExpiry(e)
			return
		end
	end
	if #feed >= 5 then dropFeed(feed[1]) end
	local right, bottom = N.feedAnchor()
	local f = T.new("CanvasGroup", { Name = "Loot", AnchorPoint = Vector2.new(1, 1), BackgroundColor3 = P.bg1,
		BorderSizePixel = 0, GroupTransparency = 1, Position = UDim2.fromOffset(right, bottom) }, toastLayer)
	T.corner(f, 6)
	T.frame(f, "Rarity", 0, 7, 3, 20, col, 0)
	if opts.ore then T.oreIcon(f, opts.ore, 6, 3, 28, 28)
	elseif opts.icon then T.icon(f, opts.icon, 6, 3, 28, 28)
	else T.text(f, "Gem", "◆", 7, 0, 24, FEED_H, 15, col, T.CENTER, "title") end
	local label = T.text(f, "Text", "+" .. T.format(qty) .. "  " .. name, 40, 0, 210, FEED_H, 14, opts.textColor or P.text, T.LEFT, "body")
	label.TextTruncate = Enum.TextTruncate.AtEnd
	local e = { key = key, qty = qty, frame = f, label = label, serial = 0 }
	table.insert(feed, e)
	layoutFeed()
	animate(f, .18, { GroupTransparency = 0 })
	feedExpiry(e)
end

-- Raios opcionais usados também por previews existentes. O tween encerra com o componente.
function N.rays(parent, cx, cy, radius, col, _count, alpha)
	local holder = T.new("Frame", { Name = "Rays", AnchorPoint = Vector2.new(.5, .5), Position = UDim2.fromOffset(cx, cy),
		Size = UDim2.fromOffset(radius * 2, radius * 2), BackgroundTransparency = 1 }, parent)
	local img = T.image(holder, "Art", T.Assets.rays, 0, 0, radius * 2, radius * 2, col, math.max(.7, alpha or .7))
	img.ScaleType = Enum.ScaleType.Fit
	local tw
	local function updateMotion()
		if tw then tw:Cancel(); tw = nil end
		if motionEnabled() then
			tw = TweenService:Create(holder, TweenInfo.new(30, Enum.EasingStyle.Linear, Enum.EasingDirection.In, -1), { Rotation = holder.Rotation + 360 })
			tw:Play()
		end
	end
	updateMotion()
	local reduced = player:GetAttributeChangedSignal("ReducedMotion"):Connect(updateMotion)
	local effects = player:GetAttributeChangedSignal("ExpeditionEffectsEnabled"):Connect(updateMotion)
	holder.Destroying:Once(function() if tw then tw:Cancel() end; reduced:Disconnect(); effects:Disconnect() end)
	return holder
end

-- BANNER: confirmação curta e não interativa, uma por vez e fora das janelas abertas.
local function finishBanner(state, alreadyDestroying)
	if state.finished then return end
	state.finished = true
	state.serial += 1
	if state.opacityTween then state.opacityTween:Cancel() end
	if bannerState == state then
		bannerState, activeBanner, bannerBusy = nil, nil, false
	end
	if not alreadyDestroying and state.root.Parent then state.root:Destroy() end
	callOnce(state.opts)
	task.defer(function()
		if toastLayer and toastLayer.Parent then nextReveal(); nextBanner() end
	end)
end

syncActiveBanner = function()
	local state = bannerState
	if not state or state.finished then return end
	if not state.root.Parent then finishBanner(state); return end
	if rewardBlocked() or state.root:GetAttribute("LayoutBlocked") == true then
		if not state.paused then
			state.remaining = math.max(0, state.remaining - (os.clock() - state.startedAt))
			state.paused = true
			state.serial += 1 -- invalidate the pending expiry; it cannot finish a resumed banner
			if state.opacityTween then state.opacityTween:Cancel(); state.opacityTween = nil end
		end
		state.root.Visible = false
		return
	end
	if not state.paused then return end
	if state.remaining <= 0 and state.phase == "exit" then finishBanner(state); return end
	if state.remaining <= 0 then state.phase = "exit"; state.remaining = .12 end
	state.paused = false
	state.root.Visible = true
	state.startedAt = os.clock()
	state.serial += 1
	local serial = state.serial
	state.opacityTween = animate(state.root, state.phase == "exit" and math.min(.10, state.remaining) or .18,
		{ GroupTransparency = state.phase == "exit" and 1 or 0 })
	task.delay(state.remaining, function()
		if bannerState ~= state or state.finished or state.paused or state.serial ~= serial then return end
		-- A blocking attribute can change just before this callback is dispatched.
		if rewardBlocked() or state.root:GetAttribute("LayoutBlocked") == true then syncActiveBanner(); return end
		if state.phase == "exit" then finishBanner(state); return end
		state.phase, state.remaining, state.paused = "exit", .12, true
		if state.opacityTween then state.opacityTween:Cancel(); state.opacityTween = nil end
		syncActiveBanner()
	end)
end

nextBanner = function()
	if bannerBusy or revealBusy or #banners == 0 or not toastLayer or not toastLayer.Parent then return end
	if rewardBlocked() then pump(); return end
	bannerBusy = true
	local b = table.remove(banners, 1)
	local vw, vh = getSize()
	local col = b.color or P.gold
	local w, h = math.min(540, vw - 40), b.big and 98 or 84
	local root = T.new("CanvasGroup", { Name = "Banner", AnchorPoint = Vector2.new(.5, 0), BackgroundColor3 = P.bg1,
		GroupTransparency = 1, BorderSizePixel = 0, Position = UDim2.fromOffset(vw / 2, math.max(N.toastTop + 20, vh * .2)),
		Size = UDim2.fromOffset(w, h), ZIndex = 50 }, toastLayer)
	activeBanner = root
	layoutBanner()
	T.corner(root, 10)
	T.stroke(root, P.neutral, 1)
	T.frame(root, "Rarity", 0, 12, 4, h - 24, col, 0)
	local tx = b.icon and 76 or 22
	if b.icon then T.icon(root, b.icon, 20, (h - 42) / 2, 42, 42) end
	local heading = T.text(root, "Title", b.title or "", tx, 14, w - tx - 22, 30, b.big and 25 or 23, col, T.LEFT, "title")
	heading:SetAttribute("Paragraph", true)
	if b.subtitle then
		local label = T.text(root, "Subtitle", b.subtitle, tx, 46, w - tx - 22, h - 54, 15, P.text2, T.LEFT, "body")
		label:SetAttribute("Paragraph", true)
	end
	layoutBanner()
	if b.sound ~= false then T.som(b.sound or "reward_banner") end
	local state = { root = root, opts = b, phase = "visible", remaining = math.clamp(b.duration or 2.2, 1.2, 6),
		paused = true, serial = 0, finished = false }
	bannerState = state
	root.Destroying:Once(function() finishBanner(state, true) end)
	syncActiveBanner()
end
function N.banner(opts)
	if type(opts) ~= "table" then return end
	for _, b in ipairs(banners) do
		if b.title == opts.title and b.subtitle == opts.subtitle then return end
	end
	opts = table.clone(opts)
	opts._closed = nil
	table.insert(banners, opts)
	if #banners > 4 then callOnce(table.remove(banners, 1)) end
	nextBanner()
end
function N.levelUp(from, to, name)
	N.banner({ title = "Novo nível", subtitle = (name and (name .. "  ·  ") or "") .. (from and to and ("Nv. " .. from .. "  →  Nv. " .. to) or ""),
		color = P.gold, sound = false, duration = 1.8 })
end

-- REVEAL: itens épicos+; comuns recebem confirmação sem interromper a mineração.
nextReveal = function()
	if revealBusy or bannerBusy or #reveals == 0 or not overlayLayer or not overlayLayer.Parent then return end
	if rewardBlocked() then pump(); return end
	revealBusy = true
	player:SetAttribute("RevealOpen", true)
	local o = table.remove(reveals, 1)
	local r = T.rar(o.rarity)
	local col = r.cor
	local holder = T.new("Frame", { Name = "Reveal", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, ZIndex = 60 }, overlayLayer)
	local shield = T.new("TextButton", { Name = "Shield", Text = "", Selectable = false, AutoButtonColor = false, BackgroundColor3 = P.bg0,
		BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), BorderSizePixel = 0 }, holder)
	animate(shield, .18, { BackgroundTransparency = .3 })
	local w, h = 420, 580
	local card = T.panel(holder, "Card", 0, 0, w, h, { bg = P.bg1, radius = 10, strokeColor = P.neutral, strokeWidth = 1 })
	card.AnchorPoint = Vector2.new(.5, .5)
	card.Position = UDim2.fromScale(.5, .5)
	local accent = T.frame(card, "RarityAccent", 0, 0, 4, h, col, 0)
	local body = T.scroll(card, "Content", 16, 16, w - 32, h - 100, col)
	body.ClipsDescendants = true
	local tag = T.text(body, "New", o.tag or "NOVA DESCOBERTA", 0, 0, w - 32, 24, 14, P.success, T.CENTER, "label")
	tag:SetAttribute("Paragraph", true)
	local art = T.frame(body, "Art", 0, 36, w - 32, 226, P.bg0, 0)
	T.corner(art, 8)
	local name = T.text(body, "Name", o.name or "", 0, 274, w - 32, 40, 27, P.text, T.CENTER, "title")
	name:SetAttribute("Paragraph", true)
	local rarity = T.text(body, "Rarity", r.nome, 0, 322, w - 32, 26, 16, col, T.CENTER, "label")
	local subtitle = o.subtitle and T.para(body, "Subtitle", o.subtitle, 0, 356, w - 32, 42, 14, P.text2, T.CENTER)
	local previewSize
	local closed, keyConnection = false, nil
	local previousSelection = GuiService.SelectedObject
	local function close()
		if closed then return end
		closed = true
		if keyConnection then keyConnection:Disconnect() end
		activeRevealLayout = nil
		animate(shield, .10, { BackgroundTransparency = 1 })
		card.Visible = false
		task.delay(.12, function()
			holder:Destroy()
			revealBusy = false
			player:SetAttribute("RevealOpen", false)
			if previousSelection and previousSelection.Parent and previousSelection.Visible then GuiService.SelectedObject = previousSelection end
			callOnce(o)
			nextReveal()
			nextBanner()
		end)
	end
	local claim = T.button(card, "Claim", o.button or "Continuar", 16, h - 68, w - 32, 52, P.accent, close, { sound = "ui_click", size = 22 })
	activeRevealLayout = function()
		if closed then return end
		local vw, vh = getSize()
		local wide = vw >= 600 and vh < 560
		w, h = math.min(wide and 680 or 420, vw - 32), math.min(wide and 400 or 580, vh - 32)
		card.Size = UDim2.fromOffset(w, h)
		accent.Size = UDim2.fromOffset(4, h)
		local bodyW, bodyH = w - 32, h - 100
		body.Size = UDim2.fromOffset(bodyW, bodyH)
		claim.Position = UDim2.fromOffset(16, h - 68)
		claim.Size = UDim2.fromOffset(bodyW, 52)
		claim.Face.Size = UDim2.fromOffset(bodyW, 52)
		claim.Face.InnerRim.Size = UDim2.fromOffset(bodyW - 4, 48)
		claim.Face.Caption.Size = UDim2.fromOffset(bodyW - 24, 52)
		local artW = wide and math.min(240, bodyW * .38) or bodyW - 8
		local artH = wide and math.max(120, bodyH) or math.clamp(vh * .28, 160, 226)
		local infoX = wide and artW + 20 or 0
		local infoW = bodyW - infoX - 8
		local tagH = math.max(24, textBounds(tag.Text, 14, infoW, Enum.Font.GothamBlack).Y + 4)
		tag.Position = UDim2.fromOffset(infoX, 0)
		tag.Size = UDim2.fromOffset(infoW, tagH)
		local artY = wide and 0 or tagH + 12
		art.Position = UDim2.fromOffset(0, artY)
		art.Size = UDim2.fromOffset(artW, artH)
		local nameY = wide and tagH + 12 or artY + artH + 12
		local nameH = math.max(36, textBounds(name.Text, 27, infoW, Enum.Font.FredokaOne).Y + 6)
		name.Position = UDim2.fromOffset(infoX, nameY)
		name.Size = UDim2.fromOffset(infoW, nameH)
		rarity.Position = UDim2.fromOffset(infoX, nameY + nameH + 8)
		rarity.Size = UDim2.fromOffset(infoW, 26)
		local bottom = nameY + nameH + 34
		if subtitle then
			local subH = math.max(20, textBounds(subtitle.Text, 14, infoW).Y + 4)
			subtitle.Position = UDim2.fromOffset(infoX, bottom + 8)
			subtitle.Size = UDim2.fromOffset(infoW, subH)
			bottom += subH + 8
		end
		bottom = math.max(bottom, artY + artH) + 8
		body.CanvasSize = UDim2.fromOffset(0, bottom)
		body.CanvasPosition = Vector2.new(0, math.clamp(body.CanvasPosition.Y, 0, math.max(0, bottom - bodyH)))
		local signature = tostring(artW) .. ":" .. tostring(artH)
		if previewSize ~= signature then
			previewSize = signature
			T.clear(art)
			if r.ordem >= 6 then N.rays(art, artW / 2, artH / 2, math.min(artW, artH) * .65, col, 8, .78) end
			if o.kind == "pet" then
				T.characterViewport(art, o.id, 8, 6, artW - 16, artH - 12, { fullBody = false })
			else T.preview(art, o.kind or "hat", o.id, 8, 6, artW - 16, artH - 12, true) end
		end
	end
	activeRevealLayout()
	shield.Activated:Connect(close)
	keyConnection = UIS.InputBegan:Connect(function(input)
		if input.KeyCode == Enum.KeyCode.Escape or input.KeyCode == Enum.KeyCode.ButtonB then close() end
	end)
	if string.find(UIS:GetLastInputType().Name, "Gamepad") then GuiService.SelectedObject = claim end
	T.som("ui_popup")
	task.delay(math.clamp(o.duration or 7, 3, 12), close)
end
function N.reveal(opts)
	if type(opts) ~= "table" or not overlayLayer then return end
	opts = table.clone(opts)
	local r = T.rar(opts.rarity)
	if r.ordem < 4 and not opts.force then
		N.push((opts.tag or "Nova descoberta") .. "  ·  " .. (opts.name or "Item") .. "  ·  " .. r.nome, "reward")
		task.defer(callOnce, opts)
		return
	end
	table.insert(reveals, opts)
	if #reveals > 6 then
		local overflow = table.remove(reveals, 1)
		N.push((overflow.tag or "Nova descoberta") .. "  ·  " .. (overflow.name or "Item"), "reward")
		callOnce(overflow)
	end
	nextReveal()
end
function N.relayout()
	if syncActiveBanner then syncActiveBanner() end
	layoutToasts()
	layoutFeed()
	if activeRevealLayout then activeRevealLayout() end
end

return N
