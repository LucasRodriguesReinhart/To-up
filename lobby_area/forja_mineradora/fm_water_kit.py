# fm_water_kit - pecas de agua que LEEM como agua (e que o Roblox recebe como malha, sem shader):
#   cachoeira em laminas curvas sobrepostas (Water atras, Water_Fall na frente, listras de Foam), labio branco no topo,
#   bacia com anel de espuma na base; chevrons de espuma a jusante das pedras; contraforte de rocha com entalhe em V.
import math, random
from mathutils import Vector
from fm_parts import rock_column, _rock_poly

# material novo (cor definitiva e do materials_export; aqui so o padrao para o build funcionar sozinho)
import fm_lib
fm_lib.MATS.setdefault("Water_Deep", ((0.025, 0.20, 0.46), 0.08, 0.0, 0.25, (0.03, 0.24, 0.58), 0.08))


def fall_path(top, bottom_z, out, lip=1.5, n=7, drop_curve=1.15):
    """pontos de uma queda: sai do bocal avancando 'lip' (parabola) e cai ate bottom_z"""
    o = Vector((out[0], out[1], 0.0)).normalized()
    T = Vector(top)
    H = T.z - bottom_z
    pts = []
    for i in range(n + 1):
        t = i / n
        f = min(1.0, t * 3.0)
        adv = lip * (1 - (1 - f) ** 2)
        pts.append(T + o * adv + Vector((0, 0, -H * t ** drop_curve)))
    return pts


def ribbon(mb, pts, widths, m, side, thick=0.3, bulge=0.2, fwd=None, flat=False):
    """lamina fechada varrida por pts, largura variavel (widths por ponto) e secao curva (barriga 'bulge' para frente).
    side = direcao lateral (horizontal) da lamina; fwd = para onde a barriga aponta (padrao: tangente x side).
    flat = secao retangular de 4 pontos (fios e listras finas: metade dos triangulos)."""
    bm = mb.bm
    side = Vector(side).normalized()
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        p = Vector(p)
        if i == 0:
            t = Vector(pts[1]) - p
        elif i == n - 1:
            t = p - Vector(pts[-2])
        else:
            t = Vector(pts[i + 1]) - Vector(pts[i - 1])
        t.normalize()
        f = Vector(fwd).normalized() if fwd is not None else t.cross(side)
        if f.length < 1e-6:
            f = Vector((0, 0, 1))
        f.normalize()
        w = widths[i] * 0.5
        if flat:
            prof = [(-w, 0.0), (w, 0.0), (w, -thick), (-w, -thick)]
        else:
            prof = [(-w, 0.0), (0.0, bulge), (w, 0.0), (w * 0.92, -thick), (0.0, bulge - thick), (-w * 0.92, -thick)]
        rings.append([bm.verts.new(p + side * a + f * b) for a, b in prof])
    k = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            j2 = (j + 1) % k
            try:
                bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
            except ValueError:
                pass
    for cap in (list(reversed(rings[0])), rings[-1]):
        try:
            bm.faces.new(cap)
        except ValueError:
            pass
    return mb._post([v for r in rings for v in r], m, None, 0, 1)


def foam_ring(mb, c, radius, rng, n=6, s=1.0, z=None, disc=True):
    """anel de espuma (icos achatados) + disco claro no centro: onde a queda bate"""
    c = Vector(c)
    zz = c.z if z is None else z
    a0 = rng.uniform(0, math.tau)
    for i in range(n):
        a = a0 + i * math.tau / n + rng.uniform(-0.25, 0.25)
        r = radius * rng.uniform(0.75, 1.1)
        rr = s * rng.uniform(0.55, 0.95)
        mb.ico(rr, (c.x + math.cos(a) * r, c.y + math.sin(a) * r, zz + rr * 0.12), "Foam", 1,
               (rng.uniform(1.1, 1.6), rng.uniform(1.0, 1.4), 0.38), (0, 0, rng.uniform(0, 3)), jitter=0.18)
    if disc:
        mb.cyl(radius * 0.8, 0.14, (c.x, c.y, zz + 0.05), (0, 0, rng.uniform(0, 1)), "Foam", 7, bevel=0.0)


