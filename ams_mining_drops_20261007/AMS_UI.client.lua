-- ============================================================================
-- AMS UI · CLIENTE (StarterPlayerScripts.AMS_UI)
-- Monta a UI inteira (ReplicatedStorage.UI) e liga aos Remotes do jogo.
-- Contrato mantido com outros scripts (ver ams_ui/ui-contract.md):
--   ScreenGui "ExpeditionUI" com ProfileReady, OpenPage, PopupOpen, HudScale,
--   HoldX/HoldY, UIScalePreference, SummonPhase; player.RevealOpen;
--   barreiras LiberaComArea; preferencias de audio como atributos.
-- Nada de economia aqui: tudo vem do snapshot do servidor.
-- ============================================================================
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local ContentProvider = game:GetService("ContentProvider")
local SoundService = game:GetService("SoundService")

local player = Players.LocalPlayer
local pg = player:WaitForChild("PlayerGui")
pg.ScreenOrientation = Enum.ScreenOrientation.LandscapeSensor

local UIRoot = RS:WaitForChild("UI")
local Theme = require(UIRoot.Theme)
local Util = require(UIRoot.Util)
local Motion = require(UIRoot.Motion)
local Responsive = require(UIRoot.Responsive)
local State = require(UIRoot.State)
local Router = require(UIRoot.Router)
local Actions = require(UIRoot.Actions)
local Comp = UIRoot.Components
local Toast = require(Comp.Toast)
local Confirm = require(Comp.Confirm)
local Tooltip = require(Comp.Tooltip)
local Button = require(Comp.Button)
local Icon = require(Comp.Icon)
local Screens = UIRoot.Screens
local Audio = require(SoundService:WaitForChild("UIAudio"))
local Config = require(RS:WaitForChild("Config"))
local Mon = require(RS:WaitForChild("MonetizacaoConfig"))
local AudioPreferences = require(RS:WaitForChild("AudioPreferences"))
local UIPreferences = require(RS:WaitForChild("UIPreferences"))
local IgnisContent = require(RS:WaitForChild("DuasIlhasUI"):WaitForChild("IgnisContent"))
local C = Theme.Color

-- ---------------------------------------------------------------- SHELL
local old = pg:FindFirstChild("ExpeditionUI")
if old then old:Destroy() end
local shell = Util.new("ScreenGui", { Name = "ExpeditionUI", ResetOnSpawn = false, DisplayOrder = 25, IgnoreGuiInset = false,
	ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets, ZIndexBehavior = Enum.ZIndexBehavior.Sibling })
shell:SetAttribute("OpenPage", "")
shell:SetAttribute("PopupOpen", false)
shell:SetAttribute("ProfileReady", false)
local root = Util.new("Frame", { Name = "Root", BackgroundTransparency = 1, Size = UDim2.fromOffset(1280, 720) }, shell)
local rootScale = Util.new("UIScale", { Name = "RootScale" }, root)
local function layer(name, z)
	return Util.new("Frame", { Name = name, BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = z }, root)
end
local L = {
	hud = layer("HUDLayer", Theme.Layer.hud),
	window = layer("WindowLayer", Theme.Layer.window),
	popup = layer("PopupLayer", Theme.Layer.popup),
	toast = layer("ToastLayer", Theme.Layer.toast),
	reveal = layer("RevealLayer", Theme.Layer.reveal),
	tooltip = layer("TooltipLayer", Theme.Layer.tooltip),
}
shell.Parent = pg

-- escala: preferencia salva (UIPreferences) * classe do aparelho
local uiPrefs = UIPreferences.sanitize()
local function prefKey() return Responsive.class == "phone" and "mobileScale" or "desktopScale" end
Responsive.compute(shell.AbsoluteSize)
Responsive.userScale = math.clamp((uiPrefs[prefKey()] or 0.85) / 0.85, 0.85, 1.15)
Responsive.bind(shell, rootScale)
local function applyRootSize()
	root.Size = UDim2.fromOffset(Responsive.view.X, Responsive.view.Y)
	shell:SetAttribute("HudScale", Responsive.scale)
	shell:SetAttribute("UIScalePreference", Responsive.userScale * 0.85)
end
Responsive.changed:Connect(applyRootSize)
applyRootSize()
Motion.reduced = player:GetAttribute("ReducedMotion") == true

