# fm_terrain_guardian - marco do skyline: busto de um guardiao-ferreiro esculpido na face da montanha dominante NE
# (esta nos 7 concepts). Planos facetados grandes (leitura a ~400 studs): Stone_Light nos planos do rosto e do
# peito, Cliff_Rock_Mid no cabelo/barba/sobrancelhas/lenco, orbitas escuras e olhos em bloco, martelo no ombro.
# Objeto proprio TER_Guardian_Face, sem colisao (o export poe no SKYLINE).
import math
from mathutils import Vector, Matrix, Euler
from fm_lib import MB
from fm_parts import rock_column, _rock_poly

M_FACE = "Stone_Light"
M_HAIR = "Cliff_Rock_Mid"
M_DEEP = "Cliff_Rock_Mid_Dark"


class _G:
    """referencial do busto: u = lateral (direita de quem olha para ele), v = para a frente (para o vale), w = cima"""

    def __init__(self, mb, origin, fwd, s):
        self.mb = mb
        self.o = Vector(origin)
        f = Vector((fwd[0], fwd[1], 0.0)).normalized()
        self.f = f
        self.r = Vector((f.y, -f.x, 0.0))       # u: eixo x local das caixas (y local = frente)
        self.s = s
        self.yaw = math.atan2(self.r.y, self.r.x)

    def P(self, u, v, w):
        s = self.s
        return self.o + self.r * (u * s) + self.f * (v * s) + Vector((0, 0, w * s))

    def box(self, size, c, m, pitch=0.0, roll=0.0, yaw=0.0):
        s = self.s
        self.mb.box((size[0] * s, size[1] * s, size[2] * s), self.P(*c), (pitch, roll, self.yaw + yaw), m, 0.0)

    def poly(self, pts_uvw, m):
        """face plana a partir de pontos locais + piramide rasa para tras (fechada)"""
        mb = self.mb
        vs = [mb.bm.verts.new(self.P(*p)) for p in pts_uvw]
        c = sum((Vector(p) for p in pts_uvw), Vector()) / len(pts_uvw)
        ap = mb.bm.verts.new(self.P(c.x, c.y - 3.0, c.z))
        try:
            mb.bm.faces.new(vs)
            for i in range(len(vs)):
                mb.bm.faces.new((vs[(i + 1) % len(vs)], vs[i], ap))
        except ValueError:
            return
        mb._post(vs + [ap], m, None, 0, 1)

    def col(self, c, a, b, w0, w1, m, n=8, taper=0.9, chamfer=1.0, rng=None, a0=None):
        """massa facetada vertical (cranio, ombros) no referencial do busto"""
        s = self.s
        pl = _rock_poly(a * s, b * s, n, rng, ex=2.4, jit=0.04, a0=(math.pi / n if a0 is None else a0))
        pl = [(self.r.x * x + self.f.x * y, self.r.y * x + self.f.y * y) for x, y in pl]
        p = self.P(c[0], c[1], 0.0)
        rock_column(self.mb, Vector((p.x, p.y, 0.0)), pl, self.o.z + w0 * s, self.o.z + w1 * s, rng, m, taper=taper,
                    rings=1, jitter=0.03, tilt=0.0, chamfer=chamfer * s, rim=False, bottom=False)


