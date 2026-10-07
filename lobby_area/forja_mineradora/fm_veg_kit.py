# fm_veg_kit - kit de vegetacao estilizada da Vila-Forja (mid-poly, cartoon premium de Roblox)
# Todo o acabamento vem de GEOMETRIA (saias caidas, ombro convexo, fundo concavo escuro, domos, tufos) e de COR
# SOLIDA por material: no Roblox cada material vira uma MeshPart de cor unica. Paleta curta de proposito (cada
# material extra custa uma MeshPart por setor de streaming): folha (Leaf_Pine), topo iluminado (Leaf_Pine_Light,
# so nas faces do topo voltadas ao sol), fundo escuro (Leaf_Shadow), folhosa (Leaf_Broad), tronco (Bark_Dark),
# madeira seca (Bark_Dead), grama/samambaia (Grass_Tuft), rosa (Sakura_Pink: sakura e flores) e branco.
# Especies: pinheiro em camadas (fir / spruce / young, com altura livre opcional), pinheiro-guarda-chuva,
# folhosa de copa redonda (3-5 domos), sakura (3-5 tufos), arvores secas, tronco caido, arbustos, arbusto
# pendente de borda, samambaia, junco, tufos, flores, pedras e manchas de floresta de fundo.
# lod: 0 = heroi (perto), 1 = medio (bordas), 2 = fundo.
import math, random
from mathutils import Vector, Matrix, noise
import fm_lib
from fm_lib import S

# ------------------------------------------------------------------ materiais novos (antes de make_materials)
# nome: (cor_linear, rough, metal, emissao, cor_emissao, variacao)
_M = fm_lib.MATS
_M.setdefault("Leaf_Shadow", ((0.018, 0.075, 0.050), 0.9, 0.0, 0, None, 0.10))    # fundo das saias e copas
_M.setdefault("Leaf_Broad", (S(122, 160, 58), 0.85, 0.0, 0, None, 0.16))          # folhosa verde-amarelada
_M.setdefault("Bark_Dark", (S(86, 60, 46), 0.9, 0.0, 0, None, 0.12))              # tronco escuro
_M.setdefault("Bark_Dead", ((0.230, 0.195, 0.160), 0.9, 0.0, 0, None, 0.12))
_M.setdefault("Grass_Tuft", ((0.180, 0.440, 0.045), 0.9, 0.0, 0, None, 0.12))
_M.setdefault("Sakura_Pink", (S(255, 140, 191), 0.8, 0.0, 0, None, 0.08))        # rosa (1.0, 0.55, 0.75) sRGB
_M.setdefault("Flower_White", ((0.860, 0.850, 0.800), 0.6, 0.0, 0, None, 0.0))

LEAF, LIT, UNDER = "Leaf_Pine", "Leaf_Pine_Light", "Leaf_Shadow"
BARK = "Bark_Dark"
FLOWERS = ["Sakura_Pink", "Flower_White"]
# direcao PARA o sol (fm_scene.setup_sun: rot (50, 0, -32) graus) - o topo iluminado so recebe as faces voltadas a ele
SUN = Vector((-0.406, -0.650, 0.643)).normalized()


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


def _split_lit(faces, inner, k):
    """faces cuja normal (para fora de 'inner') aponta para o sol alem de k"""
    on, off = [], []
    for f in faces:
        f.normal_update()
        nn = f.normal
        if nn.dot(f.calc_center_median() - inner) < 0:
            nn = -nn
        (on if nn.dot(SUN) > k else off).append(f)
    return on, off


def skirt(mb, c, r, th, lobes, m, rng, rot=None, droop=20.0, lob=0.3, shoulder=0.5, under=0.14, under_m=UNDER,
          lean=(0.0, 0.0), jit=0.1, lit=None, lit_k=0.35, asym=0.0, wind=0.0):
    """camada de pinheiro com SAIA CAIDA: as pontas dos lobos pendem 'droop' graus abaixo da horizontal, os vaos
    ficam recolhidos e mais altos, o ombro (anel a 'shoulder' do raio) deixa o perfil convexo (nada de cone de
    papel) e o fundo concavo usa under_m (lado de baixo escuro). c = centro na altura do ombro-base, th = altura
    ate o apice. lit = material das faces voltadas ao sol (topo iluminado). under=None: sem fundo.
    tris = 6*lobes (+2*lobes com fundo); sem ombro 2*lobes (+2*lobes)"""
    bm = mb.bm
    cx, cy, cz = c
    rot = rng.uniform(0, math.tau) if rot is None else rot
    n = lobes * 2
    td = math.tan(math.radians(droop))
    ring, mid = [], []
    for i in range(n):
        tip = i % 2 == 0
        a = rot + (i + rng.uniform(-jit, jit) * 1.6) * math.tau / n
        k = 1.0 + asym * math.cos(a - wind)
        rr = r * k * (1.0 if tip else 1.0 - lob) * rng.uniform(1.0 - jit, 1.0 + jit * 0.8)
        dz = -rr * td * (rng.uniform(0.85, 1.2) if tip else 0.3)
        ring.append(bm.verts.new((cx + math.cos(a) * rr, cy + math.sin(a) * rr, cz + dz)))
        if shoulder:
            rm = rr * shoulder * (1.0 if tip else 1.1)
            mid.append(bm.verts.new((cx + lean[0] * 0.35 + math.cos(a) * rm, cy + lean[1] * 0.35 + math.sin(a) * rm,
                                     cz + th * (0.3 if tip else 0.34))))
    ap = bm.verts.new((cx + lean[0], cy + lean[1], cz + th))
    side = []
    top = ring
    if shoulder:
        for i in range(n):
            j = (i + 1) % n
            _quad(mb, ring[i], ring[j], mid[j], mid[i], side)
        top = mid
    for i in range(n):
        _tri(mb, top[i], top[(i + 1) % n], ap, side)
    if lit:
        on, off = _split_lit(side, Vector((cx + lean[0] * 0.2, cy + lean[1] * 0.2, cz + th * 0.1)), lit_k)
        _assign(mb, on, lit)
        _assign(mb, off, m)
    else:
        _assign(mb, side, m)
    if under is None:
        return
    cu = bm.verts.new((cx + lean[0] * under, cy + lean[1] * under, cz + th * under))
    low = []
    for i in range(n):
        _tri(mb, ring[(i + 1) % n], ring[i], cu, low)
    _assign(mb, low, under_m or m)


