# fm_arch_kit - kit da arquitetura secundaria (loja, cabanas, casa da roda, telheiros).
# Linguagem de forma: telhas em fiadas irregulares com cumeeira arqueada, guarda-ventos grossos com chifres cruzados,
# oitoes com enxaimel e janelinha, balancos (jetty) com mao-francesa, lucarnas e empenas cruzadas, chamines de pedra
# com ombro, meias-aguas em pilares, fundacao de pedra irregular e portas reais de duas folhas.
# Tudo e GEOMETRIA + COR SOLIDA (cada material vira uma MeshPart no Roblox); variacao de cor = materiais alternados.
import math, random
import bmesh
from mathutils import Vector
from fm_lib import MB, D, MATS, col_box, marker, light
from fm_parts import Frame, P3


class AMB(MB):
    """MB da arquitetura: as faces de chanfro recebem o material da propria peca.
    (No MB base o bevel cria as faces novas com material 0 - o primeiro material do objeto - e toda peca chanfrada
    ganha um contorno dessa cor: telha vermelha com borda de pedra escura, viga com borda cinza. No Roblox esses
    chanfros iam todos para a MeshPart do material 0.)"""

    def _post(self, verts, m, tint, bevel, seg, angle=0.5):
        verts = [v for v in verts if v.is_valid]
        faces = {f for v in verts for f in v.link_faces}
        mi = self._mi(m)
        t = self.rng.uniform(-1, 1) if tint is None else tint
        for f in faces:
            f.material_index = mi
            f[self.tint] = t
            f.smooth = False
        if bevel and bevel > 0:
            self.bm.normal_update()
            edges = {e for v in verts for e in v.link_edges}
            edges = [e for e in edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > angle]
            if edges:
                bmesh.ops.bevel(self.bm, geom=edges, offset=bevel, offset_type="OFFSET", segments=seg, profile=0.5,
                                affect="EDGES", clamp_overlap=True, material=mi)
        return faces

# materiais novos da arquitetura (registrados antes de make_materials: o modulo e importado pelo build)
MATS.setdefault("Roof_Slate_Blue", ((0.10, 0.115, 0.16), 0.75, 0.0, 0, None, 0.12))
MATS.setdefault("Roof_Red_Deep", ((0.28, 0.055, 0.04), 0.7, 0.0, 0, None, 0.10))
MATS.setdefault("Roof_Shingle_Wood", ((0.24, 0.12, 0.05), 0.8, 0.0, 0, None, 0.16))
MATS.setdefault("Roof_Shingle_Moss", ((0.16, 0.20, 0.07), 0.85, 0.0, 0, None, 0.14))
MATS.setdefault("Plaster_Ochre", ((0.62, 0.40, 0.21), 0.9, 0.0, 0, None, 0.08))
MATS.setdefault("Wood_Teal", ((0.03, 0.16, 0.18), 0.7, 0.0, 0, None, 0.06))
MATS.setdefault("Wood_Painted_Red", ((0.36, 0.06, 0.045), 0.7, 0.0, 0, None, 0.06))


def sub(F, x, y, da=0.0, z=0.0):
    """sub-referencial no ponto local (x, y) de F, girado de da"""
    p = F.p(x, y, z)
    return Frame(p.x, p.y, p.z, F.a + da)


def lrng(*key):
    """rng local deterministico (nao consome a sequencia compartilhada dos modulos)"""
    return random.Random(hash(tuple(round(float(k), 2) for k in key)) & 0x7fffffff)


# ------------------------------------------------------------------ primitivas
def hexa(mb, bot, top, m, bevel=0.0, tint=None):
    """hexaedro livre: bot/top = 4 pontos cada (mesma ordem); aceita trapezios e faces levemente torcidas"""
    b = [Vector(p) for p in bot]
    t = [Vector(p) for p in top]
    n = (b[1] - b[0]).cross(b[3] - b[0])
    if n.dot((t[0] + t[2]) / 2 - (b[0] + b[2]) / 2) < 0:
        b = [b[0], b[3], b[2], b[1]]
        t = [t[0], t[3], t[2], t[1]]
    vb = [mb.bm.verts.new(p) for p in b]
    vt = [mb.bm.verts.new(p) for p in t]
    faces = [list(reversed(vb)), vt] + [[vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i]] for i in range(4)]
    for f in faces:
        try:
            mb.bm.faces.new(f)
        except ValueError:
            pass
    mb._post(vb + vt, m, tint, bevel, 1, angle=0.35)


def tile_piece(mb, pb0, pb1, pt1, pt0, N, th, jl, m, ch=0.13):
    """telha barata (16 tris): secao pentagonal com o bico de baixo chanfrado - o chanfro pega a luz como um bevel.
    pb0/pb1 = borda de baixo (s0/s1), pt0/pt1 = borda de cima, N = normal da agua."""
    def sec(pb, pt):
        U = pt - pb
        lu = U.length
        U = U / lu if lu > 1e-6 else Vector((0, 0, 1))
        c = min(ch, 0.3 * lu)
        return [pb + N * 0.02, pb + N * (th + jl - c), pb + N * (th + jl) + U * c, pt + N * th * 0.55,
                pt + N * 0.02]
    v0 = [mb.bm.verts.new(p) for p in sec(pb0, pt0)]
    v1 = [mb.bm.verts.new(p) for p in sec(pb1, pt1)]
    faces = [list(reversed(v0)), v1] + [[v0[i], v0[i + 1], v1[i + 1], v1[i]] for i in range(4)] + \
            [[v0[4], v0[0], v1[0], v1[4]]]
    for f in faces:
        try:
            mb.bm.faces.new(f)
        except ValueError:
            pass
    mb._post(v0 + v1, m, None, 0, 1)


def vprism(mb, F, pts, a0, a1, m, axis="y", bevel=0.0, tint=None):
    """poligono no plano vertical local (u, z) extrudado entre a0 e a1 ao longo do eixo local 'axis'
    axis='y': u = x local; axis='x': u = y local"""
    if axis == "y":
        mk = lambda u, z, a: F.p(u, a, z)
    else:
        mk = lambda u, z, a: F.p(a, u, z)
    vb = [mb.bm.verts.new(mk(u, z, a0)) for u, z in pts]
    vt = [mb.bm.verts.new(mk(u, z, a1)) for u, z in pts]
    n = len(pts)
    faces = [list(reversed(vb)), vt] + [[vb[i], vb[(i + 1) % n], vt[(i + 1) % n], vt[i]] for i in range(n)]
    for f in faces:
        try:
            mb.bm.faces.new(f)
        except ValueError:
            pass
    mb._post(vb + vt, m, tint, bevel, 1, angle=0.5)