-- ---------------------------------------------------------------- APP (contexto das telas)
local app = {
	State = State, Router = Router, Actions = Actions, Toast = Toast, Confirm = Confirm, Tooltip = Tooltip,
	Config = Config, Mon = Mon, shell = shell, celebrated = {}, layers = L,
}

function app.petImage(id)
	local art = Config.PetArte and Config.PetArte[id]
	return art and (art.busto or art.corpo) or ""
end
function app.hatImage(id)
	local def = Config.hatPorId(id)
	return def and def.assetId and ("rbxthumb://type=Asset&id=" .. def.assetId .. "&w=150&h=150") or ""
end
function app.hasArea(d, id)
	local a = d and d.areas
	return a ~= nil and (a[id] == true or a[tostring(id)] == true)
end

Tooltip.init(L.tooltip)
Button._setTooltip(Tooltip)
Toast.init(L.toast, function() return Responsive.view end)
Confirm.init(L.popup, function(open) shell:SetAttribute("PopupOpen", open) end)
Router.init(app, L.window, shell)

-- ---------------------------------------------------------------- ACOES COMUNS
function app.buyRobux(key)
	local res = Actions.run("ComprarRobux", { key }, { ok = false })
	return res
end

function app.travel(action, id)
	if not State.hasPass("FastTravel") then
		Confirm.ask({ title = "Fast Travel", icon = "compass", tone = "crystal",
			text = "Viaje pelo menu entre a Vila-Forja e as ilhas liberadas. Sem o passe, use os portais andando.",
			confirmText = "Ver passe", cancelText = "Agora não", onConfirm = function() app.buyRobux("FastTravel") end })
		return
	end
	local res = Actions.run("UITravel", { action, id }, { ok = "open" })
	if res.ok then Router.close() end
end

local AreaUnlock -- definido abaixo
function app.buyArea(id) AreaUnlock:confirm(id) end

-- moedas voando ate o contador (pool de 10 moedas reaproveitadas)
local coinPool = {}
for i = 1, 10 do
	local c = Icon.coin(L.toast, 30, { name = "FlyCoin" .. i, anchor = Vector2.new(0.5, 0.5), z = Theme.Layer.toast + 5 })
	c.Visible = false
	coinPool[i] = c
end
local HUD
function app.coinBurst(amount, fromGui)
	if not HUD or Motion.reduced then return end
	local scale = Responsive.scale
	local function toDesign(v) return (v - root.AbsolutePosition) / scale end
	local src = fromGui and toDesign(fromGui.AbsolutePosition + fromGui.AbsoluteSize / 2) or Responsive.view / 2
	local target = toDesign(HUD.coins.icon.AbsolutePosition + HUD.coins.icon.AbsoluteSize / 2)
	local n = math.clamp(math.floor(math.log10(math.max(10, amount or 10)) * 1.5), 4, 10)
	for i = 1, n do
		local c = coinPool[i]
		c.Visible = true
		c.Position = UDim2.fromOffset(src.X, src.Y)
		local ang = math.random() * math.pi * 2
		local r = 40 + math.random() * 80
		Motion.tween(c, 0.22, { Position = UDim2.fromOffset(src.X + math.cos(ang) * r, src.Y + math.sin(ang) * r * 0.7) }, Motion.Ease.out, "fly")
		task.delay(0.26 + i * 0.035, function()
			Motion.tween(c, 0.38, { Position = UDim2.fromOffset(target.X, target.Y) }, { Enum.EasingStyle.Quint, Enum.EasingDirection.In }, "fly")
			task.delay(0.38, function()
				c.Visible = false
				Audio.play("coinTick")
				Motion.pop(HUD.coins.icon, 1.15, Motion.Dur.fast)
			end)
		end)
	end
end

local function nearIgnis(dist)
	local npcs = workspace:FindFirstChild("NPCs")
	local npc = npcs and npcs:FindFirstChild("Ignis")
	local belly = npc and npc:FindFirstChild("belly", true)
	local hrp = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	return belly and hrp and (belly.Position - hrp.Position).Magnitude <= (dist or 22) or false
end

app.nearIgnis = nearIgnis

-- atalho Vender do HUD: abre a forja (npc se perto do Ignis; senao portatil)
function app.sellShortcut()
	local d = State.data
	if not d then return end
	if (d.qtdMinerios or 0) <= 0 then
		Audio.play("error")
		Toast.push({ kind = "info", text = "Mochila vazia. Quebre minérios para encher!", sound = false })
		return
	end
	Router.open("Ignis", { mode = nearIgnis() and "npc" or "portable", tab = "vender" })
