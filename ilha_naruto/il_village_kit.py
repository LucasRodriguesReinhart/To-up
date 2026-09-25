# il_village_kit - pecas da zona village (Vila da Folha): torno (lathe) para tambores e telhados conicos, paredes
# curvas com vao, colisao em anel, janelas de tambor, emblema da folha, kunai, shuriken, katana, estante, piso de
# tabuas redondo, lanterna de papel. So geometria (MB do lobby); materiais escolhidos por nome.
import math, random
from mathutils import Vector, Euler
import fm_lib
from fm_lib import MB, D, col_box
from fm_parts import Frame
import fm_portal_kit as PK


# ------------------------------------------------------------------ construtor com teto de variantes
class VMB(MB):
    """MB com detalhe (hero/near/far) e teto de variantes tonais por familia (vcap): no Roblox cada variante vira
    uma MeshPart, entao os predios cheios de primitivas ficam com 1 ou 2 tons por familia."""

    def __init__(self, name, collection, rng=None, detail="near", vcap=1):
        super().__init__(name, collection, rng, detail=detail)
        self.vcap = vcap

    def _uv(self, faces, m):
        # telha modelada (nervuras/casca do telhado): um tom "calmo" da textura por primitiva (mesma solucao do
        # AMB do lobby) - sem isso cada nervura pegava um pedaco claro/escuro da textura e o telhado virava xadrez
        import fm_arch_kit as AK
        return AK.AMB._uv(self, faces, m)

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


# ------------------------------------------------------------------ util
def pol(c, r, a_deg, z=0.0):
    """ponto polar em volta do centro c=(x, y, z) (angulo em graus, z relativo a c)"""
    a = math.radians(a_deg)
    return Vector((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2] + z))


def W(c, x, y, z=0.0):
    return Vector((c[0] + x, c[1] + y, c[2] + z))


def rot_to(nrm):
    """Euler que leva o eixo +Z local para nrm (cilindros/discos orientados)"""
    return Vector((0, 0, 1)).rotation_difference(Vector(nrm).normalized()).to_euler()


def tan_frame(c, r, a_deg, z=0.0):
    """referencial na parede de um tambor: +x local = tangente (anti-horario), +y local = para DENTRO"""
    p = pol(c, r, a_deg, z)
    return Frame(p.x, p.y, p.z, math.radians(a_deg) + math.pi / 2)


def arc_spans(gaps, a0=0.0, a1=360.0):
    """trechos de arco (graus) sem os vaos [(angulo_centro, meia_abertura_graus)]"""
    if not gaps:
        return [(a0, a1)]
    gs = sorted(((g % 360.0), h) for g, h in gaps)
    out = []
    for i, (g, h) in enumerate(gs):
        gn, hn = gs[(i + 1) % len(gs)]
        if i == len(gs) - 1:
            gn += 360.0
        a, b = g + h, gn - hn
        if b - a > 0.5:
            out.append((a, b))
    return out


# ------------------------------------------------------------------ torno
def lathe(mb, c, prof, m, n=48, a0=0.0, a1=360.0, tint=None):
    """revolve o perfil FECHADO [(r, z), ...] (z relativo a c) em volta do eixo vertical de c.
    Arco parcial (a0..a1) ganha tampas nas pontas. Nunca use r = 0 no perfil (use um cone no miolo)."""
    full = abs(a1 - a0) >= 359.999
    k = len(prof)
    segs = max(2, int(n))
    cnt = segs if full else segs + 1
    bm = mb.bm
    rings = []
    for i in range(cnt):
        a = math.radians(a0 + (a1 - a0) * i / segs)
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((c[0] + r * ca, c[1] + r * sa, c[2] + z)) for r, z in prof])
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % cnt]
        for j in range(k):
            j2 = (j + 1) % k
            try:
                bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
            except ValueError:
                pass
    if not full:
        for rr in (rings[0], list(reversed(rings[-1]))):
            try:
                bm.faces.new(rr)
            except ValueError:
                pass
    mb._post([v for rr in rings for v in rr], m, tint, 0, 1)


