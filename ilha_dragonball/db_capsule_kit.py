# db_capsule_kit - helpers geometricos da zona CAPSULE (Ilha 2, Dragon Ball). So geometria (MB do lobby / VMB do
# Naruto); materiais escolhidos por nome. Tudo o que sai daqui e SOLIDO FECHADO (o MB.finish recalcula as normais para
# fora), inclusive as faces vistas por dentro (cupula interna = casca com espessura: a face de dentro aponta para o
# salao).
#   CMB          VMB (chanfro/micro/variantes da Ilha 1) com detalhe "near" por padrao
#   lathe        torno de perfil [(r, z_abs)] (fechado ou aberto) com arco parcial, faces lisas por aresta do perfil
#   shell_prof   perfil fechado de casca eliptica (cupula) com espessura
#   Ell          elipsoide de revolucao (cupula): ponto, normal, tangente, projecao de um ponto ao longo de uma direcao
#   loft         secoes (listas de pontos 3D) ligadas em solido (tubo reto/curvo, nervura, faixa)
#   rib_meridian / rib_parallel   nervura/faixa saliente sobre a superficie da cupula
#   torus        anel de secao poligonal (holograma, aros)
#   extrude_uz   poligono no plano vertical de um Frame (u = x local, z) extrudado ao longo do y local
#   ring_plate   setor de anel plano num plano qualquer
#   dome_patch   disco / setor de anel que acompanha a curvatura da cupula (emblema embutido: disco + anel C)
#   porthole     escotilha redonda (aro + vidro) numa parede curva
#   sphere       esfera lisa (icosfera)
#   chords       caixas de colisao em anel (cordas), com vaos
import math
import bmesh
from mathutils import Vector, Matrix, Euler
import fm_lib
from fm_lib import col_box
import il_village_kit as VK

D2R = math.pi / 180.0


class CMB(VK.VMB):
    """VMB com detalhe 'near' por padrao e 1 variante por familia (orcamento de MeshParts)"""

    def __init__(self, name, collection, rng=None, detail="near", vcap=1):
        super().__init__(name, collection, rng, detail=detail, vcap=vcap)


def _smooth(faces):
    for f in faces:
        if f.is_valid:
            f.smooth = True


# ------------------------------------------------------------------ torno
def lathe(mb, c, prof, m, n=48, a0=0.0, a1=360.0, smooth=(), mats=None, closed=True):
    """revolve o perfil [(r, z_abs)] em volta do eixo vertical por c=(x, y). closed: perfil fechado (solido) com
    tampas nas pontas de um arco parcial. smooth: indices das arestas do perfil (aresta j = prof[j] -> prof[j+1]) com
    sombreamento liso. mats: material por aresta (None = m). Nunca use r = 0 no perfil."""
    full = abs(a1 - a0) >= 359.999
    k = len(prof)
    segs = max(2, int(round(n)))
    cnt = segs if full else segs + 1
    bm = mb.bm
    rings = []
    for i in range(cnt):
        a = (a0 + (a1 - a0) * i / segs) * D2R
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((c[0] + r * ca, c[1] + r * sa, z)) for r, z in prof])
    by_edge = {}
    ne = k if closed else k - 1
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % cnt]
        for j in range(ne):
            j2 = (j + 1) % k
            try:
                f = bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
                by_edge.setdefault(j, []).append(f)
            except ValueError:
                pass
    if closed and not full:
        for rr in (rings[0], list(reversed(rings[-1]))):
            try:
                bm.faces.new(rr)
            except ValueError:
                pass
    mb._post([v for rr in rings for v in rr], m, None, 0, 1)
    if mats:
        for j, fs in by_edge.items():
            mj = mats[j] if j < len(mats) and mats[j] else m
            if mj == m:
                continue
            mi = mb._mi_for(mj)
            for f in fs:
                f.material_index = mi
            mb._uv(fs, mj)
    for j in smooth:
        _smooth(by_edge.get(j, []))
    return by_edge


