# fm_parts - pecas modulares (escada, cerca, lanterna, penhasco, trilho, arvores, props)
import math, random
from mathutils import Vector, Matrix, Euler
from fm_lib import MB, D, col_box, col_ramp, col_beam, light, marker, resample, arc, path_len


def P3(p, z=0.0):
    return Vector((p[0], p[1], p[2] if len(p) > 2 else z))


def rot2(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return x * c - y * s, x * s + y * c


class Frame:
    """referencial local 2D (origem + angulo): converte coordenadas locais em mundo"""

    def __init__(self, ox, oy, oz=0.0, ang=0.0):
        self.o = Vector((ox, oy, oz))
        self.a = ang

    def p(self, x, y, z=0.0):
        rx, ry = rot2(x, y, self.a)
        return Vector((self.o.x + rx, self.o.y + ry, self.o.z + z))

    def r(self, rx=0.0, ry=0.0, rz=0.0):
        return (rx, ry, rz + self.a)


# ------------------------------------------------------------------ escada
def stairs(mb, area, base, ang, width, n, rise=1.0, tread=1.5, m="Stone_Light", side_m="Stone_Dark",
           stringers=True, col=True, landing=0.0):
    """escada que sobe na direcao 'ang' (rad) a partir de base (x,y,z do pe do 1o degrau)"""
    F = Frame(base[0], base[1], base[2], ang)
    for i in range(n):
        z0 = base[2] + rise * i
        # cada degrau e um bloco macico do chao ate o topo do degrau
        L = tread + 0.15
        mb.box((L, width, rise * (i + 1)), F.p(tread * i + tread / 2, 0, rise * (i + 1) / 2 - 0.0),
               F.r(), m, 0.14, 1)
    if stringers:
        run = tread * n
        for s in (-1, 1):
            # banzo lateral em blocos (parede baixa acompanhando a escada)
            for i in range(n):
                h = rise * (i + 1) + 1.2
                mb.box((tread + 0.05, 1.2, h), F.p(tread * i + tread / 2, s * (width / 2 + 0.6), h / 2),
                       F.r(), side_m, 0.16, 1)
    if col:
        top = F.p(tread * n, 0, rise * n)
        bot = F.p(0, 0, 0)
        col_ramp(area, bot, top, width)
        if stringers:
            for s in (-1, 1):
                a = F.p(0, s * (width / 2 + 0.6), 0)
                b = F.p(tread * n, s * (width / 2 + 0.6), 0)
                c = (a + b) / 2
                col_box(area, (tread * n, 1.2, rise * n + 1.2), (c.x, c.y, base[2] + (rise * n + 1.2) / 2),
                        F.r())
    return F.p(tread * n, 0, rise * n)


# ------------------------------------------------------------------ cerca / guarda-corpo de madeira
def fence(mb, area, pts, h=3.2, post_step=4.0, m="Wood_Dark", rail_m="Wood_Light", col=True, z=None,
          rng=None, rope=False):
    rng = rng or random.Random(7)
    pts = [P3(p) for p in pts]
    posts = resample(pts, post_step)
    for i, p in enumerate(posts):
        mb.box((0.9, 0.9, h + 0.5), (p.x, p.y, p.z + (h + 0.5) / 2), (0, 0, rng.uniform(-0.1, 0.1)), m, 0.12)
        mb.box((1.1, 1.1, 0.35), (p.x, p.y, p.z + h + 0.55), (0, 0, 0), m, 0.1)
    for a, b in zip(posts, posts[1:]):
        for hh in ((h * 0.92), (h * 0.5)):
            mb.beam(a + Vector((0, 0, hh)), b + Vector((0, 0, hh)), 0.45, 0.35, rail_m, 0.08)
        if rope:
            mid = (a + b) / 2 + Vector((0, 0, h * 0.72))
            mb.tube([a + Vector((0, 0, h * 0.8)), mid, b + Vector((0, 0, h * 0.8))], 0.12, "Rope", 5)
    if col:
        for a, b in zip(pts, pts[1:]):
            c = (a + b) / 2
            d = b - a
            col_box(area, (d.length, 0.8, h + 2.0), (c.x, c.y, c.z + (h + 2.0) / 2), (0, 0, math.atan2(d.y, d.x)))


def stone_parapet(mb, area, pts, h=2.2, w=1.6, m="Stone_Light", cap_m="Stone_Dark", col=True, rng=None):
    rng = rng or random.Random(3)
    pts = [P3(p) for p in pts]
    for a, b in zip(pts, pts[1:]):
        L = (b - a).length
        n = max(1, int(L / 2.6))
        d = (b - a) / n
        ang = math.atan2(d.y, d.x)
        for i in range(n):
            c = a + d * (i + 0.5)
            hh = h + rng.uniform(-0.15, 0.15)
            mb.box((d.length - 0.12, w, hh), (c.x, c.y, c.z + hh / 2), (0, 0, ang), m, 0.2, 1)
        if col:
            c = (a + b) / 2
            col_box(area, (L, w, h + 2), (c.x, c.y, c.z + (h + 2) / 2), (0, 0, ang))


# ------------------------------------------------------------------ lanterna em poste
def lantern(mb, loc, rot=0.0, lights=True, name=None, post=True, h=7.0, arm=True):
    x, y, z = loc
    F = Frame(x, y, z, rot)
    if post:
        mb.box((1.3, 1.3, 1.0), F.p(0, 0, 0.5), F.r(), "Stone_Dark", 0.15)
        mb.box((0.8, 0.8, h), F.p(0, 0, h / 2 + 1), F.r(), "Wood_Dark", 0.1)
    if arm:
        mb.box((2.6, 0.5, 0.5), F.p(1.1, 0, h + 0.6), F.r(), "Wood_Dark", 0.08)
        lx, lz = 2.1, h - 0.9
    else:
        lx, lz = 0, h + 1.6
    c = F.p(lx, 0, lz)
    # caixa da lanterna: base, 4 montantes, vidro emissivo, chapeu
    mb.box((1.5, 1.5, 0.3), c + Vector((0, 0, -1.0)), F.r(), "Metal_Dark", 0.05)
    mb.box((1.1, 1.1, 1.7), c, F.r(), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = F.p(lx + sx * 0.62, sy * 0.62, lz)
            mb.box((0.18, 0.18, 1.9), q, F.r(), "Metal_Dark", 0.0)
    mb.cyl(1.05, 0.7, c + Vector((0, 0, 1.2)), (0, 0, F.a + math.pi / 4), "Metal_Dark", 4, r2=0.2, bevel=0.0)
    mb.box((0.2, 0.2, 0.8), c + Vector((0, 0, 1.6)), F.r(), "Metal_Dark", 0.0)
    if lights:
        light((name or "L_Lantern") + "_Light", "POINT", c, 180, (1.0, 0.62, 0.28), 0.4)
    return c


def hanging_lantern(mb, loc, lights=True, name=None, chain=2.0):
    x, y, z = loc
    c = Vector((x, y, z - chain - 1.0))
    mb.rod((x, y, z), (x, y, z - chain), 0.08, "Metal_Dark", 4)
    mb.box((1.3, 1.3, 0.25), c + Vector((0, 0, -0.95)), (0, 0, 0), "Metal_Dark", 0.04)
    mb.box((0.95, 0.95, 1.5), c, (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.16, 0.16, 1.7), c + Vector((sx * 0.55, sy * 0.55, 0)), (0, 0, 0), "Metal_Dark", 0.0)
    mb.cyl(0.95, 0.6, c + Vector((0, 0, 1.05)), (0, 0, math.pi / 4), "Metal_Dark", 4, r2=0.2, bevel=0.0)
    if lights:
        light((name or "L_Hang") + "_Light", "POINT", c, 120, (1.0, 0.62, 0.28), 0.3)


# ------------------------------------------------------------------ bandeira / estandarte
def emblem_pickaxe(mb, c, F_ang, s=1.0, m="Emblem_Cream", normal_off=0.0):
    """picareta estilizada (cabo diagonal + cabeca curva) em relevo sobre plano vertical (face -Y local)"""
    F = Frame(c.x, c.y, c.z, F_ang)
    y = -0.2 - normal_off
    mb.beam(F.p(-1.4 * s, y, -1.7 * s), F.p(1.0 * s, y, 1.4 * s), 0.25, 0.42 * s, m, 0.0)
    pts = []
    for i in range(7):
        t = -1 + 2 * i / 6
        # cabeca perpendicular ao cabo, curvada para baixo nas pontas
        px = 1.0 * s + t * 1.35 * s
        pz = 1.4 * s - t * 1.05 * s - abs(t) ** 1.7 * 0.8 * s + 0.35 * s
        pts.append(F.p(px, y, pz))
    for p0, p1 in zip(pts, pts[1:]):
        mb.beam(p0, p1, 0.25, 0.55 * s, m, 0.0)


def emblem_hammers(mb, c, F_ang, s=1.0, m="Emblem_Cream", off=0.0):
    """dois martelos cruzados (identidade da forja), face -Y local"""
    F = Frame(c.x, c.y, c.z, F_ang)
    for sgn in (-1, 1):
        a = F.p(-sgn * 1.7 * s, -off, -1.9 * s)
        b = F.p(sgn * 1.4 * s, -off, 1.6 * s)
        mb.beam(a, b, 0.3, 0.45 * s, m, 0.0)
        axis = (b - a).normalized()
        nrm = Vector((math.sin(F_ang), -math.cos(F_ang), 0))  # normal da face
        perp = axis.cross(nrm).normalized()
        hd = b + axis * 0.2 * s
        mb.beam(hd - perp * 1.2 * s, hd + perp * 1.2 * s, 0.4, 1.1 * s, m, 0.05)


def banner(mb, loc, ang, w=3.2, h=6.5, cloth="Cloth_Navy", trim="Metal_Brass", emblem="pickaxe"):
    """estandarte pendurado numa trave (loc = centro da trave); face voltada para -Y local"""
    x, y, z = loc
    F = Frame(x, y, 0.0, ang)
    top = z
    mb.beam(F.p(-w / 2 - 0.5, 0, top), F.p(w / 2 + 0.5, 0, top), 0.35, 0.35, "Wood_Dark", 0.05)
    for s in (-1, 1):
        mb.box((0.45, 0.45, 0.45), F.p(s * (w / 2 + 0.6), 0, top), F.r(), trim, 0.05)
    hw = w / 2
    pts = [(-hw, 0), (hw, 0), (hw, -h), (0, -h - 1.1), (-hw, -h)]
    th = 0.18
    vf = [mb.bm.verts.new(F.p(px, -th / 2, top + pz)) for px, pz in pts]
    vb = [mb.bm.verts.new(F.p(px, th / 2, top + pz)) for px, pz in pts]
    mb.bm.faces.new(list(reversed(vf)))
    mb.bm.faces.new(vb)
    for i in range(5):
        j = (i + 1) % 5
        mb.bm.faces.new((vf[i], vf[j], vb[j], vb[i]))
    mb._post(vf + vb, cloth, None, 0, 1)
    mb.box((w, 0.3, 0.35), F.p(0, 0, top - 0.3), F.r(), trim, 0.03)
    for s in (-1, 1):
        mb.box((0.25, 0.26, h - 0.4), F.p(s * (hw - 0.12), 0, top - h / 2 - 0.2), F.r(), trim, 0.0)
    c = F.p(0, 0, top - h * 0.52)
    if emblem == "pickaxe":
        emblem_pickaxe(mb, c, ang, s=w / 5.2, normal_off=0.02)
    elif emblem == "hammers":
        emblem_hammers(mb, c, ang, s=w / 5.4, off=0.15)

# ------------------------------------------------------------------ props
def crate(mb, loc, s=2.2, rot=0.0, rng=None):
    rng = rng or random.Random(1)
    x, y, z = loc
    F = Frame(x, y, z, rot)
    mb.box((s, s, s), F.p(0, 0, s / 2), F.r(), "Wood_Plank", 0.1)
    for dz in (0.12, s - 0.12):
        for sy in (-1, 1):
            mb.box((s + 0.12, 0.22, 0.28), F.p(0, sy * s / 2, dz), F.r(), "Wood_Dark", 0.03)
        for sx in (-1, 1):
            mb.box((0.22, s + 0.12, 0.28), F.p(sx * s / 2, 0, dz), F.r(), "Wood_Dark", 0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.3, 0.3, s + 0.1), F.p(sx * s / 2, sy * s / 2, s / 2), F.r(), "Wood_Dark", 0.03)


def barrel(mb, loc, r=1.1, h=2.6, rot=0.0):
    x, y, z = loc
    mb.cyl(r, h * 0.5, (x, y, z + h * 0.25), (0, 0, rot), "Wood_Plank", 10, r2=r * 1.12, bevel=0.0)
    mb.cyl(r * 1.12, h * 0.5, (x, y, z + h * 0.75), (0, 0, rot), "Wood_Plank", 10, r2=r, bevel=0.0)
    for zz in (0.2, h * 0.5, h - 0.2):
        rr = r * (1.13 if abs(zz - h * 0.5) < 0.1 else 1.03)
        mb.cyl(rr + 0.05, 0.22, (x, y, z + zz), (0, 0, rot), "Metal_Dark", 10, bevel=0.0)


def crystal_cluster(mb, loc, s=1.0, m="Crystal_Blue", rng=None, n=5):
    rng = rng or random.Random(5)
    x, y, z = loc
    for i in range(n):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 0.8) * s if i else 0
        h = rng.uniform(1.6, 3.2) * s * (1.3 if i == 0 else 1.0)
        tilt = rng.uniform(0.1, 0.5) if i else rng.uniform(0, 0.12)
        px, py = x + math.cos(a) * r, y + math.sin(a) * r
        rot = (math.sin(a) * tilt, -math.cos(a) * tilt * -1, rng.uniform(0, 6))
        base_r = 0.45 * s * rng.uniform(0.8, 1.2)
        mb.cyl(base_r, h * 0.75, Vector((px, py, z + h * 0.375)) , rot, m, 6, r2=base_r * 0.9, bevel=0.0)
        tip = Matrix.Rotation(rot[0], 3, "X") @ Matrix.Rotation(rot[1], 3, "Y") @ Vector((0, 0, h * 0.75 + h * 0.14))
        mb.cyl(base_r * 0.9, h * 0.28, Vector((px, py, z)) + tip, rot, m, 6, r2=0.02, bevel=0.0)


