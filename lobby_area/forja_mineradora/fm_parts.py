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
        # rampa pelo MEIO de cada piso (z = rise*(i+1) no centro do degrau i): o pe fica entre -rise/2 e +rise/2
        # do degrau visual (antes a rampa passava pelos bordos de baixo e afundava ate -0.94)
        bot = F.p(-tread / 2, 0, 0)
        top = F.p(tread * n - tread / 2, 0, rise * n)
        col_ramp(area, bot, top, width)
        # meia pisada final plana (a rampa termina no meio do ultimo degrau; sem isto sobrava um vao ate o patamar)
        q = F.p(tread * n - tread / 4 + 0.15, 0, rise * n - 0.5)
        col_box(area, (tread / 2 + 0.3, width, 1.0), (q.x, q.y, q.z), F.r())
        if stringers:
            # banzo: rampa PARALELA a do piso (mesma rotacao e inclinacao), topo H acima dela = guarda-corpo
            # invisivel. Antes era uma caixa plana na cota do topo da escada, que virava passarela no ar sobre o pe
            # da escada. As pontas sao recuadas para a face inclinada da caixa nao sair do vao da escada:
            # embaixo a face cruza o chao em x = 0 (1o degrau) e em cima cruza o patamar em x = tread*n.
            k = rise / tread
            H = 4.0
            T = H + 1.5
            off = k * (tread * k / 2 + H) / (1 + k * k)
            for s in (-1, 1):
                y = s * (width / 2 + 0.6)
                xa, xb = -off, tread * n - off
                a = F.p(xa, y, (xa + tread / 2) * k + H)
                b = F.p(xb, y, (xb + tread / 2) * k + H)
                col_ramp(area, a, b, 1.2, thick=T)
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


# ------------------------------------------------------------------ penhascos (massas de rocha em estratos)
def _band_walker(pts):
    """parametriza a polilinha pelo comprimento: devolve (comprimento, at(s, h) -> (ponto, tangente suavizada))"""
    segs = []
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        ln = (b - a).length
        if ln < 1e-6:
            continue
        segs.append((acc, a, b, ln))
        acc += ln

    def point(s):
        if not segs:
            return pts[0].copy()
        s = min(max(s, 0.0), acc)
        for s0, a, b, ln in segs:
            if s <= s0 + ln + 1e-9:
                return a + (b - a) * ((s - s0) / ln)
        return segs[-1][2].copy()

    def at(s, h):
        p = point(s)
        t = point(s + h) - point(s - h)
        t.z = 0.0
        if t.length < 1e-6:
            t = Vector((1.0, 0.0, 0.0))
        return p, t.normalized()
    return acc, at


def _rock_poly(a, b, n, rng, ex=3.0, jit=0.1, a0=None):
    """contorno de bloco de rocha (superelipse facetada) em coords locais: x ao longo (semi-eixo a), y atravessado (b).
    expoente > 2 = faces frontais largas e planas (paredoes); a0 ~ 0 com n par deixa uma face chata para a frente."""
    out = []
    a0 = rng.uniform(0, math.tau) if a0 is None else a0
    for i in range(n):
        th = a0 + (i + rng.uniform(-0.12, 0.12)) * math.tau / n
        c, s = math.cos(th), math.sin(th)
        rr = (abs(c) ** ex + abs(s) ** ex) ** (-1.0 / ex)
        k = rng.uniform(1.0 - jit, 1.0 + jit * 0.6)
        out.append((c * rr * a * k, s * rr * b * k))
    return out


def _to_world(poly, t, left):
    """coords locais (ao longo de t, atravessado para 'left') -> deslocamentos 2D de mundo"""
    return [(t.x * px + left.x * py, t.y * px + left.y * py) for px, py in poly]


