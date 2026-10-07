-- ============================================================================
-- EXPEDITION CLIENT · UI V3
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
local AudioPreferences = require(RS:WaitForChild("AudioPreferences"))
local modules = RS:WaitForChild("ExpeditionUI")
local T = require(modules.Theme)
local Notify = require(modules.Notify)
local Inventory = require(modules.Inventory)
player:WaitForChild("PlayerGui").ScreenOrientation=Enum.ScreenOrientation.LandscapeSensor
local Menus = require(modules.Menus)
local P, C = T.P, T.C
local WHITE = Color3.new(1, 1, 1)

local BASE_W, BASE_H = 1440, 850
local GuiService=game:GetService("GuiService")
local function usingGamepad() return Input:GetLastInputType().Name:find("Gamepad")~=nil end
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
local popupState=nil
local pendingOffer=nil
local alive=true
local connections={}
local function connect(signal,fn) local c=signal:Connect(fn);table.insert(connections,c);return c end
screen:SetAttribute("OpenPage","")
screen:SetAttribute("PopupOpen",false)
ctx.T, ctx.Notify = T, Notify

-- Apply locally at once; coalesce rapid +/- presses into a small profile patch.
-- Only the audio whitelist is persisted. Other visual preferences remain session-local.
local pendingAudio, failedAudio, audioWorker = {}, {}, false
local audioHydrated = false
ctx.audioSaveStatus = "loading"
for key, default in pairs(AudioPreferences.defaults) do
	if AudioPreferences.value(key, player:GetAttribute(key)) == nil then player:SetAttribute(key, default) end
end
local function audioStatus(status)
	ctx.audioSaveStatus = status
	if ctx.audioSettingsStatus then ctx.audioSettingsStatus() end
end
function ctx.setAudioPreference(key, value)
	value = AudioPreferences.value(key, value)
	if value == nil then return end
	player:SetAttribute(key, value)
	for failedKey, failedValue in pairs(failedAudio) do
		if pendingAudio[failedKey] == nil then pendingAudio[failedKey] = failedValue end
	end
	failedAudio = {}
	pendingAudio[key] = value
	audioStatus("pending")
	if audioWorker then return end
	audioWorker = true
	task.spawn(function()
		task.wait(.35)
		while alive and next(pendingAudio) do
			local patch = pendingAudio
			pendingAudio = {}
			local remote = R:FindFirstChild("AtualizarAudioProfile") or R:WaitForChild("AtualizarAudioProfile", 5)
			local ok, result = false, nil
			for attempt = 1, 3 do
				if remote and remote:IsA("RemoteFunction") then
					ok, result = pcall(function() return remote:InvokeServer(patch) end)
				end
				if ok and type(result) == "table" and result.ok then break end
				if attempt < 3 then task.wait(.6) end
			end
			if not alive then break end
			if ok and type(result) == "table" and result.ok then
				local confirmed = AudioPreferences.sanitize(result.audio)
				for key, value in pairs(confirmed) do
					-- A response for an older press must not roll back newer local input.
					if pendingAudio[key] == nil then player:SetAttribute(key, value) end
				end
				ctx.audioPersistent = result.persistent == true
				audioStatus(next(pendingAudio) and "pending" or (ctx.audioPersistent and "profile" or "session"))
			else
				-- Retain failed fields for the next deliberate edit, without a retry loop.
				for key, value in pairs(patch) do
					if pendingAudio[key] == nil then failedAudio[key] = value end
				end
				if next(pendingAudio) then
					for key, value in pairs(failedAudio) do
						if pendingAudio[key] == nil then pendingAudio[key] = value end
					end
					failedAudio = {}
				end
				audioStatus("error")
			end
			task.wait(.35)
		end
		audioWorker = false
	end)
end

T.setTooltipLayer(tipLayer, function() return scale.Scale end)
-- com uma janela aberta o HUD fica atrás do fundo escuro: nada de dica dele aparecendo por cima
T.setTooltipGuard(function(o) return not (ctx.page and o:IsDescendantOf(hud)) end)
Notify.init(toastLayer, popupLayer, function() return virtualW, virtualH end)
Notify.feedAnchor = function() return virtualW - 24, virtualH - (ctx.portrait and 272 or 128) end