def mine_cart(mb, loc, ang, load="Crystal_Blue", rng=None):
    rng = rng or random.Random(11)
    x, y, z = loc
    F = Frame(x, y, z, ang)
    # chassi + cacamba trapezoidal
    mb.box((3.4, 2.2, 0.35), F.p(0, 0, 1.1), F.r(), "Metal_Dark", 0.05)
    mb.cyl(1.8, 1.7, F.p(0, 0, 2.2), F.r(0, 0, math.pi / 4), "Metal_Iron", 4, r2=2.25, bevel=0.06)
    mb.cyl(1.72, 1.4, F.p(0, 0, 2.45), F.r(0, 0, math.pi / 4), "Wood_Plank", 4, r2=2.15, bevel=0.0)
    for sx in (-1, 1):
        mb.box((0.25, 2.9, 0.3), F.p(sx * 1.5, 0, 3.0), F.r(), "Metal_Dark", 0.03)
        for sy in (-1, 1):
            mb.cyl(0.62, 0.3, F.p(sx * 1.1, sy * 1.25, 0.7), F.r(D(90), 0, 0), "Metal_Dark", 10, bevel=0.0)
            mb.cyl(0.25, 0.36, F.p(sx * 1.1, sy * 1.25, 0.7), F.r(D(90), 0, 0), "Metal_Iron", 6, bevel=0.0)
    if load:
        crystal_cluster(mb, F.p(0, 0, 2.9), 0.75, load, rng, 6)


