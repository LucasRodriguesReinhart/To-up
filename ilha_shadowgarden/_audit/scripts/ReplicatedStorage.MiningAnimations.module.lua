-- MiningAnimations: golpe de picareta autorado como TRAJETORIA DA FERRAMENTA + postura do corpo (parametros do CharacterRig).
-- Durante o golpe, os bracos sao resolvidos por IK ate a haste: a mao direita fica na base da empunhadura e a
-- esquerda desliza pela haste (afastada na preparacao, junto da direita no impacto), como no golpe real de picareta.
--
-- Anatomia (segundos desde o inicio que o SERVIDOR usa para o dano):
--   0.00 pose atual -> 0.13 PREPARACAO (ease-out: sobe rapido e "pendura" no topo)
--   -> 0.28 CONTATO (ease-in: acelera ate o impacto; instante do dano, som e VFX)
--   -> 0.325 hit stop (pose segura) -> 0.38 FOLLOW-THROUGH (ease-out, a cabeca continua para dentro da rocha)
--   -> fim RECUPERACAO (ease-in-out) ate a pose idle do frame, que e cancelavel pelo proximo golpe.
-- Pes plantados durante todo o golpe: so a pelve sobe/desce e gira (o IK das pernas dobra os joelhos).
local RS = game:GetService("ReplicatedStorage")
local Rig = require(RS:WaitForChild("CharacterRig"))
local M = {}

M.PREPARACAO = 0.13
M.CONTATO = 0.28          -- deve bater com MiningGeometry.ImpactTime (servidor)
M.HIT_STOP = 0.045
M.FOLLOW = 0.38
M.RECUPERACAO_MAX = 0.62
M.RECUPERACAO_MIN = 0.58
M.COMBO_RESET = 1.6
M.TRAIL_INICIO = 0.15
M.TRAIL_FIM = 0.34
M.CABECA_Y = 1.75         -- centro da cabeca da picareta no espaco do Handle (modelos Blender: 1.7 a 1.9)

local V = Vector3.new
local PES = { footL = V(-0.08, 0, -0.55), footR = V(0.12, 0, 0.38), footLPitch = 0, footRPitch = 0 }
local function pose(t)
	for k, v in pairs(PES) do if t[k] == nil then t[k] = v end end
	return Rig.mix(Rig.neutro(), Rig.graus(t), 1)
end

-- Alvos da empunhadura e polos dos cotovelos mantem as maos a frente do peito no contato.
-- A mao direita guia a haste; gap negativo coloca a esquerda mais perto da base. A mira vertical
-- do contato continua sendo corrigida pelo LocomocaoBigAxe conforme a altura real da rocha.

-- A: diagonal (sobe sobre o ombro direito, tronco torce para a direita e desenrola no impacto)
local A = {
	nome = "diagonal", forca = 1, arco = V(0.02, 0.16, -0.12),
	wind = pose({
		pelvisY = -0.06, pelvisPitch = 0, pelvisYaw = -24, pelvisRoll = -2, chestPitch = -6, chestYaw = -30, chestRoll = -6,
		headPitch = 6, headYaw = 26,
		gripV = V(-0.17, 0.65, -0.20), haftPitch = 138, haftYaw = -77, gap = -0.75, leftIK = 1, bladeN = V(1, 0.25, 0),
		poleR = V(1, 0, -0.7), poleL = V(-1, 0, -0.8),
	}),
	contato = pose({
		pelvisY = -0.26, pelvisPitch = 10, pelvisYaw = 2, pelvisRoll = 2, chestPitch = 16, chestYaw = 4, chestRoll = 3,
		headPitch = -14, headYaw = -2,
		gripV = V(-0.41, -0.17, -0.84), haftPitch = -5, haftYaw = 6, gap = -0.36, leftIK = 1, bladeN = V(1, 0.25, 0),
		poleR = V(0.8, -0.3, -1), poleL = V(-0.8, -0.3, -1),
	}),
	follow = pose({
		pelvisY = -0.29, pelvisPitch = 12, pelvisYaw = 5, pelvisRoll = 2, chestPitch = 20, chestYaw = 10, chestRoll = 4,
		headPitch = -16, headYaw = -4,
		gripV = V(-0.19, -0.16, -0.74), haftPitch = -11, haftYaw = 20, gap = -0.36, leftIK = 1, bladeN = V(1, 0.25, 0),
		poleR = V(0.8, -0.3, -1), poleL = V(-0.8, -0.3, -1),
	}),
}