def lbox(mb, F, size, x, y, z, m, bevel=0.1, rx=0.0, ry=0.0, rz=0.0):
    """caixa em coordenadas locais de F"""
    mb.box(size, F.p(x, y, z), F.r(rx, ry, rz), m, bevel)


def lbeam(mb, F, a, b, w, h, m="Wood_Dark", bevel=0.06):
    mb.beam(F.p(*a), F.p(*b), w, h, m, bevel)


# ------------------------------------------------------------------ plano de telhado em fiadas
def roof_plane(mb, E0, E1, R0, R1, rng, m="Roof", m2=None, alt=0.2, th=0.42, lip=0.3, course=1.55,
               tile=(1.9, 3.0), gap=0.13, sag=0.0, s_lim=None, holes=(), under_m="Wood_Dark", bevel=0.07,
               under=True, jit=1.0, bands=3):
    """agua de telhado: E0->E1 = linha do beiral, R0->R1 = linha da cumeeira (mapa bilinear; R0 == R1 = triangulo).
    Fiadas de telhas (hexaedros com bico levantado) com juntas desencontradas, larguras e bicos irregulares,
    ~alt de telhas no material m2 (cor visivel no Roblox). sag = cumeeira arqueada (desce no meio).
    s_lim(u) -> (s0, s1) recorta o plano (quadril, vale); holes = [(s0, s1, u0, u1)] sem telha."""
    E0, E1, R0, R1 = map(Vector, (E0, E1, R0, R1))
    L = (E1 - E0).length
    if L < 0.3:
        return None
    dirL = (E1 - E0) / L

    def P(s, u):
        t = s / L
        e = E0.lerp(E1, t)
        r = R0.lerp(R1, t)
        p = e.lerp(r, u)
        if sag:
            tt = min(max(t, 0.0), 1.0)
            p = p - Vector((0, 0, sag * math.sin(math.pi * tt) * (0.35 + 0.65 * u)))
        return p
    Rm, Em = (R0 + R1) / 2, (E0 + E1) / 2
    N = dirL.cross(Rm - Em).normalized()
    if N.z < 0:
        N = -N
    slope_len = (Rm - Em).length
    lim = s_lim or (lambda u: (0.0, L))
    n = max(2, int(round(slope_len / course)))
    ov = min(0.42 / max(slope_len, 0.1), 0.25)
    for i in range(n):
        u0 = i / n
        u1 = min((i + 1) / n + ov, 1.0 + 0.2 / max(slope_len, 0.1))
        a0, b0 = lim(u0)
        a1, b1 = lim(min(u1, 1.0))
        smin, smax = min(a0, a1), max(b0, b1)
        s = smin - (rng.uniform(0.3, tile[0]) if i % 2 else rng.uniform(0.0, 0.5))
        while s < smax - 0.05:
            wdt = rng.uniform(*tile)
            spans = [(s, s + wdt - gap)]
            s += wdt
            for (hs0, hs1, hu0, hu1) in holes:
                if u1 > hu0 and u0 < hu1:
                    nsp = []
                    for (x0, x1) in spans:
                        if x1 <= hs0 or x0 >= hs1:
                            nsp.append((x0, x1))
                            continue
                        if hs0 - x0 > 0.35:
                            nsp.append((x0, hs0))
                        if x1 - hs1 > 0.35:
                            nsp.append((hs1, x1))
                    spans = nsp
            for (sa, sb) in spans:
                ba, bb = max(sa, a0), min(sb, b0)
                ta, tb = max(sa, a1), min(sb, b1)
                if bb - ba < 0.2 and tb - ta < 0.2:
                    continue
                if bb - ba < 0.15:
                    c = min(max((sa + sb) / 2, a0), b0)
                    ba, bb = c - 0.075, c + 0.075
                if tb - ta < 0.15:
                    c = min(max((sa + sb) / 2, a1), b1)
                    ta, tb = c - 0.075, c + 0.075
                jl = lip + rng.uniform(-0.08, 0.1) * jit
                du = rng.uniform(-0.05, 0.05) * jit / max(slope_len, 1.0)
                pb0, pb1 = P(ba, u0 + du), P(bb, u0 + du)
                pt1, pt0 = P(tb, u1), P(ta, u1)
                mm = m2 if (m2 and rng.random() < alt) else m
                if bevel > 0:
                    tile_piece(mb, pb0, pb1, pt1, pt0, N, th, jl, mm)
                else:
                    bot = [pb0 + N * 0.02, pb1 + N * 0.02, pt1 + N * 0.02, pt0 + N * 0.02]
                    top = [pb0 + N * (th + jl), pb1 + N * (th + jl), pt1 + N * th * 0.55, pt0 + N * th * 0.55]
                    hexa(mb, bot, top, mm, 0.0)
    if under:
        # forro (visto por dentro e sob o beiral): 1 faixa em aguas retangulares, mais faixas se ha recorte
        nseg = 3 if sag else 1
        bands = bands if s_lim else 1
        for kb in range(bands):
            ua, ub = kb / bands, (kb + 1) / bands
            la0, lb0 = lim(ua)
            la1, lb1 = lim(ub)
            for k in range(nseg):
                f0, f1 = k / nseg, (k + 1) / nseg
                q = [P(la0 + (lb0 - la0) * f0, ua), P(la0 + (lb0 - la0) * f1, ua),
                     P(la1 + (lb1 - la1) * f1, ub), P(la1 + (lb1 - la1) * f0, ub)]
                if (q[1] - q[0]).length < 0.05 and (q[2] - q[3]).length < 0.05:
                    continue
                hexa(mb, [p - N * 0.28 for p in q], [p + N * 0.06 for p in q], under_m, 0.0)
    return P, N, L


