# fm_konoha - TRANSICAO PARA A PRIMEIRA ILHA: torii Naruto -> Passo da Folha (canion) -> ponte suspensa sobre a
# garganta -> Grande Portao de Konoha (WORLD_EXIT) -> mirante com a trilha descendo para a ilha (WORLD_ENTRY)
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, col_ramp, marker, light, resample, bezier
from fm_parts import (Frame, cliff_band, lantern, sakura, pine, bush, fence, pave_poly, rock_scatter, P3, frustum)
import fm_layout as L

C = "06_PORTALS"
T = L.TERR
W = 14.0   # largura do caminho


def path_pts():
    kp = [Vector((x, y, T)) for x, y in L.KONOHA_PATH]
    # suaviza a polilinha
    out = [kp[0]]
    for a, b, c in zip(kp, kp[1:], kp[2:]):
        out += bezier((a + b) / 2, b, b, (b + c) / 2, 6)[1:]
    out.append(kp[-1])
    return resample(out, 2.0)


def side_of(pts, i):
    j = min(i + 1, len(pts) - 1)
    k = max(i - 1, 0)
    t = (pts[j] - pts[k]).normalized()
    return t, Vector((-t.y, t.x, 0))


def approach(rng):
    """patio atras do torii Naruto ate a boca do canion: sando de lajes, segundo torii, toro, quadro de avisos,
    bambuzal e varal de lanternas de papel (profundidade: torii grande -> torii menor -> lanternas -> canion)"""
    import fm_portal_kit as K
    x0 = L.KONOHA_PATH[0][0]
    y_back = L.PORTAL_Y + 5.4       # fundo da plataforma do portal Naruto
    ap = MB("KONOHA_Torii_Approach", C, rng)
    K.flag_floor(ap, [(x0 - 4.2, y_back - 0.4), (x0 + 4.2, y_back - 0.4), (x0 + 4.2, 134.0), (x0 - 4.2, 134.0)], T - 0.2,
                 rng, "Stone_Light", "Stone_Paving", tile=2.8, h=0.42, bevel=0.1, base=False)
    for s in (-1, 1):
        for k in range(5):
            y = y_back + 1.2 + k * 3.1
            ap.box((0.5, 2.4, 0.3), (x0 + s * 4.55, y, T + 0.05), (0, 0, rng.uniform(-0.05, 0.05)), "Stone_Dark", 0.05)
    # segundo torii (menor) na boca do canion
    ty = 123.6
    for s in (-1, 1):
        x = x0 + s * 7.9
        ap.cyl(1.05, 0.9, (x, ty, T + 0.45), (0, 0, 0), "Stone_Dark", 10, bevel=0.1)
        ap.cyl(0.78, 14.2, (x, ty, T + 7.1), (0, 0, 0), "P_Naruto_Red", 10, r2=0.68, bevel=0.05)
        ap.cyl(0.9, 0.8, (x, ty, T + 1.3), (0, 0, 0), "Wood_Dark", 10, bevel=0.0)
        col_box("Konoha", (1.7, 1.7, 14.0), (x, ty, T + 7.0))
    ap.box((19.0, 0.9, 1.0), (x0, ty, T + 11.4), (0, 0, 0), "P_Naruto_Red", 0.1)
    kas = [Vector((x0 + x, ty, T + 14.4 + 0.02 * x * x)) for x in range(-11, 12, 2)]
    ap.sweep(kas, [(-0.9, -0.7), (0.9, -0.7), (1.0, 0.6), (-1.0, 0.6)], "Wood_Dark", True, up=(0, 0, 1))
    ap.sweep([p + Vector((0, 0, -1.3)) for p in kas[1:-1]], [(-0.7, -0.55), (0.7, -0.55), (0.7, 0.55), (-0.7, 0.55)],
             "P_Naruto_Red", True, up=(0, 0, 1))
    ap.box((1.6, 0.9, 2.0), (x0, ty - 0.1, T + 12.9), (0, 0, 0), "Wood_Dark", 0.1)
    # toro de pedra no patio
    for s in (-1, 1):
        x, y = x0 + s * 10.6, y_back + 2.8
        K.toro(ap, (x, y, T), 0.95, "Stone_Light", "Stone_Dark", name="L_Konoha_Toro_%d" % (s + 1))
        col_box("Konoha", (2.4, 2.4, 6.2), (x, y, T + 3.1))
    # fileira de lanternas de papel pendurada no nuki do segundo torii (festival)
    for dx in (-5.2, -2.6, 0.0, 2.6, 5.2):
        K.chochin(ap, (x0 + dx, ty - 0.2, T + 10.9), r=0.62, h=1.2, paper="Lantern_Glow", cap="P_Naruto_Red",
                  hang=0.35 + 0.25 * abs(dx) / 5.2, n=6)
    light("L_Konoha_Festival", "POINT", (x0, ty - 1.5, T + 9.0), 260, (1.0, 0.6, 0.3), 1.0)
    # bambuzal na borda oeste
    K.bamboo(ap, (x0 - 10.8, 136.5, T), rng, n=5, h=(10.0, 15.0))
    col_box("Konoha", (2.6, 2.6, 8.0), (x0 - 10.8, 136.5, T + 4.0))
    ap.finish()


