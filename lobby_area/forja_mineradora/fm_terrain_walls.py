# fm_terrain_walls - muros do terreno com cara de obra velha encaixada na rocha (nao arquibancada):
#   retaining_wall(): muro de arrimo dos portais (TER_Cliff_UpperWall) - alvenaria sem chanfro (vista de longe),
#       topo erodido (+-1.5), 4 afloramentos de rocha natural avancando a frente do muro (~34% do comprimento, longe
#       das escadas e patamares), 2 entalhes para quedas d'agua extras (x -60 e x 92), pilastras em 2 tamanhos com
#       espacamento irregular, hera em massas e cortinas; contrafortes de rocha das cachoeiras NO (x -121, topo 62)
#       e NE (x 130, topo 76) encostados nas encostas laterais, fora da area caminhavel (com colisao propria).
#   south_wall(): mureta sul do vale (blocos de tamanhos variados + trechos de afloramento; colisao alta).
#   spur(): esporao de rocha so visual saindo para fora da borda sul.
import math, random
from mathutils import Vector, noise
from fm_lib import MB, col_box, col_box2
from fm_parts import masonry_wall, cliff_band, rock_column, _rock_poly
from fm_terrain_detail import TMB
import fm_layout as L

YW = L.UPPER_FRONT_Y - 0.6          # eixo do muro de arrimo (face em y ~78.7)
CANAL_BED = 13.0                    # leito de colisao do canal do ledge (fm_terrain.CANAL_BED)
# afloramentos do muro: (x0, x1, x do entalhe da queda d'agua extra ou None)
OUTCROPS = [(-67.0, -53.0, -60.0), (85.0, 99.0, 92.0), (-31.0, -17.5, None), (116.5, 131.0, None)]
NOTCH_W = 4.6
BUTTRESS_NW = (L.WEST_X + 3.5, 63.0)     # (x, topo)
BUTTRESS_NE = (L.EAST_X - 5.0, 77.0)


def skip_ranges(x0, x1, holes):
    segs = []
    cur = x0
    for a, b in sorted(holes):
        if b <= cur or a >= x1:
            continue
        if a > cur:
            segs.append((cur, a))
        cur = max(cur, b)
    if cur < x1:
        segs.append((cur, x1))
    return segs


def _xprism(mb, pts_xz, y0, y1, m):
    """prisma de um poligono no plano xz, extrudado em y (cortinas de hera, lascas)"""
    f = [mb.bm.verts.new((x, y0, z)) for x, z in pts_xz]
    b = [mb.bm.verts.new((x, y1, z)) for x, z in pts_xz]
    n = len(pts_xz)
    try:
        mb.bm.faces.new(f)
        mb.bm.faces.new(list(reversed(b)))
        for i in range(n):
            j = (i + 1) % n
            mb.bm.faces.new((f[j], f[i], b[i], b[j]))
    except ValueError:
        return
    mb._post(f + b, m, None, 0, 1)


# hera em 2 tons que ja existem no objeto (Leaf_Moss e Grass_Dark): cada material novo vira mais uma MeshPart
IVY_SHADE = {"Leaf_Moss": "Grass_Dark", "Grass_Dark": "Leaf_Moss"}


def ivy_curtain(mb, x, w, ln, y_face, z_top, rng, m):
    """cortina de hera pendurada do topo do muro: feixe de ramas estreitas de comprimentos diferentes (as do meio
    mais longas), pontas recortadas, em 2 tons e em 2 profundidades, presas por um rolo de folhas no topo"""
    U = rng.uniform
    n = max(3, int(w / 1.1))
    m2 = IVY_SHADE.get(m, m)
    x0 = x - w / 2
    for i in range(n):
        f = (i + 0.5) / n
        cx = x0 + w * f + U(-0.15, 0.15)
        sw = w / n * U(0.85, 1.35)
        L_ = ln * (1.0 - 0.75 * abs(f - 0.5) * 2.0) * U(0.55, 1.0)
        L_ = max(1.2, L_)
        tip = cx + U(-0.3, 0.3) * sw
        pts = [(cx - sw / 2, z_top + 0.3), (cx + sw / 2, z_top + 0.3),
               (cx + sw * U(0.25, 0.5), z_top - L_ * U(0.6, 0.85)),
               (tip, z_top - L_),
               (cx - sw * U(0.25, 0.5), z_top - L_ * U(0.55, 0.8))]
        dy = U(-0.12, 0.12) + (0.0 if i % 2 else -0.12)
        _xprism(mb, pts, y_face - 0.32 + dy, y_face + 0.05 + dy, m if i % 2 == 0 else m2)
    # rolo de folhas no topo (de onde as ramas caem)
    ivy_mass(mb, x, y_face + 0.6, z_top + 0.4, rng, spread=w * 0.4, n=(2, 3))


