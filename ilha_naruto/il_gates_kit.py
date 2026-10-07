# il_gates_kit - pecas comuns da FAMILIA de portoes de compra da galeria (Shadow Garden, Demon Slayer, One Piece,
# One Punch Man). Dono: zona "gates". So geometria no referencial do portao (il_gate_std.gate_frame):
#   x = direita de quem atravessa, y = sentido da travessia (-y = lado de quem chega), z = cima,
#   origem = centro do vao no nivel do piso (gz).
# Regras da familia (iguais nos 4): vao livre 16 x 18 (barreira/cadeado/colisao/marcadores do il_gate_std),
# 2 apoios principais em +-(8 + ~1.5), coroa/verga entre +18 e +26, altura <= 32, largura <= 44, ornamentos laterais
# fora de +-12, piso no nivel do tabuleiro. A barreira de energia corre num TRILHO (fenda) nas jambas e na verga:
# assim nenhuma face da barreira fica coplanar com a moldura (sem z-fighting) e o trilho continua legivel depois de
# desbloqueado.
# RODADA 2: (1) GMB aplica as regras novas em TODA primitiva (chanfro 0 se menor dim < 1, <= 5% da menor dim; peca
# com todas as dimensoes < 0,35 e descartada; vcap 1 = material base sem variante); (2) KIT DE FAMILIA com o DB
# (ref_13): soleira de cantaria, plintos em degrau, pedestal 4x4x4, lanterna de pedra, emblema em relevo no pedestal,
# emblemas flutuantes VFX e a colisao disso tudo (ver "KIT DE FAMILIA" abaixo).
import math
from mathutils import Vector
import fm_lib
import il_lib as IL
from il_lib import MB, col_box
import il_gate_std as GS
import fm_portal_kit as K

C = "08_PURCHASE_GATES"
HW = GS.OPEN_W / 2          # 8.0  meia-largura do vao
OH = GS.OPEN_H              # 18.0 altura livre
SLOT = 0.4                  # meia-largura (em y) do trilho da barreira (barreira: meia-espessura 0.25)
SLOT_DEPTH = 0.35           # profundidade do trilho dentro da jamba / verga


def rule_bevel(dmin, bevel):
    """regra da rodada 2: bevel 0 se a menor dimensao < 1,0; senao no maximo 5% da menor dimensao"""
    if not bevel or dmin < 1.0:
        return 0.0
    return min(bevel, 0.05 * dmin)


def extents(verts, extra=()):
    """(menor, maior) extensao de um conjunto de vertices, medida nos eixos do mundo, nos eixos do portao (extra)
    e nos eixos principais (PCA) da peca: para caixas/vigas giradas da a dimensao real"""
    import numpy as np
    P = np.array([v.co[:] for v in verts])
    dirs = [np.array(d, dtype=float) for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1))] + \
        [np.array(tuple(d), dtype=float) for d in extra]
    if len(P) >= 4:
        X = P - P.mean(0)
        w, V = np.linalg.eigh(X.T @ X)
        dirs += [V[:, k] for k in range(3)]
    ex = []
    for d in dirs:
        n = np.linalg.norm(d)
        if n < 1e-9:
            continue
        s = P @ (d / n)
        ex.append(float(s.max() - s.min()))
    return min(ex), max(ex)