def cliff_band(mb, pts, z_base, z_top, rng, depth=2.0, rmin=3.5, rmax=6.5, step=6.0, grass=True,
               var=3.0, face_side=1, m="Cliff_Rock", m2="Cliff_Rock_Dark", top_fn=None, strata=True, min_top=None,
               back=None, front=None, detail=None, talus=None, band_m="Cliff_Rock_Top", lid_hi=None, tongues=True):
    """faixa de penhasco ao longo da polilinha, feita de MASSAS de rocha de larguras bem diferentes (nada de tubos
    de orgao): paredoes largos (25%), agulhas estreitas (10%), blocos, pilares e fendas recuadas; topo irregular
    (ruido coerente ao longo da faixa + torres, entalhes e fraturas diagonais quando var >= 2.5).
    Leitura de pedra tambem no Roblox (cor solida por malha): faixa de topo clara (band_m) nos 15-20% de cima de cada
    massa, base mais escura e fria nas massas com estratos, facetas grandes e poucas, musgo/grama escorrendo em
    linguetas sob os tampos. Estratos so em ~50% das massas (cota +-2..4 por massa, inclinados 5-10 graus, nunca
    mais de 3 seguidos). Tampo por massa: 35% rocha nua, 40% grama so de um lado (borda recortada + linguetas caindo
    pela face), 25% cheio. lid_hi: cota acima da qual o tampo vira Grass_Dark / Leaf_Moss; None (padrao) = tampo
    sempre 'Grass', porque o fm_veg so reconhece 'Grass' como chao das zonas rim/mountain (com Grass_Dark acima de
    z40 as arvores dos penhascos caiam de ~430 para ~50).
    face_side: lado (esquerda=+1) para onde a face aponta; as massas ficam para o outro lado e a frente nunca passa
    de ~0.6*rmax alem da linha (ou de 'front', quando dado: faces alinhadas a uma colisao).
    min_top: cota minima de qualquer topo (faixas que fecham volumes, ex. o macico da mina).
    back: profundidade maxima (studs) que as massas ocupam atras da linha; com ele as massas vao para a frente
          da linha em vez de invadir o que esta atras (ex. a camara da mina, a colisao do terraco).
    detail: 'far' = massas vistas de longe (1 anel, menos facetas, sem linguetas, sem beiral, sem talude).
    talus: dict(z=cota do chao no pe da face, ok=fn(x, y) -> bool, every=10) = talude: 2-4 blocos meio enterrados a
           cada ~10 studs diante da face (so onde ok() aceita: fora das rotas e das colisoes).
    tongues: True = linguetas de grama/musgo (menos em 'far'); 'always' = tambem nas faixas 'far' (bordas vistas
             de perto, ex. a queda sob o spawn e o vale)."""
    from mathutils import noise
    rng = random.Random(rng.random())       # fluxo proprio: o rng do chamador avanca 1 passo so
    pts = [P3(p) for p in pts]
    total, at = _band_walker(pts)
    rough = var >= 2.5
    far = detail == "far"
    seed = rng.uniform(0.0, 500.0)
    pmax = max(1.2, rmax * 0.6) if front is None else max(0.0, front)
    h_t = max(1.0, step * 0.5)
    near = rmin < 6.0 and not far       # faixas de massas grandes ficam longe do jogador: tampo simplificado
    U = rng.uniform
    # 1) sequencia de massas (tipo, semi-eixos): largura bimodal (paredoes largos x agulhas) + blocos/pilares/fendas
    units = []
    while True:
        prev = units[-1] if units else None
        r = U(rmin, rmax)
        u = rng.random()
        g = 0.0
        if prev is None:
            kind = "pillar"
        elif prev["kind"] in ("block", "wall") and u < 0.16 and total > 3.0 * rmax:
            kind = "fissure"
        else:
            v = rng.random()
            if v < 0.25:
                kind = "wall"
            elif v < 0.35 and (prev["kind"] != "needle"):
                kind = "needle"
            elif v < 0.55:
                kind = "pillar"
            else:
                kind = "block"
        if kind == "wall":
            a, b = r * U(2.0, 3.0), r * U(0.72, 0.92)
        elif kind == "needle":
            a, b = r * U(0.36, 0.5), r * U(0.45, 0.62)
        elif kind == "block":
            a, b = r * U(1.05, 1.5 if rough else 1.3), r * U(0.82, 1.0)
        elif kind == "pillar":
            a, b = r * U(0.85, 1.1), r * U(0.85, 1.05)
        else:
            g = U(0.18, 0.4) * r
            a, b = g * 0.5 + r * 0.3, r * U(0.6, 0.8)
        if prev is None:
            s = 0.0
        elif kind == "fissure":
            s = prev["s"] + prev["a"] * 0.85 + g * 0.5
        elif prev["kind"] == "fissure":
            s = prev["s"] + prev["g"] * 0.5 + a * 0.85
        else:
            s = prev["s"] + (prev["a"] + a) * U(0.56, 0.72)
        if prev is not None and s >= total - 0.3 * a:
            # fecha a faixa com um pilar no ponto final (pegada igual a das colunas antigas)
            if prev["kind"] == "fissure" or total - prev["s"] > prev["a"] * 0.5:
                a, b = r * U(0.72, 0.95), r * U(0.85, 1.05)
                units.append(dict(s=total, kind="pillar", a=a, b=b, r=r, g=0.0))
            break
        units.append(dict(s=s, kind=kind, a=a, b=b, r=r, g=g))
        if total < 1e-6:
            break
    # 2) cada massa: posicao atras da linha, altura, estratos, tampo, faixa de topo e linguetas
    tops = []
    fronts = []
    run = 0                                  # estratos seguidos (nunca mais de 3)
    cut_f0 = U(0.45, 0.62)                   # cota-base dos estratos na faixa; cada massa desloca +-2..4
    for un in units:
        c, t = at(un["s"], h_t)
        left = Vector((-t.y, t.x, 0.0))
        fdir = left * face_side                       # para onde a face aponta
        kind, a, b, r = un["kind"], un["a"], un["b"], un["r"]
        yaw = U(-0.12, 0.12) * (0.35 if kind == "wall" else 1.0)
        cy, sy = math.cos(yaw), math.sin(yaw)
        t2 = Vector((t.x * cy - t.y * sy, t.x * sy + t.y * cy, 0.0))
        l2 = Vector((-t2.y, t2.x, 0.0))
        off = U(0.3, depth)
        # frente limitada a pmax alem da linha (conta o giro da massa) e desencontrada: sem plano unico
        off = max(off, b * 1.06 + a * abs(sy) - pmax * U(0.5, 1.0))
        if kind == "fissure":
            off += b * U(0.45, 0.65)        # fenda: recuada atras dos vizinhos
        if back is not None:
            off = min(off, back - (b * 1.08 + a * abs(sy)))
        cc = c - fdir * off
        base = top_fn(cc) if top_fn else z_top
        hgt0 = base - z_base
        if rough:
            nz = noise.noise(Vector((un["s"] * 0.04 + seed, seed * 0.37, 0.5)))
            top = base + var * 2.2 * nz + U(-var * 0.6, var * 0.3)
            if kind == "pillar" and hgt0 > 14 and rng.random() < 0.4:
                top += hgt0 * U(0.06, 0.15)       # torre
            elif kind == "needle" and hgt0 > 10:
                top += hgt0 * U(0.08, 0.22)       # agulha
            elif kind == "wall":
                top -= hgt0 * U(0.0, 0.08)        # paredao: crista mais baixa e comprida
            if kind == "fissure":
                top -= hgt0 * U(0.12, 0.25)       # entalhe na crista
        else:
            top = base + U(-var, var * 0.4)
            if kind == "needle":
                top += U(0.2, 0.8) * max(var, 0.5)
            if kind == "fissure":
                top -= U(0.3, 0.8) * max(var, 0.5)
        if min_top is not None:
            top = max(top, min_top)
        top = max(top, z_base + 1.5)
        tops.append(top)
        # facetas grandes e poucas; face frontal plana voltada para o lado da face (a0 alinha uma aresta)
        if kind in ("block", "wall"):
            n = 7 if a > 9.0 else 6
        elif kind == "needle":
            n = 5
        else:
            n = rng.choice((5, 6, 6))
        if far:
            n = min(n, 6 if kind == "wall" else 5)
        a0 = (math.radians(90.0 * face_side - 180.0 / n) % (math.tau / n)) + U(-0.12, 0.12)
        if kind == "wall":
            ex = U(2.6, 3.4)
        elif kind == "block":
            ex = U(2.0, 2.8) if rough else U(1.8, 2.3)
        else:
            ex = U(1.8, 2.6)
        poly = _rock_poly(a, b, n, rng, ex=ex, jit=(0.1 if far else 0.13), a0=a0)
        mm = m if rng.random() > 0.3 else m2
        if kind == "fissure":
            mm = m2
        hgt = top - z_base
        # estratos: ~50% das massas, nunca mais de 3 seguidas, cota deslocada +-2..4 por massa
        cuts = []
        if (strata and kind not in ("fissure", "needle") and hgt > 14 and run < 3 and rng.random() < 0.5):
            dz = rng.choice((-1.0, 1.0)) * U(2.0, 4.0)
            if hgt > 42 and rng.random() < 0.55:
                cuts = [z_base + hgt * cut_f0 * 0.62 + dz, z_base + hgt * min(0.8, cut_f0 * 1.3) + dz * 0.5]
            else:
                cuts = [z_base + hgt * cut_f0 + dz]
            cuts = sorted(q for q in cuts if z_base + 3.0 < q < top - 4.0)
        run = run + 1 if cuts else 0
        # estrato inclinado 5-10 graus (direcao ao longo da faixa, +-30 graus)
        sg = rng.choice((-1.0, 1.0))
        ra_ = U(-0.5, 0.5)
        dv = (t2 * math.cos(ra_) + l2 * math.sin(ra_)) * sg
        gs = math.tan(math.radians(U(5.0, 10.0)))
        slope_s = (dv.x * gs, dv.y * gs)
        # fratura diagonal no topo (~25% das massas largas/pilares das faixas irregulares): silhueta em cunha, nao
        # em tubo. Faixas de borda (var baixo, topo rente a um piso caminhavel) ficam sem fratura.
        frac = rough and kind in ("block", "wall", "pillar") and hgt > 9 and rng.random() < 0.25
        gt = math.tan(math.radians(U(16.0, 30.0))) if frac else 0.0
        sgt = rng.choice((-1.0, 1.0))
        slope_t = (t2.x * gt * sgt, t2.y * gt * sgt) if frac else None
        # tampo da massa (fratura = rocha nua: grama numa rampa de 16-30 graus le como tabua verde)
        lidk = None
        if grass:
            q = rng.random()
            lidk = "bare" if (q < 0.35 or frac) else ("side" if q < 0.75 else "full")
        lid_mat = "Grass" if (lid_hi is None or top < lid_hi) else rng.choice(("Grass_Dark", "Grass_Dark", "Leaf_Moss"))
        ra2 = U(-1.0, 1.0)
        sdir = (fdir * 1.0 + t2 * ra2).normalized()      # lado da grama no tampo parcial (para a face)
        bth = hgt * U(0.15, 0.2)
        zs = [z_base - 0.2] + cuts + [top]
        ctr = cc.copy()
        sc = 1.0
        for ti in range(len(zs) - 1):
            za, zb = zs[ti], zs[ti + 1]
            last = ti == len(zs) - 2
            if last:
                lid = lid_mat if lidk == "full" else None
            else:
                # patamar intermediario: grama em ~40% (o resto e degrau so de rocha)
                lid = (("Grass" if (lid_hi is None or zb < lid_hi) else "Grass_Dark")
                       if (grass and rng.random() < 0.4) else None)
            if ti > 0:
                # estrato de cima recuado para tras da face e deslocado de lado -> patamar largo e assimetrico
                sc *= U(0.68, 0.84)
                shift = b * sc * U(0.2, 0.42)
                if back is not None:
                    shift = min(shift, max(0.0, back - (ctr - c).dot(-fdir) - b * sc * 1.08 - a * sc * abs(sy)))
                ctr = ctr - fdir * shift + t2 * (a * U(-0.25, 0.25))
                za -= 0.4 + gs * a * sc          # base enterrada no topo inclinado do estrato de baixo
            th = zb - za
            rings = 1 if (far or th < 9) else 2
            jit = 0.1 if far else (0.15 if rough else 0.12)
            lean = None
            if last and rough and rng.random() < 0.5 and th > 6:
                lv = fdir * min(1.5, 0.15 * b * sc) + t2 * U(-0.6, 0.6)
                lean = (lv.x, lv.y)
            ztop = zb + (0.5 if (lid and last) else 0.0)
            # base (estrato de baixo) mais escura e fria; estratos de cima na cor da massa
            if len(zs) > 2:
                mt = m2 if ti == 0 else m
            else:
                mt = mm
            band = (min(bth, th * 0.6), band_m) if (last and band_m and th > 2.0) else None
            slope = slope_t if last else (slope_s if cuts else None)
            tong = None
            if last and grass and (tongues == "always" or (tongues and not far)):
                if lidk == "full":
                    tong = (rng.randint(1, 2), "Grass_Dark", (1.0, 3.0), (fdir.x, fdir.y))
                elif lidk == "side":
                    tong = (rng.randint(1, 3), lid_mat, (1.0, 3.0), (sdir.x, sdir.y))
            lip = U(0.4, 1.2)
            if last and rough and kind in ("block", "wall") and a * sc > 8.0 and th > 8.0 and not frac \
                    and rng.random() < 0.4:
                # crista partida: o bloco largo termina em dois blocos de alturas diferentes (entalhe)
                half = [(px * sc * 0.56, py * sc * U(0.9, 1.0)) for px, py in poly]
                drop = th * U(0.15, 0.3)
                dk = rng.randrange(2)
                for k, sgn in enumerate((-1, 1)):
                    ck = ctr + t2 * (sgn * a * sc * 0.46)
                    zk = ztop - (drop if k == dk else 0.0)
                    if min_top is not None:
                        zk = max(zk, min_top)
                    rock_column(mb, ck, _to_world(half, t2, l2), za, zk, rng, mt if k == 0 else m2,
                                taper=U(0.78, 0.9), rings=rings, jitter=jit, tilt=0.16, lean=lean, top_m=lid,
                                lip=lip, chamfer=(0.0 if lid else min(0.45, th * 0.1)), rim=near,
                                band=((min(bth, (zk - za) * 0.6), band_m) if band else None), bottom=False)
                continue
            wp = _to_world([(px * sc, py * sc) for px, py in poly], t2, l2)
            rock_column(mb, ctr, wp, za, ztop, rng, mt,
                        taper=(0.93 if not last else (U(0.7, 0.86) if rough else U(0.78, 0.9))), rings=rings,
                        jitter=jit, tilt=(0.05 if not last else (0.18 if rough else 0.12)), lean=lean, top_m=lid,
                        lip=lip, chamfer=(0.0 if lid else min(0.45, th * 0.1)), rim=near,
                        slope=slope, band=band, tongues=tong, bottom=False)
            if last and lidk == "side":
                _side_lid(mb, _LAST_TOP, lid_mat, U(0.4, 1.2), sdir, rng)
        fronts.append((un["s"], cc + fdir * b))
    # 3) parede de fundo continua (escondida atras das massas): a faixa nunca tem fresta de ponta a ponta,
    #    nem quando duas massas vizinhas ficam em profundidades diferentes (fecha a mina, o canion, o vale)
    if len(units) > 1 and total > 1.0:
        zt_b = min(tops) - 0.6
        if zt_b > z_base + 2.0:
            ob = depth * 0.5 + rmin * 0.45 + max(0.0, rmax * 0.6 - pmax)   # frente limitada: massas mais atras
            th_b = max(1.0, rmin * 0.7)
            if back is not None:
                ob = min(ob, back - th_b * 0.5)
            bp = [Vector((p.x, p.y, 0.0)) for p in resample(pts, max(8.0, rmax * 2.0))]
            u0, u1 = face_side * (ob - th_b * 0.5), face_side * (ob + th_b * 0.5)
            prof = [(u0, z_base - 0.2), (u1, z_base - 0.2), (u1, zt_b), (u0, zt_b)]
            mb.sweep(bp, prof, m2, True)
    # 4) talude no pe da face: blocos meio enterrados (o vegetation poe samambaia e arbusto entre eles)
    if talus and fronts:
        zg = talus["z"]
        ok = talus.get("ok")
        every = talus.get("every", 10.0)
        s = U(0.0, every * 0.5)
        while s < total:
            fs_, fp_ = min(fronts, key=lambda f: abs(f[0] - s))
            c, t = at(s, h_t)
            fdir = Vector((-t.y, t.x, 0.0)) * face_side
            face = c + fdir * (fp_ - c).dot(fdir)
            for k in range(rng.randint(2, 4)):
                sz = U(1.2, 3.0) * (1.25 if k == 0 else 1.0)
                p = face + fdir * U(0.1, 2.6) + t * U(-4.5, 4.5)
                if ok is not None and not ok(p.x, p.y):
                    continue
                aa, bb = sz * U(0.65, 1.0), sz * U(0.5, 0.85)
                ang = U(0.0, math.tau)
                ca, sa = math.cos(ang), math.sin(ang)
                pl = [(x * ca - y * sa, x * sa + y * ca)
                      for x, y in _rock_poly(aa, bb, rng.choice((5, 6)), rng, ex=U(1.8, 2.4), jit=0.18)]
                rock_column(mb, Vector((p.x, p.y, 0.0)), pl, zg - sz * 0.35, zg + sz * U(0.3, 0.6), rng,
                            m if rng.random() < 0.6 else m2, taper=U(0.55, 0.8), rings=1, jitter=0.15, tilt=0.25,
                            chamfer=min(0.35, sz * 0.15), rim=False, bottom=False)
            s += every * U(0.8, 1.2)
    return


