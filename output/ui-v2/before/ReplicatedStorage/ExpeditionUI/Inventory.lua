-- ============================================================================
-- INVENTÁRIO V2 · grade de cards + personagem em destaque + ficha de atributos
-- Três colunas em tela cheia (grade | destaque | ficha); duas colunas quando estreito.
-- A lógica (equipar, alimentar, fundir, renomear) continua no servidor, pelos mesmos Remotes.
-- ============================================================================
local T = require(script.Parent.Theme)
local Config = require(game.ReplicatedStorage.Config)
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
		if (not ctx.ownedOnly or quantity > 0) and (not ctx.rarity or def.raridade == ctx.rarity)
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
local function card(ctx, parent, kind, data, entry, x, y, size)
	local def = entry.def
	local selected = ctx.selected == entry.key
	local owned = entry.quantity > 0
	local holder = T.new("TextButton", { Name = "Item_" .. entry.key, Text = "", AutoButtonColor = false, BackgroundTransparency = 1,
		BorderSizePixel = 0, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size) }, parent)
	local tile, r = T.tile(holder, "Tile", 0, 0, size, size, def.raridade, { radius = 11, dim = not owned, selected = selected })
	local artSize = size - 8
	if kind == "pet" and Config.PetArte and Config.PetArte[def.id] then
		local art = T.preview(tile, "pet", def.id, 4, 4, artSize, artSize, false, not owned)
		if art:IsA("ImageLabel") then art.ScaleType = Enum.ScaleType.Crop; T.corner(art, 8) end
	else
		T.preview(tile, kind, def.id, 4, 6, artSize, artSize - 16, false, not owned)
	end
	local shade = T.frame(tile, "Shade", 3, size - 34, size - 6, 31, P.ink, 0)
	T.corner(shade, 8)
	T.fade(shade, 90, .85, .05)
	T.text(tile, "Level", owned and ("Lv." .. entry.level) or "—", 5, 3, size - 34, 16, 13, WHITE, T.LEFT, "title")
	if isEquipped(data, kind, entry.key) then
		local badge = T.frame(tile, "Equipped", size - 26, 4, 20, 20, P.success, 0)
		T.corner(badge, 10)
		T.stroke(badge, P.ink, 2)
		T.text(badge, "C", CHECK, 0, 0, 20, 20, 14, WHITE, T.CENTER, "heavy")
	elseif ctx.favorites[kind .. ":" .. entry.key] then
		T.text(tile, "Fav", STAR, size - 24, 3, 18, 18, 15, P.gold, T.CENTER, "heavy")
	end
	T.text(tile, "Name", kind == "pet" and petName(data, def, entry.key) or def.nome, 5, size - 32, size - 10, 16, 13, WHITE, T.CENTER, "title")
	local stat = kind == "pet" and ("+" .. pct(Config.petBonusDano(def, entry.level))) or ("+" .. T.format(Config.hatDanoNoNivel(def.dano, entry.level)))
	T.text(tile, "Power", owned and stat or "não obtido", 5, size - 18, size - 10, 15, 12, owned and r.cor:Lerp(WHITE, .35) or P.text3, T.CENTER, "title")
	local sc = T.new("UIScale", {}, holder)
	holder.MouseEnter:Connect(function() T.tween(sc, .14, { Scale = 1.06 }, Enum.EasingStyle.Back) end)
	holder.MouseLeave:Connect(function() T.tween(sc, .12, { Scale = 1 }, Enum.EasingStyle.Quad) end)
	holder.Activated:Connect(function()
		if ctx.selected == entry.key then return end
		T.som("ui_tab")
		ctx.selected = entry.key
		ctx.redrawBody()
	end)
	return holder
end