# ------------------------------------------------------------------ telhado de duas aguas completo
def gable_roof(mb, F, cx, ya, yb, z_r, rng, sides=((6.0, 10.0, 1.2), (6.0, 10.0, 1.2)),
               ends=((1.0, 0.0), (1.0, 0.0)), m="Roof", m2=None, alt=0.2, sag=0.25, ridge_m="Wood_Dark",
               barge_m="Wood_Dark", horns=(True, True), holes=((), ()), tile=(1.9, 3.0), course=1.55, th=0.42,
               lip=0.3, fascia=True, rafters=0.0, valley=(None, None), barge=True, under_m="Wood_Dark",
               ridge_w=1.05, bevel=0.07, horn_len=1.2):
    """telhado de 2 aguas, cumeeira no eixo local Y (x = cx, de ya a yb) na cota z_r.
    sides[k] = (hw, z_na_parede, beiral) para k=0 (agua -x) e k=1 (agua +x): assimetria (saltbox, beirais).
    ends[k] = (beiral_oitao, h_quadril) na ponta ya (k=0) e yb (k=1); h_quadril > 0 = meia-tesoura (jerkinhead).
    valley[k] = (y_beiral, y_cumeeira): a ponta k morre em outra agua (lucarna / empena cruzada).
    holes[k] = [(y0, y1, dist0, dist1)]: sem telha na agua k (dist = distancia horizontal da cumeeira)."""
    Ys = ya - ends[0][0]
    Ye = yb + ends[1][0]
    if valley[0] is not None:
        Ys = min(valley[0]) - 0.6
    if valley[1] is not None:
        Ye = max(valley[1]) + 0.6
    L = Ye - Ys
    hiplen = [ends[k][1] * 1.15 for k in (0, 1)]
    info = {"Ys": Ys, "Ye": Ye, "L": L, "P": [None, None], "N": [None, None]}

    def make_lim(H):
        def lim(u):
            s0, s1 = 0.0, L
            if valley[0] is not None:
                y_e, y_r = valley[0]
                s0 = (y_e + (y_r - y_e) * u) - Ys - 0.3
            elif ends[0][1] > 0:
                uh = max(0.0, 1 - ends[0][1] / H)
                if u > uh:
                    s0 = (u - uh) / (1 - uh) * (ends[0][0] + hiplen[0])
            if valley[1] is not None:
                y_e, y_r = valley[1]
                s1 = (y_e + (y_r - y_e) * u) - Ys + 0.3
            elif ends[1][1] > 0:
                uh = max(0.0, 1 - ends[1][1] / H)
                if u > uh:
                    s1 = L - (u - uh) / (1 - uh) * (ends[1][0] + hiplen[1])
            return s0, s1
        return lim

    slopes = []
    for k, sgn in ((0, -1), (1, 1)):
        hw, zw, ov = sides[k]
        g = (z_r - zw) / hw
        xe = cx + sgn * (hw + ov)
        ze = z_r - g * (hw + ov)
        H = z_r - ze
        E0, E1 = F.p(xe, Ys, ze), F.p(xe, Ye, ze)
        R0, R1 = F.p(cx, Ys, z_r), F.p(cx, Ye, z_r)
        lim = make_lim(H)
        hl = []
        for (hy0, hy1, d0, d1) in holes[k]:
            hl.append((hy0 - Ys, hy1 - Ys, 1 - d1 / (hw + ov), 1 - d0 / (hw + ov)))
        res = roof_plane(mb, E0, E1, R0, R1, rng, m, m2, alt, th, lip, course, tile, 0.13, sag, lim, hl, under_m,
                         bevel)
        P, N, _ = res
        info["P"][k], info["N"][k] = P, N
        slopes.append((k, sgn, hw, zw, ov, g, xe, ze, H, lim, P, N))
        # testeira (fascia) no beiral
        if fascia:
            a0, b0 = lim(0.0)
            pts = [P(a0 + (b0 - a0) * f / 3, 0.0) for f in range(4)]
            for pa, pb in zip(pts, pts[1:]):
                d = (pb - pa).normalized()
                mb.beam(pa - d * 0.1 - N * 0.12, pb + d * 0.1 - N * 0.12, 0.42, 0.75, barge_m, 0.06)
        # caibros aparentes sob o beiral
        if rafters > 0:
            y = ya + rafters * 0.5
            while y < yb - 0.2:
                zr_w = zw - 0.3
                mb.beam(F.p(cx + sgn * (hw - 0.4), y, zr_w + g * 0.4), F.p(xe + sgn * 0.1, y, ze - 0.3),
                        0.4, 0.5, barge_m, 0.0)
                y += rafters
    # cumeeira (segue o arco) + chifres cruzados nos oitoes + guarda-ventos
    k0 = slopes[0]
    P0, N0 = k0[10], k0[11]
    s_a, s_b = k0[9](1.0)
    if valley[1] is not None:
        s_b = valley[1][1] - Ys + 0.25
    if valley[0] is not None:
        s_a = valley[0][1] - Ys - 0.25
    nseg = 5 if sag else 2
    rp = []
    for i in range(nseg + 1):
        s = s_a + (s_b - s_a) * i / nseg
        p = P0(s, 1.0)
        rp.append(Vector((p.x, p.y, p.z + th + 0.2)))
    for pa, pb in zip(rp, rp[1:]):
        d = (pb - pa).normalized()
        mb.beam(pa - d * 0.15, pb + d * 0.15, ridge_w, 0.85, ridge_m, 0.1)
    for e, (end_s, outsgn) in enumerate(((0.0, -1), (L, 1))):
        if valley[e] is not None:
            continue
        hip_h = ends[e][1]
        for (k, sgn, hw, zw, ov, g, xe, ze, H, lim, P, N) in slopes:
            uh = max(0.0, 1 - hip_h / H) if hip_h > 0 else 1.0
            if barge and uh > 0.05:
                pa = P(end_s, 0.0) + N * (th * 0.45)
                pb = P(end_s, uh) + N * (th * 0.45)
                d = (pb - pa).normalized()
                off = F.p(0, outsgn * 0.12) - F.p(0, 0)
                ext = horn_len if (hip_h <= 0 and horns[e]) else 0.25
                mb.beam(pa - d * 0.35 + off, pb + d * ext + off, 0.5, 1.15, barge_m, 0.08)
            if hip_h > 0:
                # espigao do quadril
                pa = P(end_s, uh)
                s_top = k0[9](1.0)[0] if e == 0 else k0[9](1.0)[1]
                pb = P(s_top, 1.0)
                d = (pb - pa).normalized()
                mb.beam(pa + N * (th + 0.15) - d * 0.2, pb + N * (th + 0.15) + d * 0.2, 0.8, 0.7, ridge_m, 0.08)
        if hip_h > 0:
            # agua do quadril (triangulo) - fecha a ponta cortada
            (_, _, hwl, zwl, ovl, gl, *_r) = slopes[0]
            (_, _, hwr, zwr, ovr, gr, *_r2) = slopes[1]
            zh = z_r - hip_h
            yy = Ys if e == 0 else Ye
            s_apex = (ends[0][0] + hiplen[0]) if e == 0 else L - (ends[1][0] + hiplen[1])
            apex = P0(s_apex, 1.0)
            El = F.p(cx - hip_h / gl, yy, zh)
            Er = F.p(cx + hip_h / gr, yy, zh)
            ov_h = F.p(0, -0.35 if e == 0 else 0.35) - F.p(0, 0)
            El, Er = El + ov_h - Vector((0, 0, 0.15)), Er + ov_h - Vector((0, 0, 0.15))
            roof_plane(mb, El, Er, apex, apex, rng, m, m2, alt, th, lip, max(course, hip_h * 0.55), tile, 0.13, 0.0,
                       None, (), under_m, bevel, bands=1)
            if fascia:
                mb.beam(El - N0 * 0.0 + Vector((0, 0, -0.1)), Er + Vector((0, 0, -0.1)), 0.42, 0.7, barge_m, 0.06)
    info["slopes"] = slopes
    return info


