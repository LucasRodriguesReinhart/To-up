# fm_portal_kit - pecas e materiais dos portais (lanternas japonesas, cordas, laminas, correntes, lofts, pisos).
# Tudo e geometria + cor solida (no Roblox cada material vira uma MeshPart); nada depende do ruido do shader.
import math, random
import bmesh
from mathutils import Vector, Matrix, Quaternion, Euler
import fm_lib
from fm_lib import D, col_box, light, point_in_poly

# ------------------------------------------------------------------ materiais novos (registrados antes de make_materials)
_M = fm_lib.MATS.setdefault
_M("P_DS_Char",      ((0.020, 0.016, 0.015), 0.9, 0.0, 0, None, 0.10))    # madeira carbonizada
_M("P_DS_Blood",     ((0.20, 0.010, 0.012), 0.6, 0.0, 0, None, 0.06))     # vermelho-sangue escuro
_M("P_DS_Ember_Glow", ((1.0, 0.22, 0.04), 0.5, 0.0, 7.0, (1.0, 0.26, 0.04), 0.0))  # brasa (nome *_Glow = Neon)
_M("P_DS_Checker",   ((0.015, 0.20, 0.10), 0.8, 0.0, 0, None, 0.04))      # xadrez verde do haori
_M("P_DS_Wisteria",  ((0.46, 0.24, 0.88), 0.8, 0.0, 0.4, (0.55, 0.32, 1.0), 0.08))
_M("Metal_Blade",    ((0.62, 0.66, 0.74), 0.22, 1.0, 0, None, 0.02))
_M("P_Naruto_Wall",  ((0.80, 0.75, 0.66), 0.9, 0.0, 0, None, 0.05))      # reboco claro do muro da vila
_M("P_Naruto_Tile",  ((0.07, 0.09, 0.13), 0.7, 0.0, 0, None, 0.08))      # telha escura azulada
_M("P_Naruto_Orange", ((0.95, 0.30, 0.02), 0.8, 0.0, 0, None, 0.05))     # laranja dos nobori
_M("P_Gravel",       ((0.46, 0.44, 0.40), 0.95, 0.0, 0, None, 0.06))     # cascalho rastelado
_M("P_Moss",         ((0.16, 0.38, 0.06), 0.9, 0.0, 0, None, 0.12))
_M("P_Bamboo",       ((0.34, 0.52, 0.12), 0.7, 0.0, 0, None, 0.10))
_M("P_DB_Star",      ((0.85, 0.05, 0.02), 0.4, 0.0, 1.0, (1.0, 0.1, 0.05), 0.0))
_M("P_DB_Energy_Glow", ((1.0, 0.48, 0.04), 0.3, 0.0, 1.3, (1.0, 0.45, 0.03), 0.0))
_M("P_DB_Blue",      ((0.05, 0.25, 0.75), 0.5, 0.0, 0, None, 0.05))
_M("P_DB_Dragon",    ((0.05, 0.36, 0.09), 0.45, 0.1, 0, None, 0.08))    # dragao verde
_M("P_DB_Ball",     ((1.0, 0.38, 0.02), 0.25, 0.0, 0.5, (1.0, 0.45, 0.05), 0.0))      # esfera do dragao
_M("P_Shadow_Trim",  ((0.24, 0.20, 0.32), 0.7, 0.0, 0, None, 0.08))      # friso violeta-acinzentado
_M("P_Shadow_Cloth", ((0.10, 0.02, 0.20), 0.9, 0.0, 0, None, 0.05))
_M("P_OPM_Yellow",   ((0.95, 0.62, 0.02), 0.6, 0.0, 0, None, 0.04))
_M("P_OPM_DarkGlass", ((0.02, 0.035, 0.08), 0.2, 0.3, 0.06, (0.05, 0.18, 0.5), 0.04))   # pele de vidro escura
_M("P_OPM_Red",      ((0.75, 0.04, 0.03), 0.5, 0.0, 0, None, 0.04))
_M("P_OP_Sail",      ((0.86, 0.80, 0.66), 0.9, 0.0, 0, None, 0.04))
_M("P_OP_Red",       ((0.62, 0.07, 0.05), 0.8, 0.0, 0, None, 0.06))
# aro de energia de cada portal (Neon no Roblox: nome *_Glow), mais claro que o miolo da espiral
_M("P_Naruto_Glow",  ((1.0, 0.62, 0.16), 0.4, 0.0, 6.0, (1.0, 0.60, 0.14), 0.0))
_M("P_DB_Glow",      ((1.0, 0.86, 0.42), 0.4, 0.0, 6.0, (1.0, 0.84, 0.38), 0.0))
_M("P_DS_Glow",      ((1.0, 0.20, 0.22), 0.4, 0.0, 6.0, (1.0, 0.18, 0.20), 0.0))
_M("P_OP_Glow",      ((0.42, 0.74, 1.0), 0.4, 0.0, 6.0, (0.38, 0.70, 1.0), 0.0))
_M("P_OPM_Glow",     ((0.50, 0.90, 1.0), 0.4, 0.0, 6.5, (0.48, 0.88, 1.0), 0.0))
_M("P_DS_Tile",      ((0.030, 0.030, 0.036), 0.45, 0.1, 0, None, 0.06))  # telha preta (karahafu)
_M("P_Konoha_Door",  ((0.09, 0.22, 0.12), 0.8, 0.0, 0, None, 0.06))      # folhas pintadas do Grande Portao
GLOW = {"Naruto": "P_Naruto_Glow", "DragonBall": "P_DB_Glow", "ShadowGarden": "P_Shadow_Glow",
        "DemonSlayer": "P_DS_Glow", "OnePiece": "P_OP_Glow", "OnePunchMan": "P_OPM_Glow"}
