# gerar_montagem.py - GERA export/montar_pavilhao.lua a partir de export/kit_meshes.json + export/placements.json.
# E a fonte reproduzivel do script de montagem. As correcoes achadas no Studio em 2026-09-19 moram AQUI (antes foram feitas
# a mao no .lua e uma regeneracao as apagaria): (1) o FBX exporta nome de OBJETO e o Blender sufixa (KIT_coluna.012);
# (2) a caixa de colisao do terraco nao pode engolir o 1o degrau; (3) usar o kit mais novo que existir no workspace.
import json, os
R = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(R, 'export')
info = json.load(open(os.path.join(E, 'kit_meshes.json'))); place = json.load(open(os.path.join(E, 'placements.json')))
L = []
A = L.append
A('-- montar_pavilhao.lua - GERADO por kit/gerar_montagem.py. NAO editar a mao: corrija o gerador e rode de novo.')
A('-- Pre-requisito: o FBX do kit importado UMA vez (Home > Import 3D). Monta a amostra do Gate 1 clonando cada malha unica')
A('-- (mantem o instancing) e cria a colisao em Parts invisiveis. Eixos: Blender (x,y,z) -> Roblox (-x, z, y); rotacao em Z do')
A('-- Blender = rotacao em Y do Roblox; a MeshPart fica no CENTRO da caixa envolvente, entao soma-se o centro local escalado.')
A('local ORIGEM = Vector3.new(440, 0, 0)   -- fora da planta B2 e livre (conferido no Studio: 0 pecas, 0 terreno)')
A('local KIT')
A('for _, nome in ipairs({ "KIT_FORJA_CELESTE_v3", "KIT_FORJA_CELESTE_v2", "KIT_FORJA_CELESTE" }) do')
A('\tKIT = workspace:FindFirstChild(nome); if KIT then break end')
A('end')
A('assert(KIT, "importe o FBX do kit primeiro (Model KIT_FORJA_CELESTE_v3 no workspace)")')
A('local old = workspace:FindFirstChild("PAVILHAO_MODELO_G1"); if old then old:Destroy() end')
A('local ROOT = Instance.new("Model"); ROOT.Name = "PAVILHAO_MODELO_G1"; ROOT.Parent = workspace')
A('local function B(x, y, z) return Vector3.new(-x, z, y) end')
A('local INFO = {')
for n, v in sorted(info.items()):
    c, t = v['centro'], v['tamanho']
    A('\t["%s"] = { c = {%g,%g,%g}, t = {%g,%g,%g} },' % (n, c[0], c[1], c[2], t[0], t[1], t[2]))
A('}')
A('local PLACE = {')
for p in place:
    x, y, z = p['pos']; s = p['scale']
    A('\t{"%s", %g,%g,%g, %g, %g,%g,%g},' % (p['mesh'], x, y, z, p['rot'], s[0], s[1], s[2]))