def ring(mb, c, r0, r1, z0, z1, m, n=48, a0=0.0, a1=360.0, smooth_out=False, smooth_in=False):
    """anel retangular (r0..r1, z0..z1); arestas: 0 base, 1 face externa, 2 topo, 3 face interna"""
    sm = ([1] if smooth_out else []) + ([3] if smooth_in else [])
    return lathe(mb, c, [(r0, z0), (r1, z0), (r1, z1), (r0, z1)], m, n, a0, a1, smooth=sm)


def spans(gaps, a0=0.0, a1=360.0):
    """trechos de arco (graus) sem os vaos [(angulo_centro, meia_abertura)] - o do Naruto (VK.arc_spans)"""
    return VK.arc_spans(gaps, a0, a1)


def seg_n(s0, s1, n_full):
    return max(2, int(round(n_full * (s1 - s0) / 360.0)))


def ell_pts(a, b, zc, ph0, ph1, k, dr=0.0, db=0.0):
    """pontos (r, z) da elipse (a + dr, b + db) de ph0 a ph1 (graus), k intervalos"""
    out = []
    for i in range(k + 1):
        ph = (ph0 + (ph1 - ph0) * i / k) * D2R
        out.append(((a + dr) * math.cos(ph), zc + (b + db) * math.sin(ph)))
    return out


def shell_prof(a, b, zc, ph0, ph1, k, th, inner_visible=False, k_hidden=4):
    """perfil FECHADO de uma casca eliptica de espessura th: (perfil, arestas lisas).
    inner_visible=False: a face lisa e a de fora (elipse a, b); a de dentro e (a - th, b - th).
    inner_visible=True : a face lisa e a de dentro (elipse a, b) e a de fora e (a + th, b + th).
    A face escondida sai grossa (k_hidden intervalos): as cordas ficam sempre do lado de dentro da casca."""
    if not inner_visible:
        outer = ell_pts(a, b, zc, ph0, ph1, k)
        inner = ell_pts(a - th, b - th, zc, ph1, ph0, k_hidden)
        prof = outer + inner
        smooth = list(range(0, k))
    else:
        inner = ell_pts(a, b, zc, ph0, ph1, k)
        # a face de fora (escondida) passa por FORA das cordas da elipse (a + th, b + th)
        outer = ell_pts(a + th, b + th, zc, ph1, ph0, k_hidden)
        c = math.cos(math.pi / 2 * (ph1 - ph0) / 180.0 / k_hidden)
        outer = [(r / c, z) for r, z in outer]
        prof = inner + outer
        smooth = list(range(0, k))
    return prof, smooth


# ------------------------------------------------------------------ elipsoide (cupula)
class Ell:
    """elipsoide de revolucao: centro (cx, cy, zc), semi-eixo horizontal a e vertical b. th/ph em graus."""

    def __init__(self, cx, cy, zc, a, b):
        self.c = Vector((cx, cy, zc))
        self.a, self.b = a, b

    def pt(self, th, ph, off=0.0):
        t, p = th * D2R, ph * D2R
        v = self.c + Vector((self.a * math.cos(p) * math.cos(t), self.a * math.cos(p) * math.sin(t),
                             self.b * math.sin(p)))
        return v + self.nrm(th, ph) * off if off else v

    def nrm(self, th, ph):
        t, p = th * D2R, ph * D2R
        return Vector((math.cos(p) * math.cos(t) / self.a, math.cos(p) * math.sin(t) / self.a,
                       math.sin(p) / self.b)).normalized()

    def tan_th(self, th):
        t = th * D2R
        return Vector((-math.sin(t), math.cos(t), 0.0))

    def tan_ph(self, th, ph):
        t, p = th * D2R, ph * D2R
        return Vector((-self.a * math.sin(p) * math.cos(t), -self.a * math.sin(p) * math.sin(t),
                       self.b * math.cos(p))).normalized()

    def proj(self, q, d):
        """ponto da superficie na reta q + d*t (raiz mais perto de q)"""
        q, d = Vector(q), Vector(d)
        e = q - self.c
        A = (d.x * d.x + d.y * d.y) / self.a ** 2 + d.z * d.z / self.b ** 2
        B = 2 * ((e.x * d.x + e.y * d.y) / self.a ** 2 + e.z * d.z / self.b ** 2)
        Cc = (e.x * e.x + e.y * e.y) / self.a ** 2 + e.z * e.z / self.b ** 2 - 1.0
        disc = B * B - 4 * A * Cc
        if disc < 0:
            return q
        s = math.sqrt(disc)
        t1, t2 = (-B - s) / (2 * A), (-B + s) / (2 * A)
        t = t1 if abs(t1) < abs(t2) else t2
        return q + d * t