end

-- semAcesso: o servidor recusou por distancia/lugar
Actions.onNoAccess = function(kind)
	if kind == "PortableForge" then
		Confirm.ask({ title = "Ígnis está na Vila-Forja", icon = "forge", tone = "ember",
			text = "Venda grátis falando com o Ígnis no lobby, ou venda de qualquer ilha com a Forja Portátil.",
			confirmText = "Forja Portátil", cancelText = "Entendi", onConfirm = function() app.buyRobux("PortableForge") end })
	else
		Toast.push({ kind = "info", text = "Compras de equipamento são feitas na Vila-Forja (lobby)." })
	end
end

-- ---------------------------------------------------------------- AUDIO (prefs salvas em lote)
for key, default in pairs(AudioPreferences.defaults) do
	if AudioPreferences.value(key, player:GetAttribute(key)) == nil then player:SetAttribute(key, default) end
end
local pendingAudio, audioWorker = {}, false
app.audioStatus = "loading"
function app.setAudio(key, value)
	value = AudioPreferences.value(key, value)
	if value == nil then return end
	player:SetAttribute(key, value)
	pendingAudio[key] = value
	app.audioStatus = "pending"
	if audioWorker then return end
	audioWorker = true
	task.spawn(function()
		task.wait(0.4)
		while next(pendingAudio) do
			local patch = pendingAudio
			pendingAudio = {}
			local res = State.invoke("AtualizarAudioProfile", patch)
			if res.ok then
				app.audioStatus = res.persistent and "profile" or "session"
			else
				app.audioStatus = "error"
			end
			local s = Router.get("Ajustes")
			if s then s:syncAudio() end
			task.wait(0.4)
		end
		audioWorker = false
	end)
end

function app.setUserScale(v, save)
	Responsive.setUserScale(v, shell, rootScale)
	if save then
		local key = prefKey()
		local val = UIPreferences.value(Responsive.userScale * 0.85)
		if val then task.spawn(State.invoke, "AtualizarUIProfile", { [key] = val }) end
	end
end

-- ---------------------------------------------------------------- TELAS
local Collection = require(Screens.Collection)
local function reg(name, module, meta) Router.register(name, module, meta) end
reg("Loja", require(Screens.Store), { title = "Loja", icon = "shop", color = Theme.Menu.Loja, width = 1000, height = 620 })
reg("Unidades", { build = function(a, w) return Collection.build(a, w, "pet") end }, { title = "Unidades", icon = "units", color = Theme.Menu.Unidades, width = 1060, height = 640 })
reg("Hats", { build = function(a, w) return Collection.build(a, w, "hat") end }, { title = "Hats", icon = "hat", color = Theme.Menu.Hats, width = 1060, height = 640 })
reg("Invocar", require(Screens.Summon), { title = "Invocar", icon = "star", color = Theme.Menu.Invocar, width = 1060, height = 640 })
reg("Ignis", require(Screens.Ignis), { title = "Forja do Ígnis", icon = "forge", color = Theme.Menu.Ignis, width = 1020, height = 640 })
reg("Viajar", require(Screens.Travel), { title = "Viajar", icon = "compass", color = Theme.Menu.Viajar, width = 940, height = 600 })
reg("Missoes", require(Screens.Quests), { title = "Missões", icon = "quests", color = Theme.Menu.Missoes, width = 960, height = 600 })
reg("Diario", require(Screens.Daily), { title = "Diário", icon = "calendar", color = Theme.Menu.Diario, width = 1000, height = 600 })
reg("Ajustes", require(Screens.Settings), { title = "Ajustes", icon = "settings", color = Theme.Menu.Ajustes, width = 860, height = 600 })
local Alchemy = require(Screens.Alchemy)
reg("Alquimia", Alchemy, { title = "Alquimia", icon = "potion", color = Theme.Menu.Alquimia, width = 980, height = 600 })

HUD = require(Screens.HUD).build(app, L.hud)
app.HUD = HUD
app.Reveal = require(Screens.Reveal).build(app, L.reveal)
AreaUnlock = require(Screens.AreaUnlock).build(app, L.reveal)
Alchemy.dungeonStrip(app, HUD.Root)
local Quests = require(Screens.Quests)
local Daily = require(Screens.Daily)

