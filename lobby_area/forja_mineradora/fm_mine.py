# fm_mine - MINA (face NE do macico SW) + TRILHOS (mina -> transporte -> ala de recebimento da forja)
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, bezier, resample
from fm_parts import (Frame, cliff_band, rails, mine_cart, crystal_cluster, lantern, hanging_lantern, banner,
                      crate, barrel, masonry_wall, rock_scatter, P3)
import fm_layout as L

F0 = L.FLOOR


def tunnel_frame():
    mx, my = L.MINE_MOUTH
    return Frame(mx, my, 0.0, L.MINE_DIR)   # +x local = para dentro do tunel, +y local = esquerda


# caminho do tunel em coordenadas locais (entra reto e faz curva a esquerda ate a camara)
TUN = [(-3.0, 0.0), (10.0, 0.0), (22.0, 0.0), (30.0, 2.5), (37.0, 7.0)]
CHAMBER = (46.0, 12.0, 12.5)   # centro local e raio


def build():
    rng = random.Random(505)
    F = tunnel_frame()
    W = L.MINE_W
    H = L.MINE_H
    zt = F0 + H
    mb = MB("MINE_Tunnel_Shell", "04_MINE", rng)
    tun = [F.p(x, y, 0) for x, y in TUN]
    fine = resample(tun, 3.0)
    # piso de terra batida + paredes de rocha irregular + teto
    for i, p in enumerate(fine):
        j = min(i + 1, len(fine) - 1)
        k = max(i - 1, 0)
        t = (fine[j] - fine[k]).normalized()
        a = math.atan2(t.y, t.x)
        side = Vector((-t.y, t.x, 0))
        mb.box((3.4, W + 1.0, 1.0), (p.x, p.y, F0 - 0.3), (0, 0, a), "Dirt", 0.1)
        for s in (-1, 1):
            base = p + side * s * (W / 2 + 2.2)
            mb.box((3.4, 3.4, H + 4), (base.x, base.y, F0 + (H + 4) / 2 - 1), (0, 0, a), "Cliff_Rock_Dark", 0.3)
            for zz in (F0 + 2.0, F0 + 6.5, F0 + 11.0):
                q = p + side * s * (W / 2 + rng.uniform(0.2, 0.9))
                mb.rock((q.x, q.y, zz), (rng.uniform(2.6, 4.0), rng.uniform(2.0, 3.0), rng.uniform(3.8, 5.2)),
                        "Cliff_Rock" if rng.random() > 0.4 else "Cliff_Rock_Dark", 1, (0, 0, a))
        mb.box((3.4, W + 6.0, 3.0), (p.x, p.y, zt + 1.5), (0, 0, a), "Cliff_Rock_Dark", 0.2)
        mb.rock((p.x, p.y, zt - 0.3), (3.4, W * 0.8, 1.6), "Cliff_Rock", 1, (0, 0, a), flat_bottom=False)
    # camara de cristais
    cxl, cyl, cr = CHAMBER
    cc = F.p(cxl, cyl, 0)
    mb.cyl(cr + 1.0, 1.0, (cc.x, cc.y, F0 - 0.3), (0, 0, 0), "Dirt", 16, bevel=0.1)
    n = 16
    for i in range(n):
        a = i / n * math.tau
        dirv = Vector((math.cos(a), math.sin(a), 0))
        # a abertura da camara para o tunel fica livre
        to_tun = (F.p(37.0, 7.0, 0) - cc).normalized()
        if dirv.dot(to_tun) > 0.86:
            continue
        q = cc + dirv * (cr + 2.0)
        mb.box((3.6, 2 * (cr + 2) * math.sin(math.pi / n) + 1.0, H + 6), (q.x, q.y, F0 + (H + 6) / 2 - 1), (0, 0, a),
               "Cliff_Rock_Dark", 0.3)
        for zz in (F0 + 2.5, F0 + 8.0, F0 + 13.0):
            q2 = cc + dirv * (cr + rng.uniform(-0.2, 0.6))
            mb.rock((q2.x, q2.y, zz), (rng.uniform(3.2, 4.4), rng.uniform(3.0, 4.2), rng.uniform(4.5, 6.0)),
                    "Cliff_Rock" if rng.random() > 0.5 else "Cliff_Rock_Dark", 1, (0, 0, a))
    mb.cyl(cr + 3.0, 3.0, (cc.x, cc.y, zt + 3.5), (0, 0, 0), "Cliff_Rock_Dark", 16, bevel=0.2)
    for i in range(10):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(2, cr - 2)
        mb.cyl(rng.uniform(0.8, 1.6), rng.uniform(2.5, 4.5), (cc.x + math.cos(a) * r, cc.y + math.sin(a) * r, zt + 0.5),
               (math.pi, 0, 0), "Cliff_Rock", 5, r2=0.1, bevel=0.0)
    mb.finish()

    # escoramento de madeira a cada 5 studs (pares de esteios + chapeu + maos-francesas)
    tb = MB("MINE_Timber_Sets", "04_MINE", rng)
    sets = resample(tun, 5.0)
    for i, p in enumerate(sets[1:-1], 1):
        t = (sets[i + 1] - sets[i - 1]).normalized()
        a = math.atan2(t.y, t.x)
        side = Vector((-t.y, t.x, 0))
        for s in (-1, 1):
            q = p + side * s * (W / 2 - 0.6)
            tb.box((1.1, 1.1, H - 1.0), (q.x, q.y, F0 + (H - 1.0) / 2), (0, 0, a + rng.uniform(-0.05, 0.05)),
                   "Wood_Dark", 0.12)
            tb.beam(q + Vector((0, 0, H - 4.0)), p + side * s * (W / 2 - 3.2) + Vector((0, 0, H - 1.0)), 0.6, 0.6,
                    "Wood_Dark", 0.06)
        tb.box((1.3, W + 0.6, 1.3), (p.x, p.y, F0 + H - 0.8), (0, 0, a), "Wood_Dark", 0.12)
        if i % 2 == 0:
            hanging_lantern(tb, (p.x, p.y, F0 + H - 1.5), name="L_Mine_%02d" % i, chain=1.2)
    # cristais nas paredes do tunel e da camara (luz fria) + nos cantos
    for i, p in enumerate(fine[3::2]):
        s = 1 if i % 2 else -1
        j = min(fine.index(p) + 1, len(fine) - 1)
        t = (fine[j] - p).normalized() if (fine[j] - p).length > 0 else Vector((1, 0, 0))
        side = Vector((-t.y, t.x, 0))
        q = p + side * s * (W / 2 - 1.2)
        crystal_cluster(tb, (q.x, q.y, F0 + 0.2), rng.uniform(0.7, 1.1), "Crystal_Blue", rng, 6)
    for i in range(9):
        a = i / 9 * math.tau + 0.3
        q = cc + Vector((math.cos(a), math.sin(a), 0)) * (cr - 2.2)
        crystal_cluster(tb, (q.x, q.y, F0 + 0.2), rng.uniform(1.0, 1.7), "Crystal_Blue" if i % 3 else "Crystal_Purple",
                        rng, 7)
    crystal_cluster(tb, (cc.x, cc.y, F0 + 0.2), 2.2, "Crystal_Blue", rng, 9)
    light("L_Mine_Chamber", "POINT", (cc.x, cc.y, F0 + 8), 1400, (0.35, 0.6, 1.0), 3.0)
    light("L_Mine_Tunnel", "POINT", tuple(F.p(18, 0, F0 + 8)), 500, (0.45, 0.65, 1.0), 2.0)
    # galerias que continuam (interditadas com tabuas e placa de perigo)
    for ga in (D(30), D(-40)):
        dirv = Vector((math.cos(ga + L.MINE_DIR + 0.5), math.sin(ga + L.MINE_DIR + 0.5), 0))
        q = cc + dirv * (cr - 0.5)
        a = math.atan2(dirv.y, dirv.x)
        for k in range(5):
            tb.box((0.4, 7.0, 0.9), (q.x, q.y, F0 + 1.5 + k * 1.8), (rng.uniform(-0.1, 0.1), 0, a + math.pi / 2 * 0 + math.pi / 2 + 0 * k),
                   "Wood_Plank", 0.06)
        for s in (-1, 1):
            p2 = q + Vector((-dirv.y, dirv.x, 0)) * s * 3.2
            tb.box((1.0, 1.0, 10.0), (p2.x, p2.y, F0 + 5.0), (0, 0, a), "Wood_Dark", 0.1)
    tb.finish()

    # colisao do tunel e da camara
    A = "Mine"
    for a_, b_ in zip(tun, tun[1:]):
        d = b_ - a_
        ang = math.atan2(d.y, d.x)
        c = (a_ + b_) / 2
        side = Vector((-d.y, d.x, 0)).normalized()
        col_box(A, (d.length + 3, W + 4, 3), (c.x, c.y, F0 - 1.5), (0, 0, ang), "Floor")
        for s in (-1, 1):
            q = c + side * s * (W / 2 + 1.5)
            col_box(A, (d.length + 3, 3, H + 2), (q.x, q.y, F0 + (H + 2) / 2), (0, 0, ang))
        col_box(A, (d.length + 3, W + 4, 2), (c.x, c.y, zt + 1), (0, 0, ang))
    col_box(A, (2 * cr + 4, 2 * cr + 4, 3), (cc.x, cc.y, F0 - 1.5), (0, 0, 0), "Floor")
    for i in range(12):
        a = i / 12 * math.tau
        dirv = Vector((math.cos(a), math.sin(a), 0))
        to_tun = (F.p(37.0, 7.0, 0) - cc).normalized()
        if dirv.dot(to_tun) > 0.8:
            continue
        q = cc + dirv * (cr + 1.0)
        col_box(A, (2.5, 2 * (cr + 1) * math.sin(math.pi / 12) + 1, H + 2), (q.x, q.y, F0 + (H + 2) / 2), (0, 0, a))
    col_box(A, (2 * cr + 4, 2 * cr + 4, 2), (cc.x, cc.y, zt + 1))
    marker("MINE_Interior_Zone", (cc.x, cc.y, F0), (0, 0, 0), 6, "CIRCLE", props={"zone": "mina_tutorial"})

    entrance(rng, F)
    build_rails(rng, F)


