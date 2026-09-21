# gerar_lobby.py - GERA export/montar_lobby.lua a partir de export/kit_meshes.json + lobby_placements.json.
# Monta o LOBBY inteiro na posicao da planta B2 (origem do lobby = (0,0,0) do Roblox), guarda o lobby antigo,
# cria a colisao em Parts invisiveis e mantem spawn, Ignis, Santuario, Loja e MailBox funcionando.
import json, os
R = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(R, 'export')
info_raw = json.load(open(os.path.join(E, 'kit_meshes.json')))
place = json.load(open(os.path.join(R, 'lobby_placements.json')))
# o Blender sufixa nomes repetidos (KIT_coluna.001) e o importador do Roblox sufixa de novo: a chave util e o nome BASE.
# Quando as duas versoes existem (a do pavilhao-modelo e a do lobby) elas vem da mesma funcao, entao a medida e a mesma.
import re

def _colisao_das_cotas():
    """Emite a colisao de terraco e degrau a partir de lobby_cotas.json, que a GEOMETRIA gravou.

    Antes estas alturas eram literais digitados aqui (9.98 / 6.38 / 7.98) e repetidos em
    k_montagem.py como argumentos de terraco(). Os dois conjuntos de numeros nao tinham ligacao
    nenhuma: mudar a cota na geometria deixava a colisao para tras, e o jogador ficava flutuando
    meio metro acima do piso ou afundado nele. Era por isso que eu evitava terracear.
    Agora a geometria e a fonte unica: aqui so se le o que ela registrou.
    """
    import json, os
    cam = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lobby_cotas.json')
    if not os.path.exists(cam):
        raise SystemExit('lobby_cotas.json nao existe: rode a montagem antes de gerar a colisao')
    C = json.load(open(cam))
    L = ['-- COLISAO DERIVADA DAS COTAS DA GEOMETRIA (lobby_cotas.json). Nao edite alturas aqui:',
         '-- mude o terraco em k_montagem.py e rode a montagem; estas linhas se regeneram.']
    nomes = {'t_-62_-152': 'forja', 't_-146_-45': 'santuario', 't_104_-24': 'loja'}
    for t in C['terracos']:
        n = nomes.get(t['nome'], t['nome'])
        # o lado do terraco onde a escada desce fica 0.1 recuado, para o degrau encostar sem sobrepor
        y1 = t['y1'] - 0.1 if n == 'forja' else t['y1']
        L.append('caixa("terraco_%s", %.2f, %.2f, %.2f, %.2f, 0, %.2f)' % (n, t['x0'], t['x1'], t['y0'], y1, t['z']))
    esc_nome = {'e_-90': 'forja', 'ex_-104': 'sant', 'ex_104': 'loja'}
    for e in C['escadas']:
        n = esc_nome.get(e['nome'], e['nome'])
        z, k, tr, sd = e['z'], e['n'], e['tread'], e['sentido']
        for i in range(1, k + 1):
            alt = z - (z / k) * (i - 1)
            if e['eixo'] == 'Y':
                a0, a1 = e['a0'], e['a1']
                b0 = e['b0'] + tr * (i - 1) * sd
                b1 = b0 + tr * sd
                L.append('caixa("degrau_%s%d", %.2f, %.2f, %.2f, %.2f, 0, %.3f)'
                         % (n, i, a0, a1, min(b0, b1), max(b0, b1), alt))
            else:
                b0, b1 = e['b0'], e['b1']
                a0 = e['a0'] + tr * (i - 1) * sd
                a1 = a0 + tr * sd
                L.append('caixa("degrau_%s%d", %.2f, %.2f, %.2f, %.2f, 0, %.3f)'
                         % (n, i, min(a0, a1), max(a0, a1), b0, b1, alt))
    return chr(10).join(L)


def base(n): return re.sub(r'\.\d+$', '', n)
info = {}
for n, v in info_raw.items():
    info.setdefault(base(n), v)
place = [dict(p, mesh=base(p['mesh'])) for p in place]