class GMB(MB):
    """MB da familia: nivel de detalhe + teto de variantes tonais por familia (cada variante = 1 MeshPart).
    Regras da rodada 2 em TODA primitiva (box, beam, cyl, prism, band, plate...): chanfro pela regra (rule_bevel) e
    nada com todas as dimensoes < 0,35 (a peca e descartada)."""
    AXES = ()            # eixos x/y do portao em construcao (G os registra)
    skipped = 0
    STATS = {"prims": 0, "bevel_pedido": 0, "bevel_zerado": 0, "bevel_reduzido": 0, "bevel_ok": 0}

    def __init__(self, name, rng=None, detail="hero", vcap=1):
        super().__init__(name, C, rng, detail=detail)
        self.vcap = vcap

    def _post(self, verts, m, tint, bevel, seg, angle=0.5):
        import bmesh as _bm
        verts = [v for v in verts if v.is_valid]
        if verts:
            dmin, dmax = extents(verts, GMB.AXES)
            if dmax < 0.35:
                _bm.ops.delete(self.bm, geom=verts, context="VERTS")
                GMB.skipped += 1
                return set()
            st = GMB.STATS
            st["prims"] += 1
            if bevel and bevel > 0:
                st["bevel_pedido"] += 1
                nb = rule_bevel(dmin, bevel)
                st["bevel_zerado" if nb == 0 else ("bevel_reduzido" if nb < bevel - 1e-9 else "bevel_ok")] += 1
                bevel = nb
        return super()._post(verts, m, tint, bevel, seg, angle)

    def _family(self, m):
        if self.vcap <= 1:
            return None                  # vcap 1: sempre o material base (a pedra da familia tem o MESMO tom nos 4)
        return super()._family(m)

    def _variant_names(self, m):
        old = fm_lib.VARIANT_T2, fm_lib.VARIANT_T3
        try:
            if self.vcap <= 2:
                fm_lib.VARIANT_T3 = 10 ** 9
            if self.vcap <= 1:
                fm_lib.VARIANT_T2 = 10 ** 9
            return super()._variant_names(m)
        finally:
            fm_lib.VARIANT_T2, fm_lib.VARIANT_T3 = old


