# op_col - COMPARTILHADO (dono: integracao). Colisao de TUDO que e andavel na Ilha 5, independente do visual: piso de
# cada patamar (poligonos da planta, caixas MACICAS ate FLOOR_BOT), escadas (col_ramp + guardas), pontes (chegada
# 80,2 -> 84,2; ponte vermelha de saida; 2 pontes do canal EM ARCO; prancha do navio), guarda PROVISORIA da ancora One
# Punch Man e as guardas invisiveis.
# A PRACA tem piso PLANO a 92,2 (o raycast do SpawnMinerio exige |piso - 92,2| < 0,5 e normal > 0,85).
#
# V2-0 (PLANO_V2 secao 9, U5/U8 - a auditoria mediu 11.671 studs2 de chao aparente sem colisao):
#   1. a colisao nasce do VISUAL alcancavel: alem dos pisos, colidem as ROCHAS (macicas ate o topo: rock_cols), o leito
#      dos canais/bacia/lago (water_beds), a capa dos canais (copings) e os telhados alcancaveis (lot_cols/roof_col);
#   2. faixas SEM extrapolar o poligono (poly_cover: modo 'inter' quebrado nos vertices + caixas de aresta nas arestas
#      diagonais) - acabou o piso 92,2 dentro da rocha NE (R4) e sob as muralhas do cais;
#   3. rocha fechada: cada massa de L.ROCKS colide ate o topo visual (flag L.ROCK_COL: 'walk' = topo alcancavel, vira
#      piso nas guardas; 'tall' = >= 8,5 acima do alcancavel);
#   4. guarda de 8,5 (pulo 7,2 + 1,3) no LABIO, so onde a queda leva ao vazio/mar ou e maior que o pulo (nao se volta);
#      quedas internas <= 7,2 sobre chao com colisao (praca -> rua, margem -> leito do canal) ficam abertas;
#   5. canais e bacia com leito colidivel 1,0 abaixo da agua (sem buraco ate o vazio; guarda so na boca das quedas);
#   6. telhados: cada agua de telhado alcancavel (<= 7,2 de algo alcancavel) ganha 1 rampa; corpo do lote ate o beiral;
#   7. pe afundando <= 0,3: tabuleiro das pontes em arco, capa e leitos na cota do visual.
import math
from mathutils import Vector
import op_lib as DL
from op_lib import col_box, col_box2, col_ramp, ccw
import op_layout as L

A = "OP_Terrain"
GUARD_H = L.GUARD_V2   # guarda invisivel (acima do piso): pulo 7,2 + 1,3 (era 3,2 na V1: R2 da auditoria)
DROP = 2.3             # degrau maximo do andador (rotas)
JUMP = L.JUMP


def stair_col(area, base, ang, width, n, rise, tread, guards=True, guard_h=None):
    """a colisao de fm_parts.stairs (rampa pelo meio dos pisos + meia pisada final + banzos) sem a geometria.
    V2-0: banzo invisivel de 8,5 acima da linha da escada (com 4,0 o topo dele era alcancavel e servia de degrau para
    a guarda do patamar de cima e dali para telhados/rochas: cadeia medida pelo gate 'visual')"""
    guard_h = GUARD_H if guard_h is None else guard_h
    F = DL.Frame(base[0], base[1], base[2], ang)
    bot = F.p(-tread / 2, 0, 0)
    top = F.p(tread * n - tread / 2, 0, rise * n)
    col_ramp(area, bot, top, width)
    q = F.p(tread * n - tread / 4 + 0.15, 0, rise * n - 0.5)
    col_box(area, (tread / 2 + 0.3, width, 1.0), (q.x, q.y, q.z), F.r())
    if guards and guard_h >= GUARD_H - 1e-6:
        # V2-0: caixa VERTICAL com topo plano 8,5 acima do patamar de cima (a rampa de 4 tinha topo e testa inclinados
        # alcancaveis do patamar de cima: degrau para a guarda da borda e dali para telhados/rochas)
        x0, x1 = -tread / 2 - 0.3, tread * n - tread / 2 + 0.9
        h = rise * n + guard_h + 0.5
        for s in (-1, 1):
            c = F.p((x0 + x1) / 2, s * (width / 2 + 0.6), -0.5 + h / 2)
            col_box(area, (x1 - x0, 1.2, h), (c.x, c.y, c.z), F.r())
    elif guards:
        k = rise / tread
        H = guard_h
        T = H + 1.5
        off = k * (tread * k / 2 + H) / (1 + k * k)
        for s in (-1, 1):
            y = s * (width / 2 + 0.6)
            xa, xb = -off, tread * n - off
            a = F.p(xa, y, (xa + tread / 2) * k + H)
            b = F.p(xb, y, (xb + tread / 2) * k + H)
            col_ramp(area, a, b, 1.2, thick=T)
    return F.p(tread * n, 0, rise * n)