-- B: vertical pesado (mais alto e reto por cima da cabeca, agacha mais)
local B = {
	nome = "vertical", forca = 1.35, arco = V(0, 0.2, -0.15),
	wind = pose({
		pelvisY = -0.02, pelvisPitch = -4, pelvisYaw = -8, chestPitch = -14, chestYaw = -10, chestRoll = -2,
		headPitch = 12, headYaw = 8,
		gripV = V(-0.23, 0.62, -0.36), haftPitch = 124, haftYaw = -30, gap = -0.75, leftIK = 1,
		poleR = V(1, 0, -0.7), poleL = V(-1, 0, -0.8),
	}),
	contato = pose({
		pelvisY = -0.34, pelvisPitch = 12, pelvisYaw = 0, chestPitch = 22, chestYaw = 2, chestRoll = 1,
		headPitch = -18, headYaw = 0,
		gripV = V(-0.48, -0.06, -0.72), haftPitch = 0, haftYaw = 2, gap = -0.36, leftIK = 1,
		poleR = V(0.8, -0.3, -1), poleL = V(-0.8, -0.3, -1),
	}),
	follow = pose({
		pelvisY = -0.38, pelvisPitch = 14, pelvisYaw = 0, chestPitch = 26, chestYaw = 3, chestRoll = 1,
		headPitch = -20, headYaw = 0,
		gripV = V(-0.46, 0.04, -0.68), haftPitch = -8, haftYaw = 2, gap = -0.36, leftIK = 1,
		poleR = V(0.8, -0.3, -1), poleL = V(-0.8, -0.3, -1),
	}),
}

-- C: lateral (varredura baixa vinda da direita, arco horizontal)
local C = {
	nome = "lateral", forca = 0.9, arco = V(0.1, 0.05, -0.2),
	wind = pose({
		pelvisY = -0.10, pelvisPitch = 2, pelvisYaw = -30, pelvisRoll = -2, chestPitch = 2, chestYaw = -38, chestRoll = -4,
		headPitch = 4, headYaw = 32,
		gripV = V(0, -0.36, -0.77), haftPitch = 21, haftYaw = 51, gap = -0.75, leftIK = 1, bladeN = V(-0.3, -1, 0),
		poleR = V(1, 0, -0.7), poleL = V(-1, 0, -0.8),
	}),
	contato = pose({
		pelvisY = -0.24, pelvisPitch = 8, pelvisYaw = 4, pelvisRoll = 2, chestPitch = 12, chestYaw = 6, chestRoll = 3,
		headPitch = -10, headYaw = -6,
		gripV = V(-0.37, -0.44, -0.82), haftPitch = 5, haftYaw = 30, gap = -0.40, leftIK = 1, bladeN = V(-0.3, -1, 0),
		poleR = V(0.8, -0.3, -1), poleL = V(-0.8, -0.3, -1),
	}),
	follow = pose({
		pelvisY = -0.26, pelvisPitch = 9, pelvisYaw = 8, pelvisRoll = 2, chestPitch = 14, chestYaw = 10, chestRoll = 3,
		headPitch = -10, headYaw = -10,
		gripV = V(-0.33, -0.43, -0.73), haftPitch = 8, haftYaw = 30, gap = -0.40, leftIK = 1, bladeN = V(-0.3, -1, 0),
		poleR = V(0.8, -0.3, -1), poleL = V(-0.8, -0.3, -1),
	}),
}

M.GOLPES = { A, B, C }
-- ritmo do combo: diagonal, vertical, diagonal, lateral
M.SEQUENCIA = { 1, 2, 1, 3 }

-- ---------- CURVAS ----------
local function easeOut(a) return 1 - (1 - a) ^ 3 end
local function easeIn(a) return a ^ 2.4 end
local function easeInOut(a) return a * a * (3 - 2 * a) end
M.easeOut, M.easeIn, M.easeInOut = easeOut, easeIn, easeInOut

function M.fimRecuperacao(intervalo)
	return math.clamp((intervalo or 0.8) - 0.03, M.RECUPERACAO_MIN, M.RECUPERACAO_MAX)
end

-- golpe com a mira aplicada (correcao do angulo da haste/tronco no contato)
function M.mirado(golpe, dPitch)
	if math.abs(dPitch) < 1e-3 then return golpe end
	local g = { nome = golpe.nome, forca = golpe.forca, arco = golpe.arco, wind = golpe.wind }
	g.contato = Rig.copiar(golpe.contato)
	g.follow = Rig.copiar(golpe.follow)
	for _, k in ipairs({ "contato", "follow" }) do
		g[k].haftPitch += dPitch
		g[k].chestPitch -= dPitch * 0.35
		g[k].headPitch -= dPitch * 0.3
		g[k].pelvisY += math.min(0, dPitch) * 0.25
	end
	return g
end

-- parametros no tempo t do golpe. de = parametros do personagem quando o golpe comecou.
function M.amostrar(golpe, t, de, fim, destino, out)
	out = out or {}
	if t < M.PREPARACAO then
		return Rig.mix(de, golpe.wind, easeOut(t / M.PREPARACAO), out)
	elseif t < M.CONTATO then
		local e = easeIn((t - M.PREPARACAO) / (M.CONTATO - M.PREPARACAO))
		Rig.mix(golpe.wind, golpe.contato, e, out)
		out.gripV += golpe.arco * math.sin(math.pi * e)
		return out
	elseif t < M.CONTATO + M.HIT_STOP then
		return Rig.mix(golpe.contato, golpe.contato, 0, out)
	elseif t < M.FOLLOW then
		return Rig.mix(golpe.contato, golpe.follow, easeOut((t - M.CONTATO - M.HIT_STOP) / (M.FOLLOW - M.CONTATO - M.HIT_STOP)), out)
	end
	return Rig.mix(golpe.follow, destino, easeInOut(math.clamp((t - M.FOLLOW) / math.max(0.05, fim - M.FOLLOW), 0, 1)), out)
end

return M
