-- CharacterRig: pose do personagem R15 por PARAMETROS + IK analitico.
-- Todos os estados (idle, andar, correr, postura, golpe) produzem o mesmo conjunto de parametros; o blend entre
-- estados e feito nesses numeros (angulos, alturas, pontos das maos e dos pes) e o IK roda UMA vez no fim.
-- Assim a troca de estado nunca "salta": o que muda de um estado para outro e continuo por construcao.
--
-- Espaco: tudo relativo ao HumanoidRootPart (X direita, Y cima, -Z frente).
-- Motor6D: Part1.CFrame = Part0.CFrame * C0 * Transform * C1:Inverse(). Os offsets sao lidos do rig a cada frame,
-- entao a escala do avatar (altura/largura/proporcao) e respeitada.
local Rig = {}

local PARTES = {
	LowerTorso = { "Root", "HumanoidRootPart" }, UpperTorso = { "Waist", "LowerTorso" }, Head = { "Neck", "UpperTorso" },
	RightUpperArm = { "RightShoulder", "UpperTorso" }, RightLowerArm = { "RightElbow", "RightUpperArm" }, RightHand = { "RightWrist", "RightLowerArm" },
	LeftUpperArm = { "LeftShoulder", "UpperTorso" }, LeftLowerArm = { "LeftElbow", "LeftUpperArm" }, LeftHand = { "LeftWrist", "LeftLowerArm" },
	RightUpperLeg = { "RightHip", "LowerTorso" }, RightLowerLeg = { "RightKnee", "RightUpperLeg" }, RightFoot = { "RightAnkle", "RightLowerLeg" },
	LeftUpperLeg = { "LeftHip", "LowerTorso" }, LeftLowerLeg = { "LeftKnee", "LeftUpperLeg" }, LeftFoot = { "LeftAnkle", "LeftLowerLeg" },
}
Rig.PARTES = PARTES

-- parametros com angulo (autorados em graus nas tabelas, convertidos por Rig.graus)
Rig.ANGULOS = { pelvisPitch = true, pelvisYaw = true, pelvisRoll = true, chestPitch = true, chestYaw = true, chestRoll = true,
	headPitch = true, headYaw = true, footLPitch = true, footRPitch = true, haftPitch = true, haftYaw = true, haftRoll = true,
	leftArmPitch = true, leftArmRoll = true, leftElbow = true, rightArmPitch = true, rightArmRoll = true, rightElbow = true }

function Rig.graus(t)
	local o = {}
	for k, v in pairs(t) do o[k] = Rig.ANGULOS[k] and math.rad(v) or v end
	return o
end

function Rig.neutro()
	return {
		pelvisX = 0, pelvisY = 0, pelvisPitch = 0, pelvisYaw = 0, pelvisRoll = 0, chestPitch = 0, chestYaw = 0, chestRoll = 0,
		headPitch = 0, headYaw = 0, footL = Vector3.zero, footR = Vector3.zero, footLPitch = 0, footRPitch = 0,
		gripV = Vector3.new(0, -0.6, -0.4), haftPitch = math.rad(100), haftYaw = 0, haftRoll = 0, gap = 1, leftIK = 0,
		bladeN = Vector3.new(1, 0, 0), bladeW = 0.35,
		gripY = -0.05, -- onde a mao direita segura a haste (espaco do Handle); -0.05 = valor do Tool.Grip
		poleR = Vector3.new(1, -0.7, 0.5), poleL = Vector3.new(-1, -0.7, 0.5),
		leftArmPitch = 0, leftArmRoll = 0, leftElbow = math.rad(10), rightArmPitch = 0, rightArmRoll = 0, rightElbow = math.rad(10),
	}
end

-- mistura dois conjuntos de parametros (numeros e Vector3). Chaves ausentes em b ficam como em a.
function Rig.mix(a, b, w, out)
	out = out or {}
	if w <= 0 then for k, v in pairs(a) do out[k] = v end return out end
	for k, v in pairs(a) do
		local u = b[k]
		if u == nil then out[k] = v else out[k] = v + (u - v) * w end
	end
	return out
end

function Rig.copiar(a)
	local o = {}
	for k, v in pairs(a) do o[k] = v end
	return o