# ---- o lago virou AGUA DE TERRENO (lamina em Roblox Y=0.10). O espalhamento de vegetacao do
# k_montagem nao conhecia a pegada do lago, entao grama, arbusto, bordo, rocha e ate barril
# nasciam DENTRO da agua. Aqui eles sao tirados por medida, e nao a olho.
# A caixa e a do corpo d'agua em coordenadas Blender: x -100..-70, y -70..130 (Roblox X = -x, Z = y),
# com 1.5 de folga para o raio da propria peca.
LAGO = (-101.5, -68.5, -71.5, 131.5)
TERRESTRE = ('KIT_tufo', 'KIT_arbusto', 'KIT_pinheiro', 'LOB_bordo', 'LOB_rocha', 'VIL_')
def na_agua(p):
    x, y, z = p['pos']
    if not (LAGO[0] <= x <= LAGO[1] and LAGO[2] <= y <= LAGO[3]): return False
    if z > 2.0: return False                      # espigao do telhado, bestas, imortal: passam por cima
    n = p['mesh']
    if 'lotus' in n: return False                 # lotus E de agua: fica
    if n.startswith('LOB_ponte'): return False    # a ponte-lua atravessa o lago de proposito
    return n.startswith('JAR_') or n.startswith(TERRESTRE)
afogadas = [p for p in place if na_agua(p)]
place = [p for p in place if not na_agua(p)]

# os lotus ficavam em z=-0.3, que agora esta DEBAIXO da lamina: sobem para a superficie.
for p in place:
    if 'lotus' in p['mesh'] and LAGO[0] <= p['pos'][0] <= LAGO[1] and LAGO[2] <= p['pos'][1] <= LAGO[3]:
        p['pos'] = [p['pos'][0], p['pos'][1], 0.05]