-- ---------------------------------------------------------------- SELEÇÃO (alimentar / fundir)
local function selectionPopup(ctx, opts)
	local selection = {}
	local build
	local function rebuild(p, w, h) T.clear(p); build(p, w, h) end
	function build(p, w, h)
		local data = ctx.data or {}
		local def, level, xp = opts.target(data)
		if not def then
			T.text(p, "Gone", "Esse item não está mais no inventário", 10, 20, w - 20, 40, 20, P.text2, T.CENTER, "title")
			return
		end
		local maxed = level >= opts.maxLevel
		local list = opts.candidates(data)
		local valid = {}
		for _, c in ipairs(list) do valid[c.key] = c end
		for key in pairs(selection) do if not valid[key] then selection[key] = nil end end
		local chosen, xpGain = 0, 0
		for key in pairs(selection) do
			chosen += 1
			xpGain += valid[key].xp
		end
		local newLevel, newXp = opts.previewLevel(def, level, xp, xpGain)
		local need = opts.need(def, newLevel)
		T.text(p, "Target", opts.name(data, def) .. "   Nv. " .. level .. (newLevel > level and ("  →  " .. newLevel) or ""), 0, 0, w, 32, 24,
			newLevel > level and P.success or P.text, T.LEFT, "title")
		local frac = newLevel >= opts.maxLevel and 1 or math.clamp(newXp / need, 0, 1)
		T.progress(p, "XpTrack", 0, 38, w, 24, frac, newLevel > level and P.success or P.violet, {
			text = newLevel >= opts.maxLevel and "NÍVEL MÁXIMO" or (T.format(newXp) .. " / " .. T.format(need) .. " XP" .. (xpGain > 0 and ("   (+" .. T.format(xpGain) .. ")") or "")),
			textSize = 14 })
		local bx = 0
		for _, pick in ipairs(opts.quickPicks) do
			local b = T.button(p, "Quick_" .. pick[1], pick[1], bx, 74, 160, 44, P.neutral, function()
				for _, c in ipairs(list) do if pick[2](c) then selection[c.key] = true end end
				rebuild(p, w, h)
			end, { size = 16 })
			T.setEnabled(b, not maxed)
			bx += 168
		end
		local clear = T.button(p, "Clear", "Limpar", bx, 74, 120, 44, P.neutral, function() selection = {}; rebuild(p, w, h) end, { size = 16 })
		T.setEnabled(clear, chosen > 0)
		local confirm = T.button(p, "Confirm", (opts.verb or "Fundir") .. " (" .. chosen .. ")", w - 240, 74, 240, 44, P.success, function()
			if stateFor(ctx).busy then return end
			stateFor(ctx).busy = true
			local sent = selection
			selection = {}
			task.spawn(function()
				pcall(opts.remote, data, sent)
				task.wait(.3)
				stateFor(ctx).busy = false
				if p.Parent then rebuild(p, w, h) end
				ctx.refresh()
			end)
		end, { sound = "ui_compra" })
		T.setEnabled(confirm, chosen > 0 and not maxed and not stateFor(ctx).busy)
		local grid = T.scroll(p, "Candidates", 0, 130, w, h - 130, P.violet)
		if #list == 0 then
			T.text(grid, "Empty", opts.emptyText, 10, 30, w - 30, 60, 18, P.text2, T.CENTER, "title")
			return
		end
		local cols = math.max(4, math.floor((w - 10) / 120))
		local gap = 10
		local size = math.floor((w - 14 - (cols - 1) * gap) / cols)
		for i, c in ipairs(list) do
			local x = ((i - 1) % cols) * (size + gap)
			local y = math.floor((i - 1) / cols) * (size + 34 + gap)
			local picked = selection[c.key] == true
			local cell = T.new("TextButton", { Name = "Pick_" .. c.key, Text = "", AutoButtonColor = false, BackgroundTransparency = 1,
				Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(size, size + 34) }, grid)
			local tile = T.tile(cell, "Tile", 0, 0, size, size, c.def.raridade, { radius = 10, selected = picked })
			T.preview(tile, c.kind, c.def.id, 3, 3, size - 6, size - 6, false)
			T.text(tile, "Level", "Lv." .. c.level, 4, 2, size - 8, 16, 12, WHITE, T.LEFT, "title")
			T.text(cell, "Name", c.name, 2, size - 2, size - 4, 18, 12, P.text, T.CENTER, "title")
			T.text(cell, "Xp", "+" .. T.format(c.xp) .. " XP", 2, size + 14, size - 4, 18, 13, P.gold, T.CENTER, "title")
			if picked then
				local badge = T.frame(tile, "Check", size / 2 - 16, size / 2 - 16, 32, 32, P.success, 0)
				T.corner(badge, 16)
				T.stroke(badge, P.ink, 2)
				T.text(badge, "Mark", CHECK, 0, 0, 32, 32, 20, WHITE, T.CENTER, "heavy")
			end
			cell.Activated:Connect(function()
				if maxed then return end
				T.som("ui_tab")
				selection[c.key] = not picked or nil
				rebuild(p, w, h)
			end)
		end
		grid.CanvasSize = UDim2.fromOffset(0, math.ceil(#list / cols) * (size + 34 + gap))
	end
	ctx.popup(opts.title, build, 1040, 680, { color = P.violet })
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
		emptyText = "Nenhuma unidade livre para usar.\nUnidades equipadas nunca são consumidas.",
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
				if fdef and uid ~= targetUid and not table.find(data.petsEquipados or {}, uid) then
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
			local keys = {}
			for k in pairs(sel) do table.insert(keys, k) end
			return ctx.invoke("AlimentarPet", targetUid, keys)
		end,
	})