-- ---------------------------------------------------------------- PÁGINAS
local PAGE = {
	Store = { title = "Loja", icon = "store", color = P.gold, sub = "Passes, boosts e pacotes" },
 Equipment = {title="Equipamentos",icon="pickaxe",color=P.ember,sub="Picaretas e mochilas · Ignis"},
	Inventory = { title = "Inventário", icon = "units", color = P.accent },
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
	popupState = nil
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

-- A resize renders the same builder/closure again. Stateful selection stays in that
-- closure; text, scroll and focus survive by their stable component names.
local function renderPopup(state, reflow)
	local saved, selectedName = {}, nil
	if state.box and state.box.Parent then
		local selected = GuiService.SelectedObject
		if selected and selected:IsDescendantOf(state.box) then selectedName = selected.Name end
		for _, object in ipairs(state.box:GetDescendants()) do
			if object:IsA("TextBox") then
				table.insert(saved, { name = object.Name, class = "TextBox", text = object.Text,
					focused = object:IsFocused(), cursor = object.CursorPosition, selection = object.SelectionStart })
			elseif object:IsA("ScrollingFrame") then
				table.insert(saved, { name = object.Name, class = "ScrollingFrame", position = object.CanvasPosition })
			end
		end
		state.box:Destroy()
	end
	if state.shield then state.shield:Destroy() end
 if state.shadow then state.shadow:Destroy() end
	T.hideTooltip()
	local opts = state.opts
	local w = math.min(state.width, virtualW - 32)
	local h = math.min(state.height, virtualH - 40)
	local shield = T.new("TextButton", { Name = "PopupBackdrop", Text = "", AutoButtonColor = false, BorderSizePixel = 0,
		BackgroundColor3 = P.bg0, BackgroundTransparency = reflow and .35 or 1, Size = UDim2.fromScale(1, 1) }, dialogHost)
	state.shield = shield
	if not reflow then T.tween(shield, .16, { BackgroundTransparency = .35 }, Enum.EasingStyle.Quad) end
	shield.Activated:Connect(function() if not opts.modal then closePopup() end end)
	local box = T.panel(dialogHost, "Popup", (virtualW - w) / 2, (virtualH - h) / 2, w, h, { bg = P.bg1, radius = 16, strokeColor = P.line, shade = false })
	state.box = box
	box.Active = true
	local shadow = T.shadow(box, 16, 10, .4)
 state.shadow=shadow
	local accent = opts.color or P.accent
	local ornament=T.frame(box,"TitleOrnament",18,10,math.min(w-96,360),44,nil,1)
	T.headerOrnament(ornament,math.min(w-96,360),44,accent)
	local line = T.frame(box, "Accent", 18, 0, w - 36, 3, accent, 0)
	T.new("UIGradient", { Transparency = NumberSequence.new({ T.kp(0, 1), T.kp(.5, 0), T.kp(1, 1) }) }, line)
	local closeSize = math.max(44, math.ceil(44 / scale.Scale))
	T.text(box, "Title", state.title, 22, 14, w - closeSize - 44, 36, 24, P.text, T.LEFT, "display")
	T.closeButton(box, w - closeSize - 12, 8, closeSize, closePopup)
	local area = T.frame(box, "Content", 20, 64, w - 40, h - 84, nil, 1)
	state.builder(area, w - 40, h - 84, reflow == true)
	for _, value in ipairs(saved) do
		local object = area:FindFirstChild(value.name, true)
		if object and object:IsA(value.class) and value.class == "TextBox" then object.Text = value.text end
	end
	task.defer(function()
		if popupState ~= state or state.box ~= box or not box.Parent then return end
		for _, value in ipairs(saved) do
			local object = area:FindFirstChild(value.name, true)
			if object and object:IsA(value.class) then
				if value.class == "ScrollingFrame" then object.CanvasPosition = value.position
				elseif value.focused then
					object:CaptureFocus(); object.CursorPosition = value.cursor; object.SelectionStart = value.selection
				end
			end
		end
		if usingGamepad() then
			local selected = selectedName and box:FindFirstChild(selectedName, true)
			GuiService.SelectedObject = selected and selected:IsA("GuiButton") and selected or box:FindFirstChildWhichIsA("GuiButton", true)
		end
	end)
	if not reflow then
		T.enter(box, .97, .18)
		T.enter(shadow, .97, .18)
		T.som("ui_popup")
	end
	return box
end

function ctx.popup(title, builder, w, h, opts)
	opts = opts or {}
	closePopup()
	popupOpen = true
	screen:SetAttribute("PopupOpen", true)
	popupOnClose = opts.onClose
	popupFocus = GuiService.SelectedObject
	popupState = { title = title, builder = builder, width = w or 560, height = h or 420, opts = opts }
	return renderPopup(popupState, false)
end

function ctx.refreshPopup()
	if popupOpen and popupState then renderPopup(popupState, true) end
end

-- confirmação. opts: confirmText, cancelText, tone, cost (moedas), preview(p,w) + previewH, w, h
function ctx.confirm(title, message, callback, opts)
	opts = opts or {}
	local hasCost = opts.cost ~= nil
	local used = false
	ctx.popup(title, function(p, w, h)
		local detailHeight = (opts.preview and (opts.previewH or 0) + 10 or 0) + 80 + (hasCost and 94 or 0)
		local details = T.scroll(p, "ConfirmationDetails", 0, 0, w, h - 66, opts.tone or P.accent)
		local cw = w - 14
		local y = 0
		if opts.preview then opts.preview(details, cw); y = (opts.previewH or 0) + 10 end
		T.para(details, "Prompt", message, 0, y, cw, 64, 18, P.text2, T.CENTER, "body")
		y += 80
		if hasCost then
			local have = ctx.data and ctx.data.moeda or 0
			local row = T.panel(details, "CostRow", 0, y, cw, 58, { bg = P.bg0, radius = 12 })
			T.text(row, "CostLabel", "PREÇO", 16, 0, 120, 58, 14, P.text2, T.LEFT, "title")
			T.icon(row, "coins", cw - 196, 9, 40, 40)
			T.text(row, "Cost", T.format(opts.cost), cw - 152, 0, 136, 58, 26, P.gold, T.RIGHT, "display", 1.4)
			T.text(details, "After", have >= opts.cost and ("Saldo depois da compra: " .. T.format(have - opts.cost)) or ("Faltam " .. T.format(opts.cost - have) .. " moedas"),
				0, y + 64, cw, 24, 14, have >= opts.cost and P.text3 or P.danger, T.CENTER, "body")
		end
		details.CanvasSize = UDim2.fromOffset(0, detailHeight)
		local bw = (w - 12) / 2
		T.button(p, "Cancel", opts.cancelText or "Cancelar", 0, h - 52, bw, 52, P.neutral, closePopup, { sound = "ui_cancel" })
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
				-- Visual particles do not emit extra coins: the confirmed reward owns its audio.
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
		Som.tocar(res.upgradeMax and "upgrade_max" or "upgrade")
		local def = name == "ComprarPicareta" and Config.picaretaPorId(args[1]) or Config.mochilaPorId(args[1])
		Notify.banner({ title = "UPGRADE!", subtitle = def and def.nome or "", color = P.gold, sound = false, duration = 2 })
	elseif name == "AlimentarPet" or name == "FundirHat" then
		local maximum = res.upgradeMax or (name == "AlimentarPet" and res.nivel and res.nivel >= Config.PET_NIVEL_MAX)
		Som.tocar(maximum and "upgrade_max" or (res.levelUp and "level_up" or "forge_success"))
		if res.levelUp and res.nivelAntes and res.nivel then ctx.levelUp(res) end
	elseif name == "EquiparHat" or name == "EquiparPet" or name == "EquiparPicareta" or name == "EquiparMelhores" or name == "EquiparMelhoresPets" then
		Som.tocar(res.equipped == false and "ui_desequipar" or "ui_equipar")
	elseif name == "DesequiparTodos" or name == "DesequiparPets" then
		Som.tocar("ui_desequipar")
	elseif name == "ResgatarMissao" then
		if not ctx.batchQuestAudio then Som.tocar("quest_complete") end
	elseif name == "ResgatarDaily" or name == "ResgatarCodigo" then
		-- One cue for what the server actually delivered; never infer rarity from the offer.
		local reward = res.audioReward
		if type(reward) ~= "table" then Som.tocar("reward_banner") -- compatible with an older server
		elseif type(reward.raridade) == "string" and Config.Raridades[reward.raridade] then Som.drop(reward.raridade)
		elseif reward.boost == true then Som.tocar("boost")
		elseif type(reward.moedas) == "number" and reward.moedas > 0 then Som.tocar("reward_banner") end
	elseif name ~= "RolarGacha" and name ~= "UITravel" and name ~= "ComprarRobux" then
		Som.tocar("ui_confirm")
	end
	if res.msg and name ~= "RolarGacha" and name ~= "UITravel" then ctx.toast(res.msg, nil, (name:find("Resgatar") or name:find("Comprar")) and "reward" or "success") end
	return res
end

-- fora do lobby: a opção GRÁTIS (teleporte até o Ignis) vem sempre primeiro
function ctx.accessPopup(nome)
	local passe = nome == "AutoSell" and Mon.passe("AutoSell")
	ctx.popup("Ignis está no lobby", function(p, w, h)
		local details = T.scroll(p, "AccessDetails", 0, 0, w, h - 66, P.ember)
		local cw = w - 14
		local art = T.panel(details, "Art", (cw - 120) / 2, 0, 120, 120, { bg = P.bg2, radius = 20, strokeColor = P.ember })
		T.icon(art, "forge", 10, 10, 100, 100)
		T.para(details, "Message", passe and "Venda com o Ignis usando o teleporte grátis, ou deixe o Auto Sell vender sozinho em qualquer ilha."
			or "Compras de equipamento são feitas com o Ignis. O teleporte até ele é grátis.", 0, 132, cw, 100, 18, P.text2, T.CENTER, "body")
		details.CanvasSize = UDim2.fromOffset(0, 240)
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
		local details = T.scroll(p, "OfferDetails", 0, 0, w, h - 66, P.gold)
		local cw = w - 14
		local narrow = cw < 420
		local heroH = narrow and 238 or 150
		local hero = T.panel(details, "Hero", 0, 0, cw, heroH, { bg = P.bg2, radius = 14, strokeColor = P.gold:Lerp(P.bg2, .4) })
		T.stripes(hero, "Energy", math.max(0, cw - 240), 0, math.min(cw, 240), heroH, P.gold, .93)
		T.icon(hero, info[5], 16, 15, narrow and 72 or 120, narrow and 72 or 120)
		T.text(hero, "Name", item and item.nome or info[1], narrow and 100 or 150, 22, cw - (narrow and 116 or 170), narrow and 58 or 34, 26, P.text, T.LEFT, "display")
		T.para(hero, "Desc", info[2], narrow and 16 or 150, narrow and 100 or 60, narrow and cw - 32 or cw - 170, narrow and 124 or 76, 16, P.text2, T.LEFT, "body")
		local detailsH = heroH + 8
		if item and item.starter and item.valorSeparado then
			T.para(details, "Deal", "Vendido separado: R$ " .. item.valorSeparado .. "   ·   aqui: R$ " .. item.robux, 0, heroH + 12, cw, 40, 14, P.success, T.CENTER)
			detailsH = heroH + 60
		end
		details.CanvasSize = UDim2.fromOffset(0, detailsH)
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
		T.tween(dim, .18, { BackgroundTransparency = .32 }, Enum.EasingStyle.Quad)
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
	Som.tocar(page == "Forge" and "forge_interact" or (wasOpen and "ui_tab" or "ui_abrir"))
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
local function showResults(results, count, playAudio, opened)
 if playAudio~=false and not opened and #results>0 then
  player:SetAttribute("RevealOpen",true)
  T.starOpening(popupLayer,virtualW,virtualH,function()
   player:SetAttribute("RevealOpen",false)
   if alive and screen.Parent then showResults(results,count,playAudio,true) end
  end)
  return
 end
	if #results == 0 then return end
	playAudio = playAudio ~= false
	local desiredCols = math.min(#results, ctx.portrait and 2 or 5)
	local width = math.max(460, desiredCols * 170 + (desiredCols - 1) * 12 + 54)
	local height = math.ceil(#results / desiredCols) * 244 + 150
	local best
	for _, r in ipairs(results) do
		local rr = T.rar(r.raridade)
		if not best or rr.ordem > T.rar(best.raridade).ordem then best = r end
	end
	local revealPlayed, rarityPlayed = false, false
	ctx.popup("Invocação concluída", function(p, w, h, reflow)
		local gap = 12
		local available = w - 14
		local cols = math.max(1, math.min(#results, ctx.portrait and 2 or 5, math.floor((available + gap) / 168)))
		local rows = math.ceil(#results / cols)
		local cw = math.min(170, math.floor((available - (cols - 1) * gap) / cols))
		local ch = cw + 62
		local s = T.scroll(p, "Results", 0, 0, w, h - 66, P.violet)
		s.CanvasSize = UDim2.fromOffset(0, rows * (ch + gap))
		local margin = (available - (cols * cw + (cols - 1) * gap)) / 2
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
			task.delay(reflow and 0 or thisDelay, function()
				if not card.Parent then return end
				if reflow then sc.Scale = 1 else T.tween(sc, .22, { Scale = 1 }, Enum.EasingStyle.Back) end
				task.delay(reflow and 0 or (high and .45 or .16), function()
					if not card.Parent then return end
					back:Destroy()
					T.rarityFrame(card, key, { animated = r.ordem >= 5 })
					T.preview(card, "pet", result.petId, 8, 10, cw - 16, ch - 82, false)
					local plate = T.frame(card, "Plate", 0, ch - 76, cw, 76, P.bg1, .1)
					T.text(plate, "Name", def and def.nome or result.nome or "", 8, 6, cw - 16, 28, 20, P.text, T.CENTER, "display", 1.4)
					local chip, chw = T.chip(plate, "Rarity", T.upper(r.nome), 0, 40, 26, r.cor, { size = 13 })
					chip.Position = UDim2.fromOffset((cw - chw) / 2, 40)
					if result.novo then
						local nc, nw = T.chip(card, "New", "NOVO!", 0, 8, 24, P.success, { solid = true, size = 13 })
						nc.Position = UDim2.fromOffset(cw - nw - 8, 8)
					end
					if not reflow then T.pop(card, high and 1.18 or 1.08, .3) end
					if playAudio then
						-- One rarity signature for the best item, even for x10 summons.
						if result == best and not rarityPlayed then
							rarityPlayed = true
							Som.drop(result.raridade)
						elseif not revealPlayed and not rarityPlayed then
							revealPlayed = true
							Som.tocar("summon_reveal")
						end
					end
				end)
			end)
		end
		T.button(p, "Continue", "Continuar", 0, h - 54, (w - 12) / 2, 54, P.neutral, closePopup)
		T.button(p, "Again", "Invocar de novo " .. (count > 1 and ("x" .. count) or ""), (w - 12) / 2 + 12, h - 54, (w - 12) / 2, 54, P.violet, function()
			closePopup()
			task.defer(ctx.startSummon, count)
		end)
		if not reflow and best and T.rar(best.raridade).ordem >= 5 then
			local bd = Config.petPorId(best.petId)
			local br = T.rar(best.raridade)
			task.delay(delay + .5, function()
				if not s.Parent or not popupOpen then return end
				Notify.banner({ title = T.upper(br.nome) .. "!", subtitle = bd and bd.nome or "", color = br.cor, sound = false, big = br.ordem >= 6, duration = 2.2 })
			end)
		end
	end, width, height, { color = P.violet })
end

function ctx.showLastSummon()
	if ctx.lastSummonResults then showResults(ctx.lastSummonResults,ctx.lastSummonCount or #ctx.lastSummonResults,false) end
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
				Som.tocar("ui_erro")
				if result and result.msg and not result.msg:find("Calma") then ctx.toast(result.msg, nil, "error") end
				break
			end
			if #results == 0 then Som.tocar("invocar_inicio") end
			table.insert(results, result)
			if i < count then task.wait(.66) end
		end
		ctx.summonBusy = false
		ctx.onSummonProgress = nil
		ctx.refresh()
		ctx.lastSummonResults,ctx.lastSummonCount=results,count
		if ctx.page=="Summon" and not ctx.cancelSummon then showResults(results,count)
		elseif #results>0 then
			local best = results[1]
			for _, result in ipairs(results) do
				if T.rar(result.raridade).ordem > T.rar(best.raridade).ordem then best = result end
			end
			Som.drop(best.raridade)
			ctx.toast(tostring(#results).." unidade(s) recebida(s). Veja o último resultado em Invocar.",nil,"reward")
		end
	end)
end

function ctx.levelUp(res)
	Notify.levelUp(res.nivelAntes, res.nivel)
end

-- ---------------------------------------------------------------- CABEÇALHO / CORPO
local FULLSCREEN = {Inventory=true}
local function fullPage() return FULLSCREEN[ctx.page] and not ctx.portrait end
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
	elseif ctx.page == "Equipment" then
		return { { id = "Picaretas", label = "Picaretas", icon = "pickaxe" }, { id = "Mochilas", label = "Mochilas", icon = "items" } },
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
 local full=fullPage()
 if ctx.page=="Events" then title=ctx.eventsTab=="Index" and "Coleção" or ctx.compact and "Diário" or "Recompensas diárias" end
 local banner=window:FindFirstChild("Banner")
 if banner then banner.Title.Text=title end
 local tabsRoot=window:FindFirstChild("Tabs");if tabsRoot then tabsRoot:Destroy() end
 local items,current,tcol,onPick=tabsFor()
 if items then
  local ww=window.Size.X.Offset
  local inline=not ctx.portrait
  local th=inline and 48 or 44
  local tw=math.min(#items*(ctx.compact and 174 or 160),ww-40)
  local tx=inline and (full and (ww-tw)/2 or ww-tw-96) or 20
  if inline and tx<400 and not full then inline=false;tx=20 end
  local ty=inline and 12 or 64
  tabsRoot=T.frame(window,"Tabs",tx,ty,tw,th,nil,1)
  T.tabs(tabsRoot,"Segment",0,0,tw,th,items,current,tcol or P.accent,onPick,{textSize=(ctx.portrait or ctx.compact) and #items>=3 and 18 or 22})
  return inline and 0 or 44
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
 if fullPage() then return virtualW,virtualH,0,0 end
 if ctx.portrait then
  return virtualW-20,virtualH-32,10,16
 elseif ctx.compact then
  return virtualW-28,virtualH-20,14,10
 end
 local ww=math.min(ctx.page=="Summon" and 1460 or ctx.page=="Events" and 1100 or 1280,virtualW-104)
 local wh=math.min(ctx.page=="Summon" and 800 or ctx.page=="Events" and 680 or 780,virtualH-90)
 return ww,wh,(virtualW-ww)/2,(virtualH-wh)/2
end

drawWindow = function(animate)
 if not ctx.page then return end
 modalVersion+=1
 T.clear(modalLayer)
 local ww,wh,wx,wy=windowRect()
 local full=fullPage()
 local _,_,pageColor=pageTitle()
 if ctx.page=="Events" then pageColor=P.warning end
 window=T.panel(modalLayer,"Window",wx,wy,ww,wh,{bg=P.bg0,radius=full and 0 or 10,strokeColor=pageColor,strokeWidth=full and 0 or 2})
 window.Active=true
 local shadow
 if full then
  local inset=GuiService:GetGuiInset().Y/scale.Scale
  T.frame(window,"FullBleedTop",0,-inset,ww,inset+1,P.ink,0)
  window.BackgroundColor3=WHITE
  T.gradient(window,Color3.fromRGB(6,23,31),Color3.fromRGB(5,10,15),90)
  T.texture(window,"pattern",.978,pageColor,440)
  local stars=T.frame(window,"BackdropStars",0,78,ww,wh-78,nil,1)
  T.sparkles(stars,ww,wh-78,3,pageColor:Lerp(WHITE,.35))
  local lower=T.frame(window,"LowerShade",0,wh*.63,ww,wh*.37,P.ink,0)
  T.fade(lower,90,1,.06)
  local top=T.frame(window,"TopBand",0,0,ww,78,WHITE,0)
  T.gradient(top,Color3.fromRGB(4,13,19),Color3.fromRGB(9,26,33),90)
  T.texture(top,"pattern",.975,pageColor,240)
 else shadow=T.shadow(window,10,5,.3) end
 local bw=full and 280 or math.min(ww-112,ctx.page=="Events" and 380 or 330)
 local banner=T.frame(window,"Banner",20,10,bw,50,nil,1)
 T.headerOrnament(banner,bw,50,pageColor)
 T.text(banner,"Title","",12,0,bw-24,50,ctx.page=="Events" and 27 or 32,P.text,T.LEFT,"display",2.3)
 local close=T.closeButton(window,ww-72,8,56,ctx.close)
 local extra=drawHeader()
 local headH=(ctx.compact and 70 or full and 94 or 76)+extra
 bodyW,bodyH=ww-40,wh-headH-16
 body=T.frame(window,"Body",20,headH,bodyW,bodyH,nil,1)
 hud.Visible=not(full or ctx.portrait or ctx.compact)
 drawBody()
 if animate and not full then T.enter(window,.98,.15);if shadow then T.enter(shadow,.98,.15)end end
 if usingGamepad() then task.defer(function() if window and window.Parent then GuiService.SelectedObject=close end end) end
end

-- ---------------------------------------------------------------- HUD
local NAV = {
 {id="Store",label="Loja",icon="store",tip="Passes, boosts e pacotes"},
 {id="Inventory",label="Unidades",icon="units",key="H",tip="Unidades e equipe"},
 {id="Items",label="Itens",icon="items",key="J",tip="Hats e atributos"},
 {id="Areas",label="Viajar",icon="areas",tip="Ilhas de mineração"},
 {id="Quests",label="Missões",icon="quests",tip="Objetivos e recompensas"},
 {id="Events",label="Diário",icon="events",tip="Recompensa diária e coleção"},
 {id="Settings",label="Ajustes",icon="settings",tip="Som, efeitos e códigos"},
}

drawHUD = function()
 T.clear(hud);hudRefs={}
 local compact=ctx.compact
 local margin=18
 local slot=compact and 58 or math.clamp(math.floor(virtualW*.053),64,86)
 local slots=math.clamp(ctx.data and tonumber(ctx.data.slotsPets) or 3,1,6)
 local hotW=slots*slot+(slots-1)*8
 local hotY=virtualH-slot-18
 local walletW=compact and 250 or 300
 local row=T.frame(hud,"Currency",margin,compact and 8 or 16,walletW,48,nil,1)
 hudRefs.wallet=row
 T.icon(row,"coins",-3,-3,60,60)
 hudRefs.coins=T.text(row,"Coins",ctx.shownCoins and T.format(ctx.shownCoins) or "0",61,1,walletW-65,46,compact and 30 or 34,P.gold,T.LEFT,"number",2.5)
 T.hint(row,"Moedas · obtidas na venda de minérios","below")
 local bagW=walletW
 local bag=T.frame(hud,"Bag",margin,compact and 62 or 78,bagW,36,nil,1);hudRefs.bagPanel=bag
 T.icon(bag,"items",-3,-9,46,46)
 hudRefs.bagTrack=T.progress(bag,"Track",44,0,bagW-93,28,0,P.accent,{segments=5})
 hudRefs.bag=T.text(hudRefs.bagTrack,"Count","0 / 0",3,0,bagW-99,28,15,P.text,T.CENTER,"number",1.6)
 hudRefs.sell=T.iconButton(bag,"SellShortcut","forge",bagW-42,-6,40,function() ctx.open("Forge") end)
 T.hint(hudRefs.sell,"Vender minérios com Ignis","below")
 local pw=compact and 180 or 216
 local py=virtualH-(compact and 206 or 74)
 local power=T.frame(hud,"Power",virtualW-pw-margin,py,pw,56,nil,1)
 T.statIcon(power,"dano",-5,-7,66,66)
 hudRefs.power=T.text(power,"Value","0",60,0,pw-60,54,compact and 28 or 34,P.text,T.LEFT,"number",2.5)
 T.hint(power,"Força por golpe","above")
 hudRefs.buffs=T.scroll(hud,"Buffs",walletW+50,18,math.max(100,virtualW-walletW-280),32,P.violet)
 hudRefs.buffs.ScrollingDirection=Enum.ScrollingDirection.X;hudRefs.buffs.ScrollBarThickness=2;hudRefs.buffKeys=""
 local nw=compact and 66 or 80
 local nh=compact and 65 or 82
 local ng=8
 local navY=compact and 108 or 150
 local navCols=compact and 3 or 2
 local dock=T.frame(hud,"Navigation",0,0,virtualW,virtualH,nil,1);hudRefs.rail={}
 for i,it in ipairs(NAV) do
  if it.id=="Settings" then continue end
  local x=margin+((i-1)%navCols)*(nw+ng)
  local y=navY+math.floor((i-1)/navCols)*(nh+ng)
  local navColor=T.Page[it.id] or P.violet
  local b=T.new("TextButton",{Name=it.id,Text="",AutoButtonColor=false,BackgroundColor3=WHITE,BorderSizePixel=0,Position=UDim2.fromOffset(x,y),Size=UDim2.fromOffset(nw,nh)},dock)
  T.corner(b,5);T.gradient(b,navColor:Lerp(P.ink,.68),P.bg0,90)
  T.texture(b,"pattern",.73,navColor,96);T.stroke(b,P.ink,2)
  local edge=T.frame(b,"Rim",2,2,nw-4,nh-4,nil,1);T.corner(edge,4);local rim=T.stroke(edge,navColor:Lerp(WHITE,.25),1.25)
  local isz=compact and 43 or 57
  T.icon(b,it.icon,(nw-isz)/2,1,isz,isz)
  T.text(b,"Label",it.id=="Inventory" and (compact and "Equipe" or "Inventário") or it.label,1,nh-24,nw-2,23,compact and 13 or 16,P.text,T.CENTER,compact and "caption" or "title",1.5)
  if it.key and not compact then T.text(b,"Key",it.key,5,1,18,17,12,P.text2,T.LEFT,"caption",1) end
  T.bindInteraction(b,function() if it.id=="Inventory" then ctx.collection="pet" end;ctx.open(it.id) end,{onFocus=function(on) rim.Color=on and P.text or navColor end})
  T.hint(b,it.tip..(it.key and " · ["..it.key.."]" or ""),"right")
  hudRefs.rail[it.id]=b
 end
 local settings=T.iconButton(dock,"Settings","settings",compact and 0 or margin,virtualH-60,48,function() ctx.open("Settings") end)
 T.hint(settings,"Configurações","above");hudRefs.rail.Settings=settings
 hudRefs.hotbar=T.frame(hud,"Hotbar",(virtualW-hotW)/2-27,hotY,hotW,slot,nil,1)
 screen:SetAttribute("BottomReserved",0)
 screen:SetAttribute("HoldX",(virtualW+hotW)/2-17)
 screen:SetAttribute("HoldY",hotY+(slot-48)/2)
 hudRefs.signature=nil;updateHUD()
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
  root.CanvasSize=UDim2.fromOffset(math.max(0,x-8),0)
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
	hudRefs.bag.Text = T.format(d.carregado or 0) .. " / " .. T.format(d.capacidade or 0)
	local full = frac >= .85
	if hudRefs.sellFull ~= full then
		hudRefs.sellFull = full
		T.setTone(hudRefs.sell, full and P.success or P.neutral)
		if full then T.pop(hudRefs.sell, 1.18, .4) end
	end
	if frac >= 1 and not ctx.bagWasFull then T.shake(hudRefs.bagPanel, 8) end
	ctx.bagWasFull = frac >= 1

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

local function completeCollection(data, kind, definitions)
	local known = data.index and data.index[kind]
	if type(known) ~= "table" or #definitions == 0 then return false end
	for _, definition in ipairs(definitions) do if not known[definition.id] then return false end end
	return true
end

local function acceptData(data)
	if type(data) ~= "table" or type(data.hatsInv) ~= "table" or type(data.petsInv) ~= "table" then return end
	local previous, previousClock = ctx.data, ctx.dataClock
	ctx.data = data
	ctx.dataClock = os.clock()
	if not audioHydrated then
		audioHydrated = true
		local preferences = AudioPreferences.sanitize(data.audio)
		for key, value in pairs(preferences) do
			if pendingAudio[key] == nil and not audioWorker then player:SetAttribute(key, value) end
		end
		ctx.audioPersistent = data.audioPersistent == true
		if not audioWorker then audioStatus(ctx.audioPersistent and "profile" or "session") end
	end
	local transactionAudio = data.audioContext == "daily" or data.audioContext == "code"
	if not transactionAudio and previous and previous.boosts and data.boosts then
		local elapsed = ctx.dataClock - (previousClock or ctx.dataClock)
		for _, key in ipairs({ "sorte", "moedas" }) do
			local before = math.max(0, (previous.boosts[key] or 0) - elapsed)
			if (data.boosts[key] or 0) > before + 5 then Som.tocar("boost"); break end
		end
	end
	hydrated = true
	updateHUD()
	local areas = workspace:FindFirstChild("Areas")
	local areaSig=table.concat((function() local out={} for k,v in pairs(data.areas or {}) do if v then table.insert(out,tostring(k)) end end table.sort(out);return out end)(),",")
	if areas and ctx.areaSignature~=areaSig then ctx.areaSignature=areaSig;for _,d in ipairs(areas:GetDescendants()) do if d.Name=="Barreira" then barrier(d) end end end
	local signature = inventorySignature(data)
	if signature ~= lastInventorySignature then
		if previous then
			local completed = {}
			for _, collection in ipairs({ { "pets", Config.Pets, "Unidades" }, { "hats", Config.Hats, "Hats" } }) do
				if completeCollection(data, collection[1], collection[2]) and not completeCollection(previous, collection[1], collection[2]) then
					table.insert(completed, collection[3])
				end
			end
			if #completed > 0 then
				-- The existing banner queue waits for reveal/menu closure before the milestone cue.
				Notify.banner({ title = "COLEÇÃO COMPLETA!", subtitle = table.concat(completed, " · ") .. " descobertos no Index",
					color = P.gold, sound = not transactionAudio and "achievement" or false, big = true, duration = 2.8 })
			end
		end
		lastInventorySignature = signature
		if ctx.page and not ctx.summonBusy then ctx.refresh() end
	elseif ctx.page == "Forge" or ctx.page == "Quests" or ctx.page == "Events" or ctx.page == "Store" or ctx.page == "Equipment" or ctx.page == "Areas" then
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
	elseif info.tipo == "venda" then
		if type(info.ganho) == "number" and info.ganho > 0 and info.ganho < math.huge then
			Som.venda(info.ganho, info.itens)
			ctx.coinBurst(info.ganho)
			ctx.toast(info.texto or ("+" .. T.format(info.ganho) .. " moedas"), nil, "reward")
		end
	elseif info.tipo == "area" then
		local texto = tostring(info.texto or "")
		ctx.toast(texto, nil, (texto:find("moedas") or texto:find("Compra")) and "reward" or "info")
	elseif info.tipo == "comprarArea" then
		ctx.buyArea(info.areaId)
	end
end)
connect(R.AbrirIgnis.OnClientEvent,function() if ctx.page ~= "Forge" then ctx.open("Forge") end end)
connect(R.AbrirLoja.OnClientEvent,function() ctx.storeTab = "Mochilas"; if ctx.page ~= "Equipment" then ctx.open("Equipment") else ctx.refresh() end end)
connect(R.AbrirGacha.OnClientEvent,function(id)
	if Config.Gachas[id] then ctx.bannerArea = id; if ctx.page ~= "Summon" then ctx.open("Summon") else ctx.refresh() end end
end)
connect(player:GetAttributeChangedSignal("CurrentAreaId"),function() updateHUD() end)
connect(player:GetAttributeChangedSignal("ExpeditionBlurEnabled"),updateBlur)

-- ---------------------------------------------------------------- RESOLUÇÃO
local function resize()
	local v = screen.AbsoluteSize
	if v.X < 1 or v.Y < 1 then return end
	ctx.portrait = v.X < v.Y * .85
	ctx.compact = not ctx.portrait and v.Y < 560
	local s=math.clamp(math.min(v.X/1600,v.Y/900),1,1.35)
	if ctx.portrait then s=1 elseif ctx.compact then s=math.clamp(v.Y/480,.75,.95) end
 screen:SetAttribute("HudScale",s)
	scale.Scale = s
	T.uiScale = s
	virtualW, virtualH = v.X / s, v.Y / s
	canvas.Size = UDim2.fromOffset(virtualW, virtualH)
	for _, layer in ipairs({ hud, modalLayer, toastLayer, popupLayer, dialogHost, tipLayer }) do
		layer.Size = UDim2.fromOffset(virtualW, virtualH)
	end
	Notify.toastTop = ctx.portrait and 240 or 126
	drawHUD()
	hud.Visible = not (ctx.page and (fullPage() or ctx.portrait or ctx.compact))
	if ctx.page then drawWindow(false) end
	-- Reflow preserves builder state and input, without closing or shrinking controls.
	if popupOpen and popupState then renderPopup(popupState, true) end
	Notify.relayout()
end
screen:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)

connect(Input.InputBegan,function(input, processed)
	if processed or Input:GetFocusedTextBox() then return end
	local key = input.KeyCode
	if key == Enum.KeyCode.Escape or key==Enum.KeyCode.ButtonB then
		if popupOpen then closePopup() elseif ctx.page then ctx.close() end
	elseif key == Enum.KeyCode.H or key == Enum.KeyCode.B or key==Enum.KeyCode.ButtonY then ctx.collection = "pet"; ctx.open("Inventory")
	elseif key == Enum.KeyCode.J then ctx.open("Items")
	end
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

