local ignis = script.Parent
local braco = ignis:WaitForChild("BracoEsquerdo")

-- o pivo e lido do proprio modelo, nao de atributo salvo.
-- assim escalar ou mover o Ignis nunca mais desalinha o braco.
local function acharOmbro()
	for _, d in ipairs(ignis:GetDescendants()) do
		if d:IsA("BasePart") and d.Name == "shoulder_l" then return d end
	end
end

local ombro = acharOmbro()
if not ombro then warn("[Ignis] shoulder_l nao encontrado, animacao desligada"); return end

braco.PrimaryPart = nil
braco.WorldPivot = CFrame.new(ombro.Position)

-- guarda a pose de repouso: tudo e girado a partir dela
local POUSO = braco:GetPivot()

local ERGUIDO = math.rad(-15)
local BATIDA  = math.rad(42)

local billet, faiscas
for _, d in ipairs(ignis:GetDescendants()) do
	if d:IsA("BasePart") and d.Name == "hot_billet" then
		billet = d
		faiscas = d:FindFirstChild("Faiscas")
	end
end
local corBase = billet and billet.Color

local function girar(de, para, dur, curva)
	local t = 0
	while t < dur do
		t += task.wait()
		local a = curva(math.min(t / dur, 1))
		braco:PivotTo(POUSO * CFrame.Angles(de + (para - de) * a, 0, 0))
	end
	braco:PivotTo(POUSO * CFrame.Angles(para, 0, 0))
end

local easeOut = function(a) return 1 - (1 - a) ^ 3 end
local easeIn  = function(a) return a ^ 3 end

-- se o Ignis for movido durante o jogo, recalcula o pivo
task.spawn(function()
	while true do
		task.wait(5)
		local o = acharOmbro()
		if o and (o.Position - braco.WorldPivot.Position).Magnitude > 1.5 then
			braco.WorldPivot = CFrame.new(o.Position)
			POUSO = braco:GetPivot()
		end
	end
end)

braco:PivotTo(POUSO * CFrame.Angles(ERGUIDO, 0, 0))

while true do
	girar(ERGUIDO, BATIDA, 0.14, easeIn)
	if faiscas then faiscas:Emit(50) end
	ignis:SetAttribute("ForgeImpactTime",workspace:GetServerTimeNow())
	if billet then
		billet.Color = Color3.fromRGB(255, 245, 200)
		task.delay(0.16, function() billet.Color = corBase end)
	end
	task.wait(0.12)
	girar(BATIDA, ERGUIDO, 0.6, easeOut)
	task.wait(0.25)
end

