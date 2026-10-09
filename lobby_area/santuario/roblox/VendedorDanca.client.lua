-- StarterPlayer.StarterPlayerScripts.VendedorDanca (instalado no Studio do AMS em 2026-10-09)
-- VendedorDanca: o vendedor de mochilas (lobby Santuario, dentro da loja-mochila) fica em loop INFINITO no emote
-- "Lil Wayne Idle Pose" (catalogo 108439329967345 -> animacao 123346248406109; atributo DancaAnim no NPC troca a
-- animacao). Toca no CLIENTE: o emote e de criador UGC e a faixa tocada no servidor chega ao cliente sem carregar
-- (Length 0); carregada aqui ela toca normal. Com streaming o NPC pode sair e voltar: o laco reinicia sozinho.
local ANIM_PADRAO = 'rbxassetid://123346248406109'
local NOMES = {'Vebdedor suspeito', 'npc vendedor ', 'npc vendedor'}

local function acharVendedor()
	for _, c in ipairs(workspace:GetChildren()) do
		if c:IsA('Model') and c:GetAttribute('VendedorMochilas') then return c end
	end
	for _, n in ipairs(NOMES) do
		local c = workspace:FindFirstChild(n)
		if c and c:IsA('Model') then return c end
	end
	return nil
end

local atual, faixa = nil, nil
local function tocar(m)
	local hum = m:FindFirstChildOfClass('Humanoid')
	if not hum then return nil end
	local animator = hum:FindFirstChildOfClass('Animator')
	if not animator then animator = Instance.new('Animator'); animator.Parent = hum end
	local a = Instance.new('Animation')
	a.AnimationId = m:GetAttribute('DancaAnim') or ANIM_PADRAO
	local ok, tr = pcall(function() return animator:LoadAnimation(a) end)
	if not ok or not tr then return nil end
	tr.Looped = true
	tr.Priority = Enum.AnimationPriority.Action
	tr:Play(0.3)
	return tr
end

while true do
	local m = acharVendedor()
	if m ~= atual then
		if faixa then pcall(function() faixa:Stop(0) end) end
		atual, faixa = m, nil
	end
	if atual and atual.Parent and (not faixa or not faixa.IsPlaying) then
		faixa = tocar(atual)
	end
	task.wait(2)
end
