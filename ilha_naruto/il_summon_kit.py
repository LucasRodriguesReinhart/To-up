# il_summon_kit - pecas da torre de invocacao (zona summon): estrelas facetadas, estrela 3D de cristal, lanterna
# japonesa de canto, lanterna pendurada, estandarte azul-royal com emblema dourado, contorno de arco.
# So geometria sobre o MB do lobby (fm_lib.MB); nenhuma peca cria luz nem colisao (quem chama decide).
import math
from mathutils import Vector
import fm_portal_kit as PK


def star_pts(n, r_out, r_in, rot=0.0):
    """perimetro 2D de uma estrela de n pontas (1a ponta para cima, +v)"""
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = rot + math.pi / 2 + math.pi * i / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def star(mb, c, u, v, n, r_out, r_in, depth, m, rot=0.0, edge=0.0, tint=None):
    """estrela facetada (cristal lapidado): perimetro no plano (u, v) e um apice de cada lado na normal.
    edge > 0 da espessura a borda (pontas nao ficam em faca)."""
    c = Vector(c)
    u = Vector(u).normalized()
    v = Vector(v).normalized()
    nrm = u.cross(v).normalized()
    pts = star_pts(n, r_out, r_in, rot)
    bm = mb.bm
    k = len(pts)
    if edge > 0:
        f = [bm.verts.new(c + u * a + v * b + nrm * (edge / 2)) for a, b in pts]
        g = [bm.verts.new(c + u * a + v * b - nrm * (edge / 2)) for a, b in pts]
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((f[i], f[j], g[j], g[i]))
    else:
        f = g = [bm.verts.new(c + u * a + v * b) for a, b in pts]
    top = bm.verts.new(c + nrm * (depth + edge / 2))
    bot = bm.verts.new(c - nrm * (depth + edge / 2))
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((f[i], f[j], top))
        bm.faces.new((g[j], g[i], bot))
    verts = list(f) + ([] if edge <= 0 else list(g)) + [top, bot]
    mb._post(verts, m, tint, 0, 1)


def star_duo(mb, c, u, v, n, r_out, r_in, depth, mA, mB, rot=0.0, edge=0.0, tint=None):
    """estrela facetada de cristal em 2 materiais alternados por faceta (A nas facetas pares, B nas impares; a
    borda segue a faceta da frente). No Roblox o Neon apaga o sombreado: e a troca de cor faceta a faceta que faz a
    estrela ler como cristal lapidado. Malha continua (um objeto, um bmesh; so o indice de material muda)."""
    c = Vector(c)
    u = Vector(u).normalized()
    v = Vector(v).normalized()
    nrm = u.cross(v).normalized()
    pts = star_pts(n, r_out, r_in, rot)
    bm = mb.bm
    k = len(pts)
    odd = []
    if edge > 0:
        f = [bm.verts.new(c + u * a + v * b + nrm * (edge / 2)) for a, b in pts]
        g = [bm.verts.new(c + u * a + v * b - nrm * (edge / 2)) for a, b in pts]
        for i in range(k):
            j = (i + 1) % k
            q = bm.faces.new((f[i], f[j], g[j], g[i]))
            if i % 2:
                odd.append(q)
    else:
        f = g = [bm.verts.new(c + u * a + v * b) for a, b in pts]
    top = bm.verts.new(c + nrm * (depth + edge / 2))
    bot = bm.verts.new(c - nrm * (depth + edge / 2))
    for i in range(k):
        j = (i + 1) % k
        a = bm.faces.new((f[i], f[j], top))
        b = bm.faces.new((g[j], g[i], bot))
        if i % 2:
            odd += [a, b]
    verts = list(f) + ([] if edge <= 0 else list(g)) + [top, bot]
    mb._post(verts, mA, tint, 0, 1)
    mi = mb._mi_for(mB)
    for q in odd:
        q.material_index = mi


def star_flat(mb, c, u, v, n, r_out, r_in, z_thick, m, rot=0.0):
    """estrela chata (embutida no piso ou aplicada numa parede): prisma de espessura z_thick na normal de (u, v)"""
    c = Vector(c)
    u = Vector(u).normalized()
    v = Vector(v).normalized()
    nrm = u.cross(v).normalized()
    pts = star_pts(n, r_out, r_in, rot)
    PK.plate(mb, pts, c + nrm * (z_thick / 2), u, v, z_thick, m)


