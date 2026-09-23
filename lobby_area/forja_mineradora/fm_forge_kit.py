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
# passe fabrica: o fogo da boca tem que ser o ponto MAIS CLARO e mais quente da fachada (acima das janelas e
# do lanternim em Forge_Glow_Soft): nucleo amarelo-palido forte, laranja no meio, rubro por fora
_M.setdefault("Fire_Glow_Core", ((1.0, 0.70, 0.18), 0.5, 0.0, 2.0, (1.0, 0.62, 0.12), 0.0))
_M.setdefault("Fire_Glow_Mid", ((1.0, 0.34, 0.03), 0.5, 0.0, 1.6, (1.0, 0.31, 0.02), 0.0))
_M.setdefault("Fire_Glow_Outer", ((0.85, 0.10, 0.015), 0.5, 0.0, 1.25, (1.0, 0.12, 0.01), 0.0))
_M.setdefault("Forge_Glow_Soft", ((0.62, 0.17, 0.012), 0.5, 0.0, 0.55, (1.0, 0.29, 0.02), 0.0))  # janelas < fogo
_M.setdefault("Ember_Glow", ((0.8, 0.16, 0.012), 0.5, 0.2, 1.0, (1.0, 0.21, 0.01), 0.0))
# brilho do alto-forno (fendas, bocas e labio da coroa): laranja saturado, mais contido que o fogo da boca
_M.setdefault("Furnace_Glow", ((1.0, 0.36, 0.05), 0.5, 0.0, 1.5, (1.0, 0.33, 0.04), 0.0))
_M.setdefault("Plaster_Forge", ((0.42, 0.32, 0.22), 0.9, 0.0, 0, None, 0.10))           # reboco de oficina (fuligem)
_M.setdefault("Leather_Bellows", ((0.10, 0.035, 0.018), 0.6, 0.0, 0, None, 0.08))       # couro escuro do fole
# passe fabrica: tabuado enegrecido de fuligem (metade de cima das paredes da oficina) e pedra em brasa (boca).
# Stone_Heated pode vir do fm_lib (materials_export); setdefault mantem a definicao de la se existir.
_M.setdefault("Wood_Soot", (fm_lib.S(52, 38, 31), 0.85, 0.0, 0, None, 0.12))
_M.setdefault("Stone_Heated", (fm_lib.S(112, 44, 30), 0.8, 0.0, 0.35, (1.0, 0.22, 0.04), 0.05))
# alvenaria da forja com variacao de VALOR (+-7%) no mesmo tom, no lugar do xadrez claro/escuro
if "Stone_Forge" not in fm_lib.FAMILIES and hasattr(fm_lib, "add_variants"):
    fm_lib.add_variants("Stone_Forge", [("Stone_Forge", 5), ("Stone_Forge_B", 3, (128, 118, 110)),
                                        ("Stone_Forge_C", 2, (110, 101, 95))])

Z = Vector((0.0, 0.0, 1.0))
# alas: beiral 19.5; ala esq. em meia-agua (sobe 5.5 ate o lado de fora), ala dir. em duas aguas mais baixas
# (a cumeeira baixa abre a visada spawn -> Demon Slayer). Usado por fm_forge, fm_forge_annex e fm_forge_tower.
# (rise baixos de proposito: as visadas spawn -> Shadow Garden / Demon Slayer passam rente as alas em x~+-22..28)
WING_EAVE = 19.5
WING_RISE_L = 5.5
WING_RISE_R = 4.5


def wing_roof_z(x, side):
    """cota do topo das telhas (com espessura 0.8) da ala 'L' ou 'R' na coordenada x"""
    import fm_layout as L
    if side == "L":
        x0, _, x1, _ = L.FORGE_WING_L
        return WING_EAVE + WING_RISE_L * (x1 - x) / (x1 - x0) + 0.8
    x0, _, x1, _ = L.FORGE_WING_R
    cx = (x0 + x1) / 2
    return WING_EAVE + WING_RISE_R * (1 - abs(x - cx) / ((x1 - x0) / 2)) + 0.8