def stair_list():
    return [(nm, foot, math.radians(deg), w, n, L.stair_rise(nm), tread, g) for nm, foot, deg, w, n, tread, g in L.STAIRS]


def stair_footprint(nm, pad=0.0):
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    x0, y0 = foot[0] - ux * (tread / 2 + pad), foot[1] - uy * (tread / 2 + pad)
    x1, y1 = foot[0] + ux * (tread * n + pad), foot[1] + uy * (tread * n + pad)
    hw = w / 2
    return [(x0 + vx * hw, y0 + vy * hw), (x0 - vx * hw, y0 - vy * hw), (x1 - vx * hw, y1 - vy * hw),
            (x1 + vx * hw, y1 + vy * hw)]


def _in_rect_along(x, y, a, b, hw, pad=0.0):
    ux, uy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ux, uy) or 1.0
    ux, uy = ux / ln, uy / ln
    t = (x - a[0]) * ux + (y - a[1]) * uy
    d = abs(-(x - a[0]) * uy + (y - a[1]) * ux)
    return -pad <= t <= ln + pad and d <= hw


def anchor_gap(x, y):
    """vao da ancora One Punch Man (18) na borda de fora do promontorio: fica aberto (a guarda PROVISORIA fecha)"""
    ap = L.anchor_opm_pos()
    ux, uy = L.exit_dir()
    t = (x - ap[0]) * ux + (y - ap[1]) * uy
    v = -(x - ap[0]) * uy + (y - ap[1]) * ux
    return -3.0 <= t <= 4.0 and abs(v) <= L.EXIT_W / 2 + 0.3


def opening(x, y):
    """(x, y) cai numa escada, numa ponte ou no vao da ancora: a borda do piso ali fica aberta"""
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        if L.point_in_poly(x, y, stair_footprint(nm, pad=1.0)):
            return True
    for nm, a, b, w in L.bridge_list():
        if _in_rect_along(x, y, a, b, w / 2, pad=2.0):
            return True
    return anchor_gap(x, y)


# ------------------------------------------------------------------ pontes
def arch_bridge(nm, a, b, w, rise):
    """ponte EM ARCO do canal (V2-0, U6): degraus de BRIDGE_ARCH_STEP nas 2 pontas (colisao = rampa pelos bocéis), topo
    plano a z + rise sobre o vao e os encontros; guarda-corpo baixo (1,2) com colisao nos 2 lados (o visual do
    guarda-corpo e alcancavel: colide). A queda para o canal leva ao leito colidivel: sem guarda alta."""
    rs, tr = L.BRIDGE_ARCH_STEP
    nsteps = max(1, int(round(rise / rs)))
    run = nsteps * tr
    ux, uy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ux, uy)
    ux, uy = ux / ln, uy / ln
    vx, vy = -uy, ux
    z0 = a[2]
    area = "OP_" + nm
    for s, p in ((1, a), (-1, b)):                     # rampa de cada ponta (pe -> topo), passando pelos bocéis
        d = (ux * s, uy * s)
        p0 = (p[0] - d[0] * 0.6, p[1] - d[1] * 0.6, z0 - 0.6 * rise / run)
        p1 = (p[0] + d[0] * run, p[1] + d[1] * run, z0 + rise)
        col_ramp(area, p0, p1, w, thick=1.6)
    c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    top_len = ln - 2 * run + 0.4
    col_box(area, (top_len, w, 1.6), (c[0], c[1], z0 + rise - 0.8), (0, 0, math.atan2(uy, ux)))
    for s in (-1, 1):                                  # guarda-corpo (visual 1,0 + corrimao): colisao de 1,2
        o = s * (w / 2 + 0.3)
        col_box(area + "Rail", (top_len, 0.6, 1.2), (c[0] + vx * o, c[1] + vy * o, z0 + rise + 0.6),
                (0, 0, math.atan2(uy, ux)))