def _side_lid(mb, top, mat, thick, sdir, rng):
    """tampo de grama so de um lado do topo da massa (o ultimo rock_column): poligono do topo cortado por um
    semiplano com borda recortada (zigue-zague), seguindo o plano do topo; a grama transborda 5% pela aresta"""
    ring = top.get("ring")
    if not ring or len(ring) < 3:
        return
    n = len(ring)
    cx = sum(p[0] for p in ring) / n
    cy = sum(p[1] for p in ring) / n
    cz = sum(p[2] for p in ring) / n
    sxx = sum((p[0] - cx) ** 2 for p in ring)
    syy = sum((p[1] - cy) ** 2 for p in ring)
    sxy = sum((p[0] - cx) * (p[1] - cy) for p in ring)
    sxz = sum((p[0] - cx) * (p[2] - cz) for p in ring)
    syz = sum((p[1] - cy) * (p[2] - cz) for p in ring)
    det = sxx * syy - sxy * sxy
    gx = (sxz * syy - syz * sxy) / det if abs(det) > 1e-9 else 0.0
    gy = (syz * sxx - sxz * sxy) / det if abs(det) > 1e-9 else 0.0
    rad = top.get("rad", 1.0)
    cap = top.get("cap", 0.0)

    def zp(x, y):
        return cz + cap + gx * (x - cx) + gy * (y - cy)
    ov = 1.05
    poly = [(cx + (p[0] - cx) * ov, cy + (p[1] - cy) * ov) for p in ring]
    d = Vector((sdir[0], sdir[1], 0.0))
    if d.length < 1e-6:
        return
    d.normalize()
    off = -rad * rng.uniform(0.0, 0.3)      # cobre ~50-65% do topo pelo lado d
    out = []
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        dp = (P[0] - cx) * d.x + (P[1] - cy) * d.y - off
        dq = (Q[0] - cx) * d.x + (Q[1] - cy) * d.y - off
        if dp >= 0:
            out.append((P, False))
        if (dp >= 0) != (dq >= 0):
            tt = dp / (dp - dq)
            out.append(((P[0] + (Q[0] - P[0]) * tt, P[1] + (Q[1] - P[1]) * tt), True))
    if len(out) < 3:
        return
    # borda recortada: zigue-zague entre os dois pontos de corte consecutivos
    res = []
    m_ = len(out)
    for i in range(m_):
        res.append(out[i][0])
        j = (i + 1) % m_
        if out[i][1] and out[j][1]:
            A, B = Vector(out[i][0]), Vector(out[j][0])
            for f in (0.3, 0.55, 0.8):
                q = A.lerp(B, f) + d.xy * rad * rng.uniform(-0.1, 0.22)
                res.append((q.x, q.y))
    vb = [mb.bm.verts.new((x, y, zp(x, y) - 0.15)) for x, y in res]
    vt = [mb.bm.verts.new((x, y, zp(x, y) + thick)) for x, y in res]
    k = len(res)
    try:
        mb.bm.faces.new(list(reversed(vb)))
        mb.bm.faces.new(vt)
        for i in range(k):
            j = (i + 1) % k
            mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    except ValueError:
        return
    mb._post(vb + vt, mat, None, 0, 1)