def rails(mb, pts, gauge=2.6, sleeper_step=1.7, z_off=0.0):
    """trilho: dormentes + 2 barras varridas; pts ja na cota do chao"""
    pts = [P3(p) + Vector((0, 0, z_off)) for p in pts]
    fine = resample(pts, 0.8)
    sl = resample(pts, sleeper_step)
    rng = random.Random(len(sl))
    for i, p in enumerate(sl):
        j = min(i + 1, len(sl) - 1)
        k = max(i - 1, 0)
        t = (sl[j] - sl[k])
        a = math.atan2(t.y, t.x)
        mb.box((0.8, gauge + 1.6, 0.3), (p.x, p.y, p.z + 0.15), (0, 0, a + rng.uniform(-0.05, 0.05)), "Wood_Dark", 0.06)
    prof = [(-0.18, 0.3), (0.18, 0.3), (0.18, 0.62), (-0.18, 0.62)]
    for s in (-1, 1):
        off = []
        for i, p in enumerate(fine):
            j = min(i + 1, len(fine) - 1)
            k = max(i - 1, 0)
            t = (fine[j] - fine[k]).normalized()
            side = Vector((-t.y, t.x, 0)).normalized()
            off.append(p + side * s * gauge / 2)
        mb.sweep(off, prof, "Metal_Iron", True)