# cor da luz de cada portal (pad e espiral)
LIGHT_COL = {"Naruto": (1.0, 0.55, 0.18), "DragonBall": (1.0, 0.78, 0.3), "ShadowGarden": (0.62, 0.25, 1.0),
             "DemonSlayer": (1.0, 0.22, 0.22), "OnePiece": (0.25, 0.55, 1.0), "OnePunchMan": (0.35, 0.8, 1.0)}


# ------------------------------------------------------------------ utilidades de geometria
def V(*a):
    return Vector(a if len(a) == 3 else (a[0], a[1], a[2] if len(a) > 2 else 0.0))


def frames(pts, up=(0, 0, 1)):
    """tangentes + normais por transporte paralelo (sem torcao)"""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    T = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        if t.length < 1e-9:
            t = T[-1].copy() if T else Vector((1, 0, 0))
        T.append(t.normalized())
    u = Vector(up)
    if abs(T[0].dot(u)) > 0.95:
        u = Vector((1, 0, 0)) if abs(T[0].x) < 0.9 else Vector((0, 1, 0))
    N = [(u - T[0] * u.dot(T[0])).normalized()]
    for i in range(1, n):
        a, b = T[i - 1], T[i]
        ax = a.cross(b)
        if ax.length < 1e-8:
            nv = N[-1].copy()
        else:
            nv = Quaternion(ax.normalized(), a.angle(b)) @ N[-1]
        nv = (nv - b * nv.dot(b))
        N.append(nv.normalized() if nv.length > 1e-9 else N[-1].copy())
    B = [t.cross(nn) for t, nn in zip(T, N)]
    return pts, T, N, B


def loft(mb, pts, profiles, m, caps=True, up=(0, 0, 1), tint=None):
    """varre perfis 2D (a ao longo de N, b ao longo de B) diferentes em cada ponto (mesmo numero de vertices)"""
    pts, T, N, B = frames(pts, up)
    bm = mb.bm
    rings = []
    for p, nn, bb, prof in zip(pts, N, B, profiles):
        rings.append([bm.verts.new(p + nn * a + bb * b) for a, b in prof])
    k = len(profiles[0])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            j2 = (j + 1) % k
            try:
                bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
            except ValueError:
                pass
    if caps:
        for r in (rings[0], rings[-1]):
            try:
                bm.faces.new(r)
            except ValueError:
                pass
    mb._post([v for r in rings for v in r], m, tint, 0, 1)


def circ(r, n, a0=0.0, sx=1.0, sy=1.0):
    return [(math.cos(a0 + math.tau * i / n) * r * sx, math.sin(a0 + math.tau * i / n) * r * sy) for i in range(n)]


def taper_tube(mb, pts, radii, m, n=8, caps=True, up=(0, 0, 1), flat=1.0):
    loft(mb, pts, [circ(r, n, sy=flat) for r in radii], m, caps, up)


def cone(mb, a, b, r0, r1, m, n=6):
    """tronco de cone de a ate b (r0 na base, r1 no topo)"""
    a, b = Vector(a), Vector(b)
    d = b - a
    if d.length < 1e-4:
        return
    q = d.to_track_quat("Z", "Y")
    M = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    res = bmesh.ops.create_cone(mb.bm, cap_ends=True, cap_tris=False, segments=n, radius1=r0, radius2=max(r1, 0.0),
                                depth=d.length, matrix=M)
    mb._post(res["verts"], m, None, 0, 1)


def plate(mb, pts2d, origin, u, v, thick, m, bevel=0.0, tint=None):
    """poligono 2D (u,v) extrudado na normal u x v (espessura centrada)"""
    o, u, v = Vector(origin), Vector(u).normalized(), Vector(v).normalized()
    nrm = u.cross(v).normalized()
    bm = mb.bm
    f = [bm.verts.new(o + u * a + v * b + nrm * thick / 2) for a, b in pts2d]
    k = [bm.verts.new(o + u * a + v * b - nrm * thick / 2) for a, b in pts2d]
    n = len(pts2d)
    try:
        bm.faces.new(f)
        bm.faces.new(list(reversed(k)))
    except ValueError:
        pass
    for i in range(n):
        j = (i + 1) % n
        try:
            bm.faces.new((f[j], f[i], k[i], k[j]))
        except ValueError:
            pass
    mb._post(f + k, m, tint, bevel, 1, angle=0.6)


def ring_pts(c, R, u, v, a0=0.0, a1=360.0, n=36):
    c, u, v = Vector(c), Vector(u).normalized(), Vector(v).normalized()
    return [c + (u * math.cos(D(a0 + (a1 - a0) * i / n)) + v * math.sin(D(a0 + (a1 - a0) * i / n))) * R
            for i in range(n + 1)]