def ivy_mass(mb, x, y, z, rng, spread=1.6, n=(2, 4)):
    """massa de hera transbordando do topo: bolotas facetadas baixas"""
    for k in range(rng.randint(*n)):
        r = rng.uniform(0.9, 1.8) * (1.3 if k == 0 else 1.0)
        pl = _rock_poly(r, r * rng.uniform(0.7, 0.95), 6, rng, ex=2.0, jit=0.2)
        rock_column(mb, Vector((x + rng.uniform(-spread, spread), y + rng.uniform(-0.5, 0.8), 0.0)), pl,
                    z - r * 0.5, z + r * rng.uniform(0.45, 0.8), rng, rng.choice(("Grass_Dark", "Leaf_Moss")),
                    taper=0.55, rings=1, jitter=0.18, tilt=0.2, chamfer=r * 0.25, rim=False, bottom=False)


def _pilasters(cu, a, b, rng, skip):
    x = a + rng.uniform(2.5, 5.0)
    while x < b - 2.5:
        if not any(o0 - 2.5 < x < o1 + 2.5 for o0, o1 in skip) and abs(x) > 6:
            if rng.random() < 0.45:
                w, d, top, cw, cd, ch = 3.2, 2.4, L.TERR + 2.0, 3.8, 3.0, 0.9
            else:
                w, d, top, cw, cd, ch = 2.0, 1.8, L.TERR + 0.2, 2.5, 2.3, 0.6
            cu.box((w, d, top - 11.5), (x, L.UPPER_FRONT_Y - 1.3, (11.5 + top) / 2), (0, 0, 0), "Stone_Light", 0.25)
            cu.box((cw, cd, ch), (x, L.UPPER_FRONT_Y - 1.3, top + ch / 2 - 0.1), (0, 0, rng.uniform(-0.04, 0.04)),
                   "Stone_Dark", 0.2)
            # colisao da pilastra dentro do canal (fosso fechado: o jogador nao atravessa a pedra)
            col_box2("UpperWall", (x - w / 2, L.UPPER_FRONT_Y - 1.3 - d / 2, CANAL_BED - 0.5),
                     (x + w / 2, L.UPPER_FRONT_Y, top + ch - 0.1))
        x += rng.uniform(8.0, 21.0)


