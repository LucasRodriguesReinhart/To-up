# op_landmarks - MARCOS SECUNDARIOS da Ilha 5 (ONE PIECE / WANO), M4 (PLANO_OP secoes 2, 4.3, 9 e 15.5; PROMPT_USUARIO
# secoes 2 e 12). Substitui op_blockout.landmarks. Prefixo OP_Lmk_, colecao 17_LANDMARKS. Sem colisao (nenhum dos 3 e
# alcancavel: o assento da caveira fica fora do piso do promontorio, a espada e o pagode em pinaculos). Sem luz de dia.
# Custo proporcional a distancia; o castelo + arvore continuam o marco principal (topos < 216).
#
# CAVEIRA COM CHIFRES = FORMACAO DE ROCHA, nao mascara colada: UM corpo esculpido (icosfera deformada por campos
#   analiticos) em que cranio, ORBITAS escavadas (bacias fundas, nao discos pretos colados), arcada da sobrancelha,
#   abertura nasal em pera, macas do rosto, a FAIXA DA BOCA rebaixada com os dentes da mesma pedra e a MANDIBULA mais
#   estreita sao a mesma superficie facetada (sombreamento chapado como as falesias). Integracao: a NUCA e os lados de
#   tras afundam em massas de rocha (crag do op_terrain, mesma familia das falesias, com prateleiras verdes), o PESCOCO e
#   uma massa sob o cranio que encosta no assento do op_terrain (skullnape/skullchin), e um CONTRAFORTE de rocha desce do
#   queixo pela face da falesia ate o mar: de longe le como a falesia que VIRA caveira. Musgo no alto do cranio (capa que
#   escorre, recorte irregular por ruido) como o topo verde das falesias. Rosto para a enseada/praca (SKULL_FACE_DEG),
#   rosto 12 a frente do SKULL_C da planta para o rosto ficar NO labio da falesia (adaptacao registrada).
#   CHIFRES de rocha escura polida (Cliff_OP_Void) que saem das temporas com colar de rocha, abrem para fora, sobem e
#   voltam para dentro (como na concept). OLHOS amarelos da concept: emissivo discreto (Glass_OP_Lantern), pequeno e
#   no FUNDO da orbita (a borda da orbita os esconde de lado). Sem boss, arena, dungeon ou interior.
# ESPADA MONUMENTAL cravada no pinaculo do esporao (rocha do op_terrain ate z 100): lamina RIGIDA de secao hexagonal
#   (gume, chanfro e plano central -> 2 tons de luz), afinando para a ponta ENTERRADA na rocha, guarda de quillons com
#   pontas caidas e bloco central, cabo octogonal com 4 cintas de ouro, pomo; lascas de rocha levantadas em volta da
#   lamina (a fixacao). Leve inclinacao para fora da ilha; face larga virada para a ilha (silhueta legivel). ~0,7k tris.
# PAGODE de 5 andares no pinaculo oeste (cenografico): pinaculo de rocha (crag, preso a falesia do terraco alto),
#   embasamento de pedra, 5 corpos laqueados que encolhem, faixa escura de consolos, TELHADOS de 4 aguas com beiral
#   grosso, cantos levantados (sori), espigoes; hogyo no topo e SORIN de ouro (9 aneis + chama). Topo ~197.
# Orcamento (PLANO_OP secao 9): landmarks 14k tris / 14 MeshParts (materiais: caveira 4, espada 4, pagode 6).
import math, random
import bmesh
from mathutils import Vector, noise
import op_lib as DL
from op_lib import MB, Frame, ccw
import op_layout as L
import op_kit as K
import fm_portal_kit as PK
from op_terrain import crag, assign

C = "17_LANDMARKS"
DARK, VOID, MOSS, GLOW = "Cliff_OP_Dark", "Cliff_OP_Void", "Cliff_OP_Moss", "Glass_OP_Lantern"
ROCK = "Cliff_OP_Warm"
STEEL, GOLD, WD = "Metal_OP_Steel", "Metal_OP_Gold", "Wood_OP_Dark"
LAC, RB = "Wood_OP_Lacquer", "Roof_OP_Blue"
EYE = L.EYE

