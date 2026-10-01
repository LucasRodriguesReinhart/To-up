-- Shared, pure audio preference schema. No settings outside this whitelist are persisted.
local AudioPreferences = {}

AudioPreferences.defaults = table.freeze({
	AudioMasterVolume = .8,
	AudioMusicVolume = .6,
	AudioSFXVolume = .85,
	AudioUIVolume = .65,
	AudioAmbienceVolume = .55,
	MusicEnabled = true,
	SomMineracaoEnabled = true,
	SomInterfaceEnabled = true,
})

function AudioPreferences.value(key, value)
	local default = AudioPreferences.defaults[key]
	if default == nil then return nil end
	if type(default) == "boolean" then
		if type(value) == "boolean" then return value end
		return nil
	end
	if type(value) ~= "number" or value ~= value or value == math.huge or value == -math.huge then return nil end
	return math.round(math.clamp(value, 0, 1) * 100) / 100
end

function AudioPreferences.sanitize(input, base)
	local result = {}
	input = type(input) == "table" and input or {}
	base = type(base) == "table" and base or {}
	for key, default in pairs(AudioPreferences.defaults) do
		local value = AudioPreferences.value(key, input[key])
		if value == nil then value = AudioPreferences.value(key, base[key]) end
		if value == nil then value = default end
		result[key] = value
	end
	return result
end

function AudioPreferences.apply(player, preferences)
	for key, value in pairs(AudioPreferences.sanitize(preferences)) do
		player:SetAttribute(key, value)
	end
end

return table.freeze(AudioPreferences)