def entrance(rng, F):
    """boca da mina: portico de madeira macica, marquise, muros de arrimo e rocha em volta"""
    W = L.MINE_W
    H = L.MINE_H
    mb = MB("MINE_Entrance_Portal", "04_MINE", rng)
    # muros de arrimo em pedra de cada lado da boca (sobre a face)
    for s in (-1, 1):
        a = F.p(-1.5, s * (W / 2 + 0.8), 0)
        b = F.p(-1.5, s * (W / 2 + 8.5), 0)
        masonry_wall(mb, a, b, F0 - 0.5, F0 + H + 3.0, 2.4, rng, "Stone_Light", "Stone_Dark", course=1.8, mix=0.3)
    # portico: 2 esteios grossos, verga dupla, maos-francesas, amarras de corda
    for s in (-1, 1):
        q = F.p(-2.2, s * (W / 2 + 0.6), F0)
        mb.box((2.2, 2.2, H + 3.5), (q.x, q.y, F0 + (H + 3.5) / 2), F.r(), "Wood_Dark", 0.2)
        mb.box((2.8, 2.8, 1.0), (q.x, q.y, F0 + 0.5), F.r(), "Stone_Dark", 0.2)
        for zz in (F0 + 4.0, F0 + H - 1.0):
            mb.cyl(1.35, 0.7, (q.x, q.y, zz), F.r(), "Rope", 8, bevel=0.0)
        mb.beam(F.p(-2.2, s * (W / 2 + 0.6), F0 + H - 3.5), F.p(-2.2, s * (W / 2 - 3.0), F0 + H + 1.4), 1.0, 1.0,
                "Wood_Dark", 0.1)
    mb.box((2.4, W + 7.0, 1.8), F.p(-2.2, 0, F0 + H + 2.2), F.r(), "Wood_Dark", 0.2)
    mb.box((2.0, W + 5.0, 1.4), F.p(-2.2, 0, F0 + H + 0.7), F.r(), "Wood_Light", 0.15)
    # marquise de tabuas inclinada para fora com vigas
    for k in range(7):
        y = -W / 2 - 2.5 + k * (W + 5) / 6
        mb.beam(F.p(0.5, y, F0 + H + 3.4), F.p(-7.5, y, F0 + H + 1.2), 0.7, 0.8, "Wood_Dark", 0.08)
    for k in range(9):
        x = 0.0 - k * 0.95
        z = F0 + H + 3.9 - (k * 0.95) * (2.2 / 8.0)
        mb.box((1.0, W + 7.2, 0.35), F.p(x, rng.uniform(-0.3, 0.3), z), F.r(0, math.atan2(2.2, 8.0), 0), "Wood_Plank", 0.06)
    # placa com picareta e estandarte
    mb.box((0.5, 7.0, 2.4), F.p(-3.6, 0, F0 + H + 5.4), F.r(), "Wood_Dark", 0.15)
    from fm_parts import emblem_pickaxe
    emblem_pickaxe(mb, F.p(-3.9, 0, F0 + H + 5.4), F.a - math.pi / 2, s=0.45, normal_off=0.0)
    for s in (-1, 1):
        c = lantern(mb, tuple(F.p(-4.5, s * (W / 2 + 3.0), F0)), F.a + math.pi + (0.6 * s), name="L_MineGate_%d" % (s + 1),
                    h=7.0)
    banner(mb, tuple(F.p(-3.4, W / 2 + 5.0, F0 + 13.0)), F.a - math.pi / 2, w=3.0, h=6.0, cloth="Cloth_Navy",
           emblem="pickaxe")
    mb.box((0.8, 0.8, 13.5), F.p(-3.0, W / 2 + 5.0 - 2.2, F0 + 6.75), F.r(), "Wood_Dark", 0.1)
    mb.box((0.8, 0.8, 13.5), F.p(-3.0, W / 2 + 5.0 + 2.2, F0 + 6.75), F.r(), "Wood_Dark", 0.1)
    # entulho, cristais e carrinhos na boca
    crystal_cluster(mb, tuple(F.p(-6.0, -W / 2 - 2.0, F0)), 1.2, "Crystal_Blue", rng, 7)
    crystal_cluster(mb, tuple(F.p(2.0, W / 2 - 1.5, F0)), 0.9, "Crystal_Blue", rng, 5)
    for i, (x, y) in enumerate(((-8.0, -W / 2 - 4.0), (-10.0, W / 2 + 7.0))):
        crate(mb, tuple(F.p(x, y, F0)), 2.2, rng.uniform(0, 1), rng)
    barrel(mb, tuple(F.p(-7.5, W / 2 + 3.5, F0)))
    mb.finish()
    # rocha em volta e por cima da boca (penhasco da face da mina)
    fa, fb = L.MINE_FACE
    fa, fb = Vector((fa[0], fa[1], 0)), Vector((fb[0], fb[1], 0))
    mouth = Vector((L.MINE_MOUTH[0], L.MINE_MOUTH[1], 0))
    d = (fb - fa).normalized()
    ca = MB("MINE_Face_Cliffs", "02_TERRAIN", rng)
    ea = mouth - d * (W / 2 + 9.5)
    eb = mouth + d * (W / 2 + 9.5)
    cliff_band(ca, [fa, ea], F0 - 2, 32, rng, depth=2.5, rmin=4, rmax=6.5, step=5, face_side=1)
    cliff_band(ca, [eb, fb], F0 - 2, 30, rng, depth=2.5, rmin=4, rmax=6.5, step=5, face_side=1)
    inward = Vector((math.cos(L.MINE_DIR), math.sin(L.MINE_DIR), 0))
    cliff_band(ca, [ea + inward * 3, eb + inward * 3], F0 + H + 4.0, 33, rng, depth=2.0, rmin=4, rmax=6, step=4.5,
               face_side=1)
    ca.finish()
    A = "Mine"
    for p0, p1 in ((fa, ea), (eb, fb)):
        dd = p1 - p0
        c = (p0 + p1) / 2 + inward * 2.5
        col_box(A, (dd.length + 2, 6, 40), (c.x, c.y, 20), (0, 0, math.atan2(dd.y, dd.x)))
    for s in (-1, 1):
        q = F.p(-2.2, s * (W / 2 + 0.6), F0)
        col_box(A, (2.4, 2.4, H + 4), (q.x, q.y, F0 + (H + 4) / 2), F.r())
        q2 = F.p(-1.5, s * (W / 2 + 4.6), F0)
        col_box(A, (2.6, 8.0, H + 3.5), (q2.x, q2.y, F0 + (H + 3.5) / 2), F.r())
    q = F.p(-1.0, 0, F0)
    col_box(A, (4.0, W + 10, 20), (q.x, q.y, F0 + H + 12), F.r())
    marker("MINE_Entrance", tuple(F.p(-4.0, 0, F0)), F.r(0, 0, math.pi), 3, "ARROWS")