def ring_wall(mb, c, r0, r1, z0, z1, m, n=72, gaps=()):
    """parede curva (anel r0..r1, z0..z1) com vaos [(angulo, meia_abertura_graus)]"""
    for s0, s1 in arc_spans(gaps):
        lathe(mb, c, [(r0, z0), (r1, z0), (r1, z1), (r0, z1)], m, max(2, int(round(n * (s1 - s0) / 360.0))), s0, s1)


def roof_profile(top, th):
    """perfil fechado de telhado conico: 'top' = [(r, z), ...] do beiral para o topo; espessura vertical th"""
    return list(top) + [(r, z - th) for r, z in reversed(top)]


def cone_roof(mb, c, top, th, m, n=64, ribs=0, rib_m=None, rib_w=0.42, rib_h=0.28, fascia=None, fascia_m=None,
              rafters=0, rafter_m="Wood_Dark", rafter_r=None, courses=(), course_m=None, a_off=0.0):
    """telhado conico com beiral: casca (lathe), nervuras radiais (fiadas de telha), testeira no beiral,
    cachorros (pontas de caibro) sob o beiral e degraus concentricos (fiadas)"""
    lathe(mb, c, roof_profile(top, th), m, n)
    rm = rib_m or m
    if ribs:
        for i in range(ribs):
            a = a_off + 360.0 * (i + 0.5) / ribs
            pts = [pol(c, r, a, z + rib_h * 0.5) for r, z in top]
            for p0, p1 in zip(pts, pts[1:]):
                mb.beam(p0, p1, rib_w, rib_h, rm, 0.0)
    for rc in courses:
        # degrau de fiada: anel baixo sobre a casca na cota do perfil em r = rc
        z = _prof_z(top, rc)
        lathe(mb, c, [(rc - 0.5, z - 0.1), (rc + 0.25, z - 0.25), (rc + 0.25, z + 0.22), (rc - 0.5, z + 0.2)],
              course_m or rm, max(16, int(n * 0.75)))
    if fascia:
        r0, r1, z0, z1 = fascia
        lathe(mb, c, [(r0, z0), (r1, z0), (r1, z1), (r0, z1)], fascia_m or "Wood_Dark", n)
    if rafters:
        ra, rb = rafter_r
        for i in range(rafters):
            a = a_off + 360.0 * i / rafters
            za, zb = _prof_z(top, ra) - th - 0.22, _prof_z(top, rb) - th - 0.22
            mb.beam(pol(c, ra, a, za), pol(c, rb, a, zb), 0.36, 0.42, rafter_m, 0.0)


def _prof_z(top, r):
    """cota do perfil de cima do telhado no raio r (interpolacao linear)"""
    for (ra, za), (rb, zb) in zip(top, top[1:]):
        lo, hi = min(ra, rb), max(ra, rb)
        if lo - 1e-6 <= r <= hi + 1e-6:
            t = (r - ra) / (rb - ra) if abs(rb - ra) > 1e-9 else 0.0
            return za + (zb - za) * t
    return top[0][1] if r > top[0][0] else top[-1][1]


def tan_box(mb, c, r, a_deg, size, z, m, bevel=0.0, tilt=0.0):
    """caixa encostada num tambor: size = (largura tangente, espessura radial, altura), z = centro (relativo a c)"""
    p = pol(c, r, a_deg, z)
    mb.box(size, p, (tilt, 0, math.radians(a_deg) + math.pi / 2), m, bevel)


