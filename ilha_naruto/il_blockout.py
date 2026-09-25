# il_blockout - PASS 2: massas simples da Ilha 1 (terreno em niveis, fosso, entrada, vila, summon, leste, saida,
# portao Dragon Ball) + colisao COL_ real + marcadores de gameplay. Materiais ja na paleta (sem detalhe).
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, D, col_box, col_box2, col_ramp, mk
import il_layout as L
import fm_parts as FP


def _level(x, y):
    return L.zone_of(x, y)


# ------------------------------------------------------------------ poligonos com entalhe das escadas
def stair_notch(u_deg, r_in, depth, hw):
    """pontos do entalhe (sentido horario ao longo do arco r_in) para uma escada radial"""
    a = math.radians(u_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    rin = math.sqrt(max(r_in * r_in - hw * hw, 1.0))
    return [(ux * rin + vx * hw, uy * rin + vy * hw), (ux * depth + vx * hw, uy * depth + vy * hw),
            (ux * depth - vx * hw, uy * depth - vy * hw), (ux * rin - vx * hw, uy * rin - vy * hw)]


RADIAL_STAIRS = [("C", 90.0, 12.0), ("NW", 128.0, 9.0), ("NE", 52.0, 9.0), ("SUMMON", 170.0, 12.0)]
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


# ------------------------------------------------------------------ terreno
def terrain():
    rng = random.Random(11)
    sh = MB("TER_Cliff_Shelf", "02_TERRAIN", rng, detail="far")
    IL.prism(sh, IL.ccw(L.SHELF_RIM), L.SEA, L.SHELF_Z, "Cliff_Rock_Tan", "Grass_Konoha")
    sh.finish()
    tb = MB("TER_Island_Base", "02_TERRAIN", rng, detail="far")
    for half in IL.base_halves(L.PIT_R):
        IL.prism(tb, half, L.SEA, L.G, "Cliff_Rock_Tan", "Grass_Konoha")
    tb.finish()
    # piso do fosso
    pf = MB("TER_Pit_Floor", "03_MINING", rng, detail="far")
    IL.prism(pf, IL.arc_pts(L.PIT_R + 0.3, 0, 360, 4.0)[:-1], L.G - 14.0, L.PIT, "Stone_Wall_Dark", "Dirt_Pit")
    pf.finish()
    # anel (r 60..82) + faixa do anel ao pe do T1 (r 82..88, setor do T1)
    rg = MB("TER_Ring", "03_MINING", rng, detail="far")
    IL.annulus(rg, L.RING_R0, L.RING_R1, 0.0, 360.0, L.PIT - 0.4, L.RING, "Stone_Wall_Light", 3.0,
               top_m="Stone_Paving_Warm")
    IL.annulus(rg, L.RING_R1 - 0.2, L.T1_WALL_R + 0.3, L.T1_WALL_A[0], L.T1_WALL_A[1], L.G - 1.0, L.RING,
               "Stone_Wall_Light", 3.0, top_m="Stone_Paving_Warm")
    rg.finish()
    t1 = MB("TER_Terrace_T1", "02_TERRAIN", rng, detail="far")
    IL.prism(t1, t1_poly_notched(), L.G - 2.0, L.T1, "Stone_Wall_Light", "Grass_Konoha")
    t1.finish()
    t2 = MB("TER_Terrace_T2", "02_TERRAIN", rng, detail="far")
    IL.prism(t2, t2_poly_notched(), L.T1 - 2.0, L.T2, "Stone_Wall_Light", "Grass_Konoha")
    t2.finish()
    cl = MB("TER_Back_Cliff", "02_TERRAIN", rng, detail="far")
    IL.prism(cl, IL.cliff_poly(), L.T2 - 2.0, L.CLIFF_TOP, "Cliff_Rock_Tan", "Grass_Konoha")
    cl.finish()

    # colisao do terreno
    A = "Terrain"
    for half in IL.base_halves(L.PIT_R - 0.5):
        IL.col_poly(A, half, L.G - 8.0, L.G, 3.0)
    IL.col_poly(A, IL.arc_pts(L.PIT_R, 0, 360, 4.0)[:-1], L.PIT - 6.0, L.PIT, 3.0)
    IL.col_annulus(A, L.RING_R0, L.RING_R1, 0.0, 360.0, L.PIT - 0.5, L.RING, 72)
    IL.col_annulus(A, L.RING_R1 - 0.5, L.T1_WALL_R, L.T1_WALL_A[0], L.T1_WALL_A[1], L.G - 1.0, L.RING, 36)
    IL.col_poly(A, t1_poly_notched(), L.G - 1.0, L.T1, 2.0, mode="inter")
    t1_arc_fill(A)
    IL.col_poly(A, t2_poly_notched(), L.T1 - 1.0, L.T2, 2.0, mode="inter")
    top = L.T2_STAIR_Y0 + 8 * L.TREAD
    col_box2(A, (-L.T2_STAIR_W / 2 - 1.0, top - 0.2, L.T1), (L.T2_STAIR_W / 2 + 1.0, top + 2.4, L.T2))
    IL.col_poly(A, IL.cliff_poly(), L.T2 - 1.0, L.CLIFF_TOP, 4.0)
    rim_guard()


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
        IL.col_annulus(A, L.T1_WALL_R, STAIR_TOP_R + 0.2, s0, s1, L.G - 1.0, L.T1, max(2, int((s1 - s0) / 3.0)))
    IL.col_annulus(A, STAIR_TOP_R, STAIR_TOP_R + 5.0, a0, a1, L.G - 1.0, L.T1, int((a1 - a0) / 3.0))


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


# ------------------------------------------------------------------ guarda-corpos (visual + COL)
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


# ------------------------------------------------------------------ fosso, anel, escadas, rampas
def ramp_ends(side):
    r = L.PIT_R - L.PIT_RAMP_W / 2 - 0.5
    a_top, a_bot = L.PIT_RAMP_A
    if side < 0:
        a_top, a_bot = 180.0 - a_top, 180.0 - a_bot
    top = (r * math.cos(math.radians(a_top)), r * math.sin(math.radians(a_top)))
    bot = (r * math.cos(math.radians(a_bot)), r * math.sin(math.radians(a_bot)))
    return top, bot, a_top


def mining():
    rng = random.Random(21)
    mb = MB("MINE_Blockout", "03_MINING", rng, detail="near")
    n = L.PIT_STAIR_N
    rise = (L.RING - L.PIT) / n
    tread = 1.6
    # escadas S e N (descem para dentro do fosso, radiais)
    for ang in (-90.0, 90.0):
        a = math.radians(ang)
        base = (math.cos(a) * (L.PIT_R - n * tread), math.sin(a) * (L.PIT_R - n * tread), L.PIT)
        FP.stairs(mb, "PitStairs", base, a, L.PIT_STAIR_W, n, rise, tread, "Stone_Wall_Light", "Stone_Wall_Dark")
    # rampas de madeira L e O (cordas junto ao muro)
    for side in (1, -1):
        top, bot, a_top = ramp_ends(side)
        at = Vector((top[0], top[1], L.RING))
        ab = Vector((bot[0], bot[1], L.PIT))
        d = ab - at
        mb.beam(at + Vector((0, 0, -0.35)), ab + Vector((0, 0, -0.35)), L.PIT_RAMP_W, 0.7, "Wood_Plank", 0.05)
        col_ramp("PitRamps", ab, at, L.PIT_RAMP_W, 1.0)
        # patamar no topo (liga a rampa a borda do anel)
        rim = Vector((L.PIT_R * math.cos(math.radians(a_top)), L.PIT_R * math.sin(math.radians(a_top)), L.RING))
        mb.beam(at + Vector((0, 0, -0.35)), rim + Vector((0, 0, -0.35)), L.PIT_RAMP_W, 0.7, "Wood_Plank", 0.05)
        col_box("PitRamps", ((rim - at).length + 1.0, L.PIT_RAMP_W, 1.0), ((at + rim) / 2 + Vector((0, 0, -0.5))),
                (0, 0, math.atan2(rim.y - at.y, rim.x - at.x)))
        # guarda-corpos das rampas
        side_v = Vector((-d.y, d.x, 0)).normalized() * (L.PIT_RAMP_W / 2 + 0.3)
        dn = d.normalized()
        for s in (-1, 1):
            a3 = at + side_v * s + dn * 4.5          # topo aberto: sai de lado para a borda do anel
            b3 = ab + side_v * s - dn * 2.0          # a guarda para 2 studs antes do pe (pe livre)
            mb.beam(a3 + Vector((0, 0, 2.6)), b3 + Vector((0, 0, 2.6)), 0.35, 0.35, "Wood_Dark", 0.03)
            for k in range(6):
                p = a3 + (b3 - a3) * (k / 5)
                mb.box((0.5, 0.5, 2.8), p + Vector((0, 0, 1.4)), (0, 0, 0), "Wood_Dark", 0.03)
            col_beam_ramp(a3, b3)
        # suporte: pilares sob a rampa
        for k in range(1, 4):
            p = at + d * (k / 4)
            h = p.z - L.PIT
            mb.box((0.8, 0.8, h), (p.x, p.y, L.PIT + h / 2), (0, 0, 0), "Wood_Dark", 0.03)
    # cerca da borda do fosso (vaos: escadas N/S e topo das rampas)
    gaps = [(90.0, L.PIT_STAIR_W / 2 + 0.8), (270.0, L.PIT_STAIR_W / 2 + 0.8)]
    for side in (1, -1):
        _, _, a_top = ramp_ends(side)
        gaps.append((a_top % 360.0, L.PIT_RAMP_W / 2 + 1.0))
    arc_guard(mb, L.FENCE_R, 0.0, 360.0, L.RING, "fence", gaps, step=4.0, area="PitFence")
    # lanternas do anel (borda externa), sem luz no blockout
    for i in range(16):
        a = math.radians(11.25 + i * 22.5)
        x, y = 79.5 * math.cos(a), 79.5 * math.sin(a)
        mb.box((1.6, 1.6, 1.0), (x, y, L.RING + 0.5), (0, 0, a), "Stone_Wall_Dark", 0.1)
        mb.box((0.9, 0.9, 3.4), (x, y, L.RING + 2.7), (0, 0, a), "Stone_Wall_Light", 0.05)
        mb.box((1.6, 1.6, 1.4), (x, y, L.RING + 5.1), (0, 0, a), "Lantern_Glow", 0.0)
        mb.box((2.2, 2.2, 0.5), (x, y, L.RING + 6.05), (0, 0, a), "Stone_Wall_Dark", 0.05)
    # torres de madeira (derricks) na borda interna do fosso
    for ang in L.DERRICKS:
        a = math.radians(ang)
        cx, cy = L.DERRICK_R * math.cos(a), L.DERRICK_R * math.sin(a)
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.box((0.8, 0.8, 13.0), (cx + sx * 2.4, cy + sy * 2.4, L.PIT + 6.5), (0, 0, 0), "Wood_Dark", 0.05)
        mb.box((6.4, 6.4, 0.6), (cx, cy, L.PIT + 9.0), (0, 0, 0), "Wood_Plank", 0.05)
        mb.box((7.0, 7.0, 0.8), (cx, cy, L.PIT + 13.2), (0, 0, 0), "Roof_Blue", 0.05)
        col_box("Derricks", (6.0, 6.0, 13.5), (cx, cy, L.PIT + 6.75))
    mb.finish()
    # rochedo central + cristais
    cr = MB("MINE_Core_Blockout", "03_MINING", rng)
    for k in range(9):
        a = rng.uniform(0, 6.28)
        r = rng.uniform(0, 6.0)
        s = rng.uniform(4.5, 7.5)
        cr.rock((r * math.cos(a), r * math.sin(a), L.PIT + s * 0.35), (s, s * 0.9, s * 0.9), "Cliff_Rock_Tan_Dark", 1)
    for k in range(7):
        a = rng.uniform(0, 6.28)
        r = rng.uniform(0, 4.0)
        h = rng.uniform(6.0, 13.0)
        cr.cyl(1.4, h, (r * math.cos(a), r * math.sin(a), L.PIT + 4.0 + h / 2),
               (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0), "Crystal_Blue", 6, r2=0.2, bevel=0.0)
    cr.finish()
    col_box("Core", (L.CORE_R * 1.6, L.CORE_R * 1.6, 8.0), (0, 0, L.PIT + 4.0))
    # minerio: marcador + pedra de marcacao colorida por raridade (so blockout)
    tint = {"COMMON": "Stone_Wall_Dark", "UNCOMMON": "Grass_Konoha", "EPIC": "Crystal_Purple",
            "SUPERLEGENDARY": "Metal_Gold"}
    om = MB("MINE_Ore_Placeholders", "03_MINING", rng)
    for kind, i, x, y, r in L.ore_points():
        om.rock((x, y, L.PIT + r * 0.3), (r * 1.2, r * 1.2, r * 0.9), tint[kind], 1, jitter=0.2)
        mk("ORE_%s_%02d" % (kind, i), (x, y, L.PIT), size=r, kind="SPHERE",
           props={"rarity": kind, "radius": r})
    om.finish()
    mk("GP_Zone_Pit", (0, 0, L.PIT), size=L.PIT_R - 4.0, kind="CIRCLE",
       props={"radius": L.PIT_R - 4.0, "floor": L.PIT, "kind": "mining"})


def col_beam_ramp(a, b):
    d = b - a
    c = (a + b) / 2 + Vector((0, 0, 2.2))
    yaw = math.atan2(d.y, d.x)
    pitch = math.atan2(d.z, math.hypot(d.x, d.y))
    col_box("PitRamps", (d.length, 0.6, 4.4), c, (0, -pitch, yaw))


# ------------------------------------------------------------------ guardas dos terracos e do anel
def terrace_guards():
    rng = random.Random(31)
    mb = MB("TER_Guards_Blockout", "02_TERRAIN", rng, detail="near")
    # borda externa do anel onde fora e G (setor 200 -> 386 graus), vaos: escada da entrada, escada do moinho
    arc_guard(mb, L.RING_R1 - 0.7, L.T1_WALL_A[1], 360.0 + L.T1_WALL_A[0], L.RING, "parapet",
              [(270.0, L.ENTRY_STAIR_W / 2 + 0.8), (360.0 + math.degrees(math.atan2(L.MILL_STAIR[1], 82.0)), 5.2)],
              step=4.0)
    # topo do muro T1 (arco r 88), vaos nas escadas radiais
    arc_guard(mb, L.T1_WALL_R + 0.8, L.T1_WALL_A[0], L.T1_WALL_A[1], L.T1, "parapet",
              [(ang, w / 2 + 0.8) for _, ang, w in RADIAL_STAIRS], step=4.0)
    # topo do muro T2 (y 126), vao da escada central
    hw = L.T2_STAIR_W / 2 + 0.8
    guard(mb, [(-L.T2_WALL_X[1] - 36, L.T2_WALL_Y + 0.8), (-hw, L.T2_WALL_Y + 0.8)], L.T2)
    guard(mb, [(hw, L.T2_WALL_Y + 0.8), (107.0, L.T2_WALL_Y + 0.8)], L.T2)
    # T1 -> vale leste (x = 108) e raios 26/200 graus (quedas de 10)
    ex = L.EXIT_START
    y_bridge = ex[1] + (108.0 - ex[0])            # a ponte cruza x=108 em y ~108
    guard(mb, [(107.2, 52.0), (107.2, y_bridge - 10.0)], L.T1)
    guard(mb, [(107.2, y_bridge + 10.0), (107.2, L.T2_WALL_Y)], L.T1)
    for ang in L.T1_WALL_A:
        a = math.radians(ang)
        p0 = (L.T1_WALL_R * math.cos(a), L.T1_WALL_R * math.sin(a))
        p1 = ((L.T1_WALL_R + 70) * math.cos(a), (L.T1_WALL_R + 70) * math.sin(a))
        if ang < 90:
            t = (107.2 - p0[0]) / (p1[0] - p0[0])
            p1 = (107.2, p0[1] + (p1[1] - p0[1]) * t)
        guard(mb, [p0, p1], L.T1)
    mb.finish()


# ------------------------------------------------------------------ escadas da vila / summon / moinho / entrada
def stairs_all():
    rng = random.Random(41)
    mb = MB("TER_Stairs_Blockout", "02_TERRAIN", rng, detail="near")
    n1 = 8
    r1 = (L.T1 - L.RING) / n1
    for key, ang, w in RADIAL_STAIRS:
        a = math.radians(ang)
        base = (82.5 * math.cos(a), 82.5 * math.sin(a), L.RING)
        FP.stairs(mb, "Stairs", base, a, w, n1, r1, L.TREAD, "Stone_Wall_Light", "Stone_Wall_Dark")
    FP.stairs(mb, "Stairs", (0.0, L.T2_STAIR_Y0, L.T1), math.radians(90), L.T2_STAIR_W, 8, (L.T2 - L.T1) / 8,
              L.TREAD, "Stone_Wall_Light", "Stone_Wall_Dark")
    ne = L.ENTRY_STAIR_N
    FP.stairs(mb, "Stairs", (0.0, -82.5 - ne * L.TREAD, L.G), math.radians(90), L.ENTRY_STAIR_W, ne,
              (L.RING - L.G) / ne, L.TREAD, "Stone_Wall_Light", "Stone_Wall_Dark")
    x0 = math.sqrt(82.0 ** 2 - L.MILL_STAIR[1] ** 2) - 0.4
    FP.stairs(mb, "Stairs", (x0 + ne * L.TREAD, L.MILL_STAIR[1], L.G), math.radians(180), 8.0, ne,
              (L.RING - L.G) / ne, L.TREAD, "Stone_Wall_Light", "Stone_Wall_Dark")
    mb.finish()


# ------------------------------------------------------------------ entrada: ponte, portao, leoes, praca
def entrance():
    rng = random.Random(51)
    br = MB("ENT_Bridge_Blockout", "02_TERRAIN", rng, detail="near")
    hw = L.BRIDGE_W / 2
    br.box2((-hw, L.LOBBY_Y, L.G - 2.0), (hw, L.ISLAND_S_Y + 1.0, L.G), "Stone_Paving_Warm", 0.1)
    for s in (-1, 1):
        FP.fence(br, "Bridge", [(s * (hw - 0.6), L.LOBBY_Y + 0.5, L.G), (s * (hw - 0.6), L.ISLAND_S_Y, L.G)],
                 h=3.0, post_step=6.0, m="Wood_Dark", rail_m="Wood_Plank")
    for y in (L.LOBBY_Y + 20, L.LOBBY_Y + 50):
        for s in (-1, 1):
            br.box((3.0, 3.0, 60.0), (s * (hw - 3), y, L.G - 32.0), (0, 0, 0), "Stone_Wall_Dark", 0.1)
    br.finish()
    col_box2("Bridge", (-hw, L.LOBBY_Y - 0.5, L.G - 3.0), (hw, L.ISLAND_S_Y + 2.0, L.G))
    # praca do portao (calcamento)
    pz = MB("ENT_Plaza_Blockout", "02_TERRAIN", rng, detail="far")
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    pz.box2((x0, L.ISLAND_S_Y, L.G - 0.3), (x1, y1 + 0.5, L.G + 0.05), "Stone_Paving_Warm", 0.0)
    pz.finish()
    # portao principal: 4 pilares vermelhos, verga, telhado verde, alas laterais creme
    gt = MB("ENT_Gate_Blockout", "02_TERRAIN", rng)
    gy = L.GATE_Y
    ow = L.GATE_OPEN_W / 2
    for x in (-ow - 1.2, ow + 1.2, -L.GATE_W / 2 + 1.5, L.GATE_W / 2 - 1.5):
        h = 20.0 if abs(x) < ow + 3 else 14.0
        gt.box((2.4, 2.4, h), (x, gy, L.G + h / 2), (0, 0, 0), "Wood_Lacquer_Red", 0.1)
        col_box("Gate", (2.4, 2.4, h), (x, gy, L.G + h / 2))
    gt.box((L.GATE_OPEN_W + 6.0, 3.0, 2.2), (0, gy, L.G + L.GATE_OPEN_H + 1.1), (0, 0, 0), "Wood_Lacquer_Red", 0.1)
    gt.box((L.GATE_OPEN_W + 12.0, 10.0, 1.4), (0, gy, L.G + L.GATE_OPEN_H + 3.2), (0, 0, 0), "Roof_Green", 0.1)
    gt.box((L.GATE_OPEN_W + 4.0, 7.0, 2.0), (0, gy, L.G + L.GATE_OPEN_H + 4.8), (0, 0, 0), "Roof_Green", 0.1)
    for s in (-1, 1):
        cx = s * (ow + 1.2 + (L.GATE_W / 2 - 1.5 - ow - 1.2) / 2)
        wdt = (L.GATE_W / 2 - 1.5) - (ow + 1.2) - 2.4
        gt.box((wdt, 1.4, 12.0), (cx, gy, L.G + 6.0), (0, 0, 0), "Plaster_Cream", 0.05)
        gt.box((wdt + 4.0, 7.0, 1.0), (cx, gy, L.G + 14.4), (0, 0, 0), "Roof_Green", 0.05)
        col_box("Gate", (wdt, 1.6, 12.0), (cx, gy, L.G + 6.0))
    # leoes nos pedestais
    for lx, ly in L.LIONS:
        gt.box((5.0, 5.0, 4.0), (lx, ly, L.G + 2.0), (0, 0, 0), "Stone_Wall_Light", 0.15)
        gt.box((3.0, 4.0, 5.0), (lx, ly, L.G + 6.5), (0, 0, 0), "Stone_Wall_Dark", 0.3)
        col_box("Gate", (5.0, 5.0, 9.0), (lx, ly, L.G + 4.5))
    gt.finish()


# ------------------------------------------------------------------ vila
def round_building(name, x, y, r, z, h, roof_m, tiers=1, door=True, coll="04_VILLAGE"):
    rng = random.Random(len(name))
    mb = MB(name, coll, rng)
    mb.cyl(r, h, (x, y, z + h / 2), (0, 0, 0), "Plaster_Cream", 24, bevel=0.0)
    mb.cyl(r + 3.5, 5.0, (x, y, z + h + 2.5), (0, 0, 0), roof_m, 24, r2=r * 0.35, bevel=0.0)
    if tiers > 1:
        r2 = r * 0.62
        mb.cyl(r2, h * 0.6, (x, y, z + h + 3.0 + h * 0.3), (0, 0, 0), "Plaster_Cream", 20, bevel=0.0)
        mb.cyl(r2 + 3.0, 4.5, (x, y, z + h + 3.0 + h * 0.6 + 2.25), (0, 0, 0), roof_m, 20, r2=2.0, bevel=0.0)
    if door:
        mb.box((6.0, 1.0, 8.0), (x, y - r - 0.3, z + 4.0), (0, 0, 0), "Wood_Dark", 0.05)
    mb.finish()
    col_box("Village", (r * 1.5, r * 1.5, h), (x, y, z + h / 2))
    col_box("Village", (r * 1.9, r * 0.8, h), (x, y, z + h / 2))
    col_box("Village", (r * 0.8, r * 1.9, h), (x, y, z + h / 2))


def square_house(name, x, y, w, d, z, roof_m, door=False, yaw=0.0, h=8.0, coll="04_VILLAGE"):
    rng = random.Random(len(name) * 7)
    mb = MB(name, coll, rng)
    mb.box((w, d, h), (x, y, z + h / 2), (0, 0, yaw), "Plaster_Cream", 0.1)
    mb.box((w + 0.6, d + 0.6, 1.2), (x, y, z + 0.6), (0, 0, yaw), "Stone_Wall_Dark", 0.1)
    # telhado de quatro aguas (piramide truncada)
    mb.cyl(math.hypot(w, d) / 2 + 2.0, 4.5, (x, y, z + h + 2.25), (0, 0, yaw + math.pi / 4), roof_m, 4, r2=1.2,
           bevel=0.0)
    if door:
        mb.box((5.5, 0.6, 7.0), (x, y - d / 2 - 0.2, z + 3.5), (0, 0, yaw), "Wood_Dark", 0.05)
    mb.finish()
    col_box("Village", (w, d, h), (x, y, z + h / 2), (0, 0, yaw))


def village():
    x, y, r = L.MAIN_HALL
    round_building("VIL_MainHall_Blockout", x, y, r, L.T2, 15.0, "Roof_Terracotta", tiers=2, door=True)
    x, y, r = L.BLUE_W
    round_building("VIL_WeaponShop_Blockout", x, y, r, L.T2, 11.0, "Roof_Blue", tiers=2, door=True)
    x, y, r = L.BLUE_E
    round_building("VIL_WaterTower_Blockout", x, y, r, L.T2, 11.0, "Roof_Blue", tiers=2, door=False)
    x, y, w, d, yaw = L.RAMEN
    square_house("VIL_Ramen_Blockout", x, y, w, d, L.T1, "Roof_Green", door=True, h=9.0)
    for i, (hx, hy, w, d, yaw, roof) in enumerate(L.HOUSES_T1):
        z = L.zone_of(hx, hy)
        square_house("VIL_House_T1_%d_Blockout" % i, hx, hy, w, d, z, roof, h=10.0)
    for i, (hx, hy, w, d, yaw, roof) in enumerate(L.HOUSES_T2):
        square_house("VIL_House_T2_%d_Blockout" % i, hx, hy, w, d, L.T2, roof, h=10.0)
    # casinhas no plato de cima (silhueta)
    rng = random.Random(77)
    for i, hx in enumerate((-78.0, -40.0, 0.0, 40.0, 80.0)):
        square_house("VIL_Upper_%d_Blockout" % i, hx, 196.0 + rng.uniform(-3, 3), 12.0, 10.0, L.CLIFF_TOP,
                     ("Roof_Terracotta", "Roof_Green", "Roof_Blue", "Roof_Terracotta", "Roof_Green")[i], h=8.0)
    # estandartes da escadaria central (edificio importante)
    bn = MB("VIL_Banners_Blockout", "04_VILLAGE", rng)
    for s in (-1, 1):
        bn.box((0.6, 0.6, 12.0), (s * 8.5, 99.0, L.T1 + 6.0), (0, 0, 0), "Wood_Dark", 0.05)
        bn.box((3.6, 0.3, 7.0), (s * 8.5, 98.6, L.T1 + 7.5), (0, 0, 0), "Cloth_Red", 0.0)
    bn.finish()


# ------------------------------------------------------------------ summon
def summon():
    rng = random.Random(61)
    cx, cy = L.SUMMON_C
    pl = MB("SUM_Plaza_Blockout", "05_SUMMON", rng, detail="far")
    pl.cyl(L.SUMMON_R, 0.4, (cx, cy, L.T1 + 0.2), (0, 0, 0), "Summon_Floor", 40, bevel=0.0)
    pl.cyl(L.SUMMON_R * 0.45, 0.2, (cx, cy, L.T1 + 0.45), (0, 0, 0), "Metal_Gold", 5, bevel=0.0)
    pl.finish()
    tx, ty = L.SUMMON_TOWER
    yaw = math.radians(L.SUMMON_FACE_DEG) - math.pi / 2
    tw = MB("SUM_Tower_Blockout", "05_SUMMON", rng)
    z = L.T1
    tw.box((28.0, 22.0, 6.0), (tx, ty, z + 3.0), (0, 0, yaw), "Summon_Stone_Dark", 0.2)
    tw.box((17.0, 15.0, 26.0), (tx, ty, z + 6.0 + 13.0), (0, 0, yaw), "Summon_Stone", 0.2)
    tw.box((19.0, 17.0, 2.4), (tx, ty, z + 33.0), (0, 0, yaw), "Metal_Gold", 0.1)
    tw.box((13.0, 12.0, 9.0), (tx, ty, z + 38.5), (0, 0, yaw), "Summon_Stone", 0.2)
    tw.ico(8.0, (tx, ty, z + 52.0), "Summon_Star_Glow", 1)
    for k, (rx, ry) in enumerate(((0.3, 0.0), (1.2, 0.5), (-0.6, 1.1))):
        tw.cyl(12.5, 0.7, (tx, ty, z + 52.0), (rx, ry, 0), "Metal_Gold", 32, bevel=0.0, caps=False)
    for sx in (-1, 1):
        px = tx + math.cos(yaw) * sx * 15.0
        py = ty + math.sin(yaw) * sx * 15.0
        tw.box((4.0, 4.0, 9.0), (px, py, z + 4.5), (0, 0, yaw), "Summon_Stone_Dark", 0.1)
        tw.ico(2.2, (px, py, z + 11.2), "Summon_Blue_Glow", 1)
        tw.box((5.0, 0.3, 14.0), (tx + math.cos(yaw) * sx * 10.5, ty + math.sin(yaw) * sx * 10.5, z + 24.0),
               (0, 0, yaw), "Cloth_Royal_Blue", 0.0)
    tw.finish()
    col_box("Summon", (28.0, 22.0, 6.0), (tx, ty, z + 3.0), (0, 0, yaw))
    col_box("Summon", (17.0, 15.0, 36.0), (tx, ty, z + 24.0), (0, 0, yaw))
    # balaustrada da praca (aberta para a escada do anel e para a torre)
    gm = MB("SUM_Rail_Blockout", "05_SUMMON", rng, detail="near")
    stair_ang = math.degrees(math.atan2(16.7 - cy, -94.6 - cx))
    tow_ang = math.degrees(math.atan2(ty - cy, tx - cx))
    a0 = tow_ang + 32.0
    a1 = tow_ang + 360.0 - 32.0
    spans = []
    # vao da escada
    sa = stair_ang % 360.0
    while sa < a0:
        sa += 360.0
    spans = [(a0, sa - 14.0), (sa + 14.0, a1)]
    for s0, s1 in spans:
        if s1 > s0:
            guard(gm, IL.arc_pts(L.SUMMON_R - 0.8, s0, s1, 6.0, cx, cy), L.T1 + 0.4, "parapet", "Summon")
    gm.finish()
    f = (math.cos(math.radians(L.SUMMON_FACE_DEG)), math.sin(math.radians(L.SUMMON_FACE_DEG)))
    mk("SUMMON_Main", (tx, ty, L.T1), (0, 0, yaw), 4.0, "ARROWS")
    mk("SUMMON_Interact", (tx + f[0] * 13.0, ty + f[1] * 13.0, L.T1 + 0.4), (0, 0, yaw), 2.0, "SPHERE")
    mk("SUMMON_PlayerPosition", (tx + f[0] * 18.0, ty + f[1] * 18.0, L.T1 + 0.4), (0, 0, yaw + math.pi), 2.0,
       "ARROWS")


# ------------------------------------------------------------------ leste: riacho, roda, moinho, ponte em arco, casas
def east():
    rng = random.Random(71)
    wt = MB("WATER_Blockout", "06_WATER", rng, detail="far")
    pts = L.STREAM
    for a, b in zip(pts, pts[1:]):
        za = (L.T2 if a[1] >= L.T2_WALL_Y else L.G) + 0.15
        zb = (L.T2 if b[1] >= L.T2_WALL_Y else L.G) + 0.15
        A, B = Vector((*a, max(za, zb))), Vector((*b, max(za, zb)))
        if za != zb:
            # cascata T2 -> G no muro y 126
            mid = Vector((a[0] + (b[0] - a[0]) * (a[1] - L.T2_WALL_Y) / (a[1] - b[1]), L.T2_WALL_Y, 0))
            wt.beam(Vector((a[0], a[1], za)), Vector((mid.x, mid.y + 0.5, za)), L.STREAM_W, 0.2, "Water", 0.0)
            wt.box((L.STREAM_W, 0.6, za - zb), (mid.x, mid.y - 0.3, (za + zb) / 2), (0, 0, 0), "Water_Fall", 0.0)
            wt.beam(Vector((mid.x, mid.y - 0.5, zb)), Vector((b[0], b[1], zb)), L.STREAM_W, 0.2, "Water", 0.0)
            continue
        wt.beam(A, B, L.STREAM_W, 0.2, "Water", 0.0)
    # quedas no fundo (paredao) e na borda
    for fx, fy in L.BACK_FALLS:
        wt.box((10.0, 1.0, L.CLIFF_TOP - L.T2), (fx, fy - 0.5, (L.CLIFF_TOP + L.T2) / 2), (0, 0, 0), "Water_Fall", 0.0)
        wt.cyl(9.0, 0.3, (fx, fy - 8.0, L.T2 + 0.1), (0, 0, 0), "Water", 16, bevel=0.0)
    ex, ey = L.STREAM[-1]
    wt.box((10.0, 1.0, 110.0), (ex + 2.0, ey - 2.0, L.G - 55.0), (0, 0, math.radians(-30)), "Water_Fall", 0.0)
    # oeste: poco NO -> canal -> queda sob o summon
    wt.beam(Vector((-84.0, 176.0, L.T2 + 0.15)), Vector((-120.0, 150.0, L.T2 + 0.15)), 7.0, 0.2, "Water", 0.0)
    wt.box((7.0, 0.6, L.T2 - L.T1), (-130.0, 140.0, (L.T1 + L.T2) / 2), (0, 0, math.radians(35)), "Water_Fall", 0.0)
    wt.beam(Vector((-134.0, 136.0, L.T1 + 0.15)), Vector((-160.0, 80.0, L.T1 + 0.15)), 7.0, 0.2, "Water", 0.0)
    wt.box((8.0, 1.0, 120.0), (-164.5, 74.0, L.T1 - 60.0), (0, 0, math.radians(70)), "Water_Fall", 0.0)
    # sudoeste: galeria de drenagem do fosso na face do penhasco
    wt.box((6.0, 1.0, 100.0), (-112.0, -90.0, L.G - 54.0), (0, 0, math.radians(-40)), "Water_Fall", 0.0)
    wt.finish()
    # roda d'agua e moinho
    mm = MB("MINE_Mill_Blockout", "03_MINING", rng)
    wx, wy, wr = L.WHEEL
    mm.cyl(wr, 3.0, (wx, wy, L.G + wr - 3.0), (0, math.pi / 2, 0), "Wood_Plank", 16, bevel=0.0)
    mx, my, mw, md = L.MILL
    mm.box((mw, md, 10.0), (mx, my, L.G + 5.0), (0, 0, 0), "Plaster_Cream", 0.1)
    mm.cyl(math.hypot(mw, md) / 2 + 2.0, 5.0, (mx, my, L.G + 12.5), (0, 0, math.pi / 4), "Roof_Terracotta", 4,
           r2=1.0, bevel=0.0)
    mm.box((0.6, 6.0, 7.5), (mx - mw / 2 - 0.2, my, L.G + 3.75), (0, 0, 0), "Wood_Dark", 0.05)
    mm.finish()
    col_box("Mill", (mw, md, 10.0), (mx, my, L.G + 5.0))
    col_box("Mill", (3.0, wr * 2, wr * 2), (wx, wy, L.G + wr - 3.0))
    # ponte em arco sobre o riacho
    fb = MB("PROP_Footbridge_Blockout", "09_PROPS", rng)
    fx, fy = L.FOOTBRIDGE
    fb.box((L.STREAM_W + 8.0, 4.0, 0.6), (fx, fy, L.G + 1.4), (0, 0, 0), "Wood_Plank", 0.05)
    fb.finish()
    col_box2("Footbridge", (fx - L.STREAM_W / 2 - 4.0, fy - 2.0, L.G + 0.7), (fx + L.STREAM_W / 2 + 4.0, fy + 2.0, L.G + 1.7))
    for i, (hx, hy, w, d, yaw, roof) in enumerate(L.EAST_HOUSES):
        square_house("VIL_House_E_%d_Blockout" % i, hx, hy, w, d, L.G, roof)


# ------------------------------------------------------------------ saida: ponte, ilhota, portao DB, ancora
def exit_and_gate():
    rng = random.Random(81)
    ux, uy = L.exit_dir()
    yaw = math.radians(L.EXIT_DEG) - math.pi / 2         # +Y local do portao aponta para a saida
    s0 = Vector((*L.EXIT_START, L.EXIT_Z))
    s1 = Vector((*L.exit_point(L.EXIT_BRIDGE_LEN), L.EXIT_Z))
    br = MB("EXIT_Bridge_Blockout", "07_NEXT_ISLAND", rng, detail="near")
    br.beam(s0 + Vector((0, 0, -1.0)), s1 + Vector((0, 0, -1.0)), 2.0, L.EXIT_W, "Stone_Paving_Warm", 0.05,
            roll=math.pi / 2)
    d = s1 - s0
    side = Vector((-d.y, d.x, 0)).normalized()
    for k in range(1, 5):
        p = s0 + d * (k / 5)
        for s in (-1, 1):
            q = p + side * s * (L.EXIT_W / 2 - 2.0)
            br.box((3.0, 3.0, 60.0), (q.x, q.y, L.EXIT_Z - 32.0), (0, 0, 0), "Stone_Wall_Dark", 0.1)
    for s in (-1, 1):
        a = s0 + side * s * (L.EXIT_W / 2 - 0.6)
        b = s1 + side * s * (L.EXIT_W / 2 - 0.6)
        FP.fence(br, "ExitBridge", [(a.x, a.y, L.EXIT_Z), (b.x, b.y, L.EXIT_Z)], h=3.0, post_step=6.0,
                 m="Wood_Dark", rail_m="Wood_Plank")
    br.finish()
    col_box("ExitBridge", (d.length + 1.0, L.EXIT_W, 3.0), ((s0 + s1) / 2 + Vector((0, 0, -1.5))),
            (0, 0, math.atan2(d.y, d.x)))
    # ilhota (pilar de rocha) + plataforma
    ic = L.islet_center()
    il = MB("EXIT_Islet_Blockout", "07_NEXT_ISLAND", rng, detail="far")
    il.cyl(L.GATE_ISLET_R, 90.0, (ic[0], ic[1], L.EXIT_Z - 45.0), (0, 0, 0), "Cliff_Rock_Tan", 12,
           r2=L.GATE_ISLET_R * 0.55, bevel=0.0)
    p_end = Vector((*L.anchor_pos(), L.EXIT_Z))
    il.beam(s1 + Vector((0, 0, -1.0)), p_end + Vector((0, 0, -1.0)), 2.0, 30.0, "Stone_Paving_Warm", 0.05,
            roll=math.pi / 2)
    il.finish()
    col_box("ExitIslet", ((p_end - s1).length, 30.0, 3.0), ((s1 + p_end) / 2 + Vector((0, 0, -1.5))),
            (0, 0, math.atan2(d.y, d.x)))
    # guardas laterais da plataforma (a ponta da ancora fica aberta)
    gg = MB("EXIT_Guards_Blockout", "07_NEXT_ISLAND", rng, detail="near")
    for s in (-1, 1):
        a = s1 + side * s * 14.4
        b = p_end + side * s * 14.4
        guard(gg, [(a.x, a.y), (b.x, b.y)], L.EXIT_Z, "parapet", "ExitIslet")
        c0 = s1 + side * s * 9.4
        guard(gg, [(c0.x, c0.y), (a.x, a.y)], L.EXIT_Z, "parapet", "ExitIslet")
    # pilares da interface (ponta da ancora)
    for s in (-1, 1):
        q = p_end + side * s * (L.EXIT_W / 2 + 1.5) - Vector((ux, uy, 0)) * 1.5
        gg.box((2.6, 2.6, 9.0), (q.x, q.y, L.EXIT_Z + 4.5), (0, 0, yaw), "Stone_Wall_Light", 0.15)
        gg.box((3.4, 3.4, 1.4), (q.x, q.y, L.EXIT_Z + 9.7), (0, 0, yaw), "Lantern_Glow", 0.05)
        col_box("ExitIslet", (2.6, 2.6, 9.0), (q.x, q.y, L.EXIT_Z + 4.5), (0, 0, yaw))
    gg.finish()
    # portao Dragon Ball (blockout): pilares vermelhos, telhado dourado, medalhao, barreira laranja
    gp = Vector((*L.gate_db_pos(), L.EXIT_Z))
    gt = MB("GATE_DB_Frame_Blockout", "08_PURCHASE_GATES", rng)
    ow = L.PG_OPEN_W / 2
    for s in (-1, 1):
        q = gp + side * s * (ow + 1.6)
        gt.cyl(1.6, 20.0, (q.x, q.y, L.EXIT_Z + 10.0), (0, 0, 0), "Wood_Lacquer_Red", 12, bevel=0.0)
        col_box("GateDB", (3.4, 3.4, 20.0), (q.x, q.y, L.EXIT_Z + 10.0))
        q2 = gp + side * s * (ow + 8.0) - Vector((ux, uy, 0)) * 4.0
        gt.box((5.0, 5.0, 4.0), (q2.x, q2.y, L.EXIT_Z + 2.0), (0, 0, yaw), "Stone_Wall_Light", 0.15)
        gt.box((3.0, 3.5, 5.0), (q2.x, q2.y, L.EXIT_Z + 6.5), (0, 0, yaw), "Stone_Wall_Dark", 0.3)
        gt.ico(1.6, (q2.x, q2.y, L.EXIT_Z + 9.8), "DB_Energy_Glow", 1)
        col_box("GateDB", (5.0, 5.0, 9.0), (q2.x, q2.y, L.EXIT_Z + 4.5), (0, 0, yaw))
    gt.box((L.PG_OPEN_W + 12.0, 3.0, 2.4), (gp.x, gp.y, L.EXIT_Z + L.PG_OPEN_H + 1.2), (0, 0, yaw),
           "Wood_Lacquer_Red", 0.1)
    gt.box((L.PG_OPEN_W + 18.0, 9.0, 1.4), (gp.x, gp.y, L.EXIT_Z + L.PG_OPEN_H + 3.4), (0, 0, yaw), "Metal_Gold", 0.1)
    fwd = Vector((ux, uy, 0))
    med = gp - fwd * 1.8 + Vector((0, 0, L.PG_OPEN_H + 3.0))
    gt.cyl(3.4, 1.2, med, (math.pi / 2, 0, yaw), "Metal_Gold", 20, bevel=0.0)
    gt.ico(2.6, med - fwd * 0.6, "DB_Energy_Glow", 2)
    gt.finish()
    bar = MB("GATE_DB_Barrier", "08_PURCHASE_GATES", rng)
    bar.box((L.PG_OPEN_W, 0.4, L.PG_OPEN_H), (gp.x, gp.y, L.EXIT_Z + L.PG_OPEN_H / 2), (0, 0, yaw),
            "DB_Energy_Glow", 0.0)
    bar.box((3.0, 1.0, 3.6), (gp.x - fwd.x * 0.5, gp.y - fwd.y * 0.5, L.EXIT_Z + 9.0), (0, 0, yaw),
            "Metal_Gold", 0.2)
    bar.finish()
    lock = col_box("GateDBLock", (L.PG_OPEN_W, 1.2, L.PG_OPEN_H), (gp.x, gp.y, L.EXIT_Z + L.PG_OPEN_H / 2),
                   (0, 0, yaw), kind="GateLock")
    lock["gate"] = "DB"
    # marcadores da saida e do portao
    mk("ISLAND_EXIT_Naruto", (s0.x, s0.y, L.EXIT_Z), (0, 0, yaw), 3.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": L.EXIT_Z})
    mk("GATE_DB", (gp.x, gp.y, L.EXIT_Z), (0, 0, yaw), 4.0, "ARROWS",
       props={"open_w": L.PG_OPEN_W, "open_h": L.PG_OPEN_H, "area_id": 2})
    mk("GATE_DB_LOCKED", (gp.x, gp.y, L.EXIT_Z + L.PG_OPEN_H / 2), (0, 0, yaw), 2.0, "CUBE")
    q = gp - fwd * 7.0
    mk("GATE_DB_INTERACT", (q.x, q.y, L.EXIT_Z + 0.2), (0, 0, yaw), 2.0, "SPHERE", props={"radius": 10.0})
    q = gp + fwd * 12.0
    mk("GATE_DB_EXIT", (q.x, q.y, L.EXIT_Z + 0.2), (0, 0, yaw), 2.0, "ARROWS")
    q = gp - fwd * 2.0 + Vector((0, 0, L.PG_OPEN_H + 8.0))
    mk("PURCHASE_UI_ANCHOR_DB", (q.x, q.y, q.z), (0, 0, yaw + math.pi), 2.0, "SINGLE_ARROW",
       props={"gate": "DB", "faces": "approach"})
    mk("ISLAND_NEXT_ANCHOR", (p_end.x, p_end.y, L.EXIT_Z), (0, 0, yaw), 5.0, "ARROWS",
       props={"width": L.EXIT_W, "clear_h": L.PG_OPEN_H + 4.0, "deck_z": L.EXIT_Z, "heading_deg": L.EXIT_DEG,
              "next_area": 2})


# ------------------------------------------------------------------ marcadores da entrada e do mundo
def world_markers():
    mk("WORLD_FROM_LOBBY", (0.0, L.LOBBY_Y, L.G), (0, 0, 0), 4.0, "ARROWS",
       props={"width": L.BRIDGE_W, "deck_z": L.G})
    mk("WORLD_ENTRY_Naruto", (0.0, -100.0, L.G + 0.2), (0, 0, 0), 3.0, "ARROWS")
    path = [(0.0, -100.0, L.G), (0.0, -86.0, L.RING), (0.0, -64.0, L.RING), (0.0, -44.0, L.PIT),
            (0.0, -18.0, L.PIT)]
    for i, p in enumerate(path):
        mk("PATH_ENTRY_CENTER_%02d" % i, p, (0, 0, 0), 1.5, "SPHERE")
    mk("PATH_ENTRY_CENTER", path[-2], (0, 0, 0), 3.0, "ARROWS",
       props={"waypoints": ";".join("%.1f,%.1f,%.1f" % p for p in path)})
    # NPC / interacao (4 construcoes entraveis)
    x, y, r = L.MAIN_HALL
    mk("NPC_MainHall", (x, y + 4.0, L.T2 + 0.3), (0, 0, math.pi), 2.0, "ARROWS")
    mk("PLAYER_INTERACT_MainHall", (x, y - 4.0, L.T2 + 0.3), (0, 0, 0), 2.0, "SPHERE")
    x, y, r = L.BLUE_W
    mk("NPC_WeaponShop", (x, y + 3.0, L.T2 + 0.3), (0, 0, math.pi), 2.0, "ARROWS")
    mk("PLAYER_INTERACT_WeaponShop", (x, y - 4.0, L.T2 + 0.3), (0, 0, 0), 2.0, "SPHERE")
    x, y, w, d, yaw = L.RAMEN
    mk("NPC_Ramen", (x, y + 2.0, L.T1 + 0.3), (0, 0, math.pi), 2.0, "ARROWS")
    mk("PLAYER_INTERACT_Ramen", (x, y - d / 2 - 2.5, L.T1 + 0.3), (0, 0, 0), 2.0, "SPHERE")
    mx, my, mw, md = L.MILL
    mk("NPC_Mill", (mx + 2.0, my, L.G + 0.3), (0, 0, math.pi / 2), 2.0, "ARROWS")
    mk("PLAYER_INTERACT_Mill", (mx - mw / 2 - 3.0, my, L.G + 0.3), (0, 0, -math.pi / 2), 2.0, "SPHERE")


def build():
    terrain()
    terrace_guards()
    stairs_all()
    mining()
    entrance()
    village()
    summon()
    east()
    exit_and_gate()
    world_markers()
