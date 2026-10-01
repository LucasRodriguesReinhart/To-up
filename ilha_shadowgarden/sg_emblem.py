# sg_emblem - SISTEMA DE IDENTIDADE da Ilha 3 (Shadow Garden). COMPARTILHADO E CONGELADO (dono: integracao).
# Um UNICO simbolo da ordem, original (nao e logo de obra nenhuma): a LUA EM ECLIPSE.
#   - anel externo de prata (a moldura nobre)
#   - campo negro (a lua apagada) e o CRESCENTE violeta luminoso (a parte que a sombra ainda nao comeu: "a eminencia
#     nas sombras")
#   - 8 raios curtos de prata fora do anel (so na versao 'monumental')
# AJUSTE 19 (2026-09-30, pedido do usuario: "tire a espada do logo da lua, acaba estragando o visual"): a ESPADA saiu do
#   simbolo (lamina, guarda, cabo e pomo). O crescente foi recomposto para o anel vazio: simetrico no eixo horizontal
#   (pontas para a direita de quem olha), centrado pela caixa (pontas e dorso a mesma distancia do centro) e um pouco
#   menor que o de antes para as pontas respirarem dentro do anel tambem nos emblemas pequenos (traco engrossado).
#   As espadas das estatuas/guardas NAO sao do simbolo e continuam.
# Todo lugar que fala pela ordem usa ESTE simbolo: fachada do castelo, estandartes, portoes, piso do salao, dungeon,
# porticos da entrada. Nada de tridente/estrela/lua soltos (ornamento sem sistema = cara de IA).
#
# ACABAMENTO 2026-09-29: o simbolo virou ASSET PROPRIO de malha limpa (nada de caixas empilhadas):
#   - cada peca e um perfil 2D desenhado no plano do emblema e extrudado com chanfro (casca fechada, normais por peca);
#   - anel = coroa circular continua de 32 segmentos (40 nos grandes; vertices nos eixos = simetrica) com chanfro de
#     45 graus nas duas arestas;
#   - crescente = UM poligono (diferenca de dois circulos calculada), extrudado e chanfrado; o campo negro fica ATRAS
#     (nao ha mais disco claro com disco escuro por cima);
#   - raios em secao de losango (aresta central) com a MESMA inclinacao de faceta;
#   - camadas em profundidade sem nada coplanar (fracoes de 'depth'): campo -0,04..0,12 | crescente 0,04..0,30 |
#     anel -0,05..0,50 | raios ate ~0,32;
#   - traco do anel engrossado de leve nos emblemas pequenos (legivel de longe).
#   Estandarte: verga redonda com luva de tecido e remates de prata torneados; pano com dobras, abaulado e borlas (ver
#   OVERHAUL 12 em banner()); debrum continuo com espessura contornando laterais e V com esquadria limpa. Placa: disco
#   de obsidiana chanfrado. Lanternas: travessa superior que assenta a tampa, beiral, remate; capitel do poste encosta
#   na base.
# OVERHAUL 12 (2026-09-29): crescente em Neon (MOON) SO no emblema monumental, no trono e no caldeirao; estandartes e
#   placas levam o crescente SEM emissao em lilas-prata palido (15.05). Placa so na porta do castelo, no caldeirao e no
#   fecho da dungeon (12.11). Pedestal de lanterna em UM perfil de torno quadrado (sem caixas empilhadas).
#
# API (todas desenham em MBs que o modulo chamador ja criou; nada de colisao aqui):
#   emblem(mb_metal, mb_glow, mb_dark, c, yaw, r, depth=0.6, monumental=False, glow=MOON)
#       c = (x, y, z) centro; yaw = rumo (rad) para onde o simbolo OLHA; r = raio do anel externo
#   banner(mb_cloth, mb_metal, mb_glow, mb_dark, top, yaw, w, h, tails=True, trim=None)
#       estandarte da ordem: tecido roxo profundo com barra negra e borda de prata, emblema em cima, ponta em V;
#       2 larguras (BANNER_NARROW 2,6 / BANNER_WIDE 3,8)
#   plaque(mb_stone, mb_metal, mb_glow, mb_dark, c, yaw, r, glow=None)   (None = crescente lilas-prata palido, sem emissao)
#       medalhao de pedra obsidiana com o emblema (portais, pedestais, fontes)
#   emblem_flat(mb_metal, mb_glow, mb_dark, c, yaw, r, monumental=False, up=1, glow=MOON, field=True, seg=None)
#       o mesmo simbolo DEITADO e rente (incrustacao de piso / chave de teto); yaw = rumo do "alto" do simbolo
#   lantern_head / lantern_pedestal / lantern_post (abaixo)
# Materiais: Metal_SG_Silver (prata), SG_Rune_Glow (lua), Stone_SG_Obsidian (sombra/campo), Cloth_SG_Purple (tecido).
import math
import bmesh

SILVER, MOON, SHADOW, CLOTH, TRIM = "Metal_SG_Silver", "SG_Rune_Glow", "Stone_SG_Obsidian", "Cloth_SG_Purple", "Stone_SG_Obsidian"
IRON = "Metal_SG_BlackIron"
# crescente SEM emissao (estandartes e placas, 15.05): lilas-prata PALIDO (SmoothPlastic no Roblox). Testado no modo
# roblox: a pedra violeta some no campo de obsidiana e a prata funde com o anel; o palido le a lua e separa do anel
QUIET = "Stone_SG_MoonPale"      # (registrado no sg_lib.SMATS)

# ---------------------------------------------------------------- desenho do simbolo (unidades de r, a = lateral, b = cima)
RING_OUT = 0.97                  # borda externa do anel
RING_W = 0.14                    # largura do anel (traco principal)
# crescente (ajuste 19, sem a espada): lua de raio MOON_R com centro deslocado MOON_C para a direita e sombra de raio
# SHADOW_R deslocada SHADOW_DX da lua, no mesmo eixo (simetrico em cima/embaixo). Pontas em (+0,48; +-0,51) e dorso
# em -0,48: a caixa do crescente fica centrada no anel; pontas a 0,71 do centro (anel por dentro: 0,83 / 0,77 nos
# emblemas pequenos), espessura maxima 0,37
MOON_R = 0.62
MOON_C = 0.137
SHADOW_DX, SHADOW_R = 0.27, 0.52
FACET_HW = 0.068                 # meia-largura de referencia da inclinacao das facetas (raios)
N_FIELD = 24                     # o campo so aparece por dentro do anel (a borda dele fica escondida sob o anel)


