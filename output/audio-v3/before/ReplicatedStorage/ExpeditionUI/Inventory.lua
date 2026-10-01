-- ============================================================================
-- INVENTÁRIO V2 · coleção pesquisável + ficha de equipamento
-- Favoritos e proteção são preferências desta sessão; os dados continuam no servidor.
-- A lógica (equipar, alimentar, fundir, renomear) continua no servidor, pelos mesmos Remotes.
-- ============================================================================
local T = require(script.Parent.Theme)
local Config = require(game.ReplicatedStorage.Config)
local Input = game:GetService("UserInputService")
local P = T.P
local WHITE = Color3.new(1, 1, 1)
local M = {}
local states = setmetatable({}, { __mode = "k" })
local STAR, CHECK = utf8.char(0x2605), utf8.char(0x2713)
local REMOTES = {
	hat = { equip = "EquiparHat", fuse = "FundirHat", best = "EquiparMelhores", clear = "DesequiparTodos" },
	pet = { equip = "EquiparPet", fuse = "AlimentarPet", best = "EquiparMelhoresPets", clear = "DesequiparPets" },
}

local function count(v) return math.max(0, math.floor(tonumber(v) or 0)) end
local function inventoryOf(data, kind) return (kind == "pet" and data.petsInv or data.hatsInv) or {} end
local function equippedList(data, kind) return (kind == "pet" and data.petsEquipados or data.equipados) or {} end
local function isEquipped(data, kind, id) return table.find(equippedList(data, kind), id) ~= nil end
local function maxLevel(kind) return kind == "pet" and Config.PET_NIVEL_MAX or Config.HAT_NIVEL_MAX end
local function stateFor(ctx) if not states[ctx] then states[ctx] = { busy = false } end return states[ctx] end
local function pct(v) return T.format(math.floor(v * 1000 + .5) / 10) .. "%" end
local function protected(ctx, kind, uid)
	local key = kind .. ":" .. uid
	return (ctx.favorites and ctx.favorites[key] == true) or (ctx.locks and ctx.locks[key] == true)
end
local function power(kind, entry)
	return kind == "pet" and Config.petBonusDano(entry.def, entry.level) or Config.hatDanoNoNivel(entry.def.dano, entry.level)
end
local function controlHeight(ctx, desktop)
	return (Input.TouchEnabled or (ctx and (ctx.portrait or ctx.compact))) and 52 or desktop
end

-- Very short viewports scroll the complete layout instead of squeezing controls or
-- placing actions outside the window. Parent scroll remains reachable at panel gutters.
local function scrollableSpace(parent, name, w, h, minimum)
	if h >= minimum then return parent, w, h end
	local view = T.scroll(parent, name, 0, 0, w, h, P.lineSoft)
	view.CanvasSize = UDim2.fromOffset(0, minimum)
	local content = T.frame(view, "Content", 0, 0, math.max(1, w - 14), minimum, nil, 1)
	return content, math.max(1, w - 14), minimum
end

local function petName(data, def, uid)
	local inst = data and data.petsInv and uid and data.petsInv[uid]
	local nick = type(inst) == "table" and inst.apelido
	return (nick and nick ~= "") and nick or def.nome
end

local function itemCopies(data, kind, uid)
	local inv = inventoryOf(data, kind)
	local inst = inv[uid]
	if type(inst) ~= "table" then return 0, 0 end
	local equipped = equippedList(data, kind)
	local total, free = 0, 0
	for other, o in pairs(inv) do
		if o.id == inst.id then
			total += 1
			if other ~= uid and not table.find(equipped, other) then free += 1 end
		end
	end
	return total, free
end

local function normalized(value)
	local result = tostring(value or ""):lower()
	local accents = { { 0xE1, "a" }, { 0xE0, "a" }, { 0xE2, "a" }, { 0xE3, "a" }, { 0xE9, "e" }, { 0xEA, "e" },
		{ 0xED, "i" }, { 0xF3, "o" }, { 0xF4, "o" }, { 0xF5, "o" }, { 0xFA, "u" }, { 0xFC, "u" }, { 0xE7, "c" } }
	for _, accent in ipairs(accents) do
		result = result:gsub(utf8.char(accent[1]), accent[2]):gsub(utf8.char(accent[1] - 32), accent[2])
	end
	return result:match("^%s*(.-)%s*$")
end

local function invoke(ctx, remote, ...)
	local state = stateFor(ctx)
	if state.busy then return end
	state.busy = true
	local args = table.pack(...)
	task.spawn(function()
		local ok = pcall(function() ctx.invoke(remote, table.unpack(args, 1, args.n)) end)
		state.busy = false
		if not ok then ctx.toast("Não foi possível conectar ao servidor. Tente de novo.", nil, "error") end
		ctx.refresh()
	end)
	ctx.refresh()
end