def ring(mb, c, R, u, v, w, h, m, a0=0.0, a1=360.0, n=36):
    """aro (secao w radial x h na normal do plano) no plano (u, v)"""
    pts = ring_pts(c, R, u, v, a0, a1, n)
    nrm = Vector(u).normalized().cross(Vector(v).normalized())
    mb.sweep(pts, [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], m, True, up=tuple(nrm))


def chain(mb, a, b, sag=1.5, link=0.8, m="Metal_Dark", t=0.2, w=0.5):
    """corrente de elos alternados (sem bevel, barata)"""
    a, b = Vector(a), Vector(b)
    n = max(2, int((b - a).length / link))
    pts = []
    for i in range(n + 1):
        f = i / n
        p = a + (b - a) * f
        p.z -= sag * 4 * f * (1 - f)
        pts.append(p)
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        d = (p1 - p0)
        e = d.normalized() * 0.08
        mb.beam(p0 - e, p1 + e, t if i % 2 else w, w if i % 2 else t, m, 0.0)


def chain_path(mb, pts, link=0.8, m="Metal_Dark", t=0.2, w=0.5):
    from fm_lib import resample
    pts = resample([Vector(p) for p in pts], link)
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        e = (p1 - p0).normalized() * 0.08
        mb.beam(p0 - e, p1 + e, t if i % 2 else w, w if i % 2 else t, m, 0.0)


def rope_twist(mb, pts, r, m="Rope", n=6, strands=2, pitch=2.2, taper=0.45, seg=None):
    """corda torcida grossa (shimenawa): fios helicoidais em volta da linha central, mais grossa no meio"""
    from fm_lib import resample
    pts = resample([Vector(p) for p in pts], seg or max(0.35, r * 0.7))
    pts, T, N, B = frames(pts)
    L = 0.0
    arc = [0.0]
    for p0, p1 in zip(pts, pts[1:]):
        L += (p1 - p0).length
        arc.append(L)
    for s in range(strands):
        ph = math.tau * s / strands
        cen, rad = [], []
        for p, nn, bb, a in zip(pts, N, B, arc):
            f = a / max(L, 1e-6)
            sc = (1 - taper) + taper * math.sin(math.pi * f)
            ang = ph + math.tau * a / pitch
            off = (nn * math.cos(ang) + bb * math.sin(ang)) * r * 0.45 * sc
            cen.append(p + off)
            rad.append(r * 0.62 * sc)
        taper_tube(mb, cen, rad, m, n)


def shide(mb, p, s=1.0, m="Emblem_Cream", yaw=0.0):
    """tira de papel dobrada em zigue-zague (raio) pendurada em p"""
    pts = [(-0.34, 0.0), (0.34, 0.0), (0.34, -0.52), (0.62, -0.52), (0.18, -1.12), (0.44, -1.12), (-0.2, -1.95),
           (-0.02, -1.26), (-0.3, -1.26), (0.06, -0.66), (-0.34, -0.66)]
    pts = [(a * s, b * s) for a, b in pts]
    plate(mb, pts, p, (math.cos(yaw), math.sin(yaw), 0), (0, 0, 1), 0.08, m)


class LeanMB(fm_lib.MB):
    """MB com orcamento de malhas mais apertado: no maximo `vcap` variantes tonais por familia (no Roblox cada
    variante vira uma MeshPart). As variantes continuam sorteadas por primitiva; so o numero de tons cai."""

    def __init__(self, name, collection, rng=None, vcap=2):
        super().__init__(name, collection, rng)
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


def octa(mb, c, r, h, m, rot=0.0, tint=None, n=4):
    """bipiramide (floreta barata: 2n tris; n=4 octaedro) com meia-altura h"""
    c = Vector(c)
    bm = mb.bm
    eq = [bm.verts.new(c + V(math.cos(rot + math.tau * i / n) * r, math.sin(rot + math.tau * i / n) * r, 0))
          for i in range(n)]
    top = bm.verts.new(c + V(0, 0, h))
    bot = bm.verts.new(c - V(0, 0, h))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((eq[i], eq[j], top))
        bm.faces.new((eq[j], eq[i], bot))
    mb._post(eq + [top, bot], m, tint, 0, 1)


def cluster(mb, top, length, m, r0, rng=None, n=4, step=0.62, lump=0.72, sway=0.12, taper=0.72, head=1.0, tip=0.12,
            neck=0.5):
    """peca pendente CONTINUA (cacho de glicinia, trepadeira): tubo afunilado com gomos (aneis largo/estreito
    alternados, torcidos), preso em cima pelo pescoco. Uma ilha so por cacho: nada solto no ar."""
    top = Vector(top)
    k = max(3, int(round(length / step)))
    ph = rng.uniform(0, math.tau) if rng else 0.0
    pts, profs = [], []
    for i in range(k + 1):
        f = i / k
        off = V(math.sin(ph + f * 3.1) * sway * f, math.cos(ph + f * 2.3) * sway * f, 0)
        pts.append(top - V(0, 0, length * f) + off)
        if i == 0:
            r = r0 * neck
        elif i == k:
            r = max(0.05, r0 * tip)
        else:
            r = r0 * head * (1.0 - taper * f ** 1.3) * (1.0 if i % 2 else lump)
        profs.append(circ(r, n, a0=i * 0.7))
    loft(mb, pts, profs, m, True, up=(1, 0, 0))


