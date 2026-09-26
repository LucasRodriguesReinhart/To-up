# db_village_kit - helpers geometricos da zona VILLAGE (Ilha 2, Dragon Ball). So geometria sobre o MB do lobby
# (via db_capsule_kit.CMB); materiais escolhidos por nome. Dono: zona village (prefixo DB_Hub_).
#   hip_roof      telhado de 4 aguas CHINES: agua concava (curva u^p), beiral que sobe e abre nos cantos, fiadas de
#                 telha em nervuras, cumeeira com chifres, espigoes com ponta levantada, testeira laqueada
#   porthole      escotilha redonda que atravessa a parede (aro + vidro dos dois lados)
#   pill          capsula deitada (cilindro com pontas em cupula) ao longo de um eixo horizontal
#   ellipsoid     icosfera escalada (casco do veiculo, bolha de vidro)
#   dome_open     casca eliptica ABERTA (so a face de fora) para cupulas de pecas nao entraveis; lathe_open idem
#                 para tambores (a face de dentro e as tampas escondidas nao sao criadas)
#   vault_shell   casca de hangar (paredes + abobada) extrudada ao longo de x, com material por faixa
#   end_wall      parede de empena de hangar com vao em arco (tiras verticais)
#   post_lantern  lanterna marcial de caixa num poste laqueado (mercado/dojo)
#   red_lantern   lanterna redonda de papel pendurada
#   wing_dummy    boneco de treino de madeira (poste com bracos, NAO humano)
#   jar           pote de ceramica (torno)
import math
import bmesh
from mathutils import Vector, Matrix, Euler
from fm_parts import Frame
import db_capsule_kit as K

D2R = math.pi / 180.0
UP = Vector((0.0, 0.0, 1.0))

WHITE, NAVY, BLUE, GLASS = "Plaster_DB_White", "Plaster_DB_Navy", "Roof_DB_Blue", "Glass_DB_Blue"
STEEL, DARK, CYAN = "Metal_DB_Steel", "Metal_DB_Dark", "DB_Cyan_Glow"
ORANGE, RED, WDARK, GOLD, LAMP = "Roof_DB_Orange", "Wood_Lacquer_Red", "Wood_Dark", "Metal_Gold", "Lantern_Glow"


def _dedup(vs):
    out = []
    for v in vs:
        if not out or out[-1] is not v:
            out.append(v)
    if len(out) > 2 and out[0] is out[-1]:
        out.pop()
    return out


def _face(bm, vs):
    vs = _dedup(vs)
    if len(vs) < 3:
        return None
    try:
        return bm.faces.new(vs)
    except ValueError:
        return None


def _paint(mb, faces, m):
    faces = [f for f in faces if f is not None and f.is_valid]
    if not faces:
        return
    mi = mb._mi_for(m)
    for f in faces:
        f.material_index = mi
    mb._uv(faces, m)


