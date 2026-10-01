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
	end, { size = visual and visual.size or 16, icon = visual and visual.icon, onDisabled = reason and function() ctx.toast(reason, nil, "info") end or nil })
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
	if ctx.page == "Store" then passesStore(ctx, p, w, h) else equipmentStore(ctx, p, w, h) end
end

function M.areas(ctx, p, w, h)
	local d = ctx.data
	local scroll = T.scroll(p, "Destinations", 0, 0, w, h, P.accent)
	local cw = w - 14
	local quick = { { "Lobby", w < 620 and "Lobby" or "Praça central", function() ctx.travel("area", 0) end },
		{ "Forge", w < 620 and "Vender" or "Vender com Ignis", function() ctx.open("Forge") end },
		{ "Equipment", w < 620 and "Ignis" or "Equipamentos · Ignis", function() ctx.travel("shop") end } }
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
	local narrow = w < 620
	local stageH = narrow and 520 or math.max(300, h)
	local pageH = narrow and 1116 or stageH
	if pageH > h then
		local outer = T.scroll(p, "SummonPage", 0, 0, w, h, P.violet)
		outer.ClipsDescendants = true
		w = w - 14
		p = T.frame(outer, "Content", 0, 0, w, pageH, nil, 1)
		outer.CanvasSize = UDim2.fromOffset(0, pageH)
	end
	local availableW = w - 24
	local railW = narrow and w or math.floor(availableW * .20)
	local centerW = narrow and w or math.floor(availableW * .57)
	local rightW = narrow and w or availableW - railW - centerW
	local stageX, stageY = narrow and 0 or railW + 12, narrow and 88 or 0
	local rightX, rightY = narrow and 0 or stageX + centerW + 12, narrow and stageY + stageH + 12 or 0
	local rightH = narrow and 492 or stageH
	local rail = T.scroll(p, "Banners", 0, 0, railW, narrow and 76 or stageH - 62, P.violet)
	rail.ClipsDescendants = true
	if narrow then rail.ScrollingDirection = Enum.ScrollingDirection.X end
	local thumbW = narrow and 190 or railW - 12
	local thumbH = math.max(56, math.floor(thumbW / 3.12))
	local bannerCount = 0
	for _, island in ipairs(Config.Areas) do
		if Config.Gachas[island.id] then
			local selected = island.id == id
			local tone = Config.Temas[island.tema] and Config.Temas[island.tema].cor or P.violet
			local bx, by = narrow and bannerCount * (thumbW + 10) or 0, narrow and 4 or bannerCount * (thumbH + 10) + 4
			local b = T.new("TextButton", { Name = "Banner_" .. island.id, Position = UDim2.fromOffset(bx, by), Size = UDim2.fromOffset(thumbW, thumbH),
				BackgroundColor3 = P.bg0, BorderSizePixel = 0, Text = "", AutoButtonColor = false, ClipsDescendants = true }, rail)
			T.corner(b, 5)
			T.new("UIStroke", { Color = selected and WHITE or tone, Thickness = selected and 2 or 1, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, b)
			local art = T.image(b, "Island", T.areaImage(island.id), 1, 1, thumbW - 2, thumbH - 2, WHITE, .25)
			art.ScaleType = Enum.ScaleType.Crop
			local shade = T.frame(b, "Shade", 0, 0, thumbW, thumbH, Color3.new(0, 0, 0), .42)
			T.para(b, "Name", island.nome, 9, 6, thumbW - 18, thumbH-12, (narrow or ctx.compact) and 17 or 21, selected and WHITE or tone, T.LEFT, "title")
			if thumbH >= 68 then text(b, "State", hasArea(ctx, island.id) and "Unidades desta ilha" or "Ilha bloqueada", 9, thumbH - 24, thumbW - 18, 20, 13, P.text2) end
			T.bindInteraction(b, function() ctx.bannerArea = island.id; ctx.refresh() end)
			bannerCount += 1
		end
	end
	rail.CanvasSize = narrow and UDim2.fromOffset(bannerCount * (thumbW + 10), 0) or UDim2.fromOffset(0, bannerCount * (thumbH + 10) + 4)
	local stage = T.panel(p, "BannerHero", stageX, stageY, centerW, stageH, { bg = Color3.fromRGB(12, 10, 20), radius = 6, strokeColor = P.violet, strokeWidth = 1 })
	stage.ClipsDescendants = true
	local scene = T.image(stage, "IslandScene", T.areaImage(id), 0, 0, centerW, stageH, WHITE, .5)
	scene.ScaleType = Enum.ScaleType.Crop
	T.frame(stage, "SceneShade", 0, 0, centerW, stageH, Color3.fromRGB(10, 8, 19), .42)
	local hasResults = ctx.lastSummonResults and #ctx.lastSummonResults > 0 and ctx.showLastSummon
	local titleW = centerW - (not narrow and hasResults and 154 or 24)
	T.para(stage, "BannerName", a.nome, 12, 10, titleW, 40, narrow and 25 or 29, WHITE, T.LEFT, "title")
	text(stage, "Location", unlocked and (near and "No banner · pronto para invocar" or "Viaje até o banner para invocar") or "Ilha bloqueada", 12, 52, narrow and centerW - 24 or centerW - 260, 22, 14, near and P.success or P.text2)
	currency(stage, "Wallet", d.moeda, narrow and 12 or centerW - 236, narrow and 78 or 48, narrow and centerW - 24 or 224, 28, 20)
	if hasResults and not narrow then T.button(stage, "LastResult", "Resultado", centerW - 134, 10, 122, 44, P.neutral, ctx.showLastSummon, { size = 17 }) end
	local shown, modelIds = {}, {}
	if narrow then
		if featured[1] then table.insert(shown, featured[1]); table.insert(modelIds, featured[1].id) end
	else
		for _, i in ipairs({ 2, 1, 3 }) do
			if featured[i] then table.insert(shown, featured[i]); table.insert(modelIds, featured[i].id) end
		end
	end
	local viewportH = stageH - (narrow and 274 or 184)
	if #modelIds > 0 then
		T.characterViewport(stage, modelIds, 6, narrow and 106 or 76, centerW - 12, viewportH, { fullBody = true, padding = 1.03 })
	else T.emptyState(stage, "Empty", "Nenhuma unidade", "Este banner ainda não tem unidades disponíveis.", 8, 84, centerW - 16, viewportH - 12) end
	local namesY = stageH - (narrow and 234 or 196)
	local labelW = (centerW - 24) / math.max(1, #shown)
	for i, def in ipairs(shown) do
		local rx = 12 + (i - 1) * labelW
		T.frame(stage, "NameShade_" .. i, rx, namesY, labelW, 60, Color3.new(0, 0, 0), .55)
		T.para(stage, "Name_" .. def.id, def.nome, rx + 4, namesY + 1, labelW - 8, 32, narrow and 22 or 26, WHITE, T.CENTER, "title")
		text(stage, "Rarity_" .. def.id, T.rar(def.raridade).nome, rx + 4, namesY + 34, labelW - 8, 24, 21, T.rar(def.raridade).cor, T.CENTER, "title")
	end
	local function goBanner() ctx.travel("gacha", id, true) end
	local travelParent = narrow and stage or p
	action(ctx, travelParent, "GoBanner", near and "No banner" or "Viajar ao banner", narrow and 12 or 0, narrow and stageH - 178 or stageH - 52, narrow and centerW - 24 or railW - 12, 44, goBanner,
		unlocked and not near and not ctx.summonBusy, not unlocked and "Desbloqueie esta ilha primeiro." or nil, P.info)
	local actionY = stageH - 122
	local bw = (centerW - 36) / 2
	local free = d.giroGratis == true
	if ctx.summonBusy then
		local progress = text(stage, "Progress", "Invocando...", 12, actionY, centerW - 24, 28, 22, WHITE, T.CENTER, "title")
		local bar = T.progress(stage, "ProgressBar", 12, actionY + 34, centerW - 24, 12, 0, P.success)
		ctx.onSummonProgress = function(i, n)
			if progress.Parent then progress.Text = "Invocando " .. i .. " / " .. n; T.setProgress(bar, i / math.max(1, n), P.success, .12) end
		end
	else
		ctx.onSummonProgress = nil
		if unlocked then
			for i, n in ipairs({ 1, 10 }) do
				local cost = g.custo * (free and math.max(0, n - 1) or n)
				local price = cost == 0 and "Grátis" or T.format(cost)
				local caption = (narrow and ("x" .. n) or ("Invocar x" .. n)) .. " · " .. price
				action(ctx, stage, "Summon" .. n, caption, 12 + (i - 1) * (bw + 12), actionY, bw, 52, function() ctx.startSummon(n) end,
					near and (d.moeda or 0) >= cost and #all > 0, not near and "Viaje até o banner para invocar." or "Moedas insuficientes.", P.success, "StartSummon", { size = narrow and 20 or 24, icon = "coins" })
			end
		else
			areaUnlock(ctx, stage, a, 12, actionY, bw, 52)
			action(ctx, stage, "ViewAreas", "Ver ilhas", 24 + bw, actionY, bw, 52, function() ctx.open("Areas") end, true, nil, P.neutral)
		end
	end
	local pity = d.pity or { l = 0, m = 0 }
	for i, r in ipairs({ { "Mítico+", pity.m or 0, Config.PITY_MITICO, "mitico" }, { "Lendário+", pity.l or 0, Config.PITY_LENDARIO, "lendario" } }) do
		local yy = stageH - 58 + (i - 1) * 26
		T.progress(stage, "Pity_" .. i, 12, yy, centerW - 24, 20, math.min(r[2] / r[3], 1), T.rar(r[4]).cor)
		text(stage, "PityLabel_" .. i, r[1], 20, yy, centerW * .55 - 20, 20, 13, WHITE, T.LEFT, "heavy")
		text(stage, "PityCount_" .. i, r[2] .. " / " .. r[3], centerW * .55, yy, centerW * .45 - 20, 20, 13, WHITE, T.RIGHT, "heavy")
	end
	local catalog = T.panel(p, "BannerCatalog", rightX, rightY, rightW, rightH, { bg = P.bg0, radius = 6, strokeColor = P.lineSoft, strokeWidth = 1 })
	label(catalog, "Title", "Unidades", 10, 8, rightW - 20, 26, 22)
	text(catalog, "OddsHint", "Chance por raridade", 10, 36, rightW - 20, 20, 14, P.text2)
	local list = T.scroll(catalog, "BannerUnits", 8, 66, rightW - 16, rightH - 130, P.violet)
	list.ClipsDescendants = true
	local cw = rightW - 30
	local cols = cw >= 210 and 2 or 1
	local cardW = (cw - (cols - 1) * 8) / cols
	local cardH = cols == 2 and 150 or 102
	for i, def in ipairs(all) do
		local r = T.rar(def.raridade)
		local known = d.index and d.index.pets and d.index.pets[def.id]
		local secret = def.raridade == "secreto" and not known
		local card = T.tile(list, "Unit_" .. def.id, ((i - 1) % cols) * (cardW + 8), math.floor((i - 1) / cols) * (cardH + 8), cardW, cardH, def.raridade, { animated = false, dim = secret })
		local artS = cols == 2 and 76 or 64
		local artX = cols == 2 and (cardW - artS) / 2 or 4
		if secret then T.lock(card, artX + artS / 2 - 20, 18, 40, P.text3)
		else T.preview(card, "pet", def.id, artX, 4, artS, artS, false) end
		local tx, ty, tw = cols == 2 and 6 or 76, cols == 2 and 82 or 8, cols == 2 and cardW - 12 or cardW - 82
		T.para(card, "Name", secret and "???" or def.nome, tx, ty, tw, 34, 14, WHITE, T.CENTER, "title")
		text(card, "Odds", string.format("%.2f%%", odds[def.raridade] or 0), cols == 2 and 6 or 76, cols == 2 and 120 or 58, cols == 2 and cardW - 12 or cardW - 82, 23, 16, r.cor, T.CENTER, "title")
	end
	list.CanvasSize = UDim2.fromOffset(0, math.ceil(#all / cols) * (cardH + 8))
	if #all == 0 then T.emptyState(list, "Empty", "Sem unidades", "Nenhuma unidade neste banner.", 0, 0, cw, 190) end
	if narrow and hasResults then
		T.button(catalog, "LastResult", "Resultado", 10, rightH - 54, (rightW - 30) / 2, 44, P.neutral, ctx.showLastSummon, { size = 17 })
		T.button(catalog, "Rates", "Chances", (rightW + 10) / 2, rightH - 54, (rightW - 30) / 2, 44, P.violet, function() M.rates(ctx) end, { size = 17 })
	else T.button(catalog, "Rates", "Ver chances", 10, rightH - 54, rightW - 20, 44, P.violet, function() M.rates(ctx) end, { size = 18 }) end
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
		T.button(p, "Equipment", "Equipamentos", (w + 12) / 2, quickY, (w - 12) / 2, 52, P.neutral, function() ctx.storeTab = "Picaretas"; ctx.open("Equipment") end, { size = 15 })
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
		T.button(p, "Equipment", "Melhorar equipamento", 0, h - 52, 236, 52, P.neutral, function() ctx.storeTab = "Picaretas"; ctx.open("Equipment") end, { size = 15 })
		text(p, "BaseNote", "Lista: valor base. Total: inclui seus bônus.", 252, h - 52, w - 252, 52, 13, P.text3)
	end
end

local QUEST_ICON = { minerar = "pickaxe", epico = "shiny", chefe = "forge", invocar = "summon", vender = "coins" }

function M.progress(ctx,p,w,h)
 local d=ctx.data
 local selected=ctx.questArea or Players.LocalPlayer:GetAttribute("CurrentAreaId") or 1
 if not Config.areaPorId(selected) then selected=1 end
 ctx.questArea=selected
 local railW=w<900 and 170 or 240
 local gutter=20
 local rw=w-railW-gutter
 local rail=T.scroll(p,"QuestIslands",0,0,railW,h,P.violet)
 for i,a in ipairs(Config.Areas) do
  local y=(i-1)*82
  local col=Config.Temas[a.tema].cor
  local b=T.new("TextButton",{Name="Island_"..a.id,Text="",Position=UDim2.fromOffset(3,y+3),Size=UDim2.fromOffset(railW-16,70),BackgroundColor3=P.ink,BorderSizePixel=0,ClipsDescendants=true},rail)
  T.corner(b,7);T.stroke(b,selected==a.id and P.text or col,selected==a.id and 3 or 1.5)
  local art=T.image(b,"Island",T.areaImage(a.id),0,0,railW-16,70);art.ScaleType=Enum.ScaleType.Crop;art.ImageColor3=Color3.fromRGB(115,110,130)
  T.frame(b,"Shade",0,0,railW-16,70,P.ink,.52)
  T.para(b,"Name",a.nome,10,8,railW-36,40,w<900 and 19 or 22,P.text,T.LEFT,"title")
  local done,total=0,0
  for _,q in ipairs(Config.Missoes[a.id] or {}) do total+=1;if d.missoes and d.missoes[q.id] and d.missoes[q.id].r then done+=1 end end
  T.text(b,"Progress",hasArea(ctx,a.id) and (done.." / "..total.." concluídas") or "Bloqueada",10,47,railW-36,18,12,hasArea(ctx,a.id) and col or P.text3,T.LEFT,"label",1)
  T.bindInteraction(b,function() ctx.questArea=a.id;ctx.refresh() end)
 end
 rail.CanvasSize=UDim2.fromOffset(0,#Config.Areas*82)
 local a=Config.areaPorId(selected)
 local col=Config.Temas[a.tema].cor
 local content=T.frame(p,"MissionBoard",railW+gutter,0,rw,h,nil,1)
 T.text(content,"IslandTitle",a.nome,0,0,rw-200,42,30,P.text,T.LEFT,"title",2)
 local ready,list={},{}
 for i,q in ipairs(Config.Missoes[selected] or {}) do
  local state=d.missoes and d.missoes[q.id] or {p=0,r=false}
  local rank=state.r and 3 or state.p>=q.meta and 1 or 2
  table.insert(list,{def=q,state=state,rank=rank,index=i})
  if rank==1 then table.insert(ready,q) end
 end
 table.sort(list,function(x,y) if x.rank~=y.rank then return x.rank<y.rank end;return x.index<y.index end)
 action(ctx,content,"ClaimAll","Resgatar todas",rw-190,0,190,46,function()
  local received=0;ctx.batchQuestAudio=true
  local ok,err=pcall(function() for _,q in ipairs(ready) do local result=ctx.invoke("ResgatarMissao",q.id);if result and result.ok then received+=q.premio end end end)
  ctx.batchQuestAudio=false
  if received>0 then T.som("quest_complete");ctx.coinBurst(received) end
  ctx.refresh();if not ok then error(err) end
 end,hasArea(ctx,selected) and #ready>0,"Complete uma missão para resgatar.",P.success,"ClaimQuests")
 local scroll=T.scroll(content,"Quests",0,62,rw,h-62,col)
 local cw=rw-14
 if not hasArea(ctx,selected) then
  T.lock(scroll,28,28,58,col)
  T.para(scroll,"Locked","Desbloqueie "..a.nome.." para começar estas missões.",106,25,cw-130,85,23,P.text,T.LEFT,"title")
  T.button(scroll,"ViewIsland","Ver ilha",106,124,240,52,col,function() ctx.open("Areas") end)
  scroll.CanvasSize=UDim2.fromOffset(0,210);return
 end
 for i,item in ipairs(list) do
  local q,state=item.def,item.state
  local claimed,readyNow=item.rank==3,item.rank==1
  local rowH=138
  local tone=claimed and P.neutral or readyNow and P.success or col
  local row=T.panel(scroll,"Quest_"..q.id,3,(i-1)*(rowH+14)+3,cw-6,rowH,{bg=P.bg1,strokeColor=tone,strokeWidth=2})
  T.texture(row,"halftone",.89,tone,180)
  T.frame(row,"Accent",0,10,4,rowH-20,tone,0)
  local iconBG=T.panel(row,"Medallion",14,16,56,56,{bg=tone:Lerp(P.ink,.76),strokeColor=tone,strokeWidth=1.5})
  T.icon(iconBG,QUEST_ICON[q.tipo] or "quests",2,2,52,52)
  local tw=cw-264
  T.para(row,"Title",q.texto,84,12,tw,56,21,claimed and P.text3 or P.text,T.LEFT,"title")
  T.progress(row,"Progress",84,84,tw,23,math.min(state.p or 0,q.meta)/math.max(1,q.meta),tone,{text=T.format(math.min(state.p or 0,q.meta)).." / "..T.format(q.meta),textSize=15,segments=4})
  T.text(row,"State",claimed and "CONCLUÍDA" or readyNow and "RECOMPENSA LIBERADA" or "EM ANDAMENTO",84,113,tw,18,12,tone,T.LEFT,"label",1)
  local rx=cw-164
  T.icon(row,"coins",rx+10,8,46,46)
  T.text(row,"Reward",T.format(q.premio),rx+58,12,98,40,22,P.gold,T.LEFT,"number",2)
  if claimed then T.text(row,"Claimed","✓ Resgatada",rx,66,150,46,20,P.success,T.CENTER,"title",1.5)
  else
   action(ctx,row,"Claim_"..q.id,readyNow and "Resgatar" or "Em curso",rx,68,150,50,function()
    local res=ctx.invoke("ResgatarMissao",q.id)
    if res and res.ok then ctx.coinBurst(q.premio);ctx.refresh() end
   end,readyNow,"Complete o objetivo para resgatar.",readyNow and P.success or P.neutral,"ClaimQuests")
  end
 end
 scroll.CanvasSize=UDim2.fromOffset(0,#list*152+4)
 if #list==0 then T.emptyState(scroll,"Empty","Nenhuma missão","Esta ilha ainda não tem objetivos disponíveis.",0,0,cw,200) end
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
	local black, orange = Color3.fromRGB(5, 5, 8), Color3.fromRGB(255, 144, 23)
	local board = T.frame(p, "DailySummary", 0, 0, w, h, black, 0)
	local function claim()
		local res = ctx.invoke("ResgatarDaily")
		if res and res.ok then
			if ctx.Notify then ctx.Notify.banner({ title = "Dia " .. day .. " resgatado", subtitle = Config.DAILY[day].texto, color = P.gold, sound = false }) end
			ctx.refresh()
		end
	end
	-- The window already supplies the title and Daily/Index tabs. Keep only status here.
	local headerH = narrow and 88 or 54
	local cols = narrow and 2 or 4
	local cardH = narrow and 226 or math.clamp(math.floor((h - headerH - 26) / 2), 206, 262)
	local usableW = w - 28
	local cardW = math.min((usableW - (cols - 1) * GAP) / cols, cardH * 1.05)
	local gridW = cardW * cols + (cols - 1) * GAP
	local gridX = math.max(0, (w - gridW - 14) / 2)
	local reset = "Próximo resgate em " .. T.clock(86400 - (os.time() % 86400))
	text(board, "State", info.disponivel and ("Dia " .. day .. " disponível") or reset,
		gridX, 0, narrow and gridW or gridW - 170, narrow and 32 or 44, narrow and 16 or 18,
		info.disponivel and P.success or P.text2, T.LEFT, "heavy")
	action(ctx, board, "DailyClaim", "Resgatar", narrow and gridX or gridX + gridW - 154, narrow and 36 or 0,
		narrow and gridW or 154, 44, claim, info.disponivel == true,
		"Esta recompensa estará disponível no próximo dia.", orange, "DailyClaim", { size = 20 })
	local scroll = T.scroll(board, "DailyRewards", gridX, headerH, gridW + 14, math.max(90, h - headerH), orange)
	scroll.ClipsDescendants = true
	local icons = { moedas = "coins", boost = "potion", pet = "gift", hats = "gift" }
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
		local x = ((i - 1) % cols) * (cardW + GAP)
		local y = 4 + math.floor((i - 1) / cols) * (cardH + 12)
		local card = T.frame(scroll, "Day_" .. i, x, y, cardW, cardH, black, 0)
		T.corner(card, 5)
		T.new("UIStroke", { Color = available and orange or Color3.fromRGB(98, 98, 105), Thickness = available and 2 or 1, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, card)
		local artClip = T.frame(card, "RewardArtClip", 1, 1, cardW - 2, cardH - 45, nil, 1)
		artClip.ClipsDescendants = true
		-- A restrained color field identifies reward rarity without enlarging the bitmap.
		local glow = T.frame(artClip, "RewardGlow", 0, 0, cardW - 2, cardH - 45, rewardColor, .94)
		T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(1, claimed and .7 or .1) }) }, glow)
		T.text(card, "Day", "DIA " .. i, 8, 5, cardW - 16, 28, 22, orange, T.CENTER, "title", 2)
		T.para(card, "Reward", def.texto, 10, 35, cardW - 20, 30, 14, claimed and P.text3 or WHITE, T.CENTER, "heavy")
		local first = def.itens and def.itens[1]
		local artS = math.min(144, cardW - 36, cardH - 105)
		local artY = 66 + math.max(0, (cardH - 112 - artS) / 2)
		local rewardArt = T.icon(artClip, icons[first and first.tipo] or "gift", (cardW - artS) / 2 - 1, artY, artS, artS)
		rewardArt.ImageTransparency = claimed and .45 or (available and 0 or .18)
		for itemIndex = 2, math.min(3, #(def.itens or {})) do
			local item = def.itens[itemIndex]
			local iconS = math.min(36, artS * .4)
			local iconX = (cardW - artS) / 2 + (itemIndex == 2 and artS - iconS * .35 or -iconS * .65)
			local icon = T.icon(artClip, icons[item.tipo] or "gift", iconX, artY + artS - iconS, iconS, iconS)
			icon.ImageTransparency = rewardArt.ImageTransparency
		end
		if available then
			action(ctx, card, "ClaimDay_" .. i, "Resgatar", 1, cardH - 44, cardW - 2, 43, claim, true, nil, orange, "DailyClaim", { size = 20 })
		else
			local base = T.frame(card, "ClaimedStrip", 1, cardH - 44, cardW - 2, 43, claimed and WHITE or Color3.fromRGB(57, 57, 62), 0)
			T.corner(base, 4)
			T.text(base, "Status", claimed and "RESGATADO" or (today and "AGUARDE" or "BLOQUEADO"), 5, 0, cardW - 12, 43, narrow and 18 or 24,
				claimed and Color3.fromRGB(20, 235, 35) or Color3.fromRGB(189, 189, 197), T.CENTER, "title", 2)
			if not claimed then T.lock(artClip, cardW / 2 - 20, artY + artS / 2 - 18, 40, WHITE) end
		end
	end
	local endY = 4 + math.ceil(#Config.DAILY / cols) * (cardH + 12)
	T.para(scroll, "CycleRule", "O ciclo avança ao resgatar. Faltar um dia não remove suas recompensas.", 0, endY + 2, gridW, 42, 14, P.text3, T.LEFT)
	scroll.CanvasSize = UDim2.fromOffset(0, endY + 50)
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
	if h < 380 and ctx.page ~= "Summon" and not ctx.compact then
		local outer = T.scroll(p, "CompactPage_" .. tostring(ctx.page), 0, 0, w, h, P.accent)
		w, h = w - 14, 620
		p = T.frame(outer, "Content", 0, 0, w, h, nil, 1)
		outer.CanvasSize = UDim2.fromOffset(0, h)
	end
	if (ctx.page == "Store" or ctx.page == "Equipment") then M.store(ctx, p, w, h)
	elseif ctx.page == "Areas" or ctx.page == "Play" then M.areas(ctx, p, w, h)
	elseif ctx.page == "Summon" then M.summon(ctx, p, w, h)
	elseif ctx.page == "Forge" then M.forge(ctx, p, w, h)
	elseif ctx.page == "Settings" then M.settings(ctx, p, w, h)
	elseif ctx.page == "Events" then M.daily(ctx, p, w, h)
	else M.progress(ctx, p, w, h) end
end

return M