def tier(mb, c, r, h, lobes, m, rng, rot=None, lob=0.26, droop=0.2, under=0.2, lean=(0.0, 0.0), bulge=None,
         asym=0.0, wind=0.0, under_m=UNDER, jit=0.1):
    """almofada/tufo lobado (moita, tufo de sakura, samambaia, flor): cone com saia lobada, bulge=(t, k) = anel
    intermediario (almofada fofa). droop relativo a h. tris = 4*lobes (8*lobes com bulge; -2*lobes sem fundo)"""
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
        dz = -droop * h * (rng.uniform(0.75, 1.2) if tip else 0.2) * (1.0 + asym * max(0.0, math.cos(a - wind)))
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
    """domo facetado (pedra, musgo, massa de copas). tris ~ 3*seg (rings=2)"""
    bm = mb.bm
    cx, cy, cz = c
    rot = rng.uniform(0, math.tau) if rot is None else rot
    s0 = rng.random() * 50
    levels = [(0.0, 1.0), (0.55, 0.82), (0.85, 0.48)][:max(1, min(3, rings))]
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


def blob(mb, c, r, hz, m, rng, seg=6, under_m=UNDER, jit=0.12, squash=(1.0, 1.0), lit=None, lit_k=0.55):
    """copa de folhosa: elipsoide facetado e irregular (equador em c), com o fundo em under_m (lado de baixo
    escuro). tris = 6*seg"""
    bm = mb.bm
    cx, cy, cz = c
    rot = rng.uniform(0, math.tau)
    s0 = rng.random() * 50
    lv = [(-0.3, 0.74), (0.0, 1.0), (0.46, 0.8)]
    rings = []
    for li, (fz, fr) in enumerate(lv):
        ring = []
        for i in range(seg):
            a = rot + (i + li * 0.5) * math.tau / seg
            nn = noise.noise(Vector((math.cos(a) * 1.5 + s0, math.sin(a) * 1.5, li * 1.1)))
            k = fr * (1.0 + nn * jit * 2.0 + rng.uniform(-jit, jit))
            ring.append(bm.verts.new((cx + math.cos(a) * r * k * squash[0], cy + math.sin(a) * r * k * squash[1],
                                      cz + hz * fz + rng.uniform(-jit, jit) * hz * 0.3)))
        rings.append(ring)
    bot = bm.verts.new((cx, cy, cz - hz * 0.44))
    top = bm.verts.new((cx + rng.uniform(-0.1, 0.1) * r, cy + rng.uniform(-0.1, 0.1) * r, cz + hz * 0.82))
    low, side = [], []
    for i in range(seg):
        _tri(mb, rings[0][(i + 1) % seg], rings[0][i], bot, low)
    for li in range(2):
        r0, r1 = rings[li], rings[li + 1]
        for i in range(seg):
            j = (i + 1) % seg
            _tri(mb, r0[i], r0[j], r1[i], side)
            _tri(mb, r0[j], r1[j], r1[i], side)
    for i in range(seg):
        _tri(mb, rings[2][i], rings[2][(i + 1) % seg], top, side)
    if lit:
        on, off = _split_lit(side, Vector((cx, cy, cz)), lit_k)
        _assign(mb, on, lit)
        _assign(mb, off, m)
    else:
        _assign(mb, side, m)
    _assign(mb, low, under_m or m)


def spike(mb, base, tipp, r, m, n=3, rot=0.0):
    """espeto/lamina conica fechada (galho seco, lamina de grama, caule). tris = 2n-2+n"""
    ttube(mb, [base, tipp], [r, 0.0], m, n=n, cap0=True, cap1=False, tip=True, rot=rot)


def lean_new(mb, n0, base, ang, amt):
    """inclina (em torno do pe 'base') tudo o que foi criado no bmesh a partir do vertice n0: 'amt' radianos
    para o lado 'ang' (arvore inclinada para fora da borda)"""
    bm = mb.bm
    bm.verts.ensure_lookup_table()
    d = Vector((math.cos(ang), math.sin(ang), 0.0))
    R = Matrix.Rotation(amt, 3, Vector((-d.y, d.x, 0.0)))
    b = Vector(base)
    for v in bm.verts[n0:]:
        v.co = b + R @ (v.co - b)