def build(C, origin, fwd, height=74.0, rng=None):
    import random
    rng = rng or random.Random(777)
    mb = MB("TER_Guardian_Face", C, rng)
    g = _G(mb, origin, fwd, height / 74.0)
    # bloco de rocha do proprio macico atras do busto (liga o nicho a crista: nada flutua) + nicho escuro
    g.col((0, -17.0), 36.0, 11.0, -10.0, 88.0, M_HAIR, n=8, taper=0.78, chamfer=4.0, rng=rng)
    ring = []
    for i in range(10):
        t = math.tau * (i + 0.5) / 10
        ring.append((math.cos(t) * 34.0, -7.0, 40.0 + math.sin(t) * 44.0))
    g.poly(list(reversed(ring)), M_DEEP)
    # ombros e peito (planos facetados), alcas do avental
    g.col((0, -1.0), 30.0, 10.0, -6.0, 14.0, M_FACE, n=8, taper=0.82, chamfer=2.5, rng=rng)
    g.col((0, 0.0), 22.0, 9.0, 12.0, 24.0, M_FACE, n=8, taper=0.8, chamfer=2.0, rng=rng)
    for sg in (-1, 1):
        g.box((5.0, 2.0, 26.0), (sg * 9.0, 8.4, 11.0), M_HAIR, roll=sg * 0.42)
        g.box((12.0, 13.0, 6.0), (sg * 22.0, 0.5, 15.5), M_FACE, pitch=0.0, roll=sg * 0.35)   # dorso do ombro
    # cabeca (cranio facetado) + bochechas + orelhas
    g.col((0, 1.5), 13.5, 10.5, 34.0, 64.0, M_FACE, n=8, taper=0.9, chamfer=2.2, rng=rng)
    for sg in (-1, 1):
        g.box((7.5, 4.0, 7.0), (sg * 7.6, 10.4, 45.5), M_FACE, yaw=sg * 0.45, pitch=-0.12)
        g.box((3.0, 4.5, 7.0), (sg * 14.0, 1.5, 48.0), M_FACE, yaw=sg * 0.2)
    # testa larga e sobrancelhas pesadas (cenho franzido), orbitas escuras e olhos em bloco
    g.box((23.0, 3.0, 5.5), (0, 11.2, 57.0), M_FACE, pitch=0.18)
    for sg in (-1, 1):
        g.box((10.5, 4.2, 3.4), (sg * 5.8, 12.2, 53.6), M_HAIR, roll=sg * 0.2, pitch=0.25)
        g.box((7.2, 2.2, 3.8), (sg * 5.4, 11.3, 50.2), M_DEEP)
        g.box((2.6, 1.2, 2.2), (sg * 4.8, 12.3, 50.1), M_FACE)
    # nariz (cunha) e malar
    g.poly([(0.0, 12.4, 54.0), (-2.8, 12.0, 44.2), (0.0, 17.0, 44.8)], M_FACE)
    g.poly([(0.0, 12.4, 54.0), (0.0, 17.0, 44.8), (2.8, 12.0, 44.2)], M_FACE)
    g.poly([(-2.8, 12.0, 44.2), (2.8, 12.0, 44.2), (0.0, 17.0, 44.8)], M_FACE)
    # bigode caido e barba: massa facetada em cunha (larga no queixo, estreitando para baixo) + 3 trancas
    # facetadas com aneis de ferro (le como barba de ferreiro a 400 studs, nao como pilha de caixas)
    for sg in (-1, 1):
        g.box((10.5, 3.6, 3.2), (sg * 5.6, 13.2, 41.4), M_HAIR, roll=-sg * 0.35, pitch=0.1)
        g.box((4.0, 3.4, 6.0), (sg * 10.2, 12.0, 37.8), M_HAIR, roll=-sg * 0.15)
    g.col((0, 6.8), 7.5, 4.4, 20.0, 40.5, M_HAIR, n=8, taper=1.7, chamfer=1.2, rng=rng)
    for sg in (-1, 0, 1):
        u = sg * 5.4
        v = 9.6 - abs(sg) * 0.6
        w1 = 22.5 if sg else 21.0
        w0 = (8.5 if sg else 5.0)
        g.col((u, v), 2.3, 2.2, w0, w1, M_HAIR, n=6, taper=1.45, chamfer=0.6, rng=rng)
        for k in range(2):
            wr = w0 + (w1 - w0) * (0.3 + 0.35 * k)
            g.box((5.0 if not sg else 4.6, 4.8, 1.3), (u, v, wr), M_DEEP)   # anel de ferro
    # musgo nos ombros e no alto da cabeca (estatua antiga esculpida na montanha)
    for (u, v, w, r) in ((-23.0, 1.0, 19.2, 3.2), (-18.0, -3.0, 18.4, 2.4), (22.5, 0.0, 19.4, 3.0),
                         (0.0, -2.0, 68.8, 3.4), (7.5, -1.0, 66.8, 2.2), (-30.0, -8.0, 14.0, 2.8)):
        pl = _rock_poly(r * g.s, r * 0.8 * g.s, 7, rng, ex=2.0, jit=0.2)
        p = g.P(u, v, 0.0)
        rock_column(mb, Vector((p.x, p.y, 0.0)), pl, g.o.z + (w - r * 0.4) * g.s, g.o.z + (w + r * 0.55) * g.s, rng,
                    "Leaf_Moss", taper=0.5, rings=1, jitter=0.18, tilt=0.15, chamfer=r * 0.25 * g.s, rim=False,
                    bottom=False)
    # lenco de ferreiro na testa (com no do lado) e cabelo no alto
    g.col((0, 1.2), 14.3, 11.2, 57.5, 61.5, M_HAIR, n=8, taper=1.0, chamfer=0.0, rng=rng)
    g.box((4.0, 3.5, 7.0), (14.5, -3.0, 57.0), M_HAIR, roll=0.4)
    g.col((0, -0.5), 12.0, 9.5, 61.0, 68.5, M_HAIR, n=7, taper=0.72, chamfer=2.0, rng=rng)
    # mao fechada no cabo e martelo apoiado no ombro direito (lado -u)
    a = Vector((-17.0, 9.0, 4.0))
    b = Vector((-25.0, 6.0, 50.0))
    d = (b - a).normalized()
    n_ = 7
    for i in range(n_):
        c = a.lerp(b, (i + 0.5) / n_)
        g.box((3.0, 3.0, (b - a).length / n_ + 0.2), (c.x, c.y, c.z), M_FACE,
              pitch=-math.asin(d.y), roll=math.atan2(d.x, d.z))
    g.box((7.5, 7.0, 7.5), (-18.8, 9.8, 18.0), M_FACE, roll=0.15)
    g.box((15.0, 8.0, 8.0), (-25.5, 6.0, 52.0), M_HAIR, roll=math.atan2(d.x, d.z))
    g.box((2.5, 8.6, 8.6), (-18.6, 6.0, 53.3), M_DEEP, roll=math.atan2(d.x, d.z))
    return mb.finish()