# ------------------------------------------------------------------ caveira
SR = 24.0                                   # "raio" do cranio
SK_A = math.radians(L.SKULL_FACE_DEG)
SK_F = (math.cos(SK_A), math.sin(SK_A))     # rumo do rosto (mundo)
SK_FWD = 12.0                               # rosto no labio da falesia: centro 12 a frente do SKULL_C
SK_C = (L.SKULL_C[0] + SK_F[0] * SK_FWD, L.SKULL_C[1] + SK_F[1] * SK_FWD)
SK_Z = 113.0                                # centro do cranio
AX, AY, AZ = 0.86 * SR, 1.14 * SR, 0.9 * SR  # semi-eixos (largura, profundidade, altura)
YF = 0.6 * AY                               # plano do rosto (achatamento)
ORB = (0.35 * SR, 0.05 * SR, 0.245 * SR, 0.205 * SR, 0.42 * SR)    # x, z, rx, rz, profundidade
NAS = (-0.27 * SR, 0.115 * SR, 0.15 * SR, 0.26 * SR)                # z, rx (na base), rz, profundidade
MOUTH = (-0.66 * SR, -0.47 * SR, 0.41 * SR, 3.4)                    # z0, z1, meia largura, rebaixo


def skf():
    return Frame(SK_C[0], SK_C[1], 0.0, SK_A - math.pi / 2)        # +y local = rosto


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def skull_base(d):
    """ponto da superficie (antes do entalhe) na direcao unitaria d (x lateral, y rosto, z cima)"""
    x, y, z = d.x * AX, d.y * AY, d.z * AZ
    if z < 0:                                       # face de baixo (maxila/mandibula) mais estreita
        x *= 1.0 - 0.2 * min(1.0, -z / AZ)
    elif y < 0:                                     # abobada mais cheia atras-em-cima (cranio, nao bola)
        z *= 1.0 + 0.08 * min(1.0, -y / AY)
        x *= 1.0 + 0.05 * min(1.0, -y / AY)
    if y > YF:                                      # plano do rosto
        y = YF + (y - YF) * 0.3
    if z < MOUTH[0]:                                # mandibula: mais estreita e recuada
        k = smooth((MOUTH[0] - z) / 3.0)
        x *= 1.0 - 0.13 * k
        if y > 0:
            y -= 1.4 * k
    return Vector((x, y, z))


SNAP = 0.2          # faixa (em q) em que o vertice e puxado PARA o contorno: borda limpa das cavidades (sem serrilhado)


def _nasal_q(x, z):
    zn, rxn, rzn, Dn = NAS
    tt = min(1.0, max(0.0, (z - zn) / rzn * 0.5 + 0.5))
    rx = rxn * (1.0 - 0.55 * tt)
    return math.sqrt((x / rx) ** 2 + ((z - zn) / rzn) ** 2), rx


