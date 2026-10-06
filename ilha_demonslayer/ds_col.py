# ds_col - COMPARTILHADO E CONGELADO (dono: integracao / onda 0). Colisao de TUDO que e andavel na Ilha 4, independente
# do visual: piso de cada patamar (poligonos da planta, caixas MACICAS ate FLOOR_BOT: ninguem passa por baixo de um
# terraco), o bambuzal INCLINADO (rampas por faixa), escadas (col_ramp + guardas), ponte de chegada (rampa 52,2 ->
# 54,2), ponte de saida, cabeceira do portao One Piece (+ guarda PROVISORIA da ancora), a lagoa (anel) e as guardas
# invisiveis (toda borda de piso com queda > 2,3 para fora, exceto topo/pe de escada e cabeca de ponte).
# A CLAREIRA tem piso PLANO a 60,2 (o raycast do SpawnMinerio exige |piso - 60,2| < 0,5 e normal > 0,85).
# Os modulos de detalhe desenham SO o visual destas pecas (escadas com ds_lib.plan_stair) e criam a colisao SO dos
# proprios predios/props. Generico: a planta (ds_layout.floors/STAIRS/bridge_list) manda.
import math
from mathutils import Vector
import ds_lib as DL
from ds_lib import col_box, col_box2, col_ramp, ccw
import ds_layout as L

A = "DS_Terrain"
GUARD_H = 3.2          # guarda invisivel (acima do piso)
DROP = 2.3             # queda que pede guarda


# ------------------------------------------------------------------ escadas (so colisao)
def stair_col(area, base, ang, width, n, rise, tread, guards=True, guard_h=4.0):
    """a colisao de fm_parts.stairs (rampa pelo meio dos pisos + meia pisada final + banzos) sem a geometria"""
    F = DL.Frame(base[0], base[1], base[2], ang)
    bot = F.p(-tread / 2, 0, 0)
    top = F.p(tread * n - tread / 2, 0, rise * n)
    col_ramp(area, bot, top, width)
    q = F.p(tread * n - tread / 4 + 0.15, 0, rise * n - 0.5)
    col_box(area, (tread / 2 + 0.3, width, 1.0), (q.x, q.y, q.z), F.r())
    if guards:
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
    out = []
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        out.append((nm, foot, math.radians(deg), w, n, L.stair_rise(nm), tread, g))
    return out


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


# ------------------------------------------------------------------ pontes / cabeceira
def _in_rect_along(x, y, a, b, hw, pad=0.0):
    ux, uy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ux, uy) or 1.0
    ux, uy = ux / ln, uy / ln
    t = (x - a[0]) * ux + (y - a[1]) * uy
    d = abs(-(x - a[0]) * uy + (y - a[1]) * ux)
    return -pad <= t <= ln + pad and d <= hw


def opening(x, y):
    """(x, y) cai numa escada ou numa ponte: a borda do piso ali fica aberta"""
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        if L.point_in_poly(x, y, stair_footprint(nm, pad=1.0)):
            return True
    for nm, a, b, w in L.bridge_list():
        if _in_rect_along(x, y, a, b, w / 2, pad=2.0):
            return True
    return False


def bridges():
    for nm, a, b, w in L.bridge_list():
        ux, uy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        vx, vy = -uy, ux
        dz = (b[2] - a[2]) / ln
        # tabuleiro: passa 2 de cada ponta (encosta no piso/cabeceira sem fresta), mesma inclinacao
        a2 = (a[0] - ux * 2.0, a[1] - uy * 2.0, a[2] - dz * 2.0)
        b2 = (b[0] + ux * 2.0, b[1] + uy * 2.0, b[2] + dz * 2.0)
        col_ramp("DS_" + nm, a2, b2, w, thick=2.0)
        for s in (-1, 1):
            o = s * (w / 2 + 0.6)
            ga = (a[0] + vx * o, a[1] + vy * o, a[2] + GUARD_H + 0.8)
            gb = (b[0] + vx * o, b[1] + vy * o, b[2] + GUARD_H + 0.8)
            col_ramp("DS_" + nm, ga, gb, 1.2, thick=GUARD_H + 1.3)
    pier()