# ------------------------------------------------------------------ pinheiros em camadas
# T = camadas por lod, L = lobos por lod, r0 = raio da saia de baixo (x h), droop = queda das pontas (graus),
# base = inicio da copa (x h), taper = reducao do raio ate o topo, span = fracao da copa ocupada pelas bases,
# th = altura da camada (x copa), sh = ombro, tr = raio do tronco (x h)
FORMS = {
    "fir":    dict(T=(4, 4, 3), L=(6, 5, 4), r0=0.30, droop=20.0, base=0.15, taper=0.68, span=0.74, th=0.42,
                   sh=0.5, tr=0.045),
    "spruce": dict(T=(6, 4, 3), L=(5, 5, 4), r0=0.22, droop=24.0, base=0.1, taper=0.74, span=0.8, th=0.30,
                   sh=0.55, tr=0.036),
    "young":  dict(T=(3, 3, 2), L=(6, 5, 4), r0=0.42, droop=16.0, base=0.06, taper=0.56, span=0.62, th=0.55,
                   sh=0.5, tr=0.055),
}


def pine(mb, loc, h, rng, lod=1, form="fir", clear=None, wind=None, lean_amt=0.0, lit=True, leaf=LEAF,
         bark=BARK, trunk_m=None):
    """pinheiro estilizado em camadas com saia caida, fundo escuro e topo levemente torto.
    clear = altura livre minima sob a copa (studs): a saia de baixo sobe e o tronco fica a mostra (jogador passa
    por baixo; no Roblox a copa nao some vista de dentro). wind/lean_amt = copa torta ao vento.
    retorna (raio do tronco, raio da copa, altura da base da copa acima do chao)"""
    x, y, z = loc
    P = FORMS[form]
    T, lobes = P["T"][lod], P["L"][lod]
    r0 = h * P["r0"] * rng.uniform(0.92, 1.08)
    if clear is not None:
        r0 *= 0.9
    droop = P["droop"] * rng.uniform(0.85, 1.15)
    td = math.tan(math.radians(droop))
    tr = h * P["tr"]
    zb = z + h * P["base"]
    if clear is not None:
        zb = max(zb, z + clear + r0 * td * 1.45)
    zt = z + h
    ch = zt - zb
    w = wind if wind is not None else rng.uniform(0, math.tau)
    lx, ly = math.cos(w) * lean_amt * h, math.sin(w) * lean_amt * h
    ta = rng.uniform(0, math.tau)                       # topo torto
    tl = h * rng.uniform(0.03, 0.06)
    tx, ty = math.cos(ta) * tl, math.sin(ta) * tl
    bark_m = trunk_m or bark
    # tronco (curva leve) ate dentro da copa
    tn = (6, 5, 3)[lod]
    if lod == 0 or clear is not None or wind is not None:
        ttube(mb, [(x, y, z - 0.6), (x + lx * 0.25, y + ly * 0.25, z + h * 0.3),
                   (x + lx * 0.6 + tx * 0.3, y + ly * 0.6 + ty * 0.3, z + h * 0.66)],
              [tr * 1.35, tr, tr * 0.55], bark_m, n=tn, cap1=False)
    else:
        ttube(mb, [(x, y, z - 0.6), (x + lx * 0.4, y + ly * 0.4, z + h * 0.42)], [tr * 1.3, tr * 0.8], bark_m,
              n=tn, cap1=False)
    if lod == 0:
        for k in range(3):   # raizes aparentes
            a = w + k * math.tau / 3 + rng.uniform(-0.4, 0.4)
            spike(mb, (x + math.cos(a) * tr * 0.4, y + math.sin(a) * tr * 0.4, z + h * 0.05),
                  (x + math.cos(a) * tr * 3.0, y + math.sin(a) * tr * 3.0, z - 0.3), tr * 0.55, bark_m, 3, rot=a)
    rot0 = rng.uniform(0, math.tau)
    for k in range(T):
        u = k / (T - 1) if T > 1 else 1.0
        zc = zb + ch * P["span"] * (u ** 0.92)
        r = r0 * (1.0 - P["taper"] * u) * rng.uniform(0.9, 1.1)
        top = k == T - 1
        th = (zt - zc) if top else ch * P["th"] * (1.0 - 0.3 * u) * rng.uniform(0.92, 1.08)
        f = (zc - z) / h
        cxy = (x + lx * f + tx * u * 0.5, y + ly * f + ty * u * 0.5)
        lean = (lx * 0.5 + tx, ly * 0.5 + ty) if top else (lx * 0.12 + tx * 0.2, ly * 0.12 + ty * 0.2)
        # ombro nas camadas grandes (nas 2 de cima ele quase nao aparece: economia de tris)
        shoulder = P["sh"] if ((lod == 0 and k < T - 2) or (lod == 1 and k == 0)) else None
        under = 0.14 if (lod < 2 or k == 0) else None
        # topo iluminado: so nas 2 camadas de cima e so nas faces voltadas ao sol (~10-13% da folhagem da arvore)
        lm = (LIT if lit and lod < 2 and k >= T - 2 else None)
        skirt(mb, (cxy[0], cxy[1], zc), r, th, lobes, leaf, rng, rot=rot0 + k * 0.9 + rng.uniform(-0.3, 0.3),
              droop=droop * (1.0 - 0.25 * u), lob=0.3 if lod < 2 else 0.22, shoulder=shoulder, under=under,
              lean=lean, lit=lm, lit_k=(0.22 if top else 0.5),
              asym=(0.3 if wind is not None else 0.06), wind=w)
    if lod < 2:
        # broto do topo torto (flecha)
        ap = Vector((x + lx + tx, y + ly + ty, zt))
        spike(mb, ap - Vector((0, 0, h * 0.05)), ap + Vector((tx * 0.9, ty * 0.9, h * 0.07)), h * 0.02,
              LIT if lit else leaf, 3)
    return tr * 1.3, r0, (zb - z) - r0 * td * 1.2


