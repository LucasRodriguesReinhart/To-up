# fm_veg_kit - kit de vegetacao estilizada da Vila-Forja (mid-poly, cartoon premium de Roblox)
# Todo o acabamento vem de GEOMETRIA (lobos, camadas, fundo escuro das saias) e de COR SOLIDA por material:
# no Roblox cada material vira uma MeshPart de cor unica, entao a variacao entre arvores sai da troca de paleta.
# Especies: abeto (fir), espruce alto (spruce), pinheiro jovem (young), pinheiro-guarda-chuva (umbrella),
# pinheiro ao vento (windswept), sakura, 2 arvores secas (dead_tree, dead_snag), tronco caido, arbustos,
# samambaias, plantas de pedra, tufos de grama e flores. lod: 0 = heroi (perto), 1 = medio, 2 = fundo.
import math, random
from mathutils import Vector, noise
import fm_lib

# ------------------------------------------------------------------ materiais novos (antes de make_materials)
# nome: (cor_linear, rough, metal, emissao, cor_emissao, variacao)
_M = fm_lib.MATS
_M.setdefault("Leaf_Shadow", ((0.018, 0.075, 0.050), 0.9, 0.0, 0, None, 0.10))      # fundo das saias
_M.setdefault("Leaf_Spruce", ((0.030, 0.135, 0.095), 0.85, 0.0, 0, None, 0.16))     # espruce azulado
_M.setdefault("Leaf_Spruce_Light", ((0.070, 0.250, 0.150), 0.85, 0.0, 0, None, 0.16))
_M.setdefault("Leaf_Pine_Warm", ((0.130, 0.285, 0.045), 0.85, 0.0, 0, None, 0.16))  # verde-oliva (jovens)
_M.setdefault("Leaf_Fern", ((0.085, 0.340, 0.050), 0.8, 0.0, 0, None, 0.14))
_M.setdefault("Leaf_Moss", ((0.120, 0.270, 0.035), 0.9, 0.0, 0, None, 0.14))
_M.setdefault("Leaf_Succulent", ((0.150, 0.330, 0.240), 0.7, 0.0, 0, None, 0.10))
_M.setdefault("Bark_Dead", ((0.230, 0.195, 0.160), 0.9, 0.0, 0, None, 0.12))
_M.setdefault("Grass_Tuft", ((0.180, 0.440, 0.045), 0.9, 0.0, 0, None, 0.12))
_M.setdefault("Flower_Yellow", ((0.950, 0.580, 0.050), 0.6, 0.0, 0, None, 0.0))
_M.setdefault("Flower_White", ((0.860, 0.850, 0.800), 0.6, 0.0, 0, None, 0.0))
_M.setdefault("Flower_Pink", ((0.900, 0.280, 0.440), 0.6, 0.0, 0, None, 0.0))
_M.setdefault("Flower_Blue", ((0.200, 0.380, 1.000), 0.5, 0.0, 0, None, 0.0))

# paletas (lado das saias, topo claro)
PAL_FIR = [("Leaf_Pine", "Leaf_Pine_Light"), ("Leaf_Pine", "Leaf_Pine_Warm"), ("Leaf_Spruce", "Leaf_Pine_Light")]
PAL_SPRUCE = [("Leaf_Spruce", "Leaf_Spruce_Light"), ("Leaf_Spruce", "Leaf_Pine")]
PAL_YOUNG = [("Leaf_Pine", "Leaf_Pine_Warm"), ("Leaf_Pine", "Leaf_Pine_Warm"), ("Leaf_Pine_Warm", "Leaf_Pine_Light"),
             ("Leaf_Spruce", "Leaf_Pine_Warm")]
PAL_UMB = [("Leaf_Pine", "Leaf_Pine_Warm"), ("Leaf_Spruce", "Leaf_Spruce_Light")]
FLOWERS = ["Flower_Yellow", "Flower_White", "Flower_Pink", "Flower_Blue"]


# ------------------------------------------------------------------ primitivas de malha
def _assign(mb, faces, m, tint=None):
    mi = mb._mi(m)
    t = mb.rng.uniform(-1, 1) if tint is None else tint
    for f in faces:
        f.material_index = mi
        f[mb.tint] = t
        f.smooth = False


def _tri(mb, a, b, c, out):
    try:
        out.append(mb.bm.faces.new((a, b, c)))
    except ValueError:
        pass


def _quad(mb, a, b, c, d, out):
    try:
        out.append(mb.bm.faces.new((a, b, c, d)))
    except ValueError:
        pass