class G:
    """construtor no referencial do portao (todas as medidas locais)"""

    def __init__(self, F):
        self.F = F
        self.ux = (Vector(F.p(1, 0, 0)) - Vector(F.p(0, 0, 0))).normalized()
        self.uy = (Vector(F.p(0, 1, 0)) - Vector(F.p(0, 0, 0))).normalized()
        self.uz = Vector((0.0, 0.0, 1.0))
        GMB.AXES = (tuple(self.ux), tuple(self.uy))

    # ---------------------------------------------------------------- conversao
    def P(self, x, y, z):
        return Vector(self.F.p(x, y, z))

    def R(self, rx=0.0, ry=0.0, rz=0.0):
        return self.F.r(rx, ry, rz)

    def D(self, x, y, z):
        """direcao local -> mundo"""
        return self.ux * x + self.uy * y + self.uz * z

    # ---------------------------------------------------------------- primitivas
    def box(self, mb, x0, x1, y0, y1, z0, z1, m, bev=0.12):
        mb.box((abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), self.P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               self.R(), m, bev)

    def boxr(self, mb, size, c, m, bev=0.1, rx=0.0, ry=0.0, rz=0.0):
        mb.box(size, self.P(*c), self.R(rx, ry, rz), m, bev)

    def beam(self, mb, a, b, w, h, m, bev=0.08):
        mb.beam(self.P(*a), self.P(*b), w, h, m, bev)

    def cyl(self, mb, r, h, c, m, n=12, r2=None, bev=0.0, axis="z", spin=0.0):
        # spin (giro no proprio eixo) so vale para axis="z" (Euler XYZ)
        rot = {"z": (0.0, 0.0, spin), "y": (math.pi / 2, 0.0, 0.0), "x": (0.0, math.pi / 2, 0.0)}[axis]
        mb.cyl(r, h, self.P(*c), self.R(*rot), m, n, r2=r2, bevel=bev)

    def rod(self, mb, a, b, r, m, n=6):
        mb.rod(self.P(*a), self.P(*b), r, m, n)

    def ico(self, mb, r, c, m, sub=1, scale=(1, 1, 1)):
        mb.ico(r, self.P(*c), m, sub, scale, self.R())

    def prism(self, mb, pts, z0, z1, m, bev=0.0):
        """prisma vertical de um poligono local (x, y) anti-horario"""
        oz = self.F.o.z
        mb.prism([tuple(self.P(x, y, 0))[:2] for x, y in pts], oz + z0, oz + z1, m, bev)

    def band(self, mb, outer, inner, y0, y1, m, bev=0.0):
        """solido entre duas polilinhas (x, z) com o mesmo numero de pontos, extrudado em y de y0 a y1"""
        bm = mb.bm
        of = [bm.verts.new(self.P(x, y0, z)) for x, z in outer]
        fi = [bm.verts.new(self.P(x, y0, z)) for x, z in inner]
        ob = [bm.verts.new(self.P(x, y1, z)) for x, z in outer]
        bi = [bm.verts.new(self.P(x, y1, z)) for x, z in inner]
        n = len(outer)
        for i in range(n - 1):
            j = i + 1
            bm.faces.new((of[i], of[j], fi[j], fi[i]))
            bm.faces.new((ob[j], ob[i], bi[i], bi[j]))
            bm.faces.new((of[j], of[i], ob[i], ob[j]))
            bm.faces.new((fi[i], fi[j], bi[j], bi[i]))
        bm.faces.new((of[0], fi[0], bi[0], ob[0]))
        bm.faces.new((of[-1], ob[-1], bi[-1], fi[-1]))
        mb._post(of + fi + ob + bi, m, None, bev, 1, angle=0.6)

    def side_prism(self, mb, prof, x0, x1, m, bev=0.0):
        """prisma de um poligono CONVEXO no plano lateral (y, z), extrudado em x de x0 a x1 (contrafortes, misulas)"""
        bm = mb.bm
        a = [bm.verts.new(self.P(x0, y, z)) for y, z in prof]
        b = [bm.verts.new(self.P(x1, y, z)) for y, z in prof]
        bm.faces.new(list(reversed(a)))
        bm.faces.new(b)
        n = len(prof)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
        mb._post(a + b, m, None, bev, 1, angle=0.6)

    def plate(self, mb, pts, y, thick, m, bev=0.0):
        """poligono (x, z) no plano do portao, centrado em y, espessura em y"""
        K.plate(mb, pts, self.P(0, y, 0), tuple(self.ux), (0, 0, 1), thick, m, bev)

    def ring(self, mb, cx, cz, R, w, h, y, m, a0=0.0, a1=360.0, n=36):
        """aro no plano do portao: w radial, h em y"""
        K.ring(mb, self.P(cx, y, cz), R, tuple(self.ux), (0, 0, 1), w, h, m, a0, a1, n)

    def chain(self, mb, a, b, sag=1.0, link=0.7, m="Metal_Dark", t=0.2, w=0.45):
        K.chain(mb, self.P(*a), self.P(*b), sag, link, m, t, w)

    def tube(self, mb, pts, radii, m, n=8):
        K.taper_tube(mb, [self.P(*p) for p in pts], radii, m, n, True, up=tuple(self.uy))

    def cone(self, mb, a, b, r0, r1, m, n=6):
        K.cone(mb, self.P(*a), self.P(*b), r0, r1, m, n)

    def col(self, area, x0, x1, y0, y1, z0, z1, kind="Block"):
        return col_box(area, (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)),
                       self.P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), self.R(), kind)

    # ---------------------------------------------------------------- jamba com trilho da barreira
    def jamb_box(self, mb, s, xin, xout, y0, y1, z0, z1, m, bev=0.12, lip_m=None, slot_m=None):
        """caixa encostada no vao (face interna em |x| = xin) com o TRILHO: o miolo (|y| < SLOT) recua
        SLOT_DEPTH; so os labios da frente e de tras chegam em xin. s = -1 (esquerda) / +1 (direita).
        slot_m: material do fundo do trilho (faixa fina no recuo)."""
        a, b = sorted((s * (xin + SLOT_DEPTH), s * xout))
        self.box(mb, a, b, y0, y1, z0, z1, m, bev)
        la, lb = sorted((s * xin, s * (xin + SLOT_DEPTH + 0.05)))
        for ya, yb in ((y0, -SLOT), (SLOT, y1)):
            if yb - ya > 0.05:
                self.box(mb, la, lb, ya, yb, z0, z1, lip_m or m, min(bev, 0.06))
        if slot_m:
            ga, gb = sorted((s * (xin + SLOT_DEPTH - 0.15), s * (xin + SLOT_DEPTH + 0.2)))   # 0,15 fora do fundo
            self.box(mb, ga, gb, -SLOT + 0.06, SLOT - 0.06, z0 + 0.3, z1 - 0.3, slot_m, 0.0)


# ------------------------------------------------------------------ curvas 2D (x, z)
def arc(cx, cz, r, a0, a1, n):
    """a0/a1 em graus"""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def ogive(off, zs, R, n=10):
    """ogiva (arco quebrado) de centros (+-off, zs) e raio R: da nascenca esquerda ao apice e a nascenca direita
    (2n+1 pontos). A meia-largura na nascenca e R - off; o apice fica em zs + sqrt(R^2 - off^2)."""
    aa = math.acos(-off / R)
    left = []
    for i in range(n + 1):
        a = math.pi + (aa - math.pi) * i / n
        left.append((off + R * math.cos(a), zs + R * math.sin(a)))
    left[-1] = (0.0, zs + math.sqrt(R * R - off * off))
    right = [(-x, z) for x, z in reversed(left[:-1])]
    return left + right