def pier():
    """cabeceira de pedra (30 x 30) do portao One Piece: piso + guardas (abertas na ponte e no corredor da ancora) +
    guarda PROVISORIA da ancora (a integracao da One Piece remove: next_island_guard)"""
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    pw, pd = L.PIER
    c = L.exit_point(L.EXIT_BRIDGE_LEN + pd / 2)
    col_box("DS_Pier", (pd + 1.0, pw, 8.0), (c[0], c[1], L.T4 - 4.0), (0, 0, a))
    hw = L.EXIT_W / 2 + 0.6
    for s in (-1, 1):
        # laterais (paralelas a ponte), inteiras
        q = L.exit_point(L.EXIT_BRIDGE_LEN + pd / 2, s * (pw / 2 + 0.6))
        col_box("DS_PierGuard", (pd + 1.2, 1.2, GUARD_H + 1.0), (q[0], q[1], L.T4 + (GUARD_H + 1.0) / 2 - 0.5), (0, 0, a))
        # ombros da frente (lado da ponte) e do fundo (lado da ancora), fora do vao de 18
        for d in (L.EXIT_BRIDGE_LEN - 0.6, L.EXIT_BRIDGE_LEN + pd + 0.6):
            v0, v1 = hw, pw / 2 + 1.2
            q = L.exit_point(d, s * (v0 + v1) / 2)
            col_box("DS_PierGuard", (1.2, v1 - v0, GUARD_H + 1.0), (q[0], q[1], L.T4 + (GUARD_H + 1.0) / 2 - 0.5),
                    (0, 0, a))
    ap = L.anchor_op_pos()
    g = col_box("DSAnchorGuard", (1.2, L.EXIT_W + 2.0, 9.0), (ap[0] + ux * 0.6, ap[1] + uy * 0.6, L.T4 + 4.0), (0, 0, a))
    g["next_island_guard"] = True


# ------------------------------------------------------------------ guardas
def _runs(pts, keep, step=1.0, closed=True):
    runs, run = [], []
    n = len(pts)
    for i in range(n if closed else n - 1):
        a = Vector((*pts[i], 0))
        b = Vector((*pts[(i + 1) % n], 0))
        d = b - a
        ns = max(1, int(d.length / step))
        for k in range(ns):
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


def _wall(area, run, zf, h, th=1.0, chord=10):
    """parede invisivel ao longo do trecho; zf = funcao (x, y) -> piso"""
    i = 0
    while i < len(run) - 1:
        j = min(len(run) - 1, i + chord)
        p0, p1 = run[i], run[j]
        mid = (p0 + p1) / 2
        d = p1 - p0
        if d.length > 0.3:
            z0 = max(zf(p0.x, p0.y), zf(p1.x, p1.y)) - 0.5
            col_box(area, (d.length + 0.8, th, h), (mid.x, mid.y, z0 + h / 2), (0, 0, math.atan2(d.y, d.x)))
        i = j


def edge_guards():
    """toda borda de piso VISIVEL (o ponto logo para dentro pertence a este piso) cuja queda para fora passa de 2,3 ganha
    parede invisivel; fora de piso = queda. Topo/pe de escada e cabeca de ponte ficam abertos."""
    n_runs = 0
    for nm, poly, z, pr in L.floors():
        pts = ccw(poly)
        zf = (lambda x, y, z=z: L._zval(z, x, y))
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = dy / ln, -dx / ln                      # para fora (anti-horario)

            def keep(x, y, nx=nx, ny=ny, nm=nm, zf=zf):
                if L.floor_name(x - nx * 0.6, y - ny * 0.6) != nm:
                    return False
                ox, oy = x + nx * 1.6, y + ny * 1.6
                zo = L.zone_of(ox, oy)
                if zo is not None and zf(x, y) - zo <= DROP:
                    return False
                return not opening(ox, oy)
            for run in _runs([a, b], keep, closed=False):
                shifted = [Vector((p.x + nx * 0.5, p.y + ny * 0.5, 0)) for p in run]
                _wall("DS_Guard", shifted, zf, GUARD_H + 0.5)
                n_runs += 1
    return n_runs