A('}')
A('''local tmpl, faltam = {}, {}
-- (1) o FBX sai com nomes de OBJETO sufixados pelo Blender (KIT_coluna.012): indexa pelo nome sem o sufixo numerico
for _, d in ipairs(KIT:GetDescendants()) do if d:IsA("MeshPart") then tmpl[(d.Name:gsub("%.%d+$", ""))] = d end end
local PEQUENAS = { KIT_besta_0 = true, KIT_besta_1 = true, KIT_besta_2 = true, KIT_imortal = true, KIT_tufo_a = true, KIT_prancha = true, KIT_terca = true, KIT_vaso = true }
local n = 0
for _, p in ipairs(PLACE) do
	local nome, x, y, z, rot, sx, sy, sz = p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
	local t = tmpl[nome]; local i = INFO[nome]
	if not t or not i then faltam[nome] = true
	else
		local m = t:Clone(); m.Name = nome; m.Anchored = true
		m.CanCollide = false; m.CanTouch = false; m.CanQuery = false      -- decoracao: a colisao e feita por Parts simples abaixo
		m.CastShadow = not PEQUENAS[nome]
		m.Size = Vector3.new(i.t[1] * sx, i.t[3] * sz, i.t[2] * sy)
		local cf = CFrame.new(ORIGEM + B(x, y, z)) * CFrame.Angles(0, math.rad(rot), 0)
		if nome == "KIT_placa" then cf = cf * CFrame.Angles(math.rad(13), 0, 0) end   -- a placa pende para a frente (sinal ainda nao conferido de perto)
		m.CFrame = cf * CFrame.new(B(i.c[1] * sx, i.c[2] * sy, i.c[3] * sz))
		m.Parent = ROOT; n += 1
	end
end
-- colisao simples (invisivel). Medidas em coordenadas do Blender, convertidas por B().
local COL = Instance.new("Folder"); COL.Name = "Colisao"; COL.Parent = ROOT
local function caixa(nome, x0, x1, y0, y1, z0, z1)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.Transparency = 1; p.CastShadow = false; p.CanQuery = false
	p.Size = Vector3.new(x1 - x0, z1 - z0, y1 - y0); p.CFrame = CFrame.new(ORIGEM + B((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); p.Parent = COL
end
local function cilindro(nome, x, y, z0, z1, r)
	local c = Instance.new("Part"); c.Name = nome; c.Shape = Enum.PartType.Cylinder; c.Anchored = true; c.Transparency = 1; c.CastShadow = false; c.CanQuery = false
	c.Size = Vector3.new(z1 - z0, 2 * r, 2 * r); c.CFrame = CFrame.new(ORIGEM + B(x, y, (z0 + z1) / 2)) * CFrame.Angles(0, 0, math.pi / 2); c.Parent = COL
end
-- (2) na FRENTE a caixa do terraco para em -15.75 (borda real do piso): ate -16.7 ela engole o 1o degrau e vira um paredao de 1,6
caixa("terraco", -21.95, 21.95, -15.75, 16.7, 0, 4)
for i = 1, 4 do caixa("degrau" .. i, -4, 4, -15.75 - 1.9 * i, -15.75 - 1.9 * (i - 1), 0, 4 - 0.8 * i) end
for _, sx in ipairs({ -1, 1 }) do caixa("bochecha", math.min(sx * 4, sx * 5.25), math.max(sx * 4, sx * 5.25), -25.3, -15.75, 0, 4.4) end
caixa("parede_frente", -13.5, 13.5, -0.6, 0.6, 4, 17); caixa("parede_fundo", -13.5, 13.5, 8.4, 9.6, 4, 17)
caixa("parede_E", 12.9, 14.1, 0, 9, 4, 17); caixa("parede_W", -14.1, -12.9, 0, 9, 4, 17)
for _, x in ipairs({ -13.5, -4.5, 4.5, 13.5 }) do cilindro("coluna", x, -9, 4, 17, 1.35) end
caixa("bal_frente_W", -20.6, -4.6, -15.4, -14.5, 4, 7.3); caixa("bal_frente_E", 4.6, 20.6, -15.4, -14.5, 4, 7.3)
caixa("bal_fundo", -20.6, 20.6, 14.5, 15.4, 4, 7.3); caixa("bal_E", 19.75, 20.65, -15.4, 15.4, 4, 7.3); caixa("bal_W", -20.65, -19.75, -15.4, 15.4, 4, 7.3)
-- kit 2: muro com portao pequeno, pedestais de espada, bases de estandarte
caixa("muro_S", 35.2, 36.8, -23.6, -4.5, 0, 10.4); caixa("muro_N", 35.2, 36.8, 4.5, 23.6, 0, 10.4)
for _, y in ipairs({ -22.5, 22.5 }) do caixa("muro_pilar", 34.7, 37.3, y - 1.3, y + 1.3, 0, 10.6) end
for _, y in ipairs({ -4.5, 4.5 }) do cilindro("portao_coluna", 36, y, 0, 9.4, 1.35) end
for _, sx in ipairs({ -1, 1 }) do
	caixa("pedestal_espada", sx * 7.2 - 2, sx * 7.2 + 2, -33.5, -29.5, 0, 3.5)
	caixa("base_estandarte", sx * 16.5 - 1.5, sx * 16.5 + 1.5, -29, -26, 0, 1.3)
end
local f = {}; for k in pairs(faltam) do table.insert(f, k) end
return string.format("kit usado: %s | montadas %d de %d pecas | malhas sem template: %s", KIT.Name, n, #PLACE, (#f > 0 and table.concat(f, ", ") or "nenhuma"))''')
src = '\n'.join(L)
open(os.path.join(E, 'montar_pavilhao.lua'), 'w', encoding='utf-8').write(src)
sem_info = sorted({p['mesh'] for p in place} - set(info))
print('montar_pavilhao.lua: %d bytes | INFO %d malhas | PLACE %d colocacoes | colocacoes sem medida: %s' % (len(src.encode('utf-8')), len(info), len(place), sem_info or 'nenhuma'))
