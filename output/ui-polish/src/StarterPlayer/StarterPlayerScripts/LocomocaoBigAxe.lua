-- Animacao do corpo de TODOS os personagens visiveis (roda local em cada cliente, nada replica).
-- Idle, andar, correr, postura de mineracao e golpe sao PROCEDURAIS (CharacterRig): cada estado gera parametros,
-- o blend entre estados acontece nesses parametros e o IK roda uma vez no fim do frame.
--   - pernas: IK ate o pe alvo. No apoio o pe recua exatamente na velocidade do corpo => sem foot sliding.
--   - braco direito: IK ate a empunhadura da picareta; esquerdo livre (balanco) ou IK na haste (postura/golpe).
-- Pulo, queda, escalada e nado continuam vindo dos KeyframeSequences do Big Axe, como camada misturada.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local RS = game:GetService("ReplicatedStorage")
local Rig = require(RS:WaitForChild("CharacterRig"))
local Anim = require(RS:WaitForChild("MiningAnimations"))
local Swing = require(RS:WaitForChild("MiningSwing"))
local Geometry = require(RS:WaitForChild("MiningGeometry"))
local sequences = RS:WaitForChild("BigAxeKeyframes")

local V, rad, sin, cos, pi = Vector3.new, math.rad, math.sin, math.cos, math.pi
local function lerp(a, b, t) return a + (b - a) * t end
local function smooth(a) a = math.clamp(a, 0, 1) return a * a * (3 - 2 * a) end
local function aproximar(atual, alvo, taxa, dt) return atual + (alvo - atual) * (1 - math.exp(-taxa * dt)) end

-- ---------- CLIPES (so estados aereos / agua / escada) ----------
local clips = {}
for _, sequence in ipairs(sequences:GetChildren()) do
	if sequence:IsA("KeyframeSequence") then
		local clip = { channels = {}, length = 0 }
		for _, frame in ipairs(sequence:GetKeyframes()) do
			clip.length = math.max(clip.length, frame.Time)
			for _, pose in ipairs(frame:GetDescendants()) do
				if pose:IsA("Pose") then
					local keys = clip.channels[pose.Name] or {}
					clip.channels[pose.Name] = keys
					table.insert(keys, { time = frame.Time, cf = pose.CFrame, weight = pose.Weight })
				end
			end
		end
		for _, keys in pairs(clip.channels) do table.sort(keys, function(a, b) return a.time < b.time end) end
		clips[sequence.Name] = clip
	end
end
-- clipes do bundle sao baked a 30 fps: interpolacao linear entre keys densas preserva a curva original
-- (smoothstep por segmento criaria um "para-e-anda" a cada 33 ms)
local function sample(keys, time)
	if time <= keys[1].time then return keys[1].cf end
	local lo, hi = 1, #keys
	while lo < hi do
		local mid = (lo + hi) // 2
		if keys[mid].time < time then lo = mid + 1 else hi = mid end
	end
	local b, a = keys[lo], keys[math.max(1, lo - 1)]
	local alpha = math.clamp((time - a.time) / math.max(1e-4, b.time - a.time), 0, 1)
	return a.cf:Lerp(b.cf, alpha)
end

-- ---------- POSES PROCEDURAIS ----------
-- distancias autoradas para uma perna de 2.2 studs; escaladas pelo rig no fim
local PERNA_REF = 2.2

local function idle(st, tau)
	-- respiracao ~14/min (4.2 s) + ruido lento de peso e olhar: nunca repete de forma perceptivel
	local br = sin(2 * pi * tau / 4.2)
	local br2 = sin(2 * pi * tau / 4.2 - 0.9)       -- peito e bracos atrasados (overlap)
	local sw = math.noise(tau * 0.11, st.seed)
	local sw2 = math.noise(tau * 0.16, st.seed + 3.1)
	local look = math.noise(tau * 0.07, st.seed + 7.7)
	return {
		pelvisX = 0.04 * sw, pelvisY = -0.06 + 0.006 * br, pelvisPitch = rad(2), pelvisYaw = rad(4) * sw2, pelvisRoll = rad(3) * sw,
		chestPitch = rad(2.5) - rad(1.3) * br2, chestYaw = -rad(2.8) * sw2, chestRoll = -rad(1.8) * sw,
		headPitch = rad(-3) + rad(0.8) * br, headYaw = rad(6) * look,
		footL = V(-0.05, 0, -0.14), footR = V(0.05, 0, 0.1), footLPitch = 0, footRPitch = 0,
		-- picareta atravessada nos ombros (referencia do minerador): haste horizontal apoiada no alto das costas,
		-- mao direita erguida perto da ponta, cabeca da picareta alem do ombro esquerdo, lamina vertical, cotovelo baixo a frente
		gripV = V(0.18, 0.02 + 0.008 * br2, 0.27), haftPitch = rad(3), haftYaw = rad(-90), haftRoll = 0, gap = -0.8, leftIK = 0,
		gripY = -0.75, bladeN = V(0, 0, 1), bladeW = 0.9,
		poleR = V(0.3, -1, -0.6), poleL = V(-1, -0.8, 0.4),
		leftArmPitch = rad(3) + rad(1.5) * br2, leftArmRoll = rad(-5), leftElbow = rad(12) + rad(2) * br2,
		rightArmPitch = rad(3) + rad(1.5) * br2, rightArmRoll = rad(5), rightElbow = rad(12),
	}