def drum_window(mb, c, r, a_deg, w, zlo, zhi, glass="Window_Warm", frame="Wood_Dark", out=1, sill=True, grid=True,
                jambs=True):
    """janela sobre a face de um tambor (out=1 face externa, -1 face interna): vidro + verga + peitoril + montante
    (+ batentes e travessa quando jambs)"""
    zc = (zlo + zhi) / 2
    h = zhi - zlo
    tan_box(mb, c, r + out * 0.06, a_deg, (w, 0.22, h), zc, glass)
    ro = r + out * 0.16
    tan_box(mb, c, ro, a_deg, (w + 0.7, 0.34, 0.35), zhi + 0.17, frame)
    if sill:
        tan_box(mb, c, r + out * 0.26, a_deg, (w + 1.0, 0.6, 0.36), zlo - 0.16, frame)
    if jambs:
        da = math.degrees((w / 2 + 0.17) / r)
        for s in (-1, 1):
            tan_box(mb, c, ro, a_deg + s * da, (0.34, 0.34, h + 0.2), zc, frame)
    if grid:
        tan_box(mb, c, ro, a_deg, (0.2, 0.3, h), zc, frame)
        if jambs:
            tan_box(mb, c, ro, a_deg, (w, 0.3, 0.2), zc + h * 0.12, frame)


def oculus(mb, c, r, a_deg, z, rad, glass="Window_Warm", frame="Wood_Lacquer_Red", out=1, n=8, cross=True):
    """janela redonda no tambor (eixo radial)"""
    a = math.radians(a_deg)
    rot = (math.pi / 2, 0, a + math.pi / 2)
    mb.cyl(rad + 0.35, 0.36, pol(c, r + out * 0.12, a_deg, z), rot, frame, n, bevel=0.0)
    mb.cyl(rad, 0.3, pol(c, r + out * 0.24, a_deg, z), rot, glass, n, bevel=0.0)
    if cross:
        tan_box(mb, c, r + out * 0.36, a_deg, (2 * rad, 0.14, 0.18), z, frame)
        tan_box(mb, c, r + out * 0.36, a_deg, (0.18, 0.14, 2 * rad), z, frame)


def col_ring(area, c, r0, r1, z0, z1, spans, seg=20.0):
    """colisao de anel/parede curva em caixas (corda na borda externa)"""
    n = 0
    for s0, s1 in spans:
        k = max(1, int(round((s1 - s0) / seg)))
        da = (s1 - s0) / k
        for i in range(k):
            a = s0 + da * (i + 0.5)
            rm = (r0 + r1) / 2
            w = 2 * r1 * math.tan(math.radians(da) / 2) + 0.2
            col_box(area, (w, r1 - r0, z1 - z0), pol(c, rm, a, (z0 + z1) / 2), (0, 0, math.radians(a) + math.pi / 2))
            n += 1
    return n


def col_disk(area, c, R, z0, z1, n=12):
    """piso/volume redondo em n caixas radiais (cada uma cobre o seu setor inteiro, do centro ate R; os cantos
    passam R/cos(180/n) - com n=12, 3,5%)"""
    da = 360.0 / n
    w = 2 * R * math.tan(math.radians(da) / 2)
    for i in range(n):
        a = da * (i + 0.5)
        col_box(area, (w, R, z1 - z0), pol(c, R / 2, a, (z0 + z1) / 2), (0, 0, math.radians(a) + math.pi / 2))
    return n


def plinth(mb, c, R, z_top, rng, notch=None, n=40, face="Stone_Wall_Light", core="Stone_Wall_Dark",
           top="Stone_Wall_Light", z_bot=-0.9):
    """embasamento redondo: nucleo escuro (rejunte) + blocos de face alternados + tampo de calcamento.
    notch = (meia_largura, y_fundo_local) recorte reto para a escada (lado sul)"""
    pts = []
    if notch:
        hw, yb = notch
        ar = -90.0 + math.degrees(math.asin(hw / R))
        al = ar + 360.0 - 2 * math.degrees(math.asin(hw / R))
        for i in range(n + 1):
            a = math.radians(ar + (al - ar) * i / n)
            pts.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
        pts += [(c[0] - hw, c[1] + yb), (c[0] + hw, c[1] + yb)]
    else:
        for i in range(n):
            a = 2 * math.pi * i / n
            pts.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
    import il_lib as IL
    IL.prism(mb, pts, c[2] + z_bot, c[2] + z_top, core, top)
    # blocos de face (juntas escuras entre eles)
    nb = max(12, int(2 * math.pi * R / 3.8))
    for i in range(nb):
        a = 360.0 * (i + 0.5) / nb
        p = pol(c, R, a)
        if notch and abs(p.x - c[0]) < notch[0] + 1.4 and p.y < c[1]:
            continue
        w = 2 * math.pi * R / nb - 0.16
        hh = z_top - 0.08 - (z_bot + 0.5) + rng.uniform(-0.06, 0.04)
        tan_box(mb, c, R - 0.22, a, (w, 0.7, hh), z_bot + 0.5 + hh / 2, face)