# --------------------------------------------------------------- politica de detalhe (orcamento de triangulos)
class FB(fm_lib.MB):
    """MB com politica de detalhe: 'hero' (chanfra tudo), 'near' (sem chanfro em pecas finas < 0.45),
    'far' (so blocos grandes >= 1.2 chanfrados). Qualquer peca acima de far_z vira 'far' (exceto 'hero').
    Rebites de raio <= 0.2 acima de far_z nem sao gerados (ver rivet)."""

    def __init__(self, name, collection, rng=None, detail="near", far_z=30.0, far_min=1.2):
        fm_lib.MB.__init__(self, name, collection, rng)
        self.detail = detail
        self.far_z = far_z
        self.far_min = far_min

    def lvl(self, z):
        if self.detail != "hero" and z is not None and z > self.far_z:
            return "far"
        return self.detail

    def _bev(self, bevel, dmin, z):
        if not bevel:
            return 0.0
        lv = self.lvl(z)
        if lv == "hero":
            return bevel
        if lv == "near":
            return bevel if (dmin >= 0.45 and bevel >= 0.05) else 0.0
        return bevel if dmin >= self.far_min else 0.0

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.12, seg=1, tint=None):
        fm_lib.MB.box(self, size, loc, rot, m, self._bev(bevel, min(size), loc[2]), seg, tint)

    def beam(self, a, b, w, h=None, m="Wood_Dark", bevel=0.08, roll=0.0, tint=None):
        z = (a[2] + b[2]) / 2
        fm_lib.MB.beam(self, a, b, w, h, m, self._bev(bevel, min(w, h or w), z), roll, tint)

    def cyl(self, r, h, loc, rot=(0, 0, 0), m="Metal_Iron", n=12, r2=None, bevel=0.08, seg=1, caps=True, tint=None,
            angle=0.5):
        fm_lib.MB.cyl(self, r, h, loc, rot, m, n, r2, self._bev(bevel, min(r, h), loc[2]), seg, caps, tint, angle)


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
    fz = getattr(mb, "far_z", None)
    if fz is not None and r <= 0.2 and p.z > fz and getattr(mb, "detail", "near") != "hero":
        return   # rebite miudo no alto: invisivel a distancia, so custa triangulos
    mb.rod(p - nrm * 0.05, p + nrm * h, r, m, 6)


def boss(mb, p, d, size, m="Metal_Iron", bolt_m="Metal_Dark", bolts=6, r_bolt=0.26):
    """chapa quadrada rebitada (colar/flange de parede) onde um tubo encontra uma parede ou a torre"""
    d = Vector((d[0], d[1], 0.0)).normalized()
    p = Vector(p)
    ang = math.atan2(d.y, d.x)
    mb.box((0.45, size, size), p, (0, 0, ang), m, 0.08)
    s = Vector((-d.y, d.x, 0.0))
    for i in range(bolts):
        a = math.tau * i / bolts + math.pi / bolts
        q = p + d * 0.22 + s * math.cos(a) * size * 0.38 + Z * math.sin(a) * size * 0.38
        rivet(mb, q, d, r_bolt, bolt_m)


def rufo(mb, p, r, slope=(0.0, 0.0), m="Metal_Dark"):
    """rufo baixo onde um tubo/respiro atravessa o telhado: colar conico + chapa no plano do telhado.
    slope = (rx, ry) inclinacao do telhado naquele ponto"""
    p = Vector(p)
    mb.box((r * 2.9, r * 2.9, 0.14), p + Z * 0.05, (slope[0], slope[1], 0.0), m, 0.0)
    mb.cyl(r * 1.32, 0.9, p + Z * 0.45, (0, 0, 0), m, 12, r2=r * 1.06, bevel=0.0)


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
                facing=-1, m_top=None, soot_at=0.55):
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
        pr = rng.uniform(-0.06, 0.06)
        zs_ = ze + rise * soot_at + rng.uniform(-0.6, 0.6) if m_top else None
        if zs_ is not None and zs_ < min(zt(xa), zt(xb)) - 0.4:
            # tabua em duas pecas: de baixo no tom da madeira, de cima enegrecida de fuligem
            xz_prism(mb, [(xa, ze), (xb, ze), (xb, zs_), (xa, zs_)], y_front + pr, y_front - facing * 0.3 + pr, m,
                     0.0, tint=rng.uniform(-1, 1))
            poly = [(xa, zs_), (xb, zs_), (xb, zt(xb))]
            if xa < cx < xb:
                poly.append((cx, zt(cx)))
            poly.append((xa, zt(xa)))
            xz_prism(mb, poly, y_front + pr, y_front - facing * 0.3 + pr, m_top, 0.0, tint=rng.uniform(-1, 1))
        else:
            poly = [(xa, ze), (xb, ze), (xb, zt(xb))]
            if xa < cx < xb:
                poly.append((cx, zt(cx)))
            poly.append((xa, zt(xa)))
            xz_prism(mb, poly, y_front + pr, y_front - facing * 0.3 + pr,
                     m_top if (zs_ is not None and zs_ < ze + 0.3) else m, 0.0, tint=rng.uniform(-1, 1))
        x = x1
    return zt