end

local function ready(tau)
	local p = Rig.copiar(Anim.READY)
	local br = sin(2 * pi * tau / 3.4)
	p.pelvisY += 0.008 * br
	p.chestPitch -= rad(1.2) * sin(2 * pi * tau / 3.4 - 0.8)
	p.gripV += V(0, 0.01 * br, 0)
	p.pelvisX = 0
	return p
end

-- ciclo de passada: fase avanca pela DISTANCIA percorrida (cadencia sai da velocidade)
local function gait(st, dt, speed, dir, legLen)
	local g = st.g
	local s = legLen / PERNA_REF
	local duty = lerp(0.6, 0.3, g)                         -- fracao do ciclo com o pe no chao
	local maxStance = legLen * lerp(0.7, 1.1, g)          -- dentro do alcance da perna (pelve abaixa junto)
	local f = math.max(lerp(0.8, 1.5, g), speed * duty / maxStance)  -- ciclos/s (2 passos por ciclo)
	st.phase = (st.phase + dt * f) % 1
	st.cadencia = f
	local Ls = speed * duty / f                            -- comprimento do apoio: pe recua a 'speed' => sem deslizar
	local lift = legLen * lerp(0.09, 0.22, g)
	local ph = st.phase
	local toeOff = rad(lerp(16, 26, g))
	local heel = rad(lerp(10, 4, g))
	local function pe(off, lado)
		local u = (ph + off) % 1
		local along, h, pitch
		if u < duty then
			local a = u / duty
			along, h = Ls * (0.5 - a), 0
			pitch = lerp(heel, -toeOff, smooth(a))
		else
			-- balanco: Hermite com a MESMA velocidade do apoio nas duas pontas (sem quina ao tirar/pousar o pe)
			local a = (u - duty) / (1 - duty)
			-- tangente reduzida (35%): com a velocidade cheia a curva passaria 30% alem do alcance da perna na corrida
			local m = -Ls / duty * (1 - duty) * 0.35
			local a2, a3 = a * a, a * a * a
			along = (2 * a3 - 3 * a2 + 1) * (-0.5 * Ls) + (a3 - 2 * a2 + a) * m + (-2 * a3 + 3 * a2) * (0.5 * Ls) + (a3 - a2) * m
			h = lift * sin(pi * a)
			pitch = lerp(-toeOff, heel, smooth(a))
		end
		return (dir * along + V(lado * 0.05 * g, h, 0)) / s, pitch
	end
	local fL, pL = pe(0, 1)
	local fR, pR = pe(0.5, -1)
	local c = lerp(0, duty / 2, g)
	local A = legLen * lerp(0.022, 0.025, g)
	local pelvisYaw = -rad(lerp(6, 9, g)) * cos(2 * pi * ph)
	local pelvisRoll = rad(lerp(3, 2, g)) * sin(2 * pi * ph)
	local pelvisPitch = rad(lerp(2, 7, g))
	local chestPitch = rad(lerp(4, 13, g))
	local chestYaw = -1.15 * pelvisYaw
	local armPh = 2 * pi * (ph - 0.05)                     -- braco atrasa um pouco a perna (overlap)
	local armAmp = rad(lerp(22, 55, g))
	local elbow = rad(lerp(14, 80, g)) + rad(lerp(8, 18, g)) * (0.5 - 0.5 * cos(armPh))
	return {
		pelvisX = 0, pelvisY = (-legLen * lerp(0.09, 0.15, g) - A * cos(4 * pi * (ph - c))) / s,
		pelvisPitch = pelvisPitch, pelvisYaw = pelvisYaw, pelvisRoll = pelvisRoll,
		chestPitch = chestPitch, chestYaw = chestYaw, chestRoll = -0.5 * pelvisRoll,
		headPitch = -(pelvisPitch + chestPitch) * 0.65, headYaw = -0.8 * (pelvisYaw + chestYaw),
		footL = fL, footR = fR, footLPitch = pL, footRPitch = pR,
		-- carregando no ombro; o quique acompanha a pelve com atraso (overlap)
		gripV = V(0.18, 0.02 + lerp(0.01, 0.02, g) * cos(4 * pi * (ph - c - 0.08)), 0.27),
		haftPitch = rad(3) + rad(lerp(1, 3, g)) * cos(4 * pi * (ph - c - 0.12)), haftYaw = rad(-90), haftRoll = 0, gap = -0.8, leftIK = 0,
		gripY = -0.75, bladeN = V(0, 0, 1), bladeW = 0.9,
		poleR = V(0.3, -1, -0.6), poleL = V(-1, -0.8, 0.4),
		leftArmPitch = -armAmp * cos(armPh), leftArmRoll = -rad(lerp(4, 9, g)), leftElbow = elbow,
		rightArmPitch = armAmp * cos(armPh), rightArmRoll = rad(lerp(4, 9, g)), rightElbow = elbow,
	}