end

local function fusePopup(ctx, uid)
	selectionPopup(ctx, {
		title = "Fundir hats", verb = "Fundir", maxLevel = Config.HAT_NIVEL_MAX,
		emptyText = "Nenhum hat livre para fundir.\nHats equipados nunca são consumidos.",
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
				if def and other ~= uid and not table.find(data.equipados or {}, other) then
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
			local keys = {}
			for k in pairs(sel) do table.insert(keys, k) end
			return ctx.invoke("FundirHat", uid, keys)
		end,
	})
end

local function renamePopup(ctx, def, uid)
	ctx.popup("Renomear unidade", function(p, w, h)
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

-- ---------------------------------------------------------------- DESTAQUE + FICHA
local function detailStats(kind, entry)
	local def, level = entry.def, entry.level
	if kind == "pet" then
		return {
			{ "Dano", "+" .. pct(Config.petBonusDano(def, level)), P.danger, "dano" },
			{ "Bônus de nível", "+" .. tostring(Config.petLevelBonus(def)), P.gold, "sorte" },
			{ "Velocidade", "+" .. T.format(math.floor(Config.petVelocidade(def, level) * 100 + .5) / 100), P.accent, "velocidade" },
		}
	end
	local area = def.mundo and Config.Areas[def.mundo]
	return {
		{ "Dano", "+" .. T.format(Config.hatDanoNoNivel(def.dano, level)), P.danger, "dano" },
		{ "Ilha", area and area.nome or "-", P.teal, "areas" },
		{ "Nível", level .. " / " .. maxLevel(kind), P.violet, "nivel" },
	}
end

local function renderDetail(ctx, parent, kind, entry, w, h, data)
	if not entry then
		T.text(parent, "NoSelection", "Nenhum item selecionado", 0, h / 2 - 20, w, 40, 20, P.text3, T.CENTER, "title")
		return
	end
	local tight = h < 470   -- telas baixas (celular deitado): mostra so o essencial
	local def = entry.def
	local r = entry.rarity
	local owned = entry.quantity > 0
	local equipped = isEquipped(data, kind, entry.key)
	local busy = stateFor(ctx).busy
	local maxed = entry.level >= maxLevel(kind)
	local y = 0
	T.text(parent, "SelectedName", kind == "pet" and petName(data, def, entry.key) or def.nome, 0, y, w, tight and 32 or 38, tight and 24 or 28, P.text, T.LEFT, "display")
	y += tight and 34 or 42
	local chip, cw = T.chip(parent, "Rarity", T.upper(r.nome), 0, y, tight and 26 or 30, r.cor, { solid = true, size = tight and 13 or 14 })
	T.chip(parent, "Level", "Nv. " .. entry.level .. " / " .. maxLevel(kind), cw + 8, y, tight and 26 or 30, P.text2, { size = tight and 13 or 14 })
	y += tight and 34 or 40
	-- XP
	local inst = owned and inventoryOf(data, kind)[entry.key]
	if owned and type(inst) == "table" then
		local xp = count(inst.xp)
		local need = kind == "pet" and Config.petXpParaSubir(def, entry.level) or Config.hatXpParaSubir(def, entry.level)
		T.progress(parent, "XpTrack", 0, y, w, tight and 20 or 24, maxed and 1 or math.clamp(xp / need, 0, 1), maxed and P.gold or P.violet, {
			text = maxed and "NÍVEL MÁXIMO" or (T.format(xp) .. " / " .. T.format(need) .. " XP"), textSize = tight and 12 or 14 })
		y += tight and 26 or 32
	end
	-- os botoes ocupam a base; os atributos so entram no espaco que sobra
	local actionsTop = h - 62 - 56 - 10
	if not tight then y += T.section(parent, "Atributos", 0, y, w, r.cor) end
	local rowH = tight and 34 or 44
	local stats = detailStats(kind, entry)
	local mostrados = 0
	for i, stat in ipairs(stats) do
		if y + rowH > actionsTop then break end
		T.statRow(parent, "Stat" .. i, 0, y, w, rowH, stat[4], stat[1], stat[2], stat[3])
		y += rowH + 6
		mostrados += 1
	end
	-- nao coube nenhuma linha (tela baixa): mostra ao menos o atributo principal em uma linha
	if mostrados == 0 and stats[1] and actionsTop - y > 22 then
		T.text(parent, "MainStat", stats[1][1] .. "  " .. stats[1][2], 0, y, w, 24, 17, stats[1][3], T.LEFT, "title")
		y += 28
	end
	local area = kind == "pet" and Config.Areas[def.area] or (def.mundo and Config.Areas[def.mundo])
	local total, free = 0, 0
	if owned then total, free = itemCopies(data, kind, entry.key) end
	local espaco = actionsTop - y   -- o que sobra ate os botoes
	if espaco > 176 then
		-- informações ficam coladas nos botões: o respiro vai entre os blocos, não no fim do painel
		y = math.max(y + 6, actionsTop - 42 - 3 * 38)
		y += T.section(parent, "Informações", 0, y, w, P.text3)
		T.stat(parent, "Origin", 0, y, w, "Ilha de origem", area and area.nome or "-", P.teal)
		y += 38
		T.stat(parent, "Status", 0, y, w, "Status", equipped and "Equipado" or (owned and "No inventário" or "Não obtido"),
			equipped and P.success or (owned and P.text or P.text3))
		y += 38
		T.stat(parent, "Copies", 0, y, w, "Cópias iguais",
			owned and (total .. "  (" .. free .. (free == 1 and " livre)" or " livres)")) or "-", P.violet)
	elseif espaco > 130 then
		y += 6
		T.stat(parent, "Origin", 0, y, w, "Ilha de origem", area and area.nome or "-", P.teal)
		y += 38
		T.stat(parent, "Status", 0, y, w, "Status", equipped and "Equipado" or (owned and "No inventário" or "Não obtido"),
			equipped and P.success or (owned and P.text or P.text3))
	elseif espaco > 44 then
		T.stat(parent, "Copies", 0, y + 4, w, "Status", equipped and "Equipado" or (owned and "No inventário" or "Não obtido"),
			equipped and P.success or (owned and P.text or P.text3))
	end
	-- ações principais
	local slots = tonumber(kind == "pet" and data.slotsPets or data.slots)
	local full = not equipped and slots ~= nil and #equippedList(data, kind) >= slots
	local equipText = not owned and "Não obtido" or (equipped and "Desequipar" or (full and "Limite de slots" or "Equipar"))
	local main = T.button(parent, "EquipSelected", busy and "Aguarde..." or equipText, 0, h - 62, w, 58,
		equipped and P.danger or P.success, function()
			invoke(ctx, REMOTES[kind].equip, entry.key)
		end, { size = 22, sound = "ui_equipar" })
	T.setEnabled(main, not busy and owned and not full)
	local ay = h - 62 - 56
	local bw = (w - 10) / 2
	if kind == "pet" then
		local feed = T.button(parent, "FeedSelected", maxed and "Nível máximo" or "Alimentar", 0, ay, bw, 48, P.violet, function() feedPopup(ctx, entry.key) end, { size = 17 })
		T.setEnabled(feed, not busy and owned and not maxed)
		local ren = T.button(parent, "RenameSelected", "Renomear", bw + 10, ay, bw, 48, P.neutral, function() renamePopup(ctx, def, entry.key) end, { size = 17 })
		T.setEnabled(ren, not busy and owned)
	else
		local fuse = T.button(parent, "FuseSelected", maxed and "Nível máximo" or "Fundir", 0, ay, bw, 48, P.violet, function() fusePopup(ctx, entry.key) end, { size = 17 })
		T.setEnabled(fuse, not busy and owned and not maxed)
		local favKey = kind .. ":" .. entry.key
		local fav = ctx.favorites[favKey] == true
		T.button(parent, "FavoriteToggle", fav and (STAR .. " Favorito") or "Favoritar", bw + 10, ay, bw, 48, fav and P.gold or P.neutral, function()
			ctx.favorites[favKey] = not fav or nil
			ctx.redrawBody()
		end, { size = 17 })
	end
end

local function renderStage(ctx, parent, kind, entry, w, h, data)
	if not entry then return end
	local def = entry.def
	local r = entry.rarity
	local owned = entry.quantity > 0
	local glowSize = math.min(w, h) * .9
	local glow = T.frame(parent, "Glow", (w - glowSize) / 2, (h - glowSize) / 2 - 20, glowSize, glowSize, r.cor, 0)
	T.corner(glow, glowSize / 2)
	T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, .78), T.kp(1, 1) }) }, glow)
	if r.ordem >= 5 and ctx.Notify and ctx.Notify.rays then
		local ray = ctx.Notify.rays(parent, w / 2, h / 2 - 10, glowSize * .62, r.cor, 12, .82)
		ray.ZIndex = 0
	end
	local artH = h - 150
	T.preview(parent, kind, def.id, 20, 28, w - 40, artH, true, not owned)
	-- favorito: estrela no canto do palco (equipar/alimentar/renomear ficam só na ficha, sem duplicar ações)
	if owned then
		local favKey = kind .. ":" .. entry.key
		local fav = ctx.favorites[favKey] == true
		local star = T.new("TextButton", { Name = "FavoriteStar", Text = "", AutoButtonColor = false, BackgroundColor3 = P.bg0, BackgroundTransparency = .25,
			BorderSizePixel = 0, Position = UDim2.fromOffset(w - 58, 4), Size = UDim2.fromOffset(52, 52) }, parent)
		T.corner(star, 26)
		T.stroke(star, fav and P.gold or P.lineSoft, 3)
		T.text(star, "Glyph", STAR, 0, 0, 52, 50, 30, fav and P.gold or P.text3, T.CENTER, "heavy")
		local sc = T.new("UIScale", {}, star)
		star.MouseEnter:Connect(function() T.tween(sc, .14, { Scale = 1.12 }, Enum.EasingStyle.Back) end)
		star.MouseLeave:Connect(function() T.tween(sc, .12, { Scale = 1 }, Enum.EasingStyle.Quad) end)
		star.Activated:Connect(function()
			T.som("ui_toggle")
			ctx.favorites[favKey] = not fav or nil
			ctx.redrawBody()
		end)
		T.hint(star, fav and "Remover dos favoritos" or "Favoritar  ·  sobe para o topo da grade", "left")
	end
	-- nome embaixo
	local plate = T.frame(parent, "Plate", w * .1, h - 88, w * .8, 76, P.bg0, .25)
	T.corner(plate, 14)
	T.stroke(plate, r.cor:Lerp(P.bg0, .3), 2.5)
	T.text(plate, "Name", kind == "pet" and petName(data, def, entry.key) or def.nome, 10, 6, w * .8 - 20, 34, 26, WHITE, T.CENTER, "display")
	T.text(plate, "Rarity", T.upper(r.nome) .. (owned and ("   ·   NV. " .. entry.level) or "   ·   NÃO OBTIDO"), 10, 42, w * .8 - 20, 24, 15, r.cor, T.CENTER, "title")