function app.openMenu(key)
	Router.toggle(key)
end

function app.badgeFor(key, d)
	if key == "Missoes" then return Quests.claimable(app, d) > 0 end
	if key == "Diario" then return Daily.available(d) end
	return false
end

-- HUD some atras de janela no celular (espaco); no PC fica atras do fundo escuro
Router.changed:Connect(function(name)
	local phone = Responsive.class == "phone"
	L.hud.Visible = not (name and phone)
	-- moedas/mochila ficam no canto da janela: somem enquanto uma janela esta aberta
	if HUD.wallet then HUD.wallet.Visible = name == nil end
end)

-- ---------------------------------------------------------------- MUNDO: barreiras
local function barrier(part)
	if not State.data or not part:IsA("BasePart") or part.Name ~= "Barreira" then return end
	local id = part:GetAttribute("LiberaComArea")
	local unlocked = id and app.hasArea(State.data, id)
	part.CanCollide = not unlocked
	part.Transparency = unlocked and 0.9 or 0.65
end
local areaSig = nil
local function applyBarriers(d)
	local keys = {}
	for k, v in pairs(d.areas or {}) do if v then table.insert(keys, tostring(k)) end end
	table.sort(keys)
	local sig = table.concat(keys, ",")
	if sig == areaSig then return end
	areaSig = sig
	local areas = workspace:FindFirstChild("Areas")
	if areas then for _, p in ipairs(areas:GetDescendants()) do if p.Name == "Barreira" then barrier(p) end end end
end
workspace.DescendantAdded:Connect(function(p) if p.Name == "Barreira" then task.defer(barrier, p) end end)

-- ---------------------------------------------------------------- BOOSTS
-- relogio dos boosts (a barra da Pedra Chefe saiu do HUD: o chefe tem a barra de vida dele no mundo)
task.spawn(function()
	while true do
		HUD:tickBuffs()
		task.wait(1)
	end
end)

-- ---------------------------------------------------------------- DADOS
local audioHydrated, uiHydrated = false, false
local lastFull = false
local function completeCollection(d, kind, defs)
	local known = d.index and d.index[kind]
	if type(known) ~= "table" then return false end
	for _, def in ipairs(defs) do if not known[def.id] then return false end end
	return true
end

State.changed:Connect(function(d, prev)
	if not audioHydrated then
		audioHydrated = true
		for k, v in pairs(AudioPreferences.sanitize(d.audio)) do
			if pendingAudio[k] == nil then player:SetAttribute(k, v) end
		end
		app.audioStatus = d.audioPersistent and "profile" or "session"
	end
	if not uiHydrated then
		uiHydrated = true
		uiPrefs = UIPreferences.sanitize(nil, d.ui)
		Responsive.setUserScale(math.clamp((uiPrefs[prefKey()] or 0.85) / 0.85, 0.85, 1.15), shell, rootScale)
	end
	HUD:onData(d, prev)
	Router.broadcast(d, prev)
	applyBarriers(d)
	shell:SetAttribute("ProfileReady", true)
	-- mochila encheu agora
	local full = State.backpackFull()
	if full and not lastFull and prev then
		Audio.play("backpackFull")
		Toast.push({ kind = "warning", title = "Mochila cheia!", text = "Venda no Ígnis para continuar minerando.", sound = false })
	end
	lastFull = full
	if prev then
		-- ilha liberada por outro caminho (parede de deposito)
		for _, a in ipairs(Config.Areas) do
			if app.hasArea(d, a.id) and not app.hasArea(prev, a.id) and not app.celebrated[a.id] then
				app.celebrated[a.id] = true
				AreaUnlock:celebrate(a.id)
			end
		end
		-- boost ativado (compra/daily)
		local pb, nb = prev.boosts or {}, d.boosts or {}
		for _, k in ipairs({ "moedas", "sorte" }) do
			if (nb[k] or 0) > (pb[k] or 0) + 5 and d.audioContext == nil then
				Audio.play("quest")
				Toast.push({ kind = "reward", title = k == "moedas" and "Moedas x2 ativado!" or "Sorte ativada!", text = "Aproveite enquanto dura.", sound = false })
				break
			end
		end
		-- colecao completa
		for _, col in ipairs({ { "pets", Config.Pets, "Pets" }, { "hats", Config.Hats, "Hats" } }) do
			if completeCollection(d, col[1], col[2]) and not completeCollection(prev, col[1], col[2]) then
				Audio.play("rareDrop")
				Toast.banner("COLEÇÃO COMPLETA!", col[3] .. ": todos descobertos", C.gold)
			end
		end
	end
end)

