# fm_props_kit - pecas de ambientacao low-poly (lanternas por no, mineracao, vida da vila) + validador de posicao.
# Usado por fm_props e fm_mine. Regras: bevel 0 nas pecas pequenas (orcamento de triangulos), PMB limita as
# variantes tonais por objeto (orcamento de MeshParts no Roblox), toda peca que atrapalha a passagem tem col_box.
import math, random
from mathutils import Vector, Matrix, Euler, Quaternion
import fm_lib
from fm_lib import MB, D, S, col_box, light, resample, point_in_poly
from fm_parts import Frame, P3
import fm_layout as L

F0 = L.FLOOR

# materiais novos (so os que nao existem): madeira pintada de vermelho (dinamite) e carvao/minerio escuro
fm_lib.MATS.setdefault("Wood_Red", (S(150, 44, 34), 0.8, 0.0, 0, None, 0.08))
fm_lib.MATS.setdefault("Coal_Rock", ((0.030, 0.029, 0.032), 0.95, 0.0, 0, None, 0.10))

WARM = (1.0, 0.60, 0.26)


def V(x, y, z=0.0):
    return Vector((x, y, z))


# ------------------------------------------------------------------ orcamento de MeshParts
BASE_REMAP = {"Wood_Light": "Wood_Plank", "Bark": "Wood_Dark", "Leather": "Wood_Dark", "Leaf_Palm": "Leaf_Pine_Light"}


class PMB(MB):
    """MB com orcamento de MeshParts (1 MeshPart por material por objeto no Roblox):
    - teto de variantes tonais por familia (vmax=1: UMA variante sorteada por objeto; a variacao aparece ENTRE
      objetos, sem multiplicar malhas);
    - paleta enxuta por objeto: materiais raros viram o material vizinho da paleta (remap)"""

    def __init__(self, name, collection, rng=None, vmax=1, remap=None):
        super().__init__(name, collection, rng)
        self.vmax = vmax
        self.remap = dict(BASE_REMAP)
        self.remap.update(remap or {})

    def _mi_for(self, m):
        return super()._mi_for(self.remap.get(m, m))

    def _variant_names(self, m):
        n = self.vcount.get(m, 0)
        cap = {1: fm_lib.VARIANT_T2 - 1, 2: fm_lib.VARIANT_T3 - 1}.get(self.vmax, n)
        self.vcount[m] = min(n, cap)
        try:
            return super()._variant_names(m)
        finally:
            self.vcount[m] = n


class F3:
    """referencial 3D (posicao + yaw + inclinacao): p() e r() em coords locais -> mundo"""

    def __init__(self, loc, yaw=0.0, roll=0.0, pitch=0.0):
        self.M = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(pitch, 4, "Y") \
            @ Matrix.Rotation(roll, 4, "X")
        self.R = self.M.to_3x3()

    def p(self, x, y, z=0.0):
        return self.M @ Vector((x, y, z))

    def r(self, rx=0.0, ry=0.0, rz=0.0):
        return (self.R @ Euler((rx, ry, rz)).to_matrix()).to_euler()

    def d(self, x, y, z=0.0):
        return self.R @ Vector((x, y, z))


def axis_euler(axis, spin=0.0):
    """Euler que leva o +Z local para 'axis' (girando 'spin' em torno dele)"""
    q = Vector(axis).normalized().to_track_quat("Z", "Y")
    return (q @ Quaternion((0, 0, 1), spin)).to_euler()


# ------------------------------------------------------------------ cristais (prisma de 5 lados + ponta)
def crystal(mb, base, h, r, axis=(0, 0, 1), m="Crystal_Blue", spin=0.0):
    ax = Vector(axis).normalized()
    e = axis_euler(ax, spin)
    base = Vector(base)
    mb.cyl(r, h * 0.7, base + ax * h * 0.35, e, m, 5, r2=r * 0.9, bevel=0.0)
    mb.cyl(r * 0.9, h * 0.3, base + ax * h * 0.85, e, m, 5, r2=0.03, bevel=0.0)


def crystals(mb, loc, s, rng, n=4, m="Crystal_Blue", up=(0, 0, 1), spread=0.75, m2=None):
    """tufo de cristais: um central alto e satelites inclinados para fora (up = normal da superficie)"""
    up = Vector(up).normalized()
    t1 = up.orthogonal().normalized()
    t2 = up.cross(t1)
    loc = Vector(loc)
    for i in range(n):
        a = rng.uniform(0, math.tau)
        rr = 0.0 if i == 0 else rng.uniform(0.35, 1.0) * spread * s
        off = (t1 * math.cos(a) + t2 * math.sin(a)) * rr
        tilt = rng.uniform(0.0, 0.15) if i == 0 else rng.uniform(0.3, 0.7)
        ax = (up + (t1 * math.cos(a) + t2 * math.sin(a)) * math.tan(tilt)).normalized()
        h = s * (rng.uniform(2.3, 3.0) if i == 0 else rng.uniform(1.1, 2.0))
        mm = m2 if (m2 and i and rng.random() < 0.35) else m
        crystal(mb, loc + off - up * 0.15, h, s * rng.uniform(0.34, 0.46) * (1.2 if i == 0 else 1.0), ax, mm,
                rng.uniform(0, 6))