L = []; A = L.append
A('-- montar_lobby.lua - GERADO por kit/gerar_lobby.py. NAO editar a mao: corrija o gerador e rode de novo.')
A('-- Pre-requisito: LOBBY_FORJA_CELESTE.fbx importado (Home > Import 3D).')
A('-- Eixos: Blender (x,y,z) -> Roblox (-x, z, y). A MeshPart fica no CENTRO da caixa envolvente: soma-se o centro local escalado.')
A('local SS = game:GetService("ServerStorage")')
A('local KIT = workspace:FindFirstChild("LOBBY_FORJA_CELESTE")')
A('assert(KIT, "importe LOBBY_FORJA_CELESTE.fbx primeiro")')
A('local function B(x, y, z) return Vector3.new(-x, z, y) end')
A('-- 1) guarda o que existe hoje (nada e apagado)')
A('local antigo = workspace:FindFirstChild("MURIM_BLOCKOUT")')
A('if antigo then')
A('\tlocal g = SS:FindFirstChild("MURIM_BLOCKOUT_Guardado") or Instance.new("Folder"); g.Name = "MURIM_BLOCKOUT_Guardado"; g.Parent = SS')
A('\tantigo.Parent = g')
A('end')
A('local old = workspace:FindFirstChild("LOBBY_MURIM"); if old then old:Destroy() end')
A('local ROOT = Instance.new("Model"); ROOT.Name = "LOBBY_MURIM"; ROOT.Parent = workspace')
A('local GRUPO = {}')
A('for _, n in ipairs({ "Forja", "Patio", "Portao", "Leste", "Oeste", "Veg", "Props", "Chao" }) do')
A('\tlocal f = Instance.new("Folder"); f.Name = n; f.Parent = ROOT; GRUPO[n] = f')
A('end')
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
A('''local function grupo(nome)
	if nome:find("^TEL_") or nome:find("fornalha") or nome:find("torre") or nome:find("bigorna") or nome:find("fole") or nome:find("calha") or nome:find("laminas") then return GRUPO.Forja end
	if nome:find("pinheiro") or nome:find("arbusto") or nome:find("tufo") or nome:find("bambu") or nome:find("bordo") or nome:find("rocha") then return GRUPO.Veg end
	if nome:find("lanterna") or nome:find("estandarte") or nome:find("braseiro") or nome:find("leao") or nome:find("vaso") then return GRUPO.Props end
	if nome:find("muro") or nome:find("PORTAO") or nome:find("VIA") then return GRUPO.Portao end
	if nome:find("^POR_") then return GRUPO.Leste end          -- os portais ficam no Santuario
	if nome:find("^JAR_") then return GRUPO.Veg end            -- flores, grama, lotus
	if nome:find("^VIL_") then return GRUPO.Props end          -- poco, varal, carroca, cestos
	if nome:find("ponte") or nome:find("LAGO") or nome:find("SANT") then return GRUPO.Leste end
	if nome:find("poste_treino") or nome:find("boneco") or nome:find("estante") or nome:find("TREINO") then return GRUPO.Oeste end
	if nome:find("PENHASCO") or nome:find("chao") then return GRUPO.Chao end
	-- pecas novas: cenario de fundo, calcamento e relva moram no grupo do Chao
	if nome:find("^LOB_serra") or nome:find("^LOB_nevoa") or nome:find("^LOB_calcada")
		or nome:find("^LOB_junta") or nome:find("^LOB_relva") or nome:find("^KIT_relva") then return GRUPO.Chao end
	return GRUPO.Patio
end
local SEM_SOMBRA = { KIT_piso_mod = true, KIT_sumeru_seg = true, KIT_sumeru_canto = true, KIT_bal_seg = true,
	KIT_col_base = true, LOB_chao = true, VIA_piso = true, OESTE_caminho = true, TREINO_areia = true,
	PATIO_borda = true, PATIO_leito = true, LAGO_leito = true, LAGO_margem = true, LAGO_agua = true,
	PATIO_agua = true, SANT_fundo = true }
local PEQ = { KIT_besta_0 = true, KIT_besta_1 = true, KIT_besta_2 = true, KIT_imortal = true, KIT_tufo_a = true, KIT_prancha = true, KIT_terca = true, KIT_vaso = true, KIT_arbusto_a = true, KIT_arbusto_b = true }
local tmpl, faltam, n = {}, {}, 0
for _, d in ipairs(KIT:GetDescendants()) do if d:IsA("MeshPart") then tmpl[(d.Name:gsub("%.%d+$", ""))] = d end end
for _, p in ipairs(PLACE) do
	local nome, x, y, z, rot, sx, sy, sz = p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
	local t = tmpl[nome]; local i = INFO[nome]
	if not t or not i then faltam[nome] = true
	else
		local m = t:Clone(); m.Name = nome; m.Anchored = true
		m.CanCollide = false; m.CanTouch = false; m.CanQuery = false
		-- Sombra: a regra antiga isentava so o que ja era barato (flor, grama) e deixava ligadas as
		-- familias caras. Medido: 1.322 de 1.618 pecas lancavam sombra, e piso + balaustrada sozinhos
		-- eram 35% disso - superficies planas que so projetam sombra dentro de si mesmas.
		-- Alem da lista, qualquer peca com menos de 1 stud de altura e ladrilho de chao e sai sozinha.
		m.CastShadow = not (PEQ[nome] or SEM_SOMBRA[nome]
			or nome:find("^JAR_") or nome:find("^VIL_") or nome:find("^PATIO_piso")
			or nome:find("^PENHASCO") or nome:find("^ESCADA")
			-- cenario de fundo, calcamento e relva: sombra propria nao acrescenta nada e sao as
			-- familias mais numerosas da cena (97 ladrilhos de relva, ~1.400 lajes de calcada)
			or nome:find("^LOB_serra") or nome:find("^LOB_nevoa") or nome:find("^LOB_calcada")
			or nome:find("^LOB_junta") or nome:find("^LOB_relva") or nome:find("^KIT_relva")
			or nome:find("^PATIO_base") or nome:find("^PATIO_marcos")
			or (i.t[3] * sz < 1.0))
		-- FIDELIDADE DE MALHA. A relva geometrica e o preco de nao ter alpha: sao ~890 mil triangulos
		-- nos 97 ladrilhos. Em Automatic o motor troca por versoes mais simples com a distancia, que e
		-- exatamente o que se quer num detalhe que so importa a poucos studs do jogador. O cenario de
		-- fundo vai em Performance: ele nunca e visto de perto e a silhueta se mantem.
		if nome:find("^LOB_serra") or nome:find("^LOB_nevoa") then
			m.RenderFidelity = Enum.RenderFidelity.Performance
		elseif nome:find("^KIT_relva") or nome:find("^LOB_relva") then
			m.RenderFidelity = Enum.RenderFidelity.Automatic
		end
		m.Size = Vector3.new(i.t[1] * sx, i.t[3] * sz, i.t[2] * sy)
		local cf = CFrame.new(B(x, y, z)) * CFrame.Angles(0, math.rad(rot), 0)
		m.CFrame = cf * CFrame.new(B(i.c[1] * sx, i.c[2] * sy, i.c[3] * sz))
		m.Parent = grupo(nome); n += 1
	end
end
-- 2) COLISAO simples e invisivel (as MeshParts nao colidem)
local COL = Instance.new("Folder"); COL.Name = "Colisao"; COL.Parent = ROOT
local function caixa(nome, x0, x1, y0, y1, z0, z1)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.Transparency = 1; p.CastShadow = false; p.CanQuery = false
	p.CanTouch = false   -- sem isto o chao_geral (356 x 410) dispara Touched a cada passo de cada jogador
	p.Size = Vector3.new(math.abs(x1 - x0), math.abs(z1 - z0), math.abs(y1 - y0))
	p.CFrame = CFrame.new(B((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); p.Parent = COL; return p
end
-- CHAO GERAL: sem isto o jogador cai no vazio assim que sai do patio (achado na verificacao geometrica).
-- Fica 0.5 abaixo do topo para o piso de pedra do patio/via prevalecer onde existe.
-- O chao_geral era UMA caixa so cobrindo tudo, inclusive a planta do lago: com o topo em Y=-0.5 e a
-- lamina em Y=0.45, a agua virava uma pelicula de meio stud e o leito modelado (LAGO_leito, 2.7 de
-- espessura) nunca aparecia. Agora ele e recortado em volta do lago e o fundo do lago ganha piso
-- proprio, 2 studs mais fundo: da profundidade de vadear, mostra o leito e ninguem cai do mundo.
local LX0, LX1, LY0, LY1 = -101.5, -68.5, -71.5, 131.5
caixa("chao_oeste", -178, LX0, -212, 198, -2.5, -0.5)
caixa("chao_leste", LX1, 178, -212, 198, -2.5, -0.5)
caixa("chao_sul", LX0, LX1, -212, LY0, -2.5, -0.5)
caixa("chao_norte", LX0, LX1, LY1, 198, -2.5, -0.5)
caixa("lago_fundo", LX0, LX1, LY0, LY1, -4.6, -2.6)
caixa("patio", -70, 70, -62, 62, -1, 0)                       -- piso do patio (Blender z=0 -> Roblox Y=0)
caixa("patio_spawn", -24, 24, -92, -60, -1, 0)                -- faixa entre o patio e o pe da escadaria (onde o spawn cai)
caixa("via", -16, 16, 60, 140, -1, 0.05)
caixa("soleira_portao", -46, 46, 140, 178, -1, 0)
''' + _colisao_das_cotas() + '''
caixa("pedestal_espada", -12, 12, -12, 12, 0, 6)
-- ponte-lua: degraus curtos acompanhando o arco
for i = 0, 15 do
	local t0, t1 = i / 16, (i + 1) / 16
	local x0, x1 = -100 + 30 * t0, -100 + 30 * t1
	local h = 4.6 * math.sin(math.pi * (t0 + t1) / 2) + 1.25
	caixa("ponte" .. i, x0, x1, -4.5, 4.5, 0, h)
end
-- muralhas e muros (bloqueiam)
caixa("muro_portao_W", -46, -29, 140, 160, 0, 16); caixa("muro_portao_E", 29, 46, 140, 160, 0, 16)
caixa("muro_portao_C1", -17, -11, 140, 160, 0, 16); caixa("muro_portao_C2", 11, 17, 140, 160, 0, 16)
for _, sx in ipairs({ -1, 1 }) do caixa("muralha" .. sx, sx * 46, sx * 152, 146, 154, 0, 10.4) end   -- comecava em 48 e deixava fresta de 2 studs
-- paredes dos edificios
caixa("forja_fundo", -36, 36, -148, -144, 9.98, 26); caixa("forja_E", 34, 38, -148, -120, 9.98, 26); caixa("forja_W", -38, -34, -148, -120, 9.98, 26)
-- a parede da fachada da Forja tem DUAS portas (x +-18 no Blender): a caixa inteira barrava a entrada e deixava o
-- Ignis inalcancavel (achado no teste de alcance do prompt).
caixa("forja_parede_W", -36, -22, -124, -120, 9.98, 26)
caixa("forja_parede_C", -14, 14, -124, -120, 9.98, 26)
caixa("forja_parede_E", 22, 36, -124, -120, 9.98, 26)
caixa("sant_fundo", -146, -142, -45, 45, 6.38, 18); caixa("sant_N", -146, -104, 39, 43, 6.38, 18); caixa("sant_S", -146, -104, -43, -39, 6.38, 18)
caixa("loja_fundo", 126, 130, -24, 16, 7.98, 19); caixa("loja_N", 104, 130, 12, 16, 7.98, 19)
-- contrafortes dos seis portais. Sem isto o jogador atravessa a pedra e cai no portal do lado, porque
-- MeshPart nao colide. O vao fica LIVRE de proposito: e por ele que se chega ao disco de teleporte.
for _, zy in ipairs({ -32.5, -19.5, -6.5, 6.5, 19.5, 32.5 }) do
	for _, s in ipairs({ -1, 1 }) do
		local a, b = zy + s * 4.4, zy + s * 5.7
		caixa("portal_pilar", -126.5, -122.5, math.min(a, b), math.max(a, b), 6.38, 15.9)
	end
end
-- limites do mundo: penhascos
-- A muralha agora esta em x=+-158 e y=-192..150. A parede invisivel tem de ficar ATRAS dela, senao o
-- jogador esbarra no vazio antes de chegar ao muro e o recinto parece menor do que e.
caixa("limite_N", -184, 184, -200, -192, -1, 46); caixa("limite_W", -172, -158, -200, 160, -1, 46); caixa("limite_E", 158, 172, -200, 160, -1, 46)
caixa("limite_S_W", -172, -46, 150, 164, -1, 36); caixa("limite_S_E", 46, 172, 150, 164, -1, 36)
-- Os penhascos do sul comecavam em |x|=60 e o chao acabava em y=198: sobrava um corredor de 14 studs
-- de cada lado da estrada, com piso e parede, terminando no vazio. Agora eles fecham em |x|=46, que e
-- onde a estrada (Corredores.Lobby_Area1) realmente acaba.
-- O FBX importado servia so de banco de templates e ficava no Workspace com 154 pecas NAO
-- ancoradas e colidindo, penduradas acima do lobby. Assim que o servidor subisse elas despencavam
-- sobre o patio e sobre os vaos dos portais. Depois de clonar, ele vai para o ServerStorage.
KIT.Parent = SS
local f = {}; for k in pairs(faltam) do table.insert(f, k) end
return string.format("montadas %d de %d pecas | colisao %d partes | malhas sem template: %s", n, #PLACE, #COL:GetChildren(), (#f > 0 and table.concat(f, ", ") or "nenhuma"))''')
src = '\n'.join(L)
open(os.path.join(E, 'montar_lobby.lua'), 'w', encoding='utf-8').write(src)
sem = sorted({p['mesh'] for p in place} - set(info))
print('tiradas de dentro do lago: %d pecas (%s)' % (len(afogadas), ', '.join(sorted({q['mesh'] for q in afogadas}))))
print('montar_lobby.lua: %d bytes | %d malhas | %d colocacoes | sem medida: %s' % (len(src.encode()), len(info), len(place), sem or 'nenhuma'))