def rail_path(F):
    """mina (camara) -> tunel -> boca -> praca oeste -> ala de recebimento (portao oeste, y=18)"""
    cxl, cyl, cr = CHAMBER
    inner = [F.p(cxl - 4, cyl - 2.0, F0), F.p(37.0, 7.0, F0), F.p(30.0, 2.5, F0), F.p(22.0, 0.0, F0),
             F.p(8.0, 0.0, F0), F.p(-2.0, 0.0, F0)]
    wx0, wy0 = L.FORGE_WING_L[0], L.FORGE_WING_L[1]
    door_y = wy0 + 12.0
    out = bezier(F.p(-2.0, 0, F0), F.p(-26.0, 0, F0), Vector((-58, door_y - 34, F0)), Vector((-56, door_y - 8, F0)), 14)
    out2 = bezier(Vector((-56, door_y - 8, F0)), Vector((-55, door_y - 1, F0)), Vector((-50, door_y, F0)),
                  Vector((-44, door_y, F0)), 6)
    end = [Vector((wx0 + 5.5, door_y, F0))]
    pts = inner + out[1:] + out2[1:] + end
    return [Vector((p.x, p.y, F0 + 0.02)) for p in pts]


def build_rails(rng, F):
    pts = rail_path(F)
    mb = MB("RAIL_Main_Line", "10_RAILS", rng)
    rails(mb, pts, gauge=2.6, sleeper_step=1.7)
    # batente no fim (dentro da ala, antes da tremonha)
    e = pts[-1]
    t = (pts[-1] - pts[-2]).normalized()
    a = math.atan2(t.y, t.x)
    mb.box((1.2, 4.2, 1.4), (e.x + t.x * 0.8, e.y + t.y * 0.8, F0 + 0.9), (0, 0, a), "Wood_Dark", 0.12)
    for s in (-1, 1):
        mb.beam((e.x - t.x * 1.2 + (-t.y) * s * 1.3, e.y - t.y * 1.2 + t.x * s * 1.3, F0 + 0.4),
                (e.x + t.x * 0.6 + (-t.y) * s * 1.3, e.y + t.y * 0.6 + t.x * s * 1.3, F0 + 1.6), 0.5, 0.5, "Metal_Iron", 0.05)
    mb.finish()
    # carrinhos estacionados ao longo da rota (carregados na saida da mina, vazio na forja)
    cm = MB("RAIL_Mine_Carts", "10_RAILS", rng)
    fine = resample(pts, 1.0)
    for idx, load in ((12, "Crystal_Blue"), (30, None), (58, "Crystal_Blue"), (len(fine) - 3, "Crystal_Purple")):
        idx = min(idx, len(fine) - 2)
        p = fine[idx]
        t = (fine[idx + 1] - fine[idx]).normalized()
        mine_cart(cm, (p.x, p.y, F0 + 0.3), math.atan2(t.y, t.x), load, rng)
    cm.finish()
    # colisao dos carrinhos (obstaculos baixos)
    for idx in (12, 30, 58, len(fine) - 3):
        idx = min(idx, len(fine) - 2)
        p = fine[idx]
        t = (fine[idx + 1] - fine[idx]).normalized()
        col_box("Rails", (3.6, 2.6, 3.4), (p.x, p.y, F0 + 1.9), (0, 0, math.atan2(t.y, t.x)))
    marker("RAIL_Start_Mine", tuple(pts[0]), (0, 0, 0), 2)
    marker("RAIL_End_Forge", tuple(pts[-1]), (0, 0, 0), 2)
