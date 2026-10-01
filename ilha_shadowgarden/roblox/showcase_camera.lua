-- showcase_camera.lua - passeio de camera do SHOWCASE da Ilha 3 (rodar no CLIENTE do Play pelo MCP/command bar).
-- Nao faz parte do jogo: so trava a camera num roteiro de planos (keyframes com easing), esconde HUD/personagem/pets
-- e desenha titulo, legendas e fades. Comeca com 4 s de tela preta (o gravador corta depois).
local Players = game:GetService('Players')
local RunService = game:GetService('RunService')
local StarterGui = game:GetService('StarterGui')
local pl = Players.LocalPlayer
local cam = workspace.CurrentCamera
local V = Vector3.new

local PRETO_INICIAL = 4.0
local FADE = 0.45

local function ease(t) return t * t * (3 - 2 * t) end
local function lerp(a, b, t) return a + (b - a) * t end
-- plano linear: posicao e alvo interpolados com easing
local function dolly(p0, p1, a0, a1, fov0, fov1)
	return function(t)
		local e = ease(t)
		return lerp(p0, p1, e), lerp(a0, a1, e), lerp(fov0, fov1 or fov0, e)
	end
end
-- orbita em volta de um centro
local function orbita(c, r0, r1, h0, h1, g0, g1, alvo, fov)
	return function(t)
		local e = ease(t)
		local g = math.rad(lerp(g0, g1, e))
		local r = lerp(r0, r1, e)
		return c + V(math.cos(g) * r, lerp(h0, h1, e), math.sin(g) * r), alvo, fov
	end
end

local ILHA = V(-770, 45, 560)
local PLANOS = {
	{ 9.0, 'SHADOW GARDEN', orbita(ILHA, 520, 470, 250, 190, -12, 38, V(-790, 40, 555), 40), titulo = true },
	{ 8.0, 'A chegada', dolly(V(-556, 64, 694), V(-628, 44, 640), V(-690, 62, 606), V(-770, 78, 572), 55, 50) },
	{ 7.0, 'A praca da fonte', dolly(V(-672, 42.5, 614), V(-712, 47, 597), V(-848, 84, 536), V(-860, 92, 530), 52) },
	{ 7.5, 'O castelo da Ordem', dolly(V(-812, 56, 552), V(-827, 62, 546), V(-872, 68, 527), V(-876, 98, 524), 55, 60) },
	{ 8.0, 'O Mining Hall', dolly(V(-861, 58.5, 532), V(-897, 60.5, 516), V(-935, 58, 499), V(-940, 60, 497), 58) },
	{ 9.0, 'A caverna da Masmorra', dolly(V(-800, 62, 478), V(-838, 57.5, 435), V(-848, 66, 428), V(-858, 56, 423), 55, 48) },
	{ 7.0, 'O pavilhao da Alquimia', orbita(V(-730, 44.2, 489), 50, 43, 24, 19, 195, 240, V(-730, 62, 489), 58) },
	{ 6.0, 'O caldeirao do alquimista', dolly(V(-735.5, 50.5, 499.5), V(-733, 49.5, 494.5), V(-729.5, 49, 486.5), V(-729.5, 48, 486.5), 70, 64) },
	{ 7.0, 'A vila', dolly(V(-790.7, 49.4, 592), V(-800, 49.4, 614), V(-818, 50.2, 658), V(-826, 50.5, 676), 50) },
	{ 7.0, 'A torre de invocacao', dolly(V(-759, 44, 668), V(-763, 58, 686), V(-770, 58, 732), V(-770.5, 76, 733), 55, 58) },
	{ 7.0, 'A saida para o Monte Natagumo', dolly(V(-678, 57, 318), V(-687, 61, 334), V(-742, 66, 428), V(-802, 80, 500), 55, 52) },
	{ 9.0, '', orbita(ILHA, 380, 560, 120, 260, 115, 150, V(-790, 45, 560), 42), fim = true },
}

-- ---------- overlay (titulo, legendas, fades) ----------
local gui = Instance.new('ScreenGui')
gui.Name = 'ShowcaseOverlay'; gui.IgnoreGuiInset = true; gui.DisplayOrder = 100000; gui.ResetOnSpawn = false
local preto = Instance.new('Frame')
preto.Size = UDim2.fromScale(1, 1); preto.BackgroundColor3 = Color3.new(0, 0, 0); preto.BorderSizePixel = 0
preto.BackgroundTransparency = 0; preto.ZIndex = 10; preto.Parent = gui
local function texto(nome, pos, tam, fonte, cor)
	local l = Instance.new('TextLabel')
	l.Name = nome; l.BackgroundTransparency = 1; l.Position = pos; l.Size = tam; l.Font = fonte
	l.TextScaled = true; l.TextColor3 = cor; l.TextTransparency = 1; l.TextStrokeTransparency = 1
	l.TextStrokeColor3 = Color3.fromRGB(10, 4, 24); l.ZIndex = 5; l.Parent = gui
	return l