# ------------------------------------------------------------------ vegetacao
def pine(mb, loc, h=16.0, rng=None, light_ratio=0.35):
    rng = rng or random.Random(2)
    x, y, z = loc
    tr = h * 0.055
    mb.cyl(tr, h * 0.3, (x, y, z + h * 0.15), (0, 0, 0), "Bark", 6, r2=tr * 0.7, bevel=0.0)
    tiers = 4 if h > 10 else 3
    for i in range(tiers):
        f = i / tiers
        zc = z + h * (0.22 + 0.62 * f)
        r = h * 0.3 * (1 - f * 0.65)
        th = h * (0.34 - 0.04 * i)
        m = "Leaf_Pine_Light" if (i == tiers - 1 or rng.random() < light_ratio * 0.5) else "Leaf_Pine"
        mb.cyl(r, th, (x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), zc + th / 2),
               (rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), rng.uniform(0, 6)), m, 7, r2=r * 0.12, bevel=0.0)


def bush(mb, loc, s=2.0, rng=None, m="Leaf_Pine_Light"):
    rng = rng or random.Random(3)
    x, y, z = loc
    for i in range(3):
        mb.ico(s * rng.uniform(0.55, 0.85), (x + rng.uniform(-s, s) * 0.6, y + rng.uniform(-s, s) * 0.6, z + s * 0.35),
               m if rng.random() > 0.3 else "Grass", 1, (1, 1, 0.7), jitter=0.25)


def sakura(mb, loc, h=12.0, rng=None):
    rng = rng or random.Random(4)
    x, y, z = loc
    mb.cyl(h * 0.06, h * 0.5, (x, y, z + h * 0.25), (rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), 0), "Bark", 6,
           r2=h * 0.035, bevel=0.0)
    for i in range(5):
        a = rng.uniform(0, math.tau)
        r = h * rng.uniform(0.08, 0.28)
        mb.ico(h * rng.uniform(0.18, 0.26), (x + math.cos(a) * r, y + math.sin(a) * r, z + h * rng.uniform(0.6, 0.85)),
               "Leaf_Sakura", 1, (1, 1, 0.75), jitter=0.3)


def palm(mb, loc, h=12.0, rng=None, lean=0.25):
    rng = rng or random.Random(6)
    x, y, z = loc
    a = rng.uniform(0, math.tau)
    pts = []
    for i in range(7):
        t = i / 6
        pts.append(Vector((x + math.cos(a) * lean * h * t * t, y + math.sin(a) * lean * h * t * t, z + h * t)))
    for p0, p1 in zip(pts, pts[1:]):
        mb.cyl(0.55, (p1 - p0).length * 1.05, (p0 + p1) / 2, (0, 0, 0), "Bark", 6, r2=0.45, bevel=0.0)
    top = pts[-1]
    for k in range(7):
        b = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        leaf = [top, top + Vector((math.cos(b) * 3, math.sin(b) * 3, 0.9)),
                top + Vector((math.cos(b) * 5.5, math.sin(b) * 5.5, -0.8))]
        mb.sweep(leaf, [(-1.1, 0), (0, 0.25), (1.1, 0), (0, -0.05)], "Leaf_Palm", True)


# ------------------------------------------------------------------ penhascos (colunas em estratos)
def cliff_band(mb, pts, z_base, z_top, rng, depth=2.0, rmin=3.5, rmax=6.5, step=6.0, grass=True,
               var=3.0, face_side=1, m="Cliff_Rock", m2="Cliff_Rock_Dark", top_fn=None, strata=True):
    """faixa de penhasco ao longo da polilinha; colunas de rocha empilhadas em estratos.
    face_side: lado (esquerda=+1) para onde a face aponta, colunas ficam para o outro lado."""
    pts = [P3(p) for p in pts]
    ctrs = resample(pts, step)
    for i, c in enumerate(ctrs):
        j = min(i + 1, len(ctrs) - 1)
        k = max(i - 1, 0)
        t = (ctrs[j] - ctrs[k])
        if t.length < 1e-6:
            continue
        t.normalize()
        left = Vector((-t.y, t.x, 0))
        off = -face_side * rng.uniform(0.3, depth)
        cc = c + left * off
        r = rng.uniform(rmin, rmax)
        top = (top_fn(cc) if top_fn else z_top) + rng.uniform(-var, var * 0.4)
        nsides = rng.choice((5, 6, 6, 7))
        base_poly = []
        a0 = rng.uniform(0, math.tau)
        for s in range(nsides):
            a = a0 + s * math.tau / nsides + rng.uniform(-0.2, 0.2)
            rr = r * rng.uniform(0.75, 1.1)
            base_poly.append((math.cos(a) * rr, math.sin(a) * rr))
        # coluna facetada esculpida (aneis com jitter por vertice, topo inclinado) + eventual degrau de estrato
        hgt = top - z_base
        mm = m if rng.random() > 0.3 else m2
        if strata and hgt > 16 and rng.random() < 0.55:
            zsplit = z_base + hgt * rng.uniform(0.45, 0.7)
            rock_column(mb, cc, base_poly, z_base - 0.2, zsplit, rng, mm, taper=0.94)
            sc = rng.uniform(0.72, 0.86)
            off = Vector((rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), 0))
            poly2 = [(px * sc, py * sc) for px, py in base_poly]
            # patamar de grama no degrau
            if grass:
                mb.prism([(cc.x + px * 0.97, cc.y + py * 0.97) for px, py in base_poly], zsplit - 0.4, zsplit + 0.35,
                         "Grass", bevel=0.2)
            rock_column(mb, cc + off, poly2, zsplit - 0.3, top, rng, m2 if mm == m else m, taper=0.86)
            cap_poly = [(cc.x + off.x + px * 0.8, cc.y + off.y + py * 0.8) for px, py in poly2]
        else:
            rock_column(mb, cc, base_poly, z_base - 0.2, top, rng, mm, taper=0.84)
            cap_poly = [(cc.x + px * 0.8, cc.y + py * 0.8) for px, py in base_poly]
        if grass:
            mb.prism(cap_poly, top - 0.6, top + 0.55, "Grass", bevel=0.25)
    return


