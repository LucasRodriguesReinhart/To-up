# fm_forge_kit - pecas de acabamento da Forja do Ignis: materiais proprios, tubos sem torcao com flanges,
# valvulas, rebites, maos-francesas de ferro, correntes de elos, engrenagens, chamas estilizadas,
# telhado irregular (cumeeira com barriga, fileiras variando), enxaimel irregular e prismas no plano vertical.
# Tudo em geometria + cor solida (no Roblox cada material vira uma MeshPart de cor unica).
import math
from mathutils import Vector, Matrix
import fm_lib
from fm_lib import D

# --------------------------------------------------------------- materiais da forja (registrados antes do make_materials)
_M = fm_lib.MATS
_M.setdefault("Stone_Forge", ((0.185, 0.155, 0.135), 0.85, 0.0, 0, None, 0.16))      # alvenaria quente
_M.setdefault("Stone_Forge_Dark", ((0.085, 0.075, 0.072), 0.85, 0.0, 0, None, 0.14))  # base / fuligem
_M.setdefault("Stone_Coal", ((0.02, 0.019, 0.022), 0.5, 0.15, 0, None, 0.10))          # carvao
_M.setdefault("Roof_Forge", ((0.095, 0.09, 0.105), 0.75, 0.0, 0, None, 0.18))         # ardosia escura
_M.setdefault("Metal_Copper", ((0.52, 0.20, 0.085), 0.35, 0.9, 0, None, 0.06))
_M.setdefault("Metal_Rust", ((0.22, 0.08, 0.035), 0.75, 0.4, 0, None, 0.12))
_M.setdefault("Metal_Valve_Red", ((0.55, 0.05, 0.035), 0.45, 0.3, 0, None, 0.04))
# emissao baixa de proposito: com AgX, emissao forte vira branco; aqui o brilho fica laranja saturado
# (no Roblox estes nomes viram Neon com a mesma cor)
_M.setdefault("Fire_Glow_Core", ((1.0, 0.60, 0.08), 0.5, 0.0, 0.95, (1.0, 0.56, 0.06), 0.0))
_M.setdefault("Fire_Glow_Mid", ((0.95, 0.25, 0.01), 0.5, 0.0, 0.8, (1.0, 0.24, 0.01), 0.0))
_M.setdefault("Fire_Glow_Outer", ((0.7, 0.06, 0.01), 0.5, 0.0, 0.72, (1.0, 0.08, 0.01), 0.0))
_M.setdefault("Forge_Glow_Soft", ((0.62, 0.17, 0.012), 0.5, 0.0, 0.75, (1.0, 0.29, 0.02), 0.0))
_M.setdefault("Ember_Glow", ((0.7, 0.12, 0.01), 0.5, 0.2, 0.8, (1.0, 0.19, 0.01), 0.0))
_M.setdefault("Plaster_Forge", ((0.42, 0.32, 0.22), 0.9, 0.0, 0, None, 0.10))           # reboco de oficina (fuligem)
_M.setdefault("Leather_Bellows", ((0.10, 0.035, 0.018), 0.6, 0.0, 0, None, 0.08))       # couro escuro do fole

Z = Vector((0.0, 0.0, 1.0))


def hdir(ang):
    return Vector((math.cos(ang), math.sin(ang), 0.0))


# --------------------------------------------------------------- prisma de poligono no plano vertical
def xz_prism(mb, pts, v0, v1, m, ang=0.0, org=(0.0, 0.0), tint=None, bevel=0.0):
    """poligono [(u, z)] num plano vertical (u ao longo da direcao ang, passando por org), extrudado de v0 a v1
    na normal horizontal (v). Aceita poligono concavo."""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v, z):
        return Vector((org[0] + u * ca - v * sa, org[1] + u * sa + v * ca, z))
    vf = [mb.bm.verts.new(P(u, v0, z)) for u, z in pts]
    vb = [mb.bm.verts.new(P(u, v1, z)) for u, z in pts]
    n = len(pts)
    mb.bm.faces.new(vf)
    mb.bm.faces.new(list(reversed(vb)))
    for i in range(n):
        j = (i + 1) % n
        mb.bm.faces.new((vf[j], vf[i], vb[i], vb[j]))
    mb._post(vf + vb, m, tint, bevel, 1, angle=0.6)