def bridges():
    for nm, a, b, w in L.bridge_list():
        if nm in L.BRIDGE_ARCH:
            arch_bridge(nm, a, b, w, L.BRIDGE_ARCH[nm])
            continue
        ux, uy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        vx, vy = -uy, ux
        dz = (b[2] - a[2]) / ln
        eb = 0.4 if nm == "Gangway" else 2.0          # a prancha termina RENTE ao convés (sem degrau de ponta)
        a2 = (a[0] - ux * 2.0, a[1] - uy * 2.0, a[2] - dz * 2.0)
        b2 = (b[0] + ux * eb, b[1] + uy * eb, b[2] + dz * eb)
        col_ramp("OP_" + nm, a2, b2, w, thick=2.0)
        gh = GUARD_H + (2.0 if nm == "Gangway" else 0.0)   # sobre o vazio/mar: 8,5 (+2 na prancha: cabecos do cais)
        zt = max(a[2], b[2]) + gh + 0.8                    # V2-0: caixa VERTICAL (topo plano; a rampa de testa
        zb = min(a[2], b[2]) - 0.5                         # inclinada tinha pontos alcancaveis nas cabeceiras)
        for s in (-1, 1):
            o = s * (w / 2 + 0.6)
            c = ((a[0] + b[0]) / 2 + vx * o, (a[1] + b[1]) / 2 + vy * o, (zt + zb) / 2)
            col_box("OP_" + nm + "Guard", (ln + 2.0, 1.2, zt - zb), c, (0, 0, math.atan2(uy, ux)))
    anchor_guard()


def anchor_guard():
    """guarda PROVISORIA da ancora One Punch Man (a integracao da area 6 remove: next_island_guard)"""
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    ap = L.anchor_opm_pos()
    g = col_box("OPAnchorGuard", (1.2, L.EXIT_W + 2.0, 9.0), (ap[0] + ux * 0.6, ap[1] + uy * 0.6, L.T1 + 4.0), (0, 0, a))
    g["next_island_guard"] = True


# ------------------------------------------------------------------ cobertura de poligono SEM extrapolar (item 2)
def _sub_iv(ivs, holes, ya, yb):
    """tira dos intervalos [a, b] da faixa [ya, yb] os buracos retangulares que cobrem a faixa"""
    out = list(ivs)
    for hx0, hy0, hx1, hy1 in holes:
        if hy0 <= ya + 1e-6 and hy1 >= yb - 1e-6:
            nxt = []
            for a, b in out:
                if b <= hx0 or a >= hx1:
                    nxt.append((a, b))
                else:
                    if a < hx0:
                        nxt.append((a, hx0))
                    if b > hx1:
                        nxt.append((hx1, b))
            out = nxt
    return out


def strips(area, poly, z0, z1, step, mode="inter", breaks=(), holes=()):
    """faixas horizontais (eixo X) de altura <= step; 'inter' = so o que esta dentro nas 3 amostras da faixa (nao
    extrapola); 'union' = o que esta dentro em qualquer amostra (extrapola nas arestas diagonais: so legado)"""
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        yb = min([y + step, max(ys)] + [b for b in breaks if b > y + 1e-6])
        ya = y
        ivs = None
        for sm in (ya + 0.02, (ya + yb) / 2, yb - 0.02):
            iv = DL.x_intervals(poly, sm)
            ivs = iv if ivs is None else (DL.IL._union(ivs, iv) if mode == "union" else DL.IL._inter(ivs, iv))
        for a, b in _sub_iv(ivs or [], holes, ya, yb):
            if b - a > 0.3:
                col_box2(area, (a, ya, z0), (b, yb, z1))
                n += 1
        y = yb
    return n


def _interior_angle(prev, p, nxt):
    """angulo interno (graus) no vertice p de um poligono anti-horario"""
    a1 = math.atan2(prev[1] - p[1], prev[0] - p[0])
    a2 = math.atan2(nxt[1] - p[1], nxt[0] - p[0])
    d = math.degrees(a1 - a2) % 360.0
    return d


def _hits_holes(px, py, qx, qy, holes, pad=0.05):
    for k in range(7):
        t = k / 6.0
        x, y = px + (qx - px) * t, py + (qy - py) * t
        for hx0, hy0, hx1, hy1 in holes:
            if hx0 - pad <= x <= hx1 + pad and hy0 - pad <= y <= hy1 + pad:
                return True
    return False


