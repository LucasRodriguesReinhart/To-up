# sg_emblem - SISTEMA DE IDENTIDADE da Ilha 3 (Shadow Garden). COMPARTILHADO E CONGELADO (dono: integracao).
# Um UNICO simbolo da ordem, original (nao e logo de obra nenhuma): a LUA EM ECLIPSE atravessada por uma LAMINA.
#   - anel externo de prata (a moldura nobre)
#   - campo negro (a lua apagada) e o CRESCENTE violeta luminoso (a parte que a sombra ainda nao comeu: "a eminencia
#     nas sombras")
#   - espada vertical de prata atravessando o simbolo (a espada de Shadow): ponta, lamina, guarda, cabo e pomo
#   - 8 raios curtos de prata fora do anel (so na versao 'monumental')
# Todo lugar que fala pela ordem usa ESTE simbolo: fachada do castelo, estandartes, portoes, piso do salao, dungeon,
# porticos da entrada. Nada de tridente/estrela/lua soltos (ornamento sem sistema = cara de IA).
#
# ACABAMENTO 2026-09-29: o simbolo virou ASSET PROPRIO de malha limpa (nada de caixas empilhadas):
#   - cada peca e um perfil 2D desenhado no plano do emblema e extrudado com chanfro (casca fechada, normais por peca);
#   - anel = coroa circular continua de 32 segmentos (40 nos grandes; vertices nos eixos = simetrica) com chanfro de
#     45 graus nas duas arestas;
#   - crescente = UM poligono (diferenca de dois circulos calculada), extrudado e chanfrado; o campo negro fica ATRAS
#     (nao ha mais disco claro com disco escuro por cima);
#   - espada simetrica no eixo, secao em losango (aresta central) com a MESMA inclinacao de faceta em todas as pecas:
#     a lamina nasce de dentro da guarda, o cabo sai da guarda e entra no pomo sextavado (dentro da faixa do crescente);
#   - camadas em profundidade sem nada coplanar (fracoes de 'depth'): campo -0,04..0,12 | crescente 0,04..0,30 |
#     anel -0,05..0,50 | raios ate ~0,32 | cabo ~0,60 | lamina 0,55..~0,67 | pomo ~0,70 | guarda ~0,78;
#   - larguras de traco coerentes (anel ~ lamina) e engrossadas de leve nos emblemas pequenos (legivel de longe).
#   Estandarte: verga redonda com luva de tecido e remates de prata; pano pentagonal com espessura (ponta em V na mesma
#   peca); debrum continuo com espessura contornando laterais e V com esquadria limpa. Placa: disco de obsidiana
#   chanfrado. Lanternas: travessa superior que assenta a tampa, beiral, remate; capitel do poste encosta na base.
#
# API (todas desenham em MBs que o modulo chamador ja criou; nada de colisao aqui):
#   emblem(mb_metal, mb_glow, mb_dark, c, yaw, r, depth=0.6, monumental=False)
#       c = (x, y, z) centro; yaw = rumo (rad) para onde o simbolo OLHA; r = raio do anel externo
#   banner(mb_cloth, mb_metal, mb_glow, mb_dark, top, yaw, w, h, tails=True, trim=None)
#       estandarte da ordem: tecido roxo profundo com barra negra e borda de prata, emblema em cima, ponta em V
#   plaque(mb_stone, mb_metal, mb_glow, mb_dark, c, yaw, r)
#       medalhao de pedra obsidiana com o emblema (portais, pedestais, fontes)
#   emblem_flat(mb_metal, mb_glow, mb_dark, c, yaw, r, monumental=False, up=1, glow=MOON, field=True, seg=None)
#       o mesmo simbolo DEITADO e rente (incrustacao de piso / chave de teto); yaw = rumo da ponta da lamina
#   lantern_head / lantern_pedestal / lantern_post (abaixo)
# Materiais: Metal_SG_Silver (prata), SG_Rune_Glow (lua), Stone_SG_Obsidian (sombra/campo), Cloth_SG_Purple (tecido).
import math
import bmesh

SILVER, MOON, SHADOW, CLOTH, TRIM = "Metal_SG_Silver", "SG_Rune_Glow", "Stone_SG_Obsidian", "Cloth_SG_Purple", "Stone_SG_Obsidian"
IRON = "Metal_SG_BlackIron"