-- ---------------------------------------------------------------- EVENTOS DO SERVIDOR
local function oreName(variante)
	local a = Config.areaPorId(player:GetAttribute("CurrentAreaId") or 0)
	local info = a and Config.infoMinerio(a.tema .. "_" .. (variante or "comum"))
	return info and info.nome or "Minério"
end
local VARIANT_RAR = { comum = "comum", incomum = "incomum", raro = "raro", epica = "epico", lendaria = "lendario" }

State.on("FeedbackMina", function(info)
	if type(info) ~= "table" then return end
	local t = info.tipo
	if t == "quebrou" then
		if info.chefe then
			Audio.play("bossBreak")
			Toast.banner("CHEFE DERROTADO!", "Recompensa para todos que ajudaram", C.danger)
		end
	elseif t == "dropColetado" then
		local r = Theme.rarity(VARIANT_RAR[info.variante] or "comum")
		local nome = info.nome or oreName(info.variante)
		Audio.play("collect", { pitch = 1 + (r.ordem - 1) * 0.04 })
		Toast.feed("+1 " .. nome, Theme.lighten(r.color, 0.35))
		if r.ordem >= 5 then
			Audio.play("rareDrop")
			Toast.banner("MINÉRIO " .. r.nome:upper() .. "!", nome, nil, VARIANT_RAR[info.variante])
		end
	elseif t == "hat" then
		local r = Theme.rarity(info.raridade)
		local quiet = info.audioContext == "daily" or info.audioContext == "code"
		if not quiet then
			if r.ordem >= 4 then Audio.play("rareDrop") else Audio.play("equip") end
		end
		if info.novo or r.ordem >= 4 then
			Toast.push({ kind = "rare", rarity = info.raridade, title = (info.novo and "NOVO HAT!  " or "") .. r.nome:upper(),
				text = (info.texto or "Hat") .. "  ·  nível " .. tostring(info.nivel or 1), sound = false, duration = 4 })
			if r.ordem >= 5 then Toast.banner(r.nome:upper() .. "!", info.texto, nil, info.raridade) end
		else
			Toast.feed("+ " .. (info.texto or "Hat"), Theme.lighten(r.color, 0.35))
		end
	elseif t == "cheia" then
		if info.origem == "mochila_minerio" and State.data and State.data.mochilaInfinita then return end
		Audio.play("error")
		Toast.push({ kind = "warning", title = info.origem == "mochila_minerio" and "Mochila cheia!" or "Inventário cheio!", text = info.texto, sound = false })
		Motion.shake(HUD.bag, 7)
	elseif t == "bloqueada" then
		Audio.play("error")
		Toast.push({ kind = "warning", text = info.texto or "Área bloqueada", sound = false })
	elseif t == "venda" then
		if type(info.ganho) == "number" and info.ganho > 0 and info.ganho < math.huge then
			Audio.play("sell")
			app.coinBurst(info.ganho, HUD.bag)
			Toast.push({ kind = "reward", coin = true, title = "+" .. Util.short(info.ganho) .. " moedas", text = info.texto or "Venda automática", sound = false })
		end
	elseif t == "area" then
		local txt = tostring(info.texto or "")
		local low = txt:lower()
		if low:find("chefe apareceu") then
			Audio.play("notify")
			Toast.push({ kind = "error", title = "PEDRA CHEFE!", text = txt, sound = false, duration = 4 })
		else
			Toast.push({ kind = (low:find("moedas") or low:find("compra")) and "reward" or "info", text = txt })
		end
	elseif t == "comprarArea" then
		app.buyArea(info.areaId)
	end
end)

State.on("AbrirIgnis", function() Router.open("Ignis", { mode = "npc", tab = "vender" }) end)
State.on("AbrirLoja", function() Router.open("Ignis", { mode = "npc", tab = "mochilas", say = "Mochilas novas! Quanto maior, mais minério você carrega." }) end)
State.on("AbrirCraft", function() Router.open("Alquimia") end)
State.on("AbrirGacha", function(id)
	if Config.Gachas[id] then Router.open("Invocar", { area = id }) end
end)