def carve(p, front):
    """entalhe no rosto: devolve (ponto, profundidade, q) - q < 1 = dentro de uma cavidade (orbita, nariz, boca).
    Vertices perto do contorno (|q - 1| < SNAP) vao PARA o contorno: a borda da cavidade vira uma linha limpa de
    vertices e a face so e escura se estiver do lado de dentro (classificacao por regiao, nao por profundidade)."""
    if not front:
        return p, 0.0, 9.0
    x, y, z = p
    dep, qmin = 0.0, 9.0
    # orbitas (levemente caidas para fora) + arcada da sobrancelha
    for s in (-1, 1):
        ox, oz, rx, rz, D = ORB
        xx, zz = x - s * ox, z - oz
        c, sn = math.cos(s * 0.14), math.sin(s * 0.14)
        xr, zr = xx * c + zz * sn, -xx * sn + zz * c
        q = math.sqrt((xr / rx) ** 2 + (zr / rz) ** 2)
        if abs(q - 1.0) < SNAP:
            xr, zr = xr / q, zr / q
            q = 1.0
            xx, zz = xr * c - zr * sn, xr * sn + zr * c
            x, z = s * ox + xx, oz + zz
        if q < 1.0:
            dep = max(dep, D * (1.0 - q ** 4) ** 0.5)
        elif q < 1.5 and zr > -0.2 * rz:
            y += 1.3 * (1.0 - (q - 1.0) / 0.5) * smooth(zr / rz + 0.2)
        qmin = min(qmin, q)
    # abertura nasal em pera (estreita em cima)
    zn, rxn, rzn, Dn = NAS
    q, rxq = _nasal_q(x, z)
    if abs(q - 1.0) < SNAP:
        x, z = x / q, zn + (z - zn) / q
        q = 1.0
    if q < 1.0:
        dep = max(dep, Dn * (1.0 - q ** 4) ** 0.5)
    qmin = min(qmin, q)
    # macas do rosto
    for s in (-1, 1):
        qq = math.hypot((x - s * 0.47 * SR) / (0.17 * SR), (z + 0.2 * SR) / (0.13 * SR))
        if qq < 1.0:
            y += 1.4 * (1.0 - qq * qq)
            x += s * 0.9 * (1.0 - qq * qq)
    # faixa da boca rebaixada (onde ficam os dentes): retangulo
    z0, z1, hw, Dm = MOUTH
    zc, hz = (z0 + z1) / 2, (z1 - z0) / 2
    qx, qz = abs(x) / hw, abs(z - zc) / hz
    q = max(qx, qz)
    if abs(q - 1.0) < SNAP * 0.6:
        if qx >= qz:
            x = math.copysign(hw, x)
        else:
            z = zc + math.copysign(hz, z - zc)
        q = 1.0
    if q < 1.0:
        dep = max(dep, Dm)
    qmin = min(qmin, q)
    return Vector((x, y - dep, z)), dep, qmin


def skull(mb):
    F = skf()
    bm = mb.bm
    res = bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    vs = res["verts"]
    depth = {}
    base_front = []
    for v in vs:
        d = v.co.normalized()
        p = skull_base(d)
        front = d.y > 0.2 and p.y > YF - 6.0
        if front:
            base_front.append((p.x, p.y, p.z))
        q, dep, qr = carve(p, front)
        # rocha intemperizada: relevo baixo de ruido (facetas), menor no rosto
        n = noise.noise(Vector((q.x, q.y, q.z)) * 0.11 + Vector((3.1, 7.7, 1.3)))
        q += d * n * (0.45 if front else 0.9)
        depth[v] = qr
        w = F.p(q.x, q.y, SK_Z + q.z)
        v.co = w
    faces = list({f for v in vs for f in v.link_faces})
    # some o que fica enterrado (base do pescoco)
    kill = [f for f in faces if all(v.co.z < SK_Z - 0.93 * AZ for v in f.verts)]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    faces = [f for f in faces if f.is_valid]
    dark, void, moss = [], [], []
    for f in faces:
        f.normal_update()
        qf = sum(depth.get(v, 9.0) for v in f.verts) / len(f.verts)
        c = f.calc_center_median()
        lc = c - Vector((SK_C[0], SK_C[1], SK_Z))
        fy = lc.x * SK_F[0] + lc.y * SK_F[1]
        mz = f.normal.z + 0.4 * noise.noise(c * 0.09 + Vector((0.3, 5.1, 2.2)))
        if qf < 0.999:
            void.append(f)
        elif mz > 0.74 and fy < 0.25 * AY:
            moss.append(f)
        else:
            dark.append(f)
    assign(mb, dark, DARK)
    assign(mb, void, VOID)
    assign(mb, moss, MOSS)
    return base_front


def face_y(base_front, x, z):
    """y (local) da superficie do rosto ANTES do entalhe em (x, z): media dos vizinhos mais proximos"""
    best = sorted(base_front, key=lambda p: (p[0] - x) ** 2 + (p[2] - z) ** 2)[:4]
    return sum(p[1] for p in best) / len(best)