-- ---------------------------------------------------------------- COLETA / ORDEM
local function collect(ctx, kind, data)
	local catalog = kind == "pet" and Config.Pets or Config.Hats
	local equipped = equippedList(data, kind)
	local order, equippedOrder = {}, {}
	for index, id in ipairs(equipped) do equippedOrder[id] = index end
	for index, def in ipairs(catalog) do order[def.id] = index end
	local query = normalized(ctx.search)
	local entries, lookup = {}, {}
	local function consider(def, key, quantity, level)
		local rarity = T.rar(def.raridade)
		local nick = kind == "pet" and quantity > 0 and petName(data, def, key) or ""
		local haystack = normalized(def.nome .. " " .. nick .. " " .. def.id .. " " .. (def.tema or "") .. " " .. rarity.nome)
		local status = ctx.inventoryStatus or "all"
		local stateMatch = status == "all"
			or (status == "equipped" and isEquipped(data, kind, key))
			or (status == "favorite" and ctx.favorites[kind .. ":" .. key] == true)
			or (status == "locked" and ctx.locks[kind .. ":" .. key] == true)
		if stateMatch and (not ctx.ownedOnly or quantity > 0) and (not ctx.rarity or def.raridade == ctx.rarity)
			and (query == "" or haystack:find(query, 1, true)) then
			local entry = { def = def, key = key, quantity = quantity, level = level, order = order[def.id] or 0, rarity = rarity }
			table.insert(entries, entry)
			lookup[key] = entry
		end
	end
	local ownedIds = {}
	for uid, inst in pairs(inventoryOf(data, kind)) do
		local def = kind == "pet" and Config.petPorId(inst.id) or Config.hatPorId(inst.id)
		if def then
			ownedIds[def.id] = true
			consider(def, uid, 1, math.max(1, count(inst.nivel)))
		end
	end
	for _, def in ipairs(catalog) do
		if not ownedIds[def.id] then consider(def, def.id, 0, 1) end
	end
	table.sort(entries, function(a, b)
		local sort = ctx.inventorySort or "recommended"
		if sort == "power" and power(kind, a) ~= power(kind, b) then return power(kind, a) > power(kind, b) end
		if sort == "level" and a.level ~= b.level then return a.level > b.level end
		if sort == "name" then
			local an = normalized(kind == "pet" and petName(data, a.def, a.key) or a.def.nome)
			local bn = normalized(kind == "pet" and petName(data, b.def, b.key) or b.def.nome)
			if an ~= bn then return an < bn end
		end
		if sort == "rarity" and a.rarity.ordem ~= b.rarity.ordem then return a.rarity.ordem > b.rarity.ordem end
		local ae, be = equippedOrder[a.key], equippedOrder[b.key]
		if ae ~= be then
			if not ae then return false end
			if not be then return true end
			return ae < be
		end
		local af = ctx.favorites[kind .. ":" .. a.key] == true
		local bf = ctx.favorites[kind .. ":" .. b.key] == true
		if af ~= bf then return af end
		if (a.quantity > 0) ~= (b.quantity > 0) then return a.quantity > 0 end
		if a.rarity.ordem ~= b.rarity.ordem then return a.rarity.ordem > b.rarity.ordem end
		if a.order ~= b.order then return a.order < b.order end
		if a.level ~= b.level then return a.level > b.level end
		return tostring(a.key) < tostring(b.key)
	end)
	local selected = lookup[ctx.selected]
	if not selected then
		for _, id in ipairs(equipped) do if lookup[id] then selected = lookup[id]; break end end
	end
	if not selected then
		for _, entry in ipairs(entries) do if entry.quantity > 0 then selected = entry; break end end
	end
	selected = selected or entries[1]
	ctx.selected = selected and selected.key or nil
	return entries, selected
end

-- ---------------------------------------------------------------- CARD DA GRADE
local function card(ctx, parent, kind, data, entry, x, y, size, height)
	local def = entry.def
	local selected = ctx.selected == entry.key
	local owned = entry.quantity > 0
	local r = entry.rarity
	height = height or size + 70
	local holder = T.new("TextButton", { Name = "Item_" .. entry.key, Text = "", AutoButtonColor = false, BackgroundTransparency = 1,
		BorderSizePixel = 0, Selectable = true, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, height) }, parent)
	local tile = T.panel(holder, "Tile", 0, 0, size, height, { bg = selected and P.bg3 or P.bg2, radius = 10,
		strokeColor = selected and P.accent or P.lineSoft, strokeWidth = selected and 2 or 1 })
	tile.ClipsDescendants = true
	local artH = height - 68
	local backdrop = T.frame(tile, "Art", 4, 4, size - 8, artH - 4, r.cor:Lerp(P.bg1, .88), 0)
	T.corner(backdrop, 7)
	local artSize = size - 8
	if kind == "pet" and Config.PetArte and Config.PetArte[def.id] then
		local art = T.preview(tile, "pet", def.id, 4, 4, artSize, artH - 4, false, not owned)
		if art:IsA("ImageLabel") then art.ScaleType = Enum.ScaleType.Crop; T.corner(art, 7) end
	else
		T.preview(tile, kind, def.id, 8, 8, size - 16, artH - 12, false, not owned)
	end
	local level = T.frame(tile, "LevelTag", 8, 8, 54, 22, P.bg0, .1)
	T.corner(level, 5)
	T.text(level, "Level", owned and ("Nv. " .. entry.level) or "—", 4, 0, 46, 22, 12, P.text, T.CENTER, "body")
	local key = kind .. ":" .. entry.key
	if ctx.locks[key] or ctx.favorites[key] then
		local mark = T.frame(tile, "SessionMarks", size - 54, 8, 46, 22, P.bg0, .1)
		T.corner(mark, 5)
		if ctx.locks[key] then T.lock(mark, 4, 3, 16, P.accent) end
		if ctx.favorites[key] then T.text(mark, "Favorite", STAR, 23, 0, 20, 22, 13, P.gold, T.CENTER, "body") end
	end
	if isEquipped(data, kind, entry.key) then
		local badge = T.frame(tile, "Equipped", 8, artH - 25, size - 16, 22, P.success:Lerp(P.bg0, .65), 0)
		T.corner(badge, 5)
		T.text(badge, "State", CHECK .. " Equipado", 3, 0, size - 22, 22, 12, P.success, T.CENTER, "body")
	elseif selected then
		local badge = T.frame(tile, "Selected", 8, artH - 25, size - 16, 22, P.accent:Lerp(P.bg0, .72), 0)
		T.corner(badge, 5)
		T.text(badge, "State", "Selecionado", 3, 0, size - 22, 22, 12, P.accent, T.CENTER, "body")
	end
	T.frame(tile, "RarityRule", 0, artH, size, 2, r.cor, .1)
	T.text(tile, "Name", kind == "pet" and petName(data, def, entry.key) or def.nome, 10, artH + 7, size - 20, 21, 14, P.text, T.LEFT, "title")
	T.text(tile, "Rarity", r.nome, 10, artH + 30, size - 20, 16, 12, r.cor, T.LEFT, "body")
	local stat = kind == "pet" and ("+" .. pct(power(kind, entry))) or ("+" .. T.format(power(kind, entry)))
	T.text(tile, "Power", owned and (stat .. " dano") or "Não obtido", 10, artH + 48, size - 20, 16, 12, owned and P.text2 or P.text3, T.LEFT, "body")
	T.bindInteraction(holder, function()
		if ctx.selected == entry.key and not (ctx.inventoryNarrow and not ctx.inventoryDetailOpen) then return end
		ctx.selected = entry.key
		if ctx.inventoryNarrow then ctx.inventoryDetailOpen = true end
		ctx.redrawBody()
	end, { sound = "ui_tab", hoverScale = 1.015 })
	return holder