def tier(mb, c, r, h, lobes, m, rng, rot=None, lob=0.26, droop=0.2, under=0.2, lean=(0.0, 0.0), bulge=None,
         asym=0.0, wind=0.0, under_m="Leaf_Shadow", jit=0.1):
    """camada de copa: cone com saia lobada (pontas caidas, vales recolhidos) e fundo concavo escuro.
    c = centro da base, h = altura ate o apice, bulge=(t, k): anel intermediario (copa fofa).
    asym/wind: a saia se estende a favor do vento (arvore torta). under=None: sem fundo (base enterrada
    ou escondida - economiza 2*lobes tris). tris = 4*lobes (8*lobes com bulge)"""
    bm = mb.bm
    cx, cy, cz = c
    rot = rng.uniform(0, math.tau) if rot is None else rot
    n = lobes * 2
    ring, mid = [], []
    for i in range(n):
        tip = i % 2 == 0
        a = rot + (i + rng.uniform(-jit, jit) * 1.6) * math.tau / n
        k = 1.0 + asym * math.cos(a - wind)
        rr = r * k * (1.0 if tip else 1.0 - lob) * rng.uniform(1.0 - jit, 1.0 + jit * 0.8)
        dz = -droop * h * (rng.uniform(0.75, 1.2) if tip else 0.2)
        ring.append(bm.verts.new((cx + math.cos(a) * rr, cy + math.sin(a) * rr, cz + dz)))
        if bulge:
            t, kk = bulge
            rm = rr * (1.0 - t) * kk
            mid.append(bm.verts.new((cx + lean[0] * t + math.cos(a) * rm, cy + lean[1] * t + math.sin(a) * rm,
                                     cz + dz * (1.0 - t) * 0.6 + h * t)))
    apex = bm.verts.new((cx + lean[0], cy + lean[1], cz + h))
    side, low = [], []
    top_ring = ring
    if bulge:
        for i in range(n):
            j = (i + 1) % n
            _quad(mb, ring[i], ring[j], mid[j], mid[i], side)
        top_ring = mid
    for i in range(n):
        _tri(mb, top_ring[i], top_ring[(i + 1) % n], apex, side)
    _assign(mb, side, m)
    if under is None:
        return
    cu = bm.verts.new((cx + lean[0] * under, cy + lean[1] * under, cz + h * under))
    for i in range(n):
        _tri(mb, ring[(i + 1) % n], ring[i], cu, low)
    _assign(mb, low, under_m or m)