# ------------------------------------------------------------------ telhado chines de 4 aguas
def hip_roof(mb, cx, cy, yaw, hx, hy, z_eave, rise, m=ORANGE, under_m=WDARK, edge_m=RED, th=0.5, lift=1.5,
             flare=1.0, p=1.6, ns=8, nu=5, rib_step=1.9, rib_m=None, ridge_m=None, orn_m=GOLD, ribs=True,
             fascia=True, horns=True, orn=None, fascia_n=8, hip_n=4, hidden=False):
    """telhado de 4 aguas (hx >= hy = meia-planta do BEIRAL no referencial local girado de yaw; cumeeira ao longo
    do x local em z_eave + rise). Cada agua e uma casca (topo liso, forro, testeira); as aguas triangulares
    fecham num vertice unico. Devolve a funcao altura do topo no centro (z_top).
    hidden=False: as faces laterais das aguas (nos espigoes e na cumeeira, onde duas aguas se encostam com os mesmos
    vertices, sob as vigas) nao sao criadas - nunca aparecem. fascia_n/hip_n: segmentos da testeira e dos espigoes
    (telhado pequeno de barraca usa menos)."""
    F = Frame(cx, cy, 0.0, yaw)
    bm = mb.bm
    rx = max(hx - hy, 0.0)
    C = [Vector((-hx, -hy, 0.0)), Vector((hx, -hy, 0.0)), Vector((hx, hy, 0.0)), Vector((-hx, hy, 0.0))]
    R0, R1 = Vector((-rx, 0.0, 0.0)), Vector((rx, 0.0, 0.0))
    pats = [(C[0], C[1], R0, R1), (C[1], C[2], R1, R1), (C[2], C[3], R1, R0), (C[3], C[0], R0, R0)]
    ridge_m = ridge_m or m
    rib_m = rib_m or m
    o = orn if orn is not None else max(0.5, min(1.0, hy / 7.5))      # escala dos ornamentos (barraca x pavilhao)

    def P(E0, E1, Ra, Rb, s, u):
        e = E0.lerp(E1, s)
        r = Ra.lerp(Rb, s)
        q = e.lerp(r, u)
        c = abs(2.0 * s - 1.0)
        k = E0 if s < 0.5 else E1
        d = Vector((k.x, k.y, 0.0)).normalized()
        w = flare * c ** 4 * (1.0 - u) ** 3
        z = z_eave + rise * max(u, 0.0) ** p + lift * c ** 3 * (1.0 - u) ** 2
        return F.p(q.x + d.x * w, q.y + d.y * w, z)

    dz = Vector((0.0, 0.0, th))
    for (E0, E1, Ra, Rb) in pats:
        tri = (Ra - Rb).length < 1e-6
        T, B = [], []
        for i in range(ns + 1):
            s = i / ns
            rt, rb = [], []
            for j in range(nu + 1):
                u = j / nu
                if tri and j == nu and i > 0:
                    rt.append(T[0][nu])
                    rb.append(B[0][nu])
                    continue
                q = P(E0, E1, Ra, Rb, s, u)
                rt.append(bm.verts.new(q))
                rb.append(bm.verts.new(q - dz))
            T.append(rt)
            B.append(rb)
        tops, bots, edges, sides = [], [], [], []
        for i in range(ns):
            for j in range(nu):
                tops.append(_face(bm, [T[i][j], T[i + 1][j], T[i + 1][j + 1], T[i][j + 1]]))
                bots.append(_face(bm, [B[i][j], B[i][j + 1], B[i + 1][j + 1], B[i + 1][j]]))
        for i in range(ns):
            edges.append(_face(bm, [T[i][0], B[i][0], B[i + 1][0], T[i + 1][0]]))
        if hidden:
            for j in range(nu):
                sides.append(_face(bm, [T[0][j], T[0][j + 1], B[0][j + 1], B[0][j]]))
                sides.append(_face(bm, [T[ns][j], B[ns][j], B[ns][j + 1], T[ns][j + 1]]))
            if not tri:
                for i in range(ns):
                    sides.append(_face(bm, [T[i][nu], T[i + 1][nu], B[i + 1][nu], B[i][nu]]))
        allv = []
        seen = set()
        for row in T + B:
            for v in row:
                if id(v) not in seen:
                    seen.add(id(v))
                    allv.append(v)
        mb._post(allv, m, None, 0, 1)
        _paint(mb, bots + sides, under_m)
        _paint(mb, edges, edge_m)
        for f in tops:
            if f is not None:
                f.smooth = True
        # nervuras (fiadas de telha canal) do beiral ate perto da cumeeira
        if ribs:
            Le = (E1 - E0).length
            cnt = max(2, int(Le / rib_step))
            umax = 0.8 if tri else 0.97
            prof = [(-0.2, -0.06), (0.2, -0.06), (0.2, 0.24), (-0.2, 0.24)]
            for k in range(cnt):
                s = (k + 0.5) / cnt
                if tri and abs(2 * s - 1) > 0.8:
                    continue
                pts = [P(E0, E1, Ra, Rb, s, umax * t) + Vector((0, 0, 0.02)) for t in (0.0, 0.3, 0.62, 1.0)]
                mb.sweep(pts, prof, rib_m, True)
        # testeira laqueada ao longo do beiral
        if fascia:
            pts = [P(E0, E1, Ra, Rb, i / float(fascia_n), 0.0) for i in range(fascia_n + 1)]
            mb.sweep(pts, [(-0.16, -th - 0.28), (0.16, -th - 0.28), (0.16, 0.06), (-0.16, 0.06)], edge_m, True)
    # espigoes (4 cantos) com a ponta levantada e remate dourado
    for k, (E0, E1, Ra, Rb) in enumerate(pats):
        pts = [P(E0, E1, Ra, Rb, 0.0, t / float(hip_n)) + Vector((0, 0, 0.28 * o)) for t in range(hip_n + 1)]
        for a, b in zip(pts, pts[1:]):
            mb.beam(a, b, 0.6 * o, 0.5 * o, ridge_m, 0.0)
        d = Vector((E0.x, E0.y, 0.0)).normalized()
        dw = F.p(d.x, d.y, 0.0) - F.p(0.0, 0.0, 0.0)
        tip = pts[0] + dw * (1.25 * o) + Vector((0, 0, 1.0 * o))
        mb.beam(pts[0], tip, 0.5 * o, 0.5 * o, ridge_m, 0.0)
        mb.cyl(0.36 * o, 0.7 * o, tip + Vector((0, 0, 0.3 * o)), (0, 0, 0), orn_m, 6, r2=0.08, bevel=0.0)
    z_top = z_eave + rise
    if rx > 0.0:
        a, b = F.p(-rx - 0.35, 0.0, z_top + 0.3 * o), F.p(rx + 0.35, 0.0, z_top + 0.3 * o)
        mb.beam(a, b, 0.95 * o, 0.85 * o, ridge_m, 0.0)
        mb.beam(F.p(-rx, 0.0, z_top + 0.78 * o), F.p(rx, 0.0, z_top + 0.78 * o), 0.5 * o, 0.25, orn_m, 0.0)
        if horns:
            for sg in (-1, 1):
                p0 = F.p(sg * (rx + 0.2), 0.0, z_top + 0.3 * o)
                p1 = F.p(sg * (rx + 1.1 * o), 0.0, z_top + 1.9 * o)
                p2 = F.p(sg * (rx + 0.55 * o), 0.0, z_top + 2.6 * o)
                mb.beam(p0, p1, 0.75 * o, 0.7 * o, ridge_m, 0.0)
                mb.beam(p1, p2, 0.6 * o, 0.55 * o, ridge_m, 0.0)
                mb.cyl(0.3 * o, 0.55 * o, p2 + Vector((0, 0, 0.2 * o)), (0, 0, 0), orn_m, 6, r2=0.1, bevel=0.0)
    else:
        mb.cyl(0.55, 0.9, F.p(0, 0, z_top + 0.45), (0, 0, 0), ridge_m, 8, bevel=0.0)
        K.sphere(mb, F.p(0, 0, z_top + 1.35), 0.55, orn_m, sub=1)
        mb.cyl(0.18, 1.1, F.p(0, 0, z_top + 2.2), (0, 0, 0), orn_m, 6, r2=0.05, bevel=0.0)
    return z_top