end

-- ---------------------------------------------------------------- SELEÇÃO (alimentar / fundir)
local function selectionPopup(ctx, opts)
	local selection, reviewing = {}, false
	local build
	local function rebuild(p, w, h)
		local old = p:FindFirstChild("Candidates", true)
		local position = old and old.CanvasPosition
		T.clear(p); build(p, w, h)
		local current = p:FindFirstChild("Candidates", true)
		if current and position then current.CanvasPosition = position end
	end
	function build(p, w, h)
		p, w, h = scrollableSpace(p, "ConsumptionLayout", w, h, 500)
		local buttonH = controlHeight(ctx, 44)
		local data = ctx.data or {}
		local def, level, xp = opts.target(data)
		if not def then
			T.emptyState(p, "Gone", "Item indisponível", "Este item não está mais no inventário.", 0, 0, w, h)
			return
		end
		local maxed = level >= opts.maxLevel
		local list = opts.candidates(data)
		local valid, ordered, xpGain = {}, {}, 0
		for _, c in ipairs(list) do valid[c.key] = c end
		for key in pairs(selection) do if not valid[key] then selection[key] = nil end end
		-- Deterministic low-rarity order; do not select extra copies after the level cap.
		for _, c in ipairs(list) do
			if selection[c.key] then
				local currentLevel = opts.previewLevel(def, level, xp, xpGain)
				if currentLevel >= opts.maxLevel then selection[c.key] = nil
				else table.insert(ordered, c.key); xpGain += c.xp end
			end
		end
		local chosen = #ordered
		if chosen == 0 then reviewing = false end
		local newLevel, newXp = opts.previewLevel(def, level, xp, xpGain)
		local need = opts.need(def, newLevel)
		local busy = stateFor(ctx).busy
		T.text(p, "Target", opts.name(data, def), 0, 0, w - 150, 30, 22, P.text, T.LEFT, "title")
		T.text(p, "Level", "Nv. " .. level .. (newLevel > level and (" → " .. newLevel) or ""), w - 150, 0, 150, 30, 18,
			newLevel > level and P.success or P.text2, T.RIGHT, "title")
		T.progress(p, "XpTrack", 0, 38, w, 24, newLevel >= opts.maxLevel and 1 or math.clamp(newXp / need, 0, 1), P.violet, {
			text = newLevel >= opts.maxLevel and "NÍVEL MÁXIMO" or (T.format(newXp) .. " / " .. T.format(need) .. " XP"), textSize = 14 })
		T.para(p, "Protection", "Equipados, favoritos e protegidos nesta sessão ficam fora da seleção.", 0, 72, w, 34, 14, P.text2, T.LEFT, "body")
		local gridTop = 108 + buttonH + 12
		if reviewing then
			T.para(p, "ReviewWarning", "Confira antes de continuar: os " .. chosen .. " itens abaixo serão consumidos. Esta ação não pode ser desfeita.",
				0, 108, w, buttonH, 15, P.warning, T.LEFT, "body")
		else
			local gap = 8
			local bw = (w - gap * #opts.quickPicks) / (#opts.quickPicks + 1)
			for i, pick in ipairs(opts.quickPicks) do
				local b = T.button(p, "Quick_" .. i, pick[1], (i - 1) * (bw + gap), 108, bw, buttonH, P.neutral, function()
					for _, c in ipairs(list) do if pick[2](c) then selection[c.key] = true end end
					rebuild(p, w, h)
				end, { size = 15 })
				T.setEnabled(b, not maxed and not busy)
			end
			local clear = T.button(p, "Clear", "Limpar", #opts.quickPicks * (bw + gap), 108, bw, buttonH, P.neutral, function()
				selection = {}; rebuild(p, w, h)
			end, { size = 15 })
			T.setEnabled(clear, chosen > 0 and not busy)
		end
		local footerH = buttonH + 36
		local gridH = math.max(72, h - gridTop - footerH)
		local grid = T.scroll(p, "Candidates", 0, gridTop, w, gridH, P.violet)
		local cols = math.max(2, math.floor((w - 8) / 130))
		local gap = 10
		local size = math.floor((w - 12 - (cols - 1) * gap) / cols)
		local cellH = size + 48
		local index = 0
		for _, c in ipairs(list) do
			if reviewing and not selection[c.key] then continue end
			local x, y = (index % cols) * (size + gap), math.floor(index / cols) * (cellH + gap)
			index += 1
			local picked = selection[c.key] == true
			local cell = T.new("TextButton", { Name = "Pick_" .. c.key, Text = "", AutoButtonColor = false, BackgroundTransparency = 1,
				Selectable = not reviewing, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, cellH) }, grid)
			local tile = T.panel(cell, "Tile", 0, 0, size, cellH, { bg = P.bg2, radius = 9,
				strokeColor = picked and P.accent or P.lineSoft, strokeWidth = picked and 2 or 1 })
			T.preview(tile, c.kind, c.def.id, 5, 5, size - 10, size - 12, false)
			T.text(tile, "Level", "Nv. " .. c.level, 8, 6, size - 16, 20, 12, P.text, T.LEFT, "body")
			T.text(tile, "Name", c.name, 8, size - 1, size - 16, 21, 13, P.text, T.LEFT, "title")
			T.text(tile, "Xp", "+" .. T.format(c.xp) .. " XP", 8, size + 22, size - 16, 18, 13, P.violet, T.LEFT, "body")
			if picked then
				local badge = T.frame(tile, "Check", size - 32, 8, 24, 24, P.accent, 0)
				T.corner(badge, 6)
				T.text(badge, "Mark", CHECK, 0, 0, 24, 24, 16, P.bg0, T.CENTER, "heavy")
			end
			if not reviewing then
				T.bindInteraction(cell, function()
					if maxed or stateFor(ctx).busy then return end
					selection[c.key] = not picked or nil
					rebuild(p, w, h)
				end, { sound = "ui_tab", hoverScale = 1.015 })
			end
		end
		grid.CanvasSize = UDim2.fromOffset(0, math.ceil(index / cols) * (cellH + gap))
		if index == 0 then
			T.emptyState(grid, "Empty", maxed and "Nível máximo" or "Nenhum item disponível", maxed and "Este item já alcançou seu nível máximo." or opts.emptyText, 0, 0, w - 12, gridH)
		end
		T.text(p, "Summary", chosen .. " selecionado(s)  ·  +" .. T.format(xpGain) .. " XP", 0, h - buttonH - 32, w, 26, 15, P.text2, T.LEFT, "body")
		local actionX, actionW = 0, w
		if reviewing then
			actionW = (w - 12) / 2; actionX = actionW + 12
			local back = T.button(p, "BackToSelection", "Voltar à seleção", 0, h - buttonH, actionW, buttonH, P.neutral, function()
				reviewing = false; rebuild(p, w, h)
			end, { size = 16 })
			T.setEnabled(back, not busy)
		end
		local confirm = T.button(p, "Confirm", busy and "Processando..." or (reviewing and ("Confirmar · " .. chosen .. " itens") or ("Revisar seleção (" .. chosen .. ")")),
			actionX, h - buttonH, actionW, buttonH, reviewing and P.warning or P.violet, function()
			if stateFor(ctx).busy then return end
			if not reviewing then reviewing = true; rebuild(p, w, h); return end
			stateFor(ctx).busy = true
			local sent = table.clone(ordered)
			rebuild(p, w, h)
			task.spawn(function()
				-- Revalidate local protection just before the request. Server revalidates ownership/equipment.
				local allowed, keys = {}, {}
				for _, c in ipairs(opts.candidates(ctx.data or {})) do allowed[c.key] = true end
				for _, key in ipairs(sent) do if allowed[key] then table.insert(keys, key) end end
				local ok, result = pcall(opts.remote, ctx.data or {}, keys)
				stateFor(ctx).busy = false
				if ok and result and result.ok then selection = {}; reviewing = false
				elseif not ok then ctx.toast("Não foi possível concluir. Tente novamente.", nil, "error") end
				if p.Parent then rebuild(p, w, h) end
				ctx.refresh()
			end)
		end, { size = 16 })
		T.setEnabled(confirm, chosen > 0 and not maxed and not busy)
	end
	ctx.popup(opts.title, build, 920, 680, { color = P.violet })