def teeth(mb, base_front):
    F = skf()
    z0, z1, hw, Dm = MOUTH
    zmid = (z0 + z1) / 2
    for row, (za, zb, n, wt) in enumerate(((z1 + 0.1, zmid + 0.2, 8, 2.05), (z0 - 0.1, zmid - 0.2, 7, 1.9))):
        span = hw - 1.2
        for i in range(n):
            x = -span + (2 * span) * (i + 0.5) / n
            yf = face_y(base_front, x, (za + zb) / 2)
            yl = face_y(base_front, x - 1.0, (za + zb) / 2)
            yr = face_y(base_front, x + 1.0, (za + zb) / 2)
            yaw = math.atan2(yr - yl, 2.0)
            w = wt * (0.92 if abs(x) > span * 0.7 else 1.0)
            # dente afunilado: raiz larga na gengiva, ponta mais estreita e chanfrada
            zr, zt = za, zb
            hh = abs(zt - zr)
            sg = 1 if zt > zr else -1
            tip = 0.62
            rings = []
            for k, (t, sc) in enumerate(((0.0, 1.0), (0.7, 0.92), (1.0, tip))):
                zz = zr + sg * hh * t
                ring = []
                for (ux, uy) in ((-w / 2, -2.8), (w / 2, -2.8), (w / 2, -0.35), (-w / 2, -0.35)):
                    lx = x + ux * sc * math.cos(yaw)
                    ly = yf + uy + ux * sc * math.sin(yaw) - (0.25 * t if uy > -1 else 0.0)
                    ring.append(tuple(F.p(lx, ly, SK_Z + zz)))
                rings.append(ring)
            if sg < 0:
                rings = [r[::-1] for r in rings]
            _skin(mb, rings, DARK)


def _skin(mb, rings, m, caps=True):
    bm = mb.bm
    V = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
    out = []
    n = len(V[0])
    for a, b in zip(V, V[1:]):
        for i in range(n):
            j = (i + 1) % n
            try:
                out.append(bm.faces.new((a[i], a[j], b[j], b[i])))
            except ValueError:
                pass
    if caps:
        for r, rev in ((V[0], True), (V[-1], False)):
            try:
                out.append(bm.faces.new(list(reversed(r)) if rev else r))
            except ValueError:
                pass
    for f in out:
        f.normal_update()
    assign(mb, out, m)
    return out


def horns(mb):
    """chifres de rocha escura: saem das temporas, abrem para fora, sobem e voltam para dentro (concept)"""
    F = skf()
    for s in (-1, 1):
        ctrl = [(0.5, -0.05, 0.36, 6.2), (0.84, -0.1, 0.56, 5.8), (1.16, -0.13, 0.8, 4.8), (1.36, -0.1, 1.12, 3.7),
                (1.36, -0.02, 1.44, 2.6), (1.2, 0.08, 1.7, 1.5), (0.98, 0.14, 1.84, 0.25)]
        pts = [(s * a * SR, b * SR, c * SR, r) for a, b, c, r in ctrl]
        sm = _catmull(pts, 3)
        P = [tuple(F.p(x, y, SK_Z + z)) for x, y, z, r in sm]
        PK.taper_tube(mb, P, [r for x, y, z, r in sm], VOID, n=8)
        # colar de rocha onde o chifre sai do cranio
        cx, cy, cz, _ = pts[1]
        c = F.p(cx * 0.97, cy, SK_Z + cz * 0.96)
        mb.ico(7.2, tuple(c), DARK, 1, scale=(1.0, 1.0, 0.62), rot=(0, s * 0.5, F.a), jitter=0.12, seed=7.0 + s)


def _catmull(pts, sub=3):
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(sub):
            t = k / sub
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(4)))
    out.append(pts[-1])
    return out


def eyes(mb, base_front):
    F = skf()
    ox, oz, rx, rz, D = ORB
    for s in (-1, 1):
        # M6b item 45: o olho estava 0,9 a frente do fundo da orbita (solto): recua 1,05 e encosta (entra ~0,15)
        y = face_y(base_front, s * ox, oz) - D + 2.4 - 1.05
        mb.ico(1.55, tuple(F.p(s * ox * 0.98, y - 0.6, SK_Z + oz - 0.5)), GLOW, 2, scale=(1.2, 0.7, 1.0), rot=(0, 0, F.a))