# ------------------------------------------------------------------ oitao (triangulo) com enxaimel
def gable_infill(mb, F, y, x_l, x_r, cx, z0, z_apex, thick, rng, m_p="Plaster", m_t="Wood_Dark", z_clip=None,
                 style="king", window=None, both=True, out_sign=-1):
    """oitao no plano local y. style: 'king' (pendural + escoras), 'cross' (Aspa), 'collar' (linha alta + montantes),
    'plain'. window = (largura, altura, z_centro) -> janelinha acesa com caixilho."""
    if z_clip is not None and z_clip < z_apex - 0.2:
        f = (z_clip - z0) / (z_apex - z0)
        xl2, xr2 = x_l + (cx - x_l) * f, x_r + (cx - x_r) * f
        pts = [(x_l, z0), (x_r, z0), (xr2, z_clip), (xl2, z_clip)]
        zt = z_clip
    else:
        pts = [(x_l, z0), (x_r, z0), (cx, z_apex)]
        zt = z_apex
    vprism(mb, F, pts, y - thick / 2, y + thick / 2, m_p, "y")
    H = zt - z0

    def half_w(z):
        f = (z - z0) / (z_apex - z0)
        return (x_r - x_l) / 2 * (1 - f)
    wz0 = wz1 = None
    if window:
        ww, wh, wzc = window
        wz0, wz1 = wzc - wh / 2, wzc + wh / 2
        mb.box((ww, thick + 0.1, wh), F.p(cx, y, wzc), F.r(), "Lantern_Glow", 0.0)
        mb.box((ww, thick + 0.16, 0.22), F.p(cx, y, wzc), F.r(), "Wood_Dark", 0.0)
        mb.box((0.22, thick + 0.16, wh), F.p(cx, y, wzc), F.r(), "Wood_Dark", 0.0)
    sides = (out_sign, -out_sign) if both else (out_sign,)
    for sd in sides:
        yy = y + sd * (thick / 2 + 0.12)
        b6 = 0.06 if sd == out_sign else 0.0      # lado de dentro sem chanfro (economia)
        b5 = 0.05 if sd == out_sign else 0.0
        # linha (frechal do oitao)
        mb.box((x_r - x_l, 0.5, 0.6), F.p((x_l + x_r) / 2, yy, z0 + 0.3), F.r(), m_t, b6)
        if window:
            ww, wh, wzc = window
            # caixilho
            mb.box((ww + 0.9, 0.5, 0.5), F.p(cx, yy, wz0 - 0.2), F.r(), m_t, b6)
            mb.box((ww + 0.6, 0.5, 0.45), F.p(cx, yy, wz1 + 0.2), F.r(), m_t, b6)
            for sx in (-1, 1):
                mb.box((0.45, 0.5, wh + 0.4), F.p(cx + sx * (ww / 2 + 0.2), yy, wzc), F.r(), m_t, b6)
        if style == "plain":
            continue
        if sd != out_sign and style in ("cross", "king"):
            # lado de dentro: so o pendural (as escoras ficam na fachada)
            if not window:
                mb.box((0.6, 0.5, H - 0.35), F.p(cx, yy, z0 + (H - 0.35) / 2), F.r(), m_t, 0.0)
            continue
        if style in ("king", "collar"):
            if window:
                if wz0 - z0 > 0.8:
                    mb.box((0.55, 0.5, wz0 - 0.4 - z0), F.p(cx, yy, (z0 + wz0 - 0.4) / 2), F.r(), m_t, b6)
                if zt - wz1 > 0.9:
                    mb.box((0.55, 0.5, zt - 0.3 - wz1 - 0.4), F.p(cx, yy, (wz1 + 0.4 + zt - 0.3) / 2), F.r(), m_t,
                           b6)
            else:
                mb.box((0.6, 0.5, H - 0.35), F.p(cx, yy, z0 + (H - 0.35) / 2), F.r(), m_t, b6)
        if style == "king":
            zk = z0 + H * (0.5 if not window else min(0.5, (wz0 - z0) / H * 0.9 + 0.05))
            for sx in (-1, 1):
                xa = cx + sx * (x_r - x_l) / 2 * 0.62
                xb = cx + sx * 0.3
                if window and zk > wz0 - 0.2:
                    xb = cx + sx * (window[0] / 2 + 0.45)
                    zk2 = wz0 - 0.1
                else:
                    zk2 = zk
                mb.beam(F.p(xa, yy, z0 + 0.5), F.p(xb, yy, zk2), 0.5, 0.42, m_t, b5)
        elif style == "collar":
            zc = z0 + H * 0.52
            hw = half_w(zc)
            if not window or zc < wz0 - 0.4 or zc > wz1 + 0.4:
                mb.beam(F.p(cx - hw + 0.3, yy, zc), F.p(cx + hw - 0.3, yy, zc), 0.5, 0.45, m_t, b5)
            for sx in (-1, 1):
                xx = cx + sx * (x_r - x_l) / 2 * 0.45
                mb.box((0.5, 0.5, max(0.3, zc - z0 - 0.6)), F.p(xx, yy, (z0 + 0.6 + zc) / 2), F.r(), m_t, b5)
        elif style == "cross":
            zc = z0 + H * 0.62
            hw = half_w(zc)
            for sx in (-1, 1):
                mb.beam(F.p(cx - sx * (x_r - x_l) / 2 * 0.72, yy, z0 + 0.5), F.p(cx + sx * hw * 0.8, yy, zc), 0.45,
                        0.42, m_t, b5)


