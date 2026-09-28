# sg_col - COMPARTILHADO E CONGELADO (dono: integracao). Colisao de TUDO que e andavel na Ilha 3, independente do
# visual: piso de cada patamar (poligonos da planta), escadas (col_ramp), pontes (chegada, summon, saida), ilhota do
# portao Demon Slayer, a bacia da fonte e as guardas invisiveis (toda borda de piso com queda > 2,3 para o lado de fora,
# exceto topo de escada e cabeceira de ponte). Os modulos de detalhe desenham SO o visual destas pecas (escadas com
# sg_lib.plan_stair, guardas com vis_parapet/vis_fence) e criam a colisao SO dos proprios predios/props.
# Generico por construcao: a planta (sg_layout.floors/STAIRS) manda; nada aqui tem coordenada solta.
import math
from mathutils import Vector
import sg_lib as SL
from sg_lib import col_box, col_box2, col_ramp, ccw, ngon_col
import sg_layout as L

A = "SG_Terrain"
GUARD_H = 3.2          # guarda invisivel (acima do piso de cima)
FLOOR_T = 8.0          # espessura das caixas de piso (a de cima encosta na de baixo: sem fresta entre patamares)


# ------------------------------------------------------------------ escadas (so colisao)
def stair_col(area, base, ang, width, n, rise, tread, guards=True, guard_h=4.0):
    """a colisao de fm_parts.stairs (rampa pelo meio dos pisos + meia pisada final + banzos) sem a geometria"""
    F = SL.Frame(base[0], base[1], base[2], ang)
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
    """(nome, pe (x, y, z), rumo_rad, largura, n, espelho, piso, guardas) de todas as escadas da planta"""
    out = []
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        rise = (L.STAIR_TOP_Z[nm] - foot[2]) / n
        out.append((nm, foot, math.radians(deg), w, n, rise, tread, g))
    return out


def stair_footprint(nm, pad=0.0):
    """retangulo (poligono) ocupado pela escada, do pe ao topo (pad alonga as pontas)"""
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    x0, y0 = foot[0] - ux * (tread / 2 + pad), foot[1] - uy * (tread / 2 + pad)
    x1, y1 = foot[0] + ux * (tread * n + pad), foot[1] + uy * (tread * n + pad)
    hw = w / 2
    return [(x0 + vx * hw, y0 + vy * hw), (x0 - vx * hw, y0 - vy * hw), (x1 - vx * hw, y1 - vy * hw),
            (x1 + vx * hw, y1 + vy * hw)]


# ------------------------------------------------------------------ pontes
def bridge_list():
    """(nome, inicio (x, y), fim (x, y), cota, largura)"""
    ex = L.exit_point(L.EXIT_BRIDGE_LEN)
    a0, a1, w = L.SUMMON_BRIDGE
    return [("Arrival", (0.0, L.BRIDGE_Y0), (0.0, L.BRIDGE_Y1), L.DECK, L.DECK_W),
            ("SummonBridge", a0, a1, L.P1, w),
            ("ExitBridge", L.EXIT_START, ex, L.EXIT_Z, L.EXIT_W)]


def _in_rect_along(x, y, a, b, hw, pad=0.0):
    ux, uy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ux, uy) or 1.0
    ux, uy = ux / ln, uy / ln
    t = (x - a[0]) * ux + (y - a[1]) * uy
    d = abs(-(x - a[0]) * uy + (y - a[1]) * ux)
    return -pad <= t <= ln + pad and d <= hw


def opening(x, y):
    """(x, y) cai numa escada, numa ponte ou na ilhota: a borda do piso ali fica aberta"""
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        if L.point_in_poly(x, y, stair_footprint(nm, pad=1.0)):
            return True
    for nm, a, b, z, w in bridge_list():
        if _in_rect_along(x, y, a, b, w / 2, pad=2.0):
            return True
    return False


def bridges():
    for nm, a, b, z, w in bridge_list():
        ux, uy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ux, uy)
        ang = math.atan2(uy, ux)
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        # tabuleiro (passa 2 de cada ponta: encosta no piso/ilhota sem fresta)
        col_box("SG_" + nm, (ln + 4.0, w, 2.0), (c[0], c[1], z - 1.0), (0, 0, ang))
        for s in (-1, 1):
            q = (c[0] - uy / ln * s * (w / 2 + 0.6), c[1] + ux / ln * s * (w / 2 + 0.6))
            col_box("SG_" + nm, (ln, 1.2, GUARD_H + 1.3), (q[0], q[1], z + (GUARD_H + 1.3) / 2 - 0.5), (0, 0, ang))
    # ilhota do portao Demon Slayer + plataforma da ancora + guardas (aberta na ponte e no corredor da ancora)
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    ic = L.islet_center()
    isl = [(ic[0] + L.GATE_ISLET_R * math.cos(t * math.pi / 12), ic[1] + L.GATE_ISLET_R * math.sin(t * math.pi / 12))
           for t in range(24)]
    SL.col_poly("SG_Islet", isl, L.EXIT_Z - 3.0, L.EXIT_Z, 3.0, mode="union")
    ap = L.anchor_pos()
    pc = (ap[0] - ux * 5.0, ap[1] - uy * 5.0)
    col_box("SG_Islet", (10.0, L.DECK_W, 2.0), (pc[0], pc[1], L.EXIT_Z - 1.0), (0, 0, a))
    bs = L.exit_point(L.EXIT_BRIDGE_LEN)

    def keep(x, y):
        t = (x - bs[0]) * ux + (y - bs[1]) * uy
        d = abs(-(x - bs[0]) * uy + (y - bs[1]) * ux)
        if d < L.EXIT_W / 2 + 0.6 and (t < 3.0 or t > L.ANCHOR_OFF - 14.0):
            return False
        return True
    for run in _runs(ccw(isl), keep):
        _wall("SG_Islet", run, L.EXIT_Z - 0.5, GUARD_H + 0.5)
    for s in (-1, 1):
        q = (pc[0] - uy * s * (L.DECK_W / 2 + 0.6), pc[1] + ux * s * (L.DECK_W / 2 + 0.6))
        col_box("SG_Islet", (10.0, 1.2, GUARD_H + 1.0), (q[0], q[1], L.EXIT_Z + (GUARD_H + 1.0) / 2 - 0.5), (0, 0, a))
    # guarda PROVISORIA da ancora (sai quando a ilha Demon Slayer encostar): parede invisivel na ponta
    g = col_box("SGAnchorGuard", (1.2, L.DECK_W + 2.0, 9.0), (ap[0] + ux * 0.6, ap[1] + uy * 0.6, L.EXIT_Z + 4.0),
                (0, 0, a))
    g["next_island_guard"] = True