def ttube(mb, pts, radii, m, n=5, cap0=False, cap1=True, tip=False, rot=0.0):
    """tubo afunilado ao longo da polilinha (transporte paralelo do referencial: sem torcao).
    tip=True fecha a ponta em bico (galho seco)."""
    bm = mb.bm
    pts = [Vector(p) for p in pts]
    N = len(pts)
    tans = []
    for i in range(N):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == N - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        tans.append(t.normalized())
    ref = Vector((1, 0, 0)) if abs(tans[0].z) > 0.9 else Vector((0, 0, 1))
    s = tans[0].cross(ref).normalized()
    rings = []
    faces = []
    for i, p in enumerate(pts):
        t = tans[i]
        s = (s - t * s.dot(t))
        if s.length < 1e-6:
            s = t.orthogonal()
        s.normalize()
        u = t.cross(s).normalized()
        if tip and i == N - 1:
            rings.append([bm.verts.new(p)])
            continue
        rr = radii[i]
        rings.append([bm.verts.new(p + (s * math.cos(rot + k * math.tau / n) + u * math.sin(rot + k * math.tau / n)) * rr)
                      for k in range(n)])
    for i in range(N - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(n):
            k2 = (k + 1) % n
            if len(r1) == 1:
                _tri(mb, r0[k], r0[k2], r1[0], faces)
            else:
                _quad(mb, r0[k], r0[k2], r1[k2], r1[k], faces)
    if cap0:
        try:
            faces.append(bm.faces.new(list(reversed(rings[0]))))
        except ValueError:
            pass
    if cap1 and len(rings[-1]) > 2:
        try:
            faces.append(bm.faces.new(rings[-1]))
        except ValueError:
            pass
    _assign(mb, faces, m)
    return rings


def dome(mb, c, r, hz, m, rng, seg=7, jit=0.14, rot=None, bottom=True, squash=(1.0, 1.0), rings=2):
    """domo facetado (moita, pedra, musgo). tris ~ 3*seg (rings=2)"""
    bm = mb.bm
    cx, cy, cz = c
    rot = rng.uniform(0, math.tau) if rot is None else rot
    s0 = rng.random() * 50
    levels = [(0.0, 1.0), (0.55, 0.82), (0.85, 0.48)][:rings] if rings <= 3 else [(0.0, 1.0), (0.55, 0.82)]
    rr_list = []
    for li, (fz, fr) in enumerate(levels):
        ring = []
        for i in range(seg):
            a = rot + (i + li * 0.5) * math.tau / seg
            nn = noise.noise(Vector((math.cos(a) * 1.7 + s0, math.sin(a) * 1.7, li * 0.9)))
            k = fr * (1.0 + nn * jit * 2.2 + rng.uniform(-jit, jit))
            ring.append(bm.verts.new((cx + math.cos(a) * r * k * squash[0], cy + math.sin(a) * r * k * squash[1],
                                      cz + hz * fz * (1.0 + rng.uniform(-jit, jit)))))
        rr_list.append(ring)
    top = bm.verts.new((cx + rng.uniform(-0.12, 0.12) * r, cy + rng.uniform(-0.12, 0.12) * r, cz + hz))
    faces = []
    for li in range(len(rr_list) - 1):
        r0, r1 = rr_list[li], rr_list[li + 1]
        for i in range(seg):
            j = (i + 1) % seg
            _tri(mb, r0[i], r0[j], r1[i], faces)
            _tri(mb, r0[j], r1[j], r1[i], faces)
    last = rr_list[-1]
    for i in range(seg):
        _tri(mb, last[i], last[(i + 1) % seg], top, faces)
    if bottom:
        try:
            faces.append(bm.faces.new(list(reversed(rr_list[0]))))
        except ValueError:
            pass
    _assign(mb, faces, m)


def spike(mb, base, tipp, r, m, n=3, rot=0.0):
    """espeto/lamina conica fechada (galho seco, lamina de grama, caule). tris = 2n-2+n"""
    ttube(mb, [base, tipp], [r, 0.0], m, n=n, cap0=True, cap1=False, tip=True, rot=rot)


# ------------------------------------------------------------------ arvores
def _und(u, lod, k):
    """fundo escuro da saia: no fundo (lod 2) so a camada de baixo tem fundo; as de cima ficam abertas
    (a saia de baixo cobre a vista; economiza 2*lobes tris por camada)"""
    return None if (lod >= 2 and k > 0) else u


def _canopy_z(h, k, T, z0, h_fac=0.17):
    return z0 + h * h_fac + h * (1 - h_fac) * 0.80 * (k / T) ** 0.92


def fir(mb, loc, h, rng, lod=1, pal=None, wind=None, lean_amt=0.0, bark="Bark"):
    """abeto classico: saias lobadas caidas em camadas, topo claro. wind=angulo -> versao torta ao vento"""
    x, y, z = loc
    pal = pal or rng.choice(PAL_FIR)
    T = (5, 4, 3)[lod]
    lobes = (6, 5, 3)[lod]
    tr = h * 0.048
    w = wind if wind is not None else rng.uniform(0, math.tau)
    la = lean_amt if wind is not None else rng.uniform(0.0, 0.035)
    lx, ly = math.cos(w) * la * h, math.sin(w) * la * h
    # tronco (curva leve) - ate dentro da copa
    top_t = z + h * 0.62
    if lod == 0 or wind is not None:
        ttube(mb, [(x, y, z - 0.6), (x + lx * 0.25, y + ly * 0.25, z + h * 0.25), (x + lx * 0.62, y + ly * 0.62, top_t)],
              [tr * 1.35, tr, tr * 0.55], bark, n=(6, 5, 4)[lod], cap1=False)
    else:
        ttube(mb, [(x, y, z - 0.6), (x + lx * 0.4, y + ly * 0.4, z + h * 0.4)], [tr * 1.3, tr * 0.8], bark,
              n=(6, 4, 3)[lod], cap1=False)
    if lod == 0:
        for k in range(3):   # raizes aparentes
            a = w + k * math.tau / 3 + rng.uniform(-0.4, 0.4)
            spike(mb, (x + math.cos(a) * tr * 0.4, y + math.sin(a) * tr * 0.4, z + h * 0.05),
                  (x + math.cos(a) * tr * 3.0, y + math.sin(a) * tr * 3.0, z - 0.3), tr * 0.55, bark, 3, rot=a)
    rot0 = rng.uniform(0, math.tau)
    for k in range(T):
        u = k / T
        zb = _canopy_z(h, k, T, z)
        f = (zb - z) / h
        th = (z + h - zb) if k == T - 1 else h * (0.36 - 0.07 * u) * rng.uniform(0.92, 1.08)
        r = h * (0.31 - 0.21 * u) * rng.uniform(0.9, 1.1)
        cxy = (x + lx * f, y + ly * f)
        m = pal[1] if (k == T - 1 or (k == T - 2 and rng.random() < 0.35)) else pal[0]
        lean = ((lx * 0.5, ly * 0.5) if k == T - 1 else (lx * 0.12, ly * 0.12))
        tier(mb, (cxy[0], cxy[1], zb), r, th, lobes, m, rng, rot=rot0 + k * 0.9 + rng.uniform(-0.3, 0.3),
             lob=0.26 if lod < 2 else 0.2, droop=0.2 if lod < 2 else 0.12, under=_und(0.22, lod, k), lean=lean,
             bulge=(0.42, 1.12) if (lod == 0 and k < 2) else None,
             asym=(0.32 if wind is not None else 0.08), wind=w)
    return tr * 1.35, h * 0.31


def spruce(mb, loc, h, rng, lod=1, pal=None):
    """espruce alto e estreito: muitas camadas curtas, pontas mais caidas, flecha no topo"""
    x, y, z = loc
    pal = pal or rng.choice(PAL_SPRUCE)
    T = (7, 5, 3)[lod]
    lobes = (5, 4, 3)[lod]
    tr = h * 0.036
    w = rng.uniform(0, math.tau)
    la = rng.uniform(0.0, 0.03)
    lx, ly = math.cos(w) * la * h, math.sin(w) * la * h
    if lod == 0:
        ttube(mb, [(x, y, z - 0.6), (x + lx * 0.4, y + ly * 0.4, z + h * 0.4), (x + lx * 0.8, y + ly * 0.8, z + h * 0.8)],
              [tr * 1.3, tr, tr * 0.5], "Bark", n=5, cap1=False)
    else:
        ttube(mb, [(x, y, z - 0.6), (x + lx * 0.4, y + ly * 0.4, z + h * 0.4)], [tr * 1.3, tr * 0.8], "Bark",
              n=(5, 4, 3)[lod], cap1=False)
    rot0 = rng.uniform(0, math.tau)
    for k in range(T):
        u = k / T
        zb = z + h * 0.12 + h * 0.80 * (u ** 0.95)
        f = (zb - z) / h
        th = (z + h - zb) if k == T - 1 else h * (0.24 - 0.05 * u) * rng.uniform(0.9, 1.1)
        r = h * (0.215 - 0.15 * u) * rng.uniform(0.9, 1.1)
        m = pal[1] if k >= T - 1 or (k == T - 3 and rng.random() < 0.3) else pal[0]
        tier(mb, (x + lx * f, y + ly * f, zb), r, th, lobes, m, rng, rot=rot0 + k * 1.3,
             lob=0.3 if lod < 2 else 0.2, droop=0.3 if lod < 2 else 0.15, under=_und(0.25, lod, k),
             lean=(lx * 0.2, ly * 0.2) if k < T - 1 else (lx * 0.5, ly * 0.5))
    return tr * 1.3, h * 0.22


def young_pine(mb, loc, h, rng, lod=1, pal=None):
    """pinheiro jovem/arbustivo: baixo e largo, saia de baixo quase no chao"""
    x, y, z = loc
    pal = pal or rng.choice(PAL_YOUNG)
    T = (3, 3, 2)[lod]
    lobes = (6, 5, 3)[lod]
    tr = h * 0.06
    ttube(mb, [(x, y, z - 0.5), (x, y, z + h * 0.5)], [tr * 1.2, tr * 0.6], "Bark", n=(5, 4, 3)[lod], cap1=False)
    rot0 = rng.uniform(0, math.tau)
    for k in range(T):
        u = k / T
        zb = z + h * 0.1 + h * 0.62 * u
        th = (z + h - zb) if k == T - 1 else h * (0.5 - 0.1 * u)
        r = h * (0.44 - 0.2 * u) * rng.uniform(0.9, 1.1)
        m = pal[1] if k == T - 1 else pal[0]
        tier(mb, (x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), zb), r, th, lobes, m, rng,
             rot=rot0 + k * 0.8, lob=0.28, droop=0.16, under=_und(0.2, lod, k), bulge=(0.45, 1.1) if lod == 0 else None)
    return tr * 1.2, h * 0.44