def poly_cover(area, poly, z0, z1, step=8.0, min_edge=1.5, holes=()):
    """cobre o poligono com caixas SEM passar da borda: faixas 'inter' quebradas em todos os vertices + 1 caixa ao
    longo de cada aresta diagonal (dentro do poligono, largura = a lasca que a faixa deixa), encurtada nos vertices
    agudos, + escada de 2 caixas nos cantos agudos. 'holes' = retangulos (x0, y0, x1, y1) que ficam VAZIOS (entalhe
    de escada, lago): o poligono nao e picado (picar criava cantos agudos artificiais com frestas). Devolve o numero
    de caixas."""
    P_ = ccw(poly)
    ybreaks = sorted({p[1] for p in P_} | {h[1] for h in holes} | {h[3] for h in holes})
    n = strips(area, P_, z0, z1, step, mode="inter", breaks=ybreaks, holes=holes)
    m = len(P_)
    for i in range(m):
        a, b = P_[i], P_[(i + 1) % m]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < min_edge or abs(dx) < 0.05 or abs(dy) < 0.05:
            continue                                       # aresta em X ou Y: a faixa ja encosta nela
        # maior faixa que a aresta atravessa (as faixas quebram nos vertices e a cada 'step')
        y0, y1 = min(a[1], b[1]), max(a[1], b[1])
        hmax = 0.0
        y = y0
        while y < y1 - 1e-6:
            nb = min([y + step, y1] + [q for q in ybreaks if q > y + 1e-6])
            hmax = max(hmax, nb - y)
            y = nb
        w = min(hmax * abs(dx) / ln + 0.35, 16.0)
        inx, iny = -dy / ln, dx / ln                      # normal para DENTRO (anti-horario)
        th0 = _interior_angle(P_[i - 1], a, b)
        th1 = _interior_angle(a, b, P_[(i + 2) % m])

        def cut(th):
            if th < 90.0:                                 # vertice agudo: a caixa sairia pela aresta vizinha
                return w / max(math.tan(math.radians(th)), 0.2)
            return 0.0                                    # obtuso ou reflexo: o semi-disco de dentro esta no poligono
        c0, c1 = cut(th0), cut(th1)
        ex, ey = dx / ln, dy / ln
        ang = math.atan2(dy, dx)

        def box1(t0, t1, ww):
            cx = a[0] + ex * (t0 + t1) / 2 + inx * ww / 2
            cy = a[1] + ey * (t0 + t1) / 2 + iny * ww / 2
            col_box(area, (t1 - t0, ww, z1 - z0), (cx, cy, (z0 + z1) / 2), (0, 0, ang))

        def box(t0, t1, ww):
            if not holes:
                box1(t0, t1, ww)
                return
            ok = []
            t = t0
            while t <= t1 + 1e-6:
                px, py = a[0] + ex * t, a[1] + ey * t
                ok.append((t, not _hits_holes(px, py, px + inx * ww, py + iny * ww, holes)))
                t += 0.25
            run = None
            for t, good in ok + [(t1 + 1.0, False)]:
                if good and run is None:
                    run = t
                elif not good and run is not None:
                    te = min(t - 0.25, t1)
                    if te - run > 0.3:
                        box1(run, te, ww)
                    run = None
        L_ = ln - c0 - c1
        if L_ >= 0.5:
            box(c0, ln - c1, w)
            n += 1
        # canto agudo: escada de 2 caixas mais estreitas no recorte (a cunha tem largura t.tan(angulo) a distancia t)
        for th, c, end in ((th0, c0, 0), (th1, c1, 1)):
            if c < 1.0 or c > ln:
                continue
            tn = math.tan(math.radians(th))
            for f0, f1 in ((0.34, 0.67), (0.67, 1.0)):
                ww = min(w, f0 * c * tn) - 0.05
                if ww < 0.3:
                    continue
                t0, t1 = (f0 * c, f1 * c) if end == 0 else (ln - f1 * c, ln - f0 * c)
                box(t0, t1, ww)
                n += 1
    return n


# ------------------------------------------------------------------ superficies e topos (para as guardas)
def rock_walk():
    return [(nm, pts, z) for nm, pts, z in L.ROCKS if L.ROCK_COL.get(nm) == "walk"]