# ------------------------------------------------------------------ balanco (jetty) e maos-francesas
def jetty_band(mb, F, x0, x1, y_face, out, z_top, rng, out_sign=-1, m="Wood_Dark", step=1.5, brackets=2,
               joists=True, depth_in=1.2):
    """faixa de balanco ao longo da parede local (x0..x1 no plano y_face); a parede de cima avanca 'out'"""
    L_ = x1 - x0
    cxx = (x0 + x1) / 2
    ydepth = out + depth_in
    yc = y_face + out_sign * (out - depth_in) / 2
    lbox(mb, F, (L_, ydepth, 0.85), cxx, yc, z_top - 0.42, m, 0.1)
    if joists:
        x = x0 + step * 0.5
        while x < x1 - 0.3:
            lbox(mb, F, (0.5, out + 0.55, 0.55), x, y_face + out_sign * (out + 0.55) / 2, z_top - 1.1, m, 0.0)
            x += step
    if brackets:
        xs = [x0 + 0.7, x1 - 0.7] if brackets == 2 else [x0 + 0.7, cxx, x1 - 0.7]
        for x in xs:
            lbeam(mb, F, (x, y_face + out_sign * 0.1, z_top - 3.0), (x, y_face + out_sign * (out - 0.05), z_top - 0.9),
                  0.45, 0.5, m, 0.05)


def gable_jetty(mb, F, x_l, x_r, y_wall, jet, z, rng, out_sign=-1, m="Wood_Dark", nbr=2):
    """oitao projetado na altura do beiral: viga (bressumer) + consolos"""
    lbox(mb, F, (x_r - x_l + 0.5, jet + 1.0, 0.95), (x_l + x_r) / 2, y_wall + out_sign * (jet - 1.0) / 2 + out_sign * 0.3,
         z - 0.47, m, 0.1)
    xs = [x_l + 0.7, x_r - 0.7] if nbr == 2 else [x_l + 0.7, (x_l + x_r) / 2, x_r - 0.7]
    for x in xs:
        lbeam(mb, F, (x, y_wall + out_sign * 0.1, z - 2.8), (x, y_wall + out_sign * (jet + 0.2), z - 0.85), 0.5, 0.55,
              m, 0.05)
        lbox(mb, F, (0.6, 0.6, 0.9), x, y_wall + out_sign * (jet + 0.25), z - 1.2, m, 0.08)