def retaining_wall(C, rng):
    cu = TMB("TER_Cliff_UpperWall", C, rng, detail="far")
    cu._mi("Stone_Light")
    holes = [(px - 7.4, px + 7.4) for px in L.PORTAL_X] + [(-3.6, 3.6)]
    segs = skip_ranges(L.WEST_X, L.EAST_X, holes)
    z_flat = L.TERR - 1.8
    for a, b in segs:
        outs = [(o0, o1, nx) for (o0, o1, nx) in OUTCROPS if a <= o0 and o1 <= b]
        # colisao da face do muro sobre o leito do canal (antes a pedra ficava 1,3 dentro do fosso sem colisao);
        # o topo acompanha o topo visual do muro (28,2 + fiada erodida) e o dos afloramentos (~31)
        col_box2("UpperWall", (a, YW - 0.75, CANAL_BED - 0.5), (b, L.UPPER_FRONT_Y, L.TERR - 1.0))
        for o0, o1, nx in outs:
            # afloramentos: a rocha avanca ate ~2,3 a frente do muro
            col_box2("UpperWall", (o0 + 0.6, YW - 0.9 - 2.4, CANAL_BED - 0.5), (o1 - 0.6, YW - 0.75, L.TERR + 1.0))
        # alvenaria so onde nao ha afloramento (a rocha toma o lugar do muro)
        for w0, w1 in skip_ranges(a, b, [(o0 + 1.2, o1 - 1.2) for o0, o1, _ in outs]):
            if w1 - w0 < 0.5:
                continue
            masonry_wall(cu, (w0, YW), (w1, YW), 11.5, z_flat, 1.4, rng, "Stone_Light", "Stone_Dark", course=2.0, mix=0.3)
            # fiada de cima erodida: blocos de alturas bem diferentes (topo +-1.5 em torno de 29.7) e falhas
            x = w0
            while x < w1 - 0.2:
                ln = rng.uniform(1.8, 3.4)
                xe = min(w1, x + ln)
                h = rng.uniform(-0.2, 3.0)
                if h > 0.35 and xe - x > 0.4:
                    cu.box((xe - x - 0.1, 1.4 + rng.uniform(-0.05, 0.12), h - 0.08),
                           ((x + xe) / 2, YW + rng.uniform(-0.05, 0.05), z_flat + h / 2),
                           (rng.uniform(-0.02, 0.02), 0, rng.uniform(-0.03, 0.03)),
                           "Stone_Light" if rng.random() > 0.3 else "Stone_Dark", 0.0)
                x = xe
        # afloramentos de rocha natural avancando no canal (entalhe no meio p/ a queda extra)
        for o0, o1, nx in outs:
            parts = [(o0, o1)] if nx is None else [(o0, nx - NOTCH_W / 2), (nx + NOTCH_W / 2, o1)]
            for p0, p1 in parts:
                cliff_band(cu, [(p0, YW - 0.9), (p1, YW - 0.9)], 11.2, L.TERR + 2.0, rng, depth=2.5, rmin=2.4,
                           rmax=4.0, step=4.0, grass=True, var=1.6, face_side=-1, front=2.3, back=7.0,
                           top_fn=lambda c: L.TERR + 1.4 + 2.2 * noise.noise(Vector((c.x * 0.09, 3.3, 0.2))))
            if nx is not None:
                # calha recuada de rocha escura onde a agua desce + bica de pedra no topo
                cu.box2((nx - NOTCH_W / 2 - 0.2, YW + 0.3, 11.3), (nx + NOTCH_W / 2 + 0.2, YW + 1.8, L.TERR - 0.7),
                        "Cliff_Rock_Dark", 0.0)
                cu.box2((nx - 2.1, YW - 0.9, L.TERR - 1.3), (nx + 2.1, L.UPPER_FRONT_Y + 2.0, L.TERR - 0.75),
                        "Stone_Dark", 0.0)
        # berma de rocha no alto (aberta nos entalhes)
        if b - a > 12:
            gaps = [(nx - 3.2, nx + 3.2) for (o0, o1, nx) in outs if nx is not None]
            for p0, p1 in skip_ranges(a + 4, b - 4, gaps):
                if p1 - p0 < 3.0:
                    continue
                cliff_band(cu, [(p0, L.UPPER_FRONT_Y + 4), (p1, L.UPPER_FRONT_Y + 4)], L.TERR - 3, L.TERR + 2.5,
                           rng, depth=1.5, rmin=2.4, rmax=4.0, step=5.5, grass=True, var=1.2, face_side=-1,
                           strata=False, back=4.0, detail="far")
            col_box2("UpperWall", (a, L.UPPER_FRONT_Y, L.TERR - 1), (b, L.UPPER_FRONT_Y + 8, L.TERR + 4))
        # pilastras em 2 tamanhos, espacamento irregular (fora dos afloramentos)
        _pilasters(cu, a, b, rng, [(o0, o1) for o0, o1, _ in outs])
        # hera: cortinas penduradas e massas transbordando do topo
        x = a + rng.uniform(1.0, 6.0)
        while x < b - 2.0:
            if not any(o0 - 1.5 < x < o1 + 1.5 for o0, o1, _ in outs):
                if rng.random() < 0.55:
                    ivy_curtain(cu, x, rng.uniform(2.5, 6.5), rng.uniform(3.0, 9.0), YW - 0.7, z_flat + 0.6, rng,
                                rng.choice(("Leaf_Moss", "Grass_Dark")))
                else:
                    ivy_mass(cu, x, YW + 0.2, z_flat + 1.2, rng)
            x += rng.uniform(6.0, 15.0)
    buttresses(cu, rng)
    return cu.finish()