def roof_z(hx, hy, z_eave, rise, lx, ly, p=1.6):
    """cota aproximada do TOPO do telhado no ponto local (lx, ly) sem o levantamento dos cantos (para assentar
    pecas que atravessam a agua: clerestorio, pilares)"""
    d = min(hy - abs(ly), hx - abs(lx))
    u = max(0.0, min(1.0, d / hy))
    return z_eave + rise * u ** p


# ------------------------------------------------------------------ pecas Capsule
def porthole(mb, p_out, nrm, r, t_wall=0.6, frame_m=NAVY, glass_m=GLASS, n=12, rim=0.32, stick=0.22):
    """escotilha: aro (disco atravessando a parede, saliente stick dos dois lados) + vidro 0,1 mais saliente"""
    nrm = Vector(nrm).normalized()
    p_out = Vector(p_out)
    p_in = p_out - nrm * t_wall
    a, b = p_in - nrm * stick, p_out + nrm * stick
    K.cyl_axis(mb, r + rim, (b - a).length, (a + b) / 2, nrm, frame_m, n)
    a2, b2 = p_in - nrm * (stick + 0.1), p_out + nrm * (stick + 0.1)
    K.cyl_axis(mb, r - 0.05, (b2 - a2).length, (a2 + b2) / 2, nrm, glass_m, n)


