-- gerado pelo montar da ilha/portoes: gira/flutua as pecas com a tag IlhaMovel (so visual, no cliente).
-- Tudo e relativo ao pivo do Model dono (atributo movel_de): o Model pode ser movido com PivotTo.
local CS = game:GetService('CollectionService'); local RS = game:GetService('RunService')
local t0 = os.clock()
RS.RenderStepped:Connect(function()
  local t = os.clock() - t0
  for _, d in ipairs(CS:GetTagged('IlhaMovel')) do
    local dono = d:FindFirstAncestor(d:GetAttribute('movel_de') or '')
    local cf0, p, a = d:GetAttribute('cf0_rel'), d:GetAttribute('pivot_rel'), d:GetAttribute('axis_rel')
    if dono and cf0 and p and a and a.Magnitude > 0 then
      local ang = t * (d:GetAttribute('rpm') or 0) * math.pi / 30
      local amp, rate = d:GetAttribute('bob') or 0, d:GetAttribute('rate') or 0
      local bob
      if rate > 0 then  -- pilao: sobe devagar (70% do ciclo) e cai rapido (30%)
        local f = (t * rate) % 1
        bob = amp * ((f < 0.7) and (f / 0.7) or (1 - (f - 0.7) / 0.3))
      else
        bob = math.sin(t * 1.6 + p.X * 0.1) * amp
      end
      local r = CFrame.fromAxisAngle(a.Unit, ang)
      d.CFrame = dono:GetPivot() * (CFrame.new(p + Vector3.new(0, bob, 0)) * r * CFrame.new(-p) * cf0)
    end
  end
end)
