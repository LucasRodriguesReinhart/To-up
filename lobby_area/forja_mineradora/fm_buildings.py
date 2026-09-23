# fm_buildings - praca + caminhos pavimentados, loja (interior completo), cabanas de mineiros (entraveis),
# estacao de carga sobre o trilho, galpao aberto de cristais na margem leste
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, resample, bezier, point_in_poly
from fm_parts import (Frame, masonry_wall, timber_wall, window_glow, arch, lantern, hanging_lantern, crate, barrel,
                      crystal_cluster, pave_poly, pave_ring, banner, emblem_pickaxe, fence, mine_cart, P3, frustum,
                      stone_parapet)
import fm_layout as L

F0 = L.FLOOR


def ribbon(pts, w):
    """poligono de uma faixa de largura w ao longo da polilinha"""
    pts = [Vector((p[0], p[1], 0)) for p in pts]
    left, right = [], []
    for i, p in enumerate(pts):
        j = min(i + 1, len(pts) - 1)
        k = max(i - 1, 0)
        t = (pts[j] - pts[k]).normalized()
        s = Vector((-t.y, t.x, 0))
        left.append(p + s * w / 2)
        right.append(p - s * w / 2)
    return [(p.x, p.y) for p in left + list(reversed(right))]


# ------------------------------------------------------------------ praca e caminhos
PATHS = {
    # nome: (pontos, largura)
    "Avenue": ([(0, -62.2), (0, -52)], 20.0),
    "West_Road": ([(-24, -36), (-38, -24), (-44, -8), (-44, 34)], 10.0),
    "Mine_Road": ([(-22, -44), (-40, -46), (-54, -40), (-60, -38)], 10.0),
    "Back_Court": ([(-116, 41), (50, 41)], 10.0),
    "East_Lane": ([(38, -8), (38, 36)], 7.0),
    "East_Road": ([(24, -20), (40, -18), (54, -18)], 10.0),
    "East_Bank": ([(70, -18), (96, -18), (96, 36), (70, 41)], 9.0),
    "East_Back": ([(70, 41), (116, 41)], 9.0),
    "Shop_Apron": ([(18, -40), (26, -39)], 8.0),
    "Mill_Apron": ([(38, 4), (L.MILL[0] + 9.0, 6), (L.MILL[0] + 9.0, 11)], 6.0),
}


def plaza_and_paths(rng):
    mb = MB("TER_Plaza_Paving", "02_TERRAIN", rng)
    cx, cy = 0.0, -30.0
    R = 25.0
    # praca circular: aneis de pedra + anel escuro de borda + mosaico central
    mb.cyl(R + 1.2, 0.8, (cx, cy, F0 - 0.2), (0, 0, 0), "Stone_Grout", 48, bevel=0.0)
    pave_ring(mb, cx, cy, 5.0, R - 1.4, F0 + 0.02, rng, 0, 360, ring_w=2.6, h=0.33, m="Stone_Paving")
    pave_ring(mb, cx, cy, R - 1.4, R + 0.8, F0 + 0.02, rng, 0, 360, ring_w=2.2, h=0.38, m="Stone_Dark")
    # centro: medalhao com picareta e martelo em pedra clara
    mb.cyl(5.0, 0.4, (cx, cy, F0 + 0.2), (0, 0, 0), "Stone_Dark", 32, bevel=0.1)
    mb.cyl(4.2, 0.45, (cx, cy, F0 + 0.25), (0, 0, 0), "Stone_Light", 32, bevel=0.1)
    for a in range(0, 360, 45):
        p = Vector((cx + math.cos(D(a)) * 3.2, cy + math.sin(D(a)) * 3.2, F0 + 0.5))
        mb.box((1.6, 0.5, 0.12), p, (0, 0, D(a)), "Metal_Brass", 0.02)
    mb.finish()
    pv = MB("TER_Path_Paving", "02_TERRAIN", rng)
    for name, (pts, w) in PATHS.items():
        pts2 = []
        for a, b in zip(pts, pts[1:]):
            pts2 += resample([Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))], 3.0)[:-1]
        pts2.append(Vector((pts[-1][0], pts[-1][1], 0)))
        poly = ribbon(pts2, w)
        pave_poly(pv, poly, F0 + 0.02, rng, tile=2.6, h=0.33, grout=True, bevel=0.0)
        # meio-fio de pedras nas bordas
        for i, p in enumerate(pts2[:-1]):
            q = pts2[i + 1]
            t = (q - p).normalized()
            s = Vector((-t.y, t.x, 0))
            for k in (-1, 1):
                c = (p + q) / 2 + s * k * (w / 2 + 0.35)
                if rng.random() < 0.85:
                    pv.box(((q - p).length - 0.2, 0.7, 0.55), (c.x, c.y, F0 + 0.2), (0, 0, math.atan2(t.y, t.x)),
                           "Stone_Light", 0.12)
    # patios diante dos pes das escadas dos portais
    for px in L.PORTAL_X:
        pave_poly(pv, [(px - 8, 38), (px + 8, 38), (px + 8, L.FLIGHT1_Y0), (px - 8, L.FLIGHT1_Y0)], F0 + 0.02, rng,
                  tile=2.6, h=0.33, grout=True)
    pv.finish()