# ---------------------------------------------------------------- desenho do simbolo (unidades de r, a = lateral, b = cima)
RING_OUT = 0.97                  # borda externa do anel
RING_W = 0.14                    # largura do anel (traco principal)
MOON_R = 0.70                    # circulo da lua
SHADOW_C, SHADOW_R = (0.27, 0.05), 0.60      # circulo da sombra (deslocado para +u): pontas longe da lamina
BLADE_B0, BLADE_SH, BLADE_TIP = -0.07, 0.90, 1.16    # base (dentro da guarda), ombro da ponta, ponta
BLADE_HW0, BLADE_HW1 = 0.068, 0.056                  # meia-largura da lamina na base e no ombro (afina de leve)
GUARD_B = -0.05
GUARD = ((0.26, 0.0), (0.215, 0.050), (0.10, 0.034), (0.045, 0.058))   # (|a|, meia-altura) do extremo ao miolo
GRIP = ((-0.02, 0.034), (-0.30, 0.029), (-0.58, 0.034))   # de dentro da guarda a dentro do pomo
POMMEL = ((-0.545, 0.0), (-0.572, 0.062), (-0.625, 0.062), (-0.652, 0.0))   # sextavado, DENTRO da faixa do crescente
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
    # 2) crescente violeta: um poligono so, chanfrado
    c2 = (SHADOW_C[0] * r, SHADOW_C[1] * r)
    R1, R2 = MOON_R * r, SHADOW_R * r
    m0, m1 = lay["moon"]
    loops = [_crescent_loop(P, R1, c2, R2, n_moon, m0), _crescent_loop(P, R1, c2, R2, n_moon, m1 - chc),
             _crescent_loop(P, R1 - chc, c2, R2 + chc, n_moon, m1)]
    _shell(mb_glow, loops, glow, "strip", "strip", strip_n=n_moon)
    # 3) anel de prata continuo
    _annulus(mb_metal, P, ri, ro, lay["ring"][0], lay["ring"][1], ch, SILVER, n=n_ring)
    # 4) espada (prata), secao em losango com a mesma inclinacao de faceta em todas as pecas
    hw0, hw1 = BLADE_HW0 * r * kb, BLADE_HW1 * r * kb
    if monumental:
        # raios de prata saindo de baixo do anel: longos perto da horizontal, curtos ladeando a ponta e o pomo
        # (simetrico nos dois eixos; a lamina e o raio do alto)
        for q in range(8):
            t = math.pi / 8 + q * math.pi / 4
            longo = abs(math.cos(t)) > 0.7
            L = r * (0.34 if longo else 0.22)
            hwr = r * (0.050 if longo else 0.040) * kb
            _bar(mb_metal, P, SILVER, (0.0, 0.0), (math.cos(t), math.sin(t)),
                 ((ro - 0.6 * w, hwr), (ro + 0.02 * r, hwr * 0.92), (0.98 * r + L, 0.0)),
                 lay["rays"][0], lay["rays"][1], k)
    _bar(mb_metal, P, SILVER, (0.0, 0.0), (0.0, 1.0),
         ((BLADE_B0 * r, hw0), (BLADE_SH * r, hw1), (BLADE_TIP * r, 0.0)), lay["blade"][0], lay["blade"][1], k)
    _bar(mb_metal, P, SILVER, (0.0, 0.0), (0.0, 1.0),
         tuple((b * r, hw * r * kb) for b, hw in GRIP), lay["grip"][0], lay["grip"][1], k)
    _bar(mb_metal, P, SILVER, (0.0, 0.0), (0.0, 1.0),
         tuple((b * r, hw * r * kb) for b, hw in POMMEL), lay["pommel"][0], lay["pommel"][1], k)
    gst = [(-a * r, hw * r * kb) for a, hw in GUARD] + [(a * r, hw * r * kb) for a, hw in reversed(GUARD)]
    _bar(mb_metal, P, SILVER, (0.0, GUARD_B * r), (1.0, 0.0), gst, lay["guard"][0], lay["guard"][1], k)


def emblem(mb_metal, mb_glow, mb_dark, c, yaw, r, depth=0.6, monumental=False):
    f, u = _frame(c, yaw)
    P = _W(c, f, u)
    D = depth
    kb = min(1.4, max(1.0, 0.8 / r))
    w = RING_W * r * kb
    ch = min(0.032 * r, 0.12 * D, 0.22 * w)       # o MESMO chanfro no anel e no crescente
    lay = {"ch": ch, "chc": min(ch, 0.06 * D), "k": min(1.0, max(0.3, 0.12 * D / (BLADE_HW0 * r * kb))),
           "field": (-0.04 * D, 0.12 * D), "moon": (0.04 * D, 0.30 * D), "ring": (-0.05 * D, 0.50 * D),
           "rays": (-0.045 * D, 0.22 * D), "blade": (-0.03 * D, 0.55 * D), "grip": (-0.025 * D, 0.54 * D),
           "pommel": (-0.02 * D, 0.58 * D), "guard": (-0.02 * D, 0.67 * D)}
    _emblem_geo(mb_metal, mb_glow, mb_dark, P, r, lay, monumental)