def water_polys():
    """leitos colidiveis (nome, poligono, cota do leito): segmentos dos canais, bacia, lago e rego do NE"""
    out = []
    for cn, pts, w in (("CanalE", L.CANAL_E, L.CANAL_E_W), ("CanalW", L.CANAL_W, L.CANAL_W_X[1] - L.CANAL_W_X[0])):
        P_ = list(pts)
        if cn == "CanalW":                                # o leito vai ate o labio da queda oeste
            P_ = P_ + [(L.FALL_W[0], L.FALL_W[1], P_[-1][2])]
        else:
            P_ = P_ + [(L.FALL_E[0], L.FALL_E[1], P_[-1][2])]
        for k, (a, b) in enumerate(zip(P_, P_[1:])):
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.5:
                continue
            ux, uy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ux, uy)
            ux, uy = ux / ln, uy / ln
            ext = w / 2                                   # emenda nos cantos
            a2 = (a[0] - ux * ext, a[1] - uy * ext) if k else (a[0], a[1])
            b2 = (b[0] + ux * ext, b[1] + uy * ext) if k < len(P_) - 2 else (b[0], b[1])
            out.append(("%s%d" % (cn, k), L.ribbon([a2, b2], w / 2), min(a[2], b[2]) - L.CANAL_BED))
    out.append(("Basin", list(L.BASIN), L.BASIN_Z - L.CANAL_BED))
    rect, pz = L.NE_POND
    out.append(("Pond", L.rect_poly(rect), pz - L.CANAL_BED))
    out.append(("PondLink", L.rect_poly(L.NE_POND_LINK), pz - L.CANAL_BED))
    return out


def solid_top(x, y):
    """maior topo colidivel em (x, y): piso da planta, rocha (qualquer), leito de agua; None = vazio/mar"""
    best = L.zone_of(x, y)
    for nm, pts, z in L.ROCKS:
        if L.point_in_poly(x, y, pts) and (best is None or z > best):
            best = z
    if best is None:
        for nm, pts, z in water_polys():
            if L.point_in_poly(x, y, pts):
                best = z if best is None else max(best, z)
    return best


# ------------------------------------------------------------------ guardas (item 4)
def _runs(pts, keep, step=1.0, closed=True):
    runs, run = [], []
    n = len(pts)
    for i in range(n if closed else n - 1):
        a = Vector((*pts[i], 0))
        b = Vector((*pts[(i + 1) % n], 0))
        d = b - a
        ns = max(1, int(d.length / step))
        for k in range(ns + (0 if closed else 1)):
            p = a + d * (k / ns)
            if keep(p.x, p.y):
                run.append(p)
            else:
                if len(run) > 1:
                    runs.append(run)
                run = []
    if len(run) > 1:
        runs.append(run)
    return runs


def _wall(area, run, zf, h, th=1.0, max_len=60.0):
    """parede invisivel ao longo de uma corrida RETA (as corridas sao por aresta): poucas caixas longas"""
    p0, p1 = run[0], run[-1]
    d = p1 - p0
    ln = d.length
    if ln < 0.3:
        return
    k = max(1, int(math.ceil(ln / max_len)))
    for i in range(k):
        a = p0 + d * (i / k)
        b = p0 + d * ((i + 1) / k)
        mid = (a + b) / 2
        z0 = max(zf(a.x, a.y), zf(b.x, b.y)) - 0.5
        col_box(area, ((b - a).length + 0.8, th, h), (mid.x, mid.y, z0 + h / 2), (0, 0, math.atan2(d.y, d.x)))


def guard_surfaces():
    """(nome, poligono, cota) das superficies alcancaveis que recebem guarda no labio: pisos (menos o convés: amurada
    propria), rochas 'walk' e leitos de agua"""
    out = [(nm, poly, z) for nm, poly, z, pr in L.floors()]
    out += [("Rock" + nm, pts, z) for nm, pts, z in rock_walk()]
    out += [("Water" + nm, pts, z) for nm, pts, z in water_polys()]
    return out


def _owner(nm, poly, z, x, y):
    """(x, y) pertence VISUALMENTE a esta superficie? (piso: o de maior prioridade; rocha/agua: dentro e sem piso)"""
    if nm.startswith(("Rock", "Water")):
        if not L.point_in_poly(x, y, poly):
            return False
        if nm.startswith("Water"):
            return L.zone_of(x, y) is None
        return L.zone_of(x, y) is None
    return L.floor_name(x, y) == nm


def edge_guards():
    """borda de superficie alcancavel cuja queda para fora leva ao VAZIO/mar ou passa do pulo (7,2: nao se volta)
    ganha parede invisivel de 8,5 no labio. Topo/pe de escada, cabeca de ponte e o vao da ancora ficam abertos."""
    n_runs = 0
    for nm, poly, z in guard_surfaces():
        pts = ccw(poly)
        zf = (lambda x, y, z=z: L._zval(z, x, y))
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = dy / ln, -dx / ln                      # para fora (anti-horario)

            def keep(x, y, nx=nx, ny=ny, nm=nm, zf=zf, poly=poly, z=z):
                if not _owner(nm, poly, z, x - nx * 0.6, y - ny * 0.6):
                    return False
                ox, oy = x + nx * 1.6, y + ny * 1.6
                if opening(ox, oy) or opening(x, y):
                    return False
                zo = solid_top(ox, oy)
                if zo is None:
                    return True                             # vazio / mar
                return zf(x, y) - zo > JUMP                 # queda maior que o pulo: nao se volta
            ex, ey = dx / ln, dy / ln
            for run in _runs([a, b], keep, closed=False):
                shifted = [Vector((p.x + nx * 1.1, p.y + ny * 1.1, 0)) for p in run]
                shifted[0] = shifted[0] - Vector((ex * 1.1, ey * 1.1, 0))      # fecha a cunha do canto
                shifted[-1] = shifted[-1] + Vector((ex * 1.1, ey * 1.1, 0))
                _wall("OP_Guard", shifted, zf, GUARD_H + 0.5, th=2.2)
                n_runs += 1
    return n_runs