-- ofertas do servidor (Starter / Inventario cheio). Mochila cheia ja tem fluxo proprio.
local OFFER = {
	Starter = { "Kit do Explorador", "60 min de renda da sua ilha + Moedas x2 (60 min) + Sorte x1,5 (30 min).", "gift" },
	Inventory300 = { "Inventário cheio", "Funda repetidos para liberar espaço (grátis) ou adicione 300 espaços.", "badge" },
}
local pendingOffer
local function offerBusy()
	return Router.current ~= nil or Confirm.isOpen or player:GetAttribute("RevealOpen") == true or player:GetAttribute("TravelTransition") == true
end
local function showOffer(oferta)
	local function closed() State.fire("OfertaAcao", "fechada", oferta) end
	local o = OFFER[oferta]
	if not o then closed() return end
	-- tela ocupada: guarda e mostra quando liberar (nao descarta)
	if offerBusy() then pendingOffer = oferta return end
	pendingOffer = nil
	local item = Mon.passe and Mon.passe(oferta) or nil
	item = item or (Mon.produto and Mon.produto(oferta))
	if not item or (item.id or 0) <= 0 then closed() return end
	Confirm.ask({ title = o[1], icon = o[3], tone = "gold", text = o[2], confirmText = item.robux .. " Robux",
		cancelText = oferta == "Inventory300" and "Fundir hats" or "Agora não",
		onConfirm = function() closed(); app.buyRobux(oferta) end,
		onCancel = function()
			closed()
			if oferta == "Inventory300" then Router.open("Hats") end
		end })
end
State.on("OfertaMostrar", showOffer)
local function retryOffer()
	if pendingOffer and not offerBusy() then
		local o = pendingOffer
		task.delay(0.6, function() if pendingOffer == o and not offerBusy() then showOffer(o) end end)
	end
end
shell:GetAttributeChangedSignal("OpenPage"):Connect(retryOffer)
shell:GetAttributeChangedSignal("PopupOpen"):Connect(retryOffer)
player:GetAttributeChangedSignal("RevealOpen"):Connect(retryOffer)
player:GetAttributeChangedSignal("TravelTransition"):Connect(retryOffer)

-- ---------------------------------------------------------------- IGNIS: conversa de introducao
local talk, pendingTalk = nil, nil
local function talkInvoke(cmd, token, step)
	local res = State.invoke("IgnisConversationAction", cmd, token, step)
	if res.busy then return { ok = false, msg = "Um instante..." } end
	return res
end
local function ignisScreen() return Router.get("Ignis") end
local function renderTalk()
	local s = ignisScreen()
	if s and talk then s:renderTalk(talk, IgnisContent.Steps) end
end
local function talkReady()
	return shell:GetAttribute("ProfileReady") == true and player:GetAttribute("AMSLoadingActive") ~= true
		and player:GetAttribute("RevealOpen") ~= true and not Confirm.isOpen and (Router.current == nil or Router.current == "Ignis")
end
local function openTalk(payload)
	if talk or not talkReady() then pendingTalk = payload return end
	pendingTalk = nil
	if not nearIgnis(25) then task.spawn(talkInvoke, "cancel", payload.token) return end
	if payload.version ~= IgnisContent.Version then Toast.push({ kind = "info", text = "Fale comigo novamente em instantes." }) return end
	talk = { token = payload.token, index = 1, busy = false, finished = false, status = "" }
	Router.open("Ignis", { talk = true, mode = "npc" })
	renderTalk()
	local mine = talk
	task.spawn(function()
		while talk == mine do
			task.wait(8)
			if talk == mine and not mine.busy and nearIgnis(25) then
				local rf = State.remote("IgnisConversationAction")
				if rf then pcall(rf.InvokeServer, rf, "progress", mine.token, mine.index) end
			end
		end
	end)
end
function app.ignisTalkNext()
	local st = talk
	if not st or st.busy then return end
	st.busy = true
	renderTalk()
	local completing = st.index == #IgnisContent.Steps
	local res = talkInvoke(completing and "finish" or "progress", st.token, st.index + 1)
	if talk ~= st then return end
	st.busy = false
	if not res.ok then st.status = res.msg or "Tente novamente em um instante."; renderTalk() return end
	if completing then
		st.finished = true
		talk = nil
		Audio.play("levelUp")
		Router.open("Ignis", { mode = "npc", tab = "vender", say = "Pronto! Agora é com você. Traga minério que eu pago bem." })
	else
		st.index += 1
		st.status = ""
		renderTalk()
	end
