# op_col - COMPARTILHADO E CONGELADO (dono: integracao / M1). Colisao de TUDO que e andavel na Ilha 5, independente do
# visual: piso de cada patamar (poligonos da planta, caixas MACICAS ate FLOOR_BOT), escadas (col_ramp + guardas),
# pontes (chegada 80,2 -> 84,2; ponte vermelha de saida; 2 pontes do canal; prancha do navio), guarda PROVISORIA da
# ancora One Punch Man e as guardas invisiveis (toda borda de piso com queda > 2,3 para fora, exceto topo/pe de escada,
# cabeca de ponte e o vao da ancora). Canais e bacia sao BURACOS entre pisos: a guarda sai sozinha nas margens.
# A PRACA tem piso PLANO a 92,2 (o raycast do SpawnMinerio exige |piso - 92,2| < 0,5 e normal > 0,85).
import math
from mathutils import Vector
import op_lib as DL
from op_lib import col_box, col_box2, col_ramp, ccw
import op_layout as L

A = "OP_Terrain"
GUARD_H = 3.2          # guarda invisivel (acima do piso)
DROP = 2.3             # queda que pede guarda


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


def bridges():
    for nm, a, b, w in L.bridge_list():
        ux, uy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        vx, vy = -uy, ux
        dz = (b[2] - a[2]) / ln
        eb = 0.4 if nm == "Gangway" else 2.0          # a prancha termina RENTE ao convés (sem degrau de ponta)
        a2 = (a[0] - ux * 2.0, a[1] - uy * 2.0, a[2] - dz * 2.0)
        b2 = (b[0] + ux * eb, b[1] + uy * eb, b[2] + dz * eb)
        col_ramp("OP_" + nm, a2, b2, w, thick=2.0)
        for s in (-1, 1):
            o = s * (w / 2 + 0.6)
            ga = (a[0] + vx * o, a[1] + vy * o, a[2] + GUARD_H + 0.8)
            gb = (b[0] + vx * o, b[1] + vy * o, b[2] + GUARD_H + 0.8)
            col_ramp("OP_" + nm, ga, gb, 1.2, thick=GUARD_H + 1.3)
    anchor_guard()


def anchor_guard():
    """guarda PROVISORIA da ancora One Punch Man (a integracao da area 6 remove: next_island_guard)"""
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    ap = L.anchor_opm_pos()
    g = col_box("OPAnchorGuard", (1.2, L.EXIT_W + 2.0, 9.0), (ap[0] + ux * 0.6, ap[1] + uy * 0.6, L.T1 + 4.0), (0, 0, a))
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


def _wall(area, run, zf, h, th=1.0, chord=14):
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
    """toda borda de piso VISIVEL cuja queda para fora passa de 2,3 ganha parede invisivel; fora de piso = queda (mar,
    canal, bacia). Topo/pe de escada, cabeca de ponte e o vao da ancora ficam abertos."""
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
                return not opening(ox, oy) and not opening(x, y)
            for run in _runs([a, b], keep, closed=False):
                shifted = [Vector((p.x + nx * 0.5, p.y + ny * 0.5, 0)) for p in run]
                _wall("OP_Guard", shifted, zf, GUARD_H + 0.5)
                n_runs += 1
    return n_runs


# ------------------------------------------------------------------ chao
def strips(area, poly, z0, z1, step, mode="inter", breaks=()):
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        yb = min([y + step, max(ys)] + [b for b in breaks if b > y + 1e-6])
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


def floors():
    """caixas MACICAS ate FLOOR_BOT em faixas de 6 (modo 'union'), sem os entalhes das escadas (+ enchimento ate a cota
    do pe da escada). O convés do navio e fino (casco: nao e terreno)."""
    for nm, poly, z, pr in L.floors():
        bot = z - 2.0 if nm == "ShipDeck" else L.FLOOR_BOT
        for piece in L.floor_pieces(nm):
            # M6b-D (item 36, acrescimo pontual): no cais a faixa 'union' nao pode atravessar uma aresta horizontal do
            # poligono (y 76 e 110: a faixa 72..80 e a 104..112 viravam piso INVISIVEL sobre o mar ao lado da palafita
            # e na raiz do pier) -> a faixa quebra nessas cotas
            brk = (sorted({a[1] for a, b in zip(piece, piece[1:] + piece[:1]) if abs(a[1] - b[1]) < 1e-6})
                   if nm == "Harbor" else ())
            strips(A, ccw(piece), bot, z, 8.0, mode="union", breaks=brk)
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
        stair_col("OP_Stair" + nm, base, ang, w, n, rise, tread, guards=g)
    bridges()
    edge_guards()