def umbrella_pine(mb, loc, h, rng, lod=1, pal=None, leaf=None):
    """pinheiro-guarda-chuva (estilo pinheiro japones): tronco torto, bracos, almofadas de copa achatadas.
    leaf=material unico das almofadas (ex.: Leaf_Sakura para a cerejeira)"""
    x, y, z = loc
    pal = pal or rng.choice(PAL_UMB)
    tr = h * 0.055
    w = rng.uniform(0, math.tau)
    bend = rng.uniform(0.08, 0.16) * h
    p0 = Vector((x, y, z - 0.6))
    p1 = Vector((x + math.cos(w) * bend * 0.3, y + math.sin(w) * bend * 0.3, z + h * 0.3))
    p2 = Vector((x + math.cos(w) * bend * 0.9 + math.cos(w + 1.8) * bend * 0.4,
                 y + math.sin(w) * bend * 0.9 + math.sin(w + 1.8) * bend * 0.4, z + h * 0.58))
    p3 = Vector((x + math.cos(w) * bend * 0.7, y + math.sin(w) * bend * 0.7, z + h * 0.8))
    tn = (6, 5, 4)[lod]
    ttube(mb, [p0, p1, p2, p3], [tr * 1.4, tr, tr * 0.8, tr * 0.5], "Bark", n=tn, cap1=False)
    pads = [(p3 + Vector((0, 0, h * 0.02)), h * 0.27, pal[1])]
    narms = (4, 3, 1)[lod]
    for i in range(narms):
        a = w + math.pi + (i - (narms - 1) / 2) * (4.6 / max(1, narms - 1)) + rng.uniform(-0.3, 0.3)
        base = p1.lerp(p2, rng.uniform(0.35, 0.95))
        L = h * rng.uniform(0.24, 0.34)
        end = base + Vector((math.cos(a) * L, math.sin(a) * L, h * rng.uniform(0.06, 0.18)))
        midp = base.lerp(end, 0.5) + Vector((0, 0, h * 0.05))
        ttube(mb, [base, midp, end], [tr * 0.6, tr * 0.45, tr * 0.3], "Bark", n=max(3, tn - 2), cap1=False)
        pads.append((end, h * rng.uniform(0.17, 0.23), pal[0]))
    for i, (pc, pr, m) in enumerate(pads):
        # almofada fofa (nuvem de agulhas) + tufo menor por cima nas maiores
        tier(mb, (pc.x, pc.y, pc.z - pr * 0.22), pr, pr * 0.95, (6, 5, 4)[lod], leaf or m, rng, lob=0.2, droop=0.28,
             under=0.22, bulge=(0.42, 1.5) if lod < 2 else None, jit=0.16)
        if lod == 0 and i == 0:
            tier(mb, (pc.x + rng.uniform(-0.2, 0.2) * pr, pc.y + rng.uniform(-0.2, 0.2) * pr, pc.z + pr * 0.35),
                 pr * 0.55, pr * 0.6, 5, leaf or pal[1], rng, lob=0.2, droop=0.25, under=0.2, bulge=(0.45, 1.4))
    return tr * 1.4, h * 0.35