def fir(mb, loc, h, rng, lod=1, wind=None, lean_amt=0.0, clear=None, **kw):
    """compatibilidade: abeto classico"""
    return pine(mb, loc, h, rng, lod, "fir", clear=clear, wind=wind, lean_amt=lean_amt)


def spruce(mb, loc, h, rng, lod=1, clear=None, **kw):
    """compatibilidade: espruce alto e estreito"""
    return pine(mb, loc, h, rng, lod, "spruce", clear=clear)


def young_pine(mb, loc, h, rng, lod=1, **kw):
    """compatibilidade: pinheiro jovem, baixo e largo"""
    return pine(mb, loc, h, rng, lod, "young")


def umbrella_pine(mb, loc, h, rng, lod=1, clear=None, **kw):
    """pinheiro-guarda-chuva (estilo pinheiro japones): tronco torto, bracos e almofadas achatadas de saia caida"""
    x, y, z = loc
    tr = h * 0.055
    w = rng.uniform(0, math.tau)
    bend = rng.uniform(0.08, 0.16) * h
    p0 = Vector((x, y, z - 0.6))
    p1 = Vector((x + math.cos(w) * bend * 0.3, y + math.sin(w) * bend * 0.3, z + h * 0.3))
    p2 = Vector((x + math.cos(w) * bend * 0.9 + math.cos(w + 1.8) * bend * 0.4,
                 y + math.sin(w) * bend * 0.9 + math.sin(w + 1.8) * bend * 0.4, z + h * 0.58))
    p3 = Vector((x + math.cos(w) * bend * 0.7, y + math.sin(w) * bend * 0.7, z + h * 0.8))
    tn = (6, 5, 4)[lod]
    ttube(mb, [p0, p1, p2, p3], [tr * 1.4, tr, tr * 0.8, tr * 0.5], BARK, n=tn, cap1=False)
    pads = [(p3 + Vector((0, 0, h * 0.02)), h * 0.27, True)]
    narms = (4, 3, 2)[lod]
    lo = z + (clear if clear else 0.0)
    for i in range(narms):
        a = w + math.pi + (i - (narms - 1) / 2) * (4.6 / max(1, narms - 1)) + rng.uniform(-0.3, 0.3)
        base = p1.lerp(p2, rng.uniform(0.35, 0.95))
        Ln = h * rng.uniform(0.24, 0.34)
        end = base + Vector((math.cos(a) * Ln, math.sin(a) * Ln, h * rng.uniform(0.06, 0.18)))
        pr = h * rng.uniform(0.17, 0.23)
        end.z = max(end.z, lo + pr * 0.62)
        midp = base.lerp(end, 0.5) + Vector((0, 0, h * 0.05))
        ttube(mb, [base, midp, end], [tr * 0.6, tr * 0.45, tr * 0.3], BARK, n=max(3, tn - 2), cap1=False)
        pads.append((end, pr, False))
    for (pc, pr, top) in pads:
        skirt(mb, (pc.x, pc.y, pc.z), pr, pr * 0.7, (6, 5, 4)[lod], LEAF, rng, droop=24, lob=0.26,
              shoulder=0.55 if lod < 2 else None, under=0.12, lit=LIT if (top and lod < 2) else None, lit_k=0.35,
              jit=0.14)
    return tr * 1.4, h * 0.38, h * 0.3