def skull_rock(mb):
    """nuca e lados de tras afundados em rocha, pescoco sob o cranio e contraforte do queixo ate o mar"""
    F = skf()
    for i, (x, y, r, z0, z1, st, tp) in enumerate((
            (0.0, -0.86 * SR, 19.0, 84.0, SK_Z + 11.0, 3, 0.84),         # nuca (a falesia sobe atras do cranio)
            (-0.74 * SR, -0.36 * SR, 12.0, 85.0, SK_Z + 3.0, 3, 0.82),    # lado de tras esquerdo
            (0.76 * SR, -0.4 * SR, 12.5, 85.0, SK_Z + 0.0, 3, 0.82),      # lado de tras direito
            (0.0, -0.15 * SR, 14.0, 84.0, SK_Z - 0.72 * AZ, 1, 0.9),      # pescoco
            (-0.55 * SR, 0.18 * SR, 7.0, 85.0, SK_Z - 0.6 * AZ, 1, 0.9),  # canto da mandibula
            (0.55 * SR, 0.18 * SR, 7.0, 85.0, SK_Z - 0.62 * AZ, 1, 0.9))):
        p = F.p(x, y, 0.0)
        crag(mb, p.x, p.y, r, z0, z1, "skullrock%d" % i, steps=st, top_tilt=0.12, drape=1.4, cap=MOSS, m=DARK,
             mlow=DARK, taper=tp)
    # contraforte do queixo: desce pela falesia ate o mar (a caveira nasce da falesia)
    for i, (x, y, r, z1, tp) in enumerate(((0.0, 0.42 * SR, 9.5, SK_Z - 0.84 * AZ, 0.9),
                                            (-0.42 * SR, 0.3 * SR, 7.0, 82.0, 0.88),
                                            (0.42 * SR, 0.3 * SR, 7.5, 84.0, 0.88))):
        p = F.p(x, y, 0.0)
        crag(mb, p.x, p.y, r, 30.0, z1, "skullbut%d" % i, steps=3, top_tilt=0.1, drape=1.0, cap=MOSS, m=DARK,
             mlow=DARK, taper=tp, sx=0.8, ang=F.a)


def build_skull():
    mb = MB("OP_Lmk_Skull", C, random.Random(1301), detail="far", floor=-999)
    bf = skull(mb)
    teeth(mb, bf)
    horns(mb)
    eyes(mb, bf)
    skull_rock(mb)
    mb.finish()


# ------------------------------------------------------------------ espada
SW_LEAN = 0.06


def sword_axes():
    wx, wy = L.SWORD_POS
    th = math.atan2(250.0 - wy, 0.0 - wx)            # rumo da ilha (centro ~ (0, 250))
    X = Vector((math.cos(th - math.pi / 2), math.sin(th - math.pi / 2), 0.0))   # largura da lamina
    Y = Vector((math.cos(th), math.sin(th), 0.0))                              # para a ilha
    Z = Vector((0.0, 0.0, 1.0))
    A = (Z * math.cos(SW_LEAN) - Y * math.sin(SW_LEAN)).normalized()          # eixo (inclina para FORA da ilha)
    Yt = A.cross(X).normalized()
    if Yt.dot(Y) < 0:
        Yt = -Yt
    O = Vector((wx, wy, L.SWORD_ROCK_Z))
    return O, X, Yt, A