def _circle(p, v, w, r, n):
    return [p + v * (r * math.cos(2 * math.pi * i / n)) + w * (r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def pill(mb, c, axis, R, half_len, m, n=24, k_cap=4, tip_deg=82.0, nose=None, tail=None):
    """capsula deitada: cilindro de raio R e meio-comprimento half_len ao longo de 'axis' (horizontal), pontas em
    cupula (fechadas por um disco pequeno). nose/tail = (material, latitude_de_corte_graus): a ponta -u/+u a partir
    do corte sai noutro material (janelao de vidro no nariz, exaustor na cauda)"""
    u = Vector(axis).normalized()
    v = Vector((-u.y, u.x, 0.0)).normalized()
    w = u.cross(v).normalized()
    if w.z < 0:
        w = -w
    c = Vector(c)

    def secs(sign, ph0, ph1, k):
        out = []
        for i in range(k + 1):
            ph = (ph0 + (ph1 - ph0) * i / k) * D2R
            out.append(_circle(c + u * (sign * (half_len + R * math.sin(ph))), v, w, R * math.cos(ph), n))
        return out
    n_split = nose[1] if nose else tip_deg
    t_split = tail[1] if tail else tip_deg
    kn = max(2, int(round(k_cap * n_split / tip_deg)))
    kt = max(2, int(round(k_cap * t_split / tip_deg)))
    body = secs(-1, n_split, 0.0, kn) + secs(1, 0.0, t_split, kt)[1:]
    fs = K.loft(mb, body, m, smooth=True)
    if nose:
        K.loft(mb, secs(-1, tip_deg, n_split, max(2, k_cap - kn + 1)), nose[0], smooth=True)
    if tail:
        K.loft(mb, secs(1, t_split, tip_deg, max(2, k_cap - kt + 1)), tail[0], smooth=True)
    return fs


def ellipsoid(mb, c, radii, yaw, m, sub=2, smooth=True, pitch=0.0):
    M = Matrix.LocRotScale(Vector(c), Euler((0.0, pitch, yaw)), Vector(radii))
    res = bmesh.ops.create_icosphere(mb.bm, subdivisions=sub, radius=1.0, matrix=M)
    fs = mb._post(res["verts"], m, None, 0, 1)
    if smooth:
        for f in fs:
            f.smooth = True
    return fs


def band_ring(mb, c, r0, r1, z0, z1, m, n=40, a0=0.0, a1=360.0):
    """anel retangular (lathe fechado) - faixa, soco, beiral"""
    return K.lathe(mb, c, [(r0, z0), (r1, z0), (r1, z1), (r0, z1)], m, n, a0, a1)


def dome_open(mb, c, a, b, zc, ph0, ph1, k, m, n, mats=None, lip=None):
    """casca eliptica ABERTA (so a face de fora, de ph0 a ph1) para pecas NAO entraveis: a face de dentro e as bordas
    da casca grossa (shell_prof) nunca aparecem e custavam metade dos tris. lip=(a0, b0): comeca com um degrau que
    sai da superficie (a0, b0) na latitude ph0 (capa saliente sobre outra cupula). mats: material por aresta da
    elipse (o degrau usa o da 1a)."""
    prof = K.ell_pts(a, b, zc, ph0, ph1, k)
    sm = list(range(k))
    if lip:
        t = math.radians(ph0)
        prof = [(lip[0] * math.cos(t), zc + lip[1] * math.sin(t))] + prof
        sm = [j + 1 for j in sm]
        if mats:
            mats = [mats[0]] + list(mats)
    return K.lathe(mb, c, prof, m, n, smooth=sm, mats=mats, closed=False)


def lathe_open(mb, c, prof, m, n, mats=None, smooth=()):
    """superficie de revolucao ABERTA (so a face de fora do perfil, de baixo para cima)"""
    return K.lathe(mb, c, prof, m, n, smooth=smooth, mats=mats, closed=False)


# ------------------------------------------------------------------ hangar (oficina)
def vault_profile(R, wall_h, k=14):
    """perfil (u, z) de parede vertical + abobada semicircular de raio R sobre a parede (u de -R a +R)"""
    pts = [(-R, 0.0)]
    for i in range(k + 1):
        a = math.pi * (1.0 - i / k)
        pts.append((R * math.cos(a), wall_h + R * math.sin(a)))
    pts.append((R, 0.0))
    return pts


def vault_shell(mb, F, R_out, R_in, wall_h, x0, x1, mat_fn, ring_m, k=14):
    """casca (paredes + abobada) entre os perfis externo e interno, extrudada ao longo do x local de F (u = y
    local). mat_fn(i, lado, zc_rel, ang_deg) -> material da faixa i ('out' ou 'in'). Faixas de borda (anel) em ring_m.
    Devolve os perfis (externo, interno)."""
    bm = mb.bm
    po, pi_ = vault_profile(R_out, wall_h, k), vault_profile(R_in, wall_h, k)
    n = len(po)

    def row(prof, x):
        return [bm.verts.new(F.p(x, u, z)) for u, z in prof]
    Oa, Ob, Ia, Ib = row(po, x0), row(po, x1), row(pi_, x0), row(pi_, x1)
    groups = {}
    for i in range(n - 1):
        zc = (po[i][1] + po[i + 1][1]) / 2
        ang = math.degrees(math.atan2(zc - wall_h, (po[i][0] + po[i + 1][0]) / 2)) if zc > wall_h + 0.01 else -90.0
        f = _face(bm, [Oa[i], Ob[i], Ob[i + 1], Oa[i + 1]])
        groups.setdefault(mat_fn(i, "out", zc, ang), []).append(f)
        f = _face(bm, [Ia[i], Ia[i + 1], Ib[i + 1], Ib[i]])
        groups.setdefault(mat_fn(i, "in", zc, ang), []).append(f)
        groups.setdefault(ring_m, []).append(_face(bm, [Oa[i], Oa[i + 1], Ia[i + 1], Ia[i]]))
        groups.setdefault(ring_m, []).append(_face(bm, [Ob[i], Ib[i], Ib[i + 1], Ob[i + 1]]))
    for j in (0, n - 1):
        groups.setdefault(ring_m, []).append(_face(bm, [Oa[j], Ia[j], Ib[j], Ob[j]]))
    allv = Oa + Ob + Ia + Ib
    first = next(iter(groups))
    mb._post(allv, first, None, 0, 1)
    for mm, fs in groups.items():
        if mm != first:
            _paint(mb, fs, mm)
    return po, pi_


def hexa(mb, bot, top, m):
    """hexaedro livre (4 pontos em baixo, 4 em cima, mesma ordem)"""
    bm = mb.bm
    vb = [bm.verts.new(Vector(p)) for p in bot]
    vt = [bm.verts.new(Vector(p)) for p in top]
    for f in ([vb[3], vb[2], vb[1], vb[0]], vt, [vb[0], vb[1], vt[1], vt[0]], [vb[1], vb[2], vt[2], vt[1]],
              [vb[2], vb[3], vt[3], vt[2]], [vb[3], vb[0], vt[0], vt[3]]):
        _face(bm, f)
    mb._post(vb + vt, m, None, 0, 1)


def end_wall(mb, F, x0, x1, R_in, wall_h, m, door=None, k=24):
    """parede de empena do hangar (contorno = perfil interno), de x0 a x1 (x local), em tiras verticais.
    door = (meia_largura, z_arranque, flecha): vao com topo em meia-elipse, do chao."""
    us = []
    if door:
        dw, zs, fl = door
        n_out = 4
        for i in range(n_out + 1):
            us.append(-R_in + (R_in - dw) * i / n_out)
        for i in range(1, k):
            us.append(-dw + 2 * dw * i / k)
        for i in range(n_out + 1):
            us.append(dw + (R_in - dw) * i / n_out)
    else:
        us = [-R_in + 2 * R_in * i / k for i in range(k + 1)]

    def ztop(u):
        return wall_h + math.sqrt(max(0.0, R_in * R_in - u * u))

    def zbot(u):
        if not door:
            return 0.0
        dw, zs, fl = door
        if abs(u) > dw + 1e-6:
            return 0.0
        return zs + fl * math.sqrt(max(0.0, 1.0 - (u / dw) ** 2))
    for a, b in zip(us, us[1:]):
        # as tiras nunca atravessam o batente (us contem -dw e +dw): dentro do vao o fundo e o arco
        inside = bool(door) and a >= -door[0] - 1e-6 and b <= door[0] + 1e-6
        za0 = zbot(a) if inside else 0.0
        zb0 = zbot(b) if inside else 0.0
        za1, zb1 = ztop(a), ztop(b)
        bot = [F.p(x0, a, za0), F.p(x0, b, zb0), F.p(x1, b, zb0), F.p(x1, a, za0)]
        top = [F.p(x0, a, za1), F.p(x0, b, zb1), F.p(x1, b, zb1), F.p(x1, a, za1)]
        hexa(mb, bot, top, m)


# ------------------------------------------------------------------ pecas marciais
def post_lantern(mb, x, y, z, yaw=0.0, h=4.6, s=1.0, post_m=RED, base_m="Stone_DB_Block"):
    """lanterna de caixa (papel ambar, montantes escuros, chapeu laranja em piramide) num poste laqueado"""
    F = Frame(x, y, z, yaw)
    mb.box((1.5 * s, 1.5 * s, 0.6), F.p(0, 0, 0.3), F.r(), base_m, 0.0)
    mb.box((0.62 * s, 0.62 * s, h), F.p(0, 0, 0.6 + h / 2), F.r(), post_m, 0.0)
    zc = z + 0.6 + h + 0.2
    mb.box((1.45 * s, 1.45 * s, 0.3), F.p(0, 0, 0.6 + h + 0.15), F.r(), WDARK, 0.0)
    mb.box((1.1 * s, 1.1 * s, 1.35 * s), F.p(0, 0, 0.6 + h + 0.3 + 0.675 * s), F.r(), LAMP, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.24, 0.24, 1.45 * s), F.p(sx * 0.6 * s, sy * 0.6 * s, 0.6 + h + 0.3 + 0.675 * s), F.r(), WDARK, 0.0)
    zt = 0.6 + h + 0.3 + 1.35 * s
    mb.cyl(1.25 * s, 0.75 * s, F.p(0, 0, zt + 0.37 * s), F.r(0, 0, math.pi / 4), ORANGE, 4, r2=0.18, bevel=0.0)
    mb.cyl(0.16, 0.6, F.p(0, 0, zt + 0.75 * s + 0.3), F.r(), GOLD, 6, r2=0.05, bevel=0.0)
    return F.p(0, 0, 0.6 + h + 0.3 + 0.675 * s)


def red_lantern(mb, top, r=0.8, h=1.4, hang=0.8, body="Cloth_Red", glow=LAMP):
    """lanterna redonda pendurada: corpo vermelho em torno, faixa ambar acesa no meio, tampas douradas"""
    top = Vector(top)
    if hang > 0:
        mb.rod(top, top - Vector((0, 0, hang)), 0.07, WDARK, 4)
    c = top - Vector((0, 0, hang + 0.2 + h / 2))
    prof = [(0.12, -h / 2), (r * 0.62, -h / 2), (r, -h * 0.12), (r, h * 0.12), (r * 0.62, h / 2), (0.12, h / 2)]
    K.lathe(mb, (c.x, c.y), [(rr, c.z + zz) for rr, zz in prof], body, 8, mats=[GOLD, body, glow, body, GOLD, GOLD])
    mb.cyl(r * 0.5, 0.22, c + Vector((0, 0, h / 2 + 0.1)), (0, 0, 0), GOLD, 8, bevel=0.0)
    mb.rod(c - Vector((0, 0, h / 2)), c - Vector((0, 0, h / 2 + 0.85)), 0.1, RED, 4)
    return c


def wing_dummy(mb, x, y, z, yaw, wood="Wood_Dark", base=WDARK):
    """boneco de treino (wing chun): tronco de madeira num pe baixo, dois bracos altos, um baixo e uma perna.
    Frente = +y local."""
    F = Frame(x, y, z, yaw)
    mb.box((1.8, 1.8, 0.35), F.p(0, 0, 0.175), F.r(), base, 0.0)
    mb.cyl(0.62, 5.0, F.p(0, 0, 0.35 + 2.5), F.r(), wood, 10, bevel=0.0)
    mb.cyl(0.7, 0.3, F.p(0, 0, 0.35 + 5.0 + 0.15), F.r(), GOLD, 10, bevel=0.0)
    for zz in (1.9, 3.4, 4.3):
        mb.cyl(0.66, 0.2, F.p(0, 0, 0.35 + zz), F.r(), GOLD if zz == 4.3 else base, 10, bevel=0.0)
    for sg in (-1, 1):
        a = F.p(sg * 0.25, 0.4, 0.35 + 3.9)
        b = F.p(sg * 0.75, 2.0, 0.35 + 4.1)
        mb.beam(a, b, 0.32, 0.32, wood, 0.0)
    mb.beam(F.p(0, 0.4, 0.35 + 2.9), F.p(0, 1.9, 0.35 + 2.75), 0.34, 0.34, wood, 0.0)
    mb.beam(F.p(0, 0.4, 0.35 + 1.2), F.p(0.1, 1.2, 0.35 + 1.0), 0.36, 0.36, wood, 0.0)
    mb.beam(F.p(0.1, 1.2, 0.35 + 1.0), F.p(0.35, 1.5, 0.35 + 0.3), 0.36, 0.36, wood, 0.0)


def jar(mb, x, y, z, s=1.0, m="Roof_DB_Blue", rim_m=GOLD, n=8):
    """pote de ceramica (torno) com borda dourada"""
    prof = [(0.25 * s, 0.0), (0.55 * s, 0.0), (0.76 * s, 0.6 * s), (0.44 * s, 1.25 * s), (0.5 * s, 1.5 * s),
            (0.25 * s, 1.5 * s)]
    K.lathe(mb, (x, y), [(r, z + zz) for r, zz in prof], m, n, mats=[m, m, m, rim_m, rim_m, m])