def broadleaf(mb, loc, h, rng, lod=0, clear=5.5, leaf="Leaf_Broad"):
    """folhosa de copa redonda: tronco escuro e torto abrindo em bracos, 3-5 domos agrupados (o maior no alto),
    fundo escuro. A copa comeca acima de 'clear' (jogador passa por baixo). retorna (tronco, raio, base)"""
    x, y, z = loc
    tr = h * 0.05
    w = rng.uniform(0, math.tau)
    R = h * 0.34
    zc = z + max(clear + R * 0.62, h * 0.58)          # centro da copa (base dos domos >= clear)
    p0 = Vector((x, y, z - 0.5))
    p1 = Vector((x + math.cos(w) * h * 0.05, y + math.sin(w) * h * 0.05, z + (zc - z) * 0.55))
    p2 = Vector((x - math.cos(w) * h * 0.03, y - math.sin(w) * h * 0.03, zc - R * 0.1))
    ttube(mb, [p0, p1, p2], [tr * 1.5, tr, tr * 0.7], BARK, n=(6, 5, 4)[lod], cap1=False)
    if lod == 0:
        for k in range(3):
            a = w + 0.6 + k * math.tau / 3
            spike(mb, (x, y, z + h * 0.06), (x + math.cos(a) * tr * 3.0, y + math.sin(a) * tr * 3.0, z - 0.3),
                  tr * 0.6, BARK, 3, rot=a)
    n = (rng.choice((4, 5)), 3, 3)[lod]
    seg = (6, 6, 5)[lod]
    blob(mb, (p2.x, p2.y, zc + R * 0.3), R * 0.78, R * 1.05, leaf, rng, seg=seg)
    a0 = rng.uniform(0, math.tau)
    for i in range(n - 1):
        a = a0 + i * math.tau / (n - 1) + rng.uniform(-0.4, 0.4)
        d = R * rng.uniform(0.52, 0.7)
        rr = R * rng.uniform(0.5, 0.64)
        c = Vector((p2.x + math.cos(a) * d, p2.y + math.sin(a) * d, zc - R * rng.uniform(0.02, 0.2)))
        c.z = max(c.z, z + clear + rr * 0.5)
        ttube(mb, [p1.lerp(p2, 0.6), c - Vector((0, 0, rr * 0.2))], [tr * 0.5, tr * 0.3], BARK, n=4, cap1=False)
        blob(mb, c, rr, rr * 1.0, leaf, rng, seg=seg)
    return tr * 1.5, R * 1.25, zc - R * 0.55 - z


def sakura_tree(mb, loc, h, rng, lod=0, clear=5.5, **kw):
    """cerejeira: tronco escuro e torto que se abre em 2-3 bracos, com 3-5 tufos rosa lobados (Sakura_Pink).
    Os tufos ficam acima de 'clear' (jogador passa por baixo). retorna (tronco, raio da copa, base da copa)"""
    x, y, z = loc
    tr = h * 0.05
    w = rng.uniform(0, math.tau)
    b1, b2 = h * rng.uniform(0.06, 0.1), h * rng.uniform(0.05, 0.09)
    p0 = Vector((x, y, z - 0.5))
    p1 = Vector((x + math.cos(w) * b1, y + math.sin(w) * b1, z + h * 0.3))
    p2 = Vector((x + math.cos(w + 2.4) * b2, y + math.sin(w + 2.4) * b2, z + h * 0.52))
    tn = (6, 5, 4)[lod]
    ttube(mb, [p0, p1, p2], [tr * 1.45, tr, tr * 0.72], BARK, n=tn, cap1=False)
    if lod == 0:
        for k in range(3):
            a = w + 0.9 + k * math.tau / 3
            spike(mb, (x, y, z + h * 0.05), (x + math.cos(a) * tr * 3.2, y + math.sin(a) * tr * 3.2, z - 0.3),
                  tr * 0.6, BARK, 3, rot=a)
    nt = (rng.choice((4, 5)), 4, 3)[lod]
    tufts = []
    top = p2 + Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), h * 0.16))
    tufts.append((top, h * rng.uniform(0.25, 0.3)))
    a0 = rng.uniform(0, math.tau)
    for i in range(nt - 1):
        a = a0 + i * math.tau / (nt - 1) + rng.uniform(-0.35, 0.35)
        base = p1.lerp(p2, rng.uniform(0.55, 1.0))
        Ln = h * rng.uniform(0.26, 0.38)
        end = base + Vector((math.cos(a) * Ln, math.sin(a) * Ln, h * rng.uniform(0.1, 0.24)))
        rr = h * rng.uniform(0.18, 0.24)
        end.z = max(end.z, z + clear + rr * 0.55)
        mid = base.lerp(end, 0.5) + Vector((0, 0, h * rng.uniform(0.02, 0.07)))   # braco torto
        ttube(mb, [base, mid, end], [tr * 0.55, tr * 0.38, tr * 0.24], BARK, n=max(3, tn - 2), cap1=False)
        tufts.append((end, rr))
    for i, (c, rr) in enumerate(tufts):
        # tufo fofo (couve-flor): nuvem facetada redonda + 1-2 bolotas menores coladas embaixo/ao lado, que
        # quebram a silhueta sem as pontas de papel
        blob(mb, (c.x, c.y, c.z + rr * 0.2), rr * 0.9, rr * 0.95, "Sakura_Pink", rng, seg=(7, 6, 5)[lod],
             under_m="Sakura_Pink", jit=0.16, squash=(1.08, 0.96))
        if lod < 2:
            a1 = rng.uniform(0, math.tau)
            for j in range(2 if lod == 0 else 1):
                a = a1 + j * rng.uniform(2.0, 2.8)
                sr = rr * rng.uniform(0.46, 0.58)
                blob(mb, (c.x + math.cos(a) * rr * 0.62, c.y + math.sin(a) * rr * 0.62, c.z - rr * 0.08), sr, sr * 0.9,
                     "Sakura_Pink", rng, seg=5, under_m="Sakura_Pink", jit=0.18)
    return tr * 1.45, h * 0.42, clear