def ray_hit(poly, cx, cz, th):
    """distancia de (cx, cz) ate a borda do poligono (x, z) na direcao th (rad); poligono estrelado em torno do centro"""
    dx, dz = math.cos(th), math.sin(th)
    best = None
    n = len(poly)
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        ex, ez = bx - ax, bz - az
        den = dx * ez - dz * ex
        if abs(den) < 1e-9:
            continue
        t = ((ax - cx) * ez - (az - cz) * ex) / den
        s = ((ax - cx) * dz - (az - cz) * dx) / den
        if t > 1e-6 and -1e-6 <= s <= 1 + 1e-6:
            best = t if best is None else min(best, t)
    return best if best is not None else 0.0


def radial_fill(cx, cz, r_in, poly, a0, a1, n):
    """(outer, inner) para band(): do circulo r_in ate a borda do poligono, varrendo a0..a1 graus"""
    outer, inner = [], []
    for i in range(n + 1):
        th = math.radians(a0 + (a1 - a0) * i / n)
        d = ray_hit(poly, cx, cz, th)
        outer.append((cx + d * math.cos(th), cz + d * math.sin(th)))
        inner.append((cx + r_in * math.cos(th), cz + r_in * math.sin(th)))
    return outer, inner


def crescent(R, r, d, theta, n=40, cx=0.0, cz=0.0):
    """lua crescente 2D: circulo R menos o circulo r deslocado d na direcao theta (a mordida)"""
    ui = (R * R - r * r + d * d) / (2 * d)
    vi = math.sqrt(max(R * R - ui * ui, 1e-6))
    phi = math.atan2(vi, ui)
    psi = math.atan2(vi, ui - d)
    pts = []
    for i in range(n + 1):
        a = phi + (math.tau - 2 * phi) * i / n
        pts.append((math.cos(a) * R, math.sin(a) * R))
    ni = max(8, int(round(n * (math.tau - 2 * psi) * r / ((math.tau - 2 * phi) * R))))
    for i in range(1, ni):
        a = (math.tau - psi) - (math.tau - 2 * psi) * i / ni
        pts.append((d + math.cos(a) * r, math.sin(a) * r))
    c, s = math.cos(theta), math.sin(theta)
    return [(cx + u * c - v * s, cz + u * s + v * c) for u, v in pts]


def star(cx, cz, radii, a0=90.0):
    """estrela 2D (x, z): radii = [externo, interno, externo, interno, ...] a partir do angulo a0 (graus)"""
    n = len(radii)
    return [(cx + radii[i] * math.cos(math.radians(a0 + 360.0 * i / n)),
             cz + radii[i] * math.sin(math.radians(a0 + 360.0 * i / n))) for i in range(n)]


def offset(pts, dz=0.0, dx=0.0):
    return [(x + dx, z + dz) for x, z in pts]


# ================================================================== KIT DE FAMILIA (rodada 2)
# Base comum dos 4 portoes, na mesma pedra do Dragon Ball (ref_13): soleira de cantaria no vao, plintos em degrau nas
# laterais, 2 pedestais 4x4x4 com o guardiao de cada portao, 2 lanternas de pedra no padrao da do DB e 3-4 emblemas
# flutuantes (VFX com bob) como as esferas do DB. A cota do vao nao muda: so a soleira sobe 0,15.
FAM_LIGHT, FAM_DARK = "Stone_Wall_Light", "Stone_Wall_Dark"
SOL_HX, SOL_HY, SOL_TOP = 11.0, 5.0, 0.15       # soleira 22 x 10, topo gz + 0,15
BASE_Z = -0.6                                   # tudo que fica fora do tabuleiro desce ate aqui (chao irregular)
POD_X, POD_Y = (11.0, 18.0), (-10.2, 2.9)       # plinto lateral (degrau 1), lado direito (o esquerdo e o espelho)
POD_Z1 = 0.6
POD2_X, POD2_Y, POD2_Z1 = (12.5, 17.7), (-7.3, -2.1), 1.1   # degrau 2 (sob o pedestal)
PED_C, PED_S = (15.1, -4.7), 4.0               # pedestal 4 x 4 x 4 sobre o degrau 2
PED_Z0 = POD2_Z1
PED_TOP = PED_Z0 + PED_S                        # 5,1: base do guardiao
LANT_C = (12.4, -8.5)                           # lanterna de pedra sobre o degrau 1
EMB_POS = [(-13.0, -4.3, 15.6), (-12.4, -8.5, 10.8), (12.4, -8.5, 11.1), (13.0, -4.3, 15.9)]