def rock_scatter(mb, center, radius, n, rng, smin=1.2, smax=3.2, z=0.0, m="Cliff_Rock"):
    for i in range(n):
        a = rng.uniform(0, math.tau)
        r = radius * math.sqrt(rng.random())
        s = rng.uniform(smin, smax)
        mb.rock((center[0] + math.cos(a) * r, center[1] + math.sin(a) * r, z + s * 0.25),
                (s * rng.uniform(1.0, 1.5), s * rng.uniform(0.9, 1.3), s * rng.uniform(0.6, 1.0)),
                m, 1, (0, 0, rng.uniform(0, 6)))


# ------------------------------------------------------------------ pavimento
def pave_poly(mb, poly, z, rng, tile=2.6, gap=0.22, h=0.35, m="Stone_Paving", grout=True, jitter=0.06,
              grout_m="Stone_Grout", bevel=0.1):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    from fm_lib import point_in_poly
    if grout:
        mb.prism(poly, z - 0.4, z + h * 0.35, grout_m, 0.0)
    y = min(ys) + tile / 2
    row = 0
    while y < max(ys):
        x = min(xs) + tile / 2 + (tile / 2 if row % 2 else 0)
        while x < max(xs):
            if point_in_poly(x, y, poly):
                w = tile - gap + rng.uniform(-0.1, 0.1)
                hh = h + rng.uniform(-jitter, jitter)
                mb.box((w * rng.choice((1.0, 1.0, 1.9 if False else 1.0)), tile - gap, hh), (x, y, z + hh / 2),
                       (0, 0, rng.uniform(-0.03, 0.03)), m, bevel, 1)
            x += tile
        y += tile
        row += 1


def pave_ring(mb, cx, cy, r0, r1, z, rng, a0=0.0, a1=360.0, ring_w=2.6, gap=0.22, h=0.35, m="Stone_Paving"):
    """pavimento radial (aneis concentricos de pedras em arco)"""
    r = r0
    while r < r1 - 0.3:
        rr = min(r + ring_w, r1)
        circ = D(a1 - a0) * (r + rr) / 2
        n = max(3, int(circ / 2.8))
        da = (a1 - a0) / n
        for i in range(n):
            aa = a0 + da * i + (da * 0.5 if int(r / ring_w) % 2 else 0)
            ab = aa + da
            if ab > a1 + 1e-6 and a1 - a0 < 359:
                continue
            g = gap / max(r, 1.0)
            pts = []
            seg = 2
            for k in range(seg + 1):
                t = D(aa) + g + (D(ab) - D(aa) - 2 * g) * k / seg
                pts.append((cx + math.cos(t) * (rr - gap / 2), cy + math.sin(t) * (rr - gap / 2)))
            for k in range(seg, -1, -1):
                t = D(aa) + g + (D(ab) - D(aa) - 2 * g) * k / seg
                pts.append((cx + math.cos(t) * (r + gap / 2), cy + math.sin(t) * (r + gap / 2)))
            hh = h + rng.uniform(-0.05, 0.05)
            mb.prism(pts, z, z + hh, m, bevel=0.09, seg=1)
        r = rr


def _lrng(*key):
    """rng local deterministico a partir da geometria: variacoes novas nao consomem a sequencia compartilhada
    (a forja e os outros modulos continuam com os mesmos sorteios)"""
    return random.Random(hash(tuple(round(float(k), 2) for k in key)) & 0x7fffffff)


# ------------------------------------------------------------------ parede de alvenaria em blocos
def masonry_wall(mb, a, b, z0, z1, thick, rng, m="Stone_Light", m2="Stone_Dark", course=1.6, mix=0.2,
                 openings=(), blk=(1.8, 3.4)):
    """parede de blocos entre a e b; openings = [(s0, s1, zlo, zhi)] em distancia ao longo de a->b.
    Blocos com leve giro/inclinacao (assentamento a mao) - sem consumir o rng compartilhado.
    blk = faixa de comprimento dos blocos (blocos maiores = menos triangulos, leitura mais robusta)."""
    a, b = P3(a), P3(b)
    L = (b - a).length
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    z = z0
    row = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        s = -rng.uniform(0, 1.2) if row % 2 else 0.0
        while s < L - 0.05:
            w = rng.uniform(*blk)
            sa, sb = max(s, 0.0), min(s + w, L)
            # recorta aberturas
            blocked = False
            for op in openings:
                o0, o1, zl, zh = op[:4]
                rise = op[4] if len(op) > 4 else 0.0
                if rise > 0 and z + h > zh - rise:
                    # linha dentro da zona do arco: abertura estreita conforme o arco (elipse)
                    zm = z + h * 0.5
                    t = min(1.0, max(0.0, (zm - (zh - rise)) / rise))
                    hw = (o1 - o0) / 2 * math.sqrt(max(0.0, 1 - t * t))
                    cmid = (o0 + o1) / 2
                    o0, o1 = cmid - hw, cmid + hw
                    if hw < 0.2:
                        continue
                if z + h > zl + 0.01 and z < zh - 0.01 and sb > o0 and sa < o1:
                    # divide o bloco nas bordas da abertura
                    if sa < o0:
                        _block(mb, a, d, ang, sa, o0, z, h, thick, rng, m, m2, mix)
                    if sb > o1:
                        _block(mb, a, d, ang, o1, sb, z, h, thick, rng, m, m2, mix)
                    blocked = True
                    break
            if not blocked:
                _block(mb, a, d, ang, sa, sb, z, h, thick, rng, m, m2, mix)
            s += w
        z += h
        row += 1