# ------------------------------------------------------------------ guardas
def _runs(pts, keep, step=1.0, closed=True):
    """divide a polilinha em trechos continuos onde keep(p) e verdadeiro"""
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


def _wall(area, run, z0, h, th=1.0, chord=10):
    i = 0
    while i < len(run) - 1:
        j = min(len(run) - 1, i + chord)
        p0, p1 = run[i], run[j]
        mid = (p0 + p1) / 2
        d = p1 - p0
        if d.length > 0.3:
            col_box(area, (d.length + 0.8, th, h), (mid.x, mid.y, z0 + h / 2), (0, 0, math.atan2(d.y, d.x)))
        i = j


def edge_guards():
    """toda borda de piso VISIVEL (o ponto logo para dentro pertence a este piso) cuja queda para fora passa de 2,3 ganha
    parede invisivel; fora de piso = queda. Topo de escada, ponte e ilhota ficam abertos."""
    n_runs = 0
    for nm, poly, z, pr in L.floors():
        pts = ccw(poly)
        n = len(pts)
        seg_normals = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            seg_normals.append((dy / ln, -dx / ln))          # para fora (poligono anti-horario)

        def keep_seg(x, y, nx, ny, nm=nm, z=z):
            if L.floor_name(x - nx * 0.6, y - ny * 0.6) != nm:
                return False                                   # trecho escondido sob um patamar mais alto
            ox, oy = x + nx * 1.6, y + ny * 1.6
            zo = L.zone_of(ox, oy)
            if zo is not None and z - zo <= 2.3:
                return False
            return not opening(ox, oy)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            nx, ny = seg_normals[i]
            seg = [a, b]
            for run in _runs(seg, lambda x, y, nx=nx, ny=ny: keep_seg(x, y, nx, ny), closed=False):
                # a parede fica com a face de dentro na linha da borda
                shifted = [Vector((p.x + nx * 0.5, p.y + ny * 0.5, 0)) for p in run]
                _wall("SG_Guard", shifted, z - 0.5, GUARD_H + 0.5)
                n_runs += 1
    return n_runs


# ------------------------------------------------------------------ chao
def strips(area, poly, z0, z1, step, mode="inter"):
    """colisao de poligono em faixas ao longo de y (como il_lib.col_poly)"""
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        yb = min(y + step, max(ys))
        ya = y
        samples = [ya + 0.05, (ya + yb) / 2, yb - 0.05]
        ivs = None
        for sm in samples:
            iv = SL.x_intervals(poly, sm)
            ivs = iv if ivs is None else (SL.IL._union(ivs, iv) if mode == "union" else SL.IL._inter(ivs, iv))
        for x0, x1 in ivs or []:
            if x1 - x0 > 0.3:
                col_box2(area, (x0, ya, z0), (x1, yb, z1))
                n += 1
        y = yb
    return n


def edge_fill(area, poly, z0, z1, w=3.2):
    """caixas finas por dentro de cada aresta: devolve o piso ate a aresta exata (as faixas 'inter' aparam a borda
    inclinada)"""
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


def floors():
    for nm, poly, z, pr in L.floors():
        if nm == "Summon":
            ngon_col(A, L.SUMMON_C[0], L.SUMMON_C[1], 24, L.SUMMON_R, z - FLOOR_T, z)
            continue
        if len(poly) == 4:                                     # retangulos da entrada: caixa exata
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            col_box2(A, (min(xs), min(ys), z - FLOOR_T), (max(xs), max(ys), z))
            continue
        strips(A, ccw(poly), z - FLOOR_T, z, 6.0, mode="inter")
        edge_fill(A, poly, z - FLOOR_T, z, w=4.6)


def fountain():
    """bacia da fonte da praca: solida ate 2,6 acima do piso (nao da para subir: > 2,3)"""
    cx, cy = L.PLAZA_C
    ngon_col("SG_Fountain", cx, cy, 12, L.FOUNTAIN_R, L.P1 - 1.0, L.P1 + 2.6)


def terrain_col():
    floors()
    for nm, base, ang, w, n, rise, tread, g in stair_list():
        stair_col("SG_Stair" + nm, base, ang, w, n, rise, tread, guards=g)
    bridges()
    fountain()
    edge_guards()