def pond_guard():
    """lagoa (agua do Roblox): anel invisivel no contorno (ninguem entra na agua)"""
    P = ccw(L.POND)
    run = [Vector((x, y, 0)) for x, y in P + [P[0]]]
    _wall("DS_PondGuard", run, lambda x, y: L.T1, GUARD_H + 0.5, chord=1)


# ------------------------------------------------------------------ chao
def strips(area, poly, z0, z1, step, mode="inter"):
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        yb = min(y + step, max(ys))
        ya = y
        ivs = None
        for sm in (ya + 0.05, (ya + yb) / 2, yb - 0.05):
            iv = DL.x_intervals(poly, sm)
            ivs = iv if ivs is None else (DL.IL._union(ivs, iv) if mode == "union" else DL.IL._inter(ivs, iv))
        for a, b in ivs or []:
            if b - a > 0.3:
                col_box2(area, (a, ya, z0), (b, yb, z1))
                n += 1
        y = yb
    return n


def edge_fill(area, poly, z0, z1, w=4.6):
    pts = ccw(poly)
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            continue
        nx, ny = -dy / ln, dx / ln
        mid = ((a[0] + b[0]) / 2 + nx * w / 2, (a[1] + b[1]) / 2 + ny * w / 2)
        col_box(area, (ln + 0.4, w, z1 - z0), (mid[0], mid[1], (z0 + z1) / 2), (0, 0, math.atan2(dy, dx)))


def sloped_strips(area, poly, zfun, step=3.0):
    """piso inclinado (bambuzal): uma rampa por faixa em y (inclinacao continua, sem degrau)"""
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        yb = min(y + step, max(ys))
        ivs = None
        for sm in (y + 0.05, (y + yb) / 2, yb - 0.05):
            iv = DL.x_intervals(poly, sm)
            ivs = iv if ivs is None else DL.IL._union(ivs, iv)
        for a, b in ivs or []:
            if b - a > 0.3:
                xm = (a + b) / 2
                col_ramp(area, (xm, y - 0.05, zfun(xm, y - 0.05)), (xm, yb + 0.05, zfun(xm, yb + 0.05)), b - a + 0.2,
                         thick=6.0)
                n += 1
        y = yb
    return n


def floors():
    """caixas MACICAS ate FLOOR_BOT em faixas de 6 (modo 'union': cobrem ate a aresta; o que passa da aresta fica atras
    da guarda ou dentro do patamar vizinho), sem os entalhes das escadas (+ enchimento ate a cota do pe da escada)"""
    for nm, poly, z, pr in L.floors():
        if callable(z):
            sloped_strips(A, ccw(poly), z)
            continue
        for piece in L.floor_pieces(nm):
            strips(A, ccw(piece), L.FLOOR_BOT, z, 6.0, mode="union")
    for nm, up, rect, zf, zt in L.stair_notches():
        if up is None:
            continue
        fill = L.clip_rect(ccw(L.floor_poly(up)), rect)
        if len(fill) >= 3:
            xs = [p[0] for p in fill]
            ys = [p[1] for p in fill]
            col_box2(A, (min(xs), min(ys), L.FLOOR_BOT), (max(xs), max(ys), zf))


def terrain_col():
    floors()
    for nm, base, ang, w, n, rise, tread, g in stair_list():
        stair_col("DS_Stair" + nm, base, ang, w, n, rise, tread, guards=g)
    bridges()
    edge_guards()
    pond_guard()