def sakura_tree(mb, loc, h, rng, lod=0):
    """cerejeira: mesma estrutura do guarda-chuva com almofadas rosas mais cheias"""
    return umbrella_pine(mb, loc, h, rng, lod, pal=("Leaf_Sakura", "Leaf_Sakura"), leaf="Leaf_Sakura")


def tree(kind, mb, loc, h, rng, lod=1, wind=None):
    if kind == "fir":
        return fir(mb, loc, h, rng, lod)
    if kind == "spruce":
        return spruce(mb, loc, h, rng, lod)
    if kind == "young":
        return young_pine(mb, loc, h, rng, lod)
    if kind == "umbrella":
        return umbrella_pine(mb, loc, h, rng, lod)
    if kind == "windswept":
        return fir(mb, loc, h, rng, lod, wind=wind if wind is not None else rng.uniform(0, math.tau),
                   lean_amt=rng.uniform(0.13, 0.2))
    if kind == "dead":
        return dead_tree(mb, loc, h, rng, lod)
    if kind == "snag":
        return dead_snag(mb, loc, h, rng, lod)
    return fir(mb, loc, h, rng, lod)


# ------------------------------------------------------------------ arvores secas
def dead_tree(mb, loc, h, rng, lod=1):
    """arvore seca galhada: tronco torto e 3-4 galhos que se bifurcam (silhueta de contraste)"""
    x, y, z = loc
    tr = h * 0.06
    w = rng.uniform(0, math.tau)
    n = (6, 5, 4)[lod]
    pts = [Vector((x, y, z - 0.6))]
    for i, f in enumerate((0.3, 0.55, 0.78)):
        a = w + i * 1.3
        pts.append(Vector((x + math.cos(a) * h * 0.05 * (i + 1) * 0.6, y + math.sin(a) * h * 0.05 * (i + 1) * 0.6,
                           z + h * f)))
    ttube(mb, pts, [tr * 1.5, tr, tr * 0.7, tr * 0.4], "Bark_Dead", n=n, cap1=False)
    ttube(mb, [pts[-1], pts[-1] + Vector((math.cos(w) * h * 0.08, math.sin(w) * h * 0.08, h * 0.2))],
          [tr * 0.4, 0.0], "Bark_Dead", n=max(3, n - 2), cap1=False, tip=True)
    for k in range(3):   # raizes
        a = w + 0.5 + k * math.tau / 3
        spike(mb, (x, y, z + h * 0.06), (x + math.cos(a) * tr * 3.2, y + math.sin(a) * tr * 3.2, z - 0.3), tr * 0.6,
              "Bark_Dead", 3, rot=a)
    nb = (4, 3, 2)[lod]
    for i in range(nb):
        f = rng.uniform(0.35, 0.75)
        seg = min(2, int(f * 3))
        base = pts[seg + 1].lerp(pts[seg], rng.uniform(0.0, 0.5))
        a = w + math.pi * 0.6 + i * math.tau / nb + rng.uniform(-0.4, 0.4)
        L = h * rng.uniform(0.22, 0.34)
        mid = base + Vector((math.cos(a) * L * 0.55, math.sin(a) * L * 0.55, L * 0.35))
        end = mid + Vector((math.cos(a + 0.4) * L * 0.5, math.sin(a + 0.4) * L * 0.5, L * 0.45))
        ttube(mb, [base, mid, end], [tr * 0.45, tr * 0.28, 0.0], "Bark_Dead", n=max(3, n - 2), cap1=False, tip=True)
        if lod < 2:   # forquilha
            spike(mb, mid, mid + Vector((math.cos(a - 0.9) * L * 0.4, math.sin(a - 0.9) * L * 0.4, L * 0.3)),
                  tr * 0.2, "Bark_Dead", 3)
    return tr * 1.5, h * 0.3