def chamfer_block(g, mb, x0, x1, y0, y1, zb, zs, zt, ins, m):
    """bloco de cantaria: corpo zb..zs e chanfro zs..zt recuado 'ins' em volta (geometria explicita, sem bevel)"""
    bm = mb.bm

    def rect(a):
        return [(x0 + a, y0 + a), (x1 - a, y0 + a), (x1 - a, y1 - a), (x0 + a, y1 - a)]
    b = [bm.verts.new(g.P(x, y, zb)) for x, y in rect(0.0)]
    s = [bm.verts.new(g.P(x, y, zs)) for x, y in rect(0.0)]
    t = [bm.verts.new(g.P(x, y, zt)) for x, y in rect(ins)]
    bm.faces.new(list(reversed(b)))
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((b[i], b[j], s[j], s[i]))
        bm.faces.new((s[i], s[j], t[j], t[i]))
    mb._post(b + s + t, m, None, 0.0, 1)


def soleira(g, mb, light=FAM_LIGHT, dark=FAM_DARK):
    """soleira de cantaria 22 x 10 rente ao piso (topo +0,15): meio-fio escuro na frente e atras (blocos longos) e
    2 fiadas de blocos claros desencontrados; chanfro de 0,3 x 0,15 em cada bloco (a junta vira um V, a fiada do
    meio encontra a outra no plano da barreira = trilho do piso)"""
    hx, hy = SOL_HX, SOL_HY
    kerb = 1.3
    for y0, y1 in ((-hy, -hy + kerb), (hy - kerb, hy)):
        xs = [-hx + 5.5 * i for i in range(5)]
        for x0, x1 in zip(xs, xs[1:]):
            chamfer_block(g, mb, x0, x1, y0, y1, BASE_Z, 0.0, SOL_TOP, 0.3, dark)
    for (y0, y1), off in (((-hy + kerb, 0.0), 0.0), ((0.0, hy - kerb), 1.375)):
        xs = sorted({-hx, hx} | {round(-hx + off + 2.75 * i, 4) for i in range(9) if -hx < -hx + off + 2.75 * i < hx})
        for x0, x1 in zip(xs, xs[1:]):
            chamfer_block(g, mb, x0, x1, y0, y1, BASE_Z, 0.0, SOL_TOP, 0.3, light)


def side_plinths(g, mb, light=FAM_LIGHT, dark=FAM_DARK, pod_y=None):
    """plintos em degrau nas laterais (fora do vao): degrau 1 largo (lanterna, pe da moldura) e degrau 2 sob o
    pedestal. Decorativos: o vao continua no nivel do piso."""
    py = pod_y or POD_Y
    for s in (-1, 1):
        xa, xb = sorted((s * POD_X[0], s * POD_X[1]))
        chamfer_block(g, mb, xa, xb, py[0], py[1], BASE_Z, POD_Z1 - 0.18, POD_Z1, 0.3, dark)
        xa, xb = sorted((s * POD2_X[0], s * POD2_X[1]))
        chamfer_block(g, mb, xa, xb, POD2_Y[0], POD2_Y[1], POD_Z1 - 0.3, POD2_Z1 - 0.15, POD2_Z1, 0.25, light)


