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


def arch_poly(hw, z0, z_spring, n=12):
    """contorno (u, z) de um vao em arco pleno: ombreiras retas de z0 a z_spring + meio circulo de raio hw"""
    pts = [(-hw, z0), (hw, z0), (hw, z_spring)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((hw * math.cos(a), z_spring + hw * math.sin(a)))
    pts.append((-hw, z_spring))
    return pts


def corner_lantern(stone, glow, gold, F, u, v, z, s=1.0):
    """lanterna japonesa de canto (estilo pagode, 'de pedra'): pe, camara de luz com montantes, 2 telhados de 4
    aguas com pontas douradas e remate. Referencial F (Frame da torre), base em (u, v, z)."""
    R = F.r()
    stone.box((2.3 * s, 2.3 * s, 0.45 * s), F.p(u, v, z + 0.22 * s), R, "Summon_Stone_Dark", 0.1)
    stone.box((1.7 * s, 1.7 * s, 0.35 * s), F.p(u, v, z + 0.62 * s), R, "Summon_Stone", 0.06)
    zc = z + 0.8 * s + 1.0 * s
    glow.box((1.5 * s, 1.5 * s, 1.95 * s), F.p(u, v, zc), R, "Lantern_Glow", 0.0)
    for su in (-1, 1):
        for sv in (-1, 1):
            stone.box((0.42 * s, 0.42 * s, 2.1 * s), F.p(u + su * 0.82 * s, v + sv * 0.82 * s, zc), R,
                      "Summon_Stone_Dark", 0.0)
    # travessas (grade da camara)
    for sv in (-1, 1):
        stone.box((1.7 * s, 0.26 * s, 0.26 * s), F.p(u, v + sv * 0.8 * s, zc), R, "Summon_Stone_Dark", 0.0)
    for su in (-1, 1):
        stone.box((0.26 * s, 1.7 * s, 0.26 * s), F.p(u + su * 0.8 * s, v, zc), R, "Summon_Stone_Dark", 0.0)
    zr = z + 0.8 * s + 2.05 * s
    stone.box((2.1 * s, 2.1 * s, 0.25 * s), F.p(u, v, zr + 0.12 * s), R, "Summon_Stone_Dark", 0.0)
    # telhado largo (piramide de 4 aguas) e pontas douradas viradas para cima
    stone.cyl(2.35 * s, 0.9 * s, F.p(u, v, zr + 0.25 * s + 0.45 * s), F.r(0, 0, math.pi / 4), "Summon_Stone_Dark", 4,
              r2=0.75 * s, bevel=0.0)
    for su in (-1, 1):
        for sv in (-1, 1):
            p = F.p(u + su * 1.62 * s, v + sv * 1.62 * s, zr + 0.3 * s)
            q = F.p(u + su * 1.95 * s, v + sv * 1.95 * s, zr + 0.85 * s)
            PK.cone(gold, p, q, 0.22 * s, 0.03, "Metal_Gold", 4)
    stone.cyl(0.62 * s, 0.55 * s, F.p(u, v, zr + 1.15 * s + 0.27 * s), F.r(0, 0, math.pi / 4), "Summon_Stone_Dark",
              4, r2=0.62 * s, bevel=0.0)
    stone.cyl(1.25 * s, 0.7 * s, F.p(u, v, zr + 1.7 * s + 0.35 * s), F.r(0, 0, math.pi / 4), "Summon_Stone_Dark", 4,
              r2=0.2 * s, bevel=0.0)
    gold.ico(0.34 * s, F.p(u, v, zr + 2.6 * s), "Metal_Gold", 1, (1, 1, 1.3))
    return F.p(u, v, zc)


def hang_lantern(stone, glow, gold, top, s=1.0, drop=1.0):
    """lanterna pendurada (caixa de luz com moldura escura e chapeu), presa em 'top' (mundo)"""
    top = Vector(top)
    gold.rod(top, top - Vector((0, 0, drop)), 0.12 * s, "Metal_Gold", 4)
    c = top - Vector((0, 0, drop + 0.35 * s + 0.75 * s))
    stone.box((1.35 * s, 1.35 * s, 0.25 * s), c + Vector((0, 0, -0.85 * s)), (0, 0, 0), "Summon_Stone_Dark", 0.0)
    glow.box((1.0 * s, 1.0 * s, 1.4 * s), c, (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            stone.box((0.24 * s, 0.24 * s, 1.55 * s), c + Vector((sx * 0.56 * s, sy * 0.56 * s, 0)), (0, 0, 0),
                      "Summon_Stone_Dark", 0.0)
    stone.cyl(1.05 * s, 0.6 * s, c + Vector((0, 0, 1.0 * s)), (0, 0, math.pi / 4), "Summon_Stone_Dark", 4,
              r2=0.25 * s, bevel=0.0)
    gold.ico(0.22 * s, c + Vector((0, 0, 1.42 * s)), "Metal_Gold", 1)
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
    gold.box((w + 0.5, 0.5, 0.45), F.p(uc, v, z_top + 0.05), F.r(), "Metal_Gold", 0.08)
    for sgn in (-1, 1):
        dv = sgn * 0.17
        for su in (-1, 1):
            a = F.p(uc + su * (hw - 0.22), v + dv, z_top - 0.3)
            b = F.p(uc + su * (hw - 0.22), v + dv, z_top - length + 0.1)
            gold.beam(a, b, 0.12, 0.34, "Metal_Gold", 0.0)
        # V da ponta
        for su in (-1, 1):
            a = F.p(uc + su * (hw - 0.22), v + dv, z_top - length + 0.1)
            b = F.p(uc, v + dv, z_top - length - tip + 0.35)
            gold.beam(a, b, 0.12, 0.34, "Metal_Gold", 0.0)
        # emblema: anel + 4 estrelinhas em losango + estrela central (constelacao)
        ce = Vector(F.p(uc, v + sgn * 0.2, z_top - length * 0.5))
        PK.ring(gold, ce, 1.25, X, Z, 0.26, 0.14, "Metal_Gold", 0, 360, 20)
        star(gold, ce, X, Z, 4, 0.95, 0.24, 0.12, "Metal_Gold", edge=0.1)
        for du, dz in ((0, 2.1), (0, -2.1), (1.55, 0), (-1.55, 0)):
            star(gold, ce + X * du + Z * dz, X, Z, 4, 0.6, 0.16, 0.1, "Metal_Gold", edge=0.1)
        star(gold, Vector(F.p(uc, v + sgn * 0.2, z_top - length + 1.4)), X, Z, 4, 0.5, 0.14, 0.1, "Metal_Gold",
             edge=0.1)


def gem(mb, base, h, r, d, m, n=6):
    """cristal lapidado: prisma de n lados + ponta piramidal, de 'base' na direcao d (comprimento h)"""
    base = Vector(base)
    d = Vector(d).normalized()
    a = base
    b = base + d * (h * 0.66)
    t = base + d * h
    PK.cone(mb, a, b, r * 0.86, r, m, n)
    PK.cone(mb, b, t, r, 0.03, m, n)


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