def _nseg(r):
    """segmentos do anel (multiplo de 4: vertices nos eixos, simetria mantida) e de cada arco do crescente"""
    return (32, 16) if r < 2.0 else (40, 22)


def _frame(c, yaw):
    """eixos do plano do emblema: f = normal (para onde olha), u = direita, z = cima"""
    fx, fy = math.cos(yaw), math.sin(yaw)
    ux, uy = math.sin(yaw), -math.cos(yaw)       # direita de quem OLHA o emblema de frente
    return (fx, fy), (ux, uy)


def _p(c, f, u, a, b, d):
    """ponto no plano: a = lateral (u), b = altura, d = profundidade (ao longo de f)"""
    return (c[0] + u[0] * a + f[0] * d, c[1] + u[1] * a + f[1] * d, c[2] + b)


def _W(c, f, u):
    return lambda a, b, d: _p(c, f, u, a, b, d)


# ---------------------------------------------------------------- construtores de malha limpa
def _clean(vs):
    """tira vertices repetidos em sequencia (pontas em que duas arestas convergem num vertice so)"""
    out = []
    for v in vs:
        if not out or out[-1] is not v:
            out.append(v)
    while len(out) > 1 and out[0] is out[-1]:
        out.pop()
    return out


def _shell(mb, loops, m, cap0="ngon", cap1="ngon", strip_n=None):
    """casca fechada por lacos de mesma contagem (fundo -> ... -> frente). cap 'ngon' (laco convexo) ou 'strip'
    (crescente: arco externo O0..ON + arco interno de volta, costurados em faixa O_i <-> I_i)"""
    bm = mb.bm
    V = [[bm.verts.new(p) for p in lp] for lp in loops]
    n = len(loops[0])
    faces = []
    for L0, L1 in zip(V, V[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new((L0[i], L0[j], L1[j], L1[i])))
    for cap, L in ((cap0, V[0]), (cap1, V[-1])):
        if cap == "ngon":
            faces.append(bm.faces.new(L))
        elif cap == "strip":
            N = strip_n
            for i in range(N):
                vs = _clean([L[i], L[i + 1], L[(2 * N - i - 1) % (2 * N)], L[(2 * N - i) % (2 * N)]])
                if len(vs) >= 3:
                    faces.append(bm.faces.new(vs))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for L in V for v in L], m, None, 0, 1)


def _ring_loops(P, R, n, d, cx=0.0, cy=0.0, ph=0.0):
    return [P(cx + R * math.cos(ph + 2 * math.pi * k / n), cy + R * math.sin(ph + 2 * math.pi * k / n), d)
            for k in range(n)]


def _disc(mb, P, R, d0, d1, m, n=32, ch=0.0, cx=0.0, cy=0.0):
    """disco no plano (a, b) de d0 (fundo) a d1 (frente), chanfro de 45 graus na aresta da frente"""
    if ch > 0:
        loops = [_ring_loops(P, R, n, d0, cx, cy), _ring_loops(P, R, n, d1 - ch, cx, cy),
                 _ring_loops(P, R - ch, n, d1, cx, cy)]
    else:
        loops = [_ring_loops(P, R, n, d0, cx, cy), _ring_loops(P, R, n, d1, cx, cy)]
    _shell(mb, loops, m)


def _annulus(mb, P, r_in, r_out, d0, d1, ch, m, n=36):
    """coroa circular continua: perfil (fundo externo, chanfro externo, topo, chanfro interno, fundo interno) varrido"""
    prof = [(r_out, d0), (r_out, d1 - ch), (r_out - ch, d1), (r_in + ch, d1), (r_in, d1 - ch), (r_in, d0)]
    bm = mb.bm
    rings = []
    for k in range(n):
        t = 2 * math.pi * k / n
        ct, st = math.cos(t), math.sin(t)
        rings.append([bm.verts.new(P(rr * ct, rr * st, dd)) for rr, dd in prof])
    faces = []
    m_ = len(prof)
    for k in range(n):
        A, B = rings[k], rings[(k + 1) % n]
        for i in range(m_):
            j = (i + 1) % m_
            faces.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for rg in rings for v in rg], m, None, 0, 1)


def _circ_x(c1, r1, c2, r2):
    """intersecao de dois circulos: (ponto de cima, ponto de baixo) em relacao ao eixo c1->c2"""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    ex, ey = dx / d, dy / d
    a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 1e-9))
    bx, by = c1[0] + ex * a, c1[1] + ey * a
    return (bx - ey * h, by + ex * h), (bx + ey * h, by - ex * h)


def _crescent_loop(P, R1, c2, R2, N, d):
    """UM poligono de crescente = circulo (0,0,R1) menos circulo (c2,R2): arco externo de ponta a ponta passando pelo
    lado oposto a sombra + arco interno de volta; N segmentos em cada arco, pontas compartilhadas (2N vertices)"""
    hp, hm = _circ_x((0.0, 0.0), R1, c2, R2)
    t0 = math.atan2(hp[1], hp[0])
    ta = (math.atan2(hm[1], hm[0]) - t0) % (2 * math.pi)
    p0 = math.atan2(hp[1] - c2[1], hp[0] - c2[0])
    pa = (math.atan2(hm[1] - c2[1], hm[0] - c2[0]) - p0) % (2 * math.pi)
    outer = [(R1 * math.cos(t0 + ta * j / N), R1 * math.sin(t0 + ta * j / N)) for j in range(N + 1)]
    outer[0], outer[N] = hp, hm
    inner = [(c2[0] + R2 * math.cos(p0 + pa * j / N), c2[1] + R2 * math.sin(p0 + pa * j / N)) for j in range(1, N)]
    pts = outer + list(reversed(inner))
    return [P(a, b, d) for a, b in pts]