def star3d(mb, c, r, m, rot=0.0, thin=0.3):
    """estrela de cristal 3D de 4 pontas (duas estrelas facetadas cruzadas + uma pequena na horizontal)"""
    c = Vector(c)
    a = Vector((math.cos(rot), math.sin(rot), 0.0))
    b = Vector((-math.sin(rot), math.cos(rot), 0.0))
    z = Vector((0.0, 0.0, 1.0))
    star(mb, c, a, z, 4, r, r * thin, r * 0.32, m)
    star(mb, c, b, z, 4, r * 0.82, r * thin, r * 0.30, m)
    star(mb, c, a, b, 4, r * 0.55, r * thin * 0.8, r * 0.22, m, rot=math.pi / 4)


def const_star(mb, c, size, m, m_core, rot=0.0):
    """estrela de constelacao (4 pontas): estrela facetada principal de frente para 'rot' (plano vertical), uma
    cruzada menor e um miolo claro que fura as duas faces (o brilho do centro das refs 08-12)"""
    c = Vector(c)
    a = Vector((math.cos(rot), math.sin(rot), 0.0))
    b = Vector((-math.sin(rot), math.cos(rot), 0.0))
    z = Vector((0.0, 0.0, 1.0))
    star(mb, c, a, z, 4, size, size * 0.27, size * 0.3, m, edge=0.3)
    star(mb, c, b, z, 4, size * 0.72, size * 0.24, size * 0.26, m, edge=0.3)
    star(mb, c, a, z, 4, size * 0.42, size * 0.15, size * 0.3 + 0.3, m_core, rot=math.pi / 4, edge=0.2)