end

local function previewPet(def, level, xp, gain)
	xp += gain
	while level < Config.PET_NIVEL_MAX and xp >= Config.petXpParaSubir(def, level) do
		xp -= Config.petXpParaSubir(def, level); level += 1
	end
	return level, level >= Config.PET_NIVEL_MAX and 0 or xp
end
local function previewHat(def, level, xp, gain)
	local fake = { nivel = level, xp = xp, xpTotal = 0 }
	Config.hatAplicarXp(def, fake, gain)
	return fake.nivel, fake.xp
end

local function feedPopup(ctx, targetUid)
	selectionPopup(ctx, {
		title = "Alimentar unidade", verb = "Alimentar", maxLevel = Config.PET_NIVEL_MAX,
		emptyText = "Você pode usar cópias não equipadas. Favoritos e protegidos nesta sessão ficam preservados.",
		name = function(data, def) return petName(data, def, targetUid) end,
		need = function(def, level) return Config.petXpParaSubir(def, level) end,
		previewLevel = previewPet,
		target = function(data)
			local inst = data.petsInv and data.petsInv[targetUid]
			local def = type(inst) == "table" and Config.petPorId(inst.id)
			if not def then return nil end
			return def, math.max(1, count(inst.nivel)), count(inst.xp)
		end,
		candidates = function(data)
			local list = {}
			for uid, inst in pairs(data.petsInv or {}) do
				local fdef = Config.petPorId(inst.id)
				if fdef and uid ~= targetUid and not table.find(data.petsEquipados or {}, uid) and not protected(ctx, "pet", uid) then
					table.insert(list, { key = uid, kind = "pet", def = fdef, level = math.max(1, count(inst.nivel)),
						name = petName(data, fdef, uid), xp = Config.petXpComoComida(fdef, inst) })
				end
			end
			table.sort(list, function(a, b)
				local ra, rb = T.rar(a.def.raridade).ordem, T.rar(b.def.raridade).ordem
				if ra ~= rb then return ra < rb end
				if a.xp ~= b.xp then return a.xp < b.xp end
				return a.key < b.key
			end)
			return list
		end,
		quickPicks = {
			{ "Comuns", function(c) return c.def.raridade == "comum" end },
			{ "Até incomum", function(c) return c.def.raridade == "comum" or c.def.raridade == "incomum" end },
		},
		remote = function(_, sel)
			return ctx.invoke("AlimentarPet", targetUid, sel)
		end,
	})
