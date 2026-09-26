local ROTAS={
{nome="NARUTO_GATE->DB_ENTRY",y0=16.2,pts={{-175.2,595.2},{-192.87,612.87},{-217.62,637.62},{-230.7,650.7},{-245.55,665.55},{-250.15,670.15},{-258.64,678.64}}},
{nome="DB_ENTRY->MINING",y0=24.2,pts={{-258.64,678.64},{-269.95,689.95},{-283.03,703.03},{-284.09,704.09},{-290.1,710.1},{-294.34,714.34},{-309.55,729.55}}},
{nome="DB_ENTRY->CAPSULE",y0=24.2,pts={{-258.64,678.64},{-277.73,697.73},{-286.13,690.06},{-295.61,683.47},{-306.17,678.29},{-317.63,674.43},{-329.94,672.26},{-342.67,672.84},{-355.01,676.52},{-366.3,682.83},{-376.01,691.36},{-383.68,701.68},{-388.92,713.27},{-391.57,725.5},{-391.32,737.77},{-388.58,749.37},{-384.47,759.98},{-379.36,769.65},{-373.16,778.33},{-366.12,786.12},{-370.71,790.71},{-378.49,798.49},{-392.42,812.42},{-406.7,826.7},{-418.09,838.09},{-417.73,837.73},{-421.27,841.27},{-427.63,847.63},{-434.0,854.0},{-450.97,870.97}}},
{nome="MINING->SUMMON",y0=20.2,pts={{-316.62,750.76},{-288.69,778.69},{-284.44,782.93},{-278.43,788.94},{-277.37,790.0},{-273.13,794.25},{-260.47,804.08},{-248.38,816.17},{-237.42,824.3}}},
{nome="MINING->CAPSULE",y0=20.2,pts={{-330.76,750.76},{-350.91,770.91},{-355.16,775.16},{-361.17,781.17},{-362.23,782.23},{-366.12,786.12},{-370.71,790.71},{-378.49,798.49},{-392.42,812.42},{-406.7,826.7},{-418.09,838.09},{-417.73,837.73},{-421.27,841.27},{-427.63,847.63},{-434.0,854.0},{-450.97,870.97}}},
{nome="MINING->SHADOW_GATE",y0=20.2,pts={{-333.59,736.62},{-360.63,721.49},{-364.06,719.43},{-379.49,710.16},{-380.77,709.39},{-386.08,706.2},{-391.25,723.03},{-393.14,710.8},{-404.46,708.81},{-424.1,705.51},{-449.55,699.85},{-472.18,694.19},{-483.49,691.36},{-501.91,683.55},{-524.0,674.17},{-544.25,665.57},{-547.01,664.4}}},
{nome="CAPSULE->SHADOW_GATE",y0=34.2,pts={{-450.97,870.97},{-434.0,854.0},{-427.63,847.63},{-421.27,841.27},{-417.73,837.73},{-418.44,838.44},{-406.35,826.35},{-391.57,811.57},{-397.23,788.94},{-417.73,767.02},{-443.9,742.27},{-456.62,735.2},{-455.21,713.99},{-455.21,699.85},{-483.49,691.36},{-501.91,683.55},{-524.0,674.17},{-544.25,665.57},{-547.01,664.4}}},
{nome="SUMMON->SHADOW_GATE",y0=30.2,pts={{-237.42,824.3},{-248.38,816.17},{-260.47,804.08},{-271.72,792.83},{-264.87,784.27},{-259.04,772.74},{-255.62,760.41},{-254.86,747.78},{-256.6,735.45},{-260.2,723.79},{-265.62,713.07},{-272.56,703.46},{-280.64,694.85},{-289.79,687.28},{-300.13,681.0},{-311.56,676.29},{-323.94,673.02},{-337.07,672.18},{-350.16,674.72},{-362.39,680.28},{-373.11,688.42},{-381.77,698.64},{-387.9,710.41},{-391.25,723.03},{-393.14,710.8},{-404.46,708.81},{-424.1,705.51},{-449.55,699.85},{-472.18,694.19},{-483.49,691.36},{-501.91,683.55},{-524.0,674.17},{-544.25,665.57},{-547.01,664.4}}},
}-- teste_caminhadas.lua (SERVIDOR, em Play): anda o personagem pelas rotas da missao com Humanoid:MoveTo sobre a
-- colisao real da ilha e registra se cada ponto foi alcancado, recuperacoes do IslandTravel e a area atual.
local Players = game:GetService('Players')
local plr = Players:GetPlayers()[1]
local res = {}
local function log(s) table.insert(res, s) print('[CAMINHADA] ' .. s) end
local function walk(r)
	local char = plr.Character or plr.CharacterAdded:Wait()
	local hum, hrp = char:WaitForChild('Humanoid'), char:WaitForChild('HumanoidRootPart')
	hum.WalkSpeed = 32
	local p0 = r.pts[1]
	-- ponto inicial: raio para achar o piso
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = { char }
	local hit = workspace:Raycast(Vector3.new(p0[1], r.y0 + 20, p0[2]), Vector3.new(0, -60, 0), rp)
	local y = hit and hit.Position.Y or r.y0
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.CFrame = CFrame.new(p0[1], y + 3.5, p0[2])
	task.wait(1.5)
	local rec0 = plr:GetAttribute('AreaRecoveries') or 0
	local falhas = 0
	for i = 2, #r.pts do
		local q = r.pts[i]
		local alvo = Vector3.new(q[1], hrp.Position.Y, q[2])
		local done = false
		local con = hum.MoveToFinished:Connect(function() done = true end)
		hum:MoveTo(alvo)
		local t0 = os.clock()
		while not done and os.clock() - t0 < 12 do task.wait(0.1) end
		con:Disconnect()
		local d = (Vector3.new(hrp.Position.X, 0, hrp.Position.Z) - Vector3.new(q[1], 0, q[2])).Magnitude
		if d > 3 then
			falhas += 1
			log(('%s: ponto %d NAO alcancado (faltam %.1f) em %s'):format(r.nome, i, d, tostring(hrp.Position)))
			break
		end
	end
	local rec = (plr:GetAttribute('AreaRecoveries') or 0) - rec0
	log(('%s: %s | recuperacoes %d | area %s | fim %s'):format(r.nome, falhas == 0 and 'OK' or 'FALHOU', rec,
		tostring(plr:GetAttribute('CurrentAreaId')), tostring(hrp.Position)))
	return falhas == 0 and rec == 0
end
local ok = 0
for _, r in ipairs(ROTAS) do if walk(r) then ok += 1 end end
log(('ROTAS NO JOGO %d/%d'):format(ok, #ROTAS))
workspace:SetAttribute('TesteCaminhadas', table.concat(res, '\n'))