def octagon(w, h, ch):
    """octogono (retangulo chanfrado) centrado na origem, pontos (u, z)"""
    a, b = w / 2, h / 2
    return [(-a + ch, -b), (a - ch, -b), (a, -b + ch), (a, b - ch), (a - ch, b), (-a + ch, b), (-a, b - ch),
            (-a, -b + ch)]


# --------------------------------------------------------------- tubos
def tube_pt(mb, pts, r, m, n=12, caps=True, tint=None, rfn=None):
    """tubo ao longo de uma polilinha com referencial de transporte paralelo (sem torcao nas curvas)"""
    pts = [Vector(p) for p in pts]
    k = len(pts)
    if k < 2:
        return
    tans = []
    for i in range(k):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == k - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
            if t.length < 1e-6:
                t = pts[i + 1] - pts[i]
        tans.append(t.normalized())
    ref = Z if abs(tans[0].z) < 0.9 else Vector((1.0, 0.0, 0.0))
    nrm = tans[0].cross(ref).normalized()
    rings = []
    for i, p in enumerate(pts):
        if i > 0:
            q = tans[i - 1].rotation_difference(tans[i])
            nrm = q @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        b = tans[i].cross(nrm).normalized()
        rr = rfn(i, k) if rfn else r
        rings.append([mb.bm.verts.new(p + (nrm * math.cos(math.tau * j / n) + b * math.sin(math.tau * j / n)) * rr)
                      for j in range(n)])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            j2 = (j + 1) % n
            mb.bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    if caps:
        mb.bm.faces.new(list(reversed(rings[0])))
        mb.bm.faces.new(rings[-1])
    mb._post([v for rg in rings for v in rg], m, tint, 0, 1)


def round_path(pts, rad, nseg=6):
    """polilinha com cantos arredondados; devolve (pontos, trechos_retos[(a, b, tangente)])"""
    pts = [Vector(p) for p in pts]
    trims = [0.0] * len(pts)
    for i in range(1, len(pts) - 1):
        l1 = (pts[i] - pts[i - 1]).length
        l2 = (pts[i + 1] - pts[i]).length
        trims[i] = min(rad, l1 * 0.45, l2 * 0.45)
    out = [pts[0]]
    straights = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        t = (b - a).normalized()
        sa = a + t * trims[i]
        sb = b - t * trims[i + 1]
        straights.append((sa, sb, t))
        if i + 1 < len(pts) - 1:
            c = pts[i + 2]
            t2 = (c - b).normalized()
            p2 = b + t2 * trims[i + 1]
            out.append(sb)
            for k in range(1, nseg):
                u = k / nseg
                out.append(sb * (1 - u) ** 2 + b * 2 * (1 - u) * u + p2 * u * u)
        else:
            out.append(b)
    return out, straights