# ------------------------------------------------------------------ emblema da folha
def leaf_symbol(mb, o, u, v, s, m, th=0.2, w=0.14):
    """folha estilizada (espiral + ponta + haste) no plano (u, v) centrado em o; u x v = normal da face"""
    o, u, v = Vector(o), Vector(u).normalized(), Vector(v).normalized()
    nrm = u.cross(v).normalized()
    turns = 1.3
    k = 20
    end = math.radians(212.0)
    phi0 = end - turns * 2 * math.pi
    pts = []
    for i in range(k + 1):
        t = i / k
        a = phi0 + t * turns * 2 * math.pi
        r = (0.06 + 0.5 * t) * s
        pts.append(o + (u * math.cos(a) + v * math.sin(a)) * r)
    hw = w * s / 2
    mb.sweep(pts, [(-hw, -th / 2), (hw, -th / 2), (hw, th / 2), (-hw, th / 2)], m, True, up=tuple(nrm))

    def uv(a_deg, r):
        a = math.radians(a_deg)
        return (math.cos(a) * r * s, math.sin(a) * r * s)
    # ponta da folha (triangulo que sai do fim da espiral para baixo-esquerda)
    tri = [uv(186.0, 0.5), uv(224.0, 1.0), uv(240.0, 0.5)]
    PK.plate(mb, tri, o, u, v, th, m)
    # haste curta a direita
    a0, a1 = Vector(uv(-16.0, 0.5)), Vector(uv(-34.0, 0.92))
    p0 = o + u * a0.x + v * a0.y
    p1 = o + u * a1.x + v * a1.y
    d = (p1 - p0)
    side = nrm.cross(d).normalized()
    PK.plate(mb, [(0.0, -hw), (d.length, -hw * 0.6), (d.length, hw * 0.6), (0.0, hw)], p0, d, side, th, m)


def emblem_disk(mb, c, nrm, R, up=(0, 0, 1), face="Emblem_Cream", rim="Metal_Gold", back="Wood_Lacquer_Red",
                sym="Wood_Lacquer_Red", n=28, depth=0.7):
    """disco-emblema: fundo grosso + aro dourado + face clara + folha em relevo (virado para nrm)"""
    c, nrm = Vector(c), Vector(nrm).normalized()
    upv = Vector(up) - nrm * Vector(up).dot(nrm)
    upv.normalize()
    u = upv.cross(nrm).normalized()         # direita de quem olha a face
    v = nrm.cross(u).normalized()           # cima  (u x v = nrm)
    rot = rot_to(nrm)
    mb.cyl(R + 0.55, depth, c - nrm * (depth / 2), rot, back, n, bevel=0.0)
    PK.ring(mb, c + nrm * 0.12, R + 0.08, u, v, 0.55, 0.32, rim, n=n)
    mb.cyl(R - 0.15, 0.22, c + nrm * 0.02, rot, face, n, bevel=0.0)
    leaf_symbol(mb, c + nrm * 0.22, u, v, R * 0.82, sym, th=0.2)
    return u, v