def rock_scatter(mb, center, radius, n, rng, smin=1.2, smax=3.2, z=0.0, m="Cliff_Rock"):
    """pedras soltas agrupadas: uma pedra-mae e satelites menores, achatadas e meio enterradas"""
    for i in range(n):
        a = rng.uniform(0, math.tau)
        r = radius * math.sqrt(rng.random())
        s = rng.uniform(smin, smax) * (1.35 if i == 0 else 1.0)
        mb.rock((center[0] + math.cos(a) * r, center[1] + math.sin(a) * r, z + s * 0.18),
                (s * rng.uniform(1.0, 1.6), s * rng.uniform(0.8, 1.2), s * rng.uniform(0.5, 0.85)),
                m if rng.random() > 0.25 else "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 6)))


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
                 openings=(), blk=(1.8, 3.4), core=True, quoins=(True, True), base_dark=True, tones=None,
                 bevel=0.14, core_m="Stone_Grout"):
    """parede de blocos entre a e b; openings = [(s0, s1, zlo, zhi[, flecha_do_arco])] ao longo de a->b.
    Blocos com leve giro/inclinacao (assentamento a mao) - sem consumir o rng compartilhado.
    blk = faixa de comprimento dos blocos (blocos maiores = menos triangulos, leitura mais robusta).
    core: laje-nucleo continua de rejunte escuro atras dos blocos (espessura thick-0.35, recortada nas aberturas):
          as juntas deixam de atravessar a parede (antes se via o ceu/interior pelas frestas contra a luz).
          core_m = material do nucleo (as casas usam Stone_Dark, que ja tem: uma MeshPart a menos por casa).
    mix: fracao de blocos em m2, limitada a 0.12 (nada de sal-e-pimenta claro/escuro bloco a bloco).
    base_dark / quoins: fiada de base e cunhais (blocos das pontas a->b) sempre em m2.
    tones: lista opcional de materiais do MESMO tom (variacao de valor +-6-8%) sorteados bloco a bloco em vez de m."""
    a, b = P3(a), P3(b)
    L = (b - a).length
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    mix = min(mix, 0.12)
    if core and L > 0.3 and z1 - z0 > 0.2 and thick > 0.6:
        _masonry_core(mb, a, d, ang, L, z0, z1, max(0.25, thick - 0.35), openings, core_m)
    z = z0
    row = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        s = -rng.uniform(0, 1.2) if row % 2 else 0.0
        mrow = m2 if (base_dark and row == 0 and z1 - z0 > course * 1.5) else None
        while s < L - 0.05:
            w = rng.uniform(*blk)
            sa, sb = max(s, 0.0), min(s + w, L)
            mq = mrow or (m2 if ((quoins[0] and sa <= 0.01) or (quoins[1] and sb >= L - 0.01)) else None)
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
                        _block(mb, a, d, ang, sa, o0, z, h, thick, rng, m, m2, mix, mq, tones, bevel)
                    if sb > o1:
                        _block(mb, a, d, ang, o1, sb, z, h, thick, rng, m, m2, mix, mq, tones, bevel)
                    blocked = True
                    break
            if not blocked:
                _block(mb, a, d, ang, sa, sb, z, h, thick, rng, m, m2, mix, mq, tones, bevel)
            s += w
        z += h
        row += 1


def _masonry_core(mb, a, d, ang, L, z0, z1, th, openings, m="Stone_Grout"):
    """nucleo de rejunte: faixas verticais entre as aberturas + peitoril/verga de cada abertura (arco: recorta o
    retangulo inteiro ate o fecho - a bandeira e as aduelas ficam a vista)"""
    cuts = [(max(0.0, op[0] + 0.05), min(L, op[1] - 0.05), op[2], op[3]) for op in openings]
    cuts = [c for c in cuts if c[1] > c[0]]
    segs = []
    xb = sorted(set([0.0, L] + [c[k] for c in cuts for k in (0, 1)]))
    for s0, s1 in zip(xb, xb[1:]):
        mid = (s0 + s1) / 2
        zc = z0
        for (zl, zh) in sorted((c[2], c[3]) for c in cuts if c[0] < mid < c[1]):
            if zl > zc:
                segs.append((s0, s1, zc, zl))
            zc = max(zc, zh)
        if zc < z1:
            segs.append((s0, s1, zc, z1))
    for s0, s1, za, zb in segs:
        za, zb = max(za, z0), min(zb, z1)
        if s1 - s0 < 0.1 or zb - za < 0.1:
            continue
        c = a + d * ((s0 + s1) / 2)
        mb.box((s1 - s0, th, zb - za), (c.x, c.y, (za + zb) / 2), (0, 0, ang), m, 0.0)


