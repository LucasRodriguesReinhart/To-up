local RS = game:GetService("ReplicatedStorage")
local Debris = game:GetService("Debris")
local Config = require(RS.Config)
local Geometry = require(RS.MiningGeometry)
local pending = {}
local PlayerData = require(script.Parent.PlayerData)

local Mineracao = {}
local rnd = Random.new()
local ultimoGolpe = {}   -- [player] = tick
local COOLDOWN = Config.COOLDOWN_GOLPE

local RESPAWN_ROCHA = Config.RESPAWN_ROCHA
local RESPAWN_CHEFE = Config.RESPAWN_CHEFE

-- ---------- SORTEIO DE HAT ----------
local CHANCE_HAT = 0.05   -- 5% por rocha quebrada, antes da sorte

local function sortearHat(sorte, tema)
	if rnd:NextNumber() > CHANCE_HAT * (1 + sorte) then return nil end

	-- peso da raridade melhora um pouco com sorte
	local total = 0
	local pesos = {}
	for chave, r in pairs(Config.Raridades) do
		local p = r.peso
		if chave ~= "comum" then p = p * (1 + sorte) end
		pesos[chave] = p
		total = total + p
	end

	local roll = rnd:NextNumber() * total
	local escolhida
	for chave, p in pairs(pesos) do
		roll = roll - p
		if roll <= 0 then escolhida = chave; break end
	end
	escolhida = escolhida or "comum"

	-- o hat sempre vem da colecao da propria ilha
	local candidatos = Config.hatsDoTema(tema, escolhida)
	if #candidatos == 0 then return nil end
	return candidatos[rnd:NextInteger(1, #candidatos)]
end

-- ---------- BARRA DE VIDA ----------
local function fmt(n)
	n = math.max(math.floor(n), 0)
	if n >= 1e9 then return string.format("%.1fB", n / 1e9) end
	if n >= 1e6 then return string.format("%.1fM", n / 1e6) end
	if n >= 1e3 then return string.format("%.1fK", n / 1e3) end
	return tostring(n)
end

local function atualizarBarra(rocha)
	local bb = rocha:FindFirstChild("Vida")
	if not bb then return end
	local barra = bb:FindFirstChild("Barra", true)
	local texto = bb:FindFirstChild("HPTexto", true)
	local hp, hpMax = rocha:GetAttribute("HP"), rocha:GetAttribute("HPMax")
	if barra then
		barra.Size = UDim2.fromScale(math.clamp(hp / hpMax, 0, 1), 1)
		-- vermelho conforme vai quebrando
		local f = math.clamp(hp / hpMax, 0, 1)
		if not rocha:GetAttribute("Chefe") then
			barra.BackgroundColor3 = Color3.fromRGB(120, 220, 130):Lerp(Color3.fromRGB(255, 100, 70), 1 - f)
		end
	end
	if texto then
		texto.Text = fmt(hp) .. " / " .. fmt(hpMax)
	end
end

-- ---------- QUEBRA ----------
local function quebrar(rocha, player)
	local perfil = PlayerData.get(player)
	if not perfil then return end

	local areaId = rocha:GetAttribute("AreaId")
	local minerioId = Config.idMinerio(rocha:GetAttribute("Tema"), rocha:GetAttribute("Variante"))
	local ehChefe = rocha:GetAttribute("Chefe")

	if ehChefe then
		-- libera a proxima area
		local prox = areaId + 1
		if Config.areaPorId(prox) and not perfil.areas[prox] then
			perfil.areas[prox] = true
			RS.Remotes.FeedbackMina:FireClient(player, {
				tipo = "area",
				texto = "Area desbloqueada: " .. Config.areaPorId(prox).nome,
			})
		end
	else
		-- minerio, respeitando a capacidade
		if PlayerData.mochilaCheia(perfil) then
			-- nao deveria chegar aqui, mas se chegar a rocha volta ao normal
			-- em vez de ficar travada com HP 0 pra sempre
			rocha:SetAttribute("HP", rocha:GetAttribute("HPMax"))
			atualizarBarra(rocha)
			RS.Remotes.FeedbackMina:FireClient(player, { tipo = "cheia", texto = "Mochila cheia!" })
			return
		end
		perfil.mochila[minerioId] = (perfil.mochila[minerioId] or 0) + 1

		local _, extraB = PlayerData.bonusHats(perfil)
		local sorte = extraB.sorte
		local hat = sortearHat(sorte, rocha:GetAttribute("Tema"))
		if hat then
			local posse = perfil.hats[hat.id]
			if posse then
				posse.qtd = posse.qtd + 1
			else
				perfil.hats[hat.id] = { qtd = 1, nivel = 1 }
			end
			RS.Remotes.FeedbackMina:FireClient(player, {
				tipo = "hat",
				texto = hat.nome,
				raridade = hat.raridade,
				novo = posse == nil,
			})
		end
	end

	RS.Remotes.FeedbackMina:FireClient(player, {
		tipo = "quebrou", pos = rocha.Position, chefe = ehChefe,
	})
	PlayerData.sincronizar(player)

	-- esconde e reativa (preserva barra de vida, ClickDetector e conexoes)
	local hpMax = rocha:GetAttribute("HPMax")
	local espera = ehChefe and RESPAWN_CHEFE or RESPAWN_ROCHA

	local visual = rocha.Parent and rocha.Parent:FindFirstChild("Visual")
	if visual then
		for _, d in ipairs(visual:GetDescendants()) do
			if d:IsA("BasePart") then
    d:SetAttribute("MiningVisibleTransparency",d.Transparency)
    d.Transparency=1 d.CanQuery=false
   end
		end
	end
	rocha.CanCollide = false
	rocha.CanQuery = false
	local cd = rocha:FindFirstChildOfClass("ClickDetector")
	if cd then cd.MaxActivationDistance = 0 end
	local bb = rocha:FindFirstChild("Vida")
	if bb then bb.Enabled = false end
	rocha:SetAttribute("UltimoGolpe", nil)

	task.delay(espera, function()
		if not rocha.Parent then return end
		rocha:SetAttribute("HP", hpMax)
		if visual then
			for _, d in ipairs(visual:GetDescendants()) do
				if d:IsA("BasePart") then
     d.Transparency=d:GetAttribute("MiningVisibleTransparency") or 0
     d.CanQuery=true
    end
			end
		end
		rocha.CanCollide = true
		rocha.CanQuery = true
		if cd then cd.MaxActivationDistance = ehChefe and 45 or 26 end
		if bb then bb.Enabled = ehChefe and true or false end
		atualizarBarra(rocha)
	end)
end

-- ---------- GOLPE ----------
function Mineracao.golpear(player, rocha)
 local char=player.Character
 if not Geometry.valid(rocha) or not rocha:IsDescendantOf(workspace.Areas) then return end
 if not char or not char:FindFirstChild("Picareta") or not Geometry.canReach(char,rocha) then return end
 local perfil=PlayerData.get(player)
 if not perfil then return end
 local agora=os.clock()
 if pending[player] or (ultimoGolpe[player] and agora-ultimoGolpe[player]<COOLDOWN) then return end
 if not perfil.areas[rocha:GetAttribute("AreaId")] then
  RS.Remotes.FeedbackMina:FireClient(player,{tipo="bloqueada",texto="Area bloqueada"})
  return
 end
 if not rocha:GetAttribute("Chefe") and PlayerData.mochilaCheia(perfil) then
  ultimoGolpe[player]=agora
  RS.Remotes.FeedbackMina:FireClient(player,{tipo="cheia",texto="Mochila cheia! Venda com o Ignis."})
  return
 end
 ultimoGolpe[player]=agora
 local token={}
 pending[player]=token
 local starts=workspace:GetServerTimeNow()+.05
 RS.Remotes.AnimarPicareta:FireAllClients(player,rocha,starts)
 task.delay(Geometry.ImpactTime+.05,function()
  if pending[player]~=token then return end
  pending[player]=nil
  if player.Character~=char or not char:FindFirstChild("Picareta") or not Geometry.canReach(char,rocha) then return end
  local perfil=PlayerData.get(player)
  if not perfil or (not rocha:GetAttribute("Chefe") and PlayerData.mochilaCheia(perfil)) then return end
  local hrp=char.HumanoidRootPart
	local dano = PlayerData.dano(perfil)
	local hp = rocha:GetAttribute("HP") - dano
	rocha:SetAttribute("HP", hp)

	-- acende a etiqueta so enquanto a rocha esta sendo trabalhada
	local bb = rocha:FindFirstChild("Vida")
	if bb and not rocha:GetAttribute("Chefe") then
		bb.Enabled = true
		local marca = os.clock()
		rocha:SetAttribute("UltimoGolpe", marca)
		task.delay(3, function()
			if rocha:GetAttribute("UltimoGolpe") == marca and bb then
				bb.Enabled = false
			end
		end)
	end

	atualizarBarra(rocha)
	RS.Remotes.AnimarPicareta:FireAllClients(player, rocha, workspace:GetServerTimeNow(), true, Geometry.contact(rocha, hrp.Position))

	RS.Remotes.FeedbackMina:FireClient(player, {
		tipo = "golpe", dano = dano, pos = Geometry.contact(rocha, hrp.Position),
	})

	if hp <= 0 then
		quebrar(rocha, player)
	end
 end)
end

function Mineracao.registrar(rocha)
	local cd = rocha:FindFirstChildOfClass("ClickDetector")
	if not cd then return end
	cd.MouseClick:Connect(function(player)
		Mineracao.golpear(player, rocha)
	end)
end

function Mineracao.iniciar()
	local areas = workspace:WaitForChild("Areas")
	for _, d in ipairs(areas:GetDescendants()) do
		if d:IsA("BasePart") and d:GetAttribute("HPMax") then
			Mineracao.registrar(d)
		end
	end
	game:GetService("Players").PlayerRemoving:Connect(function(p)
		ultimoGolpe[p] = nil
        pending[p] = nil
	end)
end

return Mineracao