def buttresses(cu, rng):
    """contrafortes de rocha de onde saem as cachoeiras NO/NE, encostados nas encostas laterais do terraco"""
    U = rng.uniform
    for (x, top), side in ((BUTTRESS_NW, -1), (BUTTRESS_NE, 1)):
        hw = 4.6 if side < 0 else 6.2
        # massa principal (frente em y ~84: a queda desce por ela) + corpo alto recuado + chifre de musgo
        for k, (cy, a, b, z1, lid) in enumerate(((90.0, hw, 6.0, top - 9.0, None),
                                                  (91.5, hw * 0.85, 5.0, top - 1.0, "Leaf_Moss"),
                                                  (94.0, hw * 0.55, 3.4, top + 3.5, None))):
            cx = x + side * (0.0 if k == 0 else 0.8 * k)
            pl = _rock_poly(a, b, 6 if k else 7, rng, ex=2.4, jit=0.1, a0=0.0)
            rock_column(cu, Vector((cx, cy, 0)), pl, L.TERR - 2.0 if k == 0 else top - 14.0 - k * 4, z1, rng,
                        "Cliff_Rock" if k != 1 else "Cliff_Rock_Dark", taper=U(0.78, 0.88), rings=2, jitter=0.12,
                        tilt=0.1, top_m=lid, lip=0.9, chamfer=0.5, band=(max(2.0, (z1 - L.TERR) * 0.17), "Cliff_Rock_Top"),
                        tongues=((2, "Grass_Dark", (1.5, 3.5), (0.0, -1.0)) if lid else None), bottom=False)
        # crista encostada na encosta lateral, descendo ate o fundo (fora da area caminhavel)
        xl = (L.WEST_X - 5.0) if side < 0 else (L.EAST_X + 2.0)
        for i, (yy, zt) in enumerate(((103.0, top - 6), (113.0, top - 13), (123.0, top - 18))):
            pl = _rock_poly(U(4.5, 5.5), U(4.5, 6.0), 6, rng, ex=2.2, jit=0.12)
            rock_column(cu, Vector((xl + U(-0.6, 0.6), yy, 0)), pl, L.TERR - 2.0, zt, rng,
                        "Cliff_Rock" if i % 2 else "Cliff_Rock_Dark", taper=U(0.75, 0.88), rings=2, jitter=0.12,
                        tilt=0.14, top_m=("Grass_Dark" if rng.random() < 0.5 else None), lip=0.8, chamfer=0.45,
                        band=(max(2.0, (zt - L.TERR) * 0.17), "Cliff_Rock_Top"), bottom=False)
        if side < 0:
            col_box2("UpperWall", (x - 5.2, 83.5, L.TERR - 2), (x + 5.0, 96.8, top + 3))
        else:
            col_box2("UpperWall", (x - 6.7, 83.5, L.TERR - 2), (L.EAST_X + 1.0, 98.0, top + 3))


# ------------------------------------------------------------------ borda sul do vale
SOUTH_OUTCROPS = [(-40.5, -33.5), (26.5, 33.5), (78.0, 84.5), (97.0, 104.0)]