end

-- ---------- PERSONAGENS ----------
local characters = {}
local playerConnections = {}

local function detach(character)
	local st = characters[character]
	if not st then return end
	for _, c in ipairs(st.connections) do c:Disconnect() end
	characters[character] = nil
end

local function attach(character)
	if characters[character] then return end
	local st = { connections = {}, phase = 0, g = 0, moveW = 0, readyW = 0, clipW = 0, clipTime = 0, tau = math.random() * 50,
		seed = math.random() * 100, speedPrev = 0, acc = 0, legLen = PERNA_REF }
	characters[character] = st
	task.spawn(function()
		local humanoid = character:WaitForChild("Humanoid", 15)
		local root = character:WaitForChild("HumanoidRootPart", 15)
		if characters[character] ~= st or not humanoid or not root then return end
		if humanoid.RigType ~= Enum.HumanoidRigType.R15 then
			character:SetAttribute("LocomotionAnimationStatus", "DefaultR6")
			return
		end
		-- o jogo controla toda a animacao do corpo: pacotes de animacao do avatar nao podem misturar
		local function disableAvatarAnimate(child)
			if child.Name == "Animate" and child:IsA("LocalScript") then child.Disabled = true end
		end
		for _, child in ipairs(character:GetChildren()) do disableAvatarAnimate(child) end
		table.insert(st.connections, character.ChildAdded:Connect(disableAvatarAnimate))
		local animator = humanoid:FindFirstChildOfClass("Animator") or humanoid:WaitForChild("Animator", 5)
		if animator then
			for _, track in ipairs(animator:GetPlayingAnimationTracks()) do track:Stop(0) end
			table.insert(st.connections, animator.AnimationPlayed:Connect(function(track) track:Stop(0) end))
		end
		character:SetAttribute("GameAnimationsOnly", true)
		table.insert(st.connections, humanoid.StateChanged:Connect(function(_, novo)
			if novo == Enum.HumanoidStateType.Landed then st.land = os.clock() end
		end))
		-- rig pronto quando todos os Motor6D existem (aparencia do avatar carrega depois)
		for _ = 1, 60 do
			st.rig = Rig.novo(character)
			if st.rig or characters[character] ~= st then break end
			task.wait(0.25)
		end
		st.humanoid, st.root = humanoid, root
		character:SetAttribute("LocomotionAnimationStatus", st.rig and "Procedural" or "SemRig")
	end)
end

local function clipDe(st)
	local h, root = st.humanoid, st.root
	local kind = h:GetState()
	local vel = root.AssemblyLinearVelocity
	if kind == Enum.HumanoidStateType.Jumping then return "jump", 1 end
	if kind == Enum.HumanoidStateType.Freefall then
		if st.clipName == "jump" and st.clipTime < 0.3 then return "jump", 1 end
		return "fall", 1
	end
	if kind == Enum.HumanoidStateType.Climbing then return "climb", math.clamp(vel.Y / 5, -3, 3) end
	if kind == Enum.HumanoidStateType.Swimming then
		if vel.Magnitude > 0.6 then return "swim", math.clamp(vel.Magnitude / 10, 0.2, 3) end
		return "swimidle", 1
	end
	return nil
end

local function querPostura(character, st)
	if os.clock() < (st.readyUntil or 0) then return true end
	local owner = Players:GetPlayerFromCharacter(character)
	return owner == Players.LocalPlayer and owner:GetAttribute("MiningTargetSelected") == true and character:FindFirstChild("Picareta") ~= nil