end

local function fusePopup(ctx, uid)
	selectionPopup(ctx, {
		title = "Fundir hats", verb = "Fundir", maxLevel = Config.HAT_NIVEL_MAX,
		emptyText = "Você pode usar hats não equipados. Favoritos e protegidos nesta sessão ficam preservados.",
		name = function(_, def) return def.nome end,
		need = function(def, level) return Config.hatXpParaSubir(def, level) end,
		previewLevel = previewHat,
		target = function(data)
			local inst = data.hatsInv and data.hatsInv[uid]
			local def = type(inst) == "table" and Config.hatPorId(inst.id)
			if not def then return nil end
			return def, math.max(1, count(inst.nivel)), count(inst.xp)
		end,
		candidates = function(data)
			local list = {}
			for other, inst in pairs(data.hatsInv or {}) do
				local def = Config.hatPorId(inst.id)
				if def and other ~= uid and not table.find(data.equipados or {}, other) and not protected(ctx, "hat", other) then
					table.insert(list, { key = other, kind = "hat", def = def, level = math.max(1, count(inst.nivel)),
						name = def.nome, xp = Config.hatXpComoComida(def, inst) })
				end
			end
			table.sort(list, function(a, b)
				local ra, rb = T.rar(a.def.raridade).ordem, T.rar(b.def.raridade).ordem
				if ra ~= rb then return ra < rb end
				if a.xp ~= b.xp then return a.xp < b.xp end
				return a.key < b.key
			end)
			return list
		end,
		quickPicks = {
			{ "Comuns", function(c) return c.def.raridade == "comum" end },
			{ "Até raro", function(c) return T.rar(c.def.raridade).ordem <= 3 end },
		},
		remote = function(_, sel)
			return ctx.invoke("FundirHat", uid, sel)
		end,
	})
end

local function renamePopup(ctx, def, uid)
	ctx.popup("Renomear unidade", function(p, w, h)
		p, w, h = scrollableSpace(p, "RenameLayout", w, h, 204)
		local data = ctx.data or {}
		local inst = data.petsInv and data.petsInv[uid]
		T.para(p, "Hint", "O nome aparece acima da unidade para todos os jogadores (até 20 letras).", 0, 0, w, 44, 16, P.text2, T.CENTER)
		local box = T.input(p, "NameBox", 0, 56, w, 58, def.nome, (type(inst) == "table" and inst.apelido) or "", { size = 24, align = T.CENTER })
		box:GetPropertyChangedSignal("Text"):Connect(function()
			if utf8.len(box.Text) and utf8.len(box.Text) > 20 then box.Text = box.Text:sub(1, utf8.offset(box.Text, 21) - 1) end
		end)
		local bw = (w - 12) / 2
		T.button(p, "Reset", "Nome original", 0, h - 54, bw, 54, P.neutral, function()
			local res = ctx.invoke("RenomearPet", uid, "")
			if res and res.ok then ctx.closePopup(); ctx.refresh() end
		end)
		T.button(p, "Save", "Salvar", bw + 12, h - 54, bw, 54, P.success, function()
			local res = ctx.invoke("RenomearPet", uid, box.Text)
			if res and res.ok then ctx.closePopup(); ctx.refresh() end
		end)
	end, 560, 280, { color = P.accent })
end