def tree(kind, mb, loc, h, rng, lod=1, wind=None, clear=None):
    if kind in ("fir", "spruce", "young"):
        return pine(mb, loc, h, rng, lod, form=kind, clear=clear)
    if kind == "umbrella":
        return umbrella_pine(mb, loc, h, rng, lod, clear=clear)
    if kind == "windswept":
        return pine(mb, loc, h, rng, lod, form="fir", clear=clear,
                    wind=wind if wind is not None else rng.uniform(0, math.tau), lean_amt=rng.uniform(0.12, 0.18))
    if kind == "broad":
        return broadleaf(mb, loc, h, rng, lod, clear=clear if clear is not None else 5.5)
    if kind == "sakura":
        return sakura_tree(mb, loc, h, rng, lod, clear=clear if clear is not None else 5.5)
    if kind == "dead":
        return dead_tree(mb, loc, h, rng, lod)
    if kind == "snag":
        return dead_snag(mb, loc, h, rng, lod)
    return pine(mb, loc, h, rng, lod)


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
        Ln = h * rng.uniform(0.22, 0.34)
        mid = base + Vector((math.cos(a) * Ln * 0.55, math.sin(a) * Ln * 0.55, Ln * 0.35))
        end = mid + Vector((math.cos(a + 0.4) * Ln * 0.5, math.sin(a + 0.4) * Ln * 0.5, Ln * 0.45))
        ttube(mb, [base, mid, end], [tr * 0.45, tr * 0.28, 0.0], "Bark_Dead", n=max(3, n - 2), cap1=False, tip=True)
        if lod < 2:   # forquilha
            spike(mb, mid, mid + Vector((math.cos(a - 0.9) * Ln * 0.4, math.sin(a - 0.9) * Ln * 0.4, Ln * 0.3)),
                  tr * 0.2, "Bark_Dead", 3)
    return tr * 1.5, h * 0.3, h


def dead_snag(mb, loc, h, rng, lod=1):
    """pinheiro seco quebrado: fuste reto, topo lascado, tocos de galho apontando para baixo"""
    x, y, z = loc
    tr = h * 0.05
    w = rng.uniform(0, math.tau)
    top = Vector((x + math.cos(w) * h * 0.03, y + math.sin(w) * h * 0.03, z + h * 0.82))
    n = (7, 6, 4)[lod]
    ttube(mb, [(x, y, z - 0.6), (x, y, z + h * 0.4), top], [tr * 1.45, tr, tr * 0.72], "Bark_Dead", n=n, cap1=True)
    for k in range(3 if lod < 2 else 2):   # lascas no topo quebrado
        a = w + k * math.tau / 3 + rng.uniform(-0.3, 0.3)
        b = top + Vector((math.cos(a) * tr * 0.35, math.sin(a) * tr * 0.35, -0.1))
        spike(mb, b, b + Vector((math.cos(a) * tr * 0.3, math.sin(a) * tr * 0.3, h * rng.uniform(0.06, 0.18))),
              tr * 0.35, "Bark_Dead", 3, rot=a)
    if lod < 2:
        for k in range(3):
            a = w + 1 + k * math.tau / 3
            spike(mb, (x, y, z + h * 0.05), (x + math.cos(a) * tr * 3.4, y + math.sin(a) * tr * 3.4, z - 0.3),
                  tr * 0.6, "Bark_Dead", 3, rot=a)
    ns = (7, 5, 3)[lod]
    for k in range(ns):
        f = rng.uniform(0.3, 0.78)
        a = w + k * 2.4 + rng.uniform(-0.3, 0.3)
        rr = tr * (1.0 - f * 0.4)
        b = Vector((x + (top.x - x) * f + math.cos(a) * rr * 0.6, y + (top.y - y) * f + math.sin(a) * rr * 0.6,
                    z + h * 0.82 * f))
        Ln = h * rng.uniform(0.08, 0.2) * (1.2 - f)
        spike(mb, b, b + Vector((math.cos(a) * Ln, math.sin(a) * Ln, -Ln * rng.uniform(0.1, 0.5))), rr * 0.32,
              "Bark_Dead", 3, rot=a)
    return tr * 1.45, h * 0.12, h


def fallen_log(mb, loc, Ln, r, ang, rng, moss=True):
    """tronco caido (clareiras): ponta cortada + ponta lascada + musgo"""
    x, y, z = loc
    d = Vector((math.cos(ang), math.sin(ang), 0))
    s = Vector((-d.y, d.x, 0))
    a = Vector((x, y, z + r * 0.8)) - d * Ln / 2
    b = Vector((x, y, z + r * 0.8)) + d * Ln / 2
    m = a.lerp(b, 0.5) + s * rng.uniform(-0.4, 0.4) * r + Vector((0, 0, r * 0.1))
    ttube(mb, [a, m, b], [r, r * 0.95, r * 0.85], "Bark_Dead", n=6, cap0=True, cap1=False)
    for k in range(3):
        q = (s * math.cos(k * 2.1) + Vector((0, 0, 1)) * math.sin(k * 2.1)) * r * 0.5
        spike(mb, b + q - d * 0.2, b + q + d * rng.uniform(0.5, 1.3) * r, r * 0.35, "Bark_Dead", 3)
    if moss:
        c = a.lerp(b, rng.uniform(0.3, 0.6))
        dome(mb, (c.x, c.y, c.z + r * 0.62), r * 0.9, r * 0.45, "Leaf_Broad", rng, seg=6, squash=(1.3, 0.8),
             bottom=True)