def sword(mb, mr):
    O, X, Y, A = sword_axes()
    pt = lambda x, y, h: O + X * x + Y * y + A * h
    # LAMINA: secao hexagonal (gume / chanfro / plano), afina para a ponta enterrada
    sec = [(-9.0, 7.0), (0.0, 11.0), (22.0, 14.6), (50.0, 16.2), (77.4, 16.6), (81.0, 15.0)]
    rings = []
    for h, w in sec:
        th = max(1.2, 0.2 * w)
        rings.append([tuple(pt(px, py, h)) for px, py in ((w / 2, 0.0), (0.3 * w, th / 2), (-0.3 * w, th / 2),
                                                          (-w / 2, 0.0), (-0.3 * w, -th / 2), (0.3 * w, -th / 2))])
    _skin(mb, rings, STEEL)
    # bloco central (ricasso / langet) e GUARDA de quillons com pontas caidas
    hg = 83.0
    _box(mb, pt, 0.0, 0.0, hg, 10.0, 7.0, 5.2, GOLD)
    rings = []
    for u, dz, hh, dd in ((-24.0, -3.0, 1.8, 2.8), (-21.0, -1.4, 3.0, 4.0), (-13.0, 0.0, 4.2, 5.0), (13.0, 0.0, 4.2, 5.0),
                          (21.0, -1.4, 3.0, 4.0), (24.0, -3.0, 1.8, 2.8)):
        rings.append([tuple(pt(u, sy * dd / 2, hg + dz + sz * hh / 2)) for sy, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    _skin(mb, rings, GOLD)
    for s in (-1, 1):                                  # remate das pontas
        c = pt(s * 24.6, 0.0, hg - 3.0)
        mb.ico(1.6, tuple(c), GOLD, 1)
    # CABO octogonal (fio escuro) com 4 cintas de ouro e POMO
    h0, h1 = hg + 2.6, hg + 25.0
    rings = []
    for h, r in ((h0, 2.5), ((h0 + h1) / 2, 2.75), (h1, 2.45)):
        rings.append([tuple(pt(r * math.cos(math.pi * 2 * k / 8 + math.pi / 8), r * math.sin(math.pi * 2 * k / 8 + math.pi / 8), h))
                      for k in range(8)])
    _skin(mb, rings, WD)
    for k in range(4):
        h = h0 + 1.2 + (h1 - h0 - 2.4) * k / 3
        rings = [[tuple(pt(3.15 * math.cos(math.pi * 2 * j / 8 + math.pi / 8), 3.15 * math.sin(math.pi * 2 * j / 8 + math.pi / 8),
                           h + dh)) for j in range(8)] for dh in (-0.55, 0.55)]
        _skin(mb, rings, GOLD)
    prof = [(3.0, 0.0), (4.1, 1.2), (4.3, 2.6), (3.4, 4.3), (1.6, 5.6), (0.0, 6.2)]
    rings = []
    for r, dh in prof:
        rr = max(r, 0.05)
        rings.append([tuple(pt(rr * math.cos(math.pi * 2 * j / 8), rr * math.sin(math.pi * 2 * j / 8), h1 + dh))
                      for j in range(8)])
    _skin(mb, rings, GOLD)
    # lascas de rocha levantadas em volta da lamina (a lamina RACHOU o pinaculo)
    for i in range(6):
        a = i * math.tau / 6 + 0.4
        dist = 7.5 + 2.5 * K._h01("sh", i)
        p = O + X * math.cos(a) * dist + Y * math.sin(a) * dist * 0.7
        crag(mr, p.x, p.y, 2.2 + 1.4 * K._h01("shr", i), L.SWORD_ROCK_Z - 1.5, L.SWORD_ROCK_Z + 0.8 + 1.8 * K._h01("shz", i),
             "swshard%d" % i, n=5, steps=1, top_tilt=0.5, drape=0.3, cap=ROCK, m=ROCK, mlow=ROCK,
             lean=(math.cos(a) * 0.25, math.sin(a) * 0.25))


def _box(mb, pt, x, y, h, sx, sy, sz, m):
    rings = []
    for dz in (-sz / 2, sz / 2):
        rings.append([tuple(pt(x + ux * sx / 2, y + uy * sy / 2, h + dz)) for ux, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    _skin(mb, rings, m)


def build_sword():
    mb = MB("OP_Lmk_Sword", C, random.Random(1302), detail="far", floor=-999)
    sword(mb, mb)
    mb.finish()


# ------------------------------------------------------------------ pagode
PG_TIERS = [(5.6, 5.4), (4.85, 4.6), (4.1, 4.3), (3.35, 4.1), (2.6, 3.9)]   # (meia largura do corpo, altura)


def pagoda_roof(mb, c, hw_lo, hw_hi, z_eave, over, rise, top=None):
    """telhado de 4 aguas do pagode: beiral grosso (testeira escura), cantos levantados (sori), agua azul ate o corpo
    de cima (hw_hi) ou ate o topo (hogyo, top = z do vertice)"""
    cx, cy = c
    E = hw_lo + over
    lift = 0.9 + 0.12 * over

    def edge(hw, z, lf):
        out = []
        for side in range(4):
            a = side * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            for t in (-1.0, -0.5, 0.0, 0.5):
                u, v = t * hw, hw
                x = cx + u * ca - v * sa
                y = cy + u * sa + v * ca
                zl = z + lf * (abs(t) ** 2.2)
                out.append((x, y, zl))
        return out
    outer_top = edge(E, z_eave, lift)
    outer_bot = edge(E - 0.15, z_eave - 0.75, lift)
    soffit_in = edge(hw_lo + 0.3, z_eave - 0.2 + 0.0, 0.0)
    if top is None:
        inner = edge(hw_hi + 0.25, z_eave + rise, 0.0)
        _skin(mb, [outer_top, inner], RB, caps=False)
        # rufo escuro contra o corpo de cima
        _skin(mb, [edge(hw_hi + 0.3, z_eave + rise - 0.05, 0.0), edge(hw_hi + 0.3, z_eave + rise + 0.35, 0.0)], WD, caps=False)
    else:
        _skin(mb, [outer_top, edge(0.6, top, 0.0)], RB, caps=False)
    _skin(mb, [outer_bot, outer_top], WD, caps=False)              # testeira
    _skin(mb, [soffit_in, outer_bot], WD, caps=False)              # forro do beiral
    # espigoes (capas nas 4 diagonais)
    zt = (z_eave + rise) if top is None else top
    hi = (hw_hi + 0.25) if top is None else 0.6
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        d0, d1 = E * math.sqrt(2) + 0.5, hi * math.sqrt(2)
        p0 = Vector((cx + math.cos(a) * d0, cy + math.sin(a) * d0, z_eave + lift + 0.35))
        p1 = Vector((cx + math.cos(a) * d1, cy + math.sin(a) * d1, zt + 0.25))
        mb.beam(p0, p1, 0.6, 0.55, RB, 0.0)


def pagoda(mb):
    px, py, pr, ptop = L.WEST_SPIRE
    # pinaculo de rocha (mesma familia das agulhas do op_terrain), preso a falesia do terraco alto
    crag(mb, px, py, 22.0, 26.0, ptop - 2.0, "pagspire", n=7, steps=4, top_tilt=0.0, drape=1.2, cap=MOSS, m=ROCK,
         mlow=ROCK, taper=0.88, lean=(0.02, 0.0))
    crag(mb, px + 9.0, py - 16.0, 11.0, 26.0, 104.0, "pagspire_b", steps=3, top_tilt=0.15, drape=1.5, cap=MOSS, m=ROCK,
         mlow=ROCK, taper=0.84)
    # embasamento (kidan) de pedra em 2 degraus
    z = ptop - 1.2
    for hw, h in ((8.6, 1.4), (7.4, 1.1)):
        mb.box((2 * hw, 2 * hw, h + 0.6), (px, py, z + (h - 0.6) / 2), (0, 0, 0), ROCK, 0.0)
        z += h
    for i, (hw, h) in enumerate(PG_TIERS):
        # corpo: parede laqueada, pilares de canto escuros, faixa escura de consolos (tokyo) no alto
        # M6b item 45: corpo e pilares de canto morrem 0,3 DENTRO da faixa escura do alto (os topos eram coplanares
        # ao topo da faixa: 365 studs2 de z-fight laca x madeira)
        mb.box((2 * hw, 2 * hw, h - 0.3), (px, py, z + (h - 0.3) / 2), (0, 0, 0), LAC, 0.0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.box((0.55, 0.55, h - 0.3), (px + sx * (hw - 0.12), py + sy * (hw - 0.12), z + (h - 0.3) / 2),
                       (0, 0, 0), WD, 0.0)
        mb.box((2 * hw + 0.7, 2 * hw + 0.7, 0.9), (px, py, z + h - 0.45), (0, 0, 0), WD, 0.0)
        if i == 0:                                         # portas (painel escuro 0,15 a frente da parede)
            for k in range(4):
                a = k * math.pi / 2
                mb.box((2.8, 0.3, 3.6), (px + math.cos(a) * (hw + 0.1), py + math.sin(a) * (hw + 0.1), z + 1.9),
                       (0, 0, a + math.pi / 2), WD, 0.0)
        over = 3.4 - 0.25 * i
        ze = z + h + 0.1
        if i < len(PG_TIERS) - 1:
            pagoda_roof(mb, (px, py), hw, PG_TIERS[i + 1][0], ze, over, 1.9)
            z = ze + 1.9
        else:
            pagoda_roof(mb, (px, py), hw, 0.0, ze, over, 0.0, top=ze + 4.4)
            z = ze + 4.4
    # SORIN de ouro: roban, haste, 9 aneis, chama (suien) e joia
    mb.box((1.8, 1.8, 0.9), (px, py, z + 0.3), (0, 0, 0), GOLD, 0.0)
    mb.cyl(0.32, 11.0, (px, py, z + 5.8), m=GOLD, n=8, bevel=0.0)
    for k in range(9):
        r = 1.15 - 0.04 * k
        mb.cyl(r, 0.28, (px, py, z + 2.0 + k * 0.82), m=GOLD, n=8, bevel=0.0)
    mb.ico(0.75, (px, py, z + 10.6), GOLD, 1, scale=(1.0, 1.0, 1.3))
    mb.ico(0.42, (px, py, z + 11.8), GOLD, 1)


def build_pagoda():
    mb = MB("OP_Lmk_Pagoda", C, random.Random(1303), detail="far", floor=-999)
    pagoda(mb)
    mb.finish()


# ------------------------------------------------------------------ cameras de revisao
def cams():
    F = skf()
    c = Vector((SK_C[0], SK_C[1], SK_Z))
    wx, wy = L.SWORD_POS
    px, py, pr, ptop = L.WEST_SPIRE
    cs = {
        "CAM_OPLmk_SkullFront": (tuple(F.p(6.0, 74.0, SK_Z + 8.0)), tuple(c), 30),
        "CAM_OPLmk_SkullSea": (tuple(F.p(40.0, 78.0, 54.0)), tuple(c + Vector((0, 0, -12.0))), 30),
        "CAM_OPLmk_SkullBack": (tuple(F.p(30.0, -76.0, SK_Z + 26.0)), tuple(c), 28),
        "CAM_OPLmk_SkullTop": (tuple(F.p(-40.0, 40.0, SK_Z + 60.0)), tuple(c), 30),
        "CAM_OPLmk_Sword": ((wx - 58.0, wy - 72.0, 150.0), (wx, wy, 156.0), 24),
        "CAM_OPLmk_SwordHilt": ((wx + 36.0, wy - 36.0, 196.0), (wx, wy, 190.0), 26),
        "CAM_OPLmk_SwordBase": ((wx + 24.0, wy - 26.0, 112.0), (wx, wy, 104.0), 24),
        "CAM_OPLmk_SwordPlaza": ((96.0, 236.0, L.P + EYE), (wx, wy, 165.0), 24),
        "CAM_OPLmk_Pagoda": ((px - 62.0, py - 40.0, ptop + 26.0), (px, py, ptop + 16.0), 26),
        "CAM_OPLmk_PagodaW3": ((-158.0, 360.0, L.W3 + EYE), (px, py, ptop + 14.0), 22),
        "CAM_OPLmk_PagodaSea": ((px - 150.0, py - 80.0, 70.0), (px, py, 110.0), 24),
    }
    for n, (loc, tgt, lens) in cs.items():
        DL.camera(n, loc, tgt, lens)


def build():
    noise.seed_set(5531)
    build_skull()
    build_sword()
    build_pagoda()
    cams()
    print("OP_LANDMARKS ok")