end

local function intervaloDe(character)
	local owner = Players:GetPlayerFromCharacter(character)
	return owner and owner:GetAttribute("IntervaloGolpe") or 0.8
end

local ESCALAVEIS = { "pelvisX", "pelvisY", "footL", "footR" }
local function escalar(p, s)
	local o = Rig.copiar(p)
	for _, k in ipairs(ESCALAVEIS) do if o[k] then o[k] = o[k] * s end end
	return o
end

-- mira do golpe: ajusta o angulo da haste para a cabeca da picareta chegar na altura do ponto de contato da rocha
local function mirar(st, character, golpe)
	local ativo = Swing.Ativo(character)
	local hit = ativo and ativo.hit
	st.mira = 0
	if not (hit and Geometry.valid(hit)) then return golpe end
	local s = st.legLen / PERNA_REF
	local d = 0
	for _ = 1, 2 do
		local info = Rig.resolver(st.rig, escalar(Anim.mirado(golpe, d).contato, s), false)
		if not (info and info.handle) then return golpe end
		local head = info.handle * V(0, Anim.CABECA_Y, 0)
		local grip = info.handle * V(0, info.gripHandleY, 0)
		local L = (head - grip).Magnitude
		-- cabeca da picareta entra na face da rocha um pouco abaixo do ponto de contato: haste desce ~30 graus
		local contato = Geometry.contact(hit, st.root.Position)
		local yMin = hit.Position.Y - hit.Size.Y * 0.5 + 0.3
		local alvo = st.root.CFrame:PointToObjectSpace(Vector3.new(contato.X, math.max(yMin, contato.Y - 0.4), contato.Z))
		local atual = math.asin(math.clamp((head.Y - grip.Y) / L, -1, 1))
		local quer = math.asin(math.clamp((alvo.Y - grip.Y) / L, -0.97, 0.5))
		d = math.clamp(d + (quer - atual), rad(-35), rad(25))
	end
	st.mira = d
	return Anim.mirado(golpe, d)
end