def emblem_flat(mb_metal, mb_glow, mb_dark, c, yaw, r, monumental=False, up=1, glow=MOON, field=True, seg=None):
    """o MESMO simbolo DEITADO, como incrustacao RENTE (piso ou chave de teto): c = (x, y, z da superficie), yaw = rumo
    (rad) para onde a PONTA da lamina aponta na planta, r = raio do anel externo. up=+1: face para cima (piso);
    up=-1: face para baixo (chave/teto). Mesma logica de camadas, mas em alturas ABSOLUTAS: tudo sobe no maximo ~0,056
    acima da superficie (nada em que tropecar) e os fundos ficam embutidos nela. Visto de cima com a ponta para
    a frente, o crescente fica a direita (igual ao emblema de pe). glow = material do crescente (ex. um Neon mais fraco
    no piso); field=False dispensa o campo negro quando a superficie ja e de obsidiana; seg = segmentos do anel
    (multiplo de 4) para chaves pequenas."""
    vx, vy = math.cos(yaw), math.sin(yaw)
    ux, uy = -vy * up, vx * up
    cx, cy, cz = c

    def P(a, b, d):
        return (cx + ux * a + vx * b, cy + uy * a + vy * b, cz + up * d)
    kb = min(1.4, max(1.0, 0.8 / r))
    ch = min(0.032 * r, 0.008)
    lay = {"ch": ch, "chc": min(ch, 0.006), "k": 0.012 / (BLADE_HW0 * r * kb),
           "field": (-0.10, 0.010), "moon": (-0.06, 0.020), "ring": (-0.12, 0.030), "rays": (-0.11, 0.024),
           "blade": (-0.09, 0.038), "grip": (-0.085, 0.036), "pommel": (-0.08, 0.040), "guard": (-0.08, 0.046)}
    _emblem_geo(mb_metal, mb_glow, mb_dark, P, r, lay, monumental, glow, field, seg)


def plaque(mb_stone, mb_metal, mb_glow, mb_dark, c, yaw, r):
    """medalhao: disco de obsidiana chanfrado (fundo em -0,5, frente em 0) com o emblema assentado (fundo embutido)"""
    f, u = _frame(c, yaw)
    P = _W(c, f, u)
    R = r * 1.12
    _disc(mb_stone, P, R, -0.5, 0.0, TRIM, n=32, ch=min(0.14, max(0.04, 0.06 * R)))
    emblem(mb_metal, mb_glow, mb_dark, _p(c, f, u, 0, 0, 0.0), yaw, r * 0.92, depth=0.45)