# ------------------------------------------------------------------ loft / nervuras / anel
def loft(mb, secs, m, closed_path=False, smooth=False):
    """liga secoes (mesmo numero de pontos, mesma ordem) num solido; closed_path: o caminho fecha (anel)"""
    bm = mb.bm
    rings = [[bm.verts.new(Vector(p)) for p in s] for s in secs]
    k = len(secs[0])
    cnt = len(rings)
    fs = []
    for i in range(cnt if closed_path else cnt - 1):
        r0, r1 = rings[i], rings[(i + 1) % cnt]
        for j in range(k):
            j2 = (j + 1) % k
            try:
                fs.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
            except ValueError:
                pass
    if not closed_path:
        for rr in (rings[0], list(reversed(rings[-1]))):
            try:
                bm.faces.new(rr)
            except ValueError:
                pass
    mb._post([v for rr in rings for v in rr], m, None, 0, 1)
    if smooth:
        _smooth(fs)
    return fs


def rib_meridian(mb, E, th, ph0, ph1, k, w, top, bot, m, inward=False):
    """nervura ao longo de um meridiano da cupula (th fixo), largura w, saliencia top (enterrada bot)"""
    sg = -1.0 if inward else 1.0
    secs = []
    for i in range(k + 1):
        ph = ph0 + (ph1 - ph0) * i / k
        p = E.pt(th, ph)
        n = E.nrm(th, ph) * sg
        t = E.tan_th(th)
        secs.append([p + t * (-w / 2) - n * bot, p + t * (w / 2) - n * bot, p + t * (w / 2) + n * top,
                     p + t * (-w / 2) + n * top])
    return loft(mb, secs, m)


def rib_parallel(mb, E, ph, th0, th1, k, w, top, bot, m, inward=False):
    """faixa ao longo de um paralelo (ph fixo); th0..th1 = 0..360 fecha o anel"""
    sg = -1.0 if inward else 1.0
    full = abs(th1 - th0) >= 359.999
    secs = []
    cnt = k if full else k + 1
    for i in range(cnt):
        th = th0 + (th1 - th0) * i / k
        p = E.pt(th, ph)
        n = E.nrm(th, ph) * sg
        t = E.tan_ph(th, ph)
        secs.append([p + t * (-w / 2) - n * bot, p + t * (w / 2) - n * bot, p + t * (w / 2) + n * top,
                     p + t * (-w / 2) + n * top])
    return loft(mb, secs, m, closed_path=full)


def torus(mb, c, R, r, m, axis=(0, 0, 1), n=40, k=6, smooth=True):
    """anel (toro) de raio R e secao r em volta do eixo 'axis' por c"""
    ax = Vector(axis).normalized()
    u = ax.orthogonal().normalized()
    v = ax.cross(u)
    c = Vector(c)
    secs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = u * math.cos(a) + v * math.sin(a)
        ctr = c + d * R
        secs.append([ctr + (d * math.cos(2 * math.pi * j / k) + ax * math.sin(2 * math.pi * j / k)) * r
                     for j in range(k)])
    return loft(mb, secs, m, closed_path=True, smooth=smooth)


