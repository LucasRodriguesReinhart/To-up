# fm_mine - MINA (face NE do macico SW) + TRILHOS (mina -> transporte -> ala de recebimento da forja)
# Passe de acabamento:
#  - boca com cara de mina: portico de madeira AVANCADO 3,5 studs (a madeira com cordas vira a silhueta), massas de
#    rocha laterais finas e irregulares sobrepondo os esteios, anel de rocha escura por dentro da boca, cristais e luz
#    fria saindo do tunel; patio vestido (rejeito, mesa de triagem, escoras, rack de ferramentas, barril d'agua, placa
#    de perigo, dinamite, sino, carrinho tombado) e altar de mineiro no pe do macico
#  - tunel com ritmo claro/escuro (lanternas de gaiola a cada 2 escoramentos, luz fria fraca), entulho no pe das
#    paredes, tabuas de revestimento atras das escoras, poca d'agua, nicho de ferramentas, veios de cristal diagonais e
#    teto de rocha irregular; cristal gigante da camara encostado na parede, com colisao
#  - trilho com leito de lastro de borda recortada, pranchas nos cruzamentos com as estradas, desvio com para-choque
#    e carrinhos na balanca, fragmentos de cristal e minerio ao longo da linha
import math, random
import bpy
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, bezier, resample, point_in_poly
from fm_parts import (Frame, cliff_band, rails, mine_cart, crystal_cluster, lantern, hanging_lantern, banner,
                      crate, barrel, masonry_wall, rock_scatter, P3, emblem_pickaxe)
import fm_layout as L
import fm_props_kit as K
from fm_props_kit import PMB, V

F0 = L.FLOOR
PORTAL_X = -5.7      # face do portico em x local (antes -2.2): 3,5 studs para fora da rocha


def tunnel_frame():
    mx, my = L.MINE_MOUTH
    return Frame(mx, my, 0.0, L.MINE_DIR)   # +x local = para dentro do tunel, +y local = esquerda


def to_local(F, p):
    dx, dy = p[0] - F.o.x, p[1] - F.o.y
    c, s = math.cos(F.a), math.sin(F.a)
    return dx * c + dy * s, -dx * s + dy * c


def along(pts, d):
    """ponto e tangente a distancia d ao longo da polilinha (segue a curva do tunel)"""
    acc = 0.0
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        seg = (b - a).length
        if seg < 1e-6:
            continue
        if acc + seg >= d or k == len(pts) - 2:
            f = min(1.0, max(0.0, (d - acc) / seg))
            return a.lerp(b, f), (b - a).normalized()
        acc += seg
    return pts[-1], (pts[-1] - pts[-2]).normalized()


def surf_hit(obs, origin, direction, maxd=30.0):
    """raio contra malhas ja finalizadas: (ponto, normal virada para o raio) mais proximo, ou None"""
    best = None
    origin = Vector(origin)
    direction = Vector(direction).normalized()
    for ob in obs:
        if ob is None:
            continue
        mi = ob.matrix_world.inverted()
        ok, loc, nrm, idx = ob.ray_cast(mi @ origin, (mi.to_3x3() @ direction).normalized(), distance=maxd)
        if not ok:
            continue
        w = ob.matrix_world @ loc
        dist = (w - origin).length
        if best is None or dist < best[0]:
            n = (ob.matrix_world.to_3x3().inverted().transposed() @ nrm).normalized()
            if n.dot(direction) > 0:
                n = -n
            best = (dist, w, n)
    return None if best is None else (best[1], best[2])


# caminho do tunel em coordenadas locais (entra reto e faz curva a esquerda ate a camara)
TUN = [(-3.0, 0.0), (10.0, 0.0), (22.0, 0.0), (30.0, 2.5), (37.0, 7.0)]
CHAMBER = (46.0, 12.0, 12.5)   # centro local e raio