def banner(mb_cloth, mb_metal, mb_glow, mb_dark, top, yaw, w, h, tails=True, trim=None):
    """estandarte pendurado por uma verga de ferro/prata em 'top' (centro da verga), olhando para yaw"""
    f, u = _frame(top, yaw)
    P = _W(top, f, u)
    th = 0.22                     # espessura do pano
    dc = 0.03                     # plano medio do pano (a verga fica em d = 0)
    yu = math.atan2(u[1], u[0])
    # verga redonda de ferro negro (mesmo comprimento/altura de antes: os bracos dos modulos continuam encostando)
    half = w / 2 + 0.35
    mb_metal.cyl(0.14, 2 * half, P(0, 0, 0), (0, math.pi / 2, yu), m=IRON, n=8, bevel=0.0)
    for s in (-1, 1):
        ys = math.atan2(s * u[1], s * u[0])
        mb_metal.cyl(0.2, 0.14, P(s * half, 0, 0), (0, math.pi / 2, ys), m=SILVER, n=8, bevel=0.0)        # colar
        mb_metal.cyl(0.17, 0.34, P(s * (half + 0.24), 0, 0), (0, math.pi / 2, ys), m=SILVER, n=8, r2=0.0,
                     bevel=0.0)                                                                             # remate
    # luva de tecido abracando a verga (o pano pende DELA, nao flutua embaixo)
    mb_cloth.cyl(0.22, w, P(0, 0, dc * 0.5), (0, math.pi / 2, yu), m=CLOTH, n=8, bevel=0.0)
    body_h = h * (0.84 if tails else 1.0)
    bt = -0.05                    # topo do pano (dentro da luva)
    zb = -body_h - 0.15
    zt = zb - h * 0.16
    if tails:
        pts = [(-w / 2, bt), (-w / 2, zb), (0.0, zt), (w / 2, zb), (w / 2, bt)]
    else:
        pts = [(-w / 2, bt), (-w / 2, zb), (w / 2, zb), (w / 2, bt)]
    _prism(mb_cloth, P, pts, dc - th / 2, dc + th / 2, CLOTH)
    # barra negra no alto (abraca o pano) e debrum continuo (laterais + V) com espessura
    _prism(mb_dark, P, [(-w / 2 - 0.01, -h * 0.13), (w / 2 + 0.01, -h * 0.13), (w / 2 + 0.01, -h * 0.05),
                        (-w / 2 - 0.01, -h * 0.05)], dc - th / 2 - 0.02, dc + th / 2 + 0.02, SHADOW)
    tm = trim or SILVER
    tw = min(0.2, max(0.12, 0.05 * w))
    _band(mb_metal, P, pts, tw, dc - th / 2 - 0.035, dc + th / 2 + 0.035, tm)
    er = min(w * 0.36, h * 0.16)
    D = 0.28
    emblem(mb_metal, mb_glow, mb_dark, P(0, -h * 0.36, dc + th / 2), yaw, er, depth=D)   # fundos embutidos no pano


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
L_IRON = "Metal_SG_Iron"
L_GLOW = "Lantern_Glow"
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
    Devolve o centro do vidro."""
    x, y, z = c
    b = z - LH_BASE * s
    rot = yaw + math.pi / 6.0              # vertices em yaw +- 30: uma FACE olha para 'yaw'

    def P(pr):
        return [(r * s, h * s) for r, h in pr]
    # base: prato moldurado (pe, bojo, aba) - ferro (sem tampa de baixo: assenta sempre em alguma coisa)
    _lathe(mb_metal, (x, y, b), P([(0.30, 0.0), (0.55, 0.11), (0.55, 0.20), (0.47, 0.25)]), L_IRON, 6, rot,
           caps=(False, True))
    # vidro quente recuado (hexagono de 0,40 no vertice: a face fica 0,05 atras da face dos montantes/travessas); as
    # tampas ficariam escondidas dentro da base e da tampa
    _lathe(mb_glow, (x, y, b), P([(0.40, 0.24), (0.40, 1.46)]), L_GLOW, 6, rot, caps=(False, False))
    # 6 montantes de secao triangular nos vertices (a aresta viva aponta para fora: le como montante chanfrado)
    bm = mb_metal.bm
    for k in range(6):
        a = rot + k * math.pi / 3.0
        ca, sa = math.cos(a), math.sin(a)
        tri = [(0.37, -0.055), (0.49, 0.0), (0.37, 0.055)]            # (raio, deslocamento tangencial)
        vs = []
        for zz in (0.22, 1.48):
            vs.append([bm.verts.new((x + (r * ca - t * sa) * s, y + (r * sa + t * ca) * s, b + zz * s))
                       for r, t in tri])
        fs = [bm.faces.new((vs[0][i], vs[0][(i + 1) % 3], vs[1][(i + 1) % 3], vs[1][i])) for i in range(3)]
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        mb_metal._post(vs[0] + vs[1], L_IRON, None, 0, 1)
    # travessa dourada a 2/3 (divide cada face em 2 vidros)
    _lathe(mb_metal, (x, y, b), P([(0.46, 0.99), (0.46, 1.07)]), GOLD, 6, rot)      # (o miolo fica dentro do vidro)
    # tampa: cinta, BEIRAL que sai alem da base, telhado concavo ate o colar do remate
    _lathe(mb_metal, (x, y, b), P([(0.36, 1.44), (0.50, 1.47), (0.62, 1.58), (0.59, 1.65), (0.32, 1.80),
                                   (0.15, 1.96)]), L_IRON, 6, rot)
    # remate dourado: colar, pinha, ponta
    _lathe(mb_metal, (x, y, b), P([(0.12, 1.94), (0.16, 2.03), (0.09, 2.12), (0.0, 2.30)]), GOLD, 6, rot,
           caps=(False, True))
    return (x, y, b + LH_GLASS * s)


def lantern_pedestal(mb_stone, mb_metal, mb_glow, base, yaw=0.0, s=1.0):
    """lanterna sobre DADO MOLDURADO baixo de obsidiana (parapeitos, eixo). base = (x, y, z do apoio).
    Pedestal 1,12 s + lanterna 2,3 s = 3,42 s. Devolve o centro do vidro."""
    x, y, z = base
    mb_stone.box((1.24 * s, 1.24 * s, 0.16 * s), (x, y, z + 0.08 * s), (0, 0, yaw), SHADOW, 0.04 * s)      # plinto
    mb_stone.box((0.92 * s, 0.92 * s, 0.80 * s), (x, y, z + 0.56 * s), (0, 0, yaw), SHADOW, 0.05 * s)      # dado
    mb_stone.box((1.10 * s, 1.10 * s, 0.10 * s), (x, y, z + 1.01 * s), (0, 0, yaw), SHADOW, 0.0)          # capitel
    mb_stone.box((1.00 * s, 1.00 * s, 0.07 * s), (x, y, z + 1.09 * s), (0, 0, yaw), SHADOW, 0.02 * s)
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