def dead_snag(mb, loc, h, rng, lod=1):
    """pinheiro seco quebrado: fuste reto, topo lascado, tocos de galho apontando para baixo"""
    x, y, z = loc
    tr = h * 0.05
    w = rng.uniform(0, math.tau)
    top = Vector((x + math.cos(w) * h * 0.03, y + math.sin(w) * h * 0.03, z + h * 0.82))
    n = (7, 6, 4)[lod]
    ttube(mb, [(x, y, z - 0.6), (x, y, z + h * 0.4), top], [tr * 1.45, tr, tr * 0.72], "Bark_Dead", n=n, cap1=True)
    # lascas no topo quebrado
    for k in range(3):
        a = w + k * math.tau / 3 + rng.uniform(-0.3, 0.3)
        b = top + Vector((math.cos(a) * tr * 0.35, math.sin(a) * tr * 0.35, -0.1))
        spike(mb, b, b + Vector((math.cos(a) * tr * 0.3, math.sin(a) * tr * 0.3, h * rng.uniform(0.06, 0.18))),
              tr * 0.35, "Bark_Dead", 3, rot=a)
    for k in range(3):
        a = w + 1 + k * math.tau / 3
        spike(mb, (x, y, z + h * 0.05), (x + math.cos(a) * tr * 3.4, y + math.sin(a) * tr * 3.4, z - 0.3), tr * 0.6,
              "Bark_Dead", 3, rot=a)
    ns = (7, 5, 3)[lod]
    for k in range(ns):
        f = rng.uniform(0.3, 0.78)
        a = w + k * 2.4 + rng.uniform(-0.3, 0.3)
        rr = tr * (1.0 - f * 0.4)
        b = Vector((x + (top.x - x) * f + math.cos(a) * rr * 0.6, y + (top.y - y) * f + math.sin(a) * rr * 0.6,
                    z + h * 0.82 * f))
        L = h * rng.uniform(0.08, 0.2) * (1.2 - f)
        spike(mb, b, b + Vector((math.cos(a) * L, math.sin(a) * L, -L * rng.uniform(0.1, 0.5))), rr * 0.32,
              "Bark_Dead", 3, rot=a)
    return tr * 1.45, h * 0.12


def fallen_log(mb, loc, L, r, ang, rng, moss=True):
    """tronco caido (clareiras): ponta cortada + ponta lascada + musgo"""
    x, y, z = loc
    d = Vector((math.cos(ang), math.sin(ang), 0))
    s = Vector((-d.y, d.x, 0))
    a = Vector((x, y, z + r * 0.8)) - d * L / 2
    b = Vector((x, y, z + r * 0.8)) + d * L / 2
    m = a.lerp(b, 0.5) + s * rng.uniform(-0.4, 0.4) * r + Vector((0, 0, r * 0.1))
    ttube(mb, [a, m, b], [r, r * 0.95, r * 0.85], "Bark_Dead", n=6, cap0=True, cap1=False)
    for k in range(3):
        q = (s * math.cos(k * 2.1) + Vector((0, 0, 1)) * math.sin(k * 2.1)) * r * 0.5
        spike(mb, b + q - d * 0.2, b + q + d * rng.uniform(0.5, 1.3) * r, r * 0.35, "Bark_Dead", 3)
    if moss:
        c = a.lerp(b, rng.uniform(0.3, 0.6))
        dome(mb, (c.x, c.y, c.z + r * 0.62), r * 0.9, r * 0.45, "Leaf_Moss", rng, seg=6, squash=(1.3, 0.8), bottom=True)