def build():
    rng = random.Random(505)
    F = tunnel_frame()
    W = L.MINE_W
    H = L.MINE_H
    zt = F0 + H
    mb = PMB("MINE_Tunnel_Shell", "04_MINE", rng, vmax=1, remap={"Cliff_Rock": "Cliff_Rock_Dark"})
    tun = [F.p(x, y, 0) for x, y in TUN]
    fine = resample(tun, 3.0)
    # piso de terra batida + paredes de rocha irregular + teto de rocha (blocos irregulares, nao uma caixa)
    for i, p in enumerate(fine):
        j = min(i + 1, len(fine) - 1)
        k = max(i - 1, 0)
        t = (fine[j] - fine[k]).normalized()
        a = math.atan2(t.y, t.x)
        side = Vector((-t.y, t.x, 0))
        mb.box((3.4, W + 1.0, 1.0), (p.x, p.y, F0 - 0.3), (0, 0, a), "Dirt", 0.1)
        back = t * (1.4 if i == 0 else 0.0)        # o 1o anel recua: por dentro da boca fica o anel de rocha escura
        for s in (-1, 1):
            base = p + back + side * s * (W / 2 + 2.2)
            mb.box((3.4, 3.4, H + 4), (base.x, base.y, F0 + (H + 4) / 2 - 1), (0, 0, a), "Cliff_Rock_Dark", 0.3)
            for zz in (F0 + 2.0, F0 + 6.5, F0 + 11.0):
                q = p + side * s * (W / 2 + rng.uniform(0.2, 0.9))
                mb.rock((q.x, q.y, zz), (rng.uniform(2.6, 4.0), rng.uniform(2.0, 3.0), rng.uniform(3.8, 5.2)),
                        "Cliff_Rock" if (rng.random() > 0.4 and i > 0) else "Cliff_Rock_Dark", 1, (0, 0, a))
        pc = p + back
        mb.box((3.4, W + 6.0, 3.0), (pc.x, pc.y, zt + 1.5), (0, 0, a), "Cliff_Rock_Dark", 0.2)
        for kk in range(2 if i else 3):
            q = p + side * rng.uniform(-W * 0.32, W * 0.32) + t * rng.uniform(-0.8, 0.8)
            sz = rng.uniform(1.4, 2.4)
            mb.rock((q.x, q.y, zt - rng.uniform(-0.3, 0.5)), (rng.uniform(2.6, 3.8), rng.uniform(3.6, 5.6), sz),
                    "Cliff_Rock_Dark" if rng.random() < 0.7 else "Cliff_Rock", 1, (0, 0, a + rng.uniform(-0.4, 0.4)),
                    flat_bottom=False)
        if i == 0:
            # anel de rocha escura por dentro da boca (atras dos esteios, irregular)
            for s in (-1, 1):
                for zz, hz in ((F0 + 2.4, 5.0), (F0 + 7.2, 5.4), (F0 + 11.8, 5.0)):
                    q = p - t * 1.2 + side * s * (W / 2 + rng.uniform(0.5, 1.2))
                    mb.rock((q.x, q.y, zz), (rng.uniform(2.8, 3.6), rng.uniform(2.4, 3.2), hz), "Cliff_Rock_Dark", 1,
                            (0, 0, a + rng.uniform(-0.3, 0.3)))
            for yy in (-W * 0.33, 0.0, W * 0.33):
                q = p - t * 1.2 + side * yy
                mb.rock((q.x, q.y, zt + 0.2), (3.0, rng.uniform(4.2, 5.4), rng.uniform(1.8, 2.4)), "Cliff_Rock_Dark",
                        1, (0, 0, a + rng.uniform(-0.3, 0.3)), flat_bottom=False)
    # camara de cristais
    cxl, cyl, cr = CHAMBER
    cc = F.p(cxl, cyl, 0)
    mb.cyl(cr + 1.0, 1.0, (cc.x, cc.y, F0 - 0.3), (0, 0, 0), "Dirt", 16, bevel=0.1)
    n = 16
    to_tun = (F.p(37.0, 7.0, 0) - cc).normalized()
    for i in range(n):
        a = i / n * math.tau
        dirv = Vector((math.cos(a), math.sin(a), 0))
        # a abertura da camara para o tunel fica livre
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
    for i in range(7):     # teto da camara: blocos pendentes irregulares
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, cr - 3)
        mb.rock((cc.x + math.cos(a) * r, cc.y + math.sin(a) * r, zt + 1.4), (rng.uniform(4, 6), rng.uniform(4, 6),
                rng.uniform(1.6, 2.6)), "Cliff_Rock_Dark", 1, (0, 0, a), flat_bottom=False)
    shell = mb.finish()

    # escoramento de madeira a cada 5 studs (pares de esteios + chapeu + maos-francesas) + revestimento de tabuas
    tb = PMB("MINE_Timber_Sets", "04_MINE", rng, vmax=1,
             remap={"Metal_Iron": "Metal_Dark", "Coal_Rock": "Cliff_Rock_Dark", "Cliff_Rock": "Cliff_Rock_Dark"})
    sets = resample(tun, 5.0)
    inner = list(range(1, len(sets) - 1))
    # veios de cristal: distancia ao longo do tunel (acompanha a curva), lado, quantidade, material
    VEINS = ((10.5, -1, 4, "Crystal_Blue"), (19.0, 1, 5, "Crystal_Blue"), (27.5, -1, 6, "Crystal_Purple"),
             (35.0, 1, 4, "Crystal_Blue"))
    vein_c = []
    for (dv, s, nv, m) in VEINS:
        p, t = along(tun, dv + nv * 0.45)
        vein_c.append((s, p + Vector((-t.y, t.x, 0)) * s * (W / 2)))
    for i in inner:
        p = sets[i]
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
            K.cage_lamp(tb, (p.x, p.y, F0 + H - 1.45), "L_Mine_%02d" % i, 150, drop=0.5)
        # tabuas de revestimento entre este escoramento e o proximo (atras das escoras, falhadas)
        if i + 1 < len(sets) - 1:
            p2 = sets[i + 1]
            d = p2 - p
            mid = (p + p2) / 2
            ang = math.atan2(d.y, d.x)
            for s in (-1, 1):
                q = mid + side * s * (W / 2 - 0.25)
                if any(vs == s and (q - vc).length < 3.4 for vs, vc in vein_c):
                    continue                     # vao sem tabuas: o veio sai da rocha, nao da madeira
                for zb in (F0 + 1.1, F0 + 2.3, F0 + 3.5, F0 + 4.7, F0 + 5.9):
                    if rng.random() < 0.22:
                        continue
                    tb.box((d.length + 0.3, 0.28, 1.05), (q.x, q.y, zb), (rng.uniform(-0.03, 0.03), 0, ang),
                           "Wood_Plank", 0.0)
    # cristais: veios diagonais de 3-6 nas paredes do tunel e da camara + tufos no pe das paredes
    up = Vector((0, 0, 1))
    for (dv, s, nv, m) in VEINS:
        for kk in range(nv):
            p, t = along(tun, dv + kk * 0.9)
            side = Vector((-t.y, t.x, 0))
            o = p + Vector((0, 0, F0 + 2.4 + kk * 1.15))
            h = surf_hit([shell], o, side * s, W)            # assenta na rocha da parede (nao flutua)
            q, n = h if h else (o + side * s * (W / 2 - 0.3), -side * s)
            ax = (n + up * 0.55 + t * 0.3).normalized()
            K.crystal(tb, q - n * 0.1, rng.uniform(1.5, 2.3), rng.uniform(0.3, 0.42), ax, m, rng.uniform(0, 6))
    for i, p in enumerate(fine[3::2]):
        s = 1 if i % 2 else -1
        j = min(fine.index(p) + 1, len(fine) - 1)
        t = (fine[j] - p).normalized() if (fine[j] - p).length > 0 else Vector((1, 0, 0))
        side = Vector((-t.y, t.x, 0))
        q = p + side * s * (W / 2 - 1.2)
        K.crystals(tb, (q.x, q.y, F0 + 0.2), rng.uniform(0.55, 0.8), rng, 4, "Crystal_Blue")
    for i in range(9):
        a = i / 9 * math.tau + 0.3
        q = cc + Vector((math.cos(a), math.sin(a), 0)) * (cr - 2.2)
        K.crystals(tb, (q.x, q.y, F0 + 0.2), rng.uniform(0.8, 1.2), rng, 5,
                   "Crystal_Blue" if i % 3 else "Crystal_Purple")
    # veios na parede da camara
    # (longe da abertura para o tunel ~74 graus, das galerias interditadas e do cristal gigante)
    for a0 in (D(128), D(308)):
        for kk in range(5):
            a = a0 + kk * 0.09
            dirv = Vector((math.cos(a), math.sin(a), 0))
            o = cc + Vector((0, 0, F0 + 3.0 + kk * 1.3))
            h = surf_hit([shell], o, dirv, cr + 4.0)
            q, n = h if h else (o + dirv * (cr - 0.6), -dirv)
            ax = (n + up * 0.7).normalized()
            K.crystal(tb, q - n * 0.1, rng.uniform(1.7, 2.5), 0.4, ax, "Crystal_Purple" if kk % 2 else
                      "Crystal_Blue", rng.uniform(0, 6))
    # cristal gigante: encostado na parede do fundo (longe da entrada), com colisao; o marcador fica livre
    back_dir = -to_tun
    gc = cc + back_dir * (cr - 4.6)
    K.crystals(tb, (gc.x, gc.y, F0 + 0.2), 2.3, rng, 6, "Crystal_Blue", m2="Crystal_Purple")
    col_box("Mine", (6.0, 6.0, 10.0), (gc.x, gc.y, F0 + 5.0), (0, 0, math.atan2(back_dir.y, back_dir.x)))
    # entulho no pe das paredes (fora da faixa de caminhada), poca d'agua e nicho de ferramentas
    for i, p in enumerate(fine[1:], 1):
        j = min(i + 1, len(fine) - 1)
        t = (fine[j] - fine[i - 1]).normalized()
        side = Vector((-t.y, t.x, 0))
        for s in (-1, 1):
            if rng.random() < 0.35:
                continue
            q = p + side * s * (W / 2 - 1.0 - rng.uniform(0.0, 0.5)) + t * rng.uniform(-1.2, 1.2)
            K.ore_bits(tb, (q.x, q.y, F0 + 0.2), 0.9, rng.randint(2, 3), rng, "Cliff_Rock_Dark", 0.45, 0.9)
    pd = F.p(13.5, -4.4, F0 + 0.23)
    tb.cyl(1.7, 0.05, pd, (0, 0, 0.3), "Water", 9, bevel=0.0)
    tb.cyl(1.0, 0.05, pd + F.p(1.6, -0.5) - F.p(0, 0), (0, 0, 0.8), "Water", 7, bevel=0.0)
    Fn = Frame(*F.p(9.5, -(W / 2 - 0.55), F0)[:2], F0, F.a)
    for sx in (-1.4, 1.4):
        tb.box((0.45, 0.45, 4.6), Fn.p(sx, 0, 2.3), Fn.r(), "Wood_Dark", 0.0)
    for zz in (1.6, 3.2):
        tb.box((3.3, 0.9, 0.2), Fn.p(0, 0.2, zz), Fn.r(), "Wood_Plank", 0.0)
    tb.box((3.5, 0.5, 0.35), Fn.p(0, 0, 4.7), Fn.r(), "Wood_Dark", 0.0)
    K.lamp(tb, Fn.p(-0.7, 0.2, 3.95), None, s=0.6)
    K.crystals(tb, Fn.p(0.6, 0.2, 3.3), 0.25, rng, 3, "Crystal_Blue")
    K.keg(tb, tuple(Fn.p(0.6, 0.35, 1.7)), 0.35, 0.8)
    K.pickaxe(tb, Fn.p(1.9, 1.0, 0.0), Fn.p(2.2, 0.3, 3.4), Fn.p(1, 0) - Fn.p(0, 0), 0.9)
    K.shovel(tb, Fn.p(-2.0, 1.1, 0.0), Fn.p(-2.2, 0.35, 3.5))
    light("L_Mine_Chamber", "POINT", (cc.x, cc.y, F0 + 8), 700, (0.35, 0.6, 1.0), 3.0)
    light("L_Mine_Tunnel", "POINT", tuple(F.p(18, 0, F0 + 8)), 150, (0.45, 0.65, 1.0), 2.0)
    # galerias que continuam (interditadas com tabuas e placa de perigo)
    for ga in (D(30), D(-40)):
        dirv = Vector((math.cos(ga + L.MINE_DIR + 0.5), math.sin(ga + L.MINE_DIR + 0.5), 0))
        q = cc + dirv * (cr - 0.5)
        a = math.atan2(dirv.y, dirv.x)
        for k in range(5):
            tb.box((0.4, 7.0, 0.9), (q.x, q.y, F0 + 1.5 + k * 1.8), (rng.uniform(-0.1, 0.1), 0, a + math.pi / 2),
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
        if dirv.dot(to_tun) > 0.8:
            continue
        q = cc + dirv * (cr + 1.0)
        col_box(A, (2.5, 2 * (cr + 1) * math.sin(math.pi / 12) + 1, H + 2), (q.x, q.y, F0 + (H + 2) / 2), (0, 0, a))
    col_box(A, (2 * cr + 4, 2 * cr + 4, 2), (cc.x, cc.y, zt + 1))
    # zona da camara: ~5 studs para o lado da entrada (o cristal gigante ficou na parede do fundo)
    zdir = Vector((-86.0, -77.0, 0)) - Vector((cc.x, cc.y, 0))
    zp = cc + zdir.normalized() * 5.0
    marker("MINE_Interior_Zone", (zp.x, zp.y, F0), (0, 0, 0), 6, "CIRCLE", props={"zone": "mina_tutorial"})

    entrance(rng, F)
    build_rails(rng, F)


def entrance(rng, F):
    """boca da mina: portico de madeira macica avancado, marquise, rocha irregular em volta, patio vestido"""
    W = L.MINE_W
    H = L.MINE_H
    X0 = PORTAL_X
    dx = X0 - (-2.2)
    mb = PMB("MINE_Entrance_Portal", "04_MINE", rng, vmax=1,
              remap={"Metal_Iron": "Metal_Dark", "Coal_Rock": "Cliff_Rock_Dark", "Cliff_Rock": "Cliff_Rock_Dark",
                     "Stone_Dark": "Cliff_Rock_Dark", "Stone_Light": "Cliff_Rock_Dark", "Dirt_B": "Dirt",
                     "Cloth_Canvas": "Rope", "Metal_Brass": "Metal_Dark", "Water": "Metal_Dark",
                     "Forge_Emissive": "Lantern_Glow", "Crystal_Purple": "Crystal_Blue", "Cloth_Red": "Wood_Red"})
    # portico: 2 esteios grossos (levemente fora de prumo), verga dupla, maos-francesas, amarras de corda
    for s in (-1, 1):
        q = F.p(X0, s * (W / 2 + 0.6), F0)
        mb.box((2.2, 2.2, H + 3.5), (q.x, q.y, F0 + (H + 3.5) / 2), F.r(s * 0.015, 0, 0), "Wood_Dark", 0.2)
        mb.box((3.0, 3.0, 1.1), (q.x, q.y, F0 + 0.55), F.r(0, 0, 0.12 * s), "Stone_Dark", 0.2)
        for zz in (F0 + 4.0, F0 + H - 1.0):
            mb.cyl(1.35, 0.7, (q.x, q.y, zz), F.r(), "Rope", 8, bevel=0.0)
        mb.beam(F.p(X0, s * (W / 2 + 0.6), F0 + H - 3.5), F.p(X0, s * (W / 2 - 3.0), F0 + H + 1.4), 1.0, 1.0,
                "Wood_Dark", 0.1)
        # braco de ferro com lanterna de gaiola na face externa do esteio
        mb.beam(F.p(X0 - 1.0, s * (W / 2 + 0.6), F0 + 9.8), F.p(X0 - 2.7, s * (W / 2 + 0.6), F0 + 9.8), 0.3, 0.3,
                "Metal_Dark", 0.0)
        mb.beam(F.p(X0 - 1.0, s * (W / 2 + 0.6), F0 + 8.6), F.p(X0 - 2.2, s * (W / 2 + 0.6), F0 + 9.7), 0.22, 0.22,
                "Metal_Dark", 0.0)
        K.cage_lamp(mb, F.p(X0 - 2.5, s * (W / 2 + 0.6), F0 + 9.7), "L_MineGate_%d_Light" % (s + 1), 170, drop=0.35)
    mb.box((2.4, W + 7.0, 1.8), F.p(X0, 0, F0 + H + 2.2), F.r(0.012, 0, 0), "Wood_Dark", 0.2)
    mb.box((2.0, W + 5.0, 1.4), F.p(X0, 0, F0 + H + 0.7), F.r(), "Wood_Light", 0.15)
    for s in (-1, 1):
        mb.cyl(1.0, 0.5, F.p(X0, s * (W / 2 + 2.6), F0 + H + 2.2), F.r(0, D(90), 0), "Rope", 8, bevel=0.0)
    # marquise de tabuas inclinada para fora com vigas (acompanha o portico)
    for k in range(7):
        y = -W / 2 - 2.5 + k * (W + 5) / 6
        mb.beam(F.p(0.5 + dx, y, F0 + H + 3.4), F.p(-7.5 + dx, y, F0 + H + 1.2), 0.7, 0.8, "Wood_Dark", 0.08)
    for k in range(9):
        x = dx - k * 0.95
        z = F0 + H + 3.9 - (k * 0.95) * (2.2 / 8.0)
        mb.box((1.0, W + 7.2 - (1.2 if k % 3 == 1 else 0), 0.35), F.p(x, rng.uniform(-0.3, 0.3), z),
               F.r(0, math.atan2(2.2, 8.0), 0), "Wood_Plank", 0.06)
    # placa com picareta
    mb.box((0.5, 7.0, 2.4), F.p(X0 - 1.4, 0, F0 + H + 5.4), F.r(), "Wood_Dark", 0.15)
    emblem_pickaxe(mb, F.p(X0 - 1.7, 0, F0 + H + 5.4), F.a - math.pi / 2, s=0.45, normal_off=0.0)
    # cristais saindo da boca (chao; a rota da mina anda do lado +y, os maiores ficam do lado -y) + luz fria
    for (xl, yl, zl, s_, n_) in ((-1.0, -(W / 2 - 1.3), 0.0, 1.3, 5), (1.8, W / 2 - 1.3, 0.0, 0.7, 4),
                                 (4.5, -(W / 2 - 1.5), 0.0, 0.9, 4), (-8.4, -6.2, 0.0, 0.6, 4),
                                 (-10.6, -7.8, 0.0, 0.4, 3)):
        K.crystals(mb, F.p(xl, yl, F0 + zl + 0.1), s_, rng, n_, "Crystal_Blue")
    light("L_Mine_Mouth_Glow", "POINT", tuple(F.p(1.5, 0, F0 + 5.5)), 1800, (0.3, 0.55, 1.0), 2.5)

    # rocha em volta e por cima da boca: pontas da face, massas laterais finas sobre os esteios, faixa de cima
    fa, fb = L.MINE_FACE
    fa, fb = Vector((fa[0], fa[1], 0)), Vector((fb[0], fb[1], 0))
    mouth = Vector((L.MINE_MOUTH[0], L.MINE_MOUTH[1], 0))
    d = (fb - fa).normalized()
    # rocha em volta da boca mais escura (fuligem e umidade da mina): a boca le como buraco, nao como moldura clara;
    # tons fixos (sem sortear a variante clara da familia)
    ca = PMB("MINE_Face_Cliffs", "02_TERRAIN", rng, vmax=1,
             remap={"Cliff_Rock_Dark": "Cliff_Rock_Dark_B", "Cliff_Rock": "Cliff_Rock_C"})
    ea = mouth - d * (W / 2 + 9.5)
    eb = mouth + d * (W / 2 + 9.5)
    dk = dict(m="Cliff_Rock_Dark", m2="Cliff_Rock")
    # pontas da face: 2-3 massas menores e de topo irregular (antes um pilar unico de face lisa)
    cliff_band(ca, [fa - d * 1.5, mouth - d * (W / 2 + 6.0)], F0 - 2, 31, rng, depth=2.0, rmin=3.0, rmax=4.6, step=3.2,
               face_side=1, var=3.0, **dk)
    cliff_band(ca, [mouth + d * (W / 2 + 6.0), fb + d * 1.5], F0 - 2, 29, rng, depth=2.0, rmin=3.0, rmax=4.6, step=3.2,
               face_side=1, var=3.0, **dk)
    tips = [v.co.copy() for v in ca.bm.verts]       # so as pontas da face (antes das massas novas)
    inward = Vector((math.cos(L.MINE_DIR), math.sin(L.MINE_DIR), 0))
    cliff_band(ca, [ea + inward * 3, eb + inward * 3], F0 + H + 4.0, 33, rng, depth=2.0, rmin=4, rmax=6, step=4.5,
               face_side=1, **dk)
    for s in (-1, 1):
        # massas laterais FINAS e escuras, mais baixas que a verga: a madeira fica na silhueta
        cliff_band(ca, [F.p(-4.6, s * 9.2), F.p(-1.0, s * 16.4)], F0 - 1.0, F0 + H + 2.5, rng, depth=0.8, rmin=1.8,
                   rmax=2.9, step=2.4, face_side=s, var=3.0, m="Cliff_Rock_Dark", m2="Cliff_Rock")
        # blocos soltos que abracam a face externa dos esteios em alturas diferentes (sobreposicao irregular)
        for (xl, yl, sx, sy, sz, zc) in ((-5.4, 9.6, 2.8, 2.3, 3.2, 1.2), (-4.9, 9.9, 2.4, 2.0, 2.6, 6.8 + s),
                                         (-7.2, 11.6, 2.4, 2.2, 1.8, 0.5), (-6.0, 13.8, 2.0, 1.7, 1.3, 0.3)):
            q = F.p(xl, s * yl, 0)
            ca.rock((q.x, q.y, F0 + zc), (sx, sy, sz), "Cliff_Rock_Dark", 1, F.r(0, 0, rng.uniform(-0.4, 0.4)),
                    jitter=0.3)
    cao = ca.finish()
    outcrops(mb, rng, F, [cao, bpy.data.objects.get("MINE_Tunnel_Shell")])
    A = "Mine"
    # colisao das pontas da face (antes a rocha ficava sem colisao e o jogador entrava nela): caixa alinhada a face
    for s in (-1, 1):
        pts = [to_local(F, v) for v in tips if (to_local(F, v)[1] * s) > W / 2 + 4.0 and v.z < F0 + 26]
        if not pts:
            continue
        x0, x1 = min(p[0] for p in pts) - 0.3, max(p[0] for p in pts) + 0.3
        y0, y1 = min(p[1] for p in pts) - 0.3, max(p[1] for p in pts) + 0.3
        c = F.p((x0 + x1) / 2, (y0 + y1) / 2, 0)
        col_box(A, (x1 - x0, y1 - y0, 40), (c.x, c.y, 20), F.r())
        print("MINA ponta %+d: x %.1f..%.1f y %.1f..%.1f" % (s, x0, x1, y0, y1))
    for s in (-1, 1):
        q = F.p(X0, s * (W / 2 + 0.6), F0)
        col_box(A, (2.4, 2.4, H + 4), (q.x, q.y, F0 + (H + 4) / 2), F.r())
        q2 = F.p(-3.0, s * 12.8, F0)
        col_box(A, (9.5, 8.4, 34.0), (q2.x, q2.y, F0 + 16.0), F.r())
    q = F.p(-1.0, 0, F0)
    col_box(A, (4.0, W + 10, 20), (q.x, q.y, F0 + H + 12), F.r())
    marker("MINE_Entrance", tuple(F.p(-4.0, 0, F0)), F.r(0, 0, math.pi), 3, "ARROWS")
    yard(mb, rng, F)
    mb.finish()


def outcrops(mb, rng, F, obs):
    """afloramentos de cristal ASSENTADOS na rocha (raios contra a face ja pronta): crescem para cima nas saliencias
    em volta da boca, no pe da face (rocha encontra o gramado) e nas paredes baixas por dentro da boca. Nada preso de
    lado numa parede lisa: cristal fino colado de lado le como estilhaco flutuando."""
    W = L.MINE_W
    inward = F.p(1, 0) - F.p(0, 0)
    left = F.p(0, 1) - F.p(0, 0)
    up = Vector((0, 0, 1))
    n_ok = 0
    # saliencias (topo dos blocos e das massas laterais): raio de cima para baixo, so superficie voltada para cima
    for s in (-1, 1):
        cand = []
        for xl in (-7.5, -6.0, -4.5, -3.0):
            for yl in (9.6, 11.2, 12.8, 14.4, 16.0, 17.6):
                h = surf_hit(obs, F.p(xl, s * yl, F0 + 40.0), -up, 60.0)
                if h and h[1].z > 0.6 and F0 + 1.0 < h[0].z < F0 + 24.0:
                    cand.append(h)
        cand.sort(key=lambda h: h[0].z)
        pick = [cand[k] for k in sorted({0, len(cand) // 2, len(cand) - 1})] if cand else []
        for k, (p, n) in enumerate(pick):
            s_ = (0.75, 0.95, 1.15)[min(k, 2)]
            mb.rock(tuple(p + n * 0.1), (1.9 * s_, 1.6 * s_, 0.9 * s_), "Cliff_Rock_Dark", 1,
                    (0, 0, rng.uniform(0, 6)), jitter=0.3, flat_bottom=False)
            K.crystals(mb, p + n * 0.3, s_, rng, 5, "Crystal_Blue", up=(n + inward * -0.25), spread=0.9)
            n_ok += 1
    # pe da face: cacho no chao encostado na rocha (lado do patio e lado do altar)
    for (yl, s_) in ((11.0, 1.0), (15.0, 0.8), (-15.5, 0.9)):
        h = surf_hit(obs, F.p(-16.0, yl, F0 + 0.8), inward, 24.0)
        if not h:
            continue
        p, n = h
        n2 = Vector((n.x, n.y, 0)).normalized()
        base = Vector((p.x, p.y, F0)) + n2 * 0.4
        K.crystals(mb, base, s_, rng, 5, "Crystal_Blue", up=(n2 * 0.35 + up), spread=1.0)
        K.ore_bits(mb, tuple(base + n2 * 1.4), 1.0, 3, rng, "Cliff_Rock_Dark", 0.35, 0.6)
        n_ok += 1
    # paredes baixas por dentro da boca (iluminadas pela luz fria): crescem do pe da parede, inclinados para o eixo
    for (xl, s, s_) in ((-1.6, -1, 0.8), (0.6, 1, 0.65), (3.2, 1, 0.55)):
        h = surf_hit(obs, F.p(xl, 0, F0 + 1.2), left * s, W)
        if not h:
            continue
        p, n = h
        n2 = Vector((n.x, n.y, 0)).normalized()
        K.crystals(mb, Vector((p.x, p.y, F0 + 0.1)) + n2 * 0.3, s_, rng, 4, "Crystal_Blue", up=(n2 * 0.4 + up),
                   spread=0.8)
        n_ok += 1
    print("MINA afloramentos assentados: %d" % n_ok)


def yard(mb, rng, F):
    """patio da boca (lado -y local, entre a face e a curva do trilho) + altar no pe do macico"""
    site = K.Site(buildings=False)
    A = "Mine"

    def put(tag, xl, yl, r, **kw):
        w = F.p(xl, yl)
        p = site.place(tag, w.x, w.y, r, 3.0, **kw)
        return None if p is None else Vector((p[0], p[1], F0))

    ang_out = F.a + math.pi           # +x local do Frame da peca apontando para fora (vale)
    # placa de perigo com caveira ao lado da boca, virada para quem chega
    p = put("perigo", -8.4, -8.6, 0.7)
    if p:
        K.danger_sign(mb, p.x, p.y, F0, F.a - math.pi / 2 + 0.25)
        col_box(A, (0.8, 0.8, 5.6), (p.x, p.y, F0 + 2.8))
    # rack de picaretas e pas encostado na rocha (frente para fora)
    p = put("rack_mina", -12.8, -12.6, 2.4)
    if p:
        Fr = Frame(p.x, p.y, F0, F.a + math.pi / 2)
        K.tool_rack(mb, Fr, rng, ("pick", "shovel", "pick", "shovel", "pick"), s=1.25)
        col_box(A, (7.0, 1.6, 3.8), tuple(Fr.p(0, 0.3, 1.9)), Fr.r())
    p = put("barril_agua", -12.0, -17.6, 1.1)
    if p:
        K.water_barrel(mb, (p.x, p.y, F0), rng)
        col_box(A, (2.2, 2.2, 2.4), (p.x, p.y, F0 + 1.2))
    # pilha de rejeito escorrendo da face para o patio
    p = put("rejeito", -4.6, -23.8, 2.6)
    if p:
        K.tailings(mb, (p.x, p.y, F0), ang_out + rng.uniform(-0.2, 0.2), rng, 9.5, s=1.35)
        oc = p + Vector((math.cos(ang_out), math.sin(ang_out), 0)) * 4.0
        col_box(A, (11.0, 6.0, 3.2), (oc.x, oc.y, F0 + 1.6), (0, 0, ang_out))
        site.reserve(oc.x, oc.y, 3.5)
    # escoras de reserva empilhadas junto a face
    p = put("escoras", -6.2, -31.8, 3.3)
    if p:
        Ft = Frame(p.x, p.y, F0, F.a + math.pi / 2 + 0.12)
        K.timber_stack(mb, Ft, rng, 6, 6.2)
        col_box(A, (6.6, 3.2, 2.6), (p.x, p.y, F0 + 1.3), Ft.r())
    # mesa de triagem com sacos de minerio
    p = put("mesa_triagem", -17.8, -11.8, 2.4)
    if p:
        Fs = Frame(p.x, p.y, F0, F.a + math.pi / 2)
        K.sorting_table(mb, Fs, rng)
        for i in range(3):
            K.sack(mb, tuple(Fs.p(-2.9 + i * 0.3, -1.6 + i * 1.3, 0)), rng, 0.9, lying=(i == 1))
        col_box(A, (4.8, 3.0, 3.0), (p.x, p.y, F0 + 1.5), Fs.r())
    # caixotes vermelhos de dinamite (afastados da boca)
    p = put("dinamite", -13.8, -27.6, 2.2)
    if p:
        K.dynamite_crates(mb, (p.x, p.y, F0), F.a + 0.3, rng)
        col_box(A, (4.4, 2.8, 3.6), (p.x, p.y, F0 + 1.8), (0, 0, F.a + 0.3))
    # poste com sino (aviso de detonacao)
    p = put("sino", -13.0, -6.8, 0.7)
    if p:
        K.bell_post(mb, p.x, p.y, F0, F.a)
        col_box(A, (0.8, 0.8, 7.0), (p.x, p.y, F0 + 3.5))
    # carrinho tombado perto da boca, cristais derramados
    p = put("carrinho_tombado", -17.6, -18.6, 2.2)
    if p:
        ya = F.a + math.pi / 2 + 0.5
        K.cart(mb, (p.x, p.y, F0 + 2.0), ya, rng, None, roll=D(102))
        side = Vector((-math.sin(ya), math.cos(ya), 0))
        for k in range(3):
            q = p - side * (2.2 + k * 0.9) + Vector((math.cos(ya), math.sin(ya), 0)) * rng.uniform(-1.2, 1.2)
            K.crystals(mb, (q.x, q.y, F0), rng.uniform(0.35, 0.55), rng, 3, "Crystal_Blue")
        K.ore_bits(mb, tuple(p - side * 2.6), 1.4, 5, rng, "Coal_Rock", 0.35, 0.7)
        col_box(A, (3.8, 3.4, 2.8), (p.x, p.y, F0 + 1.4), (0, 0, ya))
    # altar de mineiro no pe do macico (alem da ponta sudeste da face), virado para o vale
    p = put("altar", -4.2, 23.4, 1.9)
    if p:
        K.altar(mb, (p.x, p.y, F0), D(135), rng, "L_Mine_Altar")
        col_box(A, (3.8, 2.6, 4.0), (p.x, p.y, F0 + 2.0), (0, 0, D(135)))


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
    mb = PMB("RAIL_Main_Line", "10_RAILS", rng, vmax=2)
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
    cm = PMB("RAIL_Mine_Carts", "10_RAILS", rng, vmax=1)
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
    rail_bed(rng, F, pts)


def ballast(bd, ext, kind_of, rng):
    """lastro de brita sob os dormentes (mais largo que eles, borda recortada) e pranchas rente ao piso nos
    cruzamentos com as estradas"""
    kinds = [kind_of(p) for p in ext]
    zt = F0 + 0.17
    last = None
    for i in range(len(ext) - 1):
        a, b = ext[i], ext[i + 1]
        t = (b - a)
        t.z = 0.0
        if t.length < 1e-4:
            continue
        tn = t.normalized()
        s = Vector((-tn.y, tn.x, 0))
        if kinds[i] == "bed" and kinds[i + 1] == "bed":
            wa = last or [2.85 + rng.uniform(-0.3, 0.45) for _ in range(2)]
            wb = [2.85 + rng.uniform(-0.3, 0.45) for _ in range(2)]
            last = wb
            A_ = Vector((a.x, a.y, 0)) + s * wa[0]
            D_ = Vector((a.x, a.y, 0)) - s * wa[1]
            B_ = Vector((b.x, b.y, 0)) + s * wb[0]
            C_ = Vector((b.x, b.y, 0)) - s * wb[1]
            z = Vector((0, 0, zt))
            zd = Vector((0, 0, F0 - 0.08))
            bd.quad(A_ + z, B_ + z, C_ + z, D_ + z, "Stone_Grout")
            bd.quad(A_ + zd, B_ + zd, B_ + z, A_ + z, "Stone_Grout")
            bd.quad(D_ + z, C_ + z, C_ + zd, D_ + zd, "Stone_Grout")
            if rng.random() < 0.22:
                q = a + s * rng.choice((-1, 1)) * (wa[0] + 0.25)
                bd.rock((q.x, q.y, F0 + 0.15), (0.75, 0.6, 0.42), "Stone_Dark", 1, (0, 0, rng.uniform(0, 6)))
        elif kinds[i] == "plank" and kinds[i + 1] == "plank":
            last = None
            c = (a + b) / 2
            ang = math.atan2(tn.y, tn.x)
            for off in (-2.05, -0.65, 0.0, 0.65, 2.05):
                w = 0.6 if abs(off) < 1 else 0.9
                q = c + s * off
                bd.box((t.length + 0.05, w, 0.14), (q.x, q.y, F0 + 0.45), (0, 0, ang + rng.uniform(-0.01, 0.01)),
                       "Wood_Plank", 0.0)
        else:
            last = None


def rail_bed(rng, F, pts):
    """leito de carga do trecho externo: lastro de borda recortada, pranchas nos cruzamentos, desvio na balanca"""
    import fm_buildings
    bd = PMB("RAIL_Bed", "10_RAILS", rng, vmax=1,
             remap={"Cliff_Rock_Dark": "Coal_Rock", "Metal_Dark": "Metal_Iron", "Stone_Dark": "Stone_Grout"})
    # cruzamentos: faixa da estrada (a estrada da mina termina rente ao trilho: margem maior para pegar a ponta)
    roads = [fm_buildings.ribbon(fm_buildings.PATHS[k][0], fm_buildings.PATHS[k][1] + mg)
             for k, mg in (("Mine_Road", 5.0), ("West_Road", 0.6)) if k in fm_buildings.PATHS]
    wing_x = L.FORGE_WING_L[0]
    st = Vector((-55.8, -8.2, 0))

    def kind_of(p):
        if p.x > wing_x - 0.8:
            return None                              # dentro da ala da forja
        if any(point_in_poly(p.x, p.y, rb) for rb in roads):
            return "plank"
        if (Vector((p.x, p.y, 0)) - st).length < 4.2:
            return None                              # plataforma da balanca
        return "bed"
    ballast(bd, resample(pts[5:], 1.5), kind_of, rng)
    # desvio curto na balanca: sai da linha antes da estacao, corre a oeste dela e termina num para-choque
    fine = resample(pts, 1.0)
    k0 = min(range(len(fine)), key=lambda k: (fine[k] - Vector((-57.4, -31.0, fine[k].z))).length)
    p0 = fine[k0]
    t0 = (fine[k0 + 1] - fine[k0 - 1]).normalized()
    sd = bezier(p0, p0 + t0 * 5.5, Vector((-66.0, -24.0, p0.z)), Vector((-66.0, -18.5, p0.z)), 9)
    sd += [Vector((-66.0, -5.5, p0.z))]
    ballast(bd, resample(sd, 1.5), lambda p: "bed" if (p - p0).length > 3.5 else None, rng)
    K.rail_stub(bd, sd, z=F0 + 0.02, rng=rng)
    K.bumper(bd, sd[-1], (0, 1))
    col_box("Rails", (4.0, 3.6, 2.2), (-66.0, -4.6, F0 + 1.1))
    for (yy, load) in ((-8.3, None), (-12.4, "crystal"), (-16.5, "crystal")):
        K.cart(bd, (-66.0, yy, F0 + 0.3), D(90), rng, load)
        col_box("Rails", (2.6, 3.6, 3.4), (-66.0, yy, F0 + 1.7))
    for a_, b_ in zip(sd[::3], sd[3::3]):
        c = (a_ + b_) / 2
        dd = b_ - a_
        col_box("Rails", (dd.length + 0.5, 4.0, 0.3), (c.x, c.y, F0 + 0.15), (0, 0, math.atan2(dd.y, dd.x)))
    # fragmentos de cristal e minerio ao longo do trilho (boca e balanca), sempre FORA da bitola: o carrinho animado
    # do export_vfx percorre a linha principal e nao pode atravessar pedras
    track = [Vector((v.x, v.y, 0)) for v in fine + resample(sd, 1.0)]
    for p, n in ((F.p(-6.0, 0), 5), (F.p(-14.0, -1.5), 4), (Vector((-56.0, -20.0, 0)), 4), (Vector((-55.6, 2.5, 0)), 3)):
        for k in range(n):
            a = rng.uniform(0, math.tau)
            q = Vector((p.x, p.y, 0)) + Vector((math.cos(a), math.sin(a), 0)) * rng.uniform(2.4, 3.6)
            if min((q - v).length for v in track) < 2.5:
                q = q + (q - min(track, key=lambda v: (q - v).length)).normalized() * 1.2
                if min((q - v).length for v in track) < 2.5:
                    continue
            if rng.random() < 0.45:
                K.crystal(bd, (q.x, q.y, F0 + 0.1), rng.uniform(0.6, 1.0), rng.uniform(0.16, 0.24),
                          (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 1.0), "Crystal_Blue", rng.uniform(0, 6))
            else:
                K.ore_bits(bd, (q.x, q.y, F0), 0.4, 1, rng, "Coal_Rock", 0.35, 0.6)
    bd.finish()