# ------------------------------------------------------------------ armas ninja
def kunai(mb, p, d, n, s=1.0, blade="Metal_VilSteel", grip="Wood_Dark", ring_m="Metal_Dark", ring=True, ring_n=6):
    """kunai: p = juncao lamina/cabo, d = direcao da ponta, n = normal da face larga da lamina"""
    p, d, n = Vector(p), Vector(d).normalized(), Vector(n).normalized()
    side = n.cross(d).normalized()
    pts = [(0.0, -0.15), (0.32, -0.3), (1.2, 0.0), (0.32, 0.3), (0.0, 0.15)]
    PK.plate(mb, [(a * s, b * s) for a, b in pts], p, d, side, 0.12 * s, blade)
    mb.beam(p - d * 0.04 * s, p - d * 0.82 * s, 0.2 * s, 0.2 * s, grip, 0.0)
    if ring:
        if ring_n >= 8:
            PK.ring(mb, p - d * 1.04 * s, 0.2 * s, d, side, 0.09 * s, 0.09 * s, ring_m, n=ring_n)
        else:
            mb.cyl(0.24 * s, 0.09 * s, p - d * 1.04 * s, rot_to(n), ring_m, 6, bevel=0.0)


def shuriken(mb, c, n, up=(0, 0, 1), R=0.9, m="Metal_VilSteel", hub="Metal_Dark", spin=0.0):
    """shuriken de 4 pontas (placa) + cubo central, face voltada para n"""
    c, n = Vector(c), Vector(n).normalized()
    u = Vector(up) - n * Vector(up).dot(n)
    if u.length < 1e-4:
        u = Vector((1, 0, 0)) - n * n.x
    u.normalize()
    v = n.cross(u)
    pts = []
    for k in range(8):
        a = math.radians(45.0 * k + spin)
        r = R if k % 2 == 0 else R * 0.3
        pts.append((r * math.cos(a), r * math.sin(a)))
    PK.plate(mb, pts, c, u, v, 0.12, m)
    mb.cyl(R * 0.24, 0.2, c, rot_to(n), hub, 6, bevel=0.0)


def katana(mb, g, d, n, L=5.6, w=0.34, blade="Metal_VilSteel", grip="Wood_Dark", guard="Metal_Gold", sheath=None):
    """katana: g = ponta do cabo, d = direcao da lamina, n = normal da face larga. sheath = material da bainha"""
    g, d, n = Vector(g), Vector(d).normalized(), Vector(n).normalized()
    hl = L * 0.24
    mb.beam(g, g + d * hl, 0.32, 0.26, grip, 0.0)
    mb.cyl(0.42, 0.14, g + d * (hl + 0.07), rot_to(d), guard, 8, bevel=0.0)
    if sheath:
        mb.beam(g + d * (hl + 0.14), g + d * L, 0.4, 0.3, sheath, 0.0)
        mb.beam(g + d * (L - 0.25), g + d * (L + 0.05), 0.44, 0.34, guard, 0.0)
    else:
        PK.blade(mb, g + d * (hl + 0.14), d, n, L - hl, w, blade, thick=0.1, curve=0.05)


# ------------------------------------------------------------------ mobilia
BOOK_MATS = ("Cloth_Red", "Cloth_Royal_Blue", "Cloth_Canvas", "Cloth_Red", "Wood_Lacquer_Red")