# ------------------------------------------------------------------ perfis no plano vertical
def extrude_uz(mb, pts, F, y0, y1, m, cap_m=None):
    """poligono [(u, z_rel)] no plano vertical do Frame F (u = x local, z relativo a F.o.z), extrudado de y0 a y1
    (y local). cap_m: material das 2 tampas (frente/fundo)."""
    bm = mb.bm
    a = [bm.verts.new(F.p(u, y0, z)) for u, z in pts]
    b = [bm.verts.new(F.p(u, y1, z)) for u, z in pts]
    n = len(pts)
    caps = []
    try:
        caps.append(bm.faces.new(a))
        caps.append(bm.faces.new(list(reversed(b))))
    except ValueError:
        pass
    for i in range(n):
        j = (i + 1) % n
        try:
            bm.faces.new((a[i], a[j], b[j], b[i]))
        except ValueError:
            pass
    mb._post(a + b, m, None, 0, 1)
    if cap_m and cap_m != m:
        mi = mb._mi_for(cap_m)
        for f in caps:
            f.material_index = mi
        mb._uv(caps, cap_m)


def semi_ell(a, b, z0, k=12, u0=0.0, rev=False):
    """pontos (u, z) de meia elipse de a (u = -a) ate -a... da esquerda para a direita passando pelo topo"""
    pts = [(u0 + a * math.cos(math.pi - math.pi * i / k), z0 + b * math.sin(math.pi - math.pi * i / k))
           for i in range(k + 1)]
    return list(reversed(pts)) if rev else pts


def ring_plate(mb, C, U, V, N, r0, r1, a0, a1, o0, o1, m, n=32):
    """setor de anel plano (r0..r1, a0..a1 graus a partir de U, anti-horario para V) entre as distancias o0..o1 ao
    longo de N a partir de C"""
    C, U, V, N = Vector(C), Vector(U), Vector(V), Vector(N)
    secs = []
    for i in range(n + 1):
        a = (a0 + (a1 - a0) * i / n) * D2R
        d = U * math.cos(a) + V * math.sin(a)
        secs.append([C + d * r0 + N * o0, C + d * r1 + N * o0, C + d * r1 + N * o1, C + d * r0 + N * o1])
    return loft(mb, secs, m)


def dome_patch(mb, E, th0, ph0, radii, o0, o1, m, a0=0.0, a1=360.0, n=48, smooth=True):
    """placa que ACOMPANHA a cupula E (emblema embutido, sem 'lata' saliente): setor de anel radii[0]..radii[-1]
    (radii[0] = 0 -> disco cheio) em volta do ponto (th0, ph0), medido no plano tangente (U = horizontal, V = subindo a
    cupula, a0..a1 em graus a partir de U) e projetado na casca ao longo da normal; solido entre as distancias o0..o1
    da casca (normal local). Os raios intermediarios fazem a placa seguir a curvatura. Devolve as faces do topo."""
    S0 = E.pt(th0, ph0)
    N0 = E.nrm(th0, ph0)
    U = E.tan_th(th0)
    V = N0.cross(U).normalized()
    full = abs(a1 - a0) >= 359.999
    segs = max(3, int(n))
    cnt = segs if full else segs + 1
    bm = mb.bm
    center = radii[0] <= 1e-6

    def surf(rho, a):
        q = S0 + (U * math.cos(a) + V * math.sin(a)) * rho
        p = E.proj(q, N0)
        e = p - E.c
        nn = Vector((e.x / E.a ** 2, e.y / E.a ** 2, e.z / E.b ** 2)).normalized()
        return p, nn
    T, B = [], []
    for i, rho in enumerate(radii):
        if center and i == 0:
            vt, vb = bm.verts.new(S0 + N0 * o1), bm.verts.new(S0 + N0 * o0)
            T.append([vt] * cnt)
            B.append([vb] * cnt)
            continue
        rt, rb = [], []
        for j in range(cnt):
            p, nn = surf(rho, (a0 + (a1 - a0) * j / segs) * D2R)
            rt.append(bm.verts.new(p + nn * o1))
            rb.append(bm.verts.new(p + nn * o0))
        T.append(rt)
        B.append(rb)

    def add(vs):
        out = []
        for v in vs:
            if not out or out[-1] is not v:
                out.append(v)
        if len(out) > 2 and out[0] is out[-1]:
            out.pop()
        if len(out) < 3:
            return None
        try:
            return bm.faces.new(out)
        except ValueError:
            return None
    k = len(radii)
    top = []
    for i in range(k - 1):
        for j in range(segs):
            j2 = (j + 1) % cnt
            f = add([T[i][j], T[i + 1][j], T[i + 1][j2], T[i][j2]])
            if f:
                top.append(f)
            add([B[i][j2], B[i + 1][j2], B[i + 1][j], B[i][j]])
    for j in range(segs):
        j2 = (j + 1) % cnt
        add([B[-1][j], B[-1][j2], T[-1][j2], T[-1][j]])
        if not center:
            add([T[0][j], T[0][j2], B[0][j2], B[0][j]])
    if not full:
        for j, rev in ((0, False), (segs, True)):
            rr = [B[i][j] for i in range(k)] + [T[i][j] for i in reversed(range(k))]
            add(list(reversed(rr)) if rev else rr)
    verts = []
    seen = set()
    for row in T + B:
        for v in row:
            if id(v) not in seen:
                seen.add(id(v))
                verts.append(v)
    mb._post(verts, m, None, 0, 1)
    if smooth:
        _smooth(top)
    return top