def _block(mb, a, d, ang, sa, sb, z, h, thick, rng, m, m2, mix, mq=None, tones=None, bevel=0.14):
    if sb - sa < 0.15:
        return
    c = a + d * ((sa + sb) / 2)
    r = rng.random()
    mm = m2 if r < mix else m
    out = rng.uniform(-0.08, 0.12)
    lr = _lrng(c.x, c.y, z)
    if mq:
        mm = mq
    elif tones and mm == m:
        mm = tones[int(lr.random() * len(tones)) % len(tones)]
    # giro/rolagem pequenos + altura levemente irregular: a parede deixa de parecer grade perfeita
    L_ = sb - sa
    yaw = lr.uniform(-0.018, 0.018) if L_ > 0.8 else 0.0
    roll = lr.uniform(-0.012, 0.012) if L_ > 0.8 else 0.0
    dh = lr.uniform(-0.05, 0.03)
    mb.box((L_ - 0.1, thick + out, h - 0.1 + dh), (c.x, c.y, z + h / 2 + dh / 2), (roll, 0, ang + yaw), mm, bevel, 1)


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
                braces=True, out_side=1, wobble=0.025, inner=None, brace_bevel=0.06, cut_plates=False,
                detail="full"):
    """painel de reboco com estrutura de madeira aparente (dos dois lados); openings = [(s0,s1,zlo,zhi)].
    wobble = inclinacao maxima (rad) dos montantes livres; escoras e secoes levemente irregulares (feito a mao).
    inner = lado interno (-1/+1, normal esquerda de a->b): la as pecas saem sem chanfro (economia de triangulos).
    detail='near' (paredes de fundo, vistas so de perto): sem chanfro nenhum e, do lado de dentro, so frechal,
    soleira e montantes (sem escoras nem guarnicoes) - ~40% menos triangulos.
    As variacoes usam rng local: nao mudam os sorteios compartilhados de quem chama."""
    if detail == "near":
        brace_bevel = 0.0
    a, b = P3(a), P3(b)
    L_ = (b - a).length
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    nrm = Vector((-d.y, d.x, 0))
    lr = _lrng(a.x, a.y, b.x, b.y, z0)
    # reboco (recortado nas aberturas): faixas verticais entre todas as bordas de abertura, cada faixa sem os
    # trechos cobertos por QUALQUER abertura que a cruze (aberturas sobrepostas - portal de pedra + janela acima -
    # deixavam o reboco tapando a janela)
    cuts = sorted(openings)
    segs = []
    xb = sorted(set([0.0, L_] + [min(max(o[k], 0.0), L_) for o in cuts for k in (0, 1)]))
    for s0, s1 in zip(xb, xb[1:]):
        if s1 - s0 < 0.05:
            continue
        mid = (s0 + s1) / 2
        zc = z0
        for (zl, zh) in sorted((o[2], o[3]) for o in cuts if o[0] < mid < o[1]):
            if zl > zc:
                segs.append((s0, s1, zc, min(zl, z1)))
            zc = max(zc, zh)
        if zc < z1:
            segs.append((s0, s1, zc, z1))
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
    near = detail == "near"
    for side in (-1, 1):
        off = nrm * side * fo
        bf = 0.0 if (side == inner or near) else 1.0
        lite = near and side == inner
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
        # frechal: interrompido nos vaos que passam do topo da parede (portal de pedra que sobe no oitao)
        tspans = [(0.0, L_)]
        for o in cuts:
            if o[3] >= z1 - 0.5:
                tspans = [(s0, min(s1, o[0])) for (s0, s1) in tspans if min(s1, o[0]) - s0 > 0.2] + \
                         [(max(s0, o[1]), s1) for (s0, s1) in tspans if s1 - max(s0, o[1]) > 0.2]
        for s0, s1 in tspans:
            mb.beam(a + d * s0 + off + Vector((0, 0, z1 - 0.38)), a + d * s1 + off + Vector((0, 0, z1 - 0.38)), 0.5,
                    plate_j[1], m_t, 0.08 * bf)
        for x in xs:
            p = a + d * min(max(x, 0.3), L_ - 0.3) + off
            if any(o[0] + 0.3 < x < o[1] - 0.3 for o in cuts):
                continue
            lx, pw = lean[x]
            mb.beam(p + Vector((0, 0, z0)) - d * (lx / 2), p + Vector((0, 0, z1)) + d * (lx / 2), pw, tw, m_t,
                    0.08 * bf)
        if braces and not lite:
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
        for o in (() if lite else cuts):
            for x in (o[0], o[1]):
                p = a + d * x + off
                mb.beam(p + Vector((0, 0, o[2])), p + Vector((0, 0, min(o[3], z1))), 0.55, 0.75, m_t, 0.08 * bf)
            pa = a + d * (o[0] - 0.4) + off
            pb = a + d * (o[1] + 0.4) + off
            for zz in (o[2], o[3]):
                if cut_plates and zz == o[2] and o[2] <= z0 + 0.8:
                    continue   # vao de porta: sem travessa embaixo
                if zz > z1 - 0.3:
                    continue   # vao que passa do topo da parede: sem verga flutuando acima do frechal
                mb.beam(pa + Vector((0, 0, zz)), pb + Vector((0, 0, zz)), 0.55, 0.75, m_t, 0.08 * bf)


def window_glow(mb, a, b, s0, s1, zlo, zhi, thick, m="Window_Warm", bars=True, sill=False, sill_m="Wood_Dark",
                panes=None, style="cross", bar_m="Wood_Dark"):
    """vidraca dentro de uma abertura. m padrao = Window_Warm (vidro quente, brilho moderado); Lantern_Glow so
    quando o chamador pede (loja/forja passam explicito); Window_Dark = janela apagada (vidro escuro de dia).
    style: 'cross' (cruz: travessa + montantes), 'two' (2 folhas: so o montante central), 'grid' (travessa + 2
    montantes), 'slit' (fresta, sem caixilho). panes = n de montantes (sobrepoe o estilo).
    sill=True: peitoril saliente dos dois lados (profundidade na fachada)."""
    from fm_lib import MATS
    MATS.setdefault("Window_Warm", ((0.92, 0.42, 0.12), 0.35, 0.0, 1.8, (1.0, 0.5, 0.16), 0.0))
    MATS.setdefault("Window_Dark", ((0.035, 0.045, 0.06), 0.18, 0.0, 0.0, None, 0.0))
    a, b = P3(a), P3(b)
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    c = a + d * ((s0 + s1) / 2)
    mb.box((s1 - s0, thick * 0.3, zhi - zlo), (c.x, c.y, (zlo + zhi) / 2), (0, 0, ang), m, 0.0)
    if bars and style != "slit":
        if style in ("cross", "grid") or panes:
            mb.box((s1 - s0, thick * 0.5, 0.25), (c.x, c.y, (zlo + zhi) / 2), (0, 0, ang), bar_m, 0.0)
        k = panes or (2 if style == "grid" else 1)
        for i in range(k):
            f = (i + 1) / (k + 1)
            q = a + d * (s0 + (s1 - s0) * f)
            mb.box((0.25, thick * 0.5, zhi - zlo), (q.x, q.y, (zlo + zhi) / 2), (0, 0, ang), bar_m, 0.0)
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

_LAST_TOP = {}     # ultimo topo de rock_column: anel (x, y, z), centro e inclinacao (tampos parciais do cliff_band)