def _block(mb, a, d, ang, sa, sb, z, h, thick, rng, m, m2, mix):
    if sb - sa < 0.15:
        return
    c = a + d * ((sa + sb) / 2)
    mm = m2 if rng.random() < mix else m
    out = rng.uniform(-0.08, 0.12)
    lr = _lrng(c.x, c.y, z)
    # giro/rolagem pequenos + altura levemente irregular: a parede deixa de parecer grade perfeita
    L_ = sb - sa
    yaw = lr.uniform(-0.018, 0.018) if L_ > 0.8 else 0.0
    roll = lr.uniform(-0.012, 0.012) if L_ > 0.8 else 0.0
    dh = lr.uniform(-0.05, 0.03)
    mb.box((L_ - 0.1, thick + out, h - 0.1 + dh), (c.x, c.y, z + h / 2 + dh / 2), (roll, 0, ang + yaw), mm, 0.14, 1)


# ------------------------------------------------------------------ arco de aduelas
def arch(mb, a_center, ang, width, z_spring, rise, depth, m="Stone_Light", key_m="Stone_Light", n=9, band=1.3,
         keystone=True):
    """arco (semi-elipse) de aduelas no plano vertical; a_center = centro da abertura no chao; ang = direcao da parede"""
    c = Vector(a_center)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    hw = width / 2
    pts = []
    for i in range(n + 1):
        t = math.pi * i / n
        pts.append((math.cos(t) * (hw + band / 2), math.sin(t) * (rise + band / 2)))
    lr = _lrng(c.x, c.y, z_spring, width)
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[i + 1]
        mid = c + d * ((x0 + x1) / 2) + Vector((0, 0, z_spring + (z0 + z1) / 2))
        L = math.hypot(x1 - x0, z1 - z0) + 0.05
        tilt = math.atan2(z1 - z0, x1 - x0)
        key = keystone and i == n // 2
        mm = key_m if key else m
        sc = 1.25 if key else lr.uniform(0.94, 1.1)
        # aduelas com profundidade e altura irregulares; a chave salta para fora
        dep = depth * (1.14 if key else lr.uniform(0.98, 1.07))
        mb.box((L - 0.12, dep, band * sc), mid + Vector((0, 0, band * (sc - 1) * 0.3)),
               (0, -tilt + lr.uniform(-0.025, 0.025), ang), mm, 0.12)
    # impostas
    for s in (-1, 1):
        p = c + d * (s * (hw + band / 2)) + Vector((0, 0, z_spring - 0.3))
        mb.box((band + 0.4, depth + 0.3, 0.6), p, (0, 0, ang), m, 0.1)


