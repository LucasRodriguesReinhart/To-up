-- ============================================================================
-- MENUS V2 · Loja, Passes, Viajar, Invocar, Forja, Missões, Diário/Index, Config.
-- Cada tela responde: onde estou, o que tenho, qual a ação principal e o que vem depois.
-- ============================================================================
local T = require(script.Parent.Theme)
local Config = require(game.ReplicatedStorage.Config)
local Players = game:GetService("Players")
local Mon = require(game.ReplicatedStorage:WaitForChild("MonetizacaoConfig"))
local P = T.P
local WHITE = Color3.new(1, 1, 1)
local M = {}

local function hasArea(ctx, id) return ctx.data and ctx.data.areas and ctx.data.areas[id] == true end
local function areaColor(id)
	local a = Config.areaPorId(id)
	local t = a and Config.Temas[a.tema]
	return t and t.cor or P.accent
end
local function hex(c) return "#" .. c:ToHex() end

-- botão com ação à esquerda e preço (moedas) à direita
local function priceButton(parent, name, action, amount, x, y, w, h, tone, fn, enabled, onDisabled)
	local b = T.button(parent, name, "", x, y, w, h, tone, fn, { onDisabled = onDisabled })
	local face = b.Face
	local fh = face.Size.Y.Offset
	local lbl = T.text(face, "Action", action, 14, 0, w * .5, fh, math.min(19, math.floor(fh * .44)), P.text, T.LEFT, "title", 1.4)
	local isz = math.floor(fh * .7)
	local price = T.text(face, "Price", amount == 0 and "GRÁTIS" or T.format(amount), w - 12 - 110, 0, 110 - (amount == 0 and 0 or isz + 4), fh,
		math.min(20, math.floor(fh * .46)), WHITE, T.RIGHT, "display", 1.4)
	if amount ~= 0 then T.icon(face, "coins", w - 10 - isz, (fh - isz) / 2, isz, isz) end
	local on = enabled == nil or (enabled and true or false)
	T.setEnabled(b, on)
	if not on then lbl.TextColor3 = P.text3; price.TextColor3 = P.text3 end
	return b
end

local function robuxButton(parent, name, def, owned, x, y, w, h, ctx)
	local label = owned and "Adquirido" or (def.id > 0 and ("R$  " .. def.robux) or "Em breve")
	local b = T.button(parent, name, label, x, y, w, h, owned and P.neutral or P.robux, function()
		if owned or def.id <= 0 then return end
		ctx.invoke("ComprarRobux", def.chave)
	end)
	T.setEnabled(b, not owned and def.id > 0)
	return b
end

local function hoverLift(btn, stroke, col, base)
	local sc = T.scaleOf(btn)
	btn.MouseEnter:Connect(function() if stroke then stroke.Color = col end; T.tween(sc, .14, { Scale = 1.02 }, Enum.EasingStyle.Quad) end)
	btn.MouseLeave:Connect(function() if stroke then stroke.Color = base end; T.tween(sc, .14, { Scale = 1 }, Enum.EasingStyle.Quad) end)
end

-- ================================================================ LOJA: EQUIPAMENTOS
local function compareRow(p, name, x, y, w, labelText, from, to, delta, good)
	local row = T.frame(p, name, x, y, w, 40, P.bg0, .3)
	T.corner(row, 10)
	T.text(row, "Label", labelText, 12, 0, 110, 40, 15, P.text2, T.LEFT, "body")
	local v = T.text(row, "Values", "<font color=\"" .. hex(P.text3) .. "\">" .. from .. "</font>   →   " .. to, 110, 0, w - 110 - 86, 40, 17, P.text, T.RIGHT, "title")
	v.RichText = true
	if delta then T.chip(row, "Delta", delta, w - 78, 7, 26, good and P.success or P.danger, { size = 13, w = 68 }) end
	return row
end