def rock_column(mb, cc, poly, z0, z1, rng, m, taper=0.85, rings=3, jitter=0.13, tilt=0.12, lean=None,
                top_m=None, lip=0.9, chamfer=0.0, taper_from=None, rim=True, slope=None, band=None, tongues=None,
                bottom=True):
    """prisma de rocha facetado: aneis com jitter radial por vertice (faces irregulares), topo inclinado.
    lean: deslocamento (x, y) do topo, aplicado progressivamente (saliencia / massa inclinada).
    top_m: material de um TAMPO integrado (ex. grama): aba saliente com beiral por baixo + chanfro no topo,
           sem prisma extra (bem mais barato que um prisma chanfrado por cima).
    chamfer: chanfro do topo na propria rocha (quando nao ha top_m).
    taper_from: cota onde o afunilamento comeca (base enterrada bem abaixo: a parte visivel afunila de verdade).
    rim: tampo com aba vertical (perto do jogador); False = so aba chanfrada (massas vistas de longe, 2n tris a menos).
    slope: (gx, gy) = dz por stud do plano do topo (estrato inclinado, fratura diagonal); substitui o tilt aleatorio.
    band: (espessura, material) = faixa de topo: anel extra 'espessura' abaixo do topo, acompanhando a inclinacao;
          as faces acima dele (e o topo, se nao houver tampo) recebem o material (rocha iluminada no Roblox, onde
          cada malha e cor solida).
    tongues: (n, material, (lmin, lmax), dir) = linguetas finas descendo da borda do topo pela face (musgo, grama
             caindo); dir (x, y) = lado preferido (None = qualquer).
    bottom: False = sem a face de baixo (base enterrada ou apoiada em outra massa).
    Retorna o centro do topo (Vector)."""
    n = len(poly)
    cap = lip if top_m else (chamfer if chamfer > 0 else 0.0)
    cap = min(cap, (z1 - z0) * 0.35)
    zb = z1 - cap
    h = zb - z0
    if taper_from is not None and z0 + 1.0 < taper_from < zb - 2.0:
        hv = zb - taper_from
        levels = [(z0, 0.0, 0.0)] + [(taper_from + hv * k / rings, k / rings, hv) for k in range(rings + 1)]
    else:
        levels = [(z0 + h * k / rings, k / rings, h) for k in range(rings + 1)]
    band_i = None
    if band is not None:
        zband = zb - band[0]
        if band[0] > 0.2 and zband > levels[-2][0] + 0.4:
            (za_, fa_, ha_), (zb_, fb_, hb_) = levels[-2], levels[-1]
            fband = fa_ + (fb_ - fa_) * (zband - za_) / max(1e-6, zb_ - za_)
            levels.insert(len(levels) - 1, (zband, fband, hb_))
            band_i = len(levels) - 2
    ring_vs = []
    tx, ty = rng.uniform(-tilt, tilt), rng.uniform(-tilt, tilt)
    if slope is not None:
        tx, ty = slope
    lx, ly = lean if lean else (0.0, 0.0)
    last_i = len(levels) - 1
    for i, (zc, f, hh) in enumerate(levels):
        if 0 < f < 1 and i != band_i:
            zc += rng.uniform(-0.12, 0.12) * hh / rings
        sc = 1.0 + (taper - 1.0) * (f ** 1.3) + (0.06 if (rings > 1 and abs(f - 1.0 / rings) < 1e-6) else 0.0)
        lf = f ** 1.6
        ring = []
        for (px, py) in poly:
            j = 1.0 + rng.uniform(-jitter, jitter) * (0.4 if i == 0 else 1.0)
            x = cc.x + px * sc * j + lx * lf
            y = cc.y + py * sc * j + ly * lf
            z = zc + ((px * tx + py * ty) if (i == last_i or i == band_i) else 0.0)
            ring.append(mb.bm.verts.new((x, y, z)))
        ring_vs.append(ring)
    if band_i is not None:
        # anel da faixa sobre a propria face (interpola o anel de baixo e o de cima: sem quina), cota do plano do topo
        r0, r1 = ring_vs[band_i - 1], ring_vs[band_i + 1]
        for v, a_, b_ in zip(ring_vs[band_i], r0, r1):
            dz = b_.co.z - a_.co.z
            if dz < 0.3:
                v.co.z = a_.co.z + dz * 0.5
                k = 0.5
            else:
                v.co.z = max(v.co.z, a_.co.z + 0.15 * dz)
                k = (v.co.z - a_.co.z) / dz
            v.co.x = a_.co.x + (b_.co.x - a_.co.x) * k
            v.co.y = a_.co.y + (b_.co.y - a_.co.y) * k
    top = ring_vs[-1]
    cx = sum(v.co.x for v in top) / n
    cy = sum(v.co.y for v in top) / n
    rad = max(0.3, sum(math.hypot(v.co.x - cx, v.co.y - cy) for v in top) / n)

    def ring_from(src, s, dz):
        return [mb.bm.verts.new((cx + (v.co.x - cx) * s, cy + (v.co.y - cy) * s, v.co.z + dz)) for v in src]

    extra = []
    cap_faces = []
    if top_m and cap > 0.05:
        ov = 1.0 + min(0.12, max(0.05, 0.45 / rad))
        ch = min(0.3, 0.55 / rad)
        ra = ring_from(top, ov, 0.0)
        rc = ring_from(top, ov * (1.0 - ch), cap)
        if rim:
            rb = ring_from(top, ov, cap * 0.6)
            extra = [top, ra, rb, rc]
        else:
            extra = [top, ra, rc]
        last = rc
    elif cap > 0.05:
        ch = min(0.35, cap / rad)
        rc = ring_from(top, 1.0 - ch, cap)
        extra = [top, rc]
        last = rc
    else:
        last = top
    if bottom:
        mb.bm.faces.new(list(reversed(ring_vs[0])))
    cap_faces.append(mb.bm.faces.new(last))
    band_faces = []
    for k, (r0, r1) in enumerate(zip(ring_vs, ring_vs[1:])):
        for i in range(n):
            j = (i + 1) % n
            f = mb.bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
            if band_i is not None and k >= band_i:
                band_faces.append(f)
    for r0, r1 in zip(extra, extra[1:]):
        for i in range(n):
            j = (i + 1) % n
            cap_faces.append(mb.bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    allv = [v for r in ring_vs for v in r] + [v for r in extra[1:] for v in r]
    mb._post(allv, m, None, 0, 1)
    if band_i is not None:
        bf = band_faces + ([] if top_m else cap_faces)
        mi = mb._mi_for(band[1])
        tt = mb.rng.uniform(-1, 1)
        for f in bf:
            f.material_index = mi
            f[mb.tint] = tt
    if top_m and extra:
        mi = mb._mi(top_m)
        tt = mb.rng.uniform(-1, 1)
        for f in cap_faces:
            f.material_index = mi
            f[mb.tint] = tt
    _LAST_TOP.clear()
    _LAST_TOP.update(ring=[tuple(v.co) for v in top], c=(cx, cy), slope=(tx, ty), rad=rad, cap=cap)
    if tongues and tongues[0] > 0 and len(ring_vs) >= 2:
        _tongues(mb, ring_vs[-2], top, (cx, cy), tongues, rng)
    return Vector((cx, cy, z1))


def _tongues(mb, below, top, c, spec, rng):
    """linguetas (musgo / grama caindo) coladas na face logo abaixo da borda do topo: pentagono recortado que
    acompanha a face entre o anel de cima e o de baixo, afastado 0.12 da rocha"""
    k, mat, (lmin, lmax), d = spec
    n = len(top)
    cands = []
    for i in range(n):
        j = (i + 1) % n
        a, b = top[i].co, top[j].co
        e = Vector((b.x - a.x, b.y - a.y, 0.0))
        if e.length < 0.8:
            continue
        nrm = Vector((e.y, -e.x, 0.0)).normalized()
        mid = Vector(((a.x + b.x) / 2 - c[0], (a.y + b.y) / 2 - c[1], 0.0))
        if nrm.dot(mid) < 0:
            nrm = -nrm
        w = 1.0 if d is None else max(0.0, nrm.dot(Vector((d[0], d[1], 0.0)).normalized()) + 0.15)
        if w > 0.05:
            cands.append((w * e.length, i, j, nrm))
    if not cands:
        return
    tot = sum(cw for cw, _, _, _ in cands)
    mi = mb._mi(mat)
    tt = mb.rng.uniform(-1, 1)
    faces = []
    for _ in range(int(k)):
        x = rng.random() * tot
        pick = cands[-1]
        for cnd in cands:
            x -= cnd[0]
            if x <= 0:
                pick = cnd
                break
        _, i, j, nrm = pick
        A, B = top[i].co, top[j].co
        A2, B2 = below[i].co, below[j].co
        ln = (Vector(B) - Vector(A)).length
        wid = min(ln * 0.8, rng.uniform(0.9, 2.4))
        u0 = rng.uniform(0.05, max(0.06, 1.0 - wid / ln - 0.05))
        u1 = u0 + wid / ln
        hz = max(0.5, min(A.z, B.z) - max(A2.z, B2.z))
        L_ = min(rng.uniform(lmin, lmax), hz * 0.85)

        def fp(u, dd):
            t = Vector(A).lerp(Vector(B), u)
            s = Vector(A2).lerp(Vector(B2), u)
            f = dd / max(0.3, t.z - s.z)
            return t.lerp(s, min(1.0, f)) + nrm * 0.12
        um = (u0 + u1) / 2 + rng.uniform(-0.12, 0.12) * (u1 - u0)
        pts = [fp(u0, 0.0), fp(u0, L_ * rng.uniform(0.4, 0.75)), fp(um, L_), fp(u1, L_ * rng.uniform(0.3, 0.6)),
               fp(u1, 0.0)]
        # piramide rasa fechada (face recortada + apice enterrado na rocha): o recalculo de normais do MB
        # orienta a face para fora (uma face solta poderia sair invertida e sumir no Roblox)
        ctr = sum(pts, Vector()) / len(pts) - nrm * 0.3
        vs = [mb.bm.verts.new(p) for p in pts]
        ap = mb.bm.verts.new(ctr)
        try:
            fr = mb.bm.faces.new(vs)
            new = [fr]
            for q in range(len(vs)):
                new.append(mb.bm.faces.new((vs[(q + 1) % len(vs)], vs[q], ap)))
        except ValueError:
            continue
        for f in new:
            f.normal_update()
            f.material_index = mi
            f[mb.tint] = tt
            f.smooth = False
        faces += new
    mb._uv(faces, mat)


_LAST_PEAK = {}   # info do ultimo peak (dominante: patamar e frente, para o busto esculpido)


def peak(mb, x, y, r, h, rng, z0=10.0, m="Cliff_Rock", m2="Cliff_Rock_Dark", kind=None, face=None,
         top_m="Grass_Dark", root=None, lids=True, avoid=None, fit=None, base_taper=None, shelf_z=None):
    """MACICO de fundo quebrado (nada de cone): aglomerado de 1-4 corpos de rocha de alturas e larguras diferentes,
    cada um com base facetada (patamar de grama opcional) e coroa partida; o conjunto le como montanha com
    paredoes, ombros, dentes e reentrancias.
    kind: 'spire' (dente alto e estreito + flancos baixos), 'horn' (chifre inclinado com topo partido),
          'wall' (paredao largo de crista serrilhada), 'mesa' (degraus largos com patamares), 'saddle' (sela baixa),
          'dominant' (macico dominante: base larga + ombro inclinado subindo em degraus ate um chifre alto),
          'range' (cordilheira baixa e comprida: base em talude, crista quase horizontal).
    z0 = base visual (proporcoes); root = cota real da base (ex. enterrada no vale distante).
    face = direcao (x, y) para onde o macico olha (padrao: centro do mapa).
    avoid(x, y, raio) -> True se o flanco nao pode ficar ali (corredores, areas jogaveis).
    fit(x, y) -> True se o CORPO nao pode chegar ali: o raio encolhe ate as pontas laterais ficarem livres.
    base_taper: afunilamento do embasamento (1/1.6 = base em talude com raio 1.6x o do topo).
    shelf_z: (dominante) cota do patamar do embasamento; a info vai para _LAST_PEAK."""
    rng = random.Random(rng.random())
    kind = kind or rng.choice(("spire", "horn", "wall", "mesa"))
    f = Vector((face[0], face[1], 0.0)) if face else Vector((-x, -y, 0.0))
    f = f.normalized() if f.length > 1e-6 else Vector((0.0, -1.0, 0.0))
    sd = Vector((-f.y, f.x, 0.0))
    back = -f
    zr = z0 if root is None else root
    lid = top_m if lids else None
    c0 = Vector((x, y, 0.0))
    side = rng.choice((-1, 1))
    U = rng.uniform
    if fit is not None:
        k_ext = {"wall": 2.6, "mesa": 1.9, "dominant": 2.2, "range": 1.8}.get(kind, 1.7)
        for _ in range(8):
            e = sd * (r * k_ext)
            if not (fit(x + e.x, y + e.y) or fit(x - e.x, y - e.y) or fit(x + f.x * r, y + f.y * r)):
                break
            r *= 0.88
    _LAST_PEAK.clear()

    def column(ctr, a, b, za, zb, taper, mat, tilt, n=None, lean=None, with_lid=False, visible_from=None, ex=None,
               rings=2, chamfer=0.0, slope=None):
        nn = n or rng.choice((6, 6, 7))
        poly = _rock_poly(a, b, nn, rng, ex=ex or U(2.0, 3.0), jit=0.14)
        rock_column(mb, ctr, _to_world(poly, sd, back), za, zb, rng, mat, taper=taper, rings=rings, jitter=0.12,
                    tilt=tilt, lean=lean, top_m=(lid if with_lid else None), lip=1.6, taper_from=visible_from,
                    chamfer=chamfer, rim=False, slope=slope, bottom=False)

    vis = z0 - 4.0 if zr < z0 - 6.0 else None

    def crown(c, a, b, za, zt, kind_c, mat, alt, lid_p=0.3):
        """coroa partida sobre o ombro: 'block' (topo chato inclinado), 'tooth' (dente chanfrado),
        'horn' (chifre inclinado), 'twin' (dois blocos com entalhe entre eles)"""
        ch = min(3.5, 0.14 * a)      # topo chanfrado: coroas robustas de cartoon, nada de agulha
        if kind_c == "block":
            column(c, a, b, za, zt, U(0.62, 0.8), alt, U(0.16, 0.28), with_lid=rng.random() < lid_p, chamfer=ch)
        elif kind_c == "tooth":
            column(c, a, b, za, zt, U(0.5, 0.64), alt, U(0.24, 0.36), n=rng.choice((5, 6, 7)),
                   lean=tuple((sd * (side * a * U(0.1, 0.25))).xy), chamfer=ch)
        elif kind_c == "horn":
            column(c, a, b, za, zt, U(0.38, 0.5), alt, U(0.3, 0.44), n=rng.choice((6, 7)),
                   lean=tuple((sd * (side * a * U(0.35, 0.5))).xy), chamfer=ch * 0.7)
        else:
            for k, sg in enumerate((-1, 1)):
                ck = c + sd * (sg * a * U(0.32, 0.4))
                zk = zt if (k == 0) == (side > 0) else zt - (zt - za) * U(0.25, 0.45)
                column(ck, a * U(0.56, 0.66), b * U(0.75, 0.95), za, zk, U(0.56, 0.72), alt if k == 0 else mat,
                       U(0.2, 0.32), n=rng.choice((5, 6, 7)), chamfer=ch * 0.6)

    def mountain(c, hrel, a, crown_k, bw=None, shelf=0.5, lid_p=0.3, t1=None):
        """perfil de montanha: base larga (afunila so na parte visivel) -> ombro recuado e deslocado -> coroa"""
        zt = z0 + h * hrel
        hm = zt - z0
        b = a * (bw or U(0.55, 0.8))
        mat = m2 if rng.random() < 0.55 else m
        alt = m if mat == m2 else m2
        z1 = z0 + hm * U(0.34, 0.5)
        big = a > 32.0
        t1 = t1 or U(0.68, 0.8)
        column(c, a, b, zr, z1, t1, mat, 0.09, with_lid=rng.random() < shelf, visible_from=vis,
               n=(rng.choice((8, 9)) if big else rng.choice((6, 7, 7, 8))), rings=(3 if big else 2))
        # ombro encostado num dos lados do topo da base: um lado le como paredao continuo, o outro como degrau
        # (nunca mais largo que o topo de baixo: nada de "cogumelo")
        s2 = t1 * U(0.8, 0.95)
        sg2 = rng.choice((-1, 1))
        c2 = c + sd * (sg2 * a * (t1 - s2) * U(0.55, 0.95)) + back * (b * U(0.05, 0.15))
        z2 = z0 + hm * U(0.64, 0.8)
        t2 = U(0.66, 0.8)
        column(c2, a * s2, b * s2, z1 - 1.5, z2, t2, alt, U(0.08, 0.16),
               with_lid=rng.random() < shelf * 0.7, n=(rng.choice((7, 8)) if big else None))
        s3 = s2 * t2 * U(0.86, 1.0)
        c3 = c2 + sd * (-sg2 * a * (s2 * t2 - s3) * U(0.3, 0.9)) + back * (b * s2 * U(0.0, 0.1))
        crown(c3, a * s3, b * s3, z2 - 1.5, zt, crown_k, mat, alt, lid_p)
        return z2

    def flank(sg, dist, dback, a):
        """posicao do flanco; se cair numa zona proibida (avoid) tenta o outro lado, senao desiste"""
        for s_ in (sg, -sg):
            c = c0 + sd * (s_ * dist) + back * dback
            if avoid is None or not avoid(c.x, c.y, a):
                return c
        return None

    base = r * U(1.35, 1.7)
    if kind == "spire":
        mountain(c0, 1.0, base, rng.choice(("tooth", "twin", "tooth")), t1=base_taper)
        a2 = base * U(0.55, 0.7)
        c = flank(rng.choice((-1, 1)), base * U(1.0, 1.3), base * U(0.0, 0.3), a2)
        if c is not None:
            mountain(c, U(0.5, 0.7), a2, rng.choice(("block", "twin")))
    elif kind == "horn":
        mountain(c0, 1.0, base, "horn", bw=U(0.6, 0.75), t1=base_taper)
        a2 = base * U(0.55, 0.7)
        c = flank(-side, base * U(1.0, 1.3), base * U(0.05, 0.3), a2)
        if c is not None:
            mountain(c, U(0.5, 0.68), a2, rng.choice(("block", "tooth")))
    elif kind == "wall":
        # paredao: 3-4 segmentos encostados, cada um com embasamento proprio (alturas e recuos diferentes ->
        # degraus e reentrancias na face) + bloco de crista em altura propria (crista serrilhada)
        a, b = r * U(2.2, 2.7), r * U(0.6, 0.75)
        k = rng.choice((3, 4))
        hi = rng.randrange(k)
        for i in range(k):
            u = -0.62 + 1.24 * (i + U(0.3, 0.7)) / k
            ci = c0 + sd * (a * u) + back * (b * U(-0.1, 0.3))
            ai, bi = a / k * U(1.2, 1.45), b * U(0.85, 1.1)
            z1 = z0 + h * U(0.42, 0.64)
            mi = m if (i + hi) % 2 else m2
            column(ci, ai, bi, zr, z1, base_taper or U(0.78, 0.88), mi, 0.06, n=rng.choice((6, 7, 8)),
                   visible_from=vis, with_lid=rng.random() < 0.4)
            zt = z0 + h * (1.0 if i == hi else U(0.72, 0.92))
            cc = ci + sd * (ai * U(-0.2, 0.2)) + back * (bi * U(0.05, 0.2))
            crown(cc, ai * U(0.5, 0.7), bi * U(0.55, 0.75), z1 - 2.0, zt,
                  rng.choice(("block", "tooth", "block", "twin")), mi, m2 if mi == m else m, 0.25)
    elif kind == "range":
        # cordilheira baixa e comprida: embasamento em talude (base 1.6x o topo) + crista quase horizontal de
        # 3-4 blocos com topos inclinados (sem silos): le como horizonte, nao como fileira de torres
        a, b = r * 1.6, r * U(0.8, 0.95)       # raio da base = 1.6x o do topo (talude)
        mat = m2 if rng.random() < 0.5 else m
        alt = m if mat == m2 else m2
        z1 = z0 + h * U(0.55, 0.7)
        column(c0, a, b, zr, z1, base_taper or 0.62, mat, 0.04, n=9, visible_from=vis, rings=2,
               with_lid=rng.random() < 0.6)
        k = rng.choice((3, 4))
        for i in range(k):
            u = -0.55 + 1.1 * (i + U(0.3, 0.7)) / k
            ci = c0 + sd * (r * 0.9 * u) + back * (b * U(0.05, 0.3))
            zt = z0 + h * U(0.84, 1.0)
            gs = U(-0.18, 0.18)
            column(ci, r * 1.2 / k * U(0.9, 1.15), b * 0.5 * U(0.8, 1.0), z1 - 2.0, zt, U(0.72, 0.85),
                   alt if i % 2 else mat, 0.0, n=rng.choice((6, 7)), slope=tuple((sd * gs).xy),
                   with_lid=rng.random() < 0.35, chamfer=U(1.0, 2.5))
    elif kind == "dominant":
        # macico dominante: embasamento largo com patamar -> ombro em degraus com topos inclinados subindo pela
        # crista -> chifre alto no outro lado -> queda abrupta com contraforte (silhueta de pico, nunca um tubo)
        A, B = r * U(1.95, 2.2), r * U(1.25, 1.45)
        sg = side
        mat = m2 if rng.random() < 0.5 else m
        alt = m if mat == m2 else m2
        zb1 = shelf_z if shelf_z is not None else z0 + h * U(0.3, 0.38)
        column(c0, A, B, zr, zb1, base_taper or U(0.8, 0.88), mat, 0.02, n=9, visible_from=vis, rings=3,
               with_lid=shelf_z is None)
        grad = min(0.85, (h * 0.13) / (A * 0.36))
        xs = (0.95, 0.6, 0.25)
        zs = (0.5, 0.64, 0.78)
        for i in range(3):
            ci = c0 + sd * (sg * A * xs[i]) + back * (B * U(0.5, 0.62))
            sl = sd * (-sg * grad)
            column(ci, A * U(0.3, 0.36), B * U(0.42, 0.52), zb1 - 2.0, z0 + h * zs[i] * U(0.96, 1.03), U(0.8, 0.9),
                   alt if i % 2 else mat, 0.0, n=rng.choice((6, 7)), slope=tuple(sl.xy),
                   with_lid=rng.random() < 0.3, chamfer=U(1.0, 2.5))
        cp = c0 + sd * (-sg * A * 0.22) + back * (B * 0.6)
        zc = z0 + h * 0.74
        column(cp, A * 0.44, B * 0.52, zb1 - 2.0, zc, U(0.8, 0.88), mat, 0.05, n=7, with_lid=False, chamfer=2.0)
        crown(cp + back * (B * 0.05), A * U(0.33, 0.37), B * U(0.4, 0.46), zc - 2.0, z0 + h, "horn", mat, alt)
        cq = c0 + sd * (-sg * A * 0.78) + back * (B * 0.45)
        column(cq, A * 0.24, B * 0.4, zb1 - 2.0, z0 + h * U(0.5, 0.58), U(0.75, 0.85), alt, 0.12, n=6,
               with_lid=rng.random() < 0.4, chamfer=1.5)
        _LAST_PEAK.update(shelf_z=zb1, front=tuple((c0 + f * (B * 0.95)).xy), wall=tuple((c0 + f * (B * 0.1)).xy),
                          face=tuple(f.xy), side=sg)
    elif kind == "saddle":
        mountain(c0, 1.0, r * U(1.2, 1.5), rng.choice(("block", "twin")), shelf=0.6, lid_p=0.4)
    else:  # mesa: degraus largos com patamares de grama, coroa chata e quebrada
        mountain(c0, 1.0, base * U(1.0, 1.15), rng.choice(("block", "twin")), shelf=0.9, lid_p=0.8, t1=base_taper)
        a2 = base * U(0.6, 0.75)
        c = flank(side, base * U(0.9, 1.2), base * U(0.1, 0.35), a2)
        if c is not None:
            mountain(c, U(0.62, 0.82), a2, "block", shelf=0.8, lid_p=0.7)
    return kind

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