# ------------------------------------------------------------------ parede enxaimel (madeira + reboco)
def timber_wall(mb, a, b, z0, z1, thick, rng, openings=(), post=3.6, m_t="Wood_Dark", m_p="Plaster",
                braces=True, out_side=1, wobble=0.025, inner=None, brace_bevel=0.06, cut_plates=False):
    """painel de reboco com estrutura de madeira aparente (dos dois lados); openings = [(s0,s1,zlo,zhi)].
    wobble = inclinacao maxima (rad) dos montantes livres; escoras e secoes levemente irregulares (feito a mao).
    inner = lado interno (-1/+1, normal esquerda de a->b): la as pecas saem sem chanfro (economia de triangulos).
    As variacoes usam rng local: nao mudam os sorteios compartilhados de quem chama."""
    a, b = P3(a), P3(b)
    L_ = (b - a).length
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    nrm = Vector((-d.y, d.x, 0))
    lr = _lrng(a.x, a.y, b.x, b.y, z0)
    # reboco (recortado nas aberturas)
    cuts = sorted(openings)
    segs = []
    cur = 0.0
    for o in cuts:
        if o[0] > cur:
            segs.append((cur, o[0], z0, z1))
        segs.append((o[0], o[1], z0, o[2]))
        segs.append((o[0], o[1], o[3], z1))
        cur = o[1]
    if cur < L_:
        segs.append((cur, L_, z0, z1))
    for s0, s1, za, zb in segs:
        if s1 - s0 < 0.05 or zb - za < 0.05:
            continue
        c = a + d * ((s0 + s1) / 2)
        mb.box((s1 - s0, thick, zb - za), (c.x, c.y, (za + zb) / 2), (0, 0, ang), m_p, 0.0)
    tw = 0.7
    fo = thick / 2 + 0.12
    n = max(1, int(round(L_ / post)))
    # sorteios locais compartilhados pelos dois lados (a estrutura atravessa a parede)
    xs = [L_ * i / n for i in range(n + 1)]
    for o in cuts:
        xs += [o[0] - 0.35, o[1] + 0.35]
    xs = sorted(set(round(x, 2) for x in xs if -0.01 <= x <= L_ + 0.01))
    lean = {}
    for x in xs:
        free = 0.9 < x < L_ - 0.9 and not any(o[0] - 1.0 < x < o[1] + 1.0 for o in cuts)
        lean[x] = (lr.uniform(-wobble, wobble) * (z1 - z0) if free else 0.0, lr.uniform(0.44, 0.58))
    br_j = [(lr.uniform(-0.25, 0.25), lr.uniform(-0.25, 0.25), lr.uniform(0.36, 0.46)) for i in range(n)]
    plate_j = (lr.uniform(0.6, 0.72), lr.uniform(0.7, 0.86))
    for side in (-1, 1):
        off = nrm * side * fo
        bf = 0.0 if side == inner else 1.0
        # soleira e frechal (frechal mais robusto); cut_plates: a soleira nao atravessa vaos que nascem no pe da parede
        spans = [(0.0, L_)]
        if cut_plates:
            for o in cuts:
                if o[2] <= z0 + 0.8:
                    spans = [(s0, min(s1, o[0])) for (s0, s1) in spans if min(s1, o[0]) - s0 > 0.2] + \
                            [(max(s0, o[1]), s1) for (s0, s1) in spans if s1 - max(s0, o[1]) > 0.2]
        for s0, s1 in spans:
            mb.beam(a + d * s0 + off + Vector((0, 0, z0 + 0.35)), a + d * s1 + off + Vector((0, 0, z0 + 0.35)), 0.5,
                    plate_j[0], m_t, 0.08 * bf)
        mb.beam(a + off + Vector((0, 0, z1 - 0.38)), b + off + Vector((0, 0, z1 - 0.38)), 0.5, plate_j[1], m_t, 0.08 * bf)
        for x in xs:
            p = a + d * min(max(x, 0.3), L_ - 0.3) + off
            if any(o[0] + 0.3 < x < o[1] - 0.3 for o in cuts):
                continue
            lx, pw = lean[x]
            mb.beam(p + Vector((0, 0, z0)) - d * (lx / 2), p + Vector((0, 0, z1)) + d * (lx / 2), pw, tw, m_t,
                    0.08 * bf)
        if braces:
            for i in range(n):
                x0_, x1_ = L_ * i / n, L_ * (i + 1) / n
                if any(o[0] - 0.5 < x1_ and o[1] + 0.5 > x0_ for o in cuts):
                    continue
                ja, jb_, bw = br_j[i]
                x0j = min(max(x0_ + ja * 0.5, 0.25), L_ - 0.25)
                x1j = min(max(x1_ + jb_ * 0.5, 0.25), L_ - 0.25)
                if i % 2 == 0:
                    pa, pb = a + d * x0j + off + Vector((0, 0, z0 + 0.4)), a + d * x1j + off + Vector((0, 0, z1 - 0.4))
                else:
                    pa, pb = a + d * x0j + off + Vector((0, 0, z1 - 0.4)), a + d * x1j + off + Vector((0, 0, z0 + 0.4))
                mb.beam(pa, pb, bw, 0.55, m_t, brace_bevel * bf)
        # vergas/ombreiras das aberturas
        for o in cuts:
            for x in (o[0], o[1]):
                p = a + d * x + off
                mb.beam(p + Vector((0, 0, o[2])), p + Vector((0, 0, o[3])), 0.55, 0.75, m_t, 0.08 * bf)
            pa = a + d * (o[0] - 0.4) + off
            pb = a + d * (o[1] + 0.4) + off
            for zz in (o[2], o[3]):
                if cut_plates and zz == o[2] and o[2] <= z0 + 0.8:
                    continue   # vao de porta: sem travessa embaixo
                mb.beam(pa + Vector((0, 0, zz)), pb + Vector((0, 0, zz)), 0.55, 0.75, m_t, 0.08 * bf)


def window_glow(mb, a, b, s0, s1, zlo, zhi, thick, m="Lantern_Glow", bars=True, sill=False, sill_m="Wood_Dark",
                panes=None):
    """vidraca iluminada dentro de uma abertura (com caixilho em cruz).
    sill=True: peitoril saliente dos dois lados (profundidade na fachada). panes = n de montantes (None = cruz)."""
    a, b = P3(a), P3(b)
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    c = a + d * ((s0 + s1) / 2)
    mb.box((s1 - s0, thick * 0.3, zhi - zlo), (c.x, c.y, (zlo + zhi) / 2), (0, 0, ang), m, 0.0)
    if bars:
        mb.box((s1 - s0, thick * 0.5, 0.25), (c.x, c.y, (zlo + zhi) / 2), (0, 0, ang), "Wood_Dark", 0.0)
        k = panes or 1
        for i in range(k):
            f = (i + 1) / (k + 1)
            q = a + d * (s0 + (s1 - s0) * f)
            mb.box((0.25, thick * 0.5, zhi - zlo), (q.x, q.y, (zlo + zhi) / 2), (0, 0, ang), "Wood_Dark", 0.0)
    if sill:
        mb.box((s1 - s0 + 0.9, thick + 0.9, 0.38), (c.x, c.y, zlo - 0.12), (0, 0, ang), sill_m, 0.08)