def south_wall(C, rng, spans, y, z, h, w, col_top):
    """mureta sul: blocos de comprimentos/alturas variados, 4 trechos trocados por afloramentos; colisao
    continua por trecho com topo em col_top (acima do pulo a partir do piso)"""
    U = rng.uniform
    mb = TMB("TER_South_Edge_Wall", C, rng, detail="near")
    for (x0, x1) in spans:
        x = x0
        while x < x1 - 0.3:
            ln = U(1.3, 3.9)
            xe = min(x1, x + ln)
            if x1 - xe < 0.8:
                xe = x1
            xm = (x + xe) / 2
            if not any(o0 < xm < o1 for o0, o1 in SOUTH_OUTCROPS):
                hh = h + U(-0.4, 0.35)
                ww = w + U(-0.15, 0.25)
                mb.box((xe - x - 0.14, ww, hh), (xm, y + U(-0.1, 0.1), z + hh / 2),
                       (U(-0.015, 0.015), 0, U(-0.03, 0.03)), "Stone_Light" if rng.random() > 0.25 else "Stone_Dark",
                       0.2)
                if rng.random() < 0.3:
                    # pedra de capa mais larga (assentamento irregular)
                    mb.box((min(xe - x + 0.3, 3.6), ww + 0.3, 0.45), (xm, y, z + hh + 0.2), (0, 0, U(-0.05, 0.05)),
                           "Stone_Dark", 0.12)
            x = xe
        c = ((x0 + x1) / 2, y)
        col_box("FloorEdge", (x1 - x0, w, col_top - z), (c[0], c[1], z + (col_top - z) / 2))
    for o0, o1 in SOUTH_OUTCROPS:
        n = max(2, int((o1 - o0) / 2.1))
        for i in range(n):
            f = (i + 0.5) / n
            px = o0 + (o1 - o0) * f + U(-0.4, 0.4)
            a, b = U(1.3, 2.1), U(1.2, 1.9)
            pl = _rock_poly(a, b, rng.choice((5, 6)), rng, ex=2.2, jit=0.15)
            top = z + h + U(-0.6, 1.8) * (1.0 - abs(f - 0.5))
            rock_column(mb, Vector((px, y + U(-0.5, 0.3), 0)), pl, z - 2.5, top, rng,
                        "Cliff_Rock", taper=U(0.62, 0.8), rings=1, jitter=0.15, tilt=0.2, lip=0.5,
                        chamfer=0.35, band=(U(0.6, 1.0), "Cliff_Rock_Top"), rim=False, bottom=False)
    return mb.finish()


def spur(mb, x, rng, y0=-64.5, length=17.0, z_root=7.0, z_tip=-9.0):
    """esporao de rocha (so visual) saindo da borda sul para o vazio: costela que desce em degraus"""
    U = rng.uniform
    ang = math.radians(-90.0 + U(-14, 14))
    d = Vector((math.cos(ang), math.sin(ang), 0.0))
    k = 5
    for i in range(k):
        f = i / (k - 1)
        p = Vector((x, y0, 0.0)) + d * (length * f) + Vector((-d.y, d.x, 0)) * U(-0.9, 0.9)
        top = z_root + (z_tip - z_root) * (f ** 1.25) + U(-1.2, 1.2)
        a, b = U(3.2, 4.8) * (1.0 - 0.3 * f), U(2.6, 3.8) * (1.0 - 0.25 * f)
        pl = _rock_poly(a, b, 6, rng, ex=2.3, jit=0.14, a0=0.0)
        ca, sa = d.x, d.y
        pl = [(px * ca - py * sa, px * sa + py * ca) for px, py in pl]
        rock_column(mb, p, pl, -46.0, top, rng, "Cliff_Rock" if i % 2 == 0 else "Cliff_Rock_Dark",
                    taper=U(0.74, 0.86), rings=2, jitter=0.13, tilt=0.16,
                    top_m=("Grass" if rng.random() < 0.4 else None), lip=0.6, chamfer=0.45,
                    band=(U(2.5, 4.5), "Cliff_Rock_Top"), bottom=False,
                    tongues=((1, "Grass_Dark", (1.0, 2.5), (d.x, d.y)) if rng.random() < 0.5 else None))