def build():
    rng = random.Random(808)
    approach(random.Random(809))
    pts = path_pts()
    g0, g1 = L.KONOHA_GORGE
    mb = MB("KONOHA_Pass_Path", C, rng)
    # leito da trilha (terra batida com lajes) e verges de grama; interrompido na garganta
    for i, p in enumerate(pts[:-1]):
        q = pts[i + 1]
        if g0 - 1 < (p.y + q.y) / 2 < g1 + 1:
            continue
        t, s = side_of(pts, i)
        a = math.atan2(t.y, t.x)
        c = (p + q) / 2
        L_ = (q - p).length + 0.3
        mb.box((L_, W + 12, 30.0), (c.x, c.y, T - 15.35), (0, 0, a), "Cliff_Rock_Dark", 0.0)
        mb.box((L_, W + 12, 0.6), (c.x, c.y, T - 0.3), (0, 0, a), "Grass", 0.0)
        mb.box((L_, W - 2, 0.5), (c.x, c.y, T - 0.05), (0, 0, a), "Dirt", 0.0)
        if i % 2 == 0:
            for k in (-1, 1):
                off = s * k * rng.uniform(1.0, 3.2)
                mb.box((rng.uniform(1.8, 2.6), rng.uniform(1.6, 2.4), 0.35), (c.x + off.x, c.y + off.y, T + 0.25),
                       (0, 0, rng.uniform(0, 3)), "Stone_Paving", 0.1)
        col_box("Konoha", (L_, W + 12, 4), (c.x, c.y, T - 2), (0, 0, a), "Floor")
    mb.finish()

    # paredes do canion (as duas margens, face para dentro), interrompidas so na garganta
    cw = MB("KONOHA_Canyon_Walls", "02_TERRAIN", rng)
    for side in (-1, 1):
        wall = []
        for i, p in enumerate(pts):
            t, s = side_of(pts, i)
            wall.append(p + s * side * (W / 2 + 6.5))
        cliff_band(cw, wall, T - 40, 64, rng, depth=3, rmin=4.5, rmax=7.5, step=6.5, face_side=-side,
                   top_fn=lambda c: 60 + 10 * math.sin(c.y * 0.05))
        for a, b in zip(wall[::6], wall[6::6] + [wall[-1]]):
            d = b - a
            if d.length < 0.5:
                continue
            cc = (a + b) / 2
            t = d.normalized()
            n = Vector((-t.y, t.x, 0)) * side
            cc = cc + n * 2.0
            col_box("Konoha", (d.length + 2, 5, 50), (cc.x, cc.y, T + 20), (0, 0, math.atan2(d.y, d.x)))
    cw.finish()

    # garganta: abismo com nevoa e cachoeirinha lateral
    gm = MB("KONOHA_Gorge", "02_TERRAIN", rng)
    gc = [p for p in pts if g0 - 2 < p.y < g1 + 2]
    mid = gc[len(gc) // 2]
    for i in range(14):
        gm.ico(rng.uniform(4, 8), (mid.x + rng.uniform(-18, 18), mid.y + rng.uniform(-10, 10), T - 34 + rng.uniform(-4, 4)),
               "Foam", 1, (1.4, 1.0, 0.5), jitter=0.2)
    # bordas da garganta: rochas de encosto e cercas
    for yy in (g0, g1):
        idx = min(range(len(pts)), key=lambda k: abs(pts[k].y - yy))
        p = pts[idx]
        t, s = side_of(pts, idx)
        for k in (-1, 1):
            q = p + s * k * (W / 2 + 1.5)
            gm.rock((q.x, q.y, T + 0.6), (4.0, 3.5, 3.0), "Cliff_Rock", 1)
    gm.finish()
    for side in (-1, 1):
        # parede de rocha continua dentro da garganta (fecha o vao lateral)
        cp = []
        for p in gc:
            idx = pts.index(p)
            t, s = side_of(pts, idx)
            cp.append(p + s * side * (W / 2 + 6.5))
        gm2 = MB("KONOHA_Gorge_Side_%s" % ("W" if side < 0 else "E"), "02_TERRAIN", rng)
        cliff_band(gm2, cp, T - 60, 62, rng, depth=2, rmin=5, rmax=8, step=6, face_side=-side)
        gm2.finish()

    # ponte suspensa: postes, cabos, tabuas, corrimao de corda
    br = MB("KONOHA_Rope_Bridge", C, rng)
    ia = min(range(len(pts)), key=lambda k: abs(pts[k].y - (g0 - 1.5)))
    ib = min(range(len(pts)), key=lambda k: abs(pts[k].y - (g1 + 1.5)))
    A, B = pts[ia], pts[ib]
    d = B - A
    Lb = d.length
    ang = math.atan2(d.y, d.x)
    side = Vector((-math.sin(ang), math.cos(ang), 0))
    sag = 2.2
    bw = 7.0
    n = int(Lb / 1.1)
    deck = []
    for i in range(n + 1):
        f = i / n
        p = A + d * f
        p.z = T - sag * 4 * f * (1 - f)
        deck.append(p)
        br.box((0.9, bw, 0.35), (p.x, p.y, p.z - 0.15), (0, 0, ang + rng.uniform(-0.03, 0.03)), "Wood_Plank", 0.05)
    for k in (-1, 1):
        base = [p + side * k * (bw / 2) for p in deck]
        br.tube([p + Vector((0, 0, -0.4)) for p in base], 0.22, "Rope", 6)
        top = [p + Vector((0, 0, 3.4 + 1.2 * (1 - 4 * (i / n) * (1 - i / n)))) for i, p in enumerate(base)]
        br.tube(top, 0.26, "Rope", 6)
        for i in range(0, n + 1, 2):
            br.rod(base[i], top[i], 0.07, "Rope", 4)
        for P in (A, B):
            q = P + side * k * (bw / 2 + 0.6)
            br.box((1.2, 1.2, 6.5), (q.x, q.y, T + 3.2), (0, 0, ang), "Wood_Dark", 0.12)
            br.box((1.6, 1.6, 0.6), (q.x, q.y, T + 6.6), (0, 0, ang), "P_Naruto_Red", 0.1)
    br.finish()
    k6 = 6
    for i in range(k6):
        f0, f1 = i / k6, (i + 1) / k6
        pa = A + d * f0
        pb = A + d * f1
        pa.z = T - sag * 4 * f0 * (1 - f0)
        pb.z = T - sag * 4 * f1 * (1 - f1)
        col_ramp("Konoha", pa, pb, bw, 1.0)
    for k in (-1, 1):
        c = (A + B) / 2 + side * k * (bw / 2 + 0.3)
        col_box("Konoha", (Lb + 2, 0.6, 6), (c.x, c.y, T + 1.5), (0, 0, ang))

    # portoes intermediarios (torii pequenos), lanternas, sakura e pinheiros no caminho
    dec = MB("KONOHA_Pass_Decor", C, rng)
    for yy in (150.0, 180.0, 250.0):
        idx = min(range(len(pts)), key=lambda k: abs(pts[k].y - yy))
        p = pts[idx]
        t, s = side_of(pts, idx)
        a = math.atan2(t.y, t.x)
        for k in (-1, 1):
            q = p + s * k * (W / 2 + 0.8)
            dec.cyl(0.7, 13.0, (q.x, q.y, T + 6.5), (0, 0, 0), "P_Naruto_Red", 10, bevel=0.05)
            dec.cyl(1.0, 0.8, (q.x, q.y, T + 0.4), (0, 0, 0), "Stone_Dark", 10, bevel=0.1)
            col_box("Konoha", (1.6, 1.6, 13.0), (q.x, q.y, T + 6.5))
        dec.beam(p - s * (W / 2 + 2.6) + Vector((0, 0, 11.0)), p + s * (W / 2 + 2.6) + Vector((0, 0, 11.0)),
                 1.1, 1.0, "P_Naruto_Red", 0.1)
        dec.beam(p - s * (W / 2 + 3.6) + Vector((0, 0, 13.3)), p + s * (W / 2 + 3.6) + Vector((0, 0, 13.3)), 1.4, 1.2,
                 "Wood_Dark", 0.12)
    for i in range(6, len(pts) - 4, 9):
        p = pts[i]
        if g0 - 4 < p.y < g1 + 4:
            continue
        t, s = side_of(pts, i)
        k = 1 if (i // 9) % 2 else -1
        q = p + s * k * (W / 2 + 2.0)
        lantern(dec, (q.x, q.y, T), math.atan2(-s.y * k, -s.x * k), name="L_Konoha_%03d" % i, h=6.5)
        col_box("Konoha", (1.4, 1.4, 8.0), (q.x, q.y, T + 4.0))
    for i in range(3, len(pts) - 2, 7):
        p = pts[i]
        if g0 - 6 < p.y < g1 + 6:
            continue
        t, s = side_of(pts, i)
        for k in (-1, 1):
            q = p + s * k * (W / 2 + rng.uniform(3.5, 5.5))
            if rng.random() < 0.35:
                sakura(dec, (q.x, q.y, T), rng.uniform(9, 12), rng)
            else:
                pine(dec, (q.x, q.y, T), rng.uniform(12, 18), rng)
    dec.finish()

    # GRANDE PORTAO DE KONOHA (fim do lobby): pilares, verga com telhado, folhas do portao abertas, emblema folha
    gate_y = L.KONOHA_GATE_Y
    idx = min(range(len(pts)), key=lambda k: abs(pts[k].y - gate_y))
    gp = pts[idx]
    t, s = side_of(pts, idx)
    a = math.atan2(t.y, t.x)
    gt = MB("KONOHA_Great_Gate", C, rng)
    GW = W + 6.0
    for k in (-1, 1):
        q = gp + s * k * (GW / 2 + 1.5)
        gt.box((3.2, 3.2, 26.0), (q.x, q.y, T + 13.0), (0, 0, a), "Wood_Dark", 0.25)
        gt.box((4.2, 4.2, 2.0), (q.x, q.y, T + 1.0), (0, 0, a), "Stone_Dark", 0.2)
        # folhas abertas (giradas 75 graus para fora, no sentido da saida)
        h = gp + s * k * (GW / 2 - 0.5) + t * 0.5
        leaf_c = h + t * 4.5 + s * k * -1.0
        gt.box((0.8, 9.0, 20.0), (leaf_c.x, leaf_c.y, T + 10.2), (0, 0, a + k * D(15)), "Wood_Plank", 0.12)
        for zz in (T + 4.0, T + 16.0):
            gt.box((1.0, 9.2, 0.8), (leaf_c.x, leaf_c.y, zz), (0, 0, a + k * D(15)), "Metal_Dark", 0.05)
        col_box("Konoha", (3.4, 3.4, 26.0), (q.x, q.y, T + 13.0), (0, 0, a))
        col_box("Konoha", (1.0, 9.0, 20.0), (leaf_c.x, leaf_c.y, T + 10.2), (0, 0, a + k * D(15)))
    top = gp + Vector((0, 0, 26.5))
    gt.box((3.0, GW + 10.0, 2.4), (top.x, top.y, top.z), (0, 0, a), "Wood_Dark", 0.2)
    gt.box((7.0, GW + 14.0, 1.0), (top.x, top.y, top.z + 1.8), (0, 0, a), "Roof_Red", 0.2)
    gt.box((4.4, GW + 11.0, 1.0), (top.x, top.y, top.z + 2.8), (0, 0, a), "Roof_Red", 0.2)
    gt.box((1.2, GW + 12.0, 1.0), (top.x, top.y, top.z + 3.6), (0, 0, a), "Wood_Dark", 0.1)
    # emblema folha-espiral (vermelho) sobre a verga
    ec = gp - t * 1.8 + Vector((0, 0, 22.5))
    gt.cyl(3.4, 0.6, ec, (D(90), 0, a - math.pi / 2), "Emblem_Cream", 20, bevel=0.1)
    spiral = []
    for i in range(24):
        tt = i * 0.45
        spiral.append(ec - t * 0.4 + s * math.cos(tt) * 0.25 * tt + Vector((0, 0, math.sin(tt) * 0.25 * tt)))
    gt.tube(spiral, 0.28, "P_Naruto_Red", 6)
    gt.finish()
    light("L_Konoha_Gate", "POINT", tuple(gp - t * 6 + Vector((0, 0, 8))), 800, (1.0, 0.7, 0.4), 2.0)
    marker("WORLD_EXIT_Naruto", tuple(gp), (0, 0, a), 4, "ARROWS",
           props={"destino": "Konoha", "tipo": "saida_continua", "nota": "passar o portao = entrar na ilha 1"})
    # mirante alem do portao (lado Konoha): trilha desce em rampa ate o ponto de chegada
    end = pts[-1]
    marker("WORLD_ENTRY_Naruto", tuple(end + t * 4.0), (0, 0, a), 4, "ARROWS",
           props={"origem": "Lobby", "nota": "ponto de chegada vindo do lobby; alinhar com a entrada da Area 1"})
    ov = MB("KONOHA_Overlook", C, rng)
    ov.box((14.0, W + 6, 1.0), (end.x + t.x * 7, end.y + t.y * 7, T - 0.5), (0, 0, a), "Stone_Paving", 0.2)
    fence(ov, "Konoha", [end + t * 14 + s * (W / 2 + 2), end + t * 14 - s * (W / 2 + 2)], h=3.2, post_step=3.0)
    ov.finish()
    col_box("Konoha", (14.0, W + 6, 4.0), (end.x + t.x * 7, end.y + t.y * 7, T - 2.0), (0, 0, a), "Floor")
    for k in (-1, 1):
        q = end + t * 7 + s * k * (W / 2 + 3)
        col_box("Konoha", (14.0, 1.0, 6.0), (q.x, q.y, T + 3.0), (0, 0, a))