end

-- ---------- RIG ----------
function Rig.novo(character)
	local j = {}
	for nome, info in pairs(PARTES) do
		local parte = character:FindFirstChild(nome)
		local motor = parte and parte:FindFirstChild(info[1])
		-- avatares novos usam AnimationConstraint (C0/C1 = Attachment0/Attachment1.CFrame, mesmo Transform)
		local ok = motor and (motor:IsA("Motor6D") or (motor:IsA("AnimationConstraint") and motor.Attachment0 and motor.Attachment1))
		if not ok then return nil end
		j[nome] = { motor = motor, pai = info[2], constraint = motor:IsA("AnimationConstraint") }
	end
	return { character = character, j = j }
end

local function perpUnit(v, eixo, reserva)
	local p = v - eixo * v:Dot(eixo)
	if p.Magnitude < 1e-4 then
		p = reserva - eixo * reserva:Dot(eixo)
		if p.Magnitude < 1e-4 then p = eixo:Cross(Vector3.xAxis) end
	end
	return p.Unit
end

local function limitarRot(cf, maxAng)
	local eixo, ang = cf:ToAxisAngle()
	if ang > maxAng and eixo.Magnitude > 1e-6 then return CFrame.fromAxisAngle(eixo.Unit, maxAng) end
	return cf
end

-- IK de dois ossos com vetor de polo. S = frame da junta raiz (espaco do root). Devolve Transform das duas juntas.
-- sinal +1 cotovelo (antebraco dobra para frente), -1 joelho. dica = lado para onde a junta do meio aponta (local).
-- suave = faixa (fracao do comprimento) em que a distancia e comprimida antes da extensao total: sem isso a junta
-- trava reta e "estala" quando o alvo volta para o alcance (derivada do acos e infinita na extensao maxima).
local function doisOssos(S, jA, jB, jC, alvo, polo, sinal, minA, maxA, dica, suave)
	local AB = jA.c1:Inverse() * jB.c0
	local a, Q = AB.Position, AB.Rotation
	local b = (jB.c1:Inverse() * jC.c0).Position
	local local_ = S:PointToObjectSpace(alvo)
	local la, lb = a.Magnitude, b.Magnitude
	local Lmax = la + lb
	local d = local_.Magnitude
	local s = (suave or 0.05) * Lmax
	if d > Lmax - s then d = (Lmax - s) + s * (1 - math.exp(-(d - (Lmax - s)) / s)) end
	d = math.clamp(d, math.abs(la - lb) + 1e-3, Lmax - 1e-3)
	local u = Q:VectorToObjectSpace(a)
	local A = u.Y * b.Y + u.Z * b.Z
	local B = u.Z * b.Y - u.Y * b.Z
	local C = u.X * b.X
	local R0 = math.sqrt(A * A + B * B)
	local theta = 0
	if R0 > 1e-6 then
		local c = math.clamp(((d * d - la * la - lb * lb) * 0.5 - C) / R0, -1, 1)
		local delta = math.atan2(B, A)
		local ac = math.acos(c)
		local t1, t2 = delta + ac, delta - ac
		theta = (sinal > 0) and math.max(t1, t2) or math.min(t1, t2)
	end
	theta = math.clamp(theta, minA, maxA)
	local T2 = CFrame.Angles(theta, 0, 0)
	local K = a + Q:VectorToWorldSpace(T2:VectorToWorldSpace(b))
	local e1 = K.Unit
	local e2 = perpUnit(a, e1, dica)
	if (a - e1 * a:Dot(e1)).Magnitude < 0.04 * la then e2 = perpUnit(dica, e1, dica) end
	local f1 = local_.Magnitude > 1e-4 and local_.Unit or e1
	local f2 = perpUnit(S:VectorToObjectSpace(polo), f1, e2)
	local T1 = CFrame.fromMatrix(Vector3.zero, f1, f2, f1:Cross(f2)) * CFrame.fromMatrix(Vector3.zero, e1, e2, e1:Cross(e2)):Inverse()
	return T1, T2
end

local function eulerPose(pitch, yaw, roll) return CFrame.fromEulerAnglesYXZ(-pitch, yaw, roll) end