def rot_to(nrm):
    return VK.rot_to(nrm)


def cyl_axis(mb, r, h, center, axis, m, n=24, r2=None):
    """cilindro de raio r e altura h centrado em 'center' com o eixo em 'axis'"""
    mb.cyl(r, h, tuple(center), tuple(rot_to(axis)), m, n, r2=r2, bevel=0.0)


def porthole(mb, cx, cy, R, th, z, rr=1.7, frame_m="Plaster_DB_Navy", glass_m="Glass_DB_Blue", n=16,
             proud=0.35):
    """escotilha redonda numa parede curva de raio R (centro cx, cy) no angulo th (graus), altura z"""
    t = th * D2R
    d = Vector((math.cos(t), math.sin(t), 0.0))
    c0 = Vector((cx, cy, z))
    mb.cyl(rr + 0.35, 1.0, tuple(c0 + d * (R + proud - 0.5)), (0.0, math.pi / 2, t), frame_m, n, bevel=0.0)
    mb.cyl(rr - 0.3, 1.0, tuple(c0 + d * (R + proud + 0.1 - 0.5)), (0.0, math.pi / 2, t), glass_m, n, bevel=0.0)


def sphere(mb, c, r, m, sub=2, smooth=True):
    res = bmesh.ops.create_icosphere(mb.bm, subdivisions=sub, radius=r,
                                     matrix=Matrix.Translation(Vector(c)))
    fs = mb._post(res["verts"], m, None, 0, 1)
    if smooth:
        _smooth(fs)
    return fs


# ------------------------------------------------------------------ colisao em anel (cordas)
def chords(area, cx, cy, rc, th, z0, z1, a0, a1, max_step=9.0):
    """paredes de colisao (caixas de corda) no anel de raio medio rc e espessura th, de a0 a a1 (graus)"""
    span = a1 - a0
    n = max(1, int(math.ceil(span / max_step)))
    da = span / n
    out = []
    for i in range(n):
        s0 = (a0 + da * i) * D2R
        s1 = (a0 + da * (i + 1)) * D2R
        am = (s0 + s1) / 2
        half = (s1 - s0) / 2
        rm = rc * math.cos(half)
        w = 2 * (rc + th / 2) * math.sin(half) + 0.3
        out.append(col_box(area, (th, w, z1 - z0), (cx + rm * math.cos(am), cy + rm * math.sin(am), (z0 + z1) / 2),
                           (0, 0, am)))
    return out