-- ---------------------------------------------------------------- FICHA
local function detailStats(kind, entry)
	local def, level = entry.def, entry.level
	if kind == "pet" then
		return {
			{ "Dano", "+" .. pct(Config.petBonusDano(def, level)), P.accent, "dano" },
			{ "Bônus de nível", "+" .. tostring(Config.petLevelBonus(def)), P.gold, "nivel" },
			{ "Velocidade", "+" .. T.format(math.floor(Config.petVelocidade(def, level) * 100 + .5) / 100), P.teal, "velocidade" },
		}
	end
	local area = def.mundo and Config.Areas[def.mundo]
	return {
		{ "Dano", "+" .. T.format(Config.hatDanoNoNivel(def.dano, level)), P.accent, "dano" },
		{ "Origem", area and area.nome or "—", P.text2, "areas" },
	}
end

local function renderDetail(ctx, parent, kind, entry, w, h, data)
	if not entry then
		T.emptyState(parent, "NoSelection", "Escolha um item", "Os atributos e ações aparecem aqui.", 0, 0, w, h)
		return
	end
	local def, r = entry.def, entry.rarity
	local owned = entry.quantity > 0
	local equipped = isEquipped(data, kind, entry.key)
	local busy = stateFor(ctx).busy
	local maxed = entry.level >= maxLevel(kind)
	local buttonH = controlHeight(ctx, 44)
	local pad = 14
	local innerW = w - pad * 2
	local actionH = owned and (buttonH * 2 + 18) or (buttonH + 12)
	local scrollH = math.max(100, h - actionH - 8)
	local content = T.scroll(parent, "DetailScroll", pad, pad, innerW, scrollH - pad, P.lineSoft)
	local cw = innerW - 10
	local y = 0
	T.text(content, "SelectedName", kind == "pet" and petName(data, def, entry.key) or def.nome, 0, y, cw, 32, 23, P.text, T.LEFT, "title")
	y += 35
	T.text(content, "Rarity", r.nome .. "  ·  Nv. " .. entry.level .. " / " .. maxLevel(kind), 0, y, cw, 23, 14, r.cor, T.LEFT, "body")
	y += 31
	local artH = math.clamp(h * .28, 120, 178)
	local art = T.frame(content, "SelectedPreview", 0, y, cw, artH, r.cor:Lerp(P.bg1, .92), 0)
	T.corner(art, 9)
	local portrait = T.preview(art, kind, def.id, 5, 5, cw - 10, artH - 10, false, not owned)
	if kind == "pet" and portrait:IsA("ImageLabel") then
		portrait.ScaleType = Enum.ScaleType.Crop
		T.corner(portrait, 7)
	end
	y += artH + 12
	if owned then
		local inst = inventoryOf(data, kind)[entry.key]
		local xp = type(inst) == "table" and count(inst.xp) or 0
		local need = kind == "pet" and Config.petXpParaSubir(def, entry.level) or Config.hatXpParaSubir(def, entry.level)
		T.progress(content, "XpTrack", 0, y, cw, 20, maxed and 1 or math.clamp(xp / math.max(1, need), 0, 1), P.violet,
			{ text = maxed and "NÍVEL MÁXIMO" or (T.format(xp) .. " / " .. T.format(need) .. " XP"), textSize = 12 })
		y += 31
	end
	for i, stat in ipairs(detailStats(kind, entry)) do
		T.stat(content, "Stat" .. i, 0, y, cw, stat[1], stat[2], stat[3], 32)
		y += 36
	end
	-- Compare against the weakest equipped copy, without altering server equip behavior.
	if owned and not equipped then
		local weakest
		for _, uid in ipairs(equippedList(data, kind)) do
			local inst = inventoryOf(data, kind)[uid]
			local other = inst and (kind == "pet" and Config.petPorId(inst.id) or Config.hatPorId(inst.id))
			if other then
				local value = power(kind, { def = other, level = math.max(1, count(inst.nivel)) })
				if not weakest or value < weakest then weakest = value end
			end
		end
		if weakest then
			local delta = power(kind, entry) - weakest
			local amount = kind == "pet" and (T.format(math.floor(math.abs(delta) * 1000 + .5) / 10) .. " p.p.") or T.format(math.abs(delta))
			T.para(content, "Compare", (delta >= 0 and "+" or "−") .. amount .. " de dano em relação ao equipado mais fraco.",
				0, y, cw, 40, 13, delta >= 0 and P.success or P.text2, T.LEFT, "body")
			y += 46
		end
	end
	if owned then
		local key = kind .. ":" .. entry.key
		local fav, locked = ctx.favorites[key] == true, ctx.locks[key] == true
		local bw = (cw - 8) / 2
		T.button(content, "FavoriteToggle", fav and (STAR .. " Favorito") or "Favoritar", 0, y, bw, buttonH, fav and P.gold or P.neutral, function()
			ctx.favorites[key] = not fav or nil; ctx.redrawBody()
		end, { size = 14 })
		T.button(content, "LockToggle", locked and "Protegido" or "Proteger", bw + 8, y, bw, buttonH, locked and P.accent or P.neutral, function()
			ctx.locks[key] = not locked or nil; ctx.redrawBody()
		end, { size = 14 })
		y += buttonH + 6
		T.para(content, "SessionScope", "Favoritos e proteção valem nesta sessão e impedem o consumo pela interface.", 0, y, cw, 38, 12, P.text3, T.LEFT, "body")
		y += 45
		if kind == "pet" then
			T.button(content, "RenameSelected", "Renomear unidade", 0, y, cw, buttonH, P.neutral, function() renamePopup(ctx, def, entry.key) end, { size = 14 })
			y += buttonH + 6
		end
		local total = itemCopies(data, kind, entry.key)
		T.text(content, "Copies", total .. " cópia(s) deste item no inventário", 0, y, cw, 22, 12, P.text3, T.LEFT, "body")
		y += 28
	else
		local area = Config.Areas[kind == "pet" and def.area or def.mundo]
		T.para(content, "Obtain", kind == "pet" and ("Encontre esta unidade no banner de " .. (area and area.nome or "sua ilha") .. ".")
			or ("Obtenha este hat minerando em " .. (area and area.nome or "sua ilha") .. "."), 0, y, cw, 48, 14, P.text2, T.LEFT, "body")
		y += 54
	end
	content.CanvasSize = UDim2.fromOffset(0, y)
	local slots = tonumber(kind == "pet" and data.slotsPets or data.slots)
	local full = not equipped and slots ~= nil and #equippedList(data, kind) >= slots
	if owned then
		local upgrade = T.button(parent, "UpgradeSelected", maxed and "Nível máximo" or (kind == "pet" and "Alimentar unidade" or "Fundir hats"),
			pad, h - buttonH * 2 - 14, innerW, buttonH, P.violet, function()
				if kind == "pet" then feedPopup(ctx, entry.key) else fusePopup(ctx, entry.key) end
			end, { size = 16 })
		T.setEnabled(upgrade, not maxed and not busy)
	end
	local text = not owned and "Não obtido" or (equipped and "Desequipar" or (full and "Todos os slots ocupados" or "Equipar"))
	local main = T.button(parent, "EquipSelected", busy and "Aguarde..." or text, pad, h - buttonH - 6, innerW, buttonH,
		equipped and P.neutral or P.success, function() invoke(ctx, REMOTES[kind].equip, entry.key) end,
		{ size = 17, onDisabled = function()
			if full then ctx.toast("Desequipe um item ou use Melhores para reorganizar os slots.", nil, "info") end
		end })
	T.setEnabled(main, not busy and owned and not full)