def bookcase(mb, F, w, h, d, rng, shelves=4, m="Wood_Dark", back_m="Wood_Plank", scrolls=0.35):
    """estante (origem = fundo-centro-embaixo, frente para +y local) com livros e pergaminhos"""
    t = 0.3
    mb.box((w, 0.2, h), F.p(0, 0.1, h / 2), F.r(), back_m, 0.0)
    for s in (-1, 1):
        mb.box((t, d, h), F.p(s * (w / 2 - t / 2), d / 2, h / 2), F.r(), m, 0.06)
    mb.box((w + 0.3, d + 0.2, 0.35), F.p(0, d / 2, h + 0.17), F.r(), m, 0.06)
    mb.box((w, d, 0.5), F.p(0, d / 2, 0.25), F.r(), m, 0.0)
    step = (h - 0.5) / shelves
    for i in range(shelves):
        z = 0.5 + step * i
        if i:
            mb.box((w - 2 * t, d - 0.1, 0.18), F.p(0, d / 2, z), F.r(), m, 0.0)
        x = -w / 2 + t + 0.1
        while x < w / 2 - t - 0.4:
            if rng.random() < scrolls:
                ln = min(rng.uniform(0.9, 1.4), w / 2 - t - x)
                if ln < 0.5:
                    break
                n = rng.randint(1, 3)
                for k in range(n):
                    rr = 0.2
                    zz = z + 0.1 + rr + k * rr * 1.7
                    mb.cyl(rr, d * 0.8, F.p(x + rr + 0.05 + (k % 2) * 0.2, d * 0.5, zz), F.r(math.pi / 2, 0, 0),
                           "Cloth_Canvas", 6, bevel=0.0)
                x += 0.6 + (0.2 if n > 1 else 0.0)
            else:
                bw = rng.uniform(0.3, 0.55)
                bh = rng.uniform(0.62, 0.9) * step
                lean = rng.uniform(-0.12, 0.12) if rng.random() < 0.2 else 0.0
                mb.box((bw, d * 0.78, bh), F.p(x + bw / 2, d * 0.5, z + 0.09 + bh / 2), F.r(0, lean, 0),
                       rng.choice(BOOK_MATS), 0.0)
                x += bw + 0.04
            if rng.random() < 0.12:
                x += rng.uniform(0.3, 0.7)


def round_floor(mb, c, R, z, rng, pw=1.3, m="Wood_Plank", alt=("Wood_Light", "Wood_Dark"), h=0.2, p_alt=0.25):
    """assoalho de tabuas corridas dentro de um circulo (tabuas ao longo de x), sobre base escura"""
    lathe(mb, c, [(0.3, z - 0.24), (R, z - 0.24), (R, z - 0.02), (0.3, z - 0.02)], "Wood_Dark", 24)
    mb.cyl(0.32, 0.22, W(c, 0, 0, z - 0.13), (0, 0, 0), "Wood_Dark", 8, bevel=0.0)
    rows = max(2, int(2 * R / pw))
    step = 2 * R / rows
    for i in range(rows):
        y = -R + step * (i + 0.5)
        yy = abs(y) + step / 2
        if yy >= R - 0.05:
            yy = abs(y)
        if yy >= R:
            continue
        hw = math.sqrt(R * R - yy * yy)
        x = -hw
        while x < hw - 0.2:
            ln = min(rng.uniform(5.0, 9.0), hw - x)
            r = rng.random()
            mm = m if r > p_alt else (alt[0] if r < p_alt * 0.6 else alt[1])
            hh = h + rng.uniform(-0.03, 0.02)
            mb.box((ln - 0.08, step - 0.08, hh), W(c, x + ln / 2, y, z - hh / 2), (0, 0, 0), mm, 0.0)
            x += ln


def paper_lantern(mb, top, r=1.0, h=1.9, paper="Lantern_Glow", cap="Wood_Dark", band=None, hang=1.0, n=8,
                  rod_m="Wood_Dark"):
    """lanterna de papel (chochin) pendurada: corpo oval em torno, tampas escuras e faixa; devolve o centro"""
    top = Vector(top)
    if hang > 0:
        mb.rod(top, top - Vector((0, 0, hang)), 0.07, rod_m, 4)
    c = top - Vector((0, 0, hang + 0.22 + h / 2))
    prof = [(0.08, -h / 2), (r * 0.6, -h / 2), (r * 0.9, -h * 0.3), (r, 0.0), (r * 0.9, h * 0.3), (r * 0.6, h / 2),
            (0.08, h / 2)]
    lathe(mb, c, prof, paper, n)
    for sgn in (-1, 1):
        mb.cyl(r * 0.64, 0.24, c + Vector((0, 0, sgn * (h / 2 + 0.08))), (0, 0, 0), cap, n, bevel=0.0)
    if band:
        lathe(mb, c, [(r * 0.97, -h * 0.07), (r + 0.04, -h * 0.07), (r + 0.04, h * 0.07), (r * 0.97, h * 0.07)], band, n)
    return c