end
function app.ignisTalkBack()
	if talk and not talk.busy and talk.index > 1 then talk.index -= 1; talk.status = ""; renderTalk() end
end
function app.ignisTalkClosed()
	local st = talk
	talk = nil
	if st and not st.finished then task.spawn(talkInvoke, "cancel", st.token) end
end
function app.ignisReplay()
	if talk then return end
	local res = talkInvoke("replay")
	if res.ok then
		Router.close()
		task.wait(Motion.Dur.close + 0.02)
		openTalk(res)
	else
		Toast.push({ kind = "info", text = res.msg or "Venha falar comigo na forja." })
	end
end
State.on("IgnisConversation", function(payload)
	if type(payload) == "table" and payload.ok and type(payload.token) == "string" and (not talk or talk.token ~= payload.token) then
		openTalk(payload)
	end
end)
local function tryPendingTalk() if pendingTalk and not talk and talkReady() then openTalk(pendingTalk) end end
for _, a in ipairs({ "ProfileReady", "PopupOpen", "OpenPage" }) do shell:GetAttributeChangedSignal(a):Connect(tryPendingTalk) end
player:GetAttributeChangedSignal("RevealOpen"):Connect(tryPendingTalk)
player:GetAttributeChangedSignal("AMSLoadingActive"):Connect(tryPendingTalk)

-- ---------------------------------------------------------------- TECLADO / CONTROLE
UIS.InputBegan:Connect(function(input, processed)
	if processed or UIS:GetFocusedTextBox() then return end
	local k = input.KeyCode
	if k == Enum.KeyCode.Escape or k == Enum.KeyCode.ButtonB then
		if Confirm.isOpen then Confirm.close(false) elseif Router.current then Router.close() end
	end
end)

-- ---------------------------------------------------------------- QA (so no Studio)
-- shell.Debug:Invoke("open","Hats") | ("close") | ("reveal",{...}) | ("celebrate",3) | ("toast",kind,text) | ("log")
local openLog = {}
Router.changed:Connect(function(name, prev)
	table.insert(openLog, string.format("%.2f %s -> %s | %s", os.clock(), tostring(prev), tostring(name), debug.traceback("", 2):gsub("\n", " / "):sub(1, 400)))
	if #openLog > 20 then table.remove(openLog, 1) end
end)
if game:GetService("RunService"):IsStudio() then
	local dbg = Instance.new("BindableFunction")
	dbg.Name = "Debug"
	dbg.OnInvoke = function(cmd, a, b, c)
		if cmd == "open" then return Router.open(a, b)
		elseif cmd == "close" then Router.close() return true
		elseif cmd == "celebrate" then AreaUnlock:celebrate(a) return true
		elseif cmd == "closeOverlay" then AreaUnlock:close() return true
		elseif cmd == "reveal" then task.spawn(function() app.Reveal:play(a, { onFinish = function() end }) end) return true
		elseif cmd == "revealSkip" then app.Reveal:skip() return true
		elseif cmd == "revealFinish" then app.Reveal:finish(false) return true
		elseif cmd == "toast" then Toast.push({ kind = a, title = b, text = c }) return true
		elseif cmd == "banner" then Toast.banner(a, b) return true
		elseif cmd == "confirm" then Confirm.ask({ title = a or "Teste", text = b or "Texto", cost = c, balance = State.data and State.data.moeda or 0 }) return true
		elseif cmd == "log" then return table.concat(openLog, "\n") .. "\n--\n" .. table.concat(Router.log, "\n")
		elseif cmd == "scale" then Responsive.setUserScale(a, shell, rootScale) return Responsive.scale
		end
	end
	dbg.Parent = shell
end

-- ---------------------------------------------------------------- PRELOAD + START
task.spawn(function()
	local imgs = {}
	for _, id in ipairs(Theme.allIcons()) do
		local l = Instance.new("ImageLabel")
		l.Image = id
		table.insert(imgs, l)
	end
	pcall(function() ContentProvider:PreloadAsync(imgs) end)
	for _, l in ipairs(imgs) do l:Destroy() end
	Audio.preload()
end)

State.start()