def raceme(mb, top, length, m="P_DS_Wisteria", r0=0.5, rng=None):
    """cacho pendente (glicinia) numa peca so: cheio em cima (gomos largos sobrepostos), afinando ate a ponta
    arredondada; proporcao ~1:5 (nao le como pingente de gelo)"""
    cluster(mb, top, length, m, r0, rng, n=4, step=0.55, lump=0.64, sway=0.08, taper=0.7, head=1.5, tip=0.42,
            neck=0.8)


def cup(mb, c, R, y0, y1, m, n=32):
    """tampa traseira do portal: parede cilindrica curta + fundo, aberta para a frente (fica atras do prato
    da espiral). O verso do portal passa a ler como costas escuras, nao como a mesma espiral."""
    c = Vector(c)
    bm = mb.bm
    f = [bm.verts.new(c + V(math.cos(math.tau * i / n) * R, y0, math.sin(math.tau * i / n) * R)) for i in range(n)]
    b = [bm.verts.new(c + V(math.cos(math.tau * i / n) * R, y1, math.sin(math.tau * i / n) * R)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((f[i], b[i], b[j], f[j]))
    bm.faces.new(list(reversed(b)))
    mb._post(f + b, m, None, 0, 1)


def round_hole_panel(mb, cx, cy, z0, z1, hw, cz, r, thick, m, n=14, tint=None):
    """painel vertical (plano XZ, espessura em Y) com abertura circular: duas metades concavas.
    Coordenadas: x relativo a cx (-hw..hw), z absoluto (z0..z1), furo de raio r centrado em (0, cz)."""
    for s in (-1, 1):
        # s<0: o arco sobe pelo lado esquerdo do furo; s>0: desce pelo lado direito (poligonos anti-horarios)
        if s < 0:
            arc = [(math.cos(D(270 - 180 * i / n)) * r, cz + math.sin(D(270 - 180 * i / n)) * r) for i in range(n + 1)]
            pts = [(-hw, z0), (0.0, z0)] + arc + [(0.0, z1), (-hw, z1)]
        else:
            arc = [(math.cos(D(-90 + 180 * i / n)) * r, cz + math.sin(D(-90 + 180 * i / n)) * r) for i in range(n + 1)]
            pts = [(hw, z0), (hw, z1), (0.0, z1)] + list(reversed(arc)) + [(0.0, z0)]
        plate(mb, pts, (cx, cy, 0.0), (1, 0, 0), (0, 0, 1), thick, m, tint=tint)


def ki_flame(mb, base, up, side, h, w, th, m, bend=0.25, n=6):
    """chama/aura de ki em volume: loft afunilado (losango) que sobe curvando; espessura th na base"""
    base, up, side = Vector(base), Vector(up).normalized(), Vector(side).normalized()
    pts, profs = [], []
    for i in range(n + 1):
        t = i / n
        p = base + up * (h * t) + side * (bend * h * t * t)
        pts.append(p)
        ww = w * (1.0 - t) ** 0.8 * (0.75 + 0.5 * math.sin(math.pi * min(1.0, t * 1.4)))
        tt = th * (1.0 - t) ** 0.9 + 0.05
        ww = max(ww, 0.06)
        profs.append([(0.0, ww / 2), (tt / 2, 0.0), (0.0, -ww / 2), (-tt / 2, 0.0)])
    loft(mb, pts, profs, m, True, up=tuple(side.cross(up)))


def palm_small(mb, loc, h, rng, frond=4.2, lean=(0.0, 0.0), n=6, a0=None):
    """palmeira compacta: tronco em aneis inclinado + folhas arqueadas de comprimento controlado (cabe no lote)"""
    x, y, z = loc
    top = V(x + lean[0], y + lean[1], z + h)
    pts = [V(x, y, z - 0.3)] + [V(x + lean[0] * t * t, y + lean[1] * t * t, z + h * t) for t in (0.33, 0.66, 1.0)]
    taper_tube(mb, pts, [0.55, 0.48, 0.42, 0.36], "Bark", 6)
    for k in range(3):
        p = pts[1] + (pts[3] - pts[1]) * (k / 3)
        mb.cyl(0.5, 0.25, p, (0, 0, 0), "Bark", 6, bevel=0.0)
    a0 = rng.uniform(0, math.tau) if a0 is None else a0
    for k in range(n):
        b = a0 + k * math.tau / n + rng.uniform(-0.2, 0.2)
        d = V(math.cos(b), math.sin(b), 0)
        leaf = [top, top + d * frond * 0.5 + V(0, 0, 0.8), top + d * frond - V(0, 0, 0.9)]
        mb.sweep(leaf, [(-0.95, 0), (0, 0.22), (0.95, 0), (0, -0.05)], "Leaf_Palm", True)
    mb.ico(0.6, top, "Bark", 1)


def barrel_small(mb, loc, r=1.0, h=2.4, m="Wood_Plank", band="Metal_Dark", n=8):
    """barril barato (2 troncos de cone + 2 cintas): ~100 tris"""
    x, y, z = loc
    mb.cyl(r, h * 0.5, (x, y, z + h * 0.25), (0, 0, 0), m, n, r2=r * 1.12, bevel=0.0)
    mb.cyl(r * 1.12, h * 0.5, (x, y, z + h * 0.75), (0, 0, 0), m, n, r2=r, bevel=0.0)
    for zz in (0.22, h - 0.22):
        mb.cyl(r * 1.05, 0.2, (x, y, z + zz), (0, 0, 0), band, n, bevel=0.0)


def sakura_small(mb, loc, h, rng, bark="Wood_Dark", leaf="Leaf_Sakura", pads=4, reach=0.28):
    """cerejeira compacta: tronco torto + bracos + almofadas rosas lobadas (fm_veg_kit), sem fundo escuro
    (2 materiais so). reach = alcance dos bracos em fracao de h (controla a largura da copa)."""
    import fm_veg_kit as VK
    x, y, z = loc
    w = rng.uniform(0, math.tau)
    bend = h * 0.12
    p0 = V(x, y, z - 0.4)
    p1 = V(x + math.cos(w) * bend * 0.3, y + math.sin(w) * bend * 0.3, z + h * 0.35)
    p2 = V(x + math.cos(w) * bend, y + math.sin(w) * bend, z + h * 0.62)
    VK.ttube(mb, [p0, p1, p2], [h * 0.07, h * 0.05, h * 0.035], bark, n=5, cap1=False)
    tops = [(p2 + V(0, 0, h * 0.08), h * 0.28)]
    for i in range(pads - 1):
        a = w + math.pi + (i - (pads - 2) / 2) * 1.9 + rng.uniform(-0.3, 0.3)
        base = p1.lerp(p2, rng.uniform(0.4, 0.9))
        end = base + V(math.cos(a) * h * reach, math.sin(a) * h * reach, h * rng.uniform(0.08, 0.16))
        VK.ttube(mb, [base, end], [h * 0.03, h * 0.018], bark, n=4, cap1=False)
        tops.append((end, h * rng.uniform(0.18, 0.22)))
    for (pc, pr) in tops:
        VK.tier(mb, (pc.x, pc.y, pc.z - pr * 0.25), pr, pr * 0.9, 6, leaf, rng, lob=0.22, droop=0.3, under=None,
                bulge=(0.42, 1.5), jit=0.16)


def vine(mb, top, length, rng, m="Leaf_Pine_Light", r=0.55, sway=0.5):
    """trepadeira pendente numa peca so (cai da borda de um patamar): tubo de folhagem com gomos, balancando"""
    cluster(mb, top, length, m, r, rng, n=5, step=0.9, lump=0.62, sway=sway, taper=0.55)


def _box_links(hx, hy, off, link):
    """pontas dos elos de UMA volta em torno de um pilar retangular (meias-larguras hx, hy), a `off` das faces:
    elos retos ao longo de cada face e um elo de quina com a ponta na diagonal (a `off` da aresta do pilar, sem
    cortar a quina). Comeca no meio da face da frente (-Y), sentido anti-horario."""
    corners = [(hx, -hy, -45.0), (hx, hy, 45.0), (-hx, hy, 135.0), (-hx, -hy, 225.0)]
    pts = [(0.0, -(hy + off))]
    faces = [((0.0, -(hy + off)), (hx, -(hy + off))), ((hx + off, -hy), (hx + off, hy)),
             ((hx, hy + off), (-hx, hy + off)), ((-(hx + off), hy), (-(hx + off), -hy)),
             ((-hx, -(hy + off)), (0.0, -(hy + off)))]
    for i, (a, b) in enumerate(faces):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(math.ceil(L_ / link)))
        if i > 0:
            pts.append(a)
        for j in range(1, k + 1):
            pts.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
        if i < 4:
            cx, cy, ang = corners[i]
            pts.append((cx + math.cos(D(ang)) * off, cy + math.sin(D(ang)) * off))
    return pts


def helix_chain(mb, c, hx, hy, z0, z1, pitch, m="Metal_Dark", link=0.8, t=0.2, w=0.5, clamp_m=None, off=0.25):
    """corrente helicoidal ABRACANDO um pilar retangular (meias-larguras hx, hy): o eixo da corrente segue a face
    do fuste a `off` (meia-largura + 0.25), inclusive nas quinas, subindo `pitch` por volta; grampo de ferro (caixa
    0.4, cravado no fuste) a cada volta, na face da frente"""
    c = Vector(c)
    ring = _box_links(hx, hy, off, link)
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ring, ring[1:])]
    per = sum(seg)
    turns = (z1 - z0) / pitch
    pts = []
    k = 0
    while True:
        acc = 0.0
        done = False
        for a, L_ in zip(ring[:-1], seg):
            s = k + acc / per
            if s > turns:
                done = True
                break
            pts.append(V(c.x + a[0], c.y + a[1], z0 + pitch * s))
            acc += L_
        if done:
            break
        k += 1
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        e = (p1 - p0).normalized() * 0.08
        mb.beam(p0 - e, p1 + e, t if i % 2 else w, w if i % 2 else t, m, 0.0)
    for k in range(int(turns) + 1):
        zz = z0 + pitch * k
        if zz > z1:
            continue
        # grampo: da face do fuste ate o elo (cravado 0.05 no pilar)
        mb.box((0.4, off + 0.25, 0.4), (c.x, c.y - hy - (off + 0.25) / 2 + 0.05, zz), (0, 0, 0), clamp_m or m, 0.0)


