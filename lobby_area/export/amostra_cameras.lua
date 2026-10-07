-- amostra_cameras.lua - cameras de validacao da amostra (Edit). Executar um bloco por vez e usar View > Screenshot.
-- Origem do trecho = Roblox (0,0,-66) (ponto do avatar). Fachada da torre em z = -98.5; terraco y=4.5.
local cam = workspace.CurrentCamera; cam.CameraType = Enum.CameraType.Scriptable
local V = {
	geral   = {Vector3.new(0, 6, -53.5),   Vector3.new(0, 6, -160),      70},  -- = camera da referencia (12,5 atras do avatar)
	portal  = {Vector3.new(0.5, 6.5, -80), Vector3.new(0, 10.5, -98.5),  58},
	poste   = {Vector3.new(-13, 14.7, -89.6), Vector3.new(-10.6, 11.2, -94.5), 40},  -- mesma inclinacao do recorte da referencia
	arvores = {Vector3.new(-4, 7, -62),    Vector3.new(-13, 8, -86),     50},
	piso    = {Vector3.new(6, 9, -50),     Vector3.new(-12, -1, -78),    60},  -- piso + margem de agua a esquerda (x negativo)
	agua    = {Vector3.new(-10, 5, -60),   Vector3.new(-21, -1.5, -78),  55},
}
return V