# ------------------------------------------------------------------ vegetacao baixa
PAL_BUSH = [("Leaf_Pine_Light", "Leaf_Pine_Warm"), ("Leaf_Pine", "Leaf_Pine_Light"), ("Leaf_Fern", "Leaf_Pine_Warm"),
            ("Leaf_Spruce", "Leaf_Spruce_Light"), ("Leaf_Fern", "Leaf_Fern")]


def puff(mb, c, r, m, rng, lod=0, hz=1.0):
    """tufo de folhagem: almofada lobada fofa (borda recortada = le como folha, nao como pedra)"""
    tier(mb, c, r, r * hz * 0.82, 5 if lod == 0 else 4, m, rng, lob=0.26, droop=0.34, under=None,
         bulge=(0.52, 1.62 if lod == 0 else 1.45), jit=0.18)


def bush(mb, loc, s, rng, pal=None, n=None, lod=1):
    """moita de 2-4 tufos de tamanhos diferentes (o maior no centro, mais claro no alto)"""
    x, y, z = loc
    pal = pal or rng.choice(PAL_BUSH)
    n = n or rng.choice((2, 3, 3, 4))
    a0 = rng.uniform(0, math.tau)
    out = []
    for i in range(n):
        a = a0 + i * math.tau / max(1, n - 1) + rng.uniform(-0.4, 0.4)
        d = 0 if i == 0 else s * rng.uniform(0.55, 0.8)
        rr = s * (1.0 if i == 0 else rng.uniform(0.5, 0.72))
        c = (x + math.cos(a) * d, y + math.sin(a) * d, z + (0.1 * s if i == 0 else -0.05 * s))
        hz = rng.uniform(0.9, 1.2)
        puff(mb, c, rr, pal[1] if i == 0 else pal[0], rng, lod, hz)
        out.append((c, rr, rr * hz))
    return out


def flower_bush(mb, loc, s, rng, color=None):
    """moita com flores pousadas na folhagem (acento de cor controlado)"""
    color = color or rng.choice(FLOWERS)
    puffs = bush(mb, loc, s, rng, pal=rng.choice((("Leaf_Pine", "Leaf_Fern"), ("Leaf_Spruce", "Leaf_Pine"))), n=3,
                 lod=0)
    for (c, r, hz) in puffs:
        for i in range(rng.randint(1, 3)):
            a = rng.uniform(0, math.tau)
            q = rng.uniform(0.2, 0.62)
            zz = c[2] + hz * (1.0 - q ** 1.35) * 0.88
            blossom(mb, (c[0] + math.cos(a) * q * r, c[1] + math.sin(a) * q * r, zz), s * 0.24, color, rng)


def blossom(mb, c, r, m, rng):
    """flor de 5 petalas achatada (estrela com fundo)"""
    tier(mb, c, r, r * 0.35, 5, m, rng, lob=0.5, droop=-0.3, under=0.1, under_m=m, jit=0.05)


def fern(mb, loc, s, rng, m=None, m2=None):
    """samambaia: roseta de frondes arqueadas (saia com lobos profundos) + miolo erguido"""
    x, y, z = loc
    m = m or rng.choice(("Leaf_Fern", "Leaf_Fern", "Leaf_Pine"))
    m2 = m2 or ("Leaf_Pine_Warm" if m != "Leaf_Pine_Warm" else "Leaf_Fern")
    tier(mb, (x, y, z + s * 0.62), s * 1.1, s * 0.42, rng.choice((6, 7)), m, rng, lob=0.72, droop=1.4, under=0.4,
         jit=0.12)
    tier(mb, (x, y, z + s * 0.2), s * 0.55, s * 0.95, 5, m2, rng, lob=0.62, droop=0.35, under=0.2, jit=0.12)


def grove(mb, c, R, rng, pal=None, n=None, lod=1):
    """mancha de floresta de fundo: copas fundidas (domo baixo) + pontas de pinheiro de 2 camadas
    (1 camada alta em lod 2). Le como bosque denso de longe com poucos triangulos (12-24 por ponta)."""
    x, y, z = c
    pal = pal or rng.choice(PAL_SPRUCE + PAL_FIR)
    dome(mb, (x, y, z - 0.4), R, R * 0.42, pal[0], rng, seg=8, jit=0.22, bottom=False)
    n = n or max(4, int(R * 0.75))
    pts = []
    for i in range(n * 3):
        if len(pts) >= n:
            break
        a = rng.uniform(0, math.tau)
        d = R * 0.82 * math.sqrt(rng.random())
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        if any((px - qx) ** 2 + (py - qy) ** 2 < (R * 0.3) ** 2 for qx, qy, _ in pts):
            continue
        pts.append((px, py, d / R))
    for (px, py, q) in pts:
        hh = R * rng.uniform(1.3, 2.1) * (1.0 - 0.4 * q)
        rr = hh * rng.uniform(0.25, 0.31)
        bz = z + R * 0.42 * (1 - q * q) * 0.55
        m = pal[1] if rng.random() < 0.35 else pal[0]
        rot = rng.uniform(0, math.tau)
        # sem fundo: o domo de copas fundidas esconde a base (visto sempre de cima/de longe)
        tier(mb, (px, py, bz), rr, hh * 0.6, 4, pal[0], rng, rot=rot, lob=0.2, droop=0.26, under=None)
        tier(mb, (px, py, bz + hh * 0.42), rr * 0.66, hh * 0.58, 4 if lod < 2 else 3, m, rng, rot=rot + 0.8, lob=0.2,
             droop=0.24, under=0.3 if lod < 2 else None)