def mossy_rock(mb, loc, size, rng, m="Cliff_Rock", moss="P_Moss", cap=0.55, sub=1):
    x, y, z = loc
    sx, sy, sz = size
    mb.rock((x, y, z + sz * 0.3), (sx, sy, sz), m, sub, (0, 0, rng.uniform(0, 6)))
    if moss:
        mb.ico(max(sx, sy) * cap * 0.5, (x + rng.uniform(-0.2, 0.2) * sx, y + rng.uniform(-0.2, 0.2) * sy, z + sz * 0.72),
               moss, 1, (1.0, sy / sx * 0.95, 0.32), jitter=0.2)


def flag_floor(mb, poly, z, rng, m="Stone_Paving", m2=None, tile=3.4, h=0.4, bevel=0.1, gap=0.2, base_m="Stone_Grout",
               mix=0.2, base=True):
    """lajes irregulares (fileiras de comprimentos variados) recortadas pelo poligono; base continua embaixo"""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    if base:
        mb.prism(poly, z - 0.5, z + h * 0.4, base_m, 0.0)
    y = min(ys)
    row = 0
    while y < max(ys) - 0.3:
        rh = tile * rng.uniform(0.7, 1.0)
        yc = y + rh / 2
        x = min(xs) - rng.uniform(0, tile * 0.7)
        while x < max(xs):
            w = tile * rng.uniform(0.8, 1.45)
            xc = x + w / 2
            if point_in_poly(xc, yc, poly):
                hh = h + rng.uniform(-0.06, 0.06)
                mm = m2 if (m2 and rng.random() < mix) else m
                mb.box((w - gap, rh - gap, hh), (xc, yc, z + hh / 2), (0, 0, rng.uniform(-0.02, 0.02)), mm, bevel)
            x += w
        y += rh
        row += 1