end

-- ---------------------------------------------------------------- COLEÇÃO
local SORT_ITEMS = {
	{ id = "recommended", label = "Recomendados" }, { id = "power", label = "Maior dano" },
	{ id = "rarity", label = "Raridade" }, { id = "level", label = "Maior nível" }, { id = "name", label = "Nome A–Z" },
}
local STATUS_ITEMS = {
	{ id = "all", label = "Todos os estados" }, { id = "equipped", label = "Equipados" },
	{ id = "favorite", label = "Favoritos" }, { id = "locked", label = "Protegidos" },
}

function M.render(ctx, parent, w, h)
	w, h = math.max(1, math.floor(w)), math.max(1, math.floor(h))
	local minimum = w < 620 and 510 or 440
	if h < minimum then parent, w, h = scrollableSpace(parent, "InventoryLayout", w, h, 540) end
	local kind = ctx.collection == "pet" and "pet" or "hat"
	local data = ctx.data or {}
	ctx.favorites, ctx.locks = ctx.favorites or {}, ctx.locks or {}
	ctx.inventorySort = ctx.inventorySort or "recommended"
	ctx.inventoryStatus = ctx.inventoryStatus or "all"
	local total = count(kind == "pet" and data.totalPets or data.totalHats)
	local capacity = kind == "pet" and (data.capacidadePets or Config.PET_INVENTARIO_MAX) or (data.capacidadeHats or Config.INVENTARIO_MAX)
	local equipped = equippedList(data, kind)
	local slots = kind == "pet" and data.slotsPets or data.slots
	local stack = w < 620
	local controlH = controlHeight(ctx, 42)
	local filterH = controlHeight(ctx, 38)
	local secondY = controlH + 10
	local thirdY = secondY + filterH + 10
	local headerH = (stack and thirdY or secondY) + filterH + 14
	ctx.inventoryNarrow = stack
	local detailW = stack and w or math.clamp(math.floor(w * .34), 272, 350)
	local gridW = stack and w or w - detailW - 16
	local contentH = h - headerH
	local gridH = contentH
	local detailH = contentH
	local entries, selected = collect(ctx, kind, data)
	local sortW = stack and (w - 10) / 2 or math.min(190, w * .3)
	local searchW = stack and w or w - sortW - 10
	local search, field = T.input(parent, "InventorySearch", 0, 0, searchW, controlH,
		kind == "pet" and "Buscar unidade ou raridade" or "Buscar hat ou raridade", ctx.search, { search = true, size = 16 })
	local serial = 0
	search:GetPropertyChangedSignal("Text"):Connect(function()
		ctx.search = search.Text
		serial += 1
		local current = serial
		task.delay(.18, function()
			if current ~= serial or not search.Parent then return end
			-- Let the player finish typing; focus is restored on the next render.
			ctx.inventorySearchFocused = search:IsFocused()
			ctx.inventorySearchCursor = search.CursorPosition
			ctx.redrawBody()
		end)
	end)
	if ctx.inventorySearchFocused then
		ctx.inventorySearchFocused = false
		task.defer(function()
			if search.Parent then search:CaptureFocus(); search.CursorPosition = math.min(#search.Text + 1, ctx.inventorySearchCursor or #search.Text + 1) end
		end)
	end
	T.dropdown(parent, "InventorySort", stack and 0 or w - sortW, stack and secondY or 0, sortW, stack and filterH or controlH, SORT_ITEMS, ctx.inventorySort, function(id)
		ctx.inventorySort = id; ctx.redrawBody()
	end, { label = "Ordenar" })
	local rarityItems = { { id = "all", label = "Todas as raridades" } }
	local rarities = {}
	for id, def in pairs(T.Rarity) do table.insert(rarities, { id = id, label = def.nome, order = def.ordem }) end
	table.sort(rarities, function(a, b) return a.order < b.order end)
	for _, item in ipairs(rarities) do table.insert(rarityItems, item) end
	local filterW = stack and (w - 10) / 2 or math.min(190, (w - 20) / 3)
	T.dropdown(parent, "InventoryRarity", stack and filterW + 10 or 0, secondY, filterW, filterH, rarityItems, ctx.rarity or "all", function(id)
		ctx.rarity = id ~= "all" and id or nil; ctx.redrawBody()
	end)
	T.dropdown(parent, "InventoryStatus", stack and 0 or filterW + 10, stack and thirdY or secondY, filterW, filterH, STATUS_ITEMS, ctx.inventoryStatus, function(id)
		ctx.inventoryStatus = id; ctx.redrawBody()
	end)
	local scopeX = stack and filterW + 10 or (filterW + 10) * 2
	T.button(parent, "CollectionToggle", ctx.ownedOnly and "Meus itens" or "Coleção completa", scopeX, stack and thirdY or secondY, stack and filterW or math.min(190, w - scopeX), filterH,
		P.neutral, function() ctx.ownedOnly = not ctx.ownedOnly; ctx.redrawBody() end, { size = 14 })
	local gridRoot = T.frame(parent, "InventoryGrid", 0, headerH, gridW, gridH, nil, 1)
	gridRoot.Visible = not (stack and ctx.inventoryDetailOpen and selected)
	local footerH = filterH + 34
	local scrollH = math.max(80, gridH - footerH)
	local scroll = T.scroll(gridRoot, "Items", 0, 0, gridW, scrollH, P.lineSoft)
	local cols = math.max(2, math.floor((gridW + 10) / 142))
	local gap = 10
	local size = math.floor((gridW - 12 - (cols - 1) * gap) / cols)
	local cardH = math.floor(size * .92) + 68
	for i, entry in ipairs(entries) do
		local index = i - 1
		card(ctx, scroll, kind, data, entry, (index % cols) * (size + gap), math.floor(index / cols) * (cardH + gap), size, cardH)
	end
	scroll.CanvasSize = UDim2.fromOffset(0, math.ceil(#entries / cols) * (cardH + gap))
	if #entries == 0 then
		local filtered = ctx.search ~= "" or ctx.rarity ~= nil or ctx.inventoryStatus ~= "all"
		T.emptyState(scroll, "NoResults", filtered and "Nenhum resultado" or (kind == "pet" and "Sua equipe começa aqui" or "Seu inventário está vazio"),
			filtered and "Experimente outro nome ou remova os filtros." or (kind == "pet" and "Invoque uma unidade para aumentar seu dano." or "Encontre hats valiosos ao minerar."),
			0, 0, gridW - 12, scrollH, filtered and "Limpar filtros" or (kind == "pet" and "Ir para invocação" or "Explorar ilhas"), function()
				if filtered then ctx.search, ctx.rarity, ctx.inventoryStatus = "", nil, "all"; ctx.redrawBody()
				elseif kind == "pet" then ctx.open("Summon") else ctx.open("Areas") end
			end)
	end
	local capY = gridH - filterH - 28
	T.text(gridRoot, "Capacity", total .. " / " .. capacity .. " itens", 0, capY, gridW * .55, 22, 14, total >= capacity and P.warning or P.text2, T.LEFT, "body")
	T.text(gridRoot, "EquippedCount", #equipped .. " / " .. tostring(slots or "?") .. " equipados", gridW * .55, capY, gridW * .45, 22, 14, P.text2, T.RIGHT, "body")
	local bw = (gridW - 10) / 2
	local busy = stateFor(ctx).busy
	local best = T.button(gridRoot, "EquipBest", "Equipar melhores", 0, gridH - filterH, bw, filterH, P.accent, function() invoke(ctx, REMOTES[kind].best) end, { size = 14 })
	T.setEnabled(best, not busy and total > 0)
	local clear = T.button(gridRoot, "UnequipAll", "Desequipar todos", bw + 10, gridH - filterH, bw, filterH, P.neutral, function() invoke(ctx, REMOTES[kind].clear) end, { size = 14 })
	T.setEnabled(clear, not busy and #equipped > 0)
	local detailX = stack and 0 or w - detailW
	local detailY = headerH
	if not stack or (ctx.inventoryDetailOpen and selected) then
		if stack then
			T.button(parent, "BackToGrid", "← Voltar à coleção", 0, headerH, w, filterH, P.neutral, function()
				ctx.inventoryDetailOpen = false; ctx.redrawBody()
			end, { size = 15 })
			detailY += filterH + 8; detailH -= filterH + 8
		end
		local panel = T.panel(parent, "Detail", detailX, detailY, detailW, detailH, { bg = P.bg2, radius = 11, strokeColor = P.lineSoft, strokeWidth = 1 })
		renderDetail(ctx, panel, kind, selected, detailW, detailH, data)
	end
	return parent
end

return M