end
local titulo = texto('Titulo', UDim2.fromScale(0.15, 0.36), UDim2.fromScale(0.7, 0.13), Enum.Font.Garamond, Color3.fromRGB(236, 224, 255))
local sub = texto('Sub', UDim2.fromScale(0.25, 0.5), UDim2.fromScale(0.5, 0.05), Enum.Font.Garamond, Color3.fromRGB(196, 170, 255))
sub.Text = 'Ilha 3  -  Anime Mining Simulator'
local legenda = texto('Legenda', UDim2.fromScale(0.05, 0.84), UDim2.fromScale(0.42, 0.06), Enum.Font.Garamond, Color3.fromRGB(236, 224, 255))
legenda.TextXAlignment = Enum.TextXAlignment.Left
local barra = Instance.new('Frame')
barra.BackgroundColor3 = Color3.fromRGB(170, 110, 255); barra.BorderSizePixel = 0; barra.BackgroundTransparency = 1
barra.Position = UDim2.fromScale(0.05, 0.905); barra.Size = UDim2.fromScale(0.12, 0.004); barra.ZIndex = 5; barra.Parent = gui
gui.Parent = pl.PlayerGui

-- ---------- esconder HUD, personagem, pets ----------
pcall(function() StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, false) end)
local desligadas = {}
-- o botao de mineracao continua (AutoMinerar) se religa sozinho: sai da tela durante o showcase
local hold = pl.PlayerGui:FindFirstChild('HoldModeGui')
if hold then hold.Parent = nil end
for _, g in ipairs(pl.PlayerGui:GetChildren()) do
	if g:IsA('ScreenGui') and g ~= gui and g.Enabled then g.Enabled = false; table.insert(desligadas, g) end
end
local hrp = pl.Character and pl.Character:FindFirstChild('HumanoidRootPart')
if hrp then hrp.Anchored = true; hrp.CFrame = CFrame.new(-779, 47, 566) end   -- dentro da ilha (area 3 + streaming)
local function esconder()
	for _, raiz in ipairs({ pl.Character, workspace:FindFirstChild('PetsVisuais') }) do
		if raiz then
			for _, d in ipairs(raiz:GetDescendants()) do
				if d:IsA('BasePart') or d:IsA('Decal') then d.LocalTransparencyModifier = 1
				elseif d:IsA('BillboardGui') then d.Enabled = false end
			end
		end
	end
	for _, g in ipairs(pl.PlayerGui:GetChildren()) do
		if g:IsA('ScreenGui') and g ~= gui and g.Enabled then g.Enabled = false; table.insert(desligadas, g) end
	end
end

-- ---------- roteiro ----------
local total = PRETO_INICIAL
for _, p in ipairs(PLANOS) do total += p[1] end
local t0 = os.clock()
local ultimoEsconder = 0
pcall(function() RunService:UnbindFromRenderStep('SHOWCASE') end)
RunService:BindToRenderStep('SHOWCASE', Enum.RenderPriority.Camera.Value + 2, function()
	local agora = os.clock() - t0
	if agora - ultimoEsconder > 0.25 then esconder(); ultimoEsconder = agora end
	cam.CameraType = Enum.CameraType.Scriptable
	local t = agora - PRETO_INICIAL
	local i, dentro = 1, t
	if t < 0 then
		i, dentro = 1, 0
	else
		while PLANOS[i] and dentro > PLANOS[i][1] do dentro -= PLANOS[i][1]; i += 1 end
	end
	local p = PLANOS[i]
	if not p then
		preto.BackgroundTransparency = 0
		RunService:UnbindFromRenderStep('SHOWCASE')
		return
	end
	local d = p[1]
	local pos, alvo, fov = p[3](math.clamp(dentro / d, 0, 1))
	cam.FieldOfView = fov
	cam.CFrame = CFrame.lookAt(pos, alvo)
	-- fades nas bordas de cada plano (o primeiro sai do preto inicial)
	local f = 0
	if t < 0 then f = 1
	else
		if dentro < FADE then f = 1 - dentro / FADE end
		if d - dentro < FADE then f = math.max(f, 1 - (d - dentro) / FADE) end
		if p.fim and d - dentro < 1.6 then f = math.max(f, 1 - (d - dentro) / 1.6) end
	end
	preto.BackgroundTransparency = 1 - f
	-- titulo (plano 1) e legendas (demais)
	local function alfa(a, b) -- visivel entre a e b (segundos do plano), com rampas de 0,6 s
		if dentro < a or dentro > b then return 1 end
		return 1 - math.min(1, (dentro - a) / 0.6, (b - dentro) / 0.6)
	end
	if p.titulo and t >= 0 then
		titulo.Text = p[2]
		titulo.TextTransparency = alfa(1.0, d - 1.2); titulo.TextStrokeTransparency = math.min(1, titulo.TextTransparency + 0.3)
		sub.TextTransparency = alfa(1.6, d - 1.4); sub.TextStrokeTransparency = math.min(1, sub.TextTransparency + 0.3)
		legenda.TextTransparency = 1; barra.BackgroundTransparency = 1
	else
		titulo.TextTransparency = 1; sub.TextTransparency = 1; titulo.TextStrokeTransparency = 1; sub.TextStrokeTransparency = 1
		legenda.Text = p[2]
		local a = (p[2] ~= '') and alfa(0.7, d - 0.9) or 1
		legenda.TextTransparency = a; legenda.TextStrokeTransparency = math.min(1, a + 0.3)
		barra.BackgroundTransparency = a
	end
end)

-- limpeza ao fim
task.delay(total + 2, function()
	pcall(function() RunService:UnbindFromRenderStep('SHOWCASE') end)
	gui:Destroy()
	for _, g in ipairs(desligadas) do if g.Parent then g.Enabled = true end end
	if hold then hold.Parent = pl.PlayerGui end
	pcall(function() StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, true) end)
	cam.CameraType = Enum.CameraType.Custom
	if hrp then hrp.Anchored = false end
end)
return string.format('showcase iniciado: %.1f s (%.1f s de preto no comeco)', total, PRETO_INICIAL)