def deck(mb, x0, x1, y0, y1, z, rng, m="Wood_Plank", pw=1.35, gap=0.14, h=0.35, jog=0.25):
    """assoalho de cais: tabuas ao longo de X, pontas desencontradas"""
    y = y0
    while y < y1 - 0.2:
        w = min(pw, y1 - y)
        a = x0 + rng.uniform(-jog, jog)
        b = x1 + rng.uniform(-jog, jog)
        mb.box((b - a, w - gap, h), ((a + b) / 2, y + w / 2, z - h / 2 + rng.uniform(-0.03, 0.03)),
               (0, 0, rng.uniform(-0.008, 0.008)), m, 0.0, tint=rng.uniform(-1, 1))
        y += w


# ------------------------------------------------------------------ pecas japonesas
def toro(mb, loc, s=1.0, m="Stone_Light", m2="Stone_Dark", glow="Lantern_Glow", yaw=0.0, name=None, lit=True):
    """lanterna de pedra (kasuga-doro): base, fuste, prato, camara de luz, chapeu hexagonal com pontas, joia"""
    x, y, z = loc
    c = Vector((x, y, z))
    mb.cyl(1.25 * s, 0.5 * s, c + V(0, 0, 0.25 * s), (0, 0, yaw), m2, 6, bevel=0.06)
    mb.cyl(0.95 * s, 0.35 * s, c + V(0, 0, 0.65 * s), (0, 0, yaw), m, 6, r2=0.6 * s, bevel=0.0)
    mb.cyl(0.42 * s, 2.3 * s, c + V(0, 0, 1.95 * s), (0, 0, yaw), m, 8, r2=0.36 * s, bevel=0.0)
    mb.cyl(1.05 * s, 0.4 * s, c + V(0, 0, 3.3 * s), (0, 0, yaw), m, 6, r2=1.15 * s, bevel=0.05)
    mb.cyl(0.72 * s, 1.15 * s, c + V(0, 0, 4.08 * s), (0, 0, yaw + D(30)), glow, 6, bevel=0.0)
    for k in range(3):
        a = yaw + D(60 * k * 2 + 30)
        mb.box((0.28 * s, 0.28 * s, 1.15 * s), c + V(math.cos(a) * 0.78 * s, math.sin(a) * 0.78 * s, 4.08 * s), (0, 0, a), m,
               0.0)
    mb.cyl(1.7 * s, 0.75 * s, c + V(0, 0, 5.05 * s), (0, 0, yaw), m2, 6, r2=0.45 * s, bevel=0.0)
    for k in range(6):
        a = yaw + D(60 * k)
        p = c + V(math.cos(a) * 1.62 * s, math.sin(a) * 1.62 * s, 4.72 * s)
        cone(mb, p, p + V(math.cos(a) * 0.35 * s, math.sin(a) * 0.35 * s, 0.55 * s), 0.16 * s, 0.02, m2, 4)
    mb.cyl(0.3 * s, 0.4 * s, c + V(0, 0, 5.6 * s), (0, 0, 0), m2, 6, bevel=0.0)
    mb.ico(0.32 * s, c + V(0, 0, 6.0 * s), m2, 1, (1, 1, 1.25))
    if lit and name:
        light(name, "POINT", c + V(0, 0, 4.1 * s), 140 * s, (1.0, 0.62, 0.3), 0.3)