-- aplica os parametros no rig. Se escrever=false so calcula (usado para mirar o golpe). Devolve info util.
-- camadas (opcional): { [parte] = {cf, peso} } transforms vindos de clipes (pulo/queda/nado) misturados antes do IK dos bracos
function Rig.resolver(rig, p, escrever, camadas, bracoClipe)
	local j = rig.j
	for _, e in pairs(j) do
		local m = e.motor
		if not m.Parent then return nil end
		if e.constraint then
			local a0, a1 = m.Attachment0, m.Attachment1
			if not (a0 and a1) then return nil end
			e.c0, e.c1 = a0.CFrame, a1.CFrame
		else
			e.c0, e.c1 = m.C0, m.C1
		end
	end
	local W = { HumanoidRootPart = CFrame.identity }
	local T = {}
	local function fk(nome)
		local e = j[nome]
		W[nome] = W[e.pai] * e.c0 * T[nome] * e.c1:Inverse()
	end
	local function camada(nome, cf)
		local c = camadas and camadas[nome]
		if c and c[2] > 0 then return cf:Lerp(c[1], c[2]) end
		return cf
	end

	-- medidas de repouso (dependem so dos offsets do rig)
	local W0 = { HumanoidRootPart = CFrame.identity }
	for _, nome in ipairs({ "LowerTorso", "RightUpperLeg", "RightLowerLeg", "RightFoot", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot" }) do
		local e = j[nome]
		W0[nome] = W0[e.pai] * e.c0 * e.c1:Inverse()
	end
	local function restAnkle(lado)
		local e = j[lado .. "Foot"]
		return (W0[lado .. "LowerLeg"] * e.c0).Position
	end
	local legLen = (j.RightUpperLeg.c1:Inverse() * j.RightLowerLeg.c0).Position.Magnitude
		+ (j.RightLowerLeg.c1:Inverse() * j.RightFoot.c0).Position.Magnitude
	rig.legLen = legLen
	local armLen = (j.RightUpperArm.c1:Inverse() * j.RightLowerArm.c0).Position.Magnitude
		+ (j.RightLowerArm.c1:Inverse() * j.RightHand.c0).Position.Magnitude
	rig.armLen = armLen

	-- tronco
	T.LowerTorso = camada("LowerTorso", CFrame.new(p.pelvisX or 0, p.pelvisY, 0) * eulerPose(p.pelvisPitch, p.pelvisYaw, p.pelvisRoll)); fk("LowerTorso")
	T.UpperTorso = camada("UpperTorso", eulerPose(p.chestPitch, p.chestYaw, p.chestRoll)); fk("UpperTorso")
	T.Head = camada("Head", eulerPose(p.headPitch, p.headYaw, 0)); fk("Head")

	-- pernas: IK ate o tornozelo alvo, pe orientado no espaco do root (fica plano no chao)
	for _, lado in ipairs({ "Right", "Left" }) do
		local up, low, foot = j[lado .. "UpperLeg"], j[lado .. "LowerLeg"], j[lado .. "Foot"]
		local off = lado == "Right" and p.footR or p.footL
		local pitch = lado == "Right" and p.footRPitch or p.footLPitch
		local S = W.LowerTorso * up.c0
		local alvo = restAnkle(lado) + off
		local polo = Vector3.new(lado == "Right" and 0.25 or -0.25, 0, -1)
		local T1, T2 = doisOssos(S, up, low, foot, alvo, polo, -1, math.rad(-150), math.rad(-3), Vector3.new(0, 0, -1), 0.06)
		T[lado .. "UpperLeg"], T[lado .. "LowerLeg"] = T1, T2
		fk(lado .. "UpperLeg"); fk(lado .. "LowerLeg")
		local J3 = W[lado .. "LowerLeg"] * foot.c0
		T[lado .. "Foot"] = limitarRot(J3.Rotation:Inverse() * CFrame.Angles(pitch, 0, 0) * foot.c1.Rotation, math.rad(60))
		T[lado .. "UpperLeg"] = camada(lado .. "UpperLeg", T[lado .. "UpperLeg"])
		T[lado .. "LowerLeg"] = camada(lado .. "LowerLeg", T[lado .. "LowerLeg"])
		T[lado .. "Foot"] = camada(lado .. "Foot", T[lado .. "Foot"])
		fk(lado .. "UpperLeg"); fk(lado .. "LowerLeg"); fk(lado .. "Foot")
	end

	local chest = W.UpperTorso
	local info = { legLen = legLen, armLen = armLen }

	-- braco direito: IK ate a empunhadura da picareta (a haste passa pelo punho fechado)
	local handR = rig.character:FindFirstChild("RightHand")
	local weld = handR and handR:FindFirstChild("RightGrip")
	local sR, eR, hR = j.RightUpperArm, j.RightLowerArm, j.RightHand
	if weld and weld:IsA("Weld") then
		-- a mao desliza pela haste conforme a pose (ponta ao carregar no ombro, meio no golpe): muda so o C1 local do weld
		local wc1 = CFrame.new(0, p.gripY or weld.C1.Position.Y, 0) * weld.C1.Rotation
		if escrever then weld.C1 = wc1 end
		local S = chest * sR.c0
		local ombro = S.Position
		local grip = chest * (sR.c0.Position + p.gripV * armLen)
		local D = chest:VectorToWorldSpace(Vector3.new(math.sin(p.haftYaw) * math.cos(p.haftPitch), math.sin(p.haftPitch), -math.cos(p.haftYaw) * math.cos(p.haftPitch)))
		local polo = chest:VectorToWorldSpace(p.poleR)
		-- A mao e a ferramenta sao uma peca so (weld): a lamina (+Y da mao) sai do ANTEBRACO. Duas passadas:
		--   1) resolve o braco com uma orientacao provisoria e acha o cotovelo;
		--   2) orienta a mao pelo antebraco real (pulso neutro), puxando so um pouco (bladeW) para o plano do movimento
		--      (bladeN = normal do plano no espaco do peito; lamina = normal x haste), e resolve de novo.
		-- Os polos dos cotovelos definem onde o antebraco fica e, portanto, o plano da lamina.
		local att = weld.C0.Position
		local function montar(dica)
			local Y = perpUnit(dica, D, Vector3.yAxis)
			Y = CFrame.fromAxisAngle(D, p.haftRoll):VectorToWorldSpace(Y)
			local Z = -D
			local rot = CFrame.fromMatrix(Vector3.zero, Y:Cross(Z), Y, Z)
			return rot, (rot + (grip - rot:VectorToWorldSpace(att))) * hR.c1.Position
		end
		local rot, pulso = montar((ombro - grip) + polo * 0.6)
		local T1, T2 = doisOssos(S, sR, eR, hR, pulso, polo, 1, math.rad(4), math.rad(150), Vector3.new(0, 0, 1))
		local cotovelo = (S * T1 * sR.c1:Inverse() * eR.c0).Position
		local dica = (cotovelo - pulso).Unit
		if p.bladeW and p.bladeW > 0.001 then
			local quer = chest:VectorToWorldSpace(p.bladeN):Cross(D)
			if quer.Magnitude > 1e-3 then
				-- o sinal da lamina e livre (a cabeca e simetrica): usa o lado mais proximo do antebraco
				if quer:Dot(dica) < 0 then quer = -quer end
				dica = dica:Lerp(quer.Unit, math.clamp(p.bladeW, 0, 1))
			end
		end
		rot, pulso = montar(dica)
		T1, T2 = doisOssos(S, sR, eR, hR, pulso, polo, 1, math.rad(4), math.rad(150), Vector3.new(0, 0, 1))
		T.RightUpperArm, T.RightLowerArm = T1, T2
		fk("RightUpperArm"); fk("RightLowerArm")
		local J3 = W.RightLowerArm * hR.c0
		-- R15 nao tem torcao de antebraco: a pronacao/supinacao que sobra vai para o pulso
		T.RightHand = limitarRot(J3.Rotation:Inverse() * rot * hR.c1.Rotation, math.rad(150))
		if bracoClipe and bracoClipe > 0 and camadas then
			for _, n in ipairs({ "RightUpperArm", "RightLowerArm", "RightHand" }) do T[n] = camada(n, T[n]) end
			fk("RightUpperArm"); fk("RightLowerArm")
		end
		fk("RightHand")
		local handle = W.RightHand * weld.C0 * wc1:Inverse()
		info.handle = handle
		info.gripHandleY = wc1.Position.Y

		-- braco esquerdo: IK ate a haste (acima da mao direita, distancia = gap), misturado com o FK livre
		local sL, eL, hL = j.LeftUpperArm, j.LeftLowerArm, j.LeftHand
		T.LeftUpperArm = CFrame.Angles(p.leftArmPitch, 0, p.leftArmRoll)
		T.LeftLowerArm = CFrame.Angles(p.leftElbow, 0, 0)
		T.LeftHand = CFrame.identity
		if p.leftIK > 0.001 then
			local SL = chest * sL.c0
			local gripL = handle * (wc1.Position + Vector3.new(0, p.gap, 0))
			local DL = handle.UpVector
			local poloL = chest:VectorToWorldSpace(p.poleL)
			local attL = handR.Parent:FindFirstChild("LeftHand") and handR.Parent.LeftHand:FindFirstChild("LeftGripAttachment")
			local attPos = attL and attL.Position or Vector3.new(0, -0.15, 0)
			-- mesma ideia da direita: segunda passada alinha a mao com o antebraco real (punho neutro na haste)
			local function montarL(dica)
				local YL = perpUnit(dica, DL, Vector3.yAxis)
				local ZL = -DL
				local r = CFrame.fromMatrix(Vector3.zero, YL:Cross(ZL), YL, ZL)
				return r, (r + (gripL - r:VectorToWorldSpace(attPos))) * hL.c1.Position
			end
			local rotL, pulsoL = montarL((SL.Position - gripL) + poloL * 0.6)
			local L1, L2 = doisOssos(SL, sL, eL, hL, pulsoL, poloL, 1, math.rad(4), math.rad(150), Vector3.new(0, 0, 1))
			rotL, pulsoL = montarL((SL * L1 * sL.c1:Inverse() * eL.c0).Position - pulsoL)
			L1, L2 = doisOssos(SL, sL, eL, hL, pulsoL, poloL, 1, math.rad(4), math.rad(150), Vector3.new(0, 0, 1))
			local w = math.clamp(p.leftIK, 0, 1)
			T.LeftUpperArm = T.LeftUpperArm:Lerp(L1, w)
			T.LeftLowerArm = T.LeftLowerArm:Lerp(L2, w)
			fk("LeftUpperArm"); fk("LeftLowerArm")
			local J3L = W.LeftLowerArm * hL.c0
			T.LeftHand = CFrame.identity:Lerp(limitarRot(J3L.Rotation:Inverse() * rotL * hL.c1.Rotation, math.rad(150)), w)
			fk("LeftHand")
			info.leftGrip = gripL
			info.leftPalm = W.LeftHand * attPos
		else
			fk("LeftUpperArm"); fk("LeftLowerArm"); fk("LeftHand")
		end
	else
		-- sem picareta: bracos soltos em FK
		T.RightUpperArm = CFrame.Angles(p.rightArmPitch, 0, p.rightArmRoll)
		T.RightLowerArm = CFrame.Angles(p.rightElbow, 0, 0)
		T.RightHand = CFrame.identity
		T.LeftUpperArm = CFrame.Angles(p.leftArmPitch, 0, p.leftArmRoll)
		T.LeftLowerArm = CFrame.Angles(p.leftElbow, 0, 0)
		T.LeftHand = CFrame.identity
		for _, n in ipairs({ "RightUpperArm", "RightLowerArm", "RightHand", "LeftUpperArm", "LeftLowerArm", "LeftHand" }) do fk(n) end
	end
	-- bracos vindos de clipe (nado/escalada)
	if bracoClipe and bracoClipe > 0 and camadas then
		for _, n in ipairs({ "LeftUpperArm", "LeftLowerArm", "LeftHand" }) do T[n] = camada(n, T[n]) end
		if not weld then for _, n in ipairs({ "RightUpperArm", "RightLowerArm", "RightHand" }) do T[n] = camada(n, T[n]) end end
	end

	info.W = W
	info.T = T
	if escrever then
		for nome, cf in pairs(T) do j[nome].motor.Transform = cf end
	end
	return info
end

return Rig

