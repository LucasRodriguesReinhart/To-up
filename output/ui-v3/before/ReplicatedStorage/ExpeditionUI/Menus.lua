-- UI V2: each page shares Theme components and preserves the existing server contract.
local T = require(script.Parent.Theme)
local Config = require(game.ReplicatedStorage.Config)
local Mon = require(game.ReplicatedStorage:WaitForChild("MonetizacaoConfig"))
local Players = game:GetService("Players")
local AudioPreferences = require(game.ReplicatedStorage:WaitForChild("AudioPreferences"))
local P, M = T.P, {}
local WHITE = Color3.new(1, 1, 1)
local GAP = 12

local function hasArea(ctx, id)
	return ctx.data and ctx.data.areas and ctx.data.areas[id] == true
end

local function panel(p, name, x, y, w, h, selected)
	return T.panel(p, name, x, y, w, h, { bg = P.bg2, radius = 8,
		strokeColor = selected and P.accent or P.lineSoft, strokeWidth = 1 })
end

-- Art is composed behind the content, with a quiet reading edge and crystal facets.
local function artSurface(p, name, x, y, w, h, color, scene)
	local f = panel(p, name, x, y, w, h)
	f.ClipsDescendants = true
	f.BackgroundColor3 = P.bg2:Lerp(color, .2)
	if scene then
		local landscape = T.image(f, "Landscape", scene, 0, 0, w, h, Color3.fromRGB(146, 157, 190), .12)
		landscape.ScaleType = Enum.ScaleType.Crop
	end
	local shade = T.frame(f, "ReadingShade", 0, 0, w, h, P.bg0, 0)
	T.new("UIGradient", { Rotation = 0, Transparency = NumberSequence.new({ T.kp(0, .04), T.kp(.46, .2), T.kp(1, .72) }) }, shade)
	local tint = T.frame(f, "EnergyTint", 0, 0, w, h, color, 0)
	T.new("UIGradient", { Rotation = 0, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.45, .97), T.kp(1, .65) }) }, tint)
	T.slant(f, "FacetA", w * .7, -h * .15, w * .16, h * 1.3, color, { alpha = .86, tilt = 22 })
	T.slant(f, "FacetB", w * .88, -h * .15, w * .08, h * 1.3, WHITE, { alpha = .95, tilt = 22 })
	return f
end

local function heroCharacter(p, def, x, y, w, h)
	local art = Config.PetArte and Config.PetArte[def.id]
	if art and (art.corpo or art.busto) then return T.image(p, "Hero_" .. def.id, art.corpo or art.busto, x, y, w, h) end
	return T.preview(p, "pet", def.id, x, y, w, h, false)
end

local function text(p, name, value, x, y, w, h, size, color, align, font)
	return T.text(p, name, value, x, y, math.max(1, w), h, size or 16, color or P.text,
		align or T.LEFT, font or "body")
end

local function label(p, name, value, x, y, w, h, size, color)
	return text(p, name, value, x, y, w, h, size or 18, color, T.LEFT, "title")
end

local function currency(p, name, amount, x, y, w, h, size)
	T.icon(p, "coins", x, y + (h - 24) / 2, 24, 24)
	return text(p, name, T.format(amount or 0), x + 30, y, w - 30, h, size or 20, P.gold, T.LEFT, "title")
end

-- Persist the in-flight guard across data-driven redraws. Every result still comes from ctx.invoke.
local function action(ctx, p, name, caption, x, y, w, h, fn, enabled, reason, tone, guard, visual)
	ctx.menuPending = ctx.menuPending or {}
	local key = guard or name
	local button
	local function allowed()
		if type(enabled) == "function" then return enabled() end
		return enabled ~= false
	end
	local active = allowed() and not ctx.menuPending[key]
	button = T.button(p, name, ctx.menuPending[key] and "Aguarde..." or caption, x, y, w, h, tone or P.accent, function()
		if ctx.menuPending[key] then return end
		ctx.menuPending[key] = true
		T.setEnabled(button, false)
		local cap = button:FindFirstChild("Face") and button.Face:FindFirstChild("Caption")
		if cap then cap.Text = "Aguarde..." end
		local ok, err = pcall(fn)
		ctx.menuPending[key] = nil
		if button.Parent then
			T.setEnabled(button, allowed())
			if cap then cap.Text = caption end
		else ctx.refresh() end
		if not ok then
			warn("[Menus V2] " .. name .. ": " .. tostring(err))
			ctx.toast("Não foi possível concluir. Tente novamente.", nil, "error")
		end
	end, { size = visual and visual.size or 16, onDisabled = reason and function() ctx.toast(reason, nil, "info") end or nil })
	T.setEnabled(button, active)
	return button
end

local function areaOptions(ctx, bannersOnly)
	local items = {}
	for _, a in ipairs(Config.Areas) do
		if not bannersOnly or Config.Gachas[a.id] then
			table.insert(items, { id = a.id, label = a.nome .. (hasArea(ctx, a.id) and "" or " · bloqueada") })
		end
	end
	return items
end

local function areaUnlock(ctx, p, a, x, y, w, h)
	local nextArea = ctx.nextArea(ctx.data)
	local sequential = nextArea and nextArea.id == a.id
	local have = ctx.data.moeda or 0
	local afford = have >= (a.custo or 0)
	local reason = sequential and ("Faltam " .. T.format(math.max(0, a.custo - have)) .. " moedas")
		or "Desbloqueie a ilha anterior primeiro."
	return action(ctx, p, "Unlock_" .. a.id, "Desbloquear", x, y, w, h,
		function() ctx.buyArea(a.id) end, sequential and afford, reason)
end