def cascade(mb, top, bottom_z, width, rng, out=(0, -1), lip=1.5, streams=((0.0, 1.0),), widen=1.3,
            stripes=2, ring=True, lip_foam=True, n=7, ring_z=None, ring_s=None, front=True):
    """queda estilizada em laminas: por fio, lamina de tras (Water) + lamina da frente mais estreita (Water_Fall,
    ~70% = faixa central que o export_vfx mede) + listras verticais de Foam comecando em alturas diferentes;
    labio de espuma no bocal; anel de espuma na base. streams = [(deslocamento lateral, largura relativa)].
    Retorna o ponto de impacto do fio principal."""
    o = Vector((out[0], out[1], 0.0)).normalized()
    side = Vector((-o.y, o.x, 0.0))
    impact = None
    for si, (dx, wr) in enumerate(streams):
        w = width * wr
        T = Vector(top) + side * dx + Vector((0, 0, rng.uniform(-0.3, 0.3) if si else 0.0))
        pts = fall_path(T, bottom_z, o, lip * (1.0 if si == 0 else rng.uniform(0.75, 0.95)), n)
        # borda viva: a lamina oscila de lado e respira na largura (nada de regua)
        wob = [0.0] + [rng.uniform(-0.09, 0.09) * w for _ in range(n)]
        pts = [p + side * wob[i] for i, p in enumerate(pts)]
        ws = [w * (1.0 + (widen - 1.0) * (i / n)) * (1.0 if i == 0 else rng.uniform(0.9, 1.08)) for i in range(n + 1)]
        ribbon(mb, [p - o * 0.12 for p in pts], ws, "Water", side, thick=0.3, bulge=0.25)
        if front and w > 1.4:
            # faixas claras (Water_Fall) separadas por vaos onde aparece a agua de tras: le como fios verticais.
            # somadas ~70% da largura (o export_vfx mede a largura pela faixa clara)
            ks = 3 if w > 3.8 else 2
            cells = [(-0.5 + (j + 0.5) / ks) for j in range(ks)]
            for j, u in enumerate(cells):
                i0 = 0 if j == 0 else rng.randint(0, 2)
                fw = 0.7 / ks * rng.uniform(0.85, 1.1)
                sub = [p + side * ((u + rng.uniform(-0.04, 0.04)) * ws[q] * 0.92) + o * 0.14
                       for q, p in enumerate(pts)][i0:]
                ribbon(mb, sub, [ws[q + i0] * fw for q in range(len(sub))], "Water_Fall", side, thick=0.16, flat=True)
        # listras de espuma: pedacos verticais comecando em alturas diferentes, nos vaos entre as faixas claras
        for k in range(stripes if w > 2.0 else 0):
            u = rng.choice((-0.33, 0.0, 0.33)) + rng.uniform(-0.05, 0.05)
            i0 = rng.randint(max(1, n // 3), max(1, n - 2))
            sub = [p + side * (u * ws[j]) + o * 0.3 for j, p in enumerate(pts)][i0:]
            if len(sub) >= 2:
                sw = rng.uniform(0.22, 0.4) * (1.0 + 0.25 * (w > 5))
                ribbon(mb, sub, [sw * (1 + 0.8 * j / len(sub)) for j in range(len(sub))], "Foam", side, thick=0.1,
                       flat=True)
        if lip_foam:
            # labio branco no bocal: a agua "rola" por cima da borda (so o primeiro trecho curto do arco)
            lp = [pts[0], pts[0].lerp(pts[1], 0.5), pts[1]]
            ribbon(mb, [p + o * 0.2 + Vector((0, 0, 0.1)) for p in lp], [w * 1.02, w * 0.95, w * 0.62], "Foam", side,
                   thick=0.2, bulge=0.22)
        b = pts[-1] + o * 0.6
        if si == 0:
            impact = Vector((b.x, b.y, bottom_z))
        if ring:
            rz = bottom_z if ring_z is None else ring_z
            foam_ring(mb, (b.x, b.y, rz), w * 0.55 + 0.6, rng, n=(6 if w > 3 else 4),
                      s=(ring_s if ring_s else max(0.7, w * 0.22)), disc=(w > 2.5))
            # respingo: nuvenzinhas em pe onde a agua bate
            for k in range(2 if w > 2.5 else 1):
                r = max(0.6, w * rng.uniform(0.18, 0.26))
                mb.ico(r, (b.x + side.x * rng.uniform(-0.3, 0.3) * w, b.y + side.y * rng.uniform(-0.3, 0.3) * w,
                           rz + r * rng.uniform(0.4, 0.9)), "Foam", 1, (1.2, 1.1, 1.0), (0, 0, rng.uniform(0, 3)),
                       jitter=0.22)
    return impact


def chevron(mb, p, z, rng, length=None, spread=30.0, flow=(0, -1)):
    """V de espuma a jusante de uma pedra: 2 tiras a +-spread graus da corrente, abrindo rio abaixo"""
    f = Vector((flow[0], flow[1], 0.0)).normalized()
    for s in (-1, 1):
        a = math.radians(spread) * s * rng.uniform(0.85, 1.15)
        d = Vector((f.x * math.cos(a) - f.y * math.sin(a), f.x * math.sin(a) + f.y * math.cos(a), 0.0))
        ln = (length or rng.uniform(2.2, 3.6)) * rng.uniform(0.85, 1.1)
        c = Vector((p[0], p[1], z)) + d * (ln / 2 + 0.4)
        mb.box((ln, rng.uniform(0.2, 0.32), 0.07), c, (0, 0, math.atan2(d.y, d.x)), "Foam", 0.0)


def buttress(mb, cx, y_face, rng, x0, x1, depth, z0, z_top, notch_x, notch_w, notch_z, m="Cliff_Rock",
             m_wet="Cliff_Rock_Dark"):
    """contraforte de rocha no canto do terraco: massas facetadas de x0 a x1 (face em y_face, para -Y),
    com ENTALHE em V em notch_x (fundo em notch_z) e a parede do entalhe em rocha escura molhada.
    Retorna o ponto do bocal (onde a agua sai)."""
    # parede do fundo do entalhe (rocha molhada, recuada) - sobe ate o fundo do entalhe
    back = [(-notch_w * 0.55, -0.4), (notch_w * 0.55, -0.4), (notch_w * 0.7, 2.6), (-notch_w * 0.7, 2.6)]
    rock_column(mb, Vector((notch_x, y_face + 1.6, 0)), back, z0, notch_z, rng, m_wet, taper=0.9, rings=2,
                jitter=0.08, tilt=0.03)
    # flancos: massas de alturas diferentes subindo para os lados (o V), mais altas junto ao penhasco
    left = [(x0, notch_x - notch_w * 0.5)]
    right = [(notch_x + notch_w * 0.5, x1)]
    for (a, b), side in ((left[0], -1), (right[0], 1)):
        span = b - a
        if span < 1.5:
            continue
        k = 1 if span < 5.5 else 2
        for i in range(k):
            sa = a + span * i / k
            sb = a + span * (i + 1) / k
            cxx = (sa + sb) / 2
            near_notch = (i == k - 1) if side < 0 else (i == 0)
            zt = notch_z + (rng.uniform(3.0, 5.0) if near_notch else rng.uniform(7.0, 11.0))
            if z_top is not None and not near_notch:
                zt = max(zt, z_top + rng.uniform(-1.5, 1.5))
            ha = (sb - sa) * 0.62 + 0.4
            poly = _rock_poly(ha, depth * 0.5, 7, rng, ex=2.3, jit=0.12, a0=0.0)
            rock_column(mb, Vector((cxx, y_face + depth * 0.5, 0)), poly, z0, zt, rng, m if rng.random() > 0.25 else m_wet,
                        taper=rng.uniform(0.8, 0.9), rings=3, jitter=0.12, tilt=0.1,
                        lean=(0.0, -rng.uniform(0.3, 0.9)), chamfer=0.4)
    # lajes do bocal (pedras chatas que formam o labio por onde a agua rola)
    for s in (-1, 1):
        mb.rock((notch_x + s * notch_w * 0.42, y_face + 0.3, notch_z + 0.1), (notch_w * 0.5, 2.4, 1.3), m, 1,
                (0, 0, rng.uniform(-0.3, 0.3)), jitter=0.18)
    return Vector((notch_x, y_face - 0.2, notch_z + 0.35))