RunService.PreSimulation:Connect(function(dt)
	local cam = workspace.CurrentCamera
	local camPos = cam and cam.CFrame.Position
	for character, st in pairs(characters) do
		local rig, h, root = st.rig, st.humanoid, st.root
		if not (rig and h and root and root.Parent) then continue end
		if h.Health <= 0 or h.Sit or h.PlatformStand then continue end
		st.tau += dt

		-- LOD: longe da camera recalcula a 20 Hz e reescreve o ultimo resultado nos outros frames
		local longe = camPos and (root.Position - camPos).Magnitude > 150
		st.frame = (st.frame or 0) + 1
		if longe and st.ultimoT and st.frame % 3 ~= 0 then
			for nome, cf in pairs(st.ultimoT) do
				local e = rig.j[nome]
				if e and e.motor.Parent then e.motor.Transform = cf end
			end
			continue
		end
		local passo = longe and dt * 3 or dt

		-- ---------- ENTRADAS ----------
		local vel = root.AssemblyLinearVelocity
		local flat = V(vel.X, 0, vel.Z)
		local speed = flat.Magnitude
		local dirLocal = speed > 0.05 and root.CFrame:VectorToObjectSpace(flat).Unit or V(0, 0, -1)
		local clipName, rate = clipDe(st)
		local noChao = clipName == nil
		-- o Humanoid para/arranca em 1 frame: a passada usa a velocidade suavizada (~0.15 s), senao os pes pulam
		st.speedS = aproximar(st.speedS or speed, speed, 7, passo)
		st.moveW = aproximar(st.moveW, noChao and math.clamp((st.speedS - 0.4) / 2.0, 0, 1) or 0, st.moveW < 0.5 and 10 or 8, passo)
		-- blend andar -> correr entre 4 e 12 studs/s (pernas curtas: 8 studs/s ja e trote)
		st.g = aproximar(st.g, smooth((speed - 4) / 8), 5, passo)
		st.acc = aproximar(st.acc, (speed - st.speedPrev) / math.max(passo, 1e-3), 6, passo)
		st.speedPrev = speed
		local legLen = st.legLen

		-- ---------- PARAMETROS DO CHAO ----------
		local p = idle(st, st.tau)
		if st.moveW > 0.001 then
			if speed > 0.5 then st.dirG = V(dirLocal.X, 0, dirLocal.Z) end
			p = Rig.mix(p, gait(st, passo, st.speedS, st.dirG or V(0, 0, -1), legLen), st.moveW)
			-- inclinacao por aceleracao e curva
			p.chestPitch += math.clamp(st.acc * 0.006, rad(-6), rad(8)) * st.moveW
			p.chestRoll += math.clamp(-root.AssemblyAngularVelocity.Y * speed * 0.0025, rad(-7), rad(7)) * st.moveW
		end

		-- postura de mineracao (so parado; andando, a picareta volta ao ombro)
		local querReady = querPostura(character, st) and noChao
		st.readyW = aproximar(st.readyW, querReady and 1 or 0, querReady and 14 or (4.5 / Anim.RELAXAR), passo)
		local wReady = smooth(st.readyW) * (1 - st.moveW)
		if wReady > 0.001 then p = Rig.mix(p, ready(st.tau), wReady) end

		-- ---------- GOLPE ----------
		local sampledSwingTime
		local mining = character:GetAttribute("MiningSwingActive") == true and character:FindFirstChild("Picareta") ~= nil
		local startedAt = character:GetAttribute("MiningSwingStart")
		if mining and startedAt then
			if startedAt ~= st.swingStart then
				if not st.lastSwing or startedAt - st.lastSwing > Anim.COMBO_RESET then st.combo = 0 end
				st.combo = (st.combo or 0) % #Anim.SEQUENCIA + 1
				local golpe = Anim.GOLPES[Anim.SEQUENCIA[st.combo]]
				st.swingStart, st.lastSwing = startedAt, startedAt
				st.fim = Anim.fimRecuperacao(intervaloDe(character))
				st.swingFrom = Rig.copiar(st.pLast or p)
				st.golpe = mirar(st, character, golpe)
				character:SetAttribute("MiningComboGolpe", golpe.nome)
			end
			local t = math.max(0, workspace:GetServerTimeNow() - st.swingStart)
			sampledSwingTime = t
			p = Anim.amostrar(st.golpe, t, st.swingFrom, st.fim)
			st.readyUntil = os.clock() + Anim.READY_SEGURA
			st.readyW = 1
		end

		-- aterrissagem: a pelve afunda e o IK dobra os joelhos
		if st.land then
			local a = (os.clock() - st.land) / 0.26
			if a < 1 then
				local k = (1 - a) ^ 2
				p.pelvisY -= 0.22 * k
				p.chestPitch += rad(7) * k
			else
				st.land = nil
			end
		end
		st.pLast = p

		-- ---------- CLIPES (ar / agua / escada) ----------
		local camadas, bracoClipe
		if clipName then
			if clipName ~= st.clipName then st.clipName, st.clipTime = clipName, 0 end
			local clip = clips[clipName]
			if clip then
				st.clipTime += passo * rate
				if clipName == "jump" or clipName == "fall" then st.clipTime = math.min(st.clipTime, clip.length)
				else st.clipTime %= clip.length end
			end
		end
		st.clipW = aproximar(st.clipW, clipName and 1 or 0, clipName and 11 or 8, passo)
		if st.clipW > 0.01 and st.clipName and clips[st.clipName] then
			local clip = clips[st.clipName]
			camadas = {}
			for nome in pairs(rig.j) do
				local keys = clip.channels[nome]
				if keys then camadas[nome] = { sample(keys, st.clipTime), st.clipW } end
			end
			bracoClipe = (st.clipName == "climb" or st.clipName == "swim" or st.clipName == "swimidle") and st.clipW or 0
		end
		local label = (mining and "mine") or clipName or (wReady > 0.5 and "ready") or (st.moveW > 0.5 and (st.g > 0.5 and "run" or "walk")) or "idle"
		if st.label ~= label then st.label = label character:SetAttribute("BigAxeAnimationState", label) end

		-- ---------- IK ----------
		local info = Rig.resolver(rig, escalar(p, legLen / PERNA_REF), true, camadas, bracoClipe)
		if info then
			st.legLen = info.legLen
			st.ultimoT = info.T
			st.handle = info.handle
		end
		if mining and startedAt and sampledSwingTime then Swing.Advance(character,sampledSwingTime) end
	end
end)

local function watch(player)
	local connections = {}
	playerConnections[player] = connections
	table.insert(connections, player.CharacterAdded:Connect(attach))
	table.insert(connections, player.CharacterRemoving:Connect(detach))
	if player.Character then attach(player.Character) end
end
Players.PlayerAdded:Connect(watch)
Players.PlayerRemoving:Connect(function(player)
	if player.Character then detach(player.Character) end
	for _, connection in ipairs(playerConnections[player] or {}) do connection:Disconnect() end
	playerConnections[player] = nil
end)
for _, player in ipairs(Players:GetPlayers()) do watch(player) end