# ------------------------------------------------------------------ chamine de pedra com ombro
def chimney(mb, F, x, y, z0, z_top, rng, w=3.2, d=2.4, w2=2.1, d2=1.7, z_sh=None, m="Stone_Light", m2="Stone_Dark",
            off=(0.0, 0.0), pot=True, name=None):
    """chamine: base larga (lareira) -> ombro inclinado -> fuste estreito com cintas -> capa + pote.
    x, y locais; off = deslocamento do fuste (assimetria)."""
    z_sh = z_sh if z_sh is not None else z0 + (z_top - z0) * 0.45
    from fm_parts import frustum
    wb, db = w, d
    if z_sh - z0 > 9.0:
        # base alta: recua uma vez a meia altura (ressalto inclinado) - a chamine nao vira um bloco liso
        zm = z0 + (z_sh - z0) * 0.5
        lbox(mb, F, (w, d, zm - z0), x, y, (z0 + zm) / 2, m, 0.18)
        wb, db = w - 0.4, d - 0.3
        frustum(mb, F.p(x, y, zm), w, d, wb, db, 0.55, m2, ang=F.a)
        lbox(mb, F, (wb, db, z_sh - zm - 0.55), x, y, (zm + 0.55 + z_sh) / 2, m, 0.16)
    else:
        lbox(mb, F, (w, d, z_sh - z0), x, y, (z0 + z_sh) / 2, m, 0.18)
    # pedras de canto (quoins) irregulares na base
    for i, zz in enumerate((z0 + 0.8, z0 + 2.2, z_sh - 1.2)):
        if zz > z_sh - 0.6:
            continue
        sx = 1 if i % 2 == 0 else -1
        ww = w if zz < z0 + 3.0 or wb == w else wb
        lbox(mb, F, (1.1 + rng.uniform(0, 0.4), (d if ww == w else db) + 0.28, 0.8 + rng.uniform(-0.1, 0.15)),
             x + sx * (ww / 2 - 0.45), y, zz, m2, 0.14)
    ox, oy = off
    c0 = F.p(x, y, z_sh)
    frustum(mb, c0, wb, db, w2, d2, 1.3, m2, top_off=(ox, oy), ang=F.a)
    zs2 = z_sh + 1.3
    lbox(mb, F, (w2, d2, z_top - zs2), x + ox, y + oy, (zs2 + z_top) / 2, m, 0.16)
    bands = (zs2 + (z_top - zs2) * 0.38, z_top - 1.4) if z_top - zs2 < 7.5 else \
        (zs2 + (z_top - zs2) * 0.3, zs2 + (z_top - zs2) * 0.62, z_top - 1.4)
    for zz in bands:
        lbox(mb, F, (w2 + 0.3, d2 + 0.3, 0.5), x + ox + rng.uniform(-0.06, 0.06), y + oy, zz, m2, 0.1,
             rz=rng.uniform(-0.05, 0.05))
    lbox(mb, F, (w2 + 0.7, d2 + 0.7, 0.45), x + ox, y + oy, z_top + 0.22, m2, 0.12)
    lbox(mb, F, (w2 - 0.2, d2 - 0.2, 0.55), x + ox, y + oy, z_top + 0.7, m, 0.12)
    if pot:
        p = F.p(x + ox + rng.uniform(-0.25, 0.25), y + oy, z_top + 1.4)
        mb.cyl(0.42, 1.0, p, (0, 0, 0), "Metal_Dark", 8, r2=0.34, bevel=0.0)
        mb.cyl(0.5, 0.2, p + Vector((0, 0, 0.55)), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
    if name:
        top = F.p(x + ox, y + oy, z_top + 2.0)
        marker("VFX_Smoke_" + name, tuple(top), (0, 0, 0), 1.5, props={"particle": "smoke", "rate": 2})


# ------------------------------------------------------------------ lucarna (dormer) / empena cruzada
def dormer(mb, F, side, cx, hw, z_wall, z_r, yc, wd, rng, inset=1.4, h=3.0, rise=None, m_roof="Roof",
           m_roof2=None, m_p="Plaster", m_t="Wood_Dark", over=0.6, thick=0.9, window=True, style="king",
           front_jet=0.0, sag=0.0):
    """lucarna na agua 'side' (-1 = -x, +1 = +x) de um telhado com cumeeira no eixo local Y (x = cx).
    inset = recuo da frente em relacao a linha da parede; h = altura da parede frontal acima do telhado.
    inset = 0 e h = 0 -> empena cruzada (o oitao nasce no beiral). Retorna o furo (y0, y1, d0, d1) da agua."""
    g = (z_r - z_wall) / hw
    dist_f = hw - inset                          # distancia horizontal da cumeeira ate a frente
    z_s = z_r - g * dist_f                       # cota do telhado na frente
    rise = rise if rise is not None else wd / 2 * 0.95
    z_de = z_s + h
    z_dr = z_de + rise
    if z_dr > z_r - 0.6:
        z_dr = z_r - 0.6
        z_de = z_dr - rise
    da = D(90) if side > 0 else D(-90)
    Dm = sub(F, cx + side * dist_f, yc, da)      # local -Y aponta para fora da agua
    # quanto a lucarna entra no telhado (y local do dormer, positivo = para dentro)
    y_e = (z_de - z_s) / g
    y_r = (z_dr - z_s) / g
    fy = -front_jet
    # parede frontal + oitao
    zb = z_s - (0.5 if h > 0 else 0.0)
    if h > 0:
        pts = [(-wd / 2, zb), (wd / 2, zb), (wd / 2, z_de), (0, z_dr), (-wd / 2, z_de)]
        vprism(mb, Dm, pts, fy - thick / 2, fy + thick / 2, m_p, "y")
        # bochechas
        for sx in (-1, 1):
            cpts = [(0.0, zb), (0.0, z_de), (y_e + 0.2, z_de)]
            vprism(mb, Dm, cpts, sx * wd / 2 - 0.3, sx * wd / 2 + 0.3, m_p, "x")
        # quadro de madeira
        for sx in (-1, 1):
            lbox(mb, Dm, (0.55, 0.55, z_de - zb), sx * (wd / 2 - 0.1), fy - thick / 2 - 0.1, (zb + z_de) / 2, m_t, 0.06)
        lbox(mb, Dm, (wd + 0.3, 0.55, 0.5), 0, fy - thick / 2 - 0.1, z_de - 0.1, m_t, 0.06)
        lbox(mb, Dm, (wd + 0.3, 0.6, 0.45), 0, fy - thick / 2 - 0.1, zb + 0.35, m_t, 0.06)
        if window:
            ww = min(wd - 1.4, 2.4)
            wz0, wz1 = zb + 1.0, z_de - 0.5
            if wz1 - wz0 > 0.8:
                lbox(mb, Dm, (ww, thick + 0.1, wz1 - wz0), 0, fy, (wz0 + wz1) / 2, "Lantern_Glow", 0.0)
                lbox(mb, Dm, (0.22, thick + 0.16, wz1 - wz0), 0, fy, (wz0 + wz1) / 2, m_t, 0.0)
                lbox(mb, Dm, (ww + 0.7, 0.5, 0.35), 0, fy - thick / 2 - 0.2, wz0 - 0.15, m_t, 0.05)
                for sx in (-1, 1):
                    lbox(mb, Dm, (0.4, 0.5, wz1 - wz0 + 0.3), sx * (ww / 2 + 0.15), fy - thick / 2 - 0.12,
                         (wz0 + wz1) / 2, m_t, 0.05)
        gable_infill(mb, Dm, fy, -wd / 2, wd / 2, 0.0, z_de, z_dr, thick, rng, m_p, m_t, style="plain", both=False)
    else:
        # empena cruzada: so o triangulo acima do beiral
        gable_infill(mb, Dm, fy, -wd / 2, wd / 2, 0.0, z_de, z_dr, thick, rng, m_p, m_t, style=style,
                     window=(1.6, 1.3, z_de + rise * 0.38) if window else None, both=True)
        # cachorros do oitao projetado
        if front_jet > 0:
            gable_jetty(mb, Dm, -wd / 2, wd / 2, 0.0, front_jet, z_de, rng, -1, m_t, 2)
    gable_roof(mb, Dm, 0.0, fy, y_r, z_dr, rng,
               sides=((wd / 2, z_de, over), (wd / 2, z_de, over)),
               ends=((over + 0.2, 0.0), (0.0, 0.0)), m=m_roof, m2=m_roof2, sag=sag,
               valley=(None, (y_e, y_r)), tile=(1.5, 2.3), course=1.3, th=0.36, lip=0.26, horn_len=0.8,
               fascia=True, ridge_w=0.85)
    # furo na agua principal, no formato de gable_roof(holes=...): (y0, y1, dist0, dist1) a partir da cumeeira
    if h <= 0:
        # empena cruzada: tira o beiral principal na frente do oitao (as telhas atravessariam o triangulo)
        return (yc - wd / 2 - over + 0.15, yc + wd / 2 + over - 0.15, dist_f - 0.5, dist_f + 12.0)
    if y_e > 1.4:
        # telhas escondidas dentro da lucarna (economia)
        return (yc - wd / 2 + 0.45, yc + wd / 2 - 0.45, dist_f - y_e + 0.6, dist_f - 0.4)
    return None


# ------------------------------------------------------------------ meia-agua (alpendre, telheiro de lenha)
def lean_to(mb, F, x0, x1, y_wall, depth, z_hi, z_lo, rng, out_sign=-1, m="Roof", m2=None, posts=True,
            post_m="Wood_Dark", sag=0.12, over=0.7, side_over=0.6, braces=True, area=None, post_inset=0.5,
            tile=(1.8, 2.8), z_ground=4.0):
    """telhado de uma agua encostado na parede (plano local y_wall, eixo x de x0 a x1), caindo para out_sign*y.
    Retorna (y da viga externa, z sob a viga)."""
    ye = y_wall + out_sign * (depth + over)
    g = (z_hi - z_lo) / depth
    ze = z_lo - g * over
    E0, E1 = F.p(x0 - side_over, ye, ze), F.p(x1 + side_over, ye, ze)
    R0, R1 = F.p(x0 - side_over, y_wall + out_sign * 0.2, z_hi + 0.2 * g), F.p(x1 + side_over, y_wall + out_sign * 0.2,
                                                                                  z_hi + 0.2 * g)
    res = roof_plane(mb, E0, E1, R0, R1, rng, m, m2, 0.2, 0.4, 0.28, 1.45, tile, 0.13, sag, None, (), "Wood_Dark",
                     0.07)
    P, N, Lr = res
    # testeira e guarda-ventos
    pts = [P(Lr * f / 3, 0.0) for f in range(4)]
    for pa, pb in zip(pts, pts[1:]):
        d = (pb - pa).normalized()
        mb.beam(pa - d * 0.1 - N * 0.12, pb + d * 0.1 - N * 0.12, 0.42, 0.7, "Wood_Dark", 0.06)
    for s in (0.0, Lr):
        pa, pb = P(s, 0.0) + N * 0.2, P(s, 1.0) + N * 0.2
        mb.beam(pa, pb, 0.45, 1.0, "Wood_Dark", 0.06)
    # frechal na parede + viga externa
    lbeam(mb, F, (x0 - 0.2, y_wall + out_sign * 0.3, z_hi - 0.45), (x1 + 0.2, y_wall + out_sign * 0.3, z_hi - 0.45),
          0.55, 0.6, "Wood_Dark", 0.06)
    yb = y_wall + out_sign * (depth - post_inset)
    zb = z_lo + g * post_inset - 0.55
    lbeam(mb, F, (x0 - 0.3, yb, zb), (x1 + 0.3, yb, zb), 0.7, 0.75, "Wood_Dark", 0.07)
    if posts:
        n = max(2, int(round((x1 - x0) / 5.5)) + 1)
        zg = z_ground
        for i in range(n):
            x = x0 + 0.4 + (x1 - x0 - 0.8) * i / (n - 1)
            lbox(mb, F, (0.8, 0.8, zb - zg - 0.5), x, yb, (zb + zg + 0.5) / 2, post_m, 0.1,
                 rx=rng.uniform(-0.02, 0.02), ry=rng.uniform(-0.02, 0.02))
            lbox(mb, F, (1.4, 1.4, 0.8), x, yb, zg + 0.3, "Stone_Dark", 0.15, rz=rng.uniform(-0.2, 0.2))
            if braces:
                for sx in ((-1, 1) if 0 < i < n - 1 else ((1,) if i == 0 else (-1,))):
                    lbeam(mb, F, (x + sx * 0.3, yb, zb - 2.0), (x + sx * 1.8, yb, zb - 0.3), 0.4, 0.45, "Wood_Dark",
                          0.05)
            if area:
                q = F.p(x, yb)
                col_box(area, (1.0, 1.0, zb - zg), (q.x, q.y, (zb + zg) / 2), F.r())
    return yb, zb


# ------------------------------------------------------------------ fundacao de pedra irregular
def stone_plinth(mb, pts, z0, z1, rng, out=0.35, skip=(), m="Stone_Dark", m2="Stone_Light", mix=0.3,
                 corner=1.35, step=(1.4, 2.6)):
    """pedras irregulares ao pe das paredes; pts = poligono anti-horario (mundo). skip = [(i_aresta, s0, s1)]"""
    pts = [Vector((p[0], p[1], 0)) for p in pts]
    n = len(pts)
    h = z1 - z0
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dv = b - a
        L_ = dv.length
        t = dv / L_
        nrm = Vector((t.y, -t.x, 0))
        ang = math.atan2(t.y, t.x)
        # pedra de canto
        c = a + nrm * (out * 0.4) - t * 0.1
        cs = corner * rng.uniform(0.9, 1.15)
        mb.box((cs * 1.5, cs * 1.3, h * rng.uniform(1.05, 1.3)), (c.x, c.y, z0 + h * 0.55),
               (rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), ang + rng.uniform(-0.12, 0.12)),
               m if rng.random() > 0.3 else m2, 0.2)
        s = 1.0
        while s < L_ - 1.0:
            w = rng.uniform(*step)
            sa, sb = s, min(s + w, L_ - 0.9)
            s += w
            if sb - sa < 0.5:
                continue
            if any(e == i and sb > k0 and sa < k1 for (e, k0, k1) in skip):
                continue
            hh = h * rng.uniform(0.75, 1.1)
            dep = 0.8 + out * rng.uniform(0.7, 1.25)
            c = a + t * ((sa + sb) / 2) + nrm * (dep / 2 - 0.55)
            mb.box((sb - sa - 0.1, dep, hh), (c.x, c.y, z0 + hh / 2),
                   (rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), ang + rng.uniform(-0.05, 0.05)),
                   m2 if rng.random() < mix else m, 0.16)