-- Store: an immediate next upgrade and a readable complete catalog, without a promotional hero.
local function equipmentStore(ctx, p, w, h)
	local d = ctx.data
	local pick = ctx.storeTab == "Picaretas"
	local defs = pick and Config.Picaretas or Config.Mochilas
	local currentId = pick and d.picareta or d.mochilaTier
	local currentIndex = 1
	for i, def in ipairs(defs) do if def.id == currentId then currentIndex = i end end
	local current = defs[currentIndex]
	local nextDef
	if pick then nextDef = ctx.nextPickaxe(d) else nextDef = defs[currentIndex + 1] end
	local function owned(i, def)
		if pick then return i == 1 or (d.picaretasCompradas and d.picaretasCompradas[def.id] == true) end
		return i <= currentIndex
	end
	local function buy(def)
		ctx.confirm(def.nome, pick and "A picareta será adicionada ao seu equipamento. Você poderá equipá-la após a compra."
			or "Sua mochila será substituída pela nova, com maior capacidade.", function()
			local res = ctx.invoke(pick and "ComprarPicareta" or "ComprarMochila", def.id)
			if res and res.ok then ctx.refresh() end
		end, { cost = def.custo, confirmText = "Comprar", tone = P.accent })
	end
	local narrow = w < 620
	local topH = narrow and 228 or 166
	local top = artSurface(p, "NextUpgrade", 0, 0, w, topH, P.accent, nil)
	local artS, mainX, actionW = narrow and 76 or 100, narrow and 106 or 128, narrow and 176 or 180
	local mainW = narrow and w - mainX - 16 or w - mainX - actionW - 36
	label(top, "Section", nextDef and "Próxima melhoria" or "Categoria concluída", 16, 10, w - 32, 24, 14, P.text2)
	local shown = nextDef or current
	T.slant(top, "ToolPlate", 4, 32, narrow and 98 or 112, narrow and 76 or 118, P.accent, { alpha = .86, tilt = 18 })
	if pick then T.preview(top, "pickaxe", shown.id, 16, 42, artS, artS, false)
	else T.statIcon(top, "capacidade", 24, 48, 84, 84) end
	T.para(top, "Name", shown.nome, mainX, 40, mainW, narrow and 48 or 30, narrow and 21 or 23, P.text, T.LEFT, "title")
	text(top, "Current", "Atual: " .. current.nome, narrow and 16 or mainX, narrow and 108 or 74, narrow and w - 32 or mainW, 22, 14, P.text2)
	local statText
	if nextDef then
		statText = pick and string.format("Dano x%.2f → x%.2f  ·  Golpe %.2fs → %.2fs", current.mult, nextDef.mult, current.intervalo, nextDef.intervalo)
			or ("Capacidade " .. T.format(current.capacidade) .. " → " .. T.format(nextDef.capacidade))
	else statText = "Você possui a melhor opção desta categoria." end
	T.para(top, "Comparison", statText, narrow and 16 or mainX, narrow and 136 or 100, narrow and w - 32 or mainW, narrow and 36 or 44, 15, P.text2, T.LEFT)
	local ax = w - actionW - 16
	if nextDef then
		currency(top, "Cost", nextDef.custo, narrow and 16 or ax, narrow and 180 or 40, narrow and w - actionW - 40 or actionW, 28, 22)
		local afford = (d.moeda or 0) >= nextDef.custo
		if not narrow then text(top, "Available", afford and "Saldo suficiente" or ("Faltam " .. T.format(nextDef.custo - (d.moeda or 0))), ax, 72, actionW, 20, 13, afford and P.success or P.text2) end
		action(ctx, top, "BuyNext", "Comprar melhoria", ax, narrow and 174 or 104, actionW, 52, function() buy(nextDef) end,
			afford, "Moedas insuficientes para esta melhoria.")
	else
		T.chip(top, "Complete", "✓ COMPLETO", ax, narrow and 184 or 70, 32, P.success, { size = 13, w = actionW })
	end
	local listY = topH + 14
	local scroll = T.scroll(p, "Catalog", 0, listY, w, math.max(80, h - listY), P.accent)
	local cw = w - 14
	local y = T.section(scroll, pick and "Picaretas" or "Mochilas", 0, 0, cw, P.accent, nil, #defs .. " opções")
	for i, def in ipairs(defs) do
		local inUse, isOwned = def.id == currentId, owned(i, def)
		local rowH = narrow and 172 or 116
		local row = panel(scroll, "Product_" .. def.id, 0, y, cw, rowH, inUse)
		local x, bw = 102, 176
		local descW = narrow and cw - x - 14 or cw - x - bw - 34
		if pick then T.preview(row, "pickaxe", def.id, 10, 14, 78, 82, false)
		else T.statIcon(row, "capacidade", 16, 24, 64, 64) end
		T.para(row, "Name", def.nome, x, 12, descW, narrow and 42 or 27, 19, P.text, T.LEFT, "title")
		local area = Config.areaPorId(def.mundo or 1)
		text(row, "Area", "Nível " .. i .. " · " .. (area and area.nome or ""), x, narrow and 57 or 42, descW, 19, 13, P.text3)
		text(row, "Stats", pick and string.format("Dano x%.2f  ·  %.2fs por golpe", def.mult, def.intervalo)
			or (T.format(def.capacidade) .. " de capacidade"), narrow and 14 or x, narrow and 87 or 69, narrow and cw - 28 or descW, 22, 15, P.text2)
		local bx = cw - bw - 14
		if inUse then
			T.chip(row, "Equipped", "✓ EQUIPADA", bx, narrow and 126 or 40, 32, P.accent, { size = 13, w = bw })
		elseif isOwned then
			text(row, "Owned", "Adquirida", narrow and 14 or bx, narrow and 127 or 14, narrow and cw - bw - 40 or bw, 22, 14, P.text2)
			if pick then
				action(ctx, row, "Equip_" .. def.id, "Equipar", bx, narrow and 112 or 52, bw, 52, function()
					local res = ctx.invoke("EquiparPicareta", def.id)
					if res and res.ok then ctx.refresh() end
				end)
			else T.chip(row, "OwnedState", "✓ ADQUIRIDA", bx, narrow and 126 or 50, 32, P.text3, { size = 13, w = bw }) end
		else
			currency(row, "Price", def.custo, narrow and 14 or bx, narrow and 123 or 12, narrow and cw - bw - 40 or bw, 30, 19)
			local afford = (d.moeda or 0) >= def.custo
			action(ctx, row, "Buy_" .. def.id, "Comprar", bx, narrow and 112 or 52, bw, 52, function() buy(def) end, afford,
				"Faltam " .. T.format(math.max(0, def.custo - (d.moeda or 0))) .. " moedas.")
		end
		y += rowH + 12
	end
	scroll.CanvasSize = UDim2.fromOffset(0, y)
end

local PASS_ICON = { VIP = "vip", Lucky = "shiny", HatSlot = "units", Inventario = "items", AutoSell = "forge",
	BoostSorte = "potion", BoostMoedas = "coins", PackP = "coins", PackM = "coins", PackG = "coins", InvocarChefe = "summon", Starter = "store" }

local function passesStore(ctx, p, w, h)
	local d = ctx.data
	local scroll = T.scroll(p, "PassCatalog", 0, 0, w, h, P.accent)
	local cw, y = w - 14, 0
	local groups = { { title = "Gamepasses", hint = "Benefícios permanentes", defs = Mon.PASSES },
		{ title = "Boosts e pacotes", hint = "Consulte o conteúdo e a duração", defs = Mon.PRODUTOS } }
	local cols = cw >= 1000 and 3 or (cw >= 570 and 2 or 1)
	local cardW = (cw - (cols - 1) * GAP) / cols
	for _, group in ipairs(groups) do
		y += T.section(scroll, group.title, 0, y, cw, P.accent, nil, group.hint)
		for i, def in ipairs(group.defs) do
			local owned = (d.passes and d.passes[def.chave] == true) or (def.starter and d.compras and (d.compras[def.chave] or 0) > 0)
			local productTone = owned and P.success or ((def.boost == "sorte" or def.chave == "Lucky") and P.violet or P.accent)
			local card = artSurface(scroll, "Product_" .. def.chave, ((i - 1) % cols) * (cardW + GAP), y + math.floor((i - 1) / cols) * 234, cardW, 222, productTone, nil)
			T.slant(card, "IconPlate", 8, 8, 62, 58, productTone, { alpha = .7, tilt = 20 })
			T.icon(card, PASS_ICON[def.chave] or "store", 12, 12, 52, 52)
			label(card, "Name", def.nome, 72, 14, cardW - 86, 26, 19)
			local state = owned and "✓ Adquirido" or (def.minutos and (def.minutos .. " minutos") or (def.starter and "Uma vez por conta" or (group.defs == Mon.PASSES and "Permanente" or "Uso imediato")))
			text(card, "State", state, 72, 42, cardW - 86, 20, 13, owned and P.success or P.text3)
			T.para(card, "Benefit", def.desc or "", 16, 76, cardW - 32, 74, 15, P.text2, T.LEFT)
			local configured = (def.id or 0) > 0
			local caption = owned and "Adquirido" or (configured and (tostring(def.robux) .. " Robux") or "Em breve")
			action(ctx, card, "Robux_" .. def.chave, caption, 14, 158, cardW - 28, 52,
				function() ctx.invoke("ComprarRobux", def.chave) end, not owned and configured,
				owned and "Este benefício já está na sua conta." or "Este produto ainda não está disponível.", P.accent)
		end
		y += math.ceil(#group.defs / cols) * 234 + 12
	end
	text(scroll, "PriceNote", "A confirmação de compra do Roblox mostra o preço final em Robux.", 0, y, cw, 26, 14, P.text3)
	scroll.CanvasSize = UDim2.fromOffset(0, y + 38)
end

function M.store(ctx, p, w, h)
	if ctx.storeTab == "Passes" then passesStore(ctx, p, w, h) else equipmentStore(ctx, p, w, h) end
end

function M.areas(ctx, p, w, h)
	local d = ctx.data
	local scroll = T.scroll(p, "Destinations", 0, 0, w, h, P.accent)
	local cw = w - 14
	local quick = { { "Lobby", w < 620 and "Lobby" or "Praça central", function() ctx.travel("area", 0) end },
		{ "Forge", w < 620 and "Vender" or "Vender com Ignis", function() ctx.open("Forge") end },
		{ "Equipment", "Equipamentos", function() ctx.storeTab = "Picaretas"; ctx.open("Store") end } }
	local qw = (cw - 24) / 3
	for i, q in ipairs(quick) do action(ctx, scroll, "Quick_" .. q[1], q[2], (i - 1) * (qw + 12), 0, qw, 52, q[3], true, nil, P.neutral) end
	local count = 0
	for _, a in ipairs(Config.Areas) do if hasArea(ctx, a.id) then count += 1 end end
	local y = 68 + T.section(scroll, "Ilhas de mineração", 0, 68, cw, P.accent, nil, count .. " / " .. #Config.Areas .. " liberadas")
	local cols = cw >= 1000 and 3 or (cw >= 580 and 2 or 1)
	local cardW, cardH = (cw - (cols - 1) * GAP) / cols, 252
	local nextArea = ctx.nextArea(d)
	local current = Players.LocalPlayer:GetAttribute("CurrentAreaId") or 0
	for i, a in ipairs(Config.Areas) do
		local unlocked, here = hasArea(ctx, a.id), current == a.id
		local card = panel(scroll, "Island_" .. a.id, ((i - 1) % cols) * (cardW + GAP), y + math.floor((i - 1) / cols) * (cardH + GAP), cardW, cardH, here)
		local theme = Config.Temas[a.tema]
		local tone = theme and theme.cor or P.accent
		local thumb = artSurface(card, "IslandArt", 0, 0, cardW, 94, tone, T.areaImage(a.id))
		T.slant(thumb, "IslandNumberPlate", 10, 10, 84, 24, P.bg0, { alpha = .16 })
		label(thumb, "IslandNumber", "ILHA " .. a.id, 22, 10, 62, 24, 12, P.text)
		if not unlocked then T.lock(thumb, cardW - 42, 15, 24, P.text2) end
		T.frame(card, "ThemeLine", 12, 94, cardW - 24, 2, tone, .22)
		label(card, "Name", a.nome, 14, 102, cardW - 28, 28, 21)
		local status = here and "✓ Você está aqui" or (unlocked and (Config.Gachas[a.id] and "Mineração · banner disponível" or "Mineração") or (nextArea and nextArea.id == a.id and "Próxima ilha" or "Ilha bloqueada"))
		text(card, "State", status, 14, 134, cardW - 28, 20, 14, here and P.accent or P.text2)
		if unlocked then
			text(card, "FreeTravel", "Viagem gratuita", 14, 160, cardW - 28, 18, 13, P.text3)
			action(ctx, card, "Travel_" .. a.id, here and "Você está aqui" or "Viajar", 14, 186, cardW - 28, 52,
				function() ctx.travel("area", a.id) end, not here, "Você já está nesta ilha.")
		elseif nextArea and nextArea.id == a.id then
			currency(card, "Cost", a.custo, 14, 158, cardW - 28, 24, 18)
			areaUnlock(ctx, card, a, 14, 186, cardW - 28, 52)
		else
			local previous = Config.areaPorId(a.id - 1)
			T.para(card, "Requirement", "Requer " .. (previous and previous.nome or "a ilha anterior") .. ".", 14, 164, cardW - 28, 48, 14, P.text3, T.LEFT)
		end
	end
	scroll.CanvasSize = UDim2.fromOffset(0, y + math.ceil(#Config.Areas / cols) * (cardH + GAP))
end

local function probabilities(ctx, id)
	local out = {}
	for _, c in ipairs(Config.chancesGacha(id, ctx.data and ctx.data.luckyMult or 1) or {}) do
		table.insert(out, { key = c.raridade, pct = c.pct, def = T.rar(c.raridade) })
	end
	table.sort(out, function(a, b) return a.def.ordem > b.def.ordem end)
	return out
end

function M.rates(ctx)
	local id = ctx.bannerArea or 1
	local rows = probabilities(ctx, id)
	local pity = ctx.data and ctx.data.pity or { l = 0, m = 0 }
	ctx.popup("Chances de invocação", function(p, w, h)
		local scroll = T.scroll(p, "Rates", 0, 0, w, h, P.accent)
		local cw = w - 14
		T.para(scroll, "Pity", ("Lendário+ em até %d giros · Mítico+ em até %d giros."):format(
			math.max(0, Config.PITY_LENDARIO - (pity.l or 0)), math.max(0, Config.PITY_MITICO - (pity.m or 0))), 0, 0, cw, 42, 16, P.text, T.LEFT)
		text(scroll, "Luck", "Percentuais com a sua sorte atual aplicada.", 0, 46, cw, 22, 14, P.text2)
		local y = 80
		for _, r in ipairs(rows) do
			local row = panel(scroll, "Rarity_" .. r.key, 0, y, cw, 74)
			label(row, "Name", "◆ " .. r.def.nome, 12, 10, cw - 136, 24, 17, r.def.cor)
			text(row, "Chance", string.format("%.3f%%", r.pct), cw - 116, 10, 104, 24, 19, P.text, T.RIGHT, "title")
			local names = {}
			for _, def in ipairs(Config.petsDaRaridade(r.key, id)) do table.insert(names, def.nome) end
			text(row, "Units", table.concat(names, ", "), 12, 40, cw - 24, 22, 14, P.text2)
			y += 84
		end
		scroll.CanvasSize = UDim2.fromOffset(0, y)
	end, 610, math.min(650, 176 + #rows * 84), { color = P.accent })
end

function M.summon(ctx, p, w, h)
	local d = ctx.data
	local id = ctx.bannerArea or 1
	if not Config.Gachas[id] then id = 1; ctx.bannerArea = id end
	local a, g = Config.areaPorId(id), Config.Gachas[id]
	local unlocked = hasArea(ctx, id)
	local near = ctx.nearBanner and ctx.nearBanner(id) or false
	local all, odds, featured = {}, {}, {}
	for _, def in ipairs(Config.Pets) do if def.area == id then table.insert(all, def) end end
	for _, row in ipairs(probabilities(ctx, id)) do odds[row.key] = row.pct end
	table.sort(all, function(x, y)
		local xr, yr = T.rar(x.raridade).ordem, T.rar(y.raridade).ordem
		if xr ~= yr then return xr > yr end
		return x.id < y.id
	end)
	for _, def in ipairs(all) do
		local known = d.index and d.index.pets and d.index.pets[def.id]
		if def.raridade ~= "secreto" or known then
			table.insert(featured, def)
			if #featured == 3 then break end
		end
	end
	local function showUnits()
		ctx.popup("Unidades · " .. a.nome, function(host, pw, ph)
			local list = T.scroll(host, "BannerUnits", 0, 0, pw, ph, P.violet)
			list.ClipsDescendants = true
			local cw = pw - 14
			local cols = math.max(2, math.floor((cw + 12) / 164))
			local cardW, cardH = (cw - (cols - 1) * 12) / cols, 224
			for i, def in ipairs(all) do
				local r = T.rar(def.raridade)
				local known = d.index and d.index.pets and d.index.pets[def.id]
				local secret = def.raridade == "secreto" and not known
				local card = T.tile(list, "Unit_" .. def.id, ((i - 1) % cols) * (cardW + 12), math.floor((i - 1) / cols) * (cardH + 12), cardW, cardH, def.raridade, { animated = false, dim = secret })
				if secret then T.lock(card, cardW / 2 - 30, 44, 60, P.text3)
				else T.preview(card, "pet", def.id, 6, 8, cardW - 12, 138, false) end
				label(card, "Name", secret and "???" or def.nome, 8, 147, cardW - 16, 26, 20)
				text(card, "Rarity", r.nome, 8, 177, cardW - 16, 22, 16, r.cor, T.CENTER, "title")
				text(card, "Odds", string.format("%.2f%% da raridade", odds[def.raridade] or 0), 8, 201, cardW - 16, 18, 12, P.text2, T.CENTER)
			end
			if #all == 0 then T.emptyState(list, "Empty", "Nenhuma unidade", "Este banner ainda não tem unidades disponíveis.", 0, 0, cw, 200) end
			list.CanvasSize = UDim2.fromOffset(0, math.max(200, math.ceil(#all / cols) * (cardH + 12)))
		end, 850, 620, { color = P.violet })
	end
	local narrow = w < 840
	local requiredH = narrow and 636 or 530
	if h < requiredH then
		local outer = T.scroll(p, "SummonPage", 0, 0, w, h, P.violet)
		outer.ClipsDescendants = true
		w, h = w - 14, requiredH
		p = T.frame(outer, "Content", 0, 0, w, h, nil, 1)
		outer.CanvasSize = UDim2.fromOffset(0, h)
	end
	-- The selector is made from actual island art: a rail on desktop and a swipe row on portrait.
	local railW = narrow and w or math.clamp(w * .185, 184, 254)
	local railH = narrow and 82 or h
	local rail = T.scroll(p, "Banners", 0, 0, railW, railH, P.violet)
	rail.ClipsDescendants = true
	if narrow then rail.ScrollingDirection = Enum.ScrollingDirection.X end
	local thumbW, thumbH = narrow and 172 or railW - 12, narrow and 72 or 100
	local bannerCount = 0
	for _, island in ipairs(Config.Areas) do
		if Config.Gachas[island.id] then
			local selected = island.id == id
			local tone = Config.Temas[island.tema] and Config.Temas[island.tema].cor or P.violet
			local bx, by = narrow and bannerCount * (thumbW + 10) or 0, narrow and 0 or bannerCount * (thumbH + 12)
			local b = T.new("TextButton", { Name = "Banner_" .. island.id, Position = UDim2.fromOffset(bx, by),
				Size = UDim2.fromOffset(thumbW, thumbH), Text = "", AutoButtonColor = false,
				BackgroundColor3 = Color3.fromRGB(8, 7, 14), BorderSizePixel = 0, ClipsDescendants = true }, rail)
			T.corner(b, 8)
			T.new("UIStroke", { Name = "Selection", Color = selected and WHITE or tone, Thickness = selected and 4 or 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, b)
			local art = T.image(b, "Island", T.areaImage(island.id), 2, 2, thumbW - 4, thumbH - 4, WHITE, selected and .12 or .35)
			art.ScaleType = Enum.ScaleType.Crop
			local shadow = T.frame(b, "ReadingShade", 2, 2, thumbW - 4, thumbH - 4, Color3.new(0, 0, 0), 0)
			T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, .7), T.kp(.5, .48), T.kp(1, .04) }) }, shadow)
			T.para(b, "Name", island.nome, 10, narrow and 8 or 12, thumbW - 20, narrow and 29 or 54, narrow and 19 or 25, selected and WHITE or tone, T.LEFT, "title")
			text(b, "State", hasArea(ctx, island.id) and (selected and "BANNER SELECIONADO" or "Ver unidades da ilha") or "Ilha bloqueada", 10, thumbH - 27, thumbW - 20, 22, narrow and 11 or 13, WHITE, T.LEFT, "heavy")
			T.bindInteraction(b, function() ctx.bannerArea = island.id; ctx.refresh() end)
			bannerCount += 1
		end
	end
	rail.CanvasSize = narrow and UDim2.fromOffset(bannerCount * (thumbW + 10), 0) or UDim2.fromOffset(0, bannerCount * (thumbH + 12))
	local stageX, stageY = narrow and 0 or railW + 16, narrow and 96 or 0
	local sw, sh = w - stageX, h - stageY
	local stage = T.frame(p, "BannerHero", stageX, stageY, sw, sh, Color3.fromRGB(9, 6, 19), 0)
	stage.ClipsDescendants = true
	T.corner(stage, 10)
	T.new("UIStroke", { Color = P.violet, Thickness = 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, stage)
	local scene = T.image(stage, "IslandScene", T.areaImage(id), 0, 0, sw, sh, WHITE, .16)
	scene.ScaleType = Enum.ScaleType.Crop
	T.frame(stage, "SceneShade", 0, 0, sw, sh, Color3.fromRGB(8, 4, 20), .43)
	T.image(stage, "StageRays", T.Assets.rays, sw * .5 - sh * .7, -sh * .2, sh * 1.4, sh * 1.4, P.violet, .74)
	local imageBottom = narrow and sh - 120 or sh + 35
	local centralSize = narrow and sw * .85 or math.min(sw * .59, sh * 1.04)
	local sideSize = centralSize * .87
	local centers = { sw * .5, sw * .18, sw * .82 }
	for _, i in ipairs({ 2, 3, 1 }) do
		local def = featured[i]
		if def then
			local size = i == 1 and centralSize or sideSize
			local top = narrow and (imageBottom - size - (i == 1 and 28 or 0)) or (sh * .11 + (i == 1 and -28 or 40))
			local art = Config.PetArte and Config.PetArte[def.id]
			if art and (art.busto or art.corpo) then
				T.image(stage, "Hero_" .. def.id, art.busto or art.corpo, centers[i] - size / 2, top, size, size)
			else heroCharacter(stage, def, centers[i] - size / 2, top, size, size) end
		end
	end
	local bottomMaskH = narrow and 272 or 242
	local bottomMask = T.frame(stage, "ActionShade", 0, sh - bottomMaskH, sw, bottomMaskH, Color3.fromRGB(7, 4, 14), 0)
	T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.23, .28), T.kp(.65, .04), T.kp(1, 0) }) }, bottomMask)
	if narrow then
		text(stage, "IslandNumber", "BANNER DA ILHA " .. id, 12, 8, sw - 24, 22, 14, P.violet, T.CENTER, "title")
		T.text(stage, "BannerName", a.nome, 12, 29, sw - 24, 43, 31, WHITE, T.CENTER, "display", 3)
		text(stage, "Location", unlocked and (near and "✓ No banner · pronto para invocar" or "Viaje até o banner desta ilha") or "Ilha bloqueada", 12, 75, sw - 24, 23, 13, near and P.success or P.text2, T.CENTER, "heavy")
	else
		text(stage, "IslandNumber", "ILHA " .. id .. " · INVOCAÇÃO", 20, 16, sw * .34, 26, 18, WHITE, T.LEFT, "title")
		T.text(stage, "BannerName", a.nome, sw * .36, 10, sw * .62 - 12, 65, math.min(48, sw / 20), P.violet, T.RIGHT, "display", 3)
		text(stage, "Location", unlocked and (near and "✓ Pronto para invocar" or "Viaje até o banner") or "Ilha bloqueada", 20, 46, sw * .33, 24, 16, near and P.success or P.text2, T.LEFT, "heavy")
		text(stage, "BannerSubtitle", "Reúna as unidades desta ilha", sw * .47, 74, sw * .51 - 12, 25, 18, WHITE, T.RIGHT, "title")
	end
	if ctx.lastSummonResults and #ctx.lastSummonResults > 0 and ctx.showLastSummon then
		T.button(stage, "LastResult", narrow and "Resultado" or "Último resultado", 14, narrow and 107 or 82, narrow and 124 or 168, 52, P.neutral, ctx.showLastSummon, { size = 15 })
	end
	local namesY = narrow and sh - 304 or sh - 292
	local nameW = narrow and sw * .31 or sw * .29
	for i, def in ipairs(featured) do
		local x = math.clamp(centers[i] - nameW / 2, 7, sw - nameW - 7)
		local r = T.rar(def.raridade)
		if i == 1 and not narrow then text(stage, "Featured", "EM DESTAQUE", x, namesY - 25, nameW, 22, 15, P.gold, T.CENTER, "title") end
		T.text(stage, "Name_" .. def.id, def.nome, x, namesY + (i == 1 and 10 or 0), nameW, narrow and 28 or 36, narrow and 18 or 29, WHITE, T.CENTER, "title", 3)
		T.text(stage, "Rarity_" .. def.id, r.nome, x, namesY + (narrow and 29 or 40) + (i == 1 and 10 or 0), nameW, narrow and 24 or 40, narrow and 17 or 30, r.cor, T.CENTER, "display", 3)
	end
	local summonY = narrow and sh - 206 or sh - 156
	local costText = not unlocked and ("Desbloqueio: " .. T.format(a.custo) .. " moedas") or (d.giroGratis and "1 GIRO GRÁTIS · x10 desconta esse giro" or (T.format(g.custo) .. " MOEDAS POR INVOCAÇÃO"))
	text(stage, "CostRule", costText, 14, summonY - 30, sw - 28, 25, narrow and 14 or 19, P.gold, T.CENTER, "title")
	local bw = narrow and (sw - 40) / 2 or (sw - 368) / 2
	local firstX = narrow and 14 or 172
	if ctx.summonBusy then
		local progressW = bw * 2 + 12
		local progress = text(stage, "Progress", "Invocando...", firstX, summonY, progressW, 30, 24, WHITE, T.CENTER, "title")
		local bar = T.progress(stage, "ProgressBar", firstX, summonY + 42, progressW, 14, 0, P.success)
		ctx.onSummonProgress = function(i, n)
			if progress.Parent then progress.Text = "Invocando " .. i .. " / " .. n; T.setProgress(bar, i / math.max(1, n), P.success, .12) end
		end
	else
		ctx.onSummonProgress = nil
		if unlocked then
			for i, n in ipairs({ 1, 10 }) do
				local cost = g.custo * (d.giroGratis and math.max(0, n - 1) or n)
				local afford = (d.moeda or 0) >= cost
				action(ctx, stage, "Summon" .. n, (n == 1 and "INVOCAR x1" or "INVOCAR x10") .. (cost == 0 and " · GRÁTIS" or ""), firstX + (i - 1) * (bw + 12), summonY, bw, 60, function() ctx.startSummon(n) end,
					near and afford and #all > 0, not near and "Viaje até o banner para invocar." or "Moedas insuficientes.", P.success, "StartSummon", { size = narrow and 20 or 27 })
				if cost > 0 then text(stage, "Cost_" .. n, T.format(cost) .. " moedas", firstX + (i - 1) * (bw + 12), summonY + 61, bw, 19, 12, P.gold, T.CENTER, "heavy") end
			end
		else
			areaUnlock(ctx, stage, a, firstX, summonY, bw, 60)
			action(ctx, stage, "ViewAreas", "VER ILHAS", firstX + bw + 12, summonY, bw, 60, function() ctx.open("Areas") end, true, nil, P.info)
		end
	end
	local secondaryY = narrow and sh - 122 or summonY + 4
	local sideW = narrow and (sw - 52) / 3 or 146
	T.button(stage, "Rates", "CHANCES", 14, secondaryY, sideW, 52, P.violet, function() M.rates(ctx) end, { size = 17 })
	T.button(stage, "Units", "UNIDADES", narrow and sideW + 26 or 14, narrow and secondaryY or summonY - 68, sideW, 52, P.info, showUnits, { size = 16 })
	local travelX = narrow and 14 + (sideW + 12) * 2 or sw - sideW - 14
	action(ctx, stage, "GoBanner", near and "NO BANNER" or "VIAJAR", travelX, secondaryY, sideW, 52, function() ctx.travel("gacha", id, true) end,
		unlocked and not near and not ctx.summonBusy, not unlocked and "Desbloqueie esta ilha primeiro." or nil, P.info)
	local pity = d.pity or { l = 0, m = 0 }
	local pityY, gap = narrow and sh - 62 or sh - 61, narrow and 5 or 12
	local pityW = narrow and sw - 28 or (sw - 40) / 2
	for i, r in ipairs({ { "Mítico+", pity.m or 0, Config.PITY_MITICO, "mitico" }, { "Lendário+", pity.l or 0, Config.PITY_LENDARIO, "lendario" } }) do
		local px, py = narrow and 14 or 14 + (i - 1) * (pityW + gap), pityY + (narrow and (i - 1) * 29 or 0)
		local bar = T.progress(stage, "Pity_" .. i, px, py, pityW, 24, math.min(r[2] / r[3], 1), T.rar(r[4]).cor)
		text(stage, "PityLabel_" .. i, r[1], px + 8, py, pityW * .54, 24, 14, WHITE, T.LEFT, "title")
		text(stage, "PityCount_" .. i, tostring(r[2]) .. " / " .. r[3], px + pityW * .53, py, pityW * .47 - 9, 24, 14, WHITE, T.RIGHT, "title")
	end
	if not narrow then text(stage, "GuaranteeNote", "Garantia ao completar a barra · Chances com sua sorte atual", 14, sh - 31, sw - 28, 23, 15, WHITE, T.CENTER, "heavy") end
end
function M.forge(ctx, p, w, h)
	local d = ctx.data
	local entries, base = {}, 0
	for id, q in pairs(d.mochila or {}) do
		local info = Config.infoMinerio(id)
		if info and q > 0 then
			table.insert(entries, { info = info, quantity = q, value = info.valor * q })
			base += info.valor * q
		end
	end
	table.sort(entries, function(a, b) return a.value > b.value end)
	local mult = d.multMoedas or 1
	local total = math.floor(base * mult)
	local narrow = w < 620
	local summaryH = narrow and 200 or 160
	local summary = artSurface(p, "SaleSummary", 0, 0, w, summaryH, P.accent, nil)
	T.slant(summary, "ForgePlate", 6, 10, 72, 68, P.accent, { alpha = .81, tilt = 20 })
	T.icon(summary, "forge", 14, 18, 52, 52)
	label(summary, "Title", "Venda de minérios", 82, 14, narrow and w - 98 or w - 350, 28, 22)
	text(summary, "Vendor", "Ignis · mestre ferreiro", 82, 47, narrow and w - 98 or w - 350, 20, 14, P.text2)
	local valueX = w - 246
	currency(summary, "Total", total, narrow and 16 or valueX, narrow and 88 or 14, narrow and w - 210 or 232, 36, 26)
	text(summary, "Bonus", mult > 1 and string.format("Bônus: x%.2f", mult) or "Valor de venda", narrow and 16 or valueX, narrow and 122 or 54, narrow and w - 210 or 232, 20, 13, P.text2)
	local frac = (d.carregado or 0) / math.max(1, d.capacidade or 1)
	text(summary, "Capacity", "Mochila " .. T.format(d.carregado or 0) .. " / " .. T.format(d.capacidade or 0), 16, narrow and 154 or 88, narrow and w - 32 or w - 300, 22, 14, P.text2)
	T.progress(summary, "CapacityBar", 16, narrow and 181 or 122, narrow and w - 32 or w - 300, 10, frac, frac >= 1 and P.warning or P.accent)
	action(ctx, summary, "SellAll", #entries > 0 and "Vender tudo" or "Mochila vazia", narrow and w - 184 or valueX, 88, narrow and 168 or 232, 52, function()
		local res = ctx.invoke("Vender")
		if res and res.ok then ctx.refresh() end
	end, #entries > 0, "Quebre minérios para encher a mochila.", P.accent, "SellOres")
	local hint = d.passes and d.passes.AutoSell and "✓ Auto Sell ativo: a venda acontece quando sua mochila enche."
		or "Vendas são feitas com Ignis. Fora do lobby, viaje gratuitamente até a praça central."
	T.para(p, "AccessHint", hint, 0, summaryH + 12, narrow and w or w - 204, narrow and 42 or 52, 14, P.text2, T.LEFT)
	local quickY = summaryH + (narrow and 64 or 12)
	action(ctx, p, "GoLobby", narrow and "Ir ao lobby" or "Ir à praça central", narrow and 0 or w - 192, quickY, narrow and (w - 12) / 2 or 192, 52, function() ctx.travel("area", 0) end, true, nil, P.neutral)
	if narrow then
		T.button(p, "Equipment", "Equipamentos", (w + 12) / 2, quickY, (w - 12) / 2, 52, P.neutral, function() ctx.storeTab = "Picaretas"; ctx.open("Store") end, { size = 15 })
	end
	local listY = quickY + 64
	local scroll = T.scroll(p, "Ores", 0, listY, w, math.max(90, h - listY - (narrow and 0 or 64)), P.accent)
	local cw = w - 14
	if #entries == 0 then
		T.emptyState(scroll, "Empty", "Sua mochila está vazia", "Quebre minérios em uma ilha para receber moedas na venda.", 0, 0, cw, math.max(190, h - listY - 64), "Ver ilhas", function() ctx.open("Areas") end)
	end
	for i, e in ipairs(entries) do
		local rowH = narrow and 90 or 56
		local row = panel(scroll, "Ore_" .. i, 0, (i - 1) * (rowH + 10), cw, rowH)
		T.oreIcon(row, e.info.variante, 8, 8, 40, 40)
		label(row, "Name", e.info.nome, 60, 6, narrow and cw - 76 or cw - 300, 25, 17)
		text(row, "UnitValue", T.format(e.info.valor) .. " moedas por minério", 60, 31, narrow and cw - 76 or cw - 300, 18, 12, P.text3)
		text(row, "Quantity", "×" .. T.format(e.quantity), narrow and 60 or cw - 236, narrow and 53 or 0, 84, narrow and 26 or 56, 16, P.text2, narrow and T.LEFT or T.RIGHT)
		text(row, "Value", T.format(e.value), cw - 138, narrow and 53 or 0, 122, narrow and 26 or 56, 19, P.gold, T.RIGHT, "title")
	end
	scroll.CanvasSize = UDim2.fromOffset(0, math.max(210, #entries * (narrow and 100 or 66)))
	if not narrow then
		T.button(p, "Equipment", "Melhorar equipamento", 0, h - 52, 236, 52, P.neutral, function() ctx.storeTab = "Picaretas"; ctx.open("Store") end, { size = 15 })
		text(p, "BaseNote", "Lista: valor base. Total: inclui seus bônus.", 252, h - 52, w - 252, 52, 13, P.text3)
	end
end

local QUEST_ICON = { minerar = "pickaxe", epico = "shiny", chefe = "forge", invocar = "summon", vender = "coins" }

function M.progress(ctx, p, w, h)
	local d = ctx.data
	local narrow = w < 620
	local selected = ctx.questArea
	if not selected or not Config.areaPorId(selected) then
		selected = Players.LocalPlayer:GetAttribute("CurrentAreaId")
		if not selected or not Config.areaPorId(selected) then selected = 1 end
		for _, a in ipairs(Config.Areas) do
			if hasArea(ctx, a.id) then
				for _, quest in ipairs(Config.Missoes[a.id] or {}) do
					local state = d.missoes and d.missoes[quest.id]
					if state and state.p >= quest.meta and not state.r then selected = a.id; break end
				end
			end
		end
	end
	ctx.questArea = selected
	local list, ready = {}, {}
	for i, quest in ipairs(Config.Missoes[selected] or {}) do
		local state = d.missoes and d.missoes[quest.id] or { p = 0, r = false }
		local rank = state.r and 3 or (state.p >= quest.meta and 1 or 2)
		table.insert(list, { def = quest, state = state, rank = rank, index = i })
		if rank == 1 then table.insert(ready, quest) end
	end
	table.sort(list, function(a, b) if a.rank ~= b.rank then return a.rank < b.rank end return a.index < b.index end)
	T.dropdown(p, "QuestArea", 0, 0, narrow and w or math.min(340, w - 240), 52, areaOptions(ctx), selected, function(id) ctx.questArea = id; ctx.refresh() end)
	local unlocked = hasArea(ctx, selected)
	action(ctx, p, "ClaimAll", #ready > 0 and ("Resgatar " .. #ready .. " missões") or "Nenhuma pronta", narrow and 0 or w - 220, narrow and 64 or 0, narrow and w or 220, 52, function()
		local received = 0
		ctx.batchQuestAudio = true
		local batchOK, batchError = pcall(function()
			for _, quest in ipairs(ready) do
				local res = ctx.invoke("ResgatarMissao", quest.id)
				if res and res.ok then received += quest.premio end
			end
		end)
		ctx.batchQuestAudio = false
		if not batchOK then error(batchError) end
		if received > 0 then T.som("quest_complete"); ctx.coinBurst(received) end
		ctx.refresh()
	end, unlocked and #ready > 0, "Complete os objetivos para liberar as recompensas.", P.accent, "ClaimQuests")
	if not narrow then text(p, "Hint", "Complete objetivos nesta ilha e resgate as moedas de cada missão.", 0, 62, w, 24, 14, P.text2) end
	local listY = narrow and 130 or 98
	local scroll = T.scroll(p, "Quests", 0, listY, w, math.max(90, h - listY), P.accent)
	local cw = w - 14
	if not unlocked then
		local a = Config.areaPorId(selected)
		local box = panel(scroll, "Locked", 0, 0, cw, narrow and 278 or 230)
		T.lock(box, 18, 22, 44, P.text3)
		label(box, "Title", "Missões bloqueadas", 80, 20, cw - 100, 30, 23)
		T.para(box, "Requirement", "Desbloqueie " .. a.nome .. " para liberar estes objetivos.", narrow and 16 or 80, narrow and 76 or 58, narrow and cw - 32 or cw - 100, narrow and 44 or 26, 15, P.text2, T.LEFT)
		currency(box, "Cost", a.custo, narrow and 16 or 80, narrow and 132 or 100, narrow and cw - 32 or cw - 100, 30, 23)
		areaUnlock(ctx, box, a, narrow and 16 or 80, narrow and 178 or 152, narrow and (cw - 44) / 2 or 220, 52)
		T.button(box, "Areas", "Ver ilhas", narrow and (cw + 12) / 2 or 312, narrow and 178 or 152, narrow and (cw - 44) / 2 or 180, 52, P.neutral, function() ctx.open("Areas") end, { size = 16 })
		scroll.CanvasSize = UDim2.fromOffset(0, narrow and 288 or 240)
		return
	end
	for i, item in ipairs(list) do
		local quest, state = item.def, item.state
		local claimed, claimable = item.rank == 3, item.rank == 1
		local rowH = narrow and 172 or 116
		local row = panel(scroll, "Quest_" .. quest.id, 0, (i - 1) * (rowH + 12), cw, rowH, claimable)
		T.icon(row, QUEST_ICON[quest.tipo] or "quests", 12, 22, 42, 42)
		local contentW = narrow and cw - 84 or cw - 256
		local title = T.para(row, "Title", quest.texto, 68, 12, contentW, 42, 17, claimed and P.text3 or P.text, T.LEFT, "title")
		title.TextYAlignment = Enum.TextYAlignment.Top
		T.progress(row, "Progress", 68, 62, contentW, 12, (state.p or 0) / math.max(1, quest.meta), claimed and P.text3 or P.accent)
		text(row, "Count", T.format(math.min(state.p or 0, quest.meta)) .. " / " .. T.format(quest.meta), 68, 80, contentW, 18, 13, P.text2)
		local rx = cw - 166
		currency(row, "Reward", quest.premio, narrow and 16 or rx, narrow and 126 or 10, narrow and cw - 198 or 150, 28, 19)
		if claimed then T.chip(row, "Claimed", "✓ RESGATADA", rx, narrow and 124 or 60, 34, P.text3, { size = 12, w = 150 })
		else
			action(ctx, row, "Claim_" .. quest.id, claimable and "Resgatar" or "Em andamento", rx, narrow and 110 or 52, 150, 52, function()
				local res = ctx.invoke("ResgatarMissao", quest.id)
				if res and res.ok then ctx.coinBurst(quest.premio); ctx.refresh() end
			end, claimable, "Complete o objetivo antes de resgatar.", claimable and P.accent or P.neutral, "ClaimQuests")
		end
	end
	if #list == 0 then T.emptyState(scroll, "Empty", "Nenhuma missão", "Não há objetivos disponíveis para esta ilha.", 0, 0, cw, 200) end
	scroll.CanvasSize = UDim2.fromOffset(0, math.max(200, #list * (narrow and 184 or 128)))
end

function M.settings(ctx, p, w, h)
	local scroll = T.scroll(p, "SettingsContent", 0, 0, w, h, P.accent)
	local cw = w - 14
	local twoColumns = cw >= 900
	local colW = twoColumns and (cw - 24) / 2 or cw
	local player = Players.LocalPlayer
	local y = T.section(scroll, "Mixagem de áudio", 0, 0, colW, P.accent)
	local volumeDefs = {
		{ "AudioMasterVolume", "Volume geral", "Controla toda a mixagem" },
		{ "AudioMusicVolume", "Música", "Trilhas do lobby e das ilhas" },
		{ "AudioSFXVolume", "Efeitos do jogo", "Mineração, recompensas e mundo" },
		{ "AudioUIVolume", "Interface", "Cliques, menus e confirmações" },
		{ "AudioAmbienceVolume", "Ambiente", "Vento, portais e forja" },
	}
	for _, def in ipairs(volumeDefs) do
		local key = def[1]
		local row = panel(scroll, "Setting_" .. key, 0, y, colW, 120)
		label(row, "Name", def[2], 16, 10, colW - 112, 24, 17)
		text(row, "Description", def[3], 16, 35, colW - 32, 21, 13, P.text2)
		local valueLabel = text(row, "Percentage", "", colW - 88, 10, 72, 24, 17, P.accent, T.RIGHT, "number")
		local bar = T.progress(row, "Level", 84, 85, colW - 168, 8, 0, P.accent)
		local function current()
			local value = AudioPreferences.value(key, player:GetAttribute(key))
			return value == nil and AudioPreferences.defaults[key] or value
		end
		local minus = T.button(row, "Decrease", "−", 16, 59, 52, 52, P.neutral, function()
			ctx.setAudioPreference(key, current() - .05)
		end, { size = 24 })
		local plus = T.button(row, "Increase", "+", colW - 68, 59, 52, 52, P.neutral, function()
			ctx.setAudioPreference(key, current() + .05)
		end, { size = 24 })
		T.hint(minus, "Diminuir " .. string.lower(def[2]) .. " em 5%", "above")
		T.hint(plus, "Aumentar " .. string.lower(def[2]) .. " em 5%", "above")
		local function update()
			local value = current()
			valueLabel.Text = tostring(math.round(value * 100)) .. "%"
			T.setProgress(bar, value, P.accent, .12)
			T.setEnabled(minus, value > 0)
			T.setEnabled(plus, value < 1)
		end
		local changed = player:GetAttributeChangedSignal(key):Connect(update)
		row.Destroying:Connect(function() changed:Disconnect() end)
		update()
		y += 130
	end
	T.button(scroll, "ResetAudio", "Restaurar áudio padrão", 0, y, colW, 52, P.neutral, function()
		for key, value in pairs(AudioPreferences.defaults) do ctx.setAudioPreference(key, value) end
		ctx.refresh()
	end, { size = 16, sound = "ui_confirm" })
	y += 58
	local status = T.para(scroll, "AudioSaveState", "", 0, y, colW, 48, 13, P.text3, T.LEFT)
	ctx.audioSettingsStatus = function()
		if not status.Parent then return end
		local state = ctx.audioSaveStatus
		status.Text = state == "pending" and "Áudio aplicado. Atualizando suas preferências..."
			or state == "profile" and "Áudio será salvo automaticamente com seu progresso."
			or state == "session" and "Áudio aplicado nesta sessão. O perfil atual não tem salvamento disponível."
			or state == "error" and "Áudio aplicado localmente. Não foi possível atualizar o perfil; ajuste novamente para tentar."
			or "Carregando as preferências de áudio do seu perfil..."
	end
	ctx.audioSettingsStatus()
	y += 60
	y += T.section(scroll, "Ativar ou silenciar", 0, y, colW, P.accent)
	local defs = {
		{ "MusicEnabled", "Música das ilhas", "Liga ou desliga a trilha sonora", true },
		{ "SomMineracaoEnabled", "Sons de mineração", "Golpes, quebras e coleta", true },
		{ "SomInterfaceEnabled", "Sons da interface", "Cliques, abas e confirmação", true },
		{ "LobbyVFXEnabled", "Efeitos do ambiente", "Partículas e efeitos do cenário", true },
		{ "ExpeditionEffectsEnabled", "Efeitos da interface", "Partículas e celebrações da UI", true },
		{ "ExpeditionBlurEnabled", "Desfoque de fundo", "Desfoca o cenário ao abrir menus", true },
		{ "ReducedMotion", "Movimento reduzido", "Reduz escalas, tremores e transições", false },
	}
	for i, def in ipairs(defs) do
		if i == 4 then y += T.section(scroll, "Efeitos visuais", 0, y, colW, P.accent) end
		local row = panel(scroll, "Setting_" .. def[1], 0, y, colW, 74)
		label(row, "Name", def[2], 16, 12, colW - 118, 24, 17)
		text(row, "Description", def[3], 16, 40, colW - 118, 20, 14, P.text2)
		local value = player:GetAttribute(def[1])
		local on = value == true or (value == nil and def[4])
		T.toggle(row, "Toggle", colW - 84, 19, on, function(state)
			if AudioPreferences.defaults[def[1]] ~= nil then ctx.setAudioPreference(def[1], state)
			else player:SetAttribute(def[1], state) end
		end)
		y += 84
	end
	local rx, ry = twoColumns and colW + 24 or 0, twoColumns and 0 or y + 16
	local cy = ry + T.section(scroll, "Códigos", rx, ry, colW, P.accent)
	local code = panel(scroll, "CodeCard", rx, cy, colW, 230)
	label(code, "Title", "Resgatar código", 16, 14, colW - 32, 28, 21)
	text(code, "Hint", "Use um código divulgado nas redes do jogo.", 16, 47, colW - 32, 22, 14, P.text2)
	local input = T.input(code, "CodeBox", 16, 84, colW - 32, 52, "Digite o código", ctx.codeDraft or "", { size = 17 })
	local redeem
	local function claim()
		local value = input.Text:match("^%s*(.-)%s*$") or ""
		if value == "" then return end
		local res = ctx.invoke("ResgatarCodigo", value)
		if res and res.ok then
			ctx.codeDraft = ""
			if input.Parent then input.Text = "" end
			ctx.refresh()
		end
	end
	redeem = action(ctx, code, "RedeemCode", "Resgatar", 16, 146, colW - 32, 52, claim,
		function() return input.Parent ~= nil and input.Text:match("%S") ~= nil end, "Digite um código para continuar.", P.accent, "RedeemCode")
	input:GetPropertyChangedSignal("Text"):Connect(function()
		ctx.codeDraft = input.Text
		T.setEnabled(redeem, input.Text:match("%S") ~= nil and not ctx.menuPending.RedeemCode)
	end)
	text(code, "CodeState", "Aguarde a confirmação para tentar novamente.", 16, 207, colW - 32, 18, 12, P.text3)
	local keyY = cy + 248
	keyY += T.section(scroll, "Atalhos", rx, keyY, colW, P.accent)
	local keys = { { "H", "Unidades" }, { "J", "Itens" }, { "G", "Invocar" }, { "T", "Mineração contínua" }, { "Esc", "Fechar janela" } }
	for i, entry in ipairs(keys) do
		local yy = keyY + (i - 1) * 42
		local key = panel(scroll, "Key_" .. entry[1], rx, yy, 48, 32)
		text(key, "Letter", entry[1], 0, 0, 48, 32, 14, P.text, T.CENTER, "title")
		text(scroll, "Shortcut_" .. i, entry[2], rx + 62, yy, colW - 62, 32, 15, P.text2)
	end
	local endY = math.max(y, keyY + #keys * 42)
	T.para(scroll, "SavedHint", "Efeitos visuais e movimento são aplicados durante a sessão.", 0, endY + 10, cw, 44, 13, P.text3, T.LEFT)
	scroll.CanvasSize = UDim2.fromOffset(0, endY + 64)
end

local DAILY_ICON = { moedas = "coins", boost = "potion", pet = "units", hats = "items" }

local function daily(ctx, p, w, h)
	local d = ctx.data
	local info = d.daily or { dia = 1, disponivel = false }
	local day = math.clamp(info.dia or 1, 1, math.max(1, #Config.DAILY))
	local narrow = w < 700
	local black, orange = Color3.fromRGB(5, 5, 8), Color3.fromRGB(255, 126, 0)
	local board = T.frame(p, "DailySummary", 0, 0, w, h, black, 0)
	T.corner(board, 10)
	T.new("UIStroke", { Color = orange, Thickness = 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, board)
	local function claim()
		local res = ctx.invoke("ResgatarDaily")
		if res and res.ok then
			if ctx.Notify then ctx.Notify.banner({ title = "Dia " .. day .. " resgatado", subtitle = Config.DAILY[day].texto, color = P.gold, sound = false }) end
			ctx.refresh()
		end
	end
	local headerH = narrow and 151 or 88
	local titleW = narrow and w - 24 or w - 384
	local titleBand = T.frame(board, "DailyTitleBand", 12, 10, titleW, 49, orange, 0)
	T.corner(titleBand, 10)
	T.text(titleBand, "Title", "RECOMPENSAS DIÁRIAS", 10, 0, titleW - 20, 49, narrow and 25 or 32, WHITE, T.CENTER, "title", 3)
	local reset = "Libera em " .. T.clock(86400 - (os.time() % 86400))
	text(board, "State", info.disponivel and ("DIA " .. day .. " DISPONÍVEL!") or reset,
		narrow and 14 or w - 200, narrow and 66 or 10, narrow and w - 28 or 186, narrow and 25 or 49, narrow and 16 or 18, info.disponivel and P.success or P.danger, T.CENTER, "title")
	action(ctx, board, "DailyClaim", "RESGATAR", narrow and 12 or w - 366, narrow and 96 or 10, narrow and w - 24 or 154, 52, claim,
		info.disponivel == true, "Esta recompensa estará disponível no próximo dia.", orange, "DailyClaim", { size = 24 })
	if not narrow then text(board, "Rule", "Seu ciclo avança ao resgatar. Faltar um dia não remove recompensas.", 14, 64, w - 28, 21, 13, P.text2, T.LEFT, "heavy") end
	local scroll = T.scroll(board, "DailyRewards", 12, headerH + 10, w - 24, math.max(90, h - headerH - 22), orange)
	scroll.ClipsDescendants = true
	local cw = w - 38
	local cols = cw >= 900 and 4 or (cw >= 620 and 3 or 2)
	local cardW = (cw - (cols - 1) * GAP) / cols
	local cardH = narrow and 294 or 280
	for i, def in ipairs(Config.DAILY) do
		local today, claimed = i == day, i < day
		local available = today and info.disponivel == true
		local rewardColor, rank = P.gold, 0
		for _, item in ipairs(def.itens or {}) do
			if item.raridade then
				local rarity = T.rar(item.raridade)
				if rarity.ordem > rank then rewardColor, rank = rarity.cor, rarity.ordem end
			elseif item.tipo == "boost" and rank == 0 then rewardColor = P.violet end
		end
		local x, y = ((i - 1) % cols) * (cardW + GAP), 14 + math.floor((i - 1) / cols) * (cardH + 20)
		local card = T.frame(scroll, "Day_" .. i, x, y, cardW, cardH, black, 0)
		T.corner(card, 10)
		T.new("UIStroke", { Color = available and orange or (i == #Config.DAILY and rewardColor or Color3.fromRGB(94, 94, 101)), Thickness = available and 3 or 2, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, card)
		local glow = T.frame(card, "RewardGlow", 1, 1, cardW - 2, cardH - 52, rewardColor, 0)
		T.corner(glow, 9)
		T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, .97), T.kp(.58, .9), T.kp(1, claimed and .95 or .69) }) }, glow)
		local dayBack = T.frame(card, "DayBack", cardW / 2 - 48, -10, 96, 32, black, 0)
		T.text(dayBack, "Day", "DIA " .. i, 0, 0, 96, 32, 25, orange, T.CENTER, "title", 3)
		T.para(card, "Reward", def.texto, 12, 29, cardW - 24, 53, narrow and 14 or 16, claimed and P.text3 or WHITE, T.LEFT, "title")
		local kind = def.itens and def.itens[1] and def.itens[1].tipo or "moedas"
		local artS = math.min(cardW - 22, narrow and 146 or 156)
		local artY = (cardH - 52 - artS) / 2 + 24
		-- Clip only the reward artwork; the floating day label and claim strip keep their layout.
		local artClip = T.frame(card, "RewardArtClip", 0, 0, cardW, cardH - 52, nil, 1)
		artClip.ClipsDescendants = true
		T.image(artClip, "RewardBurst", T.Assets.rays, cardW / 2 - artS * .63, artY - artS * .13, artS * 1.26, artS * 1.26, rewardColor, claimed and .95 or .85)
		local rewardArt = T.icon(artClip, DAILY_ICON[kind] or "gift", cardW / 2 - artS / 2, artY, artS, artS)
		if claimed or not available then rewardArt.ImageTransparency = claimed and .5 or .26 end
		for itemIndex = 2, math.min(3, #(def.itens or {})) do
			local item = def.itens[itemIndex]
			local icon = T.icon(artClip, DAILY_ICON[item.tipo] or "gift", cardW / 2 + (itemIndex == 2 and artS * .15 or -artS * .48), artY + artS * .61, artS * .43, artS * .43)
			if claimed or not available then icon.ImageTransparency = claimed and .5 or .26 end
		end
		if available then
			action(ctx, card, "ClaimDay_" .. i, "RESGATAR", 0, cardH - 52, cardW, 52, claim, true, nil, orange, "DailyClaim", { size = 27 })
		else
			local base = T.frame(card, "ClaimedStrip", 1, cardH - 52, cardW - 2, 51, claimed and WHITE or Color3.fromRGB(61, 61, 65), 0)
			T.corner(base, 8)
			T.text(base, "Status", claimed and "RESGATADO" or (today and "AGUARDE" or "BLOQUEADO"), 6, 0, cardW - 14, 51, narrow and 22 or 27, claimed and P.success or Color3.fromRGB(185, 185, 190), T.CENTER, "title", 3)
			if not claimed then T.lock(artClip, cardW / 2 - 25, artY + artS * .38, 50, WHITE) end
		end
	end
	local endY = 14 + math.ceil(#Config.DAILY / cols) * (cardH + 20)
	if narrow then
		T.para(scroll, "CycleRule", "O ciclo avança quando você resgata. Faltar um dia não remove suas recompensas.", 0, endY + 4, cw, 42, 14, P.text2, T.LEFT)
		endY += 58
	end
	scroll.CanvasSize = UDim2.fromOffset(0, endY)
end
local function index(ctx, p, w, h)
	local d = ctx.data
	local idx = d.index or {}
	local foundPets, foundHats = idx.pets or {}, idx.hats or {}
	local petCount, hatCount = 0, 0
	for _, def in ipairs(Config.Pets) do if foundPets[def.id] then petCount += 1 end end
	for _, def in ipairs(Config.Hats) do if foundHats[def.id] then hatCount += 1 end end
	local header = panel(p, "CollectionProgress", 0, 0, w, 84)
	local half = (w - 48) / 2
	label(header, "Pets", "Unidades " .. petCount .. " / " .. #Config.Pets, 16, 12, half, 25, 18)
	T.progress(header, "PetBar", 16, 52, half, 12, petCount / math.max(1, #Config.Pets), P.accent)
	label(header, "Hats", "Hats " .. hatCount .. " / " .. #Config.Hats, half + 32, 12, half, 25, 18)
	T.progress(header, "HatBar", half + 32, 52, half, 12, hatCount / math.max(1, #Config.Hats), P.accent)
	ctx.indexKind = ctx.indexKind or "Pets"
	local narrow = w < 620
	T.tabs(p, "CollectionKind", 0, 98, narrow and w or 284, 52, { { id = "Pets", label = "Unidades" }, { id = "Hats", label = "Hats" } }, ctx.indexKind, P.accent,
		function(kind) ctx.indexKind = kind; ctx.indexPage = 1; ctx.refresh() end)
	local search = T.input(p, "CollectionSearch", narrow and 0 or 300, narrow and 162 or 98, narrow and w or w - 300, 52, "Buscar na coleção", ctx.indexSearch or "", { size = 15 })
	local listY = narrow and 226 or 164
	local scroll = T.scroll(p, "Collection", 0, listY, w, math.max(90, h - listY - 64), P.accent)
	local cw = w - 14
	local draw, previous, following
	local pageText = text(p, "Page", "", 114, h - 52, w - 228, 52, 14, P.text2, T.CENTER)
	previous = T.button(p, "PreviousPage", "Anterior", 0, h - 52, 104, 52, P.neutral, function()
		ctx.indexPage = math.max(1, (ctx.indexPage or 1) - 1); scroll.CanvasPosition = Vector2.zero; draw()
	end, { size = 15 })
	following = T.button(p, "NextPage", "Próxima", w - 104, h - 52, 104, 52, P.neutral, function()
		ctx.indexPage = (ctx.indexPage or 1) + 1; scroll.CanvasPosition = Vector2.zero; draw()
	end, { size = 15 })
	draw = function()
		T.clear(scroll)
		local pets = ctx.indexKind == "Pets"
		local defs, found = pets and Config.Pets or Config.Hats, pets and foundPets or foundHats
		local query = string.lower(ctx.indexSearch or "")
		local cols = math.max(2, math.floor((cw + 12) / 154))
		local cardW = (cw - (cols - 1) * 12) / cols
		local y, matches, areaStats = 0, {}, {}
		for _, area in ipairs(Config.Areas) do areaStats[area.id] = { found = 0, total = 0 } end
		for _, def in ipairs(defs) do
			local areaId = pets and def.area or def.mundo
			local stats = areaStats[areaId]
			if stats then
				stats.total += 1
				if found[def.id] then stats.found += 1 end
				if query == "" or string.find(string.lower(def.nome or ""), query, 1, true) then table.insert(matches, def) end
			end
		end
		table.sort(matches, function(a, b)
			local aa, bb = pets and a.area or a.mundo, pets and b.area or b.mundo
			if aa ~= bb then return aa < bb end
			local ar, br = T.rar(a.raridade).ordem, T.rar(b.raridade).ordem
			if ar ~= br then return ar < br end
			return tostring(a.id) < tostring(b.id)
		end)
		local pageSize = 18
		local pages = math.max(1, math.ceil(#matches / pageSize))
		ctx.indexPage = math.clamp(ctx.indexPage or 1, 1, pages)
		local from = (ctx.indexPage - 1) * pageSize + 1
		local through = math.min(#matches, from + pageSize - 1)
		T.setEnabled(previous, ctx.indexPage > 1)
		T.setEnabled(following, ctx.indexPage < pages)
		pageText.Text = ctx.indexPage .. " / " .. pages .. " · " .. #matches .. " itens"
		for _, area in ipairs(Config.Areas) do
			local areaDefs = {}
			for i = from, through do
				local def = matches[i]
				if (pets and def.area or def.mundo) == area.id then table.insert(areaDefs, def) end
			end
			if #areaDefs > 0 then
				local stats = areaStats[area.id]
				y += T.section(scroll, area.nome, 0, y, cw, P.accent, nil, stats.found .. " / " .. stats.total .. " descobertos")
				for i, def in ipairs(areaDefs) do
					local known = found[def.id]
					local r = T.rar(def.raridade)
					local card = T.tile(scroll, "Entry_" .. def.id, ((i - 1) % cols) * (cardW + 12), y + math.floor((i - 1) / cols) * 180, cardW, 168, def.raridade, { animated = false, dim = not known })
					if known then T.preview(card, pets and "pet" or "hat", def.id, 8, 8, cardW - 16, 98, false)
					else T.lock(card, cardW / 2 - 22, 34, 44, P.text3) end
					label(card, "Name", known and def.nome or "Não descoberto", 10, 111, cardW - 20, 23, 15, known and P.text or P.text3)
					text(card, "Rarity", "◆ " .. r.nome, 10, 139, cardW - 20, 19, 12, known and r.cor or P.text3)
				end
				y += math.ceil(#areaDefs / cols) * 180 + 12
			end
		end
		if #matches == 0 then T.emptyState(scroll, "Empty", "Nenhum resultado", "Tente outro nome ou limpe a busca.", 0, 0, cw, 210, "Limpar busca", function() search.Text = "" end) end
		scroll.CanvasSize = UDim2.fromOffset(0, math.max(210, y))
	end
	search:GetPropertyChangedSignal("Text"):Connect(function() ctx.indexSearch = search.Text; ctx.indexPage = 1; scroll.CanvasPosition = Vector2.zero; draw() end)
	draw()
end

function M.daily(ctx, p, w, h)
	if ctx.eventsTab == "Index" then index(ctx, p, w, h) else daily(ctx, p, w, h) end
end

function M.render(ctx, p, w, h)
	if not ctx.data then T.emptyState(p, "Loading", "Carregando seus dados", "Aguarde para acessar seus itens e progresso.", 0, 0, w, h); return end
	-- Short landscape viewports keep a readable page, reachable through one outer scroll.
	-- Summon has its own compact scroll and fixed purchase/travel actions.
	if h < 380 and ctx.page ~= "Summon" then
		local outer = T.scroll(p, "CompactPage_" .. tostring(ctx.page), 0, 0, w, h, P.accent)
		w, h = w - 14, 620
		p = T.frame(outer, "Content", 0, 0, w, h, nil, 1)
		outer.CanvasSize = UDim2.fromOffset(0, h)
	end
	if ctx.page == "Store" then M.store(ctx, p, w, h)
	elseif ctx.page == "Areas" or ctx.page == "Play" then M.areas(ctx, p, w, h)
	elseif ctx.page == "Summon" then M.summon(ctx, p, w, h)
	elseif ctx.page == "Forge" then M.forge(ctx, p, w, h)
	elseif ctx.page == "Settings" then M.settings(ctx, p, w, h)
	elseif ctx.page == "Events" then M.daily(ctx, p, w, h)
	else M.progress(ctx, p, w, h) end
end

return M