# --------------------------------------------------------------- chama em lamina (silhueta de labareda)
_FLAME = [(-0.50, 0.00), (0.50, 0.00), (0.58, 0.16), (0.46, 0.40), (0.30, 0.60), (0.18, 0.80), (0.04, 1.00),
          (-0.10, 0.78), (-0.24, 0.56), (-0.44, 0.34), (-0.58, 0.15)]


def flame_blade(mb, base, w, h, m, rng, depth=0.45, yaw=0.0, lean=0.25):
    """labareda estilizada em lamina (prisma de silhueta concava, ponta curvada para um lado); face ~ -Y"""
    base = Vector(base)
    sg = 1.0 if rng.random() < 0.5 else -1.0
    pts = []
    for u, v in _FLAME:
        du = sg * lean * (v ** 1.6)          # a ponta curva para o lado
        pts.append((base.x + (u * sg + du) * w, base.z + v * h))
    # prisma no plano vertical que passa por base (u ao longo de yaw); u medido a partir da origem -> desloca org
    ca, sa = math.cos(yaw), math.sin(yaw)
    org = (base.x - base.x * ca, base.y - base.x * sa)
    xz_prism(mb, pts, -depth / 2, depth / 2, m, yaw, org)


# --------------------------------------------------------------- parede de oficina (tabuado + chapas de ferro)
def clad_wall(mb, a, b, z0, z1, thick, rng, openings=(), out=-1, post=3.6, zt=None, kinks=(), iron=(), soot=0.5,
              m_b="Wood_Dark", m_s="Wood_Soot", m_i="Metal_Burnt", m_t="Wood_Dark", m_r="Metal_Dark",
              back_m="Wood_Dark", bw=1.2, inner_posts=True, frames=True, rivets=True):
    """parede de oficina: tabuado VERTICAL entre montantes pesados, com a metade de cima enegrecida de fuligem;
    os vaos listados em 'iron' (indices) recebem chapas de ferro rebitadas. openings = [(s0, s1, zlo, zhi)] em
    distancia ao longo de a->b. out = lado externo (-1/+1) em relacao a normal esquerda de a->b.
    zt(s) -> cota do topo (oitao, meia-agua) ou None (topo reto z1); kinks = s onde o topo quebra (cumeeira)."""
    a = Vector((a[0], a[1], 0.0))
    b = Vector((b[0], b[1], 0.0))
    L_ = (b - a).length
    d = (b - a).normalized()
    ang = math.atan2(d.y, d.x)
    org = (a.x, a.y)
    nrm = Vector((-d.y, d.x, 0.0))

    def top(s):
        return zt(s) if zt else z1
    cuts = sorted(tuple(o) for o in openings)
    vin, vout = -out * thick / 2, out * thick / 2

    def top_pts(s0, s1):
        ks = [k for k in kinks if s0 + 0.02 < k < s1 - 0.02]
        return [(s, top(s)) for s in [s1] + list(reversed(ks)) + [s0]]

    def slab(s0, s1, za, zb, v0, v1, m, tint=None):
        if s1 - s0 < 0.05:
            return
        if zb is None:   # ate o topo
            pts = [(s0, za), (s1, za)] + top_pts(s0, s1)
        else:
            if zb - za < 0.05:
                return
            pts = [(s0, za), (s1, za), (s1, zb), (s0, zb)]
        xz_prism(mb, pts, v0, v1, m, ang, org, tint=tint)

    def pieces(s0, s1):
        """intervalos verticais livres de uma faixa [s0, s1] (fora de TODAS as aberturas que a cobrem);
        None no fim = ate o topo"""
        sm = (s0 + s1) / 2
        hs = sorted((o[2], o[3]) for o in cuts if o[0] - 0.01 <= sm <= o[1] + 0.01)
        spans = []
        z = z0
        for (zl, zh) in hs:
            if zl > z + 0.05:
                spans.append((z, zl))
            z = max(z, zh)
        if z < top(sm) - 0.1:
            spans.append((z, None))
        return spans
    # 1) fundo continuo recortado nas aberturas (face interna lisa; sem frestas entre tabuas)
    edges = sorted(set([0.0, L_] + [min(max(c, 0.0), L_) for o in cuts for c in (o[0], o[1])]))
    for sa, sb in zip(edges, edges[1:]):
        if sb - sa < 0.05:
            continue
        for za, zb in pieces(sa, sb):
            slab(sa, sb, za, zb, vin, vout, back_m)

    # 2) montantes (vaos) e divisao das tabuas: bordas das aberturas sao limites forcados
    n = max(1, int(round(L_ / post)))
    posts = [L_ * i / n for i in range(n + 1)]
    for o in cuts:
        posts += [o[0] - 0.3, o[1] + 0.3]
    posts = sorted(set(round(p, 2) for p in posts if -0.01 <= p <= L_ + 0.01 and
                       not any(o[0] + 0.2 < p < o[1] - 0.2 for o in cuts)))
    forced = sorted(set([0.0, L_] + [c for o in cuts for c in (o[0], o[1])] + posts))

    def bay_of(s):
        for i in range(len(posts) - 1):
            if posts[i] - 0.01 <= s <= posts[i + 1] + 0.01:
                return i
        return -1
    tb = 0.26
    for fa, fb_ in zip(forced, forced[1:]):
        if fb_ - fa < 0.15:
            continue
        bi = bay_of((fa + fb_) / 2)
        is_iron = bi in iron
        if is_iron:
            # chapas de ferro rebitadas, empilhadas (~3.2 de altura), recortadas nas aberturas
            for za, zb in pieces(fa, fb_):
                zz = za
                ztop = top((fa + fb_) / 2) if zb is None else zb
                while zz < ztop - 0.2:
                    z2 = min(zz + 3.2, ztop)
                    last = z2 >= ztop - 0.01 and zb is None
                    pr = rng.uniform(0.0, 0.05)
                    slab(fa + 0.04, fb_ - 0.04, zz + 0.03, None if last else z2 - 0.03, vout,
                         vout + out * (0.2 + pr), m_i)
                    if rivets:
                        zr1 = (min(top(fa), top(fb_)) if last else z2) - 0.4
                        for sr in (fa + 0.4, fb_ - 0.4):
                            for zr in (zz + 0.4, zr1):
                                p = a + d * sr + nrm * (vout + out * (0.22 + pr))
                                rivet(mb, (p.x, p.y, zr), nrm * out, 0.21, m_r, 0.12)
                    zz = z2
            continue
        # tabuas verticais dentro da faixa
        s = fa
        while s < fb_ - 0.05:
            s2 = min(s + bw * rng.uniform(0.85, 1.15), fb_)
            if fb_ - s2 < 0.45:
                s2 = fb_
            sa, sb = s + 0.04, s2 - 0.04
            pr = rng.uniform(-0.04, 0.05)
            tn = rng.uniform(-1, 1)
            v0, v1 = vout, vout + out * (tb + pr)
            for za, zb in pieces(sa, sb):
                zloc = min(top(sa), top(sb)) if zb is None else zb
                zs_ = z0 + (zloc - z0) * (1 - soot) + rng.uniform(-0.5, 0.5)
                if soot > 0 and za + 0.4 < zs_ < zloc - 0.4:
                    slab(sa, sb, za, zs_, v0, v1, m_b, tn)
                    slab(sa, sb, zs_, zb, v0, v1, m_s, tn)
                else:
                    slab(sa, sb, za, zb, v0, v1, m_s if (soot > 0 and za >= zs_) else m_b, tn)
            s = s2

    # 3) montantes pesados (fora), soleira (nao cruza vaos de porta) e frechal / tabua de beiral inclinada
    pw, pd = 0.62, 0.34
    for sides in ((out,) + ((-out,) if inner_posts else ())):
        vb = sides * thick / 2
        for p in posts:
            sp = min(max(p, pw / 2), L_ - pw / 2)
            slab(sp - pw / 2, sp + pw / 2, z0, top(sp) - 0.1, vb, vb + sides * pd, m_t)
        spans = [(0.0, L_)]
        for o in cuts:
            if o[2] <= z0 + 0.8:
                spans = [(s0, min(s1, o[0])) for (s0, s1) in spans if min(s1, o[0]) - s0 > 0.2] + \
                        [(max(s0, o[1]), s1) for (s0, s1) in spans if s1 - max(s0, o[1]) > 0.2]
        for s0, s1 in spans:
            slab(s0, s1, z0, z0 + 0.55, vb, vb + sides * (pd + 0.04), m_t)
        if zt is None:
            slab(0.0, L_, z1 - 0.6, z1, vb, vb + sides * (pd + 0.04), m_t)
        else:
            ks = [0.0] + sorted(k for k in kinks if 0 < k < L_) + [L_]
            for k0, k1 in zip(ks, ks[1:]):
                xz_prism(mb, [(k0, top(k0) - 0.6), (k1, top(k1) - 0.6), (k1, top(k1)), (k0, top(k0))],
                         vb, vb + sides * (pd + 0.04), m_t, ang, org)
    # 4) molduras das aberturas (ombreiras, verga e peitoril), so por fora
    if frames:
        for o in cuts:
            for s in (o[0] - 0.3, o[1] + 0.3):
                slab(s - 0.3, s + 0.3, o[2], o[3], vout, vout + out * (pd + 0.06), m_t)
            slab(o[0] - 0.7, o[1] + 0.7, o[3], o[3] + 0.6, vout, vout + out * (pd + 0.1), m_t)
            if o[2] > z0 + 0.8:
                slab(o[0] - 0.5, o[1] + 0.5, o[2] - 0.4, o[2], vout, vout + out * (pd + 0.2), m_t)


