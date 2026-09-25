# il_exit_plan - geometria comum das zonas EXIT (ponte, ilhota, cabeceira) e GATE_DB (portao na ilhota).
# Tudo sai de il_layout (planta travada). Referencial da saida: Frame em EXIT_START com yaw = EXIT_DEG - 90:
#   x local = lateral (+ = direita de quem vai para a proxima ilha, lado SE), y local = d (distancia no eixo),
#   z = cota absoluta. Referencial do portao (il_gate_std): mesmo yaw, origem no eixo em d = D_GATE.
import math
import il_layout as L
from fm_parts import Frame
from il_lib import MB


# ------------------------------------------------------------------ regras da rodada 2 (critica tecnica)
def rule_bevel(dims, bevel):
    """bevel 0 se a menor dimensao < 1,0; senao no maximo 5% da menor dimensao"""
    mn = min(dims)
    if not bevel or mn < 1.0:
        return 0.0
    return min(bevel, 0.05 * mn)


class XMB(MB):
    """MB com as regras novas: microchanfro controlado (rule_bevel) e nada com TODAS as dimensoes < 0,35.
    vcap=1: sem variantes tonais (1 MeshPart por material: pecas pequenas repetidas)"""
    skipped = 0

    def __init__(self, name, collection, rng=None, detail="hero", floor=None, vcap=None):
        MB.__init__(self, name, collection, rng, detail, floor)
        self.vcap = vcap

    def _family(self, m):
        if self.vcap == 1:
            return None
        return MB._family(self, m)

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.12, seg=1, tint=None):
        if max(size) < 0.35:
            XMB.skipped += 1
            return
        MB.box(self, size, loc, rot, m, rule_bevel(size, bevel), seg, tint)

    def beam(self, a, b, w, h=None, m="Wood_Dark", bevel=0.08, roll=0.0, tint=None):
        from mathutils import Vector
        ln = (Vector(b) - Vector(a)).length
        dims = (ln, w, h or w)
        if max(dims) < 0.35:
            XMB.skipped += 1
            return
        MB.beam(self, a, b, w, h, m, rule_bevel(dims, bevel), roll, tint)

    def cyl(self, r, h, loc, rot=(0, 0, 0), m="Metal_Iron", n=12, r2=None, bevel=0.08, seg=1, caps=True, tint=None,
            angle=0.5):
        rmin = r if r2 is None else min(r, r2)
        if max(2 * max(r, r2 or 0.0), h) < 0.35:
            XMB.skipped += 1
            return
        MB.cyl(self, r, h, loc, rot, m, n, r2, rule_bevel((2 * rmin, h), bevel), seg, caps, tint, angle)

Z = L.EXIT_Z
HW = L.EXIT_W / 2.0                                  # 9: meia largura do tabuleiro
RAIL_X = 8.6                                         # eixo do guarda-corpo (face interna 8,0 -> passagem 16 = vao)
D_ISL = L.EXIT_BRIDGE_LEN                            # fim da ponte / inicio da plataforma da ilhota
D_END = L.EXIT_BRIDGE_LEN + L.ANCHOR_OFF             # cabeceira (ISLAND_NEXT_ANCHOR)
D_GATE = L.EXIT_BRIDGE_LEN + L.GATE_DB_OFF           # plano do portao DB
D_IC = L.EXIT_BRIDGE_LEN + L.GATE_ISLET_R - 4.0      # centro nominal da ilhota
PLAT_HW = 15.0                                       # meia largura da plataforma (30)
BAY_HW = 21.5                                        # nicho do portao: livre +-20 e guarda-corpo vermelho em 21,5
# nicho do portao no referencial do PORTAO (x, y = d - D_GATE), lado direito; o esquerdo e o espelho
BAY = [(PLAT_HW, -11.0), (BAY_HW, -7.0), (BAY_HW, 7.0), (PLAT_HW, 11.0)]
ANCHOR_PYLON_X = HW + 1.9                            # eixo dos pilones da cabeceira (face interna 9,2 -> vao 18,4)


def yaw():
    return math.radians(L.EXIT_DEG) - math.pi / 2


def frame():
    return Frame(L.EXIT_START[0], L.EXIT_START[1], 0.0, yaw())


def gate_frame_local():
    """portao no referencial da saida: (x, d)"""
    return 0.0, D_GATE


def outline():
    """contorno da plataforma da ilhota em (x lateral, d), anti-horario"""
    right = [(PLAT_HW, D_ISL)] + [(x, D_GATE + y) for x, y in BAY] + [(PLAT_HW, D_END)]
    left = [(-x, d) for x, d in reversed(right)]
    return right + left


def to_world(F, pts, z=None):
    out = []
    for p in pts:
        w = F.p(p[0], p[1], 0.0 if z is None else z)
        out.append((w.x, w.y) if z is None else (w.x, w.y, w.z))
    return out


def point_in(poly, x, y):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            ins = not ins
        j = i
    return ins


def dist_to_edges(poly, x, y):
    best = 1e9
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        ln2 = dx * dx + dy * dy or 1e-9
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ln2))
        best = min(best, math.hypot(x - ax - dx * t, y - ay - dy * t))
    return best


def hull(pts):
    """fecho convexo (cadeia monotona), anti-horario"""
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def rounded_offset(poly, m, n_arc=6):
    """fecho convexo do contorno afastado m (cantos arredondados)"""
    pts = []
    for x, y in poly:
        for k in range(n_arc * 4):
            a = math.tau * k / (n_arc * 4)
            pts.append((x + m * math.cos(a), y + m * math.sin(a)))
    return hull(pts)


def edge_crossing(F, lateral, poly, d0=0.0, d1=160.0, step=0.1):
    """primeiro d em que a linha lateral 'lateral' sai do poligono (mundo)"""
    last = None
    d = d0
    while d <= d1:
        w = F.p(lateral, d, 0.0)
        ins = point_in(poly, w.x, w.y)
        if last is not None and ins != last:
            return d
        last = ins
        d += step
    return None
