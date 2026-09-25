# il_gates_kit - pecas comuns da FAMILIA de portoes de compra da galeria (Shadow Garden, Demon Slayer, One Piece,
# One Punch Man). Dono: zona "gates". So geometria no referencial do portao (il_gate_std.gate_frame):
#   x = direita de quem atravessa, y = sentido da travessia (-y = lado de quem chega), z = cima,
#   origem = centro do vao no nivel do piso (gz).
# Regras da familia (iguais nos 4): vao livre 16 x 18 (barreira/cadeado/colisao/marcadores do il_gate_std),
# 2 apoios principais em +-(8 + ~1.5), coroa/verga entre +18 e +26, altura <= 32, largura <= 44, ornamentos laterais
# fora de +-12, piso no nivel do tabuleiro. A barreira de energia corre num TRILHO (fenda) nas jambas e na verga:
# assim nenhuma face da barreira fica coplanar com a moldura (sem z-fighting) e o trilho continua legivel depois de
# desbloqueado.
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


class GMB(MB):
    """MB da familia: nivel de detalhe + teto de variantes tonais por familia (cada variante = 1 MeshPart)"""

    def __init__(self, name, rng=None, detail="hero", vcap=1):
        super().__init__(name, C, rng, detail=detail)
        self.vcap = vcap

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
            ga, gb = sorted((s * (xin + SLOT_DEPTH - 0.02), s * (xin + SLOT_DEPTH + 0.2)))
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
