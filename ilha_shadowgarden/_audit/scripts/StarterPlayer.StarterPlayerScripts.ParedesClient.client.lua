-- ParedesClient: reflete o progresso pessoal nas Paredes de Custo.
-- O servidor manda (modelo, pago, custo); aqui atualizamos o painel e,
-- quando quitada, a barreira abre SO para este jogador (colisao local).
local RS = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local function fmt(n)
	n = math.floor(n)
	if n >= 1e9 then return string.format("%.1fB", n/1e9) end
	if n >= 1e6 then return string.format("%.1fM", n/1e6) end
	if n >= 1e3 then return string.format("%.1fK", n/1e3) end
	return tostring(n)
end

local ev = RS:WaitForChild("ParedeAtualizar", 30)
if not ev then return end

ev.OnClientEvent:Connect(function(modelo, pago, custo)
	if typeof(modelo) ~= "Instance" or not modelo.Parent then return end
	local painel = modelo:FindFirstChild("Painel")
	local bb = painel and painel:FindFirstChild("Requisito")
	if bb then
		local valor = bb:FindFirstChild("Valor")
		if valor then valor.Text = fmt(pago) .. " / " .. fmt(custo) end
		local bar = bb:FindFirstChild("Preenchimento", true)
		if bar then bar.Size = UDim2.new(math.clamp(pago / math.max(custo, 1), 0, 1), 0, 1, 0) end
	end
	if pago >= custo then
		local barreira = modelo:FindFirstChild("Barreira")
		if barreira and barreira.CanCollide then
			barreira.CanCollide = false
			TweenService:Create(barreira, TweenInfo.new(.8), {Transparency = .93}):Play()
		end
		local brilho = modelo:FindFirstChild("Brilho")
		if brilho then brilho.Transparency = .97 end
		local zonaPiso = modelo:FindFirstChild("ZonaPiso")
		if zonaPiso then zonaPiso.Transparency = .9 end
	end
end)