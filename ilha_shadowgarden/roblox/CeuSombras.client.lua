-- CeuSombras (LocalScript, StarterPlayerScripts) - ceu noturno da Ilha 3 (Shadow Garden).
-- O AreaAtmosphere e o dono do Lighting (ClockTime/Ambient/Atmosphere/ColorCorrection) e NAO toca em Sky nem Bloom
-- (auditoria C). Este script cuida SO desses dois, reagindo ao atributo ShadowGardenMood que o AreaAtmosphere publica:
--   * Sky: lua GRANDE + muitas estrelas enquanto o jogador esta na area sombra (a referencia tem uma lua enorme);
--   * Bloom proprio (fraco) para os neons violeta/lanternas brilharem de noite.
-- Tudo restaurado ao sair. Local: nao afeta outros jogadores.
local Players = game:GetService('Players')
local Lighting = game:GetService('Lighting')
local TweenService = game:GetService('TweenService')
local player = Players.LocalPlayer

local MOON_SIZE = 24          -- MoonAngularSize na area (padrao do Roblox: 11)
local STARS = 3000
local BLOOM = { Intensity = 0.35, Size = 42, Threshold = 1.55 }

local bloom = Instance.new('BloomEffect')
bloom.Name = 'CeuSombrasBloom'
bloom.Enabled = false
bloom.Intensity = 0
bloom.Size = BLOOM.Size
bloom.Threshold = BLOOM.Threshold
bloom.Parent = Lighting

local salvo = nil             -- { sky, moon, stars } do estado fora da area

local function aplicar(ligado)
	local sky = Lighting:FindFirstChildOfClass('Sky')
	if ligado then
		if sky and not salvo then
			salvo = { sky = sky, moon = sky.MoonAngularSize, stars = sky.StarCount }
			sky.MoonAngularSize = MOON_SIZE
			sky.StarCount = STARS
		end
		bloom.Enabled = true
		TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = BLOOM.Intensity }):Play()
	else
		if salvo then
			if salvo.sky.Parent then
				salvo.sky.MoonAngularSize = salvo.moon
				salvo.sky.StarCount = salvo.stars
			end
			salvo = nil
		end
		local t = TweenService:Create(bloom, TweenInfo.new(1.6, Enum.EasingStyle.Sine), { Intensity = 0 })
		t.Completed:Once(function() if not (player:GetAttribute('ShadowGardenMood') == true) then bloom.Enabled = false end end)
		t:Play()
	end
end

player:GetAttributeChangedSignal('ShadowGardenMood'):Connect(function()
	aplicar(player:GetAttribute('ShadowGardenMood') == true)
end)
aplicar(player:GetAttribute('ShadowGardenMood') == true)