def arch_poly(hw, z0, z_spring, n=12):
    """contorno (u, z) de um vao em arco pleno: ombreiras retas de z0 a z_spring + meio circulo de raio hw"""
    pts = [(-hw, z0), (hw, z0), (hw, z_spring)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((hw * math.cos(a), z_spring + hw * math.sin(a)))
    pts.append((-hw, z_spring))
    return pts


def corner_lantern(stone, glow, gold, F, u, v, z, s=1.0, sh=None):
    """lanterna japonesa de canto (estilo pagode, 'de pedra'): pe, camara de luz com montantes, 2 telhados de 4
    aguas com pontas douradas e remate. Referencial F (Frame da torre), base em (u, v, z). s = escala horizontal,
    sh = escala vertical (altura total = 1,38 + 4,1 sh com s = 1). Sem chanfro; secoes >= 0,3."""
    sh = s if sh is None else sh
    R = F.r()
    R45 = F.r(0, 0, math.pi / 4)
    z1 = z
    h = max(0.3, 0.45 * sh)
    stone.box((2.3 * s, 2.3 * s, h), F.p(u, v, z1 + h / 2), R, "Summon_Stone_Dark", 0.0)
    z1 += h
    h = max(0.3, 0.35 * sh)
    stone.box((1.7 * s, 1.7 * s, h), F.p(u, v, z1 + h / 2), R, "Summon_Stone", 0.0)
    z1 += h
    hc = 1.95 * sh
    zc = z1 + hc / 2
    glow.box((1.5 * s, 1.5 * s, hc), F.p(u, v, zc), R, "Lantern_Glow", 0.0)
    for su in (-1, 1):
        for sv in (-1, 1):
            stone.box((0.42 * s, 0.42 * s, hc + 0.1), F.p(u + su * 0.82 * s, v + sv * 0.82 * s, zc), R,
                      "Summon_Stone_Dark", 0.0)
    # travessas (grade da camara)
    for sv in (-1, 1):
        stone.box((1.7 * s, 0.3, 0.3), F.p(u, v + sv * 0.8 * s, zc), R, "Summon_Stone_Dark", 0.0)
    for su in (-1, 1):
        stone.box((0.3, 1.7 * s, 0.3), F.p(u + su * 0.8 * s, v, zc), R, "Summon_Stone_Dark", 0.0)
    z1 += hc
    stone.box((2.1 * s, 2.1 * s, 0.3), F.p(u, v, z1 + 0.15), R, "Summon_Stone_Dark", 0.0)
    z1 += 0.3
    # telhado largo (piramide de 4 aguas) e pontas douradas viradas para cima
    h = 0.9 * sh
    stone.cyl(2.35 * s, h, F.p(u, v, z1 + h / 2), R45, "Summon_Stone_Dark", 4, r2=0.75 * s, bevel=0.0)
    for su in (-1, 1):
        for sv in (-1, 1):
            p = F.p(u + su * 1.6 * s, v + sv * 1.6 * s, z1 + 0.08)
            q = F.p(u + su * 1.95 * s, v + sv * 1.95 * s, z1 + 0.08 + 0.6 * sh)
            spike(gold, p, q, 0.24 * s, "Metal_Gold", 4)
    z1 += h
    h = 0.55 * sh
    stone.cyl(0.62 * s, h, F.p(u, v, z1 + h / 2), R45, "Summon_Stone_Dark", 4, r2=0.62 * s, bevel=0.0)
    z1 += h
    h = 0.7 * sh
    stone.cyl(1.25 * s, h, F.p(u, v, z1 + h / 2), R45, "Summon_Stone_Dark", 4, r2=0.3 * s, bevel=0.0)
    z1 += h
    gold.ico(0.34 * s, F.p(u, v, z1 + 0.3 * s), "Metal_Gold", 1, (1, 1, 1.3))
    return F.p(u, v, zc)


def hang_lantern(stone, glow, gold, top, s=1.0, drop=1.0):
    """lanterna pendurada (caixa de luz com moldura escura e chapeu), presa em 'top' (mundo)"""
    top = Vector(top)
    gold.rod(top, top - Vector((0, 0, drop)), 0.16, "Metal_Gold", 4)
    c = top - Vector((0, 0, drop + 0.35 * s + 0.75 * s))
    # (folgas >= 0,1 entre a caixa de luz e as pecas escuras: nada coplanar com o Neon)
    stone.box((1.35 * s, 1.35 * s, 0.3), c + Vector((0, 0, -0.7 * s - 0.25)), (0, 0, 0), "Summon_Stone_Dark", 0.0)
    glow.box((1.0 * s, 1.0 * s, 1.4 * s), c, (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            stone.box((0.3, 0.3, 1.4 * s + 0.2), c + Vector((sx * 0.56 * s, sy * 0.56 * s, 0)), (0, 0, 0),
                      "Summon_Stone_Dark", 0.0)
    stone.cyl(1.05 * s, 0.6 * s, c + Vector((0, 0, 0.7 * s + 0.1 + 0.3 * s)), (0, 0, math.pi / 4),
              "Summon_Stone_Dark", 4, r2=0.3, bevel=0.0)
    gold.ico(0.22 * s, c + Vector((0, 0, 0.7 * s + 0.1 + 0.6 * s + 0.2 * s)), "Metal_Gold", 1)
    return c


def banner(cloth, gold, wood, F, u0, u1, v, z_top, length, tip=1.5):
    """estandarte azul-royal pendurado de uma haste (no plano u-z do referencial F, face para +v e -v),
    com barra dourada, debrum dourado, ponta em V e emblema de constelacao dourado dos dois lados"""
    w = u1 - u0
    uc = (u0 + u1) / 2
    X = Vector(F.p(1, 0, 0)) - Vector(F.p(0, 0, 0))
    Z = Vector((0, 0, 1))
    o = F.p(uc, v, z_top)
    hw = w / 2
    pts = [(-hw, 0.0), (hw, 0.0), (hw, -length), (0.0, -length - tip), (-hw, -length)]
    PK.plate(cloth, pts, o, X, Z, 0.22, "Cloth_Royal_Blue")
    # barra de cima e debrum (dos dois lados do pano)
    gold.box((w + 0.5, 0.5, 0.45), F.p(uc, v, z_top + 0.05), F.r(), "Metal_Gold", 0.0)
    for sgn in (-1, 1):
        dv = sgn * 0.17
        for su in (-1, 1):
            a = F.p(uc + su * (hw - 0.22), v + dv, z_top - 0.3)
            b = F.p(uc + su * (hw - 0.22), v + dv, z_top - length + 0.1)
            gold.beam(a, b, 0.3, 0.34, "Metal_Gold", 0.0)
        # V da ponta
        for su in (-1, 1):
            a = F.p(uc + su * (hw - 0.22), v + dv, z_top - length + 0.1)
            b = F.p(uc, v + dv, z_top - length - tip + 0.35)
            gold.beam(a, b, 0.3, 0.34, "Metal_Gold", 0.0)
        # emblema: anel + 4 estrelinhas em losango + estrela central (constelacao)
        ce = Vector(F.p(uc, v + sgn * 0.2, z_top - length * 0.5))
        PK.ring(gold, ce, 1.25, X, Z, 0.3, 0.3, "Metal_Gold", 0, 360, 20)
        star(gold, ce, X, Z, 4, 0.95, 0.26, 0.16, "Metal_Gold")
        for du, dz in ((0, 2.1), (0, -2.1), (1.55, 0), (-1.55, 0)):
            star(gold, ce + X * du + Z * dz, X, Z, 4, 0.65, 0.2, 0.14, "Metal_Gold")
        star(gold, Vector(F.p(uc, v + sgn * 0.2, z_top - length + 1.4)), X, Z, 4, 0.6, 0.18, 0.14, "Metal_Gold")


def spike(mb, a, b, r, m, n=4, u=None, phase=None):
    """pinaculo/ponta: base de n lados (raio r) em a e apice UNICO em b (o cone do lobby com raio de topo 0,02
    deixava um anel minusculo = triangulos-lasca). u: eixo de referencia da base (p.ex. a lateral da torre)."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    uu = Vector(u) if u is not None else (Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0)))
    uu = (uu - d * uu.dot(d)).normalized()
    vv = d.cross(uu).normalized()
    ph = (math.pi / n) if phase is None else phase
    bm = mb.bm
    ring = [bm.verts.new(a + (uu * math.cos(ph + math.tau * i / n) + vv * math.sin(ph + math.tau * i / n)) * r)
            for i in range(n)]
    top = bm.verts.new(b)
    bm.faces.new(list(reversed(ring)))
    for i in range(n):
        bm.faces.new((ring[i], ring[(i + 1) % n], top))
    mb._post(ring + [top], m, None, 0, 1)


def gem(mb, base, h, r, d, m, n=6):
    """cristal lapidado: prisma de n lados + ponta piramidal, de 'base' na direcao d (comprimento h)"""
    base = Vector(base)
    d = Vector(d).normalized()
    a = base
    b = base + d * (h * 0.66)
    t = base + d * h
    PK.cone(mb, a, b, r * 0.86, r, m, n)
    spike(mb, b, t, r, m, n, phase=0.0)


def gem_cluster(mb, base, s, m, rng):
    """cacho de cristal robusto (referencia: cristal central grande + 4 menores inclinados para fora + 2 miudos)"""
    base = Vector(base)
    gem(mb, base, 6.6 * s, 1.2 * s, (rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), 1.0), m)
    a0 = rng.uniform(0, math.tau)
    for k in range(4):
        a = a0 + k * math.tau / 4 + rng.uniform(-0.3, 0.3)
        out = Vector((math.cos(a), math.sin(a), 0.0))
        tilt = rng.uniform(0.45, 0.7)
        d = out * math.sin(tilt) + Vector((0, 0, math.cos(tilt)))
        gem(mb, base + out * 0.75 * s, rng.uniform(3.2, 4.4) * s, rng.uniform(0.62, 0.8) * s, d, m)
    for k in range(2):
        a = a0 + math.pi / 4 + k * math.pi + rng.uniform(-0.2, 0.2)
        out = Vector((math.cos(a), math.sin(a), 0.0))
        d = out * 0.8 + Vector((0, 0, 0.6))
        gem(mb, base + out * 1.05 * s, 2.0 * s, 0.45 * s, d, m)