# ------------------------------------------------------------------ porta real de duas folhas (abertas para fora)
def door_leaves(mb, F, x0, x1, y_face, z0, h, rng, out_sign=-1, m="Wood_Plank", strap_m="Metal_Dark",
                open_deg=(108, 116), trim_m="Wood_Dark"):
    wl = (x1 - x0) / 2 - 0.06
    for hinge, sgn in ((x0, 1), (x1, -1)):
        th = D(rng.uniform(*open_deg))
        # direcao da folha: fechada = sgn*x; abre girando para out_sign*y
        dx, dy = sgn * math.cos(th), out_sign * math.sin(th)
        a = math.atan2(dy, dx)
        Fl = Frame(F.p(hinge, y_face).x, F.p(hinge, y_face).y, 0.0, F.a + a)
        lbox(mb, Fl, (wl, 0.32, h), wl / 2, 0, z0 + h / 2, m, 0.08)
        for zz in (z0 + 1.1, z0 + h - 1.2):
            lbox(mb, Fl, (wl * 0.8, 0.44, 0.34), wl * 0.42, 0, zz, strap_m, 0.0)
        lbox(mb, Fl, (wl - 0.3, 0.42, 0.45), wl / 2, 0, z0 + h * 0.5, trim_m, 0.0)
        mb.cyl(0.28, 0.12, Fl.p(wl - 0.45, 0.28, z0 + h * 0.46), Fl.r(D(90), 0, 0), "Metal_Brass", 8, bevel=0.0)