def grass_tuft(mb, loc, s, rng, m="Grass_Tuft", n=None):
    """tufo de laminas (tetraedros finos) abrindo em leque"""
    x, y, z = loc
    n = n or rng.randint(4, 6)
    a0 = rng.uniform(0, math.tau)
    for i in range(n):
        a = a0 + i * math.tau / n + rng.uniform(-0.3, 0.3)
        d = s * rng.uniform(0.05, 0.25)
        b = Vector((x + math.cos(a) * d, y + math.sin(a) * d, z - 0.1))
        hh = s * rng.uniform(0.7, 1.25)
        lean = s * rng.uniform(0.25, 0.55)
        t = b + Vector((math.cos(a) * lean, math.sin(a) * lean, hh))
        spike(mb, b, t, s * 0.13, m, 3, rot=a)


def flowers(mb, loc, s, rng, color=None):
    """touceira de flores do campo: laminas + 2-3 flores em hastes"""
    x, y, z = loc
    color = color or rng.choice(FLOWERS)
    grass_tuft(mb, loc, s * 0.8, rng, n=3)
    for i in range(rng.randint(2, 3)):
        a = rng.uniform(0, math.tau)
        d = s * rng.uniform(0.1, 0.4)
        b = Vector((x + math.cos(a) * d, y + math.sin(a) * d, z - 0.1))
        t = b + Vector((math.cos(a) * s * 0.2, math.sin(a) * s * 0.2, s * rng.uniform(0.8, 1.2)))
        spike(mb, b, t, s * 0.06, "Grass_Tuft", 3)
        blossom(mb, (t.x, t.y, t.z - s * 0.04), s * 0.28, color, rng)


def succulent(mb, loc, s, rng, m="Leaf_Succulent"):
    """roseta de folhas grossas apontando para cima (planta de pedra)"""
    x, y, z = loc
    tier(mb, (x, y, z), s, s * 0.35, 5, m, rng, lob=0.55, droop=-0.9, under=0.05, under_m=m)
    tier(mb, (x, y, z + s * 0.1), s * 0.55, s * 0.5, 4, m, rng, lob=0.5, droop=-0.8, under=0.05, under_m=m)


def rock_plant(mb, loc, s, rng, rock_m=None, rosettes=True):
    """planta de pedra: pedra facetada com capa de musgo caindo pela borda e rosetas nas frestas
    (rosettes=False nas bordas altas, onde a roseta nao e lida)"""
    x, y, z = loc
    rock_m = rock_m or rng.choice(("Cliff_Rock", "Cliff_Rock", "Stone_Light"))
    hz = s * rng.uniform(0.6, 0.9)
    dome(mb, (x, y, z - s * 0.12), s, hz, rock_m, rng, seg=6, jit=0.2, squash=(1.2, 0.9))
    tier(mb, (x + rng.uniform(-0.15, 0.15) * s, y, z - s * 0.12 + hz * 0.78), s * 0.8, s * 0.3, 5, "Leaf_Moss", rng,
         lob=0.35, droop=0.9, under=0.3, jit=0.15)
    for i in range(rng.randint(1, 2) if rosettes else 0):
        a = rng.uniform(0, math.tau)
        succulent(mb, (x + math.cos(a) * s * 1.1, y + math.sin(a) * s * 1.1, z - 0.05), s * rng.uniform(0.35, 0.5), rng)
    if rng.random() < 0.5:
        grass_tuft(mb, (x - s * 0.9, y + s * 0.4, z), s * 0.7, rng, n=3)


def boulder(mb, loc, s, rng, m="Cliff_Rock"):
    """pedra solta facetada (mais barata que o ico)"""
    x, y, z = loc
    dome(mb, (x, y, z - s * 0.2), s, s * rng.uniform(0.55, 0.85), m, rng, seg=rng.choice((5, 6, 7)), jit=0.22,
         squash=(rng.uniform(1.0, 1.35), rng.uniform(0.75, 1.0)))