def pedestal(g, mb, s, accent, light=FAM_LIGHT, dark=FAM_DARK):
    """pedestal 4 x 4 x 4 do padrao do DB (sapata escura, bloco claro, capa escura) com almofada no tom do portao
    nas 4 faces (0,15 saliente); s = lado (-1/+1). Retorna o centro do topo."""
    cx, cy = s * PED_C[0], PED_C[1]
    h = PED_S / 2
    z0 = PED_Z0
    g.box(mb, cx - h, cx + h, cy - h, cy + h, z0, z0 + 0.55, dark, 0.0)
    g.box(mb, cx - h + 0.3, cx + h - 0.3, cy - h + 0.3, cy + h - 0.3, z0 + 0.55, z0 + 3.45, light, 0.14)
    g.box(mb, cx - h, cx + h, cy - h, cy + h, z0 + 3.45, z0 + PED_S, dark, 0.0)
    b = h - 0.3
    for (px, py, ax) in ((0.0, -b, "y"), (0.0, b, "y"), (-b, 0.0, "x"), (b, 0.0, "x")):
        if ax == "y":
            g.box(mb, cx - 1.05, cx + 1.05, cy + py - 0.15, cy + py + 0.15, z0 + 1.1, z0 + 2.9, accent, 0.0)
        else:
            g.box(mb, cx + px - 0.15, cx + px + 0.15, cy - 1.05, cy + 1.05, z0 + 1.1, z0 + 2.9, accent, 0.0)
    return (cx, cy, z0 + PED_S)


def inlay(g, mb, s, pts2d, m):
    """emblema do portao em relevo na almofada da FRENTE do pedestal (0,25 saliente; pts2d em (x, z) relativos ao
    centro da almofada, ~1,5 de largura)"""
    cx, cy = s * PED_C[0], PED_C[1]
    zc = PED_Z0 + 2.0
    yf = cy - (PED_S / 2 - 0.3) - 0.15            # face da almofada
    g.plate(mb, [(cx + x, zc + z) for x, z in pts2d], yf - 0.1, 0.3, m)