# --------------------------------------------------------------- telhado de meia-agua (galpao)
def forge_shed_roof(mb, x_hi, x_lo, y0, y1, z_hi, z_lo, rng, m="Roof_Forge", thick=0.8, over=1.4, over_hi=0.7,
                    sag=0.3, row_h=1.65, seg=7.5, cap_m="Wood_Dark", patch_m="Metal_Rust", patches=1, edge_jit=0.35):
    """meia-agua com a queda em X (de x_hi/z_hi ate x_lo/z_lo): fileiras de telhas em trechos variaveis, barriga
    leve no meio do vao e capa de madeira na borda alta. Devolve z_topo(x, y)."""
    sdir = 1.0 if x_lo > x_hi else -1.0
    run = abs(x_lo - x_hi)
    k_ = (z_hi - z_lo) / run
    ang = math.atan(k_)
    xs0 = x_hi - sdir * over_hi
    xs1 = x_lo + sdir * over
    total = abs(xs1 - xs0)
    slope = total / math.cos(ang)
    rows = max(3, int(slope / row_h))
    cy = (y0 + y1) / 2
    Lr = (y1 - y0) + over * 2
    ya = cy - Lr / 2

    def zat(x):
        return z_hi - k_ * (x - x_hi) * sdir

    def sagz(y, f):
        u = max(-1.0, min(1.0, (y - cy) / (Lr / 2)))
        return -sag * (1 - u * u) * f * (1 - f) * 4
    npatch = 0
    for i in range(rows):
        f0 = i / rows
        f1 = min(1.0, (i + 1.3) / rows)
        xa = xs1 - sdir * total * f0
        xb = xs1 - sdir * total * f1
        za, zb = zat(xa), zat(xb)
        ln = math.hypot(xa - xb, za - zb)
        yy = ya - rng.uniform(0.0, edge_jit)
        end = ya + Lr + rng.uniform(0.0, edge_jit)
        fm = (f0 + f1) / 2
        while yy < end - 0.3:
            sl = rng.uniform(seg * 0.6, seg * 1.35)
            y1_ = min(yy + sl, end)
            if end - y1_ < 1.2:
                y1_ = end
            ym = (yy + y1_) / 2
            th = thick * 0.7 * rng.uniform(0.85, 1.2)
            mid = Vector(((xa + xb) / 2, ym, (za + zb) / 2 + thick / 2 + sagz(ym, fm)))
            ry = sdir * ang + rng.uniform(-0.02, 0.02)
            mb.box((ln + rng.uniform(-0.1, 0.2), y1_ - yy - 0.05, th), mid, (rng.uniform(-0.012, 0.012), ry,
                                                                              rng.uniform(-0.01, 0.01)),
                   m, 0.1, 1, tint=rng.uniform(-1, 1))
            if patches and npatch < patches and 0.25 < fm < 0.8 and rng.random() < 0.08:
                npatch += 1
                pl = min(2.6, y1_ - yy - 0.4)
                mb.box((ln * 1.6, pl, 0.16), mid + Vector((0, 0, th * 0.55 + 0.08)), (0, ry, rng.uniform(-0.06, 0.06)),
                       patch_m, 0.04)
            yy = y1_
    # capa (cumeeira de meia-agua) na borda alta
    mb.beam((xs0 + sdir * 0.3, ya - 0.3, z_hi + k_ * over_hi + thick * 0.55),
            (xs0 + sdir * 0.3, ya + Lr + 0.3, z_hi + k_ * over_hi + thick * 0.55), 1.0, 0.9, cap_m, 0.1)

    def ztop(x, y):
        return zat(x) + thick
    return ztop