def chochin(mb, loc, r=1.0, h=1.9, paper="Lantern_Glow", cap="Wood_Dark", band=None, hang=1.2, n=8, rod_m=None):
    """lanterna de papel pendurada (loc = ponto de fixacao em cima)"""
    x, y, z = loc
    top = Vector((x, y, z))
    if hang > 0:
        mb.rod(top, top - V(0, 0, hang), 0.07, rod_m or "Metal_Dark", 4)
    c = top - V(0, 0, hang + 0.25 + h / 2)
    mb.cyl(r * 0.78, h * 0.5, c + V(0, 0, h * 0.25), (0, 0, 0), paper, n, r2=r * 0.62, bevel=0.0)
    mb.cyl(r * 0.62, h * 0.5, c - V(0, 0, h * 0.25), (0, 0, 0), paper, n, r2=r * 0.78, bevel=0.0)
    if band:
        mb.cyl(r * 0.8, h * 0.16, c, (0, 0, 0), band, n, bevel=0.0)
    for sgn in (-1, 1):
        mb.cyl(r * 0.66, 0.26, c + V(0, 0, sgn * (h / 2 + 0.1)), (0, 0, 0), cap, n, bevel=0.0)
    return c


def tile_coping(mb, a, b, z, w, m="P_Naruto_Tile", ridge_m="P_Naruto_Tile", over=0.7, rise=0.9, t=0.32):
    """telhadinho de duas aguas sobre um muro (cumeeira de a ate b, na cota z)"""
    a, b = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
    d = b - a
    L = d.length
    ang = math.atan2(d.y, d.x)
    nrm = Vector((-math.sin(ang), math.cos(ang), 0))
    half = w / 2 + over
    slope = math.atan2(rise, half)
    ln = math.hypot(half, rise)
    for s in (-1, 1):
        c = (a + b) / 2 + nrm * s * half / 2 + V(0, 0, rise / 2)
        mb.box((L + over * 1.4, ln + 0.15, t), c, (-s * slope, 0, ang), m, 0.06)
    mb.box((L + over * 1.6, 0.55, 0.5), (a + b) / 2 + V(0, 0, rise + 0.15), (0, 0, ang), ridge_m, 0.08)
    for p in (a - d.normalized() * (over * 0.8 + 0.05), b + d.normalized() * (over * 0.8 + 0.05)):
        mb.box((0.6, 0.7, 0.6), p + V(0, 0, rise + 0.2), (0, 0, ang), ridge_m, 0.06)


def village_wall(mb, a, b, z0, h, rng, thick=1.2, m="P_Naruto_Wall", base_m="Stone_Dark", post_m="Wood_Dark",
                 roof_m="P_Naruto_Tile", post_step=3.4):
    """muro de vila (tsuiji-bei): embasamento de pedra, reboco claro, montantes de madeira, telhadinho"""
    a, b = Vector((a[0], a[1], z0)), Vector((b[0], b[1], z0))
    d = b - a
    L = d.length
    ang = math.atan2(d.y, d.x)
    dn = d.normalized()
    mb.box((L + 0.3, thick + 0.5, 1.3), (a + b) / 2 + V(0, 0, 0.55), (0, 0, ang), base_m, 0.15)
    mb.box((L, thick, h - 1.3), (a + b) / 2 + V(0, 0, 1.3 + (h - 1.3) / 2 - 0.05), (0, 0, ang), m, 0.06)
    n = max(1, int(round(L / post_step)))
    for i in range(n + 1):
        p = a + dn * (L * i / n)
        mb.box((0.55, thick + 0.18, h - 1.2), p + V(0, 0, 1.2 + (h - 1.2) / 2), (0, 0, ang), post_m, 0.0)
    mb.box((L + 0.2, thick + 0.2, 0.35), (a + b) / 2 + V(0, 0, h - 0.1), (0, 0, ang), post_m, 0.0)
    tile_coping(mb, a, b, z0 + h + 0.05, thick, roof_m, roof_m)