# ------------------------------------------------------------------ chao, rochas, agua
def floors():
    """caixas MACICAS ate FLOOR_BOT cobrindo cada piso SEM extrapolar (poly_cover), sem os entalhes das escadas
    (+ enchimento ate a cota do pe da escada). O convés do navio e fino (casco: nao e terreno)."""
    n = 0
    notches = {}
    for snm, up, rect, zf, zt in L.stair_notches():
        if up:
            notches.setdefault(up, []).append(rect)
    for nm, poly, z, pr in L.floors():
        bot = z - 2.0 if nm == "ShipDeck" else L.FLOOR_BOT
        holes = notches.get(nm, []) + list(L.FLOOR_HOLES.get(nm, ()))
        n += poly_cover(A, poly, bot, z, 14.0, holes=holes)
    for nm, up, rect, zf, zt in L.stair_notches():
        if up is None:
            continue
        fill = L.clip_rect(ccw(L.floor_poly(up)), rect)
        if len(fill) >= 3:
            xs = [p[0] for p in fill]
            ys = [p[1] for p in fill]
            col_box2(A, (min(xs), min(ys), L.FLOOR_BOT), (max(xs), max(ys), zf))
            n += 1
    return n


def rock_cols():
    """item 3: cada massa de L.ROCKS colide macica ate o topo visual (o visual do blockout/terreno e o prisma da planta)"""
    n = 0
    for nm, pts, z in L.ROCKS:
        n += poly_cover("OP_Rock" + nm, pts, L.FLOOR_BOT, z, 14.0)
    return n


def water_beds():
    """item 5: leito colidivel 1,0 abaixo da agua em canais, bacia, lago e rego (a agua do Roblox nao colide)"""
    n = 0
    for nm, pts, z in water_polys():
        n += poly_cover("OP_Bed" + nm, pts, L.FLOOR_BOT, z, 10.0)
    return n


def _near_bridge(x, y, pad=0.4):
    for nm, a, b, w in L.bridge_list():
        if nm in L.BRIDGE_ARCH and _in_rect_along(x, y, a, b, w / 2 + pad, pad=0.0):
            return True
    return False


def coping_runs():
    """capa (mureta) de 0,9 nas margens dos canais, do lado do PISO (so onde a margem e piso), interrompida nas pontes
    em arco: lista de (a, b, cota da margem, normal para o canal) com a e b na linha de centro da capa. A capa avanca 0,2
    sobre o canal (cobre o topo do muro de cantaria, que fica 0,12 para dentro do vao)"""
    out = []
    hw0 = L.CANAL_COPE_W / 2 - 0.2
    for cn, pts, w in (("E", L.CANAL_E, L.CANAL_E_W), ("W", L.CANAL_W, L.CANAL_W_X[1] - L.CANAL_W_X[0])):
        for a, b in zip(pts, pts[1:]):
            ux, uy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ux, uy)
            if ln < 0.5:
                continue
            ux, uy = ux / ln, uy / ln
            for s in (-1, 1):
                off = s * (w / 2 + hw0)
                nx, ny = -uy * off, ux * off

                def ok(t):
                    x, y = a[0] + ux * t + nx, a[1] + uy * t + ny
                    zb = L.zone_of(x + (nx / abs(off)) * 1.2, y + (ny / abs(off)) * 1.2)
                    return zb is not None and not _near_bridge(x, y) and not opening(x, y) and zb > a[2]
                t, run = 0.0, None
                while t <= ln + 1e-6:
                    if ok(t):
                        run = t if run is None else run
                    elif run is not None:
                        if t - run > 1.0:
                            out.append(((a[0] + ux * run + nx, a[1] + uy * run + ny),
                                        (a[0] + ux * (t - 0.5) + nx, a[1] + uy * (t - 0.5) + ny),
                                        _bank_z(a, ux, uy, run, nx, ny, off), (-nx / abs(off), -ny / abs(off))))
                        run = None
                    t += 0.5
                if run is not None and ln - run > 1.0:
                    out.append(((a[0] + ux * run + nx, a[1] + uy * run + ny), (b[0] + nx, b[1] + ny),
                                _bank_z(a, ux, uy, run, nx, ny, off), (-nx / abs(off), -ny / abs(off))))
    return out