# ------------------------------------------------------------------ vegetacao baixa
PAL_BUSH = [("Leaf_Broad", LEAF), (LEAF, "Leaf_Broad"), ("Leaf_Broad", "Leaf_Broad"), (LEAF, LEAF)]


def puff(mb, c, r, m, rng, lod=0, hz=1.0, under=None):
    """tufo de folhagem: almofada lobada fofa (borda recortada = le como folha, nao como pedra)"""
    tier(mb, c, r, r * hz * 0.82, 5 if lod == 0 else 4, m, rng, lob=0.26, droop=0.34, under=under,
         bulge=(0.52, 1.62 if lod == 0 else 1.45), jit=0.18)


def bush(mb, loc, s, rng, pal=None, n=None, lod=1):
    """moita de 2-4 tufos de tamanhos diferentes (o maior no centro)"""
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
        puff(mb, c, rr, pal[0] if i == 0 else pal[1], rng, lod, hz)
        out.append((c, rr, rr * hz))
    return out


def edge_bush(mb, loc, s, out_ang, rng, m=LEAF, m2="Leaf_Broad", lod=1):
    """moita PENDENTE na borda de um topo de rocha: o tufo se estende para o vazio ('out_ang') e a saia desse
    lado cai pela quina (cortina de folhagem), com um tufo menor ao lado"""
    x, y, z = loc
    tier(mb, (x, y, z + s * 0.1), s, s * 0.7, 5 if lod < 2 else 4, m, rng, lob=0.3, droop=0.55, under=0.2,
         under_m=UNDER, bulge=(0.5, 1.5) if lod < 2 else None, asym=0.55, wind=out_ang, jit=0.18)
    if lod < 2 and rng.random() < 0.35:
        a = out_ang + rng.choice((-1, 1)) * rng.uniform(1.0, 1.6)
        puff(mb, (x + math.cos(a) * s * 0.8, y + math.sin(a) * s * 0.8, z), s * 0.6, m2, rng, 1, 1.0)


def flower_bush(mb, loc, s, rng, color=None):
    """moita com flores pousadas na folhagem (acento de cor controlado)"""
    color = color or rng.choice(FLOWERS)
    puffs = bush(mb, loc, s, rng, pal=rng.choice((("Leaf_Broad", LEAF), (LEAF, "Leaf_Broad"))), n=3, lod=0)
    for (c, r, hz) in puffs:
        for i in range(rng.randint(1, 3)):
            a = rng.uniform(0, math.tau)
            q = rng.uniform(0.2, 0.62)
            zz = c[2] + hz * (1.0 - q ** 1.35) * 0.88
            blossom(mb, (c[0] + math.cos(a) * q * r, c[1] + math.sin(a) * q * r, zz), s * 0.24, color, rng)


def blossom(mb, c, r, m, rng):
    """flor de 5 petalas achatada (estrela aberta, vista de cima). 10 tris"""
    tier(mb, c, r, r * 0.35, 5, m, rng, lob=0.5, droop=-0.3, under=None, jit=0.05)


def fern(mb, loc, s, rng, m="Grass_Tuft", m2="Leaf_Broad"):
    """samambaia: roseta de frondes arqueadas (saia com lobos profundos) + miolo erguido"""
    x, y, z = loc
    tier(mb, (x, y, z + s * 0.62), s * 1.1, s * 0.42, rng.choice((6, 7)), m, rng, lob=0.72, droop=1.4, under=0.4,
         under_m=m, jit=0.12)
    tier(mb, (x, y, z + s * 0.2), s * 0.55, s * 0.95, 5, m2, rng, lob=0.62, droop=0.35, under=None, jit=0.12)


def reeds(mb, loc, s, rng, m="Grass_Tuft", head="Bark_Dark"):
    """touceira de junco: laminas finas e altas abrindo pouco + 2-3 espigas escuras (taboa)"""
    x, y, z = loc
    n = rng.randint(9, 13)
    a0 = rng.uniform(0, math.tau)
    for i in range(n):
        a = a0 + i * math.tau / n + rng.uniform(-0.4, 0.4)
        d = s * rng.uniform(0.05, 0.5)
        b = Vector((x + math.cos(a) * d, y + math.sin(a) * d, z - 0.2))
        hh = s * rng.uniform(1.5, 2.6)
        lean = s * rng.uniform(0.15, 0.45)
        spike(mb, b, b + Vector((math.cos(a) * lean, math.sin(a) * lean, hh)), s * 0.1, m, 3, rot=a)
    for i in range(rng.randint(2, 3)):
        a = rng.uniform(0, math.tau)
        b = Vector((x + math.cos(a) * s * 0.15, y + math.sin(a) * s * 0.15, z - 0.2))
        t = b + Vector((math.cos(a) * s * 0.15, math.sin(a) * s * 0.15, s * rng.uniform(1.6, 2.2)))
        spike(mb, b, t, s * 0.035, m, 3)
        ttube(mb, [t - Vector((0, 0, s * 0.42)), t - Vector((0, 0, s * 0.05))], [s * 0.08, s * 0.07], head, n=4,
              cap0=True, cap1=True)