def _bar(mb, P, m, o, ax, st, d0, de, k):
    """peca de secao em LOSANGO ao longo de um eixo: estacoes (s, meia-largura) a partir de o na direcao ax; arestas
    laterais na profundidade de, aresta central (cumeeira) em de + k * meia-largura (mesma inclinacao de faceta em
    todas as pecas); fundo reto em d0. Meia-largura 0 = ponta (as arestas convergem num vertice)."""
    bm = mb.bm
    nx, ny = -ax[1], ax[0]
    Lf, Rf, Rg, Lb, Rb = [], [], [], [], []
    for s, hw in st:
        pa, pb = o[0] + ax[0] * s, o[1] + ax[1] * s
        if hw <= 1e-6:
            t = bm.verts.new(P(pa, pb, de))
            tb = bm.verts.new(P(pa, pb, d0))
            Lf.append(t), Rf.append(t), Rg.append(t), Lb.append(tb), Rb.append(tb)
        else:
            Lf.append(bm.verts.new(P(pa + nx * hw, pb + ny * hw, de)))
            Rf.append(bm.verts.new(P(pa - nx * hw, pb - ny * hw, de)))
            Rg.append(bm.verts.new(P(pa, pb, de + k * hw)))
            Lb.append(bm.verts.new(P(pa + nx * hw, pb + ny * hw, d0)))
            Rb.append(bm.verts.new(P(pa - nx * hw, pb - ny * hw, d0)))
    faces = []

    def F(vs):
        vs = _clean(vs)
        if len(vs) >= 3:
            faces.append(bm.faces.new(vs))
    for i in range(len(st) - 1):
        j = i + 1
        F([Lf[i], Lf[j], Rg[j]])
        F([Lf[i], Rg[j], Rg[i]])
        F([Rg[i], Rg[j], Rf[j]])
        F([Rg[i], Rf[j], Rf[i]])
        F([Lb[i], Lb[j], Lf[j], Lf[i]])
        F([Rf[i], Rf[j], Rb[j], Rb[i]])
        F([Rb[i], Rb[j], Lb[j], Lb[i]])
    for i in (0, len(st) - 1):
        if st[i][1] > 1e-6:
            F([Lb[i], Lf[i], Rg[i], Rf[i], Rb[i]])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(list({v for f_ in faces for v in f_.verts}), m, None, 0, 1)