def _bank_z(a, ux, uy, t, nx, ny, off):
    k = 1.0 + 1.2 / abs(off)
    return L.zone_of(a[0] + ux * t + nx * k, a[1] + uy * t + ny * k)


def copings():
    n = 0
    for a, b, zb, nrm in coping_runs():
        if zb is None:
            continue
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        col_box("OP_CanalCope", (ln, L.CANAL_COPE_W, L.CANAL_COPE_H + 0.5),
                ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zb + (L.CANAL_COPE_H - 0.5) / 2),
                (0, 0, math.atan2(b[1] - a[1], b[0] - a[0])))
        n += 1
    return n


# ------------------------------------------------------------------ lotes da cidade V2 (item 6)
def _frame(lot):
    return DL.Frame(lot["x"], lot["y"], lot["z"], lot["yaw"] - math.pi / 2)     # +y local = FRENTE


def roof_col(area, F, W, D, z_eave, z_ridge, tsuma=False, ov=None, g_over=0.6):
    """colisao de um telhado de 2 aguas: 1 rampa por agua (topo da rampa = plano do telhado, do beiral com balanco
    ate a cumeeira). F = Frame no centro da planta (z = piso), +y = frente; W ao longo de x, D ao longo de y; cumeeira
    ao longo de x (hirairi) ou de y (tsumairi). z_eave/z_ridge ABSOLUTOS. Serve ao op_capital V2-3 com o info do kit."""
    ov = L.ROOF_OV if ov is None else ov
    k = (z_ridge - z_eave) / ((W if tsuma else D) / 2.0)
    z0 = F.p(0, 0, 0).z
    zr, ze = z_ridge - z0, z_eave - z0
    if not tsuma:
        span, length = D / 2 + ov, W + 2 * g_over
        for s in (-1, 1):
            a = F.p(0, s * span, ze - k * ov)
            b = F.p(0, 0, zr)
            col_ramp(area, a, b, length, thick=1.2)
    else:
        span, length = W / 2 + ov, D + 2 * g_over
        for s in (-1, 1):
            a = F.p(s * span, 0, ze - k * ov)
            b = F.p(0, 0, zr)
            col_ramp(area, a, b, length, thick=1.2)
    return 2


def _lot_tops():
    """topos de referencia do alcance (pisos + rochas walk + pontes): amostras (x, y, z)"""
    pts = []
    for nm, poly, z, pr in L.floors():
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x = min(xs)
        while x <= max(xs):
            y = min(ys)
            while y <= max(ys):
                if L.floor_name(x, y) == nm:
                    pts.append((x, y, L._zval(z, x, y)))
                y += 4.0
            x += 4.0
    for nm, poly, z in rock_walk():
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x = min(xs)
        while x <= max(xs):
            y = min(ys)
            while y <= max(ys):
                if L.point_in_poly(x, y, poly) and L.zone_of(x, y) is None:
                    pts.append((x, y, z))
                y += 4.0
            x += 4.0
    for a, b, zb, nrm in coping_runs():                # capa dos canais (0,9) e guarda-corpo das pontes em arco
        if zb is not None:
            for t in (0.0, 0.25, 0.5, 0.75, 1.0):
                pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, zb + L.CANAL_COPE_H))
    for nm, a, b, w in L.bridge_list():
        if nm in L.BRIDGE_ARCH:
            pts.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, a[2] + L.BRIDGE_ARCH[nm] + 1.2))
    return pts


