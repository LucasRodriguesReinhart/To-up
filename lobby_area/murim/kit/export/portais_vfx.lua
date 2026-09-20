-- portais_vfx.lua - liga os efeitos do pack VFX_Guardado_Lobby nos seis portais do Santuario.
-- Cada area ganha o vortice base (Portal-Enter-01) tingido com a cor do Config.Temas mais um efeito
-- com a cara do anime dela. Roda no Edit, e idempotente: apaga o que ele mesmo criou antes de refazer.
local SS = game:GetService("ServerStorage")
local RS = game:GetService("ReplicatedStorage")
local Config = require(RS.Config)

local pack = SS:FindFirstChild("VFX_Guardado_Lobby")
if not pack then return "VFX_Guardado_Lobby nao encontrado" end
local anime = pack:FindFirstChild("Anime")
local sant = workspace:FindFirstChild("Santuario")
if not (anime and sant) then return "Anime/Santuario nao encontrado" end

-- o sotaque de cada area: o efeito do pack que combina com o anime dela
local SOTAQUE = {
	chakra   = { "Wind-01", "Charge-01" },          -- Naruto: vento e carga de chakra
	ki       = { "Charge-01", "Fire-02" },          -- Dragon Ball: carga de ki e chama
	nichirin = { "Slashes-01", "Water-01" },        -- Demon Slayer: cortes e respiracao da agua
	sombra   = { "Smoke-01", "ForceField-01" },     -- sombra: fumaca e campo
	mare     = { "Water-02", "Splash-01" },         -- One Piece: agua e respingo
	serio    = { "Wind-02", "Crack-01" },           -- serio: deslocamento de ar e rachadura
}

local function seq(v, n)                            -- NumberSequence constante ou escalada
	if typeof(v) == "NumberSequence" then
		local kp = {}
		for _, k in ipairs(v.Keypoints) do
			table.insert(kp, NumberSequenceKeypoint.new(k.Time, k.Value * n, k.Envelope * n))
		end
		return NumberSequence.new(kp)
	end
	return NumberSequence.new(v * n)
end

local function tingir(pe, cor)
	pe.Color = ColorSequence.new(cor)
end

local feitos, avisos = 0, {}
for _, mod in ipairs(sant:GetChildren()) do
	local disco = mod:FindFirstChild("Disco")
	local id = disco and disco:GetAttribute("AreaId")
	local area = id and Config.areaPorId(id)
	if area then
		local tema = Config.Temas[area.tema]
		local cor = (typeof(tema) == "table" and (tema.cor or tema.Cor)) or Color3.fromRGB(200, 200, 200)

		local antigo = mod:FindFirstChild("VFX_PORTAL")
		if antigo then antigo:Destroy() end
		local folder = Instance.new("Folder"); folder.Name = "VFX_PORTAL"; folder.Parent = mod

		-- emissor principal, no meio do vao do arco novo (o vao vai de ~+1 a ~+13 acima do piso)
		local base = Instance.new("Part")
		base.Name = "VortexEmitter"
		base.Size = Vector3.new(0.2, 0.2, 0.2)
		base.Transparency = 1
		base.Anchored = true
		base.CanCollide = false
		base.CanQuery = false
		base.CanTouch = false
		base.CastShadow = false
		-- o portal encara -X; girar 90 em Z manda o +Y local (direcao de emissao padrao) para -X,
		-- que e o lado do jogador. Sem isso as linhas do vortice saem para dentro da parede.
		base.CFrame = CFrame.new(disco.Position + Vector3.new(-0.8, 3.2, 0)) * CFrame.Angles(0, 0, math.rad(90))
		base.Parent = folder

		local fonte = anime:FindFirstChild("Portal-Enter-01")
		if fonte then
			for _, pe in ipairs(fonte:GetDescendants()) do
				if pe:IsA("ParticleEmitter") then
					local c = pe:Clone()
					c.Size = seq(c.Size, 3.2)             -- o vao tem ~7 de largura: o emissor original e de 1 stud
					tingir(c, cor)
					c.Parent = base
				end
			end
		else
			table.insert(avisos, "Portal-Enter-01 ausente")
		end

		-- sotaque do anime, um pouco a frente e mais baixo
		for i, nome in ipairs(SOTAQUE[area.tema] or {}) do
			local src = anime:FindFirstChild(nome)
			if src then
				local p = base:Clone()
				p:ClearAllChildren()
				p.Name = "Accent_" .. nome
				p.CFrame = CFrame.new(disco.Position + Vector3.new(-1.6, i == 1 and 0.5 or 6.0, 0)) * CFrame.Angles(0, 0, math.rad(90))
				p.Parent = folder
				for _, pe in ipairs(src:GetDescendants()) do
					if pe:IsA("ParticleEmitter") then
						local c = pe:Clone()
						c.Size = seq(c.Size, 1.6)
						c.Rate = math.max(1, c.Rate * 0.35)   -- o pack e de efeito de combate: no cenario fica escandaloso
						tingir(c, cor)
						c.Parent = p
					end
				end
			else
				table.insert(avisos, nome .. " ausente")
			end
		end

		-- luz do portal: e ela que pinta a pedra em volta com a cor da area
		local luz = Instance.new("PointLight")
		luz.Color = cor
		luz.Brightness = 2.2
		luz.Range = 22
		luz.Shadows = false
		luz.Parent = base

		feitos += 1
	end