def frustum(mb, c0, w0, d0, w1, d1, h, m, top_off=(0.0, 0.0), ang=0.0, tint=None):
    """tronco de piramide retangular (coifas, bases, telhados de torre); c0 = centro da base"""
    c0 = P3(c0)
    ca, sa = math.cos(ang), math.sin(ang)

    def P(x, y, z):
        return Vector((c0.x + x * ca - y * sa, c0.y + x * sa + y * ca, c0.z + z))
    ox, oy = top_off
    b = [P(-w0 / 2, -d0 / 2, 0), P(w0 / 2, -d0 / 2, 0), P(w0 / 2, d0 / 2, 0), P(-w0 / 2, d0 / 2, 0)]
    t = [P(ox - w1 / 2, oy - d1 / 2, h), P(ox + w1 / 2, oy - d1 / 2, h), P(ox + w1 / 2, oy + d1 / 2, h),
         P(ox - w1 / 2, oy + d1 / 2, h)]
    vb = [mb.bm.verts.new(p) for p in b]
    vt = [mb.bm.verts.new(p) for p in t]
    mb.bm.faces.new(list(reversed(vb)))
    mb.bm.faces.new(vt)
    for i in range(4):
        j = (i + 1) % 4
        mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m, tint, 0.12, 1)

def rock_column(mb, cc, poly, z0, z1, rng, m, taper=0.85, rings=3, jitter=0.13, tilt=0.12):
    """prisma de rocha facetado: aneis com jitter radial por vertice (faces irregulares), topo inclinado"""
    n = len(poly)
    h = z1 - z0
    ring_vs = []
    tx, ty = rng.uniform(-tilt, tilt), rng.uniform(-tilt, tilt)
    for k in range(rings + 1):
        f = k / rings
        zc = z0 + h * f + (rng.uniform(-0.12, 0.12) * h / rings if 0 < k < rings else 0.0)
        sc = 1.0 + (taper - 1.0) * (f ** 1.3) + (0.06 if k == 1 else 0.0)
        ring = []
        for (px, py) in poly:
            j = 1.0 + rng.uniform(-jitter, jitter) * (0.4 if k == 0 else 1.0)
            x = cc.x + px * sc * j
            y = cc.y + py * sc * j
            z = zc + ((px * tx + py * ty) if k == rings else 0.0)
            ring.append(mb.bm.verts.new((x, y, z)))
        ring_vs.append(ring)
    mb.bm.faces.new(list(reversed(ring_vs[0])))
    mb.bm.faces.new(ring_vs[-1])
    for r0, r1 in zip(ring_vs, ring_vs[1:]):
        for i in range(n):
            j = (i + 1) % n
            mb.bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    allv = [v for r in ring_vs for v in r]
    mb._post(allv, m, None, 0, 1)


def peak(mb, x, y, r, h, rng, z0=10.0, m="Cliff_Rock", m2="Cliff_Rock_Dark"):
    """montanha de fundo: tronco facetado afunilando ate um cume com 2-3 ombros"""
    k = rng.choice((6, 7, 8))
    a0 = rng.uniform(0, 6)
    poly = [(math.cos(a0 + i * math.tau / k) * r * rng.uniform(0.8, 1.15),
             math.sin(a0 + i * math.tau / k) * r * rng.uniform(0.8, 1.15)) for i in range(k)]
    cc = Vector((x, y, 0))
    rock_column(mb, cc, poly, z0, z0 + h * 0.45, rng, m2, taper=0.78, rings=2, jitter=0.1, tilt=0.05)
    p2 = [(px * 0.74, py * 0.74) for px, py in poly]
    off = Vector((rng.uniform(-r, r) * 0.12, rng.uniform(-r, r) * 0.12, 0))
    rock_column(mb, cc + off, p2, z0 + h * 0.43, z0 + h * 0.78, rng, m, taper=0.62, rings=2, jitter=0.12, tilt=0.06)
    p3 = [(px * 0.44, py * 0.44) for px, py in poly]
    off2 = off + Vector((rng.uniform(-r, r) * 0.08, rng.uniform(-r, r) * 0.08, 0))
    rock_column(mb, cc + off2, p3, z0 + h * 0.76, z0 + h, rng, m2, taper=0.18, rings=2, jitter=0.15, tilt=0.0)
    # ombro com grama (pinheiros entram por raycast)
    gp = [(cc.x + off.x + px * 0.8, cc.y + off.y + py * 0.8) for px, py in p2]
    mb.prism(gp, z0 + h * 0.43 - 0.5, z0 + h * 0.45 + 0.4, "Grass_Dark", bevel=0.3)

def plank_floor(mb, F, w, d, z, rng, m="Wood_Plank", pw=1.1, gap=0.08, h=0.3, m_alt=("Wood_Light", "Wood_Dark"),
                alt=0.22):
    """assoalho de tabuas corridas (local: x em [-w/2,w/2], y em [-d/2,d/2]); tabuas ao longo de x.
    ~alt das tabuas em madeira clara/escura e alturas levemente desiguais: a variacao aparece no Roblox
    (o 'tint' do shader do Blender nao e exportado)."""
    mb.box((w, d, 0.2), F.p(0, 0, z - 0.1), F.r(), "Wood_Dark", 0.0)
    n = max(1, int(d / pw))
    step = d / n
    lr = _lrng(F.o.x, F.o.y, z, w)
    for i in range(n):
        y = -d / 2 + step * (i + 0.5)
        x = -w / 2
        while x < w / 2 - 0.05:
            L = min(rng.uniform(3.0, 6.0), w / 2 - x)
            r = lr.random()
            mm = m if r > alt else (m_alt[0] if r < alt * 0.65 else m_alt[1])
            hh = h + lr.uniform(-0.04, 0.03)
            mb.box((L - gap, step - gap, hh), F.p(x + L / 2, y, z + hh / 2 - 0.02), F.r(0, 0, lr.uniform(-0.006, 0.006)),
                   mm, 0.0, tint=rng.uniform(-1, 1))
            x += L