local function equipmentStore(ctx, p, w, h)
	local d = ctx.data
	local pick = ctx.storeTab == "Picaretas"
	local defs = pick and Config.Picaretas or Config.Mochilas
	local currentId = pick and d.picareta or d.mochilaTier
	local curIdx = 1
	for i, x in ipairs(defs) do if x.id == currentId then curIdx = i end end
	local cur = defs[curIdx]
	local function owned(i, def)
		if pick then return (d.picaretasCompradas and d.picaretasCompradas[def.id] == true) or i == 1 end
		return i <= curIdx
	end
	local nxt, nxtIdx
	if pick then nxt, nxtIdx = ctx.nextPickaxe(d) else nxt, nxtIdx = defs[curIdx + 1], curIdx + 1 end
	local function buy(def)
		ctx.confirm(def.nome, pick and "A nova picareta fica disponível para equipar na hora." or "A mochila nova substitui a atual com mais capacidade.", function()
			local res = ctx.invoke(pick and "ComprarPicareta" or "ComprarMochila", def.id)
			if res and res.ok then ctx.refresh() end
		end, { cost = def.custo, confirmText = "Comprar", tone = P.success })
	end

	local stacked = w < 980
	local heroW = stacked and w or 396
	local heroH = stacked and 244 or h
	local hero = T.panel(p, "NextUpgrade", 0, 0, heroW, heroH, { bg = P.bg2, radius = 16, strokeColor = nxt and P.gold:Lerp(P.bg2, .5) or P.lineSoft })
	if nxt then
		local wc = areaColor(nxt.mundo or 1)
		local area = Config.Areas[nxt.mundo or 1]
		local afford = d.moeda >= nxt.custo
		-- a arte cede altura para nome + comparações + preço + botão nunca se encostarem
		local compareRows = pick and 2 or 1
		local reserved = 52 + 12 + 62 + compareRows * 48 + 14 + 182
		local artX, artY, artW, artH = 16, 52, heroW - 32, math.clamp(heroH - reserved, 110, 206)
		if stacked then artX, artY, artW, artH = 12, 12, 220, heroH - 24 end
		if not stacked then T.section(hero, "Próximo upgrade", 16, 14, heroW - 32, P.gold) end
		local art = T.frame(hero, "Art", artX, artY, artW, artH, P.bg0, 0)
		T.corner(art, 14)
		local glow = T.frame(art, "Glow", 0, 0, artW, artH, wc, 0)
		T.corner(glow, 14)
		T.fade(glow, 90, 1, .72)
		T.stripes(art, "Energy", 0, 0, artW, artH, WHITE, .96)
		if pick then T.preview(art, "pickaxe", nxt.id, 10, 8, artW - 20, artH - 16, true)
		else T.statIcon(art, "capacidade", (artW - 160) / 2, (artH - 160) / 2, 160, 160) end
		T.chip(art, "World", T.upper(area and area.nome or ""), 10, 10, 24, wc, { size = 12 })
		local ix = stacked and 248 or 16
		local iw = stacked and heroW - 260 or heroW - 32
		local iy = stacked and 12 or (artY + artH + 12)
		T.text(hero, "Name", nxt.nome, ix, iy, iw, 32, 26, P.text, T.LEFT, "display", 1.2)
		T.text(hero, "Tier", "Nível " .. nxtIdx .. " de " .. #defs .. "   ·   atual: " .. (cur and cur.nome or "-"), ix, iy + 32, iw, 20, 14, P.text2, T.LEFT, "body")
		local ry = iy + 62
		if pick then
			compareRow(hero, "Damage", ix, ry, iw, "Dano", string.format("x%.2f", cur.mult), string.format("<font color=\"%s\">x%.2f</font>", hex(P.success), nxt.mult),
				"+" .. math.floor((nxt.mult / cur.mult - 1) * 100 + .5) .. "%", true)
			if not stacked then
				local faster = nxt.intervalo <= cur.intervalo
				compareRow(hero, "Speed", ix, ry + 48, iw, "Golpe", string.format("%.2fs", cur.intervalo), string.format("<font color=\"%s\">%.2fs</font>", hex(faster and P.success or P.warning), nxt.intervalo),
					nil, faster)
			end
		else
			compareRow(hero, "Capacity", ix, ry, iw, "Capacidade", T.format(cur.capacidade), string.format("<font color=\"%s\">%s</font>", hex(P.success), T.format(nxt.capacidade)),
				"+" .. math.floor((nxt.capacidade / math.max(1, cur.capacidade) - 1) * 100 + .5) .. "%", true)
		end
		local by = heroH - (stacked and 64 or 70)
		if not stacked then
			local priceRow = T.panel(hero, "Price", 16, by - 112, iw, 56, { bg = P.bg0, radius = 12 })
			T.text(priceRow, "Label", "PREÇO", 14, 0, 100, 56, 14, P.text2, T.LEFT, "title")
			T.icon(priceRow, "coins", iw - 186, 9, 38, 38)
			T.text(priceRow, "Value", T.format(nxt.custo), iw - 144, 0, 130, 56, 26, P.gold, T.RIGHT, "display", 1.4)
			if afford then
				T.text(hero, "Afford", "✓  Você já pode comprar!", 16, by - 48, iw, 36, 15, P.success, T.CENTER, "title")
			else
				T.text(hero, "Afford", "Faltam " .. T.format(nxt.custo - d.moeda) .. " moedas", 16, by - 54, iw, 22, 14, P.text2, T.CENTER, "title")
				T.progress(hero, "AffordBar", 16, by - 30, iw, 14, d.moeda / nxt.custo, P.gold)
			end
		end
		local b = priceButton(hero, "BuyNext", "Comprar", nxt.custo, ix, by, iw, 58, P.success, function() buy(nxt) end, afford,
			function() ctx.toast("Faltam " .. T.format(nxt.custo - d.moeda) .. " moedas", nil, "warning") end)
		if afford then T.pop(b, 1.06, .4) end
	else
		T.section(hero, "Equipamento", 16, 14, heroW - 32, P.gold)
		T.icon(hero, pick and "pickaxe" or "items", (heroW - 150) / 2, 80, 150, 150)
		T.text(hero, "Max", pick and "Picareta máxima!" or "Mochila máxima!", 16, 244, heroW - 32, 36, 26, P.gold, T.CENTER, "display", 1.4)
		T.para(hero, "MaxDesc", "Você já tem o melhor equipamento desta categoria.", 16, 284, heroW - 32, 44, 16, P.text2, T.CENTER)
	end

	-- catálogo completo
	local gx = stacked and 0 or heroW + 16
	local gy = stacked and heroH + 14 or 0
	local gw, gh = w - gx, h - gy
	local s = T.scroll(p, "Catalog", gx, gy, gw, gh, P.gold)
	local ownedCount = 0
	for i, def in ipairs(defs) do if owned(i, def) then ownedCount += 1 end end
	local top = T.section(s, pick and "Todas as picaretas" or "Todas as mochilas", 0, 0, gw - 14, P.gold, nil, ownedCount .. " / " .. #defs .. " adquiridas")
	local cols = gw >= 960 and 3 or (gw >= 540 and 2 or 1)
	local gap = 12
	local cw = (gw - 14 - (cols - 1) * gap) / cols
	local ch = 138
	for i, def in ipairs(defs) do
		local n = i - 1
		local x = (n % cols) * (cw + gap)
		local y = top + math.floor(n / cols) * (ch + gap)
		local isOwned, inUse = owned(i, def), def.id == currentId
		local afford = d.moeda >= def.custo
		local wc = areaColor(def.mundo or 1)
		local card = T.panel(s, "Product_" .. def.id, x, y, cw, ch, { bg = inUse and P.bg3 or P.bg2, radius = 14, strokeColor = inUse and P.gold or P.lineSoft })
		local art = T.frame(card, "Art", 10, 10, 116, 118, P.bg0, 0)
		T.corner(art, 12)
		local glow = T.frame(art, "Glow", 0, 0, 116, 118, wc, 0)
		T.corner(glow, 12)
		T.fade(glow, 90, 1, isOwned and .7 or .88)
		if pick then T.preview(art, "pickaxe", def.id, 4, 4, 108, 110, false, not isOwned and not afford)
		else
			local bp = T.statIcon(art, "capacidade", 13, 13, 90, 90)
			if not isOwned then bp.ImageColor3 = Color3.fromRGB(120, 118, 140) end
		end
		local area = Config.Areas[def.mundo or 1]
		T.text(card, "Name", def.nome, 138, 12, cw - 150, 22, 17, isOwned and P.text or P.text2, T.LEFT, "title")
		T.text(card, "Stat", pick and string.format("x%.2f dano  ·  %.2fs", def.mult, def.intervalo) or (T.format(def.capacidade) .. " de capacidade"), 138, 36, cw - 150, 18, 14, P.text2, T.LEFT, "body")
		T.text(card, "Tier", (area and area.nome or "") .. "  ·  Nível " .. i, 138, 56, cw - 150, 16, 12, wc, T.LEFT, "title")
		local ax, ay, aw = 138, ch - 50, cw - 150
		if inUse then
			T.chip(card, "InUse", "✓  EM USO", ax, ay + 4, 32, P.gold, { size = 13, w = aw })
		elseif isOwned then
			if pick then
				T.button(card, "Equip", "Equipar", ax, ay, aw, 42, P.info, function()
					local res = ctx.invoke("EquiparPicareta", def.id)
					if res and res.ok then ctx.refresh() end
				end, { sound = "ui_equipar" })
			else
				T.chip(card, "Owned", "ADQUIRIDA", ax, ay + 4, 32, P.text3, { size = 13, w = aw })
			end
		else
			priceButton(card, "Buy", "Comprar", def.custo, ax, ay, aw, 42, afford and P.success or P.neutral, function() buy(def) end, afford,
				function() ctx.toast("Faltam " .. T.format(def.custo - d.moeda) .. " moedas", nil, "warning") end)
			if i == nxtIdx then
				local tag = T.chip(card, "NextTag", "PRÓXIMO", 16, 14, 22, P.gold, { solid = true, size = 11 })
				tag.ZIndex = 5
			end
		end
	end
	s.CanvasSize = UDim2.fromOffset(0, top + math.ceil(#defs / cols) * (ch + gap))
end

-- ================================================================ LOJA: PASSES
local PASS_ICON = { VIP = "vip", Lucky = "shiny", HatSlot = "units", Inventario = "items", AutoSell = "forge",
	BoostSorte = "potion", BoostMoedas = "coins", PackP = "coins", PackM = "coins", PackG = "coins", InvocarChefe = "summon", Starter = "store" }

local function productCard(ctx, s, def, x, y, cw, ch, owned, accent)
	local card = T.panel(s, "Product_" .. def.chave, x, y, cw, ch, { bg = P.bg2, radius = 14, strokeColor = owned and P.success:Lerp(P.bg2, .4) or P.lineSoft })
	local badge = T.frame(card, "IconBack", 14, 14, 80, 80, P.bg0, 0)
	T.corner(badge, 16)
	local glow = T.frame(badge, "Glow", 0, 0, 80, 80, accent, 0)
	T.corner(glow, 16)
	T.fade(glow, 90, 1, .65)
	T.icon(badge, PASS_ICON[def.chave] or "vip", 6, 6, 68, 68)
	T.text(card, "Name", def.nome, 106, 18, cw - 120, 26, 19, P.text, T.LEFT, "display")
	if owned then T.chip(card, "Owned", "✓ ATIVO", 106, 50, 24, P.success, { size = 12 })
	elseif def.minutos then T.chip(card, "Duration", def.minutos .. " MIN", 106, 50, 24, accent, { size = 12 }) end
	T.para(card, "Desc", def.desc or "", 14, 102, cw - 28, ch - 102 - 58, 15, P.text2, T.LEFT)
	robuxButton(card, "Buy", def, owned, 14, ch - 54, cw - 28, 44, ctx)
	return card
end

local function passesStore(ctx, p, w, h)
	local d = ctx.data
	local s = T.scroll(p, "PassCatalog", 0, 0, w, h, P.gold)
	local cw0 = w - 14
	local y = 0
	local starter
	for _, x in ipairs(Mon.PRODUTOS) do if x.starter then starter = x end end
	local bought = d.compras and (d.compras.Starter or 0) > 0
	if starter and not bought then
		local card = T.panel(s, "Starter", 0, 0, cw0, 176, { bg = P.bg2, radius = 16, strokeColor = P.gold })
		local glow = T.frame(card, "Glow", 0, 0, cw0 * .6, 176, P.gold, 0)
		T.corner(glow, 16)
		T.fade(glow, 0, .75, 1)
		T.stripes(card, "Energy", cw0 - 520, 0, 300, 176, P.gold, .92)
		T.icon(card, "store", 18, 18, 140, 140)
		T.chip(card, "Deal", "OFERTA INICIAL  ·  1 POR CONTA", 176, 20, 26, P.gold, { solid = true, size = 12 })
		T.text(card, "Name", starter.nome, 176, 52, cw0 - 460, 38, 32, P.text, T.LEFT, "display", 1.4)
		T.para(card, "Desc", starter.desc, 176, 94, cw0 - 460, 44, 16, P.text2, T.LEFT)
		local value = T.text(card, "Value", "<s>R$ " .. starter.valorSeparado .. "</s>   <font color=\"" .. hex(P.success) .. "\">R$ " .. starter.robux .. "</font>", 176, 138, 300, 24, 17, P.text3, T.LEFT, "title")
		value.RichText = true
		local b = robuxButton(card, "Buy", starter, false, cw0 - 262, 60, 240, 58, ctx)
		T.shine(card, 3, .8)
		y = 192
	end
	y += T.section(s, "Gamepasses", 0, y, cw0, P.gold, nil, "permanentes")
	local cols = cw0 >= 900 and 3 or (cw0 >= 560 and 2 or 1)
	local gap = 12
	local cw = (cw0 - (cols - 1) * gap) / cols
	local ch = 196
	for i, def in ipairs(Mon.PASSES) do
		local owned = d.passes and d.passes[def.chave]
		productCard(ctx, s, def, ((i - 1) % cols) * (cw + gap), y + math.floor((i - 1) / cols) * (ch + gap), cw, ch, owned, P.gold)
	end
	y += math.ceil(#Mon.PASSES / cols) * (ch + gap) + 8
	y += T.section(s, "Boosts e packs", 0, y, cw0, P.accent, nil, "uso imediato")
	local n = 0
	for _, def in ipairs(Mon.PRODUTOS) do
		if not def.starter then
			productCard(ctx, s, def, (n % cols) * (cw + gap), y + math.floor(n / cols) * (ch + gap), cw, ch, false, def.boost == "sorte" and P.success or P.accent)
			n += 1
		end
	end
	y += math.ceil(n / cols) * (ch + gap)
	T.text(s, "Rule", "Preços em Robux. O item é entregue logo após a confirmação da Roblox.", 0, y, cw0, 24, 14, P.text3, T.CENTER, "body")
	s.CanvasSize = UDim2.fromOffset(0, y + 36)
end

function M.store(ctx, p, w, h)
	if ctx.storeTab == "Passes" then passesStore(ctx, p, w, h) else equipmentStore(ctx, p, w, h) end
end

-- ================================================================ VIAJAR
function M.areas(ctx, p, w, h)
	local d = ctx.data
	local s = T.scroll(p, "AreaCatalog", 0, 0, w, h, P.teal)
	local cw0 = w - 14
	local y = T.section(s, "Atalhos do lobby", 0, 0, cw0, P.teal)
	local quick = {
		{ "Lobby", "Praça central", "Portais, banners e NPCs", "areas", P.accent, function() ctx.travel("area", 0) end },
		{ "Ignis", "Forja de Ignis", "Vender minérios", "forge", P.ember, function() ctx.open("Forge") end },
		{ "Equip", "Equipamentos", "Picaretas e mochilas", "pickaxe", P.gold, function() ctx.storeTab = "Picaretas"; ctx.open("Store") end },
	}
	local qcols = cw0 >= 700 and 3 or 1
	local qw = (cw0 - (qcols - 1) * 12) / qcols
	for i, q in ipairs(quick) do
		local b = T.new("TextButton", { Name = "Quick_" .. q[1], Text = "", AutoButtonColor = false, BackgroundColor3 = P.bg2, BorderSizePixel = 0,
			Position = UDim2.fromOffset(((i - 1) % qcols) * (qw + 12), y + math.floor((i - 1) / qcols) * 84), Size = UDim2.fromOffset(qw, 72) }, s)
		T.corner(b, 14)
		local st = T.stroke(b, P.lineSoft, 1.5)
		local glow = T.frame(b, "Glow", 0, 0, qw, 72, q[5], 0)
		T.corner(glow, 14)
		T.fade(glow, 0, .8, 1)
		T.icon(b, q[4], 10, 6, 60, 60)
		T.text(b, "Name", q[2], 80, 12, qw - 130, 26, 18, P.text, T.LEFT, "title")
		T.text(b, "Desc", q[3], 80, 38, qw - 130, 20, 14, P.text2, T.LEFT, "body")
		T.text(b, "Arrow", "›", qw - 40, 0, 28, 72, 34, P.text3, T.CENTER, "title")
		hoverLift(b, st, q[5], P.lineSoft)
		b.Activated:Connect(function() T.som("ui_click"); q[6]() end)
	end
	y += math.ceil(#quick / qcols) * 84 + 10
	y += T.section(s, "Ilhas de mineração", 0, y, cw0, P.teal, nil, (function()
		local n = 0
		for _, a in ipairs(Config.Areas) do if d.areas[a.id] then n += 1 end end
		return n .. " / " .. #Config.Areas .. " desbloqueadas"
	end)())
	local current = Players.LocalPlayer:GetAttribute("CurrentAreaId") or 0
	local cols = cw0 >= 900 and 3 or (cw0 >= 560 and 2 or 1)
	local gap = 14
	local cw = (cw0 - (cols - 1) * gap) / cols
	local ch = 244
	local nextLocked = ctx.nextArea(d)
	for i, a in ipairs(Config.Areas) do
		local unlocked = d.areas[a.id] == true
		local isNext = nextLocked and nextLocked.id == a.id
		local here = current == a.id
		local tema = Config.Temas[a.tema]
		local col = tema and tema.cor or P.accent
		local x = ((i - 1) % cols) * (cw + gap)
		local cy = y + math.floor((i - 1) / cols) * (ch + gap)
		local card = T.frame(s, "Island_" .. a.id, x, cy, cw, ch, P.bg0, 0)
		T.corner(card, 16)
		local st = T.stroke(card, here and col or P.lineSoft, here and 2.5 or 1.5)
		local img = T.image(card, "Scene", T.areaImage(a.id), 0, 0, cw, ch, (unlocked or isNext) and WHITE or Color3.fromRGB(80, 84, 104))
		img.ScaleType = Enum.ScaleType.Crop
		T.corner(img, 16)
		local shade = T.frame(card, "Shade", 0, 0, cw, ch, P.bg0, 0)
		T.corner(shade, 16)
		T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, .55), T.kp(.4, .8), T.kp(1, .05) }) }, shade)
		local tint = T.frame(card, "Tint", 0, ch - 110, cw, 110, col, 0)
		T.corner(tint, 16)
		T.fade(tint, 90, 1, .8)
		T.chip(card, "Number", "ILHA " .. a.id, 12, 12, 26, col, { solid = true, size = 12 })
		if here then
			local c, cwid = T.chip(card, "Here", "VOCÊ ESTÁ AQUI", 0, 12, 26, P.accent, { solid = true, size = 12 })
			c.Position = UDim2.fromOffset(cw - cwid - 12, 12)
		elseif not unlocked then
			local lockBack = T.frame(card, "LockBack", cw - 46, 10, 36, 36, P.bg0, .2)
			T.corner(lockBack, 10)
			T.lock(lockBack, 6, 5, 24, isNext and P.gold or P.text2)
		end
		T.text(card, "Name", a.nome, 16, ch - 104, cw - 32, 34, 26, WHITE, T.LEFT, "display", 1.8)
		T.text(card, "Theme", T.upper(tema and tema.nome or "") .. "  ·  " .. (Config.Gachas[a.id] and "banner disponível" or "sem banner"), 16, ch - 72, cw - 32, 18, 12, col:Lerp(WHITE, .35), T.LEFT, "title", 1.2)
		local bx, by, bw = 14, ch - 50, cw - 28
		if unlocked then
			local b = T.button(card, "Travel", here and "Você está aqui" or "Viajar", bx, by, bw, 40, P.teal, function() ctx.travel("area", a.id) end)
			if here then T.setEnabled(b, false) end
		elseif isNext then
			local afford = d.moeda >= a.custo
			if not afford then
				T.progress(card, "Progress", bx, by - 22, bw, 14, d.moeda / a.custo, P.gold, { text = T.format(d.moeda) .. " / " .. T.format(a.custo), textSize = 11 })
			end
			local b = priceButton(card, "Unlock", "Desbloquear", a.custo, bx, by, bw, 40, afford and P.success or P.neutral, function() ctx.buyArea(a.id) end, afford,
				function() ctx.toast("Faltam " .. T.format(a.custo - d.moeda) .. " moedas para " .. a.nome, nil, "warning") end)
			if afford then T.shine(card, 2.2, .78) end
		else
			local prev = Config.areaPorId(a.id - 1)
			T.text(card, "Req", "Desbloqueie " .. (prev and prev.nome or "a ilha anterior") .. " antes", bx, by, bw, 40, 14, P.text2, T.CENTER, "body", 1.2)
		end
		local hit = T.new("TextButton", { Name = "Hover", Text = "", BackgroundTransparency = 1, Size = UDim2.new(1, 0, 1, -56), ZIndex = 1 }, card)
		hoverLift(hit, st, col, here and col or P.lineSoft)
		local sc = T.scaleOf(hit)
		hit.MouseEnter:Connect(function() T.tween(T.scaleOf(card), .14, { Scale = 1.02 }, Enum.EasingStyle.Quad) end)
		hit.MouseLeave:Connect(function() T.tween(T.scaleOf(card), .14, { Scale = 1 }, Enum.EasingStyle.Quad) end)
		sc.Scale = 1
	end
	y += math.ceil(#Config.Areas / cols) * (ch + gap)
	s.CanvasSize = UDim2.fromOffset(0, y + 4)
end

-- ================================================================ INVOCAR
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
		local lucky = ctx.data and (ctx.data.luckyMult or 1) > 1
		T.text(p, "Pity", ("Lendário+ garantido em %d giros   ·   Mítico+ em %d giros"):format(Config.PITY_LENDARIO - pity.l, Config.PITY_MITICO - pity.m), 0, 0, w, 22, 15, P.gold, T.CENTER, "title")
		if lucky then T.text(p, "Lucky", "Sorte ativa: chances de Épico+ aumentadas", 0, 24, w, 18, 13, P.success, T.CENTER, "body") end
		local y = 52
		for _, r in ipairs(rows) do
			local row = T.frame(p, "Rarity_" .. r.key, 0, y, w, 50, P.bg0, .25)
			T.corner(row, 10)
			T.text(row, "Gem", "◆", 10, 0, 22, 50, 18, r.def.cor, T.CENTER, "title")
			T.text(row, "Name", r.def.nome, 38, 4, w * .4, 24, 18, r.def.cor, T.LEFT, "title")
			local pets = Config.petsDaRaridade(r.key, id)
			local names = {}
			for _, pdef in ipairs(pets) do table.insert(names, pdef.nome) end
			T.text(row, "Pets", table.concat(names, ", "), 38, 26, w * .55, 18, 13, P.text2, T.LEFT, "body")
			T.text(row, "Chance", string.format("%.3f%%", r.pct), w - 150, 0, 138, 50, 20, P.text, T.RIGHT, "display")
			y += 56
		end
	end, 580, 110 + #rows * 56, { color = P.violet })
end

local function nearBanner(ctx, areaId)
	if ctx.nearBanner then return ctx.nearBanner(areaId) end
	return false
end

function M.summon(ctx, p, w, h)
	local d = ctx.data
	local id = ctx.bannerArea or 1
	if not Config.Gachas[id] then id = 1; ctx.bannerArea = 1 end
	local a = Config.areaPorId(id)
	local g = Config.Gachas[id]
	local col = areaColor(id)
	local unlocked = hasArea(ctx, id)
	local near = nearBanner(ctx, id)
	local narrow = w < 900
	local sideW = narrow and 0 or 256

	-- ===== lista de banners
	local banners = {}
	for _, area in ipairs(Config.Areas) do if Config.Gachas[area.id] then table.insert(banners, area) end end
	if narrow then
		local items = {}
		for _, area in ipairs(banners) do table.insert(items, { id = area.id, label = area.nome:gsub("Planeta ", ""):gsub("Monte ", ""), locked = not hasArea(ctx, area.id) }) end
		T.tabs(p, "Banners", 0, 0, w, 46, items, id, P.violet, function(nid) ctx.bannerArea = nid; ctx.refresh() end)
	else
		local side = T.frame(p, "Side", 0, 0, sideW, h, nil, 1)
		local y = T.section(side, "Banners", 0, 0, sideW, P.violet)
		for _, area in ipairs(banners) do
			local sel = area.id == id
			local ac = areaColor(area.id)
			local open = hasArea(ctx, area.id)
			local b = T.new("TextButton", { Name = "Banner_" .. area.id, Text = "", AutoButtonColor = false, BorderSizePixel = 0,
				BackgroundColor3 = sel and P.bg3 or P.bg2, Position = UDim2.fromOffset(0, y), Size = UDim2.fromOffset(sideW, 58) }, side)
			T.corner(b, 12)
			local st = T.stroke(b, sel and ac or P.lineSoft, sel and 2 or 1.5)
			local thumb = T.image(b, "Thumb", T.areaImage(area.id), 6, 6, 62, 46, open and WHITE or Color3.fromRGB(90, 92, 110))
			thumb.ScaleType = Enum.ScaleType.Crop
			T.corner(thumb, 8)
			T.text(b, "Name", area.nome, 78, 8, sideW - 110, 22, 16, sel and P.text or P.text2, T.LEFT, "title")
			T.text(b, "Cost", open and (T.format(Config.Gachas[area.id].custo) .. " por giro") or "Ilha bloqueada", 78, 30, sideW - 110, 18, 13, open and P.gold or P.text3, T.LEFT, "body")
			if not open then T.lock(b, sideW - 30, 18, 20, P.text3)
			elseif sel then T.text(b, "Sel", "›", sideW - 30, 0, 22, 58, 30, ac, T.CENTER, "title") end
			if sel then
				local bar = T.frame(b, "Bar", 0, 12, 4, 34, ac, 0)
				T.corner(bar, 2)
			else
				hoverLift(b, st, ac, P.lineSoft)
				b.Activated:Connect(function() T.som("ui_tab"); ctx.bannerArea = area.id; ctx.refresh() end)
			end
			y += 64
		end
		-- pity
		local pity = d.pity or { l = 0, m = 0 }
		local py = math.max(y + 6, h - 172)
		local pbox = T.panel(side, "Pity", 0, py, sideW, 172, { bg = P.bg2, radius = 14 })
		T.text(pbox, "Title", "GARANTIA (PITY)", 14, 10, sideW - 28, 20, 14, P.text, T.LEFT, "title")
		local lr, mr = T.rar("lendario"), T.rar("mitico")
		T.text(pbox, "LegLabel", "Lendário+", 14, 36, 120, 20, 14, lr.cor, T.LEFT, "title")
		T.text(pbox, "LegLeft", "em " .. (Config.PITY_LENDARIO - pity.l) .. " giros", sideW - 134, 36, 120, 20, 13, P.text2, T.RIGHT, "body")
		T.progress(pbox, "LegBar", 14, 60, sideW - 28, 14, pity.l / Config.PITY_LENDARIO, lr.cor)
		T.text(pbox, "MytLabel", "Mítico+", 14, 84, 120, 20, 14, mr.cor, T.LEFT, "title")
		T.text(pbox, "MytLeft", "em " .. (Config.PITY_MITICO - pity.m) .. " giros", sideW - 134, 84, 120, 20, 13, P.text2, T.RIGHT, "body")
		T.progress(pbox, "MytBar", 14, 108, sideW - 28, 14, pity.m / Config.PITY_MITICO, mr.cor)
		T.button(pbox, "Rates", "Ver chances", 14, 126, sideW - 28, 38, P.neutral, function() M.rates(ctx) end, { size = 15 })
	end

	-- ===== palco
	local sx = narrow and 0 or sideW + 16
	local sy = narrow and 58 or 0
	local stageW = w - sx
	local actionsH = 64
	local stageH = h - sy - actionsH - 12
	local stage = T.frame(p, "BannerStage", sx, sy, stageW, stageH, P.bg0, 0)
	T.corner(stage, 16)
	T.stroke(stage, col:Lerp(P.bg0, .4), 2)
	local scene = T.image(stage, "Scene", T.areaImage(id), 0, 0, stageW, stageH, Color3.fromRGB(120, 130, 165))
	scene.ScaleType = Enum.ScaleType.Crop
	T.corner(scene, 16)
	local shade = T.frame(stage, "Shade", 0, 0, stageW, stageH, P.bg0, 0)
	T.corner(shade, 16)
	T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, .2), T.kp(.35, .7), T.kp(.7, .45), T.kp(1, .05) }) }, shade)
	local tint = T.frame(stage, "Tint", 0, 0, stageW, stageH, col, 0)
	T.corner(tint, 16)
	T.fade(tint, 90, .88, 1)
	T.text(stage, "BannerName", a.nome, 20, 14, stageW - 300, 38, 32, WHITE, T.LEFT, "display", 1.8)
	T.text(stage, "BannerSub", "BANNER  ·  " .. T.format(g.custo) .. " MOEDAS POR GIRO", 22, 52, stageW - 300, 18, 13, col:Lerp(WHITE, .4), T.LEFT, "title", 1.2)
	local status, sw2 = T.chip(stage, "Near", near and "✓  NO BANNER" or "LONGE DO BANNER", 0, 22, 30, near and P.success or P.warning, { solid = near, size = 13 })
	status.Position = UDim2.fromOffset(stageW - sw2 - 18, 22)

	-- personagens em destaque (o mais raro no centro; Secreto não obtido aparece como silhueta)
	local all = {}
	for _, pd in ipairs(Config.Pets) do if pd.area == id then table.insert(all, pd) end end
	table.sort(all, function(x1, x2) return Config.Raridades[x1.raridade].ordem > Config.Raridades[x2.raridade].ordem end)
	local display = { all[2] or all[1], all[1], all[3] or all[1] }
	local heroTop = 84
	local plateH = 58
	local oddsH = narrow and 0 or 70
	local heroH = stageH - heroTop - plateH - oddsH - 20
	local unitW = stageW / 3
	for i, pd in ipairs(display) do
		if pd then
			local r = T.rar(pd.raridade)
			local center = i == 2
			local uh = center and heroH or heroH - 30
			local uy = heroTop + (center and 0 or 30)
			local unit = T.frame(stage, "Featured_" .. i, (i - 1) * unitW, uy, unitW, uh + plateH, nil, 1)
			local gsize = math.min(unitW, uh) * (center and .95 or .8)
			local glow = T.frame(unit, "Glow", (unitW - gsize) / 2, (uh - gsize) / 2 + 10, gsize, gsize, r.cor, 0)
			T.corner(glow, gsize / 2)
			T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, center and .72 or .8), T.kp(1, 1) }) }, glow)
			if center and r.ordem >= 6 and ctx.Notify and ctx.Notify.rays then
				local ray = ctx.Notify.rays(unit, unitW / 2, uh / 2 + 10, gsize * .75, r.cor, 10, .78)
				ray.ZIndex = 1
			end
			local owned = d.index and d.index.pets and d.index.pets[pd.id]
			local secretLocked = pd.raridade == "secreto" and not owned
			local art = T.preview(unit, "pet", pd.id, 0, 0, unitW, uh, true)
			if secretLocked and art:IsA("ImageLabel") then art.ImageColor3 = Color3.new(0, 0, 0) end
			local plate = T.frame(unit, "Plate", 16, uh, unitW - 32, plateH, P.bg0, .25)
			T.corner(plate, 12)
			T.stroke(plate, r.cor:Lerp(P.bg0, .3), 1.5)
			T.text(plate, "Name", secretLocked and "???" or pd.nome, 8, 4, unitW - 48, 26, center and 22 or 19, WHITE, T.CENTER, "display", 1.4)
			T.text(plate, "Rarity", T.upper(r.nome), 8, 30, unitW - 48, 20, 13, r.cor, T.CENTER, "title", 1.2)
			if center then
				local tag, tw = T.chip(unit, "Featured", "DESTAQUE", 0, 8, 24, P.gold, { solid = true, size = 12 })
				tag.Position = UDim2.fromOffset((unitW - tw) / 2, 0)
			end
		end
	end
	-- chances resumidas
	if not narrow then
		local odds = T.frame(stage, "Odds", 16, stageH - oddsH - 8, stageW - 32, oddsH, P.bg0, .3)
		T.corner(odds, 12)
		local rows = probabilities(ctx, id)
		local n = #rows
		local cw = (stageW - 32 - 20 - 120) / math.max(1, n)
		for i, r in ipairs(rows) do
			local cx = 12 + (i - 1) * cw
			T.text(odds, "Gem" .. i, "◆", cx, 12, 16, 22, 14, r.def.cor, T.CENTER, "title")
			T.text(odds, "Name" .. i, r.def.nome, cx + 18, 12, cw - 22, 22, 14, r.def.cor, T.LEFT, "title")
			T.text(odds, "Pct" .. i, (r.pct < 1 and string.format("%.2f%%", r.pct) or string.format("%.1f%%", r.pct)), cx + 2, 36, cw - 6, 22, 16, P.text, T.LEFT, "display")
		end
		T.button(odds, "Details", "Detalhes", stageW - 32 - 120, 14, 108, 42, P.neutral, function() M.rates(ctx) end, { size = 15 })
	end
	if not unlocked then
		local lockLayer = T.frame(stage, "Locked", 0, 0, stageW, stageH, P.bg0, .25)
		T.corner(lockLayer, 16)
		local box = T.panel(lockLayer, "Box", stageW / 2 - 190, stageH / 2 - 100, 380, 200, { bg = P.bg1, radius = 16, strokeColor = P.gold })
		T.lock(box, 170, 18, 40, P.gold)
		T.text(box, "Title", "Ilha bloqueada", 20, 66, 340, 32, 24, P.text, T.CENTER, "display")
		T.text(box, "Desc", "Desbloqueie " .. a.nome .. " para usar este banner.", 20, 98, 340, 22, 15, P.text2, T.CENTER, "body")
		priceButton(box, "BuyArea", "Desbloquear", a.custo, 30, 132, 320, 50, P.success, function() ctx.buyArea(id) end, true)
	end

	-- ===== ações
	local ay = h - actionsH
	local goW = narrow and 150 or 230
	local go = T.button(p, "GoBanner", near and "No banner ✓" or "Ir ao banner", sx, ay, goW, actionsH, near and P.neutral or P.teal, function()
		ctx.travel("gacha", id, true)
	end, { icon = "areas", size = 17 })
	if not near and unlocked then T.pop(go, 1.08, .5) end
	local space = (stageW - goW - 24) / 2
	if ctx.summonBusy then
		local prog = T.panel(p, "SummonProgress", sx + goW + 12, ay, stageW - goW - 12, actionsH, { bg = P.bg2, radius = 14, strokeColor = P.violet })
		local label = T.text(prog, "Label", "Invocando...", 18, 0, 260, actionsH, 20, P.text, T.LEFT, "display")
		local bar = T.progress(prog, "Bar", 290, (actionsH - 18) / 2, stageW - goW - 12 - 310, 18, 0, P.violet)
		ctx.onSummonProgress = function(i, n)
			if label.Parent then label.Text = "Invocando " .. i .. " / " .. n; T.setProgress(bar, i / n, P.violet, .3) end
		end
	else
		for i, n in ipairs({ 1, 10 }) do
			local free = n == 1 and d.giroGratis
			local cost = g.custo * (d.giroGratis and math.max(0, n - 1) or n)
			local afford = d.moeda >= cost
			local ok = unlocked and near and afford
			local b = priceButton(p, "Summon" .. n, n == 1 and "Invocar" or "Invocar x10", free and 0 or cost, sx + goW + 12 + (i - 1) * (space + 12), ay, space, actionsH, P.violet,
				function() ctx.startSummon(n) end, ok, function()
					if not unlocked then ctx.toast("Desbloqueie esta ilha primeiro", nil, "warning")
					elseif not near then ctx.toast("Viaje até o banner para invocar", nil, "info"); if go.Parent then T.shake(go, 6) end
					else ctx.toast("Faltam " .. T.format(cost - d.moeda) .. " moedas", nil, "warning") end
				end)
			if free and ok then T.shine(b.Face, 1.4, .7) end
		end
	end