def lantern(g, mb, s, glow, roof, finial, light=FAM_LIGHT, dark=FAM_DARK, z0=POD_Z1):
    """lanterna de pedra quadrada no padrao da do DB (il_gate_db.stone_lantern): sapata, fuste, prato, camara acesa
    com 4 montantes, prato, chapeu piramidal e remate. Sem luz (a zona nao tem luz de dia)."""
    x, y = s * LANT_C[0], LANT_C[1]
    g.box(mb, x - 1.0, x + 1.0, y - 1.0, y + 1.0, z0, z0 + 0.6, dark, 0.0)
    g.box(mb, x - 0.6, x + 0.6, y - 0.6, y + 0.6, z0 + 0.6, z0 + 3.0, light, 0.06)
    g.box(mb, x - 1.0, x + 1.0, y - 1.0, y + 1.0, z0 + 3.0, z0 + 3.35, dark, 0.0)
    g.box(mb, x - 0.65, x + 0.65, y - 0.65, y + 0.65, z0 + 3.28, z0 + 4.82, glow, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.box(mb, x + sx * 0.66 - 0.18, x + sx * 0.66 + 0.18, y + sy * 0.66 - 0.18, y + sy * 0.66 + 0.18,
                  z0 + 3.35, z0 + 4.75, light, 0.0)
    g.box(mb, x - 0.95, x + 0.95, y - 0.95, y + 0.95, z0 + 4.75, z0 + 5.05, dark, 0.0)
    g.cyl(mb, 1.75, 0.95, (x, y, z0 + 5.05 + 0.47), roof, 4, r2=0.3, bev=0.0, spin=math.pi / 4)
    g.ico(mb, 0.34, (x, y, z0 + 6.2), finial, 1)


def family_collision(g, area, ped_h=4.0, lant=True):
    """colisao da base comum: soleira (pisavel, +0,15), degraus laterais, pedestal (+ guardiao) e lanterna"""
    g.col(area, -SOL_HX, SOL_HX, -SOL_HY, SOL_HY, SOL_TOP - 0.75, SOL_TOP)
    for s in (-1, 1):
        g.col(area, s * POD_X[0], s * POD_X[1], POD_Y[0], POD_Y[1], BASE_Z, POD_Z1)
        g.col(area, s * POD2_X[0], s * POD2_X[1], POD2_Y[0], POD2_Y[1], POD_Z1, POD2_Z1)
        cx, cy = s * PED_C[0], PED_C[1]
        h = PED_S / 2
        g.col(area, cx - h, cx + h, cy - h, cy + h, POD_Z1, PED_Z0 + PED_S + ped_h)
        if lant:
            x, y = s * LANT_C[0], LANT_C[1]
            g.col(area, x - 1.0, x + 1.0, y - 1.0, y + 1.0, POD_Z1, POD_Z1 + 6.5)


def emblem_vfx(key, name, g, c, build, rpm=5.0, bob=0.6, detail="near"):
    """emblema flutuante (peca movel VFX_GATE_<k>_<nome>): gira em volta do eixo z do proprio centro e flutua"""
    mb = GMB("VFX_GATE_%s_%s" % (key, name), None, detail=detail)
    mb.coll = fm_lib.coll("12_VFX_HELPERS")
    p = g.P(*c)
    build(mb, p)
    ob = mb.finish()
    if ob is not None:
        ob["pivot"] = (p.x, p.y, p.z)
        ob["axis"] = (0.0, 0.0, 1.0)
        ob["rpm"] = rpm
        ob["bob"] = bob
        ob["gate"] = key
    return ob


def emblems(key, g, name, build, pos=None, rpm0=4.0):
    """os 3-4 emblemas do portao nas posicoes da familia (ou 'pos'), rpm alternando o sentido"""
    out = []
    for i, c in enumerate(pos or EMB_POS):
        out.append(emblem_vfx(key, "%s_%d" % (name, i + 1), g, c, build, rpm=(rpm0 + i) * (1 if i % 2 else -1),
                              bob=0.6))
    return out


def family_base(g, mb, area, accent, glow, roof, finial, ped=None, pod_y=None):
    """soleira + plintos (pedra COMUM da familia, a mesma do DB) + 2 pedestais + 2 lanternas (mesma forma nos 4; pedra
    do portao em ped=(clara, escura)), sem o guardiao; retorna os topos dos pedestais"""
    light, dark = ped or (FAM_LIGHT, FAM_DARK)
    soleira(g, mb)
    side_plinths(g, mb, pod_y=pod_y)
    tops = []
    for s in (-1, 1):
        tops.append(pedestal(g, mb, s, accent, light, dark))
        lantern(g, mb, s, glow, roof, finial, light, dark)
    return tops


# ------------------------------------------------------------------ revisao
def cams_for(key, extra=None):
    """cameras proprias de revisao 360 (as do il_gates cobrem 3/4 frente, costas e jogador):
    frente reta (silhueta), lado esquerdo, lado direito e os ornamentos laterais na altura do jogador (Eye/EyeR)"""
    gx, gy, gz, yaw = GS.gallery_slot(key)
    F = GS.gate_frame(gx, gy, gz, yaw)
    P = lambda x, y, z: tuple(round(v, 3) for v in F.p(x, y, z))
    cams = {
        "CAM_Gate_%s_Front" % key: (P(0.0, -50.0, 13.0), P(0.0, 0.0, 14.5), 24),
        "CAM_Gate_%s_Left" % key: (P(-44.0, -10.0, 13.0), P(0.0, 0.0, 13.0), 22),
        "CAM_Gate_%s_Right" % key: (P(44.0, 12.0, 13.0), P(0.0, 0.0, 13.0), 22),
        "CAM_Gate_%s_Eye" % key: (P(-4.5, -12.5, 4.8), P(-12.5, -2.0, 5.6), 18),
        "CAM_Gate_%s_EyeR" % key: (P(4.5, -12.5, 4.8), P(12.5, -2.0, 5.6), 18),
    }
    cams.update(extra or {})
    return cams


def make_cams(cams):
    import bpy
    for n, v in cams.items():
        if n not in bpy.data.objects:
            IL.camera(n, v[0], v[1], v[2] if len(v) > 2 else 20)


def scale_dummy(key, g, x=2.6, y=-4.2):
    """boneco cinza R15 (5,2 studs) na frente do portao, so para leitura de escala nos renders"""
    mb = MB("SCALE_Dummy_Gate%s" % key, "_SCALE_REFERENCE", None, detail="far", floor=-999)
    for dx, dz, sx, sz in ((-0.5, 1.0, 0.9, 2.0), (0.5, 1.0, 0.9, 2.0), (0, 3.0, 2.0, 2.0), (-1.5, 3.0, 0.9, 2.0),
                           (1.5, 3.0, 0.9, 2.0)):
        g.boxr(mb, (sx, 0.9 if sx < 2 else 1.0, sz), (x + dx, y, dz + 0.4), "Dummy_Grey", 0.0)
    g.boxr(mb, (1.15, 1.15, 1.15), (x, y, 5.0), "Dummy_Grey", 0.0)
    return mb.finish()


def tag(ob, key, part):
    if ob is not None:
        ob["gate"] = key
        ob["gate_part"] = part
    return ob