end

-- ---------------------------------------------------------------- RENDER
function M.render(ctx, parent, w, h)
	w, h = math.max(1, math.floor(w)), math.max(1, math.floor(h))
	local kind = ctx.collection == "pet" and "pet" or "hat"
	local data = ctx.data or {}
	ctx.favorites = ctx.favorites or {}
	local entries, selected = collect(ctx, kind, data)
	local wide = w >= 1080 and h >= 520
	local gridW = wide and math.clamp(math.floor(w * .36), 380, 560) or math.floor(w * .58)
	local detailW = wide and 340 or (w - gridW - 18)
	local stageW = wide and (w - gridW - detailW - 36) or 0

	-- ===== coluna 1: filtros + grade
	local gridRoot = T.frame(parent, "InventoryGrid", 0, 0, gridW, h, nil, 1)
	local filters = { { nil, "Todas", P.text2 } }
	for key, def in pairs(T.Rarity) do table.insert(filters, { key, def.nome, def.cor, def.ordem }) end
	table.sort(filters, function(a, b) return (a[4] or 0) < (b[4] or 0) end)
	local fcols = 4
	local fgap = 6
	local fw = (gridW - (fcols - 1) * fgap) / fcols
	for i, f in ipairs(filters) do
		local sel = ctx.rarity == f[1]
		local chip = T.chip(gridRoot, "Filter" .. i, f[2], ((i - 1) % fcols) * (fw + fgap), math.floor((i - 1) / fcols) * 36, 32, f[3],
			{ solid = sel, size = 14, w = fw })
		local hit = T.new("TextButton", { Name = "Hit", Text = "", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1) }, chip)
		hit.Activated:Connect(function()
			T.som("ui_tab")
			ctx.rarity = (not sel) and f[1] or nil
			ctx.redrawBody()
		end)
		fx = nil
	end
	local footerH = 48
	local scrollTop = 82
	local scrollH = h - scrollTop - footerH - 46
	local scroll = T.scroll(gridRoot, "Items", 0, scrollTop, gridW, scrollH, P.line)
	local cols = math.max(3, math.floor((gridW - 8) / 116))
	local gap = 8
	local size = math.floor((gridW - 12 - (cols - 1) * gap) / cols)
	for index, entry in ipairs(entries) do
		local zero = index - 1
		card(ctx, scroll, kind, data, entry, (zero % cols) * (size + gap), math.floor(zero / cols) * (size + gap), size)
	end
	scroll.CanvasSize = UDim2.fromOffset(0, math.ceil(#entries / cols) * (size + gap))
	if #entries == 0 then
		T.text(scroll, "NoResults", "Nenhum resultado", 0, 40, gridW - 14, 30, 20, P.text2, T.CENTER, "title")
		T.button(scroll, "ClearFilters", "Ver coleção completa", (gridW - 240) / 2, 84, 240, 46, P.gold, function()
			ctx.search, ctx.rarity, ctx.ownedOnly, ctx.selected = "", nil, false, nil
			ctx.refresh()
		end, { size = 16 })
	end
	-- capacidade + ações da grade
	local total = tonumber(kind == "pet" and data.totalPets or data.totalHats) or 0
	local capacity = kind == "pet" and (data.capacidadePets or Config.PET_INVENTARIO_MAX) or (data.capacidadeHats or Config.INVENTARIO_MAX)
	local equipped = equippedList(data, kind)
	local slots = kind == "pet" and data.slotsPets or data.slots
	local capY = h - footerH - 40
	T.icon(gridRoot, "items", 0, capY - 4, 34, 34)
	T.text(gridRoot, "Capacity", "Inventário: " .. count(total) .. " / " .. capacity, 38, capY, gridW * .5, 28, 16,
		total >= capacity and P.danger or P.text, T.LEFT, "title")
	T.text(gridRoot, "EquippedCount", "Equipados: " .. #equipped .. " / " .. tostring(slots or "?"), gridW * .55, capY, gridW * .45, 28, 16, P.success, T.RIGHT, "title")
	local busy = stateFor(ctx).busy
	local fw = (gridW - 16) / 3
	local best = T.button(gridRoot, "EquipBest", "Melhores", 0, h - footerH, fw, footerH, P.success, function() invoke(ctx, REMOTES[kind].best) end, { size = 16 })
	T.setEnabled(best, not busy and total > 0)
	local clear = T.button(gridRoot, "UnequipAll", "Desequipar", fw + 8, h - footerH, fw, footerH, P.danger, function() invoke(ctx, REMOTES[kind].clear) end, { size = 16 })
	T.setEnabled(clear, not busy and #equipped > 0)
	T.button(gridRoot, "CollectionToggle", ctx.ownedOnly and "Ver coleção" or "Só os meus", 2 * (fw + 8), h - footerH, fw, footerH, ctx.ownedOnly and P.neutral or P.gold, function()
		ctx.ownedOnly = not ctx.ownedOnly
		ctx.redrawBody()
	end, { size = 16 })

	-- ===== coluna 2: destaque
	if wide then
		local stage = T.frame(parent, "Stage", gridW + 18, 0, stageW, h, nil, 1)
		renderStage(ctx, stage, kind, selected, stageW, h, data)
	end

	-- ===== coluna 3: ficha
	local detail = T.panel(parent, "Detail", w - detailW, 0, detailW, h, { bg = P.bg2, radius = 16, strokeColor = selected and selected.rarity.cor:Lerp(P.bg2, .35) or P.lineSoft })
	local pad = T.frame(detail, "Pad", 16, 16, detailW - 32, h - 32, nil, 1)
	if not wide and selected then
		local ph = math.min(220, h * .3)
		local tile = T.tile(pad, "Art", 0, 0, detailW - 32, ph, selected.def.raridade, { radius = 12, animated = true })
		T.preview(tile, kind, selected.def.id, 8, 8, detailW - 48, ph - 16, true, selected.quantity == 0)
		local sub = T.frame(pad, "Sub", 0, ph + 12, detailW - 32, h - 32 - ph - 12, nil, 1)
		renderDetail(ctx, sub, kind, selected, detailW - 32, h - 32 - ph - 12, data)
	else
		renderDetail(ctx, pad, kind, selected, detailW - 32, h - 32, data)
	end
	return parent
end

return M