def _perp(t):
    ref = Z if abs(t.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    u = t.cross(ref).normalized()
    return u, t.cross(u).normalized()


def flange(mb, p, t, r, m="Metal_Iron", bolts=6, bolt_m="Metal_Brass", n=12, w=0.55):
    p, t = Vector(p), Vector(t).normalized()
    mb.rod(p - t * w / 2, p + t * w / 2, r, m, n)
    if bolts:
        u, v = _perp(t)
        for k in range(bolts):
            a = math.tau * (k + 0.5) / bolts
            q = p + (u * math.cos(a) + v * math.sin(a)) * (r * 0.84)
            mb.rod(q - t * (w / 2 + 0.14), q + t * (w / 2 + 0.14), max(0.11, r * 0.075), bolt_m, 5)


def big_pipe(mb, pts, r, m="Metal_Dark", fm="Metal_Iron", bend=None, step=8.0, n=12, bolts=6, bolt_m="Metal_Brass",
             end_flanges=True):
    """tubo grosso com curvas suaves, flanges nas curvas e a cada 'step' nos trechos retos"""
    path, straights = round_path(pts, bend or r * 1.9, 7)
    tube_pt(mb, path, r, m, n)
    fr = r * 1.24
    for i, (a, b, t) in enumerate(straights):
        L_ = (b - a).length
        marks = []
        if i > 0 or end_flanges:
            marks.append(a + t * 0.3)
        if i < len(straights) - 1 or end_flanges:
            marks.append(b - t * 0.3)
        k = int(L_ / step)
        for j in range(1, k + 1):
            f = j / (k + 1)
            marks.append(a + (b - a) * f)
        for q in marks:
            flange(mb, q, t, fr, fm, bolts, bolt_m, n)
    return path


def pipe_clamp(mb, p, t, r, anchor, m="Metal_Iron", strap_m="Metal_Dark"):
    """abracadeira: anel no tubo + tirante ate o ponto de ancoragem"""
    p, t, anchor = Vector(p), Vector(t).normalized(), Vector(anchor)
    mb.rod(p - t * 0.35, p + t * 0.35, r * 1.13, m, 12)
    d = anchor - p
    if d.length > r:
        dd = d.normalized()
        mb.beam(p + dd * r * 0.95, anchor, 0.55, 0.55, strap_m, 0.05)
        mb.box((1.2, 1.2, 0.4), anchor, (0, 0, math.atan2(dd.y, dd.x)), m, 0.05)


def handwheel(mb, c, axis, R, m="Metal_Valve_Red", hub_m="Metal_Dark", seg=12):
    c, axis = Vector(c), Vector(axis).normalized()
    u, v = _perp(axis)
    ring = [c + (u * math.cos(math.tau * k / seg) + v * math.sin(math.tau * k / seg)) * R for k in range(seg + 1)]
    tube_pt(mb, ring, R * 0.13, m, 6, caps=False)
    for k in range(3):
        a = math.tau * k / 3 + 0.3
        mb.beam(c, c + (u * math.cos(a) + v * math.sin(a)) * R, R * 0.14, R * 0.14, m, 0.0)
    mb.rod(c - axis * R * 0.18, c + axis * R * 0.22, R * 0.22, hub_m, 8)


def gate_valve(mb, p, t, r, up=(0, 0, 1), m="Metal_Iron", wheel_m="Metal_Valve_Red"):
    """registro gaveta sobre um tubo: corpo, castelo, haste e volante"""
    p, t, up = Vector(p), Vector(t).normalized(), Vector(up).normalized()
    mb.rod(p - t * r * 0.9, p + t * r * 0.9, r * 1.32, m, 12)
    for s in (-1, 1):
        flange(mb, p + t * s * r * 0.95, t, r * 1.42, "Metal_Dark", 6, "Metal_Brass", 12, 0.4)
    top = p + up * r * 1.25
    mb.rod(p + up * r * 0.9, top + up * r * 0.9, r * 0.5, m, 10)
    mb.rod(top + up * r * 0.9, top + up * r * 1.7, r * 0.12, "Metal_Dark", 6)
    handwheel(mb, top + up * r * 1.6, up, r * 0.95, wheel_m)


def rivet(mb, p, nrm, r=0.2, m="Metal_Brass", h=0.22):
    p, nrm = Vector(p), Vector(nrm).normalized()
    mb.rod(p - nrm * 0.05, p + nrm * h, r, m, 6)


# --------------------------------------------------------------- mao-francesa de ferro
def iron_bracket(mb, o, d, size, m="Metal_Dark", w=0.6, th=0.34, rm="Metal_Brass", scroll=True):
    """suporte em L com diagonal; o = canto superior junto a parede; d = direcao horizontal para fora"""
    o = Vector(o)
    d = Vector((d[0], d[1], 0.0)).normalized()
    s = Vector((-d.y, d.x, 0.0))
    ang = math.atan2(d.y, d.x)
    mb.box((th, w, size), o + d * th / 2 - Z * size / 2, (0, 0, ang), m, 0.06)
    mb.box((size, w, th), o + d * size / 2 - Z * th / 2, (0, 0, ang), m, 0.06)
    a = o + d * th * 0.8 - Z * size * 0.86
    b = o + d * size * 0.86 - Z * th * 0.8
    mb.beam(a, b, w * 0.9, th * 1.25, m, 0.05)
    if scroll:
        c = o + d * size * 0.34 - Z * size * 0.34
        rr = size * 0.17
        ring = [c + (d * math.cos(math.tau * k / 10) + Z * math.sin(math.tau * k / 10)) * rr for k in range(11)]
        tube_pt(mb, ring, th * 0.33, m, 5, caps=False)
    for q in (o + d * th * 0.5 - Z * size * 0.8, o + d * size * 0.8 - Z * th * 0.5, o + d * th * 0.5 - Z * th * 0.5):
        mb.rod(q - s * (w / 2 + 0.1), q + s * (w / 2 + 0.1), th * 0.42, rm, 6)


# --------------------------------------------------------------- corrente de elos (aneis de 4 barras)
def chain_links(mb, a, b, sag=1.0, link=0.9, th=0.17, m="Metal_Dark"):
    a, b = Vector(a), Vector(b)
    L_ = (b - a).length
    n = max(2, int(L_ / (link * 0.72)))
    pts = [a + (b - a) * (i / n) - Z * sag * 4 * (i / n) * (1 - i / n) for i in range(n + 1)]
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        t = p1 - p0
        ln = t.length
        if ln < 1e-5:
            continue
        t.normalize()
        s0 = t.cross(Z)
        if s0.length < 1e-4:
            s0 = Vector((1.0, 0.0, 0.0))
        s0.normalize()
        up0 = s0.cross(t).normalized()
        side = s0 if i % 2 == 0 else up0
        c = (p0 + p1) / 2
        hl = ln * 0.5 + link * 0.16
        hw = link * 0.26
        for sg in (-1, 1):
            mb.beam(c - t * hl + side * sg * hw, c + t * hl + side * sg * hw, th, th, m, 0.0)
            mb.beam(c + t * sg * hl - side * (hw + th / 2), c + t * sg * hl + side * (hw + th / 2), th, th, m, 0.0)
    return pts


def hanging_chain(mb, top, length, link=0.9, hook=True, m="Metal_Dark"):
    top = Vector(top)
    pts = chain_links(mb, top, top - Z * length, 0.0, link, 0.17, m)
    if hook:
        e = pts[-1]
        hk = [e + Vector((0.0, 0.0, -0.2)), e + Vector((0.0, 0.0, -0.9)), e + Vector((0.35, 0.0, -1.35)),
              e + Vector((0.8, 0.0, -1.0)), e + Vector((0.8, 0.0, -0.65))]
        tube_pt(mb, hk, 0.16, "Metal_Iron", 6)


# --------------------------------------------------------------- engrenagem raiada
def gear(mb, c, axis, r, w, teeth, m="Metal_Dark", m2="Metal_Iron", spokes=5, rot0=0.0):
    c, axis = Vector(c), Vector(axis).normalized()
    q = axis.to_track_quat("Z", "Y")
    R = q.to_matrix().to_4x4()

    def P(x, y, z=0.0):
        return c + (R @ Vector((x, y, z)))
    e0 = q.to_euler()
    ns = 16 if r > 1.5 else 12
    mb.cyl(r * 0.8, w * 0.45, c, e0, m, ns, bevel=0.0)
    ring = [P(math.cos(math.tau * k / ns) * r * 0.8, math.sin(math.tau * k / ns) * r * 0.8) for k in range(ns + 1)]
    tube_pt(mb, ring, w * 0.5, m, 6, caps=False)
    for k in range(teeth):
        a = rot0 + math.tau * k / teeth
        e = (R @ Matrix.Rotation(a, 4, "Z")).to_euler()
        mb.box((r * 0.2, math.tau * r / teeth * 0.48, w), P(math.cos(a) * r * 0.95, math.sin(a) * r * 0.95), e, m, 0.0)
    for k in range(spokes):
        a = rot0 + math.tau * k / spokes
        e = (R @ Matrix.Rotation(a, 4, "Z")).to_euler()
        mb.box((r * 0.62, r * 0.13, w * 0.85), P(math.cos(a) * r * 0.46, math.sin(a) * r * 0.46), e, m, 0.0)
    mb.cyl(r * 0.24, w * 1.4, c, e0, m2, 10, bevel=0.0)


# --------------------------------------------------------------- chama estilizada (lingua com curva em S)
def flame(mb, base, r, h, m, rng, n=6):
    base = Vector(base)
    lx, ly = rng.uniform(-0.35, 0.35), rng.uniform(0.0, 0.45)
    pts = []
    for k in range(6):
        f = k / 5
        sw = math.sin(f * math.pi * 1.4) * 0.35 * r
        pts.append(base + Vector((lx * f * h * 0.25 + sw * (1 if lx > 0 else -1), ly * f * h * 0.2, f * h)))
    prof = (0.75, 1.0, 0.86, 0.6, 0.3, 0.04)
    tube_pt(mb, pts, r, m, n, caps=True, rfn=lambda i, k: r * prof[i])


# --------------------------------------------------------------- telhado irregular (cumeeira em Y)
def forge_roof(mb, cx, cy, w, d, ze, rise, rng, m="Roof_Forge", thick=0.8, over=1.5, sag=0.4, row_h=1.7, seg=5.0,
               ridge_m="Wood_Dark", patch_m="Metal_Rust", patches=1, edge_jit=0.35):
    """duas aguas com cumeeira em Y: fileiras de telhas em trechos de comprimento variavel, pequenas rotacoes,
    barriga na cumeeira (sag) e 1-2 remendos de chapa. Devolve funcao z_topo(x, y)."""
    half = w / 2 + over
    Lr = d + over * 2
    ang = math.atan2(rise, w / 2)
    k_ = rise / (w / 2)
    slope = half / math.cos(ang)
    rows = max(3, int(slope / row_h))
    ya = cy - Lr / 2

    def sagz(y, f):
        u = max(-1.0, min(1.0, (y - cy) / (Lr / 2)))
        return -sag * (1 - u * u) * f

    def dsag(y, f):
        u = max(-1.0, min(1.0, (y - cy) / (Lr / 2)))
        return sag * 2 * u / (Lr / 2) * f
    npatch = 0
    for s in (-1, 1):
        for i in range(rows):
            f0 = i / rows
            f1 = min(1.0, (i + 1.3) / rows)
            xa = cx + s * half * (1 - f0)
            xb = cx + s * half * (1 - f1)
            za = ze + rise - k_ * half * (1 - f0)
            zb = ze + rise - k_ * half * (1 - f1)
            ln = math.hypot(xa - xb, za - zb)
            yy = ya - rng.uniform(0.0, edge_jit)
            end = ya + Lr + rng.uniform(0.0, edge_jit)
            while yy < end - 0.3:
                sl = rng.uniform(seg * 0.6, seg * 1.35)
                y1 = min(yy + sl, end)
                if end - y1 < 1.2:
                    y1 = end
                ym = (yy + y1) / 2
                fm = (f0 + f1) / 2
                th = thick * 0.7 * rng.uniform(0.85, 1.2)
                mid = Vector(((xa + xb) / 2, ym, (za + zb) / 2 + thick / 2 + sagz(ym, fm)))
                rx = math.atan(dsag(ym, fm)) + rng.uniform(-0.012, 0.012)
                ry = s * ang + rng.uniform(-0.022, 0.022)
                mb.box((ln + rng.uniform(-0.1, 0.2), y1 - yy - 0.05, th), mid, (rx, ry, rng.uniform(-0.01, 0.01)),
                       m, 0.1, 1, tint=rng.uniform(-1, 1))
                if patches and npatch < patches and 0.25 < fm < 0.8 and rng.random() < 0.06:
                    npatch += 1
                    pl = min(2.6, y1 - yy - 0.4)
                    mb.box((ln * 1.6, pl, 0.16), mid + Vector((0, 0, th * 0.55 + 0.08)),
                           (rx, ry, rng.uniform(-0.06, 0.06)), patch_m, 0.04)
                yy = y1
    # cumeeira em trechos seguindo a barriga
    nr = max(2, int(Lr / 3.5))
    for j in range(nr):
        y0_ = ya - 0.2 + (Lr + 0.4) * j / nr
        y1_ = ya - 0.2 + (Lr + 0.4) * (j + 1) / nr
        ym = (y0_ + y1_) / 2
        mb.box((1.15, y1_ - y0_ + 0.06, 1.1), (cx, ym, ze + rise + thick * 0.6 + sagz(ym, 1.0)),
               (math.atan(dsag(ym, 1.0)), 0, rng.uniform(-0.015, 0.015)), ridge_m, 0.12)

    def ztop(x, y):
        f = max(0.0, 1 - abs(x - cx) / half)
        return ze + rise - k_ * abs(x - cx) + thick + sagz(y, f)
    return ztop


# --------------------------------------------------------------- enxaimel irregular
def timber_wall_irr(mb, a, b, z0, z1, thick, rng, openings=(), post=3.6, m_t="Wood_Dark", m_p="Plaster_Forge",
                    braces=True, jit=0.14, lean=0.028):
    """como fm_parts.timber_wall, mas com pecas levemente tortas (offsets, inclinacoes e secoes variando)"""
    a, b = Vector((a[0], a[1], 0.0)), Vector((b[0], b[1], 0.0))
    L_ = (b - a).length
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    nrm = Vector((-d.y, d.x, 0.0))
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

    def J(v=1.0):
        return rng.uniform(-jit, jit) * v

    for side in (-1, 1):
        off = nrm * side * fo
        # soleira e frechal em 2-3 pecas
        for zz in (z0 + 0.35, z1 - 0.35):
            npc = 2 if L_ < 16 else 3
            for k in range(npc):
                sa, sb = L_ * k / npc - (0.0 if k == 0 else 0.25), L_ * (k + 1) / npc
                pa = a + d * sa + off + Vector((0, 0, zz + J(0.5)))
                pb = a + d * sb + off + Vector((0, 0, zz + J(0.5)))
                mb.beam(pa, pb, 0.5 * rng.uniform(0.92, 1.1), tw * rng.uniform(0.9, 1.12), m_t, 0.08)
        n = max(1, int(round(L_ / post)))
        xs = [L_ * i / n for i in range(n + 1)]
        for o in cuts:
            xs += [o[0] - 0.35, o[1] + 0.35]
        xs = sorted(set(round(x, 2) for x in xs if -0.01 <= x <= L_ + 0.01))
        for x in xs:
            if any(o[0] + 0.3 < x < o[1] - 0.3 for o in cuts):
                continue
            edge = any(abs(x - o[0] + 0.35) < 0.05 or abs(x - o[1] - 0.35) < 0.05 for o in cuts)
            xx = min(max(x + (0.0 if edge else J()), 0.3), L_ - 0.3)
            p = a + d * xx + off
            tl = 0.0 if edge else rng.uniform(-lean, lean) * (z1 - z0)
            mb.beam(p + Vector((0, 0, z0)), p + d * tl + Vector((0, 0, z1)), 0.5 * rng.uniform(0.9, 1.12),
                    tw * rng.uniform(0.9, 1.15), m_t, 0.08)
        if braces:
            for i in range(n):
                x0_, x1_ = L_ * i / n, L_ * (i + 1) / n
                if any(o[0] - 0.5 < x1_ and o[1] + 0.5 > x0_ for o in cuts):
                    continue
                za_, zb_ = z0 + 0.4 + J(0.8), z1 - 0.4 + J(0.8)
                if i % 2 == 0:
                    pa, pb = a + d * (x0_ + J()) + off + Vector((0, 0, za_)), a + d * (x1_ + J()) + off + Vector((0, 0, zb_))
                else:
                    pa, pb = a + d * (x0_ + J()) + off + Vector((0, 0, zb_)), a + d * (x1_ + J()) + off + Vector((0, 0, za_))
                mb.beam(pa, pb, 0.4, 0.55 * rng.uniform(0.9, 1.15), m_t, 0.06)
        for o in cuts:
            for x in (o[0], o[1]):
                p = a + d * x + off
                mb.beam(p + Vector((0, 0, o[2])), p + Vector((0, 0, o[3])), 0.55, 0.75, m_t, 0.08)
            pa = a + d * (o[0] - 0.4 - rng.uniform(0, 0.2)) + off
            pb = a + d * (o[1] + 0.4 + rng.uniform(0, 0.2)) + off
            for zz in (o[2], o[3]):
                mb.beam(pa + Vector((0, 0, zz + J(0.3))), pb + Vector((0, 0, zz + J(0.3))), 0.55, 0.75, m_t, 0.08)


# --------------------------------------------------------------- oitao de tabuas verticais
def board_gable(mb, cx, y_front, w, ze, rise, depth, rng, m="Wood_Plank", m_back="Wood_Dark", bw=1.25,
                facing=-1):
    """oitao triangular em tabuas verticais (topo inclinado seguindo o telhado). y_front = face externa;
    facing = -1 se a face externa olha para -Y."""
    hw = w / 2

    def zt(x):
        return ze + rise * (1 - abs(x - cx) / hw) - 0.08
    yb0 = y_front - facing * 0.0
    # fundo continuo (evita frestas)
    xz_prism(mb, [(cx - hw, ze), (cx + hw, ze), (cx, ze + rise - 0.1)], y_front - facing * 0.25,
             y_front - facing * depth, m_back, 0.0)
    x = cx - hw
    while x < cx + hw - 0.05:
        x1 = min(x + bw * rng.uniform(0.85, 1.15), cx + hw)
        xa, xb = x + 0.05, x1 - 0.05
        poly = [(xa, ze), (xb, ze), (xb, zt(xb))]
        if xa < cx < xb:
            poly.append((cx, zt(cx)))
        poly.append((xa, zt(xa)))
        pr = rng.uniform(-0.06, 0.06)
        xz_prism(mb, poly, y_front + pr, y_front - facing * 0.3 + pr, m, 0.0, tint=rng.uniform(-1, 1))
        x = x1
    return zt