# ------------------------------------------------------------------ janela saliente (oriel / bay)
def bay_window(mb, F, xc, y_face, z0, z1, wd, out, rng, out_sign=-1, m_t="Wood_Dark", roof_m="Roof",
               base_m="Wood_Dark"):
    yo = y_face + out_sign * out
    ym = y_face + out_sign * out / 2
    lbox(mb, F, (wd + 0.5, out + 0.4, 0.55), xc, ym + out_sign * 0.1, z0 - 0.1, base_m, 0.1)
    # vidros (frente + lados)
    lbox(mb, F, (wd - 0.6, 0.25, z1 - z0 - 0.5), xc, yo - out_sign * 0.1, (z0 + z1) / 2, "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        lbox(mb, F, (0.25, out - 0.3, z1 - z0 - 0.5), xc + sx * (wd / 2 - 0.25), ym, (z0 + z1) / 2, "Lantern_Glow", 0.0)
        lbox(mb, F, (0.5, 0.5, z1 - z0), xc + sx * (wd / 2 - 0.1), yo - out_sign * 0.12, (z0 + z1) / 2, m_t, 0.06)
    lbox(mb, F, (0.35, 0.35, z1 - z0), xc, yo - out_sign * 0.05, (z0 + z1) / 2, m_t, 0.0)
    lbox(mb, F, (wd, 0.35, 0.3), xc, yo - out_sign * 0.05, z0 + (z1 - z0) * 0.62, m_t, 0.0)
    # telhadinho
    ang = math.atan2(0.9, out + 0.5)
    lbox(mb, F, (wd + 0.8, out + 0.9, 0.35), xc, ym + out_sign * 0.15, z1 + 0.35, roof_m, 0.08, rx=-out_sign * ang)
    # consolos
    for sx in (-1, 1):
        lbeam(mb, F, (xc + sx * (wd / 2 - 0.5), y_face + out_sign * 0.1, z0 - 2.0),
              (xc + sx * (wd / 2 - 0.5), yo - out_sign * 0.2, z0 - 0.35), 0.4, 0.45, m_t, 0.05)


# ------------------------------------------------------------------ janelas: postigos, floreira, peitoril
def shutters(mb, F, x0, x1, y_face, z0, z1, rng, out_sign=-1, m="Wood_Teal", batten_m="Wood_Dark"):
    w = (x1 - x0) / 2 * 0.95
    for xh, sgn in ((x0, -1), (x1, 1)):
        a = D(rng.uniform(6, 22)) * sgn * out_sign
        Fs = Frame(F.p(xh, y_face + out_sign * 0.3).x, F.p(xh, y_face + out_sign * 0.3).y, 0.0, F.a + a)
        lbox(mb, Fs, (w, 0.22, z1 - z0), sgn * w / 2, 0, (z0 + z1) / 2, m, 0.05)
        for zz in (z0 + 0.5, z1 - 0.5):
            lbox(mb, Fs, (w * 0.9, 0.32, 0.28), sgn * w / 2, 0, zz, batten_m, 0.0)


def flower_box(mb, F, x0, x1, y_face, z, rng, out_sign=-1, flowers=("Leaf_Sakura", "Leaf_Pine_Light", "Cloth_Red")):
    L_ = x1 - x0
    lbox(mb, F, (L_ + 0.3, 0.9, 0.7), (x0 + x1) / 2, y_face + out_sign * 0.55, z - 0.35, "Wood_Plank", 0.08)
    n = max(2, int(L_ / 0.9))
    for i in range(n):
        x = x0 + 0.4 + (L_ - 0.8) * i / max(1, n - 1)
        p = F.p(x + rng.uniform(-0.15, 0.15), y_face + out_sign * (0.55 + rng.uniform(-0.1, 0.15)), z + 0.15)
        mm = flowers[0] if i % 2 == 0 else flowers[1]
        if rng.random() < 0.2:
            mm = flowers[2]
        mb.ico(rng.uniform(0.42, 0.58), p, mm, 1, (1, 1, 0.8), jitter=0.2)


def sill(mb, F, x0, x1, y_face, z, out=0.5, m="Wood_Dark", out_sign=-1):
    lbox(mb, F, (x1 - x0 + 0.7, out + 0.5, 0.35), (x0 + x1) / 2, y_face + out_sign * (out / 2), z - 0.18, m, 0.06)


# ------------------------------------------------------------------ pilha de lenha, cepo e machado
def log_pile(mb, F, x, y, z, length, rows, rng, r=0.42):
    for j in range(rows):
        n = rows - j + 2
        for i in range(n):
            yy = y + (i - (n - 1) / 2) * (2 * r + 0.02) + (r if j % 2 else 0) * 0
            zz = z + r + j * (2 * r - 0.1)
            p = F.p(x + rng.uniform(-0.25, 0.25), yy, zz)
            mb.cyl(r * rng.uniform(0.85, 1.1), length * rng.uniform(0.9, 1.05), p, F.r(0, D(90), 0),
                   "Wood_Light" if rng.random() < 0.35 else "Bark", 6, bevel=0.0)


def chopping_block(mb, F, x, y, z, rng):
    p = F.p(x, y, z + 0.6)
    mb.cyl(0.8, 1.2, p, (0, 0, 0), "Bark", 8, bevel=0.0)
    mb.cyl(0.78, 0.08, p + Vector((0, 0, 0.62)), (0, 0, 0), "Wood_Light", 8, bevel=0.0)
    a = F.p(x + 0.1, y, z + 1.2)
    mb.beam(a, a + Vector((0.3, 0.9, 1.8)), 0.18, 0.18, "Wood_Light", 0.0)
    mb.box((0.9, 0.25, 0.55), a + Vector((0.05, 0.1, 0.1)), (0, 0, F.a + 0.3), "Metal_Iron", 0.03)