end

-- ================================================================ FORJA
function M.forge(ctx, p, w, h)
	local d = ctx.data
	local narrow = w < 900
	local artW = narrow and w or math.floor(w * .36)
	local artH = narrow and 170 or h
	local art = T.frame(p, "Forge", 0, 0, artW, artH, P.bg0, 0)
	T.corner(art, 16)
	T.stroke(art, P.ember:Lerp(P.bg0, .4), 2)
	local scene = T.image(art, "Scene", T.Assets.lobby, 0, 0, artW, artH, Color3.fromRGB(120, 100, 95))
	scene.ScaleType = Enum.ScaleType.Crop
	T.corner(scene, 16)
	local shade = T.frame(art, "Shade", 0, 0, artW, artH, P.bg0, 0)
	T.corner(shade, 16)
	T.fade(shade, 90, .55, .05)
	local ember = T.frame(art, "Ember", 0, 0, artW, artH, P.ember, 0)
	T.corner(ember, 16)
	T.fade(ember, 90, 1, .7)
	if ctx.Notify and ctx.Notify.rays and not narrow then
		ctx.Notify.rays(art, artW / 2, artH * .38, artW * .55, P.ember, 10, .8)
	end
	local isz = narrow and 130 or math.min(230, artW - 60)
	T.icon(art, "forge", narrow and 20 or (artW - isz) / 2, narrow and 20 or artH * .38 - isz / 2, isz, isz)
	if narrow then
		T.text(art, "Ignis", "IGNIS", 170, 40, artW - 190, 50, 40, P.ember:Lerp(WHITE, .3), T.LEFT, "display", 2)
		T.text(art, "Role", "Mestre ferreiro  ·  compra seus minérios", 172, 92, artW - 190, 22, 15, P.text2, T.LEFT, "body", 1.2)
	else
		T.text(art, "Ignis", "IGNIS", 16, artH - 150, artW - 32, 60, 52, P.ember:Lerp(WHITE, .3), T.CENTER, "display", 2.2)
		T.text(art, "Role", "Mestre ferreiro  ·  compra seus minérios", 16, artH - 92, artW - 32, 22, 15, P.text2, T.CENTER, "body", 1.2)
		T.button(art, "UpgradeEquipment", "Equipamentos", 24, artH - 62, artW - 48, 46, P.neutral, function() ctx.storeTab = "Picaretas"; ctx.open("Store") end, { icon = "pickaxe", size = 16 })
	end

	local x = narrow and 0 or artW + 18
	local y0 = narrow and artH + 14 or 0
	local rw = w - x
	local rh = h - y0
	local frac = math.clamp((d.carregado or 0) / math.max(1, d.capacidade or 1), 0, 1)
	local top = T.section(p, "Sua mochila", x, y0, rw, P.ember, nil, T.format(d.carregado or 0) .. " / " .. T.format(d.capacidade or 0))
	T.progress(p, "Capacity", x, y0 + top, rw, 24, frac, frac >= 1 and P.danger or (frac >= .85 and P.warning or P.accent),
		{ text = math.floor(frac * 100 + .5) .. "% cheia", textSize = 13 })
	-- lista de minérios
	local rowsTop = y0 + top + 36
	local summaryH = 186
	local listH = rh - (rowsTop - y0) - summaryH - 12
	local list = T.scroll(p, "Ores", x, rowsTop, rw, listH, P.ember)
	local entries, raw = {}, 0
	for oid, q in pairs(d.mochila or {}) do
		local info = Config.infoMinerio(oid)
		if info and q > 0 then
			table.insert(entries, { info = info, q = q, v = info.valor * q })
			raw += info.valor * q
		end
	end
	table.sort(entries, function(a1, b1) return a1.v > b1.v end)
	if #entries == 0 then
		T.icon(list, "items", rw / 2 - 40, 10, 80, 80)
		T.text(list, "Empty", "Mochila vazia", 0, 92, rw - 14, 28, 20, P.text, T.CENTER, "title")
		T.text(list, "EmptyHint", "Quebre minérios nas ilhas para encher a mochila.", 0, 120, rw - 14, 22, 15, P.text2, T.CENTER, "body")
	end
	for i, e in ipairs(entries) do
		local r = T.rar(e.info.variante)
		local row = T.frame(list, "Ore_" .. i, 0, (i - 1) * 48, rw - 14, 42, P.bg2, 0)
		T.corner(row, 10)
		T.oreIcon(row, e.info.variante, 5, 3, 36, 36)
		T.text(row, "Name", e.info.nome, 46, 0, rw * .42, 42, 16, P.text, T.LEFT, "title")
		T.text(row, "Qty", "x" .. T.format(e.q), rw * .45, 0, 90, 42, 16, P.text2, T.LEFT, "title")
		T.icon(row, "coins", rw - 14 - 150, 7, 28, 28)
		T.text(row, "Value", T.format(e.v), rw - 14 - 118, 0, 104, 42, 17, P.gold, T.RIGHT, "display")
	end
	list.CanvasSize = UDim2.fromOffset(0, math.max(150, #entries * 48))
	-- resumo e venda
	local mult = d.multMoedas or 1
	local sy = h - summaryH
	local sum = T.panel(p, "Summary", x, sy, rw, summaryH, { bg = P.bg2, radius = 16, strokeColor = P.gold:Lerp(P.bg2, .5) })
	T.text(sum, "Label", "VALOR DE VENDA", 18, 12, 220, 22, 14, P.text2, T.LEFT, "title")
	T.icon(sum, "coins", 14, 36, 58, 58)
	T.text(sum, "Value", T.format(math.floor(raw * mult)), 78, 34, rw - 260, 60, 44, P.gold, T.LEFT, "display", 1.8)
	if mult > 1 then T.chip(sum, "Mult", string.format("x%.2f  VIP / boost / amigos", mult), rw - 250, 14, 28, P.success, { size = 13, w = 232 }) end
	local remote = d.passes and d.passes.AutoSell
	T.text(sum, "Access", remote and "✓ Auto Sell ativo: vende sozinho quando a mochila enche" or "Fora do lobby? Use o teleporte grátis até o Ignis.", 18, 96, rw - 36, 20, 14,
		remote and P.success or P.text3, T.LEFT, "body")
	local sell = T.button(sum, "SellAll", #entries > 0 and "Vender tudo" or "Nada para vender", 16, summaryH - 70, rw - 32, 58, P.success, function() ctx.invoke("Vender") end,
		{ icon = "coins", size = 22, sound = "ui_compra" })
	T.setEnabled(sell, #entries > 0)
	if #entries > 0 and frac >= .85 then T.shine(sell.Face, 1.6, .75) end
end

-- ================================================================ MISSÕES
local QUEST_ICON = { minerar = "pickaxe", epico = "shiny", chefe = "forge", invocar = "summon", vender = "coins" }

function M.progress(ctx, p, w, h)
	local d = ctx.data or {}
	local sel = ctx.questArea
	if not sel or not Config.areaPorId(sel) then
		sel = Players.LocalPlayer:GetAttribute("CurrentAreaId")
		if not sel or sel == 0 or not hasArea(ctx, sel) then
			sel = 1
			for _, a in ipairs(Config.Areas) do
				if hasArea(ctx, a.id) then
					for _, m in ipairs(Config.Missoes[a.id] or {}) do
						local e = d.missoes and d.missoes[m.id]
						if e and e.p >= m.meta and not e.r then sel = a.id; break end
					end
				end
			end
		end
	end
	ctx.questArea = sel
	local narrow = w < 880
	local sideW = narrow and 0 or 256
	if narrow then
		local items = {}
		for _, a in ipairs(Config.Areas) do table.insert(items, { id = a.id, label = tostring(a.id), locked = not hasArea(ctx, a.id) }) end
		T.tabs(p, "Islands", 0, 0, w, 44, items, sel, P.warning, function(id) ctx.questArea = id; ctx.refresh() end)
	else
		local y = T.section(p, "Ilhas", 0, 0, sideW, P.warning)
		for _, a in ipairs(Config.Areas) do
			local open = hasArea(ctx, a.id)
			local ready, done, total = 0, 0, 0
			for _, m in ipairs(Config.Missoes[a.id] or {}) do
				total += 1
				local e = d.missoes and d.missoes[m.id]
				if e and e.r then done += 1 elseif e and e.p >= m.meta then ready += 1 end
			end
			local isSel = a.id == sel
			local ac = areaColor(a.id)
			local b = T.new("TextButton", { Name = "QuestArea_" .. a.id, Text = "", AutoButtonColor = false, BorderSizePixel = 0,
				BackgroundColor3 = isSel and P.bg3 or P.bg2, Position = UDim2.fromOffset(0, y), Size = UDim2.fromOffset(sideW, 62) }, p)
			T.corner(b, 12)
			local st = T.stroke(b, isSel and ac or P.lineSoft, isSel and 2 or 1.5)
			T.text(b, "Pip", "◆", 10, 0, 20, 40, 16, open and ac or P.text3, T.CENTER, "title")
			T.text(b, "Name", a.nome, 34, 6, sideW - 70, 26, 16, open and P.text or P.text3, T.LEFT, "title")
			if open then
				T.progress(b, "Bar", 34, 38, sideW - 110, 10, done / math.max(1, total), ac)
				T.text(b, "Count", done .. "/" .. total, sideW - 70, 30, 56, 26, 13, P.text2, T.RIGHT, "title")
			else
				T.text(b, "Locked", "Bloqueada", 34, 32, sideW - 70, 20, 13, P.text3, T.LEFT, "body")
				T.lock(b, sideW - 32, 20, 20, P.text3)
			end
			if ready > 0 then
				local badge = T.badge(b, sideW - 20, -6, ready, P.success)
				T.pop(badge, 1.2, .3)
			end
			if isSel then
				local bar = T.frame(b, "Bar2", 0, 14, 4, 34, ac, 0)
				T.corner(bar, 2)
			else
				hoverLift(b, st, ac, P.lineSoft)
				b.Activated:Connect(function() T.som("ui_tab"); ctx.questArea = a.id; ctx.refresh() end)
			end
			y += 68
		end
	end

	local area = Config.areaPorId(sel)
	local unlocked = hasArea(ctx, sel)
	local x = narrow and 0 or sideW + 18
	local y0 = narrow and 56 or 0
	local rw = w - x
	local head = T.frame(p, "AreaHead", x, y0, rw, 56, nil, 1)
	T.text(head, "Name", area.nome, 0, 0, rw - 260, 34, 28, P.text, T.LEFT, "display")
	T.text(head, "Hint", "Missões desta ilha  ·  as recompensas são em moedas", 2, 34, rw - 260, 18, 13, P.text2, T.LEFT, "body")
	local list = {}
	local readyIds = {}
	for idx, m in ipairs(Config.Missoes[sel] or {}) do
		local e = d.missoes and d.missoes[m.id] or { p = 0, r = false }
		local state = e.r and 3 or (e.p >= m.meta and 1 or 2)
		if state == 1 then table.insert(readyIds, m.id) end
		table.insert(list, { m = m, e = e, state = state, idx = idx })
	end
	table.sort(list, function(q1, q2) if q1.state ~= q2.state then return q1.state < q2.state end return q1.idx < q2.idx end)
	if unlocked and #readyIds > 0 then
		T.button(head, "ClaimAll", "Resgatar todas (" .. #readyIds .. ")", rw - 240, 4, 240, 48, P.success, function()
			task.spawn(function()
				for _, qid in ipairs(readyIds) do ctx.invoke("ResgatarMissao", qid) end
				ctx.coinBurst(1000)
				ctx.refresh()
			end)
		end, { sound = "ui_compra" })
	end
	local s = T.scroll(p, "Quests", x, y0 + 66, rw, h - y0 - 66, P.warning)
	if not unlocked then
		local box = T.panel(s, "Locked", (rw - 14) / 2 - 220, 30, 440, 220, { bg = P.bg2, radius = 16, strokeColor = P.gold })
		T.lock(box, 196, 20, 48, P.gold)
		T.text(box, "Title", "Ilha bloqueada", 20, 80, 400, 32, 24, P.text, T.CENTER, "display")
		T.text(box, "Desc", "Desbloqueie a ilha para liberar as missões.", 20, 112, 400, 22, 15, P.text2, T.CENTER, "body")
		priceButton(box, "Buy", "Desbloquear", area.custo, 40, 148, 360, 52, P.success, function() ctx.buyArea(sel) end, true)
		s.CanvasSize = UDim2.fromOffset(0, 280)
		return
	end
	local cw = rw - 14
	local y = 0
	for _, q in ipairs(list) do
		local m, e, state = q.m, q.e, q.state
		local col = state == 3 and P.text3 or (state == 1 and P.success or P.warning)
		local card = T.panel(s, "Quest_" .. m.id, 0, y, cw, 96, { bg = state == 3 and P.bg1 or P.bg2, radius = 14, strokeColor = state == 1 and P.success or P.lineSoft })
		local ib = T.frame(card, "IconBack", 14, 14, 68, 68, P.bg0, 0)
		T.corner(ib, 14)
		local glow = T.frame(ib, "Glow", 0, 0, 68, 68, col, 0)
		T.corner(glow, 14)
		T.fade(glow, 90, 1, .65)
		T.icon(ib, QUEST_ICON[m.tipo] or "quests", 6, 6, 56, 56)
		T.text(card, "Title", m.texto, 96, 14, cw - 96 - 300, 26, 19, state == 3 and P.text3 or P.text, T.LEFT, "title")
		local frac = math.clamp(e.p / m.meta, 0, 1)
		T.progress(card, "Track", 96, 52, cw - 96 - 300, 22, frac, col, { text = T.format(math.min(e.p, m.meta)) .. " / " .. T.format(m.meta), textSize = 13 })
		local rx = cw - 286
		T.text(card, "RewardLabel", "RECOMPENSA", rx, 12, 130, 18, 12, P.text3, T.LEFT, "title")
		T.icon(card, "coins", rx - 4, 32, 36, 36)
		T.text(card, "Reward", T.format(m.premio), rx + 34, 30, 100, 40, 22, P.gold, T.LEFT, "display", 1.3)
		if state == 3 then
			T.chip(card, "Claimed", "✓  RESGATADA", cw - 150, 32, 32, P.teal, { size = 13, w = 136 })
		else
			local b = T.button(card, "Claim", state == 1 and "Resgatar" or "Em andamento", cw - 150, 24, 136, 48, state == 1 and P.success or P.neutral, function()
				local res = ctx.invoke("ResgatarMissao", m.id)
				if res and res.ok then ctx.coinBurst(m.premio); ctx.refresh() end
			end, { sound = "ui_compra", size = 16 })
			if state ~= 1 then T.setEnabled(b, false) else T.shine(b.Face, 1.8, .75) end
		end
		y += 106
	end
	s.CanvasSize = UDim2.fromOffset(0, y)
end

-- ================================================================ CONFIGURAÇÕES
function M.settings(ctx, p, w, h)
	local narrow = w < 860
	local colW = narrow and w or (w - 18) / 2
	local left = T.frame(p, "Preferences", 0, 0, colW, narrow and 600 or h, nil, 1)
	local y = T.section(left, "Preferências", 0, 0, colW, T.Page.Settings)
	local defs = {
		{ "MusicEnabled", "Música das ilhas", "Trilha sonora do ambiente" },
		{ "LobbyVFXEnabled", "Efeitos do ambiente", "Partículas e efeitos do cenário" },
		{ "SomMineracaoEnabled", "Sons de mineração", "Golpes, quebras e coleta" },
		{ "SomInterfaceEnabled", "Sons da interface", "Cliques, abas e janelas" },
		{ "ExpeditionBlurEnabled", "Desfoque de fundo", "Ao abrir menus" },
	}
	local rowH = h < 640 and 60 or 66
	for _, def in ipairs(defs) do
		local row = T.panel(left, "Row_" .. def[1], 0, y, colW, rowH, { bg = P.bg2, radius = 14 })
		T.text(row, "Name", def[2], 18, rowH / 2 - 22, colW - 120, 24, 18, P.text, T.LEFT, "title")
		T.text(row, "Desc", def[3], 18, rowH / 2 + 2, colW - 120, 20, 14, P.text2, T.LEFT, "body")
		local on = Players.LocalPlayer:GetAttribute(def[1]) ~= false
		T.toggle(row, "Toggle_" .. def[1], colW - 84, (rowH - 36) / 2, on, function(state) Players.LocalPlayer:SetAttribute(def[1], state) end)
		y += rowH + 8
	end
	y += 8
	y += T.section(left, "Atalhos", 0, y, colW, T.Page.Settings)
	local keys = { { "H", "Unidades" }, { "J", "Itens" }, { "G", "Invocar" }, { "T", "Hold Mode (minerar arrastando)" } }
	for i, k in ipairs(keys) do
		local ky = y + (i - 1) * 38
		local cap = T.frame(left, "Key_" .. k[1], 0, ky, 34, 30, P.bg3, 0)
		T.corner(cap, 8)
		T.stroke(cap, P.line, 1.5)
		T.text(cap, "K", k[1], 0, 0, 34, 28, 15, P.text, T.CENTER, "title")
		T.text(left, "KeyDesc_" .. k[1], k[2], 46, ky, colW - 46, 30, 15, P.text2, T.LEFT, "body")
	end

	local rx = narrow and 0 or colW + 18
	local ry = narrow and 610 or 0
	local right = T.frame(p, "Codes", rx, ry, colW, 260, nil, 1)
	local cy = T.section(right, "Códigos", 0, 0, colW, P.gold)
	local card = T.panel(right, "CodeCard", 0, cy, colW, 200, { bg = P.bg2, radius = 16, strokeColor = P.gold:Lerp(P.bg2, .5) })
	T.icon(card, "gift", 16, 16, 64, 64)
	T.text(card, "Title", "Resgatar código", 92, 18, colW - 110, 28, 22, P.text, T.LEFT, "display")
	T.text(card, "Hint", "Siga as redes do jogo para novos códigos.", 92, 48, colW - 110, 20, 14, P.text2, T.LEFT, "body")
	local box = T.input(card, "CodeBox", 16, 98, colW - 32, 48, "DIGITE O CÓDIGO", "", { size = 18 })
	local busy = false
	T.button(card, "RedeemCode", "Resgatar", 16, 150, colW - 32, 44, P.success, function()
		if busy or box.Text == "" then return end
		busy = true
		local res = ctx.invoke("ResgatarCodigo", box.Text)
		if res and res.ok then box.Text = ""; ctx.coinBurst(500) end
		busy = false
	end, { sound = "ui_compra" })
end

-- ================================================================ DIÁRIO / INDEX
local DAILY_ICON = { moedas = "coins", boost = "potion", pet = "units", hats = "items" }

local function showcasePet(d)
	local best
	for _, inst in pairs(d.petsInv or {}) do
		local def = Config.petPorId(inst.id)
		if def and (not best or T.rar(def.raridade).ordem > T.rar(best.raridade).ordem) then best = def end
	end
	if best then return best end
	local list = Config.petsDaRaridade("lendario", 1)
	return list[1] or Config.Pets[1]
end

local REWARD_RARITY = { moedas = "lendario", boost = "epico", pet = "mitico", hats = "raro" }

local function daily(ctx, p, w, h)
	local d = ctx.data or {}
	local info = d.daily or { dia = 1, disponivel = false }
	local secs = 86400 - (os.time() % 86400)
	local narrow = w < 940
	local heroW = narrow and w or math.min(400, math.floor(w * .32))
	local heroH = narrow and 190 or h

	-- ===== painel de destaque
	local hero = T.frame(p, "Hero", 0, 0, heroW, heroH, P.bg2, 0)
	T.corner(hero, 18)
	T.stroke(hero, P.pink:Lerp(P.bg2, .35), 2.5)
	T.texture(hero, "pattern", .9, P.pink:Lerp(WHITE, .2), 120)
	local glow = T.frame(hero, "Glow", 0, 0, heroW, heroH, P.pink, 0)
	T.corner(glow, 18)
	T.fade(glow, 90, 1, .62)
	T.sparkles(hero, heroW, heroH, 8, WHITE)
	if narrow then
		T.text(hero, "T1", "RECOMPENSA DIÁRIA", 20, 14, heroW - 40, 40, 32, WHITE, T.LEFT, "display")
	else
		T.text(hero, "T1", "RECOMPENSA", 20, 16, heroW - 40, 42, 36, WHITE, T.LEFT, "display")
		T.text(hero, "T2", "DIÁRIA", 20, 56, heroW - 40, 46, 42, P.pink:Lerp(WHITE, .35), T.LEFT, "display")
	end
	-- de baixo para cima: botão → sequência + tempo (mesma linha) → regra → personagem ocupa o resto
	local chipY = narrow and 64 or (heroH - 74 - 46)
	local ruleY = heroH - 74 - 46 - 44
	local pet = showcasePet(d)
	if pet and not narrow then
		T.preview(hero, "pet", pet.id, 30, 110, heroW - 60, math.max(100, ruleY - 116), true)
	elseif pet then
		T.preview(hero, "pet", pet.id, heroW - 170, -10, 160, heroH + 20, true)
	end
	local _, streakW = T.chip(hero, "Streak", "DIA " .. info.dia .. " DE " .. #Config.DAILY, 20, chipY, 32, P.pink, { solid = true, size = 15 })
	T.text(hero, "Next", info.disponivel and "Disponível agora!" or ("Próxima em " .. T.clock(secs)), 20 + streakW + 12, chipY, heroW - 52 - streakW, 32, 16,
		info.disponivel and P.success or P.text2, T.LEFT, "title")
	local claim = T.button(hero, "Claim", info.disponivel and ("Resgatar dia " .. info.dia) or "Volte amanhã", 20, heroH - 74, heroW - 40, 58, P.success, function()
		if not info.disponivel then return end
		local res = ctx.invoke("ResgatarDaily")
		if res and res.ok then
			ctx.Notify.banner({ title = "DIA " .. info.dia .. " RESGATADO!", subtitle = Config.DAILY[info.dia] and Config.DAILY[info.dia].texto or "", color = P.pink, sound = false })
			ctx.coinBurst(1000)
			ctx.refresh()
		end
	end, { icon = "gift", size = 20, sound = "ui_compra" })
	T.setEnabled(claim, info.disponivel)
	if info.disponivel then T.shine(claim.Face, 1.5, .8) end

	-- ===== cartas dos dias
	local gx = narrow and 0 or heroW + 16
	local gy = narrow and heroH + 14 or 0
	local gw, gh = w - gx, h - gy
	local n = #Config.DAILY
	local cols = gw >= 720 and 4 or (gw >= 520 and 3 or 2)
	local gap = 12
	local cw = (gw - (cols - 1) * gap) / cols
	local rows = math.ceil(n / cols)
	local ch = math.min(262, (gh - (rows - 1) * gap) / rows)
	local artS = math.clamp(math.floor(ch - 150), 52, 96)
	for i, def in ipairs(Config.DAILY) do
		local x = gx + ((i - 1) % cols) * (cw + gap)
		local y = gy + math.floor((i - 1) / cols) * (ch + gap)
		local claimed = i < info.dia
		local today = i == info.dia
		local last = i == n
		local col = today and (info.disponivel and P.success or P.gold) or (claimed and P.text3 or (last and P.gold or P.violet))
		local card = T.frame(p, "Dia" .. i, x, y, cw, ch, col:Lerp(P.ink, .78), 0)
		T.corner(card, 14)
		T.texture(card, "pattern", .88, col:Lerp(WHITE, .2), 90)
		local cg = T.frame(card, "Glow", 0, 0, cw, ch, col, 0)
		T.corner(cg, 14)
		T.new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.55, .9), T.kp(1, today and .45 or .7) }) }, cg)
		local st = T.stroke(card, col, today and 3.5 or 2.5)
		T.new("UIGradient", { Rotation = 90, Color = ColorSequence.new(col:Lerp(WHITE, .4), col:Lerp(P.ink, .2)) }, st)
		-- numeral grande + listras
		T.text(card, "Num", string.format("%02d", i), 12, 6, 76, 48, 44, WHITE, T.LEFT, "display")
		if not today then T.text(card, "DayLabel", "DIA", 88, 16, 44, 22, 15, col:Lerp(WHITE, .5), T.LEFT, "title") end
		T.stripes(card, "Hazard", 12, 56, cw - 24, 7, col:Lerp(WHITE, .3), .92)
		-- item
		local kind = def.itens and def.itens[1] and def.itens[1].tipo or "moedas"
		local art = T.tile(card, "Art", (cw - artS) / 2, 72, artS, artS, REWARD_RARITY[kind] or "raro", { radius = 12, animated = last })
		T.icon(art, DAILY_ICON[kind] or "gift", artS * .12, artS * .12, artS * .76, artS * .76)
		local rewardY = 72 + artS + 8
		if not claimed then
			T.para(card, "Reward", def.texto, 10, rewardY, cw - 20, ch - rewardY - (last and 36 or 10), 16, today and P.text or P.text2, T.CENTER)
		end
		if last then
			local tag, tw2 = T.chip(card, "Big", "GRANDE RECOMPENSA", 0, ch - 30, 24, P.gold, { solid = true, size = 11 })
			tag.Position = UDim2.fromOffset((cw - tw2) / 2, ch - 30)
		end
		if claimed then
			local veil = T.frame(card, "Done", 0, 0, cw, ch, P.ink, .5)
			T.corner(veil, 14)
			local dot = T.frame(veil, "Dot", cw / 2 - 26, ch / 2 - 26, 52, 52, P.teal, 0)
			T.corner(dot, 26)
			T.stroke(dot, P.ink, 3)
			T.text(dot, "Check", "✓", 0, 0, 52, 52, 30, WHITE, T.CENTER, "heavy")
			T.text(veil, "Label", "RESGATADO", 0, ch / 2 + 30, cw, 24, 14, P.teal, T.CENTER, "title")
		elseif today then
			local tag, tw2 = T.chip(card, "Today", info.disponivel and "HOJE" or "AMANHÃ", 0, 6, 24, col, { solid = true, size = 12 })
			tag.Position = UDim2.fromOffset(cw - tw2 - 10, 8)
			if info.disponivel then T.shine(card, 1.6, .75) end
		end
	end
	-- regra do ciclo: dentro do painel de destaque, logo acima do botao
	if not narrow then
		local rule = T.para(hero, "Rule", "Faltar um dia não tira nada: o ciclo só avança quando você resgata.", 20, heroH - 74 - 46 - 44, heroW - 40, 38, 14, P.text2, T.CENTER)
		rule.TextYAlignment = Enum.TextYAlignment.Bottom
	end