def yagura(mb, loc, rng, w=3.8, h=10.5, name=None):
    """torre de vigia de vila: 4 esteios com mao-francesa, sala fechada com janela acesa, telhado de 4 aguas"""
    x, y, z = loc
    c = Vector((x, y, z))
    hw = w / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = c + V(sx * hw, sy * hw, 0)
            mb.box((0.62, 0.62, h), p + V(0, 0, h / 2), (0, 0, 0), "Wood_Dark", 0.05)
            mb.box((1.0, 1.0, 0.6), p + V(0, 0, 0.3), (0, 0, 0), "Stone_Dark", 0.08)
    for sy in (-1, 1):
        mb.beam(c + V(-hw, sy * hw, 0.8), c + V(hw, sy * hw, h * 0.62), 0.3, 0.4, "Wood_Dark", 0.0)
    for sx in (-1, 1):
        mb.beam(c + V(sx * hw, -hw, h * 0.62), c + V(sx * hw, hw, 0.8), 0.3, 0.4, "Wood_Dark", 0.0)
    zr = z + h * 0.66
    mb.box((w + 1.0, w + 1.0, 0.4), (x, y, zr), (0, 0, 0), "Wood_Plank", 0.05)
    mb.box((w + 0.2, w + 0.2, h - h * 0.66), (x, y, zr + (h - h * 0.66) / 2), (0, 0, 0), "P_Naruto_Wall", 0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.5, 0.5, h - h * 0.66 + 0.2), (x + sx * (hw + 0.1), y + sy * (hw + 0.1), zr + (h - h * 0.66) / 2),
                   (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((1.6, 0.3, 1.2), (x, y - hw - 0.12, zr + (h - h * 0.66) / 2), (0, 0, 0), "Lantern_Glow", 0.0)
    mb.box((0.25, 0.4, 1.3), (x, y - hw - 0.2, zr + (h - h * 0.66) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    for sx in (-1, 1):
        mb.box((0.25, 0.4, 1.3), (x + sx * 0.85, y - hw - 0.2, zr + (h - h * 0.66) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    from fm_parts import frustum
    frustum(mb, (x, y, z + h), w + 3.2, w + 3.2, 0.7, 0.7, 2.6, "P_Naruto_Tile")
    mb.box((w + 3.4, w + 3.4, 0.3), (x, y, z + h + 0.05), (0, 0, 0), "Wood_Dark", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = c + V(sx * (hw + 1.6), sy * (hw + 1.6), h)
            cone(mb, p, p + V(sx * 0.5, sy * 0.5, 0.7), 0.25, 0.02, "P_Naruto_Tile", 4)
    mb.ico(0.45, (x, y, z + h + 3.0), "P_Naruto_Red", 1, (1, 1, 1.4))
    if name:
        light(name, "POINT", (x, y - hw - 1.2, zr + 1.6), 120, (1.0, 0.62, 0.3), 0.4)


def bamboo(mb, loc, rng, n=5, h=(9, 14), r=0.28, m="P_Bamboo", leaf="Leaf_Pine_Light"):
    x, y, z = loc
    for i in range(n):
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(0, 1.3)
        bx, by = x + math.cos(a) * rr, y + math.sin(a) * rr
        hh = rng.uniform(*h)
        lean = V(rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0)
        top = V(bx, by, z + hh) + lean
        mb.rod((bx, by, z), top, r, m, 6)
        for k in range(2, int(hh / 2.2)):
            p = V(bx, by, z) + (top - V(bx, by, z)) * (k * 2.2 / hh)
            mb.cyl(r * 1.25, 0.18, p, (0, 0, 0), m, 6, bevel=0.0)
        for k in range(3):
            aa = rng.uniform(0, math.tau)
            p = top - V(0, 0, rng.uniform(0.5, 3.0))
            mb.ico(rng.uniform(0.9, 1.4), p + V(math.cos(aa) * 0.8, math.sin(aa) * 0.8, 0), leaf, 1, (1.4, 0.6, 0.35),
                   rot=(0, 0, aa))


# ------------------------------------------------------------------ laminas, pontas
def blade(mb, base, direction, normal, length, width, m="Metal_Blade", back_m=None, thick=0.28, curve=0.06,
          tip=0.16):
    """lamina de katana: poligono com curvatura (sori) e ponta; plano definido por direction e normal"""
    u = Vector(direction).normalized()
    nrm = Vector(normal).normalized()
    v = nrm.cross(u).normalized()
    pts = []
    k = 6
    for i in range(k + 1):
        t = i / k
        a = t * length * (1 - tip)
        bend = curve * length * t * t
        pts.append((a, -width / 2 + bend))
    pts.append((length, width * 0.1 + curve * length))
    for i in range(k, -1, -1):
        t = i / k
        a = t * length * (1 - tip)
        bend = curve * length * t * t
        pts.append((a, width / 2 + bend))
    plate(mb, pts, base, u, v, thick, m)


def katana(mb, grip, direction, normal, length=11.0, width=0.9, blade_m="Metal_Blade", grip_m="P_DS_Char",
           guard_m="Metal_Brass"):
    """katana inteira a partir do punho (grip = fim do cabo) na direcao da lamina"""
    g = Vector(grip)
    u = Vector(direction).normalized()
    hl = length * 0.24
    mb.beam(g, g + u * hl, 0.55, 0.42, grip_m, 0.0)
    q = u.to_track_quat("Z", "Y")
    M = Matrix.Translation(g + u * (hl + 0.1)) @ q.to_matrix().to_4x4()
    res = bmesh.ops.create_cone(mb.bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.95, radius2=0.95,
                                depth=0.22, matrix=M)
    mb._post(res["verts"], guard_m, None, 0, 1)
    blade(mb, g + u * (hl + 0.2), u, normal, length - hl, width, blade_m)
