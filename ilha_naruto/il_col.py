# il_col - COMPARTILHADO E CONGELADO (dono: integracao). Poligonos dos terracos com entalhe das escadas, colisao do
# chao da ilha inteira (fosso, anel, T1, T2, paredao), parede invisivel da borda (aberta nas 2 pontes), guarda-corpos
# (visual + COL) e as pontas das rampas do fosso. Os modulos de detalhe IMPORTAM daqui; nao editar sem a integracao.
import math
from mathutils import Vector
import il_lib as IL
from il_lib import MB, D, col_box, col_box2, col_ramp
import il_layout as L
import fm_parts as FP


def _level(x, y):
    return L.zone_of(x, y)


def stair_notch(u_deg, r_in, depth, hw):
    """pontos do entalhe (sentido horario ao longo do arco r_in) para uma escada radial"""
    a = math.radians(u_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    rin = math.sqrt(max(r_in * r_in - hw * hw, 1.0))
    return [(ux * rin + vx * hw, uy * rin + vy * hw), (ux * depth + vx * hw, uy * depth + vy * hw),
            (ux * depth - vx * hw, uy * depth - vy * hw), (ux * rin - vx * hw, uy * rin - vy * hw)]


RADIAL_STAIRS = [("C", 90.0, 12.0), ("NW", 128.0, 9.0), ("NE", 52.0, 12.0), ("SUMMON", 170.0, 12.0)]


STAIR_TOP_R = 82.5 + 8 * L.TREAD   # 96.1


def t1_poly_notched():
    a0, a1 = L.T1_WALL_A
    p = IL.wedge_clip(IL.rim(), a0, a1)
    p = IL.clip(p, 1.0, 0.0, 108.0)
    # arco r=88 de a1 ate a0 com entalhes nas escadas radiais
    arc = []
    stairs = sorted(RADIAL_STAIRS, key=lambda s: -s[1])
    a_cur = a1
    for _, ang, w in stairs:
        hw = w / 2 + 0.6
        da = math.degrees(math.asin(hw / L.T1_WALL_R))
        arc += IL.arc_pts(L.T1_WALL_R, a_cur, ang + da, 3.0)
        arc += stair_notch(ang, L.T1_WALL_R, STAIR_TOP_R + 0.2, hw)
        a_cur = ang - da
    arc += IL.arc_pts(L.T1_WALL_R, a_cur, a0, 3.0)
    out = []
    for q in p:
        if abs(q[0]) < 1e-6 and abs(q[1]) < 1e-6:
            out.extend(arc)
        else:
            out.append(q)
    return IL.ccw(out)


def t2_poly_notched():
    p = IL.t2_poly()
    ys = L.T2_WALL_Y
    top = L.T2_STAIR_Y0 + 8 * L.TREAD + 0.2
    hw = L.T2_STAIR_W / 2 + 0.6
    out = []
    n = len(p)
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        out.append(a)
        if abs(a[1] - ys) < 1e-6 and abs(b[1] - ys) < 1e-6 and a[0] < -hw < hw < b[0]:
            out += [(-hw, ys), (-hw, top), (hw, top), (hw, ys)]
    return IL.ccw(out)


def t1_arc_fill(A):
    """colisao precisa do T1 junto ao muro em arco (r 88..101): as faixas em y deixam fresta no topo das escadas"""
    a0, a1 = L.T1_WALL_A
    gaps = []
    for _, ang, w in RADIAL_STAIRS:
        gaps.append((ang, math.degrees(math.asin((w / 2 + 0.6) / L.T1_WALL_R))))
    spans = [(a0, a1)]
    for g, da in gaps:
        new = []
        for s0, s1 in spans:
            if g + da <= s0 or g - da >= s1:
                new.append((s0, s1))
                continue
            if g - da > s0:
                new.append((s0, g - da))
            if g + da < s1:
                new.append((g + da, s1))
        spans = new
    for s0, s1 in spans:
        IL.col_annulus(A, L.T1_WALL_R, STAIR_TOP_R + 0.2, s0, s1, L.G - 1.0, L.T1, max(2, int((s1 - s0) / 5.0)))
    IL.col_annulus(A, STAIR_TOP_R, STAIR_TOP_R + 5.0, a0, a1, L.G - 1.0, L.T1, int((a1 - a0) / 5.0))


def corridor(x, y):
    """pontos da borda onde a guarda invisivel fica aberta: ponte de chegada e ponte de saida"""
    if y < -108.0 and abs(x) < L.BRIDGE_W / 2 + 0.5:
        return True
    ux, uy = L.exit_dir()
    sx, sy = L.EXIT_START
    t = (x - sx) * ux + (y - sy) * uy
    d = abs(-(x - sx) * uy + (y - sy) * ux)
    return 0.0 <= t <= L.EXIT_BRIDGE_LEN + 60.0 and d < L.EXIT_W / 2 + 0.5


def rim_guard():
    """parede invisivel na borda da ilha (8 acima do piso local), aberta so onde as pontes encostam"""
    pts = IL.rim()
    n = len(pts)
    for i in range(n):
        a, b = Vector((*pts[i], 0)), Vector((*pts[(i + 1) % n], 0))
        d = b - a
        ns = max(1, int(d.length / 1.0))
        run = []
        runs = []
        for k in range(ns + 1):
            p = a + d * (k / ns)
            if corridor(p.x, p.y):
                if len(run) > 1:
                    runs.append(run)
                run = []
            else:
                run.append(p)
        if len(run) > 1:
            runs.append(run)
        for rr in runs:
            p0, p1 = rr[0], rr[-1]
            mid = (p0 + p1) / 2
            inward = Vector((-mid.x, -mid.y, 0)).normalized() * 3.0
            z = _level(mid.x + inward.x, mid.y + inward.y)
            col_box("Rim", ((p1 - p0).length + 1.0, 1.2, 9.0), (mid.x, mid.y, z + 3.5), (0, 0, math.atan2(d.y, d.x)))


def guard(mb, pts, z, kind="parapet", area="Guard"):
    pts3 = [(p[0], p[1], z) for p in pts]
    if kind == "fence":
        FP.fence(mb, area, pts3, h=3.0, post_step=4.0, m="Wood_Dark", rail_m="Wood_Plank")
    else:
        FP.stone_parapet(mb, area, pts3, h=2.0, w=1.2, m="Stone_Wall_Light", cap_m="Stone_Wall_Dark")


def arc_guard(mb, r, a0, a1, z, kind, gaps=(), step=5.0, area="Guard"):
    """guarda em arco de a0 a a1 (graus), pulando os vaos [(ang, meia_largura_em_studs)]"""
    spans = [(a0, a1)]
    for ang, hw in gaps:
        da = math.degrees(hw / r)
        new = []
        for s0, s1 in spans:
            g0, g1 = ang - da, ang + da
            if g1 <= s0 or g0 >= s1:
                new.append((s0, s1))
                continue
            if g0 > s0:
                new.append((s0, g0))
            if g1 < s1:
                new.append((g1, s1))
        spans = new
    for s0, s1 in spans:
        if s1 - s0 < 0.5:
            continue
        guard(mb, IL.arc_pts(r, s0, s1, step), z, kind, area)


def ramp_ends(side):
    r = L.PIT_R - L.PIT_RAMP_W / 2 - 0.5
    a_top, a_bot = L.PIT_RAMP_A
    if side < 0:
        a_top, a_bot = 180.0 - a_top, 180.0 - a_bot
    top = (r * math.cos(math.radians(a_top)), r * math.sin(math.radians(a_top)))
    bot = (r * math.cos(math.radians(a_bot)), r * math.sin(math.radians(a_bot)))
    return top, bot, a_top


def stream_bed_poly():
    """leito do riacho do vale (da bacia da bica ate alem da borda SE): meia-largura (STREAM_W + 0.6) / 2"""
    pts = list(L.STREAM)
    (x0, y0), (x1, y1) = pts[0], pts[1]
    import math as _m
    d = _m.hypot(x1 - x0, y1 - y0)
    pts.insert(0, (x0 - (x1 - x0) / d * 2.5, y0 - (y1 - y0) / d * 2.5))
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    d = _m.hypot(xb - xa, yb - ya)
    pts.append((xb + (xb - xa) / d * 8.0, yb + (yb - ya) / d * 8.0))
    return IL.ribbon_poly(pts, (L.STREAM_W + 0.6) / 2)


def terrain_col():
    """colisao do chao da ilha inteira (independe do visual: o terreno detalhado usa a mesma).
    Rodada 2: faixas mais largas (teto de colisoes do export) e o LEITO do riacho do vale fora do chao G: no leito a
    colisao fica na lamina d'agua (L.STREAM_WATER), 1,6 abaixo - quem pisa no riacho anda dentro dele."""
    A = "Terrain"
    bed = stream_bed_poly()
    for half in IL.base_halves(L.PIT_R - 0.5):
        IL.col_poly(A, half, L.G - 8.0, L.G, 5.0, mode="inter", minus_polys=(bed,))
    IL.col_poly("TerrainBed", bed, L.STREAM_WATER - 6.0, L.STREAM_WATER, 4.0, mode="union")
    IL.col_poly(A, IL.arc_pts(L.PIT_R, 0, 360, 4.0)[:-1], L.PIT - 6.0, L.PIT, 5.0)
    IL.col_annulus(A, L.RING_R0, L.RING_R1, 0.0, 360.0, L.PIT - 0.5, L.RING, 48)
    IL.col_annulus(A, L.RING_R1 - 0.5, L.T1_WALL_R, L.T1_WALL_A[0], L.T1_WALL_A[1], L.G - 1.0, L.RING, 24)
    IL.col_poly(A, t1_poly_notched(), L.G - 1.0, L.T1, 3.0, mode="inter")
    t1_arc_fill(A)
    IL.col_poly(A, t2_poly_notched(), L.T1 - 1.0, L.T2, 3.0, mode="inter")
    top = L.T2_STAIR_Y0 + 8 * L.TREAD
    col_box2(A, (-L.T2_STAIR_W / 2 - 1.0, top - 0.2, L.T1), (L.T2_STAIR_W / 2 + 1.0, top + 2.4, L.T2))
    IL.col_poly(A, IL.cliff_poly(), L.T2 - 1.0, L.CLIFF_TOP, 6.0)
    rim_guard()