end
-- ---------- animacao ambiente: sem movimento nenhum a "lasca flutuando" e so uma pedra parada no ar.
-- Um Script so, no ServerScriptService, cuida dos seis portais. Ele e substituido a cada execucao.
local SSS = game:GetService("ServerScriptService")
local velho = SSS:FindFirstChild("PortaisAmbiente")
if velho then velho:Destroy() end
local amb = Instance.new("Script")
amb.Name = "PortaisAmbiente"
amb.Source = [==[
-- PortaisAmbiente - balanca as lascas dos portais e faz a luz do vortice respirar.
-- Instalado por lobby_area/murim/kit/export/portais_vfx.lua. Apagar aqui nao quebra mais nada.
local RunService = game:GetService("RunService")
local sant = workspace:WaitForChild("Santuario", 30)
local lob = workspace:WaitForChild("LOBBY_MURIM", 30)
if not (sant and lob) then return end

local lascas, luzes = {}, {}
for _, d in ipairs(lob:GetDescendants()) do
	if d:IsA("MeshPart") and d.Name:match("^POR_fragmento") then
		table.insert(lascas, { p = d, cf = d.CFrame, f = 0.5 + (#lascas % 5) * 0.17, a = (#lascas % 7) * 0.9 })
	end
end
for _, mod in ipairs(sant:GetChildren()) do
	local f = mod:FindFirstChild("VFX_PORTAL")
	local b = f and f:FindFirstChild("VortexEmitter")
	local l = b and b:FindFirstChildOfClass("PointLight")
	if l then table.insert(luzes, { l = l, base = l.Brightness, a = #luzes * 1.1 }) end
end

local t = 0
RunService.Heartbeat:Connect(function(dt)
	t += dt
	for _, s in ipairs(lascas) do
		local sobe = math.sin(t * s.f + s.a) * 0.55
		s.p.CFrame = s.cf * CFrame.new(0, sobe, 0) * CFrame.Angles(0, t * 0.35 + s.a, 0)
	end
	for _, u in ipairs(luzes) do
		u.l.Brightness = u.base * (0.78 + 0.22 * math.sin(t * 1.6 + u.a))
	end
end)
]==]
amb.Parent = SSS
table.insert(avisos, "PortaisAmbiente instalado em ServerScriptService")

return string.format("VFX ligado em %d portais | avisos: %s", feitos,
	#avisos > 0 and table.concat(avisos, ", ") or "nenhum")