def reachable_lots(lots, margin=8.0):
    """lotes cujo telhado fica ao alcance (beiral baixo <= topo alcancavel a <= margin + 7,2 + 0,5), propagando de
    telhado em telhado (um telhado alcancavel e topo para o vizinho)"""
    tops = _lot_tops()
    reach = {}
    low = {}
    for lt in lots:
        k = (lt["ridge"] - lt["eave"]) / ((lt["W"] if lt["tsuma"] else lt["D"]) / 2.0)
        low[lt["name"]] = lt["eave"] - k * L.ROOF_OV

    def near_top(lt, extra):
        best = -1e9
        R = max(lt["W"], lt["D"]) / 2 + margin
        for x, y, z in tops + extra:
            if abs(x - lt["x"]) <= R and abs(y - lt["y"]) <= R:
                best = max(best, z)
        return best
    changed = True
    while changed:
        changed = False
        extra = [(o["x"], o["y"], o["ridge"]) for o in lots if reach.get(o["name"])]
        for lt in lots:
            if reach.get(lt["name"]):
                continue
            if low[lt["name"]] <= near_top(lt, [e for e in extra if e[:2] != (lt["x"], lt["y"])]) + JUMP + 0.5:
                reach[lt["name"]] = True
                changed = True
    return reach


def lot_cols(lots=None):
    """item 6: corpo de cada lote (caixa macica ate o beiral; o portal so acima de 7 = passagem livre; a frente aberta
    do santuario so com piso + pilares) e as aguas do telhado com rampa quando alcancavel. Hisashi alcancavel: rampa."""
    lots = L.block_lots() if lots is None else lots
    reach = reachable_lots(lots)
    n = 0
    for lt in lots:
        F = _frame(lt)
        area = "OP_Lot" + lt["name"]
        W, D, z = lt["W"], lt["D"], lt["z"]
        h = lt["eave"] - z
        if lt["kind"] == "portal":
            col_box(area, (W, D, h - 7.0), F.p(0, 0, 7.0 + (h - 7.0) / 2), F.r())
            n += 1
        elif lt["open"]:
            dz = D * 0.45                                   # 45% de tras fechado; frente aberta (alpendre com piso)
            col_box(area, (W, D - dz, h + 0.5), F.p(0, -dz / 2, (h - 0.5) / 2), F.r())
            col_box(area, (W, dz, 0.8 + 0.5), F.p(0, (D - dz) / 2, 0.8 / 2 - 0.25), F.r())
            for sx in (-1, 1):
                col_box(area, (1.0, 1.0, h - 0.8), F.p(sx * (W / 2 - 0.6), D / 2 - 0.6, 0.8 + (h - 0.8) / 2), F.r())
            n += 4
        else:
            col_box(area, (W, D, h + 0.5), F.p(0, 0, (h - 0.5) / 2), F.r())
            n += 1
        if reach.get(lt["name"]):
            n += roof_col(area, F, W, D, lt["eave"], lt["ridge"], lt["tsuma"])
            lt["roof_col"] = True
    return n


def raise_guards(margin=4.0):
    """POS-PASSE (build_op, depois de todas as zonas): a guarda tem de ficar 8,5 acima de TUDO o que se alcanca perto
    dela, nao so do piso - muro, toro, banco ou caixa a <= 7,2 do piso viram degrau para o topo da guarda (cadeia
    medida pelo gate 'visual': muro do patio do castelo -> guarda -> BackN). Sobe cada COL_OP_Guard_* que tem, a menos
    de 'margin', uma colisao de outra area com topo entre o piso da guarda e o topo dela."""
    import bpy
    bpy.context.view_layer.update()                    # matrix_world das caixas recem-criadas
    guards, others = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
        bb = (min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws), max(v.x for v in ws),
              max(v.y for v in ws), max(v.z for v in ws))
        if o.name.startswith("COL_OP_Guard_"):
            guards.append((o, bb))
        elif not o.name.startswith(("COL_QA_",)) and "Guard" not in o.name:
            others.append((o, bb))                      # piso, rocha, leito, escada, ponte, prop, muro, lote
    n = 0
    for g, gb in guards:
        floor = gb[2] + 0.5
        near = [ob[5] for o, ob in others if not (ob[3] < gb[0] - margin or ob[0] > gb[3] + margin or
                                                  ob[4] < gb[1] - margin or ob[1] > gb[4] + margin)]
        need = gb[5]
        tops = [t for t in near if t > floor + 0.5]     # o que fica acima do piso perto da guarda (muro, prop, rocha)
        if tops:
            need = max(need, max(tops) + GUARD_H)       # o topo da guarda fica 8,5 acima de tudo isso
        if need > gb[5] + 1e-3:
            h = need - gb[2]
            g.scale.z = h
            g.location.z = gb[2] + h / 2
            n += 1
    return n


# ------------------------------------------------------------------ montagem
def terrain_col():
    floors()
    for nm, base, ang, w, n, rise, tread, g in stair_list():
        stair_col("OP_Stair" + nm, base, ang, w, n, rise, tread, guards=g)
    bridges()
    rock_cols()
    water_beds()
    copings()
    edge_guards()
