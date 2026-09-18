-- UI V2: each page shares Theme components and preserves the existing server contract.
local T = require(script.Parent.Theme)
local Config = require(game.ReplicatedStorage.Config)
local Mon = require(game.ReplicatedStorage:WaitForChild("MonetizacaoConfig"))
local Players = game:GetService("Players")
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
local function action(ctx, p, name, caption, x, y, w, h, fn, enabled, reason, tone, guard)
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
	end, { size = 16, onDisabled = reason and function() ctx.toast(reason, nil, "info") end or nil })
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
	local top = panel(p, "NextUpgrade", 0, 0, w, topH)
	local artS, mainX, actionW = narrow and 76 or 100, narrow and 106 or 128, narrow and 176 or 180
	local mainW = narrow and w - mainX - 16 or w - mainX - actionW - 36
	label(top, "Section", nextDef and "Próxima melhoria" or "Categoria concluída", 16, 10, w - 32, 24, 14, P.text2)
	local shown = nextDef or current
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
			local card = panel(scroll, "Product_" .. def.chave, ((i - 1) % cols) * (cardW + GAP), y + math.floor((i - 1) / cols) * 234, cardW, 222)
			T.icon(card, PASS_ICON[def.chave] or "store", 14, 14, 46, 46)
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
		local thumb = T.image(card, "Scene", T.areaImage(a.id), 10, 10, cardW - 20, 80, unlocked and WHITE or Color3.fromRGB(110, 120, 130))
		thumb.ScaleType = Enum.ScaleType.Crop
		T.corner(thumb, 6)
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
	local narrow = w < 620
	local hasResults = ctx.lastSummonResults and #ctx.lastSummonResults > 0 and ctx.showLastSummon
	local selectW = narrow and (w - (hasResults and 144 or 0)) or math.min(330, w * .48)
	T.dropdown(p, "Banners", 0, 0, selectW, 52, areaOptions(ctx, true), id, function(value) ctx.bannerArea = value; ctx.refresh() end)
	text(p, "Location", unlocked and (near and "✓ No banner" or "Viaje até o banner para invocar") or "Ilha bloqueada", narrow and 0 or selectW + 18, narrow and 60 or 0,
		narrow and w or w - selectW - (hasResults and 196 or 18), narrow and 24 or 52, 15,
		near and P.success or P.text2)
	if hasResults then T.button(p, "LastResult", narrow and "Resultado" or "Último resultado", w - (narrow and 132 or 176), 0, narrow and 132 or 176, 52, P.neutral, ctx.showLastSummon, { size = 15 }) end
	local pity = d.pity or { l = 0, m = 0 }
	local guaranteeY = narrow and 94 or 64
	local guarantees = panel(p, "Guarantees", 0, guaranteeY, w, 74)
	local statW = (w - 190) / 2
	if narrow then
		T.para(guarantees, "GuaranteeText", "Lendário+ em " .. math.max(0, Config.PITY_LENDARIO - (pity.l or 0)) .. " giros\nMítico+ em " .. math.max(0, Config.PITY_MITICO - (pity.m or 0)) .. " giros",
			12, 8, w - 164, 58, 16, P.text2, T.LEFT)
	else
		label(guarantees, "Legendary", "Lendário+", 14, 9, statW - 20, 20, 14, T.rar("lendario").cor)
		text(guarantees, "LegendaryCount", "em até " .. math.max(0, Config.PITY_LENDARIO - (pity.l or 0)) .. " giros", 14, 33, statW - 20, 21, 15, P.text2)
		label(guarantees, "Mythic", "Mítico+", statW + 14, 9, statW - 20, 20, 14, T.rar("mitico").cor)
		text(guarantees, "MythicCount", "em até " .. math.max(0, Config.PITY_MITICO - (pity.m or 0)) .. " giros", statW + 14, 33, statW - 20, 21, 15, P.text2)
	end
	T.button(guarantees, "Rates", "Ver chances", w - 148, 11, 136, 52, P.neutral, function() M.rates(ctx) end, { size = 15 })
	local footerH, cardsY = 124, guaranteeY + 88
	local scroll = T.scroll(p, "BannerUnits", 0, cardsY, w, math.max(48, h - cardsY - footerH - 12), P.accent)
	local all, odds = {}, {}
	for _, def in ipairs(Config.Pets) do if def.area == id then table.insert(all, def) end end
	for _, r in ipairs(probabilities(ctx, id)) do odds[r.key] = r.pct end
	table.sort(all, function(x, y) return T.rar(x.raridade).ordem > T.rar(y.raridade).ordem end)
	local cols = math.max(2, math.floor((w - 14 + 12) / 156))
	local cardW = (w - 14 - (cols - 1) * 12) / cols
	local cardH = 210
	for i, def in ipairs(all) do
		local r = T.rar(def.raridade)
		local known = d.index and d.index.pets and d.index.pets[def.id]
		local secret = def.raridade == "secreto" and not known
		local card = panel(scroll, "Unit_" .. def.id, ((i - 1) % cols) * (cardW + 12), math.floor((i - 1) / cols) * (cardH + 12), cardW, cardH)
		T.frame(card, "RarityMark", 12, 10, 3, 20, r.cor, 0)
		label(card, "Rarity", r.nome, 22, 8, cardW - 34, 24, 13, r.cor)
		if secret then T.lock(card, cardW / 2 - 28, 66, 56, P.text3)
		else T.preview(card, "pet", def.id, 8, 34, cardW - 16, 110, false) end
		label(card, "Name", secret and "???" or def.nome, 12, 148, cardW - 24, 26, 17)
		text(card, "Odds", string.format("%.2f%% da raridade", odds[def.raridade] or 0), 12, 179, cardW - 24, 19, 12, P.text2)
	end
	if #all == 0 then T.emptyState(scroll, "Empty", "Nenhuma unidade", "Este banner ainda não tem unidades disponíveis.", 0, 0, w - 14, 180) end
	scroll.CanvasSize = UDim2.fromOffset(0, math.max(180, math.ceil(#all / cols) * (cardH + 12)))
	local fy = h - footerH
	local foot = panel(p, "SummonActions", 0, fy, w, footerH)
	T.para(foot, "CostRule", d.giroGratis and "1 giro grátis; x10 desconta esse giro." or (T.format(g.custo) .. " moedas por invocação"),
		14, 8, w - 28, 30, 14, P.text2, T.LEFT)
	local bw = (w - 52) / 3
	local goText = near and "✓ No banner" or (narrow and "Viajar" or "Ir ao banner")
	if not unlocked then
		currency(foot, "UnlockCost", a.custo, 14, 42, bw, 28, 19)
		areaUnlock(ctx, foot, a, 14 + bw + 12, 52, bw, 52)
		action(ctx, foot, "ViewAreas", "Ver ilhas", 14 + (bw + 12) * 2, 52, bw, 52, function() ctx.open("Areas") end, true, nil, P.neutral)
	elseif ctx.summonBusy then
		T.setEnabled(T.button(foot, "GoBanner", goText, 14, 52, bw, 52, P.neutral, nil, { size = 16 }), false)
		local prog = text(foot, "Progress", "Invocando...", bw + 28, 42, w - bw - 44, 24, 17, P.text)
		local bar = T.progress(foot, "ProgressBar", bw + 28, 80, w - bw - 44, 10, 0, P.accent)
		ctx.onSummonProgress = function(i, n)
			if prog.Parent then prog.Text = "Invocando " .. i .. " / " .. n; T.setProgress(bar, i / math.max(1, n), P.accent, .12) end
		end
	else
		ctx.onSummonProgress = nil
		action(ctx, foot, "GoBanner", goText, 14, 52, bw, 52, function() ctx.travel("gacha", id, true) end, not near, nil, P.neutral)
		for i, n in ipairs({ 1, 10 }) do
			local cost = g.custo * (d.giroGratis and math.max(0, n - 1) or n)
			local afford = (d.moeda or 0) >= cost
			local caption = "Invocar " .. (n == 1 and "" or "x10 · ") .. (cost == 0 and "grátis" or ((n == 1 and "· " or "") .. T.format(cost)))
			if narrow then caption = (n == 1 and "1× " or "10× ") .. (cost == 0 and "grátis" or T.format(cost)) end
			local reason = not near and "Viaje até o banner para invocar." or "Moedas insuficientes."
			action(ctx, foot, "Summon" .. n, caption, 14 + i * (bw + 12), 52, bw, 52, function() ctx.startSummon(n) end,
				near and afford and #all > 0, reason, i == 1 and P.accent or P.neutral, "StartSummon")
		end
	end
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
	local summary = panel(p, "SaleSummary", 0, 0, w, summaryH)
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
		for _, quest in ipairs(ready) do
			local res = ctx.invoke("ResgatarMissao", quest.id)
			if res and res.ok then received += quest.premio end
		end
		if received > 0 then ctx.coinBurst(received) end
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
	local y = T.section(scroll, "Preferências", 0, 0, colW, P.accent)
	local defs = {
		{ "MusicEnabled", "Música das ilhas", "Trilha sonora do ambiente", true },
		{ "SomMineracaoEnabled", "Sons de mineração", "Golpes, quebras e coleta", true },
		{ "SomInterfaceEnabled", "Sons da interface", "Cliques, abas e confirmação", true },
		{ "LobbyVFXEnabled", "Efeitos do ambiente", "Partículas e efeitos do cenário", true },
		{ "ExpeditionEffectsEnabled", "Efeitos da interface", "Partículas e celebrações da UI", true },
		{ "ExpeditionBlurEnabled", "Desfoque de fundo", "Desfoca o cenário ao abrir menus", true },
		{ "ReducedMotion", "Movimento reduzido", "Reduz escalas, tremores e transições", false },
	}
	for _, def in ipairs(defs) do
		local row = panel(scroll, "Setting_" .. def[1], 0, y, colW, 74)
		label(row, "Name", def[2], 16, 12, colW - 118, 24, 17)
		text(row, "Description", def[3], 16, 40, colW - 118, 20, 14, P.text2)
		local value = Players.LocalPlayer:GetAttribute(def[1])
		local on = value == true or (value == nil and def[4])
		T.toggle(row, "Toggle", colW - 84, 19, on, function(state) Players.LocalPlayer:SetAttribute(def[1], state) end)
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
	text(scroll, "SavedHint", "Preferências aplicadas neste dispositivo durante a sessão.", 0, endY + 10, cw, 24, 13, P.text3)
	scroll.CanvasSize = UDim2.fromOffset(0, endY + 48)
end

local DAILY_ICON = { moedas = "coins", boost = "potion", pet = "units", hats = "items" }

local function daily(ctx, p, w, h)
	local d = ctx.data
	local info = d.daily or { dia = 1, disponivel = false }
	local day = math.clamp(info.dia or 1, 1, math.max(1, #Config.DAILY))
	local narrow = w < 620
	local headerH = narrow and 218 or 140
	local header = panel(p, "DailySummary", 0, 0, w, headerH)
	label(header, "Title", "Recompensa do dia " .. day, 16, 14, narrow and w - 32 or w - 280, 32, 24)
	text(header, "State", info.disponivel and "Disponível para resgate" or ("Próxima liberação em " .. T.clock(86400 - (os.time() % 86400))),
		16, 51, narrow and w - 32 or w - 280, 24, 15, info.disponivel and P.success or P.text2)
	T.para(header, "Rule", "O ciclo avança quando você resgata. Faltar um dia não remove recompensas.", 16, 88, narrow and w - 32 or w - 280, narrow and 46 or 36, 14, P.text2, T.LEFT)
	action(ctx, header, "DailyClaim", info.disponivel and "Resgatar recompensa" or "Aguarde o próximo dia", narrow and 16 or w - 248, narrow and 150 or 36, narrow and w - 32 or 232, 52, function()
		local res = ctx.invoke("ResgatarDaily")
		if res and res.ok then
			if ctx.Notify then ctx.Notify.banner({ title = "Dia " .. day .. " resgatado", subtitle = Config.DAILY[day].texto, color = P.gold, sound = false }) end
			ctx.refresh()
		end
	end, info.disponivel == true, "Esta recompensa estará disponível no próximo dia.")
	if not narrow then text(header, "Cycle", "Ciclo de " .. #Config.DAILY .. " dias", w - 248, 99, 232, 20, 14, P.text3, T.CENTER) end
	local scroll = T.scroll(p, "DailyRewards", 0, headerH + 14, w, math.max(90, h - headerH - 14), P.accent)
	local cw = w - 14
	local cols = cw >= 960 and 4 or (cw >= 640 and 3 or 2)
	local cardW = (cw - (cols - 1) * GAP) / cols
	local cardH = 220
	for i, def in ipairs(Config.DAILY) do
		local today, claimed = i == day, i < day
		local card = panel(scroll, "Day_" .. i, ((i - 1) % cols) * (cardW + GAP), math.floor((i - 1) / cols) * (cardH + GAP), cardW, cardH, today)
		label(card, "Day", "Dia " .. i, 14, 12, cardW - 28, 24, 18)
		local kind = def.itens and def.itens[1] and def.itens[1].tipo or "moedas"
		T.icon(card, DAILY_ICON[kind] or "gift", 14, 46, 54, 54)
		T.para(card, "Reward", def.texto, 14, 108, cardW - 28, 66, 16, claimed and P.text3 or P.text, T.LEFT, "title")
		local caption = claimed and "✓ Resgatado" or (today and (info.disponivel and "Disponível agora" or "Próximo resgate") or "A seguir")
		text(card, "Status", caption, 14, 187, cardW - 28, 20, 13, claimed and P.text3 or (today and P.accent or P.text2))
	end
	scroll.CanvasSize = UDim2.fromOffset(0, math.ceil(#Config.DAILY / cols) * (cardH + GAP))
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
					local card = panel(scroll, "Entry_" .. def.id, ((i - 1) % cols) * (cardW + 12), y + math.floor((i - 1) / cols) * 180, cardW, 168)
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
	if ctx.page == "Store" then M.store(ctx, p, w, h)
	elseif ctx.page == "Areas" or ctx.page == "Play" then M.areas(ctx, p, w, h)
	elseif ctx.page == "Summon" then M.summon(ctx, p, w, h)
	elseif ctx.page == "Forge" then M.forge(ctx, p, w, h)
	elseif ctx.page == "Settings" then M.settings(ctx, p, w, h)
	elseif ctx.page == "Events" then M.daily(ctx, p, w, h)
	else M.progress(ctx, p, w, h) end
end

return M