# ------------------------------------------------------------------ loja
def shop(rng):
    x0, y0, x1, y1 = L.SHOP
    t = 1.6
    zs, ze = 9.0, 17.0
    mb = MB("BLD_Shop", "07_BUILDINGS", rng)
    mb.box2((x0 - 0.6, y0 - 0.6, F0 - 1), (x1 + 0.6, y1 + 0.6, F0 + 0.3), "Stone_Dark", 0.2)
    # frente (oeste, x0): porta 5 (y -41.5..-36.5) + vitrine iluminada
    fx = x0 + t / 2
    ops = [(3.5, 8.5, F0, 12.0, 2.5), (11.0, 16.0, F0 + 2.5, zs)]
    masonry_wall(mb, (fx, y1), (fx, y0), F0, zs, t, rng, openings=ops)
    arch(mb, (fx, y1 - 6.0, 0), D(-90), 5.0, 9.5, 2.5, t + 0.3, n=7, band=1.0)
    window_glow(mb, (fx, y1), (fx, y0), 11.0, 16.0, F0 + 2.5, zs, t)
    timber_wall(mb, (fx, y1), (fx, y0), zs, ze, t * 0.8, rng, openings=[(3.5, 8.5, zs, 12.0), (11.0, 16.0, 11.0, 15.0)],
                post=3.0)
    window_glow(mb, (fx, y1), (fx, y0), 11.0, 16.0, 11.0, 15.0, t * 0.8)
    # demais paredes
    for a, b in (((x0, y0 + t / 2), (x1, y0 + t / 2)), ((x1 - t / 2, y0), (x1 - t / 2, y1)),
                 ((x1, y1 - t / 2), (x0, y1 - t / 2))):
        masonry_wall(mb, a, b, F0, zs, t, rng)
        timber_wall(mb, a, b, zs, ze, t * 0.8, rng, openings=[(6.0, 10.0, 11.0, 14.5)], post=3.2)
        window_glow(mb, a, b, 6.0, 10.0, 11.0, 14.5, t * 0.8)
    # oitoes para frente/fundos (cumeeira em X) e telhado vermelho
    for gx in (fx, x1 - t / 2):
        mb.gable_wall(gx, (y0 + y1) / 2, y1 - y0, ze, 7.0, t * 0.8, "X", "Plaster")
    mb.gable_roof((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, ze, 7.0, "Roof_Red", thick=0.8, over=1.5, axis="X")
    # toldo listrado sobre porta/vitrine
    for i in range(8):
        yy = y1 - 2.0 - i * 2.0
        mb.box((4.4, 2.0, 0.3), (x0 - 2.0, yy, 12.6), (0, D(-18), 0), "Cloth_Red" if i % 2 else "Cloth_Canvas", 0.03)
    for yy in (y1 - 1.6, y0 + 1.6):
        mb.beam((x0 - 4.0, yy, 11.9), (x0, yy, 13.3), 0.4, 0.4, "Wood_Dark", 0.03)
    # placa pendurada (picareta + gema)
    mb.beam((x0 - 0.2, y1 - 1.0, 15.0), (x0 - 4.5, y1 - 1.0, 15.0), 0.4, 0.4, "Wood_Dark", 0.03)
    mb.box((0.4, 3.6, 2.8), (x0 - 3.6, y1 - 1.0, 13.2), (0, 0, 0), "Wood_Plank", 0.1)
    emblem_pickaxe(mb, Vector((x0 - 3.85, y1 - 1.0, 13.2)), D(-90), s=0.32, normal_off=0.0)
    crystal_cluster(mb, (x0 - 3.6, y1 - 1.0, 14.8), 0.35, "Crystal_Blue", rng, 3)
    # interior: piso de tabuas, balcao em L, prateleiras, vitrines
    from fm_parts import plank_floor
    plank_floor(mb, Frame((x0 + x1) / 2, (y0 + y1) / 2, 0, 0.0), x1 - x0 - 2 * t, y1 - y0 - 2 * t, F0 + 0.3, rng)
    cx = x0 + 10.5
    mb.box2((cx - 0.8, y0 + 3.0, F0), (cx + 0.8, y1 - 5.5, F0 + 3.2), "Wood_Plank", 0.1)
    mb.box2((cx - 1.1, y0 + 2.8, F0 + 3.2), (cx + 1.1, y1 - 5.3, F0 + 3.6), "Wood_Light", 0.1)
    for zz in (F0 + 2.0, F0 + 4.4, F0 + 6.8):
        mb.box2((x1 - 2.6, y0 + 2.0, zz), (x1 - 1.6, y1 - 2.0, zz + 0.3), "Wood_Light", 0.05)
        for k in range(8):
            yy = y0 + 3.0 + k * 1.7
            if k % 3 == 0:
                mb.beam((x1 - 2.1, yy, zz + 0.3), (x1 - 2.1, yy + 0.4, zz + 2.1), 0.25, 0.25, "Wood_Light", 0.0)
                mb.box((0.4, 1.4, 0.4), (x1 - 2.1, yy + 0.5, zz + 2.0), (0, 0, 0), "Metal_Iron", 0.03)
            else:
                crystal_cluster(mb, (x1 - 2.1, yy, zz + 0.3), 0.3, "Crystal_Blue" if k % 2 else "Crystal_Purple", rng, 3)
    for yy in (y0 + 3.5, y1 - 3.5):
        mb.box2((x0 + 3.0, yy - 1.2, F0), (x0 + 6.0, yy + 1.2, F0 + 2.8), "Wood_Dark", 0.1)
        crystal_cluster(mb, (x0 + 4.5, yy, F0 + 2.8), 0.45, "Crystal_Blue", rng, 4)
    hanging_lantern(mb, ((x0 + x1) / 2, (y0 + y1) / 2, ze - 0.2), name="L_Shop_In", chain=5.5)
    light("L_Shop_Fill", "POINT", ((x0 + x1) / 2, (y0 + y1) / 2, 12.0), 700, (1.0, 0.72, 0.45), 3.0)
    lantern(mb, (x0 - 2.0, y0 + 2.0, F0), D(180), name="L_Shop_Door", h=6.5)
    mb.finish()
    A = "Shop"
    # parede frontal em 3 trechos (porta), vitrine fechada
    col_box2(A, (x0, y1 - 3.5, F0), (x0 + t, y1, ze))
    col_box2(A, (x0, y0, F0), (x0 + t, y1 - 8.5, ze))
    col_box2(A, (x0, y1 - 8.5, 12.0), (x0 + t, y1 - 3.5, ze))
    col_box2(A, (x0, y0, F0), (x1, y0 + t, ze))
    col_box2(A, (x1 - t, y0, F0), (x1, y1, ze))
    col_box2(A, (x0, y1 - t, F0), (x1, y1, ze))
    col_box2(A, (cx - 1.1, y0 + 2.8, F0), (cx + 1.1, y1 - 5.3, F0 + 3.6))
    col_box2(A, (x1 - 2.6, y0 + 2.0, F0), (x1 - 1.6, y1 - 2.0, F0 + 9.0))
    for yy in (y0 + 3.5, y1 - 3.5):
        col_box2(A, (x0 + 3.0, yy - 1.2, F0), (x0 + 6.0, yy + 1.2, F0 + 2.8))
    col_box2(A, (x0 - 1, y0 - 1, ze), (x1 + 1, y1 + 1, ze + 8))
    marker("NPC_Shop", (cx + 2.5, (y0 + y1) / 2, F0 + 0.3), (0, 0, D(90)), 2, "ARROWS", props={"npc": "Lojista"})
    marker("INTERACT_Shop", (cx, (y0 + y1) / 2, F0 + 3.6), (0, 0, 0), 1.5, "SPHERE")
    marker("PLAYER_INTERACT_Shop", (cx - 4.0, (y0 + y1) / 2, F0 + 0.3), (0, 0, 0), 2, "CIRCLE")
    marker("DOOR_Shop", (x0, y1 - 6.0, F0), (0, 0, 0), 1.5)


# ------------------------------------------------------------------ cabanas de mineiros (entraveis)
def cabin(name, cx, cy, ang, rng, w=14.0, d=12.0, roof="Roof", sign=None):
    """porta na face local -Y; interior com cama, mesa, bancos, prateleira e lanterna"""
    F = Frame(cx, cy, 0.0, ang)
    t = 1.4
    zs, ze = 3.5, 10.5
    mb = MB("BLD_Cabin_" + name, "07_BUILDINGS", rng)
    c = [F.p(-w / 2, -d / 2), F.p(w / 2, -d / 2), F.p(w / 2, d / 2), F.p(-w / 2, d / 2)]
    mb.prism([(p.x, p.y) for p in (F.p(-w / 2 - 0.6, -d / 2 - 0.6), F.p(w / 2 + 0.6, -d / 2 - 0.6),
                                   F.p(w / 2 + 0.6, d / 2 + 0.6), F.p(-w / 2 - 0.6, d / 2 + 0.6))],
             F0 - 1, F0 + 0.3, "Stone_Dark", bevel=0.2)
    walls = [(c[0], c[1], [(w / 2 - 2.2, w / 2 + 2.2, F0, F0 + 7.5)], [(1.5, 4.0, F0 + 3.5, F0 + 6.2)]),
             (c[1], c[2], [], [(d / 2 - 1.8, d / 2 + 1.8, F0 + 3.5, F0 + 6.2)]),
             (c[2], c[3], [], [(w / 2 - 2.0, w / 2 + 2.0, F0 + 3.5, F0 + 6.2)]),
             (c[3], c[0], [], [])]
    for a, b, doors, wins in walls:
        n = Vector((-(b - a).y, (b - a).x, 0)).normalized()   # normal interna (poligono anti-horario)
        a2, b2 = a + n * t / 2, b + n * t / 2
        ops = [(o[0], o[1], o[2], min(o[3], F0 + zs)) for o in doors]
        masonry_wall(mb, a2, b2, F0, F0 + zs, t, rng, openings=ops, course=1.2)
        tops = [(o[0], o[1], F0 + zs, o[3]) for o in doors] + wins
        timber_wall(mb, a2, b2, F0 + zs, F0 + ze, t * 0.8, rng, openings=tops, post=3.0)
        for o in wins:
            window_glow(mb, a2, b2, o[0], o[1], o[2], o[3], t * 0.8)
    axis = "Y" if abs(math.sin(ang)) < 0.5 else "X"
    for k in (-1, 1):
        g = F.p(0, k * (d / 2 - t / 2))
        mb.gable_wall(g.x, g.y, w, F0 + ze, 5.0, t * 0.8, axis, "Plaster")
    ctr = F.p(0, 0)
    if abs(math.sin(ang)) < 0.5:
        mb.gable_roof(ctr.x, ctr.y, w, d, F0 + ze, 5.0, roof, thick=0.7, over=1.2, axis="Y")
    else:
        mb.gable_roof(ctr.x, ctr.y, d, w, F0 + ze, 5.0, roof, thick=0.7, over=1.2, axis="X")
    # piso e mobilia
    from fm_parts import plank_floor
    plank_floor(mb, F, w - 2 * t, d - 2 * t, F0 + 0.3, rng)
    bed = F.p(-w / 2 + 3.0, d / 2 - 3.2, 0)
    mb.box((3.6, 5.4, 1.4), (bed.x, bed.y, F0 + 1.0), F.r(), "Wood_Dark", 0.1)
    mb.box((3.2, 5.0, 0.6), (bed.x, bed.y, F0 + 1.9), F.r(), "Cloth_Canvas", 0.15)
    mb.box((3.2, 1.6, 0.7), F.p(-w / 2 + 3.0, d / 2 - 1.3, F0 + 2.4), F.r(), "Cloth_Red", 0.2)
    tb = F.p(w / 2 - 3.4, d / 2 - 3.2, 0)
    mb.box((3.4, 2.4, 0.3), (tb.x, tb.y, F0 + 3.0), F.r(), "Wood_Light", 0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = F.p(w / 2 - 3.4 + sx * 1.3, d / 2 - 3.2 + sy * 0.9, 0)
            mb.box((0.35, 0.35, 2.8), (q.x, q.y, F0 + 1.5), F.r(), "Wood_Dark", 0.0)
    for k in (-1, 1):
        q = F.p(w / 2 - 3.4 + k * 2.4, d / 2 - 3.2, 0)
        mb.cyl(0.6, 1.8, (q.x, q.y, F0 + 0.9), F.r(), "Wood_Plank", 8, bevel=0.05)
    mb.box((1.0, 0.8, 0.9), F.p(w / 2 - 3.4, d / 2 - 3.2, F0 + 3.6), F.r(), "Lantern_Glow", 0.05)
    sh = F.p(-w / 2 + 1.6, -d / 2 + 3.5, 0)
    for zz in (F0 + 2.0, F0 + 4.0):
        mb.box((0.9, 3.4, 0.25), (sh.x, sh.y, zz), F.r(), "Wood_Light", 0.03)
    crate(mb, tuple(F.p(w / 2 - 2.2, -d / 2 + 2.6, F0)), 2.0, ang, rng)
    mb.beam(F.p(-1.5, -d / 2 + t + 0.4, F0 + 3.8), F.p(1.5, -d / 2 + t + 0.4, F0 + 3.8), 0.25, 0.25, "Wood_Dark", 0.0)
    emblem_pickaxe(mb, F.p(0, -d / 2 - 0.1, F0 + 9.0 + 3.6), ang, s=0.45)
    lantern(mb, tuple(F.p(w / 2 - 1.0, -d / 2 - 2.2, F0)), ang - math.pi / 2, name="L_Cabin_" + name, h=5.5)
    light("L_Cabin_In_" + name, "POINT", tuple(F.p(0, 1.0, F0 + 6.5)), 90, (1.0, 0.6, 0.3), 0.5)
    mb.finish()
    A = "Cabin"
    # colisao: 4 paredes (frente com vao da porta), mobilia principal, telhado
    for (a, b, doors, _w) in walls:
        dv = b - a
        Lw = dv.length
        tt = dv.normalized()
        n = Vector((-tt.y, tt.x, 0))
        segs = [(0, Lw)]
        if doors:
            o = doors[0]
            segs = [(0, o[0]), (o[1], Lw)]
            cc = a + tt * ((o[0] + o[1]) / 2) + n * t / 2
            col_box(A, (o[1] - o[0], t, ze - 7.5), (cc.x, cc.y, F0 + 7.5 + (ze - 7.5) / 2), (0, 0, math.atan2(tt.y, tt.x)))
        for s0, s1 in segs:
            cc = a + tt * ((s0 + s1) / 2) + n * t / 2
            col_box(A, (s1 - s0, t, ze), (cc.x, cc.y, F0 + ze / 2), (0, 0, math.atan2(tt.y, tt.x)))
    col_box(A, (3.6, 5.4, 2.4), (bed.x, bed.y, F0 + 1.2), F.r())
    col_box(A, (8.4, 2.4, 3.2), (tb.x, tb.y, F0 + 1.6), F.r())
    col_box(A, (w + 2, d + 2, 3), (ctr.x, ctr.y, F0 + ze + 2.0), F.r())
    marker("DOOR_Cabin_" + name, tuple(F.p(0, -d / 2, F0)), F.r(0, 0, -math.pi / 2), 1.5)


# ------------------------------------------------------------------ estacao de carga sobre o trilho + galpao leste
def weigh_station(rng):
    """telheiro aberto sobre o trilho (balanca de vagonetes, caixas, lanterna) - nao cria expectativa de porta"""
    import fm_mine
    pts = fm_mine.rail_path(fm_mine.tunnel_frame())
    fine = resample(pts, 1.0)
    # ponto do trilho na praca oeste
    idx = min(range(len(fine)), key=lambda k: (fine[k] - Vector((-54, -8, F0))).length)
    p = fine[idx]
    tdir = (fine[idx + 1] - fine[idx - 1]).normalized()
    a = math.atan2(tdir.y, tdir.x)
    F = Frame(p.x, p.y, 0, a)
    mb = MB("BLD_Rail_Weigh_Station", "07_BUILDINGS", rng)
    for sx in (-5.0, 5.0):
        for sy in (-5.5, 5.5):
            q = F.p(sx, sy)
            mb.box((1.0, 1.0, 10.0), (q.x, q.y, F0 + 5.0), F.r(), "Wood_Dark", 0.12)
            mb.box((1.6, 1.6, 0.8), (q.x, q.y, F0 + 0.4), F.r(), "Stone_Dark", 0.12)
            col_box("Station", (1.2, 1.2, 10.0), (q.x, q.y, F0 + 5.0), F.r())
    for sy in (-5.5, 5.5):
        mb.beam(F.p(-5.8, sy, F0 + 10.2), F.p(5.8, sy, F0 + 10.2), 0.9, 1.0, "Wood_Dark", 0.08)
    for sx in (-5.0, 5.0):
        mb.beam(F.p(sx, -6.2, F0 + 10.2), F.p(sx, 6.2, F0 + 10.2), 0.9, 1.0, "Wood_Dark", 0.08)
    # telhado de 2 aguas (cumeeira ao longo do trilho)
    rang = math.atan2(3.0, 7.0)
    for k in (-1, 1):
        for i in range(5):
            f = i / 5
            yy = k * (7.5 - 7.5 * f - 0.75)
            zz = F0 + 10.8 + 3.0 * f + 0.3
            q = F.p(0, yy)
            mb.box((14.0, 1.9, 0.4), (q.x, q.y, zz), F.r(k * rang, 0, 0), "Roof", 0.08)
    mb.box((14.4, 1.0, 1.0), (p.x, p.y, F0 + 14.2), F.r(), "Wood_Dark", 0.08)
    # balanca (plataforma de ferro sob o trilho) e mostrador
    q = F.p(0, 0)
    mb.box((6.0, 4.6, 0.25), (q.x, q.y, F0 + 0.02), F.r(), "Metal_Iron", 0.03)
    q2 = F.p(0, 4.4)
    mb.box((1.2, 1.2, 4.6), (q2.x, q2.y, F0 + 2.3), F.r(), "Wood_Dark", 0.1)
    mb.cyl(1.2, 0.4, (q2.x, q2.y, F0 + 5.2), F.r(D(90), 0, 0), "Metal_Brass", 16, bevel=0.05)
    col_box("Station", (1.4, 1.4, 5.0), (q2.x, q2.y, F0 + 2.5), F.r())
    for i, (sx, sy) in enumerate(((3.5, -4.2), (-3.5, -4.4), (-3.0, 4.6))):
        crate(mb, tuple(F.p(sx, sy, F0)), 2.2, a + rng.uniform(-0.3, 0.3), rng)
        q3 = F.p(sx, sy)
        col_box("Station", (2.4, 2.4, 2.4), (q3.x, q3.y, F0 + 1.2), F.r())
    hanging_lantern(mb, tuple(F.p(0, 0, F0 + 10.0)), name="L_Station", chain=1.5)
    mb.finish()
    marker("RAIL_Weigh_Station", (p.x, p.y, F0), F.r(), 2)


def crystal_shed(rng):
    """galpao aberto (tres lados) na margem leste: estoque de cristais refinados aguardando a forja"""
    F = Frame(112.0, -34.0, 0, D(180))   # abertura voltada para oeste (caminho)
    mb = MB("BLD_Crystal_Shed", "07_BUILDINGS", rng)
    w, d = 16.0, 10.0
    t = 1.2
    for (a, b) in ((F.p(-w / 2, d / 2), F.p(w / 2, d / 2)), (F.p(w / 2, -d / 2), F.p(w / 2, d / 2)),
                   (F.p(-w / 2, -d / 2), F.p(-w / 2, d / 2))):
        timber_wall(mb, a, b, F0, F0 + 8.0, t, rng, post=3.0, m_p="Wood_Plank")
        dv = b - a
        cc = (a + b) / 2
        col_box("Shed", (dv.length, t, 8.0), (cc.x, cc.y, F0 + 4.0), (0, 0, math.atan2(dv.y, dv.x)))
    for sx in (-w / 2, w / 2):
        q = F.p(sx, -d / 2)
        mb.box((1.0, 1.0, 8.0), (q.x, q.y, F0 + 4.0), F.r(), "Wood_Dark", 0.1)
    rang = math.atan2(2.5, d)
    for i in range(6):
        f = i / 6
        q = F.p(0, -d / 2 - 0.8 + (d + 1.6) * (f + 0.08))
        mb.box((w + 2.0, 2.2, 0.4), (q.x, q.y, F0 + 8.3 + 2.5 * (1 - f)), F.r(-rang, 0, 0), "Roof", 0.08)
    for k in range(4):
        q = F.p(-w / 2 + 2.5 + k * 3.7, d / 2 - 2.2, 0)
        mb.box((3.0, 2.8, 2.2), (q.x, q.y, F0 + 1.1), F.r(), "Wood_Plank", 0.1)
        crystal_cluster(mb, (q.x, q.y, F0 + 2.2), 0.6, "Crystal_Blue" if k % 2 else "Crystal_Purple", rng, 5)
        col_box("Shed", (3.0, 2.8, 3.4), (q.x, q.y, F0 + 1.7), F.r())
    mine_cart(mb, tuple(F.p(-3.0, -1.0, F0)), F.a, "Crystal_Blue", rng)
    q = F.p(-3.0, -1.0)
    col_box("Shed", (3.6, 2.6, 3.4), (q.x, q.y, F0 + 1.7), F.r())
    hanging_lantern(mb, tuple(F.p(0, 0, F0 + 9.0)), name="L_Shed", chain=1.5)
    mb.finish()


def build():
    rng = random.Random(909)
    plaza_and_paths(rng)
    shop(rng)
    # cabanas: oeste (entre trilho e penhasco) e leste (margem)
    cabin("West_A", -84.0, -4.0, D(-90), rng)        # porta para leste
    cabin("West_B", -94.0, 20.0, D(-90), rng, 12.0, 11.0, "Roof_Red")
    cabin("West_C", -64.0, 26.0, D(0), rng, 12.0, 10.0)   # porta para sul
    cabin("East_A", 114.0, -6.0, D(90), rng)          # porta para oeste
    cabin("East_B", 116.0, 18.0, D(90), rng, 12.0, 11.0, "Roof_Red")
    weigh_station(rng)
    crystal_shed(rng)