end

local function index(ctx, p, w, h)
	local d = ctx.data or {}
	local idx = d.index or { pets = {}, hats = {} }
	local np, nh = 0, 0
	for _ in pairs(idx.pets or {}) do np += 1 end
	for _ in pairs(idx.hats or {}) do nh += 1 end
	local s = T.scroll(p, "Index", 0, 0, w, h, P.pink)
	local cw0 = w - 14
	local total = T.panel(s, "Total", 0, 0, cw0, 110, { bg = P.bg2, radius = 16, strokeColor = P.gold:Lerp(P.bg2, .5) })
	T.icon(total, "units", 14, 15, 80, 80)
	T.text(total, "Title", "Coleção", 108, 14, 300, 34, 28, P.text, T.LEFT, "display")
	local pct = (np + nh) / math.max(1, #Config.Pets + #Config.Hats)
	T.text(total, "Pct", math.floor(pct * 100 + .5) .. "% completa", 108, 48, 300, 20, 15, P.gold, T.LEFT, "title")
	local bw = (cw0 - 108 - 40) / 2
	T.text(total, "PetsLabel", "UNIDADES  " .. np .. " / " .. #Config.Pets, 108, 72, bw, 18, 12, P.text2, T.LEFT, "title")
	T.progress(total, "PetsBar", 108, 90, bw, 10, np / math.max(1, #Config.Pets), P.accent)
	T.text(total, "HatsLabel", "HATS  " .. nh .. " / " .. #Config.Hats, 108 + bw + 20, 72, bw, 18, 12, P.text2, T.LEFT, "title")
	T.progress(total, "HatsBar", 108 + bw + 20, 90, bw, 10, nh / math.max(1, #Config.Hats), P.info)
	local y = 124 + T.section(s, "Por ilha", 0, 124, cw0, P.pink)
	for _, a in ipairs(Config.Areas) do
		local tp, op, th, oh = 0, 0, 0, 0
		for _, pet in ipairs(Config.Pets) do if pet.area == a.id then tp += 1; if idx.pets[pet.id] then op += 1 end end end
		for _, hat in ipairs(Config.Hats) do if hat.mundo == a.id then th += 1; if idx.hats[hat.id] then oh += 1 end end end
		local ac = areaColor(a.id)
		local row = T.panel(s, "IndexArea" .. a.id, 0, y, cw0, 64, { bg = P.bg2, radius = 12, strokeColor = ac:Lerp(P.bg2, .6) })
		local thumb = T.image(row, "Thumb", T.areaImage(a.id), 6, 6, 92, 52)
		thumb.ScaleType = Enum.ScaleType.Crop
		T.corner(thumb, 9)
		T.stroke(thumb, ac, 2)
		T.text(row, "Name", a.nome, 112, 0, cw0 * .32 - 118, 64, 17, P.text, T.LEFT, "title")
		local colX = cw0 * .32
		local barW = (cw0 - colX - 40) / 2
		T.text(row, "Pets", tp > 0 and ("Unidades " .. op .. "/" .. tp) or "Sem unidades", colX, 10, barW, 20, 13, tp > 0 and P.text2 or P.text3, T.LEFT, "title")
		if tp > 0 then T.progress(row, "PetBar", colX, 36, barW, 12, op / tp, P.accent) end
		T.text(row, "Hats", "Hats " .. oh .. "/" .. th, colX + barW + 20, 10, barW, 20, 13, P.text2, T.LEFT, "title")
		T.progress(row, "HatBar", colX + barW + 20, 36, barW, 12, oh / math.max(1, th), P.info)
		if (op == tp) and (oh == th) and th > 0 then T.chip(row, "Complete", "✓ COMPLETA", cw0 - 130, 18, 28, P.gold, { size = 12, w = 116 }) end
		y += 72
	end
	s.CanvasSize = UDim2.fromOffset(0, y)
end

function M.daily(ctx, p, w, h)
	if ctx.eventsTab == "Index" then index(ctx, p, w, h) else daily(ctx, p, w, h) end
end

function M.render(ctx, p, w, h)
	if ctx.page == "Store" then M.store(ctx, p, w, h)
	elseif ctx.page == "Areas" or ctx.page == "Play" then M.areas(ctx, p, w, h)
	elseif ctx.page == "Summon" then M.summon(ctx, p, w, h)
	elseif ctx.page == "Forge" then M.forge(ctx, p, w, h)
	elseif ctx.page == "Settings" then M.settings(ctx, p, w, h)
	elseif ctx.page == "Events" then M.daily(ctx, p, w, h)
	else M.progress(ctx, p, w, h) end
end

return M