def ore_bits(mb, loc, rad, n, rng, m="Coal_Rock", smin=0.35, smax=0.8, z=None):
    """cascalho de minerio (icosaedros achatados)"""
    x, y, z0 = loc
    for i in range(n):
        a = rng.uniform(0, math.tau)
        r = rad * math.sqrt(rng.random())
        s = rng.uniform(smin, smax)
        mb.rock((x + math.cos(a) * r, y + math.sin(a) * r, z0 + s * 0.2), (s * 1.3, s, s * 0.7),
                m if rng.random() > 0.3 else "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 6)), jitter=0.3)


# ------------------------------------------------------------------ lanternas (variantes por tipo de no)
def lamp(mb, c, name=None, e=160, s=1.0, color=WARM, frame="Metal_Dark"):
    """lanterna de caixa: vidro emissivo, base, 2 montantes e chapeu piramidal (c = centro do vidro)"""
    c = Vector(c)
    mb.box((1.2 * s, 1.2 * s, 0.22 * s), c + V(0, 0, -0.82 * s), (0, 0, 0), frame, 0.0)
    mb.box((0.88 * s, 0.88 * s, 1.35 * s), c, (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.14 * s, 0.14 * s, 1.45 * s), c + V(sx * 0.47 * s, sy * 0.47 * s, 0), (0, 0, 0), frame, 0.0)
    mb.cyl(0.95 * s, 0.55 * s, c + V(0, 0, 0.97 * s), (0, 0, math.pi / 4), frame, 4, r2=0.14 * s, bevel=0.0)
    if name:
        light(name, "POINT", c, e, color, 0.35)
    return c


def hang_lamp(mb, top, drop, name=None, e=160, s=1.0):
    """lanterna pendurada por corrente curta a partir de 'top'; devolve o centro (o fundo fica ~drop+1,9 abaixo)"""
    top = Vector(top)
    mb.rod(top, top - V(0, 0, drop), 0.07, "Metal_Dark", 4)
    return lamp(mb, top - V(0, 0, drop + 1.05 * s), name, e, s)


def cage_lamp(mb, top, name=None, e=150, drop=0.6):
    """lanterna de gaiola da mina: cilindro de vidro com aros de ferro e gancho"""
    top = Vector(top)
    c = top - V(0, 0, drop + 0.95)
    mb.rod(top, top - V(0, 0, drop), 0.07, "Metal_Dark", 4)
    mb.cyl(0.42, 1.2, c, (0, 0, 0), "Lantern_Glow", 6, bevel=0.0)
    for dz in (-0.62, 0.0, 0.62):
        mb.cyl(0.52, 0.12, c + V(0, 0, dz), (0, 0, 0), "Metal_Dark", 6, bevel=0.0)
    mb.cyl(0.55, 0.3, c + V(0, 0, 0.8), (0, 0, 0), "Metal_Dark", 6, r2=0.18, bevel=0.0)
    if name:
        light(name, "POINT", c, e, (1.0, 0.56, 0.24), 0.3)
    return c


def post_lamp(mb, x, y, z, yaw, name=None, h=6.2, arm=1.9, e=170, foot="Stone_Dark"):
    """poste de madeira com braco: a lanterna PENDURA do braco com o fundo >= 6 acima do piso (sem cabecada)"""
    F = Frame(x, y, z, yaw)
    mb.box((1.3, 1.3, 0.9), F.p(0, 0, 0.45), F.r(0, 0, 0.3), foot, 0.1)
    top = h + 2.2
    if arm > 0:
        top = max(top, 9.1)          # lanterna pendurada: fundo ~6,2 acima do piso
    mb.box((0.72, 0.72, top - 0.6), F.p(0, 0, 0.6 + (top - 0.6) / 2), F.r(), "Wood_Dark", 0.06)
    if arm > 0:
        mb.box((arm + 0.5, 0.45, 0.5), F.p(arm / 2, 0, top - 0.3), F.r(), "Wood_Dark", 0.0)
        mb.beam(F.p(0.2, 0, top - 1.5), F.p(arm * 0.6, 0, top - 0.5), 0.3, 0.3, "Wood_Dark", 0.0)
        return hang_lamp(mb, F.p(arm, 0, top - 0.55), 0.35, name, e)
    return lamp(mb, F.p(0, 0, top + 0.9), name, e)


def low_post_lamp(mb, x, y, z, yaw, name=None, e=160, z_top=None):
    """poste baixo de pedra + madeira com lanterna em cima (topo total <= z_top): nao tampa visadas"""
    F = Frame(x, y, z, yaw)
    zt = (z_top if z_top is not None else z + 6.0) - z
    mb.box((1.5, 1.5, 1.4), F.p(0, 0, 0.7), F.r(0, 0, 0.2), "Stone_Dark", 0.12)
    mb.box((0.8, 0.8, zt - 3.6), F.p(0, 0, 1.4 + (zt - 3.6) / 2), F.r(), "Wood_Dark", 0.06)
    return lamp(mb, F.p(0, 0, zt - 1.53), name, e)


def sconce(mb, p, nrm, name=None, e=150):
    """arandela: placa de madeira na parede + mao-francesa de ferro + lanterna pendurada (p = ponto na parede)"""
    p = Vector(p)
    n = Vector((nrm[0], nrm[1], 0)).normalized()
    yaw = math.atan2(n.y, n.x)
    mb.box((0.25, 0.9, 1.8), p + n * 0.12, (0, 0, yaw), "Wood_Dark", 0.0)
    mb.beam(p + n * 0.2 + V(0, 0, 0.6), p + n * 1.5 + V(0, 0, 0.6), 0.22, 0.26, "Metal_Dark", 0.0)
    mb.beam(p + n * 0.2 - V(0, 0, 0.6), p + n * 1.0 + V(0, 0, 0.5), 0.16, 0.16, "Metal_Dark", 0.0)
    return hang_lamp(mb, p + n * 1.35 + V(0, 0, 0.45), 0.25, name, e, 0.85)   # fundo ~0,7 abaixo de p


def string_lights(mb, a, b, z, h=9.4, sag=1.4, n=5, name=None, e=220, rng=None):
    """varal de lampioes entre dois postes (cruzamentos): corda em catenaria com lampioes pequenos"""
    rng = rng or random.Random(3)
    a, b = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
    for q in (a, b):
        mb.box((1.2, 1.2, 0.8), q + V(0, 0, 0.4), (0, 0, rng.uniform(0, 1)), "Stone_Dark", 0.1)
        mb.box((0.7, 0.7, h), q + V(0, 0, h / 2 + 0.3), (0, 0, rng.uniform(-0.1, 0.1)), "Wood_Dark", 0.06)
        mb.box((0.95, 0.95, 0.3), q + V(0, 0, h + 0.45), (0, 0, 0), "Wood_Dark", 0.0)
    pts = []
    k = 10
    for i in range(k + 1):
        t = i / k
        pts.append(a.lerp(b, t) + V(0, 0, h - 0.2 - sag * 4 * t * (1 - t)))
    mb.tube(pts, 0.07, "Rope", 4)
    for i in range(n):
        t = (i + 1) / (n + 1)
        c = a.lerp(b, t) + V(0, 0, h - 0.2 - sag * 4 * t * (1 - t))
        mb.rod(c, c - V(0, 0, 0.35), 0.04, "Metal_Dark", 3)
        g = c - V(0, 0, 0.85)
        mb.cyl(0.36, 0.7, g, (0, 0, 0), "Lantern_Glow", 6, r2=0.28, bevel=0.0)
        mb.cyl(0.32, 0.16, g + V(0, 0, 0.42), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
    if name:
        mid = a.lerp(b, 0.5) + V(0, 0, h - 1.4 - sag)
        light(name, "POINT", mid, e, WARM, 1.2)


def toro(mb, loc, yaw, name=None, s=0.85):
    """toro de pedra (lado do Naruto): usa o do kit dos portais; se nao existir, poste baixo"""
    try:
        import fm_portal_kit as K
        K.toro(mb, loc, s, "Stone_Light", "Stone_Dark", yaw=yaw, name=name)
    except Exception:
        low_post_lamp(mb, loc[0], loc[1], loc[2], yaw, name)


# ------------------------------------------------------------------ ferramentas
def pickaxe(mb, a, b, hd, s=1.0, head="Metal_Iron", handle="Wood_Light"):
    """picareta: cabo de a (ponta de baixo) a b (topo); hd = direcao da cabeca (perpendicular ao cabo)"""
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    hd = Vector(hd)
    hd = (hd - ax * hd.dot(ax)).normalized()
    mb.beam(a, b + ax * 0.15 * s, 0.17 * s, 0.17 * s, handle, 0.0)
    for sg in (-1, 1):
        mb.beam(b, b + hd * sg * 1.0 * s - ax * 0.3 * s, 0.2 * s, 0.24 * s, head, 0.0)


def shovel(mb, a, b, s=1.0, blade="Metal_Iron", handle="Wood_Light"):
    """pa: lamina em a (baixo), cabo ate b"""
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    mb.beam(a + ax * 0.9 * s, b, 0.15 * s, 0.15 * s, handle, 0.0)
    mb.beam(a, a + ax * 1.0 * s, 0.9 * s, 0.1 * s, blade, 0.0)
    side = ax.cross(V(0, 0, 1))
    side = side.normalized() if side.length > 0.1 else V(1, 0, 0)
    mb.beam(b - side * 0.32 * s, b + side * 0.32 * s, 0.13 * s, 0.13 * s, handle, 0.0)


def sword(mb, a, b, s=1.0):
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    side = ax.cross(V(0, 0, 1))
    side = side.normalized() if side.length > 0.1 else V(1, 0, 0)
    grip = a + ax * 0.8 * s
    mb.beam(a, grip, 0.16 * s, 0.16 * s, "Leather", 0.0)
    mb.beam(grip - side * 0.55 * s, grip + side * 0.55 * s, 0.18 * s, 0.22 * s, "Metal_Brass", 0.0)
    mb.beam(grip, b, 0.34 * s, 0.07 * s, "Metal_Iron", 0.0, roll=0.0)


def leaning_tools(mb, p, nrm, rng, kinds=("pick", "shovel")):
    """ferramentas encostadas numa parede (p no pe da parede, nrm = normal para fora)"""
    p = Vector(p)
    n = Vector((nrm[0], nrm[1], 0)).normalized()
    t = V(-n.y, n.x, 0)
    for i, k in enumerate(kinds):
        base = p + n * rng.uniform(1.0, 1.3) + t * (i * 0.9 - 0.4)
        top = p + n * 0.35 + t * (i * 0.9 - 0.4 + rng.uniform(-0.3, 0.3)) + V(0, 0, 3.4)
        if k == "pick":
            pickaxe(mb, base, top, t)
        else:
            shovel(mb, base, top)


# ------------------------------------------------------------------ caixotes, barris, sacos
def crate(mb, loc, s, yaw, m="Wood_Plank", band="Wood_Dark", lid=True, rng=None):
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    if lid:
        mb.box((s, s, s), F.p(0, 0, s / 2), F.r(), m, 0.05)
    else:
        th = 0.2
        mb.box((s, s, th), F.p(0, 0, th / 2), F.r(), m, 0.0)
        for sx in (-1, 1):
            mb.box((th, s, s), F.p(sx * (s - th) / 2, 0, s / 2), F.r(), m, 0.0)
            mb.box((s - 2 * th, th, s), F.p(0, sx * (s - th) / 2, s / 2), F.r(), m, 0.0)
    for dz in (0.3, s - 0.3):
        mb.box((s + 0.1, s + 0.1, 0.26), F.p(0, 0, dz), F.r(), band, 0.0)
    return F


def open_crate_crystals(mb, loc, s, yaw, rng, m="Crystal_Blue"):
    x, y, z = loc
    crate(mb, loc, s, yaw, lid=False)
    mb.box((s * 0.85, s * 0.85, 0.3), (x, y, z + s * 0.72), (0, 0, yaw), "Coal_Rock", 0.0)
    crystals(mb, (x, y, z + s * 0.8), s * 0.52, rng, 5, m)


def keg(mb, loc, r=1.0, h=2.3, m="Wood_Plank", band="Metal_Dark"):
    """barril low-poly (2 troncos de cone + 2 aros)"""
    x, y, z = loc
    mb.cyl(r, h * 0.5, (x, y, z + h * 0.25), (0, 0, 0), m, 8, r2=r * 1.1, bevel=0.0)
    mb.cyl(r * 1.1, h * 0.5, (x, y, z + h * 0.75), (0, 0, 0), m, 8, r2=r, bevel=0.0)
    for zz in (0.3, h - 0.3):
        mb.cyl(r * 1.06 + 0.05, 0.2, (x, y, z + zz), (0, 0, 0), band, 8, bevel=0.0)


def sack(mb, loc, rng, s=1.0, m="Cloth_Canvas", lying=False):
    x, y, z = loc
    if lying:
        a = rng.uniform(0, math.tau)
        mb.cyl(0.75 * s, 1.7 * s, (x, y, z + 0.6 * s), (D(90), 0, a), m, 6, r2=0.55 * s, bevel=0.0)
        return
    mb.cyl(0.8 * s, 1.35 * s, (x, y, z + 0.67 * s), (rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), rng.uniform(0, 1)),
           m, 6, r2=0.62 * s, bevel=0.0)
    mb.cyl(0.36 * s, 0.4 * s, (x, y, z + 1.5 * s), (0, 0, 0), m, 6, r2=0.2 * s, bevel=0.0)


def rope_coil(mb, loc, r=0.8):
    x, y, z = loc
    mb.cyl(r, 0.25, (x, y, z + 0.13), (0, 0, 0), "Rope", 8, bevel=0.0)
    mb.cyl(r * 0.85, 0.25, (x, y, z + 0.38), (0, 0, 0.2), "Rope", 8, bevel=0.0)


def log_pile(mb, loc, yaw, rng, n=6, ln=4.2, m="Bark"):
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    k = 0
    row = 0
    while k < n:
        cnt = max(1, 3 - row)
        for i in range(cnt):
            if k >= n:
                break
            r = rng.uniform(0.42, 0.55)
            yy = (i - (cnt - 1) / 2) * 1.05
            mb.cyl(r, ln * rng.uniform(0.85, 1.05), F.p(rng.uniform(-0.3, 0.3), yy, r + row * 0.85),
                   F.r(0, D(90), 0), m, 6, bevel=0.0)
            k += 1
        row += 1
    for sy in (-1, 1):
        mb.box((0.3, 0.3, 2.4), F.p(0, sy * 1.9, 1.2), F.r(), "Wood_Dark", 0.0)


def ingot_pallet(mb, loc, yaw, rng, layers=3):
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    for sy in (-0.9, 0.0, 0.9):
        mb.box((3.0, 0.5, 0.3), F.p(0, sy, 0.15), F.r(), "Wood_Dark", 0.0)
    for sx in (-1.1, 0.0, 1.1):
        mb.box((0.7, 2.4, 0.2), F.p(sx, 0, 0.4), F.r(), "Wood_Plank", 0.0)
    for L_ in range(layers):
        along = L_ % 2 == 0
        for i in range(3 if L_ < layers - 1 else 2):
            off = (i - 1) * 0.72
            px, py = (0, off) if along else (off, 0)
            m = "Metal_Brass" if (L_ == layers - 1 and i == 0) else "Metal_Iron"
            rot = F.r(0, 0, 0 if along else D(90))
            mb.cyl(0.46, 2.2, F.p(px, py, 0.8 + L_ * 0.5), (rot[0] + 0, rot[1] + D(90), rot[2]), m, 4, r2=0.36,
                   bevel=0.0)


def tool_rack(mb, F, rng, kinds=("pick", "pick", "shovel", "pick"), swords=0, s=1.0):
    """cavalete de madeira (2 montantes + 2 travessas) com ferramentas encostadas (F: +y local = frente)"""
    w = (1.2 * len(kinds) + 0.8 + swords * 1.0) * s
    for sx in (-1, 1):
        mb.box((0.5 * s, 0.5 * s, 3.6 * s), F.p(sx * w / 2, 0, 1.8 * s), F.r(), "Wood_Dark", 0.0)
    for z in (0.9, 3.0):
        mb.box((w + 0.4, 0.35 * s, 0.35 * s), F.p(0, 0.1, z * s), F.r(), "Wood_Dark", 0.0)
    items = list(kinds) + ["sword"] * swords
    for i, k in enumerate(items):
        xx = -w / 2 + 0.8 * s + i * ((w - 1.2 * s) / max(1, len(items) - 1))
        a = F.p(xx + rng.uniform(-0.1, 0.1), 0.95 * s, 0.05)
        b = F.p(xx, 0.35 * s, 3.45 * s)
        if k == "pick":
            pickaxe(mb, a, b, F.p(1, 0) - F.p(0, 0), s)
        elif k == "shovel":
            shovel(mb, a, b, s)
        else:
            sword(mb, a, b, s)


# ------------------------------------------------------------------ carrinho de mina low-poly
def cart(mb, loc, yaw, rng, load="crystal", roll=0.0, m_body="Metal_Iron"):
    """carrinho de mina (~300 tris); load: 'crystal' | 'ore' | None; roll != 0 -> tombado de lado"""
    F = F3(loc, yaw, roll)
    mb.box((3.2, 2.0, 0.3), F.p(0, 0, 1.05), F.r(), "Metal_Dark", 0.0)
    mb.cyl(1.75, 1.6, F.p(0, 0, 2.05), F.r(0, 0, math.pi / 4), m_body, 4, r2=2.12, bevel=0.0)
    for sx in (-1, 1):
        mb.box((0.25, 2.8, 0.28), F.p(sx * 1.45, 0, 2.86), F.r(), "Metal_Dark", 0.0)
        for sy in (-1, 1):
            mb.cyl(0.6, 0.3, F.p(sx * 1.05, sy * 1.15, 0.6), F.r(D(90), 0, 0), "Metal_Dark", 8, bevel=0.0)
    if load:
        heap = "Coal_Rock" if load == "ore" else "Cliff_Rock_Dark"
        mb.cyl(1.95, 0.55, F.p(0, 0, 3.12), F.r(0, 0, math.pi / 4), heap, 4, r2=0.9, bevel=0.0)
        if load == "crystal":
            up = F.d(0, 0, 1)
            crystals(mb, F.p(0.2, 0.1, 3.0), 0.9, rng, 6, "Crystal_Blue", up=up, spread=1.1)
    else:
        mb.box((2.6, 2.6, 0.08), F.p(0, 0, 2.84), F.r(0, 0, 0), "Metal_Dark", 0.0)
    return F


def rail_stub(mb, pts, gauge=2.6, step=1.7, z=None, m_sl="Wood_Dark", m_r="Metal_Iron", jitter=0.05, rng=None):
    """trilho leve (dormentes sem chanfro + 2 barras varridas) para desvios e toco de trilho"""
    rng = rng or random.Random(9)
    pts = [P3(p) for p in pts]
    if z is not None:
        pts = [V(p.x, p.y, z) for p in pts]
    sl = resample(pts, step)
    for i, p in enumerate(sl):
        j = min(i + 1, len(sl) - 1)
        k = max(i - 1, 0)
        t = sl[j] - sl[k]
        a = math.atan2(t.y, t.x)
        mb.box((0.8, gauge + 1.5, 0.28), (p.x, p.y, p.z + 0.14), (0, 0, a + rng.uniform(-jitter, jitter)), m_sl, 0.0)
    fine = resample(pts, 0.9)
    prof = [(-0.16, 0.28), (0.16, 0.28), (0.16, 0.58), (-0.16, 0.58)]
    for s in (-1, 1):
        off = []
        for i, p in enumerate(fine):
            j = min(i + 1, len(fine) - 1)
            k = max(i - 1, 0)
            t = (fine[j] - fine[k]).normalized()
            off.append(p + V(-t.y, t.x, 0) * s * gauge / 2)
        mb.sweep(off, prof, m_r, True)


def bumper(mb, p, t, gauge=2.6):
    """para-choque de fim de linha: trave de madeira + 2 escoras de ferro"""
    p = Vector(p)
    t = Vector((t[0], t[1], 0)).normalized()
    a = math.atan2(t.y, t.x)
    s = V(-t.y, t.x, 0)
    mb.box((1.1, gauge + 1.6, 1.3), p + t * 0.6 + V(0, 0, 1.0), (0, 0, a), "Wood_Dark", 0.08)
    for sg in (-1, 1):
        mb.beam(p - t * 1.2 + s * sg * gauge / 2 + V(0, 0, 0.4), p + t * 0.5 + s * sg * gauge / 2 + V(0, 0, 1.5),
                0.4, 0.4, "Metal_Dark", 0.0)
        mb.box((0.5, 0.5, 1.8), p + t * 1.3 + s * sg * 1.6 + V(0, 0, 0.9), (0, 0, a), "Wood_Dark", 0.0)


# ------------------------------------------------------------------ pecas da vila
def bench_log(mb, c, yaw, ln=3.6):
    mb.cyl(0.55, ln, V(c[0], c[1], c[2] + 0.55), (0, D(90), yaw), "Bark", 6, bevel=0.0)
    mb.box((ln * 0.9, 0.7, 0.12), V(c[0], c[1], c[2] + 1.08), (0, 0, yaw), "Wood_Plank", 0.0)


def campfire(mb, loc, rng, name=None):
    """fogueira: anel de pedras, toras cruzadas, chama emissiva e brasas + luz"""
    x, y, z = loc
    for i in range(7):
        a = i / 7 * math.tau + rng.uniform(-0.15, 0.15)
        mb.rock((x + math.cos(a) * 1.5, y + math.sin(a) * 1.5, z + 0.2), (0.8, 0.65, 0.55), "Stone_Dark", 1,
                (0, 0, a), jitter=0.2)
    mb.cyl(1.25, 0.14, (x, y, z + 0.08), (0, 0, 0), "Coal_Rock", 7, bevel=0.0)
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        mb.beam((x + math.cos(a) * 1.1, y + math.sin(a) * 1.1, z + 0.2), (x - math.cos(a) * 0.2, y - math.sin(a) * 0.2,
                z + 1.1), 0.36, 0.36, "Bark", 0.0)
    mb.cyl(0.62, 1.3, (x, y, z + 0.95), (0, 0, 0.3), "Forge_Emissive", 5, r2=0.05, bevel=0.0)
    mb.cyl(0.4, 0.9, (x + 0.35, y - 0.2, z + 0.75), (0.2, 0, 1.0), "Forge_Emissive", 5, r2=0.03, bevel=0.0)
    if name:
        light(name, "POINT", (x, y, z + 2.2), 260, (1.0, 0.5, 0.18), 0.6)


def well(mb, loc, yaw, rng):
    """poco com sarilho: bocal de pedra, 2 montantes, eixo com manivela, telhadinho e balde"""
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    n = 8
    R = 1.9
    for i in range(n):
        a = i / n * math.tau
        mb.box((1.1, 1.55, 1.9), F.p(math.cos(a) * R, math.sin(a) * R, 0.95), F.r(0, 0, a), "Stone_Light", 0.08)
    mb.cyl(1.45, 0.1, F.p(0, 0, 1.2), F.r(), "Water", 8, bevel=0.0)
    for sx in (-1, 1):
        mb.box((0.5, 0.5, 4.6), F.p(sx * 2.2, 0, 2.3), F.r(), "Wood_Dark", 0.0)
    mb.cyl(0.28, 4.8, F.p(0, 0, 3.8), F.r(0, D(90), 0), "Wood_Light", 6, bevel=0.0)
    mb.beam(F.p(2.6, 0, 3.8), F.p(2.6, 0, 3.0), 0.2, 0.2, "Metal_Dark", 0.0)
    mb.beam(F.p(2.6, 0, 3.0), F.p(2.9, 0.6, 3.0), 0.18, 0.18, "Metal_Dark", 0.0)
    for sy in (-1, 1):
        mb.box((5.6, 1.9, 0.18), F.p(0, sy * 0.85, 5.15 - 0.35), F.r(sy * D(-22), 0, 0), "Wood_Plank", 0.0)
    mb.rod(F.p(0.4, 0, 3.8), F.p(0.4, 0, 2.2), 0.05, "Rope", 3)
    keg(mb, tuple(F.p(0.4, 0, 1.45)), 0.4, 0.75, "Wood_Plank", "Metal_Dark")


def garden(mb, x0, y0, x1, y1, rng, gate_side="W"):
    """horta cercada: canteiros elevados de terra com fileiras de plantas, cerca baixa com portao"""
    z = F0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, d = x1 - x0, y1 - y0
    rows = max(2, int(d / 2.6))
    for r in range(rows):
        yy = y0 + 1.6 + r * (d - 3.2) / max(1, rows - 1)
        mb.box((w - 2.6, 1.5, 0.5), (cx, yy, z + 0.25), (0, 0, rng.uniform(-0.02, 0.02)), "Dirt_B", 0.0)
        k = int((w - 3.2) / 1.35)
        leaf = "Leaf_Pine_Light" if r % 2 == 0 else "Leaf_Palm"
        for i in range(k):
            xx = x0 + 1.9 + i * (w - 3.8) / max(1, k - 1)
            hh = rng.uniform(0.7, 1.1)
            if r % 2 == 0:
                mb.cyl(0.42, hh, (xx, yy, z + 0.5 + hh / 2), (0, 0, rng.uniform(0, 3)), leaf, 5, r2=0.06, bevel=0.0)
            else:
                mb.ico(0.42, (xx, yy, z + 0.75), leaf, 1, (1, 1, 0.8))
    # cerca baixa (postes + 2 ripas), abertura do portao no meio do lado escolhido
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    sides = {"S": (0, 1), "E": (1, 2), "N": (2, 3), "W": (3, 0)}
    gate = sides[gate_side]
    for i in range(4):
        a, b = V(*corners[i]), V(*corners[(i + 1) % 4])
        segs = [(a, b)]
        if (i, (i + 1) % 4) == gate:
            m1, m2 = a.lerp(b, 0.4), a.lerp(b, 0.6)
            segs = [(a, m1), (m2, b)]
        for p, q in segs:
            ln = (q - p).length
            npst = max(1, int(ln / 3.0))
            for k in range(npst + 1):
                c = p.lerp(q, k / npst)
                mb.box((0.45, 0.45, 2.2), (c.x, c.y, z + 1.1), (0, 0, rng.uniform(-0.1, 0.1)), "Wood_Dark", 0.0)
            ang = math.atan2(q.y - p.y, q.x - p.x)
            for hz in (0.8, 1.7):
                mb.box((ln, 0.22, 0.3), ((p.x + q.x) / 2, (p.y + q.y) / 2, z + hz), (0, 0, ang), "Wood_Light", 0.0)
            col_box("Props", (ln, 0.7, 2.6), ((p.x + q.x) / 2, (p.y + q.y) / 2, z + 1.3), (0, 0, ang))
    col_box("Props", (w - 2.6, d - 2.0, 0.5), (cx, cy, z + 0.25))


def clothesline(mb, a, b, rng, h=8.0):
    a, b = V(a[0], a[1], F0), V(b[0], b[1], F0)
    for q in (a, b):
        mb.box((0.5, 0.5, h + 0.4), q + V(0, 0, (h + 0.4) / 2), (0, 0, rng.uniform(-0.1, 0.1)), "Wood_Dark", 0.0)
        col_box("Props", (0.9, 0.9, h), (q.x, q.y, F0 + h / 2))
    pts = [a.lerp(b, i / 8) + V(0, 0, h - 0.8 * math.sin(math.pi * i / 8)) for i in range(9)]
    mb.tube(pts, 0.05, "Rope", 3)
    ln = (b - a).length
    ang = math.atan2(b.y - a.y, b.x - a.x)
    cloths = ("Cloth_Canvas", "Cloth_Red", "Cloth_Navy", "Cloth_Canvas", "Emblem_Cream")
    k = max(3, int(ln / 3.2))
    for i in range(k):
        t = (i + 0.7) / (k + 0.4)
        c = a.lerp(b, t) + V(0, 0, h - 0.8 * math.sin(math.pi * t))
        cw, ch = rng.uniform(1.2, 1.9), rng.uniform(1.3, 2.1)
        mb.box((cw, 0.08, ch), c - V(0, 0, ch / 2 + 0.05), (rng.uniform(-0.05, 0.05), 0, ang),
               cloths[i % len(cloths)], 0.0)


def altar(mb, loc, yaw, rng, name=None):
    """altar de mineiro: laje de pedra, estela com picareta entalhada, velas acesas e oferendas de cristal"""
    x, y, z = loc
    F = Frame(x, y, z, yaw)       # frente = -y local
    mb.box((3.6, 2.2, 0.6), F.p(0, 0, 0.3), F.r(0, 0, 0.04), "Stone_Dark", 0.1)
    mb.box((2.8, 1.6, 0.9), F.p(0, 0.1, 1.05), F.r(), "Stone_Light", 0.1)
    mb.box((1.6, 0.7, 2.6), F.p(0, 0.75, 2.4), F.r(0, 0, -0.03), "Stone_Light", 0.12)
    mb.box((1.9, 0.9, 0.35), F.p(0, 0.75, 3.8), F.r(), "Stone_Dark", 0.05)
    pickaxe(mb, F.p(-0.45, 0.3, 1.8), F.p(0.45, 0.3, 3.1), F.p(1, 0) - F.p(0, 0), 0.45, "Emblem_Cream",
            "Emblem_Cream")
    for i, (cx_, cy_) in enumerate(((-1.1, -0.5), (-0.7, -0.2), (1.0, -0.45), (1.2, 0.0))):
        hh = rng.uniform(0.45, 0.8)
        c = F.p(cx_, cy_, 1.5 + hh / 2)
        mb.cyl(0.13, hh, c, (0, 0, 0), "Emblem_Cream", 5, bevel=0.0)
        mb.cyl(0.09, 0.22, c + V(0, 0, hh / 2 + 0.11), (0, 0, 0), "Forge_Emissive", 4, r2=0.01, bevel=0.0)
    crystals(mb, F.p(0.1, -0.3, 1.5), 0.3, rng, 3, "Crystal_Blue")
    crystals(mb, F.p(-0.2, -1.5, 0.0), 0.35, rng, 3, "Crystal_Purple")
    if name:
        light(name, "POINT", F.p(0, -0.6, 2.4), 60, (1.0, 0.62, 0.3), 0.3)


def wheelbarrow(mb, loc, yaw, rng):
    x, y, z = loc
    F = F3((x, y, z), yaw)
    mb.cyl(0.62, 0.28, F.p(1.5, 0, 0.62), F.r(D(90), 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.cyl(1.1, 0.8, F.p(0.2, 0, 1.3), F.r(0, 0, math.pi / 4), "Wood_Plank", 4, r2=1.45, bevel=0.0)
    for sy in (-1, 1):
        mb.beam(F.p(1.5, sy * 0.35, 0.62), F.p(-2.1, sy * 0.75, 1.4), 0.22, 0.22, "Wood_Dark", 0.0)
        mb.beam(F.p(-0.9, sy * 0.65, 1.1), F.p(-0.9, sy * 0.7, 0.0), 0.2, 0.2, "Wood_Dark", 0.0)
    for i in range(2):
        pickaxe(mb, F.p(-1.6 + i * 0.3, -0.25 + i * 0.5, 1.6), F.p(1.4, -0.3 + i * 0.5, 2.1 + i * 0.25),
                F.d(0, 1, 0), 0.8)
    ore_bits(mb, tuple(F.p(0.2, 0, 1.7)), 0.5, 3, rng, "Coal_Rock", 0.3, 0.45)


def coal_bay(mb, F, rng, w=5.2, d=3.6, h=2.6):
    """baia de carvao de 3 lados (tabuas entre montantes) com monte de carvao e pa espetada; abre para -y local"""
    for sx in (-1, 1):
        for sy in (0, 1):
            mb.box((0.5, 0.5, h + 0.4), F.p(sx * w / 2, sy * d - d / 2, (h + 0.4) / 2), F.r(), "Wood_Dark", 0.0)
    for z in (0.5, 1.35, 2.2):
        mb.box((w, 0.25, 0.75), F.p(0, d / 2, z), F.r(), "Wood_Plank", 0.0)
        for sx in (-1, 1):
            mb.box((0.25, d, 0.75), F.p(sx * w / 2, 0, z), F.r(), "Wood_Plank", 0.0)
    mb.rock(F.p(0, 0.5, 1.2), (w * 0.92, d * 0.9, 3.4), "Coal_Rock", 1, F.r(0, 0, 0.2), jitter=0.35)
    mb.rock(F.p(0.2, -d / 2 + 0.2, 0.4), (w * 0.7, 2.0, 1.4), "Coal_Rock", 1, F.r(0, 0, -0.3), jitter=0.35)
    ore_bits(mb, tuple(F.p(0.4, -d / 2 - 0.8, 0.0)), 1.3, 5, rng, "Coal_Rock", 0.3, 0.6)
    shovel(mb, F.p(0.9, 0.2, 1.3), F.p(1.4, -0.8, 3.6))
    col_box("Props", (w + 0.6, d + 0.6, h + 0.4), tuple(F.p(0, 0, (h + 0.4) / 2)), F.r())


def bell_post(mb, x, y, z, yaw):
    F = Frame(x, y, z, yaw)
    mb.box((0.7, 0.7, 7.0), F.p(0, 0, 3.5), F.r(), "Wood_Dark", 0.0)
    mb.box((2.2, 0.45, 0.45), F.p(0.8, 0, 6.8), F.r(), "Wood_Dark", 0.0)
    mb.beam(F.p(0.2, 0, 5.6), F.p(1.1, 0, 6.6), 0.3, 0.3, "Wood_Dark", 0.0)
    mb.cyl(0.35, 0.9, F.p(1.5, 0, 6.05), F.r(), "Metal_Brass", 8, r2=0.72, bevel=0.0)
    mb.rod(F.p(1.5, 0, 5.5), F.p(1.5, 0, 3.0), 0.05, "Rope", 3)


def danger_sign(mb, x, y, z, yaw):
    """placa de perigo: poste + tabua com caveira e ossos cruzados (face para -y local)"""
    F = Frame(x, y, z, yaw)
    mb.box((0.5, 0.5, 5.6), F.p(0, 0.3, 2.8), F.r(), "Wood_Dark", 0.0)
    mb.box((2.6, 0.25, 2.2), F.p(0, 0, 4.3), F.r(0, 0.06, 0), "Wood_Red", 0.0)
    c = F.p(0, -0.2, 4.45)
    mb.ico(0.52, c, "Emblem_Cream", 1, (1, 0.7, 0.9))
    mb.box((0.62, 0.3, 0.3), c + V(0, 0, -0.5), F.r(), "Emblem_Cream", 0.0)
    for sg in (-1, 1):
        mb.beam(F.p(-0.85, -0.2, 3.55 + (0.9 if sg > 0 else 0)), F.p(0.85, -0.2, 3.55 + (0 if sg > 0 else 0.9)),
                0.2, 0.2, "Emblem_Cream", 0.0)


def dynamite_crates(mb, loc, yaw, rng):
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    for (cx_, cy_, cz_, s) in ((0, 0, 0, 1.8), (1.9, 0.2, 0, 1.6), (0.7, 0.1, 1.8, 1.5)):
        crate(mb, tuple(F.p(cx_, cy_, cz_)), s, yaw + rng.uniform(-0.15, 0.15), m="Wood_Red", band="Wood_Dark")
    for i in range(3):
        mb.cyl(0.16, 1.2, F.p(1.7 + i * 0.34, -1.1, 0.2), F.r(D(90), 0, 0.1), "Cloth_Red", 5, bevel=0.0)
    mb.box((0.9, 0.15, 0.2), F.p(2.05, -1.1, 0.2), F.r(), "Rope", 0.0)


def sorting_table(mb, F, rng):
    """mesa de triagem: tampo, pernas, peneira inclinada, pilhas de minerio e cristais separados"""
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.35, 0.35, 2.6), F.p(sx * 1.9, sy * 0.95, 1.3), F.r(), "Wood_Dark", 0.0)
    mb.box((4.4, 2.4, 0.3), F.p(0, 0, 2.7), F.r(), "Wood_Plank", 0.0)
    mb.box((2.0, 1.6, 0.15), F.p(-1.0, 0, 3.05), F.r(0.15, 0, 0), "Metal_Dark", 0.0)
    ore_bits(mb, tuple(F.p(-1.0, 0, 2.9)), 0.6, 3, rng, "Coal_Rock", 0.25, 0.4)
    crystals(mb, F.p(1.1, 0.2, 2.85), 0.3, rng, 3, "Crystal_Blue")
    keg(mb, tuple(F.p(0.4, 1.9, 0.0)), 0.55, 1.0, "Wood_Plank", "Metal_Dark")


def timber_stack(mb, F, rng, n=6, ln=6.0):
    """escoras empilhadas sobre calcos (reserva para o escoramento)"""
    for sx in (-1, 1):
        mb.box((0.6, 3.0, 0.5), F.p(sx * ln * 0.3, 0, 0.25), F.r(), "Wood_Dark", 0.0)
    k = 0
    for row in range(3):
        cnt = 3 - row
        for i in range(cnt):
            if k >= n:
                break
            yy = (i - (cnt - 1) / 2) * 0.95
            mb.box((ln * rng.uniform(0.9, 1.05), 0.8, 0.8), F.p(rng.uniform(-0.3, 0.3), yy, 0.9 + row * 0.8),
                   F.r(0, 0, rng.uniform(-0.04, 0.04)), "Wood_Light", 0.0)
            k += 1


def water_barrel(mb, loc, rng):
    x, y, z = loc
    keg(mb, loc, 0.95, 2.2, "Wood_Plank", "Metal_Dark")
    mb.cyl(0.9, 0.06, (x, y, z + 2.12), (0, 0, 0), "Water", 8, bevel=0.0)
    mb.beam((x - 0.3, y, z + 2.0), (x + 1.3, y + 0.3, z + 2.8), 0.1, 0.1, "Wood_Light", 0.0)
    mb.cyl(0.28, 0.25, (x - 0.35, y, z + 2.05), (0, 0, 0), "Metal_Iron", 6, bevel=0.0)


def tailings(mb, loc, yaw, rng, ln=9.0, s=1.0):
    """pilha de rejeito escorrendo da boca: montes de terra + cascalho + pedras (escorre para +x local)"""
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    k = s
    for i in range(5):
        t = i / 4
        sc = (1.0 - t * 0.6) * k
        mb.rock(F.p(t * ln, rng.uniform(-0.8, 0.8), 0.25), (5.2 * sc, 4.6 * sc, 3.4 * sc), "Dirt_B" if i % 2 else "Dirt",
                2 if i == 0 else 1, F.r(0, 0, rng.uniform(0, 1)), jitter=0.3)
    for i in range(10):
        t = rng.uniform(0.05, 1.1)
        q = F.p(t * ln, rng.uniform(-2.6, 2.6) * k, 0)
        s = rng.uniform(0.5, 1.1)
        mb.rock((q.x, q.y, z + s * 0.25), (s * 1.3, s, s * 0.8), "Cliff_Rock" if rng.random() > 0.4 else "Coal_Rock",
                1, (0, 0, rng.uniform(0, 6)), jitter=0.3)


# ------------------------------------------------------------------ validador de posicao
class Site:
    """pergunta 'posso por uma peca de raio r aqui?': fora das rotas do QA, das faixas pavimentadas, do trilho,
    das pegadas das construcoes, das colisoes ja existentes e das portas/NPCs"""
    SKIP_COL = ("COL_Floor", "COL_Terrace", "COL_MidLedge", "COL_BackMountain", "COL_WestCliff", "COL_EastCliff",
                "COL_MidWall", "COL_UpperWall", "COL_Konoha", "COL_Spawn")

    def __init__(self, buildings=True):
        import bpy
        import fm_buildings
        self.paths = [(pp, ww) for pp, ww in fm_buildings.PATHS.values()]
        self.ribbon = fm_buildings.ribbon
        self.routes = []
        try:
            import fm_qa
            for pts, z0 in fm_qa.routes().values():
                for a, b in zip(pts, pts[1:]):
                    self.routes.append((V(a[0], a[1]), V(b[0], b[1])))
        except Exception as ex:
            print("fm_props_kit: rotas do QA indisponiveis", ex)
        import fm_mine
        self.rail = [V(p.x, p.y) for p in fm_mine.rail_path(fm_mine.tunnel_frame())]
        self.rects = []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith("COL_") or o.get("col_kind") in ("Floor",):
                continue
            if o.name.startswith(self.SKIP_COL):
                continue
            self.rects.append((o.location.copy(), o.rotation_euler.z, o.scale.x / 2, o.scale.y / 2, o.name))
        self.boxes = []
        if buildings:
            for o in bpy.data.objects:
                if o.type != "MESH" or not o.name.startswith(("FORGE_", "BLD_", "WATER_Waterwheel")):
                    continue
                if o.name.startswith(("BLD_Bridges", "FORGE_Foundation_Dais", "FORGE_Pipes_Big", "FORGE_Hall_Roof",
                                      "FORGE_Catwalk", "FORGE_Roof_Vents")):
                    continue
                cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
                self.boxes.append((min(c.x for c in cs), min(c.y for c in cs), max(c.x for c in cs),
                                   max(c.y for c in cs), o.name))
        self.keep = []
        for o in bpy.data.objects:
            if o.type == "EMPTY" and o.name.startswith(("DOOR_", "NPC_", "INTERACT_", "PLAYER_INTERACT_", "MINE_Entrance",
                                                        "LEADERBOARD_")):
                self.keep.append(V(o.location.x, o.location.y))
        self.taken = []

    @staticmethod
    def dseg(p, a, b):
        ab = b - a
        l2 = ab.length_squared
        t = 0.0 if l2 == 0 else max(0.0, min(1.0, (p - a).dot(ab) / l2))
        return (p - (a + ab * t)).length

    def why(self, x, y, r, route=2.3, rail=2.8, path=0.4, door=4.5, taken=0.3, cols=0.3, boxes=0.8,
            ignore_rail=False, ignore_paths=False):
        p = V(x, y)
        for a, b in self.routes:
            if self.dseg(p, a, b) < r + route:
                return "rota(%.0f,%.0f)-(%.0f,%.0f)" % (a.x, a.y, b.x, b.y)
        if not ignore_rail:
            for a, b in zip(self.rail, self.rail[1:]):
                if self.dseg(p, a, b) < r + rail:
                    return "trilho"
        if not ignore_paths:
            for pp, ww in self.paths:
                if point_in_poly(x, y, self.ribbon(pp, ww + 2 * (r + path))):
                    return "caminho(%.0f,%.0f)" % (pp[0][0], pp[0][1])
        for q in self.keep:
            if (p - q).length < r + door:
                return "porta"
        for (cx, cy, rr) in self.taken:
            if (p - V(cx, cy)).length < r + rr + taken:
                return "ocupado"
        for (c, a, hx, hy, nm) in self.rects:
            dx, dy = x - c.x, y - c.y
            ca, sa = math.cos(-a), math.sin(-a)
            lx, ly = dx * ca - dy * sa, dx * sa + dy * ca
            ex, ey = max(abs(lx) - hx, 0.0), max(abs(ly) - hy, 0.0)
            if math.hypot(ex, ey) < r + cols:
                return "colisao:" + nm
        for (x0, y0, x1, y1, nm) in self.boxes:
            if x0 - r - boxes < x < x1 + r + boxes and y0 - r - boxes < y < y1 + r + boxes:
                return "construcao:" + nm
        return None

    def place(self, tag, x, y, r, search=5.0, **kw):
        """devolve (x, y) livre mais perto do desejado (espiral ate 'search'); None se nao couber"""
        best = None
        if self.why(x, y, r, **kw) is None:
            best = (x, y)
        else:
            k = 0.7
            while k <= search and best is None:
                n = max(8, int(k * 6))
                for i in range(n):
                    a = i / n * math.tau
                    xx, yy = x + math.cos(a) * k, y + math.sin(a) * k
                    if self.why(xx, yy, r, **kw) is None:
                        best = (xx, yy)
                        break
                k += 0.7
        if best is None:
            print("PLACE %-22s (%.1f,%.1f) r%.1f -> SEM LUGAR (%s)" % (tag, x, y, r, self.why(x, y, r, **kw)))
            return None
        if abs(best[0] - x) + abs(best[1] - y) > 0.01:
            print("PLACE %-22s (%.1f,%.1f) -> (%.1f,%.1f) [%s]" % (tag, x, y, best[0], best[1], self.why(x, y, r, **kw)))
        self.taken.append((best[0], best[1], r))
        return best

    def reserve(self, x, y, r):
        self.taken.append((x, y, r))