def _band(mb, P, path, tw, d0, d1, m):
    """faixa de largura tw ao longo de uma polilinha aberta (debrum): um lado na propria linha, o outro deslocado para
    a ESQUERDA do caminho com esquadria (miter) nos cantos; extrudada de d0 a d1, casca fechada"""
    n = len(path)
    nrm = []
    for i in range(n - 1):
        dx, dy = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        L = math.hypot(dx, dy)
        nrm.append((-dy / L, dx / L))
    inner = []
    for i in range(n):
        if i == 0:
            mx, my = nrm[0]
        elif i == n - 1:
            mx, my = nrm[-1]
        else:
            a, b = nrm[i - 1], nrm[i]
            s = 1.0 + a[0] * b[0] + a[1] * b[1]
            mx, my = (a[0] + b[0]) / s, (a[1] + b[1]) / s
        inner.append((path[i][0] + mx * tw, path[i][1] + my * tw))
    bm = mb.bm
    O0 = [bm.verts.new(P(a, b, d0)) for a, b in path]
    O1 = [bm.verts.new(P(a, b, d1)) for a, b in path]
    I0 = [bm.verts.new(P(a, b, d0)) for a, b in inner]
    I1 = [bm.verts.new(P(a, b, d1)) for a, b in inner]
    faces = []
    for i in range(n - 1):
        j = i + 1
        faces.append(bm.faces.new((O1[i], O1[j], I1[j], I1[i])))    # frente
        faces.append(bm.faces.new((I0[i], I0[j], O0[j], O0[i])))    # fundo
        faces.append(bm.faces.new((O0[i], O0[j], O1[j], O1[i])))    # borda externa
        faces.append(bm.faces.new((I1[i], I1[j], I0[j], I0[i])))    # borda interna
    for i in (0, n - 1):
        faces.append(bm.faces.new((O0[i], O1[i], I1[i], I0[i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(O0 + O1 + I0 + I1, m, None, 0, 1)


def _prism(mb, P, pts, d0, d1, m):
    """poligono CONVEXO do plano (a, b) extrudado de d0 a d1"""
    _shell(mb, [[P(a, b, d0) for a, b in pts], [P(a, b, d1) for a, b in pts]], m)


# ---------------------------------------------------------------- o simbolo
def _emblem_geo(mb_metal, mb_glow, mb_dark, P, r, lay, monumental=False, glow=MOON, field=True, seg=None):
    """o simbolo no plano (a, b) mapeado por P(a, b, d); 'lay' = camadas de profundidade (d0, d1) de cada peca + k
    (inclinacao das facetas), ch (chanfro) e chc (chanfro do crescente). Usado de pe (emblem) e deitado (emblem_flat)."""
    kb = min(1.4, max(1.0, 0.8 / r))              # emblemas pequenos: traco um pouco mais grosso (legivel de longe)
    w = RING_W * r * kb
    ro = RING_OUT * r
    ri = ro - w
    ch, chc, k = lay["ch"], lay["chc"], lay["k"]
    n_ring, n_moon = _nseg(r) if seg is None else (seg, max(8, seg // 2))
    # 1) campo negro (a lua apagada), escondido sob o anel pela borda
    if field:
        _disc(mb_dark, P, ri + 0.4 * w, lay["field"][0], lay["field"][1], SHADOW, n=N_FIELD)
    # 2) crescente violeta: um poligono so, chanfrado (lua deslocada MOON_C para a caixa ficar centrada no anel)
    Pm = lambda a, b, d: P(a + MOON_C * r, b, d)
    c2 = (SHADOW_DX * r, 0.0)
    R1, R2 = MOON_R * r, SHADOW_R * r
    m0, m1 = lay["moon"]
    loops = [_crescent_loop(Pm, R1, c2, R2, n_moon, m0), _crescent_loop(Pm, R1, c2, R2, n_moon, m1 - chc),
             _crescent_loop(Pm, R1 - chc, c2, R2 + chc, n_moon, m1)]
    _shell(mb_glow, loops, glow, "strip", "strip", strip_n=n_moon)
    # 3) anel de prata continuo
    _annulus(mb_metal, P, ri, ro, lay["ring"][0], lay["ring"][1], ch, SILVER, n=n_ring)
    # 4) raios de prata (so no monumental): saem de baixo do anel, longos perto da horizontal, curtos perto da vertical
    #    (simetrico nos dois eixos). A espada saiu do simbolo (ajuste 19).
    if monumental:
        for q in range(8):
            t = math.pi / 8 + q * math.pi / 4
            longo = abs(math.cos(t)) > 0.7
            L = r * (0.34 if longo else 0.22)
            hwr = r * (0.050 if longo else 0.040) * kb
            _bar(mb_metal, P, SILVER, (0.0, 0.0), (math.cos(t), math.sin(t)),
                 ((ro - 0.6 * w, hwr), (ro + 0.02 * r, hwr * 0.92), (0.98 * r + L, 0.0)),
                 lay["rays"][0], lay["rays"][1], k)


def emblem(mb_metal, mb_glow, mb_dark, c, yaw, r, depth=0.6, monumental=False, glow=MOON):
    """glow = material do crescente: MOON (Neon) SO no emblema monumental, no trono e no caldeirao (15.05); nos
    estandartes e placas, QUIET (lilas-prata palido, sem emissao)"""
    f, u = _frame(c, yaw)
    P = _W(c, f, u)
    D = depth
    kb = min(1.4, max(1.0, 0.8 / r))
    w = RING_W * r * kb
    ch = min(0.032 * r, 0.12 * D, 0.22 * w)       # o MESMO chanfro no anel e no crescente
    seg = 24 if r < 1.2 else None                  # overhaul 12: emblema pequeno (estandarte/placa) com anel de 24
    lay = {"ch": ch, "chc": min(ch, 0.06 * D), "k": min(1.0, max(0.3, 0.12 * D / (FACET_HW * r * kb))),
           # ONDA 3 (z-fight): o fundo do campo negro ia a -0,04 D, a 0,01 D do fundo do anel de prata (os 2 de costas,
           # sobrepostos na faixa do anel): agora fica 0,05 atras do fundo do anel (embutido no suporte quando ha um)
           "field": (-0.05 * D - 0.05, 0.12 * D), "moon": (0.04 * D, 0.30 * D), "ring": (-0.05 * D, 0.50 * D),
           "rays": (-0.045 * D, 0.22 * D)}
    _emblem_geo(mb_metal, mb_glow, mb_dark, P, r, lay, monumental, glow, seg=seg)


def emblem_flat(mb_metal, mb_glow, mb_dark, c, yaw, r, monumental=False, up=1, glow=MOON, field=True, seg=None):
    """o MESMO simbolo DEITADO, como incrustacao RENTE (piso ou chave de teto): c = (x, y, z da superficie), yaw = rumo
    (rad) para onde o "alto" do simbolo aponta na planta, r = raio do anel externo. up=+1: face para cima (piso);
    up=-1: face para baixo (chave/teto). Mesma logica de camadas, mas em alturas ABSOLUTAS: tudo sobe no maximo ~0,056
    acima da superficie (nada em que tropecar) e os fundos ficam embutidos nela. Visto de cima com o "alto" para
    a frente, as pontas do crescente apontam para a direita (igual ao emblema de pe). glow = material do crescente (ex. um Neon mais fraco
    no piso); field=False dispensa o campo negro quando a superficie ja e de obsidiana; seg = segmentos do anel
    (multiplo de 4) para chaves pequenas."""
    vx, vy = math.cos(yaw), math.sin(yaw)
    ux, uy = -vy * up, vx * up
    cx, cy, cz = c

    def P(a, b, d):
        return (cx + ux * a + vx * b, cy + uy * a + vy * b, cz + up * d)
    kb = min(1.4, max(1.0, 0.8 / r))
    ch = min(0.032 * r, 0.008)
    lay = {"ch": ch, "chc": min(ch, 0.006), "k": 0.012 / (FACET_HW * r * kb),
           "field": (-0.10, 0.010), "moon": (-0.06, 0.020), "ring": (-0.12, 0.030), "rays": (-0.11, 0.024)}
    _emblem_geo(mb_metal, mb_glow, mb_dark, P, r, lay, monumental, glow, field, seg)


def plaque(mb_stone, mb_metal, mb_glow, mb_dark, c, yaw, r, glow=None):
    """medalhao: disco de obsidiana chanfrado (fundo em -0,5, frente em 0) com o emblema assentado (fundo embutido).
    OVERHAUL 12 (12.11/15.05): a placa fica SO na porta do castelo, no caldeirao e no fecho da dungeon; o crescente e
    lilas-prata palido SEM emissao (glow=MOON so no caldeirao)."""
    f, u = _frame(c, yaw)
    P = _W(c, f, u)
    R = r * 1.12
    _disc(mb_stone, P, R, -0.5, 0.0, TRIM, n=24 if R < 1.5 else 32, ch=min(0.14, max(0.04, 0.06 * R)))   # ov12: 24 nas pequenas
    emblem(mb_metal, mb_glow, mb_dark, _p(c, f, u, 0, 0, 0.0), yaw, r * 0.92, depth=0.45, glow=glow or QUIET)


# OVERHAUL 12 (2026-09-29, 12.05/15.05/16.02): o estandarte deixa de ser placa pentagonal rigida.
#   - pano com SECAO ONDULADA: painel central plano (o emblema assenta nele) e UMA dobra vertical em crista de cada lado;
#     as bordas voltam para tras. As dobras nascem pequenas na luva (o pano franzido na verga) e abrem ate a barra
#     negra; na ponta em V estreitam junto com o pano (tudo converge na ponta);
#   - leve ABAULADO para a frente no terco de baixo (a ponta sai ~3% da altura);
#   - barra negra TECIDA no pano (as faces daquela faixa, nada colado por cima) e debrum com espessura que segue as
#     dobras; BORLAS pequenas (torno de 6) nas 2 quinas e na ponta do V;
#   - 2 LARGURAS so (estreito 2,6 / largo 3,8, escolhida pelo chamador; um w intermediario cai no estreito). A verga
#     continua do tamanho do w pedido (os bracos dos modulos seguem encostando); o pano nunca fica mais largo que o w;
#   - crescente SEM emissao em lilas-prata palido (Stone_SG_MoonPale); remate da verga em torno (colar + bulbo + ponta), sem cone.
BANNER_NARROW, BANNER_WIDE = 2.6, 3.8
# secao (t = -1..1 da meia-largura, d em unidades da amplitude)
_BN_SEC = ((-1.0, -0.4), (-0.87, 1.0), (-0.74, 0.0), (0.74, 0.0), (0.87, 1.0), (1.0, -0.4))   # painel central
# plano ate 0,74 (o medalhao grande cabe inteiro nele) e a dobra lateral em crista ingreme: os 2 flancos da dobra
# ficam de lado para a luz e leem mais escuros que o painel


def _pl(xs, ys, x):
    """interpolacao linear por partes (xs crescente)"""
    if x <= xs[0]:
        return ys[0]
    for k in range(len(xs) - 1):
        if x <= xs[k + 1]:
            f = (x - xs[k]) / (xs[k + 1] - xs[k])
            return ys[k] + (ys[k + 1] - ys[k]) * f
    return ys[-1]


def _lathe_ax(mb, o, ax, prof, m, n=8):
    """solido de revolucao em torno do eixo ax (unitario) a partir de o: prof = [(raio, distancia)], raio 0 = polo"""
    ax = tuple(ax)
    ref = (0.0, 0.0, 1.0) if abs(ax[2]) < 0.9 else (1.0, 0.0, 0.0)
    e1 = (ax[1] * ref[2] - ax[2] * ref[1], ax[2] * ref[0] - ax[0] * ref[2], ax[0] * ref[1] - ax[1] * ref[0])
    L_ = math.sqrt(sum(v * v for v in e1))
    e1 = tuple(v / L_ for v in e1)
    e2 = (ax[1] * e1[2] - ax[2] * e1[1], ax[2] * e1[0] - ax[0] * e1[2], ax[0] * e1[1] - ax[1] * e1[0])
    bm = mb.bm
    rows = []
    for r, d in prof:
        c = tuple(o[i] + ax[i] * d for i in range(3))
        if r < 1e-5:
            rows.append([bm.verts.new(c)])
        else:
            rows.append([bm.verts.new(tuple(c[i] + r * (math.cos(2 * math.pi * k / n) * e1[i] +
                                                        math.sin(2 * math.pi * k / n) * e2[i]) for i in range(3)))
                         for k in range(n)])
    faces = []
    for A, B in zip(rows, rows[1:]):
        for k in range(n):
            j = (k + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new((A[0], B[k], B[j])))
            elif len(B) == 1:
                faces.append(bm.faces.new((A[k], A[j], B[0])))
            else:
                faces.append(bm.faces.new((A[k], A[j], B[j], B[k])))
    for R in (rows[0], rows[-1]):
        if len(R) > 1:
            faces.append(bm.faces.new(R))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for r in rows for v in r], m, None, 0, 1)


def _tassel(mb, P, a, b, d, s, m):
    """borla pendurada: o topo (cordao) entra 0,06 no pano em (a, b, d); s = escala"""
    prof = [(0.0, 0.0), (0.14, 0.06), (0.09, 0.44), (0.10, 0.58), (0.0, 0.80)]     # saia, cabeca, cordao
    top = P(a, b + 0.06, d)
    _lathe(mb, (top[0], top[1], top[2] - 0.80 * s), [(r * s, h * s) for r, h in prof], m, 5)


def banner(mb_cloth, mb_metal, mb_glow, mb_dark, top, yaw, w, h, tails=True, trim=None):
    """estandarte pendurado por uma verga de ferro/prata em 'top' (centro da verga), olhando para yaw"""
    f, u = _frame(top, yaw)
    P = _W(top, f, u)
    yu = math.atan2(u[1], u[0])
    # verga redonda de ferro negro (comprimento pelo w PEDIDO: os bracos dos modulos continuam encostando)
    half = w / 2 + 0.35
    mb_metal.cyl(0.14, 2 * half, P(0, 0, 0), (0, math.pi / 2, yu), m=IRON, n=8, bevel=0.0)
    for s in (-1, 1):
        o = P(s * (half - 0.07), 0, 0)
        _lathe_ax(mb_metal, o, (s * u[0], s * u[1], 0.0),
                  [(0.19, 0.0), (0.19, 0.12), (0.16, 0.3), (0.0, 0.52)], SILVER, 6)          # colar, bulbo, ponta
    w = BANNER_WIDE if w >= 3.6 else min(w, BANNER_NARROW)     # 2 larguras so (nunca mais largo que o pedido)
    th = 0.12                     # espessura do pano
    dc = 0.03                     # plano medio do pano (a verga fica em d = 0)
    hw = w / 2.0
    mb_cloth.cyl(0.22, w, P(0, 0, dc * 0.5), (0, math.pi / 2, yu), m=CLOTH, n=8, bevel=0.0)   # luva
    body_h = h * (0.84 if tails else 1.0)
    bt = -0.05                    # topo do pano (dentro da luva)
    zb = -body_h - 0.15
    zt = zb - h * 0.16 if tails else zb
    zl = bt + (zt - bt) * 0.62    # comeco do terco de baixo (abaulado)
    amp = 0.12 * w
    bulge = 0.035 * h
    # linhas do pano: (z, fator da amplitude: as dobras abrem ate a barra); barra negra entre as linhas 1 e 2
    rows = [(bt, 0.3), (-h * 0.05, 0.6), (-h * 0.13, 1.0), (zl, 1.0), ((zl + zb) / 2, 1.0), (zb, 1.0)]
    if tails:
        rows += [((zb + zt) / 2, 1.0), (zt, 1.0)]
    zs = [r_[0] for r_ in rows][::-1]
    As = [r_[1] for r_ in rows][::-1]
    ts = [t for t, _ in _BN_SEC]
    ds = [d for _, d in _BN_SEC]

    def halfw(z):
        if not tails or z >= zb:
            return hw
        return hw * max(0.0, (z - zt) / (zb - zt))

    def D(a, z):
        """profundidade do plano medio do pano em (a, z)"""
        k = halfw(z) / hw
        t = a / halfw(z) if halfw(z) > 1e-6 else 0.0
        bz = bulge * ((zl - z) / (zl - zt)) ** 2 if z < zl else 0.0
        return dc + amp * _pl(zs, As, z) * k * _pl(ts, ds, t) + bz
    bm = mb_cloth.bm
    Fr, Bk = [], []
    for z, _ in rows:
        hz = halfw(z)
        if hz < 1e-6:
            cols = [0.0]
        else:
            cols = [t * hz for t in ts]
        Fr.append([bm.verts.new(P(a, z, D(a, z) + th / 2)) for a in cols])
        Bk.append([bm.verts.new(P(a, z, D(a, z) - th / 2)) for a in cols])
    faces, bar = [], []
    for j in range(len(rows) - 1):
        A, B, A2, B2 = Fr[j], Fr[j + 1], Bk[j], Bk[j + 1]
        fj = []
        for i in range(len(A) - 1):
            if len(B) == 1:
                fj.append(bm.faces.new((A[i], A[i + 1], B[0])))
                fj.append(bm.faces.new((A2[i + 1], A2[i], B2[0])))
            else:
                fj.append(bm.faces.new((A[i], A[i + 1], B[i + 1], B[i])))
                fj.append(bm.faces.new((A2[i + 1], A2[i], B2[i], B2[i + 1])))
        # laterais (esquerda e direita)
        for iA, iB in ((0, 0), (len(A) - 1, len(B) - 1)):
            fj.append(bm.faces.new((A[iA], B[iB], B2[iB], A2[iA])))
        faces += fj
        if j == 1:
            bar += fj
    for i in range(len(Fr[0]) - 1):                                        # topo (dentro da luva)
        faces.append(bm.faces.new((Fr[0][i + 1], Fr[0][i], Bk[0][i], Bk[0][i + 1])))
    if not tails:
        for i in range(len(Fr[-1]) - 1):                                   # fundo reto
            faces.append(bm.faces.new((Fr[-1][i], Fr[-1][i + 1], Bk[-1][i + 1], Bk[-1][i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb_cloth._post([v for R in Fr + Bk for v in R], CLOTH, None, 0, 1)
    # barra negra tecida: as faces da faixa 1-2 trocam de material
    mi = mb_cloth._mi_for(SHADOW)
    for fc in bar:
        fc.material_index = mi
    mb_cloth._uv(set(bar), SHADOW)
    # debrum continuo (laterais + V) com espessura, seguindo as dobras
    tm = trim or SILVER
    tw = min(0.2, max(0.12, 0.05 * w))
    # ONDA 3 (z-fight): o debrum passa 0,06 PARA FORA da lateral do pano (a face de fora dele era coplanar com a
    # lateral do pano: pano x debrum tremia nos estandartes da muralha, dos porticos, da invocacao e do altar)
    eo = 0.06
    left = [(-halfw(z) - eo, z) for z, _ in rows]
    if tails:
        path = left[:-1] + [(0.0, zt - eo)] + [(-a, z) for a, z in reversed(left[:-1])]
    else:
        path = left + [(-a, z) for a, z in reversed(left)]
    _band_s(mb_metal, P, path, tw, D, th / 2 + 0.04, tm)
    # borlas nas pontas
    ts_ = 0.24 * w
    for a in (-hw, hw):
        _tassel(mb_metal, P, a * 0.97, zb, D(a * 0.97, zb), ts_, tm)
    if tails:
        _tassel(mb_metal, P, 0.0, zt, D(0.0, zt), ts_, tm)
    er = min(w * 0.36, h * 0.16)                  # o medalhao grande de antes (~70 % do pano)
    ze = -h * 0.36
    emblem(mb_metal, mb_glow, mb_dark, P(0, ze, D(0.0, ze) + th / 2), yaw, er, depth=0.28, glow=QUIET)


def _band_s(mb, P, path, tw, S, off, m):
    """faixa de largura tw ao longo de uma polilinha aberta do plano (a, b), deslocada para a ESQUERDA do caminho com
    esquadria; a profundidade de cada vertice vem da superficie S(a, b) +- off (o debrum abraca o pano nas dobras)"""
    n = len(path)
    nrm = []
    for i in range(n - 1):
        dx, dy = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        L_ = math.hypot(dx, dy)
        nrm.append((-dy / L_, dx / L_))
    inner = []
    for i in range(n):
        if i == 0:
            mx, my = nrm[0]
        elif i == n - 1:
            mx, my = nrm[-1]
        else:
            a, b = nrm[i - 1], nrm[i]
            s = 1.0 + a[0] * b[0] + a[1] * b[1]
            mx, my = (a[0] + b[0]) / s, (a[1] + b[1]) / s
        inner.append((path[i][0] + mx * tw, path[i][1] + my * tw))
    bm = mb.bm
    O0 = [bm.verts.new(P(a, b, S(a, b) - off)) for a, b in path]
    O1 = [bm.verts.new(P(a, b, S(a, b) + off)) for a, b in path]
    I0 = [bm.verts.new(P(a, b, S(a, b) - off)) for a, b in inner]
    I1 = [bm.verts.new(P(a, b, S(a, b) + off)) for a, b in inner]
    faces = []
    for i in range(n - 1):
        j = i + 1
        faces.append(bm.faces.new((O1[i], O1[j], I1[j], I1[i])))
        faces.append(bm.faces.new((I0[i], I0[j], O0[j], O0[i])))
        faces.append(bm.faces.new((O0[i], O0[j], O1[j], O1[i])))
        faces.append(bm.faces.new((I1[i], I1[j], I0[j], I0[i])))
    for i in (0, n - 1):
        faces.append(bm.faces.new((O0[i], O1[i], I1[i], I0[i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(O0 + O1 + I0 + I1, m, None, 0, 1)

# ---------------------------------------------------------------- lanternas da ordem (kit definitivo)
# OVERHAUL 01 (2026-09-29, "zero tolerancia"): o "cubo amarelo" saiu. A lanterna da ordem e UM asset desenhado:
#   - HEXAGONAL (6 lados, uma face de frente para 'yaw'), escala 0,72 da antiga (2,3 s de altura, 1,2 s no beiral);
#   - base em prato moldurado (torno), vidro quente RECUADO atras de 6 montantes em losango (a aresta viva do montante
#     fica para fora: le chanfrado), travessa DOURADA a 2/3 dividindo cada face em 2 vidros;
#   - tampa com BEIRAL curvo (torno concavo que sai alem da base) e remate dourado (colar + pinha + ponta);
#   - estrutura em ferro (Metal_SG_Iron, um valor acima do ferro negro), ouro so em acento (travessa e remate):
#     a luz quente (Lantern_Glow) fica SO dentro da moldura.
# Posicionamento IGUAL ao antigo: c = ponto de referencia, a BASE fica em c.z - 1,14 s (assenta onde o chamador ja
# punha). O centro do vidro agora fica em c.z - 0,29 s (as luzes reais existentes continuam dentro do corpo).
# Poste: soco de obsidiana + UM perfil de torno (sino moldurado com plinto, toro e escocia -> fuste sextavado afinando
# com anel a 1/3 -> colar) + capitel em prato sustentado por 4 consoles em S. Pedestal: dado moldurado baixo (plinto,
# dado, capitel em 2 degraus), altura total <= 3,44 s.
GOLD = "Metal_Gold"
# overhaul 14.04: debrum dos estandartes em BRONZE envelhecido (o ouro saturado lia brinquedo no jogo)
BRONZE = "Metal_SG_Bronze"
L_IRON = "Metal_SG_Iron"
L_GLOW = "Lantern_Glow"
L_WAX = "Plaster_SG"         # vela creme (paleta base: nao e material novo)
L_GLASS = "Glass_SG_LampAmber"   # vidro ambar (Glass 0,3 no Roblox pela regra Glass_SG do sg_lib), NAO emissivo
L_CORE = "SG_LampCore_Glow"   # nucleo quente ESCURO (Neon ambar fechado; sg_lib.SMATS) atras da chama
LH_BASE = 1.14               # fundo da lanterna abaixo do ponto de referencia (API antiga)
LH_GLASS = 0.85              # centro do vidro acima do fundo


def _lathe(mb, c, prof, m, n=6, rot=0.0, closed=False, caps=(True, True)):
    """solido de revolucao vertical em c = (x, y, z): prof = [(raio, altura)] de baixo para cima, raio 0 = polo.
    closed=True: perfil fechado (anel/moldura), sem tampas."""
    bm = mb.bm
    x, y, z = c
    rows = []
    for r, h in prof:
        if r < 1e-5:
            rows.append([bm.verts.new((x, y, z + h))])
        else:
            rows.append([bm.verts.new((x + r * math.cos(rot + 2 * math.pi * i / n),
                                       y + r * math.sin(rot + 2 * math.pi * i / n), z + h)) for i in range(n)])
    pairs = list(zip(rows, rows[1:]))
    if closed:
        pairs.append((rows[-1], rows[0]))
    faces = []
    for A, B in pairs:
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new((A[0], B[i], B[j])))
            elif len(B) == 1:
                faces.append(bm.faces.new((A[i], A[j], B[0])))
            else:
                faces.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    if not closed:
        if caps[0] and len(rows[0]) > 1:
            faces.append(bm.faces.new(list(reversed(rows[0]))))
        if caps[1] and len(rows[-1]) > 1:
            faces.append(bm.faces.new(rows[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for r in rows for v in r], m, None, 0, 1)


def lantern_head(mb_metal, mb_glow, c, yaw=0.0, s=1.0):
    """lanterna da ordem (hexagonal). c = ponto de referencia da API antiga: o FUNDO da base fica em c.z - 1,14 s.
    Devolve o centro do vidro.
    OVERHAUL 12 (12.01, o que faltava do setor 01): o vidro deixa de ser Neon - e VIDRO ambar claro (L_GLASS, Glass
    0,3 no Roblox) e dentro fica uma VELA com a CHAMA em gota de Lantern_Glow (~0,48, no centro do vidro) na frente de
    um NUCLEO quente fosco (SG_LampCore_Glow, Neon ambar escuro). No jogo: gaiola + vidro + nucleo + chama. Montantes de secao
    trapezoidal (0,12 na frente, chanfros para os lados) no lugar do triangulo."""
    x, y, z = c
    b = z - LH_BASE * s
    rot = yaw + math.pi / 6.0              # vertices em yaw +- 30: uma FACE olha para 'yaw'

    def P(pr):
        return [(r * s, h * s) for r, h in pr]
    # base: prato moldurado (pe, bojo, aba) - ferro (sem tampa de baixo: assenta sempre em alguma coisa)
    _lathe(mb_metal, (x, y, b), P([(0.30, 0.0), (0.55, 0.13), (0.47, 0.25)]), L_IRON, 6, rot, caps=(False, True))
    # rodada 4: NUCLEO quente fosco (SG_LampCore_Glow, Neon ambar ESCURO: nao estoura) - cilindro sextavado de ~60 %
    # do raio e ~70 % da altura do vidro, recuado para o fundo (face de tras 0,03 antes do vidro); a vela e a chama
    # clara ficam NA FRENTE dele (deslocadas 0,12 para 'yaw'). Leitura: ferro > vidro ambar > nucleo quente > chama.
    fx_, fy_ = math.cos(yaw), math.sin(yaw)
    _lathe(mb_glow, (x - fx_ * 0.15 * s, y - fy_ * 0.15 * s, b), P([(0.21, 0.26), (0.21, 1.11)]), L_CORE, 6, rot,
           caps=(False, True))
    # vela creme de pe no prato da base (torno quadrado) e chama em gota, na frente do nucleo
    vx_, vy_ = x + fx_ * 0.12 * s, y + fy_ * 0.12 * s
    _lathe(mb_metal, (vx_, vy_, b + 0.24 * s), P([(0.08, 0.0), (0.08, 0.40), (0.0, 0.42)]), L_WAX, 4, rot,
           caps=(False, False))
    _lathe(mb_glow, (vx_, vy_, b + 0.63 * s), P([(0.0, 0.0), (0.12, 0.15), (0.065, 0.31), (0.0, 0.48)]), L_GLOW, 5,
           rot)
    # vidro ambar recuado (hexagono de 0,40 no vertice, atras dos montantes); tampas escondidas na base/tampa
    _lathe(mb_metal, (x, y, b), P([(0.40, 0.24), (0.40, 1.46)]), L_GLASS, 6, rot, caps=(False, False))
    # 6 montantes de secao trapezoidal nos vertices (frente de 0,07 de meia-largura, chanfros para os lados)
    bm = mb_metal.bm
    for k in range(6):
        a = rot + k * math.pi / 3.0
        ca, sa = math.cos(a), math.sin(a)
        sec = [(0.37, -0.06), (0.48, -0.035), (0.48, 0.035), (0.37, 0.06)]      # (raio, deslocamento tangencial)
        vs = []
        for zz in (0.22, 1.48):
            vs.append([bm.verts.new((x + (r * ca - t * sa) * s, y + (r * sa + t * ca) * s, b + zz * s))
                       for r, t in sec])
        fs = [bm.faces.new((vs[0][i], vs[0][(i + 1) % 4], vs[1][(i + 1) % 4], vs[1][i])) for i in range(4)]
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        mb_metal._post(vs[0] + vs[1], L_IRON, None, 0, 1)
    # travessa dourada a ~3/4 (divide cada face em 2 vidros), acima da chama (a chama fica no centro do vidro)
    _lathe(mb_metal, (x, y, b), P([(0.46, 1.14), (0.46, 1.21)]), GOLD, 6, rot, caps=(False, False))   # cinta
    # tampa: cinta, BEIRAL que sai alem da base, telhado concavo ate o colar do remate
    _lathe(mb_metal, (x, y, b), P([(0.36, 1.44), (0.50, 1.47), (0.62, 1.58), (0.32, 1.80), (0.15, 1.96)]), L_IRON,
           6, rot, caps=(True, False))                                           # (o topo fica dentro do remate)
    # remate dourado: colar e ponta
    _lathe(mb_metal, (x, y, b), P([(0.12, 1.94), (0.16, 2.03), (0.0, 2.30)]), GOLD, 6, rot, caps=(False, True))
    return (x, y, b + LH_GLASS * s)


def lantern_pedestal(mb_stone, mb_metal, mb_glow, base, yaw=0.0, s=1.0):
    """lanterna sobre DADO MOLDURADO baixo de obsidiana (parapeitos, eixo). base = (x, y, z do apoio).
    Pedestal 1,12 s + lanterna 2,3 s = 3,42 s. Devolve o centro do vidro."""
    x, y, z = base
    # OVERHAUL 12 (16.03): as 4 caixas empilhadas viram UM perfil de torno de secao quadrada (n=4, quinas a 45 graus
    # do yaw): plinto chanfrado, toro, dado, colarinho, capitel em 2 degraus com cimalha - mesmas cotas de antes
    prof = [(0.62, 0.0), (0.62, 0.12), (0.54, 0.18), (0.47, 0.25), (0.46, 0.86), (0.49, 0.90), (0.55, 0.96),
            (0.55, 1.03), (0.50, 1.06), (0.50, 1.12)]
    _lathe(mb_stone, (x, y, z), [(r * s * math.sqrt(2.0), hh * s) for r, hh in prof], SHADOW, 4, yaw + math.pi / 4,
           caps=(False, True))
    return lantern_head(mb_metal, mb_glow, (x, y, z + (1.12 + LH_BASE) * s), yaw, s)


def lantern_post(mb_metal, mb_glow, base, yaw=0.0, h=7.0, s=1.0):
    """poste da ordem: soco de obsidiana, fuste de ferro torneado e lanterna no alto. O fundo da lanterna fica na
    MESMA cota de antes (z + h - 0,24 s): as luzes reais do sg_lights continuam dentro dela. Devolve o centro do vidro."""
    x, y, z = base
    zb = z + h - 0.24 * s                          # fundo da lanterna (API antiga)
    mb_metal.box((1.2 * s, 1.2 * s, 0.3 * s), (x, y, z + 0.15 * s), (0, 0, yaw), SHADOW, 0.05 * s)       # soco
    z0 = z + 0.3 * s
    zc = zb - 0.40 * s                             # topo do colar (onde nasce o capitel)
    L = zc - z0
    h1 = 0.95 * s + (L - 0.95 * s) * 0.34          # anel a 1/3 do fuste
    rot = yaw + math.pi / 6.0
    prof = [(0.48, 0.0), (0.48, 0.10), (0.40, 0.15), (0.43, 0.24), (0.28, 0.36), (0.18, 0.95)]
    prof = [(r * s, hh * s) for r, hh in prof]
    prof += [(0.165 * s, h1 - 0.10 * s), (0.22 * s, h1 - 0.05 * s), (0.22 * s, h1 + 0.05 * s),
             (0.155 * s, h1 + 0.10 * s), (0.13 * s, L - 0.18 * s), (0.19 * s, L - 0.12 * s), (0.13 * s, L)]
    _lathe(mb_metal, (x, y, z0), prof, L_IRON, 6, rot, caps=(False, True))
    # capitel: prato que recebe a lanterna (sai do colar e abre ate a base dela)
    _lathe(mb_metal, (x, y, zc), [(0.13 * s, 0.0), (0.20 * s, 0.12 * s), (0.30 * s, 0.26 * s), (0.52 * s, 0.33 * s),
                                  (0.56 * s, 0.38 * s), (0.48 * s, 0.40 * s)], L_IRON, 6, rot, caps=(False, True))
    # 4 consoles em S (do fuste ate a aba do prato): nas faces do fuste sextavado
    prof_c = [(-0.035 * s, -0.05 * s), (0.035 * s, -0.05 * s), (0.035 * s, 0.05 * s), (-0.035 * s, 0.05 * s)]
    for k in range(4):
        a = yaw + math.pi / 4.0 + k * math.pi / 2.0
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        p0, p1, p2, p3 = (0.14, -0.62), (0.16, -0.18), (0.50, -0.30), (0.50, 0.30)
        for i in range(4):
            t = i / 3.0
            u = 1 - t
            r = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
            hh = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
            pts.append((x + ca * r * s, y + sa * r * s, zc + hh * s))
        mb_metal.sweep(pts, prof_c, L_IRON, True, None, up=(-sa, ca, 0.0))
    return lantern_head(mb_metal, mb_glow, (x, y, zb + LH_BASE * s), yaw, s)