def grove(mb, c, R, rng, n=None, lod=2, leaf=LEAF, dome_m=UNDER):
    """mancha de floresta de fundo: massa de copas fundidas (domo baixo escuro) + pontas de pinheiro de 2
    camadas. Le como bosque denso de longe com poucos triangulos."""
    x, y, z = c
    dome(mb, (x, y, z - 0.4), R * 0.8, R * 0.4, dome_m, rng, seg=9 if R > 14 else 8, jit=0.2, bottom=False)
    n = n or max(5, int(R * 0.8))
    pts = []
    for i in range(n * 4):
        if len(pts) >= n:
            break
        a = rng.uniform(0, math.tau)
        d = R * 0.84 * math.sqrt(rng.random())
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        if any((px - qx) ** 2 + (py - qy) ** 2 < (R * 0.26) ** 2 for qx, qy, _ in pts):
            continue
        pts.append((px, py, d / R))
    for (px, py, q) in pts:
        hh = R * rng.uniform(1.1, 1.9) * (1.0 - 0.4 * q)
        hh = min(hh, 26.0)
        rr = hh * rng.uniform(0.25, 0.31)
        bz = z + R * 0.42 * (1 - q * q) * 0.55
        rot = rng.uniform(0, math.tau)
        skirt(mb, (px, py, bz), rr, hh * 0.6, 4, leaf, rng, rot=rot, droop=22, lob=0.22, shoulder=None, under=None)
        skirt(mb, (px, py, bz + hh * 0.42), rr * 0.66, hh * 0.58, 4 if lod < 2 else 3, leaf, rng, rot=rot + 0.8,
              droop=20, lob=0.22, shoulder=None, under=0.3 if lod < 2 else None)
    return pts


def grass_tuft(mb, loc, s, rng, m="Grass_Tuft", n=None):
    """tufo de laminas (tetraedros finos) abrindo em leque"""
    x, y, z = loc
    n = n or rng.randint(3, 5)
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


def rock_plant(mb, loc, s, rng, rock_m="Cliff_Rock", rosettes=True):
    """pedra facetada com capa de musgo caindo pela borda e tufos nas frestas"""
    x, y, z = loc
    hz = s * rng.uniform(0.6, 0.9)
    dome(mb, (x, y, z - s * 0.12), s, hz, rock_m, rng, seg=6, jit=0.2, squash=(1.2, 0.9))
    tier(mb, (x + rng.uniform(-0.15, 0.15) * s, y, z - s * 0.12 + hz * 0.78), s * 0.8, s * 0.3, 5, "Leaf_Broad", rng,
         lob=0.35, droop=0.9, under=0.3, under_m="Leaf_Broad", jit=0.15)
    if rosettes:
        grass_tuft(mb, (x - s * 0.9, y + s * 0.4, z), s * 0.7, rng, n=3)


def crystal(mb, base, ang, tilt, ln, r, m="Crystal_Blue"):
    """cristal hexagonal com ponta (sem fundo, enterrado): 18 tris"""
    d = Vector((math.cos(ang) * math.sin(tilt), math.sin(ang) * math.sin(tilt), math.cos(tilt)))
    b = Vector(base) - d * 0.4
    body = b + d * ln * 0.72
    ttube(mb, [b, body, body + d * ln * 0.28], [r, r * 0.92, 0.0], m, n=6, cap0=False, cap1=False, tip=True,
          rot=ang)


def crystal_outcrop(mb, loc, s, rng, n=None, m="Crystal_Blue", rock="Cliff_Rock"):
    """afloramento de cristal: 3-5 cristais saindo da rocha em leque + 2 pedras na base"""
    x, y, z = loc
    n = n or rng.randint(3, 5)
    a0 = rng.uniform(0, math.tau)
    for i in range(n):
        a = a0 + i * math.tau / n + rng.uniform(-0.5, 0.5)
        d = 0.0 if i == 0 else s * rng.uniform(0.35, 0.9)
        ln = s * (rng.uniform(2.6, 3.4) if i == 0 else rng.uniform(1.3, 2.4))
        crystal(mb, (x + math.cos(a) * d, y + math.sin(a) * d, z), a, 0.08 if i == 0 else rng.uniform(0.3, 0.65),
                ln, s * (0.42 if i == 0 else rng.uniform(0.24, 0.34)), m)
    for i in range(2):
        a = a0 + math.pi * (0.5 + i) + rng.uniform(-0.4, 0.4)
        boulder(mb, (x + math.cos(a) * s * 1.1, y + math.sin(a) * s * 1.1, z), s * rng.uniform(0.6, 0.95), rng, rock)


def boulder(mb, loc, s, rng, m="Cliff_Rock"):
    """pedra solta facetada"""
    x, y, z = loc
    dome(mb, (x, y, z - s * 0.2), s, s * rng.uniform(0.55, 0.85), m, rng, seg=rng.choice((5, 6, 7)), jit=0.22,
         squash=(rng.uniform(1.0, 1.35), rng.uniform(0.75, 1.0)